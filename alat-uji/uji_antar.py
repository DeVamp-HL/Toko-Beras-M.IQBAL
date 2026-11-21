#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_antar.py — B3 SURAT JALAN & ANTAR (keputusan owner 18 Nov 2026). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  · ongkir = baris terpisah di struk, MENEMPEL di satu baris nota (kolom ongkirAntar, ikut hargaTotal): sesudah potongan, sebelum pembulatan Rp500;
    kas & bon = mesin beku apa adanya; Laporan per merek memisahkannya (baris luar 'ongkir', menutup ke laba kotor); retur tidak mengembalikan ongkir;
  · surat jalan lahir BERSAMA notanya (satu kiriman), nomor SJ<yy>-<kode perangkat>-<urut>, semua baris nota membawa noSJ;
  · bayar di tempat = nota bon sementara (cara Kredit), BEBAS batas kredit hari itu; uang pulang = pelunasan ber-untukSJ (dibawaOleh pengantar,
    untukFaktur bila faktur); belum disetor = peringatan merah (Dasbor, tutup hari) atas nama pengantar;
  · tanda terima: tanda tangan WAJIB, foto boleh dilewati; gagal antar; batal (owner); pembatalan nota ikut membatalkan surat jalannya;
  · SUSULAN owner 18 Nov (perangkat kasir cuma satu): tanda tangan DI KERTAS = cara utama — surat jalan dicetak 2 lembar (pembeli · toko), lembar toko
    ditandatangani & dibawa pulang, di toko ditandai diterima + FOTO lembar (WAJIB); rules v10 tidak berubah (buktiTtd kosong, kolom tetap di daftar tandai);
  · penjaga kiriman = rules v10: ben membuat (bersama nota), karyawan tidak; pengantar menandai dengan kolom terbatas; batal = owner;
  · Pelanggan › Atur: tarif ongkir bawaan, yang bisa mengantar, kendaraan.

    python3 alat-uji/uji_antar.py            → N lulus · 0 gagal
    python3 alat-uji/uji_antar.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_faktur, uji_jual_baru, uji_laporan_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
AJ = 'baru/js/layar/antar-logika.js'; JL = 'baru/js/layar/jual-logika.js'; AK = 'baru/js/data/akses.js'; STK = 'baru/js/layar/struk-logika.js'
RT = 'baru/js/layar/retur-logika.js'; LP = 'baru/js/layar/laporan-logika.js'; TH = 'baru/js/layar/tutup-hari-logika.js'; PL = 'baru/js/layar/pelanggan-logika.js'
MODUL = [m for m in uji_faktur.MODUL if m != AJ] + [AJ]
MODUL_LP = [m for m in uji_laporan_baru.MODUL if m != AJ] + [AJ]
MODUL_LP = MODUL_LP + [m for m in ['baru/js/layar/titipan-logika.js'] if m not in MODUL_LP]   # owner 21 Nov 2026: tutup hari menyebut titipan tablet
SUMBER = {'jual': 'baru/js/layar/jual.js', 'panel': 'baru/js/layar/antar-panel.js', 'app': 'baru/js/app.js', 'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml',
          'rules': 'firestore.rules', 'koleksi': 'baru/js/data/koleksi.js', 'firebase': 'baru/js/data/firebase.js', 'akses': AK, 'antar': AJ, 'pelanggan': 'baru/js/layar/pelanggan.js',
          'dasbor': 'baru/js/layar/dasbor.js', 'dasborL': 'baru/js/layar/dasbor-logika.js', 'uang': 'baru/js/layar/uang.js', 'sistem': 'baru/js/layar/sistem-logika.js'}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
var J = function (x) { return JSON.stringify(x); };
var nId = 9000; var W = { tanggal: '2026-11-18', jam: '10:00', kini: '2026-11-18T03:00:00.000Z', kodePerangkat: 'TES', idUnik: function () { nId += 1; return nId; } };
var KINI = new Date('2026-11-18T10:00:00+07:00');
var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
var BEN = keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true });
var KRY = keadaanAkun('kry.contoh@tokoberasmiqbal.web.app', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true });
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
pasok('aksesAkun', [{ id: 'uid-ben', uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true }, { id: 'uid-kry', uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true }]);
setelSumber('cadangan', 'kotak pasir');
var hak = function (akun) { return Object.assign({}, (ssAtur('peran').hak || {})[akun.peran] || {}, { jatahNego: ngJatah(akun) }); };
var atribusi = function (akun, d, ada) { return beriAtribusiAkun(d, akun, { perangkat: 'p-uji', kini: W.kini }, ada); };
var kirim = function (akun, dok) { return periksaKiriman(akun, (dok || []).map(function (x) { return { koleksi: x.koleksi, data: atribusi(akun, x.data, false), ada: false, lama: null }; }), [], hak(akun), KINI); };
var kirimUbah = function (akun, koleksi, lama, baru) { return periksaKiriman(akun, [{ koleksi: koleksi, data: atribusi(akun, baru, true), ada: true, lama: lama }], [], hak(akun), KINI); };
var s = keadaanAwal(); s.sekarang = KINI;
function terap(p) { s = Object.assign({}, s, p); sinkronKeranjang(s); return p; }
function chip(jalur, kunci, berat) { var r = susunRak(s); return r[jalur].find(function (c) { return c.kunci === kunci && (!berat || c.berat === berat); }); }
function mulai() { s = keadaanAwal(); s.sekarang = KINI; sinkronKeranjang(s); }
function isi(jalur, kunci, n, berat) { terap(ketukChip(s, chip(jalur, kunci, berat))); terap({ ketik: String(n) }); terap(masukkan(s)); }
var dok = function (N, kol) { return N.dokumen.filter(function (x) { return x.koleksi === kol; }).map(function (x) { return x.data; }); };
var SET = { id: 'hargaTingkat', tingkat: [{ id: 'warung', nama: 'Warung', potKg: 0 }], barang: {}, orang: { 'bu suti': 'warung' }, khusus: [] };
var ATUR = { id: 'pelanggan', tarifOngkir: 15000, pengantarAntar: ['Ben', 'Kurir Contoh'], kendaraanAntar: ['Motor'] };
pasok('aturanToko', [JSON.parse(J(SET))]);
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'warung depan pasar', tempoHari: 7, alamat: 'Jl. Contoh 1', batasKredit: 150000 }]);

