// PRINTER TABLET INI (putaran T1) — /baru/uji-cetak.html. Tidak masuk akun, tidak membaca/menulis Firestore.
// Langkah 1 (spike): membuktikan jalur cetak USB — hasil uji owner 16 Nov: WebUSB di Chrome CPad gagal mengklaim antarmuka printer NT320,
// jadi jalurnya APK (plugin CetakUsb). Langkah 2: halaman ini juga SETELAN printer perangkat ini (gaya gambar/teks, logo, potong, QR) —
// disimpan di localStorage perangkat (inti/printer.js), dipakai tombol Cetak di layar Jual.
// Paket S1 (19 Nov 2026): layar PERANGKAT — jalur cetak SDK SUNMI diuji & dipilih di sini; keadaan printer, scanner, lampu, kartu nama aplikasi.
import { epContohGaris, EP_POTONG, EP_KOLOM } from '../inti/escpos.js';
import { usbAda, usbMinta, usbDiingat, usbKirim, usbRingkas } from '../inti/usb-cetak.js';
import { siapkanLogo, logoKeTeks, teksKeLogo, siapkanHuruf, gambarStruk } from '../inti/struk-kanvas.js';
import { PR_GAYA, PR_JALUR, prAtur, prSimpan, asliAda, asliDaftar, susunCetak, kirimCetak, namaJalur } from '../inti/printer.js';
import { kemampuan, printerStatus, padaPindai, lampu, lampuPadam } from '../inti/perangkat.js';

const $ = (id) => document.getElementById(id);
let printer = null;          // WebUSB (peramban biasa)
let gambarLogo = null;       // <img> logo asli yang dipilih (untuk diproses ulang saat ukuran diubah)
let logo = '';               // logo siap cetak (teks ringkas logoKeTeks) — '' = tanpa logo

function tulisLog(teks, awas) {
  const li = document.createElement('li'); li.textContent = new Date().toLocaleTimeString('id-ID') + ' · ' + teks;
  if (awas) li.className = 'awas'; $('ucLog').insertBefore(li, $('ucLog').firstChild);
}
const pesan = (e) => (e && e.message ? e.message : String(e));

function isian() {
  return { gaya: $('ucGaya').value, kertas: Number($('ucKertas').value), potong: $('ucPotong').value, umpan: Number($('ucUmpan').value), qr: $('ucQr').checked, logo, aktif: $('ucAktif').checked, jalur: $('ucJalur').value || 'usb' };
}
function isiForm(a) {
  $('ucGaya').value = a.gaya; $('ucKertas').value = String(a.kertas); $('ucPotong').value = a.potong; $('ucUmpan').value = String(a.umpan);
  $('ucQr').checked = !!a.qr; $('ucAktif').checked = a.aktif !== false; logo = a.logo || ''; $('ucJalur').value = a.jalur || 'usb';
}

async function pratinjau() {
  const a = isian();
  $('ucLogoBaris').hidden = a.gaya !== 'gambar';
  if (a.gaya === 'gambar') {
    await siapkanHuruf();
    const g = gambarStruk(epContohGaris(), { kertas: a.kertas, logo: teksKeLogo(logo), logoToko: true });   // owner 17 Nov: contoh memakai logo toko (F mahkota padi) bila perangkat tidak punya logo sendiri
    const wadah = $('ucGambar'); wadah.textContent = ''; g.kanvas.className = 'kertas'; wadah.appendChild(g.kanvas);
    $('ucPratinjau').hidden = true; wadah.hidden = false;
  } else {
    const s = await susunCetak(epContohGaris(), a, { qr: a.qr ? 'UJI-CETAK' : '', logoToko: true });
    $('ucPratinjau').textContent = s.teks.join('\n'); $('ucPratinjau').hidden = false; $('ucGambar').hidden = true;
  }
}
async function prosesLogo() {
  if (!gambarLogo) return;
  try {
    const l = siapkanLogo(gambarLogo, { kertas: Number($('ucKertas').value), persen: Number($('ucLogoUkuran').value) / 100 });
    logo = logoKeTeks(l); tulisLog('Logo siap: ' + l.lebar + ' × ' + l.tinggi + ' titik');
  } catch (e) { tulisLog('Logo tidak bisa diproses: ' + pesan(e), true); }
  pratinjau();
}
function pilihLogo(ev) {
  const f = ev.target.files && ev.target.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = () => { const img = new Image(); img.onload = () => { gambarLogo = img; prosesLogo(); }; img.onerror = () => tulisLog('Berkas bukan gambar yang bisa dibaca', true); img.src = r.result; };
  r.readAsDataURL(f);
}

