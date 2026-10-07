// kasir_emulator.js — KODE ASLI kasir darurat (skrip sebaris kasir-darurat-nominal.html, versi berkas yang diberikan) dijalankan di luar peramban
// dengan DOM tiruan: muat halaman (kirimAntrean di akhir skripnya), lalu bila diminta simpanNominal — apa adanya, tanpa menyalin fungsinya.
// Dipakai alat-uji/uji_rules_emulator.py (bagian C: kirim ulang karcis kasir-v33 / kasir-v32 ke Firestore EMULATOR, hanya di runner GitHub).
// fetch = HOST.fetch: node di runner = Firestore EMULATOR (alamat & nama proyek ditulis ulang, isi kiriman tidak diubah); jsc di Mac = server palsu
// pencatat bentuk permintaan (tanpa jaringan) — pemeriksa statis --periksa memakai jalur itu.
// Skrip halaman memakai `var` & `function` di tingkat atas → dievaluasi dengan eval TIDAK langsung (kode global): nama-namanya jadi milik objek global.
var KASIR_UJI = (function () {
  'use strict';
  var G = (0, eval)('this');

  function elemenTiruan(id, simpan) {
    if (id && simpan[id]) return simpan[id];
    var dasar = {
      id: id || '', value: '', textContent: '', innerHTML: '', className: '', hidden: false, checked: false, disabled: false, style: {}, dataset: {}, children: [],
      classList: { add: function () {}, remove: function () {}, toggle: function () {}, contains: function () { return false; } },
      addEventListener: function () {}, removeEventListener: function () {}, appendChild: function (x) { return x; }, removeChild: function () {}, insertBefore: function () {},
      setAttribute: function () {}, getAttribute: function () { return null; }, removeAttribute: function () {}, focus: function () {}, blur: function () {}, click: function () {},
      scrollIntoView: function () {}, querySelector: function () { return elemenTiruan('', simpan); }, querySelectorAll: function () { return []; }, closest: function () { return null; },
      getBoundingClientRect: function () { return { top: 0, left: 0, width: 0, height: 0, right: 0, bottom: 0 }; }
    };
    // kolom/metode yang tidak dikenal = fungsi diam yang mengembalikan elemen tiruan lain (layar tidak dinilai di sini, hanya kiriman ke server)
    var p = new Proxy(dasar, {
      get: function (t, k) { if (k in t) return t[k]; if (typeof k === 'symbol') return undefined; return function () { return elemenTiruan('', simpan); }; },
      set: function (t, k, v) { t[k] = v; return true; }
    });
    if (id) simpan[id] = p;
    return p;
  }

  function pasang(H, simpanan, log, hitung) {
    var ls = {}; Object.keys(simpanan || {}).forEach(function (k) { ls[k] = String(simpanan[k]); });
    var el = {};
    var penyimpan = {
      getItem: function (k) { return Object.prototype.hasOwnProperty.call(ls, k) ? ls[k] : null; },
      setItem: function (k, v) { ls[k] = String(v); }, removeItem: function (k) { delete ls[k]; }, clear: function () { ls = {}; },
      key: function (i) { return Object.keys(ls)[i] || null; }, get length() { return Object.keys(ls).length; }
    };
    // node 21+ punya navigator / fetch bawaan di objek global: ditimpa (defineProperty), kalau ditolak lewat hapus dulu, terakhir penugasan biasa
    var tetap = function (nama, nilai) {
      try { Object.defineProperty(G, nama, { value: nilai, configurable: true, writable: true }); return; } catch (e) { /* lanjut */ }
      try { delete G[nama]; Object.defineProperty(G, nama, { value: nilai, configurable: true, writable: true }); return; } catch (e) { /* lanjut */ }
      G[nama] = nilai;
      if (G[nama] !== nilai) throw new Error('objek global ' + nama + ' tidak bisa diganti tiruan');
    };
    tetap('window', G);
    tetap('document', {
      getElementById: function (id) { return elemenTiruan(id, el); }, querySelector: function () { return elemenTiruan('', el); }, querySelectorAll: function () { return []; },
      createElement: function () { return elemenTiruan('', el); }, addEventListener: function () {}, removeEventListener: function () {}, hidden: false, visibilityState: 'visible',
      body: elemenTiruan('body', el), documentElement: elemenTiruan('html', el)
    });
    tetap('navigator', { onLine: true, userAgent: 'uji-emulator' });
    tetap('localStorage', penyimpan);
    tetap('location', { href: 'http://127.0.0.1/kasir-darurat-nominal.html', pathname: '/kasir-darurat-nominal.html', search: '', hash: '', reload: function () {}, replace: function () {} });
    // pewaktu halaman (denyut 5 menit, kirim ulang 25 dtk, pesan "tersimpan") TIDAK dijalankan — yang dinilai satu putaran kirim, bukan jam
    tetap('setInterval', function () { return 0; }); tetap('clearInterval', function () {});
    tetap('setTimeout', function () { return 0; }); tetap('clearTimeout', function () {});
    tetap('addEventListener', function () {}); tetap('removeEventListener', function () {});
    tetap('alert', function () {}); tetap('confirm', function () { return true; });
    tetap('matchMedia', function () { return { matches: false, addEventListener: function () {}, addListener: function () {} }; });
    tetap('requestAnimationFrame', function () { return 0; });
    tetap('fetch', function (url, opsi) {
      url = String(url); opsi = opsi || {}; hitung.masih += 1;
      var catat = { metode: String(opsi.method || 'GET').toUpperCase(), url: url, badan: typeof opsi.body === 'string' ? opsi.body : null, kunci: !!(opsi.headers && opsi.headers.Authorization) };
      log.push(catat);
      return H.fetch(url, opsi).then(function (r) { catat.status = r.status; hitung.masih -= 1; return r; },
        function (e) { catat.galat = String((e && e.message) || e); hitung.masih -= 1; throw e; });
    });
    return function () { return ls; };
  }

  async function diam(H, hitung) {
    // selesai = tidak ada fetch yang berjalan DAN antrean tidak sedang dikirim, 6 putaran berturut-turut (≥ 300 md di node)
    var tenang = 0;
    for (var i = 0; i < 1200 && tenang < 6; i++) {
      await H.tidur(50);
      tenang = (hitung.masih === 0 && !G.sedangKirim) ? tenang + 1 : 0;
    }
    return tenang >= 6;
  }

  return {
    jalankan: async function (H, skrip, simpanan, aksi) {
      var log = [], hitung = { masih: 0 }, galat = '';
      var isi = pasang(H, simpanan, log, hitung);
      var sesudahCatat = null, tuntasMuat = false, tuntas = false;
      try {
        (0, eval)(skrip);                                  // muat halaman: skrip tingkat atas berjalan (denyut, katalog, kirimAntrean(false))
        tuntasMuat = await diam(H, hitung);
        if (aksi && aksi.nota) {                           // satu pembeli: angka diketik lalu SIMPAN (simpanNominal memanggil kirimAntrean sendiri)
          G.barisItems = []; G.nominalDiketik = String(aksi.nota); G.bayarDAktif = 'Tunai';
          G.simpanNominal();
          sesudahCatat = JSON.parse(isi()['darurat_antrean_v1'] || '[]');
        }
        tuntas = await diam(H, hitung);
      } catch (e) { galat = String((e && (e.stack || e.message)) || e).slice(0, 1500); }
      var ls = isi();
      return { galat: galat, tuntasMuat: tuntasMuat, tuntas: tuntas, versi: typeof G.VERSI_APLIKASI === 'string' ? G.VERSI_APLIKASI : null, permintaan: log,
        antreanSesudahCatat: sesudahCatat, antrean: JSON.parse(ls['darurat_antrean_v1'] || '[]'), ditolak: JSON.parse(ls['darurat_gagal_v1'] || '[]'), simpanan: ls };
    }
  };
})();

