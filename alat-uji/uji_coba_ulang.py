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
  · uji_layar_kunci: pengulangan yang dulu DIAM sekarang tercatat — dua baris untuk tiga percobaan
  · di GitHub Actions tiap baris juga jadi peringatan "DICOBA ULANG" di halaman ringkasan run; yang DISENGAJA kontrol (kontrol 9) tetap
    ditulis barisnya tapi tanpa peringatan
  · halaman sehat → NOL baris (tidak ada tanda palsu)

    python3 alat-uji/uji_coba_ulang.py            → N lulus · 0 gagal (keluar 1 bila ada yang gagal)
    python3 alat-uji/uji_coba_ulang.py --kontrol  → tiap kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
Tanpa jaringan luar, tanpa Chrome, tanpa Node.
"""
import os, sys, json, shutil, tempfile, subprocess

SINI = os.path.dirname(os.path.abspath(__file__))
BARIS = 'DICOBA ULANG: '
PERINGATAN = '::warning title=DICOBA ULANG::'

# ---------- Chrome palsu: argumen terakhir = alamat halaman ----------
CHROME_PALSU = {
    'diam': '',   # tidak pernah memanggil /_siap, tidak mencetak apa pun → "tidak mengabarkan selesai"
    'tanpa-dom': "urllib.request.urlopen(asal + '/_siap', timeout=10).read()\n",   # skenario selesai, DOM tidak pernah keluar
    'sehat': "urllib.request.urlopen(asal + '/_siap', timeout=10).read()\nsys.stdout.write('<html><head></head><body>ok</body></html>\\n'); sys.stdout.flush()\n",
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
    try: U.buka(port, keadaan, tempfile.mkdtemp(), '/x.html', tunggu=15)
    finally: srv.shutdown()
else:
    import uji_layar_kunci as K
    K.CHROME = chrome; K.DISENGAJA = disengaja
    K.dom(d, '/baru/index.html', coba=3, butuh_cdn=False)
'''


def buat_chrome(folder, jenis):
    p = os.path.join(folder, 'chrome-' + jenis)
    open(p, 'w').write('#!' + sys.executable + '\nimport sys, urllib.request, urllib.parse\nu = urllib.parse.urlsplit(sys.argv[-1]); asal = u.scheme + "://" + u.netloc\n'
                       + CHROME_PALSU[jenis])
    os.chmod(p, 0o755); return p


def jalankan(salinan, chromes, alat, jenis, argv, gha=False, disengaja=None):
    """→ baris keluaran (stdout) proses anak."""
    env = {k: v for k, v in os.environ.items() if k not in ('GITHUB_ACTIONS', 'CI')}
    env.update(UJI_DIR=salinan, UJI_ALAT=alat, UJI_CHROME=chromes[jenis], UJI_ARGV=json.dumps(argv), UJI_DISENGAJA=disengaja or '')
    if gha: env['GITHUB_ACTIONS'] = 'true'
    r = subprocess.run([sys.executable, '-c', PELARI], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    if r.returncode != 0: return ['(proses anak gagal) ' + r.stderr.decode('utf-8', 'replace')[-300:]]
    return r.stdout.decode('utf-8', 'replace').splitlines()


def semua(ganti=None):
    """→ [(nama, lulus, keterangan)]. ganti = [(berkas, lama, baru)] untuk kontrol; 'lama' wajib ada (kontrol basi = gagal keras)."""
    kerja = tempfile.mkdtemp(prefix='coba-ulang-'); salinan = os.path.join(kerja, 'alat-uji')
    shutil.copytree(SINI, salinan, ignore=shutil.ignore_patterns('__pycache__'))
    for berkas, lama, baru in (ganti or []):
        p = os.path.join(salinan, berkas); t = open(p, encoding='utf-8').read()
        assert lama in t, 'kontrol basi: ' + berkas + ' · ' + lama[:70]; open(p, 'w', encoding='utf-8').write(t.replace(lama, baru))
    chromes = {j: buat_chrome(kerja, j) for j in CHROME_PALSU}
    out = []
    def ok(nama, syarat, ket=''): out.append((nama, bool(syarat), ket))
    def baris(k): return [b for b in k if b.startswith(BARIS)]
    def peringatan(k): return [b for b in k if b.startswith(PERINGATAN)]
    try:
        k = jalankan(salinan, chromes, 'antrean', 'diam', ['alat-uji/uji_antrean_kasir.py'])
        ok('antrean kasir · halaman tidak jalan → tepat satu baris DICOBA ULANG (nama uji, halaman, sebab, percobaan 2 dari 2)',
           baris(k) == [BARIS + 'uji_antrean_kasir · /x.html — tidak mengabarkan selesai (percobaan 2 dari 2)'], k)
        ok('antrean kasir · di luar GitHub Actions tidak ada baris peringatan', not peringatan(k), k)
        k = jalankan(salinan, chromes, 'antrean', 'tanpa-dom', ['alat-uji/uji_antrean_kasir.py', '--kontrol'])
        ok('antrean kasir · selesai tapi DOM tidak keluar (kejadian CI 8dcaae2) → ikut dicoba ulang & tercatat, mode --kontrol ikut tertulis',
           baris(k) == [BARIS + 'uji_antrean_kasir --kontrol · /x.html — selesai tapi DOM tidak keluar (percobaan 2 dari 2)'], k)
        k = jalankan(salinan, chromes, 'antrean', 'diam', ['alat-uji/uji_sistem_lama_bacasaja.py'])
        ok('sistem lama hanya-baca (memakai buka() yang sama) → barisnya menyebut uji_sistem_lama_bacasaja', len(baris(k)) == 1 and baris(k)[0].startswith(BARIS + 'uji_sistem_lama_bacasaja · '), k)
        k = jalankan(salinan, chromes, 'antrean', 'diam', ['alat-uji/uji_antrean_kasir.py'], gha=True)
        ok('GitHub Actions · tiap percobaan ulang juga jadi peringatan "DICOBA ULANG" di halaman ringkasan run',
           len(baris(k)) == 1 and peringatan(k) == [PERINGATAN + 'uji_antrean_kasir · /x.html — tidak mengabarkan selesai (percobaan 2 dari 2)'], k)
        k = jalankan(salinan, chromes, 'antrean', 'sehat', ['alat-uji/uji_antrean_kasir.py'], gha=True)
        ok('halaman sehat → nol baris DICOBA ULANG, nol peringatan (tidak ada tanda palsu)', not baris(k) and not peringatan(k), k)
        k = jalankan(salinan, chromes, 'kunci', 'diam', ['alat-uji/uji_layar_kunci.py'])
        ok('layar kunci · pengulangan yang dulu diam sekarang tercatat: dua baris untuk tiga percobaan',
           baris(k) == [BARIS + 'uji_layar_kunci · /baru/index.html — tidak mengabarkan selesai (percobaan %d dari 3)' % n for n in (2, 3)], k)
        k = jalankan(salinan, chromes, 'kunci', 'diam', ['alat-uji/uji_layar_kunci.py', '--kontrol'], gha=True, disengaja='kontrol 9 memutus Firebase')
        ok('yang DISENGAJA kontrol tetap ditulis barisnya (ditandai DISENGAJA) tapi tanpa peringatan di ringkasan',
           len(baris(k)) == 2 and all(b.endswith(' · DISENGAJA: kontrol 9 memutus Firebase') for b in baris(k)) and not peringatan(k), k)
    finally:
        shutil.rmtree(kerja, ignore_errors=True)
    return out


KONTROL = [
    ('pencatat tidak mencetak apa pun', [('coba_ulang.py', "    print('DICOBA ULANG: ' + teks, flush=True)\n", "    pass\n")]),
    ('buka() kembali ke cacat 8dcaae2 (selesai tanpa DOM tidak diulang)',
     [('uji_antrean_kasir.py', "if gambar or (keadaan['siap'].is_set() and '</html>' in h): return h", "if gambar or keadaan['siap'].is_set(): return h")]),
    ('buka() mengulang tanpa mencatat', [('uji_antrean_kasir.py', "        if coba > 1: coba_ulang.catat(jalur, sebab, coba, BATAS)\n", "")]),
    ('uji_layar_kunci mengulang diam-diam lagi', [('uji_layar_kunci.py', "        if ke > 1: coba_ulang.catat(jalur, sebab, ke, coba, disengaja=DISENGAJA)\n", "")]),
    ('peringatan GitHub Actions hilang', [('coba_ulang.py', "print('::warning title=DICOBA ULANG::'", "print('(peringatan) DICOBA ULANG::'")]),
    ('yang disengaja ikut jadi peringatan', [('coba_ulang.py', "if os.environ.get('GITHUB_ACTIONS') and not disengaja:", "if os.environ.get('GITHUB_ACTIONS'):")]),
    ('nama uji tidak disebut', [('coba_ulang.py', "    teks = '%s · %s — %s (percobaan %d dari %d)' % (nama_uji(), halaman, sebab, ke, dari)",
                                 "    teks = '%s — %s (percobaan %d dari %d)' % (halaman, sebab, ke, dari)")]),
]


if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti in KONTROL:
            try:
                g = [x for x in semua(ganti) if not x[1]]
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
