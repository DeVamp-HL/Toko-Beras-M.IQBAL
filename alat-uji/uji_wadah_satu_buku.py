#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_wadah_satu_buku.py — putaran 39: WADAH LITERAN SATU BUKU PER KOTAK (keputusan owner 29 Sep 2026, docs/peta-wadah-satu-buku.md §8).
  · Karung di belakang wadah AKTIF = buku mesin sendiri 'Karung belakang <wadah> · <merek>' (data/toko.js): buka karung = pindah buku merek → karung
    belakang (tumpukan gudang turun DI BUKU), tuang / takar = pindah buku karung belakang → wadah. Kolam catatan tetap ditulis bernama kuncinya
    (merkAsal = merek pemasok); selisih kolam vs buku DISEBUT (wbSelisihWadah).
  · Isi ulang TIGA KETUKAN (wbSusunIsiUlangTiga): merek asal × 1 karung / ½ karung / kg (koma) — karung belakang dipakai dulu, kurang → karung baru dibuka
    sebanyak yang perlu; melewati batas menggunung DITOLAK; wadah belum aktif DITOLAK. Panel − / + takar lama tetap (susunTakarWadah): sumber merek biasa
    dinormalkan ke kunci karung belakang, karung lama bernama merek yang masih cukup dipakai dulu.
  · Buku merek asal kurang → { tolak, perluTandai } tanpa dokumen; ketukan kedua opsi.tandai → pindah bertanda perluCocokkan + selisihKg + selisihPerMerk,
    buku merek dibiarkan minus; tuntas = cocokkan merek itu bertanggal ≥ dokumen (wbPindahTembusBelumCocok → L.notaTembusBelumCocok → pita Jual & kartu
    keempat Gudang 'tembus|<merek>').
  · Aktivasi PER WADAH dari daftar (wbDaftarAktivasi / wbSusunAktifkan): belum dicocokkan / bagian minus → tidak bisa; karung lama bernama merek di
    belakangnya ikut jadi buku karung belakang; nilai stok, laba, tumpukan tidak bergeser (pindah buku, modal ikut).
  · Komposisi & banding = TURUNAN riwayat isi ulang (wbKomposisiTurunan), disebar sebanding buku wadah — bukan angka kedua.
  · Cek wadah tutup toko (wbCekHari / wbSusunCek): sesuai · lupa isi ulang · dikosongkan (= sisihkan seluruh buku ke karung wadah tanpa timbang).
  · Tutup buku membawa tanda karungBelakang/merkAsal; katalog HP kasir & daftar merek tidak memuat kunci karung belakang; penjaga perangkat = rules v5.
KOTAK PASIR (ANGKA CONTOH), jam dikunci 21 Sep 2026 10:00 WIB. Cadangan toko di _privat/ (dilewati bila tidak ada): aktivasi semua wadah disimulasikan —
identitas per wadah & per merek asal, nilai stok/laba tidak bergeser, isi ulang & jual contoh, kunci karung belakang tidak bocor; ASAP GLOBAL laporan
byte-sama kode main (uji_wadah_bernama.asap_global).

    python3 alat-uji/uji_wadah_satu_buku.py            → N lulus · 0 gagal
    python3 alat-uji/uji_wadah_satu_buku.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import uji_wadah_bernama  # noqa: E402
import uji_wadah_stok_sendiri  # noqa: E402

MODUL = uji_wadah_stok_sendiri.MODUL
JAM_TETAP = "var __KINI = new Date('2026-09-21T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
brs = uji_wadah_bernama.brs

KOTAK = {
  # satu kedatangan: NG 10, Kumala 4, Angsa 4, Tawon 1 karung 50 kg; Beo 1 karung 25 kg (merek yang hanya pernah datang 25 kg → satu karung = 25 kg)
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-09-10', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
                  'merkList': [brs(1, 'NG', 10, 12000), brs(2, 'Kumala', 4, 11000), brs(3, 'Angsa', 4, 13000), brs(4, 'Tawon', 1, 12500), brs(5, 'Beo', 1, 14000, 25)]}],
  # lima wadah (belum ada yang aktif):
  #  W1 IR64 Apex  = isi 50 (NG 30 + Kumala 20) + karung LAMA bernama merek Kumala 50 kg di belakangnya      → bisa & cukup
  #  W2 Angsa      = titik samakan 0 kg                                                                     → bisa & cukup (tanpa pindah)
  #  W3 Campur Dua = isi 10 (NG 5 + Kumala 5), lalu 8,2 kg NG terjual dari wadah itu → bagian NG minus       → tidak bisa
  #  W4 Kosong Satu = belum pernah dicocokkan                                                               → tidak bisa
  #  W5 Tawon Super = isi 55 (Tawon) + karung lama Tawon sisa 30; buku Tawon cuma 50 → kurang 35            → bisa, tidak cukup (tandai)
  'wadahLiteran': [{'id': 100, 'tanggal': '2026-09-01', 'jam': '07:00', 'tipe': 'atur', 'penuhKg': 50, 'puncakKg': 60, 'isiUlangKg': 10, 'takarKg': 1.8, 'sisihKg': 10,
                    'daftar': ['IR64 Apex', 'Angsa', 'Campur Dua', 'Kosong Satu', 'Tawon Super']},
                   {'id': 101, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'IR64 Apex', 'isiKg': 50, 'komposisi': {'NG': 30, 'Kumala': 20}},
                   {'id': 102, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'Angsa', 'isiKg': 0},
                   {'id': 103, 'tanggal': '2026-09-19', 'jam': '07:30', 'tipe': 'karung', 'merk': 'Kumala', 'kg': 50, 'wadah': 'IR64 Apex'},
                   {'id': 104, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'Campur Dua', 'isiKg': 10, 'komposisi': {'NG': 5, 'Kumala': 5}},
                   {'id': 105, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'Tawon Super', 'isiKg': 55, 'komposisi': {'Tawon': 55}},
                   {'id': 106, 'tanggal': '2026-09-18', 'jam': '07:30', 'tipe': 'karung', 'merk': 'Tawon', 'kg': 50, 'wadah': 'Tawon Super'},
                   {'id': 107, 'tanggal': '2026-09-19', 'jam': '07:40', 'tipe': 'karungIsi', 'merk': 'Tawon', 'isiKg': 30, 'wadah': 'Tawon Super'}],
  'katalogHargaLiteran': [{'id': 'IR64 Apex', 'merk': 'IR64 Apex', 'hargaPerLiter': 12000}, {'id': 'Angsa', 'merk': 'Angsa', 'hargaPerLiter': 13000},
                          {'id': 'Campur Dua', 'merk': 'Campur Dua', 'hargaPerLiter': 12500}, {'id': 'Tawon Super', 'merk': 'Tawon Super', 'hargaPerLiter': 12500}],
  'katalogHargaKarung': [{'id': 'NG', 'merk': 'NG', 'hargaPerKg': 13000}, {'id': 'Kumala', 'merk': 'Kumala', 'hargaPerKg': 12000}, {'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 14000},
                         {'id': 'Tawon', 'merk': 'Tawon', 'hargaPerKg': 13500}, {'id': 'Beo', 'merk': 'Beo', 'hargaPerKg': 15000}],
  # literan 10 L dari wadah Campur Dua (model 27: baris internal merkSumber NG) sesudah titik samakan → bagian NG = 5 − 8,2 = −3,2
  'penjualan': [{'id': 5003, 'tanggal': '2026-09-19', 'jam': '09:00', 'caraBayar': 'Tunai', 'jenis': 'literan', 'merkSumber': 'NG', 'namaProduk': 'Campur Dua', 'dariWadah': 'Campur Dua',
                 'jumlahLiter': 10, 'totalKg': 8.2, 'hargaTotal': 125000, 'hppTotalSaatJual': 98400}],
}

# pembantu bersama kotak pasir & asap cadangan
BANTU = r"""
var J = JSON.stringify; var B2 = function (n) { return Math.round(n * 100) / 100; }; var B3 = function (n) { return Math.round(n * 1000) / 1000; };
var s0 = function () { var s = keadaanAwal(); s.sekarang = new Date(Date.now()); return s; };
var chipL = function (k, s) { return susunRak(s || s0()).literan.find(function (c) { return c.kunci === k && c.wadahLiteran; }); };
var masuk = function (s, c, j) { var r = masukkan(Object.assign({}, s, { pilih: c }), j); return r.keranjang ? Object.assign({}, s, { keranjang: r.keranjang, urutBaris: r.urutBaris }) : Object.assign({ tolak: r.kabar }, s); };
var buku = function (m) { return (hitungStokKarungPerMerk()[m] || { sisaKg: 0 }).sisaKg; };
var hpp = function (m) { return (hitungStokKarungPerMerk()[m] || { hppTerakhirPerKg: 0 }).hppTerakhirPerKg; };
var nilai = function () { var st = hitungStokKarungPerMerk(); var v = 0; Object.keys(st).forEach(function (m) { v += st[m].sisaKg * st[m].hppTerakhirPerKg; }); return Math.round(v); };
var tump = function (m) { return B2(tumpukanGudang(m).kg); };
var dok = function (R, k) { return (R.dokumen || []).filter(function (d) { return d.koleksi === k; }).map(function (d) { return d.data; }); };
var KB = function (Wn, M) { return wbKunciKB(Wn, M); };
var kb_ = function (m) { return /^Karung belakang /.test(String(m)); };
var kgT = function (n) { return String(B2(n)).replace('.', ',') + ' kg'; };
// IDENTITAS satu wadah aktif, dari DOKUMEN: isi titik samakan + Σ takar sesudahnya − Σ literan (buku wadah) − Σ pindah keluar (sisihan/bongkar) ± penyesuaian = buku = tinggi wadah
var identitasWadah = function (Wn) {
  var kunci = wbKunci(Wn); var semua = ambilWadahLiteran(); var tanda = wdTerbaru(semua.filter(function (d) { return d.wadah === Wn && d.tipe === 'isi'; }));
  var sejak = function (x) { return !tanda || wdSesudah(x, tanda); }; var isi0 = tanda ? Number(tanda.isiKg) || 0 : 0;
  var takar = semua.reduce(function (a, t) { return a + (t.tipe === 'takar' && t.wadah === Wn && sejak(t) ? Number(t.kg) || 0 : 0); }, 0);
  var jual = ambilPenjualan().reduce(function (a, p) { return a + (!p.dibatalkan && p.jenis === 'literan' && p.merkSumber === kunci && sejak(p) ? Number(p.totalKg) || 0 : 0); }, 0);
  var keluar = ambilProduksiBerlaku().reduce(function (a, p) { return a + (p.jadiKarungUtuh && sejak(p) ? (p.sumberList || []).reduce(function (b, x) { return b + (x.merk === kunci ? Number(x.kg) || 0 : 0); }, 0) : 0); }, 0);
  var sesuai = ambilPenyesuaianStok().reduce(function (a, q) { return a + (q.merk === kunci && sejak(q) ? Number(q.selisihKg) || 0 : 0); }, 0);
  var hitung = B2(isi0 + takar - jual - keluar + sesuai); var bk = B2(buku(kunci)); var tw = tinggiWadah(Wn, null);
  var turunan = B2(wbKomposisiTurunan(Wn).daftar.reduce(function (a, x) { return a + x.kg; }, 0));
  return { W: Wn, buku: bk, hitung: hitung, tinggi: tw ? B2(tw.sisaNyataKg) : null, turunan: turunan, ok: Math.abs(hitung - bk) < 0.011 && !!tw && Math.abs(tw.sisaNyataKg - Math.max(0, bk)) < 0.011 && Math.abs(turunan - Math.max(0, bk)) < 0.02 };
};
var bocorKB = function () { var s = s0(); var r = susunRak(s); var kini = new Date(Date.now()); var hk = kartuHpp();
  return { rakKarung: r.karung.filter(function (c) { return kb_(c.kunci); }).length, repack: r.repack.filter(function (c) { return kb_(c.kunci); }).length, literanLangsung: r.literan.filter(function (c) { return !c.wadahLiteran && kb_(c.kunci); }).length,
    calonKarung: calonKarung().filter(function (t) { return kb_(t.merk); }).length, calonCampur: calonCampur([]).filter(kb_).length, harga: hgSemua(kini).baris.filter(function (b) { return kb_(b.merk); }).length,
    masuk: calonMerkMasuk().filter(kb_).length, cocokTumpukan: barangCocok('tumpukan').filter(function (b) { return kb_(b.nama); }).length, kedatangan: daftarKedatangan(50).filter(function (b) { return /LAHIR/.test(b.pemasok); }).length,
    hpp: (hk.kartu || hk).filter(function (k) { return kb_(k.merk); }).length, tempat: barangTempat().filter(function (b) { return kb_(b.nama); }).length, belanja: daftarBelanja(kini).merk.filter(function (b) { return kb_(b.merk); }).length,
    lokasi: susunLokasi().filter(function (t) { return kb_(t.merk); }).length, katalogKasir: kkIsi().merkKarung.filter(function (m) { return kb_(m.merk); }).length, merekSaja: Object.keys(stokMerekSaja(hitungStokKarungPerMerk())).filter(kb_).length }; };
"""

