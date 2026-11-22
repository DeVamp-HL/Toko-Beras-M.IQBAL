#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_riwayat_uang.py — RIWAYAT & BATAL UANG (owner 22 Nov 2026, paket riwayat & pembatalan tahap 1), dijalankan ASLI di jsc di atas data contoh uji_uang_baru.py
+ titik kas 15 Sep, penutupan 15 Sep 21.00 (selisih +50.000), dan catatan uang buatan uji. Ditambah pemeriksaan pemasangan di Menu.

Kenapa ada: membatalkan catatan uang mengubah laci, rekening, brankas, amplop, bon, kasbon — dan, untuk hari yang sudah ditutup, selisih laci malam itu & patokan
kas. Yang paling mahal kalau salah: laba kena dua kali (biaya hilang tapi "lebih kas" malam itu tetap), patokan rekening yang tetap memuat catatan yang dibatalkan,
pendamping (biaya admin, amplop, pasangan pinjaman) yang tertinggal, kasbon yang jadi minus, titipan tablet yang tetap "disetujui", catatan buatan tutup hari /
nota yang dibatalkan lewat pintu yang salah, dan pulihkan yang tidak membalik semuanya.

    python3 alat-uji/uji_riwayat_uang.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_riwayat_uang.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json, copy, subprocess, tempfile

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru as UB  # noqa: E402
JSC = UB.JSC
RUL = 'baru/js/layar/riwayat-uang-logika.js'; MN = 'baru/js/layar/menu.js'; ML = 'baru/js/layar/menu-logika.js'; IDX = 'baru/index.html'
MODUL = list(dict.fromkeys(UB.MODUL + ['baru/js/data/hemat-baca.js', 'baru/js/layar/titipan-logika.js', RUL]))
STATIS = [MN, ML, IDX]


def kotak():
    K = copy.deepcopy(UB.KOTAK)
    K['pengaturan'] = [{'id': 'titikKas', 'tanggal': '2026-09-15', 'laci': 2000000, 'brankas': 10000000, 'rekening': 3000000, 'amplop': 1000000, 'diubahPada': '2026-09-15T14:00:00.000Z'}]
    K['tutupHari'] = [{'id': '2026-09-15', 'tanggal': '2026-09-15', 'jam': '21:00', 'selisih': 50000, 'selisihLaci': 50000, 'kasSeharusnya': 15950000, 'kasFisikLaci': 2000000, 'sistemBaru': True}]
    hk = lambda i, tgl, jam, n, **x: dict({'id': i, 'kategori': 'toko', 'untuk': 'toko', 'tanggal': tgl, 'jam': jam, 'keterangan': 'uji ' + i, 'nominal': n, 'dari': 'laci', 'oleh': 'Owner'}, **x)
    K['pengeluaranHarian'] = K.get('pengeluaranHarian', []) + [
        hk('ru-h1', '2026-09-15', '10:00', 50000),                                     # laci, hari tertutup (penutupan 21.00)
        hk('ru-h2', '2026-09-15', '10:30', 200000, dari='rekening'),                   # rekening, termuat titik 15 Sep
        hk('ru-h3', '2026-09-19', '11:00', 30000, dariPersetujuan='ru-tt', oleh='Ben (disetujui owner)'),   # dari titipan tablet
        hk('ru-h4', '2026-09-19', '11:30', 40000),                                     # dibiayai amplop ('amk-ru-h4')
        hk('ru-adm', '2026-09-19', '12:00', 2500, dari='laci', dariPindah='ru-p2', keterangan='Biaya admin'),
        hk('mdr-2026-09-15', '2026-09-15', '21:00', 1800, dari='rekening', mdr=True)]
    K['amplopLaba'] = K.get('amplopLaba', []) + [{'id': 'amk-ru-h4', 'tanggal': '2026-09-19', 'jam': '11:30', 'tipe': 'ambil', 'nominal': 40000, 'ke': 'laci', 'untuk': 'ru-h4'}]
    K['pindahUang'] = [{'id': 'ru-p2', 'tanggal': '2026-09-19', 'jam': '12:00', 'dari': 'laci', 'ke': 'rekening', 'nominal': 100000, 'biayaAdmin': 2500, 'adminNama': 'transfer', 'oleh': 'Owner'}]
    K['kasbonMutasi'] = K.get('kasbonMutasi', []) + [
        {'id': 'ru-k1', 'tipe': 'ambil', 'namaPegawai': 'Pegawai Uji', 'nominal': 100000, 'tanggal': '2026-09-19', 'jam': '09:00', 'dari': 'laci', 'oleh': 'Owner'},
        {'id': 'ru-k2', 'tipe': 'bayar', 'namaPegawai': 'Pegawai Uji', 'nominal': 60000, 'tanggal': '2026-09-19', 'jam': '13:00', 'caraBayar': 'Tunai', 'oleh': 'Owner'}]
    K['utangOwnerMutasi'] = K.get('utangOwnerMutasi', []) + [{'id': 'ru-u1', 'tipe': 'saldoAwal', 'pinjaman': True, 'nominal': 500000, 'tanggal': '2026-09-19', 'jam': '14:00', 'catatan': 'Pinjaman owner ke toko — uji'}]
    K['modalOwner'] = K.get('modalOwner', []) + [{'id': 'ru-m1', 'tipe': 'setor', 'pinjaman': True, 'pasangan': 'ru-u1', 'nominal': 500000, 'tanggal': '2026-09-19', 'jam': '14:00', 'catatan': 'Pinjaman owner', 'tempat': 'laci'}]
    K['piutangMutasi'] = K.get('piutangMutasi', []) + [{'id': 'ru-b1', 'tipe': 'bayar', 'namaPelanggan': 'Bu Uji', 'nominal': 75000, 'tanggal': '2026-09-19', 'jam': '15:00', 'caraBayar': 'Tunai', 'notaTrxId': 'trx-9'}]
    K['persetujuan'] = K.get('persetujuan', []) + [{'id': 'ru-tt', 'tindakan': 'uangKeluar', 'status': 'disetujui', 'jenis': 'toko', 'nominal': 30000, 'teks': 'bensin', 'mintaUid': 'uid-tablet', 'dari': 'Ben', 'tanggal': '2026-09-19', 'jam': '11:00'}]
    K['bukuHapus'] = [{'id': 'bh-lama', 'tanggal': '2026-09-10', 'jam': '09:00', 'koleksi': 'batchMasuk', 'idDok': 'b9', 'tanggalDok': '2026-09-01', 'ringkas': 'kedatangan lama', 'alasan': 'salah'}]
    return K


