#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_dasbor_p3.py — PAKET P3 · Dasbor & peringatan, sisa kecil (owner 27 Nov 2026; sensus ulang 27 Nov: A4 B44 B48 B67 B97 B98 B104 B129).
KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  A4    peringatan uang → Pengingat & lonceng (owner saja): biaya lewat anggaran (lampu merah) · susut merah · modal per kg lewat batas (30 hari) · harga di bawah
        minimum · + usulan untung per kg di bawah target · kas di bawah ambang. Sumber = fungsi layar lain apa adanya (peringatan-logika), lewat lokal.peringatan;
        jenis di sistem-logika SAMA; saklar per jenis mematikan; jenis asing ditolak. Daftar peringatanBiaya tampil di kartu Bulan ini (Dasbor).
  B48   "N lambat laku · Rp X modal diam" + umur stok dalam rupiah per lapisan (≤ ambang umur · sampai batas stok lama · lebih tua · tanpa tanggal · kemasan):
        nilai = rumus modal tertahan A121 (sisa × modal per kg buku) — Σ lapisan = nilai stok hari ini (penjaga); batas stok lama = setelan owner (bawaan 60).
  B67   pesanan ke pemasok yang menunggu: jumlah, kg, perkiraan Rp (dokumen pesanan) — Tugas gudang & kartu Pembelian satu sumber; batal/datang tidak ikut.
  B129  nota "jual dulu, tandai" yang belum dicocokkan = baris Tugas gudang (Dasbor & Stok); tuntas sendiri sesudah cocokkan bertanggal ≥ notanya.
  B97   urutkan ulang daftar Dasbor (stok · piutang · pemasok · biaya): pilihan pertama = urutan lama, sort stabil, pilihan asing = bawaan.
  B98   tren 'tahun' = 12 batang bulanan; geser g jendela mundur (14 hari · 8 minggu · 6 bulan · 12 bulan), batang "berjalan" hanya yang memuat hari ini,
        tidak mundur melewati catatan pertama.
  B104  cetak Dasbor A4 tegak: kepala kertas (kop = identitasUsaha, saringan, saat cetak).
  B44   tombol aksi = tujuan ke lembar pencatat layar asal (statis; Dasbor tetap BACA SAJA); kartu Pembelian memuat pesanan & kabar barang masuk menunggu.

    python3 alat-uji/uji_dasbor_p3.py            → N lulus · 0 gagal (+ asap cadangan toko bila ada; angka rupiah toko tidak dicetak)
    python3 alat-uji/uji_dasbor_p3.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_jual_baru, uji_dasbor_sensus, uji_sisa_sensus, uji_gudang_label_patuh  # noqa: E402
PW = 'baru/js/layar/peringatan-logika.js'; KL = 'baru/js/layar/kpi-laba-logika.js'; SL = 'baru/js/layar/stok-logika.js'; GD = 'baru/js/layar/gudang-logika.js'
DL = 'baru/js/layar/dasbor-logika.js'; WG = 'baru/js/layar/dasbor-widget-logika.js'; SS = 'baru/js/layar/sistem-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_gudang_label_patuh.MODUL + [PW, WG])))
SUMBER = {'dasbor': 'baru/js/layar/dasbor.js', 'kisi': 'baru/js/layar/dasbor-kisi.js', 'app': 'baru/js/app.js', 'stok': 'baru/js/layar/stok.js', 'css': 'baru/css/ringkasan.css',
          'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'bundel': 'alat-uji/bundel_baru.py',
          'pw': PW, 'kl': KL, 'sl': SL, 'gd': GD, 'dl': DL, 'wg': WG, 'ss': SS}


def KARUNG(i, tgl, merk, kg, harga, hpp, cara='Tunai', nama='', **k):
    x = {'id': i, 'tanggal': tgl, 'jam': '09:00', 'caraBayar': cara, 'namaPelanggan': nama, 'jenis': 'karung', 'merkSumber': merk, 'beratKarungAcuan': 50,
         'jumlahKarung': kg / 50, 'totalKg': kg, 'hargaTotal': harga, 'grupNota': 'g' + i}
    if hpp is not None: x['hppTotalSaatJual'] = hpp
    x.update(k); return x
