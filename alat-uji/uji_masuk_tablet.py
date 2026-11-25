#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_masuk_tablet.py — BARANG MASUK & BAYAR SUPIR dari tablet (owner 22 Nov 2026, paket ③; rules v15), dijalankan ASLI di jsc di atas data contoh
uji_uang_baru.py (kedatangan RODA CONTOH 20 Agu: Angsa Rp13.000/kg, IR64 Apex Rp14.000/kg; hari ini 19 Sep), ditambah pemeriksaan pemasangannya.

Kenapa ada: kedatangan dari tablet langsung mengubah STOK, MODAL & BON pemasok, dan uang yang keluar dari laci (upah bongkar, bayar ke supir) jadi titipan yang
owner tulis ke kedatangan / bon. Yang paling mahal kalau salah: kedatangan tablet yang tercatat tunai (laci berkurang tanpa titipan), upah bongkar yang
terhitung dua kali, bayar supir yang masuk bon yang salah / bertanggal hari owner menyetujui, dan harga beda yang tidak sampai ke owner.

Yang dipegang:
  · kiriman tablet = kedatangan (bon, hari ini, bongkar 0, dariTablet) + titipan upah bongkar (batchId) + titipan bayar supir (pemasok, batchId) + kabar owner
  · bentuknya lolos penjaga kiriman akses.js (= rules v15); karyawan / kisi kedatangan "tidak" ditolak
  · merek baru DICATAT (owner 22 Nov 2026) atas nama yang diketik, tanpa tebakan kelas & tanpa menulis peta kelas, ditandai merekBaru & disebut di kabar
    (jalur owner tetap memakai tebakan kelas); nama arsip ditolak dengan kalimat (owner dari HP); harga beda dari harga lalu ditandai & disebut di kabar; beda jauh dari modal = digabung, ditandai
  · owner menyetujui upah bongkar → biayaBongkar kedatangan itu (laci keluar sekali, bertanggal datang); dua kali tidak bisa
  · owner menyetujui bayar supir → bon kedatangan itu (bawaan) atau bon pilihan owner; bertanggal TITIPAN; sisa bon turun; melebihi sisa ditolak
  · titipan yang menunggu ikut perkiraan laci (laci fisik sudah berkurang); tanda terima tablet menyebut uang yang dibayar ke supir

    python3 alat-uji/uji_masuk_tablet.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_masuk_tablet.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json, copy, subprocess, tempfile

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru as UB  # noqa: E402
JSC = UB.JSC
MT = 'baru/js/layar/masuk-tablet-logika.js'; TPL = 'baru/js/layar/titipan-logika.js'; AK = 'baru/js/data/akses.js'; TBL = 'baru/js/layar/terima-barang-logika.js'
SC = 'baru/js/layar/stok-catat-logika.js'; STK = 'baru/js/layar/stok.js'; UG = 'baru/js/layar/uang.js'; SL = 'baru/js/layar/sistem-logika.js'; KB = 'baru/js/layar/kabar-baru-logika.js'
TBP = 'baru/js/layar/terima-barang-panel.js'; TPP = 'baru/js/layar/titipan-panel.js'; IDX = 'baru/index.html'; FN = 'functions/pesan.js'; RULES = 'firestore.rules'
# stok-hpp-logika SENGAJA tidak ikut (teksMargin bertabrakan dengan harga-logika di satu lingkup) — pola uji_ringkas_tablet.py
import uji_stok_baru as SB  # noqa: E402   urutan modul Stok (varian-logika sebelum stok-catat: konstanta tingkat atas)
MODUL = [m for m in dict.fromkeys(SB.MODUL + UB.MODUL + ['baru/js/data/hemat-baca.js', TPL, AK, 'baru/js/layar/sistem-logika.js', TBL, MT]) if not m.endswith('harga-logika.js') or m.endswith('stok-hpp-logika.js')]
STATIS = [STK, UG, SL, KB, TBP, TPP, IDX, FN, RULES]


def kotak():
    K = copy.deepcopy(UB.KOTAK)
    # IR64 Apex di kotak uang = nama WADAH (bukan merek karung) → kedatangan tablet memakai merek karung yang punya buku: Pandan Contoh (datang TUNAI 10 Agu, Rp14.000/kg)
    K['batchMasuk'].append({'id': 'b0', 'tanggal': '2026-08-10', 'jam': '09:00', 'pemasok': 'RODA CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
                            'merkList': [{'id': '1', 'merk': 'Pandan Contoh', 'satuan': 'karung', 'jumlahKarung': 10, 'beratKarung': 50, 'totalKg': 500, 'hargaPerKg': 14000, 'subtotalHarga': 7000000}]})
    # titik kas dari DOKUMEN (pola uji_ringkas_tablet): laci 2.000.000 dst. per 15 Sep — rumus laci tanggal 19 Sep terhitung
    K['pengaturan'] = [{'id': 'titikKas', 'tanggal': '2026-09-15', 'laci': 2000000, 'brankas': 10000000, 'rekening': 3000000, 'amplop': 1000000, 'diubahPada': '2026-09-15T14:00:00.000Z'}]
    # owner 22 Nov 2026 (merek baru dari tablet): peta kelas berisi TEBAKAN untuk dua merek yang belum berbuku — satu ke kelas berwadah/merek (Pandan Contoh),
    # satu ke kelas TANPA wadah (Ketan Contoh: buku atas nama kelas). Tablet wajib mengabaikan keduanya; owner tetap memakainya. + satu nama diarsipkan.
    K['aturanToko'] = [{'id': 'kelasMerek', 'peta': {'Merek Tebak Contoh': 'Pandan Contoh', 'Merek Sendiri Contoh': 'Ketan Contoh'},
                        'asal': {'Merek Tebak Contoh': 'tebakan', 'Merek Sendiri Contoh': 'tebakan'}, 'kelasSendiri': ['Ketan Contoh']},
                       {'id': 'produkArsip', 'daftar': [{'kunci': 'K:Arsip Contoh', 'jenis': 'beras', 'nama': 'Arsip Contoh', 'tanggal': '2026-09-01', 'jam': '09:00'}]}]
    K['aksesAkun'] = [{'id': 'uid-tablet', 'uid': 'uid-tablet', 'nama': 'Tablet', 'email': 'tablet@contoh.com', 'peran': 'ben', 'aktif': True}]
    return K


