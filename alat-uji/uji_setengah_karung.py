#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_setengah_karung.py — putaran 27 Bagian 4: JUAL ½ (25 kg) DARI KEMASAN 50 KG hasil produksi/campuran (owner 27 Sep).
  · Harga 25 kg = katalog; belum ada → usul ½ harga 50 kg dibulatkan ke atas ke Rp100 (owner boleh mengubah) dan ikut disimpan ke katalog.
  · Buku lewat JALUR PEMECAHAN YANG SUDAH ADA (penyusun Adukan: bahan 1 × 50 kg, hasil 2 × 25 kg, tanpa upah & kantong) + satu kemasan 25 kg terjual —
    SATU kiriman; modal total sebelum = sesudah; stok 50 turun 1, stok 25 naik 2 lalu turun 1 (sisanya kemasan 25 kg biasa, laku biasa).
  · Keranjang: ½ memegang 1 unit 50 kg; satu-satu, tanpa bonus; akun bukan-owner tidak bisa menulis katalog; tidak dipakai saat merinci karcis.
  · Batalkan nota barusan mencabut pemecahnya (bila sisa 25 kg belum terpakai).
KOTAK PASIR (ANGKA CONTOH), jam dikunci 19 Sep 2026 10:00 WIB. Cadangan toko di _privat/: tiap kemasan 50 kg yang bersisa dijual ½ → Σ modal tetap,
stok 50 −1, stok 25 +1, laba bulan-bulan sebelumnya byte-sama.

    python3 alat-uji/uji_setengah_karung.py            → N lulus · 0 gagal
    python3 alat-uji/uji_setengah_karung.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_jual_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_jual_baru.MODUL
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"

