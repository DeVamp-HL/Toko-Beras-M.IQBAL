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
// tinjauan no. 13 (9 Okt): pemisah ganda / di ujung (salah ketuk koma/titik di HP) DITOLAK — dulu tersimpan 0 % (kadar air 15,5 % jadi 0 %, AWAS hilang)
var RUSAK13 = ['15,,5', '14..5', '14,5,', '1.4.5']; var A13 = { kadarAirMaks: 14, patahMaks: 25 };
var tb13 = RUSAK13.map(function (x) { var c = tmBaris({ kadarAir: x, butirPatah: x }, 1000, 13000, A13); return [x, c.masalah, c.kadarAir, J(c.kolom)]; });
ok('tinjauan no. 13: kadar air / butir patah "15,,5" · "14..5" · "14,5," · "1.4.5" DITOLAK dengan kalimat (bukan tersimpan 0 %); berat timbang "1000..5" ditolak; ambang Atur "2..5" / "14..5" ditolak; "15,5" tetap 15,5 % → AWAS',
  RUSAK13.every(function (x) { return /kadar air harus angka/.test(tolak(0, { kadarAir: x })) && /butir patah harus angka/.test(tolak(1, { butirPatah: x })) && !!susunAturCatat({ patahMaks: x }, W).tolak && !!susunAturCatat({ kadarAirMaks: x }, W).tolak; })
  && tb13.every(function (r) { return !!r[1] && r[3] !== J({ kadarAir: 0, butirPatah: 0 }); }) && /berat timbang harus angka/.test(tolak(2, { timbangKg: '1000..5' })) && /Butir patah maksimal/.test(susunAturCatat({ patahMaks: '2..5' }, W).tolak || '')
  && tmBaris({ kadarAir: '15,5' }, 1000, 13000, A13).kadarAir === 15.5 && J(tmBaris({ kadarAir: '15,5' }, 1000, 13000, A13).awas) === J(['kadar air 15,5 % > maks 14 %']), J(tb13));
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
// tinjauan no. 22 (9 Okt): dokumen catatStok toko (cadangan 9 Okt: TANPA kolom mutu) — owner membuka Atur (draf diisi angka bawaan 14 / 25, bentuk bukaAturC)
// hanya untuk mengubah tempo 31 → 30 hari lalu SIMPAN → ambang mutu TIDAK ditulis, tetap "angka bawaan (perkiraan)"; kolom mutu dikosongkan pun tidak ditulis;
// yang benar-benar diubah (patah 20) ditulis sendiri.
pasok('aturanToko', [{ id: 'catatStok', batasSelisih: 3, minKarung: 60, tempoHari: 31, ambangSusutPositif: 250000 }]);
var A22 = aturCatat(); var t22 = function (n) { return String(n).replace('.', ','); };
var draf22 = { minKarung: t22(A22.minKarung), tempoHari: '30', batasSelisih: t22(A22.batasSelisih), ambangSusutPositif: t22(A22.ambangSusutPositif), batasVarian: t22(A22.batasVarian), kadarAirMaks: t22(A22.kadarAirMaks), patahMaks: t22(A22.patahMaks) };
var S22 = susunAturCatat(draf22, W); var d22 = S22.dokumen ? S22.dokumen[0].data : {}; var B22 = S22.dokumen ? denganCacheSementara(S22.dokumen, function () { return aturCatat(); }) : null;
var K22 = susunAturCatat({ tempoHari: '30', kadarAirMaks: '', patahMaks: '' }, W); var k22 = K22.dokumen ? K22.dokumen[0].data : {};
var P22 = susunAturCatat(Object.assign({}, draf22, { patahMaks: '20' }), W); var p22 = P22.dokumen ? P22.dokumen[0].data : {}; var Q22 = P22.dokumen ? denganCacheSementara(P22.dokumen, function () { return aturCatat(); }) : null;
ok('tinjauan no. 22: simpan Atur (tempo 31 → 30) dari draf berisi angka bawaan TIDAK menulis kadarAirMaks/patahMaks → tetap "angka bawaan (perkiraan)" (14 / 25); kolom mutu kosong juga tidak ditulis; patah diubah ke 20 → hanya patahMaks yang jadi setelan owner',
  !S22.tolak && d22.tempoHari === 30 && d22.minKarung === 60 && !('kadarAirMaks' in d22) && !('patahMaks' in d22) && !!B22 && B22.tempoHari === 30 && B22.kadarAirMaks === 14 && B22.patahMaks === 25 && B22.mutuBawaan.kadarAirMaks === true && B22.mutuBawaan.patahMaks === true
  && !K22.tolak && !('kadarAirMaks' in k22) && !('patahMaks' in k22) && !P22.tolak && p22.patahMaks === 20 && !('kadarAirMaks' in p22) && !!Q22 && Q22.mutuBawaan.patahMaks === false && Q22.mutuBawaan.kadarAirMaks === true && Q22.patahMaks === 20,
  J([d22, B22 && B22.mutuBawaan, k22, p22]));
pasok('aturanToko', []);
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
// ==================== Paket Barang masuk & mutu, Tahap 1 (owner 26 Nov 2026) ====================
pasok('aturanToko', []);
// ---- timbang SAMPEL (tangan): 5 karung ditimbang 247,5 kg → rata-rata 49,5 kg per karung (label 50 → kurang 0,5); baris 40 karung → perkiraan 1.980 kg,
//      nota 2.000 → KURANG 20 kg × Rp13.000 = Rp260.000
var s1 = tmBaris({ sampelKarung: '5', sampelKg: '247,5', jumlahKarung: '40', beratKarung: 50 }, 2000, 13000);
ok('timbang sampel (tangan): 5 karung 247,5 kg → rata-rata 49,5; perkiraan seluruh baris 1.980 kg; kurang 20 kg ≈ Rp260.000; DITANDAI perkiraan; kolom yang ditulis = sampel saja (bukan timbangKg)',
  s1.sampel.rata === 49.5 && s1.sampel.kurangPerKarung === 0.5 && s1.sampel.perkiraanKg === 1980 && s1.timbangKg === 1980 && s1.selisihKg === -20 && s1.nilaiKurang === 260000 && s1.perkiraan === true && /PERKIRAAN dari sampel 5 karung/.test(s1.timbangTeks) && s1.kolom.sampelKarung === 5 && s1.kolom.sampelKg === 247.5 && s1.kolom.timbangKg === undefined, J(s1));
