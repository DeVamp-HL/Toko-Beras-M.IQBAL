// SALINAN APLIKASI /baru/ DI PERANGKAT — putaran T1 langkah 4 (owner 16 Nov 2026: tablet kasir bisa DIBUKA tanpa internet).
//
// Sebelum ini aplikasi tablet (APK) selalu mengambil /baru/ dari GitHub Pages: internet mati saat aplikasi dibuka = layar "belum tersambung".
// Catatan yang dibuat SAAT internet mati sudah aman sejak lama (cache tetap Firestore + antrean kirim) — yang belum bisa: MEMBUKA aplikasinya.
//
// Cara kerja:
//  · Yang memasang hanya aplikasi tablet (js/inti/salinan.js: asliAda) — HP & Mac owner tidak berubah. Perangkat yang sudah memakai salinan terus
//    memperbaruinya sendiri.
//  · Satu versi = satu terbitan (commit). Daftar berkas + sidik SHA-256 tiap berkas DICAP saat terbit (alat-uji/cap_sw_baru.py di job `terbitkan`),
//    bukan ditulis tangan — jadi tidak ada VERSI yang lupa dinaikkan (pelajaran sw-kasir.js).
//  · Pasang = SEMUA berkas versi itu diunduh lalu DICOCOKKAN sidiknya. Satu saja beda (mis. CDN Pages masih menyajikan berkas lama sesaat sesudah
//    terbit) = versi itu TIDAK dipasang; yang lama tetap dipakai dan dicoba lagi nanti. Tidak pernah ada salinan campuran dua versi.
//  · Berkas yang sidiknya sama dengan versi sebelumnya disalin dari salinan lama, tidak diunduh ulang.
//  · Selama salinan dipakai, halaman & modul SELALU dari salinan (versi utuh), baik ada internet maupun tidak. Versi baru diunduh di belakang
//    layar, lalu MENUNGGU; halaman yang memasangnya saat aman (layar "Siapa yang jaga?" / belum masuk, tanpa isian) lalu memuat ulang.
//  · Data toko (Firestore, Auth) TIDAK lewat sini — tetap jaringan biasa + cache Firestore di perangkat.
//  · Aplikasi tablet: Capacitor menyuntikkan script jembatan plugin (cetak USB) ke HTML yang diambilnya. Salinan menyimpan HTML BERSUNTIKAN itu
//    (jadi cetak tetap jalan saat dibuka tanpa internet); sidiknya dicocokkan sesudah suntikan itu dibuang (slBuangSuntikan).
//  · VERSI 'lepas' (darurat): salinan menghapus dirinya sendiri dan semua simpanannya.
//
// Lantai Chrome 80 (sama dengan /baru/). Diuji: alat-uji/uji_salinan_aplikasi.py (jsc + statis) & uji_salinan_peramban.py (Chrome sungguhan).
'use strict';

const VERSI = 'belum-dicap';   // CAP:VERSI
const TERBIT = '';   // CAP:TERBIT
const BERKAS = [];   // CAP:BERKAS
const LUAR = [];   // CAP:LUAR
const HURUF = '';   // CAP:HURUF

const AWALAN = 'baru-salinan-';
const NAMA = AWALAN + VERSI;
const NAMA_LUAR = 'baru-luar-v1';      // modul Firebase dari CDN: alamat berversi, isinya tidak pernah berubah
const NAMA_HURUF = 'baru-huruf-v1';    // Google Fonts: tampilan saja — gagal disimpan tidak menggagalkan pasang
const KUNCI_LENGKAP = '__salinan-lengkap__';

