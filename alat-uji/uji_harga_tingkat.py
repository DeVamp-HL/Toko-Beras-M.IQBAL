#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_harga_tingkat.py — B1 HARGA PELANGGAN USAHA (keputusan owner 16 Nov 2026). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  · setelan: bawaan Warung · Catering · Instansi (potongan 0); dokumen aturanToko/hargaTingkat dibersihkan (tingkat / harga barang / pelanggan / khusus);
  · harga: khusus yang berlaku hari itu → harga sendiri barang di tingkatnya → eceran − potongan/kg × kg satuannya (dibulatkan Rp50) → eceran;
  · Jual: chip menyebut harga tingkat (eceran chip tetap), baris nota memakai harga pelanggan (hargaAsli = harga tingkat, eceran tercatat di
    hargaEceranSatuan), ganti pembeli menghitung ulang keranjang, +1/−1 mempertahankan tingkat, nego di atas harga tingkat, dokumen nota membawa kolomnya;
  · ubah: owner menulis setelan langsung; Ben MENGUSULKAN (persetujuan tindakan hargaPelanggan, bentuk = rules v8 stafUsulHarga); karyawan ditolak;
    papan persetujuan owner menghitung ulang kalimatnya, tidak ikut "setujui sekaligus", dan menyetujui = memasang setelan di kiriman yang sama;
  · papan Usaha: modal & untung hanya untuk owner; tanda rugi / naik / habis; harga khusus berlaku / belum / lewat;
  · kartu pelanggan: alamat antar & NPWP (15/16 angka); kisi SS2 'hargaPelanggan' (Ben minta owner, karyawan tidak boleh).

    python3 alat-uji/uji_harga_tingkat.py            → N lulus · 0 gagal
    python3 alat-uji/uji_harga_tingkat.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_jual_nego, uji_jual_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
HT = 'baru/js/layar/harga-tingkat-logika.js'; JL = 'baru/js/layar/jual-logika.js'; SL = 'baru/js/layar/sistem-logika.js'; AK = 'baru/js/data/akses.js'
NG = 'baru/js/layar/nego-logika.js'; PL = 'baru/js/layar/pelanggan-logika.js'
MODUL = [m for m in uji_jual_nego.MODUL if m != HT] + ['baru/js/layar/pelanggan-logika.js', 'baru/js/layar/bon-logika.js', HT]
MODUL = [m for i, m in enumerate(MODUL) if m not in MODUL[:i]]
SUMBER = {'pelanggan': 'baru/js/layar/pelanggan.js', 'jual': 'baru/js/layar/jual.js', 'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml', 'rules': 'firestore.rules'}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
var J = function (x) { return JSON.stringify(x); };
var nId = 9000; var W = { tanggal: '2026-11-16', jam: '10:00', kini: '2026-11-16T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
var BEN = keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true });
var KRY = keadaanAkun('kry.contoh@tokoberasmiqbal.web.app', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true });
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
pasok('aksesAkun', [{ id: 'uid-ben', uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true }, { id: 'uid-kry', uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true }]);
setelSumber('cadangan', 'kotak pasir');
var hak = function (akun) { return Object.assign({}, (ssAtur('peran').hak || {})[akun.peran] || {}, { jatahNego: ngJatah(akun) }); };
var kirim = function (akun, dok) { return periksaKiriman(akun, (dok || []).map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false, lama: null }; }), [], hak(akun), new Date('2026-11-16T10:00:00+07:00')); };

// ---- A · bawaan
var A0 = htAtur();
ok('A: tanpa dokumen = tiga tingkat bawaan Warung · Catering · Instansi, potongan 0', !A0.ada && A0.tingkat.map(function (t) { return t.nama; }).join() === 'Warung,Catering,Instansi' && A0.tingkat.every(function (t) { return t.potKg === 0; }), J(A0));
ok('A: tanpa tingkat siapa pun = harga eceran (null)', htHarga({ orang: 'Bu Suti', barang: 'karung|Angsa|50', eceran: 690000, kg: 50 }) === null);
ok('A: kisi SS2 punya tindakan hargaPelanggan — Ben "minta owner", karyawan "tidak boleh"', SS_TINDAKAN.some(function (t) { return t.id === 'hargaPelanggan'; }) && ssPeran().hak('ben', 'hargaPelanggan') === 'owner' && ssPeran().hak('karyawan', 'hargaPelanggan') === 'tidak');
ok('A: kisi Ben "minta owner" = usul lewat papan Persetujuan (bukan "alurnya belum ada")', /papan Persetujuan/.test(ssHakServer('ben', 'hargaPelanggan', 'owner').ket), J(ssHakServer('ben', 'hargaPelanggan', 'owner')));
ok('A: staf membaca dokumen hargaTingkat & produkArsip (rules v8 = DOK_STAF)', DOK_STAF.aturanToko.indexOf('hargaTingkat') >= 0 && DOK_STAF.aturanToko.indexOf('produkArsip') >= 0);

// ---- B · rumus harga
var SET = { id: 'hargaTingkat', tingkat: [{ id: 'warung', nama: 'Warung', potKg: 300 }, { id: 'catering', nama: 'Catering', potKg: 500 }, { id: 'instansi', nama: 'Instansi', potKg: 0 }],
  barang: { warung: { 'kemasan|Kembang|5': 70000 } }, orang: { 'bu suti': 'warung', 'deka': 'catering' },
  khusus: [{ id: 'k1', orang: 'deka', nama: 'Deka', barang: 'karung|Angsa|50', harga: 650000, mulai: '2026-11-01', sampai: '2026-11-30', catatan: 'kontrak' }] };
