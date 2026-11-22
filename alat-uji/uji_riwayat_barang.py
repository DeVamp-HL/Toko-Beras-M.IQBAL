#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_riwayat_barang.py — RIWAYAT & BATAL BARANG (owner 22 Nov 2026, paket riwayat & pembatalan tahap 2), dijalankan ASLI di jsc di atas kotak pasir uji_wadah_satu_buku
(+ 100 lembar karung bekas seperti uji_karung_bekas_lahir). Catatan barang dibuat lewat PENCATAT ASLI (isi ulang tiga ketukan, sisih, cek, cocokkan, pindah tempat),
lalu dibatalkan / dipulihkan lewat riwayat-barang-logika.js.

Keputusan owner yang dijaga:
  (1) isi ulang dibatalkan = SELURUH ketukan: karung yang dibuka balik ke tumpukan, karung bekas yang lahir ikut hilang → semua buku persis seperti sebelum ketukan;
  (2) sudah dihitung sesudahnya → selisih hitungan BERIKUTNYA per buku digeser: buku tetap = hitungan fisik, susut/lebih tidak menghitung salah catatnya dua kali;
  (3) cocokkan dibatalkan PER BARANG.
Ditambah: pulihkan = kembali persis (termasuk geser balik hitungannya), pulihkan dua kali ditolak, pindah tempat (peta kembali, hanya yang terbaru), kedatangan /
aktivasi tampil tanpa tombol, bulan terkunci ditolak, panel Menu tab Barang dirender asli.

    python3 alat-uji/uji_riwayat_barang.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_riwayat_barang.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_wadah_bernama  # noqa: E402
import uji_wadah_satu_buku  # noqa: E402

RBL = 'baru/js/layar/riwayat-barang-logika.js'; MN = 'baru/js/layar/menu.js'; IDX = 'baru/index.html'
_M = uji_wadah_satu_buku.MODUL + ['baru/js/layar/stok-tempat-logika.js', 'baru/js/layar/sistem-logika.js', RBL]   # lengkapi() tidak mengikuti impor: tempat & sistem (stok per lokasi) disebut
MODUL = [m for i, m in enumerate(_M) if m not in _M[:i]]
JAM_TETAP = uji_wadah_satu_buku.JAM_TETAP
KOTAK = json.loads(json.dumps(uji_wadah_satu_buku.KOTAK))
KOTAK['stokBahanLiteran'] = [{'id': 'kb0', 'tipe': 'beli', 'jenis': 'karungbekas', 'jumlah': 100, 'hargaTotal': 150000, 'tanggal': '2026-09-02'}]
KOTAK['aturanToko'] = [{'id': 'tempat', 'daftar': [{'nama': 'Kiri belakang', 'posisi': 'kiri-belakang'}, {'nama': 'Kanan belakang', 'posisi': 'kanan-belakang'}], 'batasTumpuk': 50}]

