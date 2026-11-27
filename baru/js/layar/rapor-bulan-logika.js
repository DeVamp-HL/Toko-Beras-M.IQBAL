// RAPOR BULANAN · LEMBAR KPI, ANGGARAN vs AKTUAL, PECAHAN SELISIH, KOTOR vs BERSIH, ARUS KAS (paket P2 sensus 27 Nov 2026: A109 A110 A111 A136 B4 B26 B110
// B112 B124). Logika TANPA DOM, nama berawalan rb (bundel uji jsc satu lingkup). Dijaga alat-uji/uji_rapor_bulan.py (jsc kotak pasir + statis + --kontrol).
//
// ATURAN: TIDAK ADA RUMUS UANG BARU. Tiap angka MEMANGGIL fungsi sumber yang sudah dipakai layar lain (satu angka satu sumber) dan menyebut sumbernya:
//   omzet, laba kotor, HPP, biaya, laba bersih, kg terjual   → kendaliBulan (Laporan › Biaya; mesin laba yang sama dengan Laporan › Laba)
//   laba bersih sampai hari ini                               → titikImpas (Laporan › Biaya)
//   potongan nota & tawar (per bulan & per hari)              → pjPotonganBulan / pjPotonganHarian (Laporan › Pajak, omzet sebelum potongan)
//   retur, omzet & nota per hari                              → lpHariBulan (aturan rekap hari / hariTerakhir, satu lintasan per bulan)
//   susut % & target susut                                    → susutRentang (Per merek / Mingguan) · shTarget (target susut owner)
//   piutang akhir bulan                                       → hitungPiutang mesin (sisa > 0 — sama dengan neraca)
//   nilai stok rata-rata                                      → klModalTertahan (karung + kemasan, nilai modal)
//   uang masuk / keluar / kas bersih / bon baru               → intiBulan (Laporan › Bulanan, arus kas mesin) · rincian = hitungArusKasInti
//   siklus uang, PPh final                                    → klSiklusUang · klPph (kpi-laba)
//   karcis belum dirinci                                      → daftarKarcis (Jual › Karcis kasir)
// Yang dihitung DI SINI hanya perbandingan: perubahan % vs bulan lalu, lampu target owner (kbLampuTarget), perputaran & hari stok (HPP ÷ nilai stok rata-rata),
// hari bon (piutang akhir ÷ bon per hari), dan pecahan selisih laba kotor (volume · harga jual · harga beli — Σ = laba kotor − anggaran laba kotor, persis).
// Bulan berjalan: arus (omzet, kg, laba) dibanding bulan lalu memakai PERKIRAAN SEBULAN (linear) — cara yang sama dengan Peta biaya — dan disebut "perkiraan".
import { kendaliBulan, titikImpas, targetBulan, kbLampuTarget, catatanPos, AB_TARGET, abTeks } from './kendali-biaya-logika.js';
import { pjPotonganBulan, pjPotonganHarian } from './pajak-logika.js';
import { klModalTertahan, klSiklusUang, klPph, klPctTeks } from './kpi-laba-logika.js';
import { lpBulanPendek, lpHariBulan, intiBulan, susutRentang, daftarBulan } from './laporan-logika.js';
import { shTarget } from './susut-harga-logika.js';
import { daftarKarcis } from './karcis-logika.js';
import { ugBayaran, ugTambahHari } from './uang-logika.js';
import { hitungPiutang, hitungArusKasInti } from '../mesin/beku.js';
import { akhirBulanIso } from '../mesin/pembantu.js';
import { ingatPerVersi, tahunDiarsip, potretBulan } from '../data/toko.js';
import { RP, ANGKA, DESIMAL, hariIniIso, tanggalPendek } from '../inti/format.js';

const rbGeser = (key, n) => { const y = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)) - 1 + n; const d = new Date(Date.UTC(y + Math.floor(m / 12), ((m % 12) + 12) % 12, 1)); return d.toISOString().slice(0, 7); };
const rbBagi = (a, b) => (a !== null && a !== undefined && isFinite(a) && b > 0 ? a / b : null);
const rbPct = (a, b) => (a !== null && a !== undefined && isFinite(a) && b > 0 ? a / b * 100 : null);
/** Perubahan % ini vs lalu (null bila lalu tidak ada / 0). Penyebut |lalu| supaya laba minus → membaik terbaca naik. */
export const rbUbah = (ini, lalu) => (ini === null || ini === undefined || lalu === null || lalu === undefined || !isFinite(ini) || !isFinite(lalu) || Math.abs(lalu) < 0.5 ? null : (ini - lalu) / Math.abs(lalu) * 100);
export const rbUbahTeks = (p) => (p === null || p === undefined || !isFinite(p) ? '—' : (p > 0 ? '▲ ' : p < 0 ? '▼ ' : '') + klPctTeks(Math.abs(p)));
/** Satu angka untuk layar menurut satuannya. */
export function rbNilaiTeks(n, satuan) {
  if (n === null || n === undefined || !isFinite(n)) return '—';
  if (satuan === 'rp') return RP(Math.round(n)); if (satuan === 'rpkg') return RP(Math.round(n)) + '/kg'; if (satuan === 'kg') return ANGKA(Math.round(n)) + ' kg';
  if (satuan === 'pct') return klPctTeks(n); /* di bawah 1 % dua angka di belakang koma: potongan 0,01 % tidak tertulis 0 % */ if (satuan === 'kali') return DESIMAL(Math.round(n * 100) / 100) + '×'; if (satuan === 'hari') return DESIMAL(Math.round(n * 10) / 10) + ' hari';
  return ANGKA(Math.round(n));
}
export const RB_KATA_LAMPU = { hijau: 'aman', amber: 'mendekati', merah: 'lewat', tanpa: 'tanpa target', belum: 'belum bisa dihitung' };
/** Kata lampu menurut arah target: min (target) = tercapai / sedikit di bawah / di bawah target · maks (batas) = aman / mendekati batas / lewat batas. */
export const rbKataLampu = (arah, w) => (w === 'tanpa' || w === 'belum' ? RB_KATA_LAMPU[w] : arah === 'min' ? { hijau: 'tercapai', amber: 'sedikit di bawah target', merah: 'di bawah target' }[w] : { hijau: 'aman', amber: 'mendekati batas', merah: 'lewat batas' }[w]) || '';

