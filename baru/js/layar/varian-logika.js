// VARIAN MEREK PER BELANJA (putaran 27 Bagian 2, owner 27 Sep: "LL minggu ini Rp700.000/50 kg, minggu depan bisa premium Rp800.000" — bukan
// kenaikan harga, tapi BARANG BERBEDA dengan nama yang sama). Mesin tidak berubah: barang yang berbeda menjadi NAMA yang berbeda, bentuk
// "<induk> · <mutu>" (atau "<induk> · <tanggal>" kalau owner tidak memberi nama mutu). Varian = nama karung biasa: kolam stok, modal, harga jual,
// label, tempat, dan rantai stok sendiri; kolam lama tidak disentuh (dijual sampai habis lalu diarsipkan, Bagian 3).
//  · Barang masuk: baris bernama yang sudah punya buku, harga beli/kg beda dari modal berjalan > batas owner (aturanToko/catatStok.batasVarian,
//    bawaan 5 %) → layar bertanya "sama barangnya" (gabung, modal rata-rata seperti biasa) / "beda mutu" (varian). Di bawah batas tidak bertanya.
//  · Varian mewarisi JENIS BERAS induknya: satu kunci baru di peta pengaturan/jenisBeras yang sudah ada (bukan kolom baru).
//  · Harga jual ditawarkan: usul = modal + target untung katalog (aturHarga dari layar), dibulatkan ke atas; terbit = dokumen katalog per kg varian itu saja
//    (+ hargaTerbit + label), draf harga lain tidak ikut terbit.
//  · Varian juga bisa dibuat dari Harga & Pemasok sebelum barangnya datang (katalog per kg + jenis).
// Tanpa DOM; nama berawalan vr (bundel uji satu lingkup). Dijaga alat-uji/uji_varian_merek.py.
import { hitungStokKarungPerMerk } from '../mesin/beku.js';
import { jenisUntukMerk, cariHargaKarungPerKg, hargaKarungUtuh } from '../mesin/pembantu.js';
import { ambilHargaKarung, ambilPetaJenisBeras, cacheMentah } from '../data/toko.js';
import { RP } from '../inti/format.js';
import { wbNamaKelas } from './wadah-bernama-logika.js';

export const VR_PEMISAH = ' · ';
export const VR_BATAS_BAWAAN = 5;   // % beda harga beli vs modal berjalan yang memicu pertanyaan (owner mengatur di Stok › Barang masuk › Atur)
const VR_BLN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
const vrBersih = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const vrBulatAtas = (x, k) => (k > 0 ? Math.ceil(x / k - 1e-9) * k : Math.round(x));

/** Nama varian: "LL · Premium"; tanpa nama mutu → "LL · 27 Sep" (tanggal barang masuk). */
export function vrNama(induk, mutu, tanggal) {
  const m = vrBersih(mutu); if (m) return vrBersih(induk) + VR_PEMISAH + m;
  const t = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(tanggal || '')); return vrBersih(induk) + VR_PEMISAH + (t ? Number(t[3]) + ' ' + VR_BLN[Number(t[2]) - 1] : 'baru');
}
/** Batas beda harga (%) yang diatur owner di aturanToko/catatStok (kolom batasVarian); belum diatur → 5 %. */
export function vrBatas() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'catatStok'); const n = a ? Number(a.batasVarian) : NaN;
  return a && a.batasVarian !== undefined && a.batasVarian !== null && isFinite(n) && n >= 0 ? n : VR_BATAS_BAWAAN;
}
/**
 * Perlu ditanya "sama barangnya / beda mutu"? Hanya nama yang SUDAH punya buku (stok atau riwayat) dan modal per kg-nya tercatat;
 * beda = |harga beli − modal berjalan| ÷ modal × 100, ditanya kalau LEBIH dari batas.
 */
export function vrPerluTanya(merk, hargaPerKg) {
  const st = hitungStokKarungPerMerk()[String(merk || '')]; const h = Number(hargaPerKg) || 0; const batas = vrBatas();
  if (!st || !(st.hppTerakhirPerKg > 0) || !(h > 0)) return { perlu: false, modal: st ? st.hppTerakhirPerKg || 0 : 0, beda: 0, batas, adaBuku: !!st };
  const beda = Math.abs(h - st.hppTerakhirPerKg) / st.hppTerakhirPerKg * 100;
  return { perlu: beda > batas + 1e-9, modal: st.hppTerakhirPerKg, beda: Math.round(beda * 10) / 10, naik: h > st.hppTerakhirPerKg, batas, adaBuku: true };
}
/** Usul harga jual per kg = modal + target untung katalog, dibulatkan ke atas ke pembulatan per kg. atur = aturHarga() layar Harga (satu sumber target; tidak diimpor
 *  di sini supaya logika Stok tidak menyeret seluruh logika katalog). */
