#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_stok_p5.py — PAKET P5 · Stok, gudang & produksi (owner 27 Nov 2026; sensus ulang 27 Nov: A20 A43 A50 A56 A70 A92 A125 A127 B51 B72).
KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  A56   kartu stok per merek: gerak buku persis aturan mesin beku (kedatangan, nota, adukan & pindah buku, retur utuh, cocokkan, adukan jadi karung utuh) →
        sisa berjalan terakhir = buku mesin; buku yang lahir hanya dari adukan jadi karung tidak dipotong notanya (urutan mesin).
  A125  barang masuk hari itu: kedatangan + timbang & mutu, Σ = rekap timbang Stok; buku lahir bukan kedatangan; baris teks WA rekap harian.
  A127  hitung karung minggu itu (Senin–Minggu) vs kartu stok; timbang tutup hari & wadah tidak ikut; merek berisi yang belum dihitung.
  A70   dihitung oleh / didampingi di Cocokkan (boleh kosong; orang yang sama ditolak; kolom hanya bila diisi).
  A43   batas simpan kedua (bawaan 120 hari, wajib > ambang lambat laku) + hama per tumpukan (Cocokkan) → Umur, Tugas gudang, Dasbor.
  A92   opname kejutan: tanggal & merek diundi dari benih rahasia owner (tetap, tanpa tulis tiap bulan); selesai / terlewat; pengingat owner saja.
  A20   rencana beli bulan depan dari rata-rata pemakaian 3 bulan selesai (tanpa musim): turun/naik tajam = bulan terakhir; nama berhenti tidak diramal.
  B51   modal stok yang sudah dipesan pelanggan (pesanan belum jadi nota) × nilai buku; kurang di buku; pesanan tanpa barang disebut.
  B72   produksi per bulan = kemasRentang (Laporan › Pondasi) + per adukan susut %, sampel isi, oplos, lebih berat; rencana produksi = "aduk N unit" Stok › Gudang.
  A50   Adukan: timbang sampel isi (kurang isi ditandai), hasil lebih berat ditandai, OPLOS (bahan kelas HET lebih rendah dari label) DITAHAN untuk staf, owner dua
        ketukan + alasan; kelas = peta HET (satu sumber dengan hetUnit) / kelas label owner.

    python3 alat-uji/uji_stok_p5.py            → N lulus · 0 gagal (+ asap cadangan toko bila ada; angka rupiah toko tidak dicetak)
    python3 alat-uji/uji_stok_p5.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_jual_baru, uji_dasbor_sensus, uji_sisa_sensus  # noqa: E402
SG = 'baru/js/layar/stok-pantau-logika.js'; KH = 'baru/js/layar/kelas-het-logika.js'; AD = 'baru/js/layar/stok-adukan-logika.js'; CC = 'baru/js/layar/stok-catat-logika.js'
SL = 'baru/js/layar/stok-logika.js'; GD = 'baru/js/layar/gudang-logika.js'; SS = 'baru/js/layar/sistem-logika.js'; LPL = 'baru/js/layar/laporan-logika.js'
DL = 'baru/js/layar/dasbor-logika.js'; WG = 'baru/js/layar/dasbor-widget-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_dasbor_sensus.MODUL + [SG, KH, SS])))
SUMBER = {'stok': 'baru/js/layar/stok.js', 'laporan': 'baru/js/layar/laporan.js', 'harga': 'baru/js/layar/harga.js', 'dasbor': 'baru/js/layar/dasbor.js', 'app': 'baru/js/app.js',
          'index': 'baru/index.html', 'rules': 'firestore.rules', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'css': 'baru/css/stok.css',
          'sg': SG, 'kh': KH, 'ad': AD, 'cc': CC, 'sl': SL, 'gd': GD, 'ss': SS, 'lpl': LPL, 'dl': DL, 'wg': WG}


