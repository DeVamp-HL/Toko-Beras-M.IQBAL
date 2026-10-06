// LAYAR HARGA & PEMASOK — H3 BELANJA (dikunci owner 18 Sep 2026: gabungan Isi Truk · Kapan Habis · Daftar di Kertas). Logika tanpa DOM, awalan bl.
// Aturan dari sistem berjalan (hitungSaranBelanja index.html): disarankan bila habis ≤ AMBANG hari (7), butuh = laju × TARGET hari (14) − sisa, dibulatkan KE ATAS ke karung
// yang biasa dipakai merek itu (merkPunyaKarungBerat); laju = mesin beku hitungLajuPakai (14 hari). Tanpa laju → TIDAK menebak (disebut).
// Owner memesan MUATAN, bukan uang (memori muatan-tiga-ton-tetap): muatan truk bawaan = median berat kedatangan nyata (TERUKUR, disebut), owner boleh mengubahnya di Atur.
// Tiap pemasok membawa mereknya sendiri (harga terakhir per pemasok dari kedatangan, tanggalnya selalu ditulis); RODA MAS biasa BON, SEJATI biasa TUNAI → perkiraan uangnya dibaca beda.
// Pesanan yang dikirim = koleksi BARU pesananPemasok (menunggu datang / batal); "sudah datang" dibaca dari kedatangan pemasok itu SESUDAH pesanan (tidak ditebak dari stok).
// owner 7 Okt: "belanja pakai harga modal yang sudah ada sebelumnya" — nama merek karung berganti-ganti (TH House lalu TH Grand dari pemasok yang sama), pemasok
// mengenal barangnya dari HARGA (bonnya menulis kode karung + harga per kg). Daftar belanja & pesanan dikelompokkan per pemasok lalu per HARGA BELI TERAKHIR
// per kg dari pemasok itu (blKelompokHarga); merek seharga = satu baris, karungnya dijumlah.
// Tinjauan E1 (7 Okt): PERLU & SARAN dihitung per baris harga dari stok & laju GABUNGAN merek seharga (pemasok × harga × berat × jenis), lalu karungnya dibagi ke
// merek di dalamnya (yang paling cepat habis dulu) — "Kapan habis" tetap menggambar stok per merek. Nama yang diarsipkan tidak ikut belanja. Merek berkelas mutu
// yang harganya lebih lama dari kiriman terbaru kelas yang sama dari pemasok itu ikut harga kelas itu (baris hampir kembar dirapikan, hanya bila harga kelasnya satu).
import { hitungStokKarungPerMerk, hitungLajuPakai, kasPada } from '../mesin/beku.js';
import { merkPunyaKarungBerat, JENDELA_LAJU_HARI, jenisUntukMerk } from '../mesin/pembantu.js';
import { ambilSemuaBatch, ambilPesananPemasok, cacheMentah, stokMerekSaja, lajuLintas, petaUkuran } from '../data/toko.js';
import { RP, ANGKA, hariIniIso, tanggalPendek } from '../inti/format.js';
import { daftarPemasok, tempoPemasok, nomorWa, bpTambahHari, pemasokSungguhan } from './bon-pemasok-logika.js';
import { arPeta, arBeras } from './arsip-logika.js';
import { wbNamaKelas } from './wadah-bernama-logika.js';
import { kmKelasMerk, kmKelasSendiri, kmTerisi } from './kelas-merek-logika.js';
import { vrBatas } from './varian-logika.js';

export const ATUR_BELANJA_BAWAAN = { ambangHari: 7, targetHari: 14, muatanKg: 0 };
export const TAB_BELANJA = [['truk', 'Isi truk'], ['hari', 'Kapan habis'], ['kertas', 'Daftar']];
const blAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const blKosong = (v) => v === undefined || v === null || String(v).trim() === '';
export const blKG = (n) => ANGKA(n) + ' kg';

/** Muatan truk yang TERUKUR: median kg dari 12 kedatangan nyata terakhir, dibulatkan ke 25 kg. 0 = belum ada kedatangan. */
export function muatanTerukur() {
  const kg = ambilSemuaBatch().filter((b) => !b.stokAwal && pemasokSungguhan(b.pemasok)).sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || (Number(b.id) || 0) - (Number(a.id) || 0)).slice(0, 12)
    .map((b) => (b.merkList || []).reduce((a, m) => a + (Number(m.totalKg) || 0), 0)).filter((x) => x > 0).sort((a, b) => a - b);
  if (!kg.length) return 0; const m = kg.length % 2 ? kg[(kg.length - 1) / 2] : (kg[kg.length / 2 - 1] + kg[kg.length / 2]) / 2; return Math.round(m / 25) * 25;
}
export function aturBelanja() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'belanja') || null; const ambil = (k, syarat) => (a && isFinite(Number(a[k])) && syarat(Number(a[k])) ? Number(a[k]) : null);
  const muat = ambil('muatanKg', (n) => n > 0);
  return { ambangHari: ambil('ambangHari', (n) => n >= 0 && n <= 60) ?? ATUR_BELANJA_BAWAAN.ambangHari, targetHari: ambil('targetHari', (n) => n > 0 && n <= 90) ?? ATUR_BELANJA_BAWAAN.targetHari, muatanKg: muat === null ? muatanTerukur() : muat, muatanTerukur: muat === null, dariOwner: !!a };
}
export function susunAturBelanja(isi, w) {
  const kini = aturBelanja(); const data = { id: 'belanja', tanggal: w.tanggal, jam: w.jam };
  const baca = (k, syarat, teks) => { if (blKosong(isi[k])) { data[k] = kini[k]; return ''; } const n = Math.round(blAngka(isi[k])); if (!syarat(n)) return teks; data[k] = n; return ''; };
  const salah = baca('ambangHari', (n) => n >= 0 && n <= 60, 'Disarankan kalau habis dalam: 0–60 hari') || baca('targetHari', (n) => n > 0 && n <= 90, 'Belanja untuk berapa hari: 1–90 (tidak boleh nol)') || baca('muatanKg', (n) => n > 0 && n <= 30000, 'Muatan satu truk: 1–30.000 kg (tidak boleh nol)');
  if (salah) return { tolak: salah };
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { aturL: null, kabar: 'Aturan belanja disimpan — disarankan bila habis ≤ ' + data.ambangHari + ' hari · belanja untuk ' + data.targetHari + ' hari · muatan truk ' + blKG(data.muatanKg), kabarAwas: false } };
}
// tinjauan E1: stok 0 (atau buku minus) yang MASIH laku = habis hari ini — dulu ikut "belum ada gerak, tidak ditebak" sehingga baris harga yang stok gabungannya
// habis tidak pernah disarankan (Stok › Apa yang harus dibeli sudah menghitungnya habis). Tanpa laju tetap tidak ditebak.
export const hariHabis = (sisa, laju) => (!(laju > 0) ? null : !(sisa > 0) ? 0 : Math.floor(sisa / laju + 1e-9));
export const kataHabis = (h) => (h === null ? 'belum ada gerak ' + JENDELA_LAJU_HARI + ' hari — tidak ditebak' : h <= 0 ? 'habis hari ini' : '±' + h + ' hari lagi');

