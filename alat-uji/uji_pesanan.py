#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_pesanan.py — B4 PESANAN, PO & ORDER RUTIN (keputusan owner 18 Nov 2026). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  · isi pesanan dari KATALOG (baris karung / kemasan / literan + jumlah) → teks isi untuk dokumen lama, keranjang terisi sendiri saat "catat jual";
  · nomor PO pelanggan menempel di semua baris nota, struk & surat jalan;
  · UANG MUKA = pelunasan bon ber-untukPesanan SEBELUM notanya (mesin beku: kas naik, sisa bon turun / kelebihan bayar) — nota pesanannya = nota bon yang
    dipotong DP: dibayar sekarang = total − DP (kembalian dari situ), sisa bon kembali seperti sebelum DP; DP > nota = sisanya saldo; faktur & "jadi nota"
    membaca DP sebagai pembayaran nota itu; bagian yang tertutup DP tidak kena KR1; bayar di tempat menagih total − DP;
  · BATAL ber-DP: pilih jadi saldo (Ben boleh) atau dikembalikan tunai (owner — pembayaran bernilai minus); tanpa DP seperti dulu;
  · JADWAL RUTIN = pengingat (tiap minggu / 2 minggu / bulan), hari pengingat diatur owner (Pelanggan › Atur), lewati sekali, hentikan; pesanan dari
    jadwal mengikat kejadiannya;
  · cek stok: pesanan & jadwal 14 hari + laju jual → kurang;
  · penjaga kiriman = rules v11: Ben membuat & mengubah pesanan / jadwal (kolom terbatas), karyawan tidak; DP minus = owner.

    python3 alat-uji/uji_pesanan.py            → N lulus · 0 gagal
    python3 alat-uji/uji_pesanan.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_antar, uji_jual_baru  # noqa: E402
JSC = uji_antar.JSC
PO = 'baru/js/layar/pesanan-logika.js'; JL = 'baru/js/layar/jual-logika.js'; AK = 'baru/js/data/akses.js'; STK = 'baru/js/layar/struk-logika.js'
FK = 'baru/js/layar/faktur-logika.js'; AJ = 'baru/js/layar/antar-logika.js'; PL = 'baru/js/layar/pelanggan-logika.js'
MODUL = list(dict.fromkeys([m for m in uji_antar.MODUL if m != PO] + [PO]))
SUMBER = {'jual': 'baru/js/layar/jual.js', 'panel': 'baru/js/layar/pesanan-panel.js', 'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml', 'rules': 'firestore.rules',
          'koleksi': 'baru/js/data/koleksi.js', 'akses': AK, 'po': PO, 'pelanggan': 'baru/js/layar/pelanggan.js', 'dasbor': 'baru/js/layar/dasbor.js',
          'dasborL': 'baru/js/layar/dasbor-logika.js', 'sistem': 'baru/js/layar/sistem-logika.js', 'toko': 'baru/js/data/toko.js'}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
var J = function (x) { return JSON.stringify(x); };
var nId = 9000; var W = { tanggal: '2026-11-18', jam: '10:00', kini: '2026-11-18T03:00:00.000Z', kodePerangkat: 'TES', idUnik: function () { nId += 1; return nId; } };
var KINI = new Date('2026-11-18T10:00:00+07:00');
var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
var BEN = keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true });
var KRY = keadaanAkun('kry.contoh@tokoberasmiqbal.web.app', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true });
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
pasok('aksesAkun', [{ id: 'uid-ben', uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true }, { id: 'uid-kry', uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true }]);
setelSumber('cadangan', 'kotak pasir');
var hak = function (akun) { return Object.assign({}, (ssAtur('peran').hak || {})[akun.peran] || {}, { jatahNego: ngJatah(akun) }); };
var atribusi = function (akun, d, ada) { return beriAtribusiAkun(d, akun, { perangkat: 'p-uji', kini: W.kini }, ada); };
var kirim = function (akun, dok) { return periksaKiriman(akun, (dok || []).map(function (x) { return { koleksi: x.koleksi, data: atribusi(akun, x.data, false), ada: false, lama: null }; }), [], hak(akun), KINI); };
var kirimUbah = function (akun, koleksi, lama, baru) { return periksaKiriman(akun, [{ koleksi: koleksi, data: atribusi(akun, baru, true), ada: true, lama: lama }], [], hak(akun), KINI); };
var s = keadaanAwal(); s.sekarang = KINI;
function terap(p) { s = Object.assign({}, s, p); sinkronKeranjang(s); return p; }
function rak() { return susunRak(s); }
function chip(jalur, kunci, berat) { return rak()[jalur].find(function (c) { return c.kunci === kunci && (!berat || c.berat === berat); }); }
function mulai() { s = keadaanAwal(); s.sekarang = KINI; sinkronKeranjang(s); }
function isi(jalur, kunci, n, berat) { terap(ketukChip(s, chip(jalur, kunci, berat))); terap({ ketik: String(n) }); terap(masukkan(s)); }
var dok = function (N, kol) { return N.dokumen.filter(function (x) { return x.koleksi === kol; }).map(function (x) { return x.data; }); };
var harga = function (nama) { return function (b) { var c = poChipCocok(rak(), b); var t = c ? bangunBaris(c, b.jumlah, Object.assign({}, s, { pelanggan: nama, keranjang: [] })) : null; return t ? t.hargaTotal : 0; }; };
var sisaBon = function (nama) { var r = hitungPiutang().find(function (x) { return x.kunci === kunciPelanggan(nama); }); return r ? r.sisa : 0; };
var SET = { id: 'hargaTingkat', tingkat: [{ id: 'warung', nama: 'Warung', potKg: 0 }], barang: {}, orang: { 'bu suti': 'warung' }, khusus: [] };
pasok('aturanToko', [JSON.parse(J(SET))]);
pasok('pelangganCatatan', [{ id: 'bu suti', nama: 'Bu Suti', catatan: 'warung depan pasar', tempoHari: 7, alamat: 'Jl. Contoh 1', batasKredit: 150000 }]);
var bAngsa = poBarisDariChip(chip('karung', 'Angsa', 50), '2').baris; var bKembang = function (n) { return poBarisDariChip(chip('kemasan', 'Kembang|5'), String(n)).baris; };
function pesan(draf, akun) { var r = poSusunPesanan(Object.assign(poDrafBaru(draf.nama), draf), W, { harga: harga(draf.nama) }); if (r.tolak) return r; terapkanKeCache(r.dokumen); return r; }
function dp(ps, n, cara) { var r = poSusunUangMuka(poAmbil(ps.id), String(n), cara || 'Tunai', W); if (!r.tolak) terapkanKeCache(r.dokumen); return r; }

