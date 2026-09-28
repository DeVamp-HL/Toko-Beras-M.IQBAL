#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tata_letak_jual.py — PUTARAN 34 (owner 29 Sep 2026: rapi-rapi TATA LETAK, kelompok 1 = Jual). Statis + jsc, tanpa peramban.
  · TIRAI: tidak ada aturan `.lembar` polos yang memberi LEBAR — tirai (.lembar.tirai) dulu mewarisi width 440px / 46vw dari aturan lembar Mac & tablet
    dan hanya menutup sebagian kiri layar. Tirai = inset 0.
  · KABAR: di tablet & Mac kabar hanya di kolom rak (keranjang & Hari ini tidak meloncat tiap ada kabar); baris kosong tanpa celah ganda (row-gap 0).
  · RAK: banyak kolom kartu menurut lebar RAK (auto-fill) mulai tablet; deret tab & saringan jenis dibungkus di Mac (dulu terpotong tanpa batang gulir).
  · LEMBAR: Jual duduk tepat di atas kolom keranjang (tablet, 1100–1279) / kolom Hari ini (Mac ≥1280), tinggi mengikuti isi.
  · PANGGUNG: adegan disejajarkan ke kolom keranjang di tablet & Mac (adegan.js sejajarkan), HP tetap di tengah.
  · PITA STATUS (jsc): pita Jual di mode Firestore hanya untuk TANPA INTERNET / koleksi ditolak; normal, memuat, menunggu server, cadangan → tidak ada.

    python3 alat-uji/uji_tata_letak_jual.py            → N lulus · 0 gagal
    python3 alat-uji/uji_tata_letak_jual.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
CSS = ['identitas', 'kerangka', 'jual', 'ringkasan', 'stok', 'pelanggan', 'menu', 'harga', 'uang', 'laporan', 'adegan', 'kinerja', 'gerak', 'gerbang']
BERKAS = ['baru/css/%s.css' % n for n in CSS] + ['baru/js/app.js', 'baru/js/layar/jual.js', 'baru/js/layar/adegan.js']


def baca(ganti=None):
    t = {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in BERKAS}
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def aturan(css):
    """[(media, selektor, isi)] — media = teks @media pembungkus ('' kalau tidak ada). Komentar dibuang; cukup untuk berkas CSS proyek ini."""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S); out = []; i = 0; media = []
    while i < len(css):
        j = css.find('{', i); k = css.find('}', i)
        if k != -1 and (j == -1 or k < j):
            if media: media.pop()
            i = k + 1; continue
        if j == -1: break
        kepala = css[i:j].strip()
        if kepala.startswith('@media') or kepala.startswith('@supports'):
            media.append(kepala); i = j + 1; continue
        if kepala.startswith('@keyframes'):
            d, p = 0, j   # lompati seluruh blok keyframes
            while p < len(css):
                if css[p] == '{': d += 1
                elif css[p] == '}':
                    d -= 1
                    if d == 0: break
                p += 1
            i = p + 1; continue
        k = css.find('}', j); out.append((' '.join(media), kepala, css[j + 1:k])); i = k + 1
    return out


def fungsi(teks, nama):
    m = re.search(r'\nfunction ' + nama + r'\(\) \{\n.*?\n\}\n', teks, re.S)
    return m.group(0) if m else ''


PITA_UJI = r"""
var __s = {};
function sumberData() { return { jenis: __s.jenis }; }
var statusFb = {};
%s
%s
var hasil = {};
function coba(nama, jenis, fb) { __s.jenis = jenis; statusFb = fb; hasil[nama] = statusAwas(); }
coba('normal', 'firestore', { masuk: true, koleksiSiap: 56, koleksiTotal: 56, menunggu: 0, offline: false });
coba('memuat', 'firestore', { masuk: true, koleksiSiap: 12, koleksiTotal: 56, menunggu: 0, offline: false });
coba('menunggu', 'firestore', { masuk: true, koleksiSiap: 56, koleksiTotal: 56, menunggu: 2, offline: false });
coba('belumMasuk', 'firestore', { masuk: false, koleksiSiap: 0, koleksiTotal: 0, menunggu: 0, offline: true });
coba('cadangan', 'cadangan', { masuk: false, offline: true });
coba('offline', 'firestore', { masuk: true, koleksiSiap: 56, koleksiTotal: 56, menunggu: 1, offline: true });
coba('ditolak', 'firestore', { masuk: true, koleksiSiap: 55, koleksiTotal: 56, menunggu: 0, offline: false, ditolak: ['rahasia'] });
coba('galat', 'firestore', { masuk: true, koleksiSiap: 56, koleksiTotal: 56, menunggu: 0, offline: false, galat: 'permission-denied' });
print(JSON.stringify(hasil));
"""


