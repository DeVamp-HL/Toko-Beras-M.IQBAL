#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_pemantapan_31.py — putaran 31 (empat perbaikan kecil serah terima 28 Sep 2026), butir yang dibangun:
  31.1 Rinci karcis bertanya NAMA kalau harganya sama: dua nama atau lebih dengan bentuk tebakan yang sama (jalur, berat, jumlah, harga pas) untuk satu
       nominal = SATU tebakan bertanda `seharga` yang menawarkan pilihan — tidak mengambil yang pertama (dulu IR64 Ascent/Elevate/Apex tertukar).
  31.3 Catatan bertanggal MUNDUR (barang masuk / adukan) yang tanggalnya sebelum cocokkan terakhir nama itu memotong buku dua kali → penjaga dua ketukan
       yang menyebut tanggal cocokkan terakhir; koreksi kedatangan lama tidak ditanya; cocokkan wadah & rework bukan hitungan fisik (pola putaran 11).
KOTAK PASIR (angka contoh), jam dikunci 20 Sep 2026 10:00 WIB.

    python3 alat-uji/uji_pemantapan_31.py            → N lulus · 0 gagal
    python3 alat-uji/uji_pemantapan_31.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_wadah_stok_sendiri  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_wadah_stok_sendiri.MODUL
LAYAR = ['baru/js/layar/jual.js']
JAM_TETAP = "var __KINI = new Date('2026-09-20T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def baris(merk, n, harga, berat=50):
    return {'id': str(n), 'merk': merk, 'satuan': 'karung', 'beratKarung': berat, 'jumlahKarung': n, 'totalKg': n * berat, 'hargaPerKg': harga, 'subtotalHarga': n * berat * harga}


