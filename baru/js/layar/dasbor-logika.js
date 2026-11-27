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
import { AMBANG_HARI_KRITIS, JENDELA_LAJU_HARI, akhirBulanIso, kunciPelanggan } from '../mesin/pembantu.js';
import { hariIniIso, tanggalPendek, tanggalTutupAktif } from '../inti/format.js';
// paket Dasbor sensus: kalimat headline
import { RP } from '../inti/format.js';
import { rekapHari, hariTerakhir, daftarMinggu, daftarBulan, lpPertama, lpHariRentang, merekBulan, merekTeratas } from './laporan-logika.js';
import { kendaliBulan, titikImpas, pemicuBiaya, peringatanBiaya } from './kendali-biaya-logika.js';
import { saldoKantong, ugNamaTempat, ksHari, ugSetor, ugTambahHari } from './uang-logika.js';
// owner 26 Nov 2026 (kas & rekening): awal hari semua tempat (buku kas harian) & cocok rekening — APA ADANYA dari kas-rekening-logika (Laporan › Harian, Uang › Rekening)
import { khPosisi, crRingkas } from './kas-rekening-logika.js';
import { daftarKarcis } from './karcis-logika.js';
import { daftarBarang, susunWadah, umRingkas } from './stok-logika.js';
import { wbCekHari } from './wadah-bernama-logika.js';
import { semuaBon, KATA_STATUS, tertagihBon, pnRingkas, pnHariTagih } from './bon-logika.js';
// B2 (owner 17 Nov 2026): faktur pelanggan usaha yang lewat / segera jatuh tempo
import { fkPengingat, fkTeksTempo } from './faktur-logika.js';
// B3 (owner 18 Nov 2026): bayar di tempat yang uangnya belum disetor (merah, atas nama pengantar) & antar yang masih di jalan
import { ajCodBelumSetor, ajKalimatCod, ajDaftar } from './antar-logika.js';
// B4 (owner 18 Nov 2026): order rutin yang perlu dibuat (pengingat), pesanan yang dikirim ≤ 2 hari lagi, stok yang kurang untuk pesanan
import { poPengingat, poDaftarAktif, poHariKe, poCekStok, poKataStok } from './pesanan-logika.js';
// B5 (owner 18 Nov 2026): porsi pelanggan usaha bulan ini, pelanggan usaha teratas & faktur lewat tempo (Laporan › Laba › Per pelanggan)
import { pelangganBulan, pgHariTeks } from './laba-pelanggan-logika.js';
import { susunBon as bpSusunBon } from './bon-pemasok-logika.js';
import { hetHargaKasir } from './het-logika.js';
import { rekapTimbangMutu } from './stok-catat-logika.js';
// paket KPI laba (owner 24 Nov 2026): tiga margin + pembanding BPS, target harian, kas minimum, siklus uang, nota terbesar, kedatangan lewat batas HPP,
// lama pemenuhan pesanan, bon dalam kg beras — APA ADANYA dari kpi-laba-logika.js (yang memanggil fungsi sumber layar lain)
import { klMarginBulan, klTargetHari, klKasMinimum, klSiklusUang, klNotaTerbesar, klHppLewatBulan, klLamaPesanan, klBonKg, klModalPerKg } from './kpi-laba-logika.js';
// paket tanggal janji (owner 27 Nov 2026, sensus B55 B58 B60 B61 B65): tepat janji pemasok & antar — janji-logika apa adanya
import { jnRingkas } from './janji-logika.js';
// Pondasi (owner 24 Nov 2026): delapan lampu pondasi toko — APA ADANYA dari pondasi-logika.js (yang memanggil fungsi sumber layar lain)
import { pdPondasi } from './pondasi-logika.js';
// paket Susut + HPP & harga minimum (owner 26 Nov 2026): target & dua ambang susut, opname bulan ini, harga di bawah minimum, alarm dekat HET — APA ADANYA dari susut-harga-logika.js
import { shDasborSusut, shRingkasHarga } from './susut-harga-logika.js';
// paket Stok minus, label & kepatuhan (owner 26 Nov 2026): buku minus, tugas gudang, hilang & rusak per jenis, kemasan bertanggal (gudang-logika) · kalender kepatuhan (patuh-logika) — APA ADANYA
import { gdDasbor } from './gudang-logika.js';
import { ptDasbor } from './patuh-logika.js';
// paket Dasbor sensus (owner 26 Nov 2026, sensus ulang 1c: B1 B9 B88–B91 B95 B109 B113 B127) — APA ADANYA dari fungsi sumber: pembanding "jam segini" Cincin
// (ringkasan-logika rkJamSegini), rata-rata nilai nota (laporan-logika lpRataNota), stok minimum per barang (stok-minimum-logika), enam bulan (kendali-biaya
// trenBiaya · pondasi pdPosisiBulan). Widget angka utama: dasbor-widget-logika.js (membaca hasil dasbor ini, tanpa rumus uang).
import { rkIndeks, rkJamSegini } from './ringkasan-logika.js';
import { lpRataNota, LP_RUMUS_RATA_NOTA, lpNamaBulan } from './laporan-logika.js';
import { trenBiaya } from './kendali-biaya-logika.js';
import { pdPosisiBulan } from './pondasi-logika.js';
import { smBawahDari, smCek, smKunci, smPeta, smHariBawaan, smBatas } from './stok-minimum-logika.js';
// paket sisa sensus (owner 27 Nov 2026: B94 B68 B35 A47 A121) — APA ADANYA dari fungsi sumber: rekap rentang (laporan-logika), pembelian (susut-harga-logika),
// perkiraan telat bayar (bon-logika), PPh final sebagai pos anggaran & modal tertahan di stok (kpi-laba-logika), nota terbesar (riwayat), HPP lewat (barang masuk)
import { lpRekapRentang } from './laporan-logika.js';
import { klModalTertahan, klPph } from './kpi-laba-logika.js';
import { shTrenBeli, shPembelian, SH_RENTANG_BELI } from './susut-harga-logika.js';
import { pnPerkiraanTelat } from './bon-logika.js';
import { rwTerbesar } from './riwayat-logika.js';
import { ckHppLewat } from './stok-catat-logika.js';
// paket P2 (owner 27 Nov 2026: A136 B112 B26 B110 B124) — rapor bulanan (ini · lalu · target), arus kas bulan ini, lampu target owner untuk kartu lama — APA ADANYA
// dari rapor-bulan-logika (yang memanggil fungsi sumber layar lain); laba kotor hari ini & karcis = rekapHari / daftarKarcis yang sama dengan kartu Hari ini
import { rbRapor, rbArusKas, rbAmbangDasbor } from './rapor-bulan-logika.js';
import { klBagianHari } from './kpi-laba-logika.js';
// P1 (owner 27 Nov 2026: A3 A112 A114 A115 A116 B6 B7) — APA ADANYA dari fungsi sumber: untung per kg bulan (kpi-laba klKgBulan), stok dalam rupiah (klStokRp),
// terlaris & tren per merek per minggu (laporan-logika lpTerlaris / lpMerekMinggu), lama piutang (bon-logika pnDso)
import { klKgBulan, klStokRp } from './kpi-laba-logika.js';
import { lpTerlaris, lpMerekMinggu, lpSenin } from './laporan-logika.js';
import { pnDso } from './bon-logika.js';
// paket P5 (owner 27 Nov 2026): barang masuk hari ini (A125) · produksi bulan ini (B72) · stok dipesan (B51) — kartu & angka lewat "+ Tambah kartu" (katalog)
import { sgMasukHari, sgProduksiDeret, sgPesananRp } from './stok-pantau-logika.js';

export const DB_RENTANG = [['hari', 'Hari'], ['minggu', 'Minggu'], ['bulan', 'Bulan']];
const DB_TEMPAT = ['laci', 'brankas', 'rekening', 'amplop'];
// urutan status bon pelanggan di dasbor: yang paling mendesak dulu; tiga yang pertama = "jatuh tempo" (aturan tagih/macet di Pelanggan › Atur)
const DB_STATUS_BON = ['janjiLewat', 'macet', 'perluTagih', 'menunggu', 'baru'];
const DB_JATUH = ['janjiLewat', 'macet', 'perluTagih'];

/** HARI INI: omzet & laba kotor (Laporan › Harian), kas per tempat (Uang), karcis kasir yang menunggu dirinci (Jual).
 *  B94 (owner 27 Nov 2026): SR = saringan Dasbor bukan "Hari ini" → omzet, laba kotor, nota, retur, cara bayar & per jenis untuk RENTANG saringan (lpRekapRentang)
 *  + pembanding periode sebelumnya (dbPeriode — angka kartu Periode); awal = uang toko sebelum hari pertama rentang. Kas per tempat, kas kecil, setor, rekening &
 *  karcis = posisi SEKARANG (tidak bisa disaring; disebut di kartu). */