def jsc(kode):
    fd, p = tempfile.mkstemp(suffix='.js'); os.write(fd, kode.encode('utf-8')); os.close(fd)
    try:
        r = subprocess.run([JSC, p], capture_output=True, text=True, timeout=30)
        return r.stdout.strip(), r.stderr.strip()
    finally: os.unlink(p)


def periksa(t):
    c = []   # (nama, lulus, keterangan)
    A = {n: aturan(t['baru/css/%s.css' % n]) for n in CSS}
    polos = re.compile(r'(^|[\s,>+~])\.lembar(?![\w:.\[-])')
    lebar = [(n, m, s) for n in CSS for m, s, isi in A[n] if any(polos.search(x.strip()) for x in s.split(',')) and re.search(r'(^|[;\s])width\s*:', isi)]
    c.append(('tirai: tidak ada aturan .lembar polos yang memberi lebar (tirai mewarisinya)', not lebar, lebar))
    tirai = [isi for n in CSS for m, s, isi in A[n] if s.strip() == '.lembar.tirai']
    c.append(('tirai: .lembar.tirai menutup seluruh layar (inset 0)', any(re.search(r'inset\s*:\s*0\s*;', x) for x in tirai), tirai))

    K = A['kerangka']
    dasar = [isi for m, s, isi in K if not m and s.strip() == 'main.layar-jual']
    c.append(('kabar: dasar main.layar-jual row-gap 0 (baris pita/kabar kosong tanpa celah ganda)', any(re.search(r'row-gap\s*:\s*0\s*;', x) and not re.search(r'(^|[;\s])gap\s*:', x) for x in dasar), dasar))
    margin = [s for m, s, isi in K if not m and 'margin-bottom: 12px' in isi and '.kabar-kotak' in s and '.kepala-jual' in s]
    c.append(('kabar: kepala, pita & kabar berjarak lewat margin', bool(margin), margin))
    area = [(m, re.search(r'grid-template-areas\s*:\s*([^;]+);', isi).group(1)) for m, s, isi in K if m and s.strip() == 'main.layar-jual' and 'grid-template-areas' in isi]
    c.append(('kabar: di tablet & Mac kabar hanya di kolom rak (≥720 px, tiap susunan)', len(area) >= 3 and all('"kabar keranjang' in a and '"kabar kabar' not in a for _, a in area), area))
    baris = [(m, re.search(r'grid-template-rows\s*:\s*([^;]+);', isi)) for m, s, isi in K if m and s.strip() == 'main.layar-jual' and 'grid-template-areas' in isi]
    c.append(('kabar: baris terakhir 1fr (keranjang yang tinggi tidak meregangkan baris kabar)', all(r and r.group(1).strip().endswith('1fr') for _, r in baris), [(m, r and r.group(1)) for m, r in baris]))

    J = A['jual']
    fill = [(m, isi) for m, s, isi in J if 'min-width: 720px' in m and s.strip() == 'main.layar-jual .rak-chip' and 'auto-fill' in isi]
    c.append(('rak: kolom kartu menurut lebar rak (auto-fill) mulai tablet', bool(fill), fill))
    bungkus = [isi for m, s, isi in J if 'min-width: 1100px' in m and s.strip() == 'main.layar-jual > .jual-rak > .jalur' and 'flex-wrap: wrap' in isi]
    c.append(('rak: deret tab & saringan jenis dibungkus di Mac', bool(bungkus), bungkus))
    pudar = [isi for m, s, isi in J if 'max-width: 1099px' in m and '.jual-rak > .jalur' in s and 'mask-image' in isi]
    c.append(('rak: ujung deret tab memudar di HP & tablet', bool(pudar), pudar))

    lembar = [(m, isi) for m, s, isi in K if m and s.strip() == 'main.layar-jual .lembar:not(.tirai)']
    tab = [isi for m, isi in lembar if m.strip() == '@media (min-width: 720px)']
    mac = [isi for m, isi in lembar if m.strip() == '@media (min-width: 1100px)']
    c.append(('lembar: tablet tepat di atas kolom keranjang, tinggi mengikuti isi', any('width: var(--lebar-keranjang)' in x and 'bottom: auto' in x for x in tab), tab))
    c.append(('lembar: Mac tepat di atas kolom Hari ini, tinggi mengikuti isi', any('width: var(--lebar-samping);' in x and 'bottom: auto' in x and '1720px' in x and '100vw' not in x for x in mac), mac))
    samping = re.search(r'--lebar-samping:\s*clamp\((\d+)px', t['baru/css/kerangka.css'])
    c.append(('lembar: kolom Hari ini paling sempit 360 px (lembar selebar kolom, tidak menjulur ke keranjang)', bool(samping) and int(samping.group(1)) >= 360, samping and samping.group(0)))
    tubuh = [isi for m, s, isi in K if not m and s.strip() == 'body' and 'min-height: 100%' in isi]
    c.append(('sticky: body bukan wadah gulir (overflow-x clip + overflow-y visible sesudah pasangan lama)', any(re.search(r'overflow-x:\s*clip;\s*overflow-y:\s*visible;', x) for x in tubuh), tubuh))

    ad = t['baru/js/layar/adegan.js']
    c.append(('panggung: mainkan() menyejajarkan panggung ke kolom keranjang (dan mengukur ulang sesudah digambar)', 'sejajarkan(p); requestAnimationFrame(() => sejajarkan(p));' in ad and "innerWidth >= 720" in ad, ''))
    c.append(('panggung: lembar terbuka di atas kolom keranjang → panggung pindah ke kolom rak', "m.querySelector('.lembar:not(.tirai)')" in ad and 'q.left < r.right && q.right > r.left' in ad and "':scope > .jual-rak'" in ad, ''))
    sej = [isi for n in ['adegan'] for m, s, isi in A[n] if 'min-width: 720px' in m and s.strip() == '.panggung.sejajar']
    c.append(('panggung: .panggung.sejajar hanya ≥720 px (HP tetap di tengah)', any('var(--p-kiri)' in x and 'var(--p-lebar)' in x for x in sej), sej))

    app, jual = t['baru/js/app.js'], t['baru/js/layar/jual.js']
    c.append(('pita: app.js memberi statusAwas ke Jual', re.search(r'pasangLayarJual\(akar, \{[^\n]*\bstatusAwas\b', app) is not None, ''))
    c.append(('pita: Jual mode Firestore memakai statusAwas (bukan pita tetap)', 'opsi.statusAwas' in jual and 'Nota dicatat ke data toko yang sama dengan sistem lama' not in jual, ''))
    ft, fa = fungsi(app, 'statusTeks'), fungsi(app, 'statusAwas')
    if not (ft and fa): c.append(('pita: fungsi statusTeks & statusAwas terbaca dari app.js', False, (bool(ft), bool(fa)))); return c
    out, err = jsc(PITA_UJI % (ft, fa))
    try: H = json.loads(out)
    except Exception: c.append(('pita: jsc jalan', False, err[:300] or out[:300])); return c
    kosong = ['normal', 'memuat', 'menunggu', 'belumMasuk', 'cadangan']
    c.append(('pita: normal / memuat / menunggu server / belum masuk / cadangan → TIDAK ada pita', all(H[k] == '' for k in kosong), {k: H[k] for k in kosong}))
    c.append(('pita: TANPA INTERNET tetap tampil', 'TANPA INTERNET' in H['offline'], H['offline']))
    c.append(('pita: koleksi ditolak / galat tetap tampil (teks statusTeks)', 'ditolak server' in H['ditolak'] and 'ditolak' in H['galat'], [H['ditolak'], H['galat']]))
    return c