SKENARIO = r"""
var hasil = []; var J = JSON.stringify;
function cek(nama, ok, ket) { hasil.push({ nama: nama, ok: !!ok, ket: ket === undefined ? '' : (typeof ket === 'string' ? ket : J(ket)) }); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var _id = 0; var W = { tanggal: '2026-09-19', jam: '16:00', kini: '2026-09-19T09:00:00.000Z', idUnik: function () { return 'u' + (++_id); } };
var cacheDari = function (k) { return (KOLEKSI.find(function (x) { return x.nama === k; }) || {}).cache; };
var terap = function (r) {
  (r.hapus || []).forEach(function (x) { pasok(x.koleksi, cacheMentah(cacheDari(x.koleksi)).filter(function (d) { return String(d.id) !== String(x.id); })); });
  (r.dokumen || []).forEach(function (x) { var a = cacheMentah(cacheDari(x.koleksi)).slice(); var i = a.findIndex(function (d) { return String(d.id) === String(x.data.id); }); if (i >= 0) a[i] = x.data; else a.push(x.data); pasok(x.koleksi, a); });
};
var ada = function (k, id) { return cacheMentah(cacheDari(k)).some(function (d) { return String(d.id) === String(id); }); };
var tutup15 = function () { return ambilTutupHari().find(function (t) { return t.tanggal === '2026-09-15'; }); };

// ---------- daftar ----------
var D19 = ruDaftar('2026-09-19', ''); var kunci19 = D19.map(function (b) { return b.kunci; });
cek('daftar 19 Sep: kepala kelompok saja — admin pindah & amplop pendamping & pasangan pinjaman tidak tampil sendiri', kunci19.indexOf('pindahUang|ru-p2') >= 0 && kunci19.indexOf('pengeluaranHarian|ru-adm') < 0
  && kunci19.indexOf('amplopLaba|amk-ru-h4') < 0 && kunci19.indexOf('utangOwnerMutasi|ru-u1') >= 0 && kunci19.indexOf('modalOwner|ru-m1') < 0, kunci19);
var bP = D19.find(function (b) { return b.id === 'ru-p2'; }); var bH4 = D19.find(function (b) { return b.id === 'ru-h4'; });
cek('kelompok: pindah uang + biaya admin; uang keluar + ambilan amplop', bP && bP.anggota === 1 && bH4 && bH4.anggota === 1, [bP && bP.anggota, bH4 && bH4.anggota]);
var bB = D19.find(function (b) { return b.id === 'ru-b1'; });
cek('bayar bon bersama nota → tidak di sini (batal nota)', bB && !bB.bisa && /Jual › Riwayat/.test(bB.sebab), bB);
var bM = ruDaftar('2026-09-15', '').find(function (b) { return b.id === 'mdr-2026-09-15'; });
cek('potongan QRIS tutup hari → tutup ulang, bukan batal', bM && !bM.bisa && /tutup ulang/.test(bM.sebab) && !!ruSusunBatal('pengeluaranHarian', 'mdr-2026-09-15', 'salah', W).tolak, bM);
cek('saring per orang', ruDaftar('2026-09-19', 'Ben (disetujui owner)').every(function (b) { return b.oleh === 'Ben (disetujui owner)'; }) && ruOrang('2026-09-19').indexOf('Owner') >= 0);
cek('membatalkan butuh alasan', /alasan/.test(ruSusunBatal('pengeluaranHarian', 'ru-h4', '  ', W).tolak || ''));

// ---------- uang keluar laci di hari yang SUDAH DITUTUP ----------
var R1 = ruSusunBatal('pengeluaranHarian', 'ru-h1', 'Salah catat', W);
var A1 = R1.dokumen ? R1.dokumen[0].data : {}; var T1 = (R1.dokumen || []).filter(function (x) { return x.koleksi === 'tutupHari'; })[0];
cek('batal uang keluar laci hari tertutup: arsip bukuHapus berisi salinan utuh + alasan; catatan dihapus dari buku', A1.jenisBatal === 'uang' && A1.dokumen.length === 1 && A1.dokumen[0].data.id === 'ru-h1' && A1.alasan === 'Salah catat'
  && J(R1.hapus) === J([{ koleksi: 'pengeluaranHarian', id: 'ru-h1' }]), A1);
cek('hari tertutup: selisih malam 15 Sep +50.000 → 0 (uang tidak pernah keluar), kasSeharusnya +50.000, jejak koreksiBatal', T1 && T1.data.selisih === 0 && T1.data.selisihLaci === 0 && T1.data.kasSeharusnya === 16000000
  && T1.data.koreksiBatal.length === 1 && T1.data.koreksiBatal[0].geser === -50000, T1 && T1.data);
cek('laci tidak menyentuh patokan kas (hitungan fisik tetap)', !(R1.dokumen || []).some(function (x) { return x.koleksi === 'pengaturan'; }));
terap(R1);
cek('sesudah batal: catatan hilang dari buku, arsip ada di daftar Dibatalkan', !ada('pengeluaranHarian', 'ru-h1') && ruDibatalkan().some(function (x) { return x.id === A1.id && x.bisaPulih; }));
var P1 = ruSusunPulih(A1.id, W); terap(P1);
cek('pulihkan: catatan kembali (id sama), selisih 15 Sep kembali +50.000, arsip hilang', ada('pengeluaranHarian', 'ru-h1') && tutup15().selisih === 50000 && tutup15().kasSeharusnya === 15950000 && !ada('bukuHapus', A1.id), tutup15());
cek('pulihkan dua kali ditolak', !!ruSusunPulih(A1.id, W).tolak);

// ---------- uang keluar REKENING termuat patokan kas ----------
var R2 = ruSusunBatal('pengeluaranHarian', 'ru-h2', 'Salah catat', W); var TK = (R2.dokumen || []).filter(function (x) { return x.koleksi === 'pengaturan'; })[0];
cek('batal uang keluar rekening sebelum titik: patokan rekening +200.000, diubahPada maju 1 ms (dokumen menang di semua perangkat), tanpa geser selisih laci',
  TK && TK.data.rekening === 3200000 && TK.data.laci === 2000000 && TK.data.diubahPada === '2026-09-15T14:00:00.001Z' && !(R2.dokumen || []).some(function (x) { return x.koleksi === 'tutupHari'; }), TK && TK.data);
terap(R2); var S2 = saldoKantong('2026-09-19');
var P2 = ruSusunPulih(R2.dokumen[0].data.id, W); terap(P2);
cek('pulihkan rekening: patokan rekening kembali 3.000.000', ambilTitikKas().rekening === 3000000, ambilTitikKas());

// ---------- kelompok: pindah uang + admin, uang keluar + amplop ----------
var R3 = ruSusunBatal('pindahUang', 'ru-p2', 'Dobel', W);
cek('batal pindah uang ikut biaya adminnya (satu arsip, dua catatan dihapus)', J(R3.hapus.map(function (x) { return x.id; }).sort()) === J(['ru-adm', 'ru-p2']) && R3.dokumen[0].data.dokumen.length === 2, R3.hapus);
var R4 = ruSusunBatal('pengeluaranHarian', 'ru-h4', 'Salah', W);
cek('batal uang keluar ikut ambilan amplop pembiayaannya', J(R4.hapus.map(function (x) { return x.id; }).sort()) === J(['amk-ru-h4', 'ru-h4']), R4.hapus);
var R5 = ruSusunBatal('utangOwnerMutasi', 'ru-u1', 'Salah', W);
cek('batal pinjaman owner ikut pasangan modalnya', J(R5.hapus.map(function (x) { return x.id; }).sort()) === J(['ru-m1', 'ru-u1']), R5.hapus);
cek('pendamping dibatalkan lewat kepalanya (admin pindah → kelompok pindah)', J(ruSusunBatal('pengeluaranHarian', 'ru-adm', 'x', W).hapus.map(function (x) { return x.id; }).sort()) === J(['ru-adm', 'ru-p2']));

// ---------- kasbon: tidak boleh minus ----------
cek('batal kasbon yang sudah dicicil ditolak (sisa minus)', /dicicil/.test(ruSusunBatal('kasbonMutasi', 'ru-k1', 'x', W).tolak || ''));
terap(ruSusunBatal('kasbonMutasi', 'ru-k2', 'Salah', W));
cek('sesudah cicilannya dibatalkan, kasbonnya boleh dibatalkan', !ruSusunBatal('kasbonMutasi', 'ru-k1', 'x', W).tolak);

// ---------- titipan tablet ----------
var R6 = ruSusunBatal('pengeluaranHarian', 'ru-h3', 'Bukan uang toko', W); var tt = (R6.dokumen || []).filter(function (x) { return x.koleksi === 'persetujuan'; })[0];
cek('batal uang dari titipan: titipan tablet ikut ditandai dibatalkan owner (status ditolak + alasan + tanda batalOwner)', tt && tt.data.status === 'ditolak' && /^Dibatalkan owner: Bukan uang toko/.test(tt.data.alasanTolak) && tt.data.batalOwner === R6.dokumen[0].data.id, tt && tt.data);
terap(R6); terap(ruSusunPulih(R6.dokumen[0].data.id, W));
cek('pulihkan: titipan kembali disetujui seperti semula', (cacheMentah('persetujuan').find(function (m) { return m.id === 'ru-tt'; }) || {}).status === 'disetujui' && ada('pengeluaranHarian', 'ru-h3'));

// ---------- hapus permanen & bulan terkunci ----------
var R7 = ruSusunBatal('pengeluaranHarian', 'ru-h4', 'Salah', W); terap(R7); var idA = R7.dokumen[0].data.id;
var H7 = ruSusunHapusPermanen(idA);
cek('hapus permanen = hanya baris Dibatalkan yang hilang', J(H7.hapus) === J([{ koleksi: 'bukuHapus', id: idA }]) && !H7.dokumen);
cek('baris Dibatalkan lama (hapus kedatangan tanpa salinan) tampil, tidak bisa dipulihkan, bisa dihapus permanen', (function () { var x = ruDibatalkan().find(function (b) { return b.id === 'bh-lama'; }); return x && !x.bisaPulih && !!ruSusunPulih('bh-lama', W).tolak && !ruSusunHapusPermanen('bh-lama').tolak; })());
/*TAMPILAN*/
// arsip masih ada TAPI catatan bernomor sama sudah tertulis lagi (perangkat lain menulis ulang salinan lamanya) → pulihkan ditolak (tidak ditulis dua kali)
var R8 = ruSusunBatal('pindahUang', 'ru-p2', 'Dobel', W); terap(R8);
terap({ dokumen: [{ koleksi: 'pindahUang', data: R8.dokumen[0].data.dokumen.filter(function (x) { return x.koleksi === 'pindahUang'; })[0].data }] });
cek('pulihkan ditolak bila catatan bernomor sama sudah ada lagi', /sudah ada lagi/.test(ruSusunPulih(R8.dokumen[0].data.id, W).tolak || ''));
pasok('aturanToko', cacheMentah('aturan').concat([{ id: 'kunciPeriode', sampaiBulan: '2026-09', riwayat: [] }]));
cek('bulan terkunci: batal & pulihkan ditolak', !!ruSusunBatal('pengeluaranHarian', 'ru-h3', 'x', W).tolak && !!ruSusunPulih(idA, W).tolak);
print(J(hasil));
"""