pasok('aturanToko', [JSON.parse(J(SET))]);
var H1 = htHarga({ orang: 'Bu Suti', barang: 'karung|Angsa|50', eceran: 690000, kg: 50, tanggal: '2026-11-16' });
ok('B: Warung karung Angsa 50 = 690.000 − 300 × 50 = 675.000 (potongan tingkat)', H1 && H1.harga === 675000 && H1.sumber === 'tingkat' && H1.nama === 'Warung' && H1.potongan === 15000, J(H1));
var H2 = htHarga({ orang: 'bu suti', barang: 'kemasan|Kembang|5', eceran: 72000, kg: 5 });
ok('B: harga SENDIRI barang di tingkatnya menang atas potongan (Kembang 5 kg Warung 70.000)', H2 && H2.harga === 70000 && H2.sumber === 'barang', J(H2));
var H3 = htHarga({ orang: 'BU SUTI ', barang: 'literan|Angsa', eceran: 13500, kg: 0.82 });
ok('B: literan: potongan 300 × 0,82 = 246 → dibulatkan Rp50 = 250 → 13.250; nama tak peduli huruf/spasi', H3 && H3.harga === 13250 && H3.potongan === 250, J(H3));
var H4 = htHarga({ orang: 'Deka', barang: 'karung|Angsa|50', eceran: 690000, kg: 50, tanggal: '2026-11-16' });
ok('B: harga KHUSUS yang berlaku hari itu menang atas tingkat (Deka 650.000, idnya tercatat)', H4 && H4.harga === 650000 && H4.sumber === 'khusus' && H4.khususId === 'k1' && H4.id === 'catering', J(H4));
var H5 = htHarga({ orang: 'Deka', barang: 'karung|Angsa|50', eceran: 690000, kg: 50, tanggal: '2026-12-01' });
ok('B: harga khusus yang sudah LEWAT tidak dipakai → potongan Catering 500 × 50 → 665.000', H5 && H5.harga === 665000 && H5.sumber === 'tingkat', J(H5));
ok('B: harga khusus yang BELUM mulai tidak dipakai', htHarga({ orang: 'Deka', barang: 'karung|Angsa|50', eceran: 690000, kg: 50, tanggal: '2026-10-31' }).sumber === 'tingkat');
ok('B: tingkat potongan 0 tetap tercatat (harga = eceran) supaya nota menyebut tingkat pembelinya', (function () { pasok('aturanToko', [Object.assign({}, SET, { orang: { 'bu suti': 'instansi' } })]); var x = htHarga({ orang: 'Bu Suti', barang: 'karung|Angsa|50', eceran: 690000, kg: 50 }); pasok('aturanToko', [JSON.parse(J(SET))]); return x && x.harga === 690000 && x.nama === 'Instansi'; })());
ok('B: wadah / kantong tidak pernah diberi harga tingkat', htHarga({ orang: 'Bu Suti', barang: 'wadah|5kg_kembang', eceran: 2000, kg: 0 }) === null);
ok('B: potongan yang menghabiskan harga → tidak dipakai (eceran)', htHarga({ orang: 'Bu Suti', barang: 'karung|Angsa|50', eceran: 10000, kg: 50 }) === null);

// ---- C · Jual
var s = keadaanAwal(); s.sekarang = new Date('2026-11-16T10:00:00');
function terap(p) { s = Object.assign({}, s, p); sinkronKeranjang(s); return p; }
function chip(jalur, kunci, berat) { var r = susunRak(s); return r[jalur].find(function (c) { return c.kunci === kunci && (!berat || c.berat === berat); }); }
var c0 = chip('karung', 'Angsa', 50);
ok('C: tanpa nama: chip tanpa harga tingkat', c0.harga === 690000 && c0.hargaTingkat === undefined && !c0.tingkatNama, J(c0));
terap(gantiPelanggan(s, 'Bu Suti'));
var c1 = chip('karung', 'Angsa', 50);
ok('C: pembeli Bu Suti (Warung): chip menyebut 675.000 & Warung, harga eceran chip TETAP 690.000', c1.harga === 690000 && c1.hargaTingkat === 675000 && c1.tingkatNama === 'Warung', J(c1));
ok('C: chip Sering (salinan rak) ikut membawa harga tingkat', susunRak(s).sering.every(function (c) { return c.jalur === 'wadah' || c.hargaTingkat !== undefined; }), J(susunRak(s).sering));
ok('C: keterangan pembeli di Jual: harga Warung, eceran − Rp300/kg', (function () { var T = tingkatPembeli('Bu Suti', s.sekarang); return T && T.nama === 'Warung' && /300/.test(T.teks); })(), J(tingkatPembeli('Bu Suti', s.sekarang)));
ok('C: daftar nama pembeli menyebut tingkatnya', daftarPelanggan('suti').some(function (o) { return o.tingkat === 'Warung'; }), J(daftarPelanggan('suti')));
terap(ketukChip(s, c1)); terap(tekanTuts(s, '2')); terap(masukkan(s));
var b1 = s.keranjang[0].trx;
ok('C: 2 karung Angsa untuk Bu Suti: harga dasar 675.000 (hargaAsli), total 1.350.000, eceran 690.000 tercatat, tingkat Warung',
  b1.hargaAsli === 675000 && b1.hargaSatuan === 675000 && b1.hargaTotal === 1350000 && b1.hargaEceranSatuan === 690000 && b1.tingkatHarga === 'Warung' && b1.tingkatId === 'warung' && b1.hargaSumber === 'tingkat', J(b1));
var hpp1 = b1.hppTotalSaatJual;
terap(ubahJumlahBaris(s, s.keranjang[0].id, 1));
ok('C: +1 karung mempertahankan harga Warung (baris dibangun ulang dari chip & pembelinya)', s.keranjang[0].trx.hargaSatuan === 675000 && s.keranjang[0].trx.hargaTotal === 2025000 && s.keranjang[0].trx.tingkatHarga === 'Warung', J(s.keranjang[0].trx));
terap(ubahJumlahBaris(s, s.keranjang[0].id, -1));
var g0 = gantiPelanggan(s, '');
ok('C: pembeli dilepas → keranjang kembali ke eceran 690.000, kolom tingkat hilang, kabar menyebut perubahannya, uang dikosongkan',
  g0.keranjang[0].trx.hargaSatuan === 690000 && g0.keranjang[0].trx.tingkatHarga === undefined && g0.keranjang[0].trx.hargaEceranSatuan === undefined && /675\.000 → Rp690\.000|675.000 → Rp 690.000|→/.test(g0.kabar) && g0.uang === 0, J(g0));
