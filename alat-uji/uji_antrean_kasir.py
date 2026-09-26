#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_antrean_kasir.py — putaran 25b: ANTREAN KASIR TIDAK BOLEH MACET, di PERAMBAN SUNGGUHAN (Chrome headless) atas SALINAN kasir-darurat-nominal.html
dan kasir.html yang dilayani lokal, dengan Firestore REST PALSU (fetch diganti sebelum skrip halaman jalan) yang menolak karcis bertanggal bulan
"terkunci" persis seperti rules v4 untuk kasir@ (403 PERMISSION_DENIED), dan bisa diatur menjawab 401 / 429 / 503 / sinyal putus.

SKENARIO (tiap berkas):
  · karcis ke-2 dari 5 ditolak → karcis 1, 3, 4, 5 masuk; karcis 2 di daftar "ditolak" (isi utuh); layar masuk TIDAK muncul; pita tampil;
    karcis yang ditolak tidak dikirim ulang walau antrean dijalankan lagi
  · 401 (tidak dikenali) → layar masuk muncul; antrean utuh; tidak ada yang pindah ke "ditolak"
  · sinyal putus / 429 / 503 → antrean utuh, tidak ada yang "ditolak", tidak ada layar masuk; dicoba lagi → semua masuk
  · belum masuk → TIDAK ada kiriman sama sekali (403 tanpa kunci bukan penolakan aturan)
  · denyut melaporkan antrean, jumlah ditolak, dan versi (= VERSI sw-kasir.js)
  · sesudah MUAT ULANG (profil & alamat sama): karcis yang ditolak masih ada, pita masih tampil, daftarnya menyebut tanggal & nominal;
    "sudah dicatat ulang" butuh DUA ketukan dan MEMINDAH ke arsip (tidak menghapus)
STATIS: golonganJawaban() kembar huruf per huruf di kedua berkas; VERSI_APLIKASI kedua berkas = VERSI sw-kasir.js = KP_VERSI_KASIR_25B (/baru/);
  service worker mengunduh versi baru melewati cache HTTP (cache:'reload'); kedua berkas memuat ulang diri saat versi baru mengambil alih.
/baru/ (jsc, KOTAK PASIR — nama & angka contoh): ⛔ "semua perangkat kasir yang berdenyut 7 hari terakhir sudah versi 25b" menyebut nama perangkat
  yang tertinggal; Beranda › Perlu perhatian menyebut antrean, ditolak, dan versi lama per HP kasir.

    python3 alat-uji/uji_antrean_kasir.py                → N lulus · 0 gagal (keluar 1 bila ada yang gagal)
    python3 alat-uji/uji_antrean_kasir.py --kontrol      → tiap kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
    python3 alat-uji/uji_antrean_kasir.py --gambar DIR   → juga simpan tangkapan layar kasir darurat (pita & daftar ditolak) ke DIR
