#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_terima_barang.py — tanda terima barang masuk untuk supir pemasok (baru/js/layar/terima-barang-logika.js) dijalankan ASLI di jsc,
ditambah pemeriksaan pemasangannya di layar Stok (terima-barang-panel.js, stok.js, akses-layar.js, index.html).

Kenapa ada: owner 21 Nov 2026 — "ketika mencatat barang masuk ada surat terimanya? Guna bukti pembayaran toko tunai / bayar sebagian untuk
dikirim ke pemilik pemasok melalui supir pemasok." Lembar ini bukti uang di tangan orang lain: angka yang salah di kertas tidak bisa
ditarik lagi.

Yang dipegang:
  · NILAI NOTA = jumlah subtotal baris, TANPA upah bongkar; harga per kg dan subtotal per baris tidak tercetak
  · PEMBAYARAN: tunai = lunas; bon = belum / sebagian / lunas menurut angka buku yang diberikan; uang di atas nilai bon tidak ikut;
    rincian tanggal bayar dicetak hanya bila jumlahnya persis sama dengan yang dibayar
  · AKUN YANG TIDAK MEMBACA PEMBAYARAN PEMASOK (akun tablet) tidak pernah mencetak "sisa = nilai nota": baris Dibayar & Sisa dikosongkan
    untuk ditulis tangan
  · tiap baris tercetak muat di kertas 80 mm (48 kolom) dan 58 mm (32 kolom), ASCII saja, angka rupiah menempel di tepi kanan
  · dua lembar: LEMBAR PEMASOK dan LEMBAR TOKO; nomornya turunan id kedatangan (dicetak ulang = nomor sama); lembar memuat kapan dicetak
  · stok awal / saldo pembuka / buku baru / tanpa pemasok / tanpa baris tidak diberi tanda terima
  · owner 28 Nov 2026: CATATAN UNTUK PEMASOK yang ditulis toko ikut di kedua lembar & WhatsApp (tanpa "yang tertulis di nota" ber-harga per kg, tanpa
    usul yang belum disimpan); tombol cetak catatan terpisah dihapus; tiap baris bertanda `jenis` 'tt…' dan model gambarnya (struk-model.js
    stModelTandaTerima) memuat semua isi; printer tablet mencetak menurut gaya perangkat + logo toko (Bluetooth tetap teks); gambar tanda terima
    mengikuti pelajaran cetak CPad (semua teks bergores tepi, tanpa Jost 400)
  · pemasangan: panel tidak menulis apa pun; satu cetakan pada satu waktu; di aplikasi tablet tidak membuka dialog cetak; rupiah tidak
    tampil di layar akun bukan-owner; tombol akun tablet, lembar daftar, dan kartu sesudah Simpan terpasang di layar Stok

    python3 alat-uji/uji_terima_barang.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_terima_barang.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json, subprocess, tempfile

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
LOGIKA = 'baru/js/layar/terima-barang-logika.js'
PANEL = 'baru/js/layar/terima-barang-panel.js'
STOK = 'baru/js/layar/stok.js'
AKSES_LAYAR = 'baru/js/layar/akses-layar.js'
AKSES = 'baru/js/data/akses.js'
CATAT = 'baru/js/layar/stok-catat-logika.js'
INDEX = 'baru/index.html'
MODEL = 'baru/js/inti/struk-model.js'
KANVAS = 'baru/js/inti/struk-kanvas.js'
CSS = 'baru/css/jual.css'
RAKIT = ['baru/js/inti/format.js', 'baru/js/inti/escpos.js', MODEL, LOGIKA]   # urutan rakit di jsc: keempatnya tanpa impor selain satu sama lain
BERKAS = RAKIT + [PANEL, STOK, AKSES_LAYAR, AKSES, CATAT, INDEX, KANVAS, CSS]

