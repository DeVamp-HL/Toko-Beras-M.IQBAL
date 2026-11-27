// DASBOR OWNER — SUSUNAN KARTU & WIDGET (owner 26 Nov 2026, sensus ulang 1c B88/B89 + tata letak). Logika tanpa DOM, awalan wg.
//
// Jalan keputusan owner (26 Nov 2026, empat pratinjau): angka utama = widget yang owner atur sendiri ("Seperti halnya menambahkan widget di layar HP") →
// "Tampilan saat ini yang paling penting. Yang sekarang sedang lu kerjakan cuma opsi tambahan." → desain ulang kartu ringkas DITOLAK ("Jelek. Bagusan seperti
// semula") → Perlu perhatian disembunyikan → "Gak rapet. … besar kecilnya kartu bisa gua sesuaikan seperti screenshot 3 (kotak berpegangan). Jadi fleksibel gua
// menyesuaikan ruang. Bukan hanya klik jadi besar atau kecil." + "Merapat otomatis" + "HP satu kolom".
// Maka: kartu lama Dasbor TETAP UTUH isinya, tapi tiap kartu (dan widget tambahan) = panel di kisi 12 kolom: LEBAR w (kolom) & TINGGI h (baris 8 px; null =
// setinggi isinya) ditarik bebas lewat pegangan; kisi merapat otomatis (CSS grid dense). HP: satu kolom, urutan sama, tinggi ikut isi.
// Susunan = setelan aturanToko/dasbor { widget: [{ id, w, h }] } (owner saja; ikut ke semua perangkat owner). Belum pernah diatur = BAWAAN = urutan kartu lama.
// ATURAN: TIDAK ADA RUMUS UANG di sini. Widget-angka & kartu tambahan membaca hasil dasbor-logika (susunDasbor + dbTambahan) APA ADANYA (uji_dasbor_sensus
// memeriksa tiap widget menutup ke kartunya). Kartu lama digambar dasbor.js apa adanya.
import { RP, DESIMAL, ANGKA } from '../inti/format.js';
import { cacheMentah } from '../data/toko.js';

export const WG_ID = 'dasbor';
export const WG_KOLOM = 12;       // kisi Mac / tablet: 12 kolom
export const WG_BARIS_PX = 8;     // satu baris kisi = 8 px (tinggi kartu ditarik per 8 px)
export const WG_H_MIN = 10, WG_H_MAKS = 250;   // tinggi yang ditarik: 80 px – 2.000 px (null = setinggi isinya)
const WG_LEBAR_UKURAN = { kecil: 3, lebar: 6, besar: 6, penuh: 12 };   // ukuran lama (kecil/lebar/besar/penuh) → kolom
export const WG_MAKS = 64;   // di atas jumlah katalog (semua widget boleh terpasang sekaligus) — P1 (27 Nov 2026): 48 → 64, katalog kini > 48 (dijaga uji_kpi_kg)
const wgRpPendek = (n) => { const a = Math.abs(n || 0); const s = n < 0 ? '−' : ''; return a >= 1e6 ? s + 'Rp' + DESIMAL(Math.round(a / 1e5) / 10) + ' jt' : a >= 1e3 ? s + 'Rp' + Math.round(a / 1e3) + ' rb' : s + 'Rp' + Math.round(a); };
const wgPct = (x) => (x === null || x === undefined || !isFinite(x) ? '—' : (x < 0 ? '−' : x > 0 ? '+' : '') + DESIMAL(Math.round(Math.abs(x) * 10) / 10) + '%');
const wgPctPolos = (x) => (x === null || x === undefined || !isFinite(x) ? '—' : (x < 0 ? '−' : '') + DESIMAL(Math.round(Math.abs(x) * 10) / 10) + '%');
const wgGalat = (nama, X) => ({ nilai: 'gagal dihitung', ket: String(X && X.galat ? X.galat : 'kelompoknya tidak ada').slice(0, 120), awas: true, rinci: [], tujuan: null });
const ada = (X) => X && !X.galat;
const bandingTeks = (B) => (!B ? '' : !B.ada ? B.nama + ': ' + B.ket : B.pct === null ? B.nama + ' ' + RP(B.omzet) : wgPct(B.pct) + ' vs ' + B.nama + ' (' + wgRpPendek(B.omzet) + ')');

/**
 * WIDGET-KARTU TAMBAHAN: isi(D) = versi RINGKAS (angka besar + 2–3 baris) dari kelompok dasbor yang SAMA; Enam bulan utuh = kartu Enam bulan (dasbor.js), ketuk =
 * utuh. kPerhatian membaca D.perhatian (daftar Perlu perhatian Ringkasan — kartunya disembunyikan dari mode Dasbor, owner 26 Nov 2026: "ganggu").
 * kHeadline & kPeriode digambar khusus oleh layar (isinya dari dbHeadline / dbPeriode).
 */
