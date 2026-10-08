// HEMAT BACA (owner 7 Okt 2026 — siap 2027; keputusan K1: tetap Spark + hemat baca, menyala ≤ 20 Nov). Logika MURNI: tanpa impor Firebase, tanpa DOM,
// tanpa setTimeout sendiri — jam, jadwal, penyimpan, dan "SDK" disuntikkan. firebase.js memasang adaptor SDK sungguhan; alat-uji/uji_hemat_baca.py
// memasang server mainan di jsc. Spesifikasi lengkap: docs/rancangan-hemat-baca.md (ringkasan rancangan 6 agen + keputusan owner 3 Okt).
//
// SAKLAR bawaan MATI, disimpan PER PERANGKAT (HB_KUNCI_SAKLAR, owner menekannya di Menu › Toko ini › Perangkat & antrean › Hemat baca). Saklar MATI = pendengar penuh
// seperti sebelum 7 Okt; dari berkas ini hanya ini yang ikut jalan: kupas (capServer dibuang dari isi dokumen SEBELUM masuk memori — mesin, cadangan,
// katalog tidak pernah melihatnya), cap (tulisan koleksi hemat membawa capServer = jam SERVER), batu nisan (hapus koleksi hemat — hanya sesudah aturan v7
// terbukti terpasang di perangkat ini), versi denyut 'baru-c1'.
// Saklar NYALA (owner saja; akun staf tetap penuh):
//   V = pendengar SIMPANAN PERANGKAT per koleksi (source 'cache', 0 baca) — satu-satunya pemasok memori, disaring batu nisan;
//   S = pendengar server `capServer > B` (B = tanda air koleksi itu di perangkat ini − 60 menit) — menarik ubahan ke simpanan;
//   F = baca penuh (kueri SENDIRI limit 1.000.000 — tidak pernah "selesai" dari view lama) — harian per TOKO oleh perangkat owner pertama sesudah reset kuota
//       (14.00 WIB s/d 31 Okt, 15.00 WIB mulai 1 Nov), ≤ 14 hari sekali per perangkat, dan tiap kali ragu (simpanan kosong, hitungan server beda, penulis tanpa cap);
//   N = batu nisan `capServer > Bn` — kabar hapus untuk catatan lama yang tidak ikut jendela S. Nisan hanya menyembunyikan versi yang LEBIH TUA darinya
//       (catatan yang dibuat lagi sesudah dihapus — bercap lebih baru, atau terlihat masih ada di baca penuh SERVER — tampil).
// Jam: semua batas memakai capServer (jam server), BUKAN jam perangkat — jam perangkat yang mundur tidak menggeser tanda air. Jam server perangkat ini HANYA
// dari gema denyut sendiri (tinjauan 7 Okt): cap di data tidak pernah menggeser jam — satu catatan ber-cap tahun 2099 tidak menyeret tanda air ke sana.
import { KOLEKSI } from './koleksi.js';
import { kpNomorVersiKasir } from './kunci-periode.js';

export const HB_VERSI = 'baru-c1';                 // versi denyut /baru/ yang mengecap (daftar siap-nyala; versi lain = penulis tanpa cap)
export const HB_VERSI_KASIR_CAP = 'kasir-v33';     // kasir darurat PERTAMA yang mengecap nota (REST :commit + REQUEST_TIME)
export const HB_MULAI_MS = Date.UTC(2026, 9, 7);   // kode bercap ditulis 7 Okt 2026 — catatan tanpa cap sesudahnya = penulis lama masih jalan
export const HB_MARGIN_MS = 3600000;               // B = tanda air − 60 menit (commit bisa lebih lambat dari jam permintaan)
export const HB_JEPIT_MS = 600000;                 // tanda air tidak pernah lebih dari jam server + 10 menit (cap 2099 dari Console tidak membekukan delta)
export const HB_REBASE_MS = 28800000;              // B digeser maju paling cepat 8 jam sekali …
export const HB_REBASE_MAKS = 3;                   // … paling banyak 3 target S per koleksi per hari kuota
export const HB_BARU_MENIT = 15;                   // tab /baru/ versi lama berdenyut ≤ 15 menit → semua koleksi dengar penuh
export const HB_KASIR_HARI = 14;                   // HP kasir tanpa cap / kasir.html berdenyut ≤ 14 hari → koleksinya dengar penuh
export const HB_SEGAR_MS = 120000;                 // uang-kritis (tutup hari, kunci bulan, tutup buku): hitungan server ≤ 2 menit
export const HB_BERKALA_MS = 1800000;              // hitungan berkala koleksi tulisan HP kasir: 30 menit
export const HB_KATALOG_SEGAR_MS = 2100000;        // katalog kasir terbit hanya kalau hitungan koleksi HP kasir ≤ 35 menit
export const HB_HIDUP_MS = 5000;                   // ubahan yang dibawa S/F wajib terlihat di V dalam 5 detik (pendengar simpanan hidup)
export const HB_LIMIT_F = 1000000;
export const HB_KUOTA = 50000;                     // Spark: 50 rb baca / hari
export const HB_REM = 0.8;                         // baca penuh OTOMATIS ditunda kalau perkiraan baca hari ini > 80% kuota
export const HB_SENTUH_MAKS = 400;                 // pendeteksi: lebih dari ini → semua perangkat baca penuh koleksi itu (gen), bukan disentuh satu-satu
export const HB_TOTAL_HARI = 14;
export const HB_TAB_SEGAR_MS = 12000;
export const HB_TAB_DETAK_MS = 4000;
export const HB_KLAIM_BASI_MS = 1800000;           // klaim baca penuh harian yang belum selesai 30 menit boleh diambil perangkat lain
export const HB_ULANG_MAKS = 5;                    // temuan pendeteksi yang gagal dikirim dicoba lagi tiap menit, paling banyak 5 kali
export const HB_KOLEKSI_REST = ['penjualan', 'stokBahanLiteran', 'piutangMutasi'];   // koleksi yang (pernah) ditulis HP kasir lewat REST
export const HB_KOLEKSI_NISAN = 'batuNisan';
export const HB_ID_KLAIM = 'hematHarian';          // aturanToko/hematHarian = baca penuh harian per toko (+ gen "semua perangkat baca penuh")
export const HB_KUNCI_SAKLAR = 'miqbal_hemat_saklar_v1';
export const HB_KUNCI_REKAM = 'miqbal_hemat_v2';
export const HB_KUNCI_TAB = 'miqbal_baru_kunci_tab_v1';
export const HB_KUNCI_NISAN_SAH = 'miqbal_hemat_nisan_sah_v1';
const hbMenit = 60000, hbJam = 3600000, hbHari = 86400000;
const HB_BK_AKTIF = { berjalan: 1, terkunci: 1, membatalkan: 1 };
const hbAngka = (v) => (typeof v === 'number' && isFinite(v) ? v : null);

// ---------- kelas koleksi (koleksi.js `kelas`) ----------
export function hbKelas(nama) { const k = KOLEKSI.find((x) => x.nama === nama); return !k ? '' : k.kelas || 'hemat'; }
export const hbHemat = (nama) => hbKelas(nama) === 'hemat';
export const hbKoleksiHemat = () => KOLEKSI.filter((k) => !k.kelas).map((k) => k.nama);

// ---------- saklar per perangkat ----------
/** Saklar perangkat ini. penyimpan = { baca(k), tulis(k, v), hapus(k) } (localStorage). Tidak terbaca / rusak = MATI. */
export function hbSaklar(penyimpan) { try { return penyimpan.baca(HB_KUNCI_SAKLAR) === 'nyala'; } catch (e) { return false; } }
export function hbSetelSaklar(penyimpan, nyala) { try { if (nyala) penyimpan.tulis(HB_KUNCI_SAKLAR, 'nyala'); else penyimpan.hapus(HB_KUNCI_SAKLAR); return true; } catch (e) { return false; } }
/** Aturan v7 terbukti terpasang (batuNisan bisa dibaca owner) di perangkat ini untuk proyek ini. Sekali terbukti, tidak dicabut (v6 tidak boleh ditempel balik). */
export function hbNisanSah(penyimpan, proyek) { try { const v = JSON.parse(penyimpan.baca(HB_KUNCI_NISAN_SAH) || '{}'); return !!(v && v[proyek]); } catch (e) { return false; } }
export function hbTandaiNisanSah(penyimpan, proyek, kiniMs) {
  try { const v = JSON.parse(penyimpan.baca(HB_KUNCI_NISAN_SAH) || '{}') || {}; if (v[proyek]) return true; v[proyek] = kiniMs; penyimpan.tulis(HB_KUNCI_NISAN_SAH, JSON.stringify(v)); return true; } catch (e) { return false; }
}

// ---------- jam: hari kuota = tanggal kalender Pasifik (reset kuota Spark "around midnight Pacific"), tanpa Intl ----------
function hbMingguKe(y, m, n, jamUtc) { const d1 = new Date(Date.UTC(y, m, 1)).getUTCDay(); return Date.UTC(y, m, 1 + ((7 - d1) % 7) + (n - 1) * 7, jamUtc); }
/** Jam musim panas AS: Minggu ke-2 Maret 10.00Z s/d Minggu ke-1 November 09.00Z. */
export function hbMusimPanasAS(ms) { const y = new Date(ms).getUTCFullYear(); return ms >= hbMingguKe(y, 2, 2, 10) && ms < hbMingguKe(y, 10, 1, 9); }
export function hbHariKuota(ms) { return new Date(ms + (hbMusimPanasAS(ms) ? -7 : -8) * hbJam).toISOString().slice(0, 10); }
/** Jam reset kuota dalam WIB untuk hari kuota yang memuat ms — '14.00' selama musim panas AS, '15.00' sesudahnya. */
export const hbJamResetWib = (ms) => (hbMusimPanasAS(ms) ? '14.00' : '15.00');
/** Awal hari kuota `hari` ('YYYY-MM-DD' Pasifik) dalam ms: tengah malam Pasifik = 07.00Z (musim panas AS) atau 08.00Z. Tanggal rusak = null. */
export function hbMulaiHariKuota(hari) { const t = Date.parse(String(hari || '') + 'T07:00:00Z'); if (!isFinite(t)) return null; return hbMusimPanasAS(t) ? t : t + hbJam; }
/** Jam reset (WIB, 'HH.MM') yang MEMULAI hari kuota `hari` — juga di hari pergantian jam musim panas AS. '' = hari tidak diketahui. */
export function hbJamResetHariWib(hari) { const t = hbMulaiHariKuota(hari); return t === null ? '' : ('0' + new Date(t + 7 * hbJam).getUTCHours()).slice(-2) + '.00'; }
const hbHariBerikut = (hari) => { const t = Date.parse(String(hari || '') + 'T12:00:00Z'); return isFinite(t) ? new Date(t + hbHari).toISOString().slice(0, 10) : ''; };

// ---------- cap server ----------
/** Nilai capServer → ms (Timestamp SDK), null (masih tertunda di perangkat ini), 'peta' (bukan jam server: angka/teks/peta tulisan tangan), undefined (tidak ada). */
export function hbCapMs(v) {
  if (v === undefined) return undefined;
  if (v === null) return null;
  if (typeof v === 'object' && typeof v.toMillis === 'function') { try { const n = v.toMillis(); return isFinite(n) ? n : 'peta'; } catch (e) { return 'peta'; } }
  return 'peta';
}
/** KUPAS: capServer & padaServer dibuang dari isi dokumen (objek dari data() — selalu objek baru per panggilan, jadi diubah di tempat). → nilai cap (hbCapMs). */
export function hbKupas(x) {
  if (!x || typeof x !== 'object') return undefined;
  let cap; if (Object.prototype.hasOwnProperty.call(x, 'capServer')) { cap = hbCapMs(x.capServer); delete x.capServer; }
  if (Object.prototype.hasOwnProperty.call(x, 'padaServer')) delete x.padaServer;
  return cap;
}
const hbUrutKunci = (v) => (Array.isArray(v) ? v.map(hbUrutKunci) : v && typeof v === 'object' ? (typeof v.toMillis === 'function' ? { _ms: v.toMillis() } : Object.keys(v).sort().reduce((o, k) => { o[k] = hbUrutKunci(v[k]); return o; }, {})) : v);
/** Sidik isi dokumen (tanpa capServer/padaServer), kunci diurutkan — Firestore tidak menjamin urutan kunci peta. */
export function hbSidik(x) { const y = Object.assign({}, x || {}); delete y.capServer; delete y.padaServer; return JSON.stringify(hbUrutKunci(y)); }
/** Pendeteksi statis: catatan TANPA cap jam server yang lahir/diubah sesudah batas (diubahPada, atau id = Date.now() untuk nota REST HP kasir). */
export function hbTanpaCapStatis(d, cap, batasMs) {
  if (typeof cap === 'number' || cap === null) return false;
  const u = Date.parse((d && d.diubahPada) || ''); if (isFinite(u) && u >= batasMs) return true;
  const i = Number(d && d.id); return isFinite(i) && i >= batasMs && i < batasMs + 400 * hbHari;
}

