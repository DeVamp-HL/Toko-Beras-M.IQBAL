#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_onclick_aman.py — penjaga: nilai yang masuk atribut onclick WAJIB lewat escapeHtml.

Bentuk yang dilarang:  JSON.stringify(x).replace(/"/g, '&quot;')
Ia hanya menutup kutip ganda. Nilai yang MEMUAT teks entitas (mis. `A&quot;);alert(1);(`)
di-decode peramban jadi kutip sungguhan, dan argumennya pecah keluar dari string:
    bukaLembarBayarBon("A");alert(1);("")
escapeHtml meng-escape & LEBIH DULU, jadi entitas tidak pernah terbentuk. Nama pemasok dan
nama pelanggan di toko ini TEKS BEBAS yang diketik orang — jadi ini bukan kemungkinan teoretis.

SATU PENGECUALIAN yang disengaja (index.html ~34195):
    (x.k || ("pindahDariMenu('" + x.h + "')")).replace(/"/g, '&quot;')
Di situ yang di-escape adalah KODE, bukan nilai; x.h cuma nama halaman tetap
('piutang','pemasok','tutup','harga','stok'). Memakai escapeHtml justru merusaknya
(ia meng-escape ' dan memutus pemanggilan). Dibiarkan, dan dihitung: tepat SATU.
"""
import io, re, sys, pathlib

AKAR = pathlib.Path(__file__).resolve().parent.parent
SRC = (AKAR / 'index.html').read_text(encoding='utf-8')
POLA = re.compile(r"JSON\.stringify\([^;]{0,120}?\)\s*\.replace\(/\"/g, *'&quot;'\)")
EKOR = ".replace(/\"/g, '&quot;')"

def periksa(teks):
    return len(POLA.findall(teks)), teks.count(EKOR)

nJson, nEkor = periksa(SRC)
gagal = 0
print('-- nilai di onclick --')
if nJson: print('  GAGAL: %d JSON.stringify masih dibungkus .replace(/"/g)' % nJson); gagal += 1
else: print('  ok  : nol JSON.stringify yang dibungkus .replace')
if nEkor != 1: print('  GAGAL: .replace(/"/g,&quot;) ada %d, seharusnya tepat 1 (pengecualian kode di ~34195)' % nEkor); gagal += 1
else: print('  ok  : tepat 1 pengecualian yang disengaja (kode, bukan nilai)')

# KONTROL POSITIF: suntik bentuk terlarang, penjaga WAJIB berbunyi.
print('-- kontrol positif --')
racun = SRC + "\nvar x = 'onclick=\"f(' + JSON.stringify(nama).replace(/\"/g, '&quot;') + ')\"';\n"
n2, _ = periksa(racun)
if n2 > nJson: print('  ok  : bentuk terlarang yang disuntik TERLIHAT (%d -> %d)' % (nJson, n2))
else: print('  GAGAL: penjaga BUTA — bentuk terlarang disuntik tapi tidak terlihat'); gagal += 1

sys.exit(1 if gagal else print('SEMUA LULUS') or 0)
