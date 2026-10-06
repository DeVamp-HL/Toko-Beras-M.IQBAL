#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_jual_nego.py — owner 7 Okt 2026, JS2-C "Buku Nego" (rancangan dikunci owner 18 Sep): BATAS NEGO PER ORANG di layar Jual. KOTAK PASIR (angka & nama
CONTOH), jsc saja, TANPA peramban.
  · setelan: jatah = % MARGIN barang per peran (owner 100 tetap, Ben 50, karyawan 0) dan per akun, siapa boleh di bawah modal, langkah batas — bawaan rancangan,
    dokumen aturanToko/peran (Menu › Sistem › Peran › Atur) menimpanya; ngAtur (nego-logika) = ssAtur/ssPeran (sistem-logika) satu sumber; Atur menolak angka asing;
  · batas = katalog − margin × jatah, naik ke kelipatan langkah, tidak di atas katalog; jatah penuh = modal; modal belum tercatat = belum bisa dihitung;
  · putusan: owner sampai modal sendiri, di bawah modal hanya dengan alasan; Ben dalam jatah sendiri, di bawah jatah MINTA OWNER (harga nota tetap), di bawah modal
    hanya bila diizinkan + alasan dan tetap lewat owner; kisi "tidak boleh" → ditolak; karyawan tanpa jatah → tombol nego mati;
  · alur: tawar → minta owner (dokumen persetujuan tindakan 'nego') → owner memutus lewat papan persetujuan yang sama → harga dipakai SEKALI (negoSetujuId); baris
    bernego yang dibangun ulang diputus lagi; tiap nego tercatat di baris nota (negoSelisih, negoStatus, negoBatas, negoJatah, negoAlasan, negoSetujuId);
  · penjaga kiriman: Ben dalam jatah lolos, permintaan nego ditolak selama rules belum membuka koleksi persetujuan (bentuknya sudah dijaga bila dibuka);
  · Buku Nego: tiap nego hari ini + permintaan yang menunggu, total potongan; layar & Atur memakai rumus yang sama (statis).

    python3 alat-uji/uji_jual_nego.py            → N lulus · 0 gagal
    python3 alat-uji/uji_jual_nego.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, peta_akses, uji_jual_baru, uji_wadah_bernama, uji_cache_chip_literan, uji_rak_inkremental  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = peta_akses.MODUL_KIRIM + [m for m in uji_jual_baru.MODUL if m not in peta_akses.MODUL_KIRIM] + ['baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/sistem-logika.js', 'baru/js/layar/akses-layar.js']
SUMBER = {'jual': 'baru/js/layar/jual.js', 'menu': 'baru/js/layar/menu.js', 'app': 'baru/js/app.js'}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
var J = function (x) { return JSON.stringify(x); };
var nId = 7000; var W = { tanggal: '2026-10-07', jam: '10:00', kini: '2026-10-07T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
var BEN = keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true });
var KRY = keadaanAkun('kry.contoh@tokoberasmiqbal.web.app', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true });
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
pasok('aksesAkun', [{ id: 'uid-ben', uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true }, { id: 'uid-kry', uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true }]);
setelSumber('cadangan', 'kotak pasir');
var hak = function (akun) { return Object.assign({}, (ssAtur('peran').hak || {})[akun.peran] || {}, { jatahNego: ngJatah(akun) }); };   // = app.js setelSumberHak
var kirim = function (akun, dok) { return periksaKiriman(akun, (dok || []).map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false, lama: null }; }), [], hak(akun), new Date('2026-10-07T10:00:00+07:00')); };
// baris contoh: karung 50 kg katalog 690.000, modal 650.000 per karung (2 karung)
var KRG = function (ubah) { return Object.assign({ jenis: 'karung', merkSumber: 'Merek Contoh', jumlahKarung: 2, beratKarungAcuan: 50, totalKg: 100, namaProduk: 'Merek Contoh (karung utuh)', hppTotalSaatJual: 1300000,
  label: 'Merek Contoh 50 kg', satuan: 'karung', jumlah: 2, hargaAsli: 690000, hargaSatuan: 690000, hargaTotal: 1380000 }, ubah || {}); };

