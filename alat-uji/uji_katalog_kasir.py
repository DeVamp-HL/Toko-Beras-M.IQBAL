#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_katalog_kasir.py — putaran 25c Bagian A: KATALOG KASIR (ringkasanKasir/aktif) DITERBITKAN /baru/, bentuk tetap (keputusan owner 27 Sep 2026).

STATIS:
  · penyusun isi di /baru/ (baru/js/mesin/pembantu.js) HURUF DEMI HURUF sama dengan susunIsiKatalogKasir() index.html (disalin pindah_mesin.py)
  · dokumen: kunci & urutannya dibaca dari setDoc di terbitkanRingkasanKasir() index.html (dibandingkan di jsc dengan kkDokumen)
  · firebase.js: katalog ditulis APA ADANYA (tanpa atribusi/jejak) di penulis pusat; penerbit otomatis lewat gerbang kkBolehTerbit, hanya kalau isinya
    berbeda; pendengar dokumen katalog hanya untuk owner; terbit tiap data berubah (dengarkan)
  · harga.js: terbit harga menyertakan katalog (kkSertakan) di kiriman yang SAMA
  · index.html: penulis lama DITUTUP tanpa modal (JALUR_DIAM), tombol "Terbitkan katalog sekarang" tidak menulis
  · kasir darurat (izin owner 27 Sep): ambil katalog saat layar dinyalakan & tiap 5 menit; denyut membawa cap katalog; versi kedua berkas kasir =
    VERSI sw-kasir.js = KK_VERSI_KASIR_TERBARU (/baru/); lantai kunci bulan (KP_VERSI_KASIR_25B) tidak di atas versi yang disajikan
JSC (KOTAK PASIR — angka & nama contoh; + cadangan toko kalau ada di _privat/, lokal saja):
  · isi /baru/ == isi fungsi index.html (dijalankan dari teks index.html) untuk data yang sama — kotak pasir & cadangan toko
  · kunci dokumen = urutan index.html; pembanding tidak tertipu urutan kunci peta dari Firestore; server belum terbaca = "belum tahu"
  · terbit harga → katalog SESUDAH terbit ikut di daftar dokumen yang sama; cache tidak berubah; isinya = katalog sesudah kiriman ditulis
  · tiap kejadian di peta §2 (barang masuk, adukan, nota, bayar bon, beli kantong, terbit harga) membuat katalog "tertinggal"
  · gerbang terbit: owner · Firestore · online · tanpa koleksi ditolak · semua termuat · semua dari SERVER · katalog server terbaca
  · Beranda: "katalog kasir: diperbarui …", perubahan yang belum sampai, HP kasir versi lama, HP penjaga yang masih memegang katalog lama
  · index.html (penjagaTulis dari teks index.html): katalog ditolak TANPA modal; jenis beras / operator / PIN owner ditolak DENGAN modal yang menunjuk
    /baru/; pulihkan (mode pulih) tetap lolos; denyut tetap jalan
PERAMBAN (Chrome headless, SATU peluncuran; kasir-darurat-nominal.html SUNGGUHAN + Firestore REST palsu):
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

JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/arsip-logika.js', 'baru/js/data/katalog-kasir.js', 'baru/js/layar/harga-logika.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/struk-logika.js', 'baru/js/layar/jual-logika.js', 'baru/js/layar/wadah-bernama-logika.js', 'baru/js/layar/stok-adukan-logika.js', 'baru/js/layar/setengah-logika.js']
BERKAS = ['index.html', 'baru/js/mesin/pembantu.js', 'baru/js/data/firebase.js', 'baru/js/layar/harga.js', 'baru/js/layar/ringkasan.js', 'kasir-darurat-nominal.html',
          'kasir.html', 'sw-kasir.js', 'baru/js/data/kunci-periode.js'] + MODUL
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


def modul_index(t):
    s = t['index.html']; return s[s.index('<script type="module">'):s.rindex('</script>')]


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
// ---- 1 · isi byte-sama dengan penyusun index.html (fungsi LAMA dijalankan dari teks index.html)
var I = kkIsi(); var LAMA = susunIsiKatalogKasirLama();
var I0 = I ? JSON.parse(J(I)) : null; if (I0) { delete I0.bayarBonTerhitung; delete I0.bayarBonSejak; }
ok('isi katalog /baru/ = isi susunIsiKatalogKasir() index.html untuk data yang sama (JSON persis, urutan ikut) + DUA kunci paling akhir bayarBonTerhitung & bayarBonSejak (cara persis, owner 30 Sep)', !!I && J(I0) === J(LAMA) && J(Object.keys(I).slice(-2)) === J(['bayarBonTerhitung', 'bayarBonSejak']) && Array.isArray(I.bayarBonTerhitung) && I.bayarBonSejak === '', J(I0).slice(0, 300) + ' ≠ ' + J(LAMA).slice(0, 300));
ok('isi memuat keempat bagian index.html: kemasan, merkKarung (+ modal & harga), bahanLiteran, piutang (yang masih bersisa)', !!I && I.kemasan.length === 1 && I.kemasan[0].namaProduk === 'Kembang' && I.kemasan[0].hargaPerUnit === 75000
  && I.merkKarung.some(function (m) { return m.merk === 'Angsa' && m.hargaPerKg === 13800 && m.hargaPerLiter === 12500 && m.hargaKarung50 === 700000 && m.hppPerKg > 0; })
  && I.bahanLiteran.paperbag5l.sisaPcs === 100 && I.bahanLiteran.paperbag5l.hargaPerPcs === 305 && I.piutang.length === 1 && I.piutang[0].nama === 'Pelanggan Contoh' && I.piutang[0].sisa === 150000, J(I));
if (CADANGAN) {
  Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
  var IC = kkIsi(); var LC = susunIsiKatalogKasirLama(); var IM = susunIsiKatalogKasir();
  // 39b (30 Sep): sejak putaran 27 (arsip) & 28 (buku ukuran / stok wadah) katalog HP kasir SENGAJA bukan salinan index.html — yang byte-sama adalah penyusunnya
  // SEBELUM saringan; sesudah saringan, tiap beda wajib punya alasan yang sudah dikunci kotak pasir uji_arsip_produk / uji_buku_ukuran / uji_wadah_stok_sendiri
  ok('DATA TOKO (cadangan ' + NAMA_CADANGAN + '): penyusun /baru/ SEBELUM saringan = isi index.html (JSON persis)', !!IM && J(IM) === J(LC) && IM.merkKarung.length > 0,
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
  ok('DATA TOKO: katalog HP kasir = index.html MINUS nama beras yang diarsipkan (' + hilang.length + ' nama), MINUS buku khusus wadah (' + hilangKhusus.length + ') dan MINUS kolom karung 25 kg yang pindah ke buku ukurannya (' + Object.keys(ukB).length + ' buku); kemasan, bahan literan, piutang sama; tidak ada beda lain',
    hilang.length === Object.keys(arP).filter(function (k) { return k.slice(0, 2) === 'K:'; }).length && hilang.every(function (m) { return arBeras(m, arP); }) && !tambah.length && !bedaLain.length
    && J(IC.kemasan) === J(LC.kemasan) && J(IC.bahanLiteran) === J(LC.bahanLiteran) && J(IC.piutang) === J(LC.piutang), J({ hilang: hilang, tambah: tambah, bedaLain: bedaLain }));
  Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); }); Object.keys(CADANGAN).forEach(function (n) { if (!(n in KOTAK)) pasok(n, []); });
}
// ---- 2 · bentuk dokumen & pembanding
var D = kkDokumen(I, '2026-09-19T03:00:00.000Z');
ok('dokumen: kunci & urutannya = setDoc terbitkanRingkasanKasir() index.html (' + KUNCI_LAMA.join(', ') + ') + bayarBonTerhitung & bayarBonSejak paling akhir, id "aktif"', J(Object.keys(D)) === J(KUNCI_LAMA.concat(['bayarBonTerhitung', 'bayarBonSejak'])) && D.id === 'aktif' && D.diperbaruiPada === '2026-09-19T03:00:00.000Z', J(Object.keys(D)));
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
kkPasangGerbang(function () { return { boleh: true, sebab: '' }; });
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
pasok('perangkatStatus', [hp('d-v26', 'darurat', 'kasir-v26', '2026-09-19T02:50:00.000Z', undefined), hp('d-segar', 'darurat', 'kasir-v30', '2026-09-19T02:50:00.000Z', T0),
  hp('d-basi', 'darurat', 'kasir-v30', '2026-09-19T02:50:00.000Z', '2026-09-18T01:00:00.000Z'), hp('d-baru-saja', 'darurat', 'kasir-v30', '2026-09-19T02:03:00.000Z', '2026-09-18T01:00:00.000Z'),
  hp('k-kalk', 'kasir', 'kasir-v30', '2026-09-19T02:50:00.000Z', undefined), hp('d-v27', 'darurat', 'kasir-v27', '2026-09-19T02:50:00.000Z', T0), hp('d-v27-basi', 'darurat', 'kasir-v27', '2026-09-19T02:50:00.000Z', '2026-09-18T01:00:00.000Z'), hp('d-v24', 'darurat', 'kasir-v24', '2026-09-19T02:50:00.000Z', undefined), hp('d-jauh', 'darurat', 'kasir-v26', '2026-09-01T02:50:00.000Z', undefined)]);
