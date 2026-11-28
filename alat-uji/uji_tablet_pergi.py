#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tablet_pergi.py — TABLET SAAT OWNER PERGI (owner 28 Nov 2026, rules v27).
Owner: penjaga laci "bisa liat nota dari pemasok dan foto nota atas izin gua melalui hak izin akses melalui peran dan hak yang bisa gua atur di akun owner.
Termasuk mencatat, mengatur, ubah harga jika gua izinkan dari notifikasi. Semua atas persetujuan gua." + daftar belanja + usul harga jual; kabar ke HP (buka,
ganti jaga, tutup, stok habis & jual murah, tablet putus / nyangkut); foto bukti HANYA saat owner minta; absen jaga; tugas dari owner.

Yang dipegang:
  · Hak tablet per peran (sistem-logika SS_HAK_TABLET): bawaan semua MATI; foto nota & catat harga beli hanya Penjaga laci; menyalakan foto nota menulis
    aksesAkun.hakFotoNota untuk akun Penjaga laci (server membuka fotoBon per akun); akun baru / pindah peran ikut setelan; keadaanAkun membawa tandanya
  · bentuk kiriman tablet = rules v27 (akses.js usulTabletSah / jagaSah / buktiSah + periksaKiriman): usul TIDAK boleh membawa kolom keputusan owner
  · usul harga jual: Setujui = terbit satu harga (susunTerbitSatu — dokumen katalog sama dengan terbit owner), di bawah modal ditolak; belanja = disetujui
    (dipakai owner di Belanja); kabar toko & tugas selesai = dibaca + balasan
  · kabar toko dari tablet (kbKabarToko): habis / perlu dipesan / di bawah modal — satu kabar per barang per jenis per hari; owner tidak pernah
  · tugas owner (kbSusunTugasOwner / kbTugasTerbuka / kbSusunTugasSelesai): wajib foto tanpa foto ditolak; yang sudah dijawab hilang dari daftar
  · kabar ke HP owner (sistem-logika SS_KABAR_TOKO): tiga kabar tablet di aturanToko/peran.kabarTablet (dokumen yang dibaca tablet), sisanya aturanToko/kabarToko;
    jam toko tervalidasi; bawaannya SAMA dengan functions/jaga.js
  · absen jaga (jaga-logika): deret jaga per hari, "sampai" = orang berikutnya masuk, terakhir = sampai tutup (tidak ditebak), tanpa PIN ≠ tidak masuk
  · fungsi server (functions/jaga.js, functions/pesan.js): toko dibuka / ganti jaga / orang sama = diam; belum buka / belum tutup / tablet putus / ditolak server /
    antrean berulang — sekali sehari, pulih = boleh lagi; omzet di kabar hitungan laci; tugas owner sampai ke tablet; kabar toko dibaca tanpa balasan = diam
  · sambungan layar (statis): Harga untuk staf ber-hak, absen ditulis saat PIN, kartu tugas & foto, Minta foto di titipan, rekap absen di Upah, setelan kabar
KOTAK PASIR (angka contoh uji_harga_baru), jam dikunci 19 Sep 2026 10:00 WIB.

    python3 alat-uji/uji_tablet_pergi.py            → N lulus · 0 gagal
    python3 alat-uji/uji_tablet_pergi.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_harga_baru as UH  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
SL = 'baru/js/layar/sistem-logika.js'; KB = 'baru/js/layar/kabar-baru-logika.js'; AK = 'baru/js/data/akses.js'; HL = 'baru/js/layar/harga-logika.js'; JG = 'baru/js/layar/jaga-logika.js'
FJ = 'functions/jaga.js'; FP = 'functions/pesan.js'; FI = 'functions/index.js'
APP = 'baru/js/app.js'; HG = 'baru/js/layar/harga.js'; MN = 'baru/js/layar/menu.js'; UG = 'baru/js/layar/uang.js'; LC = 'baru/js/layar/lonceng.js'; TO = 'baru/js/layar/tugas-owner-panel.js'; FB = 'baru/js/data/firebase.js'
MODUL = list(dict.fromkeys(UH.MODUL + ['baru/js/data/hemat-baca.js', 'baru/js/layar/titipan-logika.js', AK, 'baru/js/layar/bon-logika.js', 'baru/js/layar/faktur-logika.js',
                                       'baru/js/layar/banding-catat-logika.js', 'baru/js/inti/langit-logika.js', SL, KB, JG]))
IDX = 'baru/index.html'
LAYAR = [APP, HG, MN, UG, LC, TO, FB, FI, IDX]
MODUL = list(dict.fromkeys(bundel_baru.lengkapi(MODUL)))   # modul yang dipakai modul di atas ikut (kg-liter, harga tingkat, …)
JAM_TETAP = UH.JAM_TETAP

KOTAK = json.loads(json.dumps(UH.KOTAK))
KOTAK['aksesAkun'] = [{'id': 'uTab', 'uid': 'uTab', 'nama': 'Tablet toko', 'email': 'tablet@contoh', 'peran': 'ben', 'aktif': True},
                      {'id': 'uKar', 'uid': 'uKar', 'nama': 'HP karyawan', 'email': 'karyawan@contoh', 'peran': 'karyawan', 'aktif': True}]