export function dbHariIni(kini, SR) {
  const iso = hariIniIso(kini); const sar = !!(SR && !SR.bawaan); const R = sar ? lpRekapRentang(SR.dari, SR.sampai) : rekapHari(iso); const S = saldoKantong(); const KC = daftarKarcis(kini);
  const awalIso = sar ? ugTambahHari(SR.dari, -1) : ugTambahHari(iso, -1);
  const P = sar ? dbCoba(() => dbPeriode({ id: SR.id, dari: SR.dari, sampai: SR.sampai }, kini)) : null;
  return {
    iso, periode: sar ? SR.nama + (SR.dari !== SR.sampai ? ' · ' + dbTglPendek(SR.dari) + ' – ' + dbTglPendek(SR.sampai) : '') : tanggalPendek(iso), sumber: sar ? P && P.sumber || 'Laporan › Harian' : 'Laporan › Harian',
    tujuan: sar ? (P && P.tujuan) || { ke: 'laporan', keluarga: 'harian', hari: SR.sampai } : { ke: 'laporan', keluarga: 'harian', hari: iso },
    saring: sar ? { nama: SR.nama, dari: SR.dari, sampai: SR.sampai, banding: P && !P.galat && !P.tolak ? { banding: P.banding, pctOmzet: P.pctOmzet, pctNota: P.pctNota } : null, diarsip: !!R.diarsip } : null,
    judul: sar ? SR.nama : 'Hari ini',
    jenis: R.jenis || null, omzet: R.omzet, nota: R.n, retur: R.retur, margin: R.margin, tanpaHpp: R.jumlahTanpaHpp, tunai: R.tunai, qris: R.qris, transfer: R.transfer || 0, kredit: R.kredit, nKredit: R.nKredit,
    kas: S.ada ? { ada: true, total: S.total, cocok: S.cocok, minus: S.minus, titik: S.teksTitik, tempat: DB_TEMPAT.map((id) => ({ id, nama: ugNamaTempat(id), n: S[id] })) } : { ada: false, tempat: [] },
    kasSumber: 'Uang › Pindah uang', kasTujuan: { ke: 'uang', keluarga: 'pindah' },
    karcis: { n: KC.nKarcis, rp: KC.total, rapikan: KC.nRapikan, hariIni: KC.daftar.filter((d) => d.hariIni).length }, karcisSumber: 'Jual › Karcis kasir', karcisTujuan: { ke: 'jual', lembar: 'karcis' },
    // owner 26 Nov 2026: awal hari (akhir kemarin, buku kas harian) · kas kecil hari ini · setor ke bank · cocok rekening — satu yang galat tidak mematikan kartu
    awalHari: dbCoba(() => { const A = khPosisi(awalIso); return A.ada ? { ada: true, total: A.total, sumber: A.sumber, iso: awalIso } : { ada: false, sebab: A.sebab, iso: awalIso }; }), awalSumber: 'Laporan › Harian', awalTujuan: { ke: 'laporan', keluarga: 'harian', hari: sar ? SR.dari : iso },
    kasKecil: dbCoba(() => ksHari(iso)), kasKecilTujuan: { ke: 'uang', keluarga: 'keluar' },
    setor: dbCoba(() => ugSetor()), setorTujuan: { ke: 'uang', keluarga: 'pindah' },
    rekening: dbCoba(() => crRingkas(kini)), rekeningTujuan: { ke: 'uang', keluarga: 'rekening' },
  };
}
const dbCoba = (f) => { try { return f(); } catch (e) { return { galat: String((e && e.message) || e) }; } };

/** BULAN INI: margin, biaya per jenis + lampu anggaran, laba bersih vs titik impas, susut, pemicu yang naik — semuanya Laporan › Biaya. */
export function dbBulanIni(kini, SR) {
  const key = SR && !SR.bawaan ? SR.bulan : hariIniIso(kini).slice(0, 7); const K = kendaliBulan(key, kini); const T = titikImpas(K, kini); const P = pemicuBiaya(K); const W = peringatanBiaya(K, P, T);
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
    // A47 (owner 27 Nov 2026): PPh final (perkiraan) = pos anggaran sendiri — di luar "Semua biaya", laba bersih & titik impas (klPph apa adanya)
    pph: dbCoba(() => klPph(K, kini)), judul: key === hariIniIso(kini).slice(0, 7) ? 'Bulan ini' : K.nama,
  };
}

/** STOK: kg per merek & perkiraan hari tersisa (Stok › Gudang), wadah literan (Stok › Wadah literan) + cek wadah hari tutup aktif (Tutup hari). */
export function dbStok(kini) {
  const SMP = smPeta(); const SMB = smHariBawaan();
  const merek = daftarBarang().filter((b) => b.jenis === 'karung' && !b.wadahStok && Math.abs(b.sisa) > 0.004)
    .map((b) => { const C = smCek({ kunci: smKunci('karung', b.kunci), sisa: b.sisa, laju: b.laju }, SMP, SMB);   // owner 26 Nov 2026 (B127): batas = stok minimum per barang
      return { nama: b.nama, kg: b.sisa, laju: b.laju, hari: b.hariHabis, minus: b.sisa < 0, awas: C.bawah, batasTeks: C.batas.teks, urut: C.minus ? -1 : C.kenapa === 'hari' ? C.hari : C.kenapa === 'jumlah' ? 0.5 : 1e6 }; })
    .sort((a, b) => b.kg - a.kg || a.nama.localeCompare(b.nama));
  const SW = susunWadah(null); const hariCek = tanggalTutupAktif(kini); const C = wbCekHari(hariCek);
  const wadah = SW.daftar.map((w) => { const c = C.daftar.find((x) => x.W === w.nama) || {};
    return { no: w.no, nama: w.nama, merek: w.stokSendiri ? w.karungAsal : w.karungNama, banding: w.resep.length > 1 ? w.resep.map((r) => r.takar).join(' : ') + ' — ' + w.resep.map((r) => r.merk).join(' : ') : '',
      diketahui: !!w.diketahui, isiKg: w.diketahui ? w.sisaKg : null, penuhKg: w.penuhKg, bagian: w.diketahui ? w.bagian : 0, perluIsi: !!(w.diketahui && w.perluIsi), lewat: w.lewat || 0,
      terakhirTanggal: w.isiTerakhirTanggal || '', terakhirJam: w.isiTerakhirJam || '', aktif: !!c.aktif, dicek: !!c.dicek, hasilTeks: c.hasilTeks || '', jamCek: c.jam || '' }; });
  return { periode: 'Sekarang · laju jual ' + JENDELA_LAJU_HARI + ' hari terakhir', sumber: 'Stok › Gudang', tujuan: { ke: 'stok', tab: 'gudang' }, merek, ambangHari: SMB, batasTeks: 'stok minimum · bawaan ≤ ' + SMB + ' hari' + (Object.keys(SMP).length ? ' · ' + Object.keys(SMP).length + ' barang punya angka sendiri' : ''), smTujuan: { ke: 'stok', tab: 'gudang', lembar: 'stokMin' },
    wadah, wadahSumber: 'Stok › Wadah literan', wadahTujuan: { ke: 'stok', tab: 'wadah' }, hariCek, nAktif: C.nAktif, nDicek: C.nDicek, belumDicek: C.belum, perluIsi: SW.perluIsi, belumDitandai: SW.belumDitandai,
    // owner 26 Nov 2026 (B49 B50 B53 B54 A62): satu yang galat tidak mematikan kartu stok
    gudang: dbCoba(() => gdDasbor(kini)) };
}

