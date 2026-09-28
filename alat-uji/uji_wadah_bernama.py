#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_wadah_bernama.py — putaran 27 Bagian 5: WADAH BERNAMA (owner 27 Sep).
  · Wadah = TEMPAT bernama (W1–W8). Nama seperti "IR64 Apex" = nama wadah / kelas mutu, bukan merek. Harga per liter melekat pada WADAH.
  · Buku stok hanya per merek karung: literan yang terjual dari wadah memotong buku merek-merek asal isinya SEBANDING komposisi saat itu
    (satu takaran → baris internal per merek asal, nama tampil = nama wadah; struk tetap satu baris, totalnya satu). HPP = rata-rata tertimbang isi.
  · Identitas: tumpukan + karung terbuka + bagian merek di semua wadah = buku merek.
  · Katalog: merek yang cuma lewat wadah tidak ditagih harga liter; merek literan LANGSUNG tetap wajib punya harga liter; Katalog › Literan = wadah.
  · Barang masuk tidak pernah lagi dibukukan atas nama wadah/kelas (kecuali nama wadah yang juga merek karung). Ganti nama wadah membawa isi & harga.
  · Peralihan tanpa migrasi: isi wadah lama (tanpa komposisi) & baris literan lama tetap terbaca atas nama wadahnya.
KOTAK PASIR (ANGKA CONTOH), jam dikunci 19 Sep 2026 10:00 WIB. Cadangan toko di _privat/: identitas semua merek menutup, tiap wadah berharga dijual
1 L lewat jalur baru, katalog tidak menagih liter merek lewat-wadah; ASAP GLOBAL: omzet, laba, neraca tiap bulan byte-sama dengan kode main.

    python3 alat-uji/uji_wadah_bernama.py            → N lulus · 0 gagal
    python3 alat-uji/uji_wadah_bernama.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, io, sys, json, glob, tarfile, subprocess, tempfile, shutil
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_jual_baru  # noqa: E402
import uji_kunci_periode  # noqa: E402  (satu_lingkup, putaran 30)
import uji_laporan_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_jual_baru.MODUL + [m for m in ['baru/js/layar/stok-logika.js', 'baru/js/layar/varian-logika.js', 'baru/js/layar/stok-hpp-logika.js', 'baru/js/layar/kelas-merek-logika.js', 'baru/js/layar/stok-catat-logika.js', 'baru/js/layar/harga-logika.js', 'baru/js/data/katalog-kasir.js'] if m not in uji_jual_baru.MODUL]   # putaran 30: + stok-hpp & kelas-merek
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def brs(i, merk, karung, harga, berat=50):
    return {'id': str(i), 'merk': merk, 'satuan': 'karung', 'beratKarung': berat, 'jumlahKarung': karung, 'totalKg': karung * berat, 'hargaPerKg': harga, 'subtotalHarga': karung * berat * harga}


def jual(i, tgl, jam, merk, liter, kg, harga, hpp):
    return {'id': i, 'tanggal': tgl, 'jam': jam, 'caraBayar': 'Tunai', 'jenis': 'literan', 'merkSumber': merk, 'namaProduk': merk, 'jumlahLiter': liter, 'totalKg': kg, 'hargaTotal': harga, 'hppTotalSaatJual': hpp}