// ---- A · bawaan & setelan (satu sumber)
var A0 = ngAtur();
ok('A: bawaan rancangan JS2 — owner 100 %, Ben 50 %, karyawan 0 %, langkah Rp500, di bawah modal: owner', A0.jatah.owner === 100 && A0.jatah.ben === 50 && A0.jatah.karyawan === 0 && A0.langkah === 500 && J(A0.bawahModal) === '["owner"]', J(A0));
var P0 = ssPeran(); var S0 = ssAtur('peran');
ok('A: Menu › Sistem › Peran membaca angka yang SAMA (ssAtur/ssPeran = ngAtur): jatah Ben 50, karyawan 0, langkah 500, bawah modal [owner]', P0.jatahBen === A0.jatah.ben && P0.jatahKaryawan === A0.jatah.karyawan && S0.langkahNego === A0.langkah && J(S0.bawahModal) === J(A0.bawahModal), J([P0.jatahBen, P0.jatahKaryawan, S0.langkahNego, S0.bawahModal]));
pasok('aturanToko', [{ id: 'peran', hak: S0.hak, batasSekaligus: 300000, jatahBen: 40, jatahKaryawan: 10, jatahAkun: { 'uid-ben': 60 }, bawahModal: ['owner', 'uid:uid-ben'], langkahNego: 1000, jejak: [] }]);
var A1 = ngAtur();
ok('A: setelan owner: jatah akun Ben 60 % MENANG atas peran Ben 40 %; karyawan 10 %; Ben boleh di bawah modal (uid); langkah Rp1.000; owner tetap 100', ngJatah(BEN) === 60 && ngJatah(KRY) === 10 && ngJatah(OWN) === 100 && ngBolehBawahModal(BEN) && !ngBolehBawahModal(KRY) && A1.langkah === 1000, J([ngJatah(BEN), ngJatah(KRY), A1]));
ok('A: ssPeran menampilkan setelan yang sama (jatah karyawan 10, per akun Ben 60)', ssPeran().jatahKaryawan === 10 && ssPeran().jatahAkun['uid-ben'] === 60, J(ssPeran().jatahAkun));
var at1 = susunAturSistem('peran', { jatahKaryawan: '120' }, W), at2 = susunAturSistem('peran', { jatahAkun: { 'uid-ben': 'x' } }, W);
var at3 = susunAturSistem('peran', { jatahAkun: { 'uid-ben': '', 'uid-kry': '25' }, bawahModal: ['owner', 'ben', 'uid:uid-kry', 'uid-kry', 'tamu', 'owner'], langkahNego: '500' }, W);
ok('A: Atur menolak jatah karyawan 120 % dan jatah akun bukan angka; kosong = ikut peran (tidak ditulis); bawah modal disaring ke kunci dikenal tanpa ganda; setelan lain tetap',
  /jatahKaryawan harus 0–100/.test(at1.tolak || '') && /0–100 %/.test(at2.tolak || '') && !at3.tolak && J(at3.dokumen[0].data.jatahAkun) === '{"uid-kry":25}' && J(at3.dokumen[0].data.bawahModal) === '["owner","ben","uid:uid-kry"]'
  && at3.dokumen[0].data.jatahBen === 40 && at3.dokumen[0].data.langkahNego === 500 && at3.dokumen[0].data.batasSekaligus === 300000, J([at1, at2, at3.dokumen && at3.dokumen[0].data]));
var putar = susunPutarHak('ben', 'nego', W);
ok('A: memutar satu hak di kisi tidak menghapus setelan nego (jatah, per akun, bawah modal, langkah ikut tertulis)', putar.dokumen && putar.dokumen[0].data.jatahKaryawan === 10 && putar.dokumen[0].data.jatahAkun['uid-ben'] === 60 && putar.dokumen[0].data.langkahNego === 1000 && J(putar.dokumen[0].data.bawahModal) === '["owner","uid:uid-ben"]', J(putar.dokumen && putar.dokumen[0].data));
pasok('aturanToko', []);

// ---- B · batas
ok('B: batas = katalog − margin × jatah: 690.000 / modal 650.000 / 50 % → 670.000', ngBatas(690000, 650000, 50, 500) === 670000);
ok('B: dibulatkan ke langkah KE ATAS (tidak melewati jatah): 33 % → 676.800 → 677.000; langkah 1.000 → 677.000; langkah 5.000 → 680.000', ngBatas(690000, 650000, 33, 500) === 677000 && ngBatas(690000, 650000, 33, 1000) === 677000 && ngBatas(690000, 650000, 33, 5000) === 680000, J([ngBatas(690000, 650000, 33, 500), ngBatas(690000, 650000, 33, 5000)]));
ok('B: tidak pernah di atas katalog (margin Rp50, langkah 500 → 13.700); jatah 100 = modal dibulatkan ke rupiah (13.216,7 → 13.217); margin ≤ 0 → katalog; modal belum tercatat → null',
  ngBatas(13700, 13650, 50, 500) === 13700 && ngBatas(13800, 13216.7, 100, 500) === 13217 && ngBatas(690000, 700000, 50, 500) === 690000 && ngBatas(690000, null, 50, 500) === null, J([ngBatas(13700, 13650, 50, 500), ngBatas(13800, 13216.7, 100, 500)]));
ok('B: modal per satuan = modal baris ÷ satuan keluar (kemasan: + bonus) — 198.000 / (2 + 1 bonus) = 66.000; karung 1.300.000 / 2 = 650.000; tanpa modal = null', ngModalSatuan({ jenis: 'kemasan', jumlah: 2, bonusUnit: 1, hppTotalSaatJual: 198000 }) === 66000 && ngModalSatuan(KRG()) === 650000 && ngModalSatuan(KRG({ hppTotalSaatJual: 0 })) === null);

// ---- C · owner
var po = function (h, o) { return ngPutus(KRG(), h, OWN, o); };
ok('C: owner 680.000 & 650.000 (= modal) → dalam jatah / sampai modal; 690.000 → kembali ke katalog; 700.000 → di atas katalog; Rp400 → ditolak lantai',
  po(680000).status === 'jatah' && po(650000).status === 'jatah' && /sampai modal/.test(po(650000).teks) && po(690000).status === 'katalog' && po(700000).status === 'naik' && po(400).status === 'tolak' && /paling rendah Rp500/.test(po(400).teks), J([po(650000), po(400).teks]));
