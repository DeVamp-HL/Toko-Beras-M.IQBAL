#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_kelas_merek.py — putaran 30: HARGA BELI PER KELAS MUTU (owner 28 Sep 2026: pemasok mengganti nama merek walau barangnya sama).
  · Peta merek → kelas = dokumen aturanToko/kelasMerek {peta, asal (owner|tebakan), kelasSendiri} — LAPISAN BACA; buku stok per merek tidak berubah.
  · Kelas = nama wadah (aturan wadah), atau merek berbuku yang dipilih owner. Kelas TANPA WADAH (kelasSendiri): kedatangan merek pemasok dibukukan
    ATAS NAMA KELAS + kolom `merkPemasok` di baris batchMasuk (mesin beku & cadangan mengabaikannya).
  · Tebakan hanya dari nama = nama wadah · karung ber-wadah (terbaru) · resep wadah. Tidak dari harga / jenis beras.
  · Harga lalu kelas memakai ulang riwayatModal (stok-hpp): kedatangan nyata saja, pemasok yang dipilih diutamakan, batch yang dikoreksi tidak dipakai.
  · Barang masuk: merek baru → pil kelas; ▲▼= vs harga lalu; beda > batasVarian dari kelas = kalimat lunak, TIDAK memblokir; peta ditulis DALAM kiriman
    Simpan barang masuk yang sama (tebakan yang dibiarkan ditulis sebagai tebakan). Kartu "Per kelas" di Stok › HPP: rata-rata tertimbang per bulan,
    batas periode data disebut. Ganti nama wadah membawa peta kelas di kiriman yang sama.
KOTAK PASIR (angka contoh), jam dikunci 19 Sep 2026 10:00 WIB. Cadangan toko di _privat/ (kalau ada): tebakan hanya menunjuk wadah yang ada,
riwayat kelas per nama = riwayatModal, harga lalu kelas untuk merek kedatangan terbaru = kedatangan nyata terakhir kelas itu SEBELUM batch itu.

    python3 alat-uji/uji_kelas_merek.py            → N lulus · 0 gagal
    python3 alat-uji/uji_kelas_merek.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kunci_periode, uji_varian_merek  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_varian_merek.MODUL
LAYAR = ['baru/js/layar/stok.js', 'baru/js/layar/harga.js', 'firestore.rules', 'baru/js/layar/wadah-bernama-logika.js']
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def baris(merk, n, harga, berat=50, ekstra=None):
    return dict({'id': str(n), 'merk': merk, 'satuan': 'karung', 'beratKarung': berat, 'jumlahKarung': n, 'totalKg': n * berat, 'hargaPerKg': harga, 'subtotalHarga': n * berat * harga}, **(ekstra or {}))


KOTAK = {
  'batchMasuk': [
    {'id': 1000, 'tanggal': '2026-08-08', 'jam': '08:00', 'pemasok': 'STOK AWAL', 'stokAwal': True, 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [baris('IR64 Apex', 2, 14000), baris('Ketan Putih', 1, 20000)]},
    {'id': 1001, 'tanggal': '2026-08-25', 'jam': '09:00', 'pemasok': 'PEMASOK A', 'caraBayar': 'utang', 'biayaBongkar': 0, 'merkList': [baris('IR64 Apex', 10, 14300), baris('Ketan Putih', 2, 21000), baris('IR42 Value', 3, 16600)]},
    {'id': 1002, 'tanggal': '2026-09-10', 'jam': '09:00', 'pemasok': 'PEMASOK B', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [baris('IR64 Apex', 8, 14400), baris('Kumala', 10, 14000), baris('LL', 10, 14000)]},
    {'id': 1003, 'tanggal': '2026-09-18', 'jam': '09:00', 'pemasok': 'PEMASOK A', 'caraBayar': 'utang', 'biayaBongkar': 0, 'merkList': [baris('PM', 11, 13900), baris('Ketan Putih', 3, 21600)]},
    {'id': 1004, 'tanggal': '2026-09-18', 'jam': '10:00', 'pemasok': 'LAHIR BUKU', 'stokAwal': True, 'lahirBuku': True, 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [{'id': '1', 'merk': 'Wadah Angsa', 'satuan': 'lahir', 'jumlahKarung': 0, 'beratKarung': 50, 'totalKg': 0, 'hargaPerKg': 0, 'subtotalHarga': 0, 'stokWadah': 'Angsa'}]},
  ],
  'wadahLiteran': [
    {'id': 5000, 'tanggal': '2026-09-01', 'jam': '08:00', 'tipe': 'atur', 'penuhKg': 50, 'puncakKg': 60, 'isiUlangKg': 10, 'takarKg': 1.8, 'susutWajarKg': 1, 'sisihKg': 10,
     'daftar': ['IR64 Apex', 'Angsa', 'IR64 Elevate', 'IR42 Value'], 'merekKarung': ['Angsa'], 'resep': {'IR42 Value': [{'merk': 'LL', 'takar': 1}]}, 'literanLangsung': ['Ketan Putih']},
    {'id': 5001, 'tanggal': '2026-09-11', 'jam': '08:00', 'tipe': 'karung', 'merk': 'Kumala', 'wadah': 'IR64 Apex', 'kg': 50},
    {'id': 5002, 'tanggal': '2026-09-12', 'jam': '08:00', 'tipe': 'karung', 'merk': 'Kumala', 'wadah': 'IR64 Elevate', 'kg': 50},
    {'id': 5003, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'karung', 'merk': 'PM', 'wadah': 'IR64 Apex', 'kg': 50},
    {'id': 5004, 'tanggal': '2026-09-19', 'jam': '08:30', 'tipe': 'karung', 'merk': 'NG', 'wadah': 'IR64 Elevate', 'kg': 50},
  ],
  'katalogHargaKarung': [{'id': 'LL', 'merk': 'LL', 'hargaPerKg': 14800}, {'id': 'Kumala', 'merk': 'Kumala', 'hargaPerKg': 14500}],
  'pengaturan': [{'id': 'jenisBeras', 'peta': {'PM': 'IR64', 'TH': 'IR64', 'SB': 'IR42', 'CM': 'Ketan Putih', 'Kumala': 'IR64'}}],
  'aturanToko': [{'id': 'harga', 'targetPerKg': 500, 'bulatKarung': 100, 'bulatLiter': 500, 'bulatKemasan': 1000, 'langkahRp': 50, 'ambangDampak': 50000, 'bongkarKg': 0, 'mdrPersen': 30, 'mdrBatas': 500000}],
  'penjualan': [], 'hargaTerbit': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
var KOL = ['batchMasuk', 'wadahLiteran', 'katalogHargaKarung', 'pengaturan', 'aturanToko', 'penjualan', 'hargaTerbit'];
var pulih = function () { KOL.forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n] || []))); }); };
pulih();
var nId = 9000; var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var draf = function (baris, ubah) { return Object.assign({ id: null, tanggal: '2026-09-19', pemasok: 'PEMASOK B', caraBayar: 'tunai', bongkar: '', alasan: '', baris: baris }, ubah || {}); };
var brs = function (merk, n, harga, ubah) { return Object.assign({ merk: merk, jumlahKarung: String(n), beratKarung: 50, hargaPerKg: String(harga) }, ubah || {}); };
var stok = function (m) { return hitungStokKarungPerMerk()[m] || {}; };
var terapkan = function (r) { terapkanKeCache((r && r.dokumen) || []); return r; };
var dokKM = function (r) { return ((r && r.dokumen) || []).find(function (d) { return d.koleksi === 'aturanToko' && d.data.id === 'kelasMerek'; }) || null; };
var K = function (m) { return kmKelasMerk(m); };

