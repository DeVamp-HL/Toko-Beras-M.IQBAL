// POTRET TAHUN YANG DITUTUP (Paket B siap 2027, owner 7 Okt 2026) — tanpa DOM; pembantu berawalan `pt` (bundel uji jsc satu lingkup).
// Tutup buku memindah catatan tahun lama ke arsip (tidak dimuat ke memori — kuota baca). Tanpa potret, Laporan, Pajak & Dasbor tahun itu jadi Rp0 bertanda FINAL
// sesudah ritual, padahal setoran PPh masa Desember (tempo 15 Jan) dan SPT Tahunan (31 Mar) justru dikerjakan sesudahnya. Karena itu saat tahun DIKUNCI
// (tutup-buku-logika susunKunci, sebelum arsip) potret tahun itu ditulis ke berita acaranya (tutupBukuAcara/{tahun}.potret — owner saja, ikut kiriman berita
// acara yang sudah ada; rules tidak berubah). Isinya KELUARAN fungsi sumber yang SAMA dengan layar — tidak ada rumus baru:
//   per bulan : pjOmzetSistem & pjPotonganBulan (Pajak, DK3, Bulanan) · labaBulan (Laba; L = ugLabaBersih bulan itu) · keManaLabaKotor · intiBulan ·
//               hitungArusKasInti (arus kas berkop) · kendaliPotret (Biaya: jumlah per jenis + bahan pemicu) · lpKasAkhirBulan + neracaPada akhir bulan (Neraca) ·
//               kasPada akhir bulan (kas awal arus kas yang belum final);
//   per hari  : hitungLabaRentang + jumlahNota hari itu (Harian, Mingguan, tren Dasbor) — hanya hari yang punya nota/retur;
//   setahun   : nota pertama sistem (pjAwalSistem) & catatan pertama toko (lpPertama) · perkiraan pajak per masa saat dikunci (CATATAN untuk berita acara —
//               layar Pajak menghitung ulang dari angka bulan + isian di luar sistem & setoran yang tetap hidup).
// Daftar per catatan (nota rugi, nota tanpa modal, baris susut, rincian uang keluar per jenis, buku kas per gerakan, per jam) TIDAK dipotret — jumlahnya
// disimpan & layar menyebut "sudah diarsip". Pembaca: toko.js potretBulan / potretHari (satu aturan: tahun ≤ era + berita acara terkunci/selesai).
// Dijaga alat-uji/uji_potret_tahun.py: sebelum ritual = sesudah ritual, rupiah demi rupiah, per layar.
import { hitungLabaRentang, hitungArusKasInti, bayaranBiayaBulanan, kasPada } from '../mesin/beku.js';
import { akhirBulanIso } from '../mesin/pembantu.js';
import { ambilPenjualanSemua, ambilRetur, jumlahNota } from '../data/toko.js';
import { RP, hariIniIso } from '../inti/format.js';
import { pjOmzetSistem, pjPotonganBulan, pjAwalSistem, pjTahun } from './pajak-logika.js';
import { lpPertama, labaBulan, keManaLabaKotor, intiBulan, neracaPada, lpKasAkhirBulan } from './laporan-logika.js';
import { kendaliPotret } from './kendali-biaya-logika.js';

export const PT_VERSI = 1;
/** Bentuk yang bisa disimpan Firestore: tanpa fungsi & tanpa undefined (keduanya hilang lewat JSON). */
const ptBersih = (o) => JSON.parse(JSON.stringify(o));
const ptAngka = (o) => { const out = {}; Object.keys(o || {}).forEach((k) => { if (typeof o[k] === 'number' && isFinite(o[k])) out[k] = o[k]; }); return out; };
const ptTanpa = (o, buang) => { const out = {}; Object.keys(o || {}).forEach((k) => { if (buang.indexOf(k) < 0 && typeof o[k] !== 'function') out[k] = o[k]; }); return out; };
const ptNota = (d) => new Set(d.map((x) => x.nota)).size;