var g1 = gantiPelanggan(s, 'Deka');
ok('C: pembeli diganti ke Deka → harga KHUSUS 650.000 (sumber khusus, id k1)', g1.keranjang[0].trx.hargaSatuan === 650000 && g1.keranjang[0].trx.hargaSumber === 'khusus' && g1.keranjang[0].trx.hargaKhususId === 'k1', J(g1.keranjang[0].trx));
ok('C: ganti ke nama yang sama harganya tidak mengubah apa pun (tanpa kabar)', !gantiPelanggan(s, 'bu suti').kabar);
// nego di atas harga tingkat (owner)
var sN = Object.assign({}, s, { negoAkun: OWN, negoHak: 'sendiri', negoBisaMinta: true });
var pN = putusNego(sN, s.keranjang[0].id, 670000);
ok('C: nego owner 670.000 dihitung dari harga Warung 675.000 (bukan eceran 690.000)', pN.hargaAsli === 675000 && pN.status === 'jatah', J(pN));
var tN = terapkanNego(sN, s.keranjang[0].id, 670000); terap(tN);
ok('C: baris bernego tetap membawa tingkatnya', s.keranjang[0].trx.hargaSatuan === 670000 && s.keranjang[0].trx.nego && s.keranjang[0].trx.tingkatHarga === 'Warung', J(s.keranjang[0].trx));
var D = susunNotaDokumen(Object.assign({}, s, { cara: 'QRIS' }), W).dokumen.filter(function (x) { return x.koleksi === 'penjualan'; });
ok('C: dokumen nota: hargaAsliSatuan = harga Warung, negoSelisih dari harga Warung, eceran & tingkat tercatat, modal tidak berubah karena tingkat',
  D.length === 1 && D[0].data.hargaAsliSatuan === 675000 && D[0].data.negoSelisih === -5000 && D[0].data.hargaEceranSatuan === 690000 && D[0].data.tingkatHarga === 'Warung' && D[0].data.namaPelanggan === 'Bu Suti' && D[0].data.hppTotalSaatJual === hpp1, J(D[0] && D[0].data));
ok('C: kunci barang chip = kunci baris nota (dipakai harga sendiri & khusus)', htKunciChip(c1) === ngKunciBarang(b1) && htKunciChip(chip('kemasan', s.keranjang.length ? 'Kembang|5' : 'Kembang|5')) === 'kemasan|Kembang|5', htKunciChip(c1) + ' / ' + ngKunciBarang(b1));
// kemasan harga sendiri & literan lewat masukkan
var s2 = keadaanAwal(); s2.sekarang = s.sekarang; s2 = Object.assign(s2, gantiPelanggan(s2, 'Bu Suti')); s = s2; sinkronKeranjang(s);
var ck = susunRak(s).kemasan[0]; terap(ketukChip(s, ck)); terap(tekanTuts(s, '1')); terap(masukkan(s));
ok('C: Kembang 5 kg untuk Bu Suti = harga sendiri 70.000 (sumber barang)', s.keranjang[0].trx.hargaSatuan === 70000 && s.keranjang[0].trx.hargaSumber === 'barang', J(s.keranjang[0].trx));
var cl = susunRak(s).literan[0]; terap(ketukChip(s, cl)); terap(tekanTuts(s, '2')); terap(masukkan(s));
ok('C: literan Angsa 2 L untuk Bu Suti = 13.250/L', s.keranjang[1].trx.hargaSatuan === 13250 && s.keranjang[1].trx.hargaTotal === 26500, J(s.keranjang[1].trx));

// ---- D · ubah setelan (htTerapkan)
var A = htAtur();
var t1 = htTerapkan(A, { jenis: 'tingkat', tingkat: [{ id: 'warung', nama: 'Warung', potKg: '300' }, { id: '', nama: 'warung', potKg: '0' }] });
ok('D: nama tingkat dua kali ditolak (tanpa peduli huruf besar)', /dua kali/.test(t1.tolak || ''), J(t1));
ok('D: potongan negatif / bukan angka / pecahan ditolak', /bulat/.test(htTerapkan(A, { jenis: 'tingkat', tingkat: [{ nama: 'A1', potKg: '-5' }] }).tolak || '') && /bulat/.test(htTerapkan(A, { jenis: 'tingkat', tingkat: [{ nama: 'A1', potKg: 'x' }] }).tolak || '') && /bulat/.test(htTerapkan(A, { jenis: 'tingkat', tingkat: [{ nama: 'A1', potKg: '12,5' }] }).tolak || ''));
ok('D: potongan di atas Rp10.000/kg ditolak', /paling besar/.test(htTerapkan(A, { jenis: 'tingkat', tingkat: [{ nama: 'A1', potKg: '10050' }] }).tolak || ''));
var t2 = htTerapkan(A, { jenis: 'tingkat', tingkat: [{ id: 'catering', nama: 'Catering', potKg: '500' }, { id: 'instansi', nama: 'Instansi', potKg: '0' }] });
ok('D: menghapus tingkat yang masih dipakai pelanggan DITOLAK (tidak dipindah diam-diam)', /masih dipakai 1 pelanggan/.test(t2.tolak || ''), J(t2));
var t3 = htTerapkan(A, { jenis: 'tingkat', tingkat: [{ id: 'warung', nama: 'Warung Kecil', potKg: '1.000' }, { id: 'catering', nama: 'Catering', potKg: '500' }, { id: '', nama: 'Grosir Besar', potKg: '700' }] });
ok('D: ganti nama mempertahankan id (pelanggannya tetap), "1.000" dibaca 1000, tingkat baru dapat id dari namanya, tingkat kosong yang dihapus ikut hilang',
  !t3.tolak && t3.A.tingkat.map(function (t) { return t.id + ':' + t.potKg; }).join() === 'warung:1000,catering:500,grosir-besar:700' && t3.A.orang['bu suti'] === 'warung', J(t3));
ok('D: harga barang: 0 / kosong = kembali ikut potongan; bukan angka ditolak; tingkat tak ada ditolak; wadah ditolak',
  !htTerapkan(A, { jenis: 'barang', tingkatId: 'warung', barang: 'kemasan|Kembang|5', harga: '' }).A.barang.warung && /bulat/.test(htTerapkan(A, { jenis: 'barang', tingkatId: 'warung', barang: 'kemasan|Kembang|5', harga: 'abc' }).tolak || '')
  && /tidak ada/.test(htTerapkan(A, { jenis: 'barang', tingkatId: 'x', barang: 'kemasan|Kembang|5', harga: '1000' }).tolak || '') && /tidak dikenali/.test(htTerapkan(A, { jenis: 'barang', tingkatId: 'warung', barang: 'wadah|x', harga: '1000' }).tolak || ''));
