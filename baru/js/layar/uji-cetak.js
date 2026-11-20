// PRINTER TABLET INI (putaran T1) — /baru/uji-cetak.html. Tidak masuk akun, tidak membaca/menulis Firestore.
// Langkah 1 (spike): membuktikan jalur cetak USB — hasil uji owner 16 Nov: WebUSB di Chrome CPad gagal mengklaim antarmuka printer NT320,
// jadi jalurnya APK (plugin CetakUsb). Langkah 2: halaman ini juga SETELAN printer perangkat ini (gaya gambar/teks, logo, potong, QR) —
// disimpan di localStorage perangkat (inti/printer.js), dipakai tombol Cetak di layar Jual.
// Paket S1 (19 Nov 2026): layar PERANGKAT — jalur cetak SDK SUNMI diuji & dipilih di sini; keadaan printer, scanner, lampu, kartu nama aplikasi.
// Paket S4 (19 Nov 2026): printer lewat Bluetooth, mode kertas printer, label barang (contoh), lampu berwarna per kejadian, sidik jari (periksa sensor).
import { epContohGaris, EP_POTONG, EP_KOLOM } from '../inti/escpos.js';
import { usbAda, usbMinta, usbDiingat, usbKirim, usbRingkas } from '../inti/usb-cetak.js';
import { siapkanLogo, logoKeTeks, teksKeLogo, siapkanHuruf, gambarStruk } from '../inti/struk-kanvas.js';
import { PR_GAYA, PR_JALUR, PR_LABEL_CARA, prAtur, prSimpan, asliAda, asliDaftar, susunCetak, kirimCetak, namaJalur, susunLabel, cetakLabel } from '../inti/printer.js';
import { kemampuan, printerStatus, padaPindai, padaTempel, lampuPadam, lewatJalur, printerBt, printerMode, printerSetelMode, MODE_KERTAS, kalimatModeKertas,
  LAMPU_KEJADIAN, LAMPU_WARNA, LAMPU_MATI, lampuAtur, lampuSimpan, lampuKejadian, sidikJariInfo, sidikJariUji, sidikJariTolak, hasilTakDiketahui, masihMencetak } from '../inti/perangkat.js';

const $ = (id) => document.getElementById(id);
let printer = null;          // WebUSB (peramban biasa)
let gambarLogo = null;       // <img> logo asli yang dipilih (untuk diproses ulang saat ukuran diubah)
let logo = '';               // logo siap cetak (teks ringkas logoKeTeks) — '' = tanpa logo

function tulisLog(teks, awas) {
  const li = document.createElement('li'); li.textContent = new Date().toLocaleTimeString('id-ID') + ' · ' + teks;
  if (awas) li.className = 'awas'; $('ucLog').insertBefore(li, $('ucLog').firstChild);
}
const pesan = (e) => (e && e.message ? e.message : String(e));
// baris catatan untuk cetak yang gagal: kalimatnya, kabar asli aplikasi bila kalimatnya diganti (printer diam), dan lamanya — ±1 detik =
// kiriman ditolak sambungan, ±40 detik = pustaka SUNMI menunggu jawaban printer sampai menyerah (uji owner 20 Nov 2026)
const pesanGagal = (e, mulaiPada) => pesan(e) + (e && e.asli ? ' · kabar aslinya: "' + e.asli + '"' : '') + (mulaiPada ? ' · ' + (Date.now() - mulaiPada) + ' ms' : '');

function isian() {
  return { gaya: $('ucGaya').value, kertas: Number($('ucKertas').value), potong: $('ucPotong').value, umpan: Number($('ucUmpan').value), qr: $('ucQr').checked, logo, aktif: $('ucAktif').checked, jalur: $('ucJalur').value || 'usb', btPotong: $('ucBtPotong').checked,
    labelCara: $('ucLabelCara').value || 'struk', labelLebar: Number($('ucLabelLebar').value), labelTinggi: Number($('ucLabelTinggi').value), labelCelah: Number($('ucLabelCelah').value), labelPotong: $('ucLabelPotong').checked };
}
function isiForm(a) {
  $('ucGaya').value = a.gaya; $('ucKertas').value = String(a.kertas); $('ucPotong').value = a.potong; $('ucUmpan').value = String(a.umpan);
  $('ucQr').checked = !!a.qr; $('ucAktif').checked = a.aktif !== false; logo = a.logo || ''; $('ucJalur').value = a.jalur || 'usb'; $('ucBtPotong').checked = !!a.btPotong;
  $('ucLabelCara').value = a.labelCara; $('ucLabelLebar').value = String(a.labelLebar); $('ucLabelTinggi').value = String(a.labelTinggi); $('ucLabelCelah').value = String(a.labelCelah); $('ucLabelPotong').checked = a.labelPotong !== false;
}
/** Jalur SDK yang sedang dipilih di formulir → cara menyambung printer ('bt' | 'usb') untuk tombol Periksa printer & mode kertas. */
const lewatKini = () => lewatJalur($('ucJalur').value);

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