var s2 = tmBaris({ sampelKarung: '5', sampelKg: '247,5', timbangKg: '1.990', jumlahKarung: '40', beratKarung: 50 }, 2000, 13000);
ok('timbang sampel: kalau seluruh baris JUGA ditimbang, yang dipakai timbang seluruh baris (1.990 → kurang 10 kg), bukan perkiraan', s2.timbangKg === 1990 && s2.selisihKg === -10 && s2.perkiraan === false && s2.kolom.timbangKg === 1990 && s2.kolom.sampelKarung === 5, J(s2));
ok('timbang sampel: satu angka saja DITOLAK dengan kalimat; karung sampel pecahan / nol ditolak; sampel lebih banyak dari karung baris DITANDAI', /DUA angka/.test(tmBaris({ sampelKarung: '5', jumlahKarung: '40', beratKarung: 50 }, 2000, 13000).masalah) && /DUA angka/.test(tmBaris({ sampelKg: '247', jumlahKarung: '40', beratKarung: 50 }, 2000, 13000).masalah) && !!tmBaris({ sampelKarung: '2,5', sampelKg: '100', jumlahKarung: '40', beratKarung: 50 }, 2000, 13000).masalah && !!tmBaris({ sampelKarung: '0', sampelKg: '100', jumlahKarung: '40', beratKarung: 50 }, 2000, 13000).masalah && tmBaris({ sampelKarung: '50', sampelKg: '2.475', jumlahKarung: '40', beratKarung: 50 }, 2000, 13000).sampel.lebihDariBaris === true);
// ---- mutu rinci per kelas (bawaan: premium patah ≤ 15, menir ≤ 0,5 · medium patah ≤ 25, menir ≤ 2 · lainnya 0 = belum diatur)
var m1 = tmBaris({ kelasMutu: 'premium', butirPatah: '18', menir: '0,8', kuning: '3' }, 2000, 13000);
ok('mutu rinci (tangan): kelas PREMIUM, patah 18 % > 15 & menir 0,8 % > 0,5 → dua AWAS berkelas premium; kuning 3 % tanpa ambang (0) TIDAK dinilai; patah 18 < 25 umum tidak menggandakan AWAS', m1.awas.length === 2 && /butir patah 18 % > maks premium 15/.test(m1.awas.join('|')) && /menir 0,8 % > maks premium 0,5/.test(m1.awas.join('|')) && m1.rinci.kuning === 3 && m1.kolom.kelasMutu === 'premium' && m1.kolom.menir === 0.8 && m1.kolom.kuning === 3 && m1.dicek === true, J(m1));
var m2 = tmBaris({ kelasMutu: 'medium', butirPatah: '18', menir: '0,8' }, 2000, 13000); var m3 = tmBaris({ butirPatah: '18', menir: '5' }, 2000, 13000);
ok('mutu rinci: angka yang sama di kelas MEDIUM tidak AWAS; TANPA kelas → menir 5 % dicatat tapi tidak dinilai (disebut "kelas mutu belum dipilih"), bukan dianggap baik', m2.awas.length === 0 && m3.awas.length === 0 && m3.rinci.menir === 5 && /kelas mutu belum dipilih/.test(m3.mutuTeks) && m3.kolom.kelasMutu === undefined, J([m2.awas, m3.mutuTeks]));
ok('mutu rinci: ketikan rusak / di luar batas DITOLAK (menir 120 %, gabah huruf, kelas ngawur) — tidak dianggap 0', !!tmBaris({ menir: '120' }, 2000, 13000).masalah && !!tmBaris({ gabah: 'banyak' }, 2000, 13000).masalah && !!tmBaris({ kelasMutu: 'super' }, 2000, 13000).masalah);
var AM = susunAturMutuKelas({ premium: { kuning: '2', butirPatah: '15', menir: '0,5', butirLain: '', gabah: '' }, medium: { butirPatah: '25', menir: '2', kuning: '', butirLain: '', gabah: '' } }, W);
ok('ambang per kelas: owner mengisi kuning premium 2 % → tersimpan di aturanToko/catatStok.mutuKelas, ambang lain tetap; ketikan rusak ditolak; tanpa perubahan ditolak', !AM.tolak && AM.dokumen[0].koleksi === 'aturanToko' && AM.dokumen[0].data.id === 'catatStok' && AM.dokumen[0].data.mutuKelas.premium.kuning === 2 && AM.dokumen[0].data.mutuKelas.premium.butirPatah === 15 && AM.dokumen[0].data.mutuKelas.medium.menir === 2 && !!susunAturMutuKelas({ premium: { kuning: 'abc' } }, W).tolak && susunAturMutuKelas({ premium: { butirPatah: '15' } }, W).tolak === 'Tidak ada yang diubah', J(AM));
terapkanKeCache(AM.dokumen);
ok('ambang per kelas: sesudah disimpan, kuning 3 % di kelas premium jadi AWAS; setelan lain di dokumen yang sama tidak hilang', tmBaris({ kelasMutu: 'premium', kuning: '3' }, 2000, 13000).awas.length === 1 && aturCatat().mutuKelas.premium.kuning === 2 && aturCatat().kadarAirMaks === 14, J(aturCatat().mutuKelas));
// ---- ONGKOS KIRIM (tangan): Angsa 40 × 50 kg @ 13.000 = 26 jt; bongkar 60 rb + ongkir 140 rb = 200 rb ÷ 2.000 kg = Rp100/kg → modal 13.100/kg
var dO = function (ongkir) { var d = drafMasukKosong(W); d.pemasok = 'PEMASOK C'; d.caraBayar = 'utang'; d.bongkar = '60.000'; d.ongkir = ongkir; d.baris = [Object.assign(barisMasukKosong(), { merk: 'Angsa', jumlahKarung: '40', beratKarung: 50, hargaPerKg: '13.000', varian: 'sama', sampelKarung: '5', sampelKg: '247,5' })]; return d; };
var hO0 = hitungMasuk(dO('')), hO = hitungMasuk(dO('140.000'));
ok('ongkos kirim (tangan): masuk modal bersama bongkar — tanpa ongkir modal 13.030/kg; dengan ongkir 140 rb modal 13.100/kg; total = beras 26 jt + 200 rb; nilai beras (bon) tidak berubah', hO0.sah[0].hppPerKg === 13030 && hO.sah[0].hppPerKg === 13100 && hO.ongkir === 140000 && hO.bongkar === 60000 && hO.total === 26200000 && hO.nilaiBeras === 26000000 && hO0.total === 26060000, J([hO0.sah[0].hppPerKg, hO.sah[0].hppPerKg, hO.total]));
var utangSemua = function () { return hitungUtangPemasok().reduce(function (a, p) { return a + p.totalUtang; }, 0); }; var u0 = utangSemua();
var SO = susunSimpanMasuk(dO('140.000'), W, true); var bO = SO.dokumen ? SO.dokumen[0].data : {};
ok('ongkos kirim: tersimpan — biayaBongkar (yang dibaca mesin) = 200 rb, ongkosKirim = 140 rb; kabar menyebut keduanya tunai dari laci', !SO.tolak && bO.biayaBongkar === 200000 && bO.ongkosKirim === 140000 && /ongkos kirim Rp140\.000/.test(SO.patch.kabar) && /selalu tunai dari laci/.test(SO.patch.kabar), J([SO.tolak, bO.biayaBongkar, bO.ongkosKirim]));
terapkanKeCache(SO.dokumen); var idO = bO.id;
ok('ongkos kirim (tangan): bon pemasok naik TEPAT nilai beras 26 jt (bongkar & ongkir tidak masuk bon); tanpa ongkir kolomnya tidak ditulis & biayaBongkar = bongkar saja', utangSemua() - u0 === 26000000 && susunSimpanMasuk(dO(''), W, true).dokumen[0].data.ongkosKirim === undefined && susunSimpanMasuk(dO(''), W, true).dokumen[0].data.biayaBongkar === 60000, String(utangSemua() - u0));
var dK = drafDariKedatangan(idO);
ok('ongkos kirim: draf koreksi memisahkan lagi bongkar 60 rb & ongkir 140 rb; isian sampel ikut terbawa; koreksi tanpa ubah angka menulis biayaBongkar 200 rb yang sama', dK.bongkar === '60000' && dK.ongkir === '140000' && dK.baris[0].sampelKarung === '5' && dK.baris[0].sampelKg === '247,5' && ckOngkir(bO) === 140000 && (function () { dK.alasan = 'cek'; var X = susunSimpanMasuk(dK, W, true); return !X.tolak && X.dokumen[0].data.biayaBongkar === 200000 && X.dokumen[0].data.ongkosKirim === 140000; })(), J(dK));
// ---- CATATAN UNTUK PEMASOK & KLAIM: usul dari timbang sampel (kurang 20 kg), disimpan, TIDAK mengubah stok / bon / laba
var CP0 = cpKedatangan(idO); var DR = cpDraf(idO);
ok('catatan pemasok: USUL dibaca dari timbang — Angsa KURANG 20 kg (perkiraan dari timbang sampel), nilai kurang Rp260.000; draf diisi usul itu & ditandai dariUsul; belum ada yang tersimpan', CP0.usul.length === 1 && CP0.usul[0].jenis === 'kurang' && CP0.usul[0].merk === 'Angsa' && CP0.usul[0].jumlah === 20 && /perkiraan/.test(CP0.usul[0].ket) && CP0.nilaiKurang === 260000 && CP0.ada === false && DR.dariUsul === true && DR.baris[0].jumlah === '20' && CP0.nilaiBon === 26000000, J([CP0.usul, DR]));
var sebelum = uang(); var mlSebelum = J(bO.merkList);
var isiCP = { baris: [{ jenis: 'kurang', merk: 'Angsa', jumlah: '20', satuan: 'kg', ket: 'timbang sampel 5 karung' }, { jenis: 'tertinggal', merk: 'Perahu', jumlah: '2', satuan: 'karung', ket: '' }], cara: 'potong', status: 'diminta', nilai: '', catatan: '' };
var SC = susunCatatanPemasok(idO, isiCP, W); var bC = SC.dokumen ? SC.dokumen[0].data : {};
ok('catatan pemasok: tersimpan PADA kedatangannya — 2 baris + klaim "minta bon dipotong" Rp260.000 (nilai dari timbang, karena dikosongkan); baris nota, bongkar, ongkir, cara bayar TIDAK berubah', !SC.tolak && SC.dokumen.length === 1 && SC.dokumen[0].koleksi === 'batchMasuk' && String(bC.id) === String(idO) && bC.catatanPemasok.length === 2 && bC.catatanPemasok[1].satuan === 'karung' && bC.klaim.cara === 'potong' && bC.klaim.nilai === 260000 && bC.klaim.nilaiDari === 'timbang' && bC.klaim.status === 'diminta' && J(bC.merkList) === mlSebelum && bC.biayaBongkar === 200000 && bC.ongkosKirim === 140000 && bC.caraBayar === 'utang' && /TIDAK berubah/.test(SC.patch.kabar), J([SC.tolak, bC.klaim]));
terapkanKeCache(SC.dokumen);
ok('catatan pemasok: stok, modal, bon pemasok & laba SAMA PERSIS sebelum dan sesudah catatan + klaim disimpan (Tahap 1 = catatan saja)', uang() === sebelum, J([sebelum.slice(0, 200), uang().slice(0, 200)]));
ok('catatan pemasok: ditolak dengan kalimat — kurang tanpa jumlah, mutu tanpa keterangan, jenis ngawur, klaim tanpa baris, nilai pecahan, tanpa perubahan', /jumlahnya belum diisi/.test(susunCatatanPemasok(idO, { baris: [{ jenis: 'kurang', merk: 'Angsa', jumlah: '' }] }, W).tolak) && /tidak sesuai mutunya/.test(susunCatatanPemasok(idO, { baris: [{ jenis: 'mutu', merk: 'Angsa', jumlah: '', ket: '' }] }, W).tolak) && !!susunCatatanPemasok(idO, { baris: [{ jenis: 'hilang', merk: 'Angsa', jumlah: '1' }] }, W).tolak && /minimal satu baris/.test(susunCatatanPemasok(idO, { baris: [], cara: 'potong' }, W).tolak) && /rupiah bulat/.test(susunCatatanPemasok(idO, Object.assign({}, isiCP, { nilai: '12,5' }), W).tolak) && susunCatatanPemasok(idO, isiCP, W).tolak === 'Tidak ada yang diubah' && !!susunCatatanPemasok('tidak-ada', isiCP, W).tolak);
var SC2 = susunCatatanPemasok(idO, Object.assign({}, isiCP, { cara: 'ganti', status: 'disetujui', nilai: '250.000', catatan: 'diganti kiriman berikut' }), W);
ok('klaim: tiga cara (potong · ganti · catat) & status bisa diubah; nilai yang diketik owner dipakai (250 rb, nilaiDari owner); tanggal klaim pertama dipertahankan; "cukup dicatat" tanpa nilai', !SC2.tolak && SC2.dokumen[0].data.klaim.cara === 'ganti' && SC2.dokumen[0].data.klaim.status === 'disetujui' && SC2.dokumen[0].data.klaim.nilai === 250000 && SC2.dokumen[0].data.klaim.nilaiDari === 'owner' && SC2.dokumen[0].data.klaim.tanggal === W.tanggal && KLAIM_CARA.length === 3 && susunCatatanPemasok(idO, Object.assign({}, isiCP, { cara: 'catat' }), W).dokumen[0].data.klaim.nilai === 0, J(SC2.dokumen && SC2.dokumen[0].data.klaim));
var dK2 = drafDariKedatangan(idO); dK2.alasan = 'salah ketik harga'; dK2.baris[0].hargaPerKg = '13.100'; var SK2 = susunSimpanMasuk(dK2, W, true);
ok('koreksi kedatangan TIDAK menghapus catatan pemasok & klaim yang sudah tersimpan', !SK2.tolak && SK2.dokumen[0].data.catatanPemasok.length === 2 && SK2.dokumen[0].data.klaim.cara === 'potong' && SK2.dokumen[0].data.merkList[0].hargaPerKg === 13100, J([SK2.tolak, SK2.dokumen && SK2.dokumen[0].data.klaim]));
var DF = cpDaftar(40);
ok('daftar bahan berunding: kedatangan bercatatan + klaim terbuka ikut (terbuka, 2 catatan); kedatangan tanpa catatan & tanpa selisih tidak ikut; kosongkan catatan = kolomnya dihapus dari dokumen', DF.some(function (x) { return String(x.id) === String(idO) && x.terbuka === true && x.nCatatan === 2; }) && !DF.some(function (x) { return x.id === 'b2'; }) && (function () { var X = susunCatatanPemasok(idO, { baris: [], cara: '' }, W); return !X.tolak && X.dokumen[0].data.catatanPemasok === undefined && X.dokumen[0].data.klaim === undefined; })(), J(DF));
// ---- SURAT untuk pemasok (Laporan › Dokumen kecil): isi = catatan Barang masuk apa adanya
var DKP = dokumenKecil('pemasok', String(idO), '', new Date('2026-09-20T10:00:00+07:00')); var brsP = DKP.baris.map(function (b) { return b.nama; }).join(' | ');
ok('surat pemasok (tangan): judul & pemasok; baris nota Angsa 2.000 kg @ Rp13.000 = 26 jt; timbang sampel 5 karung rata-rata 49,5 → perkiraan 1.980 kg, KURANG 20 kg; catatan kurang & tertinggal; permintaan "minta bon dipotong" Rp260.000', DKP.judul === 'Catatan untuk Pemasok' && /PEMASOK C/.test(DKP.sub) && /bon/.test(DKP.sub) && DKP.baris.some(function (b) { return /Angsa · 2000 kg @ Rp13\.000\/kg/.test(b.nama) && b.n === 26000000; }) && /timbang sampel 5 karung, rata-rata 49,5 kg per karung → perkiraan 1980 kg — KURANG 20 kg/.test(brsP) && /Kurang · Angsa · 20 kg — timbang sampel 5 karung/.test(brsP) && /Tertinggal · Perahu · 2 karung/.test(brsP) && DKP.baris[DKP.baris.length - 1].n === 260000 && /Minta dipotong \/ uang kembali/.test(DKP.baris[DKP.baris.length - 1].nama) && /perkiraan/.test(DKP.identitas) && DKP.pilihan.some(function (x) { return x.id === String(idO); }), J([DKP.sub, brsP, DKP.identitas]));
ok('surat pemasok: kedatangan TANPA catatan tidak dicetak (ditolak dengan kalimat & jalan menulisnya); jenis "Catatan untuk pemasok" terdaftar di dokumen kecil', /belum punya catatan untuk pemasok/.test(dokumenKecil('pemasok', 'b1', '', new Date('2026-09-20T10:00:00+07:00')).tolak) && JENIS_KECIL.some(function (j) { return j.id === 'pemasok' && j.nama === 'Catatan untuk pemasok'; }));
// ==================== Paket Barang masuk & mutu, Tahap 2 (owner 26 Nov 2026): potong bon membukukan · retur · tolak saat datang · catatan bebas ====================
// keadaan: kedatangan idO (PEMASOK C, BON) Angsa 40 × 50 kg @ 13.000 = 26 jt; catatan "kurang Angsa 20 kg" + klaim minta bon dipotong (status: disampaikan)
var stokAngsa = function () { return Math.round(hitungStokKarungPerMerk().Angsa.sisaKg * 100) / 100; };
ok('potong bon: klaim yang BELUM disetujui pemasok tidak bisa dibukukan (ditolak dengan kalimat); kedatangan lain tanpa klaim potong juga', /SETUJU/.test(hitungPotongKlaim(idO).tolak) && !!susunPotongKlaim(idO, W).tolak && /bukan "minta bon dipotong"/.test(hitungPotongKlaim('b1').tolak));
var SCs = susunCatatanPemasok(idO, Object.assign({}, isiCP, { status: 'disetujui' }), W); terapkanKeCache(SCs.dokumen);
var HP = hitungPotongKlaim(idO);
ok('potong bon (tangan): hanya baris "kurang" yang dipotong (tertinggal tidak) — Angsa 2.000 → 1.980 kg; nilai turun 20 × 13.000 = Rp260.000; bon 26.000.000 → 25.740.000', !HP.tolak && HP.baris.length === 1 && HP.baris[0].kgPotong === 20 && HP.baris[0].kgNota === 2000 && HP.baris[0].kgBaru === 1980 && HP.rp === 260000 && HP.kg === 20 && HP.bonLama === 26000000 && HP.bonBaru === 25740000, J(HP));
var u1 = utangSemua(), st1 = stokAngsa(), laba1 = hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih;
var SP = susunPotongKlaim(idO, W); var bP = SP.dokumen ? SP.dokumen[0].data : {};
ok('potong bon: kedatangan dikoreksi — kg buku 1.980, kgPotong 20, nilai 25.740.000, HARGA per kg tetap 13.000, jumlah karung tetap 40, bongkar & ongkir tetap; klaim jadi SELESAI + dibukukan; jejak potongan tercatat; catatan tidak hilang', !SP.tolak && SP.dokumen[0].koleksi === 'batchMasuk' && bP.merkList[0].totalKg === 1980 && bP.merkList[0].kgPotong === 20 && bP.merkList[0].subtotalHarga === 25740000 && bP.merkList[0].hargaPerKg === 13000 && bP.merkList[0].jumlahKarung === 40 && bP.biayaBongkar === 200000 && bP.ongkosKirim === 140000 && bP.klaim.status === 'selesai' && bP.klaim.dibukukan.kg === 20 && bP.klaim.dibukukan.rp === 260000 && bP.potongan.length === 1 && bP.potongan[0].jenis === 'klaim' && bP.catatanPemasok.length === 2 && /bon turun Rp260\.000/.test(SP.patch.kabar), J([SP.tolak, bP.merkList, bP.klaim]));
terapkanKeCache(SP.dokumen);
ok('potong bon (tangan): bon pemasok turun TEPAT Rp260.000; stok Angsa turun TEPAT 20 kg; laba September tidak berubah (belum ada yang terjual dari kedatangan ini)', u1 - utangSemua() === 260000 && Math.round((st1 - stokAngsa()) * 100) / 100 === 20 && hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih === laba1, J([u1 - utangSemua(), st1 - stokAngsa()]));
ok('potong bon: tidak bisa dibukukan DUA kali; cara klaim yang sudah dibukukan tidak bisa diganti / dihapus; timbang tetap dibanding nota ASLI 2.000 kg (bukan 1.980)', /sudah dibukukan/.test(hitungPotongKlaim(idO).tolak) && !!susunPotongKlaim(idO, W).tolak && /sudah dibukukan/.test(susunCatatanPemasok(idO, Object.assign({}, isiCP, { cara: 'ganti' }), W).tolak) && /sudah dibukukan/.test(susunCatatanPemasok(idO, { baris: [], cara: '' }, W).tolak) && cpKedatangan(idO).timbang.baris[0].kgNota === 2000 && cpKedatangan(idO).timbang.baris[0].selisihKg === -20 && cpKedatangan(idO).potongan.length === 1);
var dK3 = drafDariKedatangan(idO);
ok('potong bon: draf koreksi membawa kg yang sudah dipotong (20) — koreksi lain sesudahnya tidak mengembalikan kg; hitung ulang tetap 1.980 kg', dK3.baris[0].kgPotong === '20' && hitungMasuk(dK3).sah[0].totalKg === 1980 && hitungMasuk(dK3).sah[0].kgNota === 2000 && hitungMasuk(dK3).nilaiBeras === 25740000, J(dK3.baris[0]));
// ---- RETUR sesudah masuk stok (tangan): Angsa dikembalikan 100 kg → kg buku 1.880; nilai turun 100 × 13.000 = Rp1.300.000; bon 25.740.000 → 24.440.000
var HR = hitungReturPemasok(idO, { merk: 'Angsa', kg: '100', alasan: 'berkutu' }); var u2 = utangSemua(), st2 = stokAngsa();
var SR = susunReturPemasok(idO, { merk: 'Angsa', kg: '100', alasan: 'berkutu' }, W); var bR = SR.dokumen ? SR.dokumen[0].data : {};
ok('retur (tangan): Angsa 1.980 → 1.880 kg; bon 25.740.000 → 24.440.000 (turun Rp1.300.000); kgPotong jadi 120 (klaim 20 + retur 100); jejak potongan kedua berjenis retur + alasan', !HR.tolak && HR.rp === 1300000 && HR.bonBaru === 24440000 && HR.baris[0].kgSudah === 20 && !SR.tolak && bR.merkList[0].totalKg === 1880 && bR.merkList[0].kgPotong === 120 && bR.merkList[0].subtotalHarga === 24440000 && bR.potongan.length === 2 && bR.potongan[1].jenis === 'retur' && bR.potongan[1].alasan === 'berkutu' && bR.klaim.status === 'selesai', J([HR, SR.tolak]));
terapkanKeCache(SR.dokumen);
ok('retur (tangan): bon turun TEPAT Rp1.300.000 dan stok Angsa turun TEPAT 100 kg', u2 - utangSemua() === 1300000 && Math.round((st2 - stokAngsa()) * 100) / 100 === 100, J([u2 - utangSemua(), st2 - stokAngsa()]));
ok('retur: ditolak dengan kalimat — tanpa alasan, kg kosong / nol, nama yang tidak ada di kedatangan, lebih dari sisa buku, menghabiskan baris; kedatangan TUNAI dikenali (jalur uang kembali, diuji di Tahap 3)', /alasan/.test(susunReturPemasok(idO, { merk: 'Angsa', kg: '10', alasan: '' }, W).tolak) && !!susunReturPemasok(idO, { merk: 'Angsa', kg: '', alasan: 'berkutu' }, W).tolak && !!susunReturPemasok(idO, { merk: 'Angsa', kg: '0', alasan: 'berkutu' }, W).tolak && /tidak ada di baris kedatangan/.test(susunReturPemasok(idO, { merk: 'Merpati', kg: '10', alasan: 'berkutu' }, W).tolak) && /menghabiskan seluruh baris|sisa di buku/.test(susunReturPemasok(idO, { merk: 'Angsa', kg: '999999', alasan: 'berkutu' }, W).tolak) && hitungPotong('b2', [{ merk: 'Merpati', kg: 10 }], 'klaim').tunai === true && hitungPotong(idO, [{ merk: 'Angsa', kg: 1 }], 'klaim').tunai === false);
// bon yang SUDAH DIBAYAR: nilai sesudah potong tidak boleh di bawah yang dibayar (penjaga jalur koreksi kedatangan ikut berlaku)
terapkanKeCache([{ koleksi: 'utangPemasokMutasi', data: { id: 'byO', tanggal: '2026-09-20', jam: '11:00', tipe: 'bayar', pemasok: 'PEMASOK C', nominal: 24400000, bonId: String(idO), bonTanggal: '2026-09-20', dari: 'laci' } }]);
var SRb = susunReturPemasok(idO, { merk: 'Angsa', kg: '10', alasan: 'apek sekali' }, W);
ok('retur pada bon yang sudah dibayar Rp24.400.000: mengembalikan 10 kg membuat nilai bon 24.310.000 < yang dibayar → DITOLAK (tanpa dokumen), kalimatnya menyebut sudah dibayar', !!SRb.tolak && !SRb.dokumen && /dibayar/.test(SRb.tolak), J(SRb.tolak));
// ---- TOLAK SAAT DATANG (tangan): Angsa 10 karung diterima (500 kg, 6,5 jt); Perahu 5 karung DITOLAK (250 kg, 3,5 jt) — tidak masuk stok & bon
var dT = drafMasukKosong(W); dT.pemasok = 'PEMASOK C'; dT.caraBayar = 'utang'; dT.catatanBebas = '  Tolong kirim pengganti Perahu minggu depan.  ';
dT.baris = [Object.assign(barisMasukKosong(), { merk: 'Angsa', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '13.000', varian: 'sama' }), Object.assign(barisMasukKosong(), { merk: 'Perahu', jumlahKarung: '5', beratKarung: 50, hargaPerKg: '14.000', varian: 'sama', ditolak: '1', alasanTolak: 'berkutu' })];
var hT = hitungMasuk(dT); var u3 = utangSemua(); var ST = susunSimpanMasuk(dT, W, true); var bT = ST.dokumen ? ST.dokumen[0].data : {};
ok('tolak saat datang (tangan): yang dihitung hanya Angsa — 10 karung, 500 kg, Rp6.500.000; Perahu 5 karung tercatat ditolak (250 kg, Rp3.500.000, alasan) dan TIDAK ada di baris kedatangan', hT.sah.length === 1 && hT.ditolak.length === 1 && hT.kg === 500 && hT.karung === 10 && hT.nilaiBeras === 6500000 && !ST.tolak && bT.merkList.length === 1 && bT.merkList[0].merk === 'Angsa' && bT.ditolak.length === 1 && bT.ditolak[0].merk === 'Perahu' && bT.ditolak[0].jumlahKarung === 5 && bT.ditolak[0].kg === 250 && bT.ditolak[0].nilai === 3500000 && bT.ditolak[0].alasan === 'berkutu', J([ST.tolak, bT.merkList, bT.ditolak]));
var stP0 = (hitungStokKarungPerMerk().Perahu || { sisaKg: 0 }).sisaKg; terapkanKeCache(ST.dokumen); var idT2 = bT.id;
ok('tolak saat datang (tangan): bon naik TEPAT Rp6.500.000 (yang ditolak tidak ditagih); stok Perahu tidak bertambah; catatan bebas tersimpan rapi', utangSemua() - u3 === 6500000 && (hitungStokKarungPerMerk().Perahu || { sisaKg: 0 }).sisaKg === stP0 && bT.catatanBebas === 'Tolong kirim pengganti Perahu minggu depan.', J([utangSemua() - u3, bT.catatanBebas]));
ok('tolak saat datang: tanpa alasan DITOLAK simpan; semua baris ditolak → tidak ada kedatangan yang dicatat (ditolak dengan kalimat)', (function () { var d = JSON.parse(J(dT)); d.baris[1].alasanTolak = ''; var X = susunSimpanMasuk(d, W, true); return /tulis alasannya/.test(X.tolak || '') && !X.dokumen; })() && (function () { var d = JSON.parse(J(dT)); d.baris[0].ditolak = '1'; d.baris[0].alasanTolak = 'apek'; var X = susunSimpanMasuk(d, W, true); return /minimal satu baris/.test(X.tolak || '') && !X.dokumen; })());
var CT = cpKedatangan(idT2); var DKT = dokumenKecil('pemasok', String(idT2), '', new Date('2026-09-20T10:00:00+07:00')); var brsT = DKT.baris.map(function (b) { return b.nama; }).join(' | ');
ok('surat pemasok: kedatangan yang hanya punya baris ditolak + catatan bebas TETAP bisa dicetak; memuat "Ditolak saat datang · Perahu · 5 karung × 50 kg — berkutu" dan catatan bebasnya', CT.ada === true && CT.ditolak.length === 1 && CT.bebas === 'Tolong kirim pengganti Perahu minggu depan.' && /Perahu · 5 karung × 50 kg — berkutu/.test(brsT) && /Tolong kirim pengganti Perahu minggu depan\./.test(brsT) && !/belum punya catatan/.test(DKT.tolak || ''), J([brsT, DKT.tolak]));
var DKO = dokumenKecil('pemasok', String(idO), '', new Date('2026-09-20T10:00:00+07:00'));
ok('surat pemasok: potongan yang sudah dibukukan ikut tercetak — klaim 20 kg (−Rp260.000) & retur 100 kg (−Rp1.300.000)', DKO.baris.some(function (b) { return /bon dipotong \(klaim kurang timbang\) · 20 kg/.test(b.nama) && b.n === -260000; }) && DKO.baris.some(function (b) { return /dikembalikan ke pemasok · 100 kg — berkutu/.test(b.nama) && b.n === -1300000; }), J(DKO.baris.map(function (b) { return [b.nama, b.n]; })));
// ---- CATATAN BEBAS lewat lembar catatan: disimpan tanpa baris & tanpa klaim, uang tidak berubah; koreksi kedatangan membawanya; dikosongkan = dihapus
var uB = uang(); var SB = susunCatatanPemasok(idT2, { baris: [], cara: '', bebas: 'Perahu jangan dikirim lagi sebelum dicek.' }, W);
ok('catatan bebas: bisa disimpan sendirian (tanpa baris, tanpa klaim); kolom lain kedatangan tidak berubah; lebih dari 600 huruf ditolak', !SB.tolak && SB.dokumen[0].data.catatanBebas === 'Perahu jangan dikirim lagi sebelum dicek.' && J(SB.dokumen[0].data.merkList) === J(bT.merkList) && SB.dokumen[0].data.ditolak.length === 1 && /paling panjang/.test(susunCatatanPemasok(idT2, { baris: [], cara: '', bebas: new Array(700).join('x') }, W).tolak), J(SB.tolak));
terapkanKeCache(SB.dokumen);
ok('catatan bebas: stok, bon & laba sama persis sebelum/sesudah; draf koreksi membawanya; mengosongkannya menghapus kolomnya', uang() === uB && drafDariKedatangan(idT2).catatanBebas === 'Perahu jangan dikirim lagi sebelum dicek.' && (function () { var X = susunCatatanPemasok(idT2, { baris: [], cara: '', bebas: '' }, W); return !X.tolak && X.dokumen[0].data.catatanBebas === undefined && X.dokumen[0].data.ditolak.length === 1; })());
// ==================== TAHAP 3 (owner 26 Nov 2026) — hitung tangan ====================
// ---- KLAIM LANGSUNG SAAT DATANG, TUNAI: Merpati 10 × 50 kg @ Rp15.000 = nota 500 kg / Rp7.500.000; kurang 12,5 kg → dibukukan 487,5 kg / Rp7.312.500 (turun Rp187.500)
var gerak = function (id) { return daftarGerakanKas().filter(function (r) { return String(r.id) === String(id); }).reduce(function (a, r) { return a + r.keluar - r.masuk; }, 0); };
var stokKg = function (m) { return Math.round(((hitungStokKarungPerMerk()[m] || { sisaKg: 0 }).sisaKg) * 1000) / 1000; };
var dL = drafMasukKosong(W); dL.pemasok = 'PEMASOK B'; dL.caraBayar = 'tunai'; dL.alasanPotong = '  karung bocor  ';
dL.baris = [Object.assign(barisMasukKosong(), { merk: 'Merpati', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '15.000', varian: 'sama', kgPotong: '12,5' })];
var hL = hitungMasuk(dL); var sM0 = stokKg('Merpati'); var SL = susunSimpanMasuk(dL, W, true); var bL = SL.dokumen ? SL.dokumen[0].data : {};
ok('klaim langsung (tunai, tangan): nota 500 kg − 12,5 = 487,5 kg dibukukan; nilai 487,5 × 15.000 = Rp7.312.500; dipotong Rp187.500; harga per kg tetap', hL.kg === 487.5 && hL.nilaiBeras === 7312500 && hL.potongKg === 12.5 && hL.potongRp === 187500 && hL.sah[0].kgNota === 500 && hL.sah[0].hargaPerKg === 15000 && !SL.tolak && bL.merkList[0].totalKg === 487.5 && bL.merkList[0].kgPotong === 12.5 && bL.merkList[0].subtotalHarga === 7312500 && bL.merkList[0].hargaPerKg === 15000 && bL.caraBayar === 'tunai', J([SL.tolak, hL.kg, hL.nilaiBeras, hL.potongRp, bL.merkList]));
ok('klaim langsung: jejaknya di kedatangan — satu potongan bertanda saatDatang, 12,5 kg, Rp187.500, alasan dirapikan; kabar menyebutnya', bL.potongan && bL.potongan.length === 1 && bL.potongan[0].jenis === 'klaim' && bL.potongan[0].saatDatang === true && bL.potongan[0].kg === 12.5 && bL.potongan[0].rp === 187500 && bL.potongan[0].alasan === 'karung bocor' && bL.potongan[0].baris[0].merk === 'Merpati' && bL.potongan[0].baris[0].kg === 12.5 && /sudah dipotong 12,5 kg \(Rp187\.500\)/.test(SL.patch.kabar), J([bL.potongan, SL.patch && SL.patch.kabar]));
terapkanKeCache(SL.dokumen); var idL = bL.id;
ok('klaim langsung (tunai): stok Merpati bertambah TEPAT 487,5 kg; uang keluar laci hari itu TEPAT Rp7.312.500 (bukan nilai nota 7,5 jt)', Math.abs(stokKg('Merpati') - sM0 - 487.5) < 0.001 && gerak(idL) === 7312500, J([stokKg('Merpati') - sM0, gerak(idL)]));
var CL = cpKedatangan(idL); var DKL = dokumenKecil('pemasok', String(idL), '', new Date('2026-09-20T10:00:00+07:00'));
ok('klaim langsung: tampil di kartu catatan & surat pemasok sebagai "dipotong saat datang" 12,5 kg (−Rp187.500)', CL.potongan.length === 1 && CL.potongan[0].saatDatang === true && /dipotong saat datang/.test(CL.potongan[0].jenisNama) && DKL.baris.some(function (b) { return /dipotong saat datang \(kurang timbang\) · 12,5 kg — karung bocor/.test(b.nama) && b.n === -187500; }), J([CL.potongan, DKL.tolak, DKL.baris && DKL.baris.map(function (b) { return b.nama; })]));
// koreksi kedatangan itu (harga salah ketik 15.000 → 15.100) membawa potongannya, tidak menulis jejak kedua: 487,5 × 15.100 = Rp7.361.250
var dLK = drafDariKedatangan(idL); dLK.alasan = 'salah ketik harga'; dLK.baris[0].hargaPerKg = '15100'; dLK.baris[0].varian = 'sama'; var SLK = susunSimpanMasuk(dLK, W, true);
ok('klaim langsung: koreksi kedatangan membawa kg potongnya (487,5 kg × 15.100 = Rp7.361.250) dan TIDAK menambah / mengganti jejak potongan (tetap Rp187.500, alasan aslinya)', !SLK.tolak && SLK.dokumen[0].data.merkList[0].totalKg === 487.5 && SLK.dokumen[0].data.merkList[0].kgPotong === 12.5 && SLK.dokumen[0].data.merkList[0].subtotalHarga === 7361250 && SLK.dokumen[0].data.potongan.length === 1 && SLK.dokumen[0].data.potongan[0].rp === 187500 && SLK.dokumen[0].data.potongan[0].alasan === 'karung bocor', J([SLK.tolak, SLK.dokumen && SLK.dokumen[0].data.merkList, SLK.dokumen && SLK.dokumen[0].data.potongan]));
// ---- KLAIM LANGSUNG, BON: Angsa 20 × 50 kg @ Rp13.000 = nota 1.000 kg / Rp13.000.000; kurang 20 kg → 980 kg / Rp12.740.000 jadi bon
var dLB = drafMasukKosong(W); dLB.pemasok = 'PEMASOK C'; dLB.caraBayar = 'utang'; dLB.baris = [Object.assign(barisMasukKosong(), { merk: 'Angsa', jumlahKarung: '20', beratKarung: 50, hargaPerKg: '13000', varian: 'sama', kgPotong: '20' })];
var uL0 = utangSemua(); var SLB = susunSimpanMasuk(dLB, W, true); if (SLB.dokumen) terapkanKeCache(SLB.dokumen);
ok('klaim langsung (bon, tangan): bon naik TEPAT Rp12.740.000 (980 kg × 13.000), bukan nilai nota 13 jt; jejak potong 20 kg / Rp260.000 dengan alasan bawaan', !SLB.tolak && utangSemua() - uL0 === 12740000 && SLB.dokumen[0].data.potongan[0].kg === 20 && SLB.dokumen[0].data.potongan[0].rp === 260000 && SLB.dokumen[0].data.potongan[0].alasan === 'kurang timbang saat datang' && gerak(SLB.dokumen[0].data.id) === 0, J([SLB.tolak, utangSemua() - uL0]));
ok('klaim langsung: potongan yang menghabiskan baris DITOLAK; baris ditolak tidak bisa sekaligus dipotong; tanpa potongan = tanpa kolom potongan', (function () { var d = JSON.parse(J(dLB)); d.baris[0].kgPotong = '1000'; var X = susunSimpanMasuk(d, W, true); return /menghabiskan seluruh baris/.test(X.tolak || '') && !X.dokumen; })() && (function () { var d = JSON.parse(J(dLB)); d.baris[0].ditolak = '1'; d.baris[0].alasanTolak = 'apek'; d.baris.push(Object.assign(barisMasukKosong(), { merk: 'Perahu', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '14000', varian: 'sama' })); var X = susunSimpanMasuk(d, W, true); return /tidak bisa sekaligus dipotong/.test(X.tolak || ''); })() && (function () { var d = JSON.parse(J(dLB)); d.baris[0].kgPotong = ''; var X = susunSimpanMasuk(d, W, true); return !X.tolak && X.dokumen[0].data.potongan === undefined && X.dokumen[0].data.merkList[0].kgPotong === undefined && X.dokumen[0].data.merkList[0].totalKg === 1000; })());