SKENARIO = r"""
var hasil = []; var J = JSON.stringify;
function cek(nama, ok, ket) { hasil.push({ nama: nama, ok: !!ok, ket: ket === undefined ? '' : (typeof ket === 'string' ? ket : J(ket)) }); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var _id = 0; var W = { tanggal: '2026-09-19', jam: '10:30', kini: '2026-09-19T03:30:00.000Z', idUnik: function () { return 'mt' + (++_id); } };
var W2 = { tanggal: '2026-09-20', jam: '08:00', kini: '2026-09-20T01:00:00.000Z', idUnik: function () { return 'ow' + (++_id); } };   // owner menyetujui BESOKNYA
var BEN = { jenis: 'aktif', peran: 'ben', nama: 'Penjaga A', operatorId: 'o1', uid: 'uid-tablet' };
var KRY = { jenis: 'aktif', peran: 'karyawan', nama: 'Orang B', uid: 'uid-k' };
var HAK_BEN = { jualTunai: 'sendiri', jualBon: 'sendiri', nego: 'owner', terimaBon: 'sendiri', hitungLaci: 'sendiri', uangKeluar: 'owner', adukan: 'sendiri', kedatangan: 'sendiri', hargaBeli: 'tidak', koreksi: 'owner', hapus: 'tidak', pelangganBaru: 'sendiri', atur: 'tidak', isiUlang: 'sendiri' };
var HAK_KRY = Object.assign({}, HAK_BEN, { uangKeluar: 'tidak', jualBon: 'owner', hitungLaci: 'tidak' });
var kirim = function (akun, r, hak) { return periksaKiriman(akun, (r.dokumen || []).map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false }; }), [], hak); };
var CACHE = { batchMasuk: 'batch', utangPemasokMutasi: 'utangPemasok', persetujuan: 'persetujuan' };   // nama simpanan = koleksi.js (cache)
var tulis = function (r) { (r.dokumen || []).forEach(function (x) { var a = cacheMentah(CACHE[x.koleksi] || x.koleksi).slice(); var i = a.findIndex(function (d) { return String(d.id) === String(x.data.id); }); if (i >= 0) a[i] = x.data; else a.push(x.data); pasok(x.koleksi, a); }); return r; };
var DRAF = { pemasok: 'RODA CONTOH', caraBayar: 'tunai', tanggal: '2026-09-01', bongkar: '70.000', bayarSupir: '1.000.000',
  baris: [{ merk: 'Angsa', jumlahKarung: '60', beratKarung: 50, hargaPerKg: '13000' }, { merk: 'Pandan Contoh', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '14.500' }] };

// ---------- kiriman tablet ----------
var titip0 = tpMenungguSampai('2026-09-19').rp; var laci0 = rumusLaci('2026-09-19'); var bon0 = hitungUtangPemasok().find(function (p) { return p.pemasok === 'RODA CONTOH'; });
var R = mtSusunSimpan(DRAF, BEN, W, false);
cek('kiriman tablet: 4 dokumen — kedatangan, titipan upah bongkar, titipan bayar supir, kabar owner', R.dokumen && J(R.dokumen.map(function (x) { return x.koleksi + (x.data.jenis ? ':' + x.data.jenis : x.data.tindakan === 'barangMasuk' ? ':kabar' : ''); })) === J(['batchMasuk', 'persetujuan:bongkar', 'persetujuan:bayarBon', 'persetujuan:kabar']), R.tolak || (R.dokumen || []).map(function (x) { return x.koleksi; }));
if (!R.dokumen || R.dokumen.length < 4) { print(J(hasil)); throw new Error('kiriman tablet tidak tersusun: ' + (R.tolak || J(R))); }
var BM = R.dokumen[0].data; var TB = R.dokumen[1].data; var TS = R.dokumen[2].data; var KBR = R.dokumen[3].data;
cek('kedatangan: BON (bukan tunai yang ada di draf), tanggal HARI INI (bukan tanggal draf), bongkar 0, bertanda dariTablet', BM.caraBayar === 'utang' && BM.tanggal === '2026-09-19' && BM.biayaBongkar === 0 && BM.dariTablet === true, BM);
cek('kedatangan: 60 karung Angsa 3.000 kg Rp39.000.000 + 10 karung Pandan Contoh 500 kg Rp7.250.000', BM.merkList.length === 2 && BM.merkList[0].totalKg === 3000 && BM.merkList[0].subtotalHarga === 39000000 && BM.merkList[1].totalKg === 500 && BM.merkList[1].subtotalHarga === 7250000, BM.merkList);
cek('harga beda dari harga lalu ditandai di kedatangan: Pandan Contoh 14.500 (lalu 14.000); Angsa sama → tidak', J(BM.hargaBeda) === J([{ merk: 'Pandan Contoh', harga: 14500, lalu: 14000, persen: 3.6 }]), BM.hargaBeda);
cek('titipan upah bongkar: 70.000, menunjuk kedatangannya, menunggu owner', TB.tindakan === 'uangKeluar' && TB.jenis === 'bongkar' && TB.nominal === 70000 && TB.batchId === String(BM.id) && TB.status === 'menunggu' && TB.mintaUid === 'uid-tablet', TB);
cek('titipan bayar supir: 1.000.000, pemasok & kedatangan ikut', TS.jenis === 'bayarBon' && TS.nominal === 1000000 && TS.pemasok === 'RODA CONTOH' && TS.batchId === String(BM.id), TS);
cek('kabar owner: barangMasuk menunggu, menunjuk kedatangan, menyebut harga beda, bongkar & bayar supir', KBR.tindakan === 'barangMasuk' && KBR.batchId === String(BM.id) && /Pandan Contoh Rp14\.500 \(lalu Rp14\.000\)/.test(KBR.teks) && /bongkar Rp70\.000/.test(KBR.teks) && /supir Rp1\.000\.000/.test(KBR.teks), KBR.teks);
cek('kiriman lolos penjaga kiriman akses.js (bentuk rules v15)', !kirim(BEN, R, HAK_BEN).tolak, kirim(BEN, R, HAK_BEN));
cek('kiriman yang sama dari karyawan / Penjaga laci berkisi kedatangan "tidak" ditolak', !!kirim(KRY, R, HAK_KRY).tolak && !!kirim(BEN, R, Object.assign({}, HAK_BEN, { kedatangan: 'tidak' })).tolak);
cek('penjaga kiriman: kedatangan tablet yang TUNAI atau membawa upah bongkar ditolak (= rules v15)', !!kirim(BEN, { dokumen: [{ koleksi: 'batchMasuk', data: Object.assign({}, BM, { caraBayar: 'tunai' }) }] }, HAK_BEN).tolak
  && !!kirim(BEN, { dokumen: [{ koleksi: 'batchMasuk', data: Object.assign({}, BM, { biayaBongkar: 70000 }) }] }, HAK_BEN).tolak);
cek('akses.js: kedatangan tablet = tindakan kedatangan (bukan isi ulang)', J(tindakanKiriman(R.dokumen.slice(0, 1).map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false }; }))) === J(['kedatangan']));

// ---------- tolakan tablet ----------
var Rb = mtSusunSimpan(Object.assign({}, DRAF, { baris: [{ merk: 'Merek Contoh Baru', jumlahKarung: '60', beratKarung: 50, hargaPerKg: '12000' }] }), BEN, W, false);
var bmB = Rb.dokumen && Rb.dokumen[0].data; var kbB = Rb.dokumen && Rb.dokumen.find(function (x) { return x.data.tindakan === 'barangMasuk'; });
cek('merek baru → DICATAT atas nama yang diketik (owner 22 Nov 2026), ditandai merekBaru, disebut di kabar owner & kalimat layar', bmB && bmB.merkList[0].merk === 'Merek Contoh Baru' && J(bmB.merekBaru) === J(['Merek Contoh Baru'])
  && kbB && /MEREK BARU: Merek Contoh Baru/.test(kbB.data.teks) && /Merek baru Merek Contoh Baru dibuka bukunya/.test(Rb.patch.kabar), Rb.tolak || bmB);
cek('kiriman merek baru = kedatangan + titipan + kabar saja (tanpa setelan kelas / jenis / arsip) dan lolos penjaga kiriman (rules v15)', Rb.dokumen && Rb.dokumen.every(function (x) { return x.koleksi === 'batchMasuk' || x.koleksi === 'persetujuan'; }) && !kirim(BEN, Rb, HAK_BEN).tolak, Rb.dokumen && Rb.dokumen.map(function (x) { return x.koleksi; }));
var DT = function (m) { return Object.assign({}, DRAF, { bongkar: '', bayarSupir: '', baris: [{ merk: m, jumlahKarung: '60', beratKarung: 50, hargaPerKg: '12000' }] }); };
var Rt = mtSusunSimpan(DT('Merek Tebak Contoh'), BEN, W, false); var Rs = mtSusunSimpan(DT('Merek Sendiri Contoh'), BEN, W, false);
cek('tablet: merek baru bertebakan kelas berwadah → tetap atas nama yang diketik, tanpa setelan lain (kelas = owner)', Rt.dokumen && Rt.dokumen.length === 2 && Rt.dokumen[0].data.merkList[0].merk === 'Merek Tebak Contoh' && !Rt.dokumen[0].data.merkList[0].merkPemasok, Rt.tolak || Rt.dokumen.map(function (x) { return x.koleksi; }));
cek('tablet: merek baru bertebakan kelas TANPA wadah → tidak dibukukan atas nama kelas (Ketan Contoh)', Rs.dokumen && Rs.dokumen[0].data.merkList[0].merk === 'Merek Sendiri Contoh' && J(Rs.dokumen[0].data.merekBaru) === J(['Merek Sendiri Contoh']), Rs.tolak || Rs.dokumen[0].data.merkList);
var Os = susunSimpanMasuk(Object.assign({}, DT('Merek Sendiri Contoh'), { tanggal: '2026-09-19' }), W, false);
cek('jalur OWNER tidak berubah: tebakan kelas tetap dipakai (Merek Sendiri Contoh → dibukukan atas nama kelas Ketan Contoh + merek pemasok), tanpa tanda merekBaru', Os.dokumen && Os.dokumen[0].data.merkList[0].merk === 'Ketan Contoh' && Os.dokumen[0].data.merkList[0].merkPemasok === 'Merek Sendiri Contoh'
  && !Os.dokumen[0].data.merekBaru, Os.tolak || Os.dokumen[0].data.merkList);
cek('nama yang DIARSIPKAN tetap ditolak dari tablet dengan kalimat tablet (memulihkan = owner; bukan pilihan PULIHKAN yang tidak ada di tablet)', /DIARSIPKAN — owner yang memulihkannya dari HP/.test(mtSusunSimpan(DT('Arsip Contoh'), BEN, W, false).tolak || ''), mtSusunSimpan(DT('Arsip Contoh'), BEN, W, false).tolak);
var Rk = mtSusunSimpan(Object.assign({}, DRAF, { baris: [{ merk: 'Angsa', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '13000' }] }), BEN, W, false);
cek('karung sedikit → ketuk sekali lagi; ketukan kedua tersimpan', !!Rk.perluYakin && !!(mtSusunSimpan(Object.assign({}, DRAF, { baris: [{ merk: 'Angsa', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '13000' }] }), BEN, W, true).dokumen), Rk.tolak);
var Rj = mtSusunSimpan(Object.assign({}, DRAF, { baris: [{ merk: 'Angsa', jumlahKarung: '60', beratKarung: 50, hargaPerKg: '15000' }] }), BEN, W, false);
cek('harga jauh dari modal (Angsa 15.000 vs 13.000) → dicatat sebagai Angsa yang sama (tablet tidak memutus mutu), ditandai hargaJauh & disebut di kabar', Rj.dokumen && Rj.dokumen[0].data.merkList[0].merk === 'Angsa' && J(Rj.dokumen[0].data.hargaJauh) === J(['Angsa']) && /digabung: Angsa/.test(Rj.dokumen[3].data.teks), Rj.tolak || Rj.dokumen[0].data);
cek('upah bongkar / bayar supir bukan angka → ditolak; kosong → tanpa titipan', /Upah bongkar hanya angka/.test(mtSusunSimpan(Object.assign({}, DRAF, { bongkar: 'tujuh puluh' }), BEN, W, false).tolak || '')
  && mtSusunSimpan(Object.assign({}, DRAF, { bongkar: '', bayarSupir: '' }), BEN, W, false).dokumen.length === 2);
cek('tanpa orang yang jaga → ditolak', !!mtSusunSimpan(DRAF, null, W, false).tolak);

// ---------- tersimpan: laci fisik & buku ----------
tulis(R);
cek('titipan yang menunggu ikut perkiraan laci: + upah bongkar 70.000 + bayar supir 1.000.000', tpMenungguSampai('2026-09-19').rp - titip0 === 1070000, [titip0, tpMenungguSampai('2026-09-19').rp]);
var laci1 = rumusLaci('2026-09-19');
cek('kedatangan bon tidak mengurangi laci di buku sebelum owner menyetujui', laci1.ada && laci0.ada && laci1.seharusnya === laci0.seharusnya, [laci0.seharusnya, laci1.seharusnya]);
var bon1 = hitungUtangPemasok().find(function (p) { return p.pemasok === 'RODA CONTOH'; });
cek('bon RODA CONTOH bertambah persis nilai nota kedatangan tablet (46.250.000)', Math.round(bon1.bon.reduce(function (a, b) { return a + b.sisa; }, 0) - bon0.bon.reduce(function (a, b) { return a + b.sisa; }, 0)) === 46250000, [bon0.bon, bon1.bon]);

// ---------- tanda terima di tablet ----------
var TT = tbmData(BM, { terbaca: false, titipSupir: 1000000 }); var GT = tbmGaris(TT, { nama: 'Toko Contoh' }, 'pemasok', { tanggal: W.tanggal, jam: W.jam, oleh: 'Penjaga A' });
cek('tanda terima tablet: bon, angka buku tidak terbaca, uang ke supir 1.000.000 tertulis; sisa ditulis tangan', TT.bayar.keadaan === 'takTerbaca' && TT.bayar.titipSupir === 1000000 && GT.some(function (g) { return g.kiri === 'Dibayar ke supir' && g.kanan === 'Rp1.000.000'; }) && GT.some(function (g) { return g.kiri === 'Sisa: Rp'; }), GT.filter(function (g) { return !g.garis; }).map(function (g) { return g.kiri + ' | ' + g.kanan; }));

// ---------- owner menyetujui upah bongkar ----------
var PB = tpSusunPutus(TB.id, 'setuju', {}, W2);
cek('setujui upah bongkar = kedatangan ditulis ulang dengan biayaBongkar 70.000 & bongkarTitipan; tanpa dokumen uang lain', PB.dokumen && PB.dokumen.length === 2 && PB.dokumen[1].koleksi === 'batchMasuk' && PB.dokumen[1].data.biayaBongkar === 70000 && J(PB.dokumen[1].data.bongkarTitipan) === J([TB.id]) && PB.dokumen[1].data.tanggal === '2026-09-19', PB.tolak || PB.dokumen[1].data);
tulis(PB);
var laci2 = rumusLaci('2026-09-19');
cek('sesudah disetujui: laci di buku tanggal DATANG berkurang tepat 70.000 (bongkar dari laci), titipannya keluar dari perkiraan', laci1.seharusnya - laci2.seharusnya === 70000 && tpMenungguSampai('2026-09-19').rp - titip0 === 1000000, [laci1.seharusnya, laci2.seharusnya]);
cek('upah bongkar tidak bisa ditulis dua kali', (function () { var m = cacheMentah('persetujuan').find(function (x) { return x.id === TB.id; }); var lama = m.status; m.status = 'menunggu'; var x = tpSusunPutus(TB.id, 'setuju', {}, W2); m.status = lama; return /dua kali/.test(x.tolak || ''); })());

// ---------- owner menyetujui bayar supir ----------
var PL = tpBonPilihan(TS.id, new Date(W2.kini));
cek('pilihan bon: bon RODA CONTOH yang bersisa (20 Agu + kedatangan tablet), bawaan = kedatangan tablet', PL.bon.length === 2 && PL.bawaan === String(BM.id) && PL.bon[0].tanggal === '2026-08-20', PL);
var PS = tpSusunPutus(TS.id, 'setuju', {}, W2);
cek('setujui bayar supir = bayar bon kedatangan tablet 1.000.000 dari laci, bertanggal TITIPAN (19 Sep), bukan hari owner menyetujui', PS.dokumen && PS.dokumen[1].koleksi === 'utangPemasokMutasi' && PS.dokumen[1].data.bonId === String(BM.id) && PS.dokumen[1].data.nominal === 1000000 && PS.dokumen[1].data.dari === 'laci' && PS.dokumen[1].data.tanggal === '2026-09-19' && PS.dokumen[1].data.dariPersetujuan === TS.id, PS.tolak || PS.dokumen[1].data);
var PS2 = tpSusunPutus(TS.id, 'setuju', { bonId: 'b1' }, W2);
cek('owner memilih bon lama 20 Agu → pembayarannya ke bon itu', PS2.dokumen && PS2.dokumen[1].data.bonId === 'b1' && PS2.dokumen[0].data.bonId === 'b1', PS2.tolak || PS2.dokumen[1].data);
cek('bayar melebihi sisa bon yang dipilih → ditolak', /Melebihi sisa/.test(tpSusunPutus(TS.id, 'setuju', { bonId: 'b1', nominal: '25.000.000' }, W2).tolak || ''));
tulis(PS);
var bon2 = hitungUtangPemasok().find(function (p) { return p.pemasok === 'RODA CONTOH'; }); var bn = bon2.bon.find(function (b) { return String(b.id) === String(BM.id); });
cek('sesudah disetujui: sisa bon kedatangan tablet = 46.250.000 − 1.000.000; laci tanggal titipan berkurang 1.000.000; titipan keluar dari perkiraan', bn && Math.round(bn.sisa) === 45250000 && laci2.seharusnya - rumusLaci('2026-09-19').seharusnya === 1000000 && tpMenungguSampai('2026-09-19').rp === titip0, [bn, laci2.seharusnya, rumusLaci('2026-09-19').seharusnya]);
var TT2 = tbmData(BM, { terbaca: false, titipSupir: 1000000 }); cek('kalimat layar tanda terima tablet menyebut uang ke supir', /dibayar ke supir Rp1\.000\.000/.test(tbmKalimatBayar(TT2)), tbmKalimatBayar(TT2));

// ---------- kabar owner ----------
cek('kabar barang masuk tampil di daftar owner sebagai kabar (bukan uang); ditandai sudah diperiksa', tpMenunggu().some(function (b) { return b.id === KBR.id && b.kabar && b.pesan; }) && tpSusunPutus(KBR.id, 'dibaca', {}, W2).dokumen[0].data.status === 'dibaca');
// ==================== TAHAP 3 (owner 26 Nov 2026): isian baru barang masuk juga di tablet — hitung tangan ====================
// Angsa 20 × 50 kg @ 13.000 = nota 1.000 kg; kurang 15 kg → 985 kg × 13.000 = Rp12.805.000 (dipotong Rp195.000); Pandan Contoh 5 karung DITOLAK;
// ongkos kirim supir Rp150.000 = titipan (bukan di kedatangan); catatan bebas untuk pemasok ikut
var DRAF3 = { pemasok: 'RODA CONTOH', bongkar: '', ongkir: '150.000', bayarSupir: '', catatanBebas: ' 1 karung sobek ', alasanPotong: 'ditimbang kurang',
  baris: [{ merk: 'Angsa', jumlahKarung: '20', beratKarung: 50, hargaPerKg: '13000', kgPotong: '15' }, { merk: 'Pandan Contoh', jumlahKarung: '5', beratKarung: 50, hargaPerKg: '14.500', ditolak: '1', alasanTolak: 'berkutu' }] };
var H3 = mtHitung(DRAF3, W); var R3 = mtSusunSimpan(DRAF3, BEN, W, true); var BM3 = R3.dokumen ? R3.dokumen[0].data : {}; var T3 = R3.dokumen && R3.dokumen[1] ? R3.dokumen[1].data : {}; var K3 = R3.dokumen && R3.dokumen[2] ? R3.dokumen[2].data : {};
cek('tablet Tahap 3: kiriman = kedatangan + titipan ongkos kirim + kabar (3 dokumen), lolos pagar kiriman Penjaga laci', !R3.tolak && R3.dokumen.length === 3 && R3.dokumen[1].koleksi === 'persetujuan' && R3.dokumen[2].data.tindakan === 'barangMasuk' && !kirim(BEN, R3, HAK_BEN).tolak && batchTablet(BM3) === true, R3.tolak || kirim(BEN, R3, HAK_BEN));
cek('tablet klaim langsung (tangan): 1.000 − 15 = 985 kg; bon Rp12.805.000; jejak potong 15 kg / Rp195.000 beralasan; tetap BON, bongkar 0', H3.potongKg === 15 && H3.potongRp === 195000 && BM3.merkList.length === 1 && BM3.merkList[0].totalKg === 985 && BM3.merkList[0].subtotalHarga === 12805000 && BM3.merkList[0].kgPotong === 15 && BM3.caraBayar === 'utang' && BM3.biayaBongkar === 0 && BM3.potongan.length === 1 && BM3.potongan[0].saatDatang === true && BM3.potongan[0].kg === 15 && BM3.potongan[0].rp === 195000 && BM3.potongan[0].alasan === 'ditimbang kurang', BM3);
cek('tablet tolak baris & catatan bebas: Pandan Contoh 5 karung tercatat ditolak (tidak di baris kedatangan), catatan bebas dirapikan', BM3.ditolak && BM3.ditolak.length === 1 && BM3.ditolak[0].merk === 'Pandan Contoh' && BM3.ditolak[0].jumlahKarung === 5 && BM3.ditolak[0].alasan === 'berkutu' && BM3.catatanBebas === '1 karung sobek', [BM3.ditolak, BM3.catatanBebas]);
cek('tablet ongkos kirim: TIDAK ditulis di kedatangan (bongkar 0, tanpa kolom ongkosKirim) — jadi titipan berjenis bongkar bertanda ongkir Rp150.000 yang menunjuk kedatangannya', BM3.ongkosKirim === undefined && H3.ongkirTitip === 150000 && H3.ongkir === 0 && T3.jenis === 'bongkar' && T3.ongkir === true && T3.nominal === 150000 && T3.batchId === String(BM3.id) && T3.teks === 'Ongkos kirim · RODA CONTOH' && /^Ongkos kirim/.test(tpTeks(T3)), [BM3.ongkosKirim, T3]);
cek('tablet: kabar owner menyebut potongan, yang ditolak, dan ongkos kirim', /DIPOTONG 15 kg \(Rp195\.000\)/.test(K3.teks) && /DITOLAK: Pandan Contoh 5 karung/.test(K3.teks) && /ongkos kirim Rp150\.000/.test(K3.teks) && /Sudah dipotong 15 kg/.test(R3.patch.kabar), [K3.teks, R3.patch && R3.patch.kabar]);
tulis(R3); var P3 = tpSusunPutus(T3.id, 'setuju', {}, W2); var B3 = P3.dokumen ? P3.dokumen.find(function (x) { return x.koleksi === 'batchMasuk'; }) : null;
cek('owner menyetujui ongkos kirim: kedatangan ditulis ulang — biayaBongkar 150.000 (dibaca mesin) DAN ongkosKirim 150.000; riwayatnya menyebut ongkos kirim', !!B3 && B3.data.biayaBongkar === 150000 && B3.data.ongkosKirim === 150000 && ckOngkir(B3.data) === 150000 && /ongkos kirim Rp150\.000/.test(B3.data.riwayat[B3.data.riwayat.length - 1].teks) && B3.data.merkList[0].totalKg === 985 && B3.data.potongan.length === 1, P3.tolak || (B3 && B3.data));
tulis(P3);
// upah bongkar 50.000 + ongkos kirim 100.000 di satu kedatangan: dua titipan (bukan kembar); keduanya disetujui → biayaBongkar 150.000, ongkos kirim 100.000
var DRAF4 = { pemasok: 'RODA CONTOH', bongkar: '50.000', ongkir: '100.000', bayarSupir: '', baris: [{ merk: 'Angsa', jumlahKarung: '30', beratKarung: 50, hargaPerKg: '13000' }] };
var R4 = mtSusunSimpan(DRAF4, BEN, W, true); var tt4 = (R4.dokumen || []).filter(function (x) { return x.koleksi === 'persetujuan' && x.data.jenis === 'bongkar'; });
cek('tablet bongkar + ongkos kirim: dua titipan terpisah (upah bongkar 50.000 tanpa tanda, ongkos kirim 100.000 bertanda)', !R4.tolak && tt4.length === 2 && tt4[0].data.nominal === 50000 && tt4[0].data.ongkir === undefined && tt4[1].data.nominal === 100000 && tt4[1].data.ongkir === true && !kirim(BEN, R4, HAK_BEN).tolak, R4.tolak || tt4);
tulis(R4); tulis(tpSusunPutus(tt4[0].data.id, 'setuju', {}, W2)); tulis(tpSusunPutus(tt4[1].data.id, 'setuju', {}, W2));
var B4 = cacheMentah('batch').find(function (b) { return String(b.id) === String(R4.dokumen[0].data.id); });
cek('keduanya disetujui (tangan): biayaBongkar 50.000 + 100.000 = 150.000; ongkosKirim 100.000 → upah bongkar 50.000', B4.biayaBongkar === 150000 && B4.ongkosKirim === 100000 && B4.biayaBongkar - ckOngkir(B4) === 50000 && B4.bongkarTitipan.length === 2, B4);
cek('tablet: ongkos kirim bukan angka DITOLAK dengan kalimat', /Ongkos kirim hanya angka/.test(mtSusunSimpan(Object.assign({}, DRAF4, { ongkir: 'seratus' }), BEN, W, true).tolak || ''));

// ==================== TAHAP 5 (owner 26 Nov 2026: "Semua tentang barang masuk adakan di tablet") — tanpa rules baru ====================
var CACHE5 = Object.assign({}, CACHE, { produksiKemasan: 'produksi' });
var tulis5 = function (r) { (r.dokumen || []).forEach(function (x) { var a = cacheMentah(CACHE5[x.koleksi] || x.koleksi).slice(); var i = a.findIndex(function (d) { return String(d.id) === String(x.data.id); }); if (i >= 0) a[i] = x.data; else a.push(x.data); pasok(x.koleksi, a); }); return r; };
var bonNama = function (n) { var p = hitungUtangPemasok().find(function (x) { return x.pemasok === n; }); return p ? Math.round(p.totalUtang) : 0; };
// (a) KEMASAN JADI dari tablet. Tangan: Angsa 10 × 50 @ 13.000 = Rp6.500.000 + Angsa Mini 20 kemasan × 5 kg @ 14.000 = Rp1.400.000 → bon + Rp7.900.000; modal per kemasan 1.400.000 ÷ 20 = Rp70.000
var bon5 = bonNama('RODA CONTOH');
var DRAF5 = { pemasok: 'RODA CONTOH', baris: [{ merk: 'Angsa', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '13000' }, { masuk: 'kemasan', merk: 'Angsa Mini', jumlahKarung: '20', beratKarung: 5, hargaPerKg: '14000' }] };
var H5 = mtHitung(DRAF5, W); var R5 = mtSusunSimpan(DRAF5, BEN, W, true); var BM5 = R5.dokumen ? R5.dokumen[0].data : {}; var PK5 = (R5.dokumen || []).filter(function (x) { return x.koleksi === 'produksiKemasan'; }); var K5 = (R5.dokumen || []).filter(function (x) { return x.koleksi === 'persetujuan'; });
cek('Tahap 5 kemasan jadi dari tablet (tangan): kedatangan (baris karung + baris kemasan berbentuk bal Rp1.400.000) + SATU beli-jadi 20 unit bermodal Rp70.000 yang menunjuk kedatangannya + kabar; nilai Rp7.900.000; tetap BON, bongkar 0', !R5.tolak && H5.nilai === 7900000 && H5.unitKemasan === 20 && R5.dokumen.length === 3 && BM5.merkList.length === 2 && BM5.merkList[1].bentuk === 'bal' && BM5.merkList[1].kemasanJadi === true && BM5.merkList[1].subtotalHarga === 1400000 && BM5.caraBayar === 'utang' && BM5.biayaBongkar === 0 && BM5.dariTablet === true
  && PK5.length === 1 && PK5[0].data.beliJadi === true && String(PK5[0].data.dariBatch) === String(BM5.id) && PK5[0].data.jumlahUnit === 20 && PK5[0].data.hppPerUnit === 70000 && PK5[0].data.ukuranKemasan === 5 && K5.length === 1 && K5[0].data.nominal === 7900000 && /20 kemasan Angsa Mini 5 kg/.test(K5[0].data.teks) && /KEMASAN JADI/.test(K5[0].data.teks), R5.tolak || [R5.dokumen.map(function (x) { return x.koleksi; }), BM5.merkList, PK5, K5]);
cek('Tahap 5 kemasan jadi: lolos pagar kiriman Penjaga laci — juga bila kisi ADUKAN-nya "tidak boleh" (pasangan beli-jadi bagian dari kedatangan); karyawan tetap ditolak; beli-jadi TANPA kedatangan tablet tetap dihitung adukan', !kirim(BEN, R5, HAK_BEN).tolak && !kirim(BEN, R5, Object.assign({}, HAK_BEN, { adukan: 'tidak' })).tolak && !!kirim(KRY, R5, HAK_KRY).tolak
  && !!kirim(BEN, { dokumen: [PK5[0]] }, Object.assign({}, HAK_BEN, { adukan: 'tidak' })).tolak && !!kirim(BEN, { dokumen: [R5.dokumen[0], { koleksi: 'produksiKemasan', data: Object.assign({}, PK5[0].data, { dariBatch: 'kedatangan-lain' }) }] }, Object.assign({}, HAK_BEN, { adukan: 'tidak' })).tolak && !!kirim(BEN, R5, Object.assign({}, HAK_BEN, { kedatangan: 'tidak' })).tolak, [kirim(BEN, R5, Object.assign({}, HAK_BEN, { adukan: 'tidak' })), kirim(KRY, R5, HAK_KRY)]);
tulis5(R5);
cek('Tahap 5 kemasan jadi (tangan, sesudah tersimpan): bon RODA CONTOH naik TEPAT Rp7.900.000; buku Kemasan "Angsa Mini 5 kg" = 20 unit; tidak ada buku beras "Angsa Mini"', bonNama('RODA CONTOH') - bon5 === 7900000 && (hitungStokKemasan()[kunciKemasan('Angsa Mini', 5)] || {}).sisaUnit === 20 && hitungStokKarungPerMerk()['Angsa Mini'] === undefined, [bonNama('RODA CONTOH') - bon5, hitungStokKemasan()[kunciKemasan('Angsa Mini', 5)]]);
cek('Tahap 5 kemasan jadi: paling banyak 8 baris kemasan satu kedatangan tablet (batas yang diukur peta_akses) — 9 baris DITOLAK dengan kalimat, 8 lolos', MT_BATAS.kemasan === 8 && (function () { var b = []; for (var q = 0; q < 9; q++) b.push({ masuk: 'kemasan', merk: 'Mini ' + q, jumlahKarung: '2', beratKarung: 5, hargaPerKg: '14000' }); var X = mtSusunSimpan({ pemasok: 'RODA CONTOH', baris: b }, BEN, W, true); var Y = mtSusunSimpan({ pemasok: 'RODA CONTOH', baris: b.slice(0, 8) }, BEN, W, true); return /Paling banyak 8 baris kemasan jadi/.test(X.tolak || '') && !Y.tolak && Y.dokumen.filter(function (x) { return x.koleksi === 'produksiKemasan'; }).length === 8 && !kirim(BEN, Y, HAK_BEN).tolak; })());
cek('Tahap 5 kemasan jadi: jumlah pecahan / nama kosong DITOLAK dengan kalimat', /bilangan bulat/.test(mtSusunSimpan({ pemasok: 'RODA CONTOH', baris: [{ masuk: 'kemasan', merk: 'Angsa Mini', jumlahKarung: '2,5', beratKarung: 5, hargaPerKg: '14000' }] }, BEN, W, true).tolak || '') && /nama kemasannya belum diisi/.test(mtSusunSimpan({ pemasok: 'RODA CONTOH', baris: [{ masuk: 'kemasan', merk: '', jumlahKarung: '2', beratKarung: 5, hargaPerKg: '14000' }] }, BEN, W, true).tolak || ''));
// (b) CATATAN UNTUK PEMASOK & KLAIM saat mencatat. Tangan: Angsa 20 × 50 = 1.000 kg, ditimbang 990 → kurang 10 kg × 13.000 = Rp130.000 (nilai klaim dari timbang); bon TETAP 1.000 × 13.000 = Rp13.000.000
var DRAF6 = { pemasok: 'RODA CONTOH', baris: [{ merk: 'Angsa', jumlahKarung: '20', beratKarung: 50, hargaPerKg: '13000', timbangKg: '990' }], klaimCara: 'potong',
  catatan: [{ jenis: 'kurang', merk: 'Angsa', jumlah: '10', satuan: 'kg', ket: 'hasil timbang' }, { jenis: 'tertinggal', merk: 'Pandan Contoh', jumlah: '2', satuan: 'karung', ket: '' }, { jenis: 'kurang', merk: '', jumlah: '', satuan: 'kg', ket: '' }] };
var R6 = mtSusunSimpan(DRAF6, BEN, W, true); var BM6 = R6.dokumen ? R6.dokumen[0].data : {}; var bon6 = bonNama('RODA CONTOH');
cek('Tahap 5 catatan saat mencatat (tangan): 2 baris tersimpan di kedatangan (baris kosong dibuang) + klaim "minta dipotong" berstatus sudah disampaikan senilai Rp130.000; kg & bon TIDAK berubah (1.000 kg, Rp13.000.000)', !R6.tolak && BM6.catatanPemasok.length === 2 && BM6.catatanPemasok[0].jenis === 'kurang' && BM6.catatanPemasok[0].jumlah === 10 && BM6.catatanPemasok[1].jenis === 'tertinggal' && BM6.catatanPemasok[1].satuan === 'karung'
  && BM6.klaim.cara === 'potong' && BM6.klaim.status === 'diminta' && BM6.klaim.nilai === 130000 && BM6.klaim.dibukukan === undefined && BM6.merkList[0].totalKg === 1000 && BM6.merkList[0].subtotalHarga === 13000000 && BM6.merkList[0].kgPotong === undefined && !kirim(BEN, R6, HAK_BEN).tolak && /catatan untuk pemasok 2 baris \(minta dipotong/.test(R6.dokumen[R6.dokumen.length - 1].data.teks), R6.tolak || [BM6.catatanPemasok, BM6.klaim, kirim(BEN, R6, HAK_BEN)]);
tulis5(R6);
cek('Tahap 5 catatan saat mencatat: bon naik TEPAT Rp13.000.000; suratnya langsung bisa dicetak dari kartu tanda terima (cpIsiSurat.bisaCetak) dan memuat catatan & permintaannya', bonNama('RODA CONTOH') - bon6 === 13000000 && cpIsiSurat(BM6.id).bisaCetak === true && cpIsiSurat(BM6.id).ada === true && cpIsiSurat(BM6.id).baris.some(function (b) { return /Kurang · Angsa · 10 kg — hasil timbang/.test(b.nama); }) && cpIsiSurat(BM6.id).baris.some(function (b) { return /Minta dipotong/.test(b.nama) && b.n === 130000; }), cpIsiSurat(BM6.id).baris);
cek('Tahap 5 catatan saat mencatat: DITOLAK dengan kalimat — baris kurang tanpa jumlah, cara klaim tanpa baris, cara klaim tak dikenal; tanpa catatan = kedatangan berbentuk lama (tanpa kolom catatan / klaim)', /jumlahnya belum diisi/.test(mtSusunSimpan(Object.assign({}, DRAF6, { catatan: [{ jenis: 'kurang', merk: 'Angsa', jumlah: '', satuan: 'kg', ket: 'x' }] }), BEN, W, true).tolak || '') && /Klaim butuh minimal satu baris/.test(mtSusunSimpan(Object.assign({}, DRAF6, { catatan: [] }), BEN, W, true).tolak || '')
  && /Cara klaim tidak dikenal/.test(mtSusunSimpan(Object.assign({}, DRAF6, { klaimCara: 'entah' }), BEN, W, true).tolak || '') && (function () { var X = mtSusunSimpan(Object.assign({}, DRAF6, { catatan: [], klaimCara: '' }), BEN, W, true); return !X.tolak && X.dokumen[0].data.catatanPemasok === undefined && X.dokumen[0].data.klaim === undefined && X.dokumen[0].data.usulPakaiPotong === undefined; })());
// (c) POTONGAN YANG MENUNGGU — dari tablet hanya USUL. PEMASOK P tunai 18 Sep (belum termuat patokan 15 Sep): Angsa 4 × 50 @ 13.000 = Rp2.600.000; retur 10 kg = Rp130.000 dipotong di pembelian berikutnya
var W18 = { tanggal: '2026-09-18', jam: '09:00', kini: '2026-09-18T02:00:00.000Z', idUnik: W2.idUnik };
var dP = drafMasukKosong(W18); dP.pemasok = 'PEMASOK P'; dP.caraBayar = 'tunai'; dP.baris = [Object.assign(barisMasukKosong(), { merk: 'Angsa', jumlahKarung: '4', beratKarung: 50, hargaPerKg: '13000', varian: 'sama' })];
var SP = susunSimpanMasuk(dP, W18, true); tulis5(SP); var idP = SP.dokumen[0].data.id; tulis5(susunReturPemasok(idP, { merk: 'Angsa', kg: '10', alasan: 'berkutu', tempat: 'berikut' }, W18));
var DRAF7 = { pemasok: 'PEMASOK P', pakaiPotong: '1', baris: [{ merk: 'Angsa', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '13000' }] };
var H7 = mtHitung(DRAF7, W); var R7 = mtSusunSimpan(DRAF7, BEN, W, true); var BM7 = R7.dokumen ? R7.dokumen[0].data : {};
cek('Tahap 5 potongan menunggu dari tablet = USUL (tangan): ditawarkan Rp130.000; kedatangan Rp6.500.000 tersimpan PENUH berkolom usulPakaiPotong 130.000 — TANPA potonganPakai, tanpa dokumen patokan kas, tanpa bayar bon; kabar owner menyebut usulnya', ptMenunggu('PEMASOK P').length === 1 && H7.potongTunggu === 130000 && H7.usulPotong === true && !R7.tolak && BM7.usulPakaiPotong.rp === 130000 && BM7.usulPakaiPotong.dari.length === 1 && String(BM7.usulPakaiPotong.dari[0].id) === String(idP) && BM7.potonganPakai === undefined && BM7.merkList[0].subtotalHarga === 6500000
  && !R7.dokumen.some(function (x) { return x.koleksi === 'pengaturan' || x.koleksi === 'utangPemasokMutasi'; }) && !kirim(BEN, R7, HAK_BEN).tolak && /USUL: potong Rp130\.000/.test(R7.dokumen[R7.dokumen.length - 1].data.teks) && /DIUSULKAN ke owner/.test(R7.patch.kabar), R7.tolak || [H7.tunggu, BM7.usulPakaiPotong, R7.dokumen.map(function (x) { return x.koleksi; })]);
cek('Tahap 5 potongan dari tablet: tanpa diketuk = tidak ada usul; potongan lebih besar dari nilai barang (1 karung 5 kg = Rp65.000) DITOLAK dengan kalimat', (function () { var X = mtSusunSimpan(Object.assign({}, DRAF7, { pakaiPotong: '' }), BEN, W, true); return !X.tolak && X.dokumen[0].data.usulPakaiPotong === undefined && X.hitung.potongTunggu === 130000; })() && /lebih besar dari nilai barang/.test(mtSusunSimpan({ pemasok: 'PEMASOK P', pakaiPotong: '1', baris: [{ merk: 'Angsa', jumlahKarung: '1', beratKarung: 5, hargaPerKg: '13000' }] }, BEN, W, true).tolak || ''));
tulis5(R7); var kas7 = kasPada(); var lac7 = ambilTitikKas().laci;
cek('Tahap 5 sebelum owner memutuskan (tangan): bon PEMASOK P PENUH Rp6.500.000; potongannya MASIH menunggu & masih piutang ke pemasok Rp130.000; "tidak dipakai" hanya melepas kolom usul (bon tetap penuh)', bonNama('PEMASOK P') === 6500000 && ptMenunggu('PEMASOK P').length === 1 && piutangPemasokPada().rp === 130000 && ingatNeraca().piutangPemasok === 130000 && (function () { var X = susunLepasUsulPakai(BM7.id, W2); return !X.tolak && X.dokumen.length === 1 && X.dokumen[0].data.usulPakaiPotong === undefined && X.dokumen[0].data.potonganPakai === undefined && X.dokumen[0].data.merkList[0].subtotalHarga === 6500000; })(), [bonNama('PEMASOK P'), piutangPemasokPada()]);
var PU = ptUsulPakai(BM7.id, W2.tanggal); var S7 = susunSetujuPakaiPotong(BM7.id, W2); var by7 = (S7.dokumen || []).filter(function (x) { return x.koleksi === 'utangPemasokMutasi'; }); var tk7 = (S7.dokumen || []).filter(function (x) { return x.koleksi === 'pengaturan'; });
cek('Tahap 5 OWNER menyetujui 20 Sep (tangan): kedatangan + potonganPakai 130.000 (usul dilepas), satu "bayar bon" Rp130.000 dari laci bertanggal 20 Sep yang menunjuk bon itu, patokan laci + 130.000', !PU.tolak && PU.rp === 130000 && PU.sisaBon === 6500000 && PU.dalamTitik === false && !S7.tolak && S7.dokumen.length === 3 && S7.dokumen[0].data.potonganPakai.rp === 130000 && S7.dokumen[0].data.potonganPakai.disetujui.tanggal === '2026-09-20' && S7.dokumen[0].data.usulPakaiPotong === undefined
  && by7.length === 1 && by7[0].data.tipe === 'bayar' && by7[0].data.nominal === 130000 && by7[0].data.tanggal === '2026-09-20' && String(by7[0].data.bonId) === String(BM7.id) && by7[0].data.pemasok === 'PEMASOK P' && by7[0].data.dari === 'laci' && tk7.length === 1 && tk7[0].data.laci === lac7 + 130000 && /bonnya tinggal Rp\s?6\.370\.000/.test(S7.patch.kabar), S7.tolak || [PU, by7, tk7]);
tulis5(S7);
cek('Tahap 5 sesudah disetujui (tangan): bon PEMASOK P TEPAT Rp6.370.000 (6.500.000 − 130.000); kas di buku TIDAK berubah; potongan tidak menunggu lagi, piutang ke pemasok Rp0 — tetapi neraca 19 Sep (sebelum disetujui) masih membawanya Rp130.000; tidak bisa disetujui dua kali', bonNama('PEMASOK P') === 6370000 && kasPada() - kas7 === 0 && ptMenunggu('PEMASOK P').length === 0 && piutangPemasokPada().rp === 0 && piutangPemasokPada('2026-09-19').rp === 130000 && piutangPemasokPada('2026-09-20').rp === 0
  && /tidak punya usul/.test(susunSetujuPakaiPotong(BM7.id, W2).tolak || '') && /sudah dipotong di kedatangan/.test(J(cpBaca(cacheMentah('batch').find(function (b) { return String(b.id) === String(idP); })).potongan.map(function (x) { return x.dipakai ? 'sudah dipotong di kedatangan' : ''; }))), [bonNama('PEMASOK P'), kasPada() - kas7, piutangPemasokPada('2026-09-19')]);
// usul yang potongannya keburu dipakai di tempat lain → ditolak dengan kalimat; kedatangan TUNAI tidak punya jalan ini
cek('Tahap 5 usul pakai potongan: potongannya sudah tidak menunggu → DITOLAK dengan kalimat (tanpa dokumen)', (function () { var b = JSON.parse(J(cacheMentah('batch').find(function (x) { return String(x.id) === String(BM6.id); }))); b.usulPakaiPotong = { rp: 130000, dari: [{ id: String(idP), i: 0, rp: 130000 }] }; var a = cacheMentah('batch').map(function (x) { return String(x.id) === String(b.id) ? b : x; }); pasok('batchMasuk', a);
  var X = susunSetujuPakaiPotong(BM6.id, W2); var Y = ptUsulPakai(BM6.id, W2.tanggal); delete b.usulPakaiPotong; pasok('batchMasuk', cacheMentah('batch').map(function (x) { return String(x.id) === String(b.id) ? b : x; })); return /sudah tidak menunggu/.test(X.tolak || '') && !X.dokumen && Y.ada === true && Y.usulRp === 130000; })());
// (d) USUL untuk kedatangan yang SUDAH tersimpan (BM6: Angsa 1.000 kg bon) — owner yang membukukan
var U1 = mtSusunUsul({ id: BM6.id, jenis: 'catatan', baris: [{ jenis: 'kurang', merk: 'Angsa', jumlah: '12', satuan: 'kg', ket: 'timbang ulang' }], cara: 'potong', status: 'disetujui', bebas: 'mohon dipotong di bon ini' }, BEN, W);
cek('Tahap 5 usul catatan dari tablet: SATU dokumen kabar barang masuk (menunggu, atas nama yang jaga, menunjuk kedatangannya) berkolom usul; kedatangan TIDAK ditulis; lolos pagar Penjaga laci, karyawan ditolak', !U1.tolak && U1.dokumen.length === 1 && U1.dokumen[0].koleksi === 'persetujuan' && U1.dokumen[0].data.tindakan === 'barangMasuk' && U1.dokumen[0].data.status === 'menunggu' && U1.dokumen[0].data.batchId === String(BM6.id) && U1.dokumen[0].data.mintaUid === 'uid-tablet' && U1.dokumen[0].data.usul.jenis === 'catatan' && U1.dokumen[0].data.usul.baris[0].jumlah === 12 && U1.dokumen[0].data.usul.status === 'disetujui'
  && /USUL catatan untuk pemasok/.test(U1.dokumen[0].data.teks) && /Kurang Angsa 12 kg/.test(U1.dokumen[0].data.teks) && !kirim(BEN, U1, HAK_BEN).tolak && !!kirim(KRY, mtSusunUsul({ id: BM6.id, jenis: 'koreksi', teks: 'harga salah ketik' }, KRY, W), HAK_KRY).tolak, U1.tolak || U1.dokumen[0].data);
tulis5(U1); var UM = mtUsulMenunggu(BM6.id); var DU = mtDrafDariUsul(BM6.id, UM.length ? UM[0].pid : '');
cek('Tahap 5 owner membuka usul catatan: terdaftar menunggu di kedatangannya; lembar catatan terisi dari usul (12 kg, minta dipotong, disetujui pemasok); catatan kedatangan BELUM berubah (masih 2 baris, 10 kg)', UM.length === 1 && UM[0].usul.jenis === 'catatan' && !!DU && DU.cpDraf.baris.length === 1 && DU.cpDraf.baris[0].jumlah === '12' && DU.cpDraf.cara === 'potong' && DU.cpDraf.status === 'disetujui' && DU.cpDraf.usulId === UM[0].pid && DU.cpDraf.bebas === 'mohon dipotong di bon ini' && cpKedatangan(BM6.id).catatan.length === 2 && cpKedatangan(BM6.id).catatan[0].jumlah === 10, [UM, DU]);
var SO = susunCatatanPemasok(BM6.id, DU.cpDraf, W2); var PO = tpSusunPutus(UM[0].pid, 'dibaca', { balasan: 'sudah disimpan' }, W2); tulis5(SO); tulis5(PO);
cek('Tahap 5 owner menyimpan usul catatan: catatan kedatangan jadi 1 baris 12 kg berklaim "disetujui pemasok"; usulnya tidak menunggu lagi; bon belum berubah (membukukan potong bon tetap ketukan owner sendiri)', !SO.tolak && cpKedatangan(BM6.id).catatan.length === 1 && cpKedatangan(BM6.id).catatan[0].jumlah === 12 && cpKedatangan(BM6.id).klaim.status === 'disetujui' && cpKedatangan(BM6.id).bebas === 'mohon dipotong di bon ini' && mtUsulMenunggu(BM6.id).length === 0 && cpKedatangan(BM6.id).nilaiBon === 13000000 && !hitungPotongKlaim(BM6.id).tolak && hitungPotongKlaim(BM6.id).rp === 156000, [SO.tolak, cpKedatangan(BM6.id).catatan, hitungPotongKlaim(BM6.id)]);
// retur: usul 25 kg Angsa → owner membukukan: bon turun 25 × 13.000 = Rp325.000
var bon8 = bonNama('RODA CONTOH'); var U2 = mtSusunUsul({ id: BM6.id, jenis: 'retur', merk: 'Angsa', kg: '25', alasan: 'berkutu' }, BEN, W);
cek('Tahap 5 usul kembalikan ke pemasok: tersusun (Angsa 25 kg, beralasan) TANPA mengubah stok / bon; DITOLAK dengan kalimat — alasan pendek, kg lebih dari sisa buku, kg kosong, nama bukan baris kedatangan itu', !U2.tolak && U2.dokumen.length === 1 && U2.dokumen[0].data.usul.jenis === 'retur' && U2.dokumen[0].data.usul.kg === 25 && U2.dokumen[0].data.usul.merk === 'Angsa' && bonNama('RODA CONTOH') === bon8 && !kirim(BEN, U2, HAK_BEN).tolak
  && /alasan/.test(mtSusunUsul({ id: BM6.id, jenis: 'retur', merk: 'Angsa', kg: '25', alasan: 'x' }, BEN, W).tolak || '') && /Berapa kg/.test(mtSusunUsul({ id: BM6.id, jenis: 'retur', merk: 'Angsa', kg: '', alasan: 'berkutu' }, BEN, W).tolak || '') && /tidak ada di baris kedatangan/.test(mtSusunUsul({ id: BM6.id, jenis: 'retur', merk: 'Entah', kg: '5', alasan: 'berkutu' }, BEN, W).tolak || '') && /menghabiskan seluruh baris|sisa di buku/.test(mtSusunUsul({ id: BM6.id, jenis: 'retur', merk: 'Angsa', kg: '99999', alasan: 'berkutu' }, BEN, W).tolak || ''), U2.tolak || U2.dokumen[0].data);
tulis5(U2); var UM2 = mtUsulMenunggu(BM6.id); var DR2 = mtDrafDariUsul(BM6.id, UM2[0].pid); var SR2 = susunReturPemasok(BM6.id, DR2.rtDraf, W2); tulis5(SR2);
cek('Tahap 5 owner membukukan usul kembalikan (tangan): lembar terisi Angsa 25 kg "berkutu"; sesudah owner mengetuk, bon RODA CONTOH turun TEPAT Rp325.000', DR2.rtDraf.merk === 'Angsa' && DR2.rtDraf.kg === '25' && DR2.rtDraf.alasan === 'berkutu' && DR2.rtDraf.usulId === UM2[0].pid && !SR2.tolak && bon8 - bonNama('RODA CONTOH') === 325000, [DR2, SR2.tolak, bon8 - bonNama('RODA CONTOH')]);
var U3 = mtSusunUsul({ id: BM6.id, jenis: 'koreksi', teks: 'harga Angsa seharusnya 13.100' }, BEN, W); var U4 = mtSusunUsul({ id: BM6.id, jenis: 'hapus', teks: 'tercatat dua kali' }, BEN, W);
cek('Tahap 5 usul pembetulan & hapus: hanya kalimat untuk owner (tidak ada lembar yang terisi sendiri); DITOLAK dengan kalimat — kalimat kurang dari 5 huruf, jenis tak dikenal, kedatangan tidak ada, belum masuk; usul catatan kosong', !U3.tolak && U3.dokumen[0].data.usul.jenis === 'koreksi' && /USUL pembetulan kedatangan/.test(U3.dokumen[0].data.teks) && !U4.tolak && /USUL hapus kedatangan/.test(U4.dokumen[0].data.teks) && (function () { tulis5(U3); var m = mtUsulMenunggu(BM6.id).find(function (x) { return x.usul.jenis === 'koreksi'; }); return !!m && mtDrafDariUsul(BM6.id, m.pid) === null; })()
  && /paling sedikit 5 huruf/.test(mtSusunUsul({ id: BM6.id, jenis: 'koreksi', teks: 'x' }, BEN, W).tolak || '') && /Pilih dulu jenis usulnya/.test(mtSusunUsul({ id: BM6.id, jenis: 'entah' }, BEN, W).tolak || '') && /tidak ditemukan/.test(mtSusunUsul({ id: 'tidak-ada', jenis: 'koreksi', teks: 'harga salah' }, BEN, W).tolak || '') && /Belum masuk/.test(mtSusunUsul({ id: BM6.id, jenis: 'koreksi', teks: 'harga salah' }, null, W).tolak || '') && /Tulis dulu catatannya/.test(mtSusunUsul({ id: BM6.id, jenis: 'catatan', baris: [], bebas: '' }, BEN, W).tolak || ''), [U3.tolak, U4.tolak]);
print(J(hasil));
"""


