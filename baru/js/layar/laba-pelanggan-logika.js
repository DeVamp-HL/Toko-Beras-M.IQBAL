// LAPORAN PER PELANGGAN — putaran B5 laporan & cost controlling B2B (keputusan owner 18 Nov 2026). Logika TANPA DOM, nama berawalan pg (bundel uji jsc satu
// lingkup). Dijaga alat-uji/uji_laba_pelanggan.py (jsc + kontrol).
//
// Keputusan owner 18 Nov 2026:
//  - KELOMPOK: baris kontribusi per TINGKAT harga (B1, aturanToko/hargaTingkat: Warung · Catering · Instansi …) + Eceran. Pelanggan USAHA (punya tingkat)
//    dirinci per orang; pembeli eceran — bernama atau tidak — digabung satu baris.
//  - TEMPO = HARI saja: rata-rata berapa hari sampai bon dibayar, sisa bon, faktur lewat jatuh tempo. Tidak ada rupiah taksiran / bunga.
//  - ANTAR: ongkir yang DITAGIH ke pelanggan itu saja; Bensin & angkut tetap di Biaya toko, tidak dibagi ke pelanggan.
//  - TEMPAT: kartu "Per pelanggan" di Laporan › Laba (1 / 3 / 12 bulan) + kartu ringkas di Dasbor.
//
// TIDAK ADA RUMUS LABA BARU. Baris yang dibaca = baris mesin laba Laporan (ambilPenjualan + tanggal; modal = hppTotalSaatJual yang TERSIMPAN di nota; retur
// periode itu memotong omzet lewat uangKembaliRetur, modal retur UTUH dibatalkan lewat hppTaksiranRetur — pola merekBulan di laporan-logika.js), cuma
// dipilah per pelanggan: nama di nota (kunciPelanggan), retur ikut nama di nota asalnya. Ongkir antar (kolom ongkirAntar, ikut hargaTotal) masuk laba kotor
// pelanggan itu dengan HPP 0 dan ditulis terpisah. PENJAGA: Σ semua kelompok = laba kotor, omzet tanpa modal, jumlah baris nota & kg di nota Laporan periode
// itu, persis sampai rupiah → kalau tidak, menutup: false + kalimat (angka per pelanggan jangan dipakai memutuskan).
// "DILEPAS dari harga eceran" = keterangan, BUKAN pengurang laba (sudah melekat di hargaTotal): potongan tingkat (hargaEceranSatuan − hargaAsliSatuan) ×
// jumlah, nego (− negoSelisih × jumlah; minus = harga dinaikkan), potongan nota (potonganTransaksi). Jumlah satuan = harga barang baris ÷ harga satuan akhir.
// TEMPO dibaca dari buku piutang mesin yang sama (hitungPiutang) disusun menurut waktu: pembayaran yang DITUJU (faktur / pesanan, fkTujuanBayar) menutup
// barisnya dulu, retur menutup nota asalnya, sisanya menutup bon TERTUA dulu (= mesin). Baris nota periode itu yang lunas → hari sampai lunas, ditimbang
// rupiah. Bon yang ditutup hapus buku tidak dihitung "dibayar".
import { bayaranBiayaBulanan, hitungPiutang } from '../mesin/beku.js';
import { akhirBulanIso, hppTercatat, kunciPelanggan, hppTaksiranRetur, uangKembaliRetur } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPenjualanSemua, ambilRetur, ingatStokKarung, ingatStokKemasan, tahunDiarsip, kunciNota, ingatPerVersi } from '../data/toko.js';
import { RP, KG, hariIniIso } from '../inti/format.js';
import { ugLabaBersih, ugBayaran } from './uang-logika.js';
import { lpFinal, lpNamaBulan, lpBulanPendek, lpPersenTeks } from './laporan-logika.js';
import { fkSemua, fkPeta, fkTujuanBayar } from './faktur-logika.js';
import { htAtur, htTingkat } from './harga-tingkat-logika.js';

