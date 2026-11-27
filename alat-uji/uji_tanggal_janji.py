#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tanggal_janji.py — paket tanggal janji (owner 27 Nov 2026; sensus B55 B58 B60 B61 B65; rules v24). KOTAK PASIR (angka & nama CONTOH, bukan data toko),
jsc saja, TANPA peramban.
  JP  janji pertama: dibetulkan di hari yang sama = salah ketik, digeser sesudahnya = geser (tetap dihitung dari janji pertama); pesanan pelanggan lewat
      riwayat ubah kirimDari → kirimKe; dokumen lama tanpa riwayat = tanggal kirim sekarang.
  PM  dari pemasok (B58 B60 B65): tepat / telat / lewat / menunggu / belum ada tanggal janji, rata-rata & terlama telat, utuh vs sebagian dari jumlah KARUNG
      (kedatangan di hari datangnya, sesudah pesanan, yang belum dipakai pesanan lain; dua trip sehari dijumlah), per pemasok, jendela 90 hari, batal tidak dihitung.
  PL  ke pelanggan (B58 B60 B61): surat jalan (janji dari isian Antar atau pesanan yang diikat — beda tanggal = geser), gagal antar = tidak tepat, nota batal =
      bukan kiriman, pesanan tanpa surat jalan (diantar / jadi nota), isi pesanan vs baris nota.
  LW  B55: daftar lewat janji (pemasok + pelanggan, telat terlama dulu); toleransi owner menggeser tepat / lewat.
  TL  tulis: isi / geser janji pemasok (owner & Penjaga laci lewat penjaga kiriman = rules v24; karyawan, pesanan datang / batal, kolom lain DITOLAK), Belanja
      menulis janji saat kirim + baris WA, surat jalan membawa janjiTanggal (isian / tanggal kirim pesanan / hari itu), ubahan tanggal kirim pesanan tercatat,
      setelan toleransi.
  ASAP: cadangan toko lokal (bila ada) — jumlah pesanan pemasok / pesanan / surat jalan, berapa yang berjanji, ringkasan dua arah (dicetak lokal saja).

    python3 alat-uji/uji_tanggal_janji.py            → N lulus · 0 gagal
    python3 alat-uji/uji_tanggal_janji.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_pesanan, uji_jual_baru  # noqa: E402
JSC = uji_pesanan.JSC
JN = 'baru/js/layar/janji-logika.js'; BL = 'baru/js/layar/belanja-logika.js'; AJ = 'baru/js/layar/antar-logika.js'; PO = 'baru/js/layar/pesanan-logika.js'
AK = 'baru/js/data/akses.js'; JL = 'baru/js/layar/jual-logika.js'; GD = 'baru/js/layar/gudang-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_pesanan.MODUL + ['baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/arsip-logika.js', 'baru/js/layar/wadah-bernama-logika.js',
                                                                     'baru/js/layar/kelas-merek-logika.js', 'baru/js/layar/varian-logika.js', BL, JN, GD])))
