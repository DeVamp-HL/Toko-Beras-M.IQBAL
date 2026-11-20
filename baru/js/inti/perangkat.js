// PERANGKAT (paket S1, 19 Nov 2026) — SATU PINTU dari halaman ke perangkat keras lewat aplikasi tablet (APK Capacitor, apk/tambahan/*.java).
// Tiap perangkat = satu plugin kecil di aplikasi: CetakUsb (byte ke printer USB), PrinterSunmi (SDK resmi SUNMI: keadaan printer, hasil cetak,
// laci, Bluetooth, mode kertas, label), Pindai (scanner bawaan), Lampu (LED CPad), Perangkat (kartu nama perangkat), Nfc (pembaca NFC bawaan),
// Biometrik (sensor sidik jari — paket S4: periksa dulu ada-tidaknya). Modul ini TIDAK membaca/menulis data toko dan TANPA impor
// (dijalankan apa adanya di jsc oleh alat-uji/uji_perangkat_sunmi.py). Di HP/Mac (bukan aplikasi) semua fungsinya diam: tidak ada yang melempar.

const cap = () => (typeof window !== 'undefined' ? window.Capacitor : null);

/** Halaman ini berjalan di dalam aplikasi tablet (bukan peramban biasa)? */
export function asliAda() { const c = cap(); return !!(c && typeof c.isNativePlatform === 'function' && c.isNativePlatform()); }

/** Plugin `nama` ada di aplikasi yang terpasang? true / false; null = aplikasi tidak bisa ditanya (anggap "coba saja"). APK lama tidak punya plugin baru. */
export function adaPlugin(nama) {
  const c = cap(); if (!asliAda()) return false;
  try { if (Array.isArray(c.PluginHeaders)) return c.PluginHeaders.some((x) => x && x.name === nama); } catch (e) { /* lanjut ke cara lain */ }
  try { if (typeof c.isPluginAvailable === 'function') return !!c.isPluginAvailable(nama); } catch (e) { /* lanjut ke cara lain */ }
  return null;
}

function galat(pesan, kode) { const e = new Error(pesan); e.code = kode; return e; }

/** Panggil satu metode plugin. Menolak dengan Error ber-`code` bila aplikasinya menolak; 'TIDAK_ADA' = bukan aplikasi / plugin tak terpasang. */
export function panggilAsli(plugin, metode, isi) {
  const c = cap();
  if (!asliAda()) return Promise.reject(galat('Bukan aplikasi tablet — ' + plugin + ' hanya ada di aplikasi tablet kasir', 'TIDAK_ADA'));
  if (typeof c.nativePromise === 'function') return c.nativePromise(plugin, metode, isi || {});
  const p = c.Plugins && c.Plugins[plugin]; if (p && typeof p[metode] === 'function') return p[metode](isi || {});
  return Promise.reject(galat('Plugin ' + plugin + ' tidak ada di aplikasi ini — pasang APK terbaru', 'TIDAK_ADA'));
}

/** Dengarkan kejadian plugin (mis. Pindai › 'pindai'). Hasil: fungsi pelepas. Bukan aplikasi = tidak mendengar apa-apa. */
export function dengarAsli(plugin, kejadian, fn) {
  const c = cap(); if (!asliAda()) return () => {};
  const lepas = (h) => () => { Promise.resolve(h).then((x) => { if (x && typeof x.remove === 'function') return x.remove(); }).catch(() => {}); };
  try {
    const p = c.Plugins && c.Plugins[plugin];
    if (p && typeof p.addListener === 'function') return lepas(p.addListener(kejadian, fn));
    if (typeof c.addListener === 'function') return lepas(c.addListener(plugin, kejadian, fn));
    if (typeof c.nativeCallback === 'function') { c.nativeCallback(plugin, 'addListener', { eventName: kejadian }, fn); return () => {}; }
  } catch (e) { /* aplikasi lama tanpa plugin ini */ }
  return () => {};
}

// ---------- cetak lewat aplikasi ----------
/** Galat dari printer yang SUDAH menjawab (kertas habis, tutup terbuka, diam sesudah data dikirim): jangan dikirim ulang lewat jalur lain. */
export function galatPrinter(e) { return !!(e && typeof e.code === 'string' && e.code.indexOf('PRINTER_') === 0); }
const pesanGalat = (e) => (e && e.message ? e.message : String(e));
/** Printer DIAM sesudah data cetak dikirim: pustaka SUNMI menyerah menanyai nomor pekerjaannya (kode PRINTER_UNKNOWN, ±40 detik) atau batas
 *  waktu aplikasi habis (PRINTER_DIAM). Hasilnya TIDAK DIKETAHUI — bukan pasti gagal, bukan pasti keluar. Uji owner 20 Nov 2026 (Bluetooth,
 *  cetak pertama sesudah printer menganggur ±3 menit): layar menulis "Cetak gagal: keadaan printer tidak diketahui", kertas tidak keluar,
 *  cetak berikutnya 5 detik kemudian keluar. */
export function hasilTakDiketahui(e) { return !!(e && (e.code === 'PRINTER_UNKNOWN' || e.code === 'PRINTER_DIAM')); }
export const KALIMAT_TAK_DIKABARI = 'Printer tidak mengabari hasil cetaknya — lihat kertasnya dulu; kalau tidak keluar, cetak lagi';