// Keadaan printer dalam satu potong kalimat untuk catatan: jawaban printer, atau kenapa ia tidak bisa ditanya.
const keadaanSingkat = (lewat) => printerStatus(lewat).then((r) => '"' + r.kalimat + '"', (e) => 'tidak bisa ditanya (' + pesan(e) + ')');
async function cetak() {
  const a = isian(); $('ucCetak').disabled = true; let mulaiPada = Date.now();
  const sdk = asliAda() && (a.jalur === 'sunmi' || a.jalur === 'sunmi-bt'); let sebelum = ''; let ukuran = '';
  try {
    const s = await susunCetak(epContohGaris(), a, { qr: a.qr ? 'UJI-CETAK' : '', logoToko: true });
    // baris yang gagal ikut menyebut gaya dan besar kirimannya: printer diam yang tercatat sejauh ini semuanya struk bergambar ±84 ribu byte
    ukuran = ' · gaya ' + s.gaya + ' · ' + s.byte.length + ' byte';
    if (asliAda()) {
      // uji owner 20 Nov 2026 malam: printer diam 2 dari 4 cetak contoh dan belum diketahui kenapa. Jawaban printer SEBELUM cetak disimpan,
      // dan kalau ia diam, ditanya lagi SESUDAHNYA — dua jawaban itu yang membedakan "printer menahan cetakan" dari "printer tidak mendengar".
      if (sdk) sebelum = await keadaanSingkat(lewatJalur(a.jalur));
      // percobaan "kirim per potong": hanya jalur Bluetooth + gaya gambar (gaya teks tidak punya batas potong); isian di layar yang dipakai, belum tentu tersimpan
      const batas = a.jalur === 'sunmi-bt' && a.btPotong ? s.batas : null;
      if (batas && batas.length) ukuran += ' · dikirim per potong (' + (batas.length + 1) + ')';
      mulaiPada = Date.now(); const r = await kirimCetak(s.byte, a.jalur === 'sunmi' || a.jalur === 'sunmi-bt' ? a.jalur : 'aplikasi', batas);
      tulisLog('TERCETAK lewat ' + namaJalur(r.jalur) + ' · gaya ' + s.gaya + ' · ' + r.byte + ' byte' + (r.potong > 1 ? ' dalam ' + r.potong + ' potong' : '') + ' · ' + (r.perangkat || 'printer') + ' · ' + (Date.now() - mulaiPada) + ' ms' + (r.peringatan ? ' · ' + r.peringatan : ''));
      if (r.cadanganDari) tulisLog('Jalur SDK SUNMI TIDAK jalan, struk ini keluar lewat USB langsung. Sebabnya: ' + r.cadanganDari, true);
    }
    else { const r = await usbKirim(printer, s.byte); tulisLog('TERCETAK lewat peramban · gaya ' + s.gaya + ' · ' + r.byte + ' byte'); }
  } catch (e) {
    tulisLog(pesanGagal(e, mulaiPada) + ukuran, true);
    if (sdk && hasilTakDiketahui(e)) tulisLog('Keadaan printer sebelum cetak itu: ' + sebelum + ' · sesudahnya: ' + await keadaanSingkat(lewatJalur(a.jalur)), true);
  }
  tampilPrinter();
}