SUMBER = {'harga': 'baru/js/layar/harga.js', 'stok': 'baru/js/layar/stok.js', 'laporan': 'baru/js/layar/laporan.js', 'dasbor': 'baru/js/layar/dasbor.js', 'dasborL': 'baru/js/layar/dasbor-logika.js',
          'gudang': GD, 'antarP': 'baru/js/layar/antar-panel.js', 'pesananP': 'baru/js/layar/pesanan-panel.js', 'jual': JL, 'akses': AK, 'rules': 'firestore.rules',
          'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'bundel': 'alat-uji/bundel_baru.py', 'peta': 'alat-uji/peta_akses.py', 'jn': JN, 'dok24': 'docs/uji-rules-v24.md'}
JAM = "var __KINI = new Date('2026-12-10T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"

PA = 'Pemasok Contoh A'; PB = 'Pemasok Contoh B'


def batch(i, pemasok, tanggal, jam, karung, merk='Beras Contoh'):
    return {'id': 'b%s' % i, 'tanggal': tanggal, 'jam': jam, 'pemasok': pemasok, 'caraBayar': 'utang', 'biayaBongkar': 0,
            'merkList': [{'id': 'r%s' % i, 'merk': merk, 'jumlahKarung': karung, 'beratKarung': 50, 'totalKg': karung * 50, 'hargaPerKg': 12000, 'subtotalHarga': karung * 50 * 12000, 'satuan': 'karung'}]}


def pp(i, pemasok, tanggal, jam, karung, riwayat=None, status='menunggu', **lain):
    d = {'id': 'pp%s' % i, 'tanggal': tanggal, 'jam': jam, 'pemasok': pemasok, 'baris': [{'merk': 'Beras Contoh', 'karung': karung, 'berat': 50, 'kg': karung * 50, 'hargaPerKg': 12000}],
         'karung': karung, 'kg': karung * 50, 'rp': karung * 50 * 12000, 'status': status, 'teks': 'Pesanan contoh', 'keNomor': ''}
    if riwayat: d['janjiRiwayat'] = [{'tanggal': t, 'pada': p, 'oleh': 'Owner'} for t, p in riwayat]; d['janjiTanggal'] = riwayat[-1][0]
    d.update(lain); return d


def pj(i, trx, tanggal, jenis, jumlah, **lain):
    d = {'id': 'j%s' % i, 'trxId': trx, 'tanggal': tanggal, 'jam': '10:00', 'caraBayar': 'Tunai', 'jenis': jenis, 'hargaTotal': 100000, 'hppTotalSaatJual': 90000}
    if jenis == 'karung': d.update({'merkSumber': 'Angsa', 'jumlahKarung': jumlah, 'beratKarungAcuan': 50, 'totalKg': jumlah * 50})
    if jenis == 'kemasan': d.update({'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': jumlah, 'totalKg': jumlah * 5})
    d.update(lain); return d


def sj(i, tanggal, status, janji=None, trx=None, **lain):
    d = {'id': 'sj%s' % i, 'noSJ': 'SJ26-TES-%04d' % i, 'tanggal': tanggal, 'jam': '09:00', 'trxIdJual': trx or 't-sj%s' % i, 'namaPelanggan': 'Pembeli Contoh %s' % i, 'status': status,
         'riwayatStatus': [{'status': 'berangkat', 'pada': tanggal + 'T02:00:00.000Z'}], 'isi': [], 'nilaiNota': 100000, 'ongkir': 0, 'bayarDiTempat': False, 'tagihRp': 0}
    if janji: d['janjiTanggal'] = janji
    d.update(lain); return d


BARIS_ANGSA = {'jalur': 'karung', 'kunci': 'Angsa', 'berat': 50, 'nama': 'Angsa 50 kg', 'jumlah': 2, 'satuan': 'karung', 'kg': 100}
BARIS_KEMBANG = {'jalur': 'kemasan', 'kunci': 'Kembang|5', 'ukuranKg': 5, 'nama': 'Kembang 5 kg', 'jumlah': 3, 'satuan': 'kemasan', 'kg': 15}

TAMBAH = {
    'batchMasuk': [batch(1, PA, '2026-12-02', '15:00', 10), batch(2, PA, '2026-12-07', '10:00', 8), batch(3, PB, '2026-12-06', '10:00', 4), batch(4, PB, '2026-12-06', '16:00', 2)],
    'pesananPemasok': [
        pp(1, PA, '2026-12-01', '09:00', 10, [('2026-12-02', '2026-12-01T02:10:00.000Z')]),
        pp(2, PA, '2026-12-03', '09:00', 10, [('2026-12-04', '2026-12-03T02:10:00.000Z'), ('2026-12-05', '2026-12-03T08:00:00.000Z'), ('2026-12-07', '2026-12-06T02:00:00.000Z')]),
        pp(3, PA, '2026-12-08', '09:00', 5, [('2026-12-09', '2026-12-08T02:10:00.000Z')]),
        pp(4, PB, '2026-12-05', '09:00', 6),
        pp(5, PB, '2026-12-09', '09:00', 5, [('2026-12-11', '2026-12-09T02:10:00.000Z')]),
        pp(6, PB, '2026-12-04', '09:00', 5, [('2026-12-05', '2026-12-04T02:10:00.000Z')], status='batal'),
        pp(7, PB, '2026-08-01', '09:00', 5, status='datang', datangTanggal='2026-08-02'),
    ],
    'suratJalan': [
        sj(1, '2026-12-02', 'diterima', '2026-12-02', diterimaTanggal='2026-12-02'),
        sj(2, '2026-12-03', 'diterima', '2026-12-03', diterimaTanggal='2026-12-05'),
        sj(3, '2026-12-04', 'gagal', '2026-12-04', riwayatStatus=[{'status': 'berangkat', 'pada': '2026-12-04T02:00:00.000Z'}, {'status': 'gagal', 'pada': '2026-12-04T09:00:00.000Z'}]),
        sj(4, '2026-12-08', 'berangkat', '2026-12-08'),
        sj(5, '2026-12-01', 'diterima', diterimaTanggal='2026-12-01'),
        sj(6, '2026-12-05', 'batal', '2026-12-05'),
        sj(7, '2026-12-06', 'diterima', '2026-12-06', trx='t-ps1', diterimaTanggal='2026-12-06'),
        sj(8, '2026-12-06', 'diterima', '2026-12-06', diterimaTanggal='2026-12-09'),
    ],
    'pesanan': [
        {'id': 'ps1', 'tanggal': '2026-12-01', 'jam': '09:00', 'namaPelanggan': 'Pemesan Contoh 1', 'baris': [BARIS_ANGSA], 'isi': '2 karung Angsa 50 kg', 'tanggalKirim': '2026-12-05', 'status': 'dibayar',
         'trxIdJual': 't-ps1', 'riwayatStatus': [{'status': 'dipesan', 'pada': '2026-12-01T02:00:00.000Z'}, {'status': 'dibayar', 'pada': '2026-12-06T02:00:00.000Z'}]},
        {'id': 'ps2', 'tanggal': '2026-12-02', 'jam': '09:00', 'namaPelanggan': 'Pemesan Contoh 2', 'baris': [BARIS_ANGSA], 'tanggalKirim': '2026-12-07', 'status': 'dipesan', 'trxIdJual': None,
         'riwayatStatus': [{'status': 'dipesan', 'pada': '2026-12-02T02:00:00.000Z'}]},
        {'id': 'ps3', 'tanggal': '2026-12-03', 'jam': '09:00', 'namaPelanggan': 'Pemesan Contoh 3', 'baris': [BARIS_KEMBANG], 'tanggalKirim': '2026-12-06', 'status': 'dibayar', 'trxIdJual': 't-ps3',
         'riwayatStatus': [{'status': 'dipesan', 'pada': '2026-12-03T02:00:00.000Z'}, {'status': 'dibayar', 'pada': '2026-12-06T03:00:00.000Z'}]},
        {'id': 'ps4', 'tanggal': '2026-12-04', 'jam': '09:00', 'namaPelanggan': 'Pemesan Contoh 4', 'baris': [BARIS_ANGSA], 'tanggalKirim': '', 'status': 'dipesan', 'trxIdJual': None,
         'riwayatStatus': [{'status': 'dipesan', 'pada': '2026-12-04T02:00:00.000Z'}]},
        {'id': 'ps5', 'tanggal': '2026-12-02', 'jam': '09:00', 'namaPelanggan': 'Pemesan Contoh 5', 'baris': [BARIS_ANGSA], 'tanggalKirim': '2026-12-08', 'status': 'diantar', 'trxIdJual': None,
         'riwayatStatus': [{'status': 'dipesan', 'pada': '2026-12-02T02:00:00.000Z'}, {'status': 'dipesan', 'pada': '2026-12-02T06:00:00.000Z', 'ubah': True, 'kirimDari': '2026-12-04', 'kirimKe': '2026-12-05'},
                           {'status': 'dipesan', 'pada': '2026-12-04T02:00:00.000Z', 'ubah': True, 'kirimDari': '2026-12-05', 'kirimKe': '2026-12-08'}, {'status': 'diantar', 'pada': '2026-12-08T04:00:00.000Z'}]},
        {'id': 'ps6', 'tanggal': '2026-12-02', 'jam': '09:00', 'namaPelanggan': 'Pemesan Contoh 6', 'baris': [BARIS_ANGSA], 'tanggalKirim': '2026-12-03', 'status': 'batal', 'trxIdJual': None, 'riwayatStatus': []},
    ],
    'penjualanTambah': [pj(1, 't-ps1', '2026-12-06', 'karung', 2), pj(2, 't-ps3', '2026-12-06', 'kemasan', 2), pj(3, 't-sj8', '2026-12-06', 'kemasan', 1, dibatalkan=True), pj(4, 't-sj1', '2026-12-02', 'kemasan', 1)],
}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
var J = function (x) { return JSON.stringify(x); };
var nId = 9000; var W = { tanggal: '2026-12-10', jam: '10:00', kini: '2026-12-10T03:00:00.000Z', kodePerangkat: 'TES', idUnik: function () { nId += 1; return nId; } };
var KINI = new Date('2026-12-10T10:00:00+07:00');
var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
var BEN = keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true });
var KRY = keadaanAkun('kry.contoh@tokoberasmiqbal.web.app', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true });
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
pasok('batchMasuk', KOTAK.batchMasuk.concat(TAMBAH.batchMasuk)); pasok('penjualan', KOTAK.penjualan.concat(TAMBAH.penjualanTambah));
pasok('pesananPemasok', JSON.parse(J(TAMBAH.pesananPemasok))); pasok('suratJalan', JSON.parse(J(TAMBAH.suratJalan))); pasok('pesanan', JSON.parse(J(TAMBAH.pesanan)));
pasok('aksesAkun', [{ id: 'uid-ben', uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true }, { id: 'uid-kry', uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true }]);
setelSumber('cadangan', 'kotak pasir');
var hak = function (akun) { return Object.assign({}, (ssAtur('peran').hak || {})[akun.peran] || {}, { jatahNego: ngJatah(akun) }); };
var atribusi = function (akun, d, ada) { return beriAtribusiAkun(d, akun, { perangkat: 'p-uji', kini: W.kini }, ada); };
var kirimUbah = function (akun, koleksi, lama, baru) { return periksaKiriman(akun, [{ koleksi: koleksi, data: atribusi(akun, baru, true), ada: true, lama: lama }], [], hak(akun), KINI); };
var cari = function (D, id) { return D.find(function (x) { return x.id === id; }) || null; };

