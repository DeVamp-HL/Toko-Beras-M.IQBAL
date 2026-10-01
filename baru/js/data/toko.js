// Lapisan DATA sistem baru: satu tempat memegang salinan koleksi Firestore di memori.
// Mesin beku (js/mesin/beku.js) membaca lewat fungsi ambil*() di bawah — nama dan bentuknya
// sama persis dengan index.html supaya tubuh mesin tidak perlu berubah satu byte pun.
//
// Yang berbeda dari index.html, dan sengaja:
//  - tidak ada cadangan localStorage buatan sendiri (kompresi LZ, kuota ±62 KB/hari); jalan tanpa
//    internet diserahkan ke cache tetap Firestore (IndexedDB) di js/data/firebase.js;
//  - keranjang aktif & yang diparkir disetel oleh layar lewat setelKeranjang(), bukan variabel global.
import { KOLEKSI } from './koleksi.js';
import { penjualanMasihBerlaku, produksiMasihBerlaku, wzJumlahDiDaftar, uangKembaliRetur } from '../mesin/pembantu.js';
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
/** Nama yang dipakai SISTEM di kolom pemasok batch (stok awal, saldo pembuka tutup buku, lahir buku) — bukan pemasok: tidak punya kartu, bon, atau utang. */
export const namaSistemPemasok = (nama) => { const n = String(nama || '').trim().toUpperCase(); return n === 'STOK AWAL' || n.startsWith('TUTUP BUKU') || n === 'LAHIR BUKU'; };
/** Satu NOTA = satu grupNota / trxId (satu nota bisa berisi banyak baris penjualan). 39b no. 20: laporan dulu menyebut jumlah BARIS sebagai "nota". */
export const kunciNota = (p) => String(p.grupNota || p.trxId || p.id);
/** Jumlah nota (bukan baris) penjualan yang masih berlaku dengan tanggal yang cocok. */
export function jumlahNota(cocok, saring) { const s = new Set(); ambilPenjualan().forEach((p) => { if (cocok(p.tanggal) && (!saring || saring(p))) s.add(kunciNota(p)); }); return s.size; }   // saring: mis. hanya nota bon
/**
 * Uang yang kembali ke pembeli lewat retur per tanggal — rumus & saringan yang SAMA dengan mesin laba (uangKembaliRetur atas semua retur bertanggal):
 * { 'YYYY-MM-DD': { uang, baris: [{ jam, uang }] } }. OMZET = penjualan − uang ini di SEMUA layar (keputusan owner 9 Sep: uang kembali selalu mengurangi
 * omzet; 39b no. 19: Ringkasan & Jual dulu bruto, Laporan/Pajak bersih).
 */
export function returUangPerHari() {
  const out = {}; ambilRetur().forEach((r) => { const t = String(r.tanggal || ''); if (!t) return; const u = uangKembaliRetur(r); if (!u) return;
    const h = out[t] || (out[t] = { uang: 0, baris: [] }); h.uang += u; h.baris.push({ jam: String(r.jam || ''), uang: u }); });
  return out;
}
export function ambilProduksi() { return _cache.produksi; }
export function ambilProduksiBerlaku() { return ambilProduksi().filter(produksiMasihBerlaku); }

