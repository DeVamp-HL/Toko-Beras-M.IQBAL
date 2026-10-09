// LAYAR RINGKASAN — DASBOR OWNER (putaran 40, brief owner 29 Sep 2026; saklar Dasbor | Cincin dipilih owner 2 Okt). Tanpa DOM.
//
// "Dalam 10 detik owner tahu": HARI INI · BULAN INI · STOK & WADAH · PIUTANG & UTANG PEMASOK yang jatuh tempo · PEMICU biaya yang naik.
// ATURAN: TIDAK ADA RUMUS UANG BARU di sini. Tiap angka diambil apa adanya dari fungsi yang sudah dipakai layar lain (satu sumber):
//   hari ini  → rekapHari (Laporan › Harian) · saldoKantong (Uang › Pindah uang) · daftarKarcis (Jual › Karcis kasir)
//   bulan ini → kendaliBulan · titikImpas · pemicuBiaya · peringatanBiaya (Laporan › Biaya; laba bersih = mesin yang sama dengan Laporan › Laba)
//   stok      → daftarBarang (Stok › Gudang) · susunWadah + wbCekHari hari tutup aktif (Stok › Wadah literan; cek wadah di Tutup hari)
//   tagihan   → semuaBon (Pelanggan › Bon) · susunBon pemasok (Harga & Pemasok › Bon pemasok › Jatuh tempo)
//   tren      → hariTerakhir / daftarMinggu / daftarBulan (Laporan) + lpHariRentang (= hitungLabaRentang & jumlahNota; Paket B: hari di tahun yang sudah
//               ditutup buku dari potret hari — awal Januari batang Desember tidak jatuh ke Rp0)
// Yang dihitung di sini cuma pengelompokan (jumlah per status dari baris yang sama, urutan, label) — dan uji_ringkasan_baru memeriksa tiap
// kelompok MENUTUP ke angka sumbernya. Tiap kelompok membawa { periode, sumber, tujuan }; tujuan berbentuk sama dengan baris Menu
// ({ ke, keluarga, tab, lembar, … }) untuk keTujuan() di app.js. Satu kelompok yang galat tidak mematikan kelompok lain. BACA SAJA.
import { AMBANG_HARI_KRITIS, JENDELA_LAJU_HARI, akhirBulanIso } from '../mesin/pembantu.js';
import { hariIniIso, tanggalPendek, tanggalTutupAktif } from '../inti/format.js';
import { rekapHari, hariTerakhir, daftarMinggu, daftarBulan, lpPertama, lpHariRentang, merekBulan, merekTeratas } from './laporan-logika.js';
import { kendaliBulan, titikImpas, pemicuBiaya, peringatanBiaya } from './kendali-biaya-logika.js';
import { saldoKantong, ugNamaTempat } from './uang-logika.js';
import { daftarKarcis } from './karcis-logika.js';
import { daftarBarang, susunWadah, umRingkas } from './stok-logika.js';
import { wbCekHari } from './wadah-bernama-logika.js';
import { semuaBon, KATA_STATUS, tertagihBon } from './bon-logika.js';
import { susunBon as bpSusunBon } from './bon-pemasok-logika.js';
import { hetHargaKasir } from './het-logika.js';
import { rekapTimbangMutu } from './stok-catat-logika.js';

export const DB_RENTANG = [['hari', 'Hari'], ['minggu', 'Minggu'], ['bulan', 'Bulan']];
const DB_TEMPAT = ['laci', 'brankas', 'rekening', 'amplop'];
// urutan status bon pelanggan di dasbor: yang paling mendesak dulu; tiga yang pertama = "jatuh tempo" (aturan tagih/macet di Pelanggan › Atur)
const DB_STATUS_BON = ['janjiLewat', 'macet', 'perluTagih', 'menunggu', 'baru'];
const DB_JATUH = ['janjiLewat', 'macet', 'perluTagih'];

