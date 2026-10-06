#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_katalog_kasir.py — putaran 25c Bagian A: KATALOG KASIR (ringkasanKasir/aktif) DITERBITKAN /baru/, bentuk tetap (keputusan owner 27 Sep 2026).

PENSIUN SISTEM LAMA (owner 3 Okt 2026): index.html & kasir.html kini halaman pengalih tanpa script; versi terakhirnya di tag git sistem-lama-terakhir
(commit 48a694d). Yang dulu dibaca dari teksnya kini: penyusun isi = susunIsiKatalogKasir di baru/js/mesin/pembantu.js yang TERKUNCI SIDIK
(alat-uji/pembantu.sha256 — dicatat saat byte-sama dengan index.html 48a694d); kunci dokumen terbitkanRingkasanKasir() DIBEKUKAN di KUNCI_LAMA. DIHAPUS
bersama objeknya: penjaga tulis index.html (bagian 7 + kontrolnya), buku kecil bayar bon kasir.html (39b no. 4 / no. 3 / cara persis — jsc, statis &
kontrolnya), dan pemeriksaan waktu server katalog kasir darurat (K2: kunci bersama yang dibaca buku kecil kasir.html — kini tanpa pembaca).

STATIS:
  · penyusun isi di /baru/ (baru/js/mesin/pembantu.js) = susunIsiKatalogKasir() sistem lama: TERKUNCI SIDIK (pembantu.sha256)
  · dokumen: kunci & urutannya = terbitkanRingkasanKasir() sistem lama (KUNCI_LAMA, dibekukan dari tag; dibandingkan di jsc dengan kkDokumen)
  · firebase.js: katalog ditulis APA ADANYA (tanpa atribusi/jejak) di penulis pusat; penerbit otomatis lewat gerbang kkBolehTerbit, hanya kalau isinya
    berbeda; pendengar dokumen katalog hanya untuk owner; terbit tiap data berubah (dengarkan)
  · harga.js: terbit harga menyertakan katalog (kkSertakan) di kiriman yang SAMA
  · kasir darurat (izin owner 27 Sep): ambil katalog saat layar dinyalakan & tiap 5 menit; denyut membawa cap katalog; versi kasir darurat =
    VERSI sw-kasir.js = KK_VERSI_KASIR_TERBARU (/baru/) = kasir-v32; lantai kunci bulan (KP_VERSI_KASIR_25B) tidak di atas versi yang disajikan
  · salinan uji peramban (dibangun TANPA peramban, owner 3 Okt, perkuat): script-src = hash halaman + hash skenario, tanpa 'unsafe-inline';
    tiap script sesudah meta ber-hash; penjaga pelanggaran CSP & palsu Firestore SEBELUM meta (uji_antrean_kasir.periksa_salinan)
JSC (KOTAK PASIR — angka & nama contoh; + cadangan toko kalau ada di _privat/, lokal saja):
  · isi /baru/ (kkIsi, dengan saringan arsip & wadah) == penyusun sistem lama untuk data yang sama — kotak pasir & cadangan toko
  · kunci dokumen = urutan sistem lama; pembanding tidak tertipu urutan kunci peta dari Firestore; server belum terbaca = "belum tahu"
  · terbit harga → katalog SESUDAH terbit ikut di daftar dokumen yang sama; cache tidak berubah; isinya = katalog sesudah kiriman ditulis
  · tiap kejadian di peta §2 (barang masuk, adukan, nota, bayar bon, beli kantong, terbit harga) membuat katalog "tertinggal"
  · gerbang terbit: owner · Firestore · online · tanpa koleksi ditolak · semua termuat · semua dari SERVER · katalog server terbaca
  · Beranda: "katalog kasir: diperbarui …", perubahan yang belum sampai, HP kasir versi lama, HP penjaga yang masih memegang katalog lama;
    perangkat kasir.html (pensiun) tidak disebut
PERAMBAN (Chrome headless, SATU peluncuran; kasir-darurat-nominal.html SUNGGUHAN + Firestore REST palsu; CSP salinan = CSP halaman + hash skenario
uji, TANPA 'unsafe-inline' — owner 3 Okt, perkuat; dulu dilonggarkan ke 'unsafe-inline'):
  · tiap pemuatan: tombol KANARI ber-onclick sebaris diblokir & tercatat (CSP berlaku, pendengar hidup), NOL pelanggaran CSP lain
  · katalog berganti di server → TANPA dibuka ulang: harga tuts tetap lama sampai layar dinyalakan (visibilitychange), lalu harga baru; denyut membawa
    cap katalog baru
  · katalog berganti → tanpa ketukan apa pun, diambil sendiri di jadwal berkala (jadwal 5 menit dipercepat di salinan uji)

    python3 alat-uji/uji_katalog_kasir.py            → N lulus · 0 gagal
    python3 alat-uji/uji_katalog_kasir.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob, shutil, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, beku2, uji_harga_baru  # noqa: E402
from uji_antrean_kasir import CHROME, layani, buka, hasil_dari, teks_stat  # noqa: E402
import uji_antrean_kasir as UA  # noqa: E402  (owner 3 Okt, perkuat: PENJAGA_CSP, csp_salinan & periksa dibaca saat dipakai — kontrol bisa menggantinya)

JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/arsip-logika.js', 'baru/js/data/katalog-kasir.js', 'baru/js/layar/harga-logika.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/struk-logika.js', 'baru/js/layar/jual-logika.js', 'baru/js/layar/wadah-bernama-logika.js', 'baru/js/layar/stok-adukan-logika.js', 'baru/js/layar/setengah-logika.js']
BERKAS = ['baru/js/mesin/pembantu.js', 'baru/js/data/firebase.js', 'baru/js/layar/harga.js', 'baru/js/layar/ringkasan.js', 'kasir-darurat-nominal.html',
          'sw-kasir.js', 'baru/js/data/kunci-periode.js'] + MODUL
JAM = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
DARURAT = 'kasir-darurat-nominal.html'


def baca(ganti=None):
    t = {}
    for b in dict.fromkeys(BERKAS):
        t[b] = open(os.path.join(AKAR, b), encoding='utf-8').read()
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert lama in t[b], 'kontrol basi: ' + b + ' · ' + lama[:80]
            t[b] = t[b].replace(lama, baru, 1)
    return t


# Kunci & urutan dokumen ringkasanKasir/aktif yang ditulis terbitkanRingkasanKasir() sistem lama (setDoc). Dibekukan 3 Okt 2026 (sistem lama pensiun):
# diekstrak dari `git show sistem-lama-terakhir:index.html` (commit 48a694d) dengan pola lama setDoc(doc(db, 'ringkasanKasir', 'aktif'), { … }).
KUNCI_LAMA = ['id', 'diperbaruiPada', 'kemasan', 'merkKarung', 'bahanLiteran', 'piutang']
VERSI_KASIR = 'kasir-v32'


# ---------- KOTAK PASIR: data uji harga (angka contoh) + bon pelanggan + kantong literan ----------
KOTAK = json.loads(json.dumps(uji_harga_baru.KOTAK))
KOTAK['piutangMutasi'] = [{'id': 601, 'tipe': 'saldoAwal', 'namaPelanggan': 'Pelanggan Contoh', 'nominal': 150000, 'tanggal': '2026-09-01', 'jam': '10:00'}]
KOTAK['stokBahanLiteran'] = [{'id': 701, 'tipe': 'beli', 'jenis': 'paperbag5l', 'jumlah': 100, 'hargaTotal': 30500, 'tanggal': '2026-09-02'}]
KOTAK['perangkatStatus'] = []


def cadangan_toko():
    c = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')), key=os.path.basename)
    return c[-1] if c else None


SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 9000; return function () { n += 1; return n; }; })() };
var kanonUrut = function (x) { return kkKanon(x); };
// ---- 1 · isi byte-sama dengan penyusun sistem lama (susunIsiKatalogKasirLama = pembantu.js yang TERKUNCI SIDIK, lihat jalan_jsc)
var I = kkIsi(); var LAMA = susunIsiKatalogKasirLama();
var I0 = I ? JSON.parse(J(I)) : null; if (I0) { delete I0.bayarBonTerhitung; delete I0.bayarBonSejak; }
ok('isi katalog /baru/ = isi susunIsiKatalogKasir() sistem lama untuk data yang sama (JSON persis, urutan ikut) + DUA kunci paling akhir bayarBonTerhitung & bayarBonSejak (cara persis, owner 30 Sep)', !!I && J(I0) === J(LAMA) && J(Object.keys(I).slice(-2)) === J(['bayarBonTerhitung', 'bayarBonSejak']) && Array.isArray(I.bayarBonTerhitung) && I.bayarBonSejak === '', J(I0).slice(0, 300) + ' ≠ ' + J(LAMA).slice(0, 300));
ok('isi memuat keempat bagian sistem lama: kemasan, merkKarung (+ modal & harga), bahanLiteran, piutang (yang masih bersisa)', !!I && I.kemasan.length === 1 && I.kemasan[0].namaProduk === 'Kembang' && I.kemasan[0].hargaPerUnit === 75000
  && I.merkKarung.some(function (m) { return m.merk === 'Angsa' && m.hargaPerKg === 13800 && m.hargaPerLiter === 12500 && m.hargaKarung50 === 700000 && m.hppPerKg > 0; })
  && I.bahanLiteran.paperbag5l.sisaPcs === 100 && I.bahanLiteran.paperbag5l.hargaPerPcs === 305 && I.piutang.length === 1 && I.piutang[0].nama === 'Pelanggan Contoh' && I.piutang[0].sisa === 150000, J(I));
if (CADANGAN) {
  Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
  var IC = kkIsi(); var LC = susunIsiKatalogKasirLama(); var IM = susunIsiKatalogKasir();
  // 39b (30 Sep): sejak putaran 27 (arsip) & 28 (buku ukuran / stok wadah) katalog HP kasir SENGAJA bukan salinan sistem lama — yang byte-sama adalah penyusunnya
  // SEBELUM saringan; sesudah saringan, tiap beda wajib punya alasan yang sudah dikunci kotak pasir uji_arsip_produk / uji_buku_ukuran / uji_wadah_stok_sendiri
  ok('DATA TOKO (cadangan ' + NAMA_CADANGAN + '): penyusun /baru/ SEBELUM saringan = isi penyusun sistem lama (JSON persis)', !!IM && J(IM) === J(LC) && IM.merkKarung.length > 0,
    IM ? IM.merkKarung.length + ' merek; ' + J(IM).slice(0, 200) + ' ≠ ' + J(LC).slice(0, 200) : 'null');
  var arP = arPeta(); var ukB = petaUkuran(); var ukI = indukTerpisah();
  var namaC = IC.merkKarung.map(function (m) { return m.merk; }); var namaL = LC.merkKarung.map(function (m) { return m.merk; });
  var hilang0 = namaL.filter(function (m) { return namaC.indexOf(m) < 0; }); var tambah = namaC.filter(function (m) { return namaL.indexOf(m) < 0; });
  // cadangan 1 Okt (semua wadah aktif): buku KHUSUS (karung belakang / sisihan / adukan dibuka) & kunci wadah lama bersisa nol juga SENGAJA tidak dijual dari HP kasir
  // (wbSaringKatalogKasir) — bukan nama yang diarsipkan
  var bwK = petaBukuWadah(); var pwK = petaStokWadah(); var skK = hitungStokKarungPerMerk();
  var khusus = function (m) { return (bwK[m] && bwK[m].jenis !== 'wadah') || (pwK[m] && Math.abs(((skK[m] || {}).sisaKg) || 0) < 0.005); };
  var hilangKhusus = hilang0.filter(khusus); var hilang = hilang0.filter(function (m) { return !khusus(m); });
  var wadahAktif = {}; aturWadah().daftar.forEach(function (W) { if (pwK[wbKunci(W)]) wadahAktif[W] = true; });
  var BOLEH_BUKU = ['karung50', 'hargaKarung25', 'hargaPerKg'], BOLEH_INDUK = ['karung25', 'hargaKarung25'];
  var bedaLain = []; IC.merkKarung.forEach(function (x) { var y = LC.merkKarung.filter(function (z) { return z.merk === x.merk; })[0]; if (!y || J(x) === J(y)) return;
    var kol = Object.keys(x).concat(Object.keys(y)).filter(function (k, i, a) { return a.indexOf(k) === i && J(x[k]) !== J(y[k]); });
    // saringan wadah (putaran 28/39, wbSaringKatalogKasir): buku 'Wadah X' dijual per liter dengan harga liter wadahnya (kolom karung & per kg nol);
    // merek bernama wadah AKTIF tidak menjual literan atas namanya sendiri (harga liter 0); induk 25 kg terpisah tidak menawarkan 25 kg lagi
    var boleh = pwK[x.merk] ? ['karung50', 'karung25', 'hargaKarung25', 'hargaKarung50', 'hargaPerKg', 'hargaPerLiter', 'rasio']
      : (ukB[x.merk] ? BOLEH_BUKU : ukI[x.merk] ? BOLEH_INDUK : []).concat(wadahAktif[x.merk] ? ['hargaPerLiter'] : []);
    if (!kol.every(function (k) { return boleh.indexOf(k) >= 0; })) bedaLain.push([x.merk, kol]); });
  ok('DATA TOKO: katalog HP kasir = penyusun sistem lama MINUS nama beras yang diarsipkan (' + hilang.length + ' nama), MINUS buku khusus wadah (' + hilangKhusus.length + ') dan MINUS kolom karung 25 kg yang pindah ke buku ukurannya (' + Object.keys(ukB).length + ' buku); kemasan, bahan literan, piutang sama; tidak ada beda lain',
    hilang.length === Object.keys(arP).filter(function (k) { return k.slice(0, 2) === 'K:'; }).length && hilang.every(function (m) { return arBeras(m, arP); }) && !tambah.length && !bedaLain.length
    && J(IC.kemasan) === J(LC.kemasan) && J(IC.bahanLiteran) === J(LC.bahanLiteran) && J(IC.piutang) === J(LC.piutang), J({ hilang: hilang, tambah: tambah, bedaLain: bedaLain }));
  Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); }); Object.keys(CADANGAN).forEach(function (n) { if (!(n in KOTAK)) pasok(n, []); });
}
// ---- 2 · bentuk dokumen & pembanding
var D = kkDokumen(I, '2026-09-19T03:00:00.000Z');
ok('dokumen: kunci & urutannya = setDoc terbitkanRingkasanKasir() sistem lama (' + KUNCI_LAMA.join(', ') + ') + bayarBonTerhitung & bayarBonSejak paling akhir, id "aktif"', J(Object.keys(D)) === J(KUNCI_LAMA.concat(['bayarBonTerhitung', 'bayarBonSejak'])) && D.id === 'aktif' && D.diperbaruiPada === '2026-09-19T03:00:00.000Z', J(Object.keys(D)));
ok('dokumen katalog = dokumen turunan, ditulis APA ADANYA oleh penulis pusat (kkMentah): hanya ringkasanKasir', kkMentah('ringkasanKasir') && !kkMentah('penjualan') && !kkMentah('pengaturan'));
var acak = function (x) { if (Array.isArray(x)) return x.map(acak); if (x && typeof x === 'object') { var o = {}; Object.keys(x).reverse().forEach(function (k) { o[k] = acak(x[k]); }); return o; } return x; };
kkLupakanServer(); ok('server belum terbaca → tertinggal = null (belum bisa tahu; tidak terbit, Beranda tidak menebak)', kkTertinggal(I) === null);
kkSetelServer(null, true); ok('server terbaca & dokumen belum pernah ada → tertinggal = true', kkTertinggal(I) === true);
kkSetelServer(acak(D), true); ok('server = isi yang sama dengan URUTAN KUNCI LAIN (seperti peta Firestore) → tidak tertinggal (tidak terbit ulang tanpa henti)', kkTertinggal(I) === false, kkKanon(acak(D)).slice(0, 200));
var D2 = JSON.parse(J(D)); D2.merkKarung[0].hargaPerKg += 100; kkSetelServer(D2, true);
ok('satu harga beda → tertinggal = true', kkTertinggal(I) === true);
// ---- 2b · cara persis (owner 30 Sep): id pembayaran bon yang SUDAH dihitung di `piutang` dokumen yang sama
var pmLama = JSON.parse(J(ambilPiutangMutasi()));
pasok('piutangMutasi', pmLama.concat([{ id: 611, tipe: 'bayar', namaPelanggan: 'Pelanggan Contoh', nominal: 20000, tanggal: '2026-09-18', jam: '10:00' },
  { id: 612, tipe: 'bayar', namaPelanggan: 'Pelanggan Contoh', nominal: 10000, tanggal: '2026-08-01', jam: '10:00' }, { id: 613, tipe: 'bayar', namaPelanggan: '  ', nominal: 5000, tanggal: '2026-09-18', jam: '10:00' },
  { id: 614, tipe: 'hapusBuku', namaPelanggan: 'Pelanggan Contoh', nominal: 1000, tanggal: '2026-09-18', jam: '10:00' },
  { id: 1759249200123 + 0.4567, tipe: 'bayar', namaPelanggan: 'Pelanggan Contoh', nominal: 1000, tanggal: '2026-09-19', jam: '10:00' }]));
