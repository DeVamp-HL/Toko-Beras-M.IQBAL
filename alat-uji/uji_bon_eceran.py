#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_bon_eceran.py — BON PELANGGAN ECERAN (owner 26 Nov 2026, sensus ulang 26 Nov bagian 1c: A101 · A105 · B29 · B30 · B31 — "paket saran"). KOTAK PASIR (nama &
angka CONTOH, bukan angka toko), jsc saja, TANPA peramban. Jam dikunci Sabtu 28 Nov 2026 10:00 WIB.
  PN piutang per NOTA: sisa tiap orang dibagi ke nota terbukanya (pembagian buku bon: bayar menutup bon tertua dulu); jatuh tempo = faktur → jatuh tempo faktur,
     selain itu tanggal nota + tempo kartu, kosong = "waktunya ditagih"; saldo awal = satu nota; kelompok lewat · hari ini · 7 hari ke depan · belum · tanpa tanggal
     MENUTUP ke total bon mesin (penjaga berbunyi bila tidak); lewat dibagi umur keterlambatan (batas kelompok umur owner).
  HT hari tagih tetap: bawaan Sabtu, -1 = mati; hari itu = "tagih hari ini" (nota jatuh tempo sampai hari itu + janji); hari lain = hari tagih berikutnya.
  SY syarat bon baru: langganan ≥ N bulan DAN ≥ N nota dalam N hari (setelan owner, 0 = mati); batas kredit owner di kartu = lolos; lintas tutup buku lewat
     ringkasan tahun yang diarsip; KR1 menahan dengan kalimat syaratnya (pintu izin owner yang sama).
  AT setelan Pelanggan › Atur menyimpan hari tagih & syarat (batas sah); PG pengingat hari tagih + lokal.uang (setor & cocok rekening) diteruskan, jenis lain dibuang.

    python3 alat-uji/uji_bon_eceran.py            → N lulus · 0 gagal
    python3 alat-uji/uji_bon_eceran.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_faktur  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
BN = 'baru/js/layar/bon-logika.js'; FK = 'baru/js/layar/faktur-logika.js'; PL = 'baru/js/layar/pelanggan-logika.js'; SL = 'baru/js/layar/sistem-logika.js'; JL = 'baru/js/layar/jual-logika.js'
MODUL = bundel_baru.lengkapi(uji_faktur.MODUL)
SUMBER = {'pelanggan': 'baru/js/layar/pelanggan.js', 'dasbor': 'baru/js/layar/dasbor.js', 'dasborL': 'baru/js/layar/dasbor-logika.js', 'jual': JL, 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'rules': 'firestore.rules'}
JAM = "var __KINI = new Date('2026-11-28T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"

def jual(i, tgl, cara, nama, trx, n, **x):
    d = {'id': i, 'tanggal': tgl, 'jam': '09:00', 'caraBayar': cara, 'namaPelanggan': nama, 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 10, 'hargaTotal': n, 'hppTotalSaatJual': round(n * 0.9), 'trxId': trx}
    d.update(x); return d

