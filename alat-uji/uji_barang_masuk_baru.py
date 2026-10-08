#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_barang_masuk_baru.py — paket brief 9 Okt (butir 6 & 7): TIMBANG & MUTU SAAT TERIMA di lembar Stok › Barang masuk.
  · Keputusan owner: isian baru OPSIONAL — boleh kosong, catatan kedatangan tetap bisa disimpan.
  · Butir 6 SELISIH TIMBANG: per baris merek "berat timbang (kg)" seluruh baris; selisih = timbang − kg nota (jumlahKarung × beratKarung = totalKg), kg & %.
    Kosong = "belum ditimbang" (BUKAN selisih 0). totalKg, stok, modal, HPP, dan bon TIDAK berubah karena timbang — catatan pemeriksaan saja.
  · Butir 7 CEK MUTU: kadar air (%), kutu (ada/tidak), bau (normal/apek/lain), butir patah (%). Ambang di Atur Barang masuk (aturanToko/catatStok):
    kadar air maks 14 %, butir patah maks 25 % = angka bawaan (perkiraan). Lewat ambang / ada kutu / bau tidak normal → AWAS; ambang diubah → tanda ikut.
  · Rekap per pemasok (rekapTimbangMutu): ditimbang dari berapa kedatangan, selisih kg, rata-rata % (tertimbang kg), nilai kg kurang (perkiraan, tidak dibukukan).
  · Koreksi kedatangan membawa & bisa mengubah isian; kedatangan lama tanpa isian tetap berbentuk lama; koreksi HPP tidak menghapus isian.
KOTAK PASIR (ANGKA CONTOH), jam dikunci 20 Sep 2026 10:00 WIB. Cadangan toko di _privat/ (asap): rekap menutup, isian baru tidak menggeser stok/utang/laba,
kolom baris kedatangan yang ditulis = kolom yang dikenal cadangan + lima kolom baru.

    python3 alat-uji/uji_barang_masuk_baru.py            → N lulus · 0 gagal
    python3 alat-uji/uji_barang_masuk_baru.py --kontrol  → logika / layar yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import uji_wadah_bernama  # noqa: E402
import uji_wadah_stok_sendiri as UW  # noqa: E402

