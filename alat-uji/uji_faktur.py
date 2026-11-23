#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_faktur.py — B2 FAKTUR BERTEMPO & BATAS KREDIT (keputusan owner 17 Nov 2026). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  · tempo: bawaan toko (Atur Pelanggan, bawaan 14 hari) — kartu pelanggan menang; jatuh tempo = tanggal nota + tempo;
  · batas kredit: angka owner di kartu, kosong = rumus lama KR1 (2× rata belanja bulanan 90 hari); bayar kurang (sisa jadi bon) IKUT batas;
  · lewat batas → Ben MEMINTA persetujuan owner (persetujuan tindakan 'kredit', bentuk = rules v9 stafMintaKredit); owner menyetujui di papan → nota hari itu
    lolos & membawa kreditSetujuId; persetujuan dipakai SEKALI, hanya hari diputus, nominal ≥ bon nota;
  · faktur: nota BON pelanggan usaha otomatis bernomor F<yy>-<kode perangkat>-<urut> + jatuhTempo + tempoHari; nota lain dijadikan faktur oleh owner;
  · pelunasan: tertua dulu (= buku bon lama, huruf demi huruf) atau faktur pilihan (untukFaktur); bayar saat beli sebuah faktur menutup faktur itu;
    jumlah sisa SELALU = sisa mesin; umur bon dari bon terbuka tertua;
  · struk & Sertifikat menyebut nomor faktur, alamat pembeli, jatuh tempo; pengingat & Dasbor menyebut faktur lewat / segera jatuh tempo;
  · faktur pajak disiapkan: rekap per bulan (CSV), PKP dari profil pajak.

    python3 alat-uji/uji_faktur.py            → N lulus · 0 gagal
    python3 alat-uji/uji_faktur.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_harga_tingkat, uji_jual_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
FK = 'baru/js/layar/faktur-logika.js'; JL = 'baru/js/layar/jual-logika.js'; SL = 'baru/js/layar/sistem-logika.js'; AK = 'baru/js/data/akses.js'
BN = 'baru/js/layar/bon-logika.js'; PL = 'baru/js/layar/pelanggan-logika.js'; STK = 'baru/js/layar/struk-logika.js'; SM = 'baru/js/inti/struk-model.js'
MODUL = [m for m in uji_harga_tingkat.MODUL if m != FK] + [SM, FK]   # Dasbor (dbTagihan = fkPengingat apa adanya) dijaga statis — bundel Dasbor tidak satu lingkup dengan bundel Jual
MODUL = [m for i, m in enumerate(MODUL) if m not in MODUL[:i]]
SUMBER = {'pelanggan': 'baru/js/layar/pelanggan.js', 'jual': 'baru/js/layar/jual.js', 'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml',
          'rules': 'firestore.rules', 'app': 'baru/js/app.js', 'dasbor': 'baru/js/layar/dasbor.js', 'dasborL': 'baru/js/layar/dasbor-logika.js', 'kanvas': 'baru/js/inti/struk-kanvas.js'}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
var J = function (x) { return JSON.stringify(x); };
var nId = 9000; var W = { tanggal: '2026-11-17', jam: '10:00', kini: '2026-11-17T03:00:00.000Z', kodePerangkat: 'TES', idUnik: function () { nId += 1; return nId; } };
var KINI = new Date('2026-11-17T10:00:00+07:00');
var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
var BEN = keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true });
var KRY = keadaanAkun('kry.contoh@tokoberasmiqbal.web.app', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true });
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
pasok('aksesAkun', [{ id: 'uid-ben', uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true }, { id: 'uid-kry', uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true }]);
setelSumber('cadangan', 'kotak pasir');
var hak = function (akun) { return Object.assign({}, (ssAtur('peran').hak || {})[akun.peran] || {}, { jatahNego: ngJatah(akun) }); };
var kirim = function (akun, dok) { return periksaKiriman(akun, (dok || []).map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false, lama: null }; }), [], hak(akun), KINI); };
var s = keadaanAwal(); s.sekarang = KINI;
function terap(p) { s = Object.assign({}, s, p); sinkronKeranjang(s); return p; }
function chip(jalur, kunci, berat) { var r = susunRak(s); return r[jalur].find(function (c) { return c.kunci === kunci && (!berat || c.berat === berat); }); }
function mulai() { s = keadaanAwal(); s.sekarang = KINI; sinkronKeranjang(s); }
function isi(jalur, kunci, n) { terap(ketukChip(s, chip(jalur, kunci))); terap({ ketik: String(n) }); terap(masukkan(s)); }
var pj = function (N) { return N.dokumen.filter(function (x) { return x.koleksi === 'penjualan'; }).map(function (x) { return x.data; }); };
var SET = { id: 'hargaTingkat', tingkat: [{ id: 'warung', nama: 'Warung', potKg: 0 }, { id: 'catering', nama: 'Catering', potKg: 0 }, { id: 'instansi', nama: 'Instansi', potKg: 0 }],
  barang: {}, orang: { 'bu suti': 'warung' }, khusus: [] };
pasok('aturanToko', [JSON.parse(J(SET))]);

