#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_google_play.py — jalur Google Play privat (owner 23 Nov 2026, docs/google-play.md). Tanpa peramban, tanpa jaringan, tanpa Pillow.

  PYTHON  apk/pasang.py — targetSdk & compileSdk dinaikkan ke SDK_SASARAN (≥ 36, syarat aplikasi baru di Play) di variables.gradle, tidak pernah
          menurunkan, pola asing DITOLAK (bangun gagal, bukan AAB yang diam-diam ditolak Play); dipanggil dari main.
          apk/periksa_aab.py — bundel sintetis: lengkap & bertanda tangan = lulus; tanpa tanda tangan / bukan ZIP / pustaka native 64-bit p_align 4 KB
          = GAGAL; pustaka 32-bit 4 KB tidak diwajibkan.
  STATIS  apk.yml — APK tetap (nama & isi artefak sama), AAB artefak terpisah, bundleRelease gagal tidak menggagalkan langkah APK, AAB ditandatangani
          lewat :env (sandi tidak di baris perintah), targetSdk ≥ 36 & RSA ≥ 2048 diperiksa, kunci dihapus, sertifikat (memuat nama pemilik) tidak
          dicetak, periksa_aab dipanggil.
          play-kunci.yml — hanya manual, isian lewat env (bukan disisipkan ke skrip), hanya PEM/heksa, pepk.jar dicocokkan SHA-256, kunci dihapus,
          artefak 1 hari.
  BAHAN   ikon 512 × 512 ≤ 1 MB, grafis unggulan 1024 × 500 TANPA alfa, sama dengan perender (bila apk/ikon_m.py ada); teks toko dalam batas Play & tanpa
          angka rupiah; privasi.html tanpa script, CSP ketat, menyebut tiap kelompok data di Data safety; panduan menyebut nama workflow & artefak yang ada.

    python3 alat-uji/uji_google_play.py            → N lulus · 0 gagal
    python3 alat-uji/uji_google_play.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import io, os, re, struct, sys, subprocess, zipfile, zlib

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
PAS = 'apk/pasang.py'; AAB = 'apk/periksa_aab.py'; YML = '.github/workflows/apk.yml'; KUNCI = '.github/workflows/play-kunci.yml'
TEKS = 'docs/google-play/teks-toko.md'; DS = 'docs/google-play/data-safety.md'; PANDU = 'docs/google-play.md'; PRIV = 'privasi.html'; BHN = 'apk/bahan_play.py'
IKON = 'docs/google-play/ikon-512.png'; GRAFIS = 'docs/google-play/grafis-unggulan-1024x500.png'
BERKAS = [PAS, AAB, YML, KUNCI, TEKS, DS, PANDU, PRIV, BHN]
BINER = [IKON, GRAFIS]

VARIABEL = """ext {
    minSdkVersion = 23
    compileSdkVersion = 35
    targetSdkVersion = 35
    androidxActivityVersion = '1.9.2'
    androidxAppCompatVersion = '1.7.0'
}
"""


def baca(ganti=None):
    t = {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in BERKAS}
    t.update({b: open(os.path.join(AKAR, b), 'rb').read() for b in BINER})
    for b, lama, baru in (ganti or []):
        if lama is None: t[b] = baru; continue
        assert t[b].count(lama) == 1, 'kontrol basi: %s · %r (%d×)' % (b, lama[:80], t[b].count(lama))
        t[b] = t[b].replace(lama, baru, 1)
    return t


def muat(teks, nama):
    ruang = {'__name__': 'uji_' + os.path.basename(nama), '__file__': os.path.join(AKAR, nama)}
    exec(compile(teks, nama, 'exec'), ruang); return ruang


def elf64(align):
    """.so ELF64 minimal: kepala 64 byte + satu PT_LOAD dengan p_align = align."""
    kepala = b'\x7fELF' + bytes([2, 1, 1]) + bytes(9) + struct.pack('<HHIQQQIHHHHHH', 3, 183, 1, 0, 64, 0, 0, 64, 56, 1, 0, 0, 0)
    return kepala + struct.pack('<IIQQQQQQ', 1, 5, 0, 0, 0, 0x100, 0x100, align)