KOTAK['permintaanAkses'] = [{'id': 'uBaru', 'uid': 'uBaru', 'nama': 'Tablet kedua', 'email': 'tablet2@contoh', 'pada': '2026-09-19T02:00:00.000Z'}]
KOTAK['persetujuan'] = []
KOTAK['jagaLog'] = [
    {'id': 'j1', 'tanggal': '2026-09-19', 'jam': '07:05', 'nama': 'Pagi', 'peran': 'karyawan'}, {'id': 'j2', 'tanggal': '2026-09-19', 'jam': '09:40', 'nama': 'Pagi', 'peran': 'karyawan'},
    {'id': 'j3', 'tanggal': '2026-09-19', 'jam': '13:05', 'nama': 'Sore', 'peran': 'karyawan'}, {'id': 'j4', 'tanggal': '2026-09-18', 'jam': '07:30', 'nama': 'Sore', 'peran': 'karyawan'},
    {'id': 'j5', 'tanggal': '2026-09-17', 'jam': '25:99', 'nama': 'Rusak', 'peran': 'karyawan'}]

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 9000; return function () { n += 1; return n; }; })() };
var terap = function (r) { (r.dokumen || []).forEach(function (d) { var A = cacheMentah(d.koleksi === 'aturanToko' ? 'aturan' : d.koleksi).filter(function (x) { return String(x.id) !== String(d.data.id); }); A.push(d.data); pasok(d.koleksi, A); }); };
var OWNER = { jenis: 'owner', nama: 'Owner', uid: 'uOwner' }; var TAB = { jenis: 'aktif', peran: 'ben', nama: 'Pagi', uid: 'uTab' };

// ---- 1 · Hak tablet per peran
ok('hak tablet bawaan: semua MATI untuk Penjaga laci & Karyawan', S_HAK().every(function (x) { return !ssHakTablet('ben', x) && !ssHakTablet('karyawan', x); }), J(S_HAK()));
var rH = susunHakTablet('ben', 'harga', true, W); terap(rH);
ok('menyalakan Harga & Pemasok untuk Penjaga laci = aturanToko/peran.hakTablet.ben.harga; Karyawan tetap mati', !rH.tolak && ssHakTablet('ben', 'harga') && !ssHakTablet('karyawan', 'harga') && rH.dokumen[0].data.id === 'peran', J(rH));
ok('foto nota & catat harga beli hanya Penjaga laci (Karyawan ditolak)', !!susunHakTablet('karyawan', 'fotoNota', true, W).tolak && !!susunHakTablet('karyawan', 'catatHargaBeli', true, W).tolak);
var rF = susunHakTablet('ben', 'fotoNota', true, W);
ok('menyalakan foto nota menulis aksesAkun.hakFotoNota = true untuk akun Penjaga laci SAJA (server membuka fotoBon per akun)', rF.dokumen.filter(function (d) { return d.koleksi === 'aksesAkun'; }).map(function (d) { return d.data.uid + ':' + d.data.hakFotoNota; }).join(',') === 'uTab:true', J(rF.dokumen));
terap(rF);
ok('setelan peran lain dibawa utuh saat hak diputar (orang di tablet, jatah nego, hak harga)', ssHakTablet('ben', 'harga') && ssHakTablet('ben', 'fotoNota') && J(ssAtur('peran').operator) === J({}));
var rD = susunDaftarkan('uBaru', 'ben', W);
ok('akun Penjaga laci yang baru didaftarkan ikut hak foto nota yang sudah menyala', rD.dokumen[0].data.hakFotoNota === true && susunDaftarkan('uBaru', 'karyawan', W).dokumen[0].data.hakFotoNota === undefined, J(rD.dokumen[0].data));
terap(rF); var rU = susunUbahAkun('uTab', { peran: 'karyawan' }, W, true);
ok('akun Penjaga laci pindah jadi Karyawan = tanda foto nota MATI', rU.dokumen[0].data.hakFotoNota === false && rU.dokumen[0].data.peran === 'karyawan', J(rU.dokumen[0].data));
ok('keadaanAkun membawa hakFotoNota hanya untuk Penjaga laci bertanda', keadaanAkun('a@b', 'u1', { peran: 'ben', aktif: true, hakFotoNota: true }).hakFotoNota === true && keadaanAkun('a@b', 'u1', { peran: 'karyawan', aktif: true, hakFotoNota: true }).hakFotoNota === false && keadaanAkun('a@b', 'u1', { peran: 'ben', aktif: true }).hakFotoNota === false);

// ---- 2 · bentuk kiriman tablet (= rules v27)
var usul = { id: 1, tindakan: 'hargaJual', status: 'menunggu', mintaUid: 'uTab', teks: 'IR64 Apex per kg 14.100 → 14.600', usul: { kunci: 'IR64 Apex|S', baru: 14600 } };
ok('usul tablet sah: hargaJual menunggu dari uid sendiri; kolom keputusan owner / uid lain / tindakan di luar daftar / teks > 500 DITOLAK', usulTabletSah(usul, 'uTab') && !usulTabletSah(Object.assign({}, usul, { diputusPada: 'x' }), 'uTab') && !usulTabletSah(usul, 'uLain')
  && !usulTabletSah(Object.assign({}, usul, { tindakan: 'hargaBanding' }), 'uTab') && !usulTabletSah(Object.assign({}, usul, { teks: new Array(502).join('a') }), 'uTab') && !usulTabletSah(Object.assign({}, usul, { status: 'disetujui' }), 'uTab')
  && ['belanja', 'kabarToko', 'tugasSelesai'].every(function (t) { return usulTabletSah(Object.assign({}, usul, { tindakan: t }), 'uTab'); }));
