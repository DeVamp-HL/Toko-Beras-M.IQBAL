#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_pelanggan_het_p7.py — PAKET P7 · Pelanggan & HET (owner 27 Nov 2026; sensus ulang 27 Nov: A15 A108 A132 B18).
KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  A15   harga per kg baris beras di keranjang / nota / lembar nego vs HET — CUMA DITANDAI (keputusan owner): satu sumber dengan Harga › HET (hetAtur · hetUnit ·
        hetNilai), harga sesudah harga pelanggan & nego, kemasan berbonus = unit dibayar, literan ÷ kg per liter nota, buku per ukuran ikut merek induk,
        literan wadah campuran = satu baris; wadah & pengganti retur tidak dinilai; nota nominal / lama = "tidak bisa dinilai"; belum dipetakan BUKAN patuh.
  A132  rekap kepatuhan HET per minggu (Senin–Minggu) + riwayat 8 minggu: Σ status = semua baris beras, kg & rupiah di atas HET, per merek.
  A108  usul batas bon bulanan: NAIK (3 bon tepat waktu & pernah ≥ 80 % batas) · TURUN (2 dari 3 telat) · HENTI (stop bon / macet) · TETAP; angka = setelan
        owner (bawaan disebut); "Pakai usul" menulis kartu (batas owner / bonDihentikan) + jejak; HENTI menahan bon baru (kunciKr1), owner membuka lagi.
  B18   halaman per pelanggan: nota terakhir, belanja per bulan & tahun, pesanan & order rutin terbuka, bon, laba (owner saja — staf tidak menerima angka
        laba sama sekali). Belanja & laba per bulan = aturan Laporan › Laba › Per pelanggan: tiap bulan SAMA PERSIS dengan pelangganBulan(bulan, 1).

    python3 alat-uji/uji_pelanggan_het_p7.py            → N lulus · 0 gagal (+ asap cadangan toko bila ada; angka rupiah toko tidak dicetak)
    python3 alat-uji/uji_pelanggan_het_p7.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_jual_baru, uji_dasbor_sensus, uji_sisa_sensus  # noqa: E402
HJ = 'baru/js/layar/het-jual-logika.js'; UL = 'baru/js/layar/usul-bon-logika.js'; HN = 'baru/js/layar/halaman-pelanggan-logika.js'
PG = 'baru/js/layar/laba-pelanggan-logika.js'; FK = 'baru/js/layar/faktur-logika.js'; JL = 'baru/js/layar/jual-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_dasbor_sensus.MODUL + [HJ, UL, HN])))
SUMBER = {'jual': 'baru/js/layar/jual.js', 'pelanggan': 'baru/js/layar/pelanggan.js', 'laporan': 'baru/js/layar/laporan.js', 'css': 'baru/css/pelanggan.css',
          'index': 'baru/index.html', 'rules': 'firestore.rules', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md',
          'hj': HJ, 'ul': UL, 'hn': HN, 'pg': PG, 'fk': FK, 'jl': JL}


def JUAL(i, tgl, jenis, merk, harga, total, **x):
    d = {'id': i, 'tanggal': tgl, 'jam': '09:00', 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': jenis, 'merkSumber': merk, 'grupNota': 'g' + i,
         'hargaTotal': total, 'hppTotalSaatJual': round(total * 0.9)}
    if harga is not None: d['hargaAsliSatuan'] = harga
    d.update(x); return d
def BON(i, tgl, nama, total, cara='Kredit', **x):
    d = {'id': i, 'tanggal': tgl, 'jam': '10:00', 'caraBayar': cara, 'namaPelanggan': nama, 'jenis': 'karung', 'merkSumber': 'Pelita', 'beratKarungAcuan': 50,
         'jumlahKarung': 1, 'totalKg': 50, 'hargaAsliSatuan': total, 'hargaTotal': total, 'hppTotalSaatJual': round(total * 0.9), 'grupNota': 'g' + i}
    d.update(x); return d
def BAYAR(i, tgl, nama, n): return {'id': i, 'tanggal': tgl, 'jam': '11:00', 'namaPelanggan': nama, 'tipe': 'bayar', 'nominal': n, 'caraBayar': 'Tunai'}