// ---- STOK WADAH (putaran 28, owner 28 Sep 2026: "semua wadah kotak literan itu punya stok tersendiri") ----
// Tiap wadah literan punya buku sendiri berkunci 'Wadah <nama>' — bukan nama merek, supaya tidak bertabrakan dengan merek karung yang senama.
// Kunci itu LAHIR lewat satu baris batch stokAwal 0 kg ber-`stokWadah` (= nama wadah saat lahir): mesin beku hitungStokKarungPerMerk hanya memotong
// penjualan / penyesuaian / sumber produksi dari nama yang sudah lahir lewat batchMasuk. Satu tempat untuk mengenali kunci itu: petaStokWadah().
export const kunciStokWadah = (W) => 'Wadah ' + String(W);
/** { kunci buku stok wadah: nama wadah saat lahir } — dari baris batch ber-stokWadah (termasuk saldo pembuka tutup buku yang membawanya). */
export function petaStokWadah() {
  const out = {}; ambilSemuaBatch().forEach((b) => (b.merkList || []).forEach((m) => { if (m && m.stokWadah && m.merk) out[String(m.merk)] = String(m.stokWadah); }));
  return out;
}
// Isi yang DIKELUARKAN dari kotak wadah (owner 28 Sep: tiap tutup toko ±10 kg dari yang menggunung disisihkan; setahun sekali wadah dibongkar penuh)
// = stok TERPISAH per wadah, berkunci 'Karung wadah <nama>' — lahir dengan cara yang sama, barisnya bertanda `karungWadah` (= nama wadah).
export const kunciKarungWadah = (W) => 'Karung wadah ' + String(W);
// Kemasan jadi HASIL ADUKAN yang dibuka jadi karung terbuka (owner 28 Sep: "hasil produksi kemasan beda dari hasil beli langsung dari pemasok")
// = buku sendiri per produk & ukuran, berkunci 'Adukan <nama> <ukuran> kg', barisnya bertanda `bukuAdukan` (= kunci kemasannya).
export const kunciBukuAdukan = (nama, ukuran) => 'Adukan ' + String(nama) + ' ' + String(ukuran).replace('.', ',') + ' kg';
// Putaran 39 (owner 29 Sep: "karung di belakang wadah jadikan buku mesin tersendiri; diambil dari tumpukan gudang, tumpukannya berkurang"):
// karung 50/25 kg yang berdiri di belakang satu wadah = buku sendiri per WADAH × MEREK ASAL, berkunci 'Karung belakang <wadah> · <merek>'.
// Buka karung = pindah buku merek → karung belakang (tumpukan gudang turun sungguhan di buku); takar = pindah buku karung belakang → wadah.
// Barisnya lahir bertanda `karungBelakang` (= nama wadah) + `merkAsal` (= merek pemasok / buku sumbernya).
export const kunciKarungBelakang = (W, merk) => 'Karung belakang ' + String(W) + ' · ' + String(merk);
/** { kunci: { jenis: 'wadah' | 'karung' | 'adukan' | 'belakang', wadah, merk? } } — buku KHUSUS yang bukan merek pemasok: isi kotak wadah (stokWadah), karung
 *  sisihan/bongkarannya (karungWadah), kemasan hasil adukan yang dibuka (bukuAdukan; `wadah` = nama produknya), karung di belakang wadah (karungBelakang + merkAsal). */