var jg = { id: 'jg-1', tanggal: '2026-09-19', jam: '07:05', pada: 'x', nama: 'Pagi', peran: 'karyawan', orangId: 'o1', oleh: 'Pagi', olehUid: 'uTab', perangkat: 'CPad', diubahOleh: 'Pagi', diubahOlehUid: 'uTab', diubahPerangkat: 'CPad', diubahPada: 'x' };
ok('absen jaga sah: kolom terbatas, jam JJ:MM, peran ben/karyawan; kolom lain / peran owner ditolak', jagaSah(jg) && !jagaSah(Object.assign({}, jg, { omzet: 1 })) && !jagaSah(Object.assign({}, jg, { peran: 'owner' })) && !jagaSah(Object.assign({}, jg, { jam: '7:05' })) && !jagaSah(Object.assign({}, jg, { nama: '' })));
var bk = { id: 'fbk-1', tugasId: '9001', tanggal: '2026-09-19', jam: '10:00', jenis: 'image/jpeg', base64: 'QUJD', byte: 3, lebar: 10, tinggi: 10 };
ok('foto bukti sah: menunjuk tugas, gambar jpeg/png/webp ≤ 960.000 huruf; tanpa tugas / jenis lain / kolom lain ditolak', buktiSah(bk) && !buktiSah(Object.assign({}, bk, { tugasId: '' })) && !buktiSah(Object.assign({}, bk, { jenis: 'text/html' })) && !buktiSah(Object.assign({}, bk, { idBon: 'b1' })) && !buktiSah(Object.assign({}, bk, { base64: new Array(960002).join('a') })));
ok('tablet boleh MEMBUAT jagaLog & fotoBukti (ben & karyawan), tidak membacanya (bukan pendengar staf)', BUAT_STAF.jagaLog.join() === 'ben,karyawan' && BUAT_STAF.fotoBukti.join() === 'ben,karyawan' && pendengarPeran(TAB).every(function (p) { return p.nama !== 'jagaLog' && p.nama !== 'fotoBukti'; }));

// ---- 3 · putusan owner atas usul tablet
var kunciApex = 'IR64 Apex|S', kunciAngsa = 'Angsa|S';   // baris katalog per kg (harga-logika: merk|S)
pasok('persetujuan', [{ id: 801, tindakan: 'hargaJual', status: 'menunggu', mintaUid: 'uTab', teks: 'Angsa 13.800 → 14.200', usul: { kunci: kunciAngsa, nama: 'Angsa · Karung per kg', lama: 13800, baru: 14200, alasan: 'pemasok naik' } },
  { id: 802, tindakan: 'hargaJual', status: 'menunggu', mintaUid: 'uTab', teks: 'IR64 Apex 14.100 → 13.000', usul: { kunci: kunciApex, lama: 14100, baru: 13000, alasan: '' } },
  { id: 803, tindakan: 'kabarToko', jenis: 'habis', status: 'menunggu', mintaUid: 'uTab', teks: 'Angsa HABIS' }, { id: 804, tindakan: 'belanja', status: 'menunggu', mintaUid: 'uTab', teks: 'Angsa 4 karung', pesan: { Angsa: { p: 'RODA CONTOH', k: 4 } } }]);
var P1 = susunPutusPersetujuan(801, true, '', W); var kat = (P1.dokumen || []).filter(function (d) { return d.koleksi === 'katalogHargaKarung'; });
var T1 = susunTerbitSatu(kunciAngsa, 14200, W);
ok('Setujui usul harga jual = terbit satu harga (katalog Angsa 14.200, catatan hargaTerbit "usul tablet") + usul disetujui', kat.length === 1 && kat[0].data.hargaPerKg === 14200 && P1.dokumen.some(function (d) { return d.koleksi === 'hargaTerbit' && d.data.dari === 'usul tablet'; })
  && P1.dokumen.some(function (d) { return d.koleksi === 'persetujuan' && d.data.status === 'disetujui'; }), J(P1));
ok('dokumen katalog dari usul = dokumen katalog terbit owner untuk baris yang sama (satu bentuk)', J(T1.dokumen.filter(function (d) { return d.koleksi === 'katalogHargaKarung'; })) === J(kat), J([T1.dokumen[0], kat[0]]));
var P2 = susunPutusPersetujuan(802, true, '', W);
ok('usul di BAWAH modal (Apex 13.000 < 14.142) TIDAK terbit lewat Setujui — owner menerbitkannya sendiri bila disengaja', !!P2.tolak && /DI BAWAH modal/.test(P2.tolak), J(P2));
var P3 = susunPutusPersetujuan(803, true, 'oke, besok pesan', W); var P4 = susunPutusPersetujuan(804, true, '', W);
ok('kabar toko = dibaca + balasan; daftar belanja = disetujui (dipakai owner di Belanja)', P3.dokumen[0].data.status === 'dibaca' && P3.dokumen[0].data.balasan === 'oke, besok pesan' && P4.dokumen[0].data.status === 'disetujui', J([P3, P4]));
var Q = ssPersetujuan(new Date(Date.now())); var q4 = Q.menunggu.find(function (x) { return x.id === '804'; });
ok('papan Persetujuan: usul tablet bukan uang (n 0) dan tidak pernah ikut "setujui sekaligus"', Q.menunggu.filter(function (x) { return ['801', '802', '803', '804'].indexOf(x.id) >= 0; }).every(function (x) { return x.n === 0 && x.sekaligus === false; }) && /Belanja/.test(q4.saran), J(Q.menunggu));

