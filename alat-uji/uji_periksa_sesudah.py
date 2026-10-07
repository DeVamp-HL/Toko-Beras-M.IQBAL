#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_periksa_sesudah.py — PAKET C siap 2027 (8 Okt 2026): kartu "Pemeriksaan sesudah tutup buku" (Uang › Tutup buku). KOTAK PASIR (nama & angka contoh) di jsc.

Sesudah 13 Okt 2026 tidak ada lagi yang memeriksa cadangan SESUDAH tutup buku di luar aplikasi — aplikasi memeriksa sendiri, owner membaca kartunya.
Simulator ritual = uji_potret_tahun.py (persiapkan, ritual: putusan per tanggal → susunKunci → semua kiriman → arsip) + hasil periksa dibekukan saat arsip
habis (susunPeriksaArsip, seperti uang.js jalankanBuku) + selesai (susunSelesai). Kotak pasir potret ditambah buku khusus: buku 25 kg (indukUkuran), buku
wadah (stokWadah), karung wadah, karung belakang (merkAsal), buku adukan, merek pemasok, kemasan jadi, katalog harga (chip rak Jual).

  S1  ritual 5 Jan 2027 → kartu tampil (fase selesaikan) → SEMUA pemeriksaan sama (6 kelompok, 24 baris); sesudah "selesai" tetap sama
      (juga 20 Jan sesudah penjualan Januari); "selesai" yang belum diakui server = belum bisa diperiksa; berkas JSON
  S2  kapan tampil: sebelum ritual tidak; arsip belum habis tidak; selesai → sampai akhir Februari 2027 (10 Feb ya, 1 Mar tidak); ritual telat (selesai 20 Mar)
      → 30 hari sesudahnya; tutup buku tahun berikutnya: tahun = yang terakhir ditutup
  S3  KONTROL KOTAK (tiap kerusakan berbunyi di baris yang BENAR, bukan sekadar "ada yang beda"): modal pembuka diubah · satu merek pembuka dihapus · tanda
      buku 25 kg lepas · chip rak Jual hilang · potret bulan hilang / omzetnya berubah · stok minus disuntik ke saldo pembuka · piutang pembuka diubah
      (sesudah & sebelum hasil periksa dibekukan) · saldo pembuka tersembunyi (penanda hilang — kartu tetap tampil) · setoran PPh yang dipotret hilang;
      setoran masa Desember sesudah tutup buku BUKAN kerusakan
  S4  BELUM BISA DIPERIKSA ('?', bukan ✓): data belum selesai dimuat · koleksi ditolak server · kiriman tutup buku masih menunggu server · hasil periksa tidak
      dibekukan & titik kas sudah maju (uang per tempat; dengan hasil beku tetap ✓) · berita acara tanpa patokan hari tutup buku · tanpa potret · tanpa
      ringkasan per buku (jatuh ke dokumen pembuka, tetap sama) · koleksi hanya dimuat sebagian
  S5  stok minus HARI INI karena catatan sesudah tutup buku: disebut di keterangan, bukan alasan "beda" (yang diperiksa = saldo pembuka)
  S6  layar: uang.js ASLI digambar di jsc (Mac, tablet, HP: ringkasan, ✓ / ✗ dengan dua angka / ? dengan sebab, lihat semua, unduh) + statis: lokal app.js
      membawa keadaan muat; modul ada di modulepreload

    python3 alat-uji/uji_periksa_sesudah.py                    → N lulus · 0 gagal
    python3 alat-uji/uji_periksa_sesudah.py --kontrol          → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
    python3 alat-uji/uji_periksa_sesudah.py --cadangan=/jalur/backup-batch-….json   (atau env PERIKSA_ASAP=…) → simulasi ritual 2026 atas cadangan LOKAL:
        semua sama (dilewati di CI: cadangan toko tidak ada di repo; keluaran hanya jumlah baris & hitungan buku, tanpa rupiah)
"""
import os, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_kunci_periode  # noqa: E402
import uji_potret_tahun as UP  # noqa: E402

LOGIKA = 'baru/js/layar/periksa-sesudah-logika.js'
MODUL = UP.MODUL + [LOGIKA]
M_OK = {'siap': True, 'siapN': 56, 'total': 56, 'ditolak': []}

TAMBAH = r"""
// ---- kotak pasir potret + buku khusus (angka contoh) — ditulis 1 Des 2026, sebelum ritual
function tambahBukuKhusus() { terapkanKeCache([
  { koleksi: 'batchMasuk', data: { id: 'kb1', tanggal: '2026-12-01', jam: '08:00', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [
    { merk: 'Bebek', satuan: 'karung', beratKarung: 50, jumlahKarung: 10, totalKg: 500, hargaPerKg: 12000, subtotalHarga: 6000000 },
    { merk: 'Bebek 25 kg', satuan: 'karung', beratKarung: 25, jumlahKarung: 8, totalKg: 200, hargaPerKg: 12100, subtotalHarga: 2420000, indukUkuran: 'Bebek' },
    { merk: 'Kelas Contoh', satuan: 'karung', beratKarung: 50, jumlahKarung: 4, totalKg: 200, hargaPerKg: 10000, subtotalHarga: 2000000, merkPemasok: 'Merek Pemasok Contoh' },
    { merk: 'Tanpa Harga Contoh', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 10500, subtotalHarga: 1050000 },
    { merk: 'Wadah W1', satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, stokWadah: 'W1' },
    { merk: 'Karung wadah W1', satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, karungWadah: 'W1' },
    { merk: 'Karung belakang W1 · Bebek', satuan: 'karung', beratKarung: 50, jumlahKarung: 1, totalKg: 50, hargaPerKg: 12000, subtotalHarga: 600000, karungBelakang: 'W1', merkAsal: 'Bebek' },
    { merk: 'Adukan Kembang 5 kg', satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, bukuAdukan: 'Kembang|5' }] } },
  { koleksi: 'produksiKemasan', data: { id: 'kp1', tanggal: '2026-12-02', jam: '09:00', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 12, hppPerUnit: 61000, merkSumber: 'BELI JADI', kgDipakai: 0, beliJadi: true } },
  { koleksi: 'katalogHargaKarung', data: { id: 'Bebek', merk: 'Bebek', hargaPerKg: 13000 } }, { koleksi: 'katalogHargaKarung', data: { id: 'Kelas Contoh', merk: 'Kelas Contoh', hargaPerKg: 11000 } },
  { koleksi: 'katalogHargaKarung', data: { id: 'Angsa', merk: 'Angsa', hargaPerKg: 13800 } }, { koleksi: 'katalogHargaKarung', data: { id: 'Beo', merk: 'Beo', hargaPerKg: 14000 } }]); }
