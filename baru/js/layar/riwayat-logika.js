// RIWAYAT PENJUALAN (owner 28 Sep 2026: "buatkan seluruh riwayat penjualan") — Jual › tab Riwayat. Baca saja; dua tindakan per nota yang sudah ada jalurnya:
// buka struk (lembar struk, struk-logika notaDari) dan retur nota ini (jalur Retur, tunjukNota) untuk baris karung/kemasan yang boleh kembali (rtDasarRetur —
// aturan rtDasarNota; audit 39b no. 37: nota BON ikut, returnya memotong bon).
// Satu nota = baris-baris dengan kunci yang SAMA dengan panel "Hari ini" (grupNota → trxId → id). Nota berlaku = baris yang belum dibatalkan / belum digantikan
// rincian (penjualanMasihBerlaku, mesin laba memakai aturan yang sama); total nota = Σ hargaTotal baris berlaku (= panel "Hari ini"). Omzet LAPORAN = total nota − uang
// retur hari itu (hitungLabaRentang.omzetPenuh) — riwayat menyebut keduanya selama tidak ada saringan jenis/cara/cari. Nota batal / dirinci hanya tampil bila diminta.
// Tanpa DOM; nama berawalan rw (bundel uji satu lingkup). Dijaga alat-uji/uji_riwayat_penjualan.py.
import { ambilPenjualanSemua, ambilRetur } from '../data/toko.js';
import { penjualanMasihBerlaku, bakuCaraBayar, uangKembaliRetur } from '../mesin/pembantu.js';
import { rtDasarRetur } from './retur-logika.js';
import { hariIniIso, RP } from '../inti/format.js';
import { gabungTakaran } from './struk-logika.js';

export const RW_LANGKAH = 50;   // nota per halaman; "muat lagi" menambah sebanyak ini
export const RW_PERIODE = [['hari', 'Hari ini'], ['7', '7 hari'], ['30', '30 hari'], ['bulan', 'Bulan ini'], ['semua', 'Semua']];
export const RW_JENIS = [['', 'Semua jenis'], ['karung', 'Karung'], ['kemasan', 'Kemasan'], ['literan', 'Literan'], ['repacking', 'Repack'], ['wadah', 'Wadah'], ['karcis', 'Karcis kasir']];
export const RW_CARA = [['', 'Semua cara'], ['Tunai', 'Tunai'], ['QRIS', 'QRIS'], ['Kredit', 'Bon']];
const RW_HARI = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
const RW_BLN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
export const RW_KARCIS = 'kasir_darurat_nominal';
export const rwKunci = (p) => String(p.grupNota || p.trxId || p.id);
const rwUrutId = (a, b) => (Number(a.id) || 0) - (Number(b.id) || 0) || String(a.id).localeCompare(String(b.id));
const rwAngka = (n) => String(Math.round((Number(n) || 0) * 100) / 100).replace('.', ',');
function rwGeser(iso, n) { const d = new Date(iso + 'T00:00:00'); d.setDate(d.getDate() + n); return hariIniIso(d); }
/** "Senin 28 Sep 2026" */
export function rwTanggalPanjang(iso) { const d = new Date(String(iso) + 'T00:00:00'); if (isNaN(d.getTime())) return String(iso || ''); return RW_HARI[d.getDay()] + ' ' + d.getDate() + ' ' + RW_BLN[d.getMonth()] + ' ' + d.getFullYear(); }

/** Teks satu baris tampil (baris internal satu takaran wadah sudah digabung). */
export function rwTeksBaris(p) {
  if (p.jenis === RW_KARCIS) return p.asalDarurat ? 'Karcis kasir — sisa yang belum diurai' : 'Karcis kasir — nominal, belum dirinci';
  if (p.jenis === 'kemasan') return (p.namaProduk || '') + ' ' + rwAngka(p.ukuranKemasan) + ' kg × ' + (p.jumlahUnit || 0) + (p.bonusUnit ? ' + bonus ' + p.bonusUnit : '');
  if (p.jenis === 'karung') return (p.merkSumber || '') + ' karung ' + (p.beratKarungAcuan || 50) + ' kg × ' + rwAngka(p.jumlahKarung);
  if (p.jenis === 'literan') return (p.dariWadah || p.merkSumber || '') + ' ' + rwAngka(p.jumlahLiter) + ' L';
  if (p.jenis === 'repacking') return 'Repack ' + (p.namaProduk || p.merkSumber || '') + ' ' + rwAngka(p.totalKg) + ' kg';
  if (p.jenis === 'wadah') return (p.namaProduk || 'Wadah') + ' × ' + (p.jumlahUnit || 0) + ' lembar';
  return p.namaProduk || p.jenis || 'Penjualan';
}
const rwJenisBaris = (p) => (p.jenis === RW_KARCIS ? 'karcis' : String(p.jenis || ''));