// ---------- rekam per perangkat (localStorage HB_KUNCI_REKAM = { skema, isi: { '<proyek>|<uid>': R } }) ----------
export const hbKunciRekam = (proyek, uid) => String(proyek || '') + '|' + String(uid || '');
const hbRekamBaru = (proyek, uid) => ({ skema: 2, proyek: String(proyek || ''), uid: String(uid || ''), skew: null, k: {}, hari: { H: '', otomatis: {}, mulai: {}, baca: 0 }, tanpaIdb: 0 });
/** Baca rekam akun ini. Tidak ada / rusak / skema lain = rekam KOSONG (akibatnya baca penuh — biaya, bukan angka salah). Rekam yang tidak dipakai 60 hari dibuang. */
export function hbBacaRekam(penyimpan, proyek, uid) {
  let semua = null; try { semua = JSON.parse(penyimpan.baca(HB_KUNCI_REKAM) || 'null'); } catch (e) { semua = null; }
  const R = semua && semua.skema === 2 && semua.isi ? semua.isi[hbKunciRekam(proyek, uid)] : null;
  if (!R || R.skema !== 2 || R.proyek !== String(proyek || '') || R.uid !== String(uid || '') || !R.k || typeof R.k !== 'object') return hbRekamBaru(proyek, uid);
  if (!R.hari || typeof R.hari !== 'object') R.hari = { H: '', otomatis: {}, mulai: {}, baca: 0 };
  return R;
}
export function hbSimpanRekam(penyimpan, R, kiniMs) {
  try {
    let semua = null; try { semua = JSON.parse(penyimpan.baca(HB_KUNCI_REKAM) || 'null'); } catch (e) { semua = null; }
    if (!semua || semua.skema !== 2 || !semua.isi) semua = { skema: 2, isi: {} };
    R.dipakai = kiniMs; semua.isi[hbKunciRekam(R.proyek, R.uid)] = R;
    Object.keys(semua.isi).forEach((kk) => { const x = semua.isi[kk]; if (!x || !(kiniMs - (Number(x.dipakai) || 0) <= 60 * hbHari)) delete semua.isi[kk]; });
    penyimpan.tulis(HB_KUNCI_REKAM, JSON.stringify(semua)); return true;
  } catch (e) { return false; }
}

// ---------- tanda air & batas ----------
/** Tanda air dijepit ≤ jam server + 10 menit. capMaks null (koleksi kosong) = jam server itu sendiri. */
export function hbJepit(capMaks, kiniS) { const c = hbAngka(capMaks); if (c === null) return kiniS; return Math.min(c, kiniS + HB_JEPIT_MS); }
/**
 * B koleksi k (S = capServer > B). Tetap SEHARI (hari kuota) supaya target S yang sama dipakai ulang; digeser maju bila > 8 jam di belakang jam server dan
 * tanda air sudah maju (≤ 3 kali sehari). Tanpa tanda air = null (koleksi wajib baca penuh dulu). Jam server belum diketahui = B lama dipakai (selalu aman:
 * B lebih tua = lebih banyak dibaca, tidak ada yang terlewat).
 */
export function hbBatasDelta(rk, kiniS, hari) {
  const r = rk || {}; const W = Math.max(hbAngka(r.Wt) || 0, hbAngka(r.Wd) || 0); if (!(W > 0)) return { B: null };
  const calon = W - HB_MARGIN_MS; const B0 = hbAngka(r.B);
  if (B0 !== null && B0 > 0) {
    if (!hari || r.hariB === hari) {
      if (hari && kiniS !== null && kiniS - B0 > HB_REBASE_MS && calon > B0 && (r.nB || 0) < HB_REBASE_MAKS) return { B: calon, hariB: hari, nB: (r.nB || 0) + 1, baru: true };
      return { B: Math.min(B0, calon), hariB: r.hariB, nB: r.nB || 0, baru: B0 > calon };
    }
  }
  return { B: calon, hariB: hari || r.hariB || '', nB: 0, baru: true };
}

// ---------- dasar dipercaya ----------
/** Simpanan perangkat ini (V pertama, c dokumen) boleh dipakai sebagai dasar? Tidak → baca penuh dulu (tirai "memuat" sampai selesai). */
export function hbDasarDipercaya(rk, c) {
  const r = rk || {};
  if (!(hbAngka(r.totalPada) > 0)) return { ya: false, sebab: 'belum pernah dibaca penuh di perangkat ini' };
  const n = Number(r.n) || 0;
  if (c === 0 && n >= 1) return { ya: false, sebab: 'simpanan perangkat kosong' };
  if (n >= 20 && c < n / 2) return { ya: false, sebab: 'simpanan perangkat tinggal ' + c + ' dari ' + n + ' catatan' };
  return { ya: true, sebab: '' };
}

// ---------- penulis tanpa cap (dari denyut perangkatStatus — koleksi tetap) ----------
/**
 * Jam denyut p: jam SERVER saat perangkat ini melihat denyut itu BERUBAH (lihat = { id: ms }, hbLihatDenyut) — `pada` ditulis jam perangkat PENULIS, dan tab
 * lama yang jamnya terlambat > 15 menit dulu dinilai "sudah lama" padahal baru saja menulis (tinjauan 7 Okt). Belum pernah terlihat berubah = `pada`.
 */
export function hbJamDenyut(p, lihat) { const s = lihat ? hbAngka(lihat[String(p && p.id)]) : null; return s !== null ? s : Date.parse((p && p.pada) || ''); }
/**
 * Catat jam server saat denyut tiap perangkat BERUBAH selagi perangkat ini mendengar. L = rekam { id: { pada, s } } (tahan lama), sesi = { id: pada } (sesi
 * ini). Berubah selagi tidak didengar (beda dengan rekam, belum terlihat sesi ini) = jamnya tidak diketahui → dibuang (kembali ke `pada`). → { id: ms }.
 */
export function hbLihatDenyut(L, sesi, daftar, kiniS) {
  (daftar || []).forEach((p) => {
    if (!p || p.id === undefined) return; const id = String(p.id), pada = String(p.pada || ''); const lama = L[id];
    if (sesi[id] !== undefined && sesi[id] !== pada && hbAngka(kiniS) !== null) L[id] = { pada, s: kiniS };
    else if (lama && lama.pada !== pada) delete L[id];
    sesi[id] = pada;
  });
  const out = {};
  Object.keys(L).forEach((id) => { const x = L[id]; if (!x || !(hbAngka(kiniS) === null || kiniS - x.s <= (HB_KASIR_HARI + 1) * hbHari)) { delete L[id]; return; } out[id] = x.s; });
  return out;
}
/**
 * daftar = denyut semua perangkat. kiniMs = jam server (atau jam perangkat bila belum tahu). lihat = hbLihatDenyut. → { penuh: { koleksi: sebab }, peristiwa: [{ kunci, T, sebab }] }.
 * Kasir darurat < HB_VERSI_KASIR_CAP ≤ 14 hari → penjualan penuh. kasir.html (pensiun) ≤ 14 hari → tiga koleksi REST penuh. Tab /baru/ versi lama atau sistem
 * lama ≤ 15 menit → SEMUA penuh; lebih lama = peristiwa TAHAN LAMA (perangkat yang belum baca penuh sesudahnya wajib baca penuh sekali, lalu lepas).
 */
export function hbGerbangPenulis(daftar, kiniMs, koleksi, lihat) {
  const penuh = {}, peristiwa = [];
  const tandai = (ks, sebab) => ks.forEach((k) => { if (!penuh[k]) penuh[k] = sebab; });
  (daftar || []).forEach((p) => {
    if (!p) return; const t = hbJamDenyut(p, lihat); if (!isFinite(t)) return; const umur = kiniMs - t; if (umur > HB_KASIR_HARI * hbHari) return;
    const app = String(p.aplikasi || ''); const nama = String(p.nama || p.id || 'perangkat tanpa nama');
    if (app === 'darurat') { if (kpNomorVersiKasir(p.versi) < kpNomorVersiKasir(HB_VERSI_KASIR_CAP)) tandai(['penjualan'], 'HP kasir ' + nama + ' masih ' + (p.versi || 'versi lama') + ' (nota tanpa cap jam server)'); return; }
    if (app === 'kasir') { tandai(HB_KOLEKSI_REST, 'kasir.html di ' + nama + ' masih berdenyut'); return; }
    if (app === 'baru' && /^baru-c\d+$/.test(String(p.versi || ''))) return;
    const sebab = (app === 'baru' ? 'tab /baru/ versi lama' : 'sistem lama') + ' di ' + nama;
    if (umur <= HB_BARU_MENIT * hbMenit) { tandai(koleksi || [], sebab + ' baru saja menulis'); return; }
    peristiwa.push({ kunci: String(p.id) + '|' + String(p.pada), T: t, sebab: sebab + ' menulis tanpa cap' });
  });
  return { penuh, peristiwa };
}
/** Peristiwa tahan lama yang mewajibkan koleksi ini baca penuh: belum dibereskan di perangkat ini DAN baca penuh terakhirnya lebih tua dari peristiwa + 15 menit. */
export function hbTotalDariPeristiwa(rk, peristiwa) {
  const r = rk || {}; const beres = r.gerbangBeres || {};
  const p = (peristiwa || []).find((x) => !beres[x.kunci] && !(hbAngka(r.Wt) >= x.T + HB_BARU_MENIT * hbMenit));
  return p ? p.sebab : '';
}

// ---------- tutup buku ----------
export const hbBkAktif = (acara) => (acara || []).some((a) => a && HB_BK_AKTIF[a.status]);
export function hbSidikBk(acara) { return (acara || []).filter((a) => a && a.tahun !== undefined).map((a) => String(a.tahun) + ':' + String(a.status || '') + ':' + String((a.paraf || {}).pada || '')).sort().join(','); }

// ---------- rencana per koleksi ----------
/**
 * c = { rk, dipercaya, sebabDasar, gerbang (hbGerbangPenulis), bkAktif, bkBeda, gen, kiniS, harian, minta, jalurPenuh } → { mode: 'delta'|'total'|'penuh', sebab, otomatis }.
 * 'penuh' = F menempel (tutup buku berjalan, penulis tanpa cap aktif, perangkat tanpa simpanan); 'total' = baca penuh sekali lalu delta.
 */
export function hbRencana(k, c) {
  const x = c || {}; const rk = x.rk || {};
  if (x.jalurPenuh) return { mode: 'penuh', sebab: x.jalurPenuh };
  if (x.bkAktif) return { mode: 'penuh', sebab: 'tutup buku sedang berjalan' };
  const g = x.gerbang && x.gerbang.penuh ? x.gerbang.penuh[k] : ''; if (g) return { mode: 'penuh', sebab: g };
  if (x.minta && x.minta[k]) return { mode: 'total', sebab: x.minta[k].sebab, otomatis: !x.minta[k].manual };
  let s = '';
  if (!x.dipercaya) s = x.sebabDasar || 'simpanan perangkat belum dipercaya';
  else if ((rk.gen || '') !== (x.gen || '')) s = 'diminta baca penuh (semua perangkat)';
  else if (x.bkBeda) s = 'tutup buku berubah sejak baca penuh terakhir';
  else if (hbAngka(x.kiniS) !== null && hbAngka(rk.totalPada) !== null && x.kiniS - rk.totalPada > HB_TOTAL_HARI * hbHari) s = 'baca penuh terakhir lebih dari 14 hari lalu';
  else if (x.gerbang && hbTotalDariPeristiwa(rk, x.gerbang.peristiwa)) s = hbTotalDariPeristiwa(rk, x.gerbang.peristiwa);
  else if (x.harian) s = 'baca penuh harian toko';
  return s ? { mode: 'total', sebab: s, otomatis: true } : { mode: 'delta', sebab: '' };
}

// ---------- batu nisan ----------
/**
 * Batu nisan t menyembunyikan versi dokumen d ({ cap, tunda }) HANYA bila versi itu lebih tua dari nisannya: tidak tertunda, cap tidak lebih baru dari nisan,
 * dan tidak terbukti LAHIR ULANG (lahirT = nisan yang berlaku saat baca penuh SERVER perangkat ini melihat catatan itu masih ada — catatan tanpa cap yang
 * dibuat lagi sesudah dihapus: HP kasir lama kirim ulang, tab lama, Console). Tanpa lahirT catatan seperti itu tersembunyi selamanya (tinjauan 7 Okt).
 */