def elf32(align):
    kepala = b'\x7fELF' + bytes([1, 1, 1]) + bytes(9) + struct.pack('<HHIIIIIHHHHHH', 3, 40, 1, 0, 52, 0, 0, 52, 32, 1, 0, 0, 0)
    return kepala + struct.pack('<IIIIIIII', 1, 0, 0, 0, 0x100, 0x100, 5, align)


def bundel(tanda=True, so=None):
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w') as z:
        z.writestr('BundleConfig.pb', b'\x0a\x00'); z.writestr('base/manifest/AndroidManifest.xml', b'\x0a\x00'); z.writestr('base/dex/classes.dex', b'dex\n')
        if tanda: z.writestr('META-INF/KUNCI.SF', b'Signature-Version: 1.0\n'); z.writestr('META-INF/KUNCI.RSA', b'\x30\x00')
        for n, isi in (so or {}).items(): z.writestr(n, isi)
    return b.getvalue()


def png_info(isi):
    """(lebar, tinggi, tipe_warna) dari kepala PNG; None bila bukan PNG."""
    if not isinstance(isi, bytes) or isi[:8] != b'\x89PNG\r\n\x1a\n' or isi[12:16] != b'IHDR': return None
    w, h, _, tipe = struct.unpack('>IIBB', isi[16:26]); return w, h, tipe


def blok(teks, nama):
    m = re.search(r'<!-- %s -->\n(.*?)\n<!-- /%s -->' % (nama, nama), teks, re.S); return m.group(1).strip() if m else None


def langkah_yml(teks, nama):
    """Isi satu langkah workflow (dari '- name: <nama>' sampai langkah berikutnya)."""
    m = re.search(r'\n      - name: ' + re.escape(nama) + r'\n(.*?)(?=\n      - name: |\Z)', teks, re.S); return m.group(1) if m else ''


def periksa_python(t):
    h = []; ok = lambda nama, benar, ket='': h.append({'nama': nama, 'ok': bool(benar), 'ket': str(ket)})
    try: P = muat(t[PAS], PAS)
    except Exception as e: return [{'nama': 'pasang.py tidak bisa dimuat', 'ok': False, 'ket': repr(e)}]
    Tolak = P['Tolak']
    def ditolak(f, *a):
        try: f(*a)
        except Tolak: return True
        except Exception: return False
        return False
    ok('pasang.py: SDK_SASARAN ≥ 36 (Play: aplikasi baru wajib menyasar Android 16 sejak 31 Agu 2026)', P.get('SDK_SASARAN', 0) >= 36, P.get('SDK_SASARAN'))
    try: v = P['ubah_variabel'](VARIABEL)
    except Exception as e: v = repr(e)
    ok('variables.gradle Capacitor 7: compileSdkVersion & targetSdkVersion 35 → 36, minSdk & pustaka tidak disentuh',
       'compileSdkVersion = 36' in v and 'targetSdkVersion = 36' in v and 'minSdkVersion = 23' in v and "androidxAppCompatVersion = '1.7.0'" in v, v)
    ok('variables.gradle: dijalankan dua kali = sama', P['ubah_variabel'](v) == v if 'Sdk' in v else False)
    v37 = VARIABEL.replace('targetSdkVersion = 35', 'targetSdkVersion = 37')
    ok('variables.gradle: angka yang sudah lebih tinggi (37) TIDAK diturunkan', 'targetSdkVersion = 37' in P['ubah_variabel'](v37))
    ok('variables.gradle tanpa targetSdkVersion DITOLAK (pola Capacitor berubah = bangun gagal)', ditolak(P['ubah_variabel'], VARIABEL.replace('    targetSdkVersion = 35\n', '')))
    ok('variables.gradle dengan compileSdkVersion dua kali DITOLAK', ditolak(P['ubah_variabel'], VARIABEL + 'compileSdkVersion = 34\n'))
    ok('pasang.py main() memanggil pasang_sdk() (angka SDK sungguh dipasang ke proyek)', re.search(r'(?m)^    pasang_java\(\);.*\bpasang_sdk\(\);', t[PAS]) is not None)

    try: A = muat(t[AAB], AAB)
    except Exception as e: return h + [{'nama': 'periksa_aab.py tidak bisa dimuat', 'ok': False, 'ket': repr(e)}]
    import tempfile
    def cek(isi):
        with tempfile.NamedTemporaryFile(suffix='.aab', delete=False) as f: f.write(isi); p = f.name
        try: return A['periksa'](p)
        finally: os.unlink(p)
    lulus = lambda r: bool(r) and all(x for x, _ in r)
    r = cek(bundel()); ok('periksa_aab: bundel lengkap bertanda tangan tanpa pustaka native = lulus', lulus(r), r)
    r = cek(bundel(tanda=False)); ok('periksa_aab: bundel TANPA tanda tangan = GAGAL (Play menolak)', not lulus(r), r)
    r = cek(b'bukan zip'); ok('periksa_aab: bukan ZIP = GAGAL', not lulus(r), r)
    r = cek(bundel(so={'base/lib/arm64-v8a/libx.so': elf64(4096)})); ok('periksa_aab: pustaka arm64 p_align 4 KB = GAGAL (syarat halaman 16 KB)', not lulus(r), r)
    r = cek(bundel(so={'base/lib/arm64-v8a/libx.so': elf64(16384), 'base/lib/x86_64/libx.so': elf64(65536)})); ok('periksa_aab: pustaka 64-bit p_align 16 KB / 64 KB = lulus', lulus(r), r)
    r = cek(bundel(so={'base/lib/armeabi-v7a/libx.so': elf32(4096)})); ok('periksa_aab: pustaka 32-bit 4 KB tidak diwajibkan (lulus)', lulus(r), r)
    r = cek(bundel(so={'base/lib/arm64-v8a/libx.so': b'bukan elf'})); ok('periksa_aab: .so yang bukan ELF = GAGAL', not lulus(r), r)
    return h