SKENARIO = BANTU + r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var nId = 9000; var W = { tanggal: '2026-09-21', jam: '10:00', kini: '2026-09-21T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var KINI = new Date(Date.now()); var laba = function () { return hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih; };
var MEREK = ['NG', 'Kumala', 'Angsa', 'Tawon', 'Beo']; var b0 = MEREK.map(buku);
var U = function (Wn, M, t, opsi) { return wbSusunIsiUlangTiga(Wn, M, t, W, s0(), opsi); };

// ---- 0 · konstanta & kunci
ok('konstanta: WB_CEK tiga hasil (sesuai · lupa · kosong), WB_TAKARAN tiga takaran (1 karung · ½ karung · kg)', J(WB_CEK.map(function (x) { return x[0]; })) === J(['sesuai', 'lupa', 'kosong']) && J(WB_TAKARAN.map(function (x) { return x[0]; })) === J(['karung', 'setengah', 'kg']) && WB_TAKARAN[1][1] === '½ karung' && WB_CEK[2][1] === 'Dikosongkan');
ok('kunci: kunciKarungBelakang / wbKunciKB = "Karung belakang <W> · <merek>"; sebelum lahir: bukan buku khusus, merkAsalKunci = kunci itu sendiri; merek biasa → dirinya', KB('Angsa', 'NG') === 'Karung belakang Angsa · NG' && kunciKarungBelakang('Angsa', 'NG') === KB('Angsa', 'NG') && !wbBukuKhusus(KB('Angsa', 'NG')) && wbMerkAsal(KB('Angsa', 'NG')) === KB('Angsa', 'NG') && merkAsalKunci('NG') === 'NG' && wbMerkAsal('NG') === 'NG');
ok('keadaan awal: buku NG 491,8 (500 − 8,2 terjual dari Campur Dua), Kumala 200, Angsa 200, Tawon 50, Beo 25; satu karung Beo = 25 kg, NG = 50 kg; belum ada wadah aktif', J(b0.map(B2)) === J([491.8, 200, 200, 50, 25]) && beratKarungBuka('Beo') === 25 && beratKarungBuka('NG') === 50 && aturWadah().daftar.every(function (Wn) { return !wbAktif(Wn); }), J(b0));

// ---- 1 · daftar aktivasi per wadah (3)
var D0 = wbDaftarAktivasi(); var dAp = D0.find(function (x) { return x.W === 'IR64 Apex'; }), dAn = D0.find(function (x) { return x.W === 'Angsa'; }), dCd = D0.find(function (x) { return x.W === 'Campur Dua'; }), dKs = D0.find(function (x) { return x.W === 'Kosong Satu'; }), dTs = D0.find(function (x) { return x.W === 'Tawon Super'; });
ok('daftar aktivasi: lima wadah berurutan W1–W5, belum ada yang aktif', D0.length === 5 && J(D0.map(function (x) { return x.no + ' ' + x.W; })) === J(['W1 IR64 Apex', 'W2 Angsa', 'W3 Campur Dua', 'W4 Kosong Satu', 'W5 Tawon Super']) && D0.every(function (x) { return !x.aktif; }), J(D0));
ok('W1 IR64 Apex: isi 50 (NG 30 + Kumala 20) + karung lama Kumala 50 kg di belakangnya → sumber Kumala 70 (20 di wadah + 50 di karung, buku 200) & NG 30 (buku 491,8); kolam [Kumala 50]; bisa & cukup',
  dAp.bisa && dAp.cukup && dAp.diketahui && dAp.isiKg === 50 && J(dAp.sumber) === J([{ merk: 'Kumala', kg: 70, diWadah: 20, diKarung: 50, buku: 200, kurang: 0, tanpaBuku: false }, { merk: 'NG', kg: 30, diWadah: 30, diKarung: 0, buku: 491.8, kurang: 0, tanpaBuku: false }])
  && J(dAp.kolam) === J([{ merk: 'Kumala', kg: 50 }]) && dAp.alasan === '' && !dAp.minus.length && !dAp.kurang.length, J(dAp));
ok('W2 Angsa: isi tercatat 0 (titik samakan 0 kg) → bisa & cukup tanpa sumber', dAn.bisa && dAn.cukup && dAn.diketahui && dAn.isiKg === 0 && !dAn.sumber.length && !dAn.kolam.length, J(dAn));
ok('W3 Campur Dua: bagian NG minus (5 − 8,2 terjual) → TIDAK bisa, alasan menyebut NG minus', !dCd.bisa && J(dCd.minus) === J(['NG']) && /bagian NG tercatat minus — cocokkan wadahnya dulu/.test(dCd.alasan), J(dCd));
ok('W4 Kosong Satu: isinya belum pernah dicocokkan → TIDAK bisa', !dKs.bisa && !dKs.diketahui && /belum pernah dicocokkan/.test(dKs.alasan), J(dKs));
ok('W5 Tawon Super: isi 55 + karung lama Tawon 30 = butuh 85, buku Tawon 50 → bisa tapi TIDAK cukup, kurang 35 kg disebut dengan dua jalan (hitung fisik / catat barang masuk, atau tandai)',
  dTs.bisa && !dTs.cukup && J(dTs.sumber) === J([{ merk: 'Tawon', kg: 85, diWadah: 55, diKarung: 30, buku: 50, kurang: 35, tanpaBuku: false }]) && J(dTs.kolam) === J([{ merk: 'Tawon', kg: 30 }])
  && J(dTs.kurang.map(function (x) { return x.merk + ' ' + x.kurang; })) === J(['Tawon 35']) && /buku Tawon kurang 35 kg — hitung fisik \/ catat barang masuk dulu, atau tandai untuk dicocokkan/.test(dTs.alasan), J(dTs));
ok('aktifkan wadah yang tidak bisa DITOLAK tanpa perluTandai & tanpa dokumen: belum dicocokkan, bagian minus, bukan wadah', (function () { var a = wbSusunAktifkan('Kosong Satu', W), b = wbSusunAktifkan('Campur Dua', W), c = wbSusunAktifkan('Bukan', W);
  return /belum pernah dicocokkan/.test(a.tolak || '') && !a.perluTandai && !a.dokumen && /minus/.test(b.tolak || '') && !b.perluTandai && !b.dokumen && /bukan wadah/.test(c.tolak || ''); })());

// ---- 2 · dua angka satu kotak: wadah BELUM aktif (7a)
var cTs = chipL('Tawon Super'); var bebasTs = B2(cTs.sisa * 0.82); var SW = wbSelisihWadah('Tawon Super', s0(), cTs.sisa);
ok('selisih wadah belum aktif: bebas dijual = langit-langit buku Tawon 50 kg (' + cTs.sisa + ' L = ' + bebasTs + ' kg) vs isi kotak 55 kg → "lebih di kotak" ' + B2(55 - bebasTs) + ' kg, mengajak mengaktifkan (kalimat pendek a9a1499)',
  cTs.sisa === Math.floor(50 / cTs.rasio * 10) / 10 && SW.ada && SW.baris.length === 1 && SW.baris[0].jenis === 'buku-merek' && SW.baris[0].selisihKg === B2(55 - bebasTs) && SW.baris[0].selisihKg > 0
  && SW.teks === 'bebas dijual ' + String(cTs.sisa).replace('.', ',') + ' L (buku Tawon 50 kg) ≠ isi kotak ±55 kg — selisih ' + kgT(55 - bebasTs) + ' lebih di kotak → aktifkan buku wadah (Stok › Wadah literan)', J([cTs.sisa, SW]));
var SWc = wbSelisihWadah('Campur Dua', s0(), chipL('Campur Dua').sisa);
ok('arah sebaliknya (Campur Dua: kotak 1,8 kg, buku Kumala 200) → "lebih di buku"; wadah belum dicocokkan / bukan wadah → ada:false', SWc.ada && SWc.baris[0].selisihKg < 0 && / lebih di buku → /.test(SWc.teks) && !wbSelisihWadah('Kosong Satu', s0(), 0).ada && !wbSelisihWadah('Bukan', s0(), 0).ada, J(SWc));

// ---- 3 · aktivasi W5 dengan TANDAI (buku kurang → dua ketukan)
var T0 = wbSusunAktifkan('Tawon Super', W);
ok('aktifkan W5 tanpa tandai: DITOLAK dengan kalimat kekurangan + perluTandai [{Tawon, buku 50, butuh 85, kurang 35}] — tidak ada dokumen', !!T0.tolak && /buku Tawon kurang 35 kg/.test(T0.tolak) && J(T0.perluTandai) === J([{ merk: 'Tawon', buku: 50, butuh: 85, kurang: 35 }]) && !T0.dokumen, J(T0));
var v0 = nilai(), laba0 = laba(), t0 = MEREK.map(tump);
var T1 = wbSusunAktifkan('Tawon Super', W, { tandai: true }); var t1b = dok(T1, 'batchMasuk'), t1p = dok(T1, 'produksiKemasan'), t1w = dok(T1, 'wadahLiteran');
ok('aktifkan W5 dengan TANDAI: satu batch lahir (buku wadah + buku karung belakang Tawon bertanda karungBelakang & merkAsal, 0 kg), pindah isi 55 kg Tawon → Wadah Tawon Super BERTANDA perluCocokkan + selisihKg 35 + selisihPerMerk {Tawon: 35}, titik samakan isi (komposisi {Tawon: 55}), pindah karung lama 30 kg → buku karung belakang TANPA tanda (kekurangan sudah habis di pindah pertama), karungIsi Tawon 0 + karungIsi kunci baru 30',
  !T1.tolak && T1.tandai === true && t1b.length === 1 && t1b[0].lahirBuku === true && t1b[0].stokAwal === true && t1b[0].pemasok === 'LAHIR BUKU' && J(t1b[0].merkList.map(function (r) { return [r.merk, r.stokWadah || '', r.karungBelakang || '', r.merkAsal || '', r.totalKg, r.satuan]; })) === J([['Wadah Tawon Super', 'Tawon Super', '', '', 0, 'lahir'], [KB('Tawon Super', 'Tawon'), '', 'Tawon Super', 'Tawon', 0, 'lahir']])
  && t1p.length === 2 && J(t1p[0].sumberList) === J([{ merk: 'Tawon', kg: 55 }]) && t1p[0].merkTujuan === 'Wadah Tawon Super' && t1p[0].perluCocokkan === true && t1p[0].selisihKg === 35 && J(t1p[0].selisihPerMerk) === J({ Tawon: 35 }) && t1p[0].pindahAwalWadah === 'Tawon Super' && t1p[0].hppSumberPerKgDipakai === 12500 && t1p[0].hppPerUnit === 55 * 12500 && t1p[0].dariTakar === true && t1p[0].jadiKarungUtuh === true
  && J(t1p[1].sumberList) === J([{ merk: 'Tawon', kg: 30 }]) && t1p[1].merkTujuan === KB('Tawon Super', 'Tawon') && !t1p[1].perluCocokkan && t1p[1].bukaKarung === 'Tawon Super' && t1p[1].merkAsal === 'Tawon' && t1p[1].pindahAwalWadah === 'Tawon Super'
  && J(t1w.map(function (d) { return [d.tipe, d.merk || d.wadah, d.isiKg]; })) === J([['isi', 'Tawon Super', 55], ['karungIsi', 'Tawon', 0], ['karungIsi', KB('Tawon Super', 'Tawon'), 30]]) && t1w[0].pindahAwal === true && t1w[0].stokWadah === 'Wadah Tawon Super' && J(t1w[0].komposisi) === J({ Tawon: 55 }) && t1w[1].wadah === 'Tawon Super' && t1w[1].pindahAwal === true && t1w[2].bukuBelakang === true && t1w[2].merkAsal === 'Tawon' && t1w[2].wadah === 'Tawon Super'
  && T1.rp === 85 * 12500 && /DITANDAI untuk dicocokkan/.test(T1.patch.kabar) && T1.patch.kabarAwas === true, J(T1));
terapkanKeCache(T1.dokumen || []);
var KBt = wbKarungBelakang('Tawon Super', 'Tawon');
ok('sesudah aktivasi W5: buku Tawon −35 (dibiarkan minus), Wadah Tawon Super 55 @12.500, Karung belakang Tawon Super · Tawon 30 (buku = kolam, lahir, penuh 50), nilai stok & laba tidak berubah, tumpukan Tawon tetap (−35, sudah minus sebelumnya)',
  B2(buku('Tawon')) === -35 && buku('Wadah Tawon Super') === 55 && hpp('Wadah Tawon Super') === 12500 && KBt.lahir && KBt.bukuKg === 30 && KBt.kolamKg === 30 && KBt.diketahui && KBt.selisihKg === 0 && KBt.penuhKg === 50 && KBt.hpp === 12500 && nilai() === v0 && laba() === laba0 && tump('Tawon') === t0[3] && tump('Tawon') === -35 && wbAktif('Tawon Super'), J([buku('Tawon'), buku('Wadah Tawon Super'), KBt, nilai(), v0, tump('Tawon'), t0]));
var PT0 = wbPindahTembusBelumCocok();
ok('pindah bertanda masuk daftar belum dicocokkan atas NAMA MEREK ASAL: Tawon 35 kg, jenis takar, wadah Tawon Super, hari & jam ini, oleh kosong (toleran — tanpa atribusi)', PT0.length === 1 && PT0[0].nama === 'Tawon' && PT0[0].selisihKg === 35 && PT0[0].jenis === 'takar' && PT0[0].wadah === 'Tawon Super' && PT0[0].tanggal === '2026-09-21' && PT0[0].jam === '10:00' && PT0[0].oleh === '' && String(PT0[0].id) === String(t1p[0].id), J(PT0));
ok('sesudah aktif, selisih W5: kolam karung belakang = buku → ada:false', !wbSelisihWadah('Tawon Super', s0()).ada);

// ---- 4 · aktivasi W1 (cukup, karung lama ikut jadi buku) & W2 (isi 0)
var v1 = nilai(), laba1 = laba(), t1 = MEREK.map(tump), bl1 = MEREK.map(buku);
var A1 = wbSusunAktifkan('IR64 Apex', W); var a1b = dok(A1, 'batchMasuk'), a1p = dok(A1, 'produksiKemasan'), a1w = dok(A1, 'wadahLiteran');
ok('aktifkan W1 IR64 Apex (cukup): lahir 2 buku (wadah + karung belakang Kumala), pindah Kumala 20 + NG 30 → Wadah IR64 Apex modal rata-rata tertimbang 11.600/kg TANPA tanda, titik samakan komposisi {Kumala 20, NG 30}, karung lama Kumala 50 → buku karung belakang (karungIsi Kumala 0 + karungIsi kunci 50), modal ikut 1.130.000',
  !A1.tolak && A1.tandai === false && a1b.length === 1 && a1b[0].merkList.length === 2 && a1b[0].merkList[0].merk === 'Wadah IR64 Apex' && a1b[0].merkList[0].stokWadah === 'IR64 Apex' && a1b[0].merkList[1].merk === KB('IR64 Apex', 'Kumala') && a1b[0].merkList[1].karungBelakang === 'IR64 Apex' && a1b[0].merkList[1].merkAsal === 'Kumala'
  && a1p.length === 2 && J(a1p[0].sumberList) === J([{ merk: 'Kumala', kg: 20 }, { merk: 'NG', kg: 30 }]) && a1p[0].merkTujuan === 'Wadah IR64 Apex' && Math.round(a1p[0].hppSumberPerKgDipakai) === 11600 && a1p[0].hppPerUnit === 580000 && !a1p[0].perluCocokkan && a1p[0].pindahAwalWadah === 'IR64 Apex'
  && J(a1p[1].sumberList) === J([{ merk: 'Kumala', kg: 50 }]) && a1p[1].merkTujuan === KB('IR64 Apex', 'Kumala') && a1p[1].hppPerUnit === 550000 && a1p[1].bukaKarung === 'IR64 Apex' && a1p[1].merkAsal === 'Kumala' && !a1p[1].perluCocokkan
  && a1w.length === 3 && a1w[0].tipe === 'isi' && a1w[0].isiKg === 50 && J(a1w[0].komposisi) === J({ Kumala: 20, NG: 30 }) && a1w[0].stokWadah === 'Wadah IR64 Apex' && a1w[0].pindahAwal === true && a1w[1].tipe === 'karungIsi' && a1w[1].merk === 'Kumala' && a1w[1].isiKg === 0 && a1w[1].wadah === 'IR64 Apex' && a1w[2].tipe === 'karungIsi' && a1w[2].merk === KB('IR64 Apex', 'Kumala') && a1w[2].isiKg === 50 && a1w[2].bukuBelakang === true
  && A1.rp === 1130000 && /IR64 Apex kini punya buku sendiri: isi 50 kg \+ karung di belakangnya Kumala 50 kg \(buku sendiri\)/.test(A1.patch.kabar) && A1.patch.kabarAwas === false, J(A1));
terapkanKeCache(A1.dokumen || []);
var KBa = wbKarungBelakang('IR64 Apex', 'Kumala');
ok('sesudah aktivasi W1: Wadah IR64 Apex 50 kg @11.600, Karung belakang IR64 Apex · Kumala 50 kg @11.000 (buku = kolam), NG −30, Kumala −70, Angsa/Tawon/Beo tetap; nilai stok, laba, tumpukan tiap merek TIDAK bergeser; kolam lama Kumala bernama merek tertutup (0)',
  buku('Wadah IR64 Apex') === 50 && Math.round(hpp('Wadah IR64 Apex')) === 11600 && KBa.bukuKg === 50 && KBa.kolamKg === 50 && KBa.selisihKg === 0 && KBa.hpp === 11000 && KBa.penuhKg === 50 && J(MEREK.map(function (m, i) { return B2(buku(m) - bl1[i]); })) === J([-30, -70, 0, 0, 0])
  && nilai() === v1 && laba() === laba1 && J(MEREK.map(tump)) === J(t1) && karungBelakang('Kumala', 'IR64 Apex').diketahui && karungBelakang('Kumala', 'IR64 Apex').sisaMentahKg === 0 && wbKarungBelakangWadah('IR64 Apex').length === 1 && wbKarungBelakangWadah('IR64 Apex')[0].merk === 'Kumala',
  J([buku('Wadah IR64 Apex'), hpp('Wadah IR64 Apex'), KBa, MEREK.map(buku), nilai(), v1, MEREK.map(tump), t1]));
var twAp = tinggiWadah('IR64 Apex', null); var cAp = chipL('IR64 Apex'); var dAp2 = wbDaftarAktivasi().find(function (x) { return x.W === 'IR64 Apex'; });
ok('sesudah aktif: tinggi wadah = buku (50 kg, stokSendiri), chip literan IR64 Apex = buku ÷ rasio = 60,9 L (Rp12.000/L), daftar aktivasi menyebut "sudah punya buku sendiri" (bisa:false), aktivasi kedua ditolak',
  twAp.stokSendiri === true && twAp.sisaNyataKg === 50 && !!cAp && cAp.sisa === Math.floor(50 / cAp.rasio * 10) / 10 && cAp.sisa === 60.9 && cAp.harga === 12000 && dAp2.aktif && !dAp2.bisa && dAp2.alasan === 'sudah punya buku sendiri' && !!wbSusunAktifkan('IR64 Apex', W).tolak, J([twAp, cAp && [cAp.sisa, cAp.rasio, cAp.harga], dAp2]));
var KTa = wbKomposisiTurunan('IR64 Apex');
ok('komposisi turunan W1 sesudah aktivasi = komposisi awal titik samakan: NG 30 kg (60 %) + Kumala 20 kg (40 %), Σ = buku 50 (bukan angka kedua), 61 L, belum ada isi ulang → terakhir null; banding 0,6 : 0,4 disederhanakan jadi "NG 3 : Kumala 2" (pengali terkecil yang membulatkan)',
  KTa.stokSendiri && KTa.diketahui && KTa.totalKg === 50 && J(KTa.daftar.map(function (x) { return [x.merk, x.kg, B3(x.porsi)]; })) === J([['NG', 30, 0.6], ['Kumala', 20, 0.4]]) && KTa.terakhir === null && KTa.banding === 'NG 3 : Kumala 2' && KTa.nama === KTa.banding && KTa.liter === 61, J(KTa));
var A2 = wbSusunAktifkan('Angsa', W);
ok('aktifkan W2 Angsa (isi 0): cuma batch lahir + titik samakan 0 kg — tidak ada pindah buku, modal 0', !A2.tolak && dok(A2, 'batchMasuk').length === 1 && dok(A2, 'batchMasuk')[0].merkList.length === 1 && !dok(A2, 'produksiKemasan').length && dok(A2, 'wadahLiteran').length === 1 && dok(A2, 'wadahLiteran')[0].isiKg === 0 && A2.rp === 0 && A2.tandai === false, J(A2));
terapkanKeCache(A2.dokumen || []);
ok('W2 aktif dengan buku 0 (lahir), tinggi 0, chip 0 L', wbAktif('Angsa') && buku('Wadah Angsa') === 0 && !!hitungStokKarungPerMerk()['Wadah Angsa'] && tinggiWadah('Angsa', null).sisaNyataKg === 0 && !!chipL('Angsa') && chipL('Angsa').sisa === 0, J([buku('Wadah Angsa'), tinggiWadah('Angsa', null), chipL('Angsa')]));
var idM = MEREK.map(function (m, i) { var kb = 0, bag = 0; ['IR64 Apex', 'Angsa', 'Tawon Super'].forEach(function (Wn) { wbKarungBelakangWadah(Wn).forEach(function (k) { if (k.merk === m) kb += k.bukuKg; }); wbKomposisiTurunan(Wn).daftar.forEach(function (x) { if (x.merk === m) bag += x.kg; }); }); return [m, B2(b0[i]), B2(buku(m) + kb + bag)]; });
ok('identitas per merek asal sesudah tiga aktivasi: buku merek SEBELUM = buku merek sekarang + Σ buku karung belakang merek itu + Σ bagian merek itu di wadah aktif (komposisi turunan) — NG 491,8, Kumala 200, Angsa 200, Tawon 50, Beo 25', idM.every(function (x) { return x[1] === x[2]; }), J(idM));

// ---- 5 · wbDokBukaKB: buka karung di belakang wadah aktif (1)
var v2 = nilai(), laba2 = laba(), tNG2 = tump('NG'), bNG2 = B2(buku('NG'));
var B1 = wbDokBukaKB('Angsa', 'NG', 2, W); var b1b = dok(B1, 'batchMasuk'), b1p = dok(B1, 'produksiKemasan'), b1w = dok(B1, 'wadahLiteran');
ok('buka 2 karung NG di belakang Angsa: buku "Karung belakang Angsa · NG" LAHIR (baris 0 kg bertanda karungBelakang + merkAsal), pindah buku NG 100 kg → kunci itu (modal 12.000 ikut, bukaKarung, merkAsal, tanpa tanda), dua catatan karung bernama kunci (merkAsal NG, 50 kg, wadah Angsa, bukuBelakang, produksiId = pindah)',
  !B1.tolak && B1.n === 2 && B1.berat === 50 && B1.kg === 100 && B1.kunci === KB('Angsa', 'NG') && B1.buku === bNG2 && B1.sesudahKg === B2(bNG2 - 100) && B1.kurang === 0 && B1.tandai === false && B1.dokumen.length === 4
  && b1b.length === 1 && b1b[0].merkList.length === 1 && b1b[0].merkList[0].merk === KB('Angsa', 'NG') && b1b[0].merkList[0].karungBelakang === 'Angsa' && b1b[0].merkList[0].merkAsal === 'NG' && b1b[0].merkList[0].satuan === 'lahir' && b1b[0].merkList[0].totalKg === 0 && b1b[0].merkList[0].subtotalHarga === 0
  && b1p.length === 1 && J(b1p[0].sumberList) === J([{ merk: 'NG', kg: 100 }]) && b1p[0].merkTujuan === KB('Angsa', 'NG') && b1p[0].hppSumberPerKgDipakai === 12000 && b1p[0].hppPerUnit === 1200000 && b1p[0].bukaKarung === 'Angsa' && b1p[0].merkAsal === 'NG' && !b1p[0].perluCocokkan && b1p[0].selisihKg === undefined
  && b1w.length === 2 && b1w.every(function (d) { return d.tipe === 'karung' && d.merk === KB('Angsa', 'NG') && d.merkAsal === 'NG' && d.kg === 50 && d.wadah === 'Angsa' && d.bukuBelakang === true && String(d.produksiId) === String(b1p[0].id) && !d.otomatis; }), J(B1));
terapkanKeCache(B1.dokumen || []);
var KBn = wbKarungBelakang('Angsa', 'NG');
ok('sesudah buka: buku NG −100, buku karung belakang 100 = kolam 100 (2 karung), nilai stok & laba tidak berubah, TUMPUKAN NG TURUN 100 kg di buku (keputusan owner)', B2(buku('NG') - bNG2) === -100 && KBn.lahir && KBn.bukuKg === 100 && KBn.kolamKg === 100 && KBn.selisihKg === 0 && KBn.hpp === 12000 && nilai() === v2 && laba() === laba2 && B2(tump('NG') - tNG2) === -100, J([buku('NG'), bNG2, KBn, nilai(), v2, tump('NG'), tNG2]));
ok('peta buku: kunci karung belakang = buku khusus jenis "belakang" (wadah Angsa, merek NG); merkAsalKunci / wbMerkAsal → NG; beratKarungBuka(kunci) = 50 = berat merek asalnya; tidak masuk daftar merek (stokMerekSaja)',
  J(petaBukuWadah()[KB('Angsa', 'NG')]) === J({ jenis: 'belakang', wadah: 'Angsa', merk: 'NG' }) && merkAsalKunci(KB('Angsa', 'NG')) === 'NG' && wbMerkAsal(KB('Angsa', 'NG')) === 'NG' && wbBukuKhusus(KB('Angsa', 'NG')) && !wbBukuKhusus('NG') && beratKarungBuka(KB('Angsa', 'NG')) === 50 && !stokMerekSaja(hitungStokKarungPerMerk())[KB('Angsa', 'NG')] && !!stokMerekSaja(hitungStokKarungPerMerk())['NG'], J(petaBukuWadah()));
var B2x = wbDokBukaKB('Angsa', 'NG', 1, W); var B7 = wbDokBukaKB('Angsa', 'NG', 7, W); var B8 = wbDokBukaKB('Angsa', 'NG', 1, W, null, B7.dokumen);
ok('buka lagi NG: buku sudah lahir → tanpa batch lahir (pindah + 1 karung); `sesudah` = dokumen kiriman yang sama diperhitungkan: sesudah 7 karung (350 kg) disusun, karung ke-8 kurang → tolak + perluTandai',
  !B2x.tolak && !dok(B2x, 'batchMasuk').length && B2x.dokumen.length === 2 && !B7.tolak && B7.n === 7 && B7.sesudahKg === B2(bNG2 - 450) && !!B8.tolak && !B8.dokumen && B8.perluTandai.length === 1 && B8.perluTandai[0].merk === 'NG' && B8.perluTandai[0].buku === B2(bNG2 - 450) && B8.perluTandai[0].butuh === 50 && B8.perluTandai[0].kurang === B2(50 - (bNG2 - 450)), J([B2x.dokumen.length, B7.sesudahKg, B8]));
var B3 = wbDokBukaKB('Angsa', 'Beo', 2, W);
ok('buka 2 karung Beo (25 kg/karung; buku 25): kurang 25 → DITOLAK dengan kalimat & perluTandai [{Beo, buku 25, butuh 50, kurang 25}], tidak ada dokumen', !!B3.tolak && /^Buku Beo tinggal 25 kg, mau dibuka 2 karung \(50 kg\) — kurang 25 kg\. Catat barang masuk dulu, atau tandai untuk dicocokkan \(buku Beo dibiarkan minus sampai dihitung\)$/.test(B3.tolak) && J(B3.perluTandai) === J([{ merk: 'Beo', buku: 25, butuh: 50, kurang: 25 }]) && !B3.dokumen, J(B3));
var v3 = nilai(); var B4 = wbDokBukaKB('Angsa', 'Beo', 2, W, { tandai: true }); var b4p = dok(B4, 'produksiKemasan'), b4w = dok(B4, 'wadahLiteran');
ok('ketukan kedua TANDAI: pindah Beo 50 kg → Karung belakang Angsa · Beo BERTANDA perluCocokkan + selisihKg 25 + selisihPerMerk {Beo: 25}; dua catatan karung 25 kg; tandai:true, kurang 25', !B4.tolak && B4.tandai === true && B4.kurang === 25 && B4.berat === 25 && dok(B4, 'batchMasuk').length === 1 && b4p.length === 1 && b4p[0].perluCocokkan === true && b4p[0].selisihKg === 25 && J(b4p[0].selisihPerMerk) === J({ Beo: 25 }) && J(b4p[0].sumberList) === J([{ merk: 'Beo', kg: 50 }]) && b4w.length === 2 && b4w.every(function (d) { return d.kg === 25 && d.merkAsal === 'Beo' && d.merk === KB('Angsa', 'Beo'); }), J(B4));
terapkanKeCache(B4.dokumen || []);
var KBb = wbKarungBelakang('Angsa', 'Beo');
ok('sesudah tandai: buku Beo −25 (minus, dibiarkan), karung belakang Beo 50 kg @14.000 (satu karung penuh = 25), beratKarungBuka(kunci Beo) = 25 = berat merek asalnya, nilai stok tetap', B2(buku('Beo')) === -25 && KBb.bukuKg === 50 && KBb.kolamKg === 50 && KBb.hpp === 14000 && KBb.penuhKg === 25 && beratKarungBuka(KB('Angsa', 'Beo')) === 25 && nilai() === v3, J([buku('Beo'), KBb, nilai(), v3]));
ok('buka merek yang tidak ada di buku gudang DITOLAK; n = 0 dibaca 1 karung', /tidak ada di buku gudang/.test(wbDokBukaKB('Angsa', 'Tidak Ada', 1, W).tolak || '') && wbDokBukaKB('Angsa', 'NG', 0, W).n === 1);
var SK1 = susunSamakanKarung(KB('Angsa', 'NG'), '80', W, 'Angsa'), SK2 = susunSamakanKarung(KB('Angsa', 'NG'), '101', W, 'Angsa');
ok('samakan karung belakang berbuku boleh di atas satu karung (buku 100 kg: 80 kg diterima, 101 ditolak); catatannya karungIsi bernama kunci di belakang Angsa', !SK1.tolak && SK1.dokumen.length === 1 && SK1.dokumen[0].data.tipe === 'karungIsi' && SK1.dokumen[0].data.merk === KB('Angsa', 'NG') && SK1.dokumen[0].data.wadah === 'Angsa' && SK1.dokumen[0].data.isiKg === 80 && /di antara 0 dan 100 kg/.test(SK2.tolak || ''), J([SK1, SK2]));
ok('daftar belum dicocokkan kini dua nama merek asal: Beo 25 & Tawon 35', J(wbPindahTembusBelumCocok().map(function (x) { return x.nama + ' ' + x.selisihKg; }).sort()) === J(['Beo 25', 'Tawon 35']), J(wbPindahTembusBelumCocok()));

// ---- 6 · isi ulang TIGA KETUKAN (2)
ok('isi ulang tiga ketukan DITOLAK dengan kalimat: wadah belum aktif (ajak ke daftar aktivasi), bukan wadah, merek kosong, buku wadah dipilih sebagai merek, kg kosong, takaran belum dipilih',
  /belum punya buku sendiri — aktifkan dulu di Stok › Wadah literan/.test(U('Kosong Satu', 'NG', { jenis: 'karung' }).tolak || '') && /bukan wadah/.test(U('Bukan', 'NG', { jenis: 'karung' }).tolak || '') && /Pilih dulu beras/.test(U('Angsa', '', { jenis: 'karung' }).tolak || '')
  && /adalah buku wadah — pilih merek karungnya/.test(U('Angsa', 'Wadah Angsa', { jenis: 'karung' }).tolak || '') && /Ketik berapa kg yang dituang/.test(U('Angsa', 'NG', { jenis: 'kg', kg: '' }).tolak || '') && /Pilih takarannya: 1 karung, ½ karung, atau kg/.test(U('Angsa', 'NG', {}).tolak || ''),
  J([U('Kosong Satu', 'NG', { jenis: 'karung' }), U('Angsa', 'Wadah Angsa', { jenis: 'karung' }), U('Angsa', 'NG', { jenis: 'kg', kg: '' }), U('Angsa', 'NG', {})]));
var v4 = nilai(), laba4 = laba(), tNG4 = tump('NG'), bNG4 = buku('NG');
var U1 = U('Angsa', 'NG', { jenis: 'kg', kg: '12,5' }); var u1w = dok(U1, 'wadahLiteran'), u1p = dok(U1, 'produksiKemasan');
ok('"kg" 12,5 (koma) NG ke Angsa dari karung belakang yang sudah terbuka (100 kg): DUA dokumen — takar (takaran kg, 12,5 kg = 6,9 takar, sumber kunci karung belakang + merkAsal NG, dari Angsa, stokWadah) + pindah buku karung belakang → Wadah Angsa (takarId, merkAsal, modal 12.000 ikut); tidak ada karung dibuka',
  !U1.tolak && U1.dokumen.length === 2 && u1w.length === 1 && u1w[0].tipe === 'takar' && u1w[0].wadah === 'Angsa' && u1w[0].kg === 12.5 && u1w[0].takaran === 'kg' && u1w[0].takar === 6.9 && u1w[0].kgPerTakar === 1.8 && J(u1w[0].sumber) === J([{ merk: KB('Angsa', 'NG'), merkAsal: 'NG', takar: 6.9, kg: 12.5, dari: 'Angsa' }]) && u1w[0].stokWadah === 'Wadah Angsa' && u1p.length === 1 && String(u1w[0].produksiId) === String(u1p[0].id)
  && J(u1p[0].sumberList) === J([{ merk: KB('Angsa', 'NG'), kg: 12.5 }]) && u1p[0].merkTujuan === 'Wadah Angsa' && String(u1p[0].takarId) === String(u1w[0].id) && u1p[0].merkAsal === 'NG' && u1p[0].hppSumberPerKgDipakai === 12000 && u1p[0].hppPerUnit === 150000
  && U1.hitung.kg === 12.5 && U1.hitung.isiBaru === 12.5 && U1.hitung.dibuka === 0 && U1.hitung.sisaKB === 87.5 && U1.hitung.takaran === 'kg' && U1.hitung.takar === 7 && U1.hitung.merk === 'NG' && U1.tandai === false && U1.kurang === 0 && J(U1.pindahBuku) === J(u1p[0])
  && /^Wadah Angsa diisi 12,5 kg NG → isinya ±12,5 kg \(buku wadah\) · dari karung yang sudah terbuka di belakangnya · sisa di karung belakang ±87,5 kg$/.test(U1.patch.kabar) && U1.patch.kabarAwas === false, J(U1));
terapkanKeCache(U1.dokumen || []);
ok('sesudah: buku wadah +12,5 (= tinggi wadah), karung belakang NG 87,5 (buku = kolam), buku & tumpukan NG tidak disentuh, nilai stok & laba tetap, hpp wadah 12.000', buku('Wadah Angsa') === 12.5 && tinggiWadah('Angsa', null).sisaNyataKg === 12.5 && wbKarungBelakang('Angsa', 'NG').bukuKg === 87.5 && wbKarungBelakang('Angsa', 'NG').kolamKg === 87.5 && buku('NG') === bNG4 && tump('NG') === tNG4 && nilai() === v4 && laba() === laba4 && Math.round(hpp('Wadah Angsa')) === 12000,
  J([buku('Wadah Angsa'), tinggiWadah('Angsa', null).sisaNyataKg, wbKarungBelakang('Angsa', 'NG'), buku('NG'), bNG4, nilai(), v4]));
var tKu5 = tump('Kumala'), bKu5 = buku('Kumala'), v5 = nilai();
var U2 = U('Angsa', 'Kumala', { jenis: 'setengah' }); var u2b = dok(U2, 'batchMasuk'), u2p = dok(U2, 'produksiKemasan'), u2w = dok(U2, 'wadahLiteran');
ok('"½ karung" Kumala ke Angsa — belum ada karung Kumala di belakangnya → SATU kiriman lima dokumen: lahir buku karung belakang, pindah Kumala 50 → karung belakang, catatan karung (bukan otomatis), takar 25 kg (takaran setengah, 13,9 takar), pindah 25 kg karung belakang → wadah; dibuka 1, sisa karung belakang 25',
  !U2.tolak && U2.dokumen.length === 5 && u2b.length === 1 && u2b[0].merkList[0].merk === KB('Angsa', 'Kumala') && u2b[0].merkList[0].merkAsal === 'Kumala' && u2p.length === 2 && J(u2p[0].sumberList) === J([{ merk: 'Kumala', kg: 50 }]) && u2p[0].merkTujuan === KB('Angsa', 'Kumala') && u2p[0].bukaKarung === 'Angsa' && J(u2p[1].sumberList) === J([{ merk: KB('Angsa', 'Kumala'), kg: 25 }]) && u2p[1].merkTujuan === 'Wadah Angsa' && u2p[1].hppSumberPerKgDipakai === 11000
  && u2w.length === 2 && u2w[0].tipe === 'karung' && u2w[0].merkAsal === 'Kumala' && u2w[0].kg === 50 && !u2w[0].otomatis && u2w[0].bukuBelakang === true && u2w[1].tipe === 'takar' && u2w[1].takaran === 'setengah' && u2w[1].kg === 25 && u2w[1].takar === 13.9 && u2w[1].sumber[0].merkAsal === 'Kumala' && u2w[1].sumber[0].merk === KB('Angsa', 'Kumala')
  && U2.hitung.dibuka === 1 && U2.hitung.sisaKB === 25 && U2.hitung.isiBaru === 37.5 && U2.hitung.takaran === 'setengah' && /^Wadah Angsa diisi ½ karung Kumala \(25 kg\) → isinya ±37,5 kg \(buku wadah\) · 1 karung Kumala dibuka dari tumpukan gudang: buku Kumala 130 kg → 80 kg · sisa di karung belakang ±25 kg$/.test(U2.patch.kabar), J(U2));
terapkanKeCache(U2.dokumen || []);
ok('sesudah ½ karung: buku Kumala −50 & TUMPUKAN Kumala −50 (satu karung dibuka), karung belakang Kumala 25 (buku = kolam), wadah 37,5, hpp wadah = rata-rata tertimbang (12,5 × 12.000 + 25 × 11.000) / 37,5, nilai stok & laba tetap',
  B2(buku('Kumala') - bKu5) === -50 && B2(tump('Kumala') - tKu5) === -50 && wbKarungBelakang('Angsa', 'Kumala').bukuKg === 25 && wbKarungBelakang('Angsa', 'Kumala').kolamKg === 25 && buku('Wadah Angsa') === 37.5 && Math.abs(hpp('Wadah Angsa') - (12.5 * 12000 + 25 * 11000) / 37.5) < 0.001 && nilai() === v5 && laba() === laba4,
  J([buku('Kumala'), bKu5, tump('Kumala'), tKu5, wbKarungBelakang('Angsa', 'Kumala'), buku('Wadah Angsa'), hpp('Wadah Angsa'), nilai(), v5]));
var KT = wbKomposisiTurunan('Angsa');
ok('komposisi turunan Angsa = riwayat isi ulang sejak titik samakan: Kumala 25 + NG 12,5 → banding "Kumala 2 : NG 1", kg sebanding buku (Σ 37,5), 45,7 L, terakhir = takar ½ karung jam 10:00 (oleh kosong, toleran)',
  KT.banding === 'Kumala 2 : NG 1' && J(KT.daftar.map(function (x) { return [x.merk, x.kg]; })) === J([['Kumala', 25], ['NG', 12.5]]) && KT.totalKg === 37.5 && KT.liter === 45.7 && J(KT.terakhir) === J({ tanggal: '2026-09-21', jam: '10:00', oleh: '', kg: 25, takaran: 'setengah' }) && KT.nama === 'Kumala 2 : NG 1' && KT.teks === 'Kumala 2 : NG 1 · ±37,5 kg ≈ 45,7 L · diisi 10:00', J(KT));
var KTo = denganCacheSementara([{ koleksi: 'wadahLiteran', data: Object.assign({}, u2w[1] || { id: 0 }, { oleh: 'Karyawan Contoh' }) }], function () { return wbKomposisiTurunan('Angsa'); });
ok('atribusi pusat mengisi oleh → "diisi 10:00 oleh Karyawan Contoh"', KTo.terakhir.oleh === 'Karyawan Contoh' && /· diisi 10:00 oleh Karyawan Contoh$/.test(KTo.teks), J(KTo));
var U3 = U('Angsa', 'NG', { jenis: 'karung' });
ok('"1 karung" NG (50 kg) ke Angsa berisi 37,5 → 87,5 melebihi batas menggunung 60 → DITOLAK dengan kalimat (paling banyak ±22,5 kg), tanpa dokumen', !!U3.tolak && /^Kalau dituang 50 kg, wadah Angsa jadi ±87,5 kg — melebihi 60 kg yang muat\. Paling banyak ±22,5 kg \(pilih takaran kg\) — layar tidak memotong diam-diam$/.test(U3.tolak) && !U3.dokumen, J(U3));
var cAn = chipL('Angsa'); var sN = masuk(s0(), cAn, 40); var N1 = simpanNota(Object.assign({}, sN, { cara: 'QRIS' }), W); var n1r = dok(N1, 'penjualan');
ok('jual 40 L dari Angsa (chip 45,7 L Rp13.000): satu baris merkSumber buku wadah, 32,8 kg, Rp520.000', !!cAn && cAn.sisa === 45.7 && !sN.tolak && !N1.tolak && n1r.length === 1 && n1r[0].merkSumber === 'Wadah Angsa' && n1r[0].totalKg === 32.8 && n1r[0].hargaTotal === 520000, J([cAn && cAn.sisa, sN.tolak, N1.tolak, n1r]));
terapkanKeCache(N1.dokumen || []);
var KT2 = wbKomposisiTurunan('Angsa');
ok('sesudah jual: buku wadah 4,7, karung belakang NG 87,5 & Kumala 25 tetap; komposisi turunan menyebar 4,7 kg sebanding (Kumala 3,13 + NG 1,57 = buku) — bukan angka kedua; banding tetap', B2(buku('Wadah Angsa')) === 4.7 && wbKarungBelakang('Angsa', 'NG').bukuKg === 87.5 && wbKarungBelakang('Angsa', 'Kumala').bukuKg === 25 && KT2.totalKg === 4.7 && J(KT2.daftar.map(function (x) { return [x.merk, x.kg]; })) === J([['Kumala', 3.13], ['NG', 1.57]]) && KT2.banding === 'Kumala 2 : NG 1', J([buku('Wadah Angsa'), KT2]));
var U4 = U('Angsa', 'NG', { jenis: 'karung' }); var u4p = dok(U4, 'produksiKemasan');
ok('"1 karung" NG sekarang muat (4,7 + 50 = 54,7): dari karung belakang NG 87,5 → tanpa membuka karung baru; 28 takar, takaran karung; pindah membawa modal 50 × 12.000', !U4.tolak && U4.dokumen.length === 2 && U4.hitung.dibuka === 0 && U4.hitung.sisaKB === 37.5 && U4.hitung.isiBaru === 54.7 && U4.hitung.takar === 28 && dok(U4, 'wadahLiteran')[0].takaran === 'karung' && dok(U4, 'wadahLiteran')[0].kg === 50 && u4p[0].hppPerUnit === 600000 && u4p[0].hppSumberPerKgDipakai === 12000 && /diisi 1 karung NG \(50 kg\) → isinya ±54,7 kg/.test(U4.patch.kabar), J(U4));
var laba6 = laba(); terapkanKeCache(U4.dokumen || []);
ok('sesudah 1 karung: wadah 54,7 = tinggi, karung belakang NG 37,5 (buku = kolam), buku NG tetap, laba tetap', B2(buku('Wadah Angsa')) === 54.7 && B2(tinggiWadah('Angsa', null).sisaNyataKg) === 54.7 && wbKarungBelakang('Angsa', 'NG').bukuKg === 37.5 && wbKarungBelakang('Angsa', 'NG').kolamKg === 37.5 && buku('NG') === bNG4 && laba() === laba6, J([buku('Wadah Angsa'), wbKarungBelakang('Angsa', 'NG'), buku('NG'), bNG4]));
var v7 = nilai(); var U5 = U('IR64 Apex', 'Kumala', { jenis: 'kg', kg: '10' }); terapkanKeCache(U5.dokumen || []); var KT3 = wbKomposisiTurunan('IR64 Apex');
ok('"kg" 10 Kumala ke IR64 Apex (50 → 60 = tepat batas, boleh) dari karung belakang Kumala 50 → 40; komposisi turunan jadi Kumala 30 : NG 30 → "Kumala 1 : NG 1", terakhir 10 kg takaran kg; nilai stok tetap', !U5.tolak && U5.dokumen.length === 2 && buku('Wadah IR64 Apex') === 60 && wbKarungBelakang('IR64 Apex', 'Kumala').bukuKg === 40 && KT3.banding === 'Kumala 1 : NG 1' && J(KT3.daftar.map(function (x) { return [x.merk, x.kg]; })) === J([['Kumala', 30], ['NG', 30]]) && KT3.terakhir.kg === 10 && KT3.terakhir.takaran === 'kg' && nilai() === v7, J([U5.tolak, buku('Wadah IR64 Apex'), KT3, nilai(), v7]));
ok('wadah belum aktif → komposisi turunan = komposisi 27 (Campur Dua: bagian positif Kumala saja, 1,8 kg); belum dicocokkan → "isi belum ditandai"', (function () { var k = wbKomposisiTurunan('Campur Dua'); var z = wbKomposisiTurunan('Kosong Satu'); return !k.stokSendiri && k.diketahui && J(k.daftar.map(function (x) { return [x.merk, x.kg]; })) === J([['Kumala', 1.8]]) && k.banding === '' && k.nama === 'Kumala' && k.terakhir === null && !z.diketahui && z.nama === 'isi belum ditandai' && !z.daftar.length && z.teks === 'isi belum ditandai'; })(), J([wbKomposisiTurunan('Campur Dua'), wbKomposisiTurunan('Kosong Satu')]));

// ---- 7 · panel − / + takar lama di wadah aktif (8)
var P1 = susunTakarWadah('Angsa', [{ merk: 'NG', takar: 2 }], W, s0()); var p1w = dok(P1, 'wadahLiteran'), p1p = dok(P1, 'produksiKemasan');
ok('panel − / + takar di wadah aktif: sumber merek biasa NG dinormalkan ke kunci karung belakang (merkAsal NG, dari Angsa, bukuBelakang), takar 2 = 3,6 kg dari karung belakang → pindah buku kunci → wadah; takaran "takar"; tanpa karung baru; kabar menyebut karung belakang',
  !P1.tolak && P1.hitung.sumber.length === 1 && P1.hitung.sumber[0].merk === KB('Angsa', 'NG') && P1.hitung.sumber[0].merkAsal === 'NG' && P1.hitung.sumber[0].bukuBelakang === true && P1.hitung.sumber[0].dari === 'Angsa' && P1.hitung.sumber[0].bukaKarung === 0 && P1.hitung.sumber[0].karung.diketahui
  && p1w.length === 1 && p1w[0].takaran === 'takar' && J(p1w[0].sumber) === J([{ merk: KB('Angsa', 'NG'), takar: 2, kg: 3.6, dari: 'Angsa', merkAsal: 'NG' }]) && p1p.length === 1 && J(p1p[0].sumberList) === J([{ merk: KB('Angsa', 'NG'), kg: 3.6 }]) && p1p[0].merkTujuan === 'Wadah Angsa' && !P1.tandai && P1.dokumen.length === 2 && !dok(P1, 'batchMasuk').length
  && /BUKU: karung belakang NG −3,6 kg → Wadah Angsa \+3,6 kg \(modal ikut\)/.test(P1.patch.kabar) && !P1.patch.kabarAwas, J(P1));
var P2 = denganCacheSementara([{ koleksi: 'wadahLiteran', data: { id: 8801, tanggal: '2026-09-21', jam: '10:30', tipe: 'karung', merk: 'NG', kg: 50, wadah: 'Angsa' } }], function () { return susunTakarWadah('Angsa', [{ merk: 'NG', takar: 2 }], W, s0()); });
ok('karung LAMA bernama merek (dibuka sebelum putaran ini) yang masih cukup tetap dipakai dulu: sumber NG apa adanya (dari Angsa, bukan buku belakang), pindah dari buku NG langsung', !P2.tolak && P2.hitung.sumber[0].merk === 'NG' && !P2.hitung.sumber[0].bukuBelakang && P2.hitung.sumber[0].dari === 'Angsa' && P2.hitung.sumber[0].bukaKarung === 0 && J(dok(P2, 'produksiKemasan')[0].sumberList) === J([{ merk: 'NG', kg: 3.6 }]) && dok(P2, 'wadahLiteran')[0].sumber[0].merkAsal === undefined, J(P2));

// ---- 8 · cek wadah tutup toko (6)
var CH0 = wbCekHari('2026-09-20');   // jam kotak pasir 21 Sep 10.00 < 12.00 → cek milik hari dagang 20 Sep (audit 39b no. 1)
ok('cek hari ini sebelum dicek: 3 wadah aktif, 0 dicek, belum = IR64 Apex, Angsa, Tawon Super (urutan daftar); buku Angsa 54,7', CH0.iso === '2026-09-20' && CH0.nAktif === 3 && CH0.nDicek === 0 && J(CH0.belum) === J(['IR64 Apex', 'Angsa', 'Tawon Super']) && CH0.daftar.length === 5 && CH0.daftar[1].W === 'Angsa' && CH0.daftar[1].bukuKg === 54.7 && !CH0.daftar[1].dicek && CH0.daftar[1].hasil === '' && CH0.daftar[1].bukuSaatCek === null, J(CH0));
var C1 = wbSusunCek('Angsa', 'sesuai', W), C2 = wbSusunCek('IR64 Apex', 'lupa', W), C3 = wbSusunCek('Kosong Satu', 'kosong', W), C3b = wbSusunCek('Kosong Satu', 'sesuai', W);
ok('cek "sesuai" Angsa: satu catatan cek (hasil, bukuKg 54,7, stokWadah), tidak awas; "lupa isi ulang" IR64 Apex: satu catatan, awas + ajakan mencatat tiga ketukan; "dikosongkan" wadah belum aktif DITOLAK; "sesuai" wadah belum aktif boleh (tanpa stokWadah, buku 0); hasil asing / bukan wadah ditolak',
  !C1.tolak && C1.dokumen.length === 1 && C1.dokumen[0].koleksi === 'wadahLiteran' && C1.dokumen[0].data.tipe === 'cek' && C1.dokumen[0].data.wadah === 'Angsa' && C1.dokumen[0].data.hasil === 'sesuai' && C1.dokumen[0].data.bukuKg === 54.7 && C1.dokumen[0].data.stokWadah === 'Wadah Angsa' && C1.hasil === 'sesuai' && C1.sisihKg === 0 && C1.patch.kabarAwas === false && /^Cek wadah Angsa 10:00: sesuai — isi kotak = buku ±54,7 kg$/.test(C1.patch.kabar)
  && !C2.tolak && C2.dokumen.length === 1 && C2.dokumen[0].data.hasil === 'lupa' && C2.patch.kabarAwas === true && /lupa isi ulang — catat isi ulangnya sekarang \(tiga ketukan\), supaya buku ikut naik/.test(C2.patch.kabar)
  && /belum punya buku sendiri — "dikosongkan" baru bisa dicatat sesudah wadahnya aktif/.test(C3.tolak || '') && !C3.dokumen && !C3b.tolak && C3b.dokumen.length === 1 && !C3b.dokumen[0].data.stokWadah && C3b.dokumen[0].data.bukuKg === 0
  && /Pilih hasil ceknya: sesuai · lupa isi ulang · dikosongkan/.test(wbSusunCek('Angsa', 'apa', W).tolak || '') && /bukan wadah/.test(wbSusunCek('Bukan', 'sesuai', W).tolak || ''), J([C1, C2, C3, C3b]));
terapkanKeCache((C1.dokumen || []).concat(C2.dokumen || [], C3b.dokumen || []));
var hW7 = hpp('Wadah Angsa'), laba7 = laba(), tK7 = MEREK.map(tump); var C4 = wbSusunCek('Angsa', 'kosong', W); var c4b = dok(C4, 'batchMasuk'), c4p = dok(C4, 'produksiKemasan'), c4w = dok(C4, 'wadahLiteran');
ok('cek "dikosongkan" Angsa = sisihkan SELURUH buku (54,7 kg) ke karung wadah tanpa timbang + catatan cek: lahir Karung wadah Angsa, pindah 54,7 kg (sisihWadah, modal wadah ikut), karung sisihan (lepas, asal wadah, sisih), cek kosong; sisihKg 54,7; awas',
  !C4.tolak && C4.hasil === 'kosong' && C4.sisihKg === 54.7 && C4.dokumen.length === 4 && c4b.length === 1 && c4b[0].merkList[0].merk === 'Karung wadah Angsa' && c4b[0].merkList[0].karungWadah === 'Angsa' && c4p.length === 1 && J(c4p[0].sumberList) === J([{ merk: 'Wadah Angsa', kg: 54.7 }]) && c4p[0].merkTujuan === 'Karung wadah Angsa' && c4p[0].sisihWadah === 'Angsa' && Math.abs(c4p[0].hppSumberPerKgDipakai - hW7) < 0.001
  && c4w.length === 2 && c4w[0].tipe === 'karung' && c4w[0].merk === 'Karung wadah Angsa' && c4w[0].kg === 54.7 && c4w[0].lepas === true && c4w[0].asal === 'wadah' && c4w[0].sisih === true && c4w[1].tipe === 'cek' && c4w[1].hasil === 'kosong' && c4w[1].bukuKg === 54.7 && c4w[1].stokWadah === 'Wadah Angsa'
  && /dikosongkan — 54,7 kg disisihkan ke karung wadahnya tanpa timbang, kotak jadi 0/.test(C4.patch.kabar) && C4.patch.kabarAwas === true, J(C4));
terapkanKeCache(C4.dokumen || []);
ok('sesudah dikosongkan: wadah 0 (chip 0 L), karung wadah Angsa 54,7 (buku & kolam), karung belakang NG/Kumala/Beo tidak disentuh, laba & tumpukan tiap merek tetap; cek "dikosongkan" lagi cuma mencatat cek (buku sudah 0)',
  buku('Wadah Angsa') === 0 && chipL('Angsa').sisa === 0 && B2(wbKarungWadah('Angsa').bukuKg) === 54.7 && B2(wbKarungWadah('Angsa').sisaKg) === 54.7 && wbKarungBelakang('Angsa', 'NG').bukuKg === 37.5 && wbKarungBelakang('Angsa', 'Kumala').bukuKg === 25 && wbKarungBelakang('Angsa', 'Beo').bukuKg === 50 && laba() === laba7 && J(MEREK.map(tump)) === J(tK7)
  && (function () { var r = wbSusunCek('Angsa', 'kosong', W); return !r.tolak && r.dokumen.length === 1 && r.sisihKg === 0 && /menurut buku kotaknya memang sudah kosong/.test(r.patch.kabar); })(), J([buku('Wadah Angsa'), wbKarungWadah('Angsa'), laba(), laba7, MEREK.map(tump), tK7]));
var CH1 = wbCekHari('2026-09-20'); var chA = CH1.daftar.find(function (x) { return x.W === 'Angsa'; }), chI = CH1.daftar.find(function (x) { return x.W === 'IR64 Apex'; }), chK = CH1.daftar.find(function (x) { return x.W === 'Kosong Satu'; });
ok('cek hari dagang 20 Sep sesudahnya (ditulis 21 Sep 10.00, sebelum jam 12 = cek hari kemarin; hari 19 & 21 nol): Angsa dicek "Dikosongkan" 10:00 (buku saat cek 54,7, oleh kosong toleran), IR64 Apex "Lupa isi ulang", Kosong Satu "Sesuai" walau belum aktif; 3 dicek, belum = Tawon Super; kemarin nol',
  chA.dicek && chA.hasil === 'kosong' && chA.hasilTeks === 'Dikosongkan' && chA.jam === '10:00' && chA.oleh === '' && chA.bukuSaatCek === 54.7 && chA.bukuKg === 0 && chI.dicek && chI.hasilTeks === 'Lupa isi ulang' && chK.dicek && chK.hasilTeks === 'Sesuai' && !chK.aktif && CH1.nDicek === 3 && CH1.nAktif === 3 && J(CH1.belum) === J(['Tawon Super']) && wbCekHari('2026-09-19').nDicek === 0 && wbCekHari('2026-09-21').nDicek === 0, J(CH1));
var kap = susunKapur(KINI).baris.map(function (x) { return x.isi; }).join(' | ');
ok('Papan Kapur: tiga baris cek (dikosongkan · lupa isi ulang · sesuai), buka karung berbuku menyebut tumpukan turun di buku, tanda KURANG pada pindah bertanda, aktivasi karung terbuka jadi buku sendiri, isi ulang = takar ke stok wadah; catatan karung/karungIsi bagian aktivasi & buka berbuku tidak digandakan',
  /Cek wadah Angsa tutup toko: dikosongkan/.test(kap) && /Cek wadah IR64 Apex tutup toko: lupa isi ulang/.test(kap) && /Cek wadah Kosong Satu tutup toko: sesuai/.test(kap) && /Karung NG dibuka di belakang wadah Angsa — tumpukan gudang turun di buku: NG 100 kg → Karung belakang Angsa · NG \(modal ikut\)/.test(kap)
  && /Karung Beo dibuka di belakang wadah Angsa[^|]*buku sumber KURANG 25 kg, DITANDAI untuk dicocokkan/.test(kap) && /Pindahan awal stok wadah IR64 Apex: karung terbuka di belakangnya jadi buku sendiri: Kumala 50 kg/.test(kap) && /Takar ke stok wadah: Karung belakang Angsa · NG 12,5 kg → Wadah Angsa \(modal ikut\)/.test(kap)
  && !/Karung Karung belakang/.test(kap) && !/Karung terbuka Karung belakang/.test(kap) && !/Karung terbuka Kumala disamakan/.test(kap), kap);

// ---- 9 · karung otomatis lewat panel, buka karung dari layar Stok, dua karung dibuka sekaligus
var P3 = susunTakarWadah('Angsa', [{ merk: 'Kumala', takar: 20 }], W, s0()); var p3p = dok(P3, 'produksiKemasan'), p3w = dok(P3, 'wadahLiteran');
ok('panel takar 20 × Kumala (36 kg) > karung belakang Kumala 25 → 39c (owner 30 Sep): karung di belakang DIHABISKAN dulu — dituang SEADANYA 25 kg (takar bertanda seadanya + kgMinta 36, pindah 25 kg karung belakang → wadah), TIDAK membuka karung baru (gudang Kumala tetap 80, tanpa catatan karung / batch); kabarnya menyebut SEADANYA & karung bersih 0; karung baru baru ditanya sesudahnya (bukaKarung 1)',
  !P3.tolak && P3.dokumen.length === 2 && p3p.length === 1 && J(p3p[0].sumberList) === J([{ merk: KB('Angsa', 'Kumala'), kg: 25 }]) && p3p[0].merkTujuan === 'Wadah Angsa' && p3w.length === 1 && p3w[0].tipe === 'takar' && p3w[0].kg === 25 && p3w[0].sumber[0].seadanya === true && p3w[0].sumber[0].kgMinta === 36
  && J(P3.gudang) === J([]) && P3.hitung.sumber[0].seadanya === true && P3.hitung.sumber[0].bukaKarung === 0 && P3.hitung.sumber[0].kurangKg === 11 && !P3.tandai && /SEADANYA: karung Kumala tinggal 25 kg dari 36 kg yang diminta/.test(P3.patch.kabar) && /bersih 0/.test(P3.patch.kabar)
  && denganCacheSementara(P3.dokumen, function () { var h = hitungTakar('Angsa', [{ merk: 'Kumala', takar: 20 }], s0()); return h.sumber[0].bukaKarung === 1 && !h.sumber[0].seadanya && h.sumber[0].kg === 36; }), J(P3));
var P4 = susunTakarWadah('Angsa', [{ merk: 'Tawon', takar: 2 }], W, s0()); var P4t = susunTakarWadah('Angsa', [{ merk: 'Tawon', takar: 2 }], W, s0(), { tandai: true });
ok('panel takar dari merek yang bukunya minus (Tawon −35): karung baru perlu dibuka → tolak + perluTandai [{Tawon, buku −35, butuh 50, kurang 85}]; dengan tandai → lahir + pindah bertanda, tandai:true, kurang 85', !!P4.tolak && !P4.dokumen && J(P4.perluTandai) === J([{ merk: 'Tawon', buku: -35, butuh: 50, kurang: 85 }]) && !P4t.tolak && P4t.tandai === true && P4t.kurang === 85 && dok(P4t, 'produksiKemasan')[0].perluCocokkan === true && dok(P4t, 'produksiKemasan')[0].selisihKg === 85 && dok(P4t, 'batchMasuk').length === 1 && /DITANDAI untuk dicocokkan/.test(P4t.patch.kabar) && P4t.patch.kabarAwas === true, J([P4, P4t]));
var BK1 = susunBukaKarung('NG', W, 'Angsa'); var BK2 = susunBukaKarung('Beo', W, 'Angsa'); var BK2t = susunBukaKarung('Beo', W, 'Angsa', null, { tandai: true }); var BK3 = susunBukaKarung('NG', W, 'Angsa', { jenis: 'masuk', batchId: 'b1' }); var BK4 = susunBukaKarung('NG', W, 'Kosong Satu');
ok('buka karung dari layar Stok di belakang wadah AKTIF = wbDokBukaKB (pindah + catatan karung; gudang di BUKU NG 361,8 → 311,8 = 7 → 6 karung; kabar menyebut kunci); Beo minus → tolak + perluTandai, dengan tandai → tandai:true; pintu "baru datang" membawa asal & batch; di belakang wadah BELUM aktif = jalur lama (catatan karung saja, tanpa pindah)',
  !BK1.tolak && dok(BK1, 'produksiKemasan').length === 1 && dok(BK1, 'wadahLiteran').length === 1 && dok(BK1, 'wadahLiteran')[0].merk === KB('Angsa', 'NG') && !dok(BK1, 'batchMasuk').length && J(BK1.gudang) === J({ merk: 'NG', kgKarung: 50, dariKg: 361.8, keKg: 311.8, dariKarung: 7, keKarung: 6 }) && BK1.tandai === false
  && /dibuka di belakang wadah Angsa — BUKU: NG 361,8 kg → 311,8 kg, Karung belakang Angsa · NG \+50 kg \(modal ikut\)/.test(BK1.patch.kabar) && !!BK2.tolak && BK2.perluTandai[0].merk === 'Beo' && !BK2t.tolak && BK2t.tandai === true && BK2t.kurang === 50
  && !BK3.tolak && dok(BK3, 'wadahLiteran')[0].asal === 'masuk' && dok(BK3, 'wadahLiteran')[0].batchId === 'b1' && dok(BK3, 'wadahLiteran')[0].bukuBelakang === true && /yang baru datang dari pemasok/.test(BK3.patch.kabar)
  && !BK4.tolak && !dok(BK4, 'produksiKemasan').length && dok(BK4, 'wadahLiteran').length === 1 && dok(BK4, 'wadahLiteran')[0].merk === 'NG' && dok(BK4, 'wadahLiteran')[0].wadah === 'Kosong Satu' && !dok(BK4, 'wadahLiteran')[0].bukuBelakang, J([BK1, BK2, BK2t, BK3, BK4]));
var tAn8 = tump('Angsa'), bAn8 = buku('Angsa'); var U6 = U('Angsa', 'Angsa', { jenis: 'kg', kg: '55' });
ok('"kg" 55 merek Angsa ke wadah Angsa (kosong): belum ada karung Angsa di belakangnya → DUA karung dibuka sekaligus (sebanyak yang perlu): enam dokumen, dibuka 2, sisa karung belakang 45', !U6.tolak && U6.dokumen.length === 6 && U6.hitung.dibuka === 2 && U6.hitung.sisaKB === 45 && U6.hitung.isiBaru === 55 && dok(U6, 'wadahLiteran').filter(function (d) { return d.tipe === 'karung'; }).length === 2 && J(dok(U6, 'produksiKemasan')[0].sumberList) === J([{ merk: 'Angsa', kg: 100 }]) && dok(U6, 'batchMasuk').length === 1 && /2 karung Angsa dibuka dari tumpukan gudang: buku Angsa 200 kg → 100 kg · sisa di karung belakang ±45 kg/.test(U6.patch.kabar), J(U6));
terapkanKeCache(U6.dokumen || []);
ok('sesudahnya: buku Angsa −100, tumpukan Angsa −100, karung belakang Angsa · Angsa 45 (buku = kolam, 2 karung), wadah 55', B2(buku('Angsa') - bAn8) === -100 && B2(tump('Angsa') - tAn8) === -100 && wbKarungBelakang('Angsa', 'Angsa').bukuKg === 45 && wbKarungBelakang('Angsa', 'Angsa').kolamKg === 45 && buku('Wadah Angsa') === 55, J([buku('Angsa'), bAn8, tump('Angsa'), tAn8, wbKarungBelakang('Angsa', 'Angsa'), buku('Wadah Angsa')]));

// ---- 10 · dua angka satu kotak: wadah AKTIF (7b)
ok('selisih wadah aktif: semua karung belakang Angsa & IR64 Apex kolam = buku → ada:false', !wbSelisihWadah('Angsa', s0()).ada && !wbSelisihWadah('IR64 Apex', s0()).ada && wbKarungBelakangWadah('Angsa').length === 4 && wbKarungBelakangWadah('Angsa').every(function (k) { return k.selisihKg === 0; }), J(wbKarungBelakangWadah('Angsa')));
var SWa = denganCacheSementara(susunSamakanKarung(KB('Angsa', 'NG'), '30', W, 'Angsa').dokumen, function () { return wbSelisihWadah('Angsa', s0()); });
ok('karung belakang NG disamakan jadi 30 kg (buku 37,5) → selisih 7,5 kg DISEBUT: "catatan ±30 kg vs buku 37,5 kg — samakan karungnya"; karung lain diam', SWa.ada && SWa.baris.length === 1 && SWa.baris[0].jenis === 'karung-belakang' && SWa.baris[0].merk === 'NG' && SWa.baris[0].selisihKg === -7.5 && SWa.teks === 'karung NG di belakang: catatan ±30 kg vs buku 37,5 kg — selisih 7,5 kg, samakan karungnya', J(SWa));
ok('karung belakang berurutan buku terbesar dulu: Beo 50, Angsa 45, NG 37,5, Kumala 25', J(wbKarungBelakangWadah('Angsa').map(function (k) { return k.merk + ' ' + k.bukuKg; })) === J(['Beo 50', 'Angsa 45', 'NG 37.5', 'Kumala 25']));

// ---- 11 · tutup buku, katalog kasir, daftar merek, deretan (9)
var TB = pembukaBuku(2026, W); var tbb = dok(TB, 'batchMasuk')[0] || { merkList: [] }; var tbKB = tbb.merkList.filter(function (r) { return kb_(r.merk); });
ok('tutup buku: baris saldo pembuka tiap buku karung belakang membawa karungBelakang + merkAsal (bukan karungWadah / stokWadah); buku wadah stokWadah; karung wadah karungWadah', tbKB.length === 6 && tbKB.every(function (r) { return r.karungBelakang && r.merkAsal && !r.karungWadah && !r.stokWadah; }) && tbKB.some(function (r) { return r.merk === KB('Angsa', 'NG') && r.karungBelakang === 'Angsa' && r.merkAsal === 'NG'; }) && tbKB.some(function (r) { return r.merk === KB('Angsa', 'Beo') && r.merkAsal === 'Beo'; })
  && tbb.merkList.some(function (r) { return r.merk === 'Wadah Angsa' && r.stokWadah === 'Angsa'; }) && tbb.merkList.some(function (r) { return r.merk === 'Karung wadah Angsa' && r.karungWadah === 'Angsa'; }), J(tbb.merkList));
var kk = kkIsi(); var kwA = kk.merkKarung.find(function (m) { return m.merk === 'Wadah Angsa'; });
ok('katalog HP kasir (wbSaringKatalogKasir): tidak ada baris kunci karung belakang; buku wadah tetap berharga liter wadahnya (Wadah Angsa 13.000/L, Wadah IR64 Apex 12.000/L) tanpa karung', !kk.merkKarung.some(function (m) { return kb_(m.merk); }) && !!kwA && kwA.hargaPerLiter === 13000 && kwA.karung50 === false && kk.merkKarung.find(function (m) { return m.merk === 'Wadah IR64 Apex'; }).hargaPerLiter === 12000, J(kk.merkKarung.map(function (m) { return m.merk; })));
var sm = stokMerekSaja(hitungStokKarungPerMerk());
ok('stokMerekSaja membuang kunci karung belakang, buku wadah, karung wadah — merek pemasok tetap', !Object.keys(sm).some(function (k) { return /^Karung belakang |^Wadah |^Karung wadah /.test(k); }) && !!sm['NG'] && !!sm['Beo'] && !!sm['Tawon'] && Object.keys(hitungStokKarungPerMerk()).filter(kb_).length === 6, J(Object.keys(sm)));
var bocor = bocorKB();
ok('kunci karung belakang tidak bocor ke daftar merek (rak karung/repack/literan, karung gudang, campuran, harga, barang masuk, cocokkan tumpukan, kedatangan (batch lahir), HPP, tempat, belanja, lokasi, katalog kasir, stokMerekSaja)', Object.keys(bocor).every(function (k) { return bocor[k] === 0; }), J(bocor));
var dr = deretanKarung().filter(function (k) { return kb_(k.merk); });
ok('deretan karung: tiap karung belakang berbuku tampil dengan label MEREK ASAL & letak di belakang wadahnya; k.merk = kunci buku, k.merkAsal = merek', dr.length === 6 && dr.every(function (k) { return k.merkAsal && /di belakang wadah /.test(k.letak) && k.label.indexOf(k.merkAsal + ' ') === 0; }) && dr.some(function (k) { return k.merk === KB('Angsa', 'NG') && k.merkAsal === 'NG' && k.letak === 'karung NG di belakang wadah Angsa' && k.label === 'NG ±37,5 kg'; }), J(dr.map(function (k) { return [k.merk, k.merkAsal, k.letak, k.label]; })));
var HM = hitungMasuk({ tanggal: '2026-09-21', baris: [{ merk: KB('Angsa', 'NG'), jumlahKarung: '1', beratKarung: '50', hargaPerKg: '12000' }] });
ok('barang masuk atas nama kunci karung belakang DITOLAK dengan kalimat (buku khusus)', HM.baris[0].masalah.indexOf('buku KHUSUS') >= 0, J(HM.baris[0]));

// ---- 12 · tanda "untuk dicocokkan": pita Jual & kartu keempat Gudang (5)
var TBn = notaTembusBelumCocok(); var G = susunGudang('cocok', KINI);
ok('L.notaTembusBelumCocok memuat pindah bertanda: nama = merek asal (Beo 25, Tawon 35), dua baris jenis takar bernama wadah, ringkas; kartu keempat Gudang (jwbCocok lewat susunGudang) punya baris tembus|Beo & tembus|Tawon "… kg tembus · belum dicocokkan" (awas); n = 2 (tiap pindah bertanda dihitung lewat trxId "takar<id>", tidak tertimpa trxId kosong dari wbPindahTembusBelumCocok)',
  J(TBn.nama) === J([{ nama: 'Beo', kg: 25, n: 1 }, { nama: 'Tawon', kg: 35, n: 1 }]) && TBn.baris.length === 2 && TBn.n === 2 && TBn.baris.every(function (b) { return b.jenis === 'takar' && b.wadah && b.selisihKg > 0 && /^takar/.test(b.trxId); }) && TBn.ringkas === 'Beo 25 kg, Tawon 35 kg'
  && G.jawab.baris.some(function (b) { return b.kunci === 'tembus|Beo' && b.n === '25 kg tembus' && b.nKet === 'belum dicocokkan' && b.awas === true; }) && G.jawab.baris.some(function (b) { return b.kunci === 'tembus|Tawon' && b.n === '35 kg tembus'; }) && G.kartu.find(function (k) { return k.id === 'cocok'; }).awas === true, J([TBn, G.jawab.baris.slice(0, 3)]));
var cocok = function (m, tgl, ekstra) { return { koleksi: 'penyesuaianStok', data: Object.assign({ id: 'ps-' + m + '-' + tgl + (ekstra ? '-r' : ''), tanggal: tgl, jam: '18:00', merk: m, kgSistem: 0, kgFisik: 0, selisihKg: 0, alasan: 'hitung', nilaiRp: 0, hppPerKgSaatOpname: 0 }, ekstra || {}) }; };
ok('tuntas = cocokkan merek asal bertanggal ≥ dokumen: Tawon 21 Sep → tinggal Beo (kartu keempat ikut); Tawon 20 Sep / rework / merek lain → tanda tetap; Beo & Tawon 22 Sep → kosong',
  denganCacheSementara([cocok('Tawon', '2026-09-21')], function () { return notaTembusBelumCocok().ringkas === 'Beo 25 kg' && !susunGudang('cocok', KINI).jawab.baris.some(function (b) { return b.kunci === 'tembus|Tawon'; }); })
  && denganCacheSementara([cocok('Tawon', '2026-09-20'), cocok('Tawon', '2026-09-21', { dariRework: true }), cocok('NG', '2026-09-22')], function () { return notaTembusBelumCocok().nama.length === 2 && notaTembusBelumCocok().baris.length === 2; })
  && denganCacheSementara([cocok('Beo', '2026-09-22'), cocok('Tawon', '2026-09-22')], function () { return notaTembusBelumCocok().nama.length === 0 && notaTembusBelumCocok().n === 0 && !wbPindahTembusBelumCocok().length && !susunGudang('cocok', KINI).jawab.baris.some(function (b) { return /^tembus\|/.test(b.kunci); }); }));

// ---- 13 · penjaga perangkat = rules v5 (10)
var KRY = keadaanAkun('kry.contoh@tokoberasmiqbal.web.app', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true }); var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
var HAK = { jualTunai: 'sendiri', jualBon: 'owner', nego: 'tidak', terimaBon: 'sendiri', hitungLaci: 'tidak', uangKeluar: 'tidak', adukan: 'sendiri', kedatangan: 'tidak', hargaBeli: 'tidak', koreksi: 'tidak', hapus: 'tidak', pelangganBaru: 'sendiri', atur: 'tidak', isiUlang: 'sendiri' };
var kirim = function (R, akun) { return periksaKiriman(akun || KRY, (R.dokumen || []).map(function (d) { return { koleksi: d.koleksi, data: d.data, ada: false }; }), [], HAK, KINI); };
ok('penjaga perangkat: karyawan boleh mengirim isi ulang tiga ketukan utuh (lahir 0 kg + pindah + karung + takar + pindah = accessCall 6), cek dikosongkan (lahir + pindah + karung sisihan + cek = 5), samakan karung (karungIsi = 2), cek sesuai (2), buka karung (3); owner 0',
  kirim(U2).accessCall === 6 && kirim(C4).accessCall === 5 && kirim(SK1).accessCall === 2 && kirim(C1).accessCall === 2 && kirim(BK1).accessCall === 3 && kirim(U2, OWN).accessCall === 0, J([kirim(U2), kirim(C4), kirim(SK1), kirim(C1), kirim(BK1)]));
