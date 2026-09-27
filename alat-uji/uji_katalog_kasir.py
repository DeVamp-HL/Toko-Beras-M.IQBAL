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
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/data/katalog-kasir.js', 'baru/js/layar/harga-logika.js']
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
ok('isi katalog /baru/ = isi susunIsiKatalogKasir() index.html untuk data yang sama (JSON persis, urutan ikut)', !!I && J(I) === J(LAMA), J(I).slice(0, 300) + ' ≠ ' + J(LAMA).slice(0, 300));
ok('isi memuat keempat bagian index.html: kemasan, merkKarung (+ modal & harga), bahanLiteran, piutang (yang masih bersisa)', !!I && I.kemasan.length === 1 && I.kemasan[0].namaProduk === 'Kembang' && I.kemasan[0].hargaPerUnit === 75000
  && I.merkKarung.some(function (m) { return m.merk === 'Angsa' && m.hargaPerKg === 13800 && m.hargaPerLiter === 12500 && m.hargaKarung50 === 700000 && m.hppPerKg > 0; })
  && I.bahanLiteran.paperbag5l.sisaPcs === 100 && I.bahanLiteran.paperbag5l.hargaPerPcs === 305 && I.piutang.length === 1 && I.piutang[0].nama === 'Pelanggan Contoh' && I.piutang[0].sisa === 150000, J(I));
if (CADANGAN) {
  Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
  var IC = kkIsi(); var LC = susunIsiKatalogKasirLama();
  ok('DATA TOKO (cadangan ' + NAMA_CADANGAN + '): isi /baru/ = isi index.html', !!IC && J(IC) === J(LC) && IC.merkKarung.length > 0, IC ? IC.merkKarung.length + ' merek' : 'null');
  Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); }); Object.keys(CADANGAN).forEach(function (n) { if (!(n in KOTAK)) pasok(n, []); });
}
// ---- 2 · bentuk dokumen & pembanding
var D = kkDokumen(I, '2026-09-19T03:00:00.000Z');
ok('dokumen: kunci & urutannya = setDoc terbitkanRingkasanKasir() index.html (' + KUNCI_LAMA.join(', ') + '), id "aktif"', J(Object.keys(D)) === J(KUNCI_LAMA) && D.id === 'aktif' && D.diperbaruiPada === '2026-09-19T03:00:00.000Z', J(Object.keys(D)));
ok('dokumen katalog = dokumen turunan, ditulis APA ADANYA oleh penulis pusat (kkMentah): hanya ringkasanKasir', kkMentah('ringkasanKasir') && !kkMentah('penjualan') && !kkMentah('pengaturan'));
var acak = function (x) { if (Array.isArray(x)) return x.map(acak); if (x && typeof x === 'object') { var o = {}; Object.keys(x).reverse().forEach(function (k) { o[k] = acak(x[k]); }); return o; } return x; };
kkLupakanServer(); ok('server belum terbaca → tertinggal = null (belum bisa tahu; tidak terbit, Beranda tidak menebak)', kkTertinggal(I) === null);
kkSetelServer(null, true); ok('server terbaca & dokumen belum pernah ada → tertinggal = true', kkTertinggal(I) === true);
kkSetelServer(acak(D), true); ok('server = isi yang sama dengan URUTAN KUNCI LAIN (seperti peta Firestore) → tidak tertinggal (tidak terbit ulang tanpa henti)', kkTertinggal(I) === false, kkKanon(acak(D)).slice(0, 200));
var D2 = JSON.parse(J(D)); D2.merkKarung[0].hargaPerKg += 100; kkSetelServer(D2, true);
ok('satu harga beda → tertinggal = true', kkTertinggal(I) === true);
// ---- 3 · terbit harga: katalog SESUDAH terbit ikut di kiriman yang sama
kkSetelServer(D, true);
terapkanKeCache(susunUbah('Angsa|S', '14.000', 'jual', W).dokumen);
var T = susunTerbit(W, true); var sebelum = J(kkIsi()); var DK = kkSertakan(T.dokumen, W.kini); var kk = DK.filter(function (d) { return d.koleksi === 'ringkasanKasir'; });
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
pasok('perangkatStatus', [hp('d-v26', 'darurat', 'kasir-v26', '2026-09-19T02:50:00.000Z', undefined), hp('d-segar', 'darurat', 'kasir-v27', '2026-09-19T02:50:00.000Z', T0),
  hp('d-basi', 'darurat', 'kasir-v27', '2026-09-19T02:50:00.000Z', '2026-09-18T01:00:00.000Z'), hp('d-baru-saja', 'darurat', 'kasir-v27', '2026-09-19T02:03:00.000Z', '2026-09-18T01:00:00.000Z'),
  hp('k-kalk', 'kasir', 'kasir-v27', '2026-09-19T02:50:00.000Z', undefined), hp('d-v24', 'darurat', 'kasir-v24', '2026-09-19T02:50:00.000Z', undefined), hp('d-jauh', 'darurat', 'kasir-v26', '2026-09-01T02:50:00.000Z', undefined)]);
