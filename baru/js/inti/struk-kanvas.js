// STRUK GAYA GAMBAR (putaran T1 langkah 2) — menggambar `garis` susunStruk() di kanvas selebar kertas cetak, lalu menjadikannya bit hitam/putih
// untuk raster ESC/POS (escpos.js epSusunGambar). Isi struk TIDAK berubah: baris, urutan, dan angkanya sama persis dengan struk teks — yang
// berubah hanya rupa. Bagian DOM (kanvas); hitungan murninya (hitam-putih, raster, buang emoji) di escpos.js & struk-model.js supaya teruji di jsc.
// Poles sesudah uji cetak owner 16 Nov: emoji dibuang, huruf isi lebih tebal (ambang 160), TOTAL tanpa pita hitam (blok hitam lebar selalu bergaris
// putih tipis di printer Sunmi — owner memilih "tanpa pita, garis tebal").
// owner 17 Nov 2026 (butir 3): gaya SERTIFIKAT + logo toko (26 Nov: padi + M stensil, logo-toko.js; dulu logo F mahkota padi) — pilihan owner dari halaman contoh. Pita guilloché atas & bawah, nama toko
// huruf pahat (Cinzel), Nota Nº (Bodoni), isian bertitik, tabel uraian, TOTAL bergaris ganda, tanda tangan yang melayani bergaya tulisan (Cormorant miring),
// cap kecil bertangkai padi. Garis yang tidak bertanda `jenis` (contoh lama) tetap digambar gaya polos di bawah.
import { EP_TITIK, epHitamPutih, epTanpaEmoji } from './escpos.js';
import { stModelSertifikat, stTebalHuruf, stAdaTandaTerima, stModelTandaTerima } from './struk-model.js';
import { qrSusun, qrTitikMuat, QR_TENANG } from './qr.js';
import { lgGambarKanvas } from './logo-toko.js';

const HURUF = 'Jost, "Helvetica Neue", Arial, sans-serif';
const F_SANS = (b, px) => b + ' ' + px + 'px Jost, "Helvetica Neue", Arial, sans-serif';
const F_CIN = (b, px) => b + ' ' + px + 'px Cinzel, "Trajan Pro", Georgia, serif';
const F_BOD = (b, px) => b + ' ' + px + 'px "Bodoni Moda", Didot, Georgia, serif';
const F_ITA = (b, px) => 'italic ' + b + ' ' + px + 'px "Cormorant Garamond", Georgia, serif';

/** Muat huruf toko sebelum menggambar (kanvas tidak menunggu sendiri). Gagal/tidak ada = pakai huruf cadangan, tidak menghentikan cetak. */
export async function siapkanHuruf() {
  if (!document.fonts || !document.fonts.load) return;
  const daftar = ['400 24px Jost', '500 24px Jost', '600 40px Jost', '700 34px Jost', '600 20px Cinzel', '700 48px Cinzel', '500 22px "Bodoni Moda"', '600 24px "Bodoni Moda"', '700 44px "Bodoni Moda"',
    'italic 500 22px "Cormorant Garamond"', 'italic 600 40px "Cormorant Garamond"'];
  try { await Promise.all(daftar.map((f) => document.fonts.load(f))); } catch (e) { /* huruf cadangan */ }
}

/** Ukuran huruf & jarak untuk 80 mm; 58 mm diperkecil sebanding. */
function ukuran(titik) {
  const k = titik / 576;
  const u = (n) => Math.round(n * k);
  return { k, tepi: u(6), kop: u(42), kecil: u(21), isi: u(25), rinci: u(22), total: u(34), totalAngka: u(40), jarak: u(8), tebal: Math.max(3, u(4)), garis: Math.max(2, u(2)) };
}

/** Pecah teks ke baris yang muat dalam `lebar` piksel (kata terlalu panjang dipotong per huruf). */
function bungkus(ctx, teks, lebar) {
  const kata = String(teks || '').split(/ +/).filter((x) => x !== ''); const hasil = []; let baris = '';
  const muat = (s) => ctx.measureText(s).width <= lebar;
  kata.forEach((k) => {
    let sisa = k;
    while (!muat(sisa)) {
      let n = sisa.length - 1; while (n > 1 && !muat(sisa.slice(0, n))) n--;
      if (baris) { hasil.push(baris); baris = ''; }
      hasil.push(sisa.slice(0, n)); sisa = sisa.slice(n);
    }
    if (!baris) baris = sisa; else if (muat(baris + ' ' + sisa)) baris += ' ' + sisa; else { hasil.push(baris); baris = sisa; }
  });
  if (baris || !hasil.length) hasil.push(baris);
  return hasil;
}

/**
 * Gambar struk. garis = susunStruk().garis (atau contoh). opsi: { kertas: 80|58, logo: { bit, lebar, tinggi } | null }.
 * Hasil: { bit, lebar, tinggi, kanvas } — kanvas = pratinjau persis (hitam/putih) yang akan keluar dari printer.
 */