// ---- A · Atur antar (Pelanggan › Atur)
var A0 = ajAtur();
ok('A: belum diatur → tarif 0, pengantar [Ben], kendaraan kosong', A0.tarif === 0 && J(A0.pengantar) === '["Ben"]' && A0.kendaraan.length === 0, J(A0));
pasok('aturanToko', [JSON.parse(J(SET)), ATUR]);
var A1 = ajAtur();
ok('A: diatur owner → tarif 15.000, pengantar Ben & Kurir Contoh, kendaraan Motor', A1.tarif === 15000 && J(A1.pengantar) === '["Ben","Kurir Contoh"]' && J(A1.kendaraan) === '["Motor"]', J(A1));
ok('A: tarif "Rp 20.000" terbaca 20000; minus / huruf ditolak', ajRupiahSah('Rp 20.000') === 20000 && ajRupiahSah('-5') === null && ajRupiahSah('dua') === null && ajRupiahSah('') === 0);
ok('A: Atur menolak pengantar kosong & nama ganda', !!ajBacaAtur({ pengantarAntar: [] }).tolak && !!ajBacaAtur({ pengantarAntar: ['Ben', 'ben'] }).tolak && !!ajBacaAtur({ tarifOngkir: 'x' }).tolak);
var SA = susunAturPelanggan(Object.assign({}, aturPelanggan(), { kosongKali: '30', tarifOngkir: '12000', pengantarAntar: ['Ben'], kendaraanAntar: [] }), W);
var SAd = SA.dokumen && SA.dokumen[0].data;
ok('A: simpan Atur Pelanggan menulis tarif & daftar antar (dokumen aturanToko/pelanggan yang dibaca tablet)', SAd && SAd.tarifOngkir === 12000 && J(SAd.pengantarAntar) === '["Ben"]' && J(SAd.kendaraanAntar) === '[]' && /ongkir bawaan Rp12\.000/.test(SA.patch.kabar), J(SA.tolak || SAd));

// ---- B · nota DIANTAR, tunai: ongkir sesudah potongan, sebelum pembulatan; surat jalan satu kiriman
mulai(); isi('kemasan', 'Kembang|5', 1); terap({ pelanggan: 'Bu Suti', antar: ajDrafBaru('Bu Suti') });
ok('B: draf antar mengambil alamat kartu & tarif bawaan & pengantar pertama', s.antar.alamat === 'Jl. Contoh 1' && s.antar.ongkir === '15000' && s.antar.pengantar === 'Ben' && s.antar.kendaraan === 'Motor' && s.antar.cod === false, J(s.antar));
terap({ antar: Object.assign({}, s.antar, { ongkir: '12300' }), potongan: 2000 });
var T1 = hitungTagihan(s);
ok('B: tagihan = 72.000 − potongan 2.000 + ongkir 12.300 = 82.300 → dibulatkan 82.500 (ongkir tidak dipotong)', T1.ongkir === 12300 && T1.potongan === 2000 && T1.bersih === 82300 && T1.total === 82500 && T1.bulat === 200, J(T1));
terap(uangPas(s));
ok('B: sah dicatat', alasanTolak(s) === '', alasanTolak(s));
var N1 = susunNotaDokumen(s, W); var P1 = dok(N1, 'penjualan'); var SJ1 = dok(N1, 'suratJalan')[0];
var jumlahNota = P1.reduce(function (a, p) { return a + p.hargaTotal; }, 0);
ok('B: Σ hargaTotal baris = yang ditagih (82.500) — kas mesin beku membaca nota apa adanya', jumlahNota === 82500 && N1.totalBayar === 82500, J(P1.map(function (p) { return [p.hargaTotal, p.ongkirAntar, p.pembulatan, p.potonganTransaksi]; })));
ok('B: ongkir menempel di TEPAT satu baris (kolom ongkirAntar 12.300)', P1.filter(function (p) { return p.ongkirAntar; }).length === 1 && P1.filter(function (p) { return p.ongkirAntar; })[0].ongkirAntar === 12300);
ok('B: surat jalan lahir bersama nota: SJ26-TES-0001, trxId nota, alamat, pengantar Ben · Motor, ongkir, bukan bayar di tempat', SJ1 && SJ1.noSJ === 'SJ26-TES-0001' && String(SJ1.trxIdJual) === String(N1.trxId) && SJ1.alamat === 'Jl. Contoh 1'
  && SJ1.pengantar === 'Ben' && SJ1.kendaraan === 'Motor' && SJ1.ongkir === 12300 && SJ1.bayarDiTempat === false && SJ1.tagihRp === 0 && SJ1.status === 'berangkat' && SJ1.nilaiNota === 82500, J(SJ1));
ok('B: isi surat jalan TANPA harga (nama, jumlah, satuan)', SJ1.isi.length === 1 && SJ1.isi[0].nama && SJ1.isi[0].jumlah === 1 && !('harga' in SJ1.isi[0]) && !('hargaTotal' in SJ1.isi[0]), J(SJ1.isi));
ok('B: semua baris nota membawa noSJ; tunai → tanpa bayarDiTempat', P1.every(function (p) { return p.noSJ === 'SJ26-TES-0001' && !p.bayarDiTempat && p.caraBayar === 'Tunai'; }));
ok('B: ringkas nota menyebut DIANTAR & ongkir', /DIANTAR · surat jalan SJ26-TES-0001 · ongkir Rp12\.300 · Ben/.test(N1.ringkas), N1.ringkas);
terapkanKeCache(N1.dokumen);
ok('B: nomor berikutnya perangkat yang sama = SJ26-TES-0002; perangkat lain mulai 0001', ajNomorBaru('2026-11-18', 'TES') === 'SJ26-TES-0002' && ajNomorBaru('2026-11-18', 'LAI') === 'SJ26-LAI-0001');
var NS = notaDari({ trxId: N1.trxId }) || notaDariBaris(ambilPenjualanSemua().filter(function (p) { return String(p.trxId) === String(N1.trxId); }));
var ST1 = susunStruk(NS, stAtur(), { kertas: 80 });
ok('B: struk: baris "Ongkir antar +Rp12.300" sendiri, Subtotal = barang 72.000, TOTAL 82.500, menyebut surat jalan', ST1 && /Ongkir antar\s+\+Rp12\.300/.test(ST1.teks) && /Subtotal\s+Rp72\.000/.test(ST1.teks) && /TOTAL\s+Rp82\.500/.test(ST1.teks) && /surat jalan SJ26-TES-0001/.test(ST1.teks), ST1 && ST1.teks);
var brs = ST1.garis.filter(function (g) { return g.jenis === 'barang' || g.jenis === 'rinci'; }).map(function (g) { return g.kanan; }).join('|');
ok('B: baris barang struk TIDAK memuat ongkir (Kembang tetap 72.000)', /72\.000/.test(brs) && !/84\.300|86\.300/.test(brs), brs);