def baca_semua():
    return dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(MODUL + STATIS)))


def rakit(t):
    isi = lambda m: t[m] if m in t else open(os.path.join(AKAR, m), encoding='utf-8').read()
    return '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(isi(m)) for m in bundel_baru.lengkapi(MODUL)])


def jalankan(t):
    js = UB.JAM_TETAP + rakit(t) + '\nvar KOTAK = ' + json.dumps(kotak()) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    keluar = (r.stdout or '').strip().split('\n')[-1] if r.stdout else ''
    if r.returncode != 0 or not keluar.startswith('['): return [{'nama': 'jsc jalan', 'ok': False, 'ket': ((r.stderr or '') + (r.stdout or ''))[-1500:]}]
    return json.loads(keluar)


def periksa_statis(t):
    c = []; ok = lambda n, x, k='': c.append({'nama': 'statis: ' + n, 'ok': bool(x), 'ket': k})
    S = t[STK]
    ok('Stok: akun tablet menyimpan lewat mtSusunSimpan (owner tetap susunSimpanMasuk)', "const r = bukanOwner(akM) ? MT.mtSusunSimpan(d, akM, waktu(), st().yakinM) : C.susunSimpanMasuk(d, waktu(), st().yakinM);" in S)
    ok('Stok: akun tablet menggambar form tablet', "if (bukanOwner(opsi.akun ? opsi.akun() : null)) return gambarMasukTablet(s);" in S)
    m = re.search(r'\n  function gambarMasukTablet\(s\) \{\n(.*?)\n  \}\n', S, re.S); f = m.group(1) if m else ''
    ok('form tablet: tanpa pilihan cara bayar / tanggal / koreksi / hapus / aturan; ada upah bongkar & bayar ke supir', f and not re.search(r"caraBayar|mTanggal|mKoreksi|mHapus|bukaAturC|mKelas|mVarian", f) and 'data-kolom="bongkar"' in f and 'data-kolom="bayarSupir"' in f, len(f))
    ok('form tablet: merek baru diberi pita "tetap dicatat, owner dikabari" (bukan penolakan)', 'data-k="mt-baru-${i}"' in f and "b.merekBaru ? 'merek baru" in f)
    ok('Stok: draf kosong tablet = mtDrafKosong (selalu bon)', "bukanOwner(opsi.akun ? opsi.akun() : null) ? MT.mtDrafKosong(waktu()) : C.drafMasukKosong(waktu())" in S)
    U = t[UG]
    ok('Uang: owner memilih bon untuk bayar supir & melihat ke mana titipan barang masuk ditulis', 'ukTtBon: ({ b }) =>' in U and 'bonId: t.bonId || \'\'' in U and 'function tujuanTitip(t)' in U and '${tujuanTitip(t)}' in U)
    ok('Uang: kabar barang masuk ditandai "Sudah diperiksa"', "p.kabar ? 'Sudah diperiksa' : 'Tandai dibaca'" in U)
    ok('papan Persetujuan & notifikasi dalam aplikasi mengenal kabar barang masuk', "m.tindakan === TP_PESAN || m.tindakan === TP_KABAR) return tpSusunPutus(id, 'dibaca'" in t[SL] and "barangMasuk: 'Barang masuk dari tablet'" in t[KB])
    ok('tanda terima: titipan bayar supir ikut (menunggu selalu; disetujui hanya bila buku bon tak terbaca)', "titipSupir: titipSupir(batch, terbaca)" in t[TBP] and "m.jenis === 'bayarBon' && String(m.batchId || '') === String(batch.id)" in t[TBP])
    ok('kartu titipan tablet: bayar bon pemasok memilih / mengetik pemasok', "data-aksi=\"tpPemasok\"" in t[TPP] and "tpPemasok: ({ p }) =>" in t[TPP])
    ok('index.html memuat masuk-tablet-logika lebih dulu (modulepreload)', '<link rel="modulepreload" href="js/layar/masuk-tablet-logika.js">' in t[IDX])
    ok('push HP menyebut upah bongkar, bayar bon pemasok, barang masuk', "bongkar: 'Upah bongkar', bayarBon: 'Bayar bon pemasok'" in t[FN] and "barangMasuk: 'Barang masuk'" in t[FN])
    ok('rules v15: kedatangan tablet lewat stafCatatMasuk([ben]); kabar lewat stafKabarMasuk([ben])', "(stafCatatMasuk(['ben']) && tglStaf('tanggal'))" in t[RULES] and "stafKabarMasuk(['ben']) || (stafHitungLaci(" in t[RULES])   # v16: baris create persetujuan bersambung
    # Tahap 5 (owner 26 Nov 2026): semua tentang barang masuk ada di tablet — kemasan jadi, catatan & klaim, usul pakai potongan, usul kedatangan tersimpan
    ok('Tahap 5 form tablet: baris bisa dijadikan KEMASAN JADI; baris kemasan tanpa potong / tolak / timbang', 'data-k="mt-kj-${i}" data-aksi="mPilih" data-kolom="masuk"' in f and "${b.kemasan || d.baris[i].ditolak ? '' : pilPotong(b, d.baris[i], i)}" in f and "${b.kemasan ? '' : gambarCekMasuk(b, d.baris[i], i, a)}" in f)
    ok('Tahap 5 form tablet: kartu catatan untuk pemasok & cara klaim; bisa diisi dari hasil timbang', 'data-k="mt-catatan"' in f and "${editorCatatan(d.catatan || [], 'mc')}" in f and 'data-aksi="mcPilih" data-kolom="klaimCara"' in f and 'data-aksi="mcTimbang"' in f)
    ok('Tahap 5 form tablet: potongan yang menunggu hanya DIUSULKAN (kalimatnya menyebut bon dicatat penuh dulu)', 'data-k="mt-pakai"' in f and "'USULKAN POTONG DI KEDATANGAN INI'" in f and 'Bon dicatat <b>penuh ${RP(hm.nilai)}</b> dulu' in f)
    ok('Tahap 5 form tablet: modal per kemasan TIDAK ditampilkan (modal tersembunyi di tablet)', 'hppPerUnit' not in f and 'hppPerKg' not in f)
    ok('Tahap 5 form tablet: jalan ke kedatangan tersimpan', 'data-aksi="bukaTerima" data-k="mt-ke-tersimpan"' in f)
    ok('Tahap 5 Stok: kartu usul tablet hanya untuk akun bukan-owner & terpasang di lembar kedatangan tersimpan', "if (!id || !bukanOwner(ak)) return '';" in S and "bawah: gambarUsulTablet(s) })" in S and "${o.bawah || ''}" in t[TBP])
    ok('Tahap 5 Stok: usul dikirim lewat mtSusunUsul (tablet tidak menulis kedatangan tersimpan)', "if (await tulis(MT.mtSusunUsul(d, opsi.akun ? opsi.akun() : null, waktu()))) set({ usDraf: null });" in S and 'data-aksi="usKirim"' in S)
    ok('Tahap 5 Stok owner: kartu "Usul dari tablet" di Koreksi kedatangan — setujui pakai potongan dua ketukan, usul catatan / kembalikan mengisi lembarnya', '${gambarUsulOwner(s, id, K)}' in S and "ppSetuju: async ({ id }) => { if (st().ppYakin !== String(id)) return set({ ppYakin: String(id), kabar: '' }); if (await tulis(C.susunSetujuPakaiPotong(id, waktu())))" in S and 'data-aksi="usulPakai"' in S and 'data-aksi="usulSelesai"' in S)
    ok('Tahap 5 Stok owner: menyimpan lembar yang diisi dari usul ikut menandai usulnya sudah diperiksa', "denganUsulSelesai(C.susunCatatanPemasok(d.id, d, waktu()), d.usulId," in S and "denganUsulSelesai(C.susunReturPemasok(d.id, d, waktu()), d.usulId," in S and "const p = tpSusunPutus(pid, 'dibaca', { balasan }, waktu());" in S)
    ok('Tahap 5: tanpa rules baru — kedatangan tablet tetap lewat stafCatatMasuk, pasangan beli-jadi lewat create produksiKemasan staf (sejak v3), usul lewat stafKabarMasuk', "(stafBuat(['ben', 'karyawan']) && tglStaf('tanggal'));   // adukan" in t[RULES] and 'ATURAN FIRESTORE v20 FINAL' in t[RULES])
    ok('logika tablet tidak menulis sendiri (hanya menyusun)', not re.search(r'tulisDokumen|setDoc|import .*firebase', t[MT]))
    return c


