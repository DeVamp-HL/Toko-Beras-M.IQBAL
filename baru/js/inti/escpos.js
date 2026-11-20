// ESC/POS (putaran T1 — tablet Sunmi CPad + printer 80 mm linerless lewat USB stand, Nov 2026) — penyusun byte TANPA DOM & tanpa impor.
// Masukan = `garis` dari susunStruk() (struk-logika.js: [{kiri, kanan, tebal, tengah} | {garis: true}]) — struk tetap hanya menyusun nota yang
// tersimpan, berkas ini cuma mengubah wujudnya jadi perintah printer. Tidak ada angka baru di sini.
// Lebar: 80 mm = 576 titik = 48 kolom huruf A (12×24); 58 mm = 384 titik = 32 kolom. Teks diubah ke ASCII (printer memakai halaman kode
// PC437; tanda seperti "·", "×", "−", emoji tidak bisa dicetak apa adanya). Lantai Chrome 80: tanpa ??= .at( replaceAll dsb.

export const EP_KOLOM = { 58: 32, 80: 48 };
export const EP_POTONG = [['sebagian', 'potong sebagian'], ['penuh', 'potong penuh'], ['tidak', 'tanpa potong (sobek)']];

const ESC = 0x1b, GS = 0x1d, LF = 0x0a;

// tanda yang sering muncul di struk toko → padanan ASCII; sisanya: huruf beraksen dilepas aksennya, yang tidak dikenal dibuang
const PADANAN = { '·': '-', '•': '-', '×': 'x', '−': '-', '–': '-', '—': '-', '‘': "'", '’': "'", '“': '"', '”': '"', '…': '...', '→': '->',
  '←': '<-', '±': '+/-', '½': '1/2', '¼': '1/4', '¾': '3/4', '\u00a0': ' ', '\u202f': ' ', '°': ' derajat' };
// Emoji & simbol bergambar (termasuk penyambung ZWJ, pemilih varian, warna kulit, bendera). Gaya gambar: emoji berwarna jadi bintik acak
// sesudah dijadikan hitam-putih (uji cetak owner 16 Nov); gaya teks: printer tidak punya hurufnya. Panah, ©, ®, ™, huruf beraksen TIDAK kena.
const EMOJI = /[\u{1F000}-\u{1FAFF}\u{2300}-\u{23FF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE00}-\u{FE0F}\u{200D}\u{20E3}\u{E0020}-\u{E007F}]/gu;
/** Buang emoji saja — spasi tidak diubah (baris teks yang sudah diratakan & data QR tetap utuh; pembungkus kata merapatkan spasi sendiri). */
export function epTanpaEmoji(s) {
  return String(s === undefined || s === null ? '' : s).replace(EMOJI, '');
}
/** Teks → hanya ASCII cetak (0x20–0x7E). */
export function epAscii(s) {
  const t = epTanpaEmoji(s);
  let out = '';
  for (let i = 0; i < t.length; i++) {
    const c = t.charAt(i); const k = c.charCodeAt(0);
    if (k >= 0x20 && k <= 0x7e) { out += c; continue; }
    if (PADANAN[c] !== undefined) { out += PADANAN[c]; continue; }
    if (k >= 0xd800 && k <= 0xdbff) { i++; continue; }   // pasangan surrogate (emoji) dibuang utuh
    const lepas = c.normalize ? c.normalize('NFD').replace(/[̀-ͯ]/g, '') : '';
    if (lepas && /^[\x20-\x7e]+$/.test(lepas)) { out += lepas; continue; }
    if (k === 0x09) out += ' ';
  }
  return out.replace(/\s+$/, '');
}

/** Pecah teks per kata ke baris selebar `lebar` (kata yang lebih panjang dari baris dipotong paksa). */
export function epBungkus(teks, lebar) {
  const kata = epAscii(teks).split(/ +/).filter((x) => x !== ''); const hasil = []; let baris = '';
  kata.forEach((k) => {
    while (k.length > lebar) { if (baris) { hasil.push(baris); baris = ''; } hasil.push(k.slice(0, lebar)); k = k.slice(lebar); }
    if (!k) return;
    if (!baris) baris = k; else if (baris.length + 1 + k.length <= lebar) baris += ' ' + k; else { hasil.push(baris); baris = k; }
  });
  if (baris || !hasil.length) hasil.push(baris);
  return hasil;
}