// ---- 1 · membaca tanpa dokumen (cadangan lama): nama wadah = kelasnya sendiri; tebakan tiga sumber; selain itu kosong
ok('tanpa dokumen kelasMerek: kmPeta kosong & ada=false; nama wadah (IR64 Apex, Angsa yang juga merek karung) = kelas dirinya, asal wadah', !kmPeta().ada && J(kmPeta().peta) === '{}' && J(K('IR64 Apex')) === J({ kelas: 'IR64 Apex', asal: 'wadah' }) && J(K('Angsa')) === J({ kelas: 'Angsa', asal: 'wadah' }), J([kmPeta(), K('IR64 Apex')]));
ok('tebakan karung ber-wadah: Kumala → IR64 Elevate (catatan TERBARU 12 Sep menang atas 11 Sep ke Apex); PM → IR64 Apex; NG (belum berbuku) → IR64 Elevate', J(K('Kumala')) === J({ kelas: 'IR64 Elevate', asal: 'tebakan' }) && J(K('PM')) === J({ kelas: 'IR64 Apex', asal: 'tebakan' }) && J(K('NG')) === J({ kelas: 'IR64 Elevate', asal: 'tebakan' }), J([K('Kumala'), K('PM'), K('NG')]));
ok('tebakan resep wadah: LL ada di resep IR42 Value → IR42 Value; Ketan Putih & TH (tanpa petunjuk) → kosong — jenis beras BUKAN tebakan', J(K('LL')) === J({ kelas: 'IR42 Value', asal: 'tebakan' }) && J(K('Ketan Putih')) === J({ kelas: '', asal: '' }) && J(K('TH')) === J({ kelas: '', asal: '' }), J([K('LL'), K('Ketan Putih'), K('TH')]));
var D1 = kmDaftar();
ok('daftar Kelas mutu: 6 merek berbuku (IR42 Value, IR64 Apex, Ketan Putih, Kumala, LL, PM); terisi 2 (dua nama wadah); belum dikonfirmasi 4; usulan kelas tanpa wadah = literan langsung (Ketan Putih); petunjuk jenis beras ikut',
  J(D1.baris.map(function (b) { return b.merk; })) === J(['IR42 Value', 'IR64 Apex', 'Ketan Putih', 'Kumala', 'LL', 'PM']) && D1.terisi === 2 && D1.total === 6 && J(D1.belumKonfirmasi) === J(['Ketan Putih', 'Kumala', 'LL', 'PM']) && J(D1.usulSendiri) === J(['Ketan Putih']) && D1.baris.find(function (b) { return b.merk === 'PM'; }).petunjuk === 'IR64', J(D1));
ok('pil kelas: nama wadah dulu (urutan kotak di toko), lalu merek berbuku bukan varian yang belum dipetakan; tanpa buku khusus', J(kmCalonKelas().map(function (c) { return c.nama + ':' + c.jenis; })) === J(['IR64 Apex:wadah', 'Angsa:wadah', 'IR64 Elevate:wadah', 'IR42 Value:wadah', 'Ketan Putih:merek', 'Kumala:merek', 'LL:merek', 'PM:merek']), J(kmCalonKelas()));
// ---- 2 · owner memetakan
var R2 = susunKelasMerk('Kumala', 'IR64 Elevate', W); var d2 = dokKM(R2);
ok('Kumala → IR64 Elevate: SATU dokumen aturanToko/kelasMerek {id, tanggal, jam, diubahPada, peta, asal, kelasSendiri}; peta {Kumala: IR64 Elevate}, asal owner', !R2.tolak && R2.dokumen.length === 1 && d2 && J(Object.keys(d2.data).sort()) === J(['asal', 'diubahPada', 'id', 'jam', 'kelasSendiri', 'peta', 'tanggal']) && J(d2.data.peta) === J({ Kumala: 'IR64 Elevate' }) && J(d2.data.asal) === J({ Kumala: 'owner' }) && J(d2.data.kelasSendiri) === J([]) && d2.data.diubahPada === W.kini, J(R2));
terapkan(R2);
ok('sesudahnya: kelas Kumala = owner; terisi 3; Kumala hilang dari pil kelas (sudah anggota kelas lain); peta yang sama lagi ditolak "sudah berkelas"', J(K('Kumala')) === J({ kelas: 'IR64 Elevate', asal: 'owner' }) && kmDaftar().terisi === 3 && !kmCalonKelas().some(function (c) { return c.nama === 'Kumala'; }) && /sudah berkelas IR64 Elevate/.test(susunKelasMerk('Kumala', 'IR64 Elevate', W).tolak || ''));
ok('ditolak dengan kalimat: nama wadah dipetakan; kelas varian; merek tak dikenal; kelas tak dikenal; kelas = dirinya; buku khusus', /nama WADAH/.test(susunKelasMerk('IR64 Apex', 'Angsa', W).tolak || '') && /VARIAN/.test(susunKelasMerk('LL', 'Kumala · X', W).tolak || '') && /tidak dikenal/.test(susunKelasMerk('Hantu', 'IR64 Apex', W).tolak || '')
  && /tidak dikenal/.test(susunKelasMerk('LL', 'Hantu', W).tolak || '') && /dirinya sendiri/.test(susunKelasMerk('LL', 'LL', W).tolak || '') && /buku khusus/.test(susunKelasMerk('Wadah Angsa', 'Angsa', W).tolak || ''));
var R2b = terapkan(susunKelasMerk('LL', '', W));
ok('"tanpa kelas" = peta LL "" asal owner: menimpa tebakan resep; daftar menyebut tanpa kelas (terisi)', !R2b.tolak && J(K('LL')) === J({ kelas: '', asal: 'owner' }) && kmDaftar().baris.find(function (b) { return b.merk === 'LL'; }).asal === 'owner' && kmDaftar().terisi === 4, J(K('LL')));
ok('merek yang dipilih sebagai kelas merek lain = kelasnya sendiri (asal dipakai), tidak perlu dipetakan', (function () { var r = terapkan(susunKelasMerk('PM', 'Ketan Putih', W)); var out = !r.tolak && J(K('Ketan Putih')) === J({ kelas: 'Ketan Putih', asal: 'dipakai' }) && kmAnggota('Ketan Putih').indexOf('PM') >= 0; pulih(); terapkan(susunKelasMerk('Kumala', 'IR64 Elevate', W)); return out; })());
// ---- 3 · kelas TANPA WADAH (kelasSendiri)
var R3 = susunKelasSendiri('Ketan Putih', true, W); var d3 = dokKM(R3);
ok('tandai Ketan Putih KELAS tanpa wadah: kelasSendiri [Ketan Putih], peta Kumala utuh; sesudahnya asal sendiri; pil kelas menyebutnya sebagai "sendiri"', !R3.tolak && d3 && J(d3.data.kelasSendiri) === J(['Ketan Putih']) && d3.data.peta.Kumala === 'IR64 Elevate' && (terapkan(R3), J(K('Ketan Putih')) === J({ kelas: 'Ketan Putih', asal: 'sendiri' })) && kmCalonKelas().some(function (c) { return c.nama === 'Ketan Putih' && c.jenis === 'sendiri'; }), J(R3));
ok('ditolak: nama wadah ditandai kelas; varian; tak dikenal; sudah ditandai; memetakan kelas sendiri ke kelas lain', /nama WADAH/.test(susunKelasSendiri('Angsa', true, W).tolak || '') && /varian/.test(susunKelasSendiri('LL · X', true, W).tolak || '') && /tidak dikenal/.test(susunKelasSendiri('Hantu', true, W).tolak || '') && /sudah ditandai/.test(susunKelasSendiri('Ketan Putih', true, W).tolak || '') && /ditandai KELAS/.test(susunKelasMerk('Ketan Putih', 'IR64 Apex', W).tolak || ''));
// ---- 4 · riwayat & harga lalu kelas (memakai ulang riwayatModal)
var RK = kmRiwayatKelas('IR64 Apex');
ok('riwayat kelas IR64 Apex = kedatangan nyata anggota (Apex 25 Agu, Apex 10 Sep, PM 18 Sep — PM tebakan karung) lama → baru; stok awal (fondasi) TIDAK ikut; tiap baris = riwayatModal nama itu', J(RK.map(function (r) { return [r.tanggal, r.merk, r.hargaPerKg, r.pemasok]; })) === J([['2026-08-25', 'IR64 Apex', 14300, 'PEMASOK A'], ['2026-09-10', 'IR64 Apex', 14400, 'PEMASOK B'], ['2026-09-18', 'PM', 13900, 'PEMASOK A']])
  && J(RK.filter(function (r) { return r.merk === 'IR64 Apex'; }).map(function (r) { return [r.batchId, r.hargaPerKg, r.hppPerKg, r.totalKg]; })) === J(riwayatModal('IR64 Apex').filter(function (r) { return r.jenis === 'kedatangan' && !r.fondasi; }).map(function (r) { return [r.batchId, r.hargaPerKg, r.hppPerKg, r.totalKg]; })), J(RK));
