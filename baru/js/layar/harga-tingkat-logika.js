// HARGA PELANGGAN USAHA — putaran B1 (keputusan owner 16 Nov 2026). Logika TANPA DOM, nama berawalan ht (bundel uji jsc satu lingkup).
// Dijaga alat-uji/uji_harga_tingkat.py (jsc + kontrol).
//
// Keputusan owner 16 Nov 2026:
//  - TINGKAT bawaan Warung · Catering · Instansi, di bawah harga eceran. Daftarnya (nama & potongan) diatur owner sendiri dari layar.
//  - Harga tingkat = harga ECERAN katalog dikurangi POTONGAN Rp per kg (satu angka per tingkat, berlaku ke semua barang, ikut berubah otomatis kalau eceran
//    diubah). Barang tertentu boleh diberi HARGA SENDIRI per tingkat. Di atas itu: HARGA KHUSUS per pelanggan per barang dengan tanggal berlaku.
//    Urutan yang dipakai: harga khusus yang berlaku hari itu → harga sendiri barang di tingkatnya → eceran − potongan tingkat → eceran.
//  - Ben MENGUSULKAN (tingkat, pasang pelanggan ke tingkat, harga barang, harga khusus) lewat papan Persetujuan; berlaku sesudah owner menyetujui.
//    Karyawan cuma memakai harganya di Jual. Kisi SS2 tindakan 'hargaPelanggan' (bawaan Ben "minta owner", karyawan "tidak boleh").
//  - Saran harga grosir per JUMLAH (keputusan 9 Okt) BUKAN bagian B1 — ditunda.
// Tempat: SATU dokumen aturanToko/hargaTingkat { tingkat: [{ id, nama, potKg }], barang: { <tingkat>: { <kunci barang>: harga } },
//   orang: { <kunci pelanggan>: <tingkat> }, khusus: [{ id, orang, nama, barang, harga, mulai, sampai, catatan }] } — ditulis owner saja, dibaca staf
//   (rules v8). Kunci barang = ngKunciBarang (nego-logika): karung|merek|berat · kemasan|merek|ukuran · literan|merek-atau-wadah · repack|merek.
// Potongan per satuan = potongan per kg × kg satuannya (karung = beratnya, kemasan = ukurannya, literan = kg per liter, repack = 1), dibulatkan ke Rp50
// terdekat. Mesin uang tidak disentuh: harga tingkat masuk nota sebagai harga satuan (hargaAsliSatuan), eceran ikut tercatat (hargaEceranSatuan).
import { cacheMentah } from '../data/toko.js';
import { kunciPelanggan, kunciKemasan, RASIO_KONVERSI, RASIO_DEFAULT } from '../mesin/pembantu.js';
import { ngNamaBarang } from './nego-logika.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';

export const HT_ID = 'hargaTingkat';
export const HT_TINDAKAN = 'hargaPelanggan';
export const HT_LANGKAH = 50;            // potongan per satuan dibulatkan ke Rp50 terdekat
export const HT_MAKS_TINGKAT = 8;
export const HT_MAKS_KHUSUS = 300;
export const HT_MAKS_POT_KG = 10000;     // potongan paling besar Rp10.000 per kg
export const HT_MAKS_HARGA = 100000000;
export const HT_BAWAAN = { tingkat: [{ id: 'warung', nama: 'Warung', potKg: 0 }, { id: 'catering', nama: 'Catering', potKg: 0 }, { id: 'instansi', nama: 'Instansi', potKg: 0 }],
  barang: {}, orang: {}, khusus: [] };
const HT_JENIS = ['karung', 'kemasan', 'literan', 'repack'];
const htSalin = (x) => JSON.parse(JSON.stringify(x));
const htTeks = (v, n) => String(v === undefined || v === null ? '' : v).trim().replace(/\s+/g, ' ').slice(0, n || 60);
const htTgl = (v) => (/^\d{4}-\d{2}-\d{2}$/.test(String(v || '')) ? String(v) : '');
const htObj = (v) => (v && typeof v === 'object' && !Array.isArray(v) ? v : {});
/** Angka ketikan ("1.500", "1500", "1,5") → bilangan; kosong = 0; bukan angka = NaN. */
export function htAngka(v) {
  if (typeof v === 'number') return v;
  const t = String(v === undefined || v === null ? '' : v).trim().replace(/^rp\.?\s*/i, ''); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t);
  return isFinite(n) ? n : NaN;
}
const htBulatRp = (n) => Math.round(n);
/** Kunci barang yang boleh diberi harga tingkat / khusus (beras saja — wadah & kantong tidak). */
export const htBarangSah = (k) => { const s = String(k || ''); const i = s.indexOf('|'); return i > 0 && HT_JENIS.indexOf(s.slice(0, i)) >= 0 && s.length > i + 1 && s.length <= 160; };
export const htNamaBarang = (k) => ngNamaBarang(k);

