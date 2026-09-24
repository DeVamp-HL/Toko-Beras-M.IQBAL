#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_layar_kunci.py — putaran 23c: TIRAI & GANTI ORANG, di PERAMBAN SUNGGUHAN (Chrome headless, profil baru tiap kali) atas SALINAN baru/ yang dilayani lokal.

BAGIAN 1 · TIRAI (Firebase sungguhan dari CDN): selama belum masuk, layar di belakang formulir Masuk KOSONG — satu angka rupiah pun tidak boleh ada di DOM,
  tidak ada kartu. Penyimpanan lokal peramban diisi dulu dengan angka CONTOH (titik kas, layar terakhir = Beranda) — persis jalan bocor yang pernah ada.
BAGIAN 2 · GANTI ORANG (Firebase PALSU lokal — impor gstatic di salinan firebase.js diarahkan ke /_palsu/, jadi firebase.js, akses.js & app.js yang asli
  yang bekerja; masuk-keluar digerakkan skrip uji tanpa sandi apa pun):
  owner mengisi keranjang (1 baris + 1 diparkir, nama pembeli contoh) → Keluar → ditanya "Keranjang berisi 2 baris belum disimpan — simpan atau kosongkan?"
  → Simpan dulu = tetap masuk, keranjang utuh → Keluar → Kosongkan → akun LAIN masuk → keranjang kosong, nama pembeli tidak terlihat.
  Juga: keluar dari tab lain (tanpa tombol) → keranjang dilupakan; akun yang sedang bekerja TANPA INTERNET lalu dinonaktifkan owner → tirai menutup:
  0 angka rupiah, <main> kosong, nama akun & status jaringan tidak terlihat.