def baca_semua():
    return dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(MODUL + STATIS)))


def rakit(t):
    isi = lambda m: t[m] if m in t else open(os.path.join(AKAR, m), encoding='utf-8').read()
    return '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(isi(m)) for m in bundel_baru.lengkapi(MODUL)])


def tampilan(t):
    """Panel Menu dijalankan ASLI di jsc: gambarRiwayat dipotong dari menu.js, h/esc dari inti/dom.js (keduanya hanya string), RU = fungsi logika di bundel."""
    M = t[MN]; i = M.find('  function gambarRiwayat(s, tab) {'); j = M.find('  function gambarPengingat(', i)
    if i < 0 or j < 0: return "cek('tampilan: gambarRiwayat ada di menu.js', false);"
    D = open(os.path.join(AKAR, 'baru/js/inti/dom.js'), encoding='utf-8').read(); a = D.find('export const esc'); b = D.find('export const mentah')
    dom = D[a:b].replace('export ', '')
    return ("(function () {\n" + dom + "\nvar RU = { RU_ALASAN: RU_ALASAN, ruDaftar: ruDaftar, ruOrang: ruOrang, ruPeriksa: ruPeriksa, ruDibatalkan: ruDibatalkan };\n"
            "var kini = function () { return new Date('2026-09-19T12:00:00'); };\n" + M[i:j] + r"""
try {
  var g1 = gambarRiwayat({ ruHari: '2026-09-19', ruSaring: '', ruBuka: 'pengeluaranHarian|ru-h3', ruAlasan: 'Salah catat', yakinRu: 'b:pengeluaranHarian|ru-h3' }, 'uang').html;
  cek('tampilan Uang: baris catatan + tombol Batalkan, alasan, akibat, ketukan kedua', /data-aksi="ruBuka" data-k-ru="pengeluaranHarian\|ru-h3"/.test(g1) && /KETUK LAGI · BATALKAN/.test(g1)
    && /data-aksi="ruAlasan" data-a="Salah catat"/.test(g1) && /data-ketik="ruAlasanKetik"/.test(g1) && /data-k="ru-buka"/.test(g1) && !/undefined|NaN|\[object/.test(g1), g1.slice(0, 600));
  var g0 = gambarRiwayat({ ruHari: '', ruSaring: '', ruBuka: null, ruAlasan: '', yakinRu: null }, 'uang').html;
  cek('tampilan Uang tanpa hari pilihan = hari ini (19 Sep), tanpa tombol "hari ini"', /data-aksi="ruGeser" data-d="1"/.test(g0) && !/data-d="0"/.test(g0) && !/undefined|NaN/.test(g0), g0.slice(0, 300));
  var g2 = gambarRiwayat({ yakinRu: 'h:bh-lama' }, 'batal').html;
  cek('tampilan Dibatalkan: baris arsip + Pulihkan (batal uang) + Hapus permanen (ketukan kedua)', /data-aksi="ruPulih"/.test(g2) && /data-aksi="ruHapus" data-id="bh-lama"/.test(g2)
    && /KETUK LAGI · hapus permanen/.test(g2) && !/undefined|NaN|\[object/.test(g2), g2.slice(0, 600));
} catch (e) { cek('tampilan: gambarRiwayat jalan tanpa galat', false, String(e && e.stack || e)); }
})();
""")


