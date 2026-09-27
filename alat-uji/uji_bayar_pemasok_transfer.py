#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_bayar_pemasok_transfer.py — putaran 29 Bagian 4 (owner 27 Sep 2026): BAYAR BON PEMASOK TUNAI (laci/brankas) atau TRANSFER (rekening + biaya admin).
  · Cara bayar dibaca dari `dari` (rekening = transfer) — tanpa kolom baru di utangPemasokMutasi.
  · Transfer mengurangi kantong REKENING (saldo per tempat), biaya admin = pengeluaranHarian {kategori toko, untuk toko, dari rekening, dariBayarBon} dalam SATU kiriman,
    bertanggal sama; utang pemasok turun sebesar NOMINAL BAYAR, bukan bayar + admin; laba turun sebesar admin saja; Σ kantong = kasPada tetap.
  · Kantong yang dipilih dijaga isinya (dulu hanya total kas; dulu dokumen admin tanpa `dari` → dipotong dari laci). Rekening yang belum pernah diisi (titik kas 0)
    DISEBUT dan ditawari "catat isi rekening" (K4: pengaturan/titikKas baru bertanggal kemarin; gerakan hari ini tetap terhitung; laci/brankas/amplop tidak bergeser).
  · Riwayat/buku bon menyebut tunai/transfer & adminnya; urung ≤ 90 dtk mencabut keduanya.
KOTAK PASIR (ANGKA CONTOH, nama rekaan), jam dikunci 19 Sep 2026 10:00 WIB. Cadangan toko di _privat/ (asap): tiap bon terbuka dicoba transfer dengan saldo per tempat;
rekening 0 di titik kas → ditolak dengan tawaran catat isi rekening; catat isi rekening tidak menggeser laci/brankas/amplop.

    python3 alat-uji/uji_bayar_pemasok_transfer.py            → N lulus · 0 gagal
    python3 alat-uji/uji_bayar_pemasok_transfer.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru  # noqa: E402
import uji_wadah_bernama  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_uang_baru.MODUL
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(id, tgl, jam, cara, merk, kg, harga, hpp, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': jam, 'caraBayar': cara, 'jenis': 'karung', 'merkSumber': merk, 'totalKg': kg, 'beratKarungAcuan': 50, 'jumlahKarung': kg / 50, 'hargaTotal': harga, 'hppTotalSaatJual': hpp, 'trxId': 't' + str(id)}
    d.update(k); return d


# ---- ANGKA CONTOH. Bon PEMASOK CONTOH 20 Agu 13.000.000 (utang). Titik kas 15 Sep: laci 2 jt · brankas 10 jt · rekening 5 jt · amplop 0.
#      QRIS 17 Sep 700.000 & 19 Sep 600.000 → rekening 6.300.000 sekarang (18 Sep: 5.700.000). Tunai 16 Sep 500.000 → laci 2.500.000.
KOTAK = {
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-08-20', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'utang', 'biayaBongkar': 0,
                  'merkList': [{'id': 'b10', 'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 20, 'totalKg': 1000, 'hargaPerKg': 13000, 'subtotalHarga': 13000000}]}],
  'penjualan': [jual('j1', '2026-09-16', '09:00', 'Tunai', 'Angsa', 35.7, 500000, 464100), jual('j2', '2026-09-17', '10:00', 'QRIS', 'Angsa', 50, 700000, 650000), jual('j3', '2026-09-19', '09:12', 'QRIS', 'Angsa', 40, 600000, 560000)],
  'utangPemasokMutasi': [], 'pengeluaranHarian': [], 'kasbonMutasi': [], 'biayaBulanan': [], 'absenKaryawan': [], 'slipUpah': [], 'modalOwner': [], 'utangOwnerMutasi': [], 'amplopLaba': [], 'pindahUang': [], 'tutupHari': [], 'setoranKas': [], 'piutangMutasi': [], 'penyesuaianStok': [], 'pemasokCatatan': [],
  'aturanToko': [{'id': 'bonPemasok', 'dekatHari': 7, 'admin': [{'nama': 'BI-FAST', 'n': 2500}, {'nama': 'Transfer antarbank', 'n': 6500}]}], 'pengaturan': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var TITIK = { tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 5000000, amplop: 0 };
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(TITIK));
var KINI = new Date(Date.now()); var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 9000; return function () { n += 1; return n; }; })() };
var tulis = function (r) { if (r.tolak) throw new Error('DITOLAK: ' + r.tolak); if (r.hapus) terapkanKeCache(r.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (r.dokumen) terapkanKeCache(r.dokumen); return r; };
var identitas = function (nama) { var S = saldoKantong(); ok('IDENTITAS kantong ' + nama + ': Σ empat tempat = kasPada()', S.ada && S.cocok, J(S)); return S; };
var bon = function () { return susunBon(KINI).bon[0]; }; var utang = function () { return susunBon(KINI).total; };
var LM = function () { return hitungLabaBersihRentang('2026-09-01', '2026-09-30'); };
var S0 = identitas('awal'); var L0 = LM(); var U0 = utang();
ok('awal: rekening 6.300.000 (titik 5 jt + QRIS 700.000 + 600.000), laci 2.500.000; utang 13.000.000', S0.rekening === 6300000 && S0.laci === 2500000 && U0 === 13000000, J([S0, U0]));

// ---- cara bayar dari `dari`; tanpa saldo per tempat (S) = perilaku lama
ok('caraDari: rekening = transfer, laci/brankas = tunai, kosong = belum dipilih; CARA_BAYAR_BON dua pilihan', caraDari('rekening') === 'transfer' && caraDari('laci') === 'tunai' && caraDari('brankas') === 'tunai' && caraDari('') === '' && CARA_BAYAR_BON.length === 2);
var H0 = hitungBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '3.000.000', dari: 'rekening', adminI: 0 }, KINI);
ok('tanpa S: kantong null, yang dijaga total kas (seperti dulu); cara transfer; label menyebut TRANSFER', H0.kantong === null && !H0.tolak && H0.cara === 'transfer' && /TRANSFER$/.test(H0.label) && !H0.rekeningKosong, J(H0.label));
ok('tanpa dari → ditolak dengan kalimat tunai/transfer', /tunai \(laci\/brankas\) atau transfer \(rekening\)/.test(hitungBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '1000' }, KINI).tolak));