// ---------- satu bulan: semua angka mentah dari sumbernya ----------
/** Angka satu bulan (key 'YYYY-MM') dari fungsi sumber; bulan berjalan = sampai hari ini. Diingat per versi data + hari. */
export function rbBulan(key, kini) { const iso = hariIniIso(kini); return ingatPerVersi('rbBulan|' + key + '|' + iso, () => rbBulanHitung(String(key), kini, iso)); }
function rbBulanHitung(key, kini, iso) {
  const B = ugBayaran(); const K = kendaliBulan(key, kini, B); const L = K.L || {}; const T = titikImpas(K, kini, B); const diarsip = !!K.diarsip || tahunDiarsip(key);
  const awal = key + '-01', akhir = akhirBulanIso(key); const sampai = K.berjalan && iso < akhir ? iso : akhir; const hari = K.hariJalan;
  const PT = pjPotonganBulan(key); const retur = L.returUang === undefined || L.returUang === null ? null : Number(L.returUang) || 0;
  const kotor = retur === null ? null : K.omzet + retur + PT.jumlah;
  // piutang akhir bulan (bulan berjalan: hari ini) = sisa bon pelanggan mesin; bulan yang sudah ditutup buku: dari neraca potret (bila ada)
  let piutang = null, nPiutang = 0; if (diarsip) { const Pt = potretBulan(key); const N = Pt && Pt.neraca && Pt.neraca.N; if (N && N.piutang !== null && N.piutang !== undefined) { piutang = Number(N.piutang) || 0; nPiutang = Number(N.nPiutang) || 0; } }
  else { const d = hitungPiutang(sampai).filter((x) => x.sisa > 0); piutang = d.reduce((a, x) => a + x.sisa, 0); nPiutang = d.length; }
  const I = intiBulan(key, kini, B); const bon = Number(I.kredit) || 0;
  const MT = diarsip ? null : klModalTertahan(kini, awal, sampai); const rataStok = MT && MT.rata !== null && MT.nHari > 0 ? MT.rata : null;
  const hpp = Number(L.hpp) || 0; const perputaran = rataStok > 0.5 ? hpp / rataStok : null; const hariStok = perputaran > 0 ? hari / perputaran : null;
  const S = susutRentang(awal, sampai); const susutPct = S && S.susut && S.susut.pct !== undefined ? S.susut.pct : null;
  return { key, nama: K.nama, pendek: lpBulanPendek(key, true), berjalan: K.berjalan, final: K.final, diarsip, tanpaCatatan: !!K.tanpaCatatan, hariJalan: hari, nHari: K.nHari, awal, sampai,
    omzet: K.omzet, retur, potNota: PT.nota, potTawar: PT.tawar, potongan: PT.jumlah, nPotongan: PT.n, kotor, potPct: kotor > 0 ? PT.jumlah / kotor * 100 : null,
    kg: K.kgTerjual, kgHitung: K.kgHitung, omzetHitung: K.omzetHitung, hpp, hppKg: rbBagi(hpp, K.kgHitung), jualKg: rbBagi(K.omzetHitung, K.kgHitung),
    labaKotor: K.margin, marginKotor: rbPct(K.margin, K.omzetHitung), biaya: K.semuaBiaya, labaBersih: K.labaBersih, labaSampai: T.labaSampai, marginBersih: rbPct(K.labaBersih, K.omzetHitung),
    susut: K.susut, susutPct, susutDiarsip: !!(S && S.diarsip), piutang, nPiutang, bon, dso: piutang !== null && bon > 0 && hari > 0 ? piutang / (bon / hari) : null,
    rataStok, perputaran, hariStok, masuk: I.masuk, keluar: I.keluar, kasBersih: I.bersih, cakupan: K.cakupan, tanpaHpp: L.jumlahTanpaHpp || 0, menutup: K.menutup, K };
}
/** Perkiraan sebulan (linear dari hari yang sudah jalan) untuk angka arus di bulan berjalan; selain itu angka itu sendiri. */
const rbSebulan = (X, n) => (n === null || n === undefined ? null : X.berjalan && X.hariJalan > 0 ? n / X.hariJalan * X.nHari : n);

