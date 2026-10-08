#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_modal_fifo_baru.py — MODAL FIFO (owner 9 Okt 2026, saklar di tangan owner): baru/js/mesin/modal-fifo.js + mesin beku hitungStokKarungPerMerk
+ titik layar yang menulis modal barang keluar (nota Jual/karcis lewat pecahItemsWadah, adukan, takar ke wadah, cocokkan, karung habis di deretan).
KOTAK PASIR (ANGKA CONTOH, bukan angka toko). Kalau ada backup-batch-*.json lokal: saklar dinyalakan "besok" di atas data toko → nilai rak per merek
TIDAK melompat (sama dengan rata-rata sampai rupiah), dan saklar mati = mesin sama persis dengan tanpa setelan.

    python3 alat-uji/uji_modal_fifo_baru.py            → N lulus · 0 gagal
    python3 alat-uji/uji_modal_fifo_baru.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
from uji_stok_baru import MODUL  # noqa: E402  (data + mesin + layar stok/jual/wadah)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
JAM_TETAP = "var __KINI = new Date('2026-10-05T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"

# A: 1 Sep 100 kg @10.000, 20 Sep 100 kg @12.000, 10 Sep terjual 50 kg → 30 Sep sisa 150 kg, rata-rata 11.000 (lapisan buka saklar 1 Okt).
#    2 Okt datang 100 kg @13.000. 3 Okt terjual 160 kg (dicatat terpisah di skenario) → sisa 90 kg = semuanya kedatangan 2 Okt.
KOTAK = {
  'batchMasuk': [
    {'id': 1, 'tanggal': '2026-09-01', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [{'merk': 'A', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 2, 'totalKg': 100, 'subtotalHarga': 1000000, 'hargaPerKg': 10000}]},
    {'id': 2, 'tanggal': '2026-09-20', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [{'merk': 'A', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 2, 'totalKg': 100, 'subtotalHarga': 1200000, 'hargaPerKg': 12000}]},
    {'id': 3, 'tanggal': '2026-10-02', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [{'merk': 'A', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 2, 'totalKg': 100, 'subtotalHarga': 1300000, 'hargaPerKg': 13000}]},
    {'id': 4, 'tanggal': '2026-09-05', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [{'merk': 'B', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 1, 'totalKg': 50, 'subtotalHarga': 700000, 'hargaPerKg': 14000}]},
    # C: dua kedatangan SESUDAH saklar, id terbalik dari tanggal (urutan = tanggal dulu): 2 Okt @9.000 (id 6), 3 Okt @9.500 (id 5) → keluar berikutnya 9.000
    {'id': 6, 'tanggal': '2026-10-02', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [{'merk': 'C', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 2, 'totalKg': 100, 'subtotalHarga': 900000, 'hargaPerKg': 9000}]},
    {'id': 5, 'tanggal': '2026-10-03', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [{'merk': 'C', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 2, 'totalKg': 100, 'subtotalHarga': 950000, 'hargaPerKg': 9500}]}],
  # takar 2 Okt: 20 kg B → wadah aktif W1 (buku 'Wadah W1', modal 14.000/kg)
  'produksiKemasan': [{'id': 9, 'tanggal': '2026-10-02', 'jam': '08:00', 'merkSumber': 'B', 'namaProduk': 'Wadah W1', 'ukuranKemasan': 20, 'jumlahUnit': 1, 'kgDipakai': 20, 'hppSumberPerKgDipakai': 14000, 'hppPerUnit': 280000,
                       'sumberList': [{'merk': 'B', 'kg': 20}], 'jadiKarungUtuh': True, 'merkTujuan': 'Wadah W1', 'dariTakar': True, 'biayaKemasan': 0, 'upahRepacking': 0}],
  'penjualan': [{'id': 'j1', 'tanggal': '2026-09-10', 'jam': '09:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': 'A', 'totalKg': 50, 'jumlahKarung': 1, 'beratKarungAcuan': 50, 'hargaTotal': 600000, 'hppTotalSaatJual': 500000}],
}
SAKLAR = [{'id': 'catatStok', 'tanggal': '2026-09-30', 'jam': '21:00', 'minKarung': 40, 'tempoHari': 31, 'modalFifoMulai': '2026-10-01'}]