function WG_KARTU() {
  const K = (id, nama, kel, ukuran, isi, x) => Object.assign({ id, nama, kel, ukuran, jenis: 'kartu', isi }, x || {});
  const LAMA = (id, nama, kel, w) => ({ id, nama, kel, ukuran: w === 12 ? 'penuh' : 'lebar', w, jenis: 'lama', isi: () => ({}) });   // kartu lama Dasbor: digambar dasbor.js utuh
  return [
    LAMA('kHari', 'Hari ini', 'hari', 6), LAMA('kKpi', 'Margin & target', 'kpi', 6), LAMA('kTren', 'Omzet & laba kotor', 'tren', 12), LAMA('kBulan', 'Bulan ini', 'bulan', 6),
    LAMA('kPemicu', 'Pemicu biaya yang naik', 'bulan', 6), LAMA('kStok', 'Stok per merek', 'stok', 6), LAMA('kPondasi', 'Pondasi toko', 'pondasi', 6), LAMA('kWadah', 'Wadah literan', 'stok', 6),
    LAMA('kTagihan', 'Piutang & utang pemasok', 'tagihan', 6), LAMA('kMutu', 'Mutu usaha', 'mutu', 6), LAMA('kB2b', 'Pelanggan usaha', 'b2b', 6),
    LAMA('kBeli', 'Pembelian', 'beli', 6),   // B68 (owner 27 Nov 2026): grafik pembelian per hari · minggu · bulan (dasbor.js kartuBeli)
    K('kPerhatian', 'Perlu perhatian', 'perhatian', 'lebar', (D) => { const P = (D.perhatian || []).filter((x) => x && x.teks);
      return { nilai: P.length ? P.length + ' hal' : 'tidak ada', ket: P.length ? 'yang merah didahulukan' : 'tidak ada bon, utang, stok, atau pesanan yang menunggu', awas: P.some((x) => x.awas),
        baris: P.slice().sort((a, b) => (b.awas ? 1 : 0) - (a.awas ? 1 : 0)).slice(0, 4).map((x) => [x.teks, x.nilai || '']), tujuan: null }; }),
    K('kHeadline', 'Ringkas hari ini', 'headline', 'penuh', () => ({ nilai: '', ket: '', baris: [], tujuan: null }), { khusus: true }),
    K('kPeriode', 'Periode (saringan tanggal)', 'periode', 'penuh', () => ({ nilai: '', ket: '', baris: [], tujuan: null }), { khusus: true }),
    // P1 (owner 27 Nov 2026, B7 · B6 · B133): terlaris menurut omzet Rp (rentang saringan; bawaan bulan ini) & tren per merek per minggu — kelompok dasbor `kg` apa adanya
    K('kTerlaris', 'Terlaris (omzet Rp)', 'kg', 'lebar', (D) => { const G = D.kg; if (!ada(G)) return wgGalat('kg', G); const T = G.terlaris; if (!ada(T)) return wgGalat('terlaris', T);
      if (T.diarsip) return { nilai: '—', ket: T.kalimat, awas: false, baris: [], tujuan: G.tujuan };
      const a = T.daftar[0]; return { nilai: a ? a.merek : 'belum ada jualan', ket: G.periodeNama + ' · ' + T.n + ' merek · omzet ' + wgRpPendek(T.total) + (T.menutup ? '' : ' · TIDAK MENUTUP ke mesin — laporkan'), awas: !T.menutup,
        baris: T.daftar.map((g, i) => [(i + 1) + '. ' + g.merek, wgRpPendek(g.omzet) + ' · ' + wgPctPolos(g.porsi) + (g.marginKg !== null ? ' · ' + wgRpPendek(g.marginKg) + '/kg' : '')]), tujuan: G.tujuan }; }, { ikut: true }),
    K('kTrenMerek', 'Tren per merek · mingguan', 'kg', 'lebar', (D) => { const G = D.kg; if (!ada(G)) return wgGalat('kg', G); const M = G.tren; if (!ada(M)) return wgGalat('tren merek', M);
      if (M.diarsip) return { nilai: '—', ket: M.kalimat, awas: false, baris: [], tujuan: G.tujuan }; const t = M.toko;
      return { nilai: RP(t.omzet), ket: 'minggu ini · ' + (t.omzetPct === null ? 'minggu lalu belum ada' : wgPct(t.omzetPct) + ' ' + (M.berjalan ? 'vs minggu lalu s.d. hari yang sama' : 'vs minggu lalu')) + (t.marginKg !== null ? ' · untung ' + wgRpPendek(t.marginKg) + '/kg' : ''),
        awas: !M.menutup, tren: M.deret.map((x) => ({ label: x.label, n: x.omzet, berjalan: x.berjalan })),
        baris: M.merek.slice(0, 5).map((g) => [g.merek, wgRpPendek(g.omzet) + ' · ' + (g.baru ? 'baru' : g.hilang ? 'tidak laku minggu ini' : wgPct(g.omzetPct))]), tujuan: G.tujuan }; }),
    K('kEnam', 'Enam bulan', 'enam', 'penuh', (D) => { const E = D.enam; if (!ada(E)) return wgGalat('enam', E); const b = E.bulan.filter((x) => !x.tanpaCatatan); const a = b[b.length - 1];
      return { nilai: a ? RP(a.labaBersih) : '—', ket: 'laba bersih ' + (a ? a.pendek + (a.berjalan ? ' (berjalan)' : '') : '') + ' · 6 bulan', awas: !!a && a.labaBersih < 0,
        tren: E.bulan.map((x) => ({ label: x.pendek, n: x.tanpaCatatan ? null : x.labaBersih, berjalan: x.berjalan })), baris: [['Biaya bulan ini', a ? RP(a.semuaBiaya) : '—']], tujuan: E.tujuan }; }),
  ];
}
/** KATALOG widget: id → { nama, ukuran (bawaan), sumber (kelompok dasbor), isi(D) → { nilai, ket, awas, lampu?, rinci: [[kata, nilai]], tren?: [{ label, n, berjalan }], tujuan } }. */
export const WG_KATALOG = [
  { id: 'omzetHari', nama: 'Omzet hari ini', ukuran: 'lebar', kel: 'banding', isi: (D) => { const B = D.banding; if (!ada(B)) return wgGalat('banding', B);
    return { nilai: RP(B.omzet), ket: [bandingTeks(B.kemarin), bandingTeks(B.mingguLalu)].filter(Boolean).join(' · '), awas: B.kemarin.ada && B.kemarin.pct !== null && B.kemarin.pct < 0,
      rinci: [['Omzet sampai ' + B.jam, RP(B.omzet) + ' · ' + B.nota + ' nota'], ['Kemarin jam segini', B.kemarin.ada ? RP(B.kemarin.omzet) + ' · ' + B.kemarin.nota + ' nota · ' + wgPct(B.kemarin.pct) : B.kemarin.ket],
        [B.mingguLalu.nama.charAt(0).toUpperCase() + B.mingguLalu.nama.slice(1) + ' jam segini', B.mingguLalu.ada ? RP(B.mingguLalu.omzet) + ' · ' + B.mingguLalu.nota + ' nota · ' + wgPct(B.mingguLalu.pct) : B.mingguLalu.ket]], tujuan: B.tujuan }; } },
  { id: 'labaKotorHari', nama: 'Laba kotor hari ini', ukuran: 'kecil', kel: 'hari', isi: (D) => { const H = D.hari; if (!ada(H)) return wgGalat('hari', H);
    return { nilai: RP(H.margin), ket: H.tanpaHpp ? H.tanpaHpp + ' baris tanpa modal tidak ikut' : 'semua baris bermodal', awas: H.margin < 0, rinci: [['Omzet', RP(H.omzet)], ['Laba kotor', RP(H.margin)]], tujuan: H.tujuan }; } },
  { id: 'notaHari', nama: 'Nota & rata-rata hari ini', ukuran: 'kecil', kel: 'banding', isi: (D) => { const B = D.banding; if (!ada(B)) return wgGalat('banding', B);
    return { nilai: B.rata === null ? 'belum ada nota' : RP(Math.round(B.rata)), ket: B.nota + ' nota' + (B.kemarin.ada && B.kemarin.rata ? ' · kemarin jam segini ' + wgRpPendek(B.kemarin.rata) + '/nota' : ''), awas: false,
      rinci: [['Rata-rata nilai nota', B.rata === null ? '—' : RP(Math.round(B.rata))], ['Nota', String(B.nota)], ['Cara hitung', B.rumusRata]], tujuan: B.tujuan }; } },
  { id: 'uangToko', nama: 'Uang toko sekarang', ukuran: 'kecil', kel: 'hari', isi: (D) => { const H = D.hari; if (!ada(H)) return wgGalat('hari', H); const K = H.kas;
    if (!K.ada) return { nilai: 'belum bisa', ket: 'titik kas belum disetel — Tutup hari malam ini', awas: true, rinci: [], tujuan: H.kasTujuan };
    return { nilai: RP(K.total), ket: K.tempat.filter((t) => Math.abs(t.n) > 0.5).map((t) => t.nama + ' ' + wgRpPendek(t.n)).join(' · ') || '4 tempat kosong', awas: K.minus.length > 0 || !K.cocok,
      rinci: K.tempat.map((t) => [t.nama, RP(t.n)]).concat([['Dihitung dari', K.titik]]), tujuan: H.kasTujuan }; } },
  { id: 'targetHari', nama: 'Target omzet hari ini', ukuran: 'kecil', kel: 'kpi', isi: (D) => { const Q = D.kpi; if (!ada(Q) || !ada(Q.target)) return wgGalat('kpi', ada(Q) ? Q.target : Q); const T = Q.target;
    if (T.lampu === 'tanpa') return { nilai: 'belum ada', ket: T.teks, awas: false, rinci: [], tujuan: T.tujuan };
    return { nilai: wgRpPendek(T.omzet), ket: 'target ' + wgRpPendek(T.target) + ' · ' + T.teks, awas: T.lampu === 'merah', lampu: T.lampu, bilah: T.target > 0 ? Math.max(0, Math.min(1, T.omzet / T.target)) : 0,
      rinci: [['Omzet', RP(T.omzet)], ['Target', RP(T.target)], ['Seharusnya sampai jam ini', RP(T.laju)]], tujuan: T.tujuan }; } },
  { id: 'omzetBulan', nama: 'Omzet bulan ini', ukuran: 'kecil', kel: 'banding', isi: (D) => { const B = D.banding; if (!ada(B)) return wgGalat('banding', B); const M = B.bulan;
    return { nilai: RP(M.ini.omzet), ket: M.lalu.ada ? wgPct(M.pctOmzet) + ' vs ' + M.namaLalu.split(' ')[0] + ' s.d. tgl ' + Number(M.sampaiLalu.slice(8, 10)) : M.lalu.ket, awas: M.pctOmzet !== null && M.pctOmzet < 0,
      rinci: [[M.nama, RP(M.ini.omzet) + ' · ' + M.ini.nota + ' nota']].concat(M.lalu.ada ? [[M.namaLalu + ' s.d. tanggal ' + Number(M.sampaiLalu.slice(8, 10)), RP(M.lalu.omzet) + ' · ' + M.lalu.nota + ' nota']] : []), tujuan: M.tujuan }; } },
  { id: 'labaBersihBulan', nama: 'Laba bersih bulan ini', ukuran: 'lebar', kel: 'bulan', isi: (D) => { const B = D.bulan; if (!ada(B)) return wgGalat('bulan', B);
    if (B.tanpaCatatan) return { nilai: 'belum ada catatan', ket: B.nama, awas: false, rinci: [], tujuan: B.labaTujuan }; const I = B.impas;
    return { nilai: RP(I.labaSampai), ket: 'sampai hari ini · ' + (I.menutup ? 'biaya sudah tertutup margin kotor' : 'biaya masih ' + wgRpPendek(I.kurang) + ' lebih besar dari margin kotor (belum impas)') + ' · sebulan ' + wgRpPendek(B.labaBersih), awas: !I.menutup,
      bilah: I.omzetImpas ? Math.max(0, Math.min(1, B.omzetHitung / I.omzetImpas)) : null,
      rinci: [['Laba bersih sampai hari ini', RP(I.labaSampai)], ['Laba bersih ' + B.nama + ' (tagihan sebulan penuh)', RP(B.labaBersih)], ['Omzet titik impas sebulan', I.omzetImpas === null ? '—' : RP(I.omzetImpas)]], tujuan: B.labaTujuan }; } },
  { id: 'biayaBulan', nama: 'Biaya bulan ini', ukuran: 'kecil', kel: 'bulan', isi: (D) => { const B = D.bulan; if (!ada(B)) return wgGalat('bulan', B);
    return { nilai: RP(B.semuaBiaya), ket: B.nLampu ? [B.merah ? B.merah + ' lewat' : '', B.amber ? B.amber + ' mendekati' : '', B.hijau ? B.hijau + ' aman' : ''].filter(Boolean).join(' · ') : 'anggaran belum diatur', awas: B.merah > 0,
      rinci: B.biaya.slice(0, 6).map((r) => [r.nama, RP(r.n)]), tujuan: B.tujuan }; } },
  { id: 'marginBulan', nama: 'Margin bulan ini', ukuran: 'kecil', kel: 'kpi', isi: (D) => { const Q = D.kpi; if (!ada(Q) || !ada(Q.margin)) return wgGalat('kpi', ada(Q) ? Q.margin : Q); const M = Q.margin;
    const tg = (id) => M.tangga.find((x) => x.id === id) || { pct: null };
    return { nilai: wgPctPolos(tg('kotor').pct), ket: 'kotor · usaha ' + wgPctPolos(tg('usaha').pct) + ' · bersih ' + wgPctPolos(tg('bersih').pct), awas: tg('bersih').pct !== null && tg('bersih').pct < 0,
      rinci: M.tangga.map((r) => [r.nama, wgPctPolos(r.pct)]), tujuan: Q.tujuan }; } },
  { id: 'rataBulan', nama: 'Rata-rata nota bulan ini', ukuran: 'kecil', kel: 'banding', isi: (D) => { const B = D.banding; if (!ada(B)) return wgGalat('banding', B); const M = B.bulan;
    return { nilai: M.ini.rata === null ? 'belum ada nota' : RP(Math.round(M.ini.rata)), ket: M.ini.nota + ' nota' + (M.lalu.ada && M.lalu.rata ? ' · ' + wgPct(M.pctRata) + ' vs ' + M.namaLalu.split(' ')[0] : ''), awas: false,
      rinci: [[M.nama, M.ini.rata === null ? '—' : RP(Math.round(M.ini.rata)) + ' · ' + M.ini.nota + ' nota']].concat(M.lalu.ada ? [[M.namaLalu + ' s.d. tgl ' + Number(M.sampaiLalu.slice(8, 10)), M.lalu.rata ? RP(Math.round(M.lalu.rata)) + ' · ' + M.lalu.nota + ' nota' : '—']] : []).concat([['Cara hitung', B.rumusRata]]), tujuan: M.tujuan }; } },
  { id: 'piutangLewat', nama: 'Piutang lewat jatuh tempo', ukuran: 'kecil', kel: 'tagihan', isi: (D) => { const G = D.tagihan; if (!ada(G)) return wgGalat('tagihan', G); const P = G.piutang; const N = P.nota;
    if (!N || N.galat) return { nilai: RP(P.rpJatuh), ket: P.nJatuh + ' nama jatuh tempo', awas: P.nJatuh > 0, rinci: [], tujuan: P.tujuan };
    return { nilai: RP(N.lewat), ket: N.nLewat + ' nota · ' + N.orangLewat + ' orang · hari ini ' + wgRpPendek(N.hariIni), awas: N.lewat > 0,
      rinci: [['Lewat jatuh tempo', RP(N.lewat)], ['Jatuh tempo hari ini', RP(N.hariIni)], ['7 hari ke depan', RP(N.minggu)], ['Semua piutang', RP(P.total)]], tujuan: P.notaTujuan }; } },
  { id: 'piutangTotal', nama: 'Piutang pelanggan', ukuran: 'kecil', kel: 'tagihan', isi: (D) => { const G = D.tagihan; if (!ada(G)) return wgGalat('tagihan', G); const P = G.piutang;
    return { nilai: RP(P.total), ket: P.n + ' nama' + (P.kg && P.kg.teks ? ' · ' + P.kg.teks : ''), awas: false, rinci: P.perStatus.filter((s) => s.n).map((s) => [s.kata + ' · ' + s.n, RP(s.rp)]), tujuan: P.tujuan }; } },
  { id: 'bonPemasok', nama: 'Bon pemasok jatuh tempo', ukuran: 'kecil', kel: 'tagihan', isi: (D) => { const G = D.tagihan; if (!ada(G)) return wgGalat('tagihan', G); const U = G.pemasok;
    return { nilai: RP(U.rpLewat + U.rpDekat), ket: U.lewat.length + ' lewat · ' + U.dekat.length + ' jatuh ≤ ' + U.dekatHari + ' hari · semua ' + wgRpPendek(U.total), awas: U.lewat.length > 0 || !!U.kurang,
      rinci: [['Lewat tempo', RP(U.rpLewat)], ['Jatuh ≤ ' + U.dekatHari + ' hari', RP(U.rpDekat)], ['Semua bon pemasok', RP(U.total)], ['Uang toko', U.cukupTeks]], tujuan: U.tujuan }; } },
  { id: 'stokMinimum', nama: 'Di bawah stok minimum', ukuran: 'kecil', kel: 'stokMin', isi: (D) => { const S = D.stokMin; if (!ada(S)) return wgGalat('stokMin', S);
    return { nilai: S.n ? S.n + ' barang' : 'aman', ket: S.n ? S.daftar.slice(0, 3).map((x) => x.nama).join(', ') + (S.n > 3 ? ', …' : '') : 'semua ' + S.dicek + ' barang di atas minimum', awas: S.n > 0,
      rinci: S.daftar.slice(0, 8).map((x) => [x.nama, x.kata]).concat([['Bawaan', '≤ ' + S.bawaan + ' hari (Belanja › Atur)']]), tujuan: S.tujuan }; } },
  { id: 'bukuMinus', nama: 'Buku stok minus', ukuran: 'kecil', kel: 'stok', isi: (D) => { const S = D.stok; const G = ada(S) ? S.gudang : S; if (!ada(G)) return wgGalat('stok', G); const M = G.minus;
    return { nilai: M.n ? M.n + ' buku' : 'tidak ada', ket: M.n ? RP(M.rp) + ' · ' + M.kalimat : 'semua buku stok ≥ 0', awas: M.n > 0, rinci: M.top.slice(0, 6).map((x) => [x.nama, x.teks]), tujuan: G.tujuan }; } },
  { id: 'susut', nama: 'Susut beras bulan ini', ukuran: 'kecil', kel: 'mutu', isi: (D) => { const Q = D.mutu; if (!ada(Q)) return wgGalat('mutu', Q); const S = Q.susut;
    if (!S) return { nilai: '—', ket: 'bulan ini sudah ditutup buku', awas: false, rinci: [], tujuan: Q.tujuan }; if (S.galat) return wgGalat('susut', S);
    return { nilai: wgPctPolos(S.pct), ket: 'target ' + wgPctPolos(S.target) + (S.merah.length ? ' · ' + S.merah.length + ' merek merah' : '') + (S.kuning.length ? ' · ' + S.kuning.length + ' kuning' : ''), awas: S.status === 'diAtas' || S.merah.length > 0,
      rinci: [['Susut bulan ini', wgPctPolos(S.pct)], ['Target', wgPctPolos(S.target)]], tujuan: S.tujuan }; } },
  { id: 'kasMinimum', nama: 'Kas vs ambang minimum', ukuran: 'kecil', kel: 'kpi', isi: (D) => { const Q = D.kpi; if (!ada(Q) || !ada(Q.kas)) return wgGalat('kpi', ada(Q) ? Q.kas : Q); const K = Q.kas;
    if (!K.nyala) return { nilai: 'mati', ket: 'ambang kas minimum belum diatur', awas: false, rinci: [], tujuan: Q.tujuan };
    return { nilai: K.kas === null ? 'belum bisa' : K.bawah ? 'KURANG ' + wgRpPendek(K.kurang) : 'aman', ket: 'kas ' + (K.kas === null ? '—' : RP(K.kas)) + ' · ambang ' + RP(K.batas), awas: !!K.bawah, rinci: [], tujuan: Q.tujuan }; } },
  { id: 'pondasi', nama: 'Lampu pondasi', ukuran: 'kecil', kel: 'pondasi', isi: (D) => { const Q = D.pondasi; if (!ada(Q)) return wgGalat('pondasi', Q); const L = Q.lampu || [];
    const n = (w) => L.filter((l) => l.lampu === w).length;
    return { nilai: n('merah') ? n('merah') + ' merah' : n('amber') ? n('amber') + ' kuning' : 'aman', ket: n('hijau') + ' hijau · ' + n('amber') + ' kuning · ' + n('merah') + ' merah dari ' + L.length, awas: n('merah') > 0,
      rinci: L.map((l) => [l.nama, l.nilai]), tujuan: Q.tujuan }; } },
  { id: 'karcis', nama: 'Karcis kasir belum dirinci', ukuran: 'kecil', kel: 'hari', isi: (D) => { const H = D.hari; if (!ada(H)) return wgGalat('hari', H); const K = H.karcis;
    return { nilai: K.n ? K.n + ' karcis' : 'tidak ada', ket: K.n ? RP(K.rp) + (K.rapikan ? ' · ' + K.rapikan + ' nota perlu dirapikan' : '') : 'semua nota kasir sudah dirinci', awas: K.n > 0, rinci: [], tujuan: H.karcisTujuan }; } },
  { id: 'trenOmzet', nama: 'Tren omzet', ukuran: 'besar', kel: 'tren', isi: (D) => { const T = D.tren; if (!ada(T)) return wgGalat('tren', T);
    const b = T.batang.filter((x) => !x.absen); const akhir = b[b.length - 1];
    return { nilai: akhir ? RP(akhir.omzet) : '—', ket: T.periode + ' · tertinggi ' + wgRpPendek(T.maks), awas: false, tren: T.batang.map((x) => ({ label: x.label, n: x.absen ? null : x.omzet, berjalan: !!x.berjalan })),
      rinci: b.slice(-4).map((x) => [x.panjang, RP(x.omzet) + ' · ' + x.nota + ' nota']), tujuan: { ke: 'laporan', keluarga: T.rentang === 'hari' ? 'harian' : T.rentang === 'minggu' ? 'mingguan' : 'bulanan' } }; } },
  { id: 'labaEnam', nama: 'Laba bersih 6 bulan', ukuran: 'lebar', kel: 'enam', isi: (D) => { const E = D.enam; if (!ada(E)) return wgGalat('enam', E); const b = E.bulan.filter((x) => !x.tanpaCatatan);
    const akhir = b[b.length - 1];
    return { nilai: akhir ? RP(akhir.labaBersih) : '—', ket: akhir ? akhir.pendek + (akhir.berjalan ? ' (berjalan)' : '') + ' · biaya ' + wgRpPendek(akhir.semuaBiaya) : 'belum ada bulan tercatat', awas: !!akhir && akhir.labaBersih < 0,
      tren: E.bulan.map((x) => ({ label: x.pendek, n: x.tanpaCatatan ? null : x.labaBersih, berjalan: x.berjalan })), rinci: b.map((x) => [x.pendek, RP(x.labaBersih) + ' · biaya ' + wgRpPendek(x.semuaBiaya)]), tujuan: E.tujuan }; } },
  { id: 'posisiEnam', nama: 'Kas · piutang · stok', ukuran: 'lebar', kel: 'enam', isi: (D) => { const E = D.enam; if (!ada(E)) return wgGalat('enam', E); const p = E.posisi.filter((x) => x.ada);
    const akhir = p[p.length - 1]; if (!akhir) return { nilai: 'belum bisa', ket: E.galatPosisi || (E.posisi[0] ? E.posisi[0].kenapa : 'titik kas belum disetel'), awas: false, rinci: [], tujuan: E.posisiTujuan };
    return { nilai: RP(akhir.kas), ket: 'kas · piutang ' + wgRpPendek(akhir.piutang) + ' · stok ' + wgRpPendek(akhir.stok) + ' · ' + akhir.nama, awas: false,
      tren: E.posisi.map((x) => ({ label: x.nama, n: x.ada ? x.kas : null, berjalan: x.berjalan })), rinci: p.map((x) => [x.nama, 'kas ' + wgRpPendek(x.kas) + ' · piutang ' + wgRpPendek(x.piutang) + ' · stok ' + wgRpPendek(x.stok)]), tujuan: E.posisiTujuan }; } },
  // ---------- paket sisa sensus (owner 27 Nov 2026): B68 · B35 · A121 · A47 — membaca kelompok dasbor yang SAMA dengan kartunya ----------
  { id: 'pembelian', nama: 'Pembelian', ukuran: 'lebar', kel: 'beli', ikut: true, isi: (D) => { const B = D.beli; if (!ada(B)) return wgGalat('beli', B); const P = B.saring; const T = B.tren.bulan;
    return { nilai: RP(P.rp), ket: B.periodeNama + ' · ' + P.n + ' kedatangan · bon ' + wgRpPendek(P.bon.rp), awas: false, tren: T.batang.map((x) => ({ label: x.label, n: x.absen ? null : x.rp, berjalan: !!x.berjalan })),
      rinci: [['Bon (dibayar nanti)', RP(P.bon.rp)], ['Dibayar langsung', RP(P.langsung.rp)]].concat(B.bulan ? [[B.bulanNama, RP(B.bulan.rp) + ' · ' + B.bulan.n + ' kedatangan']] : []), tujuan: B.tujuan }; } },
  { id: 'telatBayar', nama: 'Diperkirakan telat bayar', ukuran: 'kecil', kel: 'tagihan', isi: (D) => { const G = D.tagihan; if (!ada(G)) return wgGalat('tagihan', G); const T = G.piutang.telat; if (!ada(T)) return wgGalat('telat', T);
    return { nilai: T.n ? T.n + ' orang' : 'tidak ada', ket: T.n ? RP(T.rp) + ' belum jatuh tempo · 2 dari 3 bon terakhir telat' : T.kalimat, awas: T.n > 0, rinci: T.daftar.map((o) => [o.nama, RP(o.rp)]), tujuan: G.piutang.telatTujuan }; } },
  { id: 'modalTertahan', nama: 'Modal tertahan di stok', ukuran: 'kecil', kel: 'kpi', ikut: true, isi: (D) => { const Q = D.kpi; if (!ada(Q) || !ada(Q.modal)) return wgGalat('kpi', ada(Q) ? Q.modal : Q); const M = Q.modal;
    if (M.rata === null) return { nilai: '—', ket: M.kalimat, awas: false, rinci: [], tujuan: Q.tujuan };
    return { nilai: wgRpPendek(M.rata), ket: M.bunga > 0 ? 'rata-rata · biaya modal ' + wgRpPendek(M.biaya) + ' (' + M.nHari + ' hari, ' + DESIMAL(M.bunga) + '%/th)' : 'rata-rata · bunga modal mati', awas: false,
      rinci: [['Nilai stok terakhir', RP(Math.round(M.kini))], ['± sebulan', RP(Math.round(M.sebulan))]].concat(M.buku.slice(0, 3).map((x) => [x.nama, RP(Math.round(x.rata))])), tujuan: { ke: 'sistem', sistem: 'target' } }; } },
  { id: 'pphBulan', nama: 'Sisihkan PPh final', ukuran: 'kecil', kel: 'bulan', ikut: true, isi: (D) => { const B = D.bulan; if (!ada(B)) return wgGalat('bulan', B); const X = B.pph; if (!X) return wgGalat('pph', X);
    if (X.n === null) return { nilai: '—', ket: X.teks, awas: false, rinci: [], tujuan: X.tujuan };
    return { nilai: RP(X.sisihkan), ket: 'perkiraan ' + wgRpPendek(X.n) + (X.anggaran > 0 ? ' · ' + X.lampuTeks : ' · anggaran belum diatur') + ' · di luar laba bersih', awas: X.lampu === 'merah', lampu: X.lampu === 'tanpa' ? '' : X.lampu,
      rinci: [['Perkiraan', RP(X.n)], ['Sudah disetor', RP(X.setor)]].concat(X.proyeksi !== null ? [['Perkiraan sebulan', RP(X.proyeksi)]] : []), tujuan: X.tujuan }; } },
  // ---------- P1 (owner 27 Nov 2026): A112 untung per kg · A115 hari stok · A114 perputaran stok · A116 lama piutang — kelompok dasbor kpi.kg & kg apa adanya ----------
  { id: 'marginKg', nama: 'Untung per kg bulan ini', ukuran: 'kecil', kel: 'kpi', ikut: true, isi: (D) => { const Q = D.kpi; if (!ada(Q) || !ada(Q.kg)) return wgGalat('kpi', ada(Q) ? Q.kg : Q); const G = Q.kg;
    if (G.marginKg === null) return { nilai: '—', ket: G.kalimat, awas: false, rinci: [], tujuan: G.tujuan };
    return { nilai: RP(Math.round(G.marginKg)) + '/kg', ket: 'HPP ' + RP(Math.round(G.hppKg)) + '/kg' + (G.lalu && G.lalu.marginKg !== null ? ' · ' + G.lalu.pendek + ' ' + RP(Math.round(G.lalu.marginKg)) + '/kg' : '') + (G.target.rp > 0 ? ' · ' + G.nBawah + ' merek di bawah target ' + wgRpPendek(G.target.rp) + '/kg' : ''),
      awas: G.target.rp > 0 && G.marginKg < G.target.rp, rinci: [['Untung per kg', RP(Math.round(G.marginKg)) + '/kg'], ['HPP per kg', RP(Math.round(G.hppKg)) + '/kg'], ['Harga jual per kg', RP(Math.round(G.jualKg)) + '/kg'], ['Target untung', G.target.teks]]
        .concat(G.lalu ? [[G.lalu.nama, G.lalu.marginKg === null ? '—' : RP(Math.round(G.lalu.marginKg)) + '/kg']] : []).concat(G.bawah.slice(0, 3).map((x) => ['· ' + x.merek, RP(Math.round(x.marginKg)) + '/kg'])), tujuan: G.tujuan }; } },
  { id: 'hariStok', nama: 'Hari stok (rupiah)', ukuran: 'kecil', kel: 'kg', ikut: true, isi: (D) => { const G = D.kg; if (!ada(G) || !ada(G.stok)) return wgGalat('kg', ada(G) ? G.stok : G); const S = G.stok;
    if (S.hari === null) return { nilai: '—', ket: S.kalimat, awas: false, rinci: [], tujuan: S.tujuanAtur };
    return { nilai: DESIMAL(Math.round(S.hari * 10) / 10) + ' hari', ket: (S.status === 'tipis' ? 'STOK TIPIS · ' : S.status === 'diam' ? 'modal kebanyakan diam · ' : 'pas · ') + 'target ' + S.target.teks + ' · ' + G.periodeNama,
      awas: S.status !== 'pas', lampu: S.status === 'pas' ? 'hijau' : 'amber', rinci: [['Rata-rata nilai stok', RP(Math.round(S.rata))], ['Modal terjual per hari', RP(Math.round(S.hppHari))], ['Target', S.target.teks], ['Cara hitung', S.rumus]], tujuan: S.tujuanAtur }; } },
  { id: 'putaranStok', nama: 'Perputaran stok (rupiah)', ukuran: 'kecil', kel: 'kg', ikut: true, isi: (D) => { const G = D.kg; if (!ada(G) || !ada(G.stok)) return wgGalat('kg', ada(G) ? G.stok : G); const S = G.stok;
    if (S.putaranTahun === null) return { nilai: '—', ket: S.kalimat, awas: false, rinci: [], tujuan: S.tujuanAtur };
    return { nilai: DESIMAL(Math.round(S.putaranTahun * 10) / 10) + '× setahun', ket: DESIMAL(Math.round(S.putaran * 100) / 100) + '× dalam ' + S.nHari + ' hari · ' + G.periodeNama, awas: false,
      rinci: [['Modal terjual', RP(Math.round(S.hpp))], ['Rata-rata nilai stok', RP(Math.round(S.rata))], ['Dalam ' + S.nHari + ' hari', DESIMAL(Math.round(S.putaran * 100) / 100) + '×'], ['Cara hitung', S.rumus]], tujuan: S.tujuanAtur }; } },
  { id: 'dso', nama: 'Lama piutang (hari)', ukuran: 'kecil', kel: 'kg', isi: (D) => { const G = D.kg; if (!ada(G) || !ada(G.dso)) return wgGalat('kg', ada(G) ? G.dso : G); const P = G.dso; const X = P.kini;
    if (X.dso === null) return { nilai: '—', ket: P.kalimat, awas: false, rinci: [], tujuan: P.tujuan };
    return { nilai: DESIMAL(Math.round(X.dso * 10) / 10) + ' hari', ket: 'piutang ' + wgRpPendek(X.piutang) + ' ÷ bon ' + wgRpPendek(X.perHari) + '/hari' + (P.beda !== null ? ' · ' + (Math.abs(P.beda) < 0.05 ? 'sama dengan akhir minggu lalu' : (P.beda > 0 ? '+' : '−') + DESIMAL(Math.round(Math.abs(P.beda) * 10) / 10) + ' hari vs akhir minggu lalu') : ''),
      awas: P.beda !== null && P.beda >= 0.05, rinci: [['Piutang berjalan', RP(Math.round(X.piutang)) + ' · ' + X.nOrang + ' orang'], ['Penjualan bon ' + X.hari + ' hari', RP(Math.round(X.jual))], ['Bon lunas rata-rata tertagih', P.tertagih.rataTeks], ['Cara hitung', P.rumus]], tujuan: P.tujuan }; } },
  // B133 (P1): ketepatan kirim pemasok = B65 paket tanggal janji (#231) — kpi.janji (janji-logika jnRingkas) apa adanya, 90 hari terakhir, tidak ikut saringan
  { id: 'tepatJanji', nama: 'Tepat janji pemasok', ukuran: 'kecil', kel: 'kpi', isi: (D) => { const Q = D.kpi; if (!ada(Q) || !ada(Q.janji)) return wgGalat('kpi', ada(Q) ? Q.janji : Q); const J = Q.janji; const P = J.pemasok;
    const lewat = (J.lewat || []).filter((x) => x.tujuan && x.tujuan.ke === 'harga');
    if (!P.n) return { nilai: '—', ket: J.kalimatPemasok, awas: lewat.length > 0, rinci: lewat.slice(0, 4).map((x) => ['Lewat janji', x.teks]), tujuan: J.tujuan };
    return { nilai: wgPctPolos(P.pct), ket: P.tepat + ' dari ' + P.n + ' kiriman tepat janji · ' + J.hari + ' hari' + (lewat.length ? ' · ' + lewat.length + ' lewat janji' : ''), awas: lewat.length > 0,
      rinci: [['Dari pemasok', J.kalimatPemasok]].concat(lewat.slice(0, 4).map((x) => ['Lewat janji', x.teks])), tujuan: J.tujuan }; } },
  // ---------- P3 (owner 27 Nov 2026): A4 peringatan uang · B48 modal diam · B67 pesanan pemasok · B129 nota jual-dulu — kelompok dasbor apa adanya, hanya lewat katalog ----------
  { id: 'peringatanUang', nama: 'Peringatan uang (lonceng)', ukuran: 'lebar', kel: 'peringatan', isi: (D) => { const P = D.peringatan; if (!ada(P)) return wgGalat('peringatan', P);
    return { nilai: P.n ? P.n + ' menyala' : 'tidak ada', ket: P.n ? P.jenis.filter((j) => j.n).map((j) => j.nama.toLowerCase() + ' ' + j.n).join(' · ') : 'biaya, susut, modal, harga, untung per kg & kas aman', awas: P.n > 0,
      rinci: P.daftar.slice(0, 6).map((x) => [x.teks, x.n ? RP(x.n) : '']).concat(P.tidakTerbaca.length ? [['Tidak terbaca', P.tidakTerbaca.join(' · ').slice(0, 120)]] : []), tujuan: P.tujuan }; } },
  { id: 'modalDiam', nama: 'Modal diam (lambat laku)', ukuran: 'kecil', kel: 'mutu', isi: (D) => { const Q = D.mutu; if (!ada(Q) || !ada(Q.modalDiam)) return wgGalat('mutu', ada(Q) ? Q.modalDiam : Q); const M = Q.modalDiam;
    return { nilai: M.n ? wgRpPendek(M.rp) : 'tidak ada', ket: M.n + ' lambat laku · stok > ' + M.atur.tua + ' hari ' + wgRpPendek(M.tuaRp) + (M.menutup ? '' : ' · TIDAK MENUTUP'), awas: M.n > 0 || !M.menutup,
      rinci: M.lapisan.map((b) => [b.nama, RP(Math.round(b.rp))]).concat(M.daftar.slice(0, 3).map((x) => ['· ' + x.nama, RP(Math.round(x.rp))])), tujuan: M.tujuan }; } },
  { id: 'pesananPemasok', nama: 'Pesanan pemasok menunggu', ukuran: 'kecil', kel: 'beli', isi: (D) => { const B = D.beli; if (!ada(B) || !ada(B.pesanan)) return wgGalat('beli', ada(B) ? B.pesanan : B); const P = B.pesanan;
    return { nilai: P.n ? ANGKA(Math.round(P.kg)) + ' kg' : 'tidak ada', ket: P.n ? P.n + ' pesanan · ±' + wgRpPendek(P.rp) + (P.tanpaHarga ? ' · ' + P.tanpaHarga + ' tanpa harga' : '') : 'semua pesanan sudah datang / dibatalkan', awas: false,
      rinci: P.pemasok.slice(0, 5).map((g) => [g.pemasok, ANGKA(Math.round(g.kg)) + ' kg · ' + RP(Math.round(g.rp)) + (g.janji ? ' · janji ' + g.janji.slice(8, 10) + '/' + g.janji.slice(5, 7) : '')]), tujuan: P.tujuan }; } },
  { id: 'notaTembus', nama: 'Nota "jual dulu, tandai"', ukuran: 'kecil', kel: 'stok', isi: (D) => { const S = D.stok; const G = ada(S) ? S.gudang : S; if (!ada(G)) return wgGalat('stok', G);
    const T = (G.tugas.terbuka || []).find((x) => x.id === 'tembus');
    return { nilai: T ? T.n + ' nota' : 'tidak ada', ket: T ? T.ket : 'semua nota jual-dulu sudah dicocokkan', awas: !!T, rinci: [], tujuan: T ? T.tujuan : G.tujuan }; } },
].map((w) => Object.assign({ jenis: 'angka' }, w)).concat(WG_KARTU()).map((K) => Object.assign({ w: WG_LEBAR_UKURAN[K.ukuran] || 6, minW: K.jenis === 'angka' ? 2 : 3 }, K));
const wgKat = (id) => WG_KATALOG.find((w) => w.id === id) || null;
/** B94 (owner 27 Nov 2026): angka yang membaca kelompok YANG IKUT saringan (hari · bulan · kpi bulanan · mutu · pembelian) ganti nama sesuai periodenya — angka
 *  "Laba kotor hari ini" tidak boleh memajang 7 hari. Yang bernama "hari ini" dan membaca pembanding jam segini (banding) tetap hari ini. */
