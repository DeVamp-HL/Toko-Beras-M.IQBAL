#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_pembelian_p4.py — PAKET P4 · Pembelian, pemasok & utang (owner 27 Nov 2026; sensus ulang 27 Nov b: A5 A25 A57 B40 B57 B62 B63 B64 B78 B134).
KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban. Jam uji DIBEKUKAN (new Date() juga — umur bon mesin beku memakai jam perangkat).
  A25   tarif bongkar kuli PER KARUNG (sama untuk semua kuli; 50 & 25 kg beda), berlaku sejak tanggalnya: Barang masuk ditandai kalau upah bongkar beda (cuma
        tanda); kedatangan lama dicek dengan tarif DI HARINYA; ongkos kirim bukan upah bongkar; bal & kemasan tidak dihitung; tablet = titipan; catatStok utuh.
  A57   buku pembelian per periode: semua kedatangan (bon + langsung) + status bayar SEKARANG (lunas / sisa / langsung) — Σ = kartu Pembelian (shPembelian).
  B63   rata-rata per kedatangan & per pesanan (pesanan batal tidak ikut).
  B62 · B134 · B64  per pemasok bulan ini vs bulan lalu (berjalan: s.d. tanggal yang sama), pesanan datang · menunggu · batal per pemasok.
  B40 · B78  umur utang per pemasok: ≤ 7 · 8–30 · 1–3 bln · > 3 bln sejak datang + lewat tempo 1–7 · 8–30 · > 30 hari; Σ = sisa bon mesin; batas setelan owner.
  A5    piutang per nota di garis jatuh tempo Bon pemasok: masuk kalau tepat waktu, yang lewat tidak dihitung, penanda kas + piutang.
  B57   beban gudang 7 hari: masuk = pesanan ditunggu di tanggal janji TERAKHIR, keluar = laju pakai + pesanan pelanggan terjadwal.

    python3 alat-uji/uji_pembelian_p4.py            → N lulus · 0 gagal (+ asap cadangan toko bila ada; angka rupiah toko tidak dicetak)
    python3 alat-uji/uji_pembelian_p4.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_jual_baru, uji_dasbor_sensus, uji_sisa_sensus  # noqa: E402
PB = 'baru/js/layar/pembelian-logika.js'; DL = 'baru/js/layar/dasbor-logika.js'; WG = 'baru/js/layar/dasbor-widget-logika.js'; SC = 'baru/js/layar/stok-catat-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_dasbor_sensus.MODUL + [PB])))
SUMBER = {'harga': 'baru/js/layar/harga.js', 'stok': 'baru/js/layar/stok.js', 'dasbor': 'baru/js/layar/dasbor.js', 'css': 'baru/css/ringkasan.css', 'cssh': 'baru/css/harga.css',
          'index': 'baru/index.html', 'rules': 'firestore.rules', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'bundel': 'alat-uji/bundel_baru.py',
          'pb': PB, 'dl': DL, 'wg': WG, 'upah': 'baru/js/layar/upah-logika.js'}

JAM_BEKU = r"""
var __KINI = new Date('2026-11-18T14:00:00+07:00').getTime(); var __D = Date;
Date = function (a, b, c, d, e, f, g) { var n = arguments.length; if (!(this instanceof Date)) return new __D(__KINI).toString();
  return n === 0 ? new __D(__KINI) : n === 1 ? new __D(a) : new __D(a, b, c === undefined ? 1 : c, d || 0, e || 0, f || 0, g || 0); };
Date.prototype = __D.prototype; Date.now = function () { return __KINI; }; Date.UTC = __D.UTC; Date.parse = __D.parse;
"""


def KARUNG(merk, n, berat, harga):
    return {'merk': merk, 'satuan': 'karung', 'beratKarung': berat, 'jumlahKarung': n, 'totalKg': n * berat, 'subtotalHarga': n * berat * harga, 'hargaPerKg': harga}
def BATCH(i, tgl, pemasok, cara, baris, bongkar=0, **x):
    d = {'id': i, 'tanggal': tgl, 'jam': x.pop('jam', '08:00'), 'pemasok': pemasok, 'caraBayar': cara, 'biayaBongkar': bongkar, 'merkList': baris}
    d.update(x); return d
def KREDIT(i, tgl, nama, total):
    return {'id': i, 'tanggal': tgl, 'jam': '10:00', 'caraBayar': 'Kredit', 'namaPelanggan': nama, 'jenis': 'karung', 'merkSumber': 'Angsa', 'beratKarungAcuan': 50,
            'jumlahKarung': 1, 'totalKg': 50, 'hargaAsliSatuan': total, 'hargaTotal': total, 'hppTotalSaatJual': round(total * 0.9), 'grupNota': 'g' + i}