/** PIUTANG (Pelanggan › Bon) & UTANG PEMASOK (Harga & Pemasok › Bon pemasok) — yang jatuh tempo didahulukan. */
export function dbTagihan(kini) {
  const SB = semuaBon(kini); const bon = SB.filter((b) => b.sisa > 0);
  const perStatus = DB_STATUS_BON.map((s) => { const d = bon.filter((b) => b.status === s); return { status: s, kata: KATA_STATUS[s], n: d.length, rp: d.reduce((a, b) => a + b.sisa, 0), jatuh: DB_JATUH.indexOf(s) >= 0 }; });
  const jatuh = bon.filter((b) => DB_JATUH.indexOf(b.status) >= 0).sort((a, b) => DB_JATUH.indexOf(a.status) - DB_JATUH.indexOf(b.status) || b.sisa - a.sisa)
    .map((b) => ({ kunci: b.kunci, nama: b.nama, sisa: b.sisa, kata: b.cap, ket: b.ket, tujuan: { ke: 'pelanggan', keluarga: 'bon', orang: b.kunci } }));
  const BP = bpSusunBon(kini); const jauh = BP.bon.filter((b) => b.status === 'jauh'); const satuBon = (b) => ({ id: b.id, pemasok: b.pemasok, sisa: b.sisa, tempoTeks: b.tempoTeks, tanggal: b.tanggal, tujuan: { ke: 'harga', keluarga: 'bon', pemasok: b.pemasok } });
  const FP = fkPengingat(kini); const tujuF = { ke: 'pelanggan', keluarga: 'usaha', tab: 'faktur' };
  const COD = ajCodBelumSetor(hariIniIso(kini), true); const AJD = ajDaftar(hariIniIso(kini), '');
  const isoP = hariIniIso(kini); const ING = poPengingat(isoP); const hP = poHariKe(isoP); const tujuP = { ke: 'jual', lembar: 'pesanan' };
  const DEKAT = poDaftarAktif('').filter((o) => o.tanggalKirim && poHariKe(o.tanggalKirim) - hP <= 2);
  let STP = []; try { STP = poCekStok(isoP, daftarBarang()).filter((x) => x.awas); } catch (e) { STP = []; }
  return {
    pesanan: { nIngat: ING.length, ingat: ING.slice(0, 4).map((x) => ({ id: x.jadwal.id + ':' + x.tanggal, nama: x.jadwal.nama, ket: x.kata + ' · ' + x.jadwal.isi, tanggal: x.tanggal, awas: x.hariLagi <= 0, tujuan: tujuP })),
      nDekat: DEKAT.length, dekat: DEKAT.slice(0, 4).map((o) => ({ id: o.id, nama: o.nama, ket: 'kirim ' + tanggalPendek(o.tanggalKirim) + ' · ' + o.isi + (o.dp > 0 ? ' · DP' : ''), rp: o.nilai, tujuan: tujuP })),
      stok: STP.slice(0, 3).map(poKataStok), sumber: 'Jual › Pesanan', tujuan: tujuP },
    antar: { cod: COD.map((x) => ({ noSJ: x.noSJ, nama: x.nama, pengantar: x.pengantar, sisa: x.sisa, tanggal: x.tanggal, lewat: x.lewat, tujuan: { ke: 'pelanggan', keluarga: 'bon', orang: kunciPelanggan(x.nama) } })),
      rpCod: COD.reduce((a, x) => a + x.sisa, 0), kalimat: ajKalimatCod(COD), nJalan: AJD.jalan.length, nGagal: AJD.gagal.length, sumber: 'Jual › Antar' },
    faktur: { n: FP.daftar.length, rpLewat: FP.lewat, rpSegera: FP.segera, nLewat: FP.daftar.filter((f) => f.status === 'lewat').length, sumber: 'Pelanggan › Usaha › Faktur', tujuan: tujuF,
      daftar: FP.daftar.slice(0, 4).map((f) => ({ no: f.no, nama: f.nama, sisa: f.sisa, ket: fkTeksTempo(f), awas: f.status === 'lewat', tujuan: tujuF })) },
    periode: 'Sekarang · ' + tanggalPendek(hariIniIso(kini)),
    piutang: { total: bon.reduce((a, b) => a + b.sisa, 0), n: bon.length, perStatus, jatuh, nJatuh: jatuh.length, rpJatuh: jatuh.reduce((a, b) => a + b.sisa, 0), sumber: 'Pelanggan › Bon', tujuan: { ke: 'pelanggan', keluarga: 'bon' },
      kg: (() => { try { return klBonKg(bon.reduce((a, b) => a + b.sisa, 0), klModalPerKg()); } catch (e) { return null; } })(),   // paket KPI laba (butir 11)
      // owner 26 Nov 2026 (B29 · B30 · B31 · A105): piutang PER NOTA (Pelanggan › Bon › Jatuh tempo) & hari tagih tetap — apa adanya dari bon-logika
      nota: dbCoba(() => { const R = pnRingkas(kini, SB); return { lewat: R.lewat, hariIni: R.hariIni, minggu: R.minggu, nanti: R.nanti, tanpa: R.tanpa, total: R.total, menutup: R.menutup, selisih: R.selisih, nLewat: R.kelompok[0].n, orangLewat: R.kelompok[0].orang }; }),
      notaTujuan: { ke: 'pelanggan', keluarga: 'bon', tab: 'tempo' }, hariTagih: dbCoba(() => { const T = pnHariTagih(kini, SB); return { nyala: T.nyala, teks: T.teks, hariIni: !!T.hariIni, n: T.daftar.length, rp: T.rp }; }),
      // B35 (owner 27 Nov 2026): bon belum jatuh tempo milik pelanggan yang 2 dari 3 bon terakhirnya lunas lewat jatuh tempo — bon-logika pnPerkiraanTelat apa adanya
      telat: dbCoba(() => { const T = pnPerkiraanTelat(kini, SB); return { n: T.n, rp: T.rp, kalimat: T.kalimat, rumus: T.rumus, nTanpa: T.nTanpaRiwayat, nLewat: T.nLewatBiasa, rpLewat: T.rpLewatBiasa,
        daftar: T.daftar.slice(0, 4).map((o) => ({ kunci: o.kunci, nama: o.nama, rp: o.rp, kalimat: o.kalimat, jatuh: o.jatuhTerdekat, hariLagi: o.hariLagi, tujuan: o.tujuan })) }; }), telatTujuan: { ke: 'pelanggan', keluarga: 'bon', tab: 'tempo' } },
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
export function dbMutu(kini, SR) {
  const key = SR && !SR.bawaan ? SR.bulan : hariIniIso(kini).slice(0, 7);
  const aman = (f) => { try { return f(); } catch (e) { if (typeof console !== 'undefined') console.error('dasbor mutu', e); return { galat: String((e && e.message) || e) }; } };
  const T = aman(() => tertagihBon(kini)); const U = aman(() => umRingkas(kini)); const M = aman(() => merekBulan(key, kini)); const H = aman(() => hetHargaKasir(kini));
  const R = aman(() => rekapTimbangMutu({})); const TT = M.galat ? null : aman(() => merekTeratas(M, 'margin', 3));
  const SS = M.galat || M.diarsip ? null : aman(() => shDasborSusut(M, kini)); const HM = aman(() => shRingkasHarga(kini));
  return {
    periode: 'Sekarang · merek & susut ' + (M.galat ? key : M.nama), sumber: 'Laporan › Laba › Per merek', tujuan: { ke: 'laporan', keluarga: 'laba', bulan: key },
    tertagih: T.galat ? T : { keadaan: T.keadaan, rataTeks: T.rataTeks, hari: T.hari, teks: T.teks, periodeTeks: T.periodeTeks, tujuan: { ke: 'pelanggan', keluarga: 'bon' } },
    umur: U.galat ? U : { lambat: U.lambat.length, namaLambat: U.lambat.slice(0, 3).map((r) => r.nama), tertua: U.tertua.length ? { nama: U.tertua[0].nama, hari: U.tertua[0].umurAcuan } : null,
      lewatSimpan: U.lewatSimpan.length, kgLewat: U.kgLewatSimpan, batasSimpan: U.atur.batasSimpanHari,   // paket P5 (A43): tanda kedua
      putaran: U.putaranMerek, periodeHari: U.atur.periodeHari, tujuan: { ke: 'stok', tab: 'umur' } },
    merek: M.galat ? M : TT.galat ? TT : { nama: M.nama, arsip: !!M.diarsip, menutup: M.menutup, teratas: TT.daftar.map((g) => ({ merek: g.merek, margin: g.margin, pct: g.pct, keadaanMargin: g.keadaanMargin })),
      susutPct: M.susut ? M.susut.pct : null, susutTinggi: M.susut ? (Array.isArray(M.susut.tinggi) ? M.susut.tinggi.length : Number(M.susut.tinggi) || 0) : 0, tujuan: { ke: 'laporan', keluarga: 'laba', bulan: key } },
    het: H.galat ? H : { keadaan: H.keadaan, judul: H.judul, nAtas: H.nAtas, tujuan: { ke: 'harga', keluarga: 'katalog' } },
    mutu: R.galat ? R : { kedatangan: R.total.kedatangan, ditimbang: R.total.ditimbang, awas: R.total.kedatanganAwas, kgKurang: R.total.kgKurang, tujuan: { ke: 'stok', lembar: 'masuk' } },
    // paket Susut + HPP & harga minimum (owner 26 Nov 2026)
    susut: SS === null ? null : SS.galat ? SS : Object.assign({}, SS, { tujuan: { ke: 'laporan', keluarga: 'laba', bulan: key }, opnameTujuan: { ke: 'stok', lembar: 'cocok' } }),
    harga: HM.galat ? HM : Object.assign({}, HM, { tujuan: { ke: 'harga', keluarga: 'katalog' } }),
    // paket Stok minus, label & kepatuhan (owner 26 Nov 2026): kalender kepatuhan & cek aturan bulanan
    patuh: aman(() => ptDasbor(kini)),
  };
}

/** PAKET KPI LABA (owner 24 Nov 2026): margin kotor · usaha · bersih % bulan ini (+ BPS), omzet hari ini vs target, kas minimum, siklus uang, 3 nota terbesar hari ini,
 *  kedatangan lewat batas HPP bulan ini, lama pemenuhan pesanan. Tiap baris = kpi-laba-logika apa adanya; satu baris galat tidak mematikan yang lain. */
export function dbKpi(kini, SR) {
  const iso = hariIniIso(kini); const sar = !!(SR && !SR.bawaan); const key = sar ? SR.bulan : iso.slice(0, 7);
  const aman = (f) => { try { return f(); } catch (e) { if (typeof console !== 'undefined') console.error('dasbor kpi', e); return { galat: String((e && e.message) || e) }; } };
  // B94: margin = bulan saringan · nota terbesar, kedatangan lewat batas HPP & modal tertahan = rentang saringan · target harian, kas minimum, siklus uang &
  // pemenuhan pesanan = hari ini / sekarang (tidak bisa disaring — disebut di kartu). A121: modal tertahan di stok (bawaan: bulan ini sampai hari ini).
  return { periode: sar ? 'Margin ' + SR.bulanNama + ' · ' + SR.nama + ' · target, kas & siklus: sekarang' : 'Bulan ini & hari ini', sumber: 'Laporan › Laba', tujuan: { ke: 'laporan', keluarga: 'laba', bulan: key },
    margin: aman(() => klMarginBulan(key, kini)), target: aman(() => klTargetHari(kini)), kas: aman(() => klKasMinimum()), siklus: aman(() => klSiklusUang(kini)),
    nota: aman(() => (sar ? Object.assign({ rentang: 'saring', judul: SR.nama }, rwTerbesar(SR.dari, SR.sampai, 3)) : Object.assign({ judul: 'hari ini' }, klNotaTerbesar('hari', kini, 3)))),
    hpp: aman(() => (sar ? Object.assign({ key, nama: SR.nama }, ckHppLewat(SR.dari, SR.sampai)) : klHppLewatBulan(key))), pesanan: aman(() => klLamaPesanan(kini)),
    modal: aman(() => (sar ? klModalTertahan(kini, SR.dari, SR.sampai) : klModalTertahan(kini, iso.slice(0, 8) + '01', iso))), saring: sar ? SR.nama : '',
    kg: aman(() => klKgBulan(key, kini)),   // P1 A112: untung per kg bulan (kartu Margin & target — baris tetap, keputusan owner 27 Nov 2026)
    // paket tanggal janji (owner 27 Nov 2026): tepat janji = 90 hari terakhir sampai sekarang (tidak ikut saringan — rinciannya di Laporan › Pondasi)
    janji: aman(() => jnRingkas(kini)) };
}

/** B5 PELANGGAN USAHA bulan ini (owner 18 Nov 2026): porsi laba kotor & omzet pelanggan usaha, tiga teratas menurut laba kotor, faktur lewat jatuh tempo — APA
 *  ADANYA dari pelangganBulan (Laporan › Laba › Per pelanggan, satu sumber, menutup ke laba kotor Laporan). Tidak ada rumus uang di sini. */
export function dbB2b(kini, SR) {
  const key = SR && !SR.bawaan ? SR.bulan : hariIniIso(kini).slice(0, 7); const G = pelangganBulan(key, 1, kini); const tujuan = { ke: 'laporan', keluarga: 'laba', bulan: key };
  if (G.diarsip) return { nama: G.nama, arsip: true, kalimat: G.kalimat, periode: G.nama, sumber: 'Laporan › Laba › Per pelanggan', tujuan };
  return { nama: G.nama, arsip: false, periode: G.nama + (G.berjalan ? ' · berjalan' : ''), sumber: 'Laporan › Laba › Per pelanggan', tujuan, menutup: G.menutup, kalimat: G.kalimat,
    ada: !!G.usaha, porsiLaba: G.b2b ? G.b2b.porsiLaba : null, porsiOmzet: G.b2b ? G.b2b.porsiOmzet : null, laba: G.b2b ? G.b2b.laba : null, omzet: G.b2b ? G.b2b.omzet : 0, nOrang: G.b2b ? G.b2b.nOrang : 0,
    labaKotor: G.L.margin, tingkat: G.tingkat.map((t) => ({ id: t.id, nama: t.nama, laba: t.labaKotor, porsiLaba: t.porsiLaba, omzet: t.omzet, nOrang: t.nOrang })),
    teratas: G.orang.filter((o) => o.labaKotor !== null && !o.tanpaJualan).slice(0, 3).map((o) => ({ nama: o.nama, tingkat: o.tingkatNama, laba: o.labaKotor, pct: o.pct, rata: pgHariTeks(o.tempo.rata) })),
    lewat: G.lewat, rataUsaha: G.usaha ? pgHariTeks(G.usaha.tempo.rata) : '—' };
}

/** PONDASI TOKO (owner 24 Nov 2026): delapan lampu apa adanya dari pdPondasi (Laporan › Pondasi — satu sumber). Tidak ada rumus uang di sini. */
export function dbPondasi(kini) { return Object.assign({ periode: 'Hari ini', sumber: 'Laporan › Pondasi', tujuan: { ke: 'laporan', keluarga: 'pondasi' } }, pdPondasi(kini)); }

/** Seluruh dasbor untuk satu saat. Tiap kelompok dibungkus: galat di satu kelompok tampil sebagai kalimat di kelompok itu, kelompok lain tetap jalan.
 *  lama (owner 3 Okt, ganti rentang patah-patah): hasil dasbor saat & data yang SAMA — hanya tren yang memakai rentang, jadi hari ini · bulan ini · stok ·
 *  tagihan diambil dari situ dan cuma tren yang dihitung (dulu seluruh dasbor dihitung ulang tiap ganti Hari / Minggu / Bulan). */
const DB_KELOMPOK = { hari: ['hari ini', dbHariIni], bulan: ['bulan ini', dbBulanIni], stok: ['stok', dbStok], tagihan: ['tagihan', dbTagihan], mutu: ['mutu usaha', dbMutu], b2b: ['pelanggan usaha', dbB2b], kpi: ['margin & target', dbKpi], pondasi: ['pondasi toko', dbPondasi], beli: ['pembelian', dbBeli] };
/** B94 (owner 27 Nov 2026): kelompok yang IKUT saringan Dasbor. Yang lain = posisi sekarang (stok, wadah, piutang & utang, pondasi), punya rentangnya sendiri
 *  (tren omzet, enam bulan) atau memang "hari ini" (banding jam segini) — disebut di kartunya, tidak diam-diam. */
export const DB_IKUT_SARING = ['hari', 'bulan', 'kpi', 'mutu', 'b2b', 'beli'];
/** Satu kelompok dasbor ('hari' · 'bulan' · 'stok' · 'tagihan' · 'mutu' · 'b2b' · 'tren'), dibungkus aman (galat = kalimat di kelompok itu) dan — kalau
 *  ingat(kunci, f) diberikan — diingat dengan kunci kelompoknya. Dipakai susunDasbor dan pemanasan di latar (kunci SAMA → hasil yang dipanaskan terpakai).
 *  SR = dbSaring(…) (B94): kelompok DB_IKUT_SARING dihitung untuk saringan itu; saringan bawaan (Hari ini) = kunci & angka PERSIS seperti dulu. */
export function dbKelompok(kel, kini, rentang, ingat, SR) {
  const aman = (nama, f) => { try { return f(); } catch (e) { if (typeof console !== 'undefined') console.error('dasbor ' + nama, e); return { galat: String((e && e.message) || e) }; } };
  const ikut = DB_IKUT_SARING.indexOf(kel) >= 0; const S = ikut && SR && !SR.bawaan ? SR : null;
  const hitung = kel === 'tren' ? () => aman('tren', () => dbTren(rentang, kini)) : () => aman(DB_KELOMPOK[kel][0], () => DB_KELOMPOK[kel][1](kini, S));
  return ingat ? ingat(kel === 'tren' ? 'tren|' + rentang : S ? kel + '|saring|' + S.kunci : dbKunciTambahan(kel, kini), hitung) : hitung();   // paket Dasbor sensus: banding berkunci 5 menit
}
// mulus Android paket 3 (owner 23 Nov 2026): ingat(kunci, f) dari layar (Ringkasan: ingatan per versi + kunci luar) — tiap kelompok diingat sendiri, jadi
// pemanasan di latar bisa menghitungnya SATU PER SATU dan Dasbor yang dibuka sesudahnya tinggal menggambar. Tanpa ingat = hitung langsung seperti dulu.
export function susunDasbor(kini, rentang, lama, ingat, saring) {
  // B94: saring = dbSaring(pilihan, kini) — tanpa saring / "Hari ini" = Dasbor seperti dulu. lama = hasil saat, data & saringan yang SAMA (ganti rentang tren saja)
  const SR = saring || null; const k = (nama) => dbKelompok(nama, kini, rentang, ingat, SR);
  const inti = () => {   // bentuk lama apa adanya (uji lain memegang kalimatnya); pembelian & saringan ditempel sesudahnya
    if (lama) return { hari: lama.hari, bulan: lama.bulan, stok: lama.stok, tagihan: lama.tagihan, mutu: lama.mutu, b2b: lama.b2b, kpi: lama.kpi, pondasi: lama.pondasi, tren: k('tren') };
    return { hari: k('hari'), bulan: k('bulan'), stok: k('stok'), tagihan: k('tagihan'), mutu: k('mutu'), b2b: k('b2b'), kpi: k('kpi'), pondasi: k('pondasi'), tren: k('tren') };
  };
  const D = Object.assign(inti(), lama ? { beli: lama.beli, saring: lama.saring } : { beli: k('beli'), saring: SR });
  return Object.assign(D, lama ? { rapor: lama.rapor } : { rapor: k('rapor') });   // P2: rapor bulanan (ikut saringan: bulan kartu bulanan)
}
/** Urutan pemanasan dasbor di latar: yang paling atas di layar dulu. */
export const DB_PANAS = ['hari', 'kpi', 'bulan', 'stok', 'tagihan', 'tren', 'mutu', 'b2b', 'pondasi'];
DB_PANAS.push('beli');   // B68 (owner 27 Nov 2026): kartu Pembelian ikut dipanaskan
DB_PANAS.push('rapor');   // P2 (owner 27 Nov 2026): rapor bulanan ikut dipanaskan
DB_IKUT_SARING.push('rapor');   // P2: rapor memakai bulan saringan (sama dengan kartu Bulan ini)
DB_KELOMPOK.rapor = ['rapor bulan', dbRapor];

/**
 * P2 (owner 27 Nov 2026) — RAPOR BULAN untuk Dasbor: scorecard mode Laba & mode Kas (saklar, owner: "Dua-duanya"), arus kas bulan ini, dan lampu target owner untuk
 * angka yang SUDAH tampil di kartu lama (margin kotor %, piutang, karcis belum dirinci, laba kotor hari ini). Semua = rapor-bulan-logika apa adanya. Saringan: bulan
 * kartu bulanan (SR.bulan); lampu laba kotor HARI INI hanya tanpa saringan (kartu Hari ini yang disaring memajang rentang, bukan hari ini).
 */
export function dbRapor(kini, SR) {
  const iso = hariIniIso(kini); const sar = !!(SR && !SR.bawaan); const key = sar ? SR.bulan : iso.slice(0, 7);
  const R = rbRapor(key, kini, 'laba'); const RK = dbCoba(() => rbRapor(key, kini, 'kas')); const AK = dbCoba(() => rbArusKas(key, kini));
  const kiniBulan = key === iso.slice(0, 7); const RH = kiniBulan && !sar ? dbCoba(() => rekapHari(iso)) : null; const KC = kiniBulan ? dbCoba(() => daftarKarcis(kini)) : null;
  const ambang = dbCoba(() => rbAmbangDasbor(R, kini, klBagianHari(kini), RH && !RH.galat ? RH.margin : null, kiniBulan ? R.X.piutang : null, KC && !KC.galat ? KC.nKarcis : null));
  return { key, nama: R.nama, periode: R.nama + (R.berjalan ? ' · hari ke-' + R.hariJalan + ' dari ' + R.nHari : R.diarsip ? ' · tutup buku' : '') + ' vs ' + R.namaLalu, sumber: R.sumber, tujuan: R.tujuan,
    laba: R, kas: RK, arus: AK, ambang, judul: kiniBulan ? 'Rapor bulan ini' : 'Rapor ' + R.nama };
}

/** B68 (owner 27 Nov 2026): PEMBELIAN — tren per hari (14) · minggu (8) · bulan (6) dari kedatangan barang (susut-harga-logika shTrenBeli; batang bulan = "+ Pembelian"
 *  HPP periode Laporan › Bulanan) + jumlah di periode saringan (bawaan: hari ini & bulan ini). Ketiga rentang dihitung sekali (murah), pita di kartu hanya memilih. */
export function dbBeli(kini, SR) {
  const iso = hariIniIso(kini); const tren = {}; SH_RENTANG_BELI.forEach((r) => { tren[r[0]] = shTrenBeli(r[0], kini); });
  const P = SR ? shPembelian(SR.dari, SR.sampai) : shPembelian(iso, iso); const B = shPembelian(iso.slice(0, 8) + '01', iso);
  return { periode: SR ? SR.nama + (SR.dari !== SR.sampai ? ' · ' + dbTglPendek(SR.dari) + ' – ' + dbTglPendek(SR.sampai) : '') : 'Hari ini & bulan ini', sumber: 'Stok › Barang masuk', tujuan: { ke: 'stok', lembar: 'masuk' },
    tren, rumus: tren.bulan.rumus, periodeNama: SR ? SR.nama : 'Hari ini', saring: P, bulan: SR ? null : B, bulanNama: lpNamaBulan(iso.slice(0, 7)) };
}

/**
 * B94 — SATU SARINGAN UNTUK SEMUA KARTU Dasbor (owner 27 Nov 2026; sensus: "filter di atas dasbor yang menyetel periode untuk SEMUA kartu sekaligus"). pil =
 * pilihan pita (sama dengan kartu Periode — satu ingatan perangkat). Rentang = dbRentangPeriode (tujuh pilihan, tolak berkalimat). Kartu BULANAN (laba bersih,
 * biaya & anggaran, pemicu, margin, susut per merek, pelanggan usaha) memakai satu bulan: Bulan lalu = bulan lalu; selain itu = bulan tanggal akhir rentang
 * (rentang lintas bulan disebut). Pilihan yang ditolak (mis. tanggal belum terjadi) = Dasbor tetap Hari ini + kalimat tolaknya.
 * → { id, nama, dari, sampai, bawaan (= Hari ini, Dasbor seperti dulu), bulan, bulanNama, bulanKet, kunci (ingatan), tolak? }
 */
export function dbSaring(pil, kini) {
  const iso = hariIniIso(kini); const R = dbRentangPeriode(pil, kini);
  if (R.tolak) return Object.assign(dbSaringDari(dbRentangPeriode({ id: 'hari' }, kini), iso), { tolak: R.tolak, pilihan: R.id });
  return dbSaringDari(R, iso);
}
function dbSaringDari(R, iso) {
  const bulan = R.id === 'bulanLalu' ? R.dari.slice(0, 7) : R.sampai.slice(0, 7); const lintas = R.dari.slice(0, 7) !== R.sampai.slice(0, 7);
  const bulanKet = R.id === 'hari' || R.id === 'bulan' || R.id === 'bulanLalu' ? '' : 'kartu bulanan memakai ' + lpNamaBulan(bulan) + (lintas ? ' — bulan tanggal akhir; laba bersih & anggaran dihitung per bulan penuh' : ' — bulan tanggal itu');
  return { id: R.id, nama: R.nama, dari: R.dari, sampai: R.sampai, bawaan: R.id === 'hari', bulan, bulanNama: lpNamaBulan(bulan), bulanBerjalan: bulan === iso.slice(0, 7), bulanKet, lintas,
    kunci: R.id === 'hari' ? 'hari' : R.id + '|' + R.dari + '|' + R.sampai };
}
/** Kalimat di bawah pita saringan: yang ikut & yang tetap "sekarang". */
export const DB_SARING_TETAP = 'Tetap sekarang (tidak bisa disaring): uang toko per tempat, stok & wadah, piutang & utang pemasok, pondasi, target harian, kas minimum & siklus uang · punya rentang sendiri: tren omzet & enam bulan · angka bernama "hari ini" (dibanding jam segini) tetap hari ini';


// ==================== paket Dasbor sensus (owner 26 Nov 2026) ====================
const dbP2 = (n) => String(n).padStart(2, '0');
const dbJamTeks = (d) => dbP2(d.getHours()) + '.' + dbP2(d.getMinutes());
const DB_NAMA_HARI = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
const dbHariMinggu = (iso) => DB_NAMA_HARI[new Date(iso + 'T12:00:00').getDay()];
const dbPct = (a, b) => (b > 0 ? (a / b - 1) * 100 : null);
const dbBulanGeser = (key, n) => { const t = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)) - 1 + n; const y = t + Math.floor(m / 12), mm = ((m % 12) + 12) % 12; return y + '-' + dbP2(mm + 1); };
/** "13 Nov" dari ISO (tanpa tahun). */
const dbTglPendek = (iso) => tanggalPendek(iso).replace(/ \d{4}$/, '');

