// SELISIH LACI · ALARM BERULANG · TREN · PENJELASAN SUSULAN (owner 27 Nov 2026, sensus ulang A119 + A82 — paket P6). Tanpa DOM, BACA SAJA kecuali dua penyusun,
// awalan lh. TIDAK ADA RUMUS UANG BARU: selisih tiap malam = angka dokumen tutupHari apa adanya (bentuk bacaTutup tutup-hari-logika: selisihLaci, kalau tidak ada
// selisih); batas maaf = aturanToko/tutupHari.maafSelisih (sama dengan aturTutup). Dibaca LANGSUNG dari cache supaya Dasbor tidak perlu memuat tutup-hari-logika;
// uji_laci_rutin membandingkan keduanya.
// Keputusan owner 27 Nov 2026:
//   · alarm selisih laci BERULANG = N malam tutup BERTURUT-TURUT berselisih lewat batas maaf, ATAU M dari W malam tutup terakhir — bawaan 3 beruntun / 4 dari 7
//     (setelan owner di Uang › Tutup hari › Atur: aturanToko/selisihLaci). Lonceng & Dasbor owner. "Malam" = hari yang DITUTUP (hari tanpa tutup tidak dihitung,
//     disebut di Laporan › Pondasi › Disiplin); malam lebih dari LH_UMUR_HARI lalu tidak ikut alarm (alarm basi tidak berbunyi).
//   · alasan selisih BEBAS: owner mengetik sendiri di lembar Tutup hari (selain pilihan daftar), Penjaga laci menitip catatan bebas bersama hitungan laci tablet
//     (tutup-tablet-logika, tablet tetap hitung buta). "Belum ketemu — cari besok" (tutupHari.cariBesok, atau alasan bawaan "Belum tahu — dicari besok") menagih
//     owner TIAP HARI lewat pengingat sampai penjelasan susulannya ditulis (tutupHari.penjelasan { teks, tanggal, jam } — owner, satu dokumen yang sama).
import { ambilTutupHari, cacheMentah } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';