KOTAK = {
    'batchMasuk': [
        BATCH('k1', '2026-10-05', 'Pemasok Satu', 'utang', [KARUNG('Angsa', 100, 50, 12000)], 200000),
        BATCH('k2', '2026-10-12', 'Pemasok Dua', 'tunai', [KARUNG('Pelita', 40, 25, 11000)], 60000),
        BATCH('k3', '2026-10-25', 'Pemasok Satu', 'utang', [KARUNG('Angsa', 60, 50, 12500)], 120000),
        BATCH('k4', '2026-11-03', 'Pemasok Dua', 'utang', [KARUNG('Pelita', 80, 50, 11500)], 150000),
        BATCH('k5', '2026-11-10', 'Pemasok Tiga', 'tunai', [KARUNG('Angsa', 20, 50, 12200), {'merk': 'Kembang', 'bentuk': 'bal', 'kemasanJadi': True, 'jumlahBal': 10, 'ukuranBag': 5, 'subtotalHarga': 0}], 90000, ongkosKirim=50000),
        BATCH('k6', '2026-11-15', 'Pemasok Satu', 'utang', [KARUNG('Angsa', 30, 50, 12600)], 0),
        BATCH('k7', '2026-11-17', 'Pemasok Tiga', 'utang', [KARUNG('Angsa', 10, 50, 12000)], 0, jam='09:00', dariTablet=True),
        BATCH('k8', '2026-10-01', '', 'tunai', [KARUNG('Angsa', 20, 50, 5000)], 0, stokAwal=True),
        BATCH('k9', '2026-10-02', 'LAHIR BUKU', 'tunai', [dict(KARUNG('Wadah A1', 1, 40, 12000), stokWadah='A1')], 0, stokAwal=True, lahirBuku=True),   # buku wadah literan (bukan isi gudang)
    ],
    'utangPemasokMutasi': [
        {'id': 'm1', 'tanggal': '2026-10-20', 'jam': '10:00', 'tipe': 'bayar', 'pemasok': 'Pemasok Satu', 'nominal': 60000000, 'bonId': 'k1', 'bonTanggal': '2026-10-05', 'dari': 'laci'},
        {'id': 'm2', 'tanggal': '2026-11-05', 'jam': '10:00', 'tipe': 'bayar', 'pemasok': 'Pemasok Satu', 'nominal': 20000000, 'bonId': 'k3', 'bonTanggal': '2026-10-25', 'dari': 'laci'},
        {'id': 's1', 'tanggal': '2026-09-01', 'tipe': 'saldoAwal', 'pemasok': 'Pemasok Dua', 'nominal': 3000000, 'bonTanggal': '2026-07-01', 'catatan': 'bon lama contoh'},
        {'id': 's2', 'tanggal': '2026-09-01', 'tipe': 'saldoAwal', 'pemasok': 'Pemasok Tiga', 'nominal': 1000000, 'bonTanggal': '', 'catatan': 'bon lama tanpa tanggal'},
    ],
    'pemasokCatatan': [{'id': 'pemasok satu', 'nama': 'Pemasok Satu', 'tempo': 14}, {'id': 'pemasok dua', 'nama': 'Pemasok Dua', 'tempo': 30}],
    'pesananPemasok': [
        {'id': 'ps1', 'tanggal': '2026-11-01', 'jam': '09:00', 'pemasok': 'Pemasok Dua', 'status': 'menunggu', 'kg': 4000, 'karung': 80, 'rp': 46000000},
        {'id': 'ps2', 'tanggal': '2026-11-16', 'jam': '09:00', 'pemasok': 'Pemasok Satu', 'status': 'menunggu', 'kg': 2500, 'karung': 50, 'rp': 31250000, 'janjiTanggal': '2026-11-20',
         'janjiRiwayat': [{'tanggal': '2026-11-19', 'pada': '2026-11-16T03:00:00.000Z', 'oleh': 'contoh'}, {'tanggal': '2026-11-20', 'pada': '2026-11-17T03:00:00.000Z', 'oleh': 'contoh'}]},
        {'id': 'ps3', 'tanggal': '2026-11-16', 'jam': '10:00', 'pemasok': 'Pemasok Dua', 'status': 'menunggu', 'kg': 1000, 'karung': 20, 'rp': 11500000, 'janjiTanggal': '2026-11-17',
         'janjiRiwayat': [{'tanggal': '2026-11-17', 'pada': '2026-11-16T04:00:00.000Z', 'oleh': 'contoh'}]},
        {'id': 'ps4', 'tanggal': '2026-11-17', 'jam': '18:00', 'pemasok': 'Pemasok Tiga', 'status': 'menunggu', 'kg': 500, 'karung': 10, 'rp': 6000000},
        {'id': 'ps5', 'tanggal': '2026-11-05', 'jam': '09:00', 'pemasok': 'Pemasok Tiga', 'status': 'batal', 'kg': 1000, 'karung': 20, 'rp': 12000000},
        {'id': 'ps6', 'tanggal': '2026-11-16', 'jam': '10:05', 'pemasok': 'Pemasok Dua', 'status': 'menunggu', 'kg': 500, 'karung': 10, 'rp': 5750000, 'janjiTanggal': '2026-12-01',
         'janjiRiwayat': [{'tanggal': '2026-12-01', 'pada': '2026-11-16T04:05:00.000Z', 'oleh': 'contoh'}]},
    ],
    'penjualan': [KREDIT('j1', '2026-11-10', 'Bu Nota', 500000), KREDIT('j2', '2026-10-01', 'Pak Lewat', 300000), KREDIT('j3', '2026-11-15', 'Bu Jauh', 400000), KREDIT('j4', '2026-11-04', 'Bu Hari', 200000)],
    'pesanan': [{'id': 'o1', 'tanggal': '2026-11-18', 'jam': '09:00', 'namaPelanggan': 'Bu Nota', 'status': 'dipesan', 'tanggalKirim': '2026-11-19', 'nilaiPerkiraan': 1300000,
                 'baris': [{'jalur': 'karung', 'kunci': 'Angsa', 'nama': 'Angsa 50 kg', 'jumlah': 4, 'kg': 200, 'berat': 50}]}],
}
KARTU = [{'nama': 'Bu Nota', 'tempoHari': 14}, {'nama': 'Pak Lewat', 'tempoHari': 14}, {'nama': 'Bu Jauh', 'tempoHari': 60}, {'nama': 'Bu Hari', 'tempoHari': 14}]
TARIF = [{'mulai': '2026-10-01', 'berat': 50, 'rp': 2000}, {'mulai': '2026-10-01', 'berat': 25, 'rp': 1500}, {'mulai': '2026-11-16', 'berat': 50, 'rp': 2500}]