/**
 * B1 · B9 · B113 — OMZET HARI INI DIBANDINGKAN sampai jam yang sama (owner 26 Nov 2026: "kemarin + minggu lalu"): kemarin jam segini & hari yang sama minggu
 * lalu jam segini = rumus Cincin (rkJamSegini, satu sumber); omzet & nota hari ini = Laporan › Harian (rekapHari). Rata-rata nilai nota hari ini & bulan ini
 * (lpRataNota) + bulan lalu sampai tanggal yang sama. ket ≠ '' = pembanding tidak bisa dihitung (sebelum toko mencatat / rincian per jam ikut arsip tutup buku).
 */
export function dbBanding(kini) {
  const iso = hariIniIso(kini); const menit = kini.getHours() * 60 + kini.getMinutes(); const jam = dbJamTeks(kini);
  const R = rekapHari(iso); const ix = rkIndeks(); const H = rkJamSegini(ix, iso, null);
  const satu = (t, nama) => { const X = rkJamSegini(ix, t, menit); const tujuan = { ke: 'laporan', keluarga: 'harian', hari: t };
    if (X.ket) return { ada: false, iso: t, nama, ket: X.ket, tujuan };
    return { ada: true, iso: t, nama, omzet: X.omzet, nota: X.nota, rata: X.nota > 0 ? X.omzet / X.nota : null, selisih: R.omzet - X.omzet, pct: dbPct(R.omzet, X.omzet), tujuan }; };
  const kmr = ugTambahHari(iso, -1), mg = ugTambahHari(iso, -7);
  return { iso, jam, periode: 'Hari ini sampai ' + jam, sumber: 'Laporan › Harian', tujuan: { ke: 'laporan', keluarga: 'harian', hari: iso },
    nota: R.n, omzet: R.omzet, rata: R.n > 0 ? R.omzet / R.n : null, cincin: H.ket ? null : { omzet: H.omzet, nota: H.nota },
    kemarin: satu(kmr, 'kemarin'), mingguLalu: satu(mg, dbHariMinggu(mg) + ' lalu'), bulan: dbBulanBanding(kini), rumusRata: LP_RUMUS_RATA_NOTA };
}
/** Bulan ini (tanggal 1 sampai hari ini) vs bulan lalu sampai tanggal yang sama: omzet, laba kotor, nota, rata-rata nilai nota (lpRataNota). */
export function dbBulanBanding(kini) {
  const iso = hariIniIso(kini); const key = iso.slice(0, 7); const ini = lpRataNota(key + '-01', iso); const kL = dbBulanGeser(key, -1);
  const akhirL = akhirBulanIso(kL); const sampaiL = kL + '-' + iso.slice(8, 10) > akhirL ? akhirL : kL + '-' + iso.slice(8, 10); const pertama = lpPertama();
  const lalu = !pertama || pertama > sampaiL ? { ada: false, ket: 'bulan lalu belum ada catatan' } : pertama > kL + '-01' ? { ada: false, ket: 'catatan toko baru mulai ' + tanggalPendek(pertama) + ' — bulan lalu tidak utuh' }
    : Object.assign({ ada: true }, lpRataNota(kL + '-01', sampaiL));
  return { key, nama: lpNamaBulan(key), namaLalu: lpNamaBulan(kL), sampaiLalu: sampaiL, ini, lalu,
    pctOmzet: lalu.ada ? dbPct(ini.omzet, lalu.omzet) : null, pctRata: lalu.ada && ini.rata !== null && lalu.rata ? dbPct(ini.rata, lalu.rata) : null,
    tujuan: { ke: 'laporan', keluarga: 'bulanan', bulan: key }, tujuanLalu: { ke: 'laporan', keluarga: 'bulanan', bulan: kL } };
}