/** SEMUA nota sejak awal (terbaru dulu): { kunci, trxId, grupNota, id, tanggal, jam, nama, cara, total, kg, status, baris[], jenis{}, … }. */
export function rwSemuaNota() {
  const per = {}; const urut = [];
  ambilPenjualanSemua().forEach((p) => { const k = rwKunci(p); if (!per[k]) { per[k] = []; urut.push(k); } per[k].push(p); });
  return urut.map((k) => {
    const rows = per[k].slice().sort(rwUrutId); const hidup = rows.filter(penjualanMasihBerlaku); const p0 = hidup[0] || rows[0];
    const status = hidup.length === rows.length ? 'berlaku' : hidup.length ? 'sebagian' : rows.some((x) => x.dibatalkan) ? 'batal' : 'dirinci';
    const tampil = gabungTakaran(hidup.length ? hidup : rows);
    const baris = tampil.map((p) => { const d = p.jenis === 'karung' || p.jenis === 'kemasan' ? rtDasarRetur(p) : { ok: false };
      const hidupBaris = status !== 'batal' && status !== 'dirinci' && !p.penggantiRetur;
      return { id: String(p.id), teks: rwTeksBaris(p), n: Math.round(p.hargaTotal || 0), jenis: rwJenisBaris(p), bisaRetur: hidupBaris && !!(d && d.ok),
        sebabRetur: hidupBaris && (p.jenis === 'karung' || p.jenis === 'kemasan') && d && !d.ok ? String(d.sebab || '') : '', tandai: !!p.perluCocokkan, pengganti: !!p.penggantiRetur }; });
    const jenis = {}; tampil.forEach((p) => { jenis[rwJenisBaris(p)] = true; });
    const total = hidup.reduce((a, p) => a + (p.hargaTotal || 0), 0);
    return { kunci: k, trxId: p0.trxId || null, grupNota: p0.grupNota || null, id: String(p0.id), tanggal: String(p0.tanggal || ''), jam: String(p0.jam || ''), nama: String(p0.namaPelanggan || '').trim(),
      cara: bakuCaraBayar(p0.caraBayar), oleh: String(p0.oleh || p0.operator || '').trim(), total: Math.round(total), totalAsli: Math.round(rows.reduce((a, p) => a + (p.hargaTotal || 0), 0)),
      kg: Math.round(hidup.reduce((a, p) => a + (Number(p.totalKg) || 0), 0) * 100) / 100, status, baris, jenis, karcis: !!jenis.karcis, tandai: baris.some((b) => b.tandai),
      bisaRetur: baris.some((b) => b.bisaRetur), nBaris: baris.length };
  }).sort((a, b) => (b.tanggal + ' ' + b.jam).localeCompare(a.tanggal + ' ' + a.jam) || (Number(b.id) || 0) - (Number(a.id) || 0));
}

/** Rentang periode → { dari, sampai } (iso, inklusif); 'semua' → dari ''. */
export function rwRentang(periode, kini) {
  const hari = hariIniIso(kini || new Date());
  if (periode === 'hari') return { dari: hari, sampai: hari };
  if (periode === '7') return { dari: rwGeser(hari, -6), sampai: hari };
  if (periode === '30') return { dari: rwGeser(hari, -29), sampai: hari };
  if (periode === 'bulan') return { dari: hari.slice(0, 8) + '01', sampai: hari };
  return { dari: '', sampai: hari };
}
const rwCocokCari = (o, kata) => { const hay = (o.nama + ' ' + o.baris.map((b) => b.teks).join(' ') + ' ' + o.cara + ' ' + o.kunci.slice(-6)).toLowerCase(); const digit = String(o.total);
  return kata.every((w) => { const d = w.replace(/[^\d]/g, ''); return hay.indexOf(w) >= 0 || (d.length >= 3 && d === w.replace(/[.,]/g, '') && digit.indexOf(d) >= 0); }); };

/**
 * Riwayat yang tampil: s = { rwCari, rwPeriode, rwJenis, rwCara, rwBatal, rwN }. Hasil: nota yang cocok (terbaru dulu, dipotong rwN), dikelompokkan per hari
 * (omzet & jumlah nota per hari dihitung dari SEMUA nota yang cocok hari itu, bukan cuma yang tergambar), ringkasan semua yang cocok, dan kalimat saringan.
 */
