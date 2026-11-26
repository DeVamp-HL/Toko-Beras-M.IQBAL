// BANDING PEMASOK — HITUNGAN (owner 26 Nov 2026, sensus ulang bagian 1c: A6 · A95 · A129 · A137 · A19). Logika tanpa DOM, awalan bd (bundel uji jsc
// satu lingkup). Hanya MEMBACA; satu-satunya tulisan paket ini ada di banding-catat-logika.js (setelan & catatan tawaran / acuan, aturanToko).
// Dijaga alat-uji/uji_banding_pemasok.py (kotak pasir + --kontrol + asap cadangan toko).
//
// RUMUS (tidak ada rumus uang baru — tiap bagian membaca fungsi sumbernya apa adanya):
//  · MODAL SAMPAI TOKO per kg satu baris kedatangan (A6) = (nilai baris + porsi bongkar & ongkos kirim) ÷ kg yang SUNGGUH diterima.
//      nilai baris & porsi bongkar = mesin hitungHppMerkDalamBatch (yang juga dipakai modal stok) — klaim & retur sudah memotong nilai barisnya.
//      kg diterima: baris ikut timbang (Tahap 6, kgTerima) = kg bukunya; baris lama yang ditimbang / ditimbang sampel = hasil timbang − kg yang
//      dikembalikan (tmBaris, rumus timbang Barang masuk); baris belum ditimbang = kg nota (DISEBUT "belum ditimbang", bukan dianggap pas).
//      Dipecah per kg: harga nota + bongkar & ongkir + selisih timbang — tiga bagian MENUTUP ke modalnya (bagian terakhir = sisa pembulatan).
//  · LAYAK JUAL per kg (A95, keputusan owner "plus susut gudang dan plus potongan mutu Rp") = (modal + potongan mutu) ÷ (kg diterima × (1 − susut gudang %)).
//      potongan mutu = Rp/kg setelan owner untuk tiap tanda AWAS baris itu (tmBaris.tanda) × kg diterima; susut gudang % = susut per pemasok 3 bulan
//      (shSusutPemasok, Laporan › Susut — susut kg ÷ kg datang dari pemasok itu). Susut belum terukur = 0 % dan DISEBUT.
//  · HARGA TAWARAN (belum dibeli) = PERKIRAAN: harga + ongkos kirim yang disebut pemasok (tidak disebut → rata-rata ongkos kirim toko) + rata-rata upah
//      bongkar toko per kg, layak jual memakai susut rata-rata toko; mutu belum diketahui. Selalu ditandai perkiraan di urutan.
//  · Banding per KELAS (hetUnit: kelas yang dikonfirmasi owner, selain itu merek itu sendiri) — cadangan 25 Nov: 16 kelas, cuma 5 dipasok dua pemasok.
// PENJAGA: Σ (modal baris + bagian yang dilewati: baris bal & baris tanpa kg) per bulan = Σ nilai kedatangan bulan itu menurut sapuan Bon pemasok
// (daftarPemasok, bon-pemasok-logika) — dua jalan baca yang berbeda; selisih = TIDAK MENUTUP dan disebut.
import { hitungHppMerkDalamBatch } from '../mesin/beku.js';
import { kunciPelanggan } from '../mesin/pembantu.js';
import { ambilSemuaBatch, ingatPerVersi } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { tmBaris, aturCatat, cpBaca, rekapTimbangMutu } from './stok-catat-logika.js';
import { hetUnit, hetAtur } from './het-logika.js';
import { shSusutPemasok, SH_TANPA_KEDATANGAN } from './susut-harga-logika.js';
import { daftarPemasok, bpLamaKirim, bpHariTeks } from './bon-pemasok-logika.js';
import { bcAtur, bcEntri, bcSenin, bcTambahHari, bcBulanGeser, bcPemasokSungguhan, bcDibanding, bcTarik, bcTeks, BC_TANDA, BC_TINGKAT } from './banding-catat-logika.js';