def periksa_statis(t):
    h = []; ok = lambda nama, benar, ket='': h.append({'nama': nama, 'ok': bool(benar), 'ket': str(ket)})
    y = t[YML]; bangun = langkah_yml(y, 'Bangun APK'); simpan_apk = langkah_yml(y, 'Simpan APK')
    tanda = langkah_yml(y, 'Tanda tangani & periksa AAB (Google Play)'); simpan_aab = langkah_yml(y, 'Simpan AAB (Google Play)')
    ok('apk.yml: artefak APK tetap "apk-tablet-kasir" berisi *.apk saja (owner tetap pasang APK manual)',
       'name: apk-tablet-kasir' in simpan_apk and 'path: apk/keluaran/*.apk' in simpan_apk, simpan_apk)
    ok('apk.yml: AAB = artefak TERPISAH "aab-google-play" berisi *.aab, hanya bila bundel jadi',
       'name: aab-google-play' in simpan_aab and 'path: apk/keluaran/*.aab' in simpan_aab and "if: env.AAB_SIAP == '1'" in simpan_aab and 'if-no-files-found: error' in simpan_aab, simpan_aab)
    i = {n: y.find('      - name: ' + n) for n in ('Bangun APK', 'Simpan APK', 'Tanda tangani & periksa AAB (Google Play)', 'Simpan AAB (Google Play)')}
    ok('apk.yml: urutan Bangun APK → Simpan APK → Tanda tangani AAB → Simpan AAB (AAB gagal ≠ APK hilang)', all(x >= 0 for x in i.values()) and sorted(i.values()) == list(i.values()), i)
    cabang = bangun[bangun.find('if [ -n "$KEYSTORE_B64" ]'):bangun.find('          else\n            bangun assembleDebug')]
    ok('apk.yml: bundleRelease hanya di cabang berkunci, SESUDAH APK rilis ditandatangani, dan gagalnya TIDAK menggagalkan langkah APK',
       'if bangun bundleRelease; then echo "AAB_SIAP=1" >> "$GITHUB_ENV"' in cabang and cabang.find('bangun assembleRelease') < cabang.find('apksigner" verify') < cabang.find('bangun bundleRelease')
       and bangun.count('bangun bundleRelease') == 1, cabang[-600:])
    ok('apk.yml: AAB ditandatangani jarsigner dengan sandi lewat :env (tidak di baris perintah) dan alias rahasia',
       re.search(r'jarsigner -keystore "\$RUNNER_TEMP/kunci\.jks" -storepass:env KEYSTORE_PASSWORD -keypass:env KEY_PASSWORD .*\n.*"\$KEY_ALIAS"', tanda) is not None, tanda[:400])
    ok('apk.yml: tanda tangan AAB diverifikasi (jar verified) sebelum disimpan', 'jarsigner -verify "$AAB"' in tanda and "grep -q 'jar verified'" in tanda)
    ok('apk.yml: targetSdk dibaca dari APK hasil bangun yang sama, < 36 = merah', 'dump badging "$APK"' in tanda and '[ "${SASARAN:-0}" -ge 36 ]' in tanda)
    ok('apk.yml: kunci unggah wajib RSA ≥ 2048 bit', "grep -q 'RSA'" in tanda and '[ "${BIT:-0}" -lt 2048 ]' in tanda)
    ok('apk.yml: sertifikat kunci (memuat nama pemilik) TIDAK dicetak — keytool ke berkas sementara, hanya baris algoritma & SHA-256 yang diambil, lalu dihapus',
       'keytool -list -v -keystore "$RUNNER_TEMP/kunci.jks" -storepass:env KEYSTORE_PASSWORD -alias "$KEY_ALIAS" > "$RUNNER_TEMP/kunci.txt"' in tanda
       and 'rm -f "$RUNNER_TEMP/kunci.txt"' in tanda and 'cat "$RUNNER_TEMP/kunci.txt"' not in tanda)
    pos_ttd = tanda.find('jarsigner -keystore'); pos_rm = tanda.find('rm -f "$RUNNER_TEMP/kunci.jks"', pos_ttd)
    ok('apk.yml: berkas kunci dihapus sesudah AAB ditandatangani (dan di jalan keluar RSA gagal)', pos_ttd > 0 and pos_rm > pos_ttd and tanda.count('rm -f "$RUNNER_TEMP/kunci.jks"') >= 2)
    ok('apk.yml: bentuk bundel & pustaka native 16 KB diperiksa apk/periksa_aab.py', 'python3 ../periksa_aab.py "$AAB"' in tanda)
    ok('apk.yml: tanpa rahasia kunci = tanpa AAB (bundel debug ditolak Play), dicatat di ringkasan', 'AAB Google Play: TIDAK dibangun' in tanda and 'exit 0' in tanda)
    ok('apk.yml: rahasia tidak disisipkan langsung ke skrip langkah AAB (lewat env)', '${{ secrets' not in tanda.split('run: |', 1)[-1])

    k = t[KUNCI]; pemicu = k[k.find('\non:'):k.find('\npermissions:')]
    ok('play-kunci.yml: HANYA dijalankan manual (workflow_dispatch) — tidak pernah otomatis di push/PR', 'workflow_dispatch:' in pemicu and not re.search(r'\n  (push|pull_request|schedule|workflow_run)', pemicu), pemicu)
    jalan = k.split('run: |', 1)[-1]
    ok('play-kunci.yml: isian owner lewat env, TIDAK disisipkan ${{ }} ke skrip (anti suntik perintah)', 'KUNCI_ENKRIPSI: ${{ inputs.kunci_enkripsi }}' in k and '${{' not in jalan.split('- name: Simpan')[0])
    ok('play-kunci.yml: isian hanya PEM kunci publik atau heksa — lainnya ditolak', "-----BEGIN PUBLIC KEY-----" in jalan and "grep -qE '^[0-9a-fA-F]{64,}$'" in jalan and "grep -qE '^[A-Za-z0-9+/=]+$'" in jalan)
    pem = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0abc+/=\nQUJD\n-----END PUBLIC KEY-----\n'
    baris = [x for x in jalan.split('\n') if 'BADAN=$(' in x]
    if len(baris) == 1:
        import tempfile as _tf
        with _tf.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, 'pepk')); open(os.path.join(d, 'pepk', 'isian.txt'), 'w').write(pem)
            r = subprocess.run(['bash', '-c', baris[0].strip() + '; printf %s "$BADAN"'], capture_output=True, text=True, env={'RUNNER_TEMP': d, 'PATH': os.environ.get('PATH', '')})
        badan = r.stdout
    else: badan = ''
    ok('play-kunci.yml: PEM dari Play Console (berkas encryption_public_key.pem utuh) → badan base64 bersih tanpa kepala/ekor', badan == 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0abc+/=QUJD', badan[:80])
    ok('play-kunci.yml: pepk.jar dicocokkan sidik SHA-256 sebelum dijalankan', re.search(r'SIDIK_PEPK: [0-9a-f]{64}\n', k) is not None and 'sha256sum -c -' in jalan and jalan.find('sha256sum -c') < jalan.find('java -jar'))
    ok('play-kunci.yml: sandi ke PEPK dari env rahasia, sertifikat ikut (--include-cert), kunci dihapus sesudahnya',
       '--keystore-pass="$KEYSTORE_PASSWORD" --key-pass="$KEY_PASSWORD"' in jalan and '--include-cert' in jalan and jalan.find('rm -f "$RUNNER_TEMP/kunci.jks"') > jalan.find('java -jar'))
    ok('play-kunci.yml: artefak kunci terenkripsi hidup 1 hari', re.search(r'name: kunci-terenkripsi-untuk-play\n.*\n\s+retention-days: 1\n', k) is not None)
    return h


def periksa_bahan(t):
    h = []; ok = lambda nama, benar, ket='': h.append({'nama': nama, 'ok': bool(benar), 'ket': str(ket)})
    ik, gr = png_info(t[IKON]), png_info(t[GRAFIS])
    ok('ikon Play: PNG 512 × 512, ≤ 1 MB', ik is not None and ik[:2] == (512, 512) and len(t[IKON]) <= 1024 * 1024, ik)
    ok('grafis unggulan: PNG 1024 × 500 TANPA alfa (tipe warna 2 = 24-bit; syarat Play), ≤ 15 MB', gr == (1024, 500, 2) and len(t[GRAFIS]) <= 15 * 1024 * 1024, gr)
    if os.path.exists(os.path.join(AKAR, 'apk', 'ikon_m.py')) and t[BHN] == open(os.path.join(AKAR, BHN), encoding='utf-8').read() and t[IKON] == open(os.path.join(AKAR, IKON), 'rb').read() and t[GRAFIS] == open(os.path.join(AKAR, GRAFIS), 'rb').read():
        r = subprocess.run([sys.executable, os.path.join(AKAR, BHN), '--periksa'], capture_output=True, text=True)
        ok('bahan Play = hasil perender logo M (apk/bahan_play.py --periksa)', r.returncode == 0, (r.stdout + r.stderr)[-300:])
    tk = t[TEKS]; judul, pendek, lengkap = blok(tk, 'judul'), blok(tk, 'pendek'), blok(tk, 'lengkap')
    ok('teks toko: nama ≤ 30, deskripsi pendek ≤ 80, lengkap ≤ 4000 huruf, semuanya terisi',
       judul and pendek and lengkap and len(judul) <= 30 and len(pendek) <= 80 and len(lengkap) <= 4000, [len(x or '') for x in (judul, pendek, lengkap)])
    semua = tk + t[DS] + t[PRIV] + t[PANDU]
    ok('bahan toko & panduan tanpa angka rupiah (repo publik)', not re.search(r'Rp\s?\d', semua), re.findall(r'.{20}Rp\s?\d.{10}', semua)[:3])
    ok('bahan toko & panduan tanpa alamat email (repo publik; email developer diisi owner di Play Console)', not re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', semua), re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', semua)[:3])
    p = t[PRIV]
    sebaris = [x for x in re.findall(r'<\w[^>]*>', p) if re.search(r'\son\w+\s*=', x, re.I)]
    ok('privasi.html: tanpa script & handler sebaris, CSP default-src none', '<script' not in p.lower() and not sebaris and "default-src 'none'" in p, sebaris[:2])
    kata = ['email', 'id akun', 'telepon', 'alamat', 'foto', 'pesan', 'log aktivitas', 'token notifikasi', 'status perangkat', 'Firebase', 'iklan', 'id="hapus"', 'anak']
    ok('privasi.html menyebut setiap kelompok data Data safety + penghapusan + anak', all(x.lower() in p.lower() for x in kata), [x for x in kata if x.lower() not in p.lower()])
    url = 'https://devamp-hl.github.io/Toko-Beras-M.IQBAL/privasi.html'
    ok('alamat kebijakan privasi sama di teks toko, Data safety, panduan', url in tk and url in t[DS] and url in t[PANDU] and 'privasi.html#hapus' in t[DS])
    nama = [re.search(r'(?m)^name: (.+)$', t[w]).group(1) for w in (YML, KUNCI)]
    nama += [n for w in (YML, KUNCI) for n in re.findall(r'(?m)^ +name: ([\w-]+)\n +path: ', t[w])]
    ok('panduan menyebut nama workflow & artefak yang SUNGGUH ada di apk.yml / play-kunci.yml', len(nama) == 5 and all(x in t[PANDU] for x in nama), [x for x in nama if x not in t[PANDU]] or nama)
    return h