// ---------- baris rapor: ini · lalu · % ubah · target · lampu ----------
/** Daftar baris rapor. arus = angka yang menumpuk sepanjang bulan (bulan berjalan dibanding lewat perkiraan sebulan). baik = arah yang baik. tg = id pos target. */
const RB_BARIS = [
  { id: 'kotor', nama: 'Penjualan kotor', satuan: 'rp', arus: true, baik: 'naik', ambil: (X) => X.kotor, ket: 'sebelum potongan nota, tawar & retur' },
  { id: 'potongan', nama: 'Potongan & tawar', satuan: 'pct', baik: 'turun', tg: 'potonganPct', ambil: (X) => X.potPct, rp: (X) => X.potongan, ket: 'potongan nota + tawar di bawah harga daftar ÷ penjualan kotor' },
  { id: 'omzet', nama: 'Penjualan bersih (omzet)', satuan: 'rp', arus: true, baik: 'naik', tg: 'omzet', ambil: (X) => X.omzet, ket: 'omzet mesin = kotor − potongan − retur' },
  { id: 'kgTerjual', nama: 'Kg terjual', satuan: 'kg', arus: true, baik: 'naik', tg: 'kgTerjual', ambil: (X) => X.kg, ket: 'kg semua nota ber-kg' },
  { id: 'hppKg', nama: 'HPP rata-rata per kg', satuan: 'rpkg', baik: 'turun', tg: 'hppKg', ambil: (X) => X.hppKg, ket: 'HPP mesin ÷ kg nota ber-HPP' },
  { id: 'labaKotor', nama: 'Laba kotor', satuan: 'rp', arus: true, baik: 'naik', tg: 'labaKotor', ambil: (X) => X.labaKotor, ket: 'omzet ber-HPP − HPP' },
  { id: 'marginKotor', nama: 'Margin laba kotor', satuan: 'pct', baik: 'naik', tg: 'marginKotor', ambil: (X) => X.marginKotor, ket: 'laba kotor ÷ omzet ber-HPP' },
  { id: 'labaBersih', nama: 'Laba bersih', satuan: 'rp', arus: true, baik: 'naik', tg: 'labaBersih', ambil: (X) => X.labaBersih, sampai: (X) => X.labaSampai, ket: 'mesin laba · bulan berjalan: target dibanding laba bersih sampai hari ini' },
  { id: 'marginBersih', nama: 'Margin laba bersih', satuan: 'pct', baik: 'naik', ambil: (X) => X.marginBersih, ket: 'laba bersih ÷ omzet ber-HPP' },
  { id: 'susutPct', nama: 'Susut beras', satuan: 'pct', baik: 'turun', ambil: (X) => X.susutPct, ket: 'kg hilang ÷ beras keluar (Per merek) · target = target susut owner' },
  { id: 'piutangAkhir', nama: 'Piutang akhir bulan', satuan: 'rp', baik: 'turun', tg: 'piutangAkhir', ambil: (X) => X.piutang, ket: 'sisa bon pelanggan (bulan berjalan: hari ini)' },
  { id: 'dso', nama: 'Hari bon pelanggan', satuan: 'hari', baik: 'turun', ambil: (X) => X.dso, ket: 'piutang akhir bulan ÷ jual bon per hari BULAN KALENDER itu (bukan jendela 30 hari bergulir)' },
  { id: 'perputaran', nama: 'Perputaran stok', satuan: 'kali', baik: 'naik', ambil: (X) => X.perputaran, ket: 'HPP bulan itu ÷ rata-rata nilai stok (karung + kemasan) — sebulan, tidak disetahunkan' },
  { id: 'hariStok', nama: 'Hari stok', satuan: 'hari', baik: 'turun', ambil: (X) => X.hariStok, ket: 'rata-rata nilai stok ÷ HPP per hari' },
];
/** Baris mode KAS (saklar Kas | Laba, owner 27 Nov 2026 "Dua-duanya"). */
const RB_BARIS_KAS = [
  { id: 'masuk', nama: 'Uang masuk', satuan: 'rp', arus: true, baik: 'naik', ambil: (X) => X.masuk, ket: 'tunai · QRIS · transfer · bayar bon · uang masuk lain (arus kas mesin)' },
  { id: 'keluar', nama: 'Uang keluar', satuan: 'rp', arus: true, baik: 'turun', ambil: (X) => X.keluar, ket: 'belanja beras, bayar pemasok, biaya, tagihan, ambil pribadi (arus kas mesin)' },
  { id: 'kasBersih', nama: 'Kas bersih', satuan: 'rp', arus: true, baik: 'naik', ambil: (X) => X.kasBersih, ket: 'uang masuk − uang keluar' },
  { id: 'bon', nama: 'Jual bon (belum jadi uang)', satuan: 'rp', arus: true, baik: 'turun', ambil: (X) => X.bon, ket: 'ikut omzet & laba, belum masuk laci' },
  { id: 'labaBersihKas', nama: 'Laba bersih (pembanding)', satuan: 'rp', arus: true, baik: 'naik', ambil: (X) => X.labaBersih, ket: 'beda dengan kas bersih = bon baru, bayar bon lama, belanja stok, ambil pribadi' },
];
function rbSusunBaris(daftar, X, XL, TB, ambang, catatan, ST) {
  const ctx = { berjalan: X.berjalan, hariJalan: X.hariJalan, nHari: X.nHari };
  return daftar.map((b) => {
    const ini = b.ambil(X), lalu = b.ambil(XL); const pembanding = b.arus && X.berjalan ? rbSebulan(X, ini) : ini; const ubah = rbUbah(pembanding, lalu);
    const t = b.tg ? AB_TARGET.find((x) => x.id === b.tg) : null; const tb = b.tg && TB[b.tg] ? TB[b.tg] : null;
    let L = { lampu: 'tanpa', dasar: null, selisih: null, pct: null }, target = null, targetTeks = ''; const aktual = b.sampai && X.berjalan ? b.sampai(X) : ini;   // laba bersih bulan berjalan: yang dibanding = sampai hari ini
    if (t && tb && tb.nilai > 0) { L = kbLampuTarget(t, tb.nilai, aktual, ctx, ambang); target = tb.nilai;
      targetTeks = (t.arah === 'min' ? 'target ' : 'batas ') + rbNilaiTeks(tb.nilai, b.satuan) + (t.jalan && X.berjalan ? ' · sampai hari ke-' + X.hariJalan + ' ' + rbNilaiTeks(L.dasar, b.satuan) : '') + (b.sampai && X.berjalan ? ' · tercapai sampai hari ini ' + rbNilaiTeks(aktual, b.satuan) : '') + (tb.khusus ? ' · angka khusus ' + X.nama : ''); }
    else if (b.id === 'susutPct' && ST && ST.pct !== null && ST.pct !== undefined) {   // target susut = setelan susut yang sudah ada (shTarget), lampu dengan ambang yang sama
      target = ST.pct; L = kbLampuTarget({ arah: 'maks', jalan: false }, ST.pct, ini, ctx, ambang); targetTeks = 'target susut ' + klPctTeks(ST.pct) + (ST.dariOwner ? '' : ' (terukur, bukan angka owner)'); }
    const membaik = ubah === null ? null : b.baik === 'naik' ? ubah > 0 : ubah < 0;
    const c = catatan[b.id] || null;
    return { id: b.id, nama: b.nama, satuan: b.satuan, ket: b.ket, ini, lalu, pembanding, perkiraan: b.arus && X.berjalan, ubah, ubahTeks: rbUbahTeks(ubah), membaik, baik: b.baik,
      iniTeks: rbNilaiTeks(ini, b.satuan), laluTeks: rbNilaiTeks(lalu, b.satuan), perkiraanTeks: b.arus && X.berjalan ? rbNilaiTeks(pembanding, b.satuan) : '', rpTeks: b.rp ? rbNilaiTeks(b.rp(X), 'rp') : '',
      tgId: b.tg || (b.id === 'susutPct' ? 'susutPct' : ''), target, targetTeks, lampu: L.lampu, lampuKata: rbKataLampu(t ? t.arah : 'maks', L.lampu), dasar: L.dasar, selisih: L.selisih, aktual, aktualTeks: rbNilaiTeks(aktual, b.satuan), catatan: c };
  });
}
/**
 * LEMBAR KPI BULANAN / SCORECARD (A136, B112): bulan `key` vs bulan sebelumnya vs target owner. mode 'laba' (bawaan) atau 'kas' (saklar). Bulan berjalan: arus
 * dibanding lewat perkiraan sebulan; sekarang-saja (siklus uang, karcis) ikut di `sekarang`. → { key, nama, namaLalu, baris, sekarang, hitung lampu, kalimat }.
 */
