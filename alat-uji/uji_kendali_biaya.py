#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_kendali_biaya.py — putaran 38 (29 Sep 2026): KENDALI BIAYA (cost controlling) di Laporan › Biaya, logika baru/js/layar/kendali-biaya-logika.js.
  · JENIS: tiap catatan uang keluar toko/tokoDompet jatuh ke TEPAT SATU jenis (tanda MDR/bank → `untuk` karyawan → kata owner → kata bawaan → lain);
    Σ jenis harian = harianToko mesin; upah + tagihan tetap = jatahBulanan mesin; margin − Σ − hapus buku − susut = laba bersih mesin → MENUTUP. Yang tidak
    cocok kata TETAP dihitung di "Lain-lain" dan disebut "belum dipilah".
  · ANGGARAN owner (aturanToko/kendaliBiaya): tanpa anggaran lampu mati; jenis variabel bulan berjalan dibanding jatah sampai hari ke-N + perkiraan linear;
    jenis tetap dibanding anggaran sebulan; upah ditambah yang BELUM DIBAYAR (absen); lampu hijau/amber(≤ ambang)/merah. Acuan = median bulan lalu (terukur).
  · TITIK IMPAS = biaya di bawah margin ÷ rasio margin (omzet ber-HPP saja); "sampai hari ini" dari mesin rentang awal bulan → hari ini.
  · PEMICU per satuan vs bulan lalu; PARETO 80 %; PERINGATAN menunjuk layar; TREN 6 bulan; ATUR (validasi) & TAMBAH KATA (satu kata satu jenis).
KOTAK PASIR (ANGKA CONTOH, nama rekaan), jam dikunci 19 Sep 2026 10:00 WIB. Cadangan toko di _privat/ (asap): tiap bulan menutup ke mesin laba, dan
ASAP GLOBAL: omzet/laba/inti/neraca tiap bulan BYTE-SAMA dengan kode main (modul ini hanya membaca — tidak boleh menggeser angka lama).

    python3 alat-uji/uji_kendali_biaya.py            → N lulus · 0 gagal
    python3 alat-uji/uji_kendali_biaya.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_laporan_baru  # noqa: E402