def periksa(t, diam=False):
    c = jalankan(t) + periksa_statis(t)
    g = [x for x in c if not x['ok']]
    if not diam:
        for x in c: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:700]))
        print('BARANG MASUK DARI TABLET: %d lulus · %d gagal' % (len(c) - len(g), len(g)))
    return g


def main():
    t = baca_semua()
    if '--kontrol' in sys.argv:
        M = t[MT]; T = t[TPL]; A = t[AK]; TB = t[TBL]
        rusak = [
            ('kedatangan tablet tercatat tunai (laci berkurang tanpa titipan)', MT, M.replace("d.id = null; d.tanggal = w.tanggal; d.caraBayar = 'utang';", "d.id = null; d.tanggal = w.tanggal;").replace("{ dariTablet: true, biayaBongkar: 0, caraBayar: 'utang' }", "{ dariTablet: true, biayaBongkar: 0 }")),
            ('kedatangan tablet memakai tanggal draf', MT, M.replace("d.id = null; d.tanggal = w.tanggal;", "d.id = null;")),
            ('upah bongkar ikut ditulis di kedatangan (terhitung dua kali sesudah disetujui)', MT, M.replace("{ dariTablet: true, biayaBongkar: 0, caraBayar: 'utang' }", "{ dariTablet: true, biayaBongkar: bongkar, caraBayar: 'utang' }")),
            ('tanpa kabar owner', MT, M.replace("  dokumen.push(tpDokKabarMasuk({ batchId: id, pemasok, nominal: nilai, teks: teksKabar, hargaBeda: beda }, akun, w));\n", "")),
            ('merek baru ditolak lagi dari tablet', MT, M.replace("    if (b.terisi && !b.masalah && b.vr && b.vr.arsip) b.masalahTablet", "    if (b.terisi && !b.masalah && b.baru) b.masalahTablet = 'merek baru';\n    else if (b.terisi && !b.masalah && b.vr && b.vr.arsip) b.masalahTablet")),
            ('merek baru tablet memakai tebakan kelas', MT, M.replace(" d.tanpaTebakKelas = true;", "")),
            ('jalur owner kehilangan tebakan kelas', SC, t[SC].replace("baru && !draf.tanpaTebakKelas ? kmKelasMerk(merkKetik)", "baru && false ? kmKelasMerk(merkKetik)")),
            ('merek baru tidak ditandai', MT, M.replace("if (merekBaru.length) bm.merekBaru = merekBaru;", "")),
            ('kabar owner tidak menyebut merek baru', MT, M.replace("(merekBaru.length ? ' · MEREK BARU: '", "(false ? ' · MEREK BARU: '")),
            ('nama arsip boleh dari tablet', MT, M.replace("if (b.terisi && !b.masalah && b.vr && b.vr.arsip) b.masalahTablet", "if (false) b.masalahTablet")),
            ('harga beda tidak ditandai', MT, M.replace("if (beda.length) bm.hargaBeda = beda;", "")),
            ('Tahap 3: ongkos kirim tablet ikut ditulis di kedatangan', MT, M.replace("d.bongkar = ''; d.ongkir = '';", "d.bongkar = '';")),
            ('Tahap 3: ongkos kirim disetujui sebagai upah bongkar', TPL, T.replace("const ok = m.ongkir === true;", "const ok = false;")),
            ('Tahap 3: titipan ongkos kirim tanpa tanda', TPL, T.replace("  if (d.ongkir && jenis === 'bongkar') data.ongkir = true;\n", "")),
            ('Tahap 3: kabar owner tidak menyebut potongan', MT, M.replace("(h.potongKg > 0 ? ' · DIPOTONG '", "(false ? ' · DIPOTONG '")),
            ('Tahap 3: kabar owner tidak menyebut yang ditolak', MT, M.replace("(h.ditolak.length ? ' · DITOLAK: '", "(false ? ' · DITOLAK: '")),
            ('upah bongkar disetujui tanpa menambah kedatangan', TPL, T.replace("biayaBongkar: (Number(b.biayaBongkar) || 0) + n,", "biayaBongkar: (Number(b.biayaBongkar) || 0),")),
            ('bayar supir mengabaikan bon pilihan owner', TPL, T.replace("const bonId = KOSONG(o.bonId) ? P.bawaan : String(o.bonId);", "const bonId = P.bawaan;")),
            ('bayar supir bertanggal hari owner menyetujui', TPL, T.replace("uang = { koleksi: 'utangPemasokMutasi', data: { id: w.idUnik(), tanggal: tgl, jam,", "uang = { koleksi: 'utangPemasokMutasi', data: { id: w.idUnik(), tanggal: w.tanggal, jam,")),
            ('penjaga kiriman: kedatangan tablet boleh tunai', AK, A.replace("d.dariTablet === true && d.caraBayar === 'utang' && d.biayaBongkar === 0", "d.dariTablet === true && d.biayaBongkar === 0")),
            ('Tahap 5: kemasan jadi tablet tanpa pasangan beli-jadi (unit tidak lahir di buku Kemasan)', MT, M.replace("  const dokumen = [{ koleksi: 'batchMasuk', data: bm }].concat(jadi);", "  const dokumen = [{ koleksi: 'batchMasuk', data: bm }];")),
            ('Tahap 5: beli-jadi tanpa kedatangan tablet lolos sebagai kedatangan', AK, A.replace("&& String(y.data.id) === String(x.data.dariBatch));", ");")),
            ('Tahap 5: pasangan beli-jadi tablet dihitung adukan lagi', AK, A.replace("(D || []).some((x) => x.koleksi === 'produksiKemasan' && !beliJadiTablet(x))", "ada('produksiKemasan')")),
            ('Tahap 5: baris kemasan jadi tablet tanpa batas (kiriman bisa melewati batas server)', MT, M.replace("  if (H.kemasan.length > MT_BATAS.kemasan) return {", "  if (false) return {")),
            ('Tahap 5: nilai kabar & bon tablet tanpa kemasan jadi', MT, M.replace("  const h = r.hitung; const nilai = h.nilaiBeras + h.nilaiKemasan;", "  const h = r.hitung; const nilai = h.nilaiBeras;")),
            ('Tahap 5: catatan tablet tidak ikut tersimpan', MT, M.replace("  if (PB.catatan.length) bm.catatanPemasok = PB.catatan;\n", "")),
            ('Tahap 5: klaim tablet tidak ikut tersimpan', MT, M.replace("  if (cara) bm.klaim = {", "  if (false) bm.klaim = {")),
            ('Tahap 5: klaim tablet langsung berstatus disetujui', MT, M.replace("bm.klaim = { cara, status: 'diminta',", "bm.klaim = { cara, status: 'disetujui',")),
            ('Tahap 5: klaim tablet tanpa baris catatan diterima', MT, M.replace("  if (cara && !PB.catatan.length) return { tolak: 'Klaim butuh minimal satu baris catatan (apa yang kurang, lebih, tertinggal, atau tidak sesuai)' };\n  if (PB.catatan.length)", "  if (PB.catatan.length)")),
            ('Tahap 5: baris catatan tablet tidak diperiksa', SC, t[SC].replace("    if (jenis !== 'mutu' && n === null) return { tolak: 'Baris ' + (i + 1) + ' (' + cpNama(CP_JENIS, jenis).toLowerCase() + '): jumlahnya belum diisi' };", "")),
            ('Tahap 5: tablet memakai potongan langsung (jalur owner: patokan kas + bayar bon)', MT, M.replace("  d.pakaiPotong = '';   // Tahap 5", "  // Tahap 5")),
            ('Tahap 5: usul pakai potongan tidak ditulis', MT, M.replace("  if (usul) bm.usulPakaiPotong = {", "  if (false) bm.usulPakaiPotong = {")),
            ('Tahap 5: usul potong tanpa diketuk', MT, M.replace("  const usul = !!D.pakaiPotong && h.potongTunggu > 0;", "  const usul = h.potongTunggu > 0;")),
            ('Tahap 5: usul potong lebih besar dari nilai barang diterima', MT, M.replace("  if (usul && h.potongTunggu > nilai) return {", "  if (false) return {")),
            ('Tahap 5: setuju pakai potongan tanpa bayar bon (bon tetap penuh)', SC, t[SC].replace("  const dokumen = [{ koleksi: 'batchMasuk', data }, { koleksi: 'utangPemasokMutasi', data: { id: w.idUnik(), tanggal: w.tanggal,", "  const dokumen = [{ koleksi: 'batchMasuk', data }, { koleksi: 'bukanApaApa', data: { id: w.idUnik(), tanggal: w.tanggal,")),
            ('Tahap 5: setuju pakai potongan tanpa menaikkan patokan laci (laci buku turun padahal tidak ada uang keluar)', SC, t[SC].replace("  if (!H.dalamTitik) dokumen.push({ koleksi: 'pengaturan',", "  if (false) dokumen.push({ koleksi: 'pengaturan',")),
            ('Tahap 5: bayar bon potongan bertanggal hari datang (hari yang sudah ditutup diberi uang keluar susulan)', SC, t[SC].replace("{ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'bayar', pemasok: String(b.pemasok || '').trim(), nominal: H.rp,", "{ id: w.idUnik(), tanggal: String(b.tanggal), jam: w.jam, tipe: 'bayar', pemasok: String(b.pemasok || '').trim(), nominal: H.rp,")),
            ('Tahap 5: usul tetap menempel sesudah disetujui (bisa disetujui dua kali)', SC, t[SC].replace("disetujui: { tanggal: w.tanggal, jam: w.jam } } }); delete data.usulPakaiPotong;", "disetujui: { tanggal: w.tanggal, jam: w.jam } } });").replace("  if (b.potonganPakai && Number(b.potonganPakai.rp) > 0) return Object.assign(out, { tolak: 'Kedatangan ini sudah dibayar dengan potongan pemasok' });\n", "")),
            ('Tahap 5: potongan yang sudah terpakai tetap bisa disetujui', SC, t[SC].replace("  out.dari = ptMenunggu(out.pemasok).filter((x) => minta[String(x.id) + '|' + x.i]);", "  out.dari = (Array.isArray(u.dari) ? u.dari : []).map((x) => ({ id: x.id, i: x.i, rp: x.rp, tanggalDatang: '' }));")),
            ('Tahap 5: neraca per tanggal — potongan dianggap dipakai sejak hari datang, bukan hari disetujui', 'baru/js/data/toko.js', t['baru/js/data/toko.js'].replace("const selesai = String((p.disetujui && p.disetujui.tanggal) || b.tanggal || '');", "const selesai = String(b.tanggal || '');")),
            ('Tahap 5: usul catatan dari tablet langsung menulis kedatangan', MT, M.replace("  const dok = tpDokKabarMasuk({ batchId: String(D.id), pemasok: C.pemasok, nominal: 0, teks }, akun, w); dok.data.usul = usul;\n  return { dokumen: [dok],", "  const dok = tpDokKabarMasuk({ batchId: String(D.id), pemasok: C.pemasok, nominal: 0, teks }, akun, w); dok.data.usul = usul;\n  return { dokumen: [dok, { koleksi: 'batchMasuk', data: { id: D.id } }],")),
            ('Tahap 5: usul tanpa kolom usul (owner tidak melihatnya di kedatangan)', MT, M.replace(" dok.data.usul = usul;\n", "\n")),
            ('Tahap 5: usul kembalikan tidak memeriksa sisa buku', MT, M.replace("const H = hitungReturPemasok(D.id, { merk: D.merk, kg: D.kg, alasan }); if (H.tolak) return { tolak: H.tolak };", "const H = hitungReturPemasok(D.id, { merk: D.merk, kg: D.kg, alasan }); if (H.tolak) return { dokumen: [], patch: {} };")),
            ('Tahap 5: usul kembalikan tanpa alasan diterima', MT, M.replace("if (alasan.length < 5) return { tolak: 'Tulis alasan beras itu dikembalikan (paling sedikit 5 huruf)' };", "")),
            ('Tahap 5: usul yang sudah diperiksa owner masih terdaftar menunggu', MT, M.replace(" && (m.status || 'menunggu') === 'menunggu')\n    .sort(", ")\n    .sort(")),
            ('Tahap 5: lembar owner tidak membawa nomor usulnya (usul tidak ikut ditandai)', MT, M.replace(", dariUsul: false, usulId: u.pid, usulDari: u.dari } }; }", ", dariUsul: false } }; }")),
            ('tanda terima melupakan uang ke supir', TBL, TB.replace("hasil.titipSupir = bon ? Math.max(0, Math.round(bil(B.titipSupir))) : 0;", "hasil.titipSupir = 0;")),
        ]
        kode = 0
        for nama, berkas, isi in rusak:
            if isi == t[berkas]: print('KONTROL BASI  ' + nama); kode = 3; continue
            t2 = dict(t); t2[berkas] = isi; g = periksa(t2, diam=True)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0]['nama'][:100] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    sys.exit(1 if periksa(t) else 0)


if __name__ == '__main__':
    main()
