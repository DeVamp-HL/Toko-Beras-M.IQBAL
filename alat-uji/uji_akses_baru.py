#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_akses_baru.py — putaran 23 (akun per orang): logika akses sistem baru di jsc, jam dikunci seperti uji lain.
KOTAK PASIR (akun, uid, nama CONTOH — bukan orang toko). Menguji:
  · baru/js/data/akses.js      — keadaan akun (owner lewat EMAIL saja), pendengar/layar/tombol per peran, penjaga kiriman bukan-owner,
                                 atribusi (olehUid), SATU baris jejak per kiriman yang memuat daftar dokumennya;
  · baru/js/data/antre-lokal.js — salinan antre: tahan muat ulang, berbatas, dihapus hanya sesudah server mengaku, yang ditolak ditandai;
  · sistem-logika.js SS2       — daftarkan / tolak / ubah akun (tak pernah owner, dua ketukan);
  · sambungan di firebase.js   — tidak bisa dijalankan di jsc (impor URL Firebase), jadi SUMBERNYA diperiksa: penjaga sebelum kirim,
                                 salinan antre sebelum commit, dihapus hanya di .then, jejak per kiriman bukan-owner, owner via email.
Dasar: docs/peta-hak-akses.md.

    python3 alat-uji/uji_akses_baru.py            → N lulus · 0 gagal
    python3 alat-uji/uji_akses_baru.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/data/akses.js', 'baru/js/data/antre-lokal.js', 'baru/js/layar/pelanggan-logika.js', 'baru/js/layar/bon-logika.js',
                                  'baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/sistem-logika.js']
JAM = ("var __RealDate = Date; var __KINI = new __RealDate('2026-09-24T10:00:00+07:00').getTime();\n"
       "Date = function (a, b, c, d, e, f, g) { if (!(this instanceof Date)) return new __RealDate(__KINI).toString(); if (arguments.length === 0) return new __RealDate(__KINI); if (arguments.length === 1) return new __RealDate(a); return new __RealDate(a, b, c === undefined ? 1 : c, d || 0, e || 0, f || 0, g || 0); };\n"
       "Date.prototype = __RealDate.prototype; Date.now = function () { return __KINI; }; Date.UTC = __RealDate.UTC; Date.parse = __RealDate.parse;\n")

SKENARIO = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
var W = { tanggal: '2026-09-24', jam: '10:00', kini: '2026-09-24T03:00:00.000Z', idUnik: (function () { var n = 7000; return function () { n += 1; return n; }; })() };
var OWN = keadaanAkun('Owner@TokoBerasMiqbal.web.app', 'uid-owner', null);
var BEN = keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true });
var KRY = keadaanAkun('kry.contoh@tokoberasmiqbal.web.app', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true });
var HAK_BEN = { jualTunai: 'sendiri', jualBon: 'sendiri', nego: 'owner', terimaBon: 'sendiri', hitungLaci: 'sendiri', uangKeluar: 'owner', adukan: 'sendiri', kedatangan: 'sendiri', hargaBeli: 'tidak', koreksi: 'owner', hapus: 'tidak', pelangganBaru: 'sendiri', atur: 'tidak' };
var HAK_KRY = { jualTunai: 'sendiri', jualBon: 'owner', nego: 'tidak', terimaBon: 'sendiri', hitungLaci: 'tidak', uangKeluar: 'tidak', adukan: 'sendiri', kedatangan: 'sendiri', hargaBeli: 'tidak', koreksi: 'tidak', hapus: 'tidak', pelangganBaru: 'sendiri', atur: 'tidak' };

// ---- 1 · keadaan akun: owner HANYA lewat email; aksesAkun tidak pernah memberi owner
var PALSU = keadaanAkun('nakal.contoh@tokoberasmiqbal.web.app', 'uid-x', { uid: 'uid-x', nama: 'Nakal', peran: 'owner', aktif: true });
ok('akun: email owner (huruf besar-kecil apa saja) = owner walau tanpa aksesAkun; dokumen aksesAkun berperan "owner" TIDAK memberi owner (jadi nonaktif, kalimatnya jujur)',
  OWN.jenis === 'owner' && OWN.nama === 'Owner' && OWN.peran === 'owner' && PALSU.jenis === 'nonaktif' && PALSU.peran === null && /tidak dikenal/.test(PALSU.kalimat), JSON.stringify([OWN, PALSU]));
var BLM = keadaanAkun('baru.contoh@tokoberasmiqbal.web.app', 'uid-baru', null); var NON = keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { peran: 'ben', aktif: false, nama: 'Ben Contoh' });
var KAS = keadaanAkun('kasir@tokoberasmiqbal.web.app', 'uid-kasir', null); var KLR = keadaanAkun('', '', null);
ok('akun: tanpa aksesAkun = "belum didaftarkan owner"; aktif:false = "dinonaktifkan owner"; kasir@ = akun kasir darurat (tidak bisa minta didaftarkan); keluar = tanpa uid; aktif = peran & nama dari dokumen',
  BLM.jenis === 'belum' && BLM.kalimat === 'Akun ini belum didaftarkan owner' && NON.jenis === 'nonaktif' && NON.kalimat === 'Akun ini dinonaktifkan owner' && KAS.jenis === 'kasir' && KLR.jenis === 'keluar'
  && BEN.jenis === 'aktif' && BEN.peran === 'ben' && BEN.nama === 'Ben Contoh' && KRY.peran === 'karyawan' && bisaBekerja(BEN) && bisaBekerja(OWN) && !bisaBekerja(BLM) && !bisaBekerja(NON) && !bisaBekerja(KAS));