var L4a = kmHargaLaluKelas('IR64 Apex', 'PEMASOK B'); var L4b = kmHargaLaluKelas('IR64 Apex', ''); var L4c = kmHargaLaluKelas('IR64 Apex', '', 1003);
ok('harga lalu kelas: pemasok yang dipilih diutamakan (PEMASOK B → Apex 14.400 · 10 Sep; lain: PEMASOK A PM 13.900 · 18 Sep); tanpa pemasok → terbaru siapa pun (PM 13.900); batch yang dikoreksi (1003) tidak dipakai → Apex 14.400',
  L4a && L4a.harga === 14400 && L4a.merk === 'IR64 Apex' && L4a.pemasok === 'PEMASOK B' && L4a.tanggalTeks === '10 Sep' && L4a.dariPemasokDipilih === true && L4a.lain.length === 1 && L4a.lain[0].pemasok === 'PEMASOK A' && L4a.lain[0].harga === 13900 && L4a.lain[0].merk === 'PM'
  && L4b.harga === 13900 && L4b.dariPemasokDipilih === false && L4b.lain[0].harga === 14400 && L4c.harga === 14400 && L4c.pemasok === 'PEMASOK B', J([L4a, L4b, L4c]));
ok('kelas tanpa kedatangan nyata (Angsa) → null; harga lalu MEREK: angka = mesin (LL 14.000 · 10 Sep · PEMASOK B); Apex = 14.400 (id terbesar); saat koreksi batch 1002 → kedatangan sebelumnya 14.300 · 25 Agu; nama asing → null',
  kmHargaLaluKelas('Angsa', '') === null && J(kmHargaLaluMerk('LL')) === J({ merk: 'LL', harga: 14000, tanggal: '2026-09-10', tanggalTeks: '10 Sep', pemasok: 'PEMASOK B', fondasi: false, merkPemasok: '' }) && kmHargaLaluMerk('IR64 Apex').harga === 14400 && kmHargaLaluMerk('IR64 Apex', 1002).harga === 14300 && kmHargaLaluMerk('IR64 Apex', 1002).tanggalTeks === '25 Agu' && kmHargaLaluMerk('Hantu') === null, J([kmHargaLaluMerk('LL'), kmHargaLaluMerk('IR64 Apex', 1002)]));
ok('▲▼=: 14.200 vs 14.000 = naik Rp200 (1,4 %); 13.800 = turun Rp200; sama; tanpa lalu = kosong', J(kmArah(14200, 14000)) === J({ arah: 'naik', selisih: 200, persen: 1.4, teks: '▲ naik Rp200 dari lalu' }) && kmArah(13800, 14000).teks === '▼ turun Rp200 dari lalu' && kmArah(14000, 14000).arah === 'sama' && kmArah(14000, 0).teks === '', J(kmArah(14200, 14000)));
ok('kalimat lunak: 15.200 vs kelas 14.400 (5,6 % > batas 5 %) menyebut kelas, harga lalu, nama asal, tanggal, pemasok, "kelasnya benar?"; 14.600 (1,4 %) = kosong', /^beda 5,6 % dari kelas IR64 Apex \(lalu Rp14\.400 · IR64 Apex · 10 Sep · PEMASOK B\) — kelasnya benar\?$/.test(kmKalimatKelas(15200, L4a)) && kmKalimatKelas(14600, L4a) === '' && kmKalimatKelas(15200, null) === '', kmKalimatKelas(15200, L4a));
// ---- 5 · Barang masuk: merek baru → pil kelas; simpan TIDAK menunggu kelas; peta ditulis dalam kiriman yang sama
var H5 = hitungMasuk(draf([brs('TH', 4, 14600), brs('LL', 2, 14200)])); var b5 = H5.baris[0]; var l5 = H5.baris[1];
ok('TH (belum ada buku/katalog) = merek BARU: tanpa kelas & tanpa tebakan, pil kelas 7 pilihan (4 wadah, Ketan Putih sebagai kelas sendiri, LL, PM — Kumala sudah anggota kelas lain), harga lalu kosong; LL (dikenal) bukan baru: lalu 14.000 · 10 Sep · PEMASOK B, ▲ naik Rp200', b5.baru === true && b5.kelas === '' && b5.kelasAsal === '' && b5.calonKelas.length === 7 && b5.calonKelas.some(function (c) { return c.nama === 'Ketan Putih' && c.jenis === 'sendiri'; }) && !b5.calonKelas.some(function (c) { return c.nama === 'Kumala'; }) && b5.lalu === null && b5.laluKelas === null && b5.arah.teks === ''
  && l5.baru === false && l5.lalu.harga === 14000 && l5.lalu.tanggalTeks === '10 Sep' && l5.lalu.pemasok === 'PEMASOK B' && l5.arah.teks === '▲ naik Rp200 dari lalu' && l5.hargaLalu === 14000, J([b5, l5]));
