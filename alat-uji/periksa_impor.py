#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
periksa_impor.py — fungsi yang DIPANGGIL di satu modul /baru/ tetapi hanya diekspor modul lain dan TIDAK diimpor / dideklarasikan di modul itu.

Kenapa: uji jsc memakai bundel_baru.py yang MEMBUANG semua `import` dan menjadikan semua ekspor global — impor yang lupa ditulis tetap lulus di
jsc, tetapi di peramban (modul ES) jatuh `ReferenceError` saat barisnya dijalankan. 30 Sep 2026: `jual-logika.js` memanggil `denganCacheSementara`
tanpa impor → tombol "ISI ULANG · CATAT N TAKAR" untuk wadah yang sudah aktif diam tanpa kabar (galat di konsol saja).

    python3 alat-uji/periksa_impor.py            → 0 temuan = lulus (keluar 0), ada temuan = keluar 1
    python3 alat-uji/periksa_impor.py --kontrol  → impor yang dicabut wajib ketahuan (keluar 3 kalau diam)
"""
import os, re, sys
AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
DIR = os.path.join(AKAR, 'baru', 'js')
KATA = set('if for while switch catch function return typeof new await case do else try finally throw delete void in of instanceof with yield super this class import export default async const let var'.split())
GLOBAL = set('Object Array String Number Boolean Math JSON Date Promise Set Map WeakMap RegExp Error TypeError isFinite isNaN parseInt parseFloat setTimeout clearTimeout setInterval clearInterval requestAnimationFrame cancelAnimationFrame fetch alert confirm prompt encodeURIComponent decodeURIComponent atob btoa structuredClone queueMicrotask Intl Symbol Response Blob URL FileReader Image Event CustomEvent getComputedStyle matchMedia'.split())


def buang_komentar_teks(t):
    """Komentar & literal teks dikosongkan (panjang & baris tetap) supaya nama di dalamnya tidak dihitung; isi `${…}` template TETAP diperiksa."""
    n = len(t); out = []
    def kode(i, tutup):
        # salin kode sampai kurung kurawal penutup (tutup=True, untuk ${…}) atau akhir berkas; → indeks sesudahnya
        dalam = 0
        while i < n:
            c = t[i]
            if t.startswith('//', i): j = t.find('\n', i); j = n if j < 0 else j; out.append(' ' * (j - i)); i = j; continue
            if t.startswith('/*', i): j = t.find('*/', i + 2); j = n if j < 0 else j + 2; out.append(re.sub(r'[^\n]', ' ', t[i:j])); i = j; continue
            if c in '\'"':
                j = i + 1
                while j < n and t[j] != c and t[j] != '\n':
                    j += 2 if t[j] == '\\' else 1
                out.append(' ' * (min(j + 1, n) - i)); i = j + 1; continue
            if c == '`': out.append(' '); i = templat(i + 1); continue
            if tutup and c == '{': dalam += 1
            if tutup and c == '}':
                if dalam == 0: out.append(' '); return i + 1
                dalam -= 1
            out.append(c); i += 1
        return i
    def templat(i):
        while i < n:
            c = t[i]
            if c == '\\': out.append('  ' if t[i + 1:i + 2] != '\n' else ' \n'); i += 2; continue
            if c == '`': out.append(' '); return i + 1
            if t.startswith('${', i): out.append('  '); i = kode(i + 2, True); continue
            out.append('\n' if c == '\n' else ' '); i += 1
        return i
    kode(0, False)
    return ''.join(out)


def berkas_js():
    for a, _, fs in os.walk(DIR):
        for f in fs:
            if f.endswith('.js'): yield os.path.join(a, f)


def ekspor(t):
    s = set(re.findall(r'^export\s+(?:async\s+)?(?:function\*?|const|let|var|class)\s+([A-Za-z_$][\w$]*)', t, re.M))
    for blok in re.findall(r'^export\s*\{([^}]*)\}', t, re.M):
        for x in blok.split(','):
            x = x.strip()
            if x: s.add(x.split(' as ')[-1].strip())
    return s


def lokal(t):
    s = set(re.findall(r'\bfunction\*?\s+([A-Za-z_$][\w$]*)', t)) | set(re.findall(r'\b(?:const|let|var|class)\s+([A-Za-z_$][\w$]*)', t))
    for blok in re.findall(r'\b(?:const|let|var)\s*\{([^}]*)\}\s*=', t) + re.findall(r'\b(?:const|let|var)\s*\[([^\]]*)\]\s*=', t):
        for x in blok.split(','):
            x = x.strip().split(':')[-1].split('=')[0].strip()
            if x: s.add(x)
    for blok in re.findall(r'^import\s*\{([^}]*)\}\s*from', t, re.M | re.S):
        for x in blok.split(','):
            x = x.strip()
            if x: s.add(x.split(' as ')[-1].strip())
    s |= set(re.findall(r'^import\s+\*\s+as\s+([A-Za-z_$][\w$]*)', t, re.M)) | set(re.findall(r'^import\s+([A-Za-z_$][\w$]*)\s+from', t, re.M))
    # parameter fungsi panah & biasa: (a, b) => · function x(a, b) · a => …
    for blok in re.findall(r'\(([^()]*)\)\s*=>', t) + re.findall(r'\bfunction\*?\s*[A-Za-z_$]*\s*\(([^()]*)\)', t):
        for x in blok.split(','):
            x = re.sub(r'[{}\[\]]', ' ', x).split('=')[0].strip().split(':')[-1].strip()
            for y in x.split():
                if re.match(r'^[A-Za-z_$][\w$]*$', y): s.add(y)
    s |= set(re.findall(r'\b([A-Za-z_$][\w$]*)\s*=>', t))
    # definisi metode singkat di objek/kelas: `  mulai() {` · `async simpan(x) {`
    s |= set(re.findall(r'(?:^|[,{;])\s*(?:async\s+)?([A-Za-z_$][\w$]*)\s*\([^()]*\)\s*\{', t, re.M))
    return s


def periksa(teks_per_berkas):
    ek = {p: ekspor(t) for p, t in teks_per_berkas.items()}
    semua_ekspor = {}
    for p, e in ek.items():
        for x in e: semua_ekspor.setdefault(x, []).append(p)
    temuan = []
    for p, t in teks_per_berkas.items():
        bersih = buang_komentar_teks(t); dekl = lokal(bersih) | ek[p]
        for m in re.finditer(r'(?<![\w$.])([A-Za-z_$][\w$]*)\s*\(', bersih):
            x = m.group(1)
            if x in KATA or x in GLOBAL or x in dekl or x not in semua_ekspor: continue
            baris = bersih.count('\n', 0, m.start()) + 1
            temuan.append((os.path.relpath(p, AKAR), baris, x, ', '.join(os.path.relpath(q, AKAR) for q in semua_ekspor[x])))
    uniq = {}
    for f, b, x, asal in temuan: uniq.setdefault((f, x), (b, asal))
    return sorted((f, b, x, asal) for (f, x), (b, asal) in uniq.items())


def baca():
    return {p: open(p, encoding='utf-8').read() for p in berkas_js()}


if __name__ == '__main__':
    T = baca()
    if '--kontrol' in sys.argv:
        p = os.path.join(DIR, 'layar', 'jual-logika.js'); rusak = dict(T)
        a = ", denganCacheSementara } from '../data/toko.js';"
        if a not in T[p]: print('KONTROL BASI  impor denganCacheSementara di jual-logika.js'); sys.exit(3)
        rusak[p] = T[p].replace(a, " } from '../data/toko.js';")
        h = periksa(rusak); kena = [x for x in h if x[0].endswith('jual-logika.js') and x[2] == 'denganCacheSementara']
        print(('BERBUNYI ' if kena else 'DIAM!!   ') + 'impor denganCacheSementara dicabut dari jual-logika.js → ' + (('%s:%d %s' % kena[0][:3]) if kena else '-'))
        sys.exit(0 if kena else 3)
    h = periksa(T)
    for f, b, x, asal in h: print('   ✗ %s:%d memanggil %s() tanpa impor (diekspor %s)' % (f, b, x, asal))
    print('PERIKSA IMPOR /baru/: %d berkas · %d temuan' % (len(T), len(h)))
    sys.exit(1 if h else 0)
