#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_laba_pelanggan.py — B5 LAPORAN PER PELANGGAN (keputusan owner 18 Nov 2026). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  · laba kotor per TINGKAT harga (Warung · Catering) + Eceran, pelanggan USAHA dirinci per orang, pembeli eceran (bernama / tanpa nama) digabung;
  · nota dibuat lewat jalur Jual yang asli (susunNotaDokumen: harga tingkat, ongkir antar, potongan nota, faktur bon) — modal = HPP tersimpan di nota;
  · retur ikut nama di NOTA ASALNYA; ongkir yang ditagih masuk laba kotor pelanggan itu (HPP 0) & ditulis terpisah;
  · "dilepas dari eceran" = potongan tingkat + nego + potongan nota (keterangan, bukan pengurang kedua);
  · TEMPO dalam hari: bayar yang ditujukan (faktur / pesanan) menutup barisnya dulu, sisanya bon tertua dulu; hapus buku bukan "dibayar"; faktur lewat tempo;
  · PENJAGA: Σ kelompok = laba kotor, omzet tanpa modal, jumlah baris & kg Laporan — untuk 1 bulan & 3 bulan; tingkat yang dicabut tetap terbaca;
  · Dasbor (dbB2b) = angka yang sama apa adanya; layar Laporan & Dasbor memasang kartunya (statis).

    python3 alat-uji/uji_laba_pelanggan.py            → N lulus · 0 gagal
    python3 alat-uji/uji_laba_pelanggan.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_antar, uji_jual_baru, uji_ringkasan_baru, uji_kunci_periode  # noqa: E402
JSC = uji_antar.JSC
PG = 'baru/js/layar/laba-pelanggan-logika.js'; DL = 'baru/js/layar/dasbor-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_antar.MODUL + uji_ringkasan_baru.modul_dasbor() + ['baru/js/layar/pesanan-logika.js', PG])))
SUMBER = {'laporan': 'baru/js/layar/laporan.js', 'dasbor': 'baru/js/layar/dasbor.js', 'dasborL': DL, 'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml',
          'bundel': 'alat-uji/bundel_baru.py', 'cssL': 'baru/css/laporan.css', 'cssR': 'baru/css/ringkasan.css', 'pg': PG}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
var J = function (x) { return JSON.stringify(x); };
var nId = 70000; var W = { tanggal: '2026-11-02', jam: '09:00', kini: '2026-11-02T02:00:00.000Z', kodePerangkat: 'TES', idUnik: function () { nId += 1; return nId; } };
var KINI = new Date('2026-11-18T10:00:00+07:00');
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
setelSumber('cadangan', 'kotak pasir');
var SET = { id: 'hargaTingkat', tingkat: [{ id: 'warung', nama: 'Warung', potKg: 200 }, { id: 'catering', nama: 'Catering', potKg: 0 }], barang: {}, orang: { 'bu suti': 'warung', 'pak contoh': 'catering' }, khusus: [] };
var ATUR = { id: 'pelanggan', tarifOngkir: 15000, pengantarAntar: ['Ben'], kendaraanAntar: ['Motor'] };
pasok('aturanToko', [JSON.parse(J(SET)), ATUR]);
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'warung depan pasar', tempoHari: 7, alamat: 'Jl. Contoh 1', batasKredit: 5000000 },
  { id: 'pak contoh', nama: 'Pak Contoh', catatan: 'katering kantor', tempoHari: 14, alamat: 'Jl. Contoh 2', batasKredit: 5000000 },
  { id: 'mbak contoh', nama: 'Mbak Contoh', catatan: 'rumah dekat masjid' }]);
var s = keadaanAwal(); s.sekarang = KINI;
function terap(p) { s = Object.assign({}, s, p); sinkronKeranjang(s); return p; }
function chip(jalur, kunci, berat) { var r = susunRak(s); return r[jalur].find(function (c) { return c.kunci === kunci && (!berat || c.berat === berat); }); }
function mulai() { s = keadaanAwal(); s.sekarang = KINI; sinkronKeranjang(s); }
function isi(jalur, kunci, n, berat) { terap(ketukChip(s, chip(jalur, kunci, berat))); terap({ ketik: String(n) }); terap(masukkan(s)); }
var dok = function (N, kol) { return N.dokumen.filter(function (x) { return x.koleksi === kol; }).map(function (x) { return x.data; }); };
function catat(tgl, jam) { W.tanggal = tgl; W.jam = jam || '09:00'; W.kini = tgl + 'T02:00:00.000Z'; var t = alasanTolak(s); if (t) return { tolak: t }; var N = susunNotaDokumen(s, W); terapkanKeCache(N.dokumen); return N; }
var PJ = function (N) { return dok(N, 'penjualan'); };
var laba = function (rows) { return rows.reduce(function (a, p) { return a + (hppTercatat(p) ? (p.hargaTotal || 0) - (p.hppTotalSaatJual || 0) : 0); }, 0); };

