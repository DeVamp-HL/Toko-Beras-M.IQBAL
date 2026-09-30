#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
periksa_komentar.py — komentar `//` di TENGAH baris yang diikuti kode (kode itu ikut jadi komentar dan tidak pernah jalan).

Kenapa: berkas /baru/ banyak menulis beberapa pernyataan dalam satu baris. Komentar `//` yang disisipkan di tengahnya menelan sisa baris.
jsc & uji logika tetap lulus bila baris itu cuma di layar; di peramban tombolnya jatuh ReferenceError. Terjadi dua kali 30 Sep 2026
(no. 4) dan sekali 1 Okt 2026 (tombol simpan Cocokkan: `const al` tertelan). Aturan: komentar di baris sendiri, atau di UJUNG baris.

    python3 alat-uji/periksa_komentar.py            → 0 temuan = lulus (keluar 0), ada temuan = keluar 1
    python3 alat-uji/periksa_komentar.py --kontrol  → komentar penelan yang disisipkan wajib ketahuan (keluar 3 kalau diam)
"""
import glob, os, re, sys
AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
# sisa sesudah // yang mirip kode: pernyataan baru sesudah titik koma, penutup panggilan, fungsi panah
KODE = re.compile(r'(;\s*(const|let|var|if|return|for|await)\b|\}\);|\)\s*=>)')


def potong(baris):
    """(kode, komentar) — // di luar teks '…' "…" `…` dan bukan bagian regex yang di-escape (\\/) atau URL (://)."""
    q = None; i = 0
    while i < len(baris):
        c = baris[i]
        if q:
            if c == '\\': i += 2; continue
            if c == q: q = None
        else:
            if c in '\'"`': q = c
            elif baris.startswith('//', i) and (i == 0 or baris[i - 1] not in ':\\'): return baris[:i], baris[i + 2:]
        i += 1
    return baris, None


def periksa(teks_per_berkas):
    out = []
    for f, t in teks_per_berkas:
        for no, l in enumerate(t.split('\n'), 1):
            a, k = potong(l)
            if k is not None and a.strip() and KODE.search(k): out.append('%s:%d → kode sesudah // tidak pernah jalan: %s' % (f, no, k.strip()[:120]))
    return out


def berkas():
    daftar = sorted(glob.glob(os.path.join(AKAR, 'baru', 'js', '**', '*.js'), recursive=True)) + [os.path.join(AKAR, 'sw-kasir.js')]
    return [(os.path.relpath(p, AKAR), open(p, encoding='utf-8').read()) for p in daftar if os.path.exists(p)]


if __name__ == '__main__':
    B = berkas()
    if '--kontrol' in sys.argv:
        f, t = next((x for x in B if x[0].endswith('stok.js')), B[0])
        rusak = t.replace('\n', '\n  hitung(1);   // catatan const b = f(); g.forEach((x) => h(x));\n', 1)   # bentuk kejadian 1 Okt
        g = periksa([(f, rusak)])
        print(('BERBUNYI ' if g else 'DIAM!!   ') + 'komentar penelan disisipkan di ' + f + ' → ' + (g[0][:140] if g else '-'))
        sys.exit(0 if g else 3)
    g = periksa(B)
    print('PERIKSA KOMENTAR /baru/: %d berkas · %d temuan' % (len(B), len(g)))
    for x in g: print('   ✗ ' + x)
    sys.exit(1 if g else 0)