ok('C: owner di bawah modal TANPA alasan → perluAlasan, kalimat menyebut modal & rugi per karung; DENGAN alasan → bawahModal (alasannya ikut)',
  po(640000).status === 'perluAlasan' && /modal Rp650\.000, rugi Rp10\.000\/karung/.test(po(640000).teks) && po(640000, { alasan: 'karung sobek' }).status === 'bawahModal' && po(640000, { alasan: 'karung sobek' }).alasan === 'karung sobek' && po(640000).dibawahModal, J(po(640000)));
pasok('aturanToko', [{ id: 'peran', bawahModal: [] }]);
ok('C: owner mencabut dirinya dari "boleh di bawah modal" → owner pun DITOLAK di bawah modal', po(640000, { alasan: 'x' }).status === 'tolak' && /tidak diizinkan/.test(po(640000, { alasan: 'x' }).teks), J(po(640000, { alasan: 'x' })));
pasok('aturanToko', []);
ok('C: modal belum tercatat → owner boleh (diberi tahu batas belum bisa dihitung)', ngPutus(KRG({ hppTotalSaatJual: 0 }), 600000, OWN).status === 'jatah' && /belum tercatat/.test(ngPutus(KRG({ hppTotalSaatJual: 0 }), 600000, OWN).teks));

// ---- D · Ben (jatah 50 %, kisi bawaan "minta owner")
var pb = function (h, o) { return ngPutus(KRG(), h, BEN, Object.assign({ hakNego: 'owner' }, o || {})); };
ok('D: Ben 670.000 = batas jatah → sendiri; 669.500 → MINTA OWNER, kalimat menyebut jatah 50 % & paling rendah Rp670.000', pb(670000).status === 'jatah' && pb(670000).batas === 670000 && pb(669500).status === 'minta' && /jatah Ben Contoh \(50 % margin · paling rendah Rp670\.000\) — minta owner/.test(pb(669500).teks), J(pb(669500)));
ok('D: Ben di bawah modal (tidak diizinkan) → DITOLAK tanpa menyebut angka modal', pb(640000).status === 'tolak' && /di bawah modal/.test(pb(640000).teks) && !/650\.000/.test(pb(640000).teks), pb(640000).teks);
ok('D: kisi Ben "tidak boleh" → di bawah jatah DITOLAK; dalam jatah tetap boleh', pb(669500, { hakNego: 'tidak' }).status === 'tolak' && /tidak boleh nego di bawah jatah/.test(pb(669500, { hakNego: 'tidak' }).teks) && pb(675000, { hakNego: 'tidak' }).status === 'jatah');
ok('D: modal belum tercatat → Ben MINTA OWNER (jatah tidak bisa dihitung)', ngPutus(KRG({ hppTotalSaatJual: 0 }), 680000, BEN, { hakNego: 'owner' }).status === 'minta');
pasok('aturanToko', [{ id: 'peran', bawahModal: ['owner', 'ben'] }]);
ok('D: Ben DIIZINKAN di bawah modal: tanpa alasan → perluAlasan; dengan alasan → tetap MINTA OWNER (alasan ikut permintaan)', pb(640000).status === 'perluAlasan' && pb(640000, { alasan: 'beras basah' }).status === 'minta' && pb(640000, { alasan: 'beras basah' }).alasan === 'beras basah');
pasok('aturanToko', []);
var SET = { id: 'ps-uji', hargaMinta: 660000 };
ok('D: persetujuan owner 660.000: Ben mengetik 665.000 → DISETUJUI (setujuId); 655.000 (lebih rendah dari yang disetujui) → minta lagi', pb(665000, { setuju: SET }).status === 'disetujui' && pb(665000, { setuju: SET }).setujuId === 'ps-uji' && pb(655000, { setuju: SET }).status === 'minta', J(pb(665000, { setuju: SET })));

// ---- E · karyawan tanpa jatah
ok('E: karyawan (jatah 0 %, kisi "tidak") → tombol nego MATI dengan kalimat jatah; Ben & owner terbuka; karyawan berjatah 10 % → terbuka',
  !ngBolehNego(KRY, 'tidak').boleh && /tidak punya jatah nego/.test(ngBolehNego(KRY, 'tidak').kalimat) && ngBolehNego(BEN, 'owner').boleh && ngBolehNego(OWN, 'sendiri').boleh
  && (pasok('aturanToko', [{ id: 'peran', jatahKaryawan: 10 }]), ngBolehNego(KRY, 'tidak').boleh) && (pasok('aturanToko', []), true));
ok('E: karyawan menurunkan harga sedikit pun (jatah 0) → DITOLAK', ngPutus(KRG(), 689500, KRY, { hakNego: 'tidak' }).status === 'tolak');

