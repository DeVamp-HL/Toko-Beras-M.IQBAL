#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_salinan_peramban.py — putaran T1 langkah 4 (owner 16 Nov 2026): aplikasi DIBUKA tanpa internet, di PERAMBAN SUNGGUHAN.

Chrome headless dikendalikan lewat DevTools (--remote-debugging-pipe, satu Chrome, satu profil baru, dimatikan sesudahnya) atas SALINAN baru/ yang
dilayani lokal. Firebase PALSU (uji_layar_kunci.PALSU) dilayani dari ASAL LAIN (server kedua, Access-Control-Allow-Origin *) = pengganti CDN gstatic,
jadi uji ini tidak butuh internet sama sekali. sw-baru.js salinan dicap dengan cap_sw_baru (daftar & sidik berkas salinan itu).

  1. PASANG   buka /baru/index.html?salinan=pasang (online) → salinan versi A terpasang, halaman dikendalikan, kalimat "Bisa dibuka tanpa internet"
  2. TANPA INTERNET   KEDUA server dimatikan → buka /baru/index.html → aplikasi jalan (semua modul + modul "CDN" + css dari salinan; tirai masuk tampil)
  3. VERSI BARU   server hidup lagi dengan versi B → buka → A tersaji dulu, B diunduh di belakang layar, dipasang sendiri di layar masuk (aman) → halaman B
  4. BERKAS BASI   versi C dicap tapi server masih menyajikan app.js B → C DITOLAK (kalimat menyebut "sidik beda"), B tetap dipakai

    python3 -u alat-uji/uji_salinan_peramban.py            → LULUS (0) / GAGAL UJI (2)
    python3 -u alat-uji/uji_salinan_peramban.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)