export function gambarStruk(garis, opsi) {
  if (stAdaTandaTerima(garis)) return gambarTandaTerima(garis, opsi);   // owner 28 Nov 2026: tanda terima barang masuk berlogo
  if ((garis || []).some((g) => g && g.jenis)) return gambarSertifikat(garis, opsi);   // owner 17 Nov: struk nota = gaya Sertifikat
  return gambarPolos(garis, opsi);
}
/** Gaya polos lama (garis tanpa `jenis`). */
function gambarPolos(garis, opsi) {
  const o = opsi || {}; const titik = EP_TITIK[o.kertas] || EP_TITIK[80]; const U = ukuran(titik);
  const kanvas = document.createElement('canvas'); kanvas.width = titik; kanvas.height = 4000 * Math.max(1, Math.ceil((garis || []).length / 60));
  const ctx = kanvas.getContext('2d'); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, kanvas.width, kanvas.height); ctx.fillStyle = '#000'; ctx.strokeStyle = '#000';
  ctx.textBaseline = 'alphabetic';
  const kiriX = U.tepi, kananX = titik - U.tepi, lebarIsi = kananX - kiriX;
  let y = U.jarak;

  const huruf = (berat, px) => { ctx.font = berat + ' ' + px + 'px ' + HURUF; };
  const tulis = (teks, x, align, px) => { ctx.textAlign = align; ctx.fillText(teks, x, y + Math.round(px * 0.8)); };

  if (o.logo && o.logo.bit && o.logo.lebar <= titik) {
    const img = ctx.createImageData(o.logo.lebar, o.logo.tinggi);
    for (let i = 0; i < o.logo.bit.length; i++) { const v = o.logo.bit[i] ? 0 : 255; img.data[i * 4] = v; img.data[i * 4 + 1] = v; img.data[i * 4 + 2] = v; img.data[i * 4 + 3] = 255; }
    ctx.putImageData(img, Math.round((titik - o.logo.lebar) / 2), y); y += o.logo.tinggi + U.jarak * 2;
  }

  let pertama = true;
  (garis || []).forEach((g, i) => {
    if (!g) return;
    if (g.garis) {   // pemisah: garis titik-titik — dilewati tepat sebelum TOTAL (garis tebal TOTAL sudah memisahkan)
      const berikut = garis[i + 1]; if (berikut && berikut.tebal && berikut.kanan && !berikut.tengah) return;
      y += U.jarak; ctx.save(); ctx.lineWidth = U.garis; ctx.setLineDash([Math.max(3, Math.round(6 * U.k)), Math.max(3, Math.round(5 * U.k))]);
      ctx.beginPath(); ctx.moveTo(kiriX, y); ctx.lineTo(kananX, y); ctx.stroke(); ctx.restore(); y += U.jarak + U.garis; return;
    }
    const kiri = epTanpaEmoji(g.kiri); const kanan = epTanpaEmoji(g.kanan).trim();
    if (pertama && g.tebal && g.tengah) {   // kop: nama toko besar
      pertama = false; huruf(600, U.kop);
      bungkus(ctx, kiri, lebarIsi).forEach((s) => { tulis(s, titik / 2, 'center', U.kop); y += Math.round(U.kop * 1.15); }); y += Math.round(U.jarak / 2); return;
    }
    pertama = false;
    if (g.tebal && kanan) {   // TOTAL: huruf besar tebal di antara dua garis tebal (tanpa blok hitam)
      y += U.jarak; ctx.fillRect(kiriX, y, lebarIsi, U.tebal); y += U.tebal + U.jarak;
      const dasar = y + Math.round(U.totalAngka * 0.8);   // satu garis dasar untuk label & angka
      huruf(700, U.total); ctx.textAlign = 'left'; ctx.fillText(kiri, kiriX, dasar);
      huruf(700, U.totalAngka); ctx.textAlign = 'right'; ctx.fillText(kanan, kananX, dasar);
      y += Math.round(U.totalAngka * 1.05) + U.jarak; ctx.fillRect(kiriX, y, lebarIsi, U.tebal); y += U.tebal + U.jarak * 2; return;
    }
    if (g.tengah && !kanan) {
      const px = i < 4 ? U.kecil : U.isi; huruf(g.tebal ? 700 : 500, px);
      bungkus(ctx, kiri, lebarIsi).forEach((s) => { tulis(s, titik / 2, 'center', px); y += Math.round(px * 1.3); }); return;
    }
    const rinci = /^\s{2,}/.test(kiri); const px = rinci ? U.rinci : U.isi; const x0 = rinci ? kiriX + Math.round(22 * U.k) : kiriX;
    huruf(g.tebal ? 700 : 500, px);
    const lebarKanan = kanan ? ctx.measureText(kanan).width + U.jarak * 2 : 0;
    const baris = bungkus(ctx, kiri.trim(), kananX - x0 - lebarKanan);
    baris.forEach((s, j) => {
      tulis(s, x0, 'left', px);
      if (kanan && j === baris.length - 1) { huruf(g.tebal ? 700 : 600, px); tulis(kanan, kananX, 'right', px); huruf(g.tebal ? 700 : 500, px); }
      y += Math.round(px * 1.32);
    });
  });
  y += U.jarak * 2;

  return jadiBit(kanvas, ctx, titik, y);
}
/** Kanvas → bit hitam/putih (ambang 160) + pratinjau persis yang tercetak. */
function jadiBit(kanvas, ctx, titik, y) {
  const tinggi = Math.min(kanvas.height, Math.ceil(y));
  const data = ctx.getImageData(0, 0, titik, tinggi).data;
  const bit = epHitamPutih(data, titik, tinggi, { ambang: 160 });
  // pratinjau = persis yang tercetak (sesudah dijadikan hitam/putih)
  const pr = document.createElement('canvas'); pr.width = titik; pr.height = tinggi; const pc = pr.getContext('2d'); const im = pc.createImageData(titik, tinggi);
  for (let i = 0; i < bit.length; i++) { const v = bit[i] ? 0 : 255; im.data[i * 4] = v; im.data[i * 4 + 1] = v; im.data[i * 4 + 2] = v; im.data[i * 4 + 3] = 255; }
  pc.putImageData(im, 0, 0);
  return { bit, lebar: titik, tinggi, kanvas: pr };
}