// ---- A · baris pesanan dari katalog
ok('A: 2 karung Angsa 50 kg = baris karung (kunci merek, berat 50, kg 100)', bAngsa && bAngsa.jalur === 'karung' && bAngsa.kunci === 'Angsa' && bAngsa.berat === 50 && bAngsa.kg === 100 && bAngsa.satuan === 'karung', J(bAngsa));
ok('A: karung 1,3 / kemasan 1,5 / jumlah 0 ditolak; 1,5 karung boleh', !!poBarisDariChip(chip('karung', 'Angsa', 50), '1,3').tolak && !!poBarisDariChip(chip('kemasan', 'Kembang|5'), '1,5').tolak
  && !!poBarisDariChip(chip('kemasan', 'Kembang|5'), '0').tolak && poBarisDariChip(chip('karung', 'Angsa', 50), '1,5').baris.kg === 75);
ok('A: teks isi = "2 karung Angsa 50 kg · 3 kemasan Kembang 5 kg"', poIsiTeks([bAngsa, bKembang(3)]) === '2 karung ' + bAngsa.nama + ' · 3 kemasan Kembang 5 kg', poIsiTeks([bAngsa, bKembang(3)]));
var T0 = poTaruhBaris([bAngsa], poBarisDariChip(chip('karung', 'Angsa', 50), '3').baris);
ok('A: barang yang sama dimasukkan lagi = jumlahnya diganti (bukan dobel)', T0.baris.length === 1 && T0.baris[0].jumlah === 3, J(T0));

// ---- B · pesanan baru / ubah / antar + penjaga kiriman
ok('B: tanpa nama / tanpa barang / tanggal lewat / PO terlalu panjang ditolak', !!poSusunPesanan(poDrafBaru(''), W, {}).tolak && !!poSusunPesanan(poDrafBaru('Bu Suti'), W, {}).tolak
  && !!poSusunPesanan(Object.assign(poDrafBaru('Bu Suti'), { baris: [bAngsa], tanggalKirim: '2026-11-01' }), W, {}).tolak
  && !!poSusunPesanan(Object.assign(poDrafBaru('Bu Suti'), { baris: [bAngsa], noPO: '1234567890123456789012345678901' }), W, {}).tolak);
var R1 = poSusunPesanan(Object.assign(poDrafBaru('Bu Suti'), { baris: [bAngsa, bKembang(3)], noPO: 'PO-77', tanggalKirim: '2026-11-20', alamat: 'Jl. Contoh 1' }), W, { harga: harga('Bu Suti') });
var P1 = R1.dokumen[0].data;
ok('B: pesanan: dipesan, belum bernota, baris katalog, PO, tanggal kirim, perkiraan = harga pembeli (1.380.000 + 216.000)', P1.status === 'dipesan' && P1.trxIdJual === null && P1.baris.length === 2 && P1.noPO === 'PO-77'
  && P1.tanggalKirim === '2026-11-20' && P1.nilaiPerkiraan === 1596000 && /2 karung/.test(P1.isi), J(P1));
ok('B: Ben boleh membuat pesanan (rules v11), karyawan tidak', !kirim(BEN, R1.dokumen).tolak && !!kirim(KRY, R1.dokumen).tolak, J([kirim(BEN, R1.dokumen), kirim(KRY, R1.dokumen)]));
ok('B: penjaga menolak pesanan baru buatan Ben yang sudah bernota / dibayar / membawa kolom batal', !!kirim(BEN, [{ koleksi: 'pesanan', data: Object.assign({}, P1, { trxIdJual: '1' }) }]).tolak
  && !!kirim(BEN, [{ koleksi: 'pesanan', data: Object.assign({}, P1, { status: 'dibayar' }) }]).tolak && !!kirim(BEN, [{ koleksi: 'pesanan', data: Object.assign({}, P1, { nasibUangMuka: 'saldo' }) }]).tolak);
terapkanKeCache(R1.dokumen);
var U1 = poSusunPesanan(Object.assign(poDrafDariPesanan(P1), { noPO: 'PO-78', tanggalKirim: '2026-11-21' }), W, { harga: harga('Bu Suti') }); var P1u = U1.dokumen[0].data;
ok('B: ubah pesanan: PO & tanggal kirim berubah, riwayat bertanda ubah, Ben boleh, karyawan tidak', P1u.noPO === 'PO-78' && P1u.tanggalKirim === '2026-11-21' && P1u.riwayatStatus.slice(-1)[0].ubah === true
  && !kirimUbah(BEN, 'pesanan', P1, P1u).tolak && !!kirimUbah(KRY, 'pesanan', P1, P1u).tolak, J([kirimUbah(BEN, 'pesanan', P1, P1u), kirimUbah(KRY, 'pesanan', P1, P1u)]));