ok('D: pasang pelanggan ke tingkat yang sama ditolak; kosong = kembali eceran', /sudah di tingkat/.test(htTerapkan(A, { jenis: 'orang', orang: 'Bu Suti', tingkatId: 'warung' }).tolak || '') && !htTerapkan(A, { jenis: 'orang', orang: 'Bu Suti', tingkatId: '' }).A.orang['bu suti']);
ok('D: harga khusus: sampai sebelum mulai ditolak; harga 0 ditolak; ubah lewat id mempertahankan id',
  /lebih awal/.test(htTerapkan(A, { jenis: 'khusus', orang: 'Deka', barang: 'karung|Angsa|50', harga: '600000', mulai: '2026-11-10', sampai: '2026-11-01' }).tolak || '')
  && /lebih dari 0/.test(htTerapkan(A, { jenis: 'khusus', orang: 'Deka', barang: 'karung|Angsa|50', harga: '0', mulai: '2026-11-10' }).tolak || '')
  && htTerapkan(A, { jenis: 'khusus', id: 'k1', orang: 'Deka', barang: 'karung|Angsa|50', harga: '640000', mulai: '2026-11-01', sampai: '' }, W).A.khusus.filter(function (x) { return x.id === 'k1' && x.harga === 640000 && x.sampai === ''; }).length === 1);
var banyak = JSON.parse(J(SET)); banyak.khusus = []; for (var i = 0; i < HT_MAKS_KHUSUS; i++) banyak.khusus.push({ id: 'z' + i, orang: 'deka', nama: 'Deka', barang: 'karung|Angsa|50', harga: 1000 + i, mulai: '2026-01-01', sampai: '2026-01-02' });
ok('D: paling banyak ' + HT_MAKS_KHUSUS + ' harga khusus — yang ke-' + (HT_MAKS_KHUSUS + 1) + ' ditolak', /hapus yang sudah lewat/.test(htTerapkan(htAtur(banyak), { jenis: 'khusus', orang: 'Deka', barang: 'karung|Angsa|50', harga: '5', mulai: '2026-11-01' }, W).tolak || ''));

// ---- E · siapa boleh menulis
var ro = htSusun(OWN, { jenis: 'orang', orang: 'Deka', nama: 'Deka', tingkatId: 'warung' }, W, { hak: 'sendiri' });
ok('E: owner → setelan aturanToko/hargaTingkat ditulis langsung, bertanggal', ro.dokumen && ro.dokumen.length === 1 && ro.dokumen[0].koleksi === 'aturanToko' && ro.dokumen[0].data.id === 'hargaTingkat' && ro.dokumen[0].data.orang.deka === 'warung' && ro.dokumen[0].data.tanggal === '2026-11-16', J(ro));
var rb = htSusun(BEN, { jenis: 'orang', orang: 'Deka', nama: 'Deka', tingkatId: 'warung' }, W, { hak: 'owner', bisaMinta: true });
var ub = rb.dokumen && rb.dokumen[0].data;
ok('E: Ben → USUL ke owner (persetujuan hargaPelanggan, menunggu, usulUid = uid Ben, tanpa kolom keputusan), setelan TIDAK ditulis',
  rb.dokumen && rb.dokumen.length === 1 && rb.dokumen[0].koleksi === 'persetujuan' && ub.tindakan === 'hargaPelanggan' && ub.status === 'menunggu' && ub.usulUid === 'uid-ben' && !('diputusPada' in ub) && /Catering → Warung/.test(ub.teks), J(rb));
ok('E: penjaga kiriman menerima usul Ben (bentuk = rules v8)', !kirim(BEN, rb.dokumen).tolak, J(kirim(BEN, rb.dokumen)));
ok('E: penjaga menolak usul atas nama orang lain / sudah "disetujui" / membawa kolom keputusan',
  kirim(BEN, [{ koleksi: 'persetujuan', data: Object.assign({}, ub, { usulUid: 'uid-kry' }) }]).tolak && kirim(BEN, [{ koleksi: 'persetujuan', data: Object.assign({}, ub, { status: 'disetujui' }) }]).tolak
  && kirim(BEN, [{ koleksi: 'persetujuan', data: Object.assign({}, ub, { diputusPada: 'x' }) }]).tolak);
ok('E: penjaga menolak Ben menulis setelan langsung', !!kirim(BEN, ro.dokumen).tolak);
ok('E: karyawan (kisi "tidak boleh") ditolak dengan kalimat', /tidak boleh mengatur harga/.test(htSusun(KRY, { jenis: 'orang', orang: 'Deka', tingkatId: 'warung' }, W, { hak: 'tidak' }).tolak || ''));
ok('E: penjaga menolak usul dari karyawan (kisi tidak boleh)', !!kirim(KRY, [{ koleksi: 'persetujuan', data: Object.assign({}, ub, { usulUid: 'uid-kry', olehUid: 'uid-kry' }) }]).tolak);
ok('E: server belum membuka usul → kalimat menyebut aturan v8, tanpa kiriman', /aturan v8/.test(htSusun(BEN, { jenis: 'orang', orang: 'Deka', tingkatId: 'warung' }, W, { hak: 'owner', bisaMinta: false }).tolak || ''));
ok('E: usul yang tidak sah langsung ditolak di perangkat Ben (tidak dikirim)', /sudah di tingkat/.test(htSusun(BEN, { jenis: 'orang', orang: 'Bu Suti', tingkatId: 'warung' }, W, { hak: 'owner' }).tolak || ''));