export function rbRapor(key, kini, mode) {
  const X = rbBulan(key, kini), XL = rbBulan(rbGeser(String(key), -1), kini); const TB = targetBulan(key); const ambang = X.K.A.ambang; const catatan = catatanPos(key);
  let ST = null; try { ST = shTarget(kini); } catch (e) { ST = null; }
  const baris = rbSusunBaris(mode === 'kas' ? RB_BARIS_KAS : RB_BARIS, X, XL, TB, ambang, catatan, ST);
  const sekarang = []; const kiniBulan = key === hariIniIso(kini).slice(0, 7);
  if (kiniBulan && mode !== 'kas') {   // posisi sekarang (karcis, siklus uang) hanya di mode Laba — mode Kas menghitung lampunya sendiri
    let KC = null; try { KC = daftarKarcis(kini); } catch (e) { KC = null; }
    const t = AB_TARGET.find((x) => x.id === 'karcisBelum'); const tb = TB.karcisBelum; const L = KC && tb.nilai > 0 ? kbLampuTarget(t, tb.nilai, KC.nKarcis, null, ambang) : { lampu: 'tanpa' };
    sekarang.push({ id: 'karcisBelum', tgId: 'karcisBelum', satuan: 'n', lampuKata: rbKataLampu('maks', L.lampu), dasar: L.dasar === undefined ? null : L.dasar, selisih: L.selisih === undefined ? null : L.selisih, nama: 'Karcis kasir belum dirinci', iniTeks: KC ? KC.nKarcis + ' karcis' + (KC.nKarcis ? ' · ' + RP(KC.total) : '') : '—', ini: KC ? KC.nKarcis : null, lampu: L.lampu, target: tb.nilai || null,
      targetTeks: tb.nilai > 0 ? 'batas ' + tb.nilai + ' karcis' : '', catatan: catatan.karcisBelum || null, tujuan: { ke: 'jual', lembar: 'karcis' } });
    let SU = null; try { SU = klSiklusUang(kini); } catch (e) { SU = null; }
    if (SU) sekarang.push({ id: 'siklus', nama: 'Siklus uang', iniTeks: SU.hari === null ? 'belum bisa dihitung' : (SU.hari < 0 ? '−' : '±') + DESIMAL(Math.round(Math.abs(SU.hari) * 10) / 10) + ' hari', ini: SU.hari, lampu: 'tanpa', target: null, targetTeks: '', ket: SU.kalimat, catatan: null, tujuan: { ke: 'stok', tab: 'umur' } });
  }
  const semua = baris.concat(sekarang); const hitung = (w) => semua.filter((b) => b.lampu === w).length;
  return { key, nama: X.nama, pendek: X.pendek, namaLalu: XL.nama, pendekLalu: XL.pendek, mode: mode === 'kas' ? 'kas' : 'laba', berjalan: X.berjalan, hariJalan: X.hariJalan, nHari: X.nHari, diarsip: X.diarsip, diarsipLalu: XL.diarsip,
    tanpaCatatan: X.tanpaCatatan, baris, sekarang, merah: hitung('merah'), amber: hitung('amber'), hijau: hitung('hijau'), nTarget: semua.filter((b) => b.lampu !== 'tanpa').length, ambang, X, XL,
    sumber: 'Laporan › Bulanan', tujuan: { ke: 'laporan', keluarga: 'bulanan', bulan: key },
    kalimat: X.tanpaCatatan ? 'Belum ada catatan ' + X.nama + '.' : (X.berjalan ? 'Hari ke-' + X.hariJalan + ' dari ' + X.nHari + ' — angka yang menumpuk dibanding ' + XL.nama + ' lewat perkiraan sebulan (linear). ' : '')
      + (semua.some((b) => b.lampu !== 'tanpa') ? hitung('merah') + ' merah · ' + hitung('amber') + ' mendekati · ' + hitung('hijau') + ' aman.' : 'Target bulanan belum diatur — Laporan › Biaya › Atur.') };
}