ok('B: nama pemesan tidak bisa diganti (uang muka & bon atas nama itu); penjaga menolak Ben mengganti nama', !!poSusunPesanan(Object.assign(poDrafDariPesanan(P1), { nama: 'Deka' }), W, {}).tolak
  && !!kirimUbah(BEN, 'pesanan', P1, Object.assign({}, P1, { namaPelanggan: 'Deka' })).tolak);
var A1 = susunPesananAntar(P1.id, W);
ok('B: Ben menandai diantar; karyawan ditolak', !A1.tolak && !kirimUbah(BEN, 'pesanan', P1, A1.dokumen[0].data).tolak && !!kirimUbah(KRY, 'pesanan', P1, A1.dokumen[0].data).tolak);
ok('B: catat jual pesanan (JADI NOTA) tetap boleh untuk karyawan (kolom jadi nota)', !kirimUbah(KRY, 'pesanan', P1, Object.assign({}, P1, { status: 'dibayar', trxIdJual: 'tx1', riwayatStatus: P1.riwayatStatus.concat([{ status: 'dibayar' }]) })).tolak);
ok('B: pesanan yang sudah batal tidak dihidupkan lagi oleh Ben', !!kirimUbah(BEN, 'pesanan', Object.assign({}, P1, { status: 'batal' }), Object.assign({}, P1, { status: 'dipesan' })).tolak);
ok('B: pesanan yang sudah jadi nota tidak bisa diubah Ben', !!kirimUbah(BEN, 'pesanan', Object.assign({}, P1, { status: 'dibayar', trxIdJual: 'tx1' }), Object.assign({}, P1, { status: 'dibayar', trxIdJual: 'tx1', noPO: 'x' })).tolak);
terapkanKeCache(U1.dokumen);

// ---- C · uang muka → nota pesanan tunai (DP memotong yang dibayar sekarang)
var D1 = poSusunUangMuka(poAmbil(P1.id), '300.000', 'Tunai', W); var DP1 = D1.dokumen[0].data;
ok('C: uang muka = pelunasan bon ber-untukPesanan atas nama pemesan, bukan nota', DP1.tipe === 'bayar' && DP1.nominal === 300000 && DP1.untukPesanan === String(P1.id) && DP1.namaPelanggan === 'Bu Suti' && !DP1.notaTrxId, J(DP1));
ok('C: Ben boleh mencatat uang muka; karyawan tidak (tindakan pesanan)', !kirim(BEN, D1.dokumen).tolak && !!kirim(KRY, D1.dokumen).tolak, J([kirim(BEN, D1.dokumen), kirim(KRY, D1.dokumen)]));
ok('C: tindakan kiriman uang muka = terima bon + pesanan', J(tindakanKiriman(D1.dokumen.map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false }; }))) === '["terimaBon","pesanan"]', J(tindakanKiriman(D1.dokumen.map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false }; }))));
terapkanKeCache(D1.dokumen);
ok('C: mesin beku: sisa bon Bu Suti −300.000 (uang pelanggan dipegang toko = kelebihan bayar)', sisaBon('Bu Suti') === -300000 && pecahLebih(hitungPiutang().find(function (x) { return x.kunci === 'bu suti'; })).uang === 300000, sisaBon('Bu Suti'));
ok('C: poUangMuka = 300.000 & kartu pesanan menyebutnya', poUangMuka(P1.id).total === 300000 && poDaftarAktif('').find(function (o) { return o.id === String(P1.id); }).dp === 300000);
mulai(); terap(ikatPesanan(s, P1.id));
ok('C: catat jual mengisi keranjang kosong dari pesanan (2 dari 2 barang), pembeli = pemesan', s.keranjang.length === 2 && s.pelanggan === 'Bu Suti' && s.pesananId === String(P1.id) && /2 dari 2 barang/.test(s.kabar) && /uang muka Rp300\.000/.test(s.kabar), s.kabar);
var T1 = hitungTagihan(s);
ok('C: tagihan 1.596.000 · uang muka 300.000 · dibayar sekarang 1.296.000', T1.total === 1596000 && T1.muka === 300000 && T1.perlu === 1296000, J(T1));
ok('C: belum ada uang → "Ketuk uang"; PAS = yang dibayar sekarang', /Ketuk uang/.test(alasanTolak(s)) && uangPas(s).uang === 1296000);
terap({ uang: 1300000 });
var T1b = hitungTagihan(s);
ok('C: uang 1.300.000 → kembalian 4.000 (dari yang dibayar sekarang), tidak kurang', T1b.kembalian === 4000 && T1b.kurang === 0 && !T1b.sisaJadiBon && alasanTolak(s) === '', J([T1b, alasanTolak(s)]));
ok('C: nota yang tertutup penuh DP + uang tidak kena KR1 (bonKeranjang 0)', bonKeranjang(s) === 0);
var S2 = Object.assign({}, s, { pelanggan: 'Deka' });
ok('C: nama pembeli lain dari pemesan ber-DP ditolak', /atas nama Bu Suti/.test(alasanTolak(S2)), alasanTolak(S2));
var N1 = susunNotaDokumen(s, W); var PJ1 = dok(N1, 'penjualan'); var PB1 = dok(N1, 'piutangMutasi'); var PS1 = dok(N1, 'pesanan')[0];
ok('C: nota = BON sebesar total (semua baris Kredit), PO-78 di semua baris, DP di baris pertama', PJ1.every(function (p) { return p.caraBayar === 'Kredit' && p.noPO === 'PO-78'; }) && PJ1[0].uangMukaPesanan === 300000
  && PJ1.filter(function (p) { return p.uangMukaPesanan; }).length === 1 && N1.totalBayar === 1596000, J(PJ1.map(function (p) { return [p.caraBayar, p.noPO, p.uangMukaPesanan, p.hargaTotal]; })));