/** Pesanan yang masih menunggu datang: status 'batal'/'datang' tersimpan menang; kalau tidak, DATANG bila ada kedatangan pemasok itu sesudah pesanan. */
export function pesananSemua() {
  const batch = ambilSemuaBatch().filter((b) => !b.stokAwal && pemasokSungguhan(b.pemasok));
  return ambilPesananPemasok().map((p) => { const sesudah = batch.filter((b) => String(b.pemasok || '').trim() === p.pemasok && ((b.tanggal || '') > (p.tanggal || '') || ((b.tanggal || '') === (p.tanggal || '') && (b.jam || '') > (p.jam || '')))).sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal)) || String(a.jam || '').localeCompare(String(b.jam || '')));
    const status = p.status === 'batal' ? 'batal' : p.status === 'datang' ? 'datang' : sesudah.length ? 'datang' : 'menunggu';
    return Object.assign({}, p, { status, datangTanggal: status === 'datang' ? (p.datangTanggal || (sesudah[0] ? sesudah[0].tanggal : '')) : '' }); }).sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || (Number(b.id) || 0) - (Number(a.id) || 0));
}
export const pesananMenunggu = () => pesananSemua().filter((p) => p.status === 'menunggu');

// ---------- KELOMPOK HARGA: satu tempat untuk kunci, harga yang dipakai, dan perlu/saran gabungan (tinjauan E1) ----------
const blBerat = (m, uk) => (uk[m] ? uk[m].berat : merkPunyaKarungBerat(m, 50) ? 50 : merkPunyaKarungBerat(m, 25) ? 25 : 50);
const blInduk = (m, uk) => (uk[m] ? uk[m].induk : m);
const blJenis = (m, uk) => String(jenisUntukMerk(blInduk(m, uk)) || '').trim();
/** Kelas mutu yang SUDAH dipetakan (owner / nama wadah / kelas sendiri / dipakai) — tebakan tidak dipakai untuk menyamakan harga. '' = tidak ada. Diingat per hitungan. */
const blKelasMemo = (uk) => { const o = {}; return (m) => { if (o[m] === undefined) { const K = kmKelasMerk(blInduk(m, uk)); o[m] = K.kelas && kmTerisi(K.asal) ? K.kelas : ''; } return o[m]; }; };
const blTglPendek = (t, acuan) => { const s = tanggalPendek(t); return String(t || '').slice(0, 4) === String(acuan || '').slice(0, 4) ? s.replace(/ \d{4}$/, '') : s; };
/**
 * Harga kelas terkini per pemasok (tinjauan E1 — baris hampir kembar): pemasok × kelas mutu yang dipetakan × jenis × berat → tanggal kiriman TERBARU kelas itu
 * dari pemasok itu dan harga-harganya di tanggal itu. Dipakai hanya bila di tanggal itu harganya SATU (dua harga sekelas di satu kiriman = tidak ditebak).
 */
function blHargaKelas(pem, uk, arsip, kelasDari) {
  const out = {};
  pem.forEach((p) => Object.keys(p.hargaPerMerk).forEach((m) => { if (arBeras(m, arsip)) return; const K = kelasDari(m); if (!K) return; const t = p.hargaPerMerk[m].terakhir;
    const k = p.nama + '|' + K + '|' + blJenis(m, uk) + '|' + blBerat(m, uk); const o = out[k] = out[k] || { tanggal: '', harga: [], merk: [] };
    if (t.tanggal > o.tanggal) { o.tanggal = t.tanggal; o.harga = [t.hargaPerKg]; o.merk = [m]; } else if (t.tanggal === o.tanggal) { if (o.harga.indexOf(t.hargaPerKg) < 0) o.harga.push(t.hargaPerKg); o.merk.push(m); } }));
  return out;
}
/**
 * Harga yang DIPAKAI satu merek dari satu pemasok: harga beli terakhirnya; KECUALI merek itu berkelas mutu (dipetakan) dan pemasok itu sudah mengirim kelas yang
 * sama SESUDAHNYA dengan satu harga lain yang bedanya masih dalam batas "sama barangnya" owner (Barang masuk › Atur, batas varian, bawaan 5 %) → ikut harga kelas
 * terbaru itu (lalu = harga lamanya, tetap disebut). Beda lebih besar = barang lain menurut aturan owner sendiri → harganya sendiri, hanya ditandai umurnya.
 */
