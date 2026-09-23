#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_pajak_baru.py — putaran 24: MODUL PAJAK sistem baru (pajak-logika + sambungannya ke DK3 laporan-logika) di jsc.
KOTAK PASIR (ANGKA & NAMA CONTOH, bukan angka toko), jam dikunci 19 Sep 2026 10:00 WIB. Sistem "mulai mencatat" 10 Mar 2026.
Yang dijaga: omzet sistem = mesin laba (satu sumber); batas bebas hanya mengurangi bagian di bawahnya (bulan yang melewati batas → kelebihannya saja);
omzet ketikan tidak terhitung dua kali; kosong ≠ nol; setoran memotret angka & perubahan sesudahnya DISEBUT; penulis aturanToko/rekapOmzet tidak menghapus profil;
DK3 dan layar Pajak memberi perkiraan yang SAMA; tidak ada NIK/NPWP/rekening di teks bebas. Semua angka = perkiraan, bukan nasihat pajak.

    python3 alat-uji/uji_pajak_baru.py            → N lulus · 0 gagal (+ uji asap cadangan toko lokal bila ada)
    python3 alat-uji/uji_pajak_baru.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_laporan_baru  # noqa: E402  (MODUL yang sama: pajak-logika + laporan-logika & kawan-kawannya)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_laporan_baru.MODUL
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(id, tgl, harga, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': '10:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 50, 'beratKarungAcuan': 50, 'jumlahKarung': 1, 'hargaTotal': harga, 'hppTotalSaatJual': round(harga * 0.95), 'trxId': 't-' + id}
    d.update(k); return d


# ANGKA CONTOH (juta rupiah): Mar 120 (mulai 10 Mar) · Apr 100 · Mei 100 · Jun 80 · Jul 60 · Agu 70 · Sep 40 (berjalan) = 570 di sistem.
KOTAK = {
  'penjualan': [jual('m1', '2026-03-10', 70000000), jual('m2', '2026-03-25', 50000000), jual('a1', '2026-04-12', 100000000), jual('e1', '2026-05-08', 100000000), jual('n1', '2026-06-10', 80000000),
                jual('l1', '2026-07-10', 60000000), jual('g1', '2026-08-10', 50000000), jual('g2', '2026-08-25', 20000000), jual('s1', '2026-09-05', 25000000), jual('s2', '2026-09-18', 15000000),
                jual('x1', '2026-09-18', 9000000) | {'dibatalkan': True}],
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-03-10', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'merkList': [{'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'totalKg': 50000, 'hargaPerKg': 12000, 'subtotalHarga': 600000000}]}],
  'aturanToko': [], 'pajakOmzetLuar': [], 'pajakSetoran': [], 'dokumenCetak': [], 'retur': [], 'pengeluaranHarian': [], 'biayaBulanan': [], 'tutupHari': [], 'pengaturan': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var KINI = new Date(Date.now()); var n = 9000; var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: function () { n += 1; return n; } };
function tulis(r) { if (r.tolak) throw new Error('DITOLAK: ' + r.tolak); if (r.dokumen && r.dokumen.length) terapkanKeCache(r.dokumen); (r.hapus || []).forEach(function (h) { pasok(h.koleksi, cacheMentah(h.koleksi).filter(function (d) { return String(d.id) !== String(h.id); })); }); return r; }
var bln = function (T, k) { return T.daftar.find(function (b) { return b.key === k; }); };
var JT = 1000000;

// ---- 1 · bawaan: belum diatur, anggapan orang pribadi
var T0 = pjTahun(2026, KINI);
ok('bawaan: jenis WP belum diketahui → hitungan dengan anggapan orang pribadi (kalimat terlihat); tarif belum diatur → PPh tidak dihitung, status "aturan belum diatur"; DK3 tanpa perkiraan',
  T0.anggapanOp && /anggapan orang pribadi/.test(PJ_ANGGAPAN_OP) && !T0.hitung && bln(T0, '2026-06').pph === null && bln(T0, '2026-06').status.kode === 'aturan' && rekapOmzet(KINI).perkiraanTahun === null && T0.daftar.length === 9, J(T0.daftar.map(function (b) { return b.status.kode; })));