ok('C: satu pelunasan saat beli 1.296.000 menunjuk notanya & pesanannya, uang diterima 1.300.000, kembalian 4.000', PB1.length === 1 && PB1[0].nominal === 1296000 && PB1[0].notaTrxId === String(N1.trxId)
  && PB1[0].untukPesanan === String(P1.id) && PB1[0].uangDiterima === 1300000 && PB1[0].kembalian === 4000, J(PB1));
ok('C: pesanan JADI NOTA dalam kiriman yang sama; ringkas menyebut DP & LUNAS', PS1 && PS1.status === 'dibayar' && String(PS1.trxIdJual) === String(N1.trxId) && /uang muka Rp300\.000 dipotong/.test(N1.ringkas) && /LUNAS/.test(N1.ringkas), N1.ringkas);
ok('C: pelanggan usaha → nota pesanan jadi faktur', PJ1.every(function (p) { return /^F26-TES-/.test(p.noFaktur || ''); }), J(PJ1[0].noFaktur));
terapkanKeCache(N1.dokumen);
ok('C: mesin beku: sisa bon Bu Suti kembali 0 (nota 1.596.000 = DP 300.000 + bayar 1.296.000)', sisaBon('Bu Suti') === 0, sisaBon('Bu Suti'));
ok('C: "jadi nota" membaca LUNAS (DP menunjuk baris nota itu)', uangNotaPesanan(poAmbil(P1.id), '2026-11-18').lunas === true, J(uangNotaPesanan(poAmbil(P1.id), '2026-11-18')));
var F1 = fkSemua(KINI).find(function (f) { return f.trxId === String(N1.trxId); });
ok('C: faktur nota pesanan lunas (sisa 0)', F1 && F1.sisa === 0 && F1.status === 'lunas', J(F1 && [F1.sisa, F1.status]));
var ST1 = susunStruk(notaDariBaris(ambilPenjualanSemua().filter(function (p) { return String(p.trxId) === String(N1.trxId); })), stAtur(), { kertas: 80 });
ok('C: struk: LUNAS — uang muka + bayar sekarang, baris uang muka, dibayar sekarang, kembali 4.000, No. PO, tanpa "kelebihan bayar"', /LUNAS — uang muka \+ bayar sekarang/.test(ST1.teks) && /Uang muka pesanan\s+Rp300\.000/.test(ST1.teks)
  && /Dibayar sekarang\s+Rp1\.296\.000/.test(ST1.teks) && /Kembali\s+Rp4\.000/.test(ST1.teks) && /No\. PO pelanggan: PO-78/.test(ST1.teks) && !/Dari kelebihan bayar/.test(ST1.teks), ST1.teks);

// ---- D · DP lebih besar dari nota; nota bon ber-DP & KR1
var R2 = pesan({ nama: 'Bu Suti', baris: [bKembang(1)] }); var P2 = R2.pesanan; dp(P2, 100000);
mulai(); terap(ikatPesanan(s, P2.id));
var T2 = hitungTagihan(s);
ok('D: DP 100.000 > nota 72.000 → dibayar sekarang 0, sisa DP 28.000; sah tanpa uang', T2.muka === 72000 && T2.perlu === 0 && T2.dpSisa === 28000 && alasanTolak(s) === '', J([T2, alasanTolak(s)]));
var N2 = susunNotaDokumen(s, W);
ok('D: nota Kredit tanpa pelunasan saat beli; ringkas: sisa uang muka jadi saldo', dok(N2, 'piutangMutasi').length === 0 && dok(N2, 'penjualan').every(function (p) { return p.caraBayar === 'Kredit'; }) && /sisa uang muka Rp28\.000 jadi saldo Bu Suti/.test(N2.ringkas), N2.ringkas);
terapkanKeCache(N2.dokumen);
ok('D: sisa bon Bu Suti −28.000 (saldo, memotong belanja berikutnya)', sisaBon('Bu Suti') === -28000, sisaBon('Bu Suti'));
var R3 = pesan({ nama: 'Bu Suti', baris: [bKembang(4)] }); var P3 = R3.pesanan; dp(P3, 50000);
mulai(); terap(ikatPesanan(s, P3.id)); terap(pilihCara(s, 'Kredit'));
ok('D: bon 288.000 ber-DP 50.000: utang baru = 210.000 (> batas 150.000) → KR1 menahan', bonKeranjang(s) === 210000 && /batas kredit/i.test(alasanTolak(s)), J([bonKeranjang(s), alasanTolak(s)]));
mulai(); terap({ pesananId: String(P3.id), pelanggan: 'Bu Suti' }); isi('kemasan', 'Kembang|5', 2); terap(pilihCara(s, 'Kredit'));
ok('D: bon 144.000 ber-DP 50.000 → utang akhir 66.000 (saldo 28.000 ikut memotong), lolos batas', bonKeranjang(s) === 66000 && alasanTolak(s) === '', J([bonKeranjang(s), alasanTolak(s)]));
var N3 = susunNotaDokumen(s, W); terapkanKeCache(N3.dokumen);
ok('D: mesin: sisa bon Bu Suti 66.000; "jadi nota" = BON sisa 66.000 (sama dengan mesin)', sisaBon('Bu Suti') === 66000 && uangNotaPesanan(poAmbil(P3.id), '2026-11-18').sisa === 66000, J([sisaBon('Bu Suti'), uangNotaPesanan(poAmbil(P3.id), '2026-11-18')]));
var B0 = poBarisSah([bKembang(1)]); var R6 = pesan({ nama: 'Bu Suti', baris: [bKembang(2)] }); dp(R6.pesanan, 44000);
mulai(); terap(ikatPesanan(s, R6.pesanan.id)); terap({ antar: Object.assign(ajDrafBaru('Bu Suti'), { ongkir: '0' }) }); terap(ajSetelCod(s, true));
var N6 = susunNotaDokumen(s, W); var SJ6 = dok(N6, 'suratJalan')[0];
ok('D: bayar di tempat ber-DP: surat jalan menagih total − DP (144.000 − 44.000), mencetak DP', SJ6 && SJ6.tagihRp === 100000 && SJ6.uangMuka === 44000 && ajGarisCetak(SJ6, {}, 'toko').some(function (g) { return /Uang muka sudah masuk/.test(g.kiri); }), J(SJ6));