// ---- ISI KARUNG BEBAS: bawaan 50 & 25; owner menambah 10 · 2,5 · 0,5; setelan lain di dokumen yang sama tidak hilang
terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'catatStok', tempoHari: 21 } }]);
ok('isi karung: belum diatur = 50 & 25 (bawaan, bukan milik owner); baris baru berisi 50', J(ukuranKarungPilihan()) === '[50,25]' && ukuranMilikOwner() === false && barisMasukKosong().beratKarung === 50);
var SU1 = susunTambahUkuran('2,5', W);
ok('isi karung: tambah 2,5 kg → daftar 50 · 25 · 2,5 (besar dulu) di aturanToko/catatStok; tempo bon 21 hari ikut tersalin', !SU1.tolak && SU1.dokumen.length === 1 && SU1.dokumen[0].koleksi === 'aturanToko' && SU1.dokumen[0].data.id === 'catatStok' && J(SU1.dokumen[0].data.ukuranKarung) === '[50,25,2.5]' && SU1.dokumen[0].data.tempoHari === 21, J(SU1));
terapkanKeCache(SU1.dokumen); terapkanKeCache(susunTambahUkuran('0,5', W).dokumen); terapkanKeCache(susunTambahUkuran('10', W).dokumen);
ok('isi karung: 0,5 kg dan 10 kg ikut; urutan 50 · 25 · 10 · 2,5 · 0,5; kini milik owner; tempo bon tetap 21', J(ukuranKarungPilihan()) === '[50,25,10,2.5,0.5]' && ukuranMilikOwner() === true && aturCatat().tempoHari === 21, J(ukuranKarungPilihan()));
ok('isi karung: DITOLAK dengan kalimat — bukan angka, kosong, di bawah 0,25 kg, di atas 100 kg, tiga angka di belakang koma, sudah ada', !!susunTambahUkuran('abc', W).tolak && !!susunTambahUkuran('', W).tolak && /0,25–100/.test(susunTambahUkuran('0,1', W).tolak) && /0,25–100/.test(susunTambahUkuran('150', W).tolak) && /dua angka/.test(susunTambahUkuran('2,555', W).tolak) && /sudah ada/.test(susunTambahUkuran('2,5', W).tolak) && !susunTambahUkuran('abc', W).dokumen);
// Merpati 40 karung × 2,5 kg @ Rp15.000 = 100 kg / Rp1.500.000 → buku beras per kg Merpati (bukan buku ukuran sendiri)
var dU = drafMasukKosong(W); dU.pemasok = 'PEMASOK B'; dU.caraBayar = 'tunai'; dU.baris = [Object.assign(barisMasukKosong(), { merk: 'Merpati', jumlahKarung: '40', beratKarung: 2.5, hargaPerKg: '15000', varian: 'sama' })];
var sM1 = stokKg('Merpati'); var SUm = susunSimpanMasuk(dU, W, true); var bU = SUm.dokumen ? SUm.dokumen[0].data : {};
ok('isi karung 2,5 kg (tangan): 40 karung × 2,5 = 100 kg, Rp1.500.000; masuk buku Merpati sendiri (tanpa buku ukuran), isi karung tersimpan 2,5', !SUm.tolak && bU.merkList.length === 1 && bU.merkList[0].merk === 'Merpati' && bU.merkList[0].indukUkuran === undefined && bU.merkList[0].beratKarung === 2.5 && bU.merkList[0].jumlahKarung === 40 && bU.merkList[0].totalKg === 100 && bU.merkList[0].subtotalHarga === 1500000, J([SUm.tolak, bU.merkList]));
terapkanKeCache(SUm.dokumen);
ok('isi karung 2,5 kg: stok Merpati bertambah TEPAT 100 kg; Merpati yang punya karung 50 kg tetap dibuka per 50 kg', Math.abs(stokKg('Merpati') - sM1 - 100) < 0.001 && beratKarungBuka('Merpati') === 50, J([stokKg('Merpati') - sM1, beratKarungBuka('Merpati')]));
// merek yang HANYA datang karung 10 kg: Mentik 30 × 10 kg @ Rp16.000 = 300 kg / Rp4.800.000 → isi karung yang dibuka = 10 kg
var dU2 = drafMasukKosong(W); dU2.pemasok = 'PEMASOK B'; dU2.caraBayar = 'tunai'; dU2.baris = [Object.assign(barisMasukKosong(), { merk: 'Mentik', jumlahKarung: '30', beratKarung: 10, hargaPerKg: '16000', kelasPilih: true, kelas: '' })];
var SU2 = susunSimpanMasuk(dU2, W, true); if (SU2.dokumen) terapkanKeCache(SU2.dokumen);
ok('isi karung 10 kg (tangan): Mentik 30 × 10 = 300 kg, Rp4.800.000; merek yang tidak pernah datang 50 / 25 kg → karung yang dibuka 10 kg (bukan 50)', !SU2.tolak && SU2.dokumen[0].data.merkList[0].totalKg === 300 && SU2.dokumen[0].data.merkList[0].subtotalHarga === 4800000 && stokKg('Mentik') === 300 && beratKarungBuka('Mentik') === 10 && beratKarungBuka('Angsa') === 50, J([SU2.tolak, stokKg('Mentik'), beratKarungBuka('Mentik'), beratKarungBuka('Angsa')]));
ok('isi karung: ukuran tak wajar di baris (150 kg) DITOLAK dengan kalimat; melepas ukuran tidak mengubah kedatangan lama; satu ukuran terakhir tidak bisa dilepas', (function () { var d = JSON.parse(J(dU)); d.baris[0].beratKarung = 150; return /isi karungnya 150 kg/.test(susunSimpanMasuk(d, W, true).tolak || ''); })() && (function () { var X = susunHapusUkuran(2.5, W); if (X.tolak) return false; return J(X.dokumen[0].data.ukuranKarung) === '[50,25,10,0.5]' && X.dokumen[0].data.tempoHari === 21; })() && /tidak ada di daftar/.test(susunHapusUkuran(7, W).tolak) && (function () { terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'catatStok', tempoHari: 21, ukuranKarung: [10] } }]); var t = susunHapusUkuran(10, W).tolak; var b = barisMasukKosong().beratKarung; terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'catatStok', tempoHari: 21, ukuranKarung: [50, 25, 10, 2.5, 0.5] } }]); return /minimal satu/.test(t) && b === 10; })());