// ---- A · tempo, batas, nomor
ok('A: tempo bawaan tanpa setelan = 14 hari', fkTempoBawaan() === 14 && fkTempo('Bu Suti').hari === 14 && fkTempo('Bu Suti').sumber === 'bawaan', J(fkTempo('Bu Suti')));
pasok('aturanToko', [JSON.parse(J(SET)), { id: 'pelanggan', tempoBawaan: 30 }]);
ok('A: tempo bawaan diatur owner (30) dipakai', fkTempoBawaan() === 30 && fkTempo('Deka').hari === 30);
pasok('aturanToko', [JSON.parse(J(SET)), { id: 'pelanggan', tempoBawaan: 999 }]);
ok('A: tempo bawaan di luar 0–365 diabaikan → 14', fkTempoBawaan() === 14);
pasok('aturanToko', [JSON.parse(J(SET))]);
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'warung depan pasar', tempoHari: 7, alamat: 'Jl. Contoh 1' }]);
ok('A: tempo di kartu pelanggan menang (7 hari, sumber kartu)', fkTempo('bu suti').hari === 7 && fkTempo('Bu Suti').sumber === 'kartu' && /kartu/.test(fkTempoTeks(fkTempo('Bu Suti'))));
var I0 = fkInfoKredit('Bu Suti');
ok('A: batas kosong = rumus lama (2× rata belanja bulanan; Bu Suti 216.000/3 × 2 = 144.000)', I0.sumber === 'rumus' && I0.batas === 144000 && I0.terdaftar === true, J(I0));
var ID = fkInfoKredit('Deka');
ok('A: Deka tanpa kartu → rumus, belum terdaftar', ID.sumber === 'rumus' && ID.terdaftar === false && ID.sisa === 890000, J(ID));
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'warung depan pasar', tempoHari: 7, alamat: 'Jl. Contoh 1' }, { id: 'deka', nama: 'Deka', batasKredit: 2000000 }]);
var ID2 = fkInfoKredit('Deka');
ok('A: angka owner di kartu Deka (Rp2 jt) menggantikan rumus & menganggapnya terdaftar', ID2.sumber === 'owner' && ID2.batas === 2000000 && ID2.terdaftar === true && /angka owner/.test(fkSumberBatas(ID2)), J(ID2));
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'warung depan pasar', tempoHari: 7, alamat: 'Jl. Contoh 1' }]);
ok('A: kode perangkat 3 tanda tetap untuk id yang sama, tanpa 0/O/1/I/L; tanpa id = XXX', /^[A-HJKMNP-Z2-9]{3}$/.test(fkKodePerangkat('p-abc-12345')) && ['p-1', 'p-2', 'p-xyz', 'p-mk3x9-ab12c'].every(function (x) { return /^[A-HJKMNP-Z2-9]{3}$/.test(fkKodePerangkat(x)); }) && fkKodePerangkat('p-abc-12345') === fkKodePerangkat('p-abc-12345') && fkKodePerangkat('') === 'XXX');
ok('A: nomor pertama perangkat di tahun itu = F26-TES-0001', fkNomorBaru('2026-11-17', 'TES') === 'F26-TES-0001', fkNomorBaru('2026-11-17', 'TES'));
ok('A: usaha = punya tingkat harga (Bu Suti ya, Deka tidak)', fkUsaha('Bu Suti') && !fkUsaha('Deka'));
ok('A: jatuh tempo = tanggal + hari (lintas bulan)', fkTambahHari('2026-11-25', 7) === '2026-12-02' && fkTambahHari('2026-12-30', 14) === '2027-01-13');

// ---- B · Jual: nota bon pelanggan usaha jadi faktur
mulai(); isi('kemasan', 'Kembang|5', 1); terap(pilihCara(s, 'Kredit')); terap({ pelanggan: 'Bu Suti' });
ok('B: bon Bu Suti 72.000 di bawah batas 144.000 → sah', alasanTolak(s) === '', alasanTolak(s));
var N1 = susunNotaDokumen(s, W); var P1 = pj(N1);
ok('B: nota BON pelanggan usaha → semua baris membawa noFaktur F26-TES-0001, jatuhTempo 17 Nov + 7 = 24 Nov, tempoHari 7', P1.length >= 1 && P1.every(function (p) { return p.noFaktur === 'F26-TES-0001' && p.jatuhTempo === '2026-11-24' && p.tempoHari === 7 && p.caraBayar === 'Kredit'; }), J(P1.map(function (p) { return [p.noFaktur, p.jatuhTempo, p.tempoHari]; })));
terapkanKeCache(N1.dokumen);
ok('B: nomor berikutnya perangkat yang sama = 0002 (membaca tulisannya sendiri)', fkNomorBaru('2026-11-17', 'TES') === 'F26-TES-0002' && fkNomorBaru('2026-11-17', 'LAI') === 'F26-LAI-0001');
mulai(); isi('kemasan', 'Kembang|5', 1); terap({ pelanggan: 'Bu Suti' }); terap(uangPas(s));
ok('B: nota TUNAI pelanggan usaha → bukan faktur', pj(susunNotaDokumen(s, W)).every(function (p) { return !p.noFaktur; }));
mulai(); isi('kemasan', 'Kembang|5', 1); terap(pilihCara(s, 'Kredit')); terap({ pelanggan: 'Deka', kreditDibuka: true });
ok('B: nota BON pelanggan bukan usaha → bukan faktur', pj(susunNotaDokumen(s, W)).every(function (p) { return !p.noFaktur; }));
mulai(); isi('kemasan', 'Kembang|5', 1); terap({ pelanggan: 'Bu Suti' }); terap(tambahUang(s, 50000));
ok('B: bayar kurang pelanggan usaha (sisa 22.000 jadi bon, di bawah batas) → sah & jadi faktur', alasanTolak(s) === '' && pj(susunNotaDokumen(s, W)).every(function (p) { return p.noFaktur === 'F26-TES-0002' && p.caraBayar === 'Kredit'; }), alasanTolak(s));