// ---- E · batal ber-DP: jadi saldo (Ben) / dikembalikan tunai (owner)
var R4 = pesan({ nama: 'Bu Suti', baris: [bKembang(1)] }); var P4 = R4.pesanan; dp(P4, 50000);
ok('E: batal ber-DP tanpa pilihan ditolak; Ben memilih "kembali" ditolak (owner)', !!poSusunBatal(poAmbil(P4.id), '', '', W, {}).tolak && !!poSusunBatal(poAmbil(P4.id), 'kembali', '', W, { owner: false }).tolak);
var B4 = poSusunBatal(poAmbil(P4.id), 'saldo', 'tidak jadi', W, { owner: false });
ok('E: jadi saldo: pesanan batal + nasib saldo, TANPA catatan uang; Ben boleh mengirim', B4.dokumen.length === 1 && B4.dokumen[0].data.status === 'batal' && B4.dokumen[0].data.nasibUangMuka === 'saldo' && !kirimUbah(BEN, 'pesanan', poAmbil(P4.id), B4.dokumen[0].data).tolak, J(B4.dokumen));
var sb4 = sisaBon('Bu Suti'); terapkanKeCache(B4.dokumen);
ok('E: sesudah batal-saldo DP tetap di buku (sisa bon tidak berubah: 66.000 − DP bayar-di-tempat 44.000 − DP 50.000)', sisaBon('Bu Suti') === sb4 && sb4 === -28000, sb4);
var R5 = pesan({ nama: 'Bu Suti', baris: [bKembang(1)] }); var P5 = R5.pesanan; var sb5 = sisaBon('Bu Suti'); dp(P5, 40000);
var B5 = poSusunBatal(poAmbil(P5.id), 'kembali', '', W, { owner: true }); var K5 = dok(B5, 'piutangMutasi')[0];
ok('E: owner mengembalikan: pembayaran −40.000 ber-untukPesanan, tunai', K5 && K5.nominal === -40000 && K5.untukPesanan === String(P5.id) && K5.caraBayar === 'Tunai' && K5.kembaliUangMuka === true, J(K5));
ok('E: penjaga menolak pembayaran minus dari Ben (uang keluar laci = owner)', !!kirim(BEN, B5.dokumen.filter(function (x) { return x.koleksi === 'piutangMutasi'; })).tolak);
terapkanKeCache(B5.dokumen);
ok('E: sesudah dikembalikan: DP pesanan 0, sisa bon kembali seperti sebelum DP', poUangMuka(P5.id).total === 0 && sisaBon('Bu Suti') === sb5 && sb5 === -28000, J([poUangMuka(P5.id), sisaBon('Bu Suti'), sb5]));
var R7 = pesan({ nama: 'Bu Suti', baris: [bKembang(1)] });
ok('E: tanpa DP batal seperti dulu (tanpa pilihan)', !susunPesananBatal(R7.pesanan.id, W).tolak);

// ---- F · jadwal rutin = pengingat
var JR = poSusunJadwal({ nama: 'Bu Suti', baris: [bKembang(2)], ulang: 'mingguan', hari: 5, mulai: '2026-11-18', alamat: 'Jl. Contoh 1' }, W); var J1 = JR.dokumen[0].data;
ok('F: jadwal tiap minggu hari Jumat, aktif, lewati kosong; Ben boleh, karyawan tidak', J1.ulang === 'mingguan' && J1.hari === 5 && J1.aktif === true && J1.lewati.length === 0 && !kirim(BEN, JR.dokumen).tolak && !!kirim(KRY, JR.dokumen).tolak);
ok('F: tindakan kiriman jadwal = pesanan', J(tindakanKiriman(JR.dokumen.map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false }; }))) === '["pesanan"]');
ok('F: tanggal 29 tiap bulan / tanpa ulang ditolak', !!poSusunJadwal({ nama: 'X', baris: [bKembang(1)], ulang: 'bulanan', tanggalBulan: 29 }, W).tolak && !!poSusunJadwal({ nama: 'X', baris: [bKembang(1)], ulang: '' }, W).tolak);
terapkanKeCache(JR.dokumen);
ok('F: kejadian tiap minggu: 20 Nov, 27 Nov, 4 Des', J(poKejadian(J1, '2026-11-18', '2026-12-05')) === '["2026-11-20","2026-11-27","2026-12-04"]', J(poKejadian(J1, '2026-11-18', '2026-12-05')));
ok('F: tiap 2 minggu: 20 Nov, 4 Des · tiap bulan tgl 25: 25 Nov, 25 Des', J(poKejadian(Object.assign({}, J1, { ulang: 'duaMinggu' }), '2026-11-18', '2026-12-31')) === '["2026-11-20","2026-12-04","2026-12-18"]'
  && J(poKejadian(Object.assign({}, J1, { ulang: 'bulanan', tanggalBulan: 25 }), '2026-11-18', '2026-12-31')) === '["2026-11-25","2026-12-25"]');
