// Lapisan DATA sistem baru: satu tempat memegang salinan koleksi Firestore di memori.
// Mesin beku (js/mesin/beku.js) membaca lewat fungsi ambil*() di bawah — nama dan bentuknya
// sama persis dengan index.html supaya tubuh mesin tidak perlu berubah satu byte pun.
//
// Yang berbeda dari index.html, dan sengaja:
//  - tidak ada cadangan localStorage buatan sendiri (kompresi LZ, kuota ±62 KB/hari); jalan tanpa
//    internet diserahkan ke cache tetap Firestore (IndexedDB) di js/data/firebase.js;
//  - keranjang aktif & yang diparkir disetel oleh layar lewat setelKeranjang(), bukan variabel global.
import { KOLEKSI } from './koleksi.js';
import { penjualanMasihBerlaku, produksiMasihBerlaku, wzJumlahDiDaftar, uangKembaliRetur, kunciPelanggan, kunciKemasan, tanggalLokalIso, JENDELA_LAJU_HARI, daftarGerakanKas, semuaMerkDikenal } from '../mesin/pembantu.js';
import { kpSampai, kpTenggang, kpNilaiKiriman, kpKalimat, kpPotong, kpBulanDok, kpIdx, kpBulanStr, KP_BATAS_GET, KP_ID_PINTU, kpPintu } from './kunci-periode.js';
// hari & hari tutup aktif (JAM_BATAS_TUTUP) untuk kunciLuarCache — satu aturan jam dengan Tutup hari & cek wadah
import { hariIniIso, tanggalTutupAktif } from '../inti/format.js';
// mesin beku, daftarGerakanKas & semuaMerkDikenal dipakai HANYA oleh ingatan di bawah (ingatStokKarung dkk.: hasil mesin diingat per versi cache)
import { hitungStokKarungPerMerk, hitungStokKemasan, kasPada, hitungNeraca } from '../mesin/beku.js';

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
  _cache[k.cache] = urutkanTerbaru(dokumen || [], k.urut); _versiCache += 1;
  _pendengar.forEach((f) => { try { f(namaKoleksi); } catch (e) { console.error('pendengar data', e); } });
  return true;
}
// owner 3 Okt (Jual patah-patah): nomor versi isi cache — naik tiap kali isi koleksi diganti (pasok, tulisan simulasi, cache sementara uji, ganti sumber).
// Dipakai jual-logika untuk tidak menyusun ulang seluruh rak tiap +1/−1 keranjang selama datanya sama.
let _versiCache = 0;
export const versiCache = () => _versiCache;
// owner 3 Okt "masih ada lag atau patah-patah" (layar selain Jual; diukur 7 Okt atas cadangan toko): satu angka yang sama dihitung ratusan kali per gambar —
// ambilPenjualan sampai 936×, petaBukuWadah sampai 3.366× (tiap baris / tiap wadah memanggilnya lagi). INGATAN PER VERSI: hasil fungsi yang HANYA membaca
// cache (bukan jam, localStorage, keranjang, atau isian layar) diingat sampai _versiCache naik — versi naik di SEMUA penulis cache (pasok, tulisan simulasi,
// cache sementara, ganti sumber), jadi ingatan tidak pernah lebih tua dari datanya. Hitungan yang mengubah cache di tengah jalan (denganCacheSementara)
// tidak disimpan. Hasil ingatan DIPAKAI BERSAMA: pemanggil tidak boleh mengubahnya di tempat (sort / push / Object.assign ke hasilnya) —
// alat-uji/uji_layar_mulus.py membekukan semua hasil ingatan lalu menjalankan seluruh layar, dan membandingkan tiap gambar dengan / tanpa ingatan.
const _ingatan = { versi: -1, isi: new Map(), mati: false, beku: null };
export function ingatPerVersi(kunci, f) {
  const I = _ingatan; if (I.mati) return f();
  if (I.versi !== _versiCache) { I.isi = new Map(); I.versi = _versiCache; }
  if (I.isi.has(kunci)) return I.isi.get(kunci);
  const v = _versiCache; const h = I.beku ? I.beku(f()) : f();
  if (v === _versiCache && I.versi === v) I.isi.set(kunci, h);
  return h;
}
/** Khusus alat uji: { mati: true } = hitung ulang tiap panggilan (pembanding); { beku: fn } = tiap hasil ingatan dilewatkan fn (pembeku). */
export function setelIngatan(o) { _ingatan.mati = !!(o && o.mati); _ingatan.beku = (o && o.beku) || null; _ingatan.isi = new Map(); _ingatan.versi = -1; }
/** Khusus alat uji: f dihitung TANPA ingatan (pembanding hitung ulang penuh); ingatan yang sudah ada tidak disentuh. */
export function tanpaIngatan(f) { const m = _ingatan.mati; _ingatan.mati = true; try { return f(); } finally { _ingatan.mati = m; } }
export function setelSumber(jenis, keterangan) { _versiCache += 1; _sumber.jenis = jenis; _sumber.keterangan = keterangan || ''; _pendengar.forEach((f) => f('__sumber__')); }
export function sumberData() { return Object.assign({}, _sumber); }
export function dengarkan(f) { _pendengar.add(f); return () => _pendengar.delete(f); }
export function cacheMentah(nama) { return _cache[nama] || []; }
/** Dokumen satu koleksi (nama koleksi Firestore) menurut cache — dipakai penulis pusat untuk membedakan create dari update (putaran 23). */
export function dokDiCache(koleksi, id) { const k = KOLEKSI.find((x) => x.nama === koleksi); return k ? (_cache[k.cache] || []).find((d) => String(d.id) === String(id)) || null : null; }
// §8 no. 4 (tutup buku bertahap): dokumen yang masih MENUNGGU SERVER di perangkat ini — Firestore sudah menaruh tulisannya di cache (hasPendingWrites), server
// belum mengaku (bisa saja nanti ditolak lalu dibuang). Diisi pendengar firebase.js per koleksi (nama Firestore); simulasi cadangan = selalu kosong.
const _tertunda = {};
export function setelTertunda(koleksi, ids) { _tertunda[koleksi] = (ids || []).map(String); }
export function dokTertunda(koleksi, id) { const s = _tertunda[koleksi]; return !!s && s.indexOf(String(id)) >= 0; }
// Putaran 3 AAL4: koleksi yang jawaban terakhirnya dari SALINAN PERANGKAT (Firestore fromCache, belum dijawab server) — tutup buku tidak dilanjutkan / dibatalkan
// dari data yang bisa basi. Diisi pendengar firebase.js per koleksi (nama Firestore); simulasi cadangan = selalu kosong.
// (nama sengaja beda dari _dariCache firebase.js — uji jsc membundel keduanya dalam satu lingkup)
const _salinanPerangkat = {};
export function setelDariCache(koleksi, ya) { _salinanPerangkat[koleksi] = !!ya; }
export function koleksiDariCache(koleksi) { return !!_salinanPerangkat[koleksi]; }
// Putaran 3 AAL5: HAPUS yang masih menunggu server di perangkat ini. Firestore langsung membuang dokumennya dari cache, jadi tanda per dokumen (hasPendingWrites,
// setelTertunda) tidak pernah melihatnya. Diisi tulisBerkas firebase.js per kiriman sampai server mengaku / menolak; simulasi cadangan = selalu kosong.
const _hapusTertunda = {};
export function setelHapusTertunda(idKiriman, hapus) { if (hapus && hapus.length) _hapusTertunda[idKiriman] = hapus.map((x) => ({ koleksi: x.koleksi, id: String(x.id) })); else delete _hapusTertunda[idKiriman]; }
export function hapusTertunda(koleksi) { return Object.keys(_hapusTertunda).reduce((n, k) => n + _hapusTertunda[k].filter((x) => x.koleksi === koleksi).length, 0); }

