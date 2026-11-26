// PUSH PAGI KALENDER KEPATUHAN (owner 26 Nov 2026: "Oh iya adakan/pasang notifikasi"). Murni: tanpa Firebase, tanpa jaringan — diuji di jsc oleh
// alat-uji/uji_gudang_label_patuh.py, yang juga MEWAJIBKAN rumus putaran di sini SAMA dengan baru/js/layar/patuh-logika.js (ptPutaran) untuk ratusan tanggal.
// Dipakai functions/index.js (kabarPatuh, tiap hari 07.00 WIB): membaca aturanToko/kepatuhan + kepatuhanCek, lalu mengirim SATU notifikasi ringkas ke HP / Mac
// owner (notifOwner) dan tablet Penjaga laci (notifPerangkat akun ber-peran ben yang aktif). Tidak menulis data toko.
// Kapan mengirim (supaya tidak cerewet): ada butir yang tepat H-"ingatkan" · H-7 · H-3 · H-1 · hari H, atau ada yang LEWAT dan hari ini Senin. Isinya semua
// butir yang sedang dalam jendela ingat (lewat · hari ini · segera).
'use strict';

const PT_MULAI = '2026-11-26';
const PT_ULANG = ['bulanan', 'triwulan', 'tahunan', 'sekali'];
const BAWAAN = ['spt', 'cek-het', 'cek-qris', 'cek-pajak', 'izin', 'label', 'tera', 'thr', 'tutup'];   // id butir bawaan (isinya di patuh-logika PT_BAWAAN)
const HARI_KIRIM = [7, 3, 1, 0];
const BATAS_ISI = 160;

const hariKe = (iso) => Math.round(new Date(String(iso) + 'T00:00:00Z').getTime() / 86400000);
const isoDari = (y, m, d) => { const akhir = new Date(Date.UTC(y, m, 0)).getUTCDate(); return y + '-' + String(m).padStart(2, '0') + '-' + String(Math.min(d, akhir)).padStart(2, '0'); };
const teks = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();

function tanggalSah(ulang, t) {
  const s = String(t || ''); if (!s) return true;
  if (ulang === 'bulanan' || ulang === 'triwulan') return /^\d{2}$/.test(s) && Number(s) >= 1 && Number(s) <= 31;
  if (ulang === 'tahunan') { if (!/^\d{2}-\d{2}$/.test(s)) return false; const m = Number(s.slice(0, 2)), d = Number(s.slice(3)); return m >= 1 && m <= 12 && d >= 1 && d <= new Date(Date.UTC(2024, m, 0)).getUTCDate(); }
  if (ulang === 'sekali') return /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(new Date(s + 'T00:00:00Z').getTime()) && new Date(s + 'T00:00:00Z').toISOString().slice(0, 10) === s;
  return false;
}
function periode(ulang, jatuh) {
  const y = jatuh.slice(0, 4), m = Number(jatuh.slice(5, 7));
  return ulang === 'bulanan' ? jatuh.slice(0, 7) : ulang === 'triwulan' ? y + '-K' + (Math.floor((m - 1) / 3) + 1) : ulang === 'tahunan' ? y : jatuh;
}
function jatuhSiklus(ulang, tgl, iso, k) {
  const y = Number(iso.slice(0, 4)), m = Number(iso.slice(5, 7));
  if (ulang === 'bulanan') { const t = y * 12 + (m - 1) + k; return isoDari(Math.floor(t / 12), t % 12 + 1, Number(tgl)); }
  if (ulang === 'triwulan') { const q = y * 4 + Math.floor((m - 1) / 3) + k; return isoDari(Math.floor(q / 4), (q % 4) * 3 + 1, Number(tgl)); }
  return isoDari(y + k, Number(tgl.slice(0, 2)), Number(tgl.slice(3)));
}
const tanggalBerlaku = (b, wp) => (b.id === 'spt' && !b.tanggal ? (wp === 'badan' ? '04-30' : '03-31') : String(b.tanggal || ''));
/** Cermin ptPutaran (patuh-logika.js) — rumus yang sama persis. */
function putaran(b, iso, sudah, wp) {
  const tgl = tanggalBerlaku(b, wp); if (!tgl || !tanggalSah(b.ulang, tgl)) return { tanpaTanggal: true };
  if (b.ulang === 'sekali') { const p = periode('sekali', tgl); return sudah(p) ? { selesai: true, periode: p, jatuh: tgl } : { jatuh: tgl, periode: p, sisa: hariKe(tgl) - hariKe(iso) }; }
  const mulai = b.mulai && /^\d{4}-\d{2}-\d{2}$/.test(String(b.mulai)) ? String(b.mulai) : PT_MULAI;
  let lalu = jatuhSiklus(b.ulang, tgl, iso, 0); if (lalu > iso) lalu = jatuhSiklus(b.ulang, tgl, iso, -1);
  if (lalu >= mulai && !sudah(periode(b.ulang, lalu))) return { jatuh: lalu, periode: periode(b.ulang, lalu), sisa: hariKe(lalu) - hariKe(iso) };
  for (let k = 0; k <= 3; k++) { const j = jatuhSiklus(b.ulang, tgl, iso, k); if (j <= iso) continue; if (!sudah(periode(b.ulang, j))) return { jatuh: j, periode: periode(b.ulang, j), sisa: hariKe(j) - hariKe(iso) }; }
  return { tanpaTanggal: true };
}
const WP = { perorangan: 'op', ptPerorangan: 'badan', cv: 'badan', firma: 'badan', koperasi: 'badan', pt: 'badan' };
/**
 * Isi push pagi. dok = aturanToko/kepatuhan (null = belum ada → butir bawaan berjalan tanpa tanggal kecuali yang bertanggal di bawaan), cek = isi dokumen kepatuhanCek,
 * bawaan = PT_BAWAAN (dikirim index.js dari salinan butir bawaan di sini — lihat BUTIR_BAWAAN), iso = hari ini WIB.
 * Hasil { kirim (bool), judul, isi, tag, n, daftar: [{ id, nama, sisa, jatuh }] }.
 */