ok('akun: yang belum terdaftar, nonaktif, kasir@, keluar = NOL pendengar koleksi toko', pendengarPeran(BLM).length === 0 && pendengarPeran(NON).length === 0 && pendengarPeran(KAS).length === 0 && pendengarPeran(KLR).length === 0);

// ---- 2 · pendengar & layar per peran (peta §3)
var PO = pendengarPeran(OWN).map(function (p) { return p.nama; }); var PK = pendengarPeran(KRY); var PKn = PK.map(function (p) { return p.nama; });
var UANG = ['pengeluaranHarian', 'modalOwner', 'amplopLaba', 'setoranKas', 'tutupHari', 'pindahUang', 'kasbonMutasi', 'biayaBulanan', 'slipUpah', 'absenKaryawan', 'utangOwnerMutasi', 'utangPemasokMutasi', 'pemasokCatatan', 'koreksiHpp', 'thrPelanggan', 'logAktivitas', 'cadanganCatatan', 'aksesAkun', 'permintaanAkses'];
ok('pendengar: owner = SEMUA koleksi.js (' + KOLEKSI.length + '); karyawan = daftar peta §3 — nol koleksi uang/HPP/THR/jejak/akun; aturanToko & pengaturan PER DOKUMEN (tanpa upah, identitas, hpp, titikKas, keamanan)',
  PO.length === KOLEKSI.length && PKn.length === BACA_STAF.length + 2 && !PKn.some(function (n) { return UANG.indexOf(n) >= 0; })
  && PK.filter(function (p) { return p.dok; }).length === 2 && PK.find(function (p) { return p.nama === 'aturanToko'; }).dok.indexOf('upah') < 0 && PK.find(function (p) { return p.nama === 'aturanToko'; }).dok.indexOf('hpp') < 0
  && PK.find(function (p) { return p.nama === 'pengaturan'; }).dok.join() === 'tempatSimpan' && PK.find(function (p) { return p.nama === 'aturanToko'; }).dok.indexOf('peran') >= 0, JSON.stringify(PKn));
ok('layar: karyawan & Ben hanya Jual, Pelanggan, Stok, Menu — layar Uang/Ringkasan/Harga/Laporan tertutup; owner semua; akun belum terdaftar tidak membuka layar apa pun',
  bolehLayar(KRY, 'jual') && bolehLayar(BEN, 'pelanggan') && bolehLayar(KRY, 'stok') && bolehLayar(KRY, 'menu') && !bolehLayar(KRY, 'uang') && !bolehLayar(BEN, 'ringkasan') && !bolehLayar(BEN, 'harga') && !bolehLayar(KRY, 'laporan')
  && bolehLayar(OWN, 'uang') && bolehLayar(OWN, 'laporan') && !bolehLayar(BLM, 'jual'));
ok('angka dari koleksi yang tidak didengarkan TIDAK digambar: karyawan butuh pengeluaranHarian → "tidak termasuk hak Karyawan"; butuh penjualan saja → boleh; owner selalu boleh',
  angkaBoleh(KRY, ['penjualan', 'pengeluaranHarian']) === 'tidak termasuk hak Karyawan' && angkaBoleh(KRY, ['penjualan']) === '' && angkaBoleh(OWN, ['modalOwner']) === '');

// ---- 3 · tombol per tindakan SS2 (kisi × server)
var t1 = tombolTindakan(BEN, 'jualTunai', 'sendiri', 'Jual tunai'), t2 = tombolTindakan(BEN, 'hitungLaci', 'sendiri', 'Hitung & rapikan laci'), t3 = tombolTindakan(KRY, 'jualBon', 'owner', 'Jual dengan bon'),
  t4 = tombolTindakan(KRY, 'hitungLaci', 'tidak', 'Hitung & rapikan laci'), t5 = tombolTindakan(OWN, 'hapus', 'tidak', 'Hapus'), t6 = tombolTindakan(KRY, 'jualBon', 'sendiri', 'Jual dengan bon');
ok('tombol: Ben jual tunai BOLEH; hitung laci (kisi "sendiri" tapi server tertutup, peta §6) MATI "Perlu persetujuan owner — alurnya menyusul"; karyawan jual bon "minta owner" MATI dengan kalimat yang sama; "tidak boleh" = "Peran Karyawan tidak boleh hitung & rapikan laci"; owner selalu boleh; kisi diubah owner jadi "sendiri" tapi server belum membuka → tetap mati',
  t1.boleh && !t2.boleh && t2.kalimat === KALIMAT_MINTA_OWNER && !t3.boleh && t3.kalimat === KALIMAT_MINTA_OWNER && !t4.boleh && t4.kalimat === 'Peran Karyawan tidak boleh hitung & rapikan laci' && t5.boleh && !t6.boleh, JSON.stringify([t2, t4, t6]));

// ---- 4 · atribusi sah (penulis pusat)
var K = { perangkat: 'Tablet toko', lokasi: 'toko-1', kini: '2026-09-24T03:00:00.000Z' };
var aO = beriAtribusiAkun({ id: 1, hargaTotal: 1000 }, OWN, K, false), aB = beriAtribusiAkun({ id: 2, hargaTotal: 1000 }, BEN, K, false);
var LAMA = { id: 'ps1', status: 'dipesan', namaPelanggan: 'Pelanggan Contoh', riwayatStatus: [] };   // dokumen lama: tanpa oleh/perangkat/lokasi
var aU = beriAtribusiAkun(Object.assign({}, LAMA, { status: 'dibayar' }), KRY, K, true), aUO = beriAtribusiAkun(Object.assign({}, LAMA, { status: 'dibayar' }), OWN, K, true);
ok('atribusi: owner → oleh "Owner" (sama dengan index.html) + olehUid; Ben dokumen baru → oleh nama + olehUid = uid-nya; diubahOleh/diubahOlehUid selalu diisi',
  aO.oleh === 'Owner' && aO.olehUid === 'uid-owner' && aO.diubahOlehUid === 'uid-owner' && aB.oleh === 'Ben Contoh' && aB.olehUid === 'uid-ben' && aB.diubahOleh === 'Ben Contoh' && aB.perangkat === 'Tablet toko' && aB.lokasi === 'toko-1', JSON.stringify([aO, aB]));