ok('omzet sistem per bulan = mesin laba (satu sumber): Mar 120 jt (sejak 10 Mar, sebagian), Agu 70 jt, Sep 40 jt (nota batal tidak ikut); Jan–Feb tidak ada di sistem ("—")',
  bln(T0, '2026-03').sistem === 120 * JT && bln(T0, '2026-03').sebagian && bln(T0, '2026-08').sistem === 70 * JT && bln(T0, '2026-09').sistem === 40 * JT && bln(T0, '2026-01').sistem === null && pjOmzetSistem('2026-09').omzet === hitungLabaRentang(function (t) { return !!t && bulanDari(t) === '2026-09'; }).omzetPenuh);
ok('bulan kosong ≠ nol: Jan, Feb (sebelum sistem) & Mar (sistem mulai 10 Mar, tgl 1–9 belum diisi) = 3 bulan belum diisi → kumulatif berlabel KURANG dari sebenarnya',
  T0.kosong === 3 && !T0.lengkap && /3 bulan belum diisi, kumulatif KURANG dari sebenarnya/.test(T0.kumTeks) && !bln(T0, '2026-01').lengkap && !bln(T0, '2026-03').lengkap && bln(T0, '2026-04').lengkap, T0.kumTeks);

// ---- 2 · tombol aturan
var PA = tulis(susunPakaiAturan(W)); var P1 = pjProfil();
ok('tombol "Pakai aturan PP 55/2022 jo. PP 20/2026": tarif 5‰, batas bebas Rp500 juta, batas atas Rp4,8 miliar + catatan sumber bertanggal; tiap angka tetap bisa diubah',
  P1.tarifPerMil === 5 && P1.batasBebas === 500 * JT && P1.batasOmzet === 4800 * JT && /PP 20\/2026/.test(P1.sumberAturan.teks) && P1.sumberAturan.tanggal === '2026-09-19'
  && (function () { var r = susunProfilPajak({ batasBebas: '400.000.000' }, W); return r.dokumen[0].data.batasBebas === 400 * JT && r.dokumen[0].data.tarifPerMil === 5; })(), J(P1));
var T1 = pjTahun(2026, KINI);
ok('data belum lengkap: bulan sesudah bulan "—" berstatus "data belum lengkap" (PPh tampil sebagai paling sedikit), bukan nihil/terutang', bln(T1, '2026-04').status.kode === 'belumLengkap' && bln(T1, '2026-03').status.kode === 'belumLengkap', J(bln(T1, '2026-04').status));

// ---- 3 · omzet di luar sistem
ok('catatan lama di bulan yang punya penjualan (Apr) DITOLAK — tidak boleh terhitung dua kali; bulan pertama sistem (Mar, mulai 10 Mar) hanya dengan keterangan tanggal 1–9',
  /terhitung dua kali/.test(susunOmzetLuar({ bulan: '2026-04', sumber: 'catatanLama', jumlah: '10.000.000' }, W).tolak) && /HANYA untuk tanggal 1–9/.test(susunOmzetLuar({ bulan: '2026-03', sumber: 'catatanLama', jumlah: '30.000.000' }, W).tolak)
  && !!susunOmzetLuar({ bulan: '2026-03', sumber: 'catatanLama', jumlah: '30.000.000', keterangan: 'tanggal 1–9 Maret dari buku ayah' }, W).dokumen);
ok('isian kosong ditolak ("kosong artinya belum diisi, bukan nol"); nol boleh diketik; bulan depan ditolak; sumber tak dikenal ditolak',
  /bukan nol/.test(susunOmzetLuar({ bulan: '2026-01', sumber: 'catatanLama', jumlah: '' }, W).tolak) && susunOmzetLuar({ bulan: '2026-01', sumber: 'catatanLama', jumlah: '0' }, W).dokumen[0].data.jumlah === 0
  && !!susunOmzetLuar({ bulan: '2026-10', sumber: 'catatanLama', jumlah: '1' }, W).tolak && !!susunOmzetLuar({ bulan: '2026-01', sumber: 'lain', jumlah: '1' }, W).tolak);
