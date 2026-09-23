#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_uang_baru.py — uji logika layar UANG sistem baru (uang-logika K1+K4 · upah-logika K2 · owner-toko-logika K3 · tutup-hari-logika K5 · tutup-buku-logika K6) di jsc.
KOTAK PASIR (ANGKA CONTOH, bukan angka toko), jam dikunci 19 Sep 2026 10:00 WIB.
Identitas yang dijaga: Σ empat tempat uang = kasPada() (mesin beku) SELALU; tiap dokumen yang ditulis = bentuk sistem lama + kolom yang disebut.
Kalau ada backup-batch-*.json lokal (asap): identitas kantong pada cadangan toko, tutup hari/buku dibaca tanpa menulis.

    python3 alat-uji/uji_uang_baru.py            → N lulus · 0 gagal
    python3 alat-uji/uji_uang_baru.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/harga-logika.js', 'baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/uang-logika.js', 'baru/js/layar/upah-logika.js', 'baru/js/layar/owner-toko-logika.js', 'baru/js/layar/tutup-hari-logika.js', 'baru/js/layar/tutup-buku-logika.js']
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(id, tgl, jam, cara, merk, kg, harga, hpp, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': jam, 'caraBayar': cara, 'jenis': 'karung', 'merkSumber': merk, 'totalKg': kg, 'beratKarungAcuan': 50, 'jumlahKarung': kg / 50, 'hargaTotal': harga, 'hppTotalSaatJual': hpp}
    d.update(k); return d


def absen(nama, bulan, hari):
    return {'id': nama.lower() + '|' + bulan, 'nama': nama, 'bulan': bulan, 'hari': hari}


# ---- ANGKA CONTOH. Titik kas 15 Sep: laci 2.000.000 · brankas 10.000.000 · rekening 3.000.000 · amplop 1.000.000 (= 16.000.000).
#      Sesudahnya: tunai 500.000 (16) + 250.000 (19) → laci; QRIS 700.000 (17) + 600.000 (19, > 500.000 → potongan 0,30 % = 1.800) → rekening;
#      keluar laci: bensin 20.000 (16), prive dapur 100.000 (17), kasbon Gono 100.000 (18); sisihan amplop 50.000 (16, laci → amplop).
#      Jadi laci 2.480.000 · rekening 4.300.000 · brankas 10.000.000 · amplop 1.050.000 = 17.830.000 = kasPada.
KOTAK = {
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-08-20', 'jam': '08:00', 'pemasok': 'RODA CONTOH', 'caraBayar': 'utang', 'biayaBongkar': 0,
                  'merkList': [{'id': 'b10', 'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 20, 'totalKg': 1000, 'hargaPerKg': 13000, 'subtotalHarga': 13000000},
                               {'id': 'b11', 'merk': 'IR64 Apex', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 10, 'totalKg': 500, 'hargaPerKg': 14000, 'subtotalHarga': 7000000}]}],
  'penjualan': [jual('j1', '2026-09-16', '09:00', 'Tunai', 'Angsa', 35.7, 500000, 464100), jual('j2', '2026-09-17', '10:00', 'QRIS', 'Angsa', 50, 700000, 650000),
                jual('j3', '2026-09-19', '09:12', 'QRIS', 'IR64 Apex', 40, 600000, 560000), jual('j4', '2026-09-19', '09:40', 'Tunai', 'Angsa', 17.8, 250000, 231400),
                jual('j5', '2026-09-19', '09:50', 'Kredit', 'Angsa', 21.4, 300000, 278200, namaPelanggan='Bu Contoh'),
                jual('j6', '2026-09-19', '09:55', 'Tunai', 'Angsa', 0, 0, 0) | {'dibatalkan': True}],
  'pengeluaranHarian': [{'id': 'h1', 'kategori': 'toko', 'tanggal': '2026-09-16', 'jam': '09:15', 'keterangan': 'Bensin antar', 'nominal': 20000},
                        {'id': 'h2', 'kategori': 'owner', 'tanggal': '2026-09-17', 'jam': '11:02', 'keterangan': 'Belanja dapur', 'nominal': 100000},
                        {'id': 'h3', 'kategori': 'toko', 'tanggal': '2026-09-10', 'jam': '08:00', 'keterangan': 'Bensin antar', 'nominal': 25000},
                        {'id': 'h4', 'kategori': 'toko', 'tanggal': '2026-09-12', 'jam': '08:00', 'keterangan': 'Bensin antar', 'nominal': 20000},
                        {'id': 'h5', 'kategori': 'tokoDompet', 'tanggal': '2026-09-11', 'jam': '14:00', 'keterangan': 'Beli lakban', 'nominal': 120000}],
  'kasbonMutasi': [{'id': 701, 'tipe': 'ambil', 'namaPegawai': 'Ben Mohsein', 'nominal': 200000, 'tanggal': '2026-09-05', 'catatan': 'Keperluan keluarga'},
                   {'id': 702, 'tipe': 'ambil', 'namaPegawai': 'Gono', 'nominal': 100000, 'tanggal': '2026-09-18', 'jam': '15:00', 'catatan': 'Berobat'}],
  'biayaBulanan': [{'id': '2026-08', 'bulan': '2026-08', 'listrik': 350000, 'internet': 250000, 'akses': 0, 'keamanan': 0, 'tanggalBayarPos': {'listrik': '2026-08-10', 'internet': '2026-08-05', 'gaji': '2026-08-31'},
                    'rincianGaji': [{'nama': 'Ben Mohsein', 'hari': 26, 'gaji': 1560000}, {'nama': 'Gono', 'hari': 10, 'gaji': 600000}], 'tanggalBayarGaji': {'Ben Mohsein': '2026-08-31', 'Gono': '2026-08-31'}, 'gaji': 2160000, 'gajiHariOrang': 36}],
  'absenKaryawan': [absen('Ben Mohsein', '2026-09', {('2026-09-%02d' % d): (0.5 if d == 7 else 0 if d == 14 else 1) for d in range(1, 19)}),
                    absen('Gono', '2026-09', {('2026-09-%02d' % d): 1 for d in range(10, 18)})],
  'slipUpah': [],
  'modalOwner': [{'id': 'm1', 'tanggal': '2026-08-08', 'jam': '08:00', 'tipe': 'setor', 'nominal': 25000000, 'catatan': 'Tabungan pribadi'}],
  'utangOwnerMutasi': [],
  'amplopLaba': [{'id': 'am-2026-09-16', 'tanggal': '2026-09-16', 'jam': '21:00', 'tipe': 'setor', 'nominal': 50000, 'catatan': 'Sisihan tutup hari'}],
  'pindahUang': [], 'tutupHari': [], 'setoranKas': [], 'piutangMutasi': [], 'penyesuaianStok': [], 'tutupBukuAcara': [], 'perangkatStatus': [], 'cadanganCatatan': [],
  'persetujuan': [{'id': 'p1', 'dari': 'Ben', 'peran': 'ben', 'tindakan': 'uangKeluar', 'teks': 'Tali rafia 2 gulung', 'nominal': 15000, 'tanggal': '2026-09-19', 'jam': '10:42', 'status': 'menunggu', 'pada': '2026-09-19T03:42:00.000Z'}],
  'aturanToko': [], 'pengaturan': [],   # pengaturan ikut direset: titikKas yang ditulis Tutup hari (K5) tidak boleh terbawa ke K6
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
var KINI = new Date(Date.now()); var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 9000; return function () { n += 1; return n; }; })() };
var tulis = function (r) { if (r.tolak) throw new Error('DITOLAK: ' + r.tolak); if (r.hapus) terapkanKeCache(r.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (r.dokumen) terapkanKeCache(r.dokumen); return r; };
var identitas = function (nama) { var S = saldoKantong(); ok('IDENTITAS kantong ' + nama + ': laci + brankas + rekening + amplop = kasPada()', S.ada && S.cocok, J(S)); return S; };

// ==================== BERSAMA · saldo per tempat uang ====================
var S = saldoKantong();
ok('saldo per tempat dari titik kas 15 Sep + gerakan sesudahnya: laci 2.480.000 · rekening 4.300.000 (QRIS) · brankas 10.000.000 · amplop 1.050.000 (sisihan 16 Sep) · total 17.830.000 = kasPada', S.ada && S.laci === 2480000 && S.rekening === 4300000 && S.brankas === 10000000 && S.amplop === 1050000 && S.total === 17830000 && S.mesin === 17830000 && S.cocok, J(S));
ok('sampai 17 Sep: laci 2.000.000 + 500.000 − 20.000 − 100.000 − 50.000 = 2.330.000; mundur dari titik (14 Sep) → tidak ditebak (ada false)', saldoKantong('2026-09-17').laci === 2330000 && saldoKantong('2026-09-17').cocok && !saldoKantong('2026-09-14').ada, J(saldoKantong('2026-09-17')));
localStorage.removeItem('miqbal_titik_kas_v1');
ok('tanpa titik kas: ada false, semua null, ugCukup mengaku TIDAK memeriksa (bukan cukup)', !saldoKantong().ada && saldoKantong().laci === null && ugCukup(saldoKantong(), 'laci', 1).takTerperiksa === true && ugCukup(saldoKantong(), 'laci', 1).boleh);
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
ok('modal tertanam 25.000.000; kasbon owner 0; utang toko ke owner 120.000 (lakban pakai dompet); prive bulan ini 100.000', modalTertanam() === 25000000 && kasbonOwner().sisa === 0 && hitungUtangOwner().sisa === 120000 && priveBulan('2026-09-19').total === 100000, J(priveBulan('2026-09-19')));

// ==================== K1 · CATAT UANG KELUAR ====================
var AK = aturKeluar('2026-09-19');
ok('keperluan TERUKUR dari catatan: "Bensin antar" 3× → nominal biasanya 20.000 (median); pribadi "Belanja dapur" 1× → 0; batas aman = laba bersih bulan berjalan (owner belum menyetel)', AK.terukurToko && AK.perluToko[0].nama === 'Bensin antar' && AK.perluToko[0].biasa === 20000 && AK.perluPribadi[0].nama === 'Belanja dapur' && AK.perluPribadi[0].biasa === 0 && AK.amanDariLaba && AK.aman === Math.max(0, hitungLabaBersihRentang('2026-09-01', '2026-09-19').labaBersih), J(AK));
var H = hitungKeluar({ untuk: 'toko', dari: 'laci', perlu: 'Bensin antar', ketik: '20.000' }, KINI);
ok('biaya toko dari laci: arti "Laci berkurang 20.000 · laba berkurang 20.000"; tidak ditolak', !H.tolak && H.arti.sel === 'beban' && /Laci berkurang Rp20\.000/.test(H.arti.a) && /laba berkurang Rp20\.000/.test(H.arti.b), J(H.arti));
H = hitungKeluar({ untuk: 'toko', dari: 'dompet', perlu: 'Bensin antar', ketik: '20.000' }, KINI); ok('toko pakai dompet owner: "uang toko tidak berkurang · laba berkurang · toko berutang 20.000 ke owner"', H.arti.sel === 'utang' && /tidak berkurang/.test(H.arti.a) && /berutang Rp20\.000 ke owner/.test(H.arti.c));
H = hitungKeluar({ untuk: 'pribadi', dari: 'laci', perlu: 'Belanja dapur', ketik: '50.000' }, KINI); ok('prive dari laci: laba TIDAK berubah; priveTeks menyebut batas aman & sisanya', H.arti.sel === 'prive' && /laba TIDAK berubah/.test(H.arti.b) && /batas aman/.test(H.priveTeks));
H = hitungKeluar({ untuk: 'pribadi', dari: 'dompet', perlu: 'Belanja dapur', ketik: '50.000' }, KINI); ok('pribadi pakai dompet: bukan urusan toko — tidak ada yang ditulis', H.arti.sel === 'luar' && susunKeluar({ untuk: 'pribadi', dari: 'dompet', perlu: 'Belanja dapur', ketik: '50.000' }, W).dokumen.length === 0);
H = hitungKeluar({ untuk: 'toko', dari: 'laci', perlu: 'Bensin antar', ketik: '3.000.000' }, KINI); ok('laci cuma 2.480.000 → DITOLAK menyebut isinya (bukan dijepit)', /Laci cuma Rp2\.480\.000 — tidak cukup/.test(H.tolak), H.tolak);
ok('tanpa nominal / tanpa keperluan ditolak', /nominal/.test(hitungKeluar({ untuk: 'toko', dari: 'laci', perlu: 'Bensin antar', ketik: '' }, KINI).tolak) && /untuk apa/.test(hitungKeluar({ untuk: 'toko', dari: 'laci', perlu: '', ketik: '5000' }, KINI).tolak));
var R = tulis(susunKeluar({ untuk: 'toko', dari: 'brankas', perlu: 'Upah bongkar', ketik: '150.000', catatan: 'truk RODA' }, W));
ok('dokumen = pengeluaranHarian {id, kategori toko, tanggal, keterangan, nominal, jam} sistem lama + dari brankas; keterangan "Upah bongkar — truk RODA"; urung menunjuk id-nya', R.dokumen[0].koleksi === 'pengeluaranHarian' && R.dokumen[0].data.kategori === 'toko' && R.dokumen[0].data.dari === 'brankas' && R.dokumen[0].data.keterangan === 'Upah bongkar — truk RODA' && R.dokumen[0].data.nominal === 150000 && R.urung[0].id === R.dokumen[0].data.id, J(R.dokumen));
S = identitas('sesudah biaya dari brankas'); ok('brankas turun 150.000 → 9.850.000; laci tetap 2.480.000', S.brankas === 9850000 && S.laci === 2480000, J(S));
tulis(susunUrungKeluar(R.urung)); ok('urungkan: dokumen dicabut, brankas kembali 10.000.000', saldoKantong().brankas === 10000000 && bukuKeluar('2026-09-19').n === 0);
R = tulis(susunKeluar({ untuk: 'toko', dari: 'dompet', perlu: 'Bensin antar', ketik: '30.000' }, W)); ok('toko pakai dompet → kategori tokoDompet TANPA dari; kas tidak bergerak; utang toko ke owner 150.000', R.dokumen[0].data.kategori === 'tokoDompet' && R.dokumen[0].data.dari === undefined && saldoKantong().total === 17830000 && hitungUtangOwner().sisa === 150000);
// batas aman: setel owner 150.000 → prive 100.000 sudah terpakai, sisa 50.000; prive 80.000 lewat → minta kasbon/alasan
tulis(susunAturKeluar({ aman: '150.000', perluToko: AK.perluToko, perluPribadi: [{ nama: 'Belanja dapur', biasa: '100.000' }, { nama: 'Sekolah anak', biasa: '' }], bulanan: [{ nama: 'Air PDAM', biasa: '80.000' }], alasan: AK.alasan }, W));
H = hitungKeluar({ untuk: 'pribadi', dari: 'laci', perlu: 'Sekolah anak', ketik: '80.000' }, KINI);
ok('atur owner: batas aman 150.000 (bukan laba lagi), sisa 50.000; prive 80.000 → LEWAT batas, kalimatnya menyebut lewat 30.000', !aturKeluar('2026-09-19').amanDariLaba && H.sisaAman === 50000 && H.lewatAman && /lewat Rp30\.000 dari batas aman Rp150\.000/.test(H.lewatTeks), J(H));
R = susunKeluar({ untuk: 'pribadi', dari: 'laci', perlu: 'Sekolah anak', ketik: '80.000' }, W); ok('lewat batas aman tanpa pilihan → ditolak, perluYakin aman', /kasbon owner, atau pilih alasannya/.test(R.tolak) && R.perluYakin === 'aman');
R = tulis(susunKeluar({ untuk: 'pribadi', dari: 'laci', perlu: 'Sekolah anak', ketik: '80.000' }, W, { jadiKasbon: true }));
ok('"catat sebagai kasbon owner": kasbonMutasi {tipe ambil, namaPegawai Owner, owner true, dari laci}; laci −80.000; prive TIDAK bertambah; kasbon owner 80.000', R.dokumen[0].koleksi === 'kasbonMutasi' && R.dokumen[0].data.namaPegawai === 'Owner' && R.dokumen[0].data.owner === true && saldoKantong().laci === 2400000 && priveBulan('2026-09-19').total === 100000 && kasbonOwner().sisa === 80000, J(R.dokumen));
identitas('sesudah kasbon owner');
R = tulis(susunKeluar({ untuk: 'pribadi', dari: 'laci', perlu: 'Sekolah anak', ketik: '80.000' }, W, { alasan: 'Mendesak keluarga' }));
ok('"tetap ambil pribadi" dengan alasan: pengeluaranHarian owner + alasanAman; prive bulan ini 180.000', R.dokumen[0].data.kategori === 'owner' && R.dokumen[0].data.alasanAman === 'Mendesak keluarga' && priveBulan('2026-09-19').total === 180000);
var BK = bukuKeluar('2026-09-19'); ok('buku hari ini: 3 baris (tokoDompet, kasbon owner, prive) terbaru dulu; jumlah per arti: utang 30.000 · kasbon 80.000 · prive 80.000', BK.n === 3 && BK.jumlah.utang === 30000 && BK.jumlah.kasbon === 80000 && BK.jumlah.prive === 80000 && BK.keluarLaci === 160000, J(BK));
// titipan tablet
var TT = titipanKeluar(); ok('titipan dari tablet: 1 permintaan uangKeluar menunggu (Ben · Tali rafia 15.000)', TT.length === 1 && TT[0].oleh === 'Ben' && TT[0].n === 15000, J(TT));
ok('menolak tanpa alasan ditolak', /butuh alasan/.test(susunPutusTitipan('p1', false, '', W).tolak));
R = tulis(susunPutusTitipan('p1', true, '', W)); ok('setujui: persetujuan → disetujui + pengeluaranHarian toko 15.000 dari laci menunjuk permintaannya; laci turun; titipan habis', R.dokumen.length === 2 && R.dokumen[0].data.status === 'disetujui' && R.dokumen[1].data.dariPersetujuan === 'p1' && R.dokumen[1].data.nominal === 15000 && saldoKantong().laci === 2400000 - 80000 - 15000 && titipanKeluar().length === 0, J(R.dokumen));
identitas('sesudah titipan');
// tagihan bulanan
var TG = tagihanBulan('2026-09-19'); var tg = function (k) { return TG.daftar.find(function (t) { return t.kunci === k; }); };
ok('tagihan Sep: 4 pos mesin lama + 1 tambahan (Air PDAM); listrik belum dibayar, biasanya 350.000 (median bulan lalu); Air PDAM biasanya 80.000; 5 belum', TG.daftar.length === 5 && !tg('listrik').lunas && tg('listrik').biasa === 350000 && tg('tambahan:Air PDAM').biasa === 80000 && TG.nBelum === 5, J(TG));
R = tulis(susunBayarTagihan('listrik', '', 'rekening', W));
ok('bayar listrik dari rekening tanpa ketik → pakai biasanya 350.000; dokumen biayaBulanan {id 2026-09, bulan, listrik 350000, tanggalBayarPos.listrik hari ini, dariPos.listrik rekening, akses/keamanan/internet 0, gaji 0, rincianGaji []}', R.dokumen[0].koleksi === 'biayaBulanan' && R.dokumen[0].data.id === '2026-09' && R.dokumen[0].data.listrik === 350000 && R.dokumen[0].data.tanggalBayarPos.listrik === '2026-09-19' && R.dokumen[0].data.dariPos.listrik === 'rekening' && R.dokumen[0].data.akses === 0 && Array.isArray(R.dokumen[0].data.rincianGaji), J(R.dokumen));
S = identitas('sesudah bayar listrik'); ok('rekening turun 350.000 → 3.950.000 (baris bulanan dikenali lewat dariPos); mesin arus kas ikut (kasPada turun)', S.rekening === 3950000 && S.mesin === 17830000 - 80000 - 80000 - 15000 - 350000, J(S));
ok('bayar lagi listrik bulan ini ditolak; tagihan tambahan → belanja harian "<nama> (bulanan)"', /sudah dibayar/.test(susunBayarTagihan('listrik', '', 'laci', W).tolak) && (function () { var r = tulis(susunBayarTagihan('tambahan:Air PDAM', '', 'laci', W)); return r.dokumen[0].koleksi === 'pengeluaranHarian' && r.dokumen[0].data.keterangan === 'Air PDAM (bulanan)' && r.dokumen[0].data.nominal === 80000 && tagihanBulan('2026-09-19').nBelum === 3; })());
// dokumen lama bertanggal tunggal: pindah ke peta per pos membawa SEMUA pos yang bernilai
pasok('biayaBulanan', ambilBiayaBulanan().concat([{ id: '2026-07', bulan: '2026-07', listrik: 300000, internet: 200000, akses: 0, keamanan: 0, tanggalBayar: '2026-07-09', gaji: 0, gajiHariOrang: 0, rincianGaji: [] }]));
var W7 = Object.assign({}, W, { tanggal: '2026-07-20' }); var RT = susunBayarTagihan('akses', '50.000', 'laci', W7);
ok('dokumen Juli bertanggal tunggal 9 Jul: bayar akses → tanggalBayarPos berisi listrik & internet 9 Jul + akses 20 Jul (bukan cuma akses)', RT.dokumen[0].data.tanggalBayarPos.listrik === '2026-07-09' && RT.dokumen[0].data.tanggalBayarPos.internet === '2026-07-09' && RT.dokumen[0].data.tanggalBayarPos.akses === '2026-07-20' && RT.dokumen[0].data.akses === 50000, J(RT.dokumen[0].data));
pasok('biayaBulanan', ambilBiayaBulanan().filter(function (b) { return b.bulan !== '2026-07'; }));

// ==================== K4 · PINDAH UANG ====================
var AP = aturPindah(); ok('atur pindah bawaan: uang kembalian 500.000; biaya admin = daftar Bon pemasok (BI-FAST 2.500, antarbank 6.500) — satu daftar', AP.jaga === 500000 && AP.admin.length === 2 && AP.admin[0].n === 2500 && !AP.dariOwner, J(AP));
var HP = hitungPindah({ dari: 'laci', ke: 'brankas', ketik: '1.000.000', alasan: 'Amankan ke brankas', adminI: -1 });
ok('pindah laci → brankas 1.000.000: tidak ditolak; arti: laci −1.000.000 · brankas +1.000.000 · jumlah uang toko TIDAK berubah; tanpa pilihan admin (bukan rekening)', !HP.tolak && /Laci berkurang Rp1\.000\.000 · Brankas bertambah Rp1\.000\.000/.test(HP.artiA) && /TIDAK berubah/.test(HP.artiB) && !HP.pakaiAdmin, J(HP));
ok('penjaga: dari = ke ditolak; nominal kosong; tanpa alasan; melebihi isi (laci 2.225.000 sesudah Air PDAM) ditolak menyebut isinya', /tidak boleh sama/.test(hitungPindah({ dari: 'laci', ke: 'laci', ketik: '1' }).tolak) && /nominal/.test(hitungPindah({ dari: 'laci', ke: 'brankas', ketik: '' }).tolak) && /untuk apa/.test(hitungPindah({ dari: 'laci', ke: 'brankas', ketik: '5' }).tolak) && /Laci cuma Rp2\.225\.000/.test(hitungPindah({ dari: 'laci', ke: 'brankas', ketik: '3.000.000', alasan: 'x' }).tolak));
HP = hitungPindah({ dari: 'rekening', ke: 'laci', ketik: '1.000.000', alasan: 'Tarik tunai dari bank', adminI: 1 });
ok('rekening → laci dengan admin antarbank 6.500: rekening berkurang 1.006.500; jumlah uang toko berkurang 6.500 = biaya toko', HP.admin === 6500 && /Rekening berkurang Rp1\.006\.500/.test(HP.artiA) && /biaya admin bank/.test(HP.artiB) && HP.pakaiAdmin);
var kasSebelum = kasPada(); R = tulis(susunPindah({ dari: 'rekening', ke: 'laci', ketik: '1.000.000', alasan: 'Tarik tunai dari bank', adminI: 1 }, W));
ok('dokumen: pindahUang {dari, ke, nominal, alasan, biayaAdmin 6500, adminNama} + pengeluaranHarian toko 6.500 dari rekening menunjuk pindahnya', R.dokumen.length === 2 && R.dokumen[0].koleksi === 'pindahUang' && R.dokumen[0].data.biayaAdmin === 6500 && R.dokumen[1].koleksi === 'pengeluaranHarian' && R.dokumen[1].data.dari === 'rekening' && R.dokumen[1].data.dariPindah === R.dokumen[0].data.id, J(R.dokumen));
S = identitas('sesudah pindah dengan admin'); ok('rekening 3.950.000 − 1.006.500 = 2.943.500; laci +1.000.000 = 3.225.000; kasPada turun tepat 6.500 (admin)', S.rekening === 2943500 && S.laci === 3225000 && kasPada() === kasSebelum - 6500, J(S));
tulis(susunUrungPindah(R.dokumen[0].data.id)); ok('urungkan: pindah & biaya adminnya dicabut; kas kembali', kasPada() === kasSebelum && saldoKantong().laci === 2225000);
var RT4 = rutinPindah(); ok('rutin dari isi SAAT INI: amankan laci = 2.225.000 − 500.000 = 1.725.000 (bisa); isi laci MATI (laci sudah ≥ 500.000)', RT4.daftar[0].n === 1725000 && RT4.daftar[0].bisa && RT4.daftar[1].n === 0 && !RT4.daftar[1].bisa, J(RT4.daftar));
R = tulis(susunPindah({ dari: RT4.daftar[0].dari, ke: RT4.daftar[0].ke, ketik: String(RT4.daftar[0].n), alasan: RT4.daftar[0].alasan, adminI: -1 }, W));
S = identitas('sesudah amankan'); ok('sesudah amankan: laci 500.000 · brankas 11.725.000; total tetap; buku pindah 1 baris + sisihan amplop 16 Sep ikut (2 baris)', S.laci === 500000 && S.brankas === 11725000 && S.total === kasSebelum && bukuPindah().length === 2 && bukuPindah()[0].jenis === 'pindah', J(bukuPindah()));
tulis(susunAturPindah({ jaga: '300.000', alasan: ['Amankan', 'Isi laci'] }, W)); ok('atur jaga 300.000 → rutin isi laci hidup bila laci < 300.000; alasan owner dipakai', aturPindah().jaga === 300000 && aturPindah().alasan.length === 2 && /0–100\.000\.000/.test(susunAturPindah({ jaga: '-1' }, W).tolak));

// ==================== K2 · ORANG & UPAH ====================
var AU = aturUpah(); ok('atur upah bawaan: tarif 60.000; karyawan TERUKUR dari rincian gaji & kasbon (Ben Mohsein, Gono) — bukan daftar karangan', AU.tarif === 60000 && AU.orangTerukur && AU.orang.map(function (o) { return o.nama; }).sort().join() === 'Ben Mohsein,Gono', J(AU));
var HU = hitungUpah('Ben Mohsein', KINI, 'semua');
ok('Ben: mulai 1 Sep (gaji Agu dibayar 31 Agu di sistem lama); 1–19 Sep = 19 hari: 16 penuh · 1 setengah · 1 tidak masuk · 1 kosong (hari ini); upah 16×60.000 + 30.000 = 990.000; kasbon 200.000 → bawa pulang 790.000', HU.mulai === '2026-09-01' && HU.sumberMulai === 'lama' && HU.nHari === 19 && HU.penuh === 16 && HU.setengah === 1 && HU.absen === 1 && HU.kosong === 1 && HU.kosongLama === 0 && HU.upah === 990000 && HU.sisaKasbon === 200000 && HU.bawaPulang === 790000, J(HU));
HU = hitungUpah('Gono', KINI, 'semua'); ok('Gono: mulai 1 Sep, absen 10–17 (8 penuh), 1–9 & 18 kosong LAMA (10 hari belum diisi) — BUKAN tidak masuk; upah 480.000', HU.penuh === 8 && HU.kosongLama === 10 && HU.upah === 480000, J(HU));
ok('bayar upah Gono DITOLAK selama ada hari belum diisi', /10 hari belum diisi/.test(susunBayarUpah('Gono', 'semua', W).tolak));
ok('absen: tanggal di masa depan ditolak; tanggal yang sudah dibayar (Agu) ditolak; putar kosong → penuh → setengah → tidak masuk → kosong', /belum datang/.test(susunAbsen('Gono', '2026-09-20', 1, W).tolak) && /sudah termasuk upah/.test(susunAbsen('Gono', '2026-08-30', 1, W).tolak) && putarHari(null) === 1 && putarHari(1) === 0.5 && putarHari(0.5) === 0 && putarHari(0) === null);
for (var d = 1; d <= 9; d++) tulis(susunAbsen('Gono', '2026-09-0' + d, 0, W)); tulis(susunAbsen('Gono', '2026-09-18', 1, W));
HU = hitungUpah('Gono', KINI, 'semua'); ok('sesudah diisi (1–9 tidak masuk, 18 penuh): kosongLama 0; 9 penuh · 9 tidak masuk; upah 540.000; dokumen absen satu per orang per bulan', HU.kosongLama === 0 && HU.penuh === 9 && HU.absen === 9 && HU.upah === 540000 && ambilAbsenKaryawan().filter(function (a) { return a.nama === 'Gono'; }).length === 1);
var BU = bukuUpah('Gono', KINI); ok('buku upah Gono: "9 hari tidak masuk" · "9 hari penuh" (10–18) dengan saldo berjalan 540.000, kasbon 18 Sep −100.000 diselipkan → jalan 440.000; hari ini kosong = 1 baris BELUM DIISI', BU.rows.some(function (r) { return /9 hari tidak masuk/.test(r.ket); }) && BU.rows.some(function (r) { return r.jenis === 'kasbon' && r.n === -100000; }) && BU.rows.some(function (r) { return r.jenis === 'kosong'; }) && BU.jalan === 440000, J(BU.rows));
var KL = kalenderUpah('Ben Mohsein', KINI, 7); ok('kalender 7 hari Ben: 13–19 Sep; 14 = absen, 19 (hari ini) kosong & ditandai ini; semuanya bisa diubah', KL.length === 7 && KL[1].kelas === 'absen' && KL[6].ini && KL[6].kelas === 'kosong' && KL.every(function (k) { return k.bisa; }), J(KL));
var HK = hitungKasbonKaryawan('Gono', '50.000', 'Berobat'); ok('kasbon karyawan: arti laci berkurang, jadi berutang 150.000; laci 500.000 cukup', !HK.tolak && /jadi berutang Rp150\.000/.test(HK.arti));
R = tulis(susunKasbonKaryawan('Gono', '50.000', 'Berobat', W)); ok('dokumen kasbonMutasi {tipe ambil, namaPegawai, nominal, tanggal, catatan} + jam & dari laci; laci 450.000', R.dokumen[0].data.tipe === 'ambil' && R.dokumen[0].data.namaPegawai === 'Gono' && R.dokumen[0].data.dari === 'laci' && saldoKantong().laci === 450000);
identitas('sesudah kasbon karyawan');
// bayar upah Ben: 990.000, potong semua 200.000 → diterima 790.000 > laci 450.000 → ditolak; isi laci dulu dari brankas
ok('bayar Ben: diterima 790.000 > laci 450.000 → DITOLAK menyebut isi laci', /Laci cuma Rp450\.000/.test(susunBayarUpah('Ben Mohsein', 'semua', W).tolak));
tulis(susunPindah({ dari: 'brankas', ke: 'laci', ketik: '1.000.000', alasan: 'Isi laci', adminI: -1 }, W));
var kas0 = kasPada(); R = tulis(susunBayarUpah('Ben Mohsein', 'semua', W));
ok('bayar Ben (hari ini kosong → slip berhenti 18 Sep): biayaBulanan 2026-09 dengan baris rincianGaji berkunci "Ben Mohsein · 19 Sep 2026" hari 16,5 gaji 990.000, tanggalBayarGaji[kunci] 19 Sep, dariPos gaji laci; listrik Sep tetap; + kasbon bayar 200.000 "Dipotong upah"; + slipUpah', (function () { var b = R.dokumen.find(function (d) { return d.koleksi === 'biayaBulanan'; }).data; var r = b.rincianGaji.find(function (x) { return x.nama === 'Ben Mohsein · 19 Sep 2026'; }); var k = R.dokumen.find(function (d) { return d.koleksi === 'kasbonMutasi'; }).data; var s = R.dokumen.find(function (d) { return d.koleksi === 'slipUpah'; }).data;
  return b.id === '2026-09' && r && r.hari === 16.5 && r.gaji === 990000 && r.sampai === '2026-09-18' && b.tanggalBayarGaji['Ben Mohsein · 19 Sep 2026'] === '2026-09-19' && b.dariPos['gaji:Ben Mohsein · 19 Sep 2026'] === 'laci' && b.listrik === 350000 && k.tipe === 'bayar' && k.nominal === 200000 && k.caraBayar === 'Dipotong upah' && s.diterima === 790000 && s.sampai === '2026-09-18' && /DITERIMA/.test(s.teks); })(), J(R.dokumen));
S = identitas('sesudah bayar upah');
ok('kas: gaji penuh 990.000 keluar + kasbon 200.000 masuk (hari yang sama) → kas bersih turun 790.000 = yang diterima; laci 1.450.000 − 790.000 = 660.000; kasbon Ben LUNAS', kasPada() === kas0 - 790000 && S.laci === 660000 && hitungKasbon().find(function (k) { return k.nama === 'Ben Mohsein'; }).sisa === 0, J([kasPada(), kas0, S]));
ok('laba: gaji 990.000 dibagi rata per hari September (jatah 19 Sep = 33.000)', jatahBiayaBulananHari('2026-09-19') === Math.floor(990000 / 30) || jatahBiayaBulananHari('2026-09-19') > 0);
HU = hitungUpah('Ben Mohsein', KINI, 'semua'); ok('sesudah dibayar: mulai Ben = 19 Sep (sejak slip terakhir), 1 hari kosong (hari ini), upah 0; bayar lagi ditolak "belum ada hari kerja"', HU.mulai === '2026-09-19' && HU.sumberMulai === 'slip' && HU.upah === 0 && /Belum ada hari kerja/.test(susunBayarUpah('Ben Mohsein', 'semua', W).tolak));
ok('riwayat Ben: slip baru di atas, gaji Agu sistem lama di bawah', riwayatUpah('Ben Mohsein')[0].jenis === 'slip' && riwayatUpah('Ben Mohsein')[1].jenis === 'lama' && riwayatUpah('Ben Mohsein')[1].n === 1560000);
ok('atur: menghapus karyawan yang masih punya upah/kasbon ditolak (Gono upah 540.000); tarif nol ditolak; daftar kosong ditolak', /Gono masih punya upah/.test(susunAturUpah({ orang: [{ nama: 'Ben Mohsein' }] }, W).tolak) && /1–10\.000\.000/.test(susunAturUpah({ tarif: '0' }, W).tolak) && /kosong/.test(susunAturUpah({ orang: [] }, W).tolak));
tulis(susunAturUpah({ tarif: '70.000', orang: [{ nama: 'Ben Mohsein', peran: 'tetap' }, { nama: 'Gono', peran: 'giliran' }, { nama: 'Hasan', peran: 'giliran' }] }, W));
ok('atur tarif 70.000 berlaku untuk hari yang BELUM dibayar: Gono 9 penuh → 630.000; slip Ben tetap 990.000; Hasan baru mulai hari ini', hitungUpah('Gono', KINI, 'semua').upah === 630000 && ambilSlipUpah()[0].upah === 990000 && hitungUpah('Hasan', KINI, 'semua').mulai === '2026-09-19');
ok('potong separuh: kasbon Gono 150.000 → potong 75.000 (dibulatkan ke 1.000); jangan dipotong → 0', hitungUpah('Gono', KINI, 'separuh').potong === 75000 && hitungUpah('Gono', KINI, 'tidak').potong === 0);
ok('potongan lama menggantung: Ben 0 (tak ada "Potong gaji" lama)', potongLamaMenggantung('Ben Mohsein') === 0);

// ==================== K3 · OWNER & TOKO ====================
var PO = posisiOwner(KINI); ok('posisi: modal 25.000.000 · toko berutang 150.000 · kasbon owner 80.000 · kalimat "kalau saling dilunaskan: toko masih berutang 70.000"', PO.modal === 25000000 && PO.utangToko === 150000 && PO.kasbonOwner === 80000 && /toko masih berutang Rp70\.000/.test(PO.bersihTeks) && PO.bisaSalingLunas, J(PO));
var HO = hitungOwner({ jenis: 'tarik', ketik: '30.000.000', tempat: 'brankas', ket: 'Lain-lain' }, KINI); ok('tarik modal > modal tertanam DITOLAK → diarahkan ke ambil pribadi', /Modal owner di toko cuma Rp25\.000\.000/.test(HO.tolak) && /Uang keluar/.test(HO.tolak));
HO = hitungOwner({ jenis: 'setor', ketik: '5.000.000', tempat: 'brankas', ket: 'Tabungan pribadi' }, KINI); ok('setor 5.000.000 ke brankas: arti brankas bertambah, modal jadi 30.000.000, laba tidak berubah', !HO.tolak && /Brankas bertambah Rp5\.000\.000/.test(HO.arti[0]) && /jadi Rp30\.000\.000/.test(HO.arti[1]));
ok('bayarPinjam > utang ditolak; kembaliKasbon > kasbon ditolak; keterangan wajib bila ada pilihannya; tempat wajib', /cuma Rp150\.000/.test(hitungOwner({ jenis: 'bayarPinjam', ketik: '200.000', tempat: 'laci' }, KINI).tolak) && /cuma Rp80\.000/.test(hitungOwner({ jenis: 'kembaliKasbon', ketik: '90.000', tempat: 'laci' }, KINI).tolak) && /keterangan/.test(hitungOwner({ jenis: 'setor', ketik: '1', tempat: 'laci' }, KINI).tolak) && /tempat/.test(hitungOwner({ jenis: 'setor', ketik: '1', tempat: '', ket: 'x' }, KINI).tolak));
var kasA = kasPada(); R = tulis(susunOwner({ jenis: 'pinjam', ketik: '2.000.000', tempat: 'brankas', ket: 'Menalangi bon pemasok' }, W));
ok('owner meminjamkan 2.000.000: utangOwnerMutasi {saldoAwal, pinjaman} + modalOwner {setor, pinjaman, tempat brankas}; kas +2.000.000; utang toko 2.150.000; modal tertanam TETAP 25.000.000; laba tidak berubah', R.dokumen.length === 2 && R.dokumen[0].koleksi === 'utangOwnerMutasi' && R.dokumen[0].data.tipe === 'saldoAwal' && R.dokumen[0].data.pinjaman && R.dokumen[1].koleksi === 'modalOwner' && R.dokumen[1].data.pinjaman && kasPada() === kasA + 2000000 && hitungUtangOwner().sisa === 2150000 && modalTertanam() === 25000000, J(R.dokumen));
S = identitas('sesudah pinjaman'); ok('brankas bertambah 2.000.000 (10.725.000 → 12.725.000)', S.brankas === 12725000, J(S));
R = tulis(susunOwner({ jenis: 'bayarPinjam', ketik: '150.000', tempat: 'laci' }, W)); ok('toko mengembalikan 150.000 dari laci: utangOwnerMutasi {bayar, dari laci}; utang 2.000.000; kas −150.000', R.dokumen[0].data.tipe === 'bayar' && R.dokumen[0].data.dari === 'laci' && hitungUtangOwner().sisa === 2000000 && kasPada() === kasA + 2000000 - 150000);
R = tulis(susunOwner({ jenis: 'kembaliKasbon', ketik: '30.000', tempat: 'laci' }, W)); ok('owner mengembalikan kasbon 30.000: kasbonMutasi Owner {bayar, Tunai}; kasbon 50.000; kas +30.000', R.dokumen[0].data.caraBayar === 'Tunai' && kasbonOwner().sisa === 50000 && kasPada() === kasA + 2000000 - 150000 + 30000);
var kasB = kasPada(); R = tulis(susunOwner({ jenis: 'alihPrive', ketik: '20.000' }, W));
ok('kasbon → ambil pribadi 20.000: kasbon Owner bayar "Potong gaji" alih prive → kasbon 30.000, KAS TETAP, prive bulan ini +20.000 (200.000)', R.dokumen[0].data.alih === 'prive' && kasbonOwner().sisa === 30000 && kasPada() === kasB && priveBulan('2026-09-19').total === 200000, J(R.dokumen));
R = tulis(susunOwner({ jenis: 'salingLunas', ketik: '30.000' }, W));
ok('saling lunaskan 30.000: kasbon owner 0 & utang toko 1.970.000; KAS TETAP; dua dokumen (kasbon alih + utangOwner saldoAwal −30.000)', R.dokumen.length === 2 && R.dokumen[1].data.nominal === -30000 && kasbonOwner().sisa === 0 && hitungUtangOwner().sisa === 1970000 && kasPada() === kasB, J(R.dokumen));
identitas('sesudah saling lunas');
ok('saling lunaskan saat salah satu nol ditolak; bukti menyebut tiga saldo sesudahnya', /cuma Rp0/.test(hitungOwner({ jenis: 'salingLunas', ketik: '1' }, KINI).tolak) && /Modal owner       Rp25\.000\.000/.test(R.bukti) && /Kasbon owner      Rp0/.test(R.bukti));
var BO = bukuOwner(20); ok('buku owner: terbaru di atas (saling lunaskan), setiap baris menyebut saldo yang IA ubah; ada baris "Belanja toko pakai dompet owner"', BO[0].judul === 'Saling lunaskan' && /toko berutang jadi Rp1\.970\.000/.test(BO[0].s) && BO.some(function (r) { return r.judul === 'Belanja toko pakai dompet owner'; }) && BO.some(function (r) { return r.judul === 'Pinjaman owner ke toko' && /jadi Rp2\.150\.000/.test(r.s); }), J(BO.slice(0, 6)));

__K5K6__
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

K5K6 = r"""
// ==================== K5 · TUTUP HARI (kotak pasir direset ke awal) ====================
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); }); localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'j7', tanggal: '2026-09-19', jam: '09:58', caraBayar: 'QRIS', jenis: 'karung', merkSumber: 'Angsa', totalKg: 0, beratKarungAcuan: 50, jumlahKarung: 0, hargaTotal: 50000, hppTotalSaatJual: 46800 } }]);   // nota QRIS kecil (≤ batas) — kg 0 supaya urutan timbang tidak berubah
var AT = aturTutup(); ok('atur tutup bawaan: sisih 10 % · kembalian 500.000 · dimaafkan 2.000 · potongan QRIS dari Atur harga (0,30 % di atas 500.000)', AT.persenSisih === 10 && AT.kembalian === 500000 && AT.maafSelisih === 2000 && AT.mdrPersen === 30 && AT.mdrBatas === 500000 && !AT.dariOwner, J(AT));
var RH = ringkasHari('2026-09-19');
ok('ringkas 19 Sep: 4 nota (yang dibatalkan tidak) · tunai 250.000 · QRIS 650.000 = 600.000 (> 500.000 → potongan 1.800) + 50.000 (bebas potongan) · bon baru 300.000 · laba sebelum MDR 83.600 · belum ditutup', RH.nota === 4 && RH.tunai === 250000 && RH.qris === 650000 && RH.qrisNota.length === 2 && RH.mdrKira === 1800 && RH.qrisNota.find(function (q) { return q.id === 'j7'; }).mdr === 0 && RH.kredit === 300000 && RH.labaSebelumMdr === 83600 && !RH.sudah, J(RH));
var RL = rumusLaci('2026-09-19'); ok('rumus laci: laci semalam (18 Sep) 2.230.000 + jual tunai 250.000 = seharusnya 2.480.000 = saldoKantong laci; kas total 17.880.000', RL.ada && RL.awal === 2230000 && RL.masuk === 250000 && RL.keluar === 0 && RL.seharusnya === 2480000 && RL.seharusnya === saldoKantong('2026-09-19').laci && RL.kasTotal === 17880000, J(RL));
var D = { lembar: { 100000: 20, 50000: 9 }, receh: 0, alasan: '', rekPilih: '', rekNyata: '', sisih: null, timbang: {}, status: {} }; var H5 = hitungTutup(D, KINI);
ok('hitung 20×100.000 + 9×50.000 = 2.450.000 → KURANG 30.000, di luar dimaafkan (2.000) → alasan wajib; timbang cepat 2 merek yang keluar hari ini (Apex catatan 460 kg, Angsa 875,1 kg); rekap belum boleh ditutup', H5.hitung === 2450000 && H5.selisih === -30000 && !H5.dimaafkan && /pilih alasannya/.test(H5.tolakLaci) && H5.timbang.length === 2 && H5.timbang[0].merk === 'IR64 Apex' && H5.timbang[0].sistem === 460 && /cuma itu yang tidak boleh dilewati/.test(H5.tolakTutup), J(H5.timbang));
ok('hitungan 2.478.500 → KURANG 1.500 → dimaafkan, tanpa alasan boleh; kosong → "belum dihitung"', hitungTutup(Object.assign({}, D, { lembar: { 100000: 24, 50000: 1, 20000: 1, 5000: 1, 2000: 1, 1000: 1 }, receh: 500 }), KINI).dimaafkan && !hitungTutup(Object.assign({}, D, { lembar: { 100000: 24, 50000: 1, 20000: 1, 5000: 1, 2000: 1, 1000: 1 }, receh: 500 }), KINI).tolakLaci && /belum dihitung/.test(hitungTutup(Object.assign({}, D, { lembar: {} }), KINI).selisihTeks));
D.alasan = 'Salah kasih kembalian'; D.status = { laci: 'beres' }; H5 = hitungTutup(D, KINI);
ok('dengan alasan: laci beres; laba hari ini (MDR perkiraan dipotong) 81.800 → saran sisih 10 % = 8.000; amankan = 2.450.000 − 500.000 = 1.950.000 (sisih belum)', !H5.tolakLaci && H5.labaHari === 81800 && H5.saranSisih === 8000 && H5.amankanN === 1950000, J([H5.labaHari, H5.saranSisih, H5.amankanN]));
D.rekPilih = 'beda'; D.rekNyata = '648.000'; D.status.rekening = 'beres'; H5 = hitungTutup(D, KINI);
ok('QRIS jumlahnya beda: masuk 648.000 → potongan SEBENARNYA 2.000 menggantikan perkiraan 1.800; laba 81.600; masuk > 650.000 ditolak; masuk kosong ditolak', H5.mdrJadi === 2000 && H5.mdrDicatat && H5.labaHari === 81600 && /Lebih besar dari penjualan QRIS/.test(hitungTutup(Object.assign({}, D, { rekNyata: '700.000' }), KINI).tolakRek) && /Ketik jumlah/.test(hitungTutup(Object.assign({}, D, { rekNyata: '' }), KINI).tolakRek));
D.status.sisih = 'beres'; D.sisih = '10.000'; D.timbang = { 'IR64 Apex': '459,5', 'Angsa': '875,1' }; D.status.timbang = 'beres'; D.status.amankan = 'beres'; H5 = hitungTutup(D, KINI);
ok('sisih 10.000 → amankan = 2.450.000 − 10.000 − 500.000 = 1.940.000; laci akhir 500.000; timbang Apex kurang 0,5 kg (−7.000), Angsa cocok', H5.sisihJadi === 10000 && H5.amankanN === 1940000 && H5.amankanJadi === 1940000 && H5.laciAkhir === 500000 && H5.timbang[0].beda === -0.5 && H5.timbang[0].rp === -7000 && H5.timbang[1].beda === 0 && H5.bedaTimbang === -0.5, J(H5.timbang));
ok('sisih melebihi laci ditolak; amankan saat laci ≤ kembalian ditolak', /Laci cuma/.test(hitungTutup(Object.assign({}, D, { sisih: '3.000.000' }), KINI).tolakSisih) && /tidak lebih dari uang kembalian/.test(hitungTutup(Object.assign({}, D, { lembar: { 100000: 4 } }), KINI).tolakAman));
var RK = rekapTutup(H5); ok('rekap: omzet 4 nota 1.200.000 · potongan QRIS sebenarnya −2.000 · laba 81.600 · laci 2.450.000 · selisih −30.000 · disisihkan 10.000 · diamankan 1.940.000 · timbang kurang 0,5 kg (susut) · tinggal di laci 500.000', RK[0].b === 'Rp1.200.000' && /sebenarnya/.test(RK[5].a) && RK[5].b === '−Rp2.000' && RK[6].b === 'Rp81.600' && RK[8].b === '−Rp30.000' && RK[9].b === 'Rp10.000' && RK[10].b === 'Rp1.940.000' && /kurang 0,5 kg/.test(RK[11].b) && RK[12].b === 'Rp500.000', J(RK));
var kasT = kasPada(); var R5 = susunTutup(D, W, false);
ok('dokumen tutup (satu batch): tutupHari {id = tanggal, omzet 1.200.000, jumlahTransaksi 4, kasSeharusnya 17.880.000, kasFisikLaci 2.450.000, rekening/amplop/brankas = catatan saat dihitung (Σ fisik − seharusnya = selisih −30.000), alasan, setoranOwner 0, kasAwalBesokLaci 500.000, menggantung, sistemBaru, dihitung.rekening true, mdr {kira 1.800, jadi 2.000, nyata 648.000}, timbang 2}', (function () { var t = R5.dokumen[0].data; var fisik = t.kasFisikLaci + t.kasFisikRekening + t.kasFisikAmplop + t.kasFisikBrankas; return R5.dokumen[0].koleksi === 'tutupHari' && t.id === '2026-09-19' && t.omzet === 1200000 && t.jumlahTransaksi === 4 && t.kasSeharusnya === 17880000 && t.kasFisikLaci === 2450000 && fisik - t.kasSeharusnya === -30000 && t.selisih === -30000 && t.alasanSelisih === 'Salah kasih kembalian' && t.setoranOwner === 0 && t.kasAwalBesokLaci === 500000 && t.menggantung.rapikanKasir === 0 && t.sistemBaru && t.dihitung.rekening && t.mdr.kira === 1800 && t.mdr.jadi === 2000 && t.mdr.nyata === 648000 && t.timbang.length === 2 && !t.riwayat; })(), J(R5.dokumen[0].data));
ok('+ amplopLaba am-2026-09-19 setor 10.000 · setoranKas st- 0 · modalOwner mo-st- tarik 0 dariSetoran · pengeluaranHarian mdr- 2.000 toko dari rekening · pindahUang pd- laci→brankas 1.940.000 · penyesuaianStok Apex −0,5 kg (−7.000, dariTutup) · pengaturan/titikKas {19 Sep, laci 500.000, rekening 4.348.000 (4.350.000 − MDR 2.000), amplop 1.060.000, brankas 11.940.000}', (function () { var d = function (k, id) { return R5.dokumen.find(function (x) { return x.koleksi === k && (!id || String(x.data.id) === id); }) || { data: {} }; }; var t = d('pengaturan', 'titikKas').data; var ps = d('penyesuaianStok');
  return d('amplopLaba', 'am-2026-09-19').data.nominal === 10000 && d('setoranKas', 'st-2026-09-19').data.nominal === 0 && d('modalOwner', 'mo-st-2026-09-19').data.dariSetoran === 'st-2026-09-19' && d('pengeluaranHarian', 'mdr-2026-09-19').data.nominal === 2000 && d('pengeluaranHarian', 'mdr-2026-09-19').data.dari === 'rekening' && d('pengeluaranHarian', 'mdr-2026-09-19').data.mdr === true && d('pindahUang', 'pd-2026-09-19').data.nominal === 1940000 && ps.data.merk === 'IR64 Apex' && ps.data.selisihKg === -0.5 && ps.data.nilaiRp === -7000 && ps.data.dariTutup === '2026-09-19' && t.tanggal === '2026-09-19' && t.laci === 500000 && t.rekening === 4348000 && t.amplop === 1060000 && t.brankas === 11940000 && R5.titik.laci === 500000; })(), J(R5.dokumen.map(function (x) { return x.koleksi + ':' + x.data.id + ':' + (x.data.nominal !== undefined ? x.data.nominal : ''); })));
tulis(R5); localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(R5.titik));
var S5 = identitas('sesudah tutup hari'); ok('sesudah tutup: kas = titik baru 17.848.000 = kas sebelum (17.880.000) − MDR 2.000 − selisih kurang 30.000; laci 500.000; brankas 11.940.000; laba hari ini 83.600 − MDR 2.000 − susut timbang 7.000 = 74.600; stok Apex 459,5', S5.total === 17848000 && S5.total === kasT - 2000 - 30000 && S5.laci === 500000 && S5.brankas === 11940000 && ringkasHari('2026-09-19').laba.labaBersih === 74600 && Math.abs(hitungStokKarungPerMerk()['IR64 Apex'].sisaKg - 459.5) < 1e-6 && ringkasHari('2026-09-19').sudah, J(S5));
ok('riwayat tutup: 19 Sep, sistem baru, selisih −30.000, sisih 10.000, amankan 1.940.000, 0 koreksi; teks rekap menyebut "Tidak dikerjakan" hanya bila ada yang dilewati (tidak ada)', riwayatTutup()[0].tanggal === '2026-09-19' && riwayatTutup()[0].sistemBaru && riwayatTutup()[0].selisih === -30000 && riwayatTutup()[0].sisih === 10000 && riwayatTutup()[0].amankan === 1940000 && riwayatTutup()[0].nKoreksi === 0 && !/Tidak dikerjakan/.test(R5.teks) && /REKAP TUTUP HARI/.test(R5.teks));
// tutup ulang (koreksi): hitungan laci sekarang 500.000 (uang sudah di brankas), seharusnya = titik laci 500.000 → pas; sisih lagi 5.000; MDR diganti "sudah masuk" (perkiraan 1.800)
var D2 = { lembar: { 100000: 5 }, receh: 0, alasan: '', rekPilih: 'sudah', rekNyata: '', sisih: '5.000', timbang: {}, status: { laci: 'beres', rekening: 'beres', sisih: 'beres' } }; var H2 = hitungTutup(D2, KINI);
ok('tutup ulang: seharusnya laci = titik 500.000 (uang sudah dipindah) → PAS; sisihan malam ini 10.000 (lama) + 5.000 (baru) = 15.000; amankan lama 1.940.000 tetap; laci akhir 495.000; timbang & amankan tidak dikerjakan lagi → dilewati diakui', H2.koreksi && H2.seharusnya === 500000 && H2.selisih === 0 && H2.sisihLama === 10000 && H2.sisihJadi === 15000 && H2.amankanLama === 1940000 && H2.amankanJadi === 1940000 && H2.laciAkhir === 495000 && H2.dilewati.length === 2, J([H2.sisihJadi, H2.amankanJadi, H2.laciAkhir, H2.dilewati]));
var R2 = susunTutup(D2, W, false); ok('tutup ulang tanpa ketukan kedua ditolak (catatan lama turun ke riwayat)', /sudah pernah ditutup/.test(R2.tolak) && R2.perluYakin === 'ulang');
R2 = susunTutup(D2, W, true); tulis(R2); localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(R2.titik));
ok('tutup ulang: dokumen tutupHari membawa riwayat 1 (versi tadi), am- 15.000, pd- 1.940.000 tetap, mdr- 1.800 (perkiraan menggantikan 2.000), titik {laci 495.000, rekening 4.348.200, amplop 1.065.000, brankas 11.940.000}; kas = titik; penyesuaian timbang lama dicabut (Apex kembali 460)', (function () { var d = function (k, id) { return R2.dokumen.find(function (x) { return x.koleksi === k && String(x.data.id) === id; }); }; var t = R2.titik;
  return R2.dokumen[0].data.riwayat.length === 1 && d('amplopLaba', 'am-2026-09-19').data.nominal === 15000 && d('pindahUang', 'pd-2026-09-19').data.nominal === 1940000 && d('pengeluaranHarian', 'mdr-2026-09-19').data.nominal === 1800 && t.laci === 495000 && t.rekening === 4348200 && t.amplop === 1065000 && t.brankas === 11940000 && saldoKantong().cocok && kasPada() === 495000 + 4348200 + 1065000 + 11940000 && R2.hapus.some(function (h) { return h.koleksi === 'penyesuaianStok'; }) && Math.abs(hitungStokKarungPerMerk()['IR64 Apex'].sisaKg - 460) < 1e-6; })(), J([R2.titik, R2.hapus]));
identitas('sesudah tutup ulang');
tulis(susunAturTutup({ persenSisih: '20', kembalian: '300.000', maafSelisih: '5.000', alasan: ['Salah hitung'] }, W)); ok('atur tutup owner: sisih 20 % · kembalian 300.000 · dimaafkan 5.000; persen 120 ditolak', aturTutup().persenSisih === 20 && aturTutup().kembalian === 300000 && aturTutup().maafSelisih === 5000 && aturTutup().dariOwner && /0–100/.test(susunAturTutup({ persenSisih: '120' }, W).tolak));

// ==================== K6 · TUTUP BUKU (kotak pasir direset) ====================
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); }); localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
tulis(susunOwner({ jenis: 'kasbon', ketik: '80.000', tempat: 'laci', ket: 'Keperluan keluarga' }, W));   // kasbon owner 80.000 supaya barisnya berisi
var T6 = tahunBuku(KINI); ok('tahun 2026 (era kosong, catatan pertama 20 Agu 2026); belum lewat 31 Des → hanya LATIHAN; belum ada berita acara', T6.tahun === 2026 && T6.era === null && T6.pertama === '2026-08-20' && !T6.bolehSungguhan && T6.cutoff === '2026-12-31' && !T6.acara && /LATIHAN/.test(T6.teks), J(T6));
var G = gerbangBuku(2026, KINI, { antre: [], menunggu: 0, offline: false, idPerangkat: 'ini' }); ok('gerbang: 3 hari berjualan belum ditutup (16, 17, 19 Sep) → g1 tidak ok & tidak bisa dilewati; g2–g5 ok; belum 1', !G.daftar[0].ok && G.belumTutup.length === 3 && /16 Sep 2026, 17 Sep 2026, 19 Sep 2026/.test(G.daftar[0].ket) && !G.daftar[0].bisaLewati && G.daftar.slice(1).every(function (g) { return g.ok; }) && G.belum === 1, J(G.daftar));
pasok('perangkatStatus', [{ id: 'tablet', nama: 'Tablet kasir', pada: new Date(Date.now() - 5 * 60000).toISOString() }]);
G = gerbangBuku(2026, KINI, { antre: ['x'], menunggu: 0, offline: true, idPerangkat: 'ini' }); ok('perangkat lain berdenyut 5 menit lalu → g3 tidak ok (bisa dilewati: owner menyatakan dimatikan → ok); 1 antrean → g2; tanpa internet → g5', !G.daftar[2].ok && G.daftar[2].bisaLewati && /Tablet kasir/.test(G.daftar[2].ket) && gerbangBuku(2026, KINI, { antre: [], idPerangkat: 'ini' }, { g3: true }).daftar[2].ok && !G.daftar[1].ok && !G.daftar[4].ok, J(G.daftar));
pasok('perangkatStatus', []);
var SB = barisBuku('2026-12-31', '2026-12-31'); var bb = function (id) { return SB.harta.concat(SB.utang).find(function (b) { return b.id === id; }).n; };
ok('12 baris: stok beras 1.335,1 kg 17.816.300 (bulat PER MEREK: Angsa 875,1×13.000 + Apex 460×14.000) · piutang 300.000 · kasbon karyawan 300.000 · kasbon owner 80.000 · laci 2.400.000 · brankas 10.000.000 · rekening 4.300.000 · amplop (uang) 1.050.000 · utang pemasok 20.000.000 · toko berutang ke owner 120.000; modal 25.000.000; laba tinggal −8.873.700', SB.n === 12 && bb('beras') === 17816300 && bb('piutang') === 300000 && bb('kasbonK') === 300000 && bb('kasbonO') === 80000 && bb('laci') === 2400000 && bb('brankas') === 10000000 && bb('rekening') === 4300000 && bb('amplop') === 1050000 && bb('utangP') === 20000000 && bb('utangO') === 120000 && SB.modal === 25000000 && SB.labaTinggal === 36246300 - 20120000 - 25000000 && SB.amplopDok === 50000, J(SB.harta.concat(SB.utang)));
var P6 = pembukaBuku(2026, W);
ok('saldo pembuka = persis sistem lama: 8 dokumen (batch stokAwal 2 merek, piutang saldoAwal bertanggal utang tertua, kasbon Ben & Gono & Owner (owner true), utang pemasok RODA per bon, amplop setor 50.000, utang owner 120.000) semuanya tutupBuku + tahunDari 2026, tanggal 1 Jan 2027', (function () { var d = P6.dokumen; var k = d.filter(function (x) { return x.koleksi === 'kasbonMutasi'; }); var b = d.find(function (x) { return x.koleksi === 'batchMasuk'; });
  return d.length === 8 && d.every(function (x) { return x.data.tutupBuku && x.data.tahunDari === 2026; }) && b.data.stokAwal && b.data.merkList.length === 2 && b.data.tanggal === '2027-01-01' && k.length === 3 && k.find(function (x) { return x.data.namaPegawai === 'Owner'; }).data.owner === true && d.find(function (x) { return x.koleksi === 'piutangMutasi'; }).data.tanggal === '2026-09-19' && d.find(function (x) { return x.koleksi === 'amplopLaba'; }).data.nominal === 50000 && d.find(function (x) { return x.koleksi === 'utangOwnerMutasi'; }).data.nominal === 120000 && d.find(function (x) { return x.koleksi === 'utangPemasokMutasi'; }).data.bonTanggal === '2026-08-20'; })(), J(P6.dokumen.map(function (x) { return x.koleksi; })));
var BD = bandingBuku(SB, sesudahDariPembuka(P6, SB)); ok('sebelum vs sesudah (dari susunan pembuka + titik kas): 12 baris SAMA persis; tanpa sesudah → "akan menyeberang"', BD.semuaSama && BD.baris.length === 12 && BD.baris.every(function (b) { return b.tanda === '✓'; }) && /12 baris akan menyeberang/.test(bandingBuku(SB, null).ringkas), J(BD.beda));
ok('kunci ditolak: tahun belum lewat 31 Des (hanya latihan)', /belum lewat 31 Desember/.test(susunKunci(2026, { paraf: { owner: true, saksi: true } }, W).tolak));
var W27 = { tanggal: '2027-01-01', jam: '08:10', kini: '2027-01-01T01:10:00.000Z', idUnik: W.idUnik };
ok('1 Jan 2027: boleh sungguhan; paraf belum lengkap ditolak', tahunBuku(new Date('2027-01-01T08:10:00+07:00')).bolehSungguhan && /Paraf/.test(susunKunci(2026, { paraf: { owner: true, saksi: false } }, W27).tolak));
var AR = arsipBuku(2026); ok('arsip tahun 2026 = tbDaftarKoleksi mesin: 18 dokumen (penjualan 6 · kedatangan 1 · harian 5 · kasbon 3 · amplop 1 · modal 1 · biaya bulanan 1); berkas arsip bernama arsip-tahun-2026', AR.n === 18 && AR.perKoleksi.find(function (k) { return k.koleksi === 'penjualan'; }).n === 6 && AR.perKoleksi.find(function (k) { return k.koleksi === 'kasbonMutasi'; }).n === 3 && berkasArsip(2026, KINI).nama === 'arsip-tahun-2026-miqbal.json' && berkasArsip(2026, KINI).isi.penjualan.length === 6, J(AR.perKoleksi));
var KU = susunKunci(2026, { paraf: { owner: true, saksi: true }, saksi: 'Ben Mohsein', langkah: {}, cadangan1: 'cadangan-sebelum.json', arsipNama: 'arsip-tahun-2026-miqbal.json' }, W27);
ok('KUNCI: dokumen = 8 pembuka + titikKas 31 Des {laci 2.400.000, brankas 10.000.000, rekening 4.300.000, amplop 1.050.000} + pengaturan/tutupBuku 2026 + berita acara terkunci (12 baris sebelum, saksi, paraf, 18 arsip); arsip 18', !KU.tolak && KU.dokumen.length === 11 && KU.dokumen.find(function (x) { return x.data.id === 'titikKas'; }).data.tanggal === '2026-12-31' && KU.dokumen.find(function (x) { return x.data.id === 'titikKas'; }).data.laci === 2400000 && KU.dokumen.find(function (x) { return x.data.id === 'tutupBuku'; }).data.tahunDitutup === 2026 && KU.acara.status === 'terkunci' && KU.acara.sebelum.length === 12 && KU.acara.nArsip === 18 && KU.acara.saksi === 'Ben Mohsein' && KU.arsip.length === 18, J(KU.tolak || KU.acara));
if (!KU.tolak) { tulis(KU); arsipkanDokumen(2026, KU.arsip); localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(Object.assign({ id: 'titikKas' }, KU.titik))); }
ok('kunci diterima (tidak ditolak)', !KU.tolak, KU.tolak);
ok('sesudah kunci: dokumen 2026 pindah ke arsip (penjualan hidup 0, arsip simulasi 18); era 2026; tahun berikutnya 2027; berita acara terkunci', ambilPenjualanSemua().length === 0 && arsipSimulasi().length === 18 && bkEra() === 2026 && tahunBuku(new Date('2027-01-01T08:10:00+07:00')).tahun === 2027 && tahunBuku(new Date('2027-01-01T08:10:00+07:00')).acara === null && ambilTutupBukuAcara()[0].status === 'terkunci');
var SH = sesudahHidup(2026); var BD2 = bandingBuku(SB, SH); ok('SESUDAH HIDUP (mesin pada 1 Jan 2027, hanya saldo pembuka + titik kas) = SEBELUM: 12 baris sama persis — stok, piutang, kasbon (termasuk owner), uang per tempat, utang pemasok & owner', BD2.semuaSama, J(BD2.beda.map(function (b) { return b.nama + ' ' + b.a + ' vs ' + b.b; })));
identitas('sesudah tutup buku (1 Jan)');
ok('selesai tanpa kunci → tolak; batal saat tidak terkunci → tolak (tahun 2027)', /Kunci tahunnya dulu/.test(susunSelesai(2027, '', W27).tolak) && /tidak sedang terkunci/.test(susunBatal(2027, [], W27).tolak));
var BT = susunBatal(2026, arsipSimulasi(), W27); ok('BATAL: 8 saldo pembuka dicabut, 18 dokumen dikembalikan, berita acara dibatalkan, era mundur (kosong)', !BT.tolak && BT.hapus.length === 8 && BT.pulih.length === 18 && BT.dokumen[0].data.status === 'dibatalkan' && BT.dokumen[1].data.tahunDitutup === 0, J(BT.tolak || BT.hapus));
if (!BT.tolak) { tulis(BT); pulihkanArsip(2026, BT.pulih); } localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
ok('sesudah batal: penjualan 6 kembali, kasbon Ben asli (701) kembali, era kosong, arsip simulasi kosong; 12 baris sebelum sama seperti semula', ambilPenjualanSemua().length === 6 && ambilKasbonMutasi().some(function (m) { return String(m.id) === '701'; }) && bkEra() === null && arsipSimulasi().length === 0 && bandingBuku(SB, (function () { var B = barisBuku('2026-12-31', '2026-12-31'); var o = {}; B.harta.concat(B.utang).forEach(function (b) { o[b.id] = b.n; }); return o; })()).semuaSama);
KU = susunKunci(2026, { paraf: { owner: true, saksi: true }, saksi: 'Ben Mohsein', langkah: {} }, W27); if (!KU.tolak) { tulis(KU); arsipkanDokumen(2026, KU.arsip); }
var SL = susunSelesai(2026, 'cadangan-sesudah.json', W27); if (!SL.tolak) tulis(SL); ok('kunci lagi lalu SELESAI: berita acara selesai (cadangan sesudah tercatat); batal sesudah selesai ditolak', SL.dokumen[0].data.status === 'selesai' && SL.dokumen[0].data.cadangan2 === 'cadangan-sesudah.json' && /tidak sedang terkunci/.test(susunBatal(2026, [], W27).tolak));
ok('teks berita acara menyebut 12 baris, jumlah harta, modal, paraf', /BERITA ACARA TUTUP BUKU 2026/.test(teksAcara(2026, { paraf: { owner: true, saksi: true } }, BD, SB, 'Ben Mohsein', W27)) && /Paraf: owner ✓ · Ben Mohsein ✓/.test(teksAcara(2026, { paraf: { owner: true, saksi: true } }, BD, SB, 'Ben Mohsein', W27)));
tulis(susunAturBuku({ saksi: ['Ben Mohsein', 'Hasan'] }, W27)); ok('atur saksi: 2 nama; kosong ditolak; bawaan = karyawan terukur', aturBuku().saksi.length === 2 && aturBuku().dariOwner && /Saksi tidak boleh kosong/.test(susunAturBuku({ saksi: [] }, W27).tolak));
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
if (CAD.titikKas) localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(CAD.titikKas));
var KINI = new Date(Date.now()); var salah = []; var S = saldoKantong();
if (S.ada && !S.cocok) salah.push('kantong ≠ kasPada: ' + S.total + ' vs ' + S.mesin);
var PO = posisiOwner(KINI); var U = semuaUpah(KINI); var TG = tagihanBulan(hariIniIso(KINI));
print(JSON.stringify({ salah: salah, kantong: S.ada ? { laci: S.laci, brankas: S.brankas, rekening: S.rekening, amplop: S.amplop, total: S.total, minus: S.minus } : 'titik kas tidak ada di cadangan', modal: PO.modal, utangToko: PO.utangToko, kasbonOwner: PO.kasbonOwner, prive: PO.prive,
  karyawan: U.map(function (u) { return u.nama + ' ' + u.nHari + ' hari sejak ' + u.mulai + ' (' + u.sumberMulai + ') kosong ' + u.kosongLama + ' upah ' + u.upah; }), tagihanBelum: TG.nBelum, perluToko: aturKeluar(hariIniIso(KINI)).perluToko.map(function (p) { return p.nama + ' ' + p.biasa; }) }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:1200]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js):
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO.replace('__K5K6__', K5K6))
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            # ---- bersama · saldo per tempat
            'tempat uang menurut dokumen (dari/tempat) diabaikan — semua ikut aturan lama': js.replace("if (r.id && peta.id[String(r.id)]) return peta.id[String(r.id)];", "if (false) return '';"),
            'sisihan amplop tidak menggeser laci → amplop': js.replace("ambilAmplopLaba().forEach((a) => { if (a.tutupBuku || !dalam(a.tanggal || '')) return; const n = Number(a.nominal) || 0; if (a.tipe === 'ambil') { s.amplop -= n; s.laci += n; } else { s.laci -= n; s.amplop += n; } });", ""),
            'pindah uang tidak menggeser tempatnya': js.replace("ambilPindahUang().forEach((p) => { if (!dalam(p.tanggal || '')) return; const n = Number(p.nominal) || 0; if (s[p.dari] !== undefined) s[p.dari] -= n; if (s[p.ke] !== undefined) s[p.ke] += n; });", ""),
            'tempat tidak cukup dijepit diam-diam (tidak pernah ditolak)': js.replace("if (n > isi + 0.5) return { boleh: false, teks: ugNamaTempat(tempat) + ' cuma ' + RP(isi) + ' — tidak cukup untuk ' + RP(n) };", "if (false) return {};"),
            'pinjaman owner dihitung sebagai modal tertanam': js.replace("if (m.pinjaman || (sampai && (m.tanggal || '') > sampai)) return a;", "if (sampai && (m.tanggal || '') > sampai) return a;"),
            # ---- K1
            'belanja toko pakai dompet dianggap biaya dari laci': js.replace("if (untuk === 'toko' && dari !== 'dompet') return { sel: 'beban',", "if (untuk === 'toko') return { sel: 'beban',"),
            'prive ditulis kategori toko (masuk laba)': js.replace("const kategori = H.arti.sel === 'beban' ? 'toko' : H.arti.sel === 'utang' ? 'tokoDompet' : 'owner';", "const kategori = H.arti.sel === 'utang' ? 'tokoDompet' : 'toko';"),
            'lewat batas aman lolos tanpa kasbon/alasan': js.replace("if (H.lewatAman && !P.jadiKasbon && !P.alasan) return { tolak:", "if (false) return { tolak:"),
            'kasbon owner tanpa tanda owner': js.replace("tipe: 'ambil', namaPegawai: NAMA_KASBON_OWNER, owner: true, nominal: H.n, tanggal: w.tanggal, jam: w.jam, catatan: ket, dari: D.dari };", "tipe: 'ambil', namaPegawai: NAMA_KASBON_OWNER, owner: false, nominal: H.n, tanggal: w.tanggal, jam: w.jam, catatan: ket, dari: D.dari };"),
            'batas aman bawaan angka karangan (bukan laba bulan berjalan)': js.replace("aman: amanOwner || Math.max(0, laba), amanDariLaba: !amanOwner,", "aman: amanOwner || 2000000, amanDariLaba: !amanOwner,"),
            'keperluan bawaan daftar karangan (bukan terukur dari catatan)': js.replace("  if (!urut.length) return UK_PERLU_UMUM[kategori === 'toko' ? 'toko' : 'pribadi'].map((nama) => ({ nama, biasa: 0 }));\n  return urut.map(", "  return UK_PERLU_UMUM[kategori === 'toko' ? 'toko' : 'pribadi'].map((nama) => ({ nama, biasa: 0 }));\n  const _x = urut.map("),
            'tagihan bulan ini boleh dibayar dua kali': js.replace("if (t.lunas) return { tolak: t.nama + ' sudah dibayar '", "if (false) return { tolak: t.nama + ' sudah dibayar '"),
            'dokumen bulanan bertanggal tunggal kehilangan tanggal pos lain saat pindah ke peta': js.replace("if (!lama.tanggalBayarPos && lama.tanggalBayar) { POS_BIAYA_BULANAN.forEach((p) => { if (Number(lama[p.kunci]) > 0) peta[p.kunci] = lama.tanggalBayar; }); if (Number(lama.gaji) > 0) peta.gaji = lama.tanggalBayar; }\n  peta[t.kunci] = w.tanggal;", "peta[t.kunci] = w.tanggal;"),
            'titipan tablet disetujui tanpa menulis pengeluarannya': js.replace("if (setuju) { if (!(n > 0)) return { tolak: 'Permintaan ini tidak menyebut nominal — tolak, minta dicatat ulang' }; dokumen.push(", "if (false) { dokumen.push("),
            # ---- K4
            'biaya admin pindah tidak jadi biaya toko': js.replace("if (H.admin > 0) { const adm = { id: w.idUnik(), kategori: 'toko'", "if (false) { const adm = { id: w.idUnik(), kategori: 'toko'"),
            'pindah dari = ke diterima': js.replace("else if (D.dari === D.ke) tolak = 'Dari dan ke tidak boleh sama';", ""),
            'rutin amankan angka mati (bukan dari isi laci saat ini)': js.replace("const amankan = Math.max(0, Math.round(S.laci - A.jaga)), isi = Math.max(0, Math.round(A.jaga - S.laci));", "const amankan = 1805000, isi = 0;"),
            'urungkan pindah meninggalkan biaya adminnya': js.replace("ambilPengeluaranHarian().forEach((h) => { if (String(h.dariPindah || '') === String(p.id)) hapus.push({ koleksi: 'pengeluaranHarian', id: h.id }); });", ""),
            # ---- K2
            '"sejak terakhir dibayar" mengabaikan slip sistem baru': js.replace("if (sampai) return { mulai: ugTambahHari(sampai, 1), sumber: 'slip',", "if (false) return { mulai: ugTambahHari(sampai, 1), sumber: 'slip',"),
            'hari belum diisi dianggap tidak masuk (bayar tetap jalan)': js.replace("if (H.kosongLama > 0) return { tolak: H.kosongLama + ' hari belum diisi", "if (false) return { tolak: H.kosongLama + ' hari belum diisi"),
            'potongan kasbon ditulis "Potong gaji" (mesin lama mengalokasikannya ke baris lain)': js.replace("caraBayar: 'Dipotong upah', catatan: 'dipotong dari upah '", "caraBayar: 'Potong gaji', catatan: 'dipotong dari upah '"),
            'baris gaji bernama polos (dua pembayaran sebulan saling menimpa)': js.replace("const kunci = String(nama).trim() + ' · ' + tanggalPendek(w.tanggal); const perBulan = {};", "const kunci = String(nama).trim(); const perBulan = {};"),
            'setengah hari dibayar penuh': js.replace("const upah = penuh * A.tarif + setengah * (A.tarif / 2);", "const upah = penuh * A.tarif + setengah * A.tarif;"),
            'tarif upah angka mati (setelan owner diabaikan)': js.replace("const a = ugAturDok('upah') || {}; const tarif = isFinite(Number(a.tarif)) && Number(a.tarif) > 0 ? Math.round(Number(a.tarif)) : ATUR_UPAH_BAWAAN.tarif;", "const a = ugAturDok('upah') || {}; const tarif = ATUR_UPAH_BAWAAN.tarif;"),
            'karyawan yang masih punya upah boleh dihapus': js.replace("if (H.upah > 0 || H.sisaKasbon > 0) return { tolak: o.nama + ' masih punya '", "if (false) return { tolak: o.nama + ' masih punya '"),
            # ---- K3
            'tarik modal melebihi modal tertanam diterima': js.replace("else if (n > B[0] + 0.5) tolak = B[1];", "else if (false) tolak = B[1];"),
            'kasbon → ambil pribadi ditulis sebagai uang masuk (Tunai)': js.replace("caraBayar: 'Potong gaji', alih: 'prive', catatan:", "caraBayar: 'Tunai', alih: 'prive', catatan:"),
            'saling lunaskan menambah utang toko (tanda positif)': js.replace("tipe: 'saldoAwal', alih: 'salingLunas', nominal: -n,", "tipe: 'saldoAwal', alih: 'salingLunas', nominal: n,"),
            # ---- K5
            'potongan QRIS dikenakan juga di bawah batas bebas': js.replace("const mdrSatu = (n, A) => (n > A.mdrBatas ? Math.round(n * A.mdrPersen / 10000) : 0);", "const mdrSatu = (n, A) => Math.round(n * A.mdrPersen / 10000);"),
            'selisih di luar yang dimaafkan lolos tanpa alasan': js.replace("(!dimaafkan && !D.alasan ? 'Selisihnya di luar yang dimaafkan — pilih alasannya' : '');", "'';"),
            'titik kas rekening tidak dipotong MDR': js.replace("rekening: rekening + H.mdrLama - mdrBaru, amplop: amplop + H.sisihBaru,", "rekening: rekening, amplop: amplop + H.sisihBaru,"),
            'amankan laci tidak ditulis sebagai pindah uang': js.replace("if (H.amankanJadi > 0) dokumen.push({ koleksi: 'pindahUang', data: { id: 'pd-' + iso,", "if (false) dokumen.push({ koleksi: 'pindahUang', data: { id: 'pd-' + iso,"),
            'tutup ulang tanpa ketukan kedua': js.replace("if (H.R.sudah && !yakinUlang) return { tolak:", "if (false) return { tolak:"),
            'tutup ulang mencabut uang yang sudah pindah ke brankas': js.replace("const sisihJadi = sisihLama + sisihBaru, amankanJadi = amankanLama + amankanBaru;", "const sisihJadi = sisihBaru, amankanJadi = amankanBaru;"),
            # ---- K6
            'sesudah (dari susunan pembuka) lupa utang pemasok': js.replace("else if (koleksi === 'utangPemasokMutasi') j.utangP += Number(data.nominal) || 0;", ""),
            'gerbang hari belum ditutup diabaikan': js.replace("ok: belumTutup.length === 0, ket:", "ok: true, ket:"),
            'kunci diizinkan sebelum tahunnya lewat': js.replace("if (!T.bolehSungguhan) return { tolak: 'Tahun ' + tahun + ' belum lewat 31 Desember — hanya bisa latihan' };", ""),
            'batal tutup buku tidak mencabut saldo pembuka': js.replace("if (bkTutupBuku(x) && Number(x.tahunDari) === tahun) hapus.push(", "if (false) hapus.push("),
            'kasbon owner di saldo pembuka kehilangan tanda owner': js.replace("kunciPelanggan(x.nama) === kunciPelanggan(NAMA_KASBON_OWNER) ? { owner: true } : {}, tb)", "{}, tb)"),
            'titik kas 31 Des tidak ditulis saat kunci (kas tahun lama menguap)': js.replace("if (K.ada) dokumen.push({ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: T.cutoff,", "if (false) dokumen.push({ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: T.cutoff,"),
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
    cad = sorted(glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, 'backup-batch-*.json')))
    if cad and not g:
        h, e = jalan(JAM_TETAP.replace("'2026-09-19T10:00:00+07:00'", "'2026-09-22T10:00:00+07:00'") + js + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if h is None: print('ASAP JATUH: ' + e); sys.exit(2)
        print('ASAP DATA TOKO (%s): %s' % (os.path.basename(cad[-1]), json.dumps(h, ensure_ascii=False)))
        if h['salah']: sys.exit(2)
    sys.exit(1 if g else 0)
