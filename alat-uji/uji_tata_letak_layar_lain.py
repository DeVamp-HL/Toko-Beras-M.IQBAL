#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tata_letak_layar_lain.py — PUTARAN 36 (owner 29 Sep 2026: rapi-rapi TATA LETAK, kelompok 3 = Pelanggan, Harga, Uang, Laporan, Menu). Statis.
  · SERAGAM: di Mac ketujuh layar kerja (Jual, Ringkasan, Stok, Pelanggan, Harga, Uang, Laporan) selebar 1720 px dengan pinggir 28 px — judul & pil di
    tempat yang sama tiap pindah layar (dulu 1180–1480 px, pinggir 14/28, tidak sejajar).
  · TIGA KOLOM Harga/Uang/Laporan: kolom samping melebar mengikuti layar lewat clamp(vw) — di 1280 px tetap selebar dulu (kolom tengah tidak menyempit).
  · MENU tetap kolom 860 px di tengah (owner 16 Sep: "Pertahankan desain UI di layar N1").

    python3 alat-uji/uji_tata_letak_layar_lain.py            → N lulus · 0 gagal
    python3 alat-uji/uji_tata_letak_layar_lain.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
from uji_tata_letak_jual import aturan   # noqa: E402  (pengurai CSS yang sama)
LAYAR = {'jual': 'kerangka', 'ringkasan': 'ringkasan', 'stok': 'stok', 'pelanggan': 'pelanggan', 'harga': 'harga', 'uang': 'uang', 'laporan': 'laporan'}
GRID = {'harga': '.layar-harga .hg-grid.mac', 'uang': '.layar-uang .ug-grid.mac', 'laporan': '.layar-laporan .lp-grid.mac'}
BERKAS = sorted({'baru/css/%s.css' % f for f in list(LAYAR.values()) + ['menu']}) + ['baru/index.html']   # + index.html: ikon menu bawah (owner 2 Okt)


def baca(ganti=None):
    t = {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in BERKAS}
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def mac(A, sel):
    """isi aturan `sel` yang berlaku di Mac: aturan dasar lalu aturan di media min-width 1100 (urutan berkas), digabung → nilai terakhir menang"""
    isi = ';'.join(x for m, s, x in A if s.strip() == sel and (not m or re.search(r'\(min-width:\s*(720|1100)px\)', m) and 'max-width' not in m))
    nilai = {}
    for d in isi.split(';'):
        if ':' in d: k, v = d.split(':', 1); nilai[k.strip()] = v.strip()
    return nilai