// ---- C · bayar di tempat (COD): bon sementara, bebas batas, tagih di tempat
var bonDekaAwal = hitungPiutang().find(function (r) { return r.kunci === 'deka'; }).sisa;
mulai(); isi('kemasan', 'Kembang|5', 1); terap({ pelanggan: 'Deka', antar: Object.assign(ajDrafBaru('Deka'), { ongkir: '10000', alamat: 'Gang Contoh 2' }) });
terap(ajSetelCod(s, true));
ok('C: bayar di tempat → cara Kredit, uang 0', s.cara === 'Kredit' && s.antar.cod === true && s.uang === 0);
ok('C: Deka belum terdaftar tapi bayar di tempat BEBAS batas kredit (B2 KR1 tidak menahan)', alasanTolak(s) === '' && bonKeranjang(s) === 0, alasanTolak(s));
var sTanpa = Object.assign({}, s, { antar: Object.assign({}, s.antar, { cod: false }) });
ok('C: pembanding: bon biasa yang sama DITAHAN KR1 (bukti pintu COD yang membuka)', alasanTolak(sTanpa) !== '', alasanTolak(sTanpa));
var N2 = susunNotaDokumen(s, W); var P2 = dok(N2, 'penjualan'); var SJ2 = dok(N2, 'suratJalan')[0];
ok('C: baris nota Kredit + bayarDiTempat + noSJ 0002; tanpa persetujuan bon (kreditSetujuId)', P2.every(function (p) { return p.caraBayar === 'Kredit' && p.bayarDiTempat === true && p.noSJ === 'SJ26-TES-0002' && !p.kreditSetujuId; }), J(P2));
ok('C: surat jalan tagih di tempat = total nota 82.000', SJ2.bayarDiTempat === true && SJ2.tagihRp === 82000 && SJ2.nilaiNota === 82000, J(SJ2));
ok('C: ringkas menyebut BAYAR DI TEMPAT', /BAYAR DI TEMPAT Rp82\.000/.test(N2.ringkas), N2.ringkas);
terapkanKeCache(N2.dokumen);
ok('C: bon Deka bertambah tepat 82.000 (mesin beku hitungPiutang)', hitungPiutang().find(function (r) { return r.kunci === 'deka'; }).sisa === bonDekaAwal + 82000);
var COD = ajCodBelumSetor('2026-11-18');
ok('C: tutup hari: bayar di tempat belum disetor — atas nama pengantar Ben Rp82.000', COD.length === 1 && COD[0].sisa === 82000 && COD[0].pengantar === 'Ben' && /Ben Rp82\.000/.test(ajKalimatCod(COD)), J(COD));
ok('C: besok (lewat hari) masih terlihat merah di Dasbor (sampai = semua tanggal ≤), bertanda lewat', ajCodBelumSetor('2026-11-19', true).length === 1 && ajCodBelumSetor('2026-11-19', true)[0].lewat === true);
var D2 = ajDaftar('2026-11-18', '');
ok('C: daftar Antar: 2 di jalan; saring "deka" = 1', D2.jalan.length === 2 && ajDaftar('2026-11-18', 'deka').jalan.length === 1, J(D2.jalan.map(function (x) { return x.noSJ; })));
// faktur: bayar di tempat pelanggan usaha = faktur (B2), surat jalan membawa nomornya
mulai(); isi('kemasan', 'Kembang|5', 1); terap({ pelanggan: 'Bu Suti', antar: Object.assign(ajDrafBaru('Bu Suti'), { ongkir: '0' }) }); terap(ajSetelCod(s, true));
var N3 = susunNotaDokumen(s, W); var SJ3 = dok(N3, 'suratJalan')[0];
ok('C: bayar di tempat pelanggan usaha → nota jadi faktur & surat jalan membawa noFaktur; ongkir 0 tidak menempel', /^F26-TES-/.test(SJ3.noFaktur) && dok(N3, 'penjualan').every(function (p) { return p.noFaktur === SJ3.noFaktur && !p.ongkirAntar; }), J(SJ3));

// ---- D · penolakan draf antar
mulai(); isi('kemasan', 'Kembang|5', 1); terap({ antar: Object.assign(ajDrafBaru(''), { ongkir: 'abc' }) }); terap(uangPas(s));
ok('D: ongkir bukan angka → ditolak', /Ongkir/.test(alasanTolak(s)), alasanTolak(s));
terap({ antar: Object.assign({}, s.antar, { ongkir: '5000', pengantar: '' }) });
ok('D: tanpa pengantar → ditolak', /siapa yang mengantar/.test(alasanTolak(s)), alasanTolak(s));
terap({ antar: Object.assign({}, s.antar, { pengantar: 'Ben' }) }); terap(ajSetelCod(s, true));
ok('D: bayar di tempat tanpa nama pembeli → ditolak', /nama pembelinya/.test(alasanTolak(s)), alasanTolak(s));
terap(pilihCara(s, 'Tunai'));
ok('D: pilih Tunai mematikan bayar di tempat', s.antar.cod === false && s.cara === 'Tunai');
terap({ tukar: { kredit: 1000, ringkas: 'uji', returDraf: {} } });
ok('D: tukar & antar saling meniadakan', /Tukar tidak bisa sekaligus diantar/.test(ajAlasanTolak(s)), ajAlasanTolak(s));
var Dp = parkir(Object.assign({}, s, { tukar: null }));
ok('D: draf antar ikut diparkir & kembali saat dibuka', Dp.antar === null && Dp.antrean[Dp.antrean.length - 1].beku.antar && Dp.antrean[Dp.antrean.length - 1].beku.antar.pengantar === 'Ben');