SKENARIO = uji_wadah_satu_buku.BANTU + r"""
var hasil = [];
function ok(nama, syarat, ket) { hasil.push({ nama: nama, ok: !!syarat, ket: ket === undefined ? '' : (typeof ket === 'string' ? ket : J(ket)) }); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
// tiap ketukan = satu kiriman bernomor berurutan; ketukan berikutnya bernomor jauh (seperti Date.now() + acak di aplikasi)
var nId = 1000000; var WS = function (jam) { nId += 5000; return { tanggal: '2026-09-21', jam: jam, kini: '2026-09-21T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } }; };   // ketukan lain di MENIT YANG SAMA, ±5 detik kemudian
var WJ = function (jam) { nId += 100000; return { tanggal: '2026-09-21', jam: jam, kini: '2026-09-21T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } }; };
var terap = function (R) { if (R.hapus) terapkanKeCache(R.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); terapkanKeCache(R.dokumen || []); return R; };
var semuaBuku = function () { var st = hitungStokKarungPerMerk(); var o = {}; Object.keys(st).sort().forEach(function (m) { if (Math.abs(st[m].sisaKg) > 0.004) o[m] = B2(st[m].sisaKg); }); return J(o); };
var laba = function () { return hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih; };
var kb = function () { var s = hitungStokBahanLiteran().karungbekas || {}; return s.sisaPcs || 0; };
var kolam = function () { return B2(karungBelakang(KB('Angsa', 'Angsa'), 'Angsa').sisaMentahKg || 0); };
var HARI = '2026-09-21';
var baris = function (k) { return rbDaftar(HARI, '').find(function (b) { return b.kunci === k; }); };
var arsip = function (id) { return cacheMentah('bukuHapus').find(function (x) { return x.id === id; }); };
var idBatal = function (R) { return ((R.dokumen || []).find(function (d) { return d.koleksi === 'bukuHapus'; }) || { data: {} }).data.id; };

// ---------- 0 · aktivasi wadah Angsa (tampil, tidak dibatalkan) ----------
terap(wbSusunAktifkan('Angsa', WJ('08:00')));
var S0 = semuaBuku(), K0 = kb(), L0 = laba(), C0 = kolam();
ok('aktivasi wadah tampil di riwayat barang TANPA tombol batal (sebab disebut)', rbDaftar(HARI, '').some(function (b) { return /^Aktivasi wadah Angsa/.test(b.jenis) && !b.bisa && /aktivasi/.test(b.sebab); }), rbDaftar(HARI, ''));

// ---------- 1 · isi ulang tiga ketukan (2 karung dibuka dari tumpukan, satu habis → karung bekas) lalu dibatalkan ----------
var R1 = wbSusunIsiUlangTiga('Angsa', 'Angsa', { jenis: 'kg', kg: '55' }, WJ('08:10'), s0(), {}); terap(R1);
var T1 = dok(R1, 'wadahLiteran').find(function (d) { return d.tipe === 'takar'; }); var nAng = (R1.dokumen || []).filter(function (d) { return d.koleksi !== 'batchMasuk'; }).length;
var S1 = semuaBuku(), K1 = kb(), L1 = laba(), C1 = kolam();
ok('isi ulang 55 kg tercatat: 2 karung dibuka, karung bekas +1 (bahan uji)', !R1.tolak && dok(R1, 'wadahLiteran').filter(function (d) { return d.tipe === 'karung'; }).length === 2 && K1 === K0 + 1 && S1 !== S0, J([R1.tolak, K0, K1]));
var r1 = baris('barang|wadahLiteran|' + T1.id);
ok('riwayat barang: SATU baris untuk ketukan itu (takar + pindah buku + buka karung + karung + karung bekas = ' + nAng + ' catatan), bisa dibatalkan, kalimatnya menyebut karung yang dibuka',
  !!r1 && r1.bisa && r1.anggota + 1 === nAng && /^Isi ulang wadah Angsa · Angsa 55 kg \(\+2 karung dibuka dari tumpukan\)$/.test(r1.jenis)
  && rbDaftar(HARI, '').filter(function (b) { return b.bisa; }).length === 1, [r1, rbDaftar(HARI, '').map(function (b) { return [b.jenis, b.bisa, b.anggota]; })]);
var P1 = rbPeriksa('wadahLiteran', T1.id);
ok('akibat sebelum diketuk: tiap buku yang bergeser disebut, karung bekas ikut batal', !P1.tolak && P1.akibat.some(function (t) { return /karung bekas/i.test(t); }) && P1.akibat.some(function (t) { return /^Buku Angsa \+100 kg/.test(t); }), P1);
ok('membatalkan butuh alasan', /alasan/.test(rbSusunBatal('wadahLiteran', T1.id, '  ', WJ('08:15')).tolak || ''));
var B1 = rbSusunBatal('wadahLiteran', T1.id, 'Salah catat', WJ('08:20')); var A1 = idBatal(B1); terap(B1);
ok('batal isi ulang: SEMUA buku persis seperti sebelum ketukan (karung balik ke tumpukan, wadah & karung belakang kembali), karung bekas kembali, laba kembali, kolam karung kembali',
  semuaBuku() === S0 && kb() === K0 && laba() === L0 && kolam() === C0, [S0, semuaBuku(), K0, kb(), L0, laba(), C0, kolam()]);
ok('arsip Dibatalkan: jenis barang, salinan utuh semua catatan ketukan itu, hilang dari riwayat hari itu',
  !!arsip(A1) && arsip(A1).jenisBatal === 'barang' && arsip(A1).dokumen.length === nAng && !baris('barang|wadahLiteran|' + T1.id), arsip(A1));

// ---------- 2 · pulihkan & pulihkan dua kali ----------
terap(rbSusunPulih(A1, WJ('08:25')));
ok('pulihkan: semua buku, karung bekas, laba, kolam kembali seperti sesudah ketukan; arsip hilang', semuaBuku() === S1 && kb() === K1 && laba() === L1 && kolam() === C1 && !arsip(A1), [S1, semuaBuku(), K1, kb()]);
ok('pulihkan dua kali ditolak', !!rbSusunPulih(A1, WJ('08:26')).tolak);

// ---------- 3 · sisihkan + cek dikosongkan: dibatalkan per ketukan ----------
var Sb = semuaBuku(), Wb = B2(buku('Wadah Angsa'));
var R3 = wbSusunSisih('Angsa', '10', WS('08:27')); terap(R3); var p3 = dok(R3, 'produksiKemasan')[0];
var R3c = wbSusunSisih('Angsa', '5', WS('08:27')); terap(R3c); var p3c = dok(R3c, 'produksiKemasan')[0];   // ketukan kedua, menit yang sama, 5 detik kemudian
var r3 = baris('barang|produksiKemasan|' + p3.id), r3c = baris('barang|produksiKemasan|' + p3c.id);
ok('dua sisih di MENIT YANG SAMA = dua baris terpisah (pindah buku + catatan karung sisihan masing-masing)', !!r3 && r3.bisa && r3.anggota === 1 && /^Sisihkan wadah Angsa → karung sisihan · 10 kg$/.test(r3.jenis)
  && !!r3c && r3c.anggota === 1 && /· 5 kg$/.test(r3c.jenis), [r3, r3c]);
terap(rbSusunBatal('produksiKemasan', p3.id, 'Salah catat', WJ('08:28')));
ok('batal sisih pertama: hanya 10 kg-nya yang kembali, sisih kedua tetap', B2(buku('Wadah Angsa')) === B2(Wb - 5) && !!baris('barang|produksiKemasan|' + p3c.id), [buku('Wadah Angsa'), Wb]);
var B3c = rbSusunBatal('produksiKemasan', p3c.id, 'Salah catat', WJ('08:28')); var A3c = idBatal(B3c); terap(B3c);
ok('batal sisih kedua: buku wadah & karung wadah kembali seperti sebelum keduanya', semuaBuku() === Sb, [Sb, semuaBuku()]);
terapkanKeCache([{ koleksi: 'produksiKemasan', data: p3c }]);   // catatan bernomor sama tertulis lagi (perangkat lain menulis ulang salinan lamanya)
ok('pulihkan ditolak bila catatan bernomor sama sudah ada lagi', /sudah ada lagi/.test(rbSusunPulih(A3c, WJ('08:28')).tolak || ''), rbSusunPulih(A3c, WJ('08:28')));
terapkanKeCache([{ koleksi: 'produksiKemasan', hapus: p3c.id }]);
var R3b = wbSusunCek('Angsa', 'kosong', WJ('08:29')); terap(R3b); var c3 = dok(R3b, 'wadahLiteran').find(function (d) { return d.tipe === 'cek'; });
var r3b = baris('barang|wadahLiteran|' + c3.id);
ok('cek "dikosongkan" = cek + sisih seluruh isi dalam satu baris', !!r3b && r3b.bisa && r3b.anggota === 2 && /dikosongkan/.test(r3b.jenis), r3b);
terap(rbSusunBatal('wadahLiteran', c3.id, 'Salah catat', WJ('08:29')));
ok('batal cek dikosongkan: buku kembali', semuaBuku() === Sb, [Sb, semuaBuku()]);

// ---------- 4 · SUDAH DIHITUNG sesudahnya: hitungan berikutnya digeser ----------
var H4 = {}; H4['wadah|Angsa'] = '0';   // isi ulang tadi ternyata tidak pernah terjadi: wadah ditimbang kosong
var S4 = susunSimpanCocok('wadah', H4, { 'wadah|Angsa': 'uji' }, WJ('08:30'), { sebagian: true, aneh: true, susutPositif: true, ganda: true }); terap(S4);
var py4 = dok(S4, 'penyesuaianStok').find(function (d) { return d.merk === 'Wadah Angsa'; }); var Sh = semuaBuku(), Lh = laba();
ok('cocokkan wadah Angsa 0 kg sesudah isi ulang: susut −55 kg tercatat', !S4.tolak && !!py4 && py4.selisihKg === -55, [S4.tolak, py4]);
var P4 = rbPeriksa('wadahLiteran', T1.id);
ok('akibat menyebut hitungan yang digeser: "Hitungan … Wadah Angsa: selisih −55 kg → 0"', !P4.tolak && P4.akibat.some(function (t) { return /^Hitungan 21 Sep 2026 08:30 · Wadah Angsa: selisih −55 kg → 0 \(nilai −Rp715\.000 → Rp0; stok tetap = hitungan fisik\)$/.test(t); }), P4.akibat || P4.tolak);
var B4 = rbSusunBatal('wadahLiteran', T1.id, 'Salah catat', WJ('08:40')); var A4 = idBatal(B4); var g4 = (B4.dokumen || []).find(function (d) { return d.koleksi === 'penyesuaianStok'; });
ok('hitungan itu digeser: selisih 0, kgSistem ikut (fisik − sistem = selisih), nilai 0, jejak koreksiBatal', !!g4 && g4.data.selisihKg === 0 && B2(g4.data.kgFisik - g4.data.kgSistem) === 0 && g4.data.nilaiRp === 0
  && Array.isArray(g4.data.koreksiBatal) && g4.data.koreksiBatal[0].geser === 55 && g4.data.koreksiBatal[0].batal === A4, g4 && g4.data);
terap(B4);
ok('sesudah batal: buku wadah = hitungan fisik (0), semua buku = sebelum isi ulang, laba = sebelum isi ulang (susut palsu & karung bekas hilang, tidak dua kali)',
  B2(buku('Wadah Angsa')) === 0 && semuaBuku() === S0 && laba() === L0 && kb() === K0, [semuaBuku(), S0, laba(), L0]);
terap(rbSusunPulih(A4, WJ('08:45')));
ok('pulihkan: hitungan digeser balik (−55), buku & laba = sesudah hitungan', semuaBuku() === Sh && laba() === Lh && (ambilPenyesuaianStok().find(function (d) { return d.id === py4.id; }) || {}).selisihKg === -55, [semuaBuku(), Sh, laba(), Lh]);

// ---------- 5 · cocokkan PER BARANG + dua hitungan berurutan ----------
var NG0 = B2(buku('NG')), TNG0 = tump('NG');   // cocokkan tumpukan menghitung TUMPUKAN (karung utuh), bukan seluruh buku
var Ha = {}; Ha['tumpukan|NG'] = String(B2(TNG0 - 50)).replace('.', ','); var Ra = susunSimpanCocok('tumpukan', Ha, { 'tumpukan|NG': 'uji' }, WJ('08:50'), { sebagian: true, aneh: true, susutPositif: true, ganda: true }); terap(Ra);
var pa = dok(Ra, 'penyesuaianStok')[0];
var Hb = {}; Hb['tumpukan|NG'] = String(B2(TNG0 - 60)).replace('.', ','); var Rb = susunSimpanCocok('tumpukan', Hb, { 'tumpukan|NG': 'uji' }, WJ('08:55'), { sebagian: true, aneh: true, susutPositif: true, ganda: true }); terap(Rb);
var pb = dok(Rb, 'penyesuaianStok')[0];
var Hc = {}; Hc['tumpukan|NG'] = String(B2(TNG0 - 65)).replace('.', ','); var Rc = susunSimpanCocok('tumpukan', Hc, { 'tumpukan|NG': 'uji' }, WJ('08:57'), { sebagian: true, aneh: true, susutPositif: true, ganda: true }); terap(Rc);
var pc = dok(Rc, 'penyesuaianStok')[0];
ok('tiga hitungan tumpukan NG: −50, −10, −5', !Ra.tolak && !Rb.tolak && !Rc.tolak && pa.selisihKg === -50 && pb.selisihKg === -10 && pc.selisihKg === -5, [Ra.tolak, Rb.tolak, pa, pb, pc]);
var ra = baris('barang|penyesuaianStok|' + pa.id);
ok('baris cocokkan tumpukan: per barang, bisa dibatalkan', !!ra && ra.bisa && ra.anggota === 0 && /^Cocokkan NG \(tumpukan\) · selisih −50 kg$/.test(ra.jenis), ra);
var Bpa = rbSusunBatal('penyesuaianStok', pa.id, 'Salah catat', WJ('09:00')); var Apa = idBatal(Bpa); terap(Bpa);
var sel = function (d) { return (ambilPenyesuaianStok().find(function (x) { return x.id === d.id; }) || {}).selisihKg; };
ok('batal hitungan pertama: hanya hitungan BERIKUTNYA yang menyerap (−10 → −60), hitungan sesudahnya tetap (−5), buku NG = fisik hitungan terakhir', B2(buku('NG')) === B2(NG0 - 65) && sel(pb) === -60 && sel(pc) === -5,
  [buku('NG'), NG0, sel(pb), sel(pc)]);

// ---------- 6 · pindah tempat ----------
var bNG = barangTempat().find(function (b) { return b.nama === 'NG'; });
var Pt1 = susunPindah(bNG.kunci, 'Kiri belakang', WJ('09:05')); terap(Pt1); var Pt2 = susunPindah(bNG.kunci, 'Kanan belakang', WJ('09:06')); terap(Pt2);
var t1 = dok(Pt1, 'pindahTempat')[0], t2 = dok(Pt2, 'pindahTempat')[0];
ok('pindah tempat yang LAMA ditolak (sudah dipindah lagi sesudahnya)', /dipindah lagi/.test(rbPeriksa('pindahTempat', t1.id).tolak || ''), rbPeriksa('pindahTempat', t1.id));
var Bt = rbSusunBatal('pindahTempat', t2.id, 'Salah catat', WJ('09:07')); terap(Bt);
ok('batal pindah terbaru: NG kembali ke Kiri belakang (peta tempat), catatan pindahannya hilang', petaTempat()[bNG.kunci] === 'Kiri belakang' && !cacheMentah('pindahTempat').some(function (p) { return p.id === t2.id; }), petaTempat());
terap(rbSusunPulih(idBatal(Bt), WJ('09:08')));
ok('pulihkan pindah: NG kembali ke Kanan belakang', petaTempat()[bNG.kunci] === 'Kanan belakang', petaTempat());

// ---------- 6b · pindah stok antarlokasi: dua catatan (keluar & masuk) satu baris; tidak bisa dibatalkan bila stok di tujuan sudah terpakai ----------
var psK = { id: 7000001, tipe: 'keluar', lokasi: 'utama', pasangan: 7000001, dari: 'utama', ke: 'l2', merk: 'NG', kg: 10, pengantar: 'Pengantar uji', tanggal: HARI, jam: '09:20' };
var psM = Object.assign({}, psK, { id: 7000002, tipe: 'masuk', lokasi: 'l2' });
terapkanKeCache([{ koleksi: 'pindahStok', data: psK }, { koleksi: 'pindahStok', data: psM }]);
var rps = baris('barang|pindahStok|' + psK.id);
ok('pindah stok: keluar + masuk = SATU baris (pasangan), bisa dibatalkan', !!rps && rps.bisa && rps.anggota === 1 && /^Pindah stok NG 10 kg: utama → l2$/.test(rps.jenis) && !baris('barang|pindahStok|' + psM.id), rps);
var Bps = rbSusunBatal('pindahStok', psK.id, 'Salah catat', WJ('09:21'));
ok('batal pindah stok: kedua catatannya dihapus bersama', !Bps.tolak && J(Bps.hapus.map(function (x) { return x.id; }).sort()) === J(['7000001', '7000002']), Bps);
terap(Bps);
terapkanKeCache([{ koleksi: 'pindahStok', data: Object.assign({}, psK, { id: 7000011, pasangan: 7000011 }) }, { koleksi: 'pindahStok', data: Object.assign({}, psM, { id: 7000012, pasangan: 7000011 }) },
  { koleksi: 'pindahStok', data: { id: 7100001, tipe: 'keluar', lokasi: 'l2', pasangan: 7100001, dari: 'l2', ke: 'utama', merk: 'NG', kg: 4, tanggal: HARI, jam: '09:30' } }]);
ok('pindah stok yang isinya sudah terpakai di tujuan (tinggal 6 dari 10 kg) ditolak', /sudah terpakai/.test(rbPeriksa('pindahStok', 7000011).tolak || ''), rbPeriksa('pindahStok', 7000011));
terapkanKeCache(['7000011', '7000012', '7100001'].map(function (id) { return { koleksi: 'pindahStok', hapus: Number(id) }; }));

// ---------- 7 · yang tidak lewat sini & bulan terkunci ----------
ok('kedatangan tampil tanpa tombol (koreksi / hapus di Stok › Barang masuk)', rbDaftar('2026-09-10', '').some(function (b) { return /^Kedatangan/.test(b.jenis) && !b.bisa && /Barang masuk/.test(b.sebab); }), rbDaftar('2026-09-10', ''));
pasok('aturanToko', cacheMentah('aturan').concat([{ id: 'kunciPeriode', sampaiBulan: '2026-09', riwayat: [] }]));
ok('bulan terkunci: batal & pulihkan ditolak', /dikunci/.test(rbPeriksa('penyesuaianStok', pc.id).tolak || '') && /dikunci/.test(rbSusunPulih(Apa, WJ('09:10')).tolak || ''), [rbPeriksa('penyesuaianStok', pc.id).tolak, rbSusunPulih(Apa, WJ('09:10')).tolak]);
pasok('aturanToko', cacheMentah('aturan').filter(function (x) { return x.id !== 'kunciPeriode'; }));
/*TAMPILAN*/
print(J(hasil));
"""


