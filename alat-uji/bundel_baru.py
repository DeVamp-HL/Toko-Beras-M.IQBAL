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

# Tahap 6 (owner 25 Nov 2026, "stok ikut timbang"): berat ASLI karung per kedatangan — modul daun berat-asli-logika.js (hanya membaca data/toko.js), dipakai
# Barang masuk & Cocokkan, Jual, dan retur. Ikut OTOMATIS (sekali, di belakang) bila salah satu pemakainya ada; fungsi terangkat, jadi urutan tidak menentukan.
# QR satu pintu (owner 26 Nov 2026): struk-logika membakukan nomor WhatsApp toko (setelan struk) dengan tkWaNomor dari tanda-kenal-logika.js (modul daun tanpa
# impor; semua namanya tk… / TK_… / tiga nama pribadi yang tidak dipakai modul lain). Ikut OTOMATIS di belakang bila pemakainya ada; fungsinya terangkat.
TK_MODUL = 'baru/js/layar/tanda-kenal-logika.js'
TK_PEMAKAI = ('struk-logika.js', 'pindai-logika.js')
# cap langganan (owner 26 Nov 2026): struk-logika menulis baris cap pembeli bernama (cap-logika.js — membaca data/toko.js & pembantu saja). Ikut otomatis.
CP_MODUL = 'baru/js/layar/cap-logika.js'
CP_PEMAKAI = ('struk-logika.js',)
# karcis ambil nanti (owner 26 Nov 2026, rules v23): jual-logika menulis catatan titip bersama nota, struk-logika & pindai-logika membacanya (ambil-logika.js —
# membaca data/toko.js & pembantu saja). Ikut otomatis di belakang.
AB_MODUL = 'baru/js/layar/ambil-logika.js'
AB_PEMAKAI = ('jual-logika.js', 'struk-logika.js', 'pindai-logika.js')
BA_MODUL = 'baru/js/layar/berat-asli-logika.js'
BA_PEMAKAI = ('stok-catat-logika.js', 'jual-logika.js', 'retur-logika.js', 'tutup-buku-logika.js')


# B2 (owner 17 Nov 2026): faktur bertempo & batas kredit — jual-logika (KR1, nomor faktur), bon-logika (alokasi bayar per faktur) memakai faktur-logika,
# yang sendiri memakai harga-tingkat-logika. Ikut OTOMATIS (sekali, di belakang) bila pemakainya ada.
FK_MODUL = 'baru/js/layar/faktur-logika.js'
FK_PEMAKAI = ('jual-logika.js', 'bon-logika.js', 'sistem-logika.js', 'struk-logika.js', 'dasbor-logika.js', 'pelanggan-logika.js', 'laba-pelanggan-logika.js')


# B3 (owner 18 Nov 2026): surat jalan & antar — jual-logika (ongkir & surat jalan bersama nota), retur (ongkir tidak ikut dikembalikan), struk, laporan,
# kendali biaya, Dasbor, Pelanggan › Atur, tutup hari & pembatalan nota memakai antar-logika, yang sendiri memakai faktur-logika. Ikut OTOMATIS di belakang.
AJ_MODUL = 'baru/js/layar/antar-logika.js'
AJ_PEMAKAI = ('jual-logika.js', 'retur-logika.js', 'struk-logika.js', 'laporan-logika.js', 'kendali-biaya-logika.js', 'dasbor-logika.js', 'pelanggan-logika.js',
              'uang-logika.js', 'batal-nota-logika.js', 'ganti-pembeli-logika.js')


# B4 (owner 18 Nov 2026): pesanan, PO & order rutin — jual-logika (uang muka memotong nota, keranjang dari pesanan), Dasbor (pengingat & stok pesanan),
# Pelanggan › Atur (hari pengingat) memakai pesanan-logika (modul daun: data + pembantu + format). Ikut OTOMATIS (sekali, di belakang).
PO_MODUL = 'baru/js/layar/pesanan-logika.js'
PO_PEMAKAI = ('jual-logika.js', 'dasbor-logika.js', 'pelanggan-logika.js')


