#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_escpos.py — penyusun ESC/POS (putaran T1, baru/js/inti/escpos.js) dijalankan ASLI di jsc, tanpa printer.

Membuktikan:
  · teks ke printer hanya ASCII cetak (· × − → padanan, aksen dilepas, emoji dibuang)
  · tiap baris tercetak ≤ lebar kertas (80 mm = 48, 58 mm = 32 kolom); angka kanan menempel persis di tepi kanan
  · nama barang panjang dibungkus per kata, angka kanannya tidak hilang
  · byte: mulai dengan ESC @, potong sebagian = GS V 66 0, penuh = GS V 65 0, "tanpa potong" = tidak ada GS V
  · QR: panjang data di perintah simpan (pL pH) = panjang data + 3
  · struk contoh: baris TOTAL berakhiran rupiahnya
  · gaya gambar: hitam-putih (ambang & dither, transparan = putih), raster GS v 0 per pita, bit kiri = MSB, base64 untuk aplikasi
  · emoji dibuang (ZWJ, varian, warna kulit, bendera ikut) tanpa menyentuh spasi, ©®™ panah & aksen

    python3 alat-uji/uji_escpos.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_escpos.py --kontrol  → tiap salinan rusak WAJIB gagal; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, sys, json, subprocess, tempfile

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BERKAS = os.path.join(AKAR, 'baru', 'js', 'inti', 'escpos.js')
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'

