#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tanda_kenal.py — paket S2a (19 Nov 2026): QR nomor nota di struk & scan struk → notanya terbuka.

Yang dijaga:
  · tanda-kenal-logika.js (dijalankan apa adanya di jsc): teks QR per bentuk kunci nota, urutan pilih kunci = notaDari (trxId dulu), kunci yang tidak
    bisa dicetak → struk TANPA QR (bukan QR yang salah), bolak-balik cetak → scan → kunci yang sama, kode bukan struk toko tidak dianggap nota,
    QR tidak utuh disebut rusak, lembar berisi isian (bayar, jumlah, …) tidak ditimpa lembar struk
  · paket S2b — pasangan kode → sasaran: kode yang disimpan (barcode / nomor seri kartu), pasangan TERBARU menang, yang dilepas tidak dipakai, hanya
    karung & kemasan yang bisa dipasangi barcode, berat karung dibedakan, mode daftar gugur sendiri, kartu tanpa nama ditolak; koleksi tandaKenal sama di
    koleksi.js / toko.js / akses.js / firestore.rules; jual.js membungkus aksi asli (jalur ketuk biasa tidak berubah)
  · paket S4 — daftar pasangan yang BERLAKU (satu baris per kode, yang dilepas tidak ikut), LEPAS = catatan baru bersasaran kosong (bukan hapus),
    label buatan toko: kode MIQ:B: + 8 huruf tanpa 0 O 1 I, barang yang sudah berlabel memakai kode yang SAMA, barcode pabrik bukan label toko,
    jumlah lembar 1–50 tanpa pembulatan diam-diam; jual.js: printer diperiksa dulu → kode DICATAT → baru dicetak, kabar tampil di dalam lembar
  · sambungan: jual.js mencetak QR hanya bila setelan printer perangkat menyertakannya; scan diperiksa dulu (lembar, nota ada) baru membuka struk;
    app.js meneruskan scan ke layar Jual hanya bila panel jaga tertutup & layar Jual di depan; printer.js / escpos.js sungguh mencetak QR itu

    python3 alat-uji/uji_tanda_kenal.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_tanda_kenal.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import json, os, re, subprocess, sys, tempfile

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
MODUL = os.path.join(AKAR, 'baru', 'js', 'layar', 'tanda-kenal-logika.js')
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'

