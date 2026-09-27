#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_arsip_produk.py — putaran 27 Bagian 3: ARSIP PRODUK (owner 27 Sep; penanda = satu dokumen aturanToko/produkArsip).
  · Hanya barang bersisa nol yang bisa diarsipkan; stok bukan nol → sisanya disebut, arahnya cocokkan.
  · Arsip menyembunyikan dari rak Jual (juga Sering & saring jenis), katalog harga (juga hitungan "belum ada harga"), label, dan katalog HP kasir
    — buku stok, penjualan, laba, neraca TIDAK berubah; tidak ada catatan bertanggal yang ditulis.
  · Katalog HP kasir dari /baru/ = penyusun index.html (dibaca dari teks index.html) dikurangi baris nama arsip; tanpa arsip = byte-sama.
  · Karung utuh & kemasan senama berbagi dokumen katalog kemasan → baris K<ukuran> tetap tampil selama salah satu pemakainya masih aktif.
  · Hapus hanya untuk nama yang tidak pernah bertransaksi (dua ketukan); pernah bertransaksi → ditolak.
  · Barang masuk atas nama arsip → wajib dijawab pulihkan / varian; adukan dengan hasil kemasan arsip memulihkannya.
KOTAK PASIR (ANGKA CONTOH), jam dikunci 19 Sep 2026 10:00 WIB. Cadangan toko di _privat/: semua barang bersisa nol diarsipkan → katalog kasir =
index.html minus barisnya, laba tiap bulan & neraca byte-sama, hapus ditolak untuk semuanya.

    python3 alat-uji/uji_arsip_produk.py            → N lulus · 0 gagal
    python3 alat-uji/uji_arsip_produk.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, beku2  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/arsip-logika.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/struk-logika.js',
                                  'baru/js/layar/jual-logika.js', 'baru/js/layar/wadah-bernama-logika.js', 'baru/js/layar/setengah-logika.js', 'baru/js/data/katalog-kasir.js', 'baru/js/layar/harga-logika.js', 'baru/js/layar/stok-logika.js',
                                  'baru/js/layar/varian-logika.js', 'baru/js/layar/stok-catat-logika.js', 'baru/js/layar/stok-adukan-logika.js', 'baru/js/layar/jenis-beras-logika.js']
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def baris(merk, n, harga, berat=50):
    return {'id': str(n) + merk, 'merk': merk, 'satuan': 'karung', 'beratKarung': berat, 'jumlahKarung': n, 'totalKg': n * berat, 'hargaPerKg': harga, 'subtotalHarga': n * berat * harga}


def jual(i, merk, kg, jenis='karung', **k):
    d = {'id': i, 'tanggal': '2026-09-15', 'jam': '09:00', 'caraBayar': 'Tunai', 'jenis': jenis, 'merkSumber': merk, 'totalKg': kg, 'hargaTotal': int(kg * 15000), 'hppTotalSaatJual': int(kg * 14000)}
    if jenis == 'karung': d.update({'jumlahKarung': kg / 50, 'beratKarungAcuan': 50})
    d.update(k); return d