KOTAK = {
  # b0 = kedatangan LAMA atas nama kelas "IR64 Apex" (sebelum putaran 27) + Ketan Putih (dijual literan langsung); b1 = NG, Kumala (1 karung saja), Angsa
  'batchMasuk': [{'id': 'b0', 'tanggal': '2026-08-20', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [brs(1, 'IR64 Apex', 2, 14000), brs(2, 'Ketan Putih', 1, 20000)]},
                 {'id': 'b1', 'tanggal': '2026-09-10', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [brs(1, 'NG', 10, 12000), brs(2, 'Kumala', 1, 11000), brs(3, 'Angsa', 4, 13000)]}],
  # aturan: empat wadah; IR64 Apex berisi NG 30 + Kumala 20 (komposisi putaran 27); Angsa = dokumen LAMA tanpa komposisi; Campur Tiga = tiga merek sama besar
  'wadahLiteran': [{'id': 100, 'tanggal': '2026-09-01', 'jam': '07:00', 'tipe': 'atur', 'penuhKg': 50, 'puncakKg': 60, 'isiUlangKg': 10, 'takarKg': 1.8, 'daftar': ['IR64 Apex', 'Angsa', 'Campur Tiga', 'IR42 Value']},
                   {'id': 101, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'IR64 Apex', 'isiKg': 50, 'komposisi': {'NG': 30, 'Kumala': 20}},
                   {'id': 102, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'Angsa', 'isiKg': 40},
                   {'id': 103, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'Campur Tiga', 'isiKg': 30, 'komposisi': {'NG': 10, 'Kumala': 10, 'Angsa': 10}},
                   # karung Angsa dibuka di belakang wadah Angsa dengan catatan LAMA (tanpa kolom wadah — sebelum 21 Sep): letaknya dibaca dari daftar wadah
                   {'id': 99, 'tanggal': '2026-09-18', 'jam': '07:30', 'tipe': 'karung', 'merk': 'Angsa', 'kg': 50}],
  'katalogHargaLiteran': [{'id': 'IR64 Apex', 'merk': 'IR64 Apex', 'hargaPerLiter': 12000}, {'id': 'Angsa', 'merk': 'Angsa', 'hargaPerLiter': 13000}, {'id': 'Campur Tiga', 'merk': 'Campur Tiga', 'hargaPerLiter': 12500},
                          {'id': 'NG', 'merk': 'NG', 'hargaPerLiter': 12500}, {'id': 'Ketan Putih', 'merk': 'Ketan Putih', 'hargaPerLiter': 21000}],
  'katalogHargaKarung': [{'id': 'NG', 'merk': 'NG', 'hargaPerKg': 13000}, {'id': 'Kumala', 'merk': 'Kumala', 'hargaPerKg': 12000}, {'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 14000},
                         {'id': 'Ketan Putih', 'merk': 'Ketan Putih', 'hargaPerKg': 22000}, {'id': 'IR64 Apex', 'merk': 'IR64 Apex', 'hargaPerKg': 15000}],
  # baris literan LAMA: Ketan Putih langsung dari karungnya (5 Sep); literan wadah Angsa sesudah titik samakan 08:00 (tanpa dariWadah — cara sistem lama)
  'penjualan': [jual(5001, '2026-09-05', '09:00', 'Ketan Putih', 2, 1.63, 42000, 32600), jual(5002, '2026-09-19', '09:00', 'Angsa', 5, 4.1, 65000, 53300)],
  # harga liter NG pernah TERBIT (riwayat) dan masih punya draf — yang dihapus nanti cuma dokumen katalognya (+ draf nama itu)
  'hargaTerbit': [{'id': 7, 'tanggal': '2026-09-18', 'jam': '10:00', 'n': 1, 'daftar': [{'kunci': 'NG|L', 'nama': 'NG · Literan', 'lama': 0, 'baru': 12500, 'koleksi': 'katalogHargaLiteran'}]}],
  'aturanToko': [{'id': 'hargaDraf', 'draf': {'NG|L': 13000, 'Angsa|S': 14100}}],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var nId = 9000; var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var KINI = new Date(Date.now());
var s0 = function () { var s = keadaanAwal(); s.sekarang = new Date(Date.now()); return s; };
var rakL = function (s) { return susunRak(s || s0()).literan; };
var chipL = function (k, s) { return rakL(s).find(function (c) { return c.kunci === k; }); };
var masuk = function (s, c, j) { var r = masukkan(Object.assign({}, s, { pilih: c }), j); return r.keranjang ? Object.assign({}, s, { keranjang: r.keranjang, urutBaris: r.urutBaris }) : Object.assign({ tolak: r.kabar }, s); };
var buku = function (m) { return (hitungStokKarungPerMerk()[m] || { sisaKg: 0 }).sisaKg; };
var B3 = function (n) { return Math.round(n * 1000) / 1000; };
var menutup = function (m) { var t = tumpukanGudang(m); return Math.abs(t.kg + t.diBelakangKg + t.diWadahKg - (t.bukuKg - t.pindahKeluarKg + t.pindahMasukKg)) < 0.011; };
var jualDok = function (N) { return (N.dokumen || []).filter(function (d) { return d.koleksi === 'penjualan'; }).map(function (d) { return d.data; }); };
var jumlah = function (a, f) { return a.reduce(function (x, r) { return x + (r[f] || 0); }, 0); };

// ---- 1 · rak: harga liter melekat pada WADAH; merek yang cuma lewat wadah tidak punya chip literan sendiri
var cA = chipL('IR64 Apex');
ok('rak literan: wadah IR64 Apex = SATU chip (harga wadah 12.000/L, modal = rata-rata tertimbang isi (30×12.000 + 20×11.000)/50 = 11.600/kg); NG & Kumala TIDAK punya chip literan (NG punya harga liter lama — tidak dipakai); Ketan Putih (literan langsung, dari penjualan lama) tetap; wadah tanpa harga (IR42 Value) tidak tampil',
  cA && cA.wadahLiteran === true && cA.harga === 12000 && Math.abs(cA.hppPerKg - 11600) < 0.001 && !rakL().some(function (c) { return c.kunci === 'NG' || c.kunci === 'Kumala'; }) && rakL().some(function (c) { return c.kunci === 'Ketan Putih' && !c.wadahLiteran; }) && !chipL('IR42 Value'), J(rakL().map(function (c) { return [c.kunci, c.harga, c.hppPerKg, c.sisa]; })));
ok('langit-langit liter wadah = merek yang PALING CEPAT habis dibanding porsinya: Kumala cuma 50 kg di buku, porsi 40 % → 125 kg isi wadah → 125 ÷ 0,82 = 152,4 L (bukan 833 kg dari NG)', cA.sisa === 152.4, cA.sisa);
// ---- 2 · keranjang & nota: satu takaran → baris internal per merek asal
var s1 = masuk(s0(), cA, 5); var t1 = s1.keranjang && s1.keranjang[0] && s1.keranjang[0].trx;
ok('keranjang 5 L IR64 Apex: 4,1 kg, dariWadah, pecahan NG 2,46 + Kumala 1,64 (3 : 2), Rp60.000, modal NG 2,46×12.000 + Kumala 1,64×11.000 = 47.560 + kantong', !s1.tolak && t1.dariWadah === 'IR64 Apex' && t1.namaProduk === 'IR64 Apex' && t1.totalKg === 4.1 && J(t1.pecahan) === J([{ merk: 'NG', kg: 2.46 }, { merk: 'Kumala', kg: 1.64 }]) && t1.hargaTotal === 60000 && t1.hppTotalSaatJual === 47560 + (t1.biayaKemasanLiteran || 0), J(t1));
sinkronKeranjang(s1);
ok('keranjang MEMEGANG buku merek asal (bukan nama wadah): langit-langit turun ke (50 − 1,64) ÷ 0,4 ÷ 0,82 = 147,4 L; chip karung Kumala ikut menyusut', chipL('IR64 Apex', s1).sisa === 147.4, chipL('IR64 Apex', s1).sisa);
var bNG = buku('NG'), bKu = buku('Kumala'), bAp = buku('IR64 Apex');
var N1 = simpanNota(Object.assign({}, s1, { cara: 'Tunai', uang: 60000 }), W); var r1 = jualDok(N1);
ok('nota: DUA baris internal satu takaran — nama tampil IR64 Apex, dariWadah IR64 Apex, merkSumber NG / Kumala, 3 L + 2 L, 2,46 + 1,64 kg, Rp36.000 + Rp24.000, modal 29.520 + 18.040 (merek asal); takaranId sama (= id baris pertama); kantong literan hanya di baris pertama; kolom kerja pecahan/_takaran tidak ikut; ringkas "1 barang"',
  !N1.tolak && r1.length === 2 && r1.every(function (r) { return r.namaProduk === 'IR64 Apex' && r.dariWadah === 'IR64 Apex' && r.jenis === 'literan' && r.pecahan === undefined && r._takaran === undefined && r.takaranId === String(r1[0].id); })
  && r1[0].merkSumber === 'NG' && r1[1].merkSumber === 'Kumala' && r1[0].jumlahLiter === 3 && r1[1].jumlahLiter === 2 && r1[0].totalKg === 2.46 && r1[1].totalKg === 1.64 && r1[0].hargaTotal === 36000 && r1[1].hargaTotal === 24000
  && r1[0].hppTotalSaatJual === 29520 + (r1[0].biayaKemasanLiteran || 0) && r1[1].hppTotalSaatJual === 18040 && r1[1].kemasanLiteran === undefined && r1[1].biayaKemasanLiteran === undefined && /^1 barang/.test(N1.ringkas), J([r1, N1.ringkas]));
terapkanKeCache(N1.dokumen);
ok('buku: NG turun 2,46 & Kumala turun 1,64 (3 : 2); TIDAK ada buku atas nama wadah (buku lama IR64 Apex 100 kg tetap)', B3(bNG - buku('NG')) === 2.46 && B3(bKu - buku('Kumala')) === 1.64 && buku('IR64 Apex') === bAp && bAp === 100, J([bNG, buku('NG'), bKu, buku('Kumala'), buku('IR64 Apex')]));
ok('komposisi wadah sesudahnya NG 27,54 + Kumala 18,36; IDENTITAS menutup untuk semua merek (tumpukan + karung terbuka + bagian di semua wadah = buku): NG di wadah = 27,54 + 10 (Campur Tiga)',
  J(wbKomposisi('IR64 Apex').bagian) === J({ NG: 27.54, Kumala: 18.36 }) && B3(tumpukanGudang('NG').diWadahKg) === 37.54 && ['NG', 'Kumala', 'Angsa', 'IR64 Apex', 'Ketan Putih'].every(menutup), J([wbKomposisi('IR64 Apex'), tumpukanGudang('NG')]));
// ---- 3 · tampilan: struk satu baris, Hari ini satu baris, Papan Kapur menyebut buku asal
var nota1 = notaDari({ trxId: N1.patch.notaTerakhir.trxId }); var st1 = susunStruk(nota1, stAtur());
ok('struk: SATU baris "IR64 Apex literan" (5 L × 12.000 = Rp60.000), total Rp60.000 — baris internal tidak terlihat pembeli', st1.garis.filter(function (g) { return /IR64 Apex literan/.test(g.kiri || ''); }).length === 1 && st1.garis.some(function (g) { return /5 L × 12\.000/.test(g.kiri || '') && g.kanan === 'Rp60.000'; }) && st1.total === 60000 && !st1.garis.some(function (g) { return /NG|Kumala/.test(g.kiri || ''); }), J(st1.kertas));
var HI = hariIni(s0()).terakhir.filter(function (x) { return String(x.trxId) === String(N1.patch.notaTerakhir.trxId); });
ok('Jual › Hari ini: satu takaran = SATU baris "IR64 Apex 5 L" Rp60.000', HI.length === 1 && HI[0].teks === 'IR64 Apex 5 L' && HI[0].n === 60000, J(HI));
ok('Papan Kapur: "Terjual literan wadah IR64 Apex (buku Kumala + NG) · 1 baris" −4,1 kg', susunKapur(KINI).baris.some(function (x) { return /Terjual literan wadah IR64 Apex \(buku Kumala \+ NG\) · 1 baris/.test(x.isi) && x.n === '−4,1 kg'; }), J(susunKapur(KINI).baris.filter(function (x) { return x.jenis === 'keluar'; })));
// ---- 4 · batalkan nota barusan: semua baris internal ikut batal, buku & komposisi pulih
var BT = susunPembatalan(N1.patch.notaTerakhir, 'uji', W);
ok('batalkan: KEDUA baris internal ditandai batal; buku NG/Kumala & komposisi wadah kembali persis', BT && BT.dokumen.length === 2 && (function () { terapkanKeCache(BT.dokumen); return buku('NG') === bNG && buku('Kumala') === bKu && J(wbKomposisi('IR64 Apex').bagian) === J({ NG: 30, Kumala: 20 }); })(), J(BT && BT.dokumen.length));
// ---- 5 · tiga merek: sisa pembulatan ke baris terakhir, potongan nota tetap menutup
var cT = chipL('Campur Tiga'); var s3 = masuk(s0(), cT, 1); var N3 = simpanNota(Object.assign({}, s3, { cara: 'QRIS', potongan: 1000 }), W); var r3 = jualDok(N3);
ok('1 L dari wadah tiga merek sama besar (Angsa, Kumala, NG): kg 0,273 + 0,273 + 0,274 = 0,82 · liter 0,333 + 0,333 + 0,334 = 1 · rupiah 4.162 + 4.162 + 4.176 = 12.500 (sisa ke baris terakhir) · potongan 1.000 dibagi → Σ 11.500 · modal tiap baris = kg × modal merek asalnya',
  !N3.tolak && r3.length === 3 && J(r3.map(function (r) { return r.merkSumber; })) === J(['Angsa', 'Kumala', 'NG']) && J(r3.map(function (r) { return r.totalKg; })) === J([0.273, 0.273, 0.274]) && B3(jumlah(r3, 'jumlahLiter')) === 1
  && jumlah(r3, 'hargaTotal') + jumlah(r3, 'potonganTransaksi') === 12500 && jumlah(r3, 'hargaTotal') === 11500 && jumlah(r3, 'potonganTransaksi') === 1000
  && r3[0].hppTotalSaatJual - (r3[0].biayaKemasanLiteran || 0) === Math.round(0.273 * 13000) && r3[1].hppTotalSaatJual === Math.round(0.273 * 11000) && r3[2].hppTotalSaatJual === Math.round(0.274 * 12000), J(r3));
terapkanKeCache(N3.dokumen);
// ---- 6 · isi wadah habis / lupa dicatat: kelebihan dipotong dari karung di belakang wadahnya dan DISEBUT
terapkanKeCache([{ koleksi: 'wadahLiteran', data: { id: 104, tanggal: '2026-09-19', jam: '09:50', tipe: 'karung', merk: 'NG', kg: 50, wadah: 'Campur Tiga' } }]);
var K3 = wbKomposisi('Campur Tiga'); var P3 = wbPecah('Campur Tiga', 35);
ok('pecah 35 kg dari wadah berisi ±29,18 kg: bagian positif habis dibagi, kelebihan ' + B3(35 - K3.totalKg) + ' kg dipotong dari karung di belakang wadah (NG) — lewatKg disebut, Σ persis 35', B3(jumlah(P3.bagian, 'kg')) === 35 && P3.lewatKg === B3(35 - K3.totalKg) && P3.lewatKg > 0 && B3(P3.bagian.find(function (x) { return x.merk === 'NG'; }).kg - K3.bagian['NG'] - P3.lewatKg) === 0, J([K3, P3]));
// ---- 7 · takar model baru (bukuAsal) + varian dibuka ke wadah = merek asal biasa
terapkanKeCache([{ koleksi: 'batchMasuk', data: { id: 'b2', tanggal: '2026-09-18', jam: '08:00', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ id: '1', merk: 'NG · Premium', satuan: 'karung', beratKarung: 50, jumlahKarung: 1, totalKg: 50, hargaPerKg: 12800, subtotalHarga: 640000 }] } }]);
var bPr = buku('NG · Premium'); var TK = susunTakarWadah('IR64 Apex', [{ merk: 'NG · Premium', takar: 2 }], W, s0());
ok('takar 2 × 1,8 kg dari karung varian "NG · Premium" ke wadah IR64 Apex: SATU dokumen takar bertanda bukuAsal, tanpa produksi (buku tidak dipindah)', !TK.tolak && TK.dokumen.length === 1 && TK.dokumen[0].data.bukuAsal === true && TK.dokumen[0].data.kg === 3.6, J(TK));
terapkanKeCache(TK.dokumen);
ok('sesudah takar: buku varian TIDAK berubah; komposisi IR64 Apex memegang NG · Premium 3,6 kg; modal wadah = (30×12.000 + 20×11.000 + 3,6×12.800)/53,6', buku('NG · Premium') === bPr && wbKomposisi('IR64 Apex').bagian['NG · Premium'] === 3.6 && Math.abs(wbModalPerKg('IR64 Apex') - (30 * 12000 + 20 * 11000 + 3.6 * 12800) / 53.6) < 0.001, J(wbKomposisi('IR64 Apex')));
var N7 = simpanNota(Object.assign({}, masuk(s0(), chipL('IR64 Apex'), 10), { cara: 'QRIS' }), W); var r7 = jualDok(N7);
ok('10 L sesudahnya memotong TIGA buku asal (NG, Kumala, NG · Premium) sebanding 30 : 20 : 3,6 — varian diperlakukan sebagai merek asal biasa', !N7.tolak && r7.length === 3 && J(r7.map(function (r) { return r.merkSumber; }).sort()) === J(['Kumala', 'NG', 'NG · Premium']) && B3(jumlah(r7, 'totalKg')) === 8.2 && (function () { terapkanKeCache(N7.dokumen); return B3(bPr - buku('NG · Premium')) === r7.find(function (r) { return r.merkSumber === 'NG · Premium'; }).totalKg; })(), J(r7));
// ---- 8 · peralihan: wadah LAMA tanpa komposisi = seluruh isinya milik nama wadah; baris lama tanpa dariWadah tetap mengurangi
ok('peralihan: isi wadah Angsa (dokumen lama tanpa komposisi) = milik "Angsa" 40 − 4,1 (baris literan lama 09:00) − bagian Campur Tiga yang terjual; nama lama IR64 Apex (buku 100 kg dari kedatangan lama) tetap dijual karung/repack sampai habis',
  wbKomposisi('Angsa').diketahui && Object.keys(wbKomposisi('Angsa').bagian).join() === 'Angsa' && wbKomposisi('Angsa').bagian['Angsa'] === 35.9 && susunRak(s0()).karung.some(function (c) { return c.kunci === 'IR64 Apex'; }) && susunRak(s0()).repack.some(function (c) { return c.kunci === 'IR64 Apex'; }), J([wbKomposisi('Angsa'), susunRak(s0()).karung.map(function (c) { return c.kunci; })]));