// ---- C · KR1: batas, bayar kurang, persetujuan (batas Bu Suti dikunci angka owner Rp150.000 — rumus lama ikut naik oleh nota bon uji ini sendiri)
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'warung depan pasar', tempoHari: 7, alamat: 'Jl. Contoh 1', batasKredit: 150000 }]);
mulai(); isi('kemasan', 'Kembang|5', 1); terap({ pelanggan: 'Deka' }); terap(tambahUang(s, 50000));
ok('C: bayar kurang Deka (belum terdaftar) → ditolak KR1 (dulu lolos)', /kurang Rp22\.000/.test(alasanTolak(s)) && /belum terdaftar/.test(alasanTolak(s)), alasanTolak(s));
mulai(); isi('kemasan', 'Kembang|5', 2); terap(pilihCara(s, 'Kredit')); terap({ pelanggan: 'Bu Suti' });
var tolakBatas = alasanTolak(s);
ok('C: bon Bu Suti 72.000 lama + 144.000 baru > batas 150.000 → ditolak "Melewati batas kredit"', /Melewati batas kredit Rp150\.000/.test(tolakBatas), tolakBatas);
var M = fkSusunMinta(BEN, 'Bu Suti', bonKeranjang(s), W, {}); var md = M.dokumen && M.dokumen[0].data;
ok('C: Ben meminta persetujuan → persetujuan tindakan kredit, menunggu, mintaUid = uid Ben, tanpa kolom keputusan', md && md.tindakan === 'kredit' && md.status === 'menunggu' && md.mintaUid === 'uid-ben' && md.nominal === 144000 && !('diputusPada' in md), J(md));
var mdB = beriAtribusiAkun ? null : null;
var KB = kirim(BEN, M.dokumen.map(function (x) { return { koleksi: x.koleksi, data: Object.assign({}, x.data, { olehUid: 'uid-ben' }) }; }));
ok('C: penjaga kiriman menerima permintaan bon dari Ben (bentuk rules v9)', !KB.tolak, J(KB));
var KK = kirim(KRY, [{ koleksi: 'persetujuan', data: Object.assign({}, md, { mintaUid: 'uid-kry', olehUid: 'uid-kry' }) }]);
ok('C: karyawan ditolak (bon = ben saja)', !!KK.tolak, J(KK));
var KL = kirim(BEN, [{ koleksi: 'persetujuan', data: Object.assign({}, md, { mintaUid: 'uid-lain', olehUid: 'uid-ben' }) }]);
ok('C: atas nama akun lain ditolak', !!KL.tolak, J(KL));
var KS = kirim(BEN, [{ koleksi: 'persetujuan', data: Object.assign({}, md, { status: 'disetujui', olehUid: 'uid-ben' }) }]);
ok('C: Ben tidak menyetujui sendiri', !!KS.tolak, J(KS));
// tablet yang berbohong: teks kiriman dipalsukan — papan owner wajib menghitung ulang dari buku, bukan memajang teks ini
terapkanKeCache([{ koleksi: 'persetujuan', data: Object.assign({}, md, { teks: 'Bon kecil saja Rp1.000 · batas aman' }) }]);
ok('C: permintaan yang sama tidak dikirim dua kali', !!fkSusunMinta(BEN, 'Bu Suti', 144000, W, {}).tolak);
var PP = ssPersetujuan(KINI); var bk = PP.menunggu.find(function (m) { return m.tindakan === 'kredit'; });
ok('C: papan owner: "Bon melewati batas kredit", kalimat dihitung ulang dari buku, TIDAK ikut setujui sekaligus', bk && bk.namaTindakan === 'Bon melewati batas kredit' && bk.sekaligus === false && /batas Rp150\.000 \(angka owner\)/.test(bk.teks) && /lama Rp72\.000/.test(bk.teks), J(bk));
ok('C: sebelum diputus: bon tetap ditolak', alasanTolak(s) !== '');
var PU = susunPutusPersetujuan(md.id, true, '', W); terapkanKeCache(PU.dokumen);
ok('C: owner menyetujui → nota yang sama sekarang sah', alasanTolak(s) === '', alasanTolak(s));
var N2 = susunNotaDokumen(s, W); var P2 = pj(N2);
ok('C: nota membawa kreditSetujuId = id persetujuan & jadi faktur', P2.every(function (p) { return String(p.kreditSetujuId) === String(md.id) && /^F26-TES-/.test(p.noFaktur); }), J(P2.map(function (p) { return [p.kreditSetujuId, p.noFaktur]; })));
terapkanKeCache(N2.dokumen);
mulai(); isi('kemasan', 'Kembang|5', 1); terap(pilihCara(s, 'Kredit')); terap({ pelanggan: 'Bu Suti' });
ok('C: persetujuan dipakai SEKALI — nota berikutnya ditolak lagi', /Melewati batas kredit/.test(alasanTolak(s)), alasanTolak(s));
var md2 = Object.assign({}, md, { id: 'kemarin', nominal: 999999, status: 'disetujui', diputusTanggal: '2026-11-16' }); terapkanKeCache([{ koleksi: 'persetujuan', data: md2 }]);
ok('C: persetujuan yang diputus KEMARIN tidak dipakai hari ini', /Melewati batas kredit/.test(alasanTolak(s)), alasanTolak(s));
var md3 = Object.assign({}, md, { id: 'kecil', nominal: 1000, status: 'disetujui', diputusTanggal: '2026-11-17' }); terapkanKeCache([{ koleksi: 'persetujuan', data: md3 }]);
ok('C: persetujuan bernominal lebih kecil dari bon nota tidak dipakai', /Melewati batas kredit/.test(alasanTolak(s)));
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'warung depan pasar', tempoHari: 7, alamat: 'Jl. Contoh 1', batasKredit: 5000000 }]);
ok('C: owner menaikkan batas di kartu (Rp5 jt) → bon Bu Suti sah tanpa persetujuan', alasanTolak(s) === '', alasanTolak(s));
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'warung depan pasar', tempoHari: 7, alamat: 'Jl. Contoh 1', batasKredit: 100000 }]);
ok('C: batas angka owner yang terlewati menyebut sumbernya', /batas angka owner/.test(alasanTolak(s)), alasanTolak(s));
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'warung depan pasar', tempoHari: 7, alamat: 'Jl. Contoh 1' }]);

