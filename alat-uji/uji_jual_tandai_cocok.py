#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_jual_tandai_cocok.py — putaran 31b: "JUAL DULU, TANDAI UNTUK DICOCOKKAN" (keputusan owner 28 Sep 2026, docs/peta-jual-tandai-cocok.md §6).
  · Pemeriksaan ulang stok saat mencatat TIDAK berubah: nota yang melampaui buku tetap ditahan; akun staf selalu ditahan.
  · OWNER mendapat pilihan kedua (dua ketukan) dengan kalimat yang menyebut nama & kg yang melampaui; ketukan kedua mencatat nota apa adanya, baris
    yang melampaui diberi `perluCocokkan: true` + `selisihKg`; buku dibiarkan minus. Tanpa dokumen baru.
  · Tanda tuntas = Cocokkan nama itu bertanggal ≥ tanggal nota (cocokkan biasa). Pita di Jual + item di Stok › Gudang kartu keempat.
KOTAK PASIR (angka contoh), jam dikunci 19 Sep 2026 10:00 WIB.

    python3 alat-uji/uji_jual_tandai_cocok.py            → N lulus · 0 gagal
    python3 alat-uji/uji_jual_tandai_cocok.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_stok_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_stok_baru.MODUL
LAYAR = ['baru/js/layar/jual.js', 'baru/js/layar/stok.js', 'baru/js/mesin/pembantu.js']
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"

