// KATALOG KASIR — dokumen ringkasanKasir/aktif yang dibaca HP kasir (kasir-darurat-nominal.html & kasir.html, akun kasir@) untuk tuts bernama
// barang, harga, modal, dan daftar bon. Putaran 25c (owner 27 Sep 2026): /baru/ PENERBITNYA; index.html tidak menulisnya lagi (penjaga, JALUR_DIAM).
//
// BENTUK TETAP (keputusan owner 27 Sep, pilihan "tetap dulu"): isinya disusun penyusun VERBATIM index.html (susunIsiKatalogKasir, disalin
// alat-uji/pindah_mesin.py) dan dokumennya berkunci & berurutan persis terbitkanRingkasanKasir() — byte-sama untuk data yang sama. Modal & daftar
// bon ikut terkirim ke akun kasir seperti sejak Agustus; dicabut di putaran tablet (docs/peta-pindahan-terakhir.md §6 A, peta-hak-akses.md §8).
// SATU TAMBAHAN (owner 30 Sep, audit 39b "cara persis"): dua kunci terakhir — `bayarBonTerhitung` = id SEMUA pembayaran bon yang dihitung di
// `piutang` dokumen ini (kkBayarTerhitung) dan `bayarBonSejak` = awal buku berjalan (sesudah tutup buku terakhir; '' bila belum pernah). Empat
// bagian lainnya tetap byte-sama index.html. HP kasir v30: id tercantum = sudah dihitung; bertanggal sebelum `bayarBonSejak` = sudah terserap saldo
// pembuka tutup buku; selain itu tetap dikurangkan. HP versi lama & katalog tanpa kunci ini tetap memakai tebakan waktu server (39b no. 4).
// Isinya murni dari DATA (tanpa jam perangkat penerbit): dua perangkat owner menyusun katalog yang sama (tinjauan persis P2/P3).
// Dokumen turunan, BUKAN catatan: ditulis apa adanya (tanpa atribusi, tanpa baris jejak), sama dengan index.html.
//
// KAPAN TERBIT: sesudah SETIAP perubahan data (bukan daftar kejadian yang dipilih tangan — pasti ada yang tertinggal), jeda KK_JEDA_MS seperti
// index.html, hanya kalau isinya BERBEDA dengan dokumen di server; dan terbit harga menyertakannya dalam kiriman yang SAMA (kkSertakan).
// Gerbang kkBolehTerbit(): owner, Firestore (bukan cadangan), semua koleksi sudah dijawab SERVER (bukan salinan perangkat yang bisa basi), dokumen
// katalog di server sudah terbaca, tersambung. Kalau ragu, TIDAK terbit — katalog lama di HP kasir lebih aman daripada katalog dari data basi.
import { susunIsiKatalogKasir, kunciPelanggan } from '../mesin/pembantu.js';
import { arSaringKatalogKasir } from '../layar/arsip-logika.js';
import { wbSaringKatalogKasir } from '../layar/wadah-bernama-logika.js';
import { cacheMentah, denganCacheSementara, ambilPiutangMutasi } from './toko.js';
import { kpPerangkatKasir, kpNomorVersiKasir, kpVersiKasirCukup, kpNamaAplikasiKasir, KP_VERSI_HARI } from './kunci-periode.js';
import { waktuSetempat } from '../inti/format.js';

export const KK_KOLEKSI = 'ringkasanKasir';
export const KK_ID = 'aktif';
export const KK_JEDA_MS = 4000;
// Versi kasir TERBARU yang disajikan = VERSI sw-kasir.js (uji_katalog_kasir.py & uji_antrean_kasir.py membandingkannya; naik bersama).
export const KK_VERSI_KASIR_TERBARU = 'kasir-v30';
// Versi PERTAMA yang mengambil katalog sendiri tiap layar HP dinyalakan & tiap 5 menit (25c). Di bawahnya = harga baru baru sampai saat dibuka ulang;
// di antara ini dan versi terbaru (39b no. 4: v27 belum punya buku kecil bayar bon) = cukup diberi tahu, pemeriksaan katalog lamanya tetap jalan.
export const KK_VERSI_AMBIL_SENDIRI = 'kasir-v27';
const KK_BASI_MS = 6 * 60000;   // HP yang berdenyut lebih dari 6 menit sesudah katalog terbit tapi masih memegang yang lama = belum mengambil