// ---- nota contoh lewat jalur Jual yang asli
// pembeli dipilih SESUDAH barang masuk keranjang (gantiPelanggan membangun ulang harga ke tingkatnya — jalur layar Jual)
mulai(); isi('karung', 'Angsa', 2, 50); terap(gantiPelanggan(s, 'Bu Suti')); terap({ cara: 'Kredit', antar: Object.assign(ajDrafBaru('Bu Suti'), { ongkir: '12000' }) });
var N1 = catat('2026-11-02', '09:00');
mulai(); isi('kemasan', 'Kembang|5', 2); terap(gantiPelanggan(s, 'Bu Suti')); terap(uangPas(s)); var N2 = catat('2026-11-10', '10:00');
mulai(); isi('kemasan', 'Kembang|5', 4); terap(gantiPelanggan(s, 'Pak Contoh')); terap({ cara: 'Kredit' }); var N3 = catat('2026-10-20', '11:00');
mulai(); isi('karung', 'Angsa', 1, 50); terap(gantiPelanggan(s, 'Mbak Contoh')); terap({ potongan: 5000 }); terap(uangPas(s)); var N4 = catat('2026-11-12', '12:00');
mulai(); isi('literan', 'Angsa', 3); terap(uangPas(s)); var N5 = catat('2026-11-12', '13:00');
ok('nota contoh tercatat (5 nota lewat susunNotaDokumen)', [N1, N2, N3, N4, N5].every(function (N) { return N && !N.tolak; }), J([N1, N2, N3, N4, N5].map(function (N) { return N && N.tolak; })));
var R1 = PJ(N1), R2 = PJ(N2), R3 = PJ(N3), R4 = PJ(N4), R5 = PJ(N5);
ok('nota Bu Suti: bon bertingkat Warung + ongkir 12.000 + faktur; Pak Contoh: bon Catering', R1[0].caraBayar === 'Kredit' && R1[0].tingkatId === 'warung' && R1.some(function (p) { return p.ongkirAntar === 12000; }) && !!R1[0].noFaktur
  && R3[0].caraBayar === 'Kredit' && R3[0].tingkatId === 'catering' && !!R3[0].noFaktur && R3[0].jatuhTempo === '2026-11-03', J([R1[0], R3[0]]));
// Bu Suti melunasi bon 2 Nov pada 6 Nov (4 hari); retur rusak 1 kemasan nota 10 Nov, uang dikembalikan 50.000 (dokumen retur tanpa nama — tunai)
var tot1 = R1.reduce(function (a, p) { return a + p.hargaTotal; }, 0);
terapkanKeCache([{ koleksi: 'piutangMutasi', data: { id: 'byr-suti', tanggal: '2026-11-06', jam: '15:00', namaPelanggan: 'Bu Suti', tipe: 'bayar', nominal: tot1, caraBayar: 'Tunai' } },
  { koleksi: 'retur', data: { id: 'rt-suti', tanggal: '2026-11-15', jam: '10:00', notaAsalId: String(R2[0].id), kondisi: 'rusak', nominalRefund: 50000, totalKg: 5, jenisAsal: 'kemasan', namaProduk: 'Kembang', jumlahDikembalikan: 1 } }]);