var I2 = poPengingat('2026-11-18', 2);
ok('F: pengingat 2 hari sebelumnya: Bu Suti Jumat 20 Nov "kirim 2 hari lagi"; 1 hari = belum muncul', I2.length === 1 && I2[0].tanggal === '2026-11-20' && I2[0].kata === 'kirim 2 hari lagi' && poPengingat('2026-11-18', 1).length === 0, J(I2));
ok('F: terlewat tetap tampil (23 Nov: 20 Nov terlewat 3 hari)', poPengingat('2026-11-23', 2).length === 1 && poPengingat('2026-11-23', 2)[0].terlewat === true);
var RJ = poSusunPesanan(poDrafDariJadwal(poJadwalSemua()[0], '2026-11-20'), W, { harga: harga('Bu Suti') }); var PJ = RJ.dokumen[0].data;
ok('F: pesanan dari pengingat mengikat kejadiannya (jadwalId & tanggal), isi dari jadwal', PJ.jadwalId === String(J1.id) && PJ.jadwalTanggal === '2026-11-20' && PJ.tanggalKirim === '2026-11-20' && PJ.baris.length === 1, J(PJ));
terapkanKeCache(RJ.dokumen);
ok('F: sesudah dibuat, pengingat kejadian itu hilang', poPengingat('2026-11-18', 2).length === 0);
var LW = poSusunLewati(J1.id, '2026-11-27', W); terapkanKeCache(LW.dokumen);
ok('F: lewati sekali 27 Nov → tidak diingatkan; 4 Des tetap', poPengingat('2026-11-25', 2).length === 0 && poPengingat('2026-12-02', 2).length === 1 && !kirimUbah(BEN, 'orderRutin', J1, LW.dokumen[0].data).tolak);
var HN = poSusunJadwalAktif(J1.id, false, W);
ok('F: Ben menghentikan jadwal boleh; mengganti pembuat ditolak; karyawan ditolak', !kirimUbah(BEN, 'orderRutin', J1, HN.dokumen[0].data).tolak && !!kirimUbah(BEN, 'orderRutin', J1, Object.assign({}, J1, { olehUid: 'uid-lain' })).tolak
  && !!kirimUbah(KRY, 'orderRutin', J1, HN.dokumen[0].data).tolak);
terapkanKeCache(HN.dokumen);
ok('F: jadwal berhenti → tidak ada pengingat', poPengingat('2026-12-02', 2).length === 0);
var RB = poSusunPesanan(Object.assign(poDrafBaru('Warung Contoh'), { baris: [bKembang(5)], tanggalKirim: '2026-11-23', jadwal: { nyala: true, ulang: 'mingguan', hari: 1 } }), W, { harga: harga('Warung Contoh') });
ok('F: pesanan + "ulangi sebagai order rutin" = pesanan + jadwal (Senin), pesanannya mengikat kejadian pertama', RB.dokumen.length === 2 && RB.dokumen[1].koleksi === 'orderRutin' && RB.dokumen[1].data.hari === 1
  && RB.dokumen[0].data.jadwalId === String(RB.dokumen[1].data.id) && RB.dokumen[0].data.jadwalTanggal === '2026-11-23', J(RB.dokumen.map(function (x) { return x.data; })));

// ---- G · cek stok pesanan (laju jual ikut)
mulai(); pasok('pesanan', []); pasok('orderRutin', []);
pesan({ nama: 'Bu Suti', baris: [bAngsa], tanggalKirim: '2026-11-21' });
var BRG = [{ jenis: 'karung', kunci: 'Angsa', nama: 'Angsa', sisa: 100, laju: 10 }, { jenis: 'kemasan', kunci: 'Kembang|5', nama: 'Kembang 5 kg', sisa: 50, laju: 1 }];
var CS = poCekStok('2026-11-18', BRG); var cA = CS.find(function (x) { return x.kunci === 'karung|Angsa'; });
ok('G: Angsa: pesanan 100 kg dalam 3 hari, sisa 100, laju 10/hari → KURANG ±30 kg', cA && cA.awas && cA.kurang === 30 && cA.hari === 3 && /KURANG ±30 kg dalam 3 hari/.test(poKataStok(cA)), J([cA, cA && poKataStok(cA)]));
var CS2 = poCekStok('2026-11-18', [{ jenis: 'karung', kunci: 'Angsa', nama: 'Angsa', sisa: 500, laju: 10 }]);
ok('G: stok cukup → tidak awas', CS2.length === 1 && !CS2[0].awas && /cukup/.test(poKataStok(CS2[0])), J(CS2));

