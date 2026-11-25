#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_kas_rekening.py — KAS & REKENING (owner 26 Nov 2026, sensus ulang 26 Nov bagian 1c: A35 · A37 · A55 · A84 · A134 · B86 · B128). KOTAK PASIR (nama & angka
CONTOH, bukan angka toko), jsc saja, TANPA peramban. Jam dikunci Kamis 26 Nov 2026 15:00 WIB.
  KK kas kecil: batas per catatan & sehari (tegas >), nota wajib mulai notaMin, tanpa nota = alasan, foto wajib = setelan; hanya untuk toko/karyawan dari LACI;
     setelan menumpang aturanToko/uangKeluar (kolom lain DIBAWA, dua arah); tandai nota catatan yang sudah tersimpan; titipan tablet ditandai.
  ST setor ke bank: bawaan batas 20 jt · sisakan 10 jt; tombol rutin brankas → rekening; pengingat hanya bila brankas > batas; setelan tidak menghapus kolom lain.
  BK buku kas harian semua tempat: awal = akhir kemarin, akhir = patokan terbaru + gerakan + catatan sesudah tutup; tiap tempat MENUTUP (awal + gerak + beda = akhir),
     beda laci = selisih tutup hari; hari ini empat tempat = kas mesin.
  CR cocok rekening: baris rekening dari sumber yang sama dengan saldoKantong (Σ = gerakan rekening — penjaga identitas); QRIS satu nota satu baris; centang per
     bulan (kolom lain dibawa); berkas CSV & teks bebas; cocok persis & QRIS gabung (dipotong MDR); hasil cocok tersimpan, titik kas TIDAK ditulis; bawaan cocok
     sebelumnya; bentuk berkas diingat; riwayat setelan melewati dokumen cocokRek-; pengingat setor & cocok bulanan.
  ASAP: cadangan toko lokal (bila ada) — buku kas 14 hari terakhir menutup tiap tempat, identitas baris rekening, kas kecil & cocok rekening tidak galat.

    python3 alat-uji/uji_kas_rekening.py            → N lulus · 0 gagal
    python3 alat-uji/uji_kas_rekening.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_uang_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
UG = 'baru/js/layar/uang-logika.js'; KR = 'baru/js/layar/kas-rekening-logika.js'; RS = 'baru/js/data/riwayat-setelan.js'
MODUL = list(dict.fromkeys(uji_uang_baru.MODUL + [KR, RS]))
SUMBER = {'uang': 'baru/js/layar/uang.js', 'laporan': 'baru/js/layar/laporan.js', 'dasbor': 'baru/js/layar/dasbor.js', 'dasborL': 'baru/js/layar/dasbor-logika.js', 'app': 'baru/js/app.js',
          'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'sistem': 'baru/js/layar/sistem-logika.js', 'tutup': 'baru/js/layar/tutup-hari-logika.js',
          'jual': 'baru/js/layar/jual.js', 'rules': 'firestore.rules', 'kr': KR}
JAM = "var __KINI = new Date('2026-11-26T15:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"