// ---- F · papan persetujuan owner
var USUL = Object.assign({}, ub, { teks: 'PALSU — semua gratis', olehUid: 'uid-ben' });
pasok('persetujuan', [USUL]);
var PS = ssPersetujuan(new Date('2026-11-16T10:00:00'));
var bu = PS.menunggu.find(function (m) { return m.id === String(USUL.id); });
ok('F: papan owner menghitung ULANG kalimat usul (bukan teks kiriman), tidak ikut "setujui sekaligus"', bu && /Catering → Warung/.test(bu.teks) && bu.teks.indexOf('PALSU') < 0 && bu.sekaligus === false && bu.namaTindakan.indexOf('harga pelanggan') >= 0, J(bu));
var sk = susunSetujuiKecil(W);
ok('F: "setujui sekaligus" tidak menyetujui usul harga', !(sk.dokumen || []).some(function (d) { return d.data.tindakan === 'hargaPelanggan'; }), J(sk));
var pu = susunPutusPersetujuan(USUL.id, true, '', W);
var pd = (pu.dokumen || []).find(function (d) { return d.koleksi === 'aturanToko'; });
ok('F: menyetujui = status disetujui + setelan dipasang di kiriman yang sama (dihitung atas setelan sekarang)', pu.dokumen && pu.dokumen.length === 2 && pu.dokumen[0].data.status === 'disetujui' && pd && pd.data.orang.deka === 'warung' && pd.data.orang['bu suti'] === 'warung' && /dipasang/.test(pu.patch.kabar), J(pu));
var pt = susunPutusPersetujuan(USUL.id, false, 'belum perlu', W);
ok('F: menolak tidak menyentuh setelan', pt.dokumen.length === 1 && pt.dokumen[0].koleksi === 'persetujuan' && pt.dokumen[0].data.status === 'ditolak');
pasok('aturanToko', [Object.assign(JSON.parse(J(SET)), { orang: { 'bu suti': 'warung', 'deka': 'warung' } })]);
var pb = susunPutusPersetujuan(USUL.id, true, '', W);
ok('F: usul yang sudah tidak sah lagi (Deka sudah Warung) tidak bisa dipasang — owner diminta menolak', /tidak bisa dipasang lagi/.test(pb.tolak || ''), J(pb));
pasok('aturanToko', [JSON.parse(J(SET))]);
ok('F: Ben melihat usulnya sendiri (status menunggu)', htUsulSaya(BEN).length === 1 && htUsulSaya(BEN)[0].status === 'menunggu' && htUsulSaya(KRY).length === 0);
pasok('persetujuan', []);

// ---- G · papan Usaha
var rakB = rakBarang();
var PO = htPapanBarang('warung', rakB, { owner: true }); var PSf = htPapanBarang('warung', rakB, { owner: false });
var rk = PO.find(function (x) { return x.barang === 'karung|Angsa|50'; }); var rkS = PSf.find(function (x) { return x.barang === 'karung|Angsa|50'; });
ok('G: papan barang Warung: karung Angsa 50 eceran 690.000 → 675.000, modal & untung untuk OWNER', rk && rk.eceran === 690000 && rk.harga === 675000 && rk.modal > 0 && rk.untung === 675000 - rk.modal, J(rk));
ok('G: staf TIDAK melihat modal / untung / tanda modal', rkS && rkS.modal === null && rkS.untung === null && PSf.every(function (x) { return ['rugi', 'nol', 'tanpaModal'].indexOf(x.tanda) < 0; }), J(PSf));
ok('G: barang berharga sendiri ditandai', PO.some(function (x) { return x.barang === 'kemasan|Kembang|5' && x.sendiri === 70000 && x.harga === 70000; }));
pasok('aturanToko', [Object.assign(JSON.parse(J(SET)), { tingkat: [{ id: 'warung', nama: 'Warung', potKg: 2000 }, { id: 'catering', nama: 'Catering', potKg: 500 }] })]);
ok('G: potongan besar → baris DI BAWAH MODAL ditandai rugi (owner)', htPapanBarang('warung', rakBarang(), { owner: true }).some(function (x) { return x.tanda === 'rugi'; }), J(htPapanBarang('warung', rakBarang(), { owner: true })));
pasok('aturanToko', [JSON.parse(J(SET))]);
ok('G: harga sendiri di atas eceran ditandai "di atas harga eceran"', (function () { pasok('aturanToko', [Object.assign(JSON.parse(J(SET)), { barang: { warung: { 'kemasan|Kembang|5': 80000 } } })]); var x = htPapanBarang('warung', rakBarang(), { owner: false }).find(function (y) { return y.barang === 'kemasan|Kembang|5'; }); pasok('aturanToko', [JSON.parse(J(SET))]); return x && x.tanda === 'naik'; })());
ok('G: peringatan HET dari fungsi owner ikut di baris', htPapanBarang('warung', rakB, { owner: true, het: function (m, perKg) { return m === 'Angsa' && perKg > 13000 ? 'di atas HET contoh' : ''; } }).some(function (x) { return x.het === 'di atas HET contoh'; }));
var PT = htPapanTingkat(htAtur(), function (k) { return k === 'bu suti' ? 'Bu Suti' : k; });
ok('G: papan tingkat: Warung 1 pelanggan (Bu Suti) + 1 harga sendiri; contoh potongan per satuan', PT[0].nOrang === 1 && PT[0].orang[0].nama === 'Bu Suti' && PT[0].nSendiri === 1 && /15\.000/.test(PT[0].contoh), J(PT[0]));
var PK = htPapanKhusus('', '2026-12-05');
ok('G: harga khusus berlaku / belum / lewat per tanggal', PK[0].keadaan === 'lewat' && htPapanKhusus('deka', '2026-11-16')[0].keadaan === 'berlaku' && htPapanKhusus('deka', '2026-10-01')[0].keadaan === 'belum');

// ---- H · nego di papan owner memakai harga pelanggan
var QM = ngPeriksaMinta({ tindakan: 'nego', barang: 'karung|Angsa|50', hargaMinta: 660000, jumlah: 1, pelanggan: 'bu suti', tingkatHarga: 'Warung' });
ok('H: permintaan nego untuk pembeli Warung: dasar 675.000 (harga Warung), potongan 15.000 — bukan 30.000 dari eceran', QM.katalog === 675000 && QM.nominal === 15000 && /harga Warung/.test(QM.teks), J(QM));
ok('H: permintaan nego tanpa pembeli bertingkat tetap dari katalog', ngPeriksaMinta({ tindakan: 'nego', barang: 'karung|Angsa|50', hargaMinta: 660000, jumlah: 1 }).katalog === 690000);

