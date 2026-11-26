// LANGIT GERBANG — owner 26 Nov 2026: "Bisa gak dibuat sesuai keadaan/kondisi sesuai jam dan cuaca real time?" … "Ya mau semua yang komplit. Buatkan yang
// mewah!" … "Gua gak mau yang murah. Tampilkan yang terbaik tapi optimal."
// Berkas ini TANPA DOM (diuji alat-uji/uji_langit_gerbang.py): dari jam + matahari terbit/terbenam + cuaca → warna langit, letak matahari & bulan, fase
// bulan, bintang, makhluk yang tampil (burung siang, kunang malam), awan, hujan, petir, kabut, kalimat cuaca. Penggambarnya js/inti/langit.js.
// Cuaca dari Open-Meteo (gratis, tanpa kunci) untuk LOKASI TOKO yang dipilih owner (Menu › Sistem › Perangkat › Atur); lokasi TIDAK ditulis di kode (repo
// publik) dan tidak memakai GPS perangkat. Tanpa lokasi / tanpa internet → langit tetap ikut jam (terbit & terbenam rata-rata Indonesia).

export const LG_KUNCI_LOKASI = 'miqbal_cuaca_lokasi_v1';   // { nama, lat, lon } — salinan setelan toko di perangkat ini (gerbang tampil SEBELUM masuk akun)
export const LG_KUNCI_CUACA = 'miqbal_cuaca_v1';           // hasil Open-Meteo terakhir (lihat lgBacaCuaca)
export const LG_UMUR_MS = 30 * 60000;                      // cuaca diambil paling sering tiap 30 menit
export const LG_TERBIT = 5 * 60 + 35;                      // menit sejak tengah malam — rata-rata Indonesia bila cuaca belum ada
export const LG_TERBENAM = 17 * 60 + 55;
const LG_SINODIK = 29.530588853; const LG_BULAN_BARU = Date.UTC(2000, 0, 6, 18, 14);

const lgJepit = (x, a, b) => Math.max(a, Math.min(b, x));
const lgBulat = (x, n) => { const p = Math.pow(10, n || 0); return Math.round(x * p) / p; };
export const lgMenit = (d) => d.getHours() * 60 + d.getMinutes() + d.getSeconds() / 60;

// ---------- palet: [atas langit, tengah, cakrawala, cahaya cakrawala] (r, g, b, a) — mode GELAP; mode terang = dicampur putih (lgCampurTerang) ----------
const LG_PALET = {
  malam:  { l1: [6, 10, 24, 1], l2: [13, 22, 44, 1], l3: [26, 36, 62, 1], cahaya: [70, 96, 160, 0.18] },
  fajar:  { l1: [24, 30, 66, 1], l2: [92, 70, 120, 1], l3: [236, 140, 108, 1], cahaya: [255, 158, 112, 0.62] },
  pagi:   { l1: [74, 128, 196, 1], l2: [142, 186, 228, 1], l3: [250, 214, 170, 1], cahaya: [255, 210, 150, 0.42] },
  siang:  { l1: [14, 96, 204, 1], l2: [58, 150, 232, 1], l3: [192, 226, 247, 1], cahaya: [255, 240, 204, 0.46] },   // tropis: biru pekat di puncak, cakrawala lembap berkabut terang
  sore:   { l1: [64, 104, 170, 1], l2: [178, 168, 170, 1], l3: [246, 196, 120, 1], cahaya: [246, 190, 104, 0.62] },
  senja:  { l1: [38, 42, 92, 1], l2: [164, 84, 96, 1], l3: [250, 146, 66, 1], cahaya: [255, 150, 60, 0.78] },
  petang: { l1: [14, 20, 52, 1], l2: [44, 46, 96, 1], l3: [128, 84, 112, 1], cahaya: [180, 110, 140, 0.32] },
};
// TAMPILAN G4 ASLI (owner 26 Nov 2026: "Yang ini jangan dihapus"): gerbang yang dikunci 29 Sep — langit = latar halaman (lapis langit tembus), pendar emas &
// biru-abu, cahaya cakrawala emas asli. Mode GELAP: petang cerah (±20–60 menit sesudah terbenam: cakrawala masih menyala, langit sudah arang). Mode TERANG:
// sore cerah ±15.30–17.00. Warnanya = nilai gerbang.css (--gm-senja1) & latar halaman (--bg1..3) apa adanya.
const LG_ASLI = { gelap: { l1: [17, 21, 22, 0], l2: [11, 13, 15, 0], l3: [9, 11, 13, 0], cahaya: [214, 146, 64, 0.46] },
  terang: { l1: [238, 241, 244, 0], l2: [226, 231, 236, 0], l3: [213, 220, 227, 0], cahaya: [246, 190, 104, 0.62] } };
