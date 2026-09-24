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
import { kpSampai, kpTenggang, kpNilaiKiriman, kpKalimat, kpPotong, kpBulanDok, kpIdx, kpBulanStr, KP_BATAS_GET } from './kunci-periode.js';

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
/** Dokumen satu koleksi (nama koleksi Firestore) menurut cache — dipakai penulis pusat untuk membedakan create dari update (putaran 23). */
export function dokDiCache(koleksi, id) { const k = KOLEKSI.find((x) => x.nama === koleksi); return k ? (_cache[k.cache] || []).find((d) => String(d.id) === String(id)) || null : null; }

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
export function ambilDokumenCetak() { return _cache.dokumenCetak || []; }     // putaran 19: tiap dokumen yang keluar, bernomor urut
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
// ---- KUNCI PERIODE (putaran 25): SATU penjaga untuk semua tulisan layar, sebelum apa pun dikirim (juga di mode simulasi cadangan) ----
// Tulisan yang menyentuh bulan terkunci PASTI ditolak server (firestore.rules v4) → tidak dikirim; kalimatnya menyebut bulannya. Kiriman yang butuh lebih dari
// KP_BATAS_GET pemeriksaan kunci di server (tulisan bulan lampau di luar masa tenggang, 1 get() per operasi, cache tidak diandalkan) juga tidak dikirim —
// jalur yang memang besar (SATUKAN, hapus nama, tarik balik rincian, koreksi/hapus adukan) memakai tulisBertahap() di bawah.
export function kunciSampai() { return kpSampai(_cache.aturan); }
export function kunciTenggang() { return kpTenggang(_cache.aturan); }
/** Untuk logika layar: '' = boleh; selain itu kalimat "Bulan X terkunci — <pembalik>". Dokumen satu koleksi / satu tanggal. */
export function tolakKunci(koleksi, dok, pembalik) { const s = kunciSampai(); const b = s ? kpBulanDok(koleksi, dok) : null; return b !== null && b !== undefined && b <= kpIdx(s) ? kpKalimat(kpBulanStr(b), pembalik) : ''; }
export function tolakKunciTanggal(tgl, pembalik) { const s = kunciSampai(); return s && kpIdx(tgl || null) <= kpIdx(s) ? kpKalimat(kpBulanStr(kpIdx(tgl || null)), pembalik) : ''; }
function opsKiriman(daftar, hapus) {
  return (daftar || []).map(({ koleksi, data }) => ({ koleksi, data, lama: dokDiCache(koleksi, data.id) }))
    .concat((hapus || []).map((x) => ({ koleksi: x.koleksi, id: x.id, lama: dokDiCache(x.koleksi, x.id), hapus: true })));
}
/** → null (boleh dikirim) atau { gagal, terkunci?, pesan }. opsi.pembalik = kalimat pembalik yang ditawarkan layar. */
export function jagaKunci(daftar, hapus, opsi) {
  const N = kpNilaiKiriman(opsKiriman(daftar, hapus), kunciSampai(), new Date(Date.now()));
  if (N.terkunci.length) return { gagal: true, terkunci: true, bulan: N.terkunci[0].bulan, pesan: kpKalimat(N.terkunci.reduce((a, x) => (x.bulan > a ? x.bulan : a), N.terkunci[0].bulan), opsi && opsi.pembalik) + ' (' + N.terkunci.length + ' catatan)' };
  if (N.perluGet > KP_BATAS_GET) return { gagal: true, pesan: 'Kiriman ini menyentuh ' + N.perluGet + ' catatan bulan lampau — server hanya sanggup memeriksa ' + KP_BATAS_GET + ' sekali kirim. Tidak ada yang dikirim; pecah jadi beberapa kiriman.' };
  return null;
}
/** daftar = [{ koleksi, data }] — semua dokumen satu nota, sekali jalan. hapus (opsional, owner) = [{ koleksi, id }] di batch YANG SAMA; opsi.jejakHapus = kalimat jejaknya. */
export async function tulisDokumen(daftar, hapus, opsi) {
  const j = jagaKunci(daftar, hapus, opsi); if (j) return j;
  if (_penulis) return _penulis.tulis(daftar, hapus, opsi);
  terapkanKeCache(daftar.concat((hapus || []).map((x) => ({ koleksi: x.koleksi, hapus: x.id }))));
  return { simulasi: true };
}
/** daftar = [{ koleksi, id }] */
export async function hapusDokumen(daftar, opsi) {
  const j = jagaKunci([], daftar, opsi); if (j) return j;
  if (_penulis) return _penulis.hapus(daftar);
  terapkanKeCache(daftar.map((x) => ({ koleksi: x.koleksi, hapus: x.id })));
  return { simulasi: true };
}