// ---- I · kartu pelanggan
var ki = susunSimpanKartu(new Date('2026-11-16T10:00:00'), 'bu suti', { nama: 'Bu Suti', cip: [], catatan: 'warung depan pasar', arah: '', asli: '', kontak: '', biasa: '', alamat: 'Jl. Contoh 1', npwp: '12.345' }, W);
ok('I: NPWP bukan 15/16 angka ditolak', /15 atau 16 angka/.test(ki.tolak || ''), J(ki));
var ki2 = susunSimpanKartu(new Date('2026-11-16T10:00:00'), 'bu suti', { nama: 'Bu Suti', cip: [], catatan: 'warung depan pasar', arah: '', asli: '', kontak: '', biasa: '', alamat: 'Jl. Contoh 1', npwp: '01.234.567.8-901.000' }, W);
ok('I: alamat antar & NPWP 15 angka tersimpan di kartu', ki2.dokumen && ki2.dokumen[0].data.alamat === 'Jl. Contoh 1' && ki2.dokumen[0].data.npwp === '01.234.567.8-901.000', J(ki2));
// ---- J · SARAN HARGA GROSIR per jumlah karung (owner 24 Nov 2026: per merek, tidak ditumpuk, owner saja)
var SETG = Object.assign(JSON.parse(J(SET)), { grosir: { 'karung|Angsa|50': [{ min: 10, harga: 660000 }, { min: 5, harga: 670000 }, { min: 1, harga: 1 }, { min: 7, harga: -5 }], 'kemasan|Kembang|5': [{ min: 5, harga: 60000 }] } });
pasok('aturanToko', [SETG]);
var AG = htAtur();
ok('J: setelan dibersihkan: jenjang sah saja (min ≥ 2, harga > 0), urut naik; bukan karung dibuang', J(AG.grosir) === J({ 'karung|Angsa|50': [{ min: 5, harga: 670000 }, { min: 10, harga: 660000 }] }), J(AG.grosir));
ok('J: jenjang yang berlaku = min terbesar yang tercapai', htGrosir('karung|Angsa|50', 4) === null && htGrosir('karung|Angsa|50', 5).harga === 670000 && htGrosir('karung|Angsa|50', 12).harga === 660000 && htGrosir('karung|Angsa|25', 12) === null);
var TG1 = htTerapkan(AG, { jenis: 'grosir', barang: 'karung|Angsa|50', jenjang: [{ min: '5', harga: '670.000' }, { min: '10', harga: '680.000' }] }, W);
ok('J: jenjang lebih banyak lebih MAHAL ditolak; bukan karung ditolak; min 1 ditolak', /tidak boleh lebih mahal/.test(TG1.tolak || '') && /karung utuh/.test(htTerapkan(AG, { jenis: 'grosir', barang: 'kemasan|Kembang|5', jenjang: [{ min: 5, harga: 1 }] }, W).tolak || '')
  && /bilangan bulat 2/.test(htTerapkan(AG, { jenis: 'grosir', barang: 'karung|Angsa|50', jenjang: [{ min: 1, harga: 600000 }] }, W).tolak || ''), J(TG1));
