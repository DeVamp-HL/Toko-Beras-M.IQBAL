#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gladi_data_contoh.py — DATA CONTOH SINTETIS skala toko untuk GLADI TUTUP BUKU di Firebase Emulator (runner GitHub). Benih tetap → isi sama tiap kali.

BUKAN data toko: semua nama (merek, pelanggan, pemasok, karyawan) & angka rupiah DIKARANG oleh skrip ini. Cadangan asli tidak dibaca, tidak disalin.
Bentuk dokumen = bentuk cadangan sistem baru (versi 5: satu daftar per koleksi, kolom yang dipakai mesin beku & layar), tahun 2026 (8 Agu – 31 Des):
kedatangan (tunai & bon), jual karung / literan / kemasan / karcis kasir darurat yang sudah dirinci / nota batal, adukan kemasan, kantong & paper bag,
bon pelanggan + pembayaran (ada yang lancar, ada yang menua), bon pemasok + pembayaran, kasbon, belanja toko pakai dompet owner, uang keluar, tutup hari
(+ setoran, sisihan amplop, titik kas), biaya bulanan, katalog harga, denyut perangkat lama, jejak, catatan cadangan.

VARIAN
  macet   (bawaan) 23 hari berjualan TANPA tutup hari (5 di Agustus, 15 September, 3 Oktober — pola yang sama dengan keadaan toko 6 Okt 2026):
          gerbang g1 tutup buku SUNGGUHAN wajib memblokir dan susunKunci wajib MENOLAK; sesudah putusan per tanggal "tidak ditutup — diterima apa
          adanya" (Paket A, susunPutusanHari logika /baru/) semua gerbang beres dan ritual SUNGGUHAN bisa jalan sampai kunci. Gladi ritual memakai varian ini.
  bersih  semua hari berjualan ditutup: semua gerbang beres tanpa putusan, ritual SUNGGUHAN bisa jalan sampai kunci.
  terkunci (rules v7, pintu tutup buku) = macet + SEMUA bulan 2026 DIKUNCI (aturanToko/kunciPeriode sampai 2026-12, kunci Desember sah sejak 4 Jan) + dua
          pindahan uang bertanggal bulan terkunci (koleksi yang TIDAK diarsip — wajib tetap utuh selama pintu terbuka). Dinilai di JAM_PINTU (5 Jan 2027
          15.30 WIB): tahun 2026 boleh ditutup sungguhan LEWAT PINTU; sesudah putusan, susunKunci = kiriman 1 berita acara 'berjalan' SENDIRIAN, kiriman 2
          membuka pintu (tahun 2026, ≤ 72 jam), titik kas 31 Des lewat pintu, tiap kiriman ≤ 18 pemeriksaan.
Dua-duanya: tidak ada stok / kemasan / kantong minus, tidak ada kelebihan bayar, tidak ada karcis yang belum dirinci, ±9 rb dokumen (--skala / GLADI_SKALA,
bawaan 0,65 — batas antrean pesan emulator, lihat SKALA_BAWAAN).

    python3 alat-uji/gladi_data_contoh.py --keluar data.json [--varian macet|bersih|terkunci] [--benih N] [--skala 1.0]
    python3 alat-uji/gladi_data_contoh.py --periksa   → kedua varian dinilai LOGIKA /baru/ ASLI (jsc, atau node di runner Linux):
          31 Des LATIHAN: 12 baris sebelum = sesudah ("sama persis"), gerbang sesuai varian; 1 Jan SUNGGUHAN boleh; macet: susunKunci DITOLAK
          karena g1, lalu putusan per tanggal → susunKunci jadi beberapa kiriman ≤ 18 pemeriksaan; bersih: langsung jadi; stok/kemasan/kantong ≥ 0;
          tanpa kelebihan bayar; jumlah dokumen dalam rentang skala toko.
    python3 alat-uji/gladi_data_contoh.py --kontrol   → data yang dirusak (stok minus, karcis belum dirinci, tutup hari hilang/bertambah,
          kelebihan bayar, titik kas hilang) wajib membuat --periksa berbunyi (keluar 3 kalau ada yang diam).