var dokW = function (d) { return { dokumen: [{ koleksi: 'wadahLiteran', data: d }] }; }; var dokB = function (d) { return { dokumen: [{ koleksi: 'batchMasuk', data: d }] }; }; var lahirOk = dok(U2, 'batchMasuk')[0] || { merkList: [{}] };
ok('karyawan DITOLAK: aturan wadah (tipe atur) & titik samakan isi (tipe isi) → "tidak boleh ubah setelan"; aktivasi wadah (memuat isi) → ditolak; batch lahir berisi kg / harga / bongkar / pemasok lain / kedatangan sungguhan → "tidak boleh hitung truk"; batch lahir utuh boleh',
  /tidak boleh ubah setelan/.test(kirim(dokW({ id: 1, tanggal: '2026-09-21', tipe: 'atur', daftar: ['Angsa'] })).tolak || '') && /tidak boleh ubah setelan/.test(kirim(dokW({ id: 2, tanggal: '2026-09-21', tipe: 'isi', wadah: 'Angsa', isiKg: 50 })).tolak || '') && /tidak boleh ubah setelan/.test(kirim(A1).tolak || '')
  && /tidak boleh hitung truk/.test(kirim(dokB(Object.assign({}, lahirOk, { merkList: [Object.assign({}, lahirOk.merkList[0], { totalKg: 50 })] }))).tolak || '') && /tidak boleh hitung truk/.test(kirim(dokB(Object.assign({}, lahirOk, { biayaBongkar: 1000 }))).tolak || '')
  && /tidak boleh hitung truk/.test(kirim(dokB(Object.assign({}, lahirOk, { merkList: [Object.assign({}, lahirOk.merkList[0], { subtotalHarga: 1 })] }))).tolak || '') && /tidak boleh hitung truk/.test(kirim(dokB(Object.assign({}, lahirOk, { pemasok: 'PEMASOK CONTOH' }))).tolak || '') && /tidak boleh hitung truk/.test(kirim(dokB(Object.assign({}, lahirOk, { lahirBuku: false }))).tolak || '')
  && /tidak boleh hitung truk/.test(kirim(dokB(KOTAK.batchMasuk[0])).tolak || '') && kirim(dokB(lahirOk)).accessCall === 2, J([kirim(dokW({ id: 1, tanggal: '2026-09-21', tipe: 'atur' })), kirim(A1), kirim(dokB(Object.assign({}, lahirOk, { biayaBongkar: 1000 })))]));