# B5 (owner 18 Nov 2026): laporan per pelanggan (Laporan › Laba › Per pelanggan, kartu Dasbor) — laba-pelanggan-logika memakai laporan-logika, faktur-logika &
# harga-tingkat-logika. Dasbor memakainya; ikut OTOMATIS (sekali, di belakang) — faktur & harga tingkat menyusul lewat FK_PEMAKAI.
# owner 24 Nov 2026: grosir vs ecer per jenis barang — dibaca rekap harian Laporan, teks WA tutup hari, dan Dasbor (lewat rekapHari)
GE_MODUL = 'baru/js/layar/grosir-ecer-logika.js'
GE_PEMAKAI = ('laporan-logika.js', 'tutup-hari-logika.js', 'dasbor-logika.js')
PG_MODUL = 'baru/js/layar/laba-pelanggan-logika.js'
PG_PEMAKAI = ('dasbor-logika.js',)



# owner 21 Nov 2026: titipan uang keluar & pesan dari tablet — Uang (titipan menunggu), papan Persetujuan (sistem-logika) & tutup hari memakai
# titipan-logika (modul daun: data + format). Ikut OTOMATIS (sekali, di belakang) bila pemakainya ada.
TP_MODUL = 'baru/js/layar/titipan-logika.js'
TP_PEMAKAI = ('uang-logika.js', 'sistem-logika.js', 'tutup-hari-logika.js')


# paket KPI laba (owner 24 Nov 2026): Dasbor memakai kpi-laba-logika (tiga margin, target harian, kas minimum, siklus uang, nota terbesar …) — modul itu ikut
# OTOMATIS (sekali, di belakang, sesudah semua sumbernya), bersama riwayat-logika (nota terbesar = nota Jual › Riwayat) bila belum ada.
KL_MODUL = 'baru/js/layar/kpi-laba-logika.js'
KL_PEMAKAI = ('dasbor-logika.js',)
RW_MODUL = 'baru/js/layar/riwayat-logika.js'
# Pondasi (owner 24 Nov 2026): Dasbor memakai pondasi-logika (delapan lampu) — ikut OTOMATIS sesudah kpi-laba-logika (ia membaca klAtur: kas minimum).
# pdDisiplin (cek gudang, tutup hari) hanya dipanggil Laporan; bundel Dasbor tidak perlu sistem-logika.
PD_MODUL = 'baru/js/layar/pondasi-logika.js'
PD_PEMAKAI = ('dasbor-logika.js',)


# owner 26 Nov 2026 (kas & rekening): Dasbor memakai kas-rekening-logika (awal hari semua tempat, cocok rekening) — modul itu membaca uang-logika & data/toko.js.
# Ikut OTOMATIS (sekali, di belakang) bila pemakainya ada; fungsi terangkat, jadi urutan tidak menentukan.
KR_MODUL = 'baru/js/layar/kas-rekening-logika.js'
KR_PEMAKAI = ('dasbor-logika.js',)

# paket Susut + HPP & harga minimum (owner 26 Nov 2026): Dasbor memakai susut-harga-logika (target susut, opname bulan ini, harga minimum, alarm HET) — modul itu
# hanya membaca laporan / kendali biaya / harga / HET / stok-catat / jual, yang sudah ada di bundel Dasbor. Ikut OTOMATIS (sekali, di belakang).
SH_MODUL = 'baru/js/layar/susut-harga-logika.js'
SH_PEMAKAI = ('dasbor-logika.js',)
# paket P3 (owner 27 Nov 2026, A4): sumber peringatan uang (lonceng & Pengingat) — dasbor-logika memakainya untuk widget Peringatan uang. Ikut otomatis di belakang.
PW_MODUL = 'baru/js/layar/peringatan-logika.js'
PW_PEMAKAI = ('dasbor-logika.js',)