/** Satu baris struk → baris teks selebar kolom. kanan menempel di kanan baris terakhir; kalau tidak muat, kanan turun ke baris sendiri. */
export function epSusunBaris(kiri, kanan, lebar) {
  const ka = epAscii(kanan); const ki = epBungkus(kiri, lebar);
  if (!ka) return ki;
  if (ka.length >= lebar) return ki.concat(epBungkus(ka, lebar));
  const akhir = ki[ki.length - 1];
  if (akhir.length + 1 + ka.length <= lebar) { ki[ki.length - 1] = akhir + new Array(lebar - akhir.length - ka.length + 1).join(' ') + ka; return ki; }
  return ki.concat([new Array(lebar - ka.length + 1).join(' ') + ka]);
}

function Penulis() {
  const b = [];
  const ini = {
    byte: (...x) => { x.forEach((v) => b.push(v & 0xff)); return ini; },
    teks: (s) => { const t = epAscii(s); for (let i = 0; i < t.length; i++) b.push(t.charCodeAt(i)); return ini; },
    baris: (s) => ini.teks(s).byte(LF),
    hasil: () => Uint8Array.from(b),
  };
  return ini;
}

/** QR (GS ( k model 2). data ASCII; ukuran modul 1–16. */
function tulisQr(w, data, ukuran) {
  const d = epAscii(data); const n = d.length + 3;
  w.byte(GS, 0x28, 0x6b, 0x04, 0x00, 0x31, 0x41, 0x32, 0x00)                 // model 2
    .byte(GS, 0x28, 0x6b, 0x03, 0x00, 0x31, 0x43, Math.max(1, Math.min(16, ukuran || 6)))   // ukuran modul
    .byte(GS, 0x28, 0x6b, 0x03, 0x00, 0x31, 0x45, 0x31)                       // koreksi galat M
    .byte(GS, 0x28, 0x6b, n & 0xff, (n >> 8) & 0xff, 0x31, 0x50, 0x30).teks(d) // simpan data
    .byte(GS, 0x28, 0x6b, 0x03, 0x00, 0x31, 0x51, 0x30);                      // cetak
}

/**
 * Susun byte ESC/POS dari garis struk.
 * opsi: { kertas: 80|58 (bawaan 80), potong: 'sebagian'|'penuh'|'tidak' (bawaan sebagian), umpan: baris kosong sebelum potong (bawaan 4),
 *         qr: teks QR di bawah struk (opsional), laci: true = buka laci uang (pulsa ESC p) }
 * Hasil: { byte: Uint8Array, teks: baris-baris yang tercetak (untuk pratinjau & uji), lebar }.
 */
export function epSusun(garis, opsi) {
  const o = opsi || {}; const lebar = EP_KOLOM[o.kertas] || EP_KOLOM[80];
  const w = Penulis(); const teks = [];
  w.byte(ESC, 0x40).byte(ESC, 0x74, 0x00);   // mulai ulang printer · halaman kode PC437
  (garis || []).forEach((g) => {
    if (!g) return;
    if (g.garis) { const s = new Array(lebar + 1).join('-'); w.byte(ESC, 0x61, 0).baris(s); teks.push(s); return; }
    w.byte(ESC, 0x61, g.tengah ? 1 : 0).byte(ESC, 0x45, g.tebal ? 1 : 0);
    const isi = g.tengah && !g.kanan ? epBungkus(g.kiri, lebar) : epSusunBaris(g.kiri, g.kanan, lebar);
    isi.forEach((s) => { w.baris(s); teks.push(g.tengah ? new Array(Math.floor((lebar - s.length) / 2) + 1).join(' ') + s : s); });
    if (g.tebal) w.byte(ESC, 0x45, 0);
  });
  w.byte(ESC, 0x61, 0);
  tutup(w, o, teks);
  return { byte: w.hasil(), teks, lebar };
}

/** Ekor bersama struk teks & gambar: QR (opsional) · umpan · potong · pulsa laci (opsional). */
function tutup(w, o, teks) {
  const potong = EP_POTONG.some((x) => x[0] === o.potong) ? o.potong : 'sebagian';
  const umpan = Math.max(0, Math.min(10, o.umpan === undefined ? 4 : Number(o.umpan) || 0));
  if (o.qr) { w.byte(ESC, 0x61, 1); tulisQr(w, o.qr, o.qrUkuran); w.byte(LF).byte(ESC, 0x61, 0); if (teks) teks.push('[QR ' + epAscii(o.qr) + ']'); }
  w.byte(ESC, 0x64, umpan);
  if (potong === 'penuh') w.byte(GS, 0x56, 0x41, 0x00); else if (potong === 'sebagian') w.byte(GS, 0x56, 0x42, 0x00);
  if (o.laci) w.byte(ESC, 0x70, 0x00, 0x19, 0xfa);
}

