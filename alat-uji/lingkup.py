#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lingkup.py — pemeriksa STATIS: nama fungsi yang DIPANGGIL di script sebaris sebuah halaman tapi tidak
pernah DIDEKLARASIKAN di mana pun (function/const/let/var/parameter/import) dan bukan
global peramban. Menangkap kelas cacat yang lolos pemeriksaan sintaks: salah nama di dalam
fungsi yang baru jalan sesudah ketukan.

Sasaran: kasir-darurat-nominal.html (satu <script> klasik). Sampai 2 Okt 2026 sasarannya modul index.html; sejak sistem lama
& kasir.html pensiun (owner 3 Okt 2026) index.html hanya halaman pengalih tanpa script. /baru/ (modul ES) dijaga periksa_impor.py +
kotak pasir uji_*_baru.

Kasar: tidak memahami lingkup — nama yang dideklarasikan DI MANA PUN dianggap ada. Jadi ia
tidak menangkap "benar namanya, salah lingkupnya". Untuk itu ada kotak pasir & uji peramban.

  python3 alat-uji/lingkup.py [berkas.html]  → 0 bersih, 2 ada nama tanpa deklarasi (bawaan kasir-darurat-nominal.html)
  python3 alat-uji/lingkup.py --kontrol      → suntik panggilan ke nama palsu, wajib tertangkap (3 bila tidak)
"""
import re, sys, os

AKAR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

GLOBAL = set('''window document localStorage sessionStorage console alert confirm prompt setTimeout setInterval
clearTimeout clearInterval fetch Promise Date Math JSON Object Array String Number Boolean Map Set parseInt parseFloat
isNaN isFinite encodeURIComponent decodeURIComponent encodeURI decodeURI Blob URL Error TypeError RangeError navigator
location history requestAnimationFrame cancelAnimationFrame matchMedia crypto TextEncoder TextDecoder Intl Symbol
Uint8Array Uint16Array Uint32Array Int32Array Float64Array ArrayBuffer DataView FileReader Image getComputedStyle scrollTo scroll
open print btoa atob queueMicrotask Function RegExp WeakMap WeakSet Reflect Proxy Event CustomEvent KeyboardEvent
MouseEvent TouchEvent PointerEvent InputEvent MutationObserver ResizeObserver IntersectionObserver performance screen
innerWidth innerHeight devicePixelRatio addEventListener removeEventListener dispatchEvent HTMLElement Node Element
visualViewport Audio AbortController escape unescape eval arguments undefined NaN Infinity globalThis self
Notification Option DOMParser XMLSerializer FormData Headers Request Response Worker BigInt Number
requestIdleCallback cancelIdleCallback speechSynthesis SpeechSynthesisUtterance structuredClone'''.split())
KATA_KUNCI = set('if for while switch catch return function async await typeof new delete void throw else do try '
                 'yield of in instanceof class super this import export default extends static get set'.split())


def modul_dari(html):
    """Gabungan semua <script> sebaris (klasik atau type="module", tanpa src). Tanpa satu pun → berhenti (bukan 'bersih' dengan nol nama)."""
    blok = [m.group(2) for m in re.finditer(r'<script([^>]*)>(.*?)</script>', html, re.S | re.I) if 'src=' not in m.group(1).lower()]
    if not blok:
        sys.exit('TOLAK: tidak ada <script> sebaris — tidak ada yang diperiksa')
    return '\n'.join(blok)


def bungkam(js):
    """Buang komentar dan isi string/template supaya kata di dalamnya tidak terhitung."""
    js = re.sub(r'/\*.*?\*/', '', js, flags=re.S)
    js = re.sub(r'//[^\n]*', '', js)
    js = re.sub(r'`(?:[^`\\]|\\.)*`', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), js)   # spasi, bukan '_' (huruf identifier)
    js = re.sub(r"'(?:[^'\\\n]|\\.)*'", '""', js)
    js = re.sub(r'"(?:[^"\\\n]|\\.)*"', '""', js)
    return js


def deklarasi(js):
    d = set(re.findall(r'\bfunction\s+([A-Za-z_$][\w$]*)', js))
    d |= set(re.findall(r'\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)', js))
    for m in re.finditer(r'\b(?:const|let|var)\s+\{([^}]*)\}', js):
        d |= set(re.findall(r'[A-Za-z_$][\w$]*', m.group(1)))
    for m in re.finditer(r'\b(?:const|let|var)\s+\[([^\]]*)\]', js):
        d |= set(re.findall(r'[A-Za-z_$][\w$]*', m.group(1)))
    d |= set(re.findall(r'\b(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*[^;]*?,\s*([A-Za-z_$][\w$]*)\s*=', js))
    for m in re.finditer(r'\(([^()]*)\)\s*=>', js):
        d |= set(re.findall(r'[A-Za-z_$][\w$]*', m.group(1)))
    for m in re.finditer(r'function\s*[\w$]*\s*\(([^()]*)\)', js):
        d |= set(re.findall(r'[A-Za-z_$][\w$]*', m.group(1)))
    d |= set(re.findall(r'\b([A-Za-z_$][\w$]*)\s*=>', js))
    for m in re.finditer(r'\bimport\s*\{([^}]*)\}', js):
        d |= set(re.findall(r'[A-Za-z_$][\w$]*', m.group(1)))
    d |= set(re.findall(r'\bimport\s+([A-Za-z_$][\w$]*)', js))
    d |= set(re.findall(r'\bcatch\s*\(\s*([A-Za-z_$][\w$]*)', js))
    d |= set(re.findall(r'\bclass\s+([A-Za-z_$][\w$]*)', js))
    return d


def periksa(html):
    js = bungkam(modul_dari(html))
    d = deklarasi(js)
    panggilan = re.findall(r'(?<![\w$.])([A-Za-z_$][\w$]*)\s*\(', js)
    hilang = sorted({c for c in panggilan if c not in d and c not in GLOBAL and c not in KATA_KUNCI})
    return len(d), hilang


def main(argv):
    berkas = os.path.join(AKAR, 'kasir-darurat-nominal.html')
    if '--kontrol' in argv:
        html = open(berkas, encoding='utf-8').read()
        jangkar = '\nvar DASAR = '
        assert html.count(jangkar) == 1, 'kontrol basi: jangkar ' + jangkar.strip()
        html = html.replace(jangkar, '\nfungsiTakAdaKontrol();' + jangkar, 1)
        n, hilang = periksa(html)
        if 'fungsiTakAdaKontrol' in hilang:
            print('KONTROL   : panggilan ke nama palsu tertangkap (deklarasi %d)' % n)
            return 0
        print('KONTROL GAGAL: nama palsu TIDAK tertangkap — alat buta')
        return 3
    if argv and not argv[0].startswith('--'):
        berkas = argv[0] if os.path.isabs(argv[0]) else os.path.join(os.getcwd(), argv[0])
    html = open(berkas, encoding='utf-8').read()
    n, hilang = periksa(html)
    print('DEKLARASI : %d' % n)
    print('TANPA DEKLARASI: %s' % (hilang if hilang else 'nihil'))
    return 2 if hilang else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
