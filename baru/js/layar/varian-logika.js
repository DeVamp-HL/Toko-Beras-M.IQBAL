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
import { ambilHargaKarung, ambilPetaJenisBeras, cacheMentah, ambilSemuaBatch, ambilPenjualan, ambilProduksiBerlaku, ambilRetur, ambilPenyesuaianStok, tolakKunci, denganCacheSementara, ingatStokKarung } from '../data/toko.js';
import { RP, tanggalPendek } from '../inti/format.js';
// owner 7 Okt: varian yang lahir dari stok induk — buku lahir & pindah buku (modal ikut) memakai pintu yang sama dengan wadah / buku per ukuran
import { wbNamaKelas, wbDokLahir, wbDokPindah } from './wadah-bernama-logika.js';

export const VR_PEMISAH = ' · ';
export const VR_BATAS_BAWAAN = 5;   // % beda harga beli vs modal berjalan yang memicu pertanyaan (owner mengatur di Stok › Barang masuk › Atur)
const VR_BLN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
const vrBersih = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const vrBulatAtas = (x, k) => (k > 0 ? Math.ceil(x / k - 1e-9) * k : Math.round(x));
const vrB2 = (n) => Math.round(n * 100) / 100;
// owner 7 Okt: paling banyak sekian kedatangan dikoreksi dalam satu kiriman (tiap kedatangan bulan lampau = satu pemeriksaan kunci di server, batas 18)
const VR_KOREKSI_MAKS = 10;
const vrKG = (n) => String(vrB2(n)).replace('.', ',') + ' kg';

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
  const st = ingatStokKarung()[String(merk || '')]; const h = Number(hargaPerKg) || 0; const batas = vrBatas();
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
export const vrAda = (nama) => !!ingatStokKarung()[nama] || ambilHargaKarung().some((h) => h.merk === nama);

/**
 * TERBITKAN harga jual per kg SATU varian (tawaran sesudah barang masuk, atau varian baru dari Harga): dokumen katalogHargaKarung bentuk
 * simpanHargaKarung + modalSaatSetel, catatan hargaTerbit, tugas label, dan draf nama itu (kalau ada) dibuang — draf harga lain TIDAK ikut terbit.
 * Di bawah modal = dua ketukan. Layar menambahkan katalog HP kasir di kiriman yang sama (kkSertakan).
 */
export function vrSusunTerbitHarga(varian, hargaKetik, w, yakin, modalDari) {
  const nama = vrBersih(varian); const n = Math.round(Number(String(hargaKetik === undefined || hargaKetik === null ? '' : hargaKetik).replace(/\./g, '').replace(',', '.')) || 0);
  if (!nama) return { tolak: 'Nama variannya kosong' };
  if (!(n >= 1000)) return { tolak: 'Harga jual per kg belum benar — ketik rupiahnya (mis. 16.000)' };
  // owner 7 Okt: varian yang lahir dari stok induk (vrSusunBuatDariHarga, bawa) — modalnya = modal stok induk yang ikut pindah (bukunya baru terisi di kiriman ini)
  const st = hitungStokKarungPerMerk()[modalDari ? vrBersih(modalDari) : nama]; const modal = st ? st.hppTerakhirPerKg || 0 : 0;
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
  const ind = vrBersih(induk); if (!ind) return ''; const st = ingatStokKarung()[ind]; const sisa = st ? Number(st.sisaKg) || 0 : 0; if (!(sisa > 0.05)) return '';
  const perKg = cariHargaKarungPerKg(ind); const utuh = hargaKarungUtuh(ind, 50) || hargaKarungUtuh(ind, 25); if ((perKg !== null && perKg > 0) || (utuh && utuh.perUnit > 0)) return '';
  return ind + ' punya stok ' + String(Math.round(sisa * 10) / 10).replace('.', ',') + ' kg tapi BELUM ada harga jual — stok itu tetap atas nama ' + ind + ' dan tidak tampil di Jual. Kalau barangnya SAMA, setel harga ' + ind + ' di katalog (bukan varian). Varian = nama BARU yang stoknya 0 sampai ada barang masuk atas nama varian itu.';
}
/** Pilihan merek induk untuk varian baru dari layar Harga: bukan nama varian, bukan nama wadah / kelas mutu (yang itu ditolak saat dibuat). */
export function vrCalonInduk(daftar) { const kelas = wbNamaKelas(); return (daftar || []).filter((m) => String(m).indexOf(VR_PEMISAH) < 0 && !kelas[m]); }
/**
 * GERAK BUKU satu nama (tinjauan E1 — satu tempat untuk "buku ini sudah bergerak", dipakai varian dari Harga & koreksi kedatangan): catatan selain kedatangan yang
 * memotong / mengisi buku nama itu, dari sumber yang sama dengan mesin beku — penjualan yang berlaku (merkSumber), adukan & pindah buku (produksi berlaku: sumber
 * atau tujuan), retur, cocokkan (penyesuaianStok). sejak = 'YYYY-MM-DD' (inklusif): hanya catatan bertanggal itu atau sesudahnya; '' = semua.
 * → daftar kata ('terjual', 'diaduk / dipindah buku', 'diretur', 'dicocokkan'); kosong = bukunya belum bergerak.
 */
