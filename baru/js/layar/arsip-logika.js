// ARSIP PRODUK (putaran 27 Bagian 3, owner 27 Sep: merek yang habis dan tidak akan datang lagi perlu bisa disingkirkan dari layar).
// Penanda arsip = SATU dokumen setelan aturanToko/produkArsip { daftar: [{ kunci, jenis, nama, ukuran?, tanggal, jam }] } (keputusan owner 27 Sep).
// Kunci = skema peta tempat simpan sistem lama: 'K:<nama>' = nama karung/beras, 'M:<nama>|<ukuran>' = kemasan jadi.
//  · Hanya barang bersisa NOL yang bisa diarsipkan (stok bukan nol → sisanya disebut, arahnya cocokkan).
//  · Arsip MENYEMBUNYIKAN dari Jual (termasuk baris saring jenis), katalog harga, label, dan katalog HP kasir. Riwayat, laporan, dan buku stok TIDAK berubah
//    (tidak ada catatan bertanggal yang ditulis/dihapus). Layar "Produk arsip" di Harga & Pemasok memulihkan.
//  · Nama arsip yang datang lagi lewat barang masuk → layar bertanya dulu: pulihkan (sama barangnya) atau buat varian; adukan dengan hasil kemasan arsip
//    memulihkannya sendiri (disebut di kabar).
//  · HAPUS hanya untuk nama yang TIDAK PERNAH punya transaksi apa pun (mis. varian yang dibuat dari Harga tapi barangnya tidak jadi datang): yang dihapus
//    cuma setelan (katalog harga nama itu, jenis beras, draf/label/sengaja, arsip). Pernah bertransaksi → tidak ada tombol hapus, yang ada Arsipkan.
//  · Katalog HP kasir: nama arsip disaring dari HASIL susunIsiKatalogKasir (fungsi salinan tidak diubah) — lihat data/katalog-kasir.js.
// Tanpa DOM; nama berawalan ar (bundel uji satu lingkup). Dijaga alat-uji/uji_arsip_produk.py.
import { hitungStokKarungPerMerk, hitungStokKemasan } from '../mesin/beku.js';
import { kunciKemasan } from '../mesin/pembantu.js';
import { ambilSemuaBatch, ambilPenjualanSemua, ambilProduksi, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilRetur, ambilKarantina, ambilWadahLiteran,
  ambilHargaKarung, ambilHargaKemasan, ambilHargaLiteran, ambilPetaJenisBeras, cacheMentah } from '../data/toko.js';
import { RP } from '../inti/format.js';

export const AR_ID = 'produkArsip';
const arKG = (n) => String(Math.round(n * 100) / 100).replace('.', ',') + ' kg';
export const arKunciBeras = (nama) => 'K:' + String(nama || '');
export const arKunciKemasan = (nama, ukuran) => 'M:' + kunciKemasan(nama, ukuran);
const arDok = () => cacheMentah('aturan').find((d) => String(d.id) === AR_ID) || null;
/** Daftar nama yang diarsipkan (terbaru di belakang). */
export function arDaftar() { const d = arDok(); return Array.isArray(d && d.daftar) ? d.daftar.filter((x) => x && x.kunci) : []; }
/** Peta kunci → true, untuk saringan cepat. */
export function arPeta() { const o = {}; arDaftar().forEach((x) => { o[String(x.kunci)] = true; }); return o; }
export const arBeras = (nama, peta) => !!(peta || arPeta())[arKunciBeras(nama)];
export const arKemasan = (nama, ukuran, peta) => !!(peta || arPeta())[arKunciKemasan(nama, ukuran)];
/** Pecah kunci arsip → { jenis, nama, ukuran }. */
export function arUrai(kunci) {
  const k = String(kunci || ''); if (k.indexOf('K:') === 0) return { jenis: 'beras', nama: k.slice(2), ukuran: null };
  if (k.indexOf('M:') === 0) { const isi = k.slice(2); const i = isi.lastIndexOf('|'); return { jenis: 'kemasan', nama: isi.slice(0, i), ukuran: Number(isi.slice(i + 1)) }; }
  return { jenis: '', nama: k, ukuran: null };
}