# paket Banding pemasok (owner 26 Nov 2026): pengingat mingguan / bulanan & papan Persetujuan (usul harga tawaran / acuan dari tablet) — sistem-logika memakai
# banding-catat-logika (modul DAUN: data + pembantu + format). Ikut OTOMATIS (sekali, di belakang) bila pemakainya ada. Hitungan banding (banding-pemasok-logika)
# hanya dipakai layar Harga & Pemasok — bundel ujinya menyebutnya sendiri.
BC_MODUL = 'baru/js/layar/banding-catat-logika.js'
BC_PEMAKAI = ('sistem-logika.js', 'banding-pemasok-logika.js')
# owner 26 Nov 2026: lokasi langit & cuaca gerbang — atur Perangkat (sistem-logika) & pemilih tempat (menu.js) memakai langit-logika (modul DAUN, tanpa impor)
LG_MODUL = 'baru/js/inti/langit-logika.js'
LG_PEMAKAI = ('sistem-logika.js', 'menu.js')


# paket Stok minus, label & kepatuhan (owner 26 Nov 2026): Dasbor memakai gudang-logika (buku minus, hilang & rusak per jenis, tugas gudang — membaca belanja-logika
# untuk pesanan ke pemasok, jenis-beras-logika, label-logika untuk kemasan bertanggal) dan patuh-logika (kalender kepatuhan). Semua modul daun / sudah ada di bundel
# Dasbor; ikut OTOMATIS (sekali, di belakang) bila pemakainya ada. gudang-logika sengaja TIDAK memakai sistem-logika (sistem-logika menerimanya lewat lokal.gudang).
GD_MODUL = ['baru/js/layar/gudang-logika.js', 'baru/js/layar/label-logika.js', 'baru/js/layar/patuh-logika.js', 'baru/js/layar/belanja-logika.js', 'baru/js/layar/jenis-beras-logika.js']
GD_PEMAKAI = ('dasbor-logika.js', 'gudang-logika.js')
# paket Dasbor sensus (owner 26 Nov 2026, B127 "Hari + kg per barang"): stok minimum per barang — modul DAUN stok-minimum-logika.js (data/toko.js + format), dipakai
# Belanja (batas per merek), Ringkasan (Perlu perhatian) & Dasbor. Ikut OTOMATIS (sekali, di belakang) bila pemakainya ada; fungsi terangkat, urutan tidak menentukan.
SM_MODUL = 'baru/js/layar/stok-minimum-logika.js'
SM_PEMAKAI = ('belanja-logika.js', 'ringkasan-logika.js', 'dasbor-logika.js')
# layar Stok (stok.js) memasang lembar stok minimum (stok-minimum-panel.js → stok-minimum-logika + daftarBarang stok-logika) — ikut OTOMATIS bila stok.js dibundel
SMP_MODUL = 'baru/js/layar/stok-minimum-panel.js'


# owner 26 Nov 2026 (modul ERP no. 70): aset tetap & penyusutan — modul DAUN aset-tetap-logika.js (data/toko.js + format saja) dibaca uang-logika (ugLabaBersih).
# Ikut OTOMATIS (sekali) DI DEPAN uang-logika.js bila pemakainya ada: konstanta `const` modul itu sudah hidup sebelum modul lain memanggilnya.
AS_MODUL = 'baru/js/layar/aset-tetap-logika.js'
AS_PEMAKAI = ('uang-logika.js',)
# layar Laporan memakai aset-panel.js (Laporan › Aset tetap) — ikut OTOMATIS di belakang bila laporan.js ada.
ASP_MODUL = 'baru/js/layar/aset-panel.js'
ASP_PEMAKAI = ('laporan.js',)
# Laporan › Jurnal (owner 26 Nov 2026, modul ERP no. 69): jurnal-logika.js + jurnal-panel.js ikut OTOMATIS di belakang bila laporan.js ada.
JR_MODUL = ('baru/js/layar/jurnal-logika.js', 'baru/js/layar/jurnal-panel.js')

# paket tanggal janji (owner 27 Nov 2026, rules v24): Dasbor (KPI), Stok › Tugas gudang, Laporan › Pondasi, Harga › Belanja & Barang masuk tablet memakai
# janji-logika.js (membaca data/toko.js, pembantu, bon-pemasok-logika & pesanan-logika). Ikut OTOMATIS (sekali, di belakang) bila pemakainya ada, bersama
# dua sumbernya bila belum ada; fungsi terangkat, konstantanya hanya dipakai di dalam fungsi — urutan tidak menentukan.
JN_MODUL = 'baru/js/layar/janji-logika.js'
JN_PEMAKAI = ('dasbor-logika.js', 'gudang-logika.js', 'laporan.js', 'stok.js', 'harga.js')
JN_SUMBER = ('baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/pesanan-logika.js')