// ---- E · tanda terima, setor, gagal, batal
var sj2 = ajCari(SJ2.id);
var UP = uangNotaPesanan({ status: 'dibayar', trxIdJual: N2.trxId }, '2026-11-18');
ok('E: pesanan yang notanya bayar di tempat → BELUM lunas: "BAYAR DI TEMPAT — belum setor Rp82.000"', !UP.lunas && UP.sisa === 82000 && /BAYAR DI TEMPAT — belum setor Rp82\.000/.test(UP.kata), J(UP));
ok('E: tanpa tanda tangan → ditolak', /tanda tangan/.test(ajSusunTerima(sj2, { uang: '82000' }, W).tolak || ''));
ok('E: uang lebih dari tagihan → ditolak', /lebih besar/.test(ajSusunTerima(sj2, { ttdId: 'T1', uang: '90000' }, W).tolak || ''));
var R1 = ajSusunTerima(sj2, { ttdId: 'T1', fotoId: '', uang: '82000', caraUang: 'Tunai', penerima: 'Deka', oleh: 'Ben Contoh' }, W);
var M1 = R1.dokumen.filter(function (x) { return x.koleksi === 'piutangMutasi'; })[0].data; var U1 = R1.dokumen.filter(function (x) { return x.koleksi === 'suratJalan'; })[0].data;
ok('E: diterima + uang → pelunasan bayar 82.000 ber-untukSJ, dibawaOleh pengantar Ben, Tunai', M1.tipe === 'bayar' && M1.nominal === 82000 && M1.untukSJ === 'SJ26-TES-0002' && M1.dibawaOleh === 'Ben' && M1.caraBayar === 'Tunai' && M1.namaPelanggan === 'Deka' && !M1.untukFaktur, J(M1));
ok('E: surat jalan diterima: penerima, bukti tanda tangan, tanpa foto, uangDiterima, pelunasanId', U1.status === 'diterima' && U1.penerima === 'Deka' && J(U1.buktiTtd) === '["T1"]' && U1.buktiFoto.length === 0 && U1.uangDiterima === 82000 && String(U1.pelunasanId) === String(M1.id) && U1.riwayatStatus.length === 2, J(U1));
ok('E: kabar: LUNAS · tanpa foto', /LUNAS/.test(R1.patch.kabar) && /tanpa foto/.test(R1.patch.kabar), R1.patch.kabar);
// penjaga kiriman (= rules v10)
var KB1 = kirim(BEN, N2.dokumen);
ok('E: Ben mengirim nota bayar di tempat + surat jalan (satu kiriman) → diterima penjaga', !KB1.tolak, J(KB1));
var simpanS = s; mulai(); isi('kemasan', 'Kembang|5', 1); terap({ antar: Object.assign(ajDrafBaru(''), { ongkir: '5000' }) }); terap(uangPas(s)); var N5 = susunNotaDokumen(s, W); s = simpanS;
var KK1 = kirim(KRY, N5.dokumen);
ok('E: karyawan mengirim nota tunai + surat jalan → DITOLAK (bikin surat jalan = owner & ben)', !!KK1.tolak && /surat jalan/.test(KK1.tolak), J(KK1));
var KK1b = periksaKiriman(KRY, N5.dokumen.map(function (x) { return { koleksi: x.koleksi, data: atribusi(KRY, x.data, false), ada: false, lama: null }; }), [], Object.assign(hak(KRY), { antar: 'sendiri' }), KINI);
ok('E: walau kisi karyawan dibuka owner, penjaga server (BUAT_STAF = rules v10) tetap menolak karyawan membuat surat jalan', !!KK1b.tolak, J(KK1b));
var KB2 = periksaKiriman(BEN, N5.dokumen.map(function (x) { return { koleksi: x.koleksi, data: atribusi(BEN, x.data, false), ada: false, lama: null }; }), [], Object.assign(hak(BEN), { antar: 'tidak' }), KINI);
ok('E: kisi Ben "bikin surat jalan" = tidak boleh → nota antar Ben ditolak (kisi ditegakkan)', !!KB2.tolak && /surat jalan/.test(KB2.tolak), J(KB2));
var KK2 = periksaKiriman(KRY, [{ koleksi: 'suratJalan', data: atribusi(KRY, U1, true), ada: true, lama: sj2 }, { koleksi: 'piutangMutasi', data: atribusi(KRY, M1, false), ada: false, lama: null }], [], hak(KRY), KINI);
ok('E: karyawan (pengantar) menandai diterima + uang pulang → diterima penjaga', !KK2.tolak, J(KK2));
ok('E: karyawan mengubah tagihan saat menandai → DITOLAK', !!kirimUbah(KRY, 'suratJalan', sj2, Object.assign({}, U1, { tagihRp: 1 })).tolak);
ok('E: karyawan membatalkan surat jalan → DITOLAK', !!kirimUbah(KRY, 'suratJalan', sj2, Object.assign({}, sj2, { status: 'batal' })).tolak);
ok('E: Ben membuat surat jalan berisi kolom penerimaan → DITOLAK', !!kirim(BEN, [{ koleksi: 'suratJalan', data: Object.assign({}, SJ2, { penerima: 'x' }) }]).tolak);
ok('E: menandai ulang yang sudah diterima → DITOLAK', !!kirimUbah(BEN, 'suratJalan', U1, Object.assign({}, U1, { status: 'gagal', alasanGagal: 'x' })).tolak);
terapkanKeCache(R1.dokumen);
ok('E: uang di tempat pulang → pesanan nota itu LUNAS', uangNotaPesanan({ status: 'dibayar', trxIdJual: N2.trxId }, '2026-11-18').lunas);
ok('E: sesudah uang pulang: bon Deka kembali ke awal, tidak ada bayar di tempat yang belum disetor', hitungPiutang().find(function (r) { return r.kunci === 'deka'; }).sisa === bonDekaAwal && ajCodBelumSetor('2026-11-18').length === 0);
var NS2 = notaDariBaris(ambilPenjualanSemua().filter(function (p) { return String(p.trxId) === String(N2.trxId); }));
var ST2 = susunStruk(NS2, stAtur(), { kertas: 80 });
ok('E: struk nota bayar di tempat: "BAYAR DI TEMPAT — lunas" + "Dibayar di tempat Rp82.000"', /BAYAR DI TEMPAT — lunas/.test(ST2.teks) && /Dibayar di tempat\s+Rp82\.000/.test(ST2.teks), ST2.teks);
// setor menyusul & sebagian
var sj3 = SJ3; terapkanKeCache(N3.dokumen);
var R3 = ajSusunTerima(ajCari(SJ3.id), { ttdId: 'T3', uang: '20000', caraUang: 'QRIS' }, W); terapkanKeCache(R3.dokumen);
var M3 = R3.dokumen.filter(function (x) { return x.koleksi === 'piutangMutasi'; })[0].data;
ok('E: bayar sebagian di tempat (QRIS) → untukFaktur = faktur surat jalan; sisa tetap bon & merah', M3.caraBayar === 'QRIS' && J(M3.untukFaktur) === J([SJ3.noFaktur]) && ajCodBelumSetor('2026-11-18').length === 1 && ajCodBelumSetor('2026-11-18')[0].sisa === SJ3.tagihRp - 20000, J(M3));
var RS = ajSusunSetor(ajCari(SJ3.id), { uang: String(SJ3.tagihRp - 20000) }, W); terapkanKeCache(RS.dokumen);
ok('E: uang sisa disetor menyusul → lunas, merah hilang', !RS.tolak && ajCodBelumSetor('2026-11-18').length === 0 && /LUNAS/.test(RS.patch.kabar), RS.tolak || RS.patch.kabar);
// gagal antar & batal
var sj1 = ajCari(SJ1.id);
ok('E: gagal antar tanpa alasan → ditolak', !!ajSusunGagal(sj1, '', W).tolak);
var RG = ajSusunGagal(sj1, 'toko tutup', W, 'Ben'); terapkanKeCache(RG.dokumen);
ok('E: gagal antar → status gagal, notanya tetap berlaku → "perlu dibereskan owner"', ajCari(SJ1.id).status === 'gagal' && ajDaftar('2026-11-18', '').gagal.length === 1, J(ajCari(SJ1.id)));
// batalkan nota barusan → surat jalannya ikut batal
var B1 = susunPembatalan({ trxId: N1.trxId, idPenjualan: P1.map(function (p) { return p.id; }), piutangId: null, pesanan: null, retur: null }, 'uji', W);
var BS = B1.dokumen.filter(function (x) { return x.koleksi === 'suratJalan'; });
ok('E: batalkan nota → surat jalannya ikut BATAL di kiriman yang sama', BS.length === 1 && BS[0].data.status === 'batal' && BS[0].data.alasanBatal === 'notanya dibatalkan', J(BS));
ok('E: batal surat jalan (owner) wajib alasan; yang sudah batal ditolak', !!ajSusunBatal(sj1, '', W).tolak && !!ajSusunBatal(Object.assign({}, sj1, { status: 'batal' }), 'uji batal', W).tolak);

// ---- F · retur: ongkir tidak ikut dikembalikan
mulai(); isi('karung', 'Angsa', 2, 50); terap({ antar: Object.assign(ajDrafBaru(''), { ongkir: '20000' }) }); terap(uangPas(s));
var N4 = susunNotaDokumen(s, W); terapkanKeCache(N4.dokumen);
var bK = ambilPenjualanSemua().find(function (p) { return String(p.trxId) === String(N4.trxId) && p.jenis === 'karung'; });
var DR = rtDasarRetur(bK);
ok('F: baris karung membawa ongkir 20.000 (bermodal, terbesar)', bK.ongkirAntar === 20000 && bK.hargaTotal === 1400000, J([bK.ongkirAntar, bK.hargaTotal]));
ok('F: dasar retur per kg = 13.800 (harga beras), bukan 14.000 (ongkir ikut)', DR.ok && Math.abs(DR.perSatuan - 13800) < 0.001 && /ongkir antar Rp20\.000 tidak ikut/.test(DR.dasar), J(DR));