// ---------- gaya SERTIFIKAT (owner 17 Nov 2026) ----------
function bez(p, t) { const u = 1 - t; return [u * u * u * p[0][0] + 3 * u * u * t * p[1][0] + 3 * u * t * t * p[2][0] + t * t * t * p[3][0], u * u * u * p[0][1] + 3 * u * u * t * p[1][1] + 3 * u * t * t * p[2][1] + t * t * t * p[3][1]]; }
function bezD(p, t) { const u = 1 - t; return [3 * u * u * (p[1][0] - p[0][0]) + 6 * u * t * (p[2][0] - p[1][0]) + 3 * t * t * (p[3][0] - p[2][0]), 3 * u * u * (p[1][1] - p[0][1]) + 6 * u * t * (p[2][1] - p[1][1]) + 3 * t * t * (p[3][1] - p[2][1])]; }
function bulir(c, x, y, rot, rx, ry) { c.save(); c.translate(x, y); c.rotate(rot); c.beginPath(); c.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2); c.fill(); c.restore(); }
/** Setangkai padi merunduk sepanjang kurva p (4 titik): batang + bulir berpasangan yang mengecil ke ujung. */
function padi(c, p, mulai, s, tebal, n) {
  const nb = n || 9;
  c.lineWidth = tebal; c.lineCap = 'round'; c.beginPath(); c.moveTo(p[0][0], p[0][1]); c.bezierCurveTo(p[1][0], p[1][1], p[2][0], p[2][1], p[3][0], p[3][1]); c.stroke();
  for (let i = 0; i <= nb; i++) {
    const t = mulai + (1 - mulai) * i / nb; const q = bez(p, t); const d = bezD(p, t); const a = Math.atan2(d[1], d[0]); const kc = 1 - 0.45 * (i / nb);
    [-1, 1].forEach((kk) => bulir(c, q[0] + Math.cos(a + kk * Math.PI / 2) * 5.5 * s * kc, q[1] + Math.sin(a + kk * Math.PI / 2) * 5.5 * s * kc, a + kk * 0.5 + Math.PI / 2, 3.4 * s * kc, 8 * s * kc));
  }
}
/** LOGO TOKO (owner 26 Nov 2026: "samakan semua") — padi emas + M stensil bergaris bawah dari logo-toko.js, hitam di kertas. Kotak tinggi h.
 *  Menggantikan logo F "mahkota padi" 17 Nov. */
export function gambarLogoToko(c, cx, y, h) { return lgGambarKanvas(c, cx, y, h, '#000'); }

/** Struk nota gaya Sertifikat. Isi dari model garis (struk-model.js); opsi: { kertas, logo (bitmap perangkat), logoToko (bool: logo F),
 *  qr (teks QR nota; digambar di antara tanda tangan dan cap bila muat) }. Hasil jadiBit + qrDiGambar (true = QR sudah ada di gambar). */