// ---------- JP · janji pertama ----------
var U1 = jnJanjiDariUrutan([{ nilai: '2026-12-04', pada: '2026-12-03T02:10:00.000Z' }, { nilai: '2026-12-05', pada: '2026-12-03T08:00:00.000Z' }, { nilai: '2026-12-07', pada: '2026-12-06T02:00:00.000Z' }]);
ok('JP1 dibetulkan di hari yang sama (4 → 5 Des) = janji pertama 5 Des; digeser hari lain (→ 7 Des) = geser', U1.awal === '2026-12-05' && U1.akhir === '2026-12-07' && U1.geser.length === 1 && U1.geser[0].dari === '2026-12-05' && U1.geser[0].ke === '2026-12-07', J(U1));
var U2 = jnJanjiDariUrutan([{ nilai: '', pada: '2026-12-01T02:00:00.000Z' }, { nilai: '2026-12-03', pada: '2026-12-02T02:00:00.000Z' }]);
ok('JP2 kosong lalu diisi hari lain = janji pertama yang diisi itu (mengisi bukan geser)', U2.awal === '2026-12-03' && U2.geser.length === 0, J(U2));
var U3 = jnJanjiDariUrutan([{ nilai: '2026-12-03', pada: '2026-12-02T02:00:00.000Z' }, { nilai: '', pada: '2026-12-02T05:00:00.000Z' }]);
ok('JP3 diisi lalu dikosongkan di hari yang sama = belum ada tanggal janji', U3.awal === '' && jnKataJanji(U3) === 'belum ada tanggal janji', J(U3));
ok('JP4 tanggal cacat (31 Nov, "3 Des") tidak dianggap janji', !jnTanggalSah('2026-11-31') && !jnTanggalSah('3 Des') && jnTanggalSah('2026-12-31'));
var P5 = jnJanjiPesanan(TAMBAH.pesanan[4]);
ok('JP5 pesanan: riwayat ubah kirimDari → kirimKe — 4 → 5 Des di hari dibuat (salah ketik), → 8 Des dua hari kemudian (geser)', P5.awal === '2026-12-05' && P5.akhir === '2026-12-08' && P5.geser.length === 1, J(P5));
var P6 = jnJanjiPesanan({ tanggal: '2026-12-01', jam: '09:00', tanggalKirim: '2026-12-09', riwayatStatus: [{ status: 'dipesan', pada: '2026-12-01T02:00:00.000Z' }, { status: 'dipesan', pada: '2026-12-03T02:00:00.000Z', ubah: true }] });
ok('JP6 pesanan diubah sebelum paket ini (riwayat ubah tanpa kirimDari): tanggal kirim sekarang = janji sejak dibuat', P6.awal === '2026-12-09' && P6.geser.length === 0, J(P6));

// ---------- PM · dari pemasok ----------
var SP = jnPemasokSemua(KINI); var M1 = cari(SP, 'pp1'), M2 = cari(SP, 'pp2'), M3 = cari(SP, 'pp3'), M4 = cari(SP, 'pp4'), M5 = cari(SP, 'pp5'), M6 = cari(SP, 'pp6');
ok('PM1 janji 2 Des, datang 2 Des (kedatangan 15.00 sesudah pesan): TEPAT, 10/10 karung UTUH', M1.keadaan === 'tepat' && M1.telat === 0 && M1.isi === 'utuh' && M1.datang === 10, J(M1));
ok('PM2 janji pertama 5 Des (dibetulkan hari itu), digeser ke 7 Des, datang 7 Des: TELAT 2 hari (dihitung dari janji pertama), 8/10 karung SEBAGIAN', M2.keadaan === 'telat' && M2.telat === 2 && M2.isi === 'sebagian' && M2.datang === 8 && M2.pesan === 10 && M2.janji.geser.length === 1, J(M2));
ok('PM3 janji 9 Des, hari ini 10 Des, belum datang: LEWAT janji 1 hari', M3.keadaan === 'lewat' && M3.telat === 1 && !M3.sampai, J(M3));
ok('PM4 tanpa janji, dua trip sehari (4 + 2 karung) = 6/6 UTUH; keadaan "belum ada tanggal janji" (tidak tepat, tidak telat)', M4.keadaan === 'tanpaJanji' && M4.isi === 'utuh' && M4.datang === 6 && M4.nKedatangan === 2, J(M4));
ok('PM5 janji 11 Des, hari ini 10 Des: MENUNGGU', M5.keadaan === 'menunggu', J(M5));
ok('PM6 pesanan batal: keadaan batal, tidak dihitung', M6.keadaan === 'batal', J(M6));
var RP9 = jnPemasok(KINI); var R = RP9.ringkas;
ok('PM7 ringkas 90 hari: 1 dari 2 tepat (50 %), telat rata-rata 1 hari (0 + 2), terlama 2; utuh 2 dari 3; 1 lewat, 1 menunggu, 1 belum ada janji, 1 digeser; pesanan Agustus di luar jendela',
  R.tepat === 1 && R.telat === 1 && R.n === 2 && Math.round(R.pct) === 50 && R.rataTelat === 1 && R.maksTelat === 2 && R.utuh === 2 && R.sebagian === 1 && R.lewat === 1 && R.menunggu === 1 && R.tanpaJanji === 1 && R.digeser === 1 && R.semua === 5, J(R));
