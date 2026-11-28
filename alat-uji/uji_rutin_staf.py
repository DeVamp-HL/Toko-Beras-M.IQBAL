#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_rutin_staf.py — PAKET P6 · Rutinitas, tutup hari & halaman staf (owner 27 Nov 2026; sensus ulang 27 Nov: A82 A119 A143 B116).
KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  A143  daftar centang rutin harian · mingguan · bulanan (rutin-logika): bawaan ±30 butir sah · putaran (hari / Senin / bulan) & jatuh · siapa melihat apa (owner semua,
        Penjaga laci = semua + penjaga, karyawan = semua) · centang = satu dokumen rutinCek berbentuk rules v25 (cekRutinSah) · dobel / di luar peran / butir otomatis
        ditolak · dua centang bersamaan = yang PERTAMA · butir otomatis dari layar sumbernya (hitungan laci tablet, tutup hari, cek gudang, karcis) · lewat sesudah jatuh
        · atur daftar (owner) · batal centang (owner) · riwayat siapa mencentang · Dasbor = angka yang sama.
  A119  alarm selisih laci BERULANG (laci-logika): bawaan 3 berturut-turut / 4 dari 7 malam · setelan owner menggeser · malam > 30 hari tidak ikut · selisih tiap malam
        = bacaTutup (tutup-hari-logika) apa adanya · tren 7 / 30 malam · per orang yang menghitung · Pengingat & lonceng owner (lokal.peringatan, jenis laci) · Dasbor.
  A82   alasan selisih BEBAS (diketik owner, tertulis di tutupHari) · catatan bebas Penjaga laci ikut hitungan tablet (rules v16 tanpa kolom baru, hitung buta tetap) →
        sampai di malam itu (dariTablet.catatan) · "Belum ketemu — cari besok" ditagih pengingat tiap hari sampai penjelasan susulan ditulis (susunJelaskanLaci).
  B116  halaman tugas staf (tugas-staf-logika): rutin · wadah · pesanan & antar · janji bayar · karcis · titipan — sama untuk semua staf; mendarat = ben & karyawan saja;
        semua sumbernya terbaca akun staf (pendengarPeran + v25: aturanToko/rutin & rutinCek).

    python3 alat-uji/uji_rutin_staf.py            → N lulus · 0 gagal (+ asap cadangan toko bila ada; angka rupiah toko tidak dicetak)
    python3 alat-uji/uji_rutin_staf.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_jual_baru, uji_dasbor_sensus, uji_sisa_sensus, uji_gudang_label_patuh  # noqa: E402
LH = 'baru/js/layar/laci-logika.js'; RN = 'baru/js/layar/rutin-logika.js'; TS = 'baru/js/layar/tugas-staf-logika.js'; HL = 'baru/js/layar/tutup-tablet-logika.js'
TD = 'baru/js/layar/tutup-hari-logika.js'; AK = 'baru/js/data/akses.js'; SS = 'baru/js/layar/sistem-logika.js'; DL = 'baru/js/layar/dasbor-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_gudang_label_patuh.MODUL + [LH, RN, TS, HL])))
SUMBER = {'app': 'baru/js/app.js', 'menu': 'baru/js/layar/menu.js', 'mlog': 'baru/js/layar/menu-logika.js', 'uang': 'baru/js/layar/uang.js', 'dasbor': 'baru/js/layar/dasbor.js',
          'panel': 'baru/js/layar/rutin-panel.js', 'hlp': 'baru/js/layar/tutup-tablet-panel.js', 'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml',
          'baca': 'baru/BACA-DULU.md', 'bundel': 'alat-uji/bundel_baru.py', 'rules': 'firestore.rules', 'koleksi': 'baru/js/data/koleksi.js', 'peta': 'alat-uji/peta_akses.py',
          'css_menu': 'baru/css/menu.css', 'css_uang': 'baru/css/uang.css', 'css_ring': 'baru/css/ringkasan.css',
          'lh': LH, 'rn': RN, 'ts': TS, 'hl': HL, 'td': TD, 'ak': AK, 'ss': SS, 'dl': DL}

D_ = 'Pelanggan Contoh D'
def MALAM(tgl, s, **k):
    x = {'id': tgl, 'tanggal': tgl, 'jam': '21:00', 'omzet': 1000000, 'selisihLaci': s, 'selisih': s, 'alasanSelisih': '', 'sistemBaru': True, 'kasFisikLaci': 1000000, 'kasAwalBesokLaci': 1000000}
    x.update(k); return x
KOTAK = {
    'penjualan': [
        {'id': 'n1', 'tanggal': '2026-11-20', 'jam': '09:00', 'caraBayar': 'Kredit', 'namaPelanggan': D_, 'jenis': 'karung', 'merkSumber': 'Angsa', 'beratKarungAcuan': 50, 'jumlahKarung': 1, 'totalKg': 50, 'hargaTotal': 650000, 'hppTotalSaatJual': 600000, 'grupNota': 'gn1'},
        {'id': 'kc1', 'tanggal': '2026-12-02', 'jam': '10:00', 'jenis': 'kasir_darurat_nominal', 'hargaTotal': 50000, 'caraBayar': 'Tunai', 'trxId': 'KC1'}],
    'tutupHari': [MALAM('2026-12-01', 50000, dariTablet={'id': 'hl-lama', 'oleh': 'UJI B', 'jam': '20:30', 'hitung': 1050000, 'sesudah': 0, 'amankan': 0, 'catatan': 'bensin belum dicatat'}),
                  MALAM('2026-11-30', -20000, alasanSelisih='Belum ketemu — cari besok'), MALAM('2026-11-29', 8000, alasanSelisih='Salah kasih kembalian'),
                  MALAM('2026-11-28', 3000), MALAM('2026-11-27', 0), MALAM('2026-11-26', 100000, alasanSelisih='Belum tahu — dicari besok', penjelasan={'teks': 'uang titipan tetangga', 'tanggal': '2026-11-27', 'jam': '08:00'}),
                  MALAM('2026-11-25', None, selisih=None), MALAM('2026-10-01', -900000)],
    'pesanan': [{'id': 'p1', 'tanggal': '2026-11-30', 'jam': '10:00', 'namaPelanggan': 'Warung Contoh', 'status': 'dipesan', 'tanggalKirim': '2026-12-02', 'isi': '2 karung Angsa', 'baris': []},
                {'id': 'p2', 'tanggal': '2026-11-30', 'jam': '10:00', 'namaPelanggan': 'Warung Jauh', 'status': 'dipesan', 'tanggalKirim': '2026-12-09', 'isi': '1 karung', 'baris': []}],
    'cekGudang': [{'id': 'cg1', 'tanggal': '2026-11-30', 'jam': '08:00', 'cek': {'timbangan': True, 'palet': True, 'bocor': True, 'lembap': True, 'kutu': True}, 'catatan': '', 'oleh': 'UJI B'}],
}
ATUR = [{'id': 'tutupHari', 'persenSisih': 10, 'kembalian': 2000000, 'maafSelisih': 5000, 'alasan': ['Salah kasih kembalian', 'Ada pengeluaran belum dicatat']}, {'id': 'catatStok', 'tempoHari': 21}]