PEMERIKSA = r"""
const hasil = [];
const cek = (nama, ok, ket) => hasil.push({ nama, ok: !!ok, ket: ket === undefined ? '' : String(ket) });
const J = (x) => JSON.stringify(x);

// ---- teks QR ----
cek('QR nota bernomor transaksi (angka pecahan seperti di data toko)', tkQrNota({ trxId: 1763553890123.25, grupNota: 'G1', id: 9 }) === 'MIQ:N:t:1763553890123.25', tkQrNota({ trxId: 1763553890123.25 }));
cek('QR nota lama bergrup', tkQrNota({ trxId: null, grupNota: 'grup-77', id: 9 }) === 'MIQ:N:g:grup-77');
cek('QR nota satu baris tanpa grup', tkQrNota({ trxId: null, grupNota: null, id: 1761999999999.25 }) === 'MIQ:N:i:1761999999999.25');
cek('id 0 tetap kunci', tkQrNota({ id: 0 }) === 'MIQ:N:i:0');
cek('tanpa nota / tanpa kunci → tanpa QR', tkQrNota(null) === '' && tkQrNota({}) === '' && tkQrNota({ trxId: '', grupNota: '', id: '' }) === '');
cek('kunci berspasi / berhuruf bukan ASCII → tanpa QR (bukan QR yang salah)', tkQrNota({ trxId: 'a b' }) === '' && tkQrNota({ trxId: 'nota—1' }) === '');
cek('kunci terlalu panjang → tanpa QR', tkQrNota({ trxId: 'x'.repeat(TK_PANJANG_MAKS) }) === '' && tkQrNota({ trxId: 'x'.repeat(TK_PANJANG_MAKS - 8) }) !== '');

// ---- bolak-balik cetak → scan ----
for (const n of [{ trxId: 1763553890123.4567 }, { grupNota: 'grup-77' }, { id: 1761999999999.25 }, { trxId: 'T-1:2:3' }]) {
  const u = tkUraiPindai(tkQrNota(n)); const kol = Object.keys(n)[0];
  cek('bolak-balik ' + kol + ' ' + n[kol], u && u.jenis === 'nota' && Object.keys(u.kunci).length === 1 && u.kunci[kol] === String(n[kol]) && typeof u.kunci[kol] === 'string', J(u));
}
cek('hasil scan dirapikan (spasi & baris baru di tepi)', J(tkUraiPindai('  MIQ:N:t:abc \n')) === J({ jenis: 'nota', kunci: { trxId: 'abc' } }), J(tkUraiPindai('  MIQ:N:t:abc \n')));

// ---- bukan struk toko ----
for (const k of ['8991234567890', '(90)NA18250100004', 'miq:n:t:1', 'https://contoh.id/MIQ:N:t:1', 'UJI-CETAK']) {
  const u = tkUraiPindai(k); cek('bukan struk toko: ' + k, u && u.jenis === 'lain' && u.kode === k, J(u));
}
cek('kosong → null', tkUraiPindai('') === null && tkUraiPindai('   ') === null && tkUraiPindai(null) === null && tkUraiPindai(undefined) === null);

// ---- QR struk tidak utuh ----
for (const k of ['MIQ:N:x:abc', 'MIQ:N:t:', 'MIQ:N:t', 'MIQ:N:', 'MIQ:N:t:a b', 'MIQ:N:tabc', 'MIQ:N:t:' + 'x'.repeat(TK_PANJANG_MAKS)]) {
  const u = tkUraiPindai(k); cek('QR struk tidak utuh disebut rusak: ' + k.slice(0, 24), u && u.jenis === 'rusak', J(u));
}

// ---- lembar ----
cek('layar dasar, keranjang, struk lain boleh diganti lembar struk', tkLembarBolehDiganti(null) && tkLembarBolehDiganti('') && tkLembarBolehDiganti(undefined) && tkLembarBolehDiganti('struk') && tkLembarBolehDiganti('keranjang'));
cek('lembar berisi isian TIDAK ditimpa', ['bayar', 'jumlah', 'retur', 'returTanpa', 'pelanggan', 'karcis', 'pesanan', 'potongan'].every((x) => tkLembarBolehDiganti(x) === false));

// ================= paket S2b: pasangan kode → sasaran =================
// ---- kode yang disimpan ----
cek('barcode: angka EAN & kode GS1 berkurung diterima apa adanya, tepinya dirapikan', tkKode('barcode', ' 8991234567890\n') === '8991234567890' && tkKode('barcode', '(90)NA18250100004') === '(90)NA18250100004');
cek('barcode: terlalu pendek / terlalu panjang / berhuruf bukan cetak / QR struk toko ditolak', tkKode('barcode', '123') === '' && tkKode('barcode', 'x'.repeat(65)) === '' && tkKode('barcode', 'beras—5kg') === '' && tkKode('barcode', 'MIQ:N:t:1') === '' && tkKode('barcode', '') === '' && tkKode('barcode', null) === '');
cek('nfc: nomor seri heksa 4–10 byte jadi huruf besar', tkKode('nfc', '04a1b2c3') === '04A1B2C3' && tkKode('nfc', ' 04A1B2C3D4E5F6 ') === '04A1B2C3D4E5F6' && tkKode('nfc', '0102030405060708090A') === '0102030405060708090A');
cek('nfc: bukan heksa / ganjil / terlalu pendek / terlalu panjang ditolak', tkKode('nfc', 'XYZ12345') === '' && tkKode('nfc', '04A1B') === '' && tkKode('nfc', '04A1B2') === '' && tkKode('nfc', '0102030405060708090A0B') === '');
cek('jenis lain tidak punya kode', tkKode('qr', '8991234567890') === '' && tkKode(undefined, '8991234567890') === '');

// ---- mencari pasangan terbaru ----
const D = [
  { id: 100, jenis: 'barcode', kode: '8991234567890', sasaran: { jalur: 'kemasan', kunci: 'Uji 5', berat: '', nama: 'Uji 5 kg' } },
  { id: 300, jenis: 'barcode', kode: '8991234567890', sasaran: { jalur: 'karung', kunci: 'Uji', berat: '50', nama: 'Uji 50 kg' } },
  { id: 200, jenis: 'barcode', kode: '8991234567890', sasaran: { jalur: 'kemasan', kunci: 'Lain', berat: '', nama: 'Lain' } },
  { id: 150, jenis: 'nfc', kode: '04A1B2C3', sasaran: { nama: 'Contoh' } },
  { id: 400, jenis: 'nfc', kode: '8991234567890', sasaran: { nama: 'Kebetulan sama' } },
  { id: 500, jenis: 'barcode', kode: '111122223333', sasaran: { jalur: 'kemasan', kunci: 'Uji 5', berat: '', nama: 'Uji 5 kg' } },
  { id: 600, jenis: 'barcode', kode: '111122223333', sasaran: null },
  null,
];
cek('pasangan terbaru menang (bukan yang pertama, bukan yang terakhir di daftar)', tkCari(D, 'barcode', '8991234567890').id === 300);
cek('jenis ikut dicocokkan (kode sama, jenis lain = pasangan lain)', tkCari(D, 'nfc', '8991234567890').sasaran.nama === 'Kebetulan sama' && tkCari(D, 'nfc', '04A1B2C3').sasaran.nama === 'Contoh');
cek('kode belum dikenal → null; daftar kosong → null', tkCari(D, 'barcode', '0000') === null && tkCari([], 'nfc', '04A1B2C3') === null && tkCari(null, 'nfc', '04A1B2C3') === null);
cek('pasangan yang terakhir DILEPAS (sasaran kosong) → null, tidak jatuh ke pasangan lama', tkCari(D, 'barcode', '111122223333') === null);

// ---- chip rak ----
const RAK = { karung: [{ jalur: 'karung', kunci: 'Uji', berat: 25, nama: 'Uji', ukuran: '25 kg' }, { jalur: 'karung', kunci: 'Uji', berat: 50, nama: 'Uji', ukuran: '50 kg' }],
  kemasan: [{ jalur: 'kemasan', kunci: 'Uji 5', nama: 'Uji', ukuran: '5 kg' }], literan: [{ jalur: 'literan', kunci: 'Uji', nama: 'Uji', ukuran: 'per liter' }], repack: [], wadah: [] };
cek('sasaran dari chip karung membawa berat', J(tkSasaranChip(RAK.karung[1])) === J({ jalur: 'karung', kunci: 'Uji', berat: '50', nama: 'Uji 50 kg' }), J(tkSasaranChip(RAK.karung[1])));
cek('sasaran dari chip kemasan', J(tkSasaranChip(RAK.kemasan[0])) === J({ jalur: 'kemasan', kunci: 'Uji 5', berat: '', nama: 'Uji 5 kg' }), J(tkSasaranChip(RAK.kemasan[0])));
cek('literan / repack / wadah / kosong tidak bisa dipasangi barcode', tkSasaranChip(RAK.literan[0]) === null && tkSasaranChip({ jalur: 'repack', kunci: 'Uji' }) === null && tkSasaranChip({ jalur: 'wadah', kunci: 'W' }) === null && tkSasaranChip(null) === null && tkSasaranChip({ jalur: 'kemasan', kunci: '' }) === null);
cek('chip dari sasaran: karung dibedakan beratnya', tkChipDari(RAK, { jalur: 'karung', kunci: 'Uji', berat: '50' }) === RAK.karung[1] && tkChipDari(RAK, { jalur: 'karung', kunci: 'Uji', berat: '25' }) === RAK.karung[0]);
cek('bolak-balik chip → sasaran → chip yang sama', [RAK.karung[0], RAK.karung[1], RAK.kemasan[0]].every((c) => tkChipDari(RAK, tkSasaranChip(c)) === c));
cek('barang tidak sedang di rak → null (tidak dipilihkan barang lain)', tkChipDari(RAK, { jalur: 'kemasan', kunci: 'Habis', berat: '' }) === null && tkChipDari(RAK, { jalur: 'karung', kunci: 'Uji', berat: '10' }) === null && tkChipDari(RAK, { jalur: 'literan', kunci: 'Uji' }) === null && tkChipDari(null, { jalur: 'kemasan', kunci: 'Uji 5' }) === null && tkChipDari(RAK, null) === null);

// ---- mode daftar gugur sendiri ----
const TKD = { jenis: 'barcode', kode: '8991234567890', mode: 'daftar', pada: 1000000 };
cek('mode daftar berlaku sampai batas gugur, lalu tidak', tkMasihDaftar(TKD, 'barcode', 1000000 + TK_DAFTAR_GUGUR_MS) === true && tkMasihDaftar(TKD, 'barcode', 1000001 + TK_DAFTAR_GUGUR_MS) === false);
cek('mode daftar: jenis lain / mode kenal / kosong = tidak', tkMasihDaftar(TKD, 'nfc', 1000001) === false && tkMasihDaftar(Object.assign({}, TKD, { mode: 'kenal' }), 'barcode', 1000001) === false && tkMasihDaftar(null, 'barcode', 1) === false);
cek('batas gugur: cukup untuk mencari barangnya, tidak sampai menempel ke pembeli berikutnya', TK_DAFTAR_GUGUR_MS >= 20000 && TK_DAFTAR_GUGUR_MS <= 120000);

// ---- menyusun pasangan baru ----
let nId = 0; const W = { tanggal: '2026-11-19', jam: '19:05', idUnik: () => 7000 + (++nId) };
let r = tkSusunDaftar('barcode', ' 8991234567890 ', tkSasaranChip(RAK.karung[1]), W);
cek('daftar barcode: satu dokumen tandaKenal, kode dirapikan, sasaran lengkap', r.dokumen && r.dokumen.length === 1 && r.dokumen[0].koleksi === 'tandaKenal' && J(r.dokumen[0].data) === J({ id: 7001, jenis: 'barcode', kode: '8991234567890', sasaran: { jalur: 'karung', kunci: 'Uji', berat: '50', nama: 'Uji 50 kg' }, tanggal: '2026-11-19', jam: '19:05' }), J(r));
cek('daftar barcode: mode daftar ditutup & kabarnya menyebut barangnya', r.patch.tk === null && r.patch.kabarAwas === false && /8991234567890/.test(r.patch.kabar) && /Uji 50 kg/.test(r.patch.kabar), r.patch.kabar);
cek('daftar barcode ke literan / tanpa sasaran DITOLAK dengan kalimat', !!tkSusunDaftar('barcode', '8991234567890', tkSasaranChip(RAK.literan[0]), W).tolak && !!tkSusunDaftar('barcode', '8991234567890', { jalur: 'literan', kunci: 'Uji' }, W).tolak && !tkSusunDaftar('barcode', '8991234567890', null, W).dokumen);
cek('daftar barcode berkode rusak DITOLAK', !!tkSusunDaftar('barcode', '12', tkSasaranChip(RAK.kemasan[0]), W).tolak && !!tkSusunDaftar('barcode', 'MIQ:N:t:1', tkSasaranChip(RAK.kemasan[0]), W).tolak);
r = tkSusunDaftar('nfc', '04a1b2c3d4e5f6', { nama: '  Contoh Pembeli  ' }, W);
cek('daftar kartu: nomor seri huruf besar, nama dirapikan', r.dokumen && J(r.dokumen[0].data.sasaran) === J({ nama: 'Contoh Pembeli' }) && r.dokumen[0].data.kode === '04A1B2C3D4E5F6' && r.dokumen[0].data.jenis === 'nfc' && /Contoh Pembeli/.test(r.patch.kabar), J(r));
cek('daftar kartu tanpa nama / nomor seri rusak DITOLAK', !!tkSusunDaftar('nfc', '04A1B2C3', { nama: '   ' }, W).tolak && !!tkSusunDaftar('nfc', '04A1B2C3', null, W).tolak && !!tkSusunDaftar('nfc', 'bukan-heksa', { nama: 'Contoh' }, W).tolak);
cek('yang baru didaftarkan langsung ditemukan & menang atas yang lama', (() => { const baru = tkSusunDaftar('barcode', '8991234567890', tkSasaranChip(RAK.kemasan[0]), W).dokumen[0].data; const d = tkCari(D.concat([baru]), 'barcode', '8991234567890'); return d === baru && tkChipDari(RAK, d.sasaran) === RAK.kemasan[0]; })());
cek('kode panjang dipendekkan di kalimat, kode pendek utuh', tkRingkasKode('8991234567890') === '8991234567890' && tkRingkasKode('(01)08991234567890(10)ABC123') === '(01)0899…ABC123');

// ================= paket S4: daftar yang berlaku, lepas, label buatan toko =================
const DK = tkDaftarKini(D);
cek('daftar berlaku: satu baris per kode (catatan terbarunya), yang dilepas tidak ikut, terbaru di atas', J(DK.map((x) => x.id)) === J([400, 300, 150]), J(DK.map((x) => x.id)));
cek('daftar berlaku: kosong / null / jenis asing aman', tkDaftarKini(null).length === 0 && tkDaftarKini([]).length === 0 && tkDaftarKini([null, { id: 1, jenis: 'qr', kode: 'x', sasaran: { nama: 'x' } }]).length === 0);
const LP = tkSusunLepas(D, 'barcode', ' 8991234567890 ', W);
cek('lepas: SATU catatan baru bersasaran kosong untuk kode itu — tidak ada yang dihapus', LP.dokumen && LP.dokumen.length === 1 && LP.dokumen[0].koleksi === 'tandaKenal' && LP.dokumen[0].data.sasaran === null && LP.dokumen[0].data.kode === '8991234567890' && LP.dokumen[0].data.jenis === 'barcode' && LP.hapus === undefined && /Uji 50 kg/.test(LP.patch.kabar) && LP.patch.kabarAwas === false, J(LP));
const D2 = D.concat([LP.dokumen[0].data]);
cek('lepas: kode itu kembali belum dikenal & hilang dari daftar; kartu yang kebetulan berkode sama TIDAK ikut lepas', tkCari(D2, 'barcode', '8991234567890') === null && tkCari(D2, 'nfc', '8991234567890') !== null && J(tkDaftarKini(D2).map((x) => x.id)) === J([400, 150]), J(tkDaftarKini(D2).map((x) => x.id)));
cek('lepas: kode yang tidak terpasang / sudah dilepas / rusak DITOLAK tanpa dokumen', [tkSusunLepas(D, 'barcode', '0000000', W), tkSusunLepas(D, 'barcode', '111122223333', W), tkSusunLepas(D, 'nfc', 'bukan-heksa', W), tkSusunLepas(D2, 'barcode', '8991234567890', W)].every((x) => !!x.tolak && !x.dokumen));
cek('lepas kartu: kalimatnya menyebut pemiliknya', /Contoh/.test(tkSusunLepas(D, 'nfc', '04a1b2c3', W).patch.kabar) && /^Kartu /.test(tkSusunLepas(D, 'nfc', '04a1b2c3', W).patch.kabar));
cek('lepas lalu pasang lagi: pasangan baru yang berlaku', (() => { const baru = tkSusunDaftar('barcode', '8991234567890', tkSasaranChip(RAK.kemasan[0]), W).dokumen[0].data; return tkCari(D2.concat([baru]), 'barcode', '8991234567890') === baru; })());

const gilir = (arr) => { let i = 0; return () => arr[i++ % arr.length]; };
cek('kode label: awalan toko + 8 huruf tanpa 0 O 1 I; lolos sebagai barcode, bukan QR struk', (() => { const k = tkKodeLabel(gilir([0, 0.5, 0.999, 0.03, 0.2, 0.7, 0.9, 0.4]), null); return /^MIQ:B:[2-9A-HJ-NP-Z]{8}$/.test(k) && tkKode('barcode', k) === k && tkUraiPindai(k).jenis === 'lain'; })());
cek('kode label: acak di tepi (0 dan 1) tetap sah', tkKodeLabel(() => 0) === 'MIQ:B:22222222' && tkKodeLabel(() => 1) === 'MIQ:B:ZZZZZZZZ' && TK_HURUF_LABEL.length === 32 && !/[0O1I]/.test(TK_HURUF_LABEL));
cek('kode label: yang sudah terpakai dilewati; semuanya terpakai → kosong (bukan kode kembar)', tkKodeLabel(gilir(new Array(8).fill(0).concat(new Array(8).fill(0.5))), (k) => k === 'MIQ:B:22222222') === 'MIQ:B:JJJJJJJJ' && tkKodeLabel(() => 0, () => true) === '');
const SL = tkSiapkanLabel(D, RAK.kemasan[0], W, () => 0.5);
cek('siapkan label: barang belum berlabel → kode baru + catatan pasangannya', SL.kode === 'MIQ:B:JJJJJJJJ' && SL.dokumen.length === 1 && SL.dokumen[0].koleksi === 'tandaKenal' && SL.dokumen[0].data.kode === SL.kode && J(SL.dokumen[0].data.sasaran) === J(tkSasaranChip(RAK.kemasan[0])) && J(SL.sasaran) === J(tkSasaranChip(RAK.kemasan[0])), J(SL));
const D3 = D.concat([SL.dokumen[0].data]);
cek('siapkan label: barang yang SUDAH berlabel memakai kode yang sama, tanpa catatan baru', (() => { const x = tkSiapkanLabel(D3, RAK.kemasan[0], W, () => 0.1); return x.kode === SL.kode && x.dokumen.length === 0 && J(x.sasaran) === J(SL.sasaran); })());
cek('siapkan label: barcode pabrik bukan label toko (barang itu tetap dibuatkan kode toko)', (() => { const x = tkSiapkanLabel(D, RAK.karung[1], W, () => 0.5); return x.dokumen.length === 1 && x.kode.indexOf(TK_AWALAN_LABEL) === 0; })());
cek('siapkan label: karung 25 kg & 50 kg tidak berbagi label', (() => { const a = tkSiapkanLabel(D, RAK.karung[0], W, () => 0.5); const b = tkSiapkanLabel(D.concat([a.dokumen[0].data]), RAK.karung[1], W, () => 0.25); return b.dokumen.length === 1 && b.kode !== a.kode; })());
cek('siapkan label: label yang sudah dilepas tidak dipakai lagi', (() => { const lepas = tkSusunLepas(D3, 'barcode', SL.kode, W).dokumen[0].data; const x = tkSiapkanLabel(D3.concat([lepas]), RAK.kemasan[0], W, () => 0.25); return x.dokumen.length === 1 && x.kode !== SL.kode; })());
cek('siapkan label: kode acak yang bentrok dengan kode yang pernah dipakai diganti', tkSiapkanLabel(D3, RAK.karung[1], W, gilir(new Array(8).fill(0.5).concat(new Array(8).fill(0.25)))).kode === 'MIQ:B:AAAAAAAA');
cek('siapkan label: literan / tanpa barang DITOLAK dengan kalimat', !!tkSiapkanLabel(D, RAK.literan[0], W, () => 0.5).tolak && !!tkSiapkanLabel(D, undefined, W, () => 0.5).tolak && !tkSiapkanLabel(D, RAK.literan[0], W, () => 0.5).dokumen);
cek('isi label: nama barang, kode UTUH untuk QR, kode pendek untuk dibaca orang', J(tkIsiLabel({ nama: 'Uji 5 kg' }, 'MIQ:B:JJJJJJJJ')) === J({ judul: 'Uji 5 kg', ket: 'TOKO BERAS M.IQBAL', kode: 'MIQ:B:JJJJJJJJ', teksKode: 'JJJJJJJJ' }) && tkIsiLabel({ nama: 'X' }, '8991234567890').teksKode === '8991234567890' && tkIsiLabel({ nama: 'X' }, '8991234567890').kode === '8991234567890');
cek('jumlah label: bulat 1–50; selain itu ditolak (0), tidak dibulatkan diam-diam', tkJumlahLabel(1) === 1 && tkJumlahLabel('20') === 20 && tkJumlahLabel(TK_LABEL_MAKS) === 50 && [0, 51, 2.5, '', 'abc', null, undefined, -3].every((v) => tkJumlahLabel(v) === 0));
cek('kode label CONTOH layar Perangkat tidak pernah jadi barcode barang', tkKode('barcode', 'UJI-LABEL-0001') === '' && !!tkSusunDaftar('barcode', 'UJI-LABEL-0001', tkSasaranChip(RAK.kemasan[0]), W).tolak);

print(JSON.stringify(hasil));
"""