/** Titik palet sepanjang hari (menit sejak tengah malam) dari terbit T & terbenam B, per mode. Di antara dua titik warnanya dicampur rata. */
export function lgTitik(T, B, mode) {
  const pagi = [[0, 'malam'], [T - 80, 'malam'], [T - 30, 'fajar'], [T + 25, 'fajar'], [T + 90, 'pagi'], [12 * 60, 'siang']];
  if (mode === 'gelap') return pagi.concat([[B - 150, 'siang'], [B - 70, 'sore'], [B - 25, 'senja'], [B - 10, 'senja'], [B + 35, 'asli'], [B + 60, 'asli'], [B + 105, 'malam'], [1440, 'malam']]);
  return pagi.concat([[B - 175, 'siang'], [B - 145, 'asli'], [B - 55, 'asli'], [B - 15, 'senja'], [B + 15, 'senja'], [B + 45, 'petang'], [B + 95, 'malam'], [1440, 'malam']]);
}
/** Warna satu titik palet untuk mode itu (mode terang = dicampur putih, kecuali tampilan asli yang dipakai apa adanya). */
function lgPalet(nama, mode) {
  if (nama === 'asli') return LG_ASLI[mode === 'gelap' ? 'gelap' : 'terang'];
  const P = LG_PALET[nama]; if (mode === 'gelap') return P;
  const o = {}; Object.keys(P).forEach((k) => { o[k] = lgCampurTerang(P[k], nama === 'malam' || nama === 'petang'); }); return o;
}
const lgCampur = (a, b, t) => a.map((x, i) => x + (b[i] - x) * t);
const lgRgba = (c) => 'rgba(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ',' + lgBulat(c[3], 3) + ')';
/** Mode terang: langit lebih muda (dicampur putih) supaya gerbang terang tetap terang. */
export const lgCampurTerang = (c, malam) => lgCampur(c, [244, 246, 250, c[3]], malam ? 0.55 : 0.4);
/** Mendung / hujan: warna ditarik ke abu kebiruan sebanyak f (0–1). */
const lgAbu = (c, f) => lgCampur(c, [112, 122, 136, c[3]], f);