def tampilan(t):
    """Panel Menu tab Barang dijalankan ASLI di jsc: gambarRiwayat dipotong dari menu.js, h/esc dari inti/dom.js, RB = fungsi logika di bundel."""
    M = t[MN]; i = M.find('  function gambarRiwayat(s, tab) {'); j = M.find('  function gambarPengingat(', i)
    if i < 0 or j < 0: return "ok('tampilan: gambarRiwayat ada di menu.js', false);"
    D = open(os.path.join(AKAR, 'baru/js/inti/dom.js'), encoding='utf-8').read(); a = D.find('export const esc'); b = D.find('export const mentah')
    return ("(function () {\n" + D[a:b].replace('export ', '') + "\nvar RU = { RU_ALASAN: [['salah', 'Salah catat'], ['dobel', 'Tercatat dua kali'], ['uji', 'Uji coba']] };\n"
            "var RB = { rbDaftar: rbDaftar, rbOrang: rbOrang, rbPeriksa: rbPeriksa };\nvar kini = function () { return new Date('2026-09-21T12:00:00'); };\n" + M[i:j] + r"""
try {
  var k = 'barang|penyesuaianStok|' + pb.id;
  var g = gambarRiwayat({ ruHari: '2026-09-21', ruSaring: '', ruBuka: k, ruAlasan: 'Salah catat', yakinRu: 'b:' + k }, 'barang').html;
  ok('tampilan Barang: baris catatan barang + Batalkan + alasan + akibat + ketukan kedua, tanpa rupiah uang', g.indexOf('data-k-ru="' + k + '"') >= 0 && /KETUK LAGI · BATALKAN/.test(g) && /catatan barang/.test(g)
    && /data-aksi="ruAlasan" data-a="Salah catat"/.test(g) && /Hitungan|Buku NG/.test(g) && /catatan satu ketukan/.test(g) && !/undefined|NaN|\[object/.test(g), g.slice(0, 900));
} catch (e) { ok('tampilan: gambarRiwayat tab Barang jalan tanpa galat', false, String(e && e.stack || e)); }
})();
""")