function blPakaiHarga(m, s, uk, ref, kelasDari) {
  if (!s) return null;
  const K = kelasDari(m); const r = K ? ref[s.pemasok + '|' + K + '|' + blJenis(m, uk) + '|' + blBerat(m, uk)] : null;
  const dekat = r && r.harga.length === 1 && s.harga > 0 && Math.abs(r.harga[0] - s.harga) / s.harga * 100 <= vrBatas() + 1e-9;
  if (dekat && r.tanggal > s.tanggal && r.harga[0] !== s.harga) return { pemasok: s.pemasok, harga: r.harga[0], tanggal: r.tanggal, kelas: K, lalu: { harga: s.harga, tanggal: s.tanggal }, dari: r.merk.slice(), kode: s.kode || '' };
  return { pemasok: s.pemasok, harga: s.harga, tanggal: s.tanggal, kelas: K, lalu: null, dari: [], kode: s.kode || '' };
}
/** Kunci baris harga satu baris belanja (pemasok sudah dipisah di luar): berat × harga yang dipakai × jenis; tanpa harga beli → baris sendiri. */
function blKunci(b, uk) {
  const harga = b.pakai && Number(b.pakai.harga) > 0 ? Number(b.pakai.harga) : 0; const berat = Number(b.berat) || 50; const jenis = harga ? blJenis(b.merk, uk) : '';
  const kunci = harga ? berat + '|' + harga + '|' + jenis : 'x|' + b.merk;
  return { harga, berat, jenis, kunci };
}
/**
 * PERLU & SARAN per KELOMPOK HARGA (tinjauan E1, sanggahan: merek yang habis hari ini disarankan penuh padahal merek seharga dari pemasok yang sama masih
 * punya stok ratusan kg — kelebihan pesan berkuintal-kuintal). Pemasok mengenal barangnya dari
 * harga, jadi stok barang itu = Σ sisa merek seharga dan lakunya = Σ laju: hari = Σ sisa ÷ Σ laju, saran = laju × target − sisa (dibulatkan ke karung penuh).
 * Karung saran dibagi ke merek di dalamnya satu-satu ke yang paling cepat habis sesudah pembagian (merek tanpa laju & yang sudah dipesan tidak menerima).
 * Satu baris yang punya pesanan menunggu = sudah dipesan (tidak disarankan lagi). Merek sendirian = rumus lama persis.
 */
function blBagiSaran(rows, atur, uk) {
  const kel = {}; const urut = [];
  rows.forEach((x) => { const K = blKunci(x, uk); const k = (x.pakai ? x.pakai.pemasok : '') + '|' + K.kunci;
    if (!kel[k]) { kel[k] = { kunci: K.kunci, pemasok: x.pakai ? x.pakai.pemasok : '', harga: K.harga, berat: K.berat, isi: [] }; urut.push(kel[k]); } kel[k].isi.push(x); });
  urut.forEach((G) => {
    const sisa = Math.round(G.isi.reduce((a, x) => a + x.sisa, 0) * 100) / 100; const laju = G.isi.reduce((a, x) => a + x.laju, 0); const hari = hariHabis(sisa, laju); const dipesan = G.isi.some((x) => !!x.dipesan);
    const butuh = laju > 0 ? Math.max(0, laju * atur.targetHari - sisa) : 0; const saranK = Math.ceil(butuh / G.berat);
    const perlu = hari !== null && hari <= atur.ambangHari && saranK > 0 && !dipesan;
    const bagi = {}; G.isi.forEach((x) => { bagi[x.merk] = 0; }); const calon = G.isi.filter((x) => x.laju > 0 && !x.dipesan);
    const cukup = (x) => (x.sisa + bagi[x.merk] * G.berat) / x.laju;
    for (let i = 0; i < saranK && calon.length; i++) { const c = calon.slice().sort((a, b) => cukup(a) - cukup(b) || a.merk.localeCompare(b.merk))[0]; bagi[c.merk] += 1; }
    const info = { kunci: G.kunci, pemasok: G.pemasok, harga: G.harga, n: G.isi.length, sisa, laju, hari, saranK, perlu, dipesan };
    G.isi.forEach((x) => { const teman = G.isi.filter((y) => y !== x).map((y) => y.merk);
      x.saranK = bagi[x.merk]; x.perlu = perlu && x.saranK > 0; x.kel = Object.assign({ teman }, info);
      // stok merek ini sendiri ≤ ambang, tapi barang seharga menutupnya (masih cukup bersama / sudah dipesan / saran baris ini jatuh ke merek lain)
      const tutup = teman.length > 0 && !x.dipesan && !x.perlu && x.hari !== null && x.hari <= atur.ambangHari;
      x.tutup = tutup ? (dipesan ? 'yang seharga sudah dipesan' : perlu ? 'saran baris harga ini masuk ke ' + G.isi.filter((y) => bagi[y.merk] > 0).map((y) => y.merk).join(', ') : 'yang seharga masih cukup bersama — ' + kataHabis(hari)) : '';
      x.gabungTeks = teman.length ? 'seharga ' + teman.join(', ') + (G.pemasok ? ' (' + G.pemasok + (G.harga ? ' ' + RP(G.harga) + '/kg' : '') + ')' : '') + ': bersama ' + blKG(Math.round(sisa)) + ' · ' + kataHabis(hari) + (dipesan ? ' · sudah dipesan' : perlu ? ' · saran ' + saranK + ' karung untuk baris harga ini' : '') : ''; });
  });
}

