#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_ringkasan_baru.py — uji logika layar RINGKASAN sistem baru (baru/js/layar/ringkasan-logika.js) di jsc.
KOTAK PASIR (ANGKA CONTOH, bukan angka toko) dengan jam tetap; kalau ada backup-batch-*.json lokal ditambah uji asap:
angka Ringkasan harus SAMA dengan jumlah langsung dari cadangan itu (penjualan − uang retur) DAN dengan omzet mesin laba (Laporan) — 39b no. 19.

    python3 alat-uji/uji_ringkasan_baru.py            → N lulus · 0 gagal
    python3 alat-uji/uji_ringkasan_baru.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, re, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/ringkasan-logika.js']


def jual(id, tgl, jam, rp, trx=None, cara='Tunai', hpp=None, jenis='kemasan'):
    d = {'id': id, 'tanggal': tgl, 'jam': jam, 'caraBayar': cara, 'namaPelanggan': '', 'jenis': jenis, 'namaProduk': 'Kembang', 'ukuranKemasan': 5,
         'jumlahUnit': 1, 'totalKg': 5, 'hargaTotal': rp, 'hppTotalSaatJual': int(rp * 0.9) if hpp is None else hpp}
    if trx: d['trxId'] = trx
    return d


# Sabtu 19 Sep 2026 14:07 = "sekarang". Catatan toko contoh mulai 25 Agu 2026.
KOTAK = {
  'produksiKemasan': [{'id': 'p1', 'tanggal': '2026-08-25', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 500, 'hppPerUnit': 66000}],
  'penjualan': [
    jual('a1', '2026-09-19', '08:10', 100000), jual('a2', '2026-09-19', '08:40', 50000, trx='T2'), jual('a3', '2026-09-19', '08:40', 25000, trx='T2'),
    jual('a4', '2026-09-19', '13:20', 200000, cara='QRIS'), jual('a5', '2026-09-19', '13:55', 40000), jual('a6', '2026-09-19', '14:05', 60000),
    jual('a7', '2026-09-19', '15:30', 999000),                       # SESUDAH "sekarang" (jam perangkat lain maju) — tetap omzet hari ini, tapi bukan 60 menit terakhir
    jual('x1', '2026-09-19', '09:00', 777000) | {'dibatalkan': True},  # baris mati: tidak boleh ikut
    jual('k1', '2026-09-18', '09:00', 300000), jual('k2', '2026-09-18', '13:30', 80000), jual('k3', '2026-09-18', '16:00', 500000),
    jual('s1', '2026-09-14', '10:00', 1000000),                       # Senin minggu ini
    jual('l1', '2026-09-12', '10:00', 700000), jual('l2', '2026-09-07', '10:00', 400000), jual('l3', '2026-09-13', '18:00', 150000),   # minggu lalu: Sen 7 & Sab 12 (& Min 13 sesudah titik)
    jual('b1', '2026-09-01', '10:00', 250000),
    jual('g1', '2026-08-25', '10:00', 600000), jual('g2', '2026-08-30', '10:00', 350000),
  ],
  'piutangMutasi': [{'id': 'm1', 'tanggal': '2026-08-10', 'namaPelanggan': 'Deka', 'tipe': 'saldoAwal', 'nominal': 200000}],
  'pesanan': [{'id': 'ps1', 'tanggal': '2026-09-19', 'namaPelanggan': 'Bu Ani', 'isi': 'x', 'status': 'diantar'}, {'id': 'ps2', 'tanggal': '2026-09-18', 'namaPelanggan': 'B', 'isi': 'y', 'status': 'dibayar'}],
}