/** HARI INI: omzet & laba kotor (Laporan › Harian), kas per tempat (Uang), karcis kasir yang menunggu dirinci (Jual). */
export function dbHariIni(kini) {
  const iso = hariIniIso(kini); const R = rekapHari(iso); const S = saldoKantong(); const KC = daftarKarcis(kini);
  return {
    iso, periode: tanggalPendek(iso), sumber: 'Laporan › Harian', tujuan: { ke: 'laporan', keluarga: 'harian', hari: iso },
    omzet: R.omzet, nota: R.n, retur: R.retur, margin: R.margin, tanpaHpp: R.jumlahTanpaHpp, tunai: R.tunai, qris: R.qris, kredit: R.kredit, nKredit: R.nKredit,
    kas: S.ada ? { ada: true, total: S.total, cocok: S.cocok, minus: S.minus, titik: S.teksTitik, tempat: DB_TEMPAT.map((id) => ({ id, nama: ugNamaTempat(id), n: S[id] })) } : { ada: false, tempat: [] },
    kasSumber: 'Uang › Pindah uang', kasTujuan: { ke: 'uang', keluarga: 'pindah' },
    karcis: { n: KC.nKarcis, rp: KC.total, rapikan: KC.nRapikan, hariIni: KC.daftar.filter((d) => d.hariIni).length }, karcisSumber: 'Jual › Karcis kasir', karcisTujuan: { ke: 'jual', lembar: 'karcis' },
  };
}

/** BULAN INI: margin, biaya per jenis + lampu anggaran, laba bersih vs titik impas, susut, pemicu yang naik — semuanya Laporan › Biaya. */
export function dbBulanIni(kini) {
  const key = hariIniIso(kini).slice(0, 7); const K = kendaliBulan(key, kini); const T = titikImpas(K, kini); const P = pemicuBiaya(K); const W = peringatanBiaya(K, P, T);
  const tujuanW = (id) => { const w = W.find((x) => x.id === id); return w && w.tujuan ? w.tujuan : null; };
  // 8 Okt 2026: baris yang NEGATIF ikut (susut & selisih stok minus = stok bertambah, mis. nilai karung bekas diterapkan) — dulu disaring `pakai > 0`, jadi
  // baris-baris kartu Biaya tidak menjumlah ke "Semua biaya" (total minus padahal barisnya positif semua). Batang negatif = 0 lebar (dbPersen), angkanya bertanda minus.
  const biaya = K.baris.filter((r) => Math.abs(r.pakai) > 0.5 || r.anggaran > 0).map((r) => ({ id: r.id, nama: r.nama, n: r.pakai, menggantung: r.menggantung, anggaran: r.anggaran, dasar: r.dasar, lampu: r.lampu, lampuTeks: r.lampuTeks, proyeksi: r.proyeksi, nLalu: r.nLalu }));
  return {
    key, nama: K.nama, berjalan: K.berjalan, final: K.final, hariJalan: K.hariJalan, nHari: K.nHari, tanpaCatatan: K.tanpaCatatan, menutup: K.menutup,
    periode: K.nama + (K.berjalan ? ' · berjalan, hari ke-' + K.hariJalan + ' dari ' + K.nHari : K.final ? ' · final' : ''), sumber: 'Laporan › Biaya',
    tujuan: { ke: 'laporan', keluarga: 'biaya', bulan: key }, labaTujuan: { ke: 'laporan', keluarga: 'laba', bulan: key },
    omzet: K.omzet, omzetHitung: K.omzetHitung, margin: K.margin, rasioTeks: T.rasioTeks, cakupan: K.cakupan, tanpaHpp: K.L.jumlahTanpaHpp,
    biaya, semuaBiaya: K.semuaBiaya, merah: K.merah, amber: K.amber, hijau: K.hijau, nLampu: K.nLampu, ambang: K.A.ambang,
    labaBersih: K.labaBersih, susut: K.susut, nSusut: K.L.nSusut, susutTujuan: tujuanW('susut') || { ke: 'stok', lembar: 'cocok' },
    impas: { rasio: T.rasio, omzetImpas: T.omzetImpas, omzetImpasHari: T.omzetImpasHari, omzetHari: T.omzetHari, labaSampai: T.labaSampai, sampai: T.sampai, menutup: T.menutupKini, kurang: T.kurang, teks: T.teks, kiniTeks: T.kiniTeks, catatan: T.catatan },
    pemicu: P.naik.map((r) => ({ id: r.id, nama: r.nama, teks: r.teks, teksLalu: r.teksLalu, deltaTeks: r.deltaTeks, sumberRumus: r.sumber, tujuan: tujuanW('pemicu-' + r.id) || { ke: 'laporan', keluarga: 'biaya', bulan: key } })),
    ambangPemicu: P.ambang, pendekLalu: P.pendekLalu, nPemicu: P.baris.filter((r) => r.n !== null).length,
  };
}