// ---------- gaya GAMBAR (T1 langkah 2): struk digambar di kanvas (huruf toko, ukuran bebas, logo) lalu dicetak sebagai raster ----------
// 80 mm = 576 titik selebar kertas cetak (203 dpi); 58 mm = 384. Bagian DOM (menggambar kanvas) ada di struk-kanvas.js; di sini hanya
// hitungan murni supaya bisa diuji di jsc.
export const EP_TITIK = { 58: 384, 80: 576 };
const PITA = 240;   // baris raster per perintah GS v 0 (buffer printer kecil aman)

/**
 * RGBA (ImageData.data) → bit 1 = hitam, 0 = putih, baris demi baris. Piksel transparan dianggap putih.
 * opsi.dither = true → Floyd–Steinberg (logo/foto: gradasi jadi titik); selain itu ambang tunggal (teks tajam), opsi.ambang bawaan 160.
 */
export function epHitamPutih(rgba, lebar, tinggi, opsi) {
  const o = opsi || {}; const ambang = o.ambang === undefined ? 160 : Number(o.ambang);
  const n = lebar * tinggi; const abu = new Float32Array(n); const bit = new Uint8Array(n);
  for (let i = 0; i < n; i++) {
    const a = rgba[i * 4 + 3] / 255; const l = 0.299 * rgba[i * 4] + 0.587 * rgba[i * 4 + 1] + 0.114 * rgba[i * 4 + 2];
    abu[i] = 255 - a * (255 - l);
  }
  if (!o.dither) { for (let i = 0; i < n; i++) bit[i] = abu[i] < ambang ? 1 : 0; return bit; }
  for (let y = 0; y < tinggi; y++) {
    for (let x = 0; x < lebar; x++) {
      const i = y * lebar + x; const lama = abu[i]; const baru = lama < 128 ? 0 : 255; bit[i] = baru === 0 ? 1 : 0; const e = lama - baru;
      if (x + 1 < lebar) abu[i + 1] += e * 7 / 16;
      if (y + 1 < tinggi) { if (x > 0) abu[i + lebar - 1] += e * 3 / 16; abu[i + lebar] += e * 5 / 16; if (x + 1 < lebar) abu[i + lebar + 1] += e / 16; }
    }
  }
  return bit;
}

/** Bit (lebar × tinggi, 1 = hitam) → perintah GS v 0 per pita PITA baris. Bit pertama tiap byte = titik paling kiri. */
export function epRaster(bit, lebar, tinggi) {
  const bpr = Math.ceil(lebar / 8); const w = Penulis();
  for (let y0 = 0; y0 < tinggi; y0 += PITA) {
    const t = Math.min(PITA, tinggi - y0);
    w.byte(GS, 0x76, 0x30, 0x00, bpr & 0xff, (bpr >> 8) & 0xff, t & 0xff, (t >> 8) & 0xff);
    for (let y = y0; y < y0 + t; y++) {
      for (let b = 0; b < bpr; b++) {
        let v = 0;
        for (let k = 0; k < 8; k++) { const x = b * 8 + k; if (x < lebar && bit[y * lebar + x]) v |= 0x80 >> k; }
        w.byte(v);
      }
    }
  }
  return w.hasil();
}

/** Struk gaya gambar: gambar = { bit, lebar, tinggi } (dari struk-kanvas.js). opsi sama dengan epSusun (qr, potong, umpan, laci). */
export function epSusunGambar(gambar, opsi) {
  const o = opsi || {}; const w = Penulis();
  w.byte(ESC, 0x40).byte(ESC, 0x61, 1);
  const kepala = 5;   // ESC @ (2 byte) + ESC a 1 (3 byte)
  const r = epRaster(gambar.bit, gambar.lebar, gambar.tinggi); for (let i = 0; i < r.length; i++) w.byte(r[i]);
  w.byte(ESC, 0x61, 0);
  tutup(w, o, null);
  // batas = tempat kiriman boleh dipotong: tepat sesudah tiap pita gambar kecuali yang terakhir (tiap pita = 8 byte kepala GS v 0 + isinya).
  // Potong pertama membawa kepala struk, potong terakhir membawa QR / umpan / potong kertas. Dipakai jalur Bluetooth "kirim per potong".
  const bpr = Math.ceil(gambar.lebar / 8); const batas = []; let pos = kepala;
  for (let y0 = 0; y0 < gambar.tinggi; y0 += PITA) { pos += 8 + bpr * Math.min(PITA, gambar.tinggi - y0); if (y0 + PITA < gambar.tinggi) batas.push(pos); }
  return { byte: w.hasil(), lebar: gambar.lebar, tinggi: gambar.tinggi, batas };
}
/** Potong satu kiriman di `batas` (letak byte, menaik). Hasil: larik Uint8Array yang bila disambung = kiriman asli. Batas yang tidak sah diabaikan. */
export function epPotong(byte, batas) {
  const hasil = []; let dari = 0;
  (Array.isArray(batas) ? batas : []).forEach((b) => { if (Number.isInteger(b) && b > dari && b < byte.length) { hasil.push(byte.subarray(dari, b)); dari = b; } });
  hasil.push(byte.subarray(dari));
  return hasil;
}

