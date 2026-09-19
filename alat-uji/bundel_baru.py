#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bundel_baru.py — menyatukan modul ES sistem baru (baru/js/**) jadi SATU skrip polos untuk jsc.
jsc tidak memuat modul ES lewat berkas, jadi baris `import …` dibuang dan kata `export` dicabut;
semua deklarasi fungsi terangkat (hoisting) sehingga urutan berkas tidak menentukan.
Dipakai alat uji saja — peramban memuat modulnya apa adanya.

    from bundel_baru import bundel
    js = bundel(['baru/js/data/koleksi.js', 'baru/js/data/toko.js', ...])
"""
import os, re

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

PRELUDE = r"""
// ---- prelude jsc: pengganti peramban yang dipakai lapisan data/layar ----
var __ls = {};
var localStorage = { getItem: function (k) { return Object.prototype.hasOwnProperty.call(__ls, k) ? __ls[k] : null; },
  setItem: function (k, v) { __ls[k] = String(v); }, removeItem: function (k) { delete __ls[k]; } };
var __dom = {};   // id -> { value } — stokMaksJalur() (mesin beku) membaca #jualKarungBerat lewat document
var document = { getElementById: function (id) { return __dom[id] || null; } };
var window = this; var navigator = { onLine: true };
if (typeof console === 'undefined') { var console = { log: print, error: print, warn: print }; }
"""


def polos(teks):
    """Buang import, cabut export. Hanya bentuk yang dipakai di baru/js: `import { a, b } from '…';`,
    `import x from '…';`, `export function`, `export const/let`, `export { a, b };`."""
    teks = re.sub(r'^\s*import\s+[^;]*?from\s+[\'"][^\'"]+[\'"];\s*$', '', teks, flags=re.M)
    teks = re.sub(r'^\s*import\s+[\'"][^\'"]+[\'"];\s*$', '', teks, flags=re.M)
    teks = re.sub(r'^\s*export\s*\{[^}]*\};?\s*$', '', teks, flags=re.M)
    teks = re.sub(r'^(\s*)export\s+(default\s+)?(async\s+)?(function|const|let|class)\b', r'\1\3\4', teks, flags=re.M)
    return teks


def bundel(daftar, prelude=True):
    bagian = [PRELUDE] if prelude else []
    for p in daftar:
        jalur = p if os.path.isabs(p) else os.path.join(AKAR, p)
        bagian.append('\n// ===== ' + p + ' =====\n' + polos(open(jalur, encoding='utf-8').read()))
    return '\n'.join(bagian)


MODUL_DATA = ['baru/js/data/koleksi.js', 'baru/js/mesin/pembantu.js', 'baru/js/data/toko.js', 'baru/js/mesin/beku.js']

if __name__ == '__main__':
    import sys
    sys.stdout.write(bundel(MODUL_DATA))