// ---------- satu cetakan pada satu waktu ----------
// Uji owner 20 Nov 2026 malam (Jual, Bluetooth): tiap gagal tercatat DUA baris dan kabarnya "printer tidak tersambung". Sebabnya dari isi
// aplikasi & pustaka: pustaka SUNMI mengerjakan perintah satu per satu di SATU antrean dan satu sambungan. Cetakan pertama masih menunggu
// printer (yang diam sampai ±43 detik); ketukan Cetak kedua menanya keadaan printer, antre di belakangnya, habis waktu 4 detik, lalu aplikasi
// MELEPAS sambungan itu — sambungan yang sedang dipakai cetakan pertama. Cetakan pertama pun melapor "tidak tersambung".
// Maka: selama satu cetakan belum dikabari hasilnya, permintaan cetak berikutnya DITOLAK di sini (kode SEDANG_CETAK) sebelum menyentuh aplikasi.
// Kunci itu tidak boleh macet: aplikasi selalu menjawab dalam batasnya sendiri (sambung 12 + tanya 4 + cetak Bluetooth 60 detik), tapi kalau
// jawabannya tidak pernah sampai ke halaman, kunci dianggap lepas sesudah BATAS_SIBUK_MS — supaya toko tidak terkunci dari printernya sendiri.
export const BATAS_SIBUK_MS = 90000;
let kunci = null;
/** Masih ada cetakan yang belum dikabari hasilnya? */
export const printerSibuk = () => !!kunci && Date.now() - kunci.sejak < BATAS_SIBUK_MS;
/** Galat "masih mencetak": bukan kegagalan printer — jangan buka dialog, jangan kirim lewat jalur lain, jangan nyalakan lampu gagal. */
export function masihMencetak(e) { return !!(e && e.code === 'SEDANG_CETAK'); }
export const KALIMAT_MASIH_MENCETAK = 'Cetakan sebelumnya belum dikabari printer — tunggu kabarnya dulu, jangan ketuk Cetak lagi (paling lama ±1,5 menit)';
const tolakBilaSibuk = () => { if (printerSibuk()) throw galat(KALIMAT_MASIH_MENCETAK, 'SEDANG_CETAK'); };
async function satuCetakan(kerja) {
  tolakBilaSibuk(); const k = { sejak: Date.now() }; kunci = k;
  // jawaban cetakan lama yang datang terlambat tidak boleh membuka kunci cetakan yang lebih baru
  try { return await kerja(); } finally { if (kunci === k) kunci = null; }
}

/** Jalur cetak → cara menyambung printer SUNMI: 'bt' (Bluetooth) atau 'usb'. */
export const lewatJalur = (jalur) => (jalur === 'sunmi-bt' ? 'bt' : 'usb');
/** Kirim byte struk (base64) lewat aplikasi tablet. Hasil: { jalur: 'sunmi' | 'sunmi-bt' | 'aplikasi', nama, peringatan, cadanganDari }.
 *  jalur 'sunmi' = SDK resmi SUNMI lewat kabel USB (keadaan printer diperiksa dulu, hasil cetak dikabari); 'sunmi-bt' = SDK yang sama lewat
 *  Bluetooth (paket S4: printer harus sudah dipasangkan di Setelan tablet). Kalau SDK gagal SEBELUM ada byte terkirim (printer tak ketemu,
 *  Bluetooth mati, plugin tak ada di APK lama) → jatuh ke CetakUsb, alasannya di `cadanganDari`. Kalau printer menjawab ada halangan
 *  → galatnya dilempar apa adanya: mengirim ulang lewat jalur lain bisa mencetak dobel atau percuma. Kalau printer diam sesudah data
 *  dikirim (hasilTakDiketahui) → dilempar berkalimat KALIMAT_TAK_DIKABARI, juga TANPA kirim ulang: yang memutuskan orangnya, sesudah melihat kertas.
 *  Satu cetakan pada satu waktu: dipanggil saat cetakan lain belum dikabari → menolak berkode SEDANG_CETAK tanpa menyentuh aplikasi.
 *  `opsi.alamat` = alamat printer untuk jalur jaringan. Satu struk = SATU kiriman: percobaan "kirim per potong" lewat Bluetooth dicabut
 *  (owner 20 Nov 2026 malam) — di kertas hanya potong pertama yang keluar. */
export const cetakAsli = (data, jalur, opsi) => satuCetakan(() => cetakAsliDalam(data, jalur, opsi));
/** Jalur yang dipilih gagal SEBELUM ada yang sampai ke printer → dikirim langsung lewat kabel USB; kalau itu gagal juga, KEDUA sebab dibawa. */
async function jatuhKeKabel(data, sebab) {
  let r;
  try { r = await panggilAsli('CetakUsb', 'cetak', { data }); }
  catch (e3) {
    // Kedua jalur gagal: sebab jalur yang DIPILIH harus tetap terbaca. Dulu hanya sebab cadangan yang sampai ke layar — uji owner 20 Nov:
    // "Printer Bluetooth gagal (Printer USB tidak ditemukan…)", sebab Bluetooth-nya sendiri hilang.
    const g = galat(sebab + ' · kirim langsung lewat kabel USB juga gagal: ' + pesanGalat(e3), e3 && e3.code);
    g.sebabUtama = sebab; throw g;
  }
  return { jalur: 'aplikasi', nama: (r && r.nama) || '', peringatan: '', cadanganDari: sebab };
}
async function cetakAsliDalam(data, jalur, opsi) {
  if (jalur === 'sunmi' || jalur === 'sunmi-bt') {
    let sebab = '';
    try {
      const r = await panggilAsli('PrinterSunmi', 'cetak', { data, lewat: lewatJalur(jalur) });
      return { jalur, nama: (r && r.nama) || '', peringatan: (r && r.peringatan) || '', cadanganDari: '' };
    } catch (e) {
      // hasil tidak diketahui: kalimatnya menyebut langkah berikutnya (lihat kertas), kodenya tetap, kabar asli aplikasi ikut di `asli`
      if (hasilTakDiketahui(e)) { const g = galat(KALIMAT_TAK_DIKABARI, e.code); g.asli = pesanGalat(e); throw g; }
      if (galatPrinter(e)) throw e;
      // aplikasi sendiri menolak karena perintah printer lain belum selesai (pintu di PrinterSunmiPlugin): cetakan itu masih jalan —
      // mengirim struk ini lewat kabel bisa mencetak dobel, dan melepas sambungan memutus cetakan yang sedang jalan
      if (masihMencetak(e)) { const gs = galat(KALIMAT_MASIH_MENCETAK, 'SEDANG_CETAK'); gs.asli = pesanGalat(e); throw gs; }
      sebab = pesanGalat(e);
      try { await panggilAsli('PrinterSunmi', 'lepas', {}); } catch (e2) { /* APK lama: plugin tidak ada */ }
    }
    return jatuhKeKabel(data, sebab);
  }
  if (jalur === 'jaringan') {
    let sebab = '';
    try {
      const r = await cetakJaringan(data, opsi && opsi.alamat);
      return { jalur, nama: r.nama, peringatan: r.peringatan, cadanganDari: '', tugas: r.tugas };
    } catch (e) {
      if (hasilTakDiketahui(e)) { const gj = galat(KALIMAT_TAK_DIKABARI, e.code); gj.asli = pesanGalat(e); throw gj; }
      // halangan pasti dari printer, atau alamatnya belum diisi: kabel tidak dicoba (percuma / bukan itu yang diminta)
      if (galatPrinter(e) || (e && e.code === 'SALAH_ISI')) throw e;
      sebab = pesanGalat(e);
    }
    return jatuhKeKabel(data, sebab);
  }
  const r = await panggilAsli('CetakUsb', 'cetak', { data });
  return { jalur: 'aplikasi', nama: (r && r.nama) || '', peringatan: '', cadanganDari: '' };
}