export const BD_TAB = [['minggu', 'Minggu ini'], ['bulan', 'Banding bulan'], ['rapor', 'Rapor pemasok'], ['acuan', 'Harga acuan'], ['tren', 'Tren modal']];
export const BD_BULAN_SUSUT = 3;   // susut gudang per pemasok = 3 bulan (sama dengan target susut terukur #214)
export const BD_TREN = 6;
export const BD_RUMUS = {
  modal: 'Modal sampai toko per kg = (nilai baris dari pemasok + bongkar & ongkos kirim) ÷ kg yang sungguh diterima (hasil timbang; belum ditimbang = kg nota)',
  layak: 'Layak jual per kg = (modal sampai toko + potongan mutu) ÷ (kg diterima × (1 − susut gudang pemasok itu, 3 bulan))',
  tawaran: 'Harga tawaran = perkiraan: harga + ongkos kirim yang disebut (atau rata-rata toko) + upah bongkar rata-rata toko; susut = rata-rata toko; mutu belum diketahui',
};
const bdB = (n) => Math.round(n * 100) / 100;
const bdD = (n) => (n < 0 ? '−' : '') + String(Math.round(Math.abs(n) * 10) / 10).replace('.', ',');
const bdKini = (k) => k || new Date();
const bdNamaBulan = (key) => { const B = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']; return B[Number(String(key).slice(5, 7)) - 1] + ' ' + String(key).slice(0, 4); };
const bdAkhirBulan = (key) => bcTambahHari(bcBulanGeser(key, 1) + '-01', -1);
/** Rentang satu bulan, dipotong di hari ini untuk bulan berjalan. */
export function bdRentangBulan(key, kini) { const iso = hariIniIso(bdKini(kini)); const akhir = bdAkhirBulan(key); return { awal: key + '-01', akhir: akhir > iso ? iso : akhir, berjalan: akhir >= iso && key <= iso.slice(0, 7) }; }
/** Rentang susut gudang: awal bulan ke-3 dari belakang s.d. akhir rentang. */
const bdRentangSusut = (akhir) => ({ awal: bcBulanGeser(String(akhir).slice(0, 7), -(BD_BULAN_SUSUT - 1)) + '-01', akhir });
const bdPct = (v) => (v === null || v === undefined || !isFinite(v) ? '—' : bdD(v) + ' %');
/** Tiga angka bulat yang menutup: a + b + sisa = total (sisa = total − a − b). */
const bdTutup = (total, a, b) => { const T = Math.round(total), A = Math.round(a), B = Math.round(b); return [A, B, T - A - B, T]; };

// ==================== BARIS KEDATANGAN ====================
/** kg yang dikembalikan ke pemasok dari baris merek ini (jejak potongan retur per baris; baris lama tanpa rincian = 0). */
function bdReturBaris(b, merk) { let kg = 0; (Array.isArray(b.potongan) ? b.potongan : []).forEach((x) => { if (!x || x.jenis !== 'retur' || !Array.isArray(x.baris)) return; x.baris.forEach((r) => { if (r && r.merk === merk) kg += Number(r.kg) || 0; }); }); return kg; }
const bdFondasi = (b) => !b || b.stokAwal || b.tutupBuku || b.lahirBuku || !bcPemasokSungguhan(b.pemasok);
/**
 * Semua baris karung kedatangan nyata bertanggal dari..sampai → { baris, dilewati, nilaiLewat } — satu baris = satu merek satu kedatangan.
 * Baris bal (beli jadi) & baris tanpa kg tidak dibanding (nilainya DIHITUNG di nilaiLewat untuk penjaga).
 */
export function bdBaris(dari, sampai) { return ingatPerVersi('bdBaris|' + dari + '|' + sampai, () => bdBarisHitung(String(dari), String(sampai))); }
function bdBarisHitung(dari, sampai) {
  const A = aturCatat(); const P = bcAtur(); const het = hetAtur(); const baris = []; let dilewati = 0, nilaiLewat = 0;
  ambilSemuaBatch().forEach((b) => { if (bdFondasi(b) || !b.tanggal || b.tanggal < dari || b.tanggal > sampai) return;
    const pemasok = String(b.pemasok).trim(); const kunci = kunciPelanggan(pemasok);
    hitungHppMerkDalamBatch(b.merkList || [], Number(b.biayaBongkar) || 0).forEach((m) => {
      const uang = Number(m.subtotalHarga) || 0; const bongkar = Number(m.alokasiBongkar) || 0;
      if (!m || m.bentuk === 'bal' || !m.merk || !(Number(m.totalKg) > 0) || !(Number(m.hargaPerKg) > 0)) { dilewati += 1; nilaiLewat += uang + bongkar; return; }
      const ikut = Number(m.kgTerima) > 0; const kgPotong = Number(m.kgPotong) > 0 ? Number(m.kgPotong) : 0; const kgBuku = Number(m.totalKg);
      const kgNota = ikut ? bdB((Number(m.jumlahKarung) || 0) * (Number(m.beratKarung) || 0)) : bdB(kgBuku + kgPotong);
      const kgTagih = ikut ? bdB(kgNota - kgPotong) : kgBuku;
      const cek = tmBaris(m, kgNota, Number(m.hargaPerKg), A);
      let kgNyata = kgBuku, asal = 'nota';
      if (ikut) asal = 'timbang';
      else if (cek.timbangKg !== null && !cek.masalah) { kgNyata = bdB(cek.timbangKg - bdReturBaris(b, m.merk)); asal = cek.perkiraan ? 'sampel' : 'timbang'; }
      if (!(kgNyata > 0) || !(kgTagih > 0)) { dilewati += 1; nilaiLewat += uang + bongkar; return; }
      const tanda = (cek.tanda || []).slice(); const potKg = tanda.reduce((a, t) => a + (P.potongMutu[t] || 0), 0);
      const U = hetUnit(m.merk); const kelas = U.unit || m.merk;
      baris.push({ batchId: b.id, tanggal: b.tanggal, pemasok, kunci, merk: m.merk, merkPemasok: String(m.merkPemasok || ''), kelas, het: het.peta[kelas] || '', caraBayar: b.caraBayar || '',
        hargaPerKg: Number(m.hargaPerKg), kgNota, kgTagih, kgBuku, kgNyata, asal, uang, bongkar, modalRp: uang + bongkar, modalKg: (uang + bongkar) / kgNyata,
        kurangKg: bdB(kgTagih - kgNyata), tanda, awas: (cek.awas || []).slice(), dicek: !!cek.dicek, potMutuKg: potKg, potMutuRp: potKg * kgNyata, ongkirBatch: Number(b.ongkosKirim) || 0 }); }); });
  return { baris, dilewati, nilaiLewat, dari, sampai };
}
/** Σ nilai kedatangan (barang + bongkar & ongkir) per bulan menurut sapuan Bon pemasok — pembanding penjaga (jalan baca yang lain). */
function bdNilaiSapuan(dari, sampai) { let n = 0; daftarPemasok().forEach((p) => (p.batch || []).forEach((x) => { if (!x.arsip && x.tanggal >= dari && x.tanggal <= sampai) n += Number(x.nilai) || 0; })); return n; }

// ==================== SUSUT & RATA-RATA TOKO ====================
/** Susut gudang per pemasok (3 bulan s.d. akhir) → { kunci: { pct, susutKg, kgMasuk } } + rata-rata toko (Σ susut ÷ Σ kg datang, kedatangan nyata saja). */
export function bdSusut(akhir) { return ingatPerVersi('bdSusut|' + akhir, () => {
  const R = bdRentangSusut(akhir); let S = null; try { S = shSusutPemasok(R.awal, R.akhir); } catch (e) { S = null; }
  const per = {}; let sk = 0, km = 0;
  if (S) S.pemasok.forEach((p) => { if (p.pemasok === SH_TANPA_KEDATANGAN || p.pemasok.charAt(0) === '(') return; const k = kunciPelanggan(p.pemasok); const o = per[k] || (per[k] = { susutKg: 0, kgMasuk: 0 });
    o.susutKg += p.susutKg || 0; o.kgMasuk += p.kgMasuk || 0; sk += p.susutKg || 0; km += p.kgMasuk || 0; });   // susutKg shSusutPemasok selalu ≥ 0 (naik dicatat terpisah)
  Object.keys(per).forEach((k) => { const o = per[k]; o.pct = o.kgMasuk > 0 && o.susutKg > 0 ? o.susutKg / o.kgMasuk * 100 : null; });
  return { per, rataPct: km > 0 && sk > 0 ? sk / km * 100 : null, awal: R.awal, akhir: R.akhir, ada: !!S, menutup: S ? S.menutup : false };
}); }
/** Rata-rata toko per kg kedatangan dalam rentang: upah bongkar saja & ongkos kirim saja (biayaBongkar = bongkar + ongkir sejak Tahap 1). */
export function bdRataBongkar(dari, sampai) { return ingatPerVersi('bdRataBongkar|' + dari + '|' + sampai, () => {
  let kg = 0, bongkar = 0, ongkir = 0, ganjil = 0;
  ambilSemuaBatch().forEach((b) => { if (bdFondasi(b) || !b.tanggal || b.tanggal < dari || b.tanggal > sampai) return; const k = (b.merkList || []).reduce((a, m) => a + (m && m.bentuk !== 'bal' ? Number(m.totalKg) || 0 : 0), 0); if (!(k > 0)) return;
    const semua = Number(b.biayaBongkar) || 0; const o = Number(b.ongkosKirim) || 0; if (o > semua) ganjil += 1; kg += k; ongkir += o; bongkar += semua - o; });
  // ganjil = kedatangan yang ongkos kirimnya lebih besar dari bongkar+ongkir tersimpan (tidak mungkin lewat layar) — DISEBUT, tidak dipotong
  return { kg, bongkarKg: kg > 0 ? bongkar / kg : 0, ongkirKg: kg > 0 ? ongkir / kg : 0, ganjil, dari, sampai };
}); }

// ==================== KELOMPOK pemasok × kelas ====================
/** Gabungan baris satu pemasok satu kelas → angka per kg (tertimbang kg) + pecahan yang menutup. susut = { pct } pemasok itu atau null. */
function bdKelompok(rs, susut) {
  const s = rs.reduce((a, r) => { a.uang += r.uang; a.bongkar += r.bongkar; a.kgTagih += r.kgTagih; a.kgNyata += r.kgNyata; a.kgNota += r.kgNota; a.pot += r.potMutuRp; a.n += 1; if (r.asal === 'nota') a.belum += 1; if (r.asal === 'sampel') a.sampel += 1; if (r.tanda.length) a.awas += 1; return a; },
    { uang: 0, bongkar: 0, kgTagih: 0, kgNyata: 0, kgNota: 0, pot: 0, n: 0, belum: 0, sampel: 0, awas: 0 });
  const modalKg = (s.uang + s.bongkar) / s.kgNyata; const hargaKg = s.uang / s.kgTagih; const bongkarKg = s.bongkar / s.kgTagih; const T = bdTutup(modalKg, hargaKg, bongkarKg);
  const pct = susut && susut.pct !== null && susut.pct !== undefined ? susut.pct : null; const mutuKg = s.pot / s.kgNyata;
  const layakKg = (s.uang + s.bongkar + s.pot) / (s.kgNyata * (1 - (pct || 0) / 100)); const L = bdTutup(layakKg, T[3], mutuKg);
  return { n: s.n, kgNota: bdB(s.kgNota), kgTagih: bdB(s.kgTagih), kgNyata: bdB(s.kgNyata), uang: s.uang, bongkar: s.bongkar, potMutuRp: s.pot, modalRp: s.uang + s.bongkar,
    hargaKg: T[0], bongkarKg: T[1], timbangKg: T[2], modalKg: T[3], mutuKg: L[1], susutKg: L[2], layakKg: L[3], susutPct: pct, nBelumTimbang: s.belum, nSampel: s.sampel, nAwas: s.awas,
    tanggal: rs.map((r) => r.tanggal).filter((t, i, x) => x.indexOf(t) === i).sort(), hargaNota: rs.map((r) => r.hargaPerKg).filter((t, i, x) => x.indexOf(t) === i).sort((a, b) => a - b) };
}
/** Satu harga tawaran → kelompok PERKIRAAN (bentuk sama dengan bdKelompok). R = rata-rata bongkar toko, rataPct = susut rata-rata toko. */
function bdKelompokTawaran(e, R, rataPct) {
  // ongkos kirim disebut pemasok (termasuk Rp0 yang diketik) / harga sudah sampai toko → dipakai; tidak disebut → rata-rata ongkos kirim toko (ditandai ditebak)
  const tahu = !!e.sampaiToko || e.ongkirDiketahui === true || (e.ongkirDiketahui === undefined && Number(e.ongkirPerKg) > 0);
  const ongkir = e.sampaiToko ? 0 : tahu ? Number(e.ongkirPerKg) || 0 : R.ongkirKg;
  const bongkarKg = R.bongkarKg + ongkir; const modalKg = e.hargaPerKg + bongkarKg; const T = bdTutup(modalKg, e.hargaPerKg, bongkarKg);
  const layakKg = modalKg / (1 - (rataPct || 0) / 100); const L = bdTutup(layakKg, T[3], 0);
  return { n: 0, perkiraan: true, ongkirDitebak: !tahu, hargaKg: T[0], bongkarKg: T[1], timbangKg: T[2], modalKg: T[3],
    mutuKg: 0, susutKg: L[2], layakKg: L[3], susutPct: rataPct, tanggal: [e.tanggal], hargaNota: [e.hargaPerKg], tawaran: e };
}

// ==================== A95 · BANDING BULAN ====================
/**
 * Banding satu bulan: per kelas, tiap pemasok (kedatangan bulan itu) + harga tawaran bulan itu (terbaru per pemasok × kelas), DIURUTKAN dari layak jual
 * termurah. → { key, nama, kelas: [{ kelas, het, kg, baris: [ … urut ] }], pemasok (jumlah pemasok berbeda), min, cukup, menutup, … }.
 */
export function bdBulan(key, kini) { const k = bdKini(kini); return ingatPerVersi('bdBulan|' + key + '|' + hariIniIso(k), () => bdBulanHitung(String(key), k)); }
function bdBulanHitung(key, kini) {
  const Rg = bdRentangBulan(key, kini); const B = bdBaris(Rg.awal, Rg.akhir); const S = bdSusut(Rg.akhir); const A = bcAtur();
  const R = bdRataBongkar(bdRentangSusut(Rg.akhir).awal, Rg.akhir); const per = {};
  B.baris.forEach((r) => { const g = per[r.kelas] || (per[r.kelas] = { kelas: r.kelas, het: r.het, pem: {}, kg: 0 }); (g.pem[r.kunci] = g.pem[r.kunci] || { nama: r.pemasok, rs: [] }).rs.push(r); g.pem[r.kunci].nama = r.pemasok; g.kg += r.kgNyata; });
  const taw = {}; bcEntri(Rg.awal, Rg.akhir).forEach((e) => { if (e.jenis === 'tawaran') taw[kunciPelanggan(e.pemasok) + '|' + e.kelas.toLowerCase()] = e; });   // terbaru menang (urut lama → baru)
  Object.keys(taw).forEach((x) => { const e = taw[x]; const nama = Object.keys(per).find((k) => k.toLowerCase() === e.kelas.toLowerCase()) || e.kelas; const g = per[nama] || (per[nama] = { kelas: nama, het: hetAtur().peta[nama] || '', pem: {}, kg: 0 }); g.tawaran = (g.tawaran || []).concat([e]); });
  const semuaPem = {}; const kelas = Object.keys(per).map((k) => { const g = per[k];
    const baris = Object.keys(g.pem).map((kp) => { semuaPem[kp] = g.pem[kp].nama; return Object.assign({ kunci: kp, pemasok: g.pem[kp].nama, jenis: 'beli' }, bdKelompok(g.pem[kp].rs, S.per[kp] || null)); })
      .concat((g.tawaran || []).map((e) => { const kp = kunciPelanggan(e.pemasok); semuaPem[kp] = semuaPem[kp] || e.pemasok; return Object.assign({ kunci: kp, pemasok: e.pemasok, jenis: 'tawaran' }, bdKelompokTawaran(e, R, S.rataPct)); }))
      .sort((a, b) => a.layakKg - b.layakKg || (a.jenis === 'beli' ? -1 : 1) || a.pemasok.localeCompare(b.pemasok));
    const t = baris[0]; baris.forEach((x, i) => { x.urut = i + 1; x.lebihMahal = i === 0 ? 0 : x.layakKg - t.layakKg; x.hematPerBulan = x.jenis === 'beli' && i > 0 ? Math.round(x.lebihMahal * x.kgNyata) : 0; });
    const nPem = baris.map((x) => x.kunci).filter((v, i, s) => s.indexOf(v) === i).length;
    return { kelas: g.kelas, het: g.het, kg: bdB(g.kg), baris, nPemasok: nPem, termurah: t,
      kalimat: baris.length < 2 ? 'baru satu pemasok berharga di kelas ini — catat harga tawaran pemasok lain untuk pembanding'
        : t.pemasok + (t.jenis === 'tawaran' ? ' (tawaran, perkiraan)' : '') + ' termurah: layak jual ' + RP(t.layakKg) + '/kg; ' + baris.slice(1).map((x) => x.pemasok + ' +' + RP(x.lebihMahal)).join(', ') };
  }).sort((a, b) => b.kg - a.kg || a.kelas.localeCompare(b.kelas));
  const nPemasok = Object.keys(semuaPem).length; const nilai = B.baris.reduce((a, r) => a + r.modalRp, 0) + B.nilaiLewat; const sapu = bdNilaiSapuan(Rg.awal, Rg.akhir); const menutup = Math.abs(nilai - sapu) < 0.5;
  const hemat = kelas.reduce((a, g) => a + g.baris.reduce((s, x) => s + x.hematPerBulan, 0), 0);
  return { key, nama: bdNamaBulan(key), awal: Rg.awal, akhir: Rg.akhir, berjalan: Rg.berjalan, kelas, nPemasok, pemasok: Object.keys(semuaPem).map((k) => semuaPem[k]).sort((a, b) => a.localeCompare(b)), min: A.minPemasok, cukup: nPemasok >= A.minPemasok,
    nBaris: B.baris.length, dilewati: B.dilewati, nilai, sapuan: sapu, menutup, susut: S, rataBongkar: R, dibanding: bcDibanding(key), hematBulan: hemat, adaPotong: A.adaPotong,
    kalimat: (!B.baris.length && !kelas.length ? 'Belum ada kedatangan maupun harga tawaran ' + bdNamaBulan(key) + '.'
      : nPemasok + ' pemasok dibanding ' + bdNamaBulan(key) + (nPemasok >= A.minPemasok ? ' (cukup, minimal ' + A.minPemasok + ')' : ' — KURANG dari ' + A.minPemasok + ': catat harga tawaran pemasok lain')
        + (hemat > 0 ? '. Kalau semua kelas dibeli dari yang termurah, bulan ini kira-kira ' + RP(hemat) + ' lebih hemat (layak jual × kg yang dibeli).' : '.'))
      + (menutup ? '' : ' PENJAGA TIDAK MENUTUP: Σ modal baris ' + RP(nilai) + ' ≠ nilai kedatangan di Bon pemasok ' + RP(sapu) + ' — jangan dipakai memutuskan, laporkan.') };
}

// ==================== A129 + A18 · LAPORAN MINGGUAN ====================
/**
 * Satu minggu (Senin–Minggu): per kelas, harga beli per kg tiap pemasok BERJAJAR (harga nota + tanggal kedatangan) + harga tawaran (tanggal ditanya),
 * + harga acuan minggu itu. → { senin, minggu, kelas: [{ kelas, het, kolom: [{ pemasok, jenis, harga, tanggal[], kg }] }], nPemasok, min, cukup, acuan }.
 */
export function bdMinggu(senin, kini) { const s = bcSenin(String(senin || hariIniIso(bdKini(kini)))); return ingatPerVersi('bdMinggu|' + s + '|' + hariIniIso(bdKini(kini)), () => bdMingguHitung(s, bdKini(kini))); }
function bdMingguHitung(senin, kini) {
  const iso = hariIniIso(kini); const minggu = bcTambahHari(senin, 6); const akhir = minggu > iso ? iso : minggu; const A = bcAtur();
  const B = bdBaris(senin, akhir); const per = {}; const semua = {};
  const kol = (kelas, het, kp, nama, jenis) => { const g = per[kelas] || (per[kelas] = { kelas, het, kolom: {} }); return g.kolom[kp + '|' + jenis] || (g.kolom[kp + '|' + jenis] = { kunci: kp, pemasok: nama, jenis, harga: [], tanggal: [], kg: 0, nilai: 0, teks: [] }); };
  B.baris.forEach((r) => { const c = kol(r.kelas, r.het, r.kunci, r.pemasok, 'beli'); c.harga.push(r.hargaPerKg); c.tanggal.push(r.tanggal); c.kg += r.kgNota; c.nilai += r.hargaPerKg * r.kgNota; semua[r.kunci] = r.pemasok; });
  const E = bcEntri(senin, akhir);
  E.filter((e) => e.jenis === 'tawaran').forEach((e) => { const kelas = Object.keys(per).find((k) => k.toLowerCase() === e.kelas.toLowerCase()) || e.kelas; const kp = kunciPelanggan(e.pemasok);
    const c = kol(kelas, hetAtur().peta[kelas] || '', kp, e.pemasok, 'tawaran'); c.harga.push(e.hargaPerKg); c.tanggal.push(e.tanggal); c.teks.push(bcTeks(e)); semua[kp] = semua[kp] || e.pemasok; });
  const kelas = Object.keys(per).map((k) => { const g = per[k];
    const kolom = Object.keys(g.kolom).map((x) => { const c = g.kolom[x]; const rata = c.jenis === 'beli' && c.kg > 0 ? c.nilai / c.kg : c.harga[c.harga.length - 1];
      return { kunci: c.kunci, pemasok: c.pemasok, jenis: c.jenis, harga: Math.round(rata), hargaSemua: c.harga.slice(), tanggal: c.tanggal.filter((t, i, s) => s.indexOf(t) === i).sort(), kg: bdB(c.kg), teks: c.teks }; })
      .sort((a, b) => a.harga - b.harga || a.pemasok.localeCompare(b.pemasok));
    const t = kolom[0]; kolom.forEach((c) => { c.lebih = c.harga - t.harga; });
    return { kelas: g.kelas, het: g.het, kolom, nPemasok: kolom.map((c) => c.kunci).filter((v, i, s) => s.indexOf(v) === i).length, kg: kolom.reduce((a, c) => a + c.kg, 0) };
  }).sort((a, b) => b.kg - a.kg || b.kolom.length - a.kolom.length || a.kelas.localeCompare(b.kelas));
  const n = Object.keys(semua).length; const acuan = E.filter((e) => e.jenis === 'acuan');
  return { senin, minggu, akhir, berjalan: minggu >= iso, kelas, nPemasok: n, pemasok: Object.keys(semua).map((k) => semua[k]).sort((a, b) => a.localeCompare(b)), min: A.minPemasok, cukup: n >= A.minPemasok, acuan,
    nTawaran: E.filter((e) => e.jenis === 'tawaran').length, nKedatangan: B.baris.map((r) => r.batchId).filter((v, i, s) => s.indexOf(v) === i).length,
    kalimat: 'Minggu ' + tanggalPendek(senin).replace(/ \d{4}$/, '') + '–' + tanggalPendek(minggu) + ': ' + n + ' pemasok punya harga' + (n >= A.minPemasok ? ' (cukup, minimal ' + A.minPemasok + ')' : ' — kurang ' + (A.minPemasok - n) + ' dari minimal ' + A.minPemasok)
      + ' · ' + B.baris.length + ' baris kedatangan, ' + E.filter((e) => e.jenis === 'tawaran').length + ' harga tawaran' + (acuan.length ? ', ' + acuan.length + ' harga acuan' : '') + '.' };
}

// ==================== A137 · RAPOR BULANAN PER PEMASOK ====================
/**
 * Rapor satu bulan per pemasok: kedatangan, kg, belanja, modal sampai toko & layak jual per kg, bongkar & ongkir per kg, selisih timbang (rekapTimbangMutu),
 * mutu (baris dicek, AWAS, potongan mutu), retur / tolak / klaim (jejak di kedatangan — cpBaca), susut gudang 3 bulan, lama kirim (Belanja), tawaran.
 */
export function bdRapor(key, kini) { const k = bdKini(kini); return ingatPerVersi('bdRapor|' + key + '|' + hariIniIso(k), () => bdRaporHitung(String(key), k)); }
function bdRaporHitung(key, kini) {
  const Rg = bdRentangBulan(key, kini); const B = bdBaris(Rg.awal, Rg.akhir); const S = bdSusut(Rg.akhir); const K = bpLamaKirim(kini, 180); const per = {};
  const p = (kp, nama) => per[kp] || (per[kp] = { kunci: kp, pemasok: nama, rs: [], batch: {}, retur: { kg: 0, rp: 0, n: 0 }, tolak: { kg: 0, rp: 0, n: 0 }, klaim: { rp: 0, n: 0, diminta: 0, disetujui: 0, ditolak: 0 }, tawaran: [], timbang: null });
  B.baris.forEach((r) => { const o = p(r.kunci, r.pemasok); o.rs.push(r); o.pemasok = r.pemasok; });
  ambilSemuaBatch().forEach((b) => { if (bdFondasi(b) || !b.tanggal || b.tanggal < Rg.awal || b.tanggal > Rg.akhir) return; const o = p(kunciPelanggan(b.pemasok), String(b.pemasok).trim()); o.batch[String(b.id)] = true;
    const C = cpBaca(b); C.potongan.forEach((x) => { if (x.jenis === 'retur') { o.retur.kg += x.kg; o.retur.rp += x.rp; o.retur.n += 1; } else { o.klaim.rp += x.rp; o.klaim.n += 1; } });
    C.ditolak.forEach((x) => { o.tolak.kg += x.kg; o.tolak.rp += x.nilai; o.tolak.n += 1; });
    if (C.klaim) { if (C.klaim.status === 'disetujui' || C.klaim.status === 'selesai') o.klaim.disetujui += 1; else if (C.klaim.status === 'ditolak') o.klaim.ditolak += 1; else o.klaim.diminta += 1; } });
  let T = null; try { T = rekapTimbangMutu({ dari: Rg.awal, sampai: Rg.akhir }); } catch (e) { T = null; }
  if (T) T.pemasok.forEach((x) => { const kp = kunciPelanggan(x.pemasok); if (!per[kp]) return; const o = per[kp]; const t = o.timbang || (o.timbang = { kedatangan: 0, ditimbang: 0, sebagian: 0, belumTimbang: 0, kgNota: 0, selisihKg: 0, kgKurang: 0, nilaiKurang: 0, dicek: 0, kedatanganAwas: 0, awas: [] });
    ['kedatangan', 'ditimbang', 'sebagian', 'belumTimbang', 'kgNota', 'selisihKg', 'kgKurang', 'nilaiKurang', 'dicek', 'kedatanganAwas'].forEach((k) => { t[k] += x[k] || 0; }); t.awas = t.awas.concat(x.awas || []); });
  bcEntri(Rg.awal, Rg.akhir).forEach((e) => { if (e.jenis === 'tawaran') p(kunciPelanggan(e.pemasok), e.pemasok).tawaran.push(e); });
  const daftar = Object.keys(per).map((kp) => { const o = per[kp]; const sus = S.per[kp] || null; const G = o.rs.length ? bdKelompok(o.rs, sus) : null; const kirim = K.pemasok.find((x) => x.kunci === kp) || null;
    const t = o.timbang; const tm = t ? Object.assign({}, t, { kgNota: bdB(t.kgNota), selisihKg: bdB(t.selisihKg), kgKurang: bdB(t.kgKurang), persen: t.kgNota > 0 ? Math.round(t.selisihKg / t.kgNota * 1000) / 10 : null }) : null;
    const tanda = {}; o.rs.forEach((r) => r.tanda.forEach((x) => { tanda[x] = (tanda[x] || 0) + 1; }));
    const kalimat = [];
    if (G) kalimat.push(G.n + ' baris dari ' + Object.keys(o.batch).length + ' kedatangan · ' + bdD(G.kgNyata) + ' kg diterima · modal sampai toko ' + RP(G.modalKg) + '/kg · layak jual ' + RP(G.layakKg) + '/kg');
    else kalimat.push(Object.keys(o.batch).length ? Object.keys(o.batch).length + ' kedatangan berisi kemasan jadi saja (tidak dibanding per kg)' : o.tawaran.length ? 'tidak ada kedatangan bulan ini — hanya ' + o.tawaran.length + ' harga tawaran' : 'tidak ada kedatangan bulan ini');
    if (tm) kalimat.push(tm.ditimbang + tm.sebagian ? 'timbang ' + (tm.selisihKg === 0 ? 'pas' : (tm.selisihKg < 0 ? 'kurang ' : 'lebih ') + bdD(Math.abs(tm.selisihKg)) + ' kg (' + bdPct(tm.persen) + ')') + (tm.belumTimbang ? ', ' + tm.belumTimbang + ' kedatangan belum ditimbang' : '') : 'belum ada yang ditimbang');
    if (G) kalimat.push(G.nAwas ? G.nAwas + ' baris mutu AWAS' + (o.rs.reduce((a, r) => a + r.potMutuRp, 0) > 0 ? ' (potongan ' + RP(o.rs.reduce((a, r) => a + r.potMutuRp, 0)) + ')' : '') : (tm && tm.dicek ? 'mutu dicek, tanpa AWAS' : 'mutu belum dicek'));
    if (o.retur.n || o.tolak.n) kalimat.push('retur ' + bdD(o.retur.kg) + ' kg (' + RP(o.retur.rp) + ') · ditolak saat datang ' + bdD(o.tolak.kg) + ' kg (' + RP(o.tolak.rp) + ')');
    if (o.klaim.n || o.klaim.diminta || o.klaim.disetujui || o.klaim.ditolak) kalimat.push('klaim: ' + (o.klaim.rp ? RP(o.klaim.rp) + ' dipotong' : 'belum ada yang dipotong') + (o.klaim.diminta ? ', ' + o.klaim.diminta + ' masih diminta' : '') + (o.klaim.ditolak ? ', ' + o.klaim.ditolak + ' ditolak pemasok' : ''));
    kalimat.push(sus && sus.pct !== null ? 'susut gudang ' + bdPct(sus.pct) + ' (3 bulan)' : 'susut gudang belum terukur');
    if (kirim) kalimat.push('dipesan sampai datang ' + bpHariTeks(kirim.rataHari));
    return { kunci: kp, pemasok: o.pemasok, kelompok: G, kedatangan: Object.keys(o.batch).length, timbang: tm, tanda: BC_TANDA.filter(([id]) => tanda[id]).map(([id, nm]) => ({ id, nama: nm, n: tanda[id] })),
      potMutuRp: o.rs.reduce((a, r) => a + r.potMutuRp, 0), retur: o.retur, tolak: o.tolak, klaim: o.klaim, susut: sus, kirim, tawaran: o.tawaran, kelas: o.rs.map((r) => r.kelas).filter((v, i, s) => s.indexOf(v) === i), kalimat: kalimat.join(' · ') };
  }).sort((a, b) => (b.kelompok ? b.kelompok.uang : -1) - (a.kelompok ? a.kelompok.uang : -1) || a.pemasok.localeCompare(b.pemasok));
  return { key, nama: bdNamaBulan(key), awal: Rg.awal, akhir: Rg.akhir, berjalan: Rg.berjalan, pemasok: daftar, susut: S,
    kalimat: daftar.filter((x) => x.kelompok).length + ' pemasok mengirim ' + bdNamaBulan(key) + (daftar.filter((x) => !x.kelompok).length ? ' · ' + daftar.filter((x) => !x.kelompok).length + ' hanya memberi harga tawaran' : '') + '.' };
}

// ==================== A19 · HARGA ACUAN ====================
/**
 * Acuan terbaru per (sumber, tingkat, mutu) dalam 62 hari + pembanding: modal sampai toko per kg 30 hari terakhir untuk kelas yang dipetakan ke HET
 * medium / premium (Harga › HET). → { acuan: [...], modal: { medium, premium }, tarik (hasil tarik otomatis) }.
 */
export function bdAcuan(kini) { const k = bdKini(kini); return ingatPerVersi('bdAcuan|' + hariIniIso(k), () => {
  const iso = hariIniIso(k); const dari = bcTambahHari(iso, -62); const E = bcEntri(dari, iso).filter((e) => e.jenis === 'acuan'); const akhir = {};
  E.forEach((e) => { akhir[e.sumber.toLowerCase() + '|' + e.tingkat + '|' + e.mutu] = e; });
  const B = bdBaris(bcTambahHari(iso, -29), iso); const modal = {};
  ['medium', 'premium'].forEach((m) => { const rs = B.baris.filter((r) => r.het === m); modal[m] = rs.length ? Object.assign({ kelas: rs.map((r) => r.kelas).filter((v, i, s) => s.indexOf(v) === i) }, bdKelompok(rs, null)) : null; });
  const acuan = Object.keys(akhir).map((x) => { const e = akhir[x]; const M = modal[e.mutu]; const riwayat = E.filter((y) => y.sumber.toLowerCase() === e.sumber.toLowerCase() && y.tingkat === e.tingkat && y.mutu === e.mutu).slice(-6);
    const lalu = riwayat.length > 1 ? riwayat[riwayat.length - 2] : null;
    return Object.assign({}, e, { tingkatNama: (BC_TINGKAT.find((t) => t[0] === e.tingkat) || ['', e.tingkat])[1], riwayat, gerak: lalu ? e.hargaPerKg - lalu.hargaPerKg : null,
      modalKg: M ? M.modalKg : null, selisih: M ? M.modalKg - e.hargaPerKg : null,
      kalimat: !M ? 'belum ada kedatangan ' + e.mutu + ' (kelas yang dipetakan HET ' + e.mutu + ') 30 hari terakhir untuk dibanding'
        : 'modal sampai toko ' + e.mutu + ' kita ' + RP(M.modalKg) + '/kg — ' + (M.modalKg > e.hargaPerKg ? RP(M.modalKg - e.hargaPerKg) + ' DI ATAS' : M.modalKg < e.hargaPerKg ? RP(e.hargaPerKg - M.modalKg) + ' di bawah' : 'sama dengan') + ' acuan ' + e.tingkat + ' ' + e.sumber });
  }).sort((a, b) => a.mutu.localeCompare(b.mutu) || BC_TINGKAT.findIndex((t) => t[0] === a.tingkat) - BC_TINGKAT.findIndex((t) => t[0] === b.tingkat) || a.sumber.localeCompare(b.sumber));
  const petaKosong = !Object.keys(hetAtur().peta).length;
  return { acuan, modal, tarik: bcTarik(), petaKosong, dari, iso,
    kalimat: !E.length ? 'Belum ada harga acuan 62 hari terakhir — ketik dari Panel Harga Bapanas / PIHPS BI / BPS (tiap Jumat, bareng harga tawaran).'
      : acuan.length + ' harga acuan terbaru' + (petaKosong ? ' · kelas beras belum dipetakan ke HET medium / premium (Harga › Katalog › HET) — pembanding modal belum bisa' : '') + '.' };
}); }

// ==================== A6 · TREN MODAL SAMPAI TOKO ====================
/** Modal sampai toko per kg per kelas, N bulan terakhir (bulan berjalan ikut), ▲▼ terhadap bulan sebelumnya + pemasok termurah tiap bulan. */
export function bdTren(kini, n) { const k = bdKini(kini); const N = Number(n) > 0 ? Math.round(Number(n)) : BD_TREN; return ingatPerVersi('bdTren|' + hariIniIso(k) + '|' + N, () => {
  const iso = hariIniIso(k); const bulan = []; for (let i = N - 1; i >= 0; i--) bulan.push(bcBulanGeser(iso.slice(0, 7), -i)); const per = {};
  bulan.forEach((key) => { const Rg = bdRentangBulan(key, k); const B = bdBaris(Rg.awal, Rg.akhir); const kel = {};
    B.baris.forEach((r) => { (kel[r.kelas] = kel[r.kelas] || []).push(r); });
    Object.keys(kel).forEach((c) => { const G = bdKelompok(kel[c], null); const pem = {}; kel[c].forEach((r) => { (pem[r.kunci] = pem[r.kunci] || { nama: r.pemasok, rs: [] }).rs.push(r); });
      const murah = Object.keys(pem).map((kp) => ({ nama: pem[kp].nama, modalKg: bdKelompok(pem[kp].rs, null).modalKg })).sort((a, b) => a.modalKg - b.modalKg)[0];
      (per[c] = per[c] || { kelas: c, het: kel[c][0].het, titik: {} }).titik[key] = { modalKg: G.modalKg, kg: G.kgNyata, n: G.n, termurah: murah }; }); });
  const kelas = Object.keys(per).map((c) => { const g = per[c]; let lalu = null; const titik = bulan.map((key) => { const t = g.titik[key] || null; const o = { key, nama: bdNamaBulan(key).slice(0, 3) + ' ' + key.slice(2, 4), ada: !!t };
      if (t) { Object.assign(o, t, { gerak: lalu ? t.modalKg - lalu.modalKg : null }); lalu = t; } return o; });
    const isi = titik.filter((t) => t.ada); const terendah = isi.slice().sort((a, b) => a.modalKg - b.modalKg)[0] || null; const akhirT = isi[isi.length - 1] || null;
    return { kelas: c, het: g.het, titik, kg: isi.reduce((a, t) => a + t.kg, 0), terendah, akhir: akhirT,
      kalimat: isi.length < 2 ? 'baru ' + isi.length + ' bulan berdata' : 'terakhir ' + RP(akhirT.modalKg) + '/kg (' + akhirT.nama + ')' + (akhirT.gerak !== null ? (akhirT.gerak > 0 ? ' ▲ ' + RP(akhirT.gerak) : akhirT.gerak < 0 ? ' ▼ ' + RP(-akhirT.gerak) : ' = sama') + ' dari bulan sebelumnya berdata' : '')
        + ' · terendah ' + RP(terendah.modalKg) + ' (' + terendah.nama + ')' }; }).sort((a, b) => b.kg - a.kg || a.kelas.localeCompare(b.kelas));
  return { bulan, kelas, kalimat: kelas.length ? kelas.length + ' kelas berkedatangan dalam ' + N + ' bulan terakhir.' : 'Belum ada kedatangan dalam ' + N + ' bulan terakhir.' };
}); }

/** Ringkas untuk Dasbor / Laporan: minggu ini + bulan lalu (sudah dibanding?) dalam dua kalimat. */
export function bdRingkas(kini) { const k = bdKini(kini); const iso = hariIniIso(k); return ingatPerVersi('bdRingkas|' + iso, () => {
  const M = bdMinggu(bcSenin(iso), k); const lalu = bcBulanGeser(iso.slice(0, 7), -1); const BL = bdBulan(lalu, k);
  return { minggu: M, bulanLalu: { key: lalu, nama: BL.nama, nPemasok: BL.nPemasok, min: BL.min, cukup: BL.cukup, dibanding: BL.dibanding, hemat: BL.hematBulan, menutup: BL.menutup },
    kalimat: M.kalimat + ' Bulan lalu (' + BL.nama + '): ' + BL.nPemasok + ' pemasok dibanding' + (BL.dibanding ? ', sudah ditandai dibaca.' : ', belum ditandai dibaca.') };
}); }

/** Calon ketikan lembar catat: kelas (kedatangan 120 hari terakhir, kg terbanyak dulu, + kelas tawaran) & pemasok (Bon pemasok + yang pernah menawarkan). */
export function bdCalon(kini) { const iso = hariIniIso(bdKini(kini)); return ingatPerVersi('bdCalon|' + iso, () => {
  const B = bdBaris(bcTambahHari(iso, -119), iso); const kg = {}; B.baris.forEach((r) => { kg[r.kelas] = (kg[r.kelas] || 0) + r.kgNyata; });
  const E = bcEntri(bcTambahHari(iso, -365), iso).filter((e) => e.jenis === 'tawaran'); E.forEach((e) => { if (!(e.kelas in kg)) kg[e.kelas] = 0; });
  const pem = {}; daftarPemasok().forEach((p) => { pem[p.kunci] = p.nama; }); E.forEach((e) => { const k = kunciPelanggan(e.pemasok); if (!pem[k]) pem[k] = e.pemasok; });
  return { kelas: Object.keys(kg).sort((a, b) => kg[b] - kg[a] || a.localeCompare(b)), pemasok: Object.keys(pem).map((k) => pem[k]).sort((a, b) => a.localeCompare(b)) };
}); }