# paket P2 (owner 27 Nov 2026): rapor bulanan (lembar KPI, anggaran vs aktual, pecahan selisih, kotor vs bersih, arus kas) — rapor-bulan-logika.js dibaca Dasbor
# (kelompok rapor) dan layar Laporan. Ia hanya memanggil modul yang sudah ada di bundel Dasbor / Laporan (kendali-biaya, pajak, kpi-laba, laporan, susut-harga, karcis,
# uang, mesin) — ikut OTOMATIS (sekali, di belakang) bila pemakainya ada; fungsi terangkat, urutan tidak menentukan.
RB_MODUL = 'baru/js/layar/rapor-bulan-logika.js'
RB_PEMAKAI = ('dasbor-logika.js', 'laporan.js')


# paket P5 (owner 27 Nov 2026, A50): Adukan memeriksa kelas bahan vs label hasil (oplos) lewat modul DAUN kelas-het-logika.js (data/toko.js + pembantu + jual-logika
# aturWadah — semuanya sudah ada di tiap bundel yang memuat stok-adukan-logika). Ikut OTOMATIS (sekali, di belakang) bila stok-adukan-logika ada.
KH_MODUL = 'baru/js/layar/kelas-het-logika.js'
KH_PEMAKAI = ('stok-adukan-logika.js',)


# paket P5 (owner 27 Nov 2026): stok-pantau-logika.js (kartu stok, barang masuk hari itu, hitung mingguan, opname kejutan, rencana beli, stok dipesan, produksi)
# dibaca gudang-logika (Tugas gudang), Dasbor, Laporan, Stok, Harga & Sistem. Sumbernya (stok-catat, stok-adukan, pesanan, laporan-logika) sudah ada di bundel Dasbor;
# ikut OTOMATIS (sekali, di belakang) bila pemakainya ada. Fungsi terangkat, konstantanya hanya dipakai di dalam fungsi — urutan tidak menentukan.
SG_MODUL = 'baru/js/layar/stok-pantau-logika.js'
SG_PEMAKAI = ('gudang-logika.js', 'dasbor-logika.js', 'laporan.js', 'stok.js', 'harga.js', 'app.js')


# paket P6 (owner 27 Nov 2026): selisih laci (laci-logika, A119 + A82) dibaca Dasbor & layar Uang; daftar centang rutin (rutin-logika, A143) dibaca Dasbor, halaman tugas
# staf & panelnya. Ikut OTOMATIS (sekali, di belakang) bila pemakainya ada; rutin-logika membawa sumber butir otomatisnya (gudang, wadah bernama, kepatuhan) bila belum
# ada — karcis-logika TIDAK ditarik (rantainya panjang; bundel Dasbor sudah memuatnya, alat uji lain menyebutnya sendiri).
LH_MODUL = 'baru/js/layar/laci-logika.js'
LH_PEMAKAI = ('dasbor-logika.js', 'uang.js', 'app.js')
RN_MODUL = 'baru/js/layar/rutin-logika.js'
RN_PEMAKAI = ('dasbor-logika.js', 'tugas-staf-logika.js', 'rutin-panel.js')
RN_SUMBER = ('baru/js/layar/wadah-bernama-logika.js', 'baru/js/layar/patuh-logika.js', 'baru/js/layar/gudang-logika.js')
# paket P8 (owner 27 Nov 2026, A94): Dasbor › Mutu menghitung nota & bon yang belum berfoto (arsip-foto-logika.js — membaca data/toko.js, pembantu & format saja; semua
# namanya af… / AF_…). Ikut OTOMATIS di belakang bila pemakainya ada; fungsinya terangkat.
AF_MODUL = 'baru/js/layar/arsip-foto-logika.js'
AF_PEMAKAI = ('dasbor-logika.js', 'foto-nota-panel.js', 'arsip-audit-panel.js', 'app.js')