/** B127 — barang di bawah STOK MINIMUM per barang (beras karung & kemasan), penghitung yang SAMA dengan Perlu perhatian (smBawahDari) atas Stok › Gudang. */
export function dbStokMin(kini) {
  const S = smBawahDari(daftarBarang());
  return Object.assign(S, { periode: 'Sekarang · bawaan ≤ ' + S.bawaan + ' hari', sumber: 'Stok › Gudang › Stok minimum', tujuan: { ke: 'stok', tab: 'gudang', lembar: 'stokMin' },
    kalimat: S.n ? S.n + ' dari ' + S.dicek + ' barang di bawah stok minimum' : 'Semua ' + S.dicek + ' barang di atas stok minimum' });
}

/** B113 — ENAM BULAN: laba bersih, biaya & omzet per bulan (Laporan › Biaya trenBiaya) · kas, piutang, stok & utang pemasok per akhir bulan (Laporan › Pondasi). */
export function dbEnam(kini) {
  const B = trenBiaya(kini, 6); let P = []; let galatP = '';
  try { P = pdPosisiBulan(kini, 6); } catch (e) { galatP = String((e && e.message) || e); }
  return { periode: '6 bulan terakhir', sumber: 'Laporan › Biaya', tujuan: { ke: 'laporan', keluarga: 'biaya' }, posisiSumber: 'Laporan › Pondasi', posisiTujuan: { ke: 'laporan', keluarga: 'pondasi' },
    bulan: B.daftar.map((b) => ({ key: b.key, pendek: b.pendek, berjalan: !!b.berjalan, tanpaCatatan: !!b.tanpaCatatan, sebelumBuku: !!b.sebelumBuku, omzet: b.omzet, margin: b.margin, semuaBiaya: b.semuaBiaya, labaBersih: b.labaBersih, tujuan: { ke: 'laporan', keluarga: 'biaya', bulan: b.key } })),
    sebelumBuku: B.sebelumBuku, ada: B.ada,
    posisi: P.map((b) => ({ key: b.key, nama: b.nama, berjalan: !!b.berjalan, ada: !!b.ada, kenapa: b.kenapa || '', kas: b.ada ? b.kas : null, piutang: b.ada ? b.piutang : null, stok: b.ada ? b.stok : null, utangPemasok: b.ada ? b.utangPemasok : null })), galatPosisi: galatP };
}