// ---- 14 · identitas tiap wadah aktif (dari dokumen) — pola asap (i)
var idW = ['IR64 Apex', 'Angsa', 'Tawon Super'].map(identitasWadah);
ok('identitas tiap wadah aktif: isi titik samakan + Σ takar − Σ literan − Σ pindah keluar (sisihan) ± penyesuaian = buku wadah = tinggi wadah; Σ komposisi turunan = buku (IR64 Apex 60 · Angsa 55 · Tawon Super 55)', idW.every(function (x) { return x.ok; }) && J(idW.map(function (x) { return x.buku; })) === J([60, 55, 55]), J(idW));

// ---- 15 · putaran 39c (owner 30 Sep): deretan = SATU SLOT PER WADAH, karung habis dihapus, dikembalikan → slot "?", karung berbuku kembali ke bukunya
var SL0 = slotKarungWadah();
ok('39c slot: tepat satu slot per wadah (5) urut W1..W5; tiap slot kosong ("?") atau menyebut merek asalnya; karung lepas/yatim tidak di slot (karungLepasDeretan tanpa no)',
  SL0.length === 5 && J(SL0.map(function (x) { return x.no; })) === J(['W1', 'W2', 'W3', 'W4', 'W5']) && SL0.every(function (x) { return x.W && (x.kosong ? !x.karung.diketahui && x.label === 'belum ada karung' : !!x.merkAsal); }) && karungLepasDeretan().every(function (k) { return !k.no; }), J(SL0.map(function (x) { return [x.no, x.kosong, x.merkAsal, x.habis, x.alasan]; })));
