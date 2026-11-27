#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_arsip_audit_p8.py — Paket P8 · Arsip, audit & bagikan (owner 27 Nov 2026, sensus A94 B13 B81 B103; rules v26). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  AF foto nota (A94): jenis foto dari idBon (tunai / bon / kas / bon lama), tanda ringan tanpa gambar (kolom = stafTandaFoto), penjaga kiriman tablet (fotoNotaSah /
     tandaFotoSah = rules v26), hitungan BELUM BERFOTO 30 hari (kedatangan nyata saja; kas kecil "nota ada" tanpa foto), per bulan, tanda foto lama yang kurang, berkas
     arsip HTML (nama di-escape, urut, tanpa foto = ditolak), Dasbor › Mutu = afBelum apa adanya.
  ORP omzet per perangkat (B13): label & tebakan jenis, Σ per perangkat MENUTUP ke Σ nota rentang (nota batal tidak ikut), nota unik per grup.
  JC log (B81): rentang satu hari SETEMPAT (WIB) dalam UTC, rentang 30 hari cadangan, saringan orang / jenis / kata / jejak kiriman staf, kalimat terpotong, log ikut berkas
     cadangan & terbaca lagi lewat isiDariCadangan.
  DPB tautan beku Dasbor (B103): pilihan sah (bagian ≥ 1, hari 1/7/30/90, catatan ≤ 40), dokumen = kode 22 huruf + `sampai` + HANYA bagian dicentang, tanpa nama orang,
     angka = fungsi sumber (lpRekapRentang · klKgBulan · klMarginBulan · neracaPada · saldoKantong), aktif / lewat, cabut, bersihkan, tautan & pesan WhatsApp.
  ST statis: halaman dasbor-publik.html (CSP ketat, tanpa penyimpanan / tautan keluar, 403/404 = tidak berlaku), penulis pusat (dasborPublik tanpa atribusi, foto + tanda
     satu kiriman, tanda ikut terhapus, baca log & foto bulan owner saja), rules v26, koleksi.js, app.js / stok.js / menu.js / dasbor tersambung, index.html.

    python3 alat-uji/uji_arsip_audit_p8.py            → N lulus · 0 gagal (+ asap cadangan toko bila ada; angka rupiah toko TIDAK dicetak)
    python3 alat-uji/uji_arsip_audit_p8.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_dasbor_sensus, uji_kunci_periode, uji_sisa_sensus  # noqa: E402
AF = 'baru/js/layar/arsip-foto-logika.js'; ORP = 'baru/js/layar/omzet-perangkat-logika.js'; JC = 'baru/js/layar/jejak-cari-logika.js'; DPB = 'baru/js/layar/dasbor-publik-logika.js'
BP = 'baru/js/layar/bon-publik-logika.js'; FB = 'baru/js/layar/foto-bon-logika.js'; AK = 'baru/js/data/akses.js'; CD = 'baru/js/data/cadangan.js'; DL = 'baru/js/layar/dasbor-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_dasbor_sensus.MODUL + [AF, ORP, JC, DPB, BP, FB, AK, CD])))
SUMBER = {'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'html': 'baru/dasbor-publik.html', 'hal': 'baru/js/dasbor-publik-halaman.js', 'fb': 'baru/js/data/firebase.js',
          'rules': 'firestore.rules', 'koleksi': 'baru/js/data/koleksi.js', 'app': 'baru/js/app.js', 'stok': 'baru/js/layar/stok.js', 'menu': 'baru/js/layar/menu.js', 'dasbor': 'baru/js/layar/dasbor.js',
          'kisi': 'baru/js/layar/dasbor-kisi.js', 'index': 'baru/index.html', 'panel': 'baru/js/layar/arsip-audit-panel.js', 'fnp': 'baru/js/layar/foto-nota-panel.js', 'bundel': 'alat-uji/bundel_baru.py',
          'peta': 'alat-uji/peta_akses.py', 'css_stok': 'baru/css/stok.css', 'css_menu': 'baru/css/menu.css', 'ak': AK, 'af': AF, 'orp': ORP, 'jc': JC, 'dpb': DPB, 'dl': DL}