KOTAK = {
  'batchMasuk': [{'id': 1001, 'tanggal': '2026-09-01', 'jam': '09:00', 'pemasok': 'PEMASOK A', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [
      {'id': '1', 'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 2, 'totalKg': 100, 'hargaPerKg': 14000, 'subtotalHarga': 1400000},
      {'id': '2', 'merk': 'Beo', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 4, 'totalKg': 200, 'hargaPerKg': 13000, 'subtotalHarga': 2600000}]}],
  'katalogHargaKarung': [{'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 15000}, {'id': 'Beo', 'merk': 'Beo', 'hargaPerKg': 14000}],
  'katalogHargaKemasan': [{'id': 'Kembang|5', 'merk': 'Kembang', 'ukuran': 5, 'hargaPerUnit': 70000}],
  'produksiKemasan': [{'id': 2001, 'tanggal': '2026-09-02', 'jam': '09:00', 'merkSumber': 'Beo', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 2, 'kgDipakai': 10, 'hppSumberPerKgDipakai': 13000, 'hppPerUnit': 65000, 'biayaKantong': 0, 'upah': 0, 'batchProduksi': 2001, 'barisKe': 1, 'jumlahBaris': 1}],
  'penjualan': [], 'penyesuaianStok': [], 'penyesuaianKemasan': [], 'wadahLiteran': [], 'pengaturan': [], 'aturanToko': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
var KOL = Object.keys(KOTAK); var pulih = function () { KOL.forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n] || []))); }); }; pulih();
var nId = 9000; var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var s; var terap = function (p) { s = Object.assign({}, s, p); sinkronKeranjang(s); };
var mulai = function () { s = keadaanAwal(); s.sekarang = new Date('2026-09-19T10:00:00'); sinkronKeranjang(s); };
var chip = function (jalur, kunci, berat) { return susunRak(s)[jalur].find(function (c) { return c.kunci === kunci && (!berat || c.berat === berat); }); };
var jualLain = function (id, merk, kg) { return { koleksi: 'penjualan', data: { id: id, tanggal: '2026-09-19', jam: '09:30', caraBayar: 'Tunai', namaPelanggan: '', jenis: 'karung', merkSumber: merk, beratKarungAcuan: 50, jumlahKarung: kg / 50, totalKg: kg, hargaTotal: kg * 15000, hppTotalSaatJual: kg * 14000 } }; };
// ---- 1 · keranjang 2 karung Angsa (buku 100 kg = pas), lalu 1 karung terjual di perangkat lain → buku 50 kg, keranjang melampaui 50 kg
mulai(); terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '2' }); terap(masukkan(s)); terap(uangPas(s));
ok('stok cukup: barisTembus kosong, periksaStokKeranjang diam, nota sah tanpa tanda', barisTembus(s).length === 0 && periksaStokKeranjang(s) === '' && !simpanNota(s, W).tolak && !simpanNota(s, W).dokumen[0].data.perluCocokkan);
terapkanKeCache([jualLain('sX', 'Angsa', 50)]);
var T1 = barisTembus(s);
ok('sesudah 1 karung terjual di tempat lain: barisTembus = 1 baris Angsa karung, bebas 1, butuh 2, selisih 1 karung = 50 kg; teksnya = kalimat periksaStokKeranjang (pemeriksaan ulang tidak berubah)', T1.length === 1 && T1[0].nama === 'Angsa' && T1[0].jalur === 'karung' && T1[0].maks === 1 && T1[0].butuh === 2 && T1[0].selisih === 1 && T1[0].selisihKg === 50 && T1[0].teks === periksaStokKeranjang(s) && /bebas dijual tinggal 1 karung/.test(T1[0].teks), J(T1));
var Rs = simpanNota(s, W);
ok('STAF (tembusBoleh tidak ada): DITAHAN dengan kalimat yang sama seperti sebelumnya, tanpa perluTembus', /bebas dijual tinggal 1 karung/.test(Rs.tolak || '') && !/jual dulu/.test(Rs.tolak) && !Rs.perluTembus, J(Rs));
var Rs2 = simpanNota(Object.assign({}, s, { tembusBoleh: false, tembusYakin: true }), W);
ok('staf dengan tembusYakin (mis. keadaan basi) tetap DITAHAN', !!Rs2.tolak && !Rs2.dokumen);
var R1 = simpanNota(Object.assign({}, s, { tembusBoleh: true }), W);
ok('OWNER ketukan pertama: DITAHAN + kalimat menyebut "Buku Angsa kurang 50 kg" dan "jual dulu, tandai untuk dicocokkan? Buku dibiarkan minus"; perluTembus = daftar barisnya', /bebas dijual tinggal 1 karung/.test(R1.tolak || '') && /Buku Angsa kurang 50 kg — jual dulu, tandai untuk dicocokkan\? Buku dibiarkan minus sampai dicocokkan/.test(R1.tolak) && R1.perluTembus && R1.perluTembus.length === 1 && R1.perluTembus[0].nama === 'Angsa' && !R1.dokumen, J(R1));
var R2 = simpanNota(Object.assign({}, s, { tembusBoleh: true, tembusYakin: true }), W); var pj2 = R2.dokumen ? R2.dokumen.filter(function (d) { return d.koleksi === 'penjualan'; }) : [];
ok('OWNER ketukan kedua: nota TERCATAT apa adanya — 1 baris penjualan Angsa 2 karung 100 kg dengan perluCocokkan true + selisihKg 50; kolom lain persis nota biasa; kabar menyebut TEMBUS STOK; patch mengosongkan tembusTanya', !R2.tolak && pj2.length === 1 && pj2[0].data.perluCocokkan === true && pj2[0].data.selisihKg === 50 && pj2[0].data.totalKg === 100 && pj2[0].data.merkSumber === 'Angsa' && pj2[0].data.hppTotalSaatJual > 0 && /TEMBUS STOK, tandai dicocokkan: Angsa 50 kg/.test(R2.patch.kabar) && R2.patch.tembusTanya === null && R2.patch.tembusYakin === false && R2.tembus.length === 1, J(R2));
ok('baris yang tidak melampaui TIDAK diberi tanda (kolom perluCocokkan/selisihKg tidak ada, bukan false)', (function () { pulih(); mulai(); terap(ketukChip(s, chip('karung', 'Beo', 50))); terap({ ketik: '1' }); terap(masukkan(s)); terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '2' }); terap(masukkan(s)); terap(uangPas(s)); terapkanKeCache([jualLain('sX', 'Angsa', 50)]);
  var r = simpanNota(Object.assign({}, s, { tembusBoleh: true, tembusYakin: true }), W); var beo = r.dokumen.find(function (d) { return d.koleksi === 'penjualan' && d.data.merkSumber === 'Beo'; }); var angsa = r.dokumen.find(function (d) { return d.koleksi === 'penjualan' && d.data.merkSumber === 'Angsa'; });
  return !r.tolak && beo && !('perluCocokkan' in beo.data) && !('selisihKg' in beo.data) && angsa.data.perluCocokkan === true; })());