// ---- G · surat jalan cetak & bukti
var G1 = ajGarisCetak(sj2, { nama: 'Toko Contoh', alamat: 'Jl. Contoh', telp: '0800' }); var TX = ajTeksCetak(G1, 32);
ok('G: cetak surat jalan: judul, nomor, kepada, isi tanpa harga barang, TAGIH DI TEMPAT, ruang tanda tangan; tiap baris ≤ 32 kolom', /SURAT JALAN/.test(TX) && /No\. SJ26-TES-0002/.test(TX) && /Kepada : Deka/.test(TX) && /TAGIH DI TEMPAT\s+Rp82\.000/.test(TX) && /Diterima oleh/.test(TX)
  && TX.split('\n').every(function (l) { return l.length <= 32; }) && (TX.match(/Rp/g) || []).length === 1, TX);
var BT = ajSusunBukti(sj2, 'ttd', { jenis: 'image/png', base64: 'iVBORw0KGgo=', lebar: 640, tinggi: 240 }, W);
ok('G: bukti tanda tangan: id, idSJ, noSJ, jenisBukti ttd, png (bentuk rules v10 buktiSah)', BT.data && BT.data.idSJ === String(sj2.id) && BT.data.jenisBukti === 'ttd' && BT.data.jenis === 'image/png' && BT.data.noSJ === 'SJ26-TES-0002', J(BT));
ok('G: bukti bukan gambar / terlalu besar ditolak', !!ajSusunBukti(sj2, 'ttd', { jenis: 'text/html', base64: 'AAAA' }, W).tolak && !!ajSusunBukti(sj2, 'foto', { jenis: 'image/jpeg', base64: new Array(1000001).join('A') }, W).tolak);
ok('G: tanda tangan cukup = ≥ 12 titik goresan', !ajTtdCukup(3) && ajTtdCukup(12));

// ---- H · tanda tangan di KERTAS (owner 18 Nov: perangkat kasir cuma satu, tablet tetap di toko) — foto lembar toko WAJIB; rules v10 tidak berubah
// sj2 sudah lunas di cache (E) → surat jalan bayar di tempat kembarannya yang belum ditandai, nomor lain
var sjK = Object.assign({}, sj2, { id: 'sjK', noSJ: 'SJ26-TES-0099' });
ok('H: kertas tanpa foto lembar → ditolak (walau ada id tanda tangan)', /LEMBAR TOKO/.test(ajSusunTerima(sjK, { cara: 'kertas', ttdId: 'T9', uang: '82000' }, W).tolak || ''));
var RK = ajSusunTerima(sjK, { cara: 'kertas', fotoId: 'F1', uang: '82000', caraUang: 'Tunai', penerima: 'Deka', oleh: 'Ben Contoh' }, W);
var UK = RK.dokumen ? RK.dokumen.filter(function (x) { return x.koleksi === 'suratJalan'; })[0].data : null;
var MK = RK.dokumen ? RK.dokumen.filter(function (x) { return x.koleksi === 'piutangMutasi'; })[0] : null;
ok('H: kertas + foto → diterima TANPA tanda tangan layar: buktiTtd kosong, buktiFoto = foto lembar, riwayat bukti kertas', !!UK && UK.status === 'diterima' && J(UK.buktiTtd) === '[]' && J(UK.buktiFoto) === '["F1"]'
  && UK.riwayatStatus[UK.riwayatStatus.length - 1].bukti === 'kertas' && ajCaraTerima(UK) === 'kertas', RK.tolak || J(UK));
ok('H: uang bayar di tempat tetap tercatat saat menandai (pelunasan 82.000 ber-untukSJ, dibawa Ben)', !!MK && MK.data.nominal === 82000 && MK.data.untukSJ === 'SJ26-TES-0099' && MK.data.dibawaOleh === 'Ben', J(MK));
ok('H: kabar menyebut tanda tangan di kertas', RK.patch && /tanda tangan di kertas/.test(RK.patch.kabar), RK.patch && RK.patch.kabar);
ok('H: cara terima: layar untuk tanda tangan layar; data tanpa keterangan dibaca dari buktiTtd; belum diterima = kosong',
  ajCaraTerima(U1) === 'layar' && U1.riwayatStatus[U1.riwayatStatus.length - 1].bukti === 'layar' && ajCaraTerima(Object.assign({}, U1, { riwayatStatus: [] })) === 'layar'
  && ajCaraTerima(Object.assign({}, UK, { riwayatStatus: [] })) === 'kertas' && ajCaraTerima(sjK) === '');
var ubahK = UK ? Object.keys(UK).filter(function (k) { return J(UK[k]) !== J(sjK[k]); }) : ['?'];
ok('H: kolom yang berubah ⊆ kolom tandai rules v10 (rules tidak perlu terbit ulang)', ubahK.every(function (k) { return AJ_KOLOM_TANDAI.indexOf(k) >= 0; }), J(ubahK));
ok('H: karyawan (pengantar) menandai diterima cara kertas + uang pulang → diterima penjaga', !periksaKiriman(KRY, [{ koleksi: 'suratJalan', data: atribusi(KRY, UK, true), ada: true, lama: sjK }, { koleksi: 'piutangMutasi', data: atribusi(KRY, MK.data, false), ada: false, lama: null }], [], hak(KRY), KINI).tolak);
var BK = ajSusunBukti(sj2, 'foto', { jenis: 'image/jpeg', base64: '/9j/AAAA', lebar: 900, tinggi: 1200 }, W, 'kertas');
ok('H: bukti foto lembar: jenisBukti foto + isiBukti kertas (bentuk buktiSah tetap); tanda tangan layar = isiBukti layar', !!BK.data && BK.data.jenisBukti === 'foto' && BK.data.isiBukti === 'kertas' && BK.data.idSJ === String(sj2.id) && BT.data.isiBukti === 'layar'
  && ajSusunBukti(sj2, 'foto', { jenis: 'image/jpeg', base64: '/9j/AAAA' }, W).data.isiBukti === 'barang', J([BK, BT.data.isiBukti]));
var LB = ajLembarCetak(sj2, { nama: 'Toko Contoh', alamat: 'Jl. Contoh', telp: '0800' }); var L1 = ajTeksCetak(LB[0], 32), L2 = ajTeksCetak(LB[1], 32), L2b = ajTeksCetak(LB[1], 48);
ok('H: cetak 2 lembar: LEMBAR PEMBELI lalu LEMBAR TOKO (WAJIB ditandatangani, bawa pulang & foto); tiap baris ≤ 32 / 48 kolom', LB.length === 2 && /LEMBAR PEMBELI/.test(L1) && !/LEMBAR TOKO/.test(L1) && /LEMBAR TOKO/.test(L2)
  && /WAJIB ditandatangani/.test(L2) && /Bawa pulang ke toko/.test(L2) && /Diterima oleh/.test(L1) && /Diterima oleh/.test(L2) && (L1 + '\n' + L2).split('\n').every(function (l) { return l.length <= 32; })
  && L2b.split('\n').every(function (l) { return l.length <= 48; }), L1 + '\n=====\n' + L2);