var B = kkBeranda(new Date(__KINI)); var tk = B.perhatian.map(function (x) { return x.teks; }).join(' | ');
ok('Beranda: "Katalog kasir: diperbarui <tanggal jam WIB> · sama dengan data sekarang"', /^Katalog kasir: diperbarui .*09\.00 · sama dengan data sekarang$/.test(B.status) || /^Katalog kasir: diperbarui .* · sama dengan data sekarang$/.test(B.status), B.status);
ok('Beranda: HP kasir versi 26 disebut (harga baru baru sampai saat dibuka ulang); HP v24 & yang tidak berdenyut 7 hari TIDAK disebut di sini', /HP d-v26 · kasir darurat: masih kasir-v26 — harga baru baru sampai saat aplikasinya dibuka ulang/.test(tk) && !/d-v24|d-jauh/.test(tk), tk);
ok('Beranda: HP penjaga yang berdenyut > 6 menit sesudah katalog terbit tapi memegang katalog lama → disebut, awas', B.perhatian.some(function (x) { return /HP d-basi · kasir darurat: masih memegang katalog/.test(x.teks) && x.awas; }), tk);
ok('Beranda: HP yang memegang katalog terbaru, yang baru saja berdenyut, dan kasir kalkulator (tanpa cap katalog) TIDAK disebut', !/d-segar|d-baru-saja|k-kalk/.test(tk), tk);
ok('Beranda 39b no. 4: HP v27 (sudah ambil katalog sendiri, belum versi terbaru) disebut "versi kasir-v30 terpasang saat dibuka ulang" tanpa awas — BUKAN "harga baru baru sampai"', B.perhatian.some(function (x) { return /^HP d-v27 · kasir darurat: masih kasir-v27 — versi kasir-v30 terpasang saat aplikasinya dibuka ulang$/.test(x.teks) && !x.awas; }) && !/d-v27[^|]*harga baru baru sampai/.test(tk), tk);
ok('Beranda 39b no. 4: HP v27 yang memegang katalog lama TETAP disebut memegang katalog lama (awas) — pemeriksaannya tidak berhenti di versi', B.perhatian.some(function (x) { return /HP d-v27-basi · kasir darurat: masih memegang katalog/.test(x.teks) && x.awas; }) && !B.perhatian.some(function (x) { return /HP d-v27 · kasir darurat: masih memegang katalog/.test(x.teks); }), tk);
terapkanKeCache([{ koleksi: 'katalogHargaLiteran', data: { id: 'Angsa', merk: 'Angsa', hargaPerLiter: 13500, diubahPada: '2026-09-19T03:00:00.000Z' } }]);
B = kkBeranda(new Date(__KINI));
ok('Beranda: ada perubahan yang belum sampai → status menyebutnya + satu baris Perlu perhatian', /BELUM sampai/.test(B.status) && B.perhatian.some(function (x) { return /belum sampai ke HP kasir/.test(x.teks); }), J(B));
kkCatatTerbit('', 'permission-denied'); B = kkBeranda(new Date(__KINI));
ok('Beranda: terbit gagal → barisnya awas & menyebut sebabnya', B.awas && B.perhatian.some(function (x) { return /permission-denied/.test(x.teks) && x.awas; }), J(B));
kkLupakanServer(); ok('Beranda: server belum terbaca → "belum terbaca dari server", tidak menebak', kkBeranda(new Date(__KINI)).status === 'Katalog kasir: belum terbaca dari server');
// ---- 7 · index.html: penjaga (teks index.html) — penulis lama ditutup
var M = __M;   // modal hanya-baca yang dibuka penjaga (blok penjaga index.html disisipkan apa adanya di bundel, lihat jalan_jsc)
ok('index.html: katalog kasir DITOLAK tanpa modal (jalan otomatis, bukan ketukan)', penjagaTulis('katalog', 'ringkasanKasir', 'aktif') === false && M.length === 0, J(M));
ok('index.html: jenis beras, operator kasir, PIN owner DITOLAK dan modalnya menunjuk tempat barunya di /baru/', penjagaTulis('simpan', 'pengaturan', 'jenisBeras') === false && /Jenis beras/.test(M[0] || '')
  && penjagaTulis('simpan', 'pengaturan', 'aksesKasir') === false && /Kasir &amp; PIN|Kasir & PIN/.test(M[1] || '') && penjagaTulis('simpan', 'pengaturan', 'keamanan') === false && M.length === 3, J(M));