var M_OK = """ + json.dumps(M_OK) + r""";
function baris(H, id) { var x = null; H.kelompok.forEach(function (g) { g.baris.forEach(function (b) { if (b.id === id) x = b; }); }); return x; }
function ringkasH(H) { return H ? H.ringkas + ' | beda: ' + H.kelompok.reduce(function (o, g) { return o.concat(g.baris.filter(function (b) { return b.status !== 'sama'; }).map(function (b) { return b.id + '=' + b.status + ' ' + (b.sebab || '') + ' ' + (b.rincian || []).slice(0, 3).join('; '); })); }, []).join(' || ') : 'null'; }
/** Ritual penuh seperti uang.js: kunci → kiriman → arsip → hasil periksa dibekukan (pemegang = LA). */
function ritualPenuh(w) { var R = ritual(w); if (R.tolak) return R; var PA = susunPeriksaArsip(2026, w, LA, true); if (PA.dokumen) kirim({ dokumen: PA.dokumen }); return R; }
function siapKotak(isoJam) { var w = persiapkan(jam(isoJam || '2027-01-05T10:00:00+07:00')); tambahBukuKhusus();
  // setoran PPh masa Juli (dicatat Agustus, sebelum ritual) — ikut potret pajak
  var wJul = jam('2026-08-14T10:00:00+07:00'); tulis(susunSetoran({ masaPajak: '2026-07', tanggalSetor: '2026-08-14', jumlah: String(Math.max(1, pjTahun(2026, new Date(__KINI)).daftar[6].pph || 1)), ntpn: 'AB12CD34EF56GH78', catatan: 'bukti kertas contoh' }, wJul, new Date(__KINI)));
  jam(w.kini); return w; }
/** Ubah satu dokumen di cache (salinan, tanpa penjaga — kerusakan SESUDAH ritual, mis. lewat Console). */
function ubahDok(koleksi, cari, ubah) { var k = KOLEKSI.filter(function (x) { return x.nama === koleksi; })[0]; var d = cacheMentah(k.cache).filter(cari)[0]; if (!d) throw new Error('kontrol: dokumen ' + koleksi + ' tidak ketemu'); var b = JSON.parse(JSON.stringify(d)); ubah(b); terapkanKeCache([{ koleksi: koleksi, data: b }]); return b; }
function hapusDok(koleksi, id) { terapkanKeCache([{ koleksi: koleksi, hapus: id }]); }
"""

SKENARIO = r"""
// ==================== S1 · ritual 5 Jan 2027 → semua sama ====================
var W, H0;
coba('S1', function () {
  W = siapKotak();
  ok('S1 sebelum ritual: kartu tidak tampil (belum ada tahun yang ditutup sistem ini)', pstTahun(new Date(__KINI)) === null && pstPeriksa(new Date(__KINI), M_OK) === null);
  var R = ritualPenuh(W); if (R.tolak) throw new Error('ritual ditolak: ' + R.tolak);
  var A = acara(2026);
  ok('S1 berita acara menyimpan ringkasan saldo pembuka per buku (ringkasPembuka): baris beras bertanda & kemasan, bentuk diterima Firestore',
    A.pembukaRingkas && A.pembukaRingkas.versi === 1 && A.pembukaRingkas.beras.some(function (r) { return r.merk === 'Bebek 25 kg' && r.indukUkuran === 'Bebek' && r.kg === 200; }) && A.pembukaRingkas.kemasan.some(function (k) { return k.nama === 'Kembang' && k.unit === 12; }) && !bentukFirestore(A.pembukaRingkas).length, J(A.pembukaRingkas && A.pembukaRingkas.beras.slice(0, 3)));
  var T = pstTahun(new Date(__KINI));
  ok('S1 sesudah kunci & arsip habis: kartu tampil untuk 2026, fase selesaikan (berita acara terkunci)', T && T.tahun === 2026 && T.fase === 'selesaikan' && T.acara.status === 'terkunci', J(T && { tahun: T.tahun, fase: T.fase }));
  H0 = pstPeriksa(new Date(__KINI), M_OK);
  ok('S1 SEMUA pemeriksaan sama: 6 kelompok, 24 baris, 0 beda, 0 belum; ringkasan "Semua 24 pemeriksaan sama — tutup buku 2026 beres"',
    H0 && H0.beres && H0.n === 24 && H0.nBeda === 0 && H0.nBelum === 0 && H0.kelompok.length === 6 && H0.ringkas === 'Semua 24 pemeriksaan sama — tutup buku 2026 beres', ringkasH(H0));
  ok('S1 baris perbandingan memakai hasil yang DIBEKUKAN saat arsip habis (bkPeriksaDipakai), 11 baris + 3 utang/piutang di kelompok 6 (tidak dobel)',
    /dibekukan saat arsip habis/.test(H0.sumber) && H0.kelompok[0].baris.length === 11 && H0.kelompok[5].baris.map(function (b) { return b.id; }).join(',') === 'piutang,utangP,utangO'
    && H0.kelompok[0].baris.every(function (b) { return ['piutang', 'utangP', 'utangO'].indexOf(b.id) < 0; }), J([H0.sumber, H0.kelompok[0].baris.map(function (b) { return b.id; })]));
  var c3 = baris(H0, 'rakJual'), c1 = baris(H0, 'bukuMerek'), c2 = baris(H0, 'bukuKemasan'), mb = baris(H0, 'modalPembuka');
  ok('S1 rak Jual: chip karung Bebek 50 & "Bebek" 25 kg (buku Bebek 25 kg), Kelas Contoh, Angsa, Beo; 5 tanda buku terbaca (25 kg, wadah, karung wadah, karung belakang, adukan); merek tanpa harga disebut, bukan beda',
    c3.status === 'sama' && /^5 chip karung di rak Jual, 5 tanda buku/.test(c3.ket) && /1 baris tanpa harga di katalog/.test(c3.ket), J(c3));
  ok('S1 buku beras per merek & kemasan saat 2027 dibuka = saldo pembuka (pembanding: ringkasan di berita acara); modal pembuka = neraca 31 Des di potret',
    c1.status === 'sama' && /ringkasan saldo pembuka di berita acara/.test(c1.ket) && c1.a > 0 && Math.abs(c1.a - c1.b) < 0.01 && c2.status === 'sama' && c2.a === 12 && mb.status === 'sama' && mb.a === mb.b && /neraca 31 Des di potret/.test(mb.ket), J([c1, c2, mb]));
  ok('S1 pajak 2026 dari potret: 12 bulan, omzet = potret, setoran Juli = potret, layar Pajak 12 masa bertanda tutup buku',
    ['pajakPotret', 'pajakOmzet', 'pajakSetor', 'pajakLayar'].every(function (id) { return baris(H0, id).status === 'sama'; }) && baris(H0, 'pajakOmzet').a > 0 && baris(H0, 'pajakSetor').a > 0, J(H0.kelompok[3]));
  ok('S1 petunjuk fase selesaikan menyebut langkah berikutnya (cadangan sesudah · selesai, lalu unduh hasil pemeriksaan) — tanpa orang luar', H0.petunjuk.length === 1 && /unduh cadangan sesudah · selesai/.test(H0.petunjuk[0]) && !/claude/i.test(J(H0)), J(H0.petunjuk));
  var B = pstBerkas(H0, new Date(__KINI));
  ok('S1 berkas hasil pemeriksaan (JSON): nama per tahun, 6 kelompok, 24 baris bertanda "sama", ringkasan & status berita acara', B.nama === 'pemeriksaan-tutup-buku-2026-miqbal.json' && B.isi.kelompok.length === 6 && B.isi.n === 24
    && B.isi.kelompok.reduce(function (a, g) { return a + g.baris.filter(function (b) { return b.hasil === 'sama'; }).length; }, 0) === 24 && B.isi.beritaAcara.status === 'terkunci' && JSON.parse(J(B.isi)).ringkasan === H0.ringkas, J(B.nama));
  // selesai (cadangan sesudah) → status selesai, tetap sama
  var wS = jam('2027-01-05T11:00:00+07:00'); tulis(susunSelesai(2026, 'cadangan-sesudah-contoh.json', wS, false, LA));
  var H1 = pstPeriksa(new Date(__KINI), M_OK);
  ok('S1 sesudah "selesai": kartu tetap tampil, semua sama, petunjuk = simpan berkas bersama cadangan SESUDAH & kunci Januari mulai 4 Feb', acara(2026).status === 'selesai' && H1 && H1.beres && H1.fase === 'selesai' && /cadangan SESUDAH/.test(H1.petunjuk[0]) && /4 Feb/.test(H1.petunjuk[0]), ringkasH(H1));
  setelTertunda('tutupBukuAcara', ['2026']); var H1t = pstPeriksa(new Date(__KINI), M_OK); setelTertunda('tutupBukuAcara', []);
  ok('S1 berita acara "selesai" yang belum diakui server (menunggu di perangkat ini) → semua "belum bisa diperiksa", bukan beres', H1t.nBelum === H1t.n && !H1t.beres && /menunggu server/.test(baris(H1t, 'modalPembuka').sebab), ringkasH(H1t));
  jam('2027-01-20T10:00:00+07:00'); var H2 = pstPeriksa(new Date(__KINI), M_OK);
  ok('S1 20 Jan 2027 (penjualan Januari berjalan): tetap semua sama — yang diperiksa saldo pembuka & hasil yang dibekukan, bukan stok hari ini', H2 && H2.beres, ringkasH(H2));
});