var BT = kkBayarTerhitung(), Dp = kkDokumen(kkIsi(), W.kini);
ok('cara persis: daftar = id SEMUA pembayaran yang dihitung hitungPiutang (tipe bayar, bernama), TANPA jendela hari (tidak bergantung jam HP / jam penerbit): 1759249200123.4567 (id pecahan idUnik HP), 611, 612 (1 Agu) — bukan 613 (tanpa nama), 614 (hapus buku), 601 (saldo awal); ikut di isi & dokumen', J(BT) === J([String(1759249200123 + 0.4567), '611', '612']) && J(kkIsi().bayarBonTerhitung) === J(BT) && J(Dp.bayarBonTerhitung) === J(BT) && Dp.bayarBonSejak === '', J([BT, Dp.bayarBonTerhitung, Dp.bayarBonSejak]));
var Dj = (function () { var t = Date.now; Date.now = function () { return t() + 400 * 86400000; }; var x = kkDokumen(kkIsi(), W.kini); Date.now = t; return x; })();
ok('cara persis: isi katalog tidak bergantung jam perangkat penerbit (jam dimajukan 400 hari → daftar & tanda awal buku sama; dua perangkat owner tidak saling timpa)', J(Dj.bayarBonTerhitung) === J(Dp.bayarBonTerhitung) && Dj.bayarBonSejak === Dp.bayarBonSejak && kkKanon(Dj) === kkKanon(Dp), J([Dj.bayarBonTerhitung, Dj.bayarBonSejak]));
pasok('piutangMutasi', ambilPiutangMutasi().concat([{ id: 615, tipe: 'saldoAwal', namaPelanggan: 'Pelanggan Contoh', nominal: 5000, tanggal: '2025-11-02', jam: '', tutupBuku: true, tahunDari: 2025 }]));
ok('cara persis: sesudah tutup buku 2025 (saldo pembuka piutang bertanda tutupBuku + tahunDari 2025) → bayarBonSejak "2026-01-01": pembayaran HP bertanggal sebelumnya sudah terserap saldo pembuka', kkBayarSejak() === '2026-01-01' && kkDokumen(kkIsi(), W.kini).bayarBonSejak === '2026-01-01' && kkKanon(kkDokumen(kkIsi(), W.kini)) !== kkKanon(Dp), kkBayarSejak());
pasok('piutangMutasi', ambilPiutangMutasi().filter(function (m) { return m.id !== 615; }));
var Dlama = JSON.parse(J(Dp)); delete Dlama.bayarBonTerhitung; kkSetelServer(Dlama, true);
ok('katalog server dari penerbit lama (tanpa daftar) sementara ada pembayaran terhitung → tertinggal (terbit ulang sekali)', kkTertinggal() === true);
kkSetelServer(Dp, true); var sama = kkTertinggal(); var Dp2 = JSON.parse(J(Dp)); Dp2.bayarBonTerhitung = ['611', '999']; kkSetelServer(Dp2, true);
ok('daftar sama → tidak tertinggal; daftar id beda → tertinggal', sama === false && kkTertinggal() === true);
pasok('piutangMutasi', pmLama); var Dl2 = JSON.parse(J(kkDokumen(kkIsi(), W.kini))); delete Dl2.bayarBonTerhitung; delete Dl2.bayarBonSejak; kkSetelServer(Dl2, true);
ok('tanpa pembayaran terhitung, katalog lama tanpa daftar = sama (tidak terbit ulang tanpa perlu)', kkTertinggal() === false && J(kkIsi().bayarBonTerhitung) === '[]');
// ---- 3 · terbit harga: katalog SESUDAH terbit ikut di kiriman yang sama
kkSetelServer(D, true);
terapkanKeCache(susunUbah('Angsa|S', '14.000', 'jual', W).dokumen);
var T = susunTerbit(W, true);
// audit 39b no. 17: kkSertakan memakai gerbang terbit yang SAMA (firebase.js kkPasangGerbang) — tertutup (tanpa penilai / data belum termuat) → katalog tidak ikut
var tanpaPenilai = kkSertakan(T.dokumen, W.kini).length; kkPasangGerbang(function () { return { boleh: false, sebab: 'data belum termuat semua' }; }); var tertutup = kkSertakan(T.dokumen, W.kini).length;
kkPasangGerbang(function () { return kkBolehTerbit({ owner: true, sumber: 'firestore', koleksiSiap: 20, koleksiTotal: 21, dariCache: 0, ditolak: 0, online: true }); }); var belumSemua = kkSertakan(T.dokumen, W.kini).length;
ok('39b-17 terbit harga saat gerbang katalog TERTUTUP (tanpa penilai · data belum termuat semua 20/21) → katalog kasir TIDAK ikut kiriman (terbit otomatis menyusul)', tanpaPenilai === T.dokumen.length && tertutup === T.dokumen.length && belumSemua === T.dokumen.length, J([tanpaPenilai, tertutup, belumSemua, T.dokumen.length]));
// tinjauan no. 17: kabar kiriman JUJUR — gerbang tertutup → "BELUM ikut … menyusul", bukan "ikut berganti di kiriman yang sama"
kkPasangGerbang(function () { return { boleh: false, sebab: 'tidak tersambung' }; }); var KT17 = kkSertakanKiriman(T, W.kini);
kkPasangGerbang(function () { return { boleh: true, sebab: '' }; }); var KB17 = kkSertakanKiriman(T, W.kini);
ok('39b-17 kabar terbit harga: gerbang tertutup → katalog tidak ikut dan kabar menyebut "BELUM ikut … (tidak tersambung) … menyusul" (kalimat "ikut berganti di kiriman yang sama" dibuang); gerbang terbuka → katalog ikut, kabar apa adanya',
  !KT17.dokumen.some(function (d) { return d.koleksi === 'ringkasanKasir'; }) && /BELUM ikut kiriman ini \(tidak tersambung\)/.test(KT17.patch.kabar) && !/ikut berganti di kiriman yang sama/.test(KT17.patch.kabar)
  && KB17.dokumen.some(function (d) { return d.koleksi === 'ringkasanKasir'; }) && KB17.patch.kabar === T.patch.kabar, J([KT17.patch.kabar, KB17.patch.kabar]));