// ---- 9 · katalog harga: liter = wadah + literan langsung; merek lewat-wadah tidak ditagih
var S = hgSemua(KINI); var bA = cariBaris(S, 'IR64 Apex|L');
ok('katalog: baris liter hanya untuk WADAH (IR64 Apex, Angsa, Campur Tiga, IR42 Value) + literan langsung (Ketan Putih); NG / Kumala / NG · Premium TIDAK ditagih harga liter; wadah tanpa harga (IR42 Value) = "belum ada harga"; modal baris liter wadah = modal isi wadah',
  J(S.baris.filter(function (b) { return b.st.id === 'L'; }).map(function (b) { return b.merk; }).sort()) === J(['Angsa', 'Campur Tiga', 'IR42 Value', 'IR64 Apex', 'Ketan Putih']) && cariBaris(S, 'IR42 Value|L').status === 'lubang' && !S.perlu.some(function (b) { return /^(NG|Kumala)/.test(b.k) && b.st.id === 'L'; })
  && bA.wadah === true && bA.judul === 'IR64 Apex · Literan wadah' && Math.abs(bA.modalKg - wbModalPerKg('IR64 Apex')) < 0.001 && bA.n === 12000, J(S.baris.filter(function (b) { return b.st.id === 'L'; }).map(function (b) { return [b.k, b.status, b.modalKg]; })));
