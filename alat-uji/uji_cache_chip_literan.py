#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_cache_chip_literan.py — audit 39b no. 29: rak Literan (Jual) & tab Wadah literan (Stok) tidak menghitung ulang komposisi turunan / selisih / cek wadah
(dan buku semua wadah, daftar aktivasi, karung tertinggal di Stok) pada KETUKAN atau HURUF yang tidak mengubah data — tapi TIDAK PERNAH basi:
data baru, isi keranjang Jual, atau tanggal berganti → dihitung ulang.
Berkas layar ASLI (baru/js/layar/jual.js, stok.js) dijalankan di jsc — TANPA peramban: impor DOM/gerak/adegan/gambar diganti tiruan kosong,
modul logika & data asli dibundel satu lingkup (pola uji_wadah_stok_sendiri). Hitungan = berapa kali fungsi WB./S. itu dibaca layar per ketukan.
KOTAK PASIR = uji_wadah_satu_buku.KOTAK (5 wadah, W1 IR64 Apex diaktifkan di sini), jam dikunci 21 Sep 2026 10:00 WIB.
Cadangan toko di _privat/ (lokal saja; dilewati di CI): ongkos per ketukan dalam ms, sebelum ingatan (hitung ulang paksa) vs sesudah.

    python3 alat-uji/uji_cache_chip_literan.py            → N lulus · 0 gagal
    python3 alat-uji/uji_cache_chip_literan.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_wadah_bernama, uji_wadah_stok_sendiri, uji_wadah_satu_buku  # noqa: E402

TAMBAH = ['baru/js/layar/riwayat-logika.js', 'baru/js/inti/dom.js', 'baru/js/inti/kunci.js', 'baru/js/inti/isian.js']
# impor layar yang menyentuh peramban → tiruan (nama yang diimpor jadi fungsi kosong; beberapa diberi bentuk)
TIRUAN = {'../inti/jadwal.js', '../inti/gerak.js', './adegan.js', './gambar.js', './wadah-panel.js', './akses-layar.js', '../inti/keadaan.js', '../inti/dom.js'}
BENTUK = {'nanti': 'function (f) { f(); }', 'segera': 'function (f) { f(); }', 'aksiPanelWadah': 'function () { return {}; }', 'drafIsi': 'function () { return {}; }',
          'tombolAkun': "function () { return { boleh: true, kalimat: '' }; }", 'tombolLuarKisi': "function () { return { boleh: true, kalimat: '' }; }",
          'bukanOwner': 'function () { return false; }', 'batasBarisNota': 'function () { return null; }', 'batasHasilAdukan': 'function () { return null; }',
          'pasang': 'function (akar, isi) { akar.__html = isi && isi.__mentah ? isi.html : String(isi || ""); }', 'delegasi': 'function (akar, p) { akar.__aksi = p; }',
}


def bungkus(berkas, nama_fungsi, keadaan_js):
    """Satu layar dalam fungsinya sendiri: impor namespace → proksi penghitung, impor peramban → tiruan, keadaan.js sinkron (tanpa queueMicrotask)."""
    t = open(os.path.join(AKAR, berkas), encoding='utf-8').read(); baris = []
    isi = re.sub(r"^import\s[^;]*;.*$", '', t, flags=re.M)   # impor berkomentar di ujung baris ikut dibuang (polos() hanya yang tanpa komentar)
    for m in re.finditer(r"^import\s+\*\s+as\s+(\w+)\s+from\s+'([^']+)';", t, flags=re.M): baris.append('var %s = __ns;' % m.group(1))
    for m in re.finditer(r"^import\s+\{([^}]*)\}\s+from\s+'([^']+)';", t, flags=re.M):
        if m.group(2) not in TIRUAN: continue
        for n in [x.strip() for x in m.group(1).split(',') if x.strip()]:
            if n in ('buatKeadaan', 'h', 'mentah', 'gabung', 'esc'): continue   # keadaan.js sinkron di bawah; h/mentah/gabung/esc = dom.js asli (dibundel)
            baris.append('var %s = %s;' % (n, BENTUK.get(n, "function () { return ''; }")))
    return ('var %s = (function () {\n  var queueMicrotask = undefined; var setTimeout = function () { return 0; }; var clearTimeout = function () {};\n'
            '  var document = { body: { classList: { toggle: function () {}, add: function () {}, remove: function () {} } }, hidden: false, querySelector: function () { return null; }, getElementById: function () { return null; } };\n'
            '  var innerHeight = 800, innerWidth = 1200;\n%s\n%s\n%s\n  return %s;\n})();\n') % (nama_fungsi, keadaan_js, '\n'.join(baris), bundel_baru.polos(isi), nama_fungsi)


