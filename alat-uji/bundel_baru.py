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


# B1 (owner 16 Nov 2026): jual-logika, nego-logika & sistem-logika memakai harga-tingkat-logika (harga pelanggan usaha). Alat uji lama menyusun daftar
# modulnya sendiri — modul itu ikut OTOMATIS (sekali, di belakang) bila pemakainya ada, supaya tiap alat uji tidak perlu diubah satu per satu.
HT_MODUL = 'baru/js/layar/harga-tingkat-logika.js'
HT_PEMAKAI = ('jual-logika.js', 'nego-logika.js', 'sistem-logika.js')


# owner 17 Nov 2026 (butir 5): berat 1 liter diatur owner — penentunya modul daun kg-liter-logika.js, dipakai Jual, wadah, harga, harga tingkat, nego.
# Ikut OTOMATIS (sekali, di belakang) bila salah satu pemakainya ada; fungsi terangkat, jadi urutan tidak menentukan.
KG_MODUL = 'baru/js/layar/kg-liter-logika.js'
KG_PEMAKAI = ('jual-logika.js', 'wadah-bernama-logika.js', 'harga-logika.js', 'harga-tingkat-logika.js', 'nego-logika.js', 'sistem-logika.js')


# B2 (owner 17 Nov 2026): faktur bertempo & batas kredit — jual-logika (KR1, nomor faktur), bon-logika (alokasi bayar per faktur) memakai faktur-logika,
# yang sendiri memakai harga-tingkat-logika. Ikut OTOMATIS (sekali, di belakang) bila pemakainya ada.
FK_MODUL = 'baru/js/layar/faktur-logika.js'
FK_PEMAKAI = ('jual-logika.js', 'bon-logika.js', 'sistem-logika.js', 'struk-logika.js', 'dasbor-logika.js', 'pelanggan-logika.js')


# B3 (owner 18 Nov 2026): surat jalan & antar — jual-logika (ongkir & surat jalan bersama nota), retur (ongkir tidak ikut dikembalikan), struk, laporan,
# kendali biaya, Dasbor, Pelanggan › Atur, tutup hari & pembatalan nota memakai antar-logika, yang sendiri memakai faktur-logika. Ikut OTOMATIS di belakang.
AJ_MODUL = 'baru/js/layar/antar-logika.js'
AJ_PEMAKAI = ('jual-logika.js', 'retur-logika.js', 'struk-logika.js', 'laporan-logika.js', 'kendali-biaya-logika.js', 'dasbor-logika.js', 'pelanggan-logika.js',
              'uang-logika.js', 'batal-nota-logika.js')


# B4 (owner 18 Nov 2026): pesanan, PO & order rutin — jual-logika (uang muka memotong nota, keranjang dari pesanan), Dasbor (pengingat & stok pesanan),
# Pelanggan › Atur (hari pengingat) memakai pesanan-logika (modul daun: data + pembantu + format). Ikut OTOMATIS (sekali, di belakang).
PO_MODUL = 'baru/js/layar/pesanan-logika.js'
PO_PEMAKAI = ('jual-logika.js', 'dasbor-logika.js', 'pelanggan-logika.js')


def lengkapi(daftar):
    d = list(daftar)
    if any(os.path.basename(x) in PO_PEMAKAI for x in d) and not any(x.endswith('pesanan-logika.js') for x in d):
        d.append(PO_MODUL)
    if any(os.path.basename(x) in AJ_PEMAKAI for x in d) and not any(x.endswith('antar-logika.js') for x in d):
        d.append(AJ_MODUL)
        if not any(x.endswith('faktur-logika.js') for x in d):
            d.append(FK_MODUL)
            if not any(x.endswith('harga-tingkat-logika.js') for x in d):
                d.append(HT_MODUL)
    if any(os.path.basename(x) in FK_PEMAKAI for x in d) and not any(x.endswith('faktur-logika.js') for x in d):
        d.append(FK_MODUL)
        if not any(x.endswith('harga-tingkat-logika.js') for x in d):
            d.append(HT_MODUL)
    if any(os.path.basename(x) in HT_PEMAKAI for x in d) and not any(x.endswith('harga-tingkat-logika.js') for x in d):
        d.append(HT_MODUL)
    if any(os.path.basename(x) in KG_PEMAKAI for x in d) and not any(x.endswith('kg-liter-logika.js') for x in d):
        d.append(KG_MODUL)
    return d


def bundel(daftar, prelude=True):
    bagian = [PRELUDE] if prelude else []
    for p in lengkapi(daftar):
        jalur = p if os.path.isabs(p) else os.path.join(AKAR, p)
        bagian.append('\n// ===== ' + p + ' =====\n' + polos(open(jalur, encoding='utf-8').read()))
    return '\n'.join(bagian)


MODUL_DATA = ['baru/js/data/koleksi.js', 'baru/js/data/kunci-periode.js', 'baru/js/mesin/pembantu.js', 'baru/js/data/toko.js', 'baru/js/mesin/modal-fifo.js', 'baru/js/mesin/beku.js']

if __name__ == '__main__':
    import sys
    sys.stdout.write(bundel(MODUL_DATA))