ok('index.html: catatan tetap ditolak; denyut & antrean-sekali tetap jalan', penjagaTulis('simpan', 'penjualan', 1) === false && penjagaTulis('denyut') === true && penjagaTulis('antrean-sekali') === true);
_modePulih = true; ok('index.html: pulihkan dari berkas (mode pulih) tetap boleh menulis setelan & catatan — prosedur pulih tidak berubah', penjagaTulis('simpan', 'pengaturan', 'jenisBeras') === true && penjagaTulis('simpan', 'penjualan', 1) === true); _modePulih = false;
print(J({ lulus: lulus, gagal: gagal }));
"""

PENJAGA_AWAL, PENJAGA_AKHIR = "  const PESAN_HANYA_BACA =", "  function galatHanyaBaca()"


def fungsi(teks, nama):
    """Badan fungsi (juga `export async function`) sampai kurung kurawal penutupnya — '' kalau tidak ada."""
    m = re.search(r'(?:^|\n)(?:export\s+)?(?:async\s+)?function\s+' + re.escape(nama) + r'\s*\(', teks)
    return (beku2.potong(teks[m.start():].replace('export ', '', 1), nama) or '') if m else ''


def kunci_lama(t):
    b = beku2.potong(modul_index(t), 'terbitkanRingkasanKasir') or ''
    m = re.search(r"setDoc\(doc\(db, 'ringkasanKasir', 'aktif'\), \{(.*?)\}\)", b, re.S)
    return [re.match(r'\s*(\w+)', x).group(1) for x in m.group(1).split(',')] if m else None


def jalan_jsc(t):
    lama = beku2.potong(modul_index(t), 'susunIsiKatalogKasir')
    if not lama: return 0, ['susunIsiKatalogKasir() tidak ditemukan di index.html']
    mi = modul_index(t); a = mi.find(PENJAGA_AWAL); z = mi.find(PENJAGA_AKHIR)
    if a < 0 or z < 0: return 0, ['blok penjaga index.html (PESAN_HANYA_BACA … galatHanyaBaca) tidak ditemukan']
    penjaga = mi[a:z].replace('  const ', '  var ').replace('  let ', '  var ')
    kl = kunci_lama(t)
    if not kl: return 0, ['setDoc ringkasanKasir di terbitkanRingkasanKasir() tidak terbaca']
    cad = None; nama_cad = ''
    p = cadangan_toko()
    if p:
        d = json.load(open(p, encoding='utf-8')); nama_cad = os.path.basename(p)
        kol = re.findall(r"\{ nama: '(\w+)'", t['baru/js/data/koleksi.js'])
        cad = dict((n, d[n]) for n in kol if isinstance(d.get(n), list))
    js = '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL])
    isi = (JAM + js + '\n' + lama.replace('function susunIsiKatalogKasir(', 'function susunIsiKatalogKasirLama(', 1)
           + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar KUNCI_LAMA = ' + json.dumps(kl) + ';\nvar CADANGAN = ' + json.dumps(cad) + ';\nvar NAMA_CADANGAN = ' + json.dumps(nama_cad)
           + ';\n// ---- blok penjaga index.html (PESAN_HANYA_BACA … sebelum galatHanyaBaca), apa adanya kecuali const/let → var; modal & escapeHtml diganti pencatat\n'
           + 'var __M = []; function bukaModalHanyaBaca(isi) { __M.push(isi); } function escapeHtml(s) { return String(s); }\n' + penjaga + '\n' + SKENARIO)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(isi); jalur = f.name
    r = subprocess.run([JSC, jalur], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(jalur)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(baris[-1]); return h['lulus'], h['gagal']


# ---- 39b no. 4: BUKU KECIL PEMBAYARAN BON di kasir.html (jsc, fungsi ASLI dipotong dari kasir.html; DOM, alert, kirimAntrean dipalsukan) ----
# Dulu sisa bon sesudah membayar cuma dikurangi di memori → muat ulang / katalog disegarkan = sisa lama kembali, bon yang sama bisa dibayar penuh lagi.
BAYAR_BON_VAR = ['K_BAYAR_BON', 'K_ANTREAN', 'K_GAGAL', 'K_DITOLAK_ARSIP', 'BAYAR_BON_UMUR_MAKS_MS', 'HARI_PENDEK', 'utangTerpilih', 'daftarTampilUtang', 'caraUtangAktif']
BAYAR_BON_FUNGSI = ['idUnik', 'esk', 'rupiah', 'tanggalLokalIso', 'tanggalRingkas', 'ambilAntrean', 'simpanAntrean', 'ambilGagal', 'idPerangkat', 'tambahAntrean',
                    'ambilArsipDitolak', 'cabutDariAntrean', 'pindahKeDitolak', 'kunciNamaKasir', 'ambilBayarBon', 'simpanBayarBon', 'msServer', 'sisaKatalogNama', 'catatBayarBon', 'tandaiBayarBonDikirim', 'tandaiBayarBonTerkirim', 'buangBayarBon', 'bayarBonTertunda',
                    'daftarUtang', 'cariUtang', 'umurDaftarSisa', 'isiSaranNamaPelanggan', 'bukaLayarUtang', 'tutupLayarUtang', 'bakuCaraBayar', 'pilihCaraUtang', 'pilihUtang', 'isiLunasUtang', 'simpanBayarUtang']
PALSU_KASIR = r"""
var __el = {}; function $(id) { if (!__el[id]) __el[id] = { id: id, textContent: '', innerHTML: '', value: '', style: {}, classList: { add: function () {}, remove: function () {}, toggle: function (c, on) { this[c] = on === undefined ? !this[c] : !!on; } }, focus: function () {} }; return __el[id]; }
var __alert = []; function alert(m) { __alert.push(String(m)); }
var __kirim = 0; function kirimAntrean() { __kirim += 1; } function perbaruiStatus() {} function operatorAktif() { return 'Owner'; } function setTimeout() {}
var bayarAktif = 'Tunai'; var ringkasan = null;
"""
SKENARIO_BAYAR_BON = r"""
var L = 0, G = []; function ok(n, c, k) { if (c) L += 1; else G.push(n + (k === undefined ? '' : ' → ' + JSON.stringify(k))); }
function antre() { return ambilAntrean().filter(function (x) { return x.koleksi === 'piutangMutasi'; }); }
function sisa(nama) { var p = cariUtang(nama); return p ? p.sisa : null; }
function muatUlang() { utangTerpilih = null; daftarTampilUtang = []; ringkasan = JSON.parse(JSON.stringify(ringkasan)); }   // HP dimuat ulang: memori hilang, localStorage tetap
function bayar(nama, n) { bukaLayarUtang(); var i = daftarTampilUtang.map(function (p) { return p.nama; }).indexOf(nama); if (i < 0) return 'tidak ada di daftar'; pilihUtang(i); $('utangNominal').value = String(n); var a = __alert.length; simpanBayarUtang(); return __alert.length > a ? __alert[__alert.length - 1] : 'ok'; }
function terkirim(id, waktu) { simpanAntrean(ambilAntrean().filter(function (x) { return String(x.docId) !== String(id); })); tandaiBayarBonTerkirim(id, waktu); }
$('utangCara-Tunai').classList.pilih = true; $('utangCara-Qris').classList.pilih = false;   // = markup kasir.html (TUNAI class="pilih"); tinjauan no. 3 K3
var KAT = { diperbaruiPada: '2026-09-30T02:00:00.000Z', _waktuServer: '2026-09-30T02:00:01.123456Z', piutang: [{ nama: 'Bu Ani', sisa: 100000 }, { nama: 'Pak Budi', sisa: 50000 }] };
ringkasan = JSON.parse(JSON.stringify(KAT));
// S1 bayar sebagian → antrean + buku kecil; sisa di layar turun
ok('S1 bayar Bu Ani 40.000: satu piutangMutasi bayar di antrean + satu catatan buku kecil; sisa di daftar Rp60.000 (tertunda 40.000)', bayar('Bu Ani', 40000) === 'ok' && antre().length === 1 && antre()[0].data.nominal === 40000 && antre()[0].data.namaPelanggan === 'Bu Ani' && ambilBayarBon().length === 1 && sisa('Bu Ani') === 60000 && cariUtang('Bu Ani').tertunda === 40000, [antre().length, ambilBayarBon(), sisa('Bu Ani')]);
ok('S1 catatan uang (antrean) ditulis LEBIH DULU daripada buku kecil, dengan docId yang sama', ambilBayarBon().length === 1 && antre().length === 1 && String(ambilBayarBon()[0].docId) === String(antre()[0].docId), [ambilBayarBon(), antre().length]);
// S2 muat ulang: dulu sisa lama kembali (100.000) — kini tetap 60.000
muatUlang(); ok('S2 sesudah HP dimuat ulang (katalog masih yang lama) sisa Bu Ani TETAP Rp60.000, bukan Rp100.000', sisa('Bu Ani') === 60000, sisa('Bu Ani'));
ok('S2 lembar utang menyebut umur daftar sisa ("Daftar sisa dari sistem per 09.00, Rab 30/09/2026") dan pembayaran HP ini yang belum masuk', (bukaLayarUtang(), /Daftar sisa dari sistem per 09\.00, Rab 30\/09\/2026\./.test($('utangSub').textContent) && /1 pembayaran dari HP ini belum masuk daftar — sudah dikurangkan\./.test($('utangSub').textContent)), $('utangSub').textContent);
// S3 bayar sisanya → nama hilang; bayar lagi ditolak (dulu: katalog basi → lolos penuh → sisa sistem minus)
ok('S3 bayar sisa Rp60.000 → lunas di HP ini: Bu Ani hilang dari daftar, antrean 2 pembayaran', bayar('Bu Ani', 60000) === 'ok' && sisa('Bu Ani') === null && antre().length === 2, [sisa('Bu Ani'), antre().length]);
muatUlang(); ok('S3 sesudah muat ulang Bu Ani TIDAK muncul lagi (katalog lama masih Rp100.000) — tidak bisa dibayar penuh dua kali', bayar('Bu Ani', 100000) === 'tidak ada di daftar' && antre().length === 2, antre().length);
utangTerpilih = { nama: 'Bu Ani' }; $('utangNominal').value = '100000'; var a3 = __alert.length; simpanBayarUtang();
ok('S3 lembar yang masih terbuka (utangTerpilih Bu Ani) → simpan DITOLAK: "sudah tidak punya sisa bon", antrean tetap 2', __alert.length === a3 + 1 && /Bu Ani sudah tidak punya sisa bon/.test(__alert[__alert.length - 1]) && antre().length === 2, __alert.slice(-1));
// S4 terkirim (waktu server 02:05); katalog ditulis 02:00 → belum mungkin memuat → tetap dikurangkan
var id1 = antre()[0] ? antre()[0].docId : 'x1', id2 = antre()[1] ? antre()[1].docId : 'x2'; terkirim(id1, '2026-09-30T02:05:00.500000Z'); terkirim(id2, '2026-09-30T02:05:02.000000Z');
ok('S4 kedua pembayaran sampai server (waktu server dicatat), katalog ditulis SEBELUMNYA → Bu Ani tetap tidak muncul', antre().length === 0 && ambilBayarBon().length === 2 && ambilBayarBon().every(function (c) { return c.dariServer && /^2026-09-30T02:05/.test(c.waktuServer); }) && sisa('Bu Ani') === null, ambilBayarBon());
// S4b katalog ditulis SEBELUM pembayaran sampai server (02:04) tapi baru diambil sekarang, isinya berubah karena catatan lain (bon baru Bu Ani
//     20.000 di perangkat lain) → belum mungkin memuat pembayaran HP ini → tetap dikurangkan: 120.000 − 100.000
ringkasan = { diperbaruiPada: '2026-09-30T02:04:00.000Z', _waktuServer: '2026-09-30T02:04:00.200Z', piutang: [{ nama: 'Bu Ani', sisa: 120000 }, { nama: 'Pak Budi', sisa: 50000 }] };
ok('S4b katalog 02:04 (sebelum pembayaran 02:05 diterima server) dengan Bu Ani 120.000 → tetap dikurangkan: Rp20.000, pembanding jadi 120.000', sisa('Bu Ani') === 20000 && ambilBayarBon().length === 2 && ambilBayarBon().every(function (c) { return c.sisaKatalog === 120000; }), [sisa('Bu Ani'), ambilBayarBon()]);
// S5 katalog ditulis SESUDAH pembayaran tapi sisa Bu Ani belum berubah (terbit karena hal lain) → tetap dikurangkan
ringkasan = { diperbaruiPada: '2026-09-30T02:05:02.000Z', _waktuServer: '2026-09-30T02:05:03.000001Z', piutang: [{ nama: 'Bu Ani', sisa: 120000 }, { nama: 'Pak Budi', sisa: 50000 }] };
ok('S5 katalog sesudah bayar dengan sisa Bu Ani SAMA (120.000) → pembayarannya belum dihitung sistem → tetap dikurangkan (Rp20.000)', sisa('Bu Ani') === 20000 && ambilBayarBon().length === 2, [sisa('Bu Ani'), ambilBayarBon().length]);
// S6 katalog sesudah bayar sudah menghitung kedua pembayaran (Bu Ani 20.000 = bon baru) → buku kecil dibersihkan; katalog = penentu lagi
ringkasan = { diperbaruiPada: '2026-09-30T02:06:00.000Z', _waktuServer: '2026-09-30T02:06:01Z', piutang: [{ nama: 'Bu Ani', sisa: 20000 }, { nama: 'Pak Budi', sisa: 50000 }] };
ok('S6 katalog sesudah bayar sudah menghitungnya (Bu Ani Rp20.000 = bon baru saja) → buku kecil kosong, TIDAK dikurangi dua kali', sisa('Bu Ani') === 20000 && sisa('Pak Budi') === 50000 && ambilBayarBon().length === 0, [sisa('Bu Ani'), ambilBayarBon()]);
ringkasan.piutang = [{ nama: 'Pak Budi', sisa: 50000 }];
// S7 ditolak server → tidak masuk buku → tidak dikurangkan
bayar('Pak Budi', 20000); var id7 = antre()[0] ? antre()[0].docId : 'x7'; ok('S7 bayar Pak Budi 20.000 (masih di antrean) → Rp30.000', sisa('Pak Budi') === 30000, sisa('Pak Budi'));
localStorage.setItem(K_GAGAL, JSON.stringify([{ koleksi: 'piutangMutasi', docId: id7, data: {}, ditolak: { status: 403 } }])); simpanAntrean([]);
ok('S7 pembayaran DITOLAK server (pindah ke daftar ditolak) → tidak dikurangkan lagi: Pak Budi kembali Rp50.000, catatannya dibuang', sisa('Pak Budi') === 50000 && ambilBayarBon().length === 0, [sisa('Pak Budi'), ambilBayarBon()]);
localStorage.setItem(K_GAGAL, '[]');
// S8 katalog berubah karena catatan lain SELAGI pembayaran masih di antrean → pembanding diperbarui, pengurangan jalan terus
bayar('Pak Budi', 10000); var id8 = antre()[0] ? antre()[0].docId : 'x8';
ringkasan = { diperbaruiPada: '2026-09-30T02:07:00.000Z', _waktuServer: '2026-09-30T02:07:00.5Z', piutang: [{ nama: 'Pak Budi', sisa: 70000 }] };
ok('S8 katalog baru (bon lain Pak Budi +20.000 dicatat di perangkat lain) selagi pembayaran belum terkirim → 70.000 − 10.000 = Rp60.000', sisa('Pak Budi') === 60000 && ambilBayarBon().length === 1 && ambilBayarBon()[0].sisaKatalog === 70000, [sisa('Pak Budi'), ambilBayarBon()]);
terkirim(id8, '2026-09-30T02:08:00Z');
ok('S8 terkirim 02:08, katalog masih 02:07 → tetap Rp60.000', sisa('Pak Budi') === 60000, sisa('Pak Budi'));
ringkasan = { diperbaruiPada: '2026-09-30T02:08:04.000Z', _waktuServer: '2026-09-30T02:08:05Z', piutang: [{ nama: 'Pak Budi', sisa: 60000 }] };
ok('S8 katalog sesudah bayar = 60.000 → sudah dihitung → catatan dibuang, tidak dikurangi dua kali (tetap Rp60.000)', sisa('Pak Budi') === 60000 && ambilBayarBon().length === 0, [sisa('Pak Budi'), ambilBayarBon()]);
// S9 pilih menurut NAMA yang terlihat, bukan nomor urut (katalog bisa berganti tiap 2 menit)
ringkasan = { diperbaruiPada: '2026-09-30T02:10:00.000Z', _waktuServer: '2026-09-30T02:10:00Z', piutang: [{ nama: 'Bu Cici', sisa: 25000 }, { nama: 'Pak Budi', sisa: 60000 }] };
bukaLayarUtang(); ringkasan = { diperbaruiPada: '2026-09-30T02:12:00.000Z', _waktuServer: '2026-09-30T02:12:00Z', piutang: [{ nama: 'Pak Budi', sisa: 60000 }, { nama: 'Bu Cici', sisa: 25000 }] };
pilihUtang(0); ok('S9 daftar berganti urutan di antara membuka lembar & mengetuk → yang terpilih tetap nama yang TERLIHAT (Bu Cici), sisa dari katalog terbaru', utangTerpilih && utangTerpilih.nama === 'Bu Cici' && $('utangJudul').textContent === 'Bu Cici' && /Sisa utang Rp25\.000/.test($('utangSub').textContent), [utangTerpilih, $('utangSub').textContent]);
ringkasan = { diperbaruiPada: '2026-09-30T02:13:00.000Z', _waktuServer: '2026-09-30T02:13:00Z', piutang: [{ nama: 'Pak Budi', sisa: 60000 }] };
bukaLayarUtang(); ringkasan.piutang = []; var a9 = __alert.length; pilihUtang(0);
ok('S9 nama yang diketuk sudah hilang dari katalog terbaru → diberi tahu, tidak memilih orang lain', !utangTerpilih && __alert.length === a9 + 1 && /Pak Budi sudah tidak punya sisa bon/.test(__alert[__alert.length - 1]), __alert.slice(-1));
// S10 pagar melebihi sisa memakai sisa yang sudah dikurangi pembayaran tertunda
ringkasan = { diperbaruiPada: '2026-09-30T02:14:00.000Z', _waktuServer: '2026-09-30T02:14:00Z', piutang: [{ nama: 'Bu Dewi', sisa: 100000 }] }; simpanAntrean([]); simpanBayarBon([]);
bayar('Bu Dewi', 70000); var r10 = bayar('Bu Dewi', 40000);
ok('S10 Bu Dewi 100.000, sudah dibayar 70.000 di HP ini → bayar 40.000 DITOLAK ("melebihi sisa utang Rp30.000 (sudah dikurangi Rp70.000 …)"); antrean tetap 1', /melebihi sisa utang Rp30\.000 \(sudah dikurangi Rp70\.000 yang dibayar lewat HP ini\)/.test(r10) && antre().length === 1, r10);
bukaLayarUtang(); pilihUtang(0); isiLunasUtang(); ok('S10 "Isi penuh" mengisi Rp30.000 (sisa sesudah pembayaran tertunda), bukan Rp100.000', $('utangNominal').value === 30000 || $('utangNominal').value === '30000', $('utangNominal').value);
// S11 waktu server: pecahan detik, tanpa pecahan, sampah
ok('S11 msServer: "…00.5Z" = +500 ms · "…00Z" · "…00.123456789Z" dipotong ke ms · teks lain = NaN', msServer('2026-09-30T02:05:00.5Z') - msServer('2026-09-30T02:05:00Z') === 500 && msServer('2026-09-30T02:05:00.123456789Z') - msServer('2026-09-30T02:05:00Z') === 123 && isNaN(msServer('')) && isNaN(msServer('kemarin')) && isNaN(msServer(undefined)), [msServer('2026-09-30T02:05:00.5Z'), msServer('2026-09-30T02:05:00Z')]);
// S12 terkirim tanpa waktu server (jawaban PATCH kosong) → tetap ditandai; katalog tanpa waktu server (cache lama) → dianggap SEBELUM bayar
simpanAntrean([]); simpanBayarBon([]); ringkasan = { diperbaruiPada: '2026-09-30T02:20:00.000Z', piutang: [{ nama: 'Bu Eka', sisa: 80000 }] };
bayar('Bu Eka', 30000); var id12 = antre()[0] ? antre()[0].docId : 'x12'; terkirim(id12, '');
ok('S12 jawaban PATCH tanpa updateTime → waktu kirim dicatat dari jam HP (bukan kosong), bukan dariServer', ambilBayarBon().length === 1 && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(ambilBayarBon()[0].waktuServer) && !ambilBayarBon()[0].dariServer, ambilBayarBon());
ok('S12 katalog TANPA waktu server (salinan versi lama) → belum dianggap menghitung → tetap dikurangkan (Rp50.000)', sisa('Bu Eka') === 50000, sisa('Bu Eka'));
// S13 pembersih: catatan > 30 hari tak pernah tampak di katalog → dibuang
var c13 = ambilBayarBon(); if (c13[0]) c13[0].dibuat = new Date(Date.now() - 31 * 86400000).toISOString(); simpanBayarBon(c13);
ok('S13 catatan buku kecil berumur > 30 hari dibuang (pembersih), katalog jadi penentu', sisa('Bu Eka') === 80000 && ambilBayarBon().length === 0, ambilBayarBon());
// S14 (tinjauan K1): kiriman pertama TERSIMPAN di server tapi jawabannya hilang → tetap di antrean; katalog yang sudah menghitungnya tiba duluan
simpanAntrean([]); simpanBayarBon([]); localStorage.setItem(K_GAGAL, '[]');
ringkasan = { diperbaruiPada: '2026-09-30T04:00:00.000Z', _waktuServer: '2026-09-30T04:00:00Z', piutang: [{ nama: 'Bu Fani', sisa: 100000 }] };
bayar('Bu Fani', 40000); var id14 = antre()[0] ? antre()[0].docId : 'x14'; tandaiBayarBonDikirim(id14);
ringkasan = { diperbaruiPada: '2026-09-30T04:01:00.000Z', _waktuServer: '2026-09-30T04:01:05Z', piutang: [{ nama: 'Bu Fani', sisa: 60000 }] };
ok('S14 K1 katalog 04:01 (sudah menghitung) tiba selagi pembayaran masih di antrean tapi SUDAH pernah dikirim → pembanding TIDAK diganti (tetap 100.000); sementara dikurangkan (Rp20.000)', sisa('Bu Fani') === 20000 && ambilBayarBon()[0] && ambilBayarBon()[0].sisaKatalog === 100000, [sisa('Bu Fani'), ambilBayarBon()]);
terkirim(id14, '2026-09-30T04:00:30.000000Z');
ok('S14 K1 kiriman ulang masuk: createTime 04:00:30 (kiriman pertama) < katalog 04:01:05 & sisa berubah → catatan dibuang, Rp60.000 — pengurangan ganda TIDAK menetap', sisa('Bu Fani') === 60000 && ambilBayarBon().length === 0, [sisa('Bu Fani'), ambilBayarBon()]);
// S15 (tinjauan K2): katalog TANPA waktu server (ditulis kasir darurat versi lama ke kunci bersama) yang sudah memuat pembayaran
ringkasan = { diperbaruiPada: '2026-09-30T05:00:00.000Z', _waktuServer: '2026-09-30T05:00:00Z', piutang: [{ nama: 'Pak Gani', sisa: 100000 }] };
bayar('Pak Gani', 40000); var id15 = antre()[0] ? antre()[0].docId : 'x15'; terkirim(id15, '2026-09-30T05:02:00Z');
ringkasan = { diperbaruiPada: '2026-09-30T05:03:00.000Z', piutang: [{ nama: 'Pak Gani', sisa: 60000 }] };
ok('S15 K2 katalog tanpa waktu server → tetap dikurangkan (sementara Rp20.000) tapi pembanding TIDAK diganti (tetap 100.000)', sisa('Pak Gani') === 20000 && ambilBayarBon()[0] && ambilBayarBon()[0].sisaKatalog === 100000, [sisa('Pak Gani'), ambilBayarBon()]);
ringkasan = { diperbaruiPada: '2026-09-30T05:03:00.000Z', _waktuServer: '2026-09-30T05:03:01Z', piutang: [{ nama: 'Pak Gani', sisa: 60000 }] };
ok('S15 K2 katalog yang sama diambil kasir.html sendiri (waktu server 05:03 > 05:02) → catatan dibuang, Rp60.000', sisa('Pak Gani') === 60000 && ambilBayarBon().length === 0, [sisa('Pak Gani'), ambilBayarBon()]);
// S16 (tinjauan K3): ditolak → dibuang SAAT penolakan (pindahKeDitolak), lalu diarsipkan owner — tidak hidup lagi
ringkasan = { diperbaruiPada: '2026-09-30T06:00:00.000Z', _waktuServer: '2026-09-30T06:00:00Z', piutang: [{ nama: 'Bu Hana', sisa: 100000 }] };
bayar('Bu Hana', 40000); var it16 = antre()[0];
ok('S16 K3 pembayaran ditolak server → pindahKeDitolak membuang catatannya dari buku kecil saat itu juga', it16 && pindahKeDitolak(it16, 403, null, 'ditolak-aturan') && ambilBayarBon().length === 0 && ambilGagal().length === 1, ambilBayarBon());
localStorage.setItem(K_DITOLAK_ARSIP, JSON.stringify(ambilGagal())); localStorage.setItem(K_GAGAL, '[]');
ok('S16 K3 sesudah diarsipkan owner: Bu Hana tetap Rp100.000 (tidak dikurangkan), kalimat "belum masuk daftar" tidak muncul', sisa('Bu Hana') === 100000 && (bukaLayarUtang(), !/belum masuk daftar/.test($('utangSub').textContent)), $('utangSub').textContent);
simpanBayarBon([{ docId: String(it16 ? it16.docId : 'x16'), kunci: 'bu hana', nominal: 40000, dibuat: new Date(Date.now()).toISOString(), sisaKatalog: 100000, waktuServer: '' }]);
ok('S16 K3 HP yang terlanjur memegang catatan untuk pembayaran yang sudah DIARSIPKAN ditolak → dianggap ditolak, dibuang', sisa('Bu Hana') === 100000 && ambilBayarBon().length === 0, ambilBayarBon());
// S17 (audit 39b no. 3): cara bayar BON dipilih di lembar utang sendiri — dulu mewarisi tombol nota (bayarAktif) diam-diam: nota terakhir QRIS → bayar bon
//     yang diterima TUNAI tercatat QRIS (laci kurang, rekening lebih). Bawaan Tunai tiap kali nama dipilih; QRIS hanya bila diketuk.
simpanAntrean([]); simpanBayarBon([]); localStorage.setItem(K_GAGAL, '[]'); localStorage.setItem(K_DITOLAK_ARSIP, '[]');
ringkasan = { diperbaruiPada: '2026-09-30T07:00:00.000Z', _waktuServer: '2026-09-30T07:00:00Z', piutang: [{ nama: 'Bu Ika', sisa: 100000 }, { nama: 'Pak Joko', sisa: 90000 }] };
bayarAktif = 'QRIS'; var r17 = bayar('Bu Ika', 30000);
ok('S17 tombol nota sedang QRIS, bayar bon tanpa memilih cara → tercatat TUNAI (bukan warisan QRIS nota)', r17 === 'ok' && antre().length === 1 && antre()[0].data.caraBayar === 'Tunai' && $('utangCara-Tunai').classList.pilih === true && $('utangCara-Qris').classList.pilih === false, [r17, antre().map(function (x) { return x.data.caraBayar; })]);
bayarAktif = 'Tunai'; bukaLayarUtang(); pilihUtang(daftarTampilUtang.map(function (p) { return p.nama; }).indexOf('Pak Joko')); pilihCaraUtang('Qris'); $('utangNominal').value = '40000'; simpanBayarUtang();
ok('S17 diketuk QRIS di lembar utang (tombol nota Tunai) → tercatat QRIS; tombol QRIS menyala', antre().length === 2 && antre()[1].data.caraBayar === 'QRIS' && antre()[1].data.namaPelanggan === 'Pak Joko' && caraUtangAktif === 'QRIS' && $('utangCara-Qris').classList.pilih === true, antre().map(function (x) { return x.data.namaPelanggan + ':' + x.data.caraBayar; }));
bukaLayarUtang(); pilihUtang(daftarTampilUtang.map(function (p) { return p.nama; }).indexOf('Bu Ika'));
ok('S17 memilih nama berikutnya → cara kembali TUNAI (QRIS tadi tidak menempel ke orang lain)', caraUtangAktif === 'Tunai' && $('utangCara-Tunai').classList.pilih === true && $('utangCara-Qris').classList.pilih === false, caraUtangAktif);
pilihCaraUtang('Kredit'); ok('S17 cara selain QRIS (mis. "Kredit") dibakukan jadi Tunai — bayar bon tidak pernah tercatat Kredit', caraUtangAktif === 'Tunai', caraUtangAktif);
// S18 (cara persis, owner 30 Sep): katalog menyebut id pembayaran bon yang SUDAH dihitung (bayarBonTerhitung) → berhenti mengurangkan tepat saat tercantum
simpanAntrean([]); simpanBayarBon([]); localStorage.setItem(K_GAGAL, '[]'); localStorage.setItem(K_DITOLAK_ARSIP, '[]');
ringkasan = { diperbaruiPada: '2026-09-30T08:00:00.000Z', _waktuServer: '2026-09-30T08:00:00Z', piutang: [{ nama: 'Bu Lina', sisa: 100000 }], bayarBonTerhitung: [] };
bayar('Bu Lina', 40000); var id18 = antre()[0] ? antre()[0].docId : 'x18'; terkirim(id18, '2026-09-30T08:01:00Z');
ringkasan = { diperbaruiPada: '2026-09-30T08:02:00.000Z', _waktuServer: '2026-09-30T08:02:00Z', piutang: [{ nama: 'Bu Lina', sisa: 120000 }], bayarBonTerhitung: ['lain-1'] };
ok('S18 persis: katalog SESUDAH bayar, sisa berubah karena bon lain (120.000), id pembayaran BELUM tercantum → tetap dikurangkan: Rp80.000 (tebakan waktu dulu membuangnya → Rp120.000)', sisa('Bu Lina') === 80000 && ambilBayarBon().length === 1, [sisa('Bu Lina'), ambilBayarBon()]);
ringkasan = { diperbaruiPada: '2026-09-30T08:03:00.000Z', _waktuServer: '2026-09-30T08:03:00Z', piutang: [{ nama: 'Bu Lina', sisa: 120000 }], bayarBonTerhitung: ['lain-1', String(id18)] };
ok('S18 persis: id tercantum, sisa KEBETULAN sama (bon baru 40.000 di perangkat lain) → catatan dibuang, sisa = katalog Rp120.000 (tebakan waktu dulu tetap mengurangi → Rp80.000)', sisa('Bu Lina') === 120000 && ambilBayarBon().length === 0, [sisa('Bu Lina'), ambilBayarBon()]);
bayar('Bu Lina', 20000); ok('S18 persis: pembayaran baru masih di antrean, id belum tercantum → dikurangkan (Rp100.000)', sisa('Bu Lina') === 100000 && ambilBayarBon().length === 1, sisa('Bu Lina'));
delete ringkasan.bayarBonTerhitung; ok('S18 katalog TANPA daftar (penerbit lama) → kembali ke tebakan waktu server 39b no. 4 (masih di antrean → dikurangkan)', sisa('Bu Lina') === 100000, sisa('Bu Lina'));
// S19 (tinjauan persis P1): tutup buku mengarsipkan dokumen bayar — id-nya tidak tercantum lagi, tetapi pembayarannya sudah terserap saldo pembuka
simpanAntrean([]); simpanBayarBon([]); ringkasan = { diperbaruiPada: '2026-09-30T09:00:00.000Z', _waktuServer: '2026-09-30T09:00:00Z', piutang: [{ nama: 'Bu Mira', sisa: 100000 }], bayarBonTerhitung: [], bayarBonSejak: '' };
bayar('Bu Mira', 30000); var id19 = antre()[0] ? antre()[0].docId : 'x19';
ok('S19 buku kecil menyimpan TANGGAL pembayaran (jam HP) untuk aturan awal buku', ambilBayarBon()[0] && ambilBayarBon()[0].tanggal === tanggalLokalIso(), ambilBayarBon());
var tg19 = ambilBayarBon()[0] ? ambilBayarBon()[0].tanggal : '2026-09-19'; var besok19 = tanggalLokalIso(new Date(new Date(tg19 + 'T12:00:00').getTime() + 86400000));
ringkasan = { diperbaruiPada: '2026-09-30T09:01:00.000Z', _waktuServer: '2026-09-30T09:01:00Z', piutang: [{ nama: 'Bu Mira', sisa: 70000 }], bayarBonTerhitung: [], bayarBonSejak: besok19 };
ok('S19 pembayaran MASIH di antrean & bertanggal sebelum awal buku → belum sampai server → tetap dikurangkan (Rp40.000)', sisa('Bu Mira') === 40000, sisa('Bu Mira'));
terkirim(id19, '2026-09-30T09:00:30Z');
ok('S19 sudah sampai server, bertanggal sebelum awal buku (sehari sesudahnya), id tidak tercantum (dokumennya diarsipkan tutup buku) → terserap saldo pembuka → dibuang, Rp70.000 (bukan dikurangi dua kali → Rp40.000)', sisa('Bu Mira') === 70000 && ambilBayarBon().length === 0, [sisa('Bu Mira'), ambilBayarBon()]);
simpanBayarBon([{ docId: 'lama-1', kunci: 'bu mira', nominal: 10000, dibuat: new Date(new Date(tg19 + 'T12:00:00').getTime() - 86400000).toISOString(), sisaKatalog: 70000, waktuServer: '2026-09-18T03:00:05Z', dariServer: true }]);
ok('S19 catatan buku kecil lama TANPA tanggal → tanggalnya dari waktu dibuat (dua hari sebelum awal buku) → dibuang', sisa('Bu Mira') === 70000 && ambilBayarBon().length === 0, ambilBayarBon());
print(JSON.stringify({ lulus: L, gagal: G }));
"""
def jalan_bayar_bon(t):
    k = t['kasir.html']; bagian = []; hilang = []
    for v in BAYAR_BON_VAR:
        m = re.search(r'^var ' + v + r' = [^;\n]*;', k, re.M)
        if m: bagian.append(m.group(0))
        else: hilang.append('var ' + v)
    for f in BAYAR_BON_FUNGSI:
        b = beku2.potong(k, f)
        if b: bagian.append(b)
        else: hilang.append(f + '()')
    if hilang: return 0, ['kasir.html: tidak ditemukan ' + ', '.join(hilang)]
    isi = JAM + bundel_baru.PRELUDE + PALSU_KASIR + '\n'.join(bagian) + '\n' + SKENARIO_BAYAR_BON
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(isi); jalur = f.name
    r = subprocess.run([JSC, jalur], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(jalur)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return 0, ['JSC JATUH (bayar bon kasir): ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(baris[-1]); return h['lulus'], h['gagal']


def periksa_statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    mi = modul_index(t)
    a = beku2.potong(mi, 'susunIsiKatalogKasir'); b = beku2.potong(t['baru/js/mesin/pembantu.js'], 'susunIsiKatalogKasir')
    ok('penyusun isi katalog /baru/ (pembantu.js) HURUF DEMI HURUF = susunIsiKatalogKasir() index.html', a and b and a.strip() == b.strip(), 'beda' if a and b else 'hilang')
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
    ok('harga.js: terbit harga menyertakan katalog kasir di kiriman yang SAMA (kkSertakan)', re.search(r"hgTerbitkan: async \(\) => \{[^\n]*tulis\(Object\.assign\(\{\}, r, \{ dokumen: kkSertakan\(r\.dokumen, ", t['baru/js/layar/harga.js']))
    ok('Beranda: baris katalog kasir (kkBeranda → #rkKatalog) & perhatiannya ikut di Perlu perhatian', 'kkBeranda(k)' in t['baru/js/layar/ringkasan.js'] and "$('rkKatalog').textContent = KK ? KK.status : ''" in t['baru/js/layar/ringkasan.js'] and 'KK ? KK.perhatian : []' in t['baru/js/layar/ringkasan.js'])
    jb = re.search(r"const JALUR_BUKAN_CATATAN = \{([^}]*)\};", mi); jd = re.search(r"const JALUR_DIAM = \{([^}]*)\};", mi)
    ok('index.html: katalog kasir bukan lagi jalur yang selalu lolos; ditutup TANPA modal (JALUR_DIAM)', jb and 'katalog' not in jb.group(1) and jd and re.search(r'\bkatalog:', jd.group(1)))
    tr = beku2.potong(mi, 'terbitkanRingkasanKasir') or ''; ap = beku2.potong(mi, 'apTerbitkanKatalog') or ''
    ok('index.html: penerbit lama bertanya ke penjaga di baris pertama; tombol "Terbitkan katalog sekarang" tidak menulis apa pun', "if (!penjagaTulis('katalog', 'ringkasanKasir', 'aktif')) return;" in [x for x in tr.split('\n') if x.strip()][1:2][0] and ap and not re.search(r'terbitkanRingkasanKasir\(|setDoc|simpanKeFirestore', ap))
    d = t[DARURAT]
    ok('kasir darurat: katalog diambil saat layar dinyalakan & tiap 5 menit selagi terlihat (jadwal denyut)',
       "document.addEventListener('visibilitychange', function () { if (!document.hidden) segarkanRingkasanD(); });" in d and "setInterval(function () { if (!document.hidden) segarkanRingkasanD(); }, 300000);" in d)
    ok('kasir darurat: denyut membawa cap katalog yang dipegang; katalog berganti → denyut segera', 'katalog: katalogDipegangD()' in d and 'if (katalogDipegangD() !== tadi) { denyutTerakhirD = 0; kirimDenyutD(); }' in d)
    vs = re.search(r"const VERSI = '([^']+)';", t['sw-kasir.js']); kk = re.search(r"export const KK_VERSI_KASIR_TERBARU = '([^']+)';", t['baru/js/data/katalog-kasir.js'])
    va = [re.search(r"var VERSI_APLIKASI = '([^']+)';", t[b]) for b in (DARURAT, 'kasir.html')]
    kp = re.search(r"export const KP_VERSI_KASIR_25B = '([^']+)';", t['baru/js/data/kunci-periode.js'])
    nomor = lambda m: int(re.match(r'kasir-v(\d+)$', m.group(1)).group(1)) if m else -1
    ok('versi: kedua berkas kasir = VERSI sw-kasir.js = KK_VERSI_KASIR_TERBARU (/baru/) = kasir-v30', vs and kk and all(v and v.group(1) == vs.group(1) for v in va) and kk.group(1) == vs.group(1) == 'kasir-v30', [x.group(1) if x else None for x in [vs, kk] + va])
    ok('versi: lantai kunci bulan (KP_VERSI_KASIR_25B) tidak di atas versi yang disajikan sw-kasir.js', kp and vs and 0 < nomor(kp) <= nomor(vs), kp.group(1) if kp else None)
    k = t['kasir.html']
    ok('kasir.html (39b no. 4): katalog yang diambil menyimpan waktu SERVER dokumennya (updateTime) — pembanding buku kecil bayar bon', "o._waktuServer = j.updateTime || '';" in k)
    ok('kasir.html (39b no. 3): lembar utang punya tombol TUNAI/QRIS sendiri (pilihCaraUtang, terpasang ke window), letaknya sesudah kotak nominal', all(x in k for x in ('<button type="button" id="utangCara-Tunai" class="pilih" onclick="pilihCaraUtang(\'Tunai\')">TUNAI</button>', '<button type="button" id="utangCara-Qris" onclick="pilihCaraUtang(\'Qris\')">QRIS</button>', 'window.pilihCaraUtang = pilihCaraUtang;')) and k.find('id="utangNominal"') < k.find('id="utangCara"'))
    ok('kasir.html (39b no. 4 K1): kiriman pertama pembayaran bon ditandai sebelum PATCH (sesudahnya katalog bukan pembanding lagi)', "    var item = a2[0];\n    if (item.koleksi === 'piutangMutasi') tandaiBayarBonDikirim(item.docId);\n    denganAuth({" in k)
    ok('kasir darurat (39b no. 4 K2): katalog yang ditulisnya ke kunci BERSAMA ikut menyimpan waktu server', "o._waktuServer = j.updateTime || '';" in t[DARURAT])
    ok('kasir.html (39b no. 4): PATCH piutangMutasi yang MASUK menandai buku kecil dengan waktu server dari jawabannya, sebelum dicabut dari antrean',
       re.search(r"if \(g === 'masuk'\) \{\n\s+if \(item\.koleksi === 'piutangMutasi'\) \{ tandaiBayarBonTerkirim\(item\.docId, ''\); r\.json\(\)\.then\(function \(isi\) \{ tandaiBayarBonTerkirim\(item\.docId, isi && \(isi\.createTime \|\| isi\.updateTime\)\); \}\)\.catch\(function \(\) \{\}\); \}\n\s+cabutDariAntrean\(item\); kirimSatu\(\); return;", k) is not None)
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
  try { await fetch('/_hasil' + location.search, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(hasil) }); } catch (e) {}
  fetch('/_siap');
  var lanjut = new URLSearchParams(location.search).get('lanjut');
  if (lanjut) location.replace(lanjut);
})();
</script>"""


