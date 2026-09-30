#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_cocokkan_terpisah.py — putaran 27 Bagian 1: COCOKKAN DIPISAH (owner 27 Sep: "masing-masing stok punya aturannya sendiri").
  · Tumpukan gudang: karung utuh 50 / 25 kg per nama; tercatat = buku − karung terbuka − bagian nama itu di wadah; selisih → penyesuaianStok
    {bagian 'tumpukan'} dengan kgSistem/kgFisik = buku sebelum/sesudah. Wadah & karung terbuka tidak bergeser.
  · Wadah literan: isi kotak (takar / liter / kg) + karung terbuka di belakangnya; selisih isi dibagi ke MEREK ASAL menurut komposisi tercatat,
    selisih karung = merek karung itu; susut di bawah batas owner (Aturan wadah, kg per wadah per hari × hari sejak disamakan) = wajar tanpa alasan,
    di atasnya wajib alasan; isi ulang yang lupa dicatat ditawarkan dicatat dulu; hitungan pertama = titik awal tanpa selisih. Tumpukan tidak bergeser.
  · Papan Kapur: cocokkan tumpukan & cocokkan wadah = dua kejadian berbeda. Mesin beku tidak disentuh (buku lewat penyesuaianStok yang sama).
KOTAK PASIR (ANGKA CONTOH), jam dikunci 19 Sep 2026 10:00 WIB. Kalau ada cadangan toko di _privat/: semua wadah & tumpukan dicocokkan di data toko,
rantai stok diperiksa sebelum/sesudah.

    python3 alat-uji/uji_cocokkan_terpisah.py            → N lulus · 0 gagal
    python3 alat-uji/uji_cocokkan_terpisah.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_stok_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_stok_baru.MODUL
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def baris(merk, n, harga, berat=50):
    return {'id': str(n), 'merk': merk, 'satuan': 'karung', 'beratKarung': berat, 'jumlahKarung': n, 'totalKg': n * berat, 'hargaPerKg': harga, 'subtotalHarga': n * berat * harga}


KOTAK = {
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-09-10', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
                  'merkList': [baris('Angsa', 20, 13000), baris('NG', 10, 14400), baris('Kumala', 10, 14000), baris('IR64 Apex', 6, 14300)]}],
  'wadahLiteran': [
    {'id': 1, 'tanggal': '2026-09-10', 'jam': '08:00', 'tipe': 'atur', 'penuhKg': 50, 'puncakKg': 60, 'isiUlangKg': 10, 'takarKg': 1.8, 'susutWajarKg': 1, 'daftar': ['IR64 Apex', 'Angsa'], 'resep': {}},
    # W1 "IR64 Apex" = nama wadah; isinya dua merek asal (komposisi putaran 27), karung NG di belakangnya tinggal 20 kg
    {'id': 2, 'tanggal': '2026-09-17', 'jam': '09:00', 'tipe': 'karung', 'merk': 'NG', 'kg': 50, 'wadah': 'IR64 Apex'},
    {'id': 3, 'tanggal': '2026-09-17', 'jam': '10:00', 'tipe': 'karungIsi', 'merk': 'NG', 'isiKg': 20, 'wadah': 'IR64 Apex'},
    {'id': 4, 'tanggal': '2026-09-17', 'jam': '10:00', 'wadah': 'IR64 Apex', 'tipe': 'isi', 'isiKg': 40, 'komposisi': {'NG': 30, 'Kumala': 10}},
    # W2 "Angsa": titik samakan LAMA (tanpa komposisi) = seluruh isi milik nama wadah; karung Angsa utuh di belakangnya
    {'id': 5, 'tanggal': '2026-09-17', 'jam': '09:30', 'tipe': 'karung', 'merk': 'Angsa', 'kg': 50, 'wadah': 'Angsa'},
    {'id': 6, 'tanggal': '2026-09-17', 'jam': '10:00', 'wadah': 'Angsa', 'tipe': 'isi', 'isiKg': 30}],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var KINI = new Date(Date.now()); var s = keadaanAwal();
