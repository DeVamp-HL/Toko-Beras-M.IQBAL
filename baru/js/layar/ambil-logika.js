// KARCIS AMBIL NANTI (owner 26 Nov 2026, paket QR kedua, rules v23). Logika TANPA DOM, nama berawalan ab. Dijaga alat-uji/uji_ambil_barang.py.
//
// Pembeli bayar sekarang, barang (karung / kemasan) diambil belakangan — boleh sebagian-sebagian. Keputusan owner: STOK BERKURANG SAAT BAYAR (nota & stok buku
// seperti biasa) + DAFTAR TITIPAN supaya hitung fisik / opname tidak menganggap barang yang masih di toko sebagai selisih. Struk nota itu = karcisnya: scan →
// "Serahkan barang titipan".
// Koleksi ambilBarang (rules v23), TAMBAH-SAJA: 'titip' (ditulis bersama nota: tiap baris karung/kemasan = { idBaris, jenis, nama, jumlah, satuan }) dan 'ambil'
// (barang yang diserahkan: { idBaris, jumlah }). Catatannya BERDIRI SENDIRI (nama & jumlah ikut disalin) — nota bisa diarsip tutup buku, titipannya tetap terbaca.
// Tidak ada rupiah, tidak menyentuh stok & uang (mesin beku tidak membaca koleksi ini).
import { cacheMentah, ambilPenjualanSemua } from '../data/toko.js';
import { formatTanggal } from '../mesin/pembantu.js';

export const AB_KOLEKSI = 'ambilBarang';
/** Kolom yang ditulis penyusun (penulis pusat menambah atribusi) — wajib bagian dari stafAmbilBarang rules v23 (dijaga periksa_rules). */
export const AB_KOLOM = ['id', 'tanggal', 'jam', 'jenis', 'trxId', 'namaPelanggan', 'isi', 'catatan'];
export const AB_BARIS_MAKS = 20;
const abAngka = (v) => Math.round((Number(v) || 0) * 100) / 100;
const abSatuan = (j) => (j === 'karung' ? 'karung' : 'kemasan');
/** Nama barang satu baris nota (bentuk ringkas, tanpa impor struk-logika — struk mengimpor modul ini). */
export function abNamaBaris(p) {
  if (!p) return '';
  if (p.jenis === 'karung') return String(p.merkSumber || p.namaProduk || 'Karung').replace(/ \(karung utuh\)$/, '') + ' karung ' + (p.beratKarungAcuan || 50) + ' kg';
  return String(p.namaProduk || 'Kemasan') + (p.ukuranKemasan ? ' ' + String(p.ukuranKemasan).replace('.', ',') + ' kg' : '');
}
/** Baris nota yang ikut dititip: karung & kemasan (bukan pengganti retur, jumlah > 0). Literan / repack / wadah ditakar & diserahkan saat itu juga. */
export function abIsiTitip(barisNota) {
  return (barisNota || []).filter((p) => p && (p.jenis === 'karung' || p.jenis === 'kemasan') && !p.penggantiRetur)
    .sort((a, b) => (Number(a.id) || 0) - (Number(b.id) || 0))   // urutan keranjang (id baris naik) — struk & lembar serahkan berurutan sama dengan notanya
    .map((p) => ({ idBaris: String(p.id), jenis: p.jenis, nama: abNamaBaris(p).slice(0, 80), jumlah: abAngka(p.jenis === 'karung' ? p.jumlahKarung : p.jumlahUnit), satuan: abSatuan(p.jenis) }))
    .filter((x) => x.jumlah > 0).slice(0, AB_BARIS_MAKS);
}
/** Id dokumen = kolom id (rules v23: d.id == id dokumen). */
const abId = (w) => 'ab-' + String(w.idUnik()).replace(/[^0-9a-zA-Z]/g, '-');
/** Dokumen titipan untuk satu nota (ditulis BERSAMA notanya). */
export function abSusunTitip(trxId, nama, isi, w) {
  return { koleksi: AB_KOLEKSI, data: { id: abId(w), tanggal: w.tanggal, jam: w.jam, jenis: 'titip', trxId: String(trxId), namaPelanggan: String(nama || '').trim().slice(0, 60), isi, catatan: '' } };
}
const abSemua = () => (cacheMentah('ambilBarang') || []).filter((d) => d && (d.jenis === 'titip' || d.jenis === 'ambil'));
/** Nota titipan yang SUDAH DIBATALKAN (semua barisnya ada di data & dibatalkan) — barangnya kembali ke toko, titipannya gugur. Nota yang sudah diarsip tutup buku
 *  (barisnya tidak ada lagi) TIDAK dianggap batal: titipannya tetap. */