// ---------- fungsi murni (diuji di jsc) ----------
/** Jalur relatif terhadap folder salinan ('/x/baru/'): '/x/baru/js/a.js' → 'js/a.js', '/x/baru/' → '', '/x/icon.png' → '../icon.png', lain → null. */
function slRelatif(dasar, jalur) {
  if (typeof dasar !== 'string' || typeof jalur !== 'string' || dasar.slice(-1) !== '/') return null;
  if (jalur.indexOf(dasar) === 0) return jalur.slice(dasar.length);
  const induk = dasar.slice(0, dasar.slice(0, -1).lastIndexOf('/') + 1);
  if (induk && jalur.indexOf(induk) === 0 && jalur.slice(induk.length).indexOf('/') < 0) return '../' + jalur.slice(induk.length);
  return null;
}
/** Kunci simpanan satu berkas: alamat + sidik (berkas yang sama di versi berikutnya ditemukan lewat kunci ini). */
function slKunci(alamat, sidik) { return alamat + '?sidik=' + sidik; }
/** HTML dari Capacitor: script jembatan disisipkan tepat sesudah <head> ("\n<script type=\"text/javascript\">…</script>"). Dibuang untuk mencocokkan sidik. */
function slBuangSuntikan(html) {
  return String(html).replace(/<head>\n<script type="text\/javascript">[\s\S]*?<\/script>(?=\n)/, '<head>');
}
/** Alamat berkas huruf subset latin dari stylesheet Google Fonts (subset lain diambil saat diminta). */
function slHurufLatin(css) {
  const out = []; const re = /\/\* latin \*\/\s*@font-face\s*\{[^}]*?url\(([^)]+)\)/g; let m;
  while ((m = re.exec(String(css)))) { const u = m[1].replace(/^['"]|['"]$/g, ''); if (out.indexOf(u) < 0) out.push(u); }
  return out;
}
function slHex(buf) {
  const b = new Uint8Array(buf); let s = '';
  for (let i = 0; i < b.length; i++) s += (b[i] < 16 ? '0' : '') + b[i].toString(16);
  return s;
}
/** Jalankan f atas tiap butir, paling banyak n bersamaan; galat pertama menggagalkan semuanya. */
function slBerbatas(daftar, n, f) {
  let i = 0; let gagal = null;
  const pekerja = () => {
    if (gagal || i >= daftar.length) return Promise.resolve();
    const x = daftar[i++];
    return Promise.resolve().then(() => f(x)).then(pekerja, (e) => { gagal = gagal || e; throw e; });
  };
  const jalan = []; for (let k = 0; k < Math.min(n, daftar.length); k++) jalan.push(pekerja());
  return Promise.all(jalan).then(() => undefined);
}

// ---------- service worker ----------
if (typeof self !== 'undefined' && typeof self.addEventListener === 'function' && typeof caches !== 'undefined') {
  const DASAR = new URL('./', self.location.href);
  const PETA = new Map(BERKAS);
  const LUAR_ADA = new Set(LUAR);
  const alamatDari = (jalur) => new URL(jalur, DASAR).href;
  const jenisDari = (jalur) => (/\.html$/.test(jalur) ? 'text/html; charset=utf-8' : /\.css$/.test(jalur) ? 'text/css; charset=utf-8'
    : /\.js$/.test(jalur) ? 'text/javascript; charset=utf-8' : /\.png$/.test(jalur) ? 'image/png' : /\.svg$/.test(jalur) ? 'image/svg+xml' : 'application/octet-stream');
  const sidikDari = (isi) => crypto.subtle.digest('SHA-256', isi).then(slHex);
  const kabari = (pesan) => self.clients.matchAll({ includeUncontrolled: true, type: 'window' })
    .then((cs) => { cs.forEach((c) => { try { c.postMessage(Object.assign({ asal: 'salinan', versi: VERSI }, pesan)); } catch (e) { /* jendela sudah tutup */ } }); }, () => {});

  const simpanSatu = async (c, jalur, sidik) => {
    const alamat = alamatDari(jalur); const kunci = slKunci(alamat, sidik);
    if (await c.match(kunci)) return;   // pasang yang diulang
    const html = /\.html$/.test(jalur);
    // HTML selalu diambil baru: di aplikasi tablet isinya membawa script jembatan Capacitor milik APK yang sedang terpasang
    if (!html) { const lama = await caches.match(kunci); if (lama) { await c.put(kunci, lama); return; } }
    const r = await fetch(new Request(alamat, { cache: 'reload', credentials: 'same-origin', headers: html ? { Accept: 'text/html' } : {} }));
    if (!r.ok) throw new Error(jalur + ': server menjawab ' + r.status);
    const isi = await r.arrayBuffer();
    const dicek = html ? new TextEncoder().encode(slBuangSuntikan(new TextDecoder().decode(isi))) : isi;
    if ((await sidikDari(dicek)) !== sidik) throw new Error(jalur + ': isinya bukan versi ini (sidik beda)');
    // HTML: charset ditulis tegas — di aplikasi tablet script jembatan mendorong <meta charset> jauh melewati 1.024 bait pertama
    await c.put(kunci, new Response(isi, { headers: { 'Content-Type': html ? jenisDari(jalur) : (r.headers.get('Content-Type') || jenisDari(jalur)) } }));
  };
  const simpanLuar = async () => {
    const c = await caches.open(NAMA_LUAR);
    await slBerbatas(LUAR, 3, async (u) => {
      if (await c.match(u, { ignoreVary: true })) return;
      const r = await fetch(u, { mode: 'cors', credentials: 'omit' });
      if (!r.ok) throw new Error(u + ': server menjawab ' + r.status);
      await c.put(u, r);
    });
  };
  const simpanHuruf = async () => {
    if (!HURUF) return;
    const c = await caches.open(NAMA_HURUF);
    const r = await fetch(HURUF, { mode: 'cors', credentials: 'omit' }); if (!r.ok) return;
    const css = await r.clone().text(); await c.put(HURUF, r);
    await slBerbatas(slHurufLatin(css), 4, async (u) => {
      if (await c.match(u, { ignoreVary: true })) return;
      const f = await fetch(u, { mode: 'cors', credentials: 'omit' }); if (f.ok) await c.put(u, f);
    });
  };
  const pasang = async () => {
    if (VERSI === 'lepas') { await self.skipWaiting(); return; }
    if (!BERKAS.length) throw new Error('salinan belum dicap (bukan terbitan)');
    await kabari({ jenis: 'memasang', n: BERKAS.length });
    const c = await caches.open(NAMA);
    await slBerbatas(BERKAS, 6, (b) => simpanSatu(c, b[0], b[1]));
    await simpanLuar();
    try { await simpanHuruf(); } catch (e) { /* huruf cadangan peramban dipakai */ }
    await c.put(KUNCI_LENGKAP, new Response(JSON.stringify({ versi: VERSI, terbit: TERBIT, n: BERKAS.length })));
    await kabari({ jenis: 'terpasang' });
  };
  self.addEventListener('install', (e) => {
    e.waitUntil(pasang().catch((x) => {
      const sebab = String((x && x.message) || x);
      return kabari({ jenis: 'gagal', sebab }).then(() => { throw x; });   // pasang gagal → versi lama tetap; dicoba lagi saat pemeriksaan berikutnya
    }));
  });
  self.addEventListener('activate', (e) => {
    e.waitUntil((async () => {
      const ks = await caches.keys();
      if (VERSI === 'lepas') {
        await Promise.all(ks.filter((k) => k.indexOf(AWALAN) === 0 || k === NAMA_LUAR || k === NAMA_HURUF).map((k) => caches.delete(k)));
        await self.registration.unregister();
        const cs = await self.clients.matchAll({ type: 'window' }); cs.forEach((c) => { try { c.navigate(c.url); } catch (x) { /* biarkan */ } });
        return;
      }
      await Promise.all(ks.filter((k) => k.indexOf(AWALAN) === 0 && k !== NAMA).map((k) => caches.delete(k)));
      // modul CDN yang tidak dipakai versi ini dibuang SEKARANG (bukan saat pasang: versi lama yang masih dipakai tetap bisa dibuka tanpa internet)
      const cl = await caches.open(NAMA_LUAR); const lama = await cl.keys();
      await Promise.all(lama.filter((k) => !LUAR_ADA.has(k.url)).map((k) => cl.delete(k)));
      await self.clients.claim();
    })());
  });
  self.addEventListener('message', (e) => {
    const d = e.data || {};
    if (d.jenis === 'aktifkan') { self.skipWaiting(); return; }
    if (d.jenis === 'versi' && e.ports && e.ports[0]) {
      caches.open(NAMA).then((c) => c.match(KUNCI_LENGKAP)).then((r) => !!r, () => false)
        .then((lengkap) => { e.ports[0].postMessage({ versi: VERSI, terbit: TERBIT, n: BERKAS.length, lengkap }); });
    }
  });
  const dariSalinan = async (kunci, r) => {
    const c = await caches.open(NAMA); const ada = await c.match(kunci);
    return ada || fetch(r);
  };
  const dariLuar = async (r, u) => {
    const c = await caches.open(NAMA_LUAR); const ada = await c.match(u, { ignoreVary: true });
    if (ada) return ada;
    const net = await fetch(r); if (net.ok && net.type === 'cors') c.put(u, net.clone()); return net;
  };
  const dariHuruf = async (r) => {
    const c = await caches.open(NAMA_HURUF); const ada = await c.match(r.url, { ignoreVary: true });
    if (ada) return ada;
    const net = await fetch(r); if (net.ok || net.type === 'opaque') c.put(r.url, net.clone()); return net;
  };
  self.addEventListener('fetch', (e) => {
    const r = e.request; if (r.method !== 'GET' || VERSI === 'lepas') return;
    let u; try { u = new URL(r.url); } catch (x) { return; }
    if (u.origin === self.location.origin) {
      let rel = slRelatif(DASAR.pathname, u.pathname); if (rel === null) return;
      if (rel === '') rel = 'index.html';
      const sidik = PETA.get(rel); if (!sidik) return;   // bukan berkas salinan → jaringan biasa
      e.respondWith(dariSalinan(slKunci(alamatDari(rel), sidik), r));
      return;
    }
    if (LUAR_ADA.has(u.href)) { e.respondWith(dariLuar(r, u.href)); return; }
    if (u.host === 'fonts.googleapis.com' || u.host === 'fonts.gstatic.com') e.respondWith(dariHuruf(r));
  });
}