(function () { var semula = cacheMentah('penjualan'); pasok('penjualan', semula.concat([{ id: 'z1', tanggal: '2026-03-01', jam: '09:00', caraBayar: 'Tunai', jenis: 'karung', hargaTotal: 1000 }]));
  ok('sistem mencatat sejak tanggal 1 → catatan lama bulan itu ditolak juga', /sejak tanggal 1/.test(susunOmzetLuar({ bulan: '2026-03', sumber: 'catatanLama', jumlah: '1', keterangan: 'x' }, W).tolak || '')); pasok('penjualan', semula); })();
tulis(susunOmzetLuar({ bulan: '2026-01', sumber: 'catatanLama', jumlah: '150.000.000', keterangan: 'buku ayah' }, W)); tulis(susunOmzetLuar({ bulan: '2026-02', sumber: 'catatanLama', jumlah: '150.000.000' }, W));
tulis(susunOmzetLuar({ bulan: '2026-03', sumber: 'catatanLama', jumlah: '30.000.000', keterangan: 'tanggal 1–9 Maret' }, W));
var T2 = pjTahun(2026, KINI);
ok('omzet luar ikut kumulatif: Jan 150 + Feb 150 + Mar (120 sistem + 30 catatan lama) = 450 jt; semua bulan lengkap', T2.lengkap && bln(T2, '2026-03').omzet === 150 * JT && bln(T2, '2026-03').kum === 450 * JT && bln(T2, '2026-09').kum === 900 * JT, J(T2.daftar.map(function (b) { return b.kum; })));

// ---- 4 · hitungan PPh
ok('di bawah batas bebas → nihil (Jan–Mar, kumulatif 450 jt ≤ 500 jt)', ['2026-01', '2026-02', '2026-03'].every(function (k) { return bln(T2, k).pph === 0 && bln(T2, k).status.kode === 'nihil'; }), J(bln(T2, '2026-03').status));
ok('batas terlewati DI TENGAH bulan (Apr: 450 → 550 jt) → hanya kelebihan 50 jt yang dikenai: PPh 250.000 (bukan 500.000)', bln(T2, '2026-04').kena === 50 * JT && bln(T2, '2026-04').pph === 250000, J(bln(T2, '2026-04')));
ok('bulan sesudahnya penuh: Mei 100 jt → 500.000; Jun 80 jt → 400.000; total tahun = (900 − 500) jt × 0,5 % = 2.000.000', bln(T2, '2026-05').pph === 500000 && bln(T2, '2026-06').pph === 400000 && T2.totalPph === 2000000, T2.totalPph);
tulis(susunOmzetLuar({ bulan: '2026-06', sumber: 'usahaLain', jumlah: '999', keterangan: 'jasa angkut' }, W));
ok('pembulatan ke BAWAH ke rupiah penuh [BELUM TERVERIFIKASI]: Jun 80.000.999 → 400.004 (bukan 400.005); usaha lain WP yang sama ikut PPh', pjTahun(2026, KINI).daftar[5].pph === 400004, pjTahun(2026, KINI).daftar[5].pph);
tulis(susunHapusOmzetLuar('2026-06|usahaLain', true));
tulis(susunOmzetLuar({ bulan: '2026-07', sumber: 'usahaPasangan', jumlah: '300.000.000', keterangan: 'toko pasangan, pisah harta' }, W)); var T3 = pjTahun(2026, KINI);
ok('usaha pasangan (pisah harta) TIDAK ikut PPh toko ini (batas bebas masing-masing, PMK 164/2023 Pasal 6 ayat 5) tapi IKUT ambang Rp4,8 miliar (PP 20/2026 Pasal 58)', T3.totalPph === 2000000 && T3.kum === 900 * JT && T3.kumGabung === 1200 * JT, J([T3.kum, T3.kumGabung]));
ok('hapus isian omzet luar butuh ketukan kedua; sesudahnya bulan itu kembali "belum diisi"', susunHapusOmzetLuar('2026-07|usahaPasangan').perluYakin === true && (function () { tulis(susunHapusOmzetLuar('2026-07|usahaPasangan', true)); return pjOmzetLuar('2026-07', 'usahaPasangan') === null; })());