def jalankan(t):
    js = UB.JAM_TETAP + rakit(t) + '\nvar KOTAK = ' + json.dumps(kotak()) + ';\n' + SKENARIO.replace('/*TAMPILAN*/', tampilan(t))
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    keluar = (r.stdout or '').strip().split('\n')[-1] if r.stdout else ''
    if r.returncode != 0 or not keluar.startswith('['): return [{'nama': 'jsc jalan', 'ok': False, 'ket': ((r.stderr or '') + (r.stdout or ''))[-1500:]}]
    return json.loads(keluar)


def periksa_statis(t):
    c = []; ok = lambda n, x, k='': c.append({'nama': 'statis: ' + n, 'ok': bool(x), 'ket': k})
    M = t[MN]
    ok('Menu: panel Riwayat & batal (Uang · Dibatalkan) hanya untuk owner', "riwayat: [['uang', 'Uang'], ['barang', 'Barang'], ['batal', 'Dibatalkan']]" in M and "s.sistem === 'riwayat' ? gambarRiwayat(s, tab)" in M)
    ok('Menu: batal = alasan + ketukan kedua; pulihkan; hapus permanen = ketukan kedua', 'data-aksi="ruBatal"' in M and 'data-aksi="ruPulih"' in M and 'data-aksi="ruHapus"' in M
       and "(brg ? RB.rbSusunBatal : RU.ruSusunBatal)(" in M and ": RU.ruSusunPulih)(id, waktu())" in M and "RU.ruSusunHapusPermanen(" in M and 'yakinRu' in M)
    ok('Menu laci Toko ini: baris Riwayat & batal', "baris('riwayat'," in t[ML] and "sistem: 'riwayat'" in t[ML])
    ok('index.html memuat riwayat-uang-logika (modulepreload)', '<link rel="modulepreload" href="js/layar/riwayat-uang-logika.js">' in t[IDX])
    ok('logika riwayat tidak menulis sendiri', not re.search(r'tulisDokumen|setDoc|writeBatch|import .*firebase', t[RUL]))
    return c