var nId = 9000; var W = function (jam) { return { tanggal: '2026-09-19', jam: jam || '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } }; };
var buku = function (m) { return (hitungStokKarungPerMerk()[m] || {}).sisaKg; };
var tumpuk = function (m) { return tumpukanGudang(m).kg; };
var hampir = function (a, b) { return Math.abs(a - b) < 0.011; };
var baris = function (tab, H, A, Y) { return susunCocok(tab, H || {}, A || {}, Y || {}); };
var wd = function (r, nama) { return r.baris.find(function (b) { return b.nama === nama; }); };

// ---- 1 · daftar: tumpukan per nama & wadah per petak
var T0 = barangCocok('tumpukan'); var bAngsa = T0.find(function (b) { return b.nama === 'Angsa'; }); var bNG = T0.find(function (b) { return b.nama === 'NG'; });
ok('tumpukan: tercatat = buku − karung terbuka − bagian di wadah (Angsa 1000 − 50 − 30 = 920; NG 500 − 20 − 30 = 450; Kumala 500 − 10 = 490; IR64 Apex 300 — nama wadah tapi isinya merek lain)',
  bAngsa.sistem === 920 && bAngsa.buku === 1000 && bNG.sistem === 450 && T0.find(function (b) { return b.nama === 'Kumala'; }).sistem === 490 && T0.find(function (b) { return b.nama === 'IR64 Apex'; }).sistem === 300 && bAngsa.beratKarung === 50 && bAngsa.karungSistem === 18,
  J(T0.map(function (b) { return b.nama + ':' + b.sistem + '/' + b.buku; })));
var W0 = barangCocok('wadah'); var w1 = W0[0], w2 = W0[1];
ok('wadah: W1 IR64 Apex isi 40 kg (NG 30 + Kumala 10) + karung NG 20 kg · modal isi = tertimbang (30×14.400 + 10×14.000)/40 = 14.300; W2 Angsa isi 30 kg (titik lama = milik nama wadah) + karung Angsa 50 kg',
  w1.no === 'W1' && w1.nama === 'IR64 Apex' && w1.isiSistem === 40 && w1.karungNama === 'NG' && w1.karungSistem === 20 && J(w1.komposisi) === J([{ merk: 'NG', kg: 30 }, { merk: 'Kumala', kg: 10 }]) && Math.abs(w1.modal - 14300) < 0.001
  && w2.isiSistem === 30 && J(w2.komposisi) === J([{ merk: 'Angsa', kg: 30 }]) && w2.karungNama === 'Angsa' && w2.karungSistem === 50, J(W0));
// ---- 2 · susut wajar (1 kg × 2 hari sejak 17 Sep) tidak minta alasan; selisih dibagi ke merek asal 30 : 10
var H = {}; H['wadah|IR64 Apex'] = '38,5'; H['wadahKarung|IR64 Apex'] = '20';
var r2 = baris('wadah', H); var b2 = wd(r2, 'IR64 Apex');
ok('wadah −1,5 kg dalam 2 hari (batas 1 kg/hari → 2 kg) = SUSUT TAKAR WAJAR, tidak minta alasan; selisih dibagi ke merek asal menurut komposisi: NG −1,12 · Kumala −0,38; rupiah = Σ kg × modal tiap merek',
  b2.ada && b2.wajar === true && b2.besar === false && b2.perluAlasan === false && b2.wajarKg === 2 && b2.lamaHari === 2 && b2.selisih === -1.5 && b2.alokasi.NG === -1.12 && b2.alokasi.Kumala === -0.38 && b2.rp === Math.round(-1.12 * 14400 - 0.38 * 14000) && r2.susutRp === b2.rp, J(b2));
// ---- 3 · di atas batas → wajib alasan
var H3 = {}; H3['wadah|IR64 Apex'] = '36'; var r3 = baris('wadah', H3); var b3 = wd(r3, 'IR64 Apex');
ok('wadah −4 kg (di atas 2 kg wajar) → DITANDAI, alasan wajib; simpan ditolak menyebut wadahnya & batasnya', b3.besar && b3.perluAlasan && !b3.wajar && /wadah IR64 Apex selisih -4 kg, di atas susut wajar 2 kg/.test(r3.tolak), J([b3.selisih, r3.tolak]));
var A3 = {}; A3['wadah|IR64 Apex'] = 'tumpah'; ok('dengan alasan, penolakan tinggal "yang belum dihitung" (dua ketukan)', baris('wadah', H3, A3).perluYakin === 'sebagian' && !baris('wadah', H3, A3, { sebagian: true }).tolak);
// ---- 4 · simpan cocokkan wadah: penyesuaianStok per merek asal + titik samakan berkomposisi + karung; rantai stok tidak bergeser
var tNG0 = tumpuk('NG'), tKu0 = tumpuk('Kumala'), tAn0 = tumpuk('Angsa'), bNG0 = buku('NG'), bKu0 = buku('Kumala');
var S4 = susunSimpanCocok('wadah', H, {}, W('10:00'), { sebagian: true });
var dP = (S4.dokumen || []).filter(function (d) { return d.koleksi === 'penyesuaianStok'; }); var dI = (S4.dokumen || []).filter(function (d) { return d.koleksi === 'wadahLiteran' && d.data.tipe === 'isi'; }); var dK = (S4.dokumen || []).filter(function (d) { return d.koleksi === 'wadahLiteran' && d.data.tipe === 'karungIsi'; });
ok('simpan wadah: DUA penyesuaianStok (Kumala, NG) {bagian wadah, wadah IR64 Apex, kgSistem/kgFisik = buku sebelum/sesudah, nilaiRp dikunci} + titik samakan {isiKg 38,5, komposisi NG 28,88 + Kumala 9,62, dariCocok} + karung NG 20 kg; alasan bawaan "Susut takar wajar"',
  !S4.tolak && dP.length === 2 && dP.every(function (d) { return d.data.bagian === 'wadah' && d.data.wadah === 'IR64 Apex' && d.data.alasan === 'Susut takar wajar' && hampir(d.data.kgFisik - d.data.kgSistem, d.data.selisihKg); })
  && dP.find(function (d) { return d.data.merk === 'NG'; }).data.selisihKg === -1.12 && dP.find(function (d) { return d.data.merk === 'NG'; }).data.nilaiRp === Math.round(-1.12 * 14400) && dP.find(function (d) { return d.data.merk === 'Kumala'; }).data.kgSistem === 500
  && dI.length === 1 && dI[0].data.isiKg === 38.5 && J(dI[0].data.komposisi) === J({ NG: 28.88, Kumala: 9.62 }) && dI[0].data.dariCocok === true && dK.length === 1 && dK[0].data.merk === 'NG' && dK[0].data.isiKg === 20 && dK[0].data.wadah === 'IR64 Apex', J(S4));
terapkanKeCache(S4.dokumen || []);
ok('sesudah cocokkan wadah: buku NG −1,12 & Kumala −0,38 (mesin beku membaca selisihKg); isi W1 = 38,5 kg = hitungan; TUMPUKAN NG, Kumala, Angsa TIDAK bergeser (identitas rantai stok)',
  hampir(buku('NG'), bNG0 - 1.12) && hampir(buku('Kumala'), bKu0 - 0.38) && wbKomposisi('IR64 Apex').totalKg === 38.5 && hampir(tumpuk('NG'), tNG0) && hampir(tumpuk('Kumala'), tKu0) && hampir(tumpuk('Angsa'), tAn0),
  J([buku('NG'), buku('Kumala'), tumpuk('NG'), tNG0, tumpuk('Kumala'), tKu0, wbKomposisi('IR64 Apex')]));
// ---- 5 · papan kapur: kejadian WADAH
var K5 = susunKapur(KINI).baris;
ok('papan kapur: "Cocokkan wadah IR64 Apex → buku NG …" dan "Cocokkan wadah IR64 Apex: isinya dihitung (NG … + Kumala …)" — jenis wadah, BUKAN cocokkan biasa',
  K5.some(function (x) { return x.jenis === 'wadah' && /^Cocokkan wadah IR64 Apex → buku NG 500 kg → 498,9 kg · Susut takar wajar$/.test(x.isi) && x.n === '−1,1 kg'.replace('−', '-'); })
  && K5.some(function (x) { return x.jenis === 'wadah' && /^Cocokkan wadah IR64 Apex: isinya dihitung \(NG 28,9 kg \+ Kumala 9,6 kg\)$/.test(x.isi); }) && !K5.some(function (x) { return /^Cocokkan NG/.test(x.isi); }), J(K5));
// ---- 6 · cocokkan TUMPUKAN: karung utuh; buku ikut, wadah & karung terbuka tidak
var H6 = {}; H6['tumpukan|Angsa'] = '900'; var r6 = baris('tumpukan', H6); var b6 = r6.baris.find(function (b) { return b.nama === 'Angsa'; });
ok('tumpukan Angsa: tercatat 920, dihitung 18 karung = 900 → −20 kg (2,2 % < 3 %: tanpa alasan) = −20 × 13.000', b6.selisih === -20 && !b6.perluAlasan && b6.rp === -260000, J(b6));
var wA0 = wbKomposisi('Angsa').totalKg, kA0 = karungBelakang('Angsa', 'Angsa').sisaKg;
var S6 = susunSimpanCocok('tumpukan', H6, {}, W('10:02'), { sebagian: true }); var d6 = S6.dokumen && S6.dokumen[0] && S6.dokumen[0].data;
ok('simpan tumpukan: penyesuaianStok {merk Angsa, kgSistem 1000 (buku), kgFisik 980, selisihKg −20, bagian tumpukan, bagianSistemKg 920, bagianFisikKg 900}', !S6.tolak && !!S6.dokumen && S6.dokumen.length === 1 && d6.merk === 'Angsa' && d6.kgSistem === 1000 && d6.kgFisik === 980 && d6.selisihKg === -20 && d6.bagian === 'tumpukan' && d6.bagianSistemKg === 920 && d6.bagianFisikKg === 900 && d6.nilaiRp === -260000, J(S6));
terapkanKeCache(S6.dokumen || []);
ok('sesudah cocokkan tumpukan: buku Angsa 980, tumpukan = 900 persis hitungan; isi wadah Angsa & karung terbuka Angsa TIDAK berubah', buku('Angsa') === 980 && hampir(tumpuk('Angsa'), 900) && wbKomposisi('Angsa').totalKg === wA0 && karungBelakang('Angsa', 'Angsa').sisaKg === kA0, J([buku('Angsa'), tumpuk('Angsa')]));
ok('papan kapur: "Cocokkan tumpukan gudang Angsa · tercatat 920 kg → dihitung 900 kg · buku 1000 kg → 980 kg" (kejadian tumpukan, terpisah dari wadah)', susunKapur(KINI).baris.some(function (x) { return x.jenis === 'opname' && /^Cocokkan tumpukan gudang Angsa · tercatat 920 kg → dihitung 900 kg · buku 1000 kg → 980 kg$/.test(x.isi); }), J(susunKapur(KINI).baris));
// ---- 7 · tumpukan di atas batas % → alasan
var H7 = {}; H7['tumpukan|Angsa'] = '830'; var b7 = baris('tumpukan', H7).baris.find(function (b) { return b.nama === 'Angsa'; });
ok('tumpukan −70 kg dari 900 (7,8 % > 3 %) → alasan wajib', b7.besar && b7.perluAlasan && b7.selisih === -70);
// ---- 8 · isi ulang yang lupa dicatat: wadah lebih, karung kurang → ditawarkan dicatat sebagai takar dulu
var H8 = {}; H8['wadah|Angsa'] = '35,4'; H8['wadahKarung|Angsa'] = '44,6'; var b8 = wd(baris('wadah', H8), 'Angsa');
ok('wadah Angsa +5,4 kg & karung Angsa −5,4 kg → "isi ulang lupa dicatat": ditawarkan 3 takar (5,4 ÷ 1,8)', b8.lupaTakar === 3 && b8.lupaKg === 5.4 && b8.dIsi === 5.4 && b8.dKr === -5.4, J(b8));
var TK8 = susunTakarWadah('Angsa', [{ merk: 'Angsa', takar: 3, dari: 'Angsa' }], W('10:03'), s); terapkanKeCache(TK8.dokumen || []);
var b8b = wd(baris('wadah', H8), 'Angsa');
ok('sesudah takar yang lupa dicatat: hitungan yang sama jadi COCOK (selisih 0, tidak ada buku yang disesuaikan)', !TK8.tolak && b8b.selisih === 0 && Object.keys(b8b.alokasi).length === 0 && b8b.lupaTakar === 0, J([TK8.tolak, b8b]));
// ---- 9 · wadah tercatat minus (literan terjual melebihi isi) → ditawarkan juga
pasok('penjualan', [{ id: 'j9', tanggal: '2026-09-19', jam: '10:04', jenis: 'literan', merkSumber: 'Angsa', namaProduk: 'Angsa', totalKg: 40, jumlahLiter: 48.8, hargaTotal: 1, hppTotalSaatJual: 1, caraBayar: 'Tunai' }]);
var b9 = wd(baris('wadah', {}), 'Angsa'); var b9h = wd(baris('wadah', { 'wadah|Angsa': '0' }), 'Angsa');
ok('wadah tercatat MINUS (35,4 − 40 = −4,6 kg) → ditawarkan isi ulang yang lupa dicatat (3 takar)', b9.isiSistem === -4.6 && b9h.lupaTakar === 3, J([b9.isiSistem, b9h.lupaTakar]));
pasok('penjualan', []);
// ---- 10 · hitungan PERTAMA: wadah belum pernah disamakan → titik awal, tanpa penyesuaian buku
terapkanKeCache(susunAturWadah({ penuhKg: '50', puncakKg: '60', isiUlangKg: '10', takarKg: '1,8', daftar: ['IR64 Apex', 'Angsa', 'IR42 Value'] }, W('10:05')).dokumen);
terapkanKeCache(susunBukaKarung('Kumala', W('10:05'), 'IR42 Value').dokumen);
var bKu10 = buku('Kumala'); var H10 = {}; H10['wadah|IR42 Value'] = '25'; var b10 = wd(baris('wadah', H10), 'IR42 Value');
var S10 = susunSimpanCocok('wadah', H10, {}, W('10:06'), { sebagian: true });
ok('hitungan pertama wadah IR42 Value (belum pernah ditandai): tanpa selisih, TANPA penyesuaianStok; titik samakan berkomposisi = karung di belakangnya (Kumala 25 kg — nama wadahnya tidak ada di buku)',
  b10.pertama === true && b10.isiSistem === null && b10.selisih === 0 && !S10.tolak && (S10.dokumen || []).filter(function (d) { return d.koleksi === 'penyesuaianStok'; }).length === 0 && J((S10.dokumen.find(function (d) { return d.data.tipe === 'isi'; }) || { data: {} }).data.komposisi) === J({ Kumala: 25 }), J([b10, S10]));
terapkanKeCache(S10.dokumen || []); ok('sesudah hitungan pertama: buku Kumala tetap; 25 kg Kumala kini tercatat di wadah IR42 Value', buku('Kumala') === bKu10 && wbKomposisi('IR42 Value').bagian.Kumala === 25);
// ---- 11 · batas susut wajar diatur owner (Aturan wadah)
var H11 = {}; H11['wadah|IR64 Apex'] = '37,7'; var b11a = wd(baris('wadah', H11), 'IR64 Apex');
var AT = susunAturWadah({ penuhKg: '50', puncakKg: '60', isiUlangKg: '10', takarKg: '1,8', susutWajarKg: '0,5', daftar: ['IR64 Apex', 'Angsa', 'IR42 Value'] }, W('10:07'));
terapkanKeCache(AT.dokumen); var b11b = wd(baris('wadah', H11), 'IR64 Apex');
ok('batas owner: −0,8 kg hari ini wajar dengan 1 kg/hari, jadi DI ATAS batas sesudah owner menyetel 0,5 kg/hari (dokumen atur membawa susutWajarKg 0,5; kabar menyebutnya); 11 kg ditolak',
  b11a.wajar && !b11a.besar && AT.dokumen[0].data.susutWajarKg === 0.5 && /susut wajar ≤ 0,5 kg\/wadah\/hari/.test(AT.patch.kabar) && b11b.besar && b11b.wajarKg === 0.5 && !!susunAturWadah({ penuhKg: '50', isiUlangKg: '10', susutWajarKg: '11', daftar: ['A'] }, W()).tolak, J([b11a.wajarKg, b11b.wajarKg]));
// ---- 12 · draf lama bertab "beras"
ok('draf hitungan lama bertab "beras" dibuka di tab tumpukan; urutan tab baru = tumpukan · wadah · kemasan · kantong', tabCocokSah('beras') === 'tumpukan' && tabCocokSah('wadah') === 'wadah' && J(TAB_COCOK.map(function (x) { return x[0]; })) === J(['tumpukan', 'wadah', 'kemasan', 'kantong']));
// ---- 13 · "Mana yang belum dicocokkan?": cocokkan wadah menghitung bagian di wadah saja — umur cocokkan nama itu tidak berubah
var G13 = susunGudang('cocok', KINI).jawab.baris;
ok('belum dicocokkan: NG (cuma bagian wadahnya yang dihitung) tetap "belum pernah"; Angsa (tumpukan dihitung) 0 hari', G13.find(function (x) { return x.nama === 'NG'; }).n === 'belum pernah' && G13.find(function (x) { return x.nama === 'Angsa'; }).n === '0 hari', J(G13));
// ---- 14 · penjaga ganda: wadah yang baru disamakan < 10 menit
var H14 = {}; H14['wadah|IR64 Apex'] = '38'; var A14 = {}; A14['wadah|IR64 Apex'] = 'hitung lagi'; var S14 = susunSimpanCocok('wadah', H14, A14, W('10:08'), { sebagian: true });
ok('wadah IR64 Apex dihitung lagi 8 menit sesudah dicocokkan → ditanya dulu (ganda)', S14.perluYakin === 'ganda' && /baru saja dicocokkan/.test(S14.tolak), J(S14.tolak));
// ---- 15 · karung terbuka dihitung beda → buku merek karung + titik samakan karung, tumpukan tetap
var kr15 = karungBelakang('Angsa', 'Angsa').sisaKg; var tA15 = tumpuk('Angsa'); var bA15 = buku('Angsa'); var H15 = {}; H15['wadahKarung|Angsa'] = String(kr15 - 1); var A15 = {}; A15['wadah|Angsa'] = 'karung robek';
var S15 = susunSimpanCocok('wadah', H15, A15, W('10:30'), { sebagian: true, ganda: true }); terapkanKeCache(S15.dokumen || []);
ok('karung Angsa di belakang wadah dihitung 1 kg kurang → buku Angsa −1, karung terbuka = hitungan, tumpukan Angsa tetap', !S15.tolak && hampir(karungBelakang('Angsa', 'Angsa').sisaKg, kr15 - 1) && hampir(buku('Angsa'), bA15 - 1) && hampir(tumpuk('Angsa'), tA15), J([S15.tolak, kr15, karungBelakang('Angsa', 'Angsa').sisaKg, buku('Angsa'), bA15]));

// ---- ASAP DATA TOKO: tiap wadah yang isinya diketahui dicocokkan (isi −0,5 kg, karung = tercatat), lalu tiap tumpukan = karung utuh; rantai stok diperiksa
var asap = null;
if (CADANGAN) {
  Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
  var WC = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
  var semua = Object.keys(hitungStokKarungPerMerk()); var tSebelum = {}, bSebelum = {}; semua.forEach(function (m) { tSebelum[m] = tumpuk(m); bSebelum[m] = buku(m); });
  var kbBeda = []; aturWadah().daftar.forEach(function (w) { wbKarungBelakangWadah(w).forEach(function (k) { if (k.diketahui && Math.abs(k.selisihKg) > 0.05) kbBeda.push(k.merk + ' di belakang ' + w + ': catatan ' + k.kolamKg + ' vs buku ' + k.bukuKg); }); });
  var HW = {}, AW = {}; var dihitungW = {}; barangCocok('wadah').forEach(function (b) { if (b.isiSistem === null) return; var isi = Math.max(0, Math.round((b.isiSistem - 0.5) * 100) / 100); HW[b.kunci] = String(isi); dihitungW[b.nama] = isi; if (b.karungSistem !== null) HW[b.kunciKarung] = String(b.karungSistem); AW[b.kunci] = 'uji asap'; });
  var SW = susunSimpanCocok('wadah', HW, AW, WC, { sebagian: true, ganda: true, aneh: true, susutPositif: true });
  var selPer = {}; (SW.dokumen || []).forEach(function (d) { if (d.koleksi === 'penyesuaianStok') selPer[d.data.merk] = (selPer[d.data.merk] || 0) + d.data.selisihKg; });
  terapkanKeCache(SW.dokumen || []);
  // 39b no. 5: buku KHUSUS (karung belakang dkk.) tidak punya tumpukan — catatan karungnya kini disamakan ke BUKU, jadi "tumpukan"-nya memang bergerak
  var bwA = petaBukuWadah(); var geserW = semua.filter(function (m) { return !bwA[m] && !hampir(tumpuk(m), tSebelum[m]); }); var bukuSalah = semua.filter(function (m) { return !hampir(buku(m) - bSebelum[m], selPer[m] || 0); });
  var isiSalah = Object.keys(dihitungW).filter(function (w) { return !hampir(wbKomposisi(w).totalKg, dihitungW[w]); });
  var HT = {}, AT2 = {}, dihitungT = {}; barangCocok('tumpukan').forEach(function (b) { if (!(b.sistem > 0)) return; var n = Math.floor(b.sistem / 50) * 50; HT[b.kunci] = String(n); AT2[b.kunci] = 'uji asap'; dihitungT[b.nama] = n; });
  var isiW2 = {}; Object.keys(dihitungW).forEach(function (w) { isiW2[w] = wbKomposisi(w).totalKg; });
  var ST2 = susunSimpanCocok('tumpukan', HT, AT2, WC, { sebagian: true, ganda: true, aneh: true, susutPositif: true }); terapkanKeCache(ST2.dokumen || []);
  var tumpukSalah = Object.keys(dihitungT).filter(function (m) { return !hampir(tumpuk(m), dihitungT[m]); }); var wadahGeser = Object.keys(isiW2).filter(function (w) { return !hampir(wbKomposisi(w).totalKg, isiW2[w]); });
  var kap = susunKapur(new Date(WC.tanggal + 'T20:00:00+07:00')).baris;
  asap = { kbBeda: kbBeda, wadah: Object.keys(dihitungW).length, dokWadah: (SW.dokumen || []).length, tolakW: SW.tolak || '', geserW: geserW, bukuSalah: bukuSalah, isiSalah: isiSalah, tumpukan: Object.keys(dihitungT).length, tolakT: ST2.tolak || '', tumpukSalah: tumpukSalah, wadahGeser: wadahGeser,
    kapurWadah: kap.filter(function (x) { return /^Cocokkan wadah /.test(x.isi); }).length, kapurTumpukan: kap.filter(function (x) { return /^Cocokkan tumpukan gudang /.test(x.isi); }).length };
}
print(J({ lulus: lulus, gagal: gagal, asap: asap }));
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


def utama(js, pakai_cadangan):
    cad = 'null'; tgl = ''
    p = cadangan_toko() if pakai_cadangan else None
    if p:
        import re
        d = json.load(open(p, encoding='utf-8')); kol = re.findall(r"\{ nama: '(\w+)'", open(os.path.join(AKAR, 'baru/js/data/koleksi.js'), encoding='utf-8').read())
        cad = json.dumps(dict((n, d[n]) for n in kol if isinstance(d.get(n), list))); tgl = os.path.basename(p).split('miqbal-')[-1][:10]
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    return h['lulus'], h['gagal'], h.get('asap')


RUSAK = {
    'selisih wadah tidak dibagi ke merek asal (semua ke karung di belakang)': ("if (b.isiSistem !== null) Object.keys(kb.alokasi).forEach((m) => tambah(m, kb.alokasi[m]));", "if (b.isiSistem !== null) tambah(b.karungNama, ckB2(isiH - b.isiSistem));"),
    'susut wajar tidak dikali hari sejak disamakan': (": ckB2(b.susutWajarKg * lamaHari);", ": ckB2(b.susutWajarKg);"),
    'batas susut owner di Aturan wadah diabaikan': ("? Number(a.susutWajarKg) : WADAH_SUSUT_WAJAR_KG;", "? WADAH_SUSUT_WAJAR_KG : WADAH_SUSUT_WAJAR_KG;"),
    'susut tanpa batas (semua selisih wajar)': ("const besar = ada && Math.abs(selisih) > wajarKg + 0.0001;", "const besar = false;"),
    'titik samakan cocokkan tanpa komposisi (isi jadi milik nama wadah)': ("b.stokSendiri ? { stokWadah: b.kunciStok } : { komposisi: b.komposisiBaru || {} }, { dariCocok: true })", "{}, { dariCocok: true })"),
    'cocokkan wadah tanpa titik samakan (tumpukan ikut bergeser)': ("    if (b.isiH !== null) dokumen.push({ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: b.nama, tipe: 'isi',", "    if (false) dokumen.push({ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: b.nama, tipe: 'isi',"),
    'karung terbuka tidak disamakan saat dicocokkan': ("    if (b.krH !== null && b.karungNama) dokumen.push(", "    if (false) dokumen.push("),
    'penanda bagian tumpukan hilang': ("bagian: 'tumpukan', bagianSistemKg: b.sistem, bagianFisikKg: b.dihitung", "bagianSistemKg: b.sistem, bagianFisikKg: b.dihitung"),
    'kgFisik tumpukan = hitungan tumpukan, bukan buku sesudahnya': ("kgFisik: ckB2(b.buku + b.selisih), selisihKg: b.selisih,", "kgFisik: b.dihitung, selisihKg: b.selisih,"),
    'isi ulang lupa dicatat tidak ditawarkan': ("const lupaTakar = lupaKg > 0 ? Math.max(1, Math.round(lupaKg / b.takarKg)) : 0;", "const lupaTakar = 0;"),
    'hitungan pertama dianggap selisih dari nol': ("const isiSistem = K.diketahui ? ckB2(K.totalKg) : null;", "const isiSistem = K.diketahui ? ckB2(K.totalKg) : 0;"),
    'cocokkan wadah mengubah umur cocokkan nama itu': ("if (!hitunganFisik(p) || (p.bagian === 'wadah' && (!bw[p.merk] || bw[p.merk].jenis === 'adukan'))) return;", "if (!hitunganFisik(p)) return;"),
    'papan kapur: cocokkan wadah ditulis sebagai cocokkan biasa': ("    else if (p.bagian === 'wadah') out.push(", "    else if (false) out.push("),
    'draf lama bertab beras tidak dipetakan': ("const tabCocokSah = (tab) => (TAB_COCOK.some((x) => x[0] === tab) ? tab : 'tumpukan');", "const tabCocokSah = (tab) => tab;"),
    'wadah yang baru disamakan tidak dijaga penjaga ganda': ("  ambilWadahLiteran().forEach((d) => { if (d.tipe === 'isi' && d.wadah && !d.pindahAwal) catat('wadah|' + d.wadah, d);", "  ambilWadahLiteran().forEach((d) => {"),
    'tumpukan tercatat = buku (karung terbuka & wadah tidak dikurangi)': ("out.push({ kunci: 'tumpukan|' + m, tab, nama: m, satuan: 'kg', sistem: ckB2(t.kg),", "out.push({ kunci: 'tumpukan|' + m, tab, nama: m, satuan: 'kg', sistem: ckB2(st[m].sisaKg || 0),"),
}

if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, (a, b) in RUSAK.items():
            if js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g, _ = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    print('COCOKKAN DIPISAH (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    if asap:
        salah = asap['geserW'] + asap['bukuSalah'] + asap['isiSalah'] + asap['tumpukSalah'] + asap['wadahGeser']
        print('ASAP DATA TOKO (%s): %d wadah dicocokkan (%d dokumen) · tumpukan tidak bergeser: %s · buku = Σ selisih: %s · isi wadah = hitungan: %s · %d tumpukan dicocokkan · tumpukan = hitungan: %s · wadah tidak bergeser: %s · papan kapur wadah %d / tumpukan %d'
              % (os.path.basename(cadangan_toko()), asap['wadah'], asap['dokWadah'], not asap['geserW'], not asap['bukuSalah'], not asap['isiSalah'], asap['tumpukan'], not asap['tumpukSalah'], not asap['wadahGeser'], asap['kapurWadah'], asap['kapurTumpukan']))
        if asap.get('kbBeda'): print('   karung belakang catatan ≠ buku SEBELUM dicocokkan (data toko, bukan cacat uji): ' + '; '.join(asap['kbBeda']))
        if asap['tolakW'] or asap['tolakT']: g.append('asap ditolak: ' + asap['tolakW'] + ' ' + asap['tolakT'])
        if salah: g.append('asap: rantai stok bergeser ' + json.dumps(salah, ensure_ascii=False)); print('   ✗ ' + g[-1][:600])
        if not asap['kapurWadah'] or not asap['kapurTumpukan']: g.append('asap: papan kapur tidak memisahkan cocokkan wadah & tumpukan')
    sys.exit(2 if g else 0)