var tNG0 = tump('NG'); var bNG0 = buku('NG'); var BKn = susunBukaKarung('NG', W, 'Angsa'); terapkanKeCache(BKn.dokumen || []); var BKk = susunBukaKarung('Kumala', W, 'Angsa'); terapkanKeCache(BKk.dokumen || []);
var slAn = function () { return slotKarungWadah().find(function (x) { return x.W === 'Angsa'; }); };
ok('39c slot W2 Angsa: dua karung berbuku dibuka berturut (NG lalu Kumala) → slotnya = yang TERBARU (Kumala, buku sendiri, tidak habis); karungUntukWadah per merek', !BKn.tolak && !BKk.tolak && slAn().merkAsal === 'Kumala' && slAn().bukuSendiri && !slAn().habis && !slAn().kosong && karungUntukWadah('Angsa').merk === KB('Angsa', 'Kumala'), J(slAn()));
var kNG = karungBelakang(KB('Angsa', 'NG'), 'Angsa'); var sisaNG = B2(kNG.sisaMentahKg); var bNG1 = buku('NG'); var tNG1 = tump('NG');
var RK = susunKembalikanKarung(KB('Angsa', 'NG'), 'Angsa', W, true); terapkanKeCache(RK.dokumen || []);
ok('39c kembalikan karung BERBUKU yang lebih lama (kolam NG di belakang Angsa: sisa lama 37,5 + karung baru 50 = 87,5): bukan menghapus catatan — karungIsi 0 dikembalikan + pindah buku KB → NG sebesar seluruh sisa kolam; buku NG & tumpukan NG naik persis sebesar itu, buku karung belakang NG 0; slot W2 TETAP Kumala (per merek, bukan jatuh ke karung lama)',
  !RK.tolak && sisaNG === 87.5 && dok(RK, 'wadahLiteran').length === 1 && dok(RK, 'wadahLiteran')[0].dikembalikan === true && dok(RK, 'produksiKemasan').length === 1 && dok(RK, 'produksiKemasan')[0].namaProduk === 'NG' && dok(RK, 'produksiKemasan')[0].ukuranKemasan === sisaNG && dok(RK, 'produksiKemasan')[0].kembaliTumpukan === 'Angsa'
  && B2(buku('NG')) === B2(bNG1 + sisaNG) && B2(buku(KB('Angsa', 'NG'))) === 0 && B2(tump('NG')) === B2(tNG1 + sisaNG) && slAn().merkAsal === 'Kumala', J([RK.tolak, sisaNG, buku('NG'), bNG1, buku(KB('Angsa', 'NG')), tump('NG'), tNG1, slAn()]));
