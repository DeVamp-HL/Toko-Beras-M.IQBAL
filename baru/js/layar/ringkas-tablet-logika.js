// RINGKAS HARI INI di tablet (owner 21 Nov 2026) — kartu paling atas Menu akun tablet, tampil HANYA saat orang yang jaga = orang pilihan owner
// (aturanToko/peran.ringkasOrang, diatur owner di Menu › Toko ini › Peran & persetujuan › Orang di tablet). Logika tanpa DOM, tidak menulis apa pun —
// dijaga alat-uji/uji_ringkas_tablet.py (jsc + kontrol).
//
// Keputusan owner 21 Nov 2026: data uang DIBUKA untuk akun tablet yang ditandai owner (rules v14 stafBacaUang; aksesAkun.bacaUang), tampil pakai PIN orang
// pilihan owner; isi = omzet, tunai / QRIS / bon, titipan, laci seharusnya & uang keluar PERSIS seperti di HP (rumus laci Tutup hari yang sama), per orang
// yang jaga, terlaris & stok tipis, pesanan & antar; bisa dicetak. Data uang dimuat firebase.js (setelDataUang) hanya selama orang itu jaga.
import { ambilPenjualan, ambilPiutangMutasi, ambilPesanan, ambilSuratJalan, kunciNota, returUangPerHari, ingatGerakanKas } from '../data/toko.js';
import { caraBayarKunci, AMBANG_HARI_KRITIS } from '../mesin/pembantu.js';
import { RP, KG, ANGKA, tanggalPendek, hariIniIso } from '../inti/format.js';
import { rumusLaci, tdNamaGerak } from './tutup-hari-logika.js';
import { tpMenungguSampai } from './titipan-logika.js';
import { ajCodBelumSetor } from './antar-logika.js';
import { daftarBarang } from './stok-logika.js';
import { ssAtur } from './sistem-logika.js';

export const RT_TERLARIS = 5;
export const RT_TIPIS = 6;

/** Kode orang pilihan owner yang membuka Ringkas hari ini ('' = mati). */
export const rtOrang = () => String((ssAtur('peran') || {}).ringkasOrang || '');
/** Kartu tampil untuk akun EFEKTIF ini? = akun staf aktif yang sedang dijaga orang pilihan owner (lewat PIN di "Siapa yang jaga?"). */
export function rtTampil(akun, orang) {
  const o = orang === undefined ? rtOrang() : String(orang || '');
  return !!akun && akun.jenis === 'aktif' && !!akun.operatorId && !!o && String(akun.operatorId) === o;
}
/** Data uang dimuat? Kartu tampil DAN akun tabletnya ditandai owner (bacaUang — dari aksesAkun, bukan dari orang yang jaga). */
export const rtBukaUang = (akun, orang) => rtTampil(akun, orang) && akun.bacaUang === true;

/** Keadaan data uang di perangkat ini. u = status.uang firebase.js ({ nyala, siap, total, ditolak }). */
export function rtKeadaanUang(akun, u) {
  if (!akun || akun.bacaUang !== true) return { st: 'mati', teks: 'Akun tablet ini belum ditandai owner untuk membaca data uang — laci & uang keluar tidak dihitung. Owner: Menu › Toko ini › Peran & persetujuan › Orang di tablet › Ringkas hari ini.' };
  const U = u || {};
  if ((U.ditolak || []).length) return { st: 'ditolak', teks: 'Server menolak data uang (' + U.ditolak.length + ' bagian) — aturan server v14 belum terbit atau tanda akun belum sampai. Laci & uang keluar tidak ditebak.' };
  if (!U.nyala || !(U.total > 0) || U.siap < U.total) return { st: 'muat', teks: 'Memuat data uang… ' + ANGKA(U.siap || 0) + ' dari ' + ANGKA(U.total || 0) + ' bagian' };
  return { st: 'siap', teks: '' };
}

const rtTambah = (peta, k, isi) => { if (!peta[k]) peta[k] = isi(); return peta[k]; };

/**
 * Hitung ringkas hari `kini` (tanggal perangkat). akun = akun efektif (orang yang jaga); u = status.uang. Hasil: semua angka kartu & cetakan.
 * Bagian uang (laci, uang keluar) hanya diisi bila data uangnya siap — selain itu null, BUKAN Rp0.
 */