export function abNotaBatal(trxId) { const r = (ambilPenjualanSemua() || []).filter((p) => String(p.trxId) === String(trxId)); return r.length > 0 && r.every((p) => p.dibatalkan); }
/**
 * Keadaan titipan satu nota. null = nota ini tidak dititip. { trxId, nama, tanggal, jam, isi: [{ idBaris, nama, satuan, jumlah, diambil, sisa }], sisa (Σ, satuan
 * campur → hanya "ada / tidak"), habis (semua sudah diambil), riwayat: [{ tanggal, jam, teks, oleh }] }.
 */
export function abKeadaan(trxId) {
  const t = String(trxId || ''); if (!t) return null; const S = abSemua().filter((d) => String(d.trxId) === t);
  const titip = S.filter((d) => d.jenis === 'titip').sort((a, b) => String(a.id).localeCompare(String(b.id)))[0]; if (!titip) return null;
  const ambil = S.filter((d) => d.jenis === 'ambil').sort((a, b) => String(a.tanggal + ' ' + (a.jam || '')).localeCompare(String(b.tanggal + ' ' + (b.jam || ''))));
  const diambil = {}; ambil.forEach((d) => (d.isi || []).forEach((x) => { const k = String(x.idBaris); diambil[k] = abAngka((diambil[k] || 0) + abAngka(x.jumlah)); }));
  const isi = (titip.isi || []).map((x) => { const d = Math.min(abAngka(x.jumlah), diambil[String(x.idBaris)] || 0); return { idBaris: String(x.idBaris), nama: String(x.nama || ''), satuan: String(x.satuan || ''), jumlah: abAngka(x.jumlah), diambil: d, sisa: abAngka(abAngka(x.jumlah) - d) }; });
  const nm = (id) => (isi.find((x) => x.idBaris === String(id)) || {}).nama || 'barang';
  const riwayat = ambil.map((d) => ({ tanggal: d.tanggal, jam: d.jam || '', oleh: d.oleh || '', teks: (d.isi || []).map((x) => nm(x.idBaris) + ' ' + String(abAngka(x.jumlah)).replace('.', ',')).join(', ') + (d.catatan ? ' · ' + d.catatan : '') }));
  return { trxId: t, nama: titip.namaPelanggan || '', tanggal: titip.tanggal || '', jam: titip.jam || '', isi, sisa: isi.reduce((a, x) => a + x.sisa, 0), habis: isi.every((x) => x.sisa <= 0), riwayat, batal: abNotaBatal(t) };
}
/** Semua titipan yang masih ada barangnya, tertua dulu. */
export function abDaftar() {
  const ids = []; abSemua().filter((d) => d.jenis === 'titip').forEach((d) => { if (ids.indexOf(String(d.trxId)) < 0) ids.push(String(d.trxId)); });
  return ids.map(abKeadaan).filter((k) => k && !k.habis && !k.batal).sort((a, b) => String(a.tanggal + ' ' + a.jam).localeCompare(String(b.tanggal + ' ' + b.jam)));
}
/** Barang titipan yang masih di toko per nama barang (untuk hitung fisik / opname): [{ nama, satuan, jumlah, nota }]. */
export function abRingkasBarang() {
  const per = {}; abDaftar().forEach((k) => k.isi.forEach((x) => { if (x.sisa <= 0) return; const kk = x.nama + '|' + x.satuan; const p = per[kk] || (per[kk] = { nama: x.nama, satuan: x.satuan, jumlah: 0, nota: 0 }); p.jumlah = abAngka(p.jumlah + x.sisa); p.nota += 1; }));
  return Object.keys(per).map((k) => per[k]).sort((a, b) => a.nama.localeCompare(b.nama));
}
/** Teks jumlah: "3 karung" · "1,5 karung" · "2 kemasan". */
export const abJumlahTeks = (n, satuan) => String(abAngka(n)).replace('.', ',') + ' ' + satuan;
/**
 * Serahkan barang titipan. jumlah = { idBaris: angka } (yang tidak diisi / 0 = tidak diambil). Ditolak: titipan tidak ada, tidak ada yang diambil, melebihi sisa,
 * karung bukan kelipatan ½, kemasan bukan bilangan bulat. Hasil { dokumen, patch } | { tolak }.
 */