// ---- keadaan dokumen di server (diisi pendengar firebase.js; owner saja) ----
let _kkServer = { ada: null, dok: null, dariServer: false };   // ada: null = belum terbaca · false = belum pernah diterbitkan
let _kkTerbit = { pada: '', galat: '' };
export function kkSetelServer(dok, dariServer) { _kkServer = { ada: !!dok, dok: dok || null, dariServer: !!dariServer }; }
export function kkLupakanServer() { _kkServer = { ada: null, dok: null, dariServer: false }; }
export function kkServer() { return Object.assign({}, _kkServer); }
export function kkCatatTerbit(pada, galat) { _kkTerbit = { pada: pada || _kkTerbit.pada, galat: galat || '' }; }

/** Isi katalog dari data sekarang — penyusun VERBATIM index.html. null = gagal disusun (tidak ada yang diterbitkan).
 *  Putaran 27: baris nama yang DIARSIPKAN owner dibuang dari HASILNYA (arsip-logika.js arSaringKatalogKasir); tanpa arsip = byte-sama index.html.
 *  Putaran 28: buku STOK WADAH memakai harga liter wadahnya & nama wadah berstok sendiri tidak menjual literan atas nama mereknya (wbSaringKatalogKasir);
 *  tanpa wadah berstok sendiri = byte-sama index.html. */
export function kkIsi() { const isi = wbSaringKatalogKasir(arSaringKatalogKasir(susunIsiKatalogKasir())); return isi ? Object.assign(isi, { bayarBonTerhitung: kkBayarTerhitung(), bayarBonSejak: kkBayarSejak() }) : isi; }
/** Cara persis (owner 30 Sep): id SEMUA pembayaran bon yang dihitung hitungPiutang() — penyusun `piutang` di atas — persis saringannya (tipe bayar,
 *  nama yang punya kunci pelanggan), TANPA jendela hari (tinjauan P2: jendela memakai tanggal dari jam HP & jam penerbit). Tutup buku mengarsipkan
 *  pembayaran tahun lama (tahunnya selesai, daftarnya mulai lagi dari kecil); diurutkan supaya pembanding isi tidak bergantung urutan cache. */
export function kkBayarTerhitung() {
  return ambilPiutangMutasi().filter((m) => m && m.tipe === 'bayar' && kunciPelanggan(m.namaPelanggan)).map((m) => String(m.id)).sort();
}
/** Awal buku berjalan = 1 Januari sesudah tahun terakhir yang ditutup (saldo pembuka piutang bertanda tutupBuku + tahunDari); '' = belum pernah tutup
 *  buku. Pembayaran bertanggal sebelum ini sudah TERSERAP saldo pembuka (dokumennya pindah ke arsip, id-nya tidak tercantum lagi — tinjauan P1). */