var R5 = susunSimpanMasuk(draf([brs('TH', 4, 14600)]), W, true);
ok('simpan TH tanpa kelas: SAH (satu dokumen batchMasuk, kolom baris PERSIS sistem berjalan, tanpa merkPemasok/kelas); tidak ada dokumen peta', !R5.tolak && R5.dokumen.length === 1 && R5.dokumen[0].koleksi === 'batchMasuk' && J(Object.keys(R5.dokumen[0].data.merkList[0]).sort()) === J(['beratKarung', 'hargaPerKg', 'id', 'jumlahKarung', 'merk', 'satuan', 'subtotalHarga', 'totalKg']) && !dokKM(R5), J(R5));
var H5b = hitungMasuk(draf([brs('TH', 4, 14600, { kelas: 'IR64 Apex', kelasPilih: true })])); var b5b = H5b.baris[0];
ok('TH + kelas IR64 Apex (pilihan owner, pemasok B): harga lalu kelas = Apex 14.400 · 10 Sep · PEMASOK B (pemasok B diutamakan), lain PM 13.900; ▲ naik Rp200; tidak ada kalimat lunak (1,4 %)', b5b.kelas === 'IR64 Apex' && b5b.kelasAsal === 'owner' && b5b.keSendiri === false && b5b.merk === 'TH' && b5b.laluKelas.harga === 14400 && b5b.laluKelas.pemasok === 'PEMASOK B' && b5b.laluKelas.lain[0].merk === 'PM' && b5b.arah.teks === '▲ naik Rp200 dari lalu' && b5b.kelasTanya === '', J(b5b));
var H5c = hitungMasuk(draf([brs('TH', 4, 15200, { kelas: 'IR64 Apex', kelasPilih: true })])); var R5c = susunSimpanMasuk(draf([brs('TH', 4, 15200, { kelas: 'IR64 Apex', kelasPilih: true })]), W, true); var d5c = dokKM(R5c);
ok('TH @15.200 (5,6 % dari kelas): kalimat lunak muncul, simpan TETAP SAH; kiriman = batchMasuk (buku TH sendiri, tanpa merkPemasok) + aturanToko/kelasMerek {TH: IR64 Apex, asal owner}; kabar menyebut kelas', /kelasnya benar\?/.test(H5c.baris[0].kelasTanya) && !R5c.tolak && R5c.dokumen.length === 2 && R5c.dokumen[0].data.merkList[0].merk === 'TH' && !('merkPemasok' in R5c.dokumen[0].data.merkList[0]) && d5c && d5c.data.peta.TH === 'IR64 Apex' && d5c.data.asal.TH === 'owner' && d5c.data.peta.Kumala === 'IR64 Elevate' && /Kelas: TH → kelas IR64 Apex/.test(R5c.patch.kabar), J(R5c));
terapkan(R5c);
ok('sesudah tersimpan: TH dikenal (bukan baru lagi), kelas owner; kedatangan berikutnya TH: lalu = TH sendiri 15.200; kelas IR64 Apex kini beranggota TH & harga lalu kelasnya 15.200 (TH · 19 Sep)', hitungMasuk(draf([brs('TH', 1, 15000)])).baris[0].baru === false && J(K('TH')) === J({ kelas: 'IR64 Apex', asal: 'owner' }) && hitungMasuk(draf([brs('TH', 1, 15000)])).baris[0].lalu.harga === 15200 && kmAnggota('IR64 Apex').indexOf('TH') >= 0 && kmHargaLaluKelas('IR64 Apex', '').harga === 15200 && kmHargaLaluKelas('IR64 Apex', '').merk === 'TH', J(kmHargaLaluKelas('IR64 Apex', '')));
ok('simpan ditolak (jumlah kosong) → tidak ada dokumen apa pun, peta tidak tertulis; kelas asing di draf ditolak dengan kalimat', (function () { var r = susunSimpanMasuk(draf([brs('SB', '', 16300, { kelas: 'IR42 Value', kelasPilih: true })]), W, true); var r2 = susunSimpanMasuk(draf([brs('SB', 4, 16300, { kelas: 'Hantu', kelasPilih: true })]), W, true); return !!r.tolak && !r.dokumen && /kelas "Hantu" tidak dikenal/.test(r2.tolak || ''); })());
ok('koreksi kedatangan lama: kelas tidak ditanya (baru=false), harga lalu = kedatangan SEBELUM batch itu', (function () { var d = drafDariKedatangan(1002); var h = hitungMasuk(d); var a = h.baris.find(function (b) { return b.merk === 'IR64 Apex'; }); return a.baru === false && a.lalu.harga === 14300 && a.lalu.tanggalTeks === '25 Agu'; })());
// ---- 6 · tebakan yang dibiarkan ikut ditulis SEBAGAI tebakan; keputusan owner tidak ditimpa
var H6 = hitungMasuk(draf([brs('NG', 5, 14100)])); var R6 = susunSimpanMasuk(draf([brs('NG', 5, 14100)]), W, true); var d6 = dokKM(R6);
ok('NG (baru, karung tercatat di belakang IR64 Elevate): kelas tebakan IR64 Elevate; harga lalu kelas = Kumala 14.000 · 10 Sep (anggota Elevate); simpan menulis peta {NG: IR64 Elevate, asal TEBAKAN}', H6.baris[0].kelas === 'IR64 Elevate' && H6.baris[0].kelasAsal === 'tebakan' && H6.baris[0].laluKelas.merk === 'Kumala' && H6.baris[0].laluKelas.harga === 14000 && !R6.tolak && d6 && d6.data.peta.NG === 'IR64 Elevate' && d6.data.asal.NG === 'tebakan', J([H6.baris[0], d6]));
terapkan(R6);
ok('daftar menandai NG belum dikonfirmasi (tebakan tersimpan ≠ keputusan owner); konfirmasi owner → asal owner; sesudahnya tebakan tidak menimpa (kmDokKelas null)', kmDaftar().belumKonfirmasi.indexOf('NG') >= 0 && J(K('NG')) === J({ kelas: 'IR64 Elevate', asal: 'tebakan' }) && (terapkan(susunKelasMerk('NG', 'IR64 Elevate', W)), J(K('NG')) === J({ kelas: 'IR64 Elevate', asal: 'owner' })) && kmDokKelas([{ merk: 'NG', kelas: 'IR64 Apex', asal: 'tebakan' }], W) === null && kmDaftar().belumKonfirmasi.indexOf('NG') < 0);
ok('pilihan "tanpa kelas" saat barang masuk (kelasPilih, kelas "") ditulis sebagai keputusan owner; merek baru tanpa petunjuk & tanpa pilihan tidak ditulis', (function () { var r = susunSimpanMasuk(draf([brs('SB', 4, 16300, { kelas: '', kelasPilih: true })]), W, true); var d = dokKM(r); var r2 = susunSimpanMasuk(draf([brs('II', 4, 15300)]), W, true); return d && d.data.peta.SB === '' && d.data.asal.SB === 'owner' && !dokKM(r2); })());
// ---- 7 · kelas TANPA WADAH: dibukukan atas nama kelas + merkPemasok
var kpSebelum = J(stok('Ketan Putih')); var H7 = hitungMasuk(draf([brs('CM', 2, 21600, { kelas: 'Ketan Putih', kelasPilih: true })], { pemasok: 'PEMASOK A' })); var b7 = H7.baris[0];
ok('CM (baru) → kelas Ketan Putih (tanpa wadah): baris dibukukan ATAS NAMA Ketan Putih, merkPemasok CM; petunjuk = lalu Ketan Putih 21.600 · 18 Sep · PEMASOK A; = sama', b7.keSendiri === true && b7.merk === 'Ketan Putih' && b7.merkSimpan === 'Ketan Putih' && b7.merkPemasok === 'CM' && b7.merkKetik === 'CM' && b7.lalu.harga === 21600 && b7.lalu.tanggalTeks === '18 Sep' && b7.arah.arah === 'sama' && b7.laluKelas === null, J(b7));
var R7 = susunSimpanMasuk(draf([brs('CM', 2, 21600, { kelas: 'Ketan Putih', kelasPilih: true })], { pemasok: 'PEMASOK A' }), W, true); var m7 = R7.dokumen && R7.dokumen[0].data.merkList[0];
ok('simpan: merkList[0] = {kolom sistem berjalan + merkPemasok CM}, merk Ketan Putih; TIDAK ada dokumen peta (CM tidak dipetakan — merkPemasok cukup); kabar menyebut "CM dibukukan sebagai Ketan Putih"', !R7.tolak && R7.dokumen.length === 1 && m7.merk === 'Ketan Putih' && m7.merkPemasok === 'CM' && J(Object.keys(m7).sort()) === J(['beratKarung', 'hargaPerKg', 'id', 'jumlahKarung', 'merk', 'merkPemasok', 'satuan', 'subtotalHarga', 'totalKg']) && !dokKM(R7) && /CM dibukukan sebagai Ketan Putih/.test(R7.patch.kabar), J(R7));
terapkan(R7);
ok('buku Ketan Putih sesudah kedatangan CM = sisa lama 300 + 100 kg = 400; modal rata-rata biasa (50×20.000 + 100×21.000 + 150×21.600 + 100×21.600) / 400; TIDAK ada buku "CM"', stok('Ketan Putih').sisaKg === 400 && Math.abs(stok('Ketan Putih').hppTerakhirPerKg - (50 * 20000 + 100 * 21000 + 150 * 21600 + 100 * 21600) / 400) < 0.001 && !hitungStokKarungPerMerk().CM, J([kpSebelum, stok('Ketan Putih')]));
ok('mesin beku mengabaikan merkPemasok: buku stok byte-sama dengan kolom itu dibuang', (function () { var s1 = J(hitungStokKarungPerMerk()); var B0 = JSON.parse(J(ambilSemuaBatch())); var B = JSON.parse(J(B0)); var n = 0; B.forEach(function (b) { (b.merkList || []).forEach(function (m) { if (m.merkPemasok) n += 1; delete m.merkPemasok; }); }); pasok('batchMasuk', B); var s2 = J(hitungStokKarungPerMerk()); pasok('batchMasuk', B0); return n === 1 && s1 === s2 && J(hitungStokKarungPerMerk()) === s1; })());
var idCM = R7.dokumen[0].data.id;
ok('buku kedatangan menulis "Ketan Putih (CM) 2×50"; draf koreksi membawa merkPemasok; koreksi harga menyimpan merkPemasok lagi; riwayatModal Ketan Putih baris terakhir merkPemasok CM & sumber "· merek CM"', /Ketan Putih \(CM\) 2×50/.test(daftarKedatangan(3).find(function (k) { return String(k.id) === String(idCM); }).ringkas) && drafDariKedatangan(idCM).baris[0].merkPemasok === 'CM'
  && (function () { var d = drafDariKedatangan(idCM); d.baris[0].hargaPerKg = '21700'; d.alasan = 'salah ketik'; var r = susunSimpanMasuk(d, W, true); return !r.tolak && r.dokumen[0].data.merkList[0].merkPemasok === 'CM' && r.dokumen[0].data.merkList[0].merk === 'Ketan Putih'; })()
  && (function () { var r = riwayatModal('Ketan Putih'); var t = r[r.length - 1]; return t.merkPemasok === 'CM' && /· merek CM/.test(t.sumber); })(), J(riwayatModal('Ketan Putih').slice(-1)));