def periksa(t):
    c = []
    A = {b: aturan(t[b]) for b in BERKAS}
    lebar, pinggir = {}, {}
    for n, f in LAYAR.items():
        v = mac(A['baru/css/%s.css' % f], 'main.layar-' + n)
        lebar[n] = v.get('max-width'); pinggir[n] = v.get('padding')
    c.append(('seragam: di Mac ketujuh layar kerja selebar 1720 px', all(x == '1720px' for x in lebar.values()), lebar))
    c.append(('seragam: pinggir Mac 22/28/40 px di ketujuh layar', all(x == '22px 28px 40px' for x in pinggir.values()), pinggir))
    bs = mac(A['baru/css/pelanggan.css'], 'main.layar-pelanggan').get('box-sizing')
    c.append(('seragam: Pelanggan menghitung lebar termasuk pinggir (border-box) seperti layar lain', bs == 'border-box', bs))
    for n, sel in GRID.items():
        v = [x for m, s, x in A['baru/css/%s.css' % n] if 'min-width: 1100px' in m and s.strip() == sel]
        kolom = v[-1] if v else ''
        c.append(('tiga kolom %s: kolom samping clamp(vw) — di 1280 tidak lebih lebar dari dulu' % n.capitalize(), kolom.count('clamp(') == 2 and 'vw' in kolom and 'minmax(0, 1fr)' in kolom, kolom))
    lembar = {n: any('max-width: 1180px' in x for m, s, x in A['baru/css/%s.css' % n] if 'min-width: 1100px' in m and s.strip() == sel)
              for n, sel in [('uang', '.layar-uang section > .ug-lembar'), ('harga', '.layar-harga section > .kartu'), ('laporan', '.layar-laporan section > .lp-lembar')]}
    c.append(('lembar & formulir di luar grid tetap 1180 px (Uang, Harga, Laporan)', all(lembar.values()), lembar))
    truk = [x for m, s, x in A['baru/css/harga.css'] if 'min-width: 1100px' in m and s.strip() == '.layar-harga .bl-truk']
    c.append(('Harga › Belanja: gambar truk tidak melar (paling lebar 360 px)', any('max-width: 360px' in x for x in truk), truk))
    menu = [x for m, s, x in A['baru/css/menu.css'] if s.strip() == 'main.layar-menu' and 'max-width' in x]
    c.append(('menu: tetap kolom 860 px (desain N1 dikunci owner)', any('max-width: 860px' in x for x in menu) and not any('1720' in x for x in menu), menu))
    # owner 2 Okt: menu bawah HP & tablet BERIKON — tiap petak = satu SVG + teks; ikon sama persis dengan menu samping Mac; garisnya digambar (stroke, tanpa isi)
    H = t['baru/index.html']; nav = H[H.index('<nav class="nav"'):H.index('</nav>')]; side = H[H.index('<aside class="side"'):H.index('</aside>')]
    petak = re.findall(r'<div[^>]*data-tujuan="(\w+)"[^>]*>(.*?)</div>', nav)
    ikonSide = dict((k, re.search(r'<svg viewBox="0 0 24 24">(.*?)</svg>', v).group(1)) for k, v in re.findall(r'<div class="item[^"]*" data-tujuan="(\w+)"[^>]*>(.*?)</div>', side))
    sama = [k for k, isi in petak if re.search(r'<svg[^>]*>(.*?)</svg>', isi) and re.search(r'<svg[^>]*>(.*?)</svg>', isi).group(1) == ikonSide.get(k)]
    c.append(('menu bawah: kelima petak berikon (sama dengan menu samping) + teks', len(petak) == 5 and len(sama) == 5 and all('<span>' in isi for k, isi in petak), [k for k, _ in petak if k not in sama]))
    K = aturan(t['baru/css/kerangka.css'])
    c.append(('menu bawah: ikon digambar garis (fill none, stroke currentColor) — warna ikut petak aktif & mode gelap', any(s.strip() == '.nav > div > svg' and 'fill: none' in x and 'stroke: currentColor' in x for m, s, x in K if not m), ''))
    return c


KONTROL = [
    ('Harga kembali 1240', {'baru/css/harga.css': [('main.layar-harga { max-width: 1720px;', 'main.layar-harga { max-width: 1240px;')]}),
    ('Uang pinggir 14 lagi', {'baru/css/uang.css': [('main.layar-uang { max-width: 1720px; padding: 22px 28px 40px; }', 'main.layar-uang { max-width: 1720px; }')]}),
    ('Pelanggan content-box lagi', {'baru/css/pelanggan.css': [('main.layar-pelanggan { max-width: 1720px; box-sizing: border-box; }', 'main.layar-pelanggan { max-width: 1720px; }')]}),
    ('Laporan kolom samping tetap (menyempitkan tengah di 1280)', {'baru/css/laporan.css': [('minmax(280px, clamp(326px, 21vw, 400px))', 'minmax(280px, 400px)')]}),
    ('lembar Uang melar', {'baru/css/uang.css': [('  .layar-uang section > .ug-lembar { width: 100%; max-width: 1180px; box-sizing: border-box; }\n', '')]}),
    ('truk Harga lonjong lagi', {'baru/css/harga.css': [('.layar-harga .bl-truk { width: 100%; max-width: 360px; margin-inline: auto; }', '')]}),
    ('Menu ikut 1720', {'baru/css/menu.css': [('max-width: 860px;', 'max-width: 1720px;')]}),
    ('menu bawah kehilangan ikon Stok', {'baru/index.html': [('<div data-tujuan="stok"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8.5 12 4l8 4.5v7L12 20l-8-4.5z"/><path d="M4 8.5 12 13l8-4.5M12 13v7"/></svg>', '<div data-tujuan="stok">')]}),
    ('ikon menu bawah beda dengan menu samping', {'baru/index.html': [('<div data-tujuan="menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/>', '<div data-tujuan="menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 17h16"/>')]}),
    ('ikon menu bawah terisi hitam (tanpa stroke)', {'baru/css/kerangka.css': [('.nav > div > svg { fill: none; stroke: currentColor;', '.nav > div > svg {')]}),
]


def main():
    if '--kontrol' in sys.argv:
        dasar = {n for n, ok, k in periksa(baca()) if ok}; diam = []
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