export function vrUsulHarga(modalKg, atur) { const a = atur || {}; return modalKg > 0 ? vrBulatAtas(modalKg + (Number(a.targetPerKg) || 0), Number(a.bulatKarung) || 0) : 0; }
/**
 * Dokumen peta jenis beras dengan kunci varian baru = jenis induknya (jenisUntukMerk: isi peta atau tebakan dari nama; '' tetap ditulis '').
 * Kunci yang sudah ada tidak ditimpa (owner boleh sudah mengubahnya). null = tidak ada yang perlu ditulis.
 */
export function vrDokJenis(pasangan, w) {
  const peta = ambilPetaJenisBeras(); let ubah = false;
  (pasangan || []).forEach((x) => { if (!x || !x.varian || Object.prototype.hasOwnProperty.call(peta, x.varian)) return; peta[x.varian] = jenisUntukMerk(x.induk); ubah = true; });
  return ubah ? { koleksi: 'pengaturan', data: { id: 'jenisBeras', peta, diubahPada: w.kini } } : null;
}
/** Apakah nama ini sudah dikenal (buku stok atau katalog per kg)? */
export const vrAda = (nama) => !!hitungStokKarungPerMerk()[nama] || ambilHargaKarung().some((h) => h.merk === nama);

/**
 * TERBITKAN harga jual per kg SATU varian (tawaran sesudah barang masuk, atau varian baru dari Harga): dokumen katalogHargaKarung bentuk
 * simpanHargaKarung + modalSaatSetel, catatan hargaTerbit, tugas label, dan draf nama itu (kalau ada) dibuang — draf harga lain TIDAK ikut terbit.
 * Di bawah modal = dua ketukan. Layar menambahkan katalog HP kasir di kiriman yang sama (kkSertakan).
 */
export function vrSusunTerbitHarga(varian, hargaKetik, w, yakin) {
  const nama = vrBersih(varian); const n = Math.round(Number(String(hargaKetik === undefined || hargaKetik === null ? '' : hargaKetik).replace(/\./g, '').replace(',', '.')) || 0);
  if (!nama) return { tolak: 'Nama variannya kosong' };
  if (!(n >= 1000)) return { tolak: 'Harga jual per kg belum benar — ketik rupiahnya (mis. 16.000)' };
  const st = hitungStokKarungPerMerk()[nama]; const modal = st ? st.hppTerakhirPerKg || 0 : 0;
  if (modal > 0 && n < modal - 0.5 && !yakin) return { tolak: RP(n) + '/kg DI BAWAH modal ' + nama + ' ' + RP(Math.round(modal)) + '/kg. Boleh — tapi ini keputusan, bukan kebetulan. Ketuk sekali lagi.', perluYakin: true };
  const lama = ambilHargaKarung().find((h) => h.merk === nama) || null;
  const dok = { koleksi: 'katalogHargaKarung', data: { id: lama ? lama.id : nama, merk: nama, hargaPerKg: n, diubahPada: w.kini, modalSaatSetel: st ? Math.round(st.hargaTerakhirPerKg || 0) : 0 } };
  const label = (cacheMentah('aturan').find((d) => String(d.id) === 'hargaLabel') || {}).daftar; const daftarLabel = Array.isArray(label) ? label.filter((x) => x.k !== nama + '|S') : [];
  const lamaN = lama ? Math.round(Number(lama.hargaPerKg) || 0) : 0; if (lamaN !== n) daftarLabel.push({ k: nama + '|S', lama: lamaN, tanggal: w.tanggal });
  const drafDok = cacheMentah('aturan').find((d) => String(d.id) === 'hargaDraf'); const draf = Object.assign({}, (drafDok && drafDok.draf) || {}); const adaDraf = draf[nama + '|S'] !== undefined; delete draf[nama + '|S'];
  const dokumen = [dok, { koleksi: 'aturanToko', data: { id: 'hargaLabel', tanggal: w.tanggal, jam: w.jam, daftar: daftarLabel } },
    { koleksi: 'hargaTerbit', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, n: 1, daftar: [{ kunci: nama + '|S', nama: nama + ' · Karung per kg', lama: lamaN, baru: n, koleksi: 'katalogHargaKarung' }] } }];
  if (adaDraf) dokumen.push({ koleksi: 'aturanToko', data: { id: 'hargaDraf', tanggal: w.tanggal, jam: w.jam, draf } });
  return { dokumen, patch: { varianTawar: null, vrKetik: {}, vrYakin: false, kabar: 'Harga ' + nama + ' terbit: ' + RP(n) + '/kg' + (modal > 0 ? ' (modal ' + RP(Math.round(modal)) + ', untung ' + RP(Math.round(n - modal)) + '/kg)' : '') + ' — rak Jual & katalog HP kasir ikut. Draf harga lain tidak ikut terbit.', kabarAwas: false } };
}
/**
 * VARIAN BARU dari Harga & Pemasok (sebelum barangnya datang): nama "<induk> · <mutu>" + harga jual per kg langsung terbit + jenis induk.
 * Induk wajib nama yang dikenal; nama varian yang sudah ada ditolak (pilih di katalog seperti biasa).
 */