/** Tiap merek yang bisa dibeli: sisa & laju dari mesin, harga terakhir per pemasok, saran karung per kelompok harga (blBagiSaran). Nama diarsipkan tidak ikut. */
export function daftarBelanja(kini) {
  const atur = aturBelanja(); const stok = hitungStokKarungPerMerk(); const laju = lajuLintas(hitungLajuPakai()).kgMerk || {}; const pem = daftarPemasok(); const menunggu = pesananMenunggu(); const arsip = arPeta();
  // putaran 28: stok wadah diisi dari karung, tidak dibeli
  const merks = new Set(Object.keys(stokMerekSaja(stok))); pem.forEach((p) => Object.keys(p.hargaPerMerk).forEach((m) => merks.add(m)));
  // owner 7 Okt (pesanan per harga): buku per ukuran 'Merek 25 kg' dipesan dalam karung 25 kg — pisah buku (pindah jadi-karung-utuh) membuatnya tampak "punya karung 50 kg"
  const uk = petaUkuran(); const kelasDari = blKelasMemo(uk); const ref = blHargaKelas(pem, uk, arsip, kelasDari);
  // tinjauan E1: nama yang DIARSIPKAN tidak dibeli lagi (tidak tampil di rak) — dulu tetap disarankan (IR42 Select dkk.)
  const merk = Array.from(merks).filter((m) => !arBeras(m, arsip)).map((m) => { const sisa = (stok[m] || {}).sisaKg || 0; const l = laju[m] || 0; const hari = hariHabis(sisa, l); const berat = blBerat(m, uk);
    const sumber = pem.filter((p) => p.hargaPerMerk[m]).map((p) => ({ pemasok: p.nama, harga: p.hargaPerMerk[m].terakhir.hargaPerKg, tanggal: p.hargaPerMerk[m].terakhir.tanggal, kode: p.hargaPerMerk[m].terakhir.merkPemasok || '' })).sort((a, b) => a.harga - b.harga);
    const dipesan = menunggu.find((p) => (p.baris || []).some((b) => b.merk === m)) || null;
    return { merk: m, sisa: Math.round(sisa * 100) / 100, laju: l, lajuTeks: String(Math.round(l * 10) / 10).replace('.', ','), hari, berat, saranK: 0, perlu: false, sumber, termurah: sumber[0] || null, pakai: blPakaiHarga(m, sumber[0] || null, uk, ref, kelasDari), dipesan, kritis: hari !== null && hari <= 2,
      sisaTeks: 'sisa ' + blKG(Math.round(sisa)) + (l > 0 ? ' · laku ' + String(Math.round(l * 10) / 10).replace('.', ',') + ' kg/hari' : '') + ' · ' + kataHabis(hari) }; })
    .filter((x) => x.sisa > 0 || x.laju > 0 || x.sumber.length);
  blBagiSaran(merk, atur, uk);
  return { merk, ref, kelasDari, pemasok: pem.filter((p) => p.kedatangan > 0).map((p) => ({ nama: p.nama, kunci: p.kunci, cara: p.caraBiasa, caraTeks: p.caraTeks, tempo: tempoPemasok(p.nama), kontak: p.kontak, orang: p.orang, terakhir: p.terakhir })), atur, tanpaPemasok: merk.filter((x) => !x.sumber.length).map((x) => x.merk), menunggu };
}
/** Daftar belanja yang sedang disusun: pesan = { merk: { p: pemasok, k: karung } }. Per pemasok: muatan, karung, perkiraan uang; truk; kertas; kalimat uang (bon vs tunai). */
export function hitungBelanja(pesan, kini) {
  const D = daftarBelanja(kini); const atur = D.atur; const P = pesan || {}; const kas = kasPada(); const uk = petaUkuran();
  const baris = D.merk.map((x) => { const o = P[x.merk] || null; const k = o && o.k > 0 ? Math.round(o.k) : 0; const sumber = (o && x.sumber.find((s) => s.pemasok === o.p)) || x.termurah || null;
    const pakai = sumber === x.termurah ? x.pakai : blPakaiHarga(x.merk, sumber, uk, D.ref, D.kelasDari);
    const kg = k * x.berat; const rp = pakai ? kg * pakai.harga : 0;
    return Object.assign({}, x, { k, kg, rp, sumber, pakai, adaHarga: !!sumber, hariSesudah: x.laju > 0 ? Math.floor((x.sisa + kg) / x.laju + 1e-9) : null,
      hargaTeks: pakai ? pakai.pemasok + ' · ' + RP(pakai.harga) + '/kg (harga ' + tanggalPendek(pakai.tanggal) + (pakai.lalu ? ', kelas ' + pakai.kelas + '; ' + x.merk + ' terakhir ' + RP(pakai.lalu.harga) + ' ' + tanggalPendek(pakai.lalu.tanggal) : '') + ')' + (x.sumber.length > 1 ? ' · ganti ›' : '') : 'belum pernah dibeli — pemasok & harganya belum diketahui',
      saranTeks: x.saranK > 0 ? 'saran ' + x.saranK + ' karung' : 'tambah', sesudahTeks: k && x.hariSesudah !== null ? 'jadi cukup ±' + x.hariSesudah + ' hari' : '', dipesanTeks: x.dipesan ? 'sudah dipesan ' + tanggalPendek(x.dipesan.tanggal) + ' — menunggu datang' : '' }); });
  const perP = D.pemasok.map((p) => { const d = baris.filter((b) => b.k > 0 && b.sumber && b.sumber.pemasok === p.nama); const kg = d.reduce((a, b) => a + b.kg, 0), rp = d.reduce((a, b) => a + b.rp, 0), karung = d.reduce((a, b) => a + b.k, 0);
    const milik = baris.filter((b) => b.sumber && b.sumber.pemasok === p.nama);
    const uang = !karung ? '' : p.cara === 'bon' ? 'Biasanya BON — jadi utang ±' + RP(rp) + (p.tempo.hari > 0 ? ', jatuh tempo ±' + tanggalPendek(bpTambahHari(hariIniIso(kini || new Date()), p.tempo.hari)) + ' kalau datang hari ini' : ', tempo belum disepakati') + '. Yang tunai cuma ongkos bongkar.'
      : p.cara === 'tunai' ? 'Biasanya TUNAI — perlu ±' + RP(rp) + ' waktu barang datang. ' + (kas === null ? 'Uang toko belum bisa dihitung (titik kas belum disetel).' : 'Uang toko sekarang ' + RP(kas) + (rp > kas ? ' — KURANG ' + RP(rp - kas) + '.' : ' — cukup.')) : 'Belum ada kedatangan dari pemasok ini, jadi belum tahu biasanya bon atau tunai. Perkiraan ±' + RP(rp) + '.';
    const saran = baris.filter((b) => b.perlu && !b.k && b.sumber && b.sumber.pemasok === p.nama); const gMilik = blKelompokHarga(milik.filter((b) => !b.dipesan), p.terakhir, milik);
    return { pemasok: p.nama, kunci: p.kunci, cara: p.caraBiasa, caraTeks: p.caraTeks, tempo: p.tempo, kontak: p.kontak, terakhir: p.terakhir, d, kg, rp, karung, sisaMuat: atur.muatanKg > 0 ? atur.muatanKg - kg : 0, lebih: atur.muatanKg > 0 ? Math.max(0, kg - atur.muatanKg) : 0, uangTeks: uang, uangAwas: p.cara === 'tunai' && kas !== null && rp > kas,
      // owner 7 Okt: g = pesanan per HARGA (truk, pesanan WA); gMilik = merek pemasok ini yang belum dipesan, per harga (daftar di bawah truk)
      milik, saran, saranG: gMilik.filter((g) => g.merk.some((b) => b.perlu && !b.k)).length, saranKarung: saran.reduce((a, b) => a + b.saranK, 0), g: blKelompokHarga(d, p.terakhir, milik), gMilik, dipesanMerk: milik.filter((b) => !!b.dipesan) }; });
  const totKarung = perP.reduce((a, r) => a + r.karung, 0), totKg = perP.reduce((a, r) => a + r.kg, 0), totRp = perP.reduce((a, r) => a + r.rp, 0);
  const perluSemua = baris.filter((b) => b.perlu && !b.k && b.termurah);
  const urutHari = (a, b) => (a.hari === null ? 999 : a.hari) - (b.hari === null ? 999 : b.hari);
  const kelompok = []; const tambah = (judul, ket, awas, d) => { if (d.length) kelompok.push({ judul, ket, awas, isi: d.slice().sort(urutHari) }); };
  tambah('Habis dalam ' + atur.ambangHari + ' hari', 'perlu dipesan', true, baris.filter((b) => !b.dipesan && b.hari !== null && b.hari <= atur.ambangHari && !b.tutup));
  // tinjauan E1: stok merek ini sendiri tipis, tapi baris harganya (merek seharga dari pemasok yang sama) menutupnya — tidak dipesan terpisah
  tambah('Habis dalam ' + atur.ambangHari + ' hari — ada yang seharga', 'tidak dipesan terpisah', false, baris.filter((b) => !b.dipesan && b.hari !== null && b.hari <= atur.ambangHari && !!b.tutup));
  tambah('Masih aman', 'lebih dari ' + atur.ambangHari + ' hari', false, baris.filter((b) => !b.dipesan && b.hari !== null && b.hari > atur.ambangHari));
  tambah('Belum bisa dihitung', 'belum ada penjualan ' + JENDELA_LAJU_HARI + ' hari ini', false, baris.filter((b) => !b.dipesan && b.hari === null));
  tambah('Sudah dipesan', 'menunggu datang', false, baris.filter((b) => !!b.dipesan));
  // owner 7 Okt + tinjauan E1: lembar daftar belanja = satu baris per harga; baris yang perlu (gabungan) atau sudah berisi tampil LENGKAP dengan merek seharganya
  // (stok merek yang tidak perlu ikut terlihat, karena barangnya sama di mata pemasok)
  const kertas = perP.map((r) => { const g = r.gMilik.filter((x) => x.k > 0 || x.perlu); const isi = []; g.forEach((x) => x.merk.forEach((b) => isi.push(b)));
    return { pemasok: r.pemasok, kunci: r.kunci, karung: r.karung, kg: r.kg, rp: r.rp, lebih: r.lebih, sisaMuat: r.sisaMuat, muatanKg: atur.muatanKg, g, isi: isi.sort(urutHari) }; }).filter((r) => r.isi.length);
  const diKertas = {}; kertas.forEach((r) => r.isi.forEach((b) => { diKertas[b.merk] = true; }));
  const lainnya = baris.filter((b) => !b.dipesan && b.k === 0 && !b.perlu && b.termurah && !diKertas[b.merk]).sort(urutHari);
  const nBarisSaran = perP.reduce((a, r) => a + r.saranG, 0); const karungSaran = perluSemua.reduce((a, b) => a + b.saranK, 0);
  return { D, atur, baris, perP, totKarung, totKg, totRp, perluSemua, nBarisSaran, saranSemuaTeks: 'Pakai saran: ' + nBarisSaran + ' baris harga · ' + karungSaran + ' karung', kelompok, kertas, lainnya, kas, ringkas: [{ a: baris.filter((b) => !b.dipesan && b.hari !== null && b.hari <= 2).length, l: 'habis ≤ 2 hari', nyala: true }, { a: baris.filter((b) => b.perlu).length, l: 'perlu dipesan', nyala: false }, { a: baris.filter((b) => b.dipesan).length, l: 'sudah dipesan', nyala: false }],
    legenda: 'Batang abu = stok cukup sampai hari ke berapa (penuh = 30 hari) · garis = ' + atur.ambangHari + ' hari · emas = tambahan dari pesanan', pesanTeks: totKarung ? totKarung + ' karung · ' + blKG(totKg) + ' · ±' + RP(totRp) : '', pesanKet: perP.filter((r) => r.karung).map((r) => r.pemasok + ' ' + r.karung).join(' · ') };
}
/**
 * "Pakai saran" (tinjauan E1: satu pintu untuk tombol per pemasok & "Pakai saran untuk semua"): tiap merek yang perlu menerima bagiannya dari saran baris harganya
 * (blBagiSaran) — jumlah per baris harga = saran gabungan, bukan Σ saran per merek. pemasok kosong = semua pemasok. → { pesan, baris, merk, karung }.
 */
