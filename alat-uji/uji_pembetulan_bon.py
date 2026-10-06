#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_pembetulan_bon.py — owner 7 Okt 2026: PEMBETULAN BON PEMASOK di Harga & Pemasok › Bon pemasok (dulu salah tunjuk cuma bisa diurungkan 90 detik).
  · PINDAH pembayaran ke bon lain pemasok yang sama: dokumen yang SAMA ditulis ulang (bonId & bonTanggal baru) + `riwayat` (nilai lama → baru, alasan) +
    `alasanKoreksi`; alasan wajib; bon yang datang SESUDAH pembayaran ditolak; utang total, kas, laba TIDAK berubah, yang bergeser bon mana yang lunas
    (mesin beku; kelebihan mengalir ke bon tertua dan disebut).
  · KELEBIHAN saat pindah (pembayaran > sisa bon tujuan) disebut: berapa, kenapa, dan bon mana yang menerimanya — juga bila itu bon ASAL (sanggahan E2).
  · JUMLAH pembayaran: utang & kas bergeser sebesar selisihnya, laba tetap; jejak di riwayat. PENJAGA BESARAN (sanggahan E2): ≥ 2× / ≤ ½, kenaikan melebihi
    sisa bon yang ditunjuk, uang toko jadi minus, atau hari tunai yang sudah ditutup → ketukan kedua, kalimatnya menyebut angka lama → baru.
  · Tanggal bon lama = pemilih tanggal (type="date"; papan angka iPhone tidak punya '-').
  · NOMOR bon pemasok: kolom noBon di kedatangan (tanpa alasanKoreksi — bukan koreksi barang) / bon lama; ganti nomor wajib alasan; nomor kembar ditolak;
    Koreksi kedatangan membawanya; tampil di tusukan & Buku bon.
  · Bon LAMA: tanggal & nilai dibetulkan berjejak.
  · Bulan TERKUNCI (kunci periode) DITOLAK dengan kalimatnya.
KOTAK PASIR (ANGKA CONTOH, "PEMASOK CONTOH"), jam dikunci 19 Sep 2026 10:00 WIB. Cadangan toko di _privat/ (asap, dilewati bila tidak ada): tiap pemasok —
Σ sisa semua bon = mesin; tiap pembayaran bertunjuk dicoba dipindah ke bon tertua yang sudah ada saat itu → utang total, kas, laba tetap.

    python3 alat-uji/uji_pembetulan_bon.py            → N lulus · 0 gagal
    python3 alat-uji/uji_pembetulan_bon.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru  # noqa: E402