export function vrGerakBuku(nama, sejak) {
  const ind = vrBersih(nama); if (!ind) return [];
  const t = (x) => !sejak || String((x && x.tanggal) || '') >= String(sejak); const out = [];
  if (ambilPenjualan().some((p) => p && p.merkSumber === ind && t(p))) out.push('terjual');
  if (ambilProduksiBerlaku().some((p) => p && t(p) && (p.merkSumber === ind || p.merkTujuan === ind || (Array.isArray(p.sumberList) && p.sumberList.some((x) => x && x.merk === ind))))) out.push('diaduk / dipindah buku');
  if (ambilRetur().some((r) => r && r.merkSumber === ind && t(r))) out.push('diretur');
  if (ambilPenyesuaianStok().some((o) => o && o.merk === ind && t(o))) out.push('dicocokkan');
  return out;
}
/**
 * STOK INDUK SAAT VARIAN DIBUAT (owner 7 Okt, kejadian nyata: barang masuk diketik "FJN", lalu "+ Varian merek baru" FJN · Imperial — stoknya tetap di FJN,
 * varian kosong: stok BERCABANG diam-diam). Bacaan buku induk untuk pertanyaan "stok itu ikut jadi varian?":
 *  · sisa, dan kedatangan nyata yang memuat nama induk (tanggal, pemasok, karung, kg);
 *  · UTUH = buku induk hanya berisi kedatangan itu (tidak ada jual / adukan / pindah buku / retur / cocokkan / stok awal atas namanya, sisa = Σ kg kedatangan,
 *    tidak ada yang di bulan terkunci) → kedatangannya bisa DIKOREKSI menjadi nama varian: stok, modal, riwayat harga beli & pemasok ikut varian;
 *  · tidak utuh → stoknya PINDAH BUKU ke varian (modal rata-rata ikut), kedatangan lama tetap atas nama induk. sebab = kalimat kenapa tidak utuh.
 * Bacaan keluar/masuk memakai sumber yang sama dengan mesin beku (penjualan & adukan yang masih berlaku, retur, cocokkan).
 */