export function pakaiSaran(H, pesan, pemasok) {
  let o = Object.assign({}, pesan || {}); const kena = H.baris.filter((b) => b.perlu && !b.k && !b.dipesan && b.sumber && b.saranK > 0 && (!pemasok || b.sumber.pemasok === pemasok));
  const uk = petaUkuran(); const g = {}; kena.forEach((b) => { o = tulisPesan(o, b.merk, b.sumber.pemasok, b.saranK); g[b.sumber.pemasok + '|' + blKunci(b, uk).kunci] = true; });
  return { pesan: o, baris: Object.keys(g).length, merk: kena.length, karung: kena.reduce((a, b) => a + b.saranK, 0) };
}
/**
 * KELOMPOK HARGA (owner 7 Okt: "belanja pakai harga modal yang sudah ada sebelumnya"). Baris belanja satu pemasok dikelompokkan per harga yang dipakai (harga beli
 * terakhir per kg dari pemasok itu, atau harga kelas terbarunya — blPakaiHarga; yang sama dengan yang menghitung rp barisnya), per berat karung, dan per jenis beras
 * (IR64 & IR42 yang kebetulan seharga tetap dua baris, supaya pemasok tidak salah kirim). Merek seharga = SATU baris; karung, kg, rp dijumlah apa adanya (Σ kelompok
 * = Σ baris). Merek tanpa harga beli = baris sendiri bertanda "harga belum tercatat". Urutan: termurah dulu, tanpa harga paling akhir. terakhir = tanggal kiriman
 * terakhir pemasok itu: harga yang lebih tua ditandai umurnya ("harga 18 Sep"). kode "merek lalu" = nama karung yang dikenal pemasok (merek pemasok yang tercatat,
 * atau nama sebelum " · "); nama buatan toko (wadah / kelas mutu / kelas sendiri / bahan campuran) tidak disebut.
 */