export const PG_RENTANG = [[1, '1 bulan'], [3, '3 bulan'], [12, '12 bulan']].map((x) => ({ n: x[0], nama: x[1] }));
export const PG_ECERAN = 'eceran';
export const PG_TERATAS = 10;   // pelanggan usaha yang dirinci di kartu; sisanya di balik "lihat semua"
export const PG_KALIMAT_DILEPAS = '"Dibanding eceran" = harga eceran katalog dibanding harga yang benar-benar dibayar: potongan tingkat, nego (turun atau naik), dan potongan nota. Sudah ada di dalam laba kotor (bukan pengurang kedua).';
export const PG_KALIMAT_TEMPO = 'Rata-rata hari dibayar = nota bon periode ini yang sudah lunas, dihitung dari tanggal nota sampai lunas, ditimbang rupiah. Urutan bayar sama dengan buku bon: bayar yang ditujukan ke faktur / pesanan dulu, sisanya bon tertua dulu. Dibayar saat beli = 0 hari.';
const pgKey = (iso) => String(iso || '').slice(0, 7);
const pgGeser = (key, n) => { const y = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)) - 1 + n; return new Date(Date.UTC(y + Math.floor(m / 12), ((m % 12) + 12) % 12, 1)).toISOString().slice(0, 7); };
export const pgHariKe = (iso) => Math.round(Date.parse(String(iso || '').slice(0, 10) + 'T00:00:00Z') / 86400000);
export const pgPersen = lpPersenTeks;

/** Rentang n bulan yang berakhir di bulan key ('YYYY-MM'). Bulan di tahun yang sudah ditutup buku ikut arsip (catatan per notanya tidak dimuat) → tidak
 *  dirinci, DISEBUT. → { key, n, bulan, pakai, diarsip, dari, sampai, nama, final } — dari/sampai = '' bila semua bulannya ikut arsip. */
export function pgRentang(key, n0) {
  const n = PG_RENTANG.some((r) => r.n === Number(n0)) ? Number(n0) : 1; const bulan = [];
  for (let i = n - 1; i >= 0; i--) bulan.push(pgGeser(key, -i));
  const diarsip = bulan.filter((k) => tahunDiarsip(k)); const pakai = bulan.filter((k) => !tahunDiarsip(k));
  return { key, n, bulan, pakai, diarsip, dari: pakai.length ? pakai[0] + '-01' : '', sampai: pakai.length ? akhirBulanIso(pakai[pakai.length - 1]) : '',
    nama: n === 1 ? lpNamaBulan(key) : lpBulanPendek(bulan[0], true) + ' – ' + lpBulanPendek(key, true), final: pakai.length > 0 && pakai.every((k) => lpFinal(k)) };
}

/** Harga yang dilepas dibanding eceran untuk satu baris nota → { tingkat, nego, nota } (rupiah, belum dibulatkan). */
export function pgDilepas(p) {
  const nota = Math.round(Number(p.potonganTransaksi) || 0); const asli = Number(p.hargaAsliSatuan); const neg = Number(p.negoSelisih) || 0; const hs = asli + neg;
  if (p.hargaAsliSatuan === undefined || p.hargaAsliSatuan === null || !isFinite(asli) || !(hs > 0)) return { tingkat: 0, nego: 0, nota };
  const barang = (Number(p.hargaTotal) || 0) - (Number(p.ongkirAntar) || 0) - (Number(p.pembulatan) || 0) - (Number(p.upahRepack) || 0) + nota;
  const jml = Math.max(0, barang / hs); const ec = Number(p.hargaEceranSatuan);
  return { tingkat: p.hargaEceranSatuan !== undefined && isFinite(ec) && ec > 0 ? (ec - asli) * jml : 0, nego: -neg * jml, nota };
}

const pgKosong = () => ({ nBaris: 0, nota: {}, kgNota: 0, kgKembali: 0, omzetHitung: 0, hppHitung: 0, adaHitung: false, nTanpaHpp: 0, omzetTanpaHpp: 0,
  ongkirHitung: 0, ongkirTanpaHpp: 0, nOngkir: 0, nRetur: 0, returUang: 0, returHpp: 0, lepasTingkat: 0, lepasNego: 0, lepasNota: 0 });
const PG_JUMLAH = ['nBaris', 'kgNota', 'kgKembali', 'omzetHitung', 'hppHitung', 'nTanpaHpp', 'omzetTanpaHpp', 'ongkirHitung', 'ongkirTanpaHpp', 'nOngkir', 'nRetur', 'returUang', 'returHpp',
  'lepasTingkat', 'lepasNego', 'lepasNota'];