async function tampilPrinter() {
  if (asliAda()) {
    try { const r = await asliDaftar(); $('ucPrinter').textContent = JSON.stringify(r.perangkat || [], null, 2); }
    catch (e) { $('ucPrinter').textContent = 'Daftar USB tidak terbaca: ' + pesan(e); }
    $('ucCetak').disabled = false; return;
  }
  const r = usbRingkas(printer);
  $('ucPrinter').textContent = r ? JSON.stringify(r, null, 2) : 'Belum ada printer dipilih.';
  $('ucCetak').disabled = !printer;
}

async function pilih(semua) {
  try { printer = await usbMinta(semua); tulisLog('Dipilih: ' + (printer.productName || 'tanpa nama') + ' (' + usbRingkas(printer).vid + ':' + usbRingkas(printer).pid + ')'); }
  catch (e) { tulisLog('Tidak jadi memilih: ' + pesan(e), true); }
  tampilPrinter();
}

async function cetak() {
  const a = isian(); $('ucCetak').disabled = true;
  try {
    const s = await susunCetak(epContohGaris(), a, { qr: a.qr ? 'UJI-CETAK' : '', logoToko: true });
    if (asliAda()) {
      const mulaiPada = Date.now(); const r = await kirimCetak(s.byte, a.jalur === 'sunmi' ? 'sunmi' : 'aplikasi');
      tulisLog('TERCETAK lewat ' + namaJalur(r.jalur) + ' · gaya ' + s.gaya + ' · ' + r.byte + ' byte · ' + (r.perangkat || 'printer') + ' · ' + (Date.now() - mulaiPada) + ' ms' + (r.peringatan ? ' · ' + r.peringatan : ''));
      if (r.cadanganDari) tulisLog('Jalur SDK SUNMI TIDAK jalan, struk ini keluar lewat USB langsung. Sebabnya: ' + r.cadanganDari, true);
    }
    else { const r = await usbKirim(printer, s.byte); tulisLog('TERCETAK lewat peramban · gaya ' + s.gaya + ' · ' + r.byte + ' byte'); }
  } catch (e) { tulisLog(pesan(e), true); }
  tampilPrinter();
}

// ---------- paket S1: perangkat SUNMI (hanya di aplikasi tablet) ----------
async function periksaPrinter() {
  $('ucStatus').disabled = true; $('ucStatusHasil').textContent = 'Menanyakan printer…'; $('ucStatusHasil').className = '';
  try {
    const r = await printerStatus();
    // pustaka melapor "SDK Version: 1.0.16 Print SDK for Android Copyright by SUNMI" — yang perlu dibaca owner cuma nomornya
    const versi = (String(r.sdk || '').match(/\d+(?:\.\d+)+/) || [''])[0];
    $('ucStatusHasil').textContent = 'Printer ' + (r.nama || 'SUNMI') + ': ' + r.kalimat + (versi ? ' · SDK SUNMI ' + versi : '');
    $('ucStatusHasil').className = r.siap ? 'baik' : 'awas'; tulisLog('Keadaan printer (SDK SUNMI): ' + r.status + ' — ' + r.kalimat, !r.siap);
  } catch (e) { $('ucStatusHasil').textContent = 'Printer tidak bisa ditanya lewat SDK SUNMI: ' + pesan(e); $('ucStatusHasil').className = 'awas'; tulisLog('Periksa printer gagal: ' + pesan(e), true); }
  $('ucStatus').disabled = false;
}
async function cobaLampu(warna, o, nama) {
  const r = warna ? await lampu(warna, o) : await lampuPadam();
  tulisLog('Lampu ' + nama + ': ' + (r && r.ok ? 'jalan' : 'tidak jalan' + (r && r.kode !== undefined ? ' (kode ' + r.kode + ')' : '')), !(r && r.ok));
}
async function tampilSunmi() {
  const k = await kemampuan();
  const i = k.info;
  $('ucKartu').textContent = i ? (i.merek + ' ' + i.model + ' · Android ' + i.android + ' · aplikasi ' + (i.versiApk || '?') + (i.sunmi ? '' : ' · BUKAN perangkat SUNMI'))
    : 'Aplikasi ini belum punya bagian perangkat SUNMI — pasang APK terbaru (cetak USB langsung tetap jalan).';
  $('ucKartu').className = i ? 'baik' : 'awas';
  const l = k.lampu;
  $('ucLampu').textContent = !l ? 'tidak ada di aplikasi ini' : l.dukung ? 'ada' : 'tidak didukung perangkat ini (kode ' + l.kode + ')';
  const p = k.pindai;
  if (p && !p.terpasang) $('ucPindai').textContent = 'tablet ini tidak punya layanan scanner SUNMI';
  else if (!p) $('ucPindai').textContent = 'tidak ada di aplikasi ini';
  $('ucKemampuan').textContent = JSON.stringify(k, null, 2); $('ucKemampuan').hidden = false;
}