export function vrStokInduk(induk) {
  const ind = vrBersih(induk); const st = ind ? hitungStokKarungPerMerk()[ind] : null; const sisa = st ? vrB2(Number(st.sisaKg) || 0) : 0;
  const datang = []; let kgMasuk = 0; let fondasi = false; let terkunci = '';
  if (ind) ambilSemuaBatch().forEach((b) => { const brs = (b.merkList || []).filter((m) => m && m.merk === ind && m.bentuk !== 'bal'); if (!brs.length) return;
    const kg = brs.reduce((a, m) => a + (Number(m.totalKg) || 0), 0);
    if (b.stokAwal || b.tutupBuku || b.lahirBuku) { if (kg > 0.004) fondasi = true; return; }
    kgMasuk += kg; const t = tolakKunci('batchMasuk', b, ''); if (t && !terkunci) terkunci = t;
    datang.push({ id: b.id, tanggal: String(b.tanggal || ''), pemasok: String(b.pemasok || '').trim(), karung: brs.reduce((a, m) => a + (Number(m.jumlahKarung) || 0), 0), kg: vrB2(kg) }); });
  datang.sort((a, b) => a.tanggal.localeCompare(b.tanggal) || (Number(a.id) || 0) - (Number(b.id) || 0));
  const dipakai = !!ind && vrGerakBuku(ind, '').length > 0;
  const sebab = !(sisa > 0.004) ? 'stoknya kosong' : !datang.length ? 'belum pernah ada kedatangan atas nama ini' : fondasi ? 'sebagian dari stok awal / saldo pembuka' : dipakai ? 'sudah ada yang terjual, diaduk, dipindah, diretur, atau dicocokkan'
    : Math.abs(kgMasuk - sisa) >= 0.01 ? 'sisa buku tidak sama dengan jumlah kedatangannya' : terkunci ? 'kedatangannya di bulan yang sudah dikunci'
    : datang.length > VR_KOREKSI_MAKS ? 'kedatangannya lebih dari ' + VR_KOREKSI_MAKS + ' — terlalu banyak dikoreksi sekaligus' : '';
  return { induk: ind, sisa, modal: st ? Number(st.hppTerakhirPerKg) || 0 : 0, datang, utuh: !sebab, sebab, teksDatang: datang.map((d) => tanggalPendek(d.tanggal) + (d.pemasok ? ' · ' + d.pemasok : '') + ' · ' + d.karung + ' karung').join('; ') };
}
/** Kalimat pilihan "stok induk ikut jadi varian" untuk layar (bawa = 'bawa' | 'kosong' | ''). '' = induk tanpa stok, tidak perlu ditanya. */
export function vrKalimatBawa(induk, nama, bawa) {
  const S = vrStokInduk(induk); if (!(S.sisa > 0.004)) return '';
  if (bawa === 'bawa') return S.utuh ? 'Kedatangan ' + S.teksDatang + ' dikoreksi jadi nama ' + nama + ': stok ' + vrKG(S.sisa) + ', modal, riwayat harga beli & pemasoknya ikut. Nilai stok & laba tidak berubah.'
    : vrKG(S.sisa) + ' pindah buku ' + S.induk + ' → ' + nama + ', modal rata-rata ' + RP(Math.round(S.modal)) + '/kg ikut. Kedatangan lama tetap atas nama ' + S.induk + ' (' + S.sebab + '). Nilai stok & laba tidak berubah.';
  if (bawa === 'kosong') return vrPeringatanInduk(induk) || 'Stok ' + vrKG(S.sisa) + ' tetap atas nama ' + S.induk + ' dan dijual sebagai ' + S.induk + '; ' + nama + ' mulai dari barang masuk atas nama varian.';
  return S.induk + ' masih punya stok ' + vrKG(S.sisa) + (S.datang.length ? ' (datang ' + S.teksDatang + ')' : '') + '. Barang itu = ' + nama + '?';
}
/**
 * Dokumen "stok induk IKUT jadi varian" (owner 7 Okt) — satu pintu untuk varian baru maupun varian yang sudah ada dengan buku kosong:
 *  · buku induk UTUH → kedatangan dikoreksi: baris atas nama induk → nama varian (baris lain, uang, pemasok, tanggal tidak berubah); jejak koreksi seperti
 *    Buku kedatangan › koreksi; + buku induk TETAP ADA lewat baris lahir 0 kg (tinjauan E1: tanpa baris batch, mesin beku melewatkan penjualan/adukan/retur/
 *    cocokkan atas nama induk — catatan yang tiba sesudah kiriman ini dari perangkat dengan cache lama, keranjang parkir, atau kiriman tertunda lenyap dari stok;
 *    dengan buku 0 kg catatan itu membuat induk MINUS yang terlihat);
 *  · selain itu → buku varian lahir (supaya mesin memotong penjualannya; dilewati bila sudah punya baris batch) lalu pindah buku seluruh sisa induk, modal ikut.
 */