SKENARIO = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var KINI = new Date('2026-09-19T14:07:30'); var ix = bangunIndeks();
ok('indeks: catatan mulai 25 Agu; baris dibatalkan tidak ikut; hari ini 7 baris / 6 nota (T2 dua baris = satu nota)', ix.mulai === '2026-08-25' && ix.perHari['2026-09-19'].baris.length === 7 && ix.perHari['2026-09-19'].nota.size === 6, JSON.stringify([ix.mulai, ix.perHari['2026-09-19'].baris.length]));
var R = susunRingkasan('jam', ix, KINI);
ok('jam: angka = omzet HARI INI 1.474.000 (termasuk nota berjam 15:30), 6 nota, judul "Hari ini · per jam"', R.angka === 1474000 && R.judul === 'Hari ini · per jam' && /6 nota/.test(R.sub), JSON.stringify([R.angka, R.sub]));
ok('jam: margin kotor dari mesin laba (10% dari harga contoh) disebut dengan persennya', /margin kotor Rp147\.400 · 10%/.test(R.sub), R.sub);
ok('jam: pembanding menyebut jam berjalan 14 (60.000 · 1 nota) dan jam tersibuk 15', /Jam 14 berjalan Rp60\.000 · 1 nota/.test(R.banding) && /tersibuk 15 · Rp999\.000/.test(R.banding), R.banding);
ok('jam: tiga lapis = jam (luar) · hari (induk) · bulan (kakek)', R.lapisan.length === 3 && /^Luar · Jam 14/.test(R.lapisan[0].nama) && /^Induk · Hari ini/.test(R.lapisan[1].nama) && /^Kakek · September/.test(R.lapisan[2].nama), JSON.stringify(R.lapisan.map(function (l) { return l.nama; })));
ok('jam: induk menyebut kemarin JAM SEGINI (s/d 14:07 = 380.000, bukan 880.000 sehari penuh)', /kemarin jam segini Rp380\.000/.test(R.lapisan[1].ket), R.lapisan[1].ket);
var sJam = R.sektor.filter(function (x) { return x.lapis === 'jam'; }), sHari = R.sektor.filter(function (x) { return x.lapis === 'hari'; }), sBulan = R.sektor.filter(function (x) { return x.lapis === 'bulan'; });
ok('cincin: 17 sel jam (05–21) r=86, 30 sel hari r=66, 12 sel bulan r=49', sJam.length === 17 && sJam[0].r === 86 && sHari.length === 30 && sHari[0].r === 66 && sBulan.length === 12 && sBulan[0].r === 49, [sJam.length, sHari.length, sBulan.length].join());
ok('cincin jam: sel 14 BERJALAN (tepi putus), jam 15–21 rel (belum terjadi) walau ada nota berjam 15:30, jam 08 emas', sJam[9].kelas === 'berjalan' && sJam.slice(10).every(function (x) { return x.kelas === 'rel'; }) && sJam[3].kelas === 'emas', JSON.stringify(sJam.map(function (x) { return x.kelas; })));
ok('cincin hari: hari sebelum 25 Agu ABSEN (bukan nol), hari ini berjalan, hari tanpa jualan = rel tipis', sHari[0].kelas === 'absen' && sHari[29].kelas === 'berjalan' && sHari.filter(function (x) { return x.kelas === 'absen'; }).length === 4 && sHari[28].kelas === 'emas', JSON.stringify(sHari.map(function (x) { return x.kelas; })));
ok('cincin bulan: Jan–Jul absen, Agu emas, Sep berjalan, Okt–Des rel', sBulan.slice(0, 7).every(function (x) { return x.kelas === 'absen'; }) && sBulan[7].kelas === 'emas' && sBulan[8].kelas === 'berjalan' && sBulan.slice(9).every(function (x) { return x.kelas === 'rel'; }), JSON.stringify(sBulan.map(function (x) { return x.kelas; })));
ok('cincin: tebal ∝ akar nilai dan tak pernah melebihi tebal maksimum lapisnya', sJam.every(function (x) { return x.w <= 13; }) && sHari.every(function (x) { return x.w <= 11; }) && sJam[10 - 0] && sJam.filter(function (x) { return x.kelas === 'emas'; })[0].w > 1.5);
ok('cincin: KETUJUH lapis selalu ada (147 sel + tahun); yang tak berperan menunggu di luar r=108 (lebih halus dari skala) atau di dalam r=22, opasitas 0', R.sektor.length === 15 + 60 + 17 + 30 + 12 + 12 + 1 && R.sektor.filter(function (x) { return x.lapis === 'menit'; }).every(function (x) { return x.r === 108 && x.op === 0; }) && R.sektor.filter(function (x) { return x.lapis === 'tahun'; }).every(function (x) { return x.r === 22 && x.op === 0; }) && sJam.every(function (x) { return x.op === 1; }), String(R.sektor.length));
ok('cincin: identitas sel tetap antar skala (lapis:urutan) — syarat cincin bisa BERGESER, bukan digambar ulang', JSON.stringify(R.sektor.map(function (x) { return x.id; })) === JSON.stringify(susunRingkasan('tahun', ix, KINI).sektor.map(function (x) { return x.id; })));
ok('cincin: sel membawa label & nilai untuk diketuk — hari ke-29 (kemarin) "Jumat, 18 Sep" Rp880.000; sel bulan Agustus 950.000; hari sebelum catatan nilai null', sHari[28].label === 'Jumat, 18 Sep' && sHari[28].nilai === 880000 && sBulan[7].label === 'Agustus 2026' && sBulan[7].nilai === 950000 && sHari[0].nilai === null && sHari[0].keadaan === 'absen', JSON.stringify([sHari[28].label, sHari[28].nilai, sBulan[7].label, sBulan[7].nilai]));
var kt = selDariKetukan(R.sektor, 86, 0); ok('ketukan: jam 12 di cincin luar = sel BERJALAN (jam 14)', kt && kt.lapis === 'jam' && kt.i === 9, JSON.stringify(kt && [kt.lapis, kt.i]));
kt = selDariKetukan(R.sektor, 64, -12); ok('ketukan: cincin induk, satu sel ke kiri dari jam 12 = KEMARIN (Jumat, 18 Sep)', kt && kt.lapis === 'hari' && kt.label === 'Jumat, 18 Sep', JSON.stringify(kt && [kt.lapis, kt.label]));
ok('ketukan: di luar semua cincin (jarak 130) atau di pusat (jarak 10) → tidak memilih apa-apa; lapis tersembunyi tak bisa diketuk', selDariKetukan(R.sektor, 130, 0) === null && selDariKetukan(R.sektor, 10, 0) === null && selDariKetukan(R.sektor, 108, 0) === null);
ok('lapisan menyebut lapisnya → ketuk "Induk · Hari ini" pindah ke skala hari', R.lapisan[1].lapis === 'hari' && SKALA_DARI_LAPIS[R.lapisan[1].lapis] === 'hari' && SKALA_DARI_LAPIS.m15 === 'langsung');
R = susunRingkasan('menit', ix, KINI);
ok('menit: 60 menit terakhir (13:08–14:07) = 200.000 + 40.000 + 60.000 = 300.000, 3 nota; nota 15:30 TIDAK ikut', R.angka === 300000 && /3 nota/.test(R.sub) && /Rp100\.000\/nota/.test(R.sub), JSON.stringify([R.angka, R.sub]));
ok('menit: pembanding = kemarin jendela yang sama (13:30 → 80.000, 1 nota, +275%)', /kemarin jendela ini 1 nota · Rp80\.000 \(\+275%\)/.test(R.banding), R.banding);
R = susunRingkasan('langsung', ix, KINI);
ok('langsung: nota ke-6 hari ini · kemarin jam segini nota ke-2; lapis luar = 15 menit terakhir (13:55 + 14:05 → 100.000, 2 nota)', /Nota ke-6 hari ini · kemarin jam segini nota ke-2/.test(R.banding) && /15 menit terakhir/.test(R.lapisan[0].nama) && R.lapisan[0].nilai === 'Rp100.000' && R.lapisan[0].ket === '2 nota', R.banding + ' | ' + JSON.stringify(R.lapisan[0]));
ok('langsung: umpan = nota hari ini terbaru dulu, nota dua baris digabung (+1), QRIS disebut', R.umpan.length === 6 && R.umpan[0].jam === '15:30' && R.umpan.some(function (u) { return /\+1/.test(u.isi) && u.rp === 75000; }) && R.umpan.some(function (u) { return /QRIS/.test(u.isi); }), JSON.stringify(R.umpan));
ok('langsung: sejak nota terakhir = 2 menit (14:05), nota berjam 15:30 tidak membuatnya negatif', R.sejakNotaMenit === 2, String(R.sejakNotaMenit));
R = susunRingkasan('hari', ix, KINI);
ok('hari: angka = MINGGU INI berjalan (Sen 14 → Sab 19) = 1.000.000 + 880.000 + 1.474.000 = 3.354.000', R.angka === 3354000 && R.judul === 'Minggu ini · per hari · berjalan', String(R.angka));
ok('hari: pembanding minggu lalu SAMPAI Sabtu jam segini = 400.000 + 700.000 = 1.100.000 (Minggu 13 tidak ikut), +204,9%', /minggu lalu sampai Sabtu jam segini: Rp1\.100\.000 \(\+204,9%\)/.test(R.banding), R.banding);
R = susunRingkasan('bulan', ix, KINI);
ok('bulan: September berjalan = 5.854.000; Agustus hanya sejak tanggal 25 → MENOLAK membandingkan', R.angka === 3354000 + 1250000 + 250000 + 1000000 * 0 && /Agustus 2026 hanya sejak tanggal 25 · belum bisa dibandingkan/.test(R.banding), R.angka + ' | ' + R.banding);
ok('bulan: dua lapis saja (bulan · tahun), hari buka dihitung dari hari yang ada jualannya', R.lapisan.length === 2 && /7 hari buka/.test(R.sub), R.sub);
R = susunRingkasan('tahun', ix, KINI);
ok('tahun: 2026 · sejak 25 Agustus; 9 hari buka; pembanding tahun lalu DITOLAK dengan sebabnya', /2026 · sejak 25 Agustus/.test(R.judul) && /9 hari buka/.test(R.sub) && /belum ada/.test(R.banding) && R.lapisan.length === 1 && R.sektor.filter(function (x) { return x.op === 1; }).length === 1, R.judul + ' | ' + R.sub + ' | ' + R.banding);
ok('tahun: angka = semua baris berlaku 2026 = 5.804.000', R.angka === 5804000, String(R.angka));
var P = susunPerhatian();
ok('perhatian: bon belum lunas 1 nama Rp200.000 (tertua ≥ 30 hari → awas); pesanan belum dibayar 1 (1 sudah diantar)', P.some(function (x) { return /Bon belum lunas · 1 nama/.test(x.teks) && x.nilai === 'Rp200.000' && x.awas; }) && P.some(function (x) { return /Pesanan belum dibayar · 1 sudah diantar/.test(x.teks) && x.nilai === '1 pesanan'; }), JSON.stringify(P));
// 39b no. 4: kelebihan bayar pelanggan BERBUNYI di Perlu perhatian (dulu disaring sisa > 0 dengan diam). Baris bon di atas tidak berubah.
ok('perhatian 39b-4: tanpa sisa negatif tidak ada baris kelebihan bayar', !P.some(function (x) { return /Kelebihan bayar pelanggan/.test(x.teks); }), JSON.stringify(P));
var piu0 = cacheMentah('piutang').slice(); pasok('piutangMutasi', piu0.concat([{ id: 'm9', tanggal: '2026-09-19', namaPelanggan: 'Wati', tipe: 'saldoAwal', nominal: 50000 }, { id: 'm10', tanggal: '2026-09-19', namaPelanggan: 'Wati', tipe: 'bayar', nominal: 80000, dicatatDi: 'kasir' }]));
var P4 = susunPerhatian(); var b4 = P4.find(function (x) { return /Kelebihan bayar pelanggan/.test(x.teks); });
ok('perhatian 39b-4: sisa Wati −30.000 → "Kelebihan bayar pelanggan · 1 nama (Wati) — uang pelanggan dipegang toko", Rp30.000, AWAS; baris bon tetap 1 nama Rp200.000', b4 && b4.teks === 'Kelebihan bayar pelanggan · 1 nama (Wati) — uang pelanggan dipegang toko' && b4.nilai === 'Rp30.000' && b4.awas && P4.some(function (x) { return /Bon belum lunas · 1 nama/.test(x.teks) && x.nilai === 'Rp200.000'; }), JSON.stringify(P4));
pasok('piutangMutasi', piu0.concat([{ id: 'm11', tanggal: '2026-09-10', namaPelanggan: 'Yoga', tipe: 'saldoAwal', nominal: 100000 }, { id: 'm12', tanggal: '2026-09-18', namaPelanggan: 'Yoga', tipe: 'hapusBuku', nominal: 100000, alasan: 'pindah' }, { id: 'm13', tanggal: '2026-09-19', namaPelanggan: 'Yoga', tipe: 'bayar', nominal: 100000, dicatatDi: 'kasir' }]));
var P5 = susunPerhatian(); var h5 = P5.find(function (x) { return /Hapus buku yang ternyata dibayar/.test(x.teks); });
ok('perhatian 39b-4 B1: bon 100.000 dihapus buku lalu dibayar 100.000 (katalog kasir basi) → "Hapus buku yang ternyata dibayar · 1 nama (Yoga)" Rp100.000, AWAS — BUKAN "Kelebihan bayar pelanggan"', h5 && h5.teks === 'Hapus buku yang ternyata dibayar · 1 nama (Yoga) — hapus bukunya perlu dibalik, bukan uang pelanggan' && h5.nilai === 'Rp100.000' && h5.awas && !P5.some(function (x) { return /Kelebihan bayar pelanggan/.test(x.teks); }), JSON.stringify(P5));
pasok('piutangMutasi', piu0);
// Paket F1 (owner 8 Okt 2026): bon lama pemasok yang BERGULIR (kartu "bon lama ikut kedatangan terakhir") tidak punya umur tetap → tidak ikut "bon tertua"
var up0 = cacheMentah('utangPemasok').slice(), pc0 = cacheMentah('pemasokCat').slice();
pasok('utangPemasokMutasi', up0.concat([{ id: 9801, tipe: 'saldoAwal', pemasok: 'PEMASOK LAMA', nominal: 5000000, tanggal: '2026-08-25', jam: '23:02', bonTanggal: '2026-07-01', catatan: 'contoh' }]));
var PF0 = susunPerhatian().find(function (x) { return /Utang ke pemasok/.test(x.teks); });
pasok('pemasokCatatan', pc0.concat([{ id: 'pemasok lama', nama: 'PEMASOK LAMA', bonLamaBergulir: true }])); var PF1 = susunPerhatian().find(function (x) { return /Utang ke pemasok/.test(x.teks); });
pasok('utangPemasokMutasi', up0); pasok('pemasokCatatan', pc0);
ok('perhatian F1: bon lama 1 Jul → "bon tertua N hari"; kartu pemasoknya bergulir → baris utang tetap Rp5.000.000 tanpa "bon tertua"', PF0 && /bon tertua \d+ hari/.test(PF0.teks) && PF0.nilai === 'Rp5.000.000' && PF1 && !/bon tertua/.test(PF1.teks) && PF1.nilai === 'Rp5.000.000', JSON.stringify([PF0, PF1]));
var K = susunKas(KINI);
ok('kas: tanpa titik kas di perangkat → MENOLAK menyebut saldo; arus hari ini tetap dari buku kas: laci 1.274.000 · rekening 200.000', K.adaTitik === false && K.total === null && K.masukLaci === 1274000 && K.masukRek === 200000 && K.keluar === 0, JSON.stringify(K));
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-18', laci: 1000000, rekening: 500000, amplop: 0, brankas: 0 }));
K = susunKas(KINI); ok('kas: dengan titik kas 18 Sep (1.500.000) → saldo = titik + gerakan SESUDAH titik = 1.500.000 + 1.474.000', K.adaTitik === true && K.total === 2974000, JSON.stringify(K));
ok('kelompok angka untuk animasi: "Rp 5.804.000" → [Rp, 5, .804, .000]', JSON.stringify(kelompokAngka(5804000)) === JSON.stringify(['Rp', '5', '.804', '.000']), JSON.stringify(kelompokAngka(5804000)));
ok('salam & tanggal: 14:07 → Selamat siang · Sabtu, 19 September 2026', salam(KINI) === 'Selamat siang' && tanggalPanjang(KINI) === 'Sabtu, 19 September 2026', salam(KINI) + ' ' + tanggalPanjang(KINI));
// 39b no. 19: uang retur mengurangi omzet (keputusan owner 9 Sep) — Ringkasan dulu bruto sementara Laporan/Pajak bersih
var RT19 = [{ koleksi: 'retur', data: { id: 'rt19', tanggal: '2026-09-19', jam: '10:00', nominalRefund: 20000, selisihHargaTukar: 0, kondisi: 'utuh' } }, { koleksi: 'retur', data: { id: 'rt19b', tanggal: '2026-09-19', jam: '15:00', nominalRefund: 5000, kondisi: 'utuh' } }];
ok('39b-19 retur hari ini 20.000 (10.00) mengurangi omzet hari/minggu/bulan & sel hari; retur 5.000 berjam 15.00 ikut hari ini (hari = seluruh hari); sub menyebut "sudah dikurangi retur"; = omzet mesin laba',
  denganCacheSementara(RT19, function () { var ix2 = bangunIndeks(); var a = susunRingkasan('langsung', ix2, KINI), b = susunRingkasan('langsung', ix, KINI); var bl2 = susunRingkasan('bulan', ix2, KINI), bl = susunRingkasan('bulan', ix, KINI);
    var sel2 = rkDataLapis('hari', ix2, KINI).sel, sel = rkDataLapis('hari', ix, KINI).sel;
    return b.angka - a.angka === 25000 && bl.angka - bl2.angka === 25000 && sel[29].v - sel2[29].v === 25000 && sel2[29].v === a.angka && /sudah dikurangi retur Rp25\.000/.test(a.sub) && a.angka === hitungLabaRentang(function (t) { return t === '2026-09-19'; }).omzetPenuh; }),
  JSON.stringify(denganCacheSementara(RT19, function () { var ix2 = bangunIndeks(); return [susunRingkasan('langsung', ix2, KINI).angka, susunRingkasan('langsung', ix, KINI).angka, susunRingkasan('langsung', ix2, KINI).sub]; })));