PEMERIKSA = r"""
if (typeof btoa !== 'function') { globalThis.btoa = (s) => { const T = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'; let o = ''; for (let i = 0; i < s.length; i += 3) { const a = s.charCodeAt(i), b = s.charCodeAt(i + 1), c = s.charCodeAt(i + 2); const n = (a << 16) | ((b || 0) << 8) | (c || 0); o += T[n >> 18 & 63] + T[n >> 12 & 63] + (i + 1 < s.length ? T[n >> 6 & 63] : '=') + (i + 2 < s.length ? T[n & 63] : '='); } return o; }; }
const hasil = [];
const cek = (nama, ok, ket) => hasil.push({ nama, ok: !!ok, ket: ket === undefined ? '' : String(ket) });
const ascii = (s) => /^[\x20-\x7e]*$/.test(s);

cek('ascii: titik tengah jadi -', epAscii('a · b') === 'a - b', epAscii('a · b'));
cek('ascii: kali jadi x', epAscii('2 × 3') === '2 x 3', epAscii('2 × 3'));
cek('ascii: minus rupiah jadi -', epAscii('−Rp500') === '-Rp500', epAscii('−Rp500'));
cek('ascii: aksen dilepas', epAscii('café') === 'cafe', epAscii('café'));
cek('ascii: emoji dibuang', epAscii('Terima kasih 🙏') === 'Terima kasih', JSON.stringify(epAscii('Terima kasih 🙏')));
cek('ascii: huruf di luar BMP (bukan emoji) tetap dibuang', epAscii('𝐀bc') === 'bc', JSON.stringify(epAscii('𝐀bc')));
cek('ascii: spasi baris rata tidak diubah', epAscii('Beras       Rp10.000') === 'Beras       Rp10.000');

// ---- buang emoji (gaya gambar & teks; poles sesudah uji cetak 16 Nov) ----
const te = (s, harap) => cek('tanpa emoji: ' + JSON.stringify(s), epTanpaEmoji(s) === harap, JSON.stringify(epTanpaEmoji(s)));
te('Terima kasih 🙏', 'Terima kasih ');
te('Bu Ani 👩‍🌾 langganan', 'Bu Ani  langganan');
te('  2 kemasan ☕️ × 3', '  2 kemasan  × 3');
te('Bendera 🇮🇩 ok 👍🏽', 'Bendera  ok ');
te('jam ⏰ ⭐ ✅', 'jam   ');
te('© ® ™ → ← é ñ · × − Rp1.000', '© ® ™ → ← é ñ · × − Rp1.000');
te(null, '');


[80, 58].forEach((k) => {
  const L = EP_KOLOM[k];
  const r = epSusun(epContohGaris(), { kertas: k });
  cek(k + ' mm: lebar kolom', r.lebar === (k === 80 ? 48 : 32), r.lebar);
  const lewat = r.teks.filter((s) => s.length > L && s.indexOf('[QR') !== 0);
  cek(k + ' mm: tiap baris ≤ ' + L + ' kolom', lewat.length === 0, lewat.join(' | '));
  cek(k + ' mm: teks pratinjau ASCII', r.teks.every(ascii), r.teks.filter((s) => !ascii(s)).join(' | '));
  const total = r.teks.filter((s) => /^TOTAL/.test(s));
  cek(k + ' mm: TOTAL menempel kanan', total.length === 1 && total[0].length === L && /Rp153\.000$/.test(total[0]), JSON.stringify(total));
  const panjang = r.teks.filter((s) => /Rp13\.000$/.test(s));
  cek(k + ' mm: nama panjang dibungkus, angkanya tetap', panjang.length === 1 && r.teks.some((s) => /^Literan contoh/.test(s)), JSON.stringify(panjang));
});

const sb = epSusunBaris('Beras', 'Rp10.000', 20);
cek('susun baris: tepat 20 kolom', sb.length === 1 && sb[0] === 'Beras       Rp10.000', JSON.stringify(sb));
const turun = epSusunBaris('1234567890123456', 'Rp10.000', 20);
cek('susun baris: kanan tidak muat → baris sendiri rata kanan', turun.length === 2 && turun[1] === '            Rp10.000', JSON.stringify(turun));
const bk = epBungkus('aaaaaaaaaaaaaaaaaaaaaaaaa bb', 10);
cek('bungkus: kata terlalu panjang dipotong', bk.every((s) => s.length <= 10) && bk.join('') .replace(/ /g, '') === 'aaaaaaaaaaaaaaaaaaaaaaaaabb', JSON.stringify(bk));

const arr = (u) => Array.prototype.slice.call(u);
const cari = (u, pola) => { const a = arr(u); for (let i = 0; i + pola.length <= a.length; i++) { let ok = true; for (let j = 0; j < pola.length; j++) if (a[i + j] !== pola[j]) { ok = false; break; } if (ok) return i; } return -1; };
const g = [{ kiri: 'X', kanan: '' }];
const sebagian = epSusun(g, {}).byte, penuh = epSusun(g, { potong: 'penuh' }).byte, tanpa = epSusun(g, { potong: 'tidak' }).byte;
cek('byte: mulai ESC @', sebagian[0] === 0x1b && sebagian[1] === 0x40, arr(sebagian).slice(0, 2));
cek('byte: potong sebagian = GS V 66 0 (bawaan)', cari(sebagian, [0x1d, 0x56, 0x42, 0x00]) >= 0);
cek('byte: potong penuh = GS V 65 0', cari(penuh, [0x1d, 0x56, 0x41, 0x00]) >= 0 && cari(penuh, [0x1d, 0x56, 0x42]) < 0);
cek('byte: tanpa potong = tidak ada GS V', cari(tanpa, [0x1d, 0x56]) < 0);
const q = epSusun(g, { qr: 'ABC123' }).byte; const iq = cari(q, [0x1d, 0x28, 0x6b]);
let simpan = -1; for (let i = 0; i < q.length - 6; i++) if (q[i] === 0x1d && q[i + 1] === 0x28 && q[i + 2] === 0x6b && q[i + 5] === 0x31 && q[i + 6] === 0x50) { simpan = i; break; }
cek('QR: perintah ada', iq >= 0);
cek('QR: pL pH = data + 3', simpan >= 0 && q[simpan + 3] === 9 && q[simpan + 4] === 0, simpan >= 0 ? [q[simpan + 3], q[simpan + 4]] : 'tidak ada');
const laci = epSusun(g, { laci: true }).byte;
cek('laci: pulsa ESC p hanya kalau diminta', cari(laci, [0x1b, 0x70, 0x00]) >= 0 && cari(sebagian, [0x1b, 0x70]) < 0);

// ---- gaya gambar (T1 langkah 2) ----
const rgba = (w, h, f) => { const d = new Uint8Array(w * h * 4); for (let i = 0; i < w * h; i++) { const v = f(i % w, Math.floor(i / w)); d[i * 4] = d[i * 4 + 1] = d[i * 4 + 2] = v; d[i * 4 + 3] = 255; } return d; };
const hp = epHitamPutih(rgba(4, 1, (x) => [0, 100, 200, 255][x]), 4, 1, { ambang: 150 });
cek('hitam-putih: ambang (gelap = 1)', arr(hp).join('') === '1100', arr(hp).join(''));
const tr = new Uint8Array([0, 0, 0, 0]); cek('hitam-putih: transparan = putih', epHitamPutih(tr, 1, 1)[0] === 0);
const abu = epHitamPutih(rgba(64, 64, () => 128), 64, 64, { dither: true }); let hitam = 0; for (let i = 0; i < abu.length; i++) hitam += abu[i];
cek('dither: abu-abu 50% jadi ±separuh titik hitam', hitam > 64 * 64 * 0.4 && hitam < 64 * 64 * 0.6, hitam);
const bit = new Uint8Array(10 * 2); bit[0] = 1; bit[9] = 1; bit[10] = 1;
const rs = epRaster(bit, 10, 2);
cek('raster: kepala GS v 0, 2 byte/baris, 2 baris', arr(rs).slice(0, 8).join(',') === [0x1d, 0x76, 0x30, 0, 2, 0, 2, 0].join(','), arr(rs).slice(0, 8));
cek('raster: bit kiri = MSB', arr(rs).slice(8).join(',') === [0x80, 0x40, 0x80, 0x00].join(','), arr(rs).slice(8));
const tinggi = 500; const rb = epRaster(new Uint8Array(576 * tinggi), 576, tinggi); let pita = 0; for (let i = 0; i < rb.length; i++) if (rb[i] === 0x1d && rb[i + 1] === 0x76 && rb[i + 2] === 0x30) pita++;
cek('raster: dipecah per pita (500 baris → 3 perintah)', pita === 3 && rb.length === 3 * 8 + 72 * tinggi, pita + ' / ' + rb.length);
const sg = epSusunGambar({ bit, lebar: 10, tinggi: 2 }, { potong: 'penuh', qr: 'X1' });
cek('struk gambar: ESC @ · raster · QR · potong penuh', sg.byte[0] === 0x1b && sg.byte[1] === 0x40 && cari(sg.byte, [0x1d, 0x76, 0x30]) > 0 && cari(sg.byte, [0x1d, 0x28, 0x6b]) > 0 && cari(sg.byte, [0x1d, 0x56, 0x41, 0x00]) > 0);
// owner 18 Nov: printer NT320 TIDAK memahami GS ( K fn 49 (kepekatan) — byte 0x31 tercetak jadi "1" di atas struk, pita uji sama semua → perintah DICABUT.
// Setelan `pekat` yang telanjur tersimpan di tablet wajib diabaikan.
const gp = epSusunGambar({ bit, lebar: 10, tinggi: 2 }, { pekat: 6 }), tp = epSusun([{ kiri: 'A', kanan: '' }], { pekat: 6 });
cek('struk tanpa perintah kepekatan GS ( K (NT320 mencetaknya jadi "1")', cari(gp.byte, [0x1d, 0x28, 0x4b]) < 0 && cari(tp.byte, [0x1d, 0x28, 0x4b]) < 0 && arr(gp.byte).slice(0, 5).join(',') === [0x1b, 0x40, 0x1b, 0x61, 1].join(','), arr(gp.byte).slice(0, 9));
// ---- label barang (paket S4, 19 Nov 2026) ----
const IL = { judul: 'Beras contoh kemasan 5 kg', ket: 'TOKO BERAS M.IQBAL', kode: 'MIQ:B:JJJJJJJJ', teksKode: 'JJJJJJJJ' };
const berapa = (b, pola) => { let n = 0; for (let i = 0; i + pola.length <= b.length; i++) { let sama = true; for (let k = 0; k < pola.length; k++) if (b[i + k] !== pola[k]) { sama = false; break; } if (sama) n++; } return n; };
// percobaan "kirim per potong" DICABUT (owner 20 Nov 2026 malam: di kertas hanya potong pertama yang keluar) → struk gambar = SATU kiriman
{
  const tg = 1164; const besar = epSusunGambar({ bit: new Uint8Array(576 * tg), lebar: 576, tinggi: tg }, { potong: 'penuh', qr: 'X1', umpan: 4 });
  cek('struk gambar besar: satu kiriman utuh (5 pita, lalu QR dan potong kertas di ekornya), tanpa batas potong', besar.byte.length > 80000 && berapa(besar.byte, [0x1d, 0x76, 0x30, 0x00, 72, 0]) === Math.ceil(tg / 240)
    && cari(besar.byte, [0x1d, 0x56, 0x41, 0x00]) > besar.byte.length - 40 && !('batas' in besar) && typeof epPotong === 'undefined', besar.byte.length + ' ' + Object.keys(besar).join(','));
}
const lb = epSusunLabel(IL, { kertas: 80, potong: 'penuh', umpan: 2, jumlah: 3 });
cek('label struk: tiap lembar punya QR sendiri & dipotong sendiri (3 lembar = 3 QR, 3 potong)', lb.jumlah === 3 && berapa(lb.byte, [0x1d, 0x28, 0x6b, 0x03, 0x00, 0x31, 0x51, 0x30]) === 3 && berapa(lb.byte, [0x1d, 0x56, 0x41, 0x00]) === 3, berapa(lb.byte, [0x1d, 0x56, 0x41, 0x00]));
cek('label struk: nama barang dua kali besar lalu DIKEMBALIKAN ke ukuran biasa sebelum baris kecil', berapa(lb.byte, [0x1d, 0x21, 0x11]) === 3 && berapa(lb.byte, [0x1d, 0x21, 0x00]) === 3 && cari(lb.byte, [0x1d, 0x21, 0x00]) > cari(lb.byte, [0x1d, 0x21, 0x11]));
cek('label struk: isi QR = kode utuh', berapa(lb.byte, [0x31, 0x50, 0x30].concat('MIQ:B:JJJJJJJJ'.split('').map((c) => c.charCodeAt(0)))) === 3);
cek('label struk: pratinjau satu lembar — nama, baris toko, QR, kode pendek', lb.teks.join('|') === 'Beras contoh kemasan 5|kg|TOKO BERAS M.IQBAL|[QR MIQ:B:JJJJJJJJ]|JJJJJJJJ', lb.teks.join('|'));
cek('label struk: jumlah dijepit 1–50; tanpa jumlah = 1', epSusunLabel(IL, {}).jumlah === 1 && epSusunLabel(IL, { jumlah: 0 }).jumlah === 1 && epSusunLabel(IL, { jumlah: 999 }).jumlah === 50 && epSusunLabel(IL, { jumlah: 'x' }).jumlah === 1);
cek('label struk: nama panjang berhenti di 3 baris; tanpa kode → tanpa QR', epSusunLabel({ judul: 'kata '.repeat(40) }, {}).teks.length === 3 && cari(epSusunLabel({ judul: 'A' }, {}).byte, [0x1d, 0x28, 0x6b]) < 0);
cek('label struk: tanpa perintah kepekatan GS ( K (NT320 mencetaknya jadi "1")', cari(lb.byte, [0x1d, 0x28, 0x4b]) < 0);
const tl = epTsplLabel(IL, { lebarMm: 50, tinggiMm: 30, celahMm: 2, jumlah: 4, potong: true });
cek('label TSPL: ukuran, celah, arah, bersih di depan; cetak N lalu potong di belakang', JSON.stringify(tl.teks.slice(0, 4)) === JSON.stringify(['SIZE 50 mm,30 mm', 'GAP 2 mm,0 mm', 'DIRECTION 1', 'CLS']) && tl.teks[tl.teks.length - 2] === 'PRINT 4' && tl.teks[tl.teks.length - 1] === 'CUT', tl.teks.join(' / '));
cek('label TSPL: QR berisi kode utuh; nama barang sebagai TEXT diperbesar (label 50 mm)', tl.teks.some((s) => /^QRCODE \d+,\d+,M,4,A,0,"MIQ:B:JJJJJJJJ"$/.test(s)) && tl.teks.some((s) => /^TEXT 16,16,"0",0,2,2,"Beras contoh/.test(s)) && tl.teks.some((s) => /"JJJJJJJJ"$/.test(s)), tl.teks.join(' / '));
cek('label TSPL: byte = perintah ASCII, tiap perintah diakhiri baris baru', tl.byte.length === tl.teks.join('\n').length + 1 && tl.byte[tl.byte.length - 1] === 0x0a && arr(tl.byte).every((b) => b === 0x0a || (b >= 0x20 && b <= 0x7e)));
cek('label TSPL: tanda kutip & garis miring terbalik di isi tidak memutus perintah', epTsplLabel({ judul: 'Beras "A"', kode: 'X"Y\\Z1', teksKode: 'k"1' }, { lebarMm: 80 }).teks.filter((s) => /^(TEXT|QRCODE)/.test(s)).every((s) => (s.match(/"/g) || []).length === (s.indexOf('TEXT') === 0 ? 4 : 2) && s.indexOf('\\') < 0));
cek('label TSPL: ukuran dijepit (20–80 × 15–200 mm, celah 0–10); tanpa potong = tanpa CUT', (() => { const x = epTsplLabel(IL, { lebarMm: 500, tinggiMm: 1, celahMm: 99, jumlah: 0, potong: false }); return x.teks[0] === 'SIZE 80 mm,15 mm' && x.teks[1] === 'GAP 10 mm,0 mm' && x.teks[x.teks.length - 1] === 'PRINT 1'; })());
cek('label TSPL: celah 0 = kertas bersambung; tanpa setelan = 50 × 30 celah 2', epTsplLabel(IL, { celahMm: 0 }).teks[1] === 'GAP 0 mm,0 mm' && epTsplLabel(IL, {}).teks[0] === 'SIZE 50 mm,30 mm' && epTsplLabel(IL, {}).teks[1] === 'GAP 2 mm,0 mm');
cek('label TSPL: label sempit (30 mm) — huruf tidak diperbesar, kode pendek tidak dipaksa keluar tepi', (() => { const x = epTsplLabel(IL, { lebarMm: 30, tinggiMm: 30 }); return x.teks.some((s) => /^TEXT 16,16,"0",0,1,1,/.test(s)) && !x.teks.some((s) => /"JJJJJJJJ"$/.test(s)) && x.teks.some((s) => /^QRCODE/.test(s)); })());
if (typeof btoa === 'function') cek('base64: byte → teks', epBase64(new Uint8Array([0x1b, 0x40, 0x41])) === 'G0BB', epBase64(new Uint8Array([0x1b, 0x40, 0x41])));
// ---- teks polos → garis struk (owner 21 Nov 2026: slip upah & rekap tutup hari dicetak langsung di tablet) ----
{
  const slip = 'TOKO BERAS M.IQBAL\nSlip upah · Hasan\n1–7 Nov 2026\n\n6 hari penuh × Rp100.000 = Rp600.000\nUpah               Rp600.000\nBonus (rajin)   +Rp50.000\nPotong kasbon     −Rp100.000\nDITERIMA           Rp550.000\n\nDibayar 7 Nov dari laci toko\n\n';
  const G = epGarisDariTeks(slip);
  cek('teks → garis: baris pertama = judul (tengah, tebal); baris kosong di ekor dibuang; baris kosong di tengah tetap', G[0].kiri === 'TOKO BERAS M.IQBAL' && G[0].tengah === true && G[0].tebal === true && G.length === 11 && G[3].kiri === '' && G[9].kiri === '' && !G[1].tengah, JSON.stringify(G.map((g) => g.kiri)));
  cek('teks → garis: "label   nilai" (satu celah dua spasi atau lebih) dipisah jadi kiri/kanan', G[5].kiri === 'Upah' && G[5].kanan === 'Rp600.000' && G[6].kiri === 'Bonus (rajin)' && G[6].kanan === '+Rp50.000' && G[8].kiri === 'DITERIMA' && G[8].kanan === 'Rp550.000', JSON.stringify(G.slice(5, 9)));
  cek('teks → garis: baris biasa (spasi tunggal) tidak dipisah', G[4].kiri === '6 hari penuh × Rp100.000 = Rp600.000' && G[4].kanan === '' && G[10].kanan === '');
  const baris = epSusun(G, { kertas: 80 }).teks;
  cek('teks dicetak: nilai rata kanan selebar kertas, tiap baris ≤ 48 huruf, semuanya ASCII', baris.every((b) => b.length <= 48 && ascii(b)) && baris.some((b) => b.length === 48 && /^Upah +Rp600\.000$/.test(b)) && baris.some((b) => b.length === 48 && /^DITERIMA +Rp550\.000$/.test(b)), JSON.stringify(baris));
  cek('teks dicetak: tanda yang tidak ada di printer diganti padanannya (× → x, − → -, · → -, ÷ → /, ≈ → ~), bukan hilang', baris.some((b) => b.indexOf('6 hari penuh x Rp100.000 = Rp600.000') === 0) && baris.some((b) => /-Rp100\.000$/.test(b)) && baris.some((b) => b.indexOf('Slip upah - Hasan') === 0)
    && epAscii('Rp600.000 ÷ 6 hari ≈ Rp100.000') === 'Rp600.000 / 6 hari ~ Rp100.000', JSON.stringify(baris));
  cek('teks → garis: tiga kolom TIDAK ditebak (dicetak apa adanya); teks kosong = tanpa garis; baris kosong di depan bukan judul', epGarisDariTeks('JUDUL\na   b   c')[1].kanan === '' && epGarisDariTeks('JUDUL\na   b   c')[1].kiri === 'a   b   c'
    && epGarisDariTeks('').length === 0 && epGarisDariTeks(null).length === 0 && epGarisDariTeks('\n\n').length === 0 && epGarisDariTeks('\n  Judul dulu\nisi')[1].tengah === true && !epGarisDariTeks('\n  Judul dulu\nisi')[0].tengah);
  cek('teks 58 mm: baris panjang dibungkus, tidak ada yang lewat 32 huruf', epSusun(G, { kertas: 58 }).teks.every((b) => b.length <= 32));
}
print(JSON.stringify(hasil));
"""