// ---- D · faktur, alokasi, pembayaran
var R0 = function (id, tgl, no, total, cara) { return { id: id, trxId: 't' + id, tanggal: tgl, jam: '09:00', caraBayar: cara || 'Kredit', namaPelanggan: 'Pak Contoh', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, hargaTotal: total, hppTotalSaatJual: 1, noFaktur: no, jatuhTempo: fkTambahHari(tgl, 14), tempoHari: 14 }; };
pasok('penjualan', KOTAK.penjualan.concat([R0('f1', '2026-11-01', 'F26-AAA-0001', 100000), R0('f2', '2026-11-10', 'F26-AAA-0002', 50000)]));
pasok('piutangMutasi', JSON.parse(J(KOTAK.piutangMutasi)));
var D = fkSemua(KINI); var F1 = D.find(function (f) { return f.no === 'F26-AAA-0001'; }); var F2 = D.find(function (f) { return f.no === 'F26-AAA-0002'; });
ok('D: dua faktur Pak Contoh: F1 lewat 2 hari (jatuh 15 Nov), F2 belum (24 Nov); sisa = total', F1 && F1.status === 'lewat' && F1.hariLewat === 2 && F1.sisa === 100000 && F2 && F2.status === 'belum' && F2.sisa === 50000, J([F1, F2].map(function (f) { return f && [f.status, f.hariLewat, f.sisa]; })));
var semuaSama = function () { return hitungPiutang().every(function (d) { return J(rincianBelumLunas(d)) === J(bnRincianLama(d)); }); };
ok('D: tanpa pembayaran beralamat, rincian bon = loop lama huruf demi huruf (semua orang)', semuaSama());
terapkanKeCache([{ koleksi: 'piutangMutasi', data: { id: 'byr1', tipe: 'bayar', namaPelanggan: 'Pak Contoh', nominal: 60000, tanggal: '2026-11-12', jam: '10:00', caraBayar: 'Tunai' } }]);
D = fkSemua(KINI); F1 = D.find(function (f) { return f.no === 'F26-AAA-0001'; }); F2 = D.find(function (f) { return f.no === 'F26-AAA-0002'; });
ok('D: bayar 60.000 tanpa pilihan → tertua dulu: F1 sisa 40.000, F2 utuh 50.000', F1.sisa === 40000 && F2.sisa === 50000, J([F1.sisa, F2.sisa]));
ok('D: masih sama dengan loop lama (tidak ada yang beralamat)', semuaSama());
var BB = susunBayarBon(KINI, 'pak contoh', 50000, 'Tunai', '', '', W, ['F26-AAA-0002']);
ok('D: bayar 50.000 untuk F2 → dokumen membawa untukFaktur [F2]', BB.dokumen && J(BB.dokumen[0].data.untukFaktur) === J(['F26-AAA-0002']), J(BB));
ok('D: bayar melebihi sisa faktur pilihan ditolak (tidak diam-diam pindah)', !!susunBayarBon(KINI, 'pak contoh', 60000, 'Tunai', '', '', W, ['F26-AAA-0002']).tolak);
ok('D: faktur yang bukan milik / bukan terbuka ditolak', !!susunBayarBon(KINI, 'pak contoh', 1000, 'Tunai', '', '', W, ['F26-ZZZ-0009']).tolak);
terapkanKeCache(BB.dokumen);
D = fkSemua(KINI); F1 = D.find(function (f) { return f.no === 'F26-AAA-0001'; }); F2 = D.find(function (f) { return f.no === 'F26-AAA-0002'; });
var dPC = hitungPiutang().find(function (x) { return x.kunci === 'pak contoh'; });
ok('D: F2 LUNAS, F1 tetap sisa 40.000 — jumlah = sisa mesin 40.000', F2.status === 'lunas' && F2.sisa === 0 && F1.sisa === 40000 && dPC.sisa === 40000, J([F1.sisa, F2.sisa, dPC.sisa]));
var rinc = rincianBelumLunas(dPC);
ok('D: rincian bon Pak Contoh = baris F1 sisa 40.000 (bukan F2 seperti tertua-dulu murni)', rinc.length === 1 && String(rinc[0].idTrx) === 'f1' && rinc[0].sisa === 40000, J(rinc));
ok('D: loop lama (tertua dulu murni) memang berbeda di sini — F1 tertutup, F2 sisa', J(bnRincianLama(dPC)) !== J(rinc));
var bonPC = semuaBon(KINI).find(function (b) { return b.kunci === 'pak contoh'; });
ok('D: umur bon Pak Contoh dari bon terbuka tertua (F1, 1 Nov = 16 hari)', bonPC.umur === 16, J(bonPC.umur));
ok('D: orang lain tidak berubah (Deka tetap = loop lama)', J(rincianBelumLunas(hitungPiutang().find(function (x) { return x.kunci === 'deka'; }))) === J(bnRincianLama(hitungPiutang().find(function (x) { return x.kunci === 'deka'; }))));
pasok('penjualan', KOTAK.penjualan.concat([R0('f1', '2026-11-01', 'F26-AAA-0001', 100000), R0('f3', '2026-11-11', 'F26-AAA-0003', 80000)]));
pasok('piutangMutasi', JSON.parse(J(KOTAK.piutangMutasi)).concat([{ id: 'sb1', tipe: 'bayar', namaPelanggan: 'Pak Contoh', nominal: 30000, tanggal: '2026-11-11', jam: '09:00', caraBayar: 'Tunai', notaTrxId: 'tf3' }]));
D = fkSemua(KINI); F1 = D.find(function (f) { return f.no === 'F26-AAA-0001'; }); var F3 = D.find(function (f) { return f.no === 'F26-AAA-0003'; });
ok('D: bayar SAAT BELI faktur F3 (notaTrxId) menutup F3, bukan F1: F3 sisa 50.000, F1 utuh', F3.sisa === 50000 && F1.sisa === 100000, J([F1.sisa, F3.sisa]));
var PG = fkPengingat(KINI);
ok('D: pengingat: F1 lewat (Rp100.000) di depan; F3 belum jatuh tempo tidak ikut', PG.daftar.length === 1 && PG.daftar[0].no === 'F26-AAA-0001' && PG.lewat === 100000, J(PG.daftar.map(function (f) { return f.no; })));
var SP = ssSumberPengingat(KINI, {}).filter(function (p) { return p.jenis === 'faktur'; });
ok('D: sumber pengingat jenis faktur: tiap faktur terbuka, jatuh = jatuh tempo, nominal = sisa', SP.length === 2 && SP.some(function (p) { return p.id === 'faktur|F26-AAA-0001' && p.jatuh === '2026-11-15' && p.n === 100000; }), J(SP));
ok('D: kisi pengingat punya jenis faktur (hariFaktur, bawaan 3 hari, Owner & Ben)', SS_JENIS_PENGINGAT.some(function (j) { return j.id === 'faktur' && j.kunci === 'hariFaktur'; }) && ssAtur('pengingat').hariFaktur === 3);