ok('39b-19 skala Jam: retur 20.000 jam 10.00 mengurangi sel jam 10 sebesar itu (sel lain tetap; sel minus tidak NaN); angka minus ditulis "−Rp 125.000" (bukan "−Rp125000"); hari tanpa penjualan dengan retur → sel minus digambar tipis, lebar bukan NaN',
  (function () { var tanpa = rkDataLapis('jam', ix, KINI).sel; return denganCacheSementara(RT19, function () { var ix2 = bangunIndeks(); var dg = rkDataLapis('jam', ix2, KINI).sel; var j10 = 10 - 5;
    return dg[j10].v === tanpa[j10].v - 20000 && dg.every(function (c, i) { return i === j10 || JSON.stringify(c.v) === JSON.stringify(tanpa[i].v); }) && susunSektor('jam', ix2, KINI).every(function (x) { return isFinite(x.w); }); }); })()
  && JSON.stringify(kelompokAngka(-125000)) === JSON.stringify(['−Rp', '125', '.000'])
  && denganCacheSementara([{ koleksi: 'retur', data: { id: 'rtNaN', tanggal: '2026-09-15', jam: '09:00', nominalRefund: 100000, kondisi: 'utuh' } }], function () { var S2 = susunSektor('hari', bangunIndeks(), KINI); return S2.every(function (x) { return isFinite(x.w); }); }),
  JSON.stringify([kelompokAngka(-125000), denganCacheSementara(RT19, function () { var ix2 = bangunIndeks(); return [rkDataLapis('jam', ix2, KINI).sel.map(function (c) { return c.v; }), susunRingkasan('jam', ix2, KINI).angka]; })]));
// 39b no. 19 (tinjauan v2): retur DI DALAM jendela menit — angka 60/15 menit, sel cincin, jam berjalan, pembanding kemarin, retur tanpa jam, nota dua trxId
var RTW = [{ koleksi: 'retur', data: { id: 'w1', tanggal: '2026-09-19', jam: '13:50', nominalRefund: 30000, kondisi: 'utuh' } }, { koleksi: 'retur', data: { id: 'w2', tanggal: '2026-09-19', jam: '14:00', nominalRefund: 10000, kondisi: 'utuh' } },
  { koleksi: 'retur', data: { id: 'w3', tanggal: '2026-09-19', jam: '13:55', nominalRefund: 50000, kondisi: 'utuh' } }, { koleksi: 'retur', data: { id: 'w4', tanggal: '2026-09-19', nominalRefund: 7000, kondisi: 'utuh' } },
  { koleksi: 'retur', data: { id: 'w5', tanggal: '2026-09-18', jam: '13:40', nominalRefund: 30000, kondisi: 'utuh' } }, { koleksi: 'retur', data: { id: 'w6', tanggal: '2026-09-18', jam: '16:00', nominalRefund: 20000, kondisi: 'utuh' } },
  { koleksi: 'penjualan', data: { id: 'g1', tanggal: '2026-09-19', jam: '14:06', hargaTotal: 10000, jenis: 'literan', caraBayar: 'Tunai', grupNota: 'G1', trxId: 'ta' } }, { koleksi: 'penjualan', data: { id: 'g2', tanggal: '2026-09-19', jam: '14:06', hargaTotal: 10000, jenis: 'literan', caraBayar: 'Tunai', grupNota: 'G1', trxId: 'tb' } }];
var W19 = denganCacheSementara(RTW, function () { var ix2 = bangunIndeks(); var mn = susunRingkasan('menit', ix2, KINI), ls = susunRingkasan('langsung', ix2, KINI), jm = susunRingkasan('jam', ix2, KINI);
  var c60 = rkDataLapis('menit', ix2, KINI).sel, c15 = rkDataLapis('m15', ix2, KINI).sel; var jumlah60 = c60.reduce(function (a, c) { return a + (typeof c.v === 'number' ? c.v : 0); }, 0);
  return { m60: mn.angka, sub60: mn.sub, banding60: mn.banding, ls: ls.angka, subLs: ls.sub, lapisLs: ls.lapisan.map(function (l) { return l.nama + ' ' + l.nilai + ' ' + l.ket; }).join(' | '), jamBanding: jm.banding, induk: jm.lapisan[1].ket,
    sel1350: c60[59 - 17], sel1355: c60[59 - 12], titik1355: c15[14 - 12], jumlah60: jumlah60, sektorOk: susunSektor('menit', ix2, KINI).every(function (x) { return isFinite(x.w); }) }; });
ok('39b-19 menit: retur 13.50 (30.000) · 14.00 (10.000) · 13.55 (50.000) masuk jendela 60 menit → 300.000 + 20.000 − 90.000 = 230.000, 4 nota (nota G1 dua trxId = SATU nota); sel 13.50 hanya retur = −30.000; sel 13.55 nota 40.000 − retur 50.000 = −10.000 (tetap sel emas, bukan "tidak ada nota"); Σ sel 60 menit = angka; tebal tidak NaN',
  W19.m60 === 230000 && /4 nota/.test(W19.sub60) && W19.sel1350.v === -30000 && W19.sel1355.v === -10000 && W19.sel1355.kelas === 'emas' && W19.jumlah60 === 230000 && W19.sektorOk, JSON.stringify(W19));