var LT = hgLiteran(S); var lA = LT.wadah.find(function (x) { return x.nama === 'IR64 Apex'; });
ok('Katalog › Literan: empat wadah berurutan (nama, harga/L, modal isi/L = modal/kg × 0,82, untung/L, komposisi %); literan langsung Ketan Putih; harga liter NG tercatat "tidak dipakai"',
  J(LT.wadah.map(function (x) { return x.nama; })) === J(['IR64 Apex', 'Angsa', 'Campur Tiga', 'IR42 Value']) && lA.harga === 12000 && Math.abs(lA.modalLiter - wbModalPerKg('IR64 Apex') * 0.82) < 0.01 && Math.abs(lA.untungLiter - (12000 - lA.modalLiter)) < 0.01 && lA.komposisi.length === 3 && Math.abs(lA.komposisi.reduce(function (a, k) { return a + k.persen; }, 0) - 100) < 0.2
  && J(LT.langsung.map(function (x) { return x.merk; })) === J(['Ketan Putih']) && LT.tidakDipakai.some(function (x) { return x.merk === 'NG' && x.harga === 12500; }), J(LT));
var LL = wbSusunLiteranLangsung('Kumala', true, W);
ok('tandai Kumala literan LANGSUNG → aturan wadah baru (koleksi wadahLiteran, terbaca karyawan) membawa semua kolom lama + literanLangsung [Ketan Putih, Kumala]; nama wadah ditolak', !LL.tolak && LL.dokumen[0].koleksi === 'wadahLiteran' && LL.dokumen[0].data.tipe === 'atur' && J(LL.dokumen[0].data.literanLangsung) === J(['Ketan Putih', 'Kumala']) && J(LL.dokumen[0].data.daftar) === J(KOTAK.wadahLiteran[0].daftar) && LL.dokumen[0].data.takarKg === 1.8 && /nama WADAH/.test(wbSusunLiteranLangsung('IR64 Apex', true, W).tolak || ''), J(LL));
terapkanKeCache(LL.dokumen);
ok('literan langsung TANPA harga liter → katalog menagih "belum ada harga" (Kumala|L) dan rak belum menampilkan chipnya; dilepas lagi → tagihannya hilang', cariBaris(hgSemua(KINI), 'Kumala|L') && cariBaris(hgSemua(KINI), 'Kumala|L').status === 'lubang' && !chipL('Kumala') && (function () { terapkanKeCache(wbSusunLiteranLangsung('Kumala', false, W).dokumen); return !cariBaris(hgSemua(KINI), 'Kumala|L'); })());
// ---- 9b · hapus harga liter yang TIDAK DIPAKAI (owner 27 Sep: hapus harga liter NG & Kumala)
var terbit0 = J(ambilHargaTerbit()); var jual0 = J(ambilPenjualanSemua()); var HL0 = susunHapusLiter('NG', W, false); var HL = susunHapusLiter('NG', W, true);
ok('hapus harga liter NG (tidak dipakai rak): ketukan pertama DITANYA; kedua = hapus dokumen katalogHargaLiteran NG + draf NG|L dibuang (draf lain tetap), harga lamanya di jejak; harga liter WADAH (IR64 Apex) & literan LANGSUNG (Ketan Putih) ditolak dihapus dari sini',
  HL0.perluYakin === true && !HL0.hapus && !HL.tolak && J(HL.hapus) === J([{ koleksi: 'katalogHargaLiteran', id: 'NG' }]) && HL.dokumen.length === 1 && J(HL.dokumen[0].data.draf) === J({ 'Angsa|S': 14100 }) && /12\.500/.test(HL.jejakHapus)
  && /tidak ada di daftar/.test(susunHapusLiter('IR64 Apex', W, true).tolak || '') && /tidak ada di daftar/.test(susunHapusLiter('Ketan Putih', W, true).tolak || ''), J([HL0, HL]));