var SG = htSusun(OWN, { jenis: 'grosir', barang: 'karung|IR64 Apex|50', jenjang: [{ min: '3', harga: '720.000' }] }, W);
ok('J: owner menyimpan jenjang → dokumen hargaTingkat membawa grosir + yang lama tetap', SG.dokumen && SG.dokumen[0].data.grosir['karung|IR64 Apex|50'][0].harga === 720000 && SG.dokumen[0].data.grosir['karung|Angsa|50'].length === 2 && SG.dokumen[0].data.tingkat.length === 3, J(SG.tolak || SG.dokumen[0].data.grosir));
ok('J: Ben tidak bisa mengatur harga grosir (owner saja, bukan usul)', /owner saja/.test(htSusun(BEN, { jenis: 'grosir', barang: 'karung|Angsa|50', jenjang: [] }, W, { hak: 'owner', bisaMinta: true }).tolak || ''));
var SG2 = htSusun(OWN, { jenis: 'tingkat', tingkat: AG.tingkat }, W);
ok('J: ubahan lain (tingkat) tidak membuang harga grosir', SG2.dokumen && SG2.dokumen[0].data.grosir['karung|Angsa|50'].length === 2, J(SG2.tolak || SG2.dokumen[0].data.grosir));
// Jual: pembeli tanpa tingkat, 5 karung Angsa → saran grosir 670.000 (eceran 690.000)
s = keadaanAwal(); s.sekarang = new Date('2026-11-16T10:00:00'); sinkronKeranjang(s);
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap(tekanTuts(s, '5')); terap(masukkan(s));
var bG = s.keranjang[0]; var SR = saranGrosir(bG);
ok('J: 5 karung eceran → saran "pakai harga grosir" 670.000, hemat 100.000', SR && SR.harga === 670000 && SR.min === 5 && SR.hemat === 100000, J(SR));
terap(toggleGrosir(s, bG.id)); var tG = s.keranjang[0].trx;
ok('J: diketuk → harga dasar 670.000, total 3.350.000, tercatat grosir ≥ 5, eceran tetap tercatat', tG.hargaAsli === 670000 && tG.hargaSatuan === 670000 && tG.hargaTotal === 3350000 && tG.hargaSumber === 'grosir' && tG.grosirMin === 5 && tG.hargaEceranSatuan === 690000 && tG.pakaiGrosir === true, J(tG));
terap(ubahJumlahBaris(s, s.keranjang[0].id, 5)); var t10 = s.keranjang[0].trx;
ok('J: naik ke 10 karung → jenjang ≥ 10 (660.000) otomatis', t10.hargaAsli === 660000 && t10.grosirMin === 10, J(t10));
terap(ubahJumlahBaris(s, s.keranjang[0].id, -6)); var t4 = s.keranjang[0].trx;
ok('J: turun ke 4 karung (di bawah jenjang) → harga biasa lagi, tanda grosir tetap menunggu', t4.hargaAsli === 690000 && t4.hargaSumber !== 'grosir' && !t4.grosirMin && t4.pakaiGrosir === true, J(t4));
terap(ubahJumlahBaris(s, s.keranjang[0].id, 1));
var DG = susunNotaDokumen(Object.assign({}, s, { cara: 'QRIS' }), W).dokumen.filter(function (x) { return x.koleksi === 'penjualan'; }).map(function (x) { return x.data; });
ok('J: dokumen nota: hargaAsliSatuan 670.000, hargaSumber grosir, grosirMin 5; tanda keranjang tidak ikut tersimpan', DG.length === 1 && DG[0].hargaAsliSatuan === 670000 && DG[0].hargaSumber === 'grosir' && DG[0].grosirMin === 5 && !('pakaiGrosir' in DG[0]), J(DG));
var SETT0 = Object.assign(JSON.parse(J(SETG)), { tingkat: [{ id: 'warung', nama: 'Warung', potKg: 600 }, { id: 'catering', nama: 'Catering', potKg: 500 }, { id: 'instansi', nama: 'Instansi', potKg: 0 }] });
pasok('aturanToko', [SETT0]); terap(gantiPelanggan(s, 'Bu Suti'));
ok('J: tanda grosir menyala tapi pembeli Warung (660.000) lebih murah dari grosir (670.000) → harga Warung dipakai, TIDAK ditumpuk', s.keranjang[0].trx.hargaAsli === 660000 && s.keranjang[0].trx.hargaSumber === 'tingkat' && !s.keranjang[0].trx.grosirMin, J(s.keranjang[0].trx));
pasok('aturanToko', [SETG]); terap(gantiPelanggan(s, ''));
terap(toggleGrosir(s, s.keranjang[0].id));
ok('J: diketuk lagi → kembali harga biasa', s.keranjang[0].trx.hargaAsli === 690000 && !s.keranjang[0].trx.pakaiGrosir);
// tidak ditumpuk: pembeli bertingkat yang harganya sudah lebih murah dari grosir → tidak ada saran
var SETT = Object.assign(JSON.parse(J(SETG)), { tingkat: [{ id: 'warung', nama: 'Warung', potKg: 600 }, { id: 'catering', nama: 'Catering', potKg: 500 }, { id: 'instansi', nama: 'Instansi', potKg: 0 }] });
pasok('aturanToko', [SETT]); terap(gantiPelanggan(s, 'Bu Suti'));
ok('J: Bu Suti Warung (690.000 − 600×50 = 660.000) sudah lebih murah dari grosir 670.000 → TIDAK ada saran (tidak ditumpuk)', s.keranjang[0].trx.hargaAsli === 660000 && saranGrosir(s.keranjang[0]) === null, J([s.keranjang[0].trx.hargaAsli, saranGrosir(s.keranjang[0])]));
terap(ubahJumlahBaris(s, s.keranjang[0].id, 5));
ok('J: 10 karung Bu Suti: grosir 660.000 = harga Warung 660.000 → tidak ada saran (harus LEBIH murah)', saranGrosir(s.keranjang[0]) === null);
pasok('aturanToko', [JSON.parse(J(SET))]);
print(J({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('layar Pelanggan punya keluarga Usaha (tingkat · harga barang · harga khusus) & bagian harga di kartu', 'pelanggan',
     ["['grosir', 'Harga grosir']", 'function gambarUGrosir(s, A, owner)', 'data-aksi="uSimpanG"', "susunHT({ jenis: 'grosir', barang: g.barang, jenjang: g.jenjang })", "['usaha', 'Usaha']", "['tingkat', 'Tingkat'], ['barang', 'Harga barang'], ['khusus', 'Harga khusus']", "function gambarUsaha(s, d)", "${gambarHargaKartu(d)}", "data-aksi=\"uSimpanT\"", "data-aksi=\"uSimpanK\"", "data-kolom=\"npwp\"", "data-kolom=\"alamat\""]),
    ('isian Usaha yang belum disimpan ikut penjaga ganti orang', 'pelanggan', ["'titip', 'uEdit', 'uBarang', 'uKhusus', 'uGrosir'"]),
    ('Jual: baris karung menawarkan "pakai harga grosir" (saranGrosir) & ketukannya', 'jual', ["grosir: ({ id }) => set(L.toggleGrosir(SBN(), id)),", 'const G = L.saranGrosir(b);', 'data-aksi="grosir"']),
    ('tombol Usaha berkata KIRIM USUL untuk bukan-owner', 'pelanggan', ["${owner ? 'SIMPAN' : 'KIRIM USUL'}"]),
    ('Jual: chip & lembar jumlah memakai harga tingkat, pita pembeli & tingkat di daftar nama', 'jual',
     ["${RP(c.hargaTingkat || c.harga)}", "tingkat-ket", "L.tingkatPembeli(s.pelanggan, s.sekarang)", "o.tingkat ? h`", "RP((c.hargaTingkat || c.harga) * L.angkaKetik(s.ketik))"]),
    ('Jual: pilih / lepas / ketik / benang pembeli menghitung ulang keranjang', 'jual',
     ["pilihPelanggan: ({ nama }) => set(Object.assign({ lembar: null, cariPelanggan: '', kabar: '' }, L.gantiPelanggan(SBN(), nama)))", "lepasPelanggan: () => set(Object.assign({ kabar: '' }, L.gantiPelanggan(SBN(), '')))", "L.gantiPelanggan(SBN(), n)", "const g = L.gantiPelanggan(SBN(), nama)"]),
    ('modul harga tingkat dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/harga-tingkat-logika.js">']),
    ('CI menjalankan uji ini (+ kontrol)', 'pages', ['python3 alat-uji/uji_harga_tingkat.py && python3 alat-uji/uji_harga_tingkat.py --kontrol']),
    ('rules v8: staf membaca hargaTingkat & produkArsip, usul harga lewat stafUsulHarga', 'rules', ["'perangkat', 'hargaTingkat', 'produkArsip', 'bukuPegangan'] && staf(['ben', 'karyawan'])", "|| stafUsulHarga(['ben', 'karyawan'])", "d.get('tindakan', '') == 'hargaPelanggan'"]),
]

RUSAK = [
    ('potongan tidak dibulatkan ke Rp50', HT, "Math.round((Number(potKg) || 0) * (Number(kg) || 0) / HT_LANGKAH) * HT_LANGKAH", "Math.round((Number(potKg) || 0) * (Number(kg) || 0))"),
    ('harga khusus tanpa memeriksa tanggal', HT, "x.mulai <= t && (!x.sampai || x.sampai >= t)", "true"),
    ('harga sendiri barang diabaikan', HT, "  if (sendiri > 0) return { harga: sendiri,", "  if (false) return { harga: sendiri,"),
    ('harga khusus kalah dari tingkat', HT, "  if (kh) return { harga: kh.harga,", "  if (kh && !T) return { harga: kh.harga,"),
    ('wadah ikut harga tingkat', HT, "const HT_JENIS = ['karung', 'kemasan', 'literan', 'repack'];", "const HT_JENIS = ['karung', 'kemasan', 'literan', 'repack', 'wadah'];"),
    ('baris nota tetap harga eceran', JL, "let hargaDasar = TG.hargaAsli; if (e.pakaiGrosir)", "let hargaDasar = chip.harga; if (e.pakaiGrosir)"),
    # saran harga grosir (owner 24 Nov 2026)
    ('grosir ditumpuk / dipakai walau lebih mahal', JL, "  if (GR && GR.harga < hargaDasar) {", "  if (GR) {"),
    ('saran grosir muncul walau tidak lebih murah', JL, "if (!G || !(G.harga < b.trx.hargaAsli)) return null;", "if (!G) return null;"),
    ('jenjang terkecil yang dipakai (bukan terbesar yang tercapai)', HT, "return J.filter((x) => n >= x.min).sort((a, b) => b.min - a.min)[0] || null; }", "return J.filter((x) => n >= x.min).sort((a, b) => a.min - b.min)[0] || null; }"),
    ('tanda keranjang ikut tersimpan di nota', JL, "'_takaran', 'pakaiGrosir'].forEach((k) => { delete d[k]; });", "'_takaran'].forEach((k) => { delete d[k]; });"),
    ('rebuild melupakan tanda grosir', JL, "upahRepack: t.upahRepack, pakaiGrosir: !!t.pakaiGrosir },", "upahRepack: t.upahRepack },"),
    ('Ben boleh mengatur harga grosir', HT, "  if (u.jenis === 'grosir' && !owner) return { tolak: 'Harga grosir per jumlah karung diatur owner saja' };\n", ""),
    ('ubahan lain membuang harga grosir', HT, "    grosir: htSalin(A.grosir || {}),\n", ""),
    ('jenjang lebih banyak boleh lebih mahal', HT, "for (let i = 1; i < J.length; i++) if (J[i].harga > J[i - 1].harga) return", "for (let i = 1; i < J.length; i++) if (false) return"),

    ('baris nota tidak mencatat eceran & tingkat', JL, "HT_KOLOM_BARIS.forEach((k) => { delete t[k]; }); if (TG.kolom) Object.assign(t, TG.kolom);", "HT_KOLOM_BARIS.forEach((k) => { delete t[k]; });"),
    ('chip rak tidak menyebut harga tingkat', JL, "  htTandaiRak(rak, s.pelanggan, hariIniIso(s.sekarang));", ""),
    ('ganti pembeli tidak menghitung ulang keranjang', JL, "  if (!(s.keranjang || []).length) return patch;", "  return patch;"),
    ('Ben menulis setelan langsung (tanpa usul)', HT, "  const owner = !akun || akun.jenis === 'owner';\n", "  const owner = true;\n"),
    ('kisi "tidak boleh" diabaikan', HT, "  if ((o.hak || 'tidak') === 'tidak') return { tolak:", "  if (false) return { tolak:"),
    ('menghapus tingkat yang dipakai pelanggan dibiarkan', HT, "if (n) return { tolak: 'Tingkat ' + t.nama + ' masih dipakai '", "if (false) return { tolak: 'Tingkat ' + t.nama + ' masih dipakai '"),
    ('papan memajang modal ke staf', HT, "const modal = !o.owner ? null : jl === 'kemasan'", "const modal = jl === 'kemasan'"),
    ('menyetujui usul tidak memasang setelan', SL, "  const HP = setuju && m.tindakan === HT_TINDAKAN ? htPasangUsul(m, w) : null;", "  const HP = null;"),
    ('papan owner memakai teks kiriman usul', SL, "teks: Q ? Q.teks : HU !== null ? HU : KR !== null ? KR : m.teks || ''", "teks: Q ? Q.teks : KR !== null ? KR : m.teks || ''"),   # B2: + permintaan bon (KR)
    ('usul harga ikut "setujui sekaligus"', SL, "    sekaligus: m.tindakan !== 'nego' && m.tindakan !== HT_TINDAKAN && m.tindakan !== FK_TINDAKAN,", "    sekaligus: m.tindakan !== 'nego' && m.tindakan !== FK_TINDAKAN,"),
    ('penjaga menerima usul atas nama orang lain', AK, " || String(d.usulUid || '') !== String(akun.uid || '')) return { tolak: tolakTindakan('hargaPelanggan') };", ") return { tolak: tolakTindakan('hargaPelanggan') };"),
    ('penjaga menerima usul dari kisi "tidak boleh"', AK, " || (hak.hargaPelanggan || 'tidak') === 'tidak'", ""),
    ('nego owner dihitung dari eceran walau pembeli bertingkat', NG, "const katalog = H ? H.harga : eceran;", "const katalog = eceran;"),
    ('NPWP tidak diperiksa', PL, "if (npwp && [15, 16].indexOf(npwpAngka.length) < 0) return { tolak: 'NPWP harus 15 atau 16 angka' };", ""),
    ('kisi bawaan Ben boleh sendiri', SL, "isiUlang: 'sendiri', hargaPelanggan: 'owner', antar:", "isiUlang: 'sendiri', hargaPelanggan: 'sendiri', antar:"),
]
RUSAK_STATIS = [
    ('lembar Usaha tidak ikut penjaga ganti orang', 'pelanggan', "'titip', 'uEdit', 'uBarang', 'uKhusus'", "'titip'"),
    ('chip memakai harga eceran walau pembeli bertingkat', 'jual', "${RP(c.hargaTingkat || c.harga)}", "${RP(c.harga)}"),
]


def jalan(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write("var __KINI = new Date('2026-11-16T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" + js + '\nvar KOTAK = ' + json.dumps(uji_jual_baru.KOTAK) + ';\n' + SKENARIO); p = f.name
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
        print('\nKONTROL: ' + ('semua berbunyi (%d)' % (len(RUSAK) + len(RUSAK_STATIS)) if kode == 0 else 'ADA YANG DIAM / BASI'))
        sys.exit(kode)
    l1, g1 = jalan(teks); l2, g2 = statis(src)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l1, len(g1)))
    for x in g1: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (l2, len(g2)))
    for x in g2: print('   ✗ ' + x)
    sys.exit(0 if not (g1 or g2) else 2)