export function hbTersembunyiNisan(d, t, lahirT) {
  if (t === undefined || !d || d.tunda) return false;
  if (typeof d.cap === 'number' && typeof t === 'number' && d.cap > t) return false;
  if (typeof lahirT === 'number' && typeof t === 'number' && lahirT >= t) return false;
  return true;
}
/** dok = [{ id, cap, tunda, data }] (V mentah), nisan = { id: capMs }, lahir = { id: nisan saat terlihat lahir ulang }. → { tampil, tersembunyi }. */
export function hbSaringNisan(dok, nisan, lahir) {
  if (!nisan) return { tampil: dok, tersembunyi: 0 };
  const tampil = []; let n = 0; const L = lahir || {};
  dok.forEach((d) => { if (hbTersembunyiNisan(d, nisan[d.id], L[d.id])) n += 1; else tampil.push(d); });
  return { tampil, tersembunyi: n };
}
/** Snapshot SERVER baca penuh Z = { id: { cap, tunda } }: catatan yang ADA di server tapi akan disembunyikan nisannya = lahir ulang. → [id]. */
export function hbLahirUlang(Z, nisan, lahir) {
  if (!nisan) return []; const L = lahir || {};
  return Object.keys(Z || {}).filter((id) => { const b = Z[id]; return !!b && !b.tunda && hbTersembunyiNisan(b, nisan[id], L[id]); });
}
/**
 * Batas pendengar nisan Bn = min(jam baca penuh terakhir tiap koleksi (totalPada), jam server) − 60 menit. Catatan yang dihapus sebelum baca penuh terakhir
 * sudah dibuang dari simpanan oleh baca penuh itu; yang dihapus sesudahnya masih mentah di simpanan dan hanya disembunyikan nisan — nisan itu wajib ikut
 * jendela N. BUKAN Wt (cap tertinggi di data): koleksi yang jarang ditulis menahan Wt di tulisan terakhirnya berbulan-bulan, dan tiap buka semua nisan
 * sejak itu dibaca ulang (tinjauan 7 Okt). totalPada paling tua ±14 hari (baca penuh berkala). Koleksi tanpa totalPada sedang dibaca penuh (yang dihapus
 * sebelum selesai ikut dibuang). TIDAK PERNAH 0. null = tunggu.
 */
export function hbBatasNisan(daftarTotal, kiniS) {
  const c = (daftarTotal || []).filter((x) => hbAngka(x) > 0).map((x) => x - HB_MARGIN_MS); if (hbAngka(kiniS) > 0) c.push(kiniS - HB_MARGIN_MS);
  return c.length ? Math.min.apply(null, c) : null;
}

// ---------- hitungan server ----------
/** h = { server, mentah (dokumen V), tersembunyi (nisan), tunda, hapusTunda, galat } → 'cocok' | 'kurang' (perangkat kurang) | 'lebih' | 'belum'. */
export function hbNilaiHitung(h) {
  if (!h || h.galat || typeof h.server !== 'number') return 'belum';
  if ((h.tunda || 0) > 0 || (h.hapusTunda || 0) > 0) return 'belum';
  const lokal = (h.mentah || 0) - (h.tersembunyi || 0);
  return h.server === lokal ? 'cocok' : h.server > lokal ? 'kurang' : 'lebih';
}

// ---------- KELENGKAPAN per koleksi — SATU sumber (7 Okt, Paket C × hemat baca) ----------
// Dipakai: terperiksa (gerbang katalog kasir, uang-kritis, pil kepala, tanda "salinan perangkat" toko.js) DAN keputusan final yang membaca seluruh buku: kartu
// "Pemeriksaan sesudah tutup buku" (pstKurang), daftar periksa kunci bulan, Laporan › Pajak, perkiraan kuota & Lanjutkan/Batalkan tutup buku, gerbang g7.
// Kalimatnya kalimat toko: dibaca "data <apa> <sebab>". "Hari ini" = hari KUOTA (reset 14.00/15.00 WIB), bukan hari toko — kalimatnya menyebut jam resetnya.
// Tempat panel Hemat baca di layar = nama laci & baris Menu (menu-logika.js laci "Toko ini" · menu.js JUDUL_SISTEM & TAB_SISTEM). SATU konstanta: sistem-logika.js
// ssHemat membuang petunjuk ini dari sebab yang digambar DI panel itu sendiri (audit P2 · K5: dulu "Menu › Sistem › Perangkat", jalur yang tidak ada di layar).
export const HB_TEMPAT = 'Menu › Toko ini › Perangkat & antrean › Hemat baca';
// Tombol "<nama> sudah tidak dipakai" HANYA ada di butir perangkatDenyut daftar periksa kunci bulan (kunci-periode-logika.js). Butirnya selalu ada di daftar
// periksa itu; TOMBOLNYA baru muncul sesudah perangkat itu diam > 24 jam, dan hanya bila laporan terakhirnya antrean 0 & ditolak 0 — selain itu jalannya butir
// "Perangkat hilang atau rusak" di catatan "Prosedur pulih darurat" (= KP_BUTIR_HILANG). Daftar periksanya tampil selama ada bulan yang bisa dikunci (kpCalon).
// Teks butir & nama butir prosedur dicocokkan dengan kunci-periode-logika.js oleh alat-uji/uji_kunci_periode.py (audit P2 · sanggahan #121).
export const HB_TANDAI_TIDAK_DIPAKAI = 'ketuk "<nama> sudah tidak dipakai" di Uang › Tutup buku › kartu Kunci bulan › butir "Semua perangkat berdenyut dalam 24 jam terakhir" (tombol itu muncul sesudah perangkatnya diam lebih dari 24 jam DAN laporan terakhirnya antrean 0 & ditolak 0; selain itu: catatan "Prosedur pulih darurat", butir "Perangkat hilang atau rusak")';
const HB_KE_MENU = 'ketuk "baca penuh sekarang" (' + HB_TEMPAT + ')';
/** Sebab "harian": belum ada baca penuh sejak reset kuota yang memulai hari kuota `hari` ('' = jam resetnya tidak disebut). */
export function hbSebabHarian(hari) { const j = hbJamResetHariWib(hari); return 'belum dibaca penuh sejak kuota baca direset' + (j ? ' pukul ' + j + ' WIB' : '') + ' — ' + HB_KE_MENU; }
/** Baca penuh ditolak server karena kuota baca habis (429 resource-exhausted): mengetuk baru menolong sesudah reset BERIKUTNYA. */
export function hbSebabHabis(hari) { const j = hbJamResetHariWib(hbHariBerikut(hari)); return 'belum bisa dibaca penuh karena kuota baca hari ini habis — ketuk "baca penuh sekarang" sesudah pukul ' + (j || '14.00/15.00') + ' WIB (' + HB_TEMPAT + ')'; }
export const HB_SEBAB_TOKO_TUNDA = 'punya ubahan yang ditemukan baca penuh harian toko tapi belum sampai ke perangkat ini — ' + HB_KE_MENU;
export const HB_SEBAB_TAB_BERHENTI = 'tidak diperbarui lagi di tab ini — muat ulang aplikasi';
/**
 * Koleksi hemat di perangkat ini BELUM LENGKAP? c = { koleksi, vMati, berhenti (tab kalah kunci tab — klien Firestore dihentikan), vAda, nTerkini, online, mode,
 * fTerkini, fSelesai, fMode, fJalan (baca penuh sekali sedang berjalan), fGalat, wajibTotal, sTerkini, cocok (hitungan server cocok sesi ini), totalPada (baca
 * penuh terakhir perangkat ini — jam server), hari (hari kuota sekarang menurut jam server; '' = belum diketahui), klaim (aturanToko/hematHarian) }.
 * → null (lengkap) | { jenis, sebab }.
 *   jenis 'periksa' = BELUM TERPERIKSA dengan server (arti `terperiksa` sejak 7 Okt, + tab yang berhenti — sanggahan 7 Okt): tab berhenti menerima data · simpanan
 *     perangkat belum terbaca · batu nisan belum dicocokkan · dengar penuh belum terkini · baca penuh wajib tapi ditunda rem kuota / gagal · ubahan bercap belum
 *     dicocokkan · baca penuh masih berjalan · hitungan server belum cocok sesi ini.
 *   jenis 'harian' = terperiksa (hitungan cocok), tapi BELUM ADA BACA PENUH pada hari kuota ini — oleh perangkat ini (totalPada) maupun baca penuh harian TOKO
 *     yang selesai (klaim) TANPA temuan tertunda untuk koleksi ini (`temuanTunda` — ubahan tanpa cap yang ditemukan tapi gagal disentuh / di bulan terkunci:
 *     perangkat lain tidak menerimanya lewat delta). Ubahan tanpa cap jam server (Console, penulis lama tanpa denyut) sejak baca penuh terakhir bisa belum
 *     terlihat: hitungan yang cocok tidak membuktikan isinya sama. Dengar penuh (F menempel & terkini) = lengkap. Jam server belum diketahui = belum bisa dipastikan.
 */
export function hbBelumLengkap(c) {
  const x = c || {}; const mati = !!(x.vMati || x.berhenti);
  // tanpa internet = sebab yang terbaca owner untuk keadaan belum terperiksa apa pun (kecuali tab yang berhenti — muat ulang yang menolong)
  const P = (sebab) => ({ jenis: 'periksa', sebab: x.online === false && !mati ? 'belum dicocokkan dengan server — perangkat ini tanpa internet' : sebab });
  // 429 (kuota baca habis): mengetuk "baca penuh sekarang" tidak menolong sampai reset berikutnya — kalimatnya menyebut jamnya
  const habis = /resource-exhausted/.test(String(x.fGalat || '') + ' ' + String(x.wajibTotal || ''));
  const gagal = habis ? hbSebabHabis(x.hari) : 'gagal dibaca penuh — dicoba lagi sebentar, atau ' + HB_KE_MENU;
  if (mati) return P(HB_SEBAB_TAB_BERHENTI);
  if (!x.vAda) return P('belum terbaca dari simpanan perangkat — tunggu sebentar');
  if (!x.nTerkini) return P('belum dicocokkan dengan catatan yang dihapus di server — tunggu sebentar');
  if (x.mode === 'penuh') return x.fTerkini && (x.fSelesai || x.fMode === 'penuh') ? null : P(x.fGalat ? gagal : 'sedang dibaca penuh — tunggu sampai selesai');
  if (x.wajibTotal) return P(/^baca penuh gagal/.test(String(x.wajibTotal)) ? gagal : 'perlu dibaca penuh, tapi ditunda supaya kuota baca hari ini tidak habis — ' + HB_KE_MENU);
  if (!x.sTerkini) return P('belum dicocokkan dengan ubahan terbaru di server — tunggu sebentar');
  if (x.fJalan) return P('sedang dibaca penuh — tunggu sampai selesai');
  if (!x.fSelesai && !x.cocok) return P(x.fGalat ? gagal : 'belum dicocokkan dengan server — tunggu sebentar');
  if (!x.hari) return { jenis: 'harian', sebab: 'belum bisa dipastikan sudah dibaca penuh sejak kuota baca terakhir direset (jam server belum diterima) — tunggu sebentar' };
  if (hbAngka(x.totalPada) > 0 && hbHariKuota(x.totalPada) === x.hari) return null;
  const k = x.klaim || {}; const tokoHariIni = k.hari === x.hari && !!k.selesai;
  const tunda = tokoHariIni && k.temuanTunda && typeof k.temuanTunda === 'object' ? Number(k.temuanTunda[x.koleksi]) || 0 : 0;
  if (tokoHariIni && !(tunda > 0)) return null;
  if (habis) return { jenis: 'harian', sebab: hbSebabHabis(x.hari) };
  return { jenis: 'harian', sebab: tunda > 0 ? HB_SEBAB_TOKO_TUNDA : hbSebabHarian(x.hari) };
}
/**
 * Dari peta kelengkapan { koleksi: { jenis, sebab } } (hbSesi.belumLengkap; kosong = semua lengkap) untuk koleksi `perlu` (tanpa / '*' = semua): null atau
 * { koleksi: [semua yang belum lengkap], jenis, sebab, utama: [koleksi yang sebabnya PERSIS sebab itu], lain: [sisanya], sebabLain }. Sebab = koleksi pertama
 * yang belum terperiksa (lebih berat), selain itu koleksi pertama. Sebab SATU koleksi tidak dipinjamkan ke koleksi lain (sanggahan 7 Okt): kalimat menyebut
 * `utama` dengan sebabnya, `lain` dihitung dengan sebabnya sendiri (hbEkorLain).
 */
