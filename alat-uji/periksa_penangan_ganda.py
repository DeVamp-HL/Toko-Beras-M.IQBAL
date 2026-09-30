#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
periksa_penangan_ganda.py — nama penangan ketukan yang GANDA dalam satu layar /baru/ (peta yang diberikan ke `delegasi(akar, …)`, termasuk peta kedua
yang digabung lewat Object.assign, mis. `aksiPanelWadah(…)`), dan kunci GANDA di keadaan awal layar (`const awal = () => ({ … })`).

Kenapa: peta penangan dan keadaan awal ditulis sebagai objek besar; dua kunci bernama sama → yang belakangan menang DIAM-DIAM (tidak ada galat).
1 Okt 2026: penangan baru `ktKetik` bentrok dengan layar Kantong di stok.js (isian baru mati) dan keadaan `ktYakin: false` kalah oleh `ktYakin: {}` (objek
kosong = benar → tombol baru langsung tampil "YAKIN"). Tertangkap di Browser pane, bukan di uji. Tinjauan #80: versi pertama cuma membaca objek pertama
Object.assign, jadi bentrok dengan peta panel wadah lolos.

    python3 alat-uji/periksa_penangan_ganda.py            → 0 temuan = lulus (keluar 0), ada temuan = keluar 1
    python3 alat-uji/periksa_penangan_ganda.py --kontrol  → empat kunci ganda yang disisipkan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import glob, os, re, sys
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
from periksa_impor import buang_komentar_teks  # noqa: E402


def tutup(t, i):
    """t[i] = pembuka ({[( → indeks penutupnya (komentar & teks sudah dikosongkan)."""
    d = 0; j = i
    while j < len(t):
        if t[j] in '{[(': d += 1
        elif t[j] in '}])':
            d -= 1
            if d == 0: return j
        j += 1
    return len(t) - 1


def kunci_objek(t, i):
    """t[i] = '{' → daftar (nama, baris) kunci tingkat pertama objek itu."""
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


def argumen(t, i):
    """t[i] = '(' → daftar indeks awal tiap argumen tingkat pertama."""
    akhir = tutup(t, i); out = []; j = i + 1; d = 0; mulai = j
    while j < akhir:
        c = t[j]
        if c in '{[(': d += 1
        elif c in '}])': d -= 1
        elif c == ',' and d == 0: out.append(mulai); mulai = j + 1
        j += 1
    out.append(mulai)
    return [a + len(t[a:akhir]) - len(t[a:akhir].lstrip()) for a in out if t[a:akhir].strip()]


def kunci_fungsi(nama, semua):
    """Kunci objek yang DIKEMBALIKAN `export function nama(…)` (return { … } / return IDENT; dengan const IDENT = { … } di badannya)."""
    for f, t in semua:
        m = re.search(r'export\s+function\s+' + re.escape(nama) + r'\s*\(', t)
        if not m: continue
        b0 = t.index('{', tutup(t, m.end() - 1)); b1 = tutup(t, b0)
        d = 0; j = b0   # hanya pernyataan di tingkat badan fungsi itu sendiri (bukan return / const di fungsi panah di dalamnya)
        while j < b1:
            c = t[j]
            if c in '{[(': d += 1
            elif c in '}])': d -= 1
            elif d == 1:
                r = re.match(r'return\s+\{', t[j:])
                if r and not re.match(r'[\w$]', t[j - 1]): return f, kunci_objek(t, j + r.end() - 1)
                r = re.match(r'return\s+([A-Za-z_$][\w$]*)\s*;', t[j:])
                if r and not re.match(r'[\w$]', t[j - 1]):
                    c2 = re.search(r'(?:const|let|var)\s+' + re.escape(r.group(1)) + r'\s*=\s*\{', t[b0:j])
                    if c2: return f, kunci_objek(t, b0 + c2.end() - 1)
            j += 1
    return None, []


def kunci_dari_argumen(t, a, semua, f):
    """Satu argumen Object.assign / satu nilai peta: objek harfiah → kuncinya; panggilan fungsi → kunci objek yang dikembalikannya."""
    if t[a] == '{': return [(f, n, b) for n, b in kunci_objek(t, a)]
    m = re.match(r'([A-Za-z_$][\w$.]*)\s*\(', t[a:])
    if m:
        g, ks = kunci_fungsi(m.group(1).split('.')[-1], semua)
        return [(g, n, b) for n, b in ks]
    return []