SKENARIO = r"""
(function () {
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); };
var KINI = new Date('2026-12-02T14:00:00+07:00'); var nId = 90000; var iso = '2026-12-02'; var D_ = 'Pelanggan Contoh D';
var W = { tanggal: '2026-12-02', jam: '14:00', kini: '2026-12-02T07:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK0).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'penyesuaianStok', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'stokBahanKemasan', 'pesanan', 'karantina', 'persetujuan', 'pengeluaranHarian', 'absenKaryawan', 'pajakSetoran', 'pajakOmzetLuar', 'pesananPemasok', 'pengingat',
 'tutupHari', 'suratJalan', 'tagihPelanggan', 'cekGudang', 'rutinCek', 'kepatuhanCek', 'ambilBarang', 'cadanganCatatan'].forEach(function (n) { pasok(n, []); });
Object.keys(GK).forEach(function (n) { pasok(n, JSON.parse(J(GK[n]))); });
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-12-01', laci: 1000000, brankas: 0, rekening: 0, amplop: 0, diubahPada: '2026-12-01T14:00:00.000Z' }]);
setelSumber('cadangan', 'kotak pasir');
var aturDengan = function (extra) { var e = extra || []; var id = {}; e.forEach(function (d) { id[d.id] = 1; }); pasok('aturanToko', JSON.parse(J(ATUR)).filter(function (d) { return !id[d.id]; }).concat(e)); };
aturDengan([]);
var akO = { jenis: 'owner', uid: 'uid-owner', nama: 'Owner' };
var akB = keadaanAkun('ben.contoh@contoh.com', 'uid-ben', { uid: 'uid-ben', nama: 'UJI B', peran: 'ben', aktif: true });
var akK = keadaanAkun('kry@contoh.com', 'uid-kry', { uid: 'uid-kry', nama: 'UJI K', peran: 'karyawan', aktif: true });
var HK = { hitungLaci: 'sendiri' }; Object.keys(SERVER_BUKA).forEach(function (t) { HK[t] = 'sendiri'; });
var rc = function (b, p, oleh, jam, tgl) { return { id: 'rc-' + (tgl || iso) + '-' + b + (jam || ''), tanggal: tgl || iso, jam: jam || '09:00', butir: b, periode: p, catatan: '', oleh: oleh || 'UJI K' }; };

// ==================== 1 · A143 DAFTAR RUTIN ====================
var A0 = rnAtur(); var ids = A0.butir.map(function (b) { return b.id; });
ok('1: bawaan ±30 butir, semuanya sah (id unik, ulang dikenal, otomatis dikenal) & tidak dariOwner', A0.butir.length === RN_BAWAAN.length && RN_BAWAAN.length >= 28 && RN_BAWAAN.length <= RN_BATAS.butir && new Set(ids).size === ids.length && !A0.dariOwner
  && RN_BAWAAN.every(function (b) { return !b.otomatis || RN_OTOMATIS[b.otomatis]; }), J([A0.butir.length, RN_BAWAAN.length]));
ok('1: tiga kelompok ada: harian, mingguan, bulanan', ['harian', 'mingguan', 'bulanan'].every(function (u) { return A0.butir.some(function (b) { return b.ulang === u; }); }));
ok('1: putaran — harian = tanggal · mingguan = Senin · bulanan = bulan', rnPeriode('harian', iso) === iso && rnPeriode('mingguan', iso) === '2026-11-30' && rnPeriode('mingguan', '2026-12-06') === '2026-11-30' && rnPeriode('mingguan', '2026-12-07') === '2026-12-07' && rnPeriode('bulanan', iso) === '2026-12', J([rnPeriode('mingguan', iso)]));
ok('1: jatuh — mingguan hari 5 = Jumat minggu itu · bulanan 15 = tgl 15 · bulanan 0 = akhir bulan (28 Feb)', rnJatuh({ ulang: 'mingguan', hari: 5 }, iso) === '2026-12-04' && rnJatuh({ ulang: 'bulanan', hari: 15 }, iso) === '2026-12-15' && rnJatuh({ ulang: 'bulanan', hari: 0 }, '2027-02-10') === '2027-02-28');
ok('1: periode bentuk rules v25 (YYYY-MM-DD / YYYY-MM)', [rnPeriode('harian', iso), rnPeriode('mingguan', iso), rnPeriode('bulanan', iso)].every(function (p) { return /^\d{4}-\d{2}(-\d{2})?$/.test(p); }));
var RO = rnHari(KINI, akO), RB = rnHari(KINI, akB), RK = rnHari(KINI, akK);
ok('1: owner melihat semua butir menyala; Penjaga laci = semua + penjaga; karyawan = semua saja', RO.baris.length === A0.butir.filter(function (b) { return b.nyala; }).length
  && RB.baris.every(function (b) { return b.untuk !== 'owner'; }) && RB.baris.some(function (b) { return b.untuk === 'penjaga'; }) && RK.baris.every(function (b) { return b.untuk === 'semua'; }) && RK.baris.length > 0, J([RO.baris.length, RB.baris.length, RK.baris.length]));
ok('1: sebelum ada centang: harian manual = belum, bukan lewat', RK.baris.filter(function (b) { return b.ulang === 'harian' && !b.otomatis; }).every(function (b) { return b.keadaan === 'belum' && b.bisaCentang; }));
var bP = RO.baris.find(function (b) { return b.id === 'putar-karung'; });
ok('1: mingguan jatuh Senin 30 Nov, belum dicentang 2 Des = LEWAT', bP && bP.keadaan === 'lewat' && bP.periode === '2026-11-30', J(bP));
var bB = RO.baris.find(function (b) { return b.id === 'banding'; });
ok('1: mingguan jatuh Jumat (sesudah hari ini) = NANTI, tetap boleh dicentang lebih awal', bB && bB.keadaan === 'nanti' && bB.bisaCentang, J(bB));
ok('1: jatuh sebelum RN_MULAI tidak ditagih (28 Nov: Senin 23 Nov jatuh sebelum daftar lahir 27 Nov = belum, bukan lewat)', (function () { var R = rnHari(new Date('2026-11-28T14:00:00+07:00'), akO); var x = R.baris.find(function (b) { return b.id === 'putar-karung'; }); return x && x.keadaan === 'belum'; })());
// centang
var r1 = susunCentangRutin('bersih', 'sudah disapu', W, akK, KINI); var d1 = r1.dokumen && r1.dokumen[0];
ok('1: karyawan mencentang butir "semua" = satu dokumen rutinCek berbentuk rules v25 (cekRutinSah) & kolom RN_CEK_KOLOM', d1 && d1.koleksi === 'rutinCek' && cekRutinSah(Object.assign({}, d1.data, { olehUid: 'uid-kry', oleh: 'UJI K' }))
  && J(Object.keys(d1.data).sort()) === J(RN_CEK_KOLOM.slice().sort()) && d1.data.periode === iso && d1.data.butir === 'bersih', J(r1));
ok('1: kiriman karyawan lolos penjaga perangkat; bentuk di luar rules v25 ditolak', !periksaKiriman(akK, [{ koleksi: 'rutinCek', data: Object.assign({}, d1.data, { olehUid: 'uid-kry' }), ada: false, lama: null }], [], HK).tolak
  && !!periksaKiriman(akK, [{ koleksi: 'rutinCek', data: Object.assign({}, d1.data, { nominal: 5 }), ada: false, lama: null }], [], HK).tolak
  && !!periksaKiriman(akK, [{ koleksi: 'rutinCek', data: Object.assign({}, d1.data, { periode: '2026-W49' }), ada: false, lama: null }], [], HK).tolak, J(periksaKiriman(akK, [{ koleksi: 'rutinCek', data: d1.data, ada: false, lama: null }], [], HK)));
ok('1: karyawan TIDAK boleh mencentang butir Penjaga laci / owner; butir otomatis ditolak', !!susunCentangRutin('buka-harga', '', W, akK, KINI).tolak && !!susunCentangRutin('rekening', '', W, akB, KINI).tolak && !!susunCentangRutin('cek-wadah', '', W, akO, KINI).tolak
  && !susunCentangRutin('buka-harga', '', W, akB, KINI).tolak && !susunCentangRutin('rekening', '', W, akO, KINI).tolak);
var oh = function (R, id) { return R.baris.find(function (b) { return b.id === id; }); };
ok('1: butir otomatis yang belum beres (karcis hari ini) ditolak dengan kalimat "kerjakan di sana"', /tercatat sendiri/.test(String(susunCentangRutin('karcis', '', W, akO, KINI).tolak || '')), J(susunCentangRutin('karcis', '', W, akO, KINI)));
ok('1: cek gudang minggu LALU (Sabtu 28 Nov) tidak menutup minggu ini', (function () { pasok('cekGudang', [Object.assign({}, GK.cekGudang[0], { tanggal: '2026-11-28' })]); var x = oh(rnHari(KINI, akB), 'cek-gudang'); pasok('cekGudang', JSON.parse(J(GK.cekGudang))); return x && !x.sudah && x.keadaan === 'lewat'; })());
ok('1: catatan > 160 huruf ditolak', !!susunCentangRutin('bersih', new Array(170).join('x'), W, akK, KINI).tolak);
pasok('rutinCek', [rc('bersih', iso, 'UJI K', '09:00'), rc('bersih', iso, 'UJI B', '09:05'), rc('putar-karung', '2026-11-30', 'UJI B', '08:00', '2026-12-01'), rc('palet', '2026-12-01', 'UJI K', '09:00', '2026-12-01')]);
var R2 = rnHari(KINI, akO); var x2 = R2.baris.find(function (b) { return b.id === 'bersih'; }); var x3 = R2.baris.find(function (b) { return b.id === 'putar-karung'; });
ok('1: sesudah centang: sudah · oleh orang PERTAMA (dua centang bersamaan = yang pertama dihitung) · tidak bisa dicentang lagi', x2 && x2.sudah && x2.oleh === 'UJI K' && x2.jam === '09:00' && !x2.bisaCentang && !!susunCentangRutin('bersih', '', W, akB, KINI).tolak, J(x2));
ok('1: mingguan dicentang hari lain minggu itu = sudah untuk seluruh minggu', x3 && x3.sudah && x3.keadaan === 'sudah', J(x3));
ok('1: centang kemarin tidak menutup putaran hari ini (harian)', R2.baris.find(function (b) { return b.id === 'palet'; }).keadaan === 'belum');
// otomatis
ok('1: otomatis hitung laci — belum ada hitungan hari ini = belum; hitungan tablet hari ini (menunggu) = sudah, oleh Penjaga laci', (function () { var a = oh(rnHari(KINI, akB), 'hitung-laci').keadaan; pasok('persetujuan', [{ id: 'hl1', tindakan: 'hitungLaci', status: 'menunggu', tanggal: iso, jam: '20:00', dari: 'UJI B', hitung: 100000, amankan: 0, mintaUid: 'uid-ben' }]);
  var b = oh(rnHari(KINI, akB), 'hitung-laci'); pasok('persetujuan', [{ id: 'hl1', tindakan: 'hitungLaci', status: 'ditolak', tanggal: iso, jam: '20:00', dari: 'UJI B', hitung: 100000, amankan: 0 }]); var c = oh(rnHari(KINI, akB), 'hitung-laci').keadaan; pasok('persetujuan', []);
  return a === 'belum' && b.sudah && b.oleh === 'UJI B' && c === 'belum'; })());
ok('1: otomatis tutup hari (owner): malam ini belum ditutup = belum; ditutup = sudah', (function () { var a = oh(rnHari(KINI, akO), 'tutup-hari').keadaan; var T = JSON.parse(J(GK.tutupHari)); pasok('tutupHari', T.concat([MALAM_INI])); var b = oh(rnHari(KINI, akO), 'tutup-hari').keadaan; pasok('tutupHari', T); return a === 'belum' && b === 'sudah'; })());
ok('1: otomatis cek gudang (Senin) — cek 30 Nov = sudah minggu ini', oh(rnHari(KINI, akB), 'cek-gudang').sudah);
ok('1: otomatis karcis — karcis darurat HARI INI belum dirinci = belum', oh(rnHari(KINI, akB), 'karcis').keadaan === 'belum' && /1 karcis/.test(oh(rnHari(KINI, akB), 'karcis').teks));
ok('1: otomatis cadangan / cek aturan untuk staf = tidak terbaca (disebut, tidak ditebak) & tidak ikut hitungan', (function () { var R = rnHari(KINI, akB); return R.n === R.baris.filter(function (b) { return b.keadaan !== 'tidakTerbaca'; }).length; })());
// atur
ok('1: atur daftar (owner) — hari mingguan di luar 1–7 / tanpa nama ditolak', !!susunAturRutin({ butir: [{ nama: 'X', ulang: 'mingguan', hari: 9, untuk: 'semua' }] }, W).tolak && !!susunAturRutin({ butir: [{ nama: '', ulang: 'harian' }] }, W).tolak
  && !!susunAturRutin({ butir: [{ nama: 'X', ulang: 'bulanan', hari: 31 }] }, W).tolak);
var ra = susunAturRutin({ butir: [{ nama: 'Sapu', ulang: 'harian', untuk: 'semua' }, { id: 'putar-karung', nama: 'Putar karung', ulang: 'mingguan', hari: 3, untuk: 'penjaga' }, { nama: 'Rekening', ulang: 'bulanan', hari: '', untuk: 'owner', nyala: false }] }, W);
ok('1: atur daftar tersimpan di aturanToko/rutin (id lama dipertahankan, bulanan kosong = akhir bulan)', ra.dokumen && ra.dokumen[0].koleksi === 'aturanToko' && ra.dokumen[0].data.id === 'rutin' && ra.dokumen[0].data.butir.length === 3
  && ra.dokumen[0].data.butir[1].id === 'putar-karung' && ra.dokumen[0].data.butir[2].hari === 0, J(ra));
aturDengan([ra.dokumen[0].data]);
ok('1: daftar owner berlaku (dariOwner) · butir mati tidak tampil · karyawan tidak melihat butir penjaga', rnAtur().dariOwner && rnHari(KINI, akO).baris.length === 2 && rnHari(KINI, akK).baris.length === 1, J(rnHari(KINI, akO).baris.map(function (b) { return b.id; })));
aturDengan([]);
ok('1: batal centang — hanya owner, berupa hapus dokumen', !!susunBatalRutin('rc-' + iso + '-bersih09:00', akB).tolak && J(susunBatalRutin('rc-' + iso + '-bersih09:00', akO).hapus) === J([{ koleksi: 'rutinCek', id: 'rc-' + iso + '-bersih09:00' }]));
var RW = rnRiwayat(KINI, 7);
ok('1: riwayat siapa mencentang per hari (harian manual) — 2 Des: UJI K 1; 1 Des: UJI K 1; tidak mundur sebelum RN_MULAI', RW.hari[0].iso === iso && RW.hari[0].oleh['UJI K'] === 1 && !RW.hari[0].oleh['UJI B'] && RW.hari[1].oleh['UJI K'] === 1 && RW.hari.every(function (x) { return x.iso >= RN_MULAI; }), J(RW.hari.slice(0, 2)));
var RD = rnDasbor(KINI); var hO = rnHari(KINI, akO).kelompok.find(function (k) { return k.ulang === 'harian'; });
ok('1: Dasbor = angka Menu › Toko ini › Rutin (harian x dari y) + kemarin terlewat = harian manual tanpa centang 1 Des', RD.harian.n === hO.n && RD.harian.nSudah === hO.nSudah && RD.kemarin === '2026-12-01' && RD.terlewat.indexOf('Karung di atas palet, tidak menempel dinding') < 0 && RD.terlewat.indexOf('Sapu & rapikan toko, buang karung bekas') >= 0
  && RD.terlewat.indexOf('Cek wadah literan saat tutup') < 0 && RD.terlewat.indexOf('Hitung laci & kirim ke owner') < 0, J(RD));
ok('1: Dasbor › Mutu memuat kelompok rutin yang sama', J(dbMutu(KINI).rutin.harian) === J(RD.harian));

// ==================== 2 · A119 ALARM & TREN SELISIH LACI ====================
var AT = lhAtur();
ok('2: bawaan 3 berturut / 4 dari 7, batas maaf = aturTutup (5.000 owner)', AT.beruntun === 3 && AT.dalam === 4 && AT.jendela === 7 && AT.maaf === aturTutup().maafSelisih && AT.maaf === 5000 && !AT.dariOwner, J(AT));
ok('2: selisih tiap malam = bacaTutup apa adanya', GK.tutupHari.every(function (d) { var a = lhBaca(d, AT).selisih; var b = bacaTutup(d).selisih; return (a === null && (b === null || b === undefined)) || a === b; }));
var L = lhAlarm(KINI);
ok('2: 1 Des +50 rb · 30 Nov −20 rb · 29 Nov +8 rb (lewat 5 rb) = 3 berturut-turut → ALARM', L.nyala && L.beruntun === 3 && L.kenaBeruntun && L.dalam === 4 && L.jendela === 7 && L.lebih === 158000 && L.kurang === -20000, J([L.beruntun, L.dalam, L.jendela, L.lebih, L.kurang]));
ok('2: malam 1 Okt (> 30 hari) tidak ikut alarm; 15 Jan 2027 (semua malam basi) = alarm tidak berbunyi', L.malam.every(function (m) { return m.tanggal >= '2026-11-01'; })
  && (function () { var X = lhAlarm(new Date('2027-01-15T14:00:00+07:00')); return !X.nyala && X.jendela === 0 && /Belum ada malam/.test(X.kalimat); })());
ok('2: 3 Rp dimaafkan (28 Nov) bukan malam berselisih; malam tanpa patokan (25 Nov) bukan berselisih', !L.malam.find(function (m) { return m.tanggal === '2026-11-28'; }).lewat && !L.malam.find(function (m) { return m.tanggal === '2026-11-25'; }).lewat);
aturDengan([{ id: 'selisihLaci', alarmBeruntun: 4, alarmDalam: 4, alarmJendela: 7 }]); var L2 = lhAlarm(KINI);
aturDengan([{ id: 'selisihLaci', alarmBeruntun: 4, alarmDalam: 5, alarmJendela: 7 }]); var L3 = lhAlarm(KINI);
aturDengan([{ id: 'selisihLaci', alarmBeruntun: 3, alarmDalam: 4, alarmJendela: 7, nyala: false }]); var L4 = lhAlarm(KINI); aturDengan([]);
ok('2: setelan owner — 4 berturut tak tercapai tapi 4 dari 7 tercapai = nyala; 5 dari 7 = mati; saklar mati = mati', L2.nyala && !L2.kenaBeruntun && L2.kenaDalam && !L3.nyala && !L4.nyala && L2.A.dariOwner, J([L2.nyala, L3.nyala, L4.nyala]));
var sa = susunAturLaci({ alarmBeruntun: '2', alarmDalam: '3', alarmJendela: '5' }, W);
ok('2: simpan setelan = aturanToko/selisihLaci; di luar batas ditolak; "dari M" tidak boleh > jendela', sa.dokumen && sa.dokumen[0].data.id === 'selisihLaci' && sa.dokumen[0].data.alarmBeruntun === 2 && sa.dokumen[0].data.alarmDalam === 3 && sa.dokumen[0].data.alarmJendela === 5
  && !!susunAturLaci({ alarmBeruntun: '1' }, W).tolak && !!susunAturLaci({ alarmDalam: '9', alarmJendela: '7' }, W).tolak && !!susunAturLaci({ alarmJendela: '40' }, W).tolak, J(sa));
var T7 = lhTren(KINI, 7), T30 = lhTren(KINI, 30);
ok('2: tren 7 malam (urut lama → baru) & 30 malam (semua yang ada) — lewat, pas, dimaafkan, tanpa patokan terhitung', T7.n === 7 && T7.malam[6].tanggal === '2026-12-01' && T7.malam[0].tanggal === '2026-11-25' && T7.nLewat === 4 && T7.nPas === 1 && T7.nDimaafkan === 1 && T7.nTanpa === 1
  && T30.n === 8 && T30.nLewat === 5 && T30.kurang === -920000, J([T7.n, T7.nLewat, T7.nPas, T7.nDimaafkan, T7.nTanpa, T30.n, T30.nLewat, T30.kurang]));
var PO = lhPerOrang(KINI, 30);
ok('2: per orang yang menghitung — malam tablet = nama Penjaga laci, sisanya owner', PO.find(function (x) { return x.nama === 'UJI B'; }).n === 1 && PO.find(function (x) { return x.nama === 'UJI B'; }).jumlah === 50000 && PO.find(function (x) { return x.nama === 'UJI B'; }).lebih === 50000 && PO.find(function (x) { return x.nama === 'owner'; }).kurang === -920000 && PO.find(function (x) { return x.nama === 'owner'; }).lebih === 108000 && PO.find(function (x) { return x.nama === 'owner'; }).n === 7, J(PO));
var SP = lhSumberPengingat(KINI); var spJ = function (j) { return SP.filter(function (x) { return x.jenis === j; }); };
ok('2: pengingat — satu baris alarm (laci|malam terakhir, jatuh hari ini)', spJ('laci').length === 1 && spJ('laci')[0].id === 'laci|2026-12-01' && spJ('laci')[0].jatuh === iso, J(SP));
var PG = ssPengingat(KINI, { peringatan: SP }).aktif; var PG0 = ssPengingat(KINI, {}).aktif;
ok('2: Pengingat (lokal.peringatan) memuat jenis laci & jelaskan; tanpa lokal (akun bukan owner) = tidak ada', PG.some(function (p) { return p.jenis === 'laci'; }) && PG.some(function (p) { return p.jenis === 'jelaskan'; }) && !PG0.some(function (p) { return SS_JENIS_LACI.indexOf(p.jenis) >= 0; })
  && SS_JENIS_LACI.every(function (j) { return SS_JENIS_PENGINGAT.some(function (x) { return x.id === j; }) && SS_ATUR_BAWAAN.pengingat.nyala[j] === true && J(SS_ATUR_BAWAAN.pengingat.ke[j]) === '["Owner"]'; }), J(PG.map(function (p) { return p.id; })));
ok('2: saklar pengingat laci mati (Atur pengingat) = tidak aktif', (function () { aturDengan([{ id: 'pengingat', nyala: { laci: false } }]); var X = ssPengingat(KINI, { peringatan: SP }).aktif; aturDengan([]); return !X.some(function (p) { return p.jenis === 'laci'; }) && X.some(function (p) { return p.jenis === 'jelaskan'; }); })());
var LD = lhDasbor(KINI); var DH = dbHariIni(KINI);
ok('2: Dasbor › Hari ini = lhDasbor apa adanya (malam terakhir 1 Des +50 rb, alarm, 1 belum dijelaskan, 7 titik)', DH.laci && DH.laci.terakhir.tanggal === '2026-12-01' && DH.laci.terakhir.selisih === 50000 && DH.laci.alarm.nyala && DH.laci.belumJelas === 1 && DH.laci.tren.length === 7 && J(DH.laci) === J(LD), J(DH.laci));

// ==================== 3 · A82 ALASAN BEBAS · CATATAN TABLET · CARI BESOK ====================
var PJ = lhPerluJelas(KINI);
ok('3: "Belum ketemu — cari besok" (30 Nov) = perlu dijelaskan; "Belum tahu — dicari besok" yang SUDAH dijelaskan (26 Nov) = tidak', PJ.length === 1 && PJ[0].tanggal === '2026-11-30' && !lhMalam(KINI).find(function (m) { return m.tanggal === '2026-11-26'; }).perluJelas, J(PJ));
ok('3: alasan bawaan lama "Belum tahu — dicari besok" tanpa penjelasan ikut ditagih', (function () { pasok('tutupHari', GK.tutupHari.map(function (d) { if (d.tanggal !== '2026-11-26') return d; var x = JSON.parse(J(d)); delete x.penjelasan; return x; }));
  var X = lhPerluJelas(KINI).map(function (m) { return m.tanggal; }); pasok('tutupHari', JSON.parse(J(GK.tutupHari))); return J(X) === J(['2026-11-26', '2026-11-30']); })());
ok('3: pengingat jelaskan jatuh besoknya (1 Des) & tetap aktif sampai dijelaskan', spJ('jelaskan').length === 1 && spJ('jelaskan')[0].id === 'jelaskan|2026-11-30' && spJ('jelaskan')[0].jatuh === '2026-12-01', J(spJ('jelaskan')));
ok('3: penjelasan terlalu pendek / malam tak ada ditolak', !!susunJelaskanLaci('2026-11-30', 'ok', W).tolak && !!susunJelaskanLaci('2026-11-01', 'sebabnya ketemu', W).tolak);
var rj = susunJelaskanLaci('2026-11-30', 'uang kembalian salah hitung, sudah dikembalikan', W); var dj = rj.dokumen && rj.dokumen[0].data; var lama = GK.tutupHari.find(function (d) { return d.tanggal === '2026-11-30'; });
ok('3: penjelasan = dokumen tutupHari malam itu APA ADANYA + penjelasan { teks, tanggal, jam } (tanpa riwayat baru)', rj.dokumen[0].koleksi === 'tutupHari' && dj.penjelasan.teks === 'uang kembalian salah hitung, sudah dikembalikan' && dj.penjelasan.tanggal === iso
  && Object.keys(lama).every(function (k) { return J(lama[k]) === J(dj[k]); }) && Object.keys(dj).length === Object.keys(lama).length + 1, J(dj));
pasok('tutupHari', GK.tutupHari.map(function (d) { return d.tanggal === '2026-11-30' ? dj : d; }));
ok('3: sesudah dijelaskan — tidak ditagih lagi', lhPerluJelas(KINI).length === 0 && !lhSumberPengingat(KINI).some(function (x) { return x.jenis === 'jelaskan'; }));
pasok('tutupHari', JSON.parse(J(GK.tutupHari)));
// catatan tablet
var draf = { lembar: { 100000: 9 }, receh: '', timbang: {}, amankan: '', catatan: '  bensin 20 rb   belum dicatat ' };
var k1 = hlSusunKirim(draf, akB, W); var dk = k1.dokumen && k1.dokumen[0].data;
ok('3: tablet — catatan bebas ikut hitungan (dirapikan), bentuk tetap lolos rules v16 (hitungLaciSah) & penjaga perangkat', dk && dk.catatan === 'bensin 20 rb belum dicatat' && hitungLaciSah(dk, 'uid-ben') && !periksaKiriman(akB, [{ koleksi: 'persetujuan', data: Object.assign({}, dk, { olehUid: 'uid-ben' }), ada: false, lama: null }], [], HK).tolak, J(k1));
ok('3: tablet — tanpa catatan = kolomnya tidak ada; > 160 huruf ditolak; hitung buta tetap (tanpa seharusnya / selisih)', !('catatan' in hlSusunKirim(Object.assign({}, draf, { catatan: '' }), akB, W).dokumen[0].data) && !!hlSusunKirim(Object.assign({}, draf, { catatan: new Array(170).join('y') }), akB, W).tolak
  && !('seharusnya' in dk) && !('selisih' in dk));
pasok('persetujuan', [Object.assign({}, dk, { id: 'hlx' })]);
var hb = hlBaris(Object.assign({}, dk, { id: 'hlx' })); var tp = hlTerapkan('hlx', {});
ok('3: owner melihat catatannya (hlBaris) & "Pakai hitungan ini" membawanya ke lembar', hb.catatan === 'bensin 20 rb belum dicatat' && tp.patch && tp.patch.hitungCatatan === 'bensin 20 rb belum dicatat' && J(hlLepas({}).hitungCatatan) === 'null', J([hb.catatan, tp]));
var Dt = Object.assign({}, DRAF0, tp.patch, { alasan: 'uang dipakai beli bensin, belum dicatat' });
var st1 = susunTutup(Dt, W, false); var tH = st1.dokumen ? st1.dokumen.find(function (x) { return x.koleksi === 'tutupHari'; }).data : null;
ok('3: tutup hari — alasan BEBAS tertulis apa adanya & catatan tablet sampai di malam itu (dariTablet.catatan)', tH && tH.alasanSelisih === 'uang dipakai beli bensin, belum dicatat' && tH.selisih === -150000 && tH.dariTablet.catatan === 'bensin 20 rb belum dicatat', J(st1.tolak || tH));
pasok('tutupHari', JSON.parse(J(GK.tutupHari)).concat([tH]));
ok('3: catatan tablet terbaca kartu Selisih laci (lhBaca.catatanTablet) & alasan bebas = alasan', (function () { var m = lhMalam(KINI)[0]; return m.tanggal === iso && m.catatanTablet === 'bensin 20 rb belum dicatat' && m.alasan === 'uang dipakai beli bensin, belum dicatat' && m.penghitung === 'UJI B' && !m.perluJelas; })());
var st2 = susunTutup(Object.assign({}, DRAF0, { lembar: { 100000: 9 }, status: { laci: 'beres' }, alasan: LH_CARI }), W, true); var tH2 = st2.dokumen ? st2.dokumen.find(function (x) { return x.koleksi === 'tutupHari'; }).data : null;
pasok('tutupHari', JSON.parse(J(GK.tutupHari)).concat([tH2]));
ok('3: tutup hari dengan "Belum ketemu — cari besok" = ditagih mulai besok', tH2 && tH2.alasanSelisih === LH_CARI && lhPerluJelas(KINI).some(function (m) { return m.tanggal === iso; }) && lhSumberPengingat(KINI).some(function (x) { return x.id === 'jelaskan|' + iso && x.jatuh === '2026-12-03'; }), J(st2.tolak || tH2));
pasok('tutupHari', JSON.parse(J(GK.tutupHari))); pasok('persetujuan', []);

// ==================== 4 · B116 HALAMAN TUGAS STAF ====================
ok('4: mendarat di halaman tugas = Penjaga laci & karyawan saja (bukan owner / kasir@ / belum aktif)', tsMendarat(akB) && tsMendarat(akK) && !tsMendarat(akO) && !tsMendarat({ jenis: 'kasir' }) && !tsMendarat(null) && !tsMendarat({ jenis: 'menunggu', peran: 'ben' }));
var kunciD = (semuaBon(KINI).find(function (b) { return b.nama === D_; }) || {}).kunci;
pasok('tagihPelanggan', [{ id: 't1', kunci: kunciD, nama: D_, tanggal: '2026-11-28', jam: '10:00', janji: '2026-12-01', sisa: 650000 }]);
pasok('ambilBarang', [{ id: 'ab1', tanggal: '2026-12-01', jam: '10:00', jenis: 'titip', trxId: 'T9', namaPelanggan: 'Pelanggan Titip', isi: [{ idBaris: 'b1', nama: 'Angsa 50 kg', satuan: 'karung', jumlah: 1 }] }]);
var TK = tsTugas(KINI, akK), TB = tsTugas(KINI, akB); var tk = function (T, id) { return T.daftar.find(function (x) { return x.id === id; }); };
ok('4: enam bagian, urut: rutin · wadah · pesanan & antar · janji bayar · karcis · titipan; tidak ada yang galat', J(TK.daftar.map(function (x) { return x.id; })) === J(['rutin', 'wadah', 'antar', 'janji', 'karcis', 'titip']) && !TK.daftar.some(function (x) { return x.galat; }), J(TK.daftar.filter(function (x) { return x.galat; })));
ok('4: pesanan dikirim hari ini dihitung (yang 9 Des tidak)', tk(TK, 'antar').n === 1 && /Warung Contoh hari ini/.test(tk(TK, 'antar').ket) && tk(TK, 'antar').awas, J(tk(TK, 'antar')));
ok('4: janji bayar lewat (1 Des) — nama & sisa bon, SAMA untuk karyawan & Penjaga laci (keputusan owner)', tk(TK, 'janji').n === 1 && /Pelanggan Contoh D/.test(tk(TK, 'janji').ket) && tk(TK, 'janji').awas && J(tk(TK, 'janji')) === J(tk(TB, 'janji')), J(tk(TK, 'janji')));
ok('4: karcis darurat belum dirinci = karcis-logika apa adanya', tk(TK, 'karcis').n === daftarKarcis(KINI).nKarcis && tk(TK, 'karcis').n === 1);
ok('4: titipan belum diambil = ambil-logika apa adanya', tk(TK, 'titip').n === abDaftar().length && tk(TK, 'titip').n === 1);
ok('4: rutin = rnHari akun itu (karyawan: butir "semua" yang belum)', tk(TK, 'rutin').n === rnHari(KINI, akK).baris.filter(function (b) { return b.keadaan === 'belum' || b.keadaan === 'lewat'; }).length && tk(TB, 'rutin').n >= tk(TK, 'rutin').n);
ok('4: tujuan tiap baris = layar yang boleh dibuka staf (jual · pelanggan · stok · menu)', TK.daftar.every(function (x) { return x.tujuan && ['jual', 'pelanggan', 'stok', 'menu'].indexOf(x.tujuan.ke) >= 0 && (x.tujuan.ke === 'menu' || bolehLayar(akK, x.tujuan.ke)); }));
ok('4: kalimat = jumlah tugas terbuka', TK.n === TK.terbuka.reduce(function (a, x) { return a + x.n; }, 0) && /tugas di/.test(TK.kalimat));
var PK = pendengarPeran(akK), PB = pendengarPeran(akB); var dokP = function (P) { return (P.find(function (x) { return x.nama === 'aturanToko'; }) || {}).dok || []; }; var kol = function (P) { return P.map(function (x) { return x.nama; }); };
ok('4: v25 — karyawan & Penjaga laci mendengar rutinCek + aturanToko/rutin; sumber halaman tugas lain sudah di daftar baca staf', [PK, PB].every(function (P) { return kol(P).indexOf('rutinCek') >= 0 && dokP(P).indexOf('rutin') >= 0
    && ['wadahLiteran', 'pesanan', 'suratJalan', 'piutangMutasi', 'tagihPelanggan', 'penjualan', 'ambilBarang'].every(function (n) { return kol(P).indexOf(n) >= 0; }); }) && dokP(PK).indexOf('kepatuhan') < 0, J([kol(PK), dokP(PK)]));
ok('4: v25 — BUAT_STAF rutinCek = ben & karyawan (= rules stafCekRutin)', J(BUAT_STAF.rutinCek) === '["ben","karyawan"]');

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
})();
"""