terapkanKeCache(HL.dokumen.concat(HL.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })));
var kkNG = kkIsi().merkKarung.find(function (m) { return m.merk === 'NG'; });
ok('sesudah hapus: NG hilang dari "tidak dipakai", rak & katalog tetap tanpa liter NG; riwayat terbit & semua nota BYTE-SAMA; katalog HP kasir: baris NG tetap ada dengan harga liter 0 (kasir.html menulis tuts literannya "harga?")',
  !hgLiteran(hgSemua(KINI)).tidakDipakai.some(function (x) { return x.merk === 'NG'; }) && !cariBaris(hgSemua(KINI), 'NG|L') && !chipL('NG') && J(ambilHargaTerbit()) === terbit0 && J(ambilPenjualanSemua()) === jual0 && kkNG && kkNG.hargaPerLiter === 0, J([kkNG, ambilHargaTerbit()]));

// ---- 10 · barang masuk: nama wadah / kelas ditolak
var dm = drafMasukKosong(W); dm.pemasok = 'PEMASOK CONTOH'; dm.caraBayar = 'tunai';
var tolakMasuk = function (merk, harga) { return susunSimpanMasuk(Object.assign({}, dm, { baris: [{ merk: merk, jumlahKarung: '60', beratKarung: 50, hargaPerKg: harga || '12.000' }] }), W, true).tolak || ''; };
ok('barang masuk: "IR64 Apex" (nama wadah / kelas) & "IR64 Apex · Super" DITOLAK dengan kalimat; "Angsa" (wadah yang juga merek karung) BOLEH; koreksi kedatangan LAMA atas nama IR64 Apex tetap boleh; IR64 Apex tidak ditawarkan di pilihan cepat; varian dari layar Harga atas IR64 Apex ditolak',
  /nama WADAH/.test(tolakMasuk('IR64 Apex')) && /nama WADAH/.test(tolakMasuk('IR64 Apex · Super')) && !tolakMasuk('Angsa', '13.000') && hitungMasuk(drafDariKedatangan('b0')).bermasalah.length === 0 && calonMerkMasuk().indexOf('IR64 Apex') < 0
  && /nama WADAH/.test(vrSusunBuatDariHarga('IR64 Apex', 'Super', '15000', W, true).tolak || ''), J([tolakMasuk('IR64 Apex'), tolakMasuk('Angsa', '13.000'), hitungMasuk(drafDariKedatangan('b0')).bermasalah]));
// ---- 11 · ganti nama wadah: isi, karung di belakangnya & harga liter ikut; buku tidak disentuh
var kT = J(wbKomposisi('Campur Tiga').bagian); var bukuSemua = J(hitungStokKarungPerMerk()); var GN = wbSusunGantiNama('Campur Tiga', 'Wadah Tiga', W);
var lokasi = function () { return J(susunLokasi().map(function (t) { return [t.merk, B3(t.kg), B3(t.diBelakangKg), B3(t.diWadahKg)]; })); }; var lok0 = lokasi();
var karungSemua = function () { return B3(semuaKarungTerbuka().reduce(function (a, k) { return a + k.sisaMentahKg; }, 0)); }; var kr0 = karungSemua();
ok('ganti nama "Campur Tiga" → "Wadah Tiga": aturan wadah baru (posisi W3 sama, gantiNama), titik samakan isi untuk nama baru (komposisi sekarang), karung terbuka di belakangnya, harga liter 12.500 ikut; nama yang sudah dipakai wadah lain ditolak',
  !GN.tolak && GN.dokumen[0].data.daftar[2] === 'Wadah Tiga' && J(GN.dokumen[0].data.gantiNama) === J({ dari: 'Campur Tiga', ke: 'Wadah Tiga' }) && GN.dokumen.some(function (d) { return d.data.tipe === 'isi' && d.data.wadah === 'Wadah Tiga' && J(d.data.komposisi) === kT; })
  && GN.dokumen.some(function (d) { return d.data.tipe === 'karungIsi' && d.data.wadah === 'Wadah Tiga' && d.data.merk === 'NG'; }) && GN.dokumen.some(function (d) { return d.koleksi === 'katalogHargaLiteran' && d.data.id === 'Wadah Tiga' && d.data.hargaPerLiter === 12500; })
  && /sudah jadi nama wadah/.test(wbSusunGantiNama('Campur Tiga', 'Angsa', W).tolak || ''), J(GN.dokumen));