"""
import os, re, sys, json, math, random, shutil, datetime, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)

BENIH = 20270101
MULAI, AKHIR = datetime.date(2026, 8, 8), datetime.date(2026, 12, 31)
WIB = datetime.timezone(datetime.timedelta(hours=7))
# jam halaman untuk LATIHAN (31 Des sesudah tutup hari terakhir) & SUNGGUHAN (1 Jan sesudah reset kuota 15.00 WIB) — sama dengan pelari gladi
JAM_LATIHAN, JAM_SUNGGUHAN = '2026-12-31T21:45:00+07:00', '2027-01-01T15:30:00+07:00'
# varian terkunci (rules v7): semua bulan 2026 dikunci — Desember paling cepat dikunci 4 Jan (tenggang minimal 3 hari, rules tenggangMin), jadi gladi pintu
# berjalan 5 Jan 2027 sesudah reset kuota. Jam server emulator digeser ke jam yang sama (gladi_tutup_buku.py --geser-jam, alat-uji/jam_geser.c).
JAM_PINTU, KUNCI_PINTU = '2027-01-05T15:30:00+07:00', '2026-12'
PERANGKAT_GLADI = 'p-gladi-runner'
# rentang "skala toko" (proyeksi akhir Des ±16,5–18 rb dokumen arsip; tugas gladi: ±8–20 rb)
RENTANG_DOK = (8000, 20000)
# SKALA BAWAAN 0,65 (±9 rb dokumen, penjualan ±6 rb): Firestore EMULATOR membatasi 10.000 pesan antre per kanal WebChannel (run 7 Okt: data 17 rb →
# "too many pending messagings in the back channel (10001)", pendengar tidak pernah menerima data, kanal diputus berulang). Server sungguhan tidak punya
# batas itu. Angka baca/tulis/hapus hari ritual skala toko (±16,5–18 rb) = hasil gladi × (dokumen toko ÷ dokumen gladi) — laporan gladi menghitungnya.
SKALA_BAWAAN = float(os.environ.get('GLADI_SKALA') or 0.65)
# varian terkunci (skenario pintu): yang diuji MEKANISME pintu, bukan skala — tiap catatan bulan terkunci butuh 5 pemeriksaan (arsip 3 catatan per kiriman,
# bukan 9), jadi skala toko berarti ±3 rb kiriman per arsip, ×3 (arsip, batal, arsip lagi). Skala 0,05 (±1,7 rb dokumen, arsip ±1,3 rb, 23 hari macet tetap)
# = ±450 kiriman per jalan; angka kuota skala toko tetap diproyeksikan (× dokumen toko ÷ dokumen gladi). GLADI_SKALA_PINTU mengubahnya.
SKALA_TERKUNCI = float(os.environ.get('GLADI_SKALA_PINTU') or 0.05)
RENTANG_DOK_TERKUNCI = (1000, 20000)
# hari tanpa tutup hari varian macet: (bulan, jumlah) — pola keadaan toko 6 Okt 2026 (Agu 5 · Sep 15 · Okt 3)
POLA_MACET = [(8, 5), (9, 15), (10, 3)]

# ---- DUNIA CONTOH (dikarang) ----
# (merek, HPP per kg awal, jual literan?) — karung 50 kg
MEREK = [('Contoh Alfa', 12400, True), ('Contoh Bravo', 13100, True), ('Contoh Ceri', 13800, True), ('Contoh Dahlia', 14600, True),
         ('Contoh Elang', 15300, False), ('Contoh Fajar', 16200, False), ('Ketan Contoh', 19500, False)]
# kemasan jadi: (nama produk, ukuran kg, merek sumber, jenis kantong)
KEMASAN = [('Kemasan Contoh', 5, 'Contoh Bravo', '5kg_kembangbmw'), ('Kemasan Contoh', 10, 'Contoh Ceri', '10kg_kembangbmw'),
           ('Kemasan Contoh Wangi', 20, 'Contoh Elang', '20kg_kembangbmw'), ('Kemasan Contoh', 25, 'Contoh Dahlia', '25kg_kembang')]
HARGA_KANTONG = {'5kg_kembangbmw': 900, '10kg_kembangbmw': 1300, '20kg_kembangbmw': 2100, '25kg_kembang': 2400}
HARGA_PAPERBAG = {'paperbag5l': 305, 'paperbag10l': 395}
PEMASOK = ['PEMASOK CONTOH SATU', 'PEMASOK CONTOH DUA']
KARYAWAN = ['Karyawan Contoh Satu', 'Karyawan Contoh Dua']
SAKSI = ['Saksi Contoh']
RASIO_LITER = 0.82
EMAIL_OWNER = 'owner@tokoberasmiqbal.web.app'
# alasan putusan per tanggal yang diketik owner contoh di gladi (gerbang & ritual) dan di --periksa — kalimat karangan, ≥ 5 huruf
ALASAN_PUTUS = 'Lupa tutup hari, uang laci tidak dihitung (contoh gladi)'
ACARA_KB_MAKS = 900   # berita acara 'berjalan' = SATU dokumen Firestore (batas 1 MiB) — memuat rencana, saldo pembuka, putusan, potret tahun (Paket B)


def iso(d): return d.isoformat()


class Pembangkit:
    def __init__(self, benih=BENIH, varian='macet', skala=None):
        self.r = random.Random(benih); self.varian = varian
        self.skala = float((SKALA_TERKUNCI if varian == 'terkunci' else SKALA_BAWAAN) if skala is None else skala)
        self.ids = set(); self.D = {}
        self.stok = {m: 0.0 for m, _, _ in MEREK}; self.nilai = {m: 0.0 for m, _, _ in MEREK}   # kg & nilai (rata-rata tertimbang, seperti mesin)
        self.hpp_dasar = {m: h for m, h, _ in MEREK}
        self.kem = {(n, u): {'unit': 0, 'nilai': 0.0, 'dibuat': 0} for n, u, _, _ in KEMASAN}
        self.bahan = {j: 0 for j in list(HARGA_KANTONG) + list(HARGA_PAPERBAG)}
        self.piutang = {}      # nama -> [ [tanggal, sisa] ... ] FIFO
        self.kasbon = {k: 0 for k in KARYAWAN + ['Owner']}
        self.utang_owner = 0
        self.bon_terbuka = []  # [batch, tanggal bayar]
        self.hari_tanpa_tutup = []
        self.pelanggan = ['Pelanggan Contoh %02d' % i for i in range(1, 41)]
        self.lambat = set(self.pelanggan[:30])   # 30 nama jarang membayar → piutang menua (banyak kiriman saldo pembuka)

    # ---- id: milidetik WIB tanggal+jam (bentuk Date.now() sistem), unik; cadangkan id+1 untuk kantong literan ----
    def id(self, tgl, jam, cadang=False):
        hh, mm = [int(x) for x in jam.split(':')]
        n = int(datetime.datetime(tgl.year, tgl.month, tgl.day, hh, mm, tzinfo=WIB).timestamp() * 1000) + self.r.randint(0, 59999)
        while n in self.ids or (cadang and (n + 1) in self.ids): n += 7
        self.ids.add(n)
        if cadang: self.ids.add(n + 1)
        return n

    def tambah(self, koleksi, dok): self.D.setdefault(koleksi, []).append(dok); return dok

    def jam_acak(self, a=7, b=21):
        return '%02d:%02d' % (self.r.randint(a, b - 1), self.r.randint(0, 59))

    def hpp(self, m): return self.nilai[m] / self.stok[m] if self.stok[m] > 0.01 else self.hpp_dasar[m]

    def harga_kg(self, m): return int(round(self.hpp_dasar[m] * 1.065 / 100.0)) * 100

    def harga_liter(self, m): return int(math.ceil(self.hpp_dasar[m] * RASIO_LITER * 1.16 / 500.0)) * 500

    def harga_unit(self, n, u, m): return int(math.ceil((self.hpp_dasar[m] * u * 1.09 + HARGA_KANTONG[[k for k in KEMASAN if k[0] == n and k[1] == u][0][3]]) / 500.0)) * 500

    # ---- kedatangan ----
    def kedatangan(self, tgl, paksa=False):
        rendah = [m for m, _, _ in MEREK if self.stok[m] < (900 if m != 'Ketan Contoh' else 250)]
        if not rendah and not paksa: return
        if not rendah: rendah = [self.r.choice([m for m, _, _ in MEREK])]
        utang = self.r.random() < 0.35; pemasok = PEMASOK[0] if utang or self.r.random() < 0.5 else PEMASOK[1]
        jam = '%02d:%02d' % (self.r.randint(7, 10), self.r.randint(0, 59)); rows = []
        for i, m in enumerate(rendah):
            krg = self.r.randint(20, 40) if m != 'Ketan Contoh' else self.r.randint(4, 8)
            hk = int(round(self.hpp_dasar[m] * self.r.uniform(0.985, 1.02) / 100.0)) * 100
            rows.append({'id': str(i + 1), 'merk': m, 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': krg, 'totalKg': krg * 50, 'hargaPerKg': hk, 'subtotalHarga': krg * 50 * hk})
        nkrg = sum(x['jumlahKarung'] for x in rows); bongkar = nkrg * 2000
        b = self.tambah('batchMasuk', {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'pemasok': pemasok, 'caraBayar': 'utang' if utang else 'tunai', 'biayaBongkar': bongkar, 'merkList': rows})
        tot = sum(x['totalKg'] for x in rows)
        for x in rows:   # HPP per kg = harga + bagian bongkar (hitungHppMerkDalamBatch membagi bongkar sebanding kg)
            self.stok[x['merk']] += x['totalKg']; self.nilai[x['merk']] += x['subtotalHarga'] + bongkar * x['totalKg'] / tot
        if utang: self.bon_terbuka.append([b, tgl + datetime.timedelta(days=self.r.randint(18, 24))])

    def beli_bahan(self, tgl, koleksi, jenis, n, harga):
        jam = self.jam_acak(8, 12)
        self.tambah(koleksi, {'id': self.id(tgl, jam), 'tipe': 'beli', 'jenis': jenis, 'jumlah': n, 'hargaTotal': n * harga, 'hargaPerPcs': harga, 'tanggal': iso(tgl), 'jam': jam, 'catatan': 'Beli contoh'})
        self.bahan[jenis] += n

    # ---- adukan kemasan ----
    def adukan(self, tgl):
        for n, u, m, kantong in KEMASAN:
            k = self.kem[(n, u)]
            if k['unit'] >= 12: continue
            unit = 20 if u <= 10 else 10; kg = unit * u
            if self.stok[m] < kg + 300: continue
            if self.bahan[kantong] < unit: self.beli_bahan(tgl, 'stokBahanKemasan', kantong, 300, HARGA_KANTONG[kantong])
            jam = self.jam_acak(19, 21); hk = self.hpp(m); biaya = unit * HARGA_KANTONG[kantong]
            hpu = round(hk * u + HARGA_KANTONG[kantong], 4); pid = self.id(tgl, jam)
            self.tambah('produksiKemasan', {'id': pid, 'tanggal': iso(tgl), 'jam': jam, 'namaProduk': n, 'ukuranKemasan': u, 'jumlahUnit': unit, 'hppPerUnit': hpu, 'merkSumber': m, 'kgDipakai': kg,
                                            'biayaKemasan': biaya, 'upahRepacking': 0, 'hppSumberPerKgDipakai': round(hk, 4), 'kantongJenis': kantong, 'kantongJumlah': unit, 'batchProduksi': pid,
                                            'jumlahBaris': 1, 'barisKe': 1, 'sumberList': [{'merk': m, 'kg': kg}], 'sumberKemasanList': [], 'kgKemasanDipakai': 0, 'jadiKarungUtuh': False, 'merkTujuan': None})
            self.tambah('stokBahanKemasan', {'id': self.id(tgl, jam), 'tipe': 'pakai', 'jenis': kantong, 'jumlah': unit, 'hargaTotal': 0, 'tanggal': iso(tgl), 'jam': jam, 'catatan': 'Otomatis dari produksi id ' + str(pid)[:4]})
            self.bahan[kantong] -= unit
            self.nilai[m] -= hk * kg; self.stok[m] -= kg
            k['unit'] += unit; k['dibuat'] += unit; k['nilai'] += hpu * unit

    # ---- penjualan ----
    def cara(self, p_qris, p_kredit):
        x = self.r.random(); return 'QRIS' if x < p_qris else 'Kredit' if x < p_qris + p_kredit else 'Tunai'

    def pelanggan_kredit(self):
        return self.r.choice(self.pelanggan)

    def isi_bayar(self, d):
        if d['caraBayar'] == 'Tunai':
            uang = int(math.ceil(d['hargaTotal'] / 50000.0)) * 50000 if self.r.random() < 0.6 else d['hargaTotal']
            d['uangDiterima'] = uang; d['kembalian'] = uang - d['hargaTotal']
        if d['caraBayar'] == 'Kredit':
            d['namaPelanggan'] = self.pelanggan_kredit(); self.piutang.setdefault(d['namaPelanggan'], []).append([d['tanggal'], d['hargaTotal']])
        return d

    def jual_karung(self, tgl, jam):
        pilih = [m for m, _, _ in MEREK if self.stok[m] >= 50 + 150]
        if not pilih: return None
        m = self.r.choice(pilih); hk = self.hpp(m); harga = int(math.ceil(self.harga_kg(m) * 50 / 500.0)) * 500
        d = {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'jenis': 'karung', 'caraBayar': self.cara(0.07, 0.09), 'merkSumber': m, 'namaProduk': m + ' (karung utuh)',
             'totalKg': 50, 'beratKarungAcuan': 50, 'jumlahKarung': 1, 'hargaTotal': harga, 'hargaAsliSatuan': harga, 'hppTotalSaatJual': int(round(hk * 50)), 'namaPelanggan': ''}
        d['trxId'] = self.id(tgl, jam)
        self.stok[m] -= 50; self.nilai[m] -= hk * 50
        return self.isi_bayar(d)

    def jual_literan(self, tgl, jam, dari_darurat=None):
        pilih = [m for m, _, lit in MEREK if lit and self.stok[m] >= 60]
        if not pilih: return None
        m = self.r.choice(pilih); liter = self.r.choice([1, 1, 2, 2, 2, 3, 3, 5, 5, 5, 5, 10, 10]); kg = round(liter * RASIO_LITER, 2)
        # sepertiga nota literan memakai paper bag toko (dokumen 'pakai' id+1), sisanya wadah pembeli — perbandingan yang sama dengan cadangan toko
        kantong = ('paperbag5l' if liter <= 5 else 'paperbag10l') if self.r.random() < 0.35 else None
        if kantong and self.bahan[kantong] < 1: self.beli_bahan(tgl, 'stokBahanLiteran', kantong, 1000, HARGA_PAPERBAG[kantong])
        hk = self.hpp(m); hl = self.harga_liter(m); harga = liter * hl; biaya = HARGA_PAPERBAG[kantong] if kantong else 0
        sid = self.id(tgl, jam, cadang=True)
        d = {'id': sid, 'tanggal': iso(tgl), 'jam': jam, 'jenis': 'literan', 'caraBayar': 'Tunai' if dari_darurat else self.cara(0.015, 0.012), 'merkSumber': m, 'namaProduk': m,
             'jumlahLiter': liter, 'totalKg': kg, 'rasioPakai': RASIO_LITER, 'hargaTotal': harga, 'hargaAsliSatuan': hl, 'jumlahKemasanLiteranDipakai': 1 if kantong else 0,
             'biayaKemasanLiteran': biaya, 'hppTotalSaatJual': int(round(hk * kg)) + biaya, 'namaPelanggan': '', 'trxId': self.id(tgl, jam)}
        if kantong: d['kemasanLiteran'] = kantong
        if dari_darurat:
            d.update({'koreksiDari': dari_darurat['id'], 'rinciDari': dari_darurat['id'], 'asalDarurat': True, 'grupNota': dari_darurat['grupNota'],
                      'dirinciPada': datetime.datetime(tgl.year, tgl.month, tgl.day, 20, 30, tzinfo=WIB).astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                      'alasanKoreksi': 'Rincian dari kasir darurat (contoh)'})
        if kantong:
            self.tambah('stokBahanLiteran', {'id': sid + 1, 'tipe': 'pakai', 'jenis': kantong, 'jumlah': 1, 'hargaTotal': 0, 'tanggal': iso(tgl), 'jam': jam, 'catatan': 'Otomatis dari penjualan literan'})
            self.bahan[kantong] -= 1
        self.stok[m] -= kg; self.nilai[m] -= hk * kg
        return self.isi_bayar(d)

    def jual_kemasan(self, tgl, jam):
        pilih = [(n, u, m) for n, u, m, _ in KEMASAN if self.kem[(n, u)]['unit'] >= 1]
        if not pilih: return None
        n, u, m = self.r.choice(pilih); k = self.kem[(n, u)]; unit = 1 if self.r.random() < 0.8 else min(2, k['unit'])
        hpu = k['nilai'] / k['unit']; harga = unit * self.harga_unit(n, u, m)
        d = {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'jenis': 'kemasan', 'caraBayar': self.cara(0.02, 0.02), 'namaProduk': n, 'ukuranKemasan': u, 'jumlahUnit': unit,
             'totalKg': u * unit, 'hargaTotal': harga, 'hargaAsliSatuan': harga // unit, 'hppTotalSaatJual': int(round(hpu * unit)), 'namaPelanggan': '', 'trxId': self.id(tgl, jam)}
        k['unit'] -= unit; k['nilai'] -= hpu * unit
        return self.isi_bayar(d)

    def karcis_darurat(self, tgl, jam):
        """Karcis kasir darurat yang SUDAH dirinci jadi satu nota literan (bentuk rincian /baru/): karcis bertanda dikoreksiOleh, rinciannya nota biasa."""
        gid = self.id(tgl, jam)
        k = {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'jenis': 'kasir_darurat_nominal', 'caraBayar': 'Tunai', 'namaProduk': '(tidak tercatat — kasir darurat)',
             'namaPelanggan': '', 'grupNota': gid, 'hargaTotal': 0}
        r = self.jual_literan(tgl, jam, dari_darurat=k)
        if not r: self.ids.discard(k['id']); return []
        k['hargaTotal'] = r['hargaTotal']; k['dikoreksiOleh'] = r['id']; k['alasanKoreksi'] = 'Dirinci jadi 1 barang: Literan'
        return [k, r]

    def hari(self, tgl):
        hk = tgl.weekday(); f = (1.25 if hk in (5, 6) else 1.0) * self.skala
        self.kedatangan(tgl, paksa=(tgl == MULAI))
        if tgl == MULAI:
            for kantong, h in HARGA_KANTONG.items(): self.beli_bahan(tgl, 'stokBahanKemasan', kantong, 200, h)
            for kantong, h in HARGA_PAPERBAG.items(): self.beli_bahan(tgl, 'stokBahanLiteran', kantong, 1500, h)
            self.adukan(tgl)
        nota = []
        for _ in range(int(round(self.r.uniform(29, 37) * f))): nota.append(('literan', self.jam_acak()))
        for _ in range(int(round(self.r.uniform(5, 8) * f))): nota.append(('karung', self.jam_acak()))
        for _ in range(int(round(self.r.uniform(4, 7) * f))): nota.append(('kemasan', self.jam_acak()))
        for _ in range(int(round(self.r.uniform(5, 8) * f))): nota.append(('darurat', self.jam_acak()))
        nota.sort(key=lambda x: x[1]); jual = []
        for jenis, jam in nota:
            if jenis == 'darurat':
                for d in self.karcis_darurat(tgl, jam): jual.append(d)
                continue
            d = {'literan': self.jual_literan, 'karung': self.jual_karung, 'kemasan': self.jual_kemasan}[jenis](tgl, jam)
            if d: jual.append(d)
        # nota yang dibatalkan (tidak memotong stok — mesin menyaringnya); dibuat sesudah stok dikembalikan
        if self.r.random() < 0.55:
            jam = self.jam_acak(); m = self.r.choice([x for x, _, lit in MEREK if lit])
            jual.append({'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'jenis': 'literan', 'caraBayar': 'Tunai', 'merkSumber': m, 'namaProduk': m, 'jumlahLiter': 2,
                         'totalKg': round(2 * RASIO_LITER, 2), 'hargaTotal': 2 * self.harga_liter(m), 'hppTotalSaatJual': 0, 'namaPelanggan': '', 'dibatalkan': True,
                         'alasanKoreksi': 'Salah ketik — dibatalkan (contoh)'})
        for d in jual: self.tambah('penjualan', d)
        self.adukan(tgl)
        self.uang_harian(tgl)
        self.bayar_bon_pelanggan(tgl)
        self.bayar_pemasok(tgl)
        return [d for d in jual if not d.get('dibatalkan') and not d.get('dikoreksiOleh')]

    def uang_harian(self, tgl):
        for _ in range(self.r.randint(1, 3)):
            jam = self.jam_acak(8, 20); ket = self.r.choice(['Bensin antar (contoh)', 'Plastik & tali (contoh)', 'Makan siang (contoh)', 'Parkir (contoh)'])
            self.tambah('pengeluaranHarian', {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'kategori': 'toko', 'untuk': 'toko', 'dari': 'laci', 'keterangan': ket, 'nominal': self.r.randint(2, 16) * 5000})
        if self.r.random() < 0.3:
            jam = self.jam_acak(10, 20); self.tambah('pengeluaranHarian', {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'kategori': 'owner', 'keterangan': 'Ambil pribadi (contoh)', 'nominal': self.r.randint(4, 30) * 5000})
        if tgl.day in (5, 20):
            jam = self.jam_acak(10, 16); n = self.r.randint(10, 40) * 10000; self.utang_owner += n
            self.tambah('pengeluaranHarian', {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'kategori': 'tokoDompet', 'keterangan': 'Belanja toko dibayar dompet owner (contoh)', 'nominal': n})
        if tgl.day == 25 and self.utang_owner > 0:
            jam = self.jam_acak(18, 21); n = int(self.utang_owner * 0.6 / 1000) * 1000; self.utang_owner -= n
            self.tambah('utangOwnerMutasi', {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'tipe': 'bayar', 'dari': 'laci', 'nominal': n, 'catatan': 'Toko mengembalikan pinjaman owner (contoh)'})
        if tgl.weekday() == 4:
            for k in KARYAWAN:
                jam = self.jam_acak(12, 18); n = self.r.randint(5, 20) * 10000; self.kasbon[k] += n
                self.tambah('kasbonMutasi', {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'tipe': 'ambil', 'namaPegawai': k, 'nominal': n, 'dari': 'laci', 'catatan': 'Kasbon (contoh)'})
        if tgl.weekday() == 0:
            for k in KARYAWAN:
                if self.kasbon[k] <= 0: continue
                jam = self.jam_acak(12, 18); n = int(self.kasbon[k] * self.r.uniform(0.4, 0.9) / 1000) * 1000; self.kasbon[k] -= n
                self.tambah('kasbonMutasi', {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'tipe': 'bayar', 'namaPegawai': k, 'nominal': n, 'caraBayar': 'Tunai', 'catatan': 'Kembali (contoh)'})
        if tgl.day == 12:
            jam = self.jam_acak(10, 18); n = self.r.randint(5, 30) * 10000; self.kasbon['Owner'] += n
            self.tambah('kasbonMutasi', {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'tipe': 'ambil', 'namaPegawai': 'Owner', 'owner': True, 'nominal': n, 'dari': 'laci', 'catatan': 'Lain-lain (contoh)'})

    def bayar_bon_pelanggan(self, tgl):
        for nama in list(self.piutang):
            utang = [u for u in self.piutang[nama] if u[1] > 0.5]
            if not utang: continue
            p = 0.04 if nama in self.lambat else 0.35
            if self.r.random() > p: continue
            sisa = sum(u[1] for u in utang)
            n = sisa if nama not in self.lambat and self.r.random() < 0.7 else int(sisa * self.r.uniform(0.15, 0.5) / 1000) * 1000
            if n <= 0: continue
            jam = self.jam_acak(9, 20); bayar = n
            for u in utang:   # FIFO, sama dengan mesin (utang tertua dulu)
                a = min(bayar, u[1]); u[1] -= a; bayar -= a
                if bayar <= 0: break
            self.tambah('piutangMutasi', {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'tipe': 'bayar', 'namaPelanggan': nama, 'nominal': n, 'caraBayar': 'Tunai', 'dicatatDi': 'sistem', 'catatan': 'Cicil (contoh)'})

    def bayar_pemasok(self, tgl):
        for x in list(self.bon_terbuka):
            b, tbayar = x
            if tbayar != tgl: continue
            jam = self.jam_acak(10, 20); nilai = sum(r['subtotalHarga'] for r in b['merkList'])
            self.tambah('utangPemasokMutasi', {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'tipe': 'bayar', 'pemasok': b['pemasok'], 'nominal': nilai, 'bonId': str(b['id']),
                                                'bonTanggal': b['tanggal'], 'dari': 'laci', 'catatan': ''})
            self.bon_terbuka.remove(x)

    def tutup_hari(self, tgl, jual):
        omzet = sum(d['hargaTotal'] for d in jual); nota = len(set(str(d.get('grupNota') or d.get('trxId') or d['id']) for d in jual))
        sisih = int(round(omzet * 0.004 / 1000.0)) * 1000; jam = '%02d:%02d' % (21, self.r.randint(10, 50))
        laci = self.r.randint(15, 45) * 10000; brankas = self.r.randint(400, 900) * 10000; amplop = self.r.randint(10, 40) * 10000
        titik = {'laci': laci, 'rekening': self.r.randint(0, 20) * 100000, 'amplop': amplop, 'brankas': brankas}
        self.tambah('tutupHari', {'id': iso(tgl), 'tanggal': iso(tgl), 'jam': jam, 'omzet': omzet, 'jumlahTransaksi': len(jual), 'jumlahNota': nota, 'kasFisikLaci': laci,
                                  'kasFisikRekening': titik['rekening'], 'kasFisikBrankas': brankas, 'kasFisikAmplop': amplop, 'kasSeharusnya': laci, 'selisih': 0, 'selisihLaci': 0,
                                  'alasanSelisih': '', 'setoranOwner': 0, 'sisihJadi': sisih, 'sistemBaru': True, 'langkah': 'laci:beres rekening:beres sisi', 'dilewati': [],
                                  'dihitung': {'laci': True, 'rekening': True, 'amplop': True, 'brankas': True}, 'menggantung': {'rapikanKasir': 0, 'daruratBelumRinci': 0}, 'titik': titik})
        self.tambah('setoranKas', {'id': 'st-' + iso(tgl), 'tanggal': iso(tgl), 'jam': jam, 'catatan': 'Tutup hari', 'nominal': 0})
        self.tambah('modalOwner', {'id': 'mo-st-' + iso(tgl), 'tanggal': iso(tgl), 'jam': jam, 'tipe': 'tarik', 'nominal': 0, 'dariSetoran': 'st-' + iso(tgl), 'catatan': 'Setoran tutup hari'})
        if sisih > 0: self.tambah('amplopLaba', {'id': 'am-' + iso(tgl), 'tanggal': iso(tgl), 'jam': jam, 'tipe': 'setor', 'nominal': sisih, 'catatan': 'Sisihan tutup hari'})
        return titik

    def pilih_hari_macet(self, hari_jual):
        if self.varian not in ('macet', 'terkunci'): return set()   # terkunci = data macet yang sama (benih & urutan acak sama)
        out = set()
        for bln, n in POLA_MACET:
            calon = [d for d in hari_jual if d.month == bln and d != AKHIR]
            out |= set(self.r.sample(calon, n))
        return out

    def bangun(self):
        hari = [MULAI + datetime.timedelta(days=i) for i in range((AKHIR - MULAI).days + 1)]
        # bon pemasok sebelum sistem (saldoAwal, bonTanggal = tanggal bonnya) + sebagian dibayar
        self.tambah('utangPemasokMutasi', {'id': self.id(MULAI, '08:00'), 'tanggal': iso(MULAI), 'jam': '08:00', 'tipe': 'saldoAwal', 'pemasok': PEMASOK[0], 'nominal': 6400000,
                                           'bonTanggal': '2026-07-31', 'catatan': 'Bon sebelum sistem (contoh)'})
        macet = self.pilih_hari_macet(hari); titik_akhir = None
        for tgl in hari:
            jual = self.hari(tgl)
            if tgl == datetime.date(2026, 9, 3):
                jam = '19:00'; self.tambah('utangPemasokMutasi', {'id': self.id(tgl, jam), 'tanggal': iso(tgl), 'jam': jam, 'tipe': 'bayar', 'pemasok': PEMASOK[0], 'nominal': 2400000,
                                                                  'bonId': str(self.D['utangPemasokMutasi'][0]['id']), 'bonTanggal': '2026-07-31', 'dari': 'laci', 'catatan': 'Cicil bon lama (contoh)'})
            if jual and tgl in macet: self.hari_tanpa_tutup.append(iso(tgl)); continue
            titik_akhir = self.tutup_hari(tgl, jual)
        self.lain_lain(titik_akhir)
        if self.varian == 'terkunci': self.kunci_semua()
        return self.cadangan()

    def kunci_semua(self):
        """varian terkunci: kunci periode sampai Desember 2026 (dikunci owner contoh 4 Jan 2027, sah: lewat tenggang) + dua pindahan uang laci ↔ brankas
        bertanggal bulan terkunci (saling meniadakan; pindahUang TIDAK diarsip tutup buku dan TIDAK berpintu — wajib utuh selama ritual). Dibuat PALING AKHIR:
        isi lain sama persis dengan varian macet."""
        self.tambah('aturanToko', {'id': 'kunciPeriode', 'sampaiBulan': KUNCI_PINTU, 'riwayat': [{'aksi': 'kunci', 'bulan': KUNCI_PINTU, 'pada': '2027-01-04T03:00:00.000Z',
                                                                                                    'olehUid': 'uid-owner-contoh', 'oleh': 'Owner'}]})
        for tgl, dari, ke in ((datetime.date(2026, 10, 15), 'laci', 'brankas'), (datetime.date(2026, 11, 20), 'brankas', 'laci')):
            self.tambah('pindahUang', {'id': self.id(tgl, '21:30'), 'tanggal': iso(tgl), 'jam': '21:30', 'dari': dari, 'ke': ke, 'nominal': 100000,
                                       'alasan': 'pindahan contoh (tidak diarsip)', 'biayaAdmin': 0, 'adminNama': ''})

    def lain_lain(self, titik):
        D = self.D; r = self.r
        # titik kas = hitungan tutup hari 31 Des (patokan uang per tempat untuk 31 Des)
        D.setdefault('pengaturan', []).append(dict({'id': 'titikKas', 'tanggal': iso(AKHIR), 'diubahPada': '2026-12-31T14:40:00.000Z'}, **titik))
        D.setdefault('aturanToko', []).extend([
            {'id': 'tutupBuku', 'tanggal': '2026-12-01', 'jam': '10:00', 'saksi': SAKSI},
            {'id': 'upah', 'tanggal': '2026-08-08', 'jam': '08:00', 'tarif': 60000, 'orang': [{'nama': k, 'status': 'aktif', 'masuk': '2026-08-08'} for k in KARYAWAN]}])
        for m, _, lit in MEREK:
            D.setdefault('katalogHargaKarung', []).append({'id': m, 'merk': m, 'hargaPerKg': self.harga_kg(m)})
            if lit: D.setdefault('katalogHargaLiteran', []).append({'id': m, 'merk': m, 'hargaPerLiter': self.harga_liter(m)})
        for n, u, m, _ in KEMASAN:
            D.setdefault('katalogHargaKemasan', []).append({'id': re.sub(r'[^a-z0-9]+', '_', n.lower()) + '_%dkg' % u, 'merk': n, 'ukuran': u, 'hargaPerUnit': self.harga_unit(n, u, m)})
        for nama in self.pelanggan: D.setdefault('pelangganCatatan', []).append({'id': self.id(MULAI, '09:00'), 'nama': nama, 'catatan': 'Pelanggan contoh'})
        for bln in ['2026-08', '2026-09', '2026-10', '2026-11', '2026-12']:
            D.setdefault('biayaBulanan', []).append({'id': bln, 'bulan': bln, 'listrik': r.randint(18, 26) * 10000, 'internet': 250000, 'akses': 20000, 'keamanan': 15000,
                                                     'tanggalBayarPos': {'listrik': bln + '-10', 'internet': bln + '-05', 'akses': bln + '-28', 'keamanan': bln + '-05'},
                                                     'dariPos': {'listrik': 'laci', 'internet': 'laci', 'akses': 'laci', 'keamanan': 'laci'}, 'gaji': 0, 'gajiHariOrang': 0, 'rincianGaji': []})
            for k in KARYAWAN:
                D.setdefault('absenKaryawan', []).append({'id': k.lower() + '|' + bln, 'nama': k, 'bulan': bln, 'hari': {}})
        # denyut perangkat lama (bukan perangkat gladi): terakhir ±1,5 jam sebelum LATIHAN → gerbang g3 tidak berbunyi
        for i, (nm, apl) in enumerate([('HP penjaga contoh', 'darurat'), ('Tablet contoh', 'baru'), ('Mac contoh', 'baru')]):
            D.setdefault('perangkatStatus', []).append({'id': 'p-contoh-%d' % (i + 1), 'nama': nm, 'akun': EMAIL_OWNER if apl == 'baru' else 'kasir@tokoberasmiqbal.web.app',
                                                        'aplikasi': apl, 'pada': '2026-12-31T1%d:05:00.000Z' % (1 + i), 'antrean': 0, 'gagal': 0, 'versi': apl})
        for i in range(260):
            t = datetime.datetime(2026, 12, 20, 8, 0, tzinfo=datetime.timezone.utc) + datetime.timedelta(minutes=55 * i)
            D.setdefault('logAktivitas', []).append({'id': int(t.timestamp() * 1000) + i, 'pada': t.strftime('%Y-%m-%dT%H:%M:%S.000Z'), 'aksi': 'tulis', 'koleksi': 'penjualan',
                                                     'idDok': str(1798000000000 + i), 'oleh': 'Owner', 'olehUid': 'uid-owner-contoh', 'perangkat': 'p-contoh-3', 'ringkas': 'nota contoh'})
        for w in range(21):
            tgl = MULAI + datetime.timedelta(days=7 * w)
            D.setdefault('cadanganCatatan', []).append({'id': self.id(tgl, '22:00'), 'tanggal': iso(tgl), 'jam': '22:00', 'nama': 'backup-batch-contoh-' + iso(tgl), 'jenis': 'manual',
                                                        'versi': 5, 'ok': True, 'koleksi': 54, 'dokumen': 0, 'ukuranKb': 0, 'era': None})

    def cadangan(self):
        out = {'versi': 5, 'diunduhPada': '2026-12-31T14:45:00.000Z', 'sumber': 'gladi · DATA CONTOH SINTETIS (bukan data toko)', 'eraTutupBuku': None}
        for k in sorted(self.D): out[k] = sorted(self.D[k], key=lambda d: str(d['id']))
        n = sum(len(v) for v in self.D.values())
        out['gladi'] = {'varian': self.varian, 'benih': BENIH, 'skala': self.skala, 'dokumen': n, 'hariTanpaTutup': sorted(self.hari_tanpa_tutup),
                        'perKoleksi': {k: len(v) for k, v in sorted(self.D.items())}, 'saksi': SAKSI, 'jamLatihan': JAM_LATIHAN, 'jamSungguhan': JAM_SUNGGUHAN}
        if self.varian == 'terkunci': out['gladi'].update(jamPintu=JAM_PINTU, kunci=KUNCI_PINTU)
        return out


def bangun(varian='macet', benih=BENIH, skala=None):
    return Pembangkit(benih, varian, skala).bangun()


# ======================= PERIKSA: data dinilai LOGIKA /baru/ ASLI (bundel jsc / node) =======================
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
SKENARIO_PERIKSA = r"""
var out = { koleksi: {} };
KOLEKSI.forEach(function (k) { pasok(k.nama, DATA[k.nama] || []); });
Object.keys(DATA).forEach(function (n) { if (Array.isArray(DATA[n])) out.koleksi[n] = DATA[n].length; });
var L = { antre: [], menunggu: 0, offline: false, idPerangkat: PERANGKAT };
function minus() {
  var m = [], sk = hitungStokKarungPerMerk(), km = hitungStokKemasan(), bk = hitungStokBahanKemasan(), bl = hitungStokBahanLiteran();
  Object.keys(sk).forEach(function (k) { if (sk[k].sisaKg < -0.01) m.push('karung ' + k + ' ' + sk[k].sisaKg); });
  Object.keys(km).forEach(function (k) { if (km[k].sisaUnit < 0) m.push('kemasan ' + k + ' ' + km[k].sisaUnit); });
  Object.keys(bk).forEach(function (k) { if (bk[k].sisaPcs < 0) m.push('kantong ' + k + ' ' + bk[k].sisaPcs); });
  Object.keys(bl).forEach(function (k) { if (bl[k].sisaPcs < 0) m.push('paper bag ' + k + ' ' + bl[k].sisaPcs); });
  return m;
}
function nilai(iso) {
  __KINI = new Date(iso).getTime(); var kini = new Date(__KINI);
  var T = tahunBuku(kini); var G = gerbangBuku(T.tahun, kini, L, {}); var SB = barisTahun(T.tahun);
  var P = pembukaBuku(T.tahun, { idUnik: function () { return 0; } }); var B = bandingBuku(SB, sesudahDariPembuka(P, SB));
  return { tahun: T.tahun, bolehSungguhan: T.bolehSungguhan, gerbang: G.daftar.map(function (g) { return { id: g.id, ok: g.ok, ket: g.ket }; }), belumTutup: G.belumTutup,
    semuaSama: B.semuaSama, ringkas: B.ringkas, beda: B.beda.map(function (b) { return b.nama; }), kasAda: SB.kasAda, nPembuka: P.dokumen.length, nArsip: arsipBuku(T.tahun).n,
    baris: B.baris.map(function (b) { return { id: b.id, a: b.a, b: b.b, tanda: b.tanda }; }), lebih: SB.lebih ? SB.lebih.n : 0, tekor: hitungUtangPemasok('2026-12-31').filter(function (x) { return x.tekor > 0; }).length };
}
out.minus = minus();
out.latihan = nilai(JAM_LATIHAN);
out.sungguhan = nilai(JAM_SUNGGUHAN);
var n0 = 50000; var W = { tanggal: '2027-01-01', jam: '15:30', kini: new Date(JAM_SUNGGUHAN).toISOString(), idUnik: function () { n0 += 1; return n0; } };
function gladiKunci() {
  var R = susunKunci(2026, { paraf: { owner: true, saksi: true }, saksi: SAKSI[0], langkah: {} }, W, { idPerangkat: PERANGKAT, namaPerangkat: 'Runner gladi' });
  return R.tolak ? { tolak: R.tolak } : { kiriman: R.kiriman.length, get: R.kiriman.map(function (k) { return k.get; }), dokumen: R.dokumen.length, arsip: R.arsip.length,
    berjalanPertama: R.kiriman.length > 1 && R.kiriman[0].dokumen[0].koleksi === 'tutupBukuAcara' && R.kiriman[0].dokumen[0].data.status === 'berjalan',
    putusanDiAcara: (R.acara.putusanHari || []).filter(function (h) { return h.alasan; }).length,
    // dokumen berita acara 'berjalan' (rencana + saldo pembuka + putusan + potret Paket B) — satu dokumen Firestore, batas 1 MiB
    acaraKb: Math.round(JSON.stringify(R.kiriman[0].dokumen.filter(function (x) { return x.koleksi === 'tutupBukuAcara'; })[0].data).length / 1024),
    potret: R.acara.potret ? { bulan: Object.keys(R.acara.potret.bulan || {}).length, hari: Object.keys(R.acara.potret.hari || {}).length } : null,
    koleksiPerKiriman: R.kiriman.map(function (k) { var o = {}; k.dokumen.forEach(function (x) { o[x.koleksi] = (o[x.koleksi] || 0) + 1; }); return o; }) };
}
out.kunci = gladiKunci();
// Paket A (A1): hari tanpa tutup hari diputus per tanggal lewat logika /baru/ (susunPutusanHari = yang ditulis tombol "Simpan putusan"), lalu dinilai lagi
var gladiGP = gerbangBuku(2026, new Date(JAM_SUNGGUHAN), L, {});
if (gladiGP.belumPutus.length) {
  var gladiIsiP = {}; gladiGP.belumPutus.forEach(function (t) { gladiIsiP[t] = ALASAN_PUTUS; });
  var gladiRP = susunPutusanHari(gladiIsiP, W);
  if (gladiRP.tolak) out.putusan = { tolak: gladiRP.tolak };
  else {
    pasok('aturanToko', (DATA.aturanToko || []).concat(gladiRP.dokumen.map(function (x) { return x.data; })));
    out.putusan = { n: Object.keys(gladiRP.dokumen[0].data.hari).length, koleksi: gladiRP.dokumen.map(function (x) { return x.koleksi + '/' + x.data.id; }) };
    out.sungguhanPutus = nilai(JAM_SUNGGUHAN); out.kunciPutus = gladiKunci();
  }
}
print(JSON.stringify(out));
"""


SKENARIO_PERIKSA_PINTU = r"""
var out = { koleksi: {} };
KOLEKSI.forEach(function (k) { pasok(k.nama, DATA[k.nama] || []); });
Object.keys(DATA).forEach(function (n) { if (Array.isArray(DATA[n])) out.koleksi[n] = DATA[n].length; });
var L = { antre: [], menunggu: 0, offline: false, idPerangkat: PERANGKAT };
(function () {   // lingkup sendiri: nama pendek di bawah tidak bertabrakan dengan nama di bundel
__KINI = new Date(JAM_PINTU).getTime(); var kini = new Date(__KINI);
var T = tahunBuku(kini);
out.tahunBuku = { tahun: T.tahun, bolehSungguhan: T.bolehSungguhan, perluPintu: !!T.perluPintu, adaKunci: !!T.adaKunci, teks: T.teks };
var G = gerbangBuku(2026, kini, L, {});
out.gerbang = G.daftar.filter(function (g) { return !g.ok; }).map(function (g) { return g.id + ' ' + g.ket; }); out.belumPutus = G.belumPutus.length;
var n0 = 60000; var W = { tanggal: kpWib(kini).iso, jam: '15:30', kini: kini.toISOString(), idUnik: function () { n0 += 1; return n0; } };
var isiP = {}; G.belumPutus.forEach(function (t) { isiP[t] = ALASAN_PUTUS; });
var RP = susunPutusanHari(isiP, W);
if (RP.tolak) out.putusan = { tolak: RP.tolak };
else { pasok('aturanToko', (DATA.aturanToko || []).concat(RP.dokumen.map(function (x) { return x.data; }))); out.putusan = { n: Object.keys(RP.dokumen[0].data.hari).length }; }
var G2 = gerbangBuku(2026, kini, L, {}); out.gerbang2 = G2.daftar.filter(function (g) { return !g.ok; }).map(function (g) { return g.id + ' ' + g.ket; });
var SB = barisTahun(2026); var P = pembukaBuku(2026, { idUnik: function () { return 0; } }); var B = bandingBuku(SB, sesudahDariPembuka(P, SB));
out.semuaSama = B.semuaSama; out.ringkas = B.ringkas; out.nArsip = arsipBuku(2026).n; out.nPembuka = P.dokumen.length;
var R = susunKunci(2026, { paraf: { owner: true, saksi: true }, saksi: SAKSI[0], langkah: {} }, W, { idPerangkat: PERANGKAT, namaPerangkat: 'Runner gladi' });
if (R.tolak) out.kunci = { tolak: R.tolak };
else {
  var K = R.kiriman; var iP = -1, pintu = null, titik = null;
  K.forEach(function (k, i) { k.dokumen.forEach(function (x) { if (x.koleksi === 'pengaturan' && x.data.id === 'pintuBuku' && iP < 0) { iP = i; pintu = x.data; }
    if (x.koleksi === 'pengaturan' && x.data.id === 'titikKas') titik = x.data.tanggal; }); });
  out.kunci = { kiriman: K.length, get: K.map(function (k) { return k.get; }), arsip: R.arsip.length,
    pertamaAcaraSaja: K[0].dokumen.length === 1 && K[0].dokumen[0].koleksi === 'tutupBukuAcara' && K[0].dokumen[0].data.status === 'berjalan',
    pintuKe: iP, pintu: pintu ? { tahun: pintu.tahun, status: pintu.status, jam: Math.round((new Date(pintu.sampai).getTime() - __KINI) / 3600000) } : null, titik31: titik };
}
})();
out.minus = minus();
print(JSON.stringify(out));
"""


def nilai_pintu(data, bun=None):
    """varian terkunci di JAM_PINTU — logika /baru/ asli (jsc / node)."""
    i = SKENARIO_PERIKSA.index('function minus()'); j = SKENARIO_PERIKSA.index('function nilai(')
    js = ("var __KINI = new Date('" + JAM_PINTU + "').getTime(); Date.now = function () { return __KINI; };\n" + (bun or bundel_periksa())
          + '\nvar DATA = ' + json.dumps({k: v for k, v in data.items() if isinstance(v, list)}) + ';\nvar JAM_PINTU = ' + json.dumps(JAM_PINTU)
          + ', PERANGKAT = ' + json.dumps(PERANGKAT_GLADI) + ', SAKSI = ' + json.dumps(SAKSI) + ', ALASAN_PUTUS = ' + json.dumps(ALASAN_PUTUS) + ';\n'
          + SKENARIO_PERIKSA[i:j] + SKENARIO_PERIKSA_PINTU)
    return jalan_js(js)


def periksa_terkunci(data, bun=None):
    """varian terkunci → (hasil, [cacat]): tahun 2026 ditutup sungguhan LEWAT PINTU di JAM_PINTU — kiriman 1 berita acara sendirian, kiriman 2 pintu."""
    h, e = nilai_pintu(data, bun)
    if h is None: return None, [JATUH + ' saat menilai data contoh terkunci: ' + e]
    c = []; meta = data.get('gladi', {}); T = h['tahunBuku']; K = h.get('kunci') or {}
    n = sum(v for v in h['koleksi'].values()); n_macet = len(meta.get('hariTanpaTutup', []))
    if not (RENTANG_DOK_TERKUNCI[0] <= n <= RENTANG_DOK_TERKUNCI[1]): c.append('jumlah dokumen %d di luar rentang data terkunci %s' % (n, RENTANG_DOK_TERKUNCI))
    if h['minus']: c.append('stok minus: ' + ', '.join(h['minus'][:4]))
    if not (T['tahun'] == 2026 and T['bolehSungguhan'] and T['perluPintu'] and T['adaKunci']): c.append('5 Jan: tahun 2026 harus boleh ditutup sungguhan LEWAT PINTU (ada bulan terkunci): %s' % T)
    if [g.split(' ')[0] for g in h['gerbang']] != ['g1']: c.append('5 Jan sebelum putusan: gerbang yang belum beres harus hanya g1: %s' % h['gerbang'])
    if (h.get('putusan') or {}).get('n') != n_macet: c.append('putusan per tanggal untuk %d hari tidak jadi: %s' % (n_macet, h.get('putusan')))
    if h['gerbang2']: c.append('5 Jan sesudah putusan: masih ada gerbang yang belum beres: %s' % h['gerbang2'])
    if not h['semuaSama']: c.append('12 baris sebelum ≠ sesudah — ' + str(h['ringkas']))
    if K.get('tolak'): c.append('susunKunci 5 Jan ditolak: ' + K['tolak'])
    else:
        if not K.get('pertamaAcaraSaja'): c.append('kiriman 1 harus berita acara "berjalan" SENDIRIAN (server membaca berita acara SEBELUM kiriman yang membuka pintu): %s' % K)
        if K.get('pintuKe') != 1 or not K.get('pintu') or K['pintu']['tahun'] != 2026 or K['pintu']['status'] != 'berjalan' or not 0 < K['pintu']['jam'] <= 72:
            c.append('kiriman 2 harus membuka pintu tahun 2026 (berjalan, ≤ 72 jam): %s' % K)
        if any(g > 18 for g in K.get('get') or []): c.append('kiriman > 18 pemeriksaan: %s' % K.get('get'))
        if K.get('titik31') != '2026-12-31': c.append('titik kas 31 Des 2026 harus ikut kiriman (lewat pintu): %s' % K.get('titik31'))
        if K.get('arsip') != h['nArsip']: c.append('arsip susunKunci %s ≠ arsip langkah 3 %s' % (K.get('arsip'), h['nArsip']))
    pu = [x for x in data.get('pindahUang', []) if x['tanggal'][:7] <= meta.get('kunci', '')]
    if len(pu) != 2: c.append('varian terkunci harus memuat 2 pindahan uang bertanggal bulan terkunci (tidak diarsip): %d' % len(pu))
    h['latihan'] = {'nArsip': h['nArsip'], 'nPembuka': h['nPembuka']}   # bentuk ringkas()/laporan gladi (nArsip per varian)
    return h, c


def _modul():
    import uji_tutup_buku_bertahap
    return uji_tutup_buku_bertahap.MODUL


def bundel_periksa():
    import bundel_baru, uji_kunci_periode
    return uji_kunci_periode.satu_lingkup(bundel_baru.bundel(_modul()))


def jalan_js(js):
    """jsc (macOS) atau node (runner Linux — dibungkus vm.runInThisContext supaya `this` = global seperti jsc). → (stdout baris terakhir, galat)."""
    d = tempfile.mkdtemp(prefix='gladi-periksa-'); p = os.path.join(d, 'periksa.js')
    try:
        open(p, 'w', encoding='utf-8').write(js)
        env = dict(os.environ, TZ='Asia/Jakarta')
        if os.path.exists(JSC): cmd = [JSC, p]
        elif shutil.which('node'):
            cmd = ['node', '-e', "global.print = function () { console.log(Array.prototype.join.call(arguments, ' ')); };"
                   "require('vm').runInThisContext(require('fs').readFileSync(process.argv[1], 'utf8'), { filename: 'periksa.js' });", p]
        else: return None, 'tidak ada jsc maupun node di mesin ini'
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=600)
        out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
        if r.returncode != 0 or not out.startswith('{'): return None, (r.stderr or r.stdout)[-1500:]
        return json.loads(out), ''
    finally: shutil.rmtree(d, ignore_errors=True)


def nilai_data(data, bun=None):
    js = ("var __KINI = new Date('" + JAM_LATIHAN + "').getTime(); Date.now = function () { return __KINI; };\n" + (bun or bundel_periksa())
          + '\nvar DATA = ' + json.dumps({k: v for k, v in data.items() if isinstance(v, list)}) + ';\nvar JAM_LATIHAN = ' + json.dumps(JAM_LATIHAN)
          + ', JAM_SUNGGUHAN = ' + json.dumps(JAM_SUNGGUHAN) + ', PERANGKAT = ' + json.dumps(PERANGKAT_GLADI) + ', SAKSI = ' + json.dumps(SAKSI)
          + ', ALASAN_PUTUS = ' + json.dumps(ALASAN_PUTUS) + ';\n' + SKENARIO_PERIKSA)
    return jalan_js(js)


def periksa(data, varian, bun=None):
    """→ (hasil nilai_data, [cacat]). Tiap cacat = kalimat yang menyebut barisnya."""
    if varian == 'terkunci': return periksa_terkunci(data, bun)
    h, e = nilai_data(data, bun)
    if h is None: return None, [JATUH + ' saat menilai data contoh: ' + e]
    c = []; meta = data.get('gladi', {}); L, S, K = h['latihan'], h['sungguhan'], h['kunci']
    n = sum(v for v in h['koleksi'].values())
    if not (RENTANG_DOK[0] <= n <= RENTANG_DOK[1]): c.append('jumlah dokumen %d di luar skala toko %s' % (n, RENTANG_DOK))
    if h['minus']: c.append('stok minus: ' + ', '.join(h['minus'][:4]))
    if L['tahun'] != 2026 or L['bolehSungguhan']: c.append('31 Des: tahun %s, sungguhan %s (harus 2026, hanya latihan)' % (L['tahun'], L['bolehSungguhan']))
    if S['tahun'] != 2026 or not S['bolehSungguhan']: c.append('1 Jan: tahun %s, sungguhan %s (harus 2026, sungguhan boleh)' % (S['tahun'], S['bolehSungguhan']))
    for nama, X in (('31 Des', L), ('1 Jan', S)):
        if not X['kasAda']: c.append(nama + ': uang per tempat 31 Des tidak bisa dihitung (titik kas)')
        if not X['semuaSama']: c.append(nama + ': 12 baris sebelum ≠ sesudah — ' + X['ringkas'] + ' ' + ', '.join(X['beda']))
        if X['lebih']: c.append(nama + ': ada kelebihan bayar pelanggan (%d)' % X['lebih'])
        if X['tekor']: c.append(nama + ': ada kelebihan bayar ke pemasok (%d pemasok)' % X['tekor'])
        gagal = [g['id'] for g in X['gerbang'] if not g['ok']]
        harap = ['g1'] if varian == 'macet' else []
        if gagal != harap: c.append(nama + ': gerbang yang belum beres %s, harusnya %s (%s)' % (gagal, harap, '; '.join(g['id'] + ' ' + g['ket'] for g in X['gerbang'] if not g['ok'])))
        if varian == 'macet' and sorted(X['belumTutup']) != sorted(meta.get('hariTanpaTutup', [])):
            c.append(nama + ': hari tanpa tutup menurut gerbang (%d) ≠ yang dibuat pembangkit (%d)' % (len(X['belumTutup']), len(meta.get('hariTanpaTutup', []))))
    n_macet = len(meta.get('hariTanpaTutup', []))
    if varian == 'macet':
        if n_macet != sum(x[1] for x in POLA_MACET): c.append('varian macet harus %d hari tanpa tutup' % sum(x[1] for x in POLA_MACET))
        g1 = next((g for g in S['gerbang'] if g['id'] == 'g1'), {})
        if not str(g1.get('ket', '')).startswith('%d hari belum ditutup & belum diputus' % n_macet): c.append('1 Jan: kalimat g1 bukan "%d hari belum ditutup & belum diputus …": %s' % (n_macet, g1.get('ket')))
        # Paket A: tanpa putusan, susunKunci (pintu masuk, bukan hanya layar) WAJIB menolak karena g1
        if not K.get('tolak') or 'belum ditutup & belum diputus' not in K['tolak']: c.append('susunKunci 1 Jan TANPA putusan harus ditolak karena g1 ("belum ditutup & belum diputus"): %s' % (K.get('tolak') or K))
        P = h.get('putusan') or {}
        if P.get('tolak') or P.get('n') != n_macet: c.append('putusan per tanggal (susunPutusanHari) untuk %d hari tidak jadi: %s' % (n_macet, P))
        else:
            S2 = h['sungguhanPutus']; gagal2 = [g['id'] + ' ' + g['ket'] for g in S2['gerbang'] if not g['ok']]
            if gagal2: c.append('1 Jan sesudah putusan: masih ada gerbang yang belum beres: ' + '; '.join(gagal2))
            if not S2['semuaSama']: c.append('1 Jan sesudah putusan: 12 baris sebelum ≠ sesudah — ' + S2['ringkas'])
            c += cek_kunci(h.get('kunciPutus') or {}, L, 'sesudah putusan: ', n_macet)
    else:
        c += cek_kunci(K, L, '', 0)
    return h, c


def cek_kunci(K, L, awal, n_putus):
    """susunKunci 1 Jan yang JADI: bertahap, ≤ 18 pemeriksaan, titik potong gladi (bon pemasok bukan di kiriman pertama), arsip = langkah 3, putusan ikut berita acara."""
    c = []
    if K.get('tolak'): return [awal + 'susunKunci 1 Jan ditolak: ' + K['tolak']]
    if K['kiriman'] < 2 or not K['berjalanPertama']: c.append(awal + 'saldo pembuka harus BERTAHAP (≥ 2 kiriman, berita acara berjalan di kiriman pertama) supaya Lanjutkan/Batalkan teruji: %s' % K)
    if any(g > 18 for g in K['get']): c.append(awal + 'kiriman > 18 pemeriksaan: %s' % K['get'])
    # gladi memotong ritual dengan menolak saldo pembuka bon pemasok: kiriman PERTAMA (berita acara berjalan) harus lolos, jadi tanpa bon pemasok
    if not K['koleksiPerKiriman'] or 'utangPemasokMutasi' in K['koleksiPerKiriman'][0] or not any('utangPemasokMutasi' in x for x in K['koleksiPerKiriman'][1:]):
        c.append(awal + 'saldo pembuka bon pemasok harus di kiriman ke-2 atau sesudahnya (titik potong gladi): %s' % K['koleksiPerKiriman'])
    if K['arsip'] != L['nArsip']: c.append(awal + 'arsip susunKunci %d ≠ arsip langkah 3 %d' % (K['arsip'], L['nArsip']))
    if K.get('putusanDiAcara', 0) != n_putus: c.append(awal + 'berita acara memuat %s putusan hari, harusnya %d' % (K.get('putusanDiAcara'), n_putus))
    if not K.get('potret') or K['potret']['bulan'] != 12 or not K['potret']['hari']: c.append(awal + 'potret 2026 (Paket B) tidak utuh di berita acara: %s' % K.get('potret'))
    if (K.get('acaraKb') or 0) > ACARA_KB_MAKS: c.append(awal + 'berita acara "berjalan" %s KB — mendekati batas 1 MiB satu dokumen Firestore (maks gladi %d KB)' % (K.get('acaraKb'), ACARA_KB_MAKS))
    return c


def ringkas(h, data):
    meta = data.get('gladi', {}); K = h.get('kunciPutus') or h['kunci']; P = h.get('putusan') or {}
    if meta.get('varian') == 'terkunci':
        return ('terkunci · %d dokumen · kunci sampai %s · %d hari tanpa tutup (diputus) · 5 Jan: pintu dibuka di kiriman %s (%s jam) · arsip 2026 %d dokumen · saldo pembuka %d dalam %s kiriman (pemeriksaan %s) · titik kas %s'
                % (sum(h['koleksi'].values()), meta.get('kunci'), len(meta.get('hariTanpaTutup', [])), (K.get('pintuKe') or 0) + 1, (K.get('pintu') or {}).get('jam'), h['nArsip'],
                   h['nPembuka'], K.get('kiriman', '?'), K.get('get', '?'), K.get('titik31')))
    return ('%s · %d dokumen · %d hari tanpa tutup%s · arsip 2026 %d dokumen · saldo pembuka %d dokumen dalam %s kiriman (pemeriksaan %s) · berita acara %s KB · 12 baris %s'
            % (meta.get('varian'), sum(h['koleksi'].values()), len(meta.get('hariTanpaTutup', [])),
               (' (kunci ditolak g1; sesudah %d putusan per tanggal jadi)' % P['n']) if P.get('n') else '', h['latihan']['nArsip'], h['latihan']['nPembuka'],
               K.get('kiriman', '?'), K.get('get', '?'), K.get('acaraKb', '?'), 'sama persis' if h['latihan']['semuaSama'] else 'BEDA'))


JATUH = 'logika /baru/ jatuh'


def bunyi(cacat):
    """Kontrol BERBUNYI hanya karena cacat datanya: logika /baru/ yang jatuh (galat sintaks, penilai rusak) = DIAM, bukan bunyi."""
    return bool(cacat) and not any(x.startswith(JATUH) for x in cacat)


def rusak_data(data, jenis):
    d = json.loads(json.dumps(data)); P = d['penjualan']
    if jenis == 'stok minus':
        m = MEREK[0][0]; P.append({'id': 99, 'tanggal': '2026-12-30', 'jam': '10:00', 'jenis': 'karung', 'caraBayar': 'Tunai', 'merkSumber': m, 'totalKg': 99999, 'jumlahKarung': 2000,
                                   'beratKarungAcuan': 50, 'hargaTotal': 1, 'hppTotalSaatJual': 1})
    elif jenis == 'karcis belum dirinci':
        k = next(x for x in P if x.get('jenis') == 'kasir_darurat_nominal'); k.pop('dikoreksiOleh', None)
    elif jenis == 'satu tutup hari hilang':
        d['tutupHari'] = d['tutupHari'][1:]
    elif jenis == 'kelebihan bayar':
        nama = next(x['namaPelanggan'] for x in P if x.get('caraBayar') == 'Kredit')
        d['piutangMutasi'].append({'id': 98, 'tanggal': '2026-12-30', 'jam': '10:00', 'tipe': 'bayar', 'namaPelanggan': nama, 'nominal': 999999999, 'caraBayar': 'Tunai'})
    elif jenis == 'titik kas hilang':
        # patokan uang 31 Des = titik kas ATAU kolom titik tutup hari terakhir ≤ 31 Des (titikTahun) — keduanya dibuang
        d['pengaturan'] = [x for x in d['pengaturan'] if x['id'] != 'titikKas']
        for x in d['tutupHari']: x.pop('titik', None)
    elif jenis == 'perangkat lain berdenyut':
        d['perangkatStatus'][0]['pada'] = '2026-12-31T14:40:00.000Z'
    elif jenis == 'semua hari ditutup (meta macet basi)':
        hari = sorted(set(x['tanggal'] for x in P)); ada = set(x['tanggal'] for x in d['tutupHari'])
        d['tutupHari'] += [{'id': t, 'tanggal': t, 'jam': '21:00', 'omzet': 0} for t in hari if t not in ada]
    return d


if __name__ == '__main__':
    arg = sys.argv[1:]
    def opsi(nama, bawaan):
        return arg[arg.index(nama) + 1] if nama in arg else bawaan
    if '--periksa' in arg or '--kontrol' in arg:
        bun = bundel_periksa(); kode = 0
        D = {v: bangun(v) for v in ('macet', 'bersih', 'terkunci')}
        if '--kontrol' in arg:
            for jenis in ['stok minus', 'karcis belum dirinci', 'satu tutup hari hilang', 'kelebihan bayar', 'titik kas hilang', 'perangkat lain berdenyut']:
                _, c = periksa(rusak_data(D['bersih'], jenis), 'bersih', bun)
                b = bunyi(c); print(('BERBUNYI ' if b else 'DIAM!!   ') + 'kontrol · ' + jenis + ' → ' + (c[0][:150] if c else '-'))
                if not b: kode = 3
            _, c = periksa(rusak_data(D['macet'], 'semua hari ditutup (meta macet basi)'), 'macet', bun)
            b = bunyi(c); print(('BERBUNYI ' if b else 'DIAM!!   ') + 'kontrol · varian macet tanpa hari macet → ' + (c[0][:150] if c else '-'))
            if not b: kode = 3
            T0 = json.loads(json.dumps(D['terkunci'])); T0['aturanToko'] = [x for x in T0['aturanToko'] if x['id'] != 'kunciPeriode']
            _, c = periksa(T0, 'terkunci', bun)
            b = bunyi(c) and any('LEWAT PINTU' in x for x in c); print(('BERBUNYI ' if b else 'DIAM!!   ') + 'kontrol · varian terkunci tanpa dokumen kunci periode → ' + (c[0][:150] if c else '-'))
            if not b: kode = 3
            a, b = json.dumps(bangun('macet')), json.dumps(D['macet'])
            print(('BERBUNYI ' if a == b else 'DIAM!!   ') + 'kontrol · benih tetap: dua kali dibangun = byte sama' + ('' if a == b else ' (BEDA)'))
            if a != b: kode = 3
            sys.exit(kode)
        for v in ('macet', 'bersih', 'terkunci'):
            h, c = periksa(D[v], v, bun)
            if c: print('DATA CONTOH %s GAGAL:' % v); [print('   ✗ ' + x) for x in c]; kode = 2
            else: print('DATA CONTOH %s LULUS: %s' % (v, ringkas(h, D[v])))
        sys.exit(kode)
    data = bangun(opsi('--varian', 'macet'), int(opsi('--benih', BENIH)), float(opsi('--skala', 0)) or None)
    keluar = opsi('--keluar', '')
    teks = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    if keluar: open(keluar, 'w', encoding='utf-8').write(teks); print('data contoh %s: %d dokumen → %s' % (data['gladi']['varian'], data['gladi']['dokumen'], keluar))
    else: sys.stdout.write(teks)