// ---------- SETELAN ----------
/** Setelan yang berlaku. dok undefined = dari cache (aturanToko/hargaTingkat); tanpa dokumen = bawaan (tiga tingkat, potongan 0 = sama dengan eceran). */
export function htAtur(dok) {
  const d = dok !== undefined ? dok : (cacheMentah('aturan').find((x) => String(x.id) === HT_ID) || null);
  const B = htSalin(HT_BAWAAN); if (!d) return Object.assign(B, { ada: false });
  const tingkat = []; (Array.isArray(d.tingkat) ? d.tingkat : B.tingkat).forEach((t) => {
    const id = htTeks(t && t.id, 24); const nama = htTeks(t && t.nama, 24); const p = Math.round(Number(t && t.potKg) || 0);
    if (id && nama && !tingkat.some((x) => x.id === id)) tingkat.push({ id, nama, potKg: Math.max(0, Math.min(HT_MAKS_POT_KG, p)) });
  });
  const ada = (id) => tingkat.some((t) => t.id === id);
  const barang = {}; Object.keys(htObj(d.barang)).forEach((tid) => { if (!ada(tid)) return; const isi = {};
    Object.keys(htObj(d.barang[tid])).forEach((k) => { const n = Math.round(Number(d.barang[tid][k]) || 0); if (htBarangSah(k) && n > 0) isi[k] = n; });
    if (Object.keys(isi).length) barang[tid] = isi; });
  const orang = {}; Object.keys(htObj(d.orang)).forEach((k) => { const kk = kunciPelanggan(k); const tid = String(d.orang[k] || ''); if (kk && ada(tid)) orang[kk] = tid; });
  const khusus = (Array.isArray(d.khusus) ? d.khusus : []).map(htBersihKhusus).filter(Boolean);
  return { tingkat, barang, orang, khusus, ada: true, tanggal: String(d.tanggal || ''), jam: String(d.jam || '') };
}
function htBersihKhusus(x) {
  const o = htObj(x); const id = htTeks(o.id, 40); const orang = kunciPelanggan(o.orang); const barang = String(o.barang || ''); const harga = Math.round(Number(o.harga) || 0);
  const mulai = htTgl(o.mulai); const sampai = htTgl(o.sampai);
  if (!id || !orang || !htBarangSah(barang) || !(harga > 0) || !mulai || (sampai && sampai < mulai)) return null;
  return { id, orang, nama: htTeks(o.nama, 40) || orang, barang, harga, mulai, sampai, catatan: htTeks(o.catatan, 80) };
}
export const htTingkat = (A, id) => (A.tingkat.find((t) => t.id === id) || null);
/** Tingkat seorang pelanggan (nama atau kuncinya) → { id, nama, potKg } atau null (eceran). */
export function htTingkatOrang(orang, A0) { const A = A0 || htAtur(); const k = kunciPelanggan(orang); return k && A.orang[k] ? htTingkat(A, A.orang[k]) : null; }
/** Harga khusus yang berlaku untuk orang & barang pada tanggal itu (yang mulainya paling baru menang). */
export function htKhususAktif(orang, barang, tanggal, A0) {
  const A = A0 || htAtur(); const k = kunciPelanggan(orang); const t = htTgl(tanggal) || hariIniIso();
  return A.khusus.filter((x) => x.orang === k && x.barang === barang && x.mulai <= t && (!x.sampai || x.sampai >= t))
    .sort((a, b) => (b.mulai > a.mulai ? 1 : b.mulai < a.mulai ? -1 : String(b.id).localeCompare(String(a.id))))[0] || null;
}
export const htPotSatuan = (potKg, kg) => Math.round((Number(potKg) || 0) * (Number(kg) || 0) / HT_LANGKAH) * HT_LANGKAH;

/**
 * HARGA untuk satu pelanggan & satu barang. o = { orang, barang, eceran, kg, tanggal }. → null (eceran, tanpa tingkat) atau
 * { harga, eceran, sumber: 'khusus' | 'barang' | 'tingkat', id (tingkat, '' bila khusus tanpa tingkat), nama (label), khususId, potongan }.
 * Tingkat dengan potongan 0 & tanpa harga sendiri tetap dikembalikan (harga = eceran) supaya nota mencatat tingkat pembelinya.
 */