// ---------- printer lewat JARINGAN (Wi-Fi / LAN) ----------
// Uji owner 20 Nov 2026 malam: struk bergambar ±84 ribu byte lewat Bluetooth hilang kira-kira 5 dari 8 kali, sedangkan kiriman yang SAMA
// lewat jaringan (dari Mac, pintu resmi SUNMI "Cloud Printer Over LAN HTTP") keluar 6 dari 6 dan printer melaporkan tiap pekerjaan tercetak.
// Pintunya HTTP polos di printer sendiri: POST heksa ESC/POS ke /cgi-bin/print.cgi → "task_id: N"; POST /cgi-bin/status.cgi[?task_id=N] →
// baris "kunci: yes|no" + "task_status: printed | not printed". Nomor seri tidak wajib (tanpa nomor seri diterima; nomor seri SALAH ditolak).
// Halaman toko (https) tidak boleh memanggil http://… sendiri, jadi permintaannya dititipkan ke aplikasi tablet (CapacitorHttp bawaan
// Capacitor); aplikasinya harus mengizinkan HTTP polos (apk/pasang.py). Semua logikanya di sini — bisa diubah tanpa APK baru.
/** Jeda antar-tanya & batasnya. Benda yang bisa diubah supaya uji tidak menunggu sungguhan. */
export const JARINGAN = { jedaMs: 400, tanyaMaks: 50, tungguMs: 30000, sambungMs: 4000, bacaMs: 15000 };
const jeda = (ms) => new Promise((ok) => { if (ms > 0 && typeof setTimeout === 'function') setTimeout(ok, ms); else ok(); });
const KALIMAT_ALAMAT = 'Alamat printer di jaringan belum diisi dengan benar — isi di layar Perangkat (contoh 192.168.1.50; lihat struk uji jaringan printer)';
/** Alamat printer di jaringan toko → teks rapi, atau '' bila tidak sah. Hanya IPv4 PRIBADI (10.x · 172.16–31.x · 192.168.x): pintu ini
 *  tidak boleh bisa dipakai mengirim apa pun ke alamat di luar jaringan toko. Tempelan "http://192.168.1.50/#/…" (hasil scan QR struk uji
 *  jaringan) diterima dan dirapikan. */