// ---- batas data untuk mesin beku (nama & bentuk = index.html) ----
// TUTUP BUKU BERTAHAP (rancangan Okt 2026): saldo pembuka tahun yang berita acaranya BELUM terkunci ('berjalan' = kiriman pembuka belum semua masuk;
// 'membatalkan' / 'dibatalkan' = sedang / sudah ditarik) TIDAK terlihat oleh mesin & era. Tahun lama tetap utuh sampai kiriman TERAKHIR (penanda) masuk;
// sesudah itu tahun baru utuh sekaligus. Saldo pembuka sistem lama (tanpa berita acara) dan yang terkunci/selesai tetap terlihat. Satu tempat: pembukaBerlaku.
// §8 no. 1 (tinjauan 1 Okt): HP STAF tidak membaca tutupBukuAcara (rules: owner saja) → saringan berita acara saja membuat stok & piutang di HP staf DOBEL
// selama 'berjalan' / 'membatalkan'. Karena itu saldo pembuka tutup buku bertahap membawa `bertahap: true` dan baru terlihat bila PENANDA tahunnya ada:
// batch pembuka ber-`penandaBuku` (koleksi batchMasuk — dibaca staf) yang ikut kiriman TERAKHIR dan dihapus di kiriman PERTAMA pembatalan. Aturan yang sama
// di semua perangkat → HP owner & staf melihat angka yang sama di tiap titik putus. Rules tidak berubah. Pembuka tanpa `bertahap` (sistem lama) tidak tersentuh.
const BK_TERSEMBUNYI = { berjalan: 1, membatalkan: 1, dibatalkan: 1 };
let _bkMemo = null;
function bkKeadaan() {
  const a = _cache.tutupBukuAcara, b = _cache.batch; if (_bkMemo && _bkMemo.a === a && _bkMemo.b === b) return _bkMemo;
  const sembunyi = {}, penanda = {};
  (a || []).forEach((x) => { if (x && BK_TERSEMBUNYI[x.status]) sembunyi[Number(x.tahun)] = true; });
  (b || []).forEach((x) => { if (x && x.tutupBuku && x.penandaBuku) penanda[Number(x.tahunDari)] = true; });
  _bkMemo = { a, b, sembunyi, penanda }; return _bkMemo;
}
export function pembukaBerlaku(x) { if (!x || !x.tutupBuku) return true; const k = bkKeadaan(); const t = Number(x.tahunDari); return !k.sembunyi[t] && (!x.bertahap || !!k.penanda[t]); }
const bkSaring = (arr) => { const s = arr.filter(pembukaBerlaku); return s.length === arr.length ? arr : s; };
// Siap 2027 (owner 7 Okt): koleksi yang bisa memuat SALDO PEMBUKA tutup buku (nama cache → koleksi Firestore) — satu daftar untuk era, tarik saat batal,
// dan antrean tutup buku. modalOwner ikut sejak modal owner menyeberang tahun (dokumen pembuka setor, bertanggal 31 Des).
export const CACHE_PEMBUKA = { batch: 'batchMasuk', piutang: 'piutangMutasi', kasbon: 'kasbonMutasi', produksi: 'produksiKemasan', bahanKemasan: 'stokBahanKemasan', bahanLiteran: 'stokBahanLiteran', utangPemasok: 'utangPemasokMutasi', utangOwner: 'utangOwnerMutasi', amplop: 'amplopLaba', modal: 'modalOwner' };
/** ERA tutup buku = tahun saldo pembuka terakhir yang terlihat (pembukaBerlaku). `kecuali` = tahun yang tidak dihitung (pembatalan). Dibaca juga upah & lintas tahun. */
export function eraBuku(kecuali) {
  let t = null; Object.keys(CACHE_PEMBUKA).forEach((c) => (_cache[c] || []).forEach((x) => { if (x && x.tutupBuku && pembukaBerlaku(x)) { const n = Number(x.tahunDari); if (isFinite(n) && n !== kecuali && (t === null || n > t)) t = n; } }));
  return t;
}
function bacaCadanganLokal() { return []; }   // cadangan lokal buatan sendiri tidak ada di sistem baru
export function ambilSemuaBatch() { return ingatPerVersi('ambilSemuaBatch', () => bkSaring(_cache.batch)); }
export function ambilBiayaBulanan() { return _cache.bulanan; }
export function ambilPenjualanSemua() { return _cache.penjualan; }
export function ambilPenjualan() { return ingatPerVersi('ambilPenjualan', () => ambilPenjualanSemua().filter(penjualanMasihBerlaku)); }
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
export function ambilProduksi() { return bkSaring(_cache.produksi); }
export function ambilProduksiBerlaku() { return ingatPerVersi('ambilProduksiBerlaku', () => ambilProduksi().filter(produksiMasihBerlaku)); }

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
export function petaBukuWadah() { return ingatPerVersi('petaBukuWadah', petaBukuWadahHitung); }
function petaBukuWadahHitung() {
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
export function ukuranDigabung() { const out = {}; ambilProduksiBerlaku().forEach((p) => { if (p && p.gabungUkuran && p.gabungUkuran.dari) out[String(p.gabungUkuran.dari)] = String(p.gabungUkuran.induk || ''); });
  // siap 2027 (owner 7 Okt): dokumen pindah buku bertanda gabungUkuran ikut diarsip tutup buku — baris saldo pembuka buku itu membawa tandanya (`digabungKe`)
  ambilSemuaBatch().forEach((b) => (b.merkList || []).forEach((m) => { if (m && m.merk && m.digabungKe && !out[String(m.merk)]) out[String(m.merk)] = String(m.digabungKe); }));
  return out; }
/** { 'Merek': { 25: 'Merek 25 kg' } } — merek induk yang karung 25 kg-nya sudah punya buku sendiri (buku yang sudah digabung balik ke induk tidak dihitung). */
export function indukTerpisah() { const u = petaUkuran(); const g = ukuranDigabung(); const out = {}; Object.keys(u).forEach((n) => { if (g[n]) return; (out[u[n].induk] = out[u[n].induk] || {})[u[n].berat] = n; }); return out; }
/** Salinan peta stok karung TANPA buku khusus (isi wadah, karung sisihan, kemasan adukan dibuka) — untuk daftar MEREK (rak karung, gudang, harga karung, …). */
export function stokMerekSaja(stok) {
  const w = petaBukuWadah(); const out = {}; Object.keys(stok || {}).forEach((m) => { if (!w[m]) out[m] = stok[m]; }); return out;
}
// ---- BUKU STOK MESIN, DIINGAT (owner 3 Okt "masih patah-patah"): hitungStokKarungPerMerk / hitungStokKemasan (mesin beku — tidak disunting) dibaca layar
// sampai ±2.000× per gambar (tiap wadah, tiap baris katalog, tiap anggota kelas; diukur 7 Okt atas cadangan toko). Keduanya HANYA membaca cache lewat ambil*()
// di atas, jadi hasilnya sama selama versi cache sama; `sampai` ikut kunci (kosong = semua). Mesin tetap membaca data lewat ambil*(); layar membaca buku
// stok lewat sini. Rak Jual (susunRak, stokMaksJalur, ongkos yang dijaga uji Jual) dan jalur tulis tetap memanggil mesin langsung.
export function ingatStokKarung(sampai) { return ingatPerVersi('stokKarung|' + (sampai || ''), () => hitungStokKarungPerMerk(sampai)); }
export function ingatStokKemasan(sampai) { return ingatPerVersi('stokKemasan|' + (sampai || ''), () => hitungStokKemasan(sampai)); }
/** semuaMerkDikenal (pembantu: nama di buku karung, kemasan, katalog karung — hanya cache) diingat; Harga & jenis beras membacanya tiap gambar. */
export function ingatMerkDikenal() { return ingatPerVersi('merkDikenal', semuaMerkDikenal); }
// KAS & NERACA MESIN, DIINGAT: daftarGerakanKas (seluruh riwayat gerakan kas; Uang dulu menyusunnya ±6× + kasPada ±4× per gambar) hanya membaca cache.
// kasPada & hitungNeraca juga membaca TITIK KAS (ambilTitikKas: salinan localStorage perangkat atau dokumen pengaturan/titikKas) — salinan perangkat bisa berubah
// TANPA versi cache naik (tab lain, tutup hari), jadi titik kas yang sedang terbaca ikut KUNCI ingatan: titik berubah → dihitung ulang.
export function ingatGerakanKas() { return ingatPerVersi('gerakanKas', daftarGerakanKas); }
export function ingatKasPada(sampai) { return ingatPerVersi('kasPada|' + (sampai || '') + '|' + JSON.stringify(ambilTitikKas()), () => kasPada(sampai)); }
export function ingatNeraca(sampai) { return ingatPerVersi('neraca|' + (sampai || '') + '|' + JSON.stringify(ambilTitikKas()), () => hitungNeraca(sampai)); }
export function ambilRetur() { return _cache.retur; }
export function ambilKarantina() { return _cache.karantina; }
export function ambilPengeluaranHarian() { return _cache.harian; }
export function ambilBahanKemasan() { return bkSaring(_cache.bahanKemasan); }
export function ambilBahanLiteran() { return bkSaring(_cache.bahanLiteran); }
export function ambilHargaLiteran() { return _cache.hargaLiteran; }
export function ambilHargaKemasan() { return _cache.hargaKemasan; }
export function ambilHargaKarung() { return _cache.hargaKarung; }
export function ambilPiutangMutasi() { return bkSaring(_cache.piutang); }
export function ambilKasbonMutasi() { return bkSaring(_cache.kasbon); }
export function ambilPenyesuaianStok() { return _cache.penyesuaian; }
export function ambilPenyesuaianKemasan() { return _cache.penyKemasan; }
export function ambilTutupHari() { return _cache.tutup; }
export function ambilPelangganCatatan() { return _cache.pelangganCat; }
export function ambilPesanan() { return _cache.pesanan; }
export function ambilWadahLiteran() { return _cache.wadah || []; }
export function ambilTitipanHarian() { return _cache.titipan; }
export function ambilSetoranKas() { return _cache.setoran; }
export function ambilAmplopLaba() { return bkSaring(_cache.amplop); }
export function ambilModalOwner() { return bkSaring(_cache.modal); }   // siap 2027: modal owner punya saldo pembuka tutup buku (bertahap)
export function ambilUtangOwnerMutasi() { return bkSaring(_cache.utangOwner); }
export function ambilTembusanStok() { return _cache.tembusan; }
export function ambilUtangPemasokMutasi() { return bkSaring(_cache.utangPemasok); }
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
/**
 * KUNCI KEADAAN DI LUAR CACHE (sanggahan layar mulus, 7 Okt): yang ikut digambar layar tetapi TIDAK menaikkan versi cache — HARI, HARI TUTUP AKTIF (jam 12 siang
 * memindah "cek tutup" wadah & Tutup hari ke hari dagang berikutnya, tanggalTutupAktif) dan TITIK KAS yang terbaca (salinan perangkat bisa berubah dari tab lain
 * tanpa data baru). Layar yang tidak menggambar ulang karena "tidak ada data baru" (dasbor, Menu & layar lain yang dibuka lagi) memakai hasil lamanya hanya
 * bila kunci ini sama. Yang lebih halus dari hari (pita jam Menu, jam di Pelanggan) ditambahkan layarnya sendiri di belakang kunci ini.
 */
export function kunciLuarCache(kini) { const k = kini || new Date(); return hariIniIso(k) + '|' + tanggalTutupAktif(k) + '|' + JSON.stringify(ambilTitikKas()); }
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
    _cache[k.cache] = urutkanTerbaru(_cache[k.cache].filter((d) => String(d.id) !== id).concat([Object.assign({}, data)]), k.urut); _versiCache += 1;
  });
  try { return fn(); } finally { Object.keys(simpan).forEach((c) => { _cache[c] = simpan[c]; }); _versiCache += 1; }
}
/**
 * Paket C (siap 2027, 7 Okt 2026): jalankan fn di atas cache yang DISARING sementara — koleksi `nama` (nama Firestore) hanya menyisakan dokumen yang lolos
 * `lolos(dok, namaKoleksi)`; koleksi lain apa adanya. `ganti(dok, namaKoleksi)` (boleh tidak ada) = dokumen yang dipakai sebagai gantinya (salinan, mis. saldo
 * pembuka seperti saat kunci). Tanpa memberi tahu pendengar, dan cache dikembalikan persis sesudahnya (juga kalau fn melempar) — pola denganCacheSementara.
 * Dipakai kartu "Pemeriksaan sesudah tutup buku" (buku & rak Jual saat buku tahun baru DIBUKA) dan periksa ulang tutup buku (tanpa catatan sesudah kunci).
 */