var PBk = pembukaBuku(2026, W); var PBm = []; (Array.isArray(PBk) ? PBk : (PBk.dokumen || [])).forEach(function (x) { if (x.koleksi === 'batchMasuk') (x.data.merkList || []).forEach(function (m) { PBm.push(m); }); });
ok('tutup buku: merek yang hanya datang karung 10 kg dibuka dengan isi karung 10 kg (Mentik 300 kg = 30 karung), bukan 50; Angsa & Merpati tetap 50', PBm.some(function (m) { return m.merk === 'Mentik' && m.beratKarung === 10 && m.jumlahKarung === 30 && m.totalKg === 300; }) && PBm.some(function (m) { return m.merk === 'Angsa' && m.beratKarung === 50; }) && PBm.some(function (m) { return m.merk === 'Merpati' && m.beratKarung === 50; }) && !PBm.some(function (m) { return m.merk === 'Mentik' && m.beratKarung === 50; }), J(PBm.filter(function (m) { return m.merk === 'Mentik' || m.merk === 'Merpati'; })));

// ---- UANG KEMBALI DARI PEMASOK (kedatangan TUNAI, klaim / retur BELAKANGAN)
// b2 = PEMASOK B, tunai 12 Sep, Merpati 2 × 50 kg @ 15.000 = 100 kg / Rp1.500.000.
// (a) patokan kas 11 Sep (kedatangan 12 Sep BELUM termuat): retur 10 kg = Rp150.000 → kedatangan jadi 90 kg / Rp1.350.000; TANPA dokumen patokan; kas buku naik 150.000 lewat belanja hari itu
terapkanKeCache([{ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: '2026-09-11', laci: 1000000, brankas: 0, rekening: 0, amplop: 0, diubahPada: '2026-09-11T14:00:00.000Z' } }]);
var k0 = kasPada(); var sM2 = stokKg('Merpati'); var HR = hitungReturPemasok('b2', { merk: 'Merpati', kg: '10', alasan: 'berkutu' }); var SR2 = susunReturPemasok('b2', { merk: 'Merpati', kg: '10', alasan: 'berkutu' }, W);
ok('uang kembali (tangan, hari belum ditutup): retur 10 kg kedatangan tunai → Rp150.000; belanja 1.500.000 → 1.350.000; HANYA kedatangannya yang ditulis (patokan kas tidak disentuh)', HR.tunai === true && HR.dalamTitik === false && HR.rp === 150000 && HR.uangKembali === 150000 && HR.bonLama === 1500000 && HR.bonBaru === 1350000 && !SR2.tolak && SR2.dokumen.length === 1 && SR2.dokumen[0].koleksi === 'batchMasuk' && SR2.dokumen[0].data.merkList[0].totalKg === 90 && SR2.dokumen[0].data.merkList[0].subtotalHarga === 1350000 && SR2.dokumen[0].data.potongan[0].uangKembali === 150000 && SR2.dokumen[0].data.potongan[0].kePatokan === false && /masuk LACI/.test(SR2.patch.kabar) && /belum ditutup/.test(SR2.patch.kabar), J([HR, SR2.tolak, SR2.dokumen && SR2.dokumen.length]));
terapkanKeCache(SR2.dokumen);
ok('uang kembali (hari belum ditutup): kas di buku naik TEPAT Rp150.000 dan stok Merpati turun TEPAT 10 kg', kasPada() - k0 === 150000 && Math.abs(sM2 - stokKg('Merpati') - 10) < 0.001, J([kasPada() - k0, sM2 - stokKg('Merpati')]));
// (b) patokan kas maju ke 15 Sep (kedatangan 12 Sep SUDAH termuat): klaim kurang 4 kg disetujui = Rp60.000 → kedatangan 86 kg / Rp1.290.000 + patokan laci 1.000.000 → 1.060.000
terapkanKeCache([{ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: '2026-09-15', laci: 1000000, brankas: 200000, rekening: 300000, amplop: 0, diubahPada: '2026-09-15T14:00:00.000Z' } }]);
terapkanKeCache(susunCatatanPemasok('b2', { baris: [{ jenis: 'kurang', merk: 'Merpati', jumlah: '4', satuan: 'kg', ket: 'ditimbang ulang' }], cara: 'potong', status: 'disetujui', nilai: '', catatan: '' }, W).dokumen);
var k1 = kasPada(); var sM3 = stokKg('Merpati'); var HK = hitungPotongKlaim('b2'); var SK2 = susunPotongKlaim('b2', W);
var dokT = SK2.dokumen ? SK2.dokumen.filter(function (x) { return x.koleksi === 'pengaturan'; }) : []; var dokB = SK2.dokumen ? SK2.dokumen.filter(function (x) { return x.koleksi === 'batchMasuk'; }) : [];
ok('uang kembali (tangan, hari SUDAH ditutup): klaim 4 kg → Rp60.000; kedatangan 90 → 86 kg, Rp1.290.000; patokan laci 1.000.000 → 1.060.000 dalam kiriman yang sama, brankas & rekening & tanggal patokan tidak berubah, jam pasang maju 1 milidetik', !HK.tolak && HK.tunai === true && HK.dalamTitik === true && HK.rp === 60000 && !SK2.tolak && SK2.dokumen.length === 2 && dokB.length === 1 && dokT.length === 1 && dokB[0].data.merkList[0].totalKg === 86 && dokB[0].data.merkList[0].subtotalHarga === 1290000 && dokT[0].data.id === 'titikKas' && dokT[0].data.laci === 1060000 && dokT[0].data.brankas === 200000 && dokT[0].data.rekening === 300000 && dokT[0].data.tanggal === '2026-09-15' && dokT[0].data.diubahPada === '2026-09-15T14:00:00.001Z' && dokB[0].data.potongan[1].uangKembali === 60000 && dokB[0].data.potongan[1].kePatokan === true && dokB[0].data.klaim.status === 'selesai' && dokB[0].data.klaim.dibukukan.rp === 60000 && /patokan laci/.test(SK2.patch.kabar), J([HK.tolak, SK2.tolak, SK2.dokumen]));
terapkanKeCache(SK2.dokumen);
ok('uang kembali (hari sudah ditutup): kas di buku naik TEPAT Rp60.000 (lewat patokan laci), stok Merpati turun TEPAT 4 kg; klaim yang sudah dibukukan tidak bisa dibukukan lagi', kasPada() - k1 === 60000 && Math.abs(sM3 - stokKg('Merpati') - 4) < 0.001 && /sudah dibukukan/.test(susunPotongKlaim('b2', W).tolak || ''), J([kasPada() - k1, sM3 - stokKg('Merpati'), susunPotongKlaim('b2', W).tolak]));
ok('uang kembali: kedatangan BON tidak pernah menyentuh patokan kas; patokan bentuk lama (tanpa jam pasang) DITOLAK dengan kalimat, tanpa dokumen', (function () { var X = susunReturPemasok(idL === undefined ? 'x' : SLB.dokumen[0].data.id, { merk: 'Angsa', kg: '10', alasan: 'apek sekali' }, W); return !X.tolak && X.dokumen.every(function (d) { return d.koleksi !== 'pengaturan'; }) && X.hitung.tunai === false; })() && (function () { terapkanKeCache([{ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: '2026-09-15', laci: 1060000, brankas: 200000, rekening: 300000, amplop: 0 } }]); var X = susunReturPemasok('b2', { merk: 'Merpati', kg: '5', alasan: 'berkutu' }, W); terapkanKeCache([{ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: '2026-09-15', laci: 1060000, brankas: 200000, rekening: 300000, amplop: 0, diubahPada: '2026-09-15T14:00:00.001Z' } }]); return /bentuk lama/.test(X.tolak || '') && !X.dokumen; })());
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
       ('Tahap 1: isian ongkos kirim di kepala lembar', 'data-ketik="mKetik" data-kolom="ongkir"'),
       ('Tahap 1: isian timbang sampel (jumlah karung)', 'data-kolom="sampelKarung" data-i="${i}"'),
       ('Tahap 1: isian berat sampel', 'data-kolom="sampelKg" data-i="${i}"'),
       ('Tahap 1: pil kelas mutu & isian rinci per baris', 'data-k="mc-rinci-${i}"'),
       ('Tahap 1: kartu catatan untuk pemasok tampil saat kedatangan dibuka', "${koreksi ? gambarCatatanPemasok(s, d.id) : ''}"),
       ('Tahap 1: simpan catatan lewat satu pintu logika', 'await tulis(C.susunCatatanPemasok(d.id, d, waktu()))'),
       ('Tahap 2: menyimpan klaim DISEBUT belum mengubah bon, stok, atau uang', 'Menyimpan klaim ini BELUM mengubah bon, stok, atau uang.'),
       ('Tahap 2: tombol BUKUKAN potong bon dua ketukan + pratinjau', "data-aksi=\"ptKlaim\" data-id=\"${id}\" data-k=\"pt-bukukan\""),
       ('Tahap 2: bukukan lewat satu pintu logika', 'await tulis(C.susunPotongKlaim(id, waktu()))'),
       ('Tahap 2: retur ke pemasok lewat satu pintu logika + pratinjau dulu', 'await tulis(C.susunReturPemasok(d.id, d, waktu()))'),
       ('Tahap 2: tombol tolak per baris + alasan', 'data-kolom="alasanTolak" data-i="${i}"'),
       ('Tahap 2: catatan bebas di lembar barang masuk', 'data-ketik="mKetik" data-kolom="catatanBebas"'),
       ('Tahap 2: catatan bebas di lembar catatan pemasok', 'data-ketik="cpKetik" data-kolom="bebas"'),
       ('Tahap 2: layar menyebut APA yang mengubah stok & bon', 'Catatan dan klaim tidak mengubah stok, modal, bon, atau uang — yang mengubah hanya "BUKUKAN" dan "kembalikan ke pemasok" di atas.'),
       ('Tahap 3: isian kg dipotong langsung per baris (owner & tablet)', 'data-ketik="mKetik" data-kolom="kgPotong" data-i="${i}"'),
       ('Tahap 3: selisih timbang bisa dipakai sebagai potongan', 'data-aksi="mPotongTimbang" data-i="${i}" data-kg="${sel}"'),
       ('Tahap 3: pilihan isi karung dari daftar owner', 'const L = C.ukuranKarungPilihan(); const kini = Number(r.beratKarung);'),
       ('Tahap 3: tambah isi karung lewat satu pintu logika', 'await tulis(C.susunTambahUkuran(st().ukKetik, waktu()))'),
       ('Tahap 3: lepas isi karung lewat satu pintu logika', 'await tulis(C.susunHapusUkuran(n, waktu()))'),
       ('Tahap 3: lembar owner memasang Atur isi karung', '${gambarAturUkuran(s)}'),
       ('Tahap 3: kedatangan tunai — layar menyebut uang kembali masuk laci & patokan', "'Uang kembali ' + RP(H.rp) + ' masuk LACI — ketuk SESUDAH uangnya diterima. '"),
       ('Tahap 3: retur terbuka untuk kedatangan tunai', "${!K.kunci ? gambarRetur(s, id, K) : ''}"),
       ('Tahap 3: tablet punya isian ongkos kirim (titipan)', 'data-k="mt-ongkir"'),
       ('Tahap 3: tablet punya catatan bebas untuk pemasok', 'data-k="mt-bebas"'),
       ('Tahap 3: tablet bisa menolak baris', '${pilTolak(d.baris[i], i)}'),
       ('Tahap 1: tombol surat siap cetak membuka dokumen kecil pemasok', "jenis: 'pemasok', pilih: String(id)"),
       ('Tahap 1: ambang mutu per kelas bisa diatur owner', 'await tulis(C.susunAturMutuKelas(a, waktu()))'),
       ('buku kedatangan menandai timbang & mutu', "${k.cek && k.cek.teks ? ' · ' + k.cek.teks : ''}")]