KOTAK = {
    'batchMasuk': [{'id': 'b1', 'tanggal': '2026-08-01', 'jam': '07:00', 'pemasok': 'Pemasok Contoh', 'caraBayar': 'Tunai', 'biayaBongkar': 0, 'merkList': [
        {'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 40, 'totalKg': 2000, 'subtotalHarga': 24000000, 'hargaPerKg': 12000},
        {'merk': 'Angsa 25 kg', 'indukUkuran': 'Angsa', 'satuan': 'karung', 'beratKarung': 25, 'jumlahKarung': 20, 'totalKg': 500, 'subtotalHarga': 6000000, 'hargaPerKg': 12000},
        {'merk': 'Pelita', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 40, 'totalKg': 2000, 'subtotalHarga': 22000000, 'hargaPerKg': 11000}]}],
    'penjualan': [
        # ---- minggu 16–22 Nov (HET)
        JUAL('h1', '2026-11-16', 'karung', 'Angsa', 700000, 700000, beratKarungAcuan=50, jumlahKarung=1, totalKg=50),
        JUAL('h2', '2026-11-16', 'karung', 'Angsa', 650000, 650000, beratKarungAcuan=50, jumlahKarung=1, totalKg=50),
        JUAL('h3', '2026-11-17', 'kemasan', '', 70000, 152000, namaProduk='Kembang', ukuranKemasan=5, jumlahUnit=3, bonusUnit=1, totalKg=15, negoSelisih=6000),
        JUAL('h4a', '2026-11-17', 'literan', 'Angsa', 11500, 34500, dariWadah='Angsa', rasioPakai=0.82, jumlahLiter=3, totalKg=2.46, takaranId='h4a', grupNota='gh4'),
        JUAL('h4b', '2026-11-17', 'literan', 'Pelita', 11500, 23000, dariWadah='Angsa', rasioPakai=0.82, jumlahLiter=2, totalKg=1.64, takaranId='h4a', grupNota='gh4'),
        JUAL('h5', '2026-11-17', 'karung', 'Angsa 25 kg', 325000, 325000, beratKarungAcuan=25, jumlahKarung=1, totalKg=25),
        JUAL('h6', '2026-11-18', 'karung', 'Pelita', 700000, 700000, beratKarungAcuan=50, jumlahKarung=1, totalKg=50),
        JUAL('h7', '2026-11-18', 'literan', 'Ketan Contoh', 20000, 100000, rasioPakai=0.8, jumlahLiter=5, totalKg=4),
        JUAL('h8', '2026-11-18', 'kasir_darurat_nominal', '', None, 50000),
        JUAL('h9', '2026-11-18', 'karung', 'Angsa', None, 720000, beratKarungAcuan=50, jumlahKarung=1, totalKg=50),
        JUAL('h10', '2026-11-18', 'wadah', '', 500, 500, jenisWadah='kantong', jumlahUnit=1),
        JUAL('h11', '2026-11-18', 'karung', 'Angsa', 900000, 0, beratKarungAcuan=50, jumlahKarung=1, totalKg=50, penggantiRetur=True, nilaiBarangPengganti=900000),
        JUAL('h12', '2026-11-18', 'repacking', 'Angsa', 14500, 29000, totalKg=2, namaProduk='Angsa'),
        # ---- minggu 9–15 Nov
        JUAL('h13', '2026-11-10', 'karung', 'Angsa', 720000, 720000, beratKarungAcuan=50, jumlahKarung=1, totalKg=50),
        # ---- buku bon (A108 · B18) — merek Pelita (belum dipetakan) supaya tidak mengubah hitungan HET minggu di atas
        BON('n1', '2026-08-25', 'Bu Naik', 300000), BON('n2', '2026-09-20', 'Bu Naik', 400000), BON('n3', '2026-10-20', 'Bu Naik', 850000),
        BON('n4', '2026-11-03', 'Bu Naik', 650000, cara='Tunai', grupNota='gn4'),
        JUAL('n5', '2026-11-03', 'kemasan', '', 70000, 140000, namaProduk='Kembang', ukuranKemasan=5, jumlahUnit=2, totalKg=10, namaPelanggan='Bu Naik', grupNota='gn4'),
        BON('t1', '2026-08-20', 'Pak Turun', 200000), BON('t2', '2026-09-25', 'Pak Turun', 200000), BON('t3', '2026-11-01', 'Pak Turun', 130000),
        BON('s1', '2026-09-10', 'Bu Henti', 250000),
        BON('p1', '2026-11-02', 'Pak Baru', 100000),
        BON('d1', '2026-10-01', 'Bu Stop', 100000),
        BON('q1', '2026-09-01', 'Bu Tepat', 100000), BON('q2', '2026-10-01', 'Bu Tepat', 150000), BON('q3', '2026-11-01', 'Bu Tepat', 200000),
        BON('x1', '2026-08-25', 'Pak Sekali', 100000), BON('x2', '2026-10-05', 'Pak Sekali', 100000), BON('x3', '2026-11-03', 'Pak Sekali', 100000),
    ],
    'piutangMutasi': [BAYAR('m1', '2026-08-28', 'Bu Naik', 300000), BAYAR('m2', '2026-09-25', 'Bu Naik', 400000), BAYAR('m3', '2026-10-25', 'Bu Naik', 850000),
                      BAYAR('m4', '2026-09-20', 'Pak Turun', 200000), BAYAR('m5', '2026-10-30', 'Pak Turun', 200000), BAYAR('m6', '2026-11-05', 'Pak Turun', 130000),
                      BAYAR('m7', '2026-11-04', 'Pak Baru', 100000), BAYAR('m8', '2026-10-02', 'Bu Stop', 100000),
                      BAYAR('q4', '2026-09-03', 'Bu Tepat', 100000), BAYAR('q5', '2026-10-02', 'Bu Tepat', 150000), BAYAR('q6', '2026-11-02', 'Bu Tepat', 200000),
                      BAYAR('x4', '2026-09-30', 'Pak Sekali', 100000), BAYAR('x5', '2026-10-06', 'Pak Sekali', 100000), BAYAR('x6', '2026-11-04', 'Pak Sekali', 100000)],
    'retur': [{'id': 'r1', 'tanggal': '2026-11-05', 'jam': '10:00', 'jenisAsal': 'karung', 'merkSumber': 'Pelita', 'namaProduk': 'Pelita', 'totalKg': 50, 'kondisi': 'utuh',
               'nominalRefund': 650000, 'notaAsalId': 'n4', 'namaPelanggan': ''}],
    'pesanan': [{'id': 'o1', 'tanggal': '2026-11-15', 'jam': '09:00', 'namaPelanggan': 'Bu Naik', 'status': 'dipesan', 'tanggalKirim': '2026-11-20', 'nilaiPerkiraan': 500000, 'isi': 'Angsa 1 karung'},
                {'id': 'o2', 'tanggal': '2026-11-10', 'jam': '09:00', 'namaPelanggan': 'Bu Naik', 'status': 'dibayar', 'nilaiPerkiraan': 300000, 'isi': 'Pelita 1 karung'},
                {'id': 'o3', 'tanggal': '2026-11-12', 'jam': '09:00', 'namaPelanggan': 'Pak Turun', 'status': 'dipesan', 'nilaiPerkiraan': 200000, 'isi': 'Pelita 1 karung'}],
    'orderRutin': [{'id': 'j1', 'namaPelanggan': 'Bu Naik', 'ulang': 'mingguan', 'hari': 1, 'mulai': '2026-11-01', 'aktif': True, 'isi': 'Angsa 1 karung'}],
}
KARTU = [{'nama': 'Bu Naik', 'catatan': 'warung sebelah', 'batasKredit': 1000000}, {'nama': 'Pak Turun', 'catatan': 'ojek'}, {'nama': 'Bu Henti', 'catatan': 'pasar'},
         {'nama': 'Pak Baru', 'catatan': 'baru'}, {'nama': 'Bu Tepat', 'catatan': 'tepat', 'batasKredit': 1000000}, {'nama': 'Pak Sekali', 'catatan': 'sekali telat'}, {'nama': 'Bu Stop', 'catatan': 'contoh', 'bonDihentikan': {'tanggal': '2026-11-01', 'jam': '10:00', 'alasan': 'contoh henti'}}]
ATUR = [{'id': 'het', 'peta': {'Angsa': 'medium', 'Kembang': 'premium', 'Ketan Contoh': 'bukan'}, 'medium': 13500, 'premium': 14900, 'zona': 'Zona I', 'sumber': 'contoh', 'angkaTanggal': '2026-11-01'}]

SKENARIO = r"""
(function () {
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); }; var dekat = function (a, b, t) { return a !== null && b !== null && a !== undefined && b !== undefined && Math.abs(a - b) < (t || 0.005); };
var KINI = new Date('2026-11-18T14:00:00+07:00'); var nId = 90000; var iso = '2026-11-18';
var W = { tanggal: '2026-11-18', jam: '14:00', kini: '2026-11-18T07:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK0).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'penyesuaianStok', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'stokBahanKemasan', 'pesanan', 'orderRutin', 'karantina', 'persetujuan', 'pengeluaranHarian', 'tagih'].forEach(function (n) { pasok(n, []); });
Object.keys(GK).forEach(function (n) { pasok(n, JSON.parse(J(GK[n]))); });
var kartuAwal = KARTU.map(function (c) { return Object.assign({ id: kunciPelanggan(c.nama) }, JSON.parse(J(c))); }); pasok('pelangganCatatan', kartuAwal);
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-07-01', laci: 1000000, brankas: 0, rekening: 0, amplop: 0, diubahPada: '2026-07-01T14:00:00.000Z' }]);
setelSumber('cadangan', 'kotak pasir');
var aturDengan = function (extra) { var e = extra || []; var id = {}; e.forEach(function (d) { id[d.id] = 1; }); pasok('aturanToko', JSON.parse(J(ATUR)).filter(function (d) { return !id[d.id]; }).concat(e)); };
aturDengan([]);
var k = function (n) { return kunciPelanggan(n); };

// ==================== 1 · HET PER BARIS (A15) ====================
var P = {}; ambilPenjualan().forEach(function (p) { P[p.id] = p; });
var v1 = hjNilaiBaris(P.h1), v3 = hjNilaiBaris(P.h3), v4 = hjNilaiBaris(P.h4b), v5 = hjNilaiBaris(P.h5), v12 = hjNilaiBaris(P.h12);
ok('1: karung Angsa Rp700.000/50 kg = Rp14.000/kg > HET medium Rp13.500 → di atas, lebih Rp500/kg × 50 kg = Rp25.000', v1.status === 'atas' && v1.perKg === 14000 && v1.het === 13500 && v1.kg === 50 && v1.rpLebih === 25000 && v1.kategori === 'medium', J(v1));
ok('1: SATU sumber dengan Harga › HET: status & teks = hetNilai(perKg, peta[hetUnit(merek)])', v1.teks === hetNilai(14000, hetAtur().peta[hetUnit('Angsa').unit], hetAtur()).teks && hjNilaiBaris(P.h2).status === 'dalam', J([v1.teks, hjNilaiBaris(P.h2)]));
ok('1: kemasan berbonus + nego naik: (Rp70.000 + Rp6.000)/5 kg = Rp15.200 > premium Rp14.900; kg dibayar 2 × 5 (bonus tidak) → Rp3.000', v3.status === 'atas' && v3.perKg === 15200 && v3.kg === 10 && dekat(v3.rpLebih, 3000), J(v3));
ok('1: literan wadah: merek = nama WADAH (dariWadah), bukan merek asal; ÷ kg per liter nota 0,82', v4.status === 'atas' && v4.merk === 'Angsa' && dekat(v4.perKg, 11500 / 0.82) && dekat(v4.kg, 1.64), J(v4));
ok('1: buku per ukuran "Angsa 25 kg" ikut kelas merek induk (Angsa · medium): Rp325.000/25 kg = Rp13.000 → sama/di bawah', v5.status === 'dalam' && v5.merk === 'Angsa' && v5.perKg === 13000, J(v5));
ok('1: repack per kg Rp14.500 > Rp13.500 → lebih Rp1.000 × 2 kg', v12.status === 'atas' && v12.rpLebih === 2000, J(v12));
ok('1: belum dipetakan (Pelita) = "belum", BUKAN dalam; bukan beras HET (ketan) = "bukan"', hjNilaiBaris(P.h6).status === 'belum' && hjNilaiBaris(P.h7).status === 'bukan', J([hjNilaiBaris(P.h6), hjNilaiBaris(P.h7)]));
ok('1: nota nominal & nota lama tanpa harga satuan = tidak bisa dinilai (sebabnya disebut); wadah & pengganti retur tidak dinilai sama sekali',
  hjNilaiBaris(P.h8).status === 'takBisa' && /nominal/.test(hjNilaiBaris(P.h8).sebab) && hjNilaiBaris(P.h9).status === 'takBisa' && /lama/.test(hjNilaiBaris(P.h9).sebab) && hjNilaiBaris(P.h10) === null && hjNilaiBaris(P.h11) === null,
  J([hjNilaiBaris(P.h8), hjNilaiBaris(P.h9), hjNilaiBaris(P.h10), hjNilaiBaris(P.h11)]));
// keranjang & lembar nego
var KR = [{ id: 1, trx: { jenis: 'karung', merkSumber: 'Angsa', beratKarungAcuan: 50, jumlah: 2, hargaSatuan: 700000, label: 'Angsa 50 kg' } },
  { id: 2, trx: { jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlah: 2, bonusUnit: 1, hargaSatuan: 70000, label: 'Kembang 5 kg' } },
  { id: 3, trx: { jenis: 'wadah', jenisWadah: 'kantong', jumlah: 1, hargaSatuan: 500, label: 'Kantong' } }];
var K1 = hjKeranjang(KR);
ok('1: Bayar: 1 dari 2 baris beras di atas HET (wadah tidak dihitung); kalimat menyebut harga/kg, HET & selisihnya; nota tetap boleh dicatat',
  K1.nAtas === 1 && K1.nBeras === 2 && K1.keadaan === 'atas' && /Angsa 50 kg Rp14\.000\/kg \(HET medium Rp13\.500, \+Rp500\/kg\)/.test(K1.teks) && /tetap boleh dicatat/.test(K1.teks) && dekat(K1.atas[0].nilai.rpLebih, 50000), J(K1));
var n1 = hjSatuHarga(KR[1].trx, 76000), n2 = hjSatuHarga(KR[0].trx, 675000);
ok('1: lembar nego: harga yang diketik dinilai (Rp76.000 kemasan 5 kg = Rp15.200 di atas premium; Rp675.000 karung = tepat HET → bukan di atas)', n1.status === 'atas' && n2.status === 'dalam' && /tepat HET/.test(n2.teks), J([n1, n2]));
var K2 = hjKeranjang([{ id: 9, trx: { jenis: 'karung', merkSumber: 'Pelita', beratKarungAcuan: 50, jumlah: 1, hargaSatuan: 900000, label: 'Pelita 50 kg' } }]);
ok('1: keranjang yang kelasnya belum dipetakan: disebut "belum dipetakan", tidak dianggap aman', K2.keadaan === 'belum' && /Pelita belum dipetakan/.test(K2.teks) && K2.nAtas === 0, J(K2));

// ==================== 2 · REKAP MINGGU (A132) ====================
var M = hjMinggu('2026-11-18');
ok('2: minggu Senin 16 Nov: 10 baris beras (literan wadah campuran = 1 baris) = 4 di atas · 2 sama/di bawah · 1 belum dipetakan · 1 bukan HET · 2 tidak bisa dinilai',
  M.awal === '2026-11-16' && M.akhir === '2026-11-22' && M.nBaris === 10 && J(M.hit) === J({ atas: 4, dalam: 2, belum: 1, bukan: 1, takBisa: 2 }) && M.nDinilai === 6 && M.menutup, J([M.awal, M.nBaris, M.hit]));
ok('2: kg & rupiah di atas HET: 50 + 10 + 4,1 + 2 = 66,1 kg · Rp25.000 + Rp3.000 + Rp2.150 + Rp2.000 = Rp32.150 · 4 nota', dekat(M.kgAtas, 66.1) && dekat(M.rpLebih, 32150, 0.01) && M.nNotaAtas === 4, J([M.kgAtas, M.rpLebih, M.nNotaAtas]));
ok('2: per merek (rupiah terbesar dulu): Angsa 3 baris Rp29.150 (paling mahal Rp14.500/kg) · Kembang 1 baris Rp3.000', M.merek.length === 2 && M.merek[0].merk === 'Angsa' && M.merek[0].n === 3 && dekat(M.merek[0].rpLebih, 29150, 0.01) && M.merek[0].perKgMaks === 14500 && M.merek[1].merk === 'Kembang', J(M.merek));
ok('2: keadaan "sebagian": judul menyebut 4 baris di atas HET (4 nota) + 1 baris belum dipetakan; tidak bisa dinilai disebut sebabnya',
  M.keadaan === 'sebagian' && /4 baris di atas HET \(4 nota\)/.test(M.judul) && /1 baris kelasnya belum dipetakan/.test(M.judul) && M.unitBelum[0] === 'Pelita' && M.takBisa['nota nominal (tanpa barang)'] === 1 && M.takBisa['nota lama tanpa harga satuan'] === 1, J([M.judul, M.unitBelum, M.takBisa]));
var R = hjRiwayat('2026-11-18', 8);
ok('2: riwayat 8 minggu (Senin), terbaru di belakang: 9 Nov 1 di atas HET (lengkap) · 16 Nov 4; minggu lain yang hanya punya Pelita = belum dipetakan',
  R.length === 8 && R[7].awal === '2026-11-16' && R[7].nAtas === 4 && R[6].awal === '2026-11-09' && R[6].nAtas === 1 && R[6].keadaan === 'lengkap' && R[0].awal === '2026-09-28' && R[7].terakhir
  && R.filter(function (r) { return r.keadaan === 'belum'; }).length >= 2 && /4 di atas HET/.test(hjRiwayatTeks(R[7])), J(R));
aturDengan([{ id: 'het', peta: {} }]);
var M0 = hjMinggu('2026-11-18');
ok('2: peta kelas KOSONG (keadaan data toko 25 Nov): keadaan "belum", "BUKAN berarti patuh", 8 baris belum dipetakan (ketan pun), tidak ada yang dihitung patuh', M0.keadaan === 'belum' && /BUKAN berarti patuh/.test(M0.judul) && M0.hit.dalam === 0 && M0.hit.atas === 0 && M0.hit.bukan === 0 && M0.hit.belum === 8, J([M0.judul, M0.hit]));
aturDengan([]);

// ==================== 3 · USUL BATAS BON (A108) ====================
var D = ulDaftar(KINI); var cari = function (nm) { return D.daftar.find(function (o) { return o.nama === nm; }) || null; };
var A = ulAtur();
ok('3: aturan bawaan (belum diatur owner): 3 bulan · naik 25 % bila ≥ 80 % batas · turun 25 % · dibulatkan Rp10.000', !A.dariOwner && A.bulan === 3 && A.naikPersen === 25 && A.ambangPakaiPersen === 80 && A.turunPersen === 25 && A.langkah === 10000, J(A));
var oN = cari('Bu Naik'), oT = cari('Pak Turun'), oH = cari('Bu Henti'), oB = cari('Pak Baru'), oS = cari('Bu Stop'), oQ = cari('Bu Tepat'), oX = cari('Pak Sekali');
ok('3: TETAP: tepat waktu tapi pemakaian tertinggi cuma 20 % batas (aturan ≥ 80 %) · 1 dari 3 telat (aturan turun ≥ 2) — tidak diusulkan apa-apa',
  oQ && oQ.usul === 'tetap' && Math.round(oQ.pakai) === 20 && /bayar tepat waktu/.test(oQ.alasan) && oX && oX.usul === 'tetap' && oX.kebiasaan.nTelat === 1 && /belum sampai 2 dari 3/.test(oX.alasan), J([oQ, oX]));
ok('3: NAIK: 3 bon terakhir lunas tepat waktu + sisa bon pernah Rp850.000 = 85 % batas owner Rp1.000.000 → Rp1.250.000', oN && oN.usul === 'naik' && oN.batas === 1000000 && oN.sumber === 'owner' && oN.puncak === 850000 && Math.round(oN.pakai) === 85 && oN.ke === 1250000, J(oN));
ok('3: TURUN: 2 dari 3 bon terakhir lunas lewat jatuh tempo; batas rumus 2× rata belanja 90 hari = Rp220.000 → × 75 % = Rp165.000 → Rp160.000 (dibulatkan ke BAWAH) + catatan batas rumus jadi angka owner',
  oT && oT.usul === 'turun' && oT.batas === 220000 && oT.sumber === 'rumus' && oT.ke === 160000 && oT.kebiasaan.nTelat === 2 && /angka owner/.test(oT.catatan.join(' ')), J(oT));
ok('3: HENTI: bon tertua belum lunas sejak 10 Sep (> batas stop bon bawaan 30 hari)', oH && oH.usul === 'henti' && !!oH.stop && /stop bon 30 hari/.test(oH.alasan), J(oH));
ok('3: TETAP + riwayat belum cukup (1 bon lunas) · sedang DIHENTIKAN = baris sendiri', oB && oB.usul === 'tetap' && oB.kurangRiwayat && /riwayat bayar belum cukup/.test(oB.alasan) && oS && oS.usul === 'dihentikan', J([oB, oS]));
ok('3: urutan henti · turun · naik · dihentikan · tetap; kalimat: 3 usul, tidak ada yang berubah sendiri', D.daftar.map(function (o) { return o.usul; }).join(',') === 'henti,turun,naik,dihentikan,tetap,tetap,tetap' && J(D.hit) === J({ naik: 1, turun: 1, henti: 1, tetap: 3, dihentikan: 1 }) && /3 usul bulan ini/.test(D.kalimat) && /tidak ada yang berubah/.test(D.kalimat), J([D.hit, D.kalimat]));
// bon dihentikan menahan KR1; pintu owner tetap ada
ok('3: kartu bonDihentikan → kasir menahan bon baru (kunciKr1) dengan kalimat; owner membuka sekali (kreditDibuka) tetap bisa; orang lain tidak kena', /DIHENTIKAN owner sejak 1 Nov 2026/.test(kunciKr1('Bu Stop', 1000) || '') && alasanKunciKredit({ pelanggan: 'Bu Stop', kreditDibuka: true }, 1000) === null && kunciKr1('Bu Naik', 1000) === null,
  J([kunciKr1('Bu Stop', 1000), kunciKr1('Bu Naik', 1000)]));
// pakai usul
var pN = ulSusunPakai(KINI, k('Bu Naik'), W); var dN = pN.dokumen && pN.dokumen[0];
ok('3: Pakai usul NAIK → satu dokumen kartu (pelangganCatatan): batas Rp1.250.000 + jejak usulBon; isi kartu lama (catatan) utuh', dN && dN.koleksi === 'pelangganCatatan' && pN.dokumen.length === 1 && dN.data.batasKredit === 1250000 && dN.data.catatan === 'warung sebelah' && dN.data.usulBon.jenis === 'naik' && dN.data.usulBon.dari === 1000000 && dN.data.usulBon.bulan === '2026-11' && !dN.data.bonDihentikan, J(pN));
var pH = ulSusunPakai(KINI, k('Bu Henti'), W); var dH = pH.dokumen && pH.dokumen[0].data;
ok('3: Pakai usul HENTI → bonDihentikan bertanggal hari ini, batas tidak disentuh', dH && dH.bonDihentikan && dH.bonDihentikan.tanggal === '2026-11-18' && dH.batasKredit === undefined && dH.usulBon.jenis === 'henti', J(pH));
ok('3: orang tanpa usul / tidak di daftar = ditolak dengan kalimat', /tidak ada usul/.test(ulSusunPakai(KINI, k('Pak Baru'), W).tolak || '') && /tidak ada di daftar/.test(ulSusunPakai(KINI, 'orang lain', W).tolak || ''), '');
var pT = ulSusunPakai(KINI, k('Pak Turun'), W);
pasok('pelangganCatatan', kartuAwal.filter(function (c) { return c.id !== k('Pak Turun') && c.id !== k('Bu Henti'); }).concat(pT.dokumen ? [pT.dokumen[0].data] : []).concat(dH ? [dH] : []));
var D2 = ulDaftar(KINI); var oT2 = D2.daftar.find(function (o) { return o.nama === 'Pak Turun'; }); var oH2 = D2.daftar.find(function (o) { return o.nama === 'Bu Henti'; });
ok('3: sesudah dipakai: Pak Turun batas owner Rp160.000, usul turun yang sama = "sudah dipakai bulan ini" (tidak bisa dipakai dua kali); Bu Henti jadi "dihentikan" & bon barunya ditahan',
  oT2 && oT2.sumber === 'owner' && oT2.batas === 160000 && oT2.usul === 'turun' && oT2.sudah && /sudah dipakai/.test(ulSusunPakai(KINI, k('Pak Turun'), W).tolak || '') && oH2 && oH2.usul === 'dihentikan' && /DIHENTIKAN/.test(kunciKr1('Bu Henti', 1000) || ''), J([oT2, oH2]));
var bk = ulSusunBuka(k('Bu Henti'), W); var dB = bk.dokumen && bk.dokumen[0].data;
ok('3: Buka lagi (owner) → bonDihentikan dihapus, hentiDibuka mencatat kapan; yang tidak dihentikan = ditolak', dB && dB.bonDihentikan === undefined && dB.hentiDibuka.sejak === '2026-11-18' && /tidak sedang dihentikan/.test(ulSusunBuka(k('Pak Baru'), W).tolak || ''), J(bk));
pasok('pelangganCatatan', kartuAwal);
// setelan owner
ok('3: atur: periode 13 bulan / naik 0 % ditolak dengan kalimat', /Periode/.test(ulSusunAtur({ bulan: '13' }, W).tolak || '') && /Naik/.test(ulSusunAtur({ naikPersen: '0' }, W).tolak || ''), '');
var sa = ulSusunAtur({ naikPersen: '30', langkah: '50.000' }, W); aturDengan([sa.dokumen[0].data]);
var oN3 = ulDaftar(KINI).daftar.find(function (o) { return o.nama === 'Bu Naik'; });
ok('3: atur naik 30 % · bulat Rp50.000 (kolom kosong = nilai berlaku) → Bu Naik Rp1.300.000; aturan tercatat "owner"', sa.dokumen[0].koleksi === 'aturanToko' && sa.dokumen[0].data.id === 'usulBon' && sa.dokumen[0].data.bulan === 3 && oN3.ke === 1300000 && ulAtur().dariOwner, J([sa.dokumen[0].data, oN3.ke]));
aturDengan([]);

// ==================== 4 · HALAMAN PELANGGAN (B18) ====================
var H = hnHalaman(KINI, k('Bu Naik'), 'Bu Naik', { laba: true });
ok('4: nota terakhir dulu: 4 nota (nota 3 Nov = 2 baris digabung, Rp790.000 tunai); pertama 25 Agu', H.nota.n === 4 && H.nota.nota[0].tanggal === '2026-11-03' && H.nota.nota[0].nBaris === 2 && H.nota.nota[0].total === 790000 && H.nota.nota[0].cara === 'tunai' && H.nota.pertama === '2026-08-25' && H.nota.nota[1].cara === 'bon', J(H.nota));
var bN = H.bulan.find(function (b) { return b.key === '2026-11'; });
ok('4: belanja per bulan 12 bulan (Des 2025 – Nov 2026); Nov = Rp790.000 − retur Rp650.000 (retur ikut nama di nota asalnya) = Rp140.000', H.bulan.length === 12 && H.bulan[0].key === '2025-12' && bN.berjalan && bN.omzet === 140000 && bN.nNota === 1, J(H.bulan.slice(-4)));
ok('4: per tahun: 2026 = Σ bulan Jan–Nov dari nota; 2025 nol', H.tahun[0].tahun === 2026 && H.tahun[0].sumber === 'nota' && H.tahun[0].omzet === 300000 + 400000 + 850000 + 140000 && H.tahun[1].tahun === 2025 && H.tahun[1].omzet === 0, J(H.tahun));
ok('4: pesanan yang belum jadi nota (yang sudah dibayar & milik orang lain tidak) + order rutin aktif', H.pesanan.length === 1 && H.pesanan[0].id === 'o1' && H.pesanan[0].kirim === '2026-11-20' && H.rutin.length === 1 && /tiap minggu/.test(H.rutin[0].kata), J([H.pesanan, H.rutin]));
ok('4: bon: lunas semua, batas Rp1.000.000 (angka owner), 0 dari 3 bon terakhir telat', H.bon.sisa === 0 && H.bon.batas === 1000000 && H.bon.sumberBatas === 'angka owner' && H.bon.kebiasaan.n === 3 && H.bon.kebiasaan.nTelat === 0 && !H.bon.henti, J(H.bon));
ok('4: laba (owner): 1 / 3 / 12 bulan = jumlah laba kotor bulanan; kalimat ringkas', H.laba && H.laba.bulan1.labaKotor === bN.labaKotor && dekat(H.laba.bulan12.labaKotor, H.bulan.reduce(function (a, b) { return a + (b.labaKotor || 0); }, 0)) && /4 nota sejak 25 Agu 2026/.test(hnRingkas(H)), J([H.laba, hnRingkas(H)]));
var HS = hnHalaman(KINI, k('Bu Naik'), 'Bu Naik', { laba: false });
ok('4: STAF: tidak menerima angka laba sama sekali (tanpa kunci laba, tanpa labaKotor/pct per bulan); sisanya sama', HS.laba === undefined && !HS.adaLaba && HS.bulan.every(function (b) { return !('labaKotor' in b) && !('pct' in b) && !('dilepas' in b); }) && HS.nota.n === 4 && HS.pesanan.length === 1 && HS.bulan[11].omzet === 140000, J(HS.bulan[11]));
var HB = hnHalaman(KINI, k('Bu Stop'), 'Bu Stop', { laba: false });
ok('4: bon dihentikan tampil di halaman orang itu', HB.bon.henti && HB.bon.henti.tanggal === '2026-11-01', J(HB.bon));
// penjaga identitas: per bulan, tiap pembeli bernama = pelangganBulan(bulan, 1)
var cocok = 0, beda = [];
['2026-08', '2026-09', '2026-10', '2026-11'].forEach(function (m) { var PB = pelangganBulan(m, 1, KINI);
  PB.pembeli.forEach(function (x) { var o = pgOrangBulan(x.kunci, KINI, 12).find(function (b) { return b.key === m; });
    if (o && dekat(o.omzet, x.omzet, 0.5) && (o.labaKotor === null ? x.labaKotor === null : dekat(o.labaKotor, x.labaKotor, 0.5)) && o.nNota === x.nNota) cocok++; else beda.push([m, x.nama, x.omzet, x.labaKotor, o && o.omzet, o && o.labaKotor]); }); });
ok('4: belanja & laba per orang per bulan = Laporan › Laba › Per pelanggan (pelangganBulan) persis — termasuk retur yang ikut nota asal', cocok >= 8 && !beda.length, J([cocok, beda]));

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
})();
"""

STATIS = [
    ('Jual: tanda HET di Bayar & lembar nego (owner saja)', 'jual', ["import { hjKeranjang, hjSatuHarga } from './het-jual-logika.js';", "${gambarHetBayar(s)}", "${p && owner ? gambarHetNego(b.trx, p.harga) : ''}",
        "function gambarHetBayar(s) {\n    if (bukanOwner(opsi.akun ? opsi.akun() : null)) return '';", "hjKeranjang(s.keranjang)", "hjSatuHarga(t, harga)"]),
    ('Laporan › Mingguan: kepatuhan HET + riwayat 8 minggu', 'laporan', ["import { hjMinggu, hjRiwayat, hjRiwayatTeks } from './het-jual-logika.js';", "const hetM = kartuHetMinggu(hjMinggu(awal), hjRiwayat(awal, 8), s);",
        "${perHari}${hitM}${hetM}${kaki}</section>`", "h`${hitM}${hetM}${perHari}`", "function kartuHetMinggu(M, R, s)", "TUGAS OWNER: petakan di Harga › HET", "hetMingguSemua: () =>"]),
    ('Pelanggan: tab Usul batas (owner) + halaman pelanggan di kartu + tautan dari lembar bon', 'pelanggan', ["import { UL_NAMA, ulAtur, ulDaftar, ulSusunAtur, ulSusunBuka, ulSusunPakai } from './usul-bon-logika.js';", "import { hnHalaman, hnRingkas } from './halaman-pelanggan-logika.js';",
        "['umur', 'Garis umur'], ['usul', 'Usul batas']];", "TAB_B.filter(([id]) => id !== 'usul' || !bukanOwner(akunKini()))", "${s.tabB === 'usul' && !bukanOwner(akunKini()) ? gambarUsul(s, d) : ''}",
        "${gambarHalaman(d.kunci, o.nama)}", "const owner = !bukanOwner(akunKini());\n    const H = (() => { try { return hnHalaman(kini(), kunci, nama, { laba: owner }); }", 'data-aksi="ulPakai"', 'data-aksi="ulBuka"',
        "ulPakai: async ({ kunci }) => { if (bukanOwner(akunKini()))", "ulBuka: async ({ kunci }) => { if (bukanOwner(akunKini()))", "'capIsi', 'ulAtur'], []);", 'data-k="ke-halaman"']),
    ('Kasir: bon dihentikan menahan KR1', 'jl', ["const HB = fkHentiBon(nama); if (HB) return fkHentiBonTeks(nama, HB) + '.';", "import { fkHentiBon, fkHentiBonTeks } from './faktur-logika.js';"]),
    ('CSS halaman & usul bergerak (gerak hidup), reduced-motion dihormati', 'css', ['@keyframes hnTumbuh', '.layar-pelanggan .ul-baris', '.layar-pelanggan .hn-halaman, .layar-pelanggan .hn-bulan i, .layar-pelanggan .ul-baris { animation: none; }']),
    ('modul baru dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/het-jual-logika.js">', '<link rel="modulepreload" href="js/layar/usul-bon-logika.js">', '<link rel="modulepreload" href="js/layar/halaman-pelanggan-logika.js">']),
    ('pages.yml menjalankan uji ini + kontrolnya', 'pages', ['python3 alat-uji/uji_pelanggan_het_p7.py && python3 alat-uji/uji_pelanggan_het_p7.py --kontrol']),
    ('BACA-DULU: bagian Paket P7', 'baca', ['## Paket P7 · Pelanggan & HET']),
]
RUSAK = [
    ('het: nego diabaikan (harga katalog saja)', HJ, "return asli + (hjAngka(p.negoSelisih) || 0);", "return asli;"),
    ('het: bonus kemasan ikut dibayar', HJ, "return Math.max(0, (hjAngka(p.jumlahUnit) || 0) - (hjAngka(p.bonusUnit) || 0));", "return hjAngka(p.jumlahUnit) || 0;"),
    ('het: literan tidak dibagi kg per liter', HJ, "if (p.jenis === 'literan') return a(p.rasioPakai);", "if (p.jenis === 'literan') return 1;"),
    ('het: buku per ukuran tidak ikut induk', HJ, "return U[m] && U[m].induk ? hjBersih(U[m].induk) : m;", "return m;"),
    ('het: literan wadah memakai merek asal', HJ, "p.jenis === 'literan' ? p.dariWadah || p.merkSumber : p.merkSumber", "p.merkSumber"),
    ('het: pengganti retur ikut dinilai', HJ, "if (!p || p.penggantiRetur || p.jenis === 'wadah') return null;", "if (!p || p.jenis === 'wadah') return null;"),
    ('het: takaran wadah dihitung dua baris', HJ, "const hjKunciBaris = (p) => (p.takaranId ? 't:' + String(p.takaranId) : String(p.id));", "const hjKunciBaris = (p) => String(p.id);"),
    ('het: belum dipetakan dianggap patuh', HJ, "const keadaan = !nBaris ? 'kosong' : !nDinilai && hit.belum ? 'belum' : hit.belum ? 'sebagian' : nDinilai ? 'lengkap' : 'kosong';", "const keadaan = !nBaris ? 'kosong' : 'lengkap';"),
    ('het: minggu mulai Minggu', HJ, "return hjIso(n - ((((n + 3) % 7) + 7) % 7));", "return hjIso(n - ((((n + 4) % 7) + 7) % 7));"),
    ('usul: naik tanpa syarat pemakaian', UL, "pakai !== null && pakai >= A.ambangPakaiPersen - 1e-9", "pakai !== null"),
    ('usul: turun sudah dari 1 telat', UL, "else if (batas > 0 && kb.nTelat >= PN_TELAT_MIN) {", "else if (batas > 0 && kb.nTelat >= 1) {"),
    ('usul: henti mengabaikan stop bon', UL, "else if (stop || macet) {", "else if (macet) {"),
    ('usul: pembulatan turun ke atas', UL, "o.ke = ulBulat(batas * (1 - A.turunPersen / 100), A.langkah, false);", "o.ke = ulBulat(batas * (1 - A.turunPersen / 100), A.langkah, true);"),
    ('usul: henti juga menulis batas', UL, "else data.batasKredit = o.ke;", "data.batasKredit = o.ke;"),
    ('usul: dipakai dua kali sebulan', UL, "if (o.sudah) return { tolak:", "if (false) return { tolak:"),
    ('usul: puncak = sisa sekarang', UL, "if (t >= dari) puncak = Math.max(puncak, sisa); });", "});"),
    ('kasir: bon dihentikan tidak menahan', JL, "const HB = fkHentiBon(nama); if (HB) return fkHentiBonTeks(nama, HB) + '.';", "const HB = null;"),
    ('faktur: henti dibaca dari kolom lain', FK, "const H = c && c.bonDihentikan;", "const H = c && c.bonDitahan;"),
    ('halaman: laba bocor ke staf', HN, "if (o.laba) {", "if (true) {"),
    ('halaman: pesanan dibayar ikut terbuka', HN, "kunciPelanggan(p.namaPelanggan) === k && pesananBelumTuntas(p)", "kunciPelanggan(p.namaPelanggan) === k"),
    ('halaman: nota tidak digabung per nota', HN, "const g = {}; ambilPenjualan().forEach((p) => { if (!kunci || kunciPelanggan(p.namaPelanggan) !== kunci) return; const k = kunciNota(p);", "const g = {}; ambilPenjualan().forEach((p) => { if (!kunci || kunciPelanggan(p.namaPelanggan) !== kunci) return; const k = String(p.id);"),
    ('laba per orang: retur ikut nama di dokumen retur', PG, "const namaAsal = pa ? pa.namaPelanggan : r.namaPelanggan;", "const namaAsal = r.namaPelanggan;"),
    ('laba per orang: ongkir masuk omzet barang', PG, "const ongkir = Math.round(Number(p.ongkirAntar) || 0); const barang = (p.hargaTotal || 0) - ongkir;", "const ongkir = Math.round(Number(p.ongkirAntar) || 0); const barang = (p.hargaTotal || 0) - 1;"),
]
RUSAK_STATIS = [
    ('tab Usul batas tampil untuk staf', 'pelanggan', "TAB_B.filter(([id]) => id !== 'usul' || !bukanOwner(akunKini()))", "TAB_B.filter(([id]) => true)"),
    ('halaman memberi laba ke staf', 'pelanggan', "hnHalaman(kini(), kunci, nama, { laba: owner })", "hnHalaman(kini(), kunci, nama, { laba: true })"),
    ('tanda HET Bayar untuk staf', 'jual', "function gambarHetBayar(s) {\n    if (bukanOwner(opsi.akun ? opsi.akun() : null)) return '';", "function gambarHetBayar(s) {\n"),
    ('modul tidak dipramuat', 'index', '<link rel="modulepreload" href="js/layar/usul-bon-logika.js">', ''),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_pelanggan_het_p7.py && python3 alat-uji/uji_pelanggan_het_p7.py --kontrol', 'true'),
    ('modul logika menulis langsung', 'hn', "export function hnNota(kunci, n) {", "export function hnNota(kunci, n) { tulisDokumen([]);"),
    ('rumus HET kedua', 'hj', "export function hjSatuHarga(", "const HJ_HET = 13500;\nexport function hjSatuHarga("),
    ('usul menulis koleksi lain', 'ul', "return { dokumen: [{ koleksi: 'pelangganCatatan', data }], patch: { kabar: 'Bon ' + lama.nama", "return { dokumen: [{ koleksi: 'penjualan', data }], patch: { kabar: 'Bon ' + lama.nama"),
    ('komentar // menelan kode', 'hn', "export function hnRingkas(H) {", "// ringkas\nexport function hnRingkas(H) { // kalimat; const x = 1;\n"),
    ('rules: staf membaca setelan usul bon', 'rules', "'bukuPegangan', 'rutin'] && staf(['ben', 'karyawan'])", "'bukuPegangan', 'rutin', 'usulBon'] && staf(['ben', 'karyawan'])"),   # daftar baca staf rules v25 (berakhir 'rutin')
]