function pesanPatuh(dok, cek, iso, hariMinggu) {
  const daftar = dok && Array.isArray(dok.butir) ? dok.butir : BUTIR_BAWAAN; const wp = WP[dok && dok.usaha ? dok.usaha.bentuk : ''] || '';
  const sudahPer = {}; (cek || []).forEach((c) => { if (c && typeof c.butir === 'string' && typeof c.periode === 'string') (sudahPer[c.butir] = sudahPer[c.butir] || {})[c.periode] = 1; });
  const seen = {}; const masuk = [];
  daftar.forEach((b) => {
    if (!b || typeof b !== 'object' || !/^[a-z0-9-]{1,40}$/.test(String(b.id || '')) || PT_ULANG.indexOf(b.ulang) < 0 || seen[b.id] || b.nyala === false) return; seen[b.id] = 1;
    const B = { id: String(b.id), ulang: b.ulang, tanggal: tanggalSah(b.ulang, b.tanggal) ? String(b.tanggal || '') : '', mulai: b.mulai };
    const h = Math.max(0, Math.min(120, Math.round(Number(b.hariSebelum) || 0)));
    const P = putaran(B, iso, (p) => !!(sudahPer[B.id] && sudahPer[B.id][p]), wp); if (P.tanpaTanggal || P.selesai || P.sisa > h) return;
    masuk.push({ id: B.id, nama: teks(b.nama).slice(0, 60) || B.id, sisa: P.sisa, jatuh: P.jatuh, hari: h });
  });
  masuk.sort((a, b) => a.sisa - b.sisa || a.nama.localeCompare(b.nama));
  const tepat = masuk.some((x) => x.sisa >= 0 && (x.sisa === x.hari || HARI_KIRIM.indexOf(x.sisa) >= 0)); const lewatSenin = hariMinggu === 1 && masuk.some((x) => x.sisa < 0);
  const kata = (x) => x.nama + ' ' + (x.sisa < 0 ? 'lewat ' + (-x.sisa) + ' hari' : x.sisa === 0 ? 'hari ini' : x.sisa + ' hari lagi');
  const isi = masuk.map(kata).join(' · ');
  return { kirim: masuk.length > 0 && (tepat || lewatSenin), judul: 'Kalender kepatuhan · ' + masuk.length + ' urusan', isi: isi.length > BATAS_ISI ? isi.slice(0, BATAS_ISI - 1) + '…' : isi,
    tag: 'patuh-' + iso, layar: 'menu', n: masuk.length, daftar: masuk };
}
/** Butir bawaan yang bertanggal (yang tanpa tanggal tidak pernah mengingatkan) — SAMA dengan PT_BAWAAN patuh-logika.js (dibandingkan uji). */
const BUTIR_BAWAAN = [
  { id: 'spt', nama: 'Lapor SPT Tahunan', ulang: 'tahunan', tanggal: '', hariSebelum: 30 },
  { id: 'cek-het', nama: 'Cek HET beras', ulang: 'bulanan', tanggal: '01', hariSebelum: 0 },
  { id: 'cek-qris', nama: 'Cek potongan QRIS', ulang: 'bulanan', tanggal: '01', hariSebelum: 0 },
  { id: 'cek-pajak', nama: 'Cek aturan pajak UMKM', ulang: 'bulanan', tanggal: '01', hariSebelum: 0 },
  { id: 'izin', nama: 'Izin & legalitas usaha', ulang: 'sekali', tanggal: '', hariSebelum: 60 },
  { id: 'label', nama: 'Periksa label kemasan', ulang: 'triwulan', tanggal: '01', hariSebelum: 7 },
  { id: 'tera', nama: 'Tera ulang timbangan', ulang: 'tahunan', tanggal: '', hariSebelum: 30 },
  { id: 'thr', nama: 'THR karyawan', ulang: 'sekali', tanggal: '', hariSebelum: 14 },
  { id: 'tutup', nama: 'Tutup buku akhir tahun', ulang: 'tahunan', tanggal: '12-31', hariSebelum: 14 },
];
/** Hari ini di WIB (UTC+7, tanpa musim panas) dan hari dalam minggu (0 = Minggu). */
function hariWib(d) { const t = new Date((d || new Date()).getTime() + 7 * 3600000); return { iso: t.toISOString().slice(0, 10), hari: t.getUTCDay() }; }

module.exports = { pesanPatuh, putaran, periode, tanggalSah, jatuhSiklus, hariWib, BUTIR_BAWAAN, BAWAAN, PT_MULAI, HARI_KIRIM };