export function alamatPrinterSah(teks) {
  const t = String(teks == null ? '' : teks).trim().replace(/^https?:\/\//i, '').replace(/[\/#?].*$/, '');
  const m = t.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/); if (!m) return '';
  const b = m.slice(1).map(Number); if (b.some((x) => x > 255)) return '';
  const pribadi = b[0] === 10 || (b[0] === 172 && b[1] >= 16 && b[1] <= 31) || (b[0] === 192 && b[1] === 168);
  return pribadi ? b.join('.') : '';
}
/** Jawaban printer → benda. dikenali = bentuknya memang jawaban keadaan printer SUNMI (supaya alamat perangkat lain tidak dikira printer). */
export function bacaJawabJaringan(teks) {
  const o = {}; String(teks == null ? '' : teks).split(/\r?\n/).forEach((b) => { const m = b.match(/^\s*([a-z_]+)\s*:\s*(.*?)\s*$/); if (m) o[m[1]] = m[2]; });
  const ya = (k) => (o[k] === 'yes' ? true : o[k] === 'no' ? false : null);
  return { dikenali: ya('no_paper') !== null && ya('platen_opened') !== null, mencetak: ya('printing'), kertasHabis: ya('no_paper'), macet: ya('paper_jam'),
    belumDiambil: ya('paper_not_taken'), tutupTerbuka: ya('platen_opened'), kepalaPanas: ya('thermal_head_overheated'), motorPanas: ya('step_motor_overheated'),
    tugas: o.task_id === undefined ? '' : o.task_id, tugasStatus: o.task_status || '' };
}
/** Halangan pasti dari keadaan itu → { kode, kalimat } (kode & kalimat sama dengan jalur SDK) atau null. */
export function halanganJaringan(k) {
  if (!k) return null;
  if (k.tutupTerbuka) return { kode: 'PRINTER_COVER', kalimat: 'tutup printer terbuka' };
  if (k.kertasHabis) return { kode: 'PRINTER_OUT_PAPER', kalimat: 'kertas habis' };
  if (k.macet) return { kode: 'PRINTER_JAM_PAPER', kalimat: 'kertas macet' };
  if (k.kepalaPanas) return { kode: 'PRINTER_OVER_HOT', kalimat: 'kepala cetak terlalu panas' };
  if (k.motorPanas) return { kode: 'PRINTER_MOTOR_HOT', kalimat: 'motor printer terlalu panas' };
  return null;
}
const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
/** base64 → heksa huruf kecil (bentuk yang diminta print.cgi). Murni, tanpa atob, supaya sama di tablet dan di uji. */
export function b64KeHeksa(teks) {
  const t = String(teks || '').replace(/[^A-Za-z0-9+/]/g, ''); const h = '0123456789abcdef'; const keluar = [];
  let tampung = 0; let bit = 0;
  for (let i = 0; i < t.length; i++) {
    tampung = ((tampung << 6) | B64.indexOf(t[i])) & 0xffff; bit += 6;
    if (bit >= 8) { bit -= 8; const v = (tampung >> bit) & 0xff; keluar.push(h[v >> 4] + h[v & 15]); }
  }
  return keluar.join('');
}
const tanyaJaringan = (alamat, jalan, badan, bacaMs) => panggilAsli('CapacitorHttp', 'request', { url: 'http://' + alamat + jalan, method: 'POST',
  headers: { 'Content-Type': 'text/plain; charset=utf-8' }, data: badan || '', responseType: 'text', connectTimeout: JARINGAN.sambungMs, readTimeout: bacaMs || JARINGAN.bacaMs });
/** Galat permintaan jaringan → 'apk' (aplikasi belum mengizinkan HTTP polos) · 'belum' (pasti belum ada yang sampai ke printer) · 'takjelas'. */
function jenisGalatJaringan(e) {
  const kode = String((e && e.code) || ''); const p = String((e && e.message) || '').toLowerCase();
  if (kode === 'UnknownServiceException' || p.indexOf('cleartext') >= 0) return 'apk';
  if (kode === 'TIDAK_ADA' || kode === 'ConnectException' || kode === 'NoRouteToHostException' || kode === 'UnknownHostException'
    || /failed to connect|connect timed out|unreachable|refused|no route/.test(p)) return 'belum';
  return 'takjelas';
}
function galatSambungJaringan(e, alamat) {
  if (e && e.code === 'TIDAK_ADA') return galat(pesanGalat(e), 'BELUM_KIRIM');
  if (jenisGalatJaringan(e) === 'apk') return galat('Aplikasi tablet ini belum boleh menghubungi printer lewat jaringan — pasang APK terbaru', 'BELUM_KIRIM');
  return galat('Printer di ' + alamat + ' tidak terjangkau lewat jaringan — pastikan printer menyala dan tablet di Wi-Fi yang sama (' + pesanGalat(e) + ')', 'BELUM_KIRIM');
}
/** Keadaan printer di jaringan: { alamat, keadaan, siap, menghalangi, kalimat }. Menolak berkode SALAH_ISI (alamat) atau BELUM_KIRIM (tidak
 *  terjangkau / yang menjawab bukan printer) — pada titik ini belum ada data cetak yang dikirim, jadi jalur lain masih boleh dicoba. */
export async function printerJaringanStatus(alamat) {
  const a = alamatPrinterSah(alamat); if (!a) throw galat(KALIMAT_ALAMAT, 'SALAH_ISI');
  let r; try { r = await tanyaJaringan(a, '/cgi-bin/status.cgi', '', 6000); } catch (e) { throw galatSambungJaringan(e, a); }
  const k = bacaJawabJaringan(r && r.data);
  if (!r || r.status !== 200 || !k.dikenali) throw galat('Alamat ' + a + ' menjawab, tapi bukan seperti printer SUNMI (jawaban ' + (r ? r.status : '?') + ') — periksa alamatnya di layar Perangkat', 'BELUM_KIRIM');
  const h = halanganJaringan(k);
  return { alamat: a, keadaan: k, siap: !h, menghalangi: !!h, kalimat: h ? h.kalimat : k.belumDiambil ? 'siap (struk sebelumnya belum diambil)' : 'siap' };
}
/** Cetak lewat jaringan: tanya keadaan dulu (halangan pasti = tidak ada yang dikirim), kirim, lalu tanya pekerjaannya sampai "printed".
 *  Sesudah kiriman berangkat, apa pun yang tidak jelas = PRINTER_DIAM (hasil tidak diketahui, TANPA kirim ulang lewat jalur mana pun). */