SKENARIO = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
function dekat(a, b) { return Math.abs(a - b) < 0.01; }
__dom['jualKarungBerat'] = { value: '50' };
// ---- 1. hitungan irisan murni
var L = [{ kg: 100, harga: 10000 }, { kg: 50, harga: 12000 }];
ok('irisan: 0–100 kg = 100 × 10.000', mfIrisan(L, 0, 100) === 1000000, mfIrisan(L, 0, 100));
ok('irisan menyeberang lapisan: 90–110 = 10 × 10.000 + 10 × 12.000', mfIrisan(L, 90, 110) === 220000, mfIrisan(L, 90, 110));
ok('irisan sebelum jejeran (retur melebihi yang keluar) dinilai lapisan pertama', mfIrisan(L, -10, 0) === 100000, mfIrisan(L, -10, 0));
ok('irisan sesudah jejeran (stok minus) dinilai lapisan terakhir', mfIrisan(L, 150, 160) === 120000, mfIrisan(L, 150, 160));
ok('irisan terbalik = negatif', mfIrisan(L, 110, 90) === -220000, mfIrisan(L, 110, 90));
ok('harga di posisi: 99,9 → lapisan 1; 100 → lapisan 2; −5 → lapisan 1; 999 → lapisan terakhir', mfHargaDi(L, 99.9) === 10000 && mfHargaDi(L, 100) === 12000 && mfHargaDi(L, -5) === 10000 && mfHargaDi(L, 999) === 12000);
ok('saklar dari dokumen: tanggal sah dibaca, kosong / salah bentuk = mati', mfMulaiDari([{ id: 'catatStok', modalFifoMulai: '2026-10-01' }]) === '2026-10-01' && mfMulaiDari([{ id: 'catatStok', modalFifoMulai: '' }]) === '' && mfMulaiDari([{ id: 'catatStok', modalFifoMulai: '1 Okt' }]) === '' && mfMulaiDari([]) === '');
ok('hari sebelum: 1 Jan 2027 → 31 Des 2026; 1 Mar 2028 → 29 Feb', mfHariSebelum('2027-01-01') === '2026-12-31' && mfHariSebelum('2028-03-01') === '2028-02-29');

// ---- 2. saklar MATI = rata-rata seluruh kedatangan (cara lama)
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var S0 = hitungStokKarungPerMerk();
ok('saklar mati: A sisa 250 kg, modal rata-rata (1,0 + 1,2 + 1,3 jt) / 300 kg = 11.666,67, tanpa lapisan', S0.A.sisaKg === 250 && dekat(S0.A.hppTerakhirPerKg, 3500000 / 300) && S0.A.metode === undefined && S0.A.lapisan === undefined, JSON.stringify(S0.A));
ok('saklar mati: modal keluar = rata-rata (hppKeluar 10 kg = 10 × rata-rata)', dekat(hppKeluar(S0.A, 10), 10 * 3500000 / 300) && hppKeluarPerKg(S0.A) === S0.A.hppTerakhirPerKg);