const WG_NAMA_SARING = { labaKotorHari: (S) => 'Laba kotor · ' + S.nama, labaBersihBulan: (S) => 'Laba bersih · ' + S.bulanNama, biayaBulan: (S) => 'Biaya · ' + S.bulanNama,
  marginBulan: (S) => 'Margin · ' + S.bulanNama, susut: (S) => 'Susut beras · ' + S.bulanNama, pembelian: (S) => 'Pembelian · ' + S.nama, modalTertahan: (S) => 'Modal tertahan di stok · ' + S.nama, pphBulan: (S) => 'Sisihkan PPh · ' + S.bulanNama,
  marginKg: (S) => 'Untung per kg · ' + S.bulanNama, hariStok: (S) => 'Hari stok · ' + S.nama, putaranStok: (S) => 'Perputaran stok · ' + S.nama, kTerlaris: (S) => 'Terlaris · ' + S.nama };
export const wgNama = (K, S) => (S && !S.bawaan && WG_NAMA_SARING[K.id] ? WG_NAMA_SARING[K.id](S) : K.nama);
/** Bawaan (belum pernah diatur owner) = urutan kartu lama ("Tampilan saat ini yang paling penting"), Mac: Hari ini | Margin & target · Tren selebar kisi · lalu
 *  kartu lajur kiri & kanan lama bergantian (kisi merapat mengisinya seperti dua lajur dulu). Tinggi = setinggi isinya. Widget tambahan = di katalog. */