// ---- 5 · status & tempo
var T4 = pjTahun(2026, KINI);
ok('lewat tempo: Apr–Agu terutang tanpa setoran, tanggal 15 bulan berikutnya terlewati (hari ini 19 Sep) → "lewat tempo"; Sep (berjalan) → "terutang (bulan berjalan)"',
  ['2026-04', '2026-05', '2026-06', '2026-07', '2026-08'].every(function (k) { return bln(T4, k).status.kode === 'lewatTempo'; }) && bln(T4, '2026-08').tempo === '2026-09-15' && bln(T4, '2026-09').status.kode === 'terutang' && /berjalan/.test(bln(T4, '2026-09').status.teks), J(T4.daftar.map(function (b) { return b.status.kode; })));

// ---- 6 · setoran
ok('setoran dicatat mundur (> 7 hari) wajib catatan; tanpa NTPN wajib catatan; NTPN format aneh = PERINGATAN saja (tetap tercatat)',
  /catatan wajib/.test(susunSetoran({ masaPajak: '2026-04', tanggalSetor: '2026-05-14', jumlah: '250.000', ntpn: 'AB12CD34EF56GH78' }, W, KINI).tolak) && /Tanpa NTPN/.test(susunSetoran({ masaPajak: '2026-08', tanggalSetor: '2026-09-18', jumlah: '350.000' }, W, KINI).tolak)
  && (function () { var r = susunSetoran({ masaPajak: '2026-08', tanggalSetor: '2026-09-18', jumlah: '350.000', ntpn: 'ABC' }, W, KINI); return !!r.dokumen && /16 karakter/.test(r.peringatan); })());
tulis(susunSetoran({ masaPajak: '2026-04', tanggalSetor: '2026-05-14', jumlah: '250.000', ntpn: 'ab12 cd34 ef56 gh78', catatan: 'dari bukti kertas pemilik lama' }, W, KINI));
tulis(susunSetoran({ masaPajak: '2026-05', tanggalSetor: '2026-09-17', jumlah: '400.000', ntpn: '1111222233334444' }, W, KINI));
tulis(susunSetoran({ masaPajak: '2026-06', tanggalSetor: '2026-09-17', jumlah: '450.000', ntpn: '5555666677778888' }, W, KINI));
var T5 = pjTahun(2026, KINI);
ok('setoran pas → "disetor · NTPN"; kurang → "kurang setor Rp100.000"; lebih → "lebih setor Rp50.000"; potret omzet & perkiraan saat setor tersimpan',
  bln(T5, '2026-04').status.kode === 'disetor' && /AB12CD34EF56GH78/.test(bln(T5, '2026-04').status.teks) && bln(T5, '2026-05').status.teks === 'kurang setor Rp100.000' && bln(T5, '2026-06').status.teks === 'lebih setor Rp50.000'
  && cacheMentah('pajakSetoran').find(function (s) { return s.masaPajak === '2026-05'; }).omzetSaatSetor === 100 * JT && cacheMentah('pajakSetoran').find(function (s) { return s.masaPajak === '2026-05'; }).pphPerkiraanSaatSetor === 500000, J([bln(T5, '2026-05').status, bln(T5, '2026-06').status]));
