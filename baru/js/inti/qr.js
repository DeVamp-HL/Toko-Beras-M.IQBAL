// qr.js — penyusun kode QR (model 2), murni hitungan: teks → kotak modul hitam/putih. Tanpa DOM, bisa diuji di jsc.
// Kenapa ada: owner 20 Nov 2026 minta QR nota pindah ke samping tanda tangan. QR bawaan printer (GS ( k) selalu jadi baris sendiri DI BAWAH
// gambar struk — itu yang menyisakan ±8 mm kertas kosong sebelum potongan. Dengan QR digambar di dalam gambar struk, struk berakhir tepat
// di hiasan bawah.
// Hanya yang dipakai toko: mode byte (huruf ASCII yang bisa dicetak), koreksi galat M (sama dengan QR bawaan printer), versi 1–6 (≤ 106 huruf).
// Lebih dari itu → null, pemanggil kembali ke QR bawaan printer.

/** versi → [jumlah blok, kata data per blok, kata koreksi per blok] untuk koreksi galat M (ISO/IEC 18004, tabel 9). */
export const QR_BLOK = { 1: [1, 16, 10], 2: [1, 28, 16], 3: [1, 44, 26], 4: [2, 32, 18], 5: [2, 43, 24], 6: [4, 27, 16] };
export const QR_VERSI_MAKS = 6;

// GF(256) dengan polinom x^8 + x^4 + x^3 + x^2 + 1 (0x11d)
const EXP = new Uint8Array(512); const LOG = new Uint8Array(256);
(() => { let x = 1; for (let i = 0; i < 255; i++) { EXP[i] = x; LOG[x] = i; x <<= 1; if (x & 0x100) x ^= 0x11d; } for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255]; })();
const kali = (a, b) => (a && b ? EXP[LOG[a] + LOG[b]] : 0);

/** Kata koreksi Reed–Solomon: `n` byte untuk larik `data`. */
export function qrKoreksi(data, n) {
  // pembangkit = ∏ (x + α^i), i = 0 … n−1; koefisien pangkat tertinggi di depan
  let g = [1];
  for (let i = 0; i < n; i++) { const b = new Array(g.length + 1).fill(0); for (let j = 0; j < g.length; j++) { b[j] ^= g[j]; b[j + 1] ^= kali(g[j], EXP[i]); } g = b; }
  const sisa = new Array(n).fill(0);
  for (let i = 0; i < data.length; i++) {
    const f = data[i] ^ sisa[0]; sisa.shift(); sisa.push(0);
    for (let j = 0; j < n; j++) sisa[j] ^= kali(g[j + 1], f);
  }
  return sisa;
}

/** Versi terkecil yang memuat `n` byte (mode byte, koreksi M); 0 = tidak muat. Kepala = 4 bit mode + 8 bit panjang → muatan = kata data − 2. */
export function qrVersi(n) {
  for (let v = 1; v <= QR_VERSI_MAKS; v++) { const b = QR_BLOK[v]; if (n >= 1 && n <= b[0] * b[1] - 2) return v; }
  return 0;
}

/** 15 bit info format untuk koreksi M (bit 00) + nomor topeng: BCH(15,5) pembangkit 0x537, lalu XOR 0x5412. */
export function qrInfoFormat(topeng) {
  const data = topeng & 7; let sisa = data;
  for (let i = 0; i < 10; i++) sisa = (sisa << 1) ^ ((sisa >> 9) * 0x537);
  return ((data << 10) | sisa) ^ 0x5412;
}

/** Delapan topeng baku; b = baris, k = kolom. */
export const QR_TOPENG = [
  (b, k) => (b + k) % 2 === 0, (b) => b % 2 === 0, (b, k) => k % 3 === 0, (b, k) => (b + k) % 3 === 0,
  (b, k) => (Math.floor(b / 2) + Math.floor(k / 3)) % 2 === 0, (b, k) => ((b * k) % 2) + ((b * k) % 3) === 0,
  (b, k) => (((b * k) % 2) + ((b * k) % 3)) % 2 === 0, (b, k) => (((b + k) % 2) + ((b * k) % 3)) % 2 === 0,
];

