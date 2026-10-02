#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_rak_inkremental.py — owner 3 Okt 2026 ("Gua mau layar jual lebih smooth"): rak Jual disusun INKREMENTAL (jual-logika susunRakLanjut).
  · KESETARAAN (jsc, KOTAK PASIR): sesudah tiap ubahan keranjang / struk parkir, susunRakLanjut(s, rakSebelumnya) SAMA PERSIS dengan susunRak(s) — semua
    kunci & nilai (urutan kunci juga), urutan chip, kelompok, Sering, rak Wadah, dan isian #jualKarungBerat yang ditinggalkan. Rak lanjutan dirantai dari
    rak lanjutan sebelumnya (tidak pernah disegarkan dari susun penuh). Kasus tepi bernama: karung 50 & 25 kg, kemasan, bonus, ½ karung, literan wadah
    belum aktif (merek asal campuran) & aktif (buku sendiri), literan langsung, repack + kantong ditanggung / dijual, wadah barang, pengganti retur, nego,
    parkir, buka & buang struk, hapus baris, keranjang kosong, pelanggan / hari / data toko berganti, keranjang belum disinkronkan — lalu urutan ACAK
    berbenih tetap.
  · INKREMENTAL SUNGGUH: chip yang tidak tersentuh dipakai ulang (objek yang sama); tiap kasus bernama menyebut chip mana yang dihitung ulang
    (+1 karung NG → hanya chip yang membaca buku NG), ketukan yang tidak menyentuh stok → nol.
  · LAYAR (jual.js asli di jsc, impor peramban ditiruan — pola uji_cache_chip_literan): ubahan keranjang → L.susunRakLanjut; data toko basi / pelanggan /
    tukar berubah → L.susunRak; rak yang tergambar di tiap jalur = rak layar kedua yang menyusun penuh (HTML sama).
  · Cadangan toko di _privat/ (lokal saja; dilewati di CI; boleh juga CADANGAN_TOKO=<berkas>): urutan acak atas data toko + ONGKOS susun penuh vs
    lanjutan per jenis ketukan, dan satu ketukan +1 di layar (rak + gambar) sebelum/sesudah.

    python3 alat-uji/uji_rak_inkremental.py            → N lulus · 0 gagal
    python3 alat-uji/uji_rak_inkremental.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import uji_wadah_bernama, uji_cache_chip_literan  # noqa: E402

JAM_TETAP = "var __KINI = new Date('2026-09-21T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
brs = uji_wadah_bernama.brs


def jual(i, tgl, jam, jenis, isi, nama=''):
    d = {'id': i, 'tanggal': tgl, 'jam': jam, 'caraBayar': 'Tunai', 'namaPelanggan': nama, 'jenis': jenis, 'grupNota': 'g' + str(i)}
    d.update(isi); return d