ASAP = r"""
(function () {
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(Date.now()); var iso = hariIniIso(kini); var out = { akhir: iso, galat: [] };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + e); return null; } };
// A132: 8 minggu, peta kelas toko apa adanya
var R = aman('riwayat', function () { return hjRiwayat(iso, 8); }) || [];
out.minggu = R.map(function (r) { return r.awal + ' ' + r.keadaan + ' ' + r.nBaris + ' baris'; });
var semuaTutup = true; R.forEach(function (r) { var M = hjMinggu(r.awal); var s = 0; Object.keys(M.hit).forEach(function (x) { s += M.hit[x]; }); if (s !== M.nBaris || !M.menutup) semuaTutup = false; }); out.mingguMenutup = semuaTutup;
var M0 = hjMinggu(iso); out.petaToko = { keadaan: M0.keadaan, belumDipetakan: M0.unitBelum.length, takBisa: M0.takBisa };
// peta CONTOH (semua kelas yang belum dipetakan = medium) — jalur dinilai jalan di data toko; hanya jumlah yang dicetak
var het = (CAD.aturanToko || []).find(function (d) { return d.id === 'het'; }) || { id: 'het' }; var peta = {}; M0.unitBelum.forEach(function (u) { peta[u] = 'medium'; });
pasok('aturanToko', (CAD.aturanToko || []).filter(function (d) { return d.id !== 'het'; }).concat([Object.assign({}, het, { peta: peta })]));
var MC = aman('contoh', function () { return hjMinggu(iso); }); out.petaContoh = MC ? { keadaan: MC.keadaan, dinilai: MC.nDinilai, atas: MC.hit.atas, dalam: MC.hit.dalam, belum: MC.hit.belum, menutup: MC.menutup } : null;
pasok('aturanToko', CAD.aturanToko || []);
// A108
var D = aman('usul', function () { return ulDaftar(kini); });
out.usul = D ? { orang: D.daftar.length, hit: D.hit } : null;
out.usulSah = D ? D.daftar.every(function (o) { return UL_URUT.indexOf(o.usul) >= 0 && (o.usul !== 'naik' || (o.ke > o.batas && o.ke % D.atur.langkah === 0)) && (o.usul !== 'turun' || (o.ke < o.batas && o.ke % D.atur.langkah === 0)); }) : false;
out.kr1Galat = 0; if (D) D.daftar.forEach(function (o) { try { kunciKr1(o.nama, 1000); } catch (e) { out.kr1Galat += 1; } });
// B18
var orang = aman('orang', function () { return semuaOrang(kini); }) || []; var gH = 0, bocor = 0;
orang.forEach(function (o) { var Ho = aman('halaman ' + o.kunci, function () { return hnHalaman(kini, o.kunci, o.nama, { laba: true }); }); var Hs = aman('halaman staf ' + o.kunci, function () { return hnHalaman(kini, o.kunci, o.nama, { laba: false }); });
  if (!Ho || !Hs) gH += 1; else if (Hs.laba !== undefined || Hs.bulan.some(function (b) { return 'labaKotor' in b; })) bocor += 1; });
out.halaman = { orang: orang.length, galat: gH, labaBocor: bocor };
var cocok = 0, beda = 0; var bln = []; for (var i = 2; i >= 0; i--) { var d = new Date(kini.getFullYear(), kini.getMonth() - i, 1); bln.push(d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0')); }
bln.forEach(function (m) { var PB = aman('pelangganBulan ' + m, function () { return pelangganBulan(m, 1, kini); }); if (!PB || PB.diarsip) return;
  PB.pembeli.forEach(function (x) { var o = pgOrangBulan(x.kunci, kini, 12).find(function (b) { return b.key === m; });
    if (o && Math.abs(o.omzet - x.omzet) < 0.5 && (o.labaKotor === null ? x.labaKotor === null : Math.abs(o.labaKotor - x.labaKotor) < 0.5) && o.nNota === x.nNota) cocok++; else beda++; }); });
out.identitas = { bulan: bln, cocok: cocok, beda: beda };
print(JSON.stringify(out));
})();
"""