function vrDokIkut(ind, nama, S, w) {
  const dokumen = [];
  if (S.utuh) {
    const alasan = 'jadi varian ' + nama + ' (Harga › Varian merek, stok ' + ind + ' ikut)';
    S.datang.forEach((d) => { const lama = ambilSemuaBatch().find((b) => String(b.id) === String(d.id)); if (!lama) return;
      dokumen.push({ koleksi: 'batchMasuk', data: Object.assign({}, lama, { merkList: (lama.merkList || []).map((x) => (x && x.merk === ind && x.bentuk !== 'bal' ? Object.assign({}, x, { merk: nama }) : x)),
        alasanKoreksi: alasan, riwayat: (Array.isArray(lama.riwayat) ? lama.riwayat : []).concat([{ teks: 'dikoreksi: ' + alasan, tanggal: w.tanggal, jam: w.jam }]) }) }); });
    // buku induk dilahirkan ulang (0 kg) DIHITUNG SESUDAH koreksi diterapkan sementara: wbDokLahir melewati nama yang masih tertulis di batch mana pun,
    // dan sebelum koreksi nama induk masih tertulis di kedatangan yang sedang dikoreksi. Induk yang sudah punya baris lahir 0 kg → tidak ditulis lagi.
    const lahirInduk = denganCacheSementara(dokumen, () => wbDokLahir([{ merk: ind }], w)); if (lahirInduk) dokumen.push(lahirInduk);
    return { dokumen, ket: ' Stok ' + ind + ' ' + vrKG(S.sisa) + ' ikut: kedatangan ' + S.teksDatang + ' dikoreksi jadi ' + nama + ' (riwayat harga beli & pemasok ikut; buku ' + ind + ' tetap ada, 0 kg).' };
  }
  const lahir = wbDokLahir([{ merk: nama }], w); if (lahir) dokumen.push(lahir);
  dokumen.push(wbDokPindah([{ merk: ind, kg: S.sisa }], nama, w, { jadiVarian: { induk: ind, varian: nama }, keterangan: 'Jadi varian: ' + vrKG(S.sisa) + ' ' + ind + ' → ' + nama + ' (Harga › Varian merek)' }));
  return { dokumen, ket: ' Stok ' + ind + ' ' + vrKG(S.sisa) + ' pindah buku ke ' + nama + ', modal ikut (' + S.sebab + ' — kedatangan lama tetap atas nama ' + ind + ').' };
}
/** Varian yang SUDAH ADA (katalog / buku) dengan buku kosong, sedangkan induknya berstok — bentuk stok bercabang yang terlanjur terjadi; stok induk bisa dipindah ke sana. */
export function vrBisaIkutKeAda(induk, nama) {
  const nm = vrBersih(nama); if (!nm || !vrAda(nm)) return false; const sv = hitungStokKarungPerMerk()[nm];
  return !(sv && Math.abs(Number(sv.sisaKg) || 0) > 0.004) && vrStokInduk(induk).sisa > 0.004;
}
/**
 * VARIAN dari Harga. bawa (owner 7 Okt) WAJIB dijawab bila induk masih berstok: 'bawa' = stok induk ikut jadi varian DI KIRIMAN YANG SAMA (vrDokIkut, modal ikut);
 * 'kosong' = varian mulai kosong (stok tetap atas nama induk — dipilih sadar, bukan diam-diam). Nama varian yang SUDAH ADA: ditolak seperti dulu, kecuali bukunya
 * kosong dan induk berstok — maka hanya 'bawa' yang berlaku (stok dipindah, harga katalognya tidak diubah).
 */