export function denganCacheSaring(nama, lolos, fn, ganti) {
  const simpan = {};
  (nama || []).forEach((n) => { const k = KOLEKSI.find((x) => x.nama === n); if (!k || k.cache in simpan) return; simpan[k.cache] = _cache[k.cache];
    _cache[k.cache] = (_cache[k.cache] || []).filter((d) => lolos(d, n)).map((d) => (ganti ? ganti(d, n) : d)); });
  _versiCache += 1;
  try { return fn(); } finally { Object.keys(simpan).forEach((c) => { _cache[c] = simpan[c]; }); _versiCache += 1; }
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
    _cache[k.cache] = hapus ? sisa : urutkanTerbaru(sisa.concat([Object.assign({}, data)]), k.urut); _versiCache += 1;
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
// tanda = 'arsip' (hapus = pindah ke arsipTahun di batch yang sama) | 'pulih' (tulis = kembali dari arsipTahun) — hanya arsipkanDokumen / pulihkanArsip
function opsKiriman(daftar, hapus, tanda) {
  return (daftar || []).map(({ koleksi, data }) => Object.assign({ koleksi, data, lama: dokDiCache(koleksi, data.id) }, tanda === 'pulih' ? { pulih: true } : {}))
    .concat((hapus || []).map((x) => Object.assign({ koleksi: x.koleksi, id: x.id, lama: dokDiCache(x.koleksi, x.id), hapus: true }, tanda === 'arsip' ? { arsip: true } : {})));
}
/** rules v7: pintu menurut dokumen d pada jam kini, beserta titikSebelum berita acara tahun itu (cache — rules membacanya SEBELUM batch) → { tahun, sampai, titikSebelum } | null. */
export function pintuDari(d, kini) {
  const P = kpPintu(d, kini); if (!P) return null;
  const a = (_cache.tutupBukuAcara || []).find((x) => x && Number(x.tahun) === P.tahun);
  return kpPintu(d, kini, a && a.titikSebelum);
}
/** rules v7: PINTU TUTUP BUKU yang terbuka sekarang (pengaturan/pintuBuku di cache) → { tahun, sampai, titikSebelum } atau null. */
export function pintuBuku() { return pintuDari(dokDiCache('pengaturan', KP_ID_PINTU), new Date(Date.now())); }
// pintu yang berlaku untuk SATU kiriman: yang ikut ditulis di kiriman itu (rules menilainya sesudah batch — getAfter), selain itu yang di cache
function pintuKiriman(daftar) {
  const d = (daftar || []).find((x) => x.koleksi === 'pengaturan' && x.data && String(x.data.id) === KP_ID_PINTU);
  return d ? pintuDari(d.data, new Date(Date.now())) : pintuBuku();
}
/** Jumlah pemeriksaan kunci (get()) yang dibutuhkan server untuk satu kiriman — untuk logika layar yang ingin menolak dengan kalimatnya sendiri. */
export function butuhGet(daftar, hapus) { return kpNilaiKiriman(opsKiriman(daftar, hapus), null, new Date(Date.now())).perluGet; }
/** → null (boleh dikirim) atau { gagal, terkunci?, pesan }. opsi.pembalik = kalimat pembalik yang ditawarkan layar. */
/** Penilaian kunci satu kiriman SEPERTI server (kpNilaiKiriman dengan bulan terkunci & pintu tutup buku): { terkunci, perluGet, lewatPintu, … }. */
export function nilaiKunci(daftar, hapus, opsi) { return kpNilaiKiriman(opsKiriman(daftar, hapus, opsi && opsi.pintu), kunciSampai(), new Date(Date.now()), pintuKiriman(daftar)); }
export function jagaKunci(daftar, hapus, opsi) {
  // rules v7: catatan bulan terkunci yang lewat PINTU TUTUP BUKU (saldo pembuka / arsip / pengembalian / titik kas tahun pintu) tidak dihitung terkunci —
  // biayanya (access call pintu) ikut perluGet. opsi.pintu = 'arsip' | 'pulih' (hanya arsipkanDokumen / pulihkanArsip)
  const N = nilaiKunci(daftar, hapus, opsi);
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
    if (h && h.gagal) { simpanBertahap(r); return { gagal: true, sudah: r.sudah, total: r.potongan.length, pesan: h.pesan + ' — berhenti di kiriman ' + (r.sudah + 1) + ' dari ' + r.potongan.length + '; yang sebelumnya sudah masuk. Lanjutkan nanti dari Menu › Toko ini › Perangkat & antrean › Antrean kirim.' }; }
    if (h && h.antre) antre += 1;
    if (h && h.simulasi) simulasi = true;
    r.sudah += 1; simpanBertahap(r); if (progres) progres(r.sudah, r.potongan.length);
  }
  // mode cadangan: tanda simulasi ikut ke hasil supaya kabarKiriman menyebut "SIMULASI —" (dulu jalur bertahap berbunyi seperti kejadian sungguhan)
  simpanBertahap(null); return { ok: true, total: r.potongan.length, antre, simulasi: simulasi || undefined };
}
export async function tulisBertahap(judul, kelompok, progres) {
  if (bertahapTertunda()) return { gagal: true, pesan: 'Masih ada kiriman bertahap yang belum selesai (' + bacaBertahap().judul + ') — lanjutkan atau buang dulu di Menu › Toko ini › Perangkat & antrean › Antrean kirim' };
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
  // K1 (owner 25 Sep): arsip yang MEMINDAH (menghapus) dokumen ditolak di bulan terkunci. Keputusan owner 7 Okt (K8, pengecualian sempit — rules v7): catatan
  // bulan terkunci bertanggal ≤ 31 Des tahun itu BOLEH dipindah selama PINTU TUTUP BUKU tahun itu terbuka (pengaturan/pintuBuku), karena salinannya ditulis
  // ke arsipTahun di batch yang SAMA (rules: salinan arsip = isi catatan yang dihapus, dan salinan bulan terkunci = catatan aslinya). Berkas arsip dan
  // cadangan SEBELUM tetap disimpan 10 tahun di luar Mac.
  const j = jagaKunci([], daftar.map((x) => ({ koleksi: x.koleksi, id: x.id })), { pintu: 'arsip' }); if (j && j.terkunci) throw new Error(j.pesan);
  // access call server per catatan (0 bulan berjalan · 2 bulan lampau · 5 lewat pintu, termasuk salinan arsipnya) — firebase.js memecah potongan ≤ 18
  const biaya = biayaPintu(daftar.map((x) => ({ koleksi: x.koleksi, id: x.id, lama: x.data, hapus: true, arsip: true })));
  if (_penulis && _penulis.arsipkan) return _penulis.arsipkan(tahun, daftar, progres, biaya);
  daftar.forEach((x) => { _arsip = _arsip.filter((a) => !(a.tahun === tahun && a.koleksi === x.koleksi && String(a.idAsli) === String(x.id))); _arsip.push({ id: tahun + '|' + x.koleksi + '|' + x.id, tahun, koleksi: x.koleksi, idAsli: x.id, dok: x.data }); });
  terapkanKeCache(daftar.map((x) => ({ koleksi: x.koleksi, hapus: x.id })));
  if (progres) progres(daftar.length, daftar.length);
  return { simulasi: true, n: daftar.length };
}
/** Access call server per operasi arsip / pengembalian (jalur pintu tutup buku ikut) — dasar pemecah potongan firebase.js (kpPecahBiaya). */
function biayaPintu(ops) { const s = kunciSampai(); const P = pintuBuku(); const kini = new Date(Date.now()); return ops.map((op) => kpNilaiKiriman([op], s, kini, P).perluGet); }
/** Semua dokumen arsip satu tahun: [{ koleksi, idAsli, dok }]. */
export async function bacaArsipTahun(tahun) {
  if (_penulis && _penulis.bacaArsip) return _penulis.bacaArsip(tahun);
  return _arsip.filter((a) => a.tahun === tahun).map((a) => ({ koleksi: a.koleksi, idAsli: a.idAsli, dok: a.dok }));
}
/** Kebalikannya: dokumen arsip dikembalikan ke koleksinya, salinan arsipnya dihapus. */
export async function pulihkanArsip(tahun, daftar, progres) {
  const j = jagaKunci(daftar.map((x) => ({ koleksi: x.koleksi, data: Object.assign({}, x.dok, { id: x.idAsli }) })), [], { pintu: 'pulih' }); if (j && j.terkunci) throw new Error(j.pesan);
  const biaya = biayaPintu(daftar.map((x) => ({ koleksi: x.koleksi, data: Object.assign({}, x.dok, { id: x.idAsli }), lama: dokDiCache(x.koleksi, x.idAsli), pulih: true })));
  if (_penulis && _penulis.pulihkan) return _penulis.pulihkan(tahun, daftar, progres, biaya);
  terapkanKeCache(daftar.map((x) => ({ koleksi: x.koleksi, data: x.dok })));
  _arsip = _arsip.filter((a) => a.tahun !== tahun);
  if (progres) progres(daftar.length, daftar.length);
  return { simulasi: true, n: daftar.length };
}