def MASUK(i, tgl, merk, kg, perKg, pemasok='Pemasok Contoh'):
    return {'id': i, 'tanggal': tgl, 'jam': '07:00', 'pemasok': pemasok, 'caraBayar': 'Tunai', 'biayaBongkar': 0, 'merkList': [
        {'merk': merk, 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': kg / 50, 'totalKg': kg, 'subtotalHarga': kg * perKg, 'hargaPerKg': perKg}]}
D_ = 'Pelanggan Contoh D'
KOTAK = {
    'batchMasuk': [dict(MASUK(100, '2026-09-01', 'Pelita', 100, 9000), stokAwal=True), MASUK(101, '2026-09-01', 'Angsa', 1000, 12000), MASUK(102, '2026-09-01', 'Kembang', 1000, 10000), MASUK(103, '2026-11-10', 'Kembang', 500, 10500)],   # 103: modal 10.500 > batas 10.000
    'penjualan': [
        KARUNG('s1', '2026-09-10', 'Angsa', 300, 3900000, 3600000),
        KARUNG('o1', '2026-10-10', 'Angsa', 200, 2500000, 2400000), KARUNG('o2', '2026-10-15', 'Kembang', 200, 2300000, 2000000),
        KARUNG('ob', '2026-10-20', 'Kembang', 30, 360000, 300000, 'Kredit', D_),
        KARUNG('lb', '2026-11-02', 'Kembang', 10, 120000, 100000, 'Kredit', 'Pelanggan Contoh L'),
        KARUNG('a1', '2026-11-09', 'Angsa', 100, 1300000, 1200000), KARUNG('k1', '2026-11-10', 'Kembang', 50, 600000, 500000),
        KARUNG('a2', '2026-11-13', 'Angsa', 50, 650000, 600000), KARUNG('a3', '2026-11-16', 'Angsa', 150, 1920000, 1800000), KARUNG('k2', '2026-11-17', 'Kembang', 100, 1150000, 1000000),
        KARUNG('x1', '2026-11-12', 'Kembang', 100, 1200000, None),   # tanpa modal: peringatan biaya "omzet tanpa modal" (kartu Bulan ini memuat ≥ 2 peringatan)
        KARUNG('t1', '2026-11-17', 'Kembang', 10, 120000, 105000, perluCocokkan=True, selisihKg=4, trxId='T1'),   # "jual dulu, tandai untuk dicocokkan"
        KARUNG('n1', '2026-11-18', 'Angsa', 50, 640000, 600000, 'Kredit', D_)],
    'pengeluaranHarian': [{'id': 'h1', 'kategori': 'toko', 'tanggal': '2026-11-05', 'jam': '09:00', 'keterangan': 'Bensin antar', 'nominal': 300000}],   # angkut: jatah 100.000 → MERAH
    'pesananPemasok': [
        {'id': 701, 'tanggal': '2026-11-15', 'jam': '10:00', 'pemasok': 'Pemasok Contoh', 'karung': 20, 'kg': 1000, 'rp': 12000000, 'status': 'menunggu', 'janjiTanggal': '2026-11-20'},
        {'id': 702, 'tanggal': '2026-11-16', 'jam': '10:00', 'pemasok': 'Pemasok Dua', 'karung': 10, 'kg': 500, 'rp': 0, 'status': 'menunggu'},                                      # pesanan lama tanpa harga
        {'id': 703, 'tanggal': '2026-11-16', 'jam': '11:00', 'pemasok': 'Pemasok Dua', 'karung': 6, 'kg': 300, 'rp': 3600000, 'status': 'batal'}],
}
ATUR = [{'id': 'catatStok', 'tempoHari': 21, 'modalFifoMulai': '', 'hppMaksPerKg': {'Kembang': 10000}}, {'id': 'harga', 'targetPerKg': 1000},
        {'id': 'kpiLaba', 'kasMinimum': 50000000}, {'id': 'kendaliBiaya', 'anggaran': {'angkut': 100000}}]

SKENARIO = r"""
(function () {
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); }; var dekat = function (a, b, t) { return a !== null && b !== null && a !== undefined && b !== undefined && Math.abs(a - b) < (t || 0.5); };
var KINI = new Date('2026-11-18T14:00:00+07:00'); var nId = 90000; var iso = '2026-11-18';
var W = { tanggal: '2026-11-18', jam: '14:00', kini: '2026-11-18T07:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK0).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'penyesuaianStok', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'stokBahanKemasan', 'pesanan', 'karantina', 'persetujuan', 'pengeluaranHarian', 'absenKaryawan', 'pajakSetoran', 'pajakOmzetLuar', 'pesananPemasok', 'pengingat'].forEach(function (n) { pasok(n, []); });
Object.keys(GK).forEach(function (n) { pasok(n, JSON.parse(J(GK[n]))); });
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-09-01', laci: 1000000, brankas: 0, rekening: 0, amplop: 0, diubahPada: '2026-09-01T14:00:00.000Z' }]);
setelSumber('cadangan', 'kotak pasir');
var aturDengan = function (extra) { var e = extra || []; var id = {}; e.forEach(function (d) { id[d.id] = 1; }); pasok('aturanToko', JSON.parse(J(ATUR)).filter(function (d) { return !id[d.id]; }).concat(e)); };
aturDengan([]);
var jenisDari = function (S) { var o = {}; S.forEach(function (x) { o[x.jenis] = (o[x.jenis] || 0) + 1; }); return o; };

// ==================== 1 · A4 PERINGATAN UANG → PENGINGAT & LONCENG ====================
var S = pwSumberPengingat(KINI); var JS = jenisDari(S); var by = function (j) { return S.filter(function (x) { return x.jenis === j; }); };
var K = kendaliBulan('2026-11', KINI); var rA = K.baris.find(function (r) { return r.id === 'angkut'; });
ok('1: biaya lewat anggaran = lampu MERAH kendali biaya apa adanya (Bensin & angkut Rp300.000 vs jatah) — id per bulan & pos, nominal = lewatnya', rA && rA.lampu === 'merah' && by('anggaran').length === 1 && by('anggaran')[0].id === 'anggaran|2026-11|angkut'
  && dekat(by('anggaran')[0].n, rA.selisih) && by('anggaran')[0].jatuh === iso && /lewat anggaran/.test(by('anggaran')[0].teks), J([rA && [rA.lampu, rA.selisih], by('anggaran')]));
var H = ckHppLewat('2026-10-20', iso);
ok('1: modal per kg lewat batas = kedatangan 30 hari terakhir (Stok › Barang masuk) — Kembang 10.500 > 10.000, lebih Rp500 × 500 kg; jatuh = tanggal kedatangan', by('hpp').length === 1 && by('hpp')[0].id === 'hpp|103|Kembang' && by('hpp')[0].n === 250000 && by('hpp')[0].jatuh === '2026-11-10' && H.daftar.length === 1, J([by('hpp'), H.daftar]));
var G = klKgBulan('2026-11', KINI);
ok('1: usulan — untung per kg di bawah target = klKgBulan.bawah apa adanya (target owner Rp1.000/kg) — SATU baris per bulan memuat jumlah & semua mereknya', by('untungKg').length === 1 && G.bawah.length >= 1
  && by('untungKg')[0].id === 'untungKg|2026-11|' + G.bawah.length && J(by('untungKg')[0].merek) === J(G.bawah.map(function (x) { return x.merek; })), J([by('untungKg'), G.bawah]));
var KM = klKasMinimum();
ok('1: usulan — kas di bawah ambang = klKasMinimum (ambang owner) · satu per hari · nominal = kurangnya', by('kas').length === 1 && KM.bawah && by('kas')[0].id === 'kas|' + iso && by('kas')[0].n === Math.round(KM.kurang), J([by('kas'), KM]));
ok('1: tanpa anggaran merah / target / ambang: tidak ada baris (bukan "nol" yang berbunyi)', (function () { aturDengan([{ id: 'kendaliBiaya', anggaran: {} }, { id: 'harga', targetPerKg: 0 }, { id: 'kpiLaba', kasMinimum: 1 }, { id: 'catatStok', tempoHari: 21, modalFifoMulai: '' }]);
  var X = pwSumberHitung(KINI, iso); aturDengan([]); return X.length === 0 && X.tidakTerbaca.length === 0; })());
// susut merah & harga di bawah minimum: pemetaan dari fungsi sumbernya (diganti sementara supaya keadaannya pasti)
ok('1: target ada tapi tidak ada merek di bawahnya (Rp1/kg) = tidak ada baris untung per kg', (function () { aturDengan([{ id: 'harga', targetPerKg: 1 }]); var X = pwSumberHitung(KINI, iso); aturDengan([]); return !X.some(function (x) { return x.jenis === 'untungKg'; }); })());
var asliS = shDasborSusut, asliH = shRingkasHarga;
shDasborSusut = function () { return { merah: ['Angsa', 'Kembang', 'Pelita', 'Murah'], kuning: [], target: 1, ambangMerah: 2, ambangKuning: 1.5, status: 'diAtas', pct: 3 }; };
shRingkasHarga = function () { return { keadaanMin: 'ada', nBawah: 7, bawah: [{ judul: 'Angsa · karung 50 kg', n: 600000, minimum: 650000 }, { judul: 'Kembang 5/25 kg', n: 100000, minimum: 110000 }], kalimatMin: '7 harga di bawah minimum' }; };
var S2 = pwSumberHitung(KINI, iso); shDasborSusut = asliS; shRingkasHarga = asliH; var b2 = function (j) { return S2.filter(function (x) { return x.jenis === j; }); };
ok('1: susut merah = shDasborSusut.merah · harga di bawah minimum = shRingkasHarga — SATU baris per jenis per bulan (jumlah di id; tiga nama pertama + "+N")', b2('susut').length === 1 && b2('susut')[0].id === 'susut|2026-11|4'
  && /4 merek susutnya merah/.test(b2('susut')[0].teks) && /\+1 merek/.test(b2('susut')[0].ket) && J(b2('susut')[0].merek) === J(['Angsa', 'Kembang', 'Pelita', 'Murah'])
  && b2('harga').length === 1 && b2('harga')[0].id === 'harga|2026-11|7' && b2('harga')[0].n === 0 && /Rp600\.000 < Rp650\.000/.test(b2('harga')[0].ket) && /\+4 lainnya/.test(b2('harga')[0].ket) && b2('harga')[0].id.indexOf('/') < 0, J([b2('susut'), b2('harga')]));
shDasborSusut = function () { throw new Error('rusak uji'); }; var S3 = pwSumberHitung(KINI, iso); shDasborSusut = asliS;
ok('1: satu sumber galat tidak mematikan yang lain (disebut di tidakTerbaca, bukan `galat`)', S3.tidakTerbaca.length === 1 && /susut/.test(S3.tidakTerbaca[0]) && jenisDari(S3).anggaran === 1 && S3.galat === undefined, J(S3.tidakTerbaca));
// jenis sama di sistem-logika · saklar · jenis asing
ok('1: jenis peringatan = SS_JENIS_PERINGATAN = SS_JENIS_PENGINGAT (nama sama) · bawaan nyala, ke Owner, hari 0', J(PW_JENIS.map(function (j) { return j.id; })) === J(SS_JENIS_PERINGATAN)
  && PW_JENIS.every(function (j) { var s = SS_JENIS_PENGINGAT.find(function (x) { return x.id === j.id; }); var B = SS_ATUR_BAWAAN.pengingat; return s && s.nama === j.nama && B.nyala[j.id] === true && J(B.ke[j.id]) === J(['Owner']) && B[s.kunci] === 0; }), J(SS_JENIS_PENGINGAT.slice(-6)));
var P0 = ssPengingat(KINI, { peringatan: S }); var aktifJ = jenisDari(P0.aktif);
ok('1: lewat lokal.peringatan → ssPengingat.aktif (jatuh hari ini / lewat): anggaran · hpp · untungKg · kas; "Atur" punya baris per jenis', aktifJ.anggaran === 1 && aktifJ.hpp === 1 && aktifJ.kas === 1 && aktifJ.untungKg === 1
  && P0.aturan.filter(function (a) { return SS_JENIS_PERINGATAN.indexOf(a.id) >= 0; }).length === 6, J([aktifJ, P0.aktif.map(function (p) { return p.id; })]));
ok('1: tanpa lokal.peringatan (akun bukan owner) = tidak ada jenis peringatan uang', !ssPengingat(KINI, {}).aktif.some(function (p) { return SS_JENIS_PERINGATAN.indexOf(p.jenis) >= 0; }));
ok('1: jenis asing lewat lokal.peringatan ditolak', !ssSumberPengingat(KINI, { peringatan: [{ id: 'palsu', jenis: 'bon', kunci: 'x', teks: 'palsu', siapa: 'x', jatuh: iso, n: 1 }] }).some(function (p) { return p.id === 'palsu'; }));
aturDengan([{ id: 'pengingat', nyala: { kas: false } }]); var P1 = ssPengingat(KINI, { peringatan: S }); aturDengan([]);
ok('1: saklar per jenis (Menu › Sistem › Pengingat): kas dimatikan → tidak aktif, yang lain tetap', !P1.aktif.some(function (p) { return p.jenis === 'kas'; }) && P1.aktif.some(function (p) { return p.jenis === 'anggaran'; }), J(jenisDari(P1.aktif)));
var T9 = susunAturSistem('pengingat', { hariKas: '9' }, W); var T3 = susunAturSistem('pengingat', { hariKas: '3' }, W);
ok('1: hari sebelum jenis baru dijaga 0–7 (disimpan bila sah)', !!T9.tolak && /hariKas/.test(T9.tolak) && !T3.tolak && T3.dokumen[0].data.hariKas === 3, J([T9, T3.tolak]));
var B = dbBulanIni(KINI); var Wb = peringatanBiaya(K, pemicuBiaya(K), titikImpas(K, KINI));
ok('1: kartu Bulan ini memuat DAFTAR peringatanBiaya apa adanya (urutan & teks sama; tiap baris punya tujuan)', B.peringatan.length === Wb.length && Wb.length >= 2 && B.peringatan.every(function (w, i) { return w.id === Wb[i].id && w.teks === Wb[i].teks && w.tujuan; }), J([B.peringatan, Wb.map(function (w) { return w.id; })]));

// ==================== 2 · B48 MODAL DIAM & UMUR STOK DALAM RUPIAH ====================
var M = klModalDiam(KINI); var L = {}; M.lapisan.forEach(function (b) { L[b.id] = b; }); var MT = klModalTertahan(KINI, iso, iso);
var nk = klNilaiStokHari(iso).kunci; var pk = function (k) { return nk[k].rp / nk[k].kg; };
ok('2: lapisan bawaan ≤30 · 31–60 · >60 hari: Kembang kedatangan 10 Nov 500 kg muda; sisa kedatangan 1 Sep (Kembang 500 + Angsa 150 kg) tua', M.atur.muda === 30 && M.atur.tua === 60 && !M.atur.dariOwner
  && dekat(L.muda.kg, 500, 0.01) && dekat(L.tengah.kg, 0, 0.01) && dekat(L.tua.kg, 650, 0.01) && dekat(L.muda.rp, 500 * pk('Kembang')) && dekat(L.tua.rp, 500 * pk('Kembang') + 150 * pk('Angsa')), J([M.lapisan, M.atur]));
ok('2: PENJAGA Σ lapisan = nilai stok hari ini = modal tertahan A121 pada hari ini (rumus nilai yang SAMA)', M.menutup && dekat(M.total, MT.kini) && dekat(M.lapisan.reduce(function (a, b) { return a + b.rp; }, 0), MT.kini), J([M.total, MT.kini]));
var UB = umBarang(KINI); var lam = UB.filter(function (r) { return r.lambat && r.ada; });
ok('2: stok awal (bukan kedatangan) = lapisan TANPA TANGGAL masuk — Pelita 100 kg', dekat(L.tanpa.kg, 100, 0.01) && dekat(L.tanpa.rp, nk['Pelita'].rp), J(L.tanpa));
ok('2: "N lambat laku · Rp X modal diam" = barang lambat laku Umur & putaran × nilai bukunya', M.n === lam.length && M.n === 3 && dekat(M.rp, lam.reduce(function (a, r) { return a + nk[r.kunci].rp; }, 0)) && /3 lambat laku/.test(M.kalimat) && /modal diam/.test(M.kalimat), J([M.n, M.daftar]));
aturDengan([{ id: 'stokUmur', ambangUmurHari: 100, ambangHariStok: 30, periodeHari: 30, targetHariMin: 7, targetHariMaks: 14, umurTuaHari: 120 }]); var M2 = klModalDiam(KINI); var L2 = {}; M2.lapisan.forEach(function (b) { L2[b.id] = b; });
ok('2: setelan owner (ambang umur 100, batas stok lama 120) dibaca: semua lapisan ≤100 hari; lambat laku hanya yang hari stoknya > 30 (Kembang) atau tanpa gerak (Pelita) — Angsa tidak', M2.atur.muda === 100 && M2.atur.tua === 120 && M2.atur.dariOwner && dekat(L2.muda.kg, 1150, 0.01) && dekat(L2.tua.kg, 0, 0.01)
  && M2.n === 2 && J(M2.daftar.map(function (x) { return x.nama; }).sort()) === J(['Kembang', 'Pelita']) && L2.tengah.nama === '101–120 hari', J([M2.lapisan, M2.daftar]));
aturDengan([]);
var A1 = susunAturUmur({ umurTuaHari: '20', ambangUmurHari: '30' }, W); var A2 = susunAturUmur({ umurTuaHari: '90' }, W);
ok('2: batas stok lama ≤ ambang umur DITOLAK berkalimat; yang sah tersimpan di dokumen stokUmur yang sama', !!A1.tolak && /Batas stok lama/.test(A1.tolak) && !A2.tolak && A2.dokumen[0].data.id === 'stokUmur' && A2.dokumen[0].data.umurTuaHari === 90 && UM_ATUR_BAWAAN.umurTuaHari === 60, J([A1, A2.tolak]));
var Q = dbMutu(KINI);
ok('2: Dasbor › Mutu usaha membawa modalDiam (sekarang) tanpa galat', Q.modalDiam && !Q.modalDiam.galat && Q.modalDiam.n === M.n, J(Q.modalDiam && Q.modalDiam.galat));

// ==================== 3 · B67 PESANAN PEMASOK MENUNGGU · B129 NOTA JUAL-DULU ====================
var PP = gdPesananPemasok();
ok('3: pesanan menunggu: 2 pesanan · 30 karung · 1.500 kg · ±Rp12.000.000 · 1 tanpa harga; yang BATAL tidak ikut; urut Rp per pemasok', PP.n === 2 && PP.karung === 30 && PP.kg === 1500 && PP.rp === 12000000 && PP.tanpaHarga === 1
  && PP.pemasok[0].pemasok === 'Pemasok Contoh' && PP.pemasok[0].janji === '2026-11-20' && /1 pesanan tanpa harga/.test(PP.kalimat), J(PP));
var TG = gdTugas(KINI); var row = function (id) { return TG.daftar.find(function (x) { return x.id === id; }); };
ok('3: Tugas gudang "Pesanan ke pemasok" membawa kg & Rp yang SAMA (satu sumber)', row('pesanPemasok').n === 2 && row('pesanPemasok').kg === 1500 && row('pesanPemasok').rp === 12000000 && /1500 kg · ±Rp12\.000\.000/.test(row('pesanPemasok').ket), J(row('pesanPemasok')));
var DB = dbBeli(KINI, null);
ok('3: kartu Pembelian membawa pesanan menunggu yang sama (sekarang)', DB.pesanan && DB.pesanan.n === 2 && DB.pesanan.rp === 12000000, J(DB.pesanan));
ok('3: B129 — nota "jual dulu, tandai" yang belum dicocokkan = baris Tugas gudang (awas) + ikut Dasbor (gdDasbor.tugas.terbuka)', row('tembus').n === 1 && row('tembus').awas && /Kembang/.test(row('tembus').ket)
  && gdDasbor(KINI).tugas.terbuka.some(function (x) { return x.id === 'tembus' && x.n === 1; }), J(row('tembus')));
pasok('penyesuaianStok', [{ id: 'q1', tanggal: '2026-11-18', jam: '15:00', merk: 'Kembang', selisihKg: 0, kgFisik: 1, kgBuku: 1 }]);
ok('3: sesudah Kembang dicocokkan bertanggal ≥ notanya → tanda tuntas sendiri (baris 0)', gdTugas(KINI).daftar.find(function (x) { return x.id === 'tembus'; }).n === 0);
pasok('penyesuaianStok', []);

// ==================== 4 · B97 URUT DAFTAR ====================
var dd = [{ nama: 'Beta', kg: 5, sisa: 100, n: 10, lampu: 'hijau' }, { nama: 'Alfa', kg: 50, sisa: 300, n: 30, lampu: 'merah' }, { nama: 'Cici', kg: 20, sisa: 300, n: 20, lampu: 'amber' }];
var nm = function (d) { return d.map(function (x) { return x.nama; }).join(); };
ok('4: urutan pertama = urutan lama (apa adanya) · terbanyak · nama · lampu dulu · seri = urutan lama', nm(dbUrutkan('stok', dd, 'habis')) === 'Beta,Alfa,Cici' && nm(dbUrutkan('stok', dd, 'kg')) === 'Alfa,Cici,Beta'
  && nm(dbUrutkan('piutang', dd, 'rp')) === 'Alfa,Cici,Beta' && nm(dbUrutkan('pemasok', dd, 'nama')) === 'Alfa,Beta,Cici' && nm(dbUrutkan('biaya', dd, 'lampu')) === 'Alfa,Cici,Beta' && nm(dbUrutkan('biaya', dd, 'rp')) === 'Alfa,Cici,Beta', J([nm(dbUrutkan('stok', dd, 'kg'))]));
ok('4: pilihan asing = bawaan; tiap daftar punya 3 pilihan; daftar asli tidak diubah', dbUrutPilih('stok', 'ngawur') === 'habis' && dbUrutPilih('biaya', '') === 'pos' && Object.keys(DB_URUT).join() === 'stok,piutang,pemasok,biaya' && nm(dd) === 'Beta,Alfa,Cici');

// ==================== 5 · B98 TREN TAHUN & GESER ====================
var T0 = dbTren('hari', KINI); var T1 = dbTren('hari@1', KINI); var T4 = dbTren('hari@4', KINI); var T5 = dbTren('hari@5', KINI);
ok('5: geser 0 = 14 hari sampai hari ini (berjalan = hari ini) · tidak bisa maju', T0.batang.length === 14 && T0.batang[13].id === iso && T0.batang[13].berjalan && T0.geser === 0 && !T0.bisaMaju && T0.periode === '14 hari terakhir', J([T0.batang[13].id, T0.periode]));
ok('5: hari@1 = 14 hari sebelumnya (22 Okt – 4 Nov), tidak ada batang "berjalan", bisa maju; angka = mesin yang sama per hari', T1.batang.length === 14 && T1.batang[0].id === '2026-10-22' && T1.batang[13].id === '2026-11-04' && !T1.batang.some(function (b) { return b.berjalan; }) && T1.bisaMaju && T1.geser === 1
  && T1.batang.find(function (b) { return b.id === '2026-11-02'; }).omzet === lpHariRentang('2026-11-02', '2026-11-02').omzetPenuh && /mundur 1×/.test(T1.periode), J([T1.batang[0].id, T1.batang[13].id, T1.periode]));
ok('5: tidak mundur melewati catatan pertama (1 Sep): hari@4 (10–23 Sep) masih bisa, hari@5 tidak', T4.bisaMundur && T4.batang[0].id === '2026-09-10' && !T5.bisaMundur, J([T4.batang[0].id, T4.bisaMundur, T5.bisaMundur]));
var TT = dbTren('tahun', KINI); var TF = dbTren('tahun', new Date('2027-08-18T14:00:00+07:00'));
ok('5: Tahun = batang BULANAN sampai 12 (data Sep–Nov → 3 batang; Agu 2027 → 12 batang Sep 2026–Agu 2027) · sumber Laporan › Bulanan · tidak bisa mundur di awal catatan', TT.rentang === 'tahun' && TT.batang.length === 3 && TT.batang[2].id === '2026-11' && TT.batang[2].berjalan && !TT.bisaMundur
  && TF.batang.length === 12 && TF.batang[0].id === '2026-09' && TF.batang[11].id === '2027-08' && TT.sumber === 'Laporan › Bulanan' && DB_RENTANG.some(function (r) { return r[0] === 'tahun'; }), J([TT.batang.map(function (b) { return b.id; }), TF.batang.length]));
var TM = dbTren('minggu@1', KINI);
ok('5: minggu@1 = 8 minggu sebelumnya, dipotong di catatan pertama; bulan geser di luar catatan = kosong (bukan galat)', TM.batang.length >= 1 && TM.batang[TM.batang.length - 1].id === '2026-09-21' && !TM.batang.some(function (b) { return b.berjalan; }) && dbTren('bulan@1', KINI).batang.length === 0, J(TM.batang.map(function (b) { return b.id; })));
var SDk = dbKelompok('tren', KINI, 'hari@1');
ok('5: dbKelompok meneruskan rentang bergeser (kunci ingatan tren ikut berbeda)', SDk.geser === 1 && SDk.batang[13].id === '2026-11-04');

// ==================== 6 · B104 CETAK · widget katalog · bawaan tidak berubah ====================
var C = dbCetak(KINI, null, { teks: 'data per 14.00' });
ok('6: kepala kertas cetak: kop = identitasUsaha (satu sumber dokumen berkop), A4 tegak dua kolom, saat cetak & cap data', C.kop.nama === identitasUsaha().nama && C.kop.nama.length > 0 && C.kertas.id === 'A4' && C.kertas.arah === 'tegak' && C.kertas.kolom === 2
  && /Dicetak Rabu 18 Nov 2026 14\.00/.test(C.dicetak) && C.cap === 'data per 14.00' && /^Hari ini/.test(C.periode), J(C));
var C2 = dbCetak(KINI, dbSaring({ id: 'bulanLalu' }, KINI), null); ok('6: saringan ikut tertulis di kertas', /Oktober 2026/.test(C2.periode), C2.periode);
var D = dbTambahan(susunDasbor(KINI, 'hari'), KINI); var WS = wgSusun(['peringatanUang', 'modalDiam', 'pesananPemasok', 'notaTembus'].map(function (x) { return { id: x }; }), D); var wb = {}; WS.forEach(function (w) { wb[w.id] = w; });
ok('6: empat angka baru tersusun dari kelompok dasbor yang SAMA, tanpa galat', WS.length === 4 && WS.every(function (w) { return w.nilai !== 'gagal dihitung'; }) && wb.peringatanUang.nilai === D.peringatan.n + ' menyala' && D.peringatan.n === S.length
  && wb.pesananPemasok.nilai === '1.500 kg' && wb.notaTembus.nilai === '1 nota' && wb.modalDiam.awas, J(WS.map(function (w) { return [w.id, w.nilai, w.ket]; })));
ok('6: susunan BAWAAN Dasbor tidak berubah (kartu & angka baru hanya lewat "+ Tambah kartu")', J(WG_BAWAAN.map(function (w) { return w.id; })) === J(['kHari', 'kKpi', 'kTren', 'kBulan', 'kWadah', 'kPemicu', 'kTagihan', 'kStok', 'kMutu', 'kPondasi', 'kB2b']) && WG_KATALOG.length <= WG_MAKS);
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
})();
"""

RUSAK = [
    ('anggaran: lampu bukan merah yang diingatkan', PW, "if (r.lampu !== 'merah') return;", "if (r.lampu !== 'hijau') return;"),
    ('modal lewat batas hanya 1 hari terakhir', PW, "export const PW_HPP_HARI = 30;", "export const PW_HPP_HARI = 1;"),
    ('untung per kg berbunyi walau tidak ada merek di bawah target', PW, "    if (!G.bawah.length) return;\n", ""),
    ('kas berbunyi walau di atas ambang', PW, "if (!K.nyala || !K.bawah) return;", "if (!K.nyala) return;"),
    ('harga: jumlah tidak di id (Selesai menelan harga baru)', PW, "id: 'harga|' + key + '|' + H.nBawah,", "id: 'harga|' + key,"),
    ('susut: satu baris per merek (lonceng banjir)', PW, "if (!S.merah.length) return;", "if (!S.merah.length) return; S.merah.slice(1).forEach((m) => out.push({ id: 'susut|' + key + '|' + m, jenis: 'susut', kunci: m, teks: m, siapa: 'stok', jatuh: iso, n: 0 }));"),
    ('galat satu sumber mematikan semua', PW, "const coba = (nama, f) => { try { f(); } catch (e) { tak.push(", "const coba = (nama, f) => { try { f(); } finally { tak.push("),
    ('jenis asing lolos lewat lokal.peringatan', SS, "if (p && SS_JENIS_PERINGATAN.indexOf(p.jenis) >= 0 && /", "if (p && /"),
    ('bawaan anggaran mati', SS, "pengingat: { nyala: { anggaran: true,", "pengingat: { nyala: { anggaran: false,"),
    ('hari jenis baru tidak dijaga', SS, "['hariAnggaran', 'hariSusut', 'hariHpp', 'hariHarga', 'hariUntungKg', 'hariKas'].map((k) => angka(k, 0, 7, 'hari'))", "[].map((k) => angka(k, 0, 7, 'hari'))"),
    ('batas stok lama tidak dibaca', KL, "const tua = Math.max(A.umurTuaHari, muda + 1);", "const tua = Math.max(90, muda + 1);"),
    ('nilai lapisan bukan rumus modal tertahan', KL, "return x.kg > 0 ? x.rp / x.kg : 0; };", "return x.kg > 0 ? x.rp / x.kg * 1.01 : 0; };"),
    ('modal diam memuat barang yang tidak lambat', KL, "const lambat = R.filter((r) => r.lambat && r.ada)", "const lambat = R.filter((r) => r.ada)"),
    ('tanpa tanggal tidak masuk lapisan', KL, "if (U.tanpaTanggalKg > 0) { ke('tanpa',", "if (false) { ke('tanpa',"),
    ('batas stok lama ≤ ambang lolos', SL, "if (o.umurTuaHari <= o.ambangUmurHari) return { tolak:", "if (false) return { tolak:"),
    ('pesanan batal ikut dihitung', GD, "const D = d || pesananSemua().filter((p) => p.status === 'menunggu');", "const D = d || pesananSemua();"),
    ('tugas gudang tanpa kg & Rp', GD, "return { n: d.length, kg: P.kg, rp: P.rp,", "return { n: d.length, kg: 0, rp: 0,"),
    ('nota jual-dulu tidak dibaca', GD, "const T = notaTembusBelumCocok();", "const T = { n: 0, nama: [] };"),
    ('geser hari 7 hari, bukan 14', DL, "ugTambahHari(iso, -14 * g)) + 'T12:00:00');", "ugTambahHari(iso, -7 * g)) + 'T12:00:00');"),
    ('batang lama dianggap berjalan sesudah geser', DL, "berjalan: d.iso === iso, absen,", "berjalan: d.hariIni, absen,"),
    ('tahun hanya 6 batang', DL, "else if (rentang === 'tahun') batang = perBulan(12);", "else if (rentang === 'tahun') batang = perBulan(6);"),
    ('mundur melewati catatan pertama', DL, "bisaMundur: !!pertama && !!a0 && a0 > pertama", "bisaMundur: !!pertama && !!a0 && a0 >= pertama"),
    ('urut terbanyak dibalik', DL, "    : (a, b) => nilai(b.x) - nilai(a.x);", "    : (a, b) => nilai(a.x) - nilai(b.x);"),
    ('urut asing bukan bawaan', DL, "return U.some((x) => x[0] === cara) ? cara : U[0][0]; };", "return U.some((x) => x[0] === cara) ? cara : U[1][0]; };"),
    ('peringatan biaya dipotong satu', DL, "    peringatan: W.map((w) => ({", "    peringatan: W.slice(0, 1).map((w) => ({"),
    ('pesanan pemasok tidak di kartu Pembelian', DL, "pesanan: dbCoba(() => gdPesananPemasok()) };", "pesanan: null };"),
    ('kertas cetak bukan A4 tegak', DL, "export const DB_CETAK_KERTAS = { id: 'A4', arah: 'tegak', kolom: 2,", "export const DB_CETAK_KERTAS = { id: 'F4', arah: 'tegak', kolom: 2,"),
    ('widget peringatan salah hitung', WG, "return { nilai: P.n ? P.n + ' menyala' : 'tidak ada',", "return { nilai: P.n ? (P.n + 1) + ' menyala' : 'tidak ada',"),
    ('kartu baru masuk susunan bawaan', WG, "export const WG_BAWAAN = ['kHari', 'kKpi', 'kTren', 'kBulan', 'kWadah', 'kPemicu', 'kTagihan', 'kStok', 'kMutu', 'kPondasi', 'kB2b']", "export const WG_BAWAAN = ['kHari', 'kKpi', 'kTren', 'kBulan', 'kWadah', 'kPemicu', 'kTagihan', 'kStok', 'kMutu', 'kPondasi', 'kB2b', 'modalDiam']"),
]

STATIS = [
    ('lonceng & Pengingat: peringatan uang owner saja, lewat lokal.peringatan', 'app', ["import { pwSumberPengingat } from './layar/peringatan-logika.js';", "if (!a || a.jenis !== 'owner') return []; try { return pwSumberPengingat(",
        "LC_JENIS.push('anggaran', 'susut', 'hpp', 'harga', 'untungKg', 'kas');", "ssPengingat(k, { peringatan: sumberPeringatan(), patuh: sumberPatuh(), gudang: sumberGudang() }).aktif", "    peringatan: sumberPeringatan(), patuh: sumberPatuh(), gudang: sumberGudang() }),   // putaran 24"]),
    ('modul baru di-modulepreload & ikut bundel jsc otomatis', 'index', ['<link rel="modulepreload" href="js/layar/peringatan-logika.js">']),
    ('bundel jsc memuat peringatan-logika bila dasbor-logika ada', 'bundel', ["PW_MODUL = 'baru/js/layar/peringatan-logika.js'", "PW_PEMAKAI = ('dasbor-logika.js',)"]),
    ('B44 tombol aksi = tujuan lembar pencatat (tanpa tulis dari Dasbor)', 'dasbor', ["aksi('hari', [", "{ ke: 'uang', keluarga: 'tutup' }", "aksi('stok', [", "{ ke: 'stok', lembar: 'masuk' }", "aksi('tagihan', [", "{ ke: 'harga', keluarga: 'bon' }", "aksi('beli', [", "aksi('bulan', [", "aksi('wadah', ["]),
    ('B44/B67 kartu Pembelian: pesanan & kabar barang masuk menunggu', 'dasbor', ['+ barisMenunggu(Bl)', 'function barisMenunggu(Bl)', "find((x) => x.id === 'masuk')"]),
    ('A4 daftar peringatan biaya di kartu Bulan ini', 'dasbor', ['+ barisPeringatan(B)', 'function barisPeringatan(B)']),
    ('B48 Mutu usaha: lambat laku + modal diam + lapisan rupiah', 'dasbor', ["' modal diam' : '')", "baris('lapisan', 'Umur stok dalam rupiah'"]),
    ('B129 Dasbor › Gudang: nota jual-dulu & pesanan pemasok', 'dasbor', ["find((x) => x.id === 'tembus')", "r('tembus', 'Nota jual dulu, belum dicocokkan'", "r('pesanPemasok', 'Pesanan pemasok menunggu'"]),
    ('B97 pita urut di stok · piutang · pemasok · biaya, diingat perangkat', 'dasbor', ["pitaUrut('stok')", "pitaUrut('piutang')", "pitaUrut('pemasok')", "pitaUrut('biaya')", "localStorage.setItem(KUNCI_URUT, JSON.stringify(urut))", "dbUrutkan('stok', S.merek, cara)", "dbUrutkan('piutang', P.jatuh, urut.piutang)", "dbUrutkan('pemasok', U.lewat.concat(U.dekat), urut.pemasok)", "dbUrutkan('biaya', B.biaya, urut.biaya)"]),
    ('B98 geser tren & rentang komposit ke Ringkasan', 'dasbor', ['data-db-geser="-1"', 'data-db-geser="1"', "const rentangKini = () => (geser ? rentang + '@' + geser : rentang);", 'rentang: () => rentangKini()']),
    ('B104 cetak: salin kartu ke #cetakDokumen, tablet ditolak berkalimat, mode terang selama cetak', 'dasbor', ['function cetakDasbor()', "document.getElementById('cetakDokumen')", "document.body.classList.add('cetak-dokumen')", 'if (asliAda()) return { ok: false,', "document.body.classList.remove('gelap')", '<div class="layar-ringkasan dc-isi">']),
    ('B104 tombol Cetak di kepala Dasbor', 'kisi', ['data-da-aksi="cetak"', "if (x === 'cetak') {"]),
    ('CSS: aksi, urut, geser, kertas A4 tegak', 'css', ['@page dasbor { size: A4 portrait; margin: 12mm; }', '#cetakDokumen .db-cetak { page: dasbor;', '.layar-ringkasan .db-aksi-btn', '.layar-ringkasan .db-urut-pil', '.layar-ringkasan .db-geser-btn', 'prefers-reduced-motion']),
    ('Stok › Umur & putaran › Atur: batas stok lama', 'stok', ["isian('umTua', 'umurTuaHari'", 'umurTuaHari: String(a.umurTuaHari)']),
    ('pages.yml menjalankan uji ini + kontrol', 'pages', ['python3 alat-uji/uji_dasbor_p3.py && python3 alat-uji/uji_dasbor_p3.py --kontrol']),
    ('BACA-DULU bagian Paket P3', 'baca', ['Paket P3', 'uji_dasbor_p3']),
]
RUSAK_STATIS = [
    ('lonceng tanpa peringatan uang', 'app', "LC_JENIS.push('anggaran', 'susut', 'hpp', 'harga', 'untungKg', 'kas');", ''),
    ('peringatan uang untuk semua akun', 'app', "if (!a || a.jenis !== 'owner') return []; try { return pwSumberPengingat(", "try { return pwSumberPengingat("),
    ('Pengingat Menu tanpa peringatan', 'app', "    peringatan: sumberPeringatan(), patuh: sumberPatuh(), gudang: sumberGudang() }),   // putaran 24", "    patuh: sumberPatuh(), gudang: sumberGudang() }),   // putaran 24"),
    ('tombol aksi Tutup hari hilang', 'dasbor', "{ ke: 'uang', keluarga: 'tutup' }", "{ ke: 'uang', keluarga: 'keluar' }"),
    ('urut stok tidak dipakai', 'dasbor', "dbUrutkan('stok', S.merek, cara)", "S.merek"),
    ('cetak di tablet tidak ditolak', 'dasbor', 'if (asliAda()) return { ok: false,', 'if (false) return { ok: false,'),
    ('tombol Cetak hilang', 'kisi', 'data-da-aksi="cetak"', 'data-da-aksi="x"'),
    ('kertas bukan A4 tegak', 'css', '@page dasbor { size: A4 portrait; margin: 12mm; }', '@page dasbor { size: A4 landscape; margin: 12mm; }'),
    ('komentar // menelan kode', 'pw', "export const PW_HPP_HARI = 30;", "// batas\nexport const PW_HPP_HARI = 30; // hari; const x = 1;"),
    ('modul P3 menulis dokumen', 'pw', "export function pwRingkas(kini) {", "export function pwRingkas(kini) { const z = { koleksi: 'aturanToko' };"),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_dasbor_p3.py && python3 alat-uji/uji_dasbor_p3.py --kontrol', 'true'),
]

ASAP = r"""
(function () {
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(Date.now()); var iso = hariIniIso(kini); var out = { akhir: iso, galat: [] };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + e); return null; } };
var S = aman('peringatan', function () { return pwSumberPengingat(kini); }); out.peringatan = S ? { jenis: (function () { var o = {}; S.forEach(function (x) { o[x.jenis] = (o[x.jenis] || 0) + 1; }); return o; })(), tidakTerbaca: S.tidakTerbaca } : null;
var M = aman('modal diam', function () { return klModalDiam(kini); }); out.modalDiam = M ? { menutup: M.menutup, lambat: M.n, lapisanKg: M.lapisan.filter(function (b) { return b.kg !== null; }).map(function (b) { return [b.id, Math.round(b.kg)]; }), samaA121: Math.abs(M.total - klModalTertahan(kini, iso, iso).kini) < 1 } : null;
var P = aman('pesanan', function () { return gdPesananPemasok(); }); out.pesanan = P ? { n: P.n, tanpaHarga: P.tanpaHarga } : null;
var T = aman('tugas', function () { return gdTugas(kini); }); out.tembus = T ? (T.daftar.find(function (x) { return x.id === 'tembus'; }) || {}).n : null; out.tugasGalat = T ? T.daftar.filter(function (x) { return x.galat; }).map(function (x) { return x.id + ': ' + x.ket; }) : null;
out.tren = {}; ['hari', 'minggu', 'bulan', 'tahun', 'hari@1', 'minggu@1', 'tahun@1'].forEach(function (r) { var X = aman('tren ' + r, function () { return dbTren(r, kini); }); out.tren[r] = X ? [X.batang.length, X.bisaMundur, X.batang.filter(function (b) { return b.berjalan; }).length] : null; });
var B = aman('bulan', function () { return dbBulanIni(kini); }); out.peringatanBiaya = B ? B.peringatan.length : null;
var D = aman('susun', function () { return dbTambahan(susunDasbor(kini, 'hari'), kini); });
var Wd = D ? aman('wg', function () { return wgSusun(['peringatanUang', 'modalDiam', 'pesananPemasok', 'notaTembus'].map(function (x) { return { id: x }; }), D); }) : null;
out.wgGalat = Wd ? Wd.filter(function (w) { return w.nilai === 'gagal dihitung'; }).map(function (w) { return w.id + ': ' + w.ket; }) : 'gagal';
var C = aman('cetak', function () { return dbCetak(kini, null, null); }); out.cetak = C ? C.kertas.teks : null;
print(JSON.stringify(out));
})();
"""


def bundel_js(teks):   # pola uji_gudang_label_patuh (satu lingkup + nama susunBon pemasok)
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    js = uji_gudang_label_patuh.uji_kunci_periode.satu_lingkup(js)
    B = uji_gudang_label_patuh.BON_PEMASOK_LAMA
    if js.count(B) == 1: js = js.replace(B, B.replace('susunBon(', 'bpSusunBon('))
    return js


def jalan(teks):
    jam = "var __KINI = new Date('2026-11-18T14:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    r, out = uji_dasbor_sensus.jsc(jam + bundel_js(teks) + '\nvar KOTAK0 = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar GK = ' + json.dumps(KOTAK) + ';\nvar ATUR = ' + json.dumps(ATUR) + ';\n' + SKENARIO)
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], list(h['gagal'])


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    # paket ini TANPA pintu tulis baru: peringatan-logika & bagian P3 dasbor-logika tidak menyusun dokumen; logika tanpa DOM
    for k, dari, sampai in (('pw', '', None), ('dl', '// ==================== P3 · Dasbor & peringatan', None), ('gd', 'export function gdPesananPemasok(', '/** Sumber pengingat jenis')):
        t = src[k]; i = t.find(dari) if dari else 0; j = t.find(sampai, i) if sampai and i >= 0 else len(t)
        if i < 0 or j < 0: g.append(k + ': bagian P3 tidak ketemu'); continue
        if 'koleksi:' in t[i:j] or 'dokumen:' in t[i:j]: g.append(k + ': bagian P3 menulis dokumen (paket ini tanpa pintu tulis baru)')
    for k in ('pw', 'kl', 'gd', 'dl', 'wg'):
        if 'document.' in src[k] or 'tulisDokumen' in src[k]: g.append(k + ': modul logika menyentuh DOM / menulis langsung')
    if "from './sistem-logika.js'" in src['pw']: g.append('peringatan-logika mengimpor sistem-logika (pola lokal.peringatan: tanpa impor balik)')
    for k in ('dasbor', 'kisi', 'pw', 'kl', 'gd', 'dl', 'wg', 'ss', 'sl'):
        for n, baris in enumerate(src[k].split('\n')):
            ekor = uji_sisa_sensus.komentar_ekor(baris)
            if ekor and re.search(r"\b[a-zA-Z]\w*: (opsi\.|\(|async |\[|\{|'|`)|;\s*(const|let|return|if|export)\b|\)\s*=>", ekor): g.append(k + ':' + str(n + 1) + ': komentar // menelan kode → ' + ekor.strip()[:90])
    i = src['baca'].find('Paket P3')
    j = src['baca'].find('\n## ', i + 1) if i >= 0 else -1; j = j if j > 0 else i + 6000   # paket P6: bagian sesudahnya (P6, rules v25) bukan bagian P3
    if i >= 0 and ('rules v2' in src['baca'][i:j] or 'firestore.rules' in src['baca'][i:j]): g.append('BACA-DULU menyebut rules untuk paket ini (paket ini tanpa rules)')
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
            beres = (not h['galat'] and h['modalDiam'] and h['modalDiam']['menutup'] and h['modalDiam']['samaA121'] and not h['wgGalat'] and not h['tugasGalat']
                     and h['peringatan'] is not None and not h['peringatan']['tidakTerbaca'] and all(v is not None for v in h['tren'].values()))
            # angka RUPIAH toko TIDAK dicetak (repo publik) — hanya keadaan, jumlah, kg & hari
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: lapisan umur tidak menutup ke nilai stok, peringatan / tugas / widget galat')
    sys.exit(1 if g or gs else 0)