def B(i, tgl, cara, pemasok, kg=500, **x):
    d = {'id': i, 'tanggal': tgl, 'jam': '08:00', 'caraBayar': cara, 'pemasok': pemasok, 'biayaBongkar': 0,
         'merkList': [{'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'totalKg': kg, 'subtotalHarga': kg * 13000, 'hargaPerKg': 13000}]}
    d.update(x); return d
def P(i, tgl, n, perangkat=None, **x):
    d = {'id': i, 'tanggal': tgl, 'jam': '09:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': 'Angsa', 'beratKarungAcuan': 50, 'jumlahKarung': 1, 'totalKg': 50, 'hargaTotal': n,
         'hppTotalSaatJual': round(n * 0.9), 'grupNota': 'g' + str(i)}
    if perangkat: d['perangkat'] = perangkat
    d.update(x); return d
KOTAK = {
    'batchMasuk': [B('1764000000001.5', '2026-11-28', 'tunai', 'Pemasok Tunai'), B('1764000000002.5', '2026-11-29', 'utang', 'Pemasok Bon', noBon='77'),
                   B('1764000000003.5', '2026-12-01', 'tunai', 'Pemasok <b>Aneh</b>'), B('1764000000004.5', '2026-10-01', 'tunai', 'Pemasok Lama'),
                   B('1700000000000.5', '2026-11-20', 'tunai', 'STOK AWAL', stokAwal=True), B('1764000000005.5', '2026-11-30', 'tunai', 'LAHIR BUKU', kg=0, lahirBuku=True)],
    'fotoTanda': [{'id': '9001.5', 'idBon': '1764000000002.5', 'jenis': 'bon', 'pemasok': 'Pemasok Bon', 'tanggalBon': '2026-11-29', 'tanggal': '2026-11-29', 'jam': '09:00', 'byte': 250000}],
    'utangPemasokMutasi': [{'id': 'sa-1', 'tipe': 'saldoAwal', 'pemasok': 'Pemasok Bon', 'nominal': 500000, 'bonTanggal': '2026-08-01'}],
    'pengeluaranHarian': [{'id': 501, 'tanggal': '2026-12-01', 'jam': '10:00', 'kategori': 'toko', 'nominal': 25000, 'keterangan': 'plastik', 'nota': 'ada'},
                          {'id': 502, 'tanggal': '2026-12-01', 'jam': '10:05', 'kategori': 'toko', 'nominal': 30000, 'keterangan': 'bensin', 'nota': 'ada', 'fotoNota': ['8001.5']},
                          {'id': 503, 'tanggal': '2026-12-01', 'jam': '10:10', 'kategori': 'toko', 'nominal': 10000, 'keterangan': 'batal', 'nota': 'ada', 'dibatalkan': True}],
    'penjualan': [P(1, '2026-12-01', 650000, 'Mac Owner'), P(2, '2026-12-01', 1300000, 'Tablet kasir', grupNota='gT'), P(3, '2026-12-01', 650000, 'Tablet kasir', grupNota='gT'),
                  P(4, '2026-12-02', 700000, 'Iphone Owner'), P(5, '2026-12-02', 50000, None, asalDarurat=True), P(6, '2026-12-02', 999000, 'Mac Owner', dibatalkan=True),
                  P(7, '2026-11-15', 400000, None), P(8, '2026-11-16', 300000, 'p-mvwl82s4-3s9sn')],
    'perangkatStatus': [{'id': 'p-mvwl82s4-3s9sn', 'nama': '', 'aplikasi': 'baru', 'pada': '2026-12-02T01:00:00.000Z'}, {'id': 'p-abc', 'nama': 'Tablet kasir', 'aplikasi': 'baru', 'pada': '2026-12-02T01:00:00.000Z'}],
    'pelangganCatatan': [{'id': 'bu sari', 'nama': 'Bu Sari', 'catatan': 'warung'}],
    'piutangMutasi': [], 'dasborPublik': [], 'aturanToko': [],
}

SKENARIO = r"""
(function () {
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); };
var KINI = new Date('2026-12-02T14:00:00+07:00'); var nId = 900000;
var W = { tanggal: '2026-12-02', jam: '14:00', kini: '2026-12-02T07:00:00.000Z', idUnik: function () { nId += 1; return nId + 0.5; } };
__dom['jualKarungBerat'] = { value: '50' };
var K0 = JSON.parse(J(KOTAK)); Object.keys(K0).forEach(function (n) { pasok(n, K0[n]); }); setelSumber('cadangan', 'kotak pasir');
var aman = function (nama, f) { try { return f(); } catch (e) { gagal.push(nama + ' JATUH: ' + (e && e.message) + ' ' + String(e && e.stack).slice(0, 300)); return null; } };

// ==================== AF · FOTO NOTA (A94) ====================
ok('AF: jenis dari idBon — kedatangan tunai / bon, nota kas kecil (uk-…), bon lama (saldoAwal), tidak dikenal', afJenis('1764000000001.5') === 'tunai' && afJenis('1764000000002.5') === 'bon'
  && afJenis('uk-501') === 'kas' && afJenis('sa-1') === 'saldoAwal' && afJenis('zzz') === '' && afJenis('') === '');
var FD = fbnSusunSimpan({ id: '1764000000001.5', pemasok: 'Pemasok Tunai', tanggal: '2026-11-28', noBon: '' }, { jenis: 'image/jpeg', base64: 'QUJD', byte: 3, lebar: 10, tinggi: 10 }, W, [], 0).data;
var T1 = afTandaDari(FD);
ok('AF: tanda = id foto, idBon, jenis tunai, tanggal foto, byte — TANPA gambar (kolom tanda saja)', T1 && T1.id === String(FD.id) && T1.idBon === '1764000000001.5' && T1.jenis === 'tunai' && T1.tanggal === '2026-12-02'
  && !('base64' in T1) && Object.keys(T1).every(function (k) { return ['id', 'idBon', 'jenis', 'pemasok', 'tanggalBon', 'tanggal', 'jam', 'byte'].indexOf(k) >= 0; }), J(T1));
ok('AF: foto tanpa id / idBon → tanpa tanda', afTandaDari({ idBon: 'x' }) === null && afTandaDari({ id: 1 }) === null && afTandaDari(null) === null);
var atr = function (d) { return Object.assign({}, d, { oleh: 'UJI B', olehUid: 'uid-uji-b', perangkat: 'Tablet uji', diubahOleh: 'UJI B', diubahOlehUid: 'uid-uji-b', diubahPerangkat: 'Tablet uji', diubahPada: W.kini }); };
ok('AF: penjaga kiriman tablet (= rules v26) MENERIMA foto nota kedatangan & tandanya (beratribusi)', fotoNotaSah(atr(FD)) && tandaFotoSah(atr(T1)));
ok('AF: penjaga kiriman MENOLAK foto nota kas kecil (uk-…), kolom asing, jenis berkas lain; tanda berjenis kas / tanpa tanggal',
  !fotoNotaSah(atr(Object.assign({}, FD, { idBon: 'uk-501' }))) && !fotoNotaSah(atr(Object.assign({}, FD, { hargaTotal: 1 }))) && !fotoNotaSah(atr(Object.assign({}, FD, { jenis: 'text/html' })))
  && !tandaFotoSah(atr(Object.assign({}, T1, { jenis: 'kas' }))) && !tandaFotoSah(atr(Object.assign({}, T1, { tanggal: '' }))) && !tandaFotoSah(atr(Object.assign({}, T1, { base64: 'QUJD' }))));
var akB = { jenis: 'aktif', peran: 'ben', uid: 'uid-uji-b', nama: 'UJI B' }, akK = { jenis: 'aktif', peran: 'karyawan', uid: 'uid-uji-k', nama: 'UJI K' };
ok('AF: boleh memotret nota = owner & Penjaga laci aktif; karyawan & akun mati tidak', bolehFotoNota({ jenis: 'owner' }) && bolehFotoNota(akB) && !bolehFotoNota(akK) && !bolehFotoNota({ jenis: 'mati', peran: 'ben' }) && !bolehFotoNota(null));
var PK = periksaKiriman(akB, [{ koleksi: 'fotoTanda', data: atr(T1) }], [], { }, KINI);
ok('AF: BUAT_STAF fotoTanda = Penjaga laci; kiriman tanda yang sah lolos penjaga, yang berjenis kas ditolak; karyawan ditolak', J(BUAT_STAF.fotoTanda) === J(['ben']) && !PK.tolak
  && !!periksaKiriman(akB, [{ koleksi: 'fotoTanda', data: atr(Object.assign({}, T1, { jenis: 'kas' })) }], [], {}, KINI).tolak && !!periksaKiriman(akK, [{ koleksi: 'fotoTanda', data: atr(T1) }], [], {}, KINI).tolak, J(PK));
var BL = afBelum(KINI);
ok('AF: belum berfoto 30 hari = kedatangan nyata tanpa tanda (tunai 28 Nov & 1 Des); bon 29 Nov bertanda; stok awal, lahir buku & kedatangan Okt tidak dihitung', BL.kedatangan === 3 && BL.berfoto === 1
  && J(BL.belum.map(function (x) { return [x.id, x.jenis]; })) === J([['1764000000003.5', 'tunai'], ['1764000000001.5', 'tunai']]) && BL.nTunai === 2 && BL.nBon === 0, J(BL));
ok('AF: nota kas kecil "nota ada" tanpa foto dihitung (yang berfoto & yang dibatalkan tidak); n = kedatangan + kas', BL.kas.length === 1 && BL.kas[0].id === '501' && BL.n === 3, J(BL.kas));
ok('AF: kalimat menyebut tunai · bon & kas kecil; ada tanda → tanpa catatan foto lama', /2 dari 3 kedatangan belum berfoto \(2 tunai · 0 bon\)/.test(BL.kalimat) && /1 nota kas kecil/.test(BL.kalimat) && BL.catatanLama === '' && BL.tujuan.sistem === 'cadangan' && BL.tujuan.tab === 'foto', BL.kalimat);
var DM = aman('dbMutu', function () { return dbMutu(KINI); });
ok('AF: Dasbor › Mutu memuat hitungan belum berfoto APA ADANYA (afBelum)', DM && DM.foto && !DM.foto.galat && J(DM.foto) === J(BL), DM && J(DM.foto).slice(0, 300));
var BU = afBulan(KINI, 3);
ok('AF: per bulan (tanggal foto) — Des 0 foto & 0 dari 1 kedatangan, Nov 1 foto bon (± 244 KB) & 1 dari 2 kedatangan berfoto, Okt 0 dari 1', BU.length === 3 && BU[0].key === '2026-12' && BU[0].foto === 0 && BU[0].kedatangan === 1 && BU[1].key === '2026-11' && BU[1].foto === 1
  && BU[1].kb === 244 && BU[1].kedatangan === 2 && BU[1].berfoto === 1 && J(BU[1].perJenis) === J([{ jenis: 'bon', n: 1 }]) && BU[2].kedatangan === 1 && BU[2].berfoto === 0, J(BU));
var FOTO = [Object.assign({}, FD, { id: '9001.5', idBon: '1764000000002.5', tanggal: '2026-11-29', jam: '09:00', pemasok: 'Pemasok Bon' }), Object.assign({}, FD, { id: '9002.5', tanggal: '2026-11-28', jam: '07:00', pemasok: 'Pemasok <b>Aneh</b>', base64: 'QU"JD' })];
var TK = afSusunTandaKurang(FOTO);
ok('AF: tanda foto lama yang kurang — hanya yang belum bertanda (9002.5), koleksi fotoTanda; semuanya sudah = kosong', TK.dokumen && TK.dokumen.length === 1 && TK.dokumen[0].koleksi === 'fotoTanda' && TK.dokumen[0].data.id === '9002.5'
  && afSusunTandaKurang([FOTO[0]]).kosong === true, J(TK));
var BA = afBerkasArsip(FOTO, '2026-11', KINI);
ok('AF: berkas arsip = HTML mandiri, urut tanggal foto, nama pemasok di-escape, base64 dibersihkan, daftar JSON di dalamnya', BA.nama === 'arsip-foto-miqbal-2026-11.html' && BA.n === 2 && /^<!doctype html>/.test(BA.isi)
  && BA.isi.indexOf('<b>Aneh</b>') < 0 && BA.isi.indexOf('&lt;b&gt;Aneh&lt;/b&gt;') > 0 && BA.isi.indexOf('QU"JD') < 0 && BA.isi.indexOf('Pemasok &lt;b&gt;Aneh') < BA.isi.indexOf('Pemasok Bon') && /id="daftar-foto"/.test(BA.isi), BA.isi.slice(0, 200));
ok('AF: bulan tanpa foto → ditolak (tidak mengunduh berkas kosong)', !!afBerkasArsip([], '2026-12', KINI).tolak);
var KD = afKedatangan('1764000000002.5');
ok('AF: kartu kedatangan — jenis, pemasok, jumlah foto bertanda; stok awal bukan kedatangan', KD && KD.jenis === 'bon' && KD.nFoto === 1 && KD.noBon === '77' && afKedatangan('1700000000000.5') === null && afIdKedatanganSah('1764000000001.5') && !afIdKedatanganSah('uk-1'));

// ==================== ORP · OMZET PER PERANGKAT (B13) ====================
ok('ORP: label = perangkat pencatat; kasir darurat tanpa nama; tanpa keterangan = tidak tercatat', orpLabel({ perangkat: ' Mac Owner ' }) === 'Mac Owner' && orpLabel({ asalDarurat: true }) === 'kasir darurat' && orpLabel({}) === ORP_TANPA);
ok('ORP: tebakan jenis dari nama / aplikasi / id', orpJenis('Mac Owner') === 'komputer' && orpJenis('Web Owner') === 'komputer' && orpJenis('Tablet kasir') === 'tablet' && orpJenis('Iphone Owner') === 'hp'
  && orpJenis('d-abc') === 'darurat' && orpJenis('k-abc') === 'kasirLama' && orpJenis('x', { aplikasi: 'darurat' }) === 'darurat' && orpJenis('Perangkat X') === 'lain');
var OR = orpRingkas(KINI, 'bulan');
var notaDes = ambilPenjualan().filter(function (p) { return String(p.tanggal).slice(0, 7) === '2026-12'; }); var sumDes = notaDes.reduce(function (a, p) { return a + p.hargaTotal; }, 0);
ok('ORP: bulan ini — Σ per perangkat MENUTUP ke Σ nota bulan ini (nota batal tidak ikut), 4 nota unik (dua baris satu grup = 1 nota)', OR.total === sumDes && OR.baris.reduce(function (a, b) { return a + b.omzet; }, 0) === sumDes
  && sumDes === 3350000 && OR.nota === 4, J(OR.baris));
var tb = OR.baris.find(function (b) { return b.label === 'Tablet kasir'; }); var dr = OR.baris.find(function (b) { return b.label === 'kasir darurat'; });
ok('ORP: baris per perangkat — Tablet kasir 2 baris 1 nota 1.950.000 (sistem baru), kasir darurat dikenali, urut terbesar dulu', tb && tb.omzet === 1950000 && tb.nota === 1 && tb.baris === 2 && tb.aplikasi === 'sistem baru' && tb.jenis === 'tablet'
  && dr && dr.jenis === 'darurat' && OR.baris[0].label === 'Tablet kasir', J(OR.baris));
var OL = orpRingkas(KINI, 'lalu');
ok('ORP: bulan lalu — nota lama tanpa nama perangkat di baris "tidak tercatat" (paling bawah), perangkat bernama id dikenali dari denyut', OL.total === 700000 && OL.tanpa === 400000 && OL.baris[OL.baris.length - 1].tanpa
  && OL.baris.some(function (b) { return b.label === 'p-mvwl82s4-3s9sn' && b.aplikasi === 'sistem baru'; }), J(OL.baris));
ok('ORP: hari ini & pilihan tidak dikenal = bulan ini', orpRingkas(KINI, 'hari').total === 750000 && orpRingkas(KINI, 'x').pilih === 'bulan');

// ==================== JC · LOG (B81) ====================
var RH = jcRentangHari('2026-11-28');
ok('JC: rentang satu hari SETEMPAT (WIB) dalam UTC: 27 Nov 17.00Z – 28 Nov 17.00Z; tanggal rusak = null', RH && RH.dari === '2026-11-27T17:00:00.000Z' && RH.sampai === '2026-11-28T17:00:00.000Z' && jcRentangHari('28-11-2026') === null && jcRentangHari('2026-13-40') === null, J(RH));
var RC = jcRentangCadangan(KINI, 30);
ok('JC: rentang cadangan 30 hari — mulai 3 Nov 00.00 WIB, sampai 1 menit sesudah kini', RC.dari === '2026-11-02T17:00:00.000Z' && RC.sampai === new Date(KINI.getTime() + 60000).toISOString() && RC.hari === 30, J(RC));
var LOG = [{ id: 'l1', pada: '2026-11-28T02:00:00.000Z', aksi: 'tulis', koleksi: 'penjualan', idDok: '1', oleh: 'Owner', perangkat: 'Mac Owner', ringkas: 'Bu Sari 650.000' },
  { id: 'l2', pada: '2026-11-28T03:00:00.000Z', aksi: 'hapus', koleksi: 'batchMasuk', idDok: '1764000000001.5', oleh: 'Owner', perangkat: 'Mac Owner', ringkas: 'kedatangan' },
  { id: 'l3', pada: '2026-11-28T04:00:00.000Z', aksi: 'kirim', oleh: 'UJI B', olehUid: 'uid-uji-b', perangkat: 'Tablet kasir', dokumen: [{ koleksi: 'penjualan', id: '7' }, { koleksi: 'piutangMutasi', id: '8' }] }];
var NM = function (k) { return ({ penjualan: 'Nota', batchMasuk: 'Barang masuk', piutangMutasi: 'Buku bon' })[k] || k || 'catatan'; };
var JS = jcSaring(LOG, {}, NM);
ok('JC: semua — terbaru dulu, jejak kiriman staf = satu baris berisi daftar catatannya, hapus bertanda', JS.n === 3 && JS.tampil[0].id === 'l3' && /2 catatan: Nota, Buku bon/.test(JS.tampil[0].teks) && JS.tampil[0].koleksi === 'penjualan'
  && /^HAPUS · Barang masuk/.test(JS.tampil[1].teks) && JS.tampil[2].jam === '09.00' && JS.tampil[2].tanggal === '2026-11-28', J(JS.tampil));
ok('JC: saring orang · jenis catatan · kata (huruf besar/kecil sama, id catatan ikut)', jcSaring(LOG, { oleh: 'Owner' }, NM).n === 2 && jcSaring(LOG, { koleksi: 'batchMasuk' }, NM).n === 1 && jcSaring(LOG, { kata: 'bu sari' }, NM).n === 1
  && jcSaring(LOG, { kata: '1764000000001' }, NM).n === 1 && /1 dari 3 tulisan/.test(jcSaring(LOG, { kata: 'bu sari' }, NM).kalimat));
ok('JC: hitungan per orang & per jenis', J(JS.perOrang) === J([{ nama: 'Owner', n: 2 }, { nama: 'UJI B', n: 1 }]) && JS.perJenis.length === 2 && JS.perJenis[0].nama === 'Nota', J(JS.perJenis));
var BANYAK = []; for (var i = 0; i < JC_TAMPIL + 5; i++) BANYAK.push({ id: 'x' + i, pada: '2026-11-28T0' + (i % 9) + ':00:00.000Z', koleksi: 'penjualan', oleh: 'Owner' });
ok('JC: lebih dari batas tampil disebut (lebih), tidak dibuang diam-diam', jcSaring(BANYAK, {}, NM).tampil.length === JC_TAMPIL && jcSaring(BANYAK, {}, NM).lebih === 5);
var HB = LOG.slice(); HB.penuh = true;
ok('JC: kalimat baca — jumlah baca dari server; penuh = TERPOTONG; dari cache disebut', /3 tulisan dibaca dari server \(± 3 baca\) — TERPOTONG di 3000/.test(jcKalimatBaca(HB, 3000, 'Log')) && /simpanan perangkat/.test(jcKalimatBaca(Object.assign(LOG.slice(), { dariCache: true }), 3000, 'Log')));
var BK = { isi: { versi: 5, penjualan: [] }, dokumen: 10, nama: 'x.json' };
var BK2 = jcSertakanLog(BK, LOG, RC);
ok('JC: cadangan berkas membawa log 30 hari (isi.logAktivitas + logRentang), jumlah dokumen bertambah, berkas asal tidak diubah', BK2.isi.logAktivitas.length === 3 && BK2.dokumen === 13 && BK2.isi.logRentang.n === 3 && BK2.isi.logRentang.hari === 30
  && !BK.isi.logAktivitas && BK.dokumen === 10, J(BK2.isi.logRentang));
ok('JC: log tidak terbaca → berkas tetap jadi, gagalnya DISEBUT di berkas', jcSertakanLog(BK, null, RC, 'permission-denied').isi.logRentang.gagal === 'permission-denied' && jcSertakanLog(BK, null, RC).dokumen === 10);
var nLog0 = cacheMentah('log').length; isiDariCadangan({ logAktivitas: LOG, diunduhPada: '2026-12-02T07:00:00.000Z' }, 'uji'); setelSumber('cadangan', 'kotak pasir');
ok('JC: berkas cadangan yang membawa log dibaca lagi (isiDariCadangan → jejak pencatat)', nLog0 === 0 && cacheMentah('log').length === 3, cacheMentah('log').length);

// ==================== DPB · TAUTAN BEKU DASBOR (B103) ====================
ok('DPB: bawaan = omzet & nota · kg · laba kotor; hari bawaan 7; pilihan 1/7/30/90', J(dpbBagianBawaan()) === J(['omzet', 'kg', 'laba']) && DPB_HARI_BAWAAN === 7 && J(DPB_HARI) === J([1, 7, 30, 90]));
ok('DPB: pilihan tidak sah DITOLAK — tanpa bagian, hari lain (5 / 365), catatan > 40 huruf; bagian asing dibuang', !!dpbPilihSah({ bagian: [], hari: 7 }).tolak && !!dpbPilihSah({ bagian: ['omzet'], hari: 5 }).tolak
  && !!dpbPilihSah({ bagian: ['omzet'], hari: 365 }).tolak && !!dpbPilihSah({ bagian: ['omzet'], hari: 7, untuk: 'x'.repeat(41) }).tolak && J(dpbPilihSah({ bagian: ['omzet', 'rahasia'], hari: 7 }).bagian) === J(['omzet']));
var urutan = function (arr) { var i = 0; return function (n) { var b = new Uint8Array(n); for (var j = 0; j < n; j++) { b[j] = arr[i % arr.length]; i++; } return b; }; };
var D1 = dpbSusunBuat({ bagian: ['omzet', 'kg', 'laba'], hari: 7, untuk: '  Bank  Contoh ' }, KINI, W, urutan([1, 2, 3, 4, 5, 61]));
var d1 = D1.dokumen && D1.dokumen[0].data;
ok('DPB: buat = satu dokumen dasborPublik/<kode 22 huruf>, sampai = kini + 7 hari (jam), catatan dirapikan', D1.dokumen && D1.dokumen[0].koleksi === 'dasborPublik' && /^[A-Za-z0-9]{22}$/.test(d1.id) && d1.id === D1.kode
  && d1.sampai instanceof Date && d1.sampai.getTime() === KINI.getTime() + 7 * 86400000 && d1.hari === 7 && d1.untuk === 'Bank Contoh' && d1.dibuat === W.kini, J(d1).slice(0, 300));
var D30 = dpbSusunBuat({ bagian: ['kas'], hari: 30 }, KINI, W, urutan([7, 8, 9]));
ok('DPB: berlaku 30 hari = sampai kini + 30 hari (pilihan owner, bukan bawaan)', D30.dokumen && D30.dokumen[0].data.sampai.getTime() === KINI.getTime() + 30 * 86400000 && D30.dokumen[0].data.hari === 30 && /berlaku 30 hari/.test(D30.patch.kabar));
ok('DPB: HANYA bagian dicentang yang ikut — tanpa stok / piutang / utang / kas / laba bersih', d1.bulan && d1.bulan.length === DPB_BULAN && !('stok' in d1) && !('piutang' in d1) && !('utangPemasok' in d1) && !('kas' in d1)
  && d1.bulan.every(function (b) { return !('labaBersih' in b); }) && J(d1.bagian) === J(['omzet', 'kg', 'laba']));
ok('DPB: isinya angka saja — tanpa nama pelanggan / pemasok / perangkat', J(d1).indexOf('Bu Sari') < 0 && J(d1).indexOf('Pemasok') < 0 && J(d1).indexOf('Mac Owner') < 0 && J(d1).indexOf('Tablet') < 0);
var b0 = d1.bulan[0]; var R0 = lpRekapRentang('2026-12-01', '2026-12-02'); var K0b = klKgBulan('2026-12', KINI); var M0 = klMarginBulan('2026-12', KINI);
ok('DPB: angka bulan ini = fungsi sumber (lpRekapRentang · klKgBulan · klMarginBulan) apa adanya', b0.key === '2026-12' && b0.berjalan && b0.sampaiTanggal === '2026-12-02' && b0.omzet === Math.round(R0.omzet) && b0.nota === R0.n
  && b0.kg === Math.round(K0b.kg * 10) / 10 && b0.labaKotor === Math.round(M0.labaKotor) && b0.marginPct === Math.round(M0.tangga[0].pct * 10) / 10, J([b0, R0.omzet, R0.n, K0b.kg, M0.labaKotor]));
var IS = dpbIsi(['bersih', 'stok', 'piutang', 'utang', 'kas'], KINI); var N0 = neracaPada(null, KINI).N; var SK = saldoKantong();
ok('DPB: posisi = neraca (stok nilai · piutang · utang pemasok), kas = saldoKantong; laba bersih = klMarginBulan', IS.stok && IS.stok.nilai === Math.round(N0.stok) && IS.piutang === Math.round(N0.piutang) && IS.utangPemasok === Math.round(N0.utangPemasok)
  && IS.kas && IS.kas.ada === !!SK.ada && IS.bulan[0].labaBersih === Math.round(M0.labaBersih) && !('omzet' in IS.bulan[0]), J(IS).slice(0, 400));
ok('DPB: jam sampai terbaca dari Timestamp / {seconds} / ISO / Date', dpbMs({ toMillis: function () { return 5; } }) === 5 && dpbMs({ seconds: 2, nanoseconds: 5e6 }) === 2005 && dpbMs('2026-12-09T07:00:00.000Z') === Date.parse('2026-12-09T07:00:00.000Z')
  && dpbMs(new Date(7)) === 7 && isNaN(dpbMs(null)) && isNaN(dpbMs('bukan')));
terapkanKeCache(D1.dokumen);
terapkanKeCache([{ koleksi: 'dasborPublik', data: { id: 'L'.repeat(22), untuk: 'lama', dibuat: '2026-11-01T00:00:00.000Z', sampai: { seconds: Math.floor(KINI.getTime() / 1000) - 60 }, hari: 1, bagian: ['omzet'] } },
  { koleksi: 'dasborPublik', data: { id: 'S'.repeat(22), untuk: 'sebentar', dibuat: W.kini, sampai: new Date(KINI.getTime() + 86400000 - 1), hari: 1, bagian: ['kas'] } }]);
var SM = dpbSemua(KINI);
ok('DPB: daftar — aktif dulu (yang paling cepat habis dulu), lalu yang lewat; sisa hari dibulatkan ke atas', SM.length === 3 && SM[0].kode === 'S'.repeat(22) && SM[0].sisaHari === 1 && SM[1].kode === D1.kode && SM[1].sisaHari === 7 && !SM[2].aktif && SM[2].sisaHari === 0
  && J(SM[1].bagian) === J(['Omzet & jumlah nota', 'Kg beras terjual', 'Laba kotor & margin']), J(SM.map(function (x) { return [x.kode.slice(0, 2), x.aktif, x.sisaHari]; })));
var CB = dpbSusunCabut(D1.kode);
ok('DPB: cabut = hapus dokumennya (tanpa tulis); yang tidak ada ditolak', J(CB.hapus) === J([{ koleksi: 'dasborPublik', id: D1.kode }]) && CB.dokumen.length === 0 && /untuk Bank Contoh DICABUT/.test(CB.patch.kabar) && !!dpbSusunCabut('X'.repeat(22)).tolak);
var BS = dpbSusunBersihkan(KINI);
ok('DPB: bersihkan = hapus HANYA yang sudah lewat', BS.hapus && BS.hapus.length === 1 && BS.hapus[0].id === 'L'.repeat(22));
ok('DPB: tautan = folder /baru/ + dasbor-publik.html#k=<kode>; proyek lain disebut', dpbTautan('KODE', 'https://x.y/baru/') === 'https://x.y/baru/dasbor-publik.html#k=KODE' && dpbTautan('KODE', 'https://x.y/baru/', 'contoh-toko-beras') === 'https://x.y/baru/dasbor-publik.html#k=KODE&p=contoh-toko-beras');
ok('DPB: pesan WhatsApp — tautan, berlaku sampai, jangan disebarkan', /https:\/\/x\.y\/baru\/dasbor-publik\.html#k=KODE/.test(dpbPesanWa('Bank', 'https://x.y/baru/dasbor-publik.html#k=KODE', KINI.getTime())) && /Berlaku sampai 2 Des 2026 14\.00/.test(dpbPesanWa('', 'u', KINI.getTime())) && /tidak disebarkan/.test(dpbPesanWa('', 'u', 0)));
var PR = dpbPratinjau(['omzet', 'kas'], KINI);
ok('DPB: kg berpemisah ribuan (18.198,3 kg), kosong = —', dpbKgTeks(18198.34) === '18.198,3 kg' && dpbKgTeks(5) === '5 kg' && dpbKgTeks(null) === '—');
ok('DPB: pratinjau sebelum dibuat = angka yang akan dibekukan (bagian dicentang saja)', PR.baris.length === 2 && /^Omzet Desember 2026/.test(PR.baris[0][0]) && PR.baris[1][0] === 'Kas & rekening', J(PR.baris));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
})();
"""

ASAP = r"""
(function () {
var out = { galat: [] }; var kini = new Date(__KINI);
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); }); setelSumber('cadangan', 'asap');
__dom['jualKarungBerat'] = { value: '50' };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + (e && e.message)); return null; } };
var BL = aman('afBelum', function () { return afBelum(kini); }); out.belum = BL ? { kedatangan: BL.kedatangan, belum: BL.belum.length, tunai: BL.nTunai, bon: BL.nBon, kas: BL.kas.length, catatanLama: !!BL.catatanLama } : null;
var BU = aman('afBulan', function () { return afBulan(kini, 6); }); out.bulan = BU ? BU.map(function (b) { return [b.key, b.kedatangan, b.foto]; }) : null;
var OR = aman('orp', function () { return orpRingkas(kini, 'bulan'); }); var OL = aman('orp lalu', function () { return orpRingkas(kini, 'lalu'); });
var sum = function (key) { return Math.round(ambilPenjualan().filter(function (p) { return String(p.tanggal || '').slice(0, 7) === key; }).reduce(function (a, p) { return a + (Number(p.hargaTotal) || 0); }, 0)); };
var key = kini.toISOString().slice(0, 7); var keyL = new Date(Date.UTC(kini.getFullYear(), kini.getMonth() - 1, 1)).toISOString().slice(0, 7);
out.orp = OR && OL ? { menutupBulan: OR.total === sum(hariIniIso(kini).slice(0, 7)), menutupLalu: OL.total === sum(keyL), perangkatBulan: OR.baris.length, perangkatLalu: OL.baris.length,
  jenis: OR.perJenis.map(function (j) { return j.jenis + ':' + j.n; }), bagianTanpaNama: OL.tanpa > 0 } : null;
var IS = aman('dpbIsi', function () { return dpbIsi(DPB_BAGIAN.map(function (b) { return b[0]; }), kini); });
var b0 = IS && IS.bulan ? IS.bulan[0] : null; var R0 = b0 ? aman('rekap', function () { return lpRekapRentang(b0.key + '-01', b0.sampaiTanggal); }) : null;
out.dpb = IS ? { bulan: IS.bulan.length, galatBulan: IS.bulan.filter(function (b) { return b.omzetGalat || b.kgGalat || b.labaGalat || b.bersihGalat; }).map(function (b) { return b.key; }),
  omzetSama: !!(b0 && R0 && b0.omzet === Math.round(R0.omzet) && b0.nota === R0.n), stok: !!(IS.stok && IS.stok.nilai !== null && IS.stok.kg !== null), piutang: IS.piutang !== null, utang: IS.utangPemasok !== null, kas: !!(IS.kas && IS.kas.ada),
  tanpaNama: JSON.stringify(IS).indexOf('pemasok') < 0 && JSON.stringify(IS).indexOf('namaPelanggan') < 0 } : null;
var BK = aman('cadangan', function () { return jcSertakanLog({ isi: { versi: 5, penjualan: ambilPenjualanSemua() }, dokumen: ambilPenjualanSemua().length }, [], jcRentangCadangan(kini, 30)); }); out.cadanganLog = !!(BK && BK.isi && Array.isArray(BK.isi.logAktivitas) && BK.isi.logRentang.hari === 30);
print(JSON.stringify(out));
})();
"""

RUSAK = [
    ('foto: kedatangan tunai dianggap bon', AF, "if (b) return batchDiutang(b) ? 'bon' : 'tunai';", "if (b) return 'bon';"),
    ('foto: stok awal ikut dihitung kedatangan', AF, "export const afKedatanganNyata = (b) => !!b && !b.stokAwal && ", "export const afKedatanganNyata = (b) => !!b && "),
    ('foto: tanda membawa kolom foto (gambar)', AF, "  Object.keys(t).forEach((k) => { if (AF_TANDA_KOLOM.indexOf(k) < 0) delete t[k]; });\n", "  t.base64 = String(foto.base64 || '');\n"),
    ('foto: nota kas kecil yang sudah berfoto tetap dihitung', AF, " && !(Array.isArray(h.fotoNota) && h.fotoNota.length))", ")"),
    ('foto: kedatangan bertanda tetap dihitung belum', AF, "const belum = semua.filter((x) => !x.nFoto);", "const belum = semua.slice();"),
    ('foto: tanda kurang menulis ulang yang sudah ada', AF, "filter((f) => f && f.id !== undefined && !ada[String(f.id)])", "filter((f) => f && f.id !== undefined)"),
    ('foto: berkas arsip tanpa escape nama', AF, ".replace(/&/g, '&amp;').replace(/</g, '&lt;')", ".replace(/&/g, '&amp;').replace(/@@@/g, '&lt;')"),
    ('omzet: nota batal ikut dijumlah', ORP, "const nota = ambilPenjualan().filter(", "const nota = ambilPenjualanSemua().filter("),
    ('omzet: dua baris satu nota dihitung dua nota', ORP, "const orpKunciNota = (p) => String(p.grupNota || p.trxId || p.id);", "const orpKunciNota = (p) => String(p.id);"),
    ('omzet: tablet ditebak HP', ORP, "if (/tablet|cpad|sunmi|\\bpad\\b|ipad/i.test(L)) return 'tablet';", "if (/tablet|cpad|sunmi|\\bpad\\b|ipad/i.test(L)) return 'hp';"),
    ('log: hari dihitung UTC, bukan WIB', JC, "return { dari: new Date(y, m - 1, d, 0, 0, 0, 0).toISOString(), sampai: new Date(y, m - 1, d + 1, 0, 0, 0, 0).toISOString()", "return { dari: new Date(Date.UTC(y, m - 1, d)).toISOString(), sampai: new Date(Date.UTC(y, m - 1, d + 1)).toISOString()"),
    ('log: saringan orang diabaikan', JC, "const cocok = semua.filter((l) => (!s.oleh || l.oleh === s.oleh) && ", "const cocok = semua.filter((l) => "),
    ('log: cadangan tanpa log tidak menyebut gagalnya', JC, "  else isi.logRentang = { gagal: String(galat || 'log tidak terbaca'), n: 0 };\n", ""),
    ('log: terpotong tidak disebut', JC, "+ (hasil && hasil.penuh ? ' — TERPOTONG di ' + maks + ' tulisan (sisanya tidak dibaca)' : '')", ""),
    ('tautan: bagian yang tidak dicentang ikut', DPB, "const pakai = (id) => B.indexOf(id) >= 0;", "const pakai = (id) => true;"),
    ('tautan: hari bebas (365 diterima)', DPB, "if (DPB_HARI.indexOf(hari) < 0) return {", "if (!(hari > 0)) return {"),
    ('tautan: sampai dihitung dari hari bawaan, bukan pilihan', DPB, "const sampai = new Date(kini.getTime() + P.hari * 86400000);", "const sampai = new Date(kini.getTime() + DPB_HARI_BAWAAN * 86400000);"),
    ('tautan: yang sudah lewat dianggap aktif', DPB, "const aktif = isFinite(ms) && ms > t;", "const aktif = isFinite(ms);"),
    ('tautan: bersihkan menghapus yang masih aktif', DPB, "const lewat = dpbSemua(kini).filter((x) => !x.aktif);", "const lewat = dpbSemua(kini);"),
    ('akses: tanda foto berkolom asing diterima', AK, "if (Object.keys(d).some((k) => TANDA_FOTO_KOLOM.indexOf(k) < 0)) return false;\n  return typeof d.idBon", "\n  return typeof d.idBon"),
    ('akses: karyawan boleh memotret nota', AK, "export const FOTO_STAF = ['ben'];", "export const FOTO_STAF = ['ben', 'karyawan'];"),
    ('akses: foto nota kas kecil dari tablet diterima', AK, "return ID_KEDATANGAN_SAH.test(String(d.idBon || '')) && typeof d.idBon === 'string' && ", "return typeof d.idBon === 'string' && "),
]
STATIS = [
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_arsip_audit_p8.py && python3 alat-uji/uji_arsip_audit_p8.py --kontrol']),
    ('BACA-DULU menyebut paket P8', 'baca', ['Paket P8', 'fotoTanda', 'dasborPublik', 'dasbor-publik.html', 'rules v26', 'arsip-foto-logika', 'omzet-perangkat-logika', 'jejak-cari-logika', 'dasbor-publik-logika']),
    ('dasbor-publik.html: CSP ketat (skrip asal sendiri, sambungan hanya Firestore, tanpa base/form), tanpa skrip sebaris, noindex & no-referrer', 'html',
     ["content=\"default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src https://firestore.googleapis.com; base-uri 'none'; form-action 'none'\"",
      '<script src="js/dasbor-publik-halaman.js"></script>', '<meta name="robots" content="noindex, nofollow">', '<meta name="referrer" content="no-referrer">']),
    ('halaman tamu: kode dari # (tidak ke server), satu GET tanpa kredensial, 403/404 = tidak berlaku, dokumen dasborPublik', 'hal',
     ["String(location.hash || '')", "credentials: 'omit'", "if (r.status === 403 || r.status === 404) { pesan('Tautan tidak berlaku'", "/documents/dasborPublik/' + encodeURIComponent(H.kode)", "'timestampValue' in v"]),
    ('penulis pusat: dasborPublik ditulis APA ADANYA (tanpa nama / uid / perangkat penulis)', 'fb', ["if (x.koleksi === 'dasborPublik') { b.set(doc(db, x.koleksi, String(x.data.id)), x.data);"]),
    ('penulis pusat: foto + tanda SATU kiriman; Penjaga laci dijaga bentuknya & satu baris jejak kiriman; tanda ikut terhapus; baca log & foto bulan owner saja', 'fb',
     ["b.set(doc(db, KOLEKSI_FOTO_BON, String(d.id)), d); if (t) b.set(doc(db, KOLEKSI_TANDA_FOTO, String(t.id)), t);", "if (!owner0 && (!fotoNotaSah(d) || (t && !tandaFotoSah(t))))",
      "if (!owner0 && !bolehFotoNota(akun0))", "b.delete(doc(db, KOLEKSI_TANDA_FOTO, String(id)));", "export async function bacaLog(saring, batas) {\n  if (!db) throw new Error('belum tersambung');\n  if (pemilikSaja()) throw new Error(pemilikSaja());",
      "export async function bacaFotoBulan(key) {\n  if (!db) throw new Error('belum tersambung');\n  if (pemilikSaja()) throw new Error(pemilikSaja());"]),
    ('rules v26: fotoBon create + stafFotoNota, blok fotoTanda & dasborPublik (get selama belum lewat, tulis ≤ 91 hari)', 'rules',
     ["allow create: if (owner() || stafFotoNota(['ben'])) && request.resource.data.get('id', '') == id", "match /fotoTanda/{id} {\n      allow read: if owner();\n      allow create: if owner() || stafTandaFoto(['ben'], id);",
      "allow get: if kode.size() >= 20 && resource.data.sampai > request.time;", "request.resource.data.sampai <= request.time + duration.value(91, 'd');"]),
    ('koleksi.js: fotoTanda & dasborPublik didengar penuh (owner)', 'koleksi', ["{ nama: 'fotoTanda',           urut: 'id',    cache: 'fotoTanda', kelas: 'tetap' },", "{ nama: 'dasborPublik',        urut: 'id',    cache: 'dasborPublik', kelas: 'tetap' },"]),
    ('app.js: foto Stok tersambung, tanda ikut di foto bon & nota kas kecil, menu membaca log & foto bulan', 'app',
     ["simpan: (d, t) => fb.simpanFotoBon(d, t)", "bacaLog: (saring, batas) => fb.bacaLog(saring, batas), bacaFotoBulan: (key) => fb.bacaFotoBulan(key)", "stok.buka(t.lembar || null, t.tab || null, t.isi || null);"]),
    ('Stok: kartu foto nota di Barang masuk (owner: koreksi & sesudah simpan · tablet: sesudah simpan), aksi tersambung, buka koreksi dari Arsip foto', 'stok',
     ["${kartuFotoNota(koreksi ? d.id : s.tbm ? s.tbm.id : null, { s, akun: opsi.akun ? opsi.akun() : null })}", "${s.tbm ? kartuFotoNota(s.tbm.id, { s, akun: ak }) : ''}",
      "Object.assign(AKSI, aksiPanelFotoNota({ set, st, akun: opsi.akun, waktu, foto: opsi.foto || null, akar }));", "if (isi && isi.koreksi) AKSI.mKoreksi({ id: String(isi.koreksi) });"]),
    ('Menu: tab Arsip foto & Tautan Dasbor, omzet per perangkat, cari log, cadangan + log 30 hari', 'menu',
     ["cadangan: [['berkas', 'Cadangan'], ['foto', 'Arsip foto'], ['tautan', 'Tautan Dasbor']]", "if (tab === 'foto') return gambarArsipFoto(", "if (tab === 'tautan') return gambarTautanDasbor(",
      "${kartuOmzetPerangkat(s, d)}", "${kartuCariLog(s, d, opsi.akun ? opsi.akun() : null, S.ssNamaKoleksi)}", "const b = await aaSertakanLog(S.ssBerkasCadangan(", "Object.assign(AKSI, aksiPanelArsipAudit({"]),
    ('Dasbor: baris belum berfoto di Mutu, tombol Bagikan → Tautan Dasbor', 'dasbor', ["const FT = Q.foto;", "'Nota & bon belum berfoto'"]),
    ('Dasbor: tombol Bagikan', 'kisi', ['data-da-aksi="bagikan"', "if (x === 'bagikan') { if (opsi.keTujuan) opsi.keTujuan({ ke: 'sistem', sistem: 'cadangan', tab: 'tautan' });"]),
    ('dasbor-logika: Mutu memuat afBelum apa adanya', 'dl', ["foto: aman(() => afBelum(kini)),"]),
    ('index.html memuat modul baru lebih dulu', 'index', ['<link rel="modulepreload" href="js/layar/arsip-foto-logika.js">', '<link rel="modulepreload" href="js/layar/omzet-perangkat-logika.js">', '<link rel="modulepreload" href="js/layar/jejak-cari-logika.js">',
      '<link rel="modulepreload" href="js/layar/dasbor-publik-logika.js">', '<link rel="modulepreload" href="js/layar/foto-nota-panel.js">', '<link rel="modulepreload" href="js/layar/arsip-audit-panel.js">']),
    ('akses.js: Penjaga laci membuat tanda foto (BUAT_STAF) & penjaga kiriman tanda', 'ak', ["fotoTanda: ['ben'],", "if (x.koleksi === 'fotoTanda' && !tandaFotoSah(d))"]),
    ('bundel uji: arsip-foto ikut otomatis bila Dasbor dibundel', 'bundel', ["AF_MODUL = 'baru/js/layar/arsip-foto-logika.js'", "AF_PEMAKAI = ('dasbor-logika.js'"]),
    ('peta_akses: kiriman tanda foto Penjaga laci diukur', 'peta', ["catat('tanda foto nota'"]),
    ('CSS: kisi foto nota (Stok) & batang omzet per perangkat (Menu, bergerak)', 'css_stok', ['.layar-stok .fn-kisi', '.layar-stok .fn-besar']),
    ('CSS menu: batang omzet tumbuh, hormati kurangi gerak', 'css_menu', ['.layar-menu .aa-batang i', '@keyframes aa-tumbuh', 'prefers-reduced-motion: reduce) { .layar-menu .aa-batang i']),
]
RUSAK_STATIS = [
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_arsip_audit_p8.py', 'true'),
    ('halaman tamu boleh menyambung ke mana saja', 'html', 'connect-src https://firestore.googleapis.com;', 'connect-src *;'),
    ('penulis pusat menempelkan atribusi ke dasborPublik', 'fb', "if (x.koleksi === 'dasborPublik') {", "if (x.koleksi === 'dasborPublikX') {"),
    ('foto staf dikirim tanpa penjaga bentuk', 'fb', "if (!owner0 && (!fotoNotaSah(d) || (t && !tandaFotoSah(t))))", "if (false)"),
    ('hapus foto meninggalkan tandanya', 'fb', "b.delete(doc(db, KOLEKSI_TANDA_FOTO, String(id)));", ""),
    ('halaman tamu menyimpan ke localStorage', 'hal', "window.addEventListener('hashchange'", "localStorage.setItem('k', 1); window.addEventListener('hashchange'"),
    ('tautan Dasbor kedaluwarsa hanya di halaman (rules tanpa jam)', 'rules', "allow get: if kode.size() >= 20 && resource.data.sampai > request.time;", "allow get: if kode.size() >= 20;"),
]


def bundel_js(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    js = uji_kunci_periode.satu_lingkup(js)
    if js.count(uji_dasbor_sensus.BON_PEMASOK_LAMA) == 1: js = js.replace(uji_dasbor_sensus.BON_PEMASOK_LAMA, uji_dasbor_sensus.BON_PEMASOK_LAMA.replace('susunBon(', 'bpSusunBon('))
    return js


def jalan(teks):
    jam = "var __KINI = new Date('2026-12-02T14:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    r, out = uji_dasbor_sensus.jsc(jam + bundel_js(teks) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], list(h['gagal'])


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:140])
    for terlarang in ('localStorage', 'sessionStorage', 'indexedDB', 'document.cookie', 'innerHTML', 'eval(', 'http://'):
        if terlarang in src['hal']: g.append('halaman tamu memakai ' + terlarang)
    if '<script>' in src['html'] or 'onclick' in src['html'].lower() or 'href="http' in src['html']: g.append('dasbor-publik.html: skrip sebaris / penangan sebaris / tautan keluar')
    # modul logika tanpa DOM; omzet per perangkat & cari log BACA SAJA; tautan & foto hanya penyusun yang tercatat
    for k in ('af', 'orp', 'jc', 'dpb'):
        if 'document.' in src[k] or 'window.' in src[k] or 'tulisDokumen' in src[k] or 'localStorage' in src[k]: g.append(k + ': modul logika menyentuh DOM / menulis langsung')
    for k in ('orp', 'jc'):
        if re.search(r"dokumen: \[\{|\{ koleksi: '", src[k]): g.append(k + ': modul baca-saja menyusun dokumen')
    for k, boleh in (('af', {'afSusunTandaKurang'}), ('dpb', {'dpbSusunBuat', 'dpbSusunCabut', 'dpbSusunBersihkan'})):
        pintu = re.findall(r'export function (\w+)\([^)]*\) \{[^\n]*\n(?:(?!export function).)*?(?:dokumen: |hapus: \[)', src[k], re.S)
        if set(pintu) - boleh: g.append(k + ': pintu tulis di luar yang tercatat: ' + ', '.join(sorted(set(pintu) - boleh)))
    for k in ('af', 'orp', 'jc', 'dpb', 'panel', 'fnp', 'menu', 'stok', 'dasbor', 'kisi', 'dl', 'app', 'ak'):
        for n, baris in enumerate(src[k].split('\n')):
            ekor = uji_sisa_sensus.komentar_ekor(baris)
            if ekor and re.search(r"\b[a-zA-Z]\w*: (opsi\.|\(|async |\[|\{|'|`)|;\s*(const|let|return|if|export)\b|\)\s*=>", ekor): g.append(k + ':' + str(n + 1) + ': komentar // menelan kode → ' + ekor.strip()[:90])
    return len(STATIS) - len([x for x in g if ' → tidak ketemu' in x]), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read() if os.path.exists(os.path.join(AKAR, v)) else '') for k, v in SUMBER.items())