def baca_semua():
    return dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in [RBL, MN, IDX])


def rakit(t):
    js = bundel_baru.bundel(MODUL); mulai = '// ===== ' + RBL + ' ====='
    if RBL in t:   # isi riwayat-barang diganti teks (kontrol)
        i = js.index(mulai); j = js.find('// ===== ', i + len(mulai)); j = len(js) if j < 0 else j
        js = js[:i] + mulai + '\n' + bundel_baru.polos(t[RBL]) + '\n' + js[j:]
    tanda = '// ===== baru/js/layar/stok-hpp-logika.js ====='   # pola uji wadah: teksMargin stok-hpp diganti nama (satu lingkup)
    if tanda in js:
        i = js.index(tanda); j = js.find('// ===== ', i + len(tanda)); j = len(js) if j < 0 else j
        js = js[:i] + js[i:j].replace('teksMargin', 'teksMarginHpp') + js[j:]
    return js


def jalankan(t):
    h, e = uji_wadah_bernama.jalan(JAM_TETAP + rakit(t) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO.replace('/*TAMPILAN*/', tampilan(t)).replace("print(J(hasil));", "print(J({ lulus: hasil.filter(function (x) { return x.ok; }).length, gagal: [], hasil: hasil }));"))
    if h is None: return [{'nama': 'jsc jalan', 'ok': False, 'ket': (e or '')[-1500:]}]
    return h['hasil']