// ---- F · alur di keranjang (logika Jual): Ben menawar, minta owner, owner memutus, dipakai sekali
var s = keadaanAwal(); s.sekarang = new Date('2026-10-07T10:00:00+07:00');
var terap = function (p) { s = Object.assign({}, s, p || {}); sinkronKeranjang(s); return p; };
terap({ negoAkun: BEN, negoHak: 'owner' });
var rak = susunRak(s); var cA = rak.karung.filter(function (c) { return c.kunci === 'Angsa' && c.berat === 50; })[0];
terap(masukkan(Object.assign({}, s, { pilih: cA }), 2)); var idA = s.keranjang[0].id; var t0 = s.keranjang[0].trx;
var modalA = ngModalSatuan(t0), batasA = ngBatas(t0.hargaAsli, modalA, 50, 500);
terap(terapkanNego(s, idA, batasA));
var tA = s.keranjang[0].trx;
ok('F: Ben menawar Angsa 50 kg ke batas jatahnya → harga dipakai; baris bertanda negoStatus jatah, negoBatas, negoJatah 50', tA.hargaSatuan === batasA && tA.nego && tA.negoStatus === 'jatah' && tA.negoBatas === batasA && tA.negoJatah === 50 && tA.hargaTotal === batasA * 2, J([batasA, tA]));
var pMinta = terapkanNego(s, idA, batasA - 500); terap(pMinta);
ok('F: Ben menawar Rp500 di bawah batas → negoMinta (harga baris TIDAK berubah), kalimat minta owner', !pMinta.keranjang && s.negoMinta && s.negoMinta.harga === batasA - 500 && s.negoMinta.batas === batasA && s.keranjang[0].trx.hargaSatuan === batasA && /minta owner/.test(pMinta.kabar), J([pMinta, s.keranjang[0].trx.hargaSatuan]));
var rM = susunMintaNego(s, W); var dM = rM.dokumen && rM.dokumen[0];
ok('F: MINTA OWNER → satu dokumen persetujuan: tindakan nego, menunggu, milik Ben (negoUid), barang = kunci baris, harga katalog → minta, jumlah 2, selisih total; harga baris tetap',
  dM && dM.koleksi === 'persetujuan' && dM.data.tindakan === 'nego' && dM.data.status === 'menunggu' && dM.data.negoUid === 'uid-ben' && dM.data.barang === 'karung|Angsa|50' && dM.data.hargaMinta === batasA - 500 && dM.data.hargaAsli === t0.hargaAsli && dM.data.jumlah === 2
  && dM.data.nominal === (t0.hargaAsli - batasA + 500) * 2 && /Angsa 50 kg: Rp/.test(dM.data.teks) && rM.patch.negoMinta === null && /harga nota tetap/.test(rM.patch.kabar), J(rM));
var kM = kirim(BEN, rM.dokumen);
ok('F: penjaga kiriman: Ben belum boleh menulis permintaan (rules belum membuka koleksi persetujuan untuk bukan-owner) → DITOLAK di perangkat, tidak dikirim', !!kM.tolak, J(kM));
var mb = bolehMintaOwner(BEN);
ok('F: tombol MINTA OWNER untuk Ben MATI dengan kalimat sebab + jalan keluar (pakai batas jatah / owner yang mencatat); owner tidak perlu minta', !mb.boleh && /server belum membuka/.test(mb.kalimat) && /batas jatah/.test(mb.kalimat) && !bolehMintaOwner(OWN).boleh, J(mb));
// owner memutus (papan persetujuan yang sama) — permintaan dianggap sudah sampai
terapkanKeCache(rM.dokumen || []);
ok('F: permintaan nego tampil di papan persetujuan owner (Menu › Sistem › Peran › Persetujuan) & Buku Nego: menunggu 1', ssPersetujuan(new Date()).menunggu.some(function (m) { return m.tindakan === 'nego' && /Angsa/.test(m.teks); }) && ngMenunggu().length === 1 && ngBuku('2026-10-07').menunggu === 1, J(ngBuku('2026-10-07')));
var tolak0 = dM ? susunPutusPersetujuan(dM.data.id, false, '', W) : {};
ok('F: owner menolak tanpa alasan → ditolak (alasan wajib)', /butuh alasan/.test(tolak0.tolak || ''));
terapkanKeCache((dM ? susunPutusPersetujuan(dM.data.id, true, '', W).dokumen : null) || []);
ok('F: sesudah owner MENYETUJUI, layar Ben menawarkan memakainya (setujuSiap) untuk baris itu', J(setujuSiap(s)) === J([{ id: idA, label: tA.label, harga: batasA - 500 }]), J(setujuSiap(s)));
terap(terapkanNego(s, idA, batasA - 500)); var tS = s.keranjang[0].trx;
ok('F: Ben mengetik harga yang disetujui → negoStatus disetujui + negoSetujuId; tidak lagi ditawarkan', !!dM && tS.hargaSatuan === batasA - 500 && tS.negoStatus === 'disetujui' && tS.negoSetujuId === String(dM.data.id) && setujuSiap(s).length === 0, J(tS));
var pTambah = ubahJumlahBaris(s, idA, 1);
ok('F: +1 karung melebihi jumlah yang disetujui (2) → DITOLAK, kalimat menyebut persetujuan owner untuk 2 karung; −1 tetap boleh', !pTambah.keranjang && /persetujuan owner untuk 2 karung/.test(pTambah.kabar) && !!ubahJumlahBaris(s, idA, -1).keranjang, pTambah.kabar);
terap({ uang: 1e9 }); var nB = simpanNota(s, W); var dB = ((nB.dokumen || []).filter(function (x) { return x.koleksi === 'penjualan'; })[0] || { data: {} }).data;
ok('G: nota mencatat nego: hargaAsliSatuan katalog, negoSelisih, negoStatus disetujui, negoSetujuId, negoBatas, negoJatah — tanpa kolom keranjang (nego, hargaSatuan)',
  !!dM && dB.hargaAsliSatuan === t0.hargaAsli && dB.negoSelisih === batasA - 500 - t0.hargaAsli && dB.negoStatus === 'disetujui' && dB.negoSetujuId === String(dM.data.id) && dB.negoBatas === batasA && dB.negoJatah === 50 && !('nego' in dB) && !('hargaSatuan' in dB), J(dB));
