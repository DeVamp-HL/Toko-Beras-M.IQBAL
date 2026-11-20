#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_qr.py — penyusun kode QR (baru/js/inti/qr.js) dijalankan ASLI di jsc, tanpa kamera dan tanpa printer.

Kenapa ada: owner 20 Nov 2026 minta QR nota pindah ke samping tanda tangan di struk bergambar. Selama ini QR digambar printer sendiri
(GS ( k), jadi halaman tidak pernah punya penyusun QR. Kalau penyusunnya salah satu bit saja, struk tetap tercetak rapi tetapi scan struk
tidak lagi membuka nota — dan itu baru ketahuan di toko.

Yang dipegang:
  · PEMBACA MANDIRI di dalam alat uji ini (ditulis terpisah: aritmetika GF tanpa tabel, peta modul fungsi sendiri, letak info format
    sendiri) membaca balik kotak hasil qr.js: info format dua salinan sama & sah (BCH), topeng dibuka, kata dibaca berkelok, blok
    dipisah, SINDROM Reed–Solomon tiap blok nol, lalu isinya = teks yang dimasukkan. Untuk versi 1–6 dan KEDELAPAN topeng.
  · angka baku: kata koreksi contoh "HELLO WORLD" versi 1-M; batas muatan tiap versi (14, 26, 42, 62, 84, 106 huruf)
  · rupa: pola pencari di tiga pojok, pemisah putih, garis waktu, pola penjajar (versi ≥ 2), modul gelap
  · kotak beku: satu teks nota yang kotaknya SUDAH dibaca pemindai sungguhan (BarcodeDetector di panel peramban, 20 Nov 2026) dibekukan
    di sini — penyusun yang berubah diam-diam ketahuan
  · yang tidak boleh jadi QR: teks kosong, huruf di luar ASCII yang bisa dicetak, lebih dari 106 huruf → null (pemanggil kembali ke QR printer)

    python3 alat-uji/uji_qr.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_qr.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, sys, json, subprocess, tempfile

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BERKAS = os.path.join(AKAR, 'baru', 'js', 'inti', 'qr.js')
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'

PEMERIKSA = r"""
const hasil = [];
const cek = (nama, ok, ket) => hasil.push({ nama, ok: !!ok, ket: ket === undefined ? '' : String(ket) });

// ---------- pembaca mandiri (tidak memakai apa pun dari qr.js selain kotak hasilnya) ----------
const U_BLOK = { 1: [1, 16, 10], 2: [1, 28, 16], 3: [1, 44, 26], 4: [2, 32, 18], 5: [2, 43, 24], 6: [4, 27, 16] };
function uKali(a, b) { let p = 0; for (let i = 0; i < 8; i++) { if (b & 1) p ^= a; const t = a & 0x80; a = (a << 1) & 0xff; if (t) a ^= 0x1d; b >>= 1; } return p; }
function uPangkat2(e) { let r = 1; for (let i = 0; i < e; i++) r = uKali(r, 2); return r; }
function uSindrom(kata, nk) { const s = []; for (let i = 0; i < nk; i++) { const x = uPangkat2(i); let v = 0; for (let j = 0; j < kata.length; j++) v = uKali(v, x) ^ kata[j]; s.push(v); } return s; }
function uSisaBch(v) { for (let i = 14; i >= 10; i--) if ((v >> i) & 1) v ^= 0x537 << (i - 10); return v; }
const U_TOPENG = [
  (b, k) => (b + k) % 2 === 0, (b, k) => b % 2 === 0, (b, k) => k % 3 === 0, (b, k) => (b + k) % 3 === 0,
  (b, k) => ((b >> 1) + Math.floor(k / 3)) % 2 === 0, (b, k) => (b * k) % 2 + (b * k) % 3 === 0,
  (b, k) => ((b * k) % 2 + (b * k) % 3) % 2 === 0, (b, k) => ((b + k) % 2 + (b * k) % 3) % 2 === 0,
];
function uBaca(q) {
  const n = q.modul, v = (n - 17) / 4; const di = (b, k) => q.bit[b * n + k];
  const letak1 = [[0, 8], [1, 8], [2, 8], [3, 8], [4, 8], [5, 8], [7, 8], [8, 8], [8, 7], [8, 5], [8, 4], [8, 3], [8, 2], [8, 1], [8, 0]];
  let f1 = 0; letak1.forEach((p, i) => { f1 |= di(p[0], p[1]) << i; });
  let f2 = 0; for (let i = 0; i < 8; i++) f2 |= di(8, n - 1 - i) << i; for (let i = 8; i < 15; i++) f2 |= di(n - 15 + i, 8) << i;
  const f = f1 ^ 0x5412; const topeng = (f >> 10) & 7;
  const fungsi = (b, k) => (b <= 8 && k <= 8) || (b <= 8 && k >= n - 8) || (b >= n - 8 && k <= 8) || b === 6 || k === 6 || (v >= 2 && Math.abs(b - (n - 7)) <= 2 && Math.abs(k - (n - 7)) <= 2);
  const bit = []; let naik = true;
  for (let kanan = n - 1; kanan >= 1; kanan -= 2) {
    if (kanan === 6) kanan = 5;
    for (let t = 0; t < n; t++) { const b = naik ? n - 1 - t : t; [kanan, kanan - 1].forEach((k) => { if (!fungsi(b, k)) bit.push(di(b, k) ^ (U_TOPENG[topeng](b, k) ? 1 : 0)); }); }
    naik = !naik;
  }
  const B = U_BLOK[v]; const nb = B[0], nd = B[1], nk = B[2]; const total = nb * (nd + nk);
  const kata = []; for (let i = 0; i < total; i++) { let x = 0; for (let j = 0; j < 8; j++) x = (x << 1) | bit[i * 8 + j]; kata.push(x); }
  const blok = []; for (let i = 0; i < nb; i++) blok.push([]);
  let p = 0; for (let j = 0; j < nd; j++) for (let i = 0; i < nb; i++) blok[i].push(kata[p++]);
  for (let j = 0; j < nk; j++) for (let i = 0; i < nb; i++) blok[i].push(kata[p++]);
  const sindromNol = blok.every((x) => uSindrom(x, nk).every((s) => s === 0));
  let data = []; blok.forEach((x) => { data = data.concat(x.slice(0, nd)); });
  const db = []; data.forEach((x) => { for (let i = 7; i >= 0; i--) db.push((x >> i) & 1); });
  const ambil = (dari, n2) => { let x = 0; for (let i = 0; i < n2; i++) x = (x << 1) | db[dari + i]; return x; };
  const mode = ambil(0, 4), panjang = ambil(4, 8); let teks = ''; for (let i = 0; i < panjang; i++) teks += String.fromCharCode(ambil(12 + i * 8, 8));
  // ganjalan sesudah isi: penutup 0000 → rata 8 bit → 0xEC, 0x11 berselang sampai penuh
  const mulaiGanjal = Math.ceil((12 + panjang * 8 + 4) / 8); const ganjal = data.slice(Math.min(mulaiGanjal, data.length));
  const ganjalBenar = ganjal.every((x, i) => x === (i % 2 ? 0x11 : 0xec));
  return { versi: v, f1, f2, formatSah: uSisaBch(f) === 0, tingkat: f >> 13, topeng, jumlahBit: bit.length, sisaBit: bit.length - total * 8, sindromNol, mode, panjang, teks, ganjalBenar };
}
const utuh = (teks, topeng) => { const q = qrSusun(teks, topeng); if (!q) return { galat: 'null' }; const r = uBaca(q);
  const ok = r.f1 === r.f2 && r.formatSah && r.tingkat === 0 && r.sindromNol && r.mode === 4 && r.teks === teks && r.ganjalBenar && r.topeng === q.topeng && r.versi === q.versi
    && r.sisaBit === (q.versi === 1 ? 0 : 7) && q.modul === 17 + 4 * q.versi && q.bit.length === q.modul * q.modul && Array.prototype.every.call(q.bit, (x) => x === 0 || x === 1);
  return { ok, q, r }; };
const ket = (h) => h.galat || JSON.stringify(Object.assign({}, h.r, { v: h.q.versi, t: h.q.topeng }));

// ---------- angka baku ----------
const HW = [32, 91, 11, 120, 209, 114, 220, 77, 67, 64, 236, 17, 236, 17, 236, 17];
cek('Reed–Solomon: kata koreksi contoh baku "HELLO WORLD" versi 1-M', qrKoreksi(HW, 10).join(',') === '196,35,39,119,235,215,231,226,93,23', qrKoreksi(HW, 10).join(','));
cek('Reed–Solomon: data + koreksi → sindrom nol menurut aritmetika pembaca mandiri (16+10, 44+26, 27+16)', [[16, 10], [44, 26], [27, 16]].every((u) => { const d = []; for (let i = 0; i < u[0]; i++) d.push((i * 37 + 11) & 0xff);
  return uSindrom(d.concat(qrKoreksi(d, u[1])), u[1]).every((s) => s === 0); }));
cek('muatan tiap versi (mode byte, koreksi M): 14, 26, 42, 62, 84, 106 huruf; di atasnya tidak muat; nol huruf tidak muat', [[1, 1], [14, 1], [15, 2], [26, 2], [27, 3], [42, 3], [43, 4], [62, 4], [63, 5], [84, 5], [85, 6], [106, 6], [107, 0], [0, 0]]
  .every((u) => qrVersi(u[0]) === u[1]), [14, 15, 26, 27, 42, 43, 62, 63, 84, 85, 106, 107].map((n) => qrVersi(n)).join(','));
cek('info format koreksi M: kedelapan topeng sah menurut BCH, membawa nomor topengnya, dan topeng 0 = 101010000010010', [0, 1, 2, 3, 4, 5, 6, 7].every((t) => { const f = qrInfoFormat(t) ^ 0x5412; return uSisaBch(f) === 0 && (f >> 10) === t; })
  && qrInfoFormat(0).toString(2).padStart(15, '0') === '101010000010010' && qrInfoFormat(7).toString(2).padStart(15, '0') === '100101010100000', [0, 1, 2, 3, 4, 5, 6, 7].map((t) => qrInfoFormat(t).toString(2).padStart(15, '0')).join(' '));

// ---------- dibaca balik: tiap versi, tiap topeng ----------
const NOTA = 'MIQ:N:t:AbCdEfGhIjKlMnOpQrSt';   // bentuk QR nota: awalan + kunci + id 20 huruf (28 huruf → versi 3)
const teksPanjang = (n) => { let s = ''; for (let i = 0; i < n; i++) s += String.fromCharCode(0x20 + ((i * 7 + 3) % 95)); return s; };
[1, 14, 15, 26, 27, 28, 42, 43, 62, 63, 84, 85, 106].forEach((n) => { const h = utuh(teksPanjang(n)); cek('dibaca balik utuh: ' + n + ' huruf → versi ' + qrVersi(n), h.ok && h.q.versi === qrVersi(n), ket(h)); });
{
  const gagal = []; [NOTA, teksPanjang(14), teksPanjang(50), teksPanjang(100)].forEach((t) => { for (let m = 0; m < 8; m++) { const h = utuh(t, m); if (!h.ok || h.q.topeng !== m) gagal.push(t.length + '/' + m); } });
  cek('kedelapan topeng (dipaksa satu per satu) dibaca balik utuh untuk versi 1, 3, 4, dan 6', gagal.length === 0, gagal.join(' '));
}
{
  const h = utuh(NOTA); const q = h.q;
  cek('QR nota (28 huruf): versi 3, 29 × 29 modul, dibaca balik = teks nota', h.ok && q.versi === 3 && q.modul === 29, ket(h));
  cek('topeng yang dipilih sendiri = salah satu dari delapan, dan bukan selalu yang pertama', [NOTA, 'MIQ:N:g:1', 'MIQ:N:i:ZZZZZZZZ', teksPanjang(60), teksPanjang(33)].map((t) => qrSusun(t).topeng).some((t) => t !== 0), [NOTA, 'MIQ:N:g:1', teksPanjang(60)].map((t) => qrSusun(t).topeng).join(','));
}

// ---------- rupa ----------
{
  const rupa = (q) => { const n = q.modul; const di = (b, k) => q.bit[b * n + k];
    const pencari = (b0, k0) => { for (let b = 0; b < 7; b++) for (let k = 0; k < 7; k++) { const mau = b === 0 || b === 6 || k === 0 || k === 6 || (b >= 2 && b <= 4 && k >= 2 && k <= 4) ? 1 : 0; if (di(b0 + b, k0 + k) !== mau) return false; } return true; };
    let pemisah = true; for (let i = 0; i < 8; i++) { if (di(7, i) || di(i, 7) || di(7, n - 1 - i) || di(i, n - 8) || di(n - 8, i) || di(n - 1 - i, 7)) pemisah = false; }
    let waktu = true; for (let i = 8; i < n - 8; i++) { if (di(6, i) !== (i % 2 === 0 ? 1 : 0) || di(i, 6) !== (i % 2 === 0 ? 1 : 0)) waktu = false; }
    let penjajar = true; if (q.versi >= 2) { const p = n - 7; for (let b = -2; b <= 2; b++) for (let k = -2; k <= 2; k++) { if (di(p + b, p + k) !== (Math.max(Math.abs(b), Math.abs(k)) !== 1 ? 1 : 0)) penjajar = false; } }
    return { pencari: pencari(0, 0) && pencari(0, n - 7) && pencari(n - 7, 0), pemisah, waktu, penjajar, gelap: di(n - 8, 8) === 1 }; };
  const semua = []; [teksPanjang(5), teksPanjang(20), NOTA, teksPanjang(60), teksPanjang(80), teksPanjang(100)].forEach((t) => { for (let m = 0; m < 8; m++) semua.push(rupa(qrSusun(t, m))); });
  cek('rupa: tiga pola pencari utuh di pojok kiri atas, kanan atas, kiri bawah — di tiap versi dan tiap topeng (topeng tidak menyentuhnya)', semua.every((r) => r.pencari));
  cek('rupa: pemisah putih di sekeliling pola pencari', semua.every((r) => r.pemisah));
  cek('rupa: garis waktu berselang hitam-putih di baris 6 dan kolom 6', semua.every((r) => r.waktu));
  cek('rupa: pola penjajar 5 × 5 di pojok kanan bawah untuk versi 2–6', semua.every((r) => r.penjajar));
  cek('rupa: modul gelap di (n − 8, 8) selalu hitam', semua.every((r) => r.gelap));
}

// ---------- yang tidak boleh jadi QR ----------
cek('teks kosong, null, dan lebih dari 106 huruf → null (pemanggil kembali ke QR bawaan printer)', qrSusun('') === null && qrSusun(null) === null && qrSusun(undefined) === null && qrSusun(teksPanjang(107)) === null && qrSusun(teksPanjang(106)) !== null);
cek('huruf di luar ASCII yang bisa dicetak → null (tidak diam-diam diubah)', qrSusun('MIQ:N:t:é') === null && qrSusun('a\nb') === null && qrSusun('a b') === null && qrSusun('~ ') !== null);

// ---------- ukuran di gambar struk ----------
// kertas 80 mm: celah antara ujung garis tanda tangan dan tepi kiri cap = 164 titik; kertas 58 mm = 110 titik (hitungan struk-kanvas.js)
cek('ukuran: QR nota (versi 3, 29 modul) di kertas 80 mm = 4 titik per modul (±14,5 mm); di 58 mm = 3 titik', qrTitikMuat(29, 164) === 4 && qrTitikMuat(29, 110) === 3, qrTitikMuat(29, 164) + ' ' + qrTitikMuat(29, 110));
cek('ukuran: modul tidak pernah lebih besar dari ' + QR_TITIK_MAKS + ' titik walau celahnya lapang', qrTitikMuat(21, 164) === QR_TITIK_MAKS && qrTitikMuat(21, 9999) === QR_TITIK_MAKS && qrTitikMuat(25, 164) === 5);
cek('ukuran: daerah tenang ' + QR_TENANG + ' modul di kiri dan kanan ikut dihitung (29 + 4 = 33 modul × 4 = 132 ≤ 164, × 5 = 165 > 164)', qrTitikMuat(29, 165) === 5 && qrTitikMuat(29, 164) === 4 && (29 + 2 * QR_TENANG) * 4 <= 164);
cek('ukuran: kurang dari ' + QR_TITIK_MIN + ' titik per modul = TIDAK digambar (0) — pemanggil kembali ke QR printer', qrTitikMuat(33, 110) === 0 && qrTitikMuat(41, 164) === 3 && qrTitikMuat(41, 134) === 0 && qrTitikMuat(29, 0) === 0 && qrTitikMuat(29, -5) === 0,
  [qrTitikMuat(33, 110), qrTitikMuat(41, 164), qrTitikMuat(41, 134)].join(','));

// ---------- kotak beku: sudah dibaca pemindai sungguhan ----------
{
  const q = qrSusun(NOTA); let heks = ''; for (let i = 0; i < q.bit.length; i += 4) heks += ((q.bit[i] << 3) | ((q.bit[i + 1] || 0) << 2) | ((q.bit[i + 2] || 0) << 1) | (q.bit[i + 3] || 0)).toString(16);
  cek('kotak beku QR nota: persis kotak yang sudah dibaca pemindai sungguhan (topeng ' + BEKU.topeng + ')', q.topeng === BEKU.topeng && heks === BEKU.heks, q.topeng + ' ' + heks);
}
print(JSON.stringify(hasil));
"""

# Kotak QR untuk teks 'MIQ:N:t:AbCdEfGhIjKlMnOpQrSt' — dibekukan SESUDAH kanvasnya dibaca BarcodeDetector di panel peramban (20 Nov 2026).
BEKU = {'topeng': 2, 'heks': 'fe5f6bfc12fe106ebb46bb7566a5dba819aec1701507faaaafe01e5500be7093e605f86d7c95e82c5aaa1385feb50150d4cff19a21a49e1356d0eaa890fde5f86dab81f809112a258935b5fe807cc46bf9406a10575712bac8afedd4fb812ead73ed04b6cfafed71480'}


def siapkan(sumber):
    # modul tanpa impor → buang kata `export` supaya jalan sebagai skrip biasa di jsc
    return sumber.replace('export const ', 'const ').replace('export function ', 'function ')


def jalankan(sumber):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(siapkan(sumber) + '\nconst BEKU = ' + json.dumps(BEKU) + ';\n' + PEMERIKSA); p = f.name
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
    """Pemasangan di halaman: QR digambar di gambar struk, dan printer tidak mencetaknya SEKALI LAGI di bawah."""
    h = []
    def ok(nama, lulus, ket=''): h.append({'nama': 'statis · ' + nama, 'ok': bool(lulus), 'ket': str(ket)})
    sk = baca('baru', 'js', 'inti', 'struk-kanvas.js'); pr = baca('baru', 'js', 'inti', 'printer.js'); jl = baca('baru', 'js', 'layar', 'jual.js'); ep = baca('baru', 'js', 'inti', 'escpos.js')
    a = sk.find('function gambarSertifikat('); b = sk.find('\n}\n', a); gs = sk[a:b] if a >= 0 and b > a else ''
    a = sk.find('function gambarPolos('); b = sk.find('\n}\n', a); polos = sk[a:b] if a >= 0 and b > a else ''
    ok('struk-kanvas: QR disusun qr.js dan ukurannya dari qrTitikMuat (celah antara ujung garis tanda tangan dan tepi kiri cap)',
       "import { qrSusun, qrTitikMuat, QR_TENANG } from './qr.js';" in sk and "const blokY = y; const qrKiri = L + P(236), qrKanan = R - P(86) - P(42);" in gs
       and "const qr = o.qr ? qrSusun(o.qr) : null; const qrT = qr ? qrTitikMuat(qr.modul, qrKanan - qrKiri) : 0; const qrSisi = qrT ? qr.modul * qrT : 0;" in gs)
    ok('struk-kanvas: tiap modul hitam = satu kotak utuh berukuran bulat (tanpa pemulusan), di tengah celah, mulai di atas blok tanda tangan',
       "const qrX = Math.round((qrKiri + qrKanan - qrSisi) / 2);" in gs and "if (qr.bit[b * qr.modul + kk]) c.fillRect(qrX + kk * qrT, blokY + b * qrT, qrT, qrT);" in gs)
    ok('struk-kanvas: nama yang melayani dikecilkan supaya berhenti sebelum daerah tenang QR; tanpa QR ukurannya tetap',
       "const pxN = qrSisi ? muatLebar(M.pelayan, (px) => F_ITA(600, px), P(40), qrX - QR_TENANG * qrT - (L + P(36))) : P(40);" in gs)
    ok('struk-kanvas: kalimat kaki tidak menabrak QR, dan hasilnya MENGATAKAN apakah QR sudah ada di gambar',
       "y = Math.max(y, capY + P(92), qrSisi ? blokY + qrSisi + P(10) : 0);" in gs and "const jadi = jadiBit(kanvas, c, W, y); jadi.qrDiGambar = !!qrSisi;" in gs and 'qrDiGambar' not in polos and polos)
    ok('printer.js: teks QR diteruskan ke gambar; perintah QR printer DIBUANG hanya bila gambarnya sudah memuat QR (tidak dobel, tidak hilang)',
       "const g = gambarStruk(garis, { kertas: a.kertas, logo: teksKeLogo(a.logo), logoToko: !!o.logoToko, qr: o.qr || '' });" in pr
       and "const sg = epSusunGambar(g, g.qrDiGambar ? Object.assign({}, o, { qr: '' }) : o);" in pr)
    ok('escpos.js: QR bawaan printer tetap ada untuk gaya teks dan struk yang QR-nya tidak muat di gambar', 'if (o.qr) { w.byte(ESC, 0x61, 1); tulisQr(w, o.qr, o.qrUkuran);' in ep)
    ok('Jual: pratinjau struk memuat QR yang sama dengan cetakan (setelan printer perangkat ini), dan pratinjau lama tidak dipakai ulang saat QR berubah',
       "const url = pratinjauStruk(st, n.pilih.kertas, PR.prAtur().qr ? TK.tkQrNota(n.nota) : '');" in jl and "const kunci = kertas + '|' + (st.logo ? 'L' : '') + '|' + (qr || '') + '|' + st.teks;" in jl
       and "gambarStrukKanvas(st.garis, { kertas, logoToko: st.logo, qr: qr || '' })" in jl)
    ok('index.html: modul qr.js ikut dimuat di depan (dipakai gambar struk)', '<link rel="modulepreload" href="js/inti/qr.js">' in baca('baru', 'index.html'))
    return h


def periksa(sumber, diam=False):
    h, galat = jalankan(sumber)
    if h is not None: h = h + periksa_statis()
    if h is None:
        if not diam: print('GAGAL: jsc tidak jalan —', galat[:400])
        return False
    gagal = [x for x in h if not x['ok']]
    if not diam:
        for x in h: print(('  ok  ' if x['ok'] else 'GAGAL ') + x['nama'] + ('' if x['ok'] or not x['ket'] else ' · ' + x['ket'][:600]))
        print(('LULUS ' if not gagal else 'GAGAL ') + str(len(h) - len(gagal)) + '/' + str(len(h)))
    return not gagal


MUTASI = [
    ('polinom GF salah', "if (x & 0x100) x ^= 0x11d;", "if (x & 0x100) x ^= 0x11b;"),
    ('pembangkit Reed–Solomon mulai dari α^1', "b[j + 1] ^= kali(g[j], EXP[i]);", "b[j + 1] ^= kali(g[j], EXP[i + 1]);"),
    ('muatan versi kelebihan satu huruf (huruf terakhir terpotong)', "if (n >= 1 && n <= b[0] * b[1] - 2) return v;", "if (n >= 1 && n <= b[0] * b[1] - 1) return v;"),
    ('teks kosong diberi QR', "if (n >= 1 && n <= b[0] * b[1] - 2) return v;", "if (n <= b[0] * b[1] - 2) return v;"),
    ('pembangkit BCH info format salah', "((sisa >> 9) * 0x537)", "((sisa >> 9) * 0x535)"),
    ('topeng info format salah', ") ^ 0x5412;", ") ^ 0x5411;"),
    ('tanda mode bukan byte', "dorong(4, 4);", "dorong(2, 4);"),
    ('ganjalan terbalik', "kata.push(i % 2 ? 0x11 : 0xec);", "kata.push(i % 2 ? 0xec : 0x11);"),
    ('blok tidak diselang', "  for (let j = 0; j < nd; j++) for (let i = 0; i < nb; i++) hasil.push(blok[i][j]);", "  for (let i = 0; i < nb; i++) for (let j = 0; j < nd; j++) hasil.push(blok[i][j]);"),
    ('kata koreksi tidak diselang', "  for (let j = 0; j < nk; j++) for (let i = 0; i < nb; i++) hasil.push(kor[i][j]);", "  for (let i = 0; i < nb; i++) for (let j = 0; j < nk; j++) hasil.push(kor[i][j]);"),
    ('kolom garis waktu tidak dilompati', "    if (kol === 6) kol = 5;\n", ""),
    ('arah berkelok tidak berbalik', "    naik = !naik;\n", ""),
    ('bit kata ditaruh dari yang kecil', "kata.forEach((x) => { for (let i = 7; i >= 0; i--) aliran.push((x >> i) & 1); });", "kata.forEach((x) => { for (let i = 0; i < 8; i++) aliran.push((x >> i) & 1); });"),
    ('pola penjajar hilang di versi 2', "  if (v >= 2) { const p = n - 7;", "  if (v >= 3) { const p = n - 7;"),
    ('pola penjajar salah letak', "  if (v >= 2) { const p = n - 7;", "  if (v >= 2) { const p = n - 8;"),
    ('modul gelap tidak hitam', "    m[(n - 8) * n + 8] = 1;", "    m[(n - 8) * n + 8] = 0;"),
    ('topeng menimpa pola pencari', "if (!fungsi[b * n + k] && QR_TOPENG[t](b, k)) m[b * n + k] ^= 1;", "if (QR_TOPENG[t](b, k)) m[b * n + k] ^= 1;"),
    ('topeng 5 salah rumus', "(b, k) => ((b * k) % 2) + ((b * k) % 3) === 0,", "(b, k) => ((b * k) % 2) + ((b * k) % 3) === 1,"),
    ('topeng 4 salah rumus', "(Math.floor(b / 2) + Math.floor(k / 3)) % 2 === 0", "(Math.floor(b / 3) + Math.floor(k / 2)) % 2 === 0"),
    ('topeng 7 salah rumus', "(((b + k) % 2) + ((b * k) % 3)) % 2 === 0,\n];", "(((b + k) % 3) + ((b * k) % 2)) % 2 === 0,\n];"),
    ('info format salinan kedua salah letak', "m[8 * n + (n - 1 - i)] = bitKe(i);", "m[8 * n + (n - 8 + i)] = bitKe(i);"),
    ('info format salinan pertama melompati bit 6', "m[7 * n + 8] = bitKe(6);", "m[6 * n + 8] = bitKe(6);"),
    ('garis waktu terbalik', "pasang(6, i, i % 2 === 0); pasang(i, 6, i % 2 === 0);", "pasang(6, i, i % 2 === 1); pasang(i, 6, i % 2 === 1);"),
    ('pola pencari tanpa inti', "(b >= 2 && b <= 4 && k >= 2 && k <= 4)));", "(b >= 3 && b <= 3 && k >= 3 && k <= 3)));"),
    ('ukuran: modul boleh sebesar apa pun', "const t = Math.min(QR_TITIK_MAKS, Math.floor(ruang / (modul + 2 * QR_TENANG)));", "const t = Math.floor(ruang / (modul + 2 * QR_TENANG));"),
    ('ukuran: daerah tenang tidak dihitung', "Math.floor(ruang / (modul + 2 * QR_TENANG))", "Math.floor(ruang / modul)"),
    ('ukuran: QR terlalu kecil tetap digambar', "  return t >= QR_TITIK_MIN ? t : 0;", "  return t > 0 ? t : 0;"),
    ('ukuran: QR yang muat tidak digambar', "  return t >= QR_TITIK_MIN ? t : 0;", "  return 0;"),
    ('huruf di luar ASCII diterima', "if (c < 0x20 || c > 0x7e) return null;", "if (c > 0xffff) return null;"),
    ('topeng paksa diabaikan (alat uji tidak lagi memeriksa kedelapannya)', "    if (Number.isInteger(topengPaksa) && t !== topengPaksa) continue;\n", ""),
    ('selalu topeng terakhir (hukuman tidak dibandingkan)', "if (!terbaik || h < terbaik.h) terbaik = { h, m, t };", "terbaik = { h, m, t };"),
]


def main():
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
