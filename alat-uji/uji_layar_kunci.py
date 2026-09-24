#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_layar_kunci.py — putaran 23c: TIRAI. Selama belum masuk (atau akun belum disetujui / nonaktif), layar di belakang formulir Masuk KOSONG:
satu angka rupiah pun tidak boleh ada di DOM, tidak ada kartu, tidak ada nama.

Diuji di PERAMBAN SUNGGUHAN (Chrome headless, profil baru tiap kali) atas SALINAN baru/ yang dilayani lokal. Penyimpanan lokal peramban diisi dulu
dengan angka CONTOH (titik kas, layar terakhir = Beranda) — persis jalan bocor yang pernah ada: beranda menggambar "kas tercatat" dari penyimpanan lokal
sebelum siapa pun masuk.
  · UJI      : /baru/index.html tanpa masuk → body.terkunci (aplikasi sungguh jalan & menunggu masuk), formulir Masuk tampil, 0 angka rupiah, 0 kartu di <main>.
  · KONTROL 1: mode cadangan (?cadangan=, angka contoh) → tirai terbuka, angka rupiah ADA → pembaca DOM ini memang bisa melihat layar yang tergambar.
  · KONTROL 2: tirai dirusak (terkunci() selalu false) → angka rupiah muncul di belakang formulir → uji BERBUNYI.
  · KONTROL 3: beranda tanpa penjaga tirai → "kas tercatat" dari penyimpanan lokal muncul → uji BERBUNYI.
