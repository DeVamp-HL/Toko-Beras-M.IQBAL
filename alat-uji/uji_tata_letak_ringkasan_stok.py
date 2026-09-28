#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tata_letak_ringkasan_stok.py — PUTARAN 35 (owner 29 Sep 2026: rapi-rapi TATA LETAK, kelompok 2 = Ringkasan & Stok). Statis, tanpa peramban.
  · STOK Gudang: tombol kerja (Barang masuk, Adukan, Cocokkan, Kantong, Tempat simpan, HPP) sesudah kartu pertanyaan — dulu di dasar halaman ±2.600 px.
    HP/tablet: <aside> larut, urutan tanya · tombol · jawaban · per jenis. Mac: jawaban kiri (dua kolom urut ke bawah di ≥1280), aside kanan menempel.
    Lembar & tab lain tetap 1180 px (formulir tidak melar).
  · RINGKASAN: kas, perhatian & catatan katalog satu <aside>; HP hero · nota · samping; Mac hero & nota kiri, samping kanan menempel; pita sumber penuh.
  · SERAGAM: di Mac Jual, Ringkasan & Stok sama-sama selebar 1720 px.

    python3 alat-uji/uji_tata_letak_ringkasan_stok.py            → N lulus · 0 gagal
    python3 alat-uji/uji_tata_letak_ringkasan_stok.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
from uji_tata_letak_jual import aturan   # noqa: E402  (pengurai CSS yang sama)
BERKAS = ['baru/css/stok.css', 'baru/css/ringkasan.css', 'baru/css/kerangka.css', 'baru/js/layar/stok.js', 'baru/js/layar/ringkasan.js']


def baca(ganti=None):
    t = {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in BERKAS}
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def cari(A, media, sel):
    return [isi for m, s, isi in A if (media in m if media else not m) and s.strip() == sel]