var pA = RP9.perPemasok.find(function (p) { return p.nama === 'Pemasok Contoh A'; }); var pB = RP9.perPemasok.find(function (p) { return p.nama === 'Pemasok Contoh B'; });
ok('PM8 per pemasok (B65): A = 1/2 tepat, 1 lewat; B = belum ada yang berjanji & datang, 1 menunggu, 1 tanpa janji', pA && pA.ringkas.tepat === 1 && pA.ringkas.n === 2 && pA.ringkas.lewat === 1 && pB && pB.ringkas.n === 0 && pB.ringkas.menunggu === 1 && pB.ringkas.tanpaJanji === 1, J([pA && pA.ringkas, pB && pB.ringkas]));
ok('PM9 kalimat menyebut yang tanpa janji & geser (tidak dianggap tepat)', /1 dari 2 pesanan datang tepat janji/.test(RP9.kalimat) && /belum ada tanggal janji \(tidak dihitung\)/.test(RP9.kalimat) && /digeser/.test(RP9.kalimat), RP9.kalimat);
var simpanPP = cacheMentah('pesananPemasok').slice(), simpanB = cacheMentah('batch').slice();
pasok('pesananPemasok', simpanPP.concat([{ id: 'pc1', tanggal: '2026-12-04', jam: '09:00', pemasok: 'Pemasok Contoh C', karung: 5, status: 'menunggu', janjiTanggal: '2026-12-05', janjiRiwayat: [{ tanggal: '2026-12-05', pada: '2026-12-04T02:10:00.000Z' }] },
  { id: 'pc2', tanggal: '2026-12-04', jam: '10:00', pemasok: 'Pemasok Contoh C', karung: 5, status: 'menunggu', janjiTanggal: '2026-12-05', janjiRiwayat: [{ tanggal: '2026-12-05', pada: '2026-12-04T03:10:00.000Z' }] }]));
pasok('batchMasuk', simpanB.concat([{ id: 'bc1', tanggal: '2026-12-05', jam: '11:00', pemasok: 'Pemasok Contoh C', caraBayar: 'utang', biayaBongkar: 0, merkList: [{ id: 'rc1', merk: 'Beras Contoh', jumlahKarung: 5, beratKarung: 50, totalKg: 250, hargaPerKg: 12000, subtotalHarga: 3000000, satuan: 'karung' }] }]));
var C1 = cari(jnPemasokSemua(KINI), 'pc1'), C2 = cari(jnPemasokSemua(KINI), 'pc2');
ok('PM11 dua pesanan sebelum SATU kedatangan: pesanan pertama 5/5 utuh, pesanan kedua tepat waktu menurut aturan datang Belanja tapi isinya "tidak terukur" (kedatangan tidak dipakai dua kali)',
  C1 && C1.isi === 'utuh' && C1.datang === 5 && C2 && C2.keadaan === 'tepat' && C2.isi === 'tidakTerukur' && C2.datang === null, J([C1, C2]));
pasok('pesananPemasok', simpanPP); pasok('batchMasuk', simpanB);
ok('PM10 jendela 180 hari ikut pesanan Agustus (datang ditandai tanpa Barang masuk → isi "tidak terukur", tanpa janji)', jnPemasok(KINI, 180).ringkas.semua === 6 && jnPemasok(KINI, 180).ringkas.tidakTerukur === 1, J(jnPemasok(KINI, 180).ringkas));

// ---------- PL · ke pelanggan ----------
var SL = jnPelangganSemua(KINI); var A = function (id) { return cari(SL, id); };
ok('PL1 surat jalan janji 2 Des diterima 2 Des: TEPAT; tanpa pesanan = tanpa pembanding isi (bukan "tidak terukur")', A('sj1').keadaan === 'tepat' && A('sj1').telat === 0 && A('sj1').isi === '', J(A('sj1')));
ok('PL2 janji 3 Des diterima 5 Des: TELAT 2', A('sj2').keadaan === 'telat' && A('sj2').telat === 2, J(A('sj2')));
ok('PL3 gagal antar = tidak tepat janji', A('sj3').keadaan === 'gagal', J(A('sj3')));
ok('PL4 masih di jalan, janji 8 Des, hari ini 10 Des: LEWAT 2', A('sj4').keadaan === 'lewat' && A('sj4').telat === 2, J(A('sj4')));
ok('PL5 surat jalan lama tanpa janji = belum ada tanggal janji', A('sj5').keadaan === 'tanpaJanji', J(A('sj5')));
ok('PL6 surat jalan batal & surat jalan yang notanya dibatalkan = bukan kiriman', !A('sj6') && !A('sj8'), J([A('sj6'), A('sj8')]));
ok('PL7 surat jalan dari pesanan (janji pesanan 5 Des, isian Antar 6 Des = geser), diterima 6 Des: TELAT 1; 2/2 karung Angsa = UTUH; pesanannya tidak dihitung dua kali',
  A('sj7').keadaan === 'telat' && A('sj7').telat === 1 && A('sj7').janji.awal === '2026-12-05' && A('sj7').janji.geser.length === 1 && A('sj7').isi === 'utuh' && !A('ps1'), J([A('sj7'), A('ps1')]));
ok('PL8 pesanan belum dikirim, tanggal kirim 7 Des: LEWAT 3', A('ps2').keadaan === 'lewat' && A('ps2').telat === 3, J(A('ps2')));
ok('PL9 pesanan jadi nota 6 Des (janji 6 Des): TEPAT; Kembang 2 dari 3 = SEBAGIAN', A('ps3').keadaan === 'tepat' && A('ps3').isi === 'sebagian' && A('ps3').datang === 0 && A('ps3').pesan === 1, J(A('ps3')));
ok('PL10 pesanan tanpa tanggal kirim = belum ada tanggal janji; pesanan batal tidak dihitung', A('ps4').keadaan === 'tanpaJanji' && !A('ps6'), J([A('ps4'), A('ps6')]));
ok('PL11 pesanan diantar 8 Des, janji pertama 5 Des (digeser ke 8): TELAT 3', A('ps5').keadaan === 'telat' && A('ps5').telat === 3 && A('ps5').janji.geser.length === 1, J(A('ps5')));
var RA = jnPelanggan(KINI).ringkas;
ok('PL12 ringkas antar: 2 tepat dari 6 (dengan 1 gagal), telat rata-rata 1,2 hari, terlama 3; 2 lewat; 2 tanpa janji; utuh 1 dari 2; 2 digeser',
  RA.tepat === 2 && RA.telat === 3 && RA.gagal === 1 && RA.n === 6 && Math.abs(RA.rataTelat - 1.2) < 1e-9 && RA.maksTelat === 3 && RA.lewat === 2 && RA.tanpaJanji === 2 && RA.utuh === 1 && RA.sebagian === 1 && RA.digeser === 2, J(RA));