const pgGabung = (daftar) => { const g = pgKosong(); daftar.forEach((x) => { PG_JUMLAH.forEach((f) => { g[f] += x[f] || 0; }); if (x.adaHitung) g.adaHitung = true; Object.assign(g.nota, x.nota); }); return g; };
/** Angka turunan satu kelompok. laba kotor = margin barang (omzet ber-modal − retur − (HPP − modal retur utuh)) + ongkir di nota ber-modal; null = kelompok itu
 *  tidak menyumbang apa pun ke laba kotor mesin ('belum' = semua barisnya tanpa modal, 'kosong' = tidak ada jualan / retur). */
function pgJadi(g) {
  const omzetBer = g.omzetHitung - g.returUang; const hpp = g.hppHitung - g.returHpp; const marginBarang = g.adaHitung || g.nRetur > 0 ? omzetBer - hpp : null;
  const laba = marginBarang === null && !g.ongkirHitung ? null : (marginBarang || 0) + g.ongkirHitung;
  const dilepas = { tingkat: Math.round(g.lepasTingkat), nego: Math.round(g.lepasNego), nota: Math.round(g.lepasNota) }; dilepas.total = dilepas.tingkat + dilepas.nego + dilepas.nota;
  return Object.assign(g, { nNota: Object.keys(g.nota).length, kg: g.kgNota - g.kgKembali, omzet: g.omzetHitung + g.omzetTanpaHpp - g.returUang, omzetBer, hpp, marginBarang,
    ongkir: g.ongkirHitung + g.ongkirTanpaHpp, labaKotor: laba, keadaan: laba !== null ? 'ada' : g.nTanpaHpp > 0 ? 'belum' : 'kosong',
    pct: marginBarang !== null && omzetBer > 0 ? marginBarang / omzetBer * 100 : null, dilepas });
}

/** Tempo satu orang dari rekaman mesin d (hitungPiutang) → { nLunas, rpLunas, rata (hari, null = belum ada bon periode ini yang lunas), nTerbuka (baris
 *  periode itu yang belum lunas), umurTertua (hari bon tertua yang masih terbuka, null), sisa, lebih }. Disusun menurut waktu, lihat kepala berkas. */
