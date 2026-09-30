#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
periksa_penangan_ganda.py — nama penangan ketukan yang GANDA dalam satu layar /baru/ (peta yang diberikan ke `delegasi(akar, …)`).

Kenapa: peta penangan ditulis sebagai satu objek besar; dua kunci bernama sama → yang belakangan menang DIAM-DIAM (tidak ada galat), tombol yang
lebih dulu tidak pernah jalan. 1 Okt 2026: penangan baru `ktKetik` / keadaan `ktYakin` bentrok dengan layar Kantong di stok.js — tombol baru
langsung tampil "YAKIN" dan isian barunya mati. Tertangkap di Browser pane, bukan di uji.

    python3 alat-uji/periksa_penangan_ganda.py            → 0 temuan = lulus (keluar 0), ada temuan = keluar 1
    python3 alat-uji/periksa_penangan_ganda.py --kontrol  → kunci ganda yang disisipkan wajib ketahuan (keluar 3 kalau diam)
"""
import glob, os, re, sys
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
from periksa_impor import buang_komentar_teks  # noqa: E402


def kunci_objek(t, i):
    """t[i] = '{' → daftar (nama, baris) kunci tingkat pertama objek itu (komentar & teks sudah dikosongkan)."""
    d = 0; j = i; out = []; n = len(t)
    while j < n:
        c = t[j]
        if c in '{[(':
            d += 1
        elif c in '}])':
            d -= 1
            if d == 0: return out
        elif d == 1:
            m = re.match(r'([A-Za-z_$][\w$]*)\s*:(?!:)', t[j:])
            if m and re.match(r'[\s,{]', t[j - 1]):
                out.append((m.group(1), t.count('\n', 0, j) + 1)); j += m.end(); continue
        j += 1
    return out


def periksa(teks_per_berkas):
    temuan = []
    for f, asli in teks_per_berkas:
        t = buang_komentar_teks(asli)
        for peta in set(re.findall(r'delegasi\(\s*\w+\s*,\s*([A-Za-z_$][\w$]*)\s*\)', t)):
            m = re.search(r'(?:const|let|var)\s+' + re.escape(peta) + r'\s*=\s*(?:Object\.assign\(\s*)?\{', t)
            if not m: continue
            lihat = {}
            for nama, baris in kunci_objek(t, m.end() - 1):
                if nama in lihat: temuan.append('%s:%d → penangan "%s" ganda (juga di baris %d) — yang belakangan menang diam-diam' % (f, baris, nama, lihat[nama]))
                else: lihat[nama] = baris
    return temuan


def berkas():
    return [(os.path.relpath(p, AKAR), open(p, encoding='utf-8').read()) for p in sorted(glob.glob(os.path.join(AKAR, 'baru', 'js', '**', '*.js'), recursive=True))]


if __name__ == '__main__':
    B = berkas()
    if '--kontrol' in sys.argv:
        f, t = next(x for x in B if x[0].endswith(os.path.join('layar', 'stok.js')))
        m = re.search(r'const AKSI = Object\.assign\(\{\n', t)
        rusak = t[:m.end()] + "    bukaCocok: () => null,\n" + t[m.end():] if m else t
        g = periksa([(f, rusak)])
        print(('BERBUNYI ' if g else 'DIAM!!   ') + 'penangan bukaCocok disisipkan ganda di ' + f + ' → ' + (g[0][:140] if g else '-'))
        sys.exit(0 if g else 3)
    g = periksa(B)
    print('PERIKSA PENANGAN GANDA /baru/: %d berkas · %d temuan' % (len(B), len(g)))
    for x in g: print('   ✗ ' + x)
    sys.exit(1 if g else 0)