// ==================== S2 · kapan kartu tampil ====================
coba('S2', function () {
  var w = siapKotak(); putusSemua(w); var R = susunKunci(2026, D, w, LA); R.kiriman.forEach(kirim);
  ok('S2 terkunci tetapi arsip BELUM habis: kartu tidak tampil (pita tutup buku menyuruh meneruskan arsip)', pstTahun(new Date(__KINI)) === null);
  arsipkanDokumen(2026, arsipBuku(2026).daftar); var PA = susunPeriksaArsip(2026, w, LA, true); kirim({ dokumen: PA.dokumen });
  ok('S2 arsip habis → tampil', !!pstTahun(new Date(__KINI)));
  tulis(susunSelesai(2026, 'cadangan-sesudah-contoh.json', jam('2027-01-05T12:00:00+07:00'), false, LA));
  jam('2027-02-10T10:00:00+07:00'); var a = !!pstTahun(new Date(__KINI)); jam('2027-02-28T23:00:00+07:00'); var b = !!pstTahun(new Date(__KINI)); jam('2027-03-01T08:00:00+07:00'); var c = !!pstTahun(new Date(__KINI));
  ok('S2 selesai 5 Jan: tampil 10 Feb & 28 Feb, tidak tampil 1 Mar 2027', a && b && !c, J([a, b, c]));
  ubahDok('tutupBukuAcara', function (x) { return Number(x.tahun) === 2026; }, function (x) { x.selesaiTanggal = '2027-03-20'; });
  jam('2027-04-18T10:00:00+07:00'); var d = !!pstTahun(new Date(__KINI)); jam('2027-04-20T10:00:00+07:00'); var e = !!pstTahun(new Date(__KINI));
  ok('S2 ritual telat (selesai 20 Mar): tampil sampai 30 hari sesudahnya (18 Apr ya, 20 Apr tidak)', d && !e, J([d, e]));
  // tahun berikutnya: berita acara 2027 selesai (tiruan) → tahun = 2027 (yang terakhir ditutup)
  terapkanKeCache([{ koleksi: 'batchMasuk', data: { id: 'tb2027', tanggal: '2028-01-01', pemasok: 'TUTUP BUKU 2027', stokAwal: true, merkList: [], tutupBuku: true, tahunDari: 2027, bertahap: true, penandaBuku: true } },
    { koleksi: 'tutupBukuAcara', data: { id: '2027', tahun: 2027, status: 'selesai', tanggal: '2028-01-02', selesaiTanggal: '2028-01-02', paraf: { pada: '2028-01-02T03:00:00.000Z' } } }]);
  jam('2028-01-10T10:00:00+07:00'); var T = pstTahun(new Date(__KINI));
  ok('S2 tutup buku tahun berikutnya: kartu memeriksa 2027 (tahun yang terakhir ditutup), bukan 2026', T && T.tahun === 2027, J(T && T.tahun));
});

// ==================== S3 · kontrol kotak: tiap kerusakan berbunyi di barisnya ====================
function siapRitual() { var w = siapKotak(); var R = ritualPenuh(w); if (R.tolak) throw new Error('ritual ditolak: ' + R.tolak); var H = pstPeriksa(new Date(__KINI), M_OK); if (!H || !H.beres) throw new Error('kotak tidak beres sebelum dirusak: ' + ringkasH(H)); return w; }
function hasilRusak() { var H = pstPeriksa(new Date(__KINI), M_OK); return H; }
coba('S3-modal', function () { siapRitual(); ubahDok('modalOwner', function (x) { return x.tutupBuku && x.tahunDari === 2026; }, function (x) { x.nominal += 1000000; });
  var H = hasilRusak(); var m = baris(H, 'modalPembuka');
  ok('S3 modal pembuka diubah → baris "Modal owner" BEDA dengan dua angkanya (neraca 31 Des vs saldo pembuka), ringkasan "jangan jualan/menagih dulu"', m.status === 'beda' && m.b - m.a === 1000000 && /^\d+ pemeriksaan beda — jangan jualan\/menagih dulu, lihat barisnya/.test(H.ringkas) && H.petunjuk.some(function (p) { return /Modal owner di buku 2027/.test(p) && /batalkan/.test(p); }), ringkasH(H)); });
coba('S3-merek', function () { siapRitual(); ubahDok('batchMasuk', function (x) { return x.tutupBuku && x.tahunDari === 2026 && (x.merkList || []).some(function (r) { return r.merk === 'Bebek 25 kg'; }); }, function (x) { x.merkList = x.merkList.filter(function (r) { return r.merk !== 'Bebek 25 kg'; }); });
  var H = hasilRusak(); var c1 = baris(H, 'bukuMerek'), c3 = baris(H, 'rakJual');
  ok('S3 satu merek pembuka dihapus → "Buku beras per merek" BEDA menyebut Bebek 25 kg (TIDAK ADA di buku) & rak Jual BEDA (25 kg tidak terbaca / tidak tampil)',
    c1.status === 'beda' && c1.rincian.some(function (t) { return /^Bebek 25 kg: saldo pembuka 200 kg → TIDAK ADA di buku$/.test(t); }) && c3.status === 'beda' && c3.rincian.some(function (t) { return /Bebek 25 kg/.test(t); }), J([c1.rincian, c3.rincian])); });
coba('S3-tanda', function () { siapRitual(); ubahDok('batchMasuk', function (x) { return x.tutupBuku && x.tahunDari === 2026 && (x.merkList || []).some(function (r) { return r.merk === 'Bebek 25 kg'; }); }, function (x) { x.merkList.forEach(function (r) { if (r.merk === 'Bebek 25 kg') delete r.indukUkuran; }); });
  var H = hasilRusak(); var c3 = baris(H, 'rakJual'), c1 = baris(H, 'bukuMerek');
  ok('S3 tanda buku 25 kg lepas dari dokumen pembuka (kg tetap) → rak Jual BEDA: tanda tidak terbaca & chip tampil sebagai "Bebek 25 kg" / tidak tampil; buku per merek tetap sama',
    c3.status === 'beda' && c3.rincian.some(function (t) { return /Bebek 25 kg: tanda buku 25 kg \(induk Bebek\) tidak terbaca/.test(t); }) && c1.status === 'sama', J(c3.rincian)); });