def periksa(t):
    c = []
    SJ, RJ = t['baru/js/layar/stok.js'], t['baru/js/layar/ringkasan.js']
    g = SJ[SJ.index('function gambarGudang'):SJ.index('const kepalaLembar')]
    pos = {k: g.find(v) for k, v in [('tanya', 'class="tanya"'), ('samping', 'class="stok-samping"'), ('aksi', 'class="stok-aksi"'), ('masuk', "t('bukaMasuk'"),
                                      ('hpp', 'HPP / modal</div>`}</div></div>'), ('jenis', 'data-k="per-jenis"'), ('tutup', '</aside>'), ('jawab', 'class="kartu jawaban"')]}
    c.append(('stok: tombol kerja di <aside> sesudah kartu pertanyaan, sebelum daftar jawaban', all(v >= 0 for v in pos.values()) and
              pos['tanya'] < pos['samping'] < pos['aksi'] < pos['masuk'] < pos['hpp'] < pos['jenis'] < pos['tutup'] < pos['jawab'], pos))
    S = aturan(t['baru/css/stok.css'])
    c.append(('stok: HP/tablet — aside larut (display: contents)', any('display: contents' in x for x in cari(S, '', '.layar-stok .stok-gudang > .stok-samping')), ''))
    urut = {k: cari(S, '', v) for k, v in [('tanya', '.layar-stok .stok-gudang > .tanya'), ('aksi', '.layar-stok .stok-aksi'), ('jawab', '.layar-stok .stok-gudang > .jawaban'), ('jenis', '.layar-stok .stok-samping > [data-k="per-jenis"]')]}
    nilai = {k: (re.search(r'order:\s*(\d+)', v[0]) or [None, None])[1] if v else None for k, v in urut.items()}
    c.append(('stok: HP/tablet — urutan tanya · tombol · jawaban · per jenis', nilai == {'tanya': '0', 'aksi': '1', 'jawab': '2', 'jenis': '3'}, nilai))
    mac = cari(S, 'min-width: 1100px', '.layar-stok .stok-gudang > .stok-samping')
    c.append(('stok: Mac — aside kolom kanan yang menempel', any('position: sticky' in x and 'grid-column: 2' in x for x in mac), mac))
    c.append(('stok: Mac — gudang dua kolom', any('grid-template-columns: minmax(0, 1fr)' in x for x in cari(S, 'min-width: 1100px', '.layar-stok .stok-gudang')), ''))
    kolom = cari(S, 'min-width: 1280px', '.layar-stok .daftar-jawab')
    c.append(('stok: ≥1280 daftar jawaban dua kolom urut ke bawah (columns, bukan grid)', any('columns: 2' in x for x in kolom), kolom))
    form = cari(S, 'min-width: 1100px', 'main.layar-stok > section:not(.stok-gudang):not([data-k="wadah"])')
    c.append(('stok: lembar & tab lain tetap paling lebar 1180 px', any('max-width: 1180px' in x for x in form), form))
    c.append(('stok: Wadah literan selebar halaman, kotak sebaris sebanyak yang muat', any('auto-fill' in x for x in cari(S, 'min-width: 1100px', '.layar-stok .stok-wadah .petak-wadah')), ''))

    rk = RJ[RJ.index('function bangun'):RJ.index("$('rkSkala').innerHTML")]
    p = {k: rk.find(v) for k, v in [('hero', 'id="rkHero"'), ('aside', 'class="rk-samping"'), ('kas', 'id="rkKas"'), ('perhatian', 'id="rkPerhatian"'), ('katalog', 'id="rkKatalog"'), ('tutup', '</aside>'), ('nota', 'rk-nota')]}
    c.append(('ringkasan: kas, perhatian & catatan katalog satu <aside>, nota sesudahnya', all(v >= 0 for v in p.values()) and p['hero'] < p['aside'] < p['kas'] < p['perhatian'] < p['katalog'] < p['tutup'] < p['nota'], p))
    R = aturan(t['baru/css/ringkasan.css'])
    c.append(('ringkasan: pita sumber kosong tidak menyisakan baris', any('display: none' in x for x in cari(R, '', '.layar-ringkasan #rkSumber:empty')), ''))
    hp = {k: (re.search(r'order:\s*(\d+)', (cari(R, '', v) or [''])[0]) or [None, None])[1] for k, v in [('nota', '.layar-ringkasan .rk-nota'), ('samping', '.layar-ringkasan .rk-samping')]}
    c.append(('ringkasan: HP — hero · nota · samping (urutan lama tetap)', hp == {'nota': '1', 'samping': '2'}, hp))
    c.append(('ringkasan: tablet — pita sumber selebar penuh', any('grid-column: 1 / -1' in x for x in cari(R, 'min-width: 720px', '.layar-ringkasan #rkSumber')), ''))
    rm = cari(R, 'min-width: 1100px', '.layar-ringkasan .rk-samping')
    c.append(('ringkasan: Mac — samping kolom kanan setinggi hero + nota, menempel', any('position: sticky' in x and 'grid-row: span 2' in x and 'grid-column: 2' in x for x in rm), rm))

    rows = cari(R, 'min-width: 1100px', 'main.layar-ringkasan')
    c.append(('ringkasan: Mac — baris terakhir 1fr (samping tinggi tidak membuka lubang di bawah hero)', any(re.search(r'grid-template-rows:[^;]*1fr', x) for x in rows), rows))
    c.append(('ringkasan: animasi masuk atas/kiri dulu (tidak ada .kartu:last-child yang menangkap nota)', not cari(R, '', 'main.layar-ringkasan.masuk > .kartu:last-child'), ''))
    c.append(('stok: Atur wadah (formulir) ikut 1180, hanya kotak wadah yang lebar', any('[data-k="wadah"]' in s and 'max-width: 1180px' in isi for m, s, isi in S if 'min-width: 1100px' in m and 'section:not(.stok-gudang)' in s), ''))
    lebar = {n: any('max-width: 1720px' in x for x in cari(aturan(t[f]), 'min-width: 1100px', 'main.layar-' + n)) for n, f in [('jual', 'baru/css/kerangka.css'), ('ringkasan', 'baru/css/ringkasan.css'), ('stok', 'baru/css/stok.css')]}
    c.append(('seragam: di Mac Jual, Ringkasan & Stok selebar 1720 px', all(lebar.values()), lebar))
    return c