function gambarSertifikat(garis, opsi) {
  const o = opsi || {}; const W = EP_TITIK[o.kertas] || EP_TITIK[80]; const k = W / 576; const P = (n) => Math.round(n * k); const M = stModelSertifikat(garis);
  const kanvas = document.createElement('canvas'); kanvas.width = W; kanvas.height = Math.round((2600 + 120 * (M.barang.length + M.bayar.length + M.catatan.length + M.bon.length)) * k);
  const c = kanvas.getContext('2d'); c.fillStyle = '#fff'; c.fillRect(0, 0, W, kanvas.height); c.fillStyle = '#000'; c.strokeStyle = '#000'; c.textBaseline = 'alphabetic';
  const L = P(24), R = W - P(24), cx = W / 2; let y = P(8);
  const huruf = (f) => { c.font = f; };
  const lebarT = (t, f, sp) => { huruf(f); return Array.from(t).reduce((a, ch) => a + c.measureText(ch).width + (sp || 0), -(sp || 0)); };
  // owner 17 Nov (uji cetak CPad): huruf berkontras tinggi digores tepinya (stTebalHuruf) — tanpa itu garis rambut Bodoni hilang dan 44.000 terbaca 11.000
  const isiHuruf = (t, x, yb, tb) => { c.fillText(t, x, yb); if (tb) { c.save(); c.lineWidth = tb; c.lineJoin = 'round'; c.strokeText(t, x, yb); c.restore(); } };
  const tulis = (t, f, x, yb, align, sp) => {
    t = epTanpaEmoji(t); huruf(f); const tb = stTebalHuruf(f, k);
    if (!sp) { c.textAlign = align || 'left'; isiHuruf(t, x, yb, tb); return; }
    const w = lebarT(t, f, sp); let px = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x; c.textAlign = 'left';
    for (const ch of t) { isiHuruf(ch, px, yb, tb); px += c.measureText(ch).width + sp; }
  };
  const garisH = (x0, x1, yy, t) => c.fillRect(Math.round(x0), Math.round(yy), Math.round(x1 - x0), Math.max(1, Math.round(t)));
  const titik = (yy, x0, x1) => { for (let px = x0; px < x1; px += P(9)) c.fillRect(Math.round(px), Math.round(yy), Math.max(2, P(2)), Math.max(2, P(2))); };
  const guilloche = (yy, t) => {
    c.lineWidth = Math.max(1.5, 1.6 * k);
    for (let g = 0; g < 5; g++) {
      c.beginPath();
      for (let px = 0; px <= W; px += 3) { const a = px / W * Math.PI * 2; const py = yy + t / 2 + Math.sin(a * 7 + g * 0.9) * t * 0.32 + Math.sin(a * 3 - g * 0.6) * t * 0.12; if (px) c.lineTo(px, py); else c.moveTo(px, py); }
      c.stroke();
    }
    garisH(0, W, yy - 2, Math.max(2, P(3))); garisH(0, W, yy + t, Math.max(2, P(3)));
  };
  const muatLebar = (t, fBuat, px0, maks, sp) => { let px = px0; while (px > 8 && lebarT(t, fBuat(px), sp) > maks) px -= 1; return px; };

  guilloche(y, P(50)); y += P(74);
  if (o.logo && o.logo.bit && o.logo.lebar <= W) {   // logo perangkat sendiri (Printer tablet ini) menang
    const img = c.createImageData(o.logo.lebar, o.logo.tinggi);
    for (let i = 0; i < o.logo.bit.length; i++) { const v = o.logo.bit[i] ? 0 : 255; img.data[i * 4] = v; img.data[i * 4 + 1] = v; img.data[i * 4 + 2] = v; img.data[i * 4 + 3] = 255; }
    c.putImageData(img, Math.round((W - o.logo.lebar) / 2), y); y += o.logo.tinggi + P(20);
  } else if (o.logoToko) { y += gambarLogoToko(c, cx, y, P(170)) + P(20); }
  const pxBesar = muatLebar(M.kopBesar, (px) => F_CIN(700, px), P(48), R - L, P(7));
  tulis(M.kopBesar, F_CIN(700, pxBesar), cx, y + Math.round(pxBesar * 0.88), 'center', P(7)); y += Math.round(pxBesar * 1.12);
  if (M.kopKecil) { tulis(M.kopKecil, F_SANS(500, P(16)), cx, y + P(15), 'center', P(11)); y += P(28); }
  const alamat = [M.alamat, M.telp].filter(Boolean).join(' · ');
  if (alamat) {
    if (lebarT(alamat, F_SANS(500, P(17))) <= R - L) { tulis(alamat, F_SANS(500, P(17)), cx, y + P(16), 'center'); y += P(26); }
    else { if (M.alamat) { tulis(M.alamat, F_SANS(500, P(17)), cx, y + P(16), 'center'); y += P(24); } if (M.telp) { tulis('Telp ' + M.telp, F_SANS(500, P(17)), cx, y + P(16), 'center'); y += P(24); } }
  }
  y += P(14); garisH(L, R, y, Math.max(2, P(3))); garisH(L, R, y + P(7), Math.max(1.5, P(1.5))); y += P(30);
  // B2 (owner 17 Nov 2026): nota bon pelanggan usaha = FAKTUR — judul & nomornya nomor faktur (nomor nota tetap di isian, untuk dicari di Riwayat)
  if (M.faktur) { tulis('FAKTUR', F_CIN(600, P(20)), L, y + P(18), 'left', P(4)); tulis('Nº ' + M.faktur, F_BOD(700, P(26)), R, y + P(22), 'right', P(1)); y += P(40); }
  else { tulis('NOTA PEMBELIAN', F_CIN(600, P(20)), L, y + P(18), 'left', P(4)); if (M.no) tulis('Nº ' + M.no, F_BOD(700, P(30)), R, y + P(22), 'right', P(1)); y += P(40); }
  // owner 18 Nov (cetak CPad): label Jost 400 (Tanggal, Pembeli, Uraian/Jumlah, Dilayani oleh) tercetak pudar & tidak berkesan premium →
  // label jadi huruf pahat Cinzel 700 berhuruf besar renggang, sekeluarga dengan NOTA PEMBELIAN & TOTAL (digores tepi lewat stTebalHuruf)
  const F_LABEL = F_CIN(700, P(15));
  const isian = (kunci, nilai, f) => {
    if (!nilai) return; const ku = String(kunci).toUpperCase(); tulis(ku, F_LABEL, L, y + P(18), 'left', P(2)); const wk = lebarT(ku, F_LABEL, P(2)); const wv = lebarT(nilai, f);
    titik(y + P(16), L + wk + P(10), R - wv - P(10)); tulis(nilai, f, R, y + P(18), 'right'); y += P(32);
  };
  if (M.faktur && M.no) isian('Nota', M.no, F_SANS(500, P(19)));
  isian('Tanggal', M.tanggal, F_SANS(500, P(19))); isian('Pembeli', M.pembeli, F_SANS(600, P(21))); isian('Alamat', M.alamatPembeli, F_SANS(500, P(17))); isian('Jatuh tempo', M.jatuhTempo, F_SANS(600, P(19))); y += P(8);
  if (M.barang.length) {
    const atas = y; garisH(L, R, y, Math.max(2, P(2))); y += P(10);
    tulis('URAIAN', F_LABEL, L + P(10), y + P(15), 'left', P(3)); tulis('JUMLAH', F_LABEL, R - P(10), y + P(15), 'right', P(3)); y += P(26);
    garisH(L, R, y, Math.max(1.5, P(1.5))); y += P(14);
    M.barang.forEach((b, i) => {
      const wn = b.n ? lebarT(b.n, F_BOD(600, P(24))) + P(16) : 0; huruf(F_SANS(500, P(22)));
      bungkus(c, epTanpaEmoji(b.nama), R - L - P(20) - wn).forEach((t, j, arr) => { tulis(t, F_SANS(500, P(22)), L + P(10), y + P(19)); if (j === arr.length - 1 && b.n) tulis(b.n, F_BOD(600, P(24)), R - P(10), y + P(19), 'right'); y += P(27); });
      // baris rincian "2 L × 20.000" = Jost tegak (owner 18 Nov): Cormorant miring berangka gaya lama tercetak "a L × ao.ooo" di printer panas
      b.rinci.forEach((r) => {
        const wr = r.n ? lebarT(r.n, F_SANS(500, P(18))) + P(14) : 0; huruf(F_SANS(500, P(19)));
        bungkus(c, epTanpaEmoji(r.teks), R - L - P(20) - wr).forEach((t, j, arr) => { tulis(t, F_SANS(500, P(19)), L + P(10), y + P(16)); if (j === arr.length - 1 && r.n) tulis(r.n, F_SANS(500, P(18)), R - P(10), y + P(16), 'right'); y += P(24); });
      });
      y += P(6); if (i < M.barang.length - 1) { titik(y, L + P(10), R - P(10)); y += P(14); }
    });
    y += P(4); garisH(L, R, y, Math.max(1.5, P(1.5))); c.lineWidth = Math.max(1.5, P(2)); c.strokeRect(L, atas, R - L, y - atas); y += P(18);
  }
  const kolom = (label, n, fL, fN) => {
    const wn = n ? lebarT(n, fN) : 0; const wl = lebarT(label, fL); const xl = Math.max(L + P(10), Math.min(P(260), R - P(10) - wn - wl - P(20)));
    if (xl + wl > R - P(10) - wn - P(10)) { huruf(fL); bungkus(c, epTanpaEmoji(label), R - L - P(20)).forEach((t) => { tulis(t, fL, L + P(10), y + P(17)); y += P(26); }); if (n) { tulis(n, fN, R - P(10), y + P(17), 'right'); y += P(28); } return; }
    tulis(label, fL, xl, y + P(17)); if (n) tulis(n, fN, R - P(10), y + P(18), 'right'); y += P(28);
  };
  M.ringkas.forEach((r) => kolom(r.label, r.n, F_SANS(500, P(20)), F_BOD(500, P(22))));
  if (M.total) {
    y += P(8); tulis('TOTAL', F_CIN(700, P(22)), L + P(10), y + P(36), 'left', P(5));
    const pxT = muatLebar(M.total, (px) => F_BOD(700, px), P(44), R - L - P(150)); tulis(M.total, F_BOD(700, pxT), R - P(10), y + P(40), 'right');
    y += P(54); const xg = Math.min(P(260), R - P(220)); garisH(xg, R, y, Math.max(2, P(2))); garisH(xg, R, y + P(6), Math.max(2, P(2))); y += P(30);
  }
  M.bon.forEach((b) => { const f = b.tebal ? F_CIN(700, P(19)) : F_SANS(500, P(19)); huruf(f); bungkus(c, epTanpaEmoji(b.teks), R - L - P(20)).forEach((t) => { tulis(t, f, L + P(10), y + P(18), 'left', b.tebal ? P(2) : 0); y += P(28); }); });
  M.bayar.forEach((b) => kolom(b.label, b.n, F_SANS(b.tebal ? 600 : 500, P(20)), F_SANS(600, P(20))));
  M.catatan.forEach((t) => { const f = F_ITA(t.tebal ? 600 : 500, P(20)); huruf(f); bungkus(c, epTanpaEmoji(t.teks), R - L - P(20)).forEach((s) => { tulis(s, f, L + P(10), y + P(17)); y += P(25); }); });
  y += P(26);
  // QR nota di celah antara ujung garis tanda tangan dan tepi kiri cap. Lebih tinggi dari tanda tangan/cap → keduanya digeser turun supaya
  // ketiganya segaris tengah; QR sendiri mulai tepat di atas blok.
  const blokY = y; const qrKiri = L + P(236), qrKanan = R - P(86) - P(42);
  const qr = o.qr ? qrSusun(o.qr) : null; const qrT = qr ? qrTitikMuat(qr.modul, qrKanan - qrKiri) : 0; const qrSisi = qrT ? qr.modul * qrT : 0;
  const qrX = Math.round((qrKiri + qrKanan - qrSisi) / 2);
  if (qrSisi) {
    for (let b = 0; b < qr.modul; b++) for (let kk = 0; kk < qr.modul; kk++) if (qr.bit[b * qr.modul + kk]) c.fillRect(qrX + kk * qrT, blokY + b * qrT, qrT, qrT);
    y += Math.max(0, Math.round((qrSisi - P(88)) / 2));
  }
  const capX = R - P(86), capY = y; c.lineWidth = Math.max(1.5, P(2));
  c.beginPath(); c.arc(capX, capY + P(42), P(42), 0, Math.PI * 2); c.stroke(); c.beginPath(); c.arc(capX, capY + P(42), P(35), 0, Math.PI * 2); c.stroke();
  c.save(); c.beginPath(); c.arc(capX, capY + P(42), P(32), 0, Math.PI * 2); c.clip();
  padi(c, [[capX - P(6), capY + P(76)], [capX - P(4), capY + P(48)], [capX + P(2), capY + P(24)], [capX + P(16), capY + P(16)]], 0.3, 0.85 * k, Math.max(2, P(3)), 3); c.restore();   // owner 17 Nov: bulir kecil menggumpal di printer → lebih besar & lebih sedikit
  if (M.pelayan) {
    // nama panjang tidak boleh menabrak QR: hurufnya dikecilkan sampai berhenti sebelum daerah tenang QR
    const pxN = qrSisi ? muatLebar(M.pelayan, (px) => F_ITA(600, px), P(40), qrX - QR_TENANG * qrT - (L + P(36))) : P(40);
    tulis(M.pelayan, F_ITA(600, pxN), L + P(36), y + P(40)); y += P(50); garisH(L + P(16), L + P(236), y, Math.max(1.5, P(1.5))); y += P(8);
    tulis('DILAYANI OLEH', F_CIN(700, P(14)), L + P(16), y + P(16), 'left', P(2)); y += P(30);
  }
  y = Math.max(y, capY + P(92), qrSisi ? blokY + qrSisi + P(10) : 0);
  if (M.kaki) { y += P(10); huruf(F_ITA(500, P(25))); bungkus(c, epTanpaEmoji(M.kaki), R - L).forEach((t) => { tulis(t, F_ITA(500, P(25)), cx, y + P(20), 'center'); y += P(30); }); }
  y += P(16); guilloche(y, P(40)); y += P(50);
  const jadi = jadiBit(kanvas, c, W, y); jadi.qrDiGambar = !!qrSisi;
  return jadi;
}

