// PRINTER PERANGKAT INI (putaran T1 langkah 2) — satu pintu cetak struk ke printer USB: aplikasi tablet (APK, plugin CetakUsb) atau WebUSB
// peramban; kalau keduanya tidak ada, pemanggil memakai dialog cetak seperti dulu. Setelan (gaya, potong, logo) disimpan PER PERANGKAT di
// localStorage — printernya menempel di tablet, bukan di toko — dan diatur di /baru/uji-cetak.html. Tidak membaca/menulis data toko.
// Paket S1 (19 Nov 2026): di aplikasi tablet ada DUA jalur — 'aplikasi' (CetakUsb: byte langsung, terbukti sejak 16 Nov) dan 'sunmi' (SDK resmi
// SUNMI: keadaan printer diperiksa dulu + hasil cetak dikabari). Jalur 'sunmi' dipilih owner per perangkat SESUDAH lulus uji di uji-cetak.html;
// kalau SDK-nya gagal sebelum ada byte terkirim, cetak jatuh ke CetakUsb (inti/perangkat.js › cetakAsli).
// Paket S4 (19 Nov 2026): jalur ketiga 'sunmi-bt' (SDK SUNMI lewat Bluetooth) + LABEL barang — di kertas bersambung (ESC/POS) atau stiker bercelah
// (TSPL, printer di mode label); ukuran label & caranya juga setelan perangkat ini.
import { epSusun, epSusunGambar, epBase64, epSusunLabel, epTsplLabel, epPotong } from './escpos.js';
import { gambarStruk, siapkanHuruf, teksKeLogo } from './struk-kanvas.js';
import { usbAda, usbDiingat, usbKirim } from './usb-cetak.js';
import { asliAda, panggilAsli, cetakAsli, kirimTspl, lewatJalur, pastikanModeLabel, alamatPrinterSah } from './perangkat.js';

export const PR_KUNCI = 'printerPerangkat';
export const PR_GAYA = [['gambar', 'gambar (huruf toko, logo, total berpita)'], ['teks', 'teks (cepat, huruf printer)']];
/** Jalur cetak di aplikasi tablet: 'usb' = CetakUsb (bawaan, terbukti) · 'sunmi' = SDK resmi SUNMI lewat kabel USB (keadaan printer + hasil cetak)
 *  · 'sunmi-bt' = SDK yang sama lewat Bluetooth (printer dipasangkan dulu di Setelan tablet). */
export const PR_JALUR = [['usb', 'USB langsung (bawaan, terbukti)'], ['sunmi', 'SDK SUNMI lewat kabel USB (periksa kertas & tutup dulu, hasil cetak dikabari)'],
  ['sunmi-bt', 'SDK SUNMI lewat Bluetooth (tanpa kabel; struk bergambar lebih lambat)'],
  ['jaringan', 'Jaringan Wi-Fi / LAN (tanpa kabel; printer dan tablet di router yang sama)']];
/** Bluetooth + struk bergambar (uji owner 20 Nov 2026): kiriman ±84 ribu byte sering HILANG seluruhnya — printer menjawab tanya keadaan,
 *  menerima data, lalu diam dan tidak mencetak apa pun; kiriman kecil (gaya teks, label) selalu sampai. Sebab pastinya belum diketahui.
 *  `btPotong` = kirim per pita gambar, tiap potong ditunggu kabarnya dulu. PERCOBAAN: bawaan mati sampai terbukti di printer toko. */