export function hbBelumUntuk(peta, perlu) {
  const P = peta || {}; const semua = !perlu || perlu.indexOf('*') >= 0;
  const ks = Object.keys(P).filter((k) => P[k] && (semua || perlu.indexOf(k) >= 0)); if (!ks.length) return null;
  const berat = ks.find((k) => P[k].jenis === 'periksa'); const teks = (k) => String(P[k].sebab || hbSebabHarian(''));
  const sebab = teks(berat || ks[0]); const utama = ks.filter((k) => teks(k) === sebab); const lain = ks.filter((k) => teks(k) !== sebab);
  const sl = lain.map(teks); const sebabLain = sl.length && sl.every((s) => s === sl[0]) ? sl[0] : '';
  return { koleksi: ks, jenis: berat ? 'periksa' : 'harian', sebab, utama, lain, sebabLain };
}
/** Ekor kalimat untuk jenis catatan yang sebabnya LAIN: '' atau "; n jenis catatan lainnya <sebabnya>" (sebab campur → tunjuk panel Hemat baca). */
export function hbEkorLain(B) {
  if (!B || !B.lain || !B.lain.length) return '';
  return '; ' + B.lain.length + ' jenis catatan lainnya ' + (B.sebabLain || 'juga belum lengkap — lihat ' + HB_TEMPAT);
}
/** Jumlah jenis catatan disisipkan SEBELUM petunjuknya ("<keadaan> (n jenis catatan) — <petunjuk>") — tidak menempel di belakang kurung menu. */
const hbSisipJumlah = (sebab, n) => { const i = sebab.indexOf(' — '); const j = ' (' + n + ' jenis catatan)'; return i < 0 ? sebab + j : sebab.slice(0, i) + j + sebab.slice(i); };
/**
 * Kalimat layar untuk keputusan yang membaca seluruh buku (kunci bulan, pajak, perkiraan kuota, dokumen Laporan): '' = lengkap.
 * "data perangkat ini <keadaan> (n jenis catatan) — <petunjuk>; m jenis catatan lainnya <sebabnya>".
 */
export function hbKalimatBelum(peta, perlu) {
  const B = hbBelumUntuk(peta, perlu); if (!B) return '';
  return 'data perangkat ini ' + (B.koleksi.length > 1 ? hbSisipJumlah(B.sebab, B.utama.length) : B.sebab) + hbEkorLain(B);
}

// ---------- pendeteksi tanpa cap (perangkat yang baca penuh harian) ----------
/**
 * awal = { id: { cap, sidik } } (snapshot SIMPANAN pertama F), akhir = { id: { cap, sidik, tunda } } (snapshot server F). → { ubah, baru, hilang } (id).
 * ubah = isi berubah tanpa cap maju; baru = lahir tanpa cap (hanya bila dasar dipercaya — simpanan kosong tidak membanjiri); hilang = dihapus tanpa nisan, bukan sesi ini.
 */
export function hbPeriksaTanpaCap(awal, akhir, nisan, dipercaya, hapusSesi) {
  const A = awal || {}, Z = akhir || {}; const ubah = [], baru = [], hilang = [];
  Object.keys(Z).forEach((id) => { const b = Z[id]; if (!b || b.tunda) return; const a = A[id];
    if (a) { if (a.sidik === b.sidik) return; if (typeof b.cap === 'number' && !(typeof a.cap === 'number' && b.cap <= a.cap)) return; ubah.push(id); return; }
    if (typeof b.cap === 'number' || !dipercaya) return; baru.push(id); });
  Object.keys(A).forEach((id) => { if (Z[id] || (nisan && nisan[id] !== undefined) || (hapusSesi && hapusSesi[id]) || (A[id] && A[id].tunda)) return; hilang.push(id); });
  return { ubah, baru, hilang };
}
/** → { sentuh, nisan, gen }. Tutup buku berjalan = tidak menyentuh apa pun. Lebih dari HB_SENTUH_MAKS = gen baru koleksi itu (semua perangkat baca penuh). */
export function hbRencanaSentuh(t, bkAktif) {
  const x = t || { ubah: [], baru: [], hilang: [] }; const n = x.ubah.length + x.baru.length + x.hilang.length;
  if (bkAktif || !n) return { sentuh: [], nisan: [], gen: false };
  if (n > HB_SENTUH_MAKS) return { sentuh: [], nisan: [], gen: true };
  return { sentuh: x.ubah.concat(x.baru), nisan: x.hilang.slice(), gen: false };
}

// ---------- baca penuh harian per toko ----------
/** klaim = aturanToko/hematHarian. → { klaim: bool, sebab }. Hari kuota dari jam SERVER. Klaim milik perangkat ini yang belum selesai = lanjutkan. */
export function hbKlaimHarian(klaim, kiniS, idIni) {
  if (!(hbAngka(kiniS) > 0)) return { klaim: false, sebab: 'jam server belum diketahui' };
  const hari = hbHariKuota(kiniS); const k = klaim || {}; const siapa = k.perangkat === idIni ? 'perangkat ini' : String(k.nama || k.perangkat || 'perangkat lain');
  if (k.hari !== hari) return { klaim: true, hari, sebab: 'belum ada baca penuh hari kuota ' + hari };
  if (k.selesai) return { klaim: false, hari, sebab: 'sudah dibaca penuh hari ini oleh ' + siapa };
  if (k.perangkat === idIni) return { klaim: true, hari, sebab: 'baca penuh harian perangkat ini belum selesai' };
  if (kiniS - (Number(k.mulai) || 0) > HB_KLAIM_BASI_MS) return { klaim: true, hari, sebab: 'baca penuh ' + siapa + ' belum selesai sesudah 30 menit' };
  return { klaim: false, hari, sebab: siapa + ' sedang membaca penuh' };
}
/** Gen "baca penuh semua perangkat" untuk koleksi k dari dokumen klaim: '<*>|<k>'. */
export function hbGen(klaim, k) { const g = (klaim && klaim.gen) || {}; const a = g['*'] || '', b = g[k] || ''; return a || b ? a + '|' + b : ''; }

// ---------- rem kuota ----------
/** c = { manual, otomatisK (baca penuh otomatis selesai hari ini), mulaiK (mulai tanpa selesai), perkiraan, ukuran }. Tombol manual menembus rem. */
export function hbRem(c) {
  const x = c || {}; if (x.manual) return { boleh: true, sebab: '' };
  if ((x.otomatisK || 0) >= 2) return { boleh: false, sebab: 'sudah 2 kali baca penuh otomatis hari ini — menunggu kuota besok' };
  if ((x.mulaiK || 0) >= 3) return { boleh: false, sebab: '3 kali mulai baca penuh tanpa selesai — berhenti sampai besok' };
  if ((x.perkiraan || 0) + (x.ukuran || 0) > HB_KUOTA * HB_REM) return { boleh: false, sebab: 'perkiraan baca hari ini melewati 80% kuota — menunggu kuota besok' };
  return { boleh: true, sebab: '' };
}
/** Perkiraan baca toko hari kuota ini: denyut owner (hemat.baca) perangkat lain + perangkat ini + ±200 HP kasir. */
export function hbPerkiraanToko(daftar, hari, idIni, bacaIni) {
  let n = (bacaIni || 0) + 200;
  (daftar || []).forEach((p) => { const h = p && p.hemat; if (!h || h.hari !== hari || String(p.id) === String(idIni)) return; n += Number(h.baca) || 0; });
  return n;
}

// ---------- pendengar simpanan hidup (temuan SDK: tab yang turun dari primer kehilangan pendengar simpanannya tanpa kabar) ----------
export function hbPenjagaHidup() {
  const harap = {};
  const terpenuhi = (x, v, kec) => (x.hilang ? !v || kec : !!v && (v.tunda || kec || (typeof x.cap === 'number' ? typeof v.cap === 'number' && v.cap >= x.cap : v.sidik() === x.sidik)));
  return {
    /** S/F server membawa id dengan cap (atau sidik) ini — V wajib menunjukkannya dalam HB_HIDUP_MS. x = { cap } | { sidik } | { hilang: true } */
    catat(k, id, x, kini) { (harap[k] = harap[k] || {})[id] = Object.assign({}, x, { batas: kini + HB_HIDUP_MS }); },
    /** v(id) → { cap, tunda, sidik() } | null; kec(id) → true bila disembunyikan nisan / dihapus sesi ini. */
    cocokkan(k, v, kec) { const h = harap[k]; if (!h) return; Object.keys(h).forEach((id) => { if (terpenuhi(h[id], v(id), kec(id))) delete h[id]; }); },
    mati(kini) { return Object.keys(harap).filter((k) => Object.keys(harap[k]).some((id) => harap[k][id].batas < kini)); },
    ada() { return Object.keys(harap).some((k) => Object.keys(harap[k]).length > 0); },
    kosongkan(k) { if (k) delete harap[k]; else Object.keys(harap).forEach((x) => delete harap[x]); },
  };
}

// ---------- katalog kasir: penjaga ayunan antarperangkat & plafon terbit ----------
export function hbAyunanBaru() { return { terbit: [], berhenti: '' }; }
export function hbCatatTerbitKatalog(A, kanon, kini) { A.terbit = A.terbit.filter((x) => kini - x.pada <= hbJam).concat([{ kanon, pada: kini }]); return A; }
/** Dokumen katalog di server berganti ke kanonS. Bukan gema terbit sendiri, ≤ 15 menit sesudah perangkat ini terbit, dan beda dengan hitungan perangkat ini = AYUNAN. */
export function hbNilaiKatalogServer(A, kanonS, kanonIni, kini) {
  if (!kanonS || A.berhenti || A.terbit.some((x) => x.kanon === kanonS)) return A;
  const akhir = A.terbit.length ? A.terbit[A.terbit.length - 1] : null;
  if (akhir && kini - akhir.pada <= 15 * hbMenit && kanonS !== kanonIni) A.berhenti = 'dua perangkat owner berbeda hitungan katalog kasir — perangkat ini berhenti menerbitkan dan membaca penuh';
  return A;
}
export function hbBolehTerbitKatalog(A, kini) {
  if (A.berhenti) return { boleh: false, sebab: A.berhenti };
  if (A.terbit.filter((x) => kini - x.pada <= hbJam).length >= 6) return { boleh: false, sebab: 'katalog kasir sudah 6 kali terbit dalam sejam dari perangkat ini — ditahan' };
  return { boleh: true, sebab: '' };
}

// ---------- satu klien Firestore per peramban (kunci tab) ----------
/** penyimpan = { baca, tulis, hapus }, jam() = ms perangkat, sesi = id sesi tab ini. */
export function hbKunciTab(penyimpan, jam, sesi) {
  const baca = () => { try { const v = JSON.parse(penyimpan.baca(HB_KUNCI_TAB) || 'null'); return v && v.sesi ? v : null; } catch (e) { return null; } };
  const tulis = () => { try { penyimpan.tulis(HB_KUNCI_TAB, JSON.stringify({ sesi, detak: jam() })); return true; } catch (e) { return false; } };
  return {
    /** 'bebas' | 'milik' | 'lain' (tab lain berdetak < 12 detik) | 'basi' (pemegang lama diam) */
    keadaan() { const v = baca(); if (!v) return 'bebas'; if (v.sesi === sesi) return 'milik'; return jam() - (Number(v.detak) || 0) < HB_TAB_SEGAR_MS ? 'lain' : 'basi'; },
    ambil: tulis,
    detak() { const v = baca(); return !!v && v.sesi === sesi && tulis(); },
    milik() { const v = baca(); return !!v && v.sesi === sesi; },
    lepas() { const v = baca(); if (v && v.sesi === sesi) { try { penyimpan.hapus(HB_KUNCI_TAB); } catch (e) { /* abaikan */ } } },
  };
}

// ---------- daftar siap-nyala (owner menyalakan sesudah hijau 3 hari berturut-turut) ----------
/** c = { perangkat (denyut), kiniMs, lihat (hbLihatDenyut, saat nyala), nisanSah, statis (catatan tanpa cap 7 hari di perangkat ini), ownerEmail }. → [{ id, teks, ok, ket }] */
export function hbSiapNyala(c) {
  const x = c || {}; const kini = x.kiniMs; const umur = (p) => kini - hbJamDenyut(p, x.lihat);
  const P = (x.perangkat || []).filter((p) => p && isFinite(Date.parse(p.pada || '')));
  const lama = P.filter((p) => umur(p) <= 7 * hbHari && (String(p.aplikasi || '') !== 'baru' ? ['darurat', 'kasir'].indexOf(String(p.aplikasi || '')) < 0 : !/^baru-c\d+$/.test(String(p.versi || ''))));
  const kasir = P.filter((p) => umur(p) <= HB_KASIR_HARI * hbHari && (String(p.aplikasi) === 'kasir' || (String(p.aplikasi) === 'darurat' && kpNomorVersiKasir(p.versi) < kpNomorVersiKasir(HB_VERSI_KASIR_CAP))));
  const owner = P.filter((p) => umur(p) <= 7 * hbHari && String(p.aplikasi) === 'baru' && String(p.akun || '').toLowerCase() === String(x.ownerEmail || '').toLowerCase());
  const ownerBelum = owner.filter((p) => !/^baru-c\d+$/.test(String(p.versi || '')) || (Number(p.antrean) || 0) > 0);
  const nm = (L) => L.map((p) => p.nama || p.id).slice(0, 4).join(', ') + (L.length > 4 ? ' …' : '');
  return [
    { id: 'aturan', teks: 'Aturan server v7 terpasang (batu nisan terbaca)', ok: !!x.nisanSah, ket: x.nisanSah ? 'terbukti di perangkat ini' : 'owner menerbitkan rules v7 lewat Console dulu' },
    { id: 'lama', teks: 'Tidak ada tab /baru/ versi lama atau sistem lama berdenyut 7 hari terakhir', ok: !lama.length, ket: lama.length ? nm(lama) + ' — muat ulang tab itu di perangkatnya. Perangkat yang sudah tidak dipakai: ' + HB_TANDAI_TIDAK_DIPAKAI : 'bersih' },
    { id: 'kasir', teks: 'Semua HP kasir sudah ' + HB_VERSI_KASIR_CAP + ' (nota bercap) dalam 14 hari terakhir', ok: !kasir.length, ket: kasir.length ? nm(kasir) + ' — buka kasir darurat sekali sampai versi baru terpasang' : 'bersih' },
    { id: 'owner', teks: 'Tiap perangkat owner sudah ' + HB_VERSI + ' dengan antrean kosong', ok: owner.length > 0 && !ownerBelum.length, ket: !owner.length ? 'belum ada denyut owner 7 hari terakhir' : ownerBelum.length ? nm(ownerBelum) + ' belum' : owner.length + ' perangkat siap' },
    { id: 'statis', teks: 'Tidak ada catatan baru tanpa cap jam server (7 hari terakhir, perangkat ini)', ok: !(x.statis > 0), ket: x.statis > 0 ? x.statis + ' catatan — ada penulis lama yang masih jalan' : 'bersih' },
  ];
}