export function pgTempo(d, dari, sampai, iso, P0) {
  const out = { nLunas: 0, rpLunas: 0, hariRp: 0, rata: null, nTerbuka: 0, umurTertua: null, sisa: d && d.sisa > 0.5 ? Math.round(d.sisa) : 0, lebih: d && d.sisa < -0.5 ? Math.round(-d.sisa) : 0 };
  if (!d || !Array.isArray(d.mutasi)) return out;
  const P = P0 || fkPeta(); const urut = (x) => String(x.tanggal || '') + ' ' + String(x.jam || '');
  const ev = d.mutasi.map((m, i) => ({ m, i, utang: m.jenis === 'jual' || m.jenis === 'saldoAwal' })).sort((a, b) => urut(a.m).localeCompare(urut(b.m)) || (a.utang === b.utang ? a.i - b.i : a.utang ? -1 : 1));
  const buka = []; let kolam = 0;
  const tutup = (u, n, e) => { const x = Math.min(u.sisa, n); u.sisa -= x; if (u.sisa <= 0.5 && !u.lunas) { u.lunas = e.m.tanggal || ''; u.hapus = e.m.jenis === 'hapusBuku'; } return x; };
  const tuang = (e) => { if (kolam <= 0) return; buka.slice().sort((a, b) => String(a.m.tanggal || '').localeCompare(String(b.m.tanggal || ''))).forEach((u) => { if (kolam > 0 && u.sisa > 0.5) kolam -= tutup(u, kolam, e); }); };
  const semua = [];
  ev.forEach((e) => {
    const n = Number(e.m.nominal) || 0;
    if (e.utang) { const u = { m: e.m, sisa: n, nominal: n, lunas: '', hapus: false }; semua.push(u); buka.push(u); if (n <= 0.5) u.lunas = e.m.tanggal || ''; tuang(e); return; }
    let sisa = n;
    if (n > 0) {
      let tuju = [];
      if (e.m.jenis === 'retur' && e.m.notaAsalId !== null && e.m.notaAsalId !== undefined) tuju = buka.filter((u) => u.m.jenis === 'jual' && String(u.m.idTrx) === String(e.m.notaAsalId));
      else if (e.m.jenis === 'bayar') { const t = fkTujuanBayar(P.bayar[String(e.m.idMutasi)], P); if (t.length) tuju = buka.filter((u) => u.m.jenis === 'jual' && (t.indexOf(P.baris[String(u.m.idTrx)]) >= 0 || t.indexOf(P.trx[String(u.m.idTrx)]) >= 0)); }
      tuju.forEach((u) => { if (sisa > 0 && u.sisa > 0.5) sisa -= tutup(u, sisa, e); });
    }
    kolam += sisa; tuang(e);
  });
  // dihitung per NOTA (baris-baris satu nota digabung lewat peta trx faktur-logika): nota lunas = semua barisnya lunas, nota terbuka = ada baris yang belum
  const h0 = pgHariKe(iso); const nota = {}; const kunciN = (u) => (P.trx && P.trx[String(u.m.idTrx)]) || 'baris:' + String(u.m.idTrx);
  semua.forEach((u) => {
    const dlm = u.m.jenis === 'jual' && !!u.m.tanggal && (!dari || u.m.tanggal >= dari) && (!sampai || u.m.tanggal <= sampai); const N = dlm ? (nota[kunciN(u)] = nota[kunciN(u)] || { buka: false, lunas: false }) : null;
    if (u.sisa > 0.5) { if (N) N.buka = true; const um = h0 - pgHariKe(u.m.tanggal); if (out.umurTertua === null || um > out.umurTertua) out.umurTertua = Math.max(0, um); return; }
    if (!dlm || u.hapus || !(u.nominal > 0)) return;
    N.lunas = true; out.rpLunas += u.nominal; out.hariRp += Math.max(0, pgHariKe(u.lunas) - pgHariKe(u.m.tanggal)) * u.nominal;
  });
  Object.keys(nota).forEach((k) => { if (nota[k].buka) out.nTerbuka += 1; else if (nota[k].lunas) out.nLunas += 1; });
  out.rata = out.rpLunas > 0 ? out.hariRp / out.rpLunas : null;
  return out;
}
const pgTempoGabung = (daftar) => { const t = { nLunas: 0, rpLunas: 0, hariRp: 0, rata: null, nTerbuka: 0, umurTertua: null, sisa: 0, lebih: 0 };
  daftar.forEach((x) => { ['nLunas', 'rpLunas', 'hariRp', 'nTerbuka', 'sisa', 'lebih'].forEach((f) => { t[f] += x[f] || 0; }); if (x.umurTertua !== null && (t.umurTertua === null || x.umurTertua > t.umurTertua)) t.umurTertua = x.umurTertua; });
  t.rata = t.rpLunas > 0 ? t.hariRp / t.rpLunas : null; return t; };
export const pgHariTeks = (h) => (h === null || h === undefined ? '—' : h < 0.5 ? 'hari itu juga' : '±' + Math.round(h) + ' hari');

/**
 * Per pelanggan untuk n bulan yang berakhir di bulan key → { key, n, nama, final, berjalan, rentang, diarsip (semua bulannya ikut arsip), kalimatArsip,
 * tingkat: [kelompok per tingkat … , Eceran], orang: [pelanggan usaha, laba kotor terbesar dulu], pembeli: [SEMUA pembeli bernama, omzet terbesar dulu],
 * tanpaNama (nota tanpa nama pembeli), omzetBarang (Σ omzet barang semua kelompok, tanpa ongkir), eceran, usaha (gabungan semua pelanggan usaha), b2b
 * { porsiLaba, porsiOmzet }, lewat { rp, n }, L, identitas, menutup, kalimat, tanpaCatatan }.
 */