def jalankan(t):
    return periksa_python(t) + periksa_statis(t) + periksa_bahan(t)


KONTROL = [
    ('SDK sasaran kembali 35', [(PAS, 'SDK_SASARAN = 36', 'SDK_SASARAN = 35')]),
    ('pasang_sdk tidak dipanggil', [(PAS, 'pasang_versi(max(1, x.versi)); pasang_sdk(); ', 'pasang_versi(max(1, x.versi)); ')]),
    ('targetSdk tidak diubah (hanya compileSdk)', [(PAS, "    for nama in ('compileSdkVersion', 'targetSdkVersion'):", "    for nama in ('compileSdkVersion',):")]),
    ('angka SDK diturunkan', [(PAS, 'str(max(sdk, int(mm.group(2))))', 'str(sdk)')]),
    ('pola variables.gradle asing diterima diam-diam', [(PAS, '        if len(cocok) != 1: raise Tolak(', '        if len(cocok) > 9: raise Tolak(')]),
    ('periksa_aab: halaman 4 KB dianggap cukup', [(AAB, 'HALAMAN_16K = 16384', 'HALAMAN_16K = 4096')]),
    ('periksa_aab: tanda tangan tidak diperiksa', [(AAB, "h.append((bool(sf) and bool(blok),", "h.append((True,")]),
    ('periksa_aab: .so bukan ELF dilewati', [(AAB, "if hasil is None: buruk.append(n + ' (bukan ELF)'); continue", "if hasil is None: continue")]),
    ('artefak APK ikut memuat AAB', [(YML, '          name: apk-tablet-kasir\n          path: apk/keluaran/*.apk', '          name: apk-tablet-kasir\n          path: apk/keluaran/*')]),
    ('AAB masuk artefak yang sama dengan APK', [(YML, 'name: aab-google-play', 'name: apk-tablet-kasir')]),
    ('bundleRelease gagal menggagalkan langkah APK', [(YML, 'if bangun bundleRelease; then echo "AAB_SIAP=1" >> "$GITHUB_ENV"', 'bangun bundleRelease; if true; then echo "AAB_SIAP=1" >> "$GITHUB_ENV"')]),
    ('sandi kunci di baris perintah jarsigner', [(YML, '-storepass:env KEYSTORE_PASSWORD -keypass:env KEY_PASSWORD -digestalg', '-storepass "$KEYSTORE_PASSWORD" -keypass "$KEY_PASSWORD" -digestalg')]),
    ('tanda tangan AAB tidak diverifikasi', [(YML, "grep -q 'jar verified' \"$RUNNER_TEMP/aab.txt\" ||", 'true ||')]),
    ('targetSdk tidak diperiksa', [(YML, '[ "${SASARAN:-0}" -ge 36 ]', '[ "${SASARAN:-0}" -ge 0 ]')]),
    ('kunci RSA kecil diterima', [(YML, '[ "${BIT:-0}" -lt 2048 ]', '[ "${BIT:-0}" -lt 0 ]')]),
    ('sertifikat kunci dicetak ke log', [(YML, '-alias "$KEY_ALIAS" > "$RUNNER_TEMP/kunci.txt" || true', '-alias "$KEY_ALIAS" | tee "$RUNNER_TEMP/kunci.txt" || true')]),
    ('kunci tidak dihapus sesudah AAB ditandatangani', [(YML, '"$KEY_ALIAS" > /dev/null\n          rm -f "$RUNNER_TEMP/kunci.jks"\n', '"$KEY_ALIAS" > /dev/null\n')]),
    ('periksa_aab tidak dipanggil', [(YML, '          python3 ../periksa_aab.py "$AAB"\n', '')]),
    ('workflow kunci jalan di setiap push', [(KUNCI, 'on:\n  workflow_dispatch:', 'on:\n  push:\n  workflow_dispatch:')]),
    ('isian kunci disisipkan langsung ke skrip', [(KUNCI, 'printf \'%s\\n\' "$KUNCI_ENKRIPSI"', 'printf \'%s\\n\' "${{ inputs.kunci_enkripsi }}"')]),
    ('isian apa saja diterima sebagai heksa', [(KUNCI, "grep -qE '^[0-9a-fA-F]{64,}$'", "grep -qE '.*'")]),
    ('pepk.jar tidak dicocokkan sidiknya', [(KUNCI, '          echo "$SIDIK_PEPK  $RUNNER_TEMP/pepk/pepk.jar" | sha256sum -c - ||', '          true ||')]),
    ('kepala PEM dibuang sesudah spasi dibuang (bug 26 Nov)', [(KUNCI, """BADAN=$(sed -e 's/-----BEGIN PUBLIC KEY-----//' -e 's/-----END PUBLIC KEY-----//' "$RUNNER_TEMP/pepk/isian.txt" | tr -d '\\n \\t')""", """BADAN=$(tr -d '\\n ' < "$RUNNER_TEMP/pepk/isian.txt" | sed -e 's/-----BEGIN PUBLIC KEY-----//' -e 's/-----END PUBLIC KEY-----//')""")]),
    ('artefak kunci hidup 30 hari', [(KUNCI, '          retention-days: 1\n', '          retention-days: 30\n')]),
    ('grafis unggulan beralfa (diganti ikon RGBA)', [(GRAFIS, None, 'IKON')]),
    ('ikon salah ukuran (diganti grafis)', [(IKON, None, 'GRAFIS')]),
    ('deskripsi pendek kepanjangan', [(TEKS, 'Kasir tablet toko beras: jual, stok, bon, struk, dan laporan harian.', 'Kasir tablet toko beras: jual, stok, bon, struk, laporan harian, surat jalan, tutup hari, dan kabar toko.')]),
    ('angka rupiah masuk deskripsi', [(TEKS, '• Tutup hari: hitung laci dan timbang', '• Tutup hari: hitung laci Rp 500.000 dan timbang')]),
    ('email masuk panduan', [(PANDU, 'dengan akun Google owner. Pilih', 'dengan akun Google owner (toko@contoh.id). Pilih')]),
    ('privasi.html diberi script', [(PRIV, '<main>', '<main><script>1</script>')]),
    ('privasi.html diberi handler sebaris', [(PRIV, '<h2 id="hapus">', '<h2 id="hapus" onclick="x()">')]),
    ('privasi.html lupa token notifikasi', [(PRIV, 'Token notifikasi perangkat dan status', 'Penanda perangkat dan status')]),
    ('Data safety menunjuk alamat privasi lain', [(DS, '`https://devamp-hl.github.io/Toko-Beras-M.IQBAL/privasi.html`', '`https://contoh.id/privasi.html`')]),
    ('workflow kunci berganti nama, panduan tertinggal', [(KUNCI, 'name: Serahkan kunci aplikasi ke Google Play (sekali)\n', 'name: Kunci Play\n')]),
]