// ---------- LW · lewat janji (B55) & toleransi ----------
var L = jnLewat(KINI);
ok('LW1 lewat janji: pesanan 2 (3 hari) · surat jalan 4 (2 hari) · Pemasok Contoh A (1 hari), terlama dulu; tujuan ke layarnya',
  J(L.map(function (x) { return x.id; })) === '["ps2","sj4","pp3"]' && L[0].tujuan.lembar === 'pesanan' && L[1].tujuan.lembar === 'antar' && L[2].tujuan.keluarga === 'belanja', J(L.map(function (x) { return [x.id, x.telat, x.tujuan]; })));
var T0 = gdTugas(KINI, W).daftar.find(function (x) { return x.id === 'janji'; });
ok('LW2 Stok › Tugas gudang: baris "Lewat janji" = 3, merah, menuju pesanan', T0 && T0.n === 3 && T0.awas && T0.tujuan.lembar === 'pesanan', J(T0));
pasok('aturanToko', cacheMentah('aturan').concat([{ id: 'janji', tolPemasok: 1, tolAntar: 2 }]));
ok('LW3 toleransi owner (pemasok 1, antar 2): janji pemasok 9 Des belum lewat, surat jalan telat 2 jadi tepat, yang di jalan sejak 8 Des belum lewat',
  cari(jnPemasokSemua(KINI), 'pp3').keadaan === 'menunggu' && cari(jnPelangganSemua(KINI), 'sj2').keadaan === 'tepat' && cari(jnPelangganSemua(KINI), 'sj4').keadaan === 'menunggu' && jnLewat(KINI).length === 1, J(jnLewat(KINI).map(function (x) { return x.id; })));
ok('LW4 setelan dibaca: dariOwner & angka', jnAtur().tolPemasok === 1 && jnAtur().tolAntar === 2 && jnAtur().dariOwner.antar, J(jnAtur()));
pasok('aturanToko', cacheMentah('aturan').filter(function (d) { return d.id !== 'janji'; }));
ok('LW5 tanpa setelan: bawaan 0 hari', jnAtur().tolPemasok === 0 && jnAtur().tolAntar === 0 && !jnAtur().dariOwner.pemasok);
var SA = jnSusunAtur({ tolPemasok: '1', tolAntar: '' }, W);
ok('LW6 simpan toleransi: aturanToko/janji, kosong = tetap; di luar 0–14 ditolak', SA.dokumen && SA.dokumen[0].koleksi === 'aturanToko' && SA.dokumen[0].data.tolPemasok === 1 && SA.dokumen[0].data.tolAntar === 0
  && !!jnSusunAtur({ tolPemasok: '15' }, W).tolak && !!jnSusunAtur({ tolAntar: '1,5' }, W).tolak, J(SA));

// ---------- TL · tulis ----------
var lama3 = TAMBAH.pesananPemasok[2]; var G = jnSusunJanjiPemasok('pp3', '2026-12-11', W, 'Ben Contoh'); var g = G.dokumen && G.dokumen[0].data;
ok('TL1 geser janji pesanan yang menunggu: janjiTanggal 11 Des + satu baris riwayat; kolom lain SAMA; kabar menyebut janji pertama', g && g.janjiTanggal === '2026-12-11' && g.janjiRiwayat.length === 2
  && g.karung === lama3.karung && g.status === 'menunggu' && g.rp === lama3.rp && /digeser 9 Des → 11 Des/.test(G.patch.kabar) && /janji pertama \(9 Des\)/.test(G.patch.kabar), J([G.tolak, G.patch]));
var kB = kirimUbah(BEN, 'pesananPemasok', lama3, g); var kK = kirimUbah(KRY, 'pesananPemasok', lama3, g); var kO = kirimUbah(OWN, 'pesananPemasok', lama3, g);
ok('TL2 penjaga kiriman (= rules v24): Penjaga laci LOLOS, karyawan DITOLAK, owner LOLOS', !kB.tolak && !!kK.tolak && !kO.tolak, J([kB, kK, kO]));
ok('TL3 Penjaga laci mengubah jumlah karung / status / janji cacat: DITOLAK', !!kirimUbah(BEN, 'pesananPemasok', lama3, Object.assign({}, g, { karung: 9 })).tolak && !!kirimUbah(BEN, 'pesananPemasok', lama3, Object.assign({}, g, { status: 'batal' })).tolak
  && !!kirimUbah(BEN, 'pesananPemasok', lama3, Object.assign({}, g, { janjiTanggal: '11 Des' })).tolak && !!kirimUbah(BEN, 'pesananPemasok', Object.assign({}, lama3, { status: 'batal' }), g).tolak);
ok('TL4 pesanan yang sudah datang / batal / tanggal sebelum pesan / sama / cacat: ditolak', /sudah datang/.test(jnSusunJanjiPemasok('pp1', '2026-12-11', W, 'x').tolak || '') && /dibatalkan/.test(jnSusunJanjiPemasok('pp6', '2026-12-11', W, 'x').tolak || '')
  && /sebelum tanggal pesan/.test(jnSusunJanjiPemasok('pp3', '2026-12-07', W, 'x').tolak || '') && /memang/.test(jnSusunJanjiPemasok('pp3', '2026-12-09', W, 'x').tolak || '') && /tidak terbaca/.test(jnSusunJanjiPemasok('pp3', 'besok', W, 'x').tolak || ''));