def bundel(ganti=None):
    js = uji_wadah_stok_sendiri.bundel() + ''.join('\n// ===== ' + m + ' =====\n' + bundel_baru.polos(open(os.path.join(AKAR, m), encoding='utf-8').read()) for m in TAMBAH)
    kead = bundel_baru.polos(open(os.path.join(AKAR, 'baru/js/inti/keadaan.js'), encoding='utf-8').read())
    lay = bungkus('baru/js/layar/jual.js', 'pasangLayarJual', kead) + bungkus('baru/js/layar/stok.js', 'pasangLayarStok', kead)
    app = open(os.path.join(AKAR, 'baru/js/app.js'), encoding='utf-8').read()
    for (lama, baru) in (ganti or []):
        n = lay.count(lama) + app.count(lama); assert n == 1, 'kontrol basi: ' + lama[:90] + ' (' + str(n) + '×)'
        lay = lay.replace(lama, baru); app = app.replace(lama, baru)
    return js, lay, app


PROKSI = r"""
var __hitung = {}; var __ns = new Proxy({}, { get: function (t, k) { if (typeof k !== 'string') return undefined; __hitung[k] = (__hitung[k] || 0) + 1;
  try { return (0, eval)(k); } catch (e) { return undefined; } } });
var __nStok = 0; hitungStokKarungPerMerk = (function (f) { return function () { __nStok++; return f.apply(this, arguments); }; })(hitungStokKarungPerMerk);
var __versi = 0; dengarkan(function () { __versi += 1; });   // = app.js: let versi; dengarkan(() => { versi += 1; })
setelKunci(false);   // tirai 23c: layar baru menggambar sesudah app.js membuka tirai (owner / mode cadangan)
var __akar = function () { return { querySelector: function () { return null; }, querySelectorAll: function () { return []; }, firstElementChild: null, classList: { add: function () {}, remove: function () {}, toggle: function () {} }, addEventListener: function () {} }; };
var BERAT = ['wbKomposisiTurunan', 'wbSelisihWadah', 'wbCekHari'];
var BERAT_STOK = ['susunWadah', 'wbDaftarAktivasi', 'wbKarungTertinggal', 'wbKomposisiTurunan', 'wbSelisihWadah', 'wbCekHari'];
var hitungBerat = function (daftar, f) { __hitung = {}; f(); var o = {}; daftar.forEach(function (k) { o[k] = __hitung[k] || 0; }); return o; };
var jumlah = function (o) { return Object.keys(o).reduce(function (a, k) { return a + o[k]; }, 0); };
"""

