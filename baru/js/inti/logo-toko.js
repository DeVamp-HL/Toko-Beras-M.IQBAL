// LOGO TOKO — owner 24–26 Nov 2026: padi emas (geometri persis logo "B" papan 23 Nov) + huruf M stensil tebal miring bergaris bawah, TANPA LATAR.
// Satu sumber geometri untuk layar (monogram menu samping & gerbang), struk (kanvas) — ikon PNG dibuat apk/ikon_m.py dari geometri yang SAMA
// (alat-uji/uji_tablet_tampilan.py mencocokkan keduanya). Satuan: kotak 108 × 108 (seperti papan asli). Huruf M = garis dari huruf Stardos Stencil Bold
// (lisensi OFL), miring 0,25 seperti peramban memiringkan huruf tanpa versi miring — jadi tampil sama di mana pun tanpa memuat huruf.
// Dua warna: BATANG (tangkai, huruf, garis bawah) & BULIR. Mode terang = emas gelap (terbaca di latar putih), mode gelap = emas asli.

export const LG_BATANG = 'M38 84 C 50 66, 58 48, 70 26';
export const LG_BATANG_TEBAL = 2.4;
/** bulir: [cx, cy, rx, ry, putar°] */
export const LG_BULIR = [[62, 36, 4, 8, 30], [71, 42, 4, 8, 70], [56, 48, 4, 8, 25], [65, 55, 4, 8, 70], [50, 61, 4, 8, 20], [59, 67, 4, 8, 70], [70, 28, 3.5, 7, 35]];
export const LG_M = 'M39.05 34.73 L38.33 37.6 Q38.2 38.11 38.51 38.29 Q38.63 38.37 38.8 38.42 L38.8 38.42 Q38.96 38.46 39.1 38.56 L38.98 39 L36.17 39 L36.28 38.56 Q36.43 38.46 36.62 38.41 L36.62 38.41 Q36.8 38.37 36.96 38.29 Q37.35 38.11 37.48 37.6 L38.77 32.46 L39.05 34.73ZM39.24 31.51 Q39.2 31.24 39.17 31.04 Q39.01 31 38.84 30.96 L38.84 30.96 Q38.68 30.93 38.52 30.89 Q38.17 30.79 37.99 30.71 L38.17 29.98 L41.23 29.98 L42.18 37.18 L41.27 39 L40.18 39 L39.24 31.51ZM42.51 35.15 L45.1 29.98 L48.45 29.98 L48.33 30.46 Q48.14 30.53 47.98 30.56 L47.98 30.56 Q47.81 30.6 47.66 30.66 Q47.35 30.8 47.25 31.2 L45.6 37.79 Q45.5 38.19 45.75 38.33 Q45.86 38.39 46.01 38.43 L46.01 38.43 Q46.16 38.46 46.31 38.53 L46.2 39 L42.33 39 L42.45 38.53 Q42.64 38.46 42.81 38.43 L42.81 38.43 Q42.98 38.39 43.12 38.33 Q43.44 38.19 43.54 37.79 L45.15 31.34 L45.12 31.34 L42.66 36.26 L42.51 35.15Z';
/** garis bawah huruf M: [x0, x1, y, tebal] */
export const LG_GARIS = [33.5, 48.5, 42, 0.72];
/** kotak isi logo (satuan 108): yang tergambar ada di dalamnya — dipakai untuk memusatkan & menskala */
export const LG_KOTAK = { x0: 33.5, y0: 20.5, x1: 79, y1: 85.5 };
export const LG_WARNA = { terang: ['#7a5a2a', '#9a7a44'], gelap: ['#c9b37a', '#e6d7ad'] };

/** SVG logo tanpa latar. warna: [batang, bulir] atau null = ikut variabel CSS --logo-batang / --logo-bulir (berganti sendiri dengan mode). */
export function lgSvg(warna, kelas) {
  const k = LG_KOTAK; const b = warna ? warna[0] : 'var(--logo-batang)'; const u = warna ? warna[1] : 'var(--logo-bulir)';
  const bulir = LG_BULIR.map(([x, y, rx, ry, a]) => '<ellipse cx="' + x + '" cy="' + y + '" rx="' + rx + '" ry="' + ry + '" transform="rotate(' + a + ' ' + x + ' ' + y + ')"/>').join('');
  return '<svg' + (kelas ? ' class="' + kelas + '"' : '') + ' viewBox="' + k.x0 + ' ' + k.y0 + ' ' + (k.x1 - k.x0) + ' ' + (k.y1 - k.y0) + '" aria-hidden="true">'
    + '<path d="' + LG_BATANG + '" fill="none" stroke-width="' + LG_BATANG_TEBAL + '" stroke-linecap="round" style="stroke:' + b + '"/>'
    + '<g style="fill:' + u + '">' + bulir + '</g><path d="' + LG_M + '" style="fill:' + b + '"/>'
    + '<path d="M' + LG_GARIS[0] + ' ' + LG_GARIS[2] + 'L' + LG_GARIS[1] + ' ' + LG_GARIS[2] + '" stroke-width="' + LG_GARIS[3] + '" style="stroke:' + b + '"/></svg>';
}

/** Gambar logo di kanvas (struk): satu warna, tinggi isi h piksel, berpusat di cx, mulai dari y. Kembali: tinggi yang dipakai. */
export function lgGambarKanvas(c, cx, y, h, warna) {
  const k = LG_KOTAK; const s = h / (k.y1 - k.y0); const w = warna || '#000';
  c.save(); c.translate(cx - (k.x0 + k.x1) / 2 * s, y - k.y0 * s); c.scale(s, s); c.fillStyle = w; c.strokeStyle = w;
  c.lineCap = 'round'; c.lineWidth = LG_BATANG_TEBAL; c.stroke(new Path2D(LG_BATANG));
  for (const [x, yy, rx, ry, a] of LG_BULIR) { c.beginPath(); c.ellipse(x, yy, rx, ry, a * Math.PI / 180, 0, Math.PI * 2); c.fill(); }
  c.fill(new Path2D(LG_M));
  c.lineCap = 'butt'; c.lineWidth = LG_GARIS[3]; c.beginPath(); c.moveTo(LG_GARIS[0], LG_GARIS[2]); c.lineTo(LG_GARIS[1], LG_GARIS[2]); c.stroke();
  c.restore();
  return h;
}