// ---------- LINTASAN matahari & bulan (owner 26 Nov 2026: "Indonesia kan negara tropis. Lalu matahari sama sekali gak muncul beserta pancarannya.") ----------
// Busur lama berpuncak di TENGAH ATAS — jam 12 matahari tepat di belakang papan nama & pil jam, tak terlihat. Lintasan tropis: naik curam di kiri, siang
// tinggi di langit KANAN ATAS yang lapang, turun curam di kanan; jalurnya menghindari papan nama, cincin kunci & kotak Masuk (diukur di Mac 1918×937 dan CPad
// 1280×800 — tidak pernah tertutup dari terbit sampai terbenam). Layar TEGAK (HP, tablet berdiri: cincin di atas kotak Masuk) punya lintasan sendiri lewat pita
// langit kiri-kanan cincin; di sana matahari sempat lewat di balik papan ±10.00–11.00 (silau & pancaran tetap tampak). Titik = [bagian hari 0..1, x %, y %]
// pada hari rata-rata (terbit 05.35, terbenam 17.55); hari yang lebih panjang/pendek ikut menggeser. Di antara titik dihaluskan Catmull-Rom.
const lgJamKe = (h, m) => (h * 60 + m - LG_TERBIT) / (LG_TERBENAM - LG_TERBIT);
const LG_LINTASAN = {
  datar: [[0, 5, 66], [lgJamKe(6, 30), 8, 52], [lgJamKe(7, 15), 11, 42], [lgJamKe(8, 0), 17, 34], [lgJamKe(8, 45), 26, 31], [lgJamKe(9, 30), 36, 30], [lgJamKe(10, 15), 48, 30],
    [lgJamKe(11, 0), 61, 30], [lgJamKe(11, 30), 69, 22], [lgJamKe(12, 0), 75, 14], [lgJamKe(12, 45), 80, 12.5], [lgJamKe(13, 30), 84, 15], [lgJamKe(14, 30), 88, 21],
    [lgJamKe(15, 30), 91, 29], [lgJamKe(16, 15), 93, 36], [lgJamKe(17, 0), 94.5, 46], [1, 96, 64]],
  tegak: [[0, 5, 40], [lgJamKe(6, 45), 9, 32], [lgJamKe(8, 0), 15, 24], [lgJamKe(9, 0), 22, 19], [lgJamKe(10, 0), 40, 17], [lgJamKe(11, 0), 62, 17], [lgJamKe(11, 45), 76, 20],
    [lgJamKe(12, 30), 82, 23], [lgJamKe(14, 0), 87, 27], [lgJamKe(15, 30), 91, 31], [lgJamKe(16, 45), 94, 35], [1, 96, 40]],
};
/** Letak benda langit (x, y dalam % layar) pada bagian hari p (0 = terbit, 1 = terbenam) — tegak = layar tegak (HP / tablet berdiri). */
export function lgLintasan(p, tegak) {
  const K = LG_LINTASAN[tegak ? 'tegak' : 'datar']; const q = lgJepit(Number(p) || 0, 0, 1);
  let i = 0; while (i < K.length - 2 && q >= K[i + 1][0]) i += 1;
  const a = K[Math.max(i - 1, 0)], b = K[i], c = K[i + 1], d = K[Math.min(i + 2, K.length - 1)]; const t = (q - b[0]) / (c[0] - b[0]);
  const f = (j) => 0.5 * (2 * b[j] + (c[j] - a[j]) * t + (2 * a[j] - 5 * b[j] + 4 * c[j] - d[j]) * t * t + (3 * b[j] - a[j] - 3 * c[j] + d[j]) * t * t * t);
  return { x: lgBulat(f(1), 2), y: lgBulat(f(2), 2) };
}

/** Fase bulan 0..1 (0 = bulan baru, 0,5 = purnama) untuk saat ms. */
export function lgFaseBulan(ms) { const h = (ms - LG_BULAN_BARU) / 86400000; const f = (h % LG_SINODIK) / LG_SINODIK; return lgBulat(f < 0 ? f + 1 : f, 4); }
/** Nama fase bulan bahasa biasa. */
export function lgNamaBulan(f) { return f < 0.03 || f > 0.97 ? 'bulan baru' : f < 0.22 ? 'sabit muda' : f < 0.28 ? 'separuh' : f < 0.47 ? 'cembung' : f < 0.53 ? 'purnama' : f < 0.72 ? 'cembung' : f < 0.78 ? 'separuh' : 'sabit tua'; }

