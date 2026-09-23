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
export function ambilWadahLiteran() { return _cache.wadah || []; }
export function ambilTitipanHarian() { return _cache.titipan; }
export function ambilSetoranKas() { return _cache.setoran; }
export function ambilAmplopLaba() { return _cache.amplop; }
export function ambilModalOwner() { return _cache.modal; }
export function ambilUtangOwnerMutasi() { return _cache.utangOwner; }
export function ambilTembusanStok() { return _cache.tembusan; }
export function ambilUtangPemasokMutasi() { return _cache.utangPemasok; }
export function ambilThrPelanggan() { return _cache.thr; }
export function ambilPemasokCatatan() { return _cache.pemasokCat; }
export function ambilHargaWadah() { return _cache.hargaWadah || []; }     // putaran 15: harga jual wadah per lembar (id = jenis)
export function ambilStrukKeluar() { return _cache.strukKeluar || []; }   // putaran 15: struk yang sudah dikirim/dicetak
export function ambilPengaturan() { return _cache.pengaturan || []; }     // koleksi pengaturan sistem lama (tempatSimpan)
export function ambilHargaPasar() { return _cache.hargaPasar || []; }       // putaran 17: catatan harga pasar per harga (id = kunci)
export function ambilHargaTerbit() { return _cache.hargaTerbit || []; }     // putaran 17: riwayat terbit katalog
export function ambilPesananPemasok() { return _cache.pesananPemasok || []; } // putaran 17: pesanan belanja ke pemasok
export function ambilPindahUang() { return _cache.pindahUang || []; }         // putaran 18: uang berpindah tempat (laci · brankas · rekening)
export function ambilAbsenKaryawan() { return _cache.absen || []; }           // putaran 18: hari kerja per orang per bulan
export function ambilSlipUpah() { return _cache.slipUpah || []; }             // putaran 18: tiap pembayaran upah
export function ambilTutupBukuAcara() { return _cache.tutupBukuAcara || []; } // putaran 18: berita acara tutup buku per tahun
// Titik kas & peta jenis beras hidup di localStorage perangkat di index.html (kunci yang sama);
// karena sistem baru ada di asal (origin) yang sama, localStorage-nya pun sama.
// Putaran 18: dokumen pengaturan/titikKas (ditulis Tutup hari sistem baru & lama) MENANG bila lebih baru dari salinan perangkat — persis pendengar onSnapshot titikKas
// index.html, supaya HP kedua melihat titik yang disetel HP pertama; salinan lokal tetap dipakai saat dokumennya belum sampai.
export function ambilTitikKas() {
  let lokal = null; try { lokal = JSON.parse(localStorage.getItem('miqbal_titik_kas_v1') || 'null'); } catch (e) { lokal = null; }
  const dok = (_cache.pengaturan || []).find((d) => String(d.id) === 'titikKas') || null;
  if (dok && dok.tanggal && (!lokal || String(dok.diubahPada || '') > String(lokal.diubahPada || ''))) return dok;
  return lokal;
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

// ---- MENULIS (putaran 2) — satu pintu untuk layar; penulisnya Firestore, atau SIMULASI ke cache saat memakai cadangan ----
let _penulis = null;   // { tulis(daftar) → Promise<{ok|antre|gagal}>, hapus(daftar) → Promise }
export function setelPenulis(p) { _penulis = p; }
export function adaPenulis() { return !!_penulis; }
/** Terapkan dokumen ke cache lokal (upsert per id) — dipakai simulasi cadangan; Firestore melakukannya sendiri lewat onSnapshot. */
export function terapkanKeCache(daftar) {
  const kena = {};
  daftar.forEach(({ koleksi, data, hapus }) => {
    const k = KOLEKSI.find((x) => x.nama === koleksi); if (!k) return;
    const id = String((data && data.id) || hapus);
    const sisa = _cache[k.cache].filter((d) => String(d.id) !== id);
    _cache[k.cache] = hapus ? sisa : urutkanTerbaru(sisa.concat([Object.assign({}, data)]), k.urut);
    kena[koleksi] = true;
  });
  Object.keys(kena).forEach((n) => _pendengar.forEach((f) => { try { f(n); } catch (e) { console.error('pendengar data', e); } }));
}
/** daftar = [{ koleksi, data }] — semua dokumen satu nota, sekali jalan. */
export async function tulisDokumen(daftar) {
  if (_penulis) return _penulis.tulis(daftar);
  terapkanKeCache(daftar);
  return { simulasi: true };
}
/** daftar = [{ koleksi, id }] */
export async function hapusDokumen(daftar) {
  if (_penulis) return _penulis.hapus(daftar);
  terapkanKeCache(daftar.map((x) => ({ koleksi: x.koleksi, hapus: x.id })));
  return { simulasi: true };
}

// ---- ARSIP TAHUN (putaran 18, Tutup buku K6): dokumen tahun yang ditutup PINDAH ke koleksi arsipTahun, bukan dihapus ----
// arsipTahun tidak pernah dimuat ke memori (ribuan dokumen tahun lalu); dibaca hanya saat "Batalkan tutup buku".
// Simulasi cadangan: arsipnya disimpan di memori perangkat ini saja.
let _arsip = [];
export function arsipSimulasi() { return _arsip.slice(); }
/** daftar = [{ koleksi, id, data }] → dipindah ke arsipTahun (id = tahun|koleksi|id) lalu dihapus dari koleksinya. progres(sudah, total) dipanggil per potongan. */
export async function arsipkanDokumen(tahun, daftar, progres) {
  if (_penulis && _penulis.arsipkan) return _penulis.arsipkan(tahun, daftar, progres);
  daftar.forEach((x) => { _arsip = _arsip.filter((a) => !(a.tahun === tahun && a.koleksi === x.koleksi && String(a.idAsli) === String(x.id))); _arsip.push({ id: tahun + '|' + x.koleksi + '|' + x.id, tahun, koleksi: x.koleksi, idAsli: x.id, dok: x.data }); });
  terapkanKeCache(daftar.map((x) => ({ koleksi: x.koleksi, hapus: x.id })));
  if (progres) progres(daftar.length, daftar.length);
  return { simulasi: true, n: daftar.length };
}
/** Semua dokumen arsip satu tahun: [{ koleksi, idAsli, dok }]. */
export async function bacaArsipTahun(tahun) {
  if (_penulis && _penulis.bacaArsip) return _penulis.bacaArsip(tahun);
  return _arsip.filter((a) => a.tahun === tahun).map((a) => ({ koleksi: a.koleksi, idAsli: a.idAsli, dok: a.dok }));
}
/** Kebalikannya: dokumen arsip dikembalikan ke koleksinya, salinan arsipnya dihapus. */
export async function pulihkanArsip(tahun, daftar, progres) {
  if (_penulis && _penulis.pulihkan) return _penulis.pulihkan(tahun, daftar, progres);
  terapkanKeCache(daftar.map((x) => ({ koleksi: x.koleksi, data: x.dok })));
  _arsip = _arsip.filter((a) => a.tahun !== tahun);
  if (progres) progres(daftar.length, daftar.length);
  return { simulasi: true, n: daftar.length };
}