function simpan() {
  const ok = prSimpan(isian());
  tulisLog(ok ? 'Setelan tersimpan untuk perangkat ini — tombol Cetak di layar Jual memakainya' : 'Setelan TIDAK tersimpan (penyimpanan perangkat ditolak)', !ok);
}

function mulai() {
  PR_GAYA.forEach((p) => { const o = document.createElement('option'); o.value = p[0]; o.textContent = p[1]; $('ucGaya').appendChild(o); });
  EP_POTONG.forEach((p) => { const o = document.createElement('option'); o.value = p[0]; o.textContent = p[1]; $('ucPotong').appendChild(o); });
  Object.keys(EP_KOLOM).forEach((k) => { const o = document.createElement('option'); o.value = k; o.textContent = k + ' mm'; $('ucKertas').appendChild(o); });
  PR_JALUR.forEach((p) => { const o = document.createElement('option'); o.value = p[0]; o.textContent = p[1]; $('ucJalur').appendChild(o); });
  isiForm(prAtur());

  const app = asliAda();
  $('ucDukung').textContent = app ? 'Aplikasi tablet kasir — cetak langsung ke printer USB.'
    : usbAda() ? 'Peramban biasa (WebUSB). Di Sunmi CPad pakai aplikasi tablet kasir (APK).' : 'Peramban ini tidak bisa mencetak ke USB — pakai aplikasi tablet kasir (APK).';
  $('ucDukung').className = app ? 'baik' : 'awas';
  $('ucPilihBaris').hidden = app; $('ucJalurBaris').hidden = !app; $('ucPrinterSunmi').hidden = !app; $('ucSunmi').hidden = !app;
  if (app) {
    $('ucStatus').addEventListener('click', periksaPrinter);
    $('ucLampuHijau').addEventListener('click', () => cobaLampu('hijau', { batasMs: 3000 }, 'hijau'));
    $('ucLampuMerah').addEventListener('click', () => cobaLampu('merah', { kedip: true, nyalaMs: 250, matiMs: 250, batasMs: 5000 }, 'merah berkedip'));
    $('ucLampuPadam').addEventListener('click', () => cobaLampu('', null, 'padam'));
    let nPindai = 0;
    padaPindai((x) => { nPindai += 1; $('ucPindai').textContent = '"' + x.data + '" · ' + x.data.length + ' huruf · scan ke-' + nPindai; tulisLog('Scan diterima: ' + x.data); });
    tampilSunmi().catch((e) => tulisLog('Kartu perangkat tidak terbaca: ' + pesan(e), true));
  }

  $('ucPilih').addEventListener('click', () => pilih(false));
  $('ucPilihSemua').addEventListener('click', () => pilih(true));
  $('ucCetak').addEventListener('click', cetak);
  $('ucSimpan').addEventListener('click', simpan);
  $('ucLogoBerkas').addEventListener('change', pilihLogo);
  $('ucLogoUkuran').addEventListener('change', prosesLogo);
  $('ucLogoHapus').addEventListener('click', () => { gambarLogo = null; logo = ''; $('ucLogoBerkas').value = ''; tulisLog('Logo dilepas'); pratinjau(); });
  ['ucGaya', 'ucKertas', 'ucPotong', 'ucUmpan', 'ucQr'].forEach((id) => $(id).addEventListener('change', () => { if (id === 'ucKertas' && gambarLogo) prosesLogo(); else pratinjau(); }));

  if (!app && usbAda()) {
    usbDiingat().then((d) => { if (d.length) { printer = d[0]; tulisLog('Printer yang pernah diizinkan ditemukan lagi: ' + (printer.productName || 'tanpa nama')); } tampilPrinter(); });
    navigator.usb.addEventListener('disconnect', (ev) => { if (ev.device === printer) { printer = null; tulisLog('Printer dicabut', true); tampilPrinter(); } });
  }
  tampilPrinter(); pratinjau();
}
mulai();