KONTROL = [
    ('tirai mewarisi lebar lagi', {'baru/css/kerangka.css': [('  .lembar:not(.tirai) { position: fixed; right: 28px;', '  .lembar { position: fixed; right: 28px;')]}),
    ('tirai tidak lagi selayar', {'baru/css/kerangka.css': [('.lembar.tirai { position: fixed; inset: 0;', '.lembar.tirai { position: fixed;')]}),
    ('row-gap kembali (celah ganda)', {'baru/css/kerangka.css': [('display: grid; row-gap: 0; column-gap: 12px;', 'display: grid; gap: 12px;')]}),
    ('kabar merentang semua kolom di Mac', {'baru/css/kerangka.css': [('"kabar keranjang samping"', '"kabar kabar kabar"')]}),
    ('baris kabar ikut meregang', {'baru/css/kerangka.css': [('grid-template-rows: auto auto auto 1fr;\n    padding: 22px 28px 40px;', 'grid-template-rows: auto auto auto auto;\n    padding: 22px 28px 40px;')]}),
    ('kartu rak tetap 3 kolom', {'baru/css/jual.css': [('@media (min-width: 720px) { main.layar-jual .rak-chip { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); } }\n', '')]}),
    ('tab Mac tidak dibungkus', {'baru/css/jual.css': [('@media (min-width: 1100px) { main.layar-jual > .jual-rak > .jalur { flex-wrap: wrap; overflow: visible; } }\n', '')]}),
    ('lembar Mac setinggi layar lagi', {'baru/css/kerangka.css': [('width: var(--lebar-samping); bottom: auto;', 'width: var(--lebar-samping);')]}),
    ('lembar Mac lebih lebar dari kolom Hari ini', {'baru/css/kerangka.css': [('width: var(--lebar-samping); bottom: auto;', 'width: max(360px, var(--lebar-samping)); bottom: auto;'), ('--lebar-samping: clamp(360px, 20vw, 380px);', '--lebar-samping: clamp(340px, 20vw, 380px);')]}),
    ('body wadah gulir lagi (sticky mati)', {'baru/css/kerangka.css': [('overflow-x: hidden; overflow-y: auto; overflow-x: clip; overflow-y: visible;', 'overflow-x: hidden; overflow-y: auto;')]}),
    ('panggung menutupi lembar terbuka', {'baru/js/layar/adegan.js': [("  const lb = m.querySelector('.lembar:not(.tirai)'); const q = lb ? lb.getBoundingClientRect() : null;\n", "  const q = null;\n")]}),
    ('panggung tidak disejajarkan', {'baru/js/layar/adegan.js': [('  sejajarkan(p); requestAnimationFrame(() => sejajarkan(p));', '')]}),
    ('pita status selalu tampil', {'baru/js/app.js': [("  return statusFb.offline ? 'TANPA INTERNET — angka dari simpanan perangkat, catatan mengantre' : '';", '  return statusTeks();')]}),
    ('pita tanpa internet hilang', {'baru/js/app.js': [("  return statusFb.offline ? 'TANPA INTERNET — angka dari simpanan perangkat, catatan mengantre' : '';", "  return '';")]}),
]


def main():
    if not os.path.exists(JSC): print('jsc tidak ada — uji dilewati' + (' (CI: GAGAL)' if os.environ.get('CI') else '')); return 2 if os.environ.get('CI') else 0
    if '--kontrol' in sys.argv:
        diam = []; dasar = {n for n, ok, k in periksa(baca()) if ok}   # kontrol hanya dihitung dari pemeriksaan yang LULUS tanpa kerusakan
        for nama, g in KONTROL:
            gagal = [n for n, ok, k in periksa(baca(g)) if not ok and n in dasar]
            print(('BERBUNYI ' if gagal else 'DIAM     ') + nama + ('  → ' + gagal[0] if gagal else ''))
            if not gagal: diam.append(nama)
        print('kontrol: %d/%d berbunyi' % (len(KONTROL) - len(diam), len(KONTROL))); return 3 if diam else 0
    hasil = periksa(baca())
    for n, ok, k in hasil:
        if not ok: print('GAGAL:', n, '→', str(k)[:500])
    lulus = sum(1 for _, ok, _ in hasil if ok); print('%d lulus · %d gagal' % (lulus, len(hasil) - lulus))
    return 0 if lulus == len(hasil) else 1


if __name__ == '__main__':
    sys.exit(main())