PEMERIKSA = r"""
const hasil = [];
const cek = (nama, ok, ket) => hasil.push({ nama, ok: !!ok, ket: ket === undefined ? '' : (typeof ket === 'string' ? ket : JSON.stringify(ket)) });
const KOP = { nama: 'Toko Uji', alamat: 'Jl. Uji No. 1', telp: '0800' };
const CETAK = { tanggal: '2026-11-21', jam: '09:30', oleh: 'Uji' };
const kedatangan = (o) => Object.assign({ id: '1794292856829.1262', tanggal: '2026-11-09', jam: '13:40', pemasok: '  PT Uji Beras ', caraBayar: 'utang', biayaBongkar: 150000, merkList: [
  { id: '1', merk: 'Beras A', satuan: 'karung', jumlahKarung: 12, beratKarung: 50, totalKg: 600, hargaPerKg: 14000, subtotalHarga: 8400000 },
  { id: '2', merk: 'Beras B', merkPemasok: 'Cap B', satuan: 'karung', jumlahKarung: 1, beratKarung: 25, totalKg: 25, hargaPerKg: 16000, subtotalHarga: 400000 },
  { id: '3', merk: 'Kemasan C', bentuk: 'bal', jumlahBal: 3, totalKg: 30, subtotalHarga: 450000 }] }, o || {});
const NILAI = 9250000;
const teks = (d, kertas, lembar, dicetak) => epSusun(tbmGaris(d, KOP, lembar === undefined ? 'pemasok' : lembar, dicetak === undefined ? CETAK : dicetak), { kertas, potong: 'tidak', umpan: 0 }).teks;
const baris = (t, awal) => t.filter((s) => s.indexOf(awal) === 0);
const ujung = (t, awal, akhir, L) => { const b = baris(t, awal); return b.length === 1 && b[0].length === L && b[0].slice(-akhir.length) === akhir; };

// ---------- yang tidak diberi tanda terima ----------
cek('tolak: kedatangan tidak ada', tbmTolak(null) !== '');
cek('tolak: stok awal', tbmTolak(kedatangan({ stokAwal: true })) !== '');
cek('tolak: saldo pembuka tutup buku', tbmTolak(kedatangan({ tutupBuku: true })) !== '');
cek('tolak: buku baru 0 kg', tbmTolak(kedatangan({ lahirBuku: true })) !== '');
cek('tolak: tanpa nama pemasok', tbmTolak(kedatangan({ pemasok: '   ' })) !== '');
cek('tolak: tanpa baris barang', tbmTolak(kedatangan({ merkList: [] })) !== '');
cek('kedatangan biasa: boleh', tbmTolak(kedatangan()) === '', tbmTolak(kedatangan()));

// ---------- nomor ----------
cek('nomor: TT-<tanggal>-<4 angka terakhir id>', tbmNomor(kedatangan()) === 'TT-261109-1262', tbmNomor(kedatangan()));
cek('nomor: id berupa angka (bukan teks) sama hasilnya', tbmNomor(kedatangan({ id: 1794292856829.1262 })) === 'TT-261109-1262', tbmNomor(kedatangan({ id: 1794292856829.1262 })));
cek('nomor: dicetak ulang = nomor sama', tbmNomor(kedatangan()) === tbmNomor(kedatangan()));
cek('nomor: tanpa tanggal & id tetap berbentuk', tbmNomor({}) === 'TT-000000-0000', tbmNomor({}));

// ---------- isi ----------
const sebelum = JSON.stringify(kedatangan());
const asal = kedatangan(); const dTunai = tbmData(kedatangan({ caraBayar: 'tunai' }), { terbaca: true, dibayar: 0, rinci: [] });
tbmData(asal, { terbaca: true, dibayar: 1, rinci: [] });
cek('kedatangan tidak diubah oleh penyusun', JSON.stringify(asal) === sebelum);
cek('nilai nota = jumlah subtotal baris, TANPA upah bongkar', dTunai.nilai === NILAI, dTunai.nilai);
cek('jumlah: 13 karung, 3 bal, 655 kg (baris bal bukan karung)', dTunai.jumlah.karung === 13 && dTunai.jumlah.bal === 3 && dTunai.jumlah.kg === 655, dTunai.jumlah);
cek('nama pemasok dirapikan', dTunai.pemasok === 'PT Uji Beras', dTunai.pemasok);
cek('tunai: lunas saat datang', dTunai.bayar.keadaan === 'tunai' && dTunai.bayar.dibayar === NILAI && dTunai.bayar.sisa === 0 && dTunai.bon === false, dTunai.bayar);
const dTunaiTablet = tbmData(kedatangan({ caraBayar: 'tunai' }), { terbaca: false });
cek('tunai di akun yang tidak membaca pembayaran: tetap tunai (terbaca dari kedatangannya sendiri)', dTunaiTablet.bayar.keadaan === 'tunai' && dTunaiTablet.bayar.sisa === 0, dTunaiTablet.bayar);
const dBelum = tbmData(kedatangan(), { terbaca: true, dibayar: 0, rinci: [] });
cek('bon belum dibayar: sisa = nilai nota', dBelum.bayar.keadaan === 'belum' && dBelum.bayar.dibayar === 0 && dBelum.bayar.sisa === NILAI && dBelum.bon === true, dBelum.bayar);
const dSebagian = tbmData(kedatangan(), { terbaca: true, dibayar: 4000000, rinci: [{ tanggal: '2026-11-10', nominal: 4000000 }] });
cek('bon dibayar sebagian: sisa = nilai − dibayar, rincian ikut', dSebagian.bayar.keadaan === 'sebagian' && dSebagian.bayar.dibayar === 4000000 && dSebagian.bayar.sisa === 5250000 && dSebagian.bayar.rinci.length === 1, dSebagian.bayar);
const dDua = tbmData(kedatangan(), { terbaca: true, dibayar: 4000000, rinci: [{ tanggal: '2026-11-10', nominal: 1500000 }, { tanggal: '2026-11-12', nominal: 2500000 }] });
cek('bon dicicil dua kali: dua rincian', dDua.bayar.rinci.length === 2 && dDua.bayar.sisa === 5250000, dDua.bayar);
const dTakCocok = tbmData(kedatangan(), { terbaca: true, dibayar: 4000000, rinci: [{ tanggal: '2026-11-10', nominal: 1500000 }] });
cek('rincian yang jumlahnya TIDAK sama dengan yang dibayar tidak dipakai', dTakCocok.bayar.rinci.length === 0 && dTakCocok.bayar.dibayar === 4000000 && dTakCocok.bayar.sisa === 5250000, dTakCocok.bayar);
const dLunas = tbmData(kedatangan(), { terbaca: true, dibayar: NILAI + 700000, rinci: [] });
cek('bon lunas: uang di atas nilai bon tidak ikut lembar ini', dLunas.bayar.keadaan === 'lunas' && dLunas.bayar.dibayar === NILAI && dLunas.bayar.sisa === 0, dLunas.bayar);
const dMinus = tbmData(kedatangan(), { terbaca: true, dibayar: -5, rinci: [] });
cek('angka bayar minus dianggap belum dibayar', dMinus.bayar.keadaan === 'belum' && dMinus.bayar.dibayar === 0 && dMinus.bayar.sisa === NILAI, dMinus.bayar);
const dTablet = tbmData(kedatangan(), { terbaca: false, dibayar: 0, rinci: [] });
cek('bon di akun yang TIDAK membaca pembayaran: keadaan "takTerbaca", bukan nol', dTablet.bayar.keadaan === 'takTerbaca' && dTablet.bayar.dibayar === null && dTablet.bayar.sisa === null, dTablet.bayar);
cek('tanpa keterangan bayar sama sekali = tidak terbaca', tbmData(kedatangan()).bayar.keadaan === 'takTerbaca');
cek('kalimat layar: lima keadaan berbeda', new Set([dTunai, dBelum, dSebagian, dLunas, dTablet].map(tbmKalimatBayar)).size === 5, [dTunai, dBelum, dSebagian, dLunas, dTablet].map(tbmKalimatBayar));
cek('kalimat layar bon sebagian menyebut dibayar & sisa', /Rp4\.000\.000/.test(tbmKalimatBayar(dSebagian)) && /Rp5\.250\.000/.test(tbmKalimatBayar(dSebagian)), tbmKalimatBayar(dSebagian));

// ---------- kertas ----------
const ascii = (s) => /^[\x20-\x7e]*$/.test(s);
[80, 58].forEach((k) => {
  const L = EP_KOLOM[k];
  [['tunai', dTunai], ['belum', dBelum], ['sebagian', dSebagian], ['dua cicilan', dDua], ['lunas', dLunas], ['tak terbaca', dTablet]].forEach(([nm, d]) => {
    ['pemasok', 'toko', ''].forEach((lb) => { const t = teks(d, k, lb);
      const lewat = t.filter((s) => s.length > L); const bukan = t.filter((s) => !ascii(s));
      cek(k + ' mm · ' + nm + ' · lembar ' + (lb || 'WhatsApp') + ': tiap baris ≤ ' + L + ' kolom & ASCII', lewat.length === 0 && bukan.length === 0, lewat.concat(bukan)); });
  });
  const t = teks(dBelum, k);
  cek(k + ' mm: judul, nomor, nama lembar', t.some((s) => s.trim() === 'TANDA TERIMA BARANG') && t.some((s) => s.trim() === 'No. TT-261109-1262') && t.some((s) => s.trim() === 'LEMBAR PEMASOK'), t.slice(0, 9));
  cek(k + ' mm: kop toko di atas', t[0].trim() === 'TOKO UJI' && t.some((s) => s.trim() === 'Telp 0800'), t.slice(0, 3));
  cek(k + ' mm: tanggal datang & nama pemasok', baris(t, 'Datang: 9 Nov 2026 13:40').length === 1 && baris(t, 'Dari: PT Uji Beras').length === 1, t.slice(8, 11));
  cek(k + ' mm: nilai nota menempel di tepi kanan', ujung(t, 'Nilai nota', 'Rp9.250.000', L), baris(t, 'Nilai nota'));
  cek(k + ' mm: baris JUMLAH', t.some((s) => /13 karung, 3 bal, 655 kg$/.test(s)), t.filter((s) => /karung/.test(s)));
  cek(k + ' mm: baris karung "12 x 50 = 600 kg" & merek pemasok dalam kurung', t.some((s) => /12 x 50 = 600 kg$/.test(s)) && t.some((s) => /^Beras B \(Cap B\)/.test(s)) && t.some((s) => /1 x 25 = 25 kg$/.test(s)), t.filter((s) => / x /.test(s)));
  cek(k + ' mm: baris bal "3 bal = 30 kg"', t.some((s) => /3 bal = 30 kg$/.test(s)), t.filter((s) => /bal/.test(s)));
  const semua = t.join('\n');
  cek(k + ' mm: harga per kg, subtotal per baris & upah bongkar TIDAK tercetak', !/14\.?000|16\.?000|8\.400\.000|400\.000\b(?!\.)|450\.000|150\.000|9\.400\.000/.test(semua.replace(/Rp9\.250\.000/g, '')), semua.match(/[0-9.]{6,}/g));
  cek(k + ' mm: dua kolom tanda tangan', t.some((s) => /^Diterima toko,\s+Supir \/ pengirim,$/.test(s)) && t.some((s) => /^\(\.+\)\s+\(\.+\)$/.test(s)), t.slice(-8));
  cek(k + ' mm: kapan lembar dicetak', t.join(' ').replace(/\s+/g, ' ').indexOf('Keadaan per 21 Nov 2026 09:30, dicetak Uji') >= 0, t.filter((s) => /Keadaan|dicetak/.test(s)));
  cek(k + ' mm: tanpa keterangan cetak, baris "Keadaan per" tidak ada', !teks(dBelum, k, 'pemasok', null).some((s) => /Keadaan per/.test(s)));
  // tunai
  const tt = teks(dTunai, k);
  cek(k + ' mm · tunai: TUNAI, DIBAYAR = nilai nota, LUNAS', ujung(tt, 'Cara bayar', 'TUNAI', L) && ujung(tt, 'DIBAYAR', 'Rp9.250.000', L) && ujung(tt, 'Sisa', 'LUNAS', L) && !tt.some((s) => /BON/.test(s)), tt.filter((s) => /bayar|DIBAYAR|Sisa|BON/.test(s)));
  // bon belum dibayar
  cek(k + ' mm · bon belum dibayar: Sudah dibayar Rp0, SISA BON = nilai nota', ujung(t, 'Cara bayar', 'BON', L) && ujung(t, 'Sudah dibayar', 'Rp0', L) && ujung(t, 'SISA BON', 'Rp9.250.000', L), t.filter((s) => /bayar|SISA/.test(s)));
  // bon sebagian
  const ts = teks(dSebagian, k);
  cek(k + ' mm · bon sebagian (satu pembayaran): tanggal bayar + SISA BON, tanpa baris jumlah ganda', ts.some((s) => /BON, dibayar sebagian$/.test(s)) && ujung(ts, 'Bayar 10 Nov 2026', 'Rp4.000.000', L) && ujung(ts, 'SISA BON', 'Rp5.250.000', L) && baris(ts, 'Sudah dibayar').length === 0, ts.filter((s) => /ayar|SISA/.test(s)));
  const td = teks(dDua, k);
  cek(k + ' mm · bon dicicil dua kali: dua tanggal + jumlahnya + SISA BON', ujung(td, 'Bayar 10 Nov 2026', 'Rp1.500.000', L) && ujung(td, 'Bayar 12 Nov 2026', 'Rp2.500.000', L) && ujung(td, 'Sudah dibayar', 'Rp4.000.000', L) && ujung(td, 'SISA BON', 'Rp5.250.000', L), td.filter((s) => /ayar|SISA/.test(s)));
  const tc = teks(dTakCocok, k);
  cek(k + ' mm · rincian tidak cocok: hanya jumlahnya, tanpa tanggal', baris(tc, 'Bayar ').length === 0 && ujung(tc, 'Sudah dibayar', 'Rp4.000.000', L) && ujung(tc, 'SISA BON', 'Rp5.250.000', L), tc.filter((s) => /ayar|SISA/.test(s)));
  const tl = teks(dLunas, k);
  cek(k + ' mm · bon lunas: SISA BON LUNAS', ujung(tl, 'SISA BON', 'LUNAS', L) && ujung(tl, 'Sudah dibayar', 'Rp9.250.000', L), tl.filter((s) => /ayar|SISA/.test(s)));
  // akun yang tidak membaca pembayaran
  const tb = teks(dTablet, k); const bayarTb = tb.slice(tb.findIndex((s) => /^Cara bayar/.test(s)));
  cek(k + ' mm · pembayaran tidak terbaca: Dibayar & Sisa titik-titik untuk ditulis tangan', ujung(tb, 'Dibayar: Rp', '..................', L) && ujung(tb, 'Sisa: Rp', '..................', L) && /ditulis tangan/.test(tb.join(' ')), bayarTb.slice(0, 6));
  cek(k + ' mm · pembayaran tidak terbaca: TIDAK ada "SISA BON", "Sudah dibayar", atau rupiah di bagian bayar', !bayarTb.some((s) => /SISA BON|Sudah dibayar|Rp[0-9]|LUNAS/.test(s)), bayarTb.slice(0, 6));
});

// ---------- dua lembar ----------
const lembar = tbmLembar(dSebagian, KOP, CETAK);
const tl1 = epSusun(lembar[0], { kertas: 80 }).teks; const tl2 = epSusun(lembar[1], { kertas: 80 }).teks;
cek('dua lembar: pemasok dulu, lalu toko', lembar.length === 2 && tl1.some((s) => s.trim() === 'LEMBAR PEMASOK') && tl2.some((s) => s.trim() === 'LEMBAR TOKO'));
cek('lembar pemasok: untuk pemilik pemasok', /Dibawa supir untuk pemilik PT Uji Beras\./.test(tl1.join(' ').replace(/\s+/g, ' ')) && !tl1.some((s) => /Arsip toko/.test(s)));
cek('lembar toko: tempat nama terang supir & jam, arsip toko', tl2.some((s) => /^Nama terang supir dan jam:/.test(s)) && tl2.some((s) => s.trim() === 'Arsip toko.') && !tl2.some((s) => /Dibawa supir/.test(s)));
cek('dua lembar memuat angka yang sama', ['Nilai nota', 'SISA BON', 'Bayar 10 Nov 2026'].every((a) => baris(tl1, a).join() === baris(tl2, a).join() && baris(tl1, a).length === 1));
const tw = teks(dSebagian, 58, '');
cek('WhatsApp: tanpa nama lembar', !tw.some((s) => /LEMBAR|Arsip toko|Dibawa supir/.test(s)) && tw.some((s) => /SISA BON/.test(s)));

// ---------- owner 28 Nov 2026: CATATAN UNTUK PEMASOK di kedua lembar (isi = cpIsiSurat; di sini bentuk yang sama, dibuat tangan) ----------
const SURAT = { ada: true, sub: 'PT Uji Beras · barang datang 10 Nov 2026 · bon', identitas: 'Dibuat dari catatan Barang masuk toko. Mohon dikonfirmasi.', baris: [
  { nama: 'Yang tertulis di nota', n: '', kelas: 'kel' }, { nama: 'Angsa · 2000 kg @ Rp13.000/kg', n: 26000000, kelas: '' }, { nama: '   ditimbang 1987,5 kg — KURANG 12,5 kg', n: '', kelas: '' },
  { nama: 'Catatan toko', n: '', kelas: 'kel' }, { nama: 'Kurang · Angsa · 12,5 kg — hasil timbang', n: '', kelas: '' }, { nama: 'Mutu · Angsa — 2 karung sobek, minta diganti di kiriman berikut', n: '', kelas: '' },
  { nama: 'Sudah dibukukan toko', n: '', kelas: 'kel' }, { nama: '10 Nov 2026 · dipotong saat datang (kurang timbang) · 12,5 kg', n: -162500, kelas: '' },
  { nama: 'Catatan', n: '', kelas: 'kel' }, { nama: 'Total selisih susut keseluruhan 15,4 kg', n: '', kelas: '' },
  { nama: 'Permintaan toko', n: '', kelas: 'kel' }, { nama: 'Minta dipotong / uang kembali', n: 162500, kelas: 'jumlah' }] };
const CAT = tbmCatatan(SURAT);
cek('catatan: empat kelompok yang DITULIS toko, tanpa "yang tertulis di nota" (harga per kg)', CAT.length === 4 && CAT.map((k) => k.judul).join('|') === 'Catatan toko|Sudah dibukukan toko|Catatan|Permintaan toko', CAT.map((k) => k.judul));
cek('catatan: baris & angka dibawa apa adanya (potongan minus, permintaan tebal)', CAT[0].baris.length === 2 && CAT[1].baris[0].n === -162500 && CAT[3].baris[0].n === 162500 && CAT[3].baris[0].tebal === true && CAT[0].baris[0].n === '', CAT);
cek('catatan: kedatangan tanpa catatan tersimpan (hanya usul dari timbang) = tidak ada catatan', tbmCatatan(Object.assign({}, SURAT, { ada: false })).length === 0 && tbmCatatan(null).length === 0);
const dCat = tbmData(kedatangan(), { terbaca: true, dibayar: 0, rinci: [] }, CAT);
[80, 58].forEach((k) => { const L = EP_KOLOM[k];
  ['pemasok', 'toko', ''].forEach((lb) => { const t = teks(dCat, k, lb); const gab = t.join(' ').replace(/\s+/g, ' ');
    cek(k + ' mm · lembar ' + (lb || 'WhatsApp') + ': catatan ikut, ≤ ' + L + ' kolom & ASCII', t.some((s) => s.trim() === 'CATATAN UNTUK PEMASOK') && t.some((s) => s.trim() === 'CATATAN TOKO') && t.some((s) => s.trim() === 'PERMINTAAN TOKO')
      && /Kurang - Angsa - 12,5 kg/.test(gab) && /Total selisih susut keseluruhan 15,4 kg/.test(gab) && t.every((s) => s.length <= L && ascii(s)), t.filter((s) => s.length > L || !ascii(s)));
    cek(k + ' mm · lembar ' + (lb || 'WhatsApp') + ': potongan bertanda minus, permintaan di kanan, harga per kg nota TIDAK ikut', t.some((s) => /-Rp162\.500$/.test(s)) && t.some((s) => /Rp162\.500$/.test(s) && !/-Rp/.test(s)) && !/@ Rp|Rp13\.000|YANG TERTULIS DI NOTA|26\.000\.000/.test(gab), t.filter((s) => /Rp/.test(s)));
    const iC = t.findIndex((s) => s.trim() === 'CATATAN UNTUK PEMASOK'); const iT = t.findIndex((s) => /^Diterima toko,/.test(s)); const iK = t.findIndex((s) => /^Keadaan per/.test(s));
    cek(k + ' mm · lembar ' + (lb || 'WhatsApp') + ': catatan sesudah pembayaran, sebelum tanda tangan', iK >= 0 && iK < iC && iC < iT, [iK, iC, iT]); }); });
cek('tanpa catatan: lembar tanpa bagian catatan', !teks(dBelum, 80).some((s) => /CATATAN UNTUK PEMASOK/.test(s)) && Array.isArray(dBelum.catatan) && dBelum.catatan.length === 0);
const lC = tbmLembar(dCat, KOP, CETAK).map((g) => epSusun(g, { kertas: 80 }).teks);
const isiCat = (t) => t.filter((s) => /Kurang|Mutu|Total selisih|Minta dipotong|-Rp162\.500/.test(s)).join('|');
cek('dua lembar memuat catatan yang sama', isiCat(lC[0]) === isiCat(lC[1]) && lC[0].some((s) => /Minta dipotong/.test(s)));

// ---------- owner 28 Nov 2026: gaya gambar berlogo — tiap baris bertanda, model memuat semua isi ----------
const gP = tbmGaris(dCat, KOP, 'pemasok', CETAK); const gT = tbmGaris(dSebagian, KOP, 'toko', CETAK);
cek('gambar: tiap baris tanda terima bertanda jenis tt… (tidak ada isi yang hilang di gaya gambar)', gP.concat(gT).every((g) => g.garis || /^tt[A-Z]/.test(g.jenis || '')), gP.concat(gT).filter((g) => !g.garis && !/^tt[A-Z]/.test(g.jenis || '')));
cek('gambar: garis tanda terima dikenali, garis nota (jenis kop) tidak', stAdaTandaTerima(gP) && !stAdaTandaTerima([{ kiri: 'TOKO', jenis: 'kop' }, { kiri: 'Pembeli', jenis: 'pembeli' }]) && !stAdaTandaTerima([{ kiri: 'polos' }]));
const MP = stModelTandaTerima(gP); const MT = stModelTandaTerima(gT);
cek('model: kop, judul, nomor, lembar, datang, dari', MP.kop === 'TOKO UJI' && MP.judul === 'TANDA TERIMA BARANG' && MP.no === 'TT-261109-1262' && MP.lembar === 'pemasok' && MT.lembar === 'toko' && MP.datang === '9 Nov 2026 13:40' && MP.dari === 'PT Uji Beras', MP);
cek('model: tiga baris barang (rinci karung × isi, kg), bal tanpa isi', MP.barang.length === 3 && MP.barang[0].nama === 'Beras A' && MP.barang[0].rinci === '12 karung × 50 kg' && MP.barang[0].kg === '600 kg' && MP.barang[1].nama === 'Beras B (Cap B)' && MP.barang[2].rinci === '3 bal' && MP.barang[2].kg === '30 kg', MP.barang);
cek('model: jumlah & nilai nota sama dengan gaya teks', MP.jumlah === '13 karung, 3 bal, 655 kg' && MP.nilai === 'Rp9.250.000', [MP.jumlah, MP.nilai]);
cek('model: pembayaran sama dengan gaya teks (bon sebagian: tanggal bayar + SISA BON)', MT.bayar.map((b) => b.label + '=' + b.n).join('|') === 'Cara bayar=BON, dibayar sebagian|Bayar 10 Nov 2026=Rp4.000.000|SISA BON=Rp5.250.000' && MT.bayar[2].tebal === true, MT.bayar);
cek('model: catatan empat kelompok, baris & angka', MP.catatan.length === 4 && MP.catatan[0].judul === 'CATATAN TOKO' && MP.catatan[0].baris.length === 2 && MP.catatan[1].baris[0].n === '-Rp162.500' && MP.catatan[3].baris[0].n === 'Rp162.500' && MP.catatan[3].baris[0].tebal, MP.catatan);
cek('model: tanda tangan dua pihak, nama supir hanya lembar toko, kaki', !!MP.ttd && MP.ttd.kiri === 'Diterima toko,' && MP.ttd.kanan === 'Supir / pengirim,' && !MP.namaSupir && MT.namaSupir && MP.kaki === 'Dibawa supir untuk pemilik PT Uji Beras.' && MT.kaki === 'Arsip toko.', [MP.ttd, MP.kaki, MT.kaki]);
const MTb = stModelTandaTerima(tbmGaris(dTablet, KOP, 'pemasok', CETAK));
cek('model: kapan dicetak & isian tulis tangan ikut', MP.keadaan === 'Keadaan per 21 Nov 2026 09:30, dicetak Uji' && MTb.bayar.some((b) => /^\.+$/.test(b.n)) && MTb.bayarKet.length === 1, [MP.keadaan, MTb.bayar, MTb.bayarKet]);
const g6 = tbmGaris(tbmData(kedatangan({ merkList: [{ id: '1', merk: 'Beras A', satuan: 'karung', jumlahKarung: 12, beratKarung: 50, totalKg: 597.6, kgTerima: 597.6, hargaPerKg: 14000, subtotalHarga: 8400000 }] }), { terbaca: true, dibayar: 0 }), KOP, 'toko', CETAK);
cek('model Tahap 6: kg nota di baris barang, hasil timbang di bawahnya', (() => { const B = stModelTandaTerima(g6).barang[0]; return B.kg === '600 kg' && B.timbang === '597,6 kg'; })(), stModelTandaTerima(g6).barang);
cek('model: kop "TOKO BERAS M.IQBAL" dipecah seperti nota', (() => { const M = stModelTandaTerima(tbmGaris(dBelum, { nama: 'Toko Beras M.IQBAL' }, 'pemasok', CETAK)); return M.kopBesar === 'M.IQBAL' && M.kopKecil === 'TOKO BERAS'; })());

// ---------- Tahap 6 (owner 25 Nov 2026): stok ikut timbang — kg nota & kg yang dibukukan sama-sama tertulis; uang tetap dari nota ----------
const dT6 = tbmData(kedatangan({ merkList: [{ id: '1', merk: 'Beras A', satuan: 'karung', jumlahKarung: 12, beratKarung: 50, totalKg: 597.6, kgTerima: 597.6, sampelKarung: 2, sampelKg: 99.6, hargaPerKg: 14000, subtotalHarga: 8400000 }] }), { terbaca: true, dibayar: 0, rinci: [] });
const tT6 = teks(dT6, 58);
cek('Tahap 6 tanda terima: baris ikut timbang = "12 x 50 = 600 kg" (nota) + "hasil timbang (dibukukan) 597,6 kg"; nilai nota tetap Rp8.400.000; jumlah = kg yang dibukukan',
  dT6.baris[0].ikut === true && dT6.baris[0].kgNota === 600 && dT6.baris[0].kg === 597.6 && dT6.nilai === 8400000 && dT6.jumlah.kg === 597.6 && /12 x 50 = 600 kg/.test(tT6) && /hasil timbang \(dibukukan\)/.test(tT6) && /597,6 kg/.test(tT6), tT6);
cek('Tahap 6 tanda terima: kedatangan lama (tanpa kgTerima) tidak berubah — tanpa baris "hasil timbang"', !/hasil timbang/.test(teks(tbmData(kedatangan(), { terbaca: true, dibayar: 0, rinci: [] }), 58)) && tbmData(kedatangan(), { terbaca: true }).baris[0].ikut === false);
print(JSON.stringify(hasil));
"""


