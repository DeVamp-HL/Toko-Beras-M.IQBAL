// KUARTAL (owner 24 Nov 2026 — paket Pondasi kedua: "ada Kuartal 1, 2 dan seterusnya"). Logika TANPA DOM, nama berawalan kw (bundel uji jsc satu lingkup).
// Dijaga alat-uji/uji_kuartal.py.
//
// ATURAN (sama dengan pondasi-logika & kpi-laba-logika): HANYA MEMBACA. Satu kuartal = JUMLAH tiga bulan dari rekapTahun (Laporan › Tahunan — mesin laba yang
// sama, termasuk bulan di tahun yang sudah ditutup buku dari potretnya), jadi Σ empat kuartal = angka tahun persis; pemeriksanya ikut dikembalikan (kwTahun).
// Kekayaan akhir kuartal = neracaPada + kas dari hitungan tutup hari akhir bulan (lpKasAkhirBulan). Potret lampu kuartal memakai ATURAN WARNA pondasi-logika
// (pdLampu…, ambang owner yang sama). Yang tidak bisa dihitung DISEBUT (null + sebab), tidak dianggap 0:
//   · kuartal yang belum utuh (catatan toko baru mulai di tengahnya, atau masih berjalan) ditandai dan tidak dibandingkan apel-ke-apel;
//   · bulan di tahun yang ditutup tanpa potret → angka kuartalnya null.
import { rekapTahun, lpPertama, lpNamaBulan, neracaPada, lpKasAkhirBulan } from './laporan-logika.js';
import { priveRentang } from './uang-logika.js';
import { pdAtur, pdLampuAtas, pdLampuHasil, pdLampuAmbil, pdPctTeks, pdPorsiPemasok, pdAkhirBulan } from './pondasi-logika.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';

const kwDua = (n) => String(n).padStart(2, '0');
const kwBilangan = (n) => typeof n === 'number' && isFinite(n);
/** 'YYYY-MM-DD' / 'YYYY-MM' → 'YYYY-K1'…'YYYY-K4'. */
export const kwKey = (iso) => String(iso).slice(0, 4) + '-K' + (Math.floor((Number(String(iso).slice(5, 7)) - 1) / 3) + 1);
export const kwTahunDari = (key) => Number(String(key).slice(0, 4));
export const kwNomor = (key) => Number(String(key).slice(6, 7));
/** Tiga bulan satu kuartal: 'YYYY-K4' → ['YYYY-10', 'YYYY-11', 'YYYY-12']. */
export const kwBulan = (key) => { const t = kwTahunDari(key), q = kwNomor(key); return [0, 1, 2].map((i) => t + '-' + kwDua((q - 1) * 3 + 1 + i)); };
export const kwRentang = (key) => { const b = kwBulan(key); return { awal: b[0] + '-01', akhir: pdAkhirBulan(b[2]) }; };
/** Geser n kuartal (negatif = mundur). */
export const kwGeser = (key, n) => { const i = kwTahunDari(key) * 4 + (kwNomor(key) - 1) + n; return Math.floor(i / 4) + '-K' + ((i % 4 + 4) % 4 + 1); };
export const kwNama = (key) => 'K' + kwNomor(key) + ' ' + kwTahunDari(key);
const kwPersen = (a, b) => (kwBilangan(a) && kwBilangan(b) && b !== 0 ? (a - b) / Math.abs(b) * 100 : null);

/** Daftar kuartal dari catatan pertama toko sampai kuartal berjalan, TERBARU dulu. */
export function kwDaftar(kini) {
  const iso = hariIniIso(kini); const akhir = kwKey(iso); const p = lpPertama(); const awal = p ? kwKey(p) : akhir; const out = []; let k = akhir;
  while (k >= awal && out.length < 40) { out.push({ key: k, nama: kwNama(k), berjalan: k === akhir }); k = kwGeser(k, -1); }
  return out;
}