export function htHarga(o, A0) {
  const A = A0 || htAtur(); const k = kunciPelanggan(o && o.orang); const barang = String((o && o.barang) || '');
  if (!k || !htBarangSah(barang)) return null;
  const eceran = Math.round(Number(o.eceran) || 0); const T = A.orang[k] ? htTingkat(A, A.orang[k]) : null;
  const kh = htKhususAktif(k, barang, o.tanggal, A);
  if (kh) return { harga: kh.harga, eceran, sumber: 'khusus', id: T ? T.id : '', nama: 'harga khusus', khususId: kh.id, potongan: eceran > 0 ? eceran - kh.harga : 0 };
  if (!T) return null;
  const sendiri = (A.barang[T.id] || {})[barang];
  if (sendiri > 0) return { harga: sendiri, eceran, sumber: 'barang', id: T.id, nama: T.nama, khususId: '', potongan: eceran > 0 ? eceran - sendiri : 0 };
  if (!(eceran > 0)) return null;
  const pot = htPotSatuan(T.potKg, o.kg); const harga = eceran - pot;
  if (!(harga > 0)) return null;   // potongan menghabiskan harga — tidak dipakai (layar setelan menandainya)
  return { harga, eceran, sumber: 'tingkat', id: T.id, nama: T.nama, khususId: '', potongan: pot };
}

// ---------- RAK & BARIS JUAL ----------
/** Kunci barang sebuah chip rak Jual (= ngKunciBarang baris yang dibangun dari chip itu). Wadah/kantong = null. */
export function htKunciChip(c) {
  if (!c) return null;
  if (c.jalur === 'karung') return 'karung|' + c.kunci + '|' + c.berat;
  if (c.jalur === 'kemasan') return 'kemasan|' + (c.setengahDari ? kunciKemasan(c.nama, c.ukuranKg) : c.kunci);   // ½ karung = barang 25 kg (kunci baris notanya)
  if (c.jalur === 'literan') return 'literan|' + c.kunci;
  if (c.jalur === 'repack') return 'repack|' + c.kunci;
  return null;
}
/** kg satu satuan chip: karung = beratnya, kemasan = ukurannya, literan = kg per liter, repack = 1 (harga per kg). */
export function htKgChip(c) {
  if (!c) return 0;
  if (c.jalur === 'karung') return Number(c.berat) || 0;
  if (c.jalur === 'kemasan') return Number(c.ukuranKg) || 0;
  if (c.jalur === 'literan') return Number(c.rasio) || RASIO_KONVERSI[c.kunci] || RASIO_DEFAULT;
  if (c.jalur === 'repack') return 1;
  return 0;
}
/** kg satu satuan dari KUNCI barang (papan persetujuan nego): karung/kemasan = angka terakhir, literan = kg per liter mereknya, repack = 1. */
export function htKgBarang(barang) {
  const b = String(barang || '').split('|'); const akhir = Number(b[b.length - 1]) || 0;
  if (b[0] === 'karung' || b[0] === 'kemasan') return akhir; if (b[0] === 'literan') return RASIO_KONVERSI[b.slice(1).join('|')] || RASIO_DEFAULT; if (b[0] === 'repack') return 1; return 0;
}
/** Harga chip untuk pelanggan ini (null = eceran). Chip ½ karung: kg 25, kuncinya kemasan 50 kg yang dipecah. */
export function htHargaChip(c, orang, tanggal, A0) {
  const barang = htKunciChip(c); if (!barang) return null;
  return htHarga({ orang, barang, eceran: c.harga, kg: htKgChip(c), tanggal }, A0);
}
/** Tandai chip rak (karung · kemasan · literan · repack) dengan harga pelanggan ini — untuk TAMPILAN; harga eceran chip tetap (baris dibangun ulang dari chip). */
export function htTandaiRak(rak, orang, tanggal) {
  if (!kunciPelanggan(orang)) return 0; const A = htAtur(); if (!A.orang[kunciPelanggan(orang)] && !A.khusus.some((x) => x.orang === kunciPelanggan(orang))) return 0;
  let n = 0; ['karung', 'kemasan', 'literan', 'repack'].forEach((jl) => (rak[jl] || []).forEach((c) => {
    const H = htHargaChip(c, orang, tanggal, A); if (!H) return;
    c.hargaTingkat = H.harga; c.tingkatNama = H.nama; c.tingkatSumber = H.sumber; n += 1;
  }));
  return n;
}
/** Kolom harga tingkat untuk baris nota t yang dibangun dari chip. Kembali { hargaAsli, kolom } — kolom ditulis ke baris & dokumen penjualan. */
export function htKolomBaris(chip, t, orang, tanggal) {
  if (!t || t.jenis === 'wadah' || !kunciPelanggan(orang)) return { hargaAsli: chip.harga, kolom: null };
  const H = htHargaChip(chip, orang, tanggal); if (!H) return { hargaAsli: chip.harga, kolom: null };
  const kolom = { hargaEceranSatuan: chip.harga, tingkatHarga: H.nama, tingkatId: H.id, hargaSumber: H.sumber };
  if (H.khususId) kolom.hargaKhususId = H.khususId;
  return { hargaAsli: H.harga, kolom };
}
export const HT_KOLOM_BARIS = ['hargaEceranSatuan', 'tingkatHarga', 'tingkatId', 'hargaSumber', 'hargaKhususId'];