ok('setoran pada bulan yang BELUM final diterima (Agu 2026 belum tutup buku — beda dengan tanda lapor DK3)', !lpFinal('2026-08') && !!susunSetoran({ masaPajak: '2026-08', tanggalSetor: '2026-09-18', jumlah: '350.000', ntpn: '9999000011112222' }, W, KINI).dokumen);
pasok('penjualan', cacheMentah('penjualan').concat([{ id: 'e2', tanggal: '2026-05-20', jam: '11:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, hargaTotal: 2000000, hppTotalSaatJual: 1900000 }]));
var T6 = pjTahun(2026, KINI);
ok('omzet berubah SESUDAH disetor (nota Mei tambahan 2 jt) → status "angka berubah sejak disetor: omzet +Rp2.000.000 · perkiraan PPh +Rp10.000" — tidak diam',
  bln(T6, '2026-05').status.kode === 'berubah' && bln(T6, '2026-05').berubah.omzet === 2 * JT && bln(T6, '2026-05').berubah.pph === 10000 && /omzet \+Rp2\.000\.000 · perkiraan PPh \+Rp10\.000/.test(bln(T6, '2026-05').status.teks), J(bln(T6, '2026-05').status));

// ---- 7 · beranda & pengingat
var PH = pjPerhatian(KINI);
ok('beranda (owner): SATU baris pajak menyebut lewat tempo, kurang/berubah — berlabel perkiraan', PH.length === 1 && /lewat tempo/.test(PH[0].teks) && /berubah/.test(PH[0].teks) && /bukan nasihat pajak/.test(PH[0].teks) && PH[0].awas, J(PH));
var SG = pjSumberPengingat(KINI);
ok('pengingat pajak: bulan lalu (Agu) terutang & belum disetor → satu sumber jatuh 15 Sep dengan KAP-KJS 411128-420', SG.length === 1 && SG[0].jenis === 'pajak' && SG[0].jatuh === '2026-09-15' && SG[0].n === 350000 && /411128-420/.test(SG[0].ket), J(SG));
tulis(susunSetoran({ masaPajak: '2026-08', tanggalSetor: '2026-09-18', jumlah: '350.000', ntpn: '9999000011112222' }, W, KINI));
ok('sesudah Agu disetor → pengingat pajak hilang', pjSumberPengingat(KINI).length === 0);
ok('hapus catatan setoran butuh ketukan kedua', susunHapusSetoran(cacheMentah('pajakSetoran')[0].id).perluYakin === true && !!susunHapusSetoran(cacheMentah('pajakSetoran')[0].id, true).hapus);

// ---- 8 · dua ambang
var PX = { batasOmzet: 1000 };
ok('ambang atas: tanda 70/85/95/100 % dari kumulatif gabung (699 → belum; 700 → 70; 850 → 85; 950 → 95; 1000 → 100)', [[699, 0], [700, 70], [849, 70], [850, 85], [950, 95], [1000, 100], [1300, 100]].every(function (x) { return pjAmbang(x[0], PX, 2025, '2026-09-19').level === x[1]; }));
ok('di 85 % ke atas kalimatnya menyebut yang perlu ditanyakan ke konsultan: tarif 0,5 % tahun depan, pembukuan, PKP', /tarif 0,5 % tahun depan, kewajiban pembukuan, dan kemungkinan wajib PKP/.test(pjAmbang(900, PX, 2025, '2026-09-19').akibat) && !pjAmbang(800, PX, 2025, '2026-09-19').akibat);
var AM = pjTahun(2026, KINI).ambang;
ok('proyeksi akhir tahun [PERKIRAAN] = kumulatif + rata-rata harian 30 hari terakhir (60 jt / 30 = 2 jt) × sisa hari (103) = 902 + 206 = 1.108 jt', AM.proyeksi.rata === 2 * JT && AM.proyeksi.sisaHari === 103 && AM.proyeksi.n === 1108 * JT && /PERKIRAAN/.test(AM.teks), J(AM));
tulis(susunProfilPajak({ omzetTahunLalu: '5.000.000.000' }, W));
ok('omzet tahun lalu > batas atas → peringatan tetap "tarif 0,5 % kemungkinan tidak berlaku tahun ini. Tanyakan konsultan." — hitungan tetap tampil', /kemungkinan tidak berlaku tahun ini/.test(pjTahun(2026, KINI).peringatanTahunLalu) && pjTahun(2026, KINI).totalPph > 0);
tulis(susunProfilPajak({ omzetTahunLalu: '' }, W));
ok('omzet tahun lalu dikosongkan = tidak diketahui (null), bukan nol; peringatan hilang', pjProfil().omzetTahunLalu === null && !pjTahun(2026, KINI).peringatanTahunLalu);

// ---- 9 · badan
tulis(susunProfilPajak({ jenisWp: 'badan' }, W)); var TB = pjTahun(2026, KINI);
ok('badan → kolom PPh "tidak dihitung — tanyakan konsultan", tanpa angka tebakan; DK3 juga tanpa angka', TB.totalPph === null && TB.daftar.every(function (b) { return b.pph === null && b.status.kode === 'badan'; }) && rekapOmzet(KINI).perkiraanTahun === null && /badan/.test(rekapOmzet(KINI).tarifTeks), J(bln(TB, '2026-06').status));
tulis(susunProfilPajak({ jenisWp: 'orangPribadi' }, W));

// ---- 10 · DK3 = layar Pajak
var RO = rekapOmzet(KINI); var T7 = pjTahun(2026, KINI);
ok('DK3 dan layar Pajak memberi perkiraan yang SAMA per bulan & setahun (batas bebas ikut di DK3)', RO.daftar.filter(function (b) { return b.key.slice(0, 4) === '2026'; }).every(function (b) { return b.perkiraan === bln(T7, b.key).pph; }) && RO.perkiraanTahun === T7.totalPph && RO.perkiraanTahun === 2010000,
  J([RO.perkiraanTahun, T7.totalPph]));
ok('DK3 omzet per bulan = omzet sistem layar Pajak (rupiah demi rupiah)', RO.daftar.filter(function (b) { return b.key.slice(0, 4) === '2026' && b.key >= '2026-03'; }).every(function (b) { return b.omzet === bln(T7, b.key).sistem; }));

// ---- 11 · regresi penulis aturanToko/rekapOmzet (profil tidak boleh hilang)
pasok('batchMasuk', cacheMentah('batch').concat([{ id: 'tb-2025', tanggal: '2025-12-31', pemasok: 'TUTUP BUKU 2025', tutupBuku: true, tahunDari: 2025, merkList: [], stokAwal: false }]));
tulis(susunProfilPajak({ wpAtasNama: 'Pemilik Contoh', statusPkp: 'bukan', tahunMulaiTarifFinal: '2019' }, W));
tulis(susunTandaLapor('2025-12', W)); tulis(susunAturRekap({ tarifPerMil: '5', batasOmzet: '4.800.000.000', tanggalLapor: '15' }, W));
var P2 = pjProfil(); var D2 = pjDokRekap();
ok('regresi: simpan profil → tandai lapor (DK3) → ubah tarif (DK3) → profil UTUH (atas nama, jenis, PKP, tahun mulai, batas bebas, sumber aturan) dan tanda lapor tetap',
  P2.wpAtasNama === 'Pemilik Contoh' && P2.jenisWp === 'orangPribadi' && P2.statusPkp === 'bukan' && P2.tahunMulaiTarifFinal === 2019 && P2.batasBebas === 500 * JT && !!P2.sumberAturan && !!D2.lapor['2025-12'] && P2.tarifPerMil === 5, J(D2));
ok('field yang TIDAK dikenal penulis mana pun juga ikut terbawa (penulis gabung, bukan daftar kolom)', (function () { terapkanKeCache([{ koleksi: 'aturanToko', data: Object.assign({}, pjDokRekap(), { fieldMasaDepan: 'x' }) }]); return susunAturRekap({ tarifPerMil: '5', batasOmzet: '0', tanggalLapor: '15' }, W).dokumen[0].data.fieldMasaDepan === 'x' && susunTandaLapor('2025-12', W, true).dokumen[0].data.fieldMasaDepan === 'x'; })());

// ---- 12 · data pribadi & cetak
ok('NIK/NPWP/nomor rekening ditolak di teks bebas (atas nama, catatan setoran, keterangan omzet luar); angka rupiah bertitik ribuan tetap boleh',
  !!susunProfilPajak({ wpAtasNama: 'Pemilik 3201234567890001' }, W).tolak && !!susunSetoran({ masaPajak: '2026-07', tanggalSetor: '2026-09-18', jumlah: '300.000', ntpn: '1234123412341234', catatan: 'npwp 01.234.567.8-901.000' }, W, KINI).tolak
  && !!susunOmzetLuar({ bulan: '2026-01', sumber: 'catatanLama', jumlah: '1', keterangan: 'rek 1234567890' }, W).tolak && !pjAdaNomorPribadi('omzet Rp1.500.000.000 dari buku') && pjAdaNomorPribadi('3201234567890001'));
var DR = dokRekapPajak(pjTahun(2026, KINI), { nama: 'Toko Contoh', alamat: 'Jl. Contoh', versi: 1 });
ok('cetak "Rekap pajak untuk konsultan": profil, per bulan (sistem / diketik owner + sumber / kumulatif / PPh / setoran & NTPN / status), sumber aturan dengan [BELUM TERVERIFIKASI], label perkiraan',
  DR.jenis === 'pajak' && /bukan nasihat pajak/.test(DR.sub) && DR.baris.some(function (b) { return /diketik owner: catatan lama/.test(b.nama); }) && DR.baris.some(function (b) { return /NTPN AB12CD34EF56GH78/.test(b.nama); })
  && DR.baris.filter(function (b) { return /^\[BELUM TERVERIFIKASI\]/.test(b.nama); }).length === 2 && DR.baris.filter(function (b) { return b.nama.indexOf('PP 20/2026') >= 0 || b.nama.indexOf('PMK 164') >= 0; }).length >= 4 && /SEBELUM potongan/.test(DR.catatan), J(DR.baris.slice(0, 3)));
ok('sumber aturan: 9 klaim, masing-masing ber-URL resmi & tanggal lihat; 2 belum terverifikasi (NTPN era Coretax, pembulatan)', PJ_SUMBER.length === 9 && PJ_SUMBER.every(function (s) { return /^https:\/\/(peraturan\.bpk\.go\.id|jdih\.kemenkeu\.go\.id|(www\.)?pajak\.go\.id)\//.test(s.url) && s.lihat === '2026-09-24'; }) && PJ_SUMBER.filter(function (s) { return !s.terverifikasi; }).length === 2);

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var KINI = new Date(Date.now()); var salah = []; var th = Number(hariIniIso(KINI).slice(0, 4));
var T = pjTahun(th, KINI); var RO = rekapOmzet(KINI); var dicek = 0;
T.daftar.forEach(function (b) { if (b.sistem === null) return; dicek++; var mesin = hitungLabaRentang(function (t) { return !!t && bulanDari(t) === b.key; }).omzetPenuh; if (b.sistem !== mesin) salah.push(b.key + ': layar Pajak ≠ mesin laba');
  var d = RO.daftar.find(function (x) { return x.key === b.key; }); if (d && d.omzet !== b.sistem) salah.push(b.key + ': DK3 ≠ layar Pajak'); });
// dengan aturan terpasang (di memori saja): DK3 dan layar Pajak tetap satu angka
terapkanKeCache([{ koleksi: 'aturanToko', data: pjGabungRekap({ tarifPerMil: 5, batasBebas: 500000000, batasOmzet: 4800000000 }, { tanggal: hariIniIso(KINI), jam: '10:00' }) }]);
var T2 = pjTahun(th, KINI); var RO2 = rekapOmzet(KINI); if (RO2.perkiraanTahun !== T2.totalPph) salah.push('perkiraan DK3 ≠ layar Pajak');
print(JSON.stringify({ salah: salah, bulanDicek: dicek, bulanBelumDiisi: T2.kosong, awalSistem: T2.awalSistem, status: T2.daftar.map(function (b) { return b.status.kode; }) }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:1500]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js):
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            'tarif dikenakan ke seluruh omzet (tanpa batas bebas)': js.replace("const kena = Math.max(0, kum - Math.max(kumSebelum, bebas));", "const kena = Math.max(0, kum - kumSebelum);"),
            'bulan yang melewati batas dikenai penuh (bukan kelebihannya)': js.replace("const kena = Math.max(0, kum - Math.max(kumSebelum, bebas));", "const kena = kum > bebas ? omzet : 0;"),
            'pembulatan ke atas': js.replace("const pph = hitung ? Math.floor(kena * P.tarifPerMil / 1000) : null;", "const pph = hitung ? Math.ceil(kena * P.tarifPerMil / 1000) : null;"),
            'catatan lama diterima di bulan yang punya penjualan (terhitung dua kali)': js.replace("if (kAwal && bulan > kAwal) return { tolak:", "if (false) return { tolak:"),
            'usaha pasangan ikut PPh toko ini': js.replace("const omzet = (S.omzet || 0) + (lama || 0) + (lain || 0);", "const omzet = (S.omzet || 0) + (lama || 0) + (lain || 0) + (pasangan || 0);"),
            'bulan kosong dianggap nol & lengkap': js.replace("const lengkap = adaSistem ? (!sebagian || lama !== null) : lama !== null;", "const lengkap = true;"),
            'isian kosong disimpan sebagai nol': js.replace("if (ugKosong(isi.jumlah)) return { tolak: 'Ketik jumlahnya", "if (false) return { tolak: 'Ketik jumlahnya"),
            'angka berubah sesudah setor tidak terdeteksi': js.replace("const berubah = adaPotret &&", "const berubah = false &&"),
            'kurang setor dianggap disetor': js.replace("if (d < 0) return { kode: 'kurang'", "if (false) return { kode: 'kurang'"),
            'lewat tempo tidak ditandai': js.replace("if (B.pph > 0 && !B.berjalan && iso > B.tempo) return", "if (false) return"),
            'ambang 85 % hilang': js.replace("export const PJ_AMBANG = [70, 85, 95, 100];", "export const PJ_AMBANG = [70, 95, 100];").replace("const PJ_AMBANG = [70, 85, 95, 100];", "const PJ_AMBANG = [70, 95, 100];"),
            'proyeksi tanpa sisa hari': js.replace("n: Math.round(kumGabung + rata * sisa)", "n: Math.round(kumGabung)"),
            'badan diberi angka tebakan': js.replace("const hitung = P.jenisWp !== 'badan' && P.tarifPerMil > 0;", "const hitung = P.tarifPerMil > 0;"),
            'peringatan omzet tahun lalu hilang': js.replace("P.omzetTahunLalu > P.batasOmzet ? 'Omzet tahun lalu melewati batas", "false ? 'Omzet tahun lalu melewati batas"),
            'penulis lama DK3 (tandai lapor) menimpa tanpa menggabung → profil hilang': js.replace("data: pjGabungRekap({ lapor }, w)", "data: { id: 'rekapOmzet', tanggal: w.tanggal, jam: w.jam, tarifPerMil: A.tarifPerMil, batasOmzet: A.batasOmzet, tanggalLapor: A.tanggalLapor, lapor }"),
            'penulis lama DK3 (atur tarif) menimpa tanpa menggabung → profil hilang': js.replace("data: pjGabungRekap({ tarifPerMil: Math.round(tarif), batasOmzet: Math.round(batas), tanggalLapor: Math.round(tgl), lapor: A.lapor }, w)", "data: { id: 'rekapOmzet', tanggal: w.tanggal, jam: w.jam, tarifPerMil: Math.round(tarif), batasOmzet: Math.round(batas), tanggalLapor: Math.round(tgl), lapor: A.lapor }"),
            'DK3 kembali ke rumus lama (tanpa batas bebas)': js.replace("perkiraan: pb ? pb.pph : null,", "perkiraan: A.tarifPerMil ? Math.round(S.omzet * A.tarifPerMil / 1000) : null,"),
            'NIK/NPWP boleh disimpan': js.replace("return x.replace(/\\D/g, '').length >= 10; });", "return false; });"),
            'setoran mundur tanpa catatan diterima': js.replace("if ((mundur || !ntpn) && !cat) return", "if (false) return"),
            'pengingat berbunyi walau sudah disetor': js.replace("if (!b || !T.hitung || !(b.pph > 0) || b.setor.length) return [];", "if (!b || !T.hitung || !(b.pph > 0)) return [];"),
            'sumber aturan yang belum terverifikasi ditulis sebagai fakta': js.replace("baris.push({ nama: (s.terverifikasi ? '' : '[BELUM TERVERIFIKASI] ') + s.klaim, teks: '' })", "baris.push({ nama: s.klaim, teks: '' })"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, 'backup-batch-*.json')), key=os.path.basename)
    if cad and not g:
        h, e = jalan(JAM_TETAP.replace("'2026-09-19T10:00:00+07:00'", "'2026-09-24T10:00:00+07:00'") + js + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if h is None: print('ASAP JATUH: ' + e); sys.exit(2)
        print('ASAP DATA TOKO (%s): %s' % (os.path.basename(cad[-1]), json.dumps(h, ensure_ascii=False)))
        if h['salah']: sys.exit(2)
    sys.exit(1 if g else 0)