// ---- H · Pelanggan › Atur: hari pengingat order rutin
ok('H: bawaan 2 hari', poHariIngat() === 2 && aturPelanggan().hariIngatRutin === 2);
var SA = susunAturPelanggan(Object.assign({}, aturPelanggan(), { kosongKali: '30', hariIngatRutin: '5' }), W);
ok('H: simpan Atur menulis hariIngatRutin 5; 20 ditolak', SA.dokumen && SA.dokumen[0].data.hariIngatRutin === 5 && /pengingat order rutin 5 hari/.test(SA.patch.kabar)
  && !!susunAturPelanggan(Object.assign({}, aturPelanggan(), { kosongKali: '30', hariIngatRutin: '20' }), W).tolak, J(SA.patch || SA));
pasok('aturanToko', [JSON.parse(J(SET)), { id: 'pelanggan', hariIngatRutin: 5 }]);
ok('H: aturan dibaca: poHariIngat 5', poHariIngat() === 5);
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('koleksi orderRutin terdaftar, kelas tetap (Ben mengubah tanpa cap jam server)', 'koleksi', ["{ nama: 'orderRutin',          urut: 'id',    cache: 'orderRutin', kelas: 'tetap' }"]),
    ('cache jadwal di lapisan data', 'toko', ['export function ambilOrderRutin() { return _cache.orderRutin || []; }']),
    ('Jual memasang panel Pesanan', 'jual', ['const PP = buatPanelPesanan(', 'Object.assign(aksi, PP.aksi);', "if (s.lembar === 'pesanan') return PP.gambarLembar(s, muncul, kepala, L1);", 'data-k="uang-muka-tagih"']),
    ('panel: form katalog, uang muka, batal pilih saldo / kembali, pengingat & jadwal', 'panel', ['data-aksi="psPilihChip"', 'data-aksi="psDpSimpan"', 'data-aksi="psNasib" data-n="saldo"', 'data-aksi="psNasib" data-n="kembali"',
     'data-aksi="psDariJadwal"', 'data-aksi="psLewati"', 'data-aksi="psJadwalAktif"', 'data-aksi="psRutin"', "tombolAkun(akun(), 'pesanan')"]),
    ('modul baru di-modulepreload', 'index', ['<link rel="modulepreload" href="js/layar/pesanan-logika.js">', '<link rel="modulepreload" href="js/layar/pesanan-panel.js">']),
    ('Pelanggan › Atur: hari pengingat order rutin', 'pelanggan', ['data-kolom="hariIngatRutin"']),
    ('Dasbor: order rutin perlu dibuat, pesanan dikirim dekat, stok kurang', 'dasbor', ['data-k="db-pesanan"', 'G.pesanan.ingat.map(', 'G.pesanan.stok.map(']),
    ('Dasbor membaca pengingat dari pesanan-logika', 'dasborL', ['const ING = poPengingat(isoP);', 'poCekStok(isoP, daftarBarang())']),
    ('kisi peran: pesanan (ben boleh sendiri, karyawan tidak)', 'sistem', ["['pesanan', 'Bikin & ubah pesanan, PO, jadwal rutin & uang muka', 'Jual']", "terimaAntar: 'sendiri', pesanan: 'sendiri' }", "terimaAntar: 'sendiri', pesanan: 'tidak' } };"]),
    ('server membuka tindakan pesanan untuk ben (rules v11)', 'akses', ["pesanan: ['ben'], kedatangan: ['ben'] };", "suratJalan: ['ben'], pesanan: ['ben'], orderRutin: ['ben'] };"]),
    ('CI menjalankan uji ini', 'pages', ['python3 alat-uji/uji_pesanan.py && python3 alat-uji/uji_pesanan.py --kontrol']),
]


def kolom_sama(src):
    """Kolom ubah pesanan & jadwal: pesanan-logika = akses.js = rules v11 (tanpa atribusi ubah); kolom terlarang pesanan baru sama."""
    ambil = lambda t, n: re.findall(r"'(\w+)'", re.search(n + r" = \[(.*?)\];", t, re.S).group(1))
    ru = lambda f: [x for x in re.findall(r"'(\w+)'", (re.search(r'function ' + f + r'\(peranBoleh\) \{.*?affectedKeys\(\)\.hasOnly\(\[([^\]]*)\]\);', src['rules'], re.S) or re.search('(x)', 'x')).group(1)) if not x.startswith('diubah')]
    pa, aa, ra = ambil(src['po'], 'PO_KOLOM_ATUR'), ambil(src['akses'], 'KOLOM_ATUR_PESANAN'), ru('stafAturPesanan')
    pr, ar, rr = ambil(src['po'], 'PO_KOLOM_RUTIN'), ambil(src['akses'], 'KOLOM_UBAH_RUTIN'), ru('stafUbahRutin')
    rb = re.search(r"function stafBuatPesanan\(peranBoleh\) \{.*?!d\.keys\(\)\.hasAny\(\[([^\]]*)\]\)", src['rules'], re.S)
    bb = (ambil(src['akses'], 'KOLOM_BUKAN_PESANAN_BARU'), re.findall(r"'(\w+)'", rb.group(1)) if rb else [])
    return pa == aa == ra and pr == ar == rr and bb[0] == bb[1], {'atur': [pa, aa, ra], 'rutin': [pr, ar, rr], 'baru': bb}