import uji_wadah_bernama  # noqa: E402
MODUL = uji_uang_baru.MODUL
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def brs(i, merk, karung, harga):
    return {'id': str(i), 'merk': merk, 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': karung, 'totalKg': karung * 50, 'hargaPerKg': harga, 'subtotalHarga': karung * 50 * harga}


P = 'PEMASOK CONTOH'
# ANGKA CONTOH. Bon lama 1 Agu 5.000.000; kedatangan bon 10 Agu 10.000.000 · 20 Agu 11.000.000 · 1 Sep 12.000.000; satu kedatangan tunai (bukan bon).
# Bayar: 25 Agu 5.000.000 → bon lama; 5 Sep 10.000.000 → 10 Agu; 12 Sep 12.000.000 → 1 Sep (SALAH TUNJUK — mestinya bon 20 Agu: kasus pembetulan).
KOTAK = {
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-08-10', 'jam': '08:00', 'pemasok': P, 'caraBayar': 'utang', 'biayaBongkar': 0, 'merkList': [brs(1, 'Angsa', 20, 10000)]},
                 {'id': 'b2', 'tanggal': '2026-08-20', 'jam': '08:00', 'pemasok': P, 'caraBayar': 'utang', 'biayaBongkar': 0, 'merkList': [brs(1, 'Angsa', 22, 10000)]},
                 {'id': 'b3', 'tanggal': '2026-09-01', 'jam': '08:00', 'pemasok': P, 'caraBayar': 'utang', 'biayaBongkar': 0, 'merkList': [brs(1, 'Angsa', 24, 10000)]},
                 {'id': 'b4', 'tanggal': '2026-09-02', 'jam': '08:00', 'pemasok': P, 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [brs(1, 'Angsa', 2, 10000)]}],
  'utangPemasokMutasi': [{'id': 'sa1', 'tanggal': '2026-08-25', 'jam': '09:00', 'tipe': 'saldoAwal', 'pemasok': P, 'nominal': 5000000, 'bonTanggal': '2026-08-01', 'catatan': 'bon lama contoh'},
                         {'id': 'p1', 'tanggal': '2026-08-25', 'jam': '09:05', 'tipe': 'bayar', 'pemasok': P, 'nominal': 5000000, 'bonId': 'sa1', 'bonTanggal': '2026-08-01', 'catatan': '', 'dari': 'laci'},
                         {'id': 'p2', 'tanggal': '2026-09-05', 'jam': '09:00', 'tipe': 'bayar', 'pemasok': P, 'nominal': 10000000, 'bonId': 'b1', 'bonTanggal': '2026-08-10', 'catatan': '', 'dari': 'brankas'},
                         {'id': 'p3', 'tanggal': '2026-09-12', 'jam': '09:00', 'tipe': 'bayar', 'pemasok': P, 'nominal': 12000000, 'bonId': 'b3', 'bonTanggal': '2026-09-01', 'catatan': 'dibayar saat kedatangan', 'dari': 'brankas'}],
  'penjualan': [], 'pengeluaranHarian': [], 'kasbonMutasi': [], 'biayaBulanan': [], 'absenKaryawan': [], 'slipUpah': [], 'modalOwner': [], 'utangOwnerMutasi': [], 'amplopLaba': [], 'pindahUang': [],
  'tutupHari': [], 'setoranKas': [], 'piutangMutasi': [], 'penyesuaianStok': [], 'pemasokCatatan': [], 'aturanToko': [], 'pengaturan': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-08-01', laci: 50000000, brankas: 50000000, rekening: 0, amplop: 0 }));
var P = 'PEMASOK CONTOH'; var nId = 7000; var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var terap = function (r) { if (r.tolak) throw new Error('DITOLAK: ' + r.tolak); if (r.hapus) terapkanKeCache(r.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (r.dokumen) terapkanKeCache(r.dokumen); return r; };
var utang = function () { return hitungUtangPemasok().reduce(function (a, px) { return a + (px.pemasok === P ? px.totalUtang : 0); }, 0); };
var sisa = function (id) { var b = bpSemuaBon(P).find(function (x) { return x.id === id; }); return b ? b.sisa : null; };
var laba = function () { return hitungLabaBersihRentang('2026-08-01', '2026-09-30').labaBersih; };
var bayar = function (id) { return ambilUtangPemasokMutasi().find(function (m) { return String(m.id) === id; }); };
var U0 = utang(), K0 = kasPada(), L0 = laba();

// ---- 0 · semua bon (yang lunas juga) & sisanya = mesin
var S0 = bpSemuaBon(P);
ok('semua bon pemasok (yang lunas juga), urut tertua: bon lama 1 Agu, 10 Agu, 20 Agu, 1 Sep — kedatangan tunai bukan bon; sisa = mesin (20 Agu 11 jt terbuka; 1 Sep lunas oleh pembayaran salah tunjuk)',
  J(S0.map(function (b) { return [b.id, b.jenis, b.tanggal, b.nilai, b.sisa]; })) === J([['sa1', 'saldoAwal', '2026-08-01', 5000000, 0], ['b1', 'batch', '2026-08-10', 10000000, 0], ['b2', 'batch', '2026-08-20', 11000000, 11000000], ['b3', 'batch', '2026-09-01', 12000000, 0]])
  && S0.reduce(function (a, b) { return a + b.sisa; }, 0) === U0 && U0 === 11000000 && S0[3].bayar.length === 1 && S0[3].bayar[0].id === 'p3' && !S0[2].bayar.length, J(S0.map(function (b) { return [b.id, b.sisa, b.bayar.length]; })));

// ---- 1 · PINDAH pembayaran
var H1 = hitungPindahBayar('p3', 'b2');
ok('hitung pindah 12 Sep 12 jt: bon 1 Sep → bon 20 Agu; 20 Agu sisa 11 jt → 0, 1 Sep 0 → 11 jt (kelebihan 1 jt mengalir ke bon tertua yang belum lunas = 1 Sep); utang TETAP; arti menyebut uang toko & laba tidak berubah',
  !H1.tolak && H1.total.dari === 11000000 && H1.total.ke === 11000000 && J(H1.ubah.map(function (x) { return [x.id, x.dari, x.ke]; })) === J([['b2', 11000000, 0], ['b3', 0, 11000000]]) && /utang ke PEMASOK CONTOH tetap Rp11\.000\.000 · uang toko & laba TIDAK berubah/.test(H1.arti) && /bon 1 Sep 2026 → bon 20 Agu 2026/.test(H1.arti), J(H1));
ok('KELEBIHAN disebut (sanggahan E2): Rp1 jt = pembayaran Rp12 jt > sisa bon 20 Agu Rp11 jt, mengalir ke bon 1 Sep — dan itu bon ASAL pembayaran ini (sisanya naik Rp11 jt, bukan Rp12 jt)',
  H1.lebih === 1000000 && H1.terima.length === 1 && H1.terima[0].id === 'b3' && H1.terima[0].asal === true && H1.terima[0].n === 1000000
  && /KELEBIHAN Rp1\.000\.000 \(pembayaran Rp12\.000\.000 > sisa bon 20 Agu 2026 Rp11\.000\.000\) mengalir ke bon tertua yang belum lunas: bon 1 Sep 2026 \(bon asal pembayaran ini\) Rp1\.000\.000/.test(H1.arti), J([H1.lebih, H1.terima, H1.arti]));
ok('pindah tanpa alasan DITOLAK; alasan kurang dari 5 huruf ditolak', /Tulis alasannya dulu/.test(susunPindahBayar('p3', 'b2', '', W).tolak || '') && /Tulis alasannya dulu/.test(susunPindahBayar('p3', 'b2', 'ok', W).tolak || ''));
ok('ke bon yang datang SESUDAH pembayaran DITOLAK; ke bon yang sama ditolak; bon tidak ada ditolak; pembayaran tidak ada ditolak',
  /Bon 1 Sep 2026 belum ada waktu pembayaran 25 Agu 2026 dicatat/.test(hitungPindahBayar('p1', 'b3').tolak || '') && /sudah menunjuk/.test(hitungPindahBayar('p3', 'b3').tolak || '') && /Pilih bon/.test(hitungPindahBayar('p3', 'xx').tolak || '') && /sudah tidak ada/.test(hitungPindahBayar('zz', 'b2').tolak || ''));
var R1 = susunPindahBayar('p3', 'b2', 'kata pemasok: yang dibayar bon 20 Agu', W); var d1 = R1.dokumen[0].data;
ok('dokumen: utangPemasokMutasi yang SAMA (id p3) ditulis ulang — bonId b2, bonTanggal 20 Agu; nominal, tanggal, dari, catatan tetap; alasanKoreksi + riwayat {jenis pindahBon, dari {b3, 1 Sep}, ke {b2, 20 Agu}, alasan, tanggal, jam}',
  R1.dokumen.length === 1 && R1.dokumen[0].koleksi === 'utangPemasokMutasi' && d1.id === 'p3' && d1.bonId === 'b2' && d1.bonTanggal === '2026-08-20' && d1.nominal === 12000000 && d1.tanggal === '2026-09-12' && d1.dari === 'brankas' && d1.catatan === 'dibayar saat kedatangan'
  && d1.alasanKoreksi === 'kata pemasok: yang dibayar bon 20 Agu' && d1.riwayat.length === 1 && d1.riwayat[0].jenis === 'pindahBon' && J(d1.riwayat[0].dari) === J({ bonId: 'b3', bonTanggal: '2026-09-01' }) && J(d1.riwayat[0].ke) === J({ bonId: 'b2', bonTanggal: '2026-08-20' }) && d1.riwayat[0].tanggal === '2026-09-19' && d1.riwayat[0].jam === '10:00', J(R1));
terap(R1);
ok('sesudah pindah: 20 Agu LUNAS, 1 Sep sisa 11 jt; utang tetap 11 jt; kas TETAP; laba TETAP', sisa('b2') === 0 && sisa('b3') === 11000000 && utang() === U0 && kasPada() === K0 && laba() === L0, J([sisa('b2'), sisa('b3'), utang(), kasPada(), K0]));
var S1 = bpSemuaBon(P); var b3 = S1.find(function (b) { return b.id === 'b3'; });
ok('jejak: bon 1 Sep tahu pembayaran itu dulu menunjuknya (dipindahDari); buku bon menyebut "Bayar bon 20 Agu" & DIBETULKAN', b3.dipindahDari.length === 1 && b3.dipindahDari[0].id === 'p3' && bukuBon(P).baris.some(function (e) { return e.id === 'p3' && e.teks === 'Bayar bon 20 Agu 2026 · tunai' && /DIBETULKAN: dipindah dari bon 1 Sep 2026 ke bon 20 Agu 2026/.test(e.ket); }), J(bukuBon(P).baris));

// ---- 2 · JUMLAH pembayaran
var H2 = hitungNominalBayar('p3', '11.000.000');
ok('hitung jumlah 12 jt → 11 jt: utang 11 jt → 12 jt (kelebihan 1 jt hilang), kas NAIK 1 jt (brankas), laba tetap', !H2.tolak && H2.total.dari === 11000000 && H2.total.ke === 12000000 && H2.kas.ke - H2.kas.dari === 1000000 && /uang toko \(Brankas\) bertambah Rp1\.000\.000/.test(H2.arti) && /laba TIDAK berubah/.test(H2.arti), J(H2));
ok('jumlah sama / kosong / tanpa alasan ditolak', /sama dengan yang tercatat/.test(hitungNominalBayar('p3', '12000000').tolak || '') && /Ketik jumlah/.test(hitungNominalBayar('p3', '').tolak || '') && /Tulis alasannya/.test(susunNominalBayar('p3', '11000000', '', W).tolak || ''));
var R2 = susunNominalBayar('p3', '11.000.000', 'salah ketik — yang diserahkan 11 jt', W); terap(R2); var d2 = bayar('p3');
ok('selisih kecil (12 jt → 11 jt) bukan "besar" — satu ketukan', H2.besar.length === 0, J(H2.besar));
ok('sesudahnya: nominal 11 jt, riwayat dua baris (pindahBon lalu nominalBayar {dari 12 jt, ke 11 jt}); utang 12 jt; kas +1 jt; laba tetap', d2.nominal === 11000000 && d2.riwayat.length === 2 && d2.riwayat[1].jenis === 'nominalBayar' && d2.riwayat[1].dari === 12000000 && d2.riwayat[1].ke === 11000000 && utang() === 12000000 && kasPada() === K0 + 1000000 && laba() === L0, J([d2, utang(), kasPada()]));

// ---- 2b · PENJAGA BESARAN jumlah pembayaran (sanggahan E2): selisih besar = ketukan kedua, kalimat menyebut lama → baru
var H2b = hitungNominalBayar('p3', '110.000.000'); var R2b = susunNominalBayar('p3', '110.000.000', 'salah ketik nol', W);
ok('11 jt → 110 jt (nol kelebihan): BESAR — "10× lipat", naik melebihi sisa bon 20 Agu; ketukan pertama DITOLAK minta ketukan kedua, kalimat menyebut Rp11.000.000 → Rp110.000.000; tanpa dokumen',
  !H2b.tolak && H2b.besar.length >= 2 && /10× lipat/.test(H2b.besarTeks) && /lebih dari sisa bon 20 Agu 2026/.test(H2b.besarTeks) && R2b.perluYakin === true && /Rp11\.000\.000 → Rp110\.000\.000/.test(R2b.tolak) && /Ketuk sekali lagi/.test(R2b.tolak) && !R2b.dokumen, J([H2b.besarTeks, R2b]));
var R2c = susunNominalBayar('p3', '110.000.000', 'salah ketik nol', W, true);
ok('ketukan kedua (yakin) → dokumen pembetulan ditulis (owner yang memutuskan)', !R2c.tolak && R2c.dokumen.length === 1 && R2c.dokumen[0].data.nominal === 110000000, J(R2c));
ok('11 jt → 1,1 jt (nol kurang satu): BESAR — "tinggal 10 %"', /tinggal 10 %/.test(hitungNominalBayar('p3', '1.100.000').besarTeks), hitungNominalBayar('p3', '1.100.000').besarTeks);
pasok('tutupHari', [{ id: 'th1', tanggal: '2026-08-25', jam: '21:00' }]);
var H2d = hitungNominalBayar('p1', '4.900.000');
ok('pembayaran TUNAI dari laci di hari yang sudah DITUTUP (25 Agu): BESAR walau selisihnya kecil — kalimat menyebut tutup hari tidak dihitung ulang', H2d.besar.length === 1 && /hari 25 Agu 2026 sudah DITUTUP/.test(H2d.besarTeks) && /Rp5\.000\.000 → Rp4\.900\.000/.test(H2d.besarTeks), J(H2d.besar));
pasok('tutupHari', []);
ok('hari yang sama tanpa tutup hari → bukan besar', hitungNominalBayar('p1', '4.900.000').besar.length === 0);
var kasSkr = kasPada(); var Hk = hitungNominalBayar('p2', String(10000000 + kasSkr + 1000000));
ok('kenaikan yang membuat uang toko MINUS → BESAR, kalimat menyebut minusnya', kasSkr > 0 && /uang toko jadi MINUS Rp1\.000\.000/.test(Hk.besarTeks), J([kasSkr, Hk.besarTeks]));

// ---- 3 · NOMOR bon
var R3 = susunNoBon('b2', P, '  12345 ', '', W); var d3 = R3.dokumen[0].data;
ok('nomor bon kedatangan: batchMasuk YANG SAMA + noBon "12345" + riwayat noBon; TANPA alasanKoreksi (bukan koreksi barang); merkList utuh; kabar: utang, kas, laba tidak berubah', R3.dokumen[0].koleksi === 'batchMasuk' && d3.id === 'b2' && d3.noBon === '12345' && !d3.alasanKoreksi && d3.riwayat.length === 1 && d3.riwayat[0].jenis === 'noBon' && d3.riwayat[0].ke === '12345' && J(d3.merkList) === J(KOTAK.batchMasuk[1].merkList) && /utang, kas, dan laba tidak berubah/.test(R3.patch.kabar), J(R3));
terap(R3);
ok('nomor bon tampil: susunBon (tusukan) membawa noBon bon terbuka; buku bon "Barang datang — bon No. 12345"; bpSemuaBon noBon', bukuBon(P).baris.some(function (e) { return e.teks === 'Barang datang — bon No. 12345'; }) && bpSemuaBon(P).find(function (b) { return b.id === 'b2'; }).noBon === '12345' && (function () { terap(susunNoBon('b3', P, '777', '', W)); return susunBon(new Date(Date.now())).bon.find(function (b) { return b.id === 'b3'; }).noBon === '777'; })(), J(bukuBon(P).baris));
ok('ganti nomor tanpa alasan ditolak; nomor sama ditolak; nomor kembar di bon lain ditolak; dengan alasan → riwayat bertambah', /tulis alasannya/.test(susunNoBon('b2', P, '12346', '', W).tolak || '') && /sudah tercatat/.test(susunNoBon('b2', P, '12345', '', W).tolak || '') && /sudah dipakai bon 1 Sep 2026 No\. 777/.test(susunNoBon('b2', P, '777', 'ok sekali', W).tolak || '')
  && (function () { var r = susunNoBon('b2', P, '12346', 'salah baca angka', W); return !r.tolak && r.dokumen[0].data.riwayat.length === 2 && r.dokumen[0].data.riwayat[1].dari === '12345'; })());
var R3b = susunNoBon('sa1', P, 'L-1', '', W); terap(R3b);
ok('nomor bon LAMA: utangPemasokMutasi saldoAwal + noBon; buku bon "Bon lama (sebelum sistem) No. L-1"', R3b.dokumen[0].koleksi === 'utangPemasokMutasi' && R3b.dokumen[0].data.noBon === 'L-1' && bukuBon(P).baris.some(function (e) { return e.teks === 'Bon lama (sebelum sistem) No. L-1'; }), J(R3b));

// ---- 4 · bon LAMA: tanggal & nilai
var H4 = hitungBetulBonLama('sa1', { tgl: '2026-07-31', ketik: '5.500.000' });
ok('hitung bon lama 5 jt → 5,5 jt, 1 Agu → 31 Jul: utang naik 500 rb; uang, stok, laba tidak berubah', !H4.tolak && H4.total.ke - H4.total.dari === 500000 && /nilai Rp5\.000\.000 → Rp5\.500\.000, tanggal 1 Agu 2026 → 31 Jul 2026/.test(H4.arti), J(H4));
ok('bon kedatangan tidak dibetulkan di sini (lewat Barang masuk); tanpa perubahan ditolak; tanggal rusak ditolak', /lewat Stok › Barang masuk/.test(hitungBetulBonLama('b2', {}).tolak || '') && /Tidak ada yang berubah/.test(hitungBetulBonLama('sa1', { tgl: '2026-08-01', ketik: '5000000' }).tolak || '') && /tidak terbaca/.test(hitungBetulBonLama('sa1', { tgl: '31/7', ketik: '1' }).tolak || ''));
var R4 = susunBetulBonLama('sa1', { tgl: '2026-07-31', ketik: '5500000' }, 'kertas bon ketemu', W); terap(R4); var d4 = bayar('sa1') || ambilUtangPemasokMutasi().find(function (m) { return m.id === 'sa1'; });
ok('sesudahnya: bon lama 5,5 jt bertanggal 31 Jul, riwayat bonLama {dari {5 jt, 1 Agu}, ke {5,5 jt, 31 Jul}}, noBon tetap; utang +500 rb; kas & laba tetap', d4.nominal === 5500000 && d4.bonTanggal === '2026-07-31' && d4.noBon === 'L-1' && d4.riwayat.slice(-1)[0].jenis === 'bonLama' && J(d4.riwayat.slice(-1)[0].dari) === J({ nominal: 5000000, bonTanggal: '2026-08-01' }) && utang() === 12500000 && kasPada() === K0 + 1000000 && laba() === L0, J([d4, utang()]));

// ---- 5 · BULAN TERKUNCI ditolak
pasok('aturanToko', [{ id: 'kunciPeriode', sampaiBulan: '2026-09', riwayat: [{ aksi: 'kunci', bulan: '2026-09', olehUid: 'x' }] }]);
ok('September terkunci: pindah pembayaran 12 Sep DITOLAK, jumlahnya DITOLAK, nomor bon kedatangan 20 Agu DITOLAK, bon lama DITOLAK — kalimat menyebut bulannya',
  /Bulan September 2026 terkunci/.test(hitungPindahBayar('p3', 'b1').tolak || '') && /Bulan September 2026 terkunci/.test(hitungNominalBayar('p3', '1000').tolak || '') && /Bulan Agustus 2026 terkunci/.test(susunNoBon('b2', P, '999', 'alasan cukup', W).tolak || '') && /terkunci/.test(hitungBetulBonLama('sa1', { tgl: '2026-07-30', ketik: '5500000' }).tolak || ''),
  J([hitungPindahBayar('p3', 'b1').tolak, susunNoBon('b2', P, '999', 'alasan cukup', W).tolak]));
pasok('aturanToko', []);

// ---- 6 · koreksi kedatangan membawa nomor bon (statis di sisi python) & identitas akhir
ok('identitas akhir: Σ sisa semua bon = mesin = 12,5 jt', bpSemuaBon(P).reduce(function (a, b) { return a + b.sisa; }, 0) === utang() && utang() === 12500000, J(bpSemuaBon(P).map(function (b) { return [b.id, b.sisa]; })));

// ==================== ASAP: cadangan toko ====================
var asap = null;
if (CADANGAN) {
  Object.keys(CADANGAN).forEach(function (n) { if (Array.isArray(CADANGAN[n])) pasok(n, CADANGAN[n]); }); localStorage.removeItem('miqbal_titik_kas_v1'); pasok('aturanToko', (CADANGAN.aturanToko || []).filter(function (a) { return a.id !== 'kunciPeriode'; }));
  var kini2 = new Date(Date.now()); var W2 = { tanggal: hariIniIso(kini2), jam: '20:00', kini: kini2.toISOString(), idUnik: function () { return 'x' + Math.random(); } };
  var salah = []; var pem = {}; hitungUtangPemasok().forEach(function (px) { pem[px.pemasok] = px.totalUtang; });
  ambilUtangPemasokMutasi().forEach(function (m) { if (m.pemasok) pem[String(m.pemasok).trim()] = pem[String(m.pemasok).trim()] || 0; });
  var coba = 0, berhasil = 0;
  Object.keys(pem).forEach(function (nm) { var S = bpSemuaBon(nm); var tot = S.reduce(function (a, b) { return a + b.sisa; }, 0); if (tot !== pem[nm]) salah.push('Σ sisa ≠ mesin untuk satu pemasok');
    S.forEach(function (b) { b.bayar.forEach(function (m) { var tua = S.find(function (x) { return x.id !== b.id && (!x.tanggal || !m.tanggal || x.tanggal <= m.tanggal); }); if (!tua) return; coba += 1;
      var U1 = hitungUtangPemasok().reduce(function (a, px) { return a + px.totalUtang; }, 0), Kk = kasPada(); var H = hitungPindahBayar(m.id, tua.id); if (H.tolak) return; berhasil += 1;
      if (H.total.dari !== H.total.ke) salah.push('pindah menggeser utang total');
      var r = susunPindahBayar(m.id, tua.id, 'uji asap pembetulan', W2); var sesudah = denganCacheSementara(r.dokumen, function () { return { u: hitungUtangPemasok().reduce(function (a, px) { return a + px.totalUtang; }, 0), k: kasPada() }; });
      if (sesudah.u !== U1 || sesudah.k !== Kk) salah.push('pindah menggeser utang/kas'); }); }); });
  asap = { salah: salah, pemasok: Object.keys(pem).length, pindahDicoba: coba, pindahBoleh: berhasil };
  ok('ASAP: Σ sisa = mesin tiap pemasok; tiap pembayaran bertunjuk bisa dipindah ke bon lain tanpa menggeser utang total & kas', !salah.length, J(asap));
}
print(J({ lulus: lulus, gagal: gagal, asap: asap }));
"""


def jalan_utama(js, pakai_cadangan):
    cad = 'null'; p = uji_wadah_bernama.cadangan_toko() if pakai_cadangan else None
    if p: cad = uji_wadah_bernama.cad_js(p)[0]
    h, e = uji_wadah_bernama.jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CADANGAN = ' + cad + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    return h['lulus'], h['gagal'], h.get('asap')


def statis(teks=None):
    """Koreksi kedatangan membawa noBon; layar memasang pembetulan (owner) & bulan terkunci lewat tolakKunci; tanggal bon lama = pemilih tanggal; jumlah BESAR = dua ketukan."""
    g = []; T = teks or {}
    def baca(p): return T[p] if p in T else open(os.path.join(AKAR, p), encoding='utf-8').read()
    sc = baca('baru/js/layar/stok-catat-logika.js')
    if "['oleh', 'perangkat', 'catatan', 'noBon'].indexOf(k) >= 0" not in sc: g.append('koreksi kedatangan tidak membawa noBon')
    hj = baca('baru/js/layar/harga.js')
    for aksi in ['bpBetulBuka', 'bpBetulPindah', 'bpBetulNominal', 'bpBetulNo', 'bpBetulLama']:
        if ('data-aksi="' + aksi + '"') not in hj or (aksi + ':') not in hj: g.append('layar: tombol/penangan ' + aksi + ' tidak lengkap')
    if '<input class="ketik-nama" id="bpBetulTgl" type="date" value="${d.tgl}" data-ketik="bpBetulKetik" data-kolom="tgl">' not in hj: g.append('tanggal bon lama bukan pemilih tanggal (type="date") — papan angka iPhone tidak punya "-"')
    if "BP.susunNominalBayar(d.bayarId, d.ketik, d.alasan, waktu(), d.yakinN === String(d.ketik))" not in hj or 'if (r.perluYakin) return set({ betul: Object.assign({}, d, { yakinN: String(d.ketik) })' not in hj: g.append('layar: jumlah pembayaran BESAR tanpa ketukan kedua')
    bp = baca('baru/js/layar/bon-pemasok-logika.js')
    if bp.count("tolakKunci('utangPemasokMutasi'") < 3: g.append('pembetulan pembayaran/bon lama tanpa penjaga bulan terkunci')
    return g


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            'pindah menimpa tanpa jejak (riwayat dibuang)': js.replace("  const data = Object.assign({}, H.baru, { alasanKoreksi: al, dikoreksiPada: w.kini,\n    riwayat: bpRiwayat(H.m, w, { jenis: 'pindahBon',", "  const data = Object.assign({}, H.baru, { alasanKoreksi: al, dikoreksiPada: w.kini,\n    riwayatX: bpRiwayat(H.m, w, { jenis: 'pindahBon',"),
            'pindah tanpa alasan diterima': js.replace("const al = bpAlasan(alasan); if (al.length < BP_ALASAN_MIN) return { tolak: 'Tulis alasannya dulu (mis. \"pemasok: bon 31 Agu yang lunas, bukan 18 Sep\")", "const al = bpAlasan(alasan); if (false) return { tolak: 'Tulis alasannya dulu (mis. \"pemasok: bon 31 Agu yang lunas, bukan 18 Sep\")"),
            'pindah ke bon yang datang sesudah pembayaran diterima': js.replace("else if (ke.tanggal && m.tanggal && ke.tanggal > m.tanggal) tolak =", "else if (false) tolak ="),
            'bulan terkunci tidak dijaga (pindah)': js.replace("else tolak = tolakKunci('utangPemasokMutasi', m, 'pembayaran bulan itu tidak bisa dipindah lagi');", "else tolak = '';"),
            'nomor bon menandai kedatangan dikoreksi (garis waktu HPP)': js.replace("const data = Object.assign({}, b.dok, { noBon: nb, riwayat:", "const data = Object.assign({}, b.dok, { noBon: nb, alasanKoreksi: 'nomor bon', riwayat:"),
            'nomor kembar diterima': js.replace("const kembar = semua.find((x) => x.id !== b.id && x.noBon === nb);", "const kembar = null;"),
            'pindah juga mengubah jumlahnya': js.replace("const baru = Object.assign({}, m, { bonId: ke ? ke.id : String(m.bonId || ''), bonTanggal: ke ? (ke.tanggal || null) : (m.bonTanggal || null) });", "const baru = Object.assign({}, m, { nominal: ke ? ke.sisa || m.nominal : m.nominal, bonId: ke ? ke.id : String(m.bonId || ''), bonTanggal: ke ? (ke.tanggal || null) : (m.bonTanggal || null) });"),
            'sisa bon lunas dibaca nilai (bukan mesin)': js.replace("out.forEach((b) => { b.sisa = sisa[b.id] !== undefined ? sisa[b.id] : 0;", "out.forEach((b) => { b.sisa = sisa[b.id] !== undefined ? sisa[b.id] : b.nilai;"),
            'jumlah pembayaran tanpa alasan diterima': js.replace("const al = bpAlasan(alasan); if (al.length < BP_ALASAN_MIN) return { tolak: 'Tulis alasannya dulu (mis. \"salah ketik", "const al = bpAlasan(alasan); if (false) return { tolak: 'Tulis alasannya dulu (mis. \"salah ketik"),
            'buku bon tidak menyebut pembetulan': js.replace("+ (m.alasanKoreksi ? ' · DIBETULKAN: ' + ((m.riwayat || []).slice(-1)[0] || {}).teks : '')", ""),
            'kelebihan saat pindah tidak disebut': js.replace("const nom = Math.round(Number(m.nominal) || 0); const lebih = ke ? Math.max(0, nom - ke.sisa) : 0;", "const nom = Math.round(Number(m.nominal) || 0); const lebih = 0;"),
            'kelebihan ke bon asal tidak dikenali (cuma bon "lain")': js.replace("const harap = b.id === dari.id ? s0 + nom : s0;", "const harap = s0;"),
            'jumlah besar tanpa ketukan kedua': js.replace("  if (H.besar.length && !yakin) return { tolak: H.besarTeks + '. Ketuk sekali lagi kalau memang benar.', perluYakin: true };", ""),
            'penjaga besaran tanpa hitungan lipat': js.replace("    if (lama > 0 && n >= lama * 2) besar.push(", "    if (false) besar.push("),
            'hari yang sudah ditutup tidak disebut': js.replace("if ((m.dari || 'laci') === 'laci' && ambilTutupHari().some((x) => x && x.tanggal === m.tanggal)) besar.push(", "if (false) besar.push("),
            'uang toko minus tidak dijaga': js.replace("    if (d > 0 && sesudah.kas !== null && sesudah.kas < 0) besar.push(", "    if (false) besar.push("),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g, _ = jalan_utama(isi, False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        hj0 = open(os.path.join(AKAR, 'baru/js/layar/harga.js'), encoding='utf-8').read()
        statis_rusak = {
            'tanggal bon lama kembali ke kotak teks inputmode numeric (iPhone tanpa "-")': {'baru/js/layar/harga.js': hj0.replace('id="bpBetulTgl" type="date" value=', 'id="bpBetulTgl" type="text" inputmode="numeric" placeholder="2026-08-31" value=', 1)},
            'layar mengirim jumlah BESAR tanpa ketukan kedua': {'baru/js/layar/harga.js': hj0.replace("d.yakinN === String(d.ketik));", "true);", 1)},
        }
        for nama, tk in statis_rusak.items():
            if all(v == open(os.path.join(AKAR, k), encoding='utf-8').read() for k, v in tk.items()): print('KONTROL BASI  ' + nama); kode = 3; continue
            g = statis(tk)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = jalan_utama(js, True)
    g = g + statis()
    print('PEMBETULAN BON PEMASOK (kotak pasir + statis): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    p = uji_wadah_bernama.cadangan_toko()
    if p and asap: print('ASAP DATA TOKO (%s): %s' % (os.path.basename(p), json.dumps(asap, ensure_ascii=False)[:600]))
    sys.exit(0 if not g else 2)