terapkanKeCache([{ koleksi: 'pesananPemasok', data: { id: 'pp8', tanggal: '2026-12-10', jam: '09:00', pemasok: 'Pemasok Contoh B', karung: 4, baris: [], status: 'menunggu' } }]);
var I1 = jnSusunJanjiPemasok('pp8', '2026-12-12', W, 'Owner');
ok('TL5 mengisi janji pesanan baru tanpa janji = "dicatat" (bukan geser); pesanan tanpa janji yang SUDAH datang tidak bisa diisi', /sudah datang/.test(jnSusunJanjiPemasok('pp4', '2026-12-12', W, 'x').tolak || '') && I1.dokumen && /dicatat/.test(I1.patch.kabar) && I1.dokumen[0].data.janjiRiwayat.length === 1, J(I1));
terapkanKeCache(jnSusunJanjiPemasok('pp5', '2026-12-12', W, 'Owner').dokumen); var I2 = jnSusunJanjiPemasok('pp5', '2026-12-13', W, 'Owner');
ok('TL6 janji pp5 sudah 11 Des sejak 9 Des → 12 Des hari ini = geser; dibetulkan lagi hari ini → 13 Des = salah ketik', I2.dokumen && /salah ketik/.test(I2.patch.kabar) && jnJanjiPemasok(I2.dokumen[0].data).awal === '2026-12-11' && jnJanjiPemasok(I2.dokumen[0].data).geser.length === 1, J([I2.patch, jnJanjiPemasok(I2.dokumen[0].data)]));
var bt = jnKolomJanjiBaru('2026-12-11', W, 'Owner'); ok('TL7 kolom janji pesanan baru: tanggal & satu riwayat; tanggal kemarin / kosong = tanpa janji', bt.janjiTanggal === '2026-12-11' && bt.janjiRiwayat.length === 1 && !jnKolomJanjiBaru('2026-12-09', W).janjiTanggal && !jnKolomJanjiBaru('', W).janjiTanggal, J(bt));
ok('TL8 pilihan cepat: belum tahu · hari ini · besok · lusa', J(jnPilihan('2026-12-10').map(function (x) { return x[0]; })) === '["","2026-12-10","2026-12-11","2026-12-12"]');
// surat jalan membawa janji
ok('TL9 janji surat jalan: isian Antar > tanggal kirim pesanan > hari itu; isian cacat ditolak penyusun nota', ajJanjiAntar({ janji: '2026-12-12' }, '2026-12-11', '2026-12-10').tanggal === '2026-12-12' && ajJanjiAntar({ janji: '' }, '2026-12-11', '2026-12-10').sumber === 'pesanan'
  && ajJanjiAntar({}, '', '2026-12-10').tanggal === '2026-12-10' && /dijanjikan sampai/.test(ajAlasanTolak({ antar: { ongkir: '0', pengantar: 'Kurir Contoh', janji: '2026-13-01' }, cara: 'Tunai' })));
var s = keadaanAwal(); s.sekarang = KINI; sinkronKeranjang(s);
function terap(p) { s = Object.assign({}, s, p); sinkronKeranjang(s); return p; }
function chip(jalur, kunci, berat) { return susunRak(s)[jalur].find(function (c) { return c.kunci === kunci && (!berat || c.berat === berat); }); }
function isi(jalur, kunci, n, berat) { terap(ketukChip(s, chip(jalur, kunci, berat))); terap({ ketik: String(n) }); terap(masukkan(s)); }
isi('kemasan', 'Kembang|5', 1); terap({ antar: Object.assign(ajDrafBaru(''), { janji: '2026-12-12' }) }); terap(uangPas(s));
var N1 = susunNotaDokumen(s, W); var S1 = (N1.dokumen || []).filter(function (x) { return x.koleksi === 'suratJalan'; })[0];
ok('TL10 nota diantar: surat jalan menulis janjiTanggal isian (12 Des)', S1 && S1.data.janjiTanggal === '2026-12-12', J(N1.tolak || (S1 && S1.data)));
s = keadaanAwal(); s.sekarang = KINI; sinkronKeranjang(s); isi('kemasan', 'Kembang|5', 1); terap({ antar: ajDrafBaru('') }); terap(uangPas(s));
var S2 = (susunNotaDokumen(s, W).dokumen || []).filter(function (x) { return x.koleksi === 'suratJalan'; })[0];
ok('TL11 tanpa isian: janji = hari itu', S2 && S2.data.janjiTanggal === '2026-12-10', J(S2 && S2.data));
// pesanan pelanggan: ubahan tanggal kirim tercatat (Penjaga laci boleh — riwayatStatus kolom ubah v11)
var ps2 = TAMBAH.pesanan[1]; var D2 = Object.assign(poDrafDariPesanan(ps2), { tanggalKirim: '2026-12-12' }); var U = poSusunPesanan(D2, W, {}); var u = U.pesanan;
var rr = u && u.riwayatStatus[u.riwayatStatus.length - 1];
ok('TL12 ubah tanggal kirim pesanan: baris riwayat ubah membawa kirimDari 7 Des → kirimKe 12 Des; janji pertama tetap 7 Des', rr && rr.ubah && rr.kirimDari === '2026-12-07' && rr.kirimKe === '2026-12-12' && jnJanjiPesanan(u).awal === '2026-12-07' && jnJanjiPesanan(u).geser.length === 1, J([U.tolak, rr]));
var kP = kirimUbah(BEN, 'pesanan', ps2, u); ok('TL13 Penjaga laci boleh mengubah tanggal kirim (tanpa rules baru)', !kP.tolak, J(kP));
var D3 = Object.assign(poDrafDariPesanan(ps2), { catatan: 'pagi' }); var U3b = poSusunPesanan(D3, W, {}); var r3 = U3b.pesanan.riwayatStatus[U3b.pesanan.riwayatStatus.length - 1];
ok('TL14 ubahan lain (tanggal kirim tetap) tidak menulis kirimDari', r3 && r3.ubah && r3.kirimDari === undefined, J(r3));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