Tanpa jaringan luar, tanpa Node. Butuh Google Chrome (sama dengan uji_layar_kunci.py).
"""
import os, re, sys, json, time, shutil, socket, tempfile, threading, subprocess, http.server, functools
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
CHROME = next((p for p in ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'] if os.path.exists(p)), None)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
DARURAT, KASIR = 'kasir-darurat-nominal.html', 'kasir.html'

# ---------- Firestore REST PALSU: dipasang PALING AWAL di <head>, sebelum skrip halaman ----------
KEPALA = r"""<script>
(function () {
  try { delete Navigator.prototype.serviceWorker; } catch (e) {}   // tanpa service worker: yang diuji berkasnya, bukan cache
  var P = window.__palsu = { jaringan: true, mode: 'ok', sampaiBulan: '2026-08', masuk: [], permintaan: [], denyut: [], tanpaKunci: 0 };
  var TOLAK = { error: { code: 403, message: 'Missing or insufficient permissions.', status: 'PERMISSION_DENIED' } };
  function jawab(status, isi) { return Promise.resolve(new Response(JSON.stringify(isi || {}), { status: status, headers: { 'Content-Type': 'application/json' } })); }
  function nilai(v) { if (!v) return null; if ('stringValue' in v) return v.stringValue; if ('integerValue' in v) return Number(v.integerValue); if ('doubleValue' in v) return v.doubleValue;
    if ('booleanValue' in v) return v.booleanValue; if ('nullValue' in v) return null; if ('mapValue' in v) { var o = {}, f = v.mapValue.fields || {}; for (var k in f) o[k] = nilai(f[k]); return o; } return null; }
  var asli = window.fetch.bind(window);
  window.fetch = function (url, opsi) {
    url = String(url); opsi = opsi || {};
    if (url.charAt(0) === '/' || url.indexOf(location.origin) === 0) return asli(url, opsi);   // server uji (/_siap), bukan Firestore
    if (!P.jaringan) return Promise.reject(new TypeError('Failed to fetch'));
    if (url.indexOf('securetoken.googleapis.com') >= 0) return jawab(200, { id_token: 't-uji-segar', refresh_token: 'r-uji', expires_in: '3600' });
    if (url.indexOf('identitytoolkit.googleapis.com') >= 0) return jawab(200, { idToken: 't-uji', refreshToken: 'r-uji', expiresIn: '3600' });
    var m = /\/documents\/([^/?]+)\/([^?]+)/.exec(url); if (!m) return jawab(404, {});
    var koleksi = m[1], id = decodeURIComponent(m[2]), metode = String(opsi.method || 'GET').toUpperCase();
    var kunci = !!(opsi.headers && opsi.headers.Authorization);
    if (metode === 'GET') return jawab(404, { error: { code: 404, status: 'NOT_FOUND' } });
    var data = {}; try { var f = JSON.parse(opsi.body).fields || {}; for (var k in f) data[k] = nilai(f[k]); } catch (e) {}
    if (koleksi === 'perangkatStatus') { P.denyut.push(data); return jawab(200, {}); }
    P.permintaan.push({ koleksi: koleksi, id: id, kunci: kunci, hargaTotal: data.hargaTotal, tanggal: data.tanggal });
    if (!kunci) { P.tanpaKunci++; return jawab(403, TOLAK); }                        // server sungguhan: request.auth == null → ditolak rules
    if (P.mode === '401') return jawab(401, { error: { code: 401, message: 'Request had invalid authentication credentials.', status: 'UNAUTHENTICATED' } });
    if (P.mode === '429') return jawab(429, { error: { code: 429, message: 'Quota exceeded.', status: 'RESOURCE_EXHAUSTED' } });
    if (P.mode === '503') return jawab(503, { error: { code: 503, message: 'The service is currently unavailable.', status: 'UNAVAILABLE' } });
    if (P.sampaiBulan && String(data.tanggal || '').slice(0, 7) <= P.sampaiBulan) return jawab(403, TOLAK);   // rules v4 kasir@: tglBaru di bulan terkunci
    P.masuk.push({ koleksi: koleksi, id: id, hargaTotal: data.hargaTotal, tanggal: data.tanggal });
    return jawab(200, { name: 'dok', fields: {} });
  };
})();
</script>"""

# ---------- penyesuai per berkas: cara mencatat, kunci penyimpanan, denyut ----------
PENYESUAI = {
    DARURAT: r"""var A = { antrean: 'darurat_antrean_v1', gagal: 'darurat_gagal_v1', arsip: 'darurat_ditolak_arsip_v1', auth: 'kasir_auth_v1',
  catat: function (n) { String(n).split('').forEach(function (c) { tekanAngka(c); }); simpanNominal(); },   // lewat papan angka + SIMPAN sungguhan
  catatLama: function (n, tgl) { var a = JSON.parse(localStorage.getItem(this.antrean) || '[]'); var id = Date.now() + Math.random();   // karcis yang tertahan offline sejak bulan lalu
    a.push({ koleksi: 'penjualan', docId: String(id), data: { id: id, tanggal: tgl, jam: '20:15', jenis: 'kasir_darurat_nominal', namaProduk: '(tidak tercatat — kasir darurat)', hargaTotal: n,
      caraBayar: 'Tunai', namaPelanggan: '', grupNota: id, oleh: '(darurat tanpa nama)', perangkat: 'd-uji' } }); localStorage.setItem(this.antrean, JSON.stringify(a)); },
  denyut: function () { denyutTerakhirD = 0; kirimDenyutD(); } };""",
    KASIR: r"""var A = { antrean: 'kasir_antrean_v1', gagal: 'kasir_gagal_v1', arsip: 'kasir_ditolak_arsip_v1', auth: 'kasir_auth_v1',
  catat: function (n) { tambahAntrean('penjualan', { id: idUnik(), tanggal: tanggalLokalIso(), jam: '10:00', jenis: 'kemasan', namaProduk: 'Barang Contoh 5kg', hargaTotal: n, caraBayar: 'Tunai', namaPelanggan: '' }); kirimAntrean(false); },
  catatLama: function (n, tgl) { tambahAntrean('penjualan', { id: idUnik(), tanggal: tgl, jam: '20:15', jenis: 'kemasan', namaProduk: 'Barang Contoh 5kg', hargaTotal: n, caraBayar: 'Tunai', namaPelanggan: '' }); },
  denyut: function () { denyutTerakhir = 0; kirimDenyut(); } };""",
}

SKENARIO = r"""<script>
(async function () {
  __PENYESUAI__
  var tunggu = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  var sampai = async function (f, ms) { var t0 = Date.now(); while (Date.now() - t0 < (ms || 6000)) { try { if (f()) return true; } catch (e) {} await tunggu(30); } return false; };
  var P = window.__palsu; var hasil = { skenario: {} };
  var L = function (k) { try { return JSON.parse(localStorage.getItem(k) || '[]'); } catch (e) { return null; } };
  var tampil = function (id) { var e = document.getElementById(id); return !!e && e.classList.contains('tampil'); };
  var reset = function (masuk) { [A.antrean, A.gagal, A.arsip].forEach(function (k) { localStorage.removeItem(k); });
    if (masuk) localStorage.setItem(A.auth, JSON.stringify({ refreshToken: 'r-uji', idToken: 't-uji', kedaluwarsa: Date.now() + 3600000 })); else localStorage.removeItem(A.auth);
    P.masuk = []; P.permintaan = []; P.denyut = []; P.tanpaKunci = 0; P.jaringan = true; P.mode = 'ok';
    document.querySelectorAll('.lapisan.tampil').forEach(function (e) { e.classList.remove('tampil'); }); };
  var diam = async function () { await sampai(function () { return !window.sedangKirim; }, 6000); await tunggu(150); };
  var kosong = function () { return sampai(function () { return L(A.antrean).length === 0; }, 6000); };
  var potret = function () { var pita = document.getElementById('pitaDitolak');
    return { antrean: L(A.antrean).map(function (x) { return x.data.hargaTotal; }),
      ditolak: L(A.gagal).map(function (x) { return { h: x.data && x.data.hargaTotal, t: x.data && x.data.tanggal, alasan: x.ditolak && x.ditolak.alasan, status: x.ditolak && x.ditolak.status }; }),
      arsip: L(A.arsip).map(function (x) { return x.data && x.data.hargaTotal; }), masuk: P.masuk.map(function (x) { return x.hargaTotal; }), login: tampil('layarLogin'),
      pita: pita && getComputedStyle(pita).display !== 'none' ? pita.textContent : '', chip: document.getElementById('chipStatus').textContent,
      permintaan: P.permintaan.map(function (x) { return x.hargaTotal; }), tanpaKunci: P.tanpaKunci }; };
  try {
    var s = new URLSearchParams(location.search).get('s') || 'utama';
    if (s === 'utama') {
      reset(true); P.jaringan = false; A.catat(1100); A.catat(1200); A.catat(1300); kirimAntrean(true); await diam(); hasil.skenario.jaringanPutus = potret();
      P.jaringan = true; kirimAntrean(true); await kosong(); await diam(); hasil.skenario.jaringanPulih = potret();
      reset(true); P.jaringan = false; A.catat(2100); A.catat(2200); P.jaringan = true; P.mode = '429'; kirimAntrean(true); await diam(); hasil.skenario.sibuk429 = potret();
      P.mode = '503'; kirimAntrean(true); await diam(); hasil.skenario.sibuk503 = potret();
      P.mode = 'ok'; kirimAntrean(true); await kosong(); await diam(); hasil.skenario.sibukPulih = potret();
      reset(true); P.jaringan = false; A.catat(3100); A.catat(3200); P.jaringan = true; P.mode = '401'; kirimAntrean(true); await sampai(function () { return tampil('layarLogin'); }, 3000); await diam();
      hasil.skenario.tidakDikenal401 = potret();
      reset(false); P.jaringan = false; A.catat(4100); A.catat(4200); P.jaringan = true; kirimAntrean(true); await diam();
      await tunggu(1700);   // kasir darurat membuka layar masuk 1,3 detik sesudah SIMPAN kalau belum masuk — tunggu di sini, jangan sampai jatuh ke skenario berikutnya
      hasil.skenario.belumMasuk = potret();
      // PALING AKHIR: karcis ke-2 dari 5 bertanggal bulan terkunci — sisanya dibaca lagi sesudah muat ulang
      reset(true); P.jaringan = false; A.catat(5100); A.catatLama(5200, '2026-08-31'); A.catat(5300); A.catat(5400); A.catat(5500);
      hasil.antreanAwal = L(A.antrean).map(function (x) { return x.data.hargaTotal; });
      P.jaringan = true; kirimAntrean(true); await kosong(); await diam();
      kirimAntrean(false); await diam(); kirimAntrean(true); await diam();
      hasil.skenario.keduaDitolak = potret();
      A.denyut(); await sampai(function () { return P.denyut.length > 0; }, 3000); hasil.denyut = P.denyut[P.denyut.length - 1] || null;
    } else if (s === 'gambarDaftar') {
      await tunggu(300); bukaDaftarDitolak();
    } else if (s === 'muatUlang') {
      await tunggu(400); hasil.skenario.sesudahMuatUlang = potret();
      bukaDaftarDitolak(); hasil.daftarTeks = document.getElementById('isiDitolak').innerText; hasil.daftarTampil = tampil('layarDitolak');
      arsipkanDitolak(); hasil.sesudahSatuKetuk = potret(); arsipkanDitolak(); hasil.sesudahDuaKetuk = potret();
      hasil.versiLayar = document.getElementById('versiApp').textContent;
    } else { await tunggu(300); }
  } catch (e) { hasil.galat = String(e && (e.stack || e.message) || e); }
  var pre = document.createElement('pre'); pre.id = '__hasil'; pre.hidden = true; pre.textContent = JSON.stringify(hasil); document.body.appendChild(pre);
  fetch('/_siap');
})();
</script>"""


# ---------- server lokal: /_tahan menahan event load sampai skenario selesai (/_siap) ----------
class Pelayan(http.server.SimpleHTTPRequestHandler):
    keadaan = None
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.startswith('/_siap'):
            self.keadaan['siap'].set(); self.send_response(204); self.end_headers(); return
        if self.path.startswith('/_tahan'):
            self.keadaan['siap'].wait(45); time.sleep(0.4)   # halaman sehat mengabarkan selesai dalam hitungan detik, juga di runner CI
            self.send_response(200); self.send_header('Content-Type', 'image/gif'); self.end_headers()
            self.wfile.write(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'); return
        return super().do_GET()
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store'); super().end_headers()


def siapkan(berkas, ganti=None):
    """Folder kerja berisi salinan berkas kasir yang disuntik (palsu di <head>, skenario + penahan di </body>). ganti = [(lama, baru)] untuk kontrol."""
    d = tempfile.mkdtemp(prefix='antre-'); t = open(os.path.join(AKAR, berkas), encoding='utf-8').read()
    for lama, baru in (ganti or []):
        assert lama in t, 'kontrol basi: ' + berkas + ' · ' + lama[:70]; t = t.replace(lama, baru)
    assert t.count('<head>') == 1 and t.count('</body>') == 1
    t = t.replace('<head>', '<head>' + KEPALA, 1).replace('</body>', SKENARIO.replace('__PENYESUAI__', PENYESUAI[berkas]) + "<img src='/_tahan' alt='' style='display:none'></body>", 1)
    open(os.path.join(d, berkas), 'w', encoding='utf-8').write(t)
    return d


def layani(d):
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    keadaan = {'siap': threading.Event()}
    kelas = type('PelayanRun', (Pelayan,), {'keadaan': keadaan})
    Srv = type('SrvAntre', (http.server.ThreadingHTTPServer,), {'request_queue_size': 64, 'daemon_threads': True})
    srv = Srv(('127.0.0.1', port), functools.partial(kelas, directory=d)); threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port, keadaan


def buka(port, keadaan, profil, jalur, gambar=None, tunggu=60):
    """Satu pemuatan halaman di Chrome headless. → DOM (teks) sesudah skenario selesai; gambar = berkas PNG (tangkapan layar, bukan DOM).
    Runner CI macOS sesekali membuat satu Chrome macet total (PR #41: 2 dari ±60 pemuatan, halaman tidak pernah jalan). Halaman yang TIDAK
    mengabarkan selesai dicoba SEKALI lagi — skenario selalu mulai dari keadaan yang ia pasang sendiri, jadi mengulang tidak meloloskan apa pun;
    halaman yang jalan tapi hasilnya salah tetap gagal di pemeriksanya."""
    h = ''
    for coba in (1, 2):
        for kunci in ('SingletonLock', 'SingletonSocket', 'SingletonCookie'):   # kunci profil sisa Chrome yang sudah dimatikan
            try:
                if os.path.lexists(os.path.join(profil, kunci)): os.unlink(os.path.join(profil, kunci))
            except OSError: pass
        h = _buka_sekali(port, keadaan, profil, jalur, gambar, tunggu)
        if gambar or keadaan['siap'].is_set(): return h
        print('  [peramban] %s tidak mengabarkan selesai (percobaan %d)' % (jalur, coba), file=sys.stderr, flush=True)
    return h


def _buka_sekali(port, keadaan, profil, jalur, gambar, tunggu):
    keadaan['siap'] = threading.Event()
    arg = [CHROME, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--disable-component-update', '--disable-background-networking',
           '--user-data-dir=' + profil, '--window-size=500,900', '--hide-scrollbars',
           '--use-mock-keychain', '--password-store=basic']   # macOS tanpa layar: jangan menunggu keychain sungguhan
    arg += (['--screenshot=' + gambar] if gambar else ['--dump-dom'])
    p = subprocess.Popen(arg + ['http://127.0.0.1:%d%s' % (port, jalur)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    buf = []; selesai = threading.Event()
    def baca():
        # Potongan MENTAH, bukan per baris: Chrome di macOS kadang tidak keluar sesudah mencetak DOM, dan kalau </html> ada di baris terakhir
        # tanpa ganti baris, readline() menunggu selamanya walau halamannya sudah selesai (PR #41: 60 detik terbuang, hasil dianggap tidak ada).
        acc = b''
        while True:
            blok = os.read(p.stdout.fileno(), 65536)
            if not blok: break
            acc += blok
            if b'</html>' in acc[-(len(blok) + 16):]: break
        buf.append(acc.decode('utf-8', 'replace'))
        selesai.set()
    threading.Thread(target=baca, daemon=True).start()
    t0 = time.time()
    try:
        if gambar:
            t0 = time.time()
            while time.time() - t0 < tunggu and p.poll() is None and not (os.path.exists(gambar) and os.path.getsize(gambar) > 0): time.sleep(0.2)
            time.sleep(0.3); return ''
        selesai.wait(tunggu); return ''.join(buf)
    finally:
        p.kill(); p.wait()
        if os.environ.get('CI'): print('  [peramban] %s %.1f dtk%s' % (jalur, time.time() - t0, '' if keadaan['siap'].is_set() else ' · halaman TIDAK mengabarkan selesai'), file=sys.stderr, flush=True)


def hasil_dari(h):
    m = re.search(r'<pre id="__hasil"[^>]*>(.*?)</pre>', h, re.S)
    if not m: return None
    import html as H
    return json.loads(H.unescape(m.group(1)))


def jalankan_berkas(berkas, ganti=None, gambar_dir=None):
    """→ (hasil utama, hasil muat ulang) untuk satu berkas; profil & alamat SAMA di kedua pemuatan (localStorage bertahan seperti di HP)."""
    d = siapkan(berkas, ganti); srv, port, keadaan = layani(d); profil = tempfile.mkdtemp(prefix='antre-profil-')
    try:
        u = hasil_dari(buka(port, keadaan, profil, '/' + berkas + '?s=utama'))
        if gambar_dir and u:
            os.makedirs(gambar_dir, exist_ok=True); dasar = os.path.splitext(berkas)[0]
            buka(port, keadaan, profil, '/' + berkas + '?s=gambar', gambar=os.path.join(gambar_dir, dasar + '-pita-ditolak.png'))
            buka(port, keadaan, profil, '/' + berkas + '?s=gambarDaftar', gambar=os.path.join(gambar_dir, dasar + '-daftar-ditolak.png'))
        m = hasil_dari(buka(port, keadaan, profil, '/' + berkas + '?s=muatUlang'))
        return u, m
    finally:
        srv.shutdown(); shutil.rmtree(profil, ignore_errors=True); shutil.rmtree(d, ignore_errors=True)


def periksa_peramban(berkas, u, m, versi_sw):
    """→ [(nama, lulus, keterangan)] untuk satu berkas."""
    kata = 'karcis' if berkas == DARURAT else 'catatan'
    out = []; ok = lambda n, c, k='': out.append((berkas + ' · ' + n, bool(c), k))
    if not u or u.get('galat'): return [(berkas + ' · skenario utama jalan', False, (u or {}).get('galat', 'tidak ada hasil (halaman tidak jalan)'))]
    S = u['skenario']
    j = S['jaringanPutus']; ok('sinyal putus: antrean utuh (3), tidak ada yang "ditolak", layar masuk tidak muncul', j['antrean'] == [1100, 1200, 1300] and not j['ditolak'] and not j['login'], j)
    j = S['jaringanPulih']; ok('sinyal kembali → dicoba lagi → ketiganya masuk berurutan, antrean kosong', j['masuk'] == [1100, 1200, 1300] and not j['antrean'] and not j['ditolak'], j)
    for k, n in (('sibuk429', '429 (kuota / sibuk)'), ('sibuk503', '503 (server galat)')):
        j = S[k]; ok(n + ': antrean utuh (2), tidak ada yang "ditolak", layar masuk tidak muncul', j['antrean'] == [2100, 2200] and not j['ditolak'] and not j['login'] and not j['masuk'], j)
    j = S['sibukPulih']; ok('server pulih → keduanya masuk', j['masuk'] == [2100, 2200] and not j['antrean'] and not j['ditolak'], j)
    j = S['tidakDikenal401']; ok('401 → layar masuk muncul, antrean utuh (2), tidak ada yang pindah ke "ditolak"', j['login'] and j['antrean'] == [3100, 3200] and not j['ditolak'] and not j['masuk'], j)
    j = S['belumMasuk']; ok('belum masuk → nol kiriman ke server (403 tanpa kunci bukan penolakan aturan), antrean utuh, tidak ada "ditolak"' + (', layar masuk muncul' if berkas == DARURAT else ''),
                            j['tanpaKunci'] == 0 and not j['permintaan'] and j['antrean'] == [4100, 4200] and not j['ditolak'] and (j['login'] or berkas != DARURAT), j)
    j = S['keduaDitolak']
    ok('antrean awal 5 ' + kata + ', yang ke-2 bertanggal bulan terkunci', u.get('antreanAwal') == [5100, 5200, 5300, 5400, 5500], u.get('antreanAwal'))
    ok(kata + ' ke-2 dari 5 ditolak → 1, 3, 4, 5 MASUK berurutan, antrean kosong', j['masuk'] == [5100, 5300, 5400, 5500] and not j['antrean'], j)
    ok(kata + ' ke-2 ada di daftar "ditolak" dengan isi utuh (nominal, tanggal) & alasan aturan (403)',
       len(j['ditolak']) == 1 and j['ditolak'][0]['h'] == 5200 and j['ditolak'][0]['t'] == '2026-08-31' and j['ditolak'][0]['alasan'] == 'aturan' and j['ditolak'][0]['status'] == 403, j['ditolak'])
    ok('layar masuk TIDAK muncul karena penolakan aturan', not j['login'], j)
    ok('yang ditolak TIDAK dikirim ulang walau antrean dijalankan dua kali lagi (satu permintaan saja)', j['permintaan'].count(5200) == 1, j['permintaan'])
    ok('pita tampil: "1 ' + kata + ' ditolak server (bulan sudah dikunci)"', ('1 ' + kata + ' ditolak server (bulan sudah dikunci)') in j['pita'], j['pita'])
    ok('bilah status menyebut "1 ditolak"', '1 ditolak' in j['chip'], j['chip'])
    dy = u.get('denyut') or {}
    ok('denyut melaporkan antrean 0, ditolak 1, versi = VERSI sw-kasir.js (' + versi_sw + ')', dy.get('antrean') == 0 and dy.get('gagal') == 1 and dy.get('versi') == versi_sw, dy)
    if not m or m.get('galat'): out.append((berkas + ' · muat ulang jalan', False, (m or {}).get('galat', 'tidak ada hasil'))); return out
    j = m['skenario']['sesudahMuatUlang']
    ok('sesudah MUAT ULANG: ' + kata + ' yang ditolak masih ada (tidak hilang), pita masih tampil', len(j['ditolak']) == 1 and j['ditolak'][0]['h'] == 5200 and 'ditolak server' in j['pita'], j)
    ok('daftar ditolak menyebut tanggal, jam & nominal supaya bisa dicatat ulang', m.get('daftarTampil') and '31/08/2026' in (m.get('daftarTeks') or '') and '20:15' in (m.get('daftarTeks') or '') and '5.200' in (m.get('daftarTeks') or ''), m.get('daftarTeks'))
    ok('"sudah dicatat ulang": satu ketukan TIDAK memindah apa pun', len(m['sesudahSatuKetuk']['ditolak']) == 1 and not m['sesudahSatuKetuk']['arsip'], m['sesudahSatuKetuk'])
    ok('ketukan kedua MEMINDAH ke arsip (tidak dihapus), pita hilang', not m['sesudahDuaKetuk']['ditolak'] and m['sesudahDuaKetuk']['arsip'] == [5200] and not m['sesudahDuaKetuk']['pita'], m['sesudahDuaKetuk'])
    ok('versi yang berjalan tampil di layar ("versi 25b")', m.get('versiLayar') == 'versi 25b', m.get('versiLayar'))
    return out


# ---------- STATIS ----------
def fungsi(teks, nama):
    m = re.search(r'function ' + nama + r'\([^)]*\) \{.*?\n\}\n', teks, re.S); return m.group(0) if m else None


def periksa_statis(teks):
    """teks = {berkas: isi} (boleh salinan rusak untuk kontrol). → [(nama, lulus, ket)]"""
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    sw = teks['sw-kasir.js']; vs = re.search(r"const VERSI = '([^']+)';", sw)
    kp = re.search(r"export const KP_VERSI_KASIR_25B = '([^']+)';", teks['baru/js/data/kunci-periode.js'])
    g1, g2 = fungsi(teks[DARURAT], 'golonganJawaban'), fungsi(teks[KASIR], 'golonganJawaban')
    ok('golonganJawaban() ada di kedua berkas dan KEMBAR huruf per huruf', g1 and g1 == g2, (g1 or '')[:80])
    for b in (DARURAT, KASIR):
        va = re.search(r"var VERSI_APLIKASI = '([^']+)';", teks[b])
        ok(b + ': VERSI_APLIKASI = VERSI sw-kasir.js (' + (vs.group(1) if vs else '?') + ')', va and vs and va.group(1) == vs.group(1), va.group(1) if va else None)
        ok(b + ': denyut mengirim VERSI_APLIKASI (bukan teks versi yang ditulis tangan)', re.search(r'versi: VERSI_APLIKASI\b', teks[b]) and not re.search(r"versi: 'kasir-v\d+'", teks[b]))
        ok(b + ': memuat ulang diri saat versi baru mengambil alih (controllerchange) & menanyakan versi baru (reg.update)', "addEventListener('controllerchange'" in teks[b] and 'reg.update()' in teks[b])
        ok(b + ': tidak mengirim antrean tanpa masuk (403 tanpa kunci ≠ ditolak aturan)', "if (!sudahLogin()) { setStatus(navigator.onLine); return; }" in teks[b])
    ok('KP_VERSI_KASIR_25B (/baru/ daftar periksa) = VERSI sw-kasir.js', kp and vs and kp.group(1) == vs.group(1), kp.group(1) if kp else None)
    ok('sw-kasir.js mengunduh versi baru melewati cache HTTP peramban (cache: \'reload\')', "new Request(f, { cache: 'reload' })" in sw)
    return out


def baca_semua():
    return {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in (DARURAT, KASIR, 'sw-kasir.js', 'baru/js/data/kunci-periode.js')}


# ---------- /baru/ di jsc (KOTAK PASIR) ----------
JSC_SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 400) : '')); }
var __KINI = new Date('2026-09-26T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };
var kini = new Date(__KINI);
function hp(id, aplikasi, versi, pada, antrean, gagal_, nama) { return { id: id, nama: nama || '', aplikasi: aplikasi, versi: versi, pada: pada, antrean: antrean || 0, gagal: gagal_ || 0 }; }
pasok('perangkatStatus', [
  hp('d-baru', 'darurat', 'kasir-v26', '2026-09-26T02:50:00.000Z', 0, 0, 'Penjaga Contoh A'),
  hp('d-lama', 'darurat', 'kasir-v24', '2026-09-25T09:00:00.000Z', 0, 0, 'Penjaga Contoh B'),
  hp('d-tanpa', 'darurat', '', '2026-09-24T09:00:00.000Z', 0, 0, ''),
  hp('k-jauh', 'kasir', 'kasir-v25', '2026-09-15T09:00:00.000Z', 0, 0, 'Penjaga Contoh C'),
  hp('p-owner', 'baru', 'baru', '2026-09-26T02:55:00.000Z', 0, 0, 'Mac Contoh'),
  hp('d-tolak', 'darurat', 'kasir-v26', '2026-09-26T01:00:00.000Z', 0, 2, 'Penjaga Contoh D'),
  hp('d-antre', 'darurat', 'kasir-v26', '2026-09-26T01:30:00.000Z', 3, 0, 'Penjaga Contoh E')]);
var BERSIH = { lokal: { antreLokal: { belum: [], ditolak: [] }, antre: [] }, parkir: [], putusanHari: {}, centang: {}, siap25b: true };
var D = kpDaftarPeriksa('2026-08', kini, BERSIH); var b = D.butir.find(function (x) { return x.id === 'versiKasir'; });
ok('⛔ versi 25b ada, memblokir, dan kunci ditolak selama ada HP kasir versi lama', b && b.blokir && !b.ok && !D.boleh, J(b));
var r = b ? b.rincian.join(' | ') : '';
ok('⛔ versi 25b menyebut NAMA perangkat yang tertinggal & versinya (Penjaga Contoh B kasir-v24; d-tanpa "versi tidak dilaporkan")', /Penjaga Contoh B · kasir darurat · kasir-v24/.test(r) && /d-tanpa · kasir darurat · versi tidak dilaporkan/.test(r), r);
ok('⛔ versi 25b TIDAK menyebut yang sudah v26, sistem baru, atau yang tidak berdenyut 7 hari (kasir-v25 11 hari lalu)', !/Penjaga Contoh A|Mac Contoh|Penjaga Contoh C|Penjaga Contoh D|Penjaga Contoh E/.test(r) && b.rincian.length === 2, r);
pasok('perangkatStatus', cacheMentah('perangkat').map(function (p) { return Object.assign({}, p, p.aplikasi === 'baru' ? {} : { versi: 'kasir-v26' }); }));
var D2 = kpDaftarPeriksa('2026-08', kini, BERSIH); var b2 = D2.butir.find(function (x) { return x.id === 'versiKasir'; });
ok('semua HP kasir sudah kasir-v26 → butir versi beres', b2 && b2.ok, J(b2));
pasok('perangkatStatus', [hp('d-baru', 'darurat', 'kasir-v26', '2026-09-26T02:50:00.000Z', 0, 0, 'Penjaga Contoh A'), hp('d-lama', 'darurat', 'kasir-v24', '2026-09-25T09:00:00.000Z', 0, 0, 'Penjaga Contoh B'),
  hp('d-tolak', 'darurat', 'kasir-v26', '2026-09-26T01:00:00.000Z', 0, 2, 'Penjaga Contoh D'), hp('d-antre', 'darurat', 'kasir-v26', '2026-09-26T01:30:00.000Z', 3, 0, 'Penjaga Contoh E'),
  hp('k-jauh', 'kasir', 'kasir-v25', '2026-09-15T09:00:00.000Z', 0, 0, 'Penjaga Contoh C'), hp('p-owner', 'baru', 'baru', '2026-09-26T02:55:00.000Z', 0, 0, 'Mac Contoh')]);
var PH = kpPerhatianPerangkat(kini); var t = PH.map(function (x) { return x.teks; }).join(' | ');
ok('Perlu perhatian: HP dengan karcis DITOLAK disebut dengan jumlahnya (awas)', PH.some(function (x) { return /Penjaga Contoh D/.test(x.teks) && /2 DITOLAK server/.test(x.teks) && x.awas && x.nilai === '2 ditolak'; }), t);
ok('Perlu perhatian: HP dengan antrean disebut jumlah antreannya', PH.some(function (x) { return /Penjaga Contoh E/.test(x.teks) && /3 antre/.test(x.teks); }), t);
ok('Perlu perhatian: HP kasir versi lama (berdenyut 7 hari) disebut versinya', PH.some(function (x) { return /Penjaga Contoh B/.test(x.teks) && /masih kasir-v24, belum 25b/.test(x.teks) && x.awas; }), t);
ok('Perlu perhatian DIAM untuk HP yang beres, sistem baru, dan HP lama yang tidak berdenyut 7 hari tanpa antrean/ditolak', !/Penjaga Contoh A|Mac Contoh|Penjaga Contoh C/.test(t) && PH.length === 3, t);
ok('versi dibaca sebagai NOMOR: kasir-v100 ≥ kasir-v26, kasir-v9 < kasir-v26, teks lain = lama', kpVersiKasirCukup('kasir-v100') && !kpVersiKasirCukup('kasir-v9') && !kpVersiKasirCukup('baru') && !kpVersiKasirCukup(undefined));
print(J({ lulus: lulus, gagal: gagal }));
"""


def jalan_jsc(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return None, (r.stderr or r.stdout)[:1500]
    return json.loads(baris[-1]), ''


def bundel_jsc():
    import bundel_baru, uji_kunci_periode
    return uji_kunci_periode.satu_lingkup(bundel_baru.bundel(uji_kunci_periode.MODUL))


def periksa_baru(js):
    h, e = jalan_jsc(js + '\n' + JSC_SKENARIO)
    if h is None: return [('/baru/ · jsc jalan', False, e)]
    return [('/baru/ · ' + x, False, '') for x in h['gagal']] + [('/baru/ · kasus %d' % (i + 1), True, '') for i in range(h['lulus'])]


def cetak(hasil):
    lulus = [x for x in hasil if x[1]]; gagal = [x for x in hasil if not x[1]]
    for n, _, k in gagal: print('   ✗ ' + n + (' → ' + json.dumps(k, ensure_ascii=False)[:300] if k not in ('', None) else ''))
    return len(lulus), len(gagal)


def semua(ganti_berkas=None, ganti_jsc=None, gambar_dir=None, hanya=None):
    """ganti_berkas = {berkas: [(lama, baru)]} (kontrol). hanya = daftar bagian yang dijalankan ('statis', 'peramban', 'baru')."""
    ganti_berkas = ganti_berkas or {}; hanya = hanya or ['statis', 'peramban', 'baru']; hasil = []
    teks = baca_semua()
    for b, gs in ganti_berkas.items():
        for lama, baru in gs:
            assert lama in teks[b], 'kontrol basi: ' + b + ' · ' + lama[:70]; teks[b] = teks[b].replace(lama, baru)
    versi_sw = re.search(r"const VERSI = '([^']+)';", teks['sw-kasir.js']).group(1)
    if 'statis' in hanya: hasil += periksa_statis(teks)
    if 'peramban' in hanya:
        if not CHROME: hasil.append(('peramban · Google Chrome tersedia', False, 'tidak ditemukan'))
        else:
            dirusak = [b for b in (DARURAT, KASIR) if b in ganti_berkas]
            for b in (dirusak or [DARURAT, KASIR]):   # kontrol: hanya berkas yang dirusak yang dijalankan di peramban
                u, m = jalankan_berkas(b, ganti_berkas.get(b), gambar_dir if b == DARURAT else None)
                hasil += periksa_peramban(b, u, m, versi_sw)
    if 'baru' in hanya:
        js = bundel_jsc()
        for lama, baru in (ganti_jsc or []):
            assert lama in js, 'kontrol basi (jsc): ' + lama[:70]; js = js.replace(lama, baru)
        hasil += periksa_baru(js)
    return hasil


KONTROL = [
    # (nama, ganti per berkas, ganti jsc, bagian)
    ('penolakan aturan diperlakukan sebagai "belum masuk" (kasir darurat)', {DARURAT: [("if (status === 403) return adaToken ? 'ditolak-aturan' : 'masuk-ulang';", "if (status === 403) return 'masuk-ulang';")]}, None, ['peramban']),
    ('penolakan aturan diperlakukan sebagai "belum masuk" (kasir.html)', {KASIR: [("if (status === 403) return adaToken ? 'ditolak-aturan' : 'masuk-ulang';", "if (status === 403) return 'masuk-ulang';")]}, None, ['peramban']),
    ('karcis ditolak DIHAPUS (tidak ditulis ke daftar ditolak)', {DARURAT: [("    try { localStorage.setItem(K_GAGAL, JSON.stringify(d)); } catch (e) { return false; }\n  }\n  cabutDariAntrean(item);", "  }\n  cabutDariAntrean(item);")]}, None, ['peramban']),
    ('karcis ditolak dicoba ulang terus (403 = coba lagi) — antrean macet', {DARURAT: [("if (status === 403) return adaToken ? 'ditolak-aturan' : 'masuk-ulang';", "if (status === 403) return adaToken ? 'coba-lagi' : 'masuk-ulang';")]}, None, ['peramban']),
    ('429 (kuota habis) dianggap ditolak — karcis dibuang ke daftar ditolak', {DARURAT: [("if (status === 408 || status === 409 || status === 429 || !(status >= 400 && status < 500)) return 'coba-lagi';", "if (status === 408 || status === 409 || !(status >= 400 && status < 500)) return 'coba-lagi';")]}, None, ['peramban']),
    ('antrean dikirim tanpa masuk (403 tanpa kunci jadi "ditolak")', {KASIR: [("  if (!sudahLogin()) { setStatus(navigator.onLine); return; }\n  sedangKirim = true;", "  sedangKirim = true;"),
                                                                        ("      if (!(opsi.headers && opsi.headers.Authorization)) {\n        selesai(false); if (!sudahLogin()) tampilkanLayarLogin(true); return;\n      }\n", "")]}, None, ['peramban']),
    ('pita ditolak tidak digambar', {DARURAT: [("  el.style.display = 'block';\n}\nfunction barisDitolakHtml", "}\nfunction barisDitolakHtml")]}, None, ['peramban']),
    ('arsip "sudah dicatat ulang" satu ketukan', {DARURAT: [("  if (!yakinArsip) {\n    yakinArsip = true;", "  if (false) {\n    yakinArsip = true;")]}, None, ['peramban']),
    ('denyut masih versi tulis-tangan lama', {DARURAT: [("    versi: VERSI_APLIKASI\n", "    versi: 'kasir-v24'\n")]}, None, ['statis', 'peramban']),
    ('golonganJawaban kedua berkas tidak kembar lagi', {KASIR: [("if (status === 408 || status === 409 || status === 429 ||", "if (status === 408 || status === 429 ||")]}, None, ['statis']),
    ('sw-kasir.js naik tanpa kasir ikut (VERSI beda)', {'sw-kasir.js': [("const VERSI = 'kasir-v26';", "const VERSI = 'kasir-v27';")]}, None, ['statis']),
    ('service worker memakai cache HTTP lama', {'sw-kasir.js': [("c.addAll(FILES.map((f) => new Request(f, { cache: 'reload' })))", "c.addAll(FILES)")]}, None, ['statis']),
    ('/baru/: HP kasir versi lama tidak memblokir kunci', {}, [("tambah({ id: 'versiKasir', blokir: true, ok: !lamaV.length,", "tambah({ id: 'versiKasir', blokir: true, ok: true,")], ['baru']),
    ('/baru/: versi dibandingkan sebagai ada/tidak, bukan nomor', {}, [("const kpVersiKasirCukup = (v) => kpNomorVersiKasir(v) >= kpNomorVersiKasir(KP_VERSI_KASIR_25B);", "const kpVersiKasirCukup = (v) => !!v;")], ['baru']),
    ('/baru/: Perlu perhatian diam soal karcis ditolak', {}, [("if (tolak) bagian.push(tolak + ' DITOLAK server", "if (false) bagian.push(tolak + ' DITOLAK server")], ['baru']),
]


if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, gb, gj, bagian in KONTROL:
            try:
                h = semua(gb, gj, hanya=bagian); g = [x for x in h if not x[1]]
            except AssertionError as e:
                print('KONTROL BASI  ' + nama + ' · ' + str(e)); kode = 3; continue
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:110] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    gd = sys.argv[sys.argv.index('--gambar') + 1] if '--gambar' in sys.argv else None
    h = semua(gambar_dir=gd)
    l, g = cetak(h)
    print('ANTREAN KASIR (25b): %d lulus · %d gagal' % (l, g))
    if gd: print('tangkapan layar: ' + gd)
    sys.exit(1 if g else 0)