KOTAK = {
  'penjualan': [
    {'id': 1001, 'tanggal': '2026-11-25', 'jam': '09:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 25, 'hargaTotal': 400000, 'hppTotalSaatJual': 350000, 'trxId': 't1'},
    {'id': 1002, 'tanggal': '2026-11-25', 'jam': '10:00', 'caraBayar': 'QRIS', 'jenis': 'kemasan', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 2, 'totalKg': 10, 'hargaTotal': 200000, 'hppTotalSaatJual': 180000, 'trxId': 'q1'},
    {'id': 1003, 'tanggal': '2026-11-25', 'jam': '10:00', 'caraBayar': 'QRIS', 'jenis': 'kemasan', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 1, 'totalKg': 5, 'hargaTotal': 100000, 'hppTotalSaatJual': 90000, 'trxId': 'q1'},
    {'id': 1004, 'tanggal': '2026-11-25', 'jam': '11:00', 'caraBayar': 'QRIS', 'jenis': 'literan', 'merkSumber': 'Angsa', 'jumlahLiter': 3, 'totalKg': 2.4, 'hargaTotal': 50000, 'hppTotalSaatJual': 40000, 'trxId': 'q2'},
    {'id': 1005, 'tanggal': '2026-11-25', 'jam': '21:30', 'caraBayar': 'Tunai', 'jenis': 'literan', 'merkSumber': 'Angsa', 'jumlahLiter': 2, 'totalKg': 1.6, 'hargaTotal': 30000, 'hppTotalSaatJual': 25000, 'trxId': 't2'},
    {'id': 1006, 'tanggal': '2026-11-26', 'jam': '10:00', 'caraBayar': 'Transfer', 'namaPelanggan': 'Warung Contoh', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 50, 'hargaTotal': 750000, 'hppTotalSaatJual': 700000, 'trxId': 'tf1'},
    {'id': 1007, 'tanggal': '2026-11-26', 'jam': '11:30', 'caraBayar': 'Tunai', 'jenis': 'literan', 'merkSumber': 'Angsa', 'jumlahLiter': 12, 'totalKg': 9.6, 'hargaTotal': 200000, 'hppTotalSaatJual': 170000, 'trxId': 't3'},
  ],
  'piutangMutasi': [{'id': 2001, 'tanggal': '2026-11-26', 'jam': '11:00', 'tipe': 'bayar', 'namaPelanggan': 'Bu Contoh', 'nominal': 120000, 'caraBayar': 'QRIS'},
                    {'id': 2000, 'tanggal': '2026-11-10', 'jam': '09:00', 'tipe': 'saldoAwal', 'namaPelanggan': 'Bu Contoh', 'nominal': 120000}],
  'pengeluaranHarian': [
    {'id': 'mdr-2026-11-25', 'tanggal': '2026-11-25', 'jam': '21:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'Potongan QRIS (MDR) · 2 nota · perkiraan', 'nominal': 4000, 'dari': 'rekening', 'mdr': True},
    {'id': 3001, 'tanggal': '2026-11-25', 'jam': '12:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'Tali & plastik', 'nominal': 95000, 'dari': 'laci', 'nota': 'ada'},
    {'id': 3002, 'tanggal': '2026-11-26', 'jam': '09:30', 'kategori': 'toko', 'untuk': 'karyawan', 'keterangan': 'Kopi', 'nominal': 20000, 'dari': 'laci'},
    {'id': 3003, 'tanggal': '2026-11-26', 'jam': '09:40', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'Bensin antar — dari tablet', 'nominal': 80000, 'dari': 'laci', 'oleh': 'Ben'},
    {'id': 3004, 'tanggal': '2026-11-26', 'jam': '09:50', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'Galon', 'nominal': 60000, 'dari': 'brankas'},
  ],
  'pindahUang': [{'id': 'pd-2026-11-25', 'tanggal': '2026-11-25', 'jam': '21:00', 'dari': 'laci', 'ke': 'brankas', 'nominal': 500000, 'alasan': 'Amankan laci (tutup hari)', 'biayaAdmin': 0}],
  'amplopLaba': [{'id': 'am-2026-11-25', 'tanggal': '2026-11-25', 'jam': '21:00', 'tipe': 'setor', 'nominal': 10000, 'catatan': 'Sisihan tutup hari'}],
  'tutupHari': [
    {'id': '2026-11-24', 'tanggal': '2026-11-24', 'jam': '21:00', 'selisihLaci': 0, 'diubahPada': '2026-11-24T14:00:00.000Z', 'sistemBaru': True, 'titik': {'laci': 1000000, 'brankas': 25000000, 'rekening': 2000000, 'amplop': 300000}},
    {'id': '2026-11-25', 'tanggal': '2026-11-25', 'jam': '21:00', 'selisihLaci': -5000, 'diubahPada': '2026-11-25T14:00:00.000Z', 'sistemBaru': True, 'titik': {'laci': 790000, 'brankas': 25500000, 'rekening': 2346000, 'amplop': 310000}}],
  'pengaturan': [{'id': 'titikKas', 'tanggal': '2026-11-25', 'laci': 790000, 'brankas': 25500000, 'rekening': 2346000, 'amplop': 310000, 'diubahPada': '2026-11-25T14:00:00.000Z'}],
  'aturanToko': [{'id': 'uangKeluar', 'perluToko': [{'nama': 'Bensin antar', 'biasa': 0}, {'nama': 'Tali & plastik', 'biasa': 0}], 'perluKaryawan': [{'nama': 'Kopi', 'biasa': 20000}], 'perluPribadi': [], 'bulanan': [], 'aman': 0, 'alasan': ['Mendesak keluarga']}],
}
SETOR = {'id': 'st1', 'tanggal': '2026-11-26', 'jam': '12:00', 'dari': 'brankas', 'ke': 'rekening', 'nominal': 15000000, 'alasan': 'Setor ke bank', 'biayaAdmin': 0}
CSV = ('Tanggal,Keterangan,Debet,Kredit,Saldo\n'
       '25/11/2026,"PENCAIRAN GOPAY, MERCHANT",,"346.000,00","2.346.000,00"\n'
       '26/11/2026,TRSF E-BANKING CR DARI CONTOH,,"750.000,00","3.096.000,00"\n'
       '26/11/2026,QRIS BON,,"120.000,00","3.216.000,00"\n'
       '26/11/2026,SETORAN TUNAI,,"15.000.000,00","18.216.000,00"\n'
       '26/11/2026,BIAYA ADM,"2.500,00",,"18.213.500,00"\n'
       '26/11/2026,TARIK PRIBADI,"500.000,00",,"17.713.500,00"\n')
TEKS = ('26/11 TRSF E-BANKING CR 750.000,00 3.096.000,00\n'
        '26/11 BIAYA ADM 2.500,00 DB 18.213.500,00\n'
        'catatan tanpa angka\n'
        '26/11 BARIS TANPA ARAH 1.000,00\n')

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); };
var KINI = new Date('2026-11-26T15:00:00+07:00'); var nId = 900000;
var W = { tanggal: '2026-11-26', jam: '15:00', kini: '2026-11-26T08:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
var K0 = JSON.parse(J(KOTAK)); Object.keys(K0).forEach(function (n) { pasok(n, K0[n]); }); setelSumber('cadangan', 'kotak pasir');
var atur = function (extra) { pasok('aturanToko', JSON.parse(J(KOTAK.aturanToko)).concat(extra || [])); };
var pindah = function (extra) { pasok('pindahUang', JSON.parse(J(KOTAK.pindahUang)).concat(extra || [])); };
var keluar = function (extra) { pasok('pengeluaranHarian', JSON.parse(J(KOTAK.pengeluaranHarian)).concat(extra || [])); };
var dokAtur = function (r, id) { return (r.dokumen || []).filter(function (x) { return x.koleksi === 'aturanToko' && x.data.id === id; }).map(function (x) { return x.data; })[0] || null; };

// ==================== KK · KAS KECIL ====================
var A0 = aturKasKecil();
ok('KK: bawaan 150.000 per catatan · 300.000 sehari · nota mulai 50.000 · foto tidak wajib', A0.batasCatatan === 150000 && A0.batasHari === 300000 && A0.notaMin === 50000 && A0.fotoWajib === false && !A0.dariOwner, J(A0));
ok('KK: kena = toko/karyawan dari laci; brankas, MDR, tagihan bulanan, dompet, pribadi TIDAK', ksKena({ kategori: 'toko', dari: 'laci' }) && ksKena({ kategori: 'toko' }) && !ksKena({ kategori: 'toko', dari: 'brankas' }) && !ksKena({ kategori: 'toko', dari: 'rekening', mdr: true })
  && !ksKena({ kategori: 'toko', dari: 'laci', keterangan: 'Air (bulanan)' }) && !ksKena({ kategori: 'tokoDompet' }) && !ksKena({ kategori: 'owner', dari: 'laci' }) && !ksKena({ kategori: 'toko', dari: 'laci', dariPindah: 'x' }));
ok('KK: terpakai hari ini = kopi 20.000 + bensin tablet 80.000 (galon dari brankas tidak)', ksTerpakai('2026-11-26') === 100000, ksTerpakai('2026-11-26'));
var P1 = ksPeriksa(150000, '2026-11-26'), P2 = ksPeriksa(150001, '2026-11-26'), P3 = ksPeriksa(140000, '2026-11-26'), P4 = ksPeriksa(200001, '2026-11-26');
ok('KK: batas per catatan TEGAS > (150.000 boleh, 150.001 lewat)', !P1.lewatCatatan && P2.lewatCatatan && /per catatan/.test(P2.teks), J([P1, P2]));
ok('KK: batas sehari: 100.000 + 140.000 = 240.000 aman; + 200.001 = 300.001 lewat', !P3.lewatHari && P3.sesudah === 240000 && P4.lewatHari && P4.sesudah === 300001 && /lewat batas sehari/.test(P4.teks), J([P3, P4]));
ok('KK: nota wajib mulai 50.000 (≥)', ksPeriksa(50000, '2026-11-26').perluNota && !ksPeriksa(49999, '2026-11-26').perluNota);
var D = { untuk: 'toko', dari: 'laci', perlu: 'Bensin antar', ketik: '60000', catatan: '' };
ok('KK: 60.000 dari laci tanpa tanda nota DITOLAK', /ada nota/.test(String(susunKeluar(D, W, null).tolak)), J(susunKeluar(D, W, null)));
ok('KK: "tanpa nota" tanpa alasan DITOLAK', /tulis alasannya/.test(String(susunKeluar(Object.assign({}, D, { nota: 'tanpa' }), W, null).tolak)));
var R1 = susunKeluar(Object.assign({}, D, { nota: 'tanpa', alasanNota: 'warung tidak kasih nota' }), W, null); var d1 = R1.dokumen && R1.dokumen[0].data;
ok('KK: tanpa nota + alasan → pengeluaranHarian bertanda nota tanpa + alasanNota; kabar menyebut kas kecil', d1 && d1.nota === 'tanpa' && d1.alasanNota === 'warung tidak kasih nota' && d1.dari === 'laci' && !d1.fotoNota && /kas kecil hari ini Rp160\.000 dari Rp300\.000/.test(R1.patch.kabar), J(R1));
var R2 = susunKeluar(Object.assign({}, D, { nota: 'ada' }), W, null);
ok('KK: nota ADA, foto tidak wajib → boleh tanpa foto', R2.dokumen && R2.dokumen[0].data.nota === 'ada' && !R2.dokumen[0].data.fotoNota, J(R2));
ok('KK: di bawah notaMin tidak ditanya nota; kolom nota tidak ditulis', (function () { var r = susunKeluar(Object.assign({}, D, { ketik: '30000' }), W, null); return r.dokumen && r.dokumen[0].data.nota === undefined; })());
var DL = Object.assign({}, D, { ketik: '200001', nota: 'ada' });
ok('KK: lewat batas tanpa alasan DITOLAK (kalimat menyebut batasnya)', /Lewat batas kas kecil per catatan Rp150\.000/.test(String(susunKeluar(DL, W, null).tolak)), J(susunKeluar(DL, W, null)));
var R3 = susunKeluar(Object.assign({}, DL, { alasanKas: 'ganti ban motor antar' }), W, null);
ok('KK: lewat batas + alasan → tersimpan dengan alasanKasKecil', R3.dokumen && R3.dokumen[0].data.alasanKasKecil === 'ganti ban motor antar', J(R3));
ok('KK: dari BRANKAS / untuk PRIBADI / dari DOMPET bukan kas kecil (tanpa syarat nota)', (function () { var a = susunKeluar(Object.assign({}, D, { dari: 'brankas' }), W, null), b = hitungKeluar({ untuk: 'pribadi', dari: 'laci', perlu: 'Belanja dapur', ketik: '60000' }, KINI), c = susunKeluar(Object.assign({}, D, { dari: 'dompet' }), W, null);
  return a.dokumen && c.dokumen && b.ks === null && a.dokumen[0].data.nota === undefined && c.dokumen[0].data.nota === undefined; })());
// setelan kas kecil — menumpang aturanToko/uangKeluar, kolom lain DIBAWA
var SK = susunAturKasKecil({ batasCatatan: '100.000', batasHari: '250000', notaMin: '25000', fotoWajib: true }, W); var dk = dokAtur(SK, 'uangKeluar');
ok('KK: simpan setelan kas kecil membawa keperluan & batas aman lama', dk && dk.kasKecil.batasCatatan === 100000 && dk.kasKecil.batasHari === 250000 && dk.kasKecil.notaMin === 25000 && dk.kasKecil.fotoWajib === true && dk.perluToko.length === 2 && dk.perluKaryawan[0].nama === 'Kopi', J(dk));
ok('KK: per catatan > sehari DITOLAK; angka minus / ngawur DITOLAK; kosong = 0 = mati', /lebih besar dari batas sehari/.test(String(susunAturKasKecil({ batasCatatan: '400000', batasHari: '300000' }, W).tolak)) && !!susunAturKasKecil({ batasCatatan: '-5' }, W).tolak
  && dokAtur(susunAturKasKecil({ batasCatatan: '', batasHari: '', notaMin: '' }, W), 'uangKeluar').kasKecil.batasHari === 0);
terapkanKeCache(SK.dokumen);
var A1 = aturKasKecil(); ok('KK: setelan owner terbaca (dariOwner)', A1.batasCatatan === 100000 && A1.fotoWajib && A1.dariOwner, J(A1));
var SA = susunAturKeluar({ perluToko: [{ nama: 'Bensin antar', biasa: '' }], perluKaryawan: [{ nama: 'Kopi', biasa: '20000' }], perluPribadi: [], bulanan: [], aman: '', alasan: ['Mendesak keluarga'] }, W);
ok('KK: simpan aturan uang keluar TIDAK menghapus setelan kas kecil', dokAtur(SA, 'uangKeluar').kasKecil && dokAtur(SA, 'uangKeluar').kasKecil.batasCatatan === 100000, J(dokAtur(SA, 'uangKeluar')));
var DF = Object.assign({}, D, { ketik: '60000', nota: 'ada' });
ok('KK: foto WAJIB → nota ada tanpa foto DITOLAK', /Foto notanya dulu/.test(String(susunKeluar(DF, W, null).tolak)), J(susunKeluar(DF, W, null)));
var R4 = susunKeluar(Object.assign({}, DF, { fotoSiap: true, idDok: 777001, fotoId: 'f-1' }), W, null);
ok('KK: foto siap → id catatan = id yang dipesan untuk foto, fotoNota [id foto]', R4.dokumen && R4.dokumen[0].data.id === 777001 && J(R4.dokumen[0].data.fotoNota) === '["f-1"]' && /\+ foto/.test(R4.patch.kabar), J(R4));
ok('KK: "tanpa nota" tetap boleh walau foto wajib (alasan wajib)', !!susunKeluar(Object.assign({}, DF, { nota: 'tanpa', alasanNota: 'pasar' }), W, null).dokumen);
// catatan yang sudah tersimpan (titipan tablet 80.000 tanpa tanda) — ditandai sesudahnya
var KH = ksHari('2026-11-26');
ok('KK: ringkasan hari: terpakai 100.000 · sisa 150.000 dari batas 250.000 · 1 catatan notanya belum beres (bensin tablet)', KH.terpakai === 100000 && KH.sisa === 150000 && KH.nNotaKurang === 1 && /1 catatan notanya belum beres/.test(KH.teks), J(KH));
ok('KK: buku hari ini menyebut nota yang kurang per baris', (function () { var r = bukuKeluar('2026-11-26').rows.find(function (x) { return x.id === '3003'; }); return r && r.ks && r.notaKurang === 'nota belum ditandai'; })());
ok('KK: tandai ADA tanpa foto padahal foto wajib DITOLAK', /Foto nota diwajibkan/.test(String(susunTandaNota('3003', 'ada', '', null, W).tolak)));
var TN = susunTandaNota('3003', 'ada', '', 'f-9', W); var dn = TN.dokumen && TN.dokumen[0].data;
ok('KK: tandai ADA + foto → salinan catatan utuh + nota + fotoNota, catatan lain tidak disentuh', dn && dn.koleksi === undefined && TN.dokumen[0].koleksi === 'pengeluaranHarian' && dn.id === 3003 && dn.nominal === 80000 && dn.oleh === 'Ben' && dn.nota === 'ada' && J(dn.fotoNota) === '["f-9"]', J(TN));
ok('KK: tandai TANPA butuh alasan; catatan tak dikenal ditolak', /alasannya/.test(String(susunTandaNota('3003', 'tanpa', '', null, W).tolak)) && /tidak ditemukan/.test(String(susunTandaNota('xx', 'ada', '', 'f', W).tolak)));
terapkanKeCache(TN.dokumen); ok('KK: sesudah ditandai, tidak ada nota yang kurang', ksHari('2026-11-26').nNotaKurang === 0, J(ksHari('2026-11-26')));
pasok('persetujuan', [{ id: 'tt9', tindakan: 'uangKeluar', status: 'menunggu', jenis: 'toko', nominal: 200000, tanggal: '2026-11-26', jam: '14:00', dari: 'Ben', mintaUid: 'u', teks: 'ban' }]);
ok('KK: titipan tablet untuk toko yang membuat sehari lewat batas DITANDAI (sebelum disetujui)', (function () { var t = titipanKeluar().find(function (x) { return x.id === 'tt9'; }); return t && t.ks && t.ks.lewatHari && t.ks.perluNota; })(), J(titipanKeluar()));
pasok('persetujuan', []); keluar(); atur();

// ==================== ST · SETOR KE BANK ====================
var AP = aturPindah(); var SG = ugSetor();
ok('ST: bawaan batas 20.000.000 · sisakan 10.000.000', AP.setorBatas === 20000000 && AP.setorSisa === 10000000, J(AP));
ok('ST: brankas 25.440.000 (25.500.000 − galon 60.000 dari brankas) > batas → lewat, setor 15.440.000; belum pernah setor', SG.ada && SG.lewat && SG.n === 15440000 && SG.brankas === 25440000 && SG.terakhir === null && /lewat batas Rp20\.000\.000/.test(SG.teks), J(SG));
var RT = rutinPindah().daftar.find(function (r) { return r.id === 'setor'; });
ok('ST: tombol rutin Setor ke bank = brankas → rekening, sisakan 10 jt, alasan "Setor ke bank"', RT && RT.dari === 'brankas' && RT.ke === 'rekening' && RT.n === 15440000 && RT.bisa && RT.alasan === 'Setor ke bank', J(RT));
var PS = susunPindah({ dari: RT.dari, ke: RT.ke, ketik: String(RT.n), alasan: RT.alasan, adminI: -1 }, W);
ok('ST: rutin ditulis sebagai pindahUang biasa (jumlah uang toko tetap)', PS.dokumen && PS.dokumen.length === 1 && PS.dokumen[0].data.ke === 'rekening' && PS.dokumen[0].data.nominal === 15440000, J(PS));
var KP0 = khSumberPengingat(KINI); ok('ST: pengingat setor muncul hari ini (brankas lewat batas)', KP0.some(function (p) { return p.jenis === 'setor' && p.jatuh === '2026-11-26' && p.n === 15440000; }), J(KP0));
pindah([SETOR]); var SG2 = ugSetor();
ok('ST: sesudah setor 15 jt brankas 10.440.000 → tidak lewat; setoran terakhir disebut', SG2.ada && !SG2.lewat && SG2.brankas === 10440000 && SG2.terakhir && SG2.terakhir.n === 15000000 && !khSumberPengingat(KINI).some(function (p) { return p.jenis === 'setor'; }), J(SG2));
var SPx = susunAturPindah({ jaga: '400000', alasan: ['Setor ke bank'], setorBatas: '30.000.000', setorSisa: '5000000' }, W); var dp = dokAtur(SPx, 'pindahUang');
ok('ST: simpan aturan pindah menyimpan batas & sisakan; kolom lama dokumen dibawa', dp && dp.setorBatas === 30000000 && dp.setorSisa === 5000000 && dp.jaga === 400000, J(dp));
ok('ST: sisakan ≥ batas DITOLAK; 0 = pengingat mati', /harus di bawah batas/.test(String(susunAturPindah({ jaga: '0', alasan: ['x'], setorBatas: '1000', setorSisa: '1000' }, W).tolak)) && (function () { atur([{ id: 'pindahUang', jaga: 500000, alasan: ['x'], setorBatas: 0, setorSisa: 0 }]); pindah(); var x = ugSetor(); atur(); return !x.nyala && !x.lewat; })());
atur([{ id: 'pindahUang', jaga: 500000, alasan: ['x'], lainLama: 'tetap' }]); ok('ST: kolom asing di dokumen pindahUang lama DIBAWA saat simpan', dokAtur(susunAturPindah({ jaga: '500000', alasan: ['x'] }, W), 'pindahUang').lainLama === 'tetap'); atur(); pindah([SETOR]);

// ==================== BK · BUKU KAS HARIAN SEMUA TEMPAT ====================
var P25 = khPosisi('2026-11-25');
ok('BK: akhir 25 Nov = hitungan tutup hari 25 + nota tunai 21.30 yang dicatat SESUDAH tutup (laci 820.000)', P25.ada && P25.laci === 820000 && P25.brankas === 25500000 && P25.rekening === 2346000 && P25.amplop === 310000 && P25.susulan.laci === 30000, J(P25));
var B25 = khBukuHari('2026-11-25', KINI); var t25 = function (k) { return B25.tempat.find(function (x) { return x.id === k; }); };
ok('BK: 25 Nov laci: awal 1.000.000 + masuk 430.000 − keluar 95.000 − pindah 510.000 → beda −5.000 = selisih tutup hari → akhir 820.000',
  t25('laci').awal === 1000000 && t25('laci').masuk === 430000 && t25('laci').keluar === 95000 && t25('laci').pindahKeluar === 510000 && t25('laci').beda === -5000 && /selisih hitungan laci/.test(t25('laci').sebab) && t25('laci').akhir === 820000, J(t25('laci')));
ok('BK: 25 Nov rekening: 2.000.000 + QRIS 350.000 − potongan 4.000 = 2.346.000, beda 0; brankas +500.000; amplop +10.000', t25('rekening').masuk === 350000 && t25('rekening').keluar === 4000 && t25('rekening').beda === 0 && t25('brankas').pindahMasuk === 500000 && t25('brankas').beda === 0 && t25('amplop').pindahMasuk === 10000 && t25('amplop').beda === 0, J(B25.tempat));
ok('BK: TIAP tempat menutup: awal + masuk − keluar ± pindah + beda = akhir; Σ empat = jumlah', B25.tempat.every(function (x) { return Math.abs(x.awal + x.masuk - x.keluar + x.pindahMasuk - x.pindahKeluar + x.beda - x.akhir) < 0.5; }) && B25.total.akhir === 820000 + 25500000 + 2346000 + 310000 && B25.total.awal === 28300000, J(B25.total));
var B26 = khBukuHari('2026-11-26', KINI); var t26 = function (k) { return B26.tempat.find(function (x) { return x.id === k; }); };
ok('BK: hari ini laci 820.000 + 200.000 − 20.000 − 80.000 = 920.000; brankas 25.500.000 − galon 60.000 − setor 15.000.000; rekening + transfer + bon QRIS + setoran', t26('laci').akhir === 920000 && t26('brankas').akhir === 10440000 && t26('rekening').akhir === 2346000 + 750000 + 120000 + 15000000 && B26.tempat.every(function (x) { return x.beda === 0; }), J(B26.tempat));
ok('BK: hari ini empat tempat (tanpa catatan sesudah tutup) = kas mesin', B26.hariIni && B26.cocokMesin === true, J([B26.cocokMesin, saldoKantong().total, saldoKantong().mesin]));
var B23 = khBukuHari('2026-11-23', KINI);
ok('BK: hari sebelum ada patokan → belum bisa dihitung (disebut, tidak 0)', B23.tempat.every(function (x) { return x.awal === null && x.akhir === null && x.beda === null; }) && B23.total.akhir === null && /belum ada hitungan tutup hari/.test(B23.teksAwal), J(B23));
ok('BK: patokan disetel ulang (catat isi rekening) → beda rekening DISEBUT', (function () { pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-11-26', laci: 920000, brankas: 10440000, rekening: 18000000, amplop: 310000, diubahPada: '2026-11-26T07:00:00.000Z' }]);
  var B = khBukuHari('2026-11-26', KINI); var r = B.tempat.find(function (x) { return x.id === 'rekening'; }); pasok('pengaturan', JSON.parse(J(KOTAK.pengaturan))); return r.beda === 18000000 - 18216000 && /patokan/.test(r.sebab); })());

// ==================== CR · COCOK REKENING ====================
var CB = crBaris('2026-11-25', '2026-11-26'); var kb = function (k) { return CB.find(function (x) { return x.kunci === k; }); };
ok('CR: QRIS satu NOTA satu baris (q1 = 2 baris penjualan 300.000), transfer, bon QRIS, potongan QRIS, setoran', CB.length === 6 && kb('n:q1').n === 300000 && kb('n:q1').jenis === 'qris' && kb('n:q2').n === 50000 && kb('n:tf1').jenis === 'transfer'
  && kb('g:2001:m').jenis === 'qris' && /Bayar bon/.test(kb('g:2001:m').ket) && kb('g:mdr-2026-11-25:k').jenis === 'mdr' && kb('g:mdr-2026-11-25:k').arah === 'keluar' && kb('p:st1:m').n === 15000000, J(CB));
var net = CB.reduce(function (a, x) { return a + (x.arah === 'masuk' ? x.n : -x.n); }, 0); var dRek = khPosisi('2026-11-26').rekening - khPosisi('2026-11-24').rekening;
ok('CR: IDENTITAS Σ baris rekening 25–26 Nov = gerakan rekening saldoKantong (16.216.000)', Math.abs(net - dRek) < 0.5 && net === 16216000, J([net, dRek]));
ok('CR: tunai, laci, brankas, amplop laci TIDAK ikut', !CB.some(function (x) { return x.kunci === 'n:t1' || x.kunci === 'g:3002:k' || x.kunci === 'p:pd-2026-11-25:k'; }));
var C1 = crSusunCentang([kb('n:q1')], true, W, 'tangan'); var dc = dokAtur(C1, 'cocokRek-2026-11');
ok('CR: centang = dokumen aturanToko/cocokRek-2026-11 { cek: { kunci: { t, cara } } }', dc && dc.bulan === '2026-11' && dc.cek['n:q1'].t === '2026-11-26' && dc.cek['n:q1'].cara === 'tangan', J(C1));
terapkanKeCache(C1.dokumen); var C2 = crSusunCentang([kb('n:q2')], true, W, 'tangan'); var dc2 = dokAtur(C2, 'cocokRek-2026-11');
ok('CR: centang kedua MEMBAWA centang lama', dc2.cek['n:q1'] && dc2.cek['n:q2'], J(dc2));
terapkanKeCache(C2.dokumen); ok('CR: crCek & crBarisCek membaca centang', !!crCek()['n:q1'] && crBarisCek('2026-11-25', '2026-11-26').filter(function (x) { return x.cek; }).length === 2);
var C3 = crSusunCentang([kb('n:q1')], false, W, 'tangan'); terapkanKeCache(C3.dokumen); ok('CR: lepas centang menghapus satu kunci saja', !crCek()['n:q1'] && !!crCek()['n:q2']);
var H0 = crHitungHasil({ tanggal: '2026-11-26', saldoBank: '18216000' }, KINI);
ok('CR: baris buku yang BELUM dicek = "ada di buku, belum ada di mutasi": bank = buku tapi 5 baris belum dicek → belum terjelaskan +16.166.000 (minta dicentang)', !H0.tolak && H0.selisih === 0 && H0.belum.length === 5 && H0.rpBelum === 16166000 && H0.sisa === 16166000 && !H0.terjelaskan, J(H0));
ok('CR: riwayat setelan MELEWATI cocokRek- (catatan), tetap mencatat aturanToko/rekening (setelan)', !rsdDicatat('aturanToko', 'cocokRek-2026-11', true) && rsdDicatat('aturanToko', 'rekening', true));
// angka & tanggal
ok('CR: rupiah 1.234.567,00 · 1,234,567.00 · Rp 50.000 · (25.000) · 2.500,00 DB · 750 CR', crAngka('1.234.567,00', '').n === 1234567 && crAngka('1,234,567.00', '').n === 1234567 && crAngka('Rp 50.000', '').n === 50000 && crAngka('(25.000)', '').tanda === -1
  && crAngka('2.500,00 DB', '').tanda === -1 && crAngka('2.500,00 DB', '').n === 2500 && crAngka('750 CR', '').tanda === 1 && crAngka('abc', '') === null && crAngka('12,5', '').n === 12.5);
ok('CR: tanggal 26/11/2026 · 2026-11-26 · 26-11-26 · 26 Nov 2026 · 26/11 (tahun bawaan) · mdy · tanggal mustahil ditolak', crTanggal('26/11/2026', 'dmy', 2026) === '2026-11-26' && crTanggal('2026-11-26', 'dmy') === '2026-11-26' && crTanggal('26-11-26', 'dmy') === '2026-11-26'
  && crTanggal('26 Nov 2026', 'dmy') === '2026-11-26' && crTanggal('26/11', 'dmy', 2026) === '2026-11-26' && crTanggal('11/26/2026', 'mdy') === '2026-11-26' && crTanggal('31/02/2026', 'dmy') === '' && crTanggal('Keterangan', 'dmy') === '');
var M = crBacaMutasi(CSV, null, KINI);
ok('CR: CSV berkepala dibaca: tanggal, keterangan (koma di dalam kutip), debet/kredit, saldo', M.mode === 'tabel' && M.baris.length === 6 && M.baris[0].tanggal === '2026-11-25' && M.baris[0].n === 346000 && M.baris[0].arah === 'masuk' && /GOPAY, MERCHANT/.test(M.baris[0].ket)
  && M.baris[4].arah === 'keluar' && M.baris[4].n === 2500 && M.baris[5].saldo === 17713500 && M.bentuk.kolom.keluar === 2 && M.bentuk.kolom.masuk === 3 && !M.lewat.length, J(M));
var buku = crBarisCek(crRentangBuku(M.baris).dari, crRentangBuku(M.baris).sampai); var CC = crCocokkan(M.baris, buku, crAtur());
ok('CR: cocok PERSIS transfer, bon QRIS, setoran; QRIS GABUNG pencairan 346.000 = 300.000 + 50.000 − potongan 4.000', CC.pasang.length === 4 && CC.pasang.filter(function (p) { return p.cara === 'gabung'; }).length === 1
  && J(CC.pasang.find(function (p) { return p.cara === 'gabung'; }).kunci.slice().sort()) === J(['g:mdr-2026-11-25:k', 'n:q1', 'n:q2']) && CC.mutasiSaja.length === 2 && CC.bukuSaja.length === 0, J(CC));
var tgl = {}; var pilih = []; CC.pasang.forEach(function (p) { p.kunci.forEach(function (k) { var b = buku.find(function (x) { return x.kunci === k; }); if (b && !b.cek) { pilih.push(b); tgl[k] = M.baris[p.m].tanggal; } }); });
var CT = crSusunCentang(pilih, true, W, 'berkas', tgl); terapkanKeCache(CT.dokumen);
ok('CR: terapkan dari berkas: semua baris buku 25–26 Nov tercentang, cara berkas + tanggal mutasi', crBarisCek('2026-11-25', '2026-11-26').every(function (x) { return x.cek; }) && crCek()['n:tf1'].cara === 'berkas' && crCek()['n:tf1'].m === '2026-11-26', J(crCek()));
var T2 = crBacaMutasi(TEKS, null, KINI);
ok('CR: teks bebas (salinan PDF): tanggal di depan, nominal = angka sebelum saldo, arah CR/DB; baris tanpa angka / arah DILEWATI dengan sebabnya', T2.mode === 'teks' && T2.baris.length === 2 && T2.baris[0].n === 750000 && T2.baris[0].arah === 'masuk' && T2.baris[1].arah === 'keluar' && T2.baris[1].n === 2500
  && T2.lewat.some(function (x) { return /arah/.test(x.sebab); }), J(T2));
// bentuk berkas diingat
var SB = crSusunBentuk(M.bentuk, 'Mutasi contoh', W); terapkanKeCache(SB.dokumen); var M2 = crBacaMutasi(CSV, null, KINI);
ok('CR: bentuk diingat → berkas berkepala sama DIKENALI; tanpa kepala tidak bisa diingat', M2.dikenali === 'Mutasi contoh' && crAtur().bentuk.length === 1 && !!crSusunBentuk(T2.bentuk, 'x', W).tolak, J([M2.dikenali, crAtur().bentuk]));
var BB = JSON.parse(J(M.bentuk)); BB.kolom.ket = 0; var M3 = crBacaMutasi(CSV, BB, KINI); ok('CR: bentuk yang diubah owner (kolom keterangan) dipakai', /^\d/.test(M3.baris[0].ket), J(M3.baris[0]));
ok('CR: setelan cocok (toleransi, jenis) membawa bentuk tersimpan; angka ngawur ditolak', (function () { var r = crSusunAtur({ toleransiHari: '2', toleransiRp: '0', jenis: ['Uang pribadi owner', 'Biaya bank / admin'] }, W); var d = dokAtur(r, 'rekening'); return d && d.toleransiHari === 2 && d.bentuk.length === 1 && d.jenis.length === 2 && !!crSusunAtur({ toleransiHari: '99' }, W).tolak; })());
// hasil cocok saldo
var DRAF = { tanggal: '2026-11-26', saldoBank: '17.713.500', tambahan: [{ ket: 'biaya adm', n: '-2500', jenis: 'Biaya bank / admin' }, { ket: 'tarik pribadi', n: '-500000', jenis: 'Uang pribadi owner' }] };
var H = crHitungHasil(DRAF, KINI);
ok('CR: bank 17.713.500 − buku 18.216.000 = −502.500, dijelaskan biaya bank 2.500 + pribadi 500.000 → TERJELASKAN', !H.tolak && H.buku === 18216000 && H.selisih === -502500 && H.bawaan === 0 && H.rpBelum === 0 && H.rpTambah === -502500 && H.sisa === 0 && H.terjelaskan && H.dari === '2026-11-01', J(H));
ok('CR: tanpa penjelasan → sisa belum terjelaskan −502.500', crHitungHasil({ tanggal: '2026-11-26', saldoBank: '17713500' }, KINI).sisa === -502500);
ok('CR: saldo bank kosong / ngawur / tanggal tanpa patokan DITOLAK dengan sebabnya', /Ketik saldo/.test(crHitungHasil({ tanggal: '2026-11-26', saldoBank: '' }, KINI).tolak) && /tidak terbaca/.test(crHitungHasil({ tanggal: '2026-11-26', saldoBank: 'abc' }, KINI).tolak)
  && /belum bisa dihitung/.test(crHitungHasil({ tanggal: '2026-11-20', saldoBank: '1' }, KINI).tolak));
var CS = crSusunHasil(DRAF, W, KINI); var dh = dokAtur(CS, 'cocokRek-2026-11');
ok('CR: hasil cocok DISIMPAN di dokumen bulan itu (centang ikut dibawa) — patokan kas TIDAK ditulis', dh && dh.hasil.saldoBank === 17713500 && dh.hasil.sisa === 0 && dh.hasil.tambahan.length === 2 && Object.keys(dh.cek).length >= 6 && !CS.dokumen.some(function (x) { return x.koleksi === 'pengaturan'; }) && /Patokan kas tidak diubah/.test(CS.patch.kabar), J(CS));
terapkanKeCache(CS.dokumen);
ok('CR: ringkasan: terakhir dicocokkan 26 Nov, selisih disebut; semua baris sejak awal bulan lalu sudah dicek', (function () { var R = crRingkas(KINI); return R.akhir && R.akhir.tanggal === '2026-11-26' && /Terakhir dicocokkan 26 Nov/.test(R.teks) && R.nBelum === 0 && R.nBaris === 6 && R.dari === '2026-10-01' && /sudah dicek/.test(R.teks); })(), J(crRingkas(KINI)));
var CS2 = crSusunHasil(Object.assign({}, DRAF, { tambahan: [] }), W, KINI); terapkanKeCache(CS2.dokumen); var dh2 = dokAtur(CS2, 'cocokRek-2026-11');
ok('CR: cocok ulang hari yang sama: hasil lama turun ke riwayatHasil (tidak hilang)', dh2.riwayatHasil.length === 1 && dh2.riwayatHasil[0].sisa === 0 && dh2.hasil.sisa === -502500 && crSemuaHasil().length === 2);
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-11-27', laci: 1, brankas: 1, rekening: 1, amplop: 1, diubahPada: '2026-11-27T14:00:00.000Z' }]);
var H3 = crHitungHasil({ tanggal: '2026-11-28', saldoBank: '10' }, new Date('2026-11-28T10:00:00+07:00'));
ok('CR: cocok sesudahnya: baris dari sehari sesudah cocok terakhir, bawaan = sisa cocok terakhir (−502.500)', !H3.tolak && H3.dari === '2026-11-27' && H3.bawaan === -502500 && H3.prev.tanggal === '2026-11-26', J(H3));
pasok('pengaturan', JSON.parse(J(KOTAK.pengaturan)));
// pengingat cocok bulanan
var KP = khSumberPengingat(KINI);
ok('CR: pengingat: Oktober belum dicocokkan (jatuh 31 Okt) · November sudah → tidak ada pengingat November', KP.some(function (p) { return p.id === 'rekening|2026-10' && p.jatuh === '2026-10-31'; }) && !KP.some(function (p) { return p.id === 'rekening|2026-11'; }), J(KP));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
var galat = []; var CAD = __CAD__; var hasil = { tempat: 0, hari: 0, tidakMenutup: [], identitas: null, ks: null, cr: null };
try { Object.keys(CAD).forEach(function (k) { if (Array.isArray(CAD[k])) pasok(k, CAD[k]); }); setelSumber('cadangan', 'asap'); } catch (e) { galat.push('muat: ' + e.message); }
var akhir = (function () { var t = ''; (CAD.penjualan || []).forEach(function (p) { if ((p.tanggal || '') > t) t = p.tanggal; }); return t; })(); var KINI = new Date(akhir + 'T20:00:00+07:00');
try { for (var i = 0; i < 14; i++) { var t = new Date(Date.parse(akhir + 'T00:00:00Z') - i * 86400000).toISOString().slice(0, 10); var B = khBukuHari(t, KINI); hasil.hari++;
  B.tempat.forEach(function (x) { if (x.awal === null || x.akhir === null) return; hasil.tempat++; if (Math.abs(x.awal + x.masuk - x.keluar + x.pindahMasuk - x.pindahKeluar + x.beda - x.akhir) >= 0.5) hasil.tidakMenutup.push(t + ':' + x.id); }); } } catch (e) { galat.push('buku kas: ' + e.message); }
try { var T = ambilTitikKas(); if (T) { var dari = new Date(Date.parse(T.tanggal + 'T00:00:00Z') + 86400000).toISOString().slice(0, 10); var C = crBaris(dari, akhir); var net = C.reduce(function (a, x) { return a + (x.arah === 'masuk' ? x.n : -x.n); }, 0);
  var S = saldoKantong(akhir); hasil.identitas = { baris: C.length, cocok: Math.abs((T.rekening + net) - S.rekening) < 0.5 }; } } catch (e) { galat.push('baris rekening: ' + e.message); }
try { var K = ksHari(akhir); hasil.ks = { n: K.n, lewat: K.lewat, kurang: K.nNotaKurang }; } catch (e) { galat.push('kas kecil: ' + e.message); }
try { var R = crRingkas(KINI); hasil.cr = { baris: R.nBaris, belum: R.nBelum }; var Bk = crBaris(akhir.slice(0, 7) + '-01', akhir); hasil.crBulan = Bk.length; } catch (e) { galat.push('cocok rekening: ' + e.message); }
try { var SG = ugSetor(); hasil.setor = { nyala: SG.nyala, lewat: SG.lewat }; khSumberPengingat(KINI); } catch (e) { galat.push('setor: ' + e.message); }
print(JSON.stringify({ galat: galat, akhir: akhir, hasil: hasil }));
"""

# kerusakan yang WAJIB membuat uji gagal (kontrol positif)
RUSAK = [
    ('kas kecil: brankas ikut dihitung', UG, "String(h.dari || 'laci') === 'laci' && !h.mdr", "!h.mdr"),
    ('kas kecil: batas per catatan ≥ (150.000 lewat)', UG, "const lewatCatatan = A.batasCatatan > 0 && n > A.batasCatatan;", "const lewatCatatan = A.batasCatatan > 0 && n >= A.batasCatatan;"),
    ('kas kecil: nota tidak wajib', UG, "else if (ks.perluNota && !notaPilih) tolak =", "else if (false) tolak ="),
    ('kas kecil: foto wajib diabaikan', UG, "else if (notaPilih === 'ada' && ks.perluNota && ks.fotoWajib && !D.fotoSiap) tolak =", "else if (false) tolak ="),
    ('kas kecil: aturan uang keluar menghapus kas kecil', UG, "}, ksLama ? { kasKecil: ksLama } : {}) }],", "}, {}) }],"),
    ('kas kecil: setelan kas kecil menghapus kolom lain', UG, "const lama = ugAturDok('uangKeluar') || {}; const data = Object.assign({}, lama, { id: 'uangKeluar',", "const lama = {}; const data = Object.assign({}, lama, { id: 'uangKeluar',"),
    ('kas kecil: id foto tidak dipakai (foto yatim)', UG, "const idDok = D.fotoId && D.idDok !== undefined && D.idDok !== null && String(D.idDok) !== '' ? D.idDok : w.idUnik();", "const idDok = w.idUnik();"),
    ('kas kecil: titipan tablet tidak ditandai', UG, "ks: b.jenis === 'toko' || b.jenis === 'karyawan' ? ksPeriksa(", "ks: false ? ksPeriksa("),
    ('setor: brankas tepat di batas dianggap lewat / pakai total', UG, "const lewat = dasar.nyala && S.brankas > A.setorBatas;", "const lewat = dasar.nyala && S.total > A.setorBatas;"),
    ('setor: rutin menyetor semua brankas (tanpa sisakan)', UG, "n: Math.max(0, Math.round(S.brankas - A.setorSisa)), bisa: S.brankas - A.setorSisa >= 1,", "n: Math.max(0, Math.round(S.brankas)), bisa: S.brankas >= 1,"),
    ('setor: aturan pindah menghapus kolom lama', UG, "data: Object.assign({}, lama, { id: 'pindahUang',", "data: Object.assign({}, {}, { id: 'pindahUang',"),
    ('buku kas: catatan sesudah tutup tidak dihitung', KR, "  ingatGerakanKas().forEach((r) => { if (!susul(r)) return; const k = tempat(r); if (r.masuk > 0) s[k] += r.masuk; if (r.keluar > 0) s[k] -= r.keluar; });\n", ""),
    ('buku kas: beda dihitung dengan tanda terbalik', KR, "Math.round(akhir - awal - gerak)", "Math.round(awal + gerak - akhir)"),
    ('buku kas: patokan = titik kas sekarang saja (tutup hari lampau diabaikan)', KR, "  ambilTutupHari().forEach((d) => { if (!d || !d.titik || !khIsoSah(d.tanggal) || d.tanggal > iso) return;", "  [].forEach((d) => { if (!d || !d.titik || !khIsoSah(d.tanggal) || d.tanggal > iso) return;"),
    ('rekening: QRIS per baris penjualan, bukan per nota', KR, "dorong('n:' + kunciNota(p), r.t,", "dorong('n:' + p.id, r.t,"),
    ('rekening: pindah ke rekening tidak ikut (identitas)', KR, "    if (p.ke === 'rekening') dorong('p:' + p.id + ':m',", "    if (false) dorong('p:' + p.id + ':m',"),
    ('rekening: centang menimpa centang lama', KR, "const cek = Object.assign({}, lama.cek || {});", "const cek = {};"),
    ('rekening: QRIS gabung tanpa potongan MDR', KR, "if (d.length && Math.abs(kotor - pot - m.n) <= tolRp + 0.001)", "if (false)"),
    ('rekening: baris belum dicek bertanda terbalik di persamaan', KR, "const sisa = Math.round((selisih - bawaan - rpTambah + rpBelum) * 100) / 100;", "const sisa = Math.round((selisih - bawaan - rpTambah - rpBelum) * 100) / 100;"),
    ('rekening: hasil cocok tanpa bawaan sebelumnya', KR, "const bawaan = prev ? Number(prev.sisa) || 0 : 0;", "const bawaan = 0;"),
    ('rekening: hasil lama di bulan yang sama hilang', KR, "const riwayatHasil = (lama.hasil ? [lama.hasil] : []).concat(", "const riwayatHasil = [].concat("),
    ('rekening: desimal koma ditebak titik', KR, "d = /^\\d{1,3}(\\.\\d{3})+(,\\d{1,2})?$/.test(s) || /^\\d+,\\d{1,2}$/.test(s) ? ',' :", "d = false ? ',' :"),
    ('rekening: tanggal dd/mm dibaca mm/dd', KR, "jadi(th(m[3]), m[2], m[1]);\n", "jadi(th(m[3]), m[1], m[2]);\n"),
    ('rekening: bentuk tersimpan tidak dikenali', KR, "const ingat = !bentuk && tanda ? A.bentuk.find((b) => b.tanda === tanda) || null : null;", "const ingat = null;"),
    ('rekening: pengingat bulan lalu hilang', KR, "  if (!sudah(lalu.slice(0, 7))) out.push(", "  if (false) out.push("),
    ('riwayat setelan: cocokRek- ikut dicatat', RS, "&& !RSD_LEWAT_AWALAN.some((a) => (koleksi + '/' + String(id)).indexOf(a) === 0)", ""),
]
STATIS = [
    ('Uang: keluarga Rekening & gambarnya', 'uang', ["s.keluarga === 'rekening' ? gambarRekening(s, L)", 'data-k="k-rek"', 'data-k="cr-cocok"', 'data-k="cr-berkas"', 'data-berkas-mutasi', 'data-aksi="crTerapkan"', 'data-aksi="crSimpan"', 'data-aksi="crCentang"']),
    ('Uang: kas kecil di isian, buku & atur; foto nota dulu baru catatan', 'uang', ['${H.ks ? kartuKasKecil(s, H) : \'\'}', '${barisNota(s, r)}', 'aturKasKecil(s)', 'data-foto-nota="catat"', 'data-foto-nota="tanda"', "const F = await kirimFotoNota(fotoNota, idDok, w0);", "r = UG.susunKeluar(Object.assign({}, D, { idDok, fotoId: F.id }), waktu(), null);"]),
    ('Uang: setor ke bank di Pindah uang (info + atur)', 'uang', ['data-k="setor"', 'data-k="atur-setor"', 'data-kolom="setorBatas"', 'data-kolom="setorSisa"']),
    ('Laporan › Harian: buku kas semua tempat', 'laporan', ['kartuBukuTempat(t)', 'data-k="buku-tempat"', 'KR.khBukuHari(t, kini())']),
    ('Dasbor: awal hari, kas kecil, setor, rekening', 'dasbor', ['data-k="db-awal-hari"', 'data-k="db-kas-kecil"', 'data-k="db-setor"', 'data-k="db-rekening"']),
    ('Dasbor logika: angka apa adanya dari sumbernya', 'dasborL', ['kasKecil: dbCoba(() => ksHari(iso))', 'rekening: dbCoba(() => crRingkas(kini))', 'setor: dbCoba(() => ugSetor())']),
    ('app.js: pengingat uang owner lewat lokal.uang; foto Uang', 'app', ['return khSumberPengingat(sekarangCadangan || new Date());', "foto: { ada: () => sumberData().jenis === 'firestore', baca: (idBon) => fb.bacaFotoBon(idBon)"]),
    ('sistem-logika: tiga jenis pengingat baru', 'sistem', ["['setor', 'Setor ke bank (brankas lewat batas)', 'hariSetor']", "['rekening', 'Cocok saldo rekening usaha akhir bulan', 'hariRekening']", "['tagih', 'Hari tagih bon pelanggan', 'hariTagih']", "p.jenis === 'setor' || p.jenis === 'rekening'"]),
    ('bluBCA → rekening usaha (owner 26 Nov)', 'tutup', ['cocokkan dengan mutasi rekening usaha']),
    ('modul dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/kas-rekening-logika.js">']),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_kas_rekening.py && python3 alat-uji/uji_kas_rekening.py --kontrol']),
    ('BACA-DULU menyebut paket ini', 'baca', ['## Kas & rekening + bon pelanggan eceran', 'kas-rekening-logika.js', 'cocokRek-']),
]
RUSAK_STATIS = [
    ('Uang tanpa keluarga Rekening', 'uang', "s.keluarga === 'rekening' ? gambarRekening(s, L)", "false ? gambarRekening(s, L)"),
    ('foto ditulis SESUDAH catatan (urutan tulis)', 'uang', "const F = await kirimFotoNota(fotoNota, idDok, w0);", "const F = { ok: true };"),
    ('Laporan tanpa buku kas semua tempat', 'laporan', 'kartuBukuTempat(t)', "''"),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_kas_rekening.py', 'true'),
    ('bluBCA kembali', 'tutup', 'cocokkan dengan mutasi rekening usaha', 'cocokkan dengan mutasi bluBCA'),
]


def bundel(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in bundel_baru.lengkapi(MODUL))
    return js


def jalan(teks, isi=None):
    js = JAM + bundel(teks) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CSV = ' + json.dumps(CSV) + ';\nvar TEKS = ' + json.dumps(TEKS) + ';\nvar SETOR = ' + json.dumps(SETOR) + ';\n' + (isi or SKENARIO)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return None, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    return json.loads(out), None


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    kr = src['kr']
    if 'document.' in kr or 'tulisDokumen' in kr: g.append('kas-rekening-logika menyentuh DOM / menulis langsung — modul ini cuma menyusun')
    if "koleksi: 'pengaturan'" in kr: g.append('kas-rekening-logika menulis pengaturan (titik kas) — hasil cocok TIDAK boleh menimpa titik kas')
    if src['rules'].count('cocokRek') or src['rules'].count('kasKecil'): g.append('rules disentuh — paket ini sengaja tanpa rules baru')
    return len(STATIS) - len(g), g


def muat():
    sumber = set(bundel_baru.lengkapi(MODUL))
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in sumber), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama + ' (' + str(teks[berkas].count(a)) + '×)'); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b); h, e = jalan(T); g = e if h is None else h['gagal']
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_STATIS:
            if src[berkas].count(a) < 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            S = dict(src); S[berkas] = S[berkas].replace(a, b); l, g = statis(S)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h, e = jalan(teks); ls, gs = statis(src)
    g = e if h is None else h['gagal']
    print('KOTAK PASIR: %d lulus · %d gagal' % (0 if h is None else h['lulus'], len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '..', '..', '..', '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and '--tanpa-asap' not in sys.argv:
        ha, ea = jalan(teks, ASAP.replace('__CAD__', open(cad[-1], encoding='utf-8').read()))
        if ha is None: print('ASAP DATA TOKO: JSC JATUH ' + ea[0][:600]); g = list(g) + ['asap']
        else:
            H = ha['hasil']; beres = not ha['galat'] and not H['tidakMenutup'] and (H['identitas'] is None or H['identitas']['cocok'])
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %d tempat-hari menutup dari %d hari · identitas baris rekening %s · galat %s'
                  % (os.path.basename(cad[-1]), ha['akhir'], 'LULUS' if beres else 'GAGAL', H['tempat'], H['hari'], json.dumps(H['identitas']), json.dumps(ha['galat'], ensure_ascii=False)))
            if not beres: g = list(g) + ['asap: ' + json.dumps(H['tidakMenutup'][:5]) + ' ' + json.dumps(ha['galat'], ensure_ascii=False)]
    sys.exit(1 if g or gs else 0)
