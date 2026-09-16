#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_dua_arah.py — penjaga: kaki yang berjalan DUA ARAH tidak boleh dijepit lalu dijadikan saklar.

jadiStok / jadiPiutang / jadiKasbon bisa POSITIF (kas berubah wujud jadi barang & tagihan) atau
NEGATIF (barang & tagihan mencair balik jadi kas). Menjepit tiap kaki dengan Math.max(0, …) lalu
menjumlahkannya membuang arah sebaliknya — dan di tiga tempat jumlah itu dipakai MEMILIH kalimat,
sehingga layar bisa berkata kebalikan dari yang terjadi.

Aturan yang dijaga: kalimatnya WAJIB bercabang pada TANDA ASLI tiap kaki.
"""
import io, re, sys, pathlib

AKAR = pathlib.Path(__file__).resolve().parent.parent
SRC = (AKAR / 'index.html').read_text(encoding='utf-8')
TERLARANG = re.compile(
    r"Math\.max\(0, jadiStok\)\s*\+\s*Math\.max\(0, jadiPiutang\)\s*\+\s*Math\.max\(0, jadiKasbon\)")

gagal = 0
print('-- jumlah terjepit tidak boleh jadi saklar kalimat --')
n = len(TERLARANG.findall(SRC))
if n: print('  GAGAL: %d penjumlahan tiga kaki terjepit masih ada' % n); gagal += 1
else: print('  ok  : nol penjumlahan tiga kaki yang terjepit')

print('-- kalimat arah sebaliknya ada di KETIGA tempat --')
for frasa, di in [
    ('Dari stok lama', 'kotak wujud (kaca HP)'),
    ('Piutang mengempis', 'kotak wujud + kartu desktop'),
    ('Kasbon kembali', 'kotak wujud + kartu desktop'),
    ('mencair balik jadi kas', 'kotak wujud + vonis kaca'),
    ('dua arah sekaligus', 'vonis kaca'),
    ('justru kembali jadi uang', 'vonis desktop'),
]:
    if frasa in SRC: print('  ok  : %-26s (%s)' % (frasa, di))
    else: print('  GAGAL: hilang - %s (%s)' % (frasa, di)); gagal += 1

print('-- saklar membaca tanda ASLI, bukan hasil jepitan --')
for pola, ket in [
    (r"kakiV\.filter\(x => x\[1\] < 0\)", 'vonis kaca memisahkan kaki turun'),
    (r"kakiW\.filter\(x => x\[1\] < 0\)", 'vonis desktop memisahkan kaki turun'),
    (r"kaki\.filter\(x => x\[1\] < 0\)", 'kotak wujud memisahkan kaki turun'),
]:
    if re.search(pola, SRC): print('  ok  :', ket)
    else: print('  GAGAL: hilang -', ket); gagal += 1

print('-- kontrol positif --')
racun = SRC + "\nvar w = Math.max(0, jadiStok) + Math.max(0, jadiPiutang) + Math.max(0, jadiKasbon);\n"
if len(TERLARANG.findall(racun)) > n: print('  ok  : bentuk terlarang yang disuntik TERLIHAT')
else: print('  GAGAL: penjaga BUTA'); gagal += 1

sys.exit(1 if gagal else print('SEMUA LULUS') or 0)