SKENARIO = r"""
(function () {
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); }; var dekat = function (a, b, t) { return a !== null && b !== null && a !== undefined && b !== undefined && Math.abs(a - b) < (t || 0.005); };
var KINI = new Date(); var nId = 90000; var iso = '2026-11-18';
var W = { tanggal: '2026-11-18', jam: '14:00', kini: '2026-11-18T07:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK0).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'penyesuaianStok', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'stokBahanKemasan', 'pesanan', 'orderRutin', 'karantina', 'persetujuan', 'pengeluaranHarian', 'tagih', 'suratJalan'].forEach(function (n) { pasok(n, []); });
Object.keys(GK).forEach(function (n) { pasok(n, JSON.parse(J(GK[n]))); });
pasok('pelangganCatatan', KARTU.map(function (c) { return Object.assign({ id: kunciPelanggan(c.nama) }, JSON.parse(J(c))); }));
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-11-18', laci: 85000000, brankas: 0, rekening: 0, amplop: 0, diubahPada: '2026-11-18T01:00:00.000Z' }]);
setelSumber('cadangan', 'kotak pasir');
var CATAT = { id: 'catatStok', tanggal: '2026-10-01', jam: '08:00', tempoHari: 0, ukuranKarung: [50, 25], tarifBongkar: TARIF };
var aturDengan = function (e) { pasok('aturanToko', JSON.parse(J(e || []))); };
aturDengan([CATAT]);
ok('0: jam uji dibekukan (new Date() = 18 Nov 2026 14.00 WIB)', hariIniIso(new Date()) === iso && tanggalLokalIso() === iso, hariIniIso(new Date()));

// ==================== 1 · TARIF BONGKAR (A25) ====================
var D0 = [{ jumlahKarung: '10', beratKarung: 50 }, { jumlahKarung: '4', beratKarung: 25 }];
var t1 = pbCekBongkar(D0, '', iso), t2 = pbCekBongkar(D0, '31.000', iso), t3 = pbCekBongkar(D0, '30000', iso), t4 = pbCekBongkar(D0, '26000', '2026-11-10');
ok('1: 18 Nov: 10 karung 50 kg × Rp2.500 + 4 karung 25 kg × Rp1.500 = Rp31.000; kosong = "belum diisi" (awas), pas = cocok, Rp30.000 = KURANG Rp1.000 (tetap boleh disimpan)',
  t1.keadaan === 'kosong' && t1.harap === 31000 && t1.awas && t2.keadaan === 'cocok' && !t2.awas && t3.keadaan === 'kurang' && t3.beda === -1000 && /KURANG Rp1\.000/.test(t3.teks) && /tetap boleh disimpan/.test(t3.teks), J([t1, t2, t3]));
ok('1: tarif yang berlaku DI HARINYA: 10 Nov (sebelum tarif baru 16 Nov) = 10 × Rp2.000 + 4 × Rp1.500 = Rp26.000 → cocok', t4.keadaan === 'cocok' && t4.harap === 26000, J(t4));
var t5 = pbCekBongkar([{ jumlahKarung: '5', beratKarung: 10 }, { jumlahKarung: '2', beratKarung: 50 }], '5000', iso), t6 = pbCekBongkar(D0, '1000', '2026-09-01');
ok('1: ukuran tanpa tarif (10 kg) atau tanggal sebelum tarif pertama = "sebagian", tidak dicek (yang bertarif disebut)', t5.keadaan === 'sebagian' && t5.tanpaTarif[0] === 10 && t5.harap === 5000 && !t5.awas && t6.keadaan === 'sebagian' && t6.tanpaTarif.length === 2, J([t5, t6]));
var t7 = pbCekBongkar([{ jumlahKarung: '3', beratKarung: 50, masuk: 'kemasan' }, { jumlahKarung: '2', beratKarung: 50, ditolak: '1' }, { bentuk: 'bal', jumlahBal: 9 }], '', iso);
ok('1: baris kemasan jadi, ditolak & bal tidak dihitung tarif per karung → "tidak ada karung"', t7.keadaan === 'tanpaKarung' && t7.karung === 0, J(t7));
var B = {}; ambilSemuaBatch().forEach(function (b) { B[b.id] = b; });
var c5 = pbCekKedatangan(B.k5), c6 = pbCekKedatangan(B.k6), c7 = pbCekKedatangan(B.k7), c4 = pbCekKedatangan(B.k4);
ok('1: kedatangan tersimpan: upah bongkar = biayaBongkar − ongkos kirim (Rp90.000 − Rp50.000 = Rp40.000 = 20 × Rp2.000 → cocok; bal kemasan tidak dihitung)', c5.keadaan === 'cocok' && c5.bongkar === 40000 && c5.harap === 40000, J(c5));
ok('1: Rp150.000 untuk 80 karung (tarif Rp160.000) = kurang Rp10.000; bongkar 0 = belum diisi; kedatangan tablet tanpa upah = titipan (tidak ditandai)', c4.keadaan === 'kurang' && c4.beda === -10000 && c6.keadaan === 'kosong' && c6.harap === 60000 && c7.keadaan === 'titip' && !c7.awas && c7.harap === 25000, J([c4, c6, c7]));
aturDengan([{ id: 'catatStok', tempoHari: 0 }]);
var t8 = pbCekBongkar(D0, '0', iso); ok('1: tarif belum ditulis = "tidak dicek", bukan tanda awas', t8.keadaan === 'tanpaTarif' && !t8.awas && /belum ditulis/.test(t8.teks), J(t8));
aturDengan([CATAT]);
var sv = pbSusunTarif({ mulai: '2026-11-20', baris: [{ berat: 50, rp: '2.700' }, { berat: 25, rp: '' }] }, W);
var dk = sv.dokumen && sv.dokumen[0]; var L = dk ? dk.data.tarifBongkar : [];
ok('1: simpan tarif = SATU dokumen aturanToko/catatStok; kolom lain (tempo, ukuran karung) disalin utuh; kosong = tidak diubah; riwayat lama tetap', !sv.tolak && sv.dokumen.length === 1 && dk.koleksi === 'aturanToko' && dk.data.id === 'catatStok'
  && dk.data.tempoHari === 0 && J(dk.data.ukuranKarung) === '[50,25]' && L.length === 4 && L[3].mulai === '2026-11-20' && L[3].rp === 2700 && L.filter(function (x) { return x.berat === 25; }).length === 1, J(sv));
pasok('aturanToko', [dk.data]);
ok('1: tarif mulai 20 Nov belum berlaku hari ini (Rp2.500), berlaku untuk kedatangan 20 Nov (Rp2.700)', pbTarifPada(50, iso).rp === 2500 && pbTarifPada(50, '2026-11-20').rp === 2700 && pbTarifKini(iso, [50, 25]).baris[0].nanti.rp === 2700, J(pbTarifKini(iso, [50, 25])));
var sv2 = pbSusunTarif({ mulai: '2026-11-20', baris: [{ berat: 50, rp: '2800' }] }, W);
ok('1: tarif di tanggal & ukuran yang sama MENGGANTI (tidak dobel); ketik bukan angka / di atas Rp100.000 ditolak; kosong semua ditolak', !sv2.tolak && sv2.dokumen[0].data.tarifBongkar.filter(function (x) { return x.mulai === '2026-11-20'; }).length === 1 && sv2.dokumen[0].data.tarifBongkar.filter(function (x) { return x.mulai === '2026-11-20'; })[0].rp === 2800
  && !!pbSusunTarif({ baris: [{ berat: 50, rp: 'dua' }] }, W).tolak && !!pbSusunTarif({ baris: [{ berat: 50, rp: '150000' }] }, W).tolak && !!pbSusunTarif({ baris: [{ berat: 50, rp: '' }] }, W).tolak, J(sv2));
var ac = susunAturCatat({ tempoHari: '21' }, W);
ok('1: Atur Barang masuk (susunAturCatat) menyimpan tempo TANPA menghapus tarif bongkar', !ac.tolak && J(ac.dokumen[0].data.tarifBongkar) === J(dk.data.tarifBongkar), J(ac.dokumen && ac.dokumen[0].data.tarifBongkar));
aturDengan([CATAT]);

// ==================== 2 · BUKU PEMBELIAN (A57 · B63) ====================
var BK = pbBukuPembelian('2026-11-01', iso, KINI); var by = {}; BK.baris.forEach(function (x) { by[x.id] = x; });
ok('2: November: 4 kedatangan (bon + tunai), terbaru dulu; Σ Rp83.340.000 = kartu Pembelian (shPembelian) persis', BK.n === 4 && BK.rp === 83340000 && BK.menutup && BK.baris[0].id === 'k7' && BK.baris[3].id === 'k4' && shPembelian('2026-11-01', iso).rp === BK.rp, J([BK.n, BK.rp, BK.baris.map(function (x) { return x.id; })]));
ok('2: status bayar SEKARANG per kedatangan: k4 bon sisa Rp46.000.000 · k5 dibayar langsung · k6 & k7 bon bersisa', by.k4.status === 'sisa' && by.k4.sisa === 46000000 && by.k5.status === 'langsung' && by.k6.status === 'sisa' && by.k7.status === 'sisa' && /bon sisa Rp46\.000\.000/.test(by.k4.statusTeks), J([by.k4, by.k5]));
ok('2: ringkas: bon 3 kedatangan Rp71.050.000 (sisa Rp70.900.000) · langsung 1 Rp12.290.000 · rata-rata Rp20.835.000 per kedatangan', BK.bon.n === 3 && BK.bon.rp === 71050000 && BK.bon.sisa === 70900000 && BK.langsung.n === 1 && BK.langsung.rp === 12290000 && dekat(BK.rata, 20835000), J([BK.bon, BK.langsung, BK.rata]));
ok('2: upah bongkar beda tarif: 2 kedatangan (kurang Rp10.000 + belum diisi Rp60.000); tablet (titipan) & yang cocok tidak dihitung', BK.bedaTarif.n === 2 && BK.bedaTarif.rp === -70000 && !by.k7.tarif.awas && !by.k5.tarif.awas, J(BK.bedaTarif));
ok('2: B63 per pesanan: 5 pesanan dibuat November (1 batal tidak ikut) · rata-rata Rp20.100.000', BK.pesanan.n === 5 && BK.pesanan.nBatal === 1 && dekat(BK.pesanan.rata, 20100000), J(BK.pesanan));
var BO = pbBukuPembelian('2026-10-01', '2026-10-31', KINI); var bo = {}; BO.baris.forEach(function (x) { bo[x.id] = x; });
ok('2: Oktober: bon k1 LUNAS (dibayar Rp60.000.000), k3 sisa Rp17.500.000 dari Rp37.500.000, k2 langsung; stok awal = "dicatat", bukan belanja', BO.n === 3 && bo.k1.status === 'lunas' && bo.k1.dibayar === 60000000 && bo.k3.sisa === 17500000 && bo.k3.nilaiBon === 37500000 && bo.k2.status === 'langsung' && BO.nDicatat === 1 && BO.dicatat === 5000000 && BO.menutup, J([BO.n, bo.k1, bo.k3, BO.nDicatat]));

// ==================== 3 · PER PEMASOK, BULAN INI VS BULAN LALU (B62 · B134 · B63 · B64) ====================
var PM = pbPemasokBulan('2026-11', KINI); var pm = {}; PM.daftar.forEach(function (g) { pm[g.pemasok] = g; });
ok('3: bulan berjalan dibanding Oktober s.d. tanggal 18 (bukan Oktober penuh); urut rupiah bulan ini', PM.berjalan && PM.banding === 'laluSama' && PM.laluSamaSampai === '2026-10-18' && /s\.d\. tanggal 18/.test(PM.pembandingTeks) && PM.daftar[0].pemasok === 'Pemasok Dua' && PM.menutup, J([PM.pembandingTeks, PM.daftar.map(function (g) { return g.pemasok; })]));
ok('3: Pemasok Dua: Rp46.150.000 vs Rp11.060.000 (+317,3 %); Pemasok Satu: Rp18.900.000 vs Rp60.200.000 s.d. 18 Okt (Oktober penuh Rp97.820.000); Pemasok Tiga baru',
  pm['Pemasok Dua'].ini.rp === 46150000 && pm['Pemasok Dua'].laluSama.rp === 11060000 && dekat(pm['Pemasok Dua'].ubahPct, (46150000 / 11060000 - 1) * 100) && pm['Pemasok Satu'].ini.rp === 18900000 && pm['Pemasok Satu'].laluSama.rp === 60200000 && pm['Pemasok Satu'].lalu.rp === 97820000 && pm['Pemasok Satu'].lalu.n === 2 && pm['Pemasok Tiga'].baru, J(PM.daftar));
ok('3: B63 rata-rata per kedatangan per pemasok: Pemasok Tiga 2 kedatangan → Rp9.145.000; per pesanan Rp6.000.000 (pesanan batal Rp12.000.000 tidak ikut)', pm['Pemasok Tiga'].ini.n === 2 && dekat(pm['Pemasok Tiga'].ini.rata, 9145000) && pm['Pemasok Tiga'].pesanan.rp === 6000000 && dekat(pm['Pemasok Tiga'].pesanan.rata, 6000000), J([pm['Pemasok Tiga'].ini, pm['Pemasok Tiga'].pesanan]));
ok('3: B64 pesanan dibuat November per pemasok: Dua 3 (1 datang · 2 menunggu) · Satu 1 menunggu · Tiga 2 (1 menunggu · 1 batal); total 6 = 1 · 4 · 1',
  J([pm['Pemasok Dua'].pesanan.n, pm['Pemasok Dua'].pesanan.datang, pm['Pemasok Dua'].pesanan.menunggu]) === '[3,1,2]' && pm['Pemasok Satu'].pesanan.menunggu === 1 && pm['Pemasok Tiga'].pesanan.batal === 1 && pm['Pemasok Tiga'].pesanan.menunggu === 1
  && J([PM.total.pesanan.n, PM.total.pesanan.datang, PM.total.pesanan.menunggu, PM.total.pesanan.batal]) === '[6,1,4,1]' && dekat(pm['Pemasok Dua'].pesanan.rata, (46000000 + 11500000 + 5750000) / 3), J(PM.total.pesanan));
var PO = pbPemasokBulan('2026-10', KINI);
ok('3: bulan yang sudah lewat (Oktober) dibanding September PENUH; total Oktober = kartu Pembelian', !PO.berjalan && PO.banding === 'lalu' && PO.total.ini.rp === shPembelian('2026-10-01', '2026-10-31').rp && PO.menutup, J([PO.banding, PO.total]));

// ==================== 4 · UMUR UTANG (B40 · B78) ====================
var U = pbUmurUtang(KINI); var um = {}; U.daftar.forEach(function (g) { um[g.pemasok] = g; }); var ju = function (o) { return o.umur.map(function (e) { return e.rp; }); };
ok('4: kelompok bawaan ≤ 7 hari · 8–30 hari · 1–3 bulan · > 3 bulan; Σ = sisa bon mesin Rp92.400.000 (menutup)', J(U.kelompok.map(function (e) { return e.label; })) === J(['≤ 7 hari', '8–30 hari', '1–3 bulan', '> 3 bulan']) && U.total.total === 92400000 && U.totalMesin === 92400000 && U.menutup, J([U.kelompok, U.total.total, U.totalMesin]));
ok('4: total per umur: ≤7 Rp24.900.000 · 8–30 Rp63.500.000 · 1–3 bln 0 · > 3 bln Rp3.000.000 · tanpa tanggal Rp1.000.000', J(ju(U.total)) === J([24900000, 63500000, 0, 3000000]) && U.total.tanpaUmur.rp === 1000000, J([ju(U.total), U.total.tanpaUmur]));
ok('4: lewat tempo: 8–30 hari Rp17.500.000 (Pemasok Satu, lewat 10 hari) · > 30 hari Rp3.000.000 (bon lama, lewat 110 hari) · belum jatuh tempo Rp70.900.000 · tanpa tempo Rp1.000.000',
  J(U.total.lewat.map(function (x) { return x.rp; })) === J([0, 17500000, 3000000]) && U.total.belum.rp === 70900000 && U.total.tanpaTempo.rp === 1000000 && um['Pemasok Satu'].lewatTerlama === 10 && um['Pemasok Dua'].lewatTerlama === 110 && /paling lama 10 hari/.test(um['Pemasok Satu'].lewatTeks), J(U.total));
ok('4: urut yang paling banyak lewat tempo dulu; per pemasok juga menutup', U.daftar[0].pemasok === 'Pemasok Satu' && J(ju(um['Pemasok Satu'])) === J([18900000, 17500000, 0, 0]) && J(ju(um['Pemasok Dua'])) === J([0, 46000000, 0, 3000000]), J(U.daftar.map(function (g) { return [g.pemasok, ju(g)]; })));
var au = pbSusunAturUmur({ umur: ['14', '45', '120'], lewat: ['3', '14'] }, W);
ok('4: setelan owner = SATU dokumen aturanToko/umurUtang; urutan salah / bukan angka ditolak; kosong semua = bawaan', !au.tolak && au.dokumen.length === 1 && au.dokumen[0].koleksi === 'aturanToko' && au.dokumen[0].data.id === 'umurUtang' && J(au.dokumen[0].data.umurBatas) === '[14,45,120]'
  && !!pbSusunAturUmur({ umur: ['30', '7', '90'] }, W).tolak && !!pbSusunAturUmur({ lewat: ['x', '9'] }, W).tolak && J(pbSusunAturUmur({ umur: [], lewat: [] }, W).dokumen[0].data.umurBatas) === '[7,30,90]', J(au));
aturDengan([CATAT, au.dokumen[0].data]); var U2 = pbUmurUtang(KINI);
ok('4: batas owner 14 · 45 · 120 & lewat 3 · 14: umur ≤ 14 hari Rp24.900.000 (k6, k7) · 15–45 hari Rp63.500.000 (k4 umur 15, k3) · lewat 4–14 hari Rp17.500.000; tetap menutup', U2.atur.dariOwner && U2.kelompok[0].label === '≤ 14 hari' && U2.total.umur[0].rp === 24900000 && U2.total.umur[1].rp === 63500000 && U2.total.lewat[1].label === 'lewat 4–14 hari' && U2.total.lewat[1].rp === 17500000 && U2.menutup, J([U2.kelompok, ju(U2.total), U2.total.lewat]));
aturDengan([CATAT]);

// ==================== 5 · PIUTANG DI GARIS JATUH TEMPO (A5) ====================
var BS = bpSusunBon(KINI); var GP = pbGarisPiutang(BS, KINI); var urut = GP.garis.map(function (g) { return g.tanda ? '#' + g.kelas : g.piutang ? 'p:' + g.nama : g.id; });
ok('5: prasyarat: uang toko sekarang Rp85.000.000 (titik kas hari ini)', BS.kas === 85000000, BS.kas);
ok('5: piutang yang jatuh tempo hari ini s.d. bon terakhir (8 Des) ikut sebagai masuk: Bu Hari (hari ini) Rp200.000 · Bu Nota 24 Nov Rp500.000; Bu Jauh (Januari) tidak digambar',
  GP.nMasuk === 2 && GP.rpMasuk === 700000 && GP.batas === '2026-12-08' && GP.nanti.n === 1 && GP.masuk[0].nama === 'Bu Hari' && /HARI INI/.test(GP.masuk[0].tempoTeks) && /tepat waktu/.test(GP.masuk[1].tempoTeks), J([GP.masuk, GP.nanti]));
ok('5: piutang LEWAT jatuh tempo (Pak Lewat Rp300.000) TIDAK dihitung masuk — disebut di bawah penanda hari ini', GP.lewat.n === 1 && GP.lewat.rp === 300000 && urut.indexOf('#piutang-lewat') === urut.indexOf('#kini') + 1, J(urut));
ok('5: urutan garis: bon lewat · hari ini · piutang hari ini SESUDAH penanda hari ini · piutang 24 Nov sebelum bon 29 Nov · penanda lama "uang toko habis" sebelum k4 tetap',
  J(urut) === J(['s1', 'k3', '#kini', '#piutang-lewat', 'p:Bu Hari', 'p:Bu Nota', 'k6', '#habis', 'k4', '#habis2', 'k7', '#', 's2']), J(urut));
ok('5: penanda kedua: Rp85.000.000 + piutang Rp700.000 menutup k4 (s.d. Rp85.400.000) tapi habis di k7; kalimat menyebutnya', GP.kurang2 && /pun, uang toko TIDAK cukup/.test(GP.cukupTeks2) && /kurang Rp5\.700\.000/.test(GP.garis.filter(function (g) { return g.kelas === 'habis2'; })[0].teks), J([GP.cukupTeks2, GP.garis.filter(function (g) { return g.kelas === 'habis2'; })]));
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-11-18', laci: 20000000, brankas: 0, rekening: 0, amplop: 0, diubahPada: '2026-11-18T01:00:00.000Z' }]);
var BS2 = bpSusunBon(KINI); var GP2 = pbGarisPiutang(BS2, KINI); var hb2 = GP2.garis.filter(function (g) { return g.tanda && /^habis/.test(g.kelas); });
ok('5: uang toko Rp20.000.000 habis SEBELUM piutang pertama masuk → SATU penanda (penanda lama diberi keterangan, bukan dua penanda berdempetan); objek garis lama tidak diubah',
  BS2.kas === 20000000 && hb2.length === 1 && hb2[0].kelas === 'habis' && hb2[0].gabung && /piutang yang jatuh tempo sebelumnya pun tidak menutup/.test(hb2[0].teks) && !BS2.garis.some(function (g) { return g.gabung || /pun tidak menutup/.test(g.teks || ''); }) && GP2.kurang2, J(hb2));
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-11-18', laci: 85000000, brankas: 0, rekening: 0, amplop: 0, diubahPada: '2026-11-18T01:00:00.000Z' }]);
ok('5: garis lama (B.garis) TIDAK diubah oleh fungsi ini', J(BS.garis.map(function (g) { return g.tanda ? '#' + g.kelas : g.id; })) === J(['s1', 'k3', '#kini', 'k6', '#habis', 'k4', 'k7', '#', 's2']), J(BS.garis.map(function (g) { return g.tanda ? '#' + g.kelas : g.id; })));

// ==================== 6 · BEBAN GUDANG 7 HARI (B57) ====================
var G = pbBebanGudang(KINI); var stok = stokMerekSaja(ingatStokKarung()); var kgKini = 0; Object.keys(stok).forEach(function (m) { kgKini += Math.max(0, stok[m].sisaKg || 0); });
var lj = lajuLintas(hitungLajuPakai()) || {}; var laju = 0; Object.keys(lj.kgMerk || {}).forEach(function (m) { laju += lj.kgMerk[m] || 0; });
var semuaKg = 0; var SK = ingatStokKarung(); Object.keys(SK).forEach(function (m) { semuaKg += Math.max(0, SK[m].sisaKg || 0); });
ok('6: buku wadah literan (Wadah A1 40 kg) TIDAK ikut isi gudang', SK['Wadah A1'] && dekat(SK['Wadah A1'].sisaKg, 40) && dekat(G.kgKini, semuaKg - 40, 0.01), J([SK['Wadah A1'], G.kgKini, semuaKg]));
ok('6: 7 hari mulai hari ini; isi gudang = beras karung buku sekarang; laju = laju pakai mesin (lintas arsip)', G.hari.length === 7 && G.hari[0].iso === iso && G.hari[6].iso === '2026-11-24' && dekat(G.kgKini, kgKini, 0.01) && dekat(G.laju, laju, 0.01) && /^Hari ini/.test(G.hari[0].label) && /^Besok/.test(G.hari[1].label), J([G.kgKini, kgKini, G.laju, laju]));
ok('6: masuk di tanggal janji TERAKHIR (digeser 19 → 20 Nov): Jumat 20 Nov 2.500 kg, 1 kedatangan; hari lain kosong', G.hari[2].masuk.n === 1 && G.hari[2].masuk.kg === 2500 && G.hari[1].masuk.n === 0 && G.nMasuk === 1 && G.masukKg === 2500 && /^Jumat/.test(G.hari[2].label), J(G.hari.map(function (h) { return [h.iso, h.masuk.n, h.masuk.kg]; })));
ok('6: lewat janji (17 Nov, telat 1 hari) & tanpa janji disebut terpisah; janji 1 Des di luar 7 hari', G.lewatJanji.length === 1 && G.lewatJanji[0].id === 'ps3' && G.lewatJanji[0].telat === 1 && G.tanpaJanji.length === 1 && G.tanpaJanji[0].id === 'ps4' && G.jauh.length === 1 && G.jauh[0].id === 'ps6', J([G.lewatJanji, G.tanpaJanji, G.jauh]));
ok('6: keluar = laju + pesanan pelanggan terjadwal (besok 200 kg Angsa untuk Bu Nota); isi akhir hari berjalan', dekat(G.hari[1].keluar.pesanan, 200) && G.hari[1].keluar.siapa[0] === 'Bu Nota' && dekat(G.hari[1].keluar.kg, laju + 200, 0.02) && dekat(G.hari[0].akhir, kgKini - laju, 0.02) && dekat(G.hari[2].akhir, kgKini - 3 * laju - 200 + 2500, 0.05), J(G.hari.slice(0, 3)));

// ==================== 7 · DASBOR (kelompok beli4) ====================
var D4 = dbBeli4(KINI, null);
ok('7: kelompok beli4 bawaan: buku = bulan ini s.d. hari ini, per pemasok = bulan ini; umur & beban sekarang; tanpa galat', !D4.buku.galat && D4.buku.dari === '2026-11-01' && D4.buku.sampai === iso && D4.pemasok.key === '2026-11' && !D4.umur.galat && !D4.beban.galat && D4.periodeNama === 'Bulan ini', J([D4.buku.galat, D4.umur.galat, D4.beban.galat, D4.periode]));
var SR = dbSaring({ id: 'bulanLalu' }, KINI); var D5 = dbBeli4(KINI, SR);
ok('7: ikut saringan Dasbor: Bulan lalu = buku Oktober & per pemasok Oktober', D5.buku.dari === '2026-10-01' && D5.buku.sampai === '2026-10-31' && D5.pemasok.key === '2026-10' && D5.saring === SR.nama && DB_IKUT_SARING.indexOf('beli4') >= 0 && DB_TAMBAHAN.indexOf('beli4') >= 0, J([D5.buku.dari, D5.pemasok.key]));
var kat = {}; WG_KATALOG.forEach(function (k) { kat[k.id] = k; });
ok('7: empat kartu di katalog (kartu Dasbor, TIDAK di bawaan): Buku pembelian · Pembelian per pemasok · Umur utang pemasok · Beban gudang 7 hari', ['kBukuBeli', 'kPemasokBeli', 'kUmurUtang', 'kBeban'].every(function (id) { return kat[id] && kat[id].jenis === 'lama' && kat[id].kel === 'beli4'; })
  && !WG_BAWAAN.some(function (x) { return /^(kBukuBeli|kPemasokBeli|kUmurUtang|kBeban)$/.test(x.id); }) && WG_KATALOG.length <= WG_MAKS, J(WG_KATALOG.length));

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
})();
"""

