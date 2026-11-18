// PRINTER PERANGKAT INI (putaran T1 langkah 2) — satu pintu cetak struk ke printer USB: aplikasi tablet (APK, plugin CetakUsb) atau WebUSB
// peramban; kalau keduanya tidak ada, pemanggil memakai dialog cetak seperti dulu. Setelan (gaya, potong, logo) disimpan PER PERANGKAT di
// localStorage — printernya menempel di tablet, bukan di toko — dan diatur di /baru/uji-cetak.html. Tidak membaca/menulis data toko.
import { epSusun, epSusunGambar, epBase64, EP_PEKAT } from './escpos.js';
import { gambarStruk, siapkanHuruf, teksKeLogo } from './struk-kanvas.js';
import { usbAda, usbDiingat, usbKirim } from './usb-cetak.js';

export const PR_KUNCI = 'printerPerangkat';
export const PR_GAYA = [['gambar', 'gambar (huruf toko, logo, total berpita)'], ['teks', 'teks (cepat, huruf printer)']];
export const PR_BAWAAN = { gaya: 'gambar', kertas: 80, potong: 'sebagian', umpan: 4, qr: false, logo: '', aktif: true, pekat: 0 };

/** Setelan printer perangkat ini (bawaan ditimpa yang tersimpan). */
export function prAtur() {
  const a = Object.assign({}, PR_BAWAAN);
  try {
    const d = JSON.parse(localStorage.getItem(PR_KUNCI) || 'null') || {};
    if (PR_GAYA.some((x) => x[0] === d.gaya)) a.gaya = d.gaya;
    if (d.kertas === 58 || d.kertas === 80) a.kertas = d.kertas;
    if (['sebagian', 'penuh', 'tidak'].indexOf(d.potong) >= 0) a.potong = d.potong;
    if (typeof d.umpan === 'number' && d.umpan >= 0 && d.umpan <= 10) a.umpan = d.umpan;
    if (typeof d.qr === 'boolean') a.qr = d.qr;
    if (typeof d.aktif === 'boolean') a.aktif = d.aktif;
    if (typeof d.logo === 'string') a.logo = d.logo;
    if (EP_PEKAT.some((x) => x[0] === d.pekat)) a.pekat = d.pekat;
  } catch (e) { /* penyimpanan tidak bisa dibaca → bawaan */ }
  return a;
}
export function prSimpan(a) {
  try { localStorage.setItem(PR_KUNCI, JSON.stringify(Object.assign(prAtur(), a || {}))); return true; } catch (e) { return false; }
}

// ---------- aplikasi tablet (Capacitor) ----------
const cap = () => (typeof window !== 'undefined' ? window.Capacitor : null);
export const asliAda = () => { const c = cap(); return !!(c && typeof c.isNativePlatform === 'function' && c.isNativePlatform()); };
function panggilAsli(metode, isi) {
  const c = cap();
  if (c && typeof c.nativePromise === 'function') return c.nativePromise('CetakUsb', metode, isi || {});
  const p = c && c.Plugins && c.Plugins.CetakUsb; if (p && typeof p[metode] === 'function') return p[metode](isi || {});
  return Promise.reject(new Error('Plugin CetakUsb tidak ada di aplikasi ini — pasang APK terbaru'));
}
/** Daftar perangkat USB yang terlihat aplikasi (diagnosis). */
export const asliDaftar = () => panggilAsli('daftar', {});

/** Jalur cetak yang tersedia di perangkat ini: 'aplikasi' · 'peramban' (WebUSB, printer pernah diizinkan) · 'dialog'. */
export async function jalurCetak() {
  if (!prAtur().aktif) return 'dialog';
  if (asliAda()) return 'aplikasi';
  if (usbAda()) { try { const d = await usbDiingat(); if (d.length) return 'peramban'; } catch (e) { /* tidak bisa membaca */ } }
  return 'dialog';
}

/** Susun byte dari garis struk menurut setelan perangkat (atau `timpa`). Hasil: { byte, gaya, kertas, teks? (gaya teks), gambar? (gaya gambar) }. */
export async function susunCetak(garis, timpa, ekstra) {
  const a = Object.assign(prAtur(), timpa || {}); const o = Object.assign({ kertas: a.kertas, potong: a.potong, umpan: a.umpan, pekat: a.pekat }, ekstra || {});
  if (a.gaya === 'teks') { const t = epSusun(garis, o); return { byte: t.byte, teks: t.teks, gaya: 'teks', kertas: a.kertas }; }
  await siapkanHuruf();
  // owner 17 Nov (butir 3): logo perangkat sendiri menang; tanpa itu logo toko (F mahkota padi, digambar kode) bila setelan struk menyertakannya (ekstra.logoToko)
  const g = gambarStruk(garis, { kertas: a.kertas, logo: teksKeLogo(a.logo), logoToko: !!o.logoToko });
  return { byte: epSusunGambar(g, o).byte, gaya: 'gambar', kertas: a.kertas, gambar: g };
}

/** Kirim byte lewat jalur yang ada. Melempar galat berisi sebabnya (pemanggil memutuskan jatuh ke dialog cetak). */
export async function kirimCetak(byte, jalur) {
  const j = jalur || await jalurCetak();
  if (j === 'aplikasi') { const r = await panggilAsli('cetak', { data: epBase64(byte) }); return { jalur: j, byte: byte.length, perangkat: (r && r.nama) || '' }; }
  if (j === 'peramban') { const d = (await usbDiingat())[0]; const r = await usbKirim(d, byte); return { jalur: j, byte: r.byte, perangkat: d.productName || '' }; }
  throw new Error('Tidak ada printer USB di perangkat ini');
}

/** Satu langkah: garis → byte → printer. Hasil: { jalur, gaya, kertas, byte, perangkat }. */
export async function cetakGaris(garis, ekstra) {
  const j = await jalurCetak(); if (j === 'dialog') throw new Error('Tidak ada printer USB di perangkat ini');
  const s = await susunCetak(garis, null, Object.assign({ qr: '' }, ekstra || {}));
  const r = await kirimCetak(s.byte, j);
  return { jalur: j, gaya: s.gaya, kertas: s.kertas, byte: r.byte, perangkat: r.perangkat };
}
