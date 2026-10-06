#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_catat_nota_cepat.py — owner 7 Okt 2026 (J3 "simpan nota lebih cepat"): pemeriksaan ulang stok saat CATAT NOTA dulu menyusun SELURUH rak (sisa tiap chip,
Sering, tinggi wadah) hanya untuk mencari chip baris keranjang — data berubah sesudah tiap nota (penjualan + jejak), jadi tiap nota membayar ±80 ms di jsc (±0,2 dtk di
Mac). Kini rak IDENTITAS (jual-logika susunRak(s, { identitas: true })): chip, nama, harga, modal, urutan & isian berat karung SAMA, tanpa sisa/Sering.
  · PEMBANDING CHIP: tiap chip rak identitas = chip rak penuh tanpa kolom sisa (sisa, sisaTeks, dipegang, wadah) — urutan & kunci sama; rak Wadah & isian
    #jualKarungBerat sama.
  · PEMBANDING NOTA (data yang ditulis): skenario yang sama dijalankan di bundel BARU dan bundel LAMA (rakUntukChip menyusun rak penuh seperti main) — hasil
    simpanNota (dokumen, urutan, id, angka, tolak, perluTembus), pemeriksaan ulang stok, baris tembus, ubah jumlah, bonus, nego: byte-sama. Keranjang: karung, kemasan
    + bonus + nego, literan wadah campuran, literan langsung, repack + kantong ditanggung, wadah, ½ karung, bon + buka kredit, bayar sebagian, tembus stok owner.
  · ONGKOS (hitungan panggilan, pasti): simpanNota sesudah data berubah memanggil buku stok mesin (hitungStokKarungPerMerk) jauh lebih sedikit dari cara lama.
  · Cadangan toko di _privat/ (lokal saja; dilewati di CI): pembanding nota & ms simpanNota lama vs baru di data toko.

    python3 alat-uji/uji_catat_nota_cepat.py            → N lulus · 0 gagal
    python3 alat-uji/uji_catat_nota_cepat.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import uji_wadah_bernama, uji_cache_chip_literan, uji_rak_inkremental  # noqa: E402

BARU = "_rakChip = susunRak({ pelanggan: '', sekarang: null }, { identitas: true });"
LAMA = "_rakChip = susunRak({ pelanggan: '', sekarang: null });"
UKUR = r"""
var __n = { stok: 0, maks: 0 };
hitungStokKarungPerMerk = (function (f) { return function () { __n.stok++; return f.apply(this, arguments); }; })(hitungStokKarungPerMerk);
stokMaksJalur = (function (f) { return function () { __n.maks++; return f.apply(this, arguments); }; })(stokMaksJalur);
"""