// ---------- UBAH (owner langsung · Ben lewat usul) ----------
const htSlug = (nama) => String(nama || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 20) || 'tingkat';
/**
 * Terapkan SATU ubahan ke setelan A → { A, kabar } atau { tolak }. ubah.jenis:
 *  'tingkat'     { tingkat: [{ id?, nama, potKg }] }   daftar utuh (urutan = urutan tampil)
 *  'barang'      { tingkatId, barang, harga }          harga 0 / kosong = hapus harga sendiri (kembali ke potongan tingkat)
 *  'orang'       { orang, nama, tingkatId }            tingkatId '' = kembali ke harga eceran
 *  'khusus'      { id?, orang, nama, barang, harga, mulai, sampai, catatan }
 *  'hapusKhusus' { id }
 */
export function htTerapkan(A0, ubah, w) {
  const A = htSalin(A0 || htAtur()); const u = htObj(ubah); const W = w || {};
  if (u.jenis === 'tingkat') {
    const isi = Array.isArray(u.tingkat) ? u.tingkat : []; if (!isi.length) return { tolak: 'Paling sedikit satu tingkat' };
    if (isi.length > HT_MAKS_TINGKAT) return { tolak: 'Paling banyak ' + HT_MAKS_TINGKAT + ' tingkat' };
    const baru = []; const nama = {};
    for (const t of isi) {
      const nm = htTeks(t && t.nama, 24); if (nm.length < 2) return { tolak: 'Nama tingkat minimal dua huruf' };
      if (nama[nm.toLowerCase()]) return { tolak: 'Nama tingkat "' + nm + '" dua kali' }; nama[nm.toLowerCase()] = 1;
      const p = htAngka(t && t.potKg); if (!isFinite(p) || p < 0 || Math.round(p) !== p) return { tolak: 'Potongan ' + nm + ' harus rupiah bulat (boleh 0)' };
      if (p > HT_MAKS_POT_KG) return { tolak: 'Potongan ' + nm + ' paling besar ' + RP(HT_MAKS_POT_KG) + ' per kg' };
      let id = htTeks(t && t.id, 24);
      if (!id || !A.tingkat.some((x) => x.id === id) || baru.some((x) => x.id === id)) { const dasar = htSlug(nm); id = dasar; let i = 2; while (baru.some((x) => x.id === id) || A.tingkat.some((x) => x.id === id && !isi.some((y) => y && y.id === id))) id = dasar + '-' + (i++); }
      baru.push({ id, nama: nm, potKg: p });
    }
    const hilang = A.tingkat.filter((t) => !baru.some((x) => x.id === t.id));
    for (const t of hilang) { const n = Object.keys(A.orang).filter((k) => A.orang[k] === t.id).length; if (n) return { tolak: 'Tingkat ' + t.nama + ' masih dipakai ' + n + ' pelanggan — pindahkan mereka ke tingkat lain dulu' }; }
    const nSendiri = hilang.reduce((a, t) => a + Object.keys(A.barang[t.id] || {}).length, 0);
    hilang.forEach((t) => { delete A.barang[t.id]; }); A.tingkat = baru;
    return { A, kabar: 'Tingkat harga: ' + baru.map((t) => t.nama + (t.potKg > 0 ? ' −' + RP(t.potKg) + '/kg' : ' (sama dengan eceran)')).join(' · ') + (nSendiri ? ' — ' + nSendiri + ' harga barang dari tingkat yang dihapus ikut terhapus' : '') };
  }
  if (u.jenis === 'barang') {
    const T = htTingkat(A, String(u.tingkatId || '')); if (!T) return { tolak: 'Tingkatnya tidak ada lagi' };
    const barang = String(u.barang || ''); if (!htBarangSah(barang)) return { tolak: 'Barangnya tidak dikenali' };
    const n = htAngka(u.harga);
    if (u.harga === '' || u.harga === null || u.harga === undefined || n === 0) { if (!(A.barang[T.id] || {})[barang]) return { tolak: htNamaBarang(barang) + ' memang belum punya harga sendiri di ' + T.nama };
      delete A.barang[T.id][barang]; if (!Object.keys(A.barang[T.id]).length) delete A.barang[T.id];
      return { A, kabar: htNamaBarang(barang) + ' di ' + T.nama + ' kembali ikut potongan tingkat' }; }
    if (!isFinite(n) || n <= 0 || Math.round(n) !== n || n > HT_MAKS_HARGA) return { tolak: 'Harga harus rupiah bulat lebih dari 0' };
    A.barang[T.id] = Object.assign({}, A.barang[T.id] || {}); A.barang[T.id][barang] = n;
    return { A, kabar: htNamaBarang(barang) + ' untuk ' + T.nama + ': ' + RP(n) };
  }
  if (u.jenis === 'orang') {
    const k = kunciPelanggan(u.orang); if (!k) return { tolak: 'Nama pelanggannya kosong' };
    const nm = htTeks(u.nama, 40) || k; const tid = String(u.tingkatId || '');
    if (!tid) { if (!A.orang[k]) return { tolak: nm + ' memang belum punya tingkat — harganya eceran' }; delete A.orang[k]; return { A, kabar: nm + ' kembali ke harga eceran' }; }
    const T = htTingkat(A, tid); if (!T) return { tolak: 'Tingkatnya tidak ada lagi' };
    if (A.orang[k] === tid) return { tolak: nm + ' memang sudah di tingkat ' + T.nama };
    A.orang[k] = tid; return { A, kabar: nm + ' sekarang memakai harga ' + T.nama };
  }
  if (u.jenis === 'khusus') {
    const k = kunciPelanggan(u.orang); if (!k) return { tolak: 'Pilih pelanggannya dulu' };
    const barang = String(u.barang || ''); if (!htBarangSah(barang)) return { tolak: 'Pilih barangnya dulu' };
    const n = htAngka(u.harga); if (!isFinite(n) || n <= 0 || Math.round(n) !== n || n > HT_MAKS_HARGA) return { tolak: 'Harga khusus harus rupiah bulat lebih dari 0' };
    const mulai = htTgl(u.mulai) || htTgl(W.tanggal); const sampai = htTgl(u.sampai);
    if (!mulai) return { tolak: 'Tanggal mulainya belum benar' }; if (u.sampai && !sampai) return { tolak: 'Tanggal sampainya belum benar' };
    if (sampai && sampai < mulai) return { tolak: 'Tanggal sampai lebih awal dari tanggal mulai' };
    const id = htTeks(u.id, 40); const lama = id ? A.khusus.find((x) => x.id === id) : null;
    if (id && !lama) return { tolak: 'Harga khusus itu sudah tidak ada' };
    if (!lama && A.khusus.length >= HT_MAKS_KHUSUS) return { tolak: 'Sudah ' + HT_MAKS_KHUSUS + ' harga khusus — hapus yang sudah lewat dulu' };
    const x = { id: lama ? lama.id : 'k' + String(W.idUnik ? W.idUnik() : Date.now()).replace(/\D/g, '').slice(0, 16), orang: k, nama: htTeks(u.nama, 40) || k, barang, harga: n, mulai, sampai, catatan: htTeks(u.catatan, 80) };
    A.khusus = A.khusus.filter((y) => y.id !== x.id).concat([x]);
    return { A, kabar: 'Harga khusus ' + x.nama + ' · ' + htNamaBarang(barang) + ' ' + RP(n) + ' ' + htMasaTeks(x) };
  }
  if (u.jenis === 'hapusKhusus') {
    const x = A.khusus.find((y) => y.id === String(u.id || '')); if (!x) return { tolak: 'Harga khusus itu sudah tidak ada' };
    A.khusus = A.khusus.filter((y) => y.id !== x.id); return { A, kabar: 'Harga khusus ' + x.nama + ' · ' + htNamaBarang(x.barang) + ' dihapus' };
  }
  return { tolak: 'Ubahan tidak dikenali' };
}
export const htMasaTeks = (x) => (x.sampai ? tanggalPendek(x.mulai) + ' – ' + tanggalPendek(x.sampai) : 'mulai ' + tanggalPendek(x.mulai));
/** Ubahan yang dikirim (usul Ben) dibersihkan — hanya kolom yang dikenal, supaya papan owner tidak menampilkan isian liar. */
export function htBersihUbah(ubah) {
  const u = htObj(ubah); const j = String(u.jenis || '');
  if (j === 'tingkat') return { jenis: j, tingkat: (Array.isArray(u.tingkat) ? u.tingkat : []).slice(0, HT_MAKS_TINGKAT + 1).map((t) => ({ id: htTeks(t && t.id, 24), nama: htTeks(t && t.nama, 24), potKg: htTeks(t && t.potKg, 12) })) };
  if (j === 'barang') return { jenis: j, tingkatId: htTeks(u.tingkatId, 24), barang: String(u.barang || '').slice(0, 160), harga: htTeks(u.harga, 14) };
  if (j === 'orang') return { jenis: j, orang: htTeks(u.orang, 40), nama: htTeks(u.nama, 40), tingkatId: htTeks(u.tingkatId, 24) };
  if (j === 'khusus') return { jenis: j, id: htTeks(u.id, 40), orang: htTeks(u.orang, 40), nama: htTeks(u.nama, 40), barang: String(u.barang || '').slice(0, 160), harga: htTeks(u.harga, 14), mulai: htTeks(u.mulai, 10), sampai: htTeks(u.sampai, 10), catatan: htTeks(u.catatan, 80) };
  if (j === 'hapusKhusus') return { jenis: j, id: htTeks(u.id, 40) };
  return { jenis: '' };
}
/** Kalimat ubahan "dari → jadi" terhadap setelan SEKARANG (papan persetujuan menghitungnya sendiri, bukan teks kiriman). */
export function htTeksUbah(ubah, A0) {
  const A = A0 || htAtur(); const u = htBersihUbah(ubah); const r = htTerapkan(A, u, {});
  if (u.jenis === 'tingkat') { const lama = A.tingkat.map((t) => t.nama + ' −' + RP(t.potKg) + '/kg').join(' · '); return 'Tingkat harga: ' + lama + ' → ' + (r.tolak ? '(tidak sah)' : r.A.tingkat.map((t) => t.nama + ' −' + RP(t.potKg) + '/kg').join(' · ')) + (r.tolak ? ' — ' + r.tolak : ''); }
  if (u.jenis === 'barang') { const T = htTingkat(A, u.tingkatId); const lama = T ? (A.barang[T.id] || {})[u.barang] : 0; const n = htAngka(u.harga);
    return 'Harga ' + htNamaBarang(u.barang) + ' di ' + (T ? T.nama : 'tingkat yang sudah dihapus') + ': ' + (lama ? RP(lama) : 'ikut potongan') + ' → ' + (n > 0 ? RP(n) : 'ikut potongan') + (r.tolak ? ' — ' + r.tolak : ''); }
  if (u.jenis === 'orang') { const k = kunciPelanggan(u.orang); const lama = A.orang[k] ? htTingkat(A, A.orang[k]) : null; const T = htTingkat(A, u.tingkatId);
    return 'Pelanggan ' + (u.nama || k) + ': ' + (lama ? lama.nama : 'eceran') + ' → ' + (u.tingkatId ? (T ? T.nama : 'tingkat yang sudah dihapus') : 'eceran') + (r.tolak ? ' — ' + r.tolak : ''); }
  if (u.jenis === 'khusus') { const n = htAngka(u.harga); const lama = u.id ? A.khusus.find((x) => x.id === u.id) : null; const mulai = htTgl(u.mulai);
    return 'Harga khusus ' + (u.nama || u.orang) + ' · ' + htNamaBarang(u.barang) + ': ' + (lama ? RP(lama.harga) + ' → ' : '') + (n > 0 ? RP(n) : '?')
      + (mulai ? ' ' + htMasaTeks({ mulai, sampai: htTgl(u.sampai) }) : '') + (r.tolak ? ' — ' + r.tolak : ''); }
  if (u.jenis === 'hapusKhusus') { const x = A.khusus.find((y) => y.id === u.id); return x ? 'Hapus harga khusus ' + x.nama + ' · ' + htNamaBarang(x.barang) + ' ' + RP(x.harga) : 'Hapus harga khusus yang sudah tidak ada'; }
  return 'Ubahan harga yang tidak dikenali';
}
/** Dokumen aturanToko/hargaTingkat dari setelan A. */
export function htDokumen(A, w) {
  return { id: HT_ID, tingkat: A.tingkat.map((t) => ({ id: t.id, nama: t.nama, potKg: t.potKg })), barang: htSalin(A.barang), orang: htSalin(A.orang),
    khusus: A.khusus.map((x) => ({ id: x.id, orang: x.orang, nama: x.nama, barang: x.barang, harga: x.harga, mulai: x.mulai, sampai: x.sampai, catatan: x.catatan })),
    tanggal: w.tanggal, jam: w.jam, diubahPada: w.kini };
}
/**
 * Susun ubahan untuk akun ini. Owner → tulis setelan langsung. Bukan-owner → USUL ke owner (koleksi persetujuan, tindakan 'hargaPelanggan'),
 * kecuali kisinya "tidak boleh". opsi = { hak: 'sendiri' | 'owner' | 'tidak' (kisi SS2), bisaMinta (false = server belum membuka usul) }.
 */