async function cetakJaringan(data64, alamat) {
  const s = await printerJaringanStatus(alamat);
  if (s.menghalangi) throw galat('Printer belum bisa mencetak: ' + s.kalimat, halanganJaringan(s.keadaan).kode);
  let r;
  try { r = await tanyaJaringan(s.alamat, '/cgi-bin/print.cgi?copies=1', b64KeHeksa(data64), JARINGAN.bacaMs); }
  catch (e) {
    if (jenisGalatJaringan(e) !== 'takjelas') throw galatSambungJaringan(e, s.alamat);
    throw galat('Kiriman ke printer terputus di tengah jalan (' + pesanGalat(e) + ')', 'PRINTER_DIAM');
  }
  const tugas = bacaJawabJaringan(r && r.data).tugas;
  if (!r || r.status !== 200 || !/^\d+$/.test(tugas)) throw galat('Printer menerima kiriman tapi tidak memberi nomor pekerjaan (jawaban ' + (r ? r.status : '?') + ')', 'PRINTER_DIAM');
  // dua batas: jumlah tanya DAN lama menunggu — kalau printer lenyap dari jaringan tiap tanya bisa makan beberapa detik, dan seluruh cetakan
  // harus selesai (berhasil atau "lihat kertasnya") sebelum kunci satuCetakan dianggap lepas (BATAS_SIBUK_MS)
  const habisPada = Date.now() + JARINGAN.tungguMs;
  for (let i = 0; i < JARINGAN.tanyaMaks && Date.now() < habisPada; i++) {
    await jeda(JARINGAN.jedaMs);
    let k = null;
    try { const t = await tanyaJaringan(s.alamat, '/cgi-bin/status.cgi?task_id=' + tugas, '', 6000); if (t && t.status === 200) k = bacaJawabJaringan(t.data); }
    catch (e) { /* satu tanya yang gagal bukan kabar apa-apa — tanya lagi */ }
    if (!k || !k.dikenali) continue;
    if (k.tugasStatus === 'printed') return { nama: s.alamat, tugas, peringatan: '' };
    const h = halanganJaringan(k);
    if (h && !k.mencetak) throw galat('Cetak terhenti: ' + h.kalimat, h.kode);
  }
  throw galat('Printer menerima kiriman (pekerjaan ' + tugas + ') tapi belum melaporkannya tercetak', 'PRINTER_DIAM');
}

/** Keadaan printer lewat SDK SUNMI: { status, kalimat, siap, menghalangi, nama, sdk }. Menolak bila tidak bisa ditanya. lewat = 'usb' (bawaan) | 'bt'. */
export const printerStatus = (lewat) => panggilAsli('PrinterSunmi', 'status', { lewat: lewat === 'bt' ? 'bt' : 'usb' });

// ---------- printer SUNMI: Bluetooth, mode kertas, label (paket S4, 19 Nov 2026) ----------
/** Printer SUNMI yang SUDAH dipasangkan ke tablet lewat Bluetooth (Setelan tablet › Bluetooth; namanya berawalan CloudPrint_).
 *  Hasil { ada (tablet punya Bluetooth), izin, nyala, daftar: [{ nama, mac }] }. Panggilan pertama bisa memunculkan pertanyaan izin Android. */
export const printerBt = () => panggilAsli('PrinterSunmi', 'bt', {});
/** Mode kertas printer NT32x: 1 struk · 2 label bercelah · 3 stiker tanpa alas (dokumen SUNMI setPrintMode). */
export const MODE_KERTAS = [[1, 'struk (kertas bersambung)'], [2, 'label (stiker bercelah)'], [3, 'stiker tanpa alas']];
/** Jawaban printer saat ditanya modenya → 'struk' | 'label' | 'tanpa-alas' | '' (tidak dikenali / belum menjawab; teks aslinya tetap ditampilkan).
 *  Tiga jawaban ini terbaca dari printer toko (uji owner 20 Nov 2026): "Receipt printer", "label printer", "Linerless printer". */
export function bacaModeKertas(teks) {
  const t = String(teks || '').toLowerCase();
  return t.indexOf('linerless') >= 0 ? 'tanpa-alas' : t.indexOf('label') >= 0 ? 'label' : t.indexOf('receipt') >= 0 ? 'struk' : '';
}
/** Nama mode untuk layar. */
export const MODE_NAMA = { struk: 'STRUK (kertas bersambung)', label: 'LABEL (stiker bercelah)', 'tanpa-alas': 'STIKER TANPA ALAS' };
/** Kalimat hasil tanya mode untuk layar: { teks, baik }. Jawaban kosong = printer belum menjawab (uji owner: sesaat sesudah pindah mode). */
export function kalimatModeKertas(teksPrinter) {
  const asli = String(teksPrinter == null ? '' : teksPrinter).trim(); const m = bacaModeKertas(asli);
  if (!asli) return { teks: 'Printer belum menjawab modenya — biasanya masih berpindah mode; tunggu beberapa detik lalu tekan Baca mode sekarang lagi', baik: false };
  return { teks: 'Printer menjawab: ' + (m ? 'mode ' + MODE_NAMA[m] : 'tidak dikenali') + ' — "' + asli + '"', baik: !!m };
}
/** Cara label ('tspl' = bahasa label untuk stiker bercelah · selain itu bahasa struk untuk kertas bersambung) lawan mode printer.
 *  '' = boleh dikirim; selain itu kalimat tolakannya. Hanya dua pasangan yang PASTI salah yang ditolak; mode tanpa alas & mode yang tidak
 *  terbaca dibiarkan lewat (belum terbukti bahasanya). */
