#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tutup_tablet.py — TUTUP HARI dari tablet (owner 22 Nov 2026, paket ④; rules v16), dijalankan ASLI di jsc di atas data contoh uji_uang_baru.py (hari ini
19 Sep; penjualan tunai/QRIS/bon pagi), titik kas dokumen 15 Sep, setelan tutup hari owner (kembalian Rp192.500), ditambah pemeriksaan pemasangannya.

Kenapa ada: hitungan laci dari tablet menentukan SELISIH LACI, uang yang dipindah ke brankas, dan TITIK KAS yang jadi patokan besok. Yang paling mahal kalau salah:
tablet yang membocorkan angka "seharusnya" (hitung buta jadi tidak buta), uang ke brankas yang memakai angka kembalian bawaan (bukan angka owner), catatan
yang masuk SESUDAH dihitung (nota jam 21.30 sesudah hitungan 21.00) yang mengubah selisih, brankas yang ditulis padahal Ben tidak memindah uangnya, dan
hitungan yang tetap "menunggu" sesudah hari ditutup.

Yang dipegang:
  · tablet: hitungan per pecahan + receh, TANPA seharusnya / selisih; pindah ke brankas = hitungan − kembalian owner; setelan owner tak terbaca = tidak ditebak
  · kiriman = satu persetujuan hitungLaci (bentuk rules v16), tanggal = hari yang DITUTUP (lewat tengah malam = kemarin); karyawan / kisi "tidak" ditolak
  · owner Pakai → lembar terisi (laci, timbang, amankan; cek QRIS tidak disentuh); laci sekarang = hitungan + uang laci sesudah jam hitung; selisih TIDAK
    berubah oleh catatan sesudah hitungan; brankas = angka tablet; Ben tidak memindah = amankan dilewati (tanpa pindah uang)
  · Tutup: hitungan dipakai = disetujui, hitungan lain hari itu = dibaca; owner menutup sendiri = semuanya dibaca; hitungan yang sudah ditolak tidak bisa dipakai
  · minta hitung ulang = ditolak beralasan, terbaca di tablet; papan Persetujuan tidak bisa "menyetujui" hitungan (hari tidak tertutup diam-diam)
  · Penjaga laci mendengar aturanToko/tutupHari (karyawan tidak); kabar dalam aplikasi & push HP mengenal hitungan laci

    python3 alat-uji/uji_tutup_tablet.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_tutup_tablet.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json, copy, subprocess, tempfile

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru as UB  # noqa: E402
JSC = UB.JSC
HLL = 'baru/js/layar/tutup-tablet-logika.js'; HLP = 'baru/js/layar/tutup-tablet-panel.js'; TDL = 'baru/js/layar/tutup-hari-logika.js'; AK = 'baru/js/data/akses.js'
SL = 'baru/js/layar/sistem-logika.js'; KB = 'baru/js/layar/kabar-baru-logika.js'; UG = 'baru/js/layar/uang.js'; MN = 'baru/js/layar/menu.js'; IDX = 'baru/index.html'
FN = 'functions/pesan.js'; RULES = 'firestore.rules'
# modul Uang (uji_uang_baru, harga-logika ikut — aturTutup memakai aturHarga) + akses, sistem (papan Persetujuan), kabar, logika tablet
MODUL = list(dict.fromkeys(UB.MODUL + ['baru/js/data/hemat-baca.js', 'baru/js/layar/titipan-logika.js', AK, SL, KB, HLL]))
STATIS = [HLP, UG, MN, IDX, FN, RULES]


def kotak():
    K = copy.deepcopy(UB.KOTAK)
    K['pengaturan'] = [{'id': 'titikKas', 'tanggal': '2026-09-15', 'laci': 2000000, 'brankas': 10000000, 'rekening': 3000000, 'amplop': 1000000, 'diubahPada': '2026-09-15T14:00:00.000Z'}]
    # setelan tutup hari OWNER (bukan bawaan 500.000) — angka sungguhan toko 22 Nov 2026: kembalian 192.500, sisihkan 50 %, dimaafkan 5.000
    K['aturanToko'] = [{'id': 'tutupHari', 'tanggal': '2026-09-01', 'jam': '09:00', 'persenSisih': 50, 'kembalian': 192500, 'maafSelisih': 5000, 'alasan': ['Salah kasih kembalian', 'Belum tahu — dicari besok']}]
    K['aksesAkun'] = [{'id': 'uid-tablet', 'uid': 'uid-tablet', 'nama': 'Tablet', 'email': 'tablet@contoh.com', 'peran': 'ben', 'aktif': True}]
    return K