var sebelum = J(kkIsi()); var DK = kkSertakan(T.dokumen, W.kini); var kk = DK.filter(function (d) { return d.koleksi === 'ringkasanKasir'; });
ok('terbit harga: SATU dokumen ringkasanKasir ditambahkan ke daftar dokumen kiriman yang sama (paling akhir); dokumen terbit lain utuh', !T.tolak && kk.length === 1 && DK[DK.length - 1].koleksi === 'ringkasanKasir' && DK.length === T.dokumen.length + 1 && J(DK.slice(0, -1)) === J(T.dokumen), J(DK.map(function (d) { return d.koleksi; })));
ok('isinya katalog SESUDAH terbit (Angsa per kg 14.000), bukan sebelumnya (13.800)', kk.length && kk[0].data.merkKarung.some(function (m) { return m.merk === 'Angsa' && m.hargaPerKg === 14000; }), kk.length ? J(kk[0].data.merkKarung) : '-');
ok('menyusun katalog "seandainya" tidak mengubah cache (katalog dari cache masih 13.800 sebelum kiriman ditulis)', J(kkIsi()) === sebelum && kkIsi().merkKarung.some(function (m) { return m.merk === 'Angsa' && m.hargaPerKg === 13800; }));
terapkanKeCache(DK.filter(function (d) { return d.koleksi !== 'ringkasanKasir'; })); kkSetelServer(kk[0].data, true);
ok('sesudah kiriman ditulis: katalog dari data = katalog yang ikut dikirim → tidak ada terbit kedua', kkTertinggal() === false);
ok('kiriman yang tidak mengubah katalog → tidak ada dokumen katalog yang ikut', kkSertakan([{ koleksi: 'aturanToko', data: { id: 'hargaLabel', daftar: [] } }], W.kini).length === 1);
// ---- 4 · tiap kejadian di peta §2 membuat katalog tertinggal
var sejak = function () { kkSetelServer(kkDokumen(kkIsi(), W.kini), true); };
var KEJADIAN = [
  ['barang masuk (kedatangan baru)', 'batchMasuk', { id: 'b9', tanggal: '2026-09-19', jam: '08:00', pemasok: 'RODA CONTOH', caraBayar: 'tunai', merkList: [{ id: 'b90', merk: 'Angsa', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 13700, subtotalHarga: 1370000 }] }],
  ['adukan (kemasan baru jadi)', 'produksiKemasan', { id: 'p9', tanggal: '2026-09-19', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 10, hppPerUnit: 66000, merkSumber: 'Pandan Wangi', kgDipakai: 50 }],
  ['nota (karung terjual)', 'penjualan', { id: 'n9', tanggal: '2026-09-19', jam: '09:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 700000, hppTotalSaatJual: 662500 }],
  ['bayar bon pelanggan', 'piutangMutasi', { id: 602, tipe: 'bayar', namaPelanggan: 'Pelanggan Contoh', nominal: 50000, tanggal: '2026-09-19', jam: '09:10' }],
  ['beli kantong literan', 'stokBahanLiteran', { id: 702, tipe: 'beli', jenis: 'paperbag5l', jumlah: 50, hargaTotal: 16000, tanggal: '2026-09-19' }],
  ['harga literan diterbitkan', 'katalogHargaLiteran', { id: 'Angsa', merk: 'Angsa', hargaPerLiter: 13000, diubahPada: '2026-09-19T03:00:00.000Z' }]];
KEJADIAN.forEach(function (k) { sejak(); terapkanKeCache([{ koleksi: k[1], data: k[2] }]); ok('kejadian ' + k[0] + ' → katalog kasir tertinggal (akan terbit)', kkTertinggal() === true); });
// ---- 5 · gerbang terbit otomatis
sejak();
var G0 = { owner: true, sumber: 'firestore', koleksiSiap: 30, koleksiTotal: 30, dariCache: 0, ditolak: 0, online: true };
var g = function (ubah) { return kkBolehTerbit(Object.assign({}, G0, ubah || {})); };
ok('gerbang: semua syarat → boleh', g().boleh === true, J(g()));
[['bukan owner', { owner: false }], ['cadangan (bukan Firestore)', { sumber: 'cadangan' }], ['tidak tersambung', { online: false }], ['ada koleksi ditolak server', { ditolak: 1 }],
 ['data belum termuat semua', { koleksiSiap: 29 }], ['sebagian data salinan perangkat', { dariCache: 1 }]].forEach(function (x) { var r = g(x[1]); ok('gerbang: ' + x[0] + ' → TIDAK terbit, sebabnya disebut', r.boleh === false && !!r.sebab, J(r)); });
kkSetelServer(D, false); ok('gerbang: katalog server baru terbaca dari salinan perangkat → TIDAK terbit', g().boleh === false);
kkLupakanServer(); ok('gerbang: katalog server belum terbaca → TIDAK terbit', g().boleh === false);
// ---- 6 · Beranda
var T0 = '2026-09-19T02:00:00.000Z'; kkSetelServer(kkDokumen(kkIsi(), T0), true);
var hp = function (id, apl, v, pada, kat) { var x = { id: id, nama: id, aplikasi: apl, versi: v, pada: pada, antrean: 0, gagal: 0 }; if (kat !== undefined) x.katalog = kat; return x; };
pasok('perangkatStatus', [hp('d-v26', 'darurat', 'kasir-v26', '2026-09-19T02:50:00.000Z', undefined), hp('d-segar', 'darurat', 'kasir-v32', '2026-09-19T02:50:00.000Z', T0),
  hp('d-basi', 'darurat', 'kasir-v32', '2026-09-19T02:50:00.000Z', '2026-09-18T01:00:00.000Z'), hp('d-baru-saja', 'darurat', 'kasir-v32', '2026-09-19T02:03:00.000Z', '2026-09-18T01:00:00.000Z'),
  hp('k-kalk', 'kasir', 'kasir-v30', '2026-09-19T02:50:00.000Z', undefined), hp('d-v27', 'darurat', 'kasir-v27', '2026-09-19T02:50:00.000Z', T0), hp('d-v27-basi', 'darurat', 'kasir-v27', '2026-09-19T02:50:00.000Z', '2026-09-18T01:00:00.000Z'), hp('d-v24', 'darurat', 'kasir-v24', '2026-09-19T02:50:00.000Z', undefined), hp('d-jauh', 'darurat', 'kasir-v26', '2026-09-01T02:50:00.000Z', undefined)]);
var B = kkBeranda(new Date(__KINI)); var tk = B.perhatian.map(function (x) { return x.teks; }).join(' | ');
ok('Beranda: "Katalog kasir: diperbarui <tanggal jam WIB> · sama dengan data sekarang"', /^Katalog kasir: diperbarui .*09\.00 · sama dengan data sekarang$/.test(B.status) || /^Katalog kasir: diperbarui .* · sama dengan data sekarang$/.test(B.status), B.status);
ok('Beranda: HP kasir versi 26 disebut (harga baru baru sampai saat dibuka ulang); HP v24 & yang tidak berdenyut 7 hari TIDAK disebut di sini', /HP d-v26 · kasir darurat: masih kasir-v26 — harga baru baru sampai saat aplikasinya dibuka ulang/.test(tk) && !/d-v24|d-jauh/.test(tk), tk);
ok('Beranda: HP penjaga yang berdenyut > 6 menit sesudah katalog terbit tapi memegang katalog lama → disebut, awas', B.perhatian.some(function (x) { return /HP d-basi · kasir darurat: masih memegang katalog/.test(x.teks) && x.awas; }), tk);
ok('Beranda: HP yang memegang katalog terbaru, yang baru saja berdenyut, dan kasir.html (pensiun 3 Okt; k-kalk masih kasir-v30, tanpa cap katalog) TIDAK disebut', !/d-segar|d-baru-saja|k-kalk/.test(tk), tk);
ok('Beranda 39b no. 4: HP v27 (sudah ambil katalog sendiri, belum versi terbaru) disebut "versi kasir-v32 terpasang saat dibuka ulang" tanpa awas — BUKAN "harga baru baru sampai"', B.perhatian.some(function (x) { return /^HP d-v27 · kasir darurat: masih kasir-v27 — versi kasir-v32 terpasang saat aplikasinya dibuka ulang$/.test(x.teks) && !x.awas; }) && !/d-v27[^|]*harga baru baru sampai/.test(tk), tk);
ok('Beranda 39b no. 4: HP v27 yang memegang katalog lama TETAP disebut memegang katalog lama (awas) — pemeriksaannya tidak berhenti di versi', B.perhatian.some(function (x) { return /HP d-v27-basi · kasir darurat: masih memegang katalog/.test(x.teks) && x.awas; }) && !B.perhatian.some(function (x) { return /HP d-v27 · kasir darurat: masih memegang katalog/.test(x.teks); }), tk);
terapkanKeCache([{ koleksi: 'katalogHargaLiteran', data: { id: 'Angsa', merk: 'Angsa', hargaPerLiter: 13500, diubahPada: '2026-09-19T03:00:00.000Z' } }]);
B = kkBeranda(new Date(__KINI));
ok('Beranda: ada perubahan yang belum sampai → status menyebutnya + satu baris Perlu perhatian', /BELUM sampai/.test(B.status) && B.perhatian.some(function (x) { return /belum sampai ke HP kasir/.test(x.teks); }), J(B));
kkCatatTerbit('', 'permission-denied'); B = kkBeranda(new Date(__KINI));
ok('Beranda: terbit gagal → barisnya awas & menyebut sebabnya', B.awas && B.perhatian.some(function (x) { return /permission-denied/.test(x.teks) && x.awas; }), J(B));
kkLupakanServer(); ok('Beranda: server belum terbaca → "belum terbaca dari server", tidak menebak', kkBeranda(new Date(__KINI)).status === 'Katalog kasir: belum terbaca dari server');
// ---- 7 · (pensiun 3 Okt 2026) penjaga tulis index.html dihapus bersama objeknya
print(J({ lulus: lulus, gagal: gagal }));
"""

def fungsi(teks, nama):
    """Badan fungsi (juga `export async function`) sampai kurung kurawal penutupnya — '' kalau tidak ada."""
    m = re.search(r'(?:^|\n)(?:export\s+)?(?:async\s+)?function\s+' + re.escape(nama) + r'\s*\(', teks)
    return (beku2.potong(teks[m.start():].replace('export ', '', 1), nama) or '') if m else ''


def jalan_jsc(t):
    # penyusun sistem lama = susunIsiKatalogKasir pembantu.js, HANYA kalau masih terkunci sidik (pembantu.sha256 = byte-sama index.html 48a694d).
    # Sidik lepas → pembanding tidak sah (tanpa kunci itu fungsi yang diuji dibandingkan dengan dirinya sendiri).
    pb = t['baru/js/mesin/pembantu.js']; lama = beku2.potong(pb, 'susunIsiKatalogKasir')
    if not lama or not beku2.terkunci('susunIsiKatalogKasir', pb): return 0, ['susunIsiKatalogKasir() pembantu.js tidak ada / sidiknya lepas dari pembantu.sha256 — pembanding sistem lama tidak sah']
    kl = list(KUNCI_LAMA)
    cad = None; nama_cad = ''
    p = cadangan_toko()
    if p:
        d = json.load(open(p, encoding='utf-8')); nama_cad = os.path.basename(p)
        kol = re.findall(r"\{ nama: '(\w+)'", t['baru/js/data/koleksi.js'])
        cad = dict((n, d[n]) for n in kol if isinstance(d.get(n), list))
    js = '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL])
    isi = (JAM + js + '\n' + lama.replace('function susunIsiKatalogKasir(', 'function susunIsiKatalogKasirLama(', 1)
           + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar KUNCI_LAMA = ' + json.dumps(kl) + ';\nvar CADANGAN = ' + json.dumps(cad) + ';\nvar NAMA_CADANGAN = ' + json.dumps(nama_cad)
           + ';\n' + SKENARIO)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(isi); jalur = f.name
    r = subprocess.run([JSC, jalur], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(jalur)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(baris[-1]); return h['lulus'], h['gagal']


# (pensiun 3 Okt 2026) buku kecil pembayaran bon kasir.html (39b no. 4, jsc atas fungsi asli kasir.html) dihapus bersama kasir.html.


def periksa_statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    # sampai 2 Okt: HURUF DEMI HURUF dengan teks index.html; sejak sistem lama pensiun (3 Okt) pembandingnya kunci sidik pembantu.sha256
    ok('penyusun isi katalog /baru/ (pembantu.js) = susunIsiKatalogKasir() sistem lama: terkunci sidik (pembantu.sha256)', beku2.terkunci('susunIsiKatalogKasir', t['baru/js/mesin/pembantu.js']))
    fb = t['baru/js/data/firebase.js']; tb = fungsi(fb, 'tulisBerkas')
    i_mentah = tb.find('if (kkMentah(x.koleksi)) { b.set(doc(db, x.koleksi, String(x.data.id)), x.data); ditulis.push({ koleksi: x.koleksi, data: x.data }); return; }')
    ok('penulis pusat: dokumen katalog ditulis APA ADANYA sebelum atribusi & baris jejak', i_mentah >= 0 and i_mentah < tb.find('beriAtribusiAkun(x.data'))
    pn = fungsi(fb, 'terbitkanKatalogOtomatis')
    ok('penerbit otomatis: lewat gerbang kkBolehTerbit, hanya kalau isi BERBEDA (kkTertinggal(isi) === true), setDoc bentuk kkDokumen, tanpa jejak',
       'const g = gerbangKatalog();' in pn and 'return kkBolehTerbit(' in fungsi(fb, 'gerbangKatalog') and 'if (!g.boleh) return;' in pn and "kkTertinggal(isi) !== true) return;" in pn and 'setDoc(doc(db, KK_KOLEKSI, KK_ID), kkDokumen(isi, kini))' in pn and 'KOLEKSI_LOG' not in pn, pn[:200])
    ok('39b-17: terbit harga (kkSertakan) memakai gerbang yang SAMA dengan terbit otomatis — firebase.js memasang gerbangKatalog lewat kkPasangGerbang; kkSertakan berhenti bila gerbang tertutup / tanpa penilai',
       'kkPasangGerbang(gerbangKatalog);' in fb and "const g = _kkGerbang ? _kkGerbang() : null; if (!g || !g.boleh) return daftar;" in t['baru/js/data/katalog-kasir.js'] if 'baru/js/data/katalog-kasir.js' in t else False)
    ok('pendengar dokumen katalog hanya dipasang untuk owner; penerbit dijadwalkan tiap data berubah (dengarkan) dan saat sinyal kembali',
       "if (akun.jenis === 'owner') pasangPendengarKatalog();" in fb and 'dengarkan(() => jadwalkanKatalog())' in fb and 'pasangDenyut(); pasangPenerbitKatalog();' in fb)
    ok('pendengar koleksi mencatat mana yang masih salinan perangkat (fromCache) — gerbang terbit membacanya', '_dariCache[k.nama] = !!(snap.metadata && snap.metadata.fromCache);' in fb)
    ok('harga.js: terbit harga menyertakan katalog kasir di kiriman yang SAMA (kkSertakanKiriman → kkSertakan)', re.search(r"hgTerbitkan: async \(\) => \{[^\n]*tulis\(kkSertakanKiriman\(r, waktu\(\)\.kini\)\)", t['baru/js/layar/harga.js']) and 'const dokumen = kkSertakan(r.dokumen, kini);' in t['baru/js/data/katalog-kasir.js'])
    ok('Beranda: baris katalog kasir (kkBeranda → #rkKatalog) & perhatiannya ikut di Perlu perhatian', 'kkBeranda(k)' in t['baru/js/layar/ringkasan.js'] and "$('rkKatalog').textContent = KK ? KK.status : ''" in t['baru/js/layar/ringkasan.js'] and 'KK ? KK.perhatian : []' in t['baru/js/layar/ringkasan.js'])
    d = t[DARURAT]
    ok('kasir darurat: katalog diambil saat layar dinyalakan & tiap 5 menit selagi terlihat (jadwal denyut)',
       "document.addEventListener('visibilitychange', function () { if (!document.hidden) segarkanRingkasanD(); });" in d and "setInterval(function () { if (!document.hidden) segarkanRingkasanD(); }, 300000);" in d)
    ok('kasir darurat: denyut membawa cap katalog yang dipegang; katalog berganti → denyut segera', 'katalog: katalogDipegangD()' in d and 'if (katalogDipegangD() !== tadi) { denyutTerakhirD = 0; kirimDenyutD(); }' in d)
    vs = re.search(r"const VERSI = '([^']+)';", t['sw-kasir.js']); kk = re.search(r"export const KK_VERSI_KASIR_TERBARU = '([^']+)';", t['baru/js/data/katalog-kasir.js'])
    va = [re.search(r"var VERSI_APLIKASI = '([^']+)';", t[b]) for b in (DARURAT,)]
    kp = re.search(r"export const KP_VERSI_KASIR_25B = '([^']+)';", t['baru/js/data/kunci-periode.js'])
    nomor = lambda m: int(re.match(r'kasir-v(\d+)$', m.group(1)).group(1)) if m else -1
    ok('versi: kasir darurat = VERSI sw-kasir.js = KK_VERSI_KASIR_TERBARU (/baru/) = ' + VERSI_KASIR, vs and kk and all(v and v.group(1) == vs.group(1) for v in va) and kk.group(1) == vs.group(1) == VERSI_KASIR, [x.group(1) if x else None for x in [vs, kk] + va])
    ok('versi: lantai kunci bulan (KP_VERSI_KASIR_25B) tidak di atas versi yang disajikan sw-kasir.js', kp and vs and 0 < nomor(kp) <= nomor(vs), kp.group(1) if kp else None)
    out += UA.periksa_salinan(t[DARURAT], lambda: salinan_peramban(t[DARURAT]), SKENARIO_PERAMBAN, UA.PENJAGA_CSP)
    return out


# ---------- PERAMBAN: kasir darurat SUNGGUHAN, katalog berganti di server palsu ----------
KEPALA = r"""<script>
(function () {
  try { delete Navigator.prototype.serviceWorker; } catch (e) {}
  var s = new URLSearchParams(location.search).get('s') || '';
  // jadwal 5 menit (denyut & katalog) DIPERCEPAT hanya di skenario berkala — skenario "layar dinyalakan" memakai jadwal asli
  if (s === 'berkala') { var si = window.setInterval.bind(window); window.setInterval = function (f, ms) { return si(f, ms === 300000 ? 500 : ms); }; }
  var K = window.__kat = { get: 0, denyut: [], dok: null };
  var H = { nyala: [70000, '2026-09-27T01:00:00.000Z'], berkala: [73000, '2026-09-27T03:00:00.000Z'] }[s] || [70000, '2026-09-27T01:00:00.000Z'];
  K.pasang = function (harga, cap) { K.dok = { id: 'aktif', diperbaruiPada: cap, kemasan: [{ kunci: 'Beras Uji|5', namaProduk: 'Beras Uji', ukuran: 5, sisaUnit: 10, hppPerUnit: 60000, hargaPerUnit: harga }], merkKarung: [], bahanLiteran: {}, piutang: [] }; };
  K.pasang(H[0], H[1]);
  localStorage.setItem('kasir_auth_v1', JSON.stringify({ refreshToken: 'r-uji', idToken: 't-uji', kedaluwarsa: Date.now() + 3600000 }));
  if (s === 'nyala') { localStorage.removeItem('kasir_ringkasan_v1'); localStorage.removeItem('kasir_ringkasan_disegarkan'); }
  function fs(v) { if (v === null || v === undefined) return { nullValue: null }; if (typeof v === 'boolean') return { booleanValue: v }; if (typeof v === 'number') return Number.isInteger(v) ? { integerValue: String(v) } : { doubleValue: v };
    if (typeof v === 'string') return { stringValue: v }; if (Array.isArray(v)) return { arrayValue: { values: v.map(fs) } }; var f = {}; for (var k in v) f[k] = fs(v[k]); return { mapValue: { fields: f } }; }
  function nilai(v) { if (!v) return null; if ('stringValue' in v) return v.stringValue; if ('integerValue' in v) return Number(v.integerValue); if ('doubleValue' in v) return v.doubleValue; if ('booleanValue' in v) return v.booleanValue; return null; }
  function jawab(status, isi) { return Promise.resolve(new Response(JSON.stringify(isi || {}), { status: status, headers: { 'Content-Type': 'application/json' } })); }
  var asli = window.fetch.bind(window);
  window.fetch = function (url, opsi) {
    url = String(url); opsi = opsi || {};
    if (url.charAt(0) === '/' || url.indexOf(location.origin) === 0) return asli(url, opsi);
    var m = /\/documents\/([^/?]+)\/([^?]+)/.exec(url); if (!m) return jawab(404, {});
    var metode = String(opsi.method || 'GET').toUpperCase();
    if (metode === 'GET' && m[1] === 'ringkasanKasir' && m[2] === 'aktif') { K.get++; var f = {}; for (var k in K.dok) f[k] = fs(K.dok[k]); return jawab(200, { name: 'x/ringkasanKasir/aktif', fields: f }); }
    if (m[1] === 'perangkatStatus') { var d = {}; try { var ff = JSON.parse(opsi.body).fields || {}; for (var k2 in ff) d[k2] = nilai(ff[k2]); } catch (e) {} K.denyut.push(d); return jawab(200, {}); }
    if (metode === 'GET') return jawab(404, { error: { code: 404, status: 'NOT_FOUND' } });
    return jawab(200, { name: 'dok', fields: {} });
  };
})();
</script>"""

SKENARIO_PERAMBAN = r"""<script>
(async function () {
  var tunggu = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  var sampai = async function (f, ms) { var t0 = Date.now(); while (Date.now() - t0 < (ms || 6000)) { try { if (f()) return true; } catch (e) {} await tunggu(40); } return false; };
  var K = window.__kat; var hasil = {}; var s = new URLSearchParams(location.search).get('s') || '';
  var harga = function () { return (window.daftarProdukD || []).map(function (q) { return q.harga; }); };
  try {
    hasil.kanari = window.__csp ? await window.__csp.kanari() : null;   // owner 3 Okt (perkuat): CSP halaman berlaku & pendengar pelanggaran hidup
    if (s === 'nyala') {
      await sampai(function () { return harga()[0] === 70000; }, 10000); hasil.awal = harga(); hasil.getAwal = K.get;
      K.pasang(72000, '2026-09-27T02:00:00.000Z');                      // owner menerbitkan harga baru dari /baru/
      await tunggu(1500); hasil.tanpaPemicu = harga();                  // tanpa layar dinyalakan & sebelum 5 menit: masih harga lama
      document.dispatchEvent(new Event('visibilitychange'));            // layar HP dinyalakan lagi — aplikasi TIDAK dibuka ulang
      await sampai(function () { return harga()[0] === 72000; }, 6000); hasil.sesudahNyala = harga(); hasil.getAkhir = K.get;
      await sampai(function () { return K.denyut.some(function (d) { return d.katalog === '2026-09-27T02:00:00.000Z'; }); }, 4000);
      hasil.denyutKatalog = K.denyut.map(function (d) { return d.katalog === undefined ? '(tanpa field)' : d.katalog; });
      hasil.label = (document.getElementById('versiApp') || {}).textContent || '';
    } else if (s === 'berkala') {
      await sampai(function () { return harga()[0] === 73000; }, 10000); hasil.awal = harga();
      K.pasang(74000, '2026-09-27T04:00:00.000Z');                      // tanpa ketukan & tanpa layar dinyalakan
      await sampai(function () { return harga()[0] === 74000; }, 6000); hasil.sesudahJadwal = harga();
    }
  } catch (e) { hasil.galat = String(e && (e.stack || e.message) || e); }
  await tunggu(100); hasil.cspLain = window.__csp ? window.__csp.lain() : null;
  try { await fetch('/_hasil' + location.search, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(hasil) }); } catch (e) {}
  fetch('/_siap');
  var lanjut = new URLSearchParams(location.search).get('lanjut');
  if (lanjut) location.replace(lanjut);
})();
</script>"""


def salinan_peramban(s):
    """Teks salinan uji peramban — tanpa menulis atau menyalakan apa pun (dipakai periksa_peramban DAN pemeriksaan statis). Kasir darurat ber-CSP
    (kasir-v32): SKENARIO_PERAMBAN yang disuntik sesudah meta ikut DI-HASH ke script-src salinan, hash halaman tetap (dihitung ulang hanya kalau kontrol
    mengubah halaman), TANPA 'unsafe-inline' (owner 3 Okt, perkuat — uji_antrean_kasir.csp_salinan). PENJAGA_CSP & KEPALA disisip SEBELUM meta."""
    assert s.count('<head>') == 1 and s.count('</body>') == 1
    s = UA.csp_salinan(s, SKENARIO_PERAMBAN, UA._asli())
    return s.replace('<head>', '<head>' + UA.PENJAGA_CSP + KEPALA, 1).replace('</body>', SKENARIO_PERAMBAN + "<img src='/_tahan' alt='' style='display:none'></body>", 1)


def periksa_peramban(t):
    out = []; ok = lambda n, c, k='': out.append(('peramban · ' + n, bool(c), k))
    if not CHROME: return [('peramban · Google Chrome tersedia', False, 'tidak ditemukan')]
    s = salinan_peramban(t[DARURAT]); d = tempfile.mkdtemp(prefix='katalog-')
    open(os.path.join(d, DARURAT), 'w', encoding='utf-8').write(s)
    srv, port, keadaan = layani(d); profil = tempfile.mkdtemp(prefix='katalog-profil-')
    try:
        a, b = buka(port, keadaan, profil, '/' + DARURAT + '?s=nyala', lalu='/' + DARURAT + '?s=berkala')
    finally:
        srv.shutdown(); shutil.rmtree(profil, ignore_errors=True); shutil.rmtree(d, ignore_errors=True)
    N, B = hasil_dari(a), hasil_dari(b)
    if not N or N.get('galat'): return [('peramban · skenario layar dinyalakan jalan', False, {'galat': (N or {}).get('galat', 'tidak ada hasil'), 'cspLain': (N or {}).get('cspLain')})]
    UA.periksa_csp(ok, 'layar dinyalakan', N)
    ok('HP penjaga memuat katalog saat dibuka (tuts bernama berharga 70.000)', N['awal'] == [70000], N)
    ok('katalog berganti di server: tanpa pemicu harga tuts TETAP yang lama (bukti pemicunya layar dinyalakan, bukan kebetulan)', N['tanpaPemicu'] == [70000], N)
    ok('layar HP dinyalakan → harga baru 72.000 TANPA membuka ulang aplikasi', N['sesudahNyala'] == [72000] and N['getAkhir'] > N['getAwal'], N)
    ok('denyut HP penjaga membawa cap katalog yang baru dipegangnya', '2026-09-27T02:00:00.000Z' in N['denyutKatalog'], N['denyutKatalog'])
    ok('bilah atas: "versi 3 Okt b"', N.get('label') == 'versi 3 Okt b', N.get('label'))
    if not B or B.get('galat'): return out + [('peramban · skenario berkala jalan', False, {'galat': (B or {}).get('galat', 'tidak ada hasil'), 'cspLain': (B or {}).get('cspLain')})]
    UA.periksa_csp(ok, 'berkala', B)
    ok('tanpa ketukan apa pun: katalog baru (74.000) diambil sendiri di jadwal berkala', B['awal'] == [73000] and B['sesudahJadwal'] == [74000], B)
    return out


def semua(ganti=None, bagian=('statis', 'jsc', 'peramban')):
    """ganti = {berkas: [(lama, baru)]} (kontrol); kunci '@nama' = global uji_antrean_kasir (UA.ganti_alat — mis. csp_salinan, PENJAGA_CSP)."""
    ganti = ganti or {}
    with UA.ganti_alat(dict((k[1:], v) for k, v in ganti.items() if k.startswith('@')), UA):
        return _semua(dict((k, v) for k, v in ganti.items() if not k.startswith('@')), bagian)


def _semua(ganti, bagian):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        l, g = jalan_jsc(t); out += [('jsc · ' + x, False, '') for x in g] + [('jsc · %d skenario' % l, l > 0 and not g, '')]
        out.append(('__jsc_lulus', True, l))
    if 'peramban' in bagian: out += periksa_peramban(t)
    return out


KONTROL = [
    ('penyusun /baru/ beda dari sistem lama (modal kemasan dinolkan; sidik pembantu)', {'baru/js/mesin/pembantu.js': [("hppPerUnit: s.hppRataRataPerUnit || 0, hargaPerUnit: h ? h.hargaPerUnit : 0 };", "hppPerUnit: 0, hargaPerUnit: h ? h.hargaPerUnit : 0 };")]}, ('statis', 'jsc')),
    ('dokumen katalog berurutan lain', {'baru/js/data/katalog-kasir.js': [("return { id: KK_ID, diperbaruiPada: kini, kemasan: isi.kemasan, merkKarung: isi.merkKarung,", "return { diperbaruiPada: kini, id: KK_ID, kemasan: isi.kemasan, merkKarung: isi.merkKarung,")]}, ('jsc',)),
    ('pembanding tertipu urutan kunci Firestore', {'baru/js/data/katalog-kasir.js': [("return JSON.stringify(kkUrut({ kemasan:", "return JSON.stringify(({ kemasan:")]}, ('jsc',)),
    ('katalog "seandainya" dari cache SEBELUM kiriman', {'baru/js/data/katalog-kasir.js': [("const isi = denganCacheSementara(daftar, kkIsi); if (!isi) return daftar;", "const isi = kkIsi(); if (!isi) return daftar;")]}, ('jsc',)),
    ('cache tidak dikembalikan sesudah "seandainya"', {'baru/js/data/toko.js': [("try { return fn(); } finally { Object.keys(simpan).forEach((c) => { _cache[c] = simpan[c]; }); _versiCache += 1; }", "return fn();")]}, ('jsc',)),
    ('39b-17: kabar tetap bilang katalog ikut walau gerbang tertutup', {'baru/js/data/katalog-kasir.js': [("if ((g && g.boleh) || dokumen.some((d) => d.koleksi === KK_KOLEKSI)", "if (true || dokumen.some((d) => d.koleksi === KK_KOLEKSI)")]}, ('jsc',)),
    ('terbit harga tidak menyertakan katalog kasir', {'baru/js/layar/harga.js': [("hgTerbitkan: async () => { const r = HG.susunTerbit(waktu(), st().yakinRugi); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, yakinRugi: !!r.perluYakin }); if (await tulis(kkSertakanKiriman(r, waktu().kini)))", "hgTerbitkan: async () => { const r = HG.susunTerbit(waktu(), st().yakinRugi); if (r.tolak) return set({ kabar: r.tolak, kabarAwas: true, yakinRugi: !!r.perluYakin }); if (await tulis(r))")]}, ('statis',)),
    ('gerbang terbit dari salinan perangkat', {'baru/js/data/katalog-kasir.js': [("if (k.dariCache > 0) return", "if (false) return")]}, ('jsc',)),
    ('gerbang terbit tanpa katalog server terbaca', {'baru/js/data/katalog-kasir.js': [("if (_kkServer.ada === null || !_kkServer.dariServer) return", "if (false) return")]}, ('jsc',)),
    ('katalog ditulis dengan atribusi & jejak', {'baru/js/data/firebase.js': [("    if (kkMentah(x.koleksi)) { b.set(doc(db, x.koleksi, String(x.data.id)), x.data); ditulis.push({ koleksi: x.koleksi, data: x.data }); return; }", "")]}, ('statis',)),
    ('penerbit otomatis terbit walau isinya sama', {'baru/js/data/firebase.js': [("if (!isi || kkTertinggal(isi) !== true) return;", "if (!isi) return;")]}, ('statis',)),
    # (pensiun 3 Okt 2026) kontrol penjaga tulis index.html, buku kecil bayar bon kasir.html, dan K2 (waktu server katalog darurat) dihapus bersama objeknya
    ('Beranda diam soal perubahan yang belum sampai', {'baru/js/data/katalog-kasir.js': [("  if (tg) out.push({ teks: 'Katalog kasir: ada perubahan", "  if (false) out.push({ teks: 'Katalog kasir: ada perubahan")]}, ('jsc',)),
    ('HP penjaga yang masih memegang katalog lama tidak disebut', {'baru/js/data/katalog-kasir.js': [("(!isFinite(pegang) || pegang < terbitMs)", "false")]}, ('jsc',)),
    ('kasir darurat tidak mengambil katalog saat layar dinyalakan', {DARURAT: [("document.addEventListener('visibilitychange', function () { if (!document.hidden) segarkanRingkasanD(); });\n", "")]}, ('statis', 'peramban')),
    ('kasir darurat tidak mengambil katalog berkala', {DARURAT: [("setInterval(function () { if (!document.hidden) segarkanRingkasanD(); }, 300000);\n", "")]}, ('statis', 'peramban')),
    ('denyut tanpa cap katalog', {DARURAT: [("    versi: VERSI_APLIKASI,\n    katalog: katalogDipegangD()", "    versi: VERSI_APLIKASI")]}, ('statis', 'peramban')),
    ('sw-kasir.js naik tanpa /baru/ ikut', {'sw-kasir.js': [("const VERSI = 'kasir-v32';", "const VERSI = 'kasir-v33';")]}, ('statis',)),
    ('Beranda menyebut lagi perangkat kasir.html yang sudah pensiun', {'baru/js/data/katalog-kasir.js': [("    if (kpNamaAplikasiKasir(p) === 'kasir') return;\n", "")]}, ('jsc',)),
    ('dokumen katalog tanpa bagian piutang (bentuk sistem lama berubah)', {'baru/js/data/katalog-kasir.js': [(", piutang: isi.piutang", "")]}, ('jsc',)),
    ('persis: dokumen katalog tanpa daftar id', {'baru/js/data/katalog-kasir.js': [(", bayarBonTerhitung: isi.bayarBonTerhitung || [], bayarBonSejak:", ", bayarBonSejak:")]}, ('jsc',)),
    ('persis: daftar id tidak ikut pembanding katalog (tidak terbit ulang)', {'baru/js/data/katalog-kasir.js': [(", bayarBonTerhitung: d.bayarBonTerhitung || [], bayarBonSejak:", ", bayarBonSejak:")]}, ('jsc',)),
    ('persis: daftar id kembali berjendela jam perangkat', {'baru/js/data/katalog-kasir.js': [("m.tipe === 'bayar' && kunciPelanggan(m.namaPelanggan)).map(", "m.tipe === 'bayar' && kunciPelanggan(m.namaPelanggan) && (m.tanggal || '') >= new Date(Date.now() - 45 * 86400000).toISOString().slice(0, 10)).map(")]}, ('jsc',)),
    ('persis: tanda awal buku tidak ikut dokumen', {'baru/js/data/katalog-kasir.js': [(", bayarBonSejak: isi.bayarBonSejak || '' };", " };")]}, ('jsc',)),
    ('persis: pembayaran tanpa nama ikut daftar (tidak dihitung hitungPiutang)', {'baru/js/data/katalog-kasir.js': [("m.tipe === 'bayar' && kunciPelanggan(m.namaPelanggan)).map(", "m.tipe === 'bayar').map(")]}, ('jsc',)),
    # owner 3 Okt (perkuat): salinan uji kembali dilonggarkan ke 'unsafe-inline' — statis (CSP salinan) & peramban (kanari ikut jalan)
    ("salinan uji kembali melonggarkan script-src ke 'unsafe-inline' (statis)", {'@csp_salinan': UA._salinan_longgar}, ('statis',)),
    ("salinan uji kembali melonggarkan script-src ke 'unsafe-inline' (peramban: kanari ikut jalan)", {'@csp_salinan': UA._salinan_longgar}, ('peramban',)),
    ('HP v27 disebut "harga baru baru sampai" lagi (lantai ambil-sendiri disamakan dengan versi terbaru)', {'baru/js/data/katalog-kasir.js': [("export const KK_VERSI_AMBIL_SENDIRI = 'kasir-v27';", "export const KK_VERSI_AMBIL_SENDIRI = 'kasir-v32';")]}, ('jsc',)),
]

if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti, bagian in KONTROL:
            try: h = semua(ganti, bagian)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' · ' + str(e)[:120]); kode = 3; continue
            g = [x for x in h if not x[1]]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:120] if g else '-'))
            if not g: kode = 3
        print(teks_stat())
        sys.exit(kode)
    h = semua(); g = [x for x in h if not x[1]]
    jsc_l = next((x[2] for x in h if x[0] == '__jsc_lulus'), 0); tampak = [x for x in h if x[0] != '__jsc_lulus']
    for n, _, k in g: print('   ✗ ' + n + (' → ' + json.dumps(k, ensure_ascii=False)[:400] if k not in ('', None) else ''))
    n_lulus = len([x for x in tampak if x[1]]) - 1 + jsc_l
    print('KATALOG KASIR dari /baru/ (25c)%s: %d lulus · %d gagal' % (' + cadangan ' + os.path.basename(cadangan_toko()) if cadangan_toko() else '', n_lulus, len(g)))
    print(teks_stat())
    sys.exit(1 if g else 0)