export function abSusunAmbil(trxId, jumlah, w, catatan) {
  const K = abKeadaan(trxId); if (!K) return { tolak: 'Nota ini tidak punya barang titipan' };
  if (K.batal) return { tolak: 'Nota titipan ini sudah dibatalkan — barangnya bukan titipan lagi' };
  if (K.habis) return { tolak: 'Semua barang titipan nota ini sudah diambil' };
  const isi = []; let tolak = '';
  K.isi.forEach((x) => { const n = abAngka(String((jumlah || {})[x.idBaris] === undefined ? '' : jumlah[x.idBaris]).replace(',', '.')); if (!(n > 0) || tolak) return;
    if (n > x.sisa + 1e-9) { tolak = x.nama + ': diambil ' + abJumlahTeks(n, x.satuan) + ', sisa titipan ' + abJumlahTeks(x.sisa, x.satuan); return; }
    if (x.satuan === 'karung' ? (n * 2) % 1 !== 0 : n % 1 !== 0) { tolak = x.nama + ': ' + (x.satuan === 'karung' ? 'karung diambil utuh atau setengah (0,5 · 1 · 1,5 …)' : 'kemasan diambil per unit'); return; }
    isi.push({ idBaris: x.idBaris, jumlah: n }); });
  if (tolak) return { tolak };
  if (!isi.length) return { tolak: 'Isi jumlah barang yang diambil dulu' };
  const sisaSesudah = K.isi.map((x) => { const a = isi.find((y) => y.idBaris === x.idBaris); return Object.assign({}, x, { sisa: abAngka(x.sisa - (a ? a.jumlah : 0)) }); });
  const habis = sisaSesudah.every((x) => x.sisa <= 0);
  const data = { id: abId(w), tanggal: w.tanggal, jam: w.jam, jenis: 'ambil', trxId: K.trxId, namaPelanggan: K.nama, isi, catatan: String(catatan || '').trim().slice(0, 160) };
  return { dokumen: [{ koleksi: AB_KOLEKSI, data }], habis,
    patch: { kabar: 'Barang titipan ' + (K.nama || 'tanpa nama') + ' diserahkan: ' + isi.map((y) => { const x = K.isi.find((z) => z.idBaris === y.idBaris); return x.nama + ' ' + abJumlahTeks(y.jumlah, x.satuan); }).join(', ')
      + (habis ? ' — titipan nota ini HABIS' : ' — sisa: ' + sisaSesudah.filter((x) => x.sisa > 0).map((x) => x.nama + ' ' + abJumlahTeks(x.sisa, x.satuan)).join(', ')), kabarAwas: false } };
}
/** Baris struk untuk nota yang dititip (catatan, tanpa angka rupiah) — dicetak SAAT struk disusun. [] = bukan titipan. */
export function abBarisStruk(trxId) {
  const K = abKeadaan(trxId); if (!K || K.batal) return [];
  if (K.habis) return ['Barang titipan sudah diambil semua' + (K.riwayat.length ? ' (' + formatTanggal(K.riwayat[K.riwayat.length - 1].tanggal) + ')' : '')];
  return ['DITITIP DI TOKO — ambil dengan struk ini:'].concat(K.isi.filter((x) => x.sisa > 0).map((x) => '  ' + x.nama + ' ' + abJumlahTeks(x.sisa, x.satuan) + (x.diambil > 0 ? ' (dari ' + abJumlahTeks(x.jumlah, x.satuan) + ')' : '')));
}