ok('atribusi: bukan-owner MENGUBAH dokumen lama → TIDAK menambah oleh/olehUid/perangkat/lokasi (kolom pencipta; rules membatasi kolom, peta §5), cuma diubah*; owner tetap mengisi pencipta kosong seperti dulu; dokumen lama tidak ditambal',
  !('oleh' in aU) && !('olehUid' in aU) && !('perangkat' in aU) && !('lokasi' in aU) && aU.diubahOlehUid === 'uid-kry' && aUO.oleh === 'Owner' && aUO.olehUid === 'uid-owner', JSON.stringify(aU));

// ---- 5 · penjaga kiriman bukan-owner (sebelum dikirim) — sama dengan rules v3
var nota = function (cara, n) { var a = []; for (var i = 0; i < n; i++) a.push({ koleksi: 'penjualan', data: { id: 100 + i, caraBayar: cara, jenis: 'literan', hargaTotal: 13500 }, ada: false, lama: null }); return a; };
var p1 = periksaKiriman(KRY, nota('Tunai', 3).concat([{ koleksi: 'stokBahanLiteran', data: { id: 101.5, tipe: 'pakai' }, ada: false }, { koleksi: 'strukKeluar', data: { id: 9 }, ada: false }]), [], HAK_KRY);
var p2 = periksaKiriman(KRY, nota('Kredit', 1), [], HAK_KRY), p3 = periksaKiriman(BEN, nota('Kredit', 1).concat([{ koleksi: 'piutangMutasi', data: { id: 5, tipe: 'bayar' }, ada: false }]), [], HAK_BEN);
ok('kiriman: karyawan nota tunai 3 baris + kantong pakai + struk = 5 dokumen → boleh, access call 6 (dokumen + 1 jejak); karyawan nota KREDIT ditolak ("minta owner"); Ben nota kredit + bayar sebagian → boleh',
  !p1.tolak && p1.accessCall === 6 && p2.tolak === KALIMAT_MINTA_OWNER && !p3.tolak && p3.accessCall === 3, JSON.stringify([p1, p2, p3]));
var p4 = periksaKiriman(BEN, [{ koleksi: 'piutangMutasi', data: { id: 6, tipe: 'hapusBuku' }, ada: false }], [], HAK_BEN), p5 = periksaKiriman(BEN, [{ koleksi: 'stokBahanKemasan', data: { id: 7, tipe: 'beli', hargaTotal: 100000 }, ada: false }], [], HAK_BEN),
  p6 = periksaKiriman(BEN, [{ koleksi: 'batchMasuk', data: { id: 8 }, ada: false }], [], HAK_BEN), p7 = periksaKiriman(KRY, [{ koleksi: 'batchMasuk', data: { id: 8 }, ada: false }], [], HAK_KRY),
  p8 = periksaKiriman(BEN, [{ koleksi: 'pengeluaranHarian', data: { id: 9 }, ada: false }], [], HAK_BEN), p9 = periksaKiriman(KRY, [], [{ koleksi: 'penjualan', id: 1 }], HAK_KRY),
  p10 = periksaKiriman(BEN, [{ koleksi: 'penjualan', data: { id: 10, dibatalkan: true }, ada: false }], [], HAK_BEN);
ok('kiriman: hapus buku bon, beli kantong (bukan "pakai"), kedatangan (Ben kisi "sendiri" → minta owner, peta §6; karyawan juga), uang keluar, HAPUS apa pun, penjualan bertanda dibatalkan — semua DITOLAK di perangkat',
  !!p4.tolak && !!p5.tolak && p6.tolak === KALIMAT_MINTA_OWNER && p7.tolak === KALIMAT_MINTA_OWNER && p8.tolak === KALIMAT_MINTA_OWNER && p9.tolak === 'Peran Karyawan tidak boleh hapus catatan' && !!p10.tolak, JSON.stringify([p4, p5, p6, p8, p9, p10]));
var PS = { id: 'ps1', status: 'dipesan', namaPelanggan: 'Pelanggan Contoh', nilai: 90000, riwayatStatus: [], oleh: 'Owner' };
var ubahPs = function (tambah, lama) { var d = Object.assign({}, lama || PS, { status: 'dibayar', riwayatStatus: [{ status: 'dibayar', pada: W.kini }], trxIdJual: 5 }, tambah || {}); return [{ koleksi: 'pesanan', data: beriAtribusiAkun(d, KRY, K, true), ada: true, lama: lama || PS }]; };
var q1 = periksaKiriman(KRY, ubahPs(), [], HAK_KRY), q2 = periksaKiriman(KRY, ubahPs({ nilai: 1 }), [], HAK_KRY), q3 = periksaKiriman(KRY, ubahPs(null, Object.assign({}, PS, { status: 'dibayar' })), [], HAK_KRY),
  q4 = periksaKiriman(KRY, [{ koleksi: 'pelangganCatatan', data: { id: 'x', nama: 'X', ciri: 'baru' }, ada: true, lama: { id: 'x', nama: 'X', ciri: '' } }], [], HAK_KRY);
ok('kiriman: pesanan jadi DIBAYAR (status, riwayatStatus, trxIdJual + diubah*) → boleh (peta §5 baris 1); ikut mengubah nilai → ditolak; pesanan yang sudah dibayar → ditolak; mengubah kartu pelanggan yang sudah ada → ditolak',
  !q1.tolak && !!q2.tolak && !!q3.tolak && !!q4.tolak, JSON.stringify([q1, q2, q3, q4]));