// ---------- TANDA TERIMA BARANG MASUK (owner 28 Nov 2026: "jauh lebih rapi dan lebih profesional termasuk adakan logo") ----------
// Sekeluarga dengan nota Sertifikat (pita guilloché, logo toko, Cinzel / Bodoni / Jost), tapi bentuk DOKUMEN: judul & Nº, pita lembar, isian bertitik,
// tabel barang, nilai nota bergaris ganda, pembayaran, kotak CATATAN UNTUK PEMASOK, dua tanda tangan bergaris. Pelajaran cetak CPad 17–18 Nov dipakai
// sama: SEMUA teks lewat isiHuruf (isi + gores tepi stTebalHuruf), label Cinzel 700, angka Jost tegak / Bodoni bergores — tanpa Jost 400 dan tanpa
// Cormorant miring untuk angka. Isi & angka = model stModelTandaTerima (garis tbmGaris yang sama dengan gaya teks & WhatsApp).
function pitaGuilloche(c, W, k, yy, t) {
  c.lineWidth = Math.max(1.5, 1.6 * k);
  for (let g = 0; g < 5; g++) {
    c.beginPath();
    for (let px = 0; px <= W; px += 3) { const a = px / W * Math.PI * 2; const py = yy + t / 2 + Math.sin(a * 7 + g * 0.9) * t * 0.32 + Math.sin(a * 3 - g * 0.6) * t * 0.12; if (px) c.lineTo(px, py); else c.moveTo(px, py); }
    c.stroke();
  }
  const tb = Math.max(2, Math.round(3 * k)); c.fillRect(0, Math.round(yy - 2), W, tb); c.fillRect(0, Math.round(yy + t), W, tb);
}
function gambarTandaTerima(garis, opsi) {
  const o = opsi || {}; const W = EP_TITIK[o.kertas] || EP_TITIK[80]; const k = W / 576; const P = (n) => Math.round(n * k); const M = stModelTandaTerima(garis);
  const nCat = M.catatan.reduce((a, x) => a + 2 + x.baris.length * 2, 0);
  const kanvas = document.createElement('canvas'); kanvas.width = W;
  kanvas.height = Math.round((2600 + 190 * M.barang.length + 70 * (M.bayar.length + M.bayarKet.length * 2) + 60 * nCat) * k);
  const c = kanvas.getContext('2d'); c.fillStyle = '#fff'; c.fillRect(0, 0, W, kanvas.height); c.fillStyle = '#000'; c.strokeStyle = '#000'; c.textBaseline = 'alphabetic';
  const L = P(24), R = W - P(24), cx = W / 2; let y = P(8);
  const huruf = (f) => { c.font = f; };
  const lebarT = (t, f, sp) => { huruf(f); return Array.from(String(t)).reduce((a, ch) => a + c.measureText(ch).width + (sp || 0), -(sp || 0)); };
  const isiHuruf = (t, x, yb, tb) => { c.fillText(t, x, yb); if (tb) { c.save(); c.lineWidth = tb; c.lineJoin = 'round'; c.strokeText(t, x, yb); c.restore(); } };
  const tulis = (t, f, x, yb, align, sp) => {
    t = epTanpaEmoji(t); huruf(f); const tb = stTebalHuruf(f, k);
    if (!sp) { c.textAlign = align || 'left'; isiHuruf(t, x, yb, tb); return; }
    const w = lebarT(t, f, sp); let px = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x; c.textAlign = 'left';
    for (const ch of t) { isiHuruf(ch, px, yb, tb); px += c.measureText(ch).width + sp; }
  };
  const garisH = (x0, x1, yy, t) => c.fillRect(Math.round(x0), Math.round(yy), Math.round(x1 - x0), Math.max(1, Math.round(t)));
  const titik = (yy, x0, x1) => { for (let px = x0; px < x1; px += P(9)) c.fillRect(Math.round(px), Math.round(yy), Math.max(2, P(2)), Math.max(2, P(2))); };
  const muatLebar = (t, fBuat, px0, maks, sp) => { let px = px0; while (px > 8 && lebarT(t, fBuat(px), sp) > maks) px -= 1; return px; };
  const potong = (t, f, lebar) => { huruf(f); return bungkus(c, epTanpaEmoji(t), lebar); };
  const F_LABEL = F_CIN(700, P(15));

  // kop
  pitaGuilloche(c, W, k, y, P(40)); y += P(62);
  if (o.logo && o.logo.bit && o.logo.lebar <= W) {   // logo perangkat sendiri (Printer tablet ini) menang — sama dengan nota
    const img = c.createImageData(o.logo.lebar, o.logo.tinggi);
    for (let i = 0; i < o.logo.bit.length; i++) { const v = o.logo.bit[i] ? 0 : 255; img.data[i * 4] = v; img.data[i * 4 + 1] = v; img.data[i * 4 + 2] = v; img.data[i * 4 + 3] = 255; }
    c.putImageData(img, Math.round((W - o.logo.lebar) / 2), y); y += o.logo.tinggi + P(16);
  } else if (o.logoToko) { y += gambarLogoToko(c, cx, y, P(150)) + P(16); }
  if (M.kopBesar) { const px = muatLebar(M.kopBesar, (n) => F_CIN(700, n), P(46), R - L, P(7)); tulis(M.kopBesar, F_CIN(700, px), cx, y + Math.round(px * 0.88), 'center', P(7)); y += Math.round(px * 1.12); }
  if (M.kopKecil) { tulis(M.kopKecil, F_SANS(500, P(16)), cx, y + P(15), 'center', P(11)); y += P(28); }
  const alamat = [M.alamat, M.telp ? 'Telp ' + M.telp : ''].filter(Boolean).join(' · ');
  if (alamat) potong(alamat, F_SANS(500, P(17)), R - L).forEach((t) => { tulis(t, F_SANS(500, P(17)), cx, y + P(16), 'center'); y += P(24); });
  y += P(12); garisH(L, R, y, Math.max(2, P(3))); garisH(L, R, y + P(7), Math.max(1.5, P(1.5))); y += P(30);

  // judul, nomor, lembar
  const judul = (M.judul || 'TANDA TERIMA BARANG').toUpperCase(); const no = M.no ? 'Nº ' + M.no : '';
  const wJ = lebarT(judul, F_CIN(600, P(19)), P(3)); const wN = no ? lebarT(no, F_BOD(700, P(25)), P(1)) : 0;
  if (wJ + wN + P(16) <= R - L) { tulis(judul, F_CIN(600, P(19)), L, y + P(18), 'left', P(3)); if (no) tulis(no, F_BOD(700, P(25)), R, y + P(21), 'right', P(1)); y += P(38); }
  else { tulis(judul, F_CIN(600, P(19)), cx, y + P(18), 'center', P(3)); y += P(32); if (no) { tulis(no, F_BOD(700, P(25)), cx, y + P(21), 'center', P(1)); y += P(34); } }
  if (M.lembar) {
    const teks = M.lembar === 'toko' ? 'LEMBAR TOKO' : 'LEMBAR PEMASOK'; const f = F_CIN(700, P(17)); const w = lebarT(teks, f, P(4)) + P(40); const h = P(40);
    c.lineWidth = Math.max(2, P(2)); c.strokeRect(Math.round(cx - w / 2), Math.round(y), Math.round(w), h); c.lineWidth = Math.max(1, P(1)); c.strokeRect(Math.round(cx - w / 2 + P(5)), Math.round(y + P(5)), Math.round(w - P(10)), h - P(10));
    tulis(teks, f, cx, y + P(27), 'center', P(4)); y += h + P(18);
  }

  // isian bertitik
  const isian = (kunci, nilai, fBuat, px0) => {
    if (!nilai) return; const ku = String(kunci).toUpperCase(); const wk = lebarT(ku, F_LABEL, P(2)); const px = muatLebar(nilai, fBuat, px0, R - L - wk - P(30)); const f = fBuat(px); const wv = lebarT(nilai, f);
    tulis(ku, F_LABEL, L, y + P(18), 'left', P(2)); titik(y + P(16), L + wk + P(10), R - wv - P(10)); tulis(nilai, f, R, y + P(18), 'right'); y += P(32);
  };
  isian('Datang', M.datang, (n) => F_SANS(500, n), P(19)); isian('Dari', M.dari, (n) => F_SANS(600, n), P(21)); y += P(8);

  // tabel barang
  if (M.barang.length) {
    const atas = y; garisH(L, R, y, Math.max(2, P(2))); y += P(10);
    tulis('URAIAN', F_LABEL, L + P(10), y + P(15), 'left', P(3)); tulis('JUMLAH', F_LABEL, R - P(10), y + P(15), 'right', P(3)); y += P(26);
    garisH(L, R, y, Math.max(1.5, P(1.5))); y += P(14);
    M.barang.forEach((b, i) => {
      const fKg = F_BOD(600, P(24)); const wk = b.kg ? lebarT(b.kg, fKg) + P(16) : 0;
      potong(b.nama, F_SANS(600, P(22)), R - L - P(20) - wk).forEach((t, j, arr) => { tulis(t, F_SANS(600, P(22)), L + P(10), y + P(19)); if (j === arr.length - 1 && b.kg) tulis(b.kg, fKg, R - P(10), y + P(20), 'right'); y += P(27); });
      if (b.rinci) { tulis(b.rinci, F_SANS(500, P(19)), L + P(22), y + P(16)); y += P(24); }
      if (b.timbang) { const fT = F_SANS(600, P(19)); tulis('Hasil timbang (dibukukan)', F_SANS(500, P(19)), L + P(22), y + P(16)); tulis(b.timbang, fT, R - P(10), y + P(16), 'right'); y += P(24); }
      y += P(6); if (i < M.barang.length - 1) { titik(y, L + P(10), R - P(10)); y += P(14); }
    });
    y += P(4); garisH(L, R, y, Math.max(1.5, P(1.5))); c.lineWidth = Math.max(1.5, P(2)); c.strokeRect(L, atas, R - L, y - atas); y += P(20);
  }

  // jumlah & nilai nota
  if (M.jumlah) { const px = muatLebar(M.jumlah, (n) => F_SANS(600, n), P(19), R - L - P(150)); tulis('JUMLAH', F_LABEL, L + P(10), y + P(17), 'left', P(3)); tulis(M.jumlah, F_SANS(600, px), R - P(10), y + P(17), 'right'); y += P(32); }
  if (M.nilai) {
    tulis('NILAI NOTA', F_CIN(700, P(20)), L + P(10), y + P(34), 'left', P(4));
    const pxN = muatLebar(M.nilai, (n) => F_BOD(700, n), P(40), R - L - P(200)); tulis(M.nilai, F_BOD(700, pxN), R - P(10), y + P(38), 'right');
    y += P(50); const xg = Math.min(P(260), R - P(220)); garisH(xg, R, y, Math.max(2, P(2))); garisH(xg, R, y + P(6), Math.max(2, P(2))); y += P(26);
  }

  // pembayaran
  M.bayar.forEach((b) => {
    const fL = F_SANS(b.tebal ? 600 : 500, P(20)); const fN = F_SANS(600, P(20)); const kosong = /^\.+$/.test(b.n);
    const label = b.label.replace(/:\s*Rp$/, ''); const wn = kosong ? P(150) : b.n ? lebarT(b.n, fN) : 0;
    const baris = potong(label, fL, R - L - P(30) - wn);
    baris.forEach((t, j) => { tulis(t, fL, L + P(10), y + P(17)); if (j === baris.length - 1) {
      if (kosong) { tulis('Rp', fN, R - P(150), y + P(17), 'left'); titik(y + P(15), R - P(150) + lebarT('Rp', fN) + P(8), R - P(10)); }
      else if (b.n) tulis(b.n, fN, R - P(10), y + P(17), 'right'); } y += P(28); });
  });
  M.bayarKet.forEach((t) => potong(t, F_SANS(500, P(17)), R - L - P(20)).forEach((s) => { tulis(s, F_SANS(500, P(17)), L + P(10), y + P(15)); y += P(23); }));
  if (M.keadaan) { y += P(4); potong(M.keadaan, F_SANS(500, P(16)), R - L - P(20)).forEach((s) => { tulis(s, F_SANS(500, P(16)), L + P(10), y + P(14)); y += P(22); }); }

  // catatan untuk pemasok
  if (M.catatan.length) {
    y += P(16); const atas = y; y += P(12);
    tulis('CATATAN UNTUK PEMASOK', F_CIN(700, P(16)), cx, y + P(16), 'center', P(3)); y += P(28); garisH(L + P(14), R - P(14), y, Math.max(1.5, P(1.5))); y += P(12);
    M.catatan.forEach((kel, i) => {
      if (i) y += P(6);
      if (kel.judul) { tulis(kel.judul.toUpperCase(), F_CIN(700, P(13)), L + P(14), y + P(14), 'left', P(2)); y += P(24); }
      kel.baris.forEach((x) => {
        const fN = F_SANS(600, P(18)); const wn = x.n ? lebarT(x.n, fN) + P(14) : 0; const f = F_SANS(x.tebal ? 600 : 500, P(18));
        const baris = potong(x.teks, f, R - L - P(42) - wn);
        baris.forEach((t, j) => { if (j === 0) c.fillRect(L + P(14), y + P(8), Math.max(3, P(5)), Math.max(3, P(5))); tulis(t, f, L + P(26), y + P(15), 'left'); if (j === baris.length - 1 && x.n) tulis(x.n, fN, R - P(14), y + P(15), 'right'); y += P(24); });
      });
    });
    y += P(10); c.lineWidth = Math.max(1.5, P(2)); c.strokeRect(L, atas, R - L, y - atas); y += P(10);
  }

  // tanda tangan
  if (M.ttd) {
    y += P(26); const kol = [L + (R - L) / 4, L + (R - L) * 3 / 4]; const lebarKol = (R - L) / 2 - P(24);
    [M.ttd.kiri, M.ttd.kanan].forEach((t, i) => { const teks = String(t || '').replace(/,\s*$/, '').toUpperCase(); const px = muatLebar(teks, (n) => F_CIN(700, n), P(14), lebarKol, P(2)); tulis(teks, F_CIN(700, px), kol[i], y + P(14), 'center', P(2)); });
    y += P(100); kol.forEach((x) => garisH(x - lebarKol / 2, x + lebarKol / 2, y, Math.max(1.5, P(1.5)))); y += P(8);
    kol.forEach((x) => tulis('nama & paraf', F_SANS(500, P(14)), x, y + P(14), 'center')); y += P(28);
    if (M.namaSupir) { y += P(10); tulis('NAMA TERANG SUPIR & JAM', F_CIN(700, P(13)), L, y + P(14), 'left', P(2)); y += P(62); garisH(L, R, y, Math.max(1.5, P(1.5))); y += P(16); }
  }
  if (M.kaki) { y += P(10); potong(M.kaki, F_ITA(600, P(23)), R - L).forEach((t) => { tulis(t, F_ITA(600, P(23)), cx, y + P(19), 'center'); y += P(28); }); }
  y += P(16); pitaGuilloche(c, W, k, y, P(36)); y += P(46);
  return jadiBit(kanvas, c, W, y);
}