// =====================================================================================================================================================
// SESI HEMAT — satu per pemasangan pendengar owner (saklar nyala). o = {
//   koleksi: [nama koleksi hemat], R: rekam (hbBacaRekam), simpan(), jam() → ms perangkat, jadwal(fn, ms) → h, batal(h), idPerangkat, namaPerangkat, online,
//   milikTab() → bool, hapusTunda(k) → n,
//   sdk: { cache(k, cb, galat), delta(k, B, cb, galat), penuh(k, cb, galat), nisan(B, cb, galat) → lepas;  hitung(k) → Promise<n>;  klaim(dok) → Promise;
//          sentuh(k, ids, lihat(id) → isi mentah | null), tulisNisan(k, ids) → Promise<{ n, tunda: [id yang belum terkirim — diulang] }> }
//          — snapshot cb: { dariCache, dok: [{ id, tunda, capMentah, isi() }] }
//   keluar: { pasok(k, data[]), tunda(k, [{ id, data }]), siap(k), periksa(k, terperiksa), berubah(), mati(k) } }
// =====================================================================================================================================================
export function hbSesi(o) {
  const R = o.R; const K = {}; const jam = o.jam;
  const G = { skew: null, gemaS: null, online: o.online !== false, tersembunyiSejak: 0, tetap: { perangkat: [], acara: [], klaim: null, ada: false }, gerbang: { penuh: {}, peristiwa: [] },
    bkAktif: false, sidikBk: '', nisan: {}, nLepas: null, nB: null, nTerkini: false, nGalat: '', hapusSesi: {}, minta: {}, temuan: {}, lihatSesi: {}, ulangJalan: {}, temuanGagal: 0, temuanLewat: 0, klaimTunda: {},
    hidup: hbPenjagaHidup(), hidupH: null, klaimJalan: false, klaimSaya: false, klaimMulai: 0, klaimKabar: '', genMinta: {}, jalurPenuh: '', berhenti: false, kabar: '' };
  const kiniS = () => (G.skew === null ? null : jam() + G.skew);
  // jam "baca penuh terakhir" (totalPada → batas nisan Bn, umur 14 hari): kiniS, tapi paling jauh 10 menit sesudah jam server gema denyut TERAKHIR — jam
  // perangkat yang melompat maju sesudah gema tidak menaruh totalPada (lalu Bn) di masa depan; tab yang lama tanpa gema mencatat jam lebih tua (aman)
  const kiniSTercatat = () => { const s = kiniS(); return s === null || G.gemaS === null ? s : Math.min(s, G.gemaS + HB_JEPIT_MS); };
  const hariKini = () => (kiniS() === null ? '' : hbHariKuota(kiniS()));
  const rk = (k) => (R.k[k] = R.k[k] || {});
  const hariR = () => { const h = hariKini(); if (h && R.hari.H !== h) R.hari = { H: h, otomatis: {}, mulai: {}, baca: 0 }; return R.hari; };
  const simpan = () => { try { o.simpan(); } catch (e) { /* rekam gagal disimpan = baca penuh lagi nanti (biaya), bukan angka salah */ } };
  const tambahBaca = (n) => { hariR().baca = (R.hari.baca || 0) + Math.max(0, n || 0); };
  const tundaN = (k) => { const v = K[k].v; return Object.keys(v).filter((id) => v[id].tunda).length; };
  const lahirK = (k) => rk(k).lahir || {};
  const kecuali = (k) => (id) => { const v = K[k].v[id]; return !!((G.hapusSesi[k] || {})[id]) || hbTersembunyiNisan(v, (G.nisan[k] || {})[id], lahirK(k)[id]); };
  const vLihat = (k) => (id) => { const v = K[k].v[id]; return v ? { cap: v.cap, tunda: v.tunda, sidik: () => hbSidik(v.data) } : null; };
  // isi MENTAH koleksi k di simpanan perangkat (V, SEBELUM saringan nisan) — penyentuh memeriksa kunci bulan dari sini, bukan dari memori yang sudah disaring
  const lihatV = (k) => (id) => { const v = K[k] && K[k].v[id]; return v ? v.data : null; };
  const lihatDenyut = () => hbLihatDenyut(R.lihat || (R.lihat = {}), G.lihatSesi, G.tetap.perangkat, kiniS());

  // ---- V: simpanan perangkat → memori (disaring nisan) ----
  function pasokK(k) {
    const st = K[k]; const daftar = Object.keys(st.v).map((id) => Object.assign({ id }, st.v[id]));
    const S = hbSaringNisan(daftar, G.nisan[k], lahirK(k)); st.tersembunyi = S.tersembunyi;
    o.keluar.pasok(k, S.tampil.map((d) => d.data)); o.keluar.tunda(k, daftar.filter((d) => d.tunda).map((d) => ({ id: d.id, data: d.data })));
  }
  function vMasuk(k, snap) {
    const st = K[k]; if (G.berhenti) return; const v = {};
    (snap.dok || []).forEach((d) => { const x = d.isi(); const cap = hbKupas(x); v[d.id] = { data: x, cap, tunda: !!d.tunda }; });
    st.v = v; st.vGalat = '';
    pasokK(k);
    G.hidup.cocokkan(k, vLihat(k), kecuali(k));
    if (!st.vAda) { st.vAda = true; nilaiDasar(k); putuskanSemua(); }
    cekHitung(k); if (st.fMode === 'total' && st.fTerkini && !st.fSelesai) cekSelesaiF(k);
    nilaiPeriksa(k);
  }
  function nilaiDasar(k) {
    const st = K[k]; const c = Object.keys(st.v).length; const d = hbDasarDipercaya(rk(k), c);
    st.dipercaya = d.ya; st.sebabDasar = d.sebab;
    if (d.ya) siapK(k); else if (!G.online) { siapK(k); G.kabar = 'Tanpa internet: simpanan perangkat ini belum bisa dipercaya — angka belum bisa dihitung sampai tersambung'; }
    if (o.koleksi.every((x) => K[x].vAda)) {
      const kosong = o.koleksi.every((x) => !Object.keys(K[x].v).length) && o.koleksi.some((x) => (Number(rk(x).n) || 0) >= 1);
      R.tanpaIdb = kosong ? (Number(R.tanpaIdb) || 0) + 1 : 0; if (R.tanpaIdb >= 2) G.jalurPenuh = 'perangkat ini tidak menyimpan data (simpanan peramban hilang dua kali berturut-turut) — dengar penuh';
      simpan();
    }
  }
  function siapK(k) { const st = K[k]; if (st.siap) return; st.siap = true; o.keluar.siap(k); }

  // ---- rencana ----
  // tutup buku berubah sejak baca penuh terakhir koleksi k di perangkat ini (ritual berjalan selagi perangkat ini tertutup)
  const bkBeda = (k) => hbAngka(rk(k).totalPada) !== null && (rk(k).bk || '') !== G.sidikBk;
  function konteks(k) {
    const st = K[k]; const r = rk(k);
    return { rk: r, dipercaya: st.dipercaya, sebabDasar: st.sebabDasar, gerbang: G.gerbang, bkAktif: G.bkAktif, bkBeda: bkBeda(k),
      gen: hbGen(G.tetap.klaim, k), kiniS: kiniS(), harian: G.klaimSaya && !(st.fSelesai && st.fSelesaiPada >= G.klaimMulai), minta: G.minta, jalurPenuh: G.jalurPenuh };
  }
  function putuskanSemua() { if (G.berhenti || !G.tetap.ada || !o.koleksi.every((k) => K[k].vAda)) return; o.koleksi.forEach(putuskan); pastikanN(); }
  function putuskan(k) {
    const st = K[k]; if (G.berhenti) return;
    const p = hbRencana(k, konteks(k)); st.rencana = p;
    if (p.mode === 'penuh') { st.mode = 'penuh'; st.sebab = p.sebab; st.wajibTotal = ''; pastikanS(k); mulaiF(k, 'penuh'); }
    else if (p.mode === 'total') {
      if (st.fLepas && !st.fSelesai) { if (st.fMode === 'penuh') { st.fMode = 'total'; st.mode = 'total'; st.sebab = p.sebab; if (st.fTerkini) cekSelesaiF(k); } nilaiPeriksa(k); return; }
      // baca penuh otomatis yang baru gagal (galat server / hitungan beda) tidak diulang sebelum 10 menit — tiap ulang = seluruh koleksi dibaca lagi
      if (p.otomatis && st.fGagalPada && jam() - st.fGagalPada < 10 * hbMenit) { if (st.mode !== 'penuh') { st.mode = 'delta'; st.wajibTotal = 'baca penuh gagal (' + (st.fGalat || 'galat') + ') — dicoba lagi sebentar'; } pastikanS(k); nilaiPeriksa(k); return; }
      const H = hariR(); const rem = hbRem({ manual: !p.otomatis, otomatisK: H.otomatis[k] || 0, mulaiK: (H.mulai[k] || 0) - (H.otomatis[k] || 0),
        perkiraan: hbPerkiraanToko(G.tetap.perangkat, H.H, o.idPerangkat, H.baca), ukuran: Number(rk(k).n) || Object.keys(st.v).length });
      if (!rem.boleh) { if (st.mode === 'penuh') lepasF(k); st.mode = 'delta'; st.sebab = ''; st.wajibTotal = rem.sebab + ' (' + p.sebab + ')'; pastikanS(k); }
      else { st.mode = 'total'; st.sebab = p.sebab; st.otomatis = !!p.otomatis; st.wajibTotal = ''; if (st.fLepas && st.fMode === 'penuh') lepasF(k); pastikanS(k); mulaiF(k, 'total'); }
    } else {
      if (st.fLepas && st.fMode === 'penuh') lepasF(k);
      if (!(st.fLepas && st.fMode === 'total' && !st.fSelesai)) { st.mode = 'delta'; st.sebab = ''; }
      st.wajibTotal = ''; pastikanS(k);
    }
    nilaiPeriksa(k);
  }

  // ---- S: ubahan bercap ----
  function pastikanS(k) {
    const st = K[k]; if (st.sLepas || G.berhenti) return;
    const r = hbBatasDelta(rk(k), kiniS(), hariKini()); if (r.B === null) return;
    if (r.baru) { Object.assign(rk(k), { B: r.B, hariB: r.hariB, nB: r.nB }); simpan(); }
    st.sB = r.B; st.sTerkini = false; st.sPrev = {}; tambahBaca(1);
    st.sLepas = o.sdk.delta(k, r.B, (s) => sMasuk(k, s), (e) => sGalat(k, e));
    pastikanN();
  }
  function sMasuk(k, snap) {
    const st = K[k]; if (G.berhenti) return; st.sGalat = '';
    if (snap.dariCache) { st.sTerkini = false; nilaiPeriksa(k); return; }
    const kini = jam(); const prev = st.sPrev || {}; const kini2 = {}; let maks = null, baru = 0;
    (snap.dok || []).forEach((d) => { if (d.tunda) return; const c = hbCapMs(d.capMentah); if (typeof c !== 'number') return; kini2[d.id] = c; if (maks === null || c > maks) maks = c;
      if (prev[d.id] !== c) { baru += 1; G.hidup.catat(k, d.id, { cap: c }, kini); } });
    st.sPrev = kini2; if (maks !== null) st.wdCalon = Math.max(st.wdCalon || 0, maks); tambahBaca(baru);
    st.sTerkini = true;
    G.hidup.cocokkan(k, vLihat(k), kecuali(k)); jadwalHidup();
    cekHitung(k); nilaiPeriksa(k);
  }
  function sGalat(k, e) {
    const st = K[k]; st.sGalat = kodeGalat(e); st.sTerkini = false; st.sLepas = null; nilaiPeriksa(k);
    if ((st.sUlang || 0) < 1 && !G.berhenti) { st.sUlang = (st.sUlang || 0) + 1; o.jadwal(() => pastikanS(k), 30000); }
  }

  // ---- F: baca penuh (kueri sendiri) ----
  function mulaiF(k, mode) {
    const st = K[k]; if (G.berhenti) return;
    if (st.fLepas) { if (st.fMode !== mode) st.fMode = mode; return; }
    Object.assign(st, { fMode: mode, fAwal: null, fAwalKosong: false, fPrev: null, fTerkini: false, fSelesai: false, fGalat: '', fUlang: 0, fDiperiksa: false, fMulai: jam() });
    if (mode === 'total') { const H = hariR(); H.mulai[k] = (H.mulai[k] || 0) + 1; simpan(); }
    st.fLepas = o.sdk.penuh(k, (s) => fMasuk(k, s), (e) => fGalat(k, e));
  }
  function lepasF(k) { const st = K[k]; if (st.fLepas) { try { st.fLepas(); } catch (e) { /* abaikan */ } } st.fLepas = null; st.fTerkini = false; }
  function fMasuk(k, snap) {
    const st = K[k]; if (G.berhenti) return; st.fGalat = '';
    const peta = {}; let maks = null, n = 0;
    // sidik isi untuk SEMUA dokumen F: pendeteksi tanpa cap membandingkan isi (Console bisa mengubah isi tanpa menyentuh cap)
    (snap.dok || []).forEach((d) => { if (d.tunda) { peta[d.id] = { tunda: true }; return; } n += 1; const c = hbCapMs(d.capMentah);
      peta[d.id] = { cap: c, sidik: hbSidik(d.isi()) }; if (typeof c === 'number' && (maks === null || c > maks)) maks = c; });
    if (snap.dariCache) { if (!st.fAwal) st.fAwal = peta; st.fTerkini = false; nilaiPeriksa(k); return; }
    if (!st.fAwal) { st.fAwal = {}; st.fAwalKosong = true; }
    // isi MENTAH snapshot server ini untuk penyentuh (kunci bulan) — catatan lahir ulang yang tersembunyi nisan tidak ada di memori
    const dokF = {}; (snap.dok || []).forEach((d) => { if (!d.tunda) dokF[d.id] = d; });
    const lihatF = (id) => { const d = dokF[id]; if (!d) return lihatV(k)(id); const x = d.isi(); hbKupas(x); return x; };
    // LAHIR ULANG (tinjauan 7 Okt): ada di snapshot SERVER padahal batu nisannya berlaku = dibuat lagi sesudah dihapus → bukti dicatat di rekam (nisan berhenti
    // menyembunyikannya di perangkat ini) & catatannya disentuh (cap jam server baru > nisan) supaya perangkat lain ikut melihatnya
    const lahir = catatLahir(k, peta);
    const kini = jam(); const prev = st.fPrev || st.fAwal || {}; let baru = 0;
    Object.keys(peta).forEach((id) => { const a = prev[id], b = peta[id]; if (b.tunda) return; if (a && !a.tunda && a.cap === b.cap && a.sidik === b.sidik) return;
      baru += 1; G.hidup.catat(k, id, typeof b.cap === 'number' ? { cap: b.cap } : { sidik: b.sidik }, kini); });
    if (st.fPrev) Object.keys(st.fPrev).forEach((id) => { if (!peta[id] && !st.fPrev[id].tunda) G.hidup.catat(k, id, { hilang: true }, kini); });
    tambahBaca(st.fPrev ? baru : n + 1);
    // PENDETEKSI di SETIAP snapshot server F (baca penuh maupun dengar penuh), dibanding snapshot F sebelumnya (pertama: simpanan) — catatan yang berubah /
    // lahir / hilang TANPA cap disentuh atau diberi nisan, jadi perangkat lain menerimanya lewat delta. Hanya kalau dasar perangkat ini dipercaya (simpanan
    // kosong / belum terbaca penuh tidak membanjiri sentuhan). Tanpa ini, baca penuh perangkat mana pun "menelan" ubahan Console diam-diam.
    if (st.dipercaya && !(st.fAwalKosong && !st.fPrev)) deteksi(k, prev, peta, lahir, lihatF);
    else if (lahir.length && !G.bkAktif) kirimTemuan(k, 's', lahir, lihatF);
    st.fPrev = peta; st.fN = n; st.fMaks = maks; st.fTerkini = true;
    G.hidup.cocokkan(k, vLihat(k), kecuali(k)); jadwalHidup();
    if (!st.fSelesai) cekSelesaiF(k); else if (G.klaimSaya) cekKlaimSelesai();
    nilaiPeriksa(k);
  }
  // F gagal: koleksi tetap belum terperiksa (gerbang katalog & uang-kritis tertutup), memori tetap dari simpanan; tirai "memuat" tidak menggantung selamanya
  function fGagal(k, sebab) { const st = K[k]; lepasF(k); st.fGalat = sebab; st.fGagalPada = jam(); if (!st.siap) { siapK(k); G.kabar = 'Baca penuh ' + k + ' gagal (' + sebab + ') — angka dari simpanan perangkat, belum terperiksa'; } nilaiPeriksa(k); }
  function fGalat(k, e) { K[k].fLepas = null; fGagal(k, kodeGalat(e)); }
  function cekSelesaiF(k) {
    const st = K[k]; if (st.fHitungJalan || st.fSelesai || !st.fTerkini || G.berhenti) return;
    if (tundaN(k) > 0 || o.hapusTunda(k) > 0) return;   // dinilai lagi di snapshot berikutnya
    st.fHitungJalan = true; tambahBaca(1);
    o.sdk.hitung(k).then((n) => {
      st.fHitungJalan = false; if (G.berhenti || st.fSelesai) return;
      if (n === st.fN) return selesaiF(k);
      if ((st.fUlang || 0) < 1) { st.fUlang = 1; o.jadwal(() => cekSelesaiF(k), 15000); return; }
      fGagal(k, 'hitungan server ' + n + ' ≠ ' + st.fN + ' sesudah baca penuh');
    }).catch((e) => { st.fHitungJalan = false; fGagal(k, kodeGalat(e)); });
  }
  function selesaiF(k) {
    const st = K[k]; const s = kiniS(); if (s === null) { st.fTungguJam = true; return; }
    st.fTungguJam = false; const r = rk(k);
    Object.assign(r, { Wt: hbJepit(st.fMaks, s), n: st.fN, totalPada: kiniSTercatat(), gen: hbGen(G.tetap.klaim, k), bk: G.sidikBk, cocokPada: s });
    const beres = Object.assign({}, r.gerbangBeres || {}); G.gerbang.peristiwa.forEach((p) => { beres[p.kunci] = s; });
    Object.keys(beres).forEach((x) => { if (!(s - beres[x] <= (HB_KASIR_HARI + 1) * hbHari)) delete beres[x]; }); r.gerbangBeres = beres;
    const H = hariR(); if (st.otomatis && st.fMode === 'total') H.otomatis[k] = (H.otomatis[k] || 0) + 1;
    if (G.minta[k]) delete G.minta[k];
    Object.assign(st, { fSelesai: true, fSelesaiPada: s, dipercaya: true, sebabDasar: '', cocokPada: jam(), fGagalPada: 0, fGalat: '' });
    if (st.fMode === 'total') { lepasF(k); st.mode = 'delta'; st.sebab = ''; }
    simpan(); siapK(k); pastikanS(k); nilaiPeriksa(k);
    if (G.klaimSaya) cekKlaimSelesai();
  }

  // ---- N: batu nisan ----
  function pastikanN() {
    if (G.berhenti) return;
    const Bn = hbBatasNisan(o.koleksi.map((k) => rk(k).totalPada), kiniS()); if (Bn === null) return;
    if (G.nLepas && G.nB !== null && Bn >= G.nB) return;
    if (G.nLepas) { try { G.nLepas(); } catch (e) { /* abaikan */ } }
    G.nB = Bn; G.nTerkini = false; tambahBaca(1);
    G.nLepas = o.sdk.nisan(Bn, nMasuk, (e) => { G.nGalat = kodeGalat(e); G.nTerkini = false; G.nLepas = null; o.koleksi.forEach(nilaiPeriksa); });
  }
  function nMasuk(snap) {
    if (G.berhenti) return; G.nGalat = '';
    const baru = {}; let n = 0;
    (snap.dok || []).forEach((d) => { if (d.tunda) return; const x = d.isi(); const c = hbCapMs(d.capMentah); if (typeof c !== 'number' || !x || !x.koleksi || x.idDok === undefined) return;
      const m = baru[x.koleksi] || (baru[x.koleksi] = {}); const id = String(x.idDok); if (!(m[id] >= c)) m[id] = c; n += 1; });
    const kena = o.koleksi.filter((k) => JSON.stringify(baru[k] || {}) !== JSON.stringify(G.nisan[k] || {}));
    G.nisan = baru; if (!snap.dariCache) { G.nTerkini = true; tambahBaca(kena.length ? n : 0); } else G.nTerkini = false;
    if (!snap.dariCache) {
      // bukti lahir ulang yang nisannya sudah keluar jendela N, atau berganti nisan LEBIH BARU (dihapus lagi), dibuang
      let ubah = false;
      o.koleksi.forEach((k) => { const L = rk(k).lahir; if (!L) return; Object.keys(L).forEach((id) => { const t = (baru[k] || {})[id]; if (t === undefined || t > L[id]) { delete L[id]; ubah = true; } }); });
      if (ubah) simpan();
      // nisan berubah: catatan yang kini disembunyikannya mungkin LAHIR ULANG (baca penuh sebelumnya melihatnya sebelum nisan ini tiba) → hitungan server
      // dinilai lagi (beda → baca penuh → pendeteksi); koleksi yang F-nya menempel diperiksa dari snapshot server F terakhir SESUDAH semua pendengar
      // peristiwa yang sama dikabari (jadwal 0 — kalau tidak, hapus yang tiba lewat N lebih dulu dari F terbaca "lahir ulang")
      kena.forEach((k) => { K[k].cocokPada = 0; if (K[k].fLepas && K[k].fTerkini) o.jadwal(() => cekLahirF(k), 0); });
    }
    kena.forEach(pasokK); o.koleksi.forEach((k) => { G.hidup.cocokkan(k, vLihat(k), kecuali(k)); cekHitung(k); nilaiPeriksa(k); });
  }

  // ---- hitungan server ----
  function cekHitung(k, paksa) {
    const st = K[k]; if (G.berhenti || st.hitungJalan || !G.online || st.mode === 'penuh' || !st.sTerkini || !G.nTerkini || !st.vAda) return;
    if (st.fLepas && st.fMode === 'total' && !st.fSelesai) return;
    if (tundaN(k) > 0 || o.hapusTunda(k) > 0) return;
    const perlu = paksa || !st.cocokPada || (HB_KOLEKSI_REST.indexOf(k) >= 0 && jam() - st.cocokPada > HB_BERKALA_MS); if (!perlu) return;
    st.hitungJalan = true; tambahBaca(1);
    const janji = o.sdk.hitung(k).then((n) => {
      st.hitungJalan = false; if (G.berhenti) return 'batal';
      const h = hbNilaiHitung({ server: n, mentah: Object.keys(st.v).length, tersembunyi: st.tersembunyi || 0, tunda: tundaN(k), hapusTunda: o.hapusTunda(k) });
      st.hitungHasil = h; st.hitungServer = n;
      if (h === 'cocok') { st.cocokPada = jam(); st.hitungUlang = 0; const s = kiniS(); if (s !== null && st.wdCalon) { rk(k).Wd = Math.max(hbAngka(rk(k).Wd) || 0, hbJepit(st.wdCalon, s)); rk(k).cocokPada = s; simpan(); } }
      else if (h === 'kurang' || h === 'lebih') {
        st.cocokPada = 0;
        if ((st.hitungUlang || 0) < 1) { st.hitungUlang = 1; o.jadwal(() => cekHitung(k, true), 15000); }
        else { st.hitungUlang = 0; minta([k], 'hitungan server ' + n + ' beda dengan perangkat ini', false); }
      }
      nilaiPeriksa(k); return h;
    }).catch((e) => { st.hitungJalan = false; st.hitungHasil = 'galat'; st.hitungGalat = kodeGalat(e); nilaiPeriksa(k); return 'galat'; });
    st.hitungJanji = janji; return janji;
  }

  // ---- pendeteksi tanpa cap (tiap snapshot server F) ----
  function deteksi(k, sebelum, sekarang, lahir, lihat) {
    const t = hbPeriksaTanpaCap(sebelum, sekarang, G.nisan[k], true, G.hapusSesi[k]); const tm = G.temuan[k] || (G.temuan[k] = { ubah: 0, baru: 0, hilang: 0 });
    // koleksi yang DENGAR PENUH karena penulis tanpa cap (HP kasir < kasir-v33, kasir.html, tab /baru/ lama): semua perangkat owner melihat gerbang yang sama
    // dan mendengarnya penuh — catatan yang LAHIR tanpa cap tidak disentuh (tulisan ganda + satu baris jejak per nota per perangkat tanpa guna, dan nota HP
    // lama yang dikirim ulang sesudah disentuh dulu ditolak rules). Perangkat yang absen selama gerbang menangkapnya lewat hitungan server / baca penuh ≤ 14 hari.
    if (G.gerbang.penuh[k] && t.baru.length) { tm.lewat = (tm.lewat || 0) + t.baru.length; t.baru = []; }
    // tutup buku berubah sejak baca penuh terakhir perangkat ini: catatan yang hilang dari server = DIARSIPKAN (arsip tanpa batu nisan), bukan dihapus tanpa
    // kabar — tanpa ini tiap perangkat yang tertutup selama ritual menulis ratusan batu nisan (atau gen baru → semua perangkat baca penuh) tiap 2 Jan
    if (bkBeda(k) && t.hilang.length) { tm.arsip = (tm.arsip || 0) + t.hilang.length; t.hilang = []; }
    const r = hbRencanaSentuh(t, G.bkAktif);
    tm.ubah += t.ubah.length; tm.baru += t.baru.length; tm.hilang += t.hilang.length;
    if (r.gen) G.genMinta[k] = true;
    // catatan LAHIR ULANG selalu disentuh (kecuali tutup buku berjalan) — juga saat > 400 temuan (gen tidak menolong: nisan tetap menyembunyikannya)
    const sentuh = G.bkAktif ? r.sentuh : r.sentuh.concat((lahir || []).filter((id) => r.sentuh.indexOf(id) < 0));
    kirimTemuan(k, 's', sentuh, lihat); kirimTemuan(k, 'n', r.nisan);
    if (r.gen && !G.klaimSaya) cekGen();
  }
  /** Catatan di snapshot server Z yang tersembunyi nisan padahal ada di server = lahir ulang → bukti dicatat di rekam (tahan muat ulang), memori dipasok ulang. */
  function catatLahir(k, Z) {
    const ids = hbLahirUlang(Z, G.nisan[k], lahirK(k)); if (!ids.length) return ids;
    const L = rk(k).lahir || (rk(k).lahir = {}); ids.forEach((id) => { L[id] = G.nisan[k][id]; }); simpan(); pasokK(k); return ids;
  }
  function cekLahirF(k) { const st = K[k]; if (G.berhenti || !st.fLepas || !st.fTerkini || !st.fPrev) return; const ids = catatLahir(k, st.fPrev); if (ids.length && !G.bkAktif) kirimTemuan(k, 's', ids); }
  // TEMUAN dikirim lewat antrean di rekam: yang GAGAL (ditolak server, tab ini tidak boleh menulis) dicoba lagi tiap menit ≤ HB_ULANG_MAKS kali, juga sesudah
  // muat ulang — dulu dibuang diam-diam, padahal snapshot F berikutnya sudah tidak melihat bedanya lagi (tinjauan 7 Okt). jenis 's' = sentuh, 'n' = nisan.
  // Sanggahan 7 Okt: yang gagal permanen (≤ 5 kali) DAN yang dilewati penyentuh karena bulannya terkunci (`lewat` — tidak bisa disentuh, perangkat lain tidak
  // menerimanya lewat delta) dihitung per koleksi untuk baca penuh harian toko yang sedang dipegang (`temuanTunda` di dokumen klaim).
  function kirimTemuan(k, jenis, ids, lihat) {
    if (!ids || !ids.length) return;
    const U = R.ulang || (R.ulang = {}); const q = U[k] || (U[k] = {}); const m = q[jenis] || (q[jenis] = {});
    ids.forEach((id) => { if (m[id] === undefined) m[id] = 0; }); simpan();
    kirimUlang(k, jenis, lihat);
  }
  function kirimUlang(k, jenis, lihat) {
    const kunci = k + '|' + jenis; if (G.ulangJalan[kunci] || G.berhenti || !K[k]) return;
    const m = ((R.ulang || {})[k] || {})[jenis]; const ids = m ? Object.keys(m) : []; if (!ids.length) return;
    ids.forEach((id) => { m[id] += 1; }); G.ulangJalan[kunci] = true;
    const janji = jenis === 's' ? o.sdk.sentuh(k, ids, lihat || lihatV(k)) : o.sdk.tulisNisan(k, ids);
    Promise.resolve(janji).then((h) => h, () => ({ tunda: ids })).then((h) => {
      G.ulangJalan[kunci] = false; const tunda = (h && h.tunda) || []; const lewat = (h && h.lewat) || [];
      const tundaToko = () => { if (G.klaimSaya) G.klaimTunda[k] = (G.klaimTunda[k] || 0) + 1; };
      ids.forEach((id) => {
        if (lewat.indexOf(id) >= 0) { delete m[id]; G.temuanLewat += 1; tundaToko(); }
        else if (tunda.indexOf(id) < 0) delete m[id];
        else if (m[id] >= HB_ULANG_MAKS) { delete m[id]; G.temuanGagal += 1; tundaToko(); }
      });
      simpan(); o.keluar.berubah();
      // baca penuh harian toko menunggu antrean temuan habis (terkirim, atau gagal permanen & dihitung) sebelum menulis "selesai"
      if (G.klaimSaya) cekKlaimSelesai();
    });
  }
  /** Masih ada temuan pendeteksi di antrean (belum terkirim, belum gagal permanen) untuk koleksi sesi ini? */
  const antreTemuan = () => o.koleksi.some((k) => { const q = (R.ulang || {})[k] || {}; return ['s', 'n'].some((j) => !!q[j] && Object.keys(q[j]).length > 0); });
  // gen baru dari perangkat INI: koleksi yang baru saja dibaca penuh di sini tidak perlu dibaca penuh lagi
  function samakanGen(gen) { Object.keys(G.genMinta).forEach((k) => { if (K[k] && (K[k].fSelesai || (K[k].mode === 'penuh' && K[k].fTerkini))) rk(k).gen = hbGen({ gen }, k); }); simpan(); }
  // > 400 temuan di luar baca penuh harian: gen koleksi itu langsung dinaikkan di dokumen klaim (semua perangkat baca penuh koleksi itu)
  function cekGen() {
    if (!Object.keys(G.genMinta).length) return; const s = kiniS() !== null ? kiniS() : jam(); const lama = G.tetap.klaim || {};
    const gen = Object.assign({}, lama.gen || {}); Object.keys(G.genMinta).forEach((k) => { gen[k] = 'g' + s; }); samakanGen(gen); G.genMinta = {};
    o.sdk.klaim(Object.assign({}, lama, { id: HB_ID_KLAIM, gen })).catch(() => {});
  }

  // ---- baca penuh harian per toko ----
  function nilaiKlaim() {
    if (G.berhenti || !G.tetap.ada || G.klaimJalan || G.klaimSaya || !G.online || (o.milikTab && !o.milikTab())) return;
    if (!o.koleksi.every((k) => K[k].vAda)) return;
    const r = hbKlaimHarian(G.tetap.klaim, kiniS(), o.idPerangkat); G.klaimKabar = r.sebab; if (!r.klaim) return;
    const H = hariR(); const ukuran = o.koleksi.reduce((a, k) => a + (Number(rk(k).n) || Object.keys(K[k].v).length), 0);
    const rem = hbRem({ perkiraan: hbPerkiraanToko(G.tetap.perangkat, H.H, o.idPerangkat, H.baca), ukuran });
    if (!rem.boleh) { G.klaimKabar = 'baca penuh harian ditunda: ' + rem.sebab; return; }
    G.klaimJalan = true; const s = kiniS();
    const dok = Object.assign({}, G.tetap.klaim || {}, { id: HB_ID_KLAIM, hari: r.hari, perangkat: o.idPerangkat, nama: o.namaPerangkat || o.idPerangkat, mulai: s, selesai: null, temuan: null, temuanTunda: null });
    o.sdk.klaim(dok).then(() => {
      G.klaimJalan = false; G.klaimSaya = true; G.klaimMulai = s; G.temuan = {}; G.klaimTunda = {}; G.klaimKabar = 'perangkat ini membaca penuh untuk toko (hari kuota ' + r.hari + ')';
      putuskanSemua(); o.keluar.berubah();
    }).catch(() => { G.klaimJalan = false; });
  }
  function cekKlaimSelesai() {
    // koleksi yang sedang dengar penuh (F menempel & terkini) sudah terbaca penuh — tidak perlu baca penuh kedua
    if (!G.klaimSaya || !o.koleksi.every((k) => (K[k].fSelesai && K[k].fSelesaiPada >= G.klaimMulai) || (K[k].mode === 'penuh' && K[k].fTerkini))) return;
    // sanggahan 7 Okt: "selesai" = bukti LENGKAP bagi perangkat owner lain (hbBelumLengkap). Selama sentuhan / batu nisan temuan pendeteksi belum terkirim,
    // perangkat lain belum menerima ubahan itu lewat delta — "selesai" ditunda sampai antreannya habis (dinilai lagi tiap kiriman antrean selesai, kirimUlang).
    if (antreTemuan()) { G.klaimKabar = 'baca penuh harian sudah membaca semua — menunggu ubahan tanpa cap terkirim ke perangkat lain'; return; }
    const s = kiniS(); G.klaimSaya = false; const lama = G.tetap.klaim || {};
    const gen = Object.assign({}, lama.gen || {}); Object.keys(G.genMinta).forEach((k) => { gen[k] = 'g' + s; }); samakanGen(gen); G.genMinta = {};
    // temuan yang tidak bisa sampai ke perangkat lain (gagal permanen / bulan terkunci) per koleksi → perangkat lain "harian" untuk koleksi itu (baca penuh sendiri)
    const tt = {}; Object.keys(G.klaimTunda).forEach((k) => { if (G.klaimTunda[k] > 0) tt[k] = G.klaimTunda[k]; });
    const dok = Object.assign({}, lama, { id: HB_ID_KLAIM, perangkat: o.idPerangkat, nama: o.namaPerangkat || o.idPerangkat, selesai: s, temuan: G.temuan, temuanTunda: Object.keys(tt).length ? tt : null, gen });
    G.klaimKabar = 'baca penuh harian selesai' + (Object.keys(tt).length ? ' — ' + Object.keys(tt).reduce((a, k) => a + tt[k], 0) + ' ubahan tanpa cap belum bisa sampai ke perangkat lain (mereka diminta baca penuh sendiri)' : '');
    o.sdk.klaim(dok).catch(() => {});
  }

  // ---- kelengkapan & terperiksa: SATU sumber (hbBelumLengkap). Terperiksa = bukan "belum terperiksa" ('harian' tetap terperiksa: hitungannya cocok) ----
  function belumK(k) {
    const st = K[k]; const r = rk(k);
    // berhenti: tab kalah kunci tab (firebase.js berhenti → terminate) — tidak menerima data lagi; tanpa ini tab itu tetap melapor lengkap (sanggahan 7 Okt)
    return hbBelumLengkap({ koleksi: k, vMati: st.vMati, berhenti: G.berhenti, vAda: st.vAda, nTerkini: G.nTerkini, online: G.online, mode: st.mode, fTerkini: st.fTerkini, fSelesai: st.fSelesai, fMode: st.fMode,
      fJalan: !!(st.fLepas && st.fMode === 'total' && !st.fSelesai), fGalat: st.fGalat, wajibTotal: st.wajibTotal, sTerkini: st.sTerkini, cocok: st.cocokPada > 0,
      totalPada: r.totalPada, hari: hariKini(), klaim: G.tetap.klaim });
  }
  function terperiksaK(k) { const b = belumK(k); return !b || b.jenis !== 'periksa'; }
  function nilaiPeriksa(k) { const st = K[k]; const t = terperiksaK(k); if (t !== st.terperiksa) { st.terperiksa = t; o.keluar.periksa(k, t); } o.keluar.berubah(); }

  // ---- pendengar simpanan hidup ----
  function jadwalHidup() { if (G.hidupH || !G.hidup.ada()) return; G.hidupH = o.jadwal(() => { G.hidupH = null; cekHidup(); }, HB_HIDUP_MS + 500); }
  function cekHidup() {
    o.koleksi.forEach((k) => G.hidup.cocokkan(k, vLihat(k), kecuali(k)));
    G.hidup.mati(jam()).forEach((k) => { const st = K[k]; if (st.vMati) return; st.vMati = true; o.keluar.mati(k); nilaiPeriksa(k); });
    if (G.hidup.ada()) jadwalHidup();
  }

  // ---- minta baca penuh ----
  function minta(daftar, sebab, manual) {
    (daftar || o.koleksi).forEach((k) => { if (!K[k]) return; G.minta[k] = { sebab, manual: !!manual }; if (K[k].fSelesai) K[k].fSelesai = false; K[k].fUlang = 0; });
    putuskanSemua();
  }

  const kodeGalat = (e) => String((e && (e.code || e.message)) || e || 'galat');
  const sesi = {
    mulai() {
      o.koleksi.forEach((k) => { K[k] = { k, v: {}, vAda: false, siap: false, dipercaya: null, mode: null, terperiksa: null, tersembunyi: 0 }; });
      o.koleksi.forEach((k) => { K[k].vLepas = o.sdk.cache(k, (s) => vMasuk(k, s), (e) => { K[k].vGalat = kodeGalat(e); nilaiPeriksa(k);
        if (!K[k].vUlang && !G.berhenti) { K[k].vUlang = 1; K[k].vLepas = o.sdk.cache(k, (s) => vMasuk(k, s), (e2) => { K[k].vGalat = kodeGalat(e2); K[k].vMati = true; o.keluar.mati(k); nilaiPeriksa(k); }); } }); });
      if (hbAngka(R.skew) !== null) G.skewRekam = R.skew;
      return sesi;
    },
    /** Masukan dari pendengar koleksi TETAP: { perangkat: denyut[], acara: tutupBukuAcara[], klaim: aturanToko/hematHarian | null }. */
    setelTetap(t) {
      const lamaBk = G.sidikBk; Object.assign(G.tetap, t || {}); G.tetap.ada = true;
      const lihatLama = JSON.stringify(R.lihat || {}); const lihat = lihatDenyut(); if (JSON.stringify(R.lihat) !== lihatLama) simpan();
      G.gerbang = hbGerbangPenulis(G.tetap.perangkat, kiniS() !== null ? kiniS() : jam(), o.koleksi, lihat);
      G.bkAktif = hbBkAktif(G.tetap.acara); G.sidikBk = hbSidikBk(G.tetap.acara);
      if (lamaBk && G.sidikBk !== lamaBk) o.koleksi.forEach((k) => { const st = K[k]; if (st.mode === 'penuh' && st.fTerkini && hbAngka(rk(k).totalPada) !== null) rk(k).bk = G.sidikBk; });
      putuskanSemua(); nilaiKlaim(); o.keluar.berubah();
    },
    /** Gema jam server: capServer denyut perangkat ini yang baru diakui server, tiba saat jam perangkat = perangkatMs. */
    gemaServer(serverMs, perangkatMs) {
      if (!(hbAngka(serverMs) > 0) || !(hbAngka(perangkatMs) > 0)) return;
      G.skew = serverMs - perangkatMs; G.gemaS = serverMs;   // HANYA dari gema denyut sendiri — cap di data (bisa tahun 2099) tidak pernah menggeser jam server
      R.skew = G.skew; simpan();
      o.koleksi.forEach((k) => { if (K[k].fTungguJam) selesaiF(k); });
      G.gerbang = hbGerbangPenulis(G.tetap.perangkat, kiniS(), o.koleksi, lihatDenyut());
      putuskanSemua(); nilaiKlaim();
    },
    online(ya) {
      G.online = !!ya;
      if (ya) { o.koleksi.forEach((k) => { K[k].cocokPada = 0; K[k].hitungUlang = 0; }); putuskanSemua(); o.koleksi.forEach((k) => cekHitung(k)); nilaiKlaim(); }
      o.koleksi.forEach(nilaiPeriksa);
    },
    terlihat(ya) {
      if (!ya) { G.tersembunyiSejak = jam(); return; }
      if (G.tersembunyiSejak && jam() - G.tersembunyiSejak > 30 * hbMenit) o.koleksi.forEach((k) => { K[k].cocokPada = 0; cekHitung(k); });
      G.tersembunyiSejak = 0; nilaiKlaim();
    },
    /** Dipanggil berkala (±1 menit selama terlihat): hitungan berkala koleksi HP kasir, geser B, klaim harian, pendengar hidup. */
    tik() {
      if (G.berhenti) return;
      o.koleksi.forEach((k) => cekHitung(k));
      o.koleksi.forEach((k) => { const st = K[k]; if (!st.sLepas || !st.sTerkini) return; const r = hbBatasDelta(rk(k), kiniS(), hariKini());
        if (r.B !== null && r.baru && r.B > st.sB) { Object.assign(rk(k), { B: r.B, hariB: r.hariB, nB: r.nB }); simpan(); try { st.sLepas(); } catch (e) { /* abaikan */ } st.sLepas = null; st.sUlang = 0; pastikanS(k); } });
      nilaiKlaim(); cekHidup();
      Object.keys(R.ulang || {}).forEach((k) => { if (K[k]) ['s', 'n'].forEach((j) => kirimUlang(k, j)); });
    },
    /** Tombol "Baca penuh sekarang" / "Saya baru mengubah lewat Console" (manual = menembus rem). Tiap baca penuh juga MENDETEKSI ubahan tanpa cap & menyentuhnya. */
    bacaPenuh(daftar, sebab, manual) { minta(daftar && daftar.length ? daftar : null, sebab || 'tombol baca penuh', manual !== false); },
    /** Tombol "Minta semua perangkat baca penuh": gen '*' baru di dokumen klaim. */
    mintaSemua() { const s = kiniS() !== null ? kiniS() : jam(); const lama = G.tetap.klaim || {}; const gen = Object.assign({}, lama.gen || {}, { '*': 'g' + s });
      return o.sdk.klaim(Object.assign({}, lama, { id: HB_ID_KLAIM, gen })); },
    catatHapus(k, id) { if (!K[k]) return; (G.hapusSesi[k] = G.hapusSesi[k] || {})[String(id)] = true; },
    /** Uang-kritis: tiap koleksi hemat terperiksa dengan hitungan server ≤ 2 menit (atau dengar penuh terkini). → Promise<{ ok, pesan }> */
    pastikanSegar() {
      const perlu = o.koleksi.filter((k) => { const st = K[k]; if (st.vMati) return true; if (st.mode === 'penuh' && st.fTerkini) return false; return !(terperiksaK(k) && jam() - st.cocokPada <= HB_SEGAR_MS); });
      if (!perlu.length) return Promise.resolve({ ok: true, pesan: '' });
      if (G.berhenti || o.koleksi.some((k) => K[k].vMati)) return Promise.resolve({ ok: false, pesan: 'tab ini berhenti menerima data — muat ulang aplikasi dulu' });
      if (!G.online) return Promise.resolve({ ok: false, pesan: 'belum bisa dipastikan — sambungkan internet dulu (draf tetap tersimpan)' });
      const belum = perlu.filter((k) => !K[k].sTerkini || !G.nTerkini || K[k].wajibTotal || (K[k].fLepas && K[k].fMode === 'total' && !K[k].fSelesai));
      if (belum.length) return Promise.resolve({ ok: false, pesan: 'data ' + belum.slice(0, 3).join(', ') + (belum.length > 3 ? ' …' : '') + ' belum terperiksa dengan server — tunggu sebentar lalu coba lagi' });
      const tunda = perlu.filter((k) => tundaN(k) > 0 || o.hapusTunda(k) > 0);
      if (tunda.length) return Promise.resolve({ ok: false, pesan: 'masih ada catatan perangkat ini yang menunggu server (' + tunda.slice(0, 3).join(', ') + ') — tunggu antrean kosong lalu coba lagi' });
      // hitungan SEGAR sekarang (yang sedang berjalan ditunggu dulu, lalu dihitung lagi — hasil lama tidak dipakai)
      const hitungSekarang = (k) => Promise.resolve(K[k].hitungJalan ? K[k].hitungJanji : null).catch(() => null).then(() => cekHitung(k, true) || 'belum');
      let i = 0; const hasil = [];
      const jalan = () => { if (i >= perlu.length) return Promise.resolve(); const k = perlu[i++]; return hitungSekarang(k).then((h) => { hasil.push([k, h]); return jalan(); }); };
      return Promise.all([jalan(), jalan(), jalan(), jalan(), jalan(), jalan()]).then(() => {
        const beda = hasil.filter((x) => x[1] === 'kurang' || x[1] === 'lebih'); const galat = hasil.filter((x) => x[1] !== 'cocok' && x[1] !== 'kurang' && x[1] !== 'lebih');
        if (beda.length) { minta(beda.map((x) => x[0]), 'uang-kritis: hitungan server beda', true); return { ok: false, pesan: 'data ' + beda.map((x) => x[0]).join(', ') + ' belum cocok dengan server — sedang dibaca ulang, coba lagi sebentar' }; }
        if (galat.length) return { ok: false, pesan: 'belum bisa dipastikan (' + galat.map((x) => x[0]).slice(0, 3).join(', ') + ') — sambungkan internet lalu coba lagi' };
        return { ok: true, pesan: '' };
      });
    },
    /** Gerbang katalog kasir (tambahan saat nyala): semua koleksi hemat terperiksa, tidak ada V mati, hitungan koleksi HP kasir ≤ 35 menit. */
    bolehKatalog() {
      if (G.berhenti || o.koleksi.some((k) => K[k].vMati)) return { boleh: false, sebab: 'tab ini berhenti menerima data' };
      const b = o.koleksi.filter((k) => !terperiksaK(k)); if (b.length) return { boleh: false, sebab: 'data belum terperiksa dengan server (' + b.slice(0, 3).join(', ') + ')' };
      const lama = HB_KOLEKSI_REST.filter((k) => K[k] && K[k].mode !== 'penuh' && !(K[k].cocokPada > 0 && jam() - K[k].cocokPada <= HB_KATALOG_SEGAR_MS));
      if (lama.length) return { boleh: false, sebab: 'hitungan server ' + lama.join(', ') + ' lebih dari 35 menit' };
      return { boleh: true, sebab: '' };
    },
    keadaan() {
      const daftar = o.koleksi.map((k) => { const st = K[k], r = rk(k); return { k, mode: st.mode, sebab: st.wajibTotal || st.sebab || '', terperiksa: terperiksaK(k), totalPada: hbAngka(r.totalPada), cocokPada: st.cocokPada || 0,
        galat: st.vGalat || st.sGalat || st.fGalat || st.hitungGalat || '', vMati: !!st.vMati, bacaJalan: !!(st.fLepas && st.fMode === 'total' && !st.fSelesai), selesaiSesi: !!st.fSelesai, wajibTotal: st.wajibTotal || '' }; });
      const s = kiniS();
      return { nyala: true, jamServer: s !== null, kiniS: s, hari: s !== null ? hbHariKuota(s) : '', jamReset: s !== null ? hbJamResetWib(s) : '', koleksi: daftar,
        belum: daftar.filter((x) => !x.terperiksa).map((x) => x.k), vMati: daftar.some((x) => x.vMati), nisanTerkini: G.nTerkini, nisanGalat: G.nGalat,
        totalSesiIni: daftar.every((x) => x.selesaiSesi), klaim: G.tetap.klaim, klaimSaya: G.klaimSaya, klaimKabar: G.klaimKabar, temuan: G.temuan, jalurPenuh: G.jalurPenuh,
        kabar: [G.kabar, G.temuanGagal ? G.temuanGagal + ' catatan berubah tanpa cap gagal ditandai untuk perangkat lain — tekan "Saya baru mengubah data lewat Console"' : '',
          G.temuanLewat ? G.temuanLewat + ' catatan di bulan terkunci berubah tanpa cap — perangkat lain baru melihatnya sesudah membaca penuh sendiri' : ''].filter((x) => !!x).join(' · '),
        baca: { perangkat: R.hari.baca || 0, toko: hbPerkiraanToko(G.tetap.perangkat, R.hari.H, o.idPerangkat, R.hari.baca) }, belumLengkap: sesi.belumLengkap() };
    },
    /** SATU sumber kelengkapan (hbBelumLengkap) untuk layar: { koleksi: { jenis, sebab } } — hanya koleksi yang BELUM lengkap; {} = semua lengkap. */
    belumLengkap() { const out = {}; o.koleksi.forEach((k) => { if (!K[k]) return; const b = belumK(k); if (b) out[k] = b; }); return out; },
    ringkasDenyut() { const H = hariR(); return { hari: H.H || '', baca: Math.round(H.baca || 0) }; },
    /** cap per id di simpanan perangkat (V) koleksi k — daftar siap-nyala "statis" saat nyala (peta samping _cap hanya diisi pendengar penuh). */
    capPeta(k) { const v = K[k] ? K[k].v : {}; const o2 = {}; Object.keys(v).forEach((id) => { o2[id] = v[id].cap; }); return o2; },
    /** jam server saat denyut tiap perangkat terlihat berubah (umur denyut daftar siap-nyala). */
    lihatDenyut() { return Object.assign({}, lihatDenyut()); },
    berhenti() {
      G.berhenti = true;
      o.koleksi.forEach((k) => { const st = K[k]; if (!st) return; [st.vLepas, st.sLepas, st.fLepas].forEach((f) => { if (f) { try { f(); } catch (e) { /* abaikan */ } } }); st.vLepas = st.sLepas = st.fLepas = null; });
      if (G.nLepas) { try { G.nLepas(); } catch (e) { /* abaikan */ } } G.nLepas = null; if (G.hidupH) o.batal(G.hidupH);
    },
    adaMati: () => o.koleksi.some((k) => K[k] && K[k].vMati),
    _K: K, _G: G,
  };
  return sesi;
}