def baca(*bagian):
    with open(os.path.join(AKAR, *bagian), encoding='utf-8') as f: return f.read()


def siapkan(sumber):
    return sumber.replace('export const ', 'const ').replace('export function ', 'function ')


def jalankan_jsc(sumber):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(siapkan(sumber) + '\n' + PEMERIKSA); p = f.name
    try:
        r = subprocess.run([JSC, p], capture_output=True, text=True)
    finally:
        os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip():
        return [{'nama': 'jsc tidak jalan', 'ok': False, 'ket': (r.stderr or r.stdout).strip()[:400]}]
    return json.loads(r.stdout.strip().splitlines()[-1])


def periksa_statis(logika, jual, app):
    h = []; ok = lambda nama, benar, ket='': h.append({'nama': nama, 'ok': bool(benar), 'ket': str(ket)})
    ok('modul tanpa impor (dijalankan apa adanya di jsc)', not re.search(r'^\s*import\s', logika, re.M))
    ok('jual.js: QR dicetak hanya bila setelan printer perangkat menyertakan QR, isinya dari tkQrNota',
       "const qr = PR.prAtur().qr ? TK.tkQrNota(nota) : '';" in jual and "PR.cetakGaris(st.garis, { logoToko: st.logo, qr })" in jual and jual.count('PR.cetakGaris(') == 1)
    blok = jual[jual.index('  function pindai(teks) {'):]; blok = blok[:blok.index('\n  }\n') + 5]
    urut = [blok.find(x) for x in ("u.jenis === 'lain'", "u.jenis === 'rusak'", 'TK.tkLembarBolehDiganti(S().lembar)', 'ST.notaDari(u.kunci)', 'aksi.bukaStruk(')]
    ok('jual.js: scan diperiksa dulu (kode lain, rusak, lembar terbuka, nota ada) BARU membuka struk', all(x >= 0 for x in urut) and urut == sorted(urut) and blok.count('aksi.bukaStruk(') == 1, urut)
    ok('jual.js: layar terkunci tidak menanggapi scan', 'terkunci()' in blok.split("u.jenis === 'rusak'")[0])
    ok('jual.js: tiap penolakan scan berkabar (tidak diam)', blok.count('kabarAwas: true') == 3)
    ok('jual.js: pindai keluar dari pasangLayarJual', 'pulihkanKeranjang, pindai, ' in jual)
    ok('app.js: scan ke layar Jual hanya bila panel jaga tertutup & layar Jual di depan, galatnya ditelan',
       "if (panelOrang.hidden) { if (tabKini === 'jual') { try { layar.pindai(x && x.data); } catch (e) { console.error('pindai jual', e); } } return; }" in app and app.count('layar.pindai(') == 1)
    ok('index.html: modul dipramuat', '<link rel="modulepreload" href="js/layar/tanda-kenal-logika.js">' in baca('baru', 'index.html'))
    pr = baca('baru', 'js', 'inti', 'printer.js'); ep = baca('baru', 'js', 'inti', 'escpos.js')
    ok('printer.js: QR dari pemanggil menimpa bawaan kosong', "susunCetak(garis, null, Object.assign({ qr: '' }, ekstra || {}))" in pr)
    ok('escpos.js: ekor struk mencetak QR bila ada', 'if (o.qr) {' in ep and 'tulisQr(w, o.qr, o.qrUkuran)' in ep)
    ok('struk-logika.js: notaDari membandingkan kunci sebagai teks (kunci hasil scan = teks)',
       all(x in baca('baru', 'js', 'layar', 'struk-logika.js') for x in ('String(x.trxId) === String(kunci.trxId)', 'String(x.grupNota) === String(kunci.grupNota)', 'String(x.id) === String(kunci.id)')))
    # ---- paket S2b: koleksi tandaKenal terpasang di semua tempat yang harus sepakat ----
    kol = baca('baru', 'js', 'data', 'koleksi.js'); aks = baca('baru', 'js', 'data', 'akses.js'); rules = baca('firestore.rules')
    ok('koleksi.js: tandaKenal didengar penuh (kelas tetap — dokumennya tanpa cap jam server)', "{ nama: 'tandaKenal',          urut: 'id',    cache: 'tandaKenal', kelas: 'tetap' }," in kol)
    ok('toko.js: ambilTandaKenal membaca cache yang sama', "export function ambilTandaKenal() { return _cache.tandaKenal || []; }" in baca('baru', 'js', 'data', 'toko.js'))
    baca_staf = re.search(r"export const BACA_STAF = \[(.*?)\];", aks, re.S).group(1); buat_staf = re.search(r"export const BUAT_STAF = \{(.*?)\};", aks, re.S).group(1)
    ok('akses.js: akun tablet membaca & membuat tandaKenal (ben, karyawan) — sama dengan rules v12', "'tandaKenal'" in baca_staf and "tandaKenal: ['ben', 'karyawan']" in buat_staf)
    blok = re.search(r"\n    match /tandaKenal/\{id\} \{\n(.*?)\n    \}", rules, re.S)
    ok('firestore.rules: blok tandaKenal — baca owner/ben/karyawan, buat owner atau staf atas nama sendiri, ubah & hapus owner',
       blok and [x.strip() for x in blok.group(1).split('\n')] == ["allow read: if owner() || staf(['ben', 'karyawan']);", "allow create: if owner() || stafBuat(['ben', 'karyawan']);", "allow update, delete: if owner();"])
    ok('jual.js: aksi chip & pilih pembeli ASLI tidak diubah (dibungkus)',
       "    chip: ({ jalur, kunci, berat }) => { const rak = rakKini(); const c = (rak[jalur] || []).find((x) => x.kunci === kunci && (!berat || String(x.berat) === berat)); if (c) set(Object.assign({ isiW: null }, L.ketukChip(S(), c))); }," in jual
       and "    pilihPelanggan: ({ nama }) => set(Object.assign({ lembar: null, cariPelanggan: '', kabar: '' }, L.gantiPelanggan(SBN(), nama)))," in jual)
    ok('jual.js: bungkus chip memasangkan dulu, lalu aksi asli; ditolak = ketukan berhenti', "if (tkPasangChip(c)) chipAsal(arg, el, ev);" in jual and "if (tkPasangChip(c)) seringAsal(arg, el, ev);" in jual and "if (r.tolak) { set({ kabar: r.tolak, kabarAwas: true }); return false; }" in jual)
    ok('jual.js: mode daftar yang gugur tidak memasangkan (barcode & kartu)', "if (!TK.tkMasihDaftar(t, 'barcode', Date.now())) { set({ tk: null }); return true; }" in jual and "if (!TK.tkMasihDaftar(t, 'nfc', Date.now()) || !nama) return set({ tk: null });" in jual)
    ok('jual.js: lembar pembeli ditutup tanpa memilih → kartu yang menunggu dilupakan', "aksi.tutup = (arg, el, ev) => { const t = S().tk; tutupAsal(arg, el, ev); if (t && t.jenis === 'nfc') set({ tk: null }); };" in jual)
    pb = jual[jual.index('  function pindaiBarcode(mentah) {'):]; pb = pb[:pb.index('\n  }\n') + 5]
    urut = [pb.find(x) for x in ("if (!kode) return set(", "TK.tkLembarBolehDiganti(S().lembar)", "TK.tkCari(ambilTandaKenal(), 'barcode', kode)", "if (!d) { lampu('lampuAsing'); return set({ tk: { jenis: 'barcode', kode, mode: 'daftar'", "TK.tkChipDari(rakKini(), d.sasaran)", "if (!c) return set(", "L.ketukChip(S(), c)")]
    ok('jual.js: barcode — kode sah, lembar, dikenal?, barang di rak? BARU lembar jumlah (jalur ketukChip yang sama; tidak ada harga baru)', all(x >= 0 for x in urut) and urut == sorted(urut) and 'masukkan(' not in pb and 'hargaSatuan' not in pb, urut)
    tp = jual[jual.index('  function tempel(uidMentah) {'):]; tp = tp[:tp.index('\n  }\n') + 5]
    urut = [tp.find(x) for x in ("if (!kode || terkunci()) return;", "TK.tkLembarBolehDiganti(s.lembar) && s.lembar !== 'pelanggan'", "TK.tkCari(ambilTandaKenal(), 'nfc', kode)", "lembar: 'pelanggan'", "L.gantiPelanggan(SBN(), nama)")]
    ok('jual.js: kartu — lembar, dikenal?, belum → lembar pembeli; dikenal → gantiPelanggan (jalur pilih nama yang sama), kabar harga tidak ditimpa', all(x >= 0 for x in urut) and urut == sorted(urut) and "g.kabar ? {} : { kabar: 'Kartu pelanggan: ' + nama, kabarAwas: false }" in tp, urut)
    ok('jual.js: pita mode daftar & pita "salah barang? ganti" tampil; tempel keluar dari layar', 'data-k="pita-tk-daftar"' in jual and 'data-k="pita-tk-kenal"' in jual and 'data-k="pita-tk-kartu"' in jual and 'data-aksi="tkGanti"' in jual and jual.count('data-aksi="tkBatal"') == 3
       and "${s.kabar || s.tk || adaUrung ||" in jual and 'pulihkanKeranjang, pindai, tempel,\n' in jual)
    # ---- paket S4: lembar Label & kartu ----
    ok('jual.js S4: tombol pembuka, lembar, dan kabar DI DALAM lembar (kabar di belakang lembar tidak terlihat)',
       jual.count('data-aksi="bukaTandaKenal"') == 1 and "if (s.lembar === 'tandaKenal') return gambarTandaKenal(s, L1, muncul, kepala);" in jual
       and 'data-k="lembar-tandaKenal"' in jual and 'data-k="kabar-tandaKenal" data-aksi="tutupKabar">${s.kabar}</div>' in jual)
    ok('jual.js S4: yang ditampilkan hanya pasangan yang berlaku', "const semua = TK.tkDaftarKini(ambilTandaKenal());" in jual)
    ok('jual.js S4: Lepas bertanya dulu; yang ditulis catatan lepas (tkSusunLepas), bukan penghapusan',
       jual.count('data-aksi="tkLepasTanya"') == 2 and jual.count('data-aksi="tkLepas"') == 1 and 'YA, LEPAS' in jual
       and "const r = TK.tkSusunLepas(ambilTandaKenal(), t.jenis, t.kode, tkWaktu()); if (r.patch) r.patch.tkLepas = null; else set({ tkLepas: null }); return tulisUmum(r); };" in jual)
    lc = jual[jual.index('    aksi.tkLabelCetak = async () => {'):]; lc = lc[:lc.index('\n    };\n') + 8]
    urut = [lc.find(x) for x in ("const n = TK.tkJumlahLabel(st.tkLabelN); if (!n) return set(", "if (await PR.jalurCetak() === 'dialog') return set(", "TK.tkSiapkanLabel(ambilTandaKenal(), c, tkWaktu(), Math.random)",
                                 "const hsl = await tulisDokumen(dokumen); if (hsl && hsl.gagal) return set({ kabar: 'DITOLAK, kode label tidak tercatat: '", "const r = await PR.cetakLabel(isiL, n)")]   # 26 Nov 2026: isi label = isiL (kemasan lengkap / karung tkIsiLabel)
    ok('jual.js S4: cetak label — jumlah sah, printer ada, kode DICATAT (ditolak = berhenti), BARU dicetak', all(x >= 0 for x in urut) and urut == sorted(urut) and lc.count('PR.cetakLabel(') == 1 and lc.count('tulisDokumen(') == 1, urut)
    ok('jual.js S4: label gagal tercetak = berkabar & menyebut kodenya sudah tercatat; label tidak menyentuh keranjang / harga',
       "set({ kabar: 'Label tidak tercetak: '" in lc and "kodenya sudah tercatat, tinggal tekan Cetak label lagi" in lc and 'keranjang' not in lc and 'harga' not in lc.lower())
    ok('jual.js S4: lampu kejadian scan & kartu lewat pembungkus yang menelan galat', jual.count("lampu('lampuKenal')") == 3 and jual.count("lampu('lampuAsing')") == 3 and not re.search(r"(?<!['\w.])lampu(Kenal|Asing|Kertas)\(", jual))
    ok('app.js: kartu ke layar Jual hanya bila panel jaga tertutup & layar Jual di depan, galatnya ditelan',
       "padaTempel((x) => { if (panelOrang.hidden && tabKini === 'jual') { try { layar.tempel(x && x.uid); } catch (e) { console.error('tempel jual', e); } } });" in app)
    return h