export function petaBukuWadah() {
  const out = {}; ambilSemuaBatch().forEach((b) => (b.merkList || []).forEach((m) => { if (!m || !m.merk) return;
    if (m.stokWadah) out[String(m.merk)] = { jenis: 'wadah', wadah: String(m.stokWadah) }; else if (m.karungWadah) out[String(m.merk)] = { jenis: 'karung', wadah: String(m.karungWadah) };
    else if (m.bukuAdukan) out[String(m.merk)] = { jenis: 'adukan', wadah: String(m.bukuAdukan).split('|')[0] };
    else if (m.karungBelakang) out[String(m.merk)] = { jenis: 'belakang', wadah: String(m.karungBelakang), merk: String(m.merkAsal || '') }; }));
  return out;
}
/** Merek asal di balik satu kunci buku: kunci karung belakang → merek pemasoknya; selain itu kuncinya sendiri (merek biasa / buku khusus lain). */
export function merkAsalKunci(kunci, peta) { const b = (peta || petaBukuWadah())[String(kunci)]; return b && b.jenis === 'belakang' && b.merk ? b.merk : String(kunci); }
// Karung pemasok per UKURAN (owner 28 Sep: "beras hasil belanja dari pemasok itu ada 50 kg dan 25 kg … buat bukunya terpisah"): buku merek lama tetap buku
// karung 50 kg; karung 25 kg merek yang datang dua ukuran punya buku 'Merek 25 kg'. Barisnya (kedatangan / lahir) bertanda `indukUkuran` = merek induk.
export const kunciUkuran = (M, berat) => String(M) + ' ' + String(berat) + ' kg';
/** { 'Merek 25 kg': { induk: 'Merek', berat: 25 } } — dari baris batch ber-indukUkuran. */
export function petaUkuran() {
  const out = {}; ambilSemuaBatch().forEach((b) => (b.merkList || []).forEach((m) => { if (m && m.merk && m.indukUkuran) out[String(m.merk)] = { induk: String(m.indukUkuran), berat: Number(m.beratKarung) || 25 }; }));
  return out;
}
/** Audit 39b no. 35 (owner 30 Sep): buku per ukuran yang isinya sudah DIGABUNG balik ke induk (pindah buku bertanda gabungUkuran) — tidak lagi memisah induknya. */
export function ukuranDigabung() { const out = {}; ambilProduksiBerlaku().forEach((p) => { if (p && p.gabungUkuran && p.gabungUkuran.dari) out[String(p.gabungUkuran.dari)] = String(p.gabungUkuran.induk || ''); }); return out; }
/** { 'Merek': { 25: 'Merek 25 kg' } } — merek induk yang karung 25 kg-nya sudah punya buku sendiri (buku yang sudah digabung balik ke induk tidak dihitung). */
export function indukTerpisah() { const u = petaUkuran(); const g = ukuranDigabung(); const out = {}; Object.keys(u).forEach((n) => { if (g[n]) return; (out[u[n].induk] = out[u[n].induk] || {})[u[n].berat] = n; }); return out; }
/** Salinan peta stok karung TANPA buku khusus (isi wadah, karung sisihan, kemasan adukan dibuka) — untuk daftar MEREK (rak karung, gudang, harga karung, …). */
export function stokMerekSaja(stok) {
  const w = petaBukuWadah(); const out = {}; Object.keys(stok || {}).forEach((m) => { if (!w[m]) out[m] = stok[m]; }); return out;
}
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
// Putaran 25c: jenis beras diatur di /baru/ — dokumen pengaturan/jenisBeras (bentuk sama dengan index.html) MENANG; salinan localStorage (ditulis
// pendengar index.html / cadangan lama) hanya dipakai kalau dokumennya belum ada di cache. Dulu /baru/ HANYA membaca salinan itu, jadi sesudah sistem
// lama tidak dibuka lagi cadangan dari /baru/ membawa peta basi (docs/peta-pindahan-terakhir.md §3).
export function ambilPetaJenisBeras() {
  const dok = (_cache.pengaturan || []).find((d) => String(d.id) === 'jenisBeras');
  if (dok && dok.peta && typeof dok.peta === 'object' && !Array.isArray(dok.peta)) return Object.assign({}, dok.peta);
  try { return JSON.parse(localStorage.getItem('miqbal_jenis_beras_v1') || '{}'); } catch (e) { return {}; }
}
/**
 * Putaran 25c: jalankan fn di atas cache SEANDAINYA daftar dokumen [{ koleksi, data }] sudah tertulis — tanpa memberi tahu pendengar, dan cache
 * dikembalikan persis sesudahnya (juga kalau fn melempar). Dipakai katalog kasir: katalog SESUDAH terbit harga ikut dikirim dalam kiriman yang sama.
 */