ok('H: WhatsApp tetap satu teks tanpa nama lembar', !/LEMBAR/.test(TX));

// ---- I · yang mengantar BUKAN pegawai tetap (owner 18 Nov): "+ orang lain" = ketik nama; nama itu muncul lagi sebagai pilihan 60 hari (bagian TERAKHIR — cache surat jalan ditimpa)
ok('I: "orang lain" tanpa nama → ditolak dengan kalimat ketik', /Ketik nama yang mengantar/.test(ajAlasanTolak({ antar: { ongkir: '', pengantar: '', pengantarKetik: true } }) || ''));
var DSJ = ajDokumenSJ({ antar: { alamat: 'Jl. Contoh', ongkir: '', pengantar: '  Kurir Lepas Contoh  ', pengantarKetik: true, kendaraan: '', cod: true, catatan: '' }, pelanggan: 'Deka', keranjang: [] }, W, { noSJ: 'SJ26-TES-0777', trxId: 'tx-777', total: 50000, isi: [] });
ok('I: surat jalan menyimpan nama kurir lepas apa adanya (dirapikan), tanpa kolom bantu draf', !!DSJ && DSJ.pengantar === 'Kurir Lepas Contoh' && !('pengantarKetik' in DSJ), J(DSJ));
var RL = ajSusunTerima(Object.assign({}, sjK, { id: 'sjL', noSJ: 'SJ26-TES-0778', pengantar: 'Kurir Lepas Contoh' }), { cara: 'kertas', fotoId: 'F2', uang: '82000' }, W);
ok('I: uang bayar di tempat tercatat dibawa kurir lepas (dibawaOleh = namanya)', !RL.tolak && RL.dokumen[0].data.dibawaOleh === 'Kurir Lepas Contoh' && /dibawa Kurir Lepas Contoh/.test(RL.patch.kabar), RL.tolak || J(RL.dokumen[0].data));
pasok('suratJalan', [{ id: 'a', tanggal: '2026-11-17', jam: '09:00', pengantar: 'Kurir Lepas Contoh' }, { id: 'b', tanggal: '2026-11-10', jam: '09:00', pengantar: 'kurir lepas contoh ' },
  { id: 'c', tanggal: '2026-11-12', jam: '09:00', pengantar: 'Ben' }, { id: 'd', tanggal: '2026-10-01', jam: '09:00', pengantar: 'Teman Contoh' }, { id: 'e', tanggal: '2026-08-01', jam: '09:00', pengantar: 'Lama Contoh' }]);
var PP = ajPilihanPengantar('2026-11-18');
ok('I: pilihan = daftar Atur (Ben, …) + yang pernah mengantar 60 hari terakhir, terbaru dulu, tanpa kembar & tanpa yang sudah di daftar', PP.tetap.indexOf('Ben') >= 0 && J(PP.lain) === '["Kurir Lepas Contoh","Teman Contoh"]', J(PP));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

# Laporan per merek, tutup hari, kendali biaya — bundel Laporan (lingkup lain dengan bundel Jual)
SKENARIO_LP = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
var J = function (x) { return JSON.stringify(x); };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
setelSumber('cadangan', 'kotak pasir');
var KINI = new Date('2026-09-19T10:00:00+07:00');
var M0 = merekBulan('2026-09', KINI);
var jual = KOTAK.penjualan.slice(); var tambah = JSON.parse(J(BARIS_ONGKIR));
pasok('penjualan', jual.concat(tambah));
var M1 = merekBulan('2026-09', KINI);
var luarO = M1.luar && (M1.luar.rincian || []).find(function (g) { return g.id === 'ongkir'; });
var angsa0 = M0.merek.find(function (g) { return g.merek === 'Angsa'; }); var angsa1 = M1.merek.find(function (g) { return g.merek === 'Angsa'; });
ok('LP: baris luar "Ongkir antar" = 10.000 (margin penuh, HPP 0)', luarO && luarO.omzet === 10000 && luarO.margin === 10000 && luarO.nOngkir === 1, J(luarO));
ok('LP: Angsa bertambah persis barang barunya (700.000 / HPP 650.000), TANPA ongkir', angsa1 && angsa0 && angsa1.omzet - angsa0.omzet === 700000 && angsa1.margin - angsa0.margin === 50000, J([angsa0 && angsa0.omzet, angsa1 && angsa1.omzet]));
ok('LP: per merek tetap MENUTUP ke laba kotor Laporan (identitas: laba, baris nota, kg)', M1.menutup === true, J(M1.identitas));
pasok('aturanToko', [{ id: 'pelanggan', tarifOngkir: 10000 }]);
var K1 = kendaliBulan('2026-09', KINI); var ang = K1.baris.find(function (r) { return r.id === 'angkut'; });
ok('KB: Bensin & angkut menyebut ongkir antar yang ditagih (10.000, 1 nota)', ang && ang.ongkirMasuk === 10000 && ang.nAntar === 1 && /ongkir antar ditagih Rp10\.000/.test(ang.lampuTeks), ang && ang.lampuTeks);
var isoT = tanggalTutupAktif(KINI);   // sebelum jam 12 siang = menutup hari kemarin
pasok('suratJalan', [{ id: 'sj1', noSJ: 'SJ26-TES-0001', tanggal: isoT, jam: '09:00', trxIdJual: 'tx-ongkir', namaPelanggan: 'Contoh', pengantar: 'Ben', bayarDiTempat: true, tagihRp: 710000, status: 'diterima', isi: [] }]);
var H = hitungTutup({}, KINI); var rk = rekapTutup(H).find(function (r) { return /Bayar di tempat BELUM disetor/.test(r.a); });
ok('TH: tutup hari menyebut bayar di tempat yang belum disetor — merah, atas nama Ben', H.cod.length === 1 && /Ben Rp710\.000/.test(H.kalimatCod) && rk && rk.kelas === 'awas' && /Ben/.test(rk.a), J([H.kalimatCod, rk]));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""
BARIS_ONGKIR = [uji_laporan_baru.jual('p9101', '2026-09-19', '09:00', 'Kredit', 'Angsa', 50, 710000, 650000, ongkirAntar=10000, noSJ='SJ26-TES-0001', bayarDiTempat=True, namaPelanggan='Contoh', trxId='tx-ongkir')]