import uji_wadah_bernama  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_laporan_baru.MODUL + ['baru/js/layar/kendali-biaya-logika.js']
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(id, tgl, jam, cara, merk, kg, harga, hpp, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': jam, 'caraBayar': cara, 'jenis': 'karung', 'merkSumber': merk, 'totalKg': kg, 'beratKarungAcuan': 50, 'jumlahKarung': kg / 50, 'hargaTotal': harga, 'hppTotalSaatJual': hpp, 'trxId': 't' + str(id)}
    d.update(k); return d


def keluar(id, tgl, ket, n, **k):
    d = {'id': id, 'kategori': 'toko', 'tanggal': tgl, 'jam': '09:00', 'keterangan': ket, 'nominal': n}; d.update(k); return d


# ---- ANGKA CONTOH. Sep (sampai 19 Sep): omzet ber-HPP 1.450.000 (j1 500.000 tunai · j2 700.000 QRIS · j4 250.000 tunai), HPP 1.345.500 → margin 104.500; k1 100.000 karcis TANPA modal.
#      Uang keluar Sep: bensin 20.000 (kata) · MDR 1.800 (tanda) · lakban 120.000 tokoDompet untuk toko (kata) · rokok 30.000 UNTUK KARYAWAN · admin BI-FAST 2.500 (tanda bank) ·
#      kebutuhan masak 45.000 (kata dapur) · kopi kapal api 25.000 (kata karyawan) · bayar pajak rumah 500.000 & sedekah 10.000 (BELUM DIPILAH) = 754.300 · owner 100.000 (bukan biaya).
#      Tagihan Sep: listrik 350.000 (10 Sep); internet BELUM (Agu 242.000). Gaji Sep: Pekerja A 600.000 kotor, 10 hari (18 Sep); absen 19 Sep = 1 hari → upah menggantung.
#      Hapus buku 50.000 · susut −7.000 · tarik modal 50.000 (bukan biaya) · kedatangan Sep 3.000 kg @14.000 bongkar 225.000 · beli kantong 100 lembar 39.500.
#      Agu: bensin 30.000 · masak 200.000 · plastik 68.000; tagihan listrik 350.000 + internet 242.000; gaji A 1.560.000 (26 hari); kedatangan 1.000 kg @13.000 bongkar 72.000. Jul: nota 650.000/600.000, masak 100.000. Jun: nota 600.000/560.000, masak 50.000 (awal buku = Jun).
KOTAK = {
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-08-20', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'utang', 'biayaBongkar': 72000,
                  'merkList': [{'id': 'b10', 'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 20, 'totalKg': 1000, 'hargaPerKg': 13000, 'subtotalHarga': 13000000}]},
                 {'id': 'b2', 'tanggal': '2026-09-10', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'utang', 'biayaBongkar': 225000,
                  'merkList': [{'id': 'b20', 'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 60, 'totalKg': 3000, 'hargaPerKg': 14000, 'subtotalHarga': 42000000}]}],
  'penjualan': [jual('a-1', '2026-06-25', '09:00', 'Tunai', 'Angsa', 50, 600000, 560000), jual('a0', '2026-07-25', '09:00', 'Tunai', 'Angsa', 50, 650000, 600000), jual('a1', '2026-08-25', '09:00', 'Tunai', 'Angsa', 50, 700000, 650000), jual('j1', '2026-09-16', '09:00', 'Tunai', 'Angsa', 35.7, 500000, 464100),
                jual('j2', '2026-09-17', '10:00', 'QRIS', 'Angsa', 50, 700000, 650000), jual('j4', '2026-09-19', '09:40', 'Tunai', 'Angsa', 17.8, 250000, 231400),
                {'id': 'k1', 'tanggal': '2026-09-18', 'jam': '11:00', 'caraBayar': 'Tunai', 'jenis': 'kasir_darurat_nominal', 'hargaTotal': 100000, 'trxId': 'tk1'}],
  'pengeluaranHarian': [keluar('h1', '2026-09-16', 'Bensin antar', 20000), {'id': 'h2', 'kategori': 'owner', 'tanggal': '2026-09-17', 'jam': '11:02', 'keterangan': 'Belanja dapur', 'nominal': 100000},
                        keluar('mdr-2026-09-17', '2026-09-17', 'Potongan QRIS (MDR)', 1800, untuk='toko', mdr=True, dari='rekening'),
                        {'id': 'h4', 'kategori': 'tokoDompet', 'untuk': 'toko', 'tanggal': '2026-09-11', 'jam': '14:00', 'keterangan': 'Beli lakban', 'nominal': 120000},
                        keluar('h5', '2026-09-12', 'Rokok', 30000, untuk='karyawan', dari='laci'), keluar('h6', '2026-09-14', 'Biaya admin BI-FAST — bayar bon', 2500, untuk='toko', dari='rekening', dariBayarBon='x'),
                        keluar('h8', '2026-09-13', 'Kebutuhan masak', 45000), keluar('h9', '2026-09-15', 'Kopi kapal api', 25000), keluar('h10', '2026-09-08', 'Bayar pajak rumah', 500000), keluar('h11', '2026-09-09', 'Sedekah', 10000),
                        keluar('h7', '2026-08-25', 'Bensin antar', 30000), keluar('h12', '2026-08-12', 'Kebutuhan masak', 200000), keluar('h13', '2026-08-14', 'Plastik polo 24', 68000), keluar('h14', '2026-07-20', 'Kebutuhan masak', 100000), keluar('h15', '2026-06-20', 'Kebutuhan masak', 50000)],
  'biayaBulanan': [{'id': '2026-08', 'bulan': '2026-08', 'listrik': 350000, 'internet': 242000, 'akses': 0, 'keamanan': 0, 'tanggalBayarPos': {'listrik': '2026-08-10', 'internet': '2026-08-21', 'gaji': '2026-08-31'},
                    'rincianGaji': [{'nama': 'Pekerja A', 'hari': 26, 'gaji': 1560000}], 'tanggalBayarGaji': {'Pekerja A': '2026-08-31'}, 'gaji': 1560000, 'gajiHariOrang': 26},
                   {'id': '2026-09', 'bulan': '2026-09', 'listrik': 350000, 'internet': 0, 'akses': 0, 'keamanan': 0, 'tanggalBayarPos': {'listrik': '2026-09-10'},
                    'rincianGaji': [{'nama': 'Pekerja A · 18 Sep 2026', 'hari': 10, 'gaji': 600000, 'orang': 'Pekerja A', 'dari': '2026-09-01', 'sampai': '2026-09-18', 'sistemBaru': True}], 'tanggalBayarGaji': {'Pekerja A · 18 Sep 2026': '2026-09-18'}, 'gaji': 600000, 'gajiHariOrang': 10}],
  'absenKaryawan': [{'id': 'pekerja a|2026-09', 'nama': 'Pekerja A', 'bulan': '2026-09', 'hari': {'2026-09-19': 1}}],
  'kasbonMutasi': [], 'piutangMutasi': [{'id': 801, 'tipe': 'hapusBuku', 'namaPelanggan': 'Pembeli Contoh', 'nominal': 50000, 'tanggal': '2026-09-15', 'jam': '09:00'}],
  'penyesuaianStok': [{'id': 'ps1', 'tanggal': '2026-09-13', 'jam': '20:00', 'merk': 'Angsa', 'kgSistem': 100, 'kgFisik': 99.5, 'selisihKg': -0.5, 'alasan': 'Cocokkan', 'nilaiRp': -7000, 'hppPerKgSaatOpname': 14000}],
  'stokBahanKemasan': [{'id': 'bk1', 'tanggal': '2026-09-05', 'jam': '10:00', 'tipe': 'beli', 'jenis': '5kg_kembangbmw', 'jumlah': 100, 'hargaTotal': 39500, 'hargaPerPcs': 395}],
  'modalOwner': [{'id': 'm1', 'tanggal': '2026-08-08', 'jam': '08:00', 'tipe': 'setor', 'nominal': 25000000, 'catatan': 'Tabungan pribadi'}, {'id': 'm2', 'tanggal': '2026-09-18', 'jam': '17:00', 'tipe': 'tarik', 'nominal': 50000, 'catatan': 'Tarik'}],
  'utangPemasokMutasi': [], 'utangOwnerMutasi': [], 'amplopLaba': [], 'pindahUang': [], 'tutupHari': [], 'setoranKas': [], 'slipUpah': [], 'persetujuan': [], 'aturanToko': [], 'pengaturan': [], 'stokBahanLiteran': [], 'retur': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
var KINI = new Date(Date.now()); var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 9000; return function () { n += 1; return n; }; })() };
var tulis = function (r) { if (r.tolak) throw new Error('DITOLAK: ' + r.tolak); if (r.hapus) terapkanKeCache(r.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (r.dokumen) terapkanKeCache(r.dokumen); return r; };
var brs = function (K, id) { return K.baris.find(function (b) { return b.id === id; }); }; var fW = function (W, id) { return W.find(function (w) { return w.id === id; }) || { tujuan: {}, tingkat: '', teks: '' }; };
var dekat = function (a, b) { return Math.abs(a - b) < 0.5; };
var LM = function (k) { return hitungLabaBersihRentang(k + '-01', akhirBulanIso(k)); };

// ==================== 1 · JENIS & MENUTUP ====================
var K = kendaliBulan('2026-09', KINI); var L9 = LM('2026-09');
ok('Sep menutup: Σ jenis harian = harianToko mesin (754.300); upah + tetap = jatahBulanan (600.000 + 350.000); margin − Σ − hapus − susut = laba bersih mesin', K.menutup && K.cocokHarian && K.cocokTetap && dekat(K.L.harianToko, 754300) && K.per.upah.n === 600000 && K.per.tetap.n === 350000 && dekat(K.per.upah.n + K.per.tetap.n, L9.jatahBulanan) && K.labaBersih === L9.labaBersih && dekat(K.margin - K.biayaToko - K.hapus - K.susut, K.labaBersih), J([K.menutup, K.per.upah.n, K.per.tetap.n, K.L.harianToko, K.labaBersih]));
ok('pemilahan Sep: angkut 20.000 (kata bensin) · keuangan 4.300 (2 tanda: MDR + admin bank) · karyawan 55.000 (untuk 30.000 + kata kopi 25.000) · bahan 120.000 (lakban, dompet owner) · dapur 45.000 · lain 510.000 (2 belum dipilah)', K.per.angkut.n === 20000 && K.per.keuangan.n === 4300 && K.per.keuangan.jumlah === 2 && K.per.karyawan.n === 55000 && K.per.bahan.n === 120000 && K.per.dapur.n === 45000 && K.per.lain.n === 510000 && K.nBelum === 2 && K.belumDipilah === 510000, J([K.per.angkut.n, K.per.keuangan.n, K.per.karyawan.n, K.per.bahan.n, K.per.dapur.n, K.per.lain.n, K.nBelum]));
ok('asal pemilahan tercatat: tanda 2 · untuk 1 · kata bawaan 4 · belum 2; catatan dompet owner bertanda; owner (prive) BUKAN biaya', K.dariKata.tanda === 2 && K.dariKata.untuk === 1 && K.dariKata.kataBawaan === 4 && K.dariKata.belum === 2 && K.per.bahan.catatan[0].dompet === true && K.baris.every(function (r) { return r.catatan.every(function (c) { return c.id !== 'h2'; }); }), J(K.dariKata));
ok('hapus buku 50.000 & susut 7.000 (positif = biaya) sebagai baris sendiri; semuaBiaya = biaya toko + hapus + susut = 1.761.300; tetap: listrik ada, internet/akses/keamanan tidak ada', brs(K, 'hapus').n === 50000 && brs(K, 'susut').n === 7000 && K.semuaBiaya === 1761300 && K.posSemua.filter(function (p) { return p.ada; }).length === 1 && K.posSemua.find(function (p) { return p.id === 'internet'; }).n === 0, J([K.semuaBiaya, K.posSemua]));
ok('kg terjual 103,5 (35,7 + 50 + 17,8; karcis tanpa kg tidak ikut) & kg ber-HPP 103,5; karcis tanpa modal → cakupan 1.450.000 ÷ 1.550.000 = 93,5 %; per kg & % omzet tersedia', dekat(K.kgTerjual, 103.5) && dekat(K.kgHitung, 103.5) && Math.abs(K.cakupan - 1450000 / 1550000) < 1e-9 && K.biayaPerKg === Math.round(1761300 / 103.5) && K.pctBiaya === Math.round(1761300 / 1550000 * 1000) / 10 && brs(K, 'dapur').perKg === Math.round(45000 / 103.5), J([K.kgTerjual, K.cakupan, K.biayaPerKg, K.pctBiaya]));
ok('urutan baris = JENIS_BIAYA lalu hapus & susut; terjun dari margin kotor ke laba bersih menutup', K.baris.map(function (r) { return r.id; }).join() === 'upah,tetap,keuangan,karyawan,bahan,angkut,dapur,lain,hapus,susut' && dekat(K.terjun.reduce(function (a, t) { return t.kelas === 'jumlah' && t.nama === 'Laba bersih' ? a : t.nama === 'Margin kotor' ? a + t.n : a + t.n; }, 0), K.labaBersih), J(K.terjun));
var A0 = aturKendali();
ok('jenisCatatan: MDR bertanda → keuangan/tanda/mdr; "potongan mdr qris" TANPA tanda → keuangan lewat kata, mdr true; "rokok mang hasan" → karyawan kata roko; "Roti" → dapur; "x" → lain/belum; keterangan kosong → lain', jenisCatatan({ mdr: true, keterangan: 'apa saja' }, A0).id === 'keuangan' && jenisCatatan({ mdr: true, keterangan: 'apa saja' }, A0).mdr === true && jenisCatatan({ keterangan: 'potongan mdr qris' }, A0).id === 'keuangan' && jenisCatatan({ keterangan: 'potongan mdr qris' }, A0).mdr === true && jenisCatatan({ keterangan: 'Rokok — Mang Hasan' }, A0).id === 'karyawan' && jenisCatatan({ keterangan: 'Rokok — Mang Hasan' }, A0).kata === 'roko' && jenisCatatan({ keterangan: 'Roti' }, A0).id === 'dapur' && jenisCatatan({ keterangan: 'x' }, A0).dari === 'belum' && jenisCatatan({ keterangan: '' }, A0).id === 'lain');
ok('awalan di BATAS kata: "biaya admin bi-fast" kena "biaya admin"; "Donasi masjid" TIDAK kena "nasi" (bukan substring); "kebutuhan dapur" → dapur', jenisCatatan({ keterangan: 'biaya admin bi-fast' }, A0).id === 'keuangan' && jenisCatatan({ keterangan: 'Donasi masjid' }, A0).id === 'lain' && jenisCatatan({ keterangan: 'kebutuhan dapur' }, A0).id === 'dapur');

// ==================== 2 · KATA OWNER didahulukan, belum dipilah ====================
var BD0 = belumDipilah(K, 12);
ok('belum dipilah: 2 keterangan, terbesar dulu (Bayar pajak rumah 500.000, Sedekah 10.000)', BD0.length === 2 && BD0[0].kata === 'bayar pajak rumah' && BD0[0].n === 500000 && BD0[1].nama === 'Sedekah', J(BD0));
pasok('aturanToko', [{ id: 'kendaliBiaya', anggaran: {}, ambang: 10, ambangPemicu: 10, kata: { dapur: ['kopi'] } }]);
var Kk = kendaliBulan('2026-09', KINI);
ok('kata owner "kopi" di dapur MENANG atas kata bawaan karyawan: Kopi kapal api pindah ke dapur (kataOwner); karyawan 30.000; dapur 70.000; Σ harian TETAP; masih menutup', Kk.per.karyawan.n === 30000 && Kk.per.dapur.n === 70000 && Kk.per.dapur.catatan.some(function (c) { return c.dari === 'kataOwner'; }) && dekat(Kk.L.harianToko, 754300) && Kk.menutup && Kk.dariKata.kataOwner === 1, J([Kk.per.karyawan.n, Kk.per.dapur.n, Kk.dariKata]));
pasok('aturanToko', []);
ok('tambah kata: jenis lain/upah/tetap ditolak; kosong ditolak', /Jenis tidak dikenal/.test(susunTambahKata('lain', 'x', W).tolak) && /Jenis tidak dikenal/.test(susunTambahKata('upah', 'x', W).tolak) && /kosong/.test(susunTambahKata('bahan', '  — ', W).tolak));
var R1 = tulis(susunTambahKata('bahan', 'Bayar pajak rumah', W)); var K1 = kendaliBulan('2026-09', KINI);
ok('tambah kata "bayar pajak rumah" → bahan: dokumen aturanToko/kendaliBiaya {kata.bahan: [\"bayar pajak rumah\"]}, anggaran & ambang lama utuh; lain tinggal 10.000 (1 belum dipilah); bahan 620.000; kabar menyebut awalan', R1.dokumen[0].koleksi === 'aturanToko' && R1.dokumen[0].data.id === 'kendaliBiaya' && J(R1.dokumen[0].data.kata.bahan) === J(['bayar pajak rumah']) && R1.dokumen[0].data.ambang === 10 && K1.per.lain.n === 10000 && K1.nBelum === 1 && K1.per.bahan.n === 620000 && /diawali kata itu/.test(R1.patch.kabar) && R1.patch.pilahK === null, J([R1.dokumen[0].data, K1.per.lain.n, K1.per.bahan.n]));
ok('kata yang sama tidak boleh hidup di dua jenis; kata yang sudah ada di jenis itu ditolak dengan kalimat lain', /sudah dipakai Bahan pakai/.test(susunTambahKata('dapur', 'bayar pajak rumah', W).tolak) && /sudah jadi kata kunci/.test(susunTambahKata('bahan', 'Bayar Pajak Rumah', W).tolak));
pasok('aturanToko', []);

// ==================== 3 · ANGGARAN, LAMPU, PERKIRAAN, ACUAN, UPAH MENGGANTUNG ====================
ok('tanpa anggaran: semua lampu "tanpa", nLampu 0; jenis yang bisa dianggarkan berkata "anggaran belum diatur", lain & hapus "tidak dianggarkan"', K.baris.every(function (r) { return r.lampu === 'tanpa'; }) && K.nLampu === 0 && brs(K, 'dapur').lampuTeks === 'anggaran belum diatur' && brs(K, 'lain').lampuTeks === 'tidak dianggarkan' && brs(K, 'hapus').lampuTeks === 'tidak dianggarkan', J(K.baris.map(function (r) { return [r.id, r.lampuTeks]; })));
var U = upahMenggantung('2026-09', KINI); var HU = hitungUpah('Pekerja A', KINI, 'semua');
ok('upah menggantung Sep = hari absen sesudah gajian 18 Sep (19 Sep = 1 hari × tarif upah-logika), sama dengan hitungUpah; baris upah membawa menggantung & pakai = 600.000 + menggantung', U.nHari === 1 && U.total === HU.upah && U.total > 0 && U.orang[0].nama === 'Pekerja A' && brs(K, 'upah').menggantung === U.total && brs(K, 'upah').pakai === 600000 + U.total && /belum dibayar/.test(U.teks), J([U, HU.upah]));
ok('acuan TERUKUR = MEDIAN (bukan rata-rata): dapur Sep = median Jun 50.000 · Jul 100.000 · Agu 200.000 = 100.000 ("median 3 bulan lalu"; rata-rata 116.667); angkut = Agu 30.000 ("bulan lalu"); keuangan tidak punya acuan; Agu: dapur median Jun & Jul = 75.000', brs(K, 'dapur').acuan === 100000 && /median 3 bulan lalu/.test(brs(K, 'dapur').acuanTeks) && brs(K, 'angkut').acuan === 30000 && /^bulan lalu/.test(brs(K, 'angkut').acuanTeks) && brs(K, 'keuangan').acuan === null && brs(kendaliBulan('2026-08', KINI), 'dapur').acuan === 75000 && /median 2 bulan lalu/.test(brs(kendaliBulan('2026-08', KINI), 'dapur').acuanTeks) && K.sebelum.join() === '2026-08,2026-07,2026-06', J(K.baris.map(function (r) { return [r.id, r.acuan, r.acuanTeks]; })));
ok('perkiraan sebulan hanya jenis variabel bulan berjalan: dapur 45.000 ÷ 19 × 30 = 71.053; upah/tetap/susut null; Δ dapur vs Agu dari perkiraan (71.053 vs 200.000 = −64,5 %)', brs(K, 'dapur').proyeksi === 71053 && brs(K, 'upah').proyeksi === null && brs(K, 'susut').proyeksi === null && brs(K, 'dapur').deltaDari === 'perkiraan' && brs(K, 'dapur').delta === -64.5 && brs(K, 'dapur').nLalu === 200000, J([brs(K, 'dapur').proyeksi, brs(K, 'dapur').delta]));
ok('drafDariAcuan mengisi FORMULIR (string, ke ribuan) hanya jenis beracuan; bukan dokumen', (function () { var D = drafDariAcuan(K, { anggaran: { upah: '1' } }); return D.draf.anggaran.dapur === '100000' && D.draf.anggaran.angkut === '30000' && D.draf.anggaran.upah === '1560000' && D.draf.anggaran.keuangan === undefined && D.n === 5 && !D.dokumen; })(), J(drafDariAcuan(K, {})));
// atur: validasi
ok('atur ditolak: anggaran minus, terlalu besar, ambang 150, kata kembar antar jenis, kata > 40 huruf', /minus/.test(susunAturKendali({ anggaran: { dapur: '-1' } }, W).tolak) && /terlalu besar/.test(susunAturKendali({ anggaran: { dapur: '2.000.000.000' } }, W).tolak) && /0–100/.test(susunAturKendali({ ambang: '150' }, W).tolak) && /satu kata satu jenis/.test(susunAturKendali({ kata: { dapur: 'telur, kopi', karyawan: 'Kopi' } }, W).tolak) && /terlalu panjang/.test(susunAturKendali({ kata: { dapur: 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrs' } }, W).tolak));
var RA = tulis(susunAturKendali({ anggaran: { dapur: '70.000', karyawan: '40.000', bahan: '200.000', upah: '2.000.000', susut: '5.000', tetap: '' }, ambang: '10', ambangPemicu: '3', kata: { dapur: 'Telur, telur, GULA MERAH ', karyawan: '' } }, W)); var A1 = aturKendali();
ok('atur tersimpan: dokumen aturanToko/kendaliBiaya {anggaran angka, ambang 10, ambangPemicu 3, kata dapur ["telur","gula merah"] (polos, tanpa kembar)}; aturKendali membacanya; patch aturB null; kabar menyebut 5 anggaran', RA.dokumen[0].data.id === 'kendaliBiaya' && RA.dokumen[0].data.anggaran.dapur === 70000 && RA.dokumen[0].data.anggaran.tetap === 0 && RA.dokumen[0].data.ambangPemicu === 3 && J(RA.dokumen[0].data.kata.dapur) === J(['telur', 'gula merah']) && A1.anggaran.karyawan === 40000 && A1.nAnggaran === 5 && A1.dariOwner && RA.patch.aturB === null && /5 anggaran/.test(RA.patch.kabar), J([RA.dokumen[0].data, RA.patch]));
ok('tambah kata sesudah anggaran diatur: dokumen membawa anggaran, ambang & kata owner yang sudah ada (tidak menghapus)', (function () { var R = susunTambahKata('angkut', 'Ongkos becak', W); return R.dokumen[0].data.anggaran.dapur === 70000 && R.dokumen[0].data.anggaran.upah === 2000000 && R.dokumen[0].data.ambangPemicu === 3 && J(R.dokumen[0].data.kata.dapur) === J(['telur', 'gula merah']) && J(R.dokumen[0].data.kata.angkut) === J(['ongkos becak']); })());
var Ka = kendaliBulan('2026-09', KINI);
ok('lampu bulan berjalan (hari ke-19 dari 30): dapur jatah 70.000×19/30 = 44.333, aktual 45.000 → LEWAT 667 (1,5 %) ≤ ambang 10 → AMBER; karyawan jatah 25.333, aktual 55.000 → MERAH; bahan jatah 126.667, aktual 120.000 → HIJAU sisa 6.667', brs(Ka, 'dapur').lampu === 'amber' && brs(Ka, 'dapur').dasar === 44333 && brs(Ka, 'dapur').selisih === 667 && /jatah sampai hari ke-19/.test(brs(Ka, 'dapur').lampuTeks) && brs(Ka, 'karyawan').lampu === 'merah' && brs(Ka, 'karyawan').dasar === 25333 && brs(Ka, 'bahan').lampu === 'hijau' && brs(Ka, 'bahan').selisih === 120000 - 126667 && /sisa Rp6\.667/.test(brs(Ka, 'bahan').lampuTeks), J(Ka.baris.map(function (r) { return [r.id, r.lampu, r.dasar, r.selisih, r.lampuTeks]; })));
ok('jenis tetap dibanding anggaran SEBULAN: upah pakai (600.000 + menggantung) vs 2.000.000 → hijau, teks "anggaran"; susut 7.000 vs toleransi 5.000 → merah 40 %; ringkasan 2 merah · 1 amber · 2 hijau', brs(Ka, 'upah').lampu === 'hijau' && brs(Ka, 'upah').dasar === 2000000 && /^anggaran Rp2\.000\.000/.test(brs(Ka, 'upah').lampuTeks) && brs(Ka, 'susut').lampu === 'merah' && brs(Ka, 'susut').selisihPct === 40 && Ka.merah === 2 && Ka.amber === 1 && Ka.hijau === 2 && Ka.nLampu === 5, J([Ka.merah, Ka.amber, Ka.hijau]));
ok('bulan lampau (Agu) jenis variabel dibanding anggaran SEBULAN, bukan jatah harian: dapur 200.000 vs 70.000 → merah, dasar 70.000, tanpa perkiraan', (function () { var K8 = kendaliBulan('2026-08', KINI); return brs(K8, 'dapur').lampu === 'merah' && brs(K8, 'dapur').dasar === 70000 && brs(K8, 'dapur').proyeksi === null && !K8.berjalan; })());
pasok('aturanToko', [{ id: 'kunciPeriode', sampaiBulan: '2026-08', riwayat: [] }, RA.dokumen[0].data]);
ok('Agustus terkunci → final; Mei tanpa satu catatan → tanpaCatatan, menutup (nol = nol), tanpa peringatan tidak-menutup', kendaliBulan('2026-08', KINI).final && kendaliBulan('2026-05', KINI).tanpaCatatan && kendaliBulan('2026-05', KINI).menutup);
pasok('aturanToko', [RA.dokumen[0].data]);

// ==================== 4 · TITIK IMPAS ====================
var T = titikImpas(Ka, KINI); var Lj = hitungLabaBersihRentang('2026-09-01', '2026-09-19');
ok('titik impas: rasio = margin ÷ omzet ber-HPP (104.500 ÷ 1.450.000 = 7,2 %); omzet impas = semuaBiaya ÷ rasio; per hari = ÷ 30; omzet nyata/hari = 1.450.000 ÷ 19', Math.abs(T.rasio - 104500 / 1450000) < 1e-12 && T.rasioTeks === '7,2%' && T.omzetImpas === Math.round(1761300 / (104500 / 1450000)) && T.omzetImpasHari === Math.round(T.omzetImpas / 30) && T.omzetHari === Math.round(1450000 / 19), J([T.rasio, T.omzetImpas, T.omzetImpasHari, T.omzetHari]));
ok('sampai hari ini dari MESIN (1–19 Sep): laba bersih minus → belum menutup, kurang = −laba, omzet tambahan = kurang ÷ rasio, 11 hari tersisa; catatan menyebut nota tanpa modal & upah belum dibayar', !T.menutupKini && T.kurang === -Lj.labaBersih && T.omzetKurang === Math.round(T.kurang / T.rasio) && T.hariSisa === 11 && /omzet tambahan/.test(T.kiniTeks) && T.catatan.length === 2 && /1 nota tanpa modal/.test(T.catatan[0]) && /belum dibayar/.test(T.catatan[1]), J([T.kurang, Lj.labaBersih, T.kiniTeks, T.catatan]));
ok('bulan lampau dari bulan PENUH: Agu margin 50.000 < biaya → "TIDAK menutup", kurang = −laba bersih Agu, tanpa hari tersisa; rasio Agu = 50.000 ÷ 700.000', (function () { var T8 = titikImpas(kendaliBulan('2026-08', KINI), KINI); return !T8.menutupKini && /TIDAK menutup/.test(T8.kiniTeks) && Math.abs(T8.rasio - 50000 / 700000) < 1e-12 && T8.kurang === -LM('2026-08').labaBersih && T8.hariSisa === 0; })());
ok('tanpa omzet ber-HPP (Mei): rasio null, omzet impas null, kalimatnya jujur', titikImpas(kendaliBulan('2026-05', KINI), KINI).rasio === null && titikImpas(kendaliBulan('2026-05', KINI), KINI).omzetImpas === null && /tidak bisa dihitung/.test(titikImpas(kendaliBulan('2026-05', KINI), KINI).teks));

// ==================== 5 · PEMICU per satuan ====================
var P = pemicuBiaya(Ka);
var pm = function (id) { return P.baris.find(function (r) { return r.id === id; }); };
ok('pemicu Sep vs Agu: bongkar/kg 75 vs 72 (▲ 4,2 %, naik karena ambang pemicu 3); beli/kg 14.000 vs 13.000 (+7,7 %); kantong 395/lembar (Agu tidak ada → "bulan lalu belum ada"); MDR 1.800 ÷ QRIS 700.000 = 0,3 %', pm('bongkarKg').n === 75 && pm('bongkarKg').nLalu === 72 && pm('bongkarKg').delta === 4.2 && pm('bongkarKg').naik && pm('beliKg').n === 14000 && pm('beliKg').delta === 7.7 && pm('kantongLembar').n === 395 && pm('kantongLembar').nLalu === null && /belum ada/.test(pm('kantongLembar').deltaTeks) && pm('mdrQris').n === 0.3 && pm('mdrQris').teks === '0,3%', J(P.baris.map(function (r) { return [r.id, r.n, r.nLalu, r.delta, r.naik]; })));
// audit 39b no. 3: dokumen potongan tutup hari kini memuat potongan bayar bon QRIS → penyebut ikut uang QRIS bon (tarif tetap 0,3 %, bukan 0,7 %)
ok('39b-3 bayar bon QRIS 1.000.000 (18 Sep) + potongannya 3.000 di catatan MDR → (1.800 + 3.000) ÷ (700.000 + 1.000.000) = 0,3 %, bukan 4.800 ÷ 700.000 = 0,7 %', (function () { pasok('piutangMutasi', KOTAK.piutangMutasi.concat([{ id: 802, tipe: 'bayar', namaPelanggan: 'Pembeli Contoh', nominal: 1000000, tanggal: '2026-09-18', jam: '10:00', caraBayar: 'QRIS' }]));
  pasok('pengeluaranHarian', ambilPengeluaranHarian().concat([{ id: 'mdr-2026-09-18', kategori: 'toko', untuk: 'toko', tanggal: '2026-09-18', jam: '21:00', keterangan: 'Potongan QRIS (MDR) · 0 nota + 1 bayar bon · sebenarnya', nominal: 3000, dari: 'rekening', mdr: true }]));
  var r = pemicuBiaya(kendaliBulan('2026-09', KINI)).baris.find(function (x) { return x.id === 'mdrQris'; }); pasok('piutangMutasi', JSON.parse(J(KOTAK.piutangMutasi))); pasok('pengeluaranHarian', JSON.parse(J(KOTAK.pengeluaranHarian))); return r && r.n === 0.3 && /semua uang QRIS/.test(r.rumus || r.ket || J(r)); })(), J(pemicuBiaya(kendaliBulan('2026-09', KINI)).baris.find(function (x) { return x.id === 'mdrQris'; })));
ok('HPP/kg & jual/kg dari nota ber-HPP: Sep 1.345.500 ÷ 103,5 = 13.000 & 1.450.000 ÷ 103,5 = 14.009,7; margin/kg = selisihnya (1.009,7 vs Agu 1.000 → +1 %, tidak ditandai)', pm('hppKg').n === 13000 && pm('jualKg').n === Math.round(1450000 / 103.5 * 10) / 10 && Math.abs(pm('marginKg').n - (pm('jualKg').n - pm('hppKg').n)) < 0.2 && pm('marginKg').nLalu === 1000 && pm('marginKg').delta === 1 && pm('marginKg').naik === false && pm('jualKg').naik === false, J([pm('hppKg'), pm('jualKg'), pm('marginKg')]));
ok('arah dibalik untuk jual & margin per kg: nota 19 Sep 240.000 (bukan 250.000) → margin/kg 913 vs 1.000 = −8,7 % > ambang 3 → DITANDAI; jual/kg turun 0,6 % → tidak', (function () { pasok('penjualan', ambilPenjualanSemua().map(function (p) { return p.id === 'j4' ? Object.assign({}, p, { hargaTotal: 240000 }) : p; })); var Pt = pemicuBiaya(kendaliBulan('2026-09', KINI)); pasok('penjualan', JSON.parse(J(KOTAK.penjualan))); var m = Pt.baris.find(function (r) { return r.id === 'marginKg'; }), jl = Pt.baris.find(function (r) { return r.id === 'jualKg'; }); return m.n === Math.round(94500 / 103.5 * 10) / 10 && m.delta === -8.7 && m.naik === true && jl.delta === -0.6 && jl.naik === false; })());
ok('biaya karyawan per hari kerja = (upah dibayar + menggantung + di luar upah) ÷ (hari rincian gaji + hari menggantung): Sep (600.000 + U + 55.000) ÷ 11; Agu 1.560.000 ÷ 26 = 60.000', Math.abs(pm('karyawanHari').n - Math.round((600000 + U.total + 55000) / 11 * 10) / 10) < 0.11 && pm('karyawanHari').nLalu === 60000 && P.ini.hariKerja === 11 && P.lalu.hariKerja === 26, J([pm('karyawanHari'), P.ini.hariKerja]));
ok('biaya toko per kg terjual = biayaToko ÷ kg (1.704.300 ÷ 103,5); susut/kg 7.000 ÷ 103,5; ambang pemicu = setelan owner 3', pm('biayaKg').n === Math.round(1704300 / 103.5 * 10) / 10 && pm('susutKg').n === Math.round(7000 / 103.5 * 10) / 10 && P.ambang === 3 && P.keyLalu === '2026-08');

// ==================== 6 · PARETO ====================
var Pa = paretoBiaya(Ka);
ok('pareto Sep: urut turun; gaji 600.000 → pajak rumah 500.000 → listrik 350.000 = 82,3 % → inti 3 pos; kumulatif naik; total = semuaBiaya', Pa.total === 1761300 && /^Gaji Pekerja A/.test(Pa.daftar[0].nama) && Pa.daftar[1].nama === 'Bayar pajak rumah' && Pa.daftar[2].nama === 'Listrik' && Pa.nInti === 3 && Pa.inti[2].kumPct === 82.3 && Pa.daftar.every(function (x, i) { return i === 0 || x.n <= Pa.daftar[i - 1].n; }) && /3 dari .* pos membentuk 82,3%/.test(Pa.teks), J(Pa.daftar.map(function (x) { return [x.nama, x.jenis, x.n, x.kumPct, x.inti]; })));
ok('pengelompokan pareto lewat KATA yang cocok: "Kopi kapal api" (kata kopi) & "Rokok" (untuk) tetap dua pos; susut & hapus buku jadi pos sendiri', Pa.daftar.some(function (x) { return x.kunci === 'kopi' && x.n === 25000; }) && Pa.daftar.some(function (x) { return x.kunci === 'rokok' && x.n === 30000; }) && Pa.daftar.some(function (x) { return x.jenis === 'susut' && x.n === 7000; }) && Pa.daftar.some(function (x) { return x.jenis === 'hapus' && x.n === 50000; }));
ok('pareto Agu: dua catatan "Kebutuhan masak" & "masak" seketerangan menyatu lewat kata dapur', (function () { pasok('pengeluaranHarian', ambilPengeluaranHarian().concat([keluarBaru('h99', '2026-08-13', 'kebutuhan masak sayur', 15000)])); var P8 = paretoBiaya(kendaliBulan('2026-08', KINI)); var m = P8.daftar.find(function (x) { return x.kunci === 'kebutuhan masak'; }); pasok('pengeluaranHarian', ambilPengeluaranHarian().filter(function (h) { return h.id !== 'h99'; })); return m && m.n === 215000 && m.jumlah === 2; })());

// ==================== 7 · PERINGATAN ====================
var Wn = peringatanBiaya(Ka, P, T); var idW = Wn.map(function (w) { return w.id; });
ok('39b no. 25: peringatan jenis biaya yang tidak cocok kata kunci berbunyi "jenisnya belum dikenali" (bukan "belum dipilah" — itu tujuan toko/karyawan di Uang)', /jenisnya belum dikenali/.test((fW(Wn, 'belum-dipilah') || {}).teks || '') && !/dipilah/.test((fW(Wn, 'belum-dipilah') || {}).teks || ''), J(fW(Wn, 'belum-dipilah')));
ok('peringatan Sep (dengan anggaran): lampu merah karyawan & susut, amber dapur; internet belum dicatat (Agu 242.000); upah menggantung; belum dipilah (510.000 = 67,6 % harian); cakupan 93,5 % < 95 %; pemicu bongkar & beli (ambang 3); titik impas belum menutup', idW.indexOf('lampu-karyawan') >= 0 && idW.indexOf('lampu-susut') >= 0 && idW.indexOf('lampu-dapur') >= 0 && idW.indexOf('pos-internet') >= 0 && idW.indexOf('upah-gantung') >= 0 && idW.indexOf('belum-dipilah') >= 0 && idW.indexOf('cakupan') >= 0 && idW.indexOf('pemicu-bongkarKg') >= 0 && idW.indexOf('pemicu-beliKg') >= 0 && idW.indexOf('pemicu-marginKg') < 0 && idW.indexOf('impas') >= 0 && idW.indexOf('susut') < 0 && idW.indexOf('tidak-menutup') < 0, J(Wn.map(function (w) { return [w.tingkat, w.id]; })));
ok('urutan: awas dulu (merah, impas) baru info; tiap baris menunjuk pintu (lampu → Uang, susut → Stok › Cocokkan, pos → Uang › tagihan, pemicu beli → Stok › HPP, cakupan → Jual)', Wn.every(function (w, i) { return i === 0 || Wn[i - 1].tingkat !== 'info' || w.tingkat === 'info'; }) && fW(Wn, 'lampu-karyawan').tujuan.ke === 'uang' && fW(Wn, 'pos-internet').tujuan.tab === 'tagihan' && fW(Wn, 'pemicu-beliKg').tujuan.lembar === 'hpp' && fW(Wn, 'cakupan').tujuan.ke === 'jual' && fW(Wn, 'lampu-dapur').tingkat === 'info', J(Wn));
pasok('aturanToko', []);
var K0 = kendaliBulan('2026-09', KINI); var W0 = peringatanBiaya(K0, pemicuBiaya(K0), titikImpas(K0, KINI)); var id0 = W0.map(function (w) { return w.id; });
ok('tanpa anggaran: tidak ada peringatan lampu; susut 7.000 < 20 % margin → tidak dipaksa; pemicu ambang bawaan 10 → bongkar (+4,2 %) & beli (+7,7 %) tidak disebut', id0.every(function (i) { return i.indexOf('lampu-') !== 0; }) && id0.indexOf('susut') < 0 && id0.indexOf('pemicu-bongkarKg') < 0 && id0.indexOf('pemicu-beliKg') < 0 && id0.indexOf('impas') >= 0, J(id0));
pasok('penyesuaianStok', [{ id: 'ps2', tanggal: '2026-09-13', jam: '20:00', merk: 'Angsa', kgSistem: 100, kgFisik: 97, selisihKg: -3, alasan: 'Cocokkan', nilaiRp: -42000, hppPerKgSaatOpname: 14000 }]);
var Ks = kendaliBulan('2026-09', KINI); var Ws = peringatanBiaya(Ks, pemicuBiaya(Ks), titikImpas(Ks, KINI));
ok('susut 42.000 = 40,2 % margin → peringatan AWAS susut menunjuk Stok › Cocokkan; masih menutup', Ws.some(function (w) { return w.id === 'susut' && w.tingkat === 'awas' && w.tujuan.lembar === 'cocok' && /40,2%/.test(w.teks); }) && Ks.menutup && Ks.susut === 42000, J(Ws.map(function (w) { return [w.id, w.teks]; })));
pasok('penyesuaianStok', JSON.parse(J(KOTAK.penyesuaianStok)));

// ==================== 8 · TREN & pembantu ====================
var Tr = trenBiaya(KINI, 6);
ok('tren 6 bulan: Apr–Sep; Sep = kendaliBulan (semuaBiaya, margin); Jul: biaya 100.000, margin 50.000; Jun 50.000 & 40.000; Apr–Mei tanpaCatatan; maks ≥ semua; perJenis Sep dapur 45.000', Tr.daftar.map(function (b) { return b.key; }).join() === '2026-04,2026-05,2026-06,2026-07,2026-08,2026-09' && Tr.daftar[5].semuaBiaya === K0.semuaBiaya && Tr.daftar[5].margin === K0.margin && Tr.daftar[3].semuaBiaya === 100000 && Tr.daftar[3].margin === 50000 && Tr.daftar[2].semuaBiaya === 50000 && Tr.daftar[2].margin === 40000 && Tr.daftar[0].tanpaCatatan && Tr.daftar[1].tanpaCatatan && !Tr.daftar[2].tanpaCatatan && Tr.maks >= Tr.daftar[5].semuaBiaya && Tr.daftar[5].perJenis.find(function (x) { return x.id === 'dapur'; }).n === 45000 && Tr.ada, J(Tr.daftar.map(function (b) { return [b.key, b.tanpaCatatan, b.semuaBiaya, b.margin]; })));
ok('kbPctTeks: 12,3% · −5% · null → —; K.pct(a) dari omzet penuh', kbPctTeks(12.345) === '12,3%' && kbPctTeks(-5) === '−5%' && kbPctTeks(null) === '—' && K0.pct(155000) === '10%');
ok('drafAtur dari setelan: kosong = "" & ambang bawaan; sesudah atur berisi string anggaran & kata bergabung koma', drafAtur().anggaran.dapur === '' && drafAtur().ambang === '10' && (function () { pasok('aturanToko', [RA.dokumen[0].data]); var d = drafAtur(); pasok('aturanToko', []); return d.anggaran.dapur === '70000' && d.kata.dapur === 'telur, gula merah' && d.ambangPemicu === '3'; })());

// ==================== ASAP: cadangan toko ====================
var asap = null;
if (CADANGAN) {
  Object.keys(CADANGAN).forEach(function (n) { if (Array.isArray(CADANGAN[n])) pasok(n, CADANGAN[n]); });
  localStorage.removeItem('miqbal_titik_kas_v1'); var kini2 = new Date(Date.now()); var bulan = daftarBulan(kini2, 36); var salah = []; var tiap = [];
  bulan.forEach(function (b) { var Kb = kendaliBulan(b.key, kini2); var Lb = LM(b.key); var Tb = titikImpas(Kb, kini2); var Pb = pemicuBiaya(Kb); var Pab = paretoBiaya(Kb); var Wb = peringatanBiaya(Kb, Pb, Tb);
    var jenisHarian = JENIS_BIAYA.filter(function (j) { return j.sifat === 'variabel'; }).reduce(function (a, j) { return a + Kb.per[j.id].n; }, 0);
    var rasioOk = Tb.rasio === null ? Kb.omzetHitung === 0 : Math.abs(Tb.rasio - Lb.margin / Lb.omzetHitung) < 1e-12;
    var paretoOk = Pab.daftar.length === 0 || (Math.abs(Pab.total - (Kb.semuaBiaya - Kb.baris.filter(function (r) { return r.n < 0; }).reduce(function (a, r) { return a + r.n; }, 0))) < 1 && Pab.inti.length >= 1);
    if (!Kb.tanpaCatatan && (!Kb.menutup || !dekat(jenisHarian, Lb.harianToko) || Kb.labaBersih !== Lb.labaBersih || !rasioOk || !paretoOk)) salah.push(b.key + ':' + J([Kb.menutup, Kb.cocokHarian, Kb.cocokTetap, rasioOk, paretoOk]));
    tiap.push(b.key + ': ' + (Kb.tanpaCatatan ? 'tanpa catatan' : 'menutup · ' + Kb.baris.filter(function (r) { return r.n !== 0; }).length + ' jenis berisi · belum dipilah ' + Kb.nBelum + ' · lampu ' + Kb.nLampu + ' · peringatan ' + Wb.length + ' · pareto inti ' + Pab.nInti + '/' + Pab.nSemua + ' · ' + (Kb.final ? 'final' : 'draf'))); });
  var Trc = trenBiaya(kini2, 6);
  asap = { salah: salah, tiap: tiap, tren: Trc.daftar.map(function (b) { return b.key + (b.tanpaCatatan ? ' ·' : ' ✓'); }), aturOwner: aturKendali().dariOwner };
  ok('ASAP: kendali biaya tiap bulan menutup ke mesin laba (Σ jenis = harian, rasio impas = margin ÷ omzet ber-HPP, pareto total = biaya)', !salah.length, J(asap));
}
print(J({ lulus: lulus, gagal: gagal, asap: asap }));
"""
SKENARIO = SKENARIO.replace("keluarBaru(", "(function (id, tgl, ket, n) { return { id: id, kategori: 'toko', tanggal: tgl, jam: '09:00', keterangan: ket, nominal: n }; })(")


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def utama(js, pakai_cadangan):
    cad = 'null'; p = uji_wadah_bernama.cadangan_toko() if pakai_cadangan else None
    if p: cad = uji_wadah_bernama.cad_js(p)[0]
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CADANGAN = ' + cad + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    return h['lulus'], h['gagal'], h.get('asap')


def dua_nama(t):
    """39b no. 25 — layar Laporan: "belum dipilah" dulu berarti DUA hal (tujuan toko/karyawan kosong · jenis biaya tidak cocok kata kunci). Yang tampil kini
    "tanpa tujuan" (kartu laba kotor → ke mana) dan "jenisnya belum dikenali" (Kendali Biaya). Kembalikan daftar masalah."""
    out = []
    tampil = re.findall(r"'[^'\n]*'|`[^`]*`|>[^<>]*<", t)
    if any('belum dipilah' in x for x in tampil): out.append('laporan.js masih menampilkan "belum dipilah"')
    if 'jenisnya belum dikenali' not in t: out.append('Kendali Biaya tidak menyebut "jenisnya belum dikenali"')
    if 'tanpa tujuan toko / karyawan' not in t: out.append('kartu laba kotor → ke mana tidak menyebut "tanpa tujuan"')
    return out


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    lap = open(os.path.join(AKAR, 'baru', 'js', 'layar', 'laporan.js'), encoding='utf-8').read()
    if '--kontrol' in sys.argv:
        rusak = {
            'catatan lain-lain dibuang dari jumlah (tidak menutup)': js.replace("per[J.id].n += n; per[J.id].jumlah += 1;", "if (J.id !== 'lain') { per[J.id].n += n; per[J.id].jumlah += 1; }"),
            '39b-3: penyebut potongan QRIS hanya penjualan (bayar bon QRIS tak ikut)': js.replace("mdrQris: Ka.pos.qris + kbQrisLain(X) > 0 ? mdr / (Ka.pos.qris + kbQrisLain(X)) * 100 : null,", "mdrQris: Ka.pos.qris > 0 ? mdr / Ka.pos.qris * 100 : null,"),
            'kata owner tidak didahulukan dari kata bawaan': js.replace("const k = kbCocokKata(polos, A.kata[j.id] || []); if (k) return { id: j.id, dari: 'kataOwner', kata: k, kunci: k, mdr };", "void 0;"),
            'awalan kata tanpa batas kata (\"donasi\" kena \"nasi\")': js.replace("const t = ' ' + polos; for (const k of kata) { if (k && t.indexOf(' ' + k) >= 0) return k; } return '';", "for (const k of kata) { if (k && polos.indexOf(k) >= 0) return k; } return '';"),
            'kolom untuk=karyawan diabaikan': js.replace("if (ugUntukDok(h) === 'karyawan') return { id: 'karyawan', dari: 'untuk', kata: '', kunci: polos || '(tanpa keterangan)', mdr: false };", ""),
            'upah yang belum dibayar tidak ikut dibandingkan': js.replace("r.pakai = r.n + r.menggantung;", "r.pakai = r.n;"),
            'jenis variabel bulan berjalan dibanding anggaran sebulan, bukan jatah sampai hari ke-N': js.replace("r.dasar = K.berjalan && r.sifat === 'variabel' ? Math.round(r.anggaran * K.hariJalan / K.nHari) : r.anggaran;", "r.dasar = r.anggaran;"),
            'ambang amber diabaikan (semua lewat = merah)': js.replace("r.lampu = r.selisih <= 0 ? 'hijau' : r.selisihPct <= A.ambang ? 'amber' : 'merah';", "r.lampu = r.selisih <= 0 ? 'hijau' : 'merah';"),
            'acuan memakai bulan berjalan juga': js.replace(".filter((k) => k < key).slice(0, 3)", ".filter((k) => k <= key).slice(0, 3)"),
            'acuan = rata-rata, bukan median': js.replace("r.acuan = acuanArr.length ? kbMedian(acuanArr) : null;", "r.acuan = acuanArr.length ? Math.round(acuanArr.reduce((a, b) => a + b, 0) / acuanArr.length) : null;"),
            'perkiraan sebulan dipasang ke jenis tetap juga': js.replace("r.proyeksi = K.berjalan && r.sifat === 'variabel' && K.hariJalan > 0", "r.proyeksi = K.berjalan && K.hariJalan > 0"),
            'rasio impas dari omzet penuh (termasuk nota tanpa modal)': js.replace("const rasio = K.omzetHitung > 0 ? K.margin / K.omzetHitung : null;", "const rasio = K.omzet > 0 ? K.margin / K.omzet : null;"),
            'sampai hari ini dihitung dari bulan penuh, bukan mesin sampai hari ini': js.replace("const sampai = K.berjalan ? (iso < K.akhir ? iso : K.akhir) : K.akhir;", "const sampai = K.akhir;"),
            'tanda susut tertukar (stok berkurang dianggap mengurangi biaya)': js.replace("const susut = -(L.susutStok || 0); const hapus", "const susut = (L.susutStok || 0); const hapus"),
            'pareto tidak berhenti di 80 %': js.replace("inti: kum - x.n < total * batas / 100,", "inti: true,"),
            'pareto tidak mengelompokkan lewat kata': js.replace("const kunci = c.kunci || kbPolos(c.nama);", "const kunci = kbPolos(c.nama);"),
            'pemicu naik tidak pernah ditandai': js.replace("naik: delta !== null && ((naikBiaya && delta > A.ambangPemicu) || (turunBuruk && delta < -A.ambangPemicu)),", "naik: false,"),
            'biaya karyawan per hari tanpa upah menggantung': js.replace("const hk = kbHariKerja(X.key) + (U ? U.nHari : 0); const upahSemua = X.per.upah.n + (U ? U.total : 0);", "const hk = kbHariKerja(X.key); const upahSemua = X.per.upah.n;"),
            'peringatan pos tetap belum dicatat hilang': js.replace("if (K.berjalan) K.posSemua.forEach((p) => { const lalu = KL.posSemua.find((x) => x.id === p.id); if (!(p.n > 0) && lalu && lalu.n > 0)", "if (false) K.posSemua.forEach((p) => { const lalu = KL.posSemua.find((x) => x.id === p.id); if (!(p.n > 0) && lalu && lalu.n > 0)"),
            'peringatan cakupan hilang': js.replace("if (K.cakupan !== null && K.cakupan < 0.95) awas('cakupan',", "if (false) awas('cakupan',"),
            'kata kembar antar jenis diterima saat atur': js.replace("if (punya[k] && punya[k] !== j.id) return { tolak: '\"' + k + '\" ada di ' + punya[k] + ' DAN ' + j.id + ' — satu kata satu jenis' };", ""),
            'tambah kata menghapus anggaran yang sudah diatur': js.replace("data: { id: 'kendaliBiaya', tanggal: w.tanggal, jam: w.jam, anggaran: A.anggaran, ambang: A.ambang, ambangPemicu: A.ambangPemicu, kata }", "data: { id: 'kendaliBiaya', tanggal: w.tanggal, jam: w.jam, anggaran: {}, ambang: 10, ambangPemicu: 10, kata }"),
            'tambah kata ke jenis lain diterima': js.replace("const j = JENIS_BIAYA.find((x) => x.id === jenis && x.id !== 'upah' && x.id !== 'tetap' && x.id !== 'lain');", "const j = JENIS_BIAYA.find((x) => x.id === jenis);"),
            'tren: bulan tanpa catatan digambar sebagai nol': js.replace("tanpaCatatan: X.tanpaCatatan, omzet: X.omzet", "tanpaCatatan: false, omzet: X.omzet"),
        }
        kode = 0
        for nama, isi in [('39b-25 laporan.js kembali memakai "belum dipilah" untuk jenis yang belum dikenali', lap.replace('jenisnya belum dikenali</span>', 'belum dipilah</span>', 1))]:
            g = dua_nama(isi) if isi != lap else []
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g, _ = utama(isi, False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    g = g + ['39b-25: ' + x for x in dua_nama(lap)]; l = l + (0 if dua_nama(lap) else 1)
    print('KENDALI BIAYA (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    p = uji_wadah_bernama.cadangan_toko()
    if p and asap: print('ASAP DATA TOKO (%s): %s' % (os.path.basename(p), json.dumps(asap, ensure_ascii=False)[:1500]))
    if p:
        sama, ket = uji_wadah_bernama.asap_global(p)
        print('ASAP GLOBAL (kode main vs cabang, %s): %s' % (os.path.basename(p), ('BYTE-SAMA — ' + ket) if sama else ('GAGAL — ' + ket)))
        if sama is False: sys.exit(2)
    sys.exit(0 if not g else 2)