/**
 * Perbaikan 28 Sep (kejadian nyata): owner memberi harga lewat "varian merek baru" untuk merek yang BARU datang dan belum berharga — varian lahir dengan buku
 * kosong, stoknya tetap di nama induk tanpa harga, jadi tak satu pun tampil di Jual. Kalimat peringatan bila induk berstok tapi belum punya harga jual karung.
 * '' = tidak perlu diperingatkan.
 */
export function vrPeringatanInduk(induk) {
  const ind = vrBersih(induk); if (!ind) return ''; const st = hitungStokKarungPerMerk()[ind]; const sisa = st ? Number(st.sisaKg) || 0 : 0; if (!(sisa > 0.05)) return '';
  const perKg = cariHargaKarungPerKg(ind); const utuh = hargaKarungUtuh(ind, 50) || hargaKarungUtuh(ind, 25); if ((perKg !== null && perKg > 0) || (utuh && utuh.perUnit > 0)) return '';
  return ind + ' punya stok ' + String(Math.round(sisa * 10) / 10).replace('.', ',') + ' kg tapi BELUM ada harga jual — stok itu tetap atas nama ' + ind + ' dan tidak tampil di Jual. Kalau barangnya SAMA, setel harga ' + ind + ' di katalog (bukan varian). Varian = nama BARU yang stoknya 0 sampai ada barang masuk atas nama varian itu.';
}
/** Pilihan merek induk untuk varian baru dari layar Harga: bukan nama varian, bukan nama wadah / kelas mutu (yang itu ditolak saat dibuat). */
export function vrCalonInduk(daftar) { const kelas = wbNamaKelas(); return (daftar || []).filter((m) => String(m).indexOf(VR_PEMISAH) < 0 && !kelas[m]); }
export function vrSusunBuatDariHarga(induk, mutu, hargaKetik, w, yakin) {
  const ind = vrBersih(induk); const m = vrBersih(mutu);
  if (!ind || !vrAda(ind)) return { tolak: 'Pilih dulu merek induknya (nama yang sudah ada di buku atau katalog)' };
  if (wbNamaKelas()[ind.split(VR_PEMISAH)[0]]) return { tolak: ind + ' itu nama WADAH / kelas mutu, bukan merek karung — varian dibuat dari merek yang tertera di karung' };   // putaran 27 (Bagian 5)
  if (!m) return { tolak: 'Tulis nama mutunya (mis. Premium) — varian dari layar Harga harus bernama' };
  if (m.indexOf('·') >= 0) return { tolak: 'Nama mutu tidak boleh memakai titik tengah' };
  const nama = vrNama(ind, m, w.tanggal); if (vrAda(nama)) return { tolak: nama + ' sudah ada — ubah harganya di katalog seperti biasa' };
  const r = vrSusunTerbitHarga(nama, hargaKetik, w, yakin); if (r.tolak) return r;
  const jenis = vrDokJenis([{ varian: nama, induk: ind }], w); if (jenis) r.dokumen.push(jenis);
  r.patch = Object.assign({}, r.patch, { vrBaru: null, kabar: 'Varian ' + nama + ' dibuat (jenis beras ikut ' + ind + ': ' + (jenisUntukMerk(ind) || 'belum diisi') + '). ' + r.patch.kabar + ' Stoknya mulai dari barang masuk atas nama ini.' });
  return r;
}