terapkanKeCache(GN.dokumen);
var GA = wbSusunGantiNama('Angsa', 'Angsa Baru', W); terapkanKeCache(GA.dokumen);
ok('ganti nama juga wadah yang karung di belakangnya dicatat CARA LAMA (tanpa kolom wadah): karung terbuka TIDAK tergandakan (tidak tertinggal di nama lama / jadi karung lepas) — total karung terbuka, tumpukan, karung & isi wadah tiap merek sama persis dengan sebelum ganti nama', karungSemua() === kr0 && lokasi() === lok0 && karungBelakang('Angsa', 'Angsa Baru').sisaKg === 50 && !semuaKarungTerbuka().some(function (k) { return k.merk === 'Angsa' && k.lokasi !== 'Angsa Baru' && k.sisaMentahKg > 0; }), J([karungSemua(), kr0, semuaKarungTerbuka()]));
ok('sesudah ganti nama: chip literan "Wadah Tiga" 12.500 dengan isi yang sama; "Campur Tiga" bukan wadah lagi tapi tetap nama kelas (ditolak barang masuk); buku semua merek byte-sama', chipL('Wadah Tiga') && chipL('Wadah Tiga').harga === 12500 && J(wbKomposisi('Wadah Tiga').bagian) === kT && !chipL('Campur Tiga') && /nama WADAH/.test(tolakMasuk('Campur Tiga')) && J(hitungStokKarungPerMerk()) === bukuSemua, J([wbKomposisi('Wadah Tiga'), kT]));
// ---- 12 · rinci karcis kasir darurat: pemecahan yang sama dengan nota Jual
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 7771, tanggal: '2026-09-19', jam: '09:30', caraBayar: 'Tunai', jenis: 'kasir_darurat_nominal', hargaTotal: 24000 } }]);
var sk = Object.assign(s0(), ikatKarcis(s0(), '7771', KINI)); var sk2 = masuk(sk, chipL('IR64 Apex', sk), 2); var PK = wbPecah('IR64 Apex', 1.64);
var RR = susunRinciDokumen(sk2, W); var rr = (RR.dokumen || []).filter(function (d) { return d.koleksi === 'penjualan' && d.data.asalDarurat; }).map(function (d) { return d.data; });
ok('rinci karcis 2 L IR64 Apex: baris internal per merek asal persis pemecah (' + PK.bagian.map(function (x) { return x.merk + ' ' + x.kg; }).join(' + ') + '), takaranId sama, tanggal & jam karcis, Σ Rp24.000; ringkas "1 barang"',
  !RR.tolak && rr.length === PK.bagian.length && J(rr.map(function (r) { return [r.merkSumber, r.totalKg]; })) === J(PK.bagian.map(function (x) { return [x.merk, x.kg]; })) && rr.every(function (r) { return r.takaranId === String(rr[0].id) && r.dariWadah === 'IR64 Apex' && r.tanggal === '2026-09-19' && r.jam === '09:30'; })
  && jumlah(rr, 'hargaTotal') === 24000 && /→ 1 barang/.test(RR.ringkas), J([rr, RR.ringkas, RR.tolak]));