coba('S3-potret', function () { siapRitual(); ubahDok('tutupBukuAcara', function (x) { return Number(x.tahun) === 2026; }, function (x) { delete x.potret.bulan['2026-08']; });
  var H = hasilRusak(); var d1 = baris(H, 'pajakPotret');
  ok('S3 potret satu bulan hilang → "Potret 2026: 12 bulan lengkap" BEDA (11 dari 12, menyebut 2026-08), omzet & layar Pajak ikut BEDA', d1.status === 'beda' && d1.b === 11 && d1.rincian.join() === '2026-08 tidak ada di potret' && baris(H, 'pajakLayar').status === 'beda', J([d1, baris(H, 'pajakLayar').rincian])); });
coba('S3-chip', function () { siapRitual(); ubahDok('batchMasuk', function (x) { return x.tutupBuku && x.tahunDari === 2026 && (x.merkList || []).some(function (r) { return r.merk === 'Kelas Contoh'; }); }, function (x) { x.merkList.forEach(function (r) { if (r.merk === 'Kelas Contoh') r.beratKarung = '50'; }); });
  var H = hasilRusak(); var c3 = baris(H, 'rakJual'), c1 = baris(H, 'bukuMerek');
  ok('S3 baris pembuka Kelas Contoh rusak bentuknya (berat karung jadi teks, kg tetap) → rak Jual BEDA: "Kelas Contoh 50 kg … tidak tampil di rak Jual"; buku per merek tetap sama',
    c3.status === 'beda' && c3.rincian.join() === 'Kelas Contoh 50 kg (buku Kelas Contoh): tidak tampil di rak Jual' && c1.status === 'sama', J([c3.rincian, c1.status])); });
coba('S3-potret-omzet', function () { siapRitual(); ubahDok('tutupBukuAcara', function (x) { return Number(x.tahun) === 2026; }, function (x) { x.potret.bulan['2026-08'].omzet += 1000; });
  var H = hasilRusak(); var d2 = baris(H, 'pajakOmzet');
  ok('S3 omzet satu bulan di potret berubah (12 bulan tetap lengkap) → "Omzet 2026 di Laporan › Pajak = potret" BEDA, dua angkanya berselisih Rp1.000', d2.status === 'beda' && d2.b - d2.a === 1000 && baris(H, 'pajakPotret').status === 'sama', J(d2)); });
coba('S3-minus', function () { siapRitual(); terapkanKeCache([{ koleksi: 'stokBahanKemasan', data: { id: 'suntik-minus', tipe: 'saldoAwal', jenis: 'paperbag5l', jumlah: -20, hargaTotal: 0, tanggal: '2027-01-01', catatan: 'kontrol', tutupBuku: true, tahunDari: 2026, bertahap: true } }]);
  var H = hasilRusak(); var e1 = baris(H, 'minus');
  ok('S3 stok minus disuntik ke saldo pembuka (kantong −20) → "Tidak ada stok minus" BEDA dengan buku & jalannya', e1.status === 'beda' && e1.a === '1 buku minus' && /minus 20 lembar/.test(e1.rincian[0]) && /Stok › Kantong/.test(e1.rincian[0]), J(e1)); });
coba('S3-piutang', function () { siapRitual(); ubahDok('piutangMutasi', function (x) { return x.tutupBuku && x.tahunDari === 2026 && x.tipe === 'saldoAwal'; }, function (x) { x.nominal += 250000; });
  var H = hasilRusak(); var c0 = baris(H, 'pembuka');
  ok('S3 piutang pembuka diubah SESUDAH hasil dibekukan → "Saldo pembuka di buku = berita acara 31 Des" BEDA menyebut piutang pelanggan (Rp250.000 lebih)',
    c0.status === 'beda' && c0.rincian.some(function (t) { var m = /^Piutang pelanggan: berita acara (Rp[\d.]+) → saldo pembuka di buku (Rp[\d.]+)$/.exec(t); return !!m && Number(m[2].replace(/\D/g, '')) - Number(m[1].replace(/\D/g, '')) === 250000; }), J(c0.rincian)); });
coba('S3-piutang-awal', function () {
  // piutang pembuka berubah SEBELUM arsip habis (hasil periksa belum dibekukan) → kelompok 6 menghitung ulang dari mesin
  var w = siapKotak(); putusSemua(w); var R = susunKunci(2026, D, w, LA); R.kiriman.forEach(kirim); arsipkanDokumen(2026, arsipBuku(2026).daftar);
  ubahDok('piutangMutasi', function (x) { return x.tutupBuku && x.tahunDari === 2026 && x.tipe === 'saldoAwal'; }, function (x) { x.nominal += 250000; });
  var PA = susunPeriksaArsip(2026, w, LA, true); kirim({ dokumen: PA.dokumen });
  var H = hasilRusak(); var p = baris(H, 'piutang');
  ok('S3 piutang pembuka berubah sebelum hasil dibekukan → baris "Piutang pelanggan" di kelompok 6 BEDA (dua angka, selisih Rp250.000)', p.status === 'beda' && p.b - p.a === 250000 && H.kelompok[5].baris.indexOf(p) >= 0, J(p)); });
coba('S3-sembunyi', function () { siapRitual(); var tanda = cacheMentah('batch').filter(function (x) { return x.tutupBuku && x.tahunDari === 2026 && x.penandaBuku; })[0];
  ubahDok('batchMasuk', function (x) { return x.id === tanda.id; }, function (x) { delete x.penandaBuku; });
  var H = hasilRusak(); ok('S3 penanda tutup buku hilang → kartu TETAP tampil (tahun dibaca dari berita acara, bukan dari era yang ikut mundur)', !!H && H.tahun === 2026 && eraBuku() !== 2026, J([eraBuku(), H && H.tahun])); if (!H) return;
  var c0 = baris(H, 'pembuka'), c1 = baris(H, 'bukuMerek');
  ok('S3 penanda tutup buku hilang (saldo pembuka bertahap tersembunyi dari mesin) → kartu TETAP tampil; saldo pembuka BEDA ("tersembunyi"), buku per merek BEDA, Pajak 2026 tidak lagi dari potret (BEDA)', c0.status === 'beda' && c0.rincian.some(function (t) { return /tersembunyi dari mesin/.test(t); }) && c1.status === 'beda' && baris(H, 'pajakLayar').status === 'beda' && baris(H, 'pajakOmzet').status === 'beda', J([c0.rincian.slice(0, 2), c1.rincian.slice(0, 2)])); });
coba('S3-setoran', function () { siapRitual(); var s = cacheMentah('pajakSetoran').filter(function (x) { return x.masaPajak === '2026-07'; })[0]; hapusDok('pajakSetoran', s.id);
  var H = hasilRusak(); var d3 = baris(H, 'pajakSetor');
  ok('S3 setoran PPh yang dipotret hilang → "Setoran PPh 2026 = potret" BEDA menyebut masa 2026-07', d3.status === 'beda' && /^2026-07: potret Rp[\d.]+ → sekarang Rp0$/.test(d3.rincian[0]), J(d3)); });