var besar = nota('Tunai', 17), lebih = nota('Tunai', 18);
ok('kiriman: 17 dokumen = 18 access call → masih boleh; 18 dokumen (19 access call) → ditolak di perangkat "pecah jadi dua nota, batas 17" (batas batch Firebase 20, sisa 2 — owner 24 Sep, tanpa cache)',
  BATAS_KIRIM_STAF === 18 && periksaKiriman(KRY, besar, [], HAK_KRY).accessCall === 18 && /batas 17\) — pecah jadi dua nota/.test(periksaKiriman(KRY, lebih, [], HAK_KRY).tolak || ''), JSON.stringify(periksaKiriman(KRY, lebih, [], HAK_KRY)));
ok('batas per akun: owner tanpa batas baris/hasil (0); Ben & karyawan 7 baris per nota, 8 hasil per adukan (terburuknya 17 access call — alat-uji/peta_akses.py --kiriman)',
  batasBarisNota(OWN) === 0 && batasHasilAdukan(OWN) === 0 && batasBarisNota(BEN) === 7 && batasBarisNota(KRY) === 7 && batasHasilAdukan(KRY) === 8);
ok('kiriman: owner tidak diperiksa (payung owner, 0 access call); akun belum terdaftar ditolak apa pun isinya',
  periksaKiriman(OWN, lebih, [{ koleksi: 'penjualan', id: 1 }], {}).accessCall === 0 && periksaKiriman(BLM, nota('Tunai', 1), [], {}).tolak === 'Akun ini belum didaftarkan owner');

// ---- 6 · SATU baris jejak per kiriman bukan-owner memuat SEMUA dokumennya (owner poin 1-B)
var lima = nota('Tunai', 3).concat([{ koleksi: 'stokBahanLiteran', data: { id: 101.5, tipe: 'pakai' } }, { koleksi: 'strukKeluar', data: { id: 9, total: 40500 } }]);
var JK = jejakKiriman(KRY, lima, { idJejak: 555, kini: K.kini, perangkat: K.perangkat });
ok('jejak: kiriman 5 dokumen → SATU baris yang menyebut 5 (koleksi, id, ringkas), olehUid = uid penulis, ringkasnya "5 catatan"',
  JK.dokumen.length === 5 && JK.dokumen[3].koleksi === 'stokBahanLiteran' && JK.dokumen[3].id === '101.5' && JK.olehUid === 'uid-kry' && JK.oleh === 'Karyawan Contoh' && /^5 catatan/.test(JK.ringkas) && JK.id === 555, JSON.stringify(JK));

// ---- 7 · minta didaftarkan
var M1 = susunPermintaan(BLM, 'Baru Contoh', W.kini), M2 = susunPermintaan(KAS, 'Kasir', W.kini), M3 = susunPermintaan(BLM, 'x', W.kini), M4 = susunPermintaan(BEN, 'Ben', W.kini);
ok('minta didaftarkan: akun belum terdaftar → dokumen persis {uid, email, nama, pada}; kasir@ ditolak; nama < 2 huruf ditolak; akun yang sudah aktif tidak perlu minta',
  M1.data && Object.keys(M1.data).sort().join() === 'email,nama,pada,uid' && M1.data.uid === 'uid-baru' && !!M2.tolak && !!M3.tolak && !!M4.tolak, JSON.stringify([M1, M2.tolak]));

// ---- 8 · salinan antre (7b)
var simpanan = {}; var PENY = { baca: function (k) { return simpanan[k] || null; }, tulis: function (k, v) { simpanan[k] = v; } };
var A1 = buatAntre(PENY, 'sesi-1'); A1.tambah({ id: 'k1', pada: W.kini, akunUid: 'uid-kry', akunNama: 'Karyawan Contoh', peran: 'karyawan', dokumen: [{ koleksi: 'penjualan', data: { id: 1, diubahPada: '2026-09-24T03:00:00.000Z' } }] });
A1.tambah({ id: 'k2', pada: W.kini, akunUid: 'uid-kry', dokumen: [{ koleksi: 'penjualan', data: { id: 2, diubahPada: '2026-09-24T03:00:00.000Z' } }] });
var A2 = buatAntre(PENY, 'sesi-2');   // perangkat dimuat ulang
ok('antre: salinan TAHAN dimuat ulang (sesi baru membaca 2 kiriman); yang masih antre TIDAK bisa dibuang (keluar tidak menghapus diam-diam)', A2.belumTerkirim().length === 2 && A2.buang('k1') === false && A2.belumTerkirim().length === 2);
A2.tandaiDitolak('k2', 'permission-denied', W.kini); A2.konfirmasi('k1');
ok('antre: konfirmasi server → salinan hilang; ditolak → ditandai "ditolak" + alasan, tetap ada sampai owner memutuskan; buang hanya untuk yang ditolak',
  A2.belumTerkirim().length === 0 && A2.ditolak().length === 1 && A2.ditolak()[0].alasan === 'permission-denied' && A2.buang('k2') === true && A2.semua().length === 0);