/** B95 — SARINGAN TANGGAL Dasbor. Preset + "Pilih tanggal"; Tahun ini = tahun buku toko (1 Jan – 31 Des, tutup buku 31 Des). */
export const DB_PERIODE = [['hari', 'Hari ini'], ['kemarin', 'Kemarin'], ['h7', '7 hari'], ['bulan', 'Bulan ini'], ['bulanLalu', 'Bulan lalu'], ['tahun', 'Tahun ini'], ['pilih', 'Pilih tanggal']];
const DB_ISO = /^\d{4}-\d{2}-\d{2}$/;
const dbSelisihHari = (a, b) => Math.round((new Date(b + 'T12:00:00') - new Date(a + 'T12:00:00')) / 86400000);
/** Rentang satu pilihan: { id, nama, dari, sampai, banding: { dari, sampai, nama, jamSegini }, bulan: [key…] (laba bersih dihitung kalau bulannya utuh/berjalan) } | { tolak }. */
export function dbRentangPeriode(pil, kini) {
  const P = pil || {}; const id = DB_PERIODE.some((x) => x[0] === P.id) ? P.id : 'hari'; const iso = hariIniIso(kini); const key = iso.slice(0, 7); const nama = DB_PERIODE.find((x) => x[0] === id)[1];
  const kmr = ugTambahHari(iso, -1); const kL = dbBulanGeser(key, -1);
  if (id === 'hari') return { id, nama, dari: iso, sampai: iso, banding: { dari: kmr, sampai: kmr, nama: 'kemarin jam segini', jamSegini: true }, bulan: [], tujuan: { ke: 'laporan', keluarga: 'harian', hari: iso } };
  if (id === 'kemarin') { const k2 = ugTambahHari(iso, -2); return { id, nama, dari: kmr, sampai: kmr, banding: { dari: k2, sampai: k2, nama: dbHariMinggu(k2) + ' ' + dbTglPendek(k2) }, bulan: [], tujuan: { ke: 'laporan', keluarga: 'harian', hari: kmr } }; }
  if (id === 'h7') { const d = ugTambahHari(iso, -6); return { id, nama, dari: d, sampai: iso, banding: { dari: ugTambahHari(iso, -13), sampai: ugTambahHari(iso, -7), nama: '7 hari sebelumnya' }, bulan: [], ket: 'termasuk hari ini yang masih berjalan', tujuan: { ke: 'laporan', keluarga: 'harian', hari: iso } }; }
  if (id === 'bulan') { const B = dbBulanBanding(kini); return { id, nama: B.nama, dari: key + '-01', sampai: iso, banding: { dari: kL + '-01', sampai: B.sampaiLalu, nama: B.namaLalu + ' sampai tanggal ' + Number(B.sampaiLalu.slice(8, 10)) }, bulan: [key], berjalan: true, tujuan: B.tujuan }; }
  if (id === 'bulanLalu') { const k2 = dbBulanGeser(key, -2); return { id, nama: lpNamaBulan(kL), dari: kL + '-01', sampai: akhirBulanIso(kL), banding: { dari: k2 + '-01', sampai: akhirBulanIso(k2), nama: lpNamaBulan(k2) }, bulan: [kL], tujuan: { ke: 'laporan', keluarga: 'bulanan', bulan: kL } }; }
  if (id === 'tahun') { const t = iso.slice(0, 4); const t1 = String(Number(t) - 1); const bulan = []; for (let m = 1; m <= Number(key.slice(5, 7)); m++) bulan.push(t + '-' + dbP2(m));
    const sampaiL = t1 + iso.slice(4) > akhirBulanIso(t1 + iso.slice(4, 7)) ? akhirBulanIso(t1 + iso.slice(4, 7)) : t1 + iso.slice(4);
    return { id, nama: 'Tahun ' + t, dari: t + '-01-01', sampai: iso, banding: { dari: t1 + '-01-01', sampai: sampaiL, nama: 'tahun ' + t1 + ' sampai tanggal yang sama' }, bulan, berjalan: true, ket: 'tahun buku toko = 1 Januari – 31 Desember', tujuan: { ke: 'laporan', keluarga: 'tahunan' } }; }
  // pilih tanggal
  const dari = String(P.dari || ''), sampai = String(P.sampai || '');
  if (!DB_ISO.test(dari) || !DB_ISO.test(sampai)) return { id, nama, tolak: 'Pilih tanggal awal dan tanggal akhir' };
  if (dari > sampai) return { id, nama, tolak: 'Tanggal awal sesudah tanggal akhir — tukar keduanya' };
  if (sampai > iso) return { id, nama, tolak: 'Tanggal akhir sesudah hari ini (' + tanggalPendek(iso) + ') — belum terjadi' };
  const n = dbSelisihHari(dari, sampai) + 1;
  return { id, nama: dari === sampai ? tanggalPendek(dari) : tanggalPendek(dari) + ' – ' + tanggalPendek(sampai), dari, sampai, nHari: n, banding: { dari: ugTambahHari(dari, -n), sampai: ugTambahHari(dari, -1), nama: n + ' hari sebelumnya' }, bulan: [],
    tujuan: { ke: 'laporan', keluarga: 'harian', hari: sampai } };
}
/**
 * Angka satu periode Dasbor: omzet, laba kotor, nota, rata-rata nilai nota, retur (lpRataNota) + pembanding (periode sebelumnya; Hari ini = kemarin jam segini,
 * rumus Cincin). Laba bersih & biaya hanya untuk pilihan berbulan (Bulan ini / Bulan lalu / Tahun ini) = Σ kendaliBulan per bulan (mesin laba Laporan › Laba,
 * tagihan bulanan dipotong sebulan penuh). Rentang hari bebas: laba bersih TIDAK dihitung (tagihan bulanan tidak dipecah per hari) — disebut.
 */