// ---- 4 · kabar toko dari tablet
var KS = kbKabarToko([{ id: 'n1', trxId: 'T1', merkSumber: 'Angsa', hargaTotal: 600000, hppTotalSaatJual: 640000 }, { id: 'n2', trxId: 'T1', merkSumber: 'IR64 Apex', hargaTotal: 100000, hppTotalSaatJual: 90000 },
  { id: 'n3', trxId: 'T2', merkSumber: 'IR64 Apex', hargaTotal: 100000, hppTotalSaatJual: 90000 }, { id: 'n4', trxId: 'T3', merkSumber: 'Pandan Wangi', hargaTotal: 5, hppTotalSaatJual: 1, dibatalkan: true }],
  { Angsa: 0, 'IR64 Apex': 120 }, { 'IR64 Apex': 'habis ±3 hari' }, [], W, TAB, 'Pagi');
ok('kabar toko: Angsa HABIS + Angsa di BAWAH modal (600.000 < 640.000); IR64 Apex perlu dipesan SEKALI walau dua nota; nota batal tidak dikabarkan',
  J(KS.map(function (d) { return d.data.jenis + ':' + d.data.merk; })) === J(['habis:Angsa', 'bawahModal:Angsa-T1', 'menipis:IR64 Apex']) && KS.every(function (d) { return usulTabletSah(d.data, 'uTab') && d.data.dari === 'Pagi'; }), J(KS));
ok('kabar toko: yang sudah ada hari itu tidak dikirim lagi; owner tidak pernah mengirim', kbKabarToko([{ id: 'n1', trxId: 'T9', merkSumber: 'Angsa' }], { Angsa: 0 }, {}, KS.map(function (d) { return d.data; }), W, TAB, 'Pagi').length === 0
  && kbKabarToko([{ id: 'n1', merkSumber: 'Angsa' }], { Angsa: 0 }, {}, [], W, OWNER, 'Owner').length === 0);

// ---- 5 · tugas owner
var TG = kbSusunTugasOwner('  Foto rak depan  ', true, W, OWNER, 'tt1');
ok('tugas owner: hanya akun owner; status terkirim untuk tablet; wajib foto & rujukan tersimpan', !TG.tolak && TG.dokumen[0].data.tindakan === 'tugasOwner' && TG.dokumen[0].data.status === 'terkirim' && TG.dokumen[0].data.wajibFoto === true && TG.dokumen[0].data.rujukan === 'tt1' && TG.dokumen[0].data.teks === 'Foto rak depan'
  && !!kbSusunTugasOwner('x', false, W, TAB, '').tolak && !!kbSusunTugasOwner('   ', false, W, OWNER, '').tolak, J(TG));
pasok('persetujuan', [TG.dokumen[0].data]); var tg = TG.dokumen[0].data;
ok('tugas terbuka muncul di tablet; wajib foto tanpa foto DITOLAK', kbTugasTerbuka().length === 1 && !!kbSusunTugasSelesai(tg, 'sudah', '', W, TAB, 'Pagi').tolak);
var TS = kbSusunTugasSelesai(tg, 'rak sudah rapi', 'fbk-1', W, TAB, 'Pagi');
ok('jawaban tugas = persetujuan tugasSelesai menunjuk tugas & fotonya (sah rules v27); sesudahnya tugas hilang dari daftar tablet', !TS.tolak && TS.dokumen[0].data.tugasId === String(tg.id) && TS.dokumen[0].data.fotoId === 'fbk-1' && usulTabletSah(TS.dokumen[0].data, 'uTab')
  && (pasok('persetujuan', [tg, TS.dokumen[0].data]), kbTugasTerbuka().length === 0), J(TS));
ok('papan Persetujuan menyebut "lihat foto" dan membawa id tugasnya; tugas owner sendiri TIDAK tampil di papan (bukan permintaan)', (function () { var Q2 = ssPersetujuan(new Date(Date.now())); var m = Q2.menunggu.find(function (x) { return x.id === String(TS.dokumen[0].data.id); }); return m && m.fotoId === 'fbk-1' && m.tugasId === String(tg.id) && /lihat foto/.test(m.saran)
  && !Q2.menunggu.concat(Q2.riwayat).some(function (x) { return x.id === String(tg.id); }); })(), J(ssPersetujuan(new Date(Date.now()))));

// ---- 6 · setelan kabar ke HP owner
var K0 = ssKabarToko();
ok('kabar bawaan: semua 9 nyala, jam buka 07:00 telat 30, tutup 21:00, putus 30 menit', SS_KABAR_TOKO.length === 9 && SS_KABAR_TOKO.every(function (x) { return K0.nyala[x.id] === true; }) && K0.jamBuka === '07:00' && K0.telatMenit === 30 && K0.jamTutup === '21:00' && K0.menitPutus === 30, J(K0));
var rk = susunPutarKabarToko('habis', W); terap(rk);
ok('mematikan "Barang habis" = aturanToko/peran.kabarTablet.habis false (dokumen yang dibaca tablet), hak tablet tetap', rk.dokumen[0].data.id === 'peran' && rk.dokumen[0].data.kabarTablet.habis === false && ssKabarToko().nyala.habis === false && ssHakTablet('ben', 'harga'), J(rk.dokumen[0].data.kabarTablet));
var rb = susunPutarKabarToko('buka', W); terap(rb);
ok('mematikan "Toko dibuka" = aturanToko/kabarToko.nyala.buka false (dibaca fungsi server)', rb.dokumen[0].data.id === 'kabarToko' && rb.dokumen[0].data.nyala.buka === false && rb.dokumen[0].data.nyala.gantiJaga === true && ssKabarToko().nyala.buka === false, J(rb.dokumen[0].data));
ok('jam toko: bentuk JJ:MM, tutup sesudah buka, menit putus 10–240', !!susunAturSistem('kabarToko', { jamBuka: '7:00' }, W).tolak && !!susunAturSistem('kabarToko', { jamBuka: '21:00', jamTutup: '07:00' }, W).tolak
  && !!susunAturSistem('kabarToko', { menitPutus: '5' }, W).tolak && susunAturSistem('kabarToko', { jamBuka: '06:30', jamTutup: '20:00', telatMenit: '15', menitPutus: '45' }, W).dokumen[0].data.jamBuka === '06:30');
