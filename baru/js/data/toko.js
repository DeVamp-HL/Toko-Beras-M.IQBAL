// Lapisan DATA sistem baru: satu tempat memegang salinan koleksi Firestore di memori.
// Mesin beku (js/mesin/beku.js) membaca lewat fungsi ambil*() di bawah — nama dan bentuknya
// sama persis dengan index.html supaya tubuh mesin tidak perlu berubah satu byte pun.
//
// Yang berbeda dari index.html, dan sengaja:
//  - tidak ada cadangan localStorage buatan sendiri (kompresi LZ, kuota ±62 KB/hari); jalan tanpa
//    internet diserahkan ke cache tetap Firestore (IndexedDB) di js/data/firebase.js;
//  - keranjang aktif & yang diparkir disetel oleh layar lewat setelKeranjang(), bukan variabel global.
import { KOLEKSI } from './koleksi.js';
import { penjualanMasihBerlaku, produksiMasihBerlaku, wzJumlahDiDaftar } from '../mesin/pembantu.js';

const _cache = {};
KOLEKSI.forEach((k) => { _cache[k.cache] = []; });
const _pendengar = new Set();
const _sumber = { jenis: 'belum', keterangan: 'belum ada data' };   // 'firestore' | 'cadangan' | 'belum'

// Terbaru dulu — salinan urutkanTerbaru() index.html (bentuk sama, supaya urutan dokumen di cache sama).
function urutkanTerbaru(arr, field) {
  return [...arr].sort((a, b) => (b[field] > a[field] ? 1 : b[field] < a[field] ? -1 : 0));
}

/** Isi satu koleksi (dipanggil onSnapshot Firestore atau pembaca cadangan). */
export function pasok(namaKoleksi, dokumen) {
  const k = KOLEKSI.find((x) => x.nama === namaKoleksi);
  if (!k) return false;
  _cache[k.cache] = urutkanTerbaru(dokumen || [], k.urut);
  _pendengar.forEach((f) => { try { f(namaKoleksi); } catch (e) { console.error('pendengar data', e); } });
  return true;
}
export function setelSumber(jenis, keterangan) { _sumber.jenis = jenis; _sumber.keterangan = keterangan || ''; _pendengar.forEach((f) => f('__sumber__')); }
export function sumberData() { return Object.assign({}, _sumber); }
export function dengarkan(f) { _pendengar.add(f); return () => _pendengar.delete(f); }
export function cacheMentah(nama) { return _cache[nama] || []; }

// ---- batas data untuk mesin beku (nama & bentuk = index.html) ----
function bacaCadanganLokal() { return []; }   // cadangan lokal buatan sendiri tidak ada di sistem baru
export function ambilSemuaBatch() { return _cache.batch; }
export function ambilBiayaBulanan() { return _cache.bulanan; }
export function ambilPenjualanSemua() { return _cache.penjualan; }
export function ambilPenjualan() { return ambilPenjualanSemua().filter(penjualanMasihBerlaku); }
export function ambilProduksi() { return _cache.produksi; }
export function ambilProduksiBerlaku() { return ambilProduksi().filter(produksiMasihBerlaku); }
export function ambilRetur() { return _cache.retur; }
export function ambilKarantina() { return _cache.karantina; }
export function ambilPengeluaranHarian() { return _cache.harian; }
export function ambilBahanKemasan() { return _cache.bahanKemasan; }
export function ambilBahanLiteran() { return _cache.bahanLiteran; }
export function ambilHargaLiteran() { return _cache.hargaLiteran; }
export function ambilHargaKemasan() { return _cache.hargaKemasan; }
export function ambilHargaKarung() { return _cache.hargaKarung; }
export function ambilPiutangMutasi() { return _cache.piutang; }
export function ambilKasbonMutasi() { return _cache.kasbon; }
export function ambilPenyesuaianStok() { return _cache.penyesuaian; }
export function ambilPenyesuaianKemasan() { return _cache.penyKemasan; }
export function ambilTutupHari() { return _cache.tutup; }
export function ambilPelangganCatatan() { return _cache.pelangganCat; }
export function ambilPesanan() { return _cache.pesanan; }
export function ambilTitipanHarian() { return _cache.titipan; }
export function ambilSetoranKas() { return _cache.setoran; }
export function ambilAmplopLaba() { return _cache.amplop; }
export function ambilModalOwner() { return _cache.modal; }
export function ambilUtangOwnerMutasi() { return _cache.utangOwner; }
export function ambilTembusanStok() { return _cache.tembusan; }
export function ambilUtangPemasokMutasi() { return _cache.utangPemasok; }
export function ambilThrPelanggan() { return _cache.thr; }
export function ambilPemasokCatatan() { return _cache.pemasokCat; }
// Titik kas & peta jenis beras hidup di localStorage perangkat di index.html (kunci yang sama);
// karena sistem baru ada di asal (origin) yang sama, localStorage-nya pun sama.
export function ambilTitikKas() {
  try { return JSON.parse(localStorage.getItem('miqbal_titik_kas_v1') || 'null'); } catch (e) { return null; }
}
export function ambilPetaJenisBeras() {
  try { return JSON.parse(localStorage.getItem('miqbal_jenis_beras_v1') || '{}'); } catch (e) { return {}; }
}

// ---- keranjang aktif & yang diparkir (dibaca stokMaksJalur lewat wzDiKeranjang) ----
// Bentuk isinya SAMA dengan _wzItems / _wzAntre di index.html: aktif = [{ trx }], parkir = [{ beku: { items } }].
let _keranjangAktif = [], _antrean = [];
export function setelKeranjang(aktif, antrean) { _keranjangAktif = aktif || []; _antrean = antrean || []; }
// wzJumlahDiDaftar() dipindah verbatim ke pembantu.js oleh pindah_mesin.py — penjumlah yang sama untuk keduanya.
export function wzDiKeranjangAktif(jalur, kunci) { return wzJumlahDiDaftar(_keranjangAktif || [], jalur, kunci); }
export function wzDiKeranjangParkir(jalur, kunci) {
  return (_antrean || []).reduce(function (a, x) {
    return a + wzJumlahDiDaftar(((x || {}).beku || {}).items || [], jalur, kunci);
  }, 0);
}
export { bacaCadanganLokal, urutkanTerbaru };
