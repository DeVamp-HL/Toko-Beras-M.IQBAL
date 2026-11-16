// STRUK GAYA GAMBAR (putaran T1 langkah 2) — menggambar `garis` susunStruk() di kanvas selebar kertas cetak, lalu menjadikannya bit hitam/putih
// untuk raster ESC/POS (escpos.js epSusunGambar). Isi struk TIDAK berubah: baris, urutan, dan angkanya sama persis dengan struk teks — yang
// berubah hanya rupa: huruf toko (Jost), kop besar, rincian barang menjorok, TOTAL besar di antara dua garis tebal, garis titik-titik, logo.
// Bagian DOM (kanvas); hitungan murninya (hitam-putih, raster, buang emoji) di escpos.js supaya teruji di jsc.
// Poles sesudah uji cetak owner 16 Nov: emoji dibuang (tadinya jadi bintik acak), huruf isi lebih tebal (500, ambang 160). TOTAL tidak lagi
// di pita hitam: blok hitam lebar selalu bergaris putih tipis di printer Sunmi (pekat maupun dijarangkan) — owner memilih "tanpa pita, garis tebal".
import { EP_TITIK, epHitamPutih, epTanpaEmoji } from './escpos.js';

const HURUF = 'Jost, "Helvetica Neue", Arial, sans-serif';

/** Muat huruf toko sebelum menggambar (kanvas tidak menunggu sendiri). Gagal/tidak ada = pakai huruf cadangan, tidak menghentikan cetak. */
export async function siapkanHuruf() {
  if (!document.fonts || !document.fonts.load) return;
  try { await Promise.all(['400 24px Jost', '500 24px Jost', '600 40px Jost', '700 34px Jost'].map((f) => document.fonts.load(f))); } catch (e) { /* huruf cadangan */ }
}

// owner 17 Nov 2026 (butir 3): LOGO TOKO bersama — berkas baru/logo-struk.svg (hitam-putih, pilihan owner) ikut terbit & ikut salinan aplikasi tablet.
// Dipakai bila setelan struk "logo toko" menyala (aturanToko/struk sertakan.logo) dan perangkat tidak punya logo sendiri (Printer tablet ini).
// Berkas tidak ada / gagal dimuat = tanpa logo (struk tetap keluar). Hasil disimpan per lebar kertas.
export const LOGO_TOKO = new URL('../../logo-struk.svg', import.meta.url).href;
const _logoToko = {};
export function logoToko(kertas) {
  const k = kertas === 58 ? 58 : 80; if (_logoToko[k]) return _logoToko[k];
  _logoToko[k] = new Promise((jadi) => {
    try { const img = new Image(); img.onload = () => { try { jadi(siapkanLogo(img, { kertas: k, persen: 0.42, tinggiMaks: Math.round(150 * (EP_TITIK[k] || 576) / 576), dither: false })); } catch (e) { jadi(null); } };
      img.onerror = () => { delete _logoToko[k]; jadi(null); }; img.src = LOGO_TOKO; } catch (e) { delete _logoToko[k]; jadi(null); }
  });
  return _logoToko[k];
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

  const tinggi = Math.min(kanvas.height, Math.ceil(y));
  const data = ctx.getImageData(0, 0, titik, tinggi).data;
  const bit = epHitamPutih(data, titik, tinggi, { ambang: 160 });
  // pratinjau = persis yang tercetak (sesudah dijadikan hitam/putih)
  const pr = document.createElement('canvas'); pr.width = titik; pr.height = tinggi; const pc = pr.getContext('2d'); const im = pc.createImageData(titik, tinggi);
  for (let i = 0; i < bit.length; i++) { const v = bit[i] ? 0 : 255; im.data[i * 4] = v; im.data[i * 4 + 1] = v; im.data[i * 4 + 2] = v; im.data[i * 4 + 3] = 255; }
  pc.putImageData(im, 0, 0);
  return { bit, lebar: titik, tinggi, kanvas: pr };
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