// ---- TRANSFER dengan saldo per tempat
var S = saldoKantong(); var H = hitungBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '3.000.000', dari: 'rekening', adminI: 0 }, KINI, S);
ok('transfer 3.000.000 + BI-FAST 2.500: kantong rekening 6.300.000 dijaga; arti: rekening berkurang 3.002.500 lewat transfer, utang turun 3.000.000 (BUKAN 3.002.500), laba turun cuma admin', !H.tolak && H.kantong === 6300000 && H.admin === 2500 && /Rekening berkurang Rp3\.002\.500 lewat transfer/.test(H.arti.b) && /utang ke PEMASOK CONTOH berkurang Rp3\.000\.000 \(bukan Rp3\.002\.500\)/.test(H.arti.c) && /laba TIDAK berubah/.test(H.arti.c), J(H.arti));
var R = tulis(susunBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '3.000.000', dari: 'rekening', adminI: 0, catatan: 'lewat m-banking' }, W, S));
var dBayar = R.dokumen[0].data, dAdmin = R.dokumen[1].data;
ok('dokumen: utangPemasokMutasi {tipe bayar, nominal 3.000.000, dari rekening, biayaAdmin 2.500, adminNama BI-FAST, bonId, bonTanggal} + pengeluaranHarian {kategori toko, untuk toko, DARI REKENING, nominal 2.500, dariBayarBon = id bayar, tanggal sama} — satu kiriman, saling merujuk', R.dokumen.length === 2 && dBayar.tipe === 'bayar' && dBayar.nominal === 3000000 && dBayar.dari === 'rekening' && dBayar.biayaAdmin === 2500 && dBayar.adminNama === 'BI-FAST' && dBayar.bonId === bon().id && dBayar.bonTanggal === '2026-08-20' && dAdmin.kategori === 'toko' && dAdmin.untuk === 'toko' && dAdmin.dari === 'rekening' && dAdmin.nominal === 2500 && dAdmin.dariBayarBon === dBayar.id && dAdmin.tanggal === dBayar.tanggal && /Biaya admin BI-FAST — bayar bon PEMASOK CONTOH 20 Agu 2026/.test(dAdmin.keterangan), J(R.dokumen));
var S1 = identitas('sesudah transfer');
ok('REKENING benar-benar turun 3.002.500 → 3.297.500; laci tetap 2.500.000; kas total turun 3.002.500; utang turun 3.000.000 → 10.000.000; laba Sep turun 2.500 saja', S1.rekening === 3297500 && S1.laci === 2500000 && S1.mesin === S0.mesin - 3002500 && utang() === 10000000 && LM().labaBersih === L0.labaBersih - 2500, J([S1.rekening, S1.laci, utang(), LM().labaBersih, L0.labaBersih]));
ok('kabar menyebut transfer & utang turun sebesar bayar; urung ditawarkan 90 dtk', /transfer, Rekening berkurang Rp3\.002\.500 \(admin Rp2\.500 jadi biaya toko, utang turun Rp3\.000\.000\)/.test(R.patch.kabar) && R.patch.urung.id === dBayar.id, R.patch.kabar);
var BB = bukuBon('PEMASOK CONTOH');
ok('buku bon menyebut cara bayarnya: "Bayar bon 20 Agu 2026 · transfer", dari Rekening · admin Rp2.500 BI-FAST (biaya toko, bukan utang) · catatan; saldo berjalan 10.000.000', BB.baris.some(function (b) { return b.teks === 'Bayar bon 20 Agu 2026 · transfer' && b.cara === 'transfer' && /dari Rekening · admin Rp2\.500 BI-FAST \(biaya toko, bukan utang\) · lewat m-banking/.test(b.ket); }) && BB.saldo === 10000000, J(BB.baris));
// rekening tidak cukup → ditolak menyebut isinya
S = saldoKantong(); H = hitungBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '3.296.000', dari: 'rekening', adminI: 0 }, KINI, S);
ok('transfer 3.296.000 + 2.500 > rekening 3.297.500 → DITOLAK menyebut isi rekening & admin (bukan dijepit, bukan total kas)', /Rekening cuma Rp3\.297\.500 — tidak cukup untuk Rp3\.298\.500 \(termasuk biaya admin Rp2\.500\)/.test(H.tolak), H.tolak);
ok('tunai dari laci 2.600.000 > laci 2.500.000 → ditolak menyebut laci; dari brankas boleh', /Laci cuma Rp2\.500\.000/.test(hitungBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '2.600.000', dari: 'laci' }, KINI, S).tolak) && !hitungBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '2.600.000', dari: 'brankas' }, KINI, S).tolak);
// urung transfer: keduanya dicabut, rekening pulih
tulis(susunUrungBayar(dBayar.id)); var S2 = identitas('sesudah urung');
ok('urung: pembayaran & biaya adminnya dicabut; rekening kembali 6.300.000; utang 13.000.000; laba pulih', S2.rekening === 6300000 && utang() === 13000000 && LM().labaBersih === L0.labaBersih && !ambilPengeluaranHarian().some(function (h) { return h.dariBayarBon === dBayar.id; }));
// ---- TUNAI dari brankas
S = saldoKantong(); var RT = tulis(susunBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '2.000.000', dari: 'brankas', adminI: 0 }, W, S));
var S3 = identitas('sesudah tunai brankas');
ok('tunai dari brankas 2.000.000: satu dokumen (tanpa admin walau adminI terisi — admin hanya untuk rekening), cara tunai, brankas 10 jt → 8 jt, rekening tetap, utang 11.000.000, laba tetap; label "· TUNAI"', RT.dokumen.length === 1 && RT.dokumen[0].data.dari === 'brankas' && RT.dokumen[0].data.biayaAdmin === undefined && S3.brankas === 8000000 && S3.rekening === 6300000 && utang() === 11000000 && LM().labaBersih === L0.labaBersih && /tunai, Brankas berkurang Rp2\.000\.000/.test(RT.patch.kabar) && /TUNAI$/.test(hitungBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '1000', dari: 'brankas' }, KINI, S).label), J([RT.dokumen, RT.patch.kabar]));
ok('buku bon: baris tunai "· tunai", dari Brankas, tanpa admin', bukuBon('PEMASOK CONTOH').baris.some(function (b) { return b.teks === 'Bayar bon 20 Agu 2026 · tunai' && b.cara === 'tunai' && b.ket === 'dari Brankas'; }));
var UPM = ambilUtangPemasokMutasi().slice(); pasok('utangPemasokMutasi', UPM.concat([{ id: 'lama1', tipe: 'bayar', pemasok: 'PEMASOK CONTOH', nominal: 1000, tanggal: '2026-09-01', jam: '09:00', bonId: bon().id, bonTanggal: '2026-08-20' }]));
ok('pembayaran sistem lama tanpa `dari`: buku menyebut "kantong tidak dicatat (sistem lama)", cara kosong', bukuBon('PEMASOK CONTOH').baris.some(function (b) { return b.id === 'lama1' && b.cara === '' && /kantong tidak dicatat \(sistem lama\)/.test(b.ket) && b.teks === 'Bayar bon 20 Agu 2026'; }));
pasok('utangPemasokMutasi', UPM);