def periksa_peramban(t):
    out = []; ok = lambda n, c, k='': out.append(('peramban · ' + n, bool(c), k))
    if not CHROME: return [('peramban · Google Chrome tersedia', False, 'tidak ditemukan')]
    d = tempfile.mkdtemp(prefix='katalog-'); s = t[DARURAT]
    assert s.count('<head>') == 1 and s.count('</body>') == 1
    s = s.replace('<head>', '<head>' + KEPALA, 1).replace('</body>', SKENARIO_PERAMBAN + "<img src='/_tahan' alt='' style='display:none'></body>", 1)
    open(os.path.join(d, DARURAT), 'w', encoding='utf-8').write(s)
    srv, port, keadaan = layani(d); profil = tempfile.mkdtemp(prefix='katalog-profil-')
    try:
        a, b = buka(port, keadaan, profil, '/' + DARURAT + '?s=nyala', lalu='/' + DARURAT + '?s=berkala')
    finally:
        srv.shutdown(); shutil.rmtree(profil, ignore_errors=True); shutil.rmtree(d, ignore_errors=True)
    N, B = hasil_dari(a), hasil_dari(b)
    if not N or N.get('galat'): return [('peramban · skenario layar dinyalakan jalan', False, (N or {}).get('galat', 'tidak ada hasil'))]
    ok('HP penjaga memuat katalog saat dibuka (tuts bernama berharga 70.000)', N['awal'] == [70000], N)
    ok('katalog berganti di server: tanpa pemicu harga tuts TETAP yang lama (bukti pemicunya layar dinyalakan, bukan kebetulan)', N['tanpaPemicu'] == [70000], N)
    ok('layar HP dinyalakan → harga baru 72.000 TANPA membuka ulang aplikasi', N['sesudahNyala'] == [72000] and N['getAkhir'] > N['getAwal'], N)
    ok('denyut HP penjaga membawa cap katalog yang baru dipegangnya', '2026-09-27T02:00:00.000Z' in N['denyutKatalog'], N['denyutKatalog'])
    ok('bilah atas: "versi 39b-4p"', N.get('label') == 'versi 39b-4p', N.get('label'))
    if not B or B.get('galat'): return out + [('peramban · skenario berkala jalan', False, (B or {}).get('galat', 'tidak ada hasil'))]
    ok('tanpa ketukan apa pun: katalog baru (74.000) diambil sendiri di jadwal berkala', B['awal'] == [73000] and B['sesudahJadwal'] == [74000], B)
    return out