// ---- LINTAS TAHUN (siap 2027, owner 7 Okt) — fitur yang menghitung MUNDUR tetap benar di awal Januari sesudah tutup buku ----
// KR1 batas bon (90 hari), laju pakai (14 hari), dan daftar pelanggan membaca penjualan HIDUP; sesudah tahun lama diarsip, rentang ≤ 31 Des kosong (tanpa ini
// semua bon langganan ditolak sampai ±April). Saat tahun dikunci, tutup buku menulis RINGKASAN tahun itu di batch PENANDA (`ringkasTahun`) — batch yang
// dibaca semua perangkat dan terlihat bersamaan dengan saldo pembuka (pembukaBerlaku); dibatalkan = ikut hilang. Pembaca memakai ringkasan untuk rentang
// ≤ 31 Des dan catatan hidup untuk sesudahnya. Selama catatan hidup ≤ 31 Des masih sama dengan ringkasannya (sebelum arsip), hasilnya PERSIS angka mesin.
// Rumus per hari di bawah = SALINAN saringan mesin beku (infoKreditPelanggan, hitungLajuPakai); uji_tutup_buku_bertahap.py menjaga keduanya tetap sama.
export const RINGKAS_KREDIT_HARI = 90;   // KR1: tanggal ≥ hari ini − 89 (infoKreditPelanggan)
const ltGeser = (iso, n) => { const d = new Date(String(iso) + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
/** Ringkasan tahun era yang sedang terlihat (batch penanda tahun itu), atau null. */
export function ringkasArsip() {
  const era = eraBuku(); if (era === null) return null;
  const b = (_cache.batch || []).find((x) => x && x.tutupBuku && x.penandaBuku && Number(x.tahunDari) === era && x.ringkasTahun && pembukaBerlaku(x));
  return b ? b.ringkasTahun : null;
}
/** KR1 per hari: { kunci pelanggan: { tanggal: Σ hargaTotal } } — saringan sama dengan infoKreditPelanggan (penjualan berlaku, namaPelanggan, hargaTotal). */
export function kreditHarian(dari, sampai) {
  const out = {}; ambilPenjualan().forEach((t) => { const tg = t.tanggal || ''; if (!tg || tg < dari || tg > sampai) return; const k = kunciPelanggan(t.namaPelanggan); if (!k) return;
    const o = out[k] || (out[k] = {}); o[tg] = (o[tg] || 0) + (t.hargaTotal || 0); });
  return out;
}
/** Laju pakai per hari: { tanggal: { kg: {merek}, unit: {kunci kemasan}, pcs: {jenis} } } — saringan sama dengan hitungLajuPakai (belum dibagi hari). */
export function lajuHarian(dari, sampai) {
  const hari = {}; const h = (t) => hari[t] || (hari[t] = { kg: {}, unit: {}, pcs: {} }); const dlm = (t) => !!t && t >= dari && t <= sampai; const tb = (o, k, n) => { o[k] = (o[k] || 0) + n; };
  ambilPenjualan().forEach((p) => { const t = p.tanggal || ''; if (!dlm(t)) return;
    if ((p.jenis === 'karung' || p.jenis === 'repacking' || p.jenis === 'literan') && p.merkSumber) tb(h(t).kg, p.merkSumber, p.totalKg || 0);
    if (p.jenis === 'kemasan') tb(h(t).unit, kunciKemasan(p.namaProduk, p.ukuranKemasan), p.jumlahUnit || 0); });
  ambilProduksiBerlaku().forEach((pr) => { const t = pr.tanggal || ''; if (!dlm(t)) return;
    if (Array.isArray(pr.sumberList) && pr.sumberList.length > 0) pr.sumberList.forEach((x) => { if (x.merk) tb(h(t).kg, x.merk, x.kg || 0); });
    else if (pr.merkSumber && !pr.beliJadi) tb(h(t).kg, pr.merkSumber, pr.kgDipakai || 0); });
  ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((b) => { const t = b.tanggal || ''; if (b.tipe !== 'pakai' || !dlm(t)) return; tb(h(t).pcs, b.jenis, b.jumlah || 0); });
  return hari;
}
/** Bagian ringkasan untuk KR1 & laju pakai (bagian pelanggan disusun pelanggan-logika). */
export function ringkasKreditLaju(cutoff) {
  const dariK = ltGeser(cutoff, -(RINGKAS_KREDIT_HARI - 1)), dariL = ltGeser(cutoff, -JENDELA_LAJU_HARI);
  return { kredit: { dari: dariK, hari: kreditHarian(dariK, cutoff) }, laju: { dari: dariL, hari: lajuHarian(dariL, cutoff) } };
}
/** KR1 lintas tahun: info = infoKreditPelanggan(nama) (mesin beku). Rentang ≤ 31 Des diganti ringkasannya; tanpa ringkasan / sama = info apa adanya. */
export function kreditLintas(info, nama) {
  const R = ringkasArsip(); if (!info || !info.ada || !R || !R.kredit || !R.kredit.hari) return info;
  const batasIso = tanggalLokalIso(new Date(Date.now() - (RINGKAS_KREDIT_HARI - 1) * 86400000)); if (batasIso > R.cutoff) return info;
  const k = kunciPelanggan(nama); let semua = 0, hidupLama = 0, ring = 0;
  ambilPenjualan().forEach((t) => { const tg = t.tanggal || ''; if (tg >= batasIso && kunciPelanggan(t.namaPelanggan) === k) { semua += t.hargaTotal || 0; if (tg <= R.cutoff) hidupLama += t.hargaTotal || 0; } });
  const r = R.kredit.hari[k] || {}; Object.keys(r).forEach((d) => { if (d >= batasIso && d <= R.cutoff) ring += Number(r[d]) || 0; });
  if (Math.abs(ring - hidupLama) < 0.5) return info;
  const rataBulanan = Math.round((semua - hidupLama + ring) / 3);
  return Object.assign({}, info, { rataBulanan, batas: rataBulanan * 2, lintasTahun: { tahun: R.tahun, rupiah: ring } });
}
/** Laju pakai lintas tahun: L = hitungLajuPakai() (mesin beku). Rentang ≤ 31 Des diganti ringkasannya, per hari & per barang; tanpa ringkasan = L apa adanya. */
export function lajuLintas(L) {
  const R = ringkasArsip(); if (!L || !R || !R.laju || !R.laju.hari) return L;
  const mulai = tanggalLokalIso(new Date(Date.now() - JENDELA_LAJU_HARI * 86400000)); if (mulai > R.cutoff) return L;
  const hidup = lajuHarian(mulai, R.cutoff); const beda = {}; const pasang = [['kg', 'kgMerk'], ['unit', 'unitKemasan'], ['pcs', 'pcsBahan']];
  const geser = (sumber, tanda) => Object.keys(sumber).forEach((t) => { if (t < mulai || t > R.cutoff) return; pasang.forEach(([a, b]) => Object.keys(sumber[t][a] || {}).forEach((k) => { const kk = b + '|' + k; beda[kk] = (beda[kk] || 0) + tanda * (Number(sumber[t][a][k]) || 0); })); });
  geser(R.laju.hari, 1); geser(hidup, -1);
  const ubah = Object.keys(beda).filter((kk) => Math.abs(beda[kk]) > 1e-9); if (!ubah.length) return L;
  const out = { kgMerk: Object.assign({}, L.kgMerk), unitKemasan: Object.assign({}, L.unitKemasan), pcsBahan: Object.assign({}, L.pcsBahan) };
  ubah.forEach((kk) => { const i = kk.indexOf('|'); const b = kk.slice(0, i), k = kk.slice(i + 1); out[b][k] = (out[b][k] || 0) + beda[kk] / JENDELA_LAJU_HARI; });
  return out;
}

// ---- POTRET TAHUN YANG DITUTUP (Paket B siap 2027, owner 7 Okt) — Laporan, Pajak & Dasbor membaca tahun yang sudah diarsip ----
// Saat tahun dikunci, tutup buku menyimpan POTRET tahun itu di berita acaranya (tutupBukuAcara/{tahun}.potret, owner saja; disusun layar/potret-logika.js dari
// fungsi sumber yang SAMA dengan layarnya). Arsip lalu memindah catatan tahun itu keluar dari memori — tanpa potret, Pajak & Laporan tahun itu jadi Rp0 bertanda
// FINAL. SATU aturan untuk semua pembaca: tahun DIARSIP = tahun ≤ era (saldo pembuka terlihat, pembukaBerlaku) yang berita acaranya di sistem ini terkunci/selesai.
// Tahun diarsip ber-potret → potret MENGGANTIKAN catatan hidup tahun itu SELURUHNYA (yang masih tersisa — pesanan belum tuntas, catatan susulan A9 — tidak dijumlah
// dua kali). Tahun diarsip TANPA potret (dikunci sebelum Paket B) → layar menyebutnya, tidak menggambar Rp0. Dibatalkan = era turun = tidak diarsip lagi.
// Era tanpa berita acara (saldo pembuka sistem lama) tidak tersentuh: dibaca dari catatan hidup seperti sebelumnya.
let _ptMemo = null;
function ptKeadaan() {
  if (_ptMemo && _ptMemo.v === _versiCache) return _ptMemo;
  const era = eraBuku(); const potret = {}; const diarsip = {};
  if (era !== null) (_cache.tutupBukuAcara || []).forEach((a) => { const t = Number(a && a.tahun); if (!isFinite(t) || t > era || (a.status !== 'terkunci' && a.status !== 'selesai')) return; diarsip[t] = true; if (a.potret && a.potret.bulan && Number(a.potret.tahun) === t) potret[t] = a.potret; });
  _ptMemo = { v: _versiCache, era, potret, diarsip }; return _ptMemo;
}
/** Tahun (atau 'YYYY-MM' / 'YYYY-MM-DD') sudah ditutup buku — era ≥ tahun itu (juga saldo pembuka sistem lama). */
export function tahunDitutup(t) { const k = ptKeadaan(); return k.era !== null && Number(String(t).slice(0, 4)) <= k.era; }
/** Tahun yang catatannya DIARSIP tutup buku sistem ini (berita acara terkunci/selesai, era ≥ tahun) — catatan hidup tahun itu tidak lagi lengkap. */
export function tahunDiarsip(t) { return !!ptKeadaan().diarsip[Number(String(t).slice(0, 4))]; }
/** Era yang ditutup LEWAT SISTEM INI — tahun itu tercatat di sistem; null = belum ada / ditutup sistem lama. */
export function eraBerAcara() { const k = ptKeadaan(); return k.era !== null && k.diarsip[k.era] ? k.era : null; }
/** Potret tahun yang diarsip (berita acara terkunci/selesai), atau null. */
export function potretTahun(t) { return ptKeadaan().potret[Number(String(t).slice(0, 4))] || null; }
/** Satu bulan ('YYYY-MM') dari potret tahunnya, atau null (tahun belum diarsip / tanpa potret). */
export function potretBulan(key) { const P = potretTahun(key); return P ? P.bulan[String(key).slice(0, 7)] || null : null; }
/** Satu hari ('YYYY-MM-DD') dari potret: { omzet, margin, tanpaHpp, retur, nota } — hari tanpa catatan = nol (potretnya ada); null = tahun tanpa potret. */
export function potretHari(iso) {
  const P = potretTahun(iso); if (!P) return null; const x = (P.hari && P.hari[String(iso).slice(0, 10)]) || [];
  return { omzet: Number(x[0]) || 0, margin: Number(x[1]) || 0, tanpaHpp: Number(x[2]) || 0, retur: Number(x[3]) || 0, nota: Number(x[4]) || 0 };
}
/** Nilai `kolom` paling awal dari semua potret yang terbaca ('awalSistem' = nota pertama sistem, 'pertama' = catatan pertama toko); '' = tidak ada. */
export function awalPotret(kolom) { let p = ''; const P = ptKeadaan().potret; Object.keys(P).forEach((t) => { const x = String(P[t][kolom] || ''); if (x && (!p || x < p)) p = x; }); return p; }
/** Tanggal CATATAN PERTAMA toko (nota apa pun atau kedatangan sungguhan — bukan saldo pembuka tutup buku) = awal buku. SATU sumber untuk Laporan (lpPertama:
 *  daftar bulan, awal buku) dan Menu (umur buku, pintu "satu bulan penuh") — sanggahan Paket B: Menu dulu punya salinan sendiri dari catatan hidup, jadi sesudah
 *  ritual pintunya tertutup lagi ("4 hari") sementara Laporan tetap membaca 2026. Catatan tahun yang sudah ditutup buku sudah diarsip → dari potretnya. */
export function catatanPertama() { let p = ''; ambilPenjualanSemua().forEach((d) => { if (d.tanggal && (!p || d.tanggal < p)) p = d.tanggal; }); ambilSemuaBatch().forEach((b) => { if (!b.stokAwal && !b.tutupBuku && b.tanggal && (!p || b.tanggal < p)) p = b.tanggal; }); const q = awalPotret('pertama'); return q && (!p || q < p) ? q : p; }