// ---- A · November (1 bulan)
var G = pelangganBulan('2026-11', 1, KINI);
var t = function (id) { return G.tingkat.find(function (x) { return x.id === id; }); }; var o = function (G0, k) { return G0.orang.find(function (x) { return x.kunci === k; }); };
ok('A: menutup ke laba kotor, omzet tanpa modal, baris & kg Laporan November', G.menutup === true && G.identitas.length === 4, G.kalimat);
ok('A: tingkat = Warung · Catering · Eceran (urutan setelan owner, Eceran paling bawah)', J(G.tingkat.map(function (x) { return x.id; })) === '["warung","catering","eceran"]', J(G.tingkat.map(function (x) { return x.id; })));
var suti = o(G, 'bu suti');
ok('A: laba kotor Bu Suti = Σ (harga − modal) dua notanya (termasuk ongkir) − retur 50.000', suti && Math.abs(suti.labaKotor - (laba(R1) + laba(R2) - 50000)) < 0.5, J(suti && [suti.labaKotor, laba(R1) + laba(R2) - 50000]));
ok('A: ongkir Bu Suti 12.000 di 1 nota, nota 2, retur 1', suti.ongkir === 12000 && suti.nOngkir === 1 && suti.nNota === 2 && suti.nRetur === 1 && suti.returUang === 50000, J([suti.ongkir, suti.nOngkir, suti.nNota, suti.nRetur, suti.returUang]));
ok('A: dilepas tingkat Bu Suti = 200/kg × (100 kg karung + 10 kg kemasan) = 22.000; nego 0; potongan nota 0', suti.dilepas.tingkat === 22000 && suti.dilepas.nego === 0 && suti.dilepas.nota === 0, J(suti.dilepas));
ok('A: tempo Bu Suti: 1 baris bon periode ini lunas 4 hari sesudah nota; sisa 0', suti.tempo.nLunas === 1 && Math.abs(suti.tempo.rata - 4) < 1e-9 && suti.tempo.sisa === 0 && pgHariTeks(suti.tempo.rata) === '±4 hari', J(suti.tempo));
var pak = o(G, 'pak contoh');
ok('A: Pak Contoh tidak belanja November tapi masih punya bon lewat tempo → tetap tampil (tanpa jualan), laba null', pak && pak.tanpaJualan === true && pak.labaKotor === null && pak.keadaan === 'kosong', J(pak && [pak.tanpaJualan, pak.labaKotor]));
var tot3 = R3.reduce(function (a, p) { return a + p.hargaTotal; }, 0);
ok('A: Pak Contoh: faktur jatuh tempo 3 Nov lewat 15 hari, sisa = notanya, bon tertua 29 hari', pak.lewat.n === 1 && pak.lewat.hariMaks === 15 && Math.abs(pak.lewat.rp - tot3) < 0.5 && pak.tempo.sisa === tot3 && pak.tempo.umurTertua === 29, J([pak.lewat, pak.tempo]));
var ec = t('eceran');
ok('A: Eceran = Mbak Contoh (1 nama) + 1 nota literan tanpa nama; potongan nota 5.000 masuk dilepas', ec.nOrang === 1 && ec.nTanpaNama === 1 && ec.dilepas.nota === 5000 && Math.abs(ec.labaKotor - (laba(R4) + laba(R5))) < 0.5, J([ec.nOrang, ec.nTanpaNama, ec.dilepas, ec.labaKotor]));
ok('A: Σ laba kotor tingkat = laba kotor Laporan; Σ porsi = 100%', Math.abs(G.tingkat.reduce(function (a, x) { return a + (x.labaKotor || 0); }, 0) - G.L.margin) < 0.5
  && Math.abs(G.tingkat.reduce(function (a, x) { return a + (x.porsiLaba || 0); }, 0) - 100) < 1e-6, J(G.tingkat.map(function (x) { return [x.id, x.labaKotor, x.porsiLaba]; })));
ok('A: B2B = pelanggan usaha (Bu Suti) — porsi laba = laba Warung ÷ Σ', G.usaha && G.b2b.nOrang === 1 && Math.abs(G.b2b.porsiLaba - t('warung').labaKotor / G.L.margin * 100) < 1e-9, J(G.b2b));
ok('A: faktur lewat tempo se-toko = 1', G.lewat.n === 1 && Math.abs(G.lewat.rp - tot3) < 0.5, J(G.lewat));
ok('A: keterangan layar menyebut ongkir, dilepas & tempo', /ongkir ditagih Rp12\.000/.test(pgKet(suti)) && /potongan tingkat Rp22\.000/.test(pgKet(suti)) && /LEWAT TEMPO/.test(pgKetTempo(pak)) && /dibayar rata-rata ±4 hari \(1 nota lunas\)/.test(pgKetTempo(suti)) && pgDilepasTeks({ tingkat: 0, nego: -3000, nota: 0 }) === 'dibanding eceran: nego naik Rp3.000', pgKet(suti) + ' | ' + pgKetTempo(pak));