ASAP = r"""
var hasil = []; var J = JSON.stringify;
var cacheDari = function (k) { return (KOLEKSI.find(function (x) { return x.nama === k; }) || {}).cache; };
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var terap = function (r) {
  (r.hapus || []).forEach(function (x) { pasok(x.koleksi, cacheMentah(cacheDari(x.koleksi)).filter(function (d) { return String(d.id) !== String(x.id); })); });
  (r.dokumen || []).forEach(function (x) { var a = cacheMentah(cacheDari(x.koleksi)).slice(); var i = a.findIndex(function (d) { return String(d.id) === String(x.data.id); }); if (i >= 0) a[i] = x.data; else a.push(x.data); pasok(x.koleksi, a); });
};
var KOL = ['pengeluaranHarian', 'pindahUang', 'kasbonMutasi', 'utangOwnerMutasi', 'modalOwner', 'amplopLaba', 'utangPemasokMutasi', 'piutangMutasi', 'tutupHari', 'pengaturan', 'persetujuan', 'bukuHapus'];
var BUANG = { koreksiBatal: 1, diubahPada: 1 };
var potret = function () { return J(KOL.map(function (k) { return cacheMentah(cacheDari(k)).map(function (d) { var o = {}; Object.keys(d).sort().forEach(function (f) { if (!BUANG[f]) o[f] = d[f]; }); return o; })
  .sort(function (a, b) { return String(a.id).localeCompare(String(b.id)); }); })); };
var samar = function (t) { return String(t).replace(/^Kasbon .*? ini /, 'Kasbon (nama) ini ').slice(0, 60); };   // keluaran tanpa nama orang
var hari = {}; KOL.slice(0, 8).forEach(function (k) { cacheMentah(cacheDari(k)).forEach(function (d) { if (d.tanggal) hari[String(d.tanggal).slice(0, 10)] = 1; }); });
var H = Object.keys(hari).sort(); var baris = 0, bisa = 0, galat = [], bolak = 0, tolakSusun = {}, tertutup = 0;
H.forEach(function (iso) {
  var D; try { D = ruDaftar(iso, ''); } catch (e) { galat.push(iso + ' ruDaftar: ' + e); return; }
  D.forEach(function (b) { baris++; if (!b.bisa) return; bisa++;
    try {
      var P = ruPeriksa(b.koleksi, b.id); if (P.tolak) { tolakSusun[samar(P.tolak)] = (tolakSusun[samar(P.tolak)] || 0) + 1; return; }
      var awal = potret(); var R = ruSusunBatal(b.koleksi, b.id, 'asap', { tanggal: '2026-12-31', jam: '23:00', kini: '2026-12-31T16:00:00.000Z', idUnik: function () { return 'asap-' + b.kunci; } });
      if (R.tolak) { tolakSusun[samar(R.tolak)] = (tolakSusun[samar(R.tolak)] || 0) + 1; return; }
      if ((R.dokumen || []).some(function (x) { return x.koleksi === 'tutupHari'; })) tertutup++;
      terap(R); var Pl = ruSusunPulih(R.dokumen[0].data.id, { tanggal: '2026-12-31', jam: '23:01', kini: '2026-12-31T16:01:00.000Z', idUnik: function () { return 'x'; } });
      if (Pl.tolak) { galat.push(b.kunci + ' pulih ditolak: ' + Pl.tolak); return; }
      terap(Pl); if (potret() !== awal) galat.push(b.kunci + ' batal → pulihkan TIDAK kembali persis'); else bolak++;
    } catch (e) { galat.push(b.kunci + ': ' + (e && e.stack || e)); }
  });
});
var DB; try { DB = ruDibatalkan().length; } catch (e) { galat.push('ruDibatalkan: ' + e); }
print(J({ hari: H.length, baris: baris, bisa: bisa, bolak: bolak, tertutup: tertutup, tolak: tolakSusun, dibatalkan: DB, galat: galat.slice(0, 8), nGalat: galat.length }));
"""


