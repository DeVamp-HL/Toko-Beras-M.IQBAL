#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_coba_ulang.py — percobaan ulang halaman di uji peramban WAJIB tercatat (keputusan owner 26 Sep 2026).

Syarat owner: setiap kali halaman dicoba ulang, log CI memuat baris "DICOBA ULANG: <nama uji>" yang jelas terlihat — kalau mulai sering
muncul, itu tanda masalah sungguhan, bukan sekadar Chrome yang lambat. Uji ini memakai CHROME PALSU (skrip kecil, tanpa Chrome sungguhan)
yang meniru tiga keadaan: halaman tidak pernah jalan, halaman selesai tapi DOM tidak keluar (kejadian CI main 8dcaae2), dan halaman sehat.
Semua dijalankan di proses anak dan keluarannya DITANGKAP, jadi peringatan uji ini tidak ikut mengotori halaman ringkasan run sungguhan.

  · uji_antrean_kasir (juga dipakai uji_sistem_lama_bacasaja): halaman tidak jalan → tepat SATU baris DICOBA ULANG dengan nama uji, halaman,
    sebab, "percobaan 2 dari 2"; selesai-tanpa-DOM → ikut dicoba ulang dan tercatat; mode --kontrol ikut tertulis di nama uji
  · percobaan ulang mulai dari penyimpanan halaman SEBELUM percobaan pertama: percobaan yang macet sesudah selesai sudah menjalankan
    skenarionya (PR #42: skenario muat ulang sudah mengarsipkan karcis → percobaan ulang gagal palsu)
  · uji_layar_kunci: pengulangan yang dulu DIAM sekarang tercatat — dua baris untuk tiga percobaan
  · di GitHub Actions tiap baris juga jadi peringatan "DICOBA ULANG" di halaman ringkasan run; yang DISENGAJA kontrol (kontrol 9) tetap
    ditulis barisnya tapi tanpa peringatan
  · halaman sehat → NOL baris (tidak ada tanda palsu)

    python3 alat-uji/uji_coba_ulang.py            → N lulus · 0 gagal (keluar 1 bila ada yang gagal)
    python3 alat-uji/uji_coba_ulang.py --kontrol  → tiap kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
Tanpa jaringan luar, tanpa Chrome, tanpa Node.
"""
import os, sys, json, time, atexit, shutil, tempfile, subprocess

SINI = os.path.dirname(os.path.abspath(__file__))
BARIS = 'DICOBA ULANG: '
PERINGATAN = '::warning title=DICOBA ULANG::'

# ---------- Chrome palsu: argumen terakhir = alamat halaman. http.client, bukan urllib: urllib di macOS menanyakan setelan proxy sistem dulu ----------
SIAP = "c = http.client.HTTPConnection(u.hostname, u.port, timeout=10); c.request('GET', '/_siap'); c.getresponse().read()\n"
CHROME_PALSU = {
    'diam': "sys.stderr.write('[palsu] renderer macet\\n')\n",   # tidak pernah memanggil /_siap, DOM kosong → "tidak mengabarkan selesai"; satu baris catatan Chrome
    'tanpa-dom': SIAP,   # skenario selesai, DOM tidak pernah keluar (kejadian CI 8dcaae2)
    'sehat': SIAP + "sys.stdout.write('<html><head></head><body>ok</body></html>\\n'); sys.stdout.flush()\n",
    # skenario MENGUBAH penyimpanan halaman (efek.txt di Local Storage profil) lalu mengabarkan selesai; percobaan ganjil macet tanpa DOM,
    # percobaan genap menyerahkan DOM yang menyebut isi penyimpanan yang DILIHATNYA saat mulai (kejadian PR #42: skenario muat ulang)
    'efek': ("import os\nprof = next(a.split('=', 1)[1] for a in sys.argv if a.startswith('--user-data-dir='))\n"
             "ls = os.path.join(prof, 'Default', 'Local Storage'); os.makedirs(ls, exist_ok=True); pe = os.path.join(ls, 'efek.txt')\n"
             "n = int(open(pe).read()) if os.path.exists(pe) else 0\nopen(pe, 'w').write(str(n + 1))\n"
             "pk = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'efek-ke.txt')\n"
             "k = int(open(pk).read()) if os.path.exists(pk) else 0\nopen(pk, 'w').write(str(k + 1))\n" + SIAP +
             "if k % 2 == 1: sys.stdout.write('<html><body>efek=%d</body></html>\\n' % n); sys.stdout.flush()\n"),
}

# ---------- satu kasus = satu proses anak dari SALINAN alat-uji (kontrol mengganti teks di salinan itu) ----------
PELARI = r'''
import os, sys, json, tempfile
sys.path.insert(0, os.environ['UJI_DIR'])
sys.argv = json.loads(os.environ['UJI_ARGV'])
alat, chrome, disengaja = os.environ['UJI_ALAT'], os.environ['UJI_CHROME'], os.environ.get('UJI_DISENGAJA') or None
d = tempfile.mkdtemp()
if alat == 'antrean':
    import uji_antrean_kasir as U
    U.CHROME = chrome
    srv, port, keadaan = U.layani(d)
    profil = tempfile.mkdtemp()
    try:
        h = U.buka(port, keadaan, profil, '/x.html', tunggu=15)
        m = __import__('re').search(r'efek=\d+', h or '')
        if m: print('DOM:' + m.group(0))
        pe = os.path.join(profil, 'Default', 'Local Storage', 'efek.txt')
        if os.path.exists(pe): print('PROFIL:efek=' + open(pe).read())
    finally: srv.shutdown()
else:
    import uji_layar_kunci as K
    K.CHROME = chrome; K.DISENGAJA = disengaja
    K.dom(d, '/baru/index.html', coba=3, butuh_cdn=False)
'''


_CHROMES = {}


def chromes():
    """Chrome palsu dibuat SEKALI per proses (bukan per kontrol) — berkas baru yang dijalankan pertama kali di runner macOS itu mahal."""
    if not _CHROMES:
        folder = tempfile.mkdtemp(prefix='chrome-palsu-'); atexit.register(shutil.rmtree, folder, True)
        for jenis, isi in CHROME_PALSU.items():
            p = os.path.join(folder, 'chrome-' + jenis)
            open(p, 'w').write('#!' + sys.executable + '\nimport sys, http.client, urllib.parse\nu = urllib.parse.urlsplit(sys.argv[-1])\n' + isi)
            os.chmod(p, 0o755); _CHROMES[jenis] = p
    return _CHROMES


def jalankan(salinan, alat, jenis, argv, gha=False, disengaja=None):
    """→ baris keluaran (stdout) proses anak. Proses anak yang melewati 60 dtk = gagal (dicatat), bukan membuat seluruh pekerjaan CI menggantung."""
    env = {k: v for k, v in os.environ.items() if k not in ('GITHUB_ACTIONS', 'CI')}
    env.update(UJI_DIR=salinan, UJI_ALAT=alat, UJI_CHROME=chromes()[jenis], UJI_ARGV=json.dumps(argv), UJI_DISENGAJA=disengaja or '')
    if gha: env['GITHUB_ACTIONS'] = 'true'
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, '-c', PELARI], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    except subprocess.TimeoutExpired:
        return ['(proses anak melewati 60 dtk: %s · %s)' % (alat, jenis)]
    finally:
        if os.environ.get('CI'): print('  [coba-ulang] %s · %s · %s %.1f dtk' % (alat, jenis, ' '.join(argv[1:]) or '-', time.time() - t0), file=sys.stderr, flush=True)
    if r.returncode != 0: return ['(proses anak gagal) ' + r.stderr.decode('utf-8', 'replace')[-300:]]
    return r.stdout.decode('utf-8', 'replace').splitlines()


class Cukup(Exception):
    """Kontrol sudah berbunyi — sisa kasus tidak perlu dijalankan."""


def semua(ganti=None, cepat=False):
    """→ [(nama, lulus, keterangan)]. ganti = [(berkas, lama, baru)] untuk kontrol; 'lama' wajib ada (kontrol basi = gagal keras).
    cepat = berhenti di pemeriksaan gagal PERTAMA (kontrol cukup membuktikan satu pemeriksaan berbunyi)."""
    kerja = tempfile.mkdtemp(prefix='coba-ulang-'); salinan = os.path.join(kerja, 'alat-uji')
    shutil.copytree(SINI, salinan, ignore=shutil.ignore_patterns('__pycache__'))
    for berkas, lama, baru in (ganti or []):
        p = os.path.join(salinan, berkas); t = open(p, encoding='utf-8').read()
        assert lama in t, 'kontrol basi: ' + berkas + ' · ' + lama[:70]; open(p, 'w', encoding='utf-8').write(t.replace(lama, baru))
    out = []
    def ok(nama, syarat, ket=''):
        out.append((nama, bool(syarat), ket))
        if cepat and not syarat: raise Cukup()
    def jalankan_(alat, jenis, argv, **kw): return jalankan(salinan, alat, jenis, argv, **kw)
    def baris(k): return [b for b in k if b.startswith(BARIS)]
    def peringatan(k): return [b for b in k if b.startswith(PERINGATAN)]
    try:
        k = jalankan_('antrean', 'diam', ['alat-uji/uji_antrean_kasir.py'])
        ok('antrean kasir · halaman tidak jalan → tepat satu baris DICOBA ULANG (nama uji, halaman, sebab, percobaan 2 dari 2)',
           baris(k) == [BARIS + 'uji_antrean_kasir · /x.html — tidak mengabarkan selesai (percobaan 2 dari 2)'], k)
        ok('antrean kasir · di luar GitHub Actions tidak ada baris peringatan', not peringatan(k), k)
        ok('catatan Chrome dari percobaan yang macet ikut dicetak di bawah baris DICOBA ULANG (bukti untuk menyelidiki)',
           '    [palsu] renderer macet' in k and k.index('    [palsu] renderer macet') > k.index(baris(k)[0]) if baris(k) else False, k)
        k = jalankan_('antrean', 'tanpa-dom', ['alat-uji/uji_antrean_kasir.py', '--kontrol'])
        ok('antrean kasir · selesai tapi DOM tidak keluar (kejadian CI 8dcaae2) → ikut dicoba ulang & tercatat, mode --kontrol ikut tertulis',
           baris(k) == [BARIS + 'uji_antrean_kasir --kontrol · /x.html — selesai tapi DOM tidak keluar (percobaan 2 dari 2)'], k)
        k = jalankan_('antrean', 'diam', ['alat-uji/uji_sistem_lama_bacasaja.py'])
        ok('sistem lama hanya-baca (memakai buka() yang sama) → barisnya menyebut uji_sistem_lama_bacasaja', len(baris(k)) == 1 and baris(k)[0].startswith(BARIS + 'uji_sistem_lama_bacasaja · '), k)
        k = jalankan_('antrean', 'diam', ['alat-uji/uji_antrean_kasir.py'], gha=True)
        ok('GitHub Actions · tiap percobaan ulang juga jadi peringatan "DICOBA ULANG" di halaman ringkasan run',
           len(baris(k)) == 1 and peringatan(k) == [PERINGATAN + 'uji_antrean_kasir · /x.html — tidak mengabarkan selesai (percobaan 2 dari 2)'], k)
        ok('GitHub Actions · catatan Chrome dalam kelompok yang bisa dibuka (::group:: … ::endgroup::), tidak memenuhi log',
           any(b.startswith('::group::catatan Chrome dari percobaan 1') for b in k) and '::endgroup::' in k and '    [palsu] renderer macet' in k, k)
        try: os.unlink(os.path.join(os.path.dirname(chromes()['efek']), 'efek-ke.txt'))
        except OSError: pass
        k = jalankan_('antrean', 'efek', ['alat-uji/uji_antrean_kasir.py'])
        ok('antrean kasir · percobaan ulang mulai dari penyimpanan SEBELUM percobaan pertama (skenario yang sudah jalan tidak meninggalkan jejak)',
           len(baris(k)) == 1 and 'DOM:efek=0' in k, k)
        ok('antrean kasir · sesudah lulus, penyimpanan = hasil percobaan yang lulus (pemuatan berikutnya melihat keadaan yang benar)', 'PROFIL:efek=1' in k, k)
        k = jalankan_('antrean', 'sehat', ['alat-uji/uji_antrean_kasir.py'], gha=True)
        ok('halaman sehat → nol baris DICOBA ULANG, nol peringatan (tidak ada tanda palsu)', not baris(k) and not peringatan(k), k)
        k = jalankan_('kunci', 'diam', ['alat-uji/uji_layar_kunci.py'])
        ok('layar kunci · pengulangan yang dulu diam sekarang tercatat: dua baris untuk tiga percobaan',
           baris(k) == [BARIS + 'uji_layar_kunci · /baru/index.html — tidak mengabarkan selesai (percobaan %d dari 3)' % n for n in (2, 3)], k)
        ok('layar kunci · catatan Chrome ikut dicetak', k.count('    [palsu] renderer macet') == 2, k)
        k = jalankan_('kunci', 'diam', ['alat-uji/uji_layar_kunci.py', '--kontrol'], gha=True, disengaja='kontrol 9 memutus Firebase')
        ok('yang DISENGAJA kontrol tetap ditulis barisnya (ditandai DISENGAJA) tapi tanpa peringatan di ringkasan',
           len(baris(k)) == 2 and all(b.endswith(' · DISENGAJA: kontrol 9 memutus Firebase') for b in baris(k)) and not peringatan(k), k)
    except Cukup:
        pass
    finally:
        shutil.rmtree(kerja, ignore_errors=True)
    return out


KONTROL = [
    ('pencatat tidak mencetak apa pun', [('coba_ulang.py', "    print('DICOBA ULANG: ' + teks, flush=True)\n", "    pass\n")]),
    ('buka() kembali ke cacat 8dcaae2 (selesai tanpa DOM tidak diulang)',
     [('uji_antrean_kasir.py', "if gambar or (keadaan['siap'].is_set() and '</html>' in h): return h", "if gambar or keadaan['siap'].is_set(): return h")]),
    ('buka() mengulang tanpa mencatat', [('uji_antrean_kasir.py', "            coba_ulang.catat(jalur, sebab, coba, BATAS, log=coba_ulang.ekor_berkas(keadaan.get('log_chrome', '')))\n", "")]),
    ('percobaan ulang TIDAK memulihkan penyimpanan (cacat PR #42)', [('uji_antrean_kasir.py', "            _salin_penyimpanan(foto, profil)   # mulai lagi", "            pass   # mulai lagi")]),
    ('foto penyimpanan diambil SESUDAH percobaan pertama, bukan sebelum', [('uji_antrean_kasir.py',
        "    foto = tempfile.mkdtemp(prefix='antre-foto-'); _salin_penyimpanan(profil, foto)\n", "    foto = tempfile.mkdtemp(prefix='antre-foto-')\n"),
        ('uji_antrean_kasir.py', "        h = _buka_sekali(port, keadaan, profil, jalur, gambar, tunggu)\n", "        h = _buka_sekali(port, keadaan, profil, jalur, gambar, tunggu)\n        if coba == 1: _salin_penyimpanan(profil, foto)\n")]),
    ('uji_layar_kunci mengulang diam-diam lagi', [('uji_layar_kunci.py', "        if ke > 1: coba_ulang.catat(jalur, sebab, ke, coba, disengaja=DISENGAJA, log=log)\n", "")]),
    ('peringatan GitHub Actions hilang', [('coba_ulang.py', "print('::warning title=DICOBA ULANG::'", "print('(peringatan) DICOBA ULANG::'")]),
    ('yang disengaja ikut jadi peringatan', [('coba_ulang.py', "if os.environ.get('GITHUB_ACTIONS') and not disengaja:", "if os.environ.get('GITHUB_ACTIONS'):")]),
    ('catatan Chrome tidak ikut dicetak (uji antrean kasir)', [('uji_antrean_kasir.py', "BATAS, log=coba_ulang.ekor_berkas(keadaan.get('log_chrome', '')))", "BATAS)")]),
    ('catatan Chrome tidak ikut dicetak (uji layar kunci)', [('uji_layar_kunci.py', "disengaja=DISENGAJA, log=log)", "disengaja=DISENGAJA)")]),
    ('nama uji tidak disebut', [('coba_ulang.py', "    teks = '%s · %s — %s (percobaan %d dari %d)' % (nama_uji(), halaman, sebab, ke, dari)",
                                 "    teks = '%s — %s (percobaan %d dari %d)' % (halaman, sebab, ke, dari)")]),
]


if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti in KONTROL:
            try:
                g = [x for x in semua(ganti, cepat=True) if not x[1]]
            except AssertionError as e:
                print('KONTROL BASI  ' + nama + ' · ' + str(e)); kode = 3; continue
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:110] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h = semua(); gagal = 0
    for nama, lulus, ket in h:
        print(('✓ ' if lulus else '✗ ') + nama + ('' if lulus else ' → ' + json.dumps(ket, ensure_ascii=False)[:400]))
        gagal += 0 if lulus else 1
    print('PERCOBAAN ULANG TERCATAT: %d lulus · %d gagal' % (len(h) - gagal, gagal))
    sys.exit(1 if gagal else 0)