def periksa_statis(t):
    c = []; ok = lambda n, x, k='': c.append({'nama': 'statis: ' + n, 'ok': bool(x), 'ket': k})
    M = t[MN]
    ok('Menu: tab Barang di panel Riwayat & batal', "riwayat: [['uang', 'Uang'], ['barang', 'Barang'], ['batal', 'Dibatalkan']]" in M and "import * as RB from './riwayat-barang-logika.js';" in M)
    ok('Menu: batal barang & pulihkan barang memakai logika barang', "(brg ? RB.rbSusunBatal : RU.ruSusunBatal)(" in M and "x.jenisBatal === 'barang' ? RB.rbSusunPulih : RU.ruSusunPulih" in M)
    ok('index.html memuat riwayat-barang-logika (modulepreload)', '<link rel="modulepreload" href="js/layar/riwayat-barang-logika.js">' in t[IDX])
    ok('logika riwayat barang tidak menulis sendiri', not re.search(r'tulisDokumen|setDoc|writeBatch|import .*firebase', t[RBL]))
    return c


ASAP = r"""
var J = JSON.stringify; var B2 = function (n) { return Math.round(n * 100) / 100; };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
var terap = function (R) { if (R.hapus) terapkanKeCache(R.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); terapkanKeCache(R.dokumen || []); };
var KOL = { wadahLiteran: 'wadah', produksiKemasan: 'produksi', penyesuaianStok: 'penyesuaian', penyesuaianKemasan: 'penyKemasan', stokBahanLiteran: 'bahanLiteran', stokBahanKemasan: 'bahanKemasan', pindahTempat: 'pindahTempat', pindahStok: 'pindahStok', pengaturan: 'pengaturan', bukuHapus: 'bukuHapus' };
var BUANG = { koreksiBatal: 1, diubahPada: 1, diubahOleh: 1, diubahPerangkat: 1, oleh: 1, perangkat: 1 };   // jejak var BUANG = { koreksiBatal: 1, diubahPada: 1 }; cap penulis (dibubuhkan penulis aplikasi saat menulis), bukan isi
var urut = function (v) { if (Array.isArray(v)) return v.map(urut); if (v && typeof v === 'object') { var o = {}; Object.keys(v).sort().forEach(function (f) { if (!BUANG[f]) o[f] = urut(v[f]); }); return o; } return v; };   // kunci terurut sampai ke dalam (isi peta sama = sama)
var potretDok = function () { var o = {}; Object.keys(KOL).forEach(function (k) { cacheMentah(KOL[k]).forEach(function (d) { o[k + '|' + d.id] = J(urut(d)); }); }); return o; };
var potret = function () { var o = potretDok(); return J(Object.keys(o).sort().map(function (k) { return [k, o[k]]; })); };
var beda = function (a) { var b = potretDok(); var k = Object.keys(a).concat(Object.keys(b)).filter(function (x, i, s) { return s.indexOf(x) === i && a[x] !== b[x]; }); return k.slice(0, 2).map(function (x) { return x + ': ' + String(a[x]).slice(0, 300) + ' ⇒ ' + String(b[x]).slice(0, 300); }).join(' || '); };
var stok = function () { var st = hitungStokKarungPerMerk(); return J(Object.keys(st).sort().map(function (m) { return [m, B2(st[m].sisaKg)]; })); };
var hari = {}; Object.keys(KOL).slice(0, 8).forEach(function (k) { cacheMentah(KOL[k]).forEach(function (d) { if (d.tanggal) hari[String(d.tanggal).slice(0, 10)] = 1; }); });
var H = Object.keys(hari).sort(); var baris = 0, bisa = 0, bolak = 0, digeser = 0, tolak = {}, galat = [], jenis = {};
var nId = 5e12; var W = function (jam) { nId += 100000; return { tanggal: '2026-12-31', jam: jam, kini: '2026-12-31T16:00:00.000Z', idUnik: function () { nId += 1; return nId; } }; };
H.forEach(function (iso) {
  var D; try { D = rbDaftar(iso, ''); } catch (e) { galat.push(iso + ' rbDaftar: ' + e); return; }
  D.forEach(function (b) { baris++; jenis[b.jenis.split(' ')[0]] = (jenis[b.jenis.split(' ')[0]] || 0) + 1; if (!b.bisa) return; bisa++;
    try {
      var P = rbPeriksa(b.koleksi, b.id); if (P.tolak) { var t = P.tolak.replace(/[A-Z][^ ]* [^ ]*/, '').slice(0, 50); tolak[t] = (tolak[t] || 0) + 1; return; }
      var awal = potret(), awalDok = potretDok(), s0 = stok(); var R = rbSusunBatal(b.koleksi, b.id, 'asap', W('23:00')); if (R.tolak) { galat.push(b.kunci + ' batal ditolak: ' + R.tolak); return; }
      if ((R.dokumen || []).some(function (x) { return x.koleksi === 'penyesuaianStok' || x.koleksi === 'penyesuaianKemasan' || (x.koleksi !== 'bukuHapus' && x.data.koreksiBatal); })) digeser++;
      terap(R); var id = R.dokumen[0].data.id; var Pl = rbSusunPulih(id, W('23:01')); if (Pl.tolak) { galat.push(b.kunci + ' pulih ditolak: ' + Pl.tolak); return; }
      terap(Pl); if (potret() !== awal || stok() !== s0) galat.push(b.kunci + ' (' + b.jenis.slice(0, 40) + ') batal → pulihkan TIDAK kembali persis: ' + beda(awalDok)); else bolak++;
    } catch (e) { galat.push(b.kunci + ': ' + (e && e.stack || e)); }
  });
});
print(J({ hari: H.length, baris: baris, bisa: bisa, bolak: bolak, digeser: digeser, tolak: tolak, jenis: jenis, galat: galat.slice(0, 8), nGalat: galat.length }));
"""