// ---- 3. saklar NYALA mulai 1 Okt
pasok('aturanToko', SAKLAR);
var S1 = hitungStokKarungPerMerk();
ok('nyala: lapisan = sisa 30 Sep 150 kg @11.000 (rata-rata saat itu) + kedatangan 2 Okt 100 kg @13.000', S1.A.metode === 'fifo' && S1.A.lapisan.length === 2 && S1.A.lapisan[0].kg === 150 && dekat(S1.A.lapisan[0].harga, 11000) && S1.A.lapisan[0].asal === 'buka' && S1.A.lapisan[1].kg === 100 && S1.A.lapisan[1].harga === 13000, JSON.stringify(S1.A.lapisan));
ok('nyala: belum ada yang keluar sejak 1 Okt → depan antrean di 0, nota berikutnya bermodal 11.000/kg', S1.A.posKeluar === 0 && dekat(S1.A.hppKeluarPerKg, 11000), S1.A.posKeluar + ' ' + S1.A.hppKeluarPerKg);
ok('nyala: nilai sisa 250 kg = 150 × 11.000 + 100 × 13.000 = 2.950.000 (hppTerakhirPerKg = nilai per kg sisa)', dekat(S1.A.sisaKg * S1.A.hppTerakhirPerKg, 2950000) && dekat(S1.A.hppRataPerKg, 3500000 / 300), S1.A.sisaKg * S1.A.hppTerakhirPerKg);
ok('nyala: 160 kg berikutnya = 150 × 11.000 + 10 × 13.000 = 1.780.000; kedua kalinya mulai sesudah 100 kg pertama', dekat(hppKeluar(S1.A, 160), 1780000) && dekat(hppKeluar(S1.A, 60, 100), 50 * 11000 + 10 * 13000));
ok('nyala: merek tanpa kedatangan sejak saklar (B) = satu lapisan buka 50 kg @14.000; 20 kg sudah ditakar → sisa 30 kg = 420.000', S1.B.metode === 'fifo' && S1.B.sisaKg === 30 && dekat(S1.B.sisaKg * S1.B.hppTerakhirPerKg, 420000) && dekat(S1.B.hppKeluarPerKg, 14000), JSON.stringify(S1.B));
ok('nyala: dua kedatangan sesudah saklar diurut TANGGAL (bukan id) — keluar berikutnya 2 Okt @9.000', S1.C.metode === 'fifo' && S1.C.lapisan.length === 2 && S1.C.hppKeluarPerKg === 9000 && S1.C.lapisan[0].harga === 9000, JSON.stringify(S1.C.lapisan));
ok('nyala: wadah aktif (Wadah W1) tetap rata-rata — tanpa lapisan (owner: wadah campuran)', S1['Wadah W1'] && S1['Wadah W1'].metode === undefined && dekat(S1['Wadah W1'].hppTerakhirPerKg, 14000), JSON.stringify(S1['Wadah W1']));
var N30 = hitungStokKarungPerMerk('2026-09-30');
ok('buku sampai 30 Sep (sebelum saklar) tetap rata-rata — bulan lalu tidak berubah', N30.A.metode === undefined && dekat(N30.A.hppTerakhirPerKg, 11000) && N30.A.sisaKg === 150, JSON.stringify(N30.A));
var N1 = hitungStokKarungPerMerk('2026-10-01');
ok('buku sampai 1 Okt (hari saklar, belum ada kejadian) = nilai sama dengan 30 Sep: nilai rak tidak melompat', N1.A.metode === 'fifo' && dekat(N1.A.sisaKg * N1.A.hppTerakhirPerKg, 150 * 11000), JSON.stringify(N1.A));

// ---- 4. nota: pecahItemsWadah (dipakai nota Jual & rinci karcis) menulis modal FIFO berurutan; kantong / wadah repack tetap ditambahkan
var it = pecahItemsWadah([{ jenis: 'karung', merkSumber: 'A', totalKg: 100, hargaTotal: 1300000, hppTotalSaatJual: 1 },
  { jenis: 'repacking', merkSumber: 'A', totalKg: 60, hargaTotal: 800000, hppTotalSaatJual: 2, biayaKemasanRepack: 500 },
  { jenis: 'kemasan', namaProduk: 'X', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, hargaTotal: 70000, hppTotalSaatJual: 65000 }], {});
ok('nota: baris 1 (100 kg) = 100 × 11.000; baris 2 (60 kg) = 50 × 11.000 + 10 × 13.000 + wadah Rp500; kemasan tidak disentuh', it[0].hppTotalSaatJual === 1100000 && it[1].hppTotalSaatJual === 680500 && it[2].hppTotalSaatJual === 65000, it.map(function (x) { return x.hppTotalSaatJual; }).join(' · '));
var itW = pecahItemsWadah([{ jenis: 'literan', merkSumber: 'Wadah W1', totalKg: 8.2, hargaTotal: 120000, hppTotalSaatJual: 114800 }], {});
ok('nota: literan wadah aktif (kunci Wadah …) = rata-rata, tidak disentuh FIFO (owner: wadah campuran)', itW[0].hppTotalSaatJual === 114800, itW[0].hppTotalSaatJual);