// ---- REKENING BELUM PERNAH DIISI (titik kas rekening 0) → disebut & ditawari catat isi rekening
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(Object.assign({}, TITIK, { rekening: 0 })));
S = saldoKantong(); H = hitungBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '2.000.000', dari: 'rekening', adminI: -1 }, KINI, S);
ok('titik rekening 0 tapi QRIS masuk 1.300.000: rekening cuma 1.300.000 → transfer 2 jt ditolak; rekeningKosong TRUE (titik belum pernah diisi — hitungan cuma dari QRIS), teksnya menyebut 1.300.000 cuma dari gerakan rekening', /Rekening cuma Rp1\.300\.000/.test(H.tolak) && H.rekeningKosong && /hitungan Rp1\.300\.000 cuma dari gerakan rekening sejak titik kas 15 Sep 2026/.test(H.rekeningTeks), J([H.tolak, H.rekeningTeks]));
pasok('penjualan', KOTAK.penjualan.filter(function (p) { return p.caraBayar !== 'QRIS'; }));
S = saldoKantong(); H = hitungBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '2.000.000', dari: 'rekening', adminI: -1 }, KINI, S);
ok('titik rekening 0 & tanpa gerakan rekening: rekeningKosong TRUE, tolak menyebut "catat isi rekening dulu di Uang › Pindah uang", rekeningTeks menyebut hitungan Rp0', H.rekeningKosong && /Rekening cuma Rp0/.test(H.tolak) && /catat isi rekening dulu di Uang › Pindah uang/.test(H.tolak) && /hitungan Rp0 cuma dari gerakan rekening sejak titik kas 15 Sep 2026/.test(H.rekeningTeks), J([H.tolak, H.rekeningTeks]));
pasok('penjualan', KOTAK.penjualan);
// ---- CATAT ISI REKENING (K4): titik kas baru bertanggal KEMARIN, gerakan hari ini tetap terhitung, laci/brankas/amplop tidak bergeser
S = saldoKantong(); var HR = hitungTitikRekening('4.000.000', W);
ok('hitung: rekening menurut m-banking 4.000.000 (aplikasi 1.300.000 → naik 2.700.000); titik baru tanggal 18 Sep: laci 2.500.000, brankas 10.000.000 (bayar tunai brankas HARI INI tetap dihitung sesudah titik), amplop 0 = hasil hitung sampai kemarin; rekening 4.000.000 − QRIS hari ini 600.000 = 3.400.000; belumPernah true', !HR.tolak && HR.n === 4000000 && HR.selisih === 2700000 && HR.titik.tanggal === '2026-09-18' && HR.titik.laci === 2500000 && HR.titik.brankas === 10000000 && HR.titik.amplop === 0 && HR.titik.rekening === 3400000 && HR.belumPernah && /naik Rp2\.700\.000 dari hitungan Rp1\.300\.000/.test(HR.arti), J(HR));
ok('ketik kosong / minus ditolak; tanpa titik kas ditolak menyebut Tutup hari', /Ketik isi rekening/.test(hitungTitikRekening('', W).tolak) && /Ketik isi rekening/.test(hitungTitikRekening('-5', W).tolak) && (function () { localStorage.removeItem('miqbal_titik_kas_v1'); var t = hitungTitikRekening('1', W).tolak; localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(Object.assign({}, TITIK, { rekening: 0 }))); return /Titik kas belum disetel/.test(t); })());
var RR = tulis(susunTitikRekening('4.000.000', W)); pasok('pengaturan', [RR.dokumen[0].data]);
var S4 = identitas('sesudah catat isi rekening');
ok('dokumen = pengaturan/titikKas (jenis yang sudah ada) tanggal 18 Sep; sesudahnya rekening 4.000.000, laci 2.500.000, brankas 8.000.000 tidak bergeser; kas total naik 2.700.000; patch mengosongkan lembar', RR.dokumen[0].koleksi === 'pengaturan' && RR.dokumen[0].data.id === 'titikKas' && RR.titik.tanggal === '2026-09-18' && S4.rekening === 4000000 && S4.laci === 2500000 && S4.brankas === 8000000 && S4.mesin === S.mesin + 2700000 && RR.patch.rekIsi === null && /Isi rekening dicatat Rp4\.000\.000/.test(RR.patch.kabar), J([S4, RR.patch.kabar]));
S = saldoKantong(); var R2 = tulis(susunBayar({ pemasok: 'PEMASOK CONTOH', bonId: bon().id, ketik: '3.000.000', dari: 'rekening', adminI: 1 }, W, S));
ok('sesudah dicatat, transfer 3.000.000 + antarbank 6.500 lolos: rekening 993.500; utang 8.000.000; admin doc dari rekening', !R2.tolak && saldoKantong().rekening === 993500 && utang() === 8000000 && R2.dokumen[1].data.dari === 'rekening' && R2.dokumen[1].data.nominal === 6500, J([saldoKantong().rekening, utang()]));
identitas('sesudah transfer kedua');
// titik sudah bertanggal HARI INI (sesudah Tutup hari) → titik hari ini ditulis ulang dengan rekening yang diketik
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-09-19', laci: 100000, brankas: 200000, rekening: 300000, amplop: 0, diubahPada: '2026-09-19T14:00:00.000Z' }]);
HR = hitungTitikRekening('450.000', W);
ok('titik bertanggal hari ini: titik hari ini ditulis ulang, rekening = 450.000, laci 100.000 & brankas 200.000 tetap, belumPernah false', HR.titik.tanggal === '2026-09-19' && HR.titik.rekening === 450000 && HR.titik.laci === 100000 && HR.titik.brankas === 200000 && !HR.belumPernah && HR.selisih === 150000, J(HR));
pasok('pengaturan', []);