// ---- E · struk & jadikan faktur
pasok('penjualan', KOTAK.penjualan.concat([R0('f1', '2026-11-01', 'F26-AAA-0001', 100000)]));
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'x' }, { id: 'pak contoh', nama: 'Pak Contoh', catatan: 'x', alamat: 'Gang Contoh 2' }]);
var NF = notaDariBaris([R0('f1', '2026-11-01', 'F26-AAA-0001', 100000)]); var SF = susunStruk(NF, null, null); var tF = SF.teks;
ok('E: struk faktur menyebut nomor faktur, alamat pembeli, jatuh tempo', /Faktur No\. F26-AAA-0001/.test(tF) && /Alamat: Gang Contoh 2/.test(tF) && /Jatuh tempo: .*15.*\(14 hari\)/.test(tF), tF);
var MF = stModelSertifikat(SF.garis);
ok('E: model Sertifikat membawa faktur, alamat pembeli, jatuh tempo', MF.faktur === 'F26-AAA-0001' && MF.alamatPembeli === 'Gang Contoh 2' && /15/.test(MF.jatuhTempo), J({ f: MF.faktur, a: MF.alamatPembeli, j: MF.jatuhTempo }));
var NT = notaDariBaris([KOTAK.penjualan[0]]); var tT = susunStruk(NT, null, null).teks;
ok('E: struk nota biasa tanpa baris faktur', !/Faktur No\./.test(tT) && !/Jatuh tempo/.test(tT));
var JF = fkSusunJadikan(NT, W, 'TES');
ok('E: owner menjadikan nota tunai Bu Suti faktur → semua baris noFaktur + jatuhTempo', JF.dokumen && JF.dokumen.every(function (x) { return /^F26-TES-/.test(x.data.noFaktur) && x.data.jatuhTempo === fkTambahHari(NT.tanggal, fkTempo('Bu Suti').hari); }), J(JF));
ok('E: nota yang sudah faktur ditolak', !!fkSusunJadikan(NF, W, 'TES').tolak);
ok('E: nota tanpa nama ditolak', !!fkSusunJadikan(Object.assign({}, NT, { nama: '' }), W, 'TES').tolak);
ok('E: nota batal ditolak', !!fkSusunJadikan(notaDariBaris([KOTAK.penjualan[3]]), W, 'TES').tolak);
terapkanKeCache(JF.dokumen);
var FT = fkSemua(KINI).find(function (f) { return f.trxId === String(NT.trxId || NT.grupNota || NT.id); });
ok('E: faktur dari nota tunai: status dibayar, sisa 0', FT && FT.status === 'tunai' && FT.sisa === 0, J(FT));

// ---- F · Atur & kartu
var AT = susunAturPelanggan({ tempoBawaan: '30' }, W);
ok('F: Atur menyimpan tempo faktur bawaan 30', AT.dokumen && AT.dokumen[0].data.tempoBawaan === 30, J(AT.tolak || AT.dokumen[0].data.tempoBawaan));
ok('F: tempo bawaan 400 ditolak', !!susunAturPelanggan({ tempoBawaan: '400' }, W).tolak);
ok('F: Atur tanpa isian tempo mempertahankan yang tersimpan', susunAturPelanggan({}, W).dokumen[0].data.tempoBawaan === fkTempoBawaan());
var KR = susunSimpanKartu(KINI, 'bu suti', { nama: 'Bu Suti', catatan: 'x', tempoHari: '7', batasKredit: '1.000.000' }, W);
ok('F: kartu menyimpan tempo 7 & batas Rp1.000.000 (titik ribuan)', KR.dokumen && KR.dokumen[0].data.tempoHari === 7 && KR.dokumen[0].data.batasKredit === 1000000, J(KR.tolak || KR.dokumen[0].data));
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'x', tempoHari: 7, batasKredit: 1000000 }]);
var KR2 = susunSimpanKartu(KINI, 'bu suti', { nama: 'Bu Suti', catatan: 'x', tempoHari: '', batasKredit: '' }, W);
ok('F: dikosongkan → kolomnya dihapus (kembali ke bawaan / rumus)', KR2.dokumen && !('tempoHari' in KR2.dokumen[0].data) && !('batasKredit' in KR2.dokumen[0].data), J(KR2.dokumen && KR2.dokumen[0].data));
var KR3 = susunSimpanKartu(KINI, 'bu suti', { nama: 'Bu Suti', catatan: 'x' }, W);
ok('F: isian tanpa kolom tempo/batas tidak menghapus yang tersimpan', KR3.dokumen && KR3.dokumen[0].data.tempoHari === 7 && KR3.dokumen[0].data.batasKredit === 1000000);
ok('F: Atur tempo bawaan "abc" ditolak (bukan 0 hari)', !!susunAturPelanggan({ tempoBawaan: 'abc' }, W).tolak);
ok('F: tempo "abc" & batas 0 ditolak', !!susunSimpanKartu(KINI, 'bu suti', { nama: 'Bu Suti', catatan: 'x', tempoHari: 'abc' }, W).tolak && !!susunSimpanKartu(KINI, 'bu suti', { nama: 'Bu Suti', catatan: 'x', batasKredit: '0' }, W).tolak);