STATIS = [
    ('Dasbor: empat kartu P4 digambar & terdaftar', 'dasbor', ["function kartuBukuBeli(X)", "function kartuPemasokBeli(X)", "function kartuUmurUtang(X)", "function kartuBeban(X)",
        "kBukuBeli: () => kartuBukuBeli(D.beli4), kPemasokBeli: () => kartuPemasokBeli(D.beli4), kUmurUtang: () => kartuUmurUtang(D.beli4), kBeban: () => kartuBeban(D.beli4) };",
        "kepala('Umur utang pemasok', 'Sekarang · ' + U.total.n + ' bon', 'sumber:umur4', U.sumber, U.tujuan, tetap())", "kepala('Beban gudang 7 hari', 'Mulai hari ini · perkiraan', 'sumber:beban4', G.sumber, G.tujuan, tetap())"]),
    ('Dasbor: katalog kartu P4 (tidak di bawaan)', 'wg', ["LAMA('kBukuBeli', 'Buku pembelian', 'beli4', 12), LAMA('kPemasokBeli', 'Pembelian per pemasok', 'beli4', 12), LAMA('kUmurUtang', 'Umur utang pemasok', 'beli4', 6), LAMA('kBeban', 'Beban gudang 7 hari', 'beli4', 6),"]),
    ('Dasbor: kelompok beli4 ikut saringan & dipanaskan', 'dl', ["DB_KELOMPOK.beli4 = ['pembelian & pemasok', dbBeli4]; DB_IKUT_SARING.push('beli4'); DB_TAMBAHAN.push('beli4'); DB_PANAS.push('beli4');",
        "import { pbBukuPembelian, pbPemasokBulan, pbUmurUtang, pbBebanGudang } from './pembelian-logika.js';"]),
    ('Bon pemasok: piutang di garis (saklar bawaan nyala) + kartu umur utang + atur kelompok', 'harga', ["import * as PB from './pembelian-logika.js';", "garisPiutang: true, umAtur: null });",
        "const GP = sP.garisPiutang ? PB.pbGarisPiutang(B, kini()) : null; const garisP = GP ? GP.garis : B.garis;", "g.piutang ? barisPiutang(g) :", "${gambarUmurUtang(s)}\n      ${gambarHariBayar()}",
        "umSimpan: async () => { await tulis(PB.pbSusunAturUmur(st().umAtur, waktu())); },", 'data-aksi="bpGarisPiutang"', "'aturB', 'umAtur', 'aturL', 'bayar',"]),
    ('Stok › Barang masuk: tanda tarif di lembar owner & tablet + Atur tarif (owner)', 'stok', ["import * as PB from './pembelian-logika.js';", "function gambarTarifTanda(d) {", "function gambarAturTarif(s) {",
        "${gambarAturUkuran(s)}\n      ${gambarAturTarif(s)}", "if (T.keadaan === 'tanpaTarif') return bukanOwner(opsi.akun ? opsi.akun() : null) ? '' :", "tbSimpan: async () =>", "PB.pbSusunTarif({ mulai: x.tbMulai, baris }, waktu())",
        "['tbKetik', (v) => !!(v && Object.keys(v).length)], 'tbMulai'"]),
    ('CSS bergerak (gerak hidup) + reduced-motion dihormati', 'cssh', ['@keyframes bnUmurTumbuh', '.layar-harga .bn-titik.piutang', '@media (prefers-reduced-motion: reduce) { .layar-harga .bn-umur-bilah i { animation: none; } }']),
    ('CSS Dasbor P4 memakai animasi tumbuh yang sudah ada', 'css', ['.layar-ringkasan .db-p4-bilah', '.layar-ringkasan .db-p4-masuk', '.layar-ringkasan .db-p4-u4']),
    ('modul baru dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/pembelian-logika.js">']),
    ('bundel uji memuat pembelian-logika otomatis', 'bundel', ["PB_MODUL = 'baru/js/layar/pembelian-logika.js'", "PB_PEMAKAI = ('dasbor-logika.js', 'harga.js', 'stok.js')"]),
    ('pages.yml menjalankan uji ini + kontrolnya', 'pages', ['python3 alat-uji/uji_pembelian_p4.py && python3 alat-uji/uji_pembelian_p4.py --kontrol']),
    ('BACA-DULU: bagian Paket P4', 'baca', ['## Paket P4 · Pembelian, pemasok & utang']),
    ('upah borongan TIDAK dibangun (keputusan owner): satuan upah tetap hari · minggu · bulan', 'upah', ["export const SATUAN_UPAH = [['hari', 'per hari'], ['minggu', 'per minggu'], ['bulan', 'per bulan']];"]),
]
RUSAK = [
    ('tarif: kedatangan lama memakai tarif terbaru', PB, "if (x.berat === b && x.mulai <= String(iso || '')) t = x;", "if (x.berat === b) t = x;"),
    ('tarif: ongkos kirim dianggap upah bongkar', PB, "const bongkar = semua - ongkir;", "const bongkar = semua;"),
    ('tarif: bal / kemasan / ditolak ikut dihitung', PB, "if (!r || r.bentuk === 'bal' || r.masuk === 'kemasan' || r.ditolak) return;", "if (!r) return;"),
    ('tarif: tablet titipan ditandai beda', PB, "if (b && b.dariTablet && !bongkar && C.keadaan === 'kosong')", "if (false)"),
    ('tarif: simpan menghapus kolom catatStok lain', PB, "const data = Object.assign({}, lama, { id: 'catatStok', tanggal: w.tanggal, jam: w.jam }); data[PB_TARIF_KOLOM] = daftar;", "const data = { id: 'catatStok', tanggal: w.tanggal, jam: w.jam }; data[PB_TARIF_KOLOM] = daftar;"),
    ('tarif: tanggal sama tidak mengganti', PB, "const daftar = pbTarifDaftar().filter((x) => !kunci[x.mulai + '|' + pbBeratKunci(x.berat)])", "const daftar = pbTarifDaftar().filter((x) => true)"),
    ('buku: sisa bon = nilai bon', PB, "const sisa = V.bon ? (sb ? sb.sisa : 0) : 0;", "const sisa = V.bon ? (sb ? sb.nilai : 0) : 0;"),
    ('buku: stok awal dihitung belanja', PB, "if (V.jenis === 'dicatat') { dicatat += V.rp; nDicatat += 1; return; }", "if (V.jenis === 'dicatat') { dicatat += V.rp; nDicatat += 1; }"),
    ('buku: pesanan batal ikut rata-rata', PB, "const psHidup = ps.filter((p) => p.status !== 'batal');", "const psHidup = ps;"),
    ('pemasok: bulan berjalan dibanding bulan lalu penuh', PB, "const banding = berjalan ? 'laluSama' : 'lalu';", "const banding = 'lalu';"),
    ('pemasok: pesanan batal ikut rupiah', PB, "if (p.status !== 'batal' && Number(p.rp) > 0) { g.rp += Number(p.rp); g.nHarga += 1; }", "if (Number(p.rp) > 0) { g.rp += Number(p.rp); g.nHarga += 1; }"),
    ('umur: bon tanpa tanggal masuk ≤ 7 hari', PB, "const u = b.umur === null || b.umur === undefined || !isFinite(b.umur) ? null : Number(b.umur);", "const u = Number(b.umur) || 0;"),
    ('umur: lewat dihitung dari umur, bukan jatuh tempo', PB, "const h = -b.sisaHari;", "const h = b.umur;"),
    ('umur: setelan owner diabaikan', PB, "umurBatas: pbBatasSah(u, 3) ? u : PB_UMUR_BAWAAN.umurBatas.slice()", "umurBatas: PB_UMUR_BAWAAN.umurBatas.slice()"),
    ('garis: piutang lewat ikut dihitung masuk', PB, "x.jatuhTempo >= iso && x.jatuhTempo <= batas)", "x.jatuhTempo <= batas)"),
    ('garis: penanda kedua tanpa piutang', PB, "if (g.piutang) jalan += g.sisa;", "if (g.piutang) jalan += 0;"),
    ('garis: dua penanda habis berdempetan', PB, "if (t && t.tanda && t.kelas === 'habis') out[out.length - 1]", "if (false) out[out.length - 1]"),
    ('garis: penanda lama diubah di tempat', PB, "out[out.length - 1] = Object.assign({}, t, {", "out[out.length - 1] = Object.assign(t, {"),
    ('garis: piutang hari sama didahulukan dari bon', PB, "while (i < masuk.length && masuk[i].jatuh < tgl)", "while (i < masuk.length && masuk[i].jatuh <= tgl)"),
    ('beban: janji PERTAMA, bukan yang digeser', PB, "const tgl = J.akhir || J.awal || '';", "const tgl = J.awal || '';"),
    ('beban: pesanan pelanggan tidak ikut keluar', PB, "h.keluar.pesanan += Number(x.n) || 0;", "h.keluar.pesanan += 0;"),
    ('beban: wadah literan ikut isi gudang', PB, "const stok = stokMerekSaja(ingatStokKarung());", "const stok = ingatStokKarung();"),
    ('dasbor: buku tidak ikut saringan', DL, "buku: aman(() => pbBukuPembelian(dari, sampai, kini))", "buku: aman(() => pbBukuPembelian(iso.slice(0, 8) + '01', iso, kini))"),
    ('dasbor: katalog penuh memotong kartu', WG, "export const WG_MAKS = 80;", "export const WG_MAKS = 60;"),
    ('stok-catat: Atur menghapus tarif', SC, "const data = Object.assign({}, lama, { id: 'catatStok', tanggal: w.tanggal, jam: w.jam, minKarung: m.nilai,", "const data = Object.assign({}, { id: 'catatStok', tanggal: w.tanggal, jam: w.jam, minKarung: m.nilai,"),
]
RUSAK_STATIS = [
    ('saklar piutang mati bawaan', 'harga', "garisPiutang: true, umAtur: null });", "garisPiutang: false, umAtur: null });"),
    ('tanda tarif hilang dari Barang masuk', 'stok', "function gambarTarifTanda(d) {", "function gambarTarifTandaLama(d) {"),
    ('tautan tulis tarif untuk staf', 'stok', "if (T.keadaan === 'tanpaTarif') return bukanOwner(opsi.akun ? opsi.akun() : null) ? '' :", "if (T.keadaan === 'tanpaTarif') return"),
    ('kartu Dasbor tidak terdaftar', 'dasbor', "kBeban: () => kartuBeban(D.beli4) };", "};"),
    ('modul tidak dipramuat', 'index', '<link rel="modulepreload" href="js/layar/pembelian-logika.js">', ''),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_pembelian_p4.py && python3 alat-uji/uji_pembelian_p4.py --kontrol', 'true'),
    ('modul logika menulis koleksi lain', 'pb', "return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { tbBuka: false", "return { dokumen: [{ koleksi: 'batchMasuk', data }], patch: { tbBuka: false"),
    ('modul logika menyentuh DOM', 'pb', "export function pbTarifDaftar() {", "export function pbTarifDaftar() { document.title = 'x';"),
    ('komentar // menelan kode', 'pb', "export function pbBebanGudang(kini) {", "// beban\nexport function pbBebanGudang(kini) { // kalimat; const x = 1;\n"),
    ('rules: staf membaca setelan umur utang', 'rules', "'bukuPegangan', 'rutin'] && staf(['ben', 'karyawan'])", "'bukuPegangan', 'rutin', 'umurUtang'] && staf(['ben', 'karyawan'])"),
    ('upah borongan diam-diam ditambah', 'upah', "export const SATUAN_UPAH = [['hari', 'per hari'], ['minggu', 'per minggu'], ['bulan', 'per bulan']];", "export const SATUAN_UPAH = [['hari', 'per hari'], ['minggu', 'per minggu'], ['bulan', 'per bulan'], ['borongan', 'borongan']];"),
    ('BACA-DULU P4 menyebut rules baru', 'baca', "## Paket P4 · Pembelian, pemasok & utang", "## Paket P4 · Pembelian, pemasok & utang\nrules v27 baru"),
]

