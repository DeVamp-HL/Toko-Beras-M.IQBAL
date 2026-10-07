#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gladi_tutup_buku.py — GLADI TUTUP BUKU di SERVER TIRUAN: Firebase Emulator Suite (Firestore + Auth, aturan = firestore.rules repo) diisi DATA CONTOH
sintetis skala toko (gladi_data_contoh.py), lalu /baru/ ASLI dibuka di Chrome headless lewat ?emulator= (baru/js/data/server-tiruan.js) dan Uang ›
Tutup buku dijalankan lewat layarnya — ketukan sungguhan, bukan fungsi logika.

HANYA DI RUNNER GITHUB ACTIONS (CLAUDE.md, keputusan owner 27 Sep 2026: uji peramban berulang & emulator hanya di runner). Di luar Actions alat ini
MENOLAK jalan, kecuali --periksa-salinan (statis: menyusun salinan uji tanpa Chrome & tanpa emulator). Satu Chrome sekali jalan, grup prosesnya
dimatikan sesudah tiap skenario. Dijalankan di dalam `firebase emulators:exec` (.github/workflows/gladi-tutup-buku.yml).

SKENARIO (urutannya = urutan ritual owner; langkah tiap skenario = daftar nama di SKENARIO, langkahnya fungsi bernama di SKENARIO_JS). Semua di data MACET
(23 hari berjualan tanpa tutup hari, pola toko 6 Okt) — sejak Paket A gerbang g1 dibuka lewat putusan per tanggal ("Simpan putusan"), bukan data bersih:
  latihan  31 Des 2026 21.45 WIB: masuk sebagai owner contoh → muat penuh → Uang › Tutup buku → LATIHAN tujuh langkah sampai "Latihan selesai" → DIAM
           5 dtk — TANPA satu pun tulisan/hapus ke server selain denyut perangkat & katalog kasir (latar, bukan tutup buku).
  gerbang  1 Jan 2027 15.30 WIB (sesudah reset kuota): SUNGGUHAN boleh; g1 "23 hari belum ditutup & belum diputus" memblokir, tombol "1 hal belum beres —
           bereskan dulu"; mengetuknya tidak memajukan langkah dan tidak menulis apa pun. Lalu alasan diketik per tanggal → "Simpan putusan" = SATU dokumen
           aturanToko/putusanHari (dicek di server) → g1 beres → periksa lolos → DIAM tanpa tulisan.
  ritual   1 Jan 2027 15.30 WIB: SUNGGUHAN → putusan per tanggal → sampai paraf → kunci, server MENOLAK kiriman saldo pembuka ke-2 (aturan emulator diganti
           sementara, salinan firestore.rules repo + satu blok ditolak) → kartu "lanjutkan / batalkan" → BATALKAN SEBELUM PENANDA; mulai lagi → arsip
           DITOLAK server di potongan pertama → kartu "lanjutkan / batalkan" → aturan repo dipulihkan → LANJUTKAN → arsip habis → BATALKAN SESUDAH PENANDA
           (arsip dikembalikan, pembuka ditarik); mulai lagi → selesai (cadangan sesudah) → DIAM. Klaim tiap titik DIPERIKSA DI SERVER (REST emulator, bukan
           cache halaman): berita acara, arsipTahun = dokumen 2026 yang asli, dokumen 2026 tersisa di koleksi asal, saldo pembuka = nPembuka, penanda
           tutupBuku, titik kas & isi 21 koleksi 2026 sesudah batal = sebelum ritual.
  ritualPendek (kontrol saja) kunci penuh lalu BATALKAN SESUDAH PENANDA — pemulihan arsip yang dirusak di salinan wajib ketahuan dari isi server.
Tiap langkah: baca (dokumen yang diterima pendengar halaman — penghitung di salinan SDK uji — DITAMBAH tulisan halaman sendiri ke koleksi yang didengarnya,
yang ditagih Firestore tetapi tidak memicu docChange baru; get() di aturan tidak terukur), tulis & hapus (beda isi emulator lewat REST sebelum ↔ sesudah
langkah). Ringkasan: per langkah, lalu per JALUR (ritual bersih percobaan terakhir · kunci berhenti + batal sebelum penanda · batal sesudah penanda) di
skala gladi dan perkiraan skala toko, dibandingkan dengan batas Spark (50 rb baca, 20 rb tulis, 20 rb hapus per hari) dan perkiraan kuota halaman.

KELUARAN: laporan JSON (--keluar) + ringkasan Markdown (--ringkasan; workflow menempelnya ke halaman ringkasan run). Keluar 0 = semua cek lulus, 2 = gagal.

    python3 alat-uji/gladi_tutup_buku.py --keluar laporan.json --ringkasan ringkasan.md [--skenario latihan,gerbang,ritual]
    python3 alat-uji/gladi_tutup_buku.py --kontrol [N]        → kerusakan di SALINAN uji (latihan menulis, latihan menulis tertunda, gerbang g1 dibuang,
                                                               satu koleksi tidak lengkap, pemulihan arsip kurang satu) wajib membuat CEK SASARANNYA gagal, karena
                                                               kerusakan itu (bukti), dengan skenario yang jalan sampai akhir (keluar 3 kalau ada yang diam).
                                                               N = satu kontrol saja (workflow: tiap kontrol di emulator sendiri)
    python3 alat-uji/gladi_tutup_buku.py --jumlah-kontrol     → (boleh di Mac) jumlah kontrol
    python3 alat-uji/gladi_tutup_buku.py --periksa-salinan    → (boleh di Mac) salinan uji disusun & diperiksa statis: connect-src salinan = connect-src
                                                               situs − host Firebase sungguhan + alamat emulator, jam palsu sebelum meta CSP, SDK
                                                               penghitung, skenario dari 'self'