RUSAK = [
    ('uang muka tidak memotong tagihan', JL, "  const dp = uangMukaKeranjang(s).dp;", "  const dp = 0;"),
    ('nota pesanan ber-DP dicatat tunai penuh (tanpa bon & pelunasan)', JL, "    if (!(antar && antar.cod)) { if (cara === 'Tunai') { bayarSebagian = Math.min(uang, perlu); kembaliMuka = Math.max(0, uang - perlu); } else if (cara === 'QRIS') bayarSebagian = perlu; }\n    cara = 'Kredit';",
     "    if (!(antar && antar.cod)) { if (cara === 'Tunai') { kembaliMuka = Math.max(0, uang - perlu); } }"),
    ('pelunasan nota tidak menunjuk pesanannya', JL, "if (muka > 0) { pb.untukPesanan = UM.id;", "if (muka > 0) {"),
    ('faktur mengabaikan alamat pesanan (DP menutup bon tertua)', FK, "  if (m.untukPesanan !== undefined && m.untukPesanan !== null && String(m.untukPesanan) !== '') {", "  if (false) {"),
    ('KR1 menghitung bagian yang tertutup DP sebagai utang baru', JL, "const baru = s.cara === 'Kredit' ? t.total - t.muka : t.kurang;", "const baru = s.cara === 'Kredit' ? t.total : t.kurang + t.muka;"),
    ('nama pembeli boleh beda dari pemesan ber-DP', JL, "  if (UM.dp > 0 && kunciPelanggan(s.pelanggan) !== kunciPelanggan(UM.nama)) return", "  if (false) return"),
    ('keranjang tidak terisi dari pesanan', JL, "  if (baris.length && !(s.keranjang || []).length) {", "  if (false) {"),
    ('PO tidak menempel di nota', JL, "    if (noPO) d.noPO = noPO;", ""),
    ('batal ber-DP tanpa pilihan lolos', PO, "    if (pilihan !== 'saldo' && pilihan !== 'kembali') return", "    if (false) return"),
    ('Ben boleh mengembalikan uang muka', PO, "    if (pilihan === 'kembali' && !o.owner) return", "    if (false) return"),
    ('pengembalian uang muka bernilai positif', PO, "nominal: -U.total,", "nominal: U.total,"),
    ('nama pemesan boleh diganti', PO, "    if (kunciPelanggan(lama.namaPelanggan) !== kunciPelanggan(nama)) return", "    if (false) return"),
    ('pengingat tidak melihat pesanan yang sudah dibuat', PO, "      if (j.lewati.indexOf(t) >= 0 || poSudahDibuat(j.id, t)) return;", "      if (j.lewati.indexOf(t) >= 0) return;"),
    ('lewati sekali diabaikan', PO, "      if (j.lewati.indexOf(t) >= 0 || poSudahDibuat(j.id, t)) return;", "      if (poSudahDibuat(j.id, t)) return;"),
    ('jadwal 2 minggu jadi mingguan', PO, "const langkah = j.ulang === 'duaMinggu' ? 14 : 7;", "const langkah = 7;"),
    ('jadwal berhenti tetap mengingatkan', PO, "  poJadwalSemua().filter((j) => j.aktif).forEach((j) => {\n    poKejadian(j, poIso(h - PO_TERLEWAT_HARI)", "  poJadwalSemua().forEach((j) => {\n    poKejadian(j, poIso(h - PO_TERLEWAT_HARI)"),
    ('cek stok tanpa laju jual', PO, "const sisaHari = sisa - laju * x.hari - jalan;", "const sisaHari = sisa - jalan;"),
    ('penjaga menerima pesanan baru bernota dari Ben', AK, "(d.trxIdJual !== undefined && d.trxIdJual !== null) || ", ""),
    ('penjaga menerima pembayaran minus dari Ben', AK, "      if (x.koleksi === 'piutangMutasi' && (Number(d.nominal) || 0) < 0) return { tolak: KALIMAT_MINTA_OWNER };\n", ""),
    ('kisi pesanan tidak ditegakkan (uang muka dari karyawan lolos)', AK, "    || baru.some((x) => x.koleksi === 'piutangMutasi' && x.data && x.data.untukPesanan && !x.data.notaTrxId)) t.pesanan = 1;", ") t.pesanan = 1;"),
    ('penjaga menerima Ben menghidupkan pesanan batal', AK, "        if (['dibayar', 'batal'].indexOf(String(lama.status || '')) >= 0) return { tolak: tolakTindakan('koreksi') };\n", ""),
    ('surat jalan bayar di tempat menagih penuh walau ada DP', AJ, "Math.max(0, ajBulat(c.total) - ajBulat(c.uangMuka))", "ajBulat(c.total)"),
    ('struk menyebut DP sebagai kelebihan bayar', STK, "    const muka = Math.round(Number(nota.uangMuka) || 0);", "    const muka = 0;"),
    ('Atur tidak menyimpan hari pengingat', PL, ", hariIngatRutin: pi.hariIngatRutin } }],", " } }],"),
]
RUSAK_STATIS = [
    ('panel tanpa tombol uang muka', 'panel', 'data-aksi="psDpSimpan"', 'data-aksi="psDpX"'),
    ('panel tidak menahan karyawan', 'panel', "tombolAkun(akun(), 'pesanan')", "tombolAkun(akun(), 'jualTunai')"),
    ('akses.js berbeda kolom ubah pesanan dengan rules', 'akses', "'catatan', 'alasanBatal', 'nasibUangMuka'];", "'catatan', 'alasanBatal', 'nasibUangMuka', 'namaPelanggan'];"),
    ('rules membuka kolom jadwal lain', 'rules', "affectedKeys().hasOnly(['namaPelanggan', 'baris',", "affectedKeys().hasOnly(['olehUid', 'namaPelanggan', 'baris',"),
]


def jalan(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
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
    sama, rinci = kolom_sama(src)
    if not sama: g.append('kolom pesanan / jadwal pesanan-logika / akses.js / rules v11 berbeda → ' + json.dumps(rinci, ensure_ascii=False)[:400])
    return len(STATIS) + 1 - len(g), g


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