export function labelTolakMode(cara, mode) {
  if (cara === 'tspl' && mode === 'struk') return 'Printer sedang di mode STRUK (kertas bersambung), sedangkan label ini disusun untuk stiker bercelah — pindahkan printer ke mode label di layar Perangkat, atau ganti cara label ke "kertas bersambung"';
  if (cara !== 'tspl' && mode === 'label') return 'Printer sedang di mode LABEL (stiker bercelah), sedangkan label ini disusun untuk kertas bersambung — pindahkan printer ke mode struk di layar Perangkat, atau ganti cara label ke "stiker bercelah"';
  return '';
}
/** Tanya mode kertas printer: { mode: teks dari printer }. */
export const printerMode = (lewat) => panggilAsli('PrinterSunmi', 'mode', { lewat: lewat === 'bt' ? 'bt' : 'usb' });
/** Pindahkan mode kertas printer (1 | 2 | 3). Printer tidak mengabari hasilnya — tanyakan lagi modenya beberapa detik kemudian. */
export function printerSetelMode(mode, lewat) {
  const m = Number(mode); if (!MODE_KERTAS.some((x) => x[0] === m)) return Promise.reject(galat('Mode kertas tidak dikenal', 'SALAH_ISI'));
  // mode tidak dipindah di tengah cetakan yang belum dikabari
  if (printerSibuk()) return Promise.reject(galat(KALIMAT_MASIH_MENCETAK, 'SEDANG_CETAK'));
  return panggilAsli('PrinterSunmi', 'setelMode', { mode: m, lewat: lewat === 'bt' ? 'bt' : 'usb' });
}
/** Kirim perintah label (TSPL) ke printer yang sedang di mode label. Printer label TIDAK mengabari hasil cetak. Hasil { nama, byte }. */
export const kirimTspl = (data, lewat) => satuCetakan(() => panggilAsli('PrinterSunmi', 'tspl', { data: String(data || ''), lewat: lewat === 'bt' ? 'bt' : 'usb' }));
/** Sebelum label dikirim lewat SDK SUNMI: tanya mode printer, tolak (kode 'SALAH_MODE') bila bahasa labelnya pasti salah untuk mode itu.
 *  Uji owner 20 Nov 2026: label bahasa struk ke printer di mode label dijawab "kertas habis"; perintah label ke printer di mode struk
 *  berangkat tanpa kabar. cara 'tspl': printer HARUS bisa ditanya (galat tanya dilempar apa adanya — pintu label butuh sambungan yang sama).
 *  Cara lain: tanya yang gagal dibiarkan, supaya jalur cetak biasa tetap mencoba dan tetap bisa jatuh ke kabel. Hasil { mode, ditanya }. */
export async function pastikanModeLabel(cara, lewat) {
  // pertanyaan mode antre di belakang cetakan yang belum dikabari lalu habis waktu — ditolak di depan, bukan dibiarkan menebak
  tolakBilaSibuk();
  let mode = '';
  try { const r = await printerMode(lewat); mode = bacaModeKertas(r && r.mode); }
  catch (e) { if (cara === 'tspl') throw e; return { mode: '', ditanya: false }; }
  const tolak = labelTolakMode(cara, mode); if (tolak) throw galat(tolak, 'SALAH_MODE');
  return { mode, ditanya: true };
}
/** Mode kertas di jalur JARINGAN. Pintu jaringan printer hanya menerima cetakan dan tanya keadaan — tidak ada perintah mode — jadi mode tetap
 *  lewat SDK SUNMI: Bluetooth dulu (mati / belum dipasangkan = ditolak seketika), lalu kabel (mencari printer di USB makan 6 detik sebelum
 *  menyerah). Cara berikutnya hanya dicoba bila cara sebelumnya PASTI belum mengirim apa-apa (BELUM_KIRIM); galat lain dilempar apa adanya.
 *  Uji owner 20 Nov 2026 malam: di jalur jaringan tombol mode hanya mencari di USB dan menjawab "tidak ditemukan di USB — pastikan tercolok
 *  ke stand", padahal printernya memang tidak dicolok ke tablet.
 *  kerja(lewat) = perintah SDK-nya; hasilnya dipulangkan dengan tambahan { lewat } supaya layar bisa menyebut lewat mana. */
export const URUT_SDK_JARINGAN = ['bt', 'usb'];
export const namaLewat = (lewat) => (lewat === 'bt' ? 'Bluetooth' : 'kabel USB');
export async function lewatSdk(jalur, kerja) {
  if (jalur !== 'jaringan') { const l = lewatJalur(jalur); return Object.assign({}, await kerja(l), { lewat: l }); }
  const sebab = [];
  for (const l of URUT_SDK_JARINGAN) {
    try { return Object.assign({}, await kerja(l), { lewat: l }); }
    catch (e) { if (!(e && e.code === 'BELUM_KIRIM')) throw e; sebab.push(namaLewat(l) + ': ' + pesanGalat(e)); }
  }
  throw galat('lewat jaringan mode kertas tidak bisa diurus, jadi dicoba lewat Bluetooth dan kabel — dua-duanya belum bisa. ' + sebab.join(' · '), 'BELUM_KIRIM');
}

// ---------- scanner ----------
const _pendengarPindai = [];
let _pindaiTerpasang = false;
let _pindaiTerakhir = null;
function pasangPindai() {
  if (_pindaiTerpasang || !asliAda() || adaPlugin('Pindai') === false) return;
  _pindaiTerpasang = true;
  dengarAsli('Pindai', 'pindai', (d) => {
    if (!d || typeof d.data !== 'string' || !d.data) return;
    _pindaiTerakhir = { data: d.data, pada: Date.now() };
    _pendengarPindai.slice().forEach((f) => { try { f(_pindaiTerakhir); } catch (e) { console.error('pindai', e); } });
  });
}
/** Dengarkan hasil scan scanner bawaan: fn({ data, pada }). Hasil: fungsi pelepas. */
export function padaPindai(fn) {
  _pendengarPindai.push(fn); pasangPindai();
  return () => { const i = _pendengarPindai.indexOf(fn); if (i >= 0) _pendengarPindai.splice(i, 1); };
}
/** Hasil scan terakhir sejak halaman dibuka ({ data, pada }) atau null. */
export const pindaiTerakhir = () => _pindaiTerakhir;