var A3 = buatAntre(PENY, 'sesi-3'); var penuh = true; for (var i = 0; i < BATAS_ENTRI; i++) penuh = A3.tambah({ id: 'b' + i, dokumen: [] }).ok && penuh;
var lewat = A3.tambah({ id: 'lewat', dokumen: [] });
ok('antre: berbatas — kiriman ke-' + (BATAS_ENTRI + 1) + ' DITOLAK di perangkat, tidak ada salinan lama yang dibuang', penuh && !!lewat.tolak && A3.semua().length === BATAS_ENTRI && !A3.semua().some(function (x) { return x.id === 'lewat'; }));
simpanan = {}; var A4 = buatAntre(PENY, 'lama');
A4.tambah({ id: 'ada', dokumen: [{ koleksi: 'penjualan', data: { id: 11, diubahPada: '2026-09-24T03:00:00.000Z' } }] }); A4.tambah({ id: 'hilang', dokumen: [{ koleksi: 'penjualan', data: { id: 12, diubahPada: '2026-09-24T03:00:00.000Z' } }] });
var A5 = buatAntre(PENY, 'kini'); A5.tambah({ id: 'sesiini', dokumen: [{ koleksi: 'penjualan', data: { id: 13, diubahPada: '2026-09-24T03:00:00.000Z' } }] });
var server = { '11': { id: 11, diubahPada: '2026-09-24T03:00:00.000Z' } };
var H = A5.cocokkanSesudahSinkron(cekDariCache(function (kol, id) { return server[id] || null; }), W.kini);
ok('antre: sesudah sinkron, kiriman SESI LAIN yang dokumennya ada di server → dikonfirmasi; yang TIDAK ada → "ditolak server saat sinkron"; kiriman sesi ini (tab-nya masih menunggu jawaban) tidak disentuh',
  H.dikonfirmasi === 1 && H.ditolak === 1 && A5.ditolak().length === 1 && A5.ditolak()[0].id === 'hilang' && /saat sinkron/.test(A5.ditolak()[0].alasan) && A5.belumTerkirim().length === 1 && A5.belumTerkirim()[0].id === 'sesiini', JSON.stringify(H));

// ---- 9 · SS2 akun per orang (owner)
pasok('permintaanAkses', [{ id: 'uid-baru', uid: 'uid-baru', email: 'baru.contoh@tokoberasmiqbal.web.app', nama: 'Baru Contoh', pada: '2026-09-24T02:00:00.000Z' }]);
pasok('aksesAkun', [{ id: 'uid-ben', uid: 'uid-ben', nama: 'Ben Contoh', email: 'ben.contoh@tokoberasmiqbal.web.app', peran: 'ben', aktif: true }]);
var SA = ssAkun(); var D0 = susunDaftarkan('uid-baru', '', W), D1 = susunDaftarkan('uid-baru', 'owner', W), D2 = susunDaftarkan('uid-baru', 'karyawan', W);
ok('SS2: permintaan akses tampil (1) + akun terdaftar (1); daftarkan tanpa peran / sebagai OWNER ditolak; sebagai karyawan → aksesAkun {uid, nama, email, peran, aktif:true} DAN permintaannya dihapus di kiriman yang sama',
  SA.minta.length === 1 && SA.akun.length === 1 && !!D0.tolak && !!D1.tolak && D2.dokumen[0].koleksi === 'aksesAkun' && D2.dokumen[0].data.peran === 'karyawan' && D2.dokumen[0].data.aktif === true && D2.dokumen[0].data.id === 'uid-baru'
  && D2.hapus.length === 1 && D2.hapus[0].koleksi === 'permintaanAkses' && /disetujui/.test(D2.jejakHapus), JSON.stringify(D2));
var T0 = susunTolakAkses('uid-baru', '', W), T1 = susunTolakAkses('uid-baru', 'bukan orang toko', W);
var U0 = susunUbahAkun('uid-ben', { aktif: false }, W, false), U1 = susunUbahAkun('uid-ben', { aktif: false }, W, true), U2 = susunUbahAkun('uid-ben', { peran: 'owner' }, W, true);
ok('SS2: tolak butuh alasan, dicatat di jejak; nonaktifkan = dua ketukan (ketukan pertama ditanya); jadi owner lewat ubah peran ditolak',
  !!T0.tolak && T1.hapus.length === 1 && T1.dokumen.length === 0 && /bukan orang toko/.test(T1.jejakHapus) && U0.perluYakin === true && U1.dokumen[0].data.aktif === false && !!U2.tolak);
(function () { var sebelum = cacheMentah('permintaanAkses').length; tulisDokumen(D2.dokumen, D2.hapus, { jejakHapus: D2.jejakHapus });
  ok('penulis (simulasi): tulis + hapus dalam satu kiriman → aksesAkun masuk, permintaannya hilang', sebelum === 1 && cacheMentah('permintaanAkses').length === 0 && cacheMentah('aksesAkun').some(function (a) { return a.id === 'uid-baru'; })); })();

// ---- 9b · kisi SS2 menampilkan KEBENARAN SERVER (owner 24 Sep, putaran 23c)
var SP = ssPeran(); var sel = function (p, x) { return SP.tampil(p, x); };
ok('kisi SS2: hitung laci (Ben) & kedatangan (Ben, karyawan) — kisi "sendiri" tapi server menutup → tampil "tertutup server" beserta sebabnya, BUKAN "boleh sendiri"; jual tunai Ben tetap "boleh sendiri"; owner selalu "boleh sendiri"',
  sel('ben', 'hitungLaci').label === 'tertutup server' && /titik kas/.test(sel('ben', 'hitungLaci').ket) && sel('ben', 'kedatangan').label === 'tertutup server' && /harga beli/.test(sel('karyawan', 'kedatangan').ket)
  && sel('karyawan', 'kedatangan').label === 'tertutup server' && sel('ben', 'jualTunai').label === 'boleh sendiri' && sel('owner', 'hitungLaci').label === 'boleh sendiri' && sel('karyawan', 'hitungLaci').label === 'tidak boleh', JSON.stringify([sel('ben', 'hitungLaci'), sel('karyawan', 'kedatangan')]));