def periksa(logika, jual, app, diam=False):
    try: statis = periksa_statis(logika, jual, app)
    except Exception as e: statis = [{'nama': 'pemeriksa statis jatuh', 'ok': False, 'ket': repr(e)[:300]}]
    h = jalankan_jsc(logika) + statis
    gagal = [x for x in h if not x['ok']]
    if not diam:
        for x in h: print(('  ok  ' if x['ok'] else 'GAGAL ') + x['nama'] + ('' if x['ok'] or not x['ket'] else ' · ' + x['ket']))
        print(('LULUS ' if not gagal else 'GAGAL ') + str(len(h) - len(gagal)) + '/' + str(len(h)))
    return not gagal


# (nama, berkas 'logika' | 'jual' | 'app', lama, baru)
MUTASI = [
    ('QR memilih grup walau nota bernomor transaksi', 'logika', "ada(nota.trxId) ? ['t', nota.trxId] : ", ""),
    ('kunci yang tak bisa dicetak tetap jadi QR', 'logika', "return CETAK.test(String(pilih[1])) && teks.length <= TK_PANJANG_MAKS ? teks : '';", "return teks;"),
    ('kode bukan struk toko dianggap struk', 'logika', "if (t.indexOf(TK_AWALAN_NOTA) !== 0) return { jenis: 'lain', kode: t };", ""),
    ('QR struk tidak utuh dianggap nota', 'logika', "if (!kolom || sisa.charAt(1) !== ':' || !CETAK.test(nilai) || t.length > TK_PANJANG_MAKS) return { jenis: 'rusak', kode: t };", ""),
    ('kunci grup dibaca sebagai nomor transaksi', 'logika', "const KUNCI_DARI = { t: 'trxId', g: 'grupNota', i: 'id' };", "const KUNCI_DARI = { t: 'trxId', g: 'trxId', i: 'id' };"),
    ('hasil scan tidak dirapikan', 'logika', "teks).trim();", "teks);"),
    ('lembar bayar ditimpa lembar struk', 'logika', "!lembar || lembar === 'struk' || lembar === 'keranjang'", "true"),
    ('QR dicetak walau setelan perangkat tidak menyertakannya', 'jual', "const qr = PR.prAtur().qr ? TK.tkQrNota(nota) : '';", "const qr = TK.tkQrNota(nota);"),
    ('QR tidak ikut ke printer', 'jual', "PR.cetakGaris(st.garis, { logoToko: st.logo, qr })", "PR.cetakGaris(st.garis, { logoToko: st.logo })"),
    ('struk dibuka tanpa memeriksa lembar yang terbuka', 'jual', "    if (!TK.tkLembarBolehDiganti(S().lembar)) return set({ kabar: 'Struk ter-scan, tapi lembar ini masih terbuka — tutup dulu, lalu scan lagi', kabarAwas: true });\n", ""),
    ('struk dibuka walau notanya tidak ada', 'jual', "    if (!ST.notaDari(u.kunci)) return set({", "    if (false) return set({"),
    ('S2b: QR struk toko bisa didaftarkan sebagai barcode barang', 'logika', " && t.indexOf(TK_AWALAN_NOTA) !== 0 && t.indexOf(TK_KODE_CONTOH) !== 0 ? t : '';", " && t.indexOf(TK_KODE_CONTOH) !== 0 ? t : '';"),
    ('S2b: nomor seri bukan heksa diterima', 'logika', "return /^(?:[0-9A-F]{2}){4,10}$/.test(u) ? u : '';", "return u;"),
    ('S2b: pasangan pertama yang menang (bukan terbaru)', 'logika', "(!d || Number(x.id) > Number(d.id))", "!d"),
    ('S2b: jenis tidak dicocokkan (barcode terbaca sebagai kartu)', 'logika', "x.jenis === jenis && String(x.kode)", "String(x.kode)"),
    ('S2b: pasangan yang dilepas tetap dipakai', 'logika', "return d && d.sasaran && typeof d.sasaran === 'object' ? d : null;", "return d;"),
    ('S2b: literan bisa dipasangi barcode', 'logika', "export const TK_JALUR_BARCODE = ['karung', 'kemasan'];", "export const TK_JALUR_BARCODE = ['karung', 'kemasan', 'literan'];"),
    ('S2b: berat karung tidak dibedakan', 'logika', " && (!sasaran.berat || String(x.berat) === String(sasaran.berat))) || null;", ") || null;"),
    ('S2b: mode daftar tidak pernah gugur', 'logika', " && Number(kini) - Number(tk.pada || 0) <= TK_DAFTAR_GUGUR_MS);", ");"),
    ('S2b: kartu didaftarkan tanpa nama', 'logika', "    if (!nama) return { tolak: 'Pilih nama pembelinya dulu' };\n", ""),
    ('S2b: mendaftarkan tidak menutup mode daftar', 'logika', "patch: { tk: null, kabar:", "patch: { kabar:"),
    ('S2b: chip ditolak tetap membuka lembar jumlah', 'jual', "if (tkPasangChip(c)) chipAsal(arg, el, ev);", "tkPasangChip(c); chipAsal(arg, el, ev);"),
    ('S2b: mode daftar gugur tetap memasangkan barcode', 'jual', "    if (!TK.tkMasihDaftar(t, 'barcode', Date.now())) { set({ tk: null }); return true; }\n", ""),
    ('S2b: kartu yang menunggu tidak dilupakan saat lembar ditutup', 'jual', " if (t && t.jenis === 'nfc') set({ tk: null }); };", " };"),
    ('S2b: barcode dikenal tapi barangnya tidak di rak → diam', 'jual', "    if (!c) return set({ tk: kenal, kabar:", "    if (!c) return; set({ tk: kenal, kabar:"),
    ('S2b: kabar perubahan harga saat ganti pembeli ditimpa kabar kartu', 'jual', "g.kabar ? {} : { kabar: 'Kartu pelanggan: ' + nama, kabarAwas: false }", "{ kabar: 'Kartu pelanggan: ' + nama, kabarAwas: false }"),
    ('S4: daftar memuat pasangan yang sudah dilepas', 'logika', ".filter((x) => x.sasaran && typeof x.sasaran === 'object').sort(", ".sort("),
    ('S4: daftar memuat catatan lama (bukan yang terbaru per kode)', 'logika', "if (!akhir[k] || Number(x.id) > Number(akhir[k].id)) akhir[k] = x;", "if (!akhir[k]) akhir[k] = x;"),
    ('S4: lepas menulis ulang sasaran lama (tidak melepas)', 'logika', "kode, sasaran: null, tanggal: w.tanggal", "kode, sasaran: d.sasaran, tanggal: w.tanggal"),
    ('S4: lepas kode yang tidak terpasang diterima', 'logika', "  if (!d) return { tolak: (jenis === 'nfc' ? 'Kartu' : 'Barcode') + ' ini tidak sedang terpasang' };\n", "  if (!d) return { dokumen: [], patch: { kabar: '' } };\n"),
    ('S4: label toko tidak dipakai lagi (kode baru tiap cetak)', 'logika', "  if (ada) return { kode: String(ada.kode), sasaran: ada.sasaran, dokumen: [] };\n", ""),
    ('S4: barcode pabrik dianggap label toko', 'logika', "x.jenis === 'barcode' && String(x.kode).indexOf(TK_AWALAN_LABEL) === 0 && x.sasaran.jalur", "x.jenis === 'barcode' && x.sasaran.jalur"),
    ('S4: berat karung tidak dibedakan di label', 'logika', " && String(x.sasaran.berat || '') === String(sasaran.berat || '')) || null;", ") || null;"),
    ('S4: kode label yang bentrok tetap dipakai', 'logika', "const kode = TK_AWALAN_LABEL + s; if (!sudahAda || !sudahAda(kode)) return kode;", "const kode = TK_AWALAN_LABEL + s; return kode;"),
    ('S4: huruf yang mudah tertukar masuk kode label', 'logika', "export const TK_HURUF_LABEL = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';", "export const TK_HURUF_LABEL = '0123456789ABCDEFGHIJKLMNOPQRSTUV';"),
    ('S4: jumlah label dibulatkan diam-diam', 'logika', "return Number.isInteger(n) && n >= 1 && n <= TK_LABEL_MAKS ? n : 0;", "return n >= 1 && n <= TK_LABEL_MAKS ? Math.round(n) : 0;"),
    ('S4: label contoh layar Perangkat bisa jadi barcode barang', 'logika', " && t.indexOf(TK_KODE_CONTOH) !== 0 ? t : '';", " ? t : '';"),
    ('S4: QR label berisi kode pendek (scanner membaca kode yang tidak terdaftar)', 'logika', "return { judul: String((sasaran && sasaran.nama) || '').slice(0, 80), ket: 'TOKO BERAS M.IQBAL', kode: k,", "return { judul: String((sasaran && sasaran.nama) || '').slice(0, 80), ket: 'TOKO BERAS M.IQBAL', kode: tkRingkasKode(k).slice(6),"),
    ('S4: label dicetak walau kodenya ditolak server', 'jual', "const hsl = await tulisDokumen(dokumen); if (hsl && hsl.gagal) return set({ kabar: 'DITOLAK, kode label tidak tercatat: '", "const hsl = await tulisDokumen(dokumen); if (false) return set({ kabar: 'DITOLAK, kode label tidak tercatat: '"),
    ('S4: kode label dibuat walau perangkat tanpa printer', 'jual', "      if (await PR.jalurCetak() === 'dialog') return set({ kabar: 'Tidak ada printer di perangkat ini — label dicetak dari tablet kasir', kabarAwas: true });\n", ""),
    ('S4: kabar tidak tampil di dalam lembar Label & kartu', 'jual', '      ${s.kabar ? h`<div class="pita-info ${s.kabarAwas ? \'awas\' : \'\'}" data-k="kabar-tandaKenal" data-aksi="tutupKabar">${s.kabar}</div>` : \'\'}\n', ''),
    ('S4: lepas langsung tanpa bertanya', 'jual', 'data-aksi="tkLepasTanya" data-jenis="nfc"', 'data-aksi="tkLepas" data-jenis="nfc"'),
    ('S4: daftar menampilkan semua catatan, termasuk yang dilepas', 'jual', "const semua = TK.tkDaftarKini(ambilTandaKenal());", "const semua = ambilTandaKenal();"),
    ('S2b: kartu diteruskan ke Jual saat panel jaga terbuka', 'app', "padaTempel((x) => { if (panelOrang.hidden && tabKini === 'jual')", "padaTempel((x) => { if (tabKini === 'jual')"),
    ('scan diteruskan ke Jual walau layar lain di depan', 'app', "if (tabKini === 'jual') { try { layar.pindai(", "if (true) { try { layar.pindai("),
    ('scan diteruskan ke Jual saat panel jaga terbuka', 'app', "if (panelOrang.hidden) { if (tabKini === 'jual')", "if (true) { if (tabKini === 'jual')"),
]