export function pelangganBulan(key, n, kini, bayaran) {
  const iso = hariIniIso(kini);
  return ingatPerVersi('pgBulan|' + key + '|' + n + '|' + iso + (bayaran ? '|b' : ''), () => pgHitung(key, n, iso, bayaran));
}
function pgHitung(key, n, iso, bayaran) {
  const R = pgRentang(key, n);
  const dasar = { key, n: R.n, nama: R.nama, final: R.final, berjalan: key === pgKey(iso), rentang: R,
    kalimatArsip: R.diarsip.length ? (R.diarsip.length === R.bulan.length ? 'Semua bulan ' + R.nama : R.diarsip.length + ' bulan pertama') + ' sudah tutup buku — catatan per notanya ikut arsip, tidak bisa dipilah per pelanggan (laba kotornya tetap di kartu Laba).' : '' };
  if (!R.pakai.length) return Object.assign(dasar, { diarsip: true, tingkat: [], orang: [], pembeli: [], tanpaNama: null, eceran: null, usaha: null, b2b: null, lewat: { rp: 0, n: 0 }, L: null, identitas: [], menutup: null, kalimat: dasar.kalimatArsip, tanpaCatatan: true });
  const B = bayaran || ugBayaran(); const L = ugLabaBersih(R.dari, R.sampai, B); const cocok = (t) => !!t && t >= R.dari && t <= R.sampai;
  const A = htAtur(); const per = {}; const tanpaNama = pgKosong(); const baris = {}; const namaAkhir = {};
  const ke = (k) => (k ? (per[k] = per[k] || pgKosong()) : tanpaNama);
  ambilPenjualan().forEach((p) => {
    if (!cocok(p.tanggal)) return; const k = kunciPelanggan(p.namaPelanggan); const g = ke(k);
    if (k) { (baris[k] = baris[k] || []).push(p); if (!namaAkhir[k] || Number(p.id) >= namaAkhir[k].id) namaAkhir[k] = { id: Number(p.id) || 0, nama: String(p.namaPelanggan).trim() }; }
    g.nBaris += 1; g.nota[kunciNota(p)] = 1; g.kgNota += Number(p.totalKg) || 0;
    const ong = Math.round(Number(p.ongkirAntar) || 0); const harga = (p.hargaTotal || 0) - ong;
    if (hppTercatat(p)) { g.adaHitung = true; g.omzetHitung += harga; g.hppHitung += p.hppTotalSaatJual || 0; g.ongkirHitung += ong; } else { g.nTanpaHpp += 1; g.omzetTanpaHpp += harga; g.ongkirTanpaHpp += ong; }
    if (ong) g.nOngkir += 1;
    const D = pgDilepas(p); g.lepasTingkat += D.tingkat; g.lepasNego += D.nego; g.lepasNota += D.nota;
  });
  // retur periode itu — ikut nama di NOTA ASALNYA (nama di dokumen retur hanya ada untuk potong bon); uang & modal = fungsi mesin yang sama dengan merekBulan
  const retur = (ambilRetur() || []).filter((r) => cocok(r.tanggal)); const adaUtuh = retur.some((r) => r.kondisi === 'utuh');
  const stokKrg = adaUtuh ? ingatStokKarung() : null; const stokKem = adaUtuh ? ingatStokKemasan() : null; const asal = {};
  if (retur.length) (ambilPenjualanSemua() || []).forEach((p) => { asal[String(p.id)] = p; });
  retur.forEach((r) => { const pa = asal[String(r.notaAsalId)]; const g = ke(kunciPelanggan(pa ? pa.namaPelanggan : r.namaPelanggan)); g.nRetur += 1; g.returUang += uangKembaliRetur(r); g.kgKembali += Number(r.totalKg) || 0;
    if (r.kondisi === 'utuh') g.returHpp += hppTaksiranRetur(r, stokKrg, stokKem); });
  // tingkat tiap orang: tingkat SEKARANG (aturanToko/hargaTingkat.orang); yang tingkatnya sudah dicabut tapi notanya periode ini bertingkat → tingkat di nota terakhirnya
  const tingkatOrang = (k) => { const t = A.orang[k] ? htTingkat(A, A.orang[k]) : null; if (t) return { id: t.id, nama: t.nama, dulu: false };
    const r = (baris[k] || []).filter((p) => p.tingkatId).sort((a, b) => (Number(b.id) || 0) - (Number(a.id) || 0))[0];
    if (!r) return null; const t2 = htTingkat(A, r.tingkatId); return { id: t2 ? t2.id : String(r.tingkatId), nama: t2 ? t2.nama : String(r.tingkatHarga || r.tingkatId), dulu: true }; };
  // tempo: buku piutang mesin (sekarang) + faktur yang lewat jatuh tempo
  const piutang = {}; hitungPiutang().forEach((d) => { piutang[d.kunci] = d; });
  const lewatOrang = {}; fkSemua(new Date(iso + 'T12:00:00')).forEach((f) => { if (f.status !== 'lewat' || !f.kunci) return; const x = lewatOrang[f.kunci] = lewatOrang[f.kunci] || { rp: 0, n: 0, hariMaks: 0 }; x.rp += f.sisa; x.n += 1; x.hariMaks = Math.max(x.hariMaks, f.hariLewat || 0); });
  const P = fkPeta(); const tempo = (k) => pgTempo(piutang[k], R.dari, R.sampai, iso, P);
  // usaha = punya tingkat sekarang / bertingkat di nota periode ini; ikut juga pelanggan usaha yang tidak belanja periode ini tapi masih punya bon / faktur lewat
  const kunciUsaha = {}; Object.keys(per).forEach((k) => { if (tingkatOrang(k)) kunciUsaha[k] = 1; });
  Object.keys(A.orang || {}).forEach((k) => { if (htTingkat(A, A.orang[k]) && ((piutang[k] && piutang[k].sisa > 0.5) || lewatOrang[k])) kunciUsaha[k] = 1; });
  const orang = Object.keys(kunciUsaha).map((k) => { const T = tingkatOrang(k); const g = pgJadi(per[k] || pgKosong()); const d = piutang[k];
    return Object.assign(g, { kunci: k, nama: namaAkhir[k] ? namaAkhir[k].nama : d ? d.nama : k, tingkatId: T.id, tingkatNama: T.nama, tingkatDulu: T.dulu, tempo: tempo(k), lewat: lewatOrang[k] || { rp: 0, n: 0, hariMaks: 0 }, tanpaJualan: !per[k] }); })
    .sort((a, b) => (a.labaKotor === null ? (b.labaKotor === null ? 0 : 1) : b.labaKotor === null ? -1 : b.labaKotor - a.labaKotor) || b.omzet - a.omzet || a.nama.localeCompare(b.nama));
  const kunciEceran = Object.keys(per).filter((k) => !kunciUsaha[k]);
  const eceranG = pgJadi(pgGabung(kunciEceran.map((k) => per[k]).concat([tanpaNama])));
  const eceran = Object.assign(eceranG, { id: PG_ECERAN, nama: 'Pembeli umum', nOrang: kunciEceran.length, nTanpaNama: Object.keys(tanpaNama.nota).length,
    tempo: pgTempoGabung(Object.keys(piutang).filter((k) => !kunciUsaha[k]).map((k) => tempo(k))), lewat: Object.keys(lewatOrang).filter((k) => !kunciUsaha[k]).reduce((a, k) => ({ rp: a.rp + lewatOrang[k].rp, n: a.n + lewatOrang[k].n, hariMaks: Math.max(a.hariMaks, lewatOrang[k].hariMaks) }), { rp: 0, n: 0, hariMaks: 0 }) });
  // Pondasi paket ketiga (owner 25 Nov 2026): pembeli BERNAMA satu per satu (usaha + eceran bernama) dan kelompok nota tanpa nama — bahan "bergantung pada
  // satu pembeli" & "berapa omzet yang pembelinya dikenal". Disusun SESUDAH eceran digabung: pgJadi menulis angka turunan ke objek kelompoknya sendiri.
  const eceranNama = kunciEceran.map((k) => Object.assign(pgJadi(per[k]), { kunci: k, nama: namaAkhir[k] ? namaAkhir[k].nama : k }));
  const tanpaNamaG = Object.assign(pgJadi(tanpaNama), { nama: 'Tanpa nama' });
  // per tingkat — urutan tingkat di setelan owner, tingkat lama yang sudah dihapus di belakang; Eceran paling bawah
  const urutT = (A.tingkat || []).map((t) => t.id); const idT = []; orang.forEach((o) => { if (idT.indexOf(o.tingkatId) < 0) idT.push(o.tingkatId); });
  idT.sort((a, b) => (urutT.indexOf(a) < 0 ? 99 : urutT.indexOf(a)) - (urutT.indexOf(b) < 0 ? 99 : urutT.indexOf(b)));
  const gabungOrang = (daftar) => Object.assign(pgJadi(pgGabung(daftar)), { nOrang: daftar.filter((o) => !o.tanpaJualan).length, tempo: pgTempoGabung(daftar.map((o) => o.tempo)), lewat: daftar.reduce((a, o) => ({ rp: a.rp + o.lewat.rp, n: a.n + o.lewat.n, hariMaks: Math.max(a.hariMaks, o.lewat.hariMaks) }), { rp: 0, n: 0, hariMaks: 0 }) });
  const tingkat = idT.map((id) => { const dd = orang.filter((o) => o.tingkatId === id); return Object.assign(gabungOrang(dd), { id, nama: dd[0].tingkatNama }); }).concat([eceran]);
  const usaha = orang.length ? Object.assign(gabungOrang(orang), { id: 'usaha', nama: 'Pelanggan usaha' }) : null;
  // porsi: laba kotor & omzet barang (tanpa ongkir) per kelompok terhadap jumlahnya
  const totLaba = tingkat.reduce((a, g) => a + (g.labaKotor || 0), 0); const totOmzet = tingkat.reduce((a, g) => a + g.omzet, 0);
  const porsi = (g) => { g.porsiLaba = totLaba > 0 && g.labaKotor !== null ? g.labaKotor / totLaba * 100 : null; g.porsiOmzet = totOmzet > 0 ? g.omzet / totOmzet * 100 : null; };
  tingkat.forEach(porsi); orang.forEach(porsi); if (usaha) porsi(usaha);
  eceranNama.forEach(porsi); porsi(tanpaNamaG);
  const pgRingkas = (g, usahaYa) => ({ kunci: g.kunci, nama: g.nama, usaha: usahaYa, tingkatNama: usahaYa ? g.tingkatNama : '', omzet: g.omzet, labaKotor: g.labaKotor, nNota: g.nNota, porsiOmzet: g.porsiOmzet, porsiLaba: g.porsiLaba });
  const pembeli = orang.filter((o) => !o.tanpaJualan).map((o) => pgRingkas(o, true)).concat(eceranNama.map((o) => pgRingkas(o, false)))
    .sort((a, b) => b.omzet - a.omzet || a.nama.localeCompare(b.nama));
  // PENJAGA IDENTITAS — tiap jumlah dibandingkan dengan angka Laporan (mesin) periode itu, bukan dengan dirinya sendiri
  const sig = (f) => tingkat.reduce((a, g) => a + (Number(g[f]) || 0), 0);
  const banding = (nm, x, y) => ({ nama: nm, pelanggan: x, laporan: y, beda: x - y, cocok: Math.abs(x - y) < 0.5 });
  const kgNota = ambilPenjualan().reduce((a, p) => a + (cocok(p.tanggal) ? Number(p.totalKg) || 0 : 0), 0);
  const identitas = [banding('laba kotor', totLaba, L.margin), banding('omzet tanpa modal', sig('omzetTanpaHpp') + sig('ongkirTanpaHpp'), L.omzetTanpaHpp),
    banding('jumlah baris nota', sig('nBaris'), L.jumlahTrx), banding('kg di nota', sig('kgNota'), kgNota)];
  const menutup = identitas.every((x) => x.cocok); const teks = (nm, x) => (/kg/.test(nm) ? KG(x) : /baris/.test(nm) ? String(Math.round(x)) : RP(x));
  const kalimat = menutup ? 'Σ ' + (idT.length ? idT.length + ' tingkat + ' : '') + 'eceran = laba kotor Laporan ' + RP(L.margin) + ' — menutup persis sampai rupiah.'
    : 'TIDAK MENUTUP ke Laporan: ' + identitas.filter((x) => !x.cocok).map((x) => x.nama + ' per pelanggan ' + teks(x.nama, x.pelanggan) + ' ≠ Laporan ' + teks(x.nama, x.laporan) + ' (beda ' + teks(x.nama, x.beda) + ')').join('; ') + '. Angka per pelanggan jangan dipakai memutuskan — laporkan.';
  const lewat = orang.concat([eceran]).reduce((a, g) => ({ rp: a.rp + g.lewat.rp, n: a.n + g.lewat.n }), { rp: 0, n: 0 });
  return Object.assign(dasar, { diarsip: false, tingkat, orang, pembeli, tanpaNama: { omzet: tanpaNamaG.omzet, labaKotor: tanpaNamaG.labaKotor, nNota: tanpaNamaG.nNota, porsiOmzet: tanpaNamaG.porsiOmzet }, omzetBarang: totOmzet, eceran, usaha, b2b: usaha ? { porsiLaba: usaha.porsiLaba, porsiOmzet: usaha.porsiOmzet, laba: usaha.labaKotor, omzet: usaha.omzet, nOrang: usaha.nOrang } : null,
    lewat, L: { margin: L.margin, omzetTanpaHpp: L.omzetTanpaHpp, jumlahTrx: L.jumlahTrx, omzetHitung: L.omzetHitung }, identitas, menutup, kalimat, tanpaCatatan: !L.jumlahTrx && !retur.length && !orang.length });
}