pulih(); mulai(); terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '2' }); terap(masukkan(s)); terap(uangPas(s)); terapkanKeCache([jualLain('sX', 'Angsa', 50)]);
var R2b = simpanNota(Object.assign({}, s, { tembusBoleh: true, tembusYakin: true }), W); terapkanKeCache(R2b.dokumen);
var bukuAngsa = hitungStokKarungPerMerk().Angsa;
ok('sesudah tercatat: buku Angsa MINUS 50 kg (100 − 50 lain − 100 nota), modal rata-rata tidak berubah; laba membaca hppTotalSaatJual seperti nota biasa', bukuAngsa.sisaKg === -50 && Math.abs(bukuAngsa.hppTerakhirPerKg - 14000) < 1e-9, J(bukuAngsa));
// ---- 2 · pita & kartu keempat: belum tuntas → tuntas sesudah cocokkan bertanggal ≥ nota
var TB = notaTembusBelumCocok();
ok('belum dicocokkan: 1 nota, ringkas "Angsa 50 kg", baris membawa trxId/tanggal/jam/selisihKg', TB.n === 1 && TB.ringkas === 'Angsa 50 kg' && TB.baris.length === 1 && TB.baris[0].tanggal === '2026-09-19' && TB.baris[0].selisihKg === 50 && TB.nama[0].kg === 50 && TB.nama[0].n === 1, J(TB));
var G = susunGudang('cocok', new Date('2026-09-19T10:00:00'));
ok('Stok › Gudang kartu keempat: baris paling atas "Angsa · 50 kg tembus · belum dicocokkan" (awas), ikut hitungan kartu; kuncinya tembus|Angsa', G.jawab.baris[0].kunci === 'tembus|Angsa' && G.jawab.baris[0].n === '50 kg tembus' && G.jawab.baris[0].nKet === 'belum dicocokkan' && G.jawab.baris[0].awas === true && /1 nota dijual melampaui buku/.test(G.jawab.baris[0].ket) && G.kartu.find(function (k) { return k.id === 'cocok'; }).awas === true, J(G.jawab.baris.slice(0, 2)));
var cocokSebelum = { koleksi: 'penyesuaianStok', data: { id: 7001, tanggal: '2026-09-18', jam: '20:00', merk: 'Angsa', kgSistem: 100, kgFisik: 100, selisihKg: 0, alasan: '', nilaiRp: 0, hppPerKgSaatOpname: 14000, bagian: 'tumpukan' } };
var cocokSesudah = { koleksi: 'penyesuaianStok', data: { id: 7002, tanggal: '2026-09-19', jam: '15:00', merk: 'Angsa', kgSistem: -50, kgFisik: 0, selisihKg: 50, alasan: 'karung yang belum tercatat masuk', nilaiRp: 0, hppPerKgSaatOpname: 14000, bagian: 'tumpukan' } };
var rework = { koleksi: 'penyesuaianStok', data: { id: 7003, tanggal: '2026-09-20', jam: '15:00', merk: 'Angsa', kgSistem: null, kgFisik: null, selisihKg: 5, alasan: 'Rework', nilaiRp: 0, hppPerKgSaatOpname: 0, dariRework: true } };
var beoCocok = { koleksi: 'penyesuaianStok', data: { id: 7004, tanggal: '2026-09-20', jam: '15:00', merk: 'Beo', kgSistem: 200, kgFisik: 200, selisihKg: 0, alasan: '', nilaiRp: 0, hppPerKgSaatOpname: 13000, bagian: 'tumpukan' } };
ok('cocokkan SEBELUM tanggal nota (18 Sep), rework, atau nama lain → tanda tetap; cocokkan Angsa bertanggal ≥ nota (19 Sep, tanpa tombol khusus) → tuntas: pita & kartu kosong', denganCacheSementara([cocokSebelum, rework, beoCocok], function () { return notaTembusBelumCocok().n === 1; }) && denganCacheSementara([cocokSesudah], function () { return notaTembusBelumCocok().n === 0 && !susunGudang('cocok', new Date('2026-09-19T10:00:00')).jawab.baris.some(function (b) { return /^tembus\|/.test(b.kunci); }); }));
ok('nota bertanda yang dibatalkan hilang dari daftar (tanda ikut notanya)', (function () { var id = R2b.dokumen.find(function (d) { return d.koleksi === 'penjualan'; }).data.id; return denganCacheSementara([{ koleksi: 'penjualan', data: Object.assign({}, R2b.dokumen.find(function (d) { return d.koleksi === 'penjualan'; }).data, { dibatalkan: true }) }], function () { return notaTembusBelumCocok().n === 0; }); })());
// ---- 2b · 39b no. 14 (J3): dua baris satu buku — kekurangan dibagi sekali, bukan ditagih penuh di tiap baris
pulih(); mulai(); terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '1' }); terap(masukkan(s)); terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '1' }); terap(masukkan(s)); terap(uangPas(s));
terapkanKeCache([jualLain('sJ3', 'Angsa', 50)]);
var R14 = simpanNota(Object.assign({}, s, { tembusBoleh: true, tembusYakin: true }), W); var pj14 = R14.dokumen ? R14.dokumen.filter(function (d) { return d.koleksi === 'penjualan' && d.data.merkSumber === 'Angsa'; }) : [];
ok('39b-14 J3 dua baris Angsa 1 karung (buku sisa 50 kg, keranjang 100 kg): tanda kekurangan total 50 kg SEKALI — baris pertama tanpa tanda, baris kedua 50 kg (dulu 50 + 50 = 100); kabar menyebut 50 kg',
  s.keranjang.length === 2 && !R14.tolak && pj14.length === 2 && pj14.reduce(function (a, d) { return a + (d.data.selisihKg || 0); }, 0) === 50 && pj14.filter(function (d) { return d.data.perluCocokkan; }).length === 1 && /Angsa 50 kg/.test(R14.patch.kabar) && !/Angsa 50 kg, Angsa/.test(R14.patch.kabar),
  J([s.keranjang.length, R14.tolak, pj14.map(function (d) { return [d.data.perluCocokkan, d.data.selisihKg]; }), R14.patch && R14.patch.kabar]));