// ---------- LABEL barang (paket S4, 19 Nov 2026): tanda kenal untuk ditempel di kemasan ----------
// Printer toko (SUNMI NT32x) punya tiga mode kertas. Mode STRUK dan TANPA ALAS = kertas bersambung → label dikirim sebagai ESC/POS (epSusunLabel).
// Mode LABEL = stiker bercelah → printer hanya mengerti TSPL (epTsplLabel; dokumen SUNMI "Label Printer TSPL Command Set", 203 dpi: 1 mm = 8 titik).
// isi = { judul (nama barang), ket (baris kecil), kode (isi QR, yang dibaca scanner), teksKode (kode yang dibaca orang) }.
const bulat = (v, min, maks, bawaan) => { const n = Math.floor(Number(v)); return Number.isFinite(n) ? Math.max(min, Math.min(maks, n)) : bawaan; };
export const EP_LABEL_MAKS = 50;

/** Label di kertas bersambung: nama barang besar, baris kecil, QR, kode — lalu potong; diulang `jumlah` kali (tiap lembar dipotong sendiri).
 *  opsi: { kertas, potong, umpan, qrUkuran, jumlah }. Hasil { byte, teks (satu lembar, untuk pratinjau & uji), jumlah }. */
export function epSusunLabel(isi, opsi) {
  const o = opsi || {}; const x = isi || {}; const lebar = EP_KOLOM[o.kertas] || EP_KOLOM[80]; const w = Penulis(); const teks = [];
  const n = bulat(o.jumlah, 1, EP_LABEL_MAKS, 1);
  const judul = epBungkus(x.judul || '', Math.floor(lebar / 2)).filter((s) => s !== '').slice(0, 3);
  const ket = x.ket ? epBungkus(x.ket, lebar).slice(0, 1) : [];
  for (let i = 0; i < n; i++) {
    w.byte(ESC, 0x40).byte(ESC, 0x74, 0x00).byte(ESC, 0x61, 1);
    // GS ! 0x11 = huruf dua kali lebar & tinggi (nama barang terbaca dari jauh); dikembalikan sebelum baris kecil
    w.byte(GS, 0x21, 0x11).byte(ESC, 0x45, 1); judul.forEach((s) => { w.baris(s); if (!i) teks.push(s); });
    w.byte(GS, 0x21, 0x00).byte(ESC, 0x45, 0);
    ket.forEach((s) => { w.baris(s); if (!i) teks.push(s); });
    if (x.kode) { tulisQr(w, x.kode, o.qrUkuran || 6); w.byte(LF); if (!i) teks.push('[QR ' + epAscii(x.kode) + ']'); }
    if (x.teksKode) { w.baris(x.teksKode); if (!i) teks.push(epAscii(x.teksKode)); }
    w.byte(ESC, 0x61, 0);
    tutup(w, { potong: o.potong, umpan: o.umpan }, null);
  }
  return { byte: w.hasil(), teks, jumlah: n };
}

/** Label di stiker bercelah: perintah TSPL. opsi: { lebarMm (20–80), tinggiMm (15–200), celahMm (0–10; 0 = tanpa celah), jumlah, potong (true = potong
 *  sesudah lembar terakhir) }. Hasil { teks (perintah, satu per baris), byte, jumlah, lebarMm, tinggiMm, celahMm }.
 *  Tata letak: nama barang di atas (huruf 12×24 diperbesar bila muat), QR kiri-bawah, kode & baris kecil di kanannya. */