def baca_semua():
    return {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in BERKAS}


def rakit(t):
    # tiga modul tanpa impor luar → buang baris impor & kata `export`, jalan sebagai satu skrip di jsc
    bagian = []
    for b in RAKIT:
        s = re.sub(r"^import\s[^;]*;.*$", '', t[b], flags=re.M)
        bagian.append(s.replace('export const ', 'const ').replace('export function ', 'function '))
    return '\n'.join(bagian)


def jalankan(t):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(rakit(t) + '\n' + PEMERIKSA); p = f.name
    try:
        r = subprocess.run([JSC, p], capture_output=True, text=True)
    finally:
        os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip():
        return None, (r.stderr or r.stdout).strip()
    return json.loads(r.stdout.strip().splitlines()[-1]), ''


def periksa_statis(t):
    """Pemasangan di layar: siapa membaca apa, apa yang tampil, dan bagaimana lembarnya dikirim ke printer."""
    h = []
    def ok(nama, benar, ket=''): h.append({'nama': 'statis: ' + nama, 'ok': bool(benar), 'ket': ket})
    lg, pn, st, al, ak, ct, ix = t[LOGIKA], t[PANEL], t[STOK], t[AKSES_LAYAR], t[AKSES], t[CATAT], t[INDEX]
    ok('logika hanya mengimpor format (tanpa data toko, tanpa penulis)', re.findall(r"^import\s[^;]*;", lg, flags=re.M) == ["import { RP, KG, DESIMAL, tanggalPendek } from '../inti/format.js';"])
    ok('panel TIDAK menulis ke buku (tanpa tulisDokumen / hapusDokumen / tulisBertahap)', not re.search(r'tulisDokumen|hapusDokumen|tulisBertahap|\btulis\(', pn))
    ok('pembayaran pemasok dibaca hanya bila akun ini membacanya', "const KOLEKSI_BAYAR = 'utangPemasokMutasi';" in pn and "const terbaca = akunMembaca(akun, KOLEKSI_BAYAR); const bb = terbaca ? C.ckBayarBon(batch) : null;" in pn)
    ok('angka "sudah dibayar" = angka buku utang pemasok (mesin), bukan hitungan sendiri', "TBM.tbmData(batch, { terbaca, dibayar: bb ? bb.dibayarMesin : 0, rinci: bb ? bb.bayar : [], titipSupir: titipSupir(batch, terbaca) }, TBM.tbmCatatan(" in pn)
    ok('akunMembaca: owner ya; selain owner hanya koleksi yang dibuka server', "export const akunMembaca = (akun, koleksi) => !bukanOwner(akun) || BACA_STAF.indexOf(koleksi) >= 0;" in al)
    m = re.search(r"export const BACA_STAF = \[(.*?)\];", ak, flags=re.S)
    ok('pembayaran pemasok memang belum dibuka untuk akun bukan-owner (kalau dibuka: lembar tablet otomatis memuat angkanya — perbarui uji ini)', bool(m) and 'utangPemasokMutasi' not in m.group(1))
    ok('kedatangan diambil dari buku yang sama dengan Buku kedatangan', "export const batchKedatangan = (id) => ambilSemuaBatch().find((b) => String(b.id) === String(id)) || null;" in ct)
    ok('rupiah tidak tampil di layar akun bukan-owner (di kertasnya tetap ada)', "(staf ? (d.bon ? 'bon' : 'tunai') : 'nilai nota ' + RP(d.nilai) + ' · ' + TBM.tbmKalimatBayar(d))" in pn and "const staf = bukanOwner(o.akun)" in pn)
    ok('kartu berkata terus terang bila angka bayar tidak terbaca', "d.bayar.keadaan === 'takTerbaca' ? h`<div class=\"ket awas-teks\" data-k=\"tbm-tangan\">" in pn)
    ok('daftar akun tablet tanpa rupiah & tanpa batch fondasi', "C.daftarKedatangan(12).filter((k) => !k.fondasi && k.pemasok && k.pemasok !== '—')" in pn and 'RP(k.' not in pn)
    ok('keadaan kosong daftar punya kalimat', 'data-k="tbm-kosong"' in pn)
    a, z = pn.find('function kirim(lembar, T)'), pn.find('function wa(id'); cetak = pn[a:z] if 0 <= a < z else ''
    def urut(*pola):
        # semua pola ada, dan muncul berurutan — salinan yang dirusak tidak boleh menjatuhkan alat uji
        letak = [cetak.find(x) for x in pola]
        return all(i >= 0 for i in letak) and letak == sorted(letak)
    ok('satu cetakan pada satu waktu: printer sibuk → tidak ada yang dikirim', urut('if (printerSibuk()) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });', 'PR.jalurCetak()'))
    ok('dicetak menurut gaya printer perangkat + logo toko, Bluetooth tetap teks, dua lembar berurutan', "const timpa = j === 'sunmi-bt' ? { gaya: 'teks' } : null;" in cetak and "lembar.reduce((p, g) => p.then(() => PR.susunCetak(g, timpa, { qr: '', logoToko: pakaiLogo() })).then((x) => PR.kirimCetak(x.byte, j)).then(() => { n += 1; }), Promise.resolve())" in cetak and 'TBM.tbmLembar(d, ST.stAtur().kop' in pn and "kirim(lembarCetak(r.d), { nama: 'Tanda terima'," in pn)
    ok('printer diam sesudah data dikirim = "lihat kertasnya", sebelum cabang gagal & tanpa kirim ulang', urut('if (masihMencetak(e)) return set(', 'if (hasilTakDiketahui(e)) return set(', "const gagal = PR.sebutPrinter(j)"))
    ok('di aplikasi tablet dialog cetak tidak dibuka: kabarnya menyebut lembar TIDAK tercetak', "const dialog = () => { if (asliAda()) return set({ kabar: T.nama + ' TIDAK tercetak: di tablet ini hanya keluar lewat printer tablet" in cetak and "if (asliAda()) return set({ kabar: gagal + T.nama.toLowerCase() + ' TIDAK tercetak'" in cetak)
    ok('tombol WhatsApp tidak tampil di aplikasi tablet', "${asliAda() ? '' : h`<div class=\"kaca-btn\" data-aksi=\"tbmWa\" data-id=\"${id}\">WhatsApp</div>`}" in pn)
    ok('lembar memuat kapan & oleh siapa dicetak', "{ tanggal: w.tanggal, jam: w.jam, oleh: (a && a.nama) || '' }" in pn)
    # owner 28 Nov 2026: catatan untuk pemasok ikut kedua lembar; tombol cetak catatan terpisah DIHAPUS; gambar berlogo
    ok('catatan pemasok: tombol & aksi cetak catatan terpisah sudah tidak ada (cukup lewat Dokumen kecil)', 'CETAK CATATAN PEMASOK' not in pn and 'data-aksi="tbmCatatan' not in pn and 'tbmCatatan:' not in pn and 'cetakCatatan' not in pn and 'tbmGarisCatatan' not in pn and 'tbmGarisCatatan' not in lg and 'CETAK CATATAN PEMASOK' not in st)
    ok('catatan pemasok: isinya dari penyusun surat yang sama dengan Dokumen kecil, diteruskan ke tanda terima', "TBM.tbmCatatan(C.cpIsiSurat(id))) };" in pn and 'cpKedatangan(' not in pn and "export function cpIsiSurat(id, atur) {" in ct)
    ok('catatan pemasok: kartu menyebut catatan yang ikut tercetak', '${sebutCatatan(d)}' in pn and 'data-k="tbm-catatan"' in pn)
    ok('catatan pemasok: lembar Barang masuk tidak lagi menyebut tombol lama', 'ikut tercetak di kedua lembar tanda terima (CETAK 2 LEMBAR)' in st)
    ok('logo toko ikut menurut setelan struk (Jual › Struk › Sertakan logo)', "const pakaiLogo = () => { const A = ST.stAtur(); return !(A.sertakan && A.sertakan.logo === false); };" in pn)
    ok('dialog cetak gaya gambar memuat gambar lembar yang sama, gaya teks tetap teks', "if (PR.prAtur().gaya === 'teks') return teks();" in pn and "im.src = gambarStruk(g, { kertas, logoToko: pakaiLogo() }).kanvas.toDataURL('image/png');" in pn and '#cetakStruk.gambar img {' in t[CSS])
    kv = t[KANVAS]
    ok('kanvas: garis tanda terima digambar gaya tanda terima SEBELUM pemeriksaan gaya Sertifikat', kv.find('if (stAdaTandaTerima(garis)) return gambarTandaTerima(garis, opsi);') >= 0 and kv.find('if (stAdaTandaTerima(garis)) return gambarTandaTerima(garis, opsi);') < kv.find('return gambarSertifikat(garis, opsi);'))
    a0 = kv.find('function gambarTandaTerima('); a1 = kv.find('\n}\n', a0); gt = kv[a0:a1] if 0 <= a0 < a1 else ''
    ok('kanvas tanda terima: semua teks lewat isiHuruf (isi + gores tepi stTebalHuruf) — garis rambut tidak hilang di printer', gt.count('c.fillText(') == 1 and 'const isiHuruf = (t, x, yb, tb) => { c.fillText(t, x, yb); if (tb) {' in gt and 'const tb = stTebalHuruf(f, k);' in gt and 'strokeText' in gt)
    ok('kanvas tanda terima: tanpa Jost 400 (pudar di printer panas), label Cinzel 700, logo toko', bool(gt) and not __import__('re').search(r'F_SANS\([^,]*\b400\s*,', gt) and 'const F_LABEL = F_CIN(700' in gt and 'gambarLogoToko(c, cx, y,' in gt and 'jadiBit(kanvas, c, W, y)' in gt)
    # layar Stok
    ok('stok.js memasang panel', "import { kartuTerima, lembarTerima, aksiPanelTerima } from './terima-barang-panel.js';" in st and 'aksiPanelTerima({ set, akun: opsi.akun, waktu }));' in st)
    ok('keadaan awal punya tbm (ganti orang = kartu tertutup)', re.search(r"\n    tbm: null \}\);\n  const K = buatKeadaan\(awal\(\)\);", st) is not None)
    ok('akun bukan-owner punya tombol "Tanda terima barang masuk" di Stok', "${bukanOwner(ak) ? h`<div class=\"kaca-btn\" data-k=\"tombol-terima\" data-aksi=\"bukaTerima\">Tanda terima barang masuk</div>` : ''}" in st)
    ok('lembar daftar terpasang di pemilih lembar', "s.lembar === 'terima' ? lembarTerima(s, { akun: opsi.akun ? opsi.akun() : null, bawah: gambarUsulTablet(s) })" in st)
    ok('lembar Barang masuk: kartu kedatangan yang dikoreksi, atau yang baru tersimpan', "${koreksi ? kartuTerima(d.id, { akun: opsi.akun ? opsi.akun() : null }) : s.tbm ? kartuTerima(s.tbm.id, { akun: opsi.akun ? opsi.akun() : null, tutup: true }) : ''}" in st)
    ok('sesudah Simpan: kartu kedatangan yang baru tersimpan dibuka', "const dm = (r.dokumen || []).find((x) => x.koleksi === 'batchMasuk'); const idT = dm && dm.data ? dm.data.id : null;" in st and "tbm: idT !== null && idT !== undefined ? { id: String(idT) } : null });" in st)
    ok('tutup lembar / buka lembar / batal koreksi / koreksi menutup kartu lama', all(x in st for x in ["yakinHapusA: false, bukaA: null, tbm: null }),", "kabar: '', aturC: null, tbm: null }),", "yakinHapus: false, kabar: '', tbm: null }); },", "set({ masuk: d, yakinM: false, yakinHapus: false, tbm: null, kabar:"]))
    ok('modul dimuat lebih dulu (modulepreload)', '<link rel="modulepreload" href="js/layar/terima-barang-logika.js">' in ix and '<link rel="modulepreload" href="js/layar/terima-barang-panel.js">' in ix)
    return h