// ---- B · 3 bulan (Sep – Nov): nota Pak Contoh Oktober & nota contoh September ikut
var G3 = pelangganBulan('2026-11', 3, KINI); var pak3 = o(G3, 'pak contoh');
ok('B: 3 bulan menutup ke Laporan Sep–Nov', G3.menutup === true && G3.rentang.dari === '2026-09-01' && G3.rentang.sampai === '2026-11-30' && G3.nama === 'Sep 26 – Nov 26', G3.kalimat + ' ' + G3.nama);
ok('B: Pak Contoh 3 bulan: belanja Oktober, laba = notanya, bon periode ini belum lunas', pak3 && !pak3.tanpaJualan && Math.abs(pak3.labaKotor - laba(R3)) < 0.5 && pak3.tempo.nTerbuka === 1 && pak3.tempo.rata === null, J(pak3 && [pak3.labaKotor, pak3.tempo]));
var suti3 = o(G3, 'bu suti');
ok('B: Bu Suti 3 bulan ikut nota September (dulu belum bertingkat — tetap Warung karena tingkat sekarang)', suti3 && suti3.nNota === 4 && suti3.tingkatId === 'warung', J(suti3 && [suti3.nNota, suti3.tingkatId]));
ok('B: rentang tidak sah → 1 bulan', pgRentang('2026-11', 7).n === 1 && pgRentang('2026-11', '12').bulan.length === 12 && pgRentang('2026-01', 3).bulan[0] === '2025-11');

// ---- C · tingkat dicabut: Pak Contoh tidak lagi bertingkat, notanya Oktober tetap terbaca Catering
pasok('aturanToko', [Object.assign(JSON.parse(J(SET)), { orang: { 'bu suti': 'warung' } }), ATUR]);
var G3c = pelangganBulan('2026-11', 3, KINI); var pakC = o(G3c, 'pak contoh');
ok('C: tingkat dicabut → tetap pelanggan usaha Catering dari notanya (tingkatDulu), tetap menutup', pakC && pakC.tingkatId === 'catering' && pakC.tingkatDulu === true && G3c.menutup === true, J(pakC && [pakC.tingkatId, pakC.tingkatDulu]));
var G1c = pelangganBulan('2026-11', 1, KINI);
ok('C: November (tanpa nota Pak Contoh) → Pak Contoh tidak lagi pelanggan usaha; bonnya ikut Eceran', !o(G1c, 'pak contoh') && G1c.eceran.tempo.sisa >= tot3 && G1c.eceran.lewat.n === 1, J([G1c.orang.map(function (x) { return x.kunci; }), G1c.eceran.tempo, G1c.eceran.lewat]));
pasok('aturanToko', [JSON.parse(J(SET)), ATUR]);

// ---- D · dilepas & tempo (satuan)
var D1 = pgDilepas({ hargaTotal: 685000 * 2 + 15000, ongkirAntar: 15000, hargaAsliSatuan: 690000, negoSelisih: -5000, hargaEceranSatuan: 700000 });
ok('D: dilepas: 2 karung eceran 700.000, tingkat 690.000, nego −5.000, ongkir 15.000 → tingkat 20.000, nego 10.000', Math.round(D1.tingkat) === 20000 && Math.round(D1.nego) === 10000 && D1.nota === 0, J(D1));
var D2 = pgDilepas({ hargaTotal: 140000, potonganTransaksi: 4000, pembulatan: 0, hargaAsliSatuan: 72000 });
ok('D: dilepas tanpa tingkat: potongan nota 4.000 saja (tanpa harga eceran tercatat = tingkat 0)', D2.tingkat === 0 && Math.round(D2.nego) === 0 && D2.nota === 4000, J(D2));
var Pm = { bayar: { b2: { untukFaktur: ['F-2'] } }, baris: { u2: 'F-2' }, trx: {}, ps: {}, nota: {} };
var d1 = { sisa: 0, mutasi: [{ jenis: 'jual', tanggal: '2026-11-01', jam: '08:00', nominal: 100000, idTrx: 'u1' }, { jenis: 'jual', tanggal: '2026-11-03', jam: '08:00', nominal: 50000, idTrx: 'u2' },
  { jenis: 'bayar', tanggal: '2026-11-05', jam: '08:00', nominal: 50000, idMutasi: 'b2' }, { jenis: 'bayar', tanggal: '2026-11-09', jam: '08:00', nominal: 100000, idMutasi: 'b3' }] };