ok('bawaan kabar server di aplikasi = bawaan functions/jaga.js', J(SS_ATUR_BAWAAN.kabarToko) === J(__fj.ATUR_BAWAAN), J([SS_ATUR_BAWAAN.kabarToko, __fj.ATUR_BAWAAN]));

// ---- 7 · absen jaga
var SG = jgSegmen();
ok('absen 19 Sep: Pagi 07:05–13:05 (6 j 0 m, PIN dua kali digabung) lalu Sore 13:05–tutup (tanpa jam selesai); jam rusak dilewati', J(SG['2026-09-19'].map(function (x) { return [x.nama, x.mulai, x.sampai, x.menit, x.kali]; })) === J([['Pagi', '07:05', '13:05', 360, 2], ['Sore', '13:05', '', null, 1]]) && !SG['2026-09-17'], J(SG));
var RG = jgRekapOrang('Pagi Contoh', '2026-09-19', 3);
ok('nama absen ↔ nama upah: "Pagi" = "Pagi Contoh"; "Karyawan Contoh Satu" ≠ "Karyawan Contoh Dua"', jgSamaNama('Pagi', 'pagi contoh') && !jgSamaNama('Karyawan Contoh Satu', 'Karyawan Contoh Dua') && !jgSamaNama('', 'Pagi'));
ok('rekap per orang (nama upah "Pagi Contoh" cocok kata awal): 19 Sep jaga 07:05–13:05; 18 Sep "tidak jaga (Sore)"; 17 Sep "tidak ada PIN" — bukan "tidak masuk"',
  RG.nJaga === 1 && RG.hari[0].teks === '07:05–13:05 (6 j 0 m)' && RG.hari[1].teks === 'tidak jaga (Sore)' && RG.hari[2].teks === 'tidak ada PIN di tablet', J(RG));

// ---- 8 · fungsi server
var A0 = null; var hari = [{ id: 'a', tanggal: '2026-09-19', jam: '07:05', nama: 'Pagi' }, { id: 'b', tanggal: '2026-09-19', jam: '09:40', nama: 'Pagi' }, { id: 'c', tanggal: '2026-09-19', jam: '13:05', nama: 'Sore' }];
var PJ1 = __fj.pesanJaga(hari[0], hari, A0), PJ2 = __fj.pesanJaga(hari[1], hari, A0), PJ3 = __fj.pesanJaga(hari[2], hari, A0);
ok('kabarJaga: orang pertama = "Toko dibuka"; orang sama lagi = diam; orang lain = "Ganti jaga Pagi → Sore"', PJ1 && PJ1.judul === 'Toko dibuka' && /Pagi masuk jaga 07:05/.test(PJ1.isi) && PJ2 === null && PJ3 && PJ3.judul === 'Ganti jaga' && /Pagi → Sore 13:05/.test(PJ3.isi), J([PJ1, PJ2, PJ3]));
ok('kabarJaga: dimatikan owner = diam', __fj.pesanJaga(hari[0], hari, { nyala: { buka: false } }) === null && __fj.pesanJaga(hari[2], hari, { nyala: { gantiJaga: false } }) === null);
var kini = function (jam) { return new Date('2026-09-19T' + jam + ':00+07:00'); };
var P0 = __fj.periksaToko({ kini: kini('07:40'), atur: null, jaga: [], tutup: false, perangkat: [], sudah: {} });
ok('periksaToko: lewat 07:30 tanpa PIN = "Toko belum dibuka"; sudah dikirim = tidak lagi; jam 07:20 = belum', P0.kabar.length === 1 && P0.kabar[0].kunci === 'telatBuka' && __fj.periksaToko({ kini: kini('07:40'), jaga: [], sudah: { telatBuka: '07:40' } }).kabar.length === 0
  && __fj.periksaToko({ kini: kini('07:20'), jaga: [], sudah: {} }).kabar.length === 0, J(P0));
ok('periksaToko: lewat 21:00 ada jaga, belum ada hitungan laci = "Hari belum ditutup"; sudah ditutup = diam', __fj.periksaToko({ kini: kini('21:10'), jaga: hari, tutup: false, sudah: {} }).kabar.map(function (x) { return x.kunci; }).join() === 'belumTutup'
  && __fj.periksaToko({ kini: kini('21:10'), jaga: hari, tutup: true, sudah: {} }).kabar.length === 0);