/** STOK: kg per merek & perkiraan hari tersisa (Stok › Gudang), wadah literan (Stok › Wadah literan) + cek wadah hari tutup aktif (Tutup hari). */
export function dbStok(kini) {
  const merek = daftarBarang().filter((b) => b.jenis === 'karung' && !b.wadahStok && Math.abs(b.sisa) > 0.004)
    .map((b) => ({ nama: b.nama, kg: b.sisa, laju: b.laju, hari: b.hariHabis, minus: b.sisa < 0, awas: b.sisa < 0 || (b.hariHabis !== null && b.hariHabis <= AMBANG_HARI_KRITIS) }))
    .sort((a, b) => b.kg - a.kg || a.nama.localeCompare(b.nama));
  const SW = susunWadah(null); const hariCek = tanggalTutupAktif(kini); const C = wbCekHari(hariCek);
  const wadah = SW.daftar.map((w) => { const c = C.daftar.find((x) => x.W === w.nama) || {};
    return { no: w.no, nama: w.nama, merek: w.stokSendiri ? w.karungAsal : w.karungNama, banding: w.resep.length > 1 ? w.resep.map((r) => r.takar).join(' : ') + ' — ' + w.resep.map((r) => r.merk).join(' : ') : '',
      diketahui: !!w.diketahui, isiKg: w.diketahui ? w.sisaKg : null, penuhKg: w.penuhKg, bagian: w.diketahui ? w.bagian : 0, perluIsi: !!(w.diketahui && w.perluIsi), lewat: w.lewat || 0,
      terakhirTanggal: w.isiTerakhirTanggal || '', terakhirJam: w.isiTerakhirJam || '', aktif: !!c.aktif, dicek: !!c.dicek, hasilTeks: c.hasilTeks || '', jamCek: c.jam || '' }; });
  return { periode: 'Sekarang · laju jual ' + JENDELA_LAJU_HARI + ' hari terakhir', sumber: 'Stok › Gudang', tujuan: { ke: 'stok', tab: 'gudang' }, merek, ambangHari: AMBANG_HARI_KRITIS,
    wadah, wadahSumber: 'Stok › Wadah literan', wadahTujuan: { ke: 'stok', tab: 'wadah' }, hariCek, nAktif: C.nAktif, nDicek: C.nDicek, belumDicek: C.belum, perluIsi: SW.perluIsi, belumDitandai: SW.belumDitandai };
}

/** PIUTANG (Pelanggan › Bon) & UTANG PEMASOK (Harga & Pemasok › Bon pemasok) — yang jatuh tempo didahulukan. */
export function dbTagihan(kini) {
  const bon = semuaBon(kini).filter((b) => b.sisa > 0);
  const perStatus = DB_STATUS_BON.map((s) => { const d = bon.filter((b) => b.status === s); return { status: s, kata: KATA_STATUS[s], n: d.length, rp: d.reduce((a, b) => a + b.sisa, 0), jatuh: DB_JATUH.indexOf(s) >= 0 }; });
  const jatuh = bon.filter((b) => DB_JATUH.indexOf(b.status) >= 0).sort((a, b) => DB_JATUH.indexOf(a.status) - DB_JATUH.indexOf(b.status) || b.sisa - a.sisa)
    .map((b) => ({ kunci: b.kunci, nama: b.nama, sisa: b.sisa, kata: b.cap, ket: b.ket, tujuan: { ke: 'pelanggan', keluarga: 'bon', orang: b.kunci } }));
  const BP = bpSusunBon(kini); const jauh = BP.bon.filter((b) => b.status === 'jauh'); const satuBon = (b) => ({ id: b.id, pemasok: b.pemasok, sisa: b.sisa, tempoTeks: b.tempoTeks, tanggal: b.tanggal, tujuan: { ke: 'harga', keluarga: 'bon', pemasok: b.pemasok } });
  return {
    periode: 'Sekarang · ' + tanggalPendek(hariIniIso(kini)),
    piutang: { total: bon.reduce((a, b) => a + b.sisa, 0), n: bon.length, perStatus, jatuh, nJatuh: jatuh.length, rpJatuh: jatuh.reduce((a, b) => a + b.sisa, 0), sumber: 'Pelanggan › Bon', tujuan: { ke: 'pelanggan', keluarga: 'bon' } },
    pemasok: { total: BP.total, nBon: BP.nBon, nPemasok: BP.nPemasok, tekor: BP.tekor, lewat: BP.lewat.map(satuBon), dekat: BP.dekat.map(satuBon), nTanpaTempo: BP.tanpaTempo.length, rpTanpaTempo: BP.tanpaTempo.reduce((a, b) => a + b.sisa, 0), nJauh: jauh.length, rpJauh: jauh.reduce((a, b) => a + b.sisa, 0),
      rpLewat: BP.lewat.reduce((a, b) => a + b.sisa, 0), rpDekat: BP.dekat.reduce((a, b) => a + b.sisa, 0),
      dekatHari: BP.atur.dekatHari, cukupTeks: BP.cukupTeks, kurang: BP.kurang, adaKas: BP.adaKas, sumber: 'Harga & Pemasok › Bon pemasok', tujuan: { ke: 'harga', keluarga: 'bon', tab: 'garis' } },
  };
}