RUSAK = [
    ('karyawan melihat butir penjaga', RN, "export const rnTerlihat = (b, peran) => peran === 'owner' || b.untuk === 'semua' || (peran === 'penjaga' && b.untuk === 'penjaga');", "export const rnTerlihat = (b, peran) => true;"),
    ('mingguan memakai tanggal, bukan Senin', RN, "export function rnPeriode(ulang, iso) { return ulang === 'harian' ? iso : ulang === 'mingguan' ? rnSenin(iso) : iso.slice(0, 7); }", "export function rnPeriode(ulang, iso) { return ulang === 'harian' ? iso : ulang === 'mingguan' ? iso : iso.slice(0, 7); }"),
    ('centang kedua menimpa yang pertama', RN, "if (!p[d.periode]) p[d.periode] =", "p[d.periode] ="),
    ('putaran lama ikut ditagih', RN, "jatuh < iso && jatuh >= RN_MULAI ? 'lewat'", "jatuh < iso ? 'lewat'"),
    ('Penjaga laci tidak boleh mencentang butir penjaga', RN, "(peran === 'penjaga' ? b.untuk !== 'owner' : b.untuk === 'semua')", "(peran === 'penjaga' ? b.untuk === 'semua' : b.untuk === 'semua')"),
    ('butir otomatis bisa dicentang tangan', RN, "  if (b.otomatis) return { tolak: b.nama + ' tercatat sendiri dari ' + b.sumber + ' — kerjakan di sana' };\n", ""),
    ('hitungan yang ditolak owner tetap dianggap sudah', RN, "(m.status || 'menunggu') !== 'ditolak'", "true"),
    ('cek gudang minggu lalu dianggap minggu ini', RN, "const sudah = !!G.terakhir && G.terakhir >= periode;", "const sudah = !!G.terakhir;"),
    ('akhir bulan salah', RN, "return h >= 1 && h <= 28 ? key + '-' + String(h).padStart(2, '0') : akhir;", "return h >= 1 && h <= 28 ? key + '-' + String(h).padStart(2, '0') : key + '-30';"),
    ('atur menerima hari minggu 9', RN, "if (ulang === 'mingguan' && !(Number.isInteger(h) && h >= 1 && h <= 7))", "if (ulang === 'mingguan' && false)"),
    ('batal centang oleh staf', RN, "  if (rnPeran(akun) !== 'owner') return { tolak: 'Membatalkan centang hanya owner' };\n", ""),
    ('Dasbor rutin menghitung otomatis sebagai terlewat', RN, "b.nyala && b.ulang === 'harian' && !b.otomatis && !(C[b.id] || {})[kemarin]", "b.nyala && b.ulang === 'harian' && !(C[b.id] || {})[kemarin]"),
    ('beruntun tidak berhenti di malam pas', LH, "let beruntun = 0; for (const m of M) { if (!m.lewat) break; beruntun++; }", "let beruntun = 0; for (const m of M) { if (m.lewat) beruntun++; }"),
    ('dimaafkan dihitung berselisih', LH, "const lewat = selisih !== null && Math.abs(selisih) > A.maaf;", "const lewat = selisih !== null && selisih !== 0;"),
    ('malam basi ikut alarm', LH, "filter((m) => lhHariKe(iso) - lhHariKe(m.tanggal) <= LH_UMUR_HARI)", "filter((m) => true)"),
    ('saklar alarm diabaikan', LH, "const nyala = A.nyala && (kenaBeruntun || kenaDalam);", "const nyala = kenaBeruntun || kenaDalam;"),
    ('batas maaf bawaan, bukan angka owner', LH, "Math.round(Number(T.maafSelisih)) : LH_BAWAAN.maafSelisih", "LH_BAWAAN.maafSelisih : LH_BAWAAN.maafSelisih"),
    ('sudah dijelaskan tetap ditagih', LH, "penjelasan: P ? { teks: lhTeks(P.teks), tanggal: String(P.tanggal || ''), jam: String(P.jam || '') } : null, perluJelas: cari && !P,", "penjelasan: P ? { teks: lhTeks(P.teks), tanggal: String(P.tanggal || ''), jam: String(P.jam || '') } : null, perluJelas: cari,"),
    ('alasan bawaan lama tidak ditagih', LH, " || alasan === LH_CARI_LAMA);", ");"),
    ('penjelasan menimpa dokumen tutup', LH, "const data = Object.assign({}, d, { penjelasan:", "const data = Object.assign({ id: d.id, tanggal: d.tanggal }, { penjelasan:"),
    ('pengingat jelaskan jatuh hari itu juga', LH, "jatuh: lhTambah(m.tanggal, 1),", "jatuh: m.tanggal,"),
    ('jendela lebih kecil dari M diterima', LH, "const D = baca('alarmDalam', 1, J.n, 'Malam berselisih dari ' + J.n + ' malam'); if (D.tolak) return D;", "const D = baca('alarmDalam', 1, 30, 'x'); if (D.tolak) return D;"),
    ('catatan tablet tidak dikirim', HL, "  if (catatan) data.catatan = catatan;\n", ""),
    ('catatan tablet tidak sampai ke lembar owner', HL, "hitungCatatan: b.catatan || null },", "hitungCatatan: null },"),
    ('catatan tablet tidak tersimpan di malam itu', TD, "  if (H.tablet && D.hitungCatatan) dokTutup.dariTablet.catatan = String(D.hitungCatatan).slice(0, 160);\n", ""),
    ('janji bayar hanya yang lewat', TS, "(b.status === 'janjiLewat' || (b.status === 'menunggu' && b.tagih.janji <= iso))", "(b.status === 'janjiLewat' && false)"),
    ('pesanan minggu depan ikut diantar', TS, "poHariKe(o.tanggalKirim) - hP <= 1", "true"),
    ('owner ikut mendarat', TS, "export const tsMendarat = (akun) => !!akun && akun.jenis === 'aktif' && (akun.peran === 'ben' || akun.peran === 'karyawan');", "export const tsMendarat = (akun) => !!akun;"),
    ('karyawan tidak mendengar rutinCek', AK, "  BACA_RUTIN.forEach((n) => out.push({ nama: n }));   // v25: rutinCek (ben & karyawan)\n", ""),
    ('karyawan tidak mendengar aturanToko/rutin', AK, ".concat(DOK_STAF_RUTIN[n] || []) }));", " }));"),
    ('penjaga kiriman rutinCek hilang', AK, "      if (x.koleksi === 'rutinCek' && !cekRutinSah(d)) return { tolak: 'Bentuk centang rutin tidak sah — buka lagi daftarnya' };\n", ""),
    ('periode minggu bentuk lain diterima', AK, "/^\\d{4}-\\d{2}(-\\d{2})?$/.test(d.periode)", "/^[0-9W-]{4,10}$/.test(d.periode)"),
    ('pengingat laci tidak diterima sistem-logika', SS, "if (p && SS_JENIS_LACI.indexOf(p.jenis) >= 0 && /", "if (p && false && /"),
    ('Dasbor kartu Hari ini tanpa selisih laci', DL, "    laci: dbCoba(() => lhDasbor(kini)),\n", ""),
]