export function rtHitung(kini, akun, u) {
  const iso = hariIniIso(kini); const K = rtKeadaanUang(akun, u);
  const jual = ambilPenjualan().filter((p) => p.tanggal === iso);
  const jumlah = (xs) => xs.reduce((a, p) => a + (Number(p.hargaTotal) || 0), 0);
  const tunai = jumlah(jual.filter((p) => caraBayarKunci(p) !== 'qris' && caraBayarKunci(p) !== 'kredit'));
  const qris = jumlah(jual.filter((p) => caraBayarKunci(p) === 'qris')); const bon = jumlah(jual.filter((p) => caraBayarKunci(p) === 'kredit'));
  const retur = Math.round(((returUangPerHari()[iso] || {}).uang) || 0);
  const bayar = ambilPiutangMutasi().filter((m) => m && m.tipe === 'bayar' && m.tanggal === iso && Number(m.nominal) > 0);
  const bonTunai = bayar.filter((m) => caraBayarKunci(m) !== 'qris').reduce((a, m) => a + (Number(m.nominal) || 0), 0);
  const bonQris = bayar.filter((m) => caraBayarKunci(m) === 'qris').reduce((a, m) => a + (Number(m.nominal) || 0), 0);
  // per orang yang jaga (nama tertulis di nota) · terlaris per barang (kg)
  const orang = {}; const barang = {};
  jual.forEach((p) => {
    const o = rtTambah(orang, String(p.oleh || '').trim() || 'tanpa nama', () => ({ nama: String(p.oleh || '').trim() || 'tanpa nama', nota: new Set(), rp: 0 }));
    o.nota.add(kunciNota(p)); o.rp += Number(p.hargaTotal) || 0;
    const nb = String(p.merkSumber || p.namaProduk || p.jenis || '').trim(); if (!nb) return;
    const b = rtTambah(barang, nb, () => ({ nama: nb, kg: 0, rp: 0 })); b.kg += Number(p.totalKg) || 0; b.rp += Number(p.hargaTotal) || 0;
  });
  const perOrang = Object.keys(orang).map((k) => ({ nama: orang[k].nama, nota: orang[k].nota.size, rp: Math.round(orang[k].rp) })).sort((a, b) => b.rp - a.rp || a.nama.localeCompare(b.nama));
  const terlaris = Object.keys(barang).map((k) => barang[k]).filter((b) => b.kg > 0).sort((a, b) => b.kg - a.kg || b.rp - a.rp).slice(0, RT_TERLARIS)
    .map((b) => ({ nama: b.nama, kg: Math.round(b.kg * 100) / 100, rp: Math.round(b.rp) }));
  let tipis = [];
  try {
    tipis = daftarBarang().filter((b) => !b.wadahStok && (b.sisa < -0.004 || (b.laju > 0 && b.hariHabis !== null && b.hariHabis <= AMBANG_HARI_KRITIS)))
      .sort((a, b) => (a.sisa < 0 ? -1 : a.hariHabis) - (b.sisa < 0 ? -1 : b.hariHabis)).slice(0, RT_TIPIS)
      .map((b) => ({ nama: b.nama, sisa: b.sisa, satuan: b.satuan === 'unit' ? 'unit' : 'kg', hari: b.hariHabis === null ? null : Math.max(0, Math.round(b.hariHabis * 10) / 10), minus: b.sisa < 0 }));
  } catch (e) { tipis = []; }
  // pesanan yang jatuh hari ini / sudah lewat & belum tuntas · surat jalan masih di jalan · bayar di tempat belum disetor
  const pesanan = (ambilPesanan() || []).filter((x) => x && ['dipesan', 'diantar'].indexOf(String(x.status || '')) >= 0 && String(x.tanggalKirim || '') && String(x.tanggalKirim) <= iso)
    .map((x) => ({ nama: String(x.namaPelanggan || '').trim() || 'tanpa nama', isi: String(x.isi || '').trim(), status: String(x.status), tanggal: String(x.tanggalKirim), lewat: String(x.tanggalKirim) < iso }))
    .sort((a, b) => a.tanggal.localeCompare(b.tanggal));
  const jalan = (ambilSuratJalan() || []).filter((x) => x && String(x.status || '') === 'berangkat')
    .map((x) => ({ no: String(x.noSJ || x.id || ''), nama: String(x.namaPelanggan || '').trim(), pengantar: String(x.pengantar || '').trim() }));
  let cod = []; try { cod = ajCodBelumSetor(iso) || []; } catch (e) { cod = []; }
  const T = tpMenungguSampai(iso);
  // uang (rules v14): rumus laci Tutup hari + semua uang keluar hari ini (kantong mana pun) dari gerakan kas mesin
  let laci = null; let keluar = null;
  if (K.st === 'siap') {
    const RL = rumusLaci(iso);
    laci = RL.ada ? { ada: true, awal: RL.awal, masuk: RL.masuk, keluar: RL.keluar, seharusnya: RL.seharusnya, titipan: T.rp, kira: RL.seharusnya - T.rp, baris: RL.baris.slice(1) }
      : { ada: false, teks: RL.teks };
    const grup = {};
    ingatGerakanKas().forEach((r) => { if (r.t !== iso || !(r.keluar > 0)) return; const g = rtTambah(grup, tdNamaGerak(r.label, -1), () => ({ nama: tdNamaGerak(r.label, -1), n: 0, rp: 0 })); g.n += 1; g.rp += r.keluar; });
    const daftar = Object.keys(grup).map((k) => grup[k]).sort((a, b) => b.rp - a.rp);
    keluar = { daftar, total: daftar.reduce((a, g) => a + g.rp, 0) };
  }
  return { iso, uang: K, omzet: tunai + qris + bon, nota: new Set(jual.map(kunciNota)).size, tunai, qris, bon, retur, bonTunai, bonQris, titipan: T, laci, keluar,
    perOrang, terlaris, tipis, pesanan, jalan, cod: cod.map((x) => ({ pengantar: x.pengantar || 'pengantar', rp: Math.round(Number(x.sisa) || 0) })) };
}