export function blKelompokHarga(rows, terakhir, semua) {
  const uk = petaUkuran(); const peta = {}; const urut = []; const kelasToko = Object.assign({}, wbNamaKelas(), kmKelasSendiri());
  (rows || []).forEach((b) => {
    const K = blKunci(b, uk); const kunci = K.kunci;
    if (!peta[kunci]) { peta[kunci] = { kunci, harga: K.harga, berat: K.berat, jenis: K.jenis, adaHarga: K.harga > 0, merk: [], k: 0, kg: 0, rp: 0, tanggal: '', kenal: [] }; urut.push(peta[kunci]); }
    const g = peta[kunci]; g.merk.push(b); g.k += b.k || 0; g.kg += b.kg || 0; g.rp += b.rp || 0;
  });
  // tanggal harga & "merek lalu" dibaca dari SEMUA merek pemasok ini di baris harga yang sama (semua = daftar milik pemasok), bukan hanya yang dipesan
  urut.forEach((g) => { const lain = (semua || []).filter((b) => g.merk.indexOf(b) < 0 && g.merk.every((x) => x.merk !== b.merk) && blKunci(b, uk).kunci === g.kunci); g.kenal = g.merk.concat(lain);
    g.kenal.forEach((b) => { if (b.pakai && String(b.pakai.tanggal || '') > g.tanggal) g.tanggal = String(b.pakai.tanggal || ''); }); });
  const urutHari = (a, b) => (a.hari === null ? 999 : a.hari) - (b.hari === null ? 999 : b.hari);
  const tokoNama = (n) => !n || !!kelasToko[n] || /campuran/i.test(n);
  return urut.map((g) => {
    const merk = g.merk.slice().sort((a, b) => urutHari(a, b) || String(a.merk).localeCompare(String(b.merk)));
    const kode = []; if (g.adaHarga) merk.concat(g.kenal.filter((b) => merk.indexOf(b) < 0)).forEach((b) => { const asal = blInduk(b.merk, uk); const kp = b.pakai && b.pakai.kode ? String(b.pakai.kode).trim() : '';
      const kd = kp || (tokoNama(asal) ? '' : String(asal).split(' · ')[0].trim()); if (kd && kd.toLowerCase() !== g.jenis.toLowerCase() && kode.indexOf(kd) < 0) kode.push(kd); });
    const basi = g.adaHarga && !!terakhir && !!g.tanggal && g.tanggal < String(terakhir);
    const label = g.adaHarga ? (g.jenis || 'beras') + ' ' + RP(g.harga) + '/kg' : merk[0].merk;
    const saranK = merk.reduce((a, b) => a + (b.saranK || 0), 0); const sisa = merk.reduce((a, b) => a + (b.sisa || 0), 0), laju = merk.reduce((a, b) => a + (b.laju || 0), 0); const hari = hariHabis(sisa, laju);
    const kembar = g.kenal.filter((b) => b.pakai && b.pakai.lalu).map((b) => b.merk + ' terakhir ' + RP(b.pakai.lalu.harga) + ' (' + blTglPendek(b.pakai.lalu.tanggal, g.tanggal) + ')');
    return Object.assign(g, { merk, kg: Math.round(g.kg * 100) / 100, label, kode, hari, sisa: Math.round(sisa * 100) / 100, kritis: hari !== null && hari <= 2, perlu: merk.some((b) => b.perlu), saranK, basi,
      saranTeks: saranK > 0 ? 'saran ' + saranK + ' karung' : 'tambah', kodeTeks: kode.length ? 'merek lalu: ' + kode.join(' / ') : '',
      hariTeks: merk.length > 1 ? 'bersama ' + blKG(Math.round(sisa)) + ' · ' + kataHabis(hari) : '',
      hargaTeks: g.adaHarga ? 'harga beli terakhir ' + tanggalPendek(g.tanggal) + (basi ? ' — sebelum kiriman terakhir pemasok ini (' + tanggalPendek(terakhir) + ')' : '') + (kembar.length ? ' · ikut harga kelasnya: ' + kembar.join(', ') : '') : 'harga belum tercatat — pemasok mengenalnya dari nama ini',
      teks: '• ' + label + (basi ? ' (harga ' + blTglPendek(g.tanggal, terakhir) + ')' : '') + ' — ' + g.k + ' karung × ' + g.berat + ' kg' + (kode.length ? ' (merek lalu: ' + kode.join(' / ') + ')' : '') + (g.adaHarga ? '' : ' · harga belum tercatat') });
  }).sort((a, b) => (a.adaHarga ? 0 : 1) - (b.adaHarga ? 0 : 1) || a.harga - b.harga || a.jenis.localeCompare(b.jenis) || b.berat - a.berat || a.kunci.localeCompare(b.kunci));
}
/**
 * Ubah SATU kelompok harga (owner 7 Okt; pemasok mengenalnya dari harga, jadi karungnya dibagi ke merek di dalamnya): +1 → merek yang paling cepat habis sesudah
 * pesanan (merek tanpa laju terakhir); −1 → dari merek berkarung yang paling lama cukup. Hasilnya tetap peta per merek { merk: { p, k } } (laju & sisa per merek).
 */