SKENARIO = r"""
var hasil = []; var J = JSON.stringify;
function cek(nama, ok, ket) { hasil.push({ nama: nama, ok: !!ok, ket: ket === undefined ? '' : (typeof ket === 'string' ? ket : J(ket)) }); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var _id = 0; var idU = function () { return 'hl' + (++_id); };
var W = { tanggal: '2026-09-19', jam: '21:00', kini: '2026-09-19T14:00:00.000Z', idUnik: idU };
var WO = { tanggal: '2026-09-19', jam: '22:00', kini: '2026-09-19T15:00:00.000Z', idUnik: idU };   // owner menutup
var K21 = new Date('2026-09-19T21:00:00'); var K22 = new Date('2026-09-19T22:00:00');
var BEN = { jenis: 'aktif', peran: 'ben', nama: 'Penjaga A', operatorId: 'o1', uid: 'uid-tablet' };
var KRY = { jenis: 'aktif', peran: 'karyawan', nama: 'Orang B', uid: 'uid-k' };
var HAK = { hitungLaci: 'sendiri', uangKeluar: 'owner' }; var HAK_TIDAK = { hitungLaci: 'tidak', uangKeluar: 'owner' };
var kirim = function (akun, data, hak) { return periksaKiriman(akun, [{ koleksi: 'persetujuan', data: data, ada: false }], [], hak); };
var simpan = function (r) { (r.dokumen || []).forEach(function (x) { if (x.koleksi !== 'persetujuan') return; var a = cacheMentah('persetujuan').slice(); var i = a.findIndex(function (d) { return String(d.id) === String(x.data.id); }); if (i >= 0) a[i] = x.data; else a.push(x.data); pasok('persetujuan', a); }); };
var dok = function (r, kol, id) { return ((r && r.dokumen) || []).filter(function (x) { return x.koleksi === kol && (id === undefined || String(x.data.id) === String(id)); }).map(function (x) { return x.data; }); };
var DRAF_OWNER = function (p) { return Object.assign({ lembar: {}, receh: 0, alasan: '', rekPilih: '', rekNyata: '', sisih: null, timbang: {}, status: {} }, p || {}); };
var ALASAN = 'Belum tahu — dicari besok';

// ---------- tablet: hitung buta ----------
var D1 = { lembar: { 100000: 5, 50000: 2, 2000: 3 }, receh: '1.500', timbang: {}, amankan: '' };
var H1 = hlHitung(D1, K21);
cek('tablet: hitungan 5×100.000 + 2×50.000 + 3×2.000 + receh 1.500 = Rp607.500, hari 19 Sep', H1.hitung === 607500 && H1.iso === '2026-09-19', [H1.hitung, H1.iso]);
cek('tablet: pindah ke brankas = hitungan − kembalian OWNER 192.500 = Rp415.000 (bukan bawaan 500.000)', H1.amankanBisa === true && H1.kembalian === 192500 && H1.pindah === 415000, [H1.amankanBisa, H1.kembalian, H1.pindah]);
cek('HITUNG BUTA: lembar tablet tidak membawa angka seharusnya / selisih', J(H1).indexOf('seharusnya') < 0 && J(H1).indexOf('selisih') < 0 && !('RL' in H1), Object.keys(H1));
var TB = barangTimbang('2026-09-19').map(function (m) { return m.merk; });
cek('tablet: timbang cepat = barang karung yang keluar hari itu (sama dengan lembar owner)', J(H1.timbang.map(function (m) { return m.merk; })) === J(TB) && TB.indexOf('Angsa') >= 0, [TB, H1.timbang]);
var Rk = hlSusunKirim(D1, BEN, W);
cek('kirim tanpa memilih "sudah / tidak dipindah" ditolak dengan kalimat', /Amankan laci/.test(Rk.tolak || ''), Rk.tolak || Rk);
var D1b = Object.assign({}, D1, { amankan: 'sudah', timbang: { Angsa: '30,5' } });
var R1 = hlSusunKirim(D1b, BEN, W); var M1 = R1.dokumen ? R1.dokumen[0].data : {};
cek('kiriman: SATU persetujuan hitungLaci menunggu, atas nama yang jaga', R1.dokumen && R1.dokumen.length === 1 && R1.dokumen[0].koleksi === 'persetujuan' && M1.tindakan === 'hitungLaci' && M1.status === 'menunggu' && M1.mintaUid === 'uid-tablet' && M1.dari === 'Penjaga A', R1.tolak || M1);
cek('kiriman: hari 19 Sep 21:00, hitungan 607.500, brankas 415.000, lembar & receh, kembalian owner, timbang Angsa 30,5 kg, cek wadah', M1.tanggal === '2026-09-19' && M1.jam === '21:00' && M1.tanggalTulis === '2026-09-19' && M1.hitung === 607500 && M1.amankan === 415000
  && J(M1.lembar) === J({ 100000: 5, 50000: 2, 2000: 3 }) && M1.receh === 1500 && M1.kembalian === 192500 && M1.timbang.length === 1 && M1.timbang[0].merk === 'Angsa' && M1.timbang[0].fisik === 30.5 && !!M1.cekWadah, M1);
cek('kiriman: tanpa kolom keputusan & tanpa angka seharusnya', !['diputusPada', 'diputusTanggal', 'diputusJam', 'alasanTolak', 'balasan', 'koreksiOwner', 'seharusnya', 'selisih'].some(function (k) { return k in M1; }), Object.keys(M1));
cek('penjaga kiriman (= rules v16): Penjaga laci lolos', !kirim(BEN, M1, HAK).tolak, kirim(BEN, M1, HAK));
cek('penjaga kiriman: karyawan ditolak (walau kisinya "sendiri"); kisi hitungLaci "tidak" ditolak', !!kirim(KRY, Object.assign({}, M1, { mintaUid: 'uid-k' }), HAK).tolak && !!kirim(BEN, M1, HAK_TIDAK).tolak);
cek('penjaga kiriman: brankas > hitungan, hitungan 0, pecahan rupiah, kolom keputusan, atas nama orang lain → ditolak',
  !!kirim(BEN, Object.assign({}, M1, { amankan: 700000 }), HAK).tolak && !!kirim(BEN, Object.assign({}, M1, { hitung: 0, amankan: 0 }), HAK).tolak && !!kirim(BEN, Object.assign({}, M1, { hitung: 607500.5 }), HAK).tolak
  && !!kirim(BEN, Object.assign({}, M1, { diputusTanggal: '2026-09-19' }), HAK).tolak && !!kirim(BEN, Object.assign({}, M1, { mintaUid: 'uid-lain' }), HAK).tolak);
cek('logika tablet: karyawan tidak bisa menyusun hitungan', /Penjaga laci/.test(hlSusunKirim(D1b, KRY, W).tolak || ''));
simpan(R1);
cek('hitungan yang sama tidak dikirim dua kali', /masih menunggu owner/.test(hlSusunKirim(D1b, BEN, W).tolak || ''));
// lewat tengah malam: 20 Sep 00.30 = masih menutup hari 19 Sep
var W0 = { tanggal: '2026-09-20', jam: '00:30', kini: '2026-09-19T17:30:00.000Z', idUnik: idU };
var R0 = hlSusunKirim({ lembar: { 100000: 6 }, receh: '', amankan: 'sudah' }, BEN, W0); var M0 = R0.dokumen ? R0.dokumen[0].data : {};
cek('lewat tengah malam (20 Sep 00.30): hitungan untuk hari 19 Sep, tanggal tulis 20 Sep', M0.tanggal === '2026-09-19' && M0.tanggalTulis === '2026-09-20' && M0.hitung === 600000 && M0.amankan === 407500, R0.tolak || M0);
simpan(R0);
// setelan owner tidak terbaca (sebelum rules v16 / belum disimpan owner) → tidak ditebak dari angka bawaan
var AT = cacheMentah('aturan').slice(); pasok('aturanToko', AT.filter(function (d) { return d.id !== 'tutupHari'; }));
var Hx = hlHitung(D1b, K21); var Rx = hlSusunKirim(Object.assign({}, D1b, { amankan: '' }), BEN, Object.assign({}, W, { jam: '21:05' }));
cek('setelan tutup hari owner tak terbaca: amankan tidak ditebak (0), kiriman tetap jalan tanpa memilih', Hx.amankanBisa === false && Hx.pindah === 0 && Rx.dokumen && Rx.dokumen[0].data.amankan === 0 && Rx.dokumen[0].data.kembalian === null, [Hx.amankanBisa, Hx.pindah, Rx.tolak || (Rx.dokumen && Rx.dokumen[0].data)]);
pasok('aturanToko', AT);

// ---------- owner: Pakai hitungan ini ----------
var LM = hlMenungguHari('2026-09-19');
cek('owner: dua hitungan menunggu untuk 19 Sep, terbaru (00.30) di atas', LM.length === 2 && LM[0].id === M0.id && LM[1].id === M1.id && hlMenungguSemua().length === 2, LM.map(function (b) { return b.jam; }));
var P = hlTerapkan(M1.id, { rekening: 'belum' });
cek('Pakai: lembar, receh, timbang & jam hitung dari tablet; laci & amankan beres; cek QRIS tidak disentuh', P.patch && P.patch.lembar[100000] === 5 && P.patch.receh === 1500 && P.patch.timbang.Angsa === '30,5' && P.patch.status.laci === 'beres'
  && P.patch.status.amankan === 'beres' && P.patch.status.rekening === 'belum' && P.patch.amankanTetap === 415000 && P.patch.dariHitung === M1.id && P.patch.hitungJam === '21:00' && P.patch.hitungTgl === '2026-09-19', P.tolak || P.patch);
var D = DRAF_OWNER(Object.assign({}, P.patch, { alasan: ALASAN }));
var RLs = rumusLaci('2026-09-19').seharusnya; var H = hitungTutup(D, K22); var sel0 = H.selisih;
cek('lembar owner: laci 607.500 dari tablet, selisih = hitungan − seharusnya, brankas 415.000 (angka tablet), laci tinggal 192.500', H.hitung === 607500 && H.hitungKini === 607500 && H.tablet && H.tablet.id === M1.id
  && H.selisih === 607500 - RLs && H.amankanN === 415000 && H.laciAkhir === 192500, [H.hitung, H.hitungKini, RLs, H.selisih, H.amankanN, H.laciAkhir]);
// nota tunai Rp50.000 jam 21.30 — SESUDAH dihitung 21.00
var jual = cacheMentah('penjualan').slice(); var j4 = jual.find(function (p) { return String(p.id) === 'j4'; });
pasok('penjualan', jual.concat([Object.assign({}, j4, { id: 'j-sesudah', jam: '21:30', totalKg: 3.5, jumlahKarung: 0.07, hargaTotal: 50000, hppTotalSaatJual: 45500 })]));
var SH = tdSesudahHitung('2026-09-19', '2026-09-19', '21:00');
cek('uang laci sesudah jam hitung: nota tunai 21.30 = +Rp50.000 (1 catatan)', SH.net === 50000 && SH.n === 1, SH);
cek('hitungan lewat tengah malam: catatan hari itu semuanya SEBELUM hitungan (tidak ditambah)', tdSesudahHitung('2026-09-19', '2026-09-20', '00:30').net === 0);
var H2 = hitungTutup(D, K22);
cek('catatan SESUDAH dihitung tidak mengubah selisih: laci sekarang 657.500, selisih sama persis', H2.hitungKini === 657500 && H2.selisih === sel0 && rumusLaci('2026-09-19').seharusnya === RLs + 50000, [H2.hitungKini, H2.selisih, sel0]);
cek('brankas tetap angka tablet 415.000 (bukan rumus 657.500 − 192.500); laci tinggal 242.500', H2.amankanN === 415000 && H2.laciAkhir === 242500, [H2.amankanN, H2.laciAkhir]);
cek('rekap menyebut siapa & jam hitung, dan uang yang tercatat sesudahnya', rekapTutup(H2).some(function (r) { return r.a === 'Laci dihitung Penjaga A 21:00' && r.b === 'Rp607.500'; }) && rekapTutup(H2).some(function (r) { return /tercatat sesudah dihitung/.test(r.a) && r.b === '+Rp50.000'; }), rekapTutup(H2).slice(6, 12));
cek('tutup tanpa tablet tidak berubah: laci = hitungan, tanpa tanda tablet', (function () { var x = hitungTutup(DRAF_OWNER({ lembar: { 100000: 6 }, status: { laci: 'beres' } }), K22); return x.hitungKini === 600000 && x.tablet === null && x.amankanTetap === null; })());

// ---------- owner: Tutup ----------
var T1 = susunTutup(D, WO, true); var th = dok(T1, 'tutupHari')[0] || {};
cek('Tutup: tutupHari laci saat ditutup 657.500 (Σ fisik − seharusnya = selisih), tanda tablet (siapa, jam, hitungan asli, sesudahnya, brankas)', th.kasFisikLaci === 657500 && th.selisih === sel0 && th.dariTablet && th.dariTablet.id === M1.id
  && th.dariTablet.hitung === 607500 && th.dariTablet.sesudah === 50000 && th.dariTablet.amankan === 415000 && th.dariTablet.oleh === 'Penjaga A', T1.tolak || th);
cek('Tutup: pindah uang laci → brankas 415.000; titik kas laci 242.500', (dok(T1, 'pindahUang', 'pd-2026-09-19')[0] || {}).nominal === 415000 && T1.titik && T1.titik.laci === 242500, [dok(T1, 'pindahUang'), T1.titik]);
var p1 = dok(T1, 'persetujuan', M1.id)[0] || {}; var p0 = dok(T1, 'persetujuan', M0.id)[0] || {};
cek('Tutup: hitungan yang dipakai = disetujui (jam tutup); hitungan lain hari itu = dibaca, tidak dipakai', p1.status === 'disetujui' && p1.tutupJam === '22:00' && p1.diputusTanggal === '2026-09-19' && p0.status === 'dibaca' && /Tidak dipakai/.test(p0.balasan || ''), [p1.status, p0.status, p0.balasan]);
cek('Tutup: timbang Angsa dari tablet jadi penyesuaian stok (bila beda)', (function () { var m = H2.timbang.find(function (x) { return x.merk === 'Angsa'; }); var ps = dok(T1, 'penyesuaianStok').filter(function (x) { return x.merk === 'Angsa'; });
  return D.status.timbang !== 'beres' || (m && (m.beda === 0 ? ps.length === 0 : ps.length === 1 && ps[0].kgFisik === 30.5)); })(), [D.status, dok(T1, 'penyesuaianStok')]);
var T2 = susunTutup(DRAF_OWNER({ lembar: { 100000: 6 }, status: { laci: 'beres' }, alasan: ALASAN }), WO, true);
cek('owner menutup sendiri: semua hitungan tablet hari itu = dibaca ("owner menghitung sendiri"), tanpa tanda tablet', !T2.tolak && dok(T2, 'persetujuan').length === 2 && dok(T2, 'persetujuan').every(function (x) { return x.status === 'dibaca' && /sendiri/.test(x.balasan); }) && !(dok(T2, 'tutupHari')[0] || {}).dariTablet, T2.tolak || dok(T2, 'persetujuan'));

// ---------- minta hitung ulang ----------
cek('minta hitung ulang tanpa alasan ditolak', /alasan/.test(hlSusunTolak(M1.id, '  ', WO).tolak || ''));
var TL = hlSusunTolak(M1.id, 'Pecahan 50 ribu dihitung ulang', WO); var t1 = TL.dokumen ? TL.dokumen[0].data : {};
cek('minta hitung ulang = ditolak beralasan', t1.status === 'ditolak' && t1.alasanTolak === 'Pecahan 50 ribu dihitung ulang' && t1.diputusJam === '22:00', TL.tolak || t1);
simpan(TL);
var b1 = hlMilikSaya(BEN, '2026-09-19').find(function (b) { return b.id === M1.id; }) || {};
cek('tablet membaca: "owner minta hitung ulang" + alasannya', b1.namaStatus === 'owner minta hitung ulang' && b1.alasan === 'Pecahan 50 ribu dihitung ulang', b1);
cek('hitungan yang sudah ditolak tidak bisa dipakai / ditutup', /sudah tidak menunggu/.test(susunTutup(D, WO, true).tolak || '') && !!hlTerapkan(M1.id, {}).tolak, susunTutup(D, WO, true).tolak);

// ---------- Ben TIDAK memindah ke brankas ----------
var R3 = hlSusunKirim({ lembar: { 100000: 7 }, receh: '', amankan: 'tidak' }, BEN, Object.assign({}, W, { jam: '21:10' })); var M3 = R3.dokumen ? R3.dokumen[0].data : {};
cek('Ben "tidak dipindah": hitungan tanpa brankas', M3.hitung === 700000 && M3.amankan === 0, R3.tolak || M3); simpan(R3);
var P3 = hlTerapkan(M3.id, {}); var T3 = susunTutup(DRAF_OWNER(Object.assign({}, P3.patch || {}, { alasan: ALASAN })), WO, true);
cek('owner Pakai hitungan tanpa brankas: amankan DILEWATI, tidak ada pindah uang, titik laci = 700.000 + 50.000 sesudahnya', P3.patch && P3.patch.status.amankan === 'lewat' && P3.patch.amankanTetap === null && !dok(T3, 'pindahUang').length && T3.titik && T3.titik.laci === 750000, [P3.patch && P3.patch.status, dok(T3, 'pindahUang'), T3.tolak || T3.titik]);
cek('hitungan lebih kecil dari yang sudah di brankas ditolak', /lebih kecil dari yang sudah dipindah ke brankas/.test(hitungTutup(DRAF_OWNER({ lembar: { 100000: 2 }, status: { laci: 'beres', amankan: 'beres' }, dariHitung: M3.id, hitungTgl: '2026-09-19', hitungJam: '21:10', amankanTetap: 900000 }), K22).tolakLaci));

// ---------- papan Persetujuan, kabar, pendengar, cetak ----------
cek('papan Persetujuan: "Setujui" hitungan laci ditolak (diselesaikan di Tutup hari)', /Tutup hari/.test(susunPutusPersetujuan(M0.id, true, '', WO).tolak || ''));
cek('papan Persetujuan: Tolak = minta hitung ulang (ditolak beralasan)', ((susunPutusPersetujuan(M0.id, false, 'hitung lagi', WO).dokumen || [])[0] || { data: {} }).data.status === 'ditolak');
var PS = ssPersetujuan(new Date(WO.kini)).menunggu.find(function (m) { return m.id === M0.id; }) || {};
cek('papan Persetujuan: hitungan tidak ikut "setujui sekaligus", kalimatnya menyebut hitungan', PS.sekaligus === false && PS.n === 0 && /Hitungan laci/.test(PS.teks || ''), PS);
cek('kabar dalam aplikasi: "laci … dihitung Rp600.000 · Rp407.500 ke brankas"', /laci .* dihitung Rp600\.000 · Rp407\.500 ke brankas/.test(kbIsi(M0)), kbIsi(M0));
var dl = function (a) { var x = pendengarPeran(a).find(function (p) { return p.nama === 'aturanToko'; }); return (x && x.dok) || []; };
cek('Penjaga laci mendengar aturanToko/tutupHari (rules v16); karyawan tidak', dl(BEN).indexOf('tutupHari') >= 0 && dl(KRY).indexOf('tutupHari') < 0 && dl(KRY).indexOf('produkArsip') >= 0, [dl(BEN), dl(KRY)]);
var CT = hlTeksCetak(hlBaris(M1), { nama: 'Toko Contoh' }, { tanggal: '2026-09-19', jam: '21:01', oleh: 'Penjaga A' });
cek('slip hitungan: jumlah, brankas, sisa laci, timbang; tanpa seharusnya / selisih', /JUMLAH DIHITUNG  Rp607\.500/.test(CT) && /Dipindah ke brankas  Rp415\.000/.test(CT) && /Tinggal di laci  Rp192\.500/.test(CT) && /Angsa  30,5 kg/.test(CT) && !/seharusnya|selisih/i.test(CT), CT);
print(J(hasil));
"""