var T1 = pgTempo(d1, '2026-11-01', '2026-11-30', '2026-11-18', Pm);
ok('D: bayar ke faktur F-2 menutup F-2 dulu (2 hari), bon tertua lunas 9 Nov (8 hari) → rata (8×100 + 2×50)/150 = 6', T1.nLunas === 2 && Math.abs(T1.rata - 6) < 1e-9, J(T1));
var d2 = { sisa: 0, mutasi: [{ jenis: 'bayar', tanggal: '2026-11-01', jam: '08:00', nominal: 30000, idMutasi: 'dp' }, { jenis: 'jual', tanggal: '2026-11-02', jam: '08:00', nominal: 100000, idTrx: 'u3' },
  { jenis: 'bayar', tanggal: '2026-11-04', jam: '08:00', nominal: 70000, idMutasi: 'b4' }, { jenis: 'jual', tanggal: '2026-11-05', jam: '08:00', nominal: 40000, idTrx: 'u4' },
  { jenis: 'hapusBuku', tanggal: '2026-11-08', jam: '08:00', nominal: 40000, idMutasi: 'h1' }] };
var T2 = pgTempo(d2, '2026-11-01', '2026-11-30', '2026-11-18', Pm);
ok('D: uang muka sebelum nota menutup saat nota lahir; lunas 4 Nov = 2 hari; hapus buku BUKAN dibayar', T2.nLunas === 1 && Math.abs(T2.rata - 2) < 1e-9 && T2.nTerbuka === 0, J(T2));
var d3 = { sisa: 0, mutasi: [{ jenis: 'jual', tanggal: '2026-11-02', jam: '09:00', nominal: 100000, idTrx: 'u5' }, { jenis: 'bayar', tanggal: '2026-11-02', jam: '09:00', nominal: 100000, idMutasi: 'b5' }] };
var T3 = pgTempo(d3, '2026-11-01', '2026-11-30', '2026-11-18', Pm);
ok('D: bayar saat beli = 0 hari ("hari itu juga")', T3.nLunas === 1 && T3.rata === 0 && pgHariTeks(T3.rata) === 'hari itu juga' && T3.umurTertua === null, J(T3));
var d4 = { sisa: 30000, mutasi: [{ jenis: 'jual', tanggal: '2026-10-10', jam: '09:00', nominal: 30000, idTrx: 'u6' }].concat(d3.mutasi) };
var T4 = pgTempo(d4, '2026-11-01', '2026-11-30', '2026-11-18', Pm);
ok('D: bayar tanpa alamat menutup bon TERTUA dulu (= mesin): bon Oktober lunas, nota November sisa 30.000 terbuka 16 hari', T4.nLunas === 0 && T4.nTerbuka === 1 && T4.umurTertua === 16 && T4.sisa === 30000, J(T4));

// ---- E · Dasbor = angka yang sama
var DB = dbB2b(KINI);
ok('E: Dasbor pelanggan usaha = Per pelanggan bulan ini apa adanya (porsi laba, teratas, lewat tempo)', !DB.galat && Math.abs(DB.porsiLaba - G.b2b.porsiLaba) < 1e-9 && DB.teratas[0].nama === 'Bu Suti' && DB.lewat.n === 1 && DB.menutup === true && DB.tujuan.keluarga === 'laba', J(DB));
var SD = susunDasbor(KINI, 'hari');
ok('E: susunDasbor memuat kelompok b2b (dan dipertahankan saat ganti rentang)', SD.b2b && !SD.b2b.galat && susunDasbor(KINI, 'bulan', SD).b2b === SD.b2b, J(SD.b2b && SD.b2b.galat));

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('Laporan › Laba memasang kartu Per pelanggan', 'laporan', ['import * as PG from \'./laba-pelanggan-logika.js\';', 'kartuPelanggan(PG.pelangganBulan(key, s.pgN, kini()), s)', 'data-aksi="pgRentang"', 'data-aksi="pgSemua"',
                                                              '${pelanggan}${aman}', 'h`${pelanggan}${susut}${rugi}${tt}`', 'pgN: 1, pgSemua: false']),
    ('Dasbor memasang kartu Pelanggan usaha', 'dasbor', ['kartuB2b(D.b2b)', 'function kartuB2b(Q)', 'data-k="db-b2b"']),
    ('dasbor-logika menyusun kelompok b2b', 'dasborL', ["import { pelangganBulan, pgHariTeks } from './laba-pelanggan-logika.js';", "b2b: aman('pelanggan usaha', () => dbB2b(kini))", 'b2b: lama.b2b']),
    ('modul dipramuat & diuji CI', 'index', ['<link rel="modulepreload" href="js/layar/laba-pelanggan-logika.js">']),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_laba_pelanggan.py']),
    ('bundel uji melengkapi modul untuk Dasbor', 'bundel', ["PG_MODUL = 'baru/js/layar/laba-pelanggan-logika.js'", "PG_PEMAKAI = ('dasbor-logika.js',)"]),
    ('gaya bergerak (pita tumbuh) + hormat reduced motion', 'cssL', ['.layar-laporan .lp-pg-porsi i {', 'animation: lpPgTumbuh', '.layar-laporan .lp-pg-porsi i { animation: none; transition: none; }']),
    ('gaya Dasbor pita porsi', 'cssR', ['.layar-ringkasan .db-pita-b2b i {', 'animation: dbTumbuhX']),
    ('modul tanpa DOM & tanpa menulis', 'pg', []),
]