export const LH_ID = 'selisihLaci';   // aturanToko/selisihLaci — setelan alarm (owner)
export const LH_BAWAAN = { maafSelisih: 2000, alarmBeruntun: 3, alarmDalam: 4, alarmJendela: 7 };   // maafSelisih = ATUR_TUTUP_BAWAAN.maafSelisih tutup-hari-logika
export const LH_BATAS = { alarmBeruntun: [2, 30], alarmJendela: [3, 30], penjelasan: [3, 160] };
export const LH_UMUR_HARI = 30;    // malam yang lebih tua dari ini tidak ikut alarm (tren tetap memuatnya)
export const LH_CARI = 'Belum ketemu — cari besok';
export const LH_CARI_LAMA = 'Belum tahu — dicari besok';   // alasan bawaan ATUR_TUTUP_BAWAAN.alasan — dipilih = ikut ditagih
export const LH_TREN = 30;
const lhHariKe = (iso) => Math.round(new Date(String(iso) + 'T00:00:00Z').getTime() / 86400000);
const lhTambah = (iso, n) => { const d = new Date(String(iso) + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const lhTeks = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const lhDok = (id) => cacheMentah('aturan').find((d) => String(d.id) === id) || null;

/** Setelan: batas maaf (aturanToko/tutupHari, = aturTutup) + angka alarm (aturanToko/selisihLaci). Angka rusak / di luar batas = bawaan. */
export function lhAtur() {
  const T = lhDok('tutupHari') || {}; const S = lhDok(LH_ID) || {};
  const maaf = isFinite(Number(T.maafSelisih)) && Number(T.maafSelisih) >= 0 && Number(T.maafSelisih) <= 10000000 ? Math.round(Number(T.maafSelisih)) : LH_BAWAAN.maafSelisih;
  const bul = (v, b, lo, hi) => (Number.isInteger(Number(v)) && Number(v) >= lo && Number(v) <= hi ? Number(v) : b);
  const jendela = bul(S.alarmJendela, LH_BAWAAN.alarmJendela, LH_BATAS.alarmJendela[0], LH_BATAS.alarmJendela[1]);
  const beruntun = bul(S.alarmBeruntun, LH_BAWAAN.alarmBeruntun, LH_BATAS.alarmBeruntun[0], LH_BATAS.alarmBeruntun[1]);
  const dalam = bul(S.alarmDalam, LH_BAWAAN.alarmDalam, 1, jendela);
  return { maaf, beruntun, dalam: Math.min(dalam, jendela), jendela, dariOwner: !!lhDok(LH_ID), nyala: S.nyala !== false };
}
/** Satu malam dari dokumen tutupHari (selisih = bacaTutup: selisihLaci, kalau tidak ada selisih). */
export function lhBaca(d, A) {
  const s0 = d.selisihLaci !== undefined ? d.selisihLaci : d.selisih; const selisih = s0 === null || s0 === undefined || !isFinite(Number(s0)) ? null : Math.round(Number(s0));
  const lewat = selisih !== null && Math.abs(selisih) > A.maaf; const alasan = String(d.alasanSelisih || ''); const P = d.penjelasan && typeof d.penjelasan === 'object' && lhTeks(d.penjelasan.teks) ? d.penjelasan : null;
  const cari = lewat && (d.cariBesok === true || alasan === LH_CARI || alasan === LH_CARI_LAMA);
  const tablet = d.dariTablet && typeof d.dariTablet === 'object' ? d.dariTablet : null;
  return { tanggal: String(d.tanggal || ''), jam: String(d.jam || ''), selisih, lewat, arah: selisih === null ? '' : selisih > 0 ? 'lebih' : selisih < 0 ? 'kurang' : 'pas', alasan, cari,
    penjelasan: P ? { teks: lhTeks(P.teks), tanggal: String(P.tanggal || ''), jam: String(P.jam || '') } : null, perluJelas: cari && !P, sistemBaru: !!d.sistemBaru,
    penghitung: tablet ? String(tablet.oleh || 'tablet') : 'owner', catatanTablet: tablet ? lhTeks(tablet.catatan) : '' };
}
/** Semua malam yang ditutup, TERBARU dulu (≤ hari `iso`). */
export function lhMalam(kini) {
  const iso = hariIniIso(kini); const A = lhAtur();
  return ambilTutupHari().filter((d) => d && /^\d{4}-\d{2}-\d{2}$/.test(String(d.tanggal || '')) && d.tanggal <= iso).slice().sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal))).map((d) => lhBaca(d, A));
}

/**
 * ALARM selisih laci berulang. → { nyala, beruntun, dalam, jendela, A, malam (W malam terakhir dalam LH_UMUR_HARI), lebih, kurang, kalimat, terakhir }.
 * beruntun = malam tutup berturut-turut dari yang terbaru yang lewat batas maaf; dalam = jumlah malam lewat batas di W malam terakhir.
 */
export function lhAlarm(kini) {
  const iso = hariIniIso(kini); const A = lhAtur(); const M = lhMalam(kini).filter((m) => lhHariKe(iso) - lhHariKe(m.tanggal) <= LH_UMUR_HARI); const W = M.slice(0, A.jendela);
  let beruntun = 0; for (const m of M) { if (!m.lewat) break; beruntun++; }
  const dalam = W.filter((m) => m.lewat).length; const lebih = W.filter((m) => m.lewat && m.selisih > 0).reduce((a, m) => a + m.selisih, 0); const kurang = W.filter((m) => m.lewat && m.selisih < 0).reduce((a, m) => a + m.selisih, 0);
  const kenaBeruntun = beruntun >= A.beruntun; const kenaDalam = dalam >= A.dalam; const nyala = A.nyala && (kenaBeruntun || kenaDalam); const terakhir = M[0] || null;
  const kalimat = !M.length ? 'Belum ada malam yang ditutup dalam ' + LH_UMUR_HARI + ' hari terakhir'
    : (kenaBeruntun ? beruntun + ' malam berturut-turut' : dalam + ' dari ' + W.length + ' malam terakhir') + ' selisih laci lewat batas maaf ' + RP(A.maaf) + (lebih ? ' · lebih ' + RP(lebih) : '') + (kurang ? ' · kurang ' + RP(-kurang) : '')
      + (nyala ? '' : ' — di bawah ambang alarm (' + A.beruntun + ' beruntun / ' + A.dalam + ' dari ' + A.jendela + ')');
  return { iso, nyala, kenaBeruntun, kenaDalam, beruntun, dalam, jendela: W.length, A, malam: W, lebih, kurang, terakhir, kalimat, sumber: 'Uang › Tutup hari', tujuan: { ke: 'uang', keluarga: 'tutup' } };
}