/** Harga dibanding eceran dalam kalimat kejadian: potongan tingkat, nego turun / naik, potongan nota (yang nol tidak disebut). '' = sama dengan eceran. */
export function pgDilepasTeks(D) {
  if (!D) return ''; const r = [D.tingkat > 0 ? 'potongan tingkat ' + RP(D.tingkat) : D.tingkat < 0 ? 'harga tingkat di atas eceran ' + RP(-D.tingkat) : '',
    D.nego > 0 ? 'nego turun ' + RP(D.nego) : D.nego < 0 ? 'nego naik ' + RP(-D.nego) : '', D.nota > 0 ? 'potongan nota ' + RP(D.nota) : ''].filter(Boolean);
  return r.length ? 'dibanding eceran: ' + r.join(', ') : '';
}
/** Keterangan satu kelompok untuk layar (satu baris k2): kg, nota, margin %, ongkir, harga dibanding eceran. */
export function pgKet(g) {
  if (!g) return '';
  const D = g.dilepas || { total: 0 };
  return [g.nNota ? g.nNota + ' nota' : '', g.kg ? KG(g.kg) : '', g.keadaan === 'belum' ? g.nTanpaHpp + ' baris tanpa modal (' + RP(g.omzetTanpaHpp) + ') — laba belum bisa dihitung'
    : g.keadaan === 'kosong' ? 'tidak ada jualan periode ini' : 'margin barang ' + pgPersen(g.pct) + (g.nTanpaHpp ? ' · ' + g.nTanpaHpp + ' baris tanpa modal belum ikut' : ''),
    g.ongkir ? 'ongkir ditagih ' + RP(g.ongkir) + ' (' + g.nOngkir + ' nota)' : '', pgDilepasTeks(D), g.nRetur ? g.nRetur + ' retur ' + RP(g.returUang) : ''].filter(Boolean).join(' · ');
}
/** Keterangan tempo satu kelompok: rata-rata hari dibayar, sisa bon, faktur lewat jatuh tempo, bon tertua yang masih terbuka. */
export function pgKetTempo(g) {
  if (!g || !g.tempo) return ''; const T = g.tempo; const W = g.lewat || { rp: 0, n: 0, hariMaks: 0 };
  return [T.rata !== null ? 'bon dibayar rata-rata ' + pgHariTeks(T.rata) + ' (' + T.nLunas + ' nota lunas)' : '',
    T.sisa ? 'sisa bon ' + RP(T.sisa) + (T.umurTertua !== null ? ', tertua ' + T.umurTertua + ' hari' : '') : '', W.n ? 'LEWAT TEMPO ' + RP(W.rp) + ' (' + W.n + ' faktur, terlama ' + W.hariMaks + ' hari)' : '',
    T.lebih ? 'uang pelanggan dipegang toko ' + RP(T.lebih) : ''].filter(Boolean).join(' · ');
}