RUSAK = [
    ('ongkir tidak masuk laba kotor pelanggan', PG, "(marginBarang || 0) + g.ongkirHitung;", "(marginBarang || 0);"),
    ('retur ikut nama di dokumen retur saja', PG, "kunciPelanggan(pa ? pa.namaPelanggan : r.namaPelanggan)", "kunciPelanggan(r.namaPelanggan)"),
    ('potongan tingkat terbalik', PG, "(ec - asli) * jml", "(asli - ec) * jml"),
    ('tempo mengabaikan bayar yang ditujukan', PG, "      tuju.forEach((u) => { if (sisa > 0 && u.sisa > 0.5) sisa -= tutup(u, sisa, e); });\n", ""),
    ('hapus buku dihitung dibayar', PG, "if (!dlm || u.hapus || !(u.nominal > 0)) return;", "if (!dlm || !(u.nominal > 0)) return;"),
    ('tingkat dicabut jatuh ke eceran', PG, "    if (!r) return null; const t2 = htTingkat(A, r.tingkatId);", "    return null; const t2 = htTingkat(A, r.tingkatId);"),
    ('pelanggan usaha berbon tanpa jualan hilang', PG, "if (htTingkat(A, A.orang[k]) && ((piutang[k] && piutang[k].sisa > 0.5) || lewatOrang[k])) kunciUsaha[k] = 1;", ""),
    ('baris tanpa nama hilang dari Eceran', PG, ".concat([tanpaNama])", ""),
    ('Dasbor memakai porsi omzet', DL, "porsiLaba: G.b2b ? G.b2b.porsiLaba : null", "porsiLaba: G.b2b ? G.b2b.porsiOmzet : null"),
]
RUSAK_STATIS = [
    ('Laporan tanpa kartu Per pelanggan', 'laporan', '${pelanggan}${aman}', '${aman}'),
    ('Dasbor tanpa kartu B2B', 'dasbor', 'kartuB2b(D.b2b)', "''"),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_laba_pelanggan.py', 'true'),
]
BON_PEMASOK_LAMA = uji_ringkasan_baru.BON_PEMASOK_LAMA


def jalan(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    js = uji_kunci_periode.satu_lingkup(js)   # teksMargin stok-hpp vs harga-logika
    if js.count(BON_PEMASOK_LAMA) == 1: js = js.replace(BON_PEMASOK_LAMA, BON_PEMASOK_LAMA.replace('susunBon(', 'bpSusunBon('))   # susunBon pemasok vs bon pelanggan
    jam = "var __KINI = new Date('2026-11-18T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(jam + js + '\nvar KOTAK = ' + json.dumps(uji_jual_baru.KOTAK) + ';\n' + SKENARIO); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], h['gagal']


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    pg = src['pg']
    if 'document.' in pg or 'tulisDokumen' in pg or 'dokumen: [' in pg: g.append('laba-pelanggan-logika menyentuh DOM / menulis dokumen — modul ini baca saja')
    return len(STATIS) - len(g), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


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
            S = dict(src); S[berkas] = S[berkas].replace(a, b); l, g = statis(S)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = jalan(teks); ls, gs = statis(src)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    sys.exit(1 if g or gs else 0)