export function kkBayarSejak() {
  let t = null; ambilPiutangMutasi().forEach((m) => { if (m && m.tutupBuku) { const n = Number(m.tahunDari); if (isFinite(n) && n > 0 && (t === null || n > t)) t = n; } });
  return t === null ? '' : (t + 1) + '-01-01';
}
/** Dokumen yang ditulis: kunci & urutan PERSIS terbitkanRingkasanKasir() index.html. */
export function kkDokumen(isi, kini) {
  return { id: KK_ID, diperbaruiPada: kini, kemasan: isi.kemasan, merkKarung: isi.merkKarung, bahanLiteran: isi.bahanLiteran, piutang: isi.piutang, bayarBonTerhitung: isi.bayarBonTerhitung || [], bayarBonSejak: isi.bayarBonSejak || '' };
}
// Pembanding ISI (bukan umur, sama dengan index.html): kunci objek diurutkan dulu — Firestore mengembalikan peta dengan urutan kuncinya sendiri,
// jadi JSON.stringify apa adanya bisa berbeda walau isinya sama, dan katalog akan diterbitkan ulang tanpa henti.
function kkUrut(x) {
  if (Array.isArray(x)) return x.map(kkUrut);
  if (x && typeof x === 'object') { const o = {}; Object.keys(x).sort().forEach((k) => { o[k] = kkUrut(x[k]); }); return o; }
  return x;
}
export function kkKanon(x) {
  const d = x || {};
  return JSON.stringify(kkUrut({ kemasan: d.kemasan || [], merkKarung: d.merkKarung || [], bahanLiteran: d.bahanLiteran || {}, piutang: d.piutang || [], bayarBonTerhitung: d.bayarBonTerhitung || [], bayarBonSejak: d.bayarBonSejak || '' }));
}
/** true = isi sekarang belum sampai ke katalog di server · false = sama · null = belum bisa tahu (dokumen server belum terbaca / isi gagal disusun). */
export function kkTertinggal(isi) {
  const s = _kkServer; const x = isi === undefined ? kkIsi() : isi;
  if (!x || s.ada === null) return null;
  if (!s.ada) return true;
  return kkKanon(x) !== kkKanon(s.dok);
}
/**
 * Gerbang terbit otomatis. k = { owner, sumber, koleksiSiap, koleksiTotal, dariCache (jumlah koleksi yang jawaban terakhirnya dari salinan perangkat),
 * ditolak (jumlah pendengar ditolak rules), online }. → { boleh, sebab }.
 */
export function kkBolehTerbit(k) {
  if (!k || !k.owner) return { boleh: false, sebab: 'bukan owner — katalog kasir hanya diterbitkan owner' };
  if (k.sumber !== 'firestore') return { boleh: false, sebab: 'bukan data server (cadangan / belum tersambung)' };
  if (!k.online) return { boleh: false, sebab: 'tidak tersambung' };
  if (k.ditolak > 0) return { boleh: false, sebab: 'ada koleksi yang ditolak server — katalog bisa tidak lengkap' };
  if (!(k.koleksiTotal > 0) || k.koleksiSiap < k.koleksiTotal) return { boleh: false, sebab: 'data belum termuat semua' };
  if (k.dariCache > 0) return { boleh: false, sebab: 'sebagian data masih salinan perangkat (belum dijawab server)' };
  if (_kkServer.ada === null || !_kkServer.dariServer) return { boleh: false, sebab: 'katalog di server belum terbaca' };
  return { boleh: true, sebab: '' };
}
/**
 * Terbit harga (dan kiriman owner lain yang mengubah harga): katalog SESUDAH kiriman ini ikut di kiriman yang SAMA — HP kasir tidak pernah membaca harga
 * lama sesudah harga barunya terbit. Tidak berubah dari server → tidak ikut. Server belum terbaca → tetap ikut (isi sesudah kiriman = kebenaran).
 */
export function kkSertakan(dokumen, kini) {
  const daftar = dokumen || [];
  if (daftar.some((d) => d.koleksi === KK_KOLEKSI)) return daftar;
  const isi = denganCacheSementara(daftar, kkIsi); if (!isi) return daftar;
  if (_kkServer.ada === true && kkKanon(isi) === kkKanon(_kkServer.dok)) return daftar;
  return daftar.concat([{ koleksi: KK_KOLEKSI, data: kkDokumen(isi, kini) }]);
}
/** Dokumen katalog ditulis APA ADANYA (bentuk index.html): penulis pusat tidak memasang atribusi & tidak menulis baris jejak untuknya. */
export const kkMentah = (koleksi) => koleksi === KK_KOLEKSI;