// ---------- NFC (paket S2a, 19 Nov 2026) ----------
// Pembaca NFC bawaan tablet: tiap kartu / stiker yang ditempelkan = satu kejadian berisi NOMOR SERI kartu (heksadesimal). Nomor seri bisa ditiru:
// dipakai untuk mengenali (kartu pelanggan), bukan untuk membayar.
const _pendengarTempel = [];
let _tempelTerpasang = false;
let _tempelTerakhir = null;
function pasangTempel() {
  if (_tempelTerpasang || !asliAda() || adaPlugin('Nfc') === false) return;
  _tempelTerpasang = true;
  dengarAsli('Nfc', 'tempel', (d) => {
    // nomor seri kartu = 4 sampai 10 byte heksadesimal; bentuk lain dibuang
    const uid = d && typeof d.uid === 'string' ? d.uid.toUpperCase() : '';
    if (!/^(?:[0-9A-F]{2}){4,10}$/.test(uid)) return;
    _tempelTerakhir = { uid, jenis: Array.isArray(d.jenis) ? d.jenis.map(String) : [], pada: Date.now() };
    _pendengarTempel.slice().forEach((f) => { try { f(_tempelTerakhir); } catch (e) { console.error('tempel', e); } });
  });
}
/** Dengarkan kartu NFC yang ditempelkan ke tablet: fn({ uid, jenis, pada }). Hasil: fungsi pelepas. */
export function padaTempel(fn) {
  _pendengarTempel.push(fn); pasangTempel();
  return () => { const i = _pendengarTempel.indexOf(fn); if (i >= 0) _pendengarTempel.splice(i, 1); };
}
/** Kartu terakhir yang ditempelkan sejak halaman dibuka ({ uid, jenis, pada }) atau null. */
export const tempelTerakhir = () => _tempelTerakhir;

// ---------- ketikan papan fisik vs scanner (panel PIN) ----------
// Scanner bermode "ketikan" mengetik isi kode seperti papan ketik, jauh lebih cepat dari jari. Di panel PIN ketikan seperti itu dulu
// terbaca sebagai PIN salah (5 kali = nama terkunci 5 menit). Ketikan papan fisik karena itu DITAMPUNG sebentar: beruntun secepat mesin = dibuang.
export const KETIK_JEDA_MESIN = 35;   // ms antara dua ketukan: di bawah ini bukan jari
export const KETIK_MESIN_MIN = 3;     // sekian ketukan berturut-turut secepat itu = scanner
export const KETIK_TUNGGU = 80;       // ms diam sebelum tampungan diteruskan ke PIN
/** Tampungan baru sesudah satu ketukan (tidak mengubah masukan). t = saat ketukan TERJADI (ev.timeStamp), bukan saat diproses. */
export function ketikTambah(tampung, k, t) { return (tampung || []).concat([{ k: String(k), t: Number(t) || 0 }]); }
/** Tampungan ini ketikan mesin? */
export function ketikMesin(tampung) {
  let beruntun = 1;
  for (let i = 1; i < (tampung || []).length; i++) {
    if (tampung[i].t - tampung[i - 1].t < KETIK_JEDA_MESIN) { beruntun += 1; if (beruntun >= KETIK_MESIN_MIN) return true; } else beruntun = 1;
  }
  return false;
}

// ---------- lampu ----------
// Paket S4 (owner 19 Nov 2026: "lampu led indikator bisa diubah untuk sistem ini, gak hanya hijau dan merah"): tiap KEJADIAN punya warna, kedip,
// dan lama nyala sendiri — diatur per perangkat di layar Perangkat (uji-cetak.html), disimpan di localStorage perangkat ini (bukan data toko).
export const LAMPU_WARNA = { merah: 1, hijau: 2, biru: 3, kuning: 4, sian: 5, magenta: 6, putih: 7 };
export const LAMPU_KUNCI = 'lampuPerangkat';
export const LAMPU_MATI = 'mati';   // kejadian ini tidak menyalakan lampu
/** [kunci, nama di layar, bawaan { warna, kedip, detik }]. */
export const LAMPU_KEJADIAN = [
  ['berhasil', 'Nota tersimpan', { warna: 'hijau', kedip: false, detik: 1.5 }],
  ['gagal', 'Cetak gagal atau perlu dilihat', { warna: 'merah', kedip: true, detik: 6 }],
  ['kenal', 'Barcode, kartu, atau struk dikenali', { warna: 'biru', kedip: false, detik: 1 }],
  ['asing', 'Barcode atau kartu belum dikenal', { warna: 'kuning', kedip: true, detik: 3 }],
  ['kertas', 'Kertas printer hampir habis', { warna: 'magenta', kedip: true, detik: 4 }],
];
const LAMPU_DETIK = [0.5, 10];
function simpananLampu() { try { return typeof localStorage === 'undefined' ? null : JSON.parse(localStorage.getItem(LAMPU_KUNCI) || 'null'); } catch (e) { return null; } }
/** Setelan lampu perangkat ini: { kejadian: { warna, kedip, detik } } — bawaan ditimpa yang tersimpan; isi yang tidak sah dibuang satu per satu. */
export function lampuAtur(simpanan) {
  const d = (simpanan === undefined ? simpananLampu() : simpanan) || {}; const a = {};
  LAMPU_KEJADIAN.forEach((k) => {
    const b = Object.assign({}, k[2]); const x = d[k[0]] && typeof d[k[0]] === 'object' ? d[k[0]] : {};
    if (x.warna === LAMPU_MATI || LAMPU_WARNA[x.warna]) b.warna = x.warna;
    if (typeof x.kedip === 'boolean') b.kedip = x.kedip;
    if (typeof x.detik === 'number' && x.detik >= LAMPU_DETIK[0] && x.detik <= LAMPU_DETIK[1]) b.detik = x.detik;
    a[k[0]] = b;
  });
  return a;
}
export function lampuSimpan(a) { try { localStorage.setItem(LAMPU_KUNCI, JSON.stringify(lampuAtur(a))); return true; } catch (e) { return false; } }
let _lampuMati = false;   // aplikasi ini terbukti tidak punya plugin Lampu → berhenti memanggil
/** Nyalakan lampu perangkat. Tidak pernah melempar: tanpa lampu = { ok: false }. o = { kedip, nyalaMs, matiMs, batasMs }. */
export function lampu(warna, o) {
  if (_lampuMati || !asliAda() || adaPlugin('Lampu') === false) return Promise.resolve({ ok: false });
  const isi = Object.assign({ warna: LAMPU_WARNA[warna] || LAMPU_WARNA.hijau, kedip: false, batasMs: 2000 }, o || {});
  return panggilAsli('Lampu', 'nyala', isi).then((r) => r || { ok: false }).catch(() => { _lampuMati = true; return { ok: false }; });
}
export function lampuPadam() {
  if (_lampuMati || !asliAda() || adaPlugin('Lampu') === false) return Promise.resolve({ ok: false });
  return panggilAsli('Lampu', 'mati', {}).then((r) => r || { ok: false }).catch(() => ({ ok: false }));
}
/** Nyalakan lampu untuk satu kejadian menurut setelan perangkat ini (atau `timpa` = { warna, kedip, detik } untuk tombol Coba). Tidak pernah melempar. */
export function lampuKejadian(nama, timpa) {
  const a = Object.assign({}, lampuAtur()[nama], timpa || {});
  if (!a.warna || a.warna === LAMPU_MATI || !LAMPU_WARNA[a.warna]) return Promise.resolve({ ok: false, mati: true });
  return lampu(a.warna, { kedip: !!a.kedip, nyalaMs: 250, matiMs: 250, batasMs: Math.round((Number(a.detik) || 1.5) * 1000) });
}
/** Nota tersimpan (bawaan: hijau sebentar). */
export const lampuBerhasil = () => lampuKejadian('berhasil');
/** Cetak gagal / perlu perhatian (bawaan: merah berkedip beberapa detik). */
export const lampuGagal = () => lampuKejadian('gagal');
/** Barcode / kartu / struk dikenali (bawaan: biru sebentar). */
export const lampuKenal = () => lampuKejadian('kenal');
/** Barcode / kartu belum dikenal (bawaan: kuning berkedip). */
export const lampuAsing = () => lampuKejadian('asing');
/** Kertas printer hampir habis (bawaan: magenta berkedip). */
export const lampuKertas = () => lampuKejadian('kertas');