KOTAK = {
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-09-10', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
                  'merkList': [baris('Angsa', 10, 13000), baris('Lama', 2, 14000), baris('Perahu', 1, 14500)]}],
  'produksiKemasan': [{'id': 'p1', 'tanggal': '2026-09-11', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 10, 'hppPerUnit': 66000, 'merkSumber': 'Angsa', 'kgDipakai': 50, 'sumberList': [{'merk': 'Angsa', 'kg': 50}]},
                      {'id': 'p2', 'tanggal': '2026-09-11', 'namaProduk': 'Kembang', 'ukuranKemasan': 10, 'jumlahUnit': 5, 'hppPerUnit': 132000, 'merkSumber': 'Angsa', 'kgDipakai': 50, 'sumberList': [{'merk': 'Angsa', 'kg': 50}]},
                      {'id': 'p3', 'tanggal': '2026-09-11', 'namaProduk': 'Perahu', 'ukuranKemasan': 25, 'jumlahUnit': 4, 'hppPerUnit': 330000, 'merkSumber': 'Angsa', 'kgDipakai': 100, 'sumberList': [{'merk': 'Angsa', 'kg': 100}]}],
  'penjualan': [jual('j1', 'Lama', 100), jual('j2', 'Angsa', 50), jual('j3', 'Perahu', 50),
                jual('j4', None, 50, jenis='kemasan', namaProduk='Kembang', ukuranKemasan=5, jumlahUnit=10), jual('j5', None, 25, jenis='kemasan', namaProduk='Perahu', ukuranKemasan=25, jumlahUnit=1)],
  'katalogHargaKarung': [{'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 14000}, {'id': 'Lama', 'merk': 'Lama', 'hargaPerKg': 15000}, {'id': 'Perahu', 'merk': 'Perahu', 'hargaPerKg': 15500},
                         {'id': 'Coba · Super', 'merk': 'Coba · Super', 'hargaPerKg': 16000}],
  'katalogHargaKemasan': [{'id': 'kembang_5kg', 'merk': 'Kembang', 'ukuran': 5, 'hargaPerUnit': 75000}, {'id': 'kembang_10kg', 'merk': 'Kembang', 'ukuran': 10, 'hargaPerUnit': 146000},
                          {'id': 'lama_50kg', 'merk': 'Lama', 'ukuran': 50, 'hargaPerUnit': 750000}, {'id': 'perahu_25kg', 'merk': 'Perahu', 'ukuran': 25, 'hargaPerUnit': 380000}],
  'katalogHargaLiteran': [{'id': 'Angsa', 'merk': 'Angsa', 'hargaPerLiter': 12000}, {'id': 'Lama', 'merk': 'Lama', 'hargaPerLiter': 12500}],
  'aturanToko': [{'id': 'hargaLabel', 'daftar': [{'k': 'Lama|S', 'lama': 14800, 'tanggal': '2026-09-12'}, {'k': 'Angsa|S', 'lama': 13800, 'tanggal': '2026-09-12'}]}, {'id': 'hargaDraf', 'draf': {'Lama|L': 13000, 'Coba · Super|S': 16500}}],
  'pengaturan': [{'id': 'jenisBeras', 'peta': {'Lama': 'IR64', 'Coba · Super': 'IR64'}}],
  # putaran 27 (Bagian 5): Lama dijual literan LANGSUNG dari karungnya (ditandai owner di aturan wadah) — harga liternya dipakai rak
  'wadahLiteran': [{'id': 1, 'tanggal': '2026-09-01', 'jam': '08:00', 'tipe': 'atur', 'literanLangsung': ['Lama']}],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var nId = 9000; var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var s = keadaanAwal(); sinkronKeranjang(s);
var rakNama = function () { var r = susunRak(s); return [].concat(r.karung, r.literan, r.repack, r.kemasan).map(function (c) { return c.jalur + ':' + c.kunci; }); };
var barisHarga = function () { return hgSemua(new Date(Date.now())).baris.map(function (b) { return b.k; }); };
var terapkan = function (r) { terapkanKeCache((r && r.dokumen) || []); if (r && r.hapus) terapkanKeCache(r.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); return r; };
var laporan = function () { return J({ sep: hitungLabaBersihRentang('2026-09-01', '2026-09-30'), stok: hitungStokKarungPerMerk(), kem: hitungStokKemasan(), neraca: hitungNeraca() }); };
var kkSama = function (buangK, buangM) { var baru = kkIsi(); var lama = susunIsiKatalogKasirLama(); lama.merkKarung = lama.merkKarung.filter(function (m) { return (buangK || []).indexOf(m.merk) < 0; }); lama.kemasan = lama.kemasan.filter(function (k) { return (buangM || []).indexOf(k.kunci) < 0; }); return J(baru) === J(lama); };

// ---- 1 · keadaan & penjaga
var KL = arKeadaan('K:Lama'), KA = arKeadaan('K:Angsa'), KC = arKeadaan('K:Coba · Super');
ok('keadaan: Lama habis (2 karung masuk, 2 terjual) & PERNAH bertransaksi → bisa diarsipkan, TIDAK bisa dihapus; Angsa bersisa 250 kg (500 − 50 terjual − 200 diaduk); Coba · Super cuma di katalog → bisa dihapus',
  KL.nol && KL.pernah && KL.bisaArsip && !KL.bisaHapus && !KA.nol && KA.sisa === 250 && KC.nol && !KC.pernah && KC.bisaHapus, J([KL, KA, KC]));
var TA = arSusunArsip('K:Angsa', W);
ok('arsip barang bersisa DITOLAK: sisanya disebut + arah cocokkan tumpukan', !!TA.tolak && /masih bersisa 250 kg/.test(TA.tolak) && /cocokkan/.test(TA.tolak) && TA.cocok === 'tumpukan|Angsa', J(TA));
// ---- 2 · arsipkan Lama
var lap0 = laporan(); var nJual0 = cacheMentah('penjualan').length; var lubang0 = hgSemua(new Date(Date.now())).ringkas[0].a;
var R2 = arSusunArsip('K:Lama', W);
ok('arsipkan Lama: SATU dokumen aturanToko/produkArsip {daftar [kunci K:Lama, jenis beras, nama, tanggal, jam]} — tidak ada catatan bertanggal', !R2.tolak && R2.dokumen.length === 1 && R2.dokumen[0].koleksi === 'aturanToko' && R2.dokumen[0].data.id === 'produkArsip' && J(R2.dokumen[0].data.daftar) === J([{ kunci: 'K:Lama', jenis: 'beras', nama: 'Lama', tanggal: '2026-09-19', jam: '10:00' }]), J(R2));
ok('sebelum diarsipkan: Lama ada di rak (karung habis, literan, repack), katalog (per kg, per liter, karung 50 kg), dan katalog kasir', rakNama().indexOf('karung:Lama') >= 0 && rakNama().indexOf('literan:Lama') >= 0 && barisHarga().indexOf('Lama|S') >= 0 && barisHarga().indexOf('Lama|K50') >= 0 && kkIsi().merkKarung.some(function (m) { return m.merk === 'Lama'; }));
terapkan(R2);
ok('sesudah: Lama HILANG dari rak Jual (karung, literan, repack) & dari Sering', !rakNama().some(function (x) { return /:Lama$/.test(x); }) && !susunRak(s).sering.some(function (c) { return c.kunci === 'Lama'; }), J(rakNama()));
ok('sesudah: Lama hilang dari katalog harga (per kg, per liter, karung 50 kg), draf-nya tidak ditagih, label "Lama|S" tidak ditagih; label nama lain tetap', !barisHarga().some(function (k) { return /^Lama\|/.test(k); }) && susunLabelTugas(hgSemua(new Date(Date.now()))).tugas.map(function (x) { return x.k; }).join() === 'Angsa|S', J(barisHarga()));
ok('sesudah: katalog HP kasir dari /baru/ = penyusun index.html DIKURANGI baris Lama saja (fungsi salinan tidak diubah)', !kkIsi().merkKarung.some(function (m) { return m.merk === 'Lama'; }) && kkSama(['Lama'], []));
ok('sesudah: buku stok, penjualan, laba September, dan neraca BYTE-SAMA; tidak ada baris nota yang berubah', laporan() === lap0 && cacheMentah('penjualan').length === nJual0);
ok('barang masuk: nama arsip tidak ditawarkan di pilihan cepat', calonMerkMasuk().indexOf('Lama') < 0 && calonMerkMasuk().indexOf('Angsa') >= 0);
// ---- 3 · kemasan & karung utuh senama
var R3 = arSusunArsip('M:Kembang|5', W); terapkan(R3);
ok('arsipkan kemasan Kembang 5 kg (habis): hilang dari rak kemasan, katalog K5, dan katalog kasir; Kembang 10 kg (bersisa) tetap', !R3.tolak && rakNama().indexOf('kemasan:Kembang|5') < 0 && rakNama().indexOf('kemasan:Kembang|10') >= 0 && barisHarga().indexOf('Kembang|K5') < 0 && barisHarga().indexOf('Kembang|K10') >= 0 && !kkIsi().kemasan.some(function (k) { return k.kunci === 'Kembang|5'; }) && kkSama(['Lama'], ['Kembang|5']), J(barisHarga()));
terapkan(arSusunArsip('K:Perahu', W));
ok('karung Perahu (habis) diarsipkan TAPI kemasan Perahu 25 kg masih bersisa 3 → baris per kg hilang, baris "Perahu · 25 kg" (dokumen katalog kemasan yang sama) TETAP; kemasannya tetap di rak & katalog kasir',
  barisHarga().indexOf('Perahu|S') < 0 && barisHarga().indexOf('Perahu|K25') >= 0 && rakNama().indexOf('kemasan:Perahu|25') >= 0 && kkIsi().kemasan.some(function (k) { return k.kunci === 'Perahu|25'; }) && !kkIsi().merkKarung.some(function (m) { return m.merk === 'Perahu'; }), J(barisHarga()));
// ---- 4 · pulihkan
var P4 = arSusunPulih('K:Lama', W); terapkan(P4);
ok('pulihkan Lama dari Produk arsip: daftar tanpa Lama; Lama kembali di rak & katalog; katalog kasir = index.html minus yang masih diarsipkan', !P4.tolak && !arPeta()['K:Lama'] && rakNama().indexOf('karung:Lama') >= 0 && barisHarga().indexOf('Lama|S') >= 0 && kkSama(['Perahu'], ['Kembang|5']) && arRingkas().length === 2);
// ---- 5 · hapus
var H5 = arSusunHapus('K:Lama', W, true);
ok('hapus Lama (pernah bertransaksi) DITOLAK walau yakin — arahnya arsipkan', !!H5.tolak && /pernah punya transaksi/.test(H5.tolak));
var H5a = arSusunHapus('K:Coba · Super', W, false); var H5b = arSusunHapus('K:Coba · Super', W, true);
ok('hapus "Coba · Super" (cuma katalog): ketukan pertama ditanya; kedua → hapus dokumen katalog per kg + draf & jenis nama itu dibuang; nama lain utuh',
  H5a.perluYakin === true && !H5b.tolak && J(H5b.hapus) === J([{ koleksi: 'katalogHargaKarung', id: 'Coba · Super' }]) && H5b.dokumen.some(function (d) { return d.data.id === 'hargaDraf' && d.data.draf['Lama|L'] === 13000 && d.data.draf['Coba · Super|S'] === undefined; })
  && H5b.dokumen.some(function (d) { return d.data.id === 'jenisBeras' && d.data.peta.Lama === 'IR64' && d.data.peta['Coba · Super'] === undefined; }), J(H5b));
terapkan(H5b); ok('sesudah hapus: "Coba · Super" tidak ada di katalog harga', !barisHarga().some(function (k) { return /^Coba/.test(k); }));
// ---- 6 · barang masuk atas nama arsip → pulihkan atau varian
terapkan(arSusunArsip('K:Lama', W));
var brs = function (ubah) { return { id: null, tanggal: '2026-09-19', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', bongkar: '', alasan: '', baris: [Object.assign({ merk: 'Lama', jumlahKarung: '2', beratKarung: 50, hargaPerKg: '14000' }, ubah || {})] }; };
var M0 = susunSimpanMasuk(brs(), W, true);
ok('barang masuk "Lama" (diarsipkan) walau harganya sama → DITANYA pulihkan / varian', !!M0.tolak && /sudah DIARSIPKAN/.test(M0.tolak) && M0.perluVarian === 1, J(M0.tolak));
var M1 = susunSimpanMasuk(brs({ varian: 'sama' }), W, true); var ar1 = (M1.dokumen || []).find(function (d) { return d.data.id === 'produkArsip'; });
ok('"Pulihkan — sama barangnya" → kedatangan atas nama Lama + arsip TANPA Lama di kiriman yang sama; kabar menyebutnya', !M1.tolak && M1.dokumen[0].data.merkList[0].merk === 'Lama' && ar1 && !ar1.data.daftar.some(function (x) { return x.kunci === 'K:Lama'; }) && ar1.data.daftar.length === 2 && /Dipulihkan dari arsip: Lama/.test(M1.patch.kabar), J(M1));
var M2 = susunSimpanMasuk(brs({ varian: 'beda', namaMutu: 'Baru' }), W, true);
ok('"Beda mutu" → varian "Lama · Baru"; Lama TETAP diarsipkan', !M2.tolak && M2.dokumen[0].data.merkList[0].merk === 'Lama · Baru' && !M2.dokumen.some(function (d) { return d.data.id === 'produkArsip'; }));
// ---- 7 · adukan dengan hasil kemasan arsip
var A7 = susunSimpanAdukan({ tanggal: '2026-09-19', bahan: [{ merk: 'Angsa', kg: '50' }], bahanKemasan: [], hasil: [{ nama: 'Kembang', ukuran: '5', unit: '10', kantongJenis: '', kantongJumlah: '' }], upah: '' }, W, { susut: true });
var ar7 = (A7.dokumen || []).find(function (d) { return d.data.id === 'produkArsip'; });
ok('adukan menghasilkan Kembang 5 kg (diarsipkan) → dipulihkan di kiriman yang sama, kabar menyebutnya', !A7.tolak && ar7 && !ar7.data.daftar.some(function (x) { return x.kunci === 'M:Kembang|5'; }) && /Dipulihkan dari arsip: Kembang 5 kg/.test(A7.patch.kabar), J(A7.tolak || A7.patch));

// ---- ASAP DATA TOKO
var asap = null;
if (CADANGAN) {
  Object.keys(KOTAK).forEach(function (n) { pasok(n, []); }); Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
  var WC = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
  var bulan = ['2026-08', '2026-09']; var lap = function () { return J({ laba: bulan.map(function (b) { return hitungLabaBersihRentang(b + '-01', b + '-31'); }), neraca: hitungNeraca(), stok: hitungStokKarungPerMerk(), kem: hitungStokKemasan() }); };
  var sama0 = kkSama([], []); var l0 = lap();
  var nolK = Object.keys(hitungStokKarungPerMerk()).filter(function (m) { return arKeadaan('K:' + m).bisaArsip; }); var nolM = Object.keys(hitungStokKemasan()).filter(function (k) { return arKeadaan('M:' + k).bisaArsip; });
  var tolakHapus = nolK.map(function (m) { return 'K:' + m; }).concat(nolM.map(function (k) { return 'M:' + k; })).filter(function (k) { return !!arSusunHapus(k, WC, true).tolak; }).length;
  nolK.forEach(function (m) { terapkan(arSusunArsip('K:' + m, WC)); }); nolM.forEach(function (k) { terapkan(arSusunArsip('M:' + k, WC)); });
  var sisaDiRak = rakNama().filter(function (x) { var k = x.split(':').slice(1).join(':'); return nolK.indexOf(k) >= 0 || nolM.indexOf(k) >= 0; });
  asap = { nolK: nolK, nolM: nolM, kkAwal: sama0, kkSesudah: kkSama(nolK, nolM), laporanSama: lap() === l0, sisaDiRak: sisaDiRak, tolakHapus: tolakHapus, katalogBersih: !barisHarga().some(function (k) { return nolK.indexOf(k.slice(0, k.lastIndexOf('|'))) >= 0 && /\|(S|L)$/.test(k); }) };
}
print(J({ lulus: lulus, gagal: gagal, asap: asap }));
"""


def cadangan_toko():
    c = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')), key=os.path.basename)
    return c[-1] if c else None


def lama_index():
    s = open(os.path.join(AKAR, 'index.html'), encoding='utf-8').read(); mi = s[s.index('<script type="module">'):s.rindex('</script>')]
    f = beku2.potong(mi, 'susunIsiKatalogKasir'); assert f, 'susunIsiKatalogKasir() tidak ditemukan di index.html'
    return f.replace('function susunIsiKatalogKasir(', 'function susunIsiKatalogKasirLama(', 1)


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def utama(js, pakai_cadangan):
    cad = 'null'; tgl = ''
    p = cadangan_toko() if pakai_cadangan else None
    if p:
        d = json.load(open(p, encoding='utf-8')); kol = re.findall(r"\{ nama: '(\w+)'", open(os.path.join(AKAR, 'baru/js/data/koleksi.js'), encoding='utf-8').read())
        cad = json.dumps(dict((n, d[n]) for n in kol if isinstance(d.get(n), list))); tgl = os.path.basename(p).split('miqbal-')[-1][:10]
    h, e = jalan(JAM_TETAP + js + '\n' + lama_index() + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    return h['lulus'], h['gagal'], h.get('asap')


RUSAK = {
    'arsip boleh walau stok bukan nol': ("  if (!K.nol) return { tolak: K.judul + ' masih bersisa '", "  if (false) return { tolak: K.judul + ' masih bersisa '"),
    'rak Jual tidak menyaring nama arsip': ("    if (arBeras(merk, arsip)) return;\n", "\n"),
    'kemasan arsip tetap di rak Jual': ("const st = stokKemasan[kunci]; if (arKemasan(st.namaProduk, st.ukuranKemasan, arsip)) return;", "const st = stokKemasan[kunci];"),
    'katalog harga tidak menyaring arsip': ("  const arsip = arPeta(); if (Object.keys(arsip).length) Object.keys(daftar).forEach((m) => { daftar[m] = daftar[m].filter((sid) => !arSembunyiHarga(m, sid, arsip)); if (!daftar[m].length) delete daftar[m]; });", ""),
    'katalog HP kasir tidak menyaring arsip': ("function kkIsi() { return arSaringKatalogKasir(susunIsiKatalogKasir()); }", "function kkIsi() { return susunIsiKatalogKasir(); }"),
    'hapus boleh walau pernah bertransaksi': ("  if (K.pernah) return { tolak: K.judul + ' pernah punya transaksi", "  if (false) return { tolak: K.judul + ' pernah punya transaksi"),
    'hapus tanpa ketukan kedua': ("  if (!yakin) return { tolak: 'Ketuk sekali lagi untuk MENGHAPUS '", "  if (false) return { tolak: 'Ketuk sekali lagi untuk MENGHAPUS '"),
    'barang masuk nama arsip tidak bertanya': ("const diArsip = !draf.id && terisi && !masalah && arBeras(merk);", "const diArsip = false;"),
    'pulihkan tidak ditulis saat barang masuk sama barangnya': ("const dp = arDokPulihBanyak(pulih, w); if (dp) dokumen.push(dp);", "const dp = null;"),
    'label nama arsip tetap ditagih': ("const tugas = daftarLabel().filter((t) => tampil(t.k)).map((t) => {", "const tugas = daftarLabel().map((t) => {"),
    'karung utuh & kemasan senama: baris kemasan ikut hilang': ("return !kemAktif && !karungAktif && (berasArsip || !!p[arKunciKemasan(merk, u)]);", "return berasArsip || !!p[arKunciKemasan(merk, u)];"),
    'adukan tidak memulihkan hasil arsip': ("const dpAd = arDokPulihBanyak(pulihAd, w); if (dpAd) dokumen.push(dpAd);", "const dpAd = null;"),
    'arsip menulis catatan bertanggal (buku berubah)': ("return { dokumen: [arTulisDaftar(daftar, w)], patch: { kabar: K.judul + ' diarsipkan", "return { dokumen: [arTulisDaftar(daftar, w), { koleksi: 'penyesuaianStok', data: { id: w.idUnik(), tanggal: w.tanggal, merk: K.nama, selisihKg: -1 } }], patch: { kabar: K.judul + ' diarsipkan"),
}

if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, (a, b) in RUSAK.items():
            if js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g, _ = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    print('ARSIP PRODUK (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    if asap:
        print('ASAP DATA TOKO (%s): %d nama karung & %d kemasan bersisa nol diarsipkan · katalog kasir sebelum = index.html: %s · sesudah = index.html minus arsip: %s · laba Agu & Sep, neraca, buku stok byte-sama: %s · tidak ada di rak: %s · hapus ditolak (pernah bertransaksi): %d'
              % (os.path.basename(cadangan_toko()), len(asap['nolK']), len(asap['nolM']), asap['kkAwal'], asap['kkSesudah'], asap['laporanSama'], not asap['sisaDiRak'], asap['tolakHapus']))
        if not (asap['kkAwal'] and asap['kkSesudah'] and asap['laporanSama'] and not asap['sisaDiRak'] and asap['katalogBersih'] and asap['tolakHapus'] == len(asap['nolK']) + len(asap['nolM'])): g.append('asap data toko: ' + json.dumps(asap, ensure_ascii=False)[:300])
    sys.exit(2 if g else 0)