export function dbPeriode(pil, kini) {
  const R = dbRentangPeriode(pil, kini); if (R.tolak) return R;
  const X = lpRataNota(R.dari, R.sampai); const pertama = lpPertama(); const iso = hariIniIso(kini);
  let B;
  if (R.banding.jamSegini) { const J = rkJamSegini(rkIndeks(), R.banding.dari, kini.getHours() * 60 + kini.getMinutes()); B = J.ket ? { ada: false, ket: J.ket, nama: R.banding.nama } : { ada: true, nama: R.banding.nama, omzet: J.omzet, nota: J.nota, rata: J.nota > 0 ? J.omzet / J.nota : null, margin: null }; }
  else if (!pertama || pertama > R.banding.sampai) B = { ada: false, nama: R.banding.nama, ket: 'belum ada catatan (toko mulai mencatat ' + (pertama ? tanggalPendek(pertama) : '—') + ')' };
  else if (pertama > R.banding.dari) B = { ada: false, nama: R.banding.nama, ket: 'tidak utuh — catatan toko baru mulai ' + tanggalPendek(pertama) };
  else B = Object.assign({ ada: true, nama: R.banding.nama }, lpRataNota(R.banding.dari, R.banding.sampai));
  const sebelum = pertama && R.dari < pertama ? 'catatan toko baru mulai ' + tanggalPendek(pertama) + ' — sebelum itu tidak ada angka' : '';
  let laba = null;
  if (R.bulan.length) {
    const bln = R.bulan.filter((k) => !pertama || k >= pertama.slice(0, 7)); const K = bln.map((k) => { const x = kendaliBulan(k, kini); return { key: k, labaBersih: x.labaBersih, semuaBiaya: x.semuaBiaya, berjalan: !!x.berjalan, final: !!x.final }; });
    laba = { bulan: K, labaBersih: K.reduce((a, x) => a + x.labaBersih, 0), semuaBiaya: K.reduce((a, x) => a + x.semuaBiaya, 0), berjalan: K.some((x) => x.berjalan), tujuan: R.id === 'tahun' ? { ke: 'laporan', keluarga: 'tahunan' } : { ke: 'laporan', keluarga: 'laba', bulan: R.bulan[0] } };
  }
  return { id: R.id, nama: R.nama, dari: R.dari, sampai: R.sampai, ket: [R.ket || '', sebelum].filter(Boolean).join(' · '), hariIni: R.sampai === iso,
    omzet: X.omzet, margin: X.margin, nota: X.nota, rata: X.rata, retur: X.retur, tanpaHpp: X.tanpaHpp, tanpaPotret: X.tanpaPotret, banding: B,
    pctOmzet: B.ada ? dbPct(X.omzet, B.omzet) : null, pctNota: B.ada ? dbPct(X.nota, B.nota) : null, pctRata: B.ada && X.rata !== null && B.rata ? dbPct(X.rata, B.rata) : null,
    laba, labaKet: R.bulan.length ? '' : 'laba bersih dihitung per bulan penuh — pilih Bulan ini / Bulan lalu / Tahun ini, atau buka Laporan › Laba', rumusRata: LP_RUMUS_RATA_NOTA,
    sumber: R.id === 'tahun' ? 'Laporan › Tahunan' : R.bulan.length ? 'Laporan › Bulanan' : 'Laporan › Harian', tujuan: R.tujuan };
}

/**
 * B109 — CAP "data per HH.MM": seberapa segar angka di layar. info = { jenis: 'firestore'|'cadangan'|'', masuk, memuat, hidup, putus: ms, tersimpan: ms, keterangan }.
 * Tersambung (semua koleksi dijawab server) = angka ikut berubah begitu ada catatan → "data per <jam sekarang>". Tanpa internet = jam terakhir tersambung
 * (putus; dibuka tanpa internet = jam tersambung terakhir yang diingat perangkat). Cadangan = saat cadangan diunduh. Tidak ada yang ditebak.
 */
export function dbCapData(info, kini) {
  const I = info || {}; const k = kini || new Date();
  if (I.jenis === 'cadangan') return { teks: 'data cadangan · ' + dbTglPendek(hariIniIso(k)) + ' ' + dbJamTeks(k), awas: true, hidup: false, judul: 'Angka dari ' + (I.keterangan || 'cadangan') + ' — "sekarang" dianggap saat cadangan itu diunduh' };
  if (I.jenis !== 'firestore' || !I.masuk) return { teks: 'belum ada data toko', awas: true, hidup: false, judul: 'Belum masuk ke data toko' };
  if (I.memuat) return { teks: 'memuat data…', awas: false, hidup: false, judul: 'Sebagian koleksi masih dimuat — angka bisa bertambah' };
  if (I.hidup) return { teks: 'data per ' + dbJamTeks(k), awas: false, hidup: true, judul: 'Tersambung ke server — angka berubah sendiri begitu ada catatan baru' };
  const t = Number(I.putus) || Number(I.tersimpan) || 0;
  if (!t) return { teks: 'data dari simpanan perangkat', awas: true, hidup: false, judul: 'Belum tersambung ke server sejak layar dibuka — catatan dari perangkat lain belum masuk' };
  const d = new Date(t); const lain = hariIniIso(d) !== hariIniIso(k); const kapan = (lain ? dbHariMinggu(hariIniIso(d)) + ' ' + dbTglPendek(hariIniIso(d)) + ' ' : '') + dbJamTeks(d);
  return { teks: 'data per ' + kapan + ' · tanpa internet', awas: true, hidup: false, judul: 'Terakhir tersambung ke server ' + kapan + ' — catatan sesudah itu dari perangkat lain belum masuk; catatan dari perangkat ini mengantre' };
}