# KOTAK PASIR — ANGKA CONTOH, bukan angka toko. Jam dikunci 21 Sep 2026 10:00 WIB.
KOTAK = {
  # NG 8 karung (sengaja sedikit: buku NG yang membatasi literan wadah IR64 Apex), Kumala 4, Angsa 6 × 50 + 4 × 25, Tawon 6, Beo 2 × 25
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-09-10', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
                  'merkList': [brs(1, 'NG', 8, 12000), brs(2, 'Kumala', 4, 11000), brs(3, 'Angsa', 6, 13000), brs(4, 'Angsa', 4, 13200, 25), brs(5, 'Tawon', 6, 12500),
                               brs(6, 'Beo', 2, 14000, 25)]}],
  'katalogHargaKarung': [{'id': 'NG', 'merk': 'NG', 'hargaPerKg': 13000}, {'id': 'Kumala', 'merk': 'Kumala', 'hargaPerKg': 12000}, {'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 14000},
                         {'id': 'Tawon', 'merk': 'Tawon', 'hargaPerKg': 13500}, {'id': 'Beo', 'merk': 'Beo', 'hargaPerKg': 15000}],
  # Hemat 50 kg = kemasan yang boleh dijual ½ (25 kg belum punya harga → usul ½ harga); Angsa 25 kg harga dari katalog kemasan
  'katalogHargaKemasan': [{'id': 'hm1', 'merk': 'Kembang', 'ukuran': 5, 'hargaPerUnit': 72000}, {'id': 'hm2', 'merk': 'Hemat', 'ukuran': 50, 'hargaPerUnit': 640000},
                          {'id': 'hm3', 'merk': 'Angsa', 'ukuran': 25, 'hargaPerUnit': 340000}],
  'produksiKemasan': [{'id': 'p1', 'tanggal': '2026-09-11', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 20, 'hppPerUnit': 66000, 'merkSumber': 'Tawon', 'kgDipakai': 100},
                      {'id': 'p2', 'tanggal': '2026-09-11', 'namaProduk': 'Hemat', 'ukuranKemasan': 50, 'jumlahUnit': 3, 'hppPerUnit': 600000, 'merkSumber': 'Tawon', 'kgDipakai': 150}],
  'katalogHargaLiteran': [{'id': 'IR64 Apex', 'merk': 'IR64 Apex', 'hargaPerLiter': 12000}, {'id': 'Angsa', 'merk': 'Angsa', 'hargaPerLiter': 13000},
                          {'id': 'Campur Dua', 'merk': 'Campur Dua', 'hargaPerLiter': 12500}, {'id': 'Kosong Satu', 'merk': 'Kosong Satu', 'hargaPerLiter': 12000},
                          {'id': 'Tawon', 'merk': 'Tawon', 'hargaPerLiter': 13500}],
  # empat wadah: IR64 Apex = NG 30 + Kumala 20 (belum aktif) · Angsa = diaktifkan & diisi 1 karung di skenario · Campur Dua = NG 5 + Kumala 5 lalu 8,2 kg NG
  # terjual dari wadah itu (bagian NG minus → yang dibaca cuma Kumala) · Kosong Satu = belum pernah dicocokkan (merek cadangan). Tawon dijual literan LANGSUNG.
  'wadahLiteran': [{'id': 100, 'tanggal': '2026-09-01', 'jam': '07:00', 'tipe': 'atur', 'penuhKg': 50, 'puncakKg': 60, 'isiUlangKg': 10, 'takarKg': 1.8, 'sisihKg': 10,
                    'daftar': ['IR64 Apex', 'Angsa', 'Campur Dua', 'Kosong Satu'], 'literanLangsung': ['Tawon']},
                   {'id': 101, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'IR64 Apex', 'isiKg': 50, 'komposisi': {'NG': 30, 'Kumala': 20}},
                   {'id': 102, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'Angsa', 'isiKg': 0},
                   {'id': 103, 'tanggal': '2026-09-19', 'jam': '07:30', 'tipe': 'karung', 'merk': 'Kumala', 'kg': 50, 'wadah': 'IR64 Apex'},
                   {'id': 104, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'Campur Dua', 'isiKg': 10, 'komposisi': {'NG': 5, 'Kumala': 5}}],
  'stokBahanLiteran': [{'id': 'l1', 'tanggal': '2026-09-01', 'jenis': 'paperbag5l', 'tipe': 'beli', 'jumlah': 100, 'hargaTotal': 30500},
                       {'id': 'l2', 'tanggal': '2026-09-01', 'jenis': 'paperbag10l', 'tipe': 'beli', 'jumlah': 100, 'hargaTotal': 39500},
                       {'id': 'l3', 'tanggal': '2026-09-01', 'jenis': 'karungbekas', 'tipe': 'beli', 'jumlah': 40, 'hargaTotal': 40000}],
  'stokBahanKemasan': [{'id': 'k1', 'tanggal': '2026-09-01', 'jenis': '5kg_kembangbmw', 'tipe': 'beli', 'jumlah': 30, 'hargaTotal': 33750}],
  'hargaWadah': [{'id': '5kg_kembangbmw', 'jenis': '5kg_kembangbmw', 'harga': 2000, 'tanggal': '2026-09-10'}, {'id': 'karungbekas', 'jenis': 'karungbekas', 'harga': 1500, 'tanggal': '2026-09-10'}],
  # penjualan 28 hari terakhir (Sering): dua pembeli contoh; literan IR64 Apex 18 Sep = sebelum titik samakan (tidak mengubah komposisinya)
  'penjualan': [jual(5001, '2026-09-15', '09:00', 'karung', {'merkSumber': 'NG', 'jumlahKarung': 1, 'beratKarungAcuan': 50, 'totalKg': 50, 'hargaTotal': 650000, 'hppTotalSaatJual': 600000}, 'Pembeli Contoh A'),
                jual(5002, '2026-09-16', '09:00', 'karung', {'merkSumber': 'NG', 'jumlahKarung': 1, 'beratKarungAcuan': 50, 'totalKg': 50, 'hargaTotal': 650000, 'hppTotalSaatJual': 600000}),
                jual(5003, '2026-09-19', '09:00', 'literan', {'merkSumber': 'NG', 'namaProduk': 'Campur Dua', 'dariWadah': 'Campur Dua', 'jumlahLiter': 10, 'totalKg': 8.2, 'hargaTotal': 125000, 'hppTotalSaatJual': 98400}),
                jual(5004, '2026-09-17', '10:00', 'kemasan', {'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 2, 'totalKg': 10, 'hargaTotal': 144000, 'hppTotalSaatJual': 132000}, 'Pembeli Contoh B'),
                jual(5005, '2026-09-18', '11:00', 'literan', {'merkSumber': 'NG', 'namaProduk': 'IR64 Apex', 'dariWadah': 'IR64 Apex', 'jumlahLiter': 5, 'totalKg': 4.1, 'hargaTotal': 60000, 'hppTotalSaatJual': 49200}, 'Pembeli Contoh A'),
                jual(5006, '2026-09-18', '12:00', 'repacking', {'merkSumber': 'Tawon', 'namaProduk': 'Tawon', 'totalKg': 10, 'hargaTotal': 135000, 'hppTotalSaatJual': 125000}),
                jual(5007, '2026-09-20', '08:00', 'literan', {'merkSumber': 'Tawon', 'namaProduk': 'Tawon', 'jumlahLiter': 4, 'totalKg': 3.28, 'hargaTotal': 54000, 'hppTotalSaatJual': 41000}),
                jual(5008, '2026-09-20', '09:00', 'wadah', {'jenisWadah': '5kg_kembangbmw', 'namaProduk': 'Kantong 5 kg', 'jumlahUnit': 2, 'totalKg': 0, 'hargaTotal': 4000, 'hppTotalSaatJual': 2250})],
}

# fungsi yang dihitung pemanggilannya (bukti inkremental) — dibungkus SESUDAH bundel, panggilan di dalam bundel ikut terhitung
HITUNG = ['stokMaksJalur', 'bebasLiterWadah', 'wbModalPerKg', 'tinggiWadah', 'susunRakWadah', 'urutSering']
BUNGKUS = 'var __n = {};\n' + ''.join("%s = (function (f) { return function () { __n.%s = (__n.%s || 0) + 1; return f.apply(this, arguments); }; })(%s);\n" % (f, f, f, f) for f in HITUNG)

# pembantu bersama logika & layar
BANTU = r"""
var J = JSON.stringify;
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
// sama persis: Object.is untuk nilai, kunci (dan URUTAN kuncinya) sama, larik sama panjang & urut
function beda(a, b, jalur) {
  if (Object.is(a, b)) return '';
  if (typeof a !== 'object' || typeof b !== 'object' || a === null || b === null) return jalur + ': ' + J(a) + ' ≠ ' + J(b);
  if (Array.isArray(a) !== Array.isArray(b)) return jalur + ': larik vs objek';
  var ka = Object.keys(a), kb = Object.keys(b);
  if (ka.join('\u0001') !== kb.join('\u0001')) return jalur + ': kunci ' + J(ka) + ' ≠ ' + J(kb);
  for (var i = 0; i < ka.length; i++) { var r = beda(a[ka[i]], b[ka[i]], jalur + '.' + ka[i]); if (r) return r; }
  return '';
}
var JALUR_CHIP = ['karung', 'kemasan', 'literan', 'repack'];
var namaChip = function (c) { return c.jalur + ':' + c.kunci + (c.jalur === 'karung' ? ':' + c.berat : ''); };
// chip rak baru yang BUKAN objek rak lama (= dihitung ulang); 'wadah' = rak Wadah disusun ulang
var dihitung = function (lama, baru) { var out = []; JALUR_CHIP.forEach(function (j) { baru[j].forEach(function (c, i) { if (lama[j][i] !== c) out.push(namaChip(c)); }); });
  if (lama.wadah !== baru.wadah) out.push('wadah'); return out.sort(); };
var jumlahChip = function (r) { return JALUR_CHIP.reduce(function (a, j) { return a + r[j].length; }, 0); };
// kelompok menunjuk chip rak yang SAMA (seperti susun penuh)
var kelompokUtuh = function (r) { return ['karung', 'kemasan'].every(function (j) { return r.kelompok[j].every(function (g) { return g.daftar.every(function (c) { return r[j].indexOf(c) >= 0; }); }); }); };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var nId = 9000; var W = { tanggal: '2026-09-21', jam: '10:00', kini: '2026-09-21T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
// wadah Angsa diaktifkan (buku sendiri) lalu diisi satu karung Angsa; IR64 Apex, Campur Dua, Kosong Satu tetap model merek asal
var RA = wbSusunAktifkan('Angsa', W); if (!RA.tolak) terapkanKeCache(RA.dokumen);
var s0 = keadaanAwal(); s0.sekarang = new Date(Date.now());
var RI = wbSusunIsiUlangTiga('Angsa', 'Angsa', { jenis: 'karung' }, W, s0); if (!RI.tolak) terapkanKeCache(RI.dokumen);
var nJual = 7000;
var jualBaru = function (merk) { nJual += 1; terapkanKeCache([{ koleksi: 'penjualan', data: { id: nJual, tanggal: '2026-09-21', jam: '09:30', caraBayar: 'Tunai', namaPelanggan: '', jenis: 'karung', merkSumber: merk,
  jumlahKarung: 1, beratKarungAcuan: 50, totalKg: 50, hargaTotal: 650000, hppTotalSaatJual: 600000, grupNota: 'gx' + nJual } }]); };
"""

SKENARIO = BANTU + r"""
ok('kotak pasir: wadah Angsa aktif & berisi, tiga wadah lain model merek asal', !RA.tolak && !RI.tolak && wbAktif('Angsa') && !wbAktif('IR64 Apex') && tinggiWadah('Angsa', null).sisaNyataKg > 0, J([RA.tolak, RI.tolak]));
var s = Object.assign({}, s0); sinkronKeranjang(s);
var rak0 = susunRak(s);
ok('kotak pasir: semua jenis chip ada (karung 50 & 25, kemasan 5 & 50, literan wadah ×4 + langsung, repack, wadah, Sering)',
  rak0.karung.some(function (c) { return c.berat === 25; }) && rak0.karung.some(function (c) { return c.berat === 50; }) && rak0.kemasan.some(function (c) { return c.ukuranKg === 50; })
  && rak0.literan.filter(function (c) { return c.wadahLiteran; }).length === 4 && rak0.literan.some(function (c) { return !c.wadahLiteran; }) && rak0.repack.length >= 4 && rak0.wadah.length >= 1 && rak0.sering.length >= 4,
  J({ karung: rak0.karung.map(namaChip), kemasan: rak0.kemasan.map(namaChip), literan: rak0.literan.map(namaChip), repack: rak0.repack.length, wadah: rak0.wadah.length, sering: rak0.sering.length }));
var prev = rak0; var nLangkah = 0;
// satu langkah: keadaan baru → susun penuh (acuan) & lanjutan dari rak lanjutan sebelumnya; urutan keduanya bergantian (isian berat tidak boleh bergantung pada siapa duluan)
function langkah(patch) {
  if (patch) s = Object.assign({}, s, patch);
  sinkronKeranjang(s); nLangkah += 1;
  var penuh, lanjut, domP, domL;
  if (nLangkah % 2) { penuh = susunRak(s); domP = __dom.jualKarungBerat.value; __n = {}; lanjut = susunRakLanjut(s, prev); domL = __dom.jualKarungBerat.value; }
  else { __n = {}; lanjut = susunRakLanjut(s, prev); domL = __dom.jualKarungBerat.value; var n0 = __n; __n = {}; penuh = susunRak(s); domP = __dom.jualKarungBerat.value; __n = n0; }
  var b = beda(penuh, lanjut, 'rak') || (domP !== domL ? 'isian #jualKarungBerat ' + domP + ' (penuh) ≠ ' + domL + ' (lanjutan)' : '') || (kelompokUtuh(lanjut) ? '' : 'kelompok lanjutan menunjuk chip lain');
  var h = { beda: b, dihitung: dihitung(prev, lanjut), n: __n, lanjut: lanjut, penuh: penuh, sebelum: prev };
  prev = lanjut; return h;
}
var chip = function (j, k, berat) { return prev[j].find(function (c) { return c.kunci === k && (!berat || c.berat === berat); }); };
var masuk = function (c, n, isi) { var r = masukkan(Object.assign({}, s, { pilih: c }, isi || {}), n); return r.keranjang ? { keranjang: r.keranjang, urutBaris: r.urutBaris } : { tolak: r.kabar || 'ditolak' }; };
var baris = function (pred) { return s.keranjang.filter(function (b) { return pred(b.trx); })[0]; };
// kasus bernama: patch → lanjutan = penuh; harap (opsional) = chip yang dihitung ulang, persis
function kasus(nama, patch, harap) {
  if (patch && patch.tolak) { ok(nama + ': langkahnya diterima logika', false, patch.tolak); return null; }
  var h = langkah(patch);
  ok(nama + ': lanjutan = susun penuh', !h.beda, h.beda);
  if (harap) ok(nama + ': yang dihitung ulang = ' + (harap.length ? harap.join(', ') : 'tidak ada'), J(h.dihitung) === J(harap.slice().sort()), J(h.dihitung));
  return h;
}

// ---- 1 · kasus tepi bernama (rantai lanjutan dari rak awal)
kasus('keranjang kosong, tidak ada yang berubah', {}, []);
var h = kasus('+1 karung NG (baris baru)', masuk(chip('karung', 'NG', 50), 1), ['karung:NG:50', 'literan:IR64 Apex', 'repack:NG']);
ok('+1 karung NG: chip lain dipakai ulang (bukan disusun penuh) — ' + h.dihitung.length + ' dari ' + jumlahChip(h.lanjut) + ' chip, stokMaksJalur ' + (h.n.stokMaksJalur || 0) + '×, Sering tidak dihitung ulang',
  h.dihitung.length === 3 && h.n.stokMaksJalur === 1 && !h.n.urutSering && !h.n.susunRakWadah, J(h.n));
ok('+1 karung NG: sisa karung NG turun 1 & literan IR64 Apex (buku NG yang membatasi) ikut turun', chip('karung', 'NG', 50).sisa === h.sebelum.karung.find(function (c) { return c.kunci === 'NG'; }).sisa - 1
  && chip('literan', 'IR64 Apex').sisa < h.sebelum.literan.find(function (c) { return c.kunci === 'IR64 Apex'; }).sisa, J([chip('karung', 'NG', 50).sisa, chip('literan', 'IR64 Apex').sisa]));
kasus('karung NG +½ (ubahJumlahBaris)', ubahJumlahBaris(s, baris(function (t) { return t.merkSumber === 'NG'; }).id, 0.5), ['karung:NG:50', 'literan:IR64 Apex', 'repack:NG']);
kasus('+2 kemasan Kembang 5 kg', masuk(chip('kemasan', 'Kembang|5'), 2), ['kemasan:Kembang|5']);
kasus('bonus +1 kemasan Kembang', toggleBonus(s, baris(function (t) { return t.namaProduk === 'Kembang'; }).id), ['kemasan:Kembang|5']);
kasus('½ karung Hemat (kemasan 50 kg dipegang 1 unit)', masuk(skChip(chip('kemasan', 'Hemat|50'), ''), 1), ['kemasan:Hemat|50']);
h = kasus('+6 L literan wadah IR64 Apex (NG + Kumala, kantong 10 L)', masuk(chip('literan', 'IR64 Apex'), 6), ['karung:Kumala:50', 'karung:NG:50', 'literan:Campur Dua', 'literan:IR64 Apex', 'repack:Kumala', 'repack:NG']);
ok('literan wadah IR64 Apex: baris dipecah per merek asal (NG & Kumala) dan tinggi wadahnya ikut turun', baris(function (t) { return t.dariWadah === 'IR64 Apex'; }).trx.pecahan.length === 2
  && chip('literan', 'IR64 Apex').wadah.sisaKg < h.sebelum.literan.find(function (c) { return c.kunci === 'IR64 Apex'; }).wadah.sisaKg, J(baris(function (t) { return t.dariWadah === 'IR64 Apex'; }).trx.pecahan));
kasus('+2 L literan wadah Angsa (buku sendiri)', masuk(chip('literan', 'Angsa'), 2), ['literan:Angsa']);
kasus('+3 L literan langsung Tawon', masuk(chip('literan', 'Tawon'), 3), ['karung:Tawon:50', 'literan:Tawon', 'repack:Tawon']);
kasus('+5 kg repack NG, 2 kantong DITANGGUNG toko', masuk(chip('repack', 'NG'), 5, { rpWadah: '5kg_kembangbmw', rpLembar: '2', rpDijual: false }), ['karung:NG:50', 'literan:IR64 Apex', 'repack:NG', 'wadah']);
kasus('+4 kg repack Kumala, 1 kantong DIJUAL (baris wadah sendiri)', masuk(chip('repack', 'Kumala'), 4, { rpWadah: '5kg_kembangbmw', rpLembar: '1', rpDijual: true }),
  ['karung:Kumala:50', 'literan:Campur Dua', 'literan:IR64 Apex', 'repack:Kumala', 'wadah']);
kasus('+3 lembar karung bekas (wadah barang)', masuk(chip('wadah', 'karungbekas'), 3), ['wadah']);
kasus('+1 karung Beo 25 kg (isian berat kembali ke berat terakhir susun penuh)', masuk(chip('karung', 'Beo', 25), 1), ['karung:Beo:25', 'repack:Beo']);
kasus('+1 karung Angsa 25 kg (buku Angsa: 50 & 25 kg ikut)', masuk(chip('karung', 'Angsa', 25), 1), ['karung:Angsa:25', 'karung:Angsa:50', 'repack:Angsa']);
kasus('pengganti retur pada baris karung (stok tidak tersentuh)', togglePenggantiRetur(s, baris(function (t) { return t.jenis === 'karung'; }).id), []);
kasus('nego baris kemasan (harga saja)', terapkanNego(s, baris(function (t) { return t.namaProduk === 'Kembang'; }).id, 70000), []);
kasus('ketukan tanpa ubahan keranjang (kabar)', { kabar: 'contoh' }, []);
var nAktif = s.keranjang.length;
h = kasus('PARKIR: keranjang pindah ke struk @1', parkir(s));
ok('parkir: struk memegang ' + nAktif + ' baris, keranjang aktif kosong, chip menyebut yang dipegang struk lain', s.antrean.length === 1 && s.keranjang.length === 0 && chip('karung', 'NG', 50).dipegang > 0, J(chip('karung', 'NG', 50)));
kasus('pembeli kedua: +1 karung NG (struk lain memegang NG)', masuk(chip('karung', 'NG', 50), 1), ['karung:NG:50', 'literan:IR64 Apex', 'repack:NG']);
kasus('pembeli kedua: +2 L literan wadah Campur Dua', masuk(chip('literan', 'Campur Dua'), 2));
kasus('pembeli kedua: −1 karung NG (baris hilang)', ubahJumlahBaris(s, baris(function (t) { return t.merkSumber === 'NG' && t.jenis === 'karung'; }).id, -1));
kasus('PARKIR lagi → dua struk', parkir(s));
kasus('buka struk pertama (yang aktif kosong tidak diparkir)', pakaiAntrean(s, s.antrean[0].id));
kasus('hapus baris literan wadah', hapusBaris(s, baris(function (t) { return t.dariWadah === 'IR64 Apex'; }).id));
kasus('BUANG struk parkir, keranjang aktif tetap', buangAntrean(s, s.antrean[0].id));
kasus('keranjang dikosongkan', { keranjang: [] });
kasus('isi lagi: +1 karung NG', masuk(chip('karung', 'NG', 50), 1), ['karung:NG:50', 'literan:IR64 Apex', 'repack:NG']);
var sr0 = J(prev.sering.map(namaChip));
h = kasus('PELANGGAN berganti → susun penuh (Sering per pelanggan)', { pelanggan: 'Pembeli Contoh A' });
ok('pelanggan berganti: Sering ikut berganti & disusun penuh', J(h.lanjut.sering.map(namaChip)) !== sr0 && h.n.urutSering === 1 && h.dihitung.length === jumlahChip(h.lanjut) + 1, J([sr0, h.lanjut.sering.map(namaChip), h.n]));
kasus('pelanggan sama, +1 karung NG', ubahJumlahBaris(s, baris(function (t) { return t.merkSumber === 'NG'; }).id, 1), ['karung:NG:50', 'literan:IR64 Apex', 'repack:NG']);
var sisaNG = chip('karung', 'NG', 50).sisa; jualBaru('NG');
h = kasus('DATA TOKO berubah (penjualan NG baru masuk cache) → susun penuh');
ok('data berubah: sisa karung NG turun 1 & semua chip disusun ulang', chip('karung', 'NG', 50).sisa === sisaNG - 1 && h.dihitung.length === jumlahChip(h.lanjut) + 1, J([sisaNG, chip('karung', 'NG', 50).sisa, h.dihitung.length]));
h = kasus('HARI berganti (100 hari kemudian) → susun penuh', { sekarang: new Date(Date.now() + 100 * 864e5) });
ok('hari berganti: Sering di luar jendela 28/90 hari → kosong', h.lanjut.sering.length === 0 && h.sebelum.sering.length > 0, J([h.sebelum.sering.length, h.lanjut.sering.length]));
kasus('hari itu: +1 karung NG', ubahJumlahBaris(s, baris(function (t) { return t.merkSumber === 'NG'; }).id, 1), ['karung:NG:50', 'literan:IR64 Apex', 'repack:NG']);
// keranjang BELUM disinkronkan: rak lanjutan untuk keadaan A dipanggil saat salinan keranjang di logika = keadaan lain → susun penuh (tidak memakai jejak A)
(function () {
  var A = s; var rA = prev; var mC = masuk(chip('karung', 'Kumala', 50), 2); var C = Object.assign({}, A, { keranjang: mC.keranjang }); sinkronKeranjang(C);
  var f = susunRak(A); var l = susunRakLanjut(A, rA);
  ok('keranjang belum disinkronkan: lanjutan = susun penuh atas salinan yang sedang berlaku (bukan memakai ulang chip)', !mC.tolak && !beda(f, l, 'rak') && dihitung(rA, l).length === jumlahChip(l) + 1, beda(f, l, 'rak') || J(dihitung(rA, l).length));
  sinkronKeranjang(A);
})();
kasus('kembali selaras (rak lanjutan dari rak sebelum langkah tak selaras)', {}, []);

// ---- 2 · urutan ACAK berbenih tetap — rantai panjang, tiap langkah lanjutan = penuh
var JUMLAH = { karung: [0.5, 1, 1, 1.5, 2], kemasan: [1, 1, 2, 3], literan: [1, 2, 3, 5, 6, 10], repack: [1, 2.5, 5], wadah: [1, 2, 3] };
function acakDari(b) { var x = b >>> 0 || 1; return function () { x ^= x << 13; x >>>= 0; x ^= x >>> 17; x ^= x << 5; x >>>= 0; return x / 4294967296; }; }
function urutanAcak(benih, n) {
  var acak = acakDari(benih); var pilih = function (d) { return d[Math.floor(acak() * d.length)]; };
  var pilihBaris = function (pred) { var d = s.keranjang.filter(function (b) { return !pred || pred(b.trx); }); return d.length ? pilih(d) : null; };
  // nol = langkah yang tidak menyentuh stok (harga / tanda pengganti di baris yang bukan literan wadah, ketukan diam) — wajib nol chip dihitung ulang.
  // Baris literan wadah yang dibangun ulang memecah ulang merek asalnya (wbPecah atas keranjang sekarang), jadi jejaknya boleh berubah.
  var nol = false; var bukanWadah = function (t) { return !t.dariWadah; };
  var OPS = [
    ['tambah', 7, function () { var j = pilih(['karung', 'karung', 'kemasan', 'literan', 'literan', 'literan', 'repack', 'wadah']); if (!prev[j].length) return null; var c = pilih(prev[j]); var isi = {};
      var n = pilih(JUMLAH[j]);
      if (j === 'repack') { var w = pilih(['', '', 'tanggung', 'jual']); if (w) isi = { rpWadah: '5kg_kembangbmw', rpLembar: String(pilih([1, 2, 3])), rpDijual: w === 'jual', rpUpah: pilih(['', '2000']) }; }
      if (j === 'kemasan' && c.ukuranKg === 50 && acak() < 0.5) { c = skChip(c, ''); n = 1; }
      var r = masuk(c, n, isi); return r.tolak ? null : r; }],
    ['+1', 5, function () { var b = pilihBaris(); return b ? ubahJumlahBaris(s, b.id, b.trx.satuan === 'karung' ? 0.5 : 1) : null; }],
    ['−1', 4, function () { var b = pilihBaris(); return b ? ubahJumlahBaris(s, b.id, -(b.trx.satuan === 'karung' ? 0.5 : 1)) : null; }],
    ['hapus', 1.5, function () { var b = pilihBaris(); return b ? hapusBaris(s, b.id) : null; }],
    ['bonus', 1, function () { var b = pilihBaris(function (t) { return t.jenis === 'kemasan'; }); return b ? toggleBonus(s, b.id) : null; }],
    ['pengganti', 1, function () { var b = pilihBaris(bukanWadah); nol = !!b; return b ? togglePenggantiRetur(s, b.id) : null; }],
    ['nego', 1, function () { var b = pilihBaris(bukanWadah); nol = !!b; return b ? terapkanNego(s, b.id, Math.max(500, Math.round(b.trx.hargaSatuan * 0.97))) : null; }],
    ['nego literan wadah', 0.5, function () { var b = pilihBaris(function (t) { return !!t.dariWadah; }); return b ? terapkanNego(s, b.id, Math.max(500, b.trx.hargaSatuan - 500)) : null; }],
    ['parkir', 1, function () { return s.keranjang.length ? parkir(s) : null; }],
    ['buka', 1, function () { return s.antrean.length ? pakaiAntrean(s, pilih(s.antrean).id) : null; }],
    ['buang', 0.7, function () { return s.antrean.length ? buangAntrean(s, pilih(s.antrean).id) : null; }],
    ['kosong', 0.4, function () { return { keranjang: [] }; }],
    ['pelanggan', 0.5, function () { return { pelanggan: pilih(['', 'Pembeli Contoh A', 'Pembeli Contoh B']) }; }],
    ['data', 0.3, function () { jualBaru(pilih(['NG', 'Kumala', 'Tawon', 'Angsa'])); return {}; }],
    ['diam', 0.6, function () { nol = true; return { kabar: 'ketuk ' + acak() }; }]];
  var total = OPS.reduce(function (a, o) { return a + o[1]; }, 0);
  var hasil = { n: 0, beda: '', inkremental: 0, diamNol: true, nama: {} };
  for (var i = 0; i < n; i++) {
    var t = acak() * total, o = OPS[0]; for (var k = 0; k < OPS.length; k++) { t -= OPS[k][1]; if (t < 0) { o = OPS[k]; break; } }
    nol = false; var p = o[2](); if (p && p.kabarAwas && !p.keranjang && !p.antrean) p = {};
    var hh = langkah(p || {}); hasil.n += 1; hasil.nama[o[0]] = (hasil.nama[o[0]] || 0) + 1;
    if (hh.beda && !hasil.beda) hasil.beda = 'langkah ' + i + ' (' + o[0] + '): ' + hh.beda;
    if (hh.dihitung.length < jumlahChip(hh.lanjut)) hasil.inkremental += 1;
    if (nol && hh.dihitung.length && hasil.diamNol === true) hasil.diamNol = 'langkah ' + i + ' ' + o[0] + ' menghitung ulang ' + J(hh.dihitung);
  }
  return hasil;
}
[20261003, 7, 4242, 99991].forEach(function (b) {
  s = Object.assign({}, s0, { keranjang: [], antrean: [] }); prev = susunRak((sinkronKeranjang(s), s));
  var A = urutanAcak(b, 90);
  ok('acak benih ' + b + ': ' + A.n + ' langkah (' + Object.keys(A.nama).map(function (k) { return k + ' ' + A.nama[k]; }).join(' · ') + ') — tiap lanjutan = susun penuh', !A.beda, A.beda);
  ok('acak benih ' + b + ': sungguh inkremental (' + A.inkremental + ' dari ' + A.n + ' langkah memakai ulang chip); harga / pengganti / ketukan diam → nol chip dihitung ulang', A.inkremental >= A.n * 0.6 && A.diamNol === true, J([A.inkremental, A.diamNol]));
});
print(J({ lulus: lulus, gagal: gagal }));
"""

# ---- LAYAR: jual.js asli (tiruan peramban) di atas kotak pasir yang sama
LAYAR = BANTU + r"""
setelKunci(false);
var opsiJ = function () { return { akun: function () { return null; }, gantiMode: function () {}, mode: function () { return 'gelap'; }, statusTeks: function () { return ''; }, statusAwas: function () { return false; },
  statusRingkas: function () { return ''; }, versiData: function () { return __versi; }, pemegang: function () { return null; }, bukaStok: null }; };
var aJ = __akar(); var JL = null;
var sJ = function () { return JL.keadaan.baca(); };
var susun = function (f) { return hitungBerat(['susunRak', 'susunRakLanjut'], f); };
var rakSini = function () { var s = sJ(); sinkronKeranjang(s); return susunRak(s); };
var isiKeranjang = function (r) { JL.keadaan.setel({ keranjang: r.keranjang, urutBaris: r.urutBaris }); };
var masukL = function (c, n, isi) { return masukkan(Object.assign({}, sJ(), { pilih: c }, isi || {}), n); };
var h0 = susun(function () { JL = pasangLayarJual(aJ, opsiJ()); JL.keadaan.setel({ jalur: 'karung', sekarang: new Date(Date.now()) }); });
ok('layar: dibuka → rak disusun penuh sekali', h0.susunRak === 1 && !h0.susunRakLanjut, J(h0));
var cNG = rakSini().karung.find(function (c) { return c.kunci === 'NG'; });
var h1 = susun(function () { isiKeranjang(masukL(cNG, 1)); });
ok('layar: barang masuk keranjang → rak disusun LANJUTAN (L.susunRakLanjut), bukan penuh', h1.susunRakLanjut === 1 && !h1.susunRak && sJ().keranjang.length === 1, J(h1));
var h2 = susun(function () { aJ.__aksi.tambahBaris({ id: sJ().keranjang[0].id, langkah: '0.5' }); });
ok('layar: +½ karung lewat tombol + → lanjutan', h2.susunRakLanjut === 1 && !h2.susunRak && sJ().keranjang[0].trx.jumlah === 1.5, J([h2, sJ().keranjang[0].trx.jumlah]));
var h3 = susun(function () { JL.keadaan.setel({ kabar: '' }); JL.keadaan.setel({ jalur: 'literan' }); JL.keadaan.setel({ jalur: 'karung' }); });
ok('layar: ketukan & pindah jalur tanpa ubahan keranjang → rak tidak disusun sama sekali', !h3.susunRak && !h3.susunRakLanjut, J(h3));
var h4 = susun(function () { JL.keadaan.setel({ pelanggan: 'Pembeli Contoh A' }); });
ok('layar: pelanggan berganti → susun penuh', h4.susunRak === 1 && !h4.susunRakLanjut, J(h4));
var h5 = susun(function () { JL.keadaan.setel({ tukar: { ringkas: 'contoh', kredit: 0 } }); JL.keadaan.setel({ tukar: null }); });
ok('layar: tukar diikat & dilepas → susun penuh (dua kali)', h5.susunRak === 2 && !h5.susunRakLanjut, J(h5));
var h6 = susun(function () { jualBaru('Kumala'); });
ok('layar: data toko berubah (penjualan baru) → rak basi → susun penuh', h6.susunRak === 1 && !h6.susunRakLanjut, J(h6));
JL.keadaan.setel({ pelanggan: '' });   // parkir mengosongkan nama pembeli — tanpa nama dulu supaya keenam ubahan cuma isi keranjang
var h7 = susun(function () { isiKeranjang(masukL(rakSini().literan.find(function (c) { return c.kunci === 'IR64 Apex'; }), 6)); isiKeranjang(masukL(rakSini().kemasan[0], 2));
  isiKeranjang(masukL(rakSini().repack.find(function (c) { return c.kunci === 'NG'; }), 3, { rpWadah: '5kg_kembangbmw', rpLembar: '1', rpDijual: true })); JL.keadaan.setel(parkir(sJ()));
  isiKeranjang(masukL(rakSini().literan.find(function (c) { return c.kunci === 'Tawon'; }), 2)); isiKeranjang(masukL(rakSini().wadah[0], 1)); });
ok('layar: enam ubahan keranjang / parkir berturut-turut → enam susun lanjutan', h7.susunRakLanjut === 6 && !h7.susunRak && sJ().antrean.length === 1 && sJ().keranjang.length === 2, J([h7, sJ().keranjang.length, sJ().antrean.length]));
// rak yang tergambar (lanjutan) = rak layar kedua dengan keadaan yang sama, disusun PENUH (nama acuan dulu → keadaan yang sama = pelanggan berganti)
var aJ2 = __akar(); var JL2 = pasangLayarJual(aJ2, opsiJ()); JL2.keadaan.setel({ pelanggan: 'Acuan' });
var bedaJalur = [];
['sering', 'literan', 'kemasan', 'karung', 'wadah', 'repack'].forEach(function (j) {
  JL.keadaan.setel({ jalur: j }); var html1 = aJ.__html;
  var h8 = susun(function () { JL2.keadaan.setel(Object.assign({}, sJ())); }); var html2 = aJ2.__html;
  if (html1 !== html2 || h8.susunRakLanjut || (j === 'sering' && h8.susunRak !== 1)) { var i = 0; while (i < html1.length && html1[i] === html2[i]) i++; bedaJalur.push(j + ' @' + i + ': ' + html1.slice(i, i + 80) + ' ≠ ' + html2.slice(i, i + 80)); }
});
ok('layar: tiap jalur, rak lanjutan yang tergambar = rak susun penuh di layar kedua (HTML sama)', !bedaJalur.length && (aJ.__html || '').indexOf('chip') >= 0, J(bedaJalur));
print(J({ lulus: lulus, gagal: gagal }));
"""

# ---- CADANGAN TOKO (lokal saja): urutan acak + ongkos
CAD_LOGIKA = r"""
var J = JSON.stringify;
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var med = function (t) { t.sort(function (x, y) { return x - y; }); return t[Math.floor(t.length / 2)]; };
var s = keadaanAwal(); s.sekarang = new Date(TGL + 'T18:00:00+07:00'); sinkronKeranjang(s); var prev = susunRak(s);
var terap = function (p) { s = Object.assign({}, s, p || {}); sinkronKeranjang(s); };
var masuk = function (c, n) { var r = masukkan(Object.assign({}, s, { pilih: c }), n); return r.keranjang ? { keranjang: r.keranjang, urutBaris: r.urutBaris } : null; };
var o = { beda: '', langkah: 0, inkremental: 0 };
function acakDari(b) { var x = b >>> 0 || 1; return function () { x ^= x << 13; x >>>= 0; x ^= x >>> 17; x ^= x << 5; x >>>= 0; return x / 4294967296; }; }
[11, 2026].forEach(function (b) {
  var acak = acakDari(b); var pilih = function (d) { return d[Math.floor(acak() * d.length)]; }; terap({ keranjang: [], antrean: [] }); prev = susunRak(s);
  for (var i = 0; i < 45; i++) {
    var r = acak(); var p = null;
    if (r < 0.4) { var j = pilih(['karung', 'kemasan', 'literan', 'literan', 'repack']); var d = prev[j].filter(function (c) { return c.sisa > 0; }); if (d.length) p = masuk(pilih(d), j === 'literan' ? pilih([1, 2, 5]) : j === 'repack' ? 2 : 1); }
    else if (r < 0.75 && s.keranjang.length) { var bb = pilih(s.keranjang); p = ubahJumlahBaris(s, bb.id, (acak() < 0.6 ? 1 : -1) * (bb.trx.satuan === 'karung' ? 0.5 : 1)); }
    else if (r < 0.85 && s.keranjang.length) p = hapusBaris(s, pilih(s.keranjang).id);
    else if (r < 0.92 && s.keranjang.length) p = parkir(s);
    else if (s.antrean.length) p = pakaiAntrean(s, pilih(s.antrean).id);
    terap(p && !p.kabarAwas ? p : {}); var f = susunRak(s); var l = susunRakLanjut(s, prev); var bd = J(f) === J(l) ? '' : 'beda';
    if (bd && !o.beda) o.beda = 'benih ' + b + ' langkah ' + i; o.langkah += 1;
    if (['karung', 'kemasan', 'literan', 'repack'].some(function (k) { return l[k].some(function (c, x) { return c === prev[k][x]; }); })) o.inkremental += 1;
    prev = l;
  }
});
// ongkos per jenis ketukan: +1 lalu −1 bergantian pada satu baris (keadaan sama untuk penuh & lanjutan)
terap({ keranjang: [], antrean: [] }); prev = susunRak(s);
var cariChip = function (j, pred) { return prev[j].filter(pred)[0]; };
[['karung', function (c) { return c.sisa > 3; }, 1], ['literan', function (c) { return c.wadahLiteran && c.sisa > 10; }, 2], ['kemasan', function (c) { return c.sisa > 3; }, 1], ['repack', function (c) { return c.sisa > 10; }, 2]].forEach(function (x) {
  var c = cariChip(x[0], x[1]); if (!c) return; var m = masuk(c, x[2]); if (m) terap(m); });
prev = susunRak(s); o.baris = s.keranjang.map(function (b) { return b.trx.jenis; });
s.keranjang.forEach(function (b0, i) { var tp = [], tl = [];
  for (var k = 0; k < 9; k++) { var bb = s.keranjang[i]; var lg = bb.trx.satuan === 'karung' ? 0.5 : 1; terap(ubahJumlahBaris(s, bb.id, k % 2 ? -lg : lg));
    var a = Date.now(); susunRak(s); tp.push(Date.now() - a); a = Date.now(); prev = susunRakLanjut(s, prev); tl.push(Date.now() - a); }
  o['ms_' + b0.trx.jenis] = [med(tp), med(tl)]; });
var tp = [], tl = []; var simpan = s.keranjang;
for (var k = 0; k < 7; k++) { var rk = susunRak(s); var c2 = cariChip('karung', function (c) { return c.sisa > 5; }); var m2 = masuk(c2, 1); if (!m2) break; terap(m2);
  var a = Date.now(); susunRak(s); tp.push(Date.now() - a); a = Date.now(); susunRakLanjut(s, rk); tl.push(Date.now() - a); terap({ keranjang: simpan }); }
o.ms_tambahBaris = [med(tp), med(tl)];
o.chip = ['karung', 'kemasan', 'literan', 'repack'].map(function (k) { return prev[k].length; });
print(J(o));
"""

CAD_LAYAR = r"""
var J = JSON.stringify;
setelKunci(false);
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var med = function (t) { t.sort(function (x, y) { return x - y; }); return t[Math.floor(t.length / 2)]; };
var opsiJ = { akun: function () { return null; }, gantiMode: function () {}, mode: function () { return 'gelap'; }, statusTeks: function () { return ''; }, statusAwas: function () { return false; },
  statusRingkas: function () { return ''; }, versiData: function () { return __versi; }, pemegang: function () { return null; }, bukaStok: null };
var aJ = __akar(); var JL = pasangLayarJual(aJ, opsiJ); JL.keadaan.setel({ jalur: 'karung', sekarang: new Date(TGL + 'T18:00:00+07:00') });
var sJ = function () { return JL.keadaan.baca(); };
var rk = (function () { var s = sJ(); sinkronKeranjang(s); return susunRak(s); })();
var c = rk.karung.filter(function (x) { return x.sisa > 5; })[0]; var r = masukkan(Object.assign({}, sJ(), { pilih: c }), 1); JL.keadaan.setel({ keranjang: r.keranjang, urutBaris: r.urutBaris });
var t = []; for (var k = 0; k < 9; k++) { var a = Date.now(); aJ.__aksi.tambahBaris({ id: sJ().keranjang[0].id, langkah: k % 2 ? '-0.5' : '0.5' }); t.push(Date.now() - a); }
print(J({ ketuk_ms: med(t) }));
"""

PENUH_LAYAR = [("_rak = _rak && !_rakBasi && _rakDasar === dasar ? L.susunRakLanjut(s, _rak) : L.susunRak(s);", "_rak = L.susunRak(s);")]


def cadangan():
    p = os.environ.get('CADANGAN_TOKO')
    return p if p and os.path.exists(p) else uji_wadah_bernama.cadangan_toko()


def bundel(ganti_logika=None, ganti_layar=None):
    js, lay, _app = uji_cache_chip_literan.bundel(ganti_layar)
    for lama, baru in (ganti_logika or []):
        n = js.count(lama); assert n == 1, 'kontrol basi: ' + lama[:90] + ' (' + str(n) + '×)'
        js = js.replace(lama, baru)
    return js, lay


def jalan(ganti_logika=None, ganti_layar=None):
    js, lay = bundel(ganti_logika, ganti_layar)
    kotak = '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n'
    g, l = [], 0
    h, e = uji_wadah_bernama.jalan(JAM_TETAP + js + uji_cache_chip_literan.PROKSI + BUNGKUS + kotak + SKENARIO)
    if h is None: g.append('LOGIKA: JSC JATUH ' + e)
    else: l += h['lulus']; g += h['gagal']
    h, e = uji_wadah_bernama.jalan(JAM_TETAP + js + uji_cache_chip_literan.PROKSI + lay + kotak + LAYAR)
    if h is None: g.append('LAYAR: JSC JATUH ' + e)
    else: l += h['lulus']; g += h['gagal']
    return l, g


def jalan_cadangan(p):
    cad, tgl = uji_wadah_bernama.cad_js(p)
    tambah = '\nvar CAD = ' + cad + ';\nvar TGL = ' + json.dumps(tgl) + ';\n'
    js, lay = bundel()
    hL, eL = uji_wadah_bernama.jalan(js + tambah + CAD_LOGIKA)
    out = {'logika': hL if hL else 'JATUH ' + eL[-300:]}
    for nama, ganti in (('ketuk_sesudah', None), ('ketuk_sebelum', PENUH_LAYAR)):
        js2, lay2 = bundel(None, ganti)
        h, e = uji_wadah_bernama.jalan(js2 + uji_cache_chip_literan.PROKSI + lay2 + tambah + CAD_LAYAR)
        out[nama] = h['ketuk_ms'] if h else 'JATUH ' + e[-300:]
    return out


# kerusakan yang wajib ketahuan — (nama, ganti di bundel logika, ganti di layar jual.js)
RUSAK = [
    ('chip literan wadah tidak pernah dihitung ulang', [("    if (sd !== ig.sidik.literan[i]) {\n      p = c.wadahLiteran ? [] : null;", "    if (false) {\n      p = c.wadahLiteran ? [] : null;")], None),
    ('merek asal isi wadah tidak masuk sidik chip wadah', [("[J.wadah[c.kunci] || '', (pakai || []).map((m) => [m, J.kg[m] || ''])]", "[J.wadah[c.kunci] || '']")], None),
    ('jejak tanpa struk parkir (buang / parkir tak terlihat)', [("[s.keranjang].concat(s.antrean.map((a) => ((a && a.beku) || {}).items || []))", "[s.keranjang]")], None),
    ('jejak dari baris mentah, bukan bentuk "dipegang" (pecahan wadah & ½ karung terlewat)', [("    trxPegang(t).forEach((p) => {\n      const q = p || {};", "    [t].forEach((p) => {\n      const q = p || {};")], None),
    ('jejak kemasan lupa jumlah unit (bonus / +1 kemasan tak terlihat)', [("(pu[k] = pu[k] || []).push(q.jumlahUnit);", "(pu[k] = pu[k] || []).push(1);")], None),
    ('rak Wadah dipakai ulang walau lembarnya berubah', [("rak.wadah = J.lembar === ig.lembar ? rakLama.wadah :", "rak.wadah = true ? rakLama.wadah :")], None),
    ('Sering dipakai dari rak lama (sisa chip Sering basi)', [("const sr = susunSering(s, rak, ig.urutSering); rak.sering = sr.daftar;", "const sr = { daftar: rakLama.sering, urut: ig.urutSering }; rak.sering = sr.daftar;")], None),
    ('kelompok dari rak lama', [("  rak.kelompok = kelompokRak(rak);\n  const sr = susunSering(s, rak, ig.urutSering);", "  rak.kelompok = rakLama.kelompok;\n  const sr = susunSering(s, rak, ig.urutSering);")], None),
    ('tinggi wadah tidak dihitung ulang di lanjutan', [(" geraLiteranLangsung(c.kunci), { wadah: tinggiWadah(c.kunci, s) });", " geraLiteranLangsung(c.kunci));")], None),
    ('versi data tidak diperiksa (data baru → chip lama)', [("if (!ig || ig.versi !== versiCache() || !rakSelaras(s)", "if (!ig || !rakSelaras(s)")], None),
    ('pelanggan tidak diperiksa (Sering pelanggan lain)', [("|| ig.pelanggan !== kunciPelanggan(s.pelanggan) || ig.hari", "|| ig.hari")], None),
    ('hari tidak diperiksa (Sering hari lalu)', [("|| ig.hari !== hariIniIso(s.sekarang)) return susunRak(s);", ") return susunRak(s);")], None),
    ('keranjang belum disinkronkan tetap dilanjutkan', [("if (!ig || ig.versi !== versiCache() || !rakSelaras(s) ||", "if (!ig || ig.versi !== versiCache() ||")], None),
    ('isian #jualKarungBerat tidak dikembalikan ke berat terakhir susun penuh', [("  if (ig.beratAkhir !== null) setelBeratDom(ig.beratAkhir);\n", "")], None),
    ('lanjutan diam-diam selalu susun penuh (tidak inkremental)', [("function susunRakLanjut(s, rakLama) {\n", "function susunRakLanjut(s, rakLama) {\n  if (s) return susunRak(s);\n")], None),
    ('layar: rakKini selalu susun penuh', None, PENUH_LAYAR),
    ('layar: lanjutan walau pelanggan / tukar berubah', None, [("_rakDasar === dasar ? L.susunRakLanjut(s, _rak)", "true ? L.susunRakLanjut(s, _rak)")]),
    ('layar: lanjutan walau rak basi (data baru)', None, [("_rak = _rak && !_rakBasi && _rakDasar === dasar ?", "_rak = _rak && _rakDasar === dasar ?")]),
]


def main():
    if '--kontrol' in sys.argv:
        diam = 0
        for nama, gl, gy in RUSAK:
            try: l, g = jalan(gl, gy)
            except AssertionError as e: print('KONTROL BASI ' + nama + ' — ' + str(e)); diam += 1; continue
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + (' → ' + g[0][:160] if g else ''))
            if not g: diam += 1
        print('kontrol: %d/%d berbunyi' % (len(RUSAK) - diam, len(RUSAK))); return 3 if diam else 0
    l, g = jalan()
    print('RAK INKREMENTAL (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    p = cadangan()
    if p:
        h = jalan_cadangan(p); lg = h.get('logika')
        print('DATA TOKO (%s): %s' % (os.path.basename(p), json.dumps(h, ensure_ascii=False)))
        if not isinstance(lg, dict) or lg.get('beda') or not lg.get('langkah'):
            g.append('data toko: lanjutan ≠ susun penuh atau jatuh — ' + json.dumps(lg, ensure_ascii=False)[:300])
            print('   ✗ ' + g[-1])
    else: print('DATA TOKO: dilewati — tidak ada _privat/backup-batch-*.json (worktree / CI)')
    return 1 if g else 0


if __name__ == '__main__':
    sys.exit(main())
