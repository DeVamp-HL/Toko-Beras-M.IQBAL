#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_isian_lokal.py — putaran 23d: SETIAP kolom ketik (data-ketik) di kedelapan layar menulis ke kunci keadaan yang DIJAGA penjaga isian (inti/isian.js),
atau tercatat SENGAJA bukan isian (pencarian, saringan, alat hitung) di BUKAN_ISIAN beserta alasannya. Kolom baru yang lupa didaftarkan = GAGAL di sini,
jadi isiannya tidak diam-diam terbawa ke akun berikutnya. Statis (tanpa peramban); alur Keluar/ganti orang diuji di uji_layar_kunci.py bagian ISIAN.

    python3 alat-uji/uji_isian_lokal.py            → LULUS / GAGAL (keluar 2)
    python3 alat-uji/uji_isian_lokal.py --kontrol  → kontrol wajib berbunyi (keluar 3 kalau ada yang diam)
"""
import os, re, sys

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
LAYAR = ['jual', 'ringkasan', 'stok', 'pelanggan', 'menu', 'harga', 'uang', 'laporan']
# penulis pembantu → kunci keadaan yang ditulisnya
PEMBANTU = {'ubahMasuk': 'masuk', 'ubahCocok': 'cocok', 'ubahAdukan': 'adukan', 'ubahAtur': 'atur', 'ubahAturTp': 'aturTp', 'ubahDraf': 'draf', 'ubahKartu': 'kartu', 'ubahPesan': 'pesan'}
# draf LOKAL (localStorage) → kunci keadaan yang dipulihkan darinya; yang dijaga = yang DISEBUT di argumen lokal pasangIsian(…) di sumber layar
LOKAL_KE_KUNCI = {'KUNCI_DRAF_MASUK': 'masuk', 'KUNCI_DRAF_COCOK': 'cocok', 'KUNCI_DRAF_ADUKAN': 'adukan', 'KUNCI_DRAF_BELANJA': 'pesan', 'KUNCI_DRAF_TUTUP': 'draf'}
# sengaja BUKAN isian — tetap ikut dikosongkan (seluruh keadaan layar kembali ke awal), tapi tidak ditanyakan saat Keluar
BUKAN_ISIAN = {
    'harga': {'kal': 'alat hitung naik/turun massal — hasilnya baru jadi isian lewat draf katalog di server'},
    'pelanggan': {'cari': 'pencarian', 'titipCari': 'pencarian'},
    'menu': {'cari': 'pencarian'},
    'laporan': {'cariK': 'pencarian dokumen kecil', 'sampaiN': 'tanggal lihat neraca (saringan tampilan)'},
    'jual': {'cariPelanggan': 'pencarian nama', 'psSaring': 'saringan daftar pesanan', 'rtCari': 'pencarian nota retur'},
}


# kunci localStorage di layar yang SENGAJA bukan draf isian (tidak ikut dihapus saat ganti orang)
BUKAN_DRAF = {'KUNCI_TAB': 'tab/layar terakhir perangkat (navigasi)', 'KUNCI_KELUARGA': 'keluarga layar terakhir (navigasi)', 'KUNCI_LACI': 'laci Menu terbuka/tertutup (navigasi)',
              'KUNCI_SKALA': 'skala Beranda (tampilan)', 'KUNCI_HAFAL': 'skor kuis hafalan terakhir di perangkat (sudah tersimpan, bukan isian)',
              'KUNCI_TITIK': 'titik kas = salinan catatan toko, bukan isian (juga dibaca mesin; tirai 23c menahan tampilnya)'}


def baca(nama):
    return open(os.path.join(AKAR, 'baru', 'js', 'layar', nama + '.js'), encoding='utf-8').read()


def dijaga(nama, src, jl):
    """Kunci yang dijaga layar ini."""
    if nama == 'jual':
        m = re.search(r"const ISIAN_JUAL_LAIN = \[(.*?)\];", jl, re.S)
        return set(re.findall(r"'(\w+)'", m.group(1) if m else '')) | {'keranjang', 'antrean'}
    m = re.search(r"pasangIsian\(K, awal, \[(.*)\], (\[.*?\])\);", src)
    if not m: return None
    return set(re.findall(r"'(\w+)'", m.group(1))) | {LOKAL_KE_KUNCI[x] for x in re.findall(r'\b(KUNCI_DRAF_\w+)', m.group(2)) if x in LOKAL_KE_KUNCI}


def periksa(sumber):
    """sumber = {nama: teks layar, '_jl': jual-logika} → daftar cacat."""
    cacat = []
    for nama in LAYAR:
        src = sumber[nama]; jaga = dijaga(nama, src, sumber['_jl'])
        kolom = sorted(set(re.findall(r'data-ketik="(\w+)"', src)))
        if nama == 'ringkasan':
            if kolom: cacat.append('ringkasan: sekarang punya kolom ketik %s — pasang penjaga isian' % kolom)
            if 'belumDisimpan: () => false, lupakanOrang: () => {}' not in src: cacat.append('ringkasan: penjaga kosong hilang')
            continue
        if jaga is None: cacat.append('%s: tidak memasang pasangIsian (inti/isian.js)' % nama); continue
        if nama != 'jual' and 'belumDisimpan: ISIAN.belum, lupakanOrang: ISIAN.lupakan' not in src: cacat.append('%s: penjaga tidak diteruskan ke app.js' % nama)
        # setiap kunci localStorage milik layar: draf yang dijaga penjaga, atau tercatat sengaja bukan draf
        m2 = re.search(r"pasangIsian\(K, awal, \[.*\], (\[.*?\])\);", src); lokal = set(re.findall(r'\b(KUNCI_\w+)', m2.group(1))) if m2 else set()
        for kk in sorted(set(re.findall(r"\b(KUNCI_\w+)\s*=\s*'miqbal_", src))):
            if kk not in lokal and kk not in BUKAN_DRAF: cacat.append('%s: kunci localStorage %s tidak dijaga sebagai draf lokal (dan tidak tercatat sengaja bukan draf)' % (nama, kk))
        for k in kolom:
            m = re.search(r'\b' + k + r'\s*:\s*(?:async\s*)?\(([^)]*)\)\s*=>(.{0,900})', src, re.S)
            if not m: cacat.append('%s: penangan kolom %s tidak ketemu' % (nama, k)); continue
            badan = m.group(2); ujung = re.search(r',\s*\w+\s*:\s*(?:async\s*)?\([^)]*\)\s*=>', badan)   # badan berhenti di penangan berikutnya
            if ujung: badan = badan[:ujung.start()]
            temu = [(x.start(), x.group(1)) for x in re.finditer(r'set\(\{\s*(\w+)', badan)] + [(x.start(), PEMBANTU[x.group(1)]) for x in re.finditer(r'\b(ubah[A-Z]\w*)\(', badan) if x.group(1) in PEMBANTU]
            ditulis = [kk for _, kk in sorted(temu)]
            if not ditulis: cacat.append('%s: kolom %s tidak menulis kunci yang dikenali pemeriksa' % (nama, k)); continue
            kunci = ditulis[0]
            if kunci not in jaga and kunci not in BUKAN_ISIAN.get(nama, {}):
                cacat.append('%s: kolom %s menulis "%s" yang TIDAK dijaga penjaga isian (dan tidak tercatat sengaja bukan isian)' % (nama, k, kunci))
    return cacat


def muat():
    s = {n: baca(n) for n in LAYAR}; s['_jl'] = baca('jual-logika'); return s


if __name__ == '__main__':
    S = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        rusak = [
            ('Uang lupa menjaga form uang keluar (catat)', 'uang', "['catat', ", "["),
            ('Laporan lupa menjaga draf setoran pajak', 'laporan', "'drafSetor', ", ''),
            ('Stok lupa draf lokal barang masuk', 'stok', '[KUNCI_DRAF_MASUK, KUNCI_DRAF_COCOK, KUNCI_DRAF_ADUKAN]);', '[KUNCI_DRAF_COCOK, KUNCI_DRAF_ADUKAN]);'),
            ('Harga lupa draf lokal belanja', 'harga', '[KUNCI_DRAF_BELANJA]);', '[]);'),
            ('Jual lupa isian pesanan', '_jl', "const ISIAN_JUAL_LAIN = ['psNama', ", "const ISIAN_JUAL_LAIN = ["),
            ('Menu tidak meneruskan penjaga', 'menu', 'belumDisimpan: ISIAN.belum, lupakanOrang: ISIAN.lupakan', 'belumDisimpan: () => false, lupakanOrang: () => {}'),
        ]
        for nama, berkas, lama, baru in rusak:
            T = dict(S); assert lama in T[berkas], 'kontrol basi: ' + nama; T[berkas] = T[berkas].replace(lama, baru, 1)
            c = periksa(T)
            print(('BERBUNYI ' if c else 'DIAM!!   ') + nama + ' → ' + (c[0][:120] if c else '-'))
            if not c: kode = 3
        sys.exit(kode)
    c = periksa(S)
    if c: print('ISIAN LOKAL (statis) GAGAL:'); [print('   ✗ ' + x) for x in c]; sys.exit(2)
    n = sum(len(set(re.findall(r'data-ketik="(\w+)"', S[x]))) for x in LAYAR)
    nk = sum(len(set(re.findall(r"\b(KUNCI_\w+)\s*=\s*'miqbal_", S[x]))) for x in LAYAR)
    print('ISIAN LOKAL (statis) LULUS: %d kolom ketik di 8 layar — semuanya menulis ke kunci yang dijaga, atau tercatat sengaja bukan isian (%d); %d kunci localStorage layar — draf dijaga, sisanya tercatat bukan draf' % (n, sum(len(v) for v in BUKAN_ISIAN.values()), nk))