/** Angka inti satu kuartal dari rekapTahun (tanpa banding & kekayaan — dipakai juga untuk kuartal pembanding). */
function kwInti(key, kini) {
  const iso = hariIniIso(kini); const R = rekapTahun(kwTahunDari(key), kini); const kunci = kwBulan(key); const rentang = kwRentang(key); const p = lpPertama();
  const bulan = R.bulan.filter((b) => kunci.indexOf(b.key) >= 0); const ada = bulan.filter((b) => !b.depan && !b.sebelumBuku);
  const tanpaPotret = ada.some((b) => b.tanpaPotret); const jml = (k) => (tanpaPotret ? null : ada.reduce((a, b) => a + (Number(b[k]) || 0), 0));
  const berjalan = key === kwKey(iso); const depan = rentang.awal > iso; const mulaiTengah = !!p && p > rentang.awal && p <= rentang.akhir;
  const utuh = !berjalan && !depan && !mulaiTengah && ada.length === 3 && !tanpaPotret;
  const sebab = depan ? 'belum mulai' : tanpaPotret ? 'sebagian bulannya hanya ada di berkas arsip (tutup buku tanpa potret)' : mulaiTengah ? 'catatan toko baru mulai ' + tanggalPendek(p) + ', jadi kuartal ini tidak utuh'
    : berjalan ? 'masih berjalan — sampai ' + tanggalPendek(iso) : !ada.length ? 'tidak ada catatan' : '';
  return { key, nama: kwNama(key), awal: rentang.awal, akhir: rentang.akhir, sampai: berjalan ? iso : rentang.akhir, bulan, nBulan: ada.length, berjalan, depan, utuh, sebab, tanpaPotret, diarsip: ada.some((b) => b.diarsip),
    omzet: jml('omzet'), nota: jml('n'), labaKotor: jml('margin'), biaya: jml('biaya'), susut: jml('susut'), lebihKurangKas: jml('kas'), labaBersih: jml('labaBersih') };
}

/** Kekayaan toko pada akhir kuartal (kuartal berjalan: hari ini). Kas akhir bulan lampau = hitungan fisik tutup hari akhir bulan itu (lpKasAkhirBulan). */
export function kwKekayaan(key, kini) {
  const iso = hariIniIso(kini); const r = kwRentang(key); const berjalan = key === kwKey(iso);
  if (r.awal > iso) return { ada: false, per: r.akhir, kenapa: 'kuartal ini belum mulai' };
  let N, KB = null; try { KB = berjalan ? null : lpKasAkhirBulan(r.akhir.slice(0, 7)); N = berjalan ? neracaPada(null, kini) : neracaPada(r.akhir, kini, KB); } catch (e) { return { ada: false, per: berjalan ? iso : r.akhir, kenapa: 'gagal dihitung: ' + String((e && e.message) || e) }; }
  const per = berjalan ? iso : r.akhir;
  if (!N || !kwBilangan(N.aset) || !kwBilangan(N.kewajiban)) return { ada: false, per, kenapa: KB && KB.kas === null && KB.kenapa ? 'Uang toko akhir kuartal belum bisa dihitung — ' + KB.kenapa : (N && N.tolak) || 'Uang toko pada tanggal itu belum bisa dihitung' };
  return { ada: true, per, aset: N.aset, kewajiban: N.kewajiban, bersih: N.aset - N.kewajiban, utangPemasok: N.N ? N.N.utangPemasok : null, stok: N.N ? N.N.stok : null, kas: N.N ? N.N.kas : null };
}

/**
 * Satu kuartal lengkap: angka (Σ tiga bulan) + ambil pribadi + banding kuartal sebelumnya + kekayaan akhir kuartal + potret lima lampu pondasi yang bisa
 * dihitung untuk masa lampau (utang dibanding harta, hasil atas harta, ambil pribadi dibanding laba, laju omzet, porsi pemasok terbesar).
 * Lampu bon pemasok & prakiraan TIDAK ikut: keduanya hanya bisa dihitung untuk hari ini.
 */