// ---------- anggaran vs aktual SEMUA pos + sebab & tindakan (A110) ----------
/** Tabel anggaran vs aktual satu bulan: biaya per jenis (Peta biaya), hapus buku & susut, PPh final, lalu semua pos target. Tiap baris membawa sebab & tindakan owner. */
export function rbAnggaranAktual(key, kini) {
  const R = rbRapor(key, kini); const K = R.X.K; const catatan = catatanPos(key); const out = [];
  K.baris.forEach((r) => { if (r.id === 'lain' && !(r.n > 0.5) && !(r.anggaran > 0)) return;
    out.push({ id: r.id, kel: 'biaya', nama: r.nama, anggaran: r.anggaran > 0 ? r.anggaran : null, dasar: r.dasar, aktual: r.pakai, aktualTeks: RP(r.pakai), anggaranTeks: r.anggaran > 0 ? RP(r.anggaran) : 'belum diatur',
      selisih: r.selisih, selisihTeks: r.selisih === null ? '—' : (r.selisih > 0 ? 'lewat ' : 'sisa ') + RP(Math.abs(r.selisih)), lampu: r.lampu, ket: r.lampuTeks, khusus: !!r.khusus, catatan: catatan[r.id] || null }); });
  let PP = null; try { PP = klPph(K, kini); } catch (e) { PP = null; }
  if (PP) out.push({ id: 'pph', kel: 'pajak', nama: 'PPh final (perkiraan)', anggaran: PP.anggaran > 0 ? PP.anggaran : null, dasar: PP.dasar, aktual: PP.n, aktualTeks: PP.n === null ? 'belum bisa' : RP(PP.n), anggaranTeks: PP.anggaran > 0 ? RP(PP.anggaran) : 'belum diatur',
    selisih: PP.selisih, selisihTeks: PP.selisih === null ? '—' : (PP.selisih > 0 ? 'lewat ' : 'sisa ') + RP(Math.abs(PP.selisih)), lampu: PP.lampu, ket: PP.lampuTeks + ' · pos sisihan', khusus: !!(K.A.khusus && K.A.khusus.pph), catatan: catatan.pph || null });
  R.baris.concat(R.sekarang).filter((b) => b.tgId).forEach((b) => {
    out.push({ id: b.tgId, kel: 'target', nama: b.nama, anggaran: b.target, dasar: b.dasar, aktual: b.aktual === undefined ? b.ini : b.aktual, aktualTeks: b.aktualTeks || b.iniTeks, anggaranTeks: b.target ? b.targetTeks : 'belum diatur',
      selisih: b.selisih === undefined ? null : b.selisih, selisihTeks: b.selisih === null || b.selisih === undefined ? '—' : (b.selisih > 0 ? '+' : '−') + (b.satuan === 'pct' ? klPctTeks(Math.abs(b.selisih)).replace(' %', ' poin') : rbNilaiTeks(Math.abs(b.selisih), b.satuan)), lampu: b.lampu, ket: b.ket || '', khusus: /angka khusus/.test(b.targetTeks || ''), catatan: b.catatan || null }); });
  const nCat = out.filter((r) => r.catatan).length; const awas = out.filter((r) => r.lampu === 'merah' || r.lampu === 'amber');
  return { key, nama: R.nama, berjalan: R.berjalan, hariJalan: R.hariJalan, nHari: R.nHari, baris: out, nCatatan: nCat, awas: awas.length, tanpaSebab: awas.filter((r) => !r.catatan).length, ambang: R.ambang,
    kalimat: (awas.length ? awas.length + ' pos lewat / mendekati' + (awas.filter((r) => !r.catatan).length ? ' — ' + awas.filter((r) => !r.catatan).length + ' belum diberi sebab & tindakan' : ' — semuanya sudah diberi sebab & tindakan') : 'Tidak ada pos yang lewat atau mendekati batas.') };
}