def asap(t):
    """Data toko asli (cadangan lokal di _privat/ atau _arsip-mockup/, tidak pernah di git): tiap catatan uang yang bisa dibatalkan → batal lalu pulihkan wajib kembali PERSIS
    (abaikan jejak koreksiBatal & cap diubahPada). Hanya dihitung di cache uji — tidak menulis apa pun."""
    import glob
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')), key=os.path.basename)
    if not cad: return [], None
    c = json.load(open(cad[-1], encoding='utf-8'))
    js = UB.JAM_TETAP + rakit(t) + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    keluar = (r.stdout or '').strip().split('\n')[-1] if r.stdout else ''
    if r.returncode != 0 or not keluar.startswith('{'): return [{'nama': 'asap data toko: jsc jalan', 'ok': False, 'ket': ((r.stderr or '') + (r.stdout or ''))[-1500:]}], None
    h = json.loads(keluar)
    return [{'nama': 'asap data toko: semua catatan uang tergambar & batal → pulihkan kembali persis', 'ok': h['nGalat'] == 0 and h['bolak'] > 0, 'ket': h['galat']}], (os.path.basename(cad[-1]), h)


def periksa(t, diam=False):
    c = jalankan(t) + periksa_statis(t)
    g = [x for x in c if not x['ok']]
    if not diam:
        for x in c: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:700]))
        print('RIWAYAT & BATAL UANG: %d lulus · %d gagal' % (len(c) - len(g), len(g)))
        a, info = asap(t)
        for x in a: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:900]))
        g = g + [x for x in a if not x['ok']]
        if info:
            for x in []: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:900]))
            n, h = info
            print('ASAP DATA TOKO (%s): %d hari · %d catatan uang · %d bisa dibatalkan · %d bolak-balik persis (%d menyentuh hari tertutup) · ditolak: %s · Dibatalkan %s'
                  % (n, h['hari'], h['baris'], h['bisa'], h['bolak'], h['tertutup'], json.dumps(h['tolak'], ensure_ascii=False), h['dibatalkan']))
    return g