def siapkan(sumber):
    # modul tanpa impor → buang kata `export` supaya jalan sebagai skrip biasa di jsc
    return sumber.replace('export const ', 'const ').replace('export function ', 'function ')


def jalankan(sumber):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(siapkan(sumber) + '\n' + PEMERIKSA); p = f.name
    try:
        r = subprocess.run([JSC, p], capture_output=True, text=True)
    finally:
        os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip():
        return None, (r.stderr or r.stdout).strip()
    return json.loads(r.stdout.strip().splitlines()[-1]), ''


def baca(*bagian):
    with open(os.path.join(AKAR, *bagian), encoding='utf-8') as f: return f.read()


def periksa_statis():
    """Owner 21 Nov 2026: di aplikasi tablet dialog cetak hanya berkelebat — slip upah & rekap tutup hari dicetak langsung; dokumen Laporan ditolak."""
    h = []
    def ok(nama, lulus, ket=''): h.append({'nama': 'statis · ' + nama, 'ok': bool(lulus), 'ket': str(ket)})
    pr = baca('baru', 'js', 'inti', 'printer.js'); ug = baca('baru', 'js', 'layar', 'uang.js'); lp = baca('baru', 'js', 'layar', 'laporan.js')
    a = pr.find('export async function cetakTeks('); b = pr.find('\n}\n', a); ct = pr[a:b] if a >= 0 and b > a else ''
    ok('printer.js cetakTeks: selalu gaya TEKS dari epGarisDariTeks, lewat jalur cetak perangkat ini; printer belum dinyalakan → TIDAK_ADA (tidak diam, tidak dialog)',
       "const s = await susunCetak(epGarisDariTeks(teks), { gaya: 'teks' }, { qr: '' });" in ct and 'return kirimCetak(s.byte, j);' in ct
       and "if (j === 'dialog') {" in ct and "e.code = 'TIDAK_ADA'; throw e; }" in ct and 'window.print' not in ct)
    a = ug.find('  const cetak = (teks, nama) => {'); b = ug.find('\n  };\n', a); ck = ug[a:b] if a >= 0 and b > a else ''
    ok('Uang: di peramban tetap dialog cetak; di aplikasi tablet TIDAK ada window.print — teksnya dikirim ke printer struk',
       "if (!asliAda()) { const pre = document.getElementById('cetakStruk'); if (pre) pre.textContent = teks; try { window.print(); } catch (e) { /* abaikan */ } return; }" in ck
       and ck.count('window.print') == 1 and 'PR.cetakTeks(teks).then(' in ck)
    ok('Uang: satu cetakan pada satu waktu, dan tiap ujung dikabarkan (tercetak · tunggu · lihat kertasnya · TIDAK tercetak beserta sebabnya)',
       ck.find('if (printerSibuk()) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });') < ck.find('PR.cetakTeks(teks)') and ck.find('if (printerSibuk())') > 0
       and "if (masihMencetak(e)) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });" in ck and "if (hasilTakDiketahui(e)) return set({ kabar: KALIMAT_TAK_DIKABARI, kabarAwas: true });" in ck
       and "set({ kabar: nama + ' TIDAK tercetak: ' + (e && e.message ? e.message : e), kabarAwas: true });" in ck and "nama + ' tercetak lewat ' + PR.namaJalur(r.jalur)" in ck)
    ok('Uang: slip upah dan rekap tutup hari sama-sama lewat pintu itu, dengan namanya', "upSlipCetak: () => cetak(st().slipTeks, 'Slip upah')," in ug and "tdCetak: () => cetak(st().rekapTeks, 'Rekap tutup hari')," in ug and ug.count('window.print') == 1)
    k = lp.find('  async function keluarkan(D, info, cara) {'); pk = lp.find('    dkPaketSusun: async () => {')
    ok('Laporan: di aplikasi tablet dokumen kertas besar ditolak SEBELUM nomornya dihitung (tidak ada nomor Cetakan bernomor yang terpakai sia-sia); kirim WA tetap jalan',
       k > 0 and 0 < lp.find("if (cara !== 'wa' && asliAda()) { set({ kabar: KALIMAT_TABLET, kabarAwas: true }); return; }", k) < lp.find('LP.susunCetakan(info, cara, waktu())', k)
       and pk > 0 and 0 < lp.find('if (asliAda()) { set({ kabar: KALIMAT_TABLET, kabarAwas: true }); return; }', pk) < lp.find('LP.susunPaketCetakan(', pk)
       and 'nomor dokumen belum dipakai' in lp and lp.count('window.print') == 1)
    return h