KONTROL = [
    ('tombol kerja kembali ke dasar', {'baru/js/layar/stok.js': [('      <aside class="stok-samping" data-k="stok-samping">\n', ''), ('      </aside>\n      <div class="kartu jawaban"', '      <div class="kartu jawaban"')]}),
    ('aside tidak larut di HP', {'baru/css/stok.css': [('.layar-stok .stok-gudang > .stok-samping { display: contents; }', '.layar-stok .stok-gudang > .stok-samping { display: block; }')]}),
    ('per jenis naik mendahului jawaban', {'baru/css/stok.css': [('.layar-stok .stok-samping > [data-k="per-jenis"] { order: 3; }', '.layar-stok .stok-samping > [data-k="per-jenis"] { order: 1; }')]}),
    ('aside Mac tidak menempel', {'baru/css/stok.css': [('grid-column: 2; grid-row: 2; position: sticky; top: 22px;', 'grid-column: 2; grid-row: 2;')]}),
    ('daftar jawaban urut ke samping (grid)', {'baru/css/stok.css': [('.layar-stok .daftar-jawab { display: block; columns: 2; column-gap: 28px; }', '.layar-stok .daftar-jawab { display: grid; grid-template-columns: 1fr 1fr; column-gap: 28px; }')]}),
    ('formulir Stok melar', {'baru/css/stok.css': [('main.layar-stok > section:not(.stok-gudang):not([data-k="wadah"]) { width: 100%; max-width: 1180px; box-sizing: border-box; }', '')]}),
    ('Atur wadah ikut melar', {'baru/css/stok.css': [('main.layar-stok > section:not(.stok-gudang):not([data-k="wadah"])', 'main.layar-stok > section:not(.stok-gudang):not(.stok-wadah)')]}),
    ('Ringkasan Mac berlubang di bawah hero', {'baru/css/ringkasan.css': [('column-gap: 18px; grid-template-rows: auto auto auto 1fr; }', 'column-gap: 18px; }')]}),
    ('animasi Ringkasan naik dari bawah', {'baru/css/ringkasan.css': [('main.layar-ringkasan.masuk > .rk-samping { animation-delay: 230ms; }', 'main.layar-ringkasan.masuk > .rk-samping { animation-delay: 230ms; }\nmain.layar-ringkasan.masuk > .kartu:last-child { animation-delay: 300ms; }')]}),
    ('kartu Ringkasan lepas lagi', {'baru/js/layar/ringkasan.js': [('    <aside class="rk-samping">\n', ''), ('    </aside>\n    <div class="kartu rk-nota"', '    <div class="kartu rk-nota"')]}),
    ('pita sumber kosong menyisakan baris', {'baru/css/ringkasan.css': [('.layar-ringkasan #rkSumber:empty { display: none; }', '')]}),
    ('urutan HP Ringkasan berubah', {'baru/css/ringkasan.css': [('.layar-ringkasan .rk-nota { order: 1; }', '.layar-ringkasan .rk-nota { order: 3; }')]}),
    ('samping Ringkasan tidak menempel', {'baru/css/ringkasan.css': [('grid-row: span 2; align-self: start; position: sticky; top: 22px;', 'grid-row: span 2; align-self: start;')]}),
    ('Stok kembali 1180 di Mac', {'baru/css/stok.css': [('  main.layar-stok { max-width: 1720px; }\n', '')]}),
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