// ---------- sidik jari (paket S4): owner 19 Nov 2026 — "periksa sensornya dulu"; pemakaiannya diputuskan sesudah terbukti ada ----------
/** { ada, terdaftar, kode, kalimat } menurut Android (BiometricManager). Menolak bila aplikasi ini belum punya bagian sidik jari. */
export const sidikJariInfo = () => panggilAsli('Biometrik', 'info', {});
/** Minta satu kali tempel jari (dialog Android). Lulus = { ok: true }; batal / gagal = menolak dengan kalimat dari Android. */
export const sidikJariUji = () => panggilAsli('Biometrik', 'minta', { judul: 'Uji sidik jari', ket: 'Tempelkan jari yang sudah didaftarkan di tablet ini' });
/** Tolakan uji sidik jari (kode BIOMETRIK_<angka Android>) → { batal, kalimat }. batal = orangnya sendiri yang menutup, bukan kegagalan.
 *  Angka = BiometricPrompt.ERROR_*: 5 dibatalkan sistem · 10 dibatalkan orang · 13 tombol Batal · 3 kehabisan waktu · 7/9 terkunci ·
 *  11 belum ada jari terdaftar · 1/12 sensor tidak ada / tidak bisa dipakai. */
export function sidikJariTolak(e) {
  const kode = String((e && e.code) || ''); const n = /^BIOMETRIK_(\d+)$/.test(kode) ? Number(kode.slice(10)) : -1;
  if (n === 5 || n === 10 || n === 13) return { batal: true, kalimat: 'uji dibatalkan' };
  if (n === 3) return { batal: false, kalimat: 'tidak ada jari yang ditempelkan sampai waktunya habis' };
  if (n === 7) return { batal: false, kalimat: 'terlalu banyak percobaan gagal — tunggu sekitar 30 detik lalu coba lagi' };
  if (n === 9) return { batal: false, kalimat: 'sensor terkunci karena terlalu banyak percobaan gagal — buka kunci tablet dengan PIN/pola dulu' };
  if (n === 11) return { batal: false, kalimat: 'belum ada jari yang didaftarkan di Setelan tablet' };
  if (n === 1 || n === 12) return { batal: false, kalimat: 'sensor sidik jari tidak ada atau sedang tidak bisa dipakai' };
  return { batal: false, kalimat: (e && e.message) ? String(e.message) : String(e) };
}

// ---------- kartu kemampuan (layar diagnosis) ----------
/** Ringkasan apa yang ada di perangkat ini. Tidak pernah melempar. */
export async function kemampuan() {
  const k = { aplikasi: asliAda(), plugin: {}, info: null, lampu: null, pindai: null, nfc: null, biometrik: null };
  if (!k.aplikasi) return k;
  ['CetakUsb', 'PrinterSunmi', 'Pindai', 'Lampu', 'Perangkat', 'Nfc', 'Biometrik'].forEach((n) => { k.plugin[n] = adaPlugin(n); });
  const coba = (plugin, metode) => (k.plugin[plugin] === false ? Promise.resolve(null) : panggilAsli(plugin, metode, {}).catch(() => null));
  [k.info, k.lampu, k.pindai, k.nfc, k.biometrik] = await Promise.all([coba('Perangkat', 'info'), coba('Lampu', 'dukung'), coba('Pindai', 'info'), coba('Nfc', 'info'), coba('Biometrik', 'info')]);
  return k;
}
