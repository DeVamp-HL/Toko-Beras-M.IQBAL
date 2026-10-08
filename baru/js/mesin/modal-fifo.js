// MODAL FIFO (owner 9 Okt 2026): "pakai metode FIFO bukan average — barang yang dijual duluan itu barang yang lama dulu"; KECUALI wadah kotak literan
// yang dicampur = rata-rata. Owner memilih "Bangun, saklar di lu": selama saklar mati mesin tetap rata-rata seluruh kedatangan (tidak satu angka pun berubah).
// Saklar = aturanToko/catatStok.modalFifoMulai ('YYYY-MM-DD', hari pertama FIFO). Dokumen itu yang dipilih karena HP karyawan sudah boleh membacanya
// (firestore.rules: aturanToko read per dokumen) — kasir di HP karyawan wajib menghitung modal nota dengan cara yang sama dengan Mac owner.
//
// Cara hitung (tanpa mengulang tiap kejadian): sisa stok tiap merek karung = sumber yang sama dengan sekarang (masuk − terpakai). Karena yang keluar
// selalu yang PALING LAMA, sisa itu = kedatangan TERBARU. Kedatangan dijejer jadi LAPISAN berurutan (tanggal, id); lapisan pertama = sisa stok sehari
// sebelum saklar, bernilai modal rata-rata saat itu (nilai rak tidak melompat saat saklar ditekan). Panjang jejeran T, sisa S → yang keluar berikutnya
// berdiri di posisi P = T − S. Nilai sisa = harga lapisan dari P sampai T; modal nota berikutnya = harga lapisan dari P sampai P + kg.
// Di luar jejeran: posisi < 0 (retur/stok naik melebihi yang keluar) dinilai harga lapisan pertama; posisi > T (terjual sebelum kedatangannya
// dicatat — stok minus) dinilai harga lapisan terakhir.
// Tanpa DOM, tanpa Firestore: dipakai mesin beku (hitungStokKarungPerMerk) dan layar (jual, adukan, takar wadah, cocokkan, karantina, harga).

export const MF_DOK = 'catatStok';
export const MF_KOLOM = 'modalFifoMulai';

const mfTglSah = (t) => /^\d{4}-\d{2}-\d{2}$/.test(String(t || ''));

/** Hari pertama FIFO dari daftar dokumen aturanToko ('' = saklar mati). */
export function mfMulaiDari(aturan) {
  const a = (aturan || []).find((d) => d && String(d.id) === MF_DOK);
  const t = a ? String(a[MF_KOLOM] || '') : '';
  return mfTglSah(t) ? t : '';
}

/** Wadah kotak literan (kunci buku 'Wadah <nama>', data/toko.js kunciStokWadah) = isi campuran → tetap rata-rata (owner 9 Okt). */
export const mfWadah = (merk) => /^Wadah /.test(String(merk || ''));

/** 'YYYY-MM-DD' sehari sebelumnya (kalender, tanpa zona waktu). */
export function mfHariSebelum(t) {
  const d = new Date(String(t) + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() - 1);
  return d.toISOString().slice(0, 10);
}

const mfTotal = (L) => L.reduce((a, x) => a + x.kg, 0);

/** Harga per kg lapisan di posisi pos (pos = kg sejak awal jejeran). */
export function mfHargaDi(L, pos) {
  if (!L || !L.length) return 0;
  if (pos < 0) return L[0].harga;
  let awal = 0;
  for (let i = 0; i < L.length; i++) { const akhir = awal + L[i].kg; if (pos < akhir) return L[i].harga; awal = akhir; }
  return L[L.length - 1].harga;
}

/** Rupiah barang dari posisi dari sampai posisi sampai (boleh di luar jejeran, lihat kepala berkas). sampai < dari = negatif. */
export function mfIrisan(L, dari, sampai) {
  if (!L || !L.length || dari === sampai) return 0;
  if (sampai < dari) return -mfIrisan(L, sampai, dari);
  const T = mfTotal(L); let rp = 0;
  if (dari < 0) { const ujung = Math.min(sampai, 0); rp += (ujung - dari) * L[0].harga; dari = ujung; if (dari >= sampai) return rp; }
  let awal = 0;
  for (let i = 0; i < L.length && dari < sampai; i++) {
    const akhir = awal + L[i].kg;
    const a = Math.max(dari, awal), b = Math.min(sampai, akhir);
    if (b > a) { rp += (b - a) * L[i].harga; dari = b; }
    awal = akhir;
  }
  if (sampai > T && dari < sampai) rp += (sampai - Math.max(dari, T)) * L[L.length - 1].harga;
  return rp;
}