coba('S3-setoran-baru', function () { siapRitual(); var w = jam('2027-01-10T10:00:00+07:00'); tulis(susunSetoran({ masaPajak: '2026-12', tanggalSetor: '2027-01-10', jumlah: '50000', ntpn: '1234ABCD5678EFGH' }, w, new Date(__KINI)));
  var H = hasilRusak(); var d3 = baris(H, 'pajakSetor');
  ok('S3 (bukan kerusakan) setoran masa Desember dicatat 10 Jan sesudah tutup buku → setoran tetap SAMA, keterangan menyebut tambahannya', d3.status === 'sama' && /termasuk Rp50\.000 yang dicatat pada\/sesudah hari tutup buku \(5 Jan 2027\)/.test(d3.ket) && d3.b - d3.a === 50000, J(d3)); });

// ==================== S4 · belum bisa diperiksa ('?', bukan ✓) ====================
coba('S4', function () {
  siapRitual(); var k = new Date(__KINI);
  var H1 = pstPeriksa(k, { siap: false, siapN: 30, total: 56, ditolak: [] });
  ok('S4 data belum selesai dimuat → SEMUA baris "belum bisa diperiksa" dengan sebabnya, ringkasan bukan "beres"', H1.nBelum === H1.n && !H1.beres && /^24 dari 24 pemeriksaan belum bisa diperiksa — tutup buku 2026 belum bisa dinyatakan beres/.test(H1.ringkas) && H1.kelompok.every(function (g) { return g.baris.every(function (b) { return /belum selesai dimuat di perangkat ini \(30 dari 56 koleksi\)/.test(b.sebab); }); }), ringkasH(H1));
  var H2 = pstPeriksa(k, { siap: true, siapN: 56, total: 56, ditolak: ['modalOwner'] });
  ok('S4 koleksi modalOwner ditolak server → baris modal "belum", baris yang tidak membutuhkannya tetap diperiksa', baris(H2, 'modalPembuka').status === 'belum' && /modalOwner ditolak server/.test(baris(H2, 'modalPembuka').sebab) && baris(H2, 'pajakOmzet').status === 'sama' && baris(H2, 'beras').status === 'sama', ringkasH(H2));
  var H2b = pstPeriksa(k, { siap: true, siapN: 56, total: 56, ditolak: [], sebagian: ['batchMasuk'] });
  ok('S4 koleksi hanya dimuat sebagian (hemat baca) → baris stok "belum"', baris(H2b, 'bukuMerek').status === 'belum' && /hanya dimuat sebagian/.test(baris(H2b, 'bukuMerek').sebab), ringkasH(H2b));
  setelTertunda('tutupBukuAcara', ['2026']); var H3 = pstPeriksa(k, M_OK); setelTertunda('tutupBukuAcara', []);
  ok('S4 berita acara masih menunggu server di perangkat ini → semua "belum" (tunggu antrean kosong)', H3.nBelum === H3.n && /menunggu server/.test(baris(H3, 'beras').sebab), ringkasH(H3));
});
coba('S4-beku-kas', function () {
  // hasil periksa DIBEKUKAN saat arsip habis + titik kas maju (tutup hari 10 Jan) → uang per tempat tetap diperiksa dari hasil beku (✓), bukan "?"
  siapRitual(); var w = jam('2027-01-10T21:00:00+07:00'); terapkanKeCache([{ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: '2027-01-10', laci: 1000000, rekening: 2000000, amplop: 0, brankas: 3000000, diubahPada: w.kini } }]);
  var H = pstPeriksa(new Date(__KINI), M_OK);
  ok('S4 hasil beku + titik kas sudah maju (tutup hari Januari) → uang per tempat tetap SAMA dari hasil yang dibekukan, semua beres', ['laci', 'brankas', 'rekening', 'amplop'].every(function (id) { return baris(H, id).status === 'sama'; }) && H.beres && /dibekukan saat arsip habis/.test(H.sumber), ringkasH(H)); });
coba('S4-kas', function () {
  // hasil periksa TIDAK dibekukan (dokumen periksaArsip hilang) dan titik kas sudah maju (tutup hari 10 Jan) → uang per tempat '?' (mesin tidak menghitung mundur)
  siapRitual(); hapusDok('pengaturan', 'periksaArsip2026');
  var w = jam('2027-01-10T21:00:00+07:00'); terapkanKeCache([{ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: '2027-01-10', laci: 1000000, rekening: 2000000, amplop: 0, brankas: 3000000, diubahPada: w.kini } }]);
  var H = pstPeriksa(new Date(__KINI), M_OK); var kas = ['laci', 'brankas', 'rekening', 'amplop'].map(function (id) { return baris(H, id); });
  ok('S4 tanpa hasil yang dibekukan & titik kas sudah maju → baris uang per tempat "belum bisa diperiksa" (bukan ✓), stok tetap diperiksa, sumber "dihitung ulang sekarang"',
    kas.every(function (b) { return b.status === 'belum' && /titik kas sudah maju/.test(b.sebab); }) && baris(H, 'beras').status === 'sama' && /dihitung ulang sekarang/.test(H.sumber) && !H.beres, ringkasH(H)); });
coba('S4-tanpa', function () {
  siapRitual(); ubahDok('tutupBukuAcara', function (x) { return Number(x.tahun) === 2026; }, function (x) { delete x.hariIni; delete x.potret; delete x.pembukaRingkas; });
  hapusDok('pengaturan', 'periksaArsip2026');
  var H = pstPeriksa(new Date(__KINI), M_OK);
  ok('S4 berita acara tanpa patokan hari tutup buku → kelompok 1 & 6 "belum" (tidak bisa diulang), bukan ✓', H.kelompok[0].baris.concat(H.kelompok[5].baris).every(function (b) { return b.status === 'belum' && /tidak menyimpan patokan hari tutup buku/.test(b.sebab); }) && H.kelompok[0].baris.length + H.kelompok[5].baris.length === 14, ringkasH(H));
  ok('S4 tanpa potret → "12 bulan lengkap" BEDA (Laporan & Pajak hanya di arsip), omzet/setoran/layar "belum"; modal memakai angka berita acara', baris(H, 'pajakPotret').status === 'beda' && ['pajakOmzet', 'pajakSetor', 'pajakLayar'].every(function (id) { return baris(H, id).status === 'belum'; }) && baris(H, 'modalPembuka').status === 'sama' && /berita acara \(tanpa potret\)/.test(baris(H, 'modalPembuka').ket), ringkasH(H));
  ok('S4 tanpa ringkasan per buku → pembanding jatuh ke dokumen saldo pembuka (disebut), tetap sama', baris(H, 'bukuMerek').status === 'sama' && /dokumen saldo pembuka \(berita acara tanpa ringkasan per buku\)/.test(baris(H, 'bukuMerek').ket) && baris(H, 'rakJual').status === 'sama', J(baris(H, 'bukuMerek')));
});