SKENARIO_BELANJA = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
var J = function (x) { return JSON.stringify(x); };
var nId = 9000; var W = { tanggal: '2026-12-10', jam: '10:00', kini: '2026-12-10T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
pasok('batchMasuk', KOTAK.batchMasuk.concat(TAMBAH.batchMasuk)); pasok('pesananPemasok', []); setelSumber('cadangan', 'kotak pasir');
var pesan = {}; pesan['Beras Contoh'] = { p: 'Pemasok Contoh A', k: 4 };
var P1 = susunPesanan(pesan, 'Pemasok Contoh A', W, false, '2026-12-11', 'Owner'); var d1 = P1.dokumen && P1.dokumen[0].data;
ok('BL1 Belanja: pesanan dengan janji besok menulis janjiTanggal + riwayat, pesan WA "Mohon dikirim 11 Des 2026", kabar menyebut janji', d1 && d1.janjiTanggal === '2026-12-11' && d1.janjiRiwayat.length === 1 && d1.janjiRiwayat[0].oleh === 'Owner'
  && P1.baris[P1.baris.length - 1] === 'Mohon dikirim 11 Des 2026' && /janji datang 11 Des 2026/.test(P1.patch.kabar), J(P1.tolak || [d1, P1.baris]));
ok('BL2 bentuknya = jnKolomJanjiBaru (satu bentuk untuk owner & uji)', d1 && J({ janjiTanggal: d1.janjiTanggal, janjiRiwayat: d1.janjiRiwayat }) === J(jnKolomJanjiBaru('2026-12-11', W, 'Owner')));
var P2 = susunPesanan(pesan, 'Pemasok Contoh A', W, false, '', 'Owner'); var d2 = P2.dokumen && P2.dokumen[0].data;
ok('BL3 tanpa janji: tidak ada kolom janji, pesan WA tanpa baris janji, kabar "janji datang belum diisi"', d2 && d2.janjiTanggal === undefined && d2.janjiRiwayat === undefined && !/Mohon dikirim/.test(P2.baris.join('\n')) && /belum diisi/.test(P2.patch.kabar), J(P2.tolak || d2));
var P3 = susunPesanan(pesan, 'Pemasok Contoh A', W, false, '2026-12-09', 'Owner');
ok('BL4 janji sebelum hari ini tidak dipakai', P3.dokumen && P3.dokumen[0].data.janjiTanggal === undefined, J(P3.dokumen && P3.dokumen[0].data));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
var galat = []; var CAD = __CAD__; var hasil = {};
try { Object.keys(CAD).forEach(function (k) { if (Array.isArray(CAD[k])) pasok(k, CAD[k]); }); setelSumber('cadangan', 'asap'); } catch (e) { galat.push('muat: ' + e.message); }
var KINI = new Date(); try {
  var SP = jnPemasokSemua(KINI); var SL = jnPelangganSemua(KINI);
  hasil = { pesananPemasok: (CAD.pesananPemasok || []).length, berjanjiPemasok: (CAD.pesananPemasok || []).filter(function (p) { return p.janjiTanggal; }).length,
    pesanan: (CAD.pesanan || []).length, suratJalan: (CAD.suratJalan || []).length, berjanjiSJ: (CAD.suratJalan || []).filter(function (s) { return s.janjiTanggal; }).length,
    pemasokSemua: SP.map(function (x) { return [x.dibuat, x.keadaan, x.isi, x.pesan, x.datang]; }), pelangganSemua: SL.map(function (x) { return [x.jenis, x.dibuat, x.keadaan, x.isi]; }),
    ringkasPemasok: jnPemasok(KINI, 180).ringkas, ringkasAntar: jnPelanggan(KINI, 180).ringkas, lewat: jnLewat(KINI).length, kalimatPemasok: jnPemasok(KINI, 180).kalimat, kalimatAntar: jnPelanggan(KINI, 180).kalimat };
} catch (e) { galat.push('hitung: ' + e.message + ' ' + (e.stack || '').slice(0, 300)); }
print(JSON.stringify({ galat: galat, hasil: hasil }));
"""

RUSAK = [
    ('janji pertama = janji terakhir (geser menghapus telat)', JN, "    if (hari === sejak) { awal = v; if (!v) sejak = ''; continue; }\n    break;", "    awal = v || awal; continue;"),
    ('salah ketik di hari yang sama dihitung geser', JN, "    if (hari === sejak) { awal = v; if (!v) sejak = ''; continue; }", "    if (false) { continue; }"),
    ('antar tanpa pesanan dicap isi tidak terukur', JN, "o.isiTanpaUkur ? 'tidakTerukur' : '';", "o.sampai || o.isiTanpaUkur ? 'tidakTerukur' : '';"),
    ('tanpa janji dianggap tepat', JN, "  else if (!J.awal) keadaan = 'tanpaJanji';", "  else if (!J.awal) keadaan = o.sampai ? 'tepat' : 'menunggu';"),
    ('toleransi diabaikan', JN, "keadaan = telat <= tol ? 'tepat' : 'telat'; }", "keadaan = telat <= 0 ? 'tepat' : 'telat'; }"),
    ('gagal antar dianggap tepat', JN, "  else if (o.gagal) { keadaan = 'gagal';", "  else if (false) { keadaan = 'gagal';"),
    ('utuh dari kg, bukan karung (kurang timbang jadi sebagian)', JN, "const jnKarungBatch = (b) => (Array.isArray(b.merkList) ? b.merkList : []).reduce((a, r) => a + (Number(r && r.jumlahKarung) || 0), 0);", "const jnKarungBatch = (b) => (Array.isArray(b.merkList) ? b.merkList : []).reduce((a, r) => a + (Number(r && r.totalKg) || 0) / 51, 0);"),
    ('trip kedua di hari yang sama tidak dijumlah', JN, "datang = kd.reduce((a, b) => a + jnKarungBatch(b), 0); nDatang = kd.length;", "datang = jnKarungBatch(kd[0]); nDatang = 1;"),
    ('kedatangan dipakai dua pesanan', JN, "&& !pakai[String(b.id)]\n", "\n"),
    ('surat jalan batal ikut dihitung', JN, "    if (s.status === 'batal' || berlaku(s.trxIdJual) === false) return;", "    if (false) return;"),
    ('pesanan dihitung dua kali (lewat surat jalannya juga)', JN, "    if (p.status === 'batal' || (p.trxIdJual && sjPerTrx[String(p.trxIdJual)])) return;", "    if (p.status === 'batal') return;"),
    ('geser di surat jalan tidak tercatat (janji pesanan tanpa jejak geser)', JN, "    if (Jp && Jp.awal && jnTanggalSah(s.janjiTanggal) && s.janjiTanggal !== (Jp.akhir || Jp.awal)) J =", "    if (false) J ="),
    ('rata-rata telat hanya dari yang telat', JN, "R.rataTelat = R.nDatang ? R.jumlahTelat / R.nDatang : null;", "R.rataTelat = R.telat ? R.jumlahTelat / R.telat : null;"),
    ('daftar lewat: telat tersingkat dulu', JN, "  return P.concat(A).sort((a, b) => b.telat - a.telat ||", "  return P.concat(A).sort((a, b) => a.telat - b.telat ||"),
    ('Penjaga laci boleh mengubah pesanan yang sudah datang', JN, "  if (p.status !== 'menunggu' || (X && X.sampai)) return { tolak: 'Barang pesanan ini sudah datang — janjinya tidak diubah lagi' };", ""),
    ('janji sebelum tanggal pesan lolos', JN, "  if (jnSelisih(t, p.tanggal) < 0) return { tolak:", "  if (false) return { tolak:"),
    ('penjaga kiriman tidak menjaga bentuk janji (tanggal cacat lolos)', AK, "String(lama.status || '') !== 'menunggu' || !janjiPemasokSah(d)))", "String(lama.status || '') !== 'menunggu' || false))"),
    ('penjaga kiriman membolehkan kolom karung', AK, "export const KOLOM_JANJI_PEMASOK = ['janjiTanggal', 'janjiRiwayat'];", "export const KOLOM_JANJI_PEMASOK = ['janjiTanggal', 'janjiRiwayat', 'karung', 'status'];"),
    ('surat jalan tanpa janji', AJ, "  if (ajTanggalSah(c.janji)) d.janjiTanggal = String(c.janji);\n", ""),
    ('isian janji Antar diabaikan', AJ, "  const t = String((antar && antar.janji) || '').trim(); if (ajTanggalSah(t)) return { tanggal: t, sumber: 'isian' };", "  const t = '';"),
    ('ubah tanggal kirim tanpa jejak', PO, "    const geserKirim = String(lama.tanggalKirim || '') !== tk ? { kirimDari: String(lama.tanggalKirim || ''), kirimKe: tk } : {};", "    const geserKirim = {};"),
    ('Belanja tidak menulis janji', BL, "  if (adaJanji) { data.janjiTanggal = jt; data.janjiRiwayat = [{ tanggal: jt, pada: w.kini, oleh: String(oleh || '').slice(0, 40) }]; }\n", ""),
    ('Tugas gudang tanpa baris lewat janji', GD, "  baris('janji', 'Lewat janji datang / antar', () => {", "  baris('janjiX', 'Lewat janji datang / antar', () => {"),
]

STATIS = [
    ('Harga › Belanja: pilihan janji saat kirim & isi / geser janji', 'harga', ["pilihJanji(s.waJanji, 'blWaJanji', 'blWaJanjiKetik', 'wj', 'Dijanjikan datang')", 'data-aksi="blJanjiBuka"', 'data-aksi="blJanjiSimpan"', 'JN.jnSusunJanjiPemasok(', 'st().waJanji, namaPencatat()', 'JN.jnKataBaris(X)']),
    ('Barang masuk tablet: pesanan menunggu + isi / geser janji (Penjaga laci)', 'stok', ['${kartuJanjiTablet(s, ak)}', 'data-aksi="mtJanjiBuka"', 'data-aksi="mtJanjiSimpan"', "tombolAkun(ak, 'kedatangan')", 'JN.jnMenungguPemasok(']),
    ('Laporan › Pondasi: kartu Tepat janji (dua arah, lewat janji, per pemasok, toleransi)', 'laporan', ['data-k="pd-janji"', 'JN.jnPemasok(kini(), nJn)', 'JN.jnPelanggan(kini(), nJn)', 'JN.jnLewat(kini())', 'data-aksi="jnAturSimpan"', '${rantai}${janji}${upahAntar}']),
    ('Dasbor: baris Tepat janji di KPI', 'dasbor', ["baris('janji', 'Tepat janji · pemasok / antar'", 'JN.kalimatPemasok', 'JN.lewat']),
    ('dasbor-logika: dbKpi membawa jnRingkas', 'dasborL', ["janji: aman(() => jnRingkas(kini))", "import { jnRingkas } from './janji-logika.js';"]),
    ('Bayar › Antar: isian dijanjikan sampai', 'antarP', ['${gambarJanji(s, a)}', 'data-aksi="ajJanji"', 'data-kolom="janji"', 'AJ.ajJanjiAntar(']),
    ('Pesanan: tanggal kirim = janji + lewat janji disebut', 'pesananP', ['Tanggal kirim · dijanjikan ke pemesan', 'LEWAT JANJI ']),
    ('jual-logika meneruskan janji ke surat jalan', 'jual', ["janji: ajJanjiAntar(s.antar, psJanji && psJanji.tanggalKirim, w.tanggal).tanggal"]),
    ('akses.js: cermin rules v24', 'akses', ["export const BACA_BEN_JANJI = ['pesananPemasok'];", "export const KOLOM_JANJI_PEMASOK = ['janjiTanggal', 'janjiRiwayat'];", "if (x.koleksi === 'pesananPemasok' && (P !== 'ben' ||"]),
    ('rules v24: blok pesananPemasok dipecah + stafJanjiPemasok', 'rules', ['ATURAN FIRESTORE v24 FINAL', "      allow update: if owner() || stafJanjiPemasok(['ben']);", 'function stafJanjiPemasok(peranBoleh)']),
    ('docs/uji-rules-v24.md ada', 'dok24', ['## Wajib owner (3 kasus', '★I19']),
    ('bundel_baru: janji-logika ikut otomatis', 'bundel', ["JN_MODUL = 'baru/js/layar/janji-logika.js'"]),
    ('peta_akses menghitung kiriman janji dari tablet', 'peta', ['jnSusunJanjiPemasok(']),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_tanggal_janji.py && python3 alat-uji/uji_tanggal_janji.py --kontrol']),
    ('BACA-DULU menyebut paket ini', 'baca', ['## Tanggal janji', 'janji-logika.js', 'rules v24']),
]
RUSAK_STATIS = [
    ('Belanja tanpa pilihan janji', 'harga', "pilihJanji(s.waJanji, 'blWaJanji', 'blWaJanjiKetik', 'wj', 'Dijanjikan datang')", "''"),
    ('tablet tanpa kartu janji', 'stok', '${kartuJanjiTablet(s, ak)}', ''),
    ('Pondasi tanpa kartu tepat janji', 'laporan', '${rantai}${janji}${upahAntar}', '${rantai}${upahAntar}'),
    ('Antar tanpa isian janji', 'antarP', '${gambarJanji(s, a)}', ''),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_tanggal_janji.py', 'true'),
]


def bundel(teks, modul):
    return bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in modul)


def jalan(teks, isi=None, modul=None):
    js = JAM + bundel(teks, modul or MODUL) + '\nvar KOTAK = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar TAMBAH = ' + json.dumps(TAMBAH) + ';\n(function () {\n' + (isi or SKENARIO) + '\n})();\n'   # lingkup sendiri: nama skenario tidak menabrak konstanta modul
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return None, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    return json.loads(out), None


def jalan_semua(teks):
    l, g = 0, []
    for sk in (SKENARIO, SKENARIO_BELANJA):
        h, e = jalan(teks, sk)
        if h is None: g += e
        else: l += h['lulus']; g += h['gagal']
    return l, g


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    return len(STATIS) - len(g), g


def muat():
    sumber = set(MODUL + [GD])
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in sumber), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama + ' (' + str(teks[berkas].count(a)) + '×)'); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b); l, g = jalan_semua(T)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_STATIS:
            if src[berkas].count(a) < 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            S = dict(src); S[berkas] = S[berkas].replace(a, b); l, g = statis(S)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = jalan_semua(teks); ls, gs = statis(src)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '..', '..', '..', '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and '--tanpa-asap' not in sys.argv:
        ha, ea = jalan(teks, ASAP.replace('__CAD__', open(cad[-1], encoding='utf-8').read()))
        if ha is None: print('ASAP DATA TOKO: JSC JATUH ' + ea[0][:600]); g = list(g) + ['asap']
        else:
            print('ASAP DATA TOKO (%s): %s — %s · galat %s' % (os.path.basename(cad[-1]), 'LULUS' if not ha['galat'] else 'GAGAL', json.dumps(ha['hasil'], ensure_ascii=False), json.dumps(ha['galat'], ensure_ascii=False)))
            if ha['galat']: g = list(g) + ['asap']
    sys.exit(1 if g or gs else 0)