# skenario nota: dijalankan sama persis di bundel baru & lama → keluaran dibandingkan python
NOTA = uji_rak_inkremental.BANTU + r"""
var out = {}; var nW = 0; var Wd = function () { return { tanggal: '2026-09-21', jam: '10:00', kini: '2026-09-21T03:00:00.000Z', idUnik: function () { nW += 1; return 100000 + nW; } }; };
var s = Object.assign(keadaanAwal(), { sekarang: new Date(Date.now()), tembusBoleh: true });
var terap = function (p) { s = Object.assign({}, s, p || {}); sinkronKeranjang(s); return p; };
var rak = function () { sinkronKeranjang(s); return susunRak(s); };
var pilih = function (jalur, f) { return rak()[jalur].filter(f)[0]; };
var masuk = function (c, n, isi) { if (!c) { out['tanpa-chip-' + Object.keys(out).length] = 1; return; } var r = masukkan(Object.assign({}, s, { pilih: c }, isi || {}), n); if (r.keranjang) terap({ keranjang: r.keranjang, urutBaris: r.urutBaris, kabar: r.kabar }); else out['tolak-' + Object.keys(out).length] = r.kabar; };
var ubahData = function () { pasok('logAktivitas', cacheMentah('log').concat([{ id: 'log' + nW, pada: 'x' }])); };   // seperti jejak tiap nota: versi data naik
var catat = function (nama, ubah) { ubahData(); var r = simpanNota(Object.assign({}, s, ubah || {}), Wd()); out[nama] = J({ tolak: r.tolak || '', perluTembus: r.perluTembus || null, dokumen: r.dokumen || null, ringkas: r.ringkas || '' }); return r; };
var pegang = function (nama) { ubahData(); out[nama + '-periksa'] = periksaStokKeranjang(s); ubahData(); out[nama + '-tembus'] = J(barisTembus(s)); };
// A · campuran lengkap, tunai pas
masuk(pilih('karung', function (c) { return c.kunci === 'NG' && c.berat === 50; }), 2);
masuk(pilih('kemasan', function (c) { return c.kunci === 'Kembang|5'; }), 2);
masuk(pilih('literan', function (c) { return c.kunci === 'IR64 Apex'; }), 6);
masuk(pilih('literan', function (c) { return c.kunci === 'Tawon'; }), 3);
masuk(pilih('repack', function (c) { return c.kunci === 'NG'; }), 5, { rpWadah: '5kg_kembangbmw', rpLembar: '1', rpDijual: false, rpUpah: '2000' });
masuk(pilih('wadah', function (c) { return c.kunci === 'karungbekas'; }), 1);
var idK = s.keranjang[1].id; ubahData(); terap(toggleBonus(s, idK)); out.bonus = J(s.keranjang[1].trx);
ubahData(); terap(terapkanNego(s, idK, 70000)); out.nego = J(s.keranjang[1].trx);
ubahData(); terap(ubahJumlahBaris(s, s.keranjang[0].id, 0.5)); out.tambahSetengah = J(s.keranjang[0].trx);
ubahData(); var pJ = ubahJumlahBaris(s, s.keranjang[0].id, 99); out.tambahLewat = pJ.kabar || J(pJ);
pegang('A'); terap(uangPas(s)); var rA = catat('A');
terap(rA.patch || {}); terapkanKeCache(rA.dokumen || []);
// B · ½ karung Hemat + bon dengan buka kredit sekali + Angsa 25 kg
masuk(Object.assign({}, skChip(pilih('kemasan', function (c) { return c.kunci === 'Hemat|50'; }), '')), 1);
masuk(pilih('karung', function (c) { return c.kunci === 'Angsa' && c.berat === 25; }), 1);
terap({ pelanggan: 'Pembeli Contoh A', cara: 'Kredit', kreditDibuka: true }); pegang('B'); var rB = catat('B');
terap(rB.patch || {}); terapkanKeCache(rB.dokumen || []);
// C · bayar sebagian (uang kurang → sisa jadi bon)
masuk(pilih('karung', function (c) { return c.kunci === 'Kumala'; }), 1);
terap({ pelanggan: 'Pembeli Contoh B', cara: 'Tunai', uang: 100000 }); var rC = catat('C');
terap(rC.patch || {}); terapkanKeCache(rC.dokumen || []);
// D · tembus stok (owner): minta lebih dari buku → ditanya, lalu ketukan kedua
var cNG = pilih('karung', function (c) { return c.kunci === 'NG' && c.berat === 50; });
terap({ keranjang: [{ id: 'bz', trx: bangunBaris(cNG, (cNG ? cNG.sisa : 0) + 2, s) }], urutBaris: 99 }); terap(uangPas(s)); pegang('D');
var rD1 = catat('D1'); terap({ tembusTanya: rD1.perluTembus || null }); var rD2 = catat('D2', { tembusYakin: true });
print(J({ out: out }));
"""