ok('pertanyaan varian berlaku atas nama KELAS: CM2 @23.000 (beda > 5 % dari modal Ketan Putih) → simpan ditolak sampai dijawab; "sama" → sah atas nama Ketan Putih (merkPemasok CM2); "beda mutu" → "Ketan Putih · Super" + merkPemasok', (function () { var d = function (u) { return draf([brs('CM2', 2, 23000, Object.assign({ kelas: 'Ketan Putih', kelasPilih: true }, u || {}))], { pemasok: 'PEMASOK A' }); };
  var r0 = susunSimpanMasuk(d(), W, true); var r1 = susunSimpanMasuk(d({ varian: 'sama' }), W, true); var r2 = susunSimpanMasuk(d({ varian: 'beda', namaMutu: 'Super' }), W, true);
  return /modal Ketan Putih/.test(r0.tolak || '') && r0.perluVarian === 1 && !r1.tolak && r1.dokumen[0].data.merkList[0].merk === 'Ketan Putih' && r1.dokumen[0].data.merkList[0].merkPemasok === 'CM2' && !r2.tolak && r2.dokumen[0].data.merkList[0].merk === 'Ketan Putih · Super' && r2.dokumen[0].data.merkList[0].merkPemasok === 'CM2'; })());
ok('dua merek pemasok satu kelas tanpa wadah dalam satu mobil = dua baris SAH (bukan "tertulis dua kali"); baris yang sama persis tetap ditolak', (function () { var r = susunSimpanMasuk(draf([brs('CM', 1, 21600, { kelas: 'Ketan Putih', kelasPilih: true }), brs('CM3', 1, 21600, { kelas: 'Ketan Putih', kelasPilih: true })], { pemasok: 'PEMASOK A' }), W, true);
  var r2 = susunSimpanMasuk(draf([brs('CM', 1, 21600, { kelas: 'Ketan Putih', kelasPilih: true }), brs('CM', 1, 21600, { kelas: 'Ketan Putih', kelasPilih: true })], { pemasok: 'PEMASOK A' }), W, true);
  return !r.tolak && r.dokumen[0].data.merkList.length === 2 && r.dokumen[0].data.merkList[1].merkPemasok === 'CM3' && /Ketan Putih \(CM\) 50 kg tertulis dua kali/.test(r2.tolak || ''); })());
ok('KOREKSI kedatangan: baris CM lama (buku CM) diganti ke kelas tanpa wadah Ketan Putih → merkPemasok = CM otomatis (draf mengingat merkAsal); baris lain tidak diberi merkPemasok; merkAsal tidak ditulis ke dokumen', (function () {
  var b0 = { id: 7777, tanggal: '2026-09-19', jam: '09:00', pemasok: 'PEMASOK A', caraBayar: 'utang', biayaBongkar: 0, merkList: [{ id: '1', merk: 'CMX', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 21600, subtotalHarga: 2160000 }, { id: '2', merk: 'LL', satuan: 'karung', beratKarung: 50, jumlahKarung: 1, totalKg: 50, hargaPerKg: 14000, subtotalHarga: 700000 }] };
  return denganCacheSementara([{ koleksi: 'batchMasuk', data: b0 }], function () { var d = drafDariKedatangan(7777); var awal = d.baris[0].merkAsal === 'CMX' && d.baris[1].merkAsal === 'LL'; d.baris[0].merk = 'Ketan Putih'; d.alasan = 'CMX = ketan putih';
    var h = hitungMasuk(d); var r = susunSimpanMasuk(d, W, true); var m = r.dokumen ? r.dokumen[0].data.merkList : [];
    return awal && h.baris[0].merk === 'Ketan Putih' && h.baris[0].merkPemasok === 'CMX' && h.baris[1].merkPemasok === '' && !r.tolak && m[0].merk === 'Ketan Putih' && m[0].merkPemasok === 'CMX' && !('merkPemasok' in m[1]) && !m.some(function (x) { return 'merkAsal' in x; }); }); })());
ok('KOREKSI: nama tidak diganti, diganti ke merek biasa (bukan kelas tanpa wadah), atau baris sudah punya merkPemasok → tidak ada merkPemasok baru / yang lama tidak ditimpa', (function () {
  var b0 = { id: 7778, tanggal: '2026-09-19', jam: '09:00', pemasok: 'PEMASOK A', caraBayar: 'utang', biayaBongkar: 0, merkList: [{ id: '1', merk: 'CMY', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 21600, subtotalHarga: 2160000 }, { id: '2', merk: 'CMW', merkPemasok: 'ZZ', satuan: 'karung', beratKarung: 50, jumlahKarung: 1, totalKg: 50, hargaPerKg: 21600, subtotalHarga: 1080000 }] };
  return denganCacheSementara([{ koleksi: 'batchMasuk', data: b0 }], function () { var d = drafDariKedatangan(7778); var h0 = hitungMasuk(d); d.baris[0].merk = 'LL'; d.baris[1].merk = 'Ketan Putih'; var h1 = hitungMasuk(d);
    return h0.baris[0].merkPemasok === '' && h0.baris[1].merkPemasok === 'ZZ' && h1.baris[0].merkPemasok === '' && h1.baris[1].merkPemasok === 'ZZ'; }); })());
ok('nama kelas sendiri diketik langsung (Ketan Putih) = jalur biasa: bukan merek baru, tanpa merkPemasok', (function () { var h = hitungMasuk(draf([brs('Ketan Putih', 1, 21600)])); return h.baris[0].baru === false && h.baris[0].merkPemasok === '' && h.baris[0].merk === 'Ketan Putih'; })());
// ---- 8 · kartu Per kelas
var KK = kmKartuKelas(); var apex = KK.kartu.find(function (k) { return k.kelas === 'IR64 Apex'; }); var angsa = KK.kartu.find(function (k) { return k.kelas === 'Angsa'; }); var kp = KK.kartu.find(function (k) { return k.kelas === 'Ketan Putih'; });
ok('kartu per kelas: periode "data kedatangan 25 Agu 2026–19 Sep 2026 (2 bulan) — per kuartal belum bisa dibandingkan" (kalimat batas periode WAJIB); kelas = 4 wadah + Ketan Putih (sendiri)', KK.periodeTeks === 'data kedatangan 25 Agu 2026–19 Sep 2026 (2 bulan) — per kuartal belum bisa dibandingkan' && KK.periode.kuartalBisa === false && J(KK.kartu.map(function (k) { return k.kelas + ':' + k.jenis; })) === J(['IR64 Apex:wadah', 'Angsa:wadah', 'IR64 Elevate:wadah', 'IR42 Value:wadah', 'Ketan Putih:sendiri']), J([KK.periodeTeks, KK.kartu.map(function (k) { return k.kelas; })]));
ok('IR64 Apex: anggota IR64 Apex, PM, TH; tiap kedatangan satu garis (4: Apex 25 Agu, Apex 10 Sep, PM 18 Sep, TH 19 Sep) dengan nama asal & pemasok; per bulan tertimbang kg: Agu 14.300 (500 kg) · Sep (400×14.400 + 550×13.900 + 200×15.200)/1.150 = 14.301 → = "sama" 0 %? tidak: ▲/▼ menurut selisih',
  apex && J(apex.anggota) === J(['IR64 Apex', 'PM', 'TH']) && apex.baris.length === 4 && apex.baris[2].merk === 'PM' && apex.baris[2].pemasok === 'PEMASOK A' && apex.baris[3].merk === 'TH' && apex.perBulan.length === 2 && apex.perBulan[0].rata === 14300 && apex.perBulan[0].kg === 500 && apex.perBulan[0].teks === 'bulan pertama berdata'
  && apex.perBulan[1].rata === Math.round((400 * 14400 + 550 * 13900 + 200 * 15200) / 1150) && apex.perBulan[1].n === 3 && apex.perBulan[1].arah === (apex.perBulan[1].rata > 14300 ? 'naik' : apex.perBulan[1].rata < 14300 ? 'turun' : 'sama'), J(apex));