// ---------- pecahan selisih laba kotor (A111) ----------
/**
 * Laba kotor aktual − anggaran laba kotor, dipecah TIGA (Σ = selisihnya PERSIS) + susut di bawahnya:
 *   anggaran: kg_b = target kg (bulan berjalan: × hari jalan ÷ hari bulan) · HPP_b = batas HPP/kg · jual_b = HPP_b ÷ (1 − target margin %) → laba kotor_b = kg_b × (jual_b − HPP_b)
 *   aktual  : kg_a = kg nota ber-HPP · jual_a = omzet ber-HPP ÷ kg_a · HPP_a = HPP ÷ kg_a → laba kotor_a = laba kotor mesin
 *   VOLUME     = (kg_a − kg_b) × (jual_b − HPP_b)       — lebih / kurang kg terjual
 *   HARGA JUAL = kg_a × (jual_a − jual_b)               — dijual lebih mahal / murah dari harga yang dianggarkan
 *   HARGA BELI = kg_a × (HPP_b − HPP_a)                 — modal per kg lebih murah (+) / mahal (−) dari batas
 *   KUANTITAS (susut) = anggaran susut (Peta biaya) − susut & selisih stok — di bawah laba kotor, tidak ikut Σ di atas.
 * Butuh tiga target (kg terjual, HPP/kg, margin kotor %); yang belum diisi DISEBUT.
 */
export function rbPecahSelisih(key, kini) {
  const X = rbBulan(key, kini); const TB = targetBulan(key); const kurang = []; const K = X.K;
  ['kgTerjual', 'hppKg', 'marginKotor'].forEach((id) => { if (!(TB[id].nilai > 0)) kurang.push(AB_TARGET.find((t) => t.id === id).nama.toLowerCase()); });
  if (TB.marginKotor.nilai >= 100) kurang.push('margin kotor di bawah 100 %');
  const rS = K.baris.find((r) => r.id === 'susut') || null; const susut = rS && rS.anggaran > 0 ? { anggaran: rS.dasar, aktual: rS.pakai, selisih: rS.dasar - rS.pakai } : null;
  if (kurang.length) return { key, nama: X.nama, ada: false, kurang, susut, kalimat: 'Pecahan selisih butuh target ' + kurang.join(', ') + ' — isi di Laporan › Biaya › Atur.' };
  const kgB = X.berjalan ? TB.kgTerjual.nilai * X.hariJalan / X.nHari : TB.kgTerjual.nilai; const hB = TB.hppKg.nilai; const jB = hB / (1 - TB.marginKotor.nilai / 100); const mB = jB - hB;
  const kgA = X.kgHitung; const lkB = kgB * mB; const lkA = X.labaKotor;
  if (!(kgA > 0)) return { key, nama: X.nama, ada: false, kurang: [], susut, anggaran: lkB, kalimat: 'Belum ada nota ber-modal ' + X.nama + ' — laba kotor aktual belum bisa dipecah.' };
  const jA = X.omzetHitung / kgA, hA = X.hpp / kgA;
  const volume = (kgA - kgB) * mB, hargaJual = kgA * (jA - jB), hargaBeli = kgA * (hB - hA); const selisih = lkA - lkB; const sisa = selisih - (volume + hargaJual + hargaBeli);
  const bagian = [{ id: 'volume', nama: 'Volume (kg terjual)', n: volume, ket: ANGKA(Math.round(kgA)) + ' kg vs anggaran ' + ANGKA(Math.round(kgB)) + ' kg × laba kotor anggaran ' + RP(Math.round(mB)) + '/kg' },
    { id: 'hargaJual', nama: 'Harga jual', n: hargaJual, ket: 'jual ' + RP(Math.round(jA)) + '/kg vs anggaran ' + RP(Math.round(jB)) + '/kg (dari batas HPP & target margin)' },
    { id: 'hargaBeli', nama: 'Harga beli (modal)', n: hargaBeli, ket: 'HPP ' + RP(Math.round(hA)) + '/kg vs batas ' + RP(Math.round(hB)) + '/kg' }];
  return { key, nama: X.nama, ada: true, berjalan: X.berjalan, anggaran: lkB, aktual: lkA, selisih, bagian, sisa, menutup: Math.abs(sisa) < 0.5, susut,
    dasar: { kgB, hB, jB, mB, kgA, jA, hA, margin: TB.marginKotor.nilai, kgTanpaModal: Math.max(0, X.kg - kgA) },
    kalimat: 'Laba kotor ' + RP(Math.round(lkA)) + ' vs anggaran ' + RP(Math.round(lkB)) + (X.berjalan ? ' (jatah sampai hari ke-' + X.hariJalan + ')' : '') + ' = ' + (selisih >= 0 ? 'lebih ' : 'kurang ') + RP(Math.abs(Math.round(selisih)))
      + ': volume ' + rbTanda(volume) + ' · harga jual ' + rbTanda(hargaJual) + ' · harga beli ' + rbTanda(hargaBeli) + '.' + (X.kg - kgA > 0.5 ? ' ' + ANGKA(Math.round(X.kg - kgA)) + ' kg nota tanpa modal tidak ikut (belum dirinci).' : '') };
}
const rbTanda = (n) => (n >= 0 ? '+' : '−') + RP(Math.abs(Math.round(n)));