var semuaSendiri = SS_TINDAKAN.filter(function (x) { return ['ben', 'karyawan'].some(function (p) { return sel(p, x.id).label === 'boleh sendiri' && (SERVER_BUKA[x.id] || []).indexOf(p) < 0; }); });
ok('kisi SS2: TIDAK ADA sel "boleh sendiri" yang ditutup server (semua 13 tindakan × 2 peran); "minta owner" menyebut alurnya belum ada; ringkasan peran menghitung "tertutup server" terpisah',
  semuaSendiri.length === 0 && /belum ada/.test(sel('ben', 'nego').ket) && /2 tertutup server/.test(SP.peran[1].ket) && /1 tertutup server/.test(SP.peran[2].ket), JSON.stringify([semuaSendiri.map(function (x) { return x.id; }), SP.peran[1].ket, SP.peran[2].ket]));

// ---- 10 · sambungan di firebase.js (sumber diperiksa — tidak bisa dijalankan di jsc)
var F = SUMBER.firebase, A = SUMBER.app;
var iPeriksa = F.indexOf('periksaKiriman(akun, isi, H'), iBatch = F.indexOf('const b = writeBatch(db); const ditulis = [];'), iAntre = F.indexOf('antre.tambah({ id: idKiriman'), iCommit = F.indexOf('const janji = b.commit().then(() => { antre.konfirmasi(idKiriman)');
ok('firebase.js: penjaga bukan-owner jalan SEBELUM batch dibangun; salinan antre dibuat SEBELUM commit; salinan dihapus HANYA di .then (server mengaku); ditolak → tandaiDitolak',
  iPeriksa > 0 && iBatch > iPeriksa && iAntre > iBatch && iCommit > iAntre && F.indexOf("antre.tandaiDitolak(idKiriman, kode") > iCommit && F.indexOf('antre.konfirmasi(') === iCommit + 'const janji = b.commit().then(() => { '.length);
ok('firebase.js: bukan-owner = SATU jejakKiriman per kiriman; owner = satu jejak per dokumen dengan olehUid; atribusi lewat beriAtribusiAkun; owner dikenali lewat EMAIL_OWNER, peran lain lewat aksesAkun/{uid} yang didengarkan terus',
  F.indexOf('if (!owner) { const log = jejakKiriman(akun, ditulis') > 0 && F.indexOf('olehUid: akun.uid, perangkat: k.perangkat, ringkas: ringkasDok(d)') > 0 && F.indexOf('beriAtribusiAkun(x.data, akun, k, x.ada)') > 0
  && F.indexOf("if (email === EMAIL_OWNER) return terapkan(keadaanAkun(email, u.uid, null));") > 0 && F.indexOf("onSnapshot(doc(db, 'aksesAkun', u.uid)") > 0 && F.indexOf('EMAIL_TOKO') < 0);
ok('firebase.js: bukan-owner tidak pernah HAPUS / bersihkan / arsip; nonaktif = cabut SEMUA pendengar; satu pendengar ditolak tidak mematikan aplikasi (status.masuk tidak dimatikan)',
  F.indexOf("if (!status.akun || status.akun.jenis !== 'owner') { const p = periksaKiriman(status.akun, [], daftar") > 0 && (F.match(/if \(pemilikSaja\(\)\)/g) || []).length === 3
  && F.indexOf('} else { cabutPendengar(); }') > 0 && F.indexOf("includes('permission-denied')) { status.masuk = false; }") < 0);
ok('app.js: pemilih pemegang hilang; formulir = email + sandi, sandi readonly sampai diketuk (tidak diisi otomatis), email terakhir bisa dilupakan satu ketukan; Keluar menanyakan catatan yang belum terkirim; menu menyembunyikan layar bukan-hak',
  A.indexOf('setelPemegang') < 0 && SUMBER.html.indexOf('id="isianSandi" type="password" class="ketik-nama" placeholder="Sandi" autocomplete="off" readonly') > 0 && A.indexOf('lupakanEmail') > 0
  && A.indexOf("catatan belum terkirim dari akun ini") > 0 && A.indexOf("el.hidden = !!a && !bolehLayar(a, el.dataset.tujuan)") > 0 && SUMBER.html.indexOf('id="tombolKeluar"') > 0);
// ---- 11 · TIRAI (putaran 23c): sebelum masuk / belum disetujui / nonaktif, layar di belakang formulir Masuk KOSONG (uji peramban: uji_layar_kunci.py)
var LT = ['jual', 'ringkasan', 'stok', 'pelanggan', 'menu', 'harga', 'uang', 'laporan'];
var tanpaGerbang = LT.filter(function (n) { var s = SUMBER['layar_' + n]; return s.indexOf("import { terkunci } from '../inti/kunci.js';") < 0 || !/if \((!tampil \|\| )?terkunci\(\)\) return;/.test(s); });
ok('tirai: KEDELAPAN layar memeriksa terkunci() sebelum menggambar; bawaan terkunci (sebelum Firebase menjawab); app.js membuka hanya untuk owner / akun aktif (bisaBekerja) atau mode cadangan, dan saat menutup MENGOSONGKAN tiap <main>',
  tanpaGerbang.length === 0 && SUMBER.kunci.indexOf('let _kunci = true;') >= 0 && A.indexOf("const kunci = !q.get('cadangan') && !bisaBekerja(akun);") > 0 && A.indexOf("if (kunci) { Object.keys(LAYAR_ADA).forEach((k) => { LAYAR_ADA[k].innerHTML = ''; }); return; }") > 0
  && A.indexOf('function gambarAkun(akun) {\n  jagaKeranjang(akun);\n  terapkanKunci(akun);') > 0 && A.indexOf('terapkanKunci(null);') > 0 && SUMBER.layar_ringkasan.indexOf("if (!tampil || terkunci() || !$('rkJam')) return;") > 0, JSON.stringify(tanpaGerbang));