var SK0 = susunSamakanKarung(KB('Angsa', 'Kumala'), '0', W, 'Angsa'); terapkanKeCache(SK0.dokumen || []);
var bK = B2(buku(KB('Angsa', 'Kumala')));
ok('39c karung habis di kolam (sisa disamakan 0) tapi bukunya masih 75 (25 sisa lama + 50) → slot menyebut HABIS; hapus ketukan pertama DITANYA (perluYakin) menyebut susut 75 kg; tidak ada dokumen', bK === 75 && slAn().habis && /habis/.test(slAn().label) && (function () { var H = susunHapusKarungHabis(KB('Angsa', 'Kumala'), 'Angsa', W, false); return !!H.tolak && H.perluYakin === true && /susut 75 kg/.test(H.tolak) && !H.dokumen; })(), J([bK, slAn(), susunHapusKarungHabis(KB('Angsa', 'Kumala'), 'Angsa', W, false)]));
var hppK = hpp(KB('Angsa', 'Kumala')); var v0h = nilai(); var lb0h = laba();
var H1 = susunHapusKarungHabis(KB('Angsa', 'Kumala'), 'Angsa', W, true); terapkanKeCache(H1.dokumen || []);
ok('39c hapus ketukan kedua: karungIsi 0 bertanda selesai + penyesuaianStok kunci buku (kgSistem 75 → kgFisik 0, selisih −75, bagian karung, alasan "karung habis"); buku karung belakang jadi 0, nilai stok turun 75 × modal, laba turun (susut, tidak diam); slot W2 tidak lagi Kumala (jatuh ke kolam lain yang masih hidup di belakang Angsa, atau kosong); Papan Kapur menyebutnya',
  !H1.tolak && dok(H1, 'wadahLiteran').length === 1 && dok(H1, 'wadahLiteran')[0].selesai === true && dok(H1, 'wadahLiteran')[0].isiKg === 0 && dok(H1, 'penyesuaianStok').length === 1 && dok(H1, 'penyesuaianStok')[0].kgSistem === 75 && dok(H1, 'penyesuaianStok')[0].kgFisik === 0 && dok(H1, 'penyesuaianStok')[0].selisihKg === -75 && dok(H1, 'penyesuaianStok')[0].bagian === 'karung' && /karung habis/.test(dok(H1, 'penyesuaianStok')[0].alasan)
  && B2(buku(KB('Angsa', 'Kumala'))) === 0 && Math.abs((v0h - nilai()) - 75 * hppK) < 1.5 && laba() < lb0h && slAn().merkAsal !== 'Kumala' && karungUntukWadah('Angsa').merk !== KB('Angsa', 'Kumala') && susunKapur(KINI).baris.some(function (x) { return /Karung Kumala di belakang wadah Angsa habis — dihapus dari deretan/.test(x.isi); }), J([H1.tolak, H1.dokumen, buku(KB('Angsa', 'Kumala')), v0h, nilai(), hppK, slAn()]));
// kolam lain yang masih hidup di belakang Angsa (karung Angsa dari aktivasi) dikembalikan → slot W2 KOSONG "?" beralasan dikembalikan
var sisaLain = []; for (var g39 = 0; g39 < 8 && !slAn().kosong; g39++) { var sl39 = slAn(); sisaLain.push(sl39.merkAsal); var RL = susunKembalikanKarung(sl39.merk, 'Angsa', W, true); if (RL.tolak) break; terapkanKeCache(RL.dokumen || []); }
ok('39c sesudah semua karung di belakang Angsa dihapus / dikembalikan: slot W2 KOSONG "?" (karungUntukWadah: merk = nama wadahnya, dariCatatan false, kosong true, alasan disebut, merek terakhir disebut); tumpukan Kumala tidak berubah oleh hapus (susut di buku karung belakang, bukan tumpukan)',
  (function () { var k = karungUntukWadah('Angsa'); var sl = slAn(); return k.merk === 'Angsa' && k.dariCatatan === false && k.kosong === true && /dikembalikan ke tumpukan gudang|habis, dihapus dari deretan/.test(k.alasanKosong) && !!k.terakhirMerk && sl.kosong && !sl.karung.diketahui && sl.label === 'belum ada karung'; })(), J([karungUntukWadah('Angsa'), slAn(), sisaLain]));