function kataData(byte, v) {
  const D = QR_BLOK[v][0] * QR_BLOK[v][1]; const bit = [];
  const dorong = (nilai, panjang) => { for (let i = panjang - 1; i >= 0; i--) bit.push((nilai >> i) & 1); };
  dorong(4, 4); dorong(byte.length, 8); byte.forEach((x) => dorong(x, 8));
  for (let i = 0; i < 4 && bit.length < D * 8; i++) bit.push(0);
  while (bit.length % 8) bit.push(0);
  const kata = []; for (let i = 0; i < bit.length; i += 8) { let x = 0; for (let j = 0; j < 8; j++) x = (x << 1) | bit[i + j]; kata.push(x); }
  for (let i = 0; kata.length < D; i++) kata.push(i % 2 ? 0x11 : 0xec);
  return kata;
}

/** Kata data + kata koreksi, berselang per blok (urutan yang ditaruh ke kotak). */
function kataBerselang(data, v) {
  const nb = QR_BLOK[v][0], nd = QR_BLOK[v][1], nk = QR_BLOK[v][2]; const blok = []; const kor = [];
  for (let i = 0; i < nb; i++) { const d = data.slice(i * nd, (i + 1) * nd); blok.push(d); kor.push(qrKoreksi(d, nk)); }
  const hasil = [];
  for (let j = 0; j < nd; j++) for (let i = 0; i < nb; i++) hasil.push(blok[i][j]);
  for (let j = 0; j < nk; j++) for (let i = 0; i < nb; i++) hasil.push(kor[i][j]);
  return hasil;
}

/** Nilai hukuman satu kotak (empat aturan baku) — makin kecil makin mudah dibaca pemindai. */
function hukuman(m, n) {
  let h = 0; const di = (b, k) => m[b * n + k];
  for (let arah = 0; arah < 2; arah++) for (let a = 0; a < n; a++) {
    let deret = 1; let riwayat = '';
    for (let i = 0; i < n; i++) {
      const v = arah ? di(i, a) : di(a, i); riwayat += v;
      if (i > 0) { const w = arah ? di(i - 1, a) : di(a, i - 1); if (v === w) { deret++; if (deret === 5) h += 3; else if (deret > 5) h += 1; } else deret = 1; }
    }
    // pola mirip pencari (1:1:3:1:1 dengan empat terang di salah satu sisi)
    for (let p = riwayat.indexOf('10111010000'); p >= 0; p = riwayat.indexOf('10111010000', p + 1)) h += 40;
    for (let p = riwayat.indexOf('00001011101'); p >= 0; p = riwayat.indexOf('00001011101', p + 1)) h += 40;
  }
  for (let b = 0; b < n - 1; b++) for (let k = 0; k < n - 1; k++) { const v = di(b, k); if (v === di(b, k + 1) && v === di(b + 1, k) && v === di(b + 1, k + 1)) h += 3; }
  let hitam = 0; for (let i = 0; i < m.length; i++) hitam += m[i];
  h += Math.floor(Math.abs(hitam * 20 - m.length * 10) / m.length) * 10;
  return h;
}

/**
 * Susun kode QR dari teks. Hasil { versi, modul (sisi kotak), bit: Uint8Array(modul × modul; 1 = hitam, baris demi baris), topeng },
 * atau null bila teksnya kosong, memuat huruf di luar ASCII yang bisa dicetak, atau terlalu panjang (> 106 huruf).
 * topengPaksa (0–7) hanya untuk alat uji: memaksa satu topeng supaya kedelapannya bisa diperiksa.
 */