STATIS = [
    ('koleksi suratJalan terdaftar, kelas tetap (staf menandai tanpa cap jam server)', 'koleksi', ["{ nama: 'suratJalan',          urut: 'id',    cache: 'suratJalan', kelas: 'tetap' }"]),
    ('buktiTerima TIDAK didengar (bukan koleksi.js), dibaca & ditulis firebase.js', 'firebase', ["const KOLEKSI_BUKTI = 'buktiTerima';", 'export async function bacaBuktiTerima(idSJ)', 'export async function simpanBuktiTerima(daftar)']),
    ('app.js memberi Jual jalur bukti terima', 'app', ["bukti: { ada: () => sumberData().jenis === 'firestore', baca: (idSJ) => fb.bacaBuktiTerima(idSJ), simpan: (d) => fb.simpanBuktiTerima(d) }"]),
    ('Jual memasang panel Antar (Bayar, daftar, tanda terima, tanda tangan digambar ulang)', 'jual', ['const AP = buatPanelAntar(', 'Object.assign(aksi, AP.aksi); AP.pasang(akar);', '${AP.gambarBayar(s, t)}', '${AP.tombolDaftar()}', "return AP.gambarLembar(s, muncul, kepala, L1);", 'AP.sesudahGambar(akar);']),
    ('panel: tanda tangan wajib, foto boleh dilewati, kanvas tanpa gulir', 'panel', ['if (!AJ.ajTtdCukup(nTitik())) return', 'touch-action: none', 'data-aj-foto="1"', 'Foto (boleh dilewati)']),
    ('panel: tanda tangan di KERTAS bawaan, foto lembar wajib, dua pilihan cara, kartu & bukti menyebut kertas', 'panel', ["caraUang: 'Tunai', cara: 'kertas' }, ajTtdN",
     "if (kertas) { if (!foto) return set({ kabar: 'Foto dulu LEMBAR TOKO", 'data-aksi="ajCaraTerima"', "cara: kertas ? 'kertas' : 'layar', ttdId: rt ? rt.data.id : ''",
     "AJ.ajCaraTerima(x) === 'kertas' ? ' · tanda tangan di kertas (foto lembar)'", "d.isiBukti === 'kertas' ? 'foto lembar bertanda tangan'"]),
    ('panel: yang mengantar = daftar + pernah mengantar + "orang lain" (ketik nama)', 'panel', ['const P = AJ.ajPilihanPengantar(hari());', 'data-aksi="ajPengantarLain"', 'data-kolom="pengantar" data-k="aj-pengantar-ketik"',
     "!(k === 'pengantar' && s.antar.pengantarKetik)", "if (kolom === 'pengantar') o.pengantarKetik = false;", '${gambarPengantar(a, A)}']),
    ('panel: cetak surat jalan = 2 lembar berurutan di printer & dialog', 'panel', ['const lembar = AJ.ajLembarCetak(sj, atur.kop);', 'return lembar.reduce((p, g) => p.then(() => PR.susunCetak(g, { gaya: \'teks\' }))',
     "lembar.map((g) => AJ.ajTeksCetak(g, kertas === 58 ? 32 : 48)).join("]),
    ('modul baru di-modulepreload', 'index', ['<link rel="modulepreload" href="js/layar/antar-logika.js">', '<link rel="modulepreload" href="js/layar/antar-panel.js">']),
    ('Pelanggan › Atur: tarif ongkir, pengantar, kendaraan', 'pelanggan', ['data-kolom="tarifOngkir"', "daftar('pengantarAntar',", "daftar('kendaraanAntar',"]),
    ('Dasbor & tutup hari memerah untuk bayar di tempat belum disetor', 'dasbor', ['data-k="db-cod"']),
    ('tutup hari (tiga lebar layar) memajang pita merah bayar di tempat', 'uang', ['data-k="k5-cod"']),
    ('kisi peran: antar & terima antar', 'sistem', ["['antar', 'Bikin surat jalan & antar (bersama notanya)', 'Jual'], ['terimaAntar', 'Tandai barang antaran diterima / gagal', 'Jual']", "antar: 'sendiri', terimaAntar: 'sendiri', pesanan: 'sendiri' }", "antar: 'tidak', terimaAntar: 'sendiri', pesanan: 'tidak' } };"]),
    ('CI menjalankan uji ini', 'pages', ['python3 alat-uji/uji_antar.py && python3 alat-uji/uji_antar.py --kontrol']),
]


def kolom_sama(src):
    """Kolom tandai surat jalan: antar-logika AJ_KOLOM_TANDAI = akses.js KOLOM_TANDAI_SJ = rules v10 stafTandaiSJ (tanpa atribusi ubah); kolom terlarang surat jalan baru sama."""
    ambil = lambda t, n: re.findall(r"'(\w+)'", re.search(n + r" = \[(.*?)\];", t, re.S).group(1))
    aj, ak = ambil(src['antar'], 'AJ_KOLOM_TANDAI'), ambil(src['akses'], 'KOLOM_TANDAI_SJ')
    r = re.search(r"function stafTandaiSJ\(peranBoleh\) \{.*?affectedKeys\(\)\.hasOnly\(\[([^\]]*)\]\);", src['rules'], re.S)
    ru = [x for x in re.findall(r"'(\w+)'", r.group(1)) if not x.startswith('diubah')] if r else []
    bb = (ambil(src['antar'], 'AJ_KOLOM_BUKAN_BARU'), ambil(src['akses'], 'KOLOM_BUKAN_SJ_BARU'))
    rb = re.search(r"d\.get\('status', ''\) == 'berangkat'\n        && !d\.keys\(\)\.hasAny\(\[([^\]]*)\]\)", src['rules'])
    rbb = re.findall(r"'(\w+)'", rb.group(1)) if rb else []
    return aj == ak == ru and bb[0] == bb[1] == rbb, {'antar': aj, 'akses': ak, 'rules': ru, 'baru': [bb[0], bb[1], rbb]}