"""
import os, re, sys, json, time, shutil, signal, socket, secrets, hashlib, datetime, functools, threading, subprocess, tempfile, socketserver, http.server
import urllib.request, urllib.error, urllib.parse
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import gladi_data_contoh as DC  # noqa: E402
import coba_ulang  # noqa: E402  — percobaan ulang SELALU tercatat (keputusan owner 26 Sep 2026)

SDK = 'https://www.gstatic.com/firebasejs/10.13.0/'
PROYEK = re.search(r"export const PROYEK_TIRUAN = '([^']+)';", open(os.path.join(AKAR, 'baru/js/data/server-tiruan.js'), encoding='utf-8').read()).group(1)
EMAIL_OWNER = re.search(r"export const EMAIL_OWNER = '([^']+)';", open(os.path.join(AKAR, 'baru/js/data/akses.js'), encoding='utf-8').read()).group(1)
EMAIL_KARYAWAN = 'karyawan.contoh@gladi.contoh'
SPARK = {'baca': 50000, 'tulis': 20000, 'hapus': 20000}
TOKO_ARSIP = 17000   # proyeksi dokumen tahun 2026 di toko akhir Des (audit kesiapan: ±16,5–18 rb) — pengali "perkiraan skala toko" di ringkasan
MEPET = 0.8          # jalur yang memakai > 80% kuota satu hari (skala toko) diberi peringatan di ringkasan
# tulisan LATAR (bukan tutup buku): denyut perangkat & katalog HP kasir yang diterbitkan owner otomatis
LATAR = {'perangkatStatus', 'ringkasanKasir'}
# koleksi yang DIDENGAR halaman owner (koleksi.js + dokumen katalog kasir): tulisan halaman sendiri ke sana ditagih 1 baca per dokumen oleh Firestore (dokumen
# masuk/berubah di hasil pendengar), tetapi SDK tidak memunculkan docChange baru saat server mengakuinya (perubahan metadata saja) → ditambahkan dari REST
DIDENGAR = set(re.findall(r"\{ nama: '(\w+)'", open(os.path.join(AKAR, 'baru/js/data/koleksi.js'), encoding='utf-8').read())) | {
    re.search(r"export const KK_KOLEKSI = '([^']+)';", open(os.path.join(AKAR, 'baru/js/data/katalog-kasir.js'), encoding='utf-8').read()).group(1)}
TAK_TERCAPAI = 'langkah tidak tercapai'   # ket cek yang langkahnya tidak dijalankan — kontrol yang hanya "gagal" karena ini dihitung DIAM
CHROME = next((p for p in ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
                           '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'] if os.path.exists(p)), None)
TUNGGU_SKENARIO = {'latihan': 900, 'gerbang': 900, 'ritual': 6000, 'ritualPendek': 3600, 'muatSaja': 900}


def alamat_emulator():
    fs = os.environ.get('FIRESTORE_EMULATOR_HOST') or '127.0.0.1:8080'; au = os.environ.get('FIREBASE_AUTH_EMULATOR_HOST') or '127.0.0.1:9099'
    return fs.replace('localhost', '127.0.0.1'), au.replace('localhost', '127.0.0.1')


FS_HOST, AUTH_HOST = alamat_emulator()
FS, AUTH = 'http://' + FS_HOST, 'http://' + AUTH_HOST
DB = 'projects/%s/databases/(default)' % PROYEK
OWNER = {'Authorization': 'Bearer owner'}   # emulator: lewati aturan (pengisi data & pembaca isi server saja; halaman tetap tunduk aturan repo)


# ============================== REST emulator ==============================
def rest(metode, url, data=None, kepala=None, waktu=180):
    body = None if data is None else json.dumps(data).encode('utf-8')
    h = {'Content-Type': 'application/json'}; h.update(kepala or {})
    req = urllib.request.Request(url, data=body, method=metode, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=waktu) as r: t = r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        raise RuntimeError('%s %s → HTTP %s: %s' % (metode, url.split('?')[0], e.code, e.read().decode('utf-8', 'replace')[:400]))
    return json.loads(t) if t.strip()[:1] in ('{', '[') else t


def tunggu_emulator(batas=180):
    t0 = time.time(); galat = ''
    while time.time() - t0 < batas:
        try:
            rest('GET', FS + '/', waktu=5); rest('GET', AUTH + '/', waktu=5); return
        except Exception as e: galat = str(e); time.sleep(1)
    raise RuntimeError('emulator tidak menjawab dalam %d dtk: %s' % (batas, galat))


def ke_nilai(v):
    if v is None: return {'nullValue': None}
    if isinstance(v, bool): return {'booleanValue': v}
    if isinstance(v, int): return {'integerValue': str(v)}
    if isinstance(v, float): return {'doubleValue': v}
    if isinstance(v, str): return {'stringValue': v}
    if isinstance(v, list): return {'arrayValue': {'values': [ke_nilai(x) for x in v]}}
    if isinstance(v, dict): return {'mapValue': {'fields': {k: ke_nilai(x) for k, x in v.items()}}}
    raise TypeError('nilai tidak dikenal: %r' % (v,))


def dari_nilai(n):
    if 'nullValue' in n: return None
    if 'booleanValue' in n: return n['booleanValue']
    if 'integerValue' in n: return int(n['integerValue'])
    if 'doubleValue' in n: return float(n['doubleValue'])
    if 'stringValue' in n: return n['stringValue']
    if 'timestampValue' in n: return n['timestampValue']
    if 'arrayValue' in n: return [dari_nilai(x) for x in n['arrayValue'].get('values', [])]
    if 'mapValue' in n: return {k: dari_nilai(x) for k, x in n['mapValue'].get('fields', {}).items()}
    return n


def id_dok(koleksi, d):
    """Id dokumen = String(data.id) persis aplikasi (arsip menghapus doc(koleksi, String(id))); biaya bulanan = bulannya (tbDaftarKoleksi)."""
    return str(d.get('bulan') or d['id']) if koleksi == 'biayaBulanan' else str(d['id'])


def kosongkan():
    rest('DELETE', FS + '/emulator/v1/projects/%s/databases/(default)/documents' % PROYEK, waktu=900)
    rest('DELETE', AUTH + '/emulator/v1/projects/%s/accounts' % PROYEK)


def tulis_rest(daftar):
    """[(koleksi, id, data)] → commit per 400 (Bearer owner, tanpa aturan)."""
    for i in range(0, len(daftar), 400):
        rest('POST', FS + '/v1/' + DB + '/documents:commit', {'writes': [{'update': {'name': DB + '/documents/' + k + '/' + i_, 'fields': {a: ke_nilai(b) for a, b in d.items()}}}
                                                                       for k, i_, d in daftar[i:i + 400]]}, OWNER)


def isi_data(data):
    daftar = [(k, id_dok(k, d), d) for k, v in data.items() if isinstance(v, list) for d in v]
    tulis_rest(daftar); return len(daftar)


def buat_akun(email, sandi):
    r = rest('POST', AUTH + '/identitytoolkit.googleapis.com/v1/accounts:signUp?key=demo-kunci-gladi', {'email': email, 'password': sandi, 'returnSecureToken': True})
    return r['localId']


def koleksi_ada():
    out, tok = [], None
    while True:
        r = rest('POST', FS + '/v1/' + DB + '/documents:listCollectionIds', dict({'pageSize': 500}, **({'pageToken': tok} if tok else {})), OWNER)
        out += r.get('collectionIds', []); tok = r.get('nextPageToken')
        if not tok: return sorted(out)


def jalankan_query(koleksi, pilih=True):
    q = {'from': [{'collectionId': koleksi}]}
    if pilih: q['select'] = {'fields': [{'fieldPath': '__name__'}]}
    return [x['document'] for x in rest('POST', FS + '/v1/' + DB + '/documents:runQuery', {'structuredQuery': q}, OWNER) if isinstance(x, dict) and 'document' in x]


def id_dari_nama(nama):
    return urllib.parse.unquote(nama.rsplit('/', 1)[1])


def potret():
    """Isi server SEKARANG: {koleksi: {id: updateTime}} — dasar hitungan tulis/hapus per langkah."""
    return {k: {id_dari_nama(d['name']): d.get('updateTime', '') for d in jalankan_query(k)} for k in koleksi_ada()}


def potret_isi(koleksi):
    """Isi lengkap (dekode) koleksi-koleksi itu: {koleksi: {id: data}} — pembanding 'isi server kembali seperti sebelum ritual'."""
    return {k: {id_dari_nama(d['name']): {a: dari_nilai(b) for a, b in d.get('fields', {}).items()} for d in jalankan_query(k, pilih=False)} for k in koleksi}


def ambil_dok(koleksi, id_):
    """Satu dokumen dari SERVER (REST, Bearer owner) → dict, atau None kalau tidak ada."""
    try: d = rest('GET', FS + '/v1/' + DB + '/documents/' + koleksi + '/' + urllib.parse.quote(str(id_), safe=''), kepala=OWNER, waktu=60)
    except RuntimeError as e:
        if 'HTTP 404' in str(e): return None
        raise
    return {a: dari_nilai(b) for a, b in (d.get('fields') or {}).items()}


def beda(a, b):
    """Dua potret → ({koleksi: n tulis}, {koleksi: n hapus}). Tulis = dokumen baru + dokumen yang jam ubahnya berganti."""
    tulis, hapus = {}, {}
    for k in sorted(set(a) | set(b)):
        A, B = a.get(k, {}), b.get(k, {})
        t = len(set(B) - set(A)) + sum(1 for i in set(A) & set(B) if A[i] != B[i]); h = len(set(A) - set(B))
        if t: tulis[k] = t
        if h: hapus[k] = h
    return tulis, hapus


ATURAN_REPO = open(os.path.join(AKAR, 'firestore.rules'), encoding='utf-8').read()


def pasang_aturan(teks):
    r = rest('PUT', FS + '/emulator/v1/projects/%s:securityRules' % PROYEK, {'rules': {'files': [{'name': 'firestore.rules', 'content': teks}]}})
    galat = [x for x in (r.get('issues') or []) if isinstance(r, dict) and str(x.get('severity', '')).upper() == 'ERROR'] if isinstance(r, dict) else []
    if galat: raise RuntimeError('aturan emulator ditolak: %s' % json.dumps(galat)[:400])


def aturan_tolak(koleksi):
    """SALINAN firestore.rules repo dengan tulisan (create/update) ke satu koleksi ditolak server — memotong ritual di tengah seperti kuota habis /
    sinyal putus. Hanya di emulator, sementara; firestore.rules repo TIDAK diubah.
    Izin di rules = ATAU (allow mana pun yang lolos memberi izin), jadi menambah `allow … if false` TIDAK menolak apa pun (run 7 Okt): izin create/update
    blok itu DICABUT — `allow read, write` jadi `allow read, delete`, `allow write` jadi `allow delete`, baris create/update dibuang. Baca & hapus tetap."""
    m = blok_aturan(ATURAN_REPO, koleksi)
    assert m, 'blok aturan ' + koleksi + ' tidak ketemu — perbarui gladi'
    baris = []
    for b in m.group(1).split('\n'):
        t = b.strip()
        if re.match(r'allow (create|update)(, (create|update))*:', t): continue
        b = b.replace('allow read, write:', 'allow read, delete:').replace('allow write:', 'allow delete:')
        assert not re.search(r'allow [^:]*\b(create|update|write)\b', b), 'bentuk allow belum dikenal gladi: ' + t
        baris.append(b)
    baris.append('      // GLADI: create/update DICABUT sementara (penolakan di tengah ritual)')
    return ATURAN_REPO[:m.start(1)] + '\n'.join(baris) + ATURAN_REPO[m.end(1):]


def blok_aturan(teks, koleksi):
    """Isi blok `match /<koleksi>/{id} { … }` (group 1) di teks aturan."""
    return re.search(r'\n    match /' + re.escape(koleksi) + r'/\{[a-zA-Z]+\} \{\n(.*?)\n    \}\n', teks, re.S)


# koleksi yang diarsip tutup buku (beku.js tbDaftarKoleksi) — dibandingkan isinya sebelum ritual ↔ sesudah pembatalan
KOLEKSI_2026 = ['penjualan', 'batchMasuk', 'produksiKemasan', 'retur', 'karantina', 'pengeluaranHarian', 'pesanan', 'setoranKas', 'penyesuaianKemasan', 'amplopLaba', 'modalOwner',
                'utangPemasokMutasi', 'utangOwnerMutasi', 'tembusanStok', 'stokBahanKemasan', 'stokBahanLiteran', 'piutangMutasi', 'kasbonMutasi', 'penyesuaianStok', 'tutupHari', 'biayaBulanan']


def banding_isi(awal, kini=None):
    kini = kini if kini is not None else potret_isi(KOLEKSI_2026); arsip = len(jalankan_query('arsipTahun'))
    lebih = {k: len(set(kini.get(k, {})) - set(awal.get(k, {}))) for k in KOLEKSI_2026}; kurang = {k: len(set(awal.get(k, {})) - set(kini.get(k, {}))) for k in KOLEKSI_2026}
    ubah = {k: sum(1 for i in awal.get(k, {}) if i in kini.get(k, {}) and awal[k][i] != kini[k][i]) for k in KOLEKSI_2026}
    contoh = next(([k, i] for k in KOLEKSI_2026 for i in awal.get(k, {}) if i in kini.get(k, {}) and awal[k][i] != kini[k][i]), None)
    saring = lambda d: {k: v for k, v in d.items() if v}
    return {'sama': not saring(lebih) and not saring(kurang) and not saring(ubah), 'lebih': saring(lebih), 'kurang': saring(kurang), 'ubah': saring(ubah), 'contohUbah': contoh,
            'arsip': arsip, 'dokumen': sum(len(v) for v in kini.values())}


# ---- klaim ritual DIPERIKSA DI SERVER (bukan cache halaman yang bisa berisi tulisan tertunda) ----
UANG_TITIK = ('tanggal', 'laci', 'rekening', 'amplop', 'brankas')   # isi titik kas yang dibandingkan (kolom atribusi & diubahPada boleh berganti)
HARAP_SERVER = {   # jenis → status berita acara 2026 di server yang ditunggu
    'berjalan': 'berjalan', 'arsipDitolak': 'terkunci', 'batalSebelum': 'dibatalkan', 'arsipHabis': 'terkunci', 'batalSesudah': 'dibatalkan', 'selesai': 'selesai'}


def awal_ritual():
    """Isi server sebelum ritual (sesudah data contoh dimuat): 21 koleksi 2026 + titik kas & penanda tutup buku."""
    return {'isi': potret_isi(KOLEKSI_2026), 'pengaturan': {i: ambil_dok('pengaturan', i) for i in ('titikKas', 'tutupBuku')}}


def keadaan_server(jenis, awal, batas=120):
    """Klaim ritual di SERVER: menunggu (≤ batas dtk) berita acara 2026 di server berstatus yang diharapkan — tulisan halaman bisa masih di jalan — lalu
    menilai arsipTahun, dokumen 2026 asli di koleksi asal, saldo pembuka, penanda tutupBuku, titik kas, isi 21 koleksi. → {ok, gagal: [kalimat], …angka}."""
    harap = HARAP_SERVER[jenis]; t0 = time.time(); acara = None
    while True:
        acara = ambil_dok('tutupBukuAcara', '2026') or {}
        if acara.get('status') == harap or time.time() - t0 > batas: break
        time.sleep(2)
    isi = potret_isi(KOLEKSI_2026)
    asli = {(k, i) for k in KOLEKSI_2026 for i in awal['isi'].get(k, {})}
    arsip = {tuple(i.split('|', 2)[1:]) for i in (id_dari_nama(d['name']) for d in jalankan_query('arsipTahun')) if i.startswith('2026|')}
    buka = lambda d: bool(d.get('tutupBuku')) and d.get('tahunDari') == 2026
    pembuka = sum(1 for k in KOLEKSI_2026 for d in isi.get(k, {}).values() if buka(d))
    sisa = sum(1 for k, i in asli if i in isi.get(k, {}))                                                        # dokumen 2026 asli yang masih di koleksi asal
    lain = sum(1 for k in KOLEKSI_2026 for i, d in isi.get(k, {}).items() if not buka(d) and (k, i) not in asli)  # dokumen asing (bukan asli, bukan pembuka)
    tb = ambil_dok('pengaturan', 'tutupBuku'); tk = ambil_dok('pengaturan', 'titikKas') or {}; tk0 = awal['pengaturan'].get('titikKas') or {}
    titik_sama = all(tk.get(k) == tk0.get(k) for k in UANG_TITIK)
    nA, nP = acara.get('nArsip'), acara.get('nPembuka')
    r = {'jenis': jenis, 'detikTunggu': round(time.time() - t0, 1), 'acara': acara.get('status'), 'nArsipAcara': nA, 'nPembukaAcara': nP, 'arsip': len(arsip),
         'pembuka': pembuka, 'sisaAsli': sisa, 'asing': lain, 'asli': len(asli), 'tutupBuku': tb and {k: tb.get(k) for k in ('tahunDitutup', 'dibatalkan')},
         'titikKasSama': titik_sama, 'era': None}
    g = []
    if acara.get('status') != harap: g.append('berita acara 2026 di server "%s", harusnya "%s" (ditunggu %d dtk)' % (acara.get('status'), harap, batas))
    if jenis in ('berjalan',):
        if not (0 < pembuka < (nP or 0)): g.append('saldo pembuka di server %d — harusnya sebagian (1 … %s) karena kiriman berikutnya ditolak' % (pembuka, (nP or 0) - 1))
        if arsip: g.append('arsipTahun di server %d — belum boleh ada arsip' % len(arsip))
        if sisa != len(asli): g.append('%d dokumen 2026 sudah hilang dari koleksi asal' % (len(asli) - sisa))
    if jenis == 'arsipDitolak':
        if pembuka != nP: g.append('saldo pembuka di server %d ≠ nPembuka berita acara %s' % (pembuka, nP))
        if arsip: g.append('arsipTahun di server %d — arsip potongan pertama harusnya DITOLAK' % len(arsip))
        if sisa != len(asli): g.append('%d dokumen 2026 hilang dari koleksi asal padahal arsip ditolak' % (len(asli) - sisa))
    if jenis in ('arsipHabis', 'selesai'):
        if arsip != asli: g.append('arsipTahun di server ≠ dokumen 2026 asli: %d kurang, %d asing' % (len(asli - arsip), len(arsip - asli)))
        if nA != len(arsip): g.append('arsipTahun di server %d ≠ nArsip berita acara %s' % (len(arsip), nA))
        if sisa: g.append('%d dokumen 2026 asli MASIH di koleksi asal (arsip belum habis di server)' % sisa)
        if lain: g.append('%d dokumen asing di koleksi 2026' % lain)
        if pembuka != nP: g.append('saldo pembuka di server %d ≠ nPembuka berita acara %s' % (pembuka, nP))
        if not tb or tb.get('tahunDitutup') != 2026: g.append('penanda pengaturan/tutupBuku %s — harusnya tahunDitutup 2026' % r['tutupBuku'])
        # Paket B (#114): potret 2026 di berita acara — Laporan, Pajak & Dasbor membacanya sesudah arsip (12 bulan, omzet per hari)
        pt = acara.get('potret') or {}; r['potret'] = {'tahun': pt.get('tahun'), 'bulan': len(pt.get('bulan') or {}), 'hari': len(pt.get('hari') or {})}
        if pt.get('tahun') != 2026 or len(pt.get('bulan') or {}) != 12 or not pt.get('hari'): g.append('potret 2026 di berita acara server tidak utuh: %s' % r['potret'])
    if jenis in ('batalSebelum', 'batalSesudah'):
        bi = banding_isi(awal['isi'], isi); r['banding'] = bi
        if not bi['sama']: g.append('isi 21 koleksi 2026 ≠ sebelum ritual: lebih %s, kurang %s, berubah %s' % (bi['lebih'], bi['kurang'], bi['ubah']))
        if arsip: g.append('arsipTahun di server masih %d dokumen' % len(arsip))
        if pembuka: g.append('saldo pembuka 2026 di server masih %d dokumen' % pembuka)
        if not titik_sama: g.append('titik kas di server ≠ sebelum ritual: %s vs %s' % ({k: tk.get(k) for k in UANG_TITIK}, {k: tk0.get(k) for k in UANG_TITIK}))
        if jenis == 'batalSebelum' and tb != awal['pengaturan'].get('tutupBuku'): g.append('penanda pengaturan/tutupBuku berubah padahal penanda belum terkirim: %s' % r['tutupBuku'])
        if jenis == 'batalSesudah' and (not tb or tb.get('tahunDitutup') not in (0, None) or tb.get('dibatalkan') != 2026):
            g.append('penanda pengaturan/tutupBuku %s — harusnya dinetralkan (tahunDitutup 0, dibatalkan 2026)' % r['tutupBuku'])
    r['gagal'] = g; r['ok'] = not g
    return r


def putusan_server(hari, alasan, batas=60):
    """Putusan per tanggal di SERVER: dokumen aturanToko/putusanHari berisi tepat tanggal-tanggal itu, "diterima", dengan alasan yang diketik."""
    t0 = time.time()
    while True:
        d = ambil_dok('aturanToko', 'putusanHari')
        if d or time.time() - t0 > batas: break
        time.sleep(2)
    H = (d or {}).get('hari') or {}
    salah = [t for t in hari if not (isinstance(H.get(t), dict) and H[t].get('jenis') == 'diterima' and H[t].get('alasan') == alasan)]
    asing = sorted(set(H) - set(hari))
    return {'ok': bool(d) and not salah and not asing, 'ada': bool(d), 'tanggal': len(H), 'harap': len(hari), 'salah': salah[:5], 'asing': asing[:5]}


# Firestore emulator menulis firestore-debug.log di folder kerja emulators:exec. "too many pending messagings in the back channel" = antrean WebChannel
# emulator penuh (10.000 pesan) → kanal diputus, pendengar halaman tidak menerima data. Dihitung per skenario supaya penyebabnya terbaca, bukan ditebak.
LOG_EMULATOR = os.path.join(os.getcwd(), 'firestore-debug.log')
_log_pos = [0]


def log_emulator_baru():
    """→ {'penuh': n baris antrean penuh, 'putus': n kanal diputus} sejak dipanggil terakhir (0 kalau log tidak ada)."""
    try:
        with open(LOG_EMULATOR, 'rb') as f:
            f.seek(_log_pos[0]); n = {'penuh': 0, 'putus': 0}
            while True:
                b = f.read(8 << 20)
                if not b: break
                n['penuh'] += b.count(b'too many pending messagings'); n['putus'] += b.count(b'abort the channel')
            _log_pos[0] = f.tell(); return n
    except OSError: return {'penuh': 0, 'putus': 0}



# ============================== salinan /baru/ untuk uji ==============================
def jam_palsu(iso):
    """Jam halaman = iso lalu BERJALAN (bukan beku: SDK Firebase & penunggu skenario butuh waktu yang maju). Pola Date pengganti alat uji lain.
    Disisip SEBELUM meta CSP → tidak terkena CSP salinan."""
    return ("<script>(function(){var R=Date,g=new R(" + json.dumps(iso) + ").getTime()-R.now();"
            "function D(a,b,c,d,e,f,h){if(!(this instanceof D))return new R(R.now()+g).toString();if(arguments.length===0)return new R(R.now()+g);"
            "if(arguments.length===1)return new R(a);return new R(a,b,c===undefined?1:c,d||0,e||0,f||0,h||0);}"
            "D.prototype=R.prototype;D.now=function(){return R.now()+g;};D.UTC=R.UTC;D.parse=R.parse;window.Date=D;window.__jamGladi=" + json.dumps(iso) + ";"
            # pelanggaran CSP salinan dicatat SEJAK AWAL (sebelum app.js menyambung): sambungan yang ditolak connect-src = halaman mencoba server lain
            "var V=window.__gladiCsp=[];document.addEventListener('securitypolicyviolation',function(e){if(V.length<40)V.push((e.violatedDirective||e.effectiveDirective||'?')+' '+String(e.blockedURI||'').slice(0,160));});"
            "})();</script>")


FIREBASE_SUNGGUHAN = re.compile(r'^https://[a-z0-9.-]+\.googleapis\.com$')   # Firestore / Auth / token Google — salinan uji tidak boleh menyambung ke sana


def csp_salinan(t):
    """connect-src salinan = connect-src situs − host Firebase sungguhan (*.googleapis.com) + alamat emulator (Firestore & Auth) — direktif lain, hash script
    sebaris, sumber lain TETAP. Pertahanan kedua gagal-tertutup: kalaupun halaman jatuh ke proyek toko, peramban menolak sambungannya."""
    m = re.search(r'(<meta http-equiv="Content-Security-Policy" content="[^"]*?connect-src )([^;"]*)', t)
    assert m, 'meta CSP /baru/ tanpa connect-src — perbarui gladi'
    sumber = [x for x in m.group(2).split() if not FIREBASE_SUNGGUHAN.match(x)]
    assert len(sumber) < len(m.group(2).split()), 'connect-src /baru/ tanpa host *.googleapis.com — perbarui gladi'
    return t[:m.end(1)] + ' '.join(sumber + ['http://' + FS_HOST, 'http://' + AUTH_HOST]) + t[m.end():]


def salinan_index(t, jam):
    assert t.count('<head>') == 1 and t.count('</body>') == 1 and '<script type="module" src="js/app.js"></script>' in t
    t = csp_salinan(t)
    return t.replace('<head>', '<head>' + jam_palsu(jam), 1).replace('</body>', '<script type="module" src="/_gladi/skenario.js"></script>\n</body>', 1)


def siapkan(jam, rusak=None):
    """Folder kerja: baru/ (salinan) — index.html (CSP salinan, jam palsu, skenario), firebase.js (Firestore lewat SDK penghitung), app.js (pegangan layar)."""
    d = tempfile.mkdtemp(prefix='gladi-'); shutil.copytree(os.path.join(AKAR, 'baru'), os.path.join(d, 'baru'))
    def ubah(rel, f):
        p = os.path.join(d, 'baru', rel); s = open(p, encoding='utf-8').read(); open(p, 'w', encoding='utf-8').write(f(s))
    ubah('index.html', lambda s: salinan_index(s, jam))
    def fb(s):
        assert s.count(SDK + 'firebase-firestore.js') == 1, 'impor Firestore di firebase.js berubah — perbarui gladi'
        return s.replace(SDK + 'firebase-firestore.js', '/_gladi/firebase-firestore.js')
    ubah('js/data/firebase.js', fb)
    ubah('js/app.js', lambda s: s + '\nwindow.__gladiLayar = { uang, jual: layar };   // gladi_tutup_buku: pegangan layar (salinan uji saja)\n')
    for rel, lama, baru in (rusak or []):
        def r(s, lama=lama, baru=baru):
            assert s.count(lama) == 1, 'kontrol basi: ' + rel + ' · ' + lama[:70]
            return s.replace(lama, baru, 1)
        ubah(rel, r)
    return d


# SDK Firestore ASLI + penghitung dokumen yang DITERIMA halaman dari server (pendengar & getDocs). Bukan pengganti: semua ekspor SDK diteruskan,
# hanya onSnapshot & getDocs dibungkus. Perkiraan baca Firestore: tiap dokumen yang masuk/berubah di hasil pendengar & tiap dokumen getDocs.
SDK_PENGHITUNG = r"""
export * from '__SDK__firebase-firestore.js';
import { onSnapshot as _onSnapshot, getDocs as _getDocs } from '__SDK__firebase-firestore.js';
const B = (window.__gladiBaca = window.__gladiBaca || { dokumen: 0, perKoleksi: {} });
const nama = (r) => { try { if (r && typeof r.path === 'string') return r.path.split('/')[0]; const q = r && r._query; return q && q.path && q.path.segments ? q.path.segments[0] : '?'; } catch (e) { return '?'; } };
const tambah = (k, n) => { if (!n) return; B.dokumen += n; B.perKoleksi[k] = (B.perKoleksi[k] || 0) + n; };
function hitung(k, snap) {
  if (!snap || !snap.metadata || snap.metadata.fromCache) return;
  if (typeof snap.docChanges === 'function') { let n = 0; snap.docChanges().forEach((c) => { if ((c.type === 'added' || c.type === 'modified') && !c.doc.metadata.hasPendingWrites) n += 1; }); tambah(k, n); }
  else if (typeof snap.exists === 'function' && snap.exists() && !snap.metadata.hasPendingWrites) tambah(k, 1);
}
export function onSnapshot(ref, ...args) {
  const k = nama(ref); const i = args.findIndex((a) => typeof a === 'function');
  if (i >= 0) { const asli = args[i]; args[i] = (snap) => { try { hitung(k, snap); } catch (e) { /* penghitung tidak boleh mengganggu */ } return asli(snap); }; }
  return _onSnapshot(ref, ...args);
}
export async function getDocs(q) { const s = await _getDocs(q); try { if (!s.metadata.fromCache) tambah(nama(q), s.size); } catch (e) { /* abaikan */ } return s; }
""".replace('__SDK__', SDK)

# Skenario di halaman. Langkah = fungsi bernama di LANGKAH; urutannya dari konfig (SKENARIO di Python). Tiap langkah melapor ke server uji (/_langkah)
# yang MENGUKUR isi emulator sebelum menjawab — halaman menunggu jawaban, jadi hitungan tulis/hapus jatuh ke langkah yang benar.
SKENARIO_JS = r"""
import * as fb from '/baru/js/data/firebase.js';
import * as toko from '/baru/js/data/toko.js';
import { KOLEKSI } from '/baru/js/data/koleksi.js';
import * as BK from '/baru/js/layar/tutup-buku-logika.js';
const K = await (await fetch('/_gladi/konfig.json', { cache: 'no-store' })).json();
const konsol = []; const errAsli = console.error;
console.error = function () { try { konsol.push(Array.from(arguments).map((x) => String(x && x.stack ? x.stack : x)).join(' ').slice(0, 400)); } catch (e) { /* abaikan */ } return errAsli.apply(console, arguments); };
window.addEventListener('error', (e) => konsol.push('error: ' + String(e.message || e).slice(0, 300)));
window.addEventListener('unhandledrejection', (e) => konsol.push('rejection: ' + String((e.reason && (e.reason.stack || e.reason.message)) || e.reason).slice(0, 400)));
const tunggu = (ms) => new Promise((r) => setTimeout(r, ms));
async function sampai(f, ms, apa) { const t0 = performance.now(); while (performance.now() - t0 < ms) { try { const v = f(); if (v) return v; } catch (e) { /* belum */ } await tunggu(120); } throw new Error('tidak tercapai dalam ' + Math.round(ms / 1000) + ' dtk: ' + apa); }
let ST = {}; fb.dengarkanStatus((s) => { ST = s; });
const $ = (id) => document.getElementById(id);
const U = () => window.__gladiLayar.uang; const su = () => U().keadaan.baca();
const akarU = () => $('layarUang');
const ringkasKM = () => { const k = BK.kemajuanBuku(); return k ? { fase: k.fase, tahun: k.tahun, teks: k.teks, sudah: k.sudah || 0, total: k.total || 0 } : null; };
const acara = () => { const a = toko.ambilTutupBukuAcara().find((x) => Number(x.tahun) === 2026); return a ? { status: a.status, nPembuka: a.nPembuka, nArsip: a.nArsip, kiriman: a.rencana ? a.rencana.n : null,
  getRencana: a.rencana && Array.isArray(a.rencana.kiriman) ? a.rencana.kiriman.reduce((n, k) => n + (Number(k.get) || 0), 0) : null, putusanHari: Array.isArray(a.putusanHari) ? a.putusanHari.filter((h) => h.alasan).length : null } : null; };