ASAP = r"""
(function () {
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(); var iso = hariIniIso(kini); var out = { akhir: iso, galat: [] };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + e); return null; } };
var bln = iso.slice(0, 7); var lalu = (function () { var y = Number(bln.slice(0, 4)), m = Number(bln.slice(5, 7)) - 2; var d = new Date(y, m, 1); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0'); })();
var akhirLalu = akhirBulanIso(lalu);
// A57 · B63: buku bulan ini & bulan lalu — Σ = kartu Pembelian
var b1 = aman('buku ini', function () { return pbBukuPembelian(bln + '-01', iso, kini); }), b2 = aman('buku lalu', function () { return pbBukuPembelian(lalu + '-01', akhirLalu, kini); });
out.buku = [b1, b2].map(function (B) { return B ? { n: B.n, menutup: B.menutup, bon: B.bon.n, bonBersisa: B.bon.nSisa, lunas: B.bon.nLunas, langsung: B.langsung.n, tarifAda: B.tarifAda, diarsip: B.diarsip } : null; });
// B62 · B64: per pemasok
var P = aman('per pemasok', function () { return pbPemasokBulan(bln, kini); }); out.pemasok = P ? { n: P.daftar.length, menutup: P.menutup, pesanan: P.total.pesanan.n, datang: P.total.pesanan.datang, menunggu: P.total.pesanan.menunggu, batal: P.total.pesanan.batal } : null;
// B40 · B78
var U = aman('umur', function () { return pbUmurUtang(kini); }); out.umur = U ? { pemasok: U.daftar.length, bon: U.total.n, menutup: U.menutup, nPerUmur: U.total.umur.map(function (e) { return e.n; }), tanpaTanggal: U.total.tanpaUmur.n, nLewat: U.total.lewat.map(function (x) { return x.n; }), lewatTerlama: U.total.lewatTerlama } : null;
// A5
var BS = aman('bon pemasok', function () { return bpSusunBon(kini); }); var GP = BS ? aman('garis piutang', function () { return pbGarisPiutang(BS, kini); }) : null;
out.garis = GP ? { baris: GP.garis.length, lama: BS.garis.length, piutangMasuk: GP.nMasuk, piutangLewat: GP.lewat.n, nanti: GP.nanti.n, bonUtuh: GP.garis.filter(function (g) { return !g.tanda && !g.piutang; }).length === BS.garis.filter(function (g) { return !g.tanda; }).length } : null;
// B57
var G = aman('beban', function () { return pbBebanGudang(kini); }); out.beban = G ? { hari: G.hari.length, masuk: G.nMasuk, lewatJanji: G.lewatJanji.length, tanpaJanji: G.tanpaJanji.length, habis: !!G.kurang } : null;
// A25: tarif CONTOH (Rp2.000 / karung 50 kg, Rp1.500 / karung 25 kg sejak awal catatan) — jalur cek jalan di semua kedatangan toko; hanya jumlah keadaan yang dicetak
var cat = (CAD.aturanToko || []).find(function (d) { return d.id === 'catatStok'; }) || { id: 'catatStok' };
pasok('aturanToko', (CAD.aturanToko || []).filter(function (d) { return d.id !== 'catatStok'; }).concat([Object.assign({}, cat, { tarifBongkar: [{ mulai: '2020-01-01', berat: 50, rp: 2000 }, { mulai: '2020-01-01', berat: 25, rp: 1500 }] })]));
var hit = {}; var gT = 0; ambilSemuaBatch().forEach(function (b) { if (b.stokAwal || b.lahirBuku) return; var C = aman('tarif ' + b.id, function () { return pbCekKedatangan(b); }); if (!C) { gT += 1; return; } hit[C.keadaan] = (hit[C.keadaan] || 0) + 1; });
out.tarifContoh = { keadaan: hit, galat: gT };
pasok('aturanToko', CAD.aturanToko || []);
var D4 = aman('dasbor beli4', function () { return dbBeli4(kini, null); }); out.dasbor = D4 ? ['buku', 'pemasok', 'umur', 'beban'].filter(function (k) { return D4[k] && D4[k].galat; }) : null;
print(JSON.stringify(out));
})();
"""