// ==================== S5 · stok minus HARI INI (catatan sesudah tutup buku) ====================
coba('S5', function () {
  siapRitual(); var w = jam('2027-01-06T10:00:00+07:00'); terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'lebih1', tanggal: '2027-01-06', jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Bebek 25 kg', totalKg: 300, beratKarungAcuan: 25, jumlahKarung: 12, hargaTotal: 3900000, hppTotalSaatJual: 3630000, trxId: 't-lebih1' } }]);
  var H = pstPeriksa(new Date(__KINI), M_OK); var e1 = baris(H, 'minus');
  ok('S5 penjualan Januari melebihi buku (Bebek 25 kg −100 kg) → baris saldo pembuka tetap SAMA, keterangan menyebut minus hari ini & jalannya (Stok › Cocokkan)', e1.status === 'sama' && /CATATAN: hari ini 1 buku minus karena catatan sesudah tutup buku \(Buku Bebek 25 kg minus 100 kg\)/.test(e1.ket) && /Stok › Cocokkan/.test(e1.ket) && H.beres, J(e1));
});
"""


# ---- S6 · layar Uang › Tutup buku ASLI digambar di jsc (uang.js + modul impornya; peramban tidak dinyalakan) ----
MODUL_LAYAR = MODUL + ['baru/js/inti/dom.js', 'baru/js/inti/kunci.js', 'baru/js/inti/keadaan.js', 'baru/js/inti/isian.js', 'baru/js/inti/jadwal.js', 'baru/js/inti/gerak.js',
                       'baru/js/layar/akses-layar.js', 'baru/js/layar/uang.js']
LAYAR = r"""
var __html = ''; pasang = function (akar, isi) { __html = isi && isi.__mentah ? isi.html : String(isi); }; delegasi = function () {}; gulirkan = function () {}; nanti = function () {}; segera = function () {};
setelKunci(false); var __lebar = 1100; window.matchMedia = function (q) { var m = /min-width: (\d+)px/.exec(q); return { matches: !!m && __lebar >= Number(m[1]) }; }; window.addEventListener = function () {};
if (typeof setTimeout === 'undefined') { var setTimeout = function () { return 0; }; var clearTimeout = function () {}; }
var NS = new Proxy({}, { get: function (o, k) { return (0, eval)(String(k)); } }); var UG = NS, UP = NS, OT = NS, TD = NS, BK = NS, KP = NS, PST = NS, WB = NS;
// ekspor berganti nama (`export { a as b }` dibuang bundel) — nama yang dipakai uang.js lewat ruang nama
var kpNama = kpNamaBulan, kpWaktu = kpWib, PILIHAN_POTONG = UP_POTONG, bkRP = RP, tdAngka = ANGKA;
var akarU = { classList: { add: function () {}, remove: function () {} }, firstElementChild: null, offsetWidth: 0 };
var __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [] };
var U = null; var gambarU = function (patch) { U.keadaan.setel(patch || {}); U.gambar(); return __html; };
function rusakHtml(t) { return /NaN|undefined|\[object Object\]/.test(t.replace(/data-[a-z-]+="[^"]*"/g, '')); }
coba('S6', function () {
  siapRitual(); setelSumber('firestore', 'kotak pasir');
  U = pasangLayarUang(akarU, { akun: function () { return { jenis: 'owner' }; }, gantiMode: function () {}, mode: function () { return 'terang'; }, sekarang: function () { return new Date(__KINI); }, statusRingkas: function () { return 'owner'; }, pindah: function () {},
    lokal: function () { return { antre: [], menunggu: 0, idPerangkat: 'mac-contoh', namaPerangkat: 'Mac contoh', offline: false, koleksiSiap: __muat.koleksiSiap, koleksiTotal: __muat.koleksiTotal, ditolak: __muat.ditolak, sebagian: __muat.sebagian || [], antreLokal: { belum: [], ditolak: [] }, parkir: [] }; }, bukaStok: function () {} });
  U.tampilkan(true);
  var mac = gambarU({ keluarga: 'buku' }); __lebar = 400; var hp = gambarU({ keluarga: 'buku' }); __lebar = 800; var tab = gambarU({ keluarga: 'buku' }); __lebar = 1100;
  ok('S6 uang.js ASLI (Mac, tablet, HP): kartu "Pemeriksaan sesudah tutup buku 2026" digambar di Tutup buku dengan ringkasan "Semua 24 pemeriksaan sama", tombol unduh & lihat semua; tanpa NaN/undefined',
    [mac, hp, tab].every(function (t) { return /data-k="tb-periksa"/.test(t) && /Pemeriksaan sesudah tutup buku 2026/.test(t) && /data-k="pst-ringkas">Semua 24 pemeriksaan sama — tutup buku 2026 beres</.test(t) && /data-aksi="pstUnduh"/.test(t) && /lihat semua 24 baris/.test(t) && !rusakHtml(t); }),
    J([mac.length, (mac.match(/data-k="pst-ringkas">[^<]*/) || [''])[0], rusakHtml(mac) ? (mac.replace(/data-[a-z-]+="[^"]*"/g, '').match(/.{60}(NaN|undefined|\[object Object\]).{40}/) || [''])[0] : '']));
  ok('S6 bawaan: baris yang SAMA disembunyikan (6 judul kelompok "semua … sama"); "lihat semua" menggambar 24 baris bertanda ✓', (mac.match(/class="tb-cek [a-z]+" data-k="pst-/g) || []).length === 0 && (mac.match(/data-k="pstk-/g) || []).length === 6
    && (gambarU({ pstRinci: true }).match(/class="tb-cek ok" data-k="pst-/g) || []).length === 24, J((gambarU({ pstRinci: true }).match(/data-k="pst-[a-zA-Z]+"/g) || []).length));
  ubahDok('modalOwner', function (x) { return x.tutupBuku && x.tahunDari === 2026; }, function (x) { x.nominal += 1000000; });
  var rusak = gambarU({ pstRinci: false });
  ok('S6 ada yang beda: kartu bertanda awas, baris modal digambar ✗ dengan DUA angka (sebelum → sesudah) & petunjuk jalannya; baris yang sama tetap tersembunyi',
    /class="kartu awas" data-k="tb-periksa"/.test(rusak) && /class="tb-cek tidak" data-k="pst-modalPembuka"><span class="t">✗<\/span>/.test(rusak) && /data-k="pst-modalPembuka">[\s\S]*?Rp[\d.]+ → Rp[\d.]+/.test(rusak) && /data-k="pst-petunjuk-0">Modal owner di buku 2027/.test(rusak) && /\d pemeriksaan beda — jangan jualan\/menagih dulu/.test(rusak), (rusak.match(/data-k="pst-modalPembuka">.{0,400}/) || [''])[0]);
  __muat = { koleksiSiap: 20, koleksiTotal: 56, ditolak: [] }; var belum = gambarU({ pstRinci: false }); __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [] };
  ok('S6 data belum selesai dimuat: baris digambar "?" (kelas belum) dengan sebabnya — bukan ✓, bukan ✗', (belum.match(/class="tb-cek belum" data-k="pst-[a-zA-Z]+"><span class="t">\?<\/span>/g) || []).length === 24 && /belum bisa diperiksa — data toko belum selesai dimuat di perangkat ini \(20 dari 56 koleksi\)/.test(belum) && !/class="tb-cek ok" data-k="pst-/.test(belum), J((belum.match(/class="tb-cek [a-z]+" data-k="pst-[a-zA-Z]+"/g) || [])));
  __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [], sebagian: ['batchMasuk'] }; var sbg = gambarU({ pstRinci: false }); __muat = { koleksiSiap: 56, koleksiTotal: 56, ditolak: [] };
  ok('S6 lokal() menyebut koleksi yang hanya dimuat sebagian (hemat baca) → baris stok digambar "?" dengan sebabnya', /class="tb-cek belum" data-k="pst-bukuMerek"/.test(sbg) && /koleksi batchMasuk hanya dimuat sebagian di perangkat ini/.test(sbg), (sbg.match(/data-k="pst-ringkas">[^<]*/) || [''])[0]);
  setelSumber('belum', ''); var tanpa = gambarU({}); setelSumber('cadangan', 'kotak pasir'); var cad = gambarU({});
  ok('S6 belum tersambung ke data toko: semua "belum bisa diperiksa"; membaca berkas cadangan = data lengkap (diperiksa)', /data-k="pst-ringkas">24 dari 24 pemeriksaan belum bisa diperiksa/.test(tanpa) && /data-k="pst-ringkas">\d pemeriksaan beda/.test(cad), (cad.match(/data-k="pst-ringkas">[^<]*/) || [''])[0]);
});
"""


def bundelan_layar():
    import re
    bagian = [bundel_baru.PRELUDE]
    for m in MODUL_LAYAR:
        teks = open(os.path.join(AKAR, m), encoding='utf-8').read()
        teks = re.sub(r"^(\s*import\s[^;\n]*;)\s*//.*$", r"\1", teks, flags=re.M)
        bagian.append('\n// ===== ' + m + ' =====\n' + bundel_baru.polos(teks))
    return uji_kunci_periode.satu_lingkup('\n'.join(bagian))


def utama(js, cek_statis=True, js_layar=None):
    h, e = UP.jalan(UP.JAM + js + '\nvar KOTAK = ' + json.dumps(UP.KOTAK) + ';\n' + UP.BERSAMA + TAMBAH + SKENARIO + '\nprint(JSON.stringify({ lulus: lulus, gagal: gagal }));\n')
    if h is None: return 0, ['JSC JATUH: ' + e]
    l, g = h['lulus'], h['gagal'] + (statis() if cek_statis else [])
    if js_layar:
        h2, e2 = UP.jalan(UP.JAM + js_layar + '\nvar KOTAK = ' + json.dumps(UP.KOTAK) + ';\n' + UP.BERSAMA + TAMBAH + SKENARIO.split('// ==================== S1 ·')[0]
                          + "function siapRitual() { var w = siapKotak(); var R = ritualPenuh(w); if (R.tolak) throw new Error('ritual ditolak: ' + R.tolak); return w; }\n" + LAYAR
                          + '\nprint(JSON.stringify({ lulus: lulus, gagal: gagal }));\n')
        if h2 is None: g = g + ['S6 LAYAR JSC JATUH: ' + e2]
        else: l += h2['lulus']; g = g + h2['gagal']
    return l, g


# ---- S6 · layar (statis): kartu dipasang di uang.js, keadaan muat dari app.js, modulepreload ----
STATIS = [
    ('baru/js/layar/uang.js', 'uang.js memanggil pemeriksaan dengan keadaan muat perangkat', 'PST.pstPeriksa(kini(), muatData())'),
    ('baru/js/layar/uang.js', 'uang.js menggambar kartu di Tutup buku', 'data-k="tb-periksa"'),
    ('baru/js/layar/uang.js', 'tombol unduh hasil pemeriksaan (JSON)', 'data-aksi="pstUnduh"'),
    ('baru/js/layar/uang.js', 'unduh memakai berkas pemeriksaan', 'const B = PST.pstBerkas(H, kini()); const bytes = unduh(B.isi, B.nama);'),
    ('baru/js/layar/uang.js', 'kartu tidak menjatuhkan layar Tutup buku', "console.error('pemeriksaan sesudah tutup buku', e)"),
    ('baru/js/app.js', 'lokal() layar Uang membawa keadaan muat (koleksi siap / total / ditolak)', 'koleksiSiap: statusFb.koleksiSiap, koleksiTotal: statusFb.koleksiTotal, ditolak: statusFb.ditolak || []'),
    ('baru/index.html', 'modul pemeriksaan ada di modulepreload', '<link rel="modulepreload" href="js/layar/periksa-sesudah-logika.js">'),
]


def statis(ganti=None):
    out = []
    for berkas, nama, jangkar in STATIS:
        t = open(os.path.join(AKAR, berkas), encoding='utf-8').read()
        if ganti and ganti[0] == berkas: t = t.replace(ganti[1], ganti[2])
        if jangkar not in t: out.append('statis ' + berkas + ': ' + nama)
    return out


ASAP = r"""
// ==================== ASAP — CADANGAN TOKO LOKAL (tidak di-commit; dilewati di CI). Putusan per tanggal & aturan pajak = TIRUAN di memori, bukan data owner ====================
var salahA = []; var hasilA = {};
function muatCad() { KOLEKSI.forEach(function (k) { pasok(k.nama, []); setelTertunda(k.nama, []); }); Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
  while (arsipSimulasi().length) pulihkanArsip(arsipSimulasi()[0].tahun, []); __ls = {}; __dom['jualKarungBerat'] = { value: '50' };
  terapkanKeCache([{ koleksi: 'aturanToko', data: pjGabungRekap({ tarifPerMil: 5, batasBebas: 500000000, batasOmzet: 4800000000 }, { tanggal: '2026-10-06', jam: '10:00' }) }]); }
['2027-01-05T10:00:00+07:00', '2027-02-20T10:00:00+07:00'].forEach(function (x, i) {
  muatCad(); var w = jam('2027-01-05T10:00:00+07:00'); var R0 = ritualPenuh(w); if (R0.tolak) { salahA.push('ritual ditolak: ' + R0.tolak.slice(0, 300)); return; }
  if (i === 1) tulis(susunSelesai(2026, 'cadangan-sesudah-asap.json', jam('2027-01-05T12:00:00+07:00'), false, LA));
  jam(x); var t0 = new Date().getTime(); var H = pstPeriksa(new Date(__KINI), M_OK);
  if (!H) { salahA.push(x + ': kartu tidak tampil'); return; }
  hasilA[x.slice(0, 10)] = { fase: H.fase, n: H.n, sama: H.nSama, beda: H.nBeda, belum: H.nBelum, perKelompok: H.kelompok.map(function (g) { return g.baris.length; }),
    rak: baris(H, 'rakJual').ket, bukuMerek: baris(H, 'bukuMerek').ket.split(' · ')[0], kemasan: baris(H, 'bukuKemasan').ket, pembuka: baris(H, 'pembuka').a + ' dokumen', sumber: H.sumber.replace(/\(.*\)/, ''), ms: new Date().getTime() - t0 };
  if (!H.beres) salahA.push(x + ': ' + ringkasH(H).replace(/Rp[\d.]+/g, 'Rp…').slice(0, 900));
});
print(JSON.stringify({ salah: salahA, hasil: hasilA }));
"""


def asap(js, berkas):
    h, e = UP.jalan(UP.JAM + js + '\nvar KOTAK = ' + json.dumps(UP.KOTAK) + ';\nvar CAD = ' + open(berkas, encoding='utf-8').read() + ';\n' + UP.BERSAMA + TAMBAH + ASAP)
    if h is None: return None, ['ASAP JATUH: ' + e]
    return h['hasil'], h['salah']


RUSAK = [
    ('kartu memakai hasil periksa HIDUP saja (bkPeriksaDipakai dilewati) — titik kas yang maju membuat ✓ jadi ?', "const PU = bkPeriksaDipakai(tahun); const H = a.hariIni || null;", "const PU = periksaUlangBuku(tahun); const H = a.hariIni || null;"),
    ('baris "?" dianggap sama (lulus palsu)', "    return pstBaris({ id: b.id, judul, ket, status: 'belum', a: b.a, b: b.b, sebab });\n", "    return pstBaris({ id: b.id, judul, ket, status: 'sama', a: b.a, b: b.b, sebab });\n"),
    ('data belum dimuat tidak ditahan (tanpa penjaga muat)', "const m = M || {}; if (m.siap === false) return", "const m = M || {}; if (false) return"),
    ('koleksi ditolak server diabaikan', "if (tolak.length) return 'koleksi '", "if (false) return 'koleksi '"),
    ('kiriman tutup buku yang menunggu server diabaikan', "  if (tunggu) return 'catatan tutup buku", "  if (false) return 'catatan tutup buku"),
    ('berita acara selesai yang menunggu server tidak dilihat (kemajuanBuku saja)', " || dokTertunda('tutupBukuAcara', String(T.acara.id || T.tahun));", ";"),
    ('modal: saldo pembuka dibandingkan dengan dirinya sendiri', "const sama = !hilang && Math.abs(sesudah - beku.n) < 0.5;", "const sama = !hilang;"),
    ('saldo pembuka tidak dijumlah lagi dari dokumennya (piutang pembuka diubah lolos)', "    if (x === undefined || x === null || Math.abs(Number(b.n) - Number(x)) >= 0.5) bedaJ.push(", "    if (false) bedaJ.push("),
    ('saldo pembuka tersembunyi dihitung ada', "else if (!pembukaBerlaku(x)) sembunyi += 1; else ada += 1; });", "else ada += 1; });"),
    ('pembanding per buku dari dokumen pembuka sekarang, bukan ringkasan beku di berita acara (merek yang dihapus lolos)', "  if (R) return { dari: 'ringkasan saldo pembuka di berita acara'", "  if (false) return { dari: 'ringkasan saldo pembuka di berita acara'"),
    ('buku dibaca dari cache hidup, bukan saat tahun baru dibuka (penjualan Januari = beda palsu)', "  return denganCacheSaring(nama, (d) => !!(d && d.tutupBuku && Number(d.tahunDari) === t), fn);", "  return fn();"),
    ('rak Jual: tanda buku 25 kg tidak dibaca lagi', "    if (r.indukUkuran) { nTanda += 1; const u = C.uk[m]; if (!u || u.induk !== String(r.indukUkuran) || (b && u.berat !== b)) salah.push(", "    if (r.indukUkuran) { nTanda += 1; const u = C.uk[m]; if (false) salah.push("),
    ('rak Jual: chip yang hilang tidak disebut', "    if (!ch) salah.push(nama + ' ' + b + ' kg (buku ' + m + '): tidak tampil di rak Jual');", "    if (!ch) nTanpaHarga += 0;"),
    ('stok minus saldo pembuka tidak dihitung', "    const minus = minusBuku(tglBuka).daftar.filter((x) => PST_JENIS_STOK[x.jenis]);", "    const minus = [];"),
    ('minus hari ini dijadikan beda (bukan yang diperiksa)', "status: V.minus.length ? 'beda' : 'sama', satuan: 'teks', a: V.minus.length", "status: V.minus.length || minusKini.length ? 'beda' : 'sama', satuan: 'teks', a: V.minus.length"),
    ('potret: bulan yang hilang tidak dihitung', "const kosongB = kunciBulan.filter((k) => !bulan[k] ||", "const kosongB = [].filter((k) => !bulan[k] ||"),
    ('pajak: omzet dibandingkan dengan dirinya sendiri', "status: Math.abs(Math.round(TJ.totalSistem) - ptOmzet) < 0.5 ? 'sama' : 'beda', a: ptOmzet", "status: 'sama', a: ptOmzet"),
    ('setoran: yang hilang lolos', "if (!(x.jumlahSetor - baru - 0.5 <= ps && ps <= x.jumlahSetor + 0.5)) bedaS.push(", "if (!(x.jumlahSetor - baru - 0.5 <= ps)) bedaS.push("),
    ('setoran sesudah tutup buku dianggap beda', "const baru = x.setor.filter((s) => sejak && String(s.dicatatPada || '') >= sejak)", "const baru = x.setor.filter((s) => false)"),
    ('kelompok 6 dihitung dua kali (utang & piutang juga di kelompok 1)', "const lain = PB.baris.filter((x) => PST_UTANG.indexOf(x.id) < 0);", "const lain = PB.baris.slice();"),
    ('kartu tampil sebelum arsip habis', "if (a.status === 'terkunci') return bkArsipHabis(tahun) || !arsipBuku(tahun).n ?", "if (a.status === 'terkunci') return true ?"),
    ('kartu tampil selamanya sesudah selesai', "return iso <= pstAkhirFeb(tahun + 1) || (s30 && iso <= s30) ?", "return true ?"),
    ('tahun kartu dari era (saldo pembuka yang terlihat), bukan berita acara — penanda hilang = kartu lenyap diam-diam', "const a = ambilTutupBukuAcara().filter((x) => x && isFinite(Number(x.tahun)) && (x.status === 'terkunci' || x.status === 'selesai'))", "const a = ambilTutupBukuAcara().filter((x) => x && Number(x.tahun) === eraBuku() && (x.status === 'terkunci' || x.status === 'selesai'))"),
    ('ringkasan "beres" walau ada yang belum bisa diperiksa', "const beres = !nBeda && !nBelum && n > 0;", "const beres = !nBeda && n > 0;"),
]
RUSAK_LAIN = [
    ('ritual tidak menyimpan ringkasan saldo pembuka di berita acara', 'baru/js/layar/tutup-buku-logika.js', "  acara.pembukaRingkas = ringkasPembuka(P.dokumen);\n", ""),
    ('hasil yang dibekukan tidak bertanda (kartu tidak tahu sumbernya)', 'baru/js/layar/tutup-buku-logika.js', "{ beku: { tanggal: String(P.tanggal || ''), pada: String(P.pada || '') } }", "{}"),
    ('cache sementara tidak dikembalikan sesudah diperiksa (layar lain membaca saldo pembuka saja)', 'baru/js/data/toko.js', "  try { return fn(); } finally { Object.keys(simpan).forEach((c) => { _cache[c] = simpan[c]; }); _versiCache += 1; }\n}\n\n// ---- keranjang aktif", "  return fn();\n}\n\n// ---- keranjang aktif"),
]


def bundelan():
    return uji_kunci_periode.satu_lingkup(bundel_baru.bundel(MODUL))


if __name__ == '__main__':
    js = bundelan()
    if '--kontrol' in sys.argv:
        kode = 0; logika = open(os.path.join(AKAR, LOGIKA), encoding='utf-8').read()
        for nama, a, b in RUSAK:
            if logika.count(a) != 1 or js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_LAIN:
            sumber = open(os.path.join(AKAR, berkas), encoding='utf-8').read()
            if sumber.count(a) != 1 or js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for berkas, nama, jangkar in STATIS:
            g = statis((berkas, jangkar, jangkar[:len(jangkar) // 2] + '§' + jangkar[len(jangkar) // 2 + 1:]))
            print(('BERBUNYI ' if g else 'DIAM!!   ') + 'statis dicabut: ' + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js, True, bundelan_layar())
    print('PEMERIKSAAN SESUDAH TUTUP BUKU (kotak pasir + layar Uang jsc): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    berkas = next((x.split('=', 1)[1] for x in sys.argv if x.startswith('--cadangan=')), '') or os.environ.get('PERIKSA_ASAP', '')
    if berkas:
        if not os.path.exists(berkas): print('ASAP: berkas cadangan tidak ada (' + berkas + ')'); sys.exit(2)
        h, s = asap(js, berkas)
        print('ASAP CADANGAN LOKAL (%s): %s' % (os.path.basename(berkas), json.dumps(h, ensure_ascii=False)))
        for x in s: print('   ✗ ' + x)
        if s: sys.exit(2)
    sys.exit(0 if not g else 2)