export function htSusun(akun, ubah, w, opsi) {
  const o = opsi || {}; const A = htAtur(); const u = htBersihUbah(ubah); if (u.jenis === 'khusus' && !u.mulai) u.mulai = w.tanggal;
  const r = htTerapkan(A, u, w); if (r.tolak) return { tolak: r.tolak };
  const owner = !akun || akun.jenis === 'owner';
  if (owner) return { dokumen: [{ koleksi: 'aturanToko', data: htDokumen(r.A, w) }], patch: { kabar: r.kabar, kabarAwas: false } };
  if ((o.hak || 'tidak') === 'tidak') return { tolak: 'Peran ' + (akun.nama || 'ini') + ' tidak boleh mengatur harga pelanggan usaha' };
  if (o.bisaMinta === false) return { tolak: 'Usul ke owner dari perangkat ini belum bisa — server belum membuka usul harga (aturan v8). Sampaikan langsung ke owner.' };
  const data = { id: w.idUnik(), tindakan: HT_TINDAKAN, status: 'menunggu', tanggal: w.tanggal, jam: w.jam, pada: w.kini, dari: String(akun.nama || ''), peran: String(akun.peran || ''),
    usulUid: String(akun.uid || ''), ubah: u, teks: htTeksUbah(u, A) };
  return { dokumen: [{ koleksi: 'persetujuan', data }], patch: { kabar: 'Usul terkirim ke owner: ' + data.teks + ' — harga di kasir belum berubah sampai owner menyetujui.', kabarAwas: false } };
}
/** Owner menyetujui usul m → dokumen setelan yang dipasang (dihitung ulang atas setelan SEKARANG). */
export function htPasangUsul(m, w) {
  if (!m || m.tindakan !== HT_TINDAKAN) return { tolak: 'Bukan usul harga pelanggan' };
  const r = htTerapkan(htAtur(), htBersihUbah(m.ubah), w); if (r.tolak) return { tolak: 'Usul ' + (m.dari || '') + ' tidak bisa dipasang lagi: ' + r.tolak + ' — tolak usulnya dengan alasan itu' };
  return { dokumen: [{ koleksi: 'aturanToko', data: htDokumen(r.A, w) }], kabar: r.kabar };
}
/** Usul harga yang masih menunggu dari akun ini (layar Ben) — terbaru dulu. */
export function htUsulSaya(akun) {
  const uid = String((akun && akun.uid) || ''); if (!uid) return [];
  return cacheMentah('persetujuan').filter((m) => m && m.tindakan === HT_TINDAKAN && String(m.usulUid || '') === uid)
    .sort((a, b) => String(b.pada || b.tanggal || '').localeCompare(String(a.pada || a.tanggal || ''))).slice(0, 12)
    .map((m) => ({ id: String(m.id), teks: htTeksUbah(m.ubah), status: m.status || 'menunggu', alasanTolak: String(m.alasanTolak || ''), tanggal: m.tanggal || '', jam: m.jam || '' }));
}