def baca_semua():
    return dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(MODUL + STATIS)))


def rakit(t):
    isi = lambda m: t[m] if m in t else open(os.path.join(AKAR, m), encoding='utf-8').read()
    return '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(isi(m)) for m in bundel_baru.lengkapi(MODUL)])


def jalankan(t):
    js = UB.JAM_TETAP + rakit(t) + '\nvar KOTAK = ' + json.dumps(kotak()) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    keluar = (r.stdout or '').strip().split('\n')[-1] if r.stdout else ''
    if r.returncode != 0 or not keluar.startswith('['): return [{'nama': 'jsc jalan', 'ok': False, 'ket': ((r.stderr or '') + (r.stdout or ''))[-1500:]}]
    return json.loads(keluar)


def tanpa_komentar_js(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    return '\n'.join(re.sub(r'(^|\s)//.*$', '', x) for x in s.split('\n'))


def periksa_statis(t):
    c = []; ok = lambda n, x, k='': c.append({'nama': 'statis: ' + n, 'ok': bool(x), 'ket': k})
    buta = [b for b in (HLP, HLL) if re.search(r'seharusnya|selisih|rumusLaci|ringkasHari|hitungTutup|saldoKantong', tanpa_komentar_js(t[b]))]
    ok('HITUNG BUTA: panel & logika tablet tidak menyentuh seharusnya / selisih / rumus laci', not buta, buta)
    ok('logika & panel tablet tidak menulis sendiri (hanya menyusun; tulis lewat penulis layar)', not re.search(r'tulisDokumen|setDoc|writeBatch|import .*firebase', t[HLL] + t[HLP]))
    M = t[MN]
    ok('Menu akun tablet: kartu Tutup hari untuk Penjaga laci (hlTampil) + aksinya', "${hlTampil(akunM) ? kartuTutupTablet(s, { akun: akunM, kini: kini() }) : ''}" in M and "aksiTutupTablet({ set, st, tulis, akun: opsi.akun, waktu })" in M)
    ok('kartu tablet hanya untuk Penjaga laci yang kisi hitungLaci-nya bukan "tidak"', "akun.peran === 'ben' && hakAkun(akun, 'hitungLaci') !== 'tidak'" in t[HLP])
    U = t[UG]
    ok('Uang › Tutup hari: hitungan tablet di blok laci & di lembar yang sudah tertutup (tutup ulang)', "const laci = h`<div>${pitaHitungTablet(s, d, H, false)}" in U and "${pitaHitungTablet(s, d, H, true)}" in U and 'data-aksi="tdHlPakai"' in U and 'data-aksi="tdHlTolakBuka"' in U)
    ok('Uang › Uang keluar: pita hitungan laci menunggu → buka Tutup hari', 'data-k="hl-pita"' in U and 'data-aksi="tdHlKeTutup"' in U)
    ok('papan Persetujuan menolak "Setujui" hitungan laci; tindakan sama dengan tutup-hari-logika', "if (m.tindakan === SS_HITUNG_LACI && setuju) return { tolak:" in t[SL] and "export const SS_HITUNG_LACI = 'hitungLaci';" in t[SL] and "export const HL_TINDAKAN = 'hitungLaci';" in t[TDL])
    ok('kabar dalam aplikasi → layar Uang untuk hitungan laci', "hitungLaci: 'Hitungan laci dari tablet'" in t[KB] and "m.tindakan === 'hitungLaci' ? 'uang' : 'menu'" in t[KB])
    ok('push HP menyebut hitungan laci & membuka Uang', "hitungLaci: 'Hitungan laci'" in t[FN] and "t === 'barangMasuk' || t === 'hitungLaci' ? 'uang' : 'menu'" in t[FN])
    ok('index.html memuat logika & panel tutup hari tablet (modulepreload)', '<link rel="modulepreload" href="js/layar/tutup-tablet-logika.js">' in t[IDX] and '<link rel="modulepreload" href="js/layar/tutup-tablet-panel.js">' in t[IDX])
    ok('rules v16: hitungan lewat stafHitungLaci([ben]) && tglStaf; aturanToko/tutupHari terbaca ben', "(stafHitungLaci(['ben']) && tglStaf('tanggal'))" in t[RULES] and "(id == 'tutupHari' && staf(['ben']))" in t[RULES])
    return c


def periksa(t, diam=False):
    c = jalankan(t) + periksa_statis(t)
    g = [x for x in c if not x['ok']]
    if not diam:
        for x in c: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:700]))
        print('TUTUP HARI DARI TABLET: %d lulus · %d gagal' % (len(c) - len(g), len(g)))
    return g