def main():
    if not os.path.exists(JSC): print('GAGAL: jsc tidak ditemukan'); return 1
    S = {'logika': open(MODUL, encoding='utf-8').read(), 'jual': baca('baru', 'js', 'layar', 'jual.js'), 'app': baca('baru', 'js', 'app.js')}
    if '--kontrol' in sys.argv:
        lolos = []
        for nama, berkas, lama, baru in MUTASI:
            if lama not in S[berkas]: print('KONTROL BASI: pola tidak ditemukan —', nama); lolos.append(nama); continue
            R = dict(S); R[berkas] = S[berkas].replace(lama, baru, 1)
            if periksa(R['logika'], R['jual'], R['app'], diam=True): lolos.append(nama); print('LOLOS (seharusnya gagal):', nama)
            else: print('  tertangkap:', nama)
        if not periksa(S['logika'], S['jual'], S['app'], diam=True): print('GAGAL: salinan utuh tidak lulus'); return 3
        print('KONTROL ' + ('LULUS' if not lolos else 'GAGAL') + ' ' + str(len(MUTASI) - len(lolos)) + '/' + str(len(MUTASI)))
        return 0 if not lolos else 3
    return 0 if periksa(S['logika'], S['jual'], S['app']) else 1


if __name__ == '__main__':
    sys.exit(main())