// ---- 12 · GANTI ORANG (putaran 23c): keranjang Jual tidak terbawa ke akun berikutnya (uji peramban: uji_layar_kunci.py bagian 2)
var iTanya = A.indexOf("(await tanyaKeranjang(B)) !== 'kosongkan'"), iLupa = A.indexOf("layar.lupakanOrang(); uidKeranjang = '';\n  await fb.keluar();"), iBelum = A.indexOf('catatan belum terkirim dari akun ini');
ok('ganti orang: Keluar dengan keranjang berisi DITANYA dulu (sebelum pertanyaan catatan belum terkirim), keranjang dilupakan tepat sebelum keluar; keluar dari tempat lain / akun berbeda = dilupakan tanpa ditanya; kalimat owner persis',
  iTanya > 0 && iBelum > iTanya && iLupa > iBelum && A.indexOf("if (!akun || akun.jenis === 'keluar') { layar.lupakanOrang(); uidKeranjang = ''; return; }") > 0 && A.indexOf('if (uidKeranjang && uidKeranjang !== akun.uid) layar.lupakanOrang();') > 0
  && SUMBER.layar_jual.indexOf('lupakanOrang: () => K.setel((s) => L.keadaanOrangBerikutnya(s))') > 0 && SUMBER.html.indexOf('id="modalKeranjang"') > 0);
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""


LAYAR_TIRAI = ['jual', 'ringkasan', 'stok', 'pelanggan', 'menu', 'harga', 'uang', 'laporan']