var kB = kirim(BEN, nB.dokumen || []);
ok('H: penjaga kiriman: nota Ben dengan nego DISETUJUI owner → boleh', !kB.tolak, J(kB));
terapkanKeCache(nB.dokumen || []); terap(nB.patch || { keranjang: [] });
// persetujuan sekali pakai: keranjang baru, barang & harga sama → minta lagi
terap(masukkan(Object.assign({}, s, { pilih: susunRak(s).karung.filter(function (c) { return c.kunci === 'Angsa' && c.berat === 50; })[0] }), 2)); var idA2 = s.keranjang[0].id;
var pLagi = terapkanNego(s, idA2, batasA - 500);
ok('F: persetujuan SEKALI PAKAI — sesudah notanya tercatat, harga yang sama di keranjang baru kembali minta owner', !pLagi.keranjang && pLagi.negoMinta && setujuSiap(s).length === 0, J(pLagi));
terap({ keranjang: [], negoMinta: null });
var bk = ngBuku('2026-10-07');
ok('J: Buku Nego mencatat nota Ben (siapa via atribusi nanti, barang, katalog → nego, selisih × jumlah) & permintaannya "disetujui · sudah dipakai"; potongan = Σ selisih nota',
  bk.nNota === 1 && bk.baris.some(function (x) { return x.jenis === 'nota' && x.barang === 'Angsa 50 kg' && x.selisih === batasA - 500 - t0.hargaAsli && x.jumlah === 2 && x.status === 'disetujui'; })
  && bk.baris.some(function (x) { return x.jenis === 'minta' && x.status === 'dipakai'; }) && bk.potongan === (t0.hargaAsli - batasA + 500) * 2 && bk.menunggu === 0 && /1 nego tercatat · 0 menunggu owner/.test(bk.judul), J(bk));

// ---- owner di keranjang: di bawah modal dengan alasan
terap({ negoAkun: OWN, negoHak: 'sendiri' });
terap(masukkan(Object.assign({}, s, { pilih: susunRak(s).kemasan[0] }), 1)); var idK = s.keranjang[0].id; var tK = s.keranjang[0].trx; var mK = ngModalSatuan(tK);
var pK = terapkanNego(s, idK, Math.floor(mK) - 1000);
ok('C: owner di keranjang: di bawah modal tanpa alasan → harga TIDAK berubah, kalimat minta alasan', !pK.keranjang && /tulis alasannya/.test(pK.kabar), pK.kabar);
terap({ negoAlasan: 'kemasan penyok' }); terap(terapkanNego(s, idK, Math.floor(mK) - 1000)); var tK2 = s.keranjang[0].trx;
ok('C: dengan alasan → dipakai, negoStatus bawahModal, negoAlasan tercatat, alasan di layar dikosongkan; kabar diberi tanda awas', tK2.negoStatus === 'bawahModal' && tK2.negoAlasan === 'kemasan penyok' && s.negoAlasan === '' && s.kabarAwas, J([tK2, s.kabar]));
var nK = simpanNota(Object.assign({}, s, { uang: 1e9 }), W); var dK = nK.dokumen[0].data;
ok('G: nota owner di bawah modal membawa negoStatus bawahModal + negoAlasan; penjaga kiriman bukan-owner MENOLAK baris seperti itu (Ben)', dK.negoStatus === 'bawahModal' && dK.negoAlasan === 'kemasan penyok' && kirim(BEN, nK.dokumen).tolak === KALIMAT_MINTA_OWNER, J(dK));
terap(terapkanNego(s, idK, tK.hargaAsli)); var tK3 = s.keranjang[0].trx;
ok('C: mengetik harga katalog lagi → nego dilepas (tanpa kolom nego)', !tK3.nego && !tK3.negoStatus && !tK3.negoAlasan && tK3.hargaSatuan === tK.hargaAsli, J(tK3));
terap({ keranjang: [] });

// ---- H · permintaan nego bila rules kelak membukanya: bentuknya tetap dijaga penjaga kiriman
BUAT_STAF.persetujuan = ['ben', 'karyawan']; BACA_STAF.push('persetujuan');
var dOk = JSON.parse(J(rM.dokumen || [{ koleksi: 'persetujuan', data: {} }])); var dSalah = JSON.parse(J(dOk)); dSalah[0].data.status = 'disetujui'; var dLain = JSON.parse(J(dOk)); dLain[0].data.tindakan = 'uangKeluar';
var h1 = kirim(BEN, dOk), h2 = kirim(BEN, dSalah), h3 = kirim(BEN, dLain), h4 = kirim(KRY, dOk);
ok('H: (seandainya rules dibuka) Ben mengirim permintaan nego "menunggu" → boleh; menyetujui sendiri / tindakan lain → DITOLAK; karyawan berkisi "tidak" → DITOLAK; tombol MINTA OWNER hidup',
  !h1.tolak && !!h2.tolak && !!h3.tolak && /tidak boleh/.test(h4.tolak || '') && bolehMintaOwner(BEN).boleh, J([h1, h2, h3, h4]));