STATIS = [
    ('rules v25: aturanToko/rutin terbaca staf + fungsi stafCekRutin + blok rutinCek', 'rules', ["'bukuPegangan', 'rutin'] && staf(['ben', 'karyawan']))", 'function stafCekRutin(peranBoleh, id)', "match /rutinCek/{id} {", "allow create: if owner() || stafCekRutin(['ben', 'karyawan'], id);", "d.periode.matches('[0-9]{4}-[0-9]{2}(-[0-9]{2})?')"]),
    ('koleksi rutinCek didengar (kelas tetap)', 'koleksi', ["{ nama: 'rutinCek',            urut: 'id',    cache: 'rutinCek', kelas: 'tetap' }"]),
    ('modul baru di-modulepreload', 'index', ['<link rel="modulepreload" href="js/layar/laci-logika.js">', '<link rel="modulepreload" href="js/layar/rutin-logika.js">', '<link rel="modulepreload" href="js/layar/tugas-staf-logika.js">', '<link rel="modulepreload" href="js/layar/rutin-panel.js">']),
    ('bundel jsc memuat laci & rutin otomatis', 'bundel', ["LH_MODUL = 'baru/js/layar/laci-logika.js'", "RN_MODUL = 'baru/js/layar/rutin-logika.js'"]),
    ('app.js: staf mendarat di halaman tugas (sekali per orang per hari) + lonceng & Pengingat selisih laci owner saja', 'app', ['if (tadi && tsMendarat(akun))', "pindah('menu'); layar.gambar(); return;", "LC_JENIS.push('laci', 'jelaskan');",
        'return pwSumberPengingat(sekarangCadangan || new Date()).concat(sumberLaci());', 'function sumberLaci()']),
    ('Menu: kartu Tugas hari ini PALING ATAS akun staf (di bawah kartu serah terima laci yang hanya tampil saat wajib, owner 28 Nov 2026) + kartu Rutin + Menu › Toko ini › Rutin (owner)', 'menu', ["data-k=\"staf\" style=\"display: flex; flex-direction: column; gap: 10px;\">\n      ${kartuSerahLaci(s, { wajib: opsi.serahLaci ? opsi.serahLaci.baca() : null, kini: kini() })}\n      ${kartuTugasStaf(s, { akun: akunM, kini: kini() })}", "${kartuRutin(s, { akun: akunM, kini: kini() })}",
        "s.sistem === 'rutin' ? gambarRutinOwner(", "aksiPanelRutin({ set, st, tulis, waktu, kini, akun: opsi.akun, pergi })", "rutin: [['hari', 'Hari ini'], ['riwayat', 'Siapa mencentang'], ['atur', 'Atur daftar']]", "rutin: 'Rutin' };", "'rnAtur', 'rnCatat',"]),
    ('Menu › Toko ini: baris Rutin', 'mlog', ["baris('rutin', 'centang', 'Rutin',"]),
    ('panel: tombol MULAI JUALAN ke Jual + centang + atur', 'panel', ['data-aksi="stafKe" data-t="jual"', 'rnCentang: ({ id }) => centang(id)', 'rnAturSimpan: async () =>', 'tsKe: ({ id }) =>']),
    ('Uang › Tutup hari: alasan bebas, cari besok, kartu Selisih laci di semua tata letak, setelan alarm', 'uang', ["${H.perluAlasan ? alasanBebas(d, H) : ''}", 'data-ketik="tdAlasanKetik"', 'function kartuSelisih(s)', '${riwayat}${selisihK}', '${aturAlarm(s.aturT)}',
        'lhJelasSimpan: async () =>', 'const r2 = LH.susunAturLaci(', "'aturT', 'lhJelas', 'langkahB',", 'Catatan ${b.dari}: <b>${b.catatan}</b>']),
    ('Dasbor: baris selisih laci (Hari ini) & rutin (Mutu usaha)', 'dasbor', ['+ barisLaci(H.laci)', 'function barisLaci(L)', "baris('rutin', 'Rutin hari ini',"]),
    ('tablet: isian catatan untuk owner', 'hlp', ['data-ketik="hlCatatan"', 'hlCatatan: (v) => ubah({ catatan: String(v).slice(0, HL.HL_BATAS.catatan) })']),
    ('CSS: gerak baris tugas/rutin, batang selisih, titik Dasbor + reduced-motion', 'css_menu', ['.layar-menu .ts-baris', '@keyframes rn-pop', 'prefers-reduced-motion']),
    ('CSS uang: batang selisih laci', 'css_uang', ['.layar-uang .lh-b.kurang', '@keyframes lh-tumbuh']),
    ('CSS Dasbor: titik selisih laci', 'css_ring', ['.layar-ringkasan .db-laci-titik', '@keyframes db-laci-muncul']),
    ('peta_akses: jalur tulis rutinCek terdaftar', 'peta', ['rutinCek']),
    ('pages.yml menjalankan uji ini + kontrol', 'pages', ['python3 alat-uji/uji_rutin_staf.py && python3 alat-uji/uji_rutin_staf.py --kontrol']),
    ('BACA-DULU bagian Paket P6', 'baca', ['Paket P6', 'uji_rutin_staf', 'rules v25']),
]
RUSAK_STATIS = [
    ('staf tidak mendarat di tugas', 'app', 'if (tadi && tsMendarat(akun))', 'if (false && tsMendarat(akun))'),
    ('lonceng tanpa selisih laci', 'app', "LC_JENIS.push('laci', 'jelaskan');", ''),
    ('kartu tugas tidak di atas', 'menu', "kini: kini() })}\n      ${kartuTugasStaf(s, { akun: akunM, kini: kini() })}", "kini: kini() })}\n"),
    ('isian rutin tidak dijaga ganti orang', 'menu', "'rnAtur', 'rnCatat',", ''),
    ('kartu Selisih laci hilang dari satu tata letak', 'uang', '${riwayat}${selisihK}', '${riwayat}'),
    ('alasan bebas hilang', 'uang', "${H.perluAlasan ? alasanBebas(d, H) : ''}", ''),
    ('Dasbor tanpa baris laci', 'dasbor', '+ barisLaci(H.laci)', ''),
    ('rules tanpa blok rutinCek', 'rules', "match /rutinCek/{id} {", "match /rutinCekX/{id} {"),
    ('modul tidak dimuat awal', 'index', '<link rel="modulepreload" href="js/layar/rutin-logika.js">', ''),
    ('komentar // menelan kode', 'lh', "export const LH_TREN = 30;", "// tren\nexport const LH_TREN = 30; // malam; const x = 1;"),
    ('modul logika menyentuh DOM', 'rn', "export const RN_ID = 'rutin';", "export const RN_ID = 'rutin'; document.title = 'x';"),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_rutin_staf.py && python3 alat-uji/uji_rutin_staf.py --kontrol', 'true'),
]