/** TREN n malam tutup terakhir (urut LAMA → baru, untuk batang) + ringkasan. → { malam, nLewat, nPas, nDimaafkan, nTanpa, lebih, kurang, rataAbs, maksAbs }. */
export function lhTren(kini, n) {
  const A = lhAtur(); const M = lhMalam(kini).slice(0, n || LH_TREN).reverse(); const ada = M.filter((m) => m.selisih !== null);
  const lewat = ada.filter((m) => m.lewat);
  return { malam: M, n: M.length, nLewat: lewat.length, nPas: ada.filter((m) => m.selisih === 0).length, nDimaafkan: ada.filter((m) => m.selisih !== 0 && !m.lewat).length, nTanpa: M.length - ada.length,
    lebih: lewat.filter((m) => m.selisih > 0).reduce((a, m) => a + m.selisih, 0), kurang: lewat.filter((m) => m.selisih < 0).reduce((a, m) => a + m.selisih, 0),
    rataAbs: ada.length ? Math.round(ada.reduce((a, m) => a + Math.abs(m.selisih), 0) / ada.length) : null, maksAbs: ada.length ? Math.max(...ada.map((m) => Math.abs(m.selisih))) : null, maaf: A.maaf,
    dari: M.length ? M[0].tanggal : '', sampai: M.length ? M[M.length - 1].tanggal : '' };
}
/** Per orang yang MENGHITUNG laci (tablet: nama Penjaga laci; selain itu owner), n malam terakhir: malam, lewat batas, jumlah bersih + lebih & kurang terpisah. */
export function lhPerOrang(kini, n) {
  const per = {}; lhMalam(kini).slice(0, n || LH_TREN).forEach((m) => { const k = m.penghitung; const x = per[k] || (per[k] = { nama: k, n: 0, nLewat: 0, jumlah: 0, lebih: 0, kurang: 0 }); x.n++; if (m.lewat) { x.nLewat++; x.jumlah += m.selisih; if (m.selisih > 0) x.lebih += m.selisih; else x.kurang += m.selisih; } });
  return Object.keys(per).map((k) => per[k]).sort((a, b) => b.n - a.n || a.nama.localeCompare(b.nama));
}
/** Malam berselisih yang masih "dicari besok" dan belum dijelaskan (TERLAMA dulu). */
export function lhPerluJelas(kini) { return lhMalam(kini).filter((m) => m.perluJelas).reverse(); }

/** Sumber pengingat (app.js lewat lokal.laci, OWNER saja — angka uang): 'laci' = alarm berulang · 'jelaskan' = selisih yang dicari besok, ditagih sampai dijelaskan. */
export function lhSumberPengingat(kini) {
  const iso = hariIniIso(kini); const out = []; const L = lhAlarm(kini);
  if (L.nyala && L.terakhir) out.push({ id: 'laci|' + L.terakhir.tanggal, jenis: 'laci', kunci: L.terakhir.tanggal, teks: 'Selisih laci berulang', siapa: 'tutup hari', jatuh: iso, n: L.lebih - L.kurang, ket: L.kalimat + ' — Uang › Tutup hari' });
  lhPerluJelas(kini).forEach((m) => out.push({ id: 'jelaskan|' + m.tanggal, jenis: 'jelaskan', kunci: m.tanggal, teks: 'Selisih laci ' + tanggalPendek(m.tanggal) + ' belum dijelaskan', siapa: 'tutup hari', jatuh: lhTambah(m.tanggal, 1),
    n: Math.abs(m.selisih), ket: (m.selisih > 0 ? 'lebih ' : 'kurang ') + RP(Math.abs(m.selisih)) + ' · tulis penjelasannya di Uang › Tutup hari › Selisih laci' }));
  return out;
}