/**
 * B91 — HEADLINE satu kalimat (owner 26 Nov 2026: "omzet + laba + mendesak"): omzet hari ini vs kemarin jam segini · laba bersih bulan ini sampai hari ini vs
 * titik impas (Laporan › Biaya titikImpas) · berapa hal perlu perhatian & yang paling mendesak (daftar Perlu perhatian Ringkasan, apa adanya). Tiap bagian
 * membawa tujuannya. Tanpa rumus baru: semua angka dari D (susunDasbor + dbTambahan) dan daftar perhatian.
 */
export function dbHeadline(D, perhatian) {
  const bag = []; const Bd = D && D.banding; const Bl = D && D.bulan; const pc = (x) => DESIMAL_1(Math.abs(x)) + '%';
  if (Bd && !Bd.galat) {
    const K = Bd.kemarin; let t = 'Omzet hari ini ' + RP(Bd.omzet);
    if (!K.ada) t += ' (kemarin ' + K.ket + ')';
    else if (K.pct === null) t += K.omzet === 0 ? (Bd.omzet > 0 ? ', kemarin jam segini belum ada jualan' : ', kemarin jam segini juga belum ada jualan') : ', kemarin jam segini ' + RP(K.omzet);
    else t += Math.abs(K.pct) < 0.05 ? ', sama dengan kemarin jam segini' : ', ' + (K.pct > 0 ? 'naik ' : 'turun ') + pc(K.pct) + ' dari kemarin jam segini';
    bag.push({ id: 'omzet', teks: t, awas: K.ada && K.pct !== null && K.pct < 0, tujuan: Bd.tujuan });
  }
  // B94: headline = ringkas HARI INI — bagian laba hanya kalau kartu bulan memegang bulan berjalan (saringan bulan lain tidak mengubah headline)
  if (Bl && !Bl.galat && !Bl.tanpaCatatan && Bl.impas && (!Bd || Bd.galat || !Bl.key || Bl.key === String(Bd.iso || '').slice(0, 7))) {
    const I = Bl.impas; const nm = String(Bl.nama || '').split(' ')[0];
    const t = 'laba bersih ' + nm + (Bl.berjalan ? ' sampai hari ini ' : ' ') + RP(I.labaSampai) + (I.menutup ? ', biaya sudah tertutup margin kotor' : I.kurang > 0 ? ', biaya masih ' + RP(I.kurang) + ' lebih besar dari margin kotor (belum impas)' : '');
    bag.push({ id: 'laba', teks: t, awas: !I.menutup, tujuan: Bl.labaTujuan });
  }
  const P = (perhatian || []).filter((x) => x && x.teks); const top = P.find((x) => x.awas) || P[0];
  bag.push(P.length ? { id: 'perhatian', teks: P.length + ' hal perlu perhatian, paling mendesak: ' + top.teks + (top.nilai ? ' (' + top.nilai + ')' : ''), awas: P.some((x) => x.awas), tujuan: null }
    : { id: 'perhatian', teks: 'tidak ada yang perlu perhatian', awas: false, tujuan: null });
  const teks = bag.map((b) => b.teks).join(' · ');
  return { bagian: bag, teks: teks.charAt(0).toUpperCase() + teks.slice(1) + '.', awas: bag.some((b) => b.awas), nPerhatian: P.length };
}
const DESIMAL_1 = (x) => String(Math.round(x * 10) / 10).replace('.', ',');

/** Kelompok tambahan paket sensus — dihitung & diingat per kelompok seperti yang lama (dbKelompok); ikut pemanasan di latar. */
Object.assign(DB_KELOMPOK, { banding: ['banding jam segini', dbBanding], stokMin: ['stok minimum', dbStokMin], enam: ['enam bulan', dbEnam] });
DB_PANAS.push('banding', 'stokMin', 'enam');
export const DB_TAMBAHAN = ['banding', 'stokMin', 'enam'];
/** Kunci ingatan kelompok tambahan: "jam segini" bergeser tiap 5 menit walau tidak ada catatan baru (dulu: angka pembanding pagi dipakai sampai sore). */
export const dbKunciTambahan = (n, kini) => (n === 'banding' ? 'banding|' + Math.floor((kini.getHours() * 60 + kini.getMinutes()) / 5) : n);
/** Hasil susunDasbor + kelompok paket sensus (banding · stokMin · enam), diambil dari ingatan yang sama — dipanggil sesudah tiap susunDasbor (ganti rentang:
 *  susunDasbor membuat objek baru dari hasil lama; kelompok tambahan diingat, jadi tidak dihitung ulang). */
export function dbTambahan(hasil, kini, ingat) { const H = hasil || {}; DB_TAMBAHAN.forEach((n) => { H[n] = dbKelompok(n, kini, null, ingat, H.saring || null); }); return H; }   // P1: saringan ikut (hanya kelompok DB_IKUT_SARING yang membacanya)

/**
 * P1 · PER KG & PER MINGGU (owner 27 Nov 2026; keputusan: kartu & angkanya lewat "+ Tambah kartu", untung per kg = baris tetap di Margin & target). Kelompok tambahan
 * yang IKUT saringan: terlaris & stok dalam rupiah = rentang saringan (bawaan Hari ini = bulan ini sampai hari ini, seperti modal tertahan); tren per merek = 4 minggu
 * terakhir (rentangnya sendiri); lama piutang = sekarang vs akhir minggu lalu. Semua APA ADANYA dari fungsi sumber Laporan / Pelanggan.
 */
export function dbKg(kini, SR) {
  const iso = hariIniIso(kini); const sar = !!(SR && !SR.bawaan); const dari = sar ? SR.dari : iso.slice(0, 8) + '01'; const sampai = sar ? SR.sampai : iso; const nama = sar ? SR.nama : 'Bulan ini';
  const aman = (f) => { try { return f(); } catch (e) { if (typeof console !== 'undefined') console.error('dasbor per kg', e); return { galat: String((e && e.message) || e) }; } };
  return { periode: nama + (dari !== sampai ? ' · ' + dbTglPendek(dari) + ' – ' + dbTglPendek(sampai) : ''), periodeNama: nama, sumber: 'Laporan › Mingguan · Per merek', tujuan: { ke: 'laporan', keluarga: 'mingguan' },
    terlaris: aman(() => lpTerlaris(dari, sampai, 5)), stok: aman(() => klStokRp(kini, dari, sampai)), tren: aman(() => lpMerekMinggu(lpSenin(iso), kini, 4)), dso: aman(() => pnDso(kini, 2)), saring: sar ? SR.nama : '' };
}
DB_KELOMPOK.kg = ['per kg & minggu', dbKg]; DB_IKUT_SARING.push('kg'); DB_TAMBAHAN.push('kg'); DB_PANAS.push('kg');

/**
 * Paket P5 · STOK, GUDANG & PRODUKSI (owner 27 Nov 2026): kelompok tambahan `gudang5` — TIDAK ikut saringan (barang masuk = HARI INI, produksi = bulan ini & 6 bulan,
 * pesanan = sekarang, umur = sekarang). Semua APA ADANYA dari stok-pantau-logika / stok-logika (sumber yang sama dengan Stok & Laporan); widgetnya hanya di katalog.
 */
export function dbGudang5(kini) {
  const iso = hariIniIso(kini); const aman = (f) => { try { return f(); } catch (e) { if (typeof console !== 'undefined') console.error('dasbor gudang P5', e); return { galat: String((e && e.message) || e) }; } };
  const U = aman(() => umRingkas(kini));
  return { periode: 'Sekarang', sumber: 'Stok › Produksi · Laporan › Harian', masuk: aman(() => sgMasukHari(iso)), produksi: aman(() => sgProduksiDeret(kini, 6)), pesanan: aman(() => sgPesananRp(kini)),
    simpan: U.galat ? U : { n: U.lewatSimpan.length, kg: U.kgLewatSimpan, batas: U.atur.batasSimpanHari, nama: U.lewatSimpan.slice(0, 3).map((r) => r.nama + ' ' + r.umurAcuan + ' hr'), tujuan: { ke: 'stok', tab: 'umur' } } };
}
DB_KELOMPOK.gudang5 = ['stok, gudang & produksi', dbGudang5]; DB_TAMBAHAN.push('gudang5'); DB_PANAS.push('gudang5');