/** Pernah punya TRANSAKSI apa pun (catatan bertanggal yang menyebut nama itu)? Setelan (katalog, jenis, tempat) bukan transaksi. */
export function arPernahTransaksi(kunci) {
  const u = arUrai(kunci); const n = u.nama;
  if (u.jenis === 'beras') {
    const diBatch = ambilSemuaBatch().some((b) => (b.merkList || []).some((m) => m.merk === n));
    const diJual = ambilPenjualanSemua().some((p) => p.merkSumber === n);
    const diProduksi = ambilProduksi().some((p) => p.merkSumber === n || p.merkTujuan === n || (p.sumberList || []).some((s) => s.merk === n));
    const diCocok = ambilPenyesuaianStok().some((o) => o.merk === n);
    const diRetur = ambilRetur().some((r) => r.merkSumber === n) || ambilKarantina().some((r) => r.merkSumber === n);
    const diWadah = ambilWadahLiteran().some((w) => w.merk === n || (w.sumber || []).some((x) => x.merk === n));
    return diBatch || diJual || diProduksi || diCocok || diRetur || diWadah;
  }
  if (u.jenis === 'kemasan') {
    const k = kunciKemasan(n, u.ukuran); const sama = (nama, ukuran) => kunciKemasan(nama, ukuran) === k;
    return ambilProduksi().some((p) => sama(p.namaProduk, p.ukuranKemasan) || (p.sumberKemasanList || []).some((s) => sama(s.namaProduk, s.ukuranKemasan)))
      || ambilPenjualanSemua().some((p) => p.jenis === 'kemasan' && sama(p.namaProduk, p.ukuranKemasan)) || ambilPenyesuaianKemasan().some((o) => sama(o.namaProduk, o.ukuranKemasan))
      || ambilRetur().some((r) => r.jenisAsal === 'kemasan' && sama(r.namaProduk, r.ukuranKemasan)) || ambilKarantina().some((r) => sama(r.namaProduk, r.ukuranKemasan));
  }
  return true;
}
/** Keadaan satu barang untuk tiga pilihan (Isi · Arsipkan · Hapus): sisa, nol, pernah transaksi, sudah arsip. */
export function arKeadaan(kunci) {
  const u = arUrai(kunci); let sisa = 0; let satuan = 'kg';
  if (u.jenis === 'beras') { const s = hitungStokKarungPerMerk()[u.nama]; sisa = s ? Math.round((s.sisaKg || 0) * 100) / 100 : 0; }
  else if (u.jenis === 'kemasan') { const s = hitungStokKemasan()[kunciKemasan(u.nama, u.ukuran)]; sisa = s ? s.sisaUnit || 0 : 0; satuan = 'unit'; }
  const nol = Math.abs(sisa) < 0.005; const pernah = arPernahTransaksi(kunci); const arsip = !!arPeta()[String(kunci)];
  return { kunci: String(kunci), jenis: u.jenis, nama: u.nama, ukuran: u.ukuran, judul: u.jenis === 'kemasan' ? u.nama + ' ' + String(u.ukuran).replace('.', ',') + ' kg' : u.nama, sisa, satuan, nol, pernah, arsip,
    bisaArsip: nol && !arsip, bisaHapus: !pernah, sisaTeks: satuan === 'kg' ? arKG(sisa) : sisa + ' unit' };
}
const arTulisDaftar = (daftar, w) => ({ koleksi: 'aturanToko', data: { id: AR_ID, tanggal: w.tanggal, jam: w.jam, daftar } });