export function ubahKelompok(H, pemasok, kunci, arah, pesan) {
  const R = H.perP.find((r) => r.pemasok === pemasok); const g = R ? R.gMilik.find((x) => x.kunci === kunci) : null; if (!g) return pesan || {};
  const cukup = (b, k) => (b.laju > 0 ? (b.sisa + k * b.berat) / b.laju : Infinity);
  if (Number(arah) > 0) { const c = g.merk.slice().sort((x, y) => cukup(x, x.k) - cukup(y, y.k) || (y.k || 0) - (x.k || 0) || x.merk.localeCompare(y.merk))[0]; return tulisPesan(pesan, c.merk, pemasok, (c.k || 0) + 1); }
  const ada = g.merk.filter((b) => b.k > 0); if (!ada.length) return pesan || {};
  const c = ada.sort((x, y) => cukup(y, y.k) - cukup(x, x.k) || x.merk.localeCompare(y.merk))[0]; return tulisPesan(pesan, c.merk, pemasok, c.k - 1);
}
/** Centang satu kelompok di daftar: sudah berisi → semua merek di dalamnya dikosongkan; belum → saran GABUNGAN baris itu, dibagi seperti blBagiSaran (tanpa saran: satu karung). */
export function ketukKelompok(H, pemasok, kunci, pesan) {
  const R = H.perP.find((r) => r.pemasok === pemasok); const g = R ? R.gMilik.find((x) => x.kunci === kunci) : null; if (!g) return pesan || {};
  let o = Object.assign({}, pesan || {});
  if (g.k > 0) { g.merk.forEach((b) => { o = tulisPesan(o, b.merk, pemasok, 0); }); return o; }
  const bagian = g.merk.filter((b) => b.saranK > 0); if (!bagian.length) return ubahKelompok(H, pemasok, kunci, 1, o);
  bagian.forEach((b) => { o = tulisPesan(o, b.merk, pemasok, b.saranK); }); return o;
}
/** Truk satu pemasok: potongan bak berwarna per HARGA (owner 7 Okt; label hanya bila tumpukannya cukup lebar). */
export function susunTruk(H, pemasok) {
  const R = H.perP.find((r) => r.pemasok === pemasok) || H.perP[0] || null; if (!R) return null; const muat = H.atur.muatanKg; const dasar = Math.max(muat, R.kg, 1);
  const bak = R.g.map((g, i) => { const bagian = g.kg / dasar; const pendek = g.adaHarga ? ANGKA(g.harga) : g.merk[0].merk.split(' ')[0].toUpperCase(); return { kelas: 'w' + (i % 6), t: bagian >= 0.2 ? pendek + ' · ' + g.k : bagian >= 0.07 ? String(g.k) : '', flex: Math.min(g.kg, muat || g.kg), merk: g.kunci }; });
  if (!R.lebih && muat > 0) bak.push({ kelas: 'kosongbak', t: '', flex: Math.max(0, muat - Math.min(R.kg, muat)) });
  return { R, bak, lebih: R.lebih > 0, muatAngka: blKG(R.kg), muatDari: muat > 0 ? 'dari ' + blKG(muat) : '(muatan truk belum diketahui — isi di Atur)', muatSisa: muat <= 0 ? '' : R.lebih ? 'KELEBIHAN ' + blKG(R.lebih) + ' — tidak muat satu truk' : R.sisaMuat === 0 ? 'truknya penuh' : 'masih muat ' + blKG(R.sisaMuat) + ' · ' + Math.floor(R.sisaMuat / 50) + ' karung',
    bisaPenuhi: muat > 0 && R.sisaMuat >= 25 && R.milik.some((b) => b.laju > 0 && !b.dipesan), saranTeks: R.saran.length ? 'Pakai saran: ' + R.saranG + ' baris harga · ' + R.saranKarung + ' karung' : 'Tidak ada saran lagi' };
}
export const tulisPesan = (pesan, merk, p, k) => { const o = Object.assign({}, pesan || {}); if (k > 0) o[merk] = { p, k }; else delete o[merk]; return o; };
/**
 * Penuhi truk: tambah karung satu-satu ke baris HARGA yang paling cepat habis sesudah pesanan (stok & laju gabungan merek seharga — tinjauan E1), di dalamnya ke
 * merek yang paling cepat habis, sampai truknya penuh. Merek tanpa laju tidak menerima karung (stoknya tetap dihitung di barisnya).
 */