/**
 * Beranda (owner): { status: kalimat "katalog kasir: diperbarui …", awas, perhatian: [{ teks, nilai, awas }] } — perhatian = katalog tertinggal,
 * HP kasir yang belum bisa mengambil katalog sendiri (versi < KK_VERSI_AMBIL_SENDIRI), HP yang belum memakai versi terbaru, HP penjaga yang masih memegang
 * katalog lama.
 */
export function kkBeranda(kini) {
  const s = _kkServer; const t = (kini instanceof Date ? kini : new Date()).getTime(); const out = [];
  const tg = kkTertinggal();
  const stempel = s.ada && s.dok && s.dok.diperbaruiPada ? waktuSetempat(s.dok.diperbaruiPada) : '';
  const status = s.ada === null ? 'Katalog kasir: belum terbaca dari server'
    : !s.ada ? 'Katalog kasir: belum pernah diterbitkan'
    : 'Katalog kasir: diperbarui ' + (stempel || 'waktu tidak tercatat') + (tg ? ' · ada perubahan harga atau stok yang BELUM sampai' : tg === false ? ' · sama dengan data sekarang' : '');
  if (tg) out.push({ teks: 'Katalog kasir: ada perubahan harga atau stok yang belum sampai ke HP kasir' + (_kkTerbit.galat ? ' — ' + _kkTerbit.galat : ''), nilai: _kkTerbit.galat ? 'gagal terbit' : 'menunggu terbit', awas: !!_kkTerbit.galat });
  const terbitMs = s.ada && s.dok && s.dok.diperbaruiPada ? new Date(s.dok.diperbaruiPada).getTime() : NaN;
  cacheMentah('perangkat').filter(kpPerangkatKasir).forEach((p) => {
    const x = p.pada ? new Date(p.pada).getTime() : NaN; if (!isFinite(x) || t - x > KP_VERSI_HARI * 24 * 3600000) return;
    const nama = (p.nama || p.id) + ' · ' + kpNamaAplikasiKasir(p);
    // di bawah versi terbaru: HP itu belum mengambil katalog sendiri & belum melaporkan katalog yang dipegangnya. Di bawah lantai 25b sudah disebut
    // kpPerhatianPerangkat (kunci-periode-logika.js) — tidak diulang di sini.
    if (kpNomorVersiKasir(p.versi) < kpNomorVersiKasir(KK_VERSI_AMBIL_SENDIRI)) {
      if (kpVersiKasirCukup(p.versi)) out.push({ teks: 'HP ' + nama + ': masih ' + p.versi + ' — harga baru baru sampai saat aplikasinya dibuka ulang', nilai: 'buka ulang', awas: false });
      return;
    }
    // sudah mengambil katalog sendiri tapi belum versi terbaru: disebut (tanpa awas) — pemeriksaan katalog lama di bawah TETAP jalan untuknya.
    if (kpNomorVersiKasir(p.versi) < kpNomorVersiKasir(KK_VERSI_KASIR_TERBARU)) out.push({ teks: 'HP ' + nama + ': masih ' + p.versi + ' — versi ' + KK_VERSI_KASIR_TERBARU + ' terpasang saat aplikasinya dibuka ulang', nilai: 'buka ulang', awas: false });
    const pegang = p.katalog ? new Date(p.katalog).getTime() : NaN;
    if (p.aplikasi === 'darurat' && isFinite(terbitMs) && x - terbitMs > KK_BASI_MS && (!isFinite(pegang) || pegang < terbitMs)) {
      out.push({ teks: 'HP ' + nama + ': masih memegang katalog ' + (isFinite(pegang) ? waktuSetempat(p.katalog) : 'lama') + ' (denyut ' + waktuSetempat(p.pada) + ')', nilai: 'katalog lama', awas: true });
    }
  });
  return { status, awas: !!tg && !!_kkTerbit.galat, perhatian: out, terbitGalat: _kkTerbit.galat };
}