// ==================== ASAP: cadangan toko ====================
var asap = null;
if (CADANGAN) {
  Object.keys(CADANGAN).forEach(function (n) { if (Array.isArray(CADANGAN[n])) pasok(n, CADANGAN[n]); }); localStorage.removeItem('miqbal_titik_kas_v1');
  var kini2 = new Date(Date.now()); var W2 = { tanggal: hariIniIso(kini2), jam: '20:00', kini: kini2.toISOString(), idUnik: function () { return 'x' + Math.random(); } }; var Sc = saldoKantong(); var B = susunBon(kini2); var salah = [];
  var coba = B.bon.map(function (b) { var Hc = hitungBayar({ pemasok: b.pemasok, bonId: b.id, ketik: String(Math.min(1000, b.sisa)), dari: 'rekening', adminI: 0 }, kini2, Sc); return { bon: b.tanggal, tolak: Hc.tolak, rekeningKosong: Hc.rekeningKosong }; });
  coba.forEach(function (c) { if (Sc.ada && Sc.rekening < 1000 + 2500 && !/Rekening cuma/.test(c.tolak)) salah.push('transfer ' + c.bon + ' tidak dijaga'); });
  var HRc = Sc.ada ? hitungTitikRekening(String(Math.round(Sc.rekening) + 1000000), W2) : null;
  if (HRc && !HRc.tolak) { var kemarin = HRc.titik.tanggal; var Sk = kemarin >= Sc.titik.tanggal && kemarin < W2.tanggal ? saldoKantong(kemarin) : Sc; if (Math.abs(HRc.titik.laci - Sk.laci) >= 1 || Math.abs(HRc.titik.brankas - Sk.brankas) >= 1 || Math.abs(HRc.titik.amplop - Sk.amplop) >= 1) salah.push('catat isi rekening menggeser laci/brankas/amplop'); if (HRc.selisih !== 1000000) salah.push('selisih rekening bukan 1.000.000'); }
  var caraLama = ambilUtangPemasokMutasi().filter(function (m) { return m.tipe === 'bayar'; }).map(function (m) { return caraDari(m.dari); });
  asap = { salah: salah, titik: Sc.ada ? Sc.teksTitik + ' · rekening ' + Math.round(Sc.rekening) : 'tidak ada titik kas', bonTerbuka: B.bon.length, transferDitolak: coba.filter(function (c) { return /Rekening cuma/.test(c.tolak); }).length, rekeningKosong: coba.filter(function (c) { return c.rekeningKosong; }).length, catatIsiRekening: HRc ? (HRc.tolak || 'titik ' + HRc.titik.tanggal) : '-', pembayaranLama: { n: caraLama.length, tanpaKantong: caraLama.filter(function (c) { return !c; }).length, transfer: caraLama.filter(function (c) { return c === 'transfer'; }).length } };
  ok('ASAP: transfer dijaga isi rekening pada cadangan; catat isi rekening tidak menggeser laci/brankas/amplop', !salah.length, J(asap));
}
print(J({ lulus: lulus, gagal: gagal, asap: asap }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def utama(js, pakai_cadangan):
    cad = 'null'; p = uji_wadah_bernama.cadangan_toko() if pakai_cadangan else None
    if p: cad = uji_wadah_bernama.cad_js(p)[0]
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CADANGAN = ' + cad + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    return h['lulus'], h['gagal'], h.get('asap')


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            'biaya admin tanpa kantong (dipotong dari laci di saldo per tempat)': js.replace("nominal: H.admin, dari: H.D.dari, dariBayarBon: id }", "nominal: H.admin, dariBayarBon: id }"),
            'utang pemasok turun sebesar bayar + admin': js.replace("tipe: 'bayar', pemasok: H.bon.pemasok, nominal: H.n, catatan, bonId: H.bon.id,", "tipe: 'bayar', pemasok: H.bon.pemasok, nominal: H.n + H.admin, catatan, bonId: H.bon.id,"),
            'kantong yang dipilih tidak dijaga (hanya total kas)': js.replace("else if (kantong !== null && n + admin > kantong + 0.5) tolak =", "else if (false) tolak ="),
            'rekening kosong tidak disebut': js.replace("const rekeningKosong = !!(S && S.ada && !(Number(S.titik.rekening) > 0));", "const rekeningKosong = false;"),
            'cara bayar salah baca (rekening = tunai)': js.replace("const caraDari = (dari) => (dari === 'rekening' ? 'transfer' : dari ? 'tunai' : '');", "const caraDari = (dari) => (dari ? 'tunai' : '');"),
            'biaya admin bukan tujuan toko': js.replace("data: { id: w.idUnik(), kategori: 'toko', untuk: 'toko', tanggal: w.tanggal, jam: w.jam, keterangan: 'Biaya admin ' + H.biaya.nama + ' — bayar bon '", "data: { id: w.idUnik(), kategori: 'toko', tanggal: w.tanggal, jam: w.jam, keterangan: 'Biaya admin ' + H.biaya.nama + ' — bayar bon '"),
            'biaya admin dicatat juga untuk bayar tunai': js.replace("if (H.admin > 0) dokumen.push({ koleksi: 'pengeluaranHarian', data: { id: w.idUnik(), kategori: 'toko', untuk: 'toko', tanggal: w.tanggal, jam: w.jam, keterangan: 'Biaya admin ' + H.biaya.nama", "if (true) dokumen.push({ koleksi: 'pengeluaranHarian', data: { id: w.idUnik(), kategori: 'toko', untuk: 'toko', tanggal: w.tanggal, jam: w.jam, keterangan: 'Biaya admin ' + (H.biaya || {}).nama"),
            'urung bayar meninggalkan biaya adminnya': js.replace("ambilPengeluaranHarian().forEach((h) => { if (String(h.dariBayarBon || '') === String(id)) hapus.push({ koleksi: 'pengeluaranHarian', id: h.id }); });", ""),
            'titik rekening ditulis bertanggal hari ini (gerakan hari ini hilang)': js.replace("if (kemarin >= T.tanggal) { dasar = saldoKantong(kemarin); tanggal = kemarin; rekening = n - (S.rekening - dasar.rekening); }", "if (kemarin >= T.tanggal) { dasar = S; tanggal = w.tanggal; rekening = n; }"),
            'catat isi rekening menggeser laci': js.replace("laci: Math.round(dasar.laci), brankas: Math.round(dasar.brankas), rekening: Math.round(rekening),", "laci: Math.round(dasar.laci) + 1000, brankas: Math.round(dasar.brankas), rekening: Math.round(rekening),"),
            'catat isi rekening tanpa titik kas diterima': js.replace("if (!S.ada) return { n, tolak: 'Titik kas belum disetel — Tutup hari dulu malam ini, sesudahnya isi rekening bisa dicatat', S, belumPernah: true };", "if (!S.ada) return { n, tolak: '', S, titik: { id: 'titikKas', tanggal: w.tanggal, laci: 0, brankas: 0, rekening: n, amplop: 0 }, selisih: 0, belumPernah: true, arti: '' };"),
            'buku bon tidak menyebut cara bayar': js.replace("+ (m.dari === 'rekening' ? ' · transfer' : m.dari ? ' · tunai' : ''), cara: caraDari(m.dari),", ", cara: '',"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g, _ = utama(isi, False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    print('BAYAR BON TUNAI / TRANSFER (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    p = uji_wadah_bernama.cadangan_toko()
    if p and asap: print('ASAP DATA TOKO (%s): %s' % (os.path.basename(p), json.dumps(asap, ensure_ascii=False)[:1200]))
    sys.exit(0 if not g else 2)
