#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pindah_mesin.py — memindahkan MESIN UANG BEKU dari index.html ke sistem baru (baru/js/mesin/)
APA ADANYA: tubuh fungsi disalin byte demi byte oleh alat ini, bukan diketik ulang.

Keluaran:
  baru/js/mesin/beku.js      — mesin beku (daftar BEKU di beku2.py, minus yang terikat layar)
  baru/js/mesin/pembantu.js  — fungsi & konstanta pembantu yang dipanggil mesin (verbatim juga)

Batas data: fungsi ambil*(), bacaCadanganLokal, wzDiKeranjangAktif/Parkir, ambilTitikKas TIDAK
disalin — mereka milik lapisan data sistem baru (baru/js/data/toko.js) dan diimpor dari sana.

Mode:
  (tanpa opsi)   tulis kedua berkas dari index.html sekarang
  --periksa      jangan menulis; bandingkan tiap mesin di baru/js/mesin/beku.js dengan alat-uji/beku.sha256
                 (kode keluar 2 bila ada yang beda/hilang) — ini gerbang CI sistem baru
"""
import os, re, sys, hashlib

SINI = os.path.dirname(os.path.abspath(__file__))
AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import beku2  # noqa: E402

INDEX = os.path.join(AKAR, 'index.html')
SIDIK = os.path.join(AKAR, 'alat-uji', 'beku.sha256')
KELUAR_BEKU = os.path.join(AKAR, 'baru', 'js', 'mesin', 'beku.js')
KELUAR_PEMBANTU = os.path.join(AKAR, 'baru', 'js', 'mesin', 'pembantu.js')

# Mesin yang terikat layar lama (document/alert) — belum dipindah; disebut di keluaran supaya tidak diam.
BELUM_DIPINDAH = {'tulisSaldoPembuka': 'ritual Tutup Buku, memakai alert/confirm dan 700+ fungsi layar',
                  'thPagar': 'pagar Tutup Hari, membaca document'}
# Pembantu yang dipakai lapisan data (toko.js) di luar mesin — ikut dipindah verbatim supaya toko.js
# tidak menyalin tangan: saringan dokumen berlaku & penjumlah keranjang.
TAMBAHAN = ['penjualanMasihBerlaku', 'produksiMasihBerlaku', 'wzJumlahDiDaftar', 'kunciKemasan',
            # pembaca yang dipakai layar Jual sistem baru — verbatim juga, supaya harga & sisa dibaca dengan aturan yang sama
            'merkPunyaKarungBerat', 'hargaKarungUtuh', 'cariHargaKarungPerKg', 'tentukanKemasanLiteran', 'jumlahKemasanLiteran',
            'hargaBahanLiteranEfektif', 'catatanPelangganBerisi', 'infoKreditPelanggan', 'pesananBelumTuntas',
            # putaran 4 — RETUR menunjuk nota: dasar harga, sisa yang boleh kembali, rantai koreksi — verbatim, supaya nilai retur dihitung dengan aturan yang sama
            'rtKunciNota', 'rtRantaiNota', 'rtDasarNota', 'rtKalimatLebih', 'twBanyak', 'twSatuanDibayar']
# Konstanta aturan toko yang dibaca layar Jual (rasio liter→kg, lantai nego) — verbatim dari index.html
KONSTANTA_TAMBAHAN = ['RASIO_KONVERSI', 'RASIO_DEFAULT', 'NEGO_LANTAI', 'JENIS_LITERAN_KHUSUS', 'KAPASITAS_KARUNG_BEKAS_LITER',
                      'AMBANG_HARI_KRITIS']   # Ringkasan: ambang "menipis" menurut laju jual — sama dengan layar Stok lama
# Batas lapisan data: tidak disalin, diimpor dari baru/js/data/toko.js
def batas(nama):
    return nama.startswith('ambil') or nama in ('bacaCadanganLokal', 'wzDiKeranjangAktif', 'wzDiKeranjangParkir')

KW = set('function return const let var if else for while do switch case break continue new this typeof instanceof '
         'in of true false null undefined try catch finally throw async await class extends super import export default '
         'delete void yield Math Number String Array Object JSON Date parseInt parseFloat isNaN isFinite Set Map console '
         'Promise Error Boolean RegExp Infinity NaN'.split())


def modul_index():
    teks = open(INDEX, encoding='utf-8').read()
    return teks[teks.index('<script type="module">'):teks.rindex('</script>')]


def tanpa_komentar(b):
    b = re.sub(r'/\*.*?\*/', '', b, flags=re.S)
    return re.sub(r'(^|[^:\\])//[^\n]*', r'\1', b)


def deklarasi(mod):
    fn = set(re.findall(r'\n  (?:async\s+)?function\s+(\w+)\s*\(', mod))
    konst = {}
    # konstanta tingkat modul: `  const NAMA = ...;` satu pernyataan (kurung seimbang sampai ';' pada kedalaman 0)
    for m in re.finditer(r'\n  const\s+([A-Z_][A-Z0-9_]*)\s*=', mod):
        i = m.end(); d = 0; j = i; dalam = None
        while j < len(mod):
            c = mod[j]
            if dalam:
                if c == '\\': j += 2; continue
                if c == dalam: dalam = None
            elif c in '"\'`': dalam = c
            elif c in '([{': d += 1
            elif c in ')]}': d -= 1
            elif c == ';' and d == 0: break
            j += 1
        konst[m.group(1)] = mod[m.start() + 1:j + 1]
    return fn, konst


def pengenal(tubuh):
    return set(re.findall(r'(?<![.\w$])([A-Za-z_$][\w$]*)', tanpa_komentar(tubuh))) - KW


def kumpulkan(mod, mesin):
    fn, konst = deklarasi(mod)
    tubuh = {}
    urutan = []      # urutan tulis: pembantu dulu (kedalaman dulu), mesin belakangan
    pakai_konst = set()
    impor = set()

    def masuk(nama):
        if nama in tubuh: return
        if batas(nama): impor.add(nama); return
        b = beku2.potong(mod, nama)
        if b is None: raise SystemExit('tidak ketemu fungsi ' + nama)
        tubuh[nama] = b
        ids = pengenal(b)
        for d in sorted(ids & fn):
            if d != nama: masuk(d)
        for k in sorted(ids & set(konst)): pakai_konst.add(k)
        urutan.append(nama)
    for n in list(mesin) + TAMBAHAN: masuk(n)
    for k in KONSTANTA_TAMBAHAN:
        if k not in konst: raise SystemExit('konstanta tidak ketemu: ' + k)
        pakai_konst.add(k)
    # konstanta bisa merujuk konstanta lain
    tambah = True
    while tambah:
        tambah = False
        for k in list(pakai_konst):
            for d in pengenal(konst[k]) & set(konst):
                if d not in pakai_konst: pakai_konst.add(d); tambah = True
    return tubuh, urutan, sorted(pakai_konst), sorted(impor), konst


def sidik(tubuh):
    return hashlib.sha256(tubuh.encode('utf-8')).hexdigest()


def tulis():
    mod = modul_index()
    mesin = [m for m in beku2.BEKU if m not in BELUM_DIPINDAH]
    tubuh, urutan, pakai_konst, impor, konst = kumpulkan(mod, mesin)
    pembantu = [n for n in urutan if n not in mesin]
    kepala = ('// DIBUAT OLEH alat-uji/pindah_mesin.py — JANGAN DISUNTING TANGAN.\n'
              '// Tubuh tiap fungsi disalin byte demi byte dari index.html; gerbang: `python3 alat-uji/pindah_mesin.py --periksa`.\n')
    daftar_impor = ', '.join(impor)
    os.makedirs(os.path.dirname(KELUAR_BEKU), exist_ok=True)
    # pembantu yang memanggil MESIN (mis. infoKreditPelanggan → hitungPiutang): diimpor balik dari beku.js
    mesin_dipakai_pembantu = sorted({m for n in pembantu for m in (pengenal(tubuh[n]) & set(mesin))})
    with open(KELUAR_PEMBANTU, 'w', encoding='utf-8') as f:
        f.write(kepala + '// Pembantu: konstanta & fungsi yang dipanggil mesin beku (bukan mesin, tapi ikut verbatim).\n')
        f.write("import { " + daftar_impor + " } from '../data/toko.js';\n")
        if mesin_dipakai_pembantu: f.write("import { " + ', '.join(mesin_dipakai_pembantu) + " } from './beku.js';\n")
        f.write('\n')
        for k in pakai_konst: f.write(konst[k] + '\n')
        # Potongan beku2.potong() SUDAH memuat deretan baris kosong + indentasi persis seperti di index.html
        # (regex-nya mulai dari '\n' pertama). Ditulis berturut-turut TANPA pemisah supaya potong() atas berkas
        # ini menghasilkan byte yang sama — satu baris kosong tambahan saja mengubah sidiknya.
        f.write('// ---- fungsi pembantu (verbatim) ----')
        for n in pembantu: f.write(tubuh[n])
        f.write('\n\nexport { ' + ', '.join(pakai_konst + pembantu) + ' };\n')
    with open(KELUAR_BEKU, 'w', encoding='utf-8') as f:
        f.write(kepala + '// MESIN UANG BEKU (' + str(len(mesin)) + ' dari ' + str(len(beku2.BEKU)) + '). Belum dipindah: '
                + '; '.join(k + ' (' + v + ')' for k, v in BELUM_DIPINDAH.items()) + '.\n')
        f.write("import { " + daftar_impor + " } from '../data/toko.js';\n")
        f.write("import { " + ', '.join(pakai_konst + pembantu) + " } from './pembantu.js';\n")
        f.write('// ---- mesin beku (verbatim; lihat catatan di pembantu.js soal baris kosong) ----')
        for n in mesin: f.write(tubuh[n])
        f.write('\n\nexport { ' + ', '.join(mesin) + ' };\n')
    print('beku.js:', len(mesin), 'mesin ·', 'pembantu.js:', len(pembantu), 'fungsi +', len(pakai_konst), 'konstanta ·',
          'diimpor dari toko.js:', len(impor))
    return periksa()


def periksa():
    teks = open(KELUAR_BEKU, encoding='utf-8').read()
    kanon = {}
    for ln in open(SIDIK, encoding='utf-8'):
        b = ln.split()
        if len(b) == 2 and len(b[0]) == 64: kanon[b[1]] = b[0]
    beda = []; ada = 0
    for n in beku2.BEKU:
        if n in BELUM_DIPINDAH: continue
        t = beku2.potong(teks, n)
        if t is None: beda.append('HILANG ' + n); continue
        # potong() menyimpan baris & indentasi asli; sidik di beku.sha256 dihitung beku2.sidik() atas potongan yang sama
        if beku2.sidik(t) != kanon.get(n): beda.append('BEDA ' + n)
        else: ada += 1
    if beda:
        print('MESIN BERUBAH/HILANG di sistem baru:'); [print('  ' + x) for x in beda]; return 2
    print('sistem baru: %d/%d mesin byte-identik dengan beku.sha256; belum dipindah: %s' % (ada, len(beku2.BEKU), ', '.join(BELUM_DIPINDAH)))
    return 0


if __name__ == '__main__':
    sys.exit(periksa() if '--periksa' in sys.argv else tulis())