def asap(t):
    """Data toko asli (cadangan lokal di _privat/, tidak pernah di git): tiap catatan barang yang bisa dibatalkan → batal lalu pulihkan wajib kembali PERSIS
    (abaikan jejak koreksiBatal & cap diubahPada), stok tiap buku ikut kembali. Hanya dihitung di cache uji — tidak menulis apa pun."""
    p = uji_wadah_bernama.cadangan_toko()
    if not p: return [], None
    cad, tgl = uji_wadah_bernama.cad_js(p)
    h, e = uji_wadah_bernama.jalan(JAM_TETAP.replace('2026-09-21T10:00:00', tgl + 'T23:00:00') + rakit(t) + '\nvar CADANGAN = ' + cad + ';\n' + ASAP)
    if h is None: return [{'nama': 'asap data toko: jsc jalan', 'ok': False, 'ket': (e or '')[-1500:]}], None
    return [{'nama': 'asap data toko: semua catatan barang tergambar & batal → pulihkan kembali persis', 'ok': h['nGalat'] == 0 and h['bolak'] > 0, 'ket': h['galat']}], (os.path.basename(p), h)


def periksa(t, diam=False):
    c = jalankan(t) + periksa_statis(t)
    g = [x for x in c if not x['ok']]
    if not diam:
        for x in c: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:900]))
        print('RIWAYAT & BATAL BARANG: %d lulus · %d gagal' % (len(c) - len(g), len(g)))
        a, info = asap(t)
        for x in a: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:1500]))
        g = g + [x for x in a if not x['ok']]
        if info:
            n, h = info
            print('ASAP DATA TOKO (%s): %d hari · %d catatan barang · %d bisa dibatalkan · %d bolak-balik persis (%d menggeser hitungan sesudahnya) · ditolak: %s · jenis: %s'
                  % (n, h['hari'], h['baris'], h['bisa'], h['bolak'], h['digeser'], json.dumps(h['tolak'], ensure_ascii=False), json.dumps(h['jenis'], ensure_ascii=False)))
    return g