// ---- ASAP DATA TOKO
var asap = null;
if (CADANGAN) {
  Object.keys(KOTAK).forEach(function (n) { pasok(n, []); }); pasok('batchMasuk', []); Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
  var WC = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
  var nutup = susunLokasi().filter(function (t) { return !(Math.abs(t.kg + t.diBelakangKg + t.diWadahKg - (t.bukuKg - t.pindahKeluarKg + t.pindahMasukKg)) < 0.011); }).map(function (t) { return t.merk; });
  var SC = hgSemua(new Date(Date.now())); var wadahC = aturWadah().daftar; var LC = wbLiteranLangsung().daftar;
  var barisL = SC.baris.filter(function (b) { return b.st.id === 'L'; }).map(function (b) { return b.merk; });
  var lSalah = barisL.filter(function (m) { return wadahC.indexOf(m) < 0 && LC.indexOf(m) < 0; });
  var lubang = SC.ringkas.find(function (r) { return r.id === 'lubang'; }).a;
  var jualW = []; var bukuAda = hitungStokKarungPerMerk();
  rakL().filter(function (c) { return c.wadahLiteran; }).forEach(function (c) {
    var st0 = J(hitungStokKarungPerMerk()); var sN = masuk(s0(), c, 1); if (sN.tolak) { jualW.push({ w: c.kunci, tolak: sN.tolak }); return; }
    var N = simpanNota(Object.assign({}, sN, { cara: 'QRIS' }), WC); var rr = jualDok(N);
    var baik = !N.tolak && rr.length >= 1 && rr.every(function (r) { return r.dariWadah === c.kunci && !!bukuAda[r.merkSumber] && r.takaranId === String(rr[0].id); }) && jumlah(rr, 'hargaTotal') === c.harga && B3(jumlah(rr, 'jumlahLiter')) === 1;
    jualW.push({ w: c.kunci, ok: baik, merk: rr.map(function (r) { return r.merkSumber; }), tolak: N.tolak || '' });
  });
  // ganti nama tiap wadah (sementara, tidak ditulis): tumpukan, karung terbuka & isi wadah tiap merek wajib sama persis (kolam karung lama tidak tergandakan)
  var lokC = function () { return J(susunLokasi().map(function (t) { return [t.merk, B3(t.kg), B3(t.diBelakangKg), B3(t.diWadahKg)]; })); }; var lokC0 = lokC();
  var gantiGeser = wadahC.filter(function (Wn) { var R = wbSusunGantiNama(Wn, Wn + ' (uji)', WC); return R.tolak || denganCacheSementara(R.dokumen, lokC) !== lokC0; });
  // hapus semua harga liter yang tidak dipakai (NG & Kumala di cadangan 27 Sep): riwayat terbit & nota byte-sama; katalog kasir cuma berubah di harga liter itu (jadi 0)
  var terbitC = J(ambilHargaTerbit()), jualC = J(ambilPenjualanSemua()); var kk0 = kkIsi(); var hapusNama = hgLiteran(hgSemua(new Date(Date.now()))).tidakDipakai.map(function (x) { return x.merk; });
  hapusNama.forEach(function (m) { var r = susunHapusLiter(m, WC, true); if (!r.tolak) terapkanKeCache((r.dokumen || []).concat(r.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; }))); });
  var kk1 = kkIsi(); var kkBeda = kk1.merkKarung.filter(function (m) { var a = kk0.merkKarung.find(function (x) { return x.merk === m.merk; }); var b = Object.assign({}, a || {}); if (hapusNama.indexOf(m.merk) >= 0) b.hargaPerLiter = 0; return J(b) !== J(m); }).map(function (m) { return m.merk; });
  // tanpa harga liter yang tidak dipakai (cadangan 28 Sep: semua terpakai) tidak ada yang bisa dihapus — lulus hampa, yang dijaga cuma daftarnya memang nol
  var hapusOk = hapusNama.length ? (J(ambilHargaTerbit()) === terbitC && J(ambilPenjualanSemua()) === jualC && !kkBeda.length && J(kk1.kemasan) === J(kk0.kemasan) && kk1.merkKarung.length === kk0.merkKarung.length && hgLiteran(hgSemua(new Date(Date.now()))).tidakDipakai.length === 0) : hgLiteran(hgSemua(new Date(Date.now()))).tidakDipakai.length === 0;
  asap = { menutupGagal: nutup, nNama: susunLokasi().length, lSalah: lSalah, barisL: barisL.length, lubang: lubang, langsung: LC, wadah: wadahC.length, jualW: jualW, gantiGeser: gantiGeser, hapusNama: hapusNama, hapusOk: hapusOk, kkBeda: kkBeda };
}
print(J({ lulus: lulus, gagal: gagal, asap: asap }));
"""

# ASAP GLOBAL: angka laporan (omzet, laba, neraca) SEMUA BULAN — kode cabang vs kode main, di atas cadangan toko yang sama
GLOBAL = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(Date.now()); var bulan = daftarBulan(kini, 36).map(function (b) { return b.key || b; });
var akhirBulan = function (k) { var d = new Date(Number(k.slice(0, 4)), Number(k.slice(5, 7)), 0); return k + '-' + String(d.getDate()).padStart(2, '0'); };
var out = { bulan: bulan, laba: bulan.map(function (k) { return labaBulan(k, kini); }), inti: bulan.map(function (k) { return intiBulan(k, kini); }), neraca: bulan.map(function (k) { return neracaPada(akhirBulan(k), kini); }),
  neracaKini: hitungNeraca(), omzet: rekapOmzet(kini), labaMesin: bulan.map(function (k) { return hitungLabaBersihRentang(k + '-01', akhirBulan(k)); }) };
print(JSON.stringify(out));
"""


def cadangan_toko():
    c = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')), key=os.path.basename)
    return c[-1] if c else None


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def cad_js(p):
    d = json.load(open(p, encoding='utf-8')); kol = re.findall(r"\{ nama: '(\w+)'", open(os.path.join(AKAR, 'baru/js/data/koleksi.js'), encoding='utf-8').read())
    return json.dumps(dict((n, d[n]) for n in kol if isinstance(d.get(n), list))), os.path.basename(p).split('miqbal-')[-1][:10]


def utama(js, pakai_cadangan):
    cad = 'null'; tgl = ''
    p = cadangan_toko() if pakai_cadangan else None
    if p: cad, tgl = cad_js(p)
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    return h['lulus'], h['gagal'], h.get('asap')


def asap_global(p):
    """Laporan semua bulan dengan kode CABANG vs kode MAIN (git archive) — harus byte-sama. → (sama, keterangan)."""
    cad, tgl = cad_js(p); jam = "var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl
    tmp = tempfile.mkdtemp(prefix='main-')
    try:
        r = subprocess.run(['git', '-C', AKAR, 'archive', '--format=tar', 'main', 'baru/js'], capture_output=True)
        if r.returncode != 0: return None, 'git archive main gagal: ' + r.stderr.decode('utf-8', 'replace')[-200:]
        with tarfile.open(fileobj=io.BytesIO(r.stdout)) as tf: tf.extractall(tmp)
        modul = uji_laporan_baru.MODUL
        cabang, e1 = jalan(jam + bundel_baru.bundel(modul) + '\nvar CAD = ' + cad + ';\n' + GLOBAL)
        utama_ = [os.path.join(tmp, m) for m in modul if os.path.exists(os.path.join(tmp, m))]
        main, e2 = jalan(jam + bundel_baru.bundel(utama_) + '\nvar CAD = ' + cad + ';\n' + GLOBAL)
        if cabang is None or main is None: return None, 'JSC JATUH: ' + (e1 or e2)[-300:]
        beda = [k for k in cabang if json.dumps(cabang[k], sort_keys=True) != json.dumps(main.get(k), sort_keys=True)]
        return not beda, '%d bulan (%s … %s), laba/inti/neraca/omzet%s' % (len(cabang['bulan']), cabang['bulan'][0] if cabang['bulan'] else '-', cabang['bulan'][-1] if cabang['bulan'] else '-', (' · BEDA: ' + ', '.join(beda)) if beda else '')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