export const WG_BAWAAN = ['kHari', 'kKpi', 'kTren', 'kBulan', 'kWadah', 'kPemicu', 'kTagihan', 'kStok', 'kMutu', 'kPondasi', 'kB2b'].map((id) => ({ id, w: (WG_KATALOG.find((K) => K.id === id) || {}).w || 6, h: null }));
const wgBulat = (v) => (v === null || v === undefined || v === '' ? null : Math.round(Number(v)));
/** Satu panel dibersihkan: lebar bulat [minW, 12] (ukuran lama kecil/lebar/besar/penuh dibaca), tinggi null atau bulat [WG_H_MIN, WG_H_MAKS]. */
function wgPanel(w, K) {
  const ww = wgBulat(w.w); const lebar = isFinite(ww) && ww !== null ? ww : WG_LEBAR_UKURAN[w.ukuran] || K.w;
  const hh = wgBulat(w.h); const tinggi = hh === null || !isFinite(hh) ? null : Math.max(WG_H_MIN, Math.min(WG_H_MAKS, hh));
  return { id: K.id, w: Math.max(K.minW, Math.min(WG_KOLOM, lebar)), h: tinggi };
}
/** Bersihkan daftar: id dikenal, tanpa kembar, lebar & tinggi sah, paling banyak WG_MAKS. */
export function wgBersih(daftar) {
  const lihat = {}; const out = [];
  (Array.isArray(daftar) ? daftar : []).forEach((w) => { const K = w && wgKat(w.id); if (!K || lihat[K.id] || out.length >= WG_MAKS) return; lihat[K.id] = 1; out.push(wgPanel(w, K)); });
  return out;
}
/** Susunan yang berlaku: setelan owner (aturanToko/dasbor.widget) — kalau belum pernah diatur, bawaan. */
export function wgAtur() {
  const d = cacheMentah('aturan').find((x) => String(x.id) === WG_ID) || null; const milik = !!d && Array.isArray(d.widget);
  return { daftar: milik ? wgBersih(d.widget) : WG_BAWAAN.map((x) => Object.assign({}, x)), dariOwner: milik, tanggal: d ? String(d.tanggal || '') : '', jam: d ? String(d.jam || '') : '' };
}
// ---- ubahan di mode atur (murni: daftar lama → daftar baru; disimpan sekali saat "Selesai") ----
export function wgPindah(daftar, dari, ke) { const d = daftar.slice(); if (dari < 0 || dari >= d.length) return d; const j = Math.max(0, Math.min(d.length - 1, ke)); const [x] = d.splice(dari, 1); d.splice(j, 0, x); return d; }
export function wgHapus(daftar, i) { return daftar.filter((_, n) => n !== i); }
export function wgTambah(daftar, id) { const K = wgKat(id); if (!K || daftar.some((w) => w.id === id) || daftar.length >= WG_MAKS) return daftar.slice(); return daftar.concat([{ id, w: K.w, h: null }]); }
/** Tarik pegangan: lebar (kolom) dan/atau tinggi (baris); undefined = tidak diubah. Dijepit ke batasnya. */
export function wgUkur(daftar, i, w, h) { return daftar.map((x, n) => { if (n !== i) return x; const K = wgKat(x.id); if (!K) return x; return wgPanel({ w: w === undefined ? x.w : w, h: h === undefined ? x.h : h }, K); }); }
/** Kembali setinggi isinya. */
export function wgTinggiOtomatis(daftar, i) { return daftar.map((x, n) => (n !== i ? x : { id: x.id, w: x.w, h: null })); }
export const wgSama = (a, b) => JSON.stringify(wgBersih(a)) === JSON.stringify(wgBersih(b));
/** Katalog yang belum dipasang (lembar "+ Tambah"), dikelompokkan jenis: lama (kartu Dasbor) · kartu (tambahan) · angka. */
export const wgBelumDipasang = (daftar) => WG_KATALOG.filter((K) => !daftar.some((w) => w.id === K.id)).map((K) => ({ id: K.id, nama: K.nama, w: K.w, jenis: K.jenis }));
/** Simpan susunan (owner). Satu dokumen aturanToko/dasbor — tidak menyentuh uang, stok, maupun catatan. */
export function susunAturDasbor(daftar, w) {
  if (!Array.isArray(daftar)) return { tolak: 'Susunan Dasbor tidak terbaca' };
  const bersih = wgBersih(daftar); if (bersih.length !== daftar.length) return { tolak: 'Ada kartu yang tidak dikenal atau kembar — muat ulang lalu atur lagi' };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: WG_ID, tanggal: w.tanggal, jam: w.jam, widget: bersih } }],
    patch: { kabar: 'Susunan Dasbor disimpan — ' + (bersih.length ? bersih.length + ' kartu' : 'kosong') + ' (ikut ke semua perangkat owner)', kabarAwas: false } };
}
/** Isi semua panel pada susunan untuk satu hasil dasbor D (kartu lama: tanpa isi — digambar layar). Satu yang galat tidak mematikan yang lain. */
export function wgSusun(daftar, D) {
  return wgBersih(daftar).map((w) => { const K = wgKat(w.id); let isi;
    try { isi = K.isi(D || {}); } catch (e) { isi = wgGalat(K.kel, { galat: String((e && e.message) || e) }); }
    return Object.assign({ id: w.id, w: w.w, h: w.h, nama: wgNama(K, D && D.saring), kel: K.kel, jenis: K.jenis, khusus: !!K.khusus, minW: K.minW }, isi); });
}