export function qrSusun(teks, topengPaksa) {
  const s = String(teks == null ? '' : teks); const byte = [];
  for (let i = 0; i < s.length; i++) { const c = s.charCodeAt(i); if (c < 0x20 || c > 0x7e) return null; byte.push(c); }
  const v = qrVersi(byte.length); if (!v) return null;
  const n = 17 + 4 * v; const dasar = new Uint8Array(n * n); const fungsi = new Uint8Array(n * n);
  const pasang = (b, k, hitam) => { dasar[b * n + k] = hitam ? 1 : 0; fungsi[b * n + k] = 1; };
  // tiga pola pencari beserta pemisah putihnya
  const pencari = (b0, k0) => {
    for (let b = -1; b <= 7; b++) for (let k = -1; k <= 7; k++) {
      const bb = b0 + b, kk = k0 + k; if (bb < 0 || kk < 0 || bb >= n || kk >= n) continue;
      pasang(bb, kk, b >= 0 && b <= 6 && k >= 0 && k <= 6 && (b === 0 || b === 6 || k === 0 || k === 6 || (b >= 2 && b <= 4 && k >= 2 && k <= 4)));
    }
  };
  pencari(0, 0); pencari(0, n - 7); pencari(n - 7, 0);
  // pola penjajar: versi 2–6 punya satu, berpusat di (n − 7, n − 7)
  if (v >= 2) { const p = n - 7; for (let b = -2; b <= 2; b++) for (let k = -2; k <= 2; k++) pasang(p + b, p + k, Math.max(Math.abs(b), Math.abs(k)) !== 1); }
  // garis waktu
  for (let i = 8; i < n - 8; i++) { pasang(6, i, i % 2 === 0); pasang(i, 6, i % 2 === 0); }
  // tempat info format dipesan dulu (diisi sesudah topeng dipilih) + modul gelap
  for (let i = 0; i <= 8; i++) { if (!fungsi[8 * n + i]) pasang(8, i, 0); if (!fungsi[i * n + 8]) pasang(i, 8, 0); }
  for (let i = 0; i < 8; i++) { pasang(8, n - 1 - i, 0); pasang(n - 1 - i, 8, 0); }
  pasang(n - 8, 8, 1);
  // kata data berkelok dari pojok kanan bawah, dua kolom sekali jalan, melompati kolom garis waktu
  const kata = kataBerselang(kataData(byte, v), v); const aliran = [];
  kata.forEach((x) => { for (let i = 7; i >= 0; i--) aliran.push((x >> i) & 1); });
  let ke = 0; let naik = true;
  for (let kol = n - 1; kol > 0; kol -= 2) {
    if (kol === 6) kol = 5;
    for (let i = 0; i < n; i++) {
      const b = naik ? n - 1 - i : i;
      for (let j = 0; j < 2; j++) { const k = kol - j; if (fungsi[b * n + k]) continue; dasar[b * n + k] = ke < aliran.length ? aliran[ke] : 0; ke++; }
    }
    naik = !naik;
  }
  // coba delapan topeng, ambil yang hukumannya paling kecil
  let terbaik = null;
  for (let t = 0; t < 8; t++) {
    if (Number.isInteger(topengPaksa) && t !== topengPaksa) continue;
    const m = new Uint8Array(dasar);
    for (let b = 0; b < n; b++) for (let k = 0; k < n; k++) if (!fungsi[b * n + k] && QR_TOPENG[t](b, k)) m[b * n + k] ^= 1;
    const f = qrInfoFormat(t); const bitKe = (i) => (f >> i) & 1;
    // salinan pertama: mengitari pola pencari kiri atas
    for (let i = 0; i <= 5; i++) m[i * n + 8] = bitKe(i);
    m[7 * n + 8] = bitKe(6); m[8 * n + 8] = bitKe(7); m[8 * n + 7] = bitKe(8);
    for (let i = 9; i < 15; i++) m[8 * n + (14 - i)] = bitKe(i);
    // salinan kedua: bawah pola pencari kanan atas + kanan pola pencari kiri bawah
    for (let i = 0; i < 8; i++) m[8 * n + (n - 1 - i)] = bitKe(i);
    for (let i = 8; i < 15; i++) m[(n - 15 + i) * n + 8] = bitKe(i);
    m[(n - 8) * n + 8] = 1;
    const h = hukuman(m, n);
    if (!terbaik || h < terbaik.h) terbaik = { h, m, t };
  }
  return { versi: v, modul: n, bit: terbaik.m, topeng: terbaik.t };
}

// ---------- ukuran QR di gambar struk ----------
/** Sisi satu modul dalam titik printer (203 dpi: 8 titik = 1 mm): paling besar 5 (±0,6 mm), paling kecil 3 (±0,4 mm). Di bawah 3 QR tidak
 *  digambar di struk dan pemanggil mencetaknya lewat perintah QR printer seperti dulu. QR_TENANG = modul kosong yang WAJIB tersisa di
 *  kiri dan kanan QR saat menghitung muat-tidaknya. */
export const QR_TITIK_MAKS = 5;
export const QR_TITIK_MIN = 3;
export const QR_TENANG = 2;
/** Sisi modul (titik) supaya QR `modul` × `modul` muat di celah selebar `ruang` titik; 0 = tidak muat. */
export function qrTitikMuat(modul, ruang) {
  const t = Math.min(QR_TITIK_MAKS, Math.floor(ruang / (modul + 2 * QR_TENANG)));
  return t >= QR_TITIK_MIN ? t : 0;
}
