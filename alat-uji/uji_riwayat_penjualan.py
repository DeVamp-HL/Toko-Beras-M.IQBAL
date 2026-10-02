#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_riwayat_penjualan.py — RIWAYAT PENJUALAN (owner 28 Sep 2026): Jual › tab Riwayat, SEMUA nota sejak awal, baca saja; per nota Struk & Retur lewat jalur yang
sudah ada. KOTAK PASIR (angka contoh), jam dikunci 19 Sep 2026 10:00 WIB.
  · Satu nota = kunci panel "Hari ini" (grupNota → trxId → id); baris satu takaran wadah digabung; nota batal / sudah dirinci disembunyikan kecuali diminta.
  · Total nota = Σ hargaTotal baris berlaku; omzet = total nota − uang retur hari itu (rumus mesin laba) — disebut hanya tanpa saringan jenis/cara/cari.
  · Saringan periode / jenis / cara / cari (nama, barang, nominal) menumpuk; halaman 50 nota; jumlah per hari dihitung dari SEMUA nota yang cocok hari itu.
  · Retur hanya untuk baris karung/kemasan yang boleh kembali (rtDasarRetur = aturan rtDasarNota; 39b no. 37: nota BON ikut, memotong bon); yang tidak boleh menyebut alasannya.
Asap cadangan (_privat/, lokal): tiap hari omzet riwayat = rekapHari mesin, jumlah nota = panel "Hari ini", Σ total nota = Σ baris berlaku.

    python3 alat-uji/uji_riwayat_penjualan.py            → N lulus · 0 gagal
    python3 alat-uji/uji_riwayat_penjualan.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kunci_periode  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_kunci_periode.MODUL + ['baru/js/layar/riwayat-logika.js']
LAYAR = ['baru/js/layar/jual.js']
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(i, tgl, jam, jenis, n, cara='Tunai', **k):
    d = {'id': i, 'tanggal': tgl, 'jam': jam, 'jenis': jenis, 'hargaTotal': n, 'caraBayar': cara, 'namaPelanggan': k.pop('nama', ''), 'hppTotalSaatJual': int(n * 0.9)}
    d.update(k); return d