ok('Angsa (tanpa kedatangan nyata): kosong dengan kalimat, bukan angka nol; Ketan Putih (kelas sendiri): garis CM menyebut "Ketan Putih (CM)"; merek tanpa kelas disebut (II — SB "tanpa kelas" pilihan owner tidak); belum dikonfirmasi disebut', angsa && angsa.kosong === true && /belum ada kedatangan/.test(angsa.ketKosong) && angsa.perBulan.length === 0 && kp && kp.baris.some(function (r) { return r.merk === 'Ketan Putih' && r.merkPemasok === 'CM'; }) && KK.tanpaKelas.indexOf('II') < 0 && KK.tanpaKelas.indexOf('SB') < 0 && Array.isArray(KK.belumKonfirmasi), J([angsa, KK.tanpaKelas, KK.belumKonfirmasi]));
ok('bulan tanpa kedatangan tidak digambar nol (Ketan Putih: Agu & Sep saja); per bulan: Ketan Putih Agu 21.000 (100 kg) → Sep (150×21.600 + 100×21.600)/250 = 21.600 ▲ 2,9 % dari Agu 2026', kp.perBulan.length === 2 && kp.perBulan[0].rata === 21000 && kp.perBulan[0].kg === 100 && kp.perBulan[1].rata === 21600 && kp.perBulan[1].kg === 250 && kp.perBulan[1].arah === 'naik' && kp.perBulan[1].teks === '▲ 2,9 % dari Agu 2026', J(kp.perBulan));
ok('dua kuartal berdata → periode menyebut "2 kuartal" dan TIDAK lagi "belum bisa"', (function () { var out = denganCacheSementara([{ koleksi: 'batchMasuk', data: { id: 900, tanggal: '2026-06-20', jam: '08:00', pemasok: 'PEMASOK A', caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ id: '1', merk: 'IR64 Apex', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 14000, subtotalHarga: 1400000 }] } }], function () { return kmKartuKelas(); }); return out.periode.nKuartal === 2 && out.periode.kuartalBisa === true && /2 kuartal\)$/.test(out.periodeTeks) && !/belum bisa/.test(out.periodeTeks); })());
// ---- 9 · ganti nama wadah membawa peta kelas
var GN = kmSusunGantiNamaWadah('IR64 Elevate', 'Elevate Baru', W); var dGN = dokKM(GN);
ok('ganti nama IR64 Elevate → Elevate Baru: aturan wadah baru (wbSusunGantiNama) + dokumen kelasMerek yang nilainya ikut (Kumala & NG → Elevate Baru) di kiriman yang sama; kabar menyebut 2 merek', !GN.tolak && GN.dokumen[0].koleksi === 'wadahLiteran' && GN.dokumen[0].data.daftar[2] === 'Elevate Baru' && dGN && dGN.data.peta.Kumala === 'Elevate Baru' && dGN.data.peta.NG === 'Elevate Baru' && dGN.data.peta.TH === 'IR64 Apex' && /Kelas 2 merek \(Kumala, NG\) ikut jadi Elevate Baru/.test(GN.patch.kabar), J([GN.tolak, dGN, GN.patch]));
terapkan(GN); ok('sesudahnya: kelas Kumala = Elevate Baru (asal owner utuh), anggota Elevate Baru = [Elevate Baru, Kumala, NG]', J(K('Kumala')) === J({ kelas: 'Elevate Baru', asal: 'owner' }) && J(kmAnggota('Elevate Baru')) === J(['Elevate Baru', 'Kumala', 'NG']));
ok('nama baru yang sudah jadi kelas lain ditolak: kelas tanpa wadah (Ketan Putih); merek yang dipakai sebagai kelas; nama wadah lain (aturan lama)', /sudah jadi kelas lain/.test(kmSusunGantiNamaWadah('Angsa', 'Ketan Putih', W).tolak || '') && (function () { terapkan(susunKelasMerk('LL', 'PM', W)); var t = kmSusunGantiNamaWadah('Angsa', 'PM', W).tolak || ''; return /sudah jadi kelas lain/.test(t); })() && /sudah jadi nama wadah/.test(kmSusunGantiNamaWadah('Angsa', 'IR64 Apex', W).tolak || ''));
ok('ganti nama wadah yang tidak dipakai kelas mana pun: tanpa dokumen kelasMerek', !dokKM(kmSusunGantiNamaWadah('IR42 Value', 'Value Baru', W)));
// ---- 10 · dokumen lama tanpa kolom asal / cadangan tanpa dokumen
pulih(); pasok('aturanToko', KOTAK.aturanToko.concat([{ id: 'kelasMerek', peta: { Kumala: 'IR64 Apex' } }]));
ok('dokumen kelasMerek tanpa kolom asal/kelasSendiri (bentuk lebih tua) tetap terbaca: Kumala owner → IR64 Apex, kelasSendiri kosong', J(K('Kumala')) === J({ kelas: 'IR64 Apex', asal: 'owner' }) && kmPeta().kelasSendiri.length === 0);
pulih();