export function kwRekap(key, kini) {
  const iso = hariIniIso(kini); const Q = kwInti(key, kini); const L = kwInti(kwGeser(key, -1), kini); const A = pdAtur();
  // ambil pribadi: catatan tahun yang sudah ditutup buku ikut arsip — tidak dihitung dari catatan hidup (disebut, bukan Rp0)
  const prive = Q.depan || Q.diarsip || Q.tanpaPotret ? null : priveRentang(Q.awal, Q.sampai).total;
  const tinggal = kwBilangan(Q.labaBersih) && kwBilangan(prive) ? Q.labaBersih - prive : null;
  const setara = Q.utuh && L.utuh; const pctOmzet = kwPersen(Q.omzet, L.omzet); const pctLaba = kwPersen(Q.labaBersih, L.labaBersih);
  const banding = { key: L.key, nama: L.nama, ada: L.nBulan > 0 && kwBilangan(L.omzet), setara, omzet: L.omzet, labaBersih: L.labaBersih, pctOmzet, pctLaba,
    teks: !(L.nBulan > 0) || !kwBilangan(L.omzet) ? 'Belum ada ' + L.nama + ' untuk dibandingkan' + (L.sebab ? ' (' + L.sebab + ')' : '') + '.'
      : 'Dibanding ' + L.nama + ': omzet ' + (pctOmzet === null ? '—' : (pctOmzet >= 0 ? 'naik ' : 'turun ') + pdPctTeks(Math.abs(pctOmzet))) + ', laba bersih ' + RP(L.labaBersih) + ' → ' + RP(Q.labaBersih) + '.'
        + (setara ? '' : ' BUKAN banding setara: ' + [Q.utuh ? '' : Q.nama + ' ' + Q.sebab, L.utuh ? '' : L.nama + ' ' + L.sebab].filter(Boolean).join(' · ') + '.') };
  const K = kwKekayaan(key, kini); const KL = kwKekayaan(kwGeser(key, -1), kini);
  const naik = K.ada && KL.ada ? K.bersih - KL.bersih : null;
  // potret lampu
  const lampu = []; const tambah = (id, nama, lampuWarna, nilai, kalimat) => lampu.push({ id, nama, lampu: lampuWarna, nilai, kalimat });
  if (K.ada && K.aset > 0) { const pct = K.kewajiban / K.aset * 100; tambah('utang', 'Utang dibanding harta', pdLampuAtas(pct, A.utangMaks), pdPctTeks(pct), 'Per ' + tanggalPendek(K.per) + ': harta ' + RP(K.aset) + ', utang ' + RP(K.kewajiban) + '.'); }
  else tambah('utang', 'Utang dibanding harta', 'tanpa', 'belum bisa', K.kenapa || 'Harta toko pada akhir kuartal belum bisa dihitung.');
  if (K.ada && K.aset > 0 && kwBilangan(Q.labaBersih)) { const hari = Math.max(1, Math.round((Date.parse(Q.sampai) - Date.parse(Q.awal)) / 86400000) + 1); const per30 = Q.labaBersih / K.aset * 100 * 30 / hari;
    tambah('hasil', 'Hasil atas harta', pdLampuHasil(Q.labaBersih, per30, A.hasilMin), pdPctTeks(per30) + ' / 30 hari', 'Laba bersih ' + Q.nama + ' ' + RP(Q.labaBersih) + ' selama ' + hari + ' hari, dibanding harta ' + RP(K.aset) + ' — disetarakan per 30 hari supaya bisa dibandingkan dengan lampu Pondasi.'); }
  else tambah('hasil', 'Hasil atas harta', 'tanpa', 'belum bisa', 'Laba bersih atau harta kuartal ini belum bisa dihitung.');
  if (kwBilangan(prive) && kwBilangan(Q.labaBersih)) tambah('ambil', 'Ambil pribadi dibanding laba', pdLampuAmbil(prive, Q.labaBersih, false), !(prive > 0) ? 'tidak ada ambil' : tinggal < 0 ? 'toko mengecil ' + RP(-tinggal) : 'tinggal ' + RP(tinggal),
    'Laba bersih ' + RP(Q.labaBersih) + ', ambil pribadi ' + RP(prive) + ' — ' + (!(prive > 0) ? 'tidak ada yang diambil.' : tinggal < 0 ? 'yang diambil lebih besar ' + RP(-tinggal) + ' dari yang dihasilkan.' : 'yang tinggal di toko ' + RP(tinggal) + '.'));
  else tambah('ambil', 'Ambil pribadi dibanding laba', 'tanpa', 'belum bisa', 'Catatan ambil pribadi kuartal ini sudah diarsip (tutup buku) atau labanya belum bisa dihitung.');
  tambah('tumbuh', 'Laju omzet', 'tanpa', pctOmzet === null ? 'belum bisa' : (pctOmzet > 0 ? '+' : '') + pdPctTeks(pctOmzet), banding.teks);
  if (!Q.depan && !Q.diarsip) { const P = pdPorsiPemasok(Q.awal, Q.sampai);
    if (P.total > 0) tambah('pemasok', 'Bergantung pada satu pemasok', pdLampuAtas(P.pct, A.pemasokMaks), pdPctTeks(P.pct), 'Belanja beras ' + Q.nama + ' ' + RP(P.total) + ' dari ' + P.daftar.length + ' pemasok; terbesar ' + P.daftar[0].nama + ' ' + RP(P.daftar[0].rp) + '.');
    else tambah('pemasok', 'Bergantung pada satu pemasok', 'tanpa', 'belum bisa', 'Tidak ada kedatangan beras bernilai di kuartal ini.'); }
  else tambah('pemasok', 'Bergantung pada satu pemasok', 'tanpa', 'belum bisa', 'Kedatangan kuartal ini sudah diarsip (tutup buku) atau kuartalnya belum mulai.');
  return Object.assign({}, Q, { prive, tinggal, banding, kekayaan: K, kekayaanLalu: KL, kekayaanNaik: naik, lampu,
    status: Q.depan ? 'belum mulai' : Q.utuh ? 'utuh · ' + lpNamaBulan(kwBulan(key)[0]).split(' ')[0] + ' – ' + lpNamaBulan(kwBulan(key)[2]) : 'TIDAK UTUH — ' + Q.sebab,
    kalimat: Q.depan ? Q.nama + ' belum mulai.' : !kwBilangan(Q.omzet) ? Q.nama + ' belum bisa dihitung — ' + Q.sebab + '.'
      : Q.nama + ': omzet ' + RP(Q.omzet) + ' dari ' + Q.nota + ' nota, laba bersih ' + RP(Q.labaBersih) + (kwBilangan(prive) ? ', ambil pribadi ' + RP(prive) : '') + '.' });
}

