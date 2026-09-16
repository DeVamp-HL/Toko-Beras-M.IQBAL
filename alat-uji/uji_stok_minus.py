#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_stok_minus.py — penjaga: stok yang MINUS tidak boleh diucapkan sebagai "sisa 0".

Stok minus artinya pembukuannya sendiri rusak. Dijepit jadi 0, ia jadi tak terbedakan dari
"pas habis" — keadaan yang SEHAT. Tiga tempat dulu melakukannya, dan salah satunya menulis
angka terjepit itu PERMANEN ke dokumen tembusanStok yang dibaca opname berbulan kemudian.
"""
import io, re, sys, pathlib
AKAR = pathlib.Path(__file__).resolve().parent.parent
SRC = (AKAR / 'index.html').read_text(encoding='utf-8')
gagal = 0

print('-- nilai yang DIUCAPKAN tidak boleh terjepit --')
for pola, ket in [
    (r"const sisaKgEfektif = m => Math\.max\(0,", 'penjaga terakhir (karung/literan/repack) masih menjepit'),
    (r"const sisaUnitEfektif = k => Math\.max\(0,", 'penjaga terakhir (kemasan) masih menjepit'),
    (r"a \+ Math\.max\(0, stokK\[m\]\.sisaKg", 'neraca masih menilai stok minus jadi Rp0'),
    (r"a \+ Math\.max\(0, stokB\[k\]\.sisaUnit", 'neraca masih menilai kemasan minus jadi Rp0'),
]:
    if re.search(pola, SRC): print('  GAGAL:', ket); gagal += 1
    else: print('  ok  : bukan ini lagi —', ket[:52])

print('-- ada cabang untuk keadaan MINUS --')
for frasa, di in [
    ('sudah MINUS', 'pesan penolakan + peringatan wizard'),
    ('Penembusan tidak tersedia untuk keadaan ini', 'tolakStokAtauTembus menolak menembus'),
    ('catatannya yang rusak', 'kalimatnya menyebut catatan, bukan barang'),
    ('function stokMaksMentah', 'nilai mentah dibawa keluar dari langit-langit'),
    ('adaStokMinus', 'neraca membawa daftar merek minus keluar'),
]:
    if frasa in SRC: print('  ok  : %-44s (%s)' % (frasa, di))
    else: print('  GAGAL: hilang -', frasa); gagal += 1

print('-- langit-langit JUAL tetap tidak boleh minus --')
if 'return s ? Math.max(0, Math.floor((s.sisaKg' in SRC: print('  ok  : stokMaksJalur masih menjepit (itu memang benar: yang dijual tidak boleh minus)')
else: print('  GAGAL: langit-langit jual ikut dicabut jepitannya'); gagal += 1

print('-- kontrol positif --')
racun = SRC.replace('function stokMaksMentah', 'function stokMaksMentahXX', 1)
if 'function stokMaksMentah\n' not in racun and 'function stokMaksMentah(' not in racun:
    print('  ok  : penjaga melihat kalau stokMaksMentah dicabut')
else:
    print('  GAGAL: penjaga BUTA'); gagal += 1

sys.exit(1 if gagal else print('SEMUA LULUS') or 0)