def periksa(t, diam=False):
    h, galat = jalankan(t)
    if h is None:
        if not diam: print('GAGAL: jsc tidak jalan —', galat[:600])
        return False
    h = h + periksa_statis(t)
    gagal = [x for x in h if not x['ok']]
    if not diam:
        for x in h: print(('  ok  ' if x['ok'] else 'GAGAL ') + x['nama'] + ('' if x['ok'] or not x['ket'] else ' · ' + str(x['ket'])[:600]))
        print(('LULUS ' if not gagal else 'GAGAL ') + str(len(h) - len(gagal)) + '/' + str(len(h)))
    return not gagal


MUTASI = [
    ('Tahap 6: tanda terima mencetak kg yang dibukukan sebagai kg nota (jumlah × isi ≠ kg)', LOGIKA, "const kgNota = x.ikut ? x.kgNota : x.kg;", "const kgNota = x.kg;"),
    ('Tahap 6: tanda terima tanpa baris hasil timbang', LOGIKA, "    if (x.ikut) b('  hasil timbang (dibukukan)', KG(x.kg), { jenis: 'ttTimbang' }); });", "    });"),
    ('nilai nota ikut upah bongkar', LOGIKA, "const nilai = Math.round(baris.reduce((a, x) => a + x.nilai, 0));", "const nilai = Math.round(baris.reduce((a, x) => a + x.nilai, 0)) + bil(batch.biayaBongkar);"),
    ('akun yang tidak membaca pembayaran dicetak "belum dibayar"', LOGIKA, "else if (!B.terbaca) hasil = {", "else if (false) hasil = {"),
    ('pembayaran tidak terbaca mencetak sisa = nilai nota', LOGIKA, "by('Dibayar: Rp', TITIK); by('Sisa: Rp', TITIK);", "by('Sudah dibayar', RP(0)); by('SISA BON', RP(d.nilai));"),
    ('tunai dianggap bon', LOGIKA, "const bon = batch.caraBayar === 'utang';", "const bon = true;"),
    ('bon dianggap tunai', LOGIKA, "const bon = batch.caraBayar === 'utang';", "const bon = false;"),
    ('uang di atas nilai bon ikut dicetak', LOGIKA, "Math.max(0, Math.min(nilai, Math.round(bil(B.dibayar))))", "Math.max(0, Math.round(bil(B.dibayar)))"),
    ('angka bayar minus dicetak apa adanya', LOGIKA, "Math.max(0, Math.min(nilai, Math.round(bil(B.dibayar))))", "Math.min(nilai, Math.round(bil(B.dibayar)))"),
    ('rincian bayar dicetak walau jumlahnya tidak cocok', LOGIKA, "rinci: cocok ? rinci : [] };", "rinci };"),
    ('sisa bon tidak dikurangi yang dibayar', LOGIKA, "sisa: nilai - dibayar, rinci", "sisa: nilai, rinci"),
    ('bon lunas dicetak sebagai sebagian', LOGIKA, "dibayar >= nilai ? 'lunas' : 'sebagian'", "dibayar > nilai ? 'lunas' : 'sebagian'"),
    ('subtotal per baris ikut tercetak', LOGIKA, ": x.jumlah + ' x ' + DESIMAL(x.berat) + ' = ' + KG(kgNota);", ": x.jumlah + ' x ' + DESIMAL(x.berat) + ' = ' + KG(kgNota) + ' ' + RP(x.nilai);"),   # jangkar disesuaikan Tahap 6 & 28 Nov
    ('baris bal dihitung karung', LOGIKA, "karung: baris.reduce((a, x) => a + (x.bal ? 0 : x.jumlah), 0)", "karung: baris.reduce((a, x) => a + x.jumlah, 0)"),
    ('stok awal diberi tanda terima', LOGIKA, "if (batch.stokAwal || batch.tutupBuku || batch.lahirBuku) return", "if (batch.tutupBuku || batch.lahirBuku) return"),
    ('kedatangan tanpa pemasok diberi tanda terima', LOGIKA, "if (!String(batch.pemasok || '').trim()) return", "if (false) return"),
    ('nomor tanpa tanggal kedatangan', LOGIKA, ".replace(/[^0-9]/g, '').slice(2, 8);", ".replace(/[^0-9]/g, '').slice(0, 0);"),
    ('lembar toko tanpa tempat nama supir', LOGIKA, "if (lembar === 'toko') { b('Nama terang supir dan jam:'", "if (lembar === 'tokoX') { b('Nama terang supir dan jam:'"),
    ('lembar pemasok tanpa namanya', LOGIKA, "if (lembar === 'pemasok') b('LEMBAR PEMASOK'", "if (lembar === 'pemasokX') b('LEMBAR PEMASOK'"),
    ('kapan dicetak tidak dimuat', LOGIKA, "if (C.tanggal) b('Keadaan per '", "if (false) b('Keadaan per '"),
    ('titik-titik isian terlalu panjang untuk kertas 58 mm', LOGIKA, "const TITIK = '..................';", "const TITIK = '..............................';"),
    ('tunai tidak dicetak lunas', LOGIKA, "by('Sisa', 'LUNAS', { tebal: true }); }", "by('Sisa', RP(d.nilai), { tebal: true }); }"),
    ('nama pemasok tidak dirapikan', LOGIKA, "pemasok: String(batch.pemasok || '').trim(), baris,", "pemasok: String(batch.pemasok || ''), baris,"),
    ('panel: pembayaran dianggap terbaca untuk semua akun', PANEL, "const terbaca = akunMembaca(akun, KOLEKSI_BAYAR);", "const terbaca = true;"),
    ('panel: angka bayar bukan dari buku utang pemasok', PANEL, "dibayar: bb ? bb.dibayarMesin : 0,", "dibayar: bb ? bb.dibayar : 0,"),
    ('panel: rupiah tampil di layar akun bukan-owner', PANEL, "(staf ? (d.bon ? 'bon' : 'tunai') : 'nilai nota '", "(false ? (d.bon ? 'bon' : 'tunai') : 'nilai nota '"),
    ('panel: dua cetakan boleh bertumpuk', PANEL, "    if (printerSibuk()) return set({ kabar: KALIMAT_MASIH_MENCETAK, kabarAwas: true });\n    PR.jalurCetak()", "    PR.jalurCetak()"),
    ('panel: di aplikasi tablet dialog cetak dibuka', PANEL, "const dialog = () => { if (asliAda()) return set({ kabar: T.nama + ' TIDAK tercetak", "const dialog = () => { if (false) return set({ kabar: T.nama + ' TIDAK tercetak"),
    ('panel: printer diam dianggap gagal', PANEL, "          if (hasilTakDiketahui(e)) return set({ kabar: 'Printer tidak mengabari hasil cetak lembar ke-'", "          if (false) return set({ kabar: 'Printer tidak mengabari hasil cetak lembar ke-'"),
    ('panel: tombol WhatsApp tampil di aplikasi tablet', PANEL, "${asliAda() ? '' : h`<div class=\"kaca-btn\" data-aksi=\"tbmWa\"", "${false ? '' : h`<div class=\"kaca-btn\" data-aksi=\"tbmWa\""),
    ('catatan: kelompok "yang tertulis di nota" (harga per kg) ikut', LOGIKA, "const TBM_BUKAN_CATATAN = /^yang tertulis di nota/i;", "const TBM_BUKAN_CATATAN = /^$/;"),
    ('catatan: usul yang belum disimpan ikut tercetak', LOGIKA, "if (!S || !S.ada || !Array.isArray(S.baris)) return [];", "if (!S || !Array.isArray(S.baris)) return [];"),
    ('catatan: tidak tercetak di lembar', LOGIKA, "  if ((d.catatan || []).length) {", "  if (false) {"),
    ('catatan: potongan tanpa tanda minus', LOGIKA, "const tbmRpCatatan = (n) => (n === '' ? '' : n < 0 ? '-' + RP(-n) : RP(n));", "const tbmRpCatatan = (n) => (n === '' ? '' : RP(Math.abs(n)));"),
    ('catatan: judul kelompok tidak tercetak', LOGIKA, "b(String(k.judul).toUpperCase(), '', { tebal: true, jenis: 'ttCatJudul' });", ""),
    ('gambar: baris JUMLAH tanpa tanda jenis', LOGIKA, "b('JUMLAH', sebutJumlah(d.jumlah), { tebal: true, jenis: 'ttJumlah' });", "b('JUMLAH', sebutJumlah(d.jumlah), { tebal: true });"),
    ('gambar: rincian karung tidak dibawa ke model', LOGIKA, "nilai: { nama, rinci, kg:", "nilai: { nama, rinci: '', kg:"),
    ('model: hasil timbang diabaikan', MODEL, "else if (j === 'ttTimbang') { if (kini) kini.timbang = kanan; }", "else if (j === 'ttTimbang') { }"),
    ('model: catatan diabaikan', MODEL, "kel.baris.push({ teks: kiri, n: kanan, tebal: !!g.tebal }); }", "}"),
    ('model: garis nota dianggap tanda terima', MODEL, "/^tt[A-Z]/.test(g.jenis)", "!!g.jenis"),
    ('panel: catatan tidak diteruskan ke tanda terima', PANEL, ", TBM.tbmCatatan(C.cpIsiSurat(id))) };", ") };"),
    ('panel: Bluetooth mencetak gambar besar', PANEL, "const timpa = j === 'sunmi-bt' ? { gaya: 'teks' } : null;", "const timpa = null;"),
    ('panel: logo tidak ikut ke printer', PANEL, "PR.susunCetak(g, timpa, { qr: '', logoToko: pakaiLogo() })", "PR.susunCetak(g, timpa, { qr: '', logoToko: false })"),
    ('panel: masih dipaksa gaya teks', PANEL, "PR.susunCetak(g, timpa, { qr: '', logoToko: pakaiLogo() })", "PR.susunCetak(g, { gaya: 'teks' }, { qr: '', logoToko: pakaiLogo() })"),
    ('panel: dialog cetak selalu teks', PANEL, "if (PR.prAtur().gaya === 'teks') return teks();", "return teks();"),
    ('kanvas: tanda terima digambar gaya Sertifikat', KANVAS, "  if (stAdaTandaTerima(garis)) return gambarTandaTerima(garis, opsi);   // owner 28 Nov 2026: tanda terima barang masuk berlogo\n", ""),
    ('kanvas: ada teks tanda terima tanpa gores tepi', KANVAS, "  // kop\n  pitaGuilloche(c, W, k, y, P(40)); y += P(62);", "  // kop\n  c.fillText('x', 0, 0); pitaGuilloche(c, W, k, y, P(40)); y += P(62);"),
    ('kanvas: label tanda terima Jost 400', KANVAS, "tulis('nama & paraf', F_SANS(500, P(14))", "tulis('nama & paraf', F_SANS(400, P(14))"),
    ('kanvas: tanpa logo toko', KANVAS, "} else if (o.logoToko) { y += gambarLogoToko(c, cx, y, P(150)) + P(16); }", "}"),
    ('stok: lembar Barang masuk masih menyebut tombol lama', STOK, "ikut tercetak di kedua lembar tanda terima (CETAK 2 LEMBAR)", "bisa langsung dicetak (tombol \"CETAK CATATAN PEMASOK\")"),
    ('panel: menulis ke buku', PANEL, "import { bukanOwner, akunMembaca } from './akses-layar.js';", "import { bukanOwner, akunMembaca } from './akses-layar.js';\nimport { tulisDokumen } from '../data/toko.js';"),
    ('akses: akun bukan-owner dianggap membaca semua koleksi', AKSES_LAYAR, "!bukanOwner(akun) || BACA_STAF.indexOf(koleksi) >= 0;", "true;"),
    ('stok: tombol akun tablet hilang', STOK, " data-k=\"tombol-terima\" data-aksi=\"bukaTerima\">", " data-k=\"tombol-terima\" data-aksi=\"tombolMati\">"),
    ('stok: lembar daftar tidak terpasang', STOK, "s.lembar === 'terima' ? lembarTerima(s, { akun: opsi.akun ? opsi.akun() : null, bawah: gambarUsulTablet(s) }) : ", ""),
    ('stok: sesudah Simpan kartu tidak dibuka', STOK, "tbm: idT !== null && idT !== undefined ? { id: String(idT) } : null });", "tbm: null });"),
    ('stok: aksi panel tidak digabung', STOK, "\n  aksiPanelTerima({ set, akun: opsi.akun, waktu }));", ");"),
    ('index: modul panel tidak dimuat lebih dulu', INDEX, '<link rel="modulepreload" href="js/layar/terima-barang-panel.js">\n', ''),
]


def main():
    asli = baca_semua()
    if '--kontrol' in sys.argv:
        lolos = []
        for nama, berkas, lama, baru in MUTASI:
            if lama not in asli[berkas]: print('KONTROL BASI: pola tidak ditemukan —', nama); lolos.append(nama); continue
            t = dict(asli); t[berkas] = asli[berkas].replace(lama, baru, 1)
            if periksa(t, diam=True): lolos.append(nama); print('LOLOS (seharusnya gagal):', nama)
            else: print('  tertangkap:', nama)
        if not periksa(asli, diam=True): print('GAGAL: salinan utuh tidak lulus'); return 3
        print('KONTROL ' + ('LULUS' if not lolos else 'GAGAL') + ' ' + str(len(MUTASI) - len(lolos)) + '/' + str(len(MUTASI)))
        return 0 if not lolos else 3
    return 0 if periksa(asli) else 1


if __name__ == '__main__':
    sys.exit(main())