// ---------- cuaca: kode WMO (Open-Meteo) → keadaan gambar ----------
const LG_KODE = {
  0: ['cerah', 0.04, 0, 'Cerah'], 1: ['cerah', 0.22, 0, 'Cerah berawan'], 2: ['berawan', 0.5, 0, 'Berawan'], 3: ['mendung', 0.88, 0, 'Mendung'],
  45: ['kabut', 0.6, 0, 'Berkabut'], 48: ['kabut', 0.6, 0, 'Berkabut'],
  51: ['gerimis', 0.7, 1, 'Gerimis'], 53: ['gerimis', 0.75, 1, 'Gerimis'], 55: ['gerimis', 0.8, 1, 'Gerimis rapat'], 56: ['gerimis', 0.75, 1, 'Gerimis'], 57: ['gerimis', 0.8, 1, 'Gerimis rapat'],
  61: ['hujan', 0.8, 2, 'Hujan ringan'], 63: ['hujan', 0.88, 2, 'Hujan'], 65: ['lebat', 0.95, 3, 'Hujan lebat'], 66: ['hujan', 0.85, 2, 'Hujan'], 67: ['lebat', 0.95, 3, 'Hujan lebat'],
  71: ['hujan', 0.85, 2, 'Hujan'], 73: ['hujan', 0.88, 2, 'Hujan'], 75: ['lebat', 0.95, 3, 'Hujan lebat'], 77: ['gerimis', 0.8, 1, 'Gerimis'],
  80: ['hujan', 0.75, 2, 'Hujan lokal'], 81: ['hujan', 0.85, 2, 'Hujan'], 82: ['lebat', 0.95, 3, 'Hujan lebat'], 85: ['hujan', 0.85, 2, 'Hujan'], 86: ['lebat', 0.95, 3, 'Hujan lebat'],
  95: ['badai', 0.95, 3, 'Hujan petir'], 96: ['badai', 0.97, 3, 'Hujan petir'], 99: ['badai', 0.98, 3, 'Hujan petir lebat'],
};
/** Kode WMO + tutupan awan (%) → { jenis, awan 0–1, hujan 0–3, petir, kabut 0–1, teks }. Kode tak dikenal → cerah tanpa kalimat. */
export function lgCuaca(kode, awanPersen) {
  const k = LG_KODE[Number(kode)]; if (!k) return { jenis: 'cerah', awan: 0.1, hujan: 0, petir: false, kabut: 0, teks: '' };
  const awanData = Number.isFinite(Number(awanPersen)) && awanPersen !== null ? lgJepit(Number(awanPersen) / 100, 0, 1) : null;
  const awan = awanData === null ? k[1] : lgBulat(k[2] > 0 || k[0] === 'kabut' ? Math.max(k[1], awanData) : (k[1] + awanData) / 2, 3);
  return { jenis: k[0], awan, hujan: k[2], petir: k[0] === 'badai', kabut: k[0] === 'kabut' ? 1 : k[2] >= 2 ? 0.35 : 0, teks: k[3] };
}