/** Teks cetak (printer struk tablet). R = rtHitung; kop = stAtur().kop; dicetak = { tanggal, jam, oleh }. */
export function rtTeksCetak(R, kop, dicetak) {
  const C = dicetak || {}; const g = []; const baris = (a, b) => g.push(a + '  ' + b);
  g.push('RINGKAS HARI INI ' + tanggalPendek(R.iso).toUpperCase() + (C.jam ? ' ' + C.jam : '')); if (kop && kop.nama) g.push(String(kop.nama).toUpperCase()); g.push('');
  baris('Omzet · ' + R.nota + ' nota', RP(R.omzet)); baris('  tunai', RP(R.tunai)); baris('  QRIS', RP(R.qris)); baris('  bon baru', RP(R.bon));
  if (R.retur) baris('Retur & refund', '-' + RP(R.retur));
  if (R.bonTunai || R.bonQris) { baris('Bon dibayar tunai', RP(R.bonTunai)); if (R.bonQris) baris('Bon dibayar QRIS', RP(R.bonQris)); }
  g.push('');
  if (R.laci && R.laci.ada) {
    baris('Laci semalam', RP(R.laci.awal)); baris('  + masuk laci', RP(R.laci.masuk)); baris('  - keluar laci', RP(R.laci.keluar)); baris('Seharusnya di laci', RP(R.laci.seharusnya));
    if (R.laci.titipan) baris('  - titipan blm diputus', RP(R.laci.titipan));
    baris('PERKIRAAN ISI LACI', RP(R.laci.kira));
  } else g.push(R.laci ? 'Laci: ' + R.laci.teks : 'Laci: data uang belum terbaca');
  if (R.keluar) { g.push(''); g.push('Uang keluar hari ini ' + RP(R.keluar.total)); R.keluar.daftar.forEach((x) => baris('  ' + x.nama + (x.n > 1 ? ' (' + x.n + ')' : ''), RP(x.rp))); }
  if (R.titipan.n) baris('Titipan tablet menunggu ' + R.titipan.n, RP(R.titipan.rp));
  if (R.perOrang.length) { g.push(''); g.push('Per orang'); R.perOrang.forEach((o) => baris('  ' + o.nama + ' · ' + o.nota + ' nota', RP(o.rp))); }
  if (R.terlaris.length) { g.push(''); g.push('Terlaris'); R.terlaris.forEach((b) => baris('  ' + b.nama, KG(b.kg))); }
  if (R.tipis.length) { g.push(''); g.push('Stok tipis'); R.tipis.forEach((b) => baris('  ' + b.nama, b.minus ? 'MINUS ' + (b.satuan === 'kg' ? KG(b.sisa) : ANGKA(b.sisa) + ' unit') : '±' + String(b.hari).replace('.', ',') + ' hari')); }
  if (R.pesanan.length || R.jalan.length || R.cod.length) {
    g.push(''); R.pesanan.forEach((x) => g.push((x.lewat ? 'LEWAT ' : 'Pesanan ') + x.nama + (x.isi ? ': ' + x.isi : '') + (x.status === 'diantar' ? ' (diantar)' : '')));
    if (R.jalan.length) g.push('Surat jalan di jalan: ' + R.jalan.length); R.cod.forEach((x) => baris('Bayar di tempat blm setor · ' + x.pengantar, RP(x.rp)));
  }
  g.push(''); g.push('Dicetak ' + tanggalPendek(C.tanggal || R.iso) + (C.jam ? ' ' + C.jam : '') + (C.oleh ? ', ' + C.oleh : ''));
  return g.join('\n');
}