SKENARIO = uji_wadah_satu_buku.BANTU + r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var nId = 9000; var W = { tanggal: '2026-09-21', jam: '10:00', kini: '2026-09-21T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
terapkanKeCache(wbSusunAktifkan('IR64 Apex', W).dokumen);
ok('kotak pasir: W1 IR64 Apex aktif (buku sendiri + karung belakang Kumala), W2–W5 belum', wbAktif('IR64 Apex') && !wbAktif('Tawon Super') && wbKarungBelakangWadah('IR64 Apex').length === 1);
var opsiJ = { akun: function () { return null; }, gantiMode: function () {}, mode: function () { return 'gelap'; }, statusTeks: function () { return ''; }, statusAwas: function () { return false; },
  statusRingkas: function () { return ''; }, versiData: function () { return __versi; }, pemegang: function () { return null; }, bukaStok: null };
var aJ = __akar(); var JL = pasangLayarJual(aJ, opsiJ);
var sJ = function () { return JL.keadaan.baca(); };
// oracle: teks komposisi & selisih tiap chip wadah, dihitung LANGSUNG dari logika atas keadaan Jual sekarang
var chipW = function () { return susunRak(sJ()).literan.filter(function (c) { return c.wadah; }); };
var harapJ = function () { return chipW().map(function (c) { var KT = wbKomposisiTurunan(c.kunci, sJ()), SL = wbSelisihWadah(c.kunci, sJ(), c.sisa); return { k: c.kunci, kt: esc(KT.nama), sl: SL.ada ? esc(SL.teks) : '' }; }); };
var cekJ = function () { var CW = wbCekHari(tanggalTutupAktif(sJ().sekarang || new Date())); return 'Cek wadah · ' + CW.daftar.filter(function (x) { return x.aktif && x.dicek; }).length + '/' + CW.nAktif + ' hari ini'; };
var cocokJ = function () { var H = harapJ(); var html = aJ.__html || ''; var kurang = H.filter(function (x) { return html.indexOf(x.kt) < 0 || (x.sl && html.indexOf(x.sl) < 0); }).map(function (x) { return x.k; });
  if (html.indexOf(cekJ()) < 0) kurang.push('cek: ' + cekJ()); return kurang; };

JL.keadaan.setel({ jalur: 'literan', sekarang: new Date(Date.now()) });   // jam dikunci (new Date() tanpa argumen di jsc = jam sungguhan)
var nChip = chipW().length;
ok('rak Literan tergambar: ' + nChip + ' chip wadah, teks komposisi/selisih/cek = hitungan logika langsung', nChip >= 3 && !cocokJ().length, J(cocokJ()));
// --- 1 · ketukan yang tidak mengubah data: TIDAK menghitung ulang
var k1 = hitungBerat(BERAT, function () { JL.keadaan.setel({ kabar: '' }); }); var n1 = __nStok;
__nStok = 0; JL.keadaan.setel({ kabar: '' }); var nStokKetuk = __nStok;
ok('Jual: ketukan di rak Literan tanpa data baru → komposisi turunan / selisih / cek wadah TIDAK dihitung ulang (dulu ' + (nChip * 2 + 1) + ' hitungan per ketukan)', jumlah(k1) === 0, J(k1));
ok('Jual: ketukan itu tidak menghitung ulang buku stok mesin sama sekali (hitungStokKarungPerMerk)', nStokKetuk === 0, nStokKetuk);
ok('Jual: sesudah ketukan teks chip tetap = hitungan logika langsung', !cocokJ().length, J(cocokJ()));
// --- 2 · data baru: cek wadah tercatat (sisa chip TIDAK berubah) → tombol Cek ikut naik
var c0 = cekJ(); terapkanKeCache(wbSusunCek('IR64 Apex', 'sesuai', W).dokumen);
ok('Jual: cek wadah baru tercatat → tombol "' + cekJ() + '" (dulu "' + c0 + '"), tidak basi', cekJ() !== c0 && (aJ.__html || '').indexOf(cekJ()) >= 0, J(cocokJ()));
// --- 3 · data baru: catatan karung belakang disamakan (sisa chip TIDAK berubah, selisih berubah) → teks selisih chip IR64 Apex ikut
var sl0 = wbSelisihWadah('IR64 Apex', sJ(), chipW().filter(function (c) { return c.kunci === 'IR64 Apex'; })[0].sisa).teks;
var sisa0 = chipW().filter(function (c) { return c.kunci === 'IR64 Apex'; })[0].sisa;
terapkanKeCache(susunSamakanKarung(wbKunciKB('IR64 Apex', 'Kumala'), '10', W, 'IR64 Apex').dokumen);
var cIA = chipW().filter(function (c) { return c.kunci === 'IR64 Apex'; })[0]; var sl1 = wbSelisihWadah('IR64 Apex', sJ(), cIA.sisa).teks;
ok('Jual: catatan karung belakang disamakan 10 kg → selisih chip IR64 Apex tergambar baru (sisa chip tetap ' + sisa0 + ' L)', sl1 && sl1 !== sl0 && cIA.sisa === sisa0 && !cocokJ().length, J([sl0, sl1, cocokJ()]));
// --- 4 · keranjang berubah: 2 L dari Tawon Super (wadah belum aktif) masuk keranjang → bebas & selisih dihitung ulang
var cTs = chipW().filter(function (c) { return c.kunci === 'Tawon Super'; })[0]; var rM = masukkan(Object.assign({}, sJ(), { pilih: cTs }), 2);
JL.keadaan.setel({ keranjang: rM.keranjang, urutBaris: rM.urutBaris });
ok('Jual: 2 L Tawon Super masuk keranjang → teks chip = hitungan logika atas keranjang baru', sJ().keranjang.length === 1 && !cocokJ().length, J(cocokJ()));
var k2 = hitungBerat(BERAT, function () { JL.keadaan.setel({ kabar: '' }); });
ok('Jual: ketukan berikutnya (keranjang sama) kembali tanpa hitung ulang', jumlah(k2) === 0, J(k2));

// --- 5 · STOK › Wadah literan: huruf yang diketik tidak menghitung ulang; data / keranjang baru → dihitung ulang
var opsiS = { akun: function () { return null; }, gantiMode: function () {}, mode: function () { return 'gelap'; }, sekarang: function () { return new Date(Date.now()); }, statusRingkas: function () { return ''; },
  versiData: function () { return __versi; }, keranjangJual: function () { return JL.keadaan.baca(); }, bukaHarga: null };
var aS = __akar(); var SL_ = pasangLayarStok(aS, opsiS); SL_.tampilkan(true);
SL_.keadaan.setel({ tab: 'wadah', wadahAktif: 'IR64 Apex', rincianLain: true });   // lipatan "Karung di belakang" dibuka (30 Sep: dilipat)
var kjS = function () { return { keranjang: sJ().keranjang, antrean: sJ().antrean }; };
var harapS = function () { var KT = wbKomposisiTurunan('IR64 Apex', kjS()), SW = wbSelisihWadah('IR64 Apex', kjS()); return [esc(KT.teks)].concat(SW.ada ? [esc(SW.teks)] : []); };
var cocokS = function () { var html = aS.__html || ''; return harapS().filter(function (x) { return html.indexOf(x) < 0; }); };
ok('Stok: tab Wadah literan, W1 & lipatan karung di belakang dibuka → komposisi turunan & selisih = hitungan logika langsung', (aS.__html || '').indexOf('data-k="belakang-IR64 Apex"') >= 0 && !cocokS().length, J(cocokS()));
var k3 = hitungBerat(BERAT_STOK, function () { SL_.keadaan.setel({ shKetik: '1' }); SL_.keadaan.setel({ shKetik: '12' }); SL_.keadaan.setel({ krKetik: '3' }); });
ok('Stok: tiga huruf diketik → buku semua wadah / aktivasi / karung tertinggal / komposisi / selisih / cek TIDAK dihitung ulang', jumlah(k3) === 0, J(k3));
var kt0 = harapS()[0]; var rM2 = masukkan(Object.assign({}, sJ(), { pilih: chipW().filter(function (c) { return c.kunci === 'IR64 Apex'; })[0] }), 2);
JL.keadaan.setel({ keranjang: rM2.keranjang, urutBaris: rM2.urutBaris }); SL_.keadaan.setel({ shKetik: '' });
ok('Stok: keranjang Jual memegang 2 L IR64 Apex → isi kotak turunan di Stok ikut turun (tidak basi)', harapS()[0] !== kt0 && !cocokS().length, J([kt0, cocokS()]));
var sw0 = harapS().join('|'); terapkanKeCache(susunSamakanKarung(wbKunciKB('IR64 Apex', 'Kumala'), '25', W, 'IR64 Apex').dokumen);
ok('Stok: catatan karung belakang disamakan lagi (data baru) → selisih tergambar baru', harapS().join('|') !== sw0 && !cocokS().length, J([sw0, cocokS()]));
var k4 = hitungBerat(BERAT_STOK, function () { SL_.keadaan.setel({ shKetik: '5' }); });
ok('Stok: huruf berikutnya kembali tanpa hitung ulang', jumlah(k4) === 0, J(k4));
print(J({ lulus: lulus, gagal: gagal }));
"""

ONGKOS = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
__dom['jualKarungBerat'] = { value: '50' };
var opsiJ = { akun: function () { return null; }, gantiMode: function () {}, mode: function () { return 'gelap'; }, statusTeks: function () { return ''; }, statusAwas: function () { return false; },
  statusRingkas: function () { return ''; }, versiData: function () { return __versi; }, pemegang: function () { return null; }, bukaStok: null };
var aJ = __akar(); var JL = pasangLayarJual(aJ, opsiJ); JL.keadaan.setel({ jalur: 'literan', sekarang: new Date(TGL + 'T18:00:00+07:00') });
var ukur = function (f, n) { var t = []; for (var i = 0; i < n; i++) { var a = Date.now(); f(); t.push(Date.now() - a); } t.sort(function (x, y) { return x - y; }); return t[Math.floor(t.length / 2)]; };
var o = { ketuk_literan_ms: ukur(function () { JL.keadaan.setel({ kabar: '' }); }, 9) };
var aS = __akar(); var SL_ = pasangLayarStok(aS, { akun: function () { return null; }, gantiMode: function () {}, mode: function () { return 'gelap'; }, sekarang: function () { return null; }, statusRingkas: function () { return ''; },
  versiData: function () { return __versi; }, keranjangJual: function () { return JL.keadaan.baca(); }, bukaHarga: null }); SL_.tampilkan(true);
SL_.keadaan.setel({ tab: 'wadah', wadahAktif: aturWadah().daftar[0], rincianLain: true }); var i = 0;
o.huruf_stok_wadah_ms = ukur(function () { i++; SL_.keadaan.setel({ shKetik: String(i % 10) }); }, 9);
print(JSON.stringify(o));
"""


def jalan(ganti=None, cadangan=None):
    js, lay, app = bundel(ganti)
    statis = re.search(r'pasangLayarStok\([^;]*versiData: \(\) => versi', app) is not None
    # tinjauan 1 Okt: kartu Cek tutup toko di Stok & kunci ingatannya memakai TANGGAL TUTUP (lewat tengah malam = hari dagang kemarin), sama dengan Jual & Uang
    if cadangan:
        cad, tgl = uji_wadah_bernama.cad_js(cadangan)
        h, e = uji_wadah_bernama.jalan(js + PROKSI + lay + '\nvar CAD = ' + cad + ';\nvar TGL = ' + json.dumps(tgl) + ';\n' + ONGKOS)
        return h, e
    h, e = uji_wadah_bernama.jalan(uji_wadah_satu_buku.JAM_TETAP + js + PROKSI + lay + '\nvar KOTAK = ' + json.dumps(uji_wadah_satu_buku.KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    g = list(h['gagal']); l = h['lulus']
    if statis: l += 1
    else: g.append('app.js: layar Stok diberi versiData: () => versi (tanpa itu tab Wadah literan kembali menghitung ulang tiap huruf)')
    tutup = 'CK: WB.wbCekHari(tanggalTutupAktif(kini()))' in lay and "const k = opsi.versiData() + '|' + tanggalTutupAktif(kini())" in lay
    if tutup: l += 1
    else: g.append('stok.js: Cek tutup toko & kunci ingatan Wadah literan memakai tanggalTutupAktif (bukan tanggal kalender) — lewat tengah malam sama dengan Jual')
    return l, g


RUSAK = [
    ('Jual: ingatan tidak dikosongkan saat rak disusun ulang (data baru → teks basi)', [("_rakUntuk = tanda; _rakDasar = dasar; _ingatRak = {}; _rakBasi = false; }", "_rakUntuk = tanda; _rakDasar = dasar; _rakBasi = false; }")]),
    ('Jual: chip wadah kembali menghitung tiap ketukan', [("const { KT, SL } = ingatRak('w|' + c.kunci + '|' + c.sisa, () => ({ KT: WB.wbKomposisiTurunan(c.kunci, s), SL: WB.wbSelisihWadah(c.kunci, s, c.sisa) }));",
                                                          "const KT = WB.wbKomposisiTurunan(c.kunci, s); const SL = WB.wbSelisihWadah(c.kunci, s, c.sisa);")]),
    ('Jual: tombol Cek wadah kembali menghitung tiap ketukan', [("const CW = cekWadahRak(s); const nA = CW.daftar.filter((x) => x.aktif && x.dicek).length;\n      return h`<div class=\"baris-cek-wadah\"",
                                                                 "const CW = WB.wbCekHari(tanggalTutupAktif(s.sekarang || new Date())); const nA = CW.daftar.filter((x) => x.aktif && x.dicek).length;\n      return h`<div class=\"baris-cek-wadah\"")]),
    ('Stok: kunci ingatan tanpa versi data (data baru → basi)', [("const k = opsi.versiData() + '|' + tanggalTutupAktif(kini())", "const k = '|' + tanggalTutupAktif(kini())")]),
    ('Stok: kunci ingatan tanpa isi keranjang Jual (keranjang berubah → basi)', [("'|' + JSON.stringify(keranjangJual()); if (_ingatW.k !== k)", "''; if (_ingatW.k !== k)")]),
    ('Stok: buku semua wadah kembali dihitung tiap huruf', [("const w = M('susun', () => S.susunWadah(keranjangJual()));", "const w = S.susunWadah(keranjangJual());")]),
    ('Stok: wadah yang dibuka kembali dihitung tiap huruf', [("const { KB, KT, SW, CK } = M('aktif|' + aktif.nama, () => ({ KB:", "const { KB, KT, SW, CK } = ((f) => f())(() => ({ KB:")]),
    ('Stok: Cek tutup toko kembali memakai tanggal kalender', [("CK: WB.wbCekHari(tanggalTutupAktif(kini()))", "CK: WB.wbCekHari(L.waktuSekarang(kini()).tanggal)")]),
    ('app.js: Stok tidak diberi versiData', [("statusRingkas, versiData: () => versi, keranjangJual: () => layar.keadaan.baca(),", "statusRingkas, keranjangJual: () => layar.keadaan.baca(),")]),
]


def main():
    if '--kontrol' in sys.argv:
        diam = 0
        for nama, g in RUSAK:
            try: l, gg = jalan(g)
            except AssertionError as e: print('KONTROL BASI ' + nama + ' — ' + str(e)); diam += 1; continue
            print(('BERBUNYI ' if gg else 'DIAM!!   ') + nama + (' → ' + gg[0][:150] if gg else ''))
            if not gg: diam += 1
        print('kontrol: %d/%d berbunyi' % (len(RUSAK) - diam, len(RUSAK))); return 3 if diam else 0
    l, g = jalan()
    print('CACHE CHIP LITERAN (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    p = uji_wadah_bernama.cadangan_toko()
    if p:
        h, e = jalan(cadangan=p)
        print('ONGKOS DATA TOKO (%s): %s' % (os.path.basename(p), json.dumps(h) if h else 'JATUH ' + e[-300:]))
    else: print('ONGKOS DATA TOKO: dilewati — tidak ada _privat/backup-batch-*.json (worktree / CI)')
    return 1 if g else 0


if __name__ == '__main__':
    sys.exit(main())