// ---------- PAPAN (layar Pelanggan › Usaha) ----------
/** Ringkas tiap tingkat: jumlah pelanggan & harga barang sendiri. namaOrang(kunci) → nama tampil. */
export function htPapanTingkat(A0, namaOrang) {
  const A = A0 || htAtur(); const nm = namaOrang || ((k) => k);
  return A.tingkat.map((t) => { const orang = Object.keys(A.orang).filter((k) => A.orang[k] === t.id).map((k) => ({ kunci: k, nama: nm(k) || k })).sort((a, b) => a.nama.localeCompare(b.nama, 'id'));
    return { id: t.id, nama: t.nama, potKg: t.potKg, orang, nOrang: orang.length, nSendiri: Object.keys(A.barang[t.id] || {}).length,
      contoh: t.potKg > 0 ? 'karung 50 kg −' + RP(htPotSatuan(t.potKg, 50)) + ' · kemasan 5 kg −' + RP(htPotSatuan(t.potKg, 5)) + ' · literan −' + RP(htPotSatuan(t.potKg, RASIO_DEFAULT)) + '/L' : 'potongan 0 — harganya sama dengan eceran' }; });
}
/**
 * Barang rak untuk satu tingkat: eceran, harga tingkat, harga sendiri, modal & tanda (OWNER saja — staf tidak melihat modal).
 * rak = rak identitas Jual (rakBarang). opsi = { owner, het: (merk, perKg) → teks peringatan atau '' }.
 * tanda: 'rugi' (di bawah modal) · 'nol' (sama dengan modal) · 'naik' (di atas eceran) · 'habis' (potongan menghabiskan harga) · 'tanpaModal' · ''.
 */