// ---------- penjualan kotor vs bersih + potongan per hari (B4) ----------
/** Bulan `key`: kotor → potongan nota → tawar → retur → bersih (= omzet mesin), dan per hari (Σ hari = bulan). Bulan yang ditutup buku: per hari ikut arsip. */
export function rbKotorBersih(key, kini) { const iso = hariIniIso(kini); return ingatPerVersi('rbKotorBersih|' + key + '|' + iso, () => rbKotorBersihHitung(String(key), kini, iso)); }
function rbKotorBersihHitung(key, kini, iso) {
  const X = rbBulan(key, kini); const PH = pjPotonganHarian(key); const hari = [];
  const HB = X.diarsip ? {} : lpHariBulan(key);   // satu lintasan per bulan (rekap hari & hariTerakhir memakai aturan yang sama) — bukan mesin laba 30×
  if (!X.diarsip) { let t = X.awal; while (t <= X.sampai) { const R = HB[t] || { omzet: 0, retur: 0, nota: 0 }; const P = PH.hari[t] || { nota: 0, tawar: 0, jumlah: 0, n: 0 }; const bersih = R.omzet; const retur = R.retur || 0;
    if (R.nota || retur || P.jumlah) hari.push({ iso: t, kotor: bersih + retur + P.jumlah, potNota: P.nota, potTawar: P.tawar, potongan: P.jumlah, nPotongan: P.n, retur, bersih, nota: R.nota }); t = ugTambahHari(t, 1); } }
  const jml = (f) => hari.reduce((a, h) => a + h[f], 0);
  const menutup = X.diarsip ? null : Math.abs(jml('bersih') - X.omzet) < 0.5 && Math.abs(jml('potongan') - X.potongan) < 0.5 && Math.abs(jml('retur') - (X.retur || 0)) < 0.5;
  const maksPot = hari.reduce((m, h) => (h.potongan > (m ? m.potongan : 0) ? h : m), null);
  return { key, nama: X.nama, berjalan: X.berjalan, diarsip: X.diarsip, kotor: X.kotor, potNota: X.potNota, potTawar: X.potTawar, potongan: X.potongan, nPotongan: X.nPotongan, retur: X.retur, bersih: X.omzet, potPct: X.potPct,
    hari: hari.slice().reverse(), menutup, terbesar: maksPot,
    tangga: [{ nama: 'Penjualan kotor', n: X.kotor, kelas: 'jumlah', ket: 'harga daftar sebelum potongan, tawar & retur' }, { nama: 'Potongan nota', n: -X.potNota, ket: 'potongan di nota' }, { nama: 'Tawar di bawah harga daftar', n: -X.potTawar, ket: 'dari harga asli satuan' }, { nama: 'Retur', n: X.retur === null ? null : -X.retur, ket: 'uang / bon dikembalikan' }, { nama: 'Penjualan bersih (omzet)', n: X.omzet, kelas: 'jumlah', ket: 'mesin laba — sama dengan Laba & Bulanan' }],
    kalimat: X.diarsip ? X.nama + ' sudah ditutup buku — jumlah sebulan dari potret, per hari ikut arsip.' : menutup === false ? 'Per hari TIDAK MENUTUP ke angka bulan — laporkan.' : X.potongan > 0 ? 'Potongan & tawar ' + RP(X.potongan) + ' (' + klPctTeks(X.potPct) + ' dari penjualan kotor) di ' + X.nPotongan + ' baris' + (maksPot ? '; terbesar ' + tanggalPendek(maksPot.iso) + ' ' + RP(maksPot.potongan) : '') + '.' : 'Tidak ada potongan maupun tawar di bawah harga daftar ' + X.nama + '.' };
}

// ---------- arus kas bulan ini (B26) ----------
/** Uang masuk / keluar / kas bersih bulan `key` vs bulan lalu (intiBulan) + rincian per pos (hitungArusKasInti) + kenapa beda dengan laba bersih. */
export function rbArusKas(key, kini) {
  const X = rbBulan(key, kini), XL = rbBulan(rbGeser(String(key), -1), kini); let masuk = [], keluar = [];
  if (!X.diarsip) { const K = hitungArusKasInti((t) => !!t && t >= X.awal && t <= X.sampai, ugBayaran()); masuk = (K.masuk || []).filter((r) => Math.abs(r.nominal) > 0.5).map((r) => ({ nama: r.label, n: r.nominal, jumlah: r.n }));
    keluar = (K.keluar || []).filter((r) => Math.abs(r.nominal) > 0.5).map((r) => ({ nama: r.label, n: r.nominal, jumlah: r.n })); }
  const beda = X.kasBersih === null || X.labaBersih === null ? null : X.kasBersih - X.labaBersih;
  return { key, nama: X.nama, namaLalu: XL.nama, berjalan: X.berjalan, diarsip: X.diarsip, masuk: X.masuk, keluar: X.keluar, bersih: X.kasBersih, laluMasuk: XL.masuk, laluKeluar: XL.keluar, laluBersih: XL.kasBersih,
    ubahBersih: rbUbah(X.kasBersih, XL.kasBersih), bon: X.bon, labaBersih: X.labaBersih, beda, rinciMasuk: masuk, rinciKeluar: keluar, sumber: 'Laporan › Bulanan', tujuan: { ke: 'laporan', keluarga: 'bulanan', bulan: key },
    kalimat: 'Uang masuk ' + RP(X.masuk) + ' − keluar ' + RP(X.keluar) + ' = kas bersih ' + RP(X.kasBersih) + (beda === null ? '' : ' · laba bersih ' + RP(X.labaBersih) + ' (beda ' + (beda >= 0 ? '+' : '−') + RP(Math.abs(beda)) + ': bon baru, bayar bon lama, belanja stok, ambil pribadi)') + '.' };
}