export function rwSusun(s, kini) {
  const S = s || {}; const periode = RW_PERIODE.some((x) => x[0] === S.rwPeriode) ? S.rwPeriode : 'semua'; const R = rwRentang(periode, kini);
  const kata = String(S.rwCari || '').toLowerCase().split(/\s+/).filter(Boolean); const n = Math.max(RW_LANGKAH, Number(S.rwN) || RW_LANGKAH);
  const semua = rwSemuaNota();
  const cocok = semua.filter((o) => (!R.dari || o.tanggal >= R.dari) && o.tanggal <= R.sampai && (!S.rwJenis || o.jenis[S.rwJenis]) && (!S.rwCara || o.cara === S.rwCara)
    && (S.rwBatal || o.status === 'berlaku' || o.status === 'sebagian') && (!kata.length || rwCocokCari(o, kata)));
  const hidup = cocok.filter((o) => o.status === 'berlaku' || o.status === 'sebagian');
  const perCara = {}; hidup.forEach((o) => { perCara[o.cara] = (perCara[o.cara] || 0) + o.total; });
  const perHari = {}; cocok.forEach((o) => { const h = perHari[o.tanggal] = perHari[o.tanggal] || { nota: 0, omzet: 0 }; if (o.status === 'berlaku' || o.status === 'sebagian') { h.nota += 1; h.omzet += o.total; } });
  // uang retur per hari (rumus mesin laba: uangKembaliRetur) — hanya bermakna bila yang dijumlah SEMUA nota hari itu (tanpa saringan jenis/cara/cari)
  const bersihBisa = !S.rwJenis && !S.rwCara && !kata.length; const returHari = {}; if (bersihBisa) ambilRetur().forEach((r) => { const t = String(r.tanggal || ''); if ((!R.dari || t >= R.dari) && t <= R.sampai) returHari[t] = (returHari[t] || 0) + uangKembaliRetur(r); });
  const returTotal = Object.keys(returHari).reduce((a, t) => a + returHari[t], 0);
  const tampil = cocok.slice(0, n); const hari = [];
  tampil.forEach((o) => { let g = hari[hari.length - 1]; if (!g || g.tanggal !== o.tanggal) { const rt = bersihBisa ? Math.round(returHari[o.tanggal] || 0) : null; g = { tanggal: o.tanggal, judul: rwTanggalPanjang(o.tanggal), nota: [], nNota: perHari[o.tanggal].nota, omzet: Math.round(perHari[o.tanggal].omzet), retur: rt, bersih: rt === null ? null : Math.round(perHari[o.tanggal].omzet) - rt }; hari.push(g); } g.nota.push(o); });
  const saring = [periode !== 'semua' ? (RW_PERIODE.find((x) => x[0] === periode) || [])[1] : '', S.rwJenis ? (RW_JENIS.find((x) => x[0] === S.rwJenis) || [])[1] : '', S.rwCara ? (RW_CARA.find((x) => x[0] === S.rwCara) || [])[1] : '',
    kata.length ? '"' + String(S.rwCari).trim() + '"' : '', S.rwBatal ? 'termasuk batal / sudah dirinci' : ''].filter(Boolean);
  const awal = semua.length ? semua[semua.length - 1].tanggal : '';
  return { hari, n: cocok.length, nTampil: tampil.length, lebih: cocok.length > tampil.length, omzet: Math.round(hidup.reduce((a, o) => a + o.total, 0)), nBerlaku: hidup.length, perCara, periode, rentang: R,
    retur: bersihBisa ? Math.round(returTotal) : null, bersih: bersihBisa ? Math.round(hidup.reduce((a, o) => a + o.total, 0) - returTotal) : null,
    ringkas: cocok.length + ' nota' + (hidup.length !== cocok.length ? ' (' + hidup.length + ' berlaku)' : '') + ' · total nota ' + RP(Math.round(hidup.reduce((a, o) => a + o.total, 0)))
      + (bersihBisa && returTotal ? ' − retur ' + RP(Math.round(returTotal)) + ' = omzet ' + RP(Math.round(hidup.reduce((a, o) => a + o.total, 0) - returTotal)) : '') + (Object.keys(perCara).length ? ' · ' + ['Tunai', 'QRIS', 'Kredit'].filter((c) => perCara[c]).map((c) => (c === 'Kredit' ? 'Bon' : c) + ' ' + RP(Math.round(perCara[c]))).join(' · ') : ''),
    saringTeks: saring.length ? 'Saringan: ' + saring.join(' · ') : 'Semua nota sejak ' + (awal ? rwTanggalPanjang(awal) : 'awal'), kosong: !cocok.length ? (semua.length ? 'Tidak ada nota yang cocok dengan saringan ini.' : 'Belum ada penjualan tercatat.') : '' };
}