Aturan Mac owner (CLAUDE.md): satu Chrome, dimatikan seluruh grup prosesnya sesudah dipakai; kontrol = beberapa Chrome BERURUTAN (jalankan di runner).
"""
import os, re, sys, json, time, fcntl, shutil, signal, threading, tempfile, http.server, functools
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import cap_sw_baru  # noqa: E402
from uji_layar_kunci import CHROME, PALSU, SDK, _ikat_tanpa_dns  # noqa: E402
IKON = ['icon-sistem-32.png', 'icon-sistem-180.png']


# ---------- server ----------
class Diam(http.server.SimpleHTTPRequestHandler):
    cors = False
    def log_message(self, *a): pass
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        if self.cors: self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    def guess_type(self, path):
        return 'text/javascript' if str(path).endswith('.js') else super().guess_type(path)


class Server:
    def __init__(self, d, cors=False):
        self.d, self.cors = d, cors; self.port = None; self.srv = None
    def hidup(self):
        kelas = type('DiamRun', (Diam,), {'cors': self.cors})
        Srv = type('SrvUji', (http.server.ThreadingHTTPServer,), {'request_queue_size': 128, 'daemon_threads': True, 'server_bind': _ikat_tanpa_dns, 'allow_reuse_address': True})
        self.srv = Srv(('127.0.0.1', self.port or 0), functools.partial(kelas, directory=self.d)); self.port = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
    def mati(self):
        if self.srv: self.srv.shutdown(); self.srv.server_close(); self.srv = None   # soket ditutup: sambungan DITOLAK (bukan menggantung)


# ---------- Chrome lewat DevTools (pipa fd 3/4) ----------
def _fd_tinggi(fd):
    t = fcntl.fcntl(fd, fcntl.F_DUPFD_CLOEXEC, 10); os.close(fd); return t   # jauh dari 0–4: dup2 ke 3/4 pasti mencabut CLOEXEC


class Chrome:
    def __init__(self):
        self.profil = tempfile.mkdtemp(prefix='salinan-profil-'); self.log = tempfile.mkstemp(prefix='salinan-log-', suffix='.txt')
        a_r, a_w = (_fd_tinggi(x) for x in os.pipe()); b_r, b_w = (_fd_tinggi(x) for x in os.pipe())
        aksi = [(os.POSIX_SPAWN_DUP2, a_r, 3), (os.POSIX_SPAWN_DUP2, b_w, 4), (os.POSIX_SPAWN_DUP2, self.log[0], 1), (os.POSIX_SPAWN_DUP2, self.log[0], 2)]
        argv = [CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--disable-component-update', '--disable-background-networking',
                '--remote-debugging-pipe', '--user-data-dir=' + self.profil, 'about:blank']
        self.pid = os.posix_spawn(CHROME, argv, os.environ, file_actions=aksi, setpgroup=0)   # grup proses sendiri: dimatikan sekaligus
        os.close(a_r); os.close(b_w); os.close(self.log[0])
        self.w, self.r = a_w, b_r; self.n = 0; self.jawab = {}; self.kunci = threading.Condition(); self.hidup = True
        threading.Thread(target=self._baca, daemon=True).start()
        t = self.kirim('Target.createTarget', {'url': 'about:blank'})['targetId']
        self.sesi = self.kirim('Target.attachToTarget', {'targetId': t, 'flatten': True})['sessionId']
        self.kirim('Page.enable', {}, sesi=self.sesi)

    def _baca(self):
        sisa = b''
        while True:
            try: b = os.read(self.r, 1 << 16)
            except OSError: b = b''
            if not b: break
            sisa += b
            while b'\0' in sisa:
                satu, sisa = sisa.split(b'\0', 1)
                try: m = json.loads(satu)
                except ValueError: continue
                if 'id' in m:
                    with self.kunci: self.jawab[m['id']] = m; self.kunci.notify_all()
        with self.kunci: self.hidup = False; self.kunci.notify_all()

    def kirim(self, metode, param, sesi=None, batas=30):
        with self.kunci: self.n += 1; i = self.n
        pesan = {'id': i, 'method': metode, 'params': param}
        if sesi: pesan['sessionId'] = sesi
        os.write(self.w, json.dumps(pesan).encode() + b'\0')
        akhir = time.time() + batas
        with self.kunci:
            while i not in self.jawab:
                if not self.hidup or time.time() > akhir: raise RuntimeError('Chrome tidak menjawab ' + metode)
                self.kunci.wait(0.5)
            m = self.jawab.pop(i)
        if 'error' in m: raise RuntimeError(metode + ': ' + json.dumps(m['error'])[:200])
        return m.get('result', {})

    def buka(self, url):
        self.kirim('Page.navigate', {'url': url}, sesi=self.sesi)

    def nilai(self, js):
        try:
            r = self.kirim('Runtime.evaluate', {'expression': js, 'awaitPromise': True, 'returnByValue': True}, sesi=self.sesi, batas=15)
        except RuntimeError:
            return None   # konteks berganti (muat ulang) — dicoba lagi oleh tunggu()
        if r.get('exceptionDetails'): return None
        return (r.get('result') or {}).get('value')

    def tunggu(self, js, batas):
        akhir = time.time() + batas; v = None
        while time.time() < akhir:
            v = self.nilai(js)
            if v: return v
            time.sleep(0.5)
        return v

    def tutup(self):
        try: os.killpg(self.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError): pass
        try: os.waitpid(self.pid, 0)
        except ChildProcessError: pass
        for fd in (self.w, self.r):
            try: os.close(fd)
            except OSError: pass
        shutil.rmtree(self.profil, ignore_errors=True)
        try: os.unlink(self.log[1])
        except OSError: pass


# ---------- salinan situs ----------
VERSI_JS = ("(async () => { const c = navigator.serviceWorker && navigator.serviceWorker.controller; if (!c) return null; return await new Promise((jadi) => {"
            " const ch = new MessageChannel(); const t = setTimeout(() => jadi(null), 3000); ch.port1.onmessage = (e) => { clearTimeout(t); jadi(e.data); };"
            " c.postMessage({ jenis: 'versi' }, [ch.port2]); }); })()")
JALAN_JS = ("(() => { const b = document.body; const f = document.getElementById('formMasuk'); if (!b || !b.classList.contains('terkunci') || !f || f.hidden) return null;"
            " return { versi: window.__versiUji || '', dikendalikan: !!(navigator.serviceWorker && navigator.serviceWorker.controller), css: document.styleSheets.length,"
            " ket: (document.getElementById('salinanKet') || {}).textContent || '' }; })()")


def syarat(kondisi):
    """Ekspresi: keadaan jalan (JALAN_JS) yang memenuhi kondisi atas j, selain itu null."""
    return "(() => { const j = " + JALAN_JS + "; return j && (" + kondisi + ") ? j : null; })()"


def siapkan(d, cdn_port, tpl, rusak_situs=None):
    """Salinan baru/ di d/baru + ikon; Firebase palsu di d/_cdn (asal lain); impor & modulepreload gstatic → asal lain; tanpa Google Fonts."""
    shutil.copytree(os.path.join(AKAR, 'baru'), os.path.join(d, 'baru'))
    for i in IKON: shutil.copy(os.path.join(AKAR, i), os.path.join(d, i))
    os.makedirs(os.path.join(d, '_cdn', 'firebasejs'), exist_ok=True)
    for nama, isi in PALSU.items(): open(os.path.join(d, '_cdn', 'firebasejs', nama), 'w', encoding='utf-8').write(isi)
    cdn = 'http://127.0.0.1:%d/firebasejs/' % cdn_port
    for b in ('baru/js/data/firebase.js', 'baru/index.html'):
        p = os.path.join(d, b); s = open(p, encoding='utf-8').read()
        for nama in PALSU: assert SDK + nama in s, b + ': alamat ' + nama + ' berubah — perbarui uji'; s = s.replace(SDK + nama, cdn + nama)
        if b.endswith('index.html'):
            s2 = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]+">\n', '', s); assert s2 != s, 'link Google Fonts berubah — perbarui uji'
            s = s2.replace("script-src 'self' https://www.gstatic.com", "script-src 'self' https://www.gstatic.com http://127.0.0.1:%d" % cdn_port, 1)
        open(p, 'w', encoding='utf-8').write(s)
    tandai(d, 'A')
    for berkas, lama, baru in (rusak_situs or []):
        p = os.path.join(d, 'baru', berkas); s = open(p, encoding='utf-8').read(); assert lama in s, 'kontrol basi: ' + berkas + ' · ' + lama[:60]
        open(p, 'w', encoding='utf-8').write(s.replace(lama, baru, 1))
    return [cdn + n for n in sorted(PALSU)]


def tandai(d, v):
    p = os.path.join(d, 'baru', 'js', 'app.js'); s = open(p, encoding='utf-8').read()
    s = re.sub(r"\nwindow\.__versiUji = '[A-Z]';\n$", '', s) + "\nwindow.__versiUji = '" + v + "';\n"
    open(p, 'w', encoding='utf-8').write(s)


def cap(d, tpl, versi, luar, buang=None):
    berkas = [[r, cap_sw_baru.sidik(f)] for r, f in cap_sw_baru.daftar_berkas(d) if r != buang]
    nilai = {'VERSI': versi, 'TERBIT': '2026-11-16T12:00:00Z', 'BERKAS': berkas, 'LUAR': luar, 'HURUF': ''}
    open(os.path.join(d, 'baru', 'sw-baru.js'), 'w', encoding='utf-8').write(cap_sw_baru.cap(tpl, nilai))
    return len(berkas)


def jalankan(rusak_sw=None, rusak_situs=None, buang=None, cukup=None):
    """→ [(langkah, lulus, keterangan)]. Berhenti di langkah pertama yang gagal (langkah berikutnya bergantung padanya)."""
    hasil = []
    def ok(n, c, k=''): hasil.append((n, bool(c), k)); return bool(c)
    tpl = open(os.path.join(AKAR, 'baru', 'sw-baru.js'), encoding='utf-8').read()
    for lama, baru in (rusak_sw or []): assert lama in tpl, 'kontrol basi: sw-baru.js · ' + lama[:60]; tpl = tpl.replace(lama, baru, 1)
    d = tempfile.mkdtemp(prefix='salinan-'); situs = Server(d); cdn = Server(os.path.join(d, '_cdn'), cors=True); ch = None
    try:
        os.makedirs(os.path.join(d, '_cdn')); cdn.hidup(); situs.hidup()
        luar = siapkan(d, cdn.port, tpl, rusak_situs)
        n = cap(d, tpl, 'versi-a', luar, buang)
        dasar = 'http://127.0.0.1:%d/baru/' % situs.port
        ch = Chrome()
        # 1 · PASANG
        ch.buka(dasar + 'index.html?salinan=pasang')
        v = ch.tunggu(VERSI_JS + ".then((v) => v && v.lengkap ? v : null)", 90)
        if not ok('1 pasang: salinan versi A lengkap & halaman dikendalikan (' + str(n) + ' berkas)', v and v.get('versi') == 'versi-a', v): return hasil
        j = ch.tunggu(syarat("j.ket.indexOf('Bisa dibuka tanpa internet') === 0"), 20)
        if not ok('1 pasang: kalimat "Bisa dibuka tanpa internet"', j, j): return hasil
        if cukup == 1: return hasil
        # 2 · TANPA INTERNET
        situs.mati(); cdn.mati()
        ch.buka(dasar + 'index.html')
        j = ch.tunggu(JALAN_JS, 45)
        if not ok('2 tanpa internet: aplikasi jalan dari salinan (tirai masuk tampil, versi A, ' + str((j or {}).get('css')) + ' stylesheet)',
                  j and j.get('versi') == 'A' and j.get('dikendalikan') and j.get('css', 0) >= 14, j): return hasil
        if cukup == 2: return hasil
        # 3 · VERSI BARU
        tandai(d, 'B'); cap(d, tpl, 'versi-b', luar, buang); situs.hidup(); cdn.hidup()
        ch.buka(dasar + 'index.html')
        j = ch.tunggu(syarat("j.versi === 'B'"), 120)
        v = ch.nilai(VERSI_JS)
        if not ok('3 versi baru: B diunduh di belakang layar lalu dipasang sendiri di layar masuk', j and v and v.get('versi') == 'versi-b' and v.get('lengkap'), {'halaman': j, 'salinan': v}): return hasil
        # 4 · BERKAS BASI
        app = os.path.join(d, 'baru', 'js', 'app.js'); isi_b = open(app, encoding='utf-8').read()
        tandai(d, 'C'); cap(d, tpl, 'versi-c', luar, buang); open(app, 'w', encoding='utf-8').write(isi_b)   # server masih menyajikan app.js B
        ch.buka(dasar + 'index.html')
        j = ch.tunggu("(() => { const k = (document.getElementById('salinanKet') || {}).textContent || ''; return /sidik beda/.test(k) ? k : null; })()", 90)
        time.sleep(3); v = ch.nilai(VERSI_JS); m = ch.nilai("window.__versiUji")
        ok('4 berkas basi: versi C DITOLAK (kalimat menyebut sidik beda), B tetap dipakai', j and m == 'B' and v and v.get('versi') == 'versi-b', {'kalimat': j, 'halaman': m, 'salinan': v})
        return hasil
    except Exception as e:   # noqa: BLE001 — galat alat = GAGAL, bukan diam
        ok('alat uji jatuh', False, repr(e)[:300]); return hasil
    finally:
        if ch: ch.tutup()
        situs.mati(); cdn.mati(); shutil.rmtree(d, ignore_errors=True)


KONTROL = [
    # (nama, rusak sw-baru.js, rusak situs, berkas dibuang dari daftar, cukup sampai langkah)
    ('satu modul tidak masuk daftar salinan (tanpa internet jatuh)', None, None, 'js/inti/format.js', 2),
    ('halaman tidak pernah memasang versi baru', None, [('js/inti/salinan.js', "if (ok) api.pakaiSekarang();", "if (ok && false) api.pakaiSekarang();")], None, None),
    ('sidik tidak dicocokkan (berkas basi dipakai)', [("if ((await sidikDari(dicek)) !== sidik)", "if (false)")], None, None, None),
]


def main():
    if not CHROME:
        print('Chrome tidak ditemukan — uji peramban salinan DILEWATI'); sys.exit(2 if os.environ.get('CI') else 0)
    if '--kontrol' in sys.argv:
        diam = []
        for nama, rsw, rsitus, buang, cukup in KONTROL:
            h = jalankan(rsw, rsitus, buang, cukup); bunyi = any(not c for _, c, _ in h)
            print(('  tertangkap: ' if bunyi else '  DIAM     : ') + nama + ('' if not bunyi else ' · ' + next(n for n, c, _ in h if not c)), flush=True)
            if not bunyi: diam.append(nama)
        print('KONTROL ' + ('LULUS' if not diam else 'GAGAL') + ' ' + str(len(KONTROL) - len(diam)) + '/' + str(len(KONTROL)))
        sys.exit(3 if diam else 0)
    h = jalankan(); gagal = [x for x in h if not x[1]]
    for n, c, k in h: print(('  ok  ' if c else 'GAGAL ') + n + ('' if c else ' · ' + json.dumps(k, ensure_ascii=False)[:400]), flush=True)
    lengkap = len(h) >= 5 and not gagal
    print(('LULUS ' if lengkap else 'GAGAL UJI ') + str(len(h) - len(gagal)) + ' langkah lulus · ' + str(len(gagal)) + ' gagal')
    sys.exit(0 if lengkap else 2)


if __name__ == '__main__':
    main()