/** Cara mencetak label barang: 'struk' = kertas bersambung (mode struk / stiker tanpa alas) · 'tspl' = stiker bercelah (printer di mode label). */
export const PR_LABEL_CARA = [['struk', 'kertas bersambung — mode struk atau stiker tanpa alas'], ['tspl', 'stiker bercelah — printer di mode label']];
export const PR_LABEL_BATAS = { labelLebar: [20, 80], labelTinggi: [15, 200], labelCelah: [0, 10] };   // mm
export const PR_BAWAAN = { gaya: 'gambar', kertas: 80, potong: 'sebagian', umpan: 4, qr: false, logo: '', aktif: true,
  labelCara: 'struk', labelLebar: 50, labelTinggi: 30, labelCelah: 2, labelPotong: true, jalur: 'usb', btPotong: false, alamatPrinter: '' };

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
    if (PR_JALUR.some((x) => x[0] === d.jalur)) a.jalur = d.jalur;
    if (PR_LABEL_CARA.some((x) => x[0] === d.labelCara)) a.labelCara = d.labelCara;
    Object.keys(PR_LABEL_BATAS).forEach((k) => { const b = PR_LABEL_BATAS[k]; if (Number.isInteger(d[k]) && d[k] >= b[0] && d[k] <= b[1]) a[k] = d[k]; });
    if (typeof d.labelPotong === 'boolean') a.labelPotong = d.labelPotong;
    if (typeof d.btPotong === 'boolean') a.btPotong = d.btPotong;
    // alamat printer di jaringan toko: hanya yang sah (IPv4 pribadi) yang dipakai; tinggal di perangkat ini saja, tidak ikut ke data toko
    if (typeof d.alamatPrinter === 'string') a.alamatPrinter = alamatPrinterSah(d.alamatPrinter);
  } catch (e) { /* penyimpanan tidak bisa dibaca → bawaan */ }
  return a;
}
export function prSimpan(a) {
  try { localStorage.setItem(PR_KUNCI, JSON.stringify(Object.assign(prAtur(), a || {}))); return true; } catch (e) { return false; }
}

// ---------- aplikasi tablet (Capacitor) — pintunya inti/perangkat.js ----------
export { asliAda };
/** Daftar perangkat USB yang terlihat aplikasi (diagnosis). */
export const asliDaftar = () => panggilAsli('CetakUsb', 'daftar', {});
/** Nama jalur untuk catatan struk & kabar. 'aplikasi' dan 'peramban' sama persis dengan teks sebelum paket S1. */
export function namaJalur(j) { return j === 'sunmi' ? 'aplikasi tablet (SDK SUNMI)' : j === 'sunmi-bt' ? 'aplikasi tablet (SDK SUNMI, Bluetooth)' : j === 'jaringan' ? 'aplikasi tablet (jaringan Wi-Fi/LAN)' : j === 'aplikasi' ? 'aplikasi tablet' : 'peramban'; }
/** Kata depan catatan struk: jalur Bluetooth bukan "printer USB" (kata Bluetooth-nya sudah ada di namaJalur). */
export function namaPrinter(j) { return j === 'sunmi-bt' || j === 'jaringan' ? 'printer ' : 'printer USB '; }
/** Sebutan printer untuk kabar gagal di layar: "Printer Bluetooth" · "Printer jaringan" · "Printer USB". */
export function sebutPrinter(j) { return j === 'sunmi-bt' ? 'Printer Bluetooth' : j === 'jaringan' ? 'Printer jaringan' : 'Printer USB'; }

/** Jalur cetak yang tersedia di perangkat ini: 'sunmi' / 'sunmi-bt' / 'aplikasi' (aplikasi tablet, menurut setelan perangkat) · 'peramban' (WebUSB, printer pernah diizinkan) · 'dialog'. */
export async function jalurCetak() {
  const a = prAtur(); if (!a.aktif) return 'dialog';
  if (asliAda() && a.jalur === 'sunmi-bt') return 'sunmi-bt';
  if (asliAda() && a.jalur === 'jaringan') return 'jaringan';
  if (asliAda()) return a.jalur === 'sunmi' ? 'sunmi' : 'aplikasi';
  if (usbAda()) { try { const d = await usbDiingat(); if (d.length) return 'peramban'; } catch (e) { /* tidak bisa membaca */ } }
  return 'dialog';
}