if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama + ' (' + str(teks[berkas].count(a)) + '×)'); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b); l, g = jalan(T)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_STATIS:
            if src[berkas].count(a) < 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            S = dict(src); S[berkas] = S[berkas].replace(a, b, 1); l, g = statis(S)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        print('KONTROL %s: %d kerusakan' % ('LULUS' if kode == 0 else 'GAGAL', len(RUSAK) + len(RUSAK_STATIS)))
        sys.exit(kode)
    l, g = jalan(teks); ls, gs = statis(src)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '..', '..', '..', '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and '--tanpa-asap' not in sys.argv:
        tgl = os.path.basename(cad[-1]).split('miqbal-')[-1][:10]
        r, out = uji_dasbor_sensus.jsc("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + bundel_js(teks) + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if r.returncode != 0 or not out.startswith('{'): print('ASAP DATA TOKO: JSC JATUH ' + (r.stderr or r.stdout)[-600:]); g.append('asap')
        else:
            h = json.loads(out)
            beres = (not h['galat'] and h['belum'] is not None and h['bulan'] is not None and h['orp'] and h['orp']['menutupBulan'] and h['orp']['menutupLalu'] and h['dpb'] and h['dpb']['omzetSama']
                     and not h['dpb']['galatBulan'] and h['dpb']['tanpaNama'] and h['cadanganLog'])
            # angka RUPIAH toko TIDAK dicetak (repo publik) — hanya keadaan & jumlah kedatangan / foto / perangkat
            print('ASAP DATA TOKO (%s): %s — %s' % (os.path.basename(cad[-1]), 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: hitungan foto / omzet per perangkat / tautan Dasbor tidak menutup atau galat')
    sys.exit(1 if g or gs else 0)