def MASUK(i, tgl, baris, pem='Pemasok Contoh', **x):
    d = {'id': i, 'tanggal': tgl, 'jam': '07:00', 'pemasok': pem, 'caraBayar': 'Tunai', 'biayaBongkar': 0, 'merkList': [
        dict({'merk': m, 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': kg / 50, 'totalKg': kg, 'subtotalHarga': kg * h, 'hargaPerKg': h}, **(e or {})) for m, kg, h, e in baris]}
    d.update(x); return d
def JUAL(i, tgl, merk, kg, jenis='karung', jam='09:00'):
    return {'id': i, 'tanggal': tgl, 'jam': jam, 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': jenis, 'merkSumber': merk, 'beratKarungAcuan': 50, 'jumlahKarung': kg / 50, 'totalKg': kg,
            'hargaTotal': kg * 13000, 'hppTotalSaatJual': kg * 12000, 'grupNota': 'g' + str(i)}
def KEMAS(i, tgl, nama, uk, unit):
    return {'id': i, 'tanggal': tgl, 'jam': '10:00', 'caraBayar': 'Tunai', 'jenis': 'kemasan', 'namaProduk': nama, 'ukuranKemasan': uk, 'jumlahUnit': unit, 'totalKg': uk * unit,
            'hargaTotal': unit * 70000, 'hppTotalSaatJual': unit * 63000, 'grupNota': 'g' + str(i)}
def ADUK(i, tgl, batch, merk, kgBahan, nama, uk, unit, **x):
    d = {'id': i, 'tanggal': tgl, 'jam': '11:00', 'merkSumber': merk, 'namaProduk': nama, 'ukuranKemasan': uk, 'jumlahUnit': unit, 'biayaKemasan': 0, 'upahRepacking': 1000 * unit,
         'kantongJenis': None, 'kantongJumlah': 0, 'hppSumberPerKgDipakai': 12000, 'hppPerUnit': 12000 * uk, 'sumberList': [{'merk': merk, 'kg': kgBahan}], 'kgDipakai': kgBahan,
         'sumberKemasanList': [], 'kgKemasanDipakai': 0, 'batchProduksi': batch, 'barisKe': 1, 'jumlahBaris': 1, 'jadiKarungUtuh': False, 'merkTujuan': None}
    d.update(x); return d
def SESUAI(i, tgl, jam, merk, sel, **x):
    d = {'id': i, 'tanggal': tgl, 'jam': jam, 'merk': merk, 'kgSistem': 1000, 'kgFisik': 1000 + sel, 'selisihKg': sel, 'alasan': 'Cocokkan stok', 'nilaiRp': sel * 12000, 'hppPerKgSaatOpname': 12000}
    d.update(x); return d

K5 = 'Angsa|5'
KOTAK = {
    'batchMasuk': [MASUK(100, '2026-07-01', [('Lama', 100, 9000, None)]),
                   MASUK(101, '2026-08-01', [('Angsa', 3000, 12000, None), ('Kembang', 900, 10000, None), ('Pelita', 500, 11000, None)]),
                   MASUK(102, '2026-11-02', [('Angsa', 1000, 12200, None)], pem='Pemasok Kedua'),
                   MASUK(103, '2026-11-18', [('Angsa', 500, 12500, {'timbangKg': 495})]),
                   MASUK(104, '2026-11-18', [('Buku Baru', 0, 0, None)], pem='LAHIR BUKU', lahirBuku=True, stokAwal=True)],
    'penjualan': [JUAL('s%d' % i, t, m, kg) for i, (t, m, kg) in enumerate([
        ('2026-08-10', 'Angsa', 600), ('2026-09-10', 'Angsa', 600), ('2026-10-10', 'Angsa', 600), ('2026-08-11', 'Kembang', 300), ('2026-09-11', 'Kembang', 300), ('2026-10-11', 'Kembang', 60),
        ('2026-08-12', 'Pelita', 100), ('2026-09-12', 'Pelita', 100), ('2026-11-10', 'Angsa', 50), ('2026-11-12', 'Angsa', 50), ('2026-11-12', 'Kembang', 100), ('2026-11-15', 'Karung Gabung', 10)])]
      + [JUAL('n4', '2026-11-12', 'Angsa', 50, jam='15:00'), JUAL('l1', '2026-11-10', 'Angsa', 10, jenis='literan')]
      + [KEMAS('k1', '2026-10-25', 'Angsa', 5, 10), KEMAS('k2', '2026-11-08', 'Angsa', 5, 5), KEMAS('k3', '2026-11-12', 'Angsa', 5, 5), KEMAS('k4', '2026-11-16', 'Angsa', 5, 5)],
    'produksiKemasan': [ADUK('a1', '2026-11-05', 'b1', 'Angsa', 100, 'Angsa', 5, 19, sampelIsi={'unit': 3, 'kg': 14.9}),
                        ADUK('a2', '2026-11-06', 'b2', 'Kembang', 50, 'Kembang', 3, 17, oplos={'teks': 'OPLOS: contoh', 'alasan': 'alasan contoh'}),
                        ADUK('a3', '2026-10-20', 'b3', 'Angsa', 50, 'Angsa', 5, 10),
                        ADUK('g1', '2026-11-09', 'g1', 'Kembang', 50, 'Karung Gabung', 50, 1, jadiKarungUtuh=True, merkTujuan='Karung Gabung'),
                        ADUK('t1', '2026-11-07', 't1', 'Angsa', 20, 'Takar Contoh', 10, 2, dariTakar=True)],
    'retur': [{'id': 'r1', 'tanggal': '2026-11-11', 'jam': '10:00', 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'namaProduk': 'Angsa', 'totalKg': 50, 'kondisi': 'utuh', 'nominalRefund': 650000}],
    'penyesuaianStok': [SESUAI('p1', '2026-11-17', '10:00', 'Angsa', -5, bagian='tumpukan', bagianSistemKg=1000, bagianFisikKg=995, dihitungOleh='Penghitung A'),
                        SESUAI('p2', '2026-11-17', '10:05', 'Kembang', 0, bagian='tumpukan', bagianSistemKg=40, bagianFisikKg=40, cocokPersis=True, dihitungOleh='Penghitung A', didampingi='Pendamping B', hama='kutu'),
                        SESUAI('p3', '2026-11-17', '21:00', 'Angsa', -0.5, dariTutup=True),
                        SESUAI('p4', '2026-11-10', '10:00', 'Pelita', -2, bagian='tumpukan', bagianSistemKg=300, bagianFisikKg=298, hama='tidak'),
                        SESUAI('p5', '2026-10-28', '10:00', 'Buku Baru', 0, bagian='tumpukan', bagianSistemKg=0, bagianFisikKg=0, cocokPersis=True, hama='tikus')],
    'pesanan': [{'id': 'o1', 'tanggal': '2026-11-17', 'jam': '09:00', 'namaPelanggan': 'Pelanggan Contoh A', 'status': 'dipesan', 'nilaiPerkiraan': 2000000, 'isi': '',
                 'baris': [{'jalur': 'karung', 'kunci': 'Angsa', 'berat': 50, 'nama': 'Angsa 50 kg', 'jumlah': 2, 'satuan': 'karung', 'kg': 100},
                           {'jalur': 'kemasan', 'kunci': K5, 'ukuranKg': 5, 'nama': 'Angsa 5 kg', 'jumlah': 10, 'satuan': 'kemasan', 'kg': 50}]},
                {'id': 'o2', 'tanggal': '2026-11-17', 'jam': '09:30', 'namaPelanggan': 'Pelanggan Contoh B', 'status': 'dipesan', 'nilaiPerkiraan': 300000, 'isi': 'beras campur 1 karung'},
                {'id': 'o3', 'tanggal': '2026-11-10', 'jam': '09:30', 'namaPelanggan': 'Pelanggan Contoh C', 'status': 'dibayar', 'nilaiPerkiraan': 650000,
                 'baris': [{'jalur': 'karung', 'kunci': 'Angsa', 'berat': 50, 'nama': 'Angsa 50 kg', 'jumlah': 1, 'satuan': 'karung', 'kg': 50}]}],
}
ATUR = [{'id': 'catatStok', 'tempoHari': 21, 'modalFifoMulai': '', 'label': {'kelas': {K5: 'Premium'}}}, {'id': 'het', 'peta': {'Angsa': 'medium', 'Kembang': 'premium'}}]

SKENARIO = r"""
(function () {
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); }; var dekat = function (a, b, t) { return a !== null && b !== null && a !== undefined && b !== undefined && Math.abs(a - b) < (t || 0.005); };
var KINI = new Date('2026-11-18T14:00:00+07:00'); var nId = 90000; var iso = '2026-11-18';
var W = { tanggal: '2026-11-18', jam: '14:00', kini: '2026-11-18T07:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK0).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'penyesuaianStok', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'stokBahanKemasan', 'pesanan', 'karantina', 'persetujuan', 'pengeluaranHarian', 'cekGudang'].forEach(function (n) { pasok(n, []); });
Object.keys(GK).forEach(function (n) { pasok(n, JSON.parse(J(GK[n]))); });
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-07-01', laci: 1000000, brankas: 0, rekening: 0, amplop: 0, diubahPada: '2026-07-01T14:00:00.000Z' }]);
setelSumber('cadangan', 'kotak pasir');
var aturDengan = function (extra) { var e = extra || []; var id = {}; e.forEach(function (d) { id[d.id] = 1; }); pasok('aturanToko', JSON.parse(J(ATUR)).filter(function (d) { return !id[d.id]; }).concat(e)); };
aturDengan([]);
var buku = function (m) { var x = ingatStokKarung()[m]; return x ? Math.round(x.sisaKg * 100) / 100 : null; };

// ==================== 1 · KARTU STOK (A56) ====================
var KA = sgKartuStok('Angsa', '2026-11-01', iso, true);
ok('1: Angsa buku mesin 2.414,5 kg = 4.500 masuk − 1.960 terjual − 170 diaduk/takar + 50 retur utuh − 5,5 hitungan & timbang tutup', buku('Angsa') === 2414.5 && KA.sisaAkhir === 2414.5 && KA.mesin === 2414.5 && KA.menutup && !KA.pembulatan, J([buku('Angsa'), KA.sisaAkhir]));
ok('1: sisa awal 1 Nov = 3.000 − 1.800 (Agu–Okt) − 50 (adukan Okt) = 1.150; Nov masuk 1.550 (2 kedatangan + retur) keluar 285,5', KA.saldoAwal === 1150 && KA.masukKg === 1550 && KA.keluarKg === 285.5, J([KA.saldoAwal, KA.masukKg, KA.keluarKg]));
var jenisA = KA.baris.map(function (r) { return r.jenis; }).join(',');
ok('1: per nota: urut tanggal & jam — masuk · aduk · aduk(takar) · jual · jual(literan) · retur · jual · jual · cocok · tutup · masuk (11 baris)', jenisA === 'masuk,aduk,aduk,jual,jual,retur,jual,jual,cocok,tutup,masuk', jenisA);
var mA = KA.baris[0]; var akhirA = KA.baris[KA.baris.length - 1];
ok('1: baris barang masuk membawa harga beli/kg (Rp12.200) & modal/kg; sisa berjalan baris terakhir = buku', mA.harga === 12200 && mA.modal > 0 && mA.masuk === 1000 && mA.sisa === 2150 && akhirA.sisa === 2414.5 && akhirA.harga === 12500, J([mA, akhirA]));
var KR = sgKartuStok('Angsa', '2026-11-01', iso, false); var g12 = KR.baris.find(function (r) { return r.jenis === 'jual' && r.tanggal === '2026-11-12'; });
ok('1: tanpa "per nota": 2 nota karung 12 Nov digabung (100 kg, "2 nota karung"), literan 10 Nov tetap barisnya sendiri; sisa akhir sama', KR.baris.length === 10 && g12 && g12.keluar === 100 && /2 nota karung/.test(g12.ket) && KR.sisaAkhir === 2414.5 && KR.baris.some(function (r) { return r.ket === 'nota literan'; }), J(KR.baris.map(function (r) { return [r.tanggal, r.jenis, r.ket, r.keluar]; })));
var hit = KA.baris.find(function (r) { return r.jenis === 'cocok'; }); var tut = KA.baris.find(function (r) { return r.jenis === 'tutup'; });
ok('1: hitungan gudang & timbang tutup hari tampil sebagai gerak (−5 & −0,5), membawa siapa yang menghitung', hit.keluar === 5 && hit.dihitungOleh === 'Penghitung A' && tut.keluar === 0.5 && tut.nama === 'Timbang tutup hari', J([hit, tut]));
var KG_ = sgKartuStok('Karung Gabung', '2026-11-01', iso, true); var KB = sgKartuStok('Kembang', '2026-11-01', iso, true);
ok('1: buku yang lahir HANYA dari adukan jadi karung (Karung Gabung): nota 10 kg-nya tidak dipotong (urutan mesin) — kartu = mesin 50 kg', KG_.sisaAkhir === 50 && KG_.mesin === 50 && KG_.menutup && KG_.baris.length === 1 && KG_.baris[0].jenis === 'karung', J(KG_.baris));
ok('1: Kembang: pindah buku → Karung Gabung tercatat keluar 50 kg; buku 40 kg = kartu', KB.menutup && KB.sisaAkhir === 40 && KB.baris.some(function (r) { return r.jenis === 'aduk' && /pindah buku → Karung Gabung/.test(r.ket) && r.keluar === 50; }), J(KB.baris));
var semuaTutup = sgDaftarKartu().every(function (b) { return sgKartuStok(b.kunci, '2000-01-01', iso, true).menutup; });
ok('1: SEMUA buku: sisa berjalan = buku mesin (penjaga menutup)', semuaTutup && sgDaftarKartu().length >= 6, J(sgDaftarKartu()));
ok('1: buku yang tidak ada = kalimat, tidak jatuh', !sgKartuStok('Tidak Ada', '2026-11-01', iso, true).ada && /tidak ada di buku/.test(sgKartuStok('Tidak Ada', '2026-11-01', iso, true).kalimat));

// ==================== 2 · BARANG MASUK HARI ITU (A125) ====================
var MH = sgMasukHari(iso);
ok('2: 18 Nov: 1 kedatangan (buku lahir 0 kg BUKAN kedatangan) · 10 karung · 500 kg · timbang kurang 5 kg; Σ = rekap timbang Stok', MH.total.n === 1 && MH.total.karung === 10 && MH.total.kg === 500 && MH.total.selisihKg === -5 && MH.menutup && MH.rekap.kedatangan === 1, J([MH.total, MH.rekap]));
ok('2: teks satu baris: "Barang masuk: 1 kedatangan · 10 karung · 500 kg · timbang kurang 5 kg"', MH.teks === 'Barang masuk: 1 kedatangan · 10 karung · 500 kg · timbang kurang 5 kg', MH.teks);
ok('2: hari tanpa kedatangan = "tidak ada"; 2 Nov pemasok kedua tanpa timbang', /tidak ada kedatangan/.test(sgMasukHari('2026-11-03').teks) && sgMasukHari('2026-11-02').daftar[0].pemasok === 'Pemasok Kedua' && sgMasukHari('2026-11-02').total.kgNota === 0, sgMasukHari('2026-11-02').teks);
var R18 = rekapHari(iso); var T0 = teksRekapHari(R18, null); var T1 = teksRekapHari(R18, null, MH.teks);
ok('2: teks WA rekap harian: baris barang masuk ditambahkan bila diberikan; tanpa itu teks lama persis', T0 === teksRekapHari(R18, null, '') && T1.indexOf(MH.teks) > 0 && T1.replace('\n' + MH.teks, '') === T0, J([T0.slice(-80), T1.slice(-120)]));

// ==================== 3 · HITUNG KARUNG MINGGUAN (A127 · A70) ====================
var HM = sgHitungMinggu(iso, KINI); var hA = HM.daftar.find(function (p) { return p.merk === 'Angsa'; }); var hK = HM.daftar.find(function (p) { return p.merk === 'Kembang'; });
ok('3: minggu Senin 16 – Minggu 22 Nov; timbang tutup hari & hitungan minggu lalu (Pelita 10 Nov) TIDAK ikut', HM.awal === '2026-11-16' && HM.akhir === '2026-11-22' && HM.daftar.length === 2 && !HM.daftar.some(function (p) { return p.merk === 'Pelita'; }) && hA.kali === 1, J(HM.daftar));
ok('3: Angsa: buku 1.000 → dihitung 995 = −5 kg (−0,1 karung), dihitung Penghitung A, TANPA pendamping; Kembang cocok, didampingi, hama kutu', hA.selisihKg === -5 && hA.selisihKarung === -0.1 && hA.tanpaPendamping === 1 && hA.terakhir.oleh === 'Penghitung A' && !hA.terakhir.didampingi
  && hK.selisihKg === 0 && hK.terakhir.didampingi === 'Pendamping B' && hK.terakhir.hama === 'kutu' && HM.total.tanpaPendamping === 1, J([hA, hK]));
ok('3: merek berisi yang belum dihitung minggu ini disebut (Pelita, Lama, Karung Gabung)', ['Pelita', 'Lama', 'Karung Gabung'].every(function (m) { return HM.belum.some(function (x) { return x.merk === m; }); }) && !HM.belum.some(function (x) { return x.merk === 'Angsa'; }), J(HM.belum));
ok('3: minggu tanpa hitungan = kalimat "belum ada", bukan 0', sgHitungMinggu('2026-11-03', KINI).daftar.length === 0 && /belum ada tumpukan/.test(sgHitungMinggu('2026-11-03', KINI).kalimat));

// ==================== 4 · COCOKKAN: dihitung oleh / didampingi / hama (A70 · A43) ====================
var HC = { 'tumpukan|Angsa': '2400' }; var YA = { sebagian: true, ganda: true, aneh: true, susutPositif: true };
var C1 = susunSimpanCocok('tumpukan', HC, {}, W, YA, null, { dihitungOleh: ' Penghitung  A ', didampingi: 'Pendamping B', hama: { 'tumpukan|Angsa': 'ngengat' } }); var c1 = C1.dokumen && C1.dokumen[0].data;
ok('4: simpan: penyesuaianStok membawa dihitungOleh (spasi dirapikan), didampingi, hama; kabar menyebut pendampingnya', !C1.tolak && c1.dihitungOleh === 'Penghitung A' && c1.didampingi === 'Pendamping B' && c1.hama === 'ngengat' && /didampingi Pendamping B/.test(C1.patch.kabar) && /hama dicatat di 1 tumpukan/.test(C1.patch.kabar), J([C1.tolak, c1, C1.patch && C1.patch.kabar]));
var C0 = susunSimpanCocok('tumpukan', HC, {}, W, YA); var c0 = C0.dokumen[0].data;
ok('4: tanpa isian: kolom dihitungOleh/didampingi/hama TIDAK ada (bentuk dokumen lama); kabar "tanpa pendamping"', !('dihitungOleh' in c0) && !('didampingi' in c0) && !('hama' in c0) && /tanpa pendamping/.test(C0.patch.kabar), J(Object.keys(c0)));
ok('4: orang yang sama menghitung & mendampingi ditolak; hama tak dikenal ditolak; nama > 40 huruf ditolak',
  /orang lain/.test(susunSimpanCocok('tumpukan', HC, {}, W, YA, null, { dihitungOleh: 'Penghitung A', didampingi: 'penghitung a' }).tolak || '') && /tidak dikenal/.test(susunSimpanCocok('tumpukan', HC, {}, W, YA, null, { hama: { 'tumpukan|Angsa': 'kecoa' } }).tolak || '')
  && /40 huruf/.test(susunSimpanCocok('tumpukan', HC, {}, W, YA, null, { didampingi: new Array(42).join('x') }).tolak || ''));
terapkanKeCache(C1.dokumen);
var HMa = umHama(); var cal = ccCalonOrang();
ok('4: hama per tumpukan = hitungan TERBARU yang mencatat hama (Angsa ngengat baru saja · Kembang kutu); calon nama dari hitungan sebelumnya', HMa.Angsa && HMa.Angsa.ada && HMa.Angsa.label === 'ngengat' && HMa.Kembang.label === 'kutu' && cal.indexOf('Pendamping B') >= 0 && cal.indexOf('Penghitung A') >= 0, J([HMa, cal]));
var HM2 = sgHitungMinggu(iso, KINI); var hA2 = HM2.daftar.find(function (p) { return p.merk === 'Angsa'; });
ok('4: laporan mingguan memakai hitungan baru: Angsa 2× minggu ini, terakhir didampingi', hA2.kali === 2 && hA2.terakhir.didampingi === 'Pendamping B' && hA2.tanpaPendamping === 1, J(hA2));

// ==================== 5 · BATAS SIMPAN KEDUA & HAMA (A43) ====================
var UA = umAtur(); var UR = umRingkas(KINI);
ok('5: bawaan batas simpan 120 hari (keputusan owner 27 Nov 2026); Lama (masuk 1 Jul, 140 hari) lewat, 100 kg', UA.batasSimpanHari === 120 && UR.lewatSimpan.length === 1 && UR.lewatSimpan[0].nama === 'Lama' && UR.kgLewatSimpan === 100, J([UA, UR.lewatSimpan.map(function (r) { return [r.nama, r.umurAcuan]; })]));
var UP = umPapan(KINI, 'simpan', 'Lama'); var kS = UP.kartu.find(function (k) { return k.id === 'simpan'; });
ok('5: Umur & putaran: kartu kelima "lewat batas simpan" MERAH, daftar + rincian menyebut LEWAT BATAS SIMPAN', kS && kS.merah && /1 barang/.test(kS.a) && UP.kelompok[0].baris[0].kunci === 'Lama' && UP.kelompok[0].baris[0].rinci.some(function (x) { return /LEWAT BATAS SIMPAN 120 hari/.test(x.teks) && x.awas; }), J([kS, UP.kelompok]));
ok('5: atur: batas simpan ≤ ambang lambat laku ditolak; pecahan ditolak; 150 diterima (dokumen stokUmur yang sama)', /lebih lama dari ambang/.test(susunAturUmur({ batasSimpanHari: '30' }, W).tolak || '') && !!susunAturUmur({ batasSimpanHari: '120,5' }, W).tolak
  && susunAturUmur({ batasSimpanHari: '150' }, W).dokumen[0].data.batasSimpanHari === 150 && susunAturUmur({ batasSimpanHari: '150' }, W).dokumen[0].data.id === 'stokUmur');
var GT = gdTugas(KINI, W); var tS = GT.daftar.find(function (x) { return x.id === 'simpan'; }); var tH = GT.daftar.find(function (x) { return x.id === 'hama'; });
ok('5: Tugas gudang: "Stok lewat batas simpan" 1 (Lama) & "Tumpukan berhama" 2 (Angsa ngengat, Kembang kutu; Pelita "tidak ada hama" & Buku Baru tanpa stok tidak ikut) — awas', tS.n === 1 && tS.awas && /Lama 140 hr/.test(tS.ket) && tH.n === 2 && tH.awas && /Angsa \(ngengat/.test(tH.ket), J([tS, tH]));
var DMu = dbMutu(KINI);
ok('5: Dasbor › Mutu usaha: baris umur membawa lewat batas simpan (angka yang sama)', DMu.umur.lewatSimpan === 1 && DMu.umur.kgLewat === 100 && DMu.umur.batasSimpan === 120, J(DMu.umur));
terapkanKeCache(susunAturUmur({ batasSimpanHari: '150' }, W).dokumen);
ok('5: batas 150 → Lama (140 hari) tidak lagi lewat', umRingkas(KINI).lewatSimpan.length === 0 && umAtur().batasSimpanHari === 150);
terapkanKeCache(susunAturUmur({ batasSimpanHari: '120' }, W).dokumen);

// ==================== 6 · OPNAME KEJUTAN (A92) ====================
ok('6: belum dinyalakan = mati (bukan bawaan menyala); tidak ada pengingat', !sgKejutanAtur().aktif && sgSumberPengingat(KINI).length === 0 && sgKejutanTanggal('2026-12').length === 0);
ok('6: atur: pecahan / di luar batas / pengundi kosong ditolak', !!susunAturKejutan({ kaliSebulan: '2,5', benih: 'benihcontoh0001' }, W).tolak && !!susunAturKejutan({ nMerek: '51', benih: 'benihcontoh0001' }, W).tolak && !!susunAturKejutan({ kaliSebulan: '32', benih: 'benihcontoh0001' }, W).tolak && !susunAturKejutan({ kaliSebulan: '15', nMerek: '15', benih: 'benihcontoh0001' }, W).tolak && /belum siap/.test(susunAturKejutan({ benih: 'abc' }, W).tolak || ''));
var AK1 = susunAturKejutan({ kaliSebulan: '2', nMerek: '2', benih: 'benihcontoh0001' }, W); terapkanKeCache(AK1.dokumen);
var A1 = sgKejutanAtur(); var D12 = sgKejutanTanggal('2026-12'); var D12b = sgKejutanTanggal('2026-12');
ok('6: menyala: 2× sebulan, 2 merek; Desember 2 tanggal berbeda & urut, undian TETAP (benih sama = tanggal sama)', A1.aktif && A1.kaliSebulan === 2 && A1.nMerek === 2 && D12.length === 2 && D12[0] < D12[1] && J(D12) === J(D12b) && AK1.dokumen[0].data.id === 'opnameKejutan', J([A1, D12]));
ok('6: bulan mulai: hanya tanggal sejak dinyalakan (18 Nov)', sgKejutanTanggal('2026-11').every(function (t) { return t >= '2026-11-18'; }));
terapkanKeCache(susunAturKejutan({ kaliSebulan: '2', nMerek: '2', benih: 'benihlain000002' }, W).dokumen);
ok('6: simpan ulang TANPA undi ulang = benih lama dipertahankan (undian tidak berubah)', sgKejutanAtur().benih === 'benihcontoh0001' && J(sgKejutanTanggal('2026-12')) === J(D12));
terapkanKeCache(susunAturKejutan({ kaliSebulan: '2', nMerek: '2', benih: 'benihlain000002', undiUlang: true }, W).dokumen);
ok('6: undi ulang = benih baru', sgKejutanAtur().benih === 'benihlain000002');
var bln = ['2026-12', '2027-01', '2027-02', '2027-03', '2027-04', '2027-05']; var undiB = bln.map(function (k) { return J(sgKejutanTanggal(k)); });
terapkanKeCache(susunAturKejutan({ kaliSebulan: '2', nMerek: '2', benih: 'benihcontoh0001', undiUlang: true }, W).dokumen);
var undiA = bln.map(function (k) { return J(sgKejutanTanggal(k)); });
ok('6: benih lain = undian lain (tanggal enam bulan ke depan tidak semuanya sama)', undiA.some(function (x, i) { return x !== undiB[i]; }), J([undiA, undiB]));
var d = sgKejutanTanggal('2026-12')[0]; var kd = new Date(d + 'T10:00:00+07:00'); var M = sgKejutanMerek(d);
ok('6: merek diundi dari buku merek yang BERISI (bukan Buku Baru 0 kg), tetap, urut', M.length === 2 && M.every(function (m) { return (buku(m) || 0) > 0.05 && m !== 'Buku Baru'; }) && J(M) === J(sgKejutanMerek(d)) && J(M) === J(M.slice().sort()), J(M));
var R1 = sgKejutanRentang(d, d, kd)[0]; var P1 = sgSumberPengingat(kd);
ok('6: hari itu: keadaan "hari ini", pengingat owner jenis kejutan menyebut merek yang belum dihitung', R1.keadaan === 'hari ini' && P1.length === 1 && P1[0].id === 'kejutan|' + d && P1[0].jenis === 'kejutan' && M.every(function (m) { return P1[0].teks.indexOf(m) >= 0; }), J([R1, P1]));
var Sx = ssSumberPengingat(kd, { gudang: P1 }); var SJ = SS_JENIS_PENGINGAT.find(function (j) { return j.id === 'kejutan'; });
ok('6: Sistem › Pengingat menerima jenis kejutan lewat lokal.gudang; bawaan ke Owner saja', Sx.some(function (p) { return p.jenis === 'kejutan' && p.id === 'kejutan|' + d; }) && SJ && J(SS_ATUR_BAWAAN.pengingat.ke.kejutan) === '["Owner"]' && SS_ATUR_BAWAAN.pengingat.nyala.kejutan === true, J(SJ));
pasok('penyesuaianStok', ambilPenyesuaianStok().concat([{ id: 'kj1', tanggal: d, jam: '11:00', merk: M[0], kgSistem: 10, kgFisik: 10, selisihKg: 0, bagian: 'tumpukan', cocokPersis: true, alasan: 'Cocokkan stok' }]));
var kd3 = new Date(sgTambah(d, 3) + 'T10:00:00+07:00'); var R3 = sgKejutanRentang(d, d, kd3)[0];
ok('6: satu dari dua dihitung, lewat tenggang 2 hari → "terlewat", yang belum disebut; pengingat tidak lagi muncul', R3.keadaan === 'terlewat' && J(R3.belum) === J([M[1]]) && sgSumberPengingat(kd3).length === 0, J(R3));
pasok('penyesuaianStok', ambilPenyesuaianStok().concat([{ id: 'kj2', tanggal: sgTambah(d, 2), jam: '11:00', merk: M[1], kgSistem: 10, kgFisik: 10, selisihKg: 0, bagian: 'tumpukan', cocokPersis: true, alasan: 'Cocokkan stok' }]));
ok('6: keduanya dihitung dalam tenggang → "selesai"; hitungan tutup hari / wadah tidak dihitung kejutan', sgKejutanRentang(d, d, kd3)[0].keadaan === 'selesai', J(sgKejutanRentang(d, d, kd3)));
ok('6: pengundi FNV-1a tetap: "a" → 3826002220', sgAcak('a') === 3826002220, sgAcak('a'));
terapkanKeCache(susunAturKejutan({ kaliSebulan: '31', nMerek: '50', benih: 'benihcontoh0001' }, W).dokumen);
var T31 = sgKejutanTanggal('2027-01'), T28 = sgKejutanTanggal('2027-02'), M50 = sgKejutanMerek('2027-01-10'); var isi = Object.keys(stokMerekSaja(ingatStokKarung('2027-01-09'))).filter(function (m) { return (ingatStokKarung('2027-01-09')[m].sisaKg || 0) > 0.05; });
ok('6: batas longgar (owner): 31× sebulan = SETIAP hari tanpa kembar (Februari 28); 50 merek = semua merek berisi, tanpa kembar', T31.length === 31 && T28.length === 28 && T31.filter(function (t, i) { return T31.indexOf(t) === i; }).length === 31
  && M50.length === isi.length && M50.filter(function (m, i) { return M50.indexOf(m) === i; }).length === M50.length, J([T31.length, T28.length, M50, isi]));
terapkanKeCache(susunAturKejutan({ kaliSebulan: '2', nMerek: '2', benih: 'benihcontoh0001' }, W).dokumen);
terapkanKeCache(susunAturKejutan({ aktif: false }, W).dokumen);
ok('6: dimatikan → tidak ada undian / pengingat', !sgKejutanAtur().aktif && sgKejutanTanggal('2026-12').length === 0 && sgSumberPengingat(kd).length === 0);

// ==================== 7 · RENCANA BELI BULANAN (A20) ====================
var RB = sgRencanaBeli(KINI); var rb = function (m) { return RB.daftar.find(function (x) { return x.merk === m; }) || null; };
ok('7: bulan acuan Agu · Sep · Okt (selesai, sejak catatan pertama 1 Jul) = 92 hari; bulan depan Desember; musim disebut', RB.nHari === 92 && J(RB.bulan.map(function (b) { return b.key; })) === '["2026-08","2026-09","2026-10"]' && RB.depan === '2026-12' && /musim/.test(RB.musim) && /Agustus 2027/.test(RB.musim), J(RB.bulan));
var A_ = rb('Angsa'), K_ = rb('Kembang');
ok('7: Angsa: pemakaian Agu 600 · Sep 600 · Okt 650 (terjual + diaduk) → laju 1.850 ÷ 92; stok cukup → 0 karung', J(A_.perBulan) === '[600,600,650]' && dekat(A_.laju, 1850 / 92, 1e-9) && A_.arah === '' && A_.karung === 0, J(A_));
ok('7: Kembang: Okt turun tajam (60 < ½ rata-rata) → laju Okt saja 60 ÷ 31; pindah buku ke Karung Gabung BUKAN pemakaian', K_.arah === 'turun' && J(K_.perBulan) === '[300,300,60]' && dekat(K_.laju, 60 / 31, 1e-9) && dekat(K_.ini, 150), J(K_));
var lk = 60 / 31; var kur = lk * 31 + lk * 7 - Math.max(0, 40 - lk * 12);
ok('7: Kembang: butuh Des + cadangan 7 hari (batas bawah hari stok) − perkiraan sisa 1 Des → 2 karung 100 kg ±Rp1.000.000 (harga beli terakhir contoh)', dekat(K_.kurang, kur, 0.01) && K_.karung === Math.ceil(kur / 50) && K_.karung === 2 && K_.kg === 100 && K_.rp === 1000000, J([K_.kurang, kur, K_]));
ok('7: Pelita (tanpa pemakaian Okt & Nov) = berhenti dipakai, tidak diramal; total = Σ merek', !rb('Pelita') && RB.berhenti.some(function (x) { return x.merk === 'Pelita'; }) && RB.total.karung === RB.daftar.reduce(function (a, x) { return a + x.karung; }, 0) && RB.total.kg === 100, J([RB.berhenti.map(function (x) { return x.merk; }), RB.total]));

// ==================== 8 · STOK YANG DIPESAN (B51) ====================
var PS = sgPesananRp(KINI); var pK = PS.daftar.find(function (x) { return x.kunci === 'karung|Angsa'; }); var pM = PS.daftar.find(function (x) { return x.kunci === 'kemasan|' + KUNCI5; });
var modalK = ingatStokKarung().Angsa.hppTerakhirPerKg, modalM = ingatStokKemasan()[KUNCI5].hppRataRataPerUnit;
ok('8: pesanan belum jadi nota (o1, o2) — yang sudah dibayar tidak ikut; o2 tanpa barang katalog disebut', PS.nPesanan === 2 && PS.nTanpa === 1 && PS.rpJual === 2300000 && pK.jumlah === 100, J(PS));
ok('8: modal dipesan = 100 kg × modal Angsa di buku + 10 kemasan × modal kemasan (nilai neraca); kemasan sisa 4 → KURANG 6', pK.rp === Math.round(100 * modalK) && pM.rp === Math.round(10 * modalM) && PS.rp === pK.rp + pM.rp && pM.sisa === 4 && pM.kurang === 6 && PS.kurang.length === 1, J([pK, pM]));
var TP = gdTugas(KINI, W).daftar.find(function (x) { return x.id === 'pesanan'; });
ok('8: Tugas gudang › pesanan pelanggan menyebut modal dipesan & barang kurang', TP.rp === PS.rp && /modal dipesan/.test(TP.ket) && /1 barang kurang/.test(TP.ket) && TP.awas, J(TP));

// ==================== 9 · PRODUKSI PER BULAN & RENCANA PRODUKSI (B72 · A50) ====================
var PB = sgProduksiBulan('2026-11', KINI); var KR_ = kemasRentang('2026-11-01', iso);
ok('9: Nov = kemasRentang (Laporan › Pondasi): 2 adukan, bahan 150 → jadi 146 kg, susut 2,7 %; jadi karung & takar ke wadah TIDAK ikut', PB.adukan === 2 && PB.adukan === KR_.adukan && PB.kgBahan === 150 && PB.kgJadi === 146 && PB.susutPersen === 2.7 && PB.menutup && PB.daftar.length === 2, J([PB.adukan, PB.kgBahan, PB.kgJadi, PB.susutPersen, KR_]));
var b1 = PB.daftar.find(function (g) { return g.batch === 'b1'; }), b2 = PB.daftar.find(function (g) { return g.batch === 'b2'; });
ok('9: per adukan: b1 susut 5 %, sampel 3 kantong 14,9 kg → rata 4,967 < 5 = KURANG ISI; b2 hasil LEBIH BERAT 1 kg (−2 %) & OPLOS tercatat', b1.susutPersen === 5 && b1.sampel.length === 1 && b1.sampel[0].kurang && b1.kurangIsi === 1 && b2.lebihBerat && b2.susutPersen === -2 && b2.oplos && b2.oplos.alasan === 'alasan contoh' && b2.awas
  && PB.tanda.oplos === 1 && PB.tanda.kurangIsi === 1 && PB.tanda.lebihBerat === 1, J([b1, b2]));
ok('9: biaya kemas per kg = (kantong + upah) ÷ kg jadi', dekat(PB.biayaPerKg, (PB.kantongRp + PB.upahRp) / 146, 1e-9) && PB.upahRp === 36000, J([PB.kantongRp, PB.upahRp]));
var PD = sgProduksiDeret(KINI, 6);
ok('9: deret 6 bulan: Jun sebelum catatan; Okt 1 adukan 50 kg; Nov berjalan', PD.length === 6 && PD[0].sebelum && PD[4].key === '2026-10' && PD[4].adukan === 1 && PD[4].kgJadi === 50 && PD[5].berjalan, J(PD.map(function (b) { return [b.key, b.sebelum, b.adukan, b.kgJadi]; })));
var RP_ = sgRencanaProduksi(KINI); var rA = RP_.daftar.find(function (x) { return x.kunci === KUNCI5; });
var gb = susunGudang('beli', KINI).jawab.baris.find(function (x) { return x.kunci === 'kemasan|' + KUNCI5; }); var nG = gb ? Number((/aduk (\d+) unit/.exec(gb.n) || [])[1]) : null;
ok('9: rencana produksi Angsa 5 kg = "aduk N unit" Stok › Gudang (laju 14 hari × 7 − sisa 4); bahan biasa Angsa, kg bahan memperhitungkan susut 5 % terakhir', rA && nG !== null && rA.unit === nG && rA.unit > 0 && rA.bahan.length === 1 && rA.bahan[0].merk === 'Angsa' && dekat(rA.kgBahan, rA.unit * 5 / 0.95, 0.01) && rA.susutPersen === 5, J([rA, gb]));
ok('9: kemasan tanpa penjualan (Kembang 3 kg) tidak direncanakan', !RP_.daftar.some(function (x) { return x.kunci === 'Kembang|3'; }));

// ==================== 10 · ADUKAN: SAMPEL ISI · LEBIH BERAT · OPLOS (A50) ====================
var WA = { tanggal: iso, jam: '14:00', idUnik: function () { nId += 1; return nId; } }; var Y = { bahan: true, kemasan: true, kantongKosong: true, kantong: true, mundur: true, susut: true };
var draf = function (merk, kg, hasil, x) { return Object.assign({ tanggal: iso, bahan: [{ merk: merk, kg: String(kg) }], bahanKemasan: [], hasil: hasil, upah: '' }, x || {}); };
var Hr = function (nama, uk, unit, x) { return Object.assign({ nama: nama, ukuran: String(uk), unit: String(unit), kantongJenis: '', kantongJumlah: '' }, x || {}); };
var hA_ = hitungAdukan(draf('Angsa', 50, [Hr('Angsa', 10, 5)]));
ok('10: kelas: Angsa (medium) → Angsa 10 kg (tanpa kelas label → peta HET medium) = aman', hA_.kelas.status === 'aman' && !hA_.lebihBerat && !hA_.sampelSalah.length, J(hA_.kelas));
var hO = hitungAdukan(draf('Angsa', 50, [Hr('Angsa', 5, 10)]));
ok('10: kelas LABEL owner menang: Angsa 5 kg berlabel Premium ← bahan Angsa medium = OPLOS', hO.kelas.status === 'oplos' && hO.kelas.oplos[0].sumberKelas === 'label' && /Angsa \(medium\) masuk ke Angsa 5 kg berlabel premium/.test(hO.kelas.teks), hO.kelas.teks);
ok('10: premium → label medium bukan oplos; merek belum dipetakan = "belum" (disebut, tidak ditahan)', hitungAdukan(draf('Kembang', 50, [Hr('Angsa', 10, 5)])).kelas.status === 'aman' && hitungAdukan(draf('Pelita', 50, [Hr('Angsa', 10, 5)])).kelas.status === 'belum');
var dO = draf('Angsa', 50, [Hr('Kembang', 10, 5)]);
var sStaf = susunSimpanAdukan(Object.assign({}, dO, { batasHasil: 3 }), WA, Object.assign({ oplos: true }, Y));
ok('10: OPLOS DITAHAN untuk akun staf (batasHasil > 0) — walau sudah "yakin"', !!sStaf.tolak && sStaf.ditahan && /DITAHAN/.test(sStaf.tolak) && !sStaf.dokumen, sStaf.tolak);
var sO1 = susunSimpanAdukan(dO, WA, Y); var sO2 = susunSimpanAdukan(dO, WA, Object.assign({ oplos: true }, Y)); var sO3 = susunSimpanAdukan(Object.assign({}, dO, { alasanOplos: 'alasan contoh oplos' }), WA, Object.assign({ oplos: true }, Y));
ok('10: owner: ketukan pertama minta yakin, kedua tanpa alasan ditolak, dengan alasan tersimpan — dokumen pertama membawa oplos {teks, alasan}, kabar awas', sO1.perluYakin === 'oplos' && sO2.perluYakin === 'oplos' && /alasan/.test(sO2.tolak) && !!sO3.dokumen
  && sO3.dokumen[0].data.oplos.alasan === 'alasan contoh oplos' && /OPLOS/.test(sO3.dokumen[0].data.oplos.teks) && sO3.patch.kabarAwas, J([sO1.tolak, sO2.tolak, sO3.dokumen && sO3.dokumen[0].data.oplos]));
var dS = draf('Kembang', 15, [Hr('Kembang', 5, 3, { sampelUnit: '3', sampelKg: '14,9' })]); var hS = hitungAdukan(dS); var sS = susunSimpanAdukan(dS, WA, Y);
ok('10: sampel 3 kantong 14,9 kg → rata 4,967 kg < 5 − 0,005 = KURANG ISI (ditandai, tetap tersimpan); dokumen membawa sampelIsi {unit 3, kg 14,9}', hS.sampelKurang.length === 1 && hS.sahH[0].sampel.kurang && dekat(hS.sahH[0].sampel.persen, -0.7, 1e-9)
  && !!sS.dokumen && J(sS.dokumen[0].data.sampelIsi) === '{"unit":3,"kg":14.9}' && /KURANG ISI/.test(sS.patch.kabar), J([hS.sahH[0].sampel, sS.tolak]));
ok('10: sampel 5,00 kg per kantong pas = tidak ditandai; isi sebagian / di luar 50–150 % ditolak saat simpan', !hitungAdukan(draf('Kembang', 15, [Hr('Kembang', 5, 3, { sampelUnit: '2', sampelKg: '10' })])).sahH[0].sampel.kurang
  && /isi dua-duanya/.test(susunSimpanAdukan(draf('Kembang', 15, [Hr('Kembang', 5, 3, { sampelUnit: '2' })]), WA, Y).tolak || '') && /tidak masuk akal/.test(susunSimpanAdukan(draf('Kembang', 15, [Hr('Kembang', 5, 3, { sampelUnit: '2', sampelKg: '20' })]), WA, Y).tolak || ''));
var sP = susunSimpanAdukan(draf('Kembang', 15, [Hr('Kembang', 5, 3)]), WA, Y);
ok('10: tanpa sampel & bukan oplos: dokumen TANPA kolom sampelIsi / oplos (bentuk lama)', !!sP.dokumen && !('sampelIsi' in sP.dokumen[0].data) && !('oplos' in sP.dokumen[0].data), J(Object.keys(sP.dokumen[0].data)));
var hL = hitungAdukan(draf('Kembang', 15, [Hr('Kembang', 2, 8)])); var sL = susunSimpanAdukan(draf('Kembang', 15, [Hr('Kembang', 2, 8)]), WA, {});
ok('10: hasil 16 kg dari bahan 15 kg (lebih 6,7 % — di bawah ambang tanya 15 %) = LEBIH BERAT ditandai di kabar, tidak ditahan', hL.lebihBerat && /HASIL LEBIH BERAT 1 kg/.test(sL.patch.kabar) && sL.patch.kabarAwas && !!sL.dokumen, (sL.patch && sL.patch.kabar) || sL.tolak);
var nmK = ['Angsa', 'Kembang', 'Pelita', 'Lama', 'Karung Gabung'];
ok('10: kategori kelas = hetAtur().peta[hetUnit(m).unit] untuk tiap nama (satu sumber dengan Harga › HET); label = lbAtur().kelas', nmK.every(function (m) { return khKategori(m) === (hetAtur().peta[hetUnit(m).unit] || ''); }) && khKelasLabel('Angsa', 5) === lbAtur().kelas[KUNCI5] && J(LB_KELAS) === '["Premium","Medium","Submedium","Pecah"]');
aturDengan([{ id: 'kelasMerek', peta: { 'Merek Anggota': 'Angsa', 'Merek Tebak': 'Kembang' }, asal: { 'Merek Tebak': 'tebakan' } }]);
ok('10: anggota kelas yang dikonfirmasi owner memakai kelas induknya; tebakan = merek itu sendiri (sama dengan hetUnit)', khSatuan('Merek Anggota') === 'Angsa' && khKategori('Merek Anggota') === 'medium' && khSatuan('Merek Tebak') === 'Merek Tebak'
  && ['Merek Anggota', 'Merek Tebak'].every(function (m) { return khSatuan(m) === hetUnit(m).unit; }), J([hetUnit('Merek Anggota'), hetUnit('Merek Tebak')]));
aturDengan([]);

// ==================== 11 · DASBOR (katalog, bawaan tidak berubah) ====================
var D = dbTambahan(susunDasbor(KINI, 'hari', null, null, dbSaring({ id: 'hari' }, KINI)), KINI); var G5 = D.gudang5;
ok('11: kelompok gudang5 tanpa galat: barang masuk hari ini, produksi 6 bulan, pesanan, lewat simpan', G5 && !G5.masuk.galat && G5.masuk.total.n === 1 && G5.produksi.length === 6 && G5.pesanan.rp === PS.rp && G5.simpan.n === 1, J(G5 && G5.simpan));
var Wd = wgSusun(['kMasukHari', 'kProduksi', 'pesananRp', 'lewatSimpan'].map(function (x) { return { id: x }; }), D); var wg = function (id) { return Wd.find(function (w) { return w.id === id; }); };
ok('11: widget katalog membaca kelompoknya apa adanya (tanpa galat)', Wd.length === 4 && Wd.every(function (w) { return w.nilai !== 'gagal dihitung'; }) && wg('kMasukHari').nilai === '500 kg' && wg('kProduksi').nilai === '146 kg' && wg('lewatSimpan').nilai === '1 barang' && wg('lewatSimpan').awas, J(Wd.map(function (w) { return [w.id, w.nilai, w.ket]; })));
ok('11: susunan bawaan Dasbor tidak berubah (kartu baru hanya lewat "+ Tambah kartu")', !WG_BAWAAN.some(function (w) { return ['kMasukHari', 'kProduksi', 'pesananRp', 'lewatSimpan'].indexOf(w.id) >= 0; }) && WG_KATALOG.length <= WG_MAKS, J([WG_KATALOG.length, WG_MAKS]));

// ==================== 12 · PENJAGA kartu stok: catatan rusak (nota tanpa kg) → mesin NaN, kartu 0 → TIDAK MENUTUP disebut ====================
pasok('batchMasuk', ambilSemuaBatch().concat([{ id: 900, tanggal: '2026-11-01', jam: '07:00', pemasok: 'Pemasok Contoh', caraBayar: 'Tunai', biayaBongkar: 0, merkList: [{ merk: 'Rusak Contoh', satuan: 'karung', beratKarung: 50, jumlahKarung: 1, totalKg: 50, subtotalHarga: 500000, hargaPerKg: 10000 }] }]));
pasok('penjualan', ambilPenjualan().concat([{ id: 'xx', tanggal: '2026-11-02', jam: '09:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Rusak Contoh', hargaTotal: 0 }]));
var KX = sgKartuStok('Rusak Contoh', '2026-11-01', iso, true);
ok('12: catatan rusak (nota tanpa kg): buku mesin tidak terbaca → kartu bilang TIDAK MENUTUP, jangan dipakai', !KX.menutup && /TIDAK MENUTUP/.test(KX.kalimat), J([KX.sisaAkhir, KX.mesin, KX.kalimat]));

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
})();
"""
PEMBANTU = r"""
var KUNCI5 = 'Angsa|5';
function sgTambah(iso, n) { var d = new Date(iso + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); }
"""

STATIS = [
    ('Stok: kartu stok per merek (owner) + tab Produksi + opname kejutan owner saja', 'stok', ["import * as SG from './stok-pantau-logika.js';", "s.lembar === 'kartu' ? gambarKartuStok(s)", "s.tab === 'produksi' ? gambarProduksi(s, k)",
        "function gambarKartuStok(s)", "SG.sgKartuStok(kunci, dari, iso, !!s.ksRinci)", "function gambarProduksi(s, k)", "SG.sgRencanaProduksi(k)", "${bukanOwner(opsi.akun ? opsi.akun() : null) ? '' : gambarKejutan(s)}",
        "${bukanOwner(ak) ? '' : h`<div class=\"tombol-baris\" data-k=\"tombol-kartu\"><div class=\"kaca-btn\" data-aksi=\"bukaKartu\">Kartu stok</div></div>`}", "crypto.getRandomValues(b)"]),
    ('Stok › Cocokkan: dihitung oleh / didampingi / hama', 'stok', ["{ dihitungOleh: c.dihitungOleh, didampingi: c.didampingi, hama: c.hama }", 'data-ketik="cOrang"', 'data-aksi="cHama"', "S.UM_HAMA.map("]),
    ('Stok › Adukan: sampel isi + oplos ditahan', 'stok', ['data-kolom="sampelUnit"', 'data-kolom="sampelKg"', "ha.kelas.status === 'oplos'", 'data-kolom="alasanOplos"', "ha.lebihBerat"]),
    ('Stok › Umur: batas simpan di Atur', 'stok', ["isian('umBatasSimpan', 'batasSimpanHari'", "batasSimpanHari: String(a.batasSimpanHari)"]),
    ('Laporan: barang masuk di Harian + WA, hitung karung di Mingguan', 'laporan', ["import * as SG from './stok-pantau-logika.js';", "kartuMasukHari(SG.sgMasukHari(t))", "LP.teksRekapHari(R, D.kop, SG.sgMasukHari(t).teks)", "kartuHitungMinggu(SG.sgHitungMinggu(awal, kini()), s)"]),
    ('Harga › Belanja: rencana beli bulan depan', 'harga', ["import * as SG from './stok-pantau-logika.js';", "${gambarRencanaBulan(s)}", "SG.sgRencanaBeli(kini())", "${R.musim}"]),
    ('app.js: pengingat opname kejutan HANYA owner + lonceng', 'app', ["import { sgSumberPengingat } from './layar/stok-pantau-logika.js';", "if (a.jenis === 'owner') { try { sgSumberPengingat(k)", "LC_JENIS.push('kejutan');"]),
    ('index.html: modul baru ikut pramuat', 'index', ['<link rel="modulepreload" href="js/layar/kelas-het-logika.js">', '<link rel="modulepreload" href="js/layar/stok-pantau-logika.js">']),
    ('pages.yml menjalankan uji ini + kontrol', 'pages', ['python3 alat-uji/uji_stok_p5.py && python3 alat-uji/uji_stok_p5.py --kontrol']),
    ('BACA-DULU: bagian paket P5', 'baca', ['## Paket P5 · Stok, gudang & produksi']),
    ('CSS: kartu stok & merah', 'css', ['.layar-stok .ks-tabel', '.layar-stok .kartu-t.merah']),
]
RUSAK = [
    ('kartu: retur utuh tidak dihitung', SG, "if (r.jenisAsal === 'karung' && r.kondisi === 'utuh' && r.merkSumber && lahir[r.merkSumber])", "if (false)"),
    ('kartu: hitungan / penyesuaian dilewati', SG, "ambilPenyesuaianStok().filter(ok).forEach((o) => { if (!o.merk || !lahir[o.merk]) return;", "ambilPenyesuaianStok().filter(ok).forEach((o) => { if (true) return;"),
    ('kartu: nota buku lahir-adukan ikut dipotong', SG, "if (!SG_JUAL[p.jenis] || !p.merkSumber || !lahir[p.merkSumber]) return;", "if (!SG_JUAL[p.jenis] || !p.merkSumber) return;"),
    ('kartu: adukan jadi karung tidak menambah buku tujuan', SG, "taruh(pr.merkTujuan, { tanggal: pr.tanggal || '', jam: pr.jam || '', id: pr.id, jenis: 'karung', kg,", "taruh(pr.merkTujuan, { tanggal: pr.tanggal || '', jam: pr.jam || '', id: pr.id, jenis: 'karung', kg: 0,"),
    ('kartu: nota tidak digabung per hari', SG, "const k = r.tanggal + '|' + r.jalur;", "const k = r.id;"),
    ('kartu: penjaga menutup selalu benar', SG, "const menutup = mesin === null ? !semua.length : beda < 0.0101;", "const menutup = true;"),
    ('masuk hari: buku lahir ikut kedatangan', SG, "const sgKedatanganSungguhan = (b) => !!b && !b.lahirBuku && !b.stokAwal && !b.tutupBuku;", "const sgKedatanganSungguhan = (b) => !!b;"),
    ('teks WA: baris barang masuk tidak ditulis', LPL, "if (masuk) b.push(String(masuk));", ""),
    ('hitung minggu: timbang tutup hari ikut', SG, "hitunganFisik(d) && !d.dariTutup && d.bagian !== 'wadah'", "hitunganFisik(d) && d.bagian !== 'wadah'"),
    ('hitung minggu: Senin salah hari', SG, "return sgIso(n - (((n + 3) % 7) + 7) % 7);", "return sgIso(n - (((n + 4) % 7) + 7) % 7);"),
    ('kejutan: benih tidak dipakai', SG, "return sgKocok(hari, A.benih + '|' + key)", "return sgKocok(hari, '|' + key)"),
    ('kejutan: tanggal kembar (kocok rusak)', SG, "const j = sgAcak(kunci + '|' + i) % (i + 1);", "const j = 0;"),
    ('kejutan: tenggang 0 hari', SG, "export const SG_KEJUTAN_TENGGANG = 2;", "export const SG_KEJUTAN_TENGGANG = 0;"),
    ('kejutan: benih lama tidak dipertahankan', SG, "const benih = kini.benih && !I.undiUlang ? kini.benih : baru;", "const benih = baru || kini.benih;"),
    ('kejutan: menyala tanpa dinyalakan owner', SG, "aktif: !!d && d.aktif !== false && !!benih,", "aktif: true, benihX: !!benih,"),
    ('kejutan: merek kosong ikut diundi', SG, "const kolam = Object.keys(st).filter((m) => (Number(st[m].sisaKg) || 0) > 0.05).sort();", "const kolam = Object.keys(st).sort();"),
    ('rencana: cadangan hari stok hilang', SG, "const cadangan = laju * A.targetHariMin;", "const cadangan = 0;"),
    ('rencana: pindah buku ke merek lain dihitung pemakaian', SG, "(r.jenis === 'aduk' && (!r.tujuan || !!bw[r.tujuan]))", "r.jenis === 'aduk'"),
    ('rencana: turun tajam tidak dipakai', SG, "lajuAkhir < lajuRata * 0.5 ? 'turun'", "false ? 'turun'"),
    ('rencana: nama berhenti tetap diramal', SG, "const berhenti = bulan.length > 0 && !(perBulan[perBulan.length - 1] > 0.05) && !(ini > 0.05);", "const berhenti = false;"),
    ('pesanan: yang sudah dibayar ikut', SG, "if (!p || !pesananBelumTuntas(p)) return; nPesanan += 1;", "if (!p) return; nPesanan += 1;"),
    ('pesanan: dinilai harga beli terakhir, bukan buku', SG, "(kem ? Number(st.hppRataRataPerUnit) || 0 : Number(st.hppTerakhirPerKg) || 0)", "(kem ? Number(st.hppRataRataPerUnit) || 0 : Number(st.hargaTerakhirPerKg) || 0)"),
    ('produksi: takar ke wadah ikut', SG, "const sgBarisKemas = (pr) => !pr.jadiKarungUtuh && !pr.dariTakar &&", "const sgBarisKemas = (pr) => !pr.jadiKarungUtuh &&"),
    ('produksi: kurang isi tidak ditandai', SG, "kurang: rata < uk - 0.005,", "kurang: rata < uk - 0.5,"),
    ('rencana produksi: bukan rumus Gudang', SG, "const unit = Math.ceil(Math.max(0, b.laju * HARI_TARGET - b.sisa));", "const unit = Math.ceil(Math.max(0, b.laju * 14 - b.sisa));"),
    ('adukan: oplos staf tidak ditahan', AD, "if (bukanOwnerAd) return { tolak: 'DITAHAN", "if (false) return { tolak: 'DITAHAN"),
    ('adukan: oplos owner tanpa alasan lolos', AD, "if (alasanOplos.length < OPLOS_ALASAN_MIN) return", "if (false) return"),
    ('adukan: lebih berat hanya di atas 15 %', AD, "const lebihBerat = kgMasuk > 0 && kgJadi > kgMasuk + 0.0005;", "const lebihBerat = kgMasuk > 0 && kgJadi > kgMasuk * 1.15;"),
    ('adukan: sampel kurang isi tidak ditandai', AD, "S.kurang = S.rata < h.ukuran - SAMPEL_ISI_TOLERANSI_KG;", "S.kurang = false;"),
    ('adukan: sampel tersimpan walau tanpa sampel', AD, "x.sampel && !x.sampel.masalah ? { sampelIsi:", "x.sampel || true ? { sampelIsi:"),
    ('kelas: label owner tidak didahulukan', KH, "const lb = khKelasLabel(x.nama, x.ukuran); const k = lb ? lb.toLowerCase() : khKategori(x.nama, P);", "const lb = ''; const k = lb ? lb.toLowerCase() : khKategori(x.nama, P);"),
    ('kelas: tebakan dipakai jadi satuan', KH, "return asal[m] === 'tebakan' || !k ? m : k;", "return !k ? m : k;"),
    ('cocok: pendamping tidak tersimpan', CC, "K.didampingi ? { didampingi: K.didampingi } : {}", "{}"),
    ('cocok: orang yang sama boleh', CC, "if (oleh && damping && oleh.toLowerCase() === damping.toLowerCase()) return", "if (false) return"),
    ('cocok: hama tidak tersimpan', CC, "K.hama[b.kunci] ? { hama: K.hama[b.kunci] } : {}", "{}"),
    ('umur: bawaan batas simpan 30', SL, "UM_ATUR_BAWAAN.batasSimpanHari = 120;", "UM_ATUR_BAWAAN.batasSimpanHari = 30;"),
    ('umur: batas simpan boleh ≤ ambang', SL, "if (o.batasSimpanHari <= o.ambangUmurHari) return", "if (false) return"),
    ('umur: lewat simpan memakai ambang lambat laku', SL, "const lewatSimpan = umurAcuan !== null && umurAcuan > A.batasSimpanHari;", "const lewatSimpan = umurAcuan !== null && umurAcuan > A.ambangUmurHari;"),
    ('umur: hama "tidak ada" dihitung hama', SL, "ada: d.hama !== 'tidak',", "ada: true,"),
    ('gudang: hama tanpa stok ikut', GD, "H[m].ada && K[m] && (Number(K[m].sisaKg) || 0) > 0.05", "H[m].ada"),
    ('sistem: kejutan tidak diteruskan', SS, "p.jenis === 'minus' || p.jenis === 'kejutan')", "p.jenis === 'minus')"),
    ('sistem: kejutan bawaan ke Ben juga', SS, "minus: ['Owner'], kejutan: ['Owner'] },", "minus: ['Owner'], kejutan: ['Owner', 'Ben'] },"),
    ('dasbor: lewat simpan tidak dibawa ke Mutu', DL, "lewatSimpan: U.lewatSimpan.length, kgLewat: U.kgLewatSimpan, batasSimpan: U.atur.batasSimpanHari,", ""),
    ('dasbor: kartu baru masuk bawaan', WG, "export const WG_BAWAAN = ['kHari', 'kKpi', 'kTren', 'kBulan', 'kWadah', 'kPemicu', 'kTagihan', 'kStok', 'kMutu', 'kPondasi', 'kB2b']", "export const WG_BAWAAN = ['kHari', 'kKpi', 'kTren', 'kBulan', 'kWadah', 'kPemicu', 'kTagihan', 'kStok', 'kMutu', 'kPondasi', 'kB2b', 'kProduksi']"),
]
RUSAK_STATIS = [
    ('opname kejutan tampil untuk staf', 'stok', "${bukanOwner(opsi.akun ? opsi.akun() : null) ? '' : gambarKejutan(s)}", "${gambarKejutan(s)}"),
    ('pengingat kejutan untuk semua akun', 'app', "if (a.jenis === 'owner') { try { sgSumberPengingat(k)", "if (true) { try { sgSumberPengingat(k)"),
    ('rules: staf membaca setelan kejutan', 'rules', "'produkArsip', 'bukuPegangan', 'rutin']", "'produkArsip', 'bukuPegangan', 'rutin', 'opnameKejutan']"),   # v25 (paket P6): daftar baca staf kini berakhir 'rutin'
    ('modul tidak dipramuat', 'index', '<link rel="modulepreload" href="js/layar/stok-pantau-logika.js">', ''),
    ('komentar // menelan kode', 'sg', "export function sgAcak(s) {", "// pengundi\nexport function sgAcak(s) { // FNV; const x = 1;\n"),
    ('modul logika menyentuh DOM', 'kh', "export function khPetaHet() {", "export function khPetaHet() { document.title = '';"),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_stok_p5.py && python3 alat-uji/uji_stok_p5.py --kontrol', 'true'),
]

ASAP = r"""
(function () {
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(Date.now()); var iso = hariIniIso(kini); var out = { akhir: iso, galat: [] };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + e); return null; } };
var D = aman('daftar kartu', function () { return sgDaftarKartu(); }) || []; out.buku = D.length;
out.tidakMenutup = D.filter(function (b) { var K = aman('kartu ' + b.kunci, function () { return sgKartuStok(b.kunci, '2000-01-01', iso, true); }); return !K || !K.menutup; }).length;
out.pembulatan = D.filter(function (b) { var K = sgKartuStok(b.kunci, '2000-01-01', iso, true); return K.pembulatan; }).length;
var hari = []; for (var i = 0; i < 60; i++) { var t = new Date(Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10) - i)).toISOString().slice(0, 10); var M = aman('masuk ' + t, function () { return sgMasukHari(t); }); if (M && M.total.n) hari.push(M.menutup); }
out.hariMasuk = hari.length; out.masukTidakMenutup = hari.filter(function (x) { return !x; }).length;
var HM = aman('minggu', function () { return sgHitungMinggu(iso, kini); }); out.minggu = HM ? { hitungan: HM.total.hitungan, merek: HM.total.merek, belum: HM.total.belum, tanpaPendamping: HM.total.tanpaPendamping } : null;
var RB = aman('rencana', function () { return sgRencanaBeli(kini); }); out.rencana = RB ? { bulan: RB.bulan.map(function (b) { return b.key; }), karung: RB.total.karung, kg: RB.total.kg, merek: RB.total.merek, berhenti: RB.berhenti.length } : null;
var PS = aman('pesanan', function () { return sgPesananRp(kini); }); out.pesanan = PS ? { n: PS.nPesanan, tanpa: PS.nTanpa, kurang: PS.kurang.length } : null;
var PD = aman('produksi', function () { return sgProduksiDeret(kini, 6); }); out.produksi = PD ? PD.map(function (b) { return b.sebelum ? b.key + ' sebelum' : b.key + ' ' + b.adukan + ' adukan · ' + b.kgJadi + ' kg · susut ' + b.susutPersen + '% · menutup ' + b.menutup; }) : null;
out.produksiMenutup = PD ? PD.every(function (b) { return b.sebelum || b.menutup; }) : false;
var RP_ = aman('rencana produksi', function () { return sgRencanaProduksi(kini); }); out.rencanaProduksi = RP_ ? RP_.daftar.length : null;
var U = aman('umur', function () { return umRingkas(kini); }); out.lewatSimpan = U ? U.lewatSimpan.length : null; out.hama = aman('hama', function () { return Object.keys(umHama()).length; });
out.kelasBeda = aman('kelas', function () { return Object.keys(ingatStokKarung()).filter(function (m) { return khKategori(m) !== (hetAtur().peta[hetUnit(m).unit] || ''); }).length; });
out.kejutan = aman('kejutan', function () { return sgKejutanAtur().aktif; });
out.tugas = aman('tugas', function () { var T = gdTugas(kini, { tanggal: iso, jam: '20:00' }); return { baris: T.daftar.length, galat: T.daftar.filter(function (x) { return x.galat; }).map(function (x) { return x.id; }) }; });
var DD = aman('dasbor', function () { return dbTambahan(susunDasbor(kini, 'hari', null, null, dbSaring({ id: 'hari' }, kini)), kini); });
out.dasbor = DD ? { galat: ['masuk', 'pesanan', 'simpan'].filter(function (k) { return DD.gudang5[k] && DD.gudang5[k].galat; }), wg: wgSusun(['kMasukHari', 'kProduksi', 'pesananRp', 'lewatSimpan'].map(function (x) { return { id: x }; }), DD).filter(function (w) { return w.nilai === 'gagal dihitung'; }).map(function (w) { return w.id; }) } : null;
print(JSON.stringify(out));
})();
"""


def bundel_js(teks):
    uji_dasbor_sensus.MODUL[:] = MODUL
    return uji_dasbor_sensus.bundel_js(teks)


def jalan(teks):
    jam = "var __KINI = new Date('2026-11-18T14:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    r, out = uji_dasbor_sensus.jsc(jam + bundel_js(teks) + PEMBANTU + '\nvar KOTAK0 = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar GK = ' + json.dumps(KOTAK) + ';\nvar ATUR = ' + json.dumps(ATUR) + ';\n' + SKENARIO)
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], list(h['gagal'])


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    # satu-satunya pintu tulis baru = setelan owner aturanToko/opnameKejutan; staf TIDAK bisa membacanya (rules aturanToko read = daftar id)
    t = src['sg']; tulis = re.findall(r"koleksi: '(\w+)'", t)
    if tulis != ['aturanToko'] or "id: SG_KEJUTAN_ID" not in t: g.append('stok-pantau-logika: menulis selain setelan aturanToko/opnameKejutan → ' + str(tulis))
    if 'koleksi:' in src['kh'] or 'dokumen:' in src['kh']: g.append('kelas-het-logika menulis dokumen (harus baca saja)')
    m = re.search(r"match /aturanToko/\{id\} \{\s*allow read: if ([^\n]*)", src['rules'])
    if not m or 'opnameKejutan' in m.group(1): g.append('rules: setelan opname kejutan terbaca staf (atau aturan aturanToko tidak ketemu)')
    for k in ('sg', 'kh'):
        if 'document.' in src[k] or 'tulisDokumen' in src[k]: g.append(k + ': modul logika menyentuh DOM / menulis langsung')
    for k in ('sg', 'kh', 'stok', 'laporan', 'harga', 'ad', 'cc', 'sl', 'gd', 'dl', 'wg'):
        for n, baris in enumerate(src[k].split('\n')):
            ekor = uji_sisa_sensus.komentar_ekor(baris)
            if ekor and re.search(r"\b[a-zA-Z]\w*: (opsi\.|\(|async |\[|\{|'|`)|;\s*(const|let|return|if)\b|\)\s*=>", ekor): g.append(k + ':' + str(n + 1) + ': komentar // menelan kode → ' + ekor.strip()[:90])
    # mesin beku & pembantu tidak disentuh (aturan tetap owner): dijaga alat-uji/beku2.py (sha256 tubuh mesin) di pages.yml — paket ini tidak mengubah keduanya
    i = src['baca'].find('## Paket P5')
    if i >= 0 and ('rules v25' in src['baca'][i:i + 8000]): g.append('BACA-DULU menyebut rules baru untuk paket ini (paket ini tanpa rules)')
    return len(STATIS) - len([x for x in g if ' → tidak ketemu' in x]), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read() if os.path.exists(os.path.join(AKAR, v)) else '') for k, v in SUMBER.items())


if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama + ' (' + str(teks[berkas].count(a)) + '×)'); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b)
            l, g = jalan(T)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_STATIS:
            if src[berkas].count(a) < 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            S = dict(src); S[berkas] = S[berkas].replace(a, b, 1); l, g = statis(S)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = jalan(teks); ls, gs = statis(src)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '..', '..', '..', '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and '--tanpa-asap' not in sys.argv:
        tgl = os.path.basename(cad[-1]).split('miqbal-')[-1][:10]
        r, out = uji_dasbor_sensus.jsc("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + bundel_js(teks) + PEMBANTU + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if r.returncode != 0 or not out.startswith('{'): print('ASAP DATA TOKO: JSC JATUH ' + (r.stderr or r.stdout)[-600:]); g.append('asap')
        else:
            h = json.loads(out)
            beres = (not h['galat'] and h['tidakMenutup'] == 0 and h['masukTidakMenutup'] == 0 and h['produksiMenutup'] and h['kelasBeda'] == 0 and h['minggu'] is not None and h['rencana'] is not None
                     and h['tugas'] and not h['tugas']['galat'] and h['dasbor'] and not h['dasbor']['galat'] and not h['dasbor']['wg'])
            # angka RUPIAH toko TIDAK dicetak (repo publik) — hanya keadaan, jumlah, kg
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: kartu stok / barang masuk / produksi tidak menutup ke sumbernya, kelas ≠ HET, atau Dasbor galat')
    sys.exit(1 if g or gs else 0)