// ---------- paket S1: perangkat SUNMI (hanya di aplikasi tablet) ----------
async function periksaPrinter() {
  $('ucStatus').disabled = true; $('ucStatusHasil').textContent = 'Menanyakan printer…'; $('ucStatusHasil').className = '';
  try {
    const r = await printerStatus(lewatKini());
    // pustaka melapor "SDK Version: 1.0.16 Print SDK for Android Copyright by SUNMI" — yang perlu dibaca owner cuma nomornya
    const versi = (String(r.sdk || '').match(/\d+(?:\.\d+)+/) || [''])[0];
    $('ucStatusHasil').textContent = 'Printer ' + (r.nama || 'SUNMI') + ': ' + r.kalimat + (versi ? ' · SDK SUNMI ' + versi : '');
    $('ucStatusHasil').className = r.siap ? 'baik' : 'awas'; tulisLog('Keadaan printer (SDK SUNMI): ' + r.status + ' — ' + r.kalimat, !r.siap);
  } catch (e) { $('ucStatusHasil').textContent = 'Printer tidak bisa ditanya lewat SDK SUNMI: ' + pesan(e); $('ucStatusHasil').className = 'awas'; tulisLog('Periksa printer gagal: ' + pesan(e), true); }
  $('ucStatus').disabled = false;
}
// ---------- paket S4: Bluetooth, mode kertas, label ----------
async function periksaBt() {
  $('ucBt').disabled = true; $('ucBtHasil').textContent = 'Menanyakan Bluetooth tablet…'; $('ucBtHasil').className = '';
  try {
    const r = await printerBt(); const d = r.daftar || [];
    const teks = !r.ada ? 'Tablet ini tidak punya Bluetooth.' : !r.izin ? 'Izin Bluetooth ditolak — izinkan "Perangkat di sekitar" untuk aplikasi ini di Setelan tablet, lalu tekan lagi.'
      : !r.nyala ? 'Bluetooth tablet mati — nyalakan di Setelan tablet, lalu tekan lagi.'
        : !d.length ? 'Belum ada printer SUNMI yang dipasangkan. Buka Setelan tablet › Bluetooth, pasangkan printer bernama CloudPrint_…, lalu tekan lagi.'
          : 'Sudah dipasangkan: ' + d.map((x) => x.nama).join(', ') + ' — pilih jalur "SDK SUNMI lewat Bluetooth" di kartu Jalur cetak, lalu Cetak contoh.';
    $('ucBtHasil').textContent = teks; $('ucBtHasil').className = d.length ? 'baik' : 'awas'; tulisLog('Bluetooth: ' + teks, !d.length);
  } catch (e) { $('ucBtHasil').textContent = 'Bluetooth tidak bisa ditanya: ' + pesan(e) + ' — pasang APK terbaru.'; $('ucBtHasil').className = 'awas'; tulisLog('Periksa Bluetooth gagal: ' + pesan(e), true); }
  $('ucBt').disabled = false;
}
async function bacaMode(diam) {
  $('ucModeBaca').disabled = true; if (!diam) { $('ucModeHasil').textContent = 'Menanyakan mode kertas…'; $('ucModeHasil').className = ''; }
  try {
    const r = await printerMode(lewatKini()); const k = kalimatModeKertas(r && r.mode);
    $('ucModeHasil').textContent = k.teks; $('ucModeHasil').className = k.baik ? 'baik' : 'awas'; tulisLog('Mode kertas: ' + k.teks, !k.baik);
  } catch (e) { $('ucModeHasil').textContent = 'Mode kertas tidak bisa ditanya: ' + pesan(e); $('ucModeHasil').className = 'awas'; tulisLog('Baca mode gagal: ' + pesan(e), true); }
  $('ucModeBaca').disabled = false;
}
async function setelMode() {
  const m = Number($('ucModeKertas').value); const nama = (MODE_KERTAS.filter((x) => x[0] === m)[0] || [0, '?'])[1];
  $('ucModeSetel').disabled = true; $('ucModeHasil').textContent = 'Meminta printer pindah ke mode ' + nama + '…'; $('ucModeHasil').className = '';
  try {
    await printerSetelMode(m, lewatKini()); tulisLog('Perintah pindah mode terkirim: ' + nama + ' — printer tidak mengabari hasilnya, modenya ditanyakan lagi');
    // printer butuh waktu (bisa berbunyi / mencetak tanda mode); sesudah itu ditanya lagi supaya yang tampil = jawaban printer, bukan harapan
    setTimeout(() => { bacaMode(true).then(() => { $('ucModeSetel').disabled = false; }); }, 3500);
  } catch (e) { $('ucModeHasil').textContent = 'Printer tidak bisa dipindah modenya: ' + pesan(e); $('ucModeHasil').className = 'awas'; tulisLog('Pindah mode gagal: ' + pesan(e), true); $('ucModeSetel').disabled = false; }
}
// label contoh — isinya CONTOH, bukan barang toko; kodenya berawalan lain dari label sungguhan supaya tidak pernah terpasang ke barang
const LABEL_CONTOH = { judul: 'Beras contoh 5 kg', ket: 'TOKO BERAS M.IQBAL', kode: 'UJI-LABEL-0001', teksKode: 'UJI-LABEL' };
function pratinjauLabel() {
  const a = isian(); $('ucLabelUkuran').hidden = a.labelCara !== 'tspl';
  try { $('ucLabelPratinjau').textContent = susunLabel(LABEL_CONTOH, 1, a).teks.join('\n'); } catch (e) { $('ucLabelPratinjau').textContent = pesan(e); }
}
async function cetakLabelContoh() {
  const a = isian(); $('ucLabelCetak').disabled = true; const mulai = Date.now();
  try {
    const r = await cetakLabel(LABEL_CONTOH, 1, a);
    tulisLog('LABEL contoh dikirim lewat ' + namaJalur(r.jalur) + ' · ' + (r.cara === 'tspl' ? 'stiker bercelah (TSPL)' : 'kertas bersambung') + ' · ' + r.byte + ' byte'
      + (r.tanpaKabar ? ' · printer tidak mengabari hasil perintah label — lihat kertasnya' : '') + (r.peringatan ? ' · ' + r.peringatan : ''));
    if (r.cadanganDari) tulisLog('Jalur SDK SUNMI TIDAK jalan, label ini keluar lewat USB langsung. Sebabnya: ' + r.cadanganDari, true);
  } catch (e) { tulisLog((masihMencetak(e) ? 'Label contoh belum dikirim: ' : hasilTakDiketahui(e) ? 'Label contoh: ' : 'Label contoh gagal: ') + pesanGagal(e, mulai), true); }
  $('ucLabelCetak').disabled = false;
}