def main():
    t = baca_semua()
    if '--kontrol' in sys.argv:
        L = t[HLL]; P = t[HLP]; T = t[TDL]; A = t[AK]; S = t[SL]; R = t[RULES]
        rusak = [
            ('tablet menampilkan angka seharusnya (hitung buta bocor)', HLP, P.replace('<div class="th-baris jumlah"><span>Dihitung</span>', '<div class="th-baris jumlah"><span>Dihitung · seharusnya ${RP(rumusLaci(H.iso).seharusnya)}</span>')),
            ('lembar tablet membawa seharusnya', HLL, L.replace("  return { iso, A, pecahan, receh:", "  return { seharusnya: 0, iso, A, pecahan, receh:")),
            ('pindah ke brankas memakai kembalian bawaan, bukan angka owner', HLL, L.replace("const kembalian = A.kembalian;", "const kembalian = 500000;")),
            ('amankan ditebak walau setelan owner tak terbaca', HLL, L.replace("const amankanBisa = A.dariOwner;", "const amankanBisa = true;")),
            ('hitungan bertanggal tulis, bukan hari yang ditutup', HLL, L.replace("tanggal: H.iso, jam: w.jam, tanggalTulis: w.tanggal", "tanggal: w.tanggal, jam: w.jam, tanggalTulis: w.tanggal")),
            ('Ben tidak memindah tapi amankan dianggap beres', HLL, L.replace("amankan: b.amankan > 0 ? 'beres' : 'lewat'", "amankan: 'beres'")),
            ('karyawan boleh mengirim hitungan (penjaga kiriman)', AK, A.replace("if (P !== 'ben' || (hak.hitungLaci || 'tidak') === 'tidak'", "if ((hak.hitungLaci || 'tidak') === 'tidak'")),
            ('akun tablet tidak mendengar setelan tutup hari', AK, A.replace(".concat(akun.peran === 'ben' ? DOK_BEN[n] || [] : [])", ".concat([])")),
            ('catatan sesudah hitungan tidak dihitung (selisih berubah)', TDL, T.replace("const hitungKini = hitung + (tablet ? tablet.sesudah.net : 0);", "const hitungKini = hitung;")),
            ('hitungan lewat tengah malam ikut ditambah catatan sesudahnya', TDL, T.replace("if (!/^\\d\\d:\\d\\d$/.test(J) || String(tglTulis || '') !== String(iso)) return out;", "if (!/^\\d\\d:\\d\\d$/.test(J)) return out;")),
            ('laci tutupHari = hitungan tablet, bukan laci saat ditutup', TDL, T.replace("kasFisikLaci: H.hitungKini,", "kasFisikLaci: H.hitung,")),
            ('brankas tablet diganti rumus', TDL, T.replace("amankanTetap !== null ? amankanTetap : Math.max(", "false ? amankanTetap : Math.max(")),
            ('hitungan dipakai tidak ditandai disetujui', TDL, T.replace("dipakai ? { status: 'disetujui', tutupJam: w.jam } :", "dipakai ? { status: 'menunggu' } :")),
            ('hitungan lain hari itu tetap menunggu', TDL, T.replace("(m.status || 'menunggu') === 'menunggu' && String(m.tanggal || '') === iso).forEach(", "(m.status || 'menunggu') === 'menunggu' && String(m.tanggal || '') === iso && H.tablet && String(m.id) === H.tablet.id).forEach(")),
            ('hitungan yang sudah ditolak masih bisa ditutup', TDL, T.replace("  if (H.tablet && (!hlPakai || (hlPakai.status || 'menunggu') !== 'menunggu')) return", "  if (false) return")),
            ('papan Persetujuan menyetujui hitungan (hari tidak tertutup)', SL, S.replace("  if (m.tindakan === SS_HITUNG_LACI && setuju) return { tolak:", "  if (false) return { tolak:")),
            ('rules: hitungan laci dibuka untuk karyawan', RULES, R.replace("(stafHitungLaci(['ben']) && tglStaf('tanggal'))", "(stafHitungLaci(['ben', 'karyawan']) && tglStaf('tanggal'))")),
        ]
        kode = 0
        for nama, berkas, isi in rusak:
            if isi == t[berkas]: print('KONTROL BASI  ' + nama); kode = 3; continue
            t2 = dict(t); t2[berkas] = isi; g = periksa(t2, diam=True)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + (' → ' + g[0]['nama'][:100] if g else ''))
            if not g: kode = 3
        print('KONTROL: %d kerusakan' % len(rusak)); sys.exit(kode)
    sys.exit(1 if periksa(t) else 0)


if __name__ == '__main__':
    main()