/** Satu bulan: keluaran fungsi layar yang sama, tanpa daftar per catatan (jumlahnya di `dalamArsip`). */
function ptBulanPotret(key, kini, B) {
  const S = pjOmzetSistem(key); const LB = labaBulan(key, kini, B); const KM = keManaLabaKotor(key, kini, B); const IN = intiBulan(key, kini, B);
  const K = hitungArusKasInti((t) => !!t && t >= key + '-01' && t <= akhirBulanIso(key), B); const KA = lpKasAkhirBulan(key);
  return {
    omzet: S.omzet, n: S.n, potongan: pjPotonganBulan(key), L: ptAngka(LB.L),
    lb: Object.assign(ptTanpa(LB, ['key', 'nama', 'berjalan', 'final', 'L', 'margin', 'labaBersih', 'susut', 'rugi', 'tanpaHpp', 'aman', 'pct']),
      { dalamArsip: { nRugi: LB.rugi.length, nRugiNota: ptNota(LB.rugi), rugiRp: LB.rugi.reduce((a, x) => a + x.margin, 0), nTanpaHpp: LB.tanpaHpp.length, nTanpaHppNota: ptNota(LB.tanpaHpp), nSusut: LB.susut.length } }),
    km: ptTanpa(KM, ['key', 'nama', 'berjalan', 'final', 'L', 'pct']), inti: ptTanpa(IN, ['key', 'nama', 'berjalan', 'final']), kb: kendaliPotret(key, kini, B),
    K: { masuk: K.masuk, keluar: K.keluar, pos: K.pos, totalMasuk: K.totalMasuk, totalKeluar: K.totalKeluar, bersih: K.bersih, omzetPenuh: K.omzetPenuh, kreditBulanIni: K.kreditBulanIni, jumlahKredit: K.jumlahKredit },
    // neraca akhir bulan dengan kas akhir bulan dari hitungan tutup hari — sesudah tutup buku bulan ini FINAL, dan bulan final memakai dasar itu (39b no. 36)
    kas: KA, neraca: neracaPada(akhirBulanIso(key), kini, KA),
    // sanggahan Paket B: kas akhir bulan menurut TITIK KAS (kasPada) saat dikunci — kas awal arus kas yang belum final (mis. Nov – Jan dibuka Januari). Sesudah
    // ritual titik kas pindah ke 31 Des dan mesin tidak menghitung mundur; tanpa ini kas awalnya hilang. null = memang tidak bisa dihitung saat dikunci.
    kasTitik: kasPada(akhirBulanIso(key)),
  };
}
/** Hari yang punya nota atau retur di tahun itu → [omzet, margin, baris tanpa modal, uang retur, nota] (hitungLabaRentang + jumlahNota hari itu). */
function ptHariPotret(tahun) {
  const awal = tahun + '-01-01', akhir = tahun + '-12-31'; const ada = {};
  ambilPenjualanSemua().forEach((p) => { const t = p && p.tanggal; if (t && t >= awal && t <= akhir) ada[t] = true; });
  ambilRetur().forEach((r) => { const t = r && r.tanggal; if (t && t >= awal && t <= akhir) ada[t] = true; });
  const out = {}; Object.keys(ada).sort().forEach((t) => { const R = hitungLabaRentang((x) => x === t); const n = jumlahNota((x) => x === t); if (R.omzetPenuh || R.margin || R.jumlahTanpaHpp || R.returUang || n) out[t] = [R.omzetPenuh, R.margin, R.jumlahTanpaHpp, R.returUang, n]; });
  return out;
}
/** POTRET satu tahun dari catatan HIDUP (dipanggil sebelum arsip). `kini` = jam ritual. */
export function susunPotret(tahun, kini, bayaran) {
  const B = bayaran || bayaranBiayaBulanan(); const th = Number(tahun); const bulan = {};
  for (let m = 1; m <= 12; m++) { const key = th + '-' + String(m).padStart(2, '0'); bulan[key] = ptBulanPotret(key, kini, B); }
  const T = pjTahun(th, kini); const P = T.P;
  return ptBersih({ versi: PT_VERSI, tahun: th, cutoff: th + '-12-31', dibuat: hariIniIso(kini), awalSistem: pjAwalSistem(), pertama: lpPertama(), bulan, hari: ptHariPotret(th),
    pajak: { catatan: 'perkiraan saat tahun dikunci — layar Pajak menghitung ulang dari angka bulan potret + isian di luar sistem & setoran yang hidup', totalSistem: T.totalSistem, totalSebelumPotongan: T.totalSebelumPotongan, totalPph: T.totalPph, totalSetor: T.totalSetor, kosong: T.kosong,
      profil: { jenisWp: P.jenisWp, statusPasangan: P.statusPasangan, tarifPerMil: P.tarifPerMil, batasBebas: P.batasBebas, batasOmzet: P.batasOmzet },
      daftar: T.daftar.map((b) => ({ key: b.key, sistem: b.sistem, sebelumPotongan: b.sebelumPotongan, lama: b.lama, lain: b.lain, pasangan: b.pasangan, omzet: b.omzet, kum: b.kum, pph: b.pph, jumlahSetor: b.jumlahSetor, ntpn: b.ntpn, status: b.status.teks })) } });
}
/** Satu kalimat untuk layar tutup buku & berita acara: apa yang dipotret. */
export function ringkasPotret(Pt) {
  const kk = Object.keys(Pt.bulan || {}); const omzet = kk.reduce((a, k) => a + (Number(Pt.bulan[k].omzet) || 0), 0); const laba = kk.reduce((a, k) => a + (Number(Pt.bulan[k].L && Pt.bulan[k].L.labaBersih) || 0), 0);
  const D = Pt.bulan[Pt.tahun + '-12'] || {}; const N = D.neraca || {}; const nHari = Object.keys(Pt.hari || {}).length;
  return 'Potret ' + Pt.tahun + ': ' + kk.length + ' bulan & ' + nHari + ' hari berjualan · omzet sistem ' + RP(omzet) + ' · laba bersih ' + RP(laba) + ' · neraca 31 Des ' + (N.total === null || N.total === undefined ? 'belum bisa dihitung' + (N.tolak ? ' (' + N.tolak + ')' : '') : RP(N.total)) + ' — Laporan, Pajak & Dasbor ' + Pt.tahun + ' membaca angka ini sesudah arsip.';
}