// ---------- Open-Meteo ----------
export const LG_ASAL_CUACA = 'https://api.open-meteo.com';
export const LG_ASAL_CARI = 'https://geocoding-api.open-meteo.com';
/** Lokasi sah → { nama, lat, lon } (3 desimal ≈ 100 m: cukup untuk cuaca, tidak menunjuk rumah) atau null. */
export function lgLokasiSah(o) {
  if (!o || typeof o !== 'object') return null;
  const lat = Number(o.lat), lon = Number(o.lon); if (!Number.isFinite(lat) || !Number.isFinite(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) return null;
  return { nama: String(o.nama || '').replace(/[<>"'`]/g, '').trim().slice(0, 80), lat: lgBulat(lat, 3), lon: lgBulat(lon, 3) };
}
export function lgUrlCuaca(L) {
  const l = lgLokasiSah(L); if (!l) return '';
  return LG_ASAL_CUACA + '/v1/forecast?latitude=' + l.lat + '&longitude=' + l.lon + '&current=temperature_2m,weather_code,cloud_cover,precipitation,is_day&daily=sunrise,sunset&timezone=auto&forecast_days=1';
}
const lgMenitDariIso = (s) => { const m = /T(\d{2}):(\d{2})/.exec(String(s || '')); return m ? Number(m[1]) * 60 + Number(m[2]) : null; };
/** Jawaban Open-Meteo → { lat, lon, pada (ms diambil), kode, awan (%), hujanMm, suhu, terbit, terbenam (menit, jam setempat lokasi), tanggal } atau null. */
export function lgBacaCuaca(j, L, kiniMs) {
  const l = lgLokasiSah(L); const c = j && j.current; if (!l || !c || !Number.isFinite(Number(c.weather_code))) return null;
  const d = j.daily || {}; const terbit = lgMenitDariIso((d.sunrise || [])[0]); const terbenam = lgMenitDariIso((d.sunset || [])[0]);
  return { lat: l.lat, lon: l.lon, pada: Number(kiniMs) || 0, kode: Number(c.weather_code), awan: Number.isFinite(Number(c.cloud_cover)) ? Number(c.cloud_cover) : null,
    hujanMm: Number.isFinite(Number(c.precipitation)) ? Number(c.precipitation) : 0, suhu: Number.isFinite(Number(c.temperature_2m)) ? lgBulat(Number(c.temperature_2m), 1) : null,
    terbit: terbit !== null && terbenam !== null && terbit < terbenam ? terbit : null, terbenam: terbit !== null && terbenam !== null && terbit < terbenam ? terbenam : null,
    tanggal: String((d.time || [])[0] || '').slice(0, 10) };
}
/** Simpanan cuaca → bentuk sah (atau null). */
export function lgCuacaTersimpan(teks) {
  let o = null; try { o = typeof teks === 'string' ? JSON.parse(teks) : teks; } catch (e) { o = null; }
  if (!o || typeof o !== 'object' || !Number.isFinite(Number(o.kode)) || !Number.isFinite(Number(o.pada))) return null;
  return { lat: Number(o.lat), lon: Number(o.lon), pada: Number(o.pada), kode: Number(o.kode), awan: o.awan === null || o.awan === undefined ? null : Number(o.awan),
    hujanMm: Number(o.hujanMm) || 0, suhu: o.suhu === null || o.suhu === undefined ? null : Number(o.suhu), terbit: o.terbit === null ? null : Number(o.terbit),
    terbenam: o.terbenam === null ? null : Number(o.terbenam), tanggal: String(o.tanggal || '') };
}
/** Cuaca perlu diambil? — belum ada, lokasinya lain, atau lebih tua dari 30 menit (jam mundur = ambil lagi). */
export function lgPerluAmbil(cuaca, L, kiniMs) {
  const l = lgLokasiSah(L); if (!l) return false;
  if (!cuaca || cuaca.lat !== l.lat || cuaca.lon !== l.lon) return true;
  const umur = Number(kiniMs) - cuaca.pada; return !(umur >= 0 && umur < LG_UMUR_MS);
}
/** Cuaca masih menggambarkan keadaan sekarang? — lebih tua dari 3 jam = langit kembali ikut jam saja (kalimat cuaca tidak dipajang). */
export const lgCuacaSegar = (cuaca, kiniMs) => !!cuaca && Number(kiniMs) - cuaca.pada >= 0 && Number(kiniMs) - cuaca.pada < 3 * 3600000;
export function lgUrlCari(nama) {
  const n = String(nama || '').trim().slice(0, 60); if (n.length < 3) return '';
  return LG_ASAL_CARI + '/v1/search?name=' + encodeURIComponent(n) + '&count=6&language=id&format=json&countryCode=ID';
}
/** Hasil cari tempat → [{ nama, wilayah, lat, lon }] (paling banyak 6). */
export function lgBacaCari(j) {
  return ((j && Array.isArray(j.results)) ? j.results : []).map((r) => {
    const l = lgLokasiSah({ nama: r.name, lat: r.latitude, lon: r.longitude }); if (!l) return null;
    return Object.assign(l, { wilayah: [r.admin3, r.admin2, r.admin1].filter(Boolean).map(String).join(', ').replace(/[<>"'`]/g, '').slice(0, 120) });
  }).filter(Boolean).slice(0, 6);
}

/**
 * SUASANA (owner 26 Nov 2026: "saat ini kan sepi banget … Sesuaikan saja dengan kondisi jam dan cuaca"): makhluk yang tampil menurut jam (menit m, terbit T,
 * terbenam B) & cuaca C (lgCuaca) — seperti sawah sungguhan:
 *   fajar        bangau/kuntul melintas rendah, burung mulai, kelelawar terakhir pulang sebelum terang, kunang padam
 *   pagi         burung pipit, kupu-kupu, capung, bangau
 *   siang        elang melayang tinggi (cerah), kupu-kupu, capung, sedikit burung
 *   sore         kawanan burung pulang, capung ramai (juga saat mendung sebelum hujan), bangau pulang, kupu-kupu menjelang sore
 *   senja–petang burung terakhir, kelelawar keluar, kunang-kunang mulai
 *   malam        kunang-kunang, kelelawar, bintang jatuh sesekali (langit cerah berbintang)
 *   hujan/petir  sepi — tidak ada yang terbang (gerimis: kunang & kelelawar masih ada); kabut: hanya bangau samar di pagi hari
 * bintangTerang = terang bintang langit (bintang jatuh hanya bila langit cerah berbintang). Hasil: { burung, capung, kunang, kelelawar, kupu, elang, bangau, meteor }.
 */
export function lgSatwa(m, T, B, C, bintangTerang) {
  const R = (a, b) => m >= a && m < b; const kering = !C.hujan && !C.petir; const kabut = C.kabut >= 1; const basahRingan = C.hujan <= 1 && !C.petir;
  return {
    burung: kering && !kabut && (R(T + 10, T + 150) || R(B - 150, B + 35) || (R(T + 150, B - 150) && C.awan < 0.7)),
    capung: kering && !kabut && R(T + 90, B - 20),
    kupu: kering && !kabut && R(T + 60, B - 90) && C.awan < 0.75,
    elang: kering && !kabut && R(9 * 60, B - 120) && C.awan < 0.6,
    bangau: kering && (R(T - 10, T + 150) || (!kabut && R(B - 90, B + 10))),
    kelelawar: basahRingan && (R(B - 5, 1440) || R(0, T - 20)),
    kunang: basahRingan && (R(B + 5, 1440) || R(0, T - 30)),
    meteor: kering && bintangTerang > 0.6 && C.awan < 0.3,
  };
}

/**
 * Seluruh keadaan langit untuk saat `kini` (Date, jam perangkat), cuaca (lgCuacaTersimpan / null), mode 'terang' | 'gelap'.
 * Hasil: warna (CSS rgba), letak & terang matahari / bulan (persen layar), bintang, makhluk, awan, hujan, petir, kabut, kalimat — semua angka 0–1 dibulatkan.
 */
export function lgKeadaan(kini, cuaca, mode) {
  const ms = kini.getTime(); const segar = lgCuacaSegar(cuaca, ms);
  const T = segar && cuaca.terbit !== null ? cuaca.terbit : LG_TERBIT; const B = segar && cuaca.terbenam !== null ? cuaca.terbenam : LG_TERBENAM;
  const terang = mode !== 'gelap'; const m = lgMenit(kini); const titik = lgTitik(T, B, terang ? 'terang' : 'gelap');
  let i = 0; while (i < titik.length - 2 && m >= titik[i + 1][0]) i += 1;
  const [ma, na] = titik[i]; const [mb, nb] = titik[i + 1]; const t = mb > ma ? lgJepit((m - ma) / (mb - ma), 0, 1) : 0;
  const P = (k) => lgCampur(lgPalet(na, mode)[k], lgPalet(nb, mode)[k], t);
  const asli = (na === 'asli' ? 1 - t : 0) + (nb === 'asli' ? t : 0);   // seberapa jauh menuju tampilan G4 asli (matahari, bulan, bintang ikut mundur)
  const C = segar ? lgCuaca(cuaca.kode, cuaca.awan) : lgCuaca(null, null);
  // malam 0..1: 1 penuh sesudah petang sampai sebelum fajar
  const malam = m < T - 80 || m > B + 95 ? 1 : m < T - 30 ? (T - 30 - m) / 50 : m > B + 45 ? (m - B - 45) / 50 : 0;
  const siang = m > T + 25 && m < B - 15 ? 1 : m > T - 30 && m <= T + 25 ? (m - T + 30) / 55 : m >= B - 15 && m < B + 45 ? (B + 45 - m) / 60 : 0;
  const redup = lgJepit((C.awan - 0.35) * 1.35, 0, 0.88);   // mendung & hujan menarik warna ke abu (awan 99% ≈ langit kelabu, bukan biru)
  const warna = (k) => { let c = lgAbu(P(k), k === 'cahaya' ? redup * 0.9 : redup * 0.82); if (k === 'cahaya') c = [c[0], c[1], c[2], c[3] * (1 - redup * 0.75)];
    else if (C.petir) c = lgCampur(c, [42, 48, 62, c[3]], terang ? 0.3 : 0.42);   // badai: langit gelap batu tulis — sambaran petir menyala di atasnya
    return lgRgba(c); };
  // matahari & bulan: lintasan tropis (lgLintasan) dari terbit (kiri) ke terbenam (kanan); bulan lewat lintasan yang sama di malam hari
  const pS = (m - T) / (B - T); const sOp = pS > -0.04 && pS < 1.04 ? lgJepit(Math.min(pS + 0.04, 1.04 - pS) * 8, 0, 1) * (1 - lgJepit((C.awan - 0.2) * 1.3, 0, 0.92)) : 0;
  const panjangMalam = 1440 - (B - T); const pB = (((m - B) % 1440) + 1440) % 1440 / panjangMalam;
  const fB = lgFaseBulan(ms); const terangBulan = 0.35 + 0.65 * (1 - Math.abs(fB - 0.5) * 2);
  const bOpAsli = 1 - asli; const bOp = bOpAsli * (pB < 1.02 ? lgJepit(Math.min(pB, 1 - pB) * 10, 0, 1) * (1 - lgJepit((C.awan - 0.25) * 1.4, 0, 0.95)) * (fB < 0.03 || fB > 0.97 ? 0.15 : 1) : 0);
  const letak = (p) => { const d = lgLintasan(p, false); const g = lgLintasan(p, true); return { x: d.x, y: d.y, tx: g.x, ty: g.y }; };
  const sinarSenja = (m > T - 30 && m < T + 70) || (m > B - 90 && m < B + 20) ? 1 - redup : 0;   // berkas cahaya fajar & senja
  // TERIK (owner 26 Nov 2026: "Indonesia kan negara tropis … matahari sama sekali gak muncul beserta pancarannya"): ±10.00–14.00 matahari tinggi menyilaukan —
  // silau putih, pancaran panjang, kilau, suar lensa. Hilang bila berawan tebal / mendung / hujan / kabut, dan di tampilan G4 asli.
  const tinggi = Math.sin(Math.PI * lgJepit(pS, 0, 1));
  const terik = sOp > 0 ? lgJepit((tinggi - 0.6) / 0.3, 0, 1) * lgJepit(1 - (C.awan - 0.15) * 1.6, 0, 1) * (C.kabut ? 0.3 : 1) * (1 - asli) : 0;
  const S = lgSatwa(m, T, B, C, lgJepit(malam, 0, 1) * (1 - asli) * (1 - lgJepit((C.awan - 0.15) * 1.3, 0, 1)));
  return {
    fase: t < 0.5 ? na : nb, asli: lgBulat(asli, 3), malam: lgBulat(lgJepit(malam, 0, 1), 3), siang: lgBulat(lgJepit(siang, 0, 1), 3),
    warna: { l1: warna('l1'), l2: warna('l2'), l3: warna('l3'), cahaya: warna('cahaya') },
    surya: Object.assign(letak(pS), { op: lgBulat(sOp * (1 - asli), 3), sinar: lgBulat(lgJepit(sinarSenja, 0, 1) * (sOp > 0 ? 1 : 0) * (1 - asli), 3), hangat: lgBulat(lgJepit(1 - Math.abs(pS - 0.5) * 2, 0, 1), 3),
      terik: lgBulat(terik, 3) }),
    bulan: Object.assign(letak(pB), { op: lgBulat(bOp * terangBulan, 3), fase: fB, nama: lgNamaBulan(fB) }),
    bintang: lgBulat(lgJepit(malam, 0, 1) * (1 - asli) * (1 - lgJepit((C.awan - 0.15) * 1.3, 0, 1)), 3),
    satwa: S, burung: S.burung, kunang: S.kunang, capung: S.capung,
    awan: C.awan, mendung: lgBulat(redup, 3), hujan: C.hujan, petir: C.petir, kabut: C.kabut, jenis: C.jenis,
    teks: segar && C.teks ? (cuaca.suhu !== null ? Math.round(cuaca.suhu) + '° · ' : '') + C.teks : '',
  };
}

/**
 * SAMBARAN PETIR acak (owner 26 Nov 2026: "Untuk cuaca berpetir … coba garap"): satu jalur utama zig-zag dari atas awan ke bawah (viewBox 0 0 100 400) +
 * 1–3 cabang yang lebih pendek & tipis, tiap sambaran BEDA bentuk. acak() = 0..1 (Math.random di layar; benih tetap di uji). Hasil: { utama, cabang: [d…], ujungX }.
 */
export function lgPetirAcak(acak) {
  const r = typeof acak === 'function' ? acak : Math.random;
  const jalur = (x0, y0, panjang, lebar, langkah) => { const t = [[x0, y0]]; let x = x0, y = y0; const akhir = Math.min(400, y0 + panjang);
    while (y < akhir) { y = Math.min(akhir, y + langkah * (0.55 + r() * 0.9)); x = lgJepit(x + (r() - 0.5) * lebar, 4, 96); t.push([x, y]); } return t; };
  const d = (t) => 'M' + t.map((p) => p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' L');
  const utama = jalur(42 + r() * 16, 0, 360 + r() * 40, 26, 22);
  const cabang = []; const n = 1 + Math.floor(r() * 3);
  for (let i = 0; i < n; i++) { const a = utama[1 + Math.floor(r() * Math.max(1, utama.length - 4))]; const kiri = r() < 0.5 ? -1 : 1;
    const t = jalur(a[0], a[1], 60 + r() * 110, 22, 16).map((p, j) => [lgJepit(p[0] + kiri * j * (2 + r() * 2.5), 2, 98), p[1]]); cabang.push(d(t)); }
  return { utama: d(utama), cabang, ujungX: lgBulat(utama[utama.length - 1][0], 1) };
}

/** Pratinjau (alamat ?langitJam=19.30&langitCuaca=95): jam & kode cuaca paksaan — hanya rupa gerbang, tidak menyentuh data. null = tidak dipaksa. */
export function lgPaksa(cari) {
  const isian = (n) => { const m = new RegExp('[?&]' + n + '=([^&#]*)').exec(String(cari || '')); return m ? decodeURIComponent(m[1]) : null; };
  const j = /^(\d{1,2})[.:](\d{2})$/.exec(isian('langitJam') || ''); const k = isian('langitCuaca');
  const kode = k !== null && k !== '' && LG_KODE[Number(k)] ? Number(k) : null;
  if (!j && kode === null) return null;
  return { menit: j ? lgJepit(Number(j[1]), 0, 23) * 60 + lgJepit(Number(j[2]), 0, 59) : null, kode };
}