var dv = function (jam, x) { return Object.assign({ id: 'cpad~uTab', nama: 'CPad', aplikasi: 'baru', akun: 'Tablet toko', pada: new Date('2026-09-19T' + jam + ':00+07:00').toISOString(), antrean: 0, gagal: 0 }, x || {}); };
var PP = __fj.periksaToko({ kini: kini('11:00'), jaga: hari, perangkat: [dv('10:10'), dv('10:10', { id: 'macOwner', akun: 'owner@contoh' }), dv('10:10', { id: 'hp~uKas', aplikasi: 'kasir' })], sudah: {} });
ok('periksaToko: tablet diam 50 menit di jam toko = "Tablet putus" (perangkat owner & aplikasi lama tidak); pulih = boleh dikabarkan lagi', PP.kabar.map(function (x) { return x.kunci; }).join() === 'putus-cpad~uTab'
  && __fj.periksaToko({ kini: kini('11:00'), jaga: hari, perangkat: [dv('10:58')], sudah: { 'putus-cpad~uTab': '10:45' } }).pulih.join() === 'putus-cpad~uTab', J(PP));
var PG = __fj.periksaToko({ kini: kini('11:00'), jaga: hari, perangkat: [dv('10:58', { gagal: 2 })], sudah: {} });
var PA1 = __fj.periksaToko({ kini: kini('11:00'), jaga: hari, perangkat: [dv('10:58', { antrean: 3 })], sudah: {} });
var PA2 = __fj.periksaToko({ kini: kini('11:15'), jaga: hari, perangkat: [dv('11:13', { antrean: 3 })], sudah: {}, antreLalu: PA1.antre });
ok('periksaToko: ditolak server = langsung dikabarkan; antrean baru dikabarkan bila masih menunggu di pemeriksaan berikutnya', PG.kabar[0].kunci === 'gagal-cpad~uTab' && PA1.kabar.length === 0 && PA2.kabar.map(function (x) { return x.kunci; }).join() === 'antre-cpad~uTab', J([PG, PA1, PA2]));
ok('omzet hari: Σ baris tidak batal + nota unik', J(__fj.omzetHari([{ hargaTotal: 100, trxId: 1 }, { hargaTotal: 50, trxId: 1 }, { hargaTotal: 70, trxId: 2 }, { hargaTotal: 999, trxId: 3, dibatalkan: true }])) === J({ rp: 220, nota: 2 }));
var NL = __fp.pesanNotif({ tindakan: 'hitungLaci', status: 'menunggu', tanggal: '2026-09-19', hitung: 1500000, dari: 'Sore' }, 'x1', { rp: 4250000, nota: 37 });
ok('kabar hitungan laci (tutup hari) menyebut omzet & jumlah nota; tanpa angka = seperti dulu', /omzet Rp4\.250\.000 dari 37 nota/.test(NL.isi) && !/omzet/.test(__fp.pesanNotif({ tindakan: 'hitungLaci', status: 'menunggu', tanggal: '2026-09-19', hitung: 1 }, 'x2').isi), J(NL));
var NK = __fp.pesanNotif(KS[1].data, 'k1');
ok('kabar toko ke HP owner berjudul jenisnya ("Jual di bawah modal · Pagi"); tugas owner tidak dikabarkan ke HP owner', NK.judul === 'Jual di bawah modal · Pagi' && /DI BAWAH MODAL/.test(NK.isi) && __fp.pesanNotif(tg, 't1') === null, J(NK));
var ND = __fp.pesanDariOwner(tg, 't1');
ok('tugas owner sampai ke tablet ("Tugas dari owner · wajib foto")', ND && ND.judul === 'Tugas dari owner · wajib foto' && ND.isi === 'Foto rak depan', J(ND));
ok('kabar toko ditandai dibaca TANPA balasan = tanpa push ke tablet; dengan balasan = dikabarkan', __fp.pesanPutus({ tindakan: 'kabarToko', status: 'menunggu', mintaUid: 'uTab' }, { tindakan: 'kabarToko', status: 'dibaca', mintaUid: 'uTab' }, 'k') === null
  && !!__fp.pesanPutus({ tindakan: 'kabarToko', status: 'menunggu', mintaUid: 'uTab' }, { tindakan: 'kabarToko', status: 'dibaca', mintaUid: 'uTab', balasan: 'oke' }, 'k'));