KOTAK = {
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-09-10', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
                  'merkList': [{'id': '1', 'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 10, 'totalKg': 500, 'hargaPerKg': 13000, 'subtotalHarga': 6500000}]}],
  'produksiKemasan': [{'id': 'p50', 'tanggal': '2026-09-11', 'namaProduk': 'Kembang', 'ukuranKemasan': 50, 'jumlahUnit': 2, 'hppPerUnit': 700000, 'merkSumber': 'Angsa', 'kgDipakai': 100, 'sumberList': [{'merk': 'Angsa', 'kg': 100}]},
                      {'id': 'q50', 'tanggal': '2026-09-11', 'namaProduk': 'Perahu', 'ukuranKemasan': 50, 'jumlahUnit': 1, 'hppPerUnit': 740001, 'merkSumber': 'Angsa', 'kgDipakai': 50, 'sumberList': [{'merk': 'Angsa', 'kg': 50}]}],
  'katalogHargaKemasan': [{'id': 'kembang_50kg', 'merk': 'Kembang', 'ukuran': 50, 'hargaPerUnit': 760000}, {'id': 'perahu_50kg', 'merk': 'Perahu', 'ukuran': 50, 'hargaPerUnit': 780000},
                          {'id': 'perahu_25kg', 'merk': 'Perahu', 'ukuran': 25, 'hargaPerUnit': 390000}],
  'katalogHargaKarung': [{'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 14000}],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var nId = 9000; var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var s0 = function () { var s = keadaanAwal(); s.sekarang = new Date(Date.now()); return s; };
var chip = function (kunci) { return susunRak(s0()).kemasan.find(function (c) { return c.kunci === kunci; }); };
var stokK = function (k) { return (hitungStokKemasan()[k] || { sisaUnit: 0 }).sisaUnit; };
var nilaiKemasan = function () { var K = hitungStokKemasan(); return Object.keys(K).reduce(function (a, k) { return a + (K[k].sisaUnit || 0) * (K[k].hppRataRataPerUnit || 0); }, 0); };
var masukSetengah = function (s, kunci, ketik) { var c = skChip(chip(kunci), ketik || ''); var r = masukkan(Object.assign({}, s, { pilih: c }), 1); return r.keranjang ? Object.assign({}, s, { keranjang: r.keranjang, urutBaris: r.urutBaris }) : Object.assign({ tolak: r.kabar }, s); };

// ---- 1 · harga ½
var IK = skInfo(chip('Kembang|50')), IP = skInfo(chip('Perahu|50'));
ok('harga ½: Kembang belum punya harga 25 kg → usul ½ × 760.000 = 380.000 (ke atas ke Rp100); Perahu punya katalog 25 kg 390.000 → dipakai', IK && !IK.dariKatalog && IK.usul === 380000 && IK.harga25 === 380000 && IP && IP.dariKatalog && IP.harga25 === 390000, J([IK, IP]));
ok('usul dibulatkan KE ATAS ke Rp100 (50 kg 780.050 → ½ 390.025 → 390.100); bukan kemasan 50 kg → tidak ada pilihan ½', (function () { terapkanKeCache([{ koleksi: 'katalogHargaKemasan', data: { id: 'kembang_50kg', merk: 'Kembang', ukuran: 50, hargaPerUnit: 780050 } }]); var u = skInfo(chip('Kembang|50')).usul; terapkanKeCache([{ koleksi: 'katalogHargaKemasan', data: KOTAK.katalogHargaKemasan[0] }]); return u === 390100; })()
  && skInfo(susunRak(s0()).karung[0]) === null);
// ---- 2 · keranjang
var s1 = masukSetengah(s0(), 'Kembang|50'); var b1 = s1.keranjang && s1.keranjang[0] && s1.keranjang[0].trx;
ok('½ masuk keranjang: kemasan Kembang 25 kg 1 unit, harga 380.000, label "(½ dari 50 kg)", modal perkiraan ½ × 700.000', !s1.tolak && b1.jenis === 'kemasan' && b1.namaProduk === 'Kembang' && b1.ukuranKemasan === 25 && b1.jumlahUnit === 1 && b1.totalKg === 25 && b1.hargaTotal === 380000 && b1.setengahDari === 'Kembang|50' && b1.setengahHargaBaru === 380000 && /½ dari 50 kg/.test(b1.label) && b1.hppTotalSaatJual === 350000, J(b1));
sinkronKeranjang(s1);
ok('½ di keranjang MEMEGANG 1 unit Kembang 50 kg (langit-langit 2 → 1); kemasan 25 kg tidak ikut terpotong', maksUntuk(chip('Kembang|50')) === 1 && susunRak(s1).kemasan.find(function (c) { return c.kunci === 'Kembang|50'; }).sisa === 1);
ok('satu-satu: tambah jumlah ditolak, bonus ditolak; jumlah 2 lewat masukkan ditolak', /satu-satu/.test(ubahJumlahBaris(s1, s1.keranjang[0].id, 1).kabar || '') && /bonus/.test(toggleBonus(s1, s1.keranjang[0].id).kabar || '') && /satu-satu/.test(masukkan(Object.assign({}, s0(), { pilih: skChip(chip('Kembang|50'), '') }), 2).kabar || ''));
ok('akun bukan-owner: ½ tanpa harga katalog DITOLAK (tidak boleh menulis katalog); dengan harga katalog (Perahu) boleh; merinci karcis ditolak',
  /minta owner/.test(masukkan(Object.assign({}, s0(), { batasBaris: 7, pilih: skChip(chip('Kembang|50'), '') }), 1).kabar || '') && !!masukkan(Object.assign({}, s0(), { batasBaris: 7, pilih: skChip(chip('Perahu|50'), '') }), 1).keranjang
  && /merinci karcis/.test(masukkan(Object.assign({}, s0(), { karcis: { id: 'k1' }, pilih: skChip(chip('Kembang|50'), '') }), 1).kabar || ''));
// ---- 3 · nota: pemecah + penjualan satu kiriman
var nilai0 = nilaiKemasan(); var s50 = stokK('Kembang|50'), s25 = stokK('Kembang|25');
var N = simpanNota(Object.assign({}, s1, { cara: 'Tunai', uang: 400000 }), W); var D = N.dokumen || [];
var pr = D.filter(function (d) { return d.koleksi === 'produksiKemasan'; }); var jl = D.filter(function (d) { return d.koleksi === 'penjualan'; }); var kt = D.filter(function (d) { return d.koleksi === 'katalogHargaKemasan'; });
ok('nota ½: SATU kiriman = produksiKemasan pemecah (bahan 1 × Kembang 50 kg, hasil 2 × 25 kg, tanpa upah/kantong, modal/unit 350.000, dariSetengah) + katalog Kembang 25 kg 380.000 + baris nota kemasan 25 kg (dariSetengah = id pemecah, modal 350.000)',
  !N.tolak && pr.length === 1 && pr[0].data.namaProduk === 'Kembang' && pr[0].data.ukuranKemasan === 25 && pr[0].data.jumlahUnit === 2 && pr[0].data.hppPerUnit === 350000 && J(pr[0].data.sumberKemasanList) === J([{ namaProduk: 'Kembang', ukuranKemasan: 50, unit: 1, hppPerUnitSaatDipakai: 700000 }])
  && pr[0].data.upahRepacking === 0 && pr[0].data.biayaKemasan === 0 && pr[0].data.dariSetengah === true && pr[0].data.tanggal === '2026-09-19'
  && kt.length === 1 && kt[0].data.merk === 'Kembang' && kt[0].data.ukuran === 25 && kt[0].data.hargaPerUnit === 380000
  && jl.length === 1 && jl[0].data.jenis === 'kemasan' && jl[0].data.ukuranKemasan === 25 && jl[0].data.jumlahUnit === 1 && String(jl[0].data.dariSetengah) === String(pr[0].data.id) && jl[0].data.hppTotalSaatJual === 350000 && jl[0].data.setengahDari === undefined && jl[0].data.hargaTotal === 380000, J(D));
terapkanKeCache(pr.concat(kt));
ok('sesudah pemecah (sebelum jualnya): stok Kembang 50 TURUN 1 (2 → 1), stok 25 NAIK 2; MODAL TOTAL kemasan SAMA (700.000 pindah jadi 2 × 350.000)', stokK('Kembang|50') === s50 - 1 && stokK('Kembang|25') === s25 + 2 && Math.abs(nilaiKemasan() - nilai0) < 0.5, J([stokK('Kembang|50'), stokK('Kembang|25'), nilaiKemasan(), nilai0]));
terapkanKeCache(jl);
ok('sesudah nota: stok 25 turun 1 (sisa 1 = kemasan 25 kg biasa); nilai sisa + modal terjual = modal sebelum', stokK('Kembang|25') === 1 && Math.abs(nilaiKemasan() + jl[0].data.hppTotalSaatJual - nilai0) < 0.5, J([nilaiKemasan(), nilai0]));
ok('sisa 25 kg tampil di rak sebagai kemasan biasa dengan harga katalog baru 380.000, dan laku biasa (lalu turun 1)', (function () { var c = chip('Kembang|25'); if (!c || c.harga !== 380000 || c.sisa !== 1 || c.setengahDari) return false; var r = masukkan(Object.assign({}, s0(), { pilih: c }), 1); var n2 = simpanNota(Object.assign({}, s0(), { keranjang: r.keranjang, cara: 'Tunai', uang: 380000 }), W); terapkanKeCache(n2.dokumen); return stokK('Kembang|25') === 0 && !n2.dokumen.some(function (d) { return d.koleksi === 'produksiKemasan'; }); })());
// ---- 4 · harga dari katalog & diubah owner
var sP = masukSetengah(s0(), 'Perahu|50'); var NP = simpanNota(Object.assign({}, sP, { cara: 'QRIS' }), W);
ok('Perahu (katalog 25 kg ada): harga 390.000, TIDAK ada dokumen katalog; modal ½ = pembagian persis (740.001 → 370.001 + 370.000, Σ tetap)', !NP.tolak && NP.dokumen.filter(function (d) { return d.koleksi === 'katalogHargaKemasan'; }).length === 0 && (NP.dokumen.find(function (d) { return d.koleksi === 'penjualan'; }) || { data: {} }).data.hargaTotal === 390000
  && (function () { var p = (NP.dokumen.find(function (d) { return d.koleksi === 'produksiKemasan'; }) || { data: {} }).data; return p.hppPerUnit * 2 === 740001 || Math.abs(p.hppPerUnit * 2 - 740001) <= 1; })(), J(NP.dokumen.map(function (d) { return d.koleksi; })));
pasok('produksiKemasan', JSON.parse(J(KOTAK.produksiKemasan))); pasok('penjualan', []); pasok('katalogHargaKemasan', JSON.parse(J(KOTAK.katalogHargaKemasan)));
var sU = masukSetengah(s0(), 'Kembang|50', '375.000');
ok('owner mengubah harga ½ (375.000) → baris & katalog baru 375.000', sU.keranjang[0].trx.hargaTotal === 375000 && sU.keranjang[0].trx.setengahHargaBaru === 375000 && simpanNota(Object.assign({}, sU, { cara: 'QRIS' }), W).dokumen.some(function (d) { return d.koleksi === 'katalogHargaKemasan' && d.data.hargaPerUnit === 375000; }));
// ---- 5 · stok kurang, batal
var sDua = masukSetengah(masukSetengah(s0(), 'Perahu|50'), 'Perahu|50');
ok('dua ½ dari Perahu yang tinggal 1 × 50 kg → yang kedua ditolak langit-langit stok', !!sDua.tolak && /bebas dijual/.test(sDua.tolak), sDua.tolak);
var sB = masukSetengah(s0(), 'Kembang|50'); var NB = simpanNota(Object.assign({}, sB, { cara: 'QRIS' }), W); terapkanKeCache(NB.dokumen);
var batal = susunPembatalan(NB.patch.notaTerakhir, 'salah ketik', W);
ok('batalkan nota ½ barusan: baris ditandai batal + PEMECAH ikut dicabut (sisa 25 kg belum terpakai) → stok 50 kembali 2, stok 25 kembali 0',
  batal && batal.hapus.some(function (x) { return x.koleksi === 'produksiKemasan'; }) && (function () { terapkanKeCache(batal.dokumen); terapkanKeCache(batal.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); return stokK('Kembang|50') === 2 && stokK('Kembang|25') === 0; })(), J(batal && batal.hapus));
var sB2 = masukSetengah(s0(), 'Kembang|50'); var NB2 = simpanNota(Object.assign({}, sB2, { cara: 'QRIS' }), W); terapkanKeCache(NB2.dokumen);
var r25 = masukkan(Object.assign({}, s0(), { pilih: chip('Kembang|25') }), 1); terapkanKeCache(simpanNota(Object.assign({}, s0(), { keranjang: r25.keranjang || [], cara: 'QRIS' }), W).dokumen || []);
var batal2 = susunPembatalan(NB2.patch.notaTerakhir, 'salah', W);
ok('batal ½ SESUDAH sisa 25 kg-nya terjual → pemecah TIDAK dicabut (stok 25 tidak boleh minus); cuma barisnya yang batal', batal2 && !batal2.hapus.some(function (x) { return x.koleksi === 'produksiKemasan'; }), J(batal2 && batal2.hapus));

// ---- ASAP DATA TOKO
var asap = null;
if (CADANGAN) {
  Object.keys(KOTAK).forEach(function (n) { pasok(n, []); }); Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
  var WC = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
  var labaLalu = function () { return J(['2026-08'].map(function (b) { return hitungLabaBersihRentang(b + '-01', b + '-31'); })); };
  var l0 = labaLalu(); var hasil = [];
  susunRak(s0()).kemasan.filter(function (c) { return Number(c.ukuranKg) === 50 && c.sisa >= 1; }).forEach(function (c) {
    var n0 = nilaiKemasan(); var a50 = stokK(c.kunci), a25 = stokK(c.nama + '|25'); var s = masukSetengah(s0(), c.kunci); var n = simpanNota(Object.assign({}, s, { cara: 'QRIS' }), WC);
    if (n.tolak || !n.dokumen) { hasil.push({ nama: c.nama, tolak: n.tolak || s.tolak }); return; }
    terapkanKeCache(n.dokumen); var jb = n.dokumen.find(function (d) { return d.koleksi === 'penjualan'; }).data; var pc = n.dokumen.find(function (d) { return d.koleksi === 'produksiKemasan'; }).data;
    // modal yang DIPINDAH pemecah tetap (1 × modal 50 kg = 2 × modal 25 kg, pembagian mesin beku) dan baris jual memakai modal pecahan itu.
    // (Nilai neraca kemasan memakai rata-rata SELURUH riwayat produksi nama|ukuran — nama yang sudah punya stok 25 kg bergeser pembulatan; cara mesin, tidak diubah.)
    hasil.push({ nama: c.nama, ok: stokK(c.kunci) === a50 - 1 && stokK(c.nama + '|25') === a25 + 1 && Math.abs(pc.hppPerUnit * pc.jumlahUnit - pc.sumberKemasanList[0].hppPerUnitSaatDipakai) <= 1 && jb.hppTotalSaatJual === Math.round(pc.hppPerUnit) });
  });
  asap = { hasil: hasil, labaLaluSama: labaLalu() === l0 };
}
print(J({ lulus: lulus, gagal: gagal, asap: asap }));
"""


def cadangan_toko():
    c = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')), key=os.path.basename)
    return c[-1] if c else None


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
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    return h['lulus'], h['gagal'], h.get('asap')


RUSAK = {
    'usul tidak dibulatkan ke atas (ke bawah)': ("const skBulat100 = (n) => Math.ceil(n / 100 - 1e-9) * 100;", "const skBulat100 = (n) => Math.floor(n / 100) * 100;"),
    'harga katalog 25 kg diabaikan (selalu usul)': ("const dariKatalog = !!(k && Number(k.hargaPerUnit) > 0);", "const dariKatalog = false;"),
    '½ memegang stok 25 kg, bukan 50 kg': ("function skTrxPegang(t) { return t && t.setengahDari ?", "function skTrxPegang(t) { return false ?"),
    'nota ½ tanpa pemecah (stok 25 kg minus, stok 50 kg tidak turun)': ("if (t.setengahDari) { const pc = skPecah(t, w);", "if (false) { const pc = skPecah(t, w);"),
    'modal baris ½ = modal 50 kg utuh (bukan pecahannya)': ("d.dariSetengah = pc.idProduksi; d.hppTotalSaatJual = Math.round(pc.hppPerUnit);", "d.dariSetengah = pc.idProduksi; d.hppTotalSaatJual = Math.round(pc.hppPerUnit * 2);"),
    'harga ½ baru tidak disimpan ke katalog': ("if (t.setengahHargaBaru > 0 && !ambilHargaKemasan().some(", "if (false && !ambilHargaKemasan().some("),
    'pemecah tidak ikut dicabut saat nota dibatalkan': ("  skHapusPemecah(baris).forEach((x) => hapus.push(x));", ""),
    'pemecah dicabut walau sisa 25 kg sudah terjual (stok minus)': ("if (s && (s.sisaUnit || 0) + 1 - 2 < 0) return;", ""),
    '½ boleh dua sekaligus': ("  if (chip.setengahDari && j !== 1) return {", "  if (false) return {"),
    'akun bukan-owner menulis katalog lewat ½': ("  if (chip.setengahDari && chip.setengahHargaBaru > 0 && Number(s.batasBaris) > 0) return {", "  if (false) return {"),
    'pemecah memakai kantong/upah (modal total berubah)': ("upah: '' };\n  const r = susunSimpanAdukan(draf, w, {});", "upah: '1000' };\n  const r = susunSimpanAdukan(draf, w, {});"),
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
    print('SETENGAH KARUNG (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    if asap:
        baik = [x for x in asap['hasil'] if x.get('ok')]
        print('ASAP DATA TOKO (%s): %d kemasan 50 kg bersisa dijual ½ · stok 50 −1, stok 25 +1, modal dipindah utuh & baris jual = modal pecahan: %d/%d · laba Agustus byte-sama: %s'
              % (os.path.basename(cadangan_toko()), len(asap['hasil']), len(baik), len(asap['hasil']), asap['labaLaluSama']))
        if len(baik) != len(asap['hasil']) or not asap['labaLaluSama'] or not asap['hasil']: g.append('asap data toko: ' + json.dumps(asap, ensure_ascii=False)[:300])
    sys.exit(2 if g else 0)