KOTAK = {
  'batchMasuk': [{'id': 1, 'tanggal': '2026-08-01', 'pemasok': 'PEMASOK A', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [
      {'id': '1', 'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 20, 'totalKg': 1000, 'hargaPerKg': 14000, 'subtotalHarga': 14000000}]}],
  'penjualan': [
    # A · 19 Sep, trxId, karung + literan wadah dua baris satu takaran (digabung)
    jual(1001, '2026-09-19', '09:00', 'karung', 700000, trxId='tA', merkSumber='Angsa', beratKarungAcuan=50, jumlahKarung=1, totalKg=50),
    jual(1002, '2026-09-19', '09:00', 'literan', 26000, trxId='tA', merkSumber='Wadah W1', dariWadah='W1', takaranId='k1', jumlahLiter=1.2, totalKg=1),
    jual(1003, '2026-09-19', '09:00', 'literan', 13000, trxId='tA', merkSumber='Wadah W1', dariWadah='W1', takaranId='k1', jumlahLiter=0.8, totalKg=0.6),
    # B · 19 Sep, grupNota, kemasan, BON bernama
    jual(1004, '2026-09-19', '08:30', 'kemasan', 140000, 'Kredit', grupNota='gB', namaProduk='Kembang', ukuranKemasan=5, jumlahUnit=2, totalKg=10, nama='Bu Sari'),
    # C · 19 Sep, dibatalkan (QRIS)
    jual(1005, '2026-09-19', '08:00', 'karung', 700000, 'QRIS', trxId='tC', merkSumber='Angsa', beratKarungAcuan=50, jumlahKarung=1, totalKg=50, dibatalkan=True),
    # D · 18 Sep, karcis kasir darurat yang SUDAH dirinci → digantikan nota E
    jual(1006, '2026-09-18', '17:00', 'kasir_darurat_nominal', 148500, dikoreksiOleh='1007', namaProduk='(tidak tercatat — kasir darurat)'),
    jual(1007, '2026-09-18', '17:00', 'karung', 148500, grupNota='gE', merkSumber='Angsa', beratKarungAcuan=50, jumlahKarung=0.2, totalKg=10, rinciDari='1006', asalDarurat=True),
    # F · 18 Sep, karcis belum dirinci
    jual(1008, '2026-09-18', '16:00', 'kasir_darurat_nominal', 55000, namaProduk='(tidak tercatat — kasir darurat)'),
    # G · 17 Sep, pengganti retur (Rp0) + repack
    jual(1009, '2026-09-17', '12:00', 'karung', 0, trxId='tG', merkSumber='Angsa', beratKarungAcuan=50, jumlahKarung=1, totalKg=50, penggantiRetur=True, nilaiBarangPengganti=700000),
    jual(1010, '2026-09-17', '12:00', 'repacking', 72500, trxId='tG', namaProduk='Angsa', merkSumber='Angsa', totalKg=5),
    # H · 20 Agu (periode lama), memuat unit BONUS (tidak bisa diretur — alasannya disebut)
    jual(1011, '2026-08-20', '10:00', 'kemasan', 70000, trxId='tH', namaProduk='Kembang', ukuranKemasan=5, jumlahUnit=1, totalKg=5, bonusUnit=1),
  ],
  'retur': [{'id': 2001, 'tanggal': '2026-09-19', 'jam': '09:30', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 50, 'jumlahKarung': 1, 'kondisi': 'utuh', 'penyelesaian': 'refund', 'uangKembali': 90000, 'nominalRefund': 90000, 'dariPenjualanId': '1011'}],
  'katalogHargaKarung': [{'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 14000}],
  'katalogHargaKemasan': [{'id': 'Kembang|5', 'merk': 'Kembang', 'ukuran': 5, 'hargaPerUnit': 70000}],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
var KOL = Object.keys(KOTAK); var pulih = function () { KOL.forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); }); }; pulih();
var KINI = new Date('2026-09-19T10:00:00'); var S = function (o) { return rwSusun(Object.assign({ rwPeriode: 'semua' }, o || {}), KINI); };
var N = rwSemuaNota(); var notaK = function (k) { return N.find(function (o) { return o.kunci === k; }); };
// ---- 1 · pengelompokan nota
ok('nota dikelompokkan dengan kunci panel "Hari ini" (grupNota → trxId → id): 8 nota dari 11 baris; terbaru dulu (19 Sep 09:00 → 20 Agu; jam sama → id terbesar dulu)', N.length === 8 && N[0].kunci === 'tA' && N[N.length - 1].kunci === 'tH' && J(N.map(function (o) { return o.kunci; })) === J(['tA', 'gB', 'tC', 'gE', '1006', '1008', 'tG', 'tH']), J(N.map(function (o) { return [o.kunci, o.tanggal, o.jam]; })));
var A = notaK('tA');
ok('nota A: dua baris internal satu takaran wadah digabung jadi satu baris "W1 2 L" Rp39.000 (+ karung) — total Rp739.000, status berlaku, cara Tunai', A.nBaris === 2 && A.baris[1].teks === 'W1 2 L' && A.baris[1].n === 39000 && A.baris[0].teks === 'Angsa karung 50 kg × 1' && A.total === 739000 && A.status === 'berlaku' && A.cara === 'Tunai', J(A));
ok('status: C dibatalkan → batal (total berlaku 0, totalAsli 700.000); karcis 1006 digantikan rincian → dirinci; karcis 1008 belum dirinci → berlaku, teks "Karcis kasir — nominal, belum dirinci"', notaK('tC').status === 'batal' && notaK('tC').total === 0 && notaK('tC').totalAsli === 700000 && notaK('1006').status === 'dirinci' && notaK('1008').status === 'berlaku' && notaK('1008').baris[0].teks === 'Karcis kasir — nominal, belum dirinci' && notaK('1008').karcis === true, J([notaK('tC'), notaK('1006'), notaK('1008')]));
ok('retur: karung Tunai berlaku bisa diretur; literan tidak (tanpa alasan retur karena bukan karung/kemasan); kemasan BON bisa (39b no. 37: returnya memotong bon); kemasan ber-BONUS tidak + alasan rtDasarNota disebut; pengganti retur & nota batal tidak', A.baris[0].bisaRetur === true && A.baris[1].bisaRetur === false && A.baris[1].sebabRetur === '' && notaK('gB').baris[0].bisaRetur === true && notaK('gB').baris[0].sebabRetur === '' && notaK('tH').baris[0].bisaRetur === false && /BONUS/.test(notaK('tH').baris[0].sebabRetur) && notaK('tG').baris[0].bisaRetur === false && notaK('tG').baris[0].pengganti === true && notaK('tC').baris[0].bisaRetur === false, J([A.baris, notaK('gB').baris, notaK('tH').baris, notaK('tG').baris]));
// ---- 2 · riwayat tanpa saringan
var R = S();
ok('semua (bawaan): 6 nota berlaku (batal & dirinci disembunyikan); total nota = Σ baris berlaku = Rp1.225.000; per cara Tunai/Bon', R.n === 6 && R.nBerlaku === 6 && R.omzet === 1225000 && R.omzet === ambilPenjualan().reduce(function (a, p) { return a + (p.hargaTotal || 0); }, 0) && R.perCara.Tunai === 1085000 && R.perCara.Kredit === 140000 && !R.perCara.QRIS, J(R));
ok('per hari: 19 Sep 2 nota Rp879.000 − retur Rp90.000 = omzet Rp789.000 (= rekapHari mesin); 18 Sep 2 nota; 17 Sep & 20 Agu tanpa retur', R.hari[0].tanggal === '2026-09-19' && R.hari[0].nNota === 2 && R.hari[0].omzet === 879000 && R.hari[0].retur === 90000 && R.hari[0].bersih === 789000 && R.hari[0].bersih === Math.round(rekapHari('2026-09-19').omzet) && R.hari[1].tanggal === '2026-09-18' && R.hari[1].nNota === 2 && R.hari[1].retur === 0 && R.hari[0].judul === 'Sabtu 19 Sep 2026', J(R.hari.map(function (h) { return [h.tanggal, h.nNota, h.omzet, h.retur, h.bersih]; })));
ok('ringkas menyebut total nota, retur, omzet, per cara; saringan kosong → "Semua nota sejak Kamis 20 Agu 2026"', R.ringkas === '6 nota · total nota Rp1.225.000 − retur Rp90.000 = omzet Rp1.135.000 · Tunai Rp1.085.000 · Bon Rp140.000' && R.saringTeks === 'Semua nota sejak Kamis 20 Agu 2026' && R.retur === 90000 && R.bersih === 1135000, J([R.ringkas, R.saringTeks]));
ok('tampilkan batal / dirinci: 8 nota (6 berlaku), omzet tetap Rp1.225.000', S({ rwBatal: true }).n === 8 && S({ rwBatal: true }).nBerlaku === 6 && S({ rwBatal: true }).omzet === 1225000);
// ---- 3 · saringan
ok('periode: hari ini 2 nota · 7 hari 5 · 30 hari 5 (20 Agu di luar 21 Agu–19 Sep) · bulan ini 5 · semua 6', S({ rwPeriode: 'hari' }).n === 2 && S({ rwPeriode: '7' }).n === 5 && S({ rwPeriode: '30' }).n === 5 && S({ rwPeriode: 'bulan' }).n === 5 && S({ rwPeriode: 'semua' }).n === 6, J([S({ rwPeriode: 'hari' }).n, S({ rwPeriode: '7' }).n, S({ rwPeriode: '30' }).n, S({ rwPeriode: 'bulan' }).n]));
ok('tepi periode: 7 hari = 13–19 Sep (hari ini ikut) → nota 13 Sep masuk, 12 Sep tidak; 30 hari = 21 Agu–19 Sep', denganCacheSementara([{ koleksi: 'penjualan', data: { id: 3001, tanggal: '2026-09-13', jam: '10:00', jenis: 'literan', hargaTotal: 1000, caraBayar: 'Tunai', trxId: 'e13' } }, { koleksi: 'penjualan', data: { id: 3002, tanggal: '2026-09-12', jam: '10:00', jenis: 'literan', hargaTotal: 1000, caraBayar: 'Tunai', trxId: 'e12' } }, { koleksi: 'penjualan', data: { id: 3003, tanggal: '2026-08-21', jam: '10:00', jenis: 'literan', hargaTotal: 1000, caraBayar: 'Tunai', trxId: 'e21' } }], function () {
  return S({ rwPeriode: '7' }).n === 6 && S({ rwPeriode: '30' }).n === 8 && J(rwRentang('7', KINI)) === J({ dari: '2026-09-13', sampai: '2026-09-19' }) && J(rwRentang('30', KINI)) === J({ dari: '2026-08-21', sampai: '2026-09-19' }); }));
ok('jenis: karung 3 nota (A, E, G) · kemasan 2 · literan 1 · repack 1 · karcis 1 (yang belum dirinci)', S({ rwJenis: 'karung' }).n === 3 && S({ rwJenis: 'kemasan' }).n === 2 && S({ rwJenis: 'literan' }).n === 1 && S({ rwJenis: 'repacking' }).n === 1 && S({ rwJenis: 'karcis' }).n === 1);
ok('cara: Bon 1 nota (Bu Sari); QRIS 0 (yang QRIS batal) → kalimat kosong', S({ rwCara: 'Kredit' }).n === 1 && S({ rwCara: 'Kredit' }).hari[0].nota[0].nama === 'Bu Sari' && S({ rwCara: 'QRIS' }).n === 0 && S({ rwCara: 'QRIS' }).kosong === 'Tidak ada nota yang cocok dengan saringan ini.');
ok('cari: nama "sari" → 1 · barang "kembang" → 2 · nominal "739.000" / "739000" → nota A · kata ganda "angsa repack" → G', S({ rwCari: 'sari' }).n === 1 && S({ rwCari: 'kembang' }).n === 2 && S({ rwCari: '739.000' }).n === 1 && S({ rwCari: '739000' }).hari[0].nota[0].kunci === 'tA' && S({ rwCari: 'angsa repack' }).n === 1 && S({ rwCari: 'angsa repack' }).hari[0].nota[0].kunci === 'tG');
ok('saringan menumpuk & disebut; dengan saringan jenis/cara/cari retur TIDAK dikurangkan (retur & bersih null) karena tidak bisa dipilah', S({ rwPeriode: '7', rwJenis: 'karung', rwCara: 'Tunai' }).saringTeks === 'Saringan: 7 hari · Karung · Tunai' && S({ rwJenis: 'karung' }).retur === null && S({ rwJenis: 'karung' }).hari[0].bersih === null && !/retur/.test(S({ rwJenis: 'karung' }).ringkas));
// ---- 4 · halaman
var banyak = []; for (var i = 0; i < 120; i++) banyak.push({ id: 5000 + i, tanggal: '2026-09-15', jam: ('0' + (8 + Math.floor(i / 12))).slice(-2) + ':' + ('0' + (i % 60)).slice(-2), jenis: 'literan', hargaTotal: 1000, caraBayar: 'Tunai', trxId: 'p' + i, merkSumber: 'Angsa', jumlahLiter: 1, totalKg: 0.8 });
denganCacheSementara(banyak.map(function (d) { return { koleksi: 'penjualan', data: d }; }), function () {
  var P = rwSusun({ rwPeriode: 'semua', rwJenis: 'literan' }, KINI); var P2 = rwSusun({ rwPeriode: 'semua', rwJenis: 'literan', rwN: 100 }, KINI);
  ok('halaman: 121 nota literan → tampil 50, "lebih"; kepala 15 Sep menyebut SEMUA 120 nota hari itu (bukan yang tergambar saja); rwN 100 → 100', P.n === 121 && P.nTampil === 50 && P.lebih === true && P.hari.find(function (h) { return h.tanggal === '2026-09-15'; }).nNota === 120 && P2.nTampil === 100, J([P.n, P.nTampil, P.hari.map(function (h) { return [h.tanggal, h.nNota, h.nota.length]; })]));
});
ok('tanpa penjualan: kalimat "Belum ada penjualan tercatat."', denganCacheSementara([], function () { pasok('penjualan', []); var x = S(); pulih(); return x.kosong === 'Belum ada penjualan tercatat.' && x.n === 0; }));
// ---- ASAP DATA TOKO
var asap = null;
if (CADANGAN) {
  Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
  var K2 = new Date(TGL_CAD + 'T23:00:00'); var RA = rwSusun({ rwPeriode: 'semua', rwN: 1e9 }, K2);
  var hariBeda = RA.hari.filter(function (h) { return h.bersih !== Math.round(rekapHari(h.tanggal).omzet); }).map(function (h) { return h.tanggal; });
  var notaBeda = RA.hari.filter(function (h) { var st = keadaanAwal(); st.sekarang = new Date(h.tanggal + 'T12:00:00'); return hariIni(st).nota !== h.nNota || Math.round(hariIni(st).omzet) !== (h.bersih === null ? h.omzet : h.bersih); }).map(function (h) { return h.tanggal; });   // 39b no. 19: omzet "Hari ini" = bersih retur (= "… = omzet" riwayat)
  var sumBerlaku = Math.round(ambilPenjualan().reduce(function (a, p) { return a + (p.hargaTotal || 0); }, 0));
  var hariJual = {}; ambilPenjualan().forEach(function (p) { hariJual[p.tanggal] = 1; });
  asap = { nota: RA.n, hari: RA.hari.length, hariJual: Object.keys(hariJual).length, total: RA.omzet, sumBerlaku: sumBerlaku, retur: RA.retur, bersih: RA.bersih, hariBeda: hariBeda, notaBeda: notaBeda, semua: rwSemuaNota().length };
}
print(J({ lulus: lulus, gagal: gagal, asap: asap }));
"""


def cadangan_toko():
    c = glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json'))
    return max(c, key=os.path.getmtime) if c else None


def baca(ganti=None):
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(MODUL + LAYAR)))
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def periksa_statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    jl = t['baru/js/layar/jual.js']; rw = t['baru/js/layar/riwayat-logika.js']; lg = t['baru/js/layar/jual-logika.js']
    ok('Jual: tab Riwayat sesudah Retur (JALUR), gambarRiwayat dari RW.rwSusun', "['retur', 'Retur'], ['riwayat', 'Riwayat']]" in lg and "if (s.jalur === 'riwayat') return gambarRiwayat(s);" in jl and 'const R = RW.rwSusun(s, s.sekarang || new Date());' in jl)
    ok('tindakan per nota lewat jalur yang ADA: Struk = bukaStruk (trx/grup/id), Retur = tunjukNota hanya untuk baris bisaRetur', 'data-aksi="bukaStruk" data-trx="${o.trxId || \'\'}" data-grup="${o.grupNota || \'\'}" data-id="${o.id}"' in jl and '${b.bisaRetur ? h`<span class="kaca-btn kecil" data-aksi="tunjukNota" data-id="${b.id}">retur</span>` : \'\'}' in jl)
    ok('riwayat-logika baca saja: tanpa DOM, tanpa penulis (tulisDokumen/dokumen:)', 'document.' not in rw and 'tulisDokumen' not in rw and 'koleksi:' not in rw and 'localStorage' not in rw)
    ok('keadaan awal Jual memuat saringan riwayat (bawaan: semua periode, tanpa batal)', "rwCari: '', rwPeriode: 'semua', rwJenis: '', rwCara: '', rwBatal: false, rwN: 50, rwBuka: null," in lg)
    return out


def semua(ganti=None, bagian=('statis', 'jsc'), pakai_cadangan=False):
    t = baca(ganti); out = []; asap = None; p = None
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        cad = 'null'; tgl = ''
        p = cadangan_toko() if pakai_cadangan else None
        if p:
            d = json.load(open(p, encoding='utf-8')); kol = re.findall(r"\{ nama: '(\w+)'", open(os.path.join(AKAR, 'baru/js/data/koleksi.js'), encoding='utf-8').read())
            cad = json.dumps(dict((n, d[n]) for n in kol if isinstance(d.get(n), list))); tgl = str(d.get('diunduhPada', ''))[:10]
        js = uji_kunci_periode.satu_lingkup('\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL]))
        h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + SKENARIO)
        if h is None: out.append(('jsc · JATUH: ' + e, False, ''))
        else: out += [('jsc · ' + x, False, '') for x in h['gagal']] + [('__jsc', not h['gagal'], h['lulus'])]; asap = h.get('asap')
    return out, asap, p


RW_ = 'baru/js/layar/riwayat-logika.js'; JU_ = 'baru/js/layar/jual.js'
KONTROL = [
    ('nota dikelompokkan per trxId saja (grupNota diabaikan)', {RW_: [("export const rwKunci = (p) => String(p.grupNota || p.trxId || p.id);", "export const rwKunci = (p) => String(p.trxId || p.id);")]}, ('jsc',)),
    ('baris satu takaran tidak digabung', {RW_: [("const tampil = gabungTakaran(hidup.length ? hidup : rows);", "const tampil = hidup.length ? hidup : rows;")]}, ('jsc',)),
    ('nota batal ikut tampil & dijumlah', {RW_: [("&& (S.rwBatal || o.status === 'berlaku' || o.status === 'sebagian')", ""), ("const total = hidup.reduce((a, p) => a + (p.hargaTotal || 0), 0);", "const total = rows.reduce((a, p) => a + (p.hargaTotal || 0), 0);")]}, ('jsc',)),
    ('retur tidak dikurangkan (omzet ≠ laporan)', {RW_: [("returHari[t] = (returHari[t] || 0) + uangKembaliRetur(r);", "returHari[t] = (returHari[t] || 0);")]}, ('jsc',)),
    ('retur dikurangkan walau disaring per jenis', {RW_: [("const bersihBisa = !S.rwJenis && !S.rwCara && !kata.length;", "const bersihBisa = true;")]}, ('jsc',)),
    ('jumlah nota per hari hanya yang tergambar', {RW_: [("nota: [], nNota: perHari[o.tanggal].nota,", "nota: [], nNota: 0,"), ("g.nota.push(o); });", "g.nota.push(o); g.nNota += 1; });")]}, ('jsc',)),
    ('halaman tidak dipotong', {RW_: [("const tampil = cocok.slice(0, n);", "const tampil = cocok;")]}, ('jsc',)),
    ('cari nominal mati', {RW_: [("return hay.indexOf(w) >= 0 || (d.length >= 3 && d === w.replace(/[.,]/g, '') && digit.indexOf(d) >= 0);", "return hay.indexOf(w) >= 0;")]}, ('jsc',)),
    ('literan ditawari retur', {RW_: [("const d = p.jenis === 'karung' || p.jenis === 'kemasan' ? rtDasarRetur(p) : { ok: false };", "const d = { ok: true };")]}, ('jsc',)),
    ('39b-37: riwayat kembali memakai rtDasarNota (nota BON tidak bisa diretur)', {RW_: [("const d = p.jenis === 'karung' || p.jenis === 'kemasan' ? rtDasarRetur(p) : { ok: false };", "const d = p.jenis === 'karung' || p.jenis === 'kemasan' ? rtDasarNota(p) : { ok: false };")]}, ('jsc',)),
    ('alasan retur tidak disebut', {RW_: [("sebabRetur: hidupBaris && (p.jenis === 'karung' || p.jenis === 'kemasan') && d && !d.ok ? String(d.sebab || '') : '',", "sebabRetur: '',")]}, ('jsc',)),
    ('periode 7 hari jadi 8 hari', {RW_: [("if (periode === '7') return { dari: rwGeser(hari, -6), sampai: hari };", "if (periode === '7') return { dari: rwGeser(hari, -7), sampai: hari };")]}, ('jsc',)),
    ('Jual: struk tanpa kunci grupNota', {JU_: [("data-grup=\"${o.grupNota || ''}\" ", "")]}, ('statis',)),
    ('Jual: retur ditawarkan untuk semua baris', {JU_: [("${b.bisaRetur ? h`<span class=\"kaca-btn kecil\" data-aksi=\"tunjukNota\" data-id=\"${b.id}\">retur</span>` : ''}", "${h`<span class=\"kaca-btn kecil\" data-aksi=\"tunjukNota\" data-id=\"${b.id}\">retur</span>`}")]}, ('statis',)),
]

if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti, bagian in KONTROL:
            try: h, _, _ = semua(ganti, bagian)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' · ' + str(e)[:140]); kode = 3; continue
            g = [x for x in h if not x[1]]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h, asap, p = semua(pakai_cadangan=True); g = [x for x in h if not x[1]]
    n = sum(1 for x in h if x[1] and x[0] != '__jsc') + next((x[2] for x in h if x[0] == '__jsc'), 0)
    for x in g: print('   ✗ ' + x[0] + (' → ' + json.dumps(x[2], ensure_ascii=False)[:400] if x[2] not in ('', None) else ''))
    print('RIWAYAT PENJUALAN: %d lulus · %d gagal' % (n, len(g)))
    if asap:
        print('ASAP DATA TOKO (%s): %d nota berlaku dari %d nota · %d hari (hari berpenjualan %d) · total nota %s = Σ baris berlaku %s · retur %s · omzet %s · hari omzet ≠ rekapHari: %s · hari nota/total ≠ "Hari ini": %s'
              % (os.path.basename(p), asap['nota'], asap['semua'], asap['hari'], asap['hariJual'], asap['total'], asap['sumBerlaku'], asap['retur'], asap['bersih'], ', '.join(asap['hariBeda']) or 'tidak ada', ', '.join(asap['notaBeda']) or 'tidak ada'))
        if asap['hariBeda'] or asap['notaBeda'] or asap['total'] != asap['sumBerlaku'] or asap['hari'] != asap['hariJual']: g.append('asap'); print('   ✗ asap data toko gagal')
    sys.exit(1 if g else 0)