BAGIAN 3 · JARINGAN: Firebase (CDN) gagal dimuat → dicoba ulang SATU kali → keluaran berkata GAGAL JARINGAN (bukan bukti tirai rusak), beda dari GAGAL UJI.

    python3 alat-uji/uji_layar_kunci.py            → LULUS / GAGAL UJI (keluar 2) / GAGAL JARINGAN (keluar 4)
    python3 alat-uji/uji_layar_kunci.py --kontrol  → kontrol wajib berbunyi (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, time, shutil, socket, subprocess, tempfile, threading, http.server, functools, urllib.request

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
CHROME = next((p for p in ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/usr/bin/google-chrome', '/usr/bin/chromium'] if os.path.exists(p)), None)
SDK = 'https://www.gstatic.com/firebasejs/10.13.0/'
# ANGKA CONTOH (bukan angka toko)
TITIK_KAS = {'tanggal': '2026-09-15', 'laci': 2000000, 'brankas': 10000000, 'rekening': 3000000, 'amplop': 1000000}
CADANGAN = {'versi': 5, 'diunduhPada': '2026-09-19T03:00:00.000Z',
            'penjualan': [{'id': 'c1', 'tanggal': '2026-09-19', 'jam': '09:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 50, 'hargaTotal': 690000, 'hppTotalSaatJual': 650000, 'trxId': 't1'}]}
RP = re.compile(r'Rp\s?\d')
JARINGAN, TIDAK_JALAN = 'jaringan', 'tidak-jalan'

# ---------- Firebase PALSU (bagian 2): permukaan SDK yang dipakai firebase.js, tanpa jaringan ----------
PALSU = {
    'firebase-app.js': "export function initializeApp(c) { return { options: c }; }\n",
    'firebase-auth.js': r"""
let dengar = null, pengguna = null;
export const browserLocalPersistence = {};
export function getAuth() { return { palsu: true }; }
export function setPersistence() { return Promise.resolve(); }
export function onAuthStateChanged(a, f) { dengar = f; setTimeout(() => f(pengguna), 0); return () => { dengar = null; }; }
export function signInWithEmailAndPassword() { return Promise.reject({ code: 'auth/uji-palsu' }); }
export function signOut() { pengguna = null; if (dengar) dengar(null); return Promise.resolve(); }
window.__ujiAuth = { masuk(email, uid) { pengguna = { email, uid }; if (dengar) dengar(pengguna); }, keluarDariTabLain() { pengguna = null; if (dengar) dengar(null); } };
""",
    'firebase-firestore.js': r"""
const akses = {}, pendengarAkses = {};
window.__ujiAkses = { setel(uid, data) { akses[uid] = data; (pendengarAkses[uid] || []).forEach((f) => f()); } };
const snapDok = (id, d) => ({ id, exists: () => !!d, data: () => d, metadata: { hasPendingWrites: false, fromCache: false } });
export function initializeFirestore() { return { palsu: true }; }
export const persistentLocalCache = () => ({}), persistentMultipleTabManager = () => ({});
export const collection = (db, nama) => ({ nama }), doc = (db, nama, id) => ({ nama, id: String(id) });
export const query = (c) => c, orderBy = () => ({}), limit = () => ({}), where = () => ({});
export function onSnapshot(ref, a, b, c) {
  const ok = typeof a === 'function' ? a : b; let hidup = true;
  const kirim = () => {
    if (!hidup) return;
    if (ref.id !== undefined) ok(snapDok(ref.id, ref.nama === 'aksesAkun' ? (akses[ref.id] || null) : null));
    else ok({ docs: [], size: 0, empty: true, forEach() {}, metadata: { fromCache: false, hasPendingWrites: false } });
  };
  if (ref.nama === 'aksesAkun') (pendengarAkses[ref.id] = pendengarAkses[ref.id] || []).push(kirim);
  setTimeout(kirim, 0);
  return () => { hidup = false; };
}
export function writeBatch() { return { set() {}, update() {}, delete() {}, commit: () => Promise.resolve() }; }
export const setDoc = () => Promise.resolve(), waitForPendingWrites = () => Promise.resolve();
export const getDocs = () => Promise.resolve({ docs: [], size: 0, empty: true, forEach() {} });
""",
}

# Skenario ganti orang — berjalan di halaman, hasilnya ditulis ke <pre id="__hasil"> lalu /_siap. ANGKA & NAMA CONTOH.
SKENARIO_GANTI = r"""<script>
(async function () {
  const tunggu = (ms) => new Promise((r) => setTimeout(r, ms));
  const sampai = async (f, ms) => { const t0 = Date.now(); while (Date.now() - t0 < (ms || 8000)) { try { if (f()) return true; } catch (e) { /* belum */ } await tunggu(40); } return false; };
  const B = document.body, $ = (id) => document.getElementById(id), hasil = { langkah: [] };
  const baris = (id, label, harga) => ({ id, trx: { jenis: 'karung', label, merkSumber: 'Contoh', jumlah: 1, satuan: 'karung', hargaSatuan: harga, hargaTotal: harga, totalKg: 50 } });
  const isiKeranjang = (nama) => window.__ujiJual.keadaan.setel({ keranjang: [baris(1, 'Beras Contoh 50 kg', 690000)], pelanggan: nama, aktifId: 1, idBerikut: 8,
    antrean: [{ id: 7, beku: { items: [baris(2, 'Beras Contoh Lain 25 kg', 345000)], pelanggan: nama + ' (parkir)', cara: 'Tunai', uang: 0, potongan: 0 } }] });
  const potret = () => { const c = B.cloneNode(true); c.querySelectorAll('script,#__hasil').forEach((e) => e.remove());
    const J = window.__ujiJual; const s = J.keadaan.baca();
    return { terkunci: B.classList.contains('terkunci'), baris: J.belumDisimpan().total, lembar: s.lembar || null, rpDom: (c.innerHTML.match(/Rp\s?\d/g) || []).length,
      mainKosong: [...document.querySelectorAll('main')].every((m) => !m.innerHTML.trim()), terlihat: B.innerText,
      tanya: $('modalKeranjang').classList.contains('tampil') ? $('judulKeranjang').textContent : '', masuk: !$('formMasuk').hidden && $('modalMasuk').classList.contains('tampil'),
      pilTerlihat: [...document.querySelectorAll('[data-pil-akun]')].some((e) => e.offsetParent !== null),
      lembarTerlihat: (() => { const l = $('lembarAkun'); if (!l) return false; const cs = getComputedStyle(l); return l.classList.contains('buka') && cs.display !== 'none' && cs.visibility !== 'hidden'; })() };
  };
  // pil akun di kepala layar yang tampil → lembar akun (Masuk sebagai + Keluar)
  const bukaPil = async () => { const p = [...document.querySelectorAll('[data-pil-akun]')].find((e) => e.offsetParent !== null); if (p) p.click(); await tunggu(120); };
  const keluarLewatPil = async () => { await bukaPil(); $('tombolKeluar').click(); };
  const catat = async (nama) => { await tunggu(250); hasil.langkah.push(Object.assign({ nama }, potret())); };
  const keJual = async () => { const n = document.querySelector('[data-tujuan="jual"]'); if (n) n.click(); await tunggu(150); };
  try {
    const akses = await import('./js/data/akses.js');
    await sampai(() => window.__ujiJual && window.__ujiAuth && window.__ujiAkses);
    window.__ujiAkses.setel('uid-b', { aktif: true, peran: 'karyawan', nama: 'Akun Uji B' });
    // 1 · owner masuk, keranjang diisi
    window.__ujiAuth.masuk(akses.EMAIL_OWNER, 'uid-owner'); await sampai(() => !B.classList.contains('terkunci')); await keJual();
    isiKeranjang('Pembeli Contoh A'); await catat('owner mengisi keranjang');
    // 2 · Keluar → ditanya → Simpan dulu
    await keluarLewatPil(); await sampai(() => $('modalKeranjang').classList.contains('tampil')); await catat('Keluar ditekan');
    $('keranjangSimpan').click(); await catat('Simpan dulu');
    // 3 · Keluar → Kosongkan
    await keluarLewatPil(); await sampai(() => $('modalKeranjang').classList.contains('tampil'));
    $('keranjangKosongkan').click(); await sampai(() => B.classList.contains('terkunci')); await catat('Kosongkan lalu keluar');
    // 4 · akun LAIN masuk
    window.__ujiAuth.masuk('b@uji.contoh', 'uid-b'); await sampai(() => !B.classList.contains('terkunci')); await keJual(); await catat('akun lain masuk');
    // 5 · akun B mengisi keranjang, keluar dari TAB LAIN (tanpa tombol) → owner masuk
    isiKeranjang('Pembeli Contoh B'); await tunggu(150);
    window.__ujiAuth.keluarDariTabLain(); await sampai(() => B.classList.contains('terkunci'));
    window.__ujiAuth.masuk(akses.EMAIL_OWNER, 'uid-owner'); await sampai(() => !B.classList.contains('terkunci')); await keJual(); await catat('keluar dari tab lain, owner masuk');
    // 6 · akun B bekerja TANPA INTERNET, lalu dinonaktifkan owner saat masih di layar
    window.__ujiAuth.keluarDariTabLain(); await sampai(() => B.classList.contains('terkunci'));
    window.__ujiAuth.masuk('b@uji.contoh', 'uid-b'); await sampai(() => !B.classList.contains('terkunci')); await keJual();
    isiKeranjang('Pembeli Contoh C'); window.dispatchEvent(new Event('offline')); await tunggu(150); await bukaPil(); await catat('akun B tanpa internet');   // lembar akun TERBUKA saat dinonaktifkan
    window.__ujiAkses.setel('uid-b', { aktif: false, peran: 'karyawan', nama: 'Akun Uji B' }); await sampai(() => B.classList.contains('terkunci')); await catat('akun B dinonaktifkan');
    // 7 · akun nonaktif keluar dari panel akun → owner masuk
    $('tombolKeluarAkun').click(); await sampai(() => !$('formMasuk').hidden);
    window.__ujiAuth.masuk(akses.EMAIL_OWNER, 'uid-owner'); await sampai(() => !B.classList.contains('terkunci')); await keJual(); await catat('nonaktif keluar, owner masuk');
  } catch (e) { hasil.galat = String(e && (e.stack || e.message) || e); }
  const pre = document.createElement('pre'); pre.id = '__hasil'; pre.hidden = true; pre.textContent = JSON.stringify(hasil); B.appendChild(pre);
  fetch('/_siap');
})();
</script>"""

POTONG_KALIMAT = 'Keranjang berisi 2 baris belum disimpan — simpan atau kosongkan?'
# teks yang tidak boleh TERLIHAT (innerText, huruf kecil) selama tirai menutup: nama akun, status jaringan & antrean, pil kepala
TERLARANG_TERKUNCI = ['akun uji b', 'tanpa internet', 'menunggu server', 'belum terkirim', 'memuat…']
TERLARANG_TERKUNCI_PERSIS = ['DATA TOKO', 'OWNER']   # pil kepala (huruf besar); panel akun nonaktif memuat "data toko"/"owner" huruf kecil — itu bukan pil


def siapkan(rusak=None, skenario='tirai'):
    """Salinan baru/ + berkas cadangan contoh. skenario 'tirai' = penyimpanan lokal diisi angka contoh; 'ganti' = Firebase palsu + skenario ganti orang.
    rusak = [(berkas, lama, baru)] — kontrol; 'lama' wajib ada (kontrol basi = gagal keras)."""
    d = tempfile.mkdtemp(prefix='kunci-'); shutil.copytree(os.path.join(AKAR, 'baru'), os.path.join(d, 'baru'))
    idx = os.path.join(d, 'baru', 'index.html'); t = open(idx, encoding='utf-8').read()
    isi = "<script>try{localStorage.setItem('miqbal_titik_kas_v1'," + json.dumps(json.dumps(TITIK_KAS)) + ");localStorage.setItem('miqbal_baru_tab','ringkasan');}catch(e){}</script>"
    # app.js gagal dimuat (mis. Firebase dari CDN tidak terjangkau) → elemen skrip modul menerima 'error' → server diberi tahu /_gagalmuat
    tag = '<script type="module" src="js/app.js"></script>'; assert tag in t, 'tag app.js berubah — perbarui uji'
    t = t.replace(tag, '<script type="module" src="js/app.js" onerror="fetch(\'/_gagalmuat?sdk=\'+encodeURIComponent(performance.getEntriesByType(\'resource\').map(function(e){return e.name;}).filter(function(n){return n.indexOf(\'firebasejs\')>=0;}).join(\' \')))"></script>', 1)
    if skenario == 'tirai':
        # penahan waktu: event load menunggu gambar /_tahan, yang baru dijawab server sesudah halaman mengabarkan /_siap (tirai tertutup ATAU ada isi di <main>) + jeda
        ekor = ("<img src='/_tahan' alt='' style='display:none'><script>var __t=setInterval(function(){if(document.body.classList.contains('terkunci')||document.querySelector('main *'))"
                "{clearInterval(__t);fetch('/_siap');}},150);</script>")
    else:
        ekor = "<img src='/_tahan' alt='' style='display:none'>" + SKENARIO_GANTI
        for nama, sumber in PALSU.items():
            os.makedirs(os.path.join(d, '_palsu'), exist_ok=True); open(os.path.join(d, '_palsu', nama), 'w', encoding='utf-8').write(sumber)
        fbp = os.path.join(d, 'baru', 'js', 'data', 'firebase.js'); s = open(fbp, encoding='utf-8').read()
        for nama in PALSU: assert SDK + nama in s, 'impor ' + nama + ' berubah — perbarui uji'; s = s.replace(SDK + nama, '/_palsu/' + nama)
        open(fbp, 'w', encoding='utf-8').write(s)
        ap = os.path.join(d, 'baru', 'js', 'app.js'); open(ap, 'a', encoding='utf-8').write('\nwindow.__ujiJual = layar;   // uji_layar_kunci: pegangan layar Jual (salinan uji saja)\n')
    assert '<head>' in t and '</body>' in t; open(idx, 'w', encoding='utf-8').write(t.replace('<head>', '<head>' + isi, 1).replace('</body>', ekor + '</body>', 1))
    json.dump(CADANGAN, open(os.path.join(d, 'cadangan-contoh.json'), 'w'))
    for berkas, lama, baru in (rusak or []):
        p = os.path.join(d, 'baru', berkas); s = open(p, encoding='utf-8').read(); assert lama in s, 'kontrol basi: ' + berkas + ' · ' + lama[:60]; open(p, 'w', encoding='utf-8').write(s.replace(lama, baru))
    return d


GIF = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'


class Diam(http.server.SimpleHTTPRequestHandler):
    siap = None; gagal = None; diminta = None; sdk = None   # per server: Event, Event, [jalur], [modul Firebase yang termuat menurut halaman]
    def log_message(self, *a): pass
    def do_GET(self):
        self.diminta.append(self.path.split('?')[0])
        if self.path.startswith('/_siap'):
            self.siap.set(); self.send_response(204); self.end_headers(); return
        if self.path.startswith('/_gagalmuat'):
            from urllib.parse import urlparse, parse_qs
            self.sdk.extend((parse_qs(urlparse(self.path).query).get('sdk') or [''])[0].split())
            self.gagal.set(); self.siap.set(); self.send_response(204); self.end_headers(); return
        if self.path.startswith('/_tahan'):
            self.siap.wait(40); time.sleep(2.5)   # aplikasi sudah jalan → beri waktu jawaban Firebase / cadangan tergambar
            self.send_response(200); self.send_header('Content-Type', 'image/gif'); self.end_headers(); self.wfile.write(GIF); return
        return super().do_GET()
    def end_headers(self):
        if self.path.endswith('.js'): self.send_header('Cache-Control', 'no-store')
        super().end_headers()
    def guess_type(self, path):
        return 'text/javascript' if str(path).endswith('.js') else super().guess_type(path)


def layani(d):
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    kelas = type('DiamRun', (Diam,), {'siap': threading.Event(), 'gagal': threading.Event(), 'diminta': [], 'sdk': []})
    # antrean sambungan LEBAR: bawaan socketserver cuma 5, Chrome membuka lebih banyak sekaligus → sambungan ditolak → modul lokal gagal dimuat secara acak
    # (dulu tampak sebagai "Chrome mencetak DOM sebelum app.js jalan")
    Srv = type('SrvUji', (http.server.ThreadingHTTPServer,), {'request_queue_size': 128, 'daemon_threads': True})
    srv = Srv(('127.0.0.1', port), functools.partial(kelas, directory=d)); threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def cdn_terjangkau():
    try:
        with urllib.request.urlopen(SDK + 'firebase-app.js', timeout=10) as r: return r.status == 200
    except Exception:
        return False


SDK_MODUL = ['firebase-app.js', 'firebase-firestore.js', 'firebase-auth.js']


def dom(d, jalur, coba=3, butuh_cdn=True):
    """→ (DOM yang SAH, None) atau ('', JARINGAN | TIDAK_JALAN). Sah = dicetak sesudah halaman mengabarkan /_siap.
    Aplikasi gagal dimuat (elemen skrip menerima 'error'): firebase.js sudah diminta tapi modul Firebase dari CDN tidak lengkap → JARINGAN, dicoba ulang SATU kali;
    modul LOKAL yang gagal (firebase.js belum sempat diminta / SDK lengkap) = GAGAL UJI, bukan jaringan."""
    gagal_jaringan = 0
    for _ in range(coba):
        h, siap, info = dom_sekali(d, jalur)
        if info['gagal']:
            sdk_lengkap = all(any(x.endswith(m) for x in info['sdk']) for m in SDK_MODUL)
            if butuh_cdn and info['firebase_diminta'] and not sdk_lengkap:
                gagal_jaringan += 1
                if gagal_jaringan >= 2: return '', JARINGAN
            continue
        if butuh_cdn and not siap and not cdn_terjangkau():
            gagal_jaringan += 1
            if gagal_jaringan >= 2: return '', JARINGAN
            continue
        if siap and '</html>' in h: return h, None
    return '', TIDAK_JALAN


def dom_sekali(d, jalur, tunggu=90):
    """DOM sesudah halaman dimuat. Chrome di macOS kadang tidak keluar sesudah mencetak DOM → dibaca sampai </html>, lalu dimatikan."""
    srv, port = layani(d); profil = tempfile.mkdtemp(prefix='kunci-profil-'); K = srv.RequestHandlerClass.func
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
        selesai.wait(tunggu)
        return ''.join(buf), K.siap.is_set() and not K.gagal.is_set(), {'gagal': K.gagal.is_set(), 'sdk': list(K.sdk), 'firebase_diminta': '/baru/js/data/firebase.js' in K.diminta}
    finally:
        p.kill(); p.wait(); srv.shutdown(); shutil.rmtree(profil, ignore_errors=True)


def body_kelas(h):
    m = re.search(r'<body[^>]*class="([^"]*)"', h); return m.group(1).split() if m else []


def isi_main(h):
    return ''.join(re.findall(r'<main\b[^>]*>(.*?)</main>', h, re.S))


def periksa_terkunci(h):
    """→ daftar cacat untuk halaman yang BELUM masuk (bagian 1)."""
    c = []
    if 'terkunci' not in body_kelas(h): c.append('body.terkunci tidak ada — aplikasi tidak jalan atau tirai tidak menutup (uji tidak sah)')
    if 'id="formMasuk"' not in h: c.append('formulir Masuk tidak ada')
    rp = RP.findall(h)
    if rp: c.append('%d angka rupiah di DOM sebelum masuk (mis. %s)' % (len(rp), ', '.join(sorted(set(re.findall(r'Rp\s?[\d.]+', h)))[:4])))
    m = isi_main(h)
    if re.search(r'class="[^"]*\bkartu\b', m): c.append('ada kartu di <main> sebelum masuk')
    if m.strip(): c.append('<main> tidak kosong (%d karakter)' % len(m.strip()))
    if 'data-pil-akun' in h: c.append('pil akun ada di DOM sebelum masuk')
    if re.search(r'class="lembar-akun[^"]*\bbuka\b', h): c.append('lembar akun terbuka sebelum masuk')
    return c


def periksa_ganti(h):
    """→ daftar cacat skenario ganti orang (bagian 2), dari <pre id="__hasil">. Tiap langkah punya KONTROL POSITIF di langkah sebelumnya (angka/nama terlihat)."""
    m = re.search(r'<pre id="__hasil"[^>]*>(.*?)</pre>', h, re.S)
    if not m: return ['skenario tidak menulis hasil — uji tidak sah']
    import html as H
    r = json.loads(H.unescape(m.group(1)))
    if r.get('galat'): return ['skenario berhenti: ' + r['galat'][:300]]
    L = {x['nama']: x for x in r['langkah']}; c = []
    def harus(langkah, syarat, kalimat):
        x = L.get(langkah)
        if x is None: c.append(langkah + ': langkah tidak tercapai'); return
        if not syarat(x): c.append(langkah + ': ' + kalimat)
    lihat = lambda x: x['terlihat'].lower()
    terlarang = lambda x: [t for t in TERLARANG_TERKUNCI if t in lihat(x)] + [t for t in TERLARANG_TERKUNCI_PERSIS if t in x['terlihat']]
    harus('owner mengisi keranjang', lambda x: x['baris'] == 2 and 'Pembeli Contoh A' in x['terlihat'] and x['rpDom'] > 0 and x['pilTerlihat'] and 'OWNER' in x['terlihat'], 'kontrol positif gagal — keranjang contoh / nama pembeli / angka rupiah / pil OWNER tidak terlihat (uji tidak bisa melihat)')
    harus('Keluar ditekan', lambda x: x['tanya'] == POTONG_KALIMAT, 'tidak ditanya "%s" (tampil: %r)' % (POTONG_KALIMAT, L.get('Keluar ditekan', {}).get('tanya')))
    harus('Simpan dulu', lambda x: not x['terkunci'] and x['baris'] == 2 and x['lembar'] == 'keranjang', 'Simpan dulu tidak membatalkan keluar / keranjang tidak utuh / keranjang tidak dibuka')
    harus('Kosongkan lalu keluar', lambda x: x['terkunci'] and x['baris'] == 0 and x['rpDom'] == 0 and x['mainKosong'] and not x['pilTerlihat'] and not x['lembarTerlihat'] and not terlarang(x), 'sesudah keluar: keranjang tidak kosong / ada angka rupiah / <main> tidak kosong / pil atau lembar akun masih terlihat %s' % terlarang(L.get('Kosongkan lalu keluar', {'terlihat': ''})))
    harus('akun lain masuk', lambda x: not x['terkunci'] and x['baris'] == 0 and 'pembeli contoh' not in lihat(x) and 'keranjang kosong' in lihat(x), 'akun berikutnya mewarisi keranjang / nama pembeli akun sebelumnya')
    harus('keluar dari tab lain, owner masuk', lambda x: not x['terkunci'] and x['baris'] == 0 and 'pembeli contoh b' not in lihat(x), 'keluar tanpa tombol (tab lain) — keranjang terbawa ke akun berikutnya')
    harus('akun B tanpa internet', lambda x: not x['terkunci'] and 'tanpa internet' in lihat(x) and 'akun uji b' in lihat(x) and x['rpDom'] > 0 and x['pilTerlihat'] and x['lembarTerlihat'], 'kontrol positif gagal — status jaringan / nama akun / angka / pil / lembar akun tidak terlihat saat bekerja (uji tidak bisa melihat)')
    harus('akun B dinonaktifkan', lambda x: x['terkunci'] and x['rpDom'] == 0 and x['mainKosong'] and not terlarang(x) and not x['pilTerlihat'] and not x['lembarTerlihat'],
          'tirai menutup tapi masih terlihat: %s' % terlarang(L.get('akun B dinonaktifkan', {'terlihat': ''})) + ' · rp %s · main kosong %s · pil %s · lembar %s' % tuple(L.get('akun B dinonaktifkan', {}).get(k) for k in ('rpDom', 'mainKosong', 'pilTerlihat', 'lembarTerlihat')))
    harus('nonaktif keluar, owner masuk', lambda x: not x['terkunci'] and x['baris'] == 0 and 'pembeli contoh c' not in lihat(x), 'akun nonaktif keluar — keranjangnya terbawa ke owner')
    return c


def jalankan(skenario, rusak=None, jalur='/baru/index.html'):
    """→ (cacat[], sebab) ; sebab = None | JARINGAN | TIDAK_JALAN."""
    d = siapkan(rusak, skenario)
    try:
        h, sebab = dom(d, jalur, butuh_cdn=(skenario == 'tirai'))
        if sebab: return [], sebab
        return (periksa_terkunci(h) if skenario == 'tirai' else periksa_ganti(h)), None
    finally: shutil.rmtree(d, ignore_errors=True)


KALIMAT_SEBAB = {JARINGAN: 'GAGAL JARINGAN: Firebase dari CDN (gstatic) tidak termuat, sudah dicoba ulang satu kali — ini BUKAN bukti tirai rusak; jalankan ulang saat jaringan normal',
                 TIDAK_JALAN: 'GAGAL UJI: aplikasi tidak jalan di peramban uji (3 kali) dan bukan karena Firebase dari CDN — uji tidak sah, bukan lulus'}

# kontrol: [(nama, skenario, rusak)]
KONTROL = [
    ('kontrol 2 · tirai dirusak (terkunci() selalu false)', 'tirai', [('js/inti/kunci.js', 'export const terkunci = () => _kunci;', 'export const terkunci = () => false;')]),
    ('kontrol 3 · beranda tanpa penjaga tirai', 'tirai', [('js/layar/ringkasan.js', "if (!tampil || terkunci()) return;\n    if (!$('rkHero')) bangun();", "if (!tampil) return;\n    if (!$('rkHero')) bangun();"),
                                                          ('js/app.js', "SEMUA_LAYAR().forEach((l) => l.tampilkan(false));\n  if (kunci) { Object.keys(LAYAR_ADA).forEach((k) => { LAYAR_ADA[k].innerHTML = ''; });", "if (kunci) {")]),
    ('kontrol 4 · keranjang tidak pernah dilupakan', 'ganti', [('js/layar/jual.js', 'lupakanOrang: () => K.setel((s) => L.keadaanOrangBerikutnya(s))', 'lupakanOrang: () => {}')]),
    ('kontrol 5 · keluar dari tab lain tidak dijaga', 'ganti', [('js/app.js', "if (!akun || akun.jenis === 'keluar') { layar.lupakanOrang(); uidKeranjang = ''; return; }", "if (!akun || akun.jenis === 'keluar') { uidKeranjang = ''; return; }")]),
    ('kontrol 6 · Keluar tanpa bertanya', 'ganti', [('js/app.js', "(await tanyaKeranjang(B)) !== 'kosongkan'", "false")]),
    ('kontrol 7 · pengosong lupa keranjang yang diparkir', 'ganti', [('js/layar/jual-logika.js', "const baru = Object.assign(keadaanAwal(), { sekarang: (s && s.sekarang) || null });", "const baru = Object.assign(keadaanAwal(), { sekarang: (s && s.sekarang) || null, antrean: (s && s.antrean) || [] });")]),
    # lembar akun (nama + status jaringan, di luar <main>) disembunyikan DUA penjaga (app.js menutupnya + aturan tirai di CSS) — kontrol merusak keduanya
    ('kontrol 8 · lembar akun tetap terbuka saat tirai menutup', 'ganti', [('js/app.js', "document.getElementById('lembarAkun').classList.remove('buka'); return; }", "return; }"),
                                                                        ('css/kerangka.css', 'body.terkunci main, body.terkunci .nav, body.terkunci .side, body.terkunci .lembar-akun { display: none !important; }', 'body.terkunci main, body.terkunci .nav, body.terkunci .side { display: none !important; }')]),
]


if __name__ == '__main__':
    if not CHROME:
        print('Chrome tidak ditemukan — uji peramban DILEWATI' + (' (CI: GAGAL)' if os.environ.get('CI') else ''))
        sys.exit(2 if os.environ.get('CI') else 0)
    if '--kontrol' in sys.argv:
        kode = 0
        d = siapkan()
        try:
            h, sebab = dom(d, '/baru/index.html?cadangan=/cadangan-contoh.json'); n = len(RP.findall(h))
            if sebab: print(KALIMAT_SEBAB[sebab]); sys.exit(4 if sebab == JARINGAN else 2)
            ok = n > 0 and 'terkunci' not in body_kelas(h)
            print(('BERBUNYI ' if ok else 'DIAM!!   ') + 'kontrol 1 · mode cadangan (terbuka): pembaca DOM melihat %d angka rupiah' % n); kode = kode if ok else 3
        finally: shutil.rmtree(d, ignore_errors=True)
        for nama, skenario, rusak in KONTROL:
            c, sebab = jalankan(skenario, rusak)
            if sebab: print(KALIMAT_SEBAB[sebab] + ' (' + nama + ')'); sys.exit(4 if sebab == JARINGAN else 2)
            print(('BERBUNYI ' if c else 'DIAM!!   ') + nama + ' → ' + (c[0][:150] if c else '-'))
            if not c: kode = 3
        # kontrol 9 · jaringan: Firebase tidak termuat → keluaran WAJIB berkata GAGAL JARINGAN, bukan lulus & bukan gagal uji
        c, sebab = jalankan('tirai', [('js/data/firebase.js', SDK + 'firebase-app.js', 'http://127.0.0.1:9/firebase-app.js')])
        ok = sebab == JARINGAN
        print(('BERBUNYI ' if ok else 'DIAM!!   ') + 'kontrol 9 · Firebase tidak termuat → ' + (KALIMAT_SEBAB.get(sebab, 'sebab: ' + str(sebab) + ' · cacat: ' + str(c[:1])))[:110]); kode = kode if ok else 3
        sys.exit(kode)
    kode = 0
    for skenario, judul in [('tirai', 'TIRAI'), ('ganti', 'GANTI ORANG')]:
        c, sebab = jalankan(skenario)
        if sebab: print(judul + ' · ' + KALIMAT_SEBAB[sebab]); kode = max(kode, 4 if sebab == JARINGAN else 2); continue
        if c: print(judul + ' GAGAL UJI:'); [print('   ✗ ' + x) for x in c]; kode = max(kode, 2); continue
        print({'tirai': 'TIRAI LULUS: sebelum masuk — formulir Masuk tampil, 0 angka rupiah, 0 kartu, semua <main> kosong (penyimpanan lokal berisi titik kas contoh)',
               'ganti': 'GANTI ORANG LULUS: Keluar (lewat pil) dengan keranjang berisi → ditanya; Simpan dulu = tetap masuk; Kosongkan → akun lain mulai dari keranjang kosong; '
                        'keluar dari tab lain & akun nonaktif juga melupakan keranjang; dinonaktifkan saat tanpa internet dengan lembar akun terbuka → 0 rupiah, pil OWNER/nama, lembar akun & status jaringan tidak terlihat'}[skenario])
    sys.exit(kode)