// ---- HOST node (runner): node kasir_emulator.js <berkas permintaan JSON> → JSON hasil di stdout. Hanya Firestore EMULATOR yang boleh disentuh. ----
if (typeof process !== 'undefined' && process.versions && process.versions.node && typeof require === 'function' && require.main === module) {
  (async function () {
    var fs = require('fs');
    var M = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
    var asal = 'https://firestore.googleapis.com/v1/projects/' + M.proyekHalaman + '/';
    var tuju = 'http://' + M.emulator + '/v1/projects/' + M.proyekEmulator + '/';
    var fetchAsli = fetch;   // fetch bawaan node — disimpan sebelum diganti tiruan halaman
    var H = {
      tidur: function (ms) { return new Promise(function (r) { setTimeoutAsli(r, ms); }); },
      fetch: function (url, opsi) {
        if (url.indexOf(asal) !== 0) return Promise.reject(new Error('alamat di luar Firestore halaman (tidak dikirim ke mana pun): ' + url.slice(0, 80)));
        var o = Object.assign({}, opsi);
        if (typeof o.body === 'string') o.body = o.body.split('projects/' + M.proyekHalaman + '/').join('projects/' + M.proyekEmulator + '/');
        return fetchAsli(tuju + url.slice(asal.length), o);
      }
    };
    var setTimeoutAsli = setTimeout;
    var skrip = fs.readFileSync(M.skrip, 'utf8');
    var h = await KASIR_UJI.jalankan(H, skrip, M.simpanan, M.aksi);
    process.stdout.write(JSON.stringify(h) + '\n');
  })().catch(function (e) { process.stdout.write(JSON.stringify({ galat: String(e && e.stack || e) }) + '\n'); });
}