/** ARSIPKAN: hanya kalau sisanya nol. Tidak ada catatan bertanggal yang ditulis — buku stok, riwayat, laporan tetap. */
export function arSusunArsip(kunci, w) {
  const K = arKeadaan(kunci); if (!K.jenis) return { tolak: 'Barangnya tidak dikenal' };
  if (K.arsip) return { tolak: K.judul + ' sudah diarsipkan' };
  if (!K.nol) return { tolak: K.judul + ' masih bersisa ' + K.sisaTeks + ' menurut buku — tidak bisa diarsipkan. Kalau di toko memang sudah habis, cocokkan dulu (Stok › Cocokkan), baru arsipkan.', cocok: K.jenis === 'beras' ? 'tumpukan|' + K.nama : 'kemasan|' + kunciKemasan(K.nama, K.ukuran) };
  const daftar = arDaftar().concat([Object.assign({ kunci: K.kunci, jenis: K.jenis, nama: K.nama, tanggal: w.tanggal, jam: w.jam }, K.ukuran !== null ? { ukuran: K.ukuran } : {})]);
  return { dokumen: [arTulisDaftar(daftar, w)], patch: { kabar: K.judul + ' diarsipkan — hilang dari Jual, katalog harga, label, dan katalog HP kasir. Riwayat, laporan, dan buku stok tetap. Pulihkan dari Harga & Pemasok › Produk arsip.', kabarAwas: false } };
}
/** PULIHKAN dari arsip (layar Produk arsip, atau barang masuk / adukan atas nama itu). */
export function arSusunPulih(kunci, w) {
  const ada = arDaftar().some((x) => String(x.kunci) === String(kunci)); if (!ada) return { tolak: 'Barang itu tidak ada di arsip' };
  const u = arUrai(kunci);
  return { dokumen: [arTulisDaftar(arDaftar().filter((x) => String(x.kunci) !== String(kunci)), w)], patch: { kabar: (u.jenis === 'kemasan' ? u.nama + ' ' + u.ukuran + ' kg' : u.nama) + ' dipulihkan dari arsip — tampil lagi di Jual, katalog harga, dan katalog HP kasir.', kabarAwas: false } };
}
/** Dokumen arsip SESUDAH beberapa kunci dipulihkan (dipakai barang masuk & adukan di kiriman yang sama). null = tidak ada yang berubah. */
export function arDokPulihBanyak(kunci, w) {
  const set = {}; (kunci || []).forEach((k) => { set[String(k)] = true; }); const lama = arDaftar(); const baru = lama.filter((x) => !set[String(x.kunci)]);
  return baru.length === lama.length ? null : arTulisDaftar(baru, w);
}
/**
 * HAPUS nama yang tidak pernah bertransaksi: dokumen katalog harga nama itu (per kg, per liter, kemasan/karung utuh ukuran itu — kecuali yang masih dipakai
 * barang lain senama), kunci jenis beras, draf/label/"sengaja" nama itu, dan arsipnya. Dua ketukan. Pernah bertransaksi → DITOLAK (arsipkan saja).
 */
export function arSusunHapus(kunci, w, yakin) {
  const K = arKeadaan(kunci); if (!K.jenis) return { tolak: 'Barangnya tidak dikenal' };
  if (K.pernah) return { tolak: K.judul + ' pernah punya transaksi — tidak bisa dihapus supaya riwayat & laporannya tetap utuh. Arsipkan saja kalau sudah tidak dijual.' };
  const hapus = []; const n = K.nama; const kem = hitungStokKemasan();
  if (K.jenis === 'beras') {
    ambilHargaKarung().filter((x) => x.merk === n).forEach((x) => hapus.push({ koleksi: 'katalogHargaKarung', id: x.id }));
    ambilHargaLiteran().filter((x) => x.merk === n).forEach((x) => hapus.push({ koleksi: 'katalogHargaLiteran', id: x.id }));
    // harga karung utuh 50/25 tinggal di katalog kemasan yang sama — dibuang hanya kalau tidak ada kemasan jadi senama ukuran itu
    ambilHargaKemasan().filter((x) => x.merk === n && !kem[kunciKemasan(n, x.ukuran)]).forEach((x) => hapus.push({ koleksi: 'katalogHargaKemasan', id: x.id }));
  } else ambilHargaKemasan().filter((x) => x.merk === n && Number(x.ukuran) === Number(K.ukuran)).forEach((x) => hapus.push({ koleksi: 'katalogHargaKemasan', id: x.id }));
  if (!yakin) return { tolak: 'Ketuk sekali lagi untuk MENGHAPUS ' + K.judul + ' — belum pernah ada transaksinya; yang dibuang cuma ' + (hapus.length ? hapus.length + ' harga di katalog' : 'namanya') + ' dan setelannya.', perluYakin: true };
  const dokumen = []; const awal = K.jenis === 'beras' ? n + '|' : n + '|K' + K.ukuran;
  const kenaKunci = (k) => (K.jenis === 'beras' ? String(k).indexOf(awal) === 0 && (/\|(S|L)$/.test(k) || !kem[kunciKemasan(n, Number(String(k).slice(awal.length + 1)))]) : String(k) === awal);
  const atur = (id) => cacheMentah('aturan').find((d) => String(d.id) === id) || null;
  const dd = atur('hargaDraf'); if (dd && dd.draf && Object.keys(dd.draf).some(kenaKunci)) { const d = Object.assign({}, dd.draf); Object.keys(d).forEach((k) => { if (kenaKunci(k)) delete d[k]; }); dokumen.push({ koleksi: 'aturanToko', data: { id: 'hargaDraf', tanggal: w.tanggal, jam: w.jam, draf: d } }); }
  const dl = atur('hargaLabel'); if (dl && Array.isArray(dl.daftar) && dl.daftar.some((x) => kenaKunci(x.k))) dokumen.push({ koleksi: 'aturanToko', data: { id: 'hargaLabel', tanggal: w.tanggal, jam: w.jam, daftar: dl.daftar.filter((x) => !kenaKunci(x.k)) } });
  const ds = atur('hargaSengaja'); if (ds && ds.peta && Object.keys(ds.peta).some(kenaKunci)) { const p = Object.assign({}, ds.peta); Object.keys(p).forEach((k) => { if (kenaKunci(k)) delete p[k]; }); dokumen.push({ koleksi: 'aturanToko', data: { id: 'hargaSengaja', tanggal: w.tanggal, jam: w.jam, peta: p } }); }
  if (K.jenis === 'beras') { const peta = ambilPetaJenisBeras(); const masihKemasan = Object.keys(kem).some((k) => kem[k].namaProduk === n);
    if (Object.prototype.hasOwnProperty.call(peta, n) && !masihKemasan) { delete peta[n]; dokumen.push({ koleksi: 'pengaturan', data: { id: 'jenisBeras', peta, diubahPada: w.kini } }); } }
  const da = arDokPulihBanyak([K.kunci], w); if (da) dokumen.push(da);
  return { dokumen, hapus, patch: { kabar: K.judul + ' dihapus (' + (hapus.length ? hapus.length + ' harga katalog' : 'tanpa harga katalog') + ' + setelannya) — tidak pernah ada transaksinya, jadi riwayat & laporan tidak berubah.', kabarAwas: false } };
}