def statis(teks):
    return [n for n, pot in POT if pot not in teks]


RUSAK = {
    'Tahap 3: klaim langsung tanpa jejak potongan': ("if (!lama && h.potongKg > 0) { const pl = h.sah.filter((b) => b.kgPotong > 0);", "if (false) { const pl = h.sah.filter((b) => b.kgPotong > 0);"),
    'Tahap 3: koreksi kedatangan menulis jejak potongan kedua': ("if (!lama && h.potongKg > 0) { const pl", "if (h.potongKg > 0) { const pl"),
    'Tahap 3: isi karung pecahan ditolak': ("const ukSah = (n) => isFinite(n) && n >= UK_BATAS.min &&", "const ukSah = (n) => isFinite(n) && n >= 1 &&"),
    'Tahap 3: isi karung tak wajar lolos': ("        : !(berat >= UK_BATAS.min && berat <= UK_BATAS.maks) ? 'isi karungnya '", "        : false ? 'isi karungnya '"),
    'Tahap 3: menambah ukuran membuang setelan lain': ("return Object.assign({}, lama, { id: 'catatStok', ukuranKarung: daftar.slice()", "return Object.assign({}, { id: 'catatStok', ukuranKarung: daftar.slice()"),
    'Tahap 3: merek karung 10 kg tetap dibuka 50 kg': ("return ukuranLainTerakhir()[asal] || KARUNG_BELAKANG_KG; }", "return KARUNG_BELAKANG_KG; }"),
    'Tahap 3: tutup buku membuka merek karung 10 kg sebagai karung 50 kg': ("!merkPunyaKarungBerat(x.merk, 50) && ukLain(x.merk)) || 50; merkList.push(", "false) || 50; merkList.push("),
    'Tahap 3: uang kembali — patokan laci tidak dinaikkan (hari sudah ditutup)': ("if (H.dalamTitik) { const t = ambilTitikKas(); dokumen.push(", "if (false) { const t = ambilTitikKas(); dokumen.push("),
    'Tahap 3: uang kembali — patokan dinaikkan padahal hari belum ditutup': ("out.dalamTitik = !!out.titik && String(b.tanggal || '') <= out.titik;", "out.dalamTitik = !!out.titik;"),
    'Tahap 3: uang kembali — patokan naik tanpa memajukan jam pasang (salinan perangkat menang)': ("laci: (Number(t.laci) || 0) + H.rp, diubahPada: ptMajuSedikit(t.diubahPada) })", "laci: (Number(t.laci) || 0) + H.rp })"),
    'Tahap 3: kedatangan tunai ditolak lagi': ("  out.tunai = b.caraBayar !== 'utang';", "  out.tunai = b.caraBayar !== 'utang'; if (out.tunai) return Object.assign(out, { tolak: 'TUNAI' });"),
    'kosong dianggap timbang 0 (selisih = −nota)': ("const timbang = tb !== null ? ckB2(tb) : pakaiSampel ? hasil.sampel.perkiraanKg : null;", "const timbang = tb !== null ? ckB2(tb) : pakaiSampel ? hasil.sampel.perkiraanKg : 0;"),
    'sampel: perkiraan memakai berat label, bukan rata-rata sampel': ("perkiraanKg: jmlKarung > 0 ? ckB2(rata * jmlKarung) : null,", "perkiraanKg: jmlKarung > 0 ? ckB2(label * jmlKarung) : null,"),
    'sampel: perkiraan ditulis sebagai timbang seluruh baris': ("if (tb !== null) hasil.kolom.timbangKg = timbang;", "if (timbang !== null) hasil.kolom.timbangKg = timbang;"),
    'sampel: perkiraan tidak ditandai perkiraan': ("hasil.perkiraan = !!pakaiSampel;", "hasil.perkiraan = false;"),
    'sampel: mengalahkan timbang seluruh baris': ("const timbang = tb !== null ? ckB2(tb) : pakaiSampel ? hasil.sampel.perkiraanKg : null;", "const timbang = hasil.sampel && hasil.sampel.perkiraanKg !== null ? hasil.sampel.perkiraanKg : tb !== null ? ckB2(tb) : null;"),
    'mutu rinci: ambang kelas diabaikan': ("if (v === null || v === undefined || !(maks > 0) || !(v > maks)) return;", "return;"),
    'mutu rinci: tanpa ambang (0) dianggap lewat': ("if (v === null || v === undefined || !(maks > 0) || !(v > maks)) return;", "if (v === null || v === undefined || !(v > maks)) return;"),
    'mutu rinci: ambang owner per kelas diabaikan': ("o[k][id] = isFinite(n) && n >= 0 && n <= maks ? n : TM_KELAS_BAWAAN[k][id];", "o[k][id] = TM_KELAS_BAWAAN[k][id];"),
    'ongkos kirim tidak masuk modal': ("subtotalHarga: Number(m.subtotalHarga) || 0 }))), bongkar + ongkir);", "subtotalHarga: Number(m.subtotalHarga) || 0 }))), bongkar);"),
    'ongkos kirim tidak ditulis ke yang dibaca mesin': ("pemasok, biayaBongkar: h.bongkar + h.ongkir, caraBayar: cara,", "pemasok, biayaBongkar: h.bongkar, caraBayar: cara,"),
    'ongkos kirim: draf koreksi menggandakan (bongkar masih memuat ongkir)': ("bongkar: String((Number(b.biayaBongkar) || 0) - ckOngkir(b)), ongkir:", "bongkar: String(Number(b.biayaBongkar) || 0), ongkir:"),
    'catatan pemasok mengubah baris nota (uang ikut berubah)': ("const data = Object.assign({}, lama); if (bebasBaru) data.catatanBebas = bebasBaru;", "const data = Object.assign({}, lama, { merkList: (lama.merkList || []).map((m) => Object.assign({}, m, { subtotalHarga: (m.subtotalHarga || 0) - 1000 })) }); if (bebasBaru) data.catatanBebas = bebasBaru;"),
    'catatan pemasok: kurang tanpa jumlah diterima': ("if (jenis !== 'mutu' && n === null) return", "if (false) return"),
    'klaim: nilai kosong tidak diisi dari timbang': ("nilai: nv === null ? (cara === 'catat' ? 0 : T.nilaiKurang) : nv,", "nilai: nv === null ? 0 : nv,"),
    'koreksi kedatangan menghapus catatan pemasok': ("'merekBaru', 'bongkarTitipan', 'catatanPemasok', 'klaim', 'potongan', 'ditolak'].indexOf(k) >= 0)", "'merekBaru', 'bongkarTitipan'].indexOf(k) >= 0)"),
    'surat pemasok: nilai klaim tidak dicetak': ("C.klaim.cara === 'catat' || !C.klaim.nilai ? '' : C.klaim.nilai,", "'',"),
    'surat pemasok: kedatangan tanpa catatan tetap dicetak': ("if (!C.ada) tolak = 'Kedatangan ini belum punya catatan untuk pemasok", "if (false) tolak = 'Kedatangan ini belum punya catatan untuk pemasok"),
    'surat pemasok: hasil timbang tidak dicetak': ("if (x.timbangKg !== null) baris.push(brs('   ' + (x.perkiraan ?", "if (false) baris.push(brs('   ' + (x.perkiraan ?"),
    'potong bon: nilai baris tidak ikut turun (bon tetap)': ("kgPotong: potong, subtotalHarga: Math.round(kgBuku * harga), terisi,", "kgPotong: potong, subtotalHarga: Math.round(jumlah * berat * harga), terisi,"),
    'potong bon: kg buku tidak ikut turun (stok tetap)': ("const kgBuku = ckB2(jumlah * berat - potong);", "const kgBuku = ckB2(jumlah * berat);"),
    'potong bon: kolom kgPotong tidak ditulis (koreksi berikutnya mengembalikan kg)': ("b.kgPotong > 0 ? { kgPotong: b.kgPotong } : {}))", "{}))"),
    'potong bon: klaim belum disetujui boleh dibukukan': ("if (C.klaim.status !== 'disetujui') return { tolak: 'Baru dibukukan sesudah pemasok SETUJU", "if (false) return { tolak: 'Baru dibukukan sesudah pemasok SETUJU"),
    'potong bon: bisa dibukukan dua kali': ("if (C.klaim.dibukukan) return { tolak: 'Klaim ini sudah dibukukan '", "if (false) return { tolak: 'Klaim ini sudah dibukukan '"),
    'potong bon: baris "tertinggal" ikut dipotong': ("return C.catatan.filter((c) => c.jenis === 'kurang' && c.jumlah > 0)", "return C.catatan.filter((c) => c.jumlah > 0)"),
    'potong bon: timbang dibanding kg sesudah potong (nota asli hilang)': ("tmBaris(m, ckB2((Number(m.totalKg) || 0) + (Number(m.kgPotong) > 0 ? Number(m.kgPotong) : 0)), Number(m.hargaPerKg) || 0, A)));", "tmBaris(m, Number(m.totalKg) || 0, Number(m.hargaPerKg) || 0, A)));"),
    'retur: tanpa alasan diterima': ("if (jenis === 'retur' && ket.length < 5) return", "if (false) return"),
    'retur: potongan kedua menimpa yang pertama (kgPotong tidak dijumlah)': ("draf.baris[x.i].kgPotong = String(ckB2(x.kgSudah + x.kgPotong)).replace('.', ',');", "draf.baris[x.i].kgPotong = String(ckB2(x.kgPotong)).replace('.', ',');"),
    'retur: jejak potongan tidak dicatat': ("data.potongan = (Array.isArray(lama.potongan) ? lama.potongan : []).concat([Object.assign({ jenis,", "data.potonganX = (Array.isArray(lama.potongan) ? lama.potongan : []).concat([Object.assign({ jenis,"),
    'tolak saat datang: baris ditolak tetap masuk stok & bon': ("ditolak, alasanTolak, sah: terisi && !masalah && !ditolak,", "ditolak, alasanTolak, sah: terisi && !masalah,"),
    'tolak saat datang: tanpa alasan diterima': ("ditolak && alasanTolak.length < 3 ? 'baris ini ditolak — tulis alasannya' :", "false ? 'baris ini ditolak — tulis alasannya' :"),
    'tolak saat datang: baris yang ditolak tidak dicatat': ("if (h.ditolak.length) data.ditolak = h.ditolak.map(", "if (false) data.ditolak = h.ditolak.map("),
    'catatan bebas tidak disimpan dari lembar barang masuk': ("if (bebas) data.catatanBebas = bebas;", ""),
    'catatan bebas tidak tercetak di surat': ("if (C.bebas.trim()) { baris.push(brs('Catatan', '', undefined, 'kel'));", "if (false) { baris.push(brs('Catatan', '', undefined, 'kel'));"),
    'usul catatan tidak dibaca dari timbang': ("const usul = K.baris.filter((x) => x.selisihKg !== null && Math.abs(x.selisihKg) > 0.004)", "const usul = K.baris.filter((x) => false)"),
    'timbang mengubah kg buku': ("hargaPerKg: harga, totalKg: kgBuku, kgNota: ckB2(jumlah * berat),", "hargaPerKg: harga, totalKg: cek.timbangKg !== null ? cek.timbangKg : kgBuku, kgNota: ckB2(jumlah * berat),"),
    'kolom timbang & mutu tidak ditulis': (".map((r, i) => Object.assign(r, h.sah[i].cek.kolom))", ".map((r) => r)"),
    'kolom kosong ikut ditulis (bentuk lama berubah)': ("if (tb !== null) hasil.kolom.timbangKg = timbang;", "hasil.kolom.timbangKg = timbang;"),
    'koreksi tidak membawa isian': ("{ kgPotong: String(m.kgPotong).replace('.', ',') } : {}, tmDraf(m)))", "{ kgPotong: String(m.kgPotong).replace('.', ',') } : {}))"),
    'ambang kadar air owner diabaikan': ("kadarAirMaks: airMilik ? Number(a.kadarAirMaks) : ATUR_CATAT_BAWAAN.kadarAirMaks", "kadarAirMaks: ATUR_CATAT_BAWAAN.kadarAirMaks"),
    'ambang butir patah owner diabaikan': ("patahMaks: patahMilik ? Number(a.patahMaks) : ATUR_CATAT_BAWAAN.patahMaks", "patahMaks: ATUR_CATAT_BAWAAN.patahMaks"),
    'kadar air di atas ambang tidak ditandai': ("if (hasil.kadarAir !== null && hasil.kadarAir > A.kadarAirMaks) hasil.awas.push(", "if (false) hasil.awas.push("),
    'kutu ada tidak ditandai': ("if (kutu === 'ada') hasil.awas.push('ada kutu');", ""),
    'bau apek tidak ditandai': ("if (bau === 'apek') hasil.awas.push('bau apek');", ""),
    'butir patah di atas ambang tidak ditandai': ("if (hasil.butirPatah !== null && hasil.butirPatah > A.patahMaks) hasil.awas.push(", "if (false) hasil.awas.push("),
    'kadar air mustahil diterima': (": air !== null && !(air >= 0 && air <= 100) ?", ": false ?"),
    'ketikan bukan angka dianggap 0': (r"if (!/^[\d.,]*\d[\d.,]*$/.test(t)) return NaN;", "return ckAngka(t);"),   # jangkar disesuaikan tinjauan no. 13
    'tinjauan no. 13: pemisah ganda / di ujung ("15,,5") dianggap 0 %': ("const n = ckUbah(t); return isFinite(n) ? n : NaN; };", "const n = ckUbah(t); return isFinite(n) ? n : 0; };"),
    'tinjauan no. 22: simpan Atur menulis ambang bawaan jadi "setelan owner"': ("tetap: kini.mutuBawaan[k] && ckB2(n) === kini[k] }", "tetap: false }"),
    'tinjauan no. 22: kolom mutu kosong ditulis angka sekarang': ("if (ckKosong(isi[k])) return { nilai: kini[k], tetap: true };", "if (ckKosong(isi[k])) return { nilai: kini[k], tetap: false };"),
    'masalah isian tidak menghalangi simpan': ("hapus barisnya atau kurangi potongannya' : cek.masalah;", "hapus barisnya atau kurangi potongannya' : '';"),
    'baris cek tanpa nama dibuang diam-diam': ("const terisi = !!merk || jumlah > 0 || harga > 0 || cek.ada;", "const terisi = !!merk || jumlah > 0 || harga > 0;"),
    'rekap: kedatangan sebagian dihitung ditimbang': ("if (K.ditimbang === K.nBaris) p.ditimbang += 1; else if (K.ditimbang > 0) p.sebagian += 1;", "if (K.ditimbang > 0) p.ditimbang += 1; else if (false) p.sebagian += 1;"),
    'rekap: nilai kurang tanpa harga baris': ("hasil.nilaiKurang = Math.round(hasil.kgKurang * (Number(harga) || 0));", "hasil.nilaiKurang = Math.round(hasil.kgKurang);"),
    'rekap: belum ditimbang digambar 0 %': ("p.persenRata = p.kgNota > 0 ? Math.round(p.selisihKg / p.kgNota * 1000) / 10 : null;", "p.persenRata = p.kgNota > 0 ? Math.round(p.selisihKg / p.kgNota * 1000) / 10 : 0;"),
    'rekap: kedatangan tanpa nama pemasok dibuang': ("const pem = String(b.pemasok || '').trim() || '(tanpa nama pemasok)';", "const pem = String(b.pemasok || '').trim(); if (!pem) return;"),
    'rekap: kelompok tanpa nama pemasok tidak di bawah': ("tanpaNama(x) - tanpaNama(y) || ", ""),
    'atur: ambang mutu tidak disimpan': ("if (!ka.tetap) data.kadarAirMaks = ka.nilai;", ""),   # jangkar disesuaikan tinjauan no. 22 (penulisan kolom mutu kini bersyarat)
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