def main():
    t = baca_semua()
    if '--kontrol' in sys.argv:
        R = t[RBL]; M = t[MN]
        rusak = [
            ('karung yang dibuka dari tumpukan tidak ikut batal', RBL, R.replace("|| (!!p.bukaKarung && String(p.bukaKarung) === W && asal.indexOf(String(p.merkAsal || '')) >= 0))", ")")),
            ('catatan karung yang dibuka tidak ikut batal', RBL, R.replace("karung(T, (k) => (k.produksiId !== undefined && ids.indexOf(String(k.produksiId)) >= 0) ||", "karung(T, (k) => false && (k.produksiId !== undefined && ids.indexOf(String(k.produksiId)) >= 0) ||")),
            ('karung bekas yang lahir tidak ikut batal', RBL, R.replace("const kbDari = (ids) => bl.filter(", "const kbDari = (ids) => [].filter(")),
            ('hitungan sesudahnya tidak digeser (susut dua kali)', RBL, R.replace("    if (!H.length) {\n", "    if (true) {\n")),
            ('hitungan digeser ke arah yang salah', RBL, R.replace("const geser = arah < 0 ? e[bk] : -e[bk];", "const geser = arah < 0 ? -e[bk] : e[bk];")),
            ('angka sistem hitungan tidak ikut digeser', RBL, R.replace("if (typeof d.kgSistem === 'number') d.kgSistem = rbB2(d.kgSistem - geser);", "")),
            ('yang digeser hitungan terakhir, bukan yang pertama sesudahnya', RBL, R.replace("const h = H[0];", "const h = H[H.length - 1];")),
            ('pulihkan tidak menggeser balik hitungan', RBL, R.replace("const R = rbKoreksi(A, Object.assign({}, x.efek || rbJumlahPengaruh(A)), 1, x.id, w.kini);", "const R = { dokumen: [], akibat: [] };")),
            ('pulihkan dua kali', RBL, R.replace("if (rbCari(d.koleksi, d.data.id)) return { tolak: 'Catatan ' + d.koleksi", "if (false) return { tolak: 'Catatan ' + d.koleksi")),
            ('pindah stok tanpa pasangannya', RBL, R.replace("if (q.tipe === 'masuk' && bebas('pindahStok', q) && String(q.pasangan || '') === String(p.pasangan || p.id)) A.push", "if (false) A.push")),
            ('pindah stok terpakai boleh dibatalkan', RBL, R.replace("if (ada + 0.005 < (Number(ke.data.kg) || 0)) return", "if (false) return")),
            ('pindah tempat lama boleh dibatalkan', RBL, R.replace("if (RB_AMBIL.pindahTempat().some((p) => String(p.kunci) === String(d.kunci) && String(p.id) !== String(d.id) && rbSesudah(p, d))) return", "if (false) return")),
            ('batal pindah tempat tidak mengembalikan peta', RBL, R.replace("if (d.dari) peta[d.kunci] = d.dari; else delete peta[d.kunci];", "")),
            ('bulan terkunci boleh dibatalkan', RBL, R.replace("for (const x of g.anggota) { const k = tolakKunci(x.koleksi, x.data, 'bulan itu sudah dikunci — catatan tidak bisa dibatalkan lagi'); if (k) return { tolak: k }; }", "")),
            ('kedatangan boleh dibatalkan di sini', RBL, R.replace("tambah('kedatangan', [{ koleksi: 'batchMasuk', data: b }], RB_SEBAB.kedatangan)", "tambah('kedatangan', [{ koleksi: 'batchMasuk', data: b }], '')")),
            ('aktivasi wadah boleh dibatalkan', RBL, R.replace("pindah(d, () => true).forEach((p) => A.push(ambil('produksiKemasan', p))); tambah('aktivasi', A, RB_SEBAB.aktivasi);", "pindah(d, () => true).forEach((p) => A.push(ambil('produksiKemasan', p))); tambah('aktivasi', A, '');")),
            ('batal tanpa alasan', RBL, R.replace("if (!a) return { tolak: 'Membatalkan butuh alasan' };", "")),
            ('bukan satu kiriman (jendela nomor terlalu lebar: ketukan lain ikut)', RBL, R.replace("Math.abs(x - y) < 3000", "Math.abs(x - y) < 300000")),
            ('panel tab Barang memakai logika uang', MN, M.replace("const L = brg ? { daftar: RB.rbDaftar, orang: RB.rbOrang, periksa: RB.rbPeriksa } :", "const L = false ? { daftar: RB.rbDaftar, orang: RB.rbOrang, periksa: RB.rbPeriksa } :")),
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