/** Susun byte dari garis struk menurut setelan perangkat (atau `timpa`). Hasil: { byte, gaya, kertas, teks? (gaya teks), gambar? (gaya gambar) }. */
export async function susunCetak(garis, timpa, ekstra) {
  const a = Object.assign(prAtur(), timpa || {}); const o = Object.assign({ kertas: a.kertas, potong: a.potong, umpan: a.umpan }, ekstra || {});
  if (a.gaya === 'teks') { const t = epSusun(garis, o); return { byte: t.byte, teks: t.teks, gaya: 'teks', kertas: a.kertas }; }
  await siapkanHuruf();
  // owner 17 Nov (butir 3): logo perangkat sendiri menang; tanpa itu logo toko (F mahkota padi, digambar kode) bila setelan struk menyertakannya (ekstra.logoToko)
  const g = gambarStruk(garis, { kertas: a.kertas, logo: teksKeLogo(a.logo), logoToko: !!o.logoToko });
  const sg = epSusunGambar(g, o);
  return { byte: sg.byte, gaya: 'gambar', kertas: a.kertas, gambar: g, batas: sg.batas };
}

/** Kirim byte lewat jalur yang ada. Melempar galat berisi sebabnya (pemanggil memutuskan jatuh ke dialog cetak).
 *  Hasil: { jalur (yang SUNGGUH dipakai), byte, perangkat, peringatan ('' = tidak ada), cadanganDari ('' = bukan cadangan) }. */
export async function kirimCetak(byte, jalur, batas, timpa) {
  const j = jalur || await jalurCetak();
  if (j === 'aplikasi' || j === 'sunmi' || j === 'sunmi-bt' || j === 'jaringan') {
    // `batas` (dari susunCetak gaya gambar) hanya dipakai jalur Bluetooth: kiriman dipecah per pita gambar, tiap potong ditunggu kabarnya
    const bagian = j === 'sunmi-bt' && Array.isArray(batas) && batas.length ? epPotong(byte, batas).map((b) => epBase64(b)) : null;
    // jalur jaringan: alamat printer dari isian layar Perangkat (`timpa.alamat`, belum tentu tersimpan) atau dari setelan perangkat ini
    const opsi = j === 'jaringan' ? { alamat: timpa && typeof timpa.alamat === 'string' ? timpa.alamat : prAtur().alamatPrinter } : null;
    const r = await cetakAsli(epBase64(byte), j, bagian, opsi);
    return { jalur: r.jalur, byte: byte.length, perangkat: r.nama, peringatan: r.peringatan, cadanganDari: r.cadanganDari, potong: r.potong || 1, tugas: r.tugas || '' };
  }
  if (j === 'peramban') { const d = (await usbDiingat())[0]; const r = await usbKirim(d, byte); return { jalur: j, byte: r.byte, perangkat: d.productName || '', peringatan: '', cadanganDari: '' }; }
  throw new Error('Tidak ada printer USB di perangkat ini');
}

/** Satu langkah: garis → byte → printer. Hasil: { jalur, gaya, kertas, byte, perangkat, peringatan, cadanganDari }. */
export async function cetakGaris(garis, ekstra) {
  const j = await jalurCetak(); if (j === 'dialog') throw new Error('Tidak ada printer USB di perangkat ini');
  const s = await susunCetak(garis, null, Object.assign({ qr: '' }, ekstra || {}));
  // Bluetooth + struk bergambar: dikirim per potong bila setelan perangkat ini memintanya (layar Perangkat › "kirim per potong")
  const r = await kirimCetak(s.byte, j, j === 'sunmi-bt' && prAtur().btPotong ? s.batas : null);
  return { jalur: r.jalur, gaya: s.gaya, kertas: s.kertas, byte: r.byte, perangkat: r.perangkat, peringatan: r.peringatan || '', cadanganDari: r.cadanganDari || '' };
}