export function epTsplLabel(isi, opsi) {
  const o = opsi || {}; const x = isi || {};
  const lb = bulat(o.lebarMm, 20, 80, 50); const tg = bulat(o.tinggiMm, 15, 200, 30); const celah = bulat(o.celahMm, 0, 10, 2); const n = bulat(o.jumlah, 1, EP_LABEL_MAKS, 1);
  const W = lb * 8; const tepi = 16;
  const kutip = (s) => epAscii(s).replace(/["\\]/g, "'");   // tanda kutip mengakhiri isi perintah
  const besar = W >= 400 ? 2 : 1;                              // label ≥ 50 mm: nama barang dua kali lebih besar
  const kolom = Math.max(6, Math.floor((W - 2 * tepi) / (12 * besar)));
  const judul = epBungkus(x.judul || '', kolom).filter((s) => s !== '').slice(0, tg >= 40 ? 3 : 2);
  const baris = ['SIZE ' + lb + ' mm,' + tg + ' mm', 'GAP ' + celah + ' mm,0 mm', 'DIRECTION 1', 'CLS'];
  let y = tepi;
  judul.forEach((s) => { baris.push('TEXT ' + tepi + ',' + y + ',"0",0,' + besar + ',' + besar + ',"' + kutip(s) + '"'); y += 24 * besar + 6; });
  y += 4;
  if (x.kode) baris.push('QRCODE ' + tepi + ',' + y + ',M,4,A,0,"' + kutip(x.kode) + '"');
  // QR 4 titik per modul: kode sampai 64 huruf ≤ 41 modul = 164 titik → teks mulai di kanan lebar itu
  const xTeks = tepi + 164 + 12;
  if (x.teksKode && xTeks + 12 * 6 <= W) baris.push('TEXT ' + xTeks + ',' + y + ',"0",0,1,1,"' + kutip(x.teksKode) + '"');
  if (x.ket && xTeks + 8 * 8 <= W) baris.push('TEXT ' + xTeks + ',' + (y + 34) + ',"1",0,1,1,"' + kutip(x.ket).slice(0, Math.max(0, Math.floor((W - xTeks - tepi) / 8))) + '"');
  baris.push('PRINT ' + n); if (o.potong) baris.push('CUT');
  const teks = baris.join('\n') + '\n'; const w = Penulis();
  for (let i = 0; i < teks.length; i++) w.byte(teks.charCodeAt(i));
  return { teks: baris, byte: w.hasil(), jumlah: n, lebarMm: lb, tinggiMm: tg, celahMm: celah };
}

/** Byte → base64 (untuk jembatan aplikasi Android). Dipotong per 32 KB supaya String.fromCharCode tidak kehabisan tumpukan. */
export function epBase64(byte) {
  let s = '';
  for (let i = 0; i < byte.length; i += 32768) s += String.fromCharCode.apply(null, Array.prototype.slice.call(byte.subarray(i, i + 32768)));
  return btoa(s);
}

/** Struk contoh untuk halaman uji cetak — angka CONTOH HITUNG, bukan angka toko. */
export function epContohGaris() {   // owner 17 Nov: baris bertanda `jenis` → contoh tercetak bergaya Sertifikat seperti nota sungguhan
  return [
    { kiri: 'TOKO BERAS M.IQBAL', kanan: '', tebal: true, tengah: true, jenis: 'kop' },
    { kiri: 'Uji cetak printer · bukan nota', kanan: '', tengah: true, jenis: 'alamat' },
    { garis: true },
    { kiri: 'Nota No. 123456', kanan: '', jenis: 'nota', nilai: '123456' },
    { kiri: 'Senin, 16 Nov 2026 · 09.30', kanan: '', jenis: 'tanggal', nilai: 'Senin, 16 Nov 2026 · 09.30' },
    { kiri: 'Pembeli: Contoh pembeli', kanan: '', jenis: 'pembeli', nilai: 'Contoh pembeli' },
    { kiri: 'Dilayani: Karyawan contoh', kanan: '', jenis: 'pelayan', nilai: 'Karyawan contoh' },
    { garis: true },
    { kiri: 'Beras contoh kemasan 5 kg', kanan: '', jenis: 'barang' },
    { kiri: '  2 kemasan × 70.000', kanan: 'Rp140.000', jenis: 'rinci', jumlah: true },
    { kiri: 'Literan contoh dengan nama barang yang sangat panjang sekali untuk uji bungkus', kanan: 'Rp13.000', jenis: 'barang' },
    { garis: true },
    { kiri: 'TOTAL', kanan: 'Rp153.000', tebal: true, jenis: 'total' },
    { kiri: 'Tunai', kanan: 'Rp200.000', jenis: 'bayar' },
    { kiri: 'Kembali', kanan: 'Rp47.000', jenis: 'bayar' },
    { garis: true },
    { kiri: 'Huruf khusus: · × − – é ñ 🙏 (emoji tidak dicetak)', kanan: '', jenis: 'catatan' },
    { kiri: 'Terima kasih', kanan: '', tengah: true, jenis: 'kaki' },
  ];
}
