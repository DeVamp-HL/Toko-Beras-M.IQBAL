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

    python3 alat-uji/uji_escpos.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_escpos.py --kontrol  → tiap salinan rusak WAJIB gagal; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, sys, json, subprocess, tempfile

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BERKAS = os.path.join(AKAR, 'baru', 'js', 'inti', 'escpos.js')
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'

PEMERIKSA = r"""
const hasil = [];
const cek = (nama, ok, ket) => hasil.push({ nama, ok: !!ok, ket: ket === undefined ? '' : String(ket) });
const ascii = (s) => /^[\x20-\x7e]*$/.test(s);

cek('ascii: titik tengah jadi -', epAscii('a · b') === 'a - b', epAscii('a · b'));
cek('ascii: kali jadi x', epAscii('2 × 3') === '2 x 3', epAscii('2 × 3'));
cek('ascii: minus rupiah jadi -', epAscii('−Rp500') === '-Rp500', epAscii('−Rp500'));
cek('ascii: aksen dilepas', epAscii('café') === 'cafe', epAscii('café'));
cek('ascii: emoji dibuang', epAscii('Terima kasih 🙏') === 'Terima kasih', JSON.stringify(epAscii('Terima kasih 🙏')));

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


def periksa(sumber, diam=False):
    h, galat = jalankan(sumber)
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