def periksa(teks_per_berkas, semua=None):
    temuan = []
    bersih = [(f, buang_komentar_teks(x)) for f, x in teks_per_berkas]
    semua = [(f, buang_komentar_teks(x)) for f, x in semua] if semua else bersih
    for f, t in bersih:
        for peta in sorted(set(re.findall(r'delegasi\(\s*\w+\s*,\s*([A-Za-z_$][\w$]*)\s*\)', t))):
            m = re.search(r'(?:const|let|var)\s+' + re.escape(peta) + r'\s*=\s*', t)
            if not m: continue
            daftar = []; j = m.end()
            if t.startswith('Object.assign', j): daftar += [x for a in argumen(t, t.index('(', j)) for x in kunci_dari_argumen(t, a, semua, f)]
            elif t[j] == '{': daftar += kunci_dari_argumen(t, j, semua, f)
            for g in re.finditer(r'Object\.assign\(\s*' + re.escape(peta) + r'\s*,', t):   # peta yang ditambah belakangan
                daftar += [x for a in argumen(t, t.index('(', g.start()))[1:] for x in kunci_dari_argumen(t, a, semua, f)]
            lihat = {}
            for g, nama, baris in daftar:
                if nama in lihat: temuan.append('%s:%d → penangan "%s" ganda (juga di %s:%d) — yang belakangan menang diam-diam' % (g, baris, nama, lihat[nama][0], lihat[nama][1]))
                else: lihat[nama] = (g, baris)
        for m in re.finditer(r'const\s+awal\s*=\s*\(\)\s*=>\s*\(\s*\{', t):
            lihat = {}
            for nama, baris in kunci_objek(t, m.end() - 1):
                if nama in lihat: temuan.append('%s:%d → keadaan awal "%s" ganda (juga di baris %d) — yang belakangan menang diam-diam' % (f, baris, nama, lihat[nama]))
                else: lihat[nama] = baris
    return temuan


def berkas():
    return [(os.path.relpath(p, AKAR), open(p, encoding='utf-8').read()) for p in sorted(glob.glob(os.path.join(AKAR, 'baru', 'js', '**', '*.js'), recursive=True))]


if __name__ == '__main__':
    B = berkas()
    if '--kontrol' in sys.argv:
        kode = 0; f, t = next(x for x in B if x[0].endswith(os.path.join('layar', 'stok.js')))
        _, panel = kunci_fungsi('aksiPanelWadah', [(g, buang_komentar_teks(x)) for g, x in B]); nPanel = panel[0][0] if panel else 'tidakAda'
        m = re.search(r'const AKSI = Object\.assign\(\{\n', t); s0 = re.search(r'const awal = \(\) => \(\{ ', t); dasar = set(periksa([(f, t)], B))
        for nama, kunci, rusak in [('penangan bukaCocok ganda di peta pertama', 'bukaCocok', t[:m.end()] + "    bukaCocok: () => null,\n" + t[m.end():] if m else t),
                                   ('penangan ' + nPanel + ' bentrok dengan peta panel wadah (Object.assign argumen kedua)', nPanel, t[:m.end()] + "    " + nPanel + ": () => null,\n" + t[m.end():] if m else t),
                                   ('keadaan awal tab ganda', 'tab', t[:s0.end()] + "tab: 'x', " + t[s0.end():] if s0 else t)]:
            g = [x for x in periksa([(f, rusak)], [(x, rusak if x == f else y) for x, y in B]) if x not in dasar and '"' + kunci + '"' in x]   # hanya bunyi BARU atas kunci sisipan
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        fj, tj = next(x for x in B if x[0].endswith(os.path.join('layar', 'jual.js'))); mj = re.search(r'const aksi = \{\n', tj)   # peta yang ditambah belakangan: Object.assign(aksi, aksiPanelWadah(…))
        rj = tj[:mj.end()] + "    " + nPanel + ": () => null,\n" + tj[mj.end():] if mj else tj
        g = [x for x in periksa([(fj, rj)], [(x, rj if x == fj else y) for x, y in B]) if '"' + nPanel + '"' in x and fj in x]
        print(('BERBUNYI ' if g else 'DIAM!!   ') + 'penangan ' + nPanel + ' di jual.js bentrok dengan Object.assign(aksi, aksiPanelWadah(…)) → ' + (g[0][:140] if g else '-'))
        if not g: kode = 3
        sys.exit(kode)
    g = periksa(B)
    print('PERIKSA PENANGAN GANDA /baru/: %d berkas · %d temuan' % (len(B), len(g)))
    for x in g: print('   ✗ ' + x)
    sys.exit(1 if g else 0)