// ---- 5. adukan: bahan = karung terlama, dua baris merek sama berurutan
var ad = hitungAdukan({ bahan: [{ merk: 'A', kg: 100 }, { merk: 'A', kg: 60 }], hasil: [] });
ok('adukan: bahan 100 kg = 1.100.000; 60 kg berikutnya = 680.000', dekat(ad.bahan[0].nilai, 1100000) && dekat(ad.bahan[1].nilai, 680000) && dekat(ad.bahan[1].hpp, 680000 / 60), ad.bahan.map(function (b) { return b.nilai; }).join(' · '));

// ---- 6. takar ke wadah: modal masuk wadah = karung terlama
var tk = wbDokPindah([{ merk: 'A', kg: 160 }], 'Wadah W1', { tanggal: '2026-10-05', jam: '10:00', idUnik: function () { return 77; } });
ok('takar 160 kg ke wadah: nilai = 1.780.000 (modal per kg 11.125)', dekat(tk.data.hppPerUnit, 1780000) && dekat(tk.data.hppSumberPerKgDipakai, 11125), tk.data.hppPerUnit);

// ---- 7. selisih hitung fisik
ok('susut 10 kg = −10 × 11.000 (karung terlama); lebih 10 kg = +10 × 11.000 (kembali ke depan, sebelum jejeran = lapisan pertama)', dekat(nilaiSelisihKg(S1.A, -10), -110000) && dekat(nilaiSelisihKg(S1.A, 10), 110000));
ok('susut berurutan dalam satu kiriman: 10 kg sesudah 150 kg keluar = 10 × 13.000', dekat(nilaiSelisihKg(S1.A, -10, 150), -130000));