export function denganCacheSementara(daftar, fn) {
  const simpan = {};
  (daftar || []).forEach(({ koleksi, data }) => {
    const k = KOLEKSI.find((x) => x.nama === koleksi); if (!k || !data) return;
    if (!(k.cache in simpan)) simpan[k.cache] = _cache[k.cache];
    const id = String(data.id);
    _cache[k.cache] = urutkanTerbaru(_cache[k.cache].filter((d) => String(d.id) !== id).concat([Object.assign({}, data)]), k.urut);
  });
  try { return fn(); } finally { Object.keys(simpan).forEach((c) => { _cache[c] = simpan[c]; }); }
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
/** Jumlah pemeriksaan kunci (get()) yang dibutuhkan server untuk satu kiriman — untuk logika layar yang ingin menolak dengan kalimatnya sendiri. */
export function butuhGet(daftar, hapus) { return kpNilaiKiriman(opsKiriman(daftar, hapus), null, new Date(Date.now())).perluGet; }
/** → null (boleh dikirim) atau { gagal, terkunci?, pesan }. opsi.pembalik = kalimat pembalik yang ditawarkan layar. */
export function jagaKunci(daftar, hapus, opsi) {
  const N = kpNilaiKiriman(opsKiriman(daftar, hapus), kunciSampai(), new Date(Date.now()));
  if (N.terkunci.length) return { gagal: true, terkunci: true, bulan: N.terkunci[0].bulan, pesan: kpKalimat(N.terkunci.reduce((a, x) => (x.bulan > a ? x.bulan : a), N.terkunci[0].bulan), opsi && opsi.pembalik) + ' (' + N.terkunci.length + ' catatan)' };
  if (N.perluGet > KP_BATAS_GET) return { gagal: true, pesan: 'Kiriman ini menyentuh ' + N.perluGet + ' catatan bulan lampau — server hanya sanggup memeriksa ' + KP_BATAS_GET + ' sekali kirim. Tidak ada yang dikirim; pecah jadi beberapa kiriman.' };
  return null;
}
// audit 39b no. 28: kabar sesudah kiriman — SATU kalimat untuk semua layar. Server belum mengaku dalam 1,5 detik ({ antre }) = catatan baru ada di perangkat:
// kabarnya "Tersimpan di perangkat, menunggu server" (sama dengan pil kepala) dan kata Tercatat/Tersimpan di depan kabar susunan dibuang; simulasi cadangan → "SIMULASI — ".
export const KABAR_ANTRE = 'Tersimpan di perangkat, menunggu server';
export function kabarKiriman(x, kabar) {
  const k = String(kabar || '');
  if (x && x.simulasi) return 'SIMULASI — ' + k;
  if (!(x && x.antre)) return k;
  const sisa = k.replace(/^(Tercatat|Tersimpan)(\s*[·—:.]\s*|$)/, '');
  return KABAR_ANTRE + (sisa ? ' — ' + sisa : '');
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
  let antre = 0, simulasi = false;   // 39b no. 28: potongan yang belum diakui server (masih di antrean perangkat) dihitung — layar tidak boleh berkata "selesai" polos
  while (r.sudah < r.potongan.length) {
    const p = r.potongan[r.sudah];
    const h = await tulisDokumen(p.dokumen, p.hapus, { jejakHapus: r.judul + ' (' + (r.sudah + 1) + '/' + r.potongan.length + ')' });
    if (h && h.gagal) { simpanBertahap(r); return { gagal: true, sudah: r.sudah, total: r.potongan.length, pesan: h.pesan + ' — berhenti di kiriman ' + (r.sudah + 1) + ' dari ' + r.potongan.length + '; yang sebelumnya sudah masuk. Lanjutkan nanti dari Menu › Sistem › Perangkat.' }; }
    if (h && h.antre) antre += 1;
    if (h && h.simulasi) simulasi = true;
    r.sudah += 1; simpanBertahap(r); if (progres) progres(r.sudah, r.potongan.length);
  }
  // mode cadangan: tanda simulasi ikut ke hasil supaya kabarKiriman menyebut "SIMULASI —" (dulu jalur bertahap berbunyi seperti kejadian sungguhan)
  simpanBertahap(null); return { ok: true, total: r.potongan.length, antre, simulasi: simulasi || undefined };
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