var BKn2 = susunBukaKarung('NG', W, 'Angsa'); terapkanKeCache(BKn2.dokumen || []);
ok('39c hapus karung yang masih berisi DITOLAK ("belum habis"); karung baru NG di belakang Angsa mengisi slot lagi (merek berganti: terakhir Kumala → NG)', /belum habis/.test(susunHapusKarungHabis(KB('Angsa', 'NG'), 'Angsa', W, true).tolak || '') && slAn().merkAsal === 'NG' && !slAn().kosong, J([susunHapusKarungHabis(KB('Angsa', 'NG'), 'Angsa', W, true), slAn()]));
var SKb = susunSamakanKarung('Beo', '0', W, 'Kosong Satu'); terapkanKeCache(SKb.dokumen || []); var slKs = function () { return slotKarungWadah().find(function (x) { return x.W === 'Kosong Satu'; }); };
var Hb = susunHapusKarungHabis('Beo', 'Kosong Satu', W, false); terapkanKeCache(Hb.dokumen || []);
ok('39c karung biasa (bukan berbuku) yang habis di belakang wadah belum aktif: slot W4 Beo habis → hapus tanpa ketukan kedua (tidak ada buku karung belakang), satu dokumen selesai → slot W4 kosong', !SKb.tolak && !Hb.tolak && (Hb.dokumen || []).length === 1 && Hb.dokumen[0].data.selesai === true && Hb.dokumen[0].data.wadah === 'Kosong Satu' && slKs().kosong && slKs().alasan === 'habis, dihapus dari deretan' && slKs().terakhirMerk === 'Beo', J([SKb.tolak, Hb, slKs()]));
ok('39c isi ulang tiga ketukan dengan merek yang tidak punya karung di belakang wadah (NG ke Tawon Super): hitung.dibuka = 1 (karung baru dari tumpukan) — bahan peringatan dua ketukan di layar (yakinBuka)', (function () { var r = U('Tawon Super', 'NG', { jenis: 'kg', kg: '1' }); return !r.tolak && r.hitung.dibuka === 1; })(), J([U('Tawon Super', 'NG', { jenis: 'kg', kg: '1' }).tolak, U('Tawon Super', 'NG', { jenis: 'kg', kg: '1' }).hitung]));

// ---- 16 · 39c (owner 30 Sep): karung di belakang DIHABISKAN dulu — sisa yang kurang dari yang diminta dituang SEADANYA, karung baru dari tumpukan ditanya sesudah bersih 0
var SKn = susunSamakanKarung('NG', '1', W, 'Tawon Super'); terapkanKeCache(SKn.dokumen || []);
var HT1 = hitungTakar('Tawon Super', [{ merk: 'NG', takar: 1 }], s0());
ok('39c − / + takar: karung NG tinggal 1 kg di belakang wadah aktif, minta 1 takar (1,8 kg) → dituang SEADANYA 1 kg (kurang 0,8 kg TIDAK ditambal dari karung baru, bukaKarung 0); karung lama bernama merek tetap dipakai walau tidak cukup satu takar', !SKn.tolak && HT1.sumber[0].merk === 'NG' && HT1.sumber[0].seadanya === true && HT1.sumber[0].kg === 1 && HT1.sumber[0].kgMinta === 1.8 && HT1.sumber[0].kurangKg === 0.8 && HT1.sumber[0].bukaKarung === 0 && HT1.kg === 1, J([SKn.tolak, HT1.sumber]));
var TK1 = susunTakarWadah('Tawon Super', [{ merk: 'NG', takar: 1 }], W, s0()); terapkanKeCache(TK1.dokumen || []);
var HT2 = hitungTakar('Tawon Super', [{ merk: 'NG', takar: 1 }], s0());
ok('39c − / + takar dicatat: dokumen takar kg 1 bertanda seadanya (kgMinta 1,8), kabar menyebut SEADANYA & bersih 0; sesudahnya karung NG itu 0 → takar berikutnya barulah minta karung baru dari tumpukan (bukaKarung 1, tanpa seadanya, kunci karung belakang)', !TK1.tolak && dok(TK1, 'wadahLiteran').filter(function (d) { return d.tipe === 'takar'; })[0].kg === 1 && dok(TK1, 'wadahLiteran').filter(function (d) { return d.tipe === 'takar'; })[0].sumber[0].seadanya === true && /SEADANYA/.test(TK1.patch.kabar) && /bersih 0/.test(TK1.patch.kabar)
  && karungBelakang('NG', 'Tawon Super').sisaKg === 0 && HT2.sumber[0].bukaKarung === 1 && !HT2.sumber[0].seadanya && HT2.sumber[0].kg === 1.8, J([TK1.tolak, TK1.patch && TK1.patch.kabar, HT2.sumber]));