// ---------- label barang (paket S4) ----------
/** Susun satu perintah cetak label menurut setelan perangkat (atau `timpa`). isi = { judul, ket, kode, teksKode } (tanda-kenal-logika › tkIsiLabel).
 *  Hasil { cara: 'struk' | 'tspl', byte, teks (baris pratinjau / perintah TSPL), jumlah }. Murni: tidak mengirim apa-apa. */
export function susunLabel(isi, jumlah, timpa) {
  const a = Object.assign(prAtur(), timpa || {});
  if (a.labelCara === 'tspl') {
    const t = epTsplLabel(isi, { lebarMm: a.labelLebar, tinggiMm: a.labelTinggi, celahMm: a.labelCelah, jumlah, potong: a.labelPotong });
    return { cara: 'tspl', byte: t.byte, teks: t.teks, jumlah: t.jumlah };
  }
  const s = epSusunLabel(isi, { kertas: a.kertas, potong: a.potong, umpan: a.umpan, jumlah });
  return { cara: 'struk', byte: s.byte, teks: s.teks, jumlah: s.jumlah };
}

/** Cetak label barang lewat jalur cetak perangkat ini. Hasil { cara, jalur, jumlah, byte, perangkat, peringatan, cadanganDari, tanpaKabar }.
 *  tanpaKabar = true → printer tidak mengabari hasil perintah label (TSPL): lihat kertasnya. Tanpa printer di perangkat ini → melempar. */
export async function cetakLabel(isi, jumlah, timpa) {
  // layar Perangkat mencoba jalur yang sedang DIPILIH di formulir (belum tentu tersimpan): timpa.jalur menang atas setelan tersimpan — hanya di aplikasi
  const pilih = timpa && asliAda() && PR_JALUR.some((x) => x[0] === timpa.jalur) ? (timpa.jalur === 'usb' ? 'aplikasi' : timpa.jalur) : '';
  const j = pilih || await jalurCetak(); if (j === 'dialog') throw new Error('Tidak ada printer di perangkat ini — label dicetak dari tablet kasir');
  const l = susunLabel(isi, jumlah, timpa);
  // lewat SDK SUNMI printer bisa ditanya modenya: label yang bahasanya pasti salah untuk mode itu ditolak SEBELUM ada yang dikirim
  if (j === 'sunmi' || j === 'sunmi-bt') await pastikanModeLabel(l.cara, lewatJalur(j));
  if (l.cara === 'tspl' && (j === 'sunmi' || j === 'sunmi-bt')) {
    // SDK SUNMI punya pintu sendiri untuk perintah label; pintu struknya menanyakan keadaan printer dengan bahasa struk, yang tidak dijawab di mode label
    const r = await kirimTspl(l.teks.join('\n') + '\n', lewatJalur(j));
    return { cara: l.cara, jalur: j, jumlah: l.jumlah, byte: l.byte.length, perangkat: (r && r.nama) || '', peringatan: '', cadanganDari: '', tanpaKabar: true };
  }
  // jaringan: pintu printernya hanya menerima bahasa struk; perintah label stiker bercelah belum punya jalan lewat jaringan
  if (l.cara === 'tspl' && j === 'jaringan') { const e = new Error('Label stiker bercelah belum bisa dikirim lewat jaringan — pakai jalur Bluetooth atau kabel, atau ganti cara label ke "kertas bersambung"'); e.code = 'SALAH_MODE'; throw e; }
  const r = await kirimCetak(l.byte, j, null, timpa && typeof timpa.alamatPrinter === 'string' ? { alamat: timpa.alamatPrinter } : null);
  return { cara: l.cara, jalur: r.jalur, jumlah: l.jumlah, byte: r.byte, perangkat: r.perangkat, peringatan: r.peringatan || '', cadanganDari: r.cadanganDari || '', tanpaKabar: l.cara === 'tspl' };
}