export function vrSusunBuatDariHarga(induk, mutu, hargaKetik, w, yakin, bawa) {
  const ind = vrBersih(induk); const m = vrBersih(mutu);
  if (!ind || !vrAda(ind)) return { tolak: 'Pilih dulu merek induknya (nama yang sudah ada di buku atau katalog)' };
  if (wbNamaKelas()[ind.split(VR_PEMISAH)[0]]) return { tolak: ind + ' itu nama WADAH / kelas mutu, bukan merek karung — varian dibuat dari merek yang tertera di karung' };   // putaran 27 (Bagian 5)
  if (!m) return { tolak: 'Tulis nama mutunya (mis. Premium) — varian dari layar Harga harus bernama' };
  if (m.indexOf('·') >= 0) return { tolak: 'Nama mutu tidak boleh memakai titik tengah' };
  const nama = vrNama(ind, m, w.tanggal); const pilih = bawa === 'bawa' || bawa === 'kosong' ? bawa : '';
  if (vrAda(nama)) {
    if (!vrBisaIkutKeAda(ind, nama)) return { tolak: nama + ' sudah ada — ubah harganya di katalog seperti biasa' };
    const S0 = vrStokInduk(ind);
    if (pilih !== 'bawa') return { tolak: nama + ' sudah ada dengan buku kosong, sedangkan ' + ind + ' masih punya stok ' + vrKG(S0.sisa) + (S0.datang.length ? ' (datang ' + S0.teksDatang + ')' : '') + '. Kalau barang itu = ' + nama + ', pilih "Ya — stok ikut" untuk memindahkannya (harga katalognya tidak diubah).', perluBawa: true, sudahAda: true };
    const P0 = vrDokIkut(ind, nama, S0, w);
    return { dokumen: P0.dokumen, patch: { vrBaru: null, vrYakin: false, kabarAwas: false, kabar: nama + ' sudah ada — tidak dibuat ulang, harganya tidak diubah.' + P0.ket + ' Nilai stok & laba tidak berubah.' } };
  }
  const S = vrStokInduk(ind);
  if (S.sisa > 0.004 && !pilih) return { tolak: ind + ' masih punya stok ' + vrKG(S.sisa) + (S.datang.length ? ' (datang ' + S.teksDatang + ')' : '') + '. Pilih dulu: stok itu IKUT jadi ' + nama + ', atau varian kosong untuk kedatangan berikutnya (stok tetap atas nama ' + ind + ').', perluBawa: true };
  const ikut = S.sisa > 0.004 && pilih === 'bawa';
  const r = vrSusunTerbitHarga(nama, hargaKetik, w, yakin, ikut ? ind : ''); if (r.tolak) return r;
  const jenis = vrDokJenis([{ varian: nama, induk: ind }], w); if (jenis) r.dokumen.push(jenis);
  let ketIkut = '';
  if (ikut) { const P = vrDokIkut(ind, nama, S, w); P.dokumen.forEach((d) => r.dokumen.push(d)); ketIkut = P.ket; }
  else if (S.sisa > 0.004) ketIkut = ' Stok ' + ind + ' ' + vrKG(S.sisa) + ' tetap atas nama ' + ind + ' (dipilih: varian kosong).';
  if (ikut && ambilHargaKarung().some((h) => h.merk === ind)) ketIkut += ' Harga jual ' + ind + ' di katalog tidak diubah (bukunya kini kosong) — arsipkan kalau nama itu tidak dipakai lagi.';
  r.patch = Object.assign({}, r.patch, { vrBaru: null, kabar: 'Varian ' + nama + ' dibuat (jenis beras ikut ' + ind + ': ' + (jenisUntukMerk(ind) || 'belum diisi') + ').' + ketIkut + ' ' + r.patch.kabar + (ikut ? ' Nilai stok & laba tidak berubah.' : ' Stoknya mulai dari barang masuk atas nama ini.') });
  return r;
}