/** TREN omzet & laba kotor per hari (14) · minggu (8) · bulan (6) — rentang yang SAMA dengan pemilih Laporan › Harian / Mingguan / Bulanan, jadi tiap batang
 *  bisa dibuka di sana. Omzet & nota dari daftar Laporan, laba kotor dari mesin laba yang sama. */
export function dbTren(rentang, kini) {
  const iso = hariIniIso(kini); const pertama = lpPertama();
  const satu = (dari, sampai, x) => { const L = lpHariRentang(dari, sampai); return Object.assign({ omzet: L.omzetPenuh, margin: L.margin, tanpaHpp: L.jumlahTanpaHpp, retur: L.returUang, nota: L.nota }, L.tanpaPotret ? { tanpaPotret: L.tanpaPotret } : {}, x); };
  let batang;
  if (rentang === 'minggu') batang = daftarMinggu(kini, 8).reverse().map((m) => satu(m.awal, m.akhir, { id: m.awal, label: m.pendek, panjang: 'Minggu ' + m.label, berjalan: m.berjalan, absen: false, tujuan: { ke: 'laporan', keluarga: 'mingguan', awal: m.awal } }));
  else if (rentang === 'bulan') batang = daftarBulan(kini, 6).reverse().map((b) => satu(b.key + '-01', akhirBulanIso(b.key), { id: b.key, label: b.pendek, panjang: b.nama, berjalan: b.berjalan, absen: false, tujuan: { ke: 'laporan', keluarga: 'bulanan', bulan: b.key } }));
  else {
    rentang = 'hari';
    batang = hariTerakhir(kini, 14).reverse().map((d) => { const absen = !pertama || d.iso < pertama || !!d.tanpaPotret;   // Paket B: hari tahun yang ditutup tanpa potret = tidak ada angka
      const x = satu(d.iso, d.iso, { id: d.iso, label: String(Number(d.iso.slice(8, 10))), panjang: tanggalPendek(d.iso) + (d.hariIni ? ' · hari ini' : ''), berjalan: d.hariIni, absen, tujuan: { ke: 'laporan', keluarga: 'harian', hari: d.iso } });
      x.omzetDaftar = d.omzet; x.notaDaftar = d.n; return x; });
  }
  const nama = DB_RENTANG.find((r) => r[0] === rentang)[1];
  return { rentang, batang, maks: Math.max(1, ...batang.map((b) => Math.max(b.omzet, 0))), periode: rentang === 'hari' ? '14 hari terakhir' : rentang === 'minggu' ? batang.length + ' minggu terakhir (Senin–Minggu)' : batang.length + ' bulan terakhir',
    sumber: 'Laporan › ' + (rentang === 'hari' ? 'Harian' : rentang === 'minggu' ? 'Mingguan' : 'Bulanan'), nama, hariIni: iso };
}

/** MUTU USAHA (paket brief awal 9 Okt, owner "sesuaikan saja dulu"): lima KPI yang tayang 9 Okt, tiap baris = fungsi sumber layarnya APA ADANYA —
 *  rata-rata hari bon tertagih (Pelanggan › Bon), lambat laku & stok tertua & perputaran (Stok › Umur & putaran), merek teratas & susut % bulan ini
 *  (Laporan › Laba › Per merek), harga di atas HET (Harga › Katalog), kedatangan bermutu AWAS / kurang timbang (Stok › Barang masuk). Satu baris galat
 *  tidak mematikan baris lain. Tidak ada rumus uang di sini. */