def lengkapi(daftar):
    d = list(daftar)
    if any(os.path.basename(x) in SG_PEMAKAI for x in d) and not any(x.endswith('stok-pantau-logika.js') for x in d):
        d.append(SG_MODUL)
    if any(os.path.basename(x) in KH_PEMAKAI for x in d) and not any(x.endswith('kelas-het-logika.js') for x in d):
        d.append(KH_MODUL)
    if any(os.path.basename(x) in LH_PEMAKAI for x in d) and not any(x.endswith('laci-logika.js') for x in d):
        d.append(LH_MODUL)
    if any(os.path.basename(x) in AF_PEMAKAI for x in d) and not any(x.endswith('arsip-foto-logika.js') for x in d):
        d.append(AF_MODUL)
    if any(os.path.basename(x) in RN_PEMAKAI for x in d) and not any(x.endswith('rutin-logika.js') for x in d):
        d.append(RN_MODUL)
        for m in RN_SUMBER:
            if not any(x.endswith(os.path.basename(m)) for x in d): d.append(m)
    if any(os.path.basename(x) in JN_PEMAKAI for x in d) and not any(x.endswith('janji-logika.js') for x in d):
        d.append(JN_MODUL)
        for m in JN_SUMBER:
            if not any(x.endswith(os.path.basename(m)) for x in d): d.append(m)
    if any(os.path.basename(x) in AS_PEMAKAI for x in d) and not any(x.endswith('aset-tetap-logika.js') for x in d):
        i = next(i for i, x in enumerate(d) if os.path.basename(x) in AS_PEMAKAI)
        d.insert(i, AS_MODUL)
    if any(os.path.basename(x) in ASP_PEMAKAI for x in d) and not any(x.endswith('aset-panel.js') for x in d):
        d.append(ASP_MODUL)
    if any(os.path.basename(x) in ASP_PEMAKAI for x in d):
        for m in JR_MODUL:
            if not any(x.endswith(m) for x in d): d.append(m)
    if any(os.path.basename(x) in GD_PEMAKAI for x in d):
        for m in GD_MODUL:
            if not any(x.endswith(os.path.basename(m)) for x in d): d.append(m)
    if any(os.path.basename(x) in KR_PEMAKAI for x in d) and not any(x.endswith('kas-rekening-logika.js') for x in d):
        d.append(KR_MODUL)
    if any(os.path.basename(x) in SH_PEMAKAI for x in d) and not any(x.endswith('susut-harga-logika.js') for x in d):
        d.append(SH_MODUL)
    if any(os.path.basename(x) in PW_PEMAKAI for x in d) and not any(x.endswith('peringatan-logika.js') for x in d):
        d.append(PW_MODUL)
    if any(os.path.basename(x) in BC_PEMAKAI for x in d) and not any(x.endswith('banding-catat-logika.js') for x in d):
        d.append(BC_MODUL)
    if any(os.path.basename(x) in KL_PEMAKAI for x in d) and not any(x.endswith('kpi-laba-logika.js') for x in d):
        if not any(x.endswith('riwayat-logika.js') for x in d): d.append(RW_MODUL)
        d.append(KL_MODUL)
    if any(os.path.basename(x) in PD_PEMAKAI for x in d) and not any(x.endswith('pondasi-logika.js') for x in d):
        d.append(PD_MODUL)
    if any(os.path.basename(x) in LG_PEMAKAI for x in d) and not any(x.endswith('langit-logika.js') for x in d):
        d.append(LG_MODUL)
    if any(os.path.basename(x) in TP_PEMAKAI for x in d) and not any(x.endswith('titipan-logika.js') for x in d):
        d.append(TP_MODUL)
    if any(os.path.basename(x) in GE_PEMAKAI for x in d) and not any(x.endswith('grosir-ecer-logika.js') for x in d):
        d.append(GE_MODUL)
    if any(os.path.basename(x) in PG_PEMAKAI for x in d) and not any(x.endswith('laba-pelanggan-logika.js') for x in d):
        d.append(PG_MODUL)
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
    if any(os.path.basename(x) in BA_PEMAKAI for x in d) and not any(x.endswith('berat-asli-logika.js') for x in d):
        d.append(BA_MODUL)
    if any(os.path.basename(x) == 'stok.js' for x in d) and not any(x.endswith('stok-minimum-panel.js') for x in d):
        d.append(SMP_MODUL)
    if any(os.path.basename(x) in SM_PEMAKAI + ('stok-minimum-panel.js',) for x in d) and not any(x.endswith('stok-minimum-logika.js') for x in d):
        d.append(SM_MODUL)
    if any(os.path.basename(x) in TK_PEMAKAI for x in d) and not any(x.endswith('tanda-kenal-logika.js') for x in d):
        d.append(TK_MODUL)
    if any(os.path.basename(x) in CP_PEMAKAI for x in d) and not any(x.endswith('cap-logika.js') for x in d):
        d.append(CP_MODUL)
    if any(os.path.basename(x) in AB_PEMAKAI for x in d) and not any(x.endswith('ambil-logika.js') for x in d):
        d.append(AB_MODUL)
    if any(os.path.basename(x) in RB_PEMAKAI for x in d) and not any(x.endswith('rapor-bulan-logika.js') for x in d):
        d.append(RB_MODUL)
    return d