// ---- ASAP DATA TOKO
var asap = null;
if (CADANGAN) {
  Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
  var A = aturWadah(); var D = kmDaftar(); var tebakan = D.baris.filter(function (b) { return b.asal === 'tebakan'; }); var salahTebak = tebakan.filter(function (b) { return A.daftar.indexOf(b.kelas) < 0; }).map(function (b) { return b.merk; });
  var kelasMurni = A.daftar.filter(function (w) { return A.merekKarung.indexOf(w) < 0; });
  var riwayatBeda = A.daftar.filter(function (w) { var a = kmRiwayatKelas(w).filter(function (r) { return r.merk === w; }).map(function (r) { return [r.batchId, r.hargaPerKg, r.totalKg]; }); var b = riwayatModal(w).filter(function (r) { return r.jenis === 'kedatangan' && !r.fondasi; }).map(function (r) { return [r.batchId, r.hargaPerKg, r.totalKg]; }); return J(a) !== J(b); });
  var laluBeda = D.baris.filter(function (b) { var l = kmHargaLaluMerk(b.merk); var st = hitungStokKarungPerMerk()[b.merk]; return st && st.hargaTerakhirPerKg > 0 && (!l || l.harga !== Math.round(st.hargaTerakhirPerKg)); }).map(function (b) { return b.merk; });
  // batch nyata TERBARU: tiap mereknya yang bukan wadah dipetakan (di kotak pasir saja) ke kelas murni pertama → harga lalu kelas = kedatangan nyata terakhir kelas itu SEBELUM batch itu
  var nyata = ambilSemuaBatch().filter(function (b) { return !b.stokAwal && !b.tutupBuku && !b.lahirBuku; }).sort(function (a, b) { return String(b.tanggal).localeCompare(String(a.tanggal)) || (Number(b.id) || 0) - (Number(a.id) || 0); });
  var terbaru = nyata[0]; var K0 = kelasMurni[0]; var merekBaru = terbaru ? (terbaru.merkList || []).filter(function (m) { return m.merk && m.bentuk !== 'bal' && A.daftar.indexOf(m.merk) < 0 && !kmKelasSendiri()[m.merk]; }).map(function (m) { return m.merk; }) : [];
  // kedatangan nyata terakhir kelas itu SEBELUM batch terbaru; satu kedatangan bisa membawa dua anggota kelas yang sama (mis. dua merek dipetakan owner ke
  // satu kelas) → harga lalu kelas boleh salah satunya, tanggalnya harus tanggal kedatangan itu
  var harap = null; nyata.slice(1).some(function (b) { var hs = (b.merkList || []).filter(function (m) { return m.bentuk !== 'bal' && (m.merk === K0 || kmKelasMerk(m.merk).kelas === K0 || merekBaru.indexOf(m.merk) >= 0); }).map(function (m) { return Math.round(Number(m.hargaPerKg)); }); if (hs.length) { harap = { harga: hs, tanggal: b.tanggal }; return true; } return false; });
  var WC = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
  var dokPeta = kmDokKelas(merekBaru.map(function (m) { return { merk: m, kelas: K0, asal: 'owner' }; }), WC);
  var laluKelas = dokPeta ? denganCacheSementara([dokPeta], function () { return kmHargaLaluKelas(K0, '', terbaru.id); }) : null;
  var sebelum = J(hitungStokKarungPerMerk()); var sesudah = dokPeta ? denganCacheSementara([dokPeta], function () { return J(hitungStokKarungPerMerk()); }) : sebelum;
  var kartu = kmKartuKelas();
  asap = { merek: D.total, tertebak: tebakan.length, belum: D.belumKonfirmasi.length, salahTebak: salahTebak, kelasMurni: kelasMurni.length, riwayatBeda: riwayatBeda, laluBeda: laluBeda, batchTerbaru: terbaru ? terbaru.tanggal : '', merekBaru: merekBaru.length, kelasUji: K0, harap: harap, laluKelas: laluKelas ? { harga: laluKelas.harga, tanggal: laluKelas.tanggal } : null, bukuSama: sebelum === sesudah, periode: kartu.periodeTeks, kartuKosong: kartu.kartu.filter(function (k) { return k.kosong; }).map(function (k) { return k.kelas; }) };
}
print(J({ lulus: lulus, gagal: gagal, asap: asap }));
"""


def cadangan_toko():
    c = glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json'))
    return max(c, key=os.path.getmtime) if c else None


def baca(ganti=None):
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(MODUL + LAYAR)))
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def bundel_dari(t):
    return uji_kunci_periode.satu_lingkup('\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL]))


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def periksa_statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    km = t['baru/js/layar/kelas-merek-logika.js']; sk = t['baru/js/layar/stok.js']; hg = t['baru/js/layar/harga.js']; rules = t['firestore.rules']; wb = t['baru/js/layar/wadah-bernama-logika.js']; hp = t['baru/js/layar/stok-hpp-logika.js']
    ok('kelas-merek-logika tanpa DOM, tanpa Date.now sendiri; memakai riwayatModal (stok-hpp) — bukan menghitung batchMasuk sendiri', 'document.' not in km and 'window.' not in km and 'localStorage' not in km and 'riwayatModal' in km and 'ambilSemuaBatch' not in km)
    ok('wadah-bernama-logika TIDAK mengimpor kelas-merek (ganti nama wadah + peta digabung di kmSusunGantiNamaWadah; bundel Jual tetap utuh)', 'kelas-merek-logika' not in wb)
    ok('Stok: ganti nama wadah lewat kmSusunGantiNamaWadah (peta kelas ikut di kiriman yang sama), bukan wbSusunGantiNama langsung', 'KM.kmSusunGantiNamaWadah(merk, baru, waktu())' in sk and 'WB.wbSusunGantiNama(' not in sk)
    ok('Stok › koreksi kedatangan menyebut merek pemasok baris (termasuk yang diambil dari nama lama)', '${koreksi && b.merkPemasok ? h`<div class="pita-info" data-k="mp-${i}">' in sk and '(diambil dari nama lama baris ini)' in sk)
    ok('Stok › Barang masuk: pil kelas (data-aksi mKelas, "tanpa kelas") menulis kelas + kelasPilih ke draf lewat ubahMasuk (ikut localStorage KUNCI_DRAF_MASUK); ▲▼= & kalimat lunak digambar', "mKelas: ({ i, kelas }) => ubahMasuk((d) => { const b = d.baris[Number(i)]; b.kelas = String(kelas || ''); b.kelasPilih = true; })" in sk and 'data-aksi="mKelas"' in sk and '>tanpa kelas</div>' in sk and 'b.kelasTanya' in sk and "b.arah && b.arah.teks" in sk)
    ok('Stok › HPP: tab "Per kelas" (TAB_HPP) → gambarHppKelas memakai kmKartuKelas & menulis periodeTeks (kalimat batas periode data)', "['kelas', 'Per kelas']" in hp and "hp.tab === 'kelas' ? gambarHppKelas()" in sk and 'KM.kmKartuKelas()' in sk and '${K.periodeTeks}' in sk)
    ok('Harga › Katalog: daftar "Kelas mutu · N/M terisi" di samping Jenis beras + lembar pilih kelas (susunKelasMerk / susunKelasSendiri)', '${gambarJenisDaftar(s)}${gambarKelasDaftar(s)}' in hg and 'Kelas mutu · ${D.terisi}/${D.total} terisi' in hg and 'KM.susunKelasMerk(m, kelas || \'\', waktu())' in hg and "KM.susunKelasSendiri(nama, nyala === '1', waktu())" in hg and 'nama ini KELAS, bukan merek' in hg)
    m = re.search(r"match /aturanToko/\{id\} \{\s*allow read: if owner\(\) \|\| \(id in \[([^\]]*)\]", rules)
    ok('rules v4: aturanToko/kelasMerek hanya owner (tidak di daftar id yang terbaca staf); rules tidak diubah untuk putaran ini', m is not None and 'kelasMerek' not in m.group(1))
    sc = t['baru/js/layar/stok-catat-logika.js']; ml = re.search(r"merkList: h\.sah\.map\(\(b, i\) => Object\.assign\(\{ id: String\(i \+ 1\)[^\n]*\n[^\n]*", sc)
    kode_ml = re.sub(r'//[^\n]*', '', ml.group(0)) if ml else ''
    ok('stok-catat: merkPemasok hanya ditulis bila ada (kolom baris sistem berjalan tetap persis); kelas tidak pernah jadi kolom batchMasuk', ml is not None and "b.merkPemasok ? { merkPemasok: b.merkPemasok } : {}" in kode_ml and 'kelas' not in kode_ml.replace('merkPemasok', ''))
    return out


def utama(t, pakai_cadangan):
    cad = 'null'; tgl = ''
    p = cadangan_toko() if pakai_cadangan else None
    if p:
        d = json.load(open(p, encoding='utf-8')); kol = re.findall(r"\{ nama: '(\w+)'", open(os.path.join(AKAR, 'baru/js/data/koleksi.js'), encoding='utf-8').read())
        cad = json.dumps(dict((n, d[n]) for n in kol if isinstance(d.get(n), list))); tgl = str(d.get('diunduhPada', ''))[:10] or os.path.basename(p).split('miqbal-')[-1][:10]
    h, e = jalan(JAM_TETAP + bundel_dari(t) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None, p
    return h['lulus'], h['gagal'], h.get('asap'), p


def semua(ganti=None, bagian=('statis', 'jsc'), pakai_cadangan=False):
    t = baca(ganti); out = []; asap = None; p = None
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        l, g, asap, p = utama(t, pakai_cadangan); out += [('jsc · ' + x, False, '') for x in g] + [('__jsc', not g, l)]
    return out, asap, p


KM_ = 'baru/js/layar/kelas-merek-logika.js'; SC_ = 'baru/js/layar/stok-catat-logika.js'
KONTROL = [
    ('tebakan mengabaikan resep wadah', {KM_: [("const r = A.daftar.find((W) => (A.resep[W] || []).some((x) => String(x.merk) === m)); return r || '';", "return '';")]}, ('jsc',)),
    ('karung ber-wadah TERLAMA yang menang', {KM_: [("const k = wdTerbaru(ambilWadahLiteran().filter(", "const k = (function (d) { return d.slice().sort((a, b) => Number(a.id) - Number(b.id))[0] || null; })(ambilWadahLiteran().filter(")]}, ('jsc',)),
    ('fondasi (stok awal) ikut riwayat kelas', {KM_: [("if (r.jenis !== 'kedatangan' || r.fondasi) return;", "if (r.jenis !== 'kedatangan') return;")]}, ('jsc',)),
    ('batch yang sedang dikoreksi ikut harga lalu kelas', {KM_: [(".filter((r) => !kecualiBatchId || String(r.batchId) !== String(kecualiBatchId)); if (!semua.length) return null;", ".filter(() => true); if (!semua.length) return null;")]}, ('jsc',)),
    ('pemasok yang dipilih tidak diutamakan', {KM_: [("const utama = (p && per[p]) || semua[semua.length - 1];", "const utama = semua[semua.length - 1];")]}, ('jsc',)),
    ('simpan barang masuk DIBLOKIR sampai kelas dipilih', {SC_: [("const kelasSalah = h.sah.find((b) => b.baru && b.kelasPilih && String(draf.baris[b.ke - 1].kelas || '').trim() && !b.kelas);", "const kelasSalah = h.sah.find((b) => b.baru && !b.kelas);")]}, ('jsc',)),
    ('kelas ditulis sebagai kolom batchMasuk & merkPemasok selalu ada', {SC_: [("b.merkPemasok ? { merkPemasok: b.merkPemasok } : {}", "{ merkPemasok: b.merkPemasok || '', kelas: b.kelas || '' }")]}, ('jsc', 'statis')),
    ('kelas tanpa wadah dibukukan atas nama MEREK pemasok', {SC_: [("const merk = keSendiri ? kelasBaris : merkKetik;", "const merk = merkKetik;")]}, ('jsc',)),
    ('tebakan tersamar jadi keputusan owner saat simpan', {KM_: [("const asal = x && x.asal === 'tebakan' ? 'tebakan' : 'owner';", "const asal = 'owner';")]}, ('jsc',)),
    ('keputusan owner ditimpa tebakan', {KM_: [("if (ada && P.asal[m] !== 'tebakan' && asal === 'tebakan') return;   // keputusan owner tidak ditimpa tebakan", "if (false) return;")]}, ('jsc',)),
    ('▲▼ terbalik', {KM_: [("return { arah: d > 0 ? 'naik' : d < 0 ? 'turun' : 'sama',", "return { arah: d < 0 ? 'naik' : d > 0 ? 'turun' : 'sama',")]}, ('jsc',)),
    ('rata-rata bulan tidak tertimbang kg', {KM_: [("per[b].kg += r.totalKg; per[b].nilai += r.hargaPerKg * r.totalKg; per[b].n += 1;", "per[b].kg += 1; per[b].nilai += r.hargaPerKg; per[b].n += 1;")]}, ('jsc',)),
    ('kalimat batas periode data hilang (kuartal digambar walau belum bisa)', {KM_: [("(nKuartal < 2 ? ' — per kuartal belum bisa dibandingkan' : '')", "''")]}, ('jsc',)),
    ('ganti nama wadah meninggalkan nama lama di peta', {KM_: [("if (ikut.length) { ikut.forEach((x) => { P.peta[x] = B; });", "if (ikut.length) { ikut.forEach(() => {});")]}, ('jsc',)),
    ('nama wadah boleh dipetakan ke kelas lain', {KM_: [("if (kmWadah()[m]) return { tolak: m + ' adalah nama WADAH — kelasnya dirinya sendiri, tidak perlu dipetakan' };", "if (false) return {};")]}, ('jsc',)),
    ('koreksi ke kelas tanpa wadah kehilangan nama lama (merkPemasok tidak dibawa)', {SC_: [("const merkPemasok = keSendiri ? merkKetik : bawaAsal ? asalKoreksi : lamaPemasok;", "const merkPemasok = keSendiri ? merkKetik : lamaPemasok;")]}, ('jsc',)),
    ('koreksi menimpa merkPemasok yang sudah ada', {SC_: [("!!sendiri[merkKetik] && !sendiri[asalKoreksi] && !lamaPemasok;", "!!sendiri[merkKetik] && !sendiri[asalKoreksi];")]}, ('jsc',)),
    ('Stok: koreksi tidak menyebut merek pemasok', {'baru/js/layar/stok.js': [("${koreksi && b.merkPemasok ? h`<div class=\"pita-info\" data-k=\"mp-${i}\">", "${false ? h`<div class=\"pita-info\" data-k=\"mp-${i}\">")]}, ('statis',)),
    ('Stok ganti nama wadah tanpa peta kelas', {'baru/js/layar/stok.js': [("KM.kmSusunGantiNamaWadah(merk, baru, waktu())", "WB.wbSusunGantiNama(merk, baru, waktu())")]}, ('statis',)),
    ('rules: staf boleh membaca kelasMerek', {'firestore.rules': [("(id in ['struk', 'pelanggan', 'pelangganKembar', 'catatStok',", "(id in ['kelasMerek', 'struk', 'pelanggan', 'pelangganKembar', 'catatStok',")]}, ('statis',)),
    ('kartu Per kelas tanpa kalimat periode', {'baru/js/layar/stok.js': [("${K.periodeTeks}. Kelas = nama wadah", "Kelas = nama wadah")]}, ('statis',)),
]

if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti, bagian in KONTROL:
            try: h, _, _ = semua(ganti, bagian)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' · ' + str(e)[:140]); kode = 3; continue
            g = [x for x in h if not x[1]]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h, asap, p = semua(pakai_cadangan=True); g = [x for x in h if not x[1]]
    n = sum(1 for x in h if x[1] and x[0] != '__jsc') + next((x[2] for x in h if x[0] == '__jsc'), 0)
    for x in g: print('   ✗ ' + x[0] + (' → ' + json.dumps(x[2], ensure_ascii=False)[:400] if x[2] not in ('', None) else ''))
    print('KELAS MUTU MEREK (putaran 30): %d lulus · %d gagal' % (n, len(g)))
    if asap:
        print('ASAP DATA TOKO (%s): %d merek berbuku · %d tertebak · %d belum dikonfirmasi · tebakan menunjuk wadah yang tidak ada: %s · %d kelas murni · riwayat kelas ≠ riwayatModal: %s · harga lalu merek ≠ mesin: %s · batch terbaru %s: %d merek dipetakan di kotak pasir ke %s → harga lalu kelas %s (harapan %s) · buku byte-sama: %s · %s · kelas kosong: %s'
              % (os.path.basename(p), asap['merek'], asap['tertebak'], asap['belum'], ', '.join(asap['salahTebak']) or 'tidak ada', asap['kelasMurni'], ', '.join(asap['riwayatBeda']) or 'tidak ada', ', '.join(asap['laluBeda']) or 'tidak ada', asap['batchTerbaru'], asap['merekBaru'], asap['kelasUji'], json.dumps(asap['laluKelas']), json.dumps(asap['harap']), asap['bukuSama'], asap['periode'], ', '.join(asap['kartuKosong']) or 'tidak ada'))
        salah = asap['salahTebak'] or asap['riwayatBeda'] or asap['laluBeda'] or not asap['bukuSama'] or (asap['harap'] and (not asap['laluKelas'] or asap['laluKelas']['harga'] not in asap['harap']['harga'] or asap['laluKelas']['tanggal'] != asap['harap']['tanggal'])) or 'belum bisa' not in asap['periode'] and 'kuartal' not in asap['periode']
        if salah: g.append('asap data toko: ' + json.dumps(asap, ensure_ascii=False)[:400]); print('   ✗ asap data toko gagal')
    sys.exit(1 if g else 0)