/**
 * SARINGAN katalog HP kasir: buang baris nama arsip dari HASIL susunIsiKatalogKasir (fungsi salinan index.html tidak diubah). Nama arsip selalu bersisa nol,
 * jadi hasilnya = katalog seandainya nama itu tidak pernah ada. Menyaring DATA sebelum penyusun tidak aman: satu produksiKemasan membawa beberapa nama
 * (sumberList), membuang dokumennya ikut mengubah stok nama lain (docs/peta-stok-merek.md §9).
 */
export function arSaringKatalogKasir(isi, peta) {
  if (!isi) return isi; const p = peta || arPeta(); if (!Object.keys(p).length) return isi;
  return Object.assign({}, isi, { kemasan: (isi.kemasan || []).filter((k) => !p['M:' + k.kunci]), merkKarung: (isi.merkKarung || []).filter((m) => !p[arKunciBeras(m.merk)]) });
}
/** Apakah baris katalog harga (merek + satuan) disembunyikan arsip? Karung utuh (K50/K25) & kemasan berbagi dokumen katalog kemasan yang sama → baris K<u>
 *  disembunyikan hanya kalau SEMUA pemakainya diarsipkan/tidak ada (kemasan senama ukuran itu, dan karung nama itu). */
export function arSembunyiHarga(merk, sid, peta) {
  const p = peta || arPeta(); const berasArsip = !!p[arKunciBeras(merk)];
  if (sid === 'S' || sid === 'L') return berasArsip;
  const u = Number(String(sid).slice(1)); const kem = hitungStokKemasan()[kunciKemasan(merk, u)]; const kemAktif = !!kem && !p[arKunciKemasan(merk, u)];
  const karungAktif = !!hitungStokKarungPerMerk()[merk] && !berasArsip;
  return !kemAktif && !karungAktif && (berasArsip || !!p[arKunciKemasan(merk, u)]);
}
/** Ringkasan untuk layar Produk arsip. */
export function arRingkas() { return arDaftar().map((x) => Object.assign({}, arKeadaan(x.kunci), { sejak: x.tanggal || '' })); }
export const arTeksSisa = (K) => (K.nol ? 'habis' : 'sisa ' + K.sisaTeks) + (K.pernah ? '' : ' · belum pernah bertransaksi') + (K.arsip ? ' · diarsipkan' : '');