// ---- E2 · STOP BON (owner 24 Nov 2026): bon tertua belum lunas > N hari → bon baru ditahan lewat gerbang kredit yang sama (KR1/B2)
var RL = function (id, tgl, total) { return Object.assign(R0(id, tgl, '', total), { namaPelanggan: 'Pak Lama' }); };
pasok('penjualan', KOTAK.penjualan.concat([RL('sl1', '2026-10-01', 80000)]));
pasok('pelangganCatatan', [{ id: 'pak lama', nama: 'Pak Lama', catatan: 'x', batasKredit: 5000000 }]);
pasok('piutangMutasi', JSON.parse(J(KOTAK.piutangMutasi)));
pasok('aturanToko', [JSON.parse(J(SET))]);
mulai(); isi('kemasan', 'Kembang|5', 1); terap(pilihCara(s, 'Kredit')); terap({ pelanggan: 'Pak Lama' });
var tSB = alasanTolak(s);
ok('E2: bawaan 30 hari — bon tertua 1 Okt (47 hari) belum lunas → bon baru DITAHAN; kalimat menyebut tanggal, umur, batas, sisa', fkStopBonHari() === 30 && /^Stop bon: bon tertua Pak Lama belum lunas sejak /.test(tSB) && /47 hari, batas 30 hari/.test(tSB) && /sisa bon Rp80\.000/.test(tSB), tSB);
mulai(); isi('kemasan', 'Kembang|5', 1); terap({ pelanggan: 'Pak Lama' }); terap(tambahUang(s, 50000));
ok('E2: bayar kurang (sisa jadi bon) ikut ditahan', /Stop bon/.test(alasanTolak(s)), alasanTolak(s));
mulai(); isi('kemasan', 'Kembang|5', 1); terap({ pelanggan: 'Pak Lama' }); terap(tambahUang(s, 500000));
ok('E2: bayar tunai lunas tidak ditahan (bukan bon baru)', alasanTolak(s) === '', alasanTolak(s));
mulai(); isi('kemasan', 'Kembang|5', 1); terap(pilihCara(s, 'Kredit')); terap({ pelanggan: 'Pak Lama' });
pasok('aturanToko', [JSON.parse(J(SET)), { id: 'pelanggan', stopBonHari: 60 }]);
ok('E2: N = 60 (diatur owner) → 47 hari belum kena', alasanTolak(s) === '', alasanTolak(s));
pasok('aturanToko', [JSON.parse(J(SET)), { id: 'pelanggan', stopBonHari: 47 }]);
ok('E2: tepat N hari (47 = 47) belum kena — "lewat" N hari', alasanTolak(s) === '', alasanTolak(s));
pasok('aturanToko', [JSON.parse(J(SET)), { id: 'pelanggan', stopBonHari: 0 }]);
ok('E2: N = 0 → stop bon mati', fkStopBonHari() === 0 && alasanTolak(s) === '');
pasok('aturanToko', [JSON.parse(J(SET)), { id: 'pelanggan', stopBonHari: 999 }]);
ok('E2: N di luar 0–365 diabaikan → bawaan 30', fkStopBonHari() === 30 && /Stop bon/.test(alasanTolak(s)));
pasok('aturanToko', [JSON.parse(J(SET))]);
var byrL = function (id, n, tgl) { return { id: id, tipe: 'bayar', namaPelanggan: 'Pak Lama', nominal: n, tanggal: tgl, jam: '10:00', caraBayar: 'Tunai' }; };
pasok('piutangMutasi', JSON.parse(J(KOTAK.piutangMutasi)).concat([byrL('slb1', 50000, '2026-11-10')]));
ok('E2: dibayar sebagian (bon tertua belum tertutup penuh) → tetap ditahan', /Stop bon/.test(alasanTolak(s)), alasanTolak(s));
pasok('piutangMutasi', JSON.parse(J(KOTAK.piutangMutasi)).concat([byrL('slb1', 50000, '2026-11-10'), byrL('slb2', 30000, '2026-11-12')]));
ok('E2: bon lama lunas → bon baru boleh', alasanTolak(s) === '', alasanTolak(s));
pasok('piutangMutasi', JSON.parse(J(KOTAK.piutangMutasi)).concat([byrL('slb1', 80000, '2026-11-10')]));
pasok('penjualan', KOTAK.penjualan.concat([RL('sl1', '2026-10-01', 80000), RL('sl2', '2026-11-05', 40000)]));
ok('E2: bon tertua ditutup FIFO, yang tersisa bon muda (12 hari) → boleh', alasanTolak(s) === '', alasanTolak(s));
pasok('piutangMutasi', JSON.parse(J(KOTAK.piutangMutasi)));
terap({ kreditDibuka: true });
ok('E2: owner membuka sekali (dua ketukan) → lolos', alasanTolak(s) === '', alasanTolak(s));
terap({ kreditDibuka: false });
var MS = fkSusunMinta(BEN, 'Pak Lama', bonKeranjang(s), W, {}); var mds = MS.dokumen && MS.dokumen[0].data;
ok('E2: karyawan minta persetujuan; papan owner menyebut STOP BON (dihitung ulang dari buku)', mds && mds.tindakan === 'kredit' && /Stop bon: bon tertua Pak Lama/.test(fkTeksMinta(mds)), mds && fkTeksMinta(mds));
terapkanKeCache(MS.dokumen); terapkanKeCache(susunPutusPersetujuan(mds.id, true, '', W).dokumen);
ok('E2: owner menyetujui → nota bon yang sama sah', alasanTolak(s) === '', alasanTolak(s));
var ATs = susunAturPelanggan({ stopBonHari: '45' }, W);
ok('E2: Atur menyimpan stop bon 45; 400 & "abc" ditolak; kosong mempertahankan; 0 boleh', ATs.dokumen && ATs.dokumen[0].data.stopBonHari === 45 && !!susunAturPelanggan({ stopBonHari: '400' }, W).tolak
  && !!susunAturPelanggan({ stopBonHari: 'abc' }, W).tolak && susunAturPelanggan({}, W).dokumen[0].data.stopBonHari === 30 && susunAturPelanggan({ stopBonHari: '0' }, W).dokumen[0].data.stopBonHari === 0, J(ATs.tolak || ATs.dokumen[0].data.stopBonHari));
