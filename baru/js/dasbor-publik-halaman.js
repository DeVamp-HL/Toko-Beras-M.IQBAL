// HALAMAN TAUTAN BEKU DASBOR (paket P8, owner 27 Nov 2026, rules v26) — baru/dasbor-publik.html. Skrip klasik tanpa impor (HP lama ikut jalan). Dijaga alat-uji/uji_arsip_audit_p8.py.
// Alamat: dasbor-publik.html#k=<kode 22 huruf>[&p=<proyek>]. Kode di bagian # (tidak terkirim ke server Pages). Satu GET REST Firestore ke dasborPublik/<kode>; rules v26
// membolehkannya tanpa login hanya per kode (tidak bisa didaftar) dan hanya SELAMA jam server belum lewat `sampai` — sesudahnya server menolak (403), dicabut = tidak ada.
// Yang tampil = angka yang DIBEKUKAN owner (bagian yang dicentang): tidak pernah diperbarui, jam bekunya disebut. Tanpa nama orang, tanpa penyimpanan, tanpa tautan keluar.
(function () {
  'use strict';
  var PROYEK_TOKO = 'toko-beras-m-iqbal';
  var KUNCI_API = 'AIzaSyAQ0DL-RnOa4gwSpvaNf1FMVlSNWla3RzA';   // kunci web publik proyek toko (sama dengan baru/js/data/firebase.js) — bukan rahasia
  var isi = document.getElementById('isi');
  function el(tag, kelas, teks) { var e = document.createElement(tag); if (kelas) e.className = kelas; if (teks !== undefined) e.textContent = teks; return e; }
  function rp(n) { if (n === null || n === undefined || !isFinite(Number(n))) return '—'; var x = Math.round(Number(n)); return (x < 0 ? '−' : '') + 'Rp' + String(Math.abs(x)).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  function angka(n, sat) { if (n === null || n === undefined || !isFinite(Number(n))) return '—'; var s = String(Math.round(Number(n) * 10) / 10).split('.'); return s[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.') + (s[1] ? ',' + s[1] : '') + (sat || ''); }
  var BULAN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
  function jam(v) { var d = new Date(v || ''); if (isNaN(d)) return '—'; var z = function (n) { return (n < 10 ? '0' : '') + n; }; return d.getDate() + ' ' + BULAN[d.getMonth()] + ' ' + d.getFullYear() + ' ' + z(d.getHours()) + '.' + z(d.getMinutes()); }
  function tgl(iso) { var m = /^(\d{4})-(\d\d)-(\d\d)/.exec(String(iso || '')); return m ? Number(m[3]) + ' ' + BULAN[Number(m[2]) - 1] : ''; }
  function kosongkan() { while (isi.firstChild) isi.removeChild(isi.firstChild); }
  function pesan(judul, teks) {
    kosongkan(); var k = el('div', 'kartu'); k.appendChild(el('div', 'toko', 'Toko Beras M.IQBAL')); k.appendChild(el('h1', '', judul)); k.appendChild(el('p', 'redup', teks)); isi.appendChild(k);
  }
  /** Nilai Firestore REST → nilai JS (string, angka, boolean, jam, array, map). */
  function nilai(v) {
    if (!v || typeof v !== 'object') return null;
    if ('stringValue' in v) return v.stringValue; if ('integerValue' in v) return Number(v.integerValue); if ('doubleValue' in v) return Number(v.doubleValue);
    if ('booleanValue' in v) return v.booleanValue; if ('nullValue' in v) return null; if ('timestampValue' in v) return v.timestampValue;
    if ('arrayValue' in v) return ((v.arrayValue || {}).values || []).map(nilai);
    if ('mapValue' in v) { var o = {}, f = (v.mapValue || {}).fields || {}; Object.keys(f).forEach(function (k) { o[k] = nilai(f[k]); }); return o; }
    return null;
  }
  function bacaHash() {
    var h = String(location.hash || '').replace(/^#/, ''); var o = {};
    h.split('&').forEach(function (p) { var i = p.indexOf('='); if (i > 0) o[p.slice(0, i)] = decodeURIComponent(p.slice(i + 1)); });
    return { kode: /^[A-Za-z0-9]{20,64}$/.test(o.k || '') ? o.k : '', proyek: /^[a-z0-9-]{4,40}$/.test(o.p || '') ? o.p : PROYEK_TOKO };
  }
  function baris(kartu, kiri, kanan, kelas) { var b = el('div', 'baris'); b.appendChild(el('div', '', kiri)); b.appendChild(el('div', 'kanan' + (kelas ? ' ' + kelas : ''), kanan)); kartu.appendChild(b); }
  function tampil(d) {
    kosongkan(); var bagian = Array.isArray(d.bagian) ? d.bagian : []; var ada = function (id) { return bagian.indexOf(id) >= 0; };
    var k = el('div', 'kartu'); k.appendChild(el('div', 'toko', String(d.toko || 'Toko Beras M.IQBAL'))); k.appendChild(el('h1', '', 'Ringkasan toko' + (d.untuk ? ' · untuk ' + String(d.untuk) : '')));
    k.appendChild(el('p', 'redup', 'Angka DIBEKUKAN ' + jam(d.dibuat) + ' — tidak ikut berubah sesudahnya. Tautan berlaku sampai ' + jam(d.sampai) + '.'));
    isi.appendChild(k);
    (Array.isArray(d.bulan) ? d.bulan : []).forEach(function (b) {
      if (!b) return; var c = el('div', 'kartu'); c.appendChild(el('h2', '', String(b.nama || '') + (b.berjalan ? ' · sampai ' + tgl(b.sampaiTanggal) : '')));
      if (ada('omzet')) { if (b.omzetGalat) baris(c, 'Omzet', 'belum bisa dihitung', 'awas'); else { baris(c, 'Omzet', rp(b.omzet)); baris(c, 'Jumlah nota', angka(b.nota)); } }
      if (ada('kg')) baris(c, 'Beras terjual', b.kgGalat ? 'belum bisa dihitung' : angka(b.kg, ' kg'), b.kgGalat ? 'awas' : '');
      if (ada('laba')) { if (b.labaGalat) baris(c, 'Laba kotor', 'belum bisa dihitung', 'awas'); else { baris(c, 'Laba kotor', rp(b.labaKotor)); baris(c, 'Margin laba kotor', b.marginPct === null || b.marginPct === undefined ? '—' : angka(b.marginPct, ' %')); } }
      if (ada('bersih')) baris(c, 'Laba bersih', b.bersihGalat ? 'belum bisa dihitung' : rp(b.labaBersih), b.bersihGalat ? 'awas' : '');
      isi.appendChild(c);
    });
    if (ada('stok') || ada('piutang') || ada('utang') || ada('kas')) {
      var s = el('div', 'kartu'); s.appendChild(el('h2', '', 'Posisi saat dibekukan'));
      if (ada('stok') && d.stok) { baris(s, 'Stok beras', angka(d.stok.kg, ' kg')); baris(s, 'Nilai modal stok', rp(d.stok.nilai)); }
      if (ada('piutang')) baris(s, 'Total piutang pelanggan', rp(d.piutang));
      if (ada('utang')) baris(s, 'Total utang ke pemasok', rp(d.utangPemasok));
      if (ada('kas') && d.kas) { if (d.kas.ada) { baris(s, 'Kas & rekening', rp(d.kas.total)); baris(s, '· laci', rp(d.kas.laci)); baris(s, '· brankas', rp(d.kas.brankas)); baris(s, '· rekening', rp(d.kas.rekening)); } else baris(s, 'Kas & rekening', 'belum ada hitungan kas', 'awas'); }
      isi.appendChild(s);
    }
    isi.appendChild(el('p', 'redup', 'Ringkasan ini dibagikan Toko Beras M.IQBAL untuk dibaca pemegang tautan saja. Angka bisa berbeda dengan laporan resmi sesudah tutup buku.'));
  }
  window.addEventListener('hashchange', function () { location.reload(); });
  var H = bacaHash();
  if (!H.kode) { pesan('Tautan tidak lengkap', 'Buka lagi tautan dari Toko Beras M.IQBAL. Kodenya ada di ujung tautan.'); return; }
  var url = 'https://firestore.googleapis.com/v1/projects/' + H.proyek + '/databases/(default)/documents/dasborPublik/' + encodeURIComponent(H.kode) + (H.proyek === PROYEK_TOKO ? '?key=' + KUNCI_API : '');
  fetch(url, { method: 'GET', credentials: 'omit', cache: 'no-store', referrerPolicy: 'no-referrer' }).then(function (r) {
    if (r.status === 403 || r.status === 404) { pesan('Tautan tidak berlaku', 'Tautan ini sudah lewat masa berlakunya atau dicabut toko. Minta tautan baru ke Toko Beras M.IQBAL.'); return null; }
    if (!r.ok) { pesan('Belum bisa dibuka', 'Server menjawab ' + r.status + '. Coba lagi sebentar lagi.'); return null; }
    return r.json();
  }).then(function (j) { if (!j) return; var f = (j && j.fields) || {}; var d = {}; Object.keys(f).forEach(function (k) { d[k] = nilai(f[k]); }); tampil(d); })
    .catch(function () { pesan('Belum bisa dibuka', 'Periksa sambungan internet, lalu muat ulang halaman ini.'); });
})();
