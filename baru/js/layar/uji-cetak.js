// HALAMAN UJI CETAK (putaran T1, spike) — dibuka owner di Sunmi CPad: /baru/uji-cetak.html. Tidak masuk akun, tidak membaca/menulis Firestore.
// Tujuannya satu: membuktikan apakah Chrome di CPad bisa mencetak ke printer 80 mm lewat USB stand (WebUSB). Hasil diagnosis (VID/PID,
// antarmuka, langkah yang gagal) disalin owner ke putaran berikut: lolos → tablet kasir tetap PWA; gagal di klaim antarmuka → bungkus APK.
import { epSusun, epContohGaris, EP_POTONG, EP_KOLOM } from '../inti/escpos.js';
import { usbAda, usbMinta, usbDiingat, usbKirim, usbRingkas } from '../inti/usb-cetak.js';

const $ = (id) => document.getElementById(id);
let printer = null;

function tulisLog(teks, awas) {
  const li = document.createElement('li'); li.textContent = new Date().toLocaleTimeString('id-ID') + ' · ' + teks;
  if (awas) li.className = 'awas'; $('ucLog').insertBefore(li, $('ucLog').firstChild);
}
function tampilPrinter() {
  const r = usbRingkas(printer);
  $('ucPrinter').textContent = r ? JSON.stringify(r, null, 2) : 'Belum ada printer dipilih.';
  $('ucCetak').disabled = !printer;
}
function opsi() {
  return { kertas: Number($('ucKertas').value), potong: $('ucPotong').value, umpan: Number($('ucUmpan').value), qr: $('ucQr').checked ? 'UJI-CETAK-T1' : '' };
}
function pratinjau() { $('ucPratinjau').textContent = epSusun(epContohGaris(), opsi()).teks.join('\n'); }

async function pilih(semua) {
  try { printer = await usbMinta(semua); tulisLog('Dipilih: ' + (printer.productName || 'tanpa nama') + ' (' + usbRingkas(printer).vid + ':' + usbRingkas(printer).pid + ')'); }
  catch (e) { tulisLog('Tidak jadi memilih: ' + (e && e.message ? e.message : e), true); }
  tampilPrinter();
}
async function cetak() {
  const s = epSusun(epContohGaris(), opsi());
  try { const r = await usbKirim(printer, s.byte); tulisLog('TERCETAK · ' + r.byte + ' byte lewat antarmuka ' + r.jalur.antarmuka + ' (kelas ' + r.jalur.kelas + '), endpoint ' + r.jalur.endpoint); }
  catch (e) { tulisLog(e && e.message ? e.message : String(e), true); }
  tampilPrinter();
}

function mulai() {
  EP_POTONG.forEach((p) => { const o = document.createElement('option'); o.value = p[0]; o.textContent = p[1]; $('ucPotong').appendChild(o); });
  Object.keys(EP_KOLOM).forEach((k) => { const o = document.createElement('option'); o.value = k; o.textContent = k + ' mm (' + EP_KOLOM[k] + ' kolom)'; if (k === '80') o.selected = true; $('ucKertas').appendChild(o); });
  $('ucDukung').textContent = usbAda() ? 'WebUSB ADA di peramban ini.' : 'WebUSB TIDAK ADA — buka halaman ini di Chrome (https). Kalau Chrome di CPad pun tidak punya, jalannya APK.';
  $('ucDukung').className = usbAda() ? 'baik' : 'awas';
  $('ucPilih').addEventListener('click', () => pilih(false));
  $('ucPilihSemua').addEventListener('click', () => pilih(true));
  $('ucCetak').addEventListener('click', cetak);
  ['ucKertas', 'ucPotong', 'ucUmpan', 'ucQr'].forEach((id) => $(id).addEventListener('change', pratinjau));
  if (usbAda()) {
    usbDiingat().then((d) => { if (d.length) { printer = d[0]; tulisLog('Printer yang pernah diizinkan ditemukan lagi: ' + (printer.productName || 'tanpa nama')); } tampilPrinter(); });
    navigator.usb.addEventListener('disconnect', (ev) => { if (ev.device === printer) { printer = null; tulisLog('Printer dicabut', true); tampilPrinter(); } });
  }
  tampilPrinter(); pratinjau();
}
mulai();