// ---- 8. sesudah 3 Okt terjual 160 kg → sisa 90 kg = semuanya kedatangan 2 Okt
pasok('penjualan', KOTAK.penjualan.concat([{ id: 'j2', tanggal: '2026-10-03', jam: '09:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'A', totalKg: 160, jumlahKarung: 3.2, beratKarungAcuan: 50, hargaTotal: 2100000, hppTotalSaatJual: 1780000 }]));
var S2 = hitungStokKarungPerMerk();
ok('sesudah 160 kg keluar: sisa 90 kg bernilai 90 × 13.000 = 1.170.000, depan antrean di 160, modal berikutnya 13.000', S2.A.sisaKg === 90 && dekat(S2.A.posKeluar, 160) && dekat(S2.A.sisaKg * S2.A.hppTerakhirPerKg, 1170000) && S2.A.hppKeluarPerKg === 13000, JSON.stringify({ s: S2.A.sisaKg, p: S2.A.posKeluar, v: S2.A.hppTerakhirPerKg }));
ok('identitas: modal yang keluar (1.780.000) + nilai sisa (1.170.000) = semua lapisan (150 × 11.000 + 1.300.000)', dekat(1780000 + S2.A.sisaKg * S2.A.hppTerakhirPerKg, 150 * 11000 + 1300000));
// ---- 8a. retur karung utuh saat FIFO: modal kembali dicatat SAAT retur (irisan 110–160 = 40 × 11.000 + 10 × 13.000 = 570.000) dan laba Oktober tidak
// bergeser oleh penjualan November (tinjauan 9 Okt)
var RD = capModalKembali({ id: 'r1', tanggal: '2026-10-04', jam: '10:00', jenisAsal: 'karung', merkSumber: 'A', totalKg: 50, jumlahKarung: 1, kondisi: 'utuh', penyelesaian: 'refund', nominalRefund: 650000 });
ok('retur utuh FIFO menyimpan modal kembali 570.000 (karung kembali ke depan antrean)', RD.hppKembali === 570000, RD.hppKembali);
pasok('retur', [RD]);
var okt = function (t) { return t >= '2026-10-01' && t <= '2026-10-31'; };
var L1 = hitungLabaRentang(okt).returHpp;
pasok('penjualan', cacheMentah('penjualan').concat([{ id: 'j3', tanggal: '2026-11-05', jam: '09:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'A', totalKg: 40, jumlahKarung: 0.8, beratKarungAcuan: 50, hargaTotal: 520000, hppTotalSaatJual: 1 }]));
var L2 = hitungLabaRentang(okt).returHpp;
ok('laba Oktober membatalkan modal retur 570.000 dan TIDAK bergeser sesudah penjualan 5 Nov', L1 === 570000 && L2 === 570000, L1 + ' → ' + L2);
pasok('retur', []); pasok('penjualan', cacheMentah('penjualan').filter(function (p) { return p.id !== 'j3'; }));
var NR = hitungNeraca();
ok('neraca memakai nilai FIFO (A 1.170.000 + B 420.000 + C 1.850.000 + wadah W1 280.000)', dekat(NR.nilaiSack, 1170000 + 420000 + 1850000 + 280000), NR.nilaiSack);

// ---- 8b. kartu modal & saklar (Stok › HPP)
var KH = kartuHpp().kartu.find(function (k) { return k.merk === 'A'; });
ok('kartu modal FIFO: nilai rak = 1.170.000, modal keluar 13.000, teks menyebut kedatangan 2 Okt', KH.fifo && dekat(KH.nilaiRak, 1170000) && KH.modalKeluar === 13000 && /kedatangan 2 Okt( 2026)? · 90 kg @Rp13\.000\/kg/.test(KH.teksFifo), KH.teksFifo);
var W = { tanggal: '2026-10-05', jam: '10:00', idUnik: function () { return 88; } };
var SF = saklarFifo(new Date('2026-10-05T10:00:00+07:00'));
ok('saklar: keadaan nyala sejak 1 Okt; pilihan = besok 6 Okt & 1 Jan 2027', SF.keadaan === 'nyala' && SF.mulai === '2026-10-01' && SF.pilihan.map(function (p) { return p.tanggal; }).join() === '2026-10-06,2027-01-01', JSON.stringify(SF.pilihan));
ok('saklar: sudah berjalan → tidak bisa dinyalakan ulang; tanggal lampau ditolak', !!susunSaklarFifo('nyala', '2026-10-06', W, true).tolak && /sudah lewat/.test(susunSaklarFifo('nyala', '2026-10-01', W, true).tolak));
var M1 = susunSaklarFifo('mati', '', W, false), M2 = susunSaklarFifo('mati', '', W, true);
ok('saklar mati: ketukan pertama minta yakin; kedua menulis catatStok UTUH (kolom Aturan Barang masuk tetap) + riwayat', M1.perluYakin === 'mati' && M2.dokumen[0].data.modalFifoMulai === '' && M2.dokumen[0].data.minKarung === 40 && M2.dokumen[0].data.tanggal === '2026-09-30' && M2.dokumen[0].data.riwayatModalFifo.length === 1 && M2.dokumen[0].data.riwayatModalFifo[0].aksi === 'mati', JSON.stringify(M2.dokumen && M2.dokumen[0].data));
pasok('aturanToko', [M2.dokumen[0].data]);
ok('saklar dimatikan sesudah berjalan: masa 1–5 Okt DITUTUP — buku sampai 3 Okt & hari ini tetap FIFO (bulan lalu tidak dihitung ulang), mulai besok rata-rata',
  JSON.stringify(M2.dokumen[0].data.modalFifoMasa) === JSON.stringify([{ mulai: '2026-10-01', selesai: '2026-10-05' }]) && hitungStokKarungPerMerk('2026-10-03').A.metode === 'fifo'
  && hitungStokKarungPerMerk().A.metode === 'fifo' && hitungStokKarungPerMerk('2026-10-06').A.metode === undefined && dekat(hitungStokKarungPerMerk('2026-10-02').A.hppKeluarPerKg, 11000),
  JSON.stringify(M2.dokumen[0].data.modalFifoMasa));
var N2 = susunSaklarFifo('nyala', '2027-01-01', W, true);
ok('saklar nyala lagi 1 Jan 2027 (rencana): masa lama tetap tersimpan; 6 Okt–31 Des rata-rata; 1 Jan FIFO lagi', N2.dokumen[0].data.modalFifoMulai === '2027-01-01' && N2.dokumen[0].data.modalFifoMasa.length === 1
  && (pasok('aturanToko', [N2.dokumen[0].data]), saklarFifo(new Date('2026-10-05T10:00:00+07:00')).keadaan === 'rencana') && hitungStokKarungPerMerk('2026-12-31').A.metode === undefined
  && hitungStokKarungPerMerk('2026-10-02').A.metode === 'fifo' && hitungStokKarungPerMerk('2027-01-01').A.metode === 'fifo');
var MR = susunSaklarFifo('mati', '', W, true);
ok('rencana yang belum berjalan dibatalkan tanpa menambah masa', MR.dokumen[0].data.modalFifoMulai === '' && MR.dokumen[0].data.modalFifoMasa.length === 1);
pasok('aturanToko', SAKLAR);
var AC = susunAturCatat({ minKarung: '50' }, W);
ok('simpan Atur Barang masuk tidak menghapus saklar FIFO (dokumen catatStok disalin utuh)', AC.dokumen && AC.dokumen[0].data.modalFifoMulai === '2026-10-01' && AC.dokumen[0].data.minKarung === 50, JSON.stringify(AC.dokumen && AC.dokumen[0].data));

// ---- 9. saklar dimatikan lagi = kembali rata-rata
pasok('aturanToko', [{ id: 'catatStok', tanggal: '2026-10-05', jam: '11:00', modalFifoMulai: '' }]);
var S3 = hitungStokKarungPerMerk();
ok('saklar dimatikan: rata-rata lagi, tanpa lapisan', S3.A.metode === undefined && dekat(S3.A.hppTerakhirPerKg, 3500000 / 300));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var aturan = (CAD.aturanToko || []).filter(function (d) { return String(d.id) !== 'catatStok'; });
var catat = (CAD.aturanToko || []).find(function (d) { return String(d.id) === 'catatStok'; }) || { id: 'catatStok' };
pasok('aturanToko', aturan.concat([Object.assign({}, catat, { modalFifoMulai: '' })]));
var MATI = JSON.parse(JSON.stringify(hitungStokKarungPerMerk()));
var MATI_B = JSON.parse(JSON.stringify(hitungStokKarungPerMerk(BESOK)));
pasok('aturanToko', aturan.concat([Object.assign({}, catat, { modalFifoMulai: BESOK })]));
// buku dihitung SAMPAI hari saklar (besok) — hari ini saklar yang dijadwalkan belum berlaku
var NYALA = hitungStokKarungPerMerk(BESOK); var HARI_INI = hitungStokKarungPerMerk(); var beda = [], n = 0, nilaiMati = 0, nilaiNyala = 0, wadah = 0, fifo = 0, hariIniFifo = 0, tanpaLapisBerisi = [];
Object.keys(HARI_INI).forEach(function (m) { if (HARI_INI[m].metode) hariIniFifo++; });
Object.keys(MATI_B).forEach(function (m) { var a = MATI_B[m], b = NYALA[m]; if (b.metode === 'fifo') fifo++; else if (!/^Wadah /.test(m) && a.sisaKg > 0.005) tanpaLapisBerisi.push(m); if (/^Wadah /.test(m)) { wadah++; if (b.metode) beda.push(m + ' wadah ikut FIFO'); return; }
  n++; var va = a.sisaKg * a.hppTerakhirPerKg, vb = b.sisaKg * b.hppTerakhirPerKg; nilaiMati += va; nilaiNyala += vb;
  if (Math.abs(va - vb) > 1 || a.sisaKg !== b.sisaKg) beda.push(m + ' ' + Math.round(va) + ' → ' + Math.round(vb)); });
// pembanding (bukan keputusan): seandainya saklar menyala sejak 15 Sep — nilai rak sekarang FIFO vs rata-rata
pasok('aturanToko', aturan.concat([Object.assign({}, catat, { modalFifoMulai: '2026-09-15' })]));
var F15 = hitungStokKarungPerMerk(); var nilaiF15 = 0; Object.keys(F15).forEach(function (m) { if (!/^Wadah /.test(m)) nilaiF15 += F15[m].sisaKg * F15[m].hppTerakhirPerKg; });
pasok('aturanToko', CAD.aturanToko || []);
var ASLI = hitungStokKarungPerMerk(); var bedaAsli = Object.keys(ASLI).filter(function (m) { return JSON.stringify(ASLI[m]) !== JSON.stringify(MATI[m]); });
print(JSON.stringify({ n: n, fifo: fifo, tanpaLapisBerisi: tanpaLapisBerisi, hariIniFifo: hariIniFifo, wadah: wadah, beda: beda, nilaiMati: Math.round(nilaiMati), nilaiNyala: Math.round(nilaiNyala), bedaAsli: bedaAsli, nilaiF15: Math.round(nilaiF15), saklarToko: mfMulaiDari(CAD.aturanToko || []) }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:700]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js):
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar SAKLAR = ' + json.dumps(SAKLAR) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            'lapisan diurut terbaru dulu (bukan yang lama keluar dulu)': js.replace("String(x.tanggal).localeCompare(String(y.tanggal)) || (Number(x.id) || 0) - (Number(y.id) || 0)", "String(y.tanggal).localeCompare(String(x.tanggal)) || (Number(y.id) || 0) - (Number(x.id) || 0)"),
            'lapisan buka dinilai harga terbaru, bukan rata-rata saat saklar (nilai rak melompat)': js.replace("kg: b.sisaKg, harga: b.hppTerakhirPerKg || 0, asal: 'buka'", "kg: b.sisaKg, harga: b.hargaTerakhirPerKg || 0, asal: 'buka'"),
            'buku sebelum hari saklar ikut FIFO (bulan lalu berubah)': js.replace("find((m) => d >= m.mulai && (!m.selesai || d <= m.selesai))", "find((m) => (!m.selesai || d <= m.selesai))"),
            'saklar yang dijadwalkan ke depan sudah berlaku hari ini': js.replace("const d = sampai || mfHariIni();", "const d = sampai || '9999-12-31';"),
            'nota tidak memakai modal FIFO (angka keranjang apa adanya)': js.replace("const st = stok[r.merkSumber]; if (!st || st.metode !== 'fifo' || r.dariWadah", "const st = null; if (!st || st.metode !== 'fifo' || r.dariWadah"),
            'nota: dua baris merek sama mengambil dari depan yang sama': js.replace("fifoAmbil[r.merkSumber] = (fifoAmbil[r.merkSumber] || 0) + kg;\n  });\n  return out;", "\n  });\n  return out;"),
            'nota: kantong / wadah repack hilang dari modal': js.replace("+ (r.biayaKemasanLiteran || 0) + (r.biayaKemasanRepack || 0);", ";"),
            'wadah ikut FIFO (owner: wadah campuran rata-rata)': js.replace("export const mfWadah = (merk) => /^Wadah /.test(String(merk || ''));", "const mfWadah = (merk) => false;").replace("const mfWadah = (merk) => /^Wadah /.test(String(merk || ''));", "const mfWadah = (merk) => false;"),
            'adukan: modal bahan rata-rata': js.replace("hpp: st ? hppKeluarPerKg(st, kg, sudah) : 0, nilai: st ? hppKeluar(st, kg, sudah) : 0", "hpp: st ? (st.hppRataPerKg || st.hppTerakhirPerKg || 0) : 0, nilai: st ? (st.hppRataPerKg || st.hppTerakhirPerKg || 0) * kg : 0"),
            'takar ke wadah: modal rata-rata': js.replace("const v = hppKeluar(st, x.kg, fifoAmbil[x.merk]);", "const v = x.kg * ((st || {}).hppRataPerKg || 0);"),
            'selisih lebih dinilai dari belakang antrean': js.replace("return s < 0 ? -mfIrisan(st.lapisan, p, p - s) : mfIrisan(st.lapisan, p - s, p);", "return s < 0 ? -mfIrisan(st.lapisan, p, p - s) : s * (st.hppTerakhirPerKg || 0);"),
            'irisan melewatkan bagian di luar jejeran (stok minus bernilai 0)': js.replace("if (sampai > T && dari < sampai) rp += (sampai - Math.max(dari, T)) * L[L.length - 1].harga;", ""),
            'Atur Barang masuk menulis catatStok tanpa kolom lama (saklar FIFO hilang)': js.replace("const data = Object.assign({}, lama, { id: 'catatStok',", "const data = Object.assign({}, {}, { id: 'catatStok',"),
            'mematikan saklar tidak menutup masa (neraca bulan lalu dihitung ulang rata-rata)': js.replace("concat(aksi === 'mati' && S.keadaan === 'nyala' ? [{ mulai: S.mulai, selesai: S.hari }] : [])", "concat([])"),
            'masa FIFO yang sudah ditutup diabaikan mesin': js.replace("return tutup.concat(mulai ? [{ mulai, selesai: '' }] : []);", "return mulai ? [{ mulai, selesai: '' }] : [];"),
            'retur FIFO tidak menyimpan modal kembali (laba bergeser tiap penjualan baru)': js.replace("return Object.assign(d, { hppKembali: Math.round(nilaiSelisihKg(st, Number(d.totalKg) || 0)) });", "return d;"),
            'laba mengabaikan modal kembali retur yang tersimpan': js.replace("if (typeof r.hppKembali === 'number' && isFinite(r.hppKembali)) return Math.round(r.hppKembali);", ""),
            'saklar membaca tanggal yang salah bentuk': js.replace("return mfTglSah(t) ? t : '';", "return t;"),
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
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad:
        c = json.load(open(cad[-1], encoding='utf-8'))
        tgl = os.path.basename(cad[-1]).split('miqbal-')[-1][:10]
        import datetime
        besok = (datetime.date.fromisoformat(tgl) + datetime.timedelta(days=1)).isoformat()
        h, e = jalan("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\nvar BESOK = '%s';\n" % (tgl, besok) + js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP)
        if h is None: print('ASAP DATA TOKO: JSC JATUH ' + e); g.append('asap')
        else:
            print('ASAP DATA TOKO (%s): saklar toko %s · saklar dijadwalkan %s (hari ini masih rata-rata: %s): %d merek karung (%d berlapis FIFO, sisanya stok 0/minus tanpa kedatangan baru), nilai rak Rp%s → Rp%s, beda per merek: %s · %d wadah tetap rata-rata · saklar mati = mesin tanpa setelan: %s'
                  % (os.path.basename(cad[-1]), h['saklarToko'] or 'MATI', besok, 'ya' if not h['hariIniFifo'] else 'TIDAK', h['n'], h['fifo'], format(h['nilaiMati'], ',').replace(',', '.'), format(h['nilaiNyala'], ',').replace(',', '.'),
                     ', '.join(h['beda']) or 'nihil', h['wadah'], 'sama persis' if not h['bedaAsli'] else 'BEDA ' + ', '.join(h['bedaAsli'][:5])))
            print('   pembanding (bukan keputusan): seandainya FIFO sejak 15 Sep, nilai rak karung sekarang Rp%s (rata-rata Rp%s)' % (format(h['nilaiF15'], ',').replace(',', '.'), format(h['nilaiMati'], ',').replace(',', '.')))
            if h['beda'] or abs(h['nilaiMati'] - h['nilaiNyala']) > 1: g.append('asap: nilai rak melompat saat saklar dinyalakan')
            if h['hariIniFifo'] or h['tanpaLapisBerisi']: g.append('asap: saklar terjadwal sudah berlaku hari ini / merek berisi tanpa lapisan: ' + ', '.join(h['tanpaLapisBerisi']))
            if h['bedaAsli'] and not h['saklarToko']: g.append('asap: saklar mati tetapi mesin berbeda')
    sys.exit(2 if g else 0)