# rak identitas = rak penuh tanpa kolom sisa (KOTAK & cadangan)
CHIP = r"""
var J = JSON.stringify; var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
var BUANG = { sisa: 1, sisaTeks: 1, dipegang: 1, wadah: 1 };
var bersih = function (c) { var o = {}; Object.keys(c).forEach(function (k) { if (!BUANG[k]) o[k] = c[k]; }); return o; };
var periksaRak = function (nama, s) {
  // isian berat karung diawali nilai yang tidak pernah ditulis rak (7) — jejak penulisan susun penuh & identitas harus sama
  sinkronKeranjang(s); __dom['jualKarungBerat'] = { value: '7' }; var P = susunRak(s); var dP = __dom['jualKarungBerat'].value;
  __dom['jualKarungBerat'] = { value: '7' }; var I = susunRak(s, { identitas: true }); var dI = __dom['jualKarungBerat'].value; __dom['jualKarungBerat'] = { value: '50' };
  var beda = []; ['karung', 'kemasan', 'literan', 'repack'].forEach(function (j) { var a = J(P[j].map(bersih)), b = J(I[j].map(bersih)); if (a !== b) beda.push(j + ': ' + a.slice(0, 200) + ' ≠ ' + b.slice(0, 200)); });
  if (J(P.wadah) !== J(I.wadah)) beda.push('wadah');
  ok(nama + ': rak IDENTITAS = rak penuh tanpa kolom sisa — ' + ['karung', 'kemasan', 'literan', 'repack', 'wadah'].map(function (j) { return P[j].length + ' ' + j; }).join(' · ') + '; isian berat karung sama (' + dP + ')', !beda.length && dP === dI && dP !== '7' && P.karung.length > 0, J(beda) + ' · ' + dP + '/' + dI);
  ok(nama + ': rak identitas TIDAK menghitung sisa, Sering, kelompok', I.karung.every(function (c) { return c.sisa === undefined; }) && I.sering === undefined && I.kelompok === undefined);
};
"""
CHIP_KOTAK = uji_rak_inkremental.BANTU.replace("var J = JSON.stringify;\nvar gagal = [], lulus = 0;\nfunction ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }\n", '') + r"""
var s0 = Object.assign(keadaanAwal(), { sekarang: new Date(Date.now()) }); periksaRak('kotak pasir, keranjang kosong', s0);
var r0 = susunRak((sinkronKeranjang(s0), s0)); var mx = masukkan(Object.assign({}, s0, { pilih: r0.karung[0] }), 1); var s1 = Object.assign({}, s0, { keranjang: mx.keranjang || [] });
var s2 = Object.assign({}, s1, parkir(s1)); var lt = r0.literan.filter(function (c) { return c.wadahLiteran; })[0]; var m2 = masukkan(Object.assign({}, s2, { pilih: lt }), 3);
periksaRak('kotak pasir, keranjang + struk parkir memegang barang', Object.assign({}, s2, { keranjang: m2.keranjang || [] }));
// ongkos: simpanNota sesudah data berubah — panggilan buku stok mesin
var s3 = Object.assign(keadaanAwal(), { sekarang: new Date(Date.now()) }); var rr = susunRak((sinkronKeranjang(s3), s3));
[['karung', 0, 1], ['kemasan', 0, 1], ['literan', 0, 2]].forEach(function (x) { var c = rr[x[0]][x[1]]; if (!c) return; var m = masukkan(Object.assign({}, s3, { pilih: c }), x[2]); if (m.keranjang) s3 = Object.assign({}, s3, { keranjang: m.keranjang, urutBaris: m.urutBaris }); });
s3 = Object.assign({}, s3, uangPas(s3));
pasok('logAktivitas', [{ id: 'lx', pada: 'x' }]); __n.stok = 0; __n.maks = 0; var rN = simpanNota(s3, { tanggal: '2026-09-21', jam: '10:00', idUnik: function () { return Math.random(); } });
print(J({ lulus: lulus, gagal: gagal, ongkos: { stok: __n.stok, maks: __n.maks, baris: s3.keranjang.length, tolak: rN.tolak || '' } }));
"""
CHIP_CAD = r"""
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var s0 = Object.assign(keadaanAwal(), { sekarang: new Date(TGL + 'T18:00:00+07:00') }); periksaRak('data toko', s0);
var r0 = susunRak((sinkronKeranjang(s0), s0)); var s = s0;
[['karung', function (c) { return c.sisa > 3; }, 1], ['kemasan', function (c) { return c.sisa > 3; }, 2], ['literan', function (c) { return c.wadahLiteran && c.sisa > 10; }, 2], ['literan', function (c) { return !c.wadahLiteran && c.sisa > 10; }, 1], ['repack', function (c) { return c.sisa > 10; }, 3]].forEach(function (x) {
  var c = r0[x[0]].filter(x[1])[0]; if (!c) return; var m = masukkan(Object.assign({}, s, { pilih: c }), x[2]); if (m.keranjang) s = Object.assign({}, s, { keranjang: m.keranjang, urutBaris: m.urutBaris }); });
s = Object.assign({}, s, uangPas(s)); periksaRak('data toko, keranjang lima jalur', s);
// jam dinding SUNGGUHAN (Date.now dikunci JAM_TETAP): preciseTime() jsc, detik
var t = [], dok = ''; for (var i = 0; i < 7; i++) { pasok('logAktivitas', [{ id: 'l' + i, pada: 'x' }]); var a = preciseTime(); var nW = 0; var r = simpanNota(s, { tanggal: TGL, jam: '18:00', idUnik: function () { nW += 1; return 500000 + nW; } }); t.push(Math.round((preciseTime() - a) * 1000)); dok = J(r.dokumen || r.tolak); }
t.sort(function (x, y) { return x - y; });
print(J({ lulus: lulus, gagal: gagal, ms: t[3], dok: dok, baris: s.keranjang.length, tolak: dok.charAt(0) === '"' ? dok.slice(0, 160) : '' }));
"""