print(J({ lulus: lulus, gagal: gagal }));
"""

PRA = r"""
var S_HAK = function () { return SS_HAK_TABLET.map(function (x) { return x.id; }); };
var br = function (k) { return k; };
"""


def baca(ganti=None):
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(MODUL + LAYAR + [FJ, FP])))
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def jalan(t):
    js = JAM_TETAP + '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL])
    js += '\nvar __fj = (function () { var module = { exports: {} }; ' + t[FJ] + '\n return module.exports; })();\n'
    js += 'var __fp = (function () { var module = { exports: {} }; ' + t[FP] + '\n return module.exports; })();\n'
    js += '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + PRA + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-1200:]
    return json.loads(out[-1]), ''


def statis(t):
    out = []; ok = lambda n, c: out.append(('statis · ' + n, bool(c)))
    app, hg, mn, ug, lc, to, fb, fi = t[APP], t[HG], t[MN], t[UG], t[LC], t[TO], t[FB], t[FI]
    ok('Harga & Pemasok terbuka untuk staf ber-hak (pindah, chip & nav, pemulihan tab)', "(t === 'harga' && !!a && bisaBekerja(a) && a.jenis !== 'owner' && ssHakTablet(a.peran, 'harga'))" in app and app.count('!bolehLayarIni(a, ') == 3 and '!bolehLayar(a, ' not in app.replace('bolehLayar(a, t) ||', ''))
    nav = t[IDX][t[IDX].index('<nav class="nav"'):t[IDX].index('</nav>')]
    ok('nav bawah tablet: petak Harga di antara Pelanggan dan Menu (Menu tetap paling pojok), hanya akun staf ber-hak; petak Menu tidak ikut menyala',
       0 <= nav.find('data-tujuan="pelanggan"') < nav.find('<div data-tujuan="harga" data-staf="1" hidden>') < nav.find('data-tujuan="menu"')
       and "|| (el.dataset.staf === '1' && (!a || a.jenis === 'owner'));" in app and "((tujuan === 'harga' && !navHargaTampil()) ||" in app)
    ok('absen jaga ditulis tiap PIN / sidik jari berhasil (bukan owner, hanya Firestore)', 'setTimeout(() => catatJaga(op), 0);' in app and "if (!a || a.jenis === 'owner' || sumberData().jenis !== 'firestore' || !op) return;" in app and "tulisDokumen([{ koleksi: 'jagaLog', data }])" in app)
    ok('kabar toko hanya untuk nota BARU akun ini, saklar owner dihormati', "String(p.olehUid || '') === String(asli.uid || '')" in app and "if (!_ktSiap) { semua.forEach((p) => p && _ktLihat.add(String(p.id))); _ktSiap = true; return; }" in app and '.filter((x) => KT[x.data.jenis] !== false)' in app)
    ok('layar Harga staf: tampilan tablet sendiri, tidak ada yang langsung berubah', 'if (stafKini())' in hg and 'gambarStaf(' in hg)
    ok('Menu tablet: kartu tugas owner + input foto (change), papan Persetujuan "lihat foto", setelan kabar', '${kartuTugasStaf(s, { akun: akunM, kini: kini() })}\n      ${kartuTugasOwner(s, { akun: akunM })}' in mn and "ev.target.closest('[data-to-foto]')" in mn and 'gambarFotoBukti(s, m.tugasId)' in mn and '${gambarKabarToko(s)}' in mn)
    ok('tugas: foto hanya untuk tugas wajib foto, tersimpan dulu baru jawabannya', "${t.wajibFoto ? h`<div class=\"tombol-baris\"" in to and 'const F = await foto.simpan(data); if (F && F.gagal) return' in to)
    ok('Uang: Minta foto di titipan menunggu + rekap absen di Upah', 'data-aksi="ukMintaFoto"' in ug and "kbSusunTugasOwner('Foto bukti titipan '" in ug and 'JG.jgRekapOrang(nama, iso(), 7)' in ug and ug.count('${absen}') == 3)
    ok('lonceng owner: Pesan / Tugas / Tugas + wajib foto', "['tugasFoto', 'Tugas + wajib foto']" in lc and "kbSusunTugasOwner(_lcTulis, _lcJenis === 'tugasFoto', w, _lcAkun, '')" in lc)
    ok('firebase: foto nota terbaca akun bertanda hakFotoNota, foto bukti dijaga buktiSah, dibaca owner saja', "status.akun.hakFotoNota === true" in fb and "if (!owner0 && !buktiSah(d))" in fb and 'export async function bacaFotoBukti(tugasId) {\n  if (!db) throw new Error(\'belum tersambung\');\n  if (pemilikSaja())' in fb)
    ok('fungsi server: kabarJaga (jagaLog dibuat) + periksaToko tiap 15 menit WIB + omzet di kabar hitungan laci', "exports.kabarJaga = onDocumentCreated('jagaLog/{id}'" in fi and "schedule: '*/15 6-23 * * *', timeZone: 'Asia/Jakarta'" in fi and 'pesanNotif(d, event.params.id, tambah)' in fi)
    return out


def semua(ganti=None):
    t = baca(ganti); out = statis(t); h, e = jalan(t)
    if h is None: return out + [('JSC JATUH: ' + e, False)]
    return out + [('jsc · ' + x, False) for x in h['gagal']] + [('__jsc', not h['gagal'], h['lulus'])]


RUSAK = [
    ('hak tablet bawaan menyala', SL, "hakTablet: { ben: {}, karyawan: {} }, kabarTablet", "hakTablet: { ben: { harga: true }, karyawan: {} }, kabarTablet"),
    ('foto nota boleh untuk Karyawan', SL, "if (H.hanya && H.hanya !== peran) return { tolak: H.nama + ' hanya untuk Penjaga laci' };", ""),
    ('tanda foto nota tidak ditulis ke akun', SL, "if (id === 'fotoNota') cacheMentah('aksesAkun')", "if (id === 'fotoNotaX') cacheMentah('aksesAkun')"),
    ('akun baru tidak ikut hak foto nota', SL, "if (peran === 'ben' && ssHakTablet('ben', 'fotoNota')) data.hakFotoNota = true;", ""),
    ('pindah peran tidak mematikan tanda foto', SL, "a.hakFotoNota ? { hakFotoNota: false } : {};", "{};"),
    ('keadaanAkun tidak membawa hakFotoNota', AK, ", hakFotoNota: peran === 'ben' && dok.hakFotoNota === true };", " };"),
    ('usul tablet boleh membawa keputusan owner', AK, "&& d.teks.length > 0 && d.teks.length <= 500 && !KEPUTUSAN_USUL.some((k) => k in d);", "&& d.teks.length > 0 && d.teks.length <= 500;"),
    ('absen jaga tanpa batas kolom', AK, "if (!d || typeof d !== 'object' || Object.keys(d).some((k) => JAGA_KOLOM.indexOf(k) < 0)) return false;\n  return typeof d.id", "if (!d || typeof d !== 'object') return false;\n  return typeof d.id"),
    ('usul harga jual di bawah modal ikut terbit', HL, "if (N && N.status === 'rugi') return", "if (false) return"),
    ('kabar toko dibaca tanpa balasan', SL, "if (m.tindakan === 'kabarToko' || m.tindakan === 'tugasSelesai') { const bal = String(alasan || '').trim().slice(0, 200);", "if (m.tindakan === 'tugasSelesai') { const bal = String(alasan || '').trim().slice(0, 200);"),
    ('kabar toko dobel per hari', KB, "if (sudah[id] || pernah[id]) return; pernah[id] = true;", "pernah[id] = true;"),
    ('kabar bawah modal tidak diperiksa', KB, "if (hpp > 0 && harga > 0 && harga + 0.5 < hpp)", "if (false)"),
    ('tugas wajib foto tanpa foto lolos', KB, "if (tugas.wajibFoto && !fotoId) return { tolak:", "if (false) return { tolak:"),
    ('tugas terjawab tetap terbuka', KB, "m.tindakan === KB_TUGAS_OWNER && !jawab[String(m.id)]", "m.tindakan === KB_TUGAS_OWNER"),
    ('saklar kabar tablet ditulis ke dokumen server', SL, "const r = x.dok === 'peran' ? susunAturSistem('peran',", "const r = x.dok === 'peranX' ? susunAturSistem('peran',"),
    ('jam tutup sebelum buka diterima', SL, "if (!tolak && o.jamTutup <= o.jamBuka) tolak = 'Jam tutup harus sesudah jam buka';", ""),
    ('absen: nama dicocokkan kata pertama saja', JG, "return p.every((w, i) => q[i] === w);", "return p[0] === q[0];"),
    ('absen: PIN berturut digabung hilang', JG, "if (k && k.nama === nm) { k.kali += 1; return; }", ""),
    ('absen: jam selesai terakhir ditebak', JG, "x.menit = x.sampai ? jgKeMenit(x.sampai) - jgKeMenit(x.mulai) : null;", "x.menit = jgKeMenit(x.sampai || '21:00') - jgKeMenit(x.mulai);"),
    ('server: orang sama lagi dikabarkan', FJ, "if (teks(sebelum.nama).toLowerCase() === nama.toLowerCase()) return null;", ""),
    ('server: kabar dobel sehari', FJ, "const tambah = (kunci, judul, isi) => { if (!sudah[kunci]) out.push(", "const tambah = (kunci, judul, isi) => { if (true) out.push("),
    ('server: perangkat owner dikira tablet', FJ, "String(p.id || '').indexOf('~') < 0 ||", ""),
    ('server: antrean sesaat langsung dikabarkan', FJ, "if (k.antreLalu && Number(k.antreLalu[p.id]) > 0) tambah(", "tambah("),
    ('server: omzet hilang dari kabar tutup', FP, "+ (tambah && Number(tambah.nota) > 0 ? ' · omzet '", "+ (false ? ' · omzet '"),
    ('server: tugas owner tidak sampai tablet', FP, "(d.tindakan !== 'pesanOwner' && d.tindakan !== 'tugasOwner')", "d.tindakan !== 'pesanOwner'"),
    ('tablet: absen tidak ditulis', APP, "setTimeout(() => catatJaga(op), 0);", ""),
    ('tablet: Harga tetap tertutup untuk staf ber-hak', APP, "(t === 'harga' && !!a && bisaBekerja(a) && a.jenis !== 'owner' && ssHakTablet(a.peran, 'harga'))", "false"),
    ('nav: petak Harga tampil juga di HP owner', APP, "|| (el.dataset.staf === '1' && (!a || a.jenis === 'owner'));", ";"),
    ('nav: petak Harga sesudah Menu', IDX, '<div data-tujuan="harga" data-staf="1" hidden>', '<div data-tujuan="hargaX" data-staf="1" hidden>'),
    ('tablet: saklar kabar diabaikan', APP, ".filter((x) => KT[x.data.jenis] !== false)", ""),
    ('firebase: foto nota tertutup untuk akun bertanda', FB, "status.akun.hakFotoNota === true", "false"),
]


def utama():
    if '--kontrol' in sys.argv:
        lolos = []
        for nama, b, lama, baru in RUSAK:
            hasil = semua({b: [(lama, baru)]})
            if all(x[1] for x in hasil): lolos.append(nama); print('LOLOS (seharusnya gagal):', nama)
            else: print('  tertangkap:', nama)
        if not all(x[1] for x in semua()): print('GAGAL: salinan utuh tidak lulus'); return 3
        print('KONTROL ' + ('LULUS' if not lolos else 'GAGAL') + ' ' + str(len(RUSAK) - len(lolos)) + '/' + str(len(RUSAK)))
        return 0 if not lolos else 3
    hasil = semua(); gagal = [x for x in hasil if not x[1]]; n = sum(1 for x in hasil if x[1] and not x[0].startswith('__')) + next((x[2] for x in hasil if x[0] == '__jsc'), 0)
    for x in gagal: print('GAGAL', x[0])
    print('TABLET SAAT OWNER PERGI: ' + str(n) + ' lulus · ' + str(len(gagal)) + ' gagal')
    return 0 if not gagal else 1


if __name__ == '__main__':
    sys.exit(utama())