def main():
    t = baca_semua()
    if '--kontrol' in sys.argv:
        R = t[RUL]
        rusak = [
            ('hari tertutup: selisih malam itu tidak dibetulkan (laba kena dua kali)', RUL, R.replace("  if (e.laci) {\n    const T = ruPenutupan(String(kepala.tanggal || ''), kepala.jam);\n    if (T) {\n      const geser", "  if (false) {\n    const T = ruPenutupan(String(kepala.tanggal || ''), kepala.jam);\n    if (T) {\n      const geser")),
            ('selisih digeser ke arah yang salah', RUL, R.replace("const geser = arah < 0 ? e.laci : -e.laci;", "const geser = arah < 0 ? -e.laci : e.laci;")),
            ('patokan rekening tidak dibetulkan', RUL, R.replace("  let titik = null;\n  if (ruDalamTitik(kepala)) {", "  let titik = null;\n  if (false) {")),
            ('patokan dibetulkan tanpa memajukan diubahPada (salinan perangkat lama menang)', RUL, R.replace("const baru = Object.assign({}, t, { id: 'titikKas' }, t.diubahPada ? { diubahPada: ruMajuSedikit(t.diubahPada) } : {}); Object.keys(ubah).forEach((k) => { baru[k] = (Number(t[k]) || 0) + ubah[k]; });\n      dokumen.push",
                                                                                                    "const baru = Object.assign({}, t, { id: 'titikKas' }); Object.keys(ubah).forEach((k) => { baru[k] = (Number(t[k]) || 0) + ubah[k]; });\n      dokumen.push")),
            ('biaya admin tertinggal saat pindah uang dibatalkan', RUL, R.replace("if (koleksi === 'pindahUang' && String(h.dariPindah || '') === sid) out.push", "if (false) out.push")),
            ('ambilan amplop tertinggal', RUL, R.replace("ambilAmplopLaba().forEach((a) => { if (String(a.id) === 'amk-' + sid) out.push", "ambilAmplopLaba().forEach((a) => { if (false) out.push")),
            ('pasangan pinjaman tertinggal', RUL, R.replace("if (koleksi === 'utangOwnerMutasi' && k.pinjaman) ambilModalOwner()", "if (false) ambilModalOwner()")),
            ('kasbon boleh jadi minus', RUL, R.replace("if (sisa - ruN(kb.data.nominal) < -0.5) return", "if (false) return")),
            ('titipan tablet tetap disetujui', RUL, R.replace("tt.map((p) => ({ koleksi: 'persetujuan', data: Object.assign({}, p, { status: 'ditolak',", "[].map((p) => ({ koleksi: 'persetujuan', data: Object.assign({}, p, { status: 'ditolak',")),
            ('potongan QRIS tutup hari boleh dibatalkan di sini', RUL, R.replace("if (koleksi === 'pengeluaranHarian' && (d.mdr || /^mdr-/.test(id))) return", "if (false) return")),
            ('pembayaran bersama nota boleh dibatalkan di sini', RUL, R.replace("if (koleksi === 'piutangMutasi' && (d.notaTrxId || d.dariNota)) return", "if (false) return")),
            ('pulihkan tidak membalik selisih', RUL, R.replace("if (T) { const geser = -e.laci; dokumen.push(", "if (false) { const geser = -e.laci; dokumen.push(")),
            ('pulihkan boleh dua kali', RUL, R.replace("if (ruCari(d.koleksi, d.data.id)) return { tolak:", "if (false) return { tolak:")),
            ('bulan terkunci boleh dibatalkan', RUL, R.replace("for (const x of K) { const k = tolakKunci(x.koleksi, x.data, 'bulan itu sudah dikunci — catatan tidak bisa dibatalkan lagi'); if (k) return { tolak: k }; }", "")),
            ('batal tanpa alasan', RUL, R.replace("if (!a) return { tolak: 'Membatalkan butuh alasan' };", "")),
            ('tombol Batalkan tidak tergambar', MN, t[MN].replace('data-aksi="ruBuka" data-k-ru=', 'data-k-ru=')),
            ('panel memakai nama yang tidak ada (layar jatuh)', MN, t[MN].replace("{ daftar: RU.ruDaftar, orang: RU.ruOrang, periksa: RU.ruPeriksa }", "{ daftar: RU.ruDaftarX, orang: RU.ruOrang, periksa: RU.ruPeriksa }")),
        ]
        kode = 0
        for nama, berkas, isi in rusak:
            if isi == t[berkas]: print('KONTROL BASI  ' + nama); kode = 3; continue
            t2 = dict(t); t2[berkas] = isi; g = periksa(t2, diam=True)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + (' → ' + g[0]['nama'][:100] if g else ''))
            if not g: kode = 3
        print('KONTROL: %d kerusakan' % len(rusak)); sys.exit(kode)
    sys.exit(1 if periksa(t) else 0)


if __name__ == '__main__':
    main()