def bundel(daftar, prelude=True):
    bagian = [PRELUDE] if prelude else []
    for p in lengkapi(daftar):
        jalur = p if os.path.isabs(p) else os.path.join(AKAR, p)
        bagian.append('\n// ===== ' + p + ' =====\n' + polos(open(jalur, encoding='utf-8').read()))
    return '\n'.join(bagian)


# Tahap 6 (owner 25 Nov 2026, "stok ikut timbang"): kedatangan BARU wajib ditimbang dan stoknya dibukukan dari hasil timbang. Skenario alat uji yang ditulis
# sebelum aturan itu memasang penimbang PAS ini di depan SKENARIO-nya: draf baru tanpa timbang / sampel ditimbang = kg nota − kg dipotong (klaim langsung =
# selisih timbang), jadi angka bukunya sama dengan nota seperti dulu. Baris bertimbang / bersampel, kemasan jadi, baris ditolak, dan koreksi tidak disentuh.
# Jalur aslinya tetap tersedia sebagai _ssm (dipakai kasus Tahap 6 sendiri di uji_barang_masuk_baru / uji_masuk_tablet).
TIMBANG_PAS = r"""
var _tpKosong = function (v) { return v === undefined || v === null || String(v).trim() === ''; };
var _tpAngka = function (v, b) { var t = String(v === undefined || v === null || v === '' ? b : v); return Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t) || 0; };
function pasTimbang(d) { if (!d || d.id) return d; var x = JSON.parse(JSON.stringify(d)); (x.baris || []).forEach(function (b) { if (!b || b.masuk === 'kemasan' || b.ditolak) return;
  if (!_tpKosong(b.timbangKg) || !_tpKosong(b.sampelKarung) || !_tpKosong(b.sampelKg)) return; var j = _tpAngka(b.jumlahKarung, ''), be = _tpAngka(b.beratKarung, 50) || 50, pot = _tpAngka(b.kgPotong, 0);
  if (j > 0) b.timbangKg = String(Math.round((j * be - pot) * 100) / 100).replace('.', ','); }); return x; }
var _ssm = susunSimpanMasuk; susunSimpanMasuk = function (d, w, y) { return _ssm(pasTimbang(d), w, y); };
"""


# owner 26 Nov 2026: aset-tetap-logika.js (modul daun: toko.js + format) ikut di sini — uang-logika (laba bersih) memakainya, dan banyak alat uji menyusun daftar modulnya
# sendiri dari MODUL_DATA tanpa lengkapi().
MODUL_DATA = ['baru/js/data/koleksi.js', 'baru/js/data/kunci-periode.js', 'baru/js/mesin/pembantu.js', 'baru/js/data/toko.js', 'baru/js/mesin/modal-fifo.js', 'baru/js/mesin/beku.js', 'baru/js/layar/aset-tetap-logika.js']

if __name__ == '__main__':
    import sys
    sys.stdout.write(bundel(MODUL_DATA))