// ---------- ambang berwarna untuk kartu lama Dasbor (B110 B124) ----------
/**
 * Lampu target owner untuk angka yang sudah tampil di Dasbor: margin kotor % bulan (kartu Margin & target), piutang (kartu Piutang), karcis belum dirinci (kartu Hari ini),
 * laba kotor hari ini (kartu Hari ini; target per hari = target laba kotor sebulan ÷ jumlah hari bulan itu, laju jam toko seperti target omzet harian). Tanpa target = tidak ada.
 */
export function rbAmbangDasbor(R, kini, bagianHari, labaHari, piutangSekarang, karcisN) {
  const TB = targetBulan(R.key); const ambang = R.ambang; const out = {}; const bMargin = R.baris.find((b) => b.id === 'marginKotor');
  if (bMargin && bMargin.lampu !== 'tanpa') out.margin = { lampu: bMargin.lampu, teks: 'margin kotor ' + bMargin.iniTeks + ' · ' + bMargin.targetTeks };
  const tP = AB_TARGET.find((t) => t.id === 'piutangAkhir'); if (TB.piutangAkhir.nilai > 0 && piutangSekarang !== null && piutangSekarang !== undefined) { const L = kbLampuTarget(tP, TB.piutangAkhir.nilai, piutangSekarang, null, ambang); out.piutang = { lampu: L.lampu, teks: 'piutang ' + RP(piutangSekarang) + ' · batas akhir bulan ' + RP(TB.piutangAkhir.nilai) }; }
  const tK = AB_TARGET.find((t) => t.id === 'karcisBelum'); if (TB.karcisBelum.nilai > 0 && karcisN !== null && karcisN !== undefined) { const L = kbLampuTarget(tK, TB.karcisBelum.nilai, karcisN, null, ambang); out.karcis = { lampu: L.lampu, teks: karcisN + ' karcis belum dirinci · batas ' + TB.karcisBelum.nilai }; }
  if (TB.labaKotor.nilai > 0 && labaHari !== null && labaHari !== undefined && R.key === hariIniIso(kini).slice(0, 7)) { const harian = TB.labaKotor.nilai / R.nHari; const laju = harian * Math.max(0, Math.min(1, bagianHari));
    const lampu = labaHari >= harian ? 'hijau' : labaHari >= laju ? 'amber' : 'merah'; out.labaHari = { lampu, target: harian, laju, teks: lampu === 'hijau' ? 'target laba kotor hari ini ' + RP(Math.round(harian)) + ' tercapai' : lampu === 'amber' ? 'sesuai laju jam: seharusnya ±' + RP(Math.round(laju)) + ' dari ' + RP(Math.round(harian)) : 'di bawah laju jam: seharusnya sudah ±' + RP(Math.round(laju)) + ' dari ' + RP(Math.round(harian)) }; }
  return out;
}

// ---------- acuan terukur untuk formulir target (A109) ----------
/** Isi target umum di FORMULIR dari acuan terukur = median ≤ 3 bulan selesai sebelum `key` yang punya catatan (cara yang sama dengan acuan anggaran biaya). Hanya
 *  pos yang belum diketik owner. Mengisi draf, BUKAN menyimpan — yang menjadi target tetap yang owner simpan. Karcis belum dirinci tidak punya acuan (posisi sekarang). */
export function rbDrafAcuanTarget(key, kini, draf) {
  const d = Object.assign({}, draf || {}); const tg = Object.assign({}, d.target || {}); let n = 0;
  const bulan = daftarBulan(kini, 36).map((b) => b.key).filter((k) => k < String(key)).slice(0, 3).map((k) => rbBulan(k, kini)).filter((X) => !X.tanpaCatatan && !X.berjalan);
  const AMBIL = { omzet: (X) => X.omzet, kgTerjual: (X) => X.kg, labaKotor: (X) => X.labaKotor, marginKotor: (X) => X.marginKotor, labaBersih: (X) => X.labaBersih, hppKg: (X) => X.hppKg, piutangAkhir: (X) => X.piutang, potonganPct: (X) => X.potPct };
  const BULAT = { rp: (v) => Math.round(v / 1000) * 1000, kg: (v) => Math.round(v / 10) * 10, rpkg: (v) => Math.round(v / 10) * 10, pct: (v) => Math.round(v * 10) / 10 };
  AB_TARGET.forEach((t) => { const f = AMBIL[t.id]; if (!f || String(tg[t.id] || '').trim()) return; const arr = bulan.map(f).filter((v) => v !== null && v !== undefined && isFinite(v) && v > 0).sort((a, b) => a - b); if (!arr.length) return;
    const m = arr.length % 2 ? arr[(arr.length - 1) / 2] : (arr[arr.length / 2 - 1] + arr[arr.length / 2]) / 2; const v = BULAT[t.satuan](m); if (!(v > 0)) return; tg[t.id] = abTeks(v, t.satuan); n += 1; });
  d.target = tg; return { draf: d, n, bulan: bulan.map((X) => X.key) };
}