brs = uji_wadah_bernama.brs
KOTAK = {
  # b1 = kedatangan LAMA tanpa isian timbang/mutu (PEMASOK A); b2 = PEMASOK B; b3 = kedatangan lama TANPA nama pemasok (kelompok sendiri, bukan dibuang)
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-09-10', 'jam': '08:00', 'pemasok': 'PEMASOK A', 'caraBayar': 'utang', 'biayaBongkar': 0, 'merkList': [brs(1, 'Angsa', 4, 13000), brs(2, 'Perahu', 2, 14000)]},
                 {'id': 'b2', 'tanggal': '2026-09-12', 'jam': '08:00', 'pemasok': 'PEMASOK B', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [brs(1, 'Merpati', 2, 15000)]},
                 {'id': 'b3', 'tanggal': '2026-09-13', 'jam': '08:00', 'pemasok': '', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [brs(1, 'Merpati', 1, 15000)]}],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var nId = 9000; var W = { tanggal: '2026-09-20', jam: '10:00', kini: '2026-09-20T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var DASAR = 'beratKarung,hargaPerKg,id,jumlahKarung,merk,satuan,subtotalHarga,totalKg';
var kunci = function (r) { return Object.keys(r).sort().join(); };
var tanpaTM = function (rows) { return rows.map(function (r) { var o = {}; Object.keys(r).forEach(function (k) { if (TM_KOLOM.indexOf(k) < 0) o[k] = r[k]; }); return o; }); };
var uang = function () { var st = hitungStokKarungPerMerk(); var o = {}; Object.keys(st).sort().forEach(function (m) { o[m] = [Math.round(st[m].sisaKg * 1000) / 1000, Math.round(st[m].hppTerakhirPerKg * 1000) / 1000]; });
  return J({ stok: o, utang: hitungUtangPemasok().map(function (p) { return [p.pemasok, Math.round(p.totalUtang)]; }), laba: hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih }); };

// ---- ambang bawaan
var A0 = aturCatat();
ok('ambang mutu bawaan: kadar air maks 14 %, butir patah maks 25 % — keduanya ditandai angka bawaan (belum disimpan owner)', A0.kadarAirMaks === 14 && A0.patahMaks === 25 && A0.mutuBawaan.kadarAirMaks === true && A0.mutuBawaan.patahMaks === true, J(A0));

// ---- draf: Angsa ditimbang KURANG + kadar air 15 (> 14); Perahu ditimbang LEBIH + kutu ada + bau apek + patah 20 (< 25); Merpati KOSONG
var draf = function (isi) { return { id: null, tanggal: '2026-09-20', pemasok: 'PEMASOK A', caraBayar: 'utang', bongkar: '60.000', alasan: '', baris: [
  Object.assign({ merk: 'Angsa', jumlahKarung: '40', beratKarung: 50, hargaPerKg: '13.200' }, isi[0] || {}), Object.assign({ merk: 'Perahu', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '14.000' }, isi[1] || {}),
  Object.assign({ merk: 'Merpati', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '15.000' }, isi[2] || {})] }; };
var ISI = [{ timbangKg: '1.987,5', kadarAir: '15', kutu: 'tidak', bau: 'normal' }, { timbangKg: '505', kutu: 'ada', bau: 'apek', butirPatah: '20' }, {}];
var dT = draf(ISI), d0 = draf([{}, {}, {}]); var hT = hitungMasuk(dT), h0 = hitungMasuk(d0);
var cA = hT.sah[0].cek, cP = hT.sah[1].cek, cM = hT.sah[2].cek;
ok('timbang KURANG: Angsa nota 40 × 50 = 2.000 kg, timbang "1.987,5" → selisih −12,5 kg (−0,6 %), kurang ≈ 12,5 × 13.200 = Rp165.000 (perkiraan)',
  hT.sah[0].totalKg === 2000 && cA.timbangKg === 1987.5 && cA.selisihKg === -12.5 && cA.selisihPersen === -0.6 && cA.kgKurang === 12.5 && cA.kgLebih === 0 && cA.nilaiKurang === 165000 && /KURANG 12,5 kg \(−0,6 %\)/.test(cA.timbangTeks), J(cA));
ok('timbang LEBIH: Perahu nota 500 kg, timbang 505 → selisih +5 kg (+1 %), tidak ada nilai kurang', cP.timbangKg === 505 && cP.selisihKg === 5 && cP.selisihPersen === 1 && cP.kgLebih === 5 && cP.nilaiKurang === 0 && /lebih 5 kg \(\+1 %\)/.test(cP.timbangTeks), J(cP));
ok('KOSONG = belum ditimbang & tidak dicek — BUKAN selisih 0 (selisih null, persen null), tidak ada kolom yang akan ditulis', cM.ada === false && cM.timbangKg === null && cM.selisihKg === null && cM.selisihPersen === null && cM.timbangTeks === 'belum ditimbang' && cM.dicek === false && cM.mutuTeks === 'tidak dicek' && J(cM.kolom) === '{}', J(cM));
ok('mutu: Angsa kadar air 15 % > maks 14 % → AWAS; Perahu ada kutu + bau apek → AWAS (butir patah 20 % ≤ 25 % bukan awas); Merpati tidak dicek → tanpa tanda',
  J(cA.awas) === J(['kadar air 15 % > maks 14 %']) && J(cP.awas) === J(['ada kutu', 'bau apek']) && cM.awas.length === 0 && /butir patah tidak dicek/.test(cA.mutuTeks) && /butir patah 20 %/.test(cP.mutuTeks), J([cA.awas, cP.awas, cA.mutuTeks, cP.mutuTeks]));
ok('ringkasan draf: 2 dari 3 baris ditimbang, selisih −7,5 kg dari 2.500 kg nota (−0,3 %), kurang ≈ Rp165.000, mutu dicek 2 baris, 2 baris AWAS',
  J(hT.timbang) === J({ baris: 3, ditimbang: 2, kgNota: 2500, selisihKg: -7.5, nilaiKurang: 165000, dicek: 2, awas: 2, persen: -0.3 }), J(hT.timbang));
ok('TIMBANG TIDAK MENGUBAH ANGKA BUKU: kg, nilai beras, total, dan tiap baris (totalKg, subtotal, alokasi bongkar, HPP/kg) sama persis dengan draf tanpa isian',
  hT.kg === h0.kg && hT.kg === 3000 && hT.nilaiBeras === h0.nilaiBeras && hT.total === h0.total && hT.sah.every(function (b, i) { var x = h0.sah[i]; return b.totalKg === x.totalKg && b.subtotalHarga === x.subtotalHarga && b.alokasiBongkar === x.alokasiBongkar && b.hppPerKg === x.hppPerKg; }),
  J([hT.kg, h0.kg, hT.sah.map(function (b) { return [b.totalKg, b.hppPerKg]; }), h0.sah.map(function (b) { return [b.totalKg, b.hppPerKg]; })]));

// ---- dokumen: kolom baru hanya yang diisi; baris kosong = bentuk lama persis
var ST = susunSimpanMasuk(dT, W, true), S0 = susunSimpanMasuk(d0, W, true); var mT = ST.dokumen ? ST.dokumen[0].data.merkList : [], m0 = S0.dokumen ? S0.dokumen[0].data.merkList : [];
ok('simpan SAH (isian opsional tidak menghalangi): baris Angsa = kolom lama + timbangKg 1987,5 · kadarAir 15 · kutu tidak · bau normal; Perahu + timbangKg · kutu ada · bau apek · butirPatah 20; Merpati = kolom lama PERSIS',
  !ST.tolak && !S0.tolak && kunci(mT[0]) === 'bau,beratKarung,hargaPerKg,id,jumlahKarung,kadarAir,kutu,merk,satuan,subtotalHarga,timbangKg,totalKg' && mT[0].timbangKg === 1987.5 && mT[0].kadarAir === 15 && mT[0].kutu === 'tidak' && mT[0].bau === 'normal'
  && kunci(mT[1]) === 'bau,beratKarung,butirPatah,hargaPerKg,id,jumlahKarung,kutu,merk,satuan,subtotalHarga,timbangKg,totalKg' && mT[1].butirPatah === 20 && mT[1].kutu === 'ada' && mT[1].bau === 'apek' && kunci(mT[2]) === DASAR
  && m0.every(function (r) { return kunci(r) === DASAR; }), J([ST.tolak, mT, m0]));
ok('dokumen dengan isian = dokumen tanpa isian kalau lima kolom baru dibuang (totalKg 2.000/500/500, subtotal, bongkar, cara bayar sama)', J(tanpaTM(mT)) === J(m0) && ST.dokumen[0].data.biayaBongkar === S0.dokumen[0].data.biayaBongkar && ST.dokumen[0].data.caraBayar === 'utang', J([tanpaTM(mT), m0]));
var uT = denganCacheSementara(ST.dokumen, uang), u0 = denganCacheSementara(S0.dokumen, uang);
ok('stok, modal (HPP/kg), bon pemasok, dan laba bulan itu SAMA PERSIS dengan / tanpa isian timbang & mutu', uT === u0 && uT !== uang(), J([uT, u0]));

// ---- isian yang salah ditolak dengan kalimat; baris yang cuma berisi cek tidak dibuang diam-diam
var tolak = function (i, isi) { var x = [{}, {}, {}]; x[i] = isi; return susunSimpanMasuk(draf(x), W, true).tolak || ''; };
ok('ditolak: kadar air 150 / "abc", butir patah −3, berat timbang 0 / "abc", pilihan kutu & bau asing — kalimat menyebut barisnya',
  /Baris 1 \(Angsa\): kadar air harus angka 0–100 %/.test(tolak(0, { kadarAir: '150' })) && /kadar air harus angka/.test(tolak(0, { kadarAir: 'abc' })) && /butir patah harus angka/.test(tolak(1, { butirPatah: '-3' }))
  && /Baris 3 \(Merpati\): berat timbang harus angka lebih dari 0/.test(tolak(2, { timbangKg: '0' })) && /berat timbang harus/.test(tolak(2, { timbangKg: 'abc' })) && /kutu "mungkin" tidak dikenal/.test(tolak(0, { kutu: 'mungkin' })) && /bau "wangi" tidak dikenal/.test(tolak(0, { bau: 'wangi' })),
  J([tolak(0, { kadarAir: '150' }), tolak(0, { kadarAir: 'abc' }), tolak(1, { butirPatah: '-3' }), tolak(2, { timbangKg: '0' })]));
var dCek = draf([{}, {}, {}]); dCek.baris.push({ merk: '', jumlahKarung: '', beratKarung: 50, hargaPerKg: '', timbangKg: '480' });
var hCek = hitungMasuk(dCek);
ok('baris yang cuma berisi berat timbang (nama kosong) = terisi & ditanya namanya — simpan ditolak, bukan dibuang diam-diam', hCek.baris[3].terisi === true && /nama berasnya belum dipilih/.test(hCek.baris[3].masalah) && /Baris 4/.test(susunSimpanMasuk(dCek, W, true).tolak || ''), J([hCek.baris[3].terisi, hCek.baris[3].masalah]));
var hLama = hitungMasuk({ id: null, tanggal: '2026-09-20', pemasok: 'PEMASOK A', caraBayar: 'tunai', bongkar: '', baris: [{ merk: 'Angsa', jumlahKarung: '60', beratKarung: 50, hargaPerKg: '13.000' }] });
ok('draf lama di perangkat (tanpa kolom isian) tetap dihitung: belum ditimbang, tidak dicek, tanpa masalah', !hLama.bermasalah.length && hLama.sah[0].cek.ada === false && hLama.timbang.ditimbang === 0, J(hLama.sah[0].cek));

// ---- simpan → rekap per pemasok
terapkanKeCache(ST.dokumen); var idT = ST.dokumen[0].data.id;
var R = rekapTimbangMutu(); var pA = R.pemasok.find(function (p) { return p.pemasok === 'PEMASOK A'; }) || {}; var pB = R.pemasok.find(function (p) { return p.pemasok === 'PEMASOK B'; }) || {}; var pX = R.pemasok.find(function (p) { return p.pemasok === '(tanpa nama pemasok)'; }) || {};
ok('rekap PEMASOK A: 2 kedatangan = 0 ditimbang penuh + 1 sebagian (2/3 baris) + 1 belum; 5 baris, 2 ditimbang; selisih −7,5 kg = lebih 5 − kurang 12,5 dari 2.500 kg nota (−0,3 % tertimbang kg); kurang ≈ Rp165.000; mutu dicek 1 kedatangan, 1 kedatangan AWAS (2 baris)',
  pA.kedatangan === 2 && pA.ditimbang === 0 && pA.sebagian === 1 && pA.belumTimbang === 1 && pA.barisSemua === 5 && pA.barisTimbang === 2 && pA.kgNota === 2500 && pA.kgTimbang === 2492.5 && pA.selisihKg === -7.5 && pA.kgKurang === 12.5 && pA.kgLebih === 5
  && pA.persenRata === -0.3 && pA.nilaiKurang === 165000 && pA.dicek === 1 && pA.barisDicek === 2 && pA.kedatanganAwas === 1 && pA.awas.length === 2 && pA.awas[0].merk === 'Angsa' && /kadar air 15 %/.test(pA.awas[0].alasan[0]) && pA.terakhir === '2026-09-20', J(pA));
ok('rekap PEMASOK B: 1 kedatangan belum ditimbang — rata-rata % TIDAK 0 tapi null (belum bisa dihitung), nilai kurang 0, mutu dicek 0', pB.kedatangan === 1 && pB.belumTimbang === 1 && pB.barisTimbang === 0 && pB.persenRata === null && pB.nilaiKurang === 0 && pB.dicek === 0 && pB.awas.length === 0, J(pB));
ok('kedatangan tanpa nama pemasok = kelompok sendiri "(tanpa nama pemasok)" (tidak dibuang, paling bawah); PEMASOK A (ada AWAS) paling atas', pX.kedatangan === 1 && R.pemasok[0].pemasok === 'PEMASOK A' && R.pemasok.length === 3 && R.pemasok[2].pemasok === '(tanpa nama pemasok)', J(R.pemasok.map(function (p) { return p.pemasok; })));
ok('rekap MENUTUP: tiap pemasok ditimbang + sebagian + belum = kedatangan, lebih − kurang = selisih; total = Σ semua pemasok (4 kedatangan, selisih −7,5 kg, −0,3 %)',
  R.pemasok.every(function (p) { return p.ditimbang + p.sebagian + p.belumTimbang === p.kedatangan && Math.round((p.kgLebih - p.kgKurang) * 100) / 100 === p.selisihKg; })
  && ['kedatangan', 'ditimbang', 'sebagian', 'belumTimbang', 'barisSemua', 'barisTimbang', 'nilaiKurang', 'dicek', 'kedatanganAwas'].every(function (k) { return R.total[k] === R.pemasok.reduce(function (a, p) { return a + p[k]; }, 0); })
  && R.total.kedatangan === 4 && R.total.selisihKg === -7.5 && R.total.persenRata === -0.3 && R.lewatBal === 0, J(R.total));
ok('rekap satu pemasok (kelak kartu pemasok Harga & Pemasok): opsi.pemasok → hanya pemasok itu; opsi tanggal menyaring', J(rekapTimbangMutu({ pemasok: 'PEMASOK B' }).pemasok.map(function (p) { return p.pemasok; })) === J(['PEMASOK B'])
  && rekapTimbangMutu({ pemasok: 'PEMASOK A', dari: '2026-09-15' }).pemasok[0].kedatangan === 1 && rekapTimbangMutu({ pemasok: 'PEMASOK A', sampai: '2026-09-15' }).pemasok[0].sebagian === 0);
var DK = daftarKedatangan(10); var kT = DK.find(function (k) { return String(k.id) === String(idT); }), k1 = DK.find(function (k) { return k.id === 'b1'; });
ok('buku kedatangan: kedatangan baru bertanda "ditimbang 2/3 baris −7,5 kg · mutu AWAS"; kedatangan lama tanpa isian tanpa tanda (teks kosong)', kT && kT.cek.teks === 'ditimbang 2/3 baris −7,5 kg · mutu AWAS' && k1 && k1.cek.teks === '' && k1.cek.ditimbang === 0, J([kT && kT.cek.teks, k1 && k1.cek]));

// ---- ambang diubah owner → tanda ikut (kedatangan yang SUDAH tersimpan juga)
ok('atur: kadar air maks 0 / 101 / "abc" dan butir patah −1 / "abc" DITOLAK dengan kalimat', !!susunAturCatat({ kadarAirMaks: '0' }, W).tolak && !!susunAturCatat({ kadarAirMaks: '101' }, W).tolak && !!susunAturCatat({ kadarAirMaks: 'abc' }, W).tolak && !!susunAturCatat({ patahMaks: '-1' }, W).tolak && /Butir patah maksimal/.test(susunAturCatat({ patahMaks: 'abc' }, W).tolak || ''));
var AC = susunAturCatat({ kadarAirMaks: '16', patahMaks: '15' }, W);
ok('atur: dokumen catatStok membawa kadarAirMaks 16 & patahMaks 15 (kolom lama tetap: minimal 60 karung, tempo 21 hari); kabar menyebut ambang mutu', !AC.tolak && AC.dokumen[0].data.id === 'catatStok' && AC.dokumen[0].data.kadarAirMaks === 16 && AC.dokumen[0].data.patahMaks === 15 && AC.dokumen[0].data.minKarung === 60 && AC.dokumen[0].data.tempoHari === 21 && /kadar air > 16 % atau butir patah > 15 %/.test(AC.patch.kabar), J(AC));
terapkanKeCache(AC.dokumen); var R2 = rekapTimbangMutu(); var pA2 = R2.pemasok.find(function (p) { return p.pemasok === 'PEMASOK A'; }); var hT2 = hitungMasuk(dT);
ok('ambang diubah → tanda IKUT: Angsa kadar air 15 % kini di bawah maks 16 % (tidak AWAS); Perahu butir patah 20 % kini > maks 15 % (AWAS bertambah) — di draf DAN di rekap kedatangan tersimpan; bukan bawaan lagi',
  aturCatat().kadarAirMaks === 16 && aturCatat().patahMaks === 15 && aturCatat().mutuBawaan.kadarAirMaks === false && aturCatat().mutuBawaan.patahMaks === false && hT2.sah[0].cek.awas.length === 0
  && J(hT2.sah[1].cek.awas) === J(['ada kutu', 'bau apek', 'butir patah 20 % > maks 15 %']) && pA2.awas.length === 1 && pA2.awas[0].merk === 'Perahu' && pA2.awas[0].alasan.length === 3 && pA2.kedatanganAwas === 1 && R2.atur.kadarAirMaks === 16,
  J([hT2.sah.map(function (b) { return b.cek.awas; }), pA2.awas]));
var AC2 = susunAturCatat({ tempoHari: '30' }, W);
ok('menyimpan Atur tanpa menyentuh ambang mutu tidak mengembalikannya ke bawaan (16 % / 15 % tetap tertulis)', !AC2.tolak && AC2.dokumen[0].data.kadarAirMaks === 16 && AC2.dokumen[0].data.patahMaks === 15, J(AC2.dokumen && AC2.dokumen[0].data));

// ---- KOREKSI kedatangan membawa & bisa mengubah isian
var dk = drafDariKedatangan(idT);
ok('koreksi: draf membawa isian tersimpan sebagai teks (Angsa "1987,5" · 15 · tidak · normal; Perahu 505 · ada · apek · 20); Merpati kosong semua', dk.baris[0].timbangKg === '1987,5' && dk.baris[0].kadarAir === '15' && dk.baris[0].kutu === 'tidak' && dk.baris[0].bau === 'normal' && dk.baris[0].butirPatah === ''
  && dk.baris[1].timbangKg === '505' && dk.baris[1].kutu === 'ada' && dk.baris[1].butirPatah === '20' && TM_KOLOM.every(function (k) { return dk.baris[2][k] === ''; }), J(dk.baris));
var uSebelum = uang(); dk.baris[0].kadarAir = '13'; dk.baris[1].timbangKg = ''; dk.baris[2].timbangKg = '498'; dk.alasan = 'timbang ulang';
var KR = susunSimpanMasuk(dk, { tanggal: '2026-09-20', jam: '11:00', idUnik: W.idUnik }, true); var mK = KR.dokumen ? KR.dokumen[0].data.merkList : [];
ok('koreksi mengubah isian: Angsa timbang tetap 1987,5 & kadar air jadi 13; Perahu timbang DIKOSONGKAN (kolom hilang) tapi kutu/bau/patah tetap; Merpati kini ditimbang 498; id sama, alasan tercatat',
  !KR.tolak && KR.dokumen[0].data.id === idT && mK[0].timbangKg === 1987.5 && mK[0].kadarAir === 13 && !('timbangKg' in mK[1]) && mK[1].kutu === 'ada' && mK[1].butirPatah === 20 && mK[2].timbangKg === 498 && KR.dokumen[0].data.alasanKoreksi === 'timbang ulang', J([KR.tolak, mK]));
ok('koreksi isian tidak mengubah angka buku: baris tanpa lima kolom baru sama dengan sebelum koreksi; stok/modal/bon/laba sama', J(tanpaTM(mK)) === J(tanpaTM(mT)) && denganCacheSementara(KR.dokumen, uang) === uSebelum, J([tanpaTM(mK), tanpaTM(mT)]));
terapkanKeCache(KR.dokumen);
var dL = drafDariKedatangan('b1'); var hL = hitungMasuk(dL); dL.alasan = 'cek koreksi lama'; var KL = susunSimpanMasuk(dL, W, true);
ok('kedatangan LAMA tanpa isian tetap tampil benar: draf koreksi berisian kosong, belum ditimbang / tidak dicek; disimpan ulang tetap berbentuk lama persis (tanpa kolom baru)',
  TM_KOLOM.every(function (k) { return dL.baris[0][k] === ''; }) && hL.sah.every(function (b) { return b.cek.timbangKg === null && !b.cek.dicek && b.cek.timbangTeks === 'belum ditimbang'; }) && !KL.tolak && KL.dokumen[0].data.merkList.every(function (r) { return kunci(r) === DASAR; }), J([KL.tolak, KL.dokumen && KL.dokumen[0].data.merkList]));
var KH = susunKoreksiHpp('Merpati', '15100', 'bongkar belum masuk', W, true); var bH = KH.dokumen ? KH.dokumen.find(function (d) { return d.koleksi === 'batchMasuk'; }) : null;
ok('koreksi HPP (Stok › HPP) lewat jalur koreksi kedatangan TIDAK menghapus isian: Merpati harga 15.100 + timbang 498 tetap; Angsa kadar air 13 tetap', !KH.tolak && !!bH && String(bH.data.id) === String(idT) && bH.data.merkList[2].hargaPerKg === 15100 && bH.data.merkList[2].timbangKg === 498 && bH.data.merkList[0].kadarAir === 13 && bH.data.merkList[1].kutu === 'ada', J([KH.tolak, bH && bH.data.merkList]));
print(J({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
var J = JSON.stringify; __dom['jualKarungBerat'] = { value: '50' };
Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
var nId = 900000; var W = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
var bulan = TGL_CAD.slice(0, 7); var akhir = bulan + '-' + String(new Date(Number(bulan.slice(0, 4)), Number(bulan.slice(5, 7)), 0).getDate()).padStart(2, '0');
var uang = function () { var st = hitungStokKarungPerMerk(); var o = {}; Object.keys(st).sort().forEach(function (m) { o[m] = [Math.round(st[m].sisaKg * 1000) / 1000, Math.round(st[m].hppTerakhirPerKg * 1000) / 1000]; });
  return J({ stok: o, utang: hitungUtangPemasok().map(function (p) { return [p.pemasok, Math.round(p.totalUtang)]; }), laba: hitungLabaBersihRentang(bulan + '-01', akhir).labaBersih }); };
var cacat = [];
var R = rekapTimbangMutu();
R.pemasok.forEach(function (p) { if (p.ditimbang + p.sebagian + p.belumTimbang !== p.kedatangan) cacat.push('tidak menutup: ' + p.pemasok); if ((p.persenRata === null) !== (p.barisTimbang === 0)) cacat.push('persen vs ditimbang: ' + p.pemasok); });
if (R.total.kedatangan !== R.pemasok.reduce(function (a, p) { return a + p.kedatangan; }, 0)) cacat.push('total ≠ Σ pemasok');
// hitungan sendiri: kedatangan nyata = batch bukan stok awal / saldo pembuka / lahir buku yang punya baris karung ber-kg
var sendiri = 0, bal = 0; (CADANGAN.batchMasuk || []).forEach(function (b) { if (b.stokAwal || b.tutupBuku || b.lahirBuku) return; var k = (b.merkList || []).filter(function (m) { return m && m.bentuk !== 'bal' && m.merk && (Number(m.totalKg) || 0) > 0; });
  if (k.length) sendiri += 1; else if ((b.merkList || []).some(function (m) { return m && m.bentuk === 'bal'; })) bal += 1; });
if (sendiri !== R.total.kedatangan || bal !== R.lewatBal) cacat.push('jumlah kedatangan rekap ' + R.total.kedatangan + ' ≠ hitungan sendiri ' + sendiri);
var masalahLama = 0; ambilSemuaBatch().forEach(function (b) { tmKedatangan(b).baris.forEach(function (x) { if (x.masalah) masalahLama += 1; }); });
if (masalahLama) cacat.push(masalahLama + ' baris kedatangan tersimpan dibaca bermasalah');
// kolom yang dikenal cadangan + lima kolom baru
var kenal = {}; (CADANGAN.batchMasuk || []).forEach(function (b) { (b.merkList || []).forEach(function (m) { Object.keys(m).forEach(function (k) { kenal[k] = 1; }); }); }); TM_KOLOM.forEach(function (k) { kenal[k] = 1; });
var ISI = { timbangKg: '3.488', kadarAir: '14,5', kutu: 'tidak', bau: 'normal', butirPatah: '22' };
// (1) koreksi kedatangan nyata terbaru yang bisa dikoreksi: isi timbang & mutu baris pertama — angka uang tidak bergeser
var calon = daftarKedatangan(1e9).filter(function (k) { return !k.fondasi; }); var koreksi = { dicoba: 0, ok: '', tolak: [] };
for (var i = 0; i < calon.length && !koreksi.ok; i++) { var d = drafDariKedatangan(calon[i].id); if (!d || !d.baris.length) continue; koreksi.dicoba += 1;
  var d0 = JSON.parse(J(d)); d0.alasan = 'asap'; var d1 = JSON.parse(J(d0)); Object.keys(ISI).forEach(function (k) { d1.baris[0][k] = ISI[k]; });
  var K0 = susunSimpanMasuk(d0, W, true), K1 = susunSimpanMasuk(d1, W, true);
  if (K0.tolak || K1.tolak) { koreksi.tolak.push(calon[i].tanggal + ': ' + String(K0.tolak || K1.tolak).slice(0, 80)); continue; }
  var sama = denganCacheSementara(K0.dokumen, uang) === denganCacheSementara(K1.dokumen, uang) && denganCacheSementara(K1.dokumen, uang) === uang();
  var asing = Object.keys(K1.dokumen[0].data.merkList[0]).filter(function (k) { return !kenal[k]; });
  koreksi.ok = calon[i].pemasok + ' ' + calon[i].tanggal; if (!sama) cacat.push('koreksi berisian menggeser stok/utang/laba'); if (asing.length) cacat.push('kolom asing: ' + asing.join(','));
  if (J(K1.dokumen[0].data.merkList[0].timbangKg) !== '3488') cacat.push('timbang koreksi tidak tertulis'); }
// (2) kedatangan BARU berisian di data toko
var dB = drafMasukKosong(W); dB.pemasok = calonPemasok()[0] || 'X'; dB.baris = [Object.assign({ merk: calonMerkMasuk()[0], jumlahKarung: '70', beratKarung: 50, hargaPerKg: '13.000', varian: 'sama' }, ISI)];
var dB0 = JSON.parse(J(dB)); TM_KOLOM.forEach(function (k) { dB0.baris[0][k] = ''; });
var B1 = susunSimpanMasuk(dB, W, true), B0 = susunSimpanMasuk(dB0, W, true); var baru = { tolak: B1.tolak || B0.tolak || '' };
if (!baru.tolak) { if (denganCacheSementara(B1.dokumen, uang) !== denganCacheSementara(B0.dokumen, uang)) cacat.push('kedatangan baru berisian menggeser stok/utang/laba');
  var asingB = Object.keys(B1.dokumen[0].data.merkList[0]).filter(function (k) { return !kenal[k]; }); if (asingB.length) cacat.push('kolom asing kedatangan baru: ' + asingB.join(','));
  if (Object.keys(B0.dokumen[0].data.merkList[0]).some(function (k) { return TM_KOLOM.indexOf(k) >= 0; })) cacat.push('kedatangan tanpa isian menulis kolom baru');
  var sel = tmBaris(B1.dokumen[0].data.merkList[0], 3500, 13000); if (sel.selisihKg !== -12) cacat.push('selisih kedatangan baru ' + sel.selisihKg); } else cacat.push('kedatangan baru ditolak: ' + baru.tolak);
print(J({ pemasok: R.pemasok.map(function (p) { return { p: p.pemasok, k: p.kedatangan, t: p.ditimbang, s: p.sebagian, b: p.belumTimbang, dicek: p.dicek, awas: p.kedatanganAwas }; }), total: R.total, lewatBal: R.lewatBal,
  atur: R.atur, koreksi: koreksi, cacat: cacat }));
"""


def jalan_asap(js):
    p = uji_wadah_bernama.cadangan_toko()
    if not p: return None, None
    cad, tgl = uji_wadah_bernama.cad_js(p)
    a, e = uji_wadah_bernama.jalan(UW.JAM_TETAP.replace('2026-09-20T10:00:00', tgl + 'T23:00:00') + js + '\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + ASAP)
    return (a if a is not None else {'jatuh': e[-500:]}), p


def utama(js):
    h, e = uji_wadah_bernama.jalan(UW.JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


# ---- pemeriksaan statis stok.js (layar DOM tidak ikut kotak pasir): lembar Barang masuk memuat isian, kalimat "catatan pemeriksaan saja", rekap & Atur
POT = [('baris: isian berat timbang', 'data-kolom="timbangKg" data-i="${i}"'),
       ('baris: isian kadar air', 'data-kolom="kadarAir" data-i="${i}"'),
       ('baris: isian butir patah', 'data-kolom="butirPatah" data-i="${i}"'),
       ('baris: pil kutu & bau (dengan "tidak dicek")', "<div><div class=\"ket\">Kutu</div>${pil('kutu', C.TM_KUTU)}</div>"),
       ('baris: pil bau', "<div><div class=\"ket\">Bau</div>${pil('bau', C.TM_BAU)}</div>"),
       ('baris: isian timbang & mutu dipasang di tiap baris', '${gambarCekMasuk(b, d.baris[i], i, a)}'),
       ('lembar menulis bahwa timbang = catatan pemeriksaan saja', 'Catatan pemeriksaan saja — kg di buku, stok, modal, HPP, dan bon tetap menurut nota.'),
       ('kartu Jumlah: timbang tidak mengubah kg/stok/modal/bon', 'catatan pemeriksaan saja: ${KG(hm.kg)} di atas, stok, modal, HPP &amp; bon tetap menurut nota.'),
       ('rekap per pemasok dipasang di lembar', '${gambarRekapTimbang()}'),
       ('rekap memakai fungsi logika (satu sumber)', 'const R = C.rekapTimbangMutu();'),
       ('rekap: nilai kurang berlabel perkiraan, tidak dibukukan', 'perkiraan nilai, tidak dibukukan: stok, modal, HPP, dan bon tetap menurut nota.'),
       ('rekap: belum ditimbang digambar "—", bukan 0', "<span class=\"n\">${p.barisTimbang ? (p.kgKurang ? '−' + KG(p.kgKurang) : 'tidak kurang') : '—'}</span>"),
       ('Atur: isian ambang kadar air', 'data-ketik="cKetikAtur" data-kolom="kadarAirMaks"'),
       ('Atur: isian ambang butir patah', 'data-ketik="cKetikAtur" data-kolom="patahMaks"'),
       ('Atur: draf membawa ambang mutu', 'kadarAirMaks: t(a.kadarAirMaks), patahMaks: t(a.patahMaks)'),
       ('Atur: angka bawaan disebut perkiraan', '= angka bawaan (perkiraan) — bisa diubah di sini.'),
       ('buku kedatangan menandai timbang & mutu', "${k.cek && k.cek.teks ? ' · ' + k.cek.teks : ''}")]


def statis(teks):
    return [n for n, pot in POT if pot not in teks]


RUSAK = {
    'kosong dianggap timbang 0 (selisih = −nota)': ("const timbang = tb !== null ? ckB2(tb) : null;", "const timbang = tb !== null ? ckB2(tb) : 0;"),
    'timbang mengubah kg buku': ("totalKg: ckB2(jumlah * berat), subtotalHarga: Math.round(jumlah * berat * harga)", "totalKg: cek.timbangKg !== null ? cek.timbangKg : ckB2(jumlah * berat), subtotalHarga: Math.round(jumlah * berat * harga)"),
    'kolom timbang & mutu tidak ditulis': (".map((r, i) => Object.assign(r, h.sah[i].cek.kolom))", ".map((r) => r)"),
    'kolom kosong ikut ditulis (bentuk lama berubah)': ("if (timbang !== null) hasil.kolom.timbangKg = timbang;", "hasil.kolom.timbangKg = timbang;"),
    'koreksi tidak membawa isian': ("m.merkPemasok ? { merkPemasok: String(m.merkPemasok) } : {}, tmDraf(m)))", "m.merkPemasok ? { merkPemasok: String(m.merkPemasok) } : {}))"),
    'ambang kadar air owner diabaikan': ("kadarAirMaks: airMilik ? Number(a.kadarAirMaks) : ATUR_CATAT_BAWAAN.kadarAirMaks", "kadarAirMaks: ATUR_CATAT_BAWAAN.kadarAirMaks"),
    'ambang butir patah owner diabaikan': ("patahMaks: patahMilik ? Number(a.patahMaks) : ATUR_CATAT_BAWAAN.patahMaks", "patahMaks: ATUR_CATAT_BAWAAN.patahMaks"),
    'kadar air di atas ambang tidak ditandai': ("if (hasil.kadarAir !== null && hasil.kadarAir > A.kadarAirMaks) hasil.awas.push(", "if (false) hasil.awas.push("),
    'kutu ada tidak ditandai': ("if (kutu === 'ada') hasil.awas.push('ada kutu');", ""),
    'bau apek tidak ditandai': ("if (bau === 'apek') hasil.awas.push('bau apek');", ""),
    'butir patah di atas ambang tidak ditandai': ("if (hasil.butirPatah !== null && hasil.butirPatah > A.patahMaks) hasil.awas.push(", "if (false) hasil.awas.push("),
    'kadar air mustahil diterima': (": air !== null && !(air >= 0 && air <= 100) ?", ": false ?"),
    'ketikan bukan angka dianggap 0': (r"return /^[\d.,]*\d[\d.,]*$/.test(t) ? ckAngka(t) : NaN;", "return ckAngka(t);"),
    'masalah isian tidak menghalangi simpan': ("'harga beli per kg belum diisi' : cek.masalah;", "'harga beli per kg belum diisi' : '';"),
    'baris cek tanpa nama dibuang diam-diam': ("const terisi = !!merk || jumlah > 0 || harga > 0 || cek.ada;", "const terisi = !!merk || jumlah > 0 || harga > 0;"),
    'rekap: kedatangan sebagian dihitung ditimbang': ("if (K.ditimbang === K.nBaris) p.ditimbang += 1; else if (K.ditimbang > 0) p.sebagian += 1;", "if (K.ditimbang > 0) p.ditimbang += 1; else if (false) p.sebagian += 1;"),
    'rekap: nilai kurang tanpa harga baris': ("hasil.nilaiKurang = Math.round(hasil.kgKurang * (Number(harga) || 0));", "hasil.nilaiKurang = Math.round(hasil.kgKurang);"),
    'rekap: belum ditimbang digambar 0 %': ("p.persenRata = p.kgNota > 0 ? Math.round(p.selisihKg / p.kgNota * 1000) / 10 : null;", "p.persenRata = p.kgNota > 0 ? Math.round(p.selisihKg / p.kgNota * 1000) / 10 : 0;"),
    'rekap: kedatangan tanpa nama pemasok dibuang': ("const pem = String(b.pemasok || '').trim() || '(tanpa nama pemasok)';", "const pem = String(b.pemasok || '').trim(); if (!pem) return;"),
    'rekap: kelompok tanpa nama pemasok tidak di bawah': ("tanpaNama(x) - tanpaNama(y) || ", ""),
    'atur: ambang mutu tidak disimpan': ("batasVarian: v.nilai, kadarAirMaks: ka.nilai, patahMaks: bp.nilai } }]", "batasVarian: v.nilai } }]"),
}

if __name__ == '__main__':
    js = UW.bundel(); sk = open(os.path.join(AKAR, 'baru/js/layar/stok.js'), encoding='utf-8').read()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, (a, b) in RUSAK.items():
            if js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g = utama(js.replace(a, b))
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        for nama, pot in POT:
            if sk.count(pot) < 1: print('KONTROL BASI  statis ' + nama); kode = 3; continue
            g = statis(sk.replace(pot, ''))
            print(('BERBUNYI ' if g else 'DIAM!!   ') + 'statis: ' + nama)
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    gs = statis(sk); g = g + ['statis stok.js: ' + x for x in gs]
    print('BARANG MASUK — TIMBANG & MUTU (kotak pasir + statis): %d lulus · %d gagal' % (l + len(POT) - len(gs), len(g)))
    for x in g: print('   ✗ ' + x)
    asap, p = jalan_asap(js)
    if asap:
        if 'jatuh' in asap: g.append('asap data toko JATUH: ' + asap['jatuh']); print('   ✗ ' + g[-1])
        else:
            t = asap['total']
            print('ASAP DATA TOKO (%s): %s · total %d kedatangan, ditimbang %d, sebagian %d, belum %d, mutu dicek %d · koreksi berisian dicoba di %s · ambang kadar air %s %% / butir patah %s %%%s'
                  % (os.path.basename(p), '; '.join('%s %d kedatangan (ditimbang %d, sebagian %d, belum %d, mutu dicek %d, AWAS %d)' % (x['p'], x['k'], x['t'], x['s'], x['b'], x['dicek'], x['awas']) for x in asap['pemasok']) or '-',
                     t['kedatangan'], t['ditimbang'], t['sebagian'], t['belumTimbang'], t['dicek'], asap['koreksi']['ok'] or 'TIDAK ADA (' + '; '.join(asap['koreksi']['tolak'][:3]) + ')',
                     asap['atur']['kadarAirMaks'], asap['atur']['patahMaks'], ' (angka bawaan)' if asap['atur']['mutuBawaan']['kadarAirMaks'] else ''))
            if asap['cacat']: g.append('asap data toko: ' + '; '.join(asap['cacat'])[:600]); print('   ✗ ' + g[-1])
            if not asap['koreksi']['ok']: g.append('asap: tidak ada kedatangan toko yang bisa dikoreksi untuk uji isian'); print('   ✗ ' + g[-1])
    sys.exit(2 if g else 0)