export function dbMutu(kini) {
  const key = hariIniIso(kini).slice(0, 7);
  const aman = (f) => { try { return f(); } catch (e) { if (typeof console !== 'undefined') console.error('dasbor mutu', e); return { galat: String((e && e.message) || e) }; } };
  const T = aman(() => tertagihBon(kini)); const U = aman(() => umRingkas(kini)); const M = aman(() => merekBulan(key, kini)); const H = aman(() => hetHargaKasir(kini));
  const R = aman(() => rekapTimbangMutu({})); const TT = M.galat ? null : aman(() => merekTeratas(M, 'margin', 3));
  return {
    periode: 'Sekarang · merek & susut ' + (M.galat ? key : M.nama), sumber: 'Laporan › Laba › Per merek', tujuan: { ke: 'laporan', keluarga: 'laba', bulan: key },
    tertagih: T.galat ? T : { keadaan: T.keadaan, rataTeks: T.rataTeks, hari: T.hari, teks: T.teks, periodeTeks: T.periodeTeks, tujuan: { ke: 'pelanggan', keluarga: 'bon' } },
    umur: U.galat ? U : { lambat: U.lambat.length, namaLambat: U.lambat.slice(0, 3).map((r) => r.nama), tertua: U.tertua.length ? { nama: U.tertua[0].nama, hari: U.tertua[0].umurAcuan } : null,
      putaran: U.putaranMerek, periodeHari: U.atur.periodeHari, tujuan: { ke: 'stok', tab: 'umur' } },
    merek: M.galat ? M : TT.galat ? TT : { nama: M.nama, arsip: !!M.diarsip, menutup: M.menutup, teratas: TT.daftar.map((g) => ({ merek: g.merek, margin: g.margin, pct: g.pct, keadaanMargin: g.keadaanMargin })),
      susutPct: M.susut ? M.susut.pct : null, susutTinggi: M.susut ? (Array.isArray(M.susut.tinggi) ? M.susut.tinggi.length : Number(M.susut.tinggi) || 0) : 0, tujuan: { ke: 'laporan', keluarga: 'laba', bulan: key } },
    het: H.galat ? H : { keadaan: H.keadaan, judul: H.judul, nAtas: H.nAtas, tujuan: { ke: 'harga', keluarga: 'katalog' } },
    mutu: R.galat ? R : { kedatangan: R.total.kedatangan, ditimbang: R.total.ditimbang, awas: R.total.kedatanganAwas, kgKurang: R.total.kgKurang, tujuan: { ke: 'stok', lembar: 'masuk' } },
  };
}

/** Seluruh dasbor untuk satu saat. Tiap kelompok dibungkus: galat di satu kelompok tampil sebagai kalimat di kelompok itu, kelompok lain tetap jalan.
 *  lama (owner 3 Okt, ganti rentang patah-patah): hasil dasbor saat & data yang SAMA — hanya tren yang memakai rentang, jadi hari ini · bulan ini · stok ·
 *  tagihan diambil dari situ dan cuma tren yang dihitung (dulu seluruh dasbor dihitung ulang tiap ganti Hari / Minggu / Bulan). */
export function susunDasbor(kini, rentang, lama) {
  const aman = (nama, f) => { try { return f(); } catch (e) { if (typeof console !== 'undefined') console.error('dasbor ' + nama, e); return { galat: String((e && e.message) || e) }; } };
  if (lama) return { hari: lama.hari, bulan: lama.bulan, stok: lama.stok, tagihan: lama.tagihan, mutu: lama.mutu, tren: aman('tren', () => dbTren(rentang, kini)) };
  return { hari: aman('hari ini', () => dbHariIni(kini)), bulan: aman('bulan ini', () => dbBulanIni(kini)), stok: aman('stok', () => dbStok(kini)), tagihan: aman('tagihan', () => dbTagihan(kini)), mutu: aman('mutu usaha', () => dbMutu(kini)), tren: aman('tren', () => dbTren(rentang, kini)) };
}