def main():
    if '--kontrol' in sys.argv:
        kode = 0; dasar = {x['nama'] for x in jalankan(baca()) if x['ok']}
        for nama, ganti in KONTROL:
            ganti = [(b, l, (baca()[{'IKON': IKON, 'GRAFIS': GRAFIS}[x]] if x in ('IKON', 'GRAFIS') else x)) for b, l, x in ganti]
            try: t = baca(ganti)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' — ' + str(e)); kode = 3; continue
            gagal = [x for x in jalankan(t) if not x['ok'] and x['nama'] in dasar]
            print(('BERBUNYI ' if gagal else 'DIAM!!   ') + nama + (' → ' + gagal[0]['nama'][:110] if gagal else ''))
            if not gagal: kode = 3
        print('KONTROL %s %d' % ('LULUS' if kode == 0 else 'GAGAL', len(KONTROL))); sys.exit(kode)
    H = jalankan(baca()); g = [x for x in H if not x['ok']]
    for x in H: print(('  ok  ' if x['ok'] else 'GAGAL ') + x['nama'] + ('' if x['ok'] else ' — ' + x['ket'][:300]))
    print('GOOGLE PLAY (statis + python): %d lulus · %d gagal' % (len(H) - len(g), len(g)))
    sys.exit(1 if g else 0)


if __name__ == '__main__':
    main()