ASAP = r"""
(function () {
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
['rutinCek', 'kepatuhanCek', 'cekGudang', 'ambilBarang', 'suratJalan'].forEach(function (n) { if (!Array.isArray(CAD[n])) pasok(n, []); });
var kini = new Date(Date.now()); var iso = hariIniIso(kini); var out = { akhir: iso, galat: [] };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + e); return null; } };
var akK = keadaanAkun('kry@contoh.com', 'uid-kry', { uid: 'uid-kry', nama: 'K', peran: 'karyawan', aktif: true }); var akB = keadaanAkun('ben@contoh.com', 'uid-ben', { uid: 'uid-ben', nama: 'B', peran: 'ben', aktif: true });
var A = lhAtur(); var M = aman('malam', function () { return lhMalam(kini); });
out.malam = M ? M.length : null; out.samaBacaTutup = M ? ambilTutupHari().every(function (d) { var a = lhBaca(d, A).selisih; var b = bacaTutup(d).selisih; return (a === null && (b === null || b === undefined)) || a === b; }) : false;
var L = aman('alarm', function () { return lhAlarm(kini); }); out.alarm = L ? { nyala: L.nyala, beruntun: L.beruntun, dalam: L.dalam, jendela: L.jendela, umurTerakhir: L.terakhir ? L.terakhir.tanggal : null } : null;
var T = aman('tren', function () { return lhTren(kini, 30); }); out.tren = T ? { n: T.n, lewat: T.nLewat, pas: T.nPas, dimaafkan: T.nDimaafkan, tanpa: T.nTanpa } : null;
out.perluJelas = aman('jelas', function () { return lhPerluJelas(kini).length; }); out.perOrang = aman('orang', function () { return lhPerOrang(kini, 30).map(function (x) { return [x.n, x.nLewat]; }); });
var RO = aman('rutin owner', function () { return rnHari(kini, { jenis: 'owner' }); }); var RK = aman('rutin karyawan', function () { return rnHari(kini, akK); });
out.rutin = RO && RK ? { owner: [RO.n, RO.nSudah], karyawan: [RK.n, RK.nSudah], otomatisGalat: RO.baris.filter(function (b) { return /tidak dikenal/.test(b.teks); }).length } : null;
var TK = aman('tugas', function () { return tsTugas(kini, akK); }); out.tugas = TK ? TK.daftar.map(function (x) { return x.id + ':' + x.n; }) : null; out.tugasGalat = TK ? TK.daftar.filter(function (x) { return x.galat; }).map(function (x) { return x.id + ': ' + x.ket; }) : 'gagal';
var TB = aman('tugas ben', function () { return tsTugas(kini, akB); }); out.tugasBenGalat = TB ? TB.daftar.filter(function (x) { return x.galat; }).length : 'gagal';
var DH = aman('dasbor', function () { return dbHariIni(kini); }); out.dasborLaci = DH ? !!(DH.laci && !DH.laci.galat) : false;
var DM = aman('mutu', function () { return dbMutu(kini); }); out.dasborRutin = DM ? !!(DM.rutin && !DM.rutin.galat) : false;
var SP = aman('pengingat', function () { return lhSumberPengingat(kini); }); out.pengingat = SP ? SP.map(function (x) { return x.jenis; }) : null;
print(JSON.stringify(out));
})();
"""