pasok('penjualan', JSON.parse(J(KOTAK.penjualan))); pasok('pelangganCatatan', JSON.parse(J(KOTAK.pelangganCatatan || [])));

// ---- G · faktur pajak
pasok('penjualan', KOTAK.penjualan.concat([R0('f1', '2026-11-01', 'F26-AAA-0001', 100000), R0('f2', '2026-11-10', 'F26-AAA-0002', 50000)]));
var RK = fkRekapBulan('2026-11', KINI);
ok('G: rekap November: 2 faktur, nilai 150.000, CSV berkepala, status PKP belum diisi disebut jujur', RK.baris.length === 2 && RK.jumlah === 150000 && /^No faktur;/.test(RK.csv) && RK.pkp === false && /belum diisi/.test(RK.kalimat), J(RK));
pasok('aturanToko', [JSON.parse(J(SET)), { id: 'rekapOmzet', statusPkp: 'bukan' }]);
ok('G: profil pajak "bukan PKP" disebut apa adanya', /bukan PKP/.test(fkRekapBulan('2026-11', KINI).kalimat));
pasok('aturanToko', [JSON.parse(J(SET)), { id: 'rekapOmzet', statusPkp: 'pkp' }]);
ok('G: profil pajak PKP → rekap berlabel Coretax & bukan nasihat', fkRekapBulan('2026-11', KINI).pkp === true && /Coretax/.test(fkRekapBulan('2026-11', KINI).kalimat));
print(J({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('Pelanggan: tab Faktur, rekap pajak, tempo & batas di kartu, pilih faktur saat bayar, tempo bawaan & stop bon di Atur', 'pelanggan',
     ['data-kolom="stopBonHari"', 'stopBonHari: String(a.stopBonHari)', "['faktur', 'Faktur']", 'function gambarUFaktur(s, owner)', 'data-kolom="tempoHari"', 'data-kolom="batasKredit"', 'data-aksi="bayarFaktur"', 'data-kolom="tempoBawaan"', 'data-aksi="uFUnduh"',
      "B.susunBayarBon(kini(), st().orangBon, b.nominal, b.cara, b.catatan, b.pengantar, waktu(), b.faktur || [])"]),
    ('Jual: minta persetujuan bon, bayar kurang ikut KR1 di lembar Bayar, jadikan faktur di lembar Struk', 'jual',
     ['mintaKredit: () =>', 'const pitaMintaKredit = (s, bonN) =>', 'L.alasanKunciKredit(s, bonN)', 'jadikanFaktur: () =>', 'data-aksi="jadikanFaktur"', 'FK.fkSusunJadikan(x.nota']),
    ('app memasang id perangkat ke nomor faktur', 'app', ['fkPasangPerangkat(fb.idPerangkat());']),
    ('Dasbor menyebut faktur jatuh tempo (dbTagihan.faktur = fkPengingat)', 'dasbor', ['data-k="db-faktur"', 'G.faktur.daftar.map(']),
    ('Dasbor: logika piutang membawa faktur dari fkPengingat', 'dasborL', ['const FP = fkPengingat(kini);', 'faktur: { n: FP.daftar.length, rpLewat: FP.lewat, rpSegera: FP.segera,']),
    ('Sertifikat bertajuk FAKTUR untuk nota faktur', 'kanvas', ["tulis('FAKTUR'", "isian('Jatuh tempo', M.jatuhTempo"]),
    ('modul faktur dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/faktur-logika.js">']),
    ('CI menjalankan uji ini (+ kontrol)', 'pages', ['python3 alat-uji/uji_faktur.py && python3 alat-uji/uji_faktur.py --kontrol']),
    ('rules v9: permintaan bon lewat stafMintaKredit (ben)', 'rules', ["|| stafMintaKredit(['ben'])", "d.get('tindakan', '') == 'kredit'", "d.get('mintaUid', '') == request.auth.uid"]),
]

RUSAK = [
    ('nota bon bukan usaha ikut jadi faktur', FK, "  if (cara !== 'Kredit' || !String(nama || '').trim() || !fkUsaha(nama)) return null;", "  if (cara !== 'Kredit' || !String(nama || '').trim()) return null;"),
    ('nomor faktur tidak membaca yang sudah ada', FK, "if (Number.isInteger(u) && u > maks) maks = u;", "if (false) maks = u;"),
    ('tempo kartu diabaikan', FK, "const n = c ? fkHariSah(c.tempoHari) : null; return n === null ?", "const n = null; return n === null ?"),
    ('batas angka owner diabaikan', FK, "  const B = fkBatasOwner(nama);\n", "  const B = null;\n"),
    ('bayar kurang tidak kena KR1 lagi', JL, "  if (s.cara !== 'Kredit' && t.sisaJadiBon) { const nb = bonKeranjang(s, t);", "  if (false) { const nb = bonKeranjang(s, t);"),
    ('persetujuan dipakai berulang', FK, "&& fkMilik(m, akun) && !dipakai[String(m.id)])", "&& fkMilik(m, akun))"),
    ('persetujuan kemarin ikut dipakai', FK, "m.status === 'disetujui' && String(m.diputusTanggal || '') === String(tanggal) && ", "m.status === 'disetujui' && "),
    ('persetujuan kecil dipakai untuk bon besar', FK, "&& Math.round(Number(m.nominal) || 0) >= n && fkMilik", "&& fkMilik"),
    ('nota tidak mencatat persetujuan yang dipakai', JL, "    if (setujuId) d.kreditSetujuId = setujuId;", ""),
    ('pembayaran beralamat diabaikan', FK, "  if (Array.isArray(m.untukFaktur) && m.untukFaktur.length) return m.untukFaktur.map(String).filter(Boolean);", ""),
    ('bayar saat beli faktur tidak beralamat', FK, "const t = m.notaTrxId !== undefined && m.notaTrxId !== null ? (P || fkPeta()).nota[String(m.notaTrxId)] : null;", "const t = null;"),
    ('Bon memakai loop lama (pilihan faktur tidak terlihat)', BN, "export function rincianBelumLunas(d) { return fkRincian(d); }", "export function rincianBelumLunas(d) { return bnRincianLama(d); }"),
    ('bayar melebihi faktur pilihan diterima', BN, "    if (n > sisaPilih) return", "    if (false) return"),
    ('penjaga menerima permintaan bon atas nama orang lain', AK, " || String(d.mintaUid || '') !== String(akun.uid || '')) return { tolak: tolakTindakan('jualBon') };", ") return { tolak: tolakTindakan('jualBon') };"),
    ('penjaga menerima permintaan bon dari karyawan', AK, " || KREDIT_STAF.indexOf(P) < 0 || (hak.jualBon || 'tidak') === 'tidak'", ""),
    ('permintaan bon ikut setujui sekaligus', SL, "m.tindakan !== HT_TINDAKAN && m.tindakan !== FK_TINDAKAN,", "m.tindakan !== HT_TINDAKAN,"),
    ('papan memakai teks kiriman permintaan bon', SL, "HU !== null ? HU : KR !== null ? KR : m.teks || ''", "HU !== null ? HU : m.teks || ''"),
    ('struk tanpa nomor faktur', STK, "  if (nota.noFaktur) baris('Faktur No. ' + nota.noFaktur", "  if (false) baris('Faktur No. ' + nota.noFaktur"),
    ('model Sertifikat membuang jatuh tempo', SM, "else if (g.jenis === 'jatuhTempo') M.jatuhTempo = String(g.nilai || kiri);", ""),
    ('kartu tempo tidak divalidasi', PL, "  if (tempoTeks && tempo === null) return { tolak:", "  if (false) return { tolak:"),
    ('kartu menghapus tempo walau isian tidak membawanya', PL, "  if (adaTempo) { if (tempo === null) delete data.tempoHari; else data.tempoHari = tempo; }", "  if (tempo === null) delete data.tempoHari; else data.tempoHari = tempo;"),
    ('Atur tidak menyimpan tempo bawaan', PL, "tanggal: w.tanggal, jam: w.jam, tempoBawaan: tb.nilai,", "tanggal: w.tanggal, jam: w.jam,"),
    # stop bon (owner 24 Nov 2026)
    ('stop bon tidak dipasang di gerbang kredit', JL, "  return stopBon(nama);\n}", "  return null;\n}"),
    ('stop bon: N bawaan bukan 30', FK, "export const FK_STOP_BAWAAN = 30;", "export const FK_STOP_BAWAAN = 90;"),
    ('stop bon: 0 tidak mematikan', FK, "  const N = fkStopBonHari(); if (!(N > 0) || !String(nama || '').trim()) return null;", "  const N = fkStopBonHari() || 30; if (!String(nama || '').trim()) return null;"),
    ('stop bon: umur dihitung dari tanggal yang salah (bon tertua diabaikan)', FK, "Date.parse(tgl + 'T00:00:00Z')) / 86400000);", "Date.parse('2026-11-01T00:00:00Z')) / 86400000);"),
    ('stop bon: tepat N hari ikut ditahan (lebih dari, bukan sama dengan)', FK, "  if (!(umur > N)) return null;", "  if (!(umur >= N)) return null;"),
    ('papan owner tidak menyebut stop bon', FK, "    + ((S) => (S ? ' · ' + fkStopBonTeks(nama, S) : ''))(fkStopBon(nama));", ";"),
    ('Atur tidak menyimpan stop bon', PL, "tempoBawaan: tb.nilai, stopBonHari: sb.nilai, ", "tempoBawaan: tb.nilai, "),
    ('Atur stop bon tidak divalidasi', PL, "fkHariSah(isi.stopBonHari) === null ? { tolak:", "false ? { tolak:"),
    ('pengingat faktur hilang', SL, "  fkSemua(kini).forEach((f) => { if (!(f.sisa > 0.5)", "  [].forEach((f) => { if (!(f.sisa > 0.5)"),
]
RUSAK_STATIS = [
    ('lembar bayar bon tanpa pilihan faktur', 'pelanggan', 'data-aksi="bayarFaktur"', 'data-aksi="x"'),
    ('id perangkat tidak dipasang', 'app', 'fkPasangPerangkat(fb.idPerangkat());', ''),
]


def jalan(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write("var __KINI = new Date('2026-11-17T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" + js + '\nvar KOTAK = ' + json.dumps(uji_jual_baru.KOTAK) + ';\n' + SKENARIO); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], h['gagal']


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    return len(STATIS) - len(g), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


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