RUSAK = {
    'pecahan tidak sebanding komposisi (semua ke merek pertama)': ("const k = i === pos.length - 1 ? wbB3(ambil - jalan) : wbB3(ambil * x.kg / adaKg);", "const k = i === 0 ? ambil : 0;"),
    'nota tidak memecah literan wadah (satu baris, satu merek)': ("const items = pecahItemsWadah(s.keranjang.map((b) => Object.assign({}, b.trx)), s);", "const items = s.keranjang.map((b) => Object.assign({}, b.trx));"),
    'modal wadah = modal merek pertama (bukan rata-rata tertimbang)': ("if (kg > 0) return K.positif.reduce((a, x) => a + x.kg * hpp(x.merk), 0) / kg;", "if (kg > 0) return hpp(K.positif[0].merk);"),
    'sisa pembulatan rupiah tidak ke baris terakhir (Σ tidak persis)': ("r.hargaTotal = akhir ? t.hargaTotal - rp : Math.round(t.hargaTotal * x.kg / kgTot);", "r.hargaTotal = Math.round(t.hargaTotal * x.kg / kgTot);"),
    'takar tidak menambah bagian merek asal (isi jadi milik nama wadah)': ("tambah(t.bukuAsal ? String(x.merk || '') : String(W), Number(x.kg) || 0)", "tambah(String(W), Number(x.kg) || 0)"),
    'katalog menagih harga liter merek yang cuma lewat wadah': ("Object.keys(stokMerekSaja(stokK)).filter((m) => !ukuranBuku[m]).forEach((m) => { if (bolehL(m)) tambah(m, 'L'); tambah(m, 'S'); });", "Object.keys(stokMerekSaja(stokK)).filter((m) => !ukuranBuku[m]).forEach((m) => { tambah(m, 'L'); tambah(m, 'S'); });"),
    'katalog mengabaikan merek literan langsung (tanpa harga tidak ditagih)': ("const langsung = wbLiteranLangsung().daftar; const bolehL", "const langsung = []; const bolehL"),
    'nama kelas lolos di barang masuk': ("kelas[merk.split(' \\u00b7 ')[0]] && !namaLama[merk] ?", "false ?"),
    'ganti nama wadah tidak membawa isi': ("  else if (K.diketahui) dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: B, tipe: 'isi'", "  else if (false) dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: B, tipe: 'isi'"),
    'ganti nama wadah tanpa harga liter (chip hilang dari rak)': ("if (hL && Number(hL.hargaPerLiter) > 0 && !hB) dokumen.push(", "if (false) dokumen.push("),
    'struk memecah satu takaran jadi beberapa baris': ("gabungTakaran(nota.baris).forEach((p) => {   // putaran 27", "nota.baris.forEach((p) => {   // putaran 27"),
    'rinci karcis tidak memecah literan wadah': ("pecahItemsWadah(s.keranjang.map((b) => Object.assign({}, b.trx)), s).forEach((t) => {", "s.keranjang.map((b) => Object.assign({}, b.trx)).forEach((t) => {"),
    'langit-langit literan wadah mengabaikan buku merek asal': ("const kg = tot > 0 ? Math.min.apply(null, K.positif.map((x) => bebasBuku(x.merk) / (x.kg / tot))) : bebasBuku(wbMerkCadangan(W));", "const kg = 999999;"),
    'kelebihan dari isi wadah hilang (tidak dipotong dari karung di belakang)': ("if (lewat > 0) { const m = wbMerkCadangan(W);", "if (false) { const m = wbMerkCadangan(W);"),
    'baris internal tanpa pengikat takaranId': ("    if (t._takaran) d.takaranId = takaranPertama[t._takaran] || (takaranPertama[t._takaran] = String(d.id));   // pengikat baris internal satu takaran (struk menggabung)", ""),
    'modal baris internal dibagi rata dari modal wadah (bukan merek asal)': ("r.hppTotalSaatJual = Math.round(x.kg * ((stok[x.merk] || {}).hppTerakhirPerKg || 0))", "r.hppTotalSaatJual = Math.round(t.hppTotalSaatJual * x.kg / kgTot)"),
    'ganti nama wadah meninggalkan kolam karung lama (terhitung dua kali)': ("  sesudah.forEach((k) => { if (k.lokasi === B) return;", "  [].forEach((k) => { if (k.lokasi === B) return;"),
    'hapus harga liter tanpa ketukan kedua': ("if (!yakin) return { tolak: 'Hapus harga liter '", "if (false) return { tolak: 'Hapus harga liter '"),
    'harga liter wadah yang masih dipakai rak ikut bisa dihapus': ("const x = hgLiteran(S).tidakDipakai.find((t) => t.merk === m);", "const x = { merk: m, harga: 0 };"),
    'hapus harga liter membuang semua draf': ("if (draf[k] !== undefined) { const d = Object.assign({}, draf); delete d[k]; dokumen.push(hgDokDraf(d, w)); }", "if (draf[k] !== undefined) dokumen.push(hgDokDraf({}, w));"),
    'Papan Kapur menghitung baris internal sebagai barang terpisah': ("if (!p.takaranId || !takaran[p.takaranId]) o.n += 1;", "o.n += 1;"),
}

if __name__ == '__main__':
    js = uji_kunci_periode.satu_lingkup(bundel_baru.bundel(MODUL))   # putaran 30: teksMargin stok-hpp vs harga-logika
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, (a, b) in RUSAK.items():
            if js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g, _ = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    print('WADAH BERNAMA (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    p = cadangan_toko()
    if asap:
        baik = [x for x in asap['jualW'] if x.get('ok')]
        print('ASAP DATA TOKO (%s): identitas menutup %d/%d nama · %d baris harga liter (%d wadah + literan langsung %s) · liter di luar wadah/langsung: %s · belum ada harga %d · 1 L dari tiap wadah berharga lewat jalur baru: %d/%d (%s) · ganti nama tiap wadah tanpa menggeser tumpukan/karung/isi: %d/%d · hapus harga liter tidak dipakai (%s): riwayat terbit & nota byte-sama, katalog kasir cuma harga liter itu jadi 0: %s'
              % (os.path.basename(p), asap['nNama'] - len(asap['menutupGagal']), asap['nNama'], asap['barisL'], asap['wadah'], ', '.join(asap['langsung']) or '-', ', '.join(asap['lSalah']) or 'tidak ada', asap['lubang'], len(baik), len(asap['jualW']),
                 '; '.join(x['w'] + ' → ' + ' + '.join(x.get('merk') or []) for x in asap['jualW']), asap['wadah'] - len(asap['gantiGeser']), asap['wadah'], ', '.join(asap['hapusNama']) or 'tidak ada yang tidak dipakai', asap['hapusOk']))
        if asap['menutupGagal'] or asap['lSalah'] or len(baik) != len(asap['jualW']) or not asap['jualW'] or asap['gantiGeser'] or not asap['hapusOk']: g.append('asap data toko: ' + json.dumps(asap, ensure_ascii=False)[:400])
    if p:
        sama, ket = asap_global(p)
        print('ASAP GLOBAL (kode main vs cabang, %s): %s — %s' % (os.path.basename(p), 'BYTE-SAMA' if sama else 'BEDA / GAGAL', ket))
        if not sama: g.append('asap global: ' + ket)
    sys.exit(2 if g else 0)