ok('39b-14 J3 ketukan pertama tetap memakai kalimat pemeriksaan ulang yang sama (baris pertama), dan menyebut kekurangan 50 kg sekali',
  (function () { var r = simpanNota(Object.assign({}, s, { tembusBoleh: true }), W); return !!r.tolak && r.tolak.indexOf(periksaStokKeranjang(s)) === 0 && /Buku Angsa kurang 50 kg — jual dulu/.test(r.tolak) && !/Angsa kurang 50 kg, Angsa/.test(r.tolak)
    && r.perluTembus.length === 1 && r.perluTembus[0].selisihKg === 50; })(),
  J(simpanNota(Object.assign({}, s, { tembusBoleh: true }), W).tolak));
// ---- 3 · kemasan: unit × ukuran = kg
pulih(); mulai(); terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '2' }); terap(masukkan(s)); terap(uangPas(s));
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'sK', tanggal: '2026-09-19', jam: '09:30', caraBayar: 'Tunai', namaPelanggan: '', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, hargaTotal: 70000, hppTotalSaatJual: 65000 } }]);
var RK = simpanNota(Object.assign({}, s, { tembusBoleh: true, tembusYakin: true }), W); var pk = RK.dokumen ? RK.dokumen.find(function (d) { return d.koleksi === 'penjualan'; }) : null;
ok('kemasan Kembang 5 kg: 2 unit di keranjang, bebas 1 → selisihKg 5 (1 unit × 5 kg); nama di kalimat "Kembang 5 kg"; tuntas lewat penyesuaianKemasan bertanggal ≥ nota', !RK.tolak && pk.data.perluCocokkan === true && pk.data.selisihKg === 5 && RK.tembus[0].nama === 'Kembang 5 kg' && (terapkanKeCache(RK.dokumen), notaTembusBelumCocok().ringkas === 'Kembang 5 kg 5 kg') && denganCacheSementara([{ koleksi: 'penyesuaianKemasan', data: { id: 7101, tanggal: '2026-09-19', jam: '16:00', namaProduk: 'Kembang', ukuranKemasan: 5, unitSistem: -1, unitFisik: 0, selisihUnit: 1, alasan: 'ada', nilaiRp: 0, hppPerUnitSaatOpname: 65000 } }], function () { return notaTembusBelumCocok().n === 0; }), J([RK.tolak, pk && pk.data, RK.tembus]));
// ---- 4 · alasan lain tetap menang lebih dulu; karcis rinci tidak ikut jalur tembus
pulih(); mulai();
ok('keranjang kosong ditolak lebih dulu (alasanTolak), bukan jalur tembus', /Keranjang kosong/.test(simpanNota(Object.assign({}, s, { tembusBoleh: true, tembusYakin: true }), W).tolak || ''));
print(J({ lulus: lulus, gagal: gagal }));
"""


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
    jl = t['baru/js/layar/jual.js']; pb = t['baru/js/mesin/pembantu.js']
    ok('Jual: tembusBoleh hanya owner (bukanOwner), ketukan pertama menyimpan perluTembus, tombol "JUAL DULU, TANDAI" memanggil catatNota(true)', "tembusBoleh: !bukanOwner(opsi.akun ? opsi.akun() : null)" in jl and "tembusTanya: r.perluTembus || null" in jl and 'data-aksi="simpanTembus"' in jl and "simpanTembus: async () => aksi.catatNota(true)" in jl and "tembusYakin: tembusYakin === true" in jl)
    ok('Jual: pita "N nota tembus stok belum dicocokkan" dari notaTembusBelumCocok (pola pita karcis)', 'data-k="pita-tembus-belum"' in jl and 'const TB = L.notaTembusBelumCocok();' in jl and 'nota tembus stok belum dicocokkan' in jl)
    ok('katalog HP kasir (susunIsiKatalogKasir, verbatim index.html) tidak membaca perluCocokkan — kasir tetap menahan', 'perluCocokkan' not in pb)
    ok('stok-logika: kartu keempat menaruh baris tembus dari notaTembusBelumCocok', "const TB = notaTembusBelumCocok();" in t['baru/js/layar/stok-logika.js'] and "kunci: 'tembus|' + x.nama" in t['baru/js/layar/stok-logika.js'])
    return out


def semua(ganti=None, bagian=('statis', 'jsc')):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        js = '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL])
        h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
        if h is None: out.append(('jsc · JATUH: ' + e, False, ''))
        else: out += [('jsc · ' + x, False, '') for x in h['gagal']] + [('__jsc', not h['gagal'], h['lulus'])]
    return out


JL_ = 'baru/js/layar/jual-logika.js'; SL_ = 'baru/js/layar/stok-logika.js'; JU_ = 'baru/js/layar/jual.js'
KONTROL = [
    ('39b-14 J3: kekurangan satu buku ditagih di tiap baris lagi', {JL_: [("const sel = Math.max(0, Math.round((butuh - (maksUrut === null ? maks : maksUrut)) * 100) / 100);", "const sel = Math.max(0, Math.round((butuh - maks) * 100) / 100);")]}, ('jsc',)),
    ('39b-14 J3: baris tanpa kekurangan tetap ditandai', {JL_: [("tembus.forEach((t) => { if (t.selisihKg > 0.004) ids[t.id] = t; });", "tembus.forEach((t) => { ids[t.id] = t; });")]}, ('jsc',)),
    ('staf ikut boleh menembus', {JL_: [("    tembus = s.tembusBoleh ? barisTembus(s) : [];", "    tembus = barisTembus(s);")]}, ('jsc',)),
    ('tanpa ketukan kedua (owner langsung tembus)', {JL_: [("    if (!s.tembusYakin) return { tolak: stok +", "    if (false) return { tolak: stok +")]}, ('jsc',)),
    ('pemeriksaan ulang dilemahkan (nota lolos tanpa tanda)', {JL_: [("  const stok = periksaStokKeranjang(s); let tembus = [];   // pemeriksaan ulang TIDAK berubah (31b)", "  const stok = ''; let tembus = [];")]}, ('jsc',)),
    ('baris tidak ditandai perluCocokkan', {JL_: [("Object.assign({}, b.trx, { perluCocokkan: true, selisihKg: ids[b.id].selisihKg })", "Object.assign({}, b.trx)")]}, ('jsc',)),
    ('selisihKg = satuan chip, bukan kg', {JL_: [(": Math.round(kgTembus(b.trx, chip, sel) * 100) / 100,", ": sel,")]}, ('jsc',)),
    ('kalimat tanpa nama & kg', {JL_: [("'. Buku ' + tembus.filter((t) => t.selisihKg > 0.004).map((t) => t.nama + ' kurang ' + kgTeks(t.selisihKg)).join(', ') + ' — jual dulu", "'. Buku kurang — jual dulu")]}, ('jsc',)),
    ('tanda tuntas oleh cocokkan SEBELUM tanggal nota', {JL_: [("&& String(q.tanggal || '') >= tgl);\n    if (!tuntas)", "&& true);\n    if (!tuntas)")]}, ('jsc',)),
    ('rework dianggap cocokkan', {JL_: [("const PS = ambilPenyesuaianStok().filter((q) => !q.dariRework);", "const PS = ambilPenyesuaianStok();")]}, ('jsc',)),
    ('kartu keempat tanpa baris tembus', {SL_: [("  return { baris: tembus.concat(out),", "  return { baris: out,")]}, ('jsc',)),
    ('Jual: staf juga dapat tombol tembus', {JU_: [("tembusBoleh: !bukanOwner(opsi.akun ? opsi.akun() : null)", "tembusBoleh: true")]}, ('statis',)),
    ('Jual: pita belum dicocokkan hilang', {JU_: [("const TB = L.notaTembusBelumCocok();", "const TB = { n: 0, ringkas: '' };")]}, ('statis',)),
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
    print('JUAL DULU, TANDAI UNTUK DICOCOKKAN (31b): %d lulus · %d gagal' % (n, len(g)))
    sys.exit(1 if g else 0)