def sumber():
    b = lambda p: open(os.path.join(AKAR, p), encoding='utf-8').read()
    s = {'firebase': b('baru/js/data/firebase.js'), 'app': b('baru/js/app.js'), 'html': b('baru/index.html'), 'kunci': b('baru/js/inti/kunci.js')}
    for n in LAYAR_TIRAI: s['layar_' + n] = b('baru/js/layar/' + n + '.js')
    return s


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:900]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js, src=None):
    h, e = jalan(JAM + js + '\nvar SUMBER = ' + json.dumps(src or sumber()) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL); S = sumber()
    if '--kontrol' in sys.argv:
        ganti = lambda kunci, a, b: dict(S, **{kunci: S[kunci].replace(a, b)})
        rusak = {
            'peran dari dokumen bisa menjadi owner': (js.replace("if (PERAN_BUKAN_OWNER.indexOf(peran) < 0) return { jenis: 'nonaktif'", "if (peran === 'owner') return { jenis: 'owner', peran: 'owner', nama: 'Owner', uid, email: e }; if (PERAN_BUKAN_OWNER.indexOf(peran) < 0) return { jenis: 'nonaktif'"), S),
            'akun tanpa aksesAkun tetap mendengarkan koleksi': (js.replace("if (!bisaBekerja(akun)) return [];\n  if (akun.jenis === 'owner') return KOLEKSI.map", "if (akun.jenis === 'owner') return KOLEKSI.map"), S),
            'karyawan melihat layar uang': (js.replace("const LAYAR_STAF = ['jual', 'pelanggan', 'stok', 'menu'];", "const LAYAR_STAF = ['jual', 'pelanggan', 'stok', 'menu', 'uang'];"), S),
            'karyawan mendengarkan koleksi uang': (js.replace("'katalogHargaKarung', 'katalogHargaKemasan', 'katalogHargaLiteran', 'hargaWadah'];", "'katalogHargaKarung', 'katalogHargaKemasan', 'katalogHargaLiteran', 'hargaWadah', 'pengeluaranHarian'];"), S),
            'setelan didengar seluruh koleksi (tarif upah bocor)': (js.replace("aturanToko: ['struk', 'pelanggan', 'pelangganKembar', 'catatStok', 'kantong', 'tempat', 'peran', 'perangkat']", "aturanToko: ['struk', 'pelanggan', 'pelangganKembar', 'catatStok', 'kantong', 'tempat', 'peran', 'perangkat', 'upah']"), S),
            'tulisan tanpa olehUid lolos': (js.replace("if (!d.oleh) { d.oleh = akun.nama; d.olehUid = akun.uid; }", "if (!d.oleh) { d.oleh = akun.nama; }"), S),
            'update bukan-owner menambah kolom pencipta': (js.replace("const isiPencipta = akun.jenis === 'owner' || !ada;", "const isiPencipta = true;"), S),
            'tombol ikut kisi saja, server diabaikan': (js.replace("const buka = SERVER_BUKA[tindakan] || []; if (buka.indexOf(akun.peran) < 0) return { boleh: false, kalimat: KALIMAT_MINTA_OWNER };", ""), S),
            'karyawan boleh jual bon': (js.replace("const KREDIT_STAF = ['ben'];", "const KREDIT_STAF = ['ben', 'karyawan'];"), S),
            'bukan-owner boleh hapus buku bon': (js.replace("if (x.koleksi === 'piutangMutasi' && d.tipe !== 'bayar') return", "if (false) return"), S),
            'bukan-owner boleh beli kantong': (js.replace("if ((x.koleksi === 'stokBahanLiteran' || x.koleksi === 'stokBahanKemasan') && d.tipe !== 'pakai') return", "if (false) return"), S),
            'bukan-owner boleh hapus': (js.replace("if (hapus && hapus.length) return { tolak: tolakTindakan('hapus') };", ""), S),
            'update pesanan boleh mengubah kolom mana saja': (js.replace("const liar = berubah.filter((kk) => u.kolom.indexOf(kk) < 0); if (liar.length) return { tolak: tolakTindakan('koreksi') };", ""), S),
            'pesanan yang sudah dibayar bisa diubah lagi': (js.replace("if (x.koleksi === 'pesanan' && (['dibayar', 'batal'].indexOf(String(lama.status || '')) >= 0 || d.status !== 'dibayar'))", "if (x.koleksi === 'pesanan' && d.status !== 'dibayar')"), S),
            'batas access call dilewati': (js.replace("if (accessCall > BATAS_KIRIM_STAF) return", "if (accessCall > 99) return"), S),
            'pagar perangkat tanpa sisa 2': (js.replace("const BATAS_KIRIM_STAF = BATAS_ACCESS_CALL - CADANGAN_ACCESS_CALL;", "const BATAS_KIRIM_STAF = BATAS_ACCESS_CALL;"), S),
            'kisi SS2 memajang "boleh sendiri" yang ditutup server': (js.replace("if (nilai === 'sendiri' && (SERVER_BUKA[tindakan] || []).indexOf(peran) < 0) return", "if (false) return"), S),
            'jejak kiriman cuma menyebut dokumen pertama': (js.replace("const daftar = (dokumen || []).map((x) => ({ koleksi: x.koleksi, id: String(x.data.id), ringkas: ringkasDok(x.data) }));", "const daftar = (dokumen || []).slice(0, 1).map((x) => ({ koleksi: x.koleksi, id: String(x.data.id), ringkas: ringkasDok(x.data) }));"), S),
            'kasir@ bisa minta didaftarkan': (js.replace("if (e === EMAIL_KASIR) return { jenis: 'kasir'", "if (false) return { jenis: 'kasir'"), S),
            'antre tidak tahan dimuat ulang': (js.replace("const v = penyimpan.baca(KUNCI_ANTRE); const a = v ? JSON.parse(v) : [];", "const a = [];"), S),
            'antre membuang yang belum terkirim': (js.replace("if (!x || x.keadaan !== 'ditolak') return false;", "if (!x) return false;"), S),
            'antre penuh membuang salinan lama': (js.replace("if (a.length >= BATAS_ENTRI) return { tolak:", "if (a.length >= BATAS_ENTRI) a.shift(); if (false) return { tolak:"), S),
            'sinkron menyentuh kiriman sesi ini': (js.replace("baca().filter((x) => x.keadaan === 'antre' && x.sesi !== (sesi || ''))", "baca().filter((x) => x.keadaan === 'antre')"), S),
            'dokumen hilang dianggap terkirim': (js.replace("const d = ambilDok(koleksi, id); if (!d) return false;", "const d = ambilDok(koleksi, id); if (!d) return true;"), S),
            'SS2 akun bisa didaftarkan sebagai owner': (js.replace("const SS_PERAN_AKUN = SS_PERAN.filter((p) => p.id !== 'owner');", "const SS_PERAN_AKUN = SS_PERAN;"), S),
            'SS2 nonaktifkan tanpa ketukan kedua': (js.replace("if (U.aktif !== undefined && !yakin) return", "if (false) return"), S),
            'SS2 daftarkan tanpa menghapus permintaan': (js.replace("return { dokumen: [{ koleksi: 'aksesAkun', data }], hapus: [{ koleksi: 'permintaanAkses', id: m.uid }],", "return { dokumen: [{ koleksi: 'aksesAkun', data }], hapus: [],"), S),
            'firebase: salinan antre dihapus sebelum server mengaku': (js, ganti('firebase', "const janji = b.commit().then(() => { antre.konfirmasi(idKiriman); return { ok: true }; })", "antre.konfirmasi(idKiriman); const janji = b.commit().then(() => { return { ok: true }; })")),
            'firebase: penjaga bukan-owner dilewati': (js, ganti('firebase', "if (!owner) { const p = periksaKiriman(akun, isi, H, _sumberHak()); if (p.tolak) return { gagal: true, pesan: p.tolak }; }", "")),
            'firebase: jejak per dokumen untuk bukan-owner': (js, ganti('firebase', "if (!owner) { const log = jejakKiriman(akun, ditulis", "if (false) { const log = jejakKiriman(akun, ditulis")),
            'firebase: satu pendengar ditolak mematikan aplikasi': (js, ganti('firebase', "}, (err) => tolak(k.nama, err));", "}, (err) => { if (String(err && err.code || '').includes('permission-denied')) { status.masuk = false; } tolak(k.nama, err); });")),
            'app: sandi boleh diisi otomatis': (js, ganti('html', 'placeholder="Sandi" autocomplete="off" readonly', 'placeholder="Sandi" autocomplete="current-password"')),
            'app: keluar tanpa menanyakan yang belum terkirim': (js, ganti('app', "catatan belum terkirim dari akun ini", "catatan")),
            'tirai: layar Uang menggambar walau terkunci': (js, ganti('layar_uang', 'if (!tampil || terkunci()) return;', 'if (!tampil) return;')),
            'tirai: bawaan terbuka sebelum Firebase menjawab': (js, ganti('kunci', 'let _kunci = true;', 'let _kunci = false;')),
            'tirai: menutup tanpa mengosongkan <main>': (js, ganti('app', "if (kunci) { Object.keys(LAYAR_ADA).forEach((k) => { LAYAR_ADA[k].innerHTML = ''; }); return; }", "if (kunci) return;")),
            'tirai: akun belum disetujui ikut membuka': (js, ganti('app', "const kunci = !q.get('cadangan') && !bisaBekerja(akun);", "const kunci = !q.get('cadangan') && !akun;")),
            'ganti orang: Keluar tanpa menanyakan keranjang': (js, ganti('app', "(await tanyaKeranjang(B)) !== 'kosongkan'", "false")),
            'ganti orang: akun berbeda mewarisi keranjang': (js, ganti('app', 'if (uidKeranjang && uidKeranjang !== akun.uid) layar.lupakanOrang();', '')),
        }
        kode = 0
        for nama, (isi, src) in rusak.items():
            if isi == js and src == S: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi, src)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js, S)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    sys.exit(2 if g else 0)
