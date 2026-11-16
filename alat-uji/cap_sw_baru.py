#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cap_sw_baru.py — MENGECAP baru/sw-baru.js saat TERBIT (putaran T1 langkah 4, 16 Nov 2026: tablet kasir bisa dibuka tanpa internet).

Di repo, sw-baru.js TIDAK dicap (VERSI 'belum-dicap', daftar kosong) — salinan seperti itu menolak dipasang. Job `terbitkan` (pages.yml) menjalankan
alat ini tepat sebelum folder dibungkus, jadi yang tayang di GitHub Pages selalu membawa:
  VERSI  = 12 huruf pertama commit yang diterbitkan        (versi baru = commit baru; tidak ada VERSI yang lupa dinaikkan)
  TERBIT = waktu commit itu (UTC)                          (commit yang sama diterbitkan ulang = salinan yang sama, tidak dipasang ulang)
  BERKAS = [jalur relatif dari baru/, sidik SHA-256]       untuk SEMUA berkas halaman: baru/*.html, baru/*.svg, baru/css/**.css, baru/js/**.js, dan gambar ../ yang dirujuk HTML
  LUAR   = modul Firebase dari CDN (modulepreload index.html + impor di baru/js) — alamat berversi
  HURUF  = stylesheet Google Fonts index.html

    python3 alat-uji/cap_sw_baru.py --tulis            cap baru/sw-baru.js di tempat (HANYA di runner terbit; jangan commit hasilnya)
    python3 alat-uji/cap_sw_baru.py --lihat            cetak ringkasan tanpa menulis
    opsi: --akar DIR (salinan lain, dipakai uji) · --versi V · --terbit ISO
"""
import os, re, sys, json, glob, hashlib, html, subprocess, datetime

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
SW = 'sw-baru.js'
TANDA = ('VERSI', 'TERBIT', 'BERKAS', 'LUAR', 'HURUF')


def sidik(jalur):
    with open(jalur, 'rb') as f: return hashlib.sha256(f.read()).hexdigest()


def daftar_berkas(akar):
    """→ [(jalur relatif dari baru/, jalur penuh)] berurutan; gambar ../ hanya yang dirujuk HTML & ada."""
    akar = os.path.abspath(akar); baru = os.path.join(akar, 'baru'); out = []
    # owner 17 Nov 2026 (butir 3): + baru/*.svg (logo toko di struk) — tablet yang dibuka tanpa internet tetap mencetak logonya
    pola = [os.path.join(baru, '*.html'), os.path.join(baru, '*.svg'), os.path.join(baru, 'css', '**', '*.css'), os.path.join(baru, 'js', '**', '*.js')]
    for p in pola:
        for f in sorted(glob.glob(p, recursive=True)):
            out.append((os.path.relpath(f, baru).replace(os.sep, '/'), f))
    luar = set()
    for rel, f in list(out):
        if not rel.endswith('.html'): continue
        teks = open(f, encoding='utf-8').read()
        for x in re.findall(r'<(?:link|img|script)\b[^>]*\s(?:href|src)="(\.\./[^"?#]+)"', teks):
            penuh = os.path.normpath(os.path.join(baru, x))
            if os.path.isfile(penuh) and os.path.dirname(penuh) == akar: luar.add(x)
    out += [(x, os.path.normpath(os.path.join(baru, x))) for x in sorted(luar)]
    return [(r, f) for r, f in out if os.path.basename(r) != SW]


def alamat_luar(akar):
    baru = os.path.join(akar, 'baru'); alamat = set()
    idx = open(os.path.join(baru, 'index.html'), encoding='utf-8').read()
    alamat |= set(re.findall(r'<link rel="modulepreload" href="(https://www\.gstatic\.com/firebasejs/[^"]+)"', idx))
    for f in glob.glob(os.path.join(baru, 'js', '**', '*.js'), recursive=True):
        alamat |= set(re.findall(r"""from\s*['"](https://www\.gstatic\.com/firebasejs/[^'"]+)['"]""", open(f, encoding='utf-8').read()))
    return sorted(alamat)


def alamat_huruf(akar):
    idx = open(os.path.join(akar, 'baru', 'index.html'), encoding='utf-8').read()
    m = re.search(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com/[^"]+)"', idx)
    return html.unescape(m.group(1)) if m else ''


def versi_git(akar):
    try:
        sha = subprocess.run(['git', '-C', akar, 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
        waktu = subprocess.run(['git', '-C', akar, 'log', '-1', '--format=%cI'], capture_output=True, text=True, check=True).stdout.strip()
        t = datetime.datetime.fromisoformat(waktu).astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        return sha[:12], t
    except Exception:
        return None, None


def cap(teks, nilai):
    """Ganti tiap baris `const X = …;   // CAP:X` dengan nilai JSON. Galat kalau tanda hilang / ganda."""
    for k in TANDA:
        pola = re.compile(r'^const ' + k + r' = .*;   // CAP:' + k + r'$', re.M)
        if len(pola.findall(teks)) != 1: raise SystemExit('cap_sw_baru: tanda CAP:' + k + ' tidak tepat satu di ' + SW)
        teks = pola.sub(lambda m: 'const ' + k + ' = ' + json.dumps(nilai[k], ensure_ascii=False) + ';   // CAP:' + k, teks)
    return teks


def susun(akar, versi=None, terbit=None):
    v, t = versi_git(akar)
    versi = versi or os.environ.get('GITHUB_SHA', '')[:12] or v
    terbit = terbit or t
    if not versi or not re.match(r'^[0-9a-zA-Z._-]{4,40}$', versi): raise SystemExit('cap_sw_baru: VERSI tidak diketahui (bukan checkout git? pakai --versi)')
    berkas = [[r, sidik(f)] for r, f in daftar_berkas(akar)]
    return {'VERSI': versi, 'TERBIT': terbit or '', 'BERKAS': berkas, 'LUAR': alamat_luar(akar), 'HURUF': alamat_huruf(akar)}


def main(argv):
    akar = AKAR; versi = terbit = None
    if '--akar' in argv: akar = os.path.abspath(argv[argv.index('--akar') + 1])
    if '--versi' in argv: versi = argv[argv.index('--versi') + 1]
    if '--terbit' in argv: terbit = argv[argv.index('--terbit') + 1]
    nilai = susun(akar, versi, terbit)
    jalur = os.path.join(akar, 'baru', SW)
    teks = cap(open(jalur, encoding='utf-8').read(), nilai)
    if '--tulis' in argv:
        with open(jalur, 'w', encoding='utf-8') as f: f.write(teks)
    print('salinan /baru/ versi %s (%s): %d berkas, %d modul CDN, huruf %s%s' % (
        nilai['VERSI'], nilai['TERBIT'] or '-', len(nilai['BERKAS']), len(nilai['LUAR']), 'ada' if nilai['HURUF'] else 'tidak ada',
        ' — DITULIS ke baru/' + SW if '--tulis' in argv else ' (tidak ditulis; --tulis untuk mengecap)'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