export function penuhiTruk(H, pemasok, pesan) {
  const R = H.perP.find((r) => r.pemasok === pemasok); if (!R || !(H.atur.muatanKg > 0)) return { pesan: pesan || {}, tambahan: 0 };
  const uk = petaUkuran(); let o = Object.assign({}, pesan || {}); let kg = R.kg; const anggota = R.milik.filter((b) => !b.dipesan && (!o[b.merk] || o[b.merk].p === pemasok)).map((b) => ({ b, k: b.k, g: blKunci(b, uk).kunci }));
  const calon = anggota.filter((c) => c.b.laju > 0); let tambahan = 0;
  const cukupG = (g) => { const isi = anggota.filter((c) => c.g === g); const l = isi.reduce((a, c) => a + c.b.laju, 0); return isi.reduce((a, c) => a + c.b.sisa + c.k * c.b.berat, 0) / l; };
  for (let i = 0; i < 400; i++) { const muat = calon.filter((c) => kg + c.b.berat <= H.atur.muatanKg); if (!muat.length) break; muat.sort((x, y) => cukupG(x.g) - cukupG(y.g) || (x.b.sisa + x.k * x.b.berat) / x.b.laju - (y.b.sisa + y.k * y.b.berat) / y.b.laju); muat[0].k += 1; kg += muat[0].b.berat; tambahan += 1; }
  calon.forEach((c) => { if (c.k > 0) o = tulisPesan(o, c.b.merk, pemasok, c.k); }); return { pesan: o, tambahan };
}
/**
 * Pesan WhatsApp satu pemasok + dokumen pesananPemasok. Nomor dari kartu pemasok (0812… → 62812…); tanpa nomor WhatsApp yang bertanya ke siapa.
 * owner 7 Okt: satu baris pesan = satu HARGA beli terakhir dari pemasok itu ("<jenis> Rp<harga>/kg — <n> karung × <berat> kg (merek lalu: <kode karung>)"), bukan nama merek karung
 * yang berganti-ganti. Dokumen tetap mencatat baris per merek (penanda "sudah dipesan" per merek) + barisHarga = apa yang dikirim ke pemasok.
 * Tinjauan E1: harga yang lebih tua dari kiriman terakhir pemasok itu ditulis umurnya — "• IR64 Rp…/kg (harga 18 Sep) — …" — supaya tidak terbaca harga yang diminta toko.
 */
export function susunPesanan(pesan, pemasok, w, waHarga) {
  const H = hitungBelanja(pesan, new Date(w.kini)); const R = H.perP.find((r) => r.pemasok === pemasok); if (!R) return { tolak: 'Pemasok itu tidak dikenal' }; if (!R.karung) return { tolak: 'Belum ada karung untuk ' + pemasok + ' di daftar' };
  const baris = ['*Pesanan Toko Beras M.IQBAL*', tanggalPendek(w.tanggal) + ' · untuk ' + R.pemasok].concat(R.g.map((g) => g.teks)).concat(['Jumlah ' + R.karung + ' karung · ' + blKG(R.kg)]).concat(waHarga ? ['Perkiraan ' + RP(R.rp)] : []);
  const nomor = nomorWa(R.kontak); const tautan = 'https://wa.me/' + nomor + '?text=' + encodeURIComponent(baris.join('\n'));
  const data = { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, pemasok: R.pemasok, baris: R.d.map((b) => ({ merk: b.merk, karung: b.k, berat: b.berat, kg: b.kg, hargaPerKg: b.pakai.harga })),
    barisHarga: R.g.map((g) => ({ hargaPerKg: g.harga, berat: g.berat, jenis: g.jenis, karung: g.k, kg: g.kg, merk: g.merk.filter((b) => b.k > 0).map((b) => b.merk) })), karung: R.karung, kg: R.kg, rp: R.rp, status: 'menunggu', teks: baris.join('\n'), keNomor: nomor };
  const sisa = Object.assign({}, pesan || {}); R.d.forEach((b) => { delete sisa[b.merk]; });
  return { dokumen: [{ koleksi: 'pesananPemasok', data }], tautan, baris, pesanSisa: sisa, lebihTeks: R.lebih ? 'Pesanan ini ' + blKG(R.kg) + ' — lebih ' + blKG(R.lebih) + ' dari satu truk (' + blKG(H.atur.muatanKg) + '). Boleh, tapi berarti lebih dari satu kali antar.' : '', uangTeks: R.uangTeks,
    patch: { wa: null, kabar: 'Pesanan ' + R.pemasok + ' (' + R.karung + ' karung) dicatat sebagai menunggu datang' + (nomor ? ' · WhatsApp ke ' + R.kontak : ' · nomor pemasok belum ada di kartu — WhatsApp menanyakan tujuannya') + '. Dicocokkan dengan kedatangannya di Barang masuk.', kabarAwas: false } };
}
export function susunUbahPesanan(id, status, w) {
  const p = ambilPesananPemasok().find((x) => String(x.id) === String(id)); if (!p) return { tolak: 'Pesanan itu sudah tidak ada' }; if (status !== 'batal' && status !== 'datang') return { tolak: 'Keadaan tidak dikenal' };
  const data = Object.assign({}, p, { status, diubahTanggal: w.tanggal, diubahJam: w.jam }); if (status === 'datang') data.datangTanggal = w.tanggal;
  return { dokumen: [{ koleksi: 'pesananPemasok', data }], patch: { kabar: status === 'batal' ? 'Pesanan ' + p.pemasok + ' dibatalkan — mereknya bisa disarankan lagi' : 'Pesanan ' + p.pemasok + ' ditandai sudah datang', kabarAwas: false } };
}