def bundel_js(teks):   # pola uji_gudang_label_patuh (satu lingkup + nama susunBon pemasok)
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    js = uji_gudang_label_patuh.uji_kunci_periode.satu_lingkup(js)
    B = uji_gudang_label_patuh.BON_PEMASOK_LAMA
    if js.count(B) == 1: js = js.replace(B, B.replace('susunBon(', 'bpSusunBon('))
    return js


MALAM_INI = {'id': '2026-12-02', 'tanggal': '2026-12-02', 'jam': '21:00', 'selisihLaci': 0, 'selisih': 0, 'alasanSelisih': '', 'sistemBaru': True, 'oleh': 'Owner'}
DRAF0 = {'lembar': {}, 'receh': 0, 'alasan': '', 'rekPilih': '', 'rekNyata': '', 'sisih': None, 'timbang': {}, 'status': {}}


def jalan(teks):
    jam = "var __KINI = new Date('2026-12-02T14:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    r, out = uji_dasbor_sensus.jsc(jam + bundel_js(teks) + '\nvar KOTAK0 = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar GK = ' + json.dumps(KOTAK) + ';\nvar ATUR = ' + json.dumps(ATUR)
                                   + ';\nvar MALAM_INI = ' + json.dumps(MALAM_INI) + ';\nvar DRAF0 = ' + json.dumps(DRAF0) + ';\n' + SKENARIO)
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], list(h['gagal'])


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    # modul logika tanpa DOM; laci & tugas staf BACA SAJA kecuali penyusun yang tercatat
    if src['uang'].count('${riwayat}${selisihK}') != 5: g.append('uang.js: kartu Selisih laci tidak ada di kelima tata letak Tutup hari (%d×)' % src['uang'].count('${riwayat}${selisihK}'))
    for k in ('lh', 'rn', 'ts'):
        if 'document.' in src[k] or 'tulisDokumen' in src[k] or 'window.' in src[k]: g.append(k + ': modul logika menyentuh DOM / menulis langsung')
    if 'koleksi:' in src['ts'] or 'dokumen:' in src['ts']: g.append('tugas-staf-logika menyusun dokumen (halaman tugas = baca saja)')
    for k in ('lh', 'rn'):
        pintu = re.findall(r'export function (\w+)\([^)]*\) \{[^\n]*\n(?:(?!export function).)*?(?:dokumen: \[|hapus: \[)', src[k], re.S)
        boleh = {'lh': {'susunJelaskanLaci', 'susunAturLaci'}, 'rn': {'susunCentangRutin', 'susunBatalRutin', 'susunAturRutin'}}[k]
        if set(pintu) - boleh: g.append(k + ': pintu tulis di luar yang tercatat: ' + ', '.join(sorted(set(pintu) - boleh)))
    if "from './sistem-logika.js'" in src['lh'] or "from './sistem-logika.js'" in src['rn']: g.append('laci / rutin mengimpor sistem-logika (pola lokal.peringatan: tanpa impor balik)')
    for k in ('lh', 'rn', 'ts', 'panel', 'menu', 'uang', 'dasbor', 'hl', 'hlp', 'td', 'ss', 'dl', 'app'):
        for n, baris in enumerate(src[k].split('\n')):
            ekor = uji_sisa_sensus.komentar_ekor(baris)
            if ekor and re.search(r"\b[a-zA-Z]\w*: (opsi\.|\(|async |\[|\{|'|`)|;\s*(const|let|return|if|export)\b|\)\s*=>", ekor): g.append(k + ':' + str(n + 1) + ': komentar // menelan kode → ' + ekor.strip()[:90])
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
        print('KONTROL: %d kerusakan' % (len(RUSAK) + len(RUSAK_STATIS)))
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
            beres = (not h['galat'] and h['samaBacaTutup'] and h['alarm'] is not None and h['tren'] is not None and h['rutin'] is not None and not h['rutin']['otomatisGalat']
                     and not h['tugasGalat'] and h['tugasBenGalat'] == 0 and h['dasborLaci'] and h['dasborRutin'])
            # angka RUPIAH toko TIDAK dicetak (repo publik) — hanya keadaan & jumlah malam / butir / tugas
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: selisih tidak sama dengan bacaTutup / rutin, tugas, Dasbor galat')
    sys.exit(1 if g or gs else 0)