/**
 * Rupiah modal untuk kg yang KELUAR berikutnya dari satu merek (st = isi hitungStokKarungPerMerk()[merk]).
 * sudah = kg merek yang sama yang sudah diambil lebih dulu di kiriman yang sama (keranjang berisi dua baris merek sama).
 * Saklar mati / wadah / tanpa lapisan → kg × modal rata-rata (persis cara lama).
 */
export function hppKeluar(st, kg, sudah) {
  const n = Number(kg) || 0; if (!st) return 0;
  if (st.metode !== 'fifo' || !Array.isArray(st.lapisan) || !st.lapisan.length) return n * (st.hppTerakhirPerKg || 0);
  const p = (st.posKeluar || 0) + (Number(sudah) || 0);
  return mfIrisan(st.lapisan, p, p + n);
}

/** Modal per kg untuk kg yang keluar berikutnya (kg kosong = 1 kg terdepan). */
export function hppKeluarPerKg(st, kg, sudah) {
  const n = Number(kg) || 0; if (!st) return 0;
  if (st.metode !== 'fifo') return st.hppTerakhirPerKg || 0;
  return n > 0 ? hppKeluar(st, n, sudah) / n : (st.hppKeluarPerKg || 0);
}

/**
 * Dipanggil mesin sesudah buku rata-rata selesai (hasil = { merk: { sisaKg, hargaTerakhirPerKg, hppTerakhirPerKg } }).
 * buka = buku rata-rata sehari sebelum mulai; baru = { merk: [{ tanggal, id, kg, harga, asal }] } kedatangan sejak mulai.
 * Mengubah hasil di tempat: hppTerakhirPerKg = NILAI sisa per kg (neraca & nilai rak tetap sisa × hppTerakhirPerKg), plus metode/lapisan/posKeluar/
 * hppKeluarPerKg (modal nota berikutnya) dan hppRataPerKg (angka lama, pembanding berlabel).
 */
export function mfPasang(hasil, buka, baru, mulai) {
  Object.keys(hasil).forEach((merk) => {
    if (mfWadah(merk)) return;
    const h = hasil[merk]; const b = buka[merk];
    const L = [];
    if (b && b.sisaKg > 0) L.push({ tanggal: mfHariSebelum(mulai), id: 0, kg: b.sisaKg, harga: b.hppTerakhirPerKg || 0, asal: 'buka' });
    (baru[merk] || []).slice().sort((x, y) => String(x.tanggal).localeCompare(String(y.tanggal)) || (Number(x.id) || 0) - (Number(y.id) || 0))
      .forEach((x) => { if (x.kg > 0) L.push(x); });
    if (!L.length) return;
    const T = mfTotal(L); const S = h.sisaKg || 0; const P = T - S;
    const nilai = mfIrisan(L, P, T);
    h.hppRataPerKg = h.hppTerakhirPerKg;
    h.hppTerakhirPerKg = Math.abs(S) > 0.005 ? nilai / S : mfHargaDi(L, P);
    h.hppKeluarPerKg = mfHargaDi(L, P);
    h.metode = 'fifo'; h.fifoMulai = mulai; h.lapisan = L; h.posKeluar = P;
  });
  return hasil;
}

/** Modal rata-rata merek (angka lama) — dipakai isi wadah literan campuran model lama (owner 9 Okt: wadah campuran = rata-rata). */
export function modalRataPerKg(st) { return !st ? 0 : st.hppRataPerKg !== undefined ? st.hppRataPerKg : (st.hppTerakhirPerKg || 0); }

/**
 * Rupiah selisih hitung fisik (selisihKg = fisik − buku) satu merek karung. Kurang = barang keluar dari DEPAN antrean (yang terlama) → minus modal
 * irisan itu; lebih = barang kembali ke depan antrean → plus modal irisan tepat sebelum depan. Saklar mati = selisih × modal rata-rata (cara lama).
 */
export function nilaiSelisihKg(st, selisihKg, sudah) {
  const s = Number(selisihKg) || 0; if (!st || !s) return 0;
  if (st.metode !== 'fifo' || !Array.isArray(st.lapisan) || !st.lapisan.length) return s * (st.hppTerakhirPerKg || 0);
  const p = (st.posKeluar || 0) + (Number(sudah) || 0);   // sudah = kg yang sudah keluar lebih dulu di kiriman yang sama (minus = sudah kembali)
  return s < 0 ? -mfIrisan(st.lapisan, p, p - s) : mfIrisan(st.lapisan, p - s, p);
}