def bundel_js(teks):
    uji_dasbor_sensus.MODUL[:] = MODUL
    return uji_dasbor_sensus.bundel_js(teks)


def jalan(teks):
    r, out = uji_dasbor_sensus.jsc(JAM_BEKU + bundel_js(teks) + '\nvar KOTAK0 = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar GK = ' + json.dumps(KOTAK) + ';\nvar KARTU = ' + json.dumps(KARTU)
                                   + ';\nvar TARIF = ' + json.dumps(TARIF) + ';\n' + SKENARIO)
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], list(h['gagal'])


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    # tulisan: pembelian-logika hanya setelan owner di aturanToko (catatStok.tarifBongkar & umurUtang) — tidak menyentuh uang, stok, bon
    tulis = sorted(set(re.findall(r"koleksi: '(\w+)'", src['pb'])))
    if tulis != ['aturanToko']: g.append('pembelian-logika: menulis selain setelan aturanToko → ' + str(tulis))
    if 'document.' in src['pb'] or 'tulisDokumen' in src['pb'] or 'window.' in src['pb']: g.append('pb: modul logika menyentuh DOM / menulis langsung')
    if src['harga'].count('${gambarTarifTanda(d)}') or src['stok'].count('${gambarTarifTanda(d)}') != 2: g.append('stok: tanda tarif harus di lembar owner DAN tablet (2×)')
    # setelan umur utang owner saja: staf tidak membaca aturanToko/umurUtang (baris baca per dokumen rules tidak berubah)
    m = re.search(r"match /aturanToko/\{id\} \{\s*allow read: if ([^\n]*)", src['rules'])
    if not m or 'umurUtang' in m.group(1): g.append('rules: setelan umur utang terbaca staf (atau aturan aturanToko tidak ketemu)')
    if "['borongan'" in src['upah'] or "'borongan'" in src['upah']: g.append('upah: borongan dibangun padahal owner bilang tidak perlu')
    for k in ('pb', 'dl', 'harga', 'stok', 'dasbor'):
        for n, baris in enumerate(src[k].split('\n')):
            ekor = uji_sisa_sensus.komentar_ekor(baris)
            if ekor and re.search(r"\b[a-zA-Z]\w*: (opsi\.|\(|async |\[|\{|'|`)|;\s*(const|let|return|if)\b|\)\s*=>", ekor): g.append(k + ':' + str(n + 1) + ': komentar // menelan kode → ' + ekor.strip()[:90])
    i = src['baca'].find('## Paket P4')
    j = src['baca'].find('\n## ', i + 1) if i >= 0 else -1
    if i >= 0 and re.search(r'rules v2[7-9]', src['baca'][i:(j if j > i else i + 9000)]): g.append('BACA-DULU menyebut rules baru untuk paket P4 (paket ini tanpa rules)')
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
        r, out = uji_dasbor_sensus.jsc(JAM_BEKU.replace('2026-11-18T14:00:00+07:00', '%sT20:00:00+07:00' % tgl) + bundel_js(teks) + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if r.returncode != 0 or not out.startswith('{'): print('ASAP DATA TOKO: JSC JATUH ' + (r.stderr or r.stdout)[-600:]); g.append('asap')
        else:
            h = json.loads(out)
            beres = (not h['galat'] and all(b and b['menutup'] for b in h['buku']) and h['pemasok'] and h['pemasok']['menutup'] and h['umur'] and h['umur']['menutup'] and h['garis'] and h['garis']['bonUtuh']
                     and h['beban'] and h['beban']['hari'] == 7 and h['tarifContoh']['galat'] == 0 and h['dasbor'] == [])
            # angka RUPIAH toko TIDAK dicetak (repo publik) — hanya keadaan & jumlah
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: buku / per pemasok / umur / garis / beban galat atau tidak menutup')
    sys.exit(1 if g or gs else 0)