// tiga ketukan: W4 Kosong Satu diberi titik samakan 0 kg → diaktifkan (buku wadah 0, tanpa karung) → karung NG dibuka di belakangnya (buku karung belakang 50) → minta 55 kg
terapkanKeCache([{ koleksi: 'wadahLiteran', data: { id: W.idUnik(), tanggal: W.tanggal, jam: W.jam, tipe: 'isi', wadah: 'Kosong Satu', isiKg: 0 } }]);
var AK16 = wbSusunAktifkan('Kosong Satu', W); terapkanKeCache(AK16.dokumen || []); var BK16 = susunBukaKarung('NG', W, 'Kosong Satu'); terapkanKeCache(BK16.dokumen || []);
var kb16 = wbKarungBelakang('Kosong Satu', 'NG').bukuKg; var U16 = U('Kosong Satu', 'NG', { jenis: 'kg', kg: '55' });
ok('39c tiga ketukan: karung belakang NG 50 kg di W4 (baru aktif, kosong), minta 55 kg → hitung.seadanya, kg = 50 (sisa buku), dibuka 0, takar bertanda seadanya + kgMinta 55, kabar SEADANYA; sesudahnya permintaan yang sama → karung baru dibuka (dibuka 1, tanpa seadanya)',
  !AK16.tolak && !BK16.tolak && kb16 === 50 && !U16.tolak && U16.hitung.seadanya === true && U16.hitung.kg === 50 && U16.hitung.kgMinta === 55 && U16.hitung.dibuka === 0 && dok(U16, 'wadahLiteran')[0].seadanya === true && dok(U16, 'wadahLiteran')[0].kgMinta === 55 && /SEADANYA 50 kg NG \(minta 55 kg; karung di belakang bersih 0/.test(U16.patch.kabar)
  && denganCacheSementara(U16.dokumen, function () { var r2 = U('Kosong Satu', 'NG', { jenis: 'kg', kg: '5' }); return !r2.tolak && r2.hitung.dibuka === 1 && !r2.hitung.seadanya && r2.hitung.kg === 5 && wbKarungBelakang('Kosong Satu', 'NG').bukuKg === 0; }), J([AK16.tolak, BK16.tolak, kb16, U16.tolak, U16.hitung, U16.patch && U16.patch.kabar]));
print(J({ lulus: lulus, gagal: gagal }));
"""

# ASAP cadangan toko: aktivasi SEMUA wadah disimulasikan (yang kurang → tandai), identitas per merek asal & per wadah, isi ulang & jual contoh
ASAP = BANTU + r"""
Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
var nId = 900000; var W = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
var bulan = TGL_CAD.slice(0, 7); var akhir = bulan + '-' + String(new Date(Number(bulan.slice(0, 4)), Number(bulan.slice(5, 7)), 0).getDate()).padStart(2, '0');
var laba = function () { return hitungLabaBersihRentang(bulan + '-01', akhir).labaBersih; };
var tumpSemua = function () { var o = {}; susunLokasi().forEach(function (t) { o[t.merk] = B2(t.kg); }); return o; };
var namaKg = function () { var o = {}; susunLokasi().forEach(function (t) { o[t.merk] = B2(t.namaKg); }); return o; };
var v0 = nilai(), t0 = tumpSemua(), n0 = namaKg(), laba0 = laba();
var D0 = wbDaftarAktivasi();
var daftar = D0.map(function (x) { return { no: x.no, W: x.W, aktif: x.aktif, bisa: x.bisa, cukup: x.cukup, isiKg: x.isiKg, kolam: x.kolam.map(function (k) { return k.merk + ' ' + k.kg; }), kurang: x.kurang.map(function (k) { return k.merk + ' ' + k.kurang; }), alasan: x.alasan }; });
// tanpa opsi.tandai: wadah yang bukunya kurang WAJIB ditolak tanpa dokumen (tidak ada yang ditulis diam-diam)
var tanpaTandai = D0.filter(function (x) { return x.bisa && !x.cukup; }).map(function (x) { var r = wbSusunAktifkan(x.W, W); return { W: x.W, ok: !!r.tolak && !!r.perluTandai && !r.dokumen }; });
var jadi = [], tandai = [], lewati = [], gagalAktif = [];
D0.forEach(function (x) { if (x.aktif) return; if (!x.bisa) { lewati.push(x.W + ' — ' + x.alasan); return; }
  var r = wbSusunAktifkan(x.W, W, x.cukup ? undefined : { tandai: true }); if (r.tolak) { gagalAktif.push(x.W + ' — ' + r.tolak); return; }
  terapkanKeCache(r.dokumen); jadi.push(x.W); if (!x.cukup) tandai.push(x.W + ' (' + x.kurang.map(function (k) { return k.merk + ' ' + k.kurang; }).join(', ') + ')'); });
var v1 = nilai(), laba1 = laba(), t1 = tumpSemua(); var geserAkt = Object.keys(t0).filter(function (m) { return Math.abs((t1[m] || 0) - t0[m]) > 0.011; });
// (ii) per merek asal: namaKg sebelum = namaKg sesudah + Σ buku karung belakang di wadah yang baru aktif + Σ bagian merek itu di wadah yang baru aktif (komposisi turunan)
var n1 = namaKg(); var kbBaru = {}, bagianBaru = {};
jadi.forEach(function (Wn) { wbKarungBelakangWadah(Wn).forEach(function (k) { kbBaru[k.merk] = B2((kbBaru[k.merk] || 0) + k.bukuKg); }); wbKomposisiTurunan(Wn).daftar.forEach(function (x) { bagianBaru[x.merk] = B2((bagianBaru[x.merk] || 0) + x.kg); }); });
var semuaM = Object.keys(n0).concat(Object.keys(n1), Object.keys(kbBaru), Object.keys(bagianBaru)).filter(function (m, i, a) { return a.indexOf(m) === i; });
var identitasMerk = semuaM.map(function (m) { var kanan = B2((n1[m] || 0) + (kbBaru[m] || 0) + (bagianBaru[m] || 0)); return { merk: m, sebelum: n0[m] || 0, sesudah: kanan, kb: kbBaru[m] || 0, diWadah: bagianBaru[m] || 0, selisih: B2(kanan - (n0[m] || 0)) }; }).filter(function (x) { return Math.abs(x.selisih) > 0.02 + 0.005 * jadi.length; });
// isi ulang contoh 1 kg per wadah yang baru aktif (merek asal terbesar di komposisi turunan / karung di belakangnya): nilai stok tetap, buku wadah naik 1 kg
var isiUlang = []; jadi.forEach(function (Wn) { var tw = tinggiWadah(Wn, null); if (!tw || tw.muatKg < 1) { isiUlang.push({ W: Wn, lewati: 'penuh' }); return; }
  var KT = wbKomposisiTurunan(Wn); var M = KT.daftar.length ? KT.daftar[0].merk : wbMerkAsal(karungUntukWadah(Wn).merk); if (!hitungStokKarungPerMerk()[M] || wbBukuKhusus(M)) { isiUlang.push({ W: Wn, M: M, lewati: 'tanpa buku merek' }); return; }
  var r = wbSusunIsiUlangTiga(Wn, M, { jenis: 'kg', kg: '1' }, W, s0()); if (r.tolak) { isiUlang.push({ W: Wn, M: M, tolak: r.tolak.slice(0, 140), perluTandai: !!r.perluTandai }); return; }
  var vA = nilai(); var bA = buku(wbKunci(Wn)); terapkanKeCache(r.dokumen); var KB2 = wbKarungBelakang(Wn, M);
  isiUlang.push({ W: Wn, M: M, ok: nilai() === vA && Math.abs(buku(wbKunci(Wn)) - bA - 1) < 0.011 && Math.abs(KB2.bukuKg - r.hitung.sisaKB) < 0.011 && Math.abs(KB2.selisihKg) < 0.011, dibuka: r.hitung.dibuka, berat: beratKarungBuka(M), sisaKB: r.hitung.sisaKB }); });
var harapTurun = {}; isiUlang.forEach(function (x) { if (x.ok && x.dibuka) harapTurun[x.M] = B2((harapTurun[x.M] || 0) + x.dibuka * x.berat); });
var t2 = tumpSemua(); var geserIsi = Object.keys(t1).filter(function (m) { return Math.abs((t2[m] || 0) - (t1[m] - (harapTurun[m] || 0))) > 0.011; }); var laba2 = laba();
// jual contoh 1 L dari tiap wadah yang baru aktif & berharga: satu baris merkSumber = buku wadah
var jual = []; jadi.forEach(function (Wn) { var c = chipL(Wn); if (!c) { jual.push({ W: Wn, lewati: 'tanpa harga liter' }); return; } if (c.sisa < 1) { jual.push({ W: Wn, lewati: 'buku wadah kosong' }); return; }
  var r = masukkan(Object.assign({}, s0(), { pilih: c }), 1); var s = Object.assign({}, s0(), { keranjang: r.keranjang || [] }); var N = simpanNota(Object.assign({}, s, { cara: 'QRIS' }), W);
  var rows = dok(N, 'penjualan'); var baik = !N.tolak && rows.length === 1 && rows[0].merkSumber === wbKunci(Wn); if (baik) terapkanKeCache(N.dokumen); jual.push({ W: Wn, ok: baik, tolak: N.tolak || r.kabar || '' }); });
// (i) identitas tiap wadah yang baru aktif, dari dokumen yang disimulasikan
var idW = jadi.map(identitasWadah); var cek = wbCekHari(TGL_CAD);
print(J({ daftar: daftar, tanpaTandai: tanpaTandai, jadi: jadi, tandai: tandai, lewati: lewati, gagalAktif: gagalAktif, nilai: [v0, v1], laba: [laba0, laba1, laba2], geserAkt: geserAkt, identitasMerk: identitasMerk, isiUlang: isiUlang, geserIsi: geserIsi, jual: jual, identitasWadah: idW, nAktif: cek.nAktif, bocor: bocorKB() }));
"""


def utama(js, pakai_cadangan):
    h, e = uji_wadah_bernama.jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    asap = None
    p = uji_wadah_bernama.cadangan_toko() if pakai_cadangan else None
    if p:
        cad, tgl = uji_wadah_bernama.cad_js(p)
        asap = asap_cadangan(js, cad, tgl)
    return h['lulus'], h['gagal'], asap


def asap_cadangan(js, cad, tgl):
    """Jalankan blok ASAP di atas satu cadangan (cad = JSON koleksi, tgl = tanggal cadangan)."""
    a, e2 = uji_wadah_bernama.jalan(JAM_TETAP.replace('2026-09-21T10:00:00', tgl + 'T23:00:00') + js + '\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + ASAP)
    return a if a is not None else {'jatuh': e2[-400:]}


def nilai_asap(asap):
    """→ daftar masalah asap (kosong = lulus)."""
    m = []
    if asap.get('gagalAktif'): m.append('aktivasi gagal: ' + '; '.join(asap['gagalAktif']))
    if any(not x['ok'] for x in asap['tanpaTandai']): m.append('wadah kurang diaktifkan TANPA tandai: ' + ', '.join(x['W'] for x in asap['tanpaTandai'] if not x['ok']))
    if asap['nilai'][0] != asap['nilai'][1]: m.append('nilai stok bergeser sesudah aktivasi: %s → %s' % tuple(asap['nilai']))
    if asap['laba'][0] != asap['laba'][1] or asap['laba'][1] != asap['laba'][2]: m.append('laba bergeser: %s → %s → %s' % tuple(asap['laba']))
    if asap['geserAkt']: m.append('tumpukan bergeser saat aktivasi: ' + ', '.join(asap['geserAkt']))
    if asap['identitasMerk']: m.append('identitas per merek asal tidak menutup: ' + json.dumps(asap['identitasMerk'], ensure_ascii=False))
    if any(x.get('ok') is False for x in asap['isiUlang']): m.append('isi ulang contoh: ' + json.dumps([x for x in asap['isiUlang'] if x.get('ok') is False], ensure_ascii=False))
    if any(x.get('tolak') and not x.get('perluTandai') for x in asap['isiUlang']): m.append('isi ulang contoh ditolak bukan karena buku merek kurang: ' + json.dumps([x for x in asap['isiUlang'] if x.get('tolak') and not x.get('perluTandai')], ensure_ascii=False))
    if asap['geserIsi']: m.append('tumpukan bergeser tidak sebesar karung yang dibuka: ' + ', '.join(asap['geserIsi']))
    if any(x.get('ok') is False for x in asap['jual']): m.append('jual contoh: ' + json.dumps([x for x in asap['jual'] if x.get('ok') is False], ensure_ascii=False))
    if any(not x['ok'] for x in asap['identitasWadah']): m.append('identitas wadah tidak menutup: ' + json.dumps([x for x in asap['identitasWadah'] if not x['ok']], ensure_ascii=False))
    if any(asap['bocor'][k] for k in asap['bocor']): m.append('kunci karung belakang bocor: ' + json.dumps(asap['bocor']))
    return m


def cetak_asap(nama, asap):
    print('ASAP DATA TOKO (%s): %d wadah; daftar: %s' % (nama, len(asap['daftar']), ' · '.join('%s %s%s' % (x['no'], x['W'], ' AKTIF' if x['aktif'] else (' bisa' + ('' if x['cukup'] else ' KURANG ' + ', '.join(x['kurang']))) if x['bisa'] else ' TIDAK: ' + x['alasan']) for x in asap['daftar'])))
    print('   aktivasi disimulasikan: %s · dengan tandai: %s · dilewati: %s · nilai stok %s → %s · laba %s → %s → %s · tumpukan bergeser saat aktivasi: %s · identitas per merek asal tidak menutup: %d'
          % (', '.join(asap['jadi']) or 'tidak ada', '; '.join(asap['tandai']) or 'tidak ada', '; '.join(asap['lewati']) or 'tidak ada', asap['nilai'][0], asap['nilai'][1], asap['laba'][0], asap['laba'][1], asap['laba'][2], ', '.join(asap['geserAkt']) or 'tidak ada', len(asap['identitasMerk'])))
    print('   isi ulang 1 kg: %s · tumpukan bergeser tidak sebesar karung dibuka: %s · jual 1 L: %d/%d · identitas wadah menutup: %d/%d · bocor: %s'
          % ('; '.join(('%s ← %s %s' % (x['W'], x.get('M', '-'), 'ok (buka %d)' % x['dibuka'] if x.get('ok') else 'lewati ' + x['lewati'] if x.get('lewati') else 'TOLAK ' + x.get('tolak', '') if x.get('tolak') else 'GAGAL')) for x in asap['isiUlang']) or 'tidak ada',
             ', '.join(asap['geserIsi']) or 'tidak ada', len([x for x in asap['jual'] if x.get('ok')]), len([x for x in asap['jual'] if not x.get('lewati')]), len([x for x in asap['identitasWadah'] if x['ok']]), len(asap['identitasWadah']), json.dumps(asap['bocor'])))


RUSAK = {
    # toko.js
    'kunci karung belakang tidak dikenali buku khusus': ("else if (m.karungBelakang) out[String(m.merk)] = { jenis: 'belakang', wadah: String(m.karungBelakang), merk: String(m.merkAsal || '') };", ""),
    'merkAsalKunci mengembalikan kuncinya (berat karung & label salah)': ("return b && b.jenis === 'belakang' && b.merk ? b.merk : String(kunci);", "return String(kunci);"),
    # wadah-bernama-logika.js: buka karung
    'buka karung tanpa pindah buku (tumpukan tidak turun)': ("    dokumen.push(p);\n    for (let i = 0; i < n; i++)", "    for (let i = 0; i < n; i++)"),
    'buku merek kurang tidak ditolak (beras hantu)': ("if (kurang > 0.004 && !(opsi && opsi.tandai)) return { tolak: 'Buku ' + M", "if (false) return { tolak: 'Buku ' + M"),
    'tandai tanpa tanda perluCocokkan / selisihPerMerk': ("kurang > 0.004 ? { perluCocokkan: true, selisihKg: kurang, selisihPerMerk: { [M]: kurang } } : {}", "{}"),
    'catatan karung berbuku tanpa merkAsal': ("tipe: 'karung', merk: k, merkAsal: M, kg: berat, wadah: W, bukuBelakang: true", "tipe: 'karung', merk: k, kg: berat, wadah: W, bukuBelakang: true"),
    # isi ulang tiga ketukan
    'isi ulang wadah belum aktif lolos': ("if (!wbAktif(W)) return { tolak: 'Wadah ' + W + ' belum punya buku sendiri — aktifkan dulu", "if (false) return { tolak: 'Wadah ' + W + ' belum punya buku sendiri — aktifkan dulu"),
    'isi ulang melewati batas menggunung lolos': ("if (isiBaru > A.puncakKg + 0.0001) return { tolak: 'Kalau dituang '", "if (false) return { tolak: 'Kalau dituang '"),
    'karung belakang kurang tidak membuka karung baru': ("if (butuhBuka > 0.004) { const n = Math.ceil(", "if (false) { const n = Math.ceil("),
    '½ karung dihitung satu karung': ("t.jenis === 'setengah' ? wbB2(berat / 2)", "t.jenis === 'setengah' ? berat"),
    'takar tiga ketukan tanpa takaran & merkAsal': ("takaran: takaran || 'kg', sumber: [{ merk: k, merkAsal: M, takar, kg, dari: W }]", "sumber: [{ merk: k, takar, kg, dari: W }]"),
    'tuang tidak memindah buku ke wadah': ("stokWadah: kunci, produksiId: p.data.id } }, p], pindah: p.data };", "stokWadah: kunci, produksiId: p.data.id } }], pindah: p.data };"),
    # aktivasi
    'daftar aktivasi mengabaikan karung lama bernama merek di belakang wadah': ("const kolam = semuaKolam.filter((k) => k.lokasi === W && !bw[k.merk] && k.sisaMentahKg > 0.004)", "const kolam = [].filter((k) => k.lokasi === W && !bw[k.merk] && k.sisaMentahKg > 0.004)"),
    'wadah dengan bagian minus bisa diaktifkan': ("bisa: !aktif && K.diketahui && !minus.length && !tanpa.length", "bisa: !aktif && K.diketahui && !tanpa.length"),
    'aktivasi dengan buku kurang tidak ditolak': ("if (!d.cukup && !(opsi && opsi.tandai)) return { tolak: 'Wadah ' + W + ': ' + d.alasan, perluTandai:", "if (false) return { tolak: 'Wadah ' + W + ': ' + d.alasan, perluTandai:"),
    'aktivasi tandai tanpa selisihPerMerk': ("return tot > 0.004 ? { perluCocokkan: true, selisihKg: wbB2(tot), selisihPerMerk: per } : {};", "return {};"),
    'aktivasi tidak menutup kolam lama (karung terhitung dua kali)': ("    dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk: k.merk, isiKg: 0, wadah: W, pindahAwal: true } });\n", "\n"),
    # komposisi turunan
    'komposisi turunan mengabaikan isi ulang': ("tambah(x.merkAsal ? String(x.merkAsal) : asal(String(x.merk || '')), Number(x.kg) || 0)", "0"),
    'banding tidak disederhanakan': ("banding = k ? daftar.map(", "banding = false ? daftar.map("),
    # tanda untuk dicocokkan
    'cocokkan bertanggal SEBELUM dokumen dianggap tuntas': ("if (PS.some((q) => String(q.merk) === x.merk && String(q.tanggal || '') >= tgl)) return;", "if (PS.some((q) => String(q.merk) === x.merk)) return;"),
    'pindah bertanda tidak masuk pita Jual / kartu keempat': ("wbPindahTembusBelumCocok().forEach((x) => out.push(Object.assign({}, x, { trxId: 'takar' + x.id })));", ""),
    'trxId pindah bertanda tertimpa (semua dihitung satu nota)': ("out.push(Object.assign({}, x, { trxId: 'takar' + x.id }))", "out.push(Object.assign({ trxId: 'takar' + x.id }, x))"),
    # cek
    'cek dikosongkan tidak menyisihkan isi': ("if (K.totalKg > 0.004) { const r = wbSusunSisih(W, String(wbB2(K.totalKg)), w);", "if (false) { const r = wbSusunSisih(W, String(wbB2(K.totalKg)), w);"),
    'cek dikosongkan di wadah belum aktif lolos': ("if (h === 'kosong') { if (!aktif) return { tolak:", "if (h === 'kosong') { if (false) return { tolak:"),
    'Papan Kapur tidak menulis cek wadah': ("else if (w.tipe === 'cek') out.push(", "else if (false) out.push("),
    # selisih
    'selisih karung belakang (kolam vs buku) tidak disebut': ("wbKarungBelakangWadah(W).forEach((KB) => { if (KB.diketahui && Math.abs(KB.selisihKg) > 0.05) out.push(", "wbKarungBelakangWadah(W).forEach((KB) => { if (false) out.push("),
    'selisih wadah belum aktif tidak disebut': ("if (Math.abs(sel) > 0.05) { const stok = hitungStokKarungPerMerk();", "if (false) { const stok = hitungStokKarungPerMerk();"),
    # jual-logika.js
    'panel takar tidak menormalkan merek ke kunci karung belakang': ("return Object.assign({}, x, { merk: wbKunciKB(di, x.merk), merkAsal: x.merk, dari: di }); });", "return x; });"),
    'buka karung di belakang wadah aktif memakai jalur lama (buku tidak pindah)': ("if (di && wbAktif(di) && !wbBukuKhusus(merk)) {", "if (false) {"),
    'berat karung kunci belakang bukan berat merek asalnya': ("function beratKarungBuka(merk) { const asal = wbMerkAsal(merk);", "function beratKarungBuka(merk) { const asal = merk;"),
    'samakan karung belakang dibatasi satu karung (buku 100 ditolak)': ("const penuh = bwS && bwS.jenis === 'belakang' ? Math.max(beratKarungBuka(merk), wdB2((hitungStokKarungPerMerk()[merk] || {}).sisaKg || 0)) : beratKarungBuka(merk);", "const penuh = beratKarungBuka(merk);"),
    # putaran 39c: slot per wadah, hapus karung habis, kembalikan karung berbuku
    'kolam yang ditutup masih dianggap karung di belakang wadah': ("const hidup = Object.keys(perMerk).map((m) => perMerk[m]).filter((k) => !tutup(k));", "const hidup = Object.keys(perMerk).map((m) => perMerk[m]);"),
    'hapus karung yang masih berisi lolos': ("if (k.sisaMentahKg > 0.5) return { tolak: 'Karung ' + nama + ' ' + letak + ' belum habis", "if (false) return { tolak: 'Karung ' + nama + ' ' + letak + ' belum habis"),
    'hapus tidak mencatat susut buku karung belakang (buku 50 kg hilang diam-diam)': ("  if (buku > 0.5) {\n    if (!yakin) return", "  if (false) {\n    if (!yakin) return"),
    'kembalikan karung berbuku tidak memindah bukunya balik ke merek asal': ("if (berbuku && k.sisaMentahKg > 0.004) dokumen.push(wbDokPindah(", "if (false) dokumen.push(wbDokPindah("),
    'sisa karung yang kurang satu takar ditambal dari karung baru (tidak dihabiskan dulu) — panel − / +': ("const seadanya = k.diketahui && k.sisaKg > 0.004 && k.sisaKg + 0.004 < kgMinta; const kg = seadanya ? wdB2(k.sisaKg) : kgMinta;", "const seadanya = false; const kg = kgMinta;"),
    'sisa karung belakang yang kurang dari yang diminta ditambal dari karung baru — tiga ketukan': ("const seadanya = KB.bukuKg > 0.004 && KB.bukuKg + 0.004 < kg; const kgMinta = kg; if (seadanya) { kg = wbB2(KB.bukuKg); isiBaru = wbB2(tw.sisaNyataKg + kg); }", "const seadanya = false; const kgMinta = kg;"),
    # audit 39b no. 1: cek tutup toko = hari dagang (sebelum jam 12 = kemarin)
    'cek wadah sebelum jam 12 dihitung hari kalender (cek tutup lewat tengah malam jatuh ke hari baru)': ("if (String(d.jam || '') >= '12:00' || !d.jam) return String(d.tanggal || '');", "if (true) return String(d.tanggal || '');"),
    # akses.js (rules v5 di perangkat)
    'karyawan boleh menulis aturan wadah / titik samakan isi': ("if (x.koleksi === 'wadahLiteran' && TIPE_WADAH_STAF.indexOf(String(d.tipe || '')) < 0) return { tolak: tolakTindakan('atur') };", ""),
    'batch berisi kg lolos sebagai batch lahir': ("if (x.koleksi === 'batchMasuk' && !batchLahir(d)) return { tolak: tolakTindakan('kedatangan') };", ""),
    # tutup-buku-logika.js
    'tutup buku menandai karung belakang sebagai karung wadah': ("else if (bw[r.merk] && bw[r.merk].jenis === 'belakang') { r.karungBelakang = bw[r.merk].wadah; r.merkAsal = bw[r.merk].merk; }", "else if (false) { }"),
    # katalog HP kasir (wbSaringKatalogKasir)
    'katalog HP kasir menjual kunci karung belakang': ("const merkKarung = isi.merkKarung.filter((m) => !(bw[m.merk] && bw[m.merk].jenis !== 'wadah') &&", "const merkKarung = isi.merkKarung.filter((m) =>"),
}

if __name__ == '__main__':
    js = uji_wadah_stok_sendiri.bundel()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, (a, b) in RUSAK.items():
            if js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g, _ = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    # putaran 39c — statis layar: deretan 8 slot & hapus di stok.js, peringatan dua ketukan di wadah-panel.js, 4 kolom di Mac (stok.css)
    for nama, berkas, wajib in [('stok.js: deretan satu slot per wadah + slot kosong + hapus karung habis', 'baru/js/layar/stok.js', ['L.slotKarungWadah()', 'data-aksi="drKosong"', 'data-aksi="drHapus"', 'petak-wadah deretan-slot', 'L.karungLepasDeretan()']),
                                ('wadah-panel.js: karung baru dari tumpukan minta ketukan kedua (tiga ketukan & catat); sisa karung dituang seadanya dulu', 'baru/js/layar/wadah-panel.js', ['yakinBuka', "karung dari tumpukan?'", 'r.hitung.dibuka > 0 && !d.yakinBuka', 'x.bukaKarung || 0), 0) : 0;', "'ISI ULANG · seadanya '", 'dituang SEADANYA']),
                                ('audit 39b no. 1: K5 (uang.js) & lembar Cek wadah (jual.js) memakai tanggal tutup (lewat tengah malam = hari kemarin)', 'baru/js/layar/uang.js', ['const isoTutup = () => tanggalTutupAktif(kini());', 'WB.wbCekHari(isoTutup())', 'LEMBAR TUTUP HARI<br>${tanggalPendek(isoTutup())}', 'data-k="k5-lewat-malam"']),
                                ('audit 39b no. 1: lembar & tombol Cek wadah di Jual memakai tanggal tutup', 'baru/js/layar/jual.js', ['WB.wbCekHari(tanggalTutupAktif(s.sekarang || new Date()))']),
                                ('stok.css: Mac 4 kotak sebaris seperti HP + gaya slot kosong garis putus', 'baru/css/stok.css', ['.layar-stok .stok-wadah .petak-wadah { grid-template-columns: repeat(4, minmax(0, 1fr)); }', '.layar-stok .petak.slot.kosong { border-style: dashed;'])]:
        t = open(os.path.join(AKAR, berkas), encoding='utf-8').read(); kurang = [x for x in wajib if x not in t]
        if kurang: g.append('statis 39c · ' + nama + ' → tidak ada: ' + ' | '.join(kurang))
        else: l += 1
    print('WADAH SATU BUKU PER KOTAK (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    p = uji_wadah_bernama.cadangan_toko()
    if not p: print('ASAP DATA TOKO: dilewati — tidak ada _privat/backup-batch-*.json (worktree / CI)')
    if asap:
        if 'jatuh' in asap: g.append('asap data toko JATUH: ' + asap['jatuh']); print('   ✗ ' + g[-1])
        else:
            cetak_asap(os.path.basename(p), asap)
            for x in nilai_asap(asap): g.append('asap data toko: ' + x); print('   ✗ ' + g[-1])
    if p:
        sama, ket = uji_wadah_bernama.asap_global(p)
        print('ASAP GLOBAL (kode main vs cabang, %s): %s — %s' % (os.path.basename(p), 'BYTE-SAMA' if sama else 'BEDA / GAGAL', ket))
        if not sama: g.append('asap global: ' + ket)
    sys.exit(2 if g else 0)