ok('39b-19 menit: pembanding "kemarin jendela ini" = 80.000 − retur kemarin 13.40 (30.000) = 50.000 (retur kemarin 16.00 di luar jendela)', /kemarin jendela ini 1 nota · Rp50\.000 /.test(W19.banding60), W19.banding60);
ok('39b-19 15 menit: 13.55 + 14.05 + G1 = 120.000 − retur 14.00 & 13.55 (60.000) = 60.000, 3 nota; titik 13.55 tetap ada (menit itu punya nota walau returnya lebih besar)', /15 menit terakhir Rp60\.000 3 nota/.test(W19.lapisLs) && W19.titik1355.kelas === 'titik', W19.lapisLs + ' · ' + JSON.stringify(W19.titik1355));
ok('39b-19 hari: omzet hari ini 1.474.000 + 20.000 − 97.000 (termasuk retur TANPA jam 7.000) = 1.397.000; sub "sudah dikurangi retur Rp97.000"', W19.ls === 1397000 && /sudah dikurangi retur Rp97\.000/.test(W19.subLs), JSON.stringify([W19.ls, W19.subLs]));
ok('39b-19 jam: jam 14 berjalan = 60.000 + 20.000 − retur 14.00 (10.000) = 70.000 · 2 nota; induk "kemarin jam segini" = 380.000 − retur 13.40 = 350.000 (retur 16.00 belum terjadi jam segini)', /Jam 14 berjalan Rp70\.000 · 2 nota/.test(W19.jamBanding) && /kemarin jam segini Rp350\.000/.test(W19.induk), W19.jamBanding + ' | ' + W19.induk);
// toko kosong: tidak melempar, semuanya nol/ditolak
pasok('penjualan', []); var ix0 = bangunIndeks(); var R0 = susunRingkasan('hari', ix0, KINI);
ok('toko tanpa penjualan: angka 0, semua sel hari ABSEN, pembanding ditolak — tidak melempar', R0.angka === 0 && R0.sektor.filter(function (x) { return x.lapis === 'hari'; }).every(function (x) { return x.kelas === 'absen'; }) && /belum bisa dibandingkan/.test(R0.banding), JSON.stringify([R0.angka, R0.banding]));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var hidup = (CAD.penjualan || []).filter(function (p) { return !p.dikoreksiOleh && !p.dibatalkan; });
var tgl = hidup.map(function (p) { return p.tanggal || ''; }).sort(); var akhir = tgl[tgl.length - 1];
var KINI = new Date(akhir + 'T23:59:00'); var ix = bangunIndeks();
var R = susunRingkasan('jam', ix, KINI); var B = susunRingkasan('bulan', ix, KINI); var T = susunRingkasan('tahun', ix, KINI);
var langsungHari = hidup.filter(function (p) { return p.tanggal === akhir; }).reduce(function (a, p) { return a + (p.hargaTotal || 0); }, 0);
var langsungBulan = hidup.filter(function (p) { return (p.tanggal || '').slice(0, 7) === akhir.slice(0, 7) && p.tanggal <= akhir; }).reduce(function (a, p) { return a + (p.hargaTotal || 0); }, 0);
var langsungTahun = hidup.filter(function (p) { return (p.tanggal || '').slice(0, 4) === akhir.slice(0, 4); }).reduce(function (a, p) { return a + (p.hargaTotal || 0); }, 0);
// 39b no. 19: omzet = penjualan − uang retur (keputusan owner 9 Sep) — dulu asap ini MENGUNCI arti bruto; kini dibandingkan juga dengan mesin laba (omzet Laporan)
var uangR = function (r) { return (r.nominalRefund || 0) + Math.max(0, r.selisihHargaTukar || 0); };
var rJumlah = function (f) { return (CAD.retur || []).filter(function (r) { return f(String(r.tanggal || '')); }).reduce(function (a, r) { return a + uangR(r); }, 0); };
var fHari = function (t) { return t === akhir; }, fBulan = function (t) { return t.slice(0, 7) === akhir.slice(0, 7) && t <= akhir; }, fTahun = function (t) { return t.slice(0, 4) === akhir.slice(0, 4) && t <= akhir; };
langsungHari -= rJumlah(fHari); langsungBulan -= rJumlah(fBulan); langsungTahun -= rJumlah(fTahun);
var mesin = function (f) { return hitungLabaRentang(function (t) { return !!t && f(t); }).omzetPenuh; };
var semuaSkala = SKALA.map(function (s) { var r = susunRingkasan(s[0], ix, KINI); return r.sektor.length > 0 && typeof r.angka === 'number' && !!r.judul; });
print(JSON.stringify({ akhir: akhir, hariCocok: R.angka === langsungHari && R.angka === mesin(fHari), bulanCocok: B.angka === langsungBulan && B.angka === mesin(fBulan), tahunCocok: T.angka === langsungTahun && T.angka === mesin(fTahun), retur: [rJumlah(fHari), rJumlah(fBulan), rJumlah(fTahun)], skala: semuaSkala.filter(Boolean).length, perhatian: susunPerhatian().length, mulai: ix.mulai }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:700]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js):
    h, e = jalan(js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


def teks_titik_basi(berkas):
    """audit 39b no. 31: arahan titik kas menyuruh ke SISTEM LAMA (hanya-baca; titiknya jadi milik satu perangkat) — kini Tutup hari sistem baru."""
    out = []
    for f, t in berkas.items():
        if re.search(r'titik kas[^\n]{0,80}(sistem lama|Tutup Hari sistem lama)|setel di sistem lama', t, re.I): out.append(f + ' masih menyuruh setel titik kas di sistem lama')
        if 'belum disetel di perangkat ini' in t: out.append(f + ' menyebut titik kas milik "perangkat ini" (titikKas = satu dokumen untuk semua perangkat)')
    return out


def berkas_titik():
    return dict((f, open(os.path.join(AKAR, f), encoding='utf-8').read()) for f in ['baru/js/layar/ringkasan.js', 'baru/js/layar/bon-pemasok-logika.js'])


# ==================== PUTARAN 40 · DASBOR OWNER (baru/js/layar/dasbor-logika.js + saklar di ringkasan.js) ====================
# Kotak pasir = kotak Kendali Biaya (ANGKA CONTOH, jam 19 Sep 2026 10:00) + bon pelanggan tiga keadaan. Yang diuji: tiap angka dasbor MENUTUP ke fungsi
# sumbernya (satu sumber, tidak ada rumus uang baru), pengelompokan menutup ke total, kelompok galat tidak mematikan yang lain, dan dasbor hanya untuk owner.
def modul_dasbor():
    import uji_laporan_baru
    out = []
    for m in uji_laporan_baru.MODUL + ['baru/js/layar/stok-logika.js', 'baru/js/layar/kendali-biaya-logika.js', 'baru/js/layar/karcis-logika.js', 'baru/js/layar/ringkasan-logika.js', 'baru/js/layar/dasbor-logika.js']:
        if m not in out: out.append(m)
    return out


BON_PEMASOK_LAMA = "function susunBon(kini) {\n  const iso = hariIniIso(kini || new Date()); const atur = aturBon();"


def bundel_dasbor():
    """bon-logika & bon-pemasok-logika sama-sama punya susunBon; di peramban dasbor mengimpor yang pemasok sebagai bpSusunBon — di bundel jsc namanya dipisah."""
    js = bundel_baru.bundel(modul_dasbor())
    assert js.count(BON_PEMASOK_LAMA) == 1, 'jangkar susunBon pemasok basi'
    return js.replace(BON_PEMASOK_LAMA, BON_PEMASOK_LAMA.replace('susunBon(', 'bpSusunBon('))


def kotak_dasbor():
    # umur bon di mesin beku dihitung dari jam PERANGKAT (new Date()), bukan jam uji → tanggal bon baru & bon tagih relatif ke hari ini, supaya keadaannya tetap
    import uji_kendali_biaya, datetime
    hari = datetime.date.today(); iso = lambda n: (hari - datetime.timedelta(days=n)).isoformat()
    k = json.loads(json.dumps(uji_kendali_biaya.KOTAK))
    k['piutangMutasi'] = k['piutangMutasi'] + [{'id': 811, 'tipe': 'saldoAwal', 'namaPelanggan': 'Bu Baru', 'nominal': 120000, 'tanggal': iso(0), 'jam': '09:00'},
                                               {'id': 812, 'tipe': 'saldoAwal', 'namaPelanggan': 'Pak Tagih', 'nominal': 300000, 'tanggal': iso(30), 'jam': '09:00'},
                                               {'id': 813, 'tipe': 'saldoAwal', 'namaPelanggan': 'Bu Macet', 'nominal': 450000, 'tanggal': '2026-01-10', 'jam': '09:00'}]
    # merek kedua (lebih sedikit dari Angsa) supaya urutan "kg terbesar dulu" teruji; dibayar tunai → tidak menambah bon pemasok
    k['batchMasuk'] = k['batchMasuk'] + [{'id': 'b3', 'tanggal': '2026-09-12', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
                                          'merkList': [{'id': 'b30', 'merk': 'Anggrek', 'satuan': 'karung', 'beratKarung': 25, 'jumlahKarung': 8, 'totalKg': 200, 'hargaPerKg': 15000, 'subtotalHarga': 3000000}]}]
    return k


SKENARIO_DASBOR = r"""
var gagal = [], lulus = 0; var J = JSON.stringify; console.error = function () {};   // galat yang DISENGAJA (uji isolasi) tidak boleh mengotori keluaran JSON
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
var KINI = new Date(Date.now()); var iso = '2026-09-19'; var hariIni = function (t) { return t === iso; };
var D; try { D = susunDasbor(KINI, 'hari'); } catch (e) { D = { galatLuar: String(e) }; }
ok('dasbor: lima kelompok tergambar tanpa galat', ['hari', 'bulan', 'stok', 'tagihan', 'tren'].every(function (k) { return D[k] && !D[k].galat; }), J(D.galatLuar || ['hari', 'bulan', 'stok', 'tagihan', 'tren'].map(function (k) { return D[k] && D[k].galat; })));
// ---- HARI INI
var ix = bangunIndeks(); var RJ = susunRingkasan('jam', ix, KINI); var RH = rekapHari(iso); var LH = hitungLabaRentang(hariIni);
ok('hari ini: omzet = angka cincin Ringkasan = Laporan › Harian = mesin laba (250.000)', D.hari.omzet === RJ.angka && D.hari.omzet === RH.omzet && D.hari.omzet === LH.omzetPenuh && D.hari.omzet === 250000, J([D.hari.omzet, RJ.angka, RH.omzet, LH.omzetPenuh]));
ok('hari ini: nota = "N NOTA" cincin; laba kotor = mesin laba hari itu (18.600)', D.hari.nota === RJ.notaHariIni && D.hari.margin === LH.margin && D.hari.margin === 18600, J([D.hari.nota, RJ.notaHariIni, D.hari.margin]));
var RT = [{ koleksi: 'retur', data: { id: 'rtD', tanggal: iso, jam: '09:50', nominalRefund: 20000, kondisi: 'utuh' } },
  { koleksi: 'penjualan', data: { id: 'n2a', tanggal: iso, jam: '09:55', caraBayar: 'Tunai', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, hargaTotal: 60000, hppTotalSaatJual: 55000, trxId: 'tx2' } },
  { koleksi: 'penjualan', data: { id: 'n2b', tanggal: iso, jam: '09:55', caraBayar: 'Tunai', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, hargaTotal: 60000, hppTotalSaatJual: 55000, trxId: 'tx2' } }];
var R2 = denganCacheSementara(RT, function () { var d = dbHariIni(KINI); var r = susunRingkasan('jam', bangunIndeks(), KINI); var tr = dbTren('hari', KINI).batang; return { omzet: d.omzet, retur: d.retur, nota: d.nota, cincin: r.angka, notaCincin: r.notaHariIni, batang: tr[tr.length - 1] }; });
ok('hari ini + retur 20.000 & nota dua baris: omzet = cincin = 250.000 + 120.000 − 20.000 = 350.000 (sesudah retur); nota dua baris = SATU nota (2 nota); batang tren hari ini sama', R2.omzet === 350000 && R2.cincin === 350000 && R2.retur === 20000 && R2.nota === 2 && R2.notaCincin === 2 && R2.batang.omzet === 350000 && R2.batang.nota === 2 && R2.batang.notaDaftar === 2, J(R2));
var SK = susunKas(KINI); var jumlahKas = D.hari.kas.tempat.reduce(function (a, t) { return a + t.n; }, 0);
ok('kas per tempat: Laci · Brankas · Rekening · Amplop laba; Σ tempat = total = kas Ringkasan (kasPada) — menutup', D.hari.kas.ada && D.hari.kas.tempat.map(function (t) { return t.nama; }).join() === 'Laci,Brankas,Rekening,Amplop laba' && Math.abs(jumlahKas - D.hari.kas.total) < 0.5 && Math.abs(D.hari.kas.total - SK.total) < 0.5 && D.hari.kas.cocok === true, J([D.hari.kas, SK.total]));
localStorage.removeItem('miqbal_titik_kas_v1'); var tanpaTitik = dbHariIni(KINI).kas;
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
ok('kas tanpa titik kas: MENOLAK menebak (ada:false, tidak ada tempat) — keadaan "belum bisa dihitung", bukan nol', tanpaTitik.ada === false && tanpaTitik.tempat.length === 0, J(tanpaTitik));
var KC = daftarKarcis(KINI);
ok('karcis menunggu dirinci = Jual › Karcis kasir (daftarKarcis): 1 karcis Rp100.000', D.hari.karcis.n === KC.nKarcis && D.hari.karcis.rp === KC.total && D.hari.karcis.n === 1 && D.hari.karcis.rp === 100000 && D.hari.karcisTujuan.ke === 'jual' && D.hari.karcisTujuan.lembar === 'karcis', J(D.hari.karcis));
// ---- BULAN INI
var LB = labaBulan('2026-09', KINI); var K = kendaliBulan('2026-09', KINI); var T = titikImpas(K, KINI); var P = pemicuBiaya(K);
ok('bulan ini: laba kotor & laba bersih = Laporan › Laba (labaBulan) — mesin yang sama', D.bulan.margin === LB.margin && D.bulan.labaBersih === LB.labaBersih && D.bulan.labaTujuan.keluarga === 'laba', J([D.bulan.margin, LB.margin, D.bulan.labaBersih, LB.labaBersih]));
var jumlahBiaya = D.bulan.biaya.reduce(function (a, r) { return a + r.n - r.menggantung; }, 0);
ok('bulan ini: biaya = Kendali biaya; Σ baris per jenis (tanpa upah yang belum dibayar) = semua biaya — menutup', D.bulan.semuaBiaya === K.semuaBiaya && Math.abs(jumlahBiaya - D.bulan.semuaBiaya) < 0.5, J([jumlahBiaya, D.bulan.semuaBiaya, D.bulan.biaya.map(function (r) { return r.id + ':' + r.n; })]));
ok('bulan ini: titik impas & kalimatnya = titikImpas Kendali biaya; susut = baris susut (7.000)', D.bulan.impas.omzetImpas === T.omzetImpas && D.bulan.impas.kiniTeks === T.kiniTeks && D.bulan.impas.labaSampai === T.labaSampai && D.bulan.susut === K.susut && D.bulan.susut === 7000, J([D.bulan.impas, D.bulan.susut]));
ok('pemicu yang naik = pemicuBiaya().naik (urutan & teks sama); tiap pemicu punya tujuan layar', J(D.bulan.pemicu.map(function (r) { return [r.id, r.teks, r.deltaTeks]; })) === J(P.naik.map(function (r) { return [r.id, r.teks, r.deltaTeks]; })) && D.bulan.pemicu.every(function (r) { return r.tujuan && r.tujuan.ke; }), J([D.bulan.pemicu, P.naik.length]));
var jenisAda = K.baris.filter(function (r) { return ID_ANGGARAN.indexOf(r.id) >= 0 && r.n > 0; })[0];
var ang = {}; ang[jenisAda.id] = 1000;
var LM = denganCacheSementara([{ koleksi: 'aturanToko', data: { id: 'kendaliBiaya', anggaran: ang, ambang: 10, ambangPemicu: 1, kata: {} } }], function () { var b = dbBulanIni(KINI); var k2 = kendaliBulan('2026-09', KINI); var p2 = pemicuBiaya(k2);
  return { b: b.biaya.find(function (r) { return r.id === jenisAda.id; }), merah: b.merah, kMerah: k2.merah, kLampu: k2.baris.find(function (r) { return r.id === jenisAda.id; }).lampu, pemicu: b.pemicu, naik: p2.naik.map(function (r) { return r.id; }) }; });
ok('lampu anggaran = Kendali biaya: anggaran Rp1.000 untuk "' + jenisAda.nama + '" → MERAH di dasbor & di Kendali biaya', LM.b && LM.b.lampu === 'merah' && LM.kLampu === 'merah' && LM.merah === LM.kMerah && LM.merah >= 1, J(LM));
// 8 Okt 2026 (asap cadangan toko: susut bulan berjalan MINUS → total kartu Biaya minus padahal barisnya positif semua): baris NEGATIF ikut kartu Biaya → baris menutup ke total
var SN = denganCacheSementara([{ koleksi: 'penyesuaianStok', data: { id: 'snF3', tanggal: '2026-09-15', jam: '10:00', merk: 'Angsa', selisihKg: 100, nilaiRp: 50000000, alasan: 'uji stok bertambah' } }], function () { var b = dbBulanIni(KINI); return { susut: b.biaya.find(function (r) { return r.id === 'susut'; }), jumlah: b.biaya.reduce(function (a, r) { return a + r.n - r.menggantung; }, 0), semua: b.semuaBiaya }; });
ok('kartu Biaya: susut & selisih stok MINUS (stok bertambah) tetap jadi baris (angka bertanda minus) dan baris-baris menjumlah ke "Semua biaya"', SN.susut && SN.susut.n < 0 && Math.abs(SN.jumlah - SN.semua) < 0.5, J(SN));
ok('pemicu (ambang owner 1%): yang naik = pemicuBiaya().naik, tiap baris punya tujuan layar (dari peringatan Kendali biaya)', LM.pemicu.length > 0 && J(LM.pemicu.map(function (r) { return r.id; })) === J(LM.naik) && LM.pemicu.every(function (r) { return r.tujuan && r.tujuan.ke; }), J([LM.pemicu, LM.naik]));
// ---- STOK & WADAH
var DBr = daftarBarang(); var harap = DBr.filter(function (b) { return b.jenis === 'karung' && !b.wadahStok && Math.abs(b.sisa) > 0.004; });
ok('stok per merek = Stok › Gudang (daftarBarang): sisa kg & perkiraan hari sama, buku wadah tidak ikut, urut kg terbesar (Angsa sebelum Anggrek — abjad terbalik)', D.stok.merek.length === harap.length && harap.length >= 2 && D.stok.merek[0].nama === 'Angsa' && D.stok.merek[1].nama === 'Anggrek' && D.stok.merek.every(function (m, i) { var b = harap.find(function (x) { return x.nama === m.nama; }); return b && b.sisa === m.kg && b.hariHabis === m.hari && (i === 0 || D.stok.merek[i - 1].kg >= m.kg); }), J([D.stok.merek, harap.map(function (b) { return [b.nama, b.sisa]; })]));
var SW = susunWadah(null);
ok('wadah = Stok › Wadah literan (susunWadah): jumlah, nama, isi & terakhir diisi sama', D.stok.wadah.length === SW.daftar.length && D.stok.wadah.every(function (w, i) { var s = SW.daftar[i]; return w.nama === s.nama && w.no === s.no && w.isiKg === (s.diketahui ? s.sisaKg : null) && w.terakhirTanggal === (s.isiTerakhirTanggal || ''); }), J([D.stok.wadah.length, SW.daftar.length]));
ok('cek wadah memakai HARI TUTUP AKTIF (jam 10.00 → cek tutup kemarin 18 Sep, aturan Tutup hari & Jual)', D.stok.hariCek === tanggalTutupAktif(KINI) && D.stok.hariCek === '2026-09-18', D.stok.hariCek);
var W0 = SW.daftar[0].nama;
var CW = denganCacheSementara([{ koleksi: 'wadahLiteran', data: { id: 'cek1', tipe: 'cek', wadah: W0, hasil: 'sesuai', bukuKg: 10, tanggal: '2026-09-18', jam: '21:10' } }], function () { return dbStok(KINI).wadah[0]; });
ok('cek wadah tercatat 18 Sep 21.10 "sesuai" → wadah itu "✓ Sesuai 21.10" di dasbor (wbCekHari)', CW.dicek === true && CW.hasilTeks === 'Sesuai' && CW.jamCek === '21:10', J(CW));
// ---- PIUTANG & UTANG PEMASOK
var HP = hitungPiutang().filter(function (x) { return (x.sisa || 0) > 0; }); var totP = HP.reduce(function (a, x) { return a + x.sisa; }, 0);
var bonPerhatian = susunPerhatian().find(function (x) { return /Bon belum lunas/.test(x.teks); });
var jumStatus = D.tagihan.piutang.perStatus.reduce(function (a, s) { return a + s.rp; }, 0);
ok('piutang: total = mesin (hitungPiutang) = baris "Bon belum lunas" Perlu perhatian; Σ per status = total (870.000) — menutup', D.tagihan.piutang.total === totP && RP(totP) === bonPerhatian.nilai && jumStatus === totP && totP === 870000, J([D.tagihan.piutang.total, totP, bonPerhatian && bonPerhatian.nilai, jumStatus]));
var st = {}; semuaBon(KINI).forEach(function (b) { st[b.nama] = b.status; });
ok('piutang: keadaan dari Pelanggan › Bon — Bu Macet macet, Pak Tagih waktunya ditagih (jatuh tempo, 2 nama Rp750.000), Bu Baru masih baru (bukan jatuh tempo)', st['Bu Macet'] === 'macet' && st['Pak Tagih'] === 'perluTagih' && st['Bu Baru'] === 'baru' && D.tagihan.piutang.nJatuh === 2 && D.tagihan.piutang.rpJatuh === 750000 && D.tagihan.piutang.jatuh[0].nama === 'Bu Macet' && D.tagihan.piutang.jatuh[0].tujuan.orang === D.tagihan.piutang.jatuh[0].kunci, J([st, D.tagihan.piutang.jatuh]));
var U = D.tagihan.pemasok; var totU = hitungUtangPemasok().reduce(function (a, x) { return a + (x.totalUtang || 0); }, 0);
ok('utang pemasok: total = mesin (hitungUtangPemasok) = Bon pemasok; lewat + ≤7 hari + jauh + tanpa tempo = total — menutup', U.total === totU && U.rpLewat + U.rpDekat + U.rpJauh + U.rpTanpaTempo === U.total && U.total > 0, J([U.total, totU, U.rpLewat, U.rpDekat, U.rpJauh, U.rpTanpaTempo]));
ok('utang pemasok: bon 20 Agu (tempo umum 21 hari) LEWAT; bon 10 Sep jatuh 1 Okt = tempo masih jauh', U.lewat.length === 1 && U.lewat[0].tanggal === '2026-08-20' && U.nJauh === 1 && U.tujuan.ke === 'harga' && U.lewat[0].tujuan.pemasok === U.lewat[0].pemasok, J(U));
// ---- TREN
var TH = D.tren;
ok('tren hari: 14 batang = pemilih Laporan › Harian; omzet & nota tiap batang = daftar Laporan (hariTerakhir); batang terakhir = hari ini = omzet Hari ini', TH.batang.length === 14 && TH.batang[13].berjalan && TH.batang[13].id === iso && TH.batang.every(function (b) { return b.omzet === b.omzetDaftar && b.nota === b.notaDaftar; }) && TH.batang[13].omzet === D.hari.omzet, J(TH.batang.map(function (b) { return [b.id, b.omzet, b.omzetDaftar, b.nota, b.notaDaftar]; })));
ok('tren hari: laba kotor tiap batang = mesin laba hari itu; tujuan = Laporan › Harian hari itu', TH.batang.every(function (b) { return b.margin === hitungLabaRentang(function (t) { return t === b.id; }).margin && b.tujuan.keluarga === 'harian' && b.tujuan.hari === b.id; }));
var TM = dbTren('minggu', KINI); var DM = daftarMinggu(KINI, 8);
ok('tren minggu: batang = pemilih Laporan › Mingguan (8 minggu, Senin); minggu berjalan = angka "Minggu ini" Ringkasan', TM.batang.length === DM.length && TM.batang.length === 8 && TM.batang[TM.batang.length - 1].omzet === susunRingkasan('hari', ix, KINI).angka && TM.batang.every(function (b) { return b.tujuan.awal === b.id && DM.some(function (m) { return m.awal === b.id; }); }), J(TM.batang.map(function (b) { return [b.id, b.omzet]; })));
var TB = dbTren('bulan', KINI); var E = enamBulan(KINI);
ok('tren bulan: batang = pemilih Laporan › Bulanan (≤ 6, sejak catatan pertama); omzet = enamBulan; bulan berjalan = angka bulan Ringkasan', TB.batang.length === daftarBulan(KINI, 6).length && TB.batang.every(function (b) { return E.daftar.some(function (e) { return e.key === b.id && e.omzet === b.omzet; }) && b.tujuan.bulan === b.id; }) && TB.batang[TB.batang.length - 1].omzet === susunRingkasan('bulan', ix, KINI).angka, J(TB.batang.map(function (b) { return [b.id, b.omzet]; })));
var TA = dbTren('hari', new Date('2026-07-01T10:00:00+07:00'));
ok('tren hari sebelum catatan pertama (25 Jun): 7 batang ABSEN (bukan nol), sisanya terukur', TA.batang.filter(function (b) { return b.absen; }).length === 7 && TA.batang.filter(function (b) { return !b.absen; }).length === 7 && TA.batang[0].absen && !TA.batang[13].absen, J(TA.batang.map(function (b) { return [b.id, b.absen]; })));
// ---- galat satu kelompok tidak mematikan yang lain
var asliDB = daftarBarang; daftarBarang = function () { throw new Error('rusak uji'); };
var DG; try { DG = susunDasbor(KINI, 'hari'); } catch (e) { DG = { lempar: String(e) }; } daftarBarang = asliDB;
ok('galat di Stok → kelompok stok membawa pesan galat; hari ini, bulan ini, tagihan, tren tetap tergambar', !DG.lempar && DG.stok && /rusak uji/.test(DG.stok.galat) && !DG.hari.galat && !DG.bulan.galat && !DG.tagihan.galat && !DG.tren.galat, J(DG.lempar || DG.stok));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

JAM_DASBOR = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def utama_dasbor(js):
    h, e = jalan(JAM_DASBOR + js + '\nvar KOTAK = ' + json.dumps(kotak_dasbor()) + ';\n' + SKENARIO_DASBOR)
    if h is None: return 0, ['DASBOR JSC JATUH: ' + e]
    return h['lulus'], ['dasbor: ' + x for x in h['gagal']]


def statis_dasbor(r, l, d):
    """r = ringkasan.js · l = dasbor-logika.js · d = dasbor.js. Akses (owner saja) & satu sumber (tidak ada rumus uang dari dokumen mentah)."""
    out = []
    if "const pemilik = () => { const a = opsi.akun ? opsi.akun() : null; return !!a && a.jenis === 'owner'; };" not in r: out.append('akses: pemilik() bukan lagi akun berjenis owner')
    if "const modeDasbor = () => tampilan === 'dasbor' && pemilik();" not in r: out.append('akses: mode dasbor tidak lagi mensyaratkan owner')
    if "$('rkSaklar').hidden = !pemilik(); $('rkDasbor').hidden = !dsb;" not in r: out.append('akses: saklar / dasbor tidak disembunyikan untuk bukan-owner')
    if r.count('gambarDasbor(') != 3 or "if (dsb) {" not in r: out.append('akses: dasbor digambar di luar cabang mode dasbor owner (gambarDasbor dipanggil ' + str(r.count('gambarDasbor(')) + '×)')
    mentah = re.findall(r'\.(hargaTotal|hppTotalSaatJual|nominal|nilaiRp|subtotalHarga|merkList|hppPerKgSaatOpname)\b', l)
    if mentah: out.append('satu sumber: dasbor-logika membaca kolom dokumen mentah ' + ', '.join(sorted(set(mentah))) + ' — angka harus dari fungsi layar/mesin yang sudah ada')
    impor_data = re.findall(r"import \{([^}]*)\} from '\.\./data/toko\.js'", l)
    if impor_data and [x.strip() for x in impor_data[0].split(',')] != ['jumlahNota']: out.append('satu sumber: dasbor-logika mengimpor pembaca koleksi ' + impor_data[0])
    if re.search(r"from '\.\./(mesin|data)/", d): out.append('satu sumber: dasbor.js (gambar) mengimpor mesin/data — angka harus lewat dasbor-logika')
    return out


def berkas_dasbor():
    return [open(os.path.join(AKAR, f), encoding='utf-8').read() for f in ['baru/js/layar/ringkasan.js', 'baru/js/layar/dasbor-logika.js', 'baru/js/layar/dasbor.js']]


ASAP_DASBOR = r"""
console.error = function () {};
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var hidup = (CAD.penjualan || []).filter(function (p) { return !p.dikoreksiOleh && !p.dibatalkan; }); var tgl = hidup.map(function (p) { return p.tanggal || ''; }).sort();
var KINI = new Date(tgl[tgl.length - 1] + 'T20:00:00'); var D = susunDasbor(KINI, 'hari'); var ix = bangunIndeks();
var galat = ['hari', 'bulan', 'stok', 'tagihan', 'tren'].filter(function (k) { return D[k].galat; });
var kas = D.hari.kas.ada ? Math.abs(D.hari.kas.tempat.reduce(function (a, t) { return a + t.n; }, 0) - D.hari.kas.total) < 0.5 && D.hari.kas.cocok : 'tanpa titik';
var P = D.tagihan.piutang, U = D.tagihan.pemasok;
var hasil = { galat: galat, omzet: D.hari.omzet === susunRingkasan('jam', ix, KINI).angka, kas: kas, piutang: P.perStatus.reduce(function (a, s) { return a + s.rp; }, 0) === P.total && P.total === hitungPiutang().filter(function (x) { return x.sisa > 0; }).reduce(function (a, x) { return a + x.sisa; }, 0),
  pemasok: U.rpLewat + U.rpDekat + U.rpJauh + U.rpTanpaTempo === U.total, tren: D.tren.batang.every(function (b) { return b.omzet === b.omzetDaftar && b.nota === b.notaDaftar; }),
  biaya: Math.abs(D.bulan.biaya.reduce(function (a, r) { return a + r.n - r.menggantung; }, 0) - D.bulan.semuaBiaya) < 0.5, laba: D.bulan.labaBersih === labaBulan(D.bulan.key, KINI).labaBersih };
print(JSON.stringify(hasil));
"""


RUSAK_DASBOR = [
    ('8 Okt: kartu Biaya membuang baris negatif lagi', "const biaya = K.baris.filter((r) => Math.abs(r.pakai) > 0.5 || r.anggaran > 0).map(", "const biaya = K.baris.filter((r) => r.pakai > 0 || r.anggaran > 0).map("),
    ('dasbor: omzet hari ini bruto (retur tidak dikurangi)', "omzet: R.omzet, nota: R.n,", "omzet: R.omzet + R.retur, nota: R.n,"),
    ('dasbor: amplop laba tidak ikut kas per tempat', "const DB_TEMPAT = ['laci', 'brankas', 'rekening', 'amplop'];", "const DB_TEMPAT = ['laci', 'brankas', 'rekening'];"),
    ('dasbor: kas per tempat ditebak walau titik kas belum ada', "kas: S.ada ? { ada: true,", "kas: true ? { ada: true,"),
    ('dasbor: laba bersih bulan = "sampai hari ini" (beda dengan Laporan › Laba)', "labaBersih: K.labaBersih, susut: K.susut,", "labaBersih: T.labaSampai, susut: K.susut,"),
    ('dasbor: bon macet tidak dihitung di piutang', "const DB_STATUS_BON = ['janjiLewat', 'macet', 'perluTagih', 'menunggu', 'baru'];", "const DB_STATUS_BON = ['janjiLewat', 'perluTagih', 'menunggu', 'baru'];"),
    ('dasbor: bon macet bukan "jatuh tempo"', "const DB_JATUH = ['janjiLewat', 'macet', 'perluTagih'];", "const DB_JATUH = ['janjiLewat', 'perluTagih'];"),
    ('dasbor: bon pemasok bertempo jauh tidak ikut', "rpJauh: jauh.reduce((a, b) => a + b.sisa, 0),", "rpJauh: 0,"),
    ('dasbor: nota tren dihitung per baris', "nota: jumlahNota(hidup), diarsip: 0, tanpaPotret: 0 };", "nota: ambilPenjualan().filter((p) => hidup(p.tanggal)).length, diarsip: 0, tanpaPotret: 0 };"),   # Paket B: tren lewat lpHariRentang (laporan-logika)
    ('dasbor: laba kotor tren = omzet (bukan margin)', "const satu = (dari, sampai, x) => { const L = lpHariRentang(dari, sampai); return Object.assign({ omzet: L.omzetPenuh, margin: L.margin,", "const satu = (dari, sampai, x) => { const L = lpHariRentang(dari, sampai); return Object.assign({ omzet: L.omzetPenuh, margin: L.omzetPenuh,"),
    ('dasbor: cek wadah memakai tanggal kalender (bukan hari tutup aktif)', "const hariCek = tanggalTutupAktif(kini);", "const hariCek = hariIniIso(kini);"),
    ('dasbor: tren minggu lebih panjang dari pemilih Laporan (12)', "daftarMinggu(kini, 8)", "daftarMinggu(kini, 12)"),
    ('dasbor: hari sebelum catatan pertama digambar nol (bukan absen)', "const absen = !pertama || d.iso < pertama || !!d.tanpaPotret;", "const absen = false;"),
    ('dasbor: stok memakai urutan abjad (bukan kg terbesar)', ".sort((a, b) => b.kg - a.kg || a.nama.localeCompare(b.nama));", ".sort((a, b) => a.nama.localeCompare(b.nama));"),
    ('dasbor: galat satu kelompok mematikan seluruh dasbor', "return { galat: String((e && e.message) || e) }; } };", "throw e; } };"),
    ('dasbor: pemicu tanpa tujuan layar', "tujuan: tujuanW('pemicu-' + r.id) || { ke: 'laporan', keluarga: 'biaya', bulan: key } }))", "tujuan: null }))"),
]
RUSAK_DASBOR_STATIS = [
    ('akses: dasbor tampil untuk akun mana pun', 0, "const modeDasbor = () => tampilan === 'dasbor' && pemilik();", "const modeDasbor = () => tampilan === 'dasbor';"),
    ('akses: saklar tampil untuk bukan-owner', 0, "$('rkSaklar').hidden = !pemilik();", "$('rkSaklar').hidden = false;"),
    ('akses: pemilik() = siapa pun yang masuk', 0, "return !!a && a.jenis === 'owner'; };", "return !!a; };"),
    ('satu sumber: dasbor menjumlah hargaTotal sendiri', 1, "omzet: R.omzet, nota: R.n,", "omzet: ambilPenjualan().reduce((a, p) => a + p.hargaTotal, 0), nota: R.n,"),
    ('satu sumber: gambar dasbor membaca mesin langsung', 2, "import { DB_RENTANG } from './dasbor-logika.js';", "import { DB_RENTANG } from './dasbor-logika.js';\nimport { kasPada } from '../mesin/beku.js';"),
]


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            'F1 Beranda: bon lama bergulir ikut "bon tertua"': js.replace("const gulir = {}; ambilPemasokCatatan().forEach((c) => { if (c && c.bonLamaBergulir === true) gulir[String(c.id)] = true; });", "const gulir = {};"),
            '39b-19: sel per jam tidak mengurangi retur': js.replace("rkReturMenit(ix, hari).forEach((x) => { if (x.m === null) return; const j = Math.floor(x.m / 60); isi[j] = (isi[j] || 0) - x.uang; });", ""),
            '39b-19: angka minus tanpa titik ribuan': js.replace("if (n < 0) g[0] = '−' + g[0]; return g; };", "return RP(n).replace(/^Rp\\s?/, 'Rp ').split(/[ .]/).map((t, i) => (i >= 2 ? '.' + t : t)); };"),
            '39b-19: sel minus lebar NaN': js.replace("const v = typeof c.v === 'number' ? Math.max(0, c.v) : 0;", "const v = typeof c.v === 'number' ? c.v : 0;"),
            '39b-19: Ringkasan tidak mengurangi uang retur (omzet bruto)': js.replace("return { omzet: omzet - retur, penjualan: omzet,", "return { omzet: omzet, penjualan: omzet,"),
            '39b-19: sel hari Ringkasan bruto': js.replace("const rkOmzetHari = (ix, t) => ((ix.perHari[t] || {}).omzet || 0) - rkReturHari(ix, t);", "const rkOmzetHari = (ix, t) => ((ix.perHari[t] || {}).omzet || 0);"),
            '39b-19: angka 60 menit tidak mengurangi retur': js.replace("rkReturMenit(ix, hari).forEach((x) => { if (x.m !== null && menitKini - x.m >= 0 && menitKini - x.m < 60) o -= x.uang; }); return { omzet: o, nota: n.size }; })();\n  const M15", "return { omzet: o, nota: n.size }; })();\n  const M15"),
            '39b-19: angka 15 menit tidak mengurangi retur': js.replace("rkReturMenit(ix, hari).forEach((x) => { if (x.m !== null && menitKini - x.m >= 0 && menitKini - x.m < 15) o -= x.uang; }); return { omzet: o, nota: n.size }; })();", "return { omzet: o, nota: n.size }; })();"),
            '39b-19: sel cincin 15/60 menit tidak mengurangi retur': js.replace("rkReturMenit(ix, hari).forEach((x) => { if (x.m === null) return; const lalu = menitKini - x.m; if (lalu >= 0 && lalu < n) isi[n - 1 - lalu] -= x.uang; });", ""),
            '39b-19: "kemarin jam segini" mengurangi retur sehari penuh': js.replace("if (sampaiMenit == null) return r.uang;", "return r.uang;"),
            '39b-19: jam berjalan / tersibuk tidak mengurangi retur': js.replace("rkReturMenit(ix, hari).forEach((x) => { if (x.m === null) return; const j = Math.floor(x.m / 60); const o = jamIsi[j] || (jamIsi[j] = { omzet: 0, nota: new Set() }); o.omzet -= x.uang; });", ""),
            '39b-19: kunci nota trxId dulu (nota dua trxId jadi dua nota)': js.replace("const rkKunciNota = kunciNota;", "const rkKunciNota = (p) => String(p.trxId || p.grupNota || p.id);"),
            '39b-19: "kemarin jendela ini" tidak mengurangi retur kemarin': js.replace("rkReturMenit(ix, kemarin).forEach((x) => { if (x.m !== null && menitKini - x.m >= 0 && menitKini - x.m < 60) o -= x.uang; }); return 'kemarin jendela ini '", "return 'kemarin jendela ini '"),
            '39b-19: menit bernota yang returnya lebih besar jadi "tidak ada nota"': js.replace("nama === 'm15' ? (adaNota[i] ? { v: 1, kelas: 'titik' } : { v: 'rel', kelas: 'rel' }) : adaNota[i] || v !== 0 ? { v: v, kelas: 'emas' } : { v: 'rel', kelas: 'rel' }", "v > 0 ? { v: nama === 'm15' ? 1 : v, kelas: nama === 'm15' ? 'titik' : 'emas' } : { v: 'rel', kelas: 'rel' }"),
            'no.4: kelebihan bayar pelanggan tidak disebut di Perlu perhatian': js.replace("if (lebih.uang.n) out.push({ teks: 'Kelebihan bayar pelanggan · '", "if (false) out.push({ teks: 'Kelebihan bayar pelanggan · '"),
            'no.4 B1: hapus buku yang ternyata dibayar tidak disebut / disebut uang pelanggan': js.replace("if (lebih.hapus.n) out.push({ teks: 'Hapus buku yang ternyata dibayar · '", "if (false) out.push({ teks: 'Hapus buku yang ternyata dibayar · '"),
            'baris yang dibatalkan ikut dihitung': js.replace("ambilPenjualan().forEach((p) => {\n    const t = p.tanggal || ''; if (!t) return;", "ambilPenjualanSemua().forEach((p) => {\n    const t = p.tanggal || ''; if (!t) return;"),
            'nota dua baris dihitung dua nota': js.replace("const rkKunciNota = kunciNota;", "const rkKunciNota = (p) => String(p.id);"),
            'pembanding kemarin memakai SEHARI PENUH (bukan jam segini)': js.replace("const kmrSegini = adaSejak(kemarin) && !ketKmr ? rkJumlahRentang(ix, kemarin, kemarin, menitKini) : null;", "const kmrSegini = adaSejak(kemarin) && !ketKmr ? rkJumlahRentang(ix, kemarin, kemarin) : null;"),   # jangkar mengikuti sanggahan Paket B (hari tutup buku)
            'pembanding minggu lalu memakai seminggu penuh': js.replace("rkJumlahRentang(ix, rkIso(aMgLalu), rkIso(rkGeser(kini, -7)), menitKini)", "rkJumlahRentang(ix, rkIso(aMgLalu), rkIso(rkGeser(aMgLalu, 6)))"),
            'bulan lalu yang tidak lengkap tetap dibandingkan': js.replace("const blLalu = adaSejak(rkIso(blLaluAwal)) && !ketBl ?", "const blLalu = true ?"),
            'hari sebelum ada catatan digambar NOL (bukan absen)': js.replace("sel.push(t < ix.mulai || !ix.mulai || rkTanpaPotret(t) ? { v: null, kelas: 'absen' } :", "sel.push(false ? { v: null, kelas: 'absen' } :"),
            'jam yang belum terjadi digambar sebagai nol-emas': js.replace(": j > jamKini ? { v: 'rel', kelas: 'rel' } :", ": false ? { v: 'rel', kelas: 'rel' } :"),
            'minggu dimulai hari Minggu (bukan Senin)': js.replace("x.setDate(x.getDate() - ((x.getDay() + 6) % 7));", "x.setDate(x.getDate() - x.getDay());"),
            '60 menit terakhir memuat nota berjam sesudah sekarang': js.replace("if (m !== null && menitKini - m >= 0 && menitKini - m < 60) { o += p.hargaTotal || 0; n.add(rkKunciNota(p)); } });", "if (m !== null && menitKini - m < 60) { o += p.hargaTotal || 0; n.add(rkKunciNota(p)); } });"),
            'saldo kas ditebak walau titik kas belum disetel': js.replace("return { adaTitik: !!titik && total !== null, total,", "return { adaTitik: true, total: total === null ? 0 : total,"),
            'margin tidak menyebut persennya': js.replace("' · ' + pct + '%'", "''"),
            'tebal cincin linear melebihi batas lapis': js.replace("w = Math.max(1.5, wmax * Math.sqrt(Math.min(1, v / d.vmax)));", "w = Math.max(1.5, wmax * 2 * (v / d.vmax));"),
            'sejak-nota-terakhir memakai nota berjam sesudah sekarang': js.replace("return m !== null && m <= menitKini && m > a ? m : a; }, -1);", "return m !== null && m > a ? m : a; }, -1);"),
            'lapis yang tak berperan ikut tampak (opasitas 1)': js.replace("wmax = idx >= 0 ? WMAX[idx] : 6, op = idx >= 0 ? 1 : 0;", "wmax = idx >= 0 ? WMAX[idx] : 6, op = 1;"),
            'ketukan memilih sel yang salah (tidak digeser ke sel berjalan)': js.replace("let i = Math.round(((sudutDerajat % 360) + 360) % 360 / langkah) + jalan;", "let i = Math.round(((sudutDerajat % 360) + 360) % 360 / langkah);"),
            'label sel hari meleset sehari': js.replace("if (nama === 'hari') { const d = rkGeser(kini, -(n - 1 - i));", "if (nama === 'hari') { const d = rkGeser(kini, -(n - i));"),
            'pesanan yang sudah dibayar ikut "belum dibayar"': js.replace("const ps = ambilPesanan().filter(pesananBelumTuntas);", "const ps = ambilPesanan();"),
        }
        kode = 0
        B31 = berkas_titik(); B31r = dict(B31); B31r['baru/js/layar/ringkasan.js'] = B31r['baru/js/layar/ringkasan.js'].replace('Titik kas belum ada — Tutup hari malam ini', 'Titik kas belum disetel di perangkat ini — setel di sistem lama (Uang). Tutup hari malam ini', 1)
        g31 = teks_titik_basi(B31r) if B31r != B31 else []
        print(('BERBUNYI ' if g31 else 'DIAM!!   ') + '39b-31: Beranda kembali menyuruh setel titik kas di sistem lama → ' + (g31[0] if g31 else '-'))
        if not g31: kode = 3
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        jsd = bundel_dasbor()
        for nama, lama, baru in RUSAK_DASBOR:
            if jsd.count(lama) != 1: print('KONTROL BASI  ' + nama + ' (' + str(jsd.count(lama)) + '×)'); kode = 3; continue
            l, g = utama_dasbor(jsd.replace(lama, baru))
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        BD = berkas_dasbor()
        for nama, i, lama, baru in RUSAK_DASBOR_STATIS:
            if BD[i].count(lama) != 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            B2 = list(BD); B2[i] = B2[i].replace(lama, baru); g = statis_dasbor(*B2)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    t31 = teks_titik_basi(berkas_titik()); g = g + ['39b-31: ' + x for x in t31]; l = l + (0 if t31 else 1)
    ld, gd = utama_dasbor(bundel_dasbor()); sd = statis_dasbor(*berkas_dasbor()); l += ld + (0 if sd else 1); g = g + gd + sd
    print('KOTAK PASIR: %d lulus · %d gagal (termasuk dasbor owner: %d lulus)' % (l, len(g), ld + (0 if sd else 1))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')), key=os.path.basename)   # cadangan toko boleh di akar, _privat/ atau _arsip-mockup/ (semua di-gitignore); yang terbaru menurut tanggal di namanya
    if cad:
        c = json.load(open(cad[-1], encoding='utf-8'))
        h, e = jalan(js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP)
        if h is None: print('ASAP DATA TOKO: JSC JATUH ' + e); g.append('asap')
        else:
            print('ASAP DATA TOKO (%s, hari terakhir %s, catatan mulai %s): omzet hari/bulan/tahun = penjualan − uang retur cadangan = omzet Laporan: %s/%s/%s · %d skala tergambar · %d hal perlu perhatian'
                  % (os.path.basename(cad[-1]), h['akhir'], h['mulai'], h['hariCocok'], h['bulanCocok'], h['tahunCocok'], h['skala'], h['perhatian']))
            if not (h['hariCocok'] and h['bulanCocok'] and h['tahunCocok'] and h['skala'] == 7): g.append('asap: angka Ringkasan tidak sama dengan jumlah langsung baris cadangan')
        hd, ed = jalan(bundel_dasbor() + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP_DASBOR)
        if hd is None: print('ASAP DASBOR: JSC JATUH ' + ed); g.append('asap dasbor')
        else:
            beres = not hd['galat'] and all(hd[k] is True or hd[k] == 'tanpa titik' for k in ['omzet', 'kas', 'piutang', 'pemasok', 'tren', 'biaya', 'laba'])
            print('ASAP DASBOR (%s): %s — %s' % (os.path.basename(cad[-1]), 'MENUTUP' if beres else 'GAGAL', json.dumps(hd, ensure_ascii=False)))
            if not beres: g.append('asap dasbor: ada kelompok yang tidak menutup ke sumbernya di data toko')
    sys.exit(2 if g else 0)