def periksa(sumber, diam=False):
    h, galat = jalankan(sumber)
    if h is not None: h = h + periksa_statis()
    if h is None:
        if not diam: print('GAGAL: jsc tidak jalan —', galat[:400])
        return False
    gagal = [x for x in h if not x['ok']]
    if not diam:
        for x in h: print(('  ok  ' if x['ok'] else 'GAGAL ') + x['nama'] + ('' if x['ok'] or not x['ket'] else ' · ' + x['ket']))
        print(('LULUS ' if not gagal else 'GAGAL ') + str(len(h) - len(gagal)) + '/' + str(len(h)))
    return not gagal


MUTASI = [
    ('padanan titik tengah hilang', "'·': '-', ", ''),
    ('emoji tidak dibuang (surrogate ditulis)', "if (k >= 0xd800 && k <= 0xdbff) { i++; continue; }", "if (k >= 0xd800 && k <= 0xdbff) { out += '??'; i++; continue; }"),
    ('lebar 80 mm salah', "80: 48 }", "80: 42 }"),
    ('angka kanan tidak rata kanan', "new Array(lebar - akhir.length - ka.length + 1).join(' ')", "' '"),
    ('kode potong sebagian salah', "w.byte(GS, 0x56, 0x42, 0x00)", "w.byte(GS, 0x56, 0x41, 0x00)"),
    ('panjang QR tanpa +3', "const n = d.length + 3;", "const n = d.length;"),
    ('bungkus tidak memotong kata panjang', "while (k.length > lebar)", "while (false)"),
    ('raster: bit kanan dulu (LSB)', "v |= 0x80 >> k", "v |= 1 << k"),
    ('raster: tanpa pita (satu perintah raksasa)', "const PITA = 240;", "const PITA = 100000;"),
    ('teks → garis: label/nilai tidak dipisah (kolom berantakan)', "    return bagian.length === 2 ? { kiri: bagian[0], kanan: bagian[1] } : { kiri: t, kanan: '' };", "    return { kiri: t, kanan: '' };"),
    ('teks → garis: tiga kolom ditebak jadi dua', "    return bagian.length === 2 ?", "    return bagian.length >= 2 ?"),
    ('teks → garis: judul tidak ditandai', "if (judul && t) { judul = false; return { kiri: t, kanan: '', tengah: true, tebal: true }; }", "if (judul && t) { judul = false; return { kiri: t, kanan: '' }; }"),
    ('teks → garis: tiap baris dianggap judul', "if (judul && t) { judul = false; return {", "if (judul && t) { return {"),
    ('teks → garis: baris kosong di ekor ikut dicetak', "  while (baris.length && !baris[baris.length - 1].trim()) baris.pop();\n", ""),
    ('padanan ÷ hilang (angka pembagi upah jadi rancu)', "'÷': '/', ", ""),
    ('dither dimatikan diam-diam', "if (!o.dither) {", "if (true) {"),
    ('transparan dianggap hitam', "abu[i] = 255 - a * (255 - l);", "abu[i] = a * l;"),
    ('emoji tidak dibuang di gaya gambar', ".replace(EMOJI, '')", ""),
    ('penyambung ZWJ tertinggal', "\\u{200D}", ""),
    ('pemilih varian tertinggal', "\\u{FE00}-\\u{FE0F}", ""),
    ('struk gambar mengirim kepekatan lagi', "w.byte(ESC, 0x40).byte(ESC, 0x61, 1);", "w.byte(ESC, 0x40).byte(GS, 0x28, 0x4b, 0x02, 0x00, 0x31, o.pekat || 0).byte(ESC, 0x61, 1);"),
    ('label: huruf besar tidak dikembalikan (baris kecil & kode ikut raksasa)', "    w.byte(GS, 0x21, 0x00).byte(ESC, 0x45, 0);\n", "    w.byte(ESC, 0x45, 0);\n"),
    ('label: semua lembar jadi satu potongan', "    tutup(w, { potong: o.potong, umpan: o.umpan }, null);\n  }\n  return { byte: w.hasil(), teks, jumlah: n };", "  }\n  tutup(w, { potong: o.potong, umpan: o.umpan }, null);\n  return { byte: w.hasil(), teks, jumlah: n };"),
    ('label: jumlah lembar tidak dijepit', "  const n = bulat(o.jumlah, 1, EP_LABEL_MAKS, 1);\n  const judul", "  const n = Number(o.jumlah) || 1;\n  const judul"),
    ('label: QR berisi kode pendek, bukan kode utuh', "if (x.kode) { tulisQr(w, x.kode, o.qrUkuran || 6);", "if (x.kode) { tulisQr(w, x.teksKode, o.qrUkuran || 6);"),
    ('label TSPL: tanda kutip tidak dibuang', ".replace(/[\"\\\\]/g, \"'\")", ""),
    ('label TSPL: perintah cetak hilang', "  baris.push('PRINT ' + n);", "  "),
    ('label TSPL: celah tidak dikirim', "'GAP ' + celah + ' mm,0 mm', ", ""),
    ('label TSPL: ukuran tidak dijepit', "const lb = bulat(o.lebarMm, 20, 80, 50);", "const lb = Number(o.lebarMm) || 50;"),
    ('label TSPL: QR berisi kode pendek', "'QRCODE ' + tepi + ',' + y + ',M,4,A,0,\"' + kutip(x.kode)", "'QRCODE ' + tepi + ',' + y + ',M,4,A,0,\"' + kutip(x.teksKode)"),
    ('struk teks mengirim kepekatan lagi', "w.byte(ESC, 0x40).byte(ESC, 0x74, 0x00);", "w.byte(ESC, 0x40).byte(GS, 0x28, 0x4b, 0x02, 0x00, 0x31, o.pekat || 0).byte(ESC, 0x74, 0x00);"),
]


def main():
    if not os.path.exists(JSC): print('GAGAL: jsc tidak ditemukan'); return 1
    asli = open(BERKAS, encoding='utf-8').read()
    if '--kontrol' in sys.argv:
        lolos = []
        for nama, lama, baru in MUTASI:
            if lama not in asli: print('KONTROL BASI: pola tidak ditemukan —', nama); lolos.append(nama); continue
            if periksa(asli.replace(lama, baru, 1), diam=True): lolos.append(nama); print('LOLOS (seharusnya gagal):', nama)
            else: print('  tertangkap:', nama)
        if not periksa(asli, diam=True): print('GAGAL: salinan utuh tidak lulus'); return 3
        print('KONTROL ' + ('LULUS' if not lolos else 'GAGAL') + ' ' + str(len(MUTASI) - len(lolos)) + '/' + str(len(MUTASI)))
        return 0 if not lolos else 3
    return 0 if periksa(asli) else 1


if __name__ == '__main__':
    sys.exit(main())