delete BUAT_STAF.persetujuan; BACA_STAF.pop();
print(J({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('jual.js: lembar nego menyebut modal HANYA ke owner, memutus harga yang diketik dengan akun (SBN), dan menawarkan batas jatah + minta owner', 'jual',
     ["(owner ? ' · modal ' + RP(Math.round(modal)) + sat : '')", "const p = ketik > 0 ? L.putusNego(SBN(), b.id, ketik) : null;", 'data-aksi="pakaiBatasNego"', 'data-aksi="mintaOwnerNego"']),
    ('jual.js: MINTA OWNER memeriksa bolehMintaOwner (tombol mati berkata sebab); Buku Nego hanya owner; keputusan lewat susunPutusPersetujuan (papan persetujuan yang sama)', 'jual',
     ["const mb = bolehMintaOwner(a) || {}; if (!mb.boleh) return set({ kabar: mb.kalimat", "bukaBukuNego: () => { const tb = tombolLuarKisi(opsi.akun ? opsi.akun() : null); if (!tb.boleh)",
      "ngSetujui: ({ id }) => tulisUmum(susunPutusPersetujuan(id, true, ''", "tulisUmum(susunPutusPersetujuan(id, false, S().ngAlasanTolak"]),
    ('jual.js: baris bernego dibangun ulang dengan akun (tambah/kurang/bonus lewat SBN)', 'jual',
     ["kurangBaris: ({ id, langkah }) => set(L.ubahJumlahBaris(SBN(), id,", "tambahBaris: ({ id, langkah }) => set(L.ubahJumlahBaris(SBN(), id,", "bonus: ({ id }) => set(L.toggleBonus(SBN(), id)),"]),
    ('menu.js: Atur peran memuat jatah karyawan, langkah, jatah per akun & saklar di bawah modal', 'menu',
     ["angka('jatahKaryawan', 'Jatah nego karyawan', '% margin')", "angka('langkahNego', 'Langkah harga nego', 'rupiah')", 'data-ketik="aturJatahAkun"', 'data-aksi="aturBawahModal"']),
    ('app.js: penjaga kiriman menerima jatah nego akun yang masuk', 'app', ["{ jatahNego: ngJatah(a) }"]),
]


# ---- LAYAR: jual.js asli di jsc (tiruan peramban, pola uji_cache_chip_literan) — lembar nego & Buku Nego tergambar
LAYAR = uji_rak_inkremental.BANTU + r"""
var OWN = { jenis: 'owner', peran: 'owner', nama: 'Owner', uid: 'uid-owner' }; var BEN = { jenis: 'aktif', peran: 'ben', nama: 'Ben Contoh', uid: 'uid-ben' }; var akunKini = OWN;
var opsiJ = { akun: function () { return akunKini; }, gantiMode: function () {}, mode: function () { return 'gelap'; }, statusTeks: function () { return ''; }, statusAwas: function () { return false; },
  statusRingkas: function () { return ''; }, versiData: function () { return __versi; }, pemegang: function () { return null; }, bukaStok: null };
var aJ = __akar(); var JL = pasangLayarJual(aJ, opsiJ); JL.keadaan.setel({ jalur: 'karung', sekarang: new Date(Date.now()) });
var sJ = function () { return JL.keadaan.baca(); }; var H = function () { return aJ.__html || ''; };
var rk = function () { var s = sJ(); sinkronKeranjang(s); return susunRak(s); };
var c = rk().karung.filter(function (x) { return x.kunci === 'NG' && x.berat === 50; })[0]; var m = masukkan(Object.assign({}, sJ(), { pilih: c }), 2); JL.keadaan.setel({ keranjang: m.keranjang, urutBaris: m.urutBaris });
var id = sJ().keranjang[0].id; var t0 = sJ().keranjang[0].trx; var modal = ngModalSatuan(t0);
aJ.__aksi.nego({ id: id });
ok('layar owner: lembar nego terbuka dengan tangga katalog · modal · jatah owner 100 %', sJ().lembar === 'nego' && H().indexOf('data-k="ng-tangga"') >= 0 && H().indexOf('katalog ' + RP(t0.hargaAsli)) >= 0 && H().indexOf(' · modal ' + RP(Math.round(modal))) >= 0 && H().indexOf('jatah owner 100 % margin') >= 0, H().slice(0, 300));
JL.keadaan.setel({ ketik: String(Math.floor(modal) - 1000) });
ok('layar owner: harga di bawah modal → pita putusan menyebut alasan + kolom alasan muncul; tombol berkata belum bisa', H().indexOf('data-k="ng-putus"') >= 0 && /tulis alasannya/.test(H()) && H().indexOf('id="negoAlasan"') >= 0 && H().indexOf('BELUM BISA') >= 0);
aJ.__aksi.negoAlasan('beras sisa'); aJ.__aksi.terapkanNego();
ok('layar owner: dengan alasan → harga dipakai, lembar tertutup, baris keranjang menyebut "di bawah modal (beras sisa)"', sJ().lembar === null && sJ().keranjang[0].trx.negoStatus === 'bawahModal' && H().indexOf('di bawah modal (beras sisa)') >= 0, sJ().kabar);
// owner: permintaan nego menunggu → pita + Buku Nego dengan tombol setujui / tolak
terapkanKeCache([{ koleksi: 'persetujuan', data: { id: 'ps9', tindakan: 'nego', status: 'menunggu', tanggal: '2026-09-21', jam: '09:00', pada: '2026-09-21T02:00:00.000Z', dari: 'Ben Contoh', peran: 'ben', negoUid: 'uid-ben',
  teks: 'NG 50 kg: Rp650.000 → Rp640.000/karung × 1', nominal: 10000, barang: 'karung|NG|50', label: 'NG 50 kg', satuan: 'karung', jumlah: 1, hargaAsli: 650000, hargaMinta: 640000, batas: 645000, jatah: 50, alasan: '' } }]);
JL.keadaan.setel({ kabar: '' });
ok('layar owner: pita "1 permintaan nego menunggu owner" tampil dan membuka Buku Nego', H().indexOf('data-k="pita-nego-menunggu"') >= 0 && H().indexOf('1 permintaan nego menunggu owner') >= 0);
aJ.__aksi.bukaBukuNego();
ok('layar owner: Buku Nego — judul, baris permintaan Ben dengan setujui/tolak, kolom alasan tolak', sJ().lembar === 'bukuNego' && H().indexOf('data-k="lembar-bukuNego"') >= 0 && H().indexOf('1 menunggu owner') >= 0 && H().indexOf('data-aksi="ngSetujui" data-id="ps9"') >= 0 && H().indexOf('data-aksi="ngTolak" data-id="ps9"') >= 0 && H().indexOf('id="ngAlasanTolak"') >= 0, H().slice(H().indexOf('lembar-bukuNego'), H().indexOf('lembar-bukuNego') + 400));
// Ben: modal tidak disebut, di bawah jatah → minta owner (tombol mati sampai server membuka)
akunKini = BEN; JL.keadaan.setel({ lembar: null, keranjang: [], negoAlasan: '' });
m = masukkan(Object.assign({}, sJ(), { pilih: rk().karung.filter(function (x) { return x.kunci === 'NG' && x.berat === 50; })[0] }), 1); JL.keadaan.setel({ keranjang: m.keranjang, urutBaris: m.urutBaris });
id = sJ().keranjang[0].id; t0 = sJ().keranjang[0].trx; var bt = ngBatas(t0.hargaAsli, ngModalSatuan(t0), 50, 500);
aJ.__aksi.nego({ id: id }); JL.keadaan.setel({ ketik: String(bt - 500) });
ok('layar Ben: tangga menyebut jatah Ben 50 % & paling rendah, TANPA modal; harga di bawah jatah → tombol "MINTA OWNER ›"', H().indexOf('jatah Ben Contoh 50 % margin → paling rendah ' + RP(bt)) >= 0 && H().indexOf(' · modal ') < 0 && H().indexOf('MINTA OWNER ›') >= 0, H().slice(H().indexOf('ng-tangga'), H().indexOf('ng-tangga') + 300));
aJ.__aksi.terapkanNego();
ok('layar Ben: ketuk → kartu minta owner: PAKAI BATAS + MINTA OWNER mati (server belum membuka), harga baris tetap', H().indexOf('data-k="ng-minta"') >= 0 && H().indexOf('PAKAI BATAS ' + RP(bt)) >= 0 && /kaca-btn mati" data-aksi="tombolMati"[^>]*>MINTA OWNER/.test(H()) && sJ().keranjang[0].trx.hargaSatuan === t0.hargaAsli, H().slice(H().indexOf('ng-minta'), H().indexOf('ng-minta') + 500));
aJ.__aksi.pakaiBatasNego();
ok('layar Ben: PAKAI BATAS → harga = batas jatah, lembar tertutup', sJ().keranjang[0].trx.hargaSatuan === bt && sJ().keranjang[0].trx.negoStatus === 'jatah' && sJ().lembar === null, J(sJ().keranjang[0].trx));
print(J({ lulus: lulus, gagal: gagal }));
"""


def jalan_layar(ganti_layar=None):
    js, lay, _app = uji_cache_chip_literan.bundel(ganti_layar)
    lay = lay.replace("var bukanOwner = function () { return false; };", "var bukanOwner = function (a) { return !!a && a.jenis !== 'owner'; };")
    h, e = uji_wadah_bernama.jalan(uji_rak_inkremental.JAM_TETAP + js + uji_cache_chip_literan.PROKSI + lay + '\nvar KOTAK = ' + json.dumps(uji_rak_inkremental.KOTAK) + ';\n' + LAYAR)
    if h is None: return 0, ['LAYAR: JSC JATUH ' + e]
    return h['lulus'], h['gagal']


def jalan(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write("var __KINI = new Date('2026-10-07T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" + js + '\nvar KOTAK = ' + json.dumps(uji_jual_baru.KOTAK) + ';\n' + SKENARIO); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], h['gagal']


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    return len(STATIS) - len(g), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


NG = 'baru/js/layar/nego-logika.js'; JL = 'baru/js/layar/jual-logika.js'; AK = 'baru/js/data/akses.js'; SL = 'baru/js/layar/sistem-logika.js'
RUSAK = [
    ('batas dibulatkan ke BAWAH (melewati jatah)', NG, "return Math.min(harga, Math.ceil(x / L - 1e-9) * L);", "return Math.min(harga, Math.floor(x / L) * L);"),
    ('jatah per akun tidak menang atas peran', NG, "if (u && a.jatahAkun[u] !== undefined) return a.jatahAkun[u];", ""),
    ('bawaan Ben bukan 50 % (bawaan rancangan dilanggar)', NG, "export const NG_BAWAAN = { ben: 50,", "export const NG_BAWAAN = { ben: 100,"),
    ('di bawah jatah dipakai tanpa minta owner', NG, "if (harga >= modal) return mintaAtauTolak(", "if (harga >= modal) return P('jatah', 'x') || mintaAtauTolak("),
    ('di bawah modal tanpa alasan dipakai', NG, "if (!alasan) return P('perluAlasan'", "if (false) return P('perluAlasan'"),
    ('siapa pun boleh di bawah modal', NG, "if (!ngBolehBawahModal(akun, A)) return P('tolak'", "if (false) return P('tolak'"),
    ('kisi "tidak boleh" diabaikan', NG, "if ((o.hakNego || 'owner') === 'tidak') return P('tolak'", "if (false) return P('tolak'"),
    ('modal disebut ke bukan-owner', NG, "const rugi = owner ? 'di bawah modal ' + RP(modal)", "const rugi = true ? 'di bawah modal ' + RP(modal)"),
    ('persetujuan dipakai berkali-kali', NG, "const o = {}; ambilPenjualan().forEach((p) => { if (p.negoSetujuId) o[String(p.negoSetujuId)] = 1; });", "const o = {};"),
    ('persetujuan berlaku untuk jumlah lebih banyak', NG, "o.setuju = st.status === 'disetujui' && Number(st.jumlah) >= Number(t.jumlah) ? st : null;", "o.setuju = st.status === 'disetujui' ? st : null;"),
    ('nego minta owner tetap mengubah harga baris', JL, "if (p.status === 'minta') return { negoMinta: { id, harga: p.harga, batas: p.batas, alasan: p.alasan, teks: p.teks },", "if (p.status === 'minta') return { keranjang: s.keranjang.map((x) => (x.id === id ? { id, trx: selesaikanHarga(Object.assign({}, b.trx, { hargaSatuan: p.harga }), false) } : x)), negoMinta: { id, harga: p.harga, batas: p.batas, alasan: p.alasan, teks: p.teks },"),
    ('baris bernego dibangun ulang tanpa diputus lagi', JL, "  if (!baru || !baru.nego) return { trx: baru };\n  const r = ngPutusUlang(", "  return { trx: baru };\n  const r = ngPutusUlang("),
    ('nota tidak mencatat status nego', JL, "  if (e.nego) { t.nego = true; NG_KOLOM.forEach((k) => { if (e[k] !== undefined) t[k] = e[k]; }); }", "  if (e.nego) { t.nego = true; }"),
    ('penjaga: permintaan nego tanpa memeriksa bentuk', AK, "if (x.koleksi === 'persetujuan' && (d.tindakan !== 'nego' || d.status !== 'menunggu' || d.diputusPada || (hak.nego || 'tidak') === 'tidak')) return { tolak: tolakTindakan('nego') };", ""),
    ('Atur menerima jatah karyawan > 100 %', SL, "|| angka('jatahKaryawan', 0, 100, '%')", ""),
    ('Atur tidak menyaring kunci "di bawah modal"', SL, ".filter((k, i, L) => kenal.indexOf(k) >= 0 && L.indexOf(k) === i)", ""),
]
RUSAK_LAYAR = [
    ('lembar nego tanpa kolom alasan di bawah modal', "${p && p.dibawahModal && NG.ngBolehBawahModal(a, A) ? h`<input", "${false ? h`<input"),
    ('Buku Nego tanpa tombol setujui / tolak', "${owner && x.jenis === 'minta' && x.status === 'menunggu' ? h`<span class=\"kaca-btn kecil aktif emas\" data-aksi=\"ngSetujui\"", "${false ? h`<span class=\"kaca-btn kecil aktif emas\" data-aksi=\"ngSetujui\""),
    ('pita permintaan nego tidak tampil', "${NGM && s.lembar !== 'bukuNego' ? h`<div class=\"pita-info awas\" data-k=\"pita-nego-menunggu\"", "${false ? h`<div class=\"pita-info awas\" data-k=\"pita-nego-menunggu\""),
]
RUSAK_STATIS = [
    ('lembar nego memajang modal ke semua orang', 'jual', "(owner ? ' · modal ' + RP(Math.round(modal)) + sat : '')", "(' · modal ' + RP(Math.round(modal)) + sat)"),
    ('tombol MINTA OWNER tanpa memeriksa server', 'jual', "const mb = bolehMintaOwner(a) || {}; if (!mb.boleh) return set({ kabar: mb.kalimat", "const mb = { boleh: true }; if (!mb.boleh) return set({ kabar: mb.kalimat"),
]

if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b)
            l, g = jalan(T)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, a, b in RUSAK_LAYAR:
            try: l, g = jalan_layar([(a, b)])
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' — ' + str(e)); kode = 3; continue
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_STATIS:
            if src[berkas].count(a) != 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            S2 = dict(src); S2[berkas] = S2[berkas].replace(a, b)
            l, g = statis(S2)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = jalan(teks); l2, g2 = statis(src); l3, g3 = jalan_layar()
    print('BATAS NEGO (JS2-C, kotak pasir): %d lulus · %d gagal (logika %d · statis %d · layar asli %d)' % (l + l2 + l3, len(g) + len(g2) + len(g3), l, l2, l3))
    for x in g + g2 + g3: print('   ✗ ' + x[:600])
    sys.exit(2 if g or g2 or g3 else 0)
