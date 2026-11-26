// TARIK HARGA ACUAN BERAS (paket Banding pemasok, owner 26 Nov 2026: "Ketik manual + coba tarik otomatis"). Murni: tanpa Firebase, tanpa jaringan — diuji di
// jsc oleh alat-uji/uji_banding_pemasok.py. Dipakai functions/index.js (tarikAcuan, terjadwal tiap Jumat pagi WIB).
//
// JUJUR SOAL BATASNYA: alamat & parameter di bawah dibaca dari kode halaman publik Panel Harga Bapanas (panelharga.badanpangan.go.id, berkas main.js:
// apiURL + "/front/harga-pangan-informasi", GET tanpa login). Bentuk JAWABANNYA belum pernah terlihat — server itu tidak menjawab dari jaringan pengembang.
// Karena itu pembacanya MENYISIR seluruh JSON: objek yang namanya "beras premium" / "beras medium" dan punya angka harga 1.000–100.000 per kg. Tingkat harga
// (produsen / grosir / eceran) = TEBAKAN dari parameter level_harga_id yang diminta — ditandai `tebakTingkat`, owner memeriksa sebelum menekan Pakai.
// Hasil yang tidak dikenali = status 'gagal' + potongan jawaban (data publik) supaya bisa dibetulkan, BUKAN angka karangan.
'use strict';

const ACUAN_SUMBER = 'Panel Harga Bapanas';
const ACUAN_ALAMAT = 'https://api-panelhargav2.badanpangan.go.id/api/front/harga-pangan-informasi';
const ACUAN_LEVEL = [{ id: 3, tingkat: 'eceran' }, { id: 1, tingkat: 'produsen' }];   // TEBAKAN arti level_harga_id (belum terlihat dari sini)
const ACUAN_MAKS = 12;
const HARGA_MIN = 1000, HARGA_MAKS = 100000;

const bersih = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const KUNCI_NAMA = /^(nama|name|komoditas|commodity|nama_komoditas|komoditas_nama|label|title)$/i;
const KUNCI_HARGA = /(harga|price|rata|today|geomean|nilai|value)/i;
const KUNCI_TANGGAL = /(tanggal|date|periode|period)/i;
const KUNCI_WILAYAH = /(provinsi|province|wilayah|region|kota|city)/i;
/** '2026-11-27', '27/11/2026', '27-11-2026' → '2026-11-27'; selain itu ''. */
function isoDari(v) {
  const t = bersih(v); let m = /^(\d{4})-(\d{2})-(\d{2})/.exec(t); if (m) return m[1] + '-' + m[2] + '-' + m[3];
  m = /^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$/.exec(t); if (m) return m[3] + '-' + String(m[2]).padStart(2, '0') + '-' + String(m[1]).padStart(2, '0');
  return '';
}
/** Angka harga dari nilai mentah: 13100 / "13100" / "13.100" / "Rp 13.100" / 13100.45 → rupiah bulat; di luar 1.000–100.000 → null. */
function angkaHarga(v) {
  if (typeof v === 'number') { const n = Math.round(v); return n >= HARGA_MIN && n <= HARGA_MAKS ? n : null; }
  const t = bersih(v).replace(/rp/i, '').replace(/\s/g, ''); if (!t) return null;
  const n = /^\d{1,3}(\.\d{3})+(,\d+)?$/.test(t) ? Number(t.replace(/\./g, '').replace(',', '.')) : /^\d+([.,]\d+)?$/.test(t) ? Number(t.replace(',', '.')) : NaN;
  const b = Math.round(n); return isFinite(n) && b >= HARGA_MIN && b <= HARGA_MAKS ? b : null;
}
/**
 * Sisir satu jawaban JSON → [{ nama, mutu, tingkat, tebakTingkat, hargaPerKg, tanggal, wilayah }] (paling banyak ACUAN_MAKS, satu per mutu × wilayah).
 * tingkat = tingkat yang diminta (tebakan); tanggalCadangan = tanggal tarik (WIB) bila jawaban tidak menyebut tanggal.
 */
function sisirHarga(json, tingkat, tanggalCadangan) {
  const out = []; const ada = {}; let langkah = 0;
  const jalan = (o, wilayahInduk) => {
    if (langkah++ > 20000 || out.length >= ACUAN_MAKS || o === null || typeof o !== 'object') return;
    if (Array.isArray(o)) { o.forEach((x) => jalan(x, wilayahInduk)); return; }
    const kunci = Object.keys(o); let nama = '', harga = null, tanggal = '', wilayah = wilayahInduk;
    kunci.forEach((k) => { const v = o[k];
      if (!nama && KUNCI_NAMA.test(k) && typeof v === 'string') nama = bersih(v);
      if (!tanggal && KUNCI_TANGGAL.test(k) && (typeof v === 'string')) tanggal = isoDari(v);
      if (KUNCI_WILAYAH.test(k) && typeof v === 'string' && bersih(v)) wilayah = bersih(v).slice(0, 60); });
    const m = /beras\s+(premium|medium)/i.exec(nama);
    if (m && !/sphp|bulog/i.test(nama)) { kunci.forEach((k) => { if (harga === null && KUNCI_HARGA.test(k) && !KUNCI_TANGGAL.test(k)) harga = angkaHarga(o[k]); });
      const mutu = m[1].toLowerCase(); const w = wilayah || 'nasional'; const id = mutu + '|' + w.toLowerCase();
      if (harga !== null && !ada[id]) { ada[id] = true; out.push({ nama: nama.slice(0, 60), mutu, tingkat, tebakTingkat: true, hargaPerKg: harga, tanggal: tanggal || tanggalCadangan, wilayah: w }); } }
    kunci.forEach((k) => { const v = o[k]; if (v && typeof v === 'object') jalan(v, wilayah); });
  };
  jalan(json, '');
  return out;
}
/** Dokumen aturanToko/acuanTarik dari hasil tiap permintaan [{ tingkat, json | galat }]. */
function dokTarik(hasil, kini) {
  const pada = (kini || new Date()).toISOString(); const tanggal = new Date((kini || new Date()).getTime() + 7 * 3600000).toISOString().slice(0, 10);   // tanggal WIB
  const harga = []; const pesan = []; let contoh = '';
  (hasil || []).forEach((h) => { if (h.galat) { pesan.push(h.tingkat + ': ' + bersih(h.galat).slice(0, 120)); return; }
    const x = sisirHarga(h.json, h.tingkat, tanggal); if (!x.length) { pesan.push(h.tingkat + ': jawaban tidak memuat harga beras premium / medium yang dikenali'); if (!contoh) contoh = bersih(JSON.stringify(h.json)).slice(0, 400); }
    x.forEach((y) => { if (harga.length < ACUAN_MAKS) harga.push(y); }); });
  return { id: 'acuanTarik', pada, tanggal, sumber: ACUAN_SUMBER, alamat: ACUAN_ALAMAT, status: harga.length ? 'ok' : 'gagal', pesan: pesan.join(' · ').slice(0, 300), harga, contoh };
}
module.exports = { ACUAN_SUMBER, ACUAN_ALAMAT, ACUAN_LEVEL, ACUAN_MAKS, sisirHarga, dokTarik, angkaHarga, isoDari };