Butuh jaringan (Firebase SDK dari CDN). Aplikasi yang tidak jalan = GAGAL, bukan lulus (body.terkunci tidak ada).

    python3 alat-uji/uji_layar_kunci.py            → LULUS / GAGAL (keluar 2)
    python3 alat-uji/uji_layar_kunci.py --kontrol  → kontrol wajib berbunyi (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, time, shutil, socket, subprocess, tempfile, threading, http.server, functools

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
CHROME = next((p for p in ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'] if os.path.exists(p)), None)
# ANGKA CONTOH (bukan angka toko)
TITIK_KAS = {'tanggal': '2026-09-15', 'laci': 2000000, 'brankas': 10000000, 'rekening': 3000000, 'amplop': 1000000}
CADANGAN = {'versi': 5, 'diunduhPada': '2026-09-19T03:00:00.000Z',
            'penjualan': [{'id': 'c1', 'tanggal': '2026-09-19', 'jam': '09:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 50, 'hargaTotal': 690000, 'hppTotalSaatJual': 650000, 'trxId': 't1'}]}
RP = re.compile(r'Rp\s?\d')


def siapkan(rusak=None):
    """Salinan baru/ + berkas cadangan contoh; index.html diberi skrip pengisi penyimpanan lokal SEBELUM app.js. rusak = [(berkas, lama, baru)]."""
    d = tempfile.mkdtemp(prefix='kunci-'); shutil.copytree(os.path.join(AKAR, 'baru'), os.path.join(d, 'baru'))
    idx = os.path.join(d, 'baru', 'index.html'); t = open(idx, encoding='utf-8').read()
    isi = "<script>try{localStorage.setItem('miqbal_titik_kas_v1'," + json.dumps(json.dumps(TITIK_KAS)) + ");localStorage.setItem('miqbal_baru_tab','ringkasan');}catch(e){}</script>"
    # penahan waktu: event load menunggu gambar /_tahan, yang baru dijawab server sesudah halaman mengabarkan /_siap (tirai tertutup ATAU ada isi di <main>) + jeda
    tahan = ("<img src='/_tahan' alt='' style='display:none'><script>var __t=setInterval(function(){if(document.body.classList.contains('terkunci')||document.querySelector('main *'))"
             "{clearInterval(__t);fetch('/_siap');}},150);</script>")
    assert '<head>' in t and '</body>' in t; open(idx, 'w', encoding='utf-8').write(t.replace('<head>', '<head>' + isi, 1).replace('</body>', tahan + '</body>', 1))
    json.dump(CADANGAN, open(os.path.join(d, 'cadangan-contoh.json'), 'w'))
    for berkas, lama, baru in (rusak or []):
        p = os.path.join(d, 'baru', berkas); s = open(p, encoding='utf-8').read(); assert lama in s, 'kontrol basi: ' + berkas + ' · ' + lama[:50]; open(p, 'w', encoding='utf-8').write(s.replace(lama, baru))
    return d


GIF = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'


class Diam(http.server.SimpleHTTPRequestHandler):
    siap = None   # threading.Event per server
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.startswith('/_siap'):
            self.siap.set(); self.send_response(204); self.end_headers(); return
        if self.path.startswith('/_tahan'):
            self.siap.wait(20); time.sleep(2.5)   # aplikasi sudah jalan → beri waktu jawaban Firebase / cadangan tergambar
            self.send_response(200); self.send_header('Content-Type', 'image/gif'); self.end_headers(); self.wfile.write(GIF); return
        return super().do_GET()


def layani(d):
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    kelas = type('DiamRun', (Diam,), {'siap': threading.Event()})
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(kelas, directory=d)); threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def dom(d, jalur, coba=4):
    """DOM yang SAH: hanya hasil cetak sesudah halaman mengabarkan /_siap (aplikasi sungguh jalan). Chrome headless kadang mencetak sebelum app.js diminta → diulang."""
    for _ in range(coba):
        h, siap = dom_sekali(d, jalur)
        if siap and '</html>' in h: return h
    return ''


def dom_sekali(d, jalur, tunggu=80):
    """DOM sesudah halaman dimuat (+ batas waktu Chrome 12 detik). Chrome di macOS kadang tidak keluar sesudah mencetak DOM → dibaca sampai </html>, lalu dimatikan."""
    srv, port = layani(d); profil = tempfile.mkdtemp(prefix='kunci-profil-')
    p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--disable-component-update', '--disable-background-networking',
                          '--user-data-dir=' + profil, '--dump-dom', 'http://127.0.0.1:%d%s' % (port, jalur)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    buf = []; selesai = threading.Event()
    def baca():
        for baris in iter(p.stdout.readline, b''):
            buf.append(baris.decode('utf-8', 'replace'))
            if b'</html>' in baris: break
        selesai.set()
    threading.Thread(target=baca, daemon=True).start()
    try:
        selesai.wait(tunggu); return ''.join(buf), srv.RequestHandlerClass.func.siap.is_set()
    finally:
        p.kill(); p.wait(); srv.shutdown(); shutil.rmtree(profil, ignore_errors=True)


def body_kelas(h):
    m = re.search(r'<body[^>]*class="([^"]*)"', h); return m.group(1).split() if m else []


def isi_main(h):
    return ''.join(re.findall(r'<main\b[^>]*>(.*?)</main>', h, re.S))


def periksa_terkunci(h):
    """→ daftar cacat untuk halaman yang BELUM masuk."""
    c = []
    if not h: return ['aplikasi tidak sempat jalan di peramban uji (4 kali) — uji tidak sah, bukan lulus']
    if 'terkunci' not in body_kelas(h): c.append('body.terkunci tidak ada — aplikasi tidak jalan atau tirai tidak menutup (uji tidak sah)')
    if 'id="formMasuk"' not in h: c.append('formulir Masuk tidak ada')
    rp = RP.findall(h)
    if rp: c.append('%d angka rupiah di DOM sebelum masuk (mis. %s)' % (len(rp), ', '.join(sorted(set(re.findall(r'Rp\s?[\d.]+', h)))[:4])))
    m = isi_main(h)
    if re.search(r'class="[^"]*\bkartu\b', m): c.append('ada kartu di <main> sebelum masuk')
    if m.strip(): c.append('<main> tidak kosong (%d karakter)' % len(m.strip()))
    return c


if __name__ == '__main__':
    if not CHROME:
        print('Chrome tidak ditemukan — uji peramban DILEWATI' + (' (CI: GAGAL)' if os.environ.get('CI') else ''))
        sys.exit(2 if os.environ.get('CI') else 0)
    if '--kontrol' in sys.argv:
        kode = 0
        d = siapkan()
        try:
            h = dom(d, '/baru/index.html?cadangan=/cadangan-contoh.json'); n = len(RP.findall(h))
            ok = n > 0 and 'terkunci' not in body_kelas(h)
            print(('BERBUNYI ' if ok else 'DIAM!!   ') + 'kontrol 1 · mode cadangan (terbuka): pembaca DOM melihat %d angka rupiah' % n); kode = kode if ok else 3
        finally: shutil.rmtree(d, ignore_errors=True)
        for nama, rusak in [('kontrol 2 · tirai dirusak (terkunci() selalu false)', [('js/inti/kunci.js', 'export const terkunci = () => _kunci;', 'export const terkunci = () => false;')]),
                            ('kontrol 3 · beranda tanpa penjaga tirai', [('js/layar/ringkasan.js', "if (!tampil || terkunci()) return;\n    if (!$('rkHero')) bangun();", "if (!tampil) return;\n    if (!$('rkHero')) bangun();"),
                                                                          ('js/app.js', "SEMUA_LAYAR().forEach((l) => l.tampilkan(false));\n  if (kunci) { Object.keys(LAYAR_ADA).forEach((k) => { LAYAR_ADA[k].innerHTML = ''; }); return; }", "if (kunci) return;")])]:
            d = siapkan(rusak)
            try:
                c = periksa_terkunci(dom(d, '/baru/index.html'))
                print(('BERBUNYI ' if c else 'DIAM!!   ') + nama + ' → ' + (c[0][:120] if c else '-'))
                if not c: kode = 3
            finally: shutil.rmtree(d, ignore_errors=True)
        sys.exit(kode)
    d = siapkan()
    try:
        c = periksa_terkunci(dom(d, '/baru/index.html'))
    finally: shutil.rmtree(d, ignore_errors=True)
    if c: print('TIRAI GAGAL:'); [print('   ✗ ' + x) for x in c]; sys.exit(2)
    print('TIRAI LULUS: sebelum masuk — formulir Masuk tampil, 0 angka rupiah, 0 kartu, semua <main> kosong (penyimpanan lokal berisi titik kas contoh)')