/** Tulis penjelasan susulan satu malam (owner). Dokumen tutupHari malam itu ditulis ulang apa adanya + penjelasan { teks, tanggal, jam } (riwayat tutup tidak bertambah). */
export function susunJelaskanLaci(tanggal, teks, w) {
  const d = ambilTutupHari().find((x) => x && x.tanggal === String(tanggal)); if (!d) return { tolak: 'Malam ' + tanggalPendek(tanggal) + ' tidak ditemukan — muat ulang' };
  const t = lhTeks(teks); if (t.length < LH_BATAS.penjelasan[0]) return { tolak: 'Tulis penjelasannya (paling sedikit ' + LH_BATAS.penjelasan[0] + ' huruf)' };
  if (t.length > LH_BATAS.penjelasan[1]) return { tolak: 'Penjelasan paling panjang ' + LH_BATAS.penjelasan[1] + ' huruf' };
  const data = Object.assign({}, d, { penjelasan: { teks: t, tanggal: w.tanggal, jam: w.jam } });
  return { dokumen: [{ koleksi: 'tutupHari', data }], patch: { lhJelas: null, kabarAwas: false, kabar: 'Penjelasan selisih ' + tanggalPendek(d.tanggal) + ' disimpan — pengingatnya berhenti' } };
}
/** Simpan setelan alarm (owner): aturanToko/selisihLaci { alarmBeruntun, alarmDalam, alarmJendela, nyala }. Kosong = bawaan. */
export function susunAturLaci(isi, w) {
  const A = lhAtur(); const kosong = (v) => v === undefined || v === null || String(v).trim() === '';
  const baca = (k, lo, hi, kata) => { if (kosong(isi[k])) return { n: A[k === 'alarmBeruntun' ? 'beruntun' : k === 'alarmDalam' ? 'dalam' : 'jendela'] }; const n = Number(String(isi[k]).trim()); if (!Number.isInteger(n) || n < lo || n > hi) return { tolak: kata + ' harus bilangan bulat ' + lo + '–' + hi }; return { n }; };
  const J = baca('alarmJendela', LH_BATAS.alarmJendela[0], LH_BATAS.alarmJendela[1], 'Jumlah malam yang dilihat'); if (J.tolak) return J;
  const B = baca('alarmBeruntun', LH_BATAS.alarmBeruntun[0], LH_BATAS.alarmBeruntun[1], 'Malam berturut-turut'); if (B.tolak) return B;
  const D = baca('alarmDalam', 1, J.n, 'Malam berselisih dari ' + J.n + ' malam'); if (D.tolak) return D;
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: LH_ID, tanggal: w.tanggal, jam: w.jam, alarmBeruntun: B.n, alarmDalam: D.n, alarmJendela: J.n, nyala: isi.nyala !== false } }],
    patch: { kabarAwas: false, kabar: 'Alarm selisih laci: ' + B.n + ' malam berturut-turut atau ' + D.n + ' dari ' + J.n + ' malam' + (isi.nyala === false ? ' — DIMATIKAN' : '') } };
}

/** Dasbor (kartu Hari ini, owner): malam terakhir · alarm · belum dijelaskan · tren 7 malam — angka yang SAMA dengan Uang › Tutup hari. */
export function lhDasbor(kini) {
  const L = lhAlarm(kini); const T = lhTren(kini, 7); const J = lhPerluJelas(kini);
  return { terakhir: L.terakhir, alarm: { nyala: L.nyala, beruntun: L.beruntun, dalam: L.dalam, jendela: L.jendela, kalimat: L.kalimat, A: L.A }, belumJelas: J.length, belumJelasDaftar: J.slice(0, 4),
    tren: T.malam.map((m) => ({ tanggal: m.tanggal, selisih: m.selisih, lewat: m.lewat })), maaf: L.A.maaf, sumber: L.sumber, tujuan: L.tujuan };
}