RUSAK = [
    ('ongkir tidak masuk tagihan', JL, "  const ongkir = s.antar && !s.tukar ? ajOngkir(s.antar) : 0;\n", "  const ongkir = 0;\n"),
    ('ongkir dipotong potongan nota (ditambah sebelum potongan)', JL, "  const bersih = subtotal - potongan - kredit + ongkir;", "  const bersih = subtotal + ongkir - Math.min(potongan + ongkir, subtotal + ongkir) + Math.min(ongkir, 0) - kredit;"),
    ('ongkir tidak menempel di baris nota', JL, "  if (ongkir > 0) { const ip = ajBarisPembawa(items); if (ip >= 0) { items[ip].ongkirAntar = ongkir; items[ip].hargaTotal += ongkir; } }", ""),
    ('surat jalan tidak lahir bersama nota', JL, "    dokumen.push({ koleksi: 'suratJalan', data: suratJalan });", ""),
    ('bayar di tempat tetap kena batas kredit', JL, "  if (s.cara === 'Kredit' && !(s.antar && s.antar.cod)) { const nb = bonKeranjang(s, t); const k = nb > 0 ? alasanKunciKredit(s, nb) : null; if (k) return k; }", "  if (s.cara === 'Kredit') { const k = alasanKunciKredit(s, t.total); if (k) return k; }"),
    ('baris nota tanpa nomor surat jalan', JL, "    if (noSJ) { d.noSJ = noSJ; if (antar.cod) d.bayarDiTempat = true; }", ""),
    ('pembatalan nota tidak membatalkan surat jalan', JL, "  ajBatalUntukNota(notaTerakhir.trxId, { kini }).forEach((x) => dokumen.push(x));", ""),
    ('nomor surat jalan dipakai ulang', AJ, "aw + ('0000' + (maks + 1))", "aw + ('0000' + 1)"),
    ('kisi "bikin surat jalan" tidak ditegakkan', AK, "  if (ada('suratJalan')) t.antar = 1;\n", ""),
    ('tanda terima tanpa tanda tangan diterima', AJ, "  if (!kertas && ajKosong(x.ttdId)) return { tolak: 'Minta tanda tangan penerima dulu (kotak tanda tangan)' };\n", ""),
    ('tanda tangan kertas tanpa foto lembar diterima', AJ, "  if (kertas && ajKosong(x.fotoId)) return", "  if (false) return"),
    ('cara kertas tetap menulis id tanda tangan layar', AJ, "buktiTtd: kertas ? [] : [String(x.ttdId)]", "buktiTtd: [String(x.ttdId)]"),
    ('riwayat tidak mencatat cara tanda terima', AJ, "ajRiwayat(sj, 'diterima', w, { bukti: kertas ? 'kertas' : 'layar' })", "ajRiwayat(sj, 'diterima', w)"),
    ('pilihan pengantar melupakan kurir lepas', AJ, "if (!kenal[k] && lain.length < 6) { kenal[k] = 1; lain.push(n); }", "if (false) { kenal[k] = 1; lain.push(n); }"),
    ('pilihan pengantar tidak membatasi 60 hari', AJ, "String(x.tanggal || '') >= batas)", "String(x.tanggal || '') >= '')"),
    ('cetak surat jalan cuma satu lembar', AJ, "  return [ajGarisCetak(sj, kop, 'pembeli'), ajGarisCetak(sj, kop, 'toko')];", "  return [ajGarisCetak(sj, kop, 'toko')];"),
    ('lembar toko tanpa perintah bawa pulang', AJ, "b('Bawa pulang ke toko, lalu foto');", ""),
    ('uang di tempat tanpa alamat surat jalan', AJ, "      untukSJ: String(sj.noSJ), catatan: 'Bayar di tempat — surat jalan ' + sj.noSJ };", "      catatan: 'Bayar di tempat — surat jalan ' + sj.noSJ };"),
    ('uang di tempat melebihi tagihan diterima', AJ, "    if (n > K.sisaTagih) return { tolak: 'Uang yang diterima '", "    if (false) return { tolak: 'Uang yang diterima '"),
    ('retur mengembalikan ongkir', RT, "  if (caraBayarKunci(t) !== 'kredit') return ajDasarRetur(t, rtDasarNota);", "  if (caraBayarKunci(t) !== 'kredit') return rtDasarNota(t);"),
    ('struk tanpa baris ongkir', STK, "    if (ongkir > 0) baris('Ongkir antar', '+' + RP(ongkir), { jenis: 'ringkas' });", ""),
    # BUAT_STAF suratJalan ['ben'] & SERVER_BUKA antar ['ben'] = dua pagar yang sama-sama menolak karyawan (merusak satu saja tetap ditolak yang lain);
    # kesamaan BUAT_STAF dengan rules v10 dijaga periksa_rules.py (BUAT_STAF ↔ allow create), kisi dijaga kontrol di atas.
    ('penjaga menerima surat jalan baru berisi penerimaan', AK, " || KOLOM_BUKAN_SJ_BARU.some((k) => k in d))) return { tolak: tolakTindakan('antar') };", ")) return { tolak: tolakTindakan('antar') };"),
    ('penjaga menerima tandai ulang / batal oleh pengantar', AK, "(String(lama.status || '') !== 'berangkat' || ['diterima', 'gagal'].indexOf(String(d.status || '')) < 0)", "(false)"),
    ('Atur tidak menyimpan tarif ongkir', PL, "      tarifOngkir: ab.tarifOngkir, pengantarAntar: ab.pengantarAntar, kendaraanAntar: ab.kendaraanAntar, hariIngatRutin", "      hariIngatRutin"),
]
RUSAK_LP = [
    ('Laporan per merek tidak memisahkan ongkir', LP, "    if (ong) { const o = luar.ongkir; o.nOngkir += 1;", "    if (false) { const o = luar.ongkir; o.nOngkir += 1;"),
    ('ongkir dihitung sebagai baris nota (identitas tidak menutup)', LP, "o.nOngkir += 1;", "o.nOngkir += 1; o.nBaris += 1;"),
    ('tutup hari diam soal bayar di tempat', TH, "    H.cod && H.cod.length ? [['Bayar di tempat BELUM disetor", "    false ? [['Bayar di tempat BELUM disetor"),
]
RUSAK_STATIS = [
    ('Jual tidak menggambar ulang tanda tangan', 'jual', 'AP.sesudahGambar(akar);', ''),
    ('panel menerima tanda terima tanpa tanda tangan', 'panel', 'if (!AJ.ajTtdCukup(nTitik())) return', 'if (false) return'),
    ('panel menerima tanda tangan kertas tanpa foto lembar', 'panel', "if (kertas) { if (!foto) return set(", "if (kertas) { if (false) return set("),
    ('layar Terima bawaan tanda tangan di layar', 'panel', "caraUang: 'Tunai', cara: 'kertas' }, ajTtdN", "caraUang: 'Tunai', cara: 'layar' }, ajTtdN"),
    ('nama orang lain tidak bisa diketik', 'panel', "!(k === 'pengantar' && s.antar.pengantarKetik)", "false"),
    ('printer tablet cuma mencetak satu lembar', 'panel', 'const lembar = AJ.ajLembarCetak(sj, atur.kop);', 'const lembar = [AJ.ajGarisCetak(sj, atur.kop)];'),
    ('akses.js berbeda kolom tandai dengan rules', 'akses', "'uangDiterima', 'caraUang', 'pelunasanId', 'alasanGagal', 'ditandaiOleh'];", "'uangDiterima', 'caraUang', 'pelunasanId', 'alasanGagal', 'ditandaiOleh', 'tagihRp'];"),
]


def jalan_satu(daftar, teks, skenario, prelude_tambah=''):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in daftar)
    return js, skenario


def jalan(teks):
    hasil = []
    for daftar, kotak, jam, skenario in ((MODUL, uji_jual_baru.KOTAK, "var __KINI = new Date('2026-11-18T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n", SKENARIO),
                                         (MODUL_LP, uji_laporan_baru.KOTAK, uji_laporan_baru.JAM_TETAP, 'var BARIS_ONGKIR = ' + json.dumps(BARIS_ONGKIR) + ';\n' + SKENARIO_LP)):
        js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in daftar)
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(jam + js + '\nvar KOTAK = ' + json.dumps(kotak) + ';\n' + skenario); p = f.name
        r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
        out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
        if r.returncode != 0 or not out.startswith('{'): hasil.append((0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]])); continue
        h = json.loads(out); hasil.append((h['lulus'], h['gagal']))
    return sum(x[0] for x in hasil), [g for x in hasil for g in x[1]]


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    sama, rinci = kolom_sama(src)
    if not sama: g.append('kolom surat jalan antar-logika / akses.js / rules v10 berbeda → ' + json.dumps(rinci, ensure_ascii=False)[:400])
    return len(STATIS) + 1 - len(g), g


def muat():
    semua = list(dict.fromkeys(MODUL + MODUL_LP))
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in semua), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK + RUSAK_LP:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama + ' (' + str(teks[berkas].count(a)) + '×)'); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b)
            l, g = jalan(T)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_STATIS:
            if src[berkas].count(a) < 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            S = dict(src); S[berkas] = S[berkas].replace(a, b); l, g = statis(S)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = jalan(teks); ls, gs = statis(src)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    sys.exit(1 if g or gs else 0)