KOTAK = {
  'penjualan': [
    jual(101, '2026-09-01', 'Tunai', 'Bu Sari', 'a0', 100000),
    jual(102, '2026-10-20', 'Kredit', 'Bu Sari', 'a1', 200000), jual(103, '2026-10-20', 'Kredit', 'Bu Sari', 'a1', 100000),
    jual(104, '2026-11-10', 'Kredit', 'Bu Sari', 'a2', 200000), jual(105, '2026-11-20', 'Kredit', 'Bu Sari', 'a3', 150000),
    jual(106, '2026-09-10', 'Tunai', 'Pak Budi', 'b0', 90000), jual(107, '2026-10-10', 'Tunai', 'Pak Budi', 'b9', 90000), jual(108, '2026-11-25', 'Kredit', 'Pak Budi', 'b1', 80000),
    jual(109, '2026-11-27', 'Kredit', 'Warung Contoh', 'f1', 500000, noFaktur='F26-TES-0001', jatuhTempo='2026-12-27', tempoHari=30),
    jual(110, '2026-08-15', 'Tunai', 'Warung Contoh', 'f0', 500000), jual(111, '2026-10-15', 'Tunai', 'Warung Contoh', 'f9', 500000),
    jual(112, '2026-11-20', 'Tunai', 'Baru Datang', 'c1', 100000),
    jual(113, '2026-11-01', 'Kredit', 'Lebih', 'l1', 50000),
  ],
  'piutangMutasi': [
    {'id': 201, 'tanggal': '2026-11-12', 'jam': '10:00', 'tipe': 'bayar', 'namaPelanggan': 'Bu Sari', 'nominal': 350000, 'caraBayar': 'Tunai'},
    {'id': 202, 'tanggal': '2026-08-20', 'jam': '00:00', 'tipe': 'saldoAwal', 'namaPelanggan': 'Deka', 'nominal': 200000},
    {'id': 203, 'tanggal': '2026-11-02', 'jam': '10:00', 'tipe': 'bayar', 'namaPelanggan': 'Lebih', 'nominal': 60000, 'caraBayar': 'Tunai'},
  ],
  'pelangganCatatan': [{'id': 'bu sari', 'nama': 'Bu Sari', 'catatan': 'warung gang masjid'}, {'id': 'pak budi', 'nama': 'Pak Budi', 'catatan': 'tukang', 'tempoHari': 3},
                       {'id': 'baru datang', 'nama': 'Baru Datang', 'catatan': 'baru pindah'}, {'id': 'warung contoh', 'nama': 'Warung Contoh', 'catatan': 'usaha'}],
  'tagihPelanggan': [{'id': 't1', 'kunci': 'warung contoh', 'tanggal': '2026-11-26', 'jam': '10:00', 'janji': '2026-11-28'}],
  'aturanToko': [],
}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); };
var KINI = new Date('2026-11-28T10:00:00+07:00'); var nId = 900000;
var W = { tanggal: '2026-11-28', jam: '10:00', kini: '2026-11-28T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
var K0 = JSON.parse(J(KOTAK)); Object.keys(K0).forEach(function (n) { pasok(n, K0[n]); }); setelSumber('cadangan', 'kotak pasir');
var atur = function (extra) { pasok('aturanToko', [].concat(extra || [])); };
var nt = function (R, k) { return R.nota.find(function (x) { return x.kunci === k; }); };

// ==================== PN · PIUTANG PER NOTA ====================
ok('PN: tempo nota bon: kartu (Pak Budi 3 hari) · kosong = "waktunya ditagih" 14 hari', pnTempo('Pak Budi').hari === 3 && pnTempo('Pak Budi').sumber === 'kartu' && pnTempo('Bu Sari').hari === 14 && pnTempo('Bu Sari').sumber === 'tagih', J([pnTempo('Pak Budi'), pnTempo('Bu Sari')]));
var R = pnRingkas(KINI);
ok('PN: Bu Sari bayar 350.000 menutup nota 20 Okt (300.000) + 50.000 nota 10 Nov → sisa per nota 150.000 & 150.000 (= sisa mesin 300.000)', !nt(R, 'n:a1') && nt(R, 'n:a2').sisa === 150000 && nt(R, 'n:a3').sisa === 150000 && nt(R, 'n:a2').nominal === 200000, J(R.nota));
ok('PN: nota 10 Nov + 14 hari = 24 Nov → LEWAT 4 hari; nota 20 Nov → 4 Des = 7 hari ke depan (6 hari lagi)', nt(R, 'n:a2').jatuhTempo === '2026-11-24' && nt(R, 'n:a2').status === 'lewat' && nt(R, 'n:a2').hariLewat === 4 && nt(R, 'n:a3').jatuhTempo === '2026-12-04' && nt(R, 'n:a3').status === 'minggu' && nt(R, 'n:a3').hariLagi === 6, J([nt(R, 'n:a2'), nt(R, 'n:a3')]));
ok('PN: Pak Budi tempo kartu 3 hari: nota 25 Nov jatuh tempo HARI INI', nt(R, 'n:b1').jatuhTempo === '2026-11-28' && nt(R, 'n:b1').status === 'hariIni' && nt(R, 'n:b1').sumberTempo === 'kartu', J(nt(R, 'n:b1')));
ok('PN: faktur memakai jatuh tempo FAKTURNYA (27 Des), bukan tanggal + tempo', nt(R, 'n:f1').jatuhTempo === '2026-12-27' && nt(R, 'n:f1').status === 'nanti' && nt(R, 'n:f1').faktur === 'F26-TES-0001' && nt(R, 'n:f1').sumberTempo === 'faktur', J(nt(R, 'n:f1')));
ok('PN: saldo awal Deka 20 Agu = satu "nota" → lewat 86 hari', nt(R, 'sa:202').saldoAwal && nt(R, 'sa:202').status === 'lewat' && nt(R, 'sa:202').hariLewat === 86, J(nt(R, 'sa:202')));
ok('PN: kelebihan bayar (sisa minus) tidak ikut', !R.nota.some(function (x) { return x.nama === 'Lebih'; }));
var g = function (id) { return R.kelompok.find(function (k) { return k.id === id; }); };
ok('PN: kelompok lewat 350.000 (2 nota, 2 orang) · hari ini 80.000 · 7 hari ke depan 150.000 · belum 500.000 · tanpa tanggal 0', g('lewat').rp === 350000 && g('lewat').n === 2 && g('lewat').orang === 2 && g('hariIni').rp === 80000 && g('minggu').rp === 150000 && g('nanti').rp === 500000 && g('tanpa').rp === 0, J(R.kelompok.map(function (k) { return k.id + ':' + k.rp; })));
var totalMesin = hitungPiutang().filter(function (d) { return d.sisa > 0; }).reduce(function (a, d) { return a + d.sisa; }, 0);
ok('PN: Σ kelompok = total bon mesin (1.080.000) — MENUTUP', R.menutup && R.jumlah === 1080000 && R.total === totalMesin && totalMesin === 1080000, J([R.jumlah, R.total, totalMesin, R.tidakMenutup]));
ok('PN: lewat dibagi umur keterlambatan (batas owner 7/30/90): ≤ 7 hari 150.000 · 31–90 hari 200.000', R.umurLewat[0].rp === 150000 && R.umurLewat[2].rp === 200000 && R.umurLewat[1].rp === 0, J(R.umurLewat));
ok('PN: status orang dan nota tidak saling membantah — Bu Sari "waktunya ditagih" & punya nota lewat', (function () { var b = semuaBon(KINI).find(function (x) { return x.kunci === 'bu sari'; }); return b.status === 'perluTagih' && R.nota.some(function (x) { return x.orang === 'bu sari' && x.status === 'lewat'; }); })());
ok('PN: penjaga BERBUNYI bila nota satu orang tidak menutup ke sisanya (selisih & namanya disebut)', (function () { var Bs = semuaBon(KINI).map(function (b) { return b.kunci === 'bu sari' ? Object.assign({}, b, { buka: b.buka.slice(1) }) : b; }); var X = pnRingkas(KINI, Bs);
  return !X.menutup && X.tidakMenutup.length === 1 && X.tidakMenutup[0].nama === 'Bu Sari' && X.tidakMenutup[0].selisih === 150000 && X.selisih === 150000; })());
ok('PN: tempo "waktunya ditagih" diubah owner (21 hari) → jatuh tempo ikut', (function () { atur([{ id: 'pelanggan', tagihHari: 21 }]); var x = nt(pnNota(KINI), 'n:a2'); atur(); return x.jatuhTempo === '2026-12-01' && x.status === 'minggu'; })());
ok('PN: pnStatus: kemarin = lewat · hari ini · +6 = minggu · +7 = belum · tanpa tanggal', pnStatus('2026-11-27', '2026-11-28') === 'lewat' && pnStatus('2026-11-28', '2026-11-28') === 'hariIni' && pnStatus('2026-12-04', '2026-11-28') === 'minggu' && pnStatus('2026-12-05', '2026-11-28') === 'nanti' && pnStatus('', '2026-11-28') === 'tanpa');

// ==================== HT · HARI TAGIH ====================
var T = pnHariTagih(KINI);
ok('HT: bawaan Sabtu; 28 Nov = Sabtu → TAGIH HARI INI', T.nyala && T.hari === 5 && T.nama === 'Sabtu' && T.hariIni && T.berikut === '2026-11-28', J(T));
ok('HT: tagih hari ini = nota jatuh tempo sampai hari ini (Bu Sari 150.000, Deka 200.000, Pak Budi 80.000) + janji jatuh hari ini (Warung Contoh, tanpa nota jatuh tempo)', T.daftar.length === 4 && T.rp === 430000
  && T.daftar.find(function (o) { return o.kunci === 'bu sari'; }).rp === 150000 && T.daftar.find(function (o) { return o.kunci === 'warung contoh'; }).janji === '2026-11-28' && T.daftar.find(function (o) { return o.kunci === 'warung contoh'; }).rp === 0 && /Hari ini hari tagih/.test(T.teks), J(T.daftar));
atur([{ id: 'pelanggan', hariTagih: 0 }]); var T2 = pnHariTagih(KINI);
ok('HT: hari tagih Senin → berikutnya 30 Nov (2 hari lagi): nota 4 Des belum ikut, janji 28 Nov ikut', T2.nyala && !T2.hariIni && T2.berikut === '2026-11-30' && T2.lagi === 2 && T2.daftar.length === 4 && !T2.daftar.some(function (o) { return o.tertua === '2026-12-04'; }) && T2.rp === 430000 && /Hari tagih berikutnya Senin/.test(T2.teks), J(T2));
atur([{ id: 'pelanggan', hariTagih: -1 }]); ok('HT: -1 = mati', !pnHariTagih(KINI).nyala && /mati/.test(pnHariTagih(KINI).teks)); atur();
ok('HT: Jumat (4) dari Sabtu = 6 hari lagi (tidak minus)', (function () { atur([{ id: 'pelanggan', hariTagih: 4 }]); var x = pnHariTagih(KINI); atur(); return x.berikut === '2026-12-04' && x.lagi === 6; })());

// ==================== SY · SYARAT BON ====================
var SA = fkSyaratAtur(); ok('SY: bawaan langganan ≥ 1 bulan & ≥ 2 nota dalam 90 hari', SA.syaratBulan === 1 && SA.syaratNota === 2 && SA.syaratHari === 90, J(SA));
ok('SY: Bu Sari (sejak 1 Sep, 4 nota) LOLOS', fkSyaratBon('Bu Sari', '2026-11-28') === null);
var Y = fkSyaratBon('Baru Datang', '2026-11-28');
ok('SY: Baru Datang (pertama 20 Nov, 1 nota) TIDAK lolos — dua sebab disebut', Y && Y.kurang.length === 2 && /langganan sejak 20 Nov/.test(Y.kurang[0]) && /baru 1 nota dalam 90 hari \(syarat ≥ 2\)/.test(Y.kurang[1]) && Y.pertama === '2026-11-20' && Y.nNota === 1, J(Y));
ok('SY: saldo awal bon dari sebelum sistem = sudah langganan (Deka, tanpa belanja): kurang NOTA saja', (function () { var x = fkSyaratBon('Deka', '2026-11-28'); return x && x.pertama === '2026-08-20' && x.kurang.length === 1 && /baru 0 nota/.test(x.kurang[0]); })(), J(fkSyaratBon('Deka', '2026-11-28')));
ok('SY: mundur bulan kalender (31 Mar − 1 = 28 Feb; Jan − 1 = Des tahun lalu)', fkMundurBulan('2026-03-31', 1) === '2026-02-28' && fkMundurBulan('2027-01-15', 1) === '2026-12-15' && fkMundurBulan('2026-11-28', 1) === '2026-10-28');
ok('SY: tepat 1 bulan (pertama 28 Okt pada 28 Nov) lolos syarat bulan', (function () { var x = fkSyaratBon('Pak Budi', '2026-11-28'); return x === null; })());
var KR = kunciKr1('Baru Datang', 50000);
ok('SY: KR1 menahan bon baru dengan kalimat syaratnya (pintu izin owner sama dengan batas kredit)', /^Syarat bon: Baru Datang/.test(String(KR)) && /minta izin owner/.test(String(KR)), KR);
pasok('pelangganCatatan', JSON.parse(J(KOTAK.pelangganCatatan)).map(function (c) { return c.id === 'baru datang' ? Object.assign({}, c, { batasKredit: 1000000 }) : c; }));
ok('SY: batas kredit yang diisi owner di kartu = LOLOS syarat', kunciKr1('Baru Datang', 50000) === null, kunciKr1('Baru Datang', 50000));
pasok('pelangganCatatan', JSON.parse(J(KOTAK.pelangganCatatan)));
atur([{ id: 'pelanggan', syaratBulan: 0, syaratNota: 0 }]); ok('SY: 0 & 0 = syarat mati', fkSyaratBon('Baru Datang', '2026-11-28') === null && fkSyaratAtur().dariOwner);
atur([{ id: 'pelanggan', syaratBulan: 0, syaratNota: 1 }]); ok('SY: syarat nota saja (1) → Baru Datang lolos', fkSyaratBon('Baru Datang', '2026-11-28') === null);
atur([{ id: 'pelanggan', syaratBulan: 0, syaratNota: 3, syaratHari: 30 }]); ok('SY: jendela 30 hari: Bu Sari cuma 2 nota (10 & 20 Nov) → kurang', (function () { var x = fkSyaratBon('Bu Sari', '2026-11-28'); return x && x.nNota === 2 && /dalam 30 hari \(syarat ≥ 3\)/.test(x.kurang[0]); })());
atur([{ id: 'pelanggan', syaratBulan: 99, syaratNota: -1, syaratHari: 3 }]); ok('SY: angka di luar batas diabaikan → bawaan', J(fkSyaratAtur()) === J({ syaratBulan: 1, syaratNota: 2, syaratHari: 90, dariOwner: true }), J(fkSyaratAtur())); atur();
// lintas tutup buku: belanja tahun lalu dibaca dari ringkasan tahun yang diarsip
pasok('batchMasuk', [{ id: 'tb2026', tanggal: '2026-12-31', tutupBuku: true, penandaBuku: true, tahunDari: 2026, merkList: [], pemasok: 'TUTUP BUKU 2026',
  ringkasTahun: { tahun: 2026, cutoff: '2026-12-31', pelanggan: { 'baru datang': { nama: 'Baru Datang', hari: { '2026-09-05': 1, '2026-11-20': 1 } } }, kredit: { dari: '2026-10-03', hari: { 'baru datang': { '2026-12-10': 50000 } } } } }]);
pasok('penjualan', [jual(301, '2027-01-05', 'Tunai', 'Baru Datang', 'j1', 100000)]);
ok('SY: sesudah tutup buku: langganan sejak 5 Sep (ringkasan) + 1 nota Januari + 1 hari belanja Desember (ringkasan) = LOLOS', fkSyaratBon('Baru Datang', '2027-01-08') === null, J(fkSyaratBon('Baru Datang', '2027-01-08')));
pasok('batchMasuk', []); ok('SY: tanpa ringkasan tahun lalu → tidak lolos (dua sebab)', (function () { var x = fkSyaratBon('Baru Datang', '2027-01-08'); return x && x.kurang.length === 2; })());
pasok('penjualan', JSON.parse(J(KOTAK.penjualan)));

// ==================== AT · SETELAN ====================
var AS = susunAturPelanggan({ hariTagih: '0', syaratBulan: '2', syaratNota: '3', syaratHari: '60' }, W); var da = AS.dokumen && AS.dokumen[0].data;
ok('AT: simpan Atur menyimpan hari tagih & syarat; kabar menyebutnya', da && da.hariTagih === 0 && da.syaratBulan === 2 && da.syaratNota === 3 && da.syaratHari === 60 && /hari tagih Senin/.test(AS.patch.kabar) && /≥ 2 bulan langganan & ≥ 3 nota\/60 hari/.test(AS.patch.kabar), J(AS));
ok('AT: hari tagih 7 / syarat hari 5 / syarat bulan 40 DITOLAK', !!susunAturPelanggan({ hariTagih: '7' }, W).tolak && !!susunAturPelanggan({ syaratHari: '5' }, W).tolak && !!susunAturPelanggan({ syaratBulan: '40' }, W).tolak);
ok('AT: -1 (mati) & 0 (syarat mati) sah', (function () { var d = susunAturPelanggan({ hariTagih: '-1', syaratBulan: '0', syaratNota: '0' }, W).dokumen[0].data; return d.hariTagih === -1 && d.syaratBulan === 0 && d.syaratNota === 0 && d.syaratHari === 90; })());
terapkanKeCache(AS.dokumen); ok('AT: tersimpan → terbaca aturPelanggan (hari tagih) & fkSyaratAtur', aturPelanggan().hariTagih === 0 && fkSyaratAtur().syaratNota === 3 && aturPelanggan().syaratHari === 60); atur();
ok('AT: simpan Atur tanpa isian baru TIDAK menghapus hari tagih & syarat yang tersimpan', (function () { atur([{ id: 'pelanggan', hariTagih: 2, syaratNota: 4 }]); var d = susunAturPelanggan({}, W).dokumen[0].data; atur(); return d.hariTagih === 2 && d.syaratNota === 4 && d.syaratBulan === 1; })());

// ==================== PG · PENGINGAT ====================
var S = ssSumberPengingat(KINI, {});
ok('PG: hari tagih jadi satu pengingat (jatuh hari ini, 4 orang, 430.000)', S.some(function (p) { return p.id === 'tagih|2026-11-28' && p.jenis === 'tagih' && p.n === 430000 && /4 orang/.test(p.teks); }), J(S.filter(function (p) { return p.jenis === 'tagih'; })));
var S2 = ssSumberPengingat(KINI, { uang: [{ id: 'setor|2026-11-28', jenis: 'setor', kunci: 'brankas', teks: 'Setor', jatuh: '2026-11-28', n: 1 }, { id: 'rekening|2026-10', jenis: 'rekening', jatuh: '2026-10-31' }, { id: 'x', jenis: 'palsu', jatuh: '2026-11-28' }, { id: 'y', jenis: 'setor', jatuh: 'kemarin' }] });
ok('PG: lokal.uang diteruskan (setor & rekening), jenis lain / tanggal rusak DIBUANG', S2.some(function (p) { return p.id === 'setor|2026-11-28'; }) && S2.some(function (p) { return p.id === 'rekening|2026-10'; }) && !S2.some(function (p) { return p.id === 'x' || p.id === 'y'; }));
ok('PG: jenis baru ada di daftar jenis & aturan bawaan (nyala, ke, hari sebelum)', ['setor', 'rekening', 'tagih'].every(function (j) { return SS_JENIS_PENGINGAT.some(function (x) { return x.id === j; }) && ssAtur('pengingat').nyala[j] === true && ssAtur('pengingat').ke[j].length; }) && J(ssAtur('pengingat').ke.tagih) === J(['Owner', 'Ben']));
ok('PG: hari sebelum pengingat baru diatur owner (batas sah)', !!susunAturSistem('pengingat', { hariTagih: 9 }, W).tolak && !susunAturSistem('pengingat', { hariTagih: 1 }, W).tolak);
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
var galat = []; var CAD = __CAD__;
try { Object.keys(CAD).forEach(function (k) { if (Array.isArray(CAD[k])) pasok(k, CAD[k]); }); setelSumber('cadangan', 'asap'); } catch (e) { galat.push('muat: ' + e.message); }
var akhir = (function () { var t = ''; (CAD.penjualan || []).forEach(function (p) { if ((p.tanggal || '') > t) t = p.tanggal; }); return t; })(); var KINI = new Date(akhir + 'T20:00:00+07:00');
var out = { akhir: akhir };
try { var R = pnRingkas(KINI); out.menutup = R.menutup; out.selisih = R.selisih; out.nNota = R.nota.length; out.nTidak = R.tidakMenutup.length; out.kelompok = R.kelompok.map(function (k) { return k.id + ':' + k.n; }).join(' '); } catch (e) { galat.push('per nota: ' + e.message); }
try { var T = pnHariTagih(KINI); out.tagih = T.nyala ? T.daftar.length : 'mati'; } catch (e) { galat.push('hari tagih: ' + e.message); }
try { var lolos = 0, tidak = 0; semuaBon(KINI).filter(function (b) { return b.sisa > 0; }).forEach(function (b) { if (fkSyaratBon(b.nama, akhir)) tidak++; else lolos++; }); out.syarat = { lolos: lolos, tidak: tidak }; } catch (e) { galat.push('syarat: ' + e.message); }
try { ssSumberPengingat(KINI, {}); } catch (e) { galat.push('pengingat: ' + e.message); }
print(JSON.stringify({ galat: galat, out: out }));
"""

RUSAK = [
    ('tempo: kartu pelanggan diabaikan', BN, "return n === null ? { hari: aturPelanggan().tagihHari, sumber: 'tagih' } : { hari: n, sumber: 'kartu' };", "return { hari: aturPelanggan().tagihHari, sumber: 'tagih' };"),
    ('status: jatuh tempo hari ini dihitung lewat', BN, "jt < iso ? 'lewat' : jt === iso ? 'hariIni'", "jt <= iso ? 'lewat' : jt === iso ? 'hariIni'"),
    ('status: 7 hari ke depan jadi 8 hari', BN, "hariKe(jt) - hariKe(iso) <= 6 ? 'minggu' : 'nanti'", "hariKe(jt) - hariKe(iso) <= 7 ? 'minggu' : 'nanti'"),
    ('per nota: faktur memakai tanggal + tempo', BN, "if (f) x.jatuhTempo = String(f.jatuhTempo || ''); else if", "if (false) x.jatuhTempo = String(f.jatuhTempo || ''); else if"),
    ('per nota: sisa memakai nilai nota (tidak menutup)', BN, "x.sisa += Number(r.sisa) || 0; x.nominal += Number(r.nominal) || 0; jml += Number(r.sisa) || 0;", "x.sisa += Number(r.nominal) || 0; x.nominal += Number(r.nominal) || 0; jml += Number(r.sisa) || 0;"),
    ('per nota: penjaga menutup diam', BN, "menutup: !N.tidakMenutup.length && Math.abs(jumlah - N.total) < 0.5,", "menutup: true,"),
    ('per nota: umur lewat dari tanggal nota, bukan keterlambatan', BN, "x.status === 'lewat' && x.hariLewat >= Math.max(1, e.dari) && x.hariLewat <= e.sampai", "x.status === 'lewat' && hariKe(N.iso) - hariKe(x.tanggal) >= Math.max(1, e.dari) && hariKe(N.iso) - hariKe(x.tanggal) <= e.sampai"),
    ('hari tagih: janji diabaikan', BN, "  B.forEach((b) => { if (!(b.sisa > 0) || !b.tagih || !b.tagih.janji", "  [].forEach((b) => { if (!(b.sisa > 0) || !b.tagih || !b.tagih.janji"),
    ('hari tagih: hari berikutnya bisa mundur', BN, "const geser = (h - hariMingguKe(iso) + 7) % 7;", "const geser = Math.abs(h - hariMingguKe(iso));"),
    ('hari tagih: bawaan mati', PL, "  hariTagih: 5,", "  hariTagih: -1,"),
    ('syarat: ringkasan tahun lalu diabaikan', FK, "  let lintas = 0; const R = ringkasArsip();", "  let lintas = 0; const R = null;"),
    ('syarat: saldo awal tidak dihitung langganan', FK, "if (/^\\d{4}-\\d\\d-\\d\\d$/.test(t) && t <= iso && (!pertama || t < pertama)) pertama = t; });", "});"),
    ('syarat: nota di luar jendela ikut', FK, "if (t >= dari) nota[fkKunciNota(p)] = true;", "nota[fkKunciNota(p)] = true;"),
    ('syarat: langganan diukur dari hari ini, bukan belanja pertama', FK, "if (S.syaratBulan > 0 && (!pertama || pertama > fkMundurBulan(iso, S.syaratBulan)))", "if (false)"),
    ('syarat: batas owner tidak meloloskan', JL, "if (info.sumber !== 'owner') { const Y = fkSyaratBon(", "if (true) { const Y = fkSyaratBon("),
    ('syarat: KR1 tidak memeriksa syarat', JL, "if (Y) return fkSyaratBonTeks(nama, Y) + '.'; }", "if (false) return fkSyaratBonTeks(nama, Y) + '.'; }"),
    ('setelan: hari tagih tidak disimpan', PL, "hariTagih: ht.nilai, syaratBulan: sy.syaratBulan,", "syaratBulan: sy.syaratBulan,"),
    ('setelan: syarat hari < 7 diterima', FK, "syaratHari: [7, 365] };", "syaratHari: [0, 365] };"),
    ('pengingat: hari tagih tidak jadi pengingat', SL, "if (HT.nyala && HT.daftar.length) out.push(", "if (false) out.push("),
    ('pengingat: lokal.uang menerima jenis apa saja', SL, "if (p && (p.jenis === 'setor' || p.jenis === 'rekening') &&", "if (p &&"),
]
STATIS = [
    ('Pelanggan › Bon: tab Jatuh tempo + kelompok + kalimat menutup', 'pelanggan', ["['tempo', 'Jatuh tempo']", "${s.tabB === 'tempo' ? gambarTempo(d, s) : ''}", 'data-k="pn-kelompok"', 'data-k="pn-tidak-menutup"', 'data-aksi="pnPilih"']),
    ('Pelanggan › Papan tagih: hari tagih di atas', 'pelanggan', ['${kartuHariTagih(d)}', 'data-k="hari-tagih"', 'B.pnHariTagih(d)']),
    ('Pelanggan › Atur: hari tagih & syarat bon', 'pelanggan', ['data-k="atur-tagih"', 'data-aksi="aturHariTagih"', 'data-k="atur-syarat"', 'data-kolom="syaratBulan"', 'data-kolom="syaratNota"', 'data-kolom="syaratHari"', 'hariTagih: String(a.hariTagih)']),
    ('Dasbor: piutang per nota & hari tagih', 'dasbor', ['data-k="db-per-nota"', 'data-k="db-hari-tagih"', "' · per nota: lewat jatuh tempo '"]),
    ('Dasbor logika: per nota & hari tagih apa adanya dari bon-logika', 'dasborL', ['const R = pnRingkas(kini, SB);', 'const T = pnHariTagih(kini, SB);']),
    ('Jual: KR1 memeriksa syarat bon', 'jual', ["fkSyaratBon(nama, hariIniIso(new Date(Date.now())))"]),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_bon_eceran.py && python3 alat-uji/uji_bon_eceran.py --kontrol']),
    ('BACA-DULU menyebut bon eceran', 'baca', ['pnRingkas', 'fkSyaratBon', 'hariTagih']),
]
RUSAK_STATIS = [
    ('Pelanggan tanpa tab Jatuh tempo', 'pelanggan', "${s.tabB === 'tempo' ? gambarTempo(d, s) : ''}", "''"),
    ('Dasbor tanpa per nota', 'dasbor', 'data-k="db-per-nota"', 'data-k="db-x"'),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_bon_eceran.py', 'true'),
]


def bundel(teks):
    return bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)


def jalan(teks, isi=None):
    js = JAM + bundel(teks) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar jual = function (i, tgl, cara, nama, trx, n) { return { id: i, tanggal: tgl, jam: "09:00", caraBayar: cara, namaPelanggan: nama, jenis: "karung", merkSumber: "Angsa", totalKg: 10, hargaTotal: n, hppTotalSaatJual: Math.round(n * 0.9), trxId: trx }; };\n' + (isi or SKENARIO)
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
    if 'hariTagih' in src['rules'] or 'syaratBon' in src['rules']: g.append('rules disentuh — paket ini sengaja tanpa rules baru')
    return len(STATIS) - len(g), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


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
            beres = not ha['galat'] and ha['out'].get('menutup') is True
            print('ASAP DATA TOKO (%s): %s — %s' % (os.path.basename(cad[-1]), 'LULUS' if beres else 'GAGAL', json.dumps(ha, ensure_ascii=False)))
            if not beres: g = list(g) + ['asap']
    sys.exit(1 if g or gs else 0)