def bundel(lama=False, ganti=None):
    js, lay, _app = uji_cache_chip_literan.bundel()
    for a, b in (ganti or []):
        n = js.count(a); assert n == 1, 'kontrol basi: ' + a[:90] + ' (' + str(n) + '×)'
        js = js.replace(a, b)
    if lama:   # cara LAMA (main): rakUntukChip menyusun rak penuh — kontrol "lambat lagi" sudah menggantinya sendiri
        assert js.count(BARU) + js.count(LAMA) == 1, 'kontrol basi: penyusun rak chip tidak ketemu'
        js = js.replace(BARU, LAMA)
    return uji_rak_inkremental.JAM_TETAP + js + UKUR


def jalan(ganti=None):
    g, l = [], 0
    kotak = '\nvar KOTAK = ' + json.dumps(uji_rak_inkremental.KOTAK) + ';\n'
    hB, eB = uji_wadah_bernama.jalan(bundel(False, ganti) + kotak + NOTA)
    hL, eL = uji_wadah_bernama.jalan(bundel(True, ganti) + kotak + NOTA)
    if hB is None or hL is None: return 0, ['NOTA: JSC JATUH ' + (eB or eL)], None
    oB, oL = hB['out'], hL['out']
    beda = [k for k in sorted(set(oB) | set(oL)) if oB.get(k) != oL.get(k)]
    kunci = sorted(oB)
    if beda: g.append('PEMBANDING NOTA: hasil cara baru ≠ cara lama di %s — %s ≠ %s' % (beda, str(oB.get(beda[0]))[:300], str(oL.get(beda[0]))[:300]))
    else: l += 1
    nDok = sum(len(json.loads(oB[k])['dokumen'] or []) for k in kunci if k in ('A', 'B', 'C', 'D2'))
    sah = all(not json.loads(oB[k])['tolak'] for k in ('A', 'B', 'C', 'D2')) and json.loads(oB['D1'])['perluTembus'] and nDok >= 15 and not any(k.startswith('tanpa-chip') or k.startswith('tolak-') for k in kunci)
    if not sah: g.append('PEMBANDING NOTA: skenario tidak lengkap (nota tertolak / chip tidak ada / tembus tidak ditanya) → ' + json.dumps({k: str(v)[:160] for k, v in oB.items()})[:900])
    else: l += 1
    hC, eC = uji_wadah_bernama.jalan(bundel(False, ganti) + kotak + CHIP + CHIP_KOTAK)
    hCL, eCL = uji_wadah_bernama.jalan(bundel(True, ganti) + kotak + CHIP + CHIP_KOTAK)
    if hC is None or hCL is None: return l, g + ['CHIP: JSC JATUH ' + (eC or eCL)], None
    l += hC['lulus']; g += hC['gagal']
    oN, oO = hC['ongkos'], hCL['ongkos']
    if not (oN['stok'] * 3 <= oO['stok'] and oN['maks'] < oO['maks'] and not oN['tolak'] and oN['baris'] >= 3):
        g.append('ONGKOS: simpanNota sesudah data berubah memanggil buku stok %d× (cara lama %d×), langit-langit %d× (lama %d×) — harus jauh lebih sedikit' % (oN['stok'], oO['stok'], oN['maks'], oO['maks']))
    else: l += 1
    return l, g, {'nota': len(kunci), 'dokumen': nDok, 'ongkos_baru': oN, 'ongkos_lama': oO}