export function htPapanBarang(tingkatId, rak, opsi) {
  const o = opsi || {}; const A = o.atur || htAtur(); const T = htTingkat(A, tingkatId); if (!T || !rak) return [];
  const out = [];
  ['karung', 'kemasan', 'literan', 'repack'].forEach((jl) => (rak[jl] || []).forEach((c) => {
    const barang = htKunciChip(c); const kg = htKgChip(c); const eceran = Math.round(Number(c.harga) || 0); if (!barang || !(eceran > 0)) return;
    const sendiri = (A.barang[T.id] || {})[barang] || 0; const pot = htPotSatuan(T.potKg, kg); const harga = sendiri > 0 ? sendiri : eceran - pot;
    const modal = !o.owner ? null : jl === 'kemasan' ? (Number(c.hppPerUnit) > 0 ? Math.round(c.hppPerUnit) : null) : (Number(c.hppPerKg) > 0 ? Math.round(c.hppPerKg * kg) : null);
    let tanda = ''; if (!(harga > 0)) tanda = 'habis'; else if (harga > eceran) tanda = 'naik'; else if (o.owner && modal === null) tanda = 'tanpaModal'; else if (o.owner && harga < modal) tanda = 'rugi'; else if (o.owner && harga === modal) tanda = 'nol';
    const merk = jl === 'kemasan' ? c.nama : c.kunci; const het = o.het && harga > 0 && kg > 0 ? o.het(merk, harga / kg) : '';
    out.push({ barang, nama: htNamaBarang(barang), jalur: jl, satuan: c.satuan === 'L' ? 'L' : c.satuan, eceran, harga, sendiri, pot, modal, tanda, het,
      untung: o.owner && modal !== null && harga > 0 ? harga - modal : null });
  }));
  return out;
}
export const HT_TANDA = { rugi: 'di bawah modal', nol: 'untung nol', naik: 'di atas harga eceran', habis: 'potongan menghabiskan harga', tanpaModal: 'modal belum tercatat', '': '' };
/** Harga khusus untuk layar: per pelanggan (kunci) atau semua, dengan keadaan berlaku / belum / lewat pada tanggal itu. */
export function htPapanKhusus(orang, tanggal, A0) {
  const A = A0 || htAtur(); const t = htTgl(tanggal) || hariIniIso(); const k = orang ? kunciPelanggan(orang) : '';
  return A.khusus.filter((x) => !k || x.orang === k).map((x) => Object.assign({}, x, { namaBarang: htNamaBarang(x.barang), masa: htMasaTeks(x),
    keadaan: x.mulai > t ? 'belum' : x.sampai && x.sampai < t ? 'lewat' : 'berlaku' }))
    .sort((a, b) => (a.keadaan === b.keadaan ? a.nama.localeCompare(b.nama, 'id') || a.namaBarang.localeCompare(b.namaBarang, 'id') : ['berlaku', 'belum', 'lewat'].indexOf(a.keadaan) - ['berlaku', 'belum', 'lewat'].indexOf(b.keadaan)));
}