/**
 * Siapkan logo dari berkas gambar (PNG/JPG/SVG): diperkecil muat maks. lebar × tinggiMaks, latar transparan = putih, dijadikan titik hitam/putih
 * dengan dithering (gradasi tetap terbaca di printer panas). Hasil: { bit, lebar, tinggi } — bisa disimpan (logoKeTeks) dan dipakai gambarStruk.
 */
export function siapkanLogo(img, opsi) {
  const o = opsi || {}; const titik = EP_TITIK[o.kertas] || EP_TITIK[80];
  const lebarMaks = Math.round(titik * (o.persen || 0.6)); const tinggiMaks = Math.round(o.tinggiMaks || 200 * titik / 576);
  const sw = img.naturalWidth || img.width, sh = img.naturalHeight || img.height; if (!sw || !sh) throw new Error('Gambar logo kosong');
  const s = Math.min(lebarMaks / sw, tinggiMaks / sh);   // logo kecil ikut diperbesar sampai batas
  const lebar = Math.max(8, Math.round(sw * s)), tinggi = Math.max(8, Math.round(sh * s));
  const c = document.createElement('canvas'); c.width = lebar; c.height = tinggi; const x = c.getContext('2d');
  x.fillStyle = '#fff'; x.fillRect(0, 0, lebar, tinggi); x.imageSmoothingQuality = 'high'; x.drawImage(img, 0, 0, lebar, tinggi);
  const bit = epHitamPutih(x.getImageData(0, 0, lebar, tinggi).data, lebar, tinggi, { dither: o.dither !== false });
  return { bit, lebar, tinggi };
}

/** Logo ⇄ teks ringkas (disimpan per perangkat): "lebar,tinggi,base64 bit-terpadat". */
export function logoKeTeks(l) {
  const n = l.bit.length; const p = new Uint8Array(Math.ceil(n / 8));
  for (let i = 0; i < n; i++) if (l.bit[i]) p[i >> 3] |= 0x80 >> (i & 7);
  let s = ''; for (let i = 0; i < p.length; i += 32768) s += String.fromCharCode.apply(null, Array.prototype.slice.call(p.subarray(i, i + 32768)));
  return l.lebar + ',' + l.tinggi + ',' + btoa(s);
}
export function teksKeLogo(t) {
  const m = /^(\d+),(\d+),([A-Za-z0-9+/=]+)$/.exec(String(t || '')); if (!m) return null;
  const lebar = Number(m[1]), tinggi = Number(m[2]); const b = atob(m[3]); const bit = new Uint8Array(lebar * tinggi);
  for (let i = 0; i < bit.length; i++) bit[i] = (b.charCodeAt(i >> 3) >> (7 - (i & 7))) & 1;
  return { bit, lebar, tinggi };
}