KOTAK = {
  'batchMasuk': [{'id': 1001, 'tanggal': '2026-09-01', 'jam': '09:00', 'pemasok': 'PEMASOK A', 'caraBayar': 'tunai', 'biayaBongkar': 0,
                  'merkList': [baris('IR64 Ascent', 10, 14000), baris('IR64 Elevate', 10, 14000), baris('Angsa', 10, 14600), baris('Beo', 10, 13000), baris('Cendana', 10, 13000)]}],   # Beo & Cendana: tanpa harga jual (tidak ikut tebakan), untuk penjaga tanggal mundur
  'katalogHargaKarung': [{'id': 'IR64 Ascent', 'merk': 'IR64 Ascent', 'hargaPerKg': 14000}, {'id': 'IR64 Elevate', 'merk': 'IR64 Elevate', 'hargaPerKg': 14000}, {'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 14600}],
  'katalogHargaLiteran': [{'id': 'IR64 Ascent', 'merk': 'IR64 Ascent', 'hargaPerLiter': 12500}, {'id': 'IR64 Elevate', 'merk': 'IR64 Elevate', 'hargaPerLiter': 12500}, {'id': 'Angsa', 'merk': 'Angsa', 'hargaPerLiter': 13000}],
  'katalogHargaKemasan': [{'id': 'Kembang|5', 'merk': 'Kembang', 'ukuran': 5, 'hargaPerUnit': 70000}],
  'produksiKemasan': [{'id': 2001, 'tanggal': '2026-09-02', 'jam': '09:00', 'merkSumber': 'Angsa', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 20, 'kgDipakai': 100, 'hppSumberPerKgDipakai': 14600, 'hppPerUnit': 73000, 'biayaKantong': 0, 'upah': 0, 'batchProduksi': 2001, 'barisKe': 1, 'jumlahBaris': 1}],
  'penyesuaianStok': [
    {'id': 3001, 'tanggal': '2026-09-15', 'jam': '09:00', 'merk': 'Angsa', 'kgSistem': 400, 'kgFisik': 395, 'selisihKg': -5, 'alasan': 'tumpah', 'nilaiRp': 73000, 'hppPerKgSaatOpname': 14600, 'bagian': 'tumpukan'},
    {'id': 3002, 'tanggal': '2026-09-15', 'jam': '10:00', 'merk': 'Angsa', 'kgSistem': 395, 'kgFisik': 395, 'selisihKg': 0, 'alasan': '', 'nilaiRp': 0, 'hppPerKgSaatOpname': 14600, 'bagian': 'tumpukan'},
    {'id': 3003, 'tanggal': '2026-09-20', 'jam': '08:00', 'merk': 'Beo', 'kgSistem': 500, 'kgFisik': 499, 'selisihKg': -1, 'alasan': 'susut wadah', 'nilaiRp': 13000, 'hppPerKgSaatOpname': 13000, 'bagian': 'wadah', 'wadah': 'IR64 Ascent'},
    {'id': 3004, 'tanggal': '2026-09-20', 'jam': '08:00', 'merk': 'Cendana', 'kgSistem': None, 'kgFisik': None, 'selisihKg': 41.5, 'alasan': 'Rework dari karantina', 'nilaiRp': 0, 'hppPerKgSaatOpname': 0, 'dariRework': True},
  ],
  'penyesuaianKemasan': [{'id': 3101, 'tanggal': '2026-09-18', 'jam': '11:00', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'unitSistem': 20, 'unitFisik': 20, 'selisihUnit': 0, 'alasan': '', 'nilaiRp': 0, 'hppPerUnitSaatOpname': 73000}],
  'aturanToko': [{'id': 'catatStok', 'minKarung': 0, 'tempoHari': 21, 'batasSelisih': 3, 'ambangSusutPositif': 250000, 'batasVarian': 5}],
  'penjualan': [], 'wadahLiteran': [], 'pengaturan': [], 'stokBahanKemasan': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var nId = 9000; var W = { tanggal: '2026-09-20', jam: '10:00', kini: '2026-09-20T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
// ================= 31.1 rinci karcis: nama seharga ditanyakan =================
var T = tebakanKarcis(700000); var G = T.filter(function (t) { return t.seharga; }); var g = G[0];
ok('nominal 700.000: Karung 50 kg IR64 Ascent dan IR64 Elevate seharga (14.000/kg) → SATU tebakan bertanda seharga dengan 2 pilihan (bukan dua tebakan / bukan yang pertama saja); label menyebut kedua nama & "harga sama, pilih namanya"; bentuk 25 kg × 2 = kelompok sendiri',
  G.length === 2 && G[1].pilihan.every(function (p) { return p.isi[0].berat === 25 && p.isi[0].jumlah === 2; }) && g.pilihan.length === 2 && g.tepat === true && !g.isi && J(g.pilihan.map(function (p) { return p.label; })) === J(['Karung 50 kg IR64 Ascent × 1', 'Karung 50 kg IR64 Elevate × 1']) && /harga sama, pilih namanya$/.test(g.label), J(T));
ok('tebakan yang namanya tunggal tetap tebakan biasa (tanpa seharga) — Angsa 730.000 ≠ 700.000 tidak ikut', !T.some(function (t) { return !t.seharga && t.isi && t.isi[0].kunci === 'Angsa'; }) && T.every(function (t) { return t.seharga || (t.isi && t.isi.length); }));
var TL = tebakanKarcis(25000); var gl = TL.find(function (t) { return t.seharga; });
ok('literan 25.000: 2 L IR64 Ascent / 2 L IR64 Elevate (12.500/L) seharga → satu tebakan bertanya; Angsa 13.000/L (2 L = 26.000 → bulat −1.000 > toleransi) tidak ikut', gl && gl.pilihan.length === 2 && gl.pilihan.every(function (p) { return p.isi[0].jalur === 'literan' && p.isi[0].jumlah === 2; }), J(TL));
var s0 = keadaanAwal(); s0.sekarang = new Date('2026-09-20T10:00:00');
var P1 = pakaiTebakan(s0, g);
ok('memakai tebakan seharga TIDAK mengisi keranjang: keadaan kcPilih = tebakan itu, kabar menyebut "2 nama seharga" dan kedua labelnya', !P1.keranjang && P1.kcPilih === g && /2 nama seharga/.test(P1.kabar) && /IR64 Ascent/.test(P1.kabar) && /IR64 Elevate/.test(P1.kabar) && P1.kabarAwas === false, J(P1));
var P2 = pakaiTebakan(s0, g.pilihan[1]);
ok('memilih nama kedua (IR64 Elevate) → keranjang berisi 1 karung 50 kg IR64 Elevate, kcPilih dihapus', P2.keranjang && P2.keranjang.length === 1 && P2.keranjang[0].trx.merkSumber === 'IR64 Elevate' && P2.keranjang[0].trx.jenis === 'karung' && P2.kcPilih === null, J(P2));
ok('kelompokkanTebakan: bentuk sama & nama beda digabung, bentuk beda dipisah, tepat vs bulat dipisah; satu tebakan tunggal dikembalikan apa adanya', (function () { var a = { tepat: true, label: 'A', isi: [{ jalur: 'karung', kunci: 'A', berat: 50, jumlah: 1 }] }; var b = { tepat: true, label: 'B', isi: [{ jalur: 'karung', kunci: 'B', berat: 50, jumlah: 1 }] }; var c = { tepat: true, label: 'C', isi: [{ jalur: 'karung', kunci: 'C', berat: 25, jumlah: 2 }] }; var d = { tepat: false, label: 'D', isi: [{ jalur: 'karung', kunci: 'D', berat: 50, jumlah: 1 }] };
  var k = kelompokkanTebakan([a, b, c, d]); return k.length === 3 && k[0].seharga === true && k[0].pilihan.length === 2 && k[1] === c && k[2] === d; })());
ok('lepas karcis menghapus kcPilih', lepasKarcis(Object.assign({}, s0, { karcis: { id: '1' } })).kcPilih === null);
// ================= 31.3 penjaga tanggal mundur =================
ok('cocokkan terakhir Angsa = 15 Sep 10:00 (dua hitungan sehari: jam terbesar); Beo tidak punya (cocokkan WADAH bukan hitungan tumpukan); Cendana tidak punya (rework bukan hitungan); Kembang 5 kg = 18 Sep', J(ckCocokTerakhir('Angsa')) === J({ tanggal: '2026-09-15', jam: '10:00' }) && ckCocokTerakhir('Beo') === null && ckCocokTerakhir('Cendana') === null && J(ckCocokTerakhirKemasan('Kembang', 5)) === J({ tanggal: '2026-09-18', jam: '11:00' }) && ckCocokTerakhirKemasan('Kembang', 10) === null);
var draf = function (tgl, merk) { return { id: null, tanggal: tgl, pemasok: 'PEMASOK A', caraBayar: 'tunai', bongkar: '', alasan: '', baris: [{ merk: merk, jumlahKarung: '4', beratKarung: 50, hargaPerKg: merk === 'Angsa' ? '14600' : '13000' }] }; };   // harga = modal → pertanyaan varian tidak ikut campur
var R1 = susunSimpanMasuk(draf('2026-09-10', 'Angsa'), W, false);
ok('barang masuk Angsa bertanggal 10 Sep (sebelum cocokkan 15 Sep 10:00) → DITOLAK dua ketukan; kalimat menyebut tanggal datang, nama, tanggal & jam cocokkan terakhir, "terpotong dua kali", saran catat hari ini', R1.perluYakin === true && /^Tanggal datang 2026-09-10 lebih AWAL dari cocokkan terakhir Angsa \(2026-09-15 10:00\)/.test(R1.tolak) && /terpotong dua kali/.test(R1.tolak) && /catat bertanggal hari ini/.test(R1.tolak), J(R1));
ok('ketukan kedua (yakin) → tersimpan; tanggal 16 Sep (sesudah cocokkan) tidak ditanya; tanggal = hari cocokkan (15 Sep) tidak ditanya (bukan lebih awal)', !susunSimpanMasuk(draf('2026-09-10', 'Angsa'), W, true).tolak && !susunSimpanMasuk(draf('2026-09-16', 'Angsa'), W, false).tolak && !susunSimpanMasuk(draf('2026-09-15', 'Angsa'), W, false).tolak, J(susunSimpanMasuk(draf('2026-09-16', 'Angsa'), W, false).tolak));
ok('Beo (hanya cocokkan wadah) & Cendana (hanya rework) bertanggal 10 Sep → tidak ditanya', !susunSimpanMasuk(draf('2026-09-10', 'Beo'), W, false).tolak && !susunSimpanMasuk(draf('2026-09-10', 'Cendana'), W, false).tolak, J([susunSimpanMasuk(draf('2026-09-10', 'Beo'), W, false).tolak, susunSimpanMasuk(draf('2026-09-10', 'Cendana'), W, false).tolak]));
ok('koreksi kedatangan lama (1 Sep, sebelum cocokkan) TIDAK ditanya — tanggalnya sudah tercatat', (function () { var d = drafDariKedatangan(1001); d.baris[2].hargaPerKg = '14700'; d.alasan = 'salah ketik'; return !susunSimpanMasuk(d, W, false).tolak; })());
var dA = function (tgl) { return { tanggal: tgl, bahan: [{ merk: 'Angsa', kg: '50' }], bahanKemasan: [], hasil: [{ nama: 'Kembang', ukuran: '5', unit: '10', kantongJenis: '', kantongJumlah: '' }], upah: '' }; };
var A1 = susunSimpanAdukan(dA('2026-09-10'), W, {});
ok('adukan 10 Sep: bahan Angsa (cocok 15 Sep) & hasil Kembang 5 kg (cocok 18 Sep) → ditolak dua ketukan perluYakin "mundur", kalimat menyebut keduanya dengan tanggalnya', A1.perluYakin === 'mundur' && /Tanggal adukan 2026-09-10 lebih AWAL dari cocokkan terakhir Angsa \(2026-09-15 10:00\), Kembang 5 kg \(2026-09-18 11:00\)/.test(A1.tolak), J(A1));
ok('adukan: {mundur: true} → tersimpan (2 dokumen produksi + tanpa kantong); adukan 19 Sep → tidak ditanya', !susunSimpanAdukan(dA('2026-09-10'), W, { mundur: true }).tolak && !susunSimpanAdukan(dA('2026-09-19'), W, {}).tolak, J(susunSimpanAdukan(dA('2026-09-10'), W, { mundur: true }).tolak));
ok('urutan penjaga adukan: bahan kurang ditanya dulu, baru tanggal mundur', (function () { var d = dA('2026-09-10'); d.bahan[0].kg = '900'; var r = susunSimpanAdukan(d, W, {}); return r.perluYakin === 'bahan' && susunSimpanAdukan(d, W, { bahan: true, susut: true }).perluYakin === 'mundur'; })());
print(J({ lulus: lulus, gagal: gagal }));
"""


def baca(ganti=None):
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(MODUL + LAYAR)))
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def bundel_dari(t):
    js = '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL]); tanda = '// ===== baru/js/layar/stok-hpp-logika.js ====='
    i = js.index(tanda); j = js.find('// ===== ', i + len(tanda)); j = len(js) if j < 0 else j
    return js[:i] + js[i:j].replace('teksMargin', 'teksMarginHpp') + js[j:]


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def periksa_statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    jl = t['baru/js/layar/jual.js']
    ok('Jual: ketukan tebakan seharga membuka pilihan nama (data-j) dan memakai KC.pakaiTebakan — bukan memilih yang pertama', "if (j !== undefined && T.seharga) T = T.pilihan[Number(j)];" in jl and 'data-k="kc-pilih"' in jl and 'data-j="${j}"' in jl and 'Harga sama — yang mana?' in jl)
    ok('jual-logika: keadaan kcPilih ada di keadaan awal (dilupakan bersama keranjang)', 'kcPilih: null,' in t['baru/js/layar/jual-logika.js'])
    ok('penjaga tanggal mundur satu sumber (jual-logika ckCocokTerakhir / ckKalimatMundur), dipakai barang masuk & adukan', 'export function ckKalimatMundur' in t['baru/js/layar/jual-logika.js'] and "ckKalimatMundur(draf.tanggal, h.sah.map" in t['baru/js/layar/stok-catat-logika.js'] and "perluYakin: 'mundur'" in t['baru/js/layar/stok-adukan-logika.js'])
    return out


def semua(ganti=None, bagian=('statis', 'jsc')):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        h, e = jalan(JAM_TETAP + bundel_dari(t) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
        if h is None: out.append(('jsc · JATUH: ' + e, False, ''))
        else: out += [('jsc · ' + x, False, '') for x in h['gagal']] + [('__jsc', not h['gagal'], h['lulus'])]
    return out


KC_ = 'baru/js/layar/karcis-logika.js'; JL_ = 'baru/js/layar/jual-logika.js'; SC_ = 'baru/js/layar/stok-catat-logika.js'; SA_ = 'baru/js/layar/stok-adukan-logika.js'
KONTROL = [
    ('tebakan lama: nama seharga dipilih diam-diam (tanpa kelompok)', {KC_: [("  return kelompokkanTebakan(hasil).slice(0, 6).concat(kelompokkanTebakan(kombo));", "  return hasil.slice(0, 6).concat(kombo);")]}, ('jsc',)),
    ('pakaiTebakan mengabaikan tanda seharga', {KC_: [("  if (t && t.seharga) return { kcPilih: t,", "  if (false) return { kcPilih: t,")]}, ('jsc',)),
    ('kelompok hanya membandingkan jalur (berat & jumlah diabaikan)', {KC_: [("const kcBentuk = (t) => t.isi.map((x) => x.jalur + '|' + (x.berat || '') + '|' + x.jumlah + '|' + (x.hargaPas || '')).join('+') + '|' + (t.tepat ? 1 : 0);", "const kcBentuk = (t) => t.isi.map((x) => x.jalur).join('+');")]}, ('jsc',)),
    ('Jual: ketukan pilihan nama diabaikan', {'baru/js/layar/jual.js': [("if (j !== undefined && T.seharga) T = T.pilihan[Number(j)];", "")]}, ('statis',)),
    ('barang masuk: penjaga tanggal mundur dibuang', {SC_: [("  if (mundur && !yakin) return { tolak: mundur, perluYakin: true };", "  if (false) return { tolak: mundur, perluYakin: true };")]}, ('jsc',)),
    ('barang masuk: penjaga MEMBLOKIR (ketukan kedua tidak diterima)', {SC_: [("  if (mundur && !yakin) return { tolak: mundur, perluYakin: true };", "  if (mundur) return { tolak: mundur, perluYakin: true };")]}, ('jsc',)),
    ('barang masuk: koreksi kedatangan lama ikut ditanya', {SC_: [("  const mundur = lama ? '' : ckKalimatMundur(", "  const mundur = ckKalimatMundur(")]}, ('jsc',)),
    ('cocokkan WADAH dihitung sebagai hitungan tumpukan', {JL_: [("if (!hitunganFisik(p) || p.bagian === 'wadah' || String(p.merk) !== String(merk) || !p.tanggal) return;", "if (!hitunganFisik(p) || String(p.merk) !== String(merk) || !p.tanggal) return;")]}, ('jsc',)),
    ('rework dihitung sebagai hitungan fisik', {JL_: [("if (!hitunganFisik(p) || p.bagian === 'wadah' || String(p.merk) !== String(merk) || !p.tanggal) return;", "if (p.bagian === 'wadah' || String(p.merk) !== String(merk) || !p.tanggal) return;")]}, ('jsc',)),
    ('kalimat tanpa tanggal cocokkan terakhir', {JL_: [("m.map((x) => x.nama + ' (' + x.cocok.tanggal + (x.cocok.jam ? ' ' + x.cocok.jam : '') + ')').join(', ')", "m.map((x) => x.nama).join(', ')")]}, ('jsc',)),
    ('adukan: penjaga tanggal mundur dibuang', {SA_: [("  if (mundur && !Y.mundur) return { tolak: mundur, perluYakin: 'mundur' };", "  if (false) return { tolak: mundur, perluYakin: 'mundur' };")]}, ('jsc',)),
    ('adukan: hasil kemasan tidak diperiksa', {SA_: [(".concat(h.sahH.map((x) => ({ nama: x.nama + ' ' + x.ukuran + ' kg', cocok: ckCocokTerakhirKemasan(x.nama, x.ukuran) })))", "")]}, ('jsc',)),
    ('tanggal SAMA dengan hari cocokkan ikut ditanya (lebih awal → tidak lebih akhir)', {JL_: [("const m = (daftar || []).filter((x) => x.cocok && String(x.cocok.tanggal) > String(tanggal));", "const m = (daftar || []).filter((x) => x.cocok && String(x.cocok.tanggal) >= String(tanggal));")]}, ('jsc',)),
]

if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti, bagian in KONTROL:
            try: h = semua(ganti, bagian)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' · ' + str(e)[:140]); kode = 3; continue
            g = [x for x in h if not x[1]]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h = semua(); g = [x for x in h if not x[1]]
    n = sum(1 for x in h if x[1] and x[0] != '__jsc') + next((x[2] for x in h if x[0] == '__jsc'), 0)
    for x in g: print('   ✗ ' + x[0] + (' → ' + json.dumps(x[2], ensure_ascii=False)[:400] if x[2] not in ('', None) else ''))
    print('PEMANTAPAN 31 (31.1 karcis seharga · 31.3 tanggal mundur): %d lulus · %d gagal' % (n, len(g)))
    sys.exit(1 if g else 0)