def jalan_cadangan(p):
    cad, tgl = uji_wadah_bernama.cad_js(p)
    tambah = '\nvar CAD = ' + cad + ';\nvar TGL = ' + json.dumps(tgl) + ';\n'
    hB, eB = uji_wadah_bernama.jalan(bundel(False) + tambah + CHIP + CHIP_CAD)
    hL, eL = uji_wadah_bernama.jalan(bundel(True) + tambah + CHIP + CHIP_CAD)
    if hB is None or hL is None: return None, ['CADANGAN: JSC JATUH ' + (eB or eL)[-300:]]
    g = hB['gagal'] + (['CADANGAN: dokumen nota cara baru ≠ cara lama di data toko'] if hB['dok'] != hL['dok'] else [])
    if hB['tolak']: g.append('CADANGAN: nota data toko tertolak — ' + hB['tolak'])
    return {'ms_baru': hB['ms'], 'ms_lama': hL['ms'], 'baris': hB['baris'], 'dokumen_sama': hB['dok'] == hL['dok']}, g


RUSAK = [
    ('rak identitas memakai modal wadah literan yang lain', "const g = identitas ? { hppPerKg: wbModalPerKg(W, s) } : geraLiteranWadah(W, rasio, s, pakai);", "const g = identitas ? { hppPerKg: 0 } : geraLiteranWadah(W, rasio, s, pakai);"),
    ('rak identitas tidak mengisi berat karung berurutan', "const g = identitas ? (setelBeratDom(berat), {}) : geraKarung(merk, berat);", "const g = identitas ? {} : geraKarung(merk, berat);"),
    ('rak identitas membuang kemasan', "    const g = identitas ? {} : geraKemasan(kunci);", "    if (identitas) return; const g = geraKemasan(kunci);"),
    ('rak identitas tidak mengurutkan', "  rak.literan.sort(termurah); rak.repack.sort(termurah);", "  if (!identitas) { rak.literan.sort(termurah); rak.repack.sort(termurah); }"),
    ('rakUntukChip kembali menyusun rak penuh (lambat lagi)', BARU, LAMA),
]

if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, a, b in RUSAK:
            try:
                if a == BARU:   # "lambat lagi": bundel baru = bundel lama → hanya ONGKOS yang boleh berbunyi
                    l, g, _ = jalan([(BARU, LAMA)])
                else: l, g, _ = jalan([(a, b)])
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' — ' + str(e)); kode = 3; continue
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:170] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, info = jalan()
    print('CATAT NOTA CEPAT (kotak pasir): %d lulus · %d gagal%s' % (l, len(g), (' · ' + json.dumps(info)) if info else ''))
    p = uji_wadah_bernama.cadangan_toko()
    if p:
        h, gc = jalan_cadangan(p); g += gc
        print('DATA TOKO (%s): %s' % (os.path.basename(p), json.dumps(h) if h else gc))
    else: print('DATA TOKO: dilewati — tidak ada _privat/backup-batch-*.json (worktree / CI)')
    for x in g: print('   ✗ ' + x[:700])
    sys.exit(2 if g else 0)