var B = kkBeranda(new Date(__KINI)); var tk = B.perhatian.map(function (x) { return x.teks; }).join(' | ');
ok('Beranda: "Katalog kasir: diperbarui <tanggal jam WIB> · sama dengan data sekarang"', /^Katalog kasir: diperbarui .*09\.00 · sama dengan data sekarang$/.test(B.status) || /^Katalog kasir: diperbarui .* · sama dengan data sekarang$/.test(B.status), B.status);
ok('Beranda: HP kasir versi 26 disebut (harga baru baru sampai saat dibuka ulang); HP v24 & yang tidak berdenyut 7 hari TIDAK disebut di sini', /HP d-v26 · kasir darurat: masih kasir-v26 — harga baru baru sampai saat aplikasinya dibuka ulang/.test(tk) && !/d-v24|d-jauh/.test(tk), tk);
ok('Beranda: HP penjaga yang berdenyut > 6 menit sesudah katalog terbit tapi memegang katalog lama → disebut, awas', B.perhatian.some(function (x) { return /HP d-basi · kasir darurat: masih memegang katalog/.test(x.teks) && x.awas; }), tk);
ok('Beranda: HP yang memegang katalog terbaru, yang baru saja berdenyut, dan kasir kalkulator (tanpa cap katalog) TIDAK disebut', !/d-segar|d-baru-saja|k-kalk/.test(tk), tk);
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
       'const g = kkBolehTerbit(' in pn and 'if (!g.boleh) return;' in pn and "kkTertinggal(isi) !== true) return;" in pn and 'setDoc(doc(db, KK_KOLEKSI, KK_ID), kkDokumen(isi, kini))' in pn and 'KOLEKSI_LOG' not in pn, pn[:200])
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
    ok('versi: kedua berkas kasir = VERSI sw-kasir.js = KK_VERSI_KASIR_TERBARU (/baru/) = kasir-v27', vs and kk and all(v and v.group(1) == vs.group(1) for v in va) and kk.group(1) == vs.group(1) == 'kasir-v27', [x.group(1) if x else None for x in [vs, kk] + va])
    ok('versi: lantai kunci bulan (KP_VERSI_KASIR_25B) tidak di atas versi yang disajikan sw-kasir.js', kp and vs and 0 < nomor(kp) <= nomor(vs), kp.group(1) if kp else None)
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
    ok('bilah atas: "versi 25c"', N.get('label') == 'versi 25c', N.get('label'))
    if not B or B.get('galat'): return out + [('peramban · skenario berkala jalan', False, (B or {}).get('galat', 'tidak ada hasil'))]
    ok('tanpa ketukan apa pun: katalog baru (74.000) diambil sendiri di jadwal berkala', B['awal'] == [73000] and B['sesudahJadwal'] == [74000], B)
    return out


def semua(ganti=None, bagian=('statis', 'jsc', 'peramban')):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        l, g = jalan_jsc(t); out += [('jsc · ' + x, False, '') for x in g] + [('jsc · %d skenario' % l, l > 0 and not g, '')]
        out.append(('__jsc_lulus', True, l))
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
    ('sw-kasir.js naik tanpa /baru/ ikut', {'sw-kasir.js': [("const VERSI = 'kasir-v27';", "const VERSI = 'kasir-v28';")]}, ('statis',)),
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