// perkiraan kuota yang ditampilkan halaman (kartu "Perkiraan kuota Firestore", Paket A) — pembanding angka terukur gladi
const kuotaHalaman = () => { try { const Q = BK.perkiraanKuota(2026, new Date()); return { ritual: Q.ritual, batal: Q.batal, muat: Q.muat, nArsip: Q.nArsip, nPembuka: Q.nPembuka, kiriman: Q.kiriman }; } catch (e) { return { galat: String(e) }; } };
const teksBilah = () => [...document.querySelectorAll('.bilah-uji')].map((e) => e.textContent.trim()).join(' | ');
function potret() {
  const s = su(); const A = akarU();
  const g = [...A.querySelectorAll('.tb-cek[data-k^="g-"]')].map((e) => ({ id: (e.dataset.k || '').replace(/^g-/, ''), ok: e.classList.contains('ok'), teks: (e.children[1] && e.children[1].children[0] ? e.children[1].children[0].textContent : ''), ket: (e.querySelector('.k') || {}).textContent || '' }));
  const tp = A.querySelector('[data-aksi="bkPeriksa"]'); const kartu = A.querySelector('[data-k="tb-lanjut"], [data-k="tb-selesaikan"]');
  return { modeB: s.modeB, langkahB: Object.assign({}, s.langkahB), kabar: s.kabar, kabarAwas: !!s.kabarAwas, selesaiLatihan: !!s.selesaiLatihan, sibuk: !!s.sibuk, bukaB: s.bukaB,
    gerbang: g, tombolPeriksa: tp ? { teks: tp.textContent.trim(), kelas: tp.className } : null, km: ringkasKM(), acara: acara(), era: BK.bkEra(),
    kartuLanjut: kartu ? { k: kartu.dataset.k, teks: kartu.textContent.trim().slice(0, 300), tombol: [...kartu.querySelectorAll('[data-aksi]')].map((e) => ({ aksi: e.dataset.aksi, teks: e.textContent.trim(), mati: e.classList.contains('mati') })) } : null,
    tombolBatal: !!A.querySelector('.kaca-btn[data-aksi="bkBatal"]'), antre: (ST.antre || []).length, menunggu: ST.menunggu || 0, lokal: ST.lokal || null, galatFb: ST.galat || '' };
}
const salinBaca = () => JSON.parse(JSON.stringify(window.__gladiBaca || { dokumen: 0, perKoleksi: {} }));
async function lapor(nama, info, minta) {
  const r = await fetch('/_langkah', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ nama, info: info || {}, baca: salinBaca(), minta: minta || null }) });
  const j = await r.json(); if (!j.ok) throw new Error('server uji menolak langkah ' + nama + ': ' + j.pesan); return j;
}
async function ketuk(sel, apa, harap, ms) {
  const el = akarU().querySelector(sel);
  if (!el) throw new Error('tombol tidak ada: ' + apa + ' (' + sel + ') · yang ada: ' + [...new Set([...akarU().querySelectorAll('[data-aksi]')].map((e) => e.dataset.aksi))].join(','));
  el.click(); await tunggu(400);
  await sampai(() => !su().sibuk && (!harap || harap()), ms || 120000, apa);
  await tunggu(300);
}
const ketukLapor = async (nama, sel, harap, ms, minta) => { await ketuk(sel, nama, harap, ms); return lapor(nama, potret(), minta); };
const PERIKSA = '[data-aksi="bkPeriksa"]';
const L = {
  async masuk() {
    // GAGAL-TERTUTUP: formulir masuk (email owner contoh + sandi) HANYA diisi bila halaman jelas tersambung ke server tiruan proyek demo — bilah
    // "SERVER TIRUAN <proyek demo>" tampil, bukan "DITOLAK". Tanpa itu skenario berhenti di sini, sebelum apa pun diketik.
    await sampai(() => teksBilah().indexOf('SERVER TIRUAN') >= 0, 30000, 'bilah SERVER TIRUAN tampil');
    const bilah = teksBilah();
    if (bilah.indexOf('SERVER TIRUAN ' + K.proyek) < 0 || bilah.indexOf('DITOLAK') >= 0) throw new Error('bukan server tiruan ' + K.proyek + ' — formulir masuk TIDAK diisi: ' + bilah.slice(0, 300));
    await sampai(() => ST.masuk || ($('formMasuk') && !$('formMasuk').hidden), 90000, 'formulir Masuk tampil');
    if (!ST.masuk) { $('isianEmail').value = K.email; $('isianSandi').value = K.sandi; $('tombolMasuk').click(); }
    await sampai(() => ST.masuk && ST.akun && ST.akun.jenis === 'owner', 90000, 'masuk sebagai owner contoh');
    await lapor('masuk', { akun: ST.akun.jenis, sumber: toko.sumberData(), bilah: teksBilah() });
  },
  async muatPenuh() {
    // muat yang tidak selesai TETAP dilaporkan dulu (run 7 Okt kontrol 3: 600 dtk tanpa laporan → sebabnya tidak terbaca): server uji mencatat antrean
    // emulator selama muat, cache per koleksi & dokumen yang sampai per koleksi; baru sesudah itu skenario berhenti
    const t0 = performance.now(); let gagalMuat = '';
    try { await sampai(() => ST.koleksiTotal > 0 && ST.koleksiSiap >= ST.koleksiTotal, 300000, 'semua koleksi termuat'); } catch (e) { gagalMuat = e.message; }
    if (!gagalMuat) {
      try { await sampai(() => (window.__gladiBaca || {}).dokumen >= K.harapBaca, 180000, 'dokumen data contoh sampai di halaman'); } catch (e) { konsol.push('muat penuh: ' + e.message); }
      await tunggu(2500);
    }
    const n = {}; KOLEKSI.forEach((k) => { n[k.nama] = toko.cacheMentah(k.cache).length; });
    await lapor('muat penuh', { detik: Math.round((performance.now() - t0) / 100) / 10, koleksiSiap: ST.koleksiSiap, koleksiTotal: ST.koleksiTotal, ditolak: ST.ditolak || [], galat: ST.galat || '', offline: !!ST.offline, cache: n,
      gagalMuat, diterima: salinBaca().perKoleksi });
    if (gagalMuat) throw new Error(gagalMuat + ' — koleksi siap ' + ST.koleksiSiap + ' dari ' + ST.koleksiTotal + ', dokumen diterima ' + salinBaca().dokumen);
  },
  async bukaTutupBuku() {
    document.querySelector('[data-tujuan="uang"]').click();
    await sampai(() => akarU().querySelector('[data-aksi="keluarga"][data-nama="buku"]'), 60000, 'layar Uang tampil');
    await ketuk('[data-aksi="keluarga"][data-nama="buku"]', 'keluarga Tutup buku', () => akarU().querySelector(PERIKSA));
    await lapor('buka Uang › Tutup buku', Object.assign(potret(), { kuota: kuotaHalaman() }));
  },
  async latihan() {
    await ketukLapor('LATIHAN dipilih', '[data-aksi="bkMode"][data-m="latihan"]', () => su().modeB === 'latihan');
    await ketukLapor('1 periksa', PERIKSA, () => !!su().langkahB.periksa);
    await ketukLapor('2 cadangan sebelum', '[data-aksi="bkCadangan"][data-k-cad="cadangan1"]', () => !!su().langkahB.cadangan1);
    await ketukLapor('3 arsip', '[data-aksi="bkArsip"]', () => !!su().langkahB.arsip);
    await ketukLapor('4 saldo pembuka', '[data-aksi="bkSaldo"]', () => !!su().langkahB.saldo);
    await ketukLapor('5a pilih saksi', '[data-aksi="bkSaksi"][data-nama="' + K.saksi + '"]', () => su().saksiB === K.saksi);
    await ketukLapor('5b paraf owner', '[data-aksi="bkParaf"][data-siapa="owner"]', () => su().parafB.owner);
    await ketukLapor('5c paraf saksi', '[data-aksi="bkParaf"][data-siapa="saksi"]', () => !!su().langkahB.paraf);
    await ketukLapor('6a kunci (ketukan 1)', '[data-aksi="bkKunci"]', () => su().siapKunci || !!su().langkahB.kunci);
    await ketukLapor('6b kunci (ketukan 2)', '[data-aksi="bkKunci"]', () => !!su().langkahB.kunci);
    await ketukLapor('7 selesai latihan', '[data-aksi="bkSelesaiLatihan"]', () => su().selesaiLatihan);
  },
  async sungguhan() { await ketukLapor('SUNGGUHAN dipilih', '[data-aksi="bkMode"][data-m="sungguhan"]', () => su().modeB === 'sungguhan' || su().kabarAwas); },
  async gerbangDiblokir() { await ketukLapor('1 periksa (diblokir gerbang)', PERIKSA, () => su().kabarAwas || !!su().langkahB.periksa); },
  // Paket A (A1): tiap hari tanpa tutup hari diputus "tidak ditutup — diterima apa adanya" + alasan, lewat kolom di gerbang g1 → "Simpan putusan"
  async putusanG1() {
    const kolom = 'input[data-ketik="bkPutusKetik"]'; const tgl = [...akarU().querySelectorAll(kolom)].map((e) => e.dataset.tgl);
    if (!tgl.length) throw new Error('kolom alasan putusan g1 tidak ada · yang ada: ' + [...new Set([...akarU().querySelectorAll('[data-k]')].map((e) => e.dataset.k))].slice(0, 30).join(','));
    for (const t of tgl) {   // diketik seperti orang: nilai + peristiwa input per kolom (layar menggambar ulang tiap ketikan → kolomnya dicari lagi)
      const el = akarU().querySelector(kolom + '[data-tgl="' + t + '"]'); if (!el) throw new Error('kolom alasan ' + t + ' hilang');
      el.value = K.alasan; el.dispatchEvent(new Event('input', { bubbles: true })); await tunggu(40);
    }
    // beres = g1 hijau, tiap tanggal "diterima apa adanya", DAN putusannya sudah diakui server (antrean kosong — kalau tidak, g2 memblokir periksa berikutnya)
    const g1ok = () => { const g = akarU().querySelector('.tb-cek[data-k="g-g1"]'); return !!g && g.classList.contains('ok') && akarU().querySelectorAll('[data-k^="g1-20"] .th-cap.beres').length === tgl.length
      && !(ST.antre || []).length && !ST.menunggu; };
    await ketuk('[data-aksi="bkPutusSimpan"]', 'Simpan putusan', g1ok, 120000);
    await lapor('putusan per tanggal disimpan', Object.assign(potret(), { diketik: tgl, kabarPutus: su().kabar }));
  },
  async periksaBeres() { await ketukLapor('1 periksa (semua beres)', PERIKSA, () => !!su().langkahB.periksa || su().kabarAwas); },
  // DIAM: 5 dtk tanpa ketukan, lalu tunggu semua tulisan perangkat ini diakui server — tulisan yang tertunda dari langkah terakhir ikut terukur
  async diam() {
    await tunggu(5000); let h = '?'; try { h = (await fb.periksaSambungan(20000)).hasil; } catch (e) { h = 'galat: ' + String(e).slice(0, 120); }
    await lapor('diam: 5 dtk sesudah langkah terakhir', Object.assign(potret(), { sambungan: h }));
  },
  // ---- ritual SUNGGUHAN (data macet sesudah putusanG1). Gerbang / langkah tutup buku berubah → sesuaikan fungsi di sini, urutannya di SKENARIO (Python).
  async sampaiParaf() {
    await ketukLapor('1 periksa (semua beres)', PERIKSA, () => !!su().langkahB.periksa || su().kabarAwas);
    await ketukLapor('2 cadangan sebelum (unduh)', '[data-aksi="bkCadangan"][data-k-cad="cadangan1"]', () => !!su().langkahB.cadangan1 || su().kabarAwas, 300000);
    await ketukLapor('3 arsip (unduh berkas)', '[data-aksi="bkArsip"]', () => !!su().langkahB.arsip || su().kabarAwas, 300000);
    await ketukLapor('4 saldo pembuka', '[data-aksi="bkSaldo"]', () => !!su().langkahB.saldo);
    await ketuk('[data-aksi="bkSaksi"][data-nama="' + K.saksi + '"]', 'pilih saksi', () => su().saksiB === K.saksi);
    await ketuk('[data-aksi="bkParaf"][data-siapa="owner"]', 'paraf owner', () => su().parafB.owner);
    await ketukLapor('5 paraf owner + saksi', '[data-aksi="bkParaf"][data-siapa="saksi"]', () => !!su().langkahB.paraf);
  },
  async kunciTerputusPembuka() {
    await lapor('server mulai menolak saldo pembuka bon pemasok', potret(), 'tolak:utangPemasokMutasi');
    await ketuk('[data-aksi="bkKunci"]', 'kunci (ketukan 1)', () => su().siapKunci);
    await ketukLapor('6 kunci → kiriman saldo pembuka ditolak server', '[data-aksi="bkKunci"]', () => !!ringkasKM() || su().kabarAwas, 1800000, 'pulihkan');
  },
  async batalkanSebelumPenanda() {
    await ketuk('[data-k="tb-lanjut"] [data-aksi="bkBatal"]', 'batalkan (ketukan 1)', () => su().yakinBatalB === 2026);
    await ketukLapor('BATALKAN sebelum penanda', '[data-k="tb-lanjut"] [data-aksi="bkBatal"]', () => { const a = acara(); return a && a.status === 'dibatalkan' && !ringkasKM(); }, 1800000);
  },
  async mulaiLagi() {
    await ketukLapor('mulai lagi: SUNGGUHAN', '[data-aksi="bkMode"][data-m="sungguhan"]', () => su().modeB === 'sungguhan' && !su().langkahB.periksa);
    await L.sampaiParaf();
  },
  async kunciTerputusArsip() {
    await lapor('server mulai menolak arsip', potret(), 'tolak:arsipTahun');
    await ketuk('[data-aksi="bkKunci"]', 'kunci (ketukan 1)', () => su().siapKunci);
    await ketukLapor('6 kunci → saldo pembuka masuk, arsip ditolak server', '[data-aksi="bkKunci"]', () => { const k = ringkasKM(); return (k && k.fase === 'arsip') || su().kabarAwas; }, 1800000, 'pulihkan');
  },
  async lanjutkan() { await ketukLapor('LANJUTKAN arsip', '[data-k="tb-lanjut"] [data-aksi="bkLanjut"]', () => !ringkasKM() || ringkasKM().fase === 'selesaikan', 3600000); },
  async batalkanSesudahPenanda() {
    const sel = '.kaca-btn[data-aksi="bkBatal"], [data-k="tb-selesaikan"] [data-aksi="bkBatal"]';
    await ketuk(sel, 'batalkan (ketukan 1)', () => su().yakinBatalB === 2026);
    await ketukLapor('BATALKAN sesudah penanda', sel, () => { const a = acara(); return a && a.status === 'dibatalkan' && !ringkasKM(); }, 3600000);
  },
  async kunciPenuh() {
    await ketuk('[data-aksi="bkKunci"]', 'kunci (ketukan 1)', () => su().siapKunci);
    await ketukLapor('6 kunci → saldo pembuka + arsip penuh', '[data-aksi="bkKunci"]', () => { const k = ringkasKM(); return (k && k.fase === 'selesaikan') || (acara() && acara().status === 'terkunci' && !k) || su().kabarAwas; }, 3600000);
  },
  async selesai() {
    const sel = '[data-k="tb-selesaikan"] [data-aksi="bkCadangan"], .utama[data-aksi="bkCadangan"][data-k-cad="cadangan2"]';
    await ketukLapor('7 cadangan sesudah · SELESAI', sel, () => { const a = acara(); return (a && a.status === 'selesai') || su().kabarAwas; }, 600000);
  },
};
let galat = '';
try { for (const nama of K.langkah) { if (!L[nama]) throw new Error('langkah tidak dikenal: ' + nama); await L[nama](); } }
catch (e) { galat = String((e && (e.stack || e.message)) || e).slice(0, 1500); }
let akhir = null; try { akhir = potret(); } catch (e) { akhir = { galat: String(e) }; }
await fetch('/_hasil', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ galat, konsol: konsol.slice(-40), akhir, baca: salinBaca(), csp: (window.__gladiCsp || []).slice(0, 40) }) });
"""

# Skenario → (varian data, jam halaman, langkah). Semua MACET: sejak Paket A g1 dibuka lewat putusan per tanggal (putusanG1), seperti owner pada 1 Jan.
SKENARIO = {
    'latihan': ('macet', DC.JAM_LATIHAN, ['masuk', 'muatPenuh', 'bukaTutupBuku', 'latihan', 'diam']),
    'gerbang': ('macet', DC.JAM_SUNGGUHAN, ['masuk', 'muatPenuh', 'bukaTutupBuku', 'sungguhan', 'gerbangDiblokir', 'putusanG1', 'periksaBeres', 'diam']),
    'ritual': ('macet', DC.JAM_SUNGGUHAN, ['masuk', 'muatPenuh', 'bukaTutupBuku', 'sungguhan', 'putusanG1', 'sampaiParaf', 'kunciTerputusPembuka', 'batalkanSebelumPenanda',
                                           'mulaiLagi', 'kunciTerputusArsip', 'lanjutkan', 'batalkanSesudahPenanda', 'mulaiLagi', 'kunciPenuh', 'selesai', 'diam']),
    # kontrol saja (bukan bawaan workflow): muat penuh saja — kerusakan yang membuat data kurang tidak boleh ikut menjatuhkan langkah tutup buku sesudahnya
    'muatSaja': ('macet', DC.JAM_LATIHAN, ['masuk', 'muatPenuh', 'diam']),
    # kontrol saja: kunci penuh lalu batalkan sesudah penanda — cukup untuk kontrol pemulihan arsip, separuh waktu ritual
    'ritualPendek': ('macet', DC.JAM_SUNGGUHAN, ['masuk', 'muatPenuh', 'bukaTutupBuku', 'sungguhan', 'putusanG1', 'sampaiParaf', 'kunciPenuh', 'batalkanSesudahPenanda', 'diam']),
}
SKENARIO_BAWAAN = ['latihan', 'gerbang', 'ritual']


# ============================== server uji ==============================
def _ikat_tanpa_dns(self):
    socketserver.TCPServer.server_bind(self); self.server_name, self.server_port = self.server_address[:2]


class Pelayan(http.server.SimpleHTTPRequestHandler):
    keadaan = None
    def log_message(self, *a): pass
    def kirim(self, kode, isi, jenis):
        b = isi.encode('utf-8') if isinstance(isi, str) else isi
        self.send_response(kode); self.send_header('Content-Type', jenis); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        K = self.keadaan; j = self.path.split('?')[0]
        if j == '/_gladi/skenario.js': return self.kirim(200, SKENARIO_JS, 'text/javascript')
        if j == '/_gladi/firebase-firestore.js': return self.kirim(200, SDK_PENGHITUNG, 'text/javascript')
        if j == '/_gladi/konfig.json': return self.kirim(200, json.dumps(K['konfig']), 'application/json')
        return super().do_GET()
    def do_POST(self):
        K = self.keadaan; n = int(self.headers.get('Content-Length') or 0); isi = json.loads(self.rfile.read(n).decode('utf-8') or '{}')
        if self.path.startswith('/_langkah'):
            try: jawab = K['ukur'](isi)
            except Exception as e: jawab = {'ok': False, 'pesan': str(e)[:400]}
            return self.kirim(200, json.dumps(jawab), 'application/json')
        if self.path.startswith('/_hasil'):
            K['hasil'] = isi; K['selesai'].set(); return self.kirim(200, '{"ok":true}', 'application/json')
        self.send_response(404); self.end_headers()
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store'); super().end_headers()
    def guess_type(self, path):
        return 'text/javascript' if str(path).endswith('.js') else super().guess_type(path)


def layani(d, keadaan):
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    kelas = type('PelayanGladi', (Pelayan,), {'keadaan': keadaan})
    Srv = type('SrvGladi', (http.server.ThreadingHTTPServer,), {'request_queue_size': 256, 'daemon_threads': True, 'server_bind': _ikat_tanpa_dns})
    srv = Srv(('127.0.0.1', port), functools.partial(kelas, directory=d)); threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def jalankan_chrome(port, profil, batas, keadaan):
    """SATU Chrome headless; selesai = halaman mengirim /_hasil, atau batas waktu. Grup prosesnya dimatikan sesudahnya (CLAUDE.md)."""
    arg = [CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--disable-component-update', '--disable-background-networking',
           '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--user-data-dir=' + profil, '--window-size=1440,1000', '--hide-scrollbars',
           '--use-mock-keychain', '--password-store=basic']
    if sys.platform.startswith('linux'): arg.append('--no-sandbox')   # runner Ubuntu: sandbox userns dibatasi AppArmor; halaman = salinan lokal
    log = open(os.path.join(profil, '..', os.path.basename(profil) + '-chrome.log'), 'wb')
    url = 'http://127.0.0.1:%d/baru/index.html?emulator=%s' % (port, FS_HOST) + ('&emulatorAuth=' + AUTH_HOST if AUTH_HOST.split(':')[1] != '9099' else '')
    p = subprocess.Popen(arg + ['--enable-logging=stderr', url], stdout=subprocess.DEVNULL, stderr=log, start_new_session=True); log.close()
    t0 = time.time()
    try:
        while not keadaan['selesai'].is_set() and time.time() - t0 < batas and p.poll() is None: time.sleep(0.5)
        return keadaan['selesai'].is_set(), round(time.time() - t0, 1), p.poll()
    finally:
        try: os.killpg(p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError): p.kill()
        p.wait()


# ============================== satu skenario ==============================
def jalankan_skenario(nama, data, sandi, rusak=None, cetak=print, kait=None):
    varian, jam, langkah = SKENARIO[nama]
    meta = data['gladi']; d = siapkan(jam, rusak); profil = os.path.join(d, 'profil'); os.makedirs(profil)
    harap = sum(len(v) for k, v in data.items() if isinstance(v, list) and k != 'logAktivitas') + min(150, len(data.get('logAktivitas', [])))
    K = {'konfig': {'email': EMAIL_OWNER, 'sandi': sandi, 'langkah': langkah, 'saksi': meta['saksi'][0], 'harapBaca': harap, 'proyek': PROYEK, 'alasan': DC.ALASAN_PUTUS},
         'selesai': threading.Event(), 'hasil': None, 'langkah': [], 'kunci': threading.Lock()}
    K['potret'] = potret(); K['baca'] = 0; K['t'] = time.time(); log_emulator_baru()
    def ukur(isi):
        with K['kunci']:
            nama = isi.get('nama'); hasil_kait = None
            # cek SERVER langkah ini dulu (menunggu tulisan halaman sampai), baru potret — tulisan yang mendarat selama menunggu ikut langkah ini
            if (kait or {}).get(nama):
                try: hasil_kait = kait[nama]()
                except Exception as e: hasil_kait = {'ok': False, 'gagal': ['pemeriksa server jatuh: ' + str(e)[:300]]}
            p = potret(); tulis, hapus = beda(K['potret'], p); K['potret'] = p
            baca = int((isi.get('baca') or {}).get('dokumen') or 0); db = baca - K['baca']; K['baca'] = baca
            sendiri = {k: n for k, n in tulis.items() if k in DIDENGAR}
            r = {'nama': nama, 'detik': round(time.time() - K['t'], 1), 'baca': db + sum(sendiri.values()), 'bacaServer': db, 'bacaSendiri': sum(sendiri.values()),
                 'bacaPer': (isi.get('baca') or {}).get('perKoleksi'), 'tulis': sum(tulis.values()), 'hapus': sum(hapus.values()), 'tulisPer': tulis, 'hapusPer': hapus, 'info': isi.get('info') or {}}
            if hasil_kait is not None: r['kait'] = hasil_kait
            r['emulator'] = log_emulator_baru()
            if r['emulator']['penuh']: cetak('    !! emulator: antrean WebChannel penuh %d kali, kanal diputus %d kali' % (r['emulator']['penuh'], r['emulator']['putus']))
            K['t'] = time.time(); K['langkah'].append(r)
            cetak('  · %-52s %6.1f dtk · baca %6d · tulis %6d · hapus %6d%s' % (r['nama'][:52], r['detik'], r['baca'], r['tulis'], r['hapus'],
                                                                             ('  [' + ', '.join('%s +%d' % x for x in sorted(tulis.items())) + ']') if tulis and r['tulis'] < 60 else ''))
            m = isi.get('minta') or ''
            if m.startswith('tolak:'): pasang_aturan(aturan_tolak(m.split(':', 1)[1])); r['aturan'] = 'firestore.rules repo + ' + m.split(':', 1)[1] + ' ditolak'; cetak('    (aturan emulator: %s DITOLAK sementara)' % m.split(':', 1)[1])
            elif m == 'pulihkan': pasang_aturan(ATURAN_REPO); r['aturan'] = 'firestore.rules repo (dipulihkan)'; cetak('    (aturan emulator: firestore.rules repo dipulihkan)')
            return {'ok': True}
    K['ukur'] = ukur
    srv, port = layani(d, K)
    try:
        ok, detik, kode = jalankan_chrome(port, profil, TUNGGU_SKENARIO[nama], K)
    finally:
        srv.shutdown(); pasang_aturan(ATURAN_REPO)
        log = os.path.join(d, 'profil-chrome.log'); ekor = open(log, 'rb').read().decode('utf-8', 'replace').splitlines()[-30:] if os.path.exists(log) else []
        shutil.rmtree(d, ignore_errors=True)
    H = K['hasil'] or {}
    return {'nama': nama, 'varian': varian, 'jamHalaman': jam, 'langkahDiminta': langkah, 'selesai': ok, 'detik': detik, 'kodeChrome': kode, 'langkah': K['langkah'],
            'galat': H.get('galat') if ok else 'halaman tidak mengirim hasil dalam %d dtk (Chrome %s)' % (TUNGGU_SKENARIO[nama], kode),
            'konsol': H.get('konsol') or [], 'csp': H.get('csp') or [], 'akhir': H.get('akhir'), 'ekorChrome': [] if ok and not H.get('galat') else ekor}


# ============================== cek ==============================
def L_(S, nama, ke=0):
    """Langkah bernama `nama` (ke = urutan kemunculan; −1 = yang terakhir — ritual mengulang langkah yang sama sesudah pembatalan)."""
    xs = [x for x in S['langkah'] if x['nama'] == nama]
    return (xs[ke] if -len(xs) <= ke < len(xs) else None) if xs else None


def info(x, k=None):
    I = (x or {}).get('info') or {}
    return I if k is None else I.get(k)


def kait_cek(c, nama, x):
    """Cek dari pemeriksa SERVER (keadaan_server / putusan_server) yang dijalankan di langkah x."""
    K = (x or {}).get('kait')
    c.append((nama, bool(K) and K.get('ok'), K if K else TAK_TERCAPAI))


def cek_umum(S, data, c, tolak_sengaja=()):
    c.append(('skenario berjalan sampai akhir tanpa galat', S['selesai'] and not S['galat'], (S['galat'] or '')[:600]))
    m = L_(S, 'masuk'); bilah = info(m, 'bilah') or ''
    c.append(('masuk sebagai owner contoh di SERVER TIRUAN %s (bilah tampil SEBELUM formulir diisi, bukan "DITOLAK")' % PROYEK, bool(m) and info(m, 'akun') == 'owner'
              and ('SERVER TIRUAN ' + PROYEK) in bilah and 'DITOLAK' not in bilah, {k: info(m, k) for k in ('akun', 'bilah')} if m else TAK_TERCAPAI))
    mp = L_(S, 'muat penuh')
    if not mp: c.append(('muat penuh: semua koleksi siap — langkahnya tidak tercapai', False, TAK_TERCAPAI)); return
    I = mp['info']; kurang = {}
    for k, v in data.items():
        if not isinstance(v, list): continue
        harap = min(150, len(v)) if k == 'logAktivitas' else len(v)
        ada = (I.get('cache') or {}).get(k)
        if ada is None: kurang[k] = ('tidak didengar halaman', harap); continue
        if (ada < harap) or (k not in ('perangkatStatus', 'logAktivitas') and ada != harap): kurang[k] = (ada, harap)
    c.append(('muat penuh: semua koleksi siap, tak ada yang ditolak aturan, isi cache = data contoh per koleksi (%d dokumen)' % sum(len(v) for v in data.values() if isinstance(v, list)),
              I.get('koleksiSiap') == I.get('koleksiTotal') and not I.get('ditolak') and not I.get('galat') and not kurang, {'siap': [I.get('koleksiSiap'), I.get('koleksiTotal')], 'ditolak': I.get('ditolak'), 'galat': I.get('galat'), 'beda': kurang}))
    # Antrean penuh SAAT MUAT = halaman tidak pernah menerima data (run 7 Okt, data 17 rb) → gagal. Sesudah muat penuh, antrean penuh berasal dari sesi kanal
    # yang sudah ditinggal halaman (SDK menyambung ulang dengan token lanjut; emulator terus mengirimi kanal lama sampai kedaluwarsa — run 7 Okt: jutaan baris
    # di satu run, nol di run lain, semua cek isi tetap lulus) → hanya dilaporkan; isi halaman sendiri dinilai cek-cek lain (cache, langkah, isi server).
    muat = [x for x in S['langkah'] if x['nama'] in ('masuk', 'muat penuh')]
    penuh = sum((x.get('emulator') or {}).get('penuh', 0) for x in muat)
    S['antreanPenuhSesudahMuat'] = sum((x.get('emulator') or {}).get('penuh', 0) for x in S['langkah'] if x not in muat)
    c.append(('emulator tidak kewalahan saat muat: antrean WebChannel tidak penuh sampai muat penuh selesai (batas emulator 10.000 pesan per kanal)', bool(muat) and penuh == 0, {'penuh': penuh}))
    bocor = [x for x in S['konsol'] if ('permission' in x.lower() or 'FirebaseError' in x) and not any(k in x for k in tolak_sengaja)]
    c.append(('tidak ada galat izin / FirebaseError di konsol halaman' + (' (selain penolakan sengaja: ' + ', '.join(tolak_sengaja) + ')' if tolak_sengaja else ''), not bocor, bocor[:3]))
    # connect-src salinan = situs − host Firebase sungguhan + emulator: sambungan yang ditolak = halaman mencoba server SELAIN server tiruan
    tolakCsp = [x for x in S.get('csp') or [] if x.startswith('connect-src')]
    c.append(('halaman hanya bicara ke server tiruan & situs sendiri (0 sambungan ditolak connect-src salinan)', not tolakCsp, tolakCsp[:5]))
    if 'diam' in (S.get('langkahDiminta') or []):
        d = L_(S, 'diam: 5 dtk sesudah langkah terakhir')
        c.append(('DIAM di akhir skenario: 5 dtk tanpa ketukan, semua tulisan perangkat ini sudah diakui server (tulisan tertunda ikut terukur)', bool(d) and info(d, 'sambungan') == 'sampai',
                  {'sambungan': info(d, 'sambungan'), 'tulis': d['tulisPer'], 'hapus': d['hapusPer']} if d else TAK_TERCAPAI))


def tulisan_bukan_latar(langkah):
    t = {}
    for x in langkah:
        for k, n in x['tulisPer'].items():
            if k not in LATAR: t[k] = t.get(k, 0) + n
        for k, n in x['hapusPer'].items(): t['hapus:' + k] = t.get('hapus:' + k, 0) + n
    return t


def potong_langkah(S, dari, sampai=None):
    """Langkah dari kemunculan pertama `dari` sampai SEBELUM kemunculan pertama `sampai` (None = sampai akhir). [] kalau `dari` tidak tercapai."""
    i = next((n for n, x in enumerate(S['langkah']) if x['nama'] == dari), None)
    if i is None: return []
    j = next((n for n, x in enumerate(S['langkah']) if n > i and x['nama'] == sampai), len(S['langkah'])) if sampai else len(S['langkah'])
    return S['langkah'][i:j]


def cek_latihan(S, data, c):
    cek_umum(S, data, c)
    sesudah = potong_langkah(S, 'LATIHAN dipilih')
    akhir = L_(S, '7 selesai latihan')
    urut = ['periksa', 'cadangan1', 'arsip', 'saldo', 'paraf', 'kunci', 'cadangan2']
    c.append(('LATIHAN jalan sampai akhir: tujuh langkah beres, "Latihan selesai"', bool(akhir) and info(akhir, 'selesaiLatihan') and all(info(akhir, 'langkahB').get(k) for k in urut)
              and (info(akhir, 'kabar') or '').startswith('Latihan selesai'), {'langkahB': info(akhir, 'langkahB'), 'kabar': info(akhir, 'kabar')} if akhir else TAK_TERCAPAI))
    s6 = L_(S, '6b kunci (ketukan 2)')
    # Paket B (#114): kunci LATIHAN juga menyusun potret tahun (tanpa menulis) — kabarnya "Latihan: tidak ada yang dikunci. Potret 2026: …"; gagal = kabar awas
    c.append(('LATIHAN: 12 baris sebelum = sesudah (kunci latihan tidak ditolak "ada baris yang tidak sama") dan potret 2026 tersusun (Paket B)', bool(s6)
              and (info(s6, 'kabar') or '').startswith('Latihan: tidak ada yang dikunci. Potret 2026: ') and not info(s6, 'kabarAwas'),
              {'kabar': (info(s6, 'kabar') or '')[:300], 'kabarAwas': info(s6, 'kabarAwas')} if s6 else TAK_TERCAPAI))
    t = tulisan_bukan_latar(sesudah); diam = any(x['nama'].startswith('diam') for x in sesudah)
    c.append(('LATIHAN TANPA MENULIS: 0 tulis & 0 hapus ke server selama tujuh langkah DAN 5 dtk diam sesudahnya (selain denyut perangkat & katalog kasir)',
              bool(sesudah) and diam and not t, t if sesudah and diam else TAK_TERCAPAI))


def cek_putusan(S, data, c):
    """Paket A (A1): 'Simpan putusan' = SATU dokumen aturanToko/putusanHari (+ satu baris jejak) — isinya dicek di server — lalu g1 beres."""
    hari = data['gladi']['hariTanpaTutup']; p = L_(S, 'putusan per tanggal disimpan')
    G = info(p, 'gerbang') or []; g1 = next((g for g in G if g['id'] == 'g1'), None)
    t = {k: n for k, n in ((p or {}).get('tulisPer') or {}).items() if k not in LATAR}
    c.append(('"Simpan putusan" (%d tanggal diketik): tepat 1 dokumen aturanToko/putusanHari + 1 jejak, tanpa hapus; g1 jadi beres "%d hari tanpa tutup hari, semuanya sudah diputus"' % (len(hari), len(hari)),
              bool(p) and t == {'aturanToko': 1, 'logAktivitas': 1} and not p['hapusPer'] and bool(g1) and g1['ok'] and g1['ket'].startswith('%d hari tanpa tutup hari, semuanya sudah diputus' % len(hari))
              and len(info(p, 'diketik') or []) == len(hari), {'tulis': t, 'hapus': p['hapusPer'], 'g1': g1, 'diketik': len(info(p, 'diketik') or []), 'kabar': info(p, 'kabarPutus')} if p else TAK_TERCAPAI))
    kait_cek(c, 'putusan di SERVER: aturanToko/putusanHari berisi tepat %d tanggal "diterima" dengan alasan yang diketik' % len(hari), p)


def cek_gerbang(S, data, c):
    cek_umum(S, data, c)
    n = len(data['gladi']['hariTanpaTutup']); m = L_(S, 'SUNGGUHAN dipilih'); p = L_(S, '1 periksa (diblokir gerbang)')
    c.append(('1 Jan: mode SUNGGUHAN boleh dipilih (tahun 2026 sudah lewat)', bool(m) and info(m, 'modeB') == 'sungguhan' and not info(m, 'kabarAwas'), {'modeB': info(m, 'modeB'), 'kabar': info(m, 'kabar')} if m else TAK_TERCAPAI))
    G = info(m, 'gerbang') or []
    g1 = next((g for g in G if g['id'] == 'g1'), None); lain = [g for g in G if g['id'] != 'g1' and not g['ok']]
    c.append(('gerbang g1 tampil MEMBLOKIR: "%d hari belum ditutup & belum diputus: …"; gerbang lain beres' % n, bool(g1) and not g1['ok'] and g1['ket'].startswith('%d hari belum ditutup & belum diputus' % n)
              and not lain and len(G) >= 6, {'g1': g1, 'lain belum': lain, 'n': len(G)} if m else TAK_TERCAPAI))
    tp = info(m, 'tombolPeriksa') or {}
    c.append(('tombol periksa redup: "1 hal belum beres — bereskan dulu"', tp.get('teks') == '1 hal belum beres — bereskan dulu' and 'redup' in (tp.get('kelas') or ''), tp if m else TAK_TERCAPAI))
    c.append(('mengetuk periksa DITOLAK: langkah 1 tidak beres, kabar menyebut yang belum beres', bool(p) and not info(p, 'langkahB').get('periksa') and info(p, 'kabarAwas')
              and info(p, 'kabar') == '1 hal belum beres — bereskan dulu', {'langkahB': info(p, 'langkahB'), 'kabar': info(p, 'kabar')} if p else TAK_TERCAPAI))
    blok = potong_langkah(S, 'SUNGGUHAN dipilih', 'putusan per tanggal disimpan'); t = tulisan_bukan_latar(blok)
    c.append(('SUNGGUHAN yang diblokir tidak menulis apa pun ke server', bool(blok) and not t, t if blok else TAK_TERCAPAI))
    cek_putusan(S, data, c)
    b = L_(S, '1 periksa (semua beres)'); tp2 = info(b, 'tombolPeriksa') or {}
    c.append(('sesudah putusan: tombol "SEMUA BERES · LANJUT", periksa lolos (langkah 1 beres)', bool(b) and bool(info(b, 'langkahB').get('periksa')) and not info(b, 'kabarAwas')
              and tp2.get('teks') == 'SEMUA BERES · LANJUT', {'tombol': tp2, 'langkahB': info(b, 'langkahB'), 'kabar': info(b, 'kabar')} if b else TAK_TERCAPAI))
    sesudah = [x for x in potong_langkah(S, '1 periksa (semua beres)')]; t2 = tulisan_bukan_latar(sesudah)
    c.append(('periksa yang lolos & 5 dtk diam sesudahnya tidak menulis apa pun', bool(sesudah) and any(x['nama'].startswith('diam') for x in sesudah) and not t2, t2 if sesudah else TAK_TERCAPAI))


def cek_ritual(S, data, c):
    """Cek per langkah yang DIMINTA skenario (ritual penuh atau ritualPendek kontrol): halaman (kartu, berita acara di cache) DAN server (REST)."""
    cek_umum(S, data, c, tolak_sengaja=('utangPemasokMutasi', 'arsipTahun', 'insufficient permissions'))
    minta = S.get('langkahDiminta') or []
    if 'putusanG1' in minta: cek_putusan(S, data, c)
    if 'kunciTerputusPembuka' in minta:
        p = L_(S, '6 kunci → kiriman saldo pembuka ditolak server')
        km = info(p, 'km') or {}; tombol = [t['aksi'] for t in (info(p, 'kartuLanjut') or {}).get('tombol', [])]
        c.append(('kiriman saldo pembuka ke-2 ditolak server → berhenti di tengah; kartu "lanjutkan / batalkan" TERSEDIA', bool(p) and km.get('fase') == 'pembuka' and 'bkLanjut' in tombol and 'bkBatal' in tombol
                  and (info(p, 'acara') or {}).get('status') == 'berjalan', {'km': km, 'tombol': tombol, 'acara': info(p, 'acara')} if p else TAK_TERCAPAI))
        kait_cek(c, 'di SERVER: berita acara "berjalan", saldo pembuka baru sebagian, arsip kosong, dokumen 2026 utuh', p)
    if 'batalkanSebelumPenanda' in minta:
        b1 = L_(S, 'BATALKAN sebelum penanda')
        c.append(('BATALKAN SEBELUM PENANDA (halaman): berita acara "dibatalkan", era tetap, tidak ada yang tertunda', bool(b1) and (info(b1, 'acara') or {}).get('status') == 'dibatalkan'
                  and info(b1, 'era') is None and not info(b1, 'km'), {k: info(b1, k) for k in ('acara', 'era', 'km', 'kabar')} if b1 else TAK_TERCAPAI))
        kait_cek(c, 'BATALKAN SEBELUM PENANDA di SERVER: saldo pembuka ditarik habis, arsip kosong, penanda & titik kas tidak tersentuh, isi %d koleksi 2026 = sebelum ritual' % len(KOLEKSI_2026), b1)
    if 'kunciTerputusArsip' in minta:
        a = L_(S, '6 kunci → saldo pembuka masuk, arsip ditolak server')
        kmA = info(a, 'km') or {}; ktA = [t['aksi'] for t in (info(a, 'kartuLanjut') or {}).get('tombol', [])]
        c.append(('arsip ditolak server di potongan pertama → kartu "lanjutkan / batalkan" TERSEDIA (fase arsip, berita acara terkunci)', bool(a) and kmA.get('fase') == 'arsip' and 'bkLanjut' in ktA and 'bkBatal' in ktA,
                  {'km': kmA, 'tombol': ktA, 'acara': info(a, 'acara')} if a else TAK_TERCAPAI))
        kait_cek(c, 'di SERVER: berita acara "terkunci", saldo pembuka lengkap, arsip DITOLAK (kosong), dokumen 2026 utuh di koleksi asal', a)
    if 'lanjutkan' in minta:
        l = L_(S, 'LANJUTKAN arsip')
        c.append(('LANJUTKAN (halaman): pita tinggal "selesaikan"', bool(l) and (info(l, 'km') or {}).get('fase') in (None, 'selesaikan'), {'km': info(l, 'km'), 'kabar': info(l, 'kabar')} if l else TAK_TERCAPAI))
        kait_cek(c, 'LANJUTKAN di SERVER: arsipTahun = semua dokumen 2026 asli (= nArsip berita acara), 0 tersisa di koleksi asal, saldo pembuka = nPembuka, penanda tutupBuku 2026, potret 2026 di berita acara', l)
    if 'batalkanSesudahPenanda' in minta:
        b2 = L_(S, 'BATALKAN sesudah penanda')
        c.append(('BATALKAN SESUDAH PENANDA (halaman): berita acara "dibatalkan", era kembali kosong, tidak ada yang tertunda', bool(b2) and (info(b2, 'acara') or {}).get('status') == 'dibatalkan'
                  and info(b2, 'era') is None and not info(b2, 'km') and b2['hapus'] > 0, {k: info(b2, k) for k in ('acara', 'era', 'km', 'kabar')} if b2 else TAK_TERCAPAI))
        kait_cek(c, 'BATALKAN SESUDAH PENANDA di SERVER: isi %d koleksi 2026 = sebelum ritual, arsipTahun kosong, saldo pembuka ditarik habis, titik kas kembali, penanda tutupBuku dinetralkan' % len(KOLEKSI_2026), b2)
    if 'selesai' in minta:
        s = L_(S, '7 cadangan sesudah · SELESAI')
        c.append(('ritual penuh SELESAI (halaman): berita acara "selesai", era 2026, tidak ada yang tertunda', bool(s) and (info(s, 'acara') or {}).get('status') == 'selesai' and info(s, 'era') == 2026 and not info(s, 'km'),
                  {k: info(s, k) for k in ('acara', 'era', 'km', 'kabar')} if s else TAK_TERCAPAI))
        kait_cek(c, 'SELESAI di SERVER: berita acara "selesai", arsipTahun = semua dokumen 2026 asli (= nArsip), 0 tersisa, saldo pembuka = nPembuka, penanda tutupBuku 2026, potret 2026 di berita acara', s)


def cek_muat(S, data, c):
    cek_umum(S, data, c)


CEK = {'latihan': cek_latihan, 'gerbang': cek_gerbang, 'ritual': cek_ritual, 'ritualPendek': cek_ritual, 'muatSaja': cek_muat}


# jalur biaya kuota (skenario ritual): langkah mana yang dijumlah. Ritual BERSIH = yang dikerjakan owner tanpa penolakan/pembatalan: masuk, muat, putusan,
# lalu percobaan TERAKHIR (sesudah "mulai lagi" terakhir) sampai selesai & diam. Penolakan sengaja & pembatalan = jalur sendiri, bukan bagian ritual bersih.
def jalur_ritual(S):
    L = S['langkah']; nama = [x['nama'] for x in L]
    if 'mulai lagi: SUNGGUHAN' in nama:
        i = len(nama) - 1 - nama[::-1].index('mulai lagi: SUNGGUHAN')
        awal = [x for x in L[:nama.index('mulai lagi: SUNGGUHAN')] if x['nama'] in ('masuk', 'muat penuh', 'buka Uang › Tutup buku', 'SUNGGUHAN dipilih', 'putusan per tanggal disimpan')]
        bersih = awal + L[i:]
    else:
        bersih = [x for x in L if x['nama'] not in ('BATALKAN sebelum penanda', 'BATALKAN sesudah penanda')]
    J = [('ritual bersih — masuk, muat penuh, putusan, langkah 1–7 percobaan terakhir sampai selesai + diam', bersih, 'ritual')]
    b1 = [x for x in L if x['nama'] in ('6 kunci → kiriman saldo pembuka ditolak server', 'BATALKAN sebelum penanda')]
    if len(b1) == 2: J.append(('kunci yang berhenti di saldo pembuka + BATALKAN sebelum penanda', b1, None))
    b2 = [x for x in L if x['nama'] == 'BATALKAN sesudah penanda']
    if b2: J.append(('BATALKAN sesudah penanda (arsip sudah penuh) — biaya tambahan di atas ritual', b2, 'batal'))
    return J


# ============================== laporan ==============================
def rb(n):
    """Angka bergaya toko: 9.283 · 18,2 rb."""
    n = float(n)
    return format(int(round(n)), ',').replace(',', '.') if abs(n) < 10000 else ('%.1f rb' % (n / 1000.0)).replace('.', ',')


def jumlah(langkah):
    return {k: sum(x[k] for x in langkah) for k in ('baca', 'tulis', 'hapus')}


def kuota_ritual(S, lap):
    """Jalur biaya kuota skenario ritual: angka gladi, perkiraan skala toko (× TOKO_ARSIP ÷ arsip gladi), % batas Spark, perkiraan halaman, peringatan."""
    na = (lap['data'].get(S['varian']) or {}).get('nArsip') or next((x['kait'].get('nArsipAcara') for x in S['langkah'] if (x.get('kait') or {}).get('nArsipAcara')), None)
    if not na: return None
    f = TOKO_ARSIP / float(na); buka = L_(S, 'buka Uang › Tutup buku'); Q = info(buka, 'kuota') or {}
    out = {'nArsipGladi': na, 'pengali': round(f, 3), 'tokoArsip': TOKO_ARSIP, 'jalur': [], 'peringatan': []}
    for nama, langkah, jenis_halaman in jalur_ritual(S):
        g = jumlah(langkah); t = {k: g[k] * f for k in g}
        J = {'nama': nama, 'langkah': [x['nama'] for x in langkah], 'gladi': g, 'toko': {k: round(v) for k, v in t.items()}, 'persenToko': {k: round(100.0 * t[k] / SPARK[k], 1) for k in t},
             'halaman': Q.get(jenis_halaman) if jenis_halaman else None}
        out['jalur'].append(J)
    if len(out['jalur']) >= 1 and any(j['nama'].startswith('BATALKAN sesudah') for j in out['jalur']):
        r, b = out['jalur'][0], next(j for j in out['jalur'] if j['nama'].startswith('BATALKAN sesudah'))
        t = {k: r['toko'][k] + b['toko'][k] for k in r['toko']}
        out['jalur'].append({'nama': 'ritual bersih + BATALKAN sesudah penanda di HARI YANG SAMA', 'langkah': [], 'gladi': {k: r['gladi'][k] + b['gladi'][k] for k in r['gladi']},
                             'toko': t, 'persenToko': {k: round(100.0 * t[k] / SPARK[k], 1) for k in t}, 'halaman': None})
    for J in out['jalur']:
        for k in ('baca', 'tulis', 'hapus'):
            p = J['persenToko'][k]
            if p > 100: out['peringatan'].append('⛔ %s: %s %s di skala toko = %s%% batas Spark sehari — TIDAK MUAT satu hari' % (J['nama'], rb(J['toko'][k]), k, ('%.0f' % p)))
            elif p > 100 * MEPET: out['peringatan'].append('⚠ %s: %s %s di skala toko = %s%% batas Spark sehari — mepet (tulisan jualan hari itu ikut memakai kuota)' % (J['nama'], rb(J['toko'][k]), k, ('%.0f' % p)))
    return out


def ringkas_md(lap):
    out = ['## Gladi tutup buku — server tiruan (Firebase Emulator, aturan = `firestore.rules` repo, data contoh sintetis)', '',
           'Proyek emulator `%s` · firebase-tools %s · batas Spark per hari: baca %s · tulis %s · hapus %s' % (lap['proyek'], lap.get('firebaseTools', '?'), *[rb(SPARK[k]) for k in ('baca', 'tulis', 'hapus')]), '']
    for v, m in lap['data'].items():
        out.append('- data **%s**: %s dokumen, %d hari tanpa tutup hari%s' % (v, rb(m['dokumen']), len(m['hariTanpaTutup']), (' — ' + m['periksa']) if m.get('periksa') else ''))
    out.append('')
    for S in lap['skenario']:
        ok = all(x['ok'] for x in S['cek'])
        out += ['### %s %s — data %s, jam halaman %s (%s dtk)' % ('✅' if ok else '❌', S['nama'], S['varian'], S['jamHalaman'], S['detik']), '',
                'Per langkah (angka langkah itu saja; bukan jumlah berjalan):', '',
                '| langkah | dtk | baca | └ tulisan sendiri | tulis | hapus |', '|---|---:|---:|---:|---:|---:|']
        for x in S['langkah']:
            out.append('| %s%s | %s | %s | %s | %s | %s |' % (x['nama'], (' · _' + x['aturan'] + '_') if x.get('aturan') else '', x['detik'], rb(x['baca']), rb(x.get('bacaSendiri', 0)), rb(x['tulis']), rb(x['hapus'])))
        Q = S.get('kuota')
        if Q:
            out += ['', '**Kuota per jalur** — skala gladi (arsip %s dokumen) dan perkiraan skala toko (× %s → ±%s dokumen tahun 2026); %% = bagian batas Spark sehari:' % (
                rb(Q['nArsipGladi']), ('%.2f' % Q['pengali']).replace('.', ','), rb(Q['tokoArsip'])), '',
                '| jalur | baca | tulis | hapus | toko: baca | toko: tulis | toko: hapus | perkiraan halaman (gladi): baca · tulis · hapus |', '|---|---:|---:|---:|---:|---:|---:|---|']
            for J in Q['jalur']:
                H = J.get('halaman') or {}
                out.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (J['nama'], rb(J['gladi']['baca']), rb(J['gladi']['tulis']), rb(J['gladi']['hapus']),
                           *['%s (%s%%)' % (rb(J['toko'][k]), ('%.0f' % J['persenToko'][k])) for k in ('baca', 'tulis', 'hapus')],
                           (' · '.join(rb(H.get(k, 0)) for k in ('baca', 'tulis', 'hapus'))) if H else '—'))
            out += [''] + ['- ' + x for x in Q['peringatan']] + ([''] if Q['peringatan'] else [])
            out.append('_Ritual bersih = yang dikerjakan owner tanpa penolakan/pembatalan (percobaan terakhir); penolakan sengaja & pembatalan jalur sendiri. Baca = dokumen yang '
                       'diterima halaman + tulisan halaman sendiri ke koleksi yang didengarnya; get() di aturan TIDAK terukur emulator (perkiraan halaman memasukkannya). '
                       'Skala toko = pengali dokumen arsip — perkiraan, bukan Console._')
        out += ['', 'Cek:']
        for x in S['cek']: out.append('- %s %s%s' % ('✓' if x['ok'] else '✗', x['nama'], '' if x['ok'] else ' — `' + json.dumps(x['ket'], ensure_ascii=False)[:500].replace('`', "'") + '`'))
        if S.get('dicobaUlang'):
            out.append('- ⚠ **DICOBA ULANG** (1×): %s — percobaan pertama berhenti di muat penuh sebelum langkah tutup buku mana pun; angka & cek di atas dari percobaan kedua' % S['dicobaUlang']['sebab'])
        if S.get('antreanPenuhSesudahMuat'):
            out.append('- ℹ antrean WebChannel emulator penuh %s kali SESUDAH muat penuh — sesi kanal yang sudah ditinggal halaman (batas emulator, bukan server sungguhan); '
                       'isi halaman & server dinilai cek di atas' % rb(S['antreanPenuhSesudahMuat']))
        if S.get('galat'): out += ['', '```', S['galat'][:1500], '```']
        if S.get('konsol') and not ok: out += ['', 'Konsol halaman (ekor):', '```', '\n'.join(S['konsol'][-15:])[:3000], '```']
        out.append('')
    out += ['Baca = dokumen yang DITERIMA pendengar halaman dari server (penghitung di salinan SDK uji) + tulisan halaman sendiri ke koleksi yang didengarnya (dari REST; '
            'Firestore menagihnya, SDK tidak memunculkan perubahan baru). get() di aturan tidak termasuk. Tulis/hapus = beda isi emulator sebelum ↔ sesudah langkah (REST).', '',
            'Keterbatasan: jam server emulator = jam runner (Okt 2026), bukan jam halaman — get() kunci periode di aturan dinilai dengan bulan runner. Data contoh tanpa '
            'bulan terkunci (aturanToko/kunciPeriode): tutup buku 2027 dengan bulan terkunci & rules v7 belum digladikan.']
    return '\n'.join(out)


def muat_macet(S):
    """Skenario berhenti DI MUAT PENUH — sebelum langkah tutup buku mana pun (run 7 Okt: 2 dari ±32 skenario, emulator tidak menyerahkan data ke sebagian
    besar pendengar tanpa antrean penuh, tanpa galat izin). Hanya ini yang dicoba ulang sekali; galat di langkah lain tidak pernah dicoba ulang."""
    if not S.get('galat'): return ''
    nama = [x['nama'] for x in S.get('langkah') or []]
    if any(n not in ('masuk', 'muat penuh') for n in nama): return ''
    mp = next((x for x in S['langkah'] if x['nama'] == 'muat penuh'), None)
    if mp and not (mp.get('info') or {}).get('gagalMuat'): return ''
    if not mp and 'semua koleksi termuat' not in S['galat']: return ''
    return 'muat penuh tidak selesai: ' + S['galat'].split('\n')[0][:220]


def jalankan(daftar, sandi, rusak=None, cetak=print):
    lap = {'mulai': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'proyek': PROYEK, 'firebaseTools': os.environ.get('FIREBASE_TOOLS_VERSI', '?'),
           'spark': SPARK, 'data': {}, 'skenario': []}
    data_per = {}
    pasang_aturan(ATURAN_REPO)   # aturan emulator = teks firestore.rules repo, apa pun yang dimuat firebase.json
    for nama in daftar:
        varian = SKENARIO[nama][0]
        if varian not in data_per:
            data_per[varian] = DC.bangun(varian)
            h, cacat = DC.periksa(data_per[varian], varian) if DC.jalan_js('print("{}")')[0] is not None else (None, [])
            lap['data'][varian] = dict(data_per[varian]['gladi'], periksa=(DC.ringkas(h, data_per[varian]) if h and not cacat else ('; '.join(cacat) if cacat else 'tidak dinilai (tanpa jsc/node)')),
                                       nArsip=(h or {}).get('latihan', {}).get('nArsip'))
        data = data_per[varian]
        ulang = None
        for ke in (1, 2):
            # tiap skenario (dan percobaan ulangnya) mulai dari isi yang SAMA (gerbang menulis putusan, ritual memindah arsip): emulator dikosongkan & diisi ulang
            cetak('— data %s: kosongkan emulator, isi %d dokumen, akun owner & karyawan contoh' % (varian, data['gladi']['dokumen']))
            kosongkan(); t0 = time.time(); n = isi_data(data)
            buat_akun(EMAIL_OWNER, sandi); uid_k = buat_akun(EMAIL_KARYAWAN, secrets.token_urlsafe(18))
            tulis_rest([('aksesAkun', uid_k, {'uid': uid_k, 'nama': 'Karyawan Contoh Gladi', 'email': EMAIL_KARYAWAN, 'peran': 'karyawan', 'aktif': True})])
            cetak('  %d dokumen masuk emulator dalam %.1f dtk' % (n, time.time() - t0))
            # pemeriksa SERVER per langkah (dijalankan di dalam langkah itu, halaman menunggu): putusan, lalu tiap titik ritual dibanding isi sebelum ritual
            hari = data['gladi']['hariTanpaTutup']
            kait = {'putusan per tanggal disimpan': (lambda hari=hari: putusan_server(hari, DC.ALASAN_PUTUS))}
            if CEK[nama] is cek_ritual:
                awal = awal_ritual()
                for langkah, jenis in (('6 kunci → kiriman saldo pembuka ditolak server', 'berjalan'), ('BATALKAN sebelum penanda', 'batalSebelum'),
                                       ('6 kunci → saldo pembuka masuk, arsip ditolak server', 'arsipDitolak'), ('LANJUTKAN arsip', 'arsipHabis'),
                                       ('BATALKAN sesudah penanda', 'batalSesudah'), ('7 cadangan sesudah · SELESAI', 'selesai')):
                    kait[langkah] = (lambda jenis=jenis, awal=awal: keadaan_server(jenis, awal))
            cetak('— skenario %s (jam halaman %s)%s' % (nama, SKENARIO[nama][1], ' · percobaan 2' if ke == 2 else ''))
            S = jalankan_skenario(nama, data, sandi, rusak, cetak, kait)
            sebab = muat_macet(S)
            if ke == 2 or not sebab: break
            # SATU percobaan ulang, hanya bila skenario berhenti di muat penuh (belum ada langkah tutup buku) — TERCATAT: baris DICOBA ULANG + peringatan
            # di halaman ringkasan run, dan di laporan/ringkasan gladi. Sering muncul = masalah sungguhan (keputusan owner 26 Sep 2026).
            ulang = {'sebab': sebab, 'percobaan1': {'detik': S.get('detik'), 'galat': (S.get('galat') or '')[:600], 'langkah': S.get('langkah'), 'konsol': (S.get('konsol') or [])[-15:],
                                                     'ekorChrome': (S.get('ekorChrome') or [])[-30:]}}
            for b in (S.get('konsol') or [])[-10:]: cetak('    konsol: ' + b[:300])
            coba_ulang.catat('skenario ' + nama, sebab, 2, 2, log=S.get('ekorChrome') or [])
        if ulang: S['dicobaUlang'] = ulang
        c = []
        CEK[nama](S, data, c)
        S['cek'] = [{'nama': a, 'ok': bool(b), 'ket': k} for a, b, k in c]
        if CEK[nama] is cek_ritual: S['kuota'] = kuota_ritual(S, lap)
        for x in S['cek']: cetak('  %s %s%s' % ('✓' if x['ok'] else '✗', x['nama'], '' if x['ok'] else ' → ' + json.dumps(x['ket'], ensure_ascii=False)[:400]))
        for x in (S.get('kuota') or {}).get('peringatan', []): cetak('  ' + x)
        if S['galat']: cetak('  GALAT: ' + S['galat'][:800])
        if S['konsol'] and any(not x['ok'] for x in S['cek']): cetak('  konsol: ' + ' | '.join(S['konsol'][-8:])[:1500])
        lap['skenario'].append(S)
    # :ruleCoverage emulator (JSON) hanya memuat posisi ekspresi tanpa hitungan (run 7 Okt) — get() di aturan tidak bisa dihitung dari sana, tidak disimpan
    lap['lulus'] = all(x['ok'] for S in lap['skenario'] for x in S['cek'])
    return lap


# KONTROL: SALINAN uji dirusak → CEK SASARAN wajib gagal karena kerusakan itu. BERBUNYI hanya bila (1) cek sasaran gagal dengan ket yang bukan
# "langkah tidak tercapai", (2) skenario jalan sampai akhir tanpa galat, (3) cek lain yang gagal hanya yang memang ikut terkena (boleh), dan (4) BUKTI
# kerusakannya terlihat di langkah yang tepat. Skenario yang jatuh / tidak sampai ke langkahnya = DIAM (bukan lulus kosong).
KONTROL = [
    {'nama': 'LATIHAN yang diam-diam menulis (langkah 4)', 'skenario': 'latihan',
     'rusak': [('js/layar/uang.js', "    bkSaldo: () => { const s = st(); if (!bkUrut(s, 'saldo')) return set({ kabar: 'Kerjakan langkah sebelumnya dulu', kabarAwas: true }); set(",
                "    bkSaldo: () => { const s = st(); if (!bkUrut(s, 'saldo')) return set({ kabar: 'Kerjakan langkah sebelumnya dulu', kabarAwas: true }); tulisDokumen([{ koleksi: 'cadanganCatatan', data: { id: 'gladi-bocor', tanggal: '2026-12-31', jam: '21:50' } }]).catch(() => {}); set(")],
     'sasaran': 'LATIHAN TANPA MENULIS', 'boleh': [],
     'bukti': ('tulisan cadanganCatatan terukur di langkah "4 saldo pembuka"', lambda S: ((L_(S, '4 saldo pembuka') or {}).get('tulisPer') or {}).get('cadanganCatatan', 0) >= 1)},
    {'nama': 'LATIHAN menulis 5,5 dtk SESUDAH langkah terakhir (hanya langkah diam yang melihatnya)', 'skenario': 'latihan',
     'rusak': [('js/layar/uang.js', "    bkSelesaiLatihan: () => { const s = st(); if (!bkUrut(s, 'cadangan2')) return set({ kabar: 'Kerjakan langkah sebelumnya dulu', kabarAwas: true }); set(",
                "    bkSelesaiLatihan: () => { const s = st(); if (!bkUrut(s, 'cadangan2')) return set({ kabar: 'Kerjakan langkah sebelumnya dulu', kabarAwas: true }); setTimeout(() => { tulisDokumen([{ koleksi: 'cadanganCatatan', data: { id: 'gladi-bocor-tertunda', tanggal: '2026-12-31', jam: '21:59' } }]).catch(() => {}); }, 5500); set(")],
     'sasaran': 'LATIHAN TANPA MENULIS', 'boleh': [],
     'bukti': ('tulisan cadanganCatatan BUKAN di langkah "7 selesai latihan", tetapi di langkah diam', lambda S: ((L_(S, '7 selesai latihan') or {}).get('tulisPer') or {}).get('cadanganCatatan', 0) == 0
               and ((L_(S, 'diam: 5 dtk sesudah langkah terakhir') or {}).get('tulisPer') or {}).get('cadanganCatatan', 0) >= 1)},
    {'nama': 'gerbang g1 tidak memblokir', 'skenario': 'gerbang', 'rusak': [('js/layar/tutup-buku-logika.js', "ok: belumPutus.length === 0,", "ok: true,")],
     'sasaran': 'gerbang g1 tampil MEMBLOKIR', 'boleh': ['tombol periksa redup', 'mengetuk periksa DITOLAK'],
     'bukti': ('g1 tampil beres saat SUNGGUHAN dipilih walau 23 hari belum diputus', lambda S: any(g['id'] == 'g1' and g['ok'] for g in (info(L_(S, 'SUNGGUHAN dipilih'), 'gerbang') or [])))},
    # run 7 Okt (#106): koleksi yang DIBUANG dari koleksi.js membuat layar Uang tidak tampil → skenario jatuh, dulu tetap dihitung "berbunyi". Kini koleksinya
    # tetap didengar tetapi hanya 10 dokumen terbaru (pendengar berbatas, seperti jejak). Skenarionya muat saja: dengan pengeluaran yang kurang, kunci
    # LATIHAN menolak "12 baris tidak sama" (run berikutnya) — benar untuk data yang kurang, tetapi bukan yang diuji kontrol ini.
    {'nama': 'salinan memuat satu koleksi tidak lengkap (muat penuh kurang)', 'skenario': 'muatSaja',
     'rusak': [('js/data/koleksi.js', "  { nama: 'pengeluaranHarian',   urut: 'id',    cache: 'harian' },", "  { nama: 'pengeluaranHarian',   urut: 'id',    cache: 'harian', batas: 10 },")],
     'sasaran': 'muat penuh: semua koleksi siap', 'boleh': [],
     'bukti': ('cek muat penuh menyebut pengeluaranHarian hanya 10 dokumen di halaman', lambda S: (((next((x['ket'] for x in S['cek'] if x['nama'].startswith('muat penuh')), None) or {}).get('beda') or {}).get('pengeluaranHarian') or [None])[0] == 10)},
    {'nama': 'pemulihan arsip melewatkan satu dokumen (BATALKAN sesudah penanda)', 'skenario': 'ritualPendek',
     'rusak': [('js/data/firebase.js', "    potong.forEach((x) => { b.set(doc(db, x.koleksi, String(x.idAsli)), x.dok); b.delete(doc(db, KOLEKSI_ARSIP, tahun + '|' + x.koleksi + '|' + x.idAsli)); });",
                "    potong.forEach((x, j) => { if (i + j === 0) return; b.set(doc(db, x.koleksi, String(x.idAsli)), x.dok); b.delete(doc(db, KOLEKSI_ARSIP, tahun + '|' + x.koleksi + '|' + x.idAsli)); });")],
     'sasaran': 'BATALKAN SESUDAH PENANDA di SERVER', 'boleh': [],
     'bukti': ('server: 1 dokumen tertinggal di arsipTahun & kurang 1 di koleksi asal', lambda S: ((L_(S, 'BATALKAN sesudah penanda') or {}).get('kait') or {}).get('arsip') == 1
               and sum((((L_(S, 'BATALKAN sesudah penanda') or {}).get('kait') or {}).get('banding') or {}).get('kurang', {}).values()) == 1)},
]


def nilai_kontrol(k, lap):
    """→ (berbunyi, [alasan DIAM], cek sasaran yang gagal). Lihat aturan di atas KONTROL."""
    S = (lap.get('skenario') or [{}])[0]; cek = S.get('cek') or []; gagal = [x for x in cek if not x['ok']]
    sasaran = [x for x in gagal if x['nama'].startswith(k['sasaran'])]
    lain = [x['nama'] for x in gagal if not any(x['nama'].startswith(b) for b in [k['sasaran']] + k['boleh'])]
    alasan = []
    if not sasaran: alasan.append('cek "%s" tetap lulus' % k['sasaran'])
    elif all(x['ket'] == TAK_TERCAPAI for x in sasaran): alasan.append('cek sasaran gagal hanya karena langkahnya tidak tercapai')
    if not S.get('selesai') or S.get('galat'): alasan.append('skenario tidak jalan sampai akhir: ' + str(S.get('galat') or 'tanpa hasil')[:200])
    if lain: alasan.append('cek lain ikut gagal: ' + ' · '.join(lain)[:300])
    try: bukti = bool(k['bukti'][1](S))
    except Exception as e: bukti = False; alasan.append('bukti tidak terbaca: ' + str(e)[:120])
    if not bukti: alasan.append('bukti tidak terlihat: ' + k['bukti'][0])
    return not alasan, alasan, sasaran


def periksa_salinan():
    """Statis (boleh di Mac): salinan uji disusun lalu diperiksa — tanpa Chrome, tanpa emulator."""
    import uji_csp
    c = []; d = siapkan(DC.JAM_SUNGGUHAN)
    try:
        asli = open(os.path.join(AKAR, 'baru/index.html'), encoding='utf-8').read(); s = open(os.path.join(d, 'baru/index.html'), encoding='utf-8').read()
        A, _ = uji_csp.csp_dari(asli); B, pos = uji_csp.csp_dari(s)
        tambah = [x for x in B.get('connect-src', []) if x not in A.get('connect-src', [])]; buang = [x for x in A.get('connect-src', []) if x not in B.get('connect-src', [])]
        c.append(('CSP salinan: connect-src = connect-src situs − host Firebase sungguhan (*.googleapis.com) + http://<emulator Firestore> & http://<emulator Auth>; direktif lain sama',
                  {k: v for k, v in A.items() if k != 'connect-src'} == {k: v for k, v in B.items() if k != 'connect-src'} and sorted(tambah) == sorted(['http://' + FS_HOST, 'http://' + AUTH_HOST])
                  and buang and all(FIREBASE_SUNGGUHAN.match(x) for x in buang) and not any(FIREBASE_SUNGGUHAN.match(x) for x in B.get('connect-src', [])), {'tambah': tambah, 'buang': buang}))
        c.append(('hash script sebaris situs tetap berlaku di salinan (script sebarisnya tidak diubah)', uji_csp.hash_sebaris(asli) == [h for h in uji_csp.hash_sebaris(s) if h in uji_csp.hash_sebaris(asli)]
                  and all(h in B.get('script-src', []) for h in uji_csp.hash_sebaris(asli)), ''))
        i_jam = s.find('window.__jamGladi'); c.append(('jam palsu disisip SEBELUM meta CSP (tidak terkena CSP salinan)', 0 <= i_jam < pos, (i_jam, pos)))
        i_csp = s.find("addEventListener('securitypolicyviolation'"); i_app = s.find('<script type="module" src="js/app.js">')
        c.append(('pencatat pelanggaran CSP salinan terpasang sebelum meta CSP & sebelum app.js (sambungan ke server lain tercatat sejak awal)', 0 <= i_csp < pos and i_csp < i_app, (i_csp, pos, i_app)))
        c.append(('skenario dimuat dari situs sendiri (script-src \'self\'), sesudah app.js', s.find('<script type="module" src="js/app.js">') < s.find('<script type="module" src="/_gladi/skenario.js">'), ''))
        fbs = open(os.path.join(d, 'baru/js/data/firebase.js'), encoding='utf-8').read()
        c.append(('firebase.js salinan: Firestore lewat SDK penghitung (/_gladi/), app & auth tetap dari gstatic', "from '/_gladi/firebase-firestore.js'" in fbs and SDK + 'firebase-auth.js' in fbs and SDK + 'firebase-app.js' in fbs, ''))
        c.append(('SDK penghitung meneruskan SEMUA ekspor SDK asli (export *) dan hanya membungkus onSnapshot & getDocs', SDK_PENGHITUNG.count("export * from '" + SDK + "firebase-firestore.js'") == 1
                  and sorted(re.findall(r'export (?:async )?function (\w+)', SDK_PENGHITUNG)) == ['getDocs', 'onSnapshot'], ''))
        c.append(('berkas terbit TIDAK disentuh (salinan di folder sementara)', open(os.path.join(AKAR, 'baru/index.html'), encoding='utf-8').read() == asli, ''))
        ada = set(re.findall(r'^  async (\w+)\(\)', SKENARIO_JS, re.M))
        for nama, (_, _, langkah) in SKENARIO.items():
            c.append(('skenario %s: semua langkahnya ada di SKENARIO_JS, ceknya ada di CEK' % nama, all(x in ada for x in langkah) and nama in CEK, [x for x in langkah if x not in ada]))
        # langkah yang dicek / diperiksa di server harus benar-benar dilaporkan dengan nama itu oleh SKENARIO_JS (nama basi = cek "langkah tidak tercapai")
        dilapor = set(re.findall(r"(?:ketukLapor|lapor)\('([^']+)'", SKENARIO_JS))
        nama_kait = ['putusan per tanggal disimpan', '6 kunci → kiriman saldo pembuka ditolak server', 'BATALKAN sebelum penanda', '6 kunci → saldo pembuka masuk, arsip ditolak server',
                     'LANJUTKAN arsip', 'BATALKAN sesudah penanda', '7 cadangan sesudah · SELESAI', 'diam: 5 dtk sesudah langkah terakhir', '1 periksa (semua beres)', 'SUNGGUHAN dipilih']
        c.append(('nama langkah yang dicek & diperiksa di server dilaporkan SKENARIO_JS persis', all(x in dilapor for x in nama_kait), [x for x in nama_kait if x not in dilapor]))
        # percobaan ulang: HANYA skenario yang berhenti di muat penuh (sebelum langkah tutup buku), dan selalu lewat coba_ulang.catat (DICOBA ULANG + peringatan)
        L0 = lambda n, info=None: {'nama': n, 'info': info or {}}
        kasus = [('muat gagal melapor', {'galat': 'Error: tidak tercapai dalam 300 dtk: semua koleksi termuat — koleksi siap 22 dari 56', 'langkah': [L0('masuk'), L0('muat penuh', {'gagalMuat': 'x'})]}, True),
                 ('muat tanpa laporan (galat menyebut koleksi)', {'galat': 'Error: tidak tercapai dalam 600 dtk: semua koleksi termuat', 'langkah': [L0('masuk')]}, True),
                 ('galat di langkah tutup buku', {'galat': 'Error: tidak tercapai: 6a kunci', 'langkah': [L0('masuk'), L0('muat penuh'), L0('buka Uang › Tutup buku')]}, False),
                 ('muat selesai, galat sesudahnya', {'galat': 'Error: x', 'langkah': [L0('masuk'), L0('muat penuh')]}, False),
                 ('masuk gagal', {'galat': 'Error: tidak tercapai dalam 90 dtk: masuk sebagai owner contoh', 'langkah': []}, False),
                 ('tanpa galat', {'galat': '', 'langkah': [L0('masuk'), L0('muat penuh', {'gagalMuat': 'x'})]}, False)]
        salah = [n for n, S0, harap in kasus if bool(muat_macet(S0)) != harap]
        c.append(('percobaan ulang hanya untuk muat penuh yang macet (%d kasus) dan selalu tercatat lewat coba_ulang.catat' % len(kasus), not salah
                  and "coba_ulang.catat('skenario ' + nama, sebab, 2, 2" in open(os.path.abspath(__file__), encoding='utf-8').read(), salah))
        for k in KONTROL:   # jangkar kerusakan kontrol masih ada tepat satu kali di berkas sumbernya (kontrol basi = DIAM di runner, ketahuan di sini dulu)
            for rel, lama, _ in k['rusak']:
                n = open(os.path.join(AKAR, 'baru', rel), encoding='utf-8').read().count(lama)
                c.append(('jangkar kontrol "%s" ada tepat 1× di baru/%s' % (k['nama'], rel), n == 1, n))
            c.append(('kontrol "%s": skenario & cek sasaran ada' % k['nama'], k['skenario'] in SKENARIO and k['skenario'] in CEK, k['skenario']))
        for k in ('arsipTahun', 'utangPemasokMutasi'):
            A_ = aturan_tolak(k); blok = blok_aturan(A_, k).group(1)
            luar = A_.replace(blok, ''); luar0 = ATURAN_REPO.replace(blok_aturan(ATURAN_REPO, k).group(1), '')
            c.append(('aturan penolak gladi (%s): create/update/write DICABUT dari blok itu (izin rules = ATAU), baca & hapus tetap, blok lain sama persis' % k,
                      not re.search(r'allow [^:]*\b(create|update|write)\b', blok) and 'allow read' in blok and 'delete' in blok and luar == luar0, blok))
    finally: shutil.rmtree(d, ignore_errors=True)
    return c


if __name__ == '__main__':
    arg = sys.argv[1:]
    def opsi(n, b):
        return arg[arg.index(n) + 1] if n in arg and arg.index(n) + 1 < len(arg) else b
    if '--jumlah-kontrol' in arg: print(len(KONTROL)); sys.exit(0)
    if '--periksa-salinan' in arg:
        c = periksa_salinan(); g = [x for x in c if not x[1]]
        for n, ok, k in c: print(('✓ ' if ok else '✗ ') + n + ('' if ok else ' → ' + str(k)[:300]))
        print('SALINAN UJI GLADI: %d lulus · %d gagal' % (len(c) - len(g), len(g))); sys.exit(2 if g else 0)
    if '--gabung' in arg:
        # workflow: tiap skenario di emulator SENDIRI (sesi WebChannel halaman yang sudah mati tetap dikirimi pesan oleh emulator sampai kanalnya
        # kedaluwarsa — run 7 Okt: 2,2 juta baris "antrean penuh" saat ritual berjalan sesudah dua skenario lain). Laporan per skenario digabung di sini.
        berkas = []
        for x in arg[arg.index('--gabung') + 1:]:
            if x.startswith('--'): break
            berkas.append(x)
        lap = None
        for b in berkas:
            x = json.load(open(b, encoding='utf-8'))
            if lap is None: lap = x; continue
            lap['data'].update(x.get('data') or {}); lap['skenario'] += x.get('skenario') or []
            lap['lulus'] = lap['lulus'] and x.get('lulus', False)
        if lap is None: print('tidak ada laporan skenario untuk digabung'); sys.exit(2)
        harap = [x.strip() for x in (os.environ.get('GLADI_SKENARIO') or ','.join(SKENARIO_BAWAAN)).split(',') if x.strip()]
        ada = [S['nama'] for S in lap['skenario']]; hilang = [x for x in harap if x not in ada]
        if hilang:
            lap['lulus'] = False
            lap['skenario'] += [{'nama': x, 'varian': SKENARIO.get(x, ('?',))[0], 'jamHalaman': SKENARIO.get(x, ('', '?'))[1], 'detik': 0, 'langkah': [], 'galat': 'skenario tidak menghasilkan laporan (lihat log langkah GLADI)',
                                  'konsol': [], 'cek': [{'nama': 'skenario menghasilkan laporan', 'ok': False, 'ket': 'tidak ada berkas laporan'}]} for x in hilang]
        keluar = opsi('--keluar', ''); ring = opsi('--ringkasan', '')
        if keluar: json.dump(lap, open(keluar, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        md = ringkas_md(lap)
        if ring: open(ring, 'w', encoding='utf-8').write(md)
        print(md); sys.exit(0 if lap['lulus'] else 2)
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        print('DITOLAK: gladi tutup buku menyalakan Chrome & emulator — HANYA di runner GitHub Actions (CLAUDE.md, keputusan owner 27 Sep 2026).\n'
              'Jalankan workflow "Gladi tutup buku" (Actions › Gladi tutup buku › Run workflow). Di Mac boleh: --periksa-salinan.')
        sys.exit(2)
    if not CHROME: print('Chrome tidak ditemukan di runner — GAGAL'); sys.exit(2)
    tunggu_emulator()
    sandi = secrets.token_urlsafe(24)   # sandi akun owner contoh: dibuat tiap run, hanya di emulator, tidak dicetak
    if '--kontrol' in arg:
        pilih = opsi('--kontrol', '')
        if pilih and not pilih.startswith('--'):
            if not pilih.isdigit() or not 1 <= int(pilih) <= len(KONTROL): print('kontrol %s tidak ada (1–%d)' % (pilih, len(KONTROL))); sys.exit(2)
            daftar_k = [KONTROL[int(pilih) - 1]]
        else: daftar_k = KONTROL
        kode = 0
        for k in daftar_k:
            print('KONTROL · ' + k['nama'] + ' (skenario ' + k['skenario'] + ')', flush=True)
            lap = jalankan([k['skenario']], sandi, k['rusak'], cetak=lambda *a: print('   ', *a, flush=True))
            b, alasan, sasaran = nilai_kontrol(k, lap)
            if b: print('BERBUNYI ' + k['nama'] + ' → ' + sasaran[0]['nama'] + ' · ' + json.dumps(sasaran[0]['ket'], ensure_ascii=False)[:240] + ' · bukti: ' + k['bukti'][0], flush=True)
            else:
                print('DIAM!!   ' + k['nama'] + ' → ' + ' · '.join(alasan), flush=True)
                for S in lap['skenario']:
                    for x in S['cek']: print('    %s %s%s' % ('✓' if x['ok'] else '✗', x['nama'], '' if x['ok'] else ' → ' + json.dumps(x['ket'], ensure_ascii=False)[:300]))
                    for b in (S.get('konsol') or [])[-8:]: print('    konsol: ' + b[:300])
                    for b in (S.get('ekorChrome') or [])[-12:]: print('    chrome: ' + b[:300].replace('::', ': :'))
                kode = 3
        sys.exit(kode)
    daftar = [x.strip() for x in opsi('--skenario', os.environ.get('GLADI_SKENARIO') or ','.join(SKENARIO_BAWAAN)).split(',') if x.strip()]
    salah = [x for x in daftar if x not in SKENARIO]
    if salah: print('skenario tidak dikenal: %s (ada: %s)' % (', '.join(salah), ', '.join(SKENARIO))); sys.exit(2)
    lap = jalankan(daftar, sandi)
    keluar = opsi('--keluar', ''); ring = opsi('--ringkasan', '')
    if keluar:
        os.makedirs(os.path.dirname(os.path.abspath(keluar)), exist_ok=True); json.dump(lap, open(keluar, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ringkas_md(lap)
    if ring: open(ring, 'w', encoding='utf-8').write(md)
    print('\n' + md)
    sys.exit(0 if lap['lulus'] else 2)