/** Empat kuartal satu tahun + pemeriksa: Σ kuartal = angka tahun Laporan › Tahunan (omzet, laba kotor, biaya, laba bersih). */
export function kwTahun(tahun, kini) {
  const R = rekapTahun(tahun, kini); const kuartal = [1, 2, 3, 4].map((q) => kwInti(tahun + '-K' + q, kini));
  const jml = (k) => kuartal.reduce((a, x) => a + (Number(x[k]) || 0), 0); const sama = (a, b) => b === null || b === undefined || Math.abs(a - b) < 0.5;
  const beda = [['omzet', 'omzet', R.omzet], ['laba kotor', 'labaKotor', R.margin], ['biaya', 'biaya', R.biaya], ['laba bersih', 'labaBersih', R.labaBersih]].filter((x) => !sama(jml(x[1]), x[2])).map((x) => x[0]);
  return { tahun, kuartal, omzet: jml('omzet'), labaBersih: jml('labaBersih'), menutup: !beda.length, beda, tahunan: { omzet: R.omzet, labaBersih: R.labaBersih, status: R.status },
    kalimat: beda.length ? 'TIDAK MENUTUP ke Laporan › Tahunan: ' + beda.join(', ') + ' — jangan dipakai memutuskan; laporkan.' : 'Σ empat kuartal = angka ' + tahun + ' di Laporan › Tahunan (omzet, laba kotor, biaya, laba bersih).' };
}