def bundel_js(teks):
    uji_dasbor_sensus.MODUL[:] = MODUL
    return uji_dasbor_sensus.bundel_js(teks)


def jalan(teks):
    jam = "var __KINI = new Date('2026-11-18T14:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    r, out = uji_dasbor_sensus.jsc(jam + bundel_js(teks) + '\nvar KOTAK0 = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar GK = ' + json.dumps(KOTAK) + ';\nvar ATUR = ' + json.dumps(ATUR)
                                  + ';\nvar KARTU = ' + json.dumps(KARTU) + ';\n' + SKENARIO)
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], list(h['gagal'])


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    # tulisan: het-jual & halaman BACA SAJA; usul bon hanya kartu pelanggan (owner) + setelan aturanToko/usulBon
    for k in ('hj', 'hn'):
        if 'koleksi:' in src[k] or 'dokumen:' in src[k]: g.append(k + ': modul baca-saja menulis dokumen')
    tulis = sorted(set(re.findall(r"koleksi: '(\w+)'", src['ul'])))
    if tulis != ['aturanToko', 'pelangganCatatan'] or "data = { id: UL_ID," not in src['ul']: g.append('usul-bon-logika: menulis selain kartu pelanggan & setelan aturanToko/usulBon → ' + str(tulis))
    for k in ('hj', 'ul', 'hn'):
        if 'document.' in src[k] or 'tulisDokumen' in src[k] or 'window.' in src[k]: g.append(k + ': modul logika menyentuh DOM / menulis langsung')
    # SATU rumus HET: het-jual tidak membawa angka HET / rumus sendiri — hanya hetAtur · hetUnit · hetNilai
    if re.search(r'\b1[34]\.?[59]00\b', src['hj']) or 'HET_BAWAAN' in src['hj'] or "import { hetAtur, hetUnit, hetNilai } from './het-logika.js';" not in src['hj']: g.append('het-jual-logika: angka / rumus HET kedua (harus lewat het-logika)')
    # setelan usul bon owner saja: staf tidak membaca aturanToko/usulBon (rules baris baca per dokumen tidak berubah)
    m = re.search(r"match /aturanToko/\{id\} \{\s*allow read: if ([^\n]*)", src['rules'])
    if not m or 'usulBon' in m.group(1): g.append('rules: setelan usul bon terbaca staf (atau aturan aturanToko tidak ketemu)')
    for k in ('hj', 'ul', 'hn', 'pg', 'jual', 'laporan', 'pelanggan', 'jl', 'fk'):
        for n, baris in enumerate(src[k].split('\n')):
            ekor = uji_sisa_sensus.komentar_ekor(baris)
            if ekor and re.search(r"\b[a-zA-Z]\w*: (opsi\.|\(|async |\[|\{|'|`)|;\s*(const|let|return|if)\b|\)\s*=>", ekor): g.append(k + ':' + str(n + 1) + ': komentar // menelan kode → ' + ekor.strip()[:90])
    i = src['baca'].find('## Paket P7')
    if i >= 0 and re.search(r'rules v2[5-9]', src['baca'][i:i + 9000]): g.append('BACA-DULU menyebut rules baru untuk paket P7 (paket ini tanpa rules)')
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
        r, out = uji_dasbor_sensus.jsc("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + bundel_js(teks) + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if r.returncode != 0 or not out.startswith('{'): print('ASAP DATA TOKO: JSC JATUH ' + (r.stderr or r.stdout)[-600:]); g.append('asap')
        else:
            h = json.loads(out)
            beres = (not h['galat'] and h['mingguMenutup'] and h['petaContoh'] and h['petaContoh']['menutup'] and h['petaContoh']['dinilai'] > 0 and h['usul'] is not None and h['usulSah']
                     and h['kr1Galat'] == 0 and h['halaman']['galat'] == 0 and h['halaman']['labaBocor'] == 0 and h['identitas']['beda'] == 0 and h['identitas']['cocok'] > 0)
            # angka RUPIAH toko TIDAK dicetak (repo publik) — hanya keadaan & jumlah
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: rekap HET / usul bon / halaman pelanggan galat atau per orang ≠ Laporan')
    sys.exit(1 if g or gs else 0)