// ---- KIRIM BERTAHAP (owner 25 Sep): potongan ≤ KP_BATAS_GET, dikirim berurutan; RENCANANYA disimpan di perangkat sebelum potongan pertama dikirim,
// jadi kalau terputus (tab ditutup, internet putus, ditolak) bisa DILANJUTKAN dari potongan yang belum — tidak ada yang dikirim dua kali.
// Satu rencana sekaligus. kelompok: lihat kpPotong (kunci-periode.js).
export const KUNCI_BERTAHAP = 'miqbal_baru_bertahap_v1';
const bacaBertahap = () => { try { const v = localStorage.getItem(KUNCI_BERTAHAP); return v ? JSON.parse(v) : null; } catch (e) { return null; } };
const simpanBertahap = (r) => { try { if (r) localStorage.setItem(KUNCI_BERTAHAP, JSON.stringify(r)); else localStorage.removeItem(KUNCI_BERTAHAP); return true; } catch (e) { return false; } };
export function bertahapTertunda() { const r = bacaBertahap(); return r && Array.isArray(r.potongan) && r.sudah < r.potongan.length ? { judul: r.judul, sudah: r.sudah, total: r.potongan.length, pada: r.pada } : null; }
async function jalankanBertahap(r, progres) {
  while (r.sudah < r.potongan.length) {
    const p = r.potongan[r.sudah];
    const h = await tulisDokumen(p.dokumen, p.hapus, { jejakHapus: r.judul + ' (' + (r.sudah + 1) + '/' + r.potongan.length + ')' });
    if (h && h.gagal) { simpanBertahap(r); return { gagal: true, sudah: r.sudah, total: r.potongan.length, pesan: h.pesan + ' — berhenti di kiriman ' + (r.sudah + 1) + ' dari ' + r.potongan.length + '; yang sebelumnya sudah masuk. Lanjutkan nanti dari Menu › Sistem › Perangkat.' }; }
    r.sudah += 1; simpanBertahap(r); if (progres) progres(r.sudah, r.potongan.length);
  }
  simpanBertahap(null); return { ok: true, total: r.potongan.length };
}
export async function tulisBertahap(judul, kelompok, progres) {
  if (bertahapTertunda()) return { gagal: true, pesan: 'Masih ada kiriman bertahap yang belum selesai (' + bacaBertahap().judul + ') — lanjutkan atau buang dulu di Menu › Sistem › Perangkat' };
  const P = kpPotong(kelompok, dokDiCache, new Date(Date.now())); if (P.tolak) return { gagal: true, pesan: P.tolak };
  const r = { id: 'bt-' + Date.now(), judul: String(judul || 'kiriman bertahap').slice(0, 80), pada: new Date(Date.now()).toISOString(), potongan: P.potongan.map((x) => ({ dokumen: x.dokumen, hapus: x.hapus })), sudah: 0 };
  if (r.potongan.length > 1 && !simpanBertahap(r)) return { gagal: true, pesan: 'Rencana kiriman bertahap tidak bisa disimpan di perangkat ini (penyimpanan penuh) — tidak ada yang dikirim' };
  const h = await jalankanBertahap(r, progres); return Object.assign({ potongan: r.potongan.length }, h);
}
export async function lanjutkanBertahap(progres) { const r = bacaBertahap(); if (!r) return { gagal: true, pesan: 'Tidak ada kiriman bertahap yang tertunda' }; return jalankanBertahap(r, progres); }
/** Buang rencana yang tertunda (potongan yang sudah terkirim TETAP masuk; hanya sisanya yang tidak dikirim). */
export function buangBertahap() { simpanBertahap(null); return true; }

/**
 * Putaran 23b (Bersihkan ciri yang dicabut): tulis KOLOM tertentu saja — update, bukan tulis ulang dokumen — jadi kolom lain & atribusinya byte-sama.
 * potongan = [[{ koleksi, id, kolom }]] (satu potongan = satu writeBatch); ringkas = SATU baris jejak (jumlah saja) di potongan terakhir.
 * Hasil: { potongan: [{ n, keadaan: ok | antre | gagal | simulasi, pesan? }], gagal? }.
 */
export async function perbaruiKolom(potongan, ringkas) {
  if (_penulis && _penulis.perbarui) return _penulis.perbarui(potongan, ringkas);
  if (_penulis) return { gagal: true, potongan: [], pesan: 'penulis Firestore belum mengenal tulis-kolom' };
  const hasil = [];
  potongan.forEach((p) => {
    terapkanKeCache(p.map((x) => { const k = KOLEKSI.find((y) => y.nama === x.koleksi); const lama = k ? _cache[k.cache].find((d) => String(d.id) === String(x.id)) : null; return lama ? { koleksi: x.koleksi, data: Object.assign({}, lama, x.kolom) } : null; }).filter(Boolean));
    hasil.push({ n: p.length, keadaan: 'simulasi' });
  });
  return { simulasi: true, potongan: hasil };
}

// ---- ARSIP TAHUN (putaran 18, Tutup buku K6): dokumen tahun yang ditutup PINDAH ke koleksi arsipTahun, bukan dihapus ----
// arsipTahun tidak pernah dimuat ke memori (ribuan dokumen tahun lalu); dibaca hanya saat "Batalkan tutup buku".
// Simulasi cadangan: arsipnya disimpan di memori perangkat ini saja.
let _arsip = [];
export function arsipSimulasi() { return _arsip.slice(); }
/** daftar = [{ koleksi, id, data }] → dipindah ke arsipTahun (id = tahun|koleksi|id) lalu dihapus dari koleksinya. progres(sudah, total) dipanggil per potongan. */
export async function arsipkanDokumen(tahun, daftar, progres) {
  // K1 (owner 25 Sep): arsip yang MEMINDAH (menghapus) dokumen tidak berjalan selama ada bulan terkunci — dirancang ulang sebelum Januari 2027
  const j = jagaKunci([], daftar.map((x) => ({ koleksi: x.koleksi, id: x.id }))); if (j && j.terkunci) throw new Error(j.pesan);
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
  const j = jagaKunci(daftar.map((x) => ({ koleksi: x.koleksi, data: Object.assign({}, x.dok, { id: x.idAsli }) })), []); if (j && j.terkunci) throw new Error(j.pesan);
  if (_penulis && _penulis.pulihkan) return _penulis.pulihkan(tahun, daftar, progres);
  terapkanKeCache(daftar.map((x) => ({ koleksi: x.koleksi, data: x.dok })));
  _arsip = _arsip.filter((a) => a.tahun !== tahun);
  if (progres) progres(daftar.length, daftar.length);
  return { simulasi: true, n: daftar.length };
}