// ---------- paket S4: lampu berwarna per kejadian ----------
let lampuIsi = {};   // { kejadian: { warna, kedip, detik } } yang sedang tampil di formulir (belum tentu tersimpan)
function gambarLampu() {
  const wadah = $('ucLampuAtur'); wadah.textContent = '';
  LAMPU_KEJADIAN.forEach((k) => {
    const kunci = k[0]; const a = lampuIsi[kunci]; const baris = document.createElement('div'); baris.className = 'lampu-baris';
    const nama = document.createElement('span'); nama.textContent = k[1]; baris.appendChild(nama);
    const warna = document.createElement('select'); warna.setAttribute('aria-label', 'Warna lampu: ' + k[1]);
    Object.keys(LAMPU_WARNA).concat([LAMPU_MATI]).forEach((w) => { const o = document.createElement('option'); o.value = w; o.textContent = w === LAMPU_MATI ? 'tidak menyala' : w; warna.appendChild(o); });
    warna.value = a.warna; warna.addEventListener('change', () => { a.warna = warna.value; }); baris.appendChild(warna);
    const lk = document.createElement('label'); const kedip = document.createElement('input'); kedip.type = 'checkbox'; kedip.checked = !!a.kedip;
    kedip.addEventListener('change', () => { a.kedip = kedip.checked; }); lk.appendChild(kedip); lk.appendChild(document.createTextNode(' berkedip')); baris.appendChild(lk);
    const ld = document.createElement('label'); const detik = document.createElement('input'); detik.type = 'number'; detik.className = 'pendek'; detik.min = '0.5'; detik.max = '10'; detik.step = '0.5'; detik.value = String(a.detik);
    detik.setAttribute('aria-label', 'Lama nyala (detik): ' + k[1]);
    detik.addEventListener('change', () => { const n = Number(detik.value); if (n >= 0.5 && n <= 10) a.detik = n; else detik.value = String(a.detik); }); ld.appendChild(detik); ld.appendChild(document.createTextNode(' dtk')); baris.appendChild(ld);
    const coba = document.createElement('button'); coba.type = 'button'; coba.textContent = 'Coba';
    coba.addEventListener('click', async () => {
      const r = await lampuKejadian(kunci, a);
      tulisLog('Lampu "' + k[1] + '" (' + (a.warna === LAMPU_MATI ? 'tidak menyala' : a.warna + (a.kedip ? ' berkedip' : '')) + '): ' + (r && r.mati ? 'diatur tidak menyala' : r && r.ok ? 'jalan' : 'tidak jalan' + (r && r.kode !== undefined ? ' (kode ' + r.kode + ')' : '')), !(r && (r.ok || r.mati)));
    });
    baris.appendChild(coba); wadah.appendChild(baris);
  });
}
async function ujiSidik() {
  $('ucSidikUji').disabled = true;
  try { await sidikJariUji(); tulisLog('Sidik jari: jari dikenali tablet'); $('ucSidik').textContent = 'sensor ada · uji tempel jari LULUS'; $('ucSidik').className = 'baik'; }
  catch (e) { const t = sidikJariTolak(e); tulisLog('Sidik jari: ' + t.kalimat, !t.batal); }
  $('ucSidikUji').disabled = false;
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
  // paket S2a: pembaca NFC bawaan — ada / mati di Setelan / tidak ada di aplikasi lama
  const n = k.nfc;
  $('ucNfc').textContent = !n ? 'tidak ada di aplikasi ini — pasang APK terbaru' : !n.ada ? 'tablet ini tidak punya pembaca NFC'
    : !n.nyala ? 'NFC dimatikan — nyalakan di Setelan tablet, lalu buka lagi layar ini' : 'siap — tempelkan kartu apa saja ke tablet, nomor serinya muncul di sini';
  // paket S4: sensor sidik jari — owner 19 Nov: periksa dulu ada-tidaknya; pemakaiannya belum diputuskan
  const b = k.biometrik;
  $('ucSidik').textContent = !b ? 'tidak ada di aplikasi ini — pasang APK terbaru' : b.kalimat + (b.ada && !b.terdaftar ? ' — daftarkan jari di Setelan tablet › Keamanan, lalu buka lagi layar ini' : '');
  $('ucSidik').className = b && b.ada ? 'baik' : 'awas'; $('ucSidikUji').disabled = !(b && b.terdaftar);
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
  PR_LABEL_CARA.forEach((p) => { const o = document.createElement('option'); o.value = p[0]; o.textContent = p[1]; $('ucLabelCara').appendChild(o); });
  MODE_KERTAS.forEach((p) => { const o = document.createElement('option'); o.value = String(p[0]); o.textContent = p[1]; $('ucModeKertas').appendChild(o); });
  isiForm(prAtur());

  const app = asliAda();
  $('ucDukung').textContent = app ? 'Aplikasi tablet kasir — cetak langsung ke printer USB.'
    : usbAda() ? 'Peramban biasa (WebUSB). Di Sunmi CPad pakai aplikasi tablet kasir (APK).' : 'Peramban ini tidak bisa mencetak ke USB — pakai aplikasi tablet kasir (APK).';
  $('ucDukung').className = app ? 'baik' : 'awas';
  $('ucPilihBaris').hidden = app; $('ucJalurBaris').hidden = !app; $('ucPrinterSunmi').hidden = !app; $('ucSunmi').hidden = !app;
  $('ucLabel').hidden = !app;
  if (app) {
    $('ucStatus').addEventListener('click', periksaPrinter);
    $('ucBt').addEventListener('click', periksaBt);
    $('ucModeBaca').addEventListener('click', () => bacaMode(false));
    $('ucModeSetel').addEventListener('click', setelMode);
    $('ucLabelCetak').addEventListener('click', cetakLabelContoh);
    ['ucLabelCara', 'ucLabelLebar', 'ucLabelTinggi', 'ucLabelCelah', 'ucLabelPotong', 'ucKertas'].forEach((id) => $(id).addEventListener('change', pratinjauLabel));
    pratinjauLabel();
    lampuIsi = lampuAtur(); gambarLampu();
    $('ucLampuSimpan').addEventListener('click', () => { const ok = lampuSimpan(lampuIsi); tulisLog(ok ? 'Setelan lampu tersimpan untuk tablet ini' : 'Setelan lampu TIDAK tersimpan (penyimpanan perangkat ditolak)', !ok); });
    $('ucLampuBawaan').addEventListener('click', () => { lampuIsi = lampuAtur(null); gambarLampu(); tulisLog('Lampu dikembalikan ke bawaan di formulir — tekan Simpan lampu supaya berlaku'); });
    $('ucLampuPadam').addEventListener('click', async () => { const r = await lampuPadam(); tulisLog('Lampu padam: ' + (r && r.ok ? 'jalan' : 'tidak jalan'), !(r && r.ok)); });
    $('ucSidikUji').addEventListener('click', ujiSidik);
    let nPindai = 0;
    padaPindai((x) => { nPindai += 1; $('ucPindai').textContent = '"' + x.data + '" · ' + x.data.length + ' huruf · scan ke-' + nPindai; tulisLog('Scan diterima: ' + x.data); });
    let nTempel = 0;
    padaTempel((x) => { nTempel += 1; $('ucNfc').textContent = 'kartu ' + x.uid + (x.jenis.length ? ' · ' + x.jenis.join(', ') : '') + ' · tempel ke-' + nTempel; tulisLog('Kartu NFC terbaca: ' + x.uid); });
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
