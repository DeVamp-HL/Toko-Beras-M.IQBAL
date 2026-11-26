// HALAMAN CEK BON PELANGGAN (owner 26 Nov 2026, rules v23) — baru/bon.html. Skrip klasik tanpa impor (Chrome HP lama ikut jalan). Dijaga alat-uji/uji_ambil_bon.py.
// Alamat: bon.html#k=<kode 22 huruf>[&p=<proyek>]. Kode di bagian # (tidak terkirim ke server Pages). Satu GET REST Firestore ke bonPublik/<kode>; rules v23
// membolehkannya tanpa login hanya per kode (tidak bisa didaftar). Isi yang tampil = ringkasan yang ditulis HP/Mac owner: nama panggilan, sisa, nota belum lunas.
(function () {
  'use strict';
  var PROYEK_TOKO = 'toko-beras-m-iqbal';
  var KUNCI_API = 'AIzaSyAQ0DL-RnOa4gwSpvaNf1FMVlSNWla3RzA';   // kunci web publik proyek toko (sama dengan baru/js/data/firebase.js) — bukan rahasia
  var isi = document.getElementById('isi');
  function el(tag, kelas, teks) { var e = document.createElement(tag); if (kelas) e.className = kelas; if (teks !== undefined) e.textContent = teks; return e; }
  function rp(n) { var x = Math.round(Number(n) || 0); return 'Rp' + String(Math.abs(x)).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
  var BULAN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
  function tgl(iso) { var m = /^(\d{4})-(\d\d)-(\d\d)/.exec(String(iso || '')); return m ? Number(m[3]) + ' ' + BULAN[Number(m[2]) - 1] + ' ' + m[1] : '—'; }
  function jam(iso) { var d = new Date(iso || ''); if (isNaN(d)) return '—'; var z = function (n) { return (n < 10 ? '0' : '') + n; }; return d.getDate() + ' ' + BULAN[d.getMonth()] + ' ' + d.getFullYear() + ' ' + z(d.getHours()) + '.' + z(d.getMinutes()); }
  function kosongkan() { while (isi.firstChild) isi.removeChild(isi.firstChild); }
  function pesan(judul, teks) {
    kosongkan(); var k = el('div', 'kartu'); k.appendChild(el('div', 'toko', 'Toko Beras M.IQBAL')); k.appendChild(el('h1', '', judul)); k.appendChild(el('p', 'redup', teks)); isi.appendChild(k);
  }
  /** Nilai Firestore REST → nilai JS (string, angka, boolean, array, map). */
  function nilai(v) {
    if (!v || typeof v !== 'object') return null;
    if ('stringValue' in v) return v.stringValue; if ('integerValue' in v) return Number(v.integerValue); if ('doubleValue' in v) return Number(v.doubleValue);
    if ('booleanValue' in v) return v.booleanValue; if ('nullValue' in v) return null;
    if ('arrayValue' in v) return ((v.arrayValue || {}).values || []).map(nilai);
    if ('mapValue' in v) { var o = {}, f = (v.mapValue || {}).fields || {}; Object.keys(f).forEach(function (k) { o[k] = nilai(f[k]); }); return o; }
    return null;
  }
  function bacaHash() {
    var h = String(location.hash || '').replace(/^#/, ''); var o = {};
    h.split('&').forEach(function (p) { var i = p.indexOf('='); if (i > 0) o[p.slice(0, i)] = decodeURIComponent(p.slice(i + 1)); });
    return { kode: /^[A-Za-z0-9]{20,64}$/.test(o.k || '') ? o.k : '', proyek: /^[a-z0-9-]{4,40}$/.test(o.p || '') ? o.p : PROYEK_TOKO };
  }
  function tampil(d) {
    kosongkan();
    var k = el('div', 'kartu'); k.appendChild(el('div', 'toko', String(d.toko || 'Toko Beras M.IQBAL'))); k.appendChild(el('h1', '', 'Sisa bon ' + String(d.nama || '')));
    k.appendChild(el('div', 'angka' + (Number(d.sisa) > 0 ? '' : ''), rp(d.sisa)));
    k.appendChild(el('div', 'redup', 'Diperbarui ' + jam(d.diperbarui) + ' — pembayaran yang baru saja dicatat bisa belum masuk.'));
    isi.appendChild(k);
    var nota = Array.isArray(d.nota) ? d.nota : [];
    var n = el('div', 'kartu'); n.appendChild(el('div', 'toko', nota.length ? 'Nota yang belum lunas' : 'Tidak ada nota yang belum lunas'));
    var hari = new Date(); var iso = hari.getFullYear() + '-' + String(hari.getMonth() + 1).padStart(2, '0') + '-' + String(hari.getDate()).padStart(2, '0');
    nota.forEach(function (x) {
      var b = el('div', 'baris'); var kiri = el('div'); kiri.appendChild(el('div', '', tgl(x.tanggal) + (x.faktur ? ' · faktur ' + x.faktur : '')));
      if (x.jatuhTempo) kiri.appendChild(el('div', 'redup' + (String(x.jatuhTempo) < iso ? ' lewat' : ''), (String(x.jatuhTempo) < iso ? 'lewat jatuh tempo ' : 'jatuh tempo ') + tgl(x.jatuhTempo)));
      b.appendChild(kiri); b.appendChild(el('div', '', rp(x.sisa))); n.appendChild(b);
    });
    isi.appendChild(n);
    isi.appendChild(el('p', 'redup', 'Tautan ini khusus untuk Anda — jangan dibagikan. Pertanyaan soal bon: hubungi Toko Beras M.IQBAL.'));
  }
  window.addEventListener('hashchange', function () { location.reload(); });   // tautan lain dibuka di tab yang sama: cuma # yang berubah → baca ulang
  var H = bacaHash();
  if (!H.kode) { pesan('Tautan tidak lengkap', 'Buka lagi tautan dari Toko Beras M.IQBAL (pesan WhatsApp atau QR). Kodenya ada di ujung tautan.'); return; }
  var url = 'https://firestore.googleapis.com/v1/projects/' + H.proyek + '/databases/(default)/documents/bonPublik/' + encodeURIComponent(H.kode) + (H.proyek === PROYEK_TOKO ? '?key=' + KUNCI_API : '');
  fetch(url, { method: 'GET', credentials: 'omit', cache: 'no-store', referrerPolicy: 'no-referrer' }).then(function (r) {
    if (r.status === 404) { pesan('Tautan tidak berlaku', 'Tautan cek bon ini sudah dicabut toko atau salah ketik. Minta tautan baru ke Toko Beras M.IQBAL.'); return null; }
    if (!r.ok) { pesan('Belum bisa dibuka', 'Server menjawab ' + r.status + '. Coba lagi sebentar lagi.'); return null; }
    return r.json();
  }).then(function (j) { if (!j) return; var f = (j && j.fields) || {}; var d = {}; Object.keys(f).forEach(function (k) { d[k] = nilai(f[k]); }); tampil(d); })
    .catch(function () { pesan('Belum bisa dibuka', 'Periksa sambungan internet, lalu muat ulang halaman ini.'); });
})();