def semua(ganti=None, bagian=('statis', 'jsc', 'peramban')):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        l, g = jalan_jsc(t); out += [('jsc · ' + x, False, '') for x in g] + [('jsc · %d skenario' % l, l > 0 and not g, '')]
        l2, g2 = jalan_bayar_bon(t); out += [('jsc · bayar bon kasir · ' + x, False, '') for x in g2] + [('jsc · bayar bon kasir · %d skenario (39b no. 4)' % l2, l2 > 0 and not g2, '')]
        out.append(('__jsc_lulus', True, l + l2))
    if 'peramban' in bagian: out += periksa_peramban(t)
    return out


KONTROL = [
    ('penyusun /baru/ beda dari index.html (modal kemasan dinolkan)', {'baru/js/mesin/pembantu.js': [("hppPerUnit: s.hppRataRataPerUnit || 0, hargaPerUnit: h ? h.hargaPerUnit : 0 };", "hppPerUnit: 0, hargaPerUnit: h ? h.hargaPerUnit : 0 };")]}, ('statis', 'jsc')),
    ('dokumen katalog berurutan lain', {'baru/js/data/katalog-kasir.js': [("return { id: KK_ID, diperbaruiPada: kini, kemasan: isi.kemasan, merkKarung: isi.merkKarung,", "return { diperbaruiPada: kini, id: KK_ID, kemasan: isi.kemasan, merkKarung: isi.merkKarung,")]}, ('jsc',)),
    ('pembanding tertipu urutan kunci Firestore', {'baru/js/data/katalog-kasir.js': [("return JSON.stringify(kkUrut({ kemasan:", "return JSON.stringify(({ kemasan:")]}, ('jsc',)),
    ('katalog "seandainya" dari cache SEBELUM kiriman', {'baru/js/data/katalog-kasir.js': [("const isi = denganCacheSementara(daftar, kkIsi); if (!isi) return daftar;", "const isi = kkIsi(); if (!isi) return daftar;")]}, ('jsc',)),
    ('cache tidak dikembalikan sesudah "seandainya"', {'baru/js/data/toko.js': [("try { return fn(); } finally { Object.keys(simpan).forEach((c) => { _cache[c] = simpan[c]; }); }", "return fn();")]}, ('jsc',)),
    ('terbit harga tidak menyertakan katalog kasir', {'baru/js/layar/harga.js': [("tulis(Object.assign({}, r, { dokumen: kkSertakan(r.dokumen, waktu().kini) }))", "tulis(r)")]}, ('statis',)),
    ('gerbang terbit dari salinan perangkat', {'baru/js/data/katalog-kasir.js': [("if (k.dariCache > 0) return", "if (false) return")]}, ('jsc',)),
    ('gerbang terbit tanpa katalog server terbaca', {'baru/js/data/katalog-kasir.js': [("if (_kkServer.ada === null || !_kkServer.dariServer) return", "if (false) return")]}, ('jsc',)),
    ('katalog ditulis dengan atribusi & jejak', {'baru/js/data/firebase.js': [("    if (kkMentah(x.koleksi)) { b.set(doc(db, x.koleksi, String(x.data.id)), x.data); ditulis.push({ koleksi: x.koleksi, data: x.data }); return; }", "")]}, ('statis',)),
    ('penerbit otomatis terbit walau isinya sama', {'baru/js/data/firebase.js': [("if (!isi || kkTertinggal(isi) !== true) return;", "if (!isi) return;")]}, ('statis',)),
    ('penulis lama index.html jalan lagi', {'index.html': [("const JALUR_BUKAN_CATATAN = { denyut: 'denyut perangkat',", "const JALUR_BUKAN_CATATAN = { katalog: 'katalog kasir', denyut: 'denyut perangkat',")]}, ('statis', 'jsc')),
    ('index.html menolak katalog DENGAN modal tiap data berubah', {'index.html': [("    if (JALUR_DIAM[jalur]) return false;\n", "")]}, ('jsc',)),
    ('Beranda diam soal perubahan yang belum sampai', {'baru/js/data/katalog-kasir.js': [("  if (tg) out.push({ teks: 'Katalog kasir: ada perubahan", "  if (false) out.push({ teks: 'Katalog kasir: ada perubahan")]}, ('jsc',)),
    ('HP penjaga yang masih memegang katalog lama tidak disebut', {'baru/js/data/katalog-kasir.js': [("(!isFinite(pegang) || pegang < terbitMs)", "false")]}, ('jsc',)),
    ('kasir darurat tidak mengambil katalog saat layar dinyalakan', {DARURAT: [("document.addEventListener('visibilitychange', function () { if (!document.hidden) segarkanRingkasanD(); });\n", "")]}, ('statis', 'peramban')),
    ('kasir darurat tidak mengambil katalog berkala', {DARURAT: [("setInterval(function () { if (!document.hidden) segarkanRingkasanD(); }, 300000);\n", "")]}, ('statis', 'peramban')),
    ('denyut tanpa cap katalog', {DARURAT: [("    versi: VERSI_APLIKASI,\n    katalog: katalogDipegangD()", "    versi: VERSI_APLIKASI")]}, ('statis', 'peramban')),
    ('sw-kasir.js naik tanpa /baru/ ikut', {'sw-kasir.js': [("const VERSI = 'kasir-v30';", "const VERSI = 'kasir-v31';")]}, ('statis',)),
    ('bayar bon kasir hanya di memori lagi (buku kecil tidak dicatat)', {'kasir.html': [('  catatBayarBon(idBayar, p.nama, n);\n', '')]}, ('jsc',)),
    ('buku kecil tidak dikurangkan dari daftar sisa', {'kasir.html': [('sisa: Math.round(((Number(p.sisa) || 0) - (kurang[kunciNamaKasir(p.nama)] || 0)) * 100) / 100', 'sisa: Math.round((Number(p.sisa) || 0) * 100) / 100')]}, ('jsc',)),
    ('pembayaran ditolak server tetap dikurangkan', {'kasir.html': [('if (!c || ditolak[String(c.docId)]) { ubah = true; return; }', 'if (!c) { ubah = true; return; }')]}, ('jsc',)),
    ('katalog yang sudah menghitung pembayaran tetap dikurangkan (dua kali)', {'kasir.html': [('      if (raw === null || c.sisaKatalog === null || Math.abs(raw - c.sisaKatalog) > 0.005) { ubah = true; return; }\n', '')]}, ('jsc',)),
    ('waktu server diabaikan (katalog lama dianggap sudah menghitung)', {'kasir.html': [('var pastiSebelum = (antre && !c.dikirimSejak) || (!antre && !isNaN(K) && !isNaN(P) && K <= P);', 'var pastiSebelum = (antre && !c.dikirimSejak);')]}, ('jsc',)),
    ('pembanding tidak diperbarui selagi katalog belum memuat pembayaran', {'kasir.html': [('      if (c.sisaKatalog !== raw) { c.sisaKatalog = raw; ubah = true; }\n', '')]}, ('jsc',)),
    ('pilih utang lewat nomor urut lagi', {'kasir.html': [('  var t = daftarTampilUtang[i];\n', '  var t = daftarUtang()[i];\n')]}, ('jsc',)),
    ('simpan memakai sisa saat dipilih, tidak dibaca ulang', {'kasir.html': [("  var p = cariUtang(utangTerpilih.nama);\n  if (!p) { alert(utangTerpilih.nama + ' sudah tidak punya sisa bon di daftar terbaru.'); tutupLayarUtang(); return; }\n", '  var p = { nama: utangTerpilih.nama, sisa: 1e12, tertunda: 0 };\n')]}, ('jsc',)),
    ('pembersih 30 hari tidak jalan', {'kasir.html': [('    if (kini - (Date.parse(c.dibuat) || kini) > BAYAR_BON_UMUR_MAKS_MS) { ubah = true; return; }\n', '')]}, ('jsc',)),
    ('lembar utang tidak menyebut umur daftar sisa', {'kasir.html': [("    + ' ' + umurDaftarSisa().charAt(0).toUpperCase() + umurDaftarSisa().slice(1) + '.'\n", '')]}, ('jsc',)),
    ('katalog diambil tanpa waktu server', {'kasir.html': [("        o._waktuServer = j.updateTime || '';   // kapan katalog ini ditulis, menurut SERVER (bayarBonTertunda)\n", '')]}, ('statis',)),
    ('PATCH pembayaran bon yang masuk tidak menandai buku kecil', {'kasir.html': [("          if (item.koleksi === 'piutangMutasi') { tandaiBayarBonTerkirim(item.docId, ''); r.json().then(function (isi) { tandaiBayarBonTerkirim(item.docId, isi && (isi.createTime || isi.updateTime)); }).catch(function () {}); }\n", '')]}, ('statis',)),
    ('K1: katalog sesudah kiriman pertama dijadikan pembanding (pengurangan ganda menetap)', {'kasir.html': [('var pastiSebelum = (antre && !c.dikirimSejak) ||', 'var pastiSebelum = antre ||')]}, ('jsc',)),
    ('K1: waktu server PATCH memakai updateTime (kiriman ulang menggeser waktunya)', {'kasir.html': [('isi && (isi.createTime || isi.updateTime)', 'isi && isi.updateTime')]}, ('statis',)),
    ('K1: kiriman pertama tidak ditandai', {'kasir.html': [("    if (item.koleksi === 'piutangMutasi') tandaiBayarBonDikirim(item.docId);\n", '')]}, ('statis',)),
    ('K2: katalog tanpa waktu server dijadikan pembanding', {'kasir.html': [('(!antre && !isNaN(K) && !isNaN(P) && K <= P)', '(!antre && (isNaN(K) || (!isNaN(P) && K <= P)))')]}, ('jsc',)),
    ('K2: kasir darurat menulis katalog bersama tanpa waktu server', {'kasir-darurat-nominal.html': [("        o._waktuServer = j.updateTime || '';   // kunci BERSAMA kasir.html: buku kecil bayar bon membaca waktu server katalog (audit 39b no. 4)\n", '')]}, ('statis',)),
    ('K3: pembayaran ditolak tidak dibuang di titik penolakan', {'kasir.html': [("  if (item.koleksi === 'piutangMutasi') buangBayarBon(item.docId);   // ditolak = tidak masuk buku → tidak dikurangkan lagi (tinjauan no. 4 K3)\n", '')]}, ('jsc',)),
    ('K3: arsip ditolak diabaikan (catatan hidup lagi)', {'kasir.html': [('ambilGagal().concat(ambilArsipDitolak())', 'ambilGagal()')]}, ('jsc',)),
    ('39b-3: cara bayar bon mewarisi tombol nota lagi', {'kasir.html': [('    caraBayar: caraUtangAktif,\n', "    caraBayar: bayarAktif === 'Kredit' ? 'Tunai' : bayarAktif,\n")]}, ('jsc',)),
    ('39b-3: memilih nama tidak mengembalikan cara ke Tunai', {'kasir.html': [("  pilihCaraUtang('Tunai');\n", '')]}, ('jsc',)),
    ('39b-3: tombol QRIS lembar utang tidak mengubah cara', {'kasir.html': [("  caraUtangAktif = bakuCaraBayar(c) === 'QRIS' ? 'QRIS' : 'Tunai';\n", '')]}, ('jsc',)),
    ('39b-3: cara bayar bon boleh Kredit', {'kasir.html': [("  caraUtangAktif = bakuCaraBayar(c) === 'QRIS' ? 'QRIS' : 'Tunai';\n", '  caraUtangAktif = bakuCaraBayar(c);\n')]}, ('jsc',)),
    ('39b-3: tombol cara bayar bon hilang dari lembar utang', {'kasir.html': [('      <button type="button" id="utangCara-Qris" onclick="pilihCaraUtang(\'Qris\')">QRIS</button>\n', '')]}, ('statis',)),
    ('persis: kasir mengabaikan daftar id katalog (kembali ke tebakan waktu server)', {'kasir.html': [('  var persis = ringkasan && Array.isArray(ringkasan.bayarBonTerhitung) ? {} : null;\n', '  var persis = null;\n')]}, ('jsc',)),
    ('persis: id tercantum tidak membuang catatan (dikurangi dua kali)', {'kasir.html': [('      if (persis[String(c.docId)]) { ubah = true; return; }\n', '')]}, ('jsc',)),
    ('persis: dokumen katalog tanpa daftar id', {'baru/js/data/katalog-kasir.js': [(", bayarBonTerhitung: isi.bayarBonTerhitung || [], bayarBonSejak:", ", bayarBonSejak:")]}, ('jsc',)),
    ('persis: daftar id tidak ikut pembanding katalog (tidak terbit ulang)', {'baru/js/data/katalog-kasir.js': [(", bayarBonTerhitung: d.bayarBonTerhitung || [], bayarBonSejak:", ", bayarBonSejak:")]}, ('jsc',)),
    ('persis: daftar id kembali berjendela jam perangkat', {'baru/js/data/katalog-kasir.js': [("m.tipe === 'bayar' && kunciPelanggan(m.namaPelanggan)).map(", "m.tipe === 'bayar' && kunciPelanggan(m.namaPelanggan) && (m.tanggal || '') >= new Date(Date.now() - 45 * 86400000).toISOString().slice(0, 10)).map(")]}, ('jsc',)),
    ('persis: tanda awal buku tidak ikut dokumen', {'baru/js/data/katalog-kasir.js': [(", bayarBonSejak: isi.bayarBonSejak || '' };", " };")]}, ('jsc',)),
    ('persis: HP mengabaikan tanda awal buku (dikurangi dua kali sesudah tutup buku)', {'kasir.html': [("      if (sejak && !antre && tgl && tgl < sejak) { ubah = true; return; }\n", '')]}, ('jsc',)),
    ('persis: awal buku dianggap juga untuk pembayaran yang belum sampai server', {'kasir.html': [("if (sejak && !antre && tgl && tgl < sejak)", "if (sejak && tgl && tgl < sejak)")]}, ('jsc',)),
    ('persis: buku kecil tidak menyimpan tanggal', {'kasir.html': [("nominal: nominal, tanggal: tanggalLokalIso(), dibuat:", "nominal: nominal, dibuat:")]}, ('jsc',)),
    ('persis: pembayaran tanpa nama ikut daftar (tidak dihitung hitungPiutang)', {'baru/js/data/katalog-kasir.js': [("m.tipe === 'bayar' && kunciPelanggan(m.namaPelanggan)).map(", "m.tipe === 'bayar').map(")]}, ('jsc',)),
    ('HP v27 disebut "harga baru baru sampai" lagi (lantai ambil-sendiri disamakan dengan versi terbaru)', {'baru/js/data/katalog-kasir.js': [("export const KK_VERSI_AMBIL_SENDIRI = 'kasir-v27';", "export const KK_VERSI_AMBIL_SENDIRI = 'kasir-v30';")]}, ('jsc',)),
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
