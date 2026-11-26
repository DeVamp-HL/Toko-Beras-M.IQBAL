#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_brankas_susulan.py — paket brankas & catatan susulan (owner 26 Nov 2026). KOTAK PASIR (angka CONTOH, bukan angka toko), jsc saja, TANPA peramban.
  SU  catatan bertanggal hari tutup yang dicatat SESUDAH tutup (pola kasus 18 Okt: bayar utang ke owner dari brankas; pola kasus 25 Okt: owner mengembalikan kasbon
      ke rekening; + pindah laci → brankas & ambil amplop ke laci sesudah tutup): ugSusulan per tempat, tutup berikutnya MEMBAWANYA — laci seharusnya (kertas
      Σ baris = seharusnya, tidak jadi "kurang kas" palsu), titik brankas / rekening / amplop, Σ fisik − seharusnya = selisih laci; tutup ulang hari yang sama
      ikut catatan sesudah tutup pertama; buku kas harian (khSusulan) satu aturan.
  CI  Catat isi brankas menurut hitungan (pola Catat isi rekening): patokan bertanggal kemarin / hari ini, tempat yang dicatat = angka diketik dikurangi gerakan
      hari ini, tempat lain MEMBAWA catatan susulan patokan lama; laba tidak berubah; ditolak tanpa angka / tanpa patokan; rekening tetap jalan.
  ASAP: cadangan toko lokal (bila ada) — daftar patokan yang dulu kehilangan catatan susulan (tempat & rupiah per hari, dicetak lokal saja), tutup berikutnya
        lama vs baru, Catat isi brankas di angka hitungan = selisih 0.

    python3 alat-uji/uji_brankas_susulan.py            → N lulus · 0 gagal
    python3 alat-uji/uji_brankas_susulan.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kas_rekening  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
UG = 'baru/js/layar/uang-logika.js'; TH = 'baru/js/layar/tutup-hari-logika.js'; KR = 'baru/js/layar/kas-rekening-logika.js'
MODUL = uji_kas_rekening.MODUL
SUMBER = {'uang': 'baru/js/layar/uang.js', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'rules': 'firestore.rules', 'ug': UG}
JAM = "var __KINI = new Date('2026-10-19T21:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"

TITIK18 = {'laci': 300000, 'brankas': 20000000, 'rekening': 1000000, 'amplop': 500000}
KOTAK = {
  'tutupHari': [{'id': '2026-10-18', 'tanggal': '2026-10-18', 'jam': '18:05', 'selisihLaci': 0, 'diubahPada': '2026-10-18T11:05:00.000Z', 'sistemBaru': True, 'titik': TITIK18}],
  'pengaturan': [dict(TITIK18, id='titikKas', tanggal='2026-10-18', diubahPada='2026-10-18T11:05:00.000Z')],
  'utangOwnerMutasi': [{'id': 'uo1', 'tanggal': '2026-10-01', 'jam': '09:00', 'tipe': 'saldoAwal', 'pinjaman': True, 'nominal': 10000000},
                       {'id': 'uo2', 'tanggal': '2026-10-18', 'jam': '20:50', 'tipe': 'bayar', 'nominal': 7000000, 'dari': 'brankas', 'catatan': 'Toko mengembalikan pinjaman owner'}],
  'kasbonMutasi': [{'id': 'kb1', 'tanggal': '2026-10-10', 'jam': '09:00', 'tipe': 'ambil', 'namaPegawai': 'Owner', 'owner': True, 'nominal': 450000, 'dari': 'laci'},
                   {'id': 'kb2', 'tanggal': '2026-10-18', 'jam': '21:20', 'tipe': 'bayar', 'namaPegawai': 'Owner', 'owner': True, 'nominal': 450000, 'caraBayar': 'Transfer', 'dari': 'rekening'}],
  'pindahUang': [{'id': 'pd-2026-10-18', 'tanggal': '2026-10-18', 'jam': '18:05', 'dari': 'laci', 'ke': 'brankas', 'nominal': 900000, 'alasan': 'Amankan laci (tutup hari)', 'biayaAdmin': 0},
                 {'id': 'p1', 'tanggal': '2026-10-18', 'jam': '21:00', 'dari': 'laci', 'ke': 'brankas', 'nominal': 100000, 'alasan': 'Amankan ke brankas', 'biayaAdmin': 0}],
  'amplopLaba': [{'id': 'am-2026-10-18', 'tanggal': '2026-10-18', 'jam': '18:05', 'tipe': 'setor', 'nominal': 20000, 'catatan': 'Sisihan tutup hari'},
                 {'id': 'a1', 'tanggal': '2026-10-18', 'jam': '21:10', 'tipe': 'ambil', 'nominal': 50000, 'ke': 'laci', 'catatan': 'Ambil amplop'}],
  'penjualan': [{'id': 1001, 'tanggal': '2026-10-19', 'jam': '10:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 25, 'hargaTotal': 500000, 'hppTotalSaatJual': 450000, 'trxId': 't1'},
                {'id': 1000, 'tanggal': '2026-10-18', 'jam': '10:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 25, 'hargaTotal': 500000, 'hppTotalSaatJual': 450000, 'trxId': 't0'}],
  'aturanToko': [{'id': 'tutupHari', 'persenSisih': 0, 'kembalian': 500000, 'maafSelisih': 0}],
}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); };
var KINI = new Date('2026-10-19T21:00:00+07:00'); var nId = 900000;
var W = { tanggal: '2026-10-19', jam: '21:00', kini: '2026-10-19T14:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
var K0 = JSON.parse(J(KOTAK)); Object.keys(K0).forEach(function (n) { pasok(n, K0[n]); }); setelSumber('cadangan', 'kotak pasir');
var T18 = ambilTitikKas(); var su = ugSusulan(T18);
ok('SU1 catatan sesudah tutup 18 Okt 18.05 per tempat: brankas −7.000.000 (bayar utang) +100.000 (pindah dari laci) · rekening +450.000 (kasbon kembali) · laci −100.000 +50.000 · amplop −50.000; sisihan & amankan tutup itu sendiri TIDAK',
  su.brankas === -6900000 && su.rekening === 450000 && su.laci === -50000 && su.amplop === -50000, J(su));
ok('SU1 buku kas harian memakai aturan yang sama (khSusulan = ugSusulan)', J(khSusulan(T18)) === J(su));
var S1 = saldoKantong('2026-10-19');
ok('SU2 saldoKantong melewati catatan sesudah tutup (sebab cacatnya): brankas tetap 20.000.000, rekening 1.000.000', S1.brankas === 20000000 && S1.rekening === 1000000 && S1.laci === 800000, J(S1));
var RL = rumusLaci('2026-10-19'); var jb = RL.baris.reduce(function (a, b) { return a + (b.arah === 0 ? b.n : b.arah * b.n); }, 0);
ok('SU3 laci seharusnya 19 Okt = 300.000 + jual 500.000 − pindah sesudah tutup 100.000 + ambil amplop sesudah tutup 50.000 = 750.000; kertas Σ baris = seharusnya', RL.seharusnya === 750000 && jb === 750000
  && RL.baris.some(function (b) { return /^Dipindah ke brankas · dicatat sesudah tutup/.test(b.nama) && b.n === 100000; }) && RL.baris.some(function (b) { return /^Diambil dari amplop laba · dicatat sesudah tutup/.test(b.nama) && b.n === 50000; }), J([RL.seharusnya, jb, RL.baris]));
ok('SU3 kas seharusnya total = semua tempat + catatan sesudah tutup = 15.750.000 (uang sungguhan)', RL.kasTotal === 15750000, RL.kasTotal);
var D = { lembar: { 50000: 15 }, receh: 0, status: { laci: 'beres', rekening: 'lewat', sisih: 'lewat', timbang: 'lewat', amankan: 'lewat' }, rekPilih: '', alasan: '' };
var R = susunTutup(D, W); var dt = R.dokumen.find(function (x) { return x.koleksi === 'tutupHari'; }).data; var ti = R.dokumen.find(function (x) { return x.koleksi === 'pengaturan'; }).data;
ok('SU4 tutup 19 Okt: laci dihitung 750.000 = PAS (dulu "kurang 50.000" palsu)', !R.tolak && dt.selisihLaci === 0, J([R.tolak, dt.selisihLaci]));
ok('SU4 titik 19 Okt MEMBAWA catatan sesudah tutup: brankas 13.100.000 · rekening 1.450.000 · amplop 450.000 · laci 750.000', ti.brankas === 13100000 && ti.rekening === 1450000 && ti.amplop === 450000 && ti.laci === 750000, J(ti));
ok('SU4 Σ fisik − seharusnya = selisih laci (dokumen tutup)', dt.kasFisikLaci + dt.kasFisikRekening + dt.kasFisikAmplop + dt.kasFisikBrankas - dt.kasSeharusnya === dt.selisihLaci, J([dt.kasFisikLaci, dt.kasFisikRekening, dt.kasFisikAmplop, dt.kasFisikBrankas, dt.kasSeharusnya]));
terapkanKeCache(R.dokumen);
var S2 = saldoKantong('2026-10-19'); ok('SU5 sesudah tutup 19 Okt: isi tiap tempat = uang sungguhan (total 15.750.000)', S2.total === 15750000 && S2.brankas === 13100000 && S2.rekening === 1450000, J(S2));
// tutup ulang hari yang sama: catatan sesudah tutup pertama ikut
pasok('pengeluaranHarian', [{ id: 'h1', tanggal: '2026-10-19', jam: '22:00', kategori: 'toko', untuk: 'toko', keterangan: 'Bensin', nominal: 30000, dari: 'brankas' }]);
var W2 = Object.assign({}, W, { jam: '22:30', kini: '2026-10-19T15:30:00.000Z' }); var R2 = susunTutup(D, W2, true); var ti2 = R2.dokumen.find(function (x) { return x.koleksi === 'pengaturan'; }).data;
ok('SU6 tutup ulang 19 Okt 22.30: uang keluar brankas 22.00 (sesudah tutup pertama) ikut — brankas 13.070.000', !R2.tolak && ti2.brankas === 13070000, J([R2.tolak, ti2]));
pasok('pengeluaranHarian', []);
// ---------- Catat isi brankas ----------
pasok('pindahUang', cacheMentah('pindahUang').concat([{ id: 'p2', tanggal: '2026-10-19', jam: '22:00', dari: 'brankas', ke: 'rekening', nominal: 1000000, alasan: 'Setor ke bank', biayaAdmin: 0 }]));
pasok('pengeluaranHarian', [{ id: 'h2', tanggal: '2026-10-20', jam: '09:00', kategori: 'toko', untuk: 'toko', keterangan: 'Galon', nominal: 200000, dari: 'brankas' }]);
var W3 = { tanggal: '2026-10-20', jam: '10:00', kini: '2026-10-20T03:00:00.000Z', idUnik: W.idUnik };
var H = hitungTitikTempat('brankas', '11.800.000', W3);
ok('CI1 hitungan brankas sekarang = 13.100.000 − 1.000.000 (pindah sesudah tutup) − 200.000 = 11.900.000; diketik 11.800.000 → turun 100.000', !H.tolak && H.hitungan === 11900000 && H.selisih === -100000, J([H.tolak, H.hitungan, H.selisih]));
ok('CI1 patokan baru bertanggal kemarin (19 Okt): brankas = 11.800.000 + 200.000 (gerakan hari ini) = 12.000.000; rekening MEMBAWA setoran sesudah tutup (1.450.000 + 1.000.000)', H.titik.tanggal === '2026-10-19' && H.titik.brankas === 12000000 && H.titik.rekening === 2450000 && H.titik.laci === 750000 && H.titik.amplop === 450000, J(H.titik));
var Rb = susunTitikBrankas('11.800.000', W3); terapkanKeCache(Rb.dokumen); var S3 = saldoKantong('2026-10-20');
ok('CI2 sesudah dicatat: brankas sekarang = 11.800.000 (angka diketik), rekening 2.450.000 tidak hilang; laba tidak berubah; satu dokumen titikKas saja', S3.brankas === 11800000 && S3.rekening === 2450000 && Rb.dokumen.length === 1 && Rb.dokumen[0].koleksi === 'pengaturan' && /Isi brankas dicatat Rp11\.800\.000/.test(Rb.patch.kabar), J([S3, Rb.patch.kabar]));
ok('CI3 ditolak tanpa angka / minus; tempat tak dikenal', /Hitung isi brankas/.test(hitungTitikTempat('brankas', '', W3).tolak) && /Hitung isi brankas/.test(hitungTitikTempat('brankas', '-5', W3).tolak) && /tidak dikenal/.test(hitungTitikTempat('laci', '5', W3).tolak));
var Hr = hitungTitikRekening('2.500.000', W3); ok('CI4 Catat isi rekening tetap jalan (pembungkus): rekening naik 50.000, brankas tetap', !Hr.tolak && Hr.selisih === 50000 && Hr.titik.brankas === S3.brankas + 200000 - 0, J([Hr.selisih, Hr.titik]));
// patokan bertanggal hari ini (sesudah tutup) → ditulis ulang dengan angka diketik
var tH = Object.assign({}, ambilTitikKas(), { tanggal: '2026-10-20', diubahPada: '2026-10-20T02:00:00.000Z' }); pasok('pengaturan', [tH]);
var H5 = hitungTitikTempat('brankas', '9.999.000', W3); ok('CI5 patokan sudah bertanggal hari ini: patokan hari ini ditulis ulang, brankas = angka diketik', H5.titik.tanggal === '2026-10-20' && H5.titik.brankas === 9999000, J(H5.titik));
pasok('pengaturan', []); ok('CI6 tanpa patokan kas: ditolak dengan sebabnya', /Titik kas belum disetel/.test(hitungTitikTempat('brankas', '5', W3).tolak));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
var galat = []; var CAD = __CAD__; var hasil = { patokan: [], tutupBerikut: null, catat: null };
try { Object.keys(CAD).forEach(function (k) { if (Array.isArray(CAD[k])) pasok(k, CAD[k]); }); setelSumber('cadangan', 'asap'); } catch (e) { galat.push('muat: ' + e.message); }
var akhir = (function () { var t = ''; (CAD.penjualan || []).forEach(function (p) { if ((p.tanggal || '') > t) t = p.tanggal; }); return t; })();
try { ambilTutupHari().filter(function (d) { return d && d.titik; }).forEach(function (d) { var t = Object.assign({ tanggal: d.tanggal, diubahPada: d.diubahPada }, d.titik); var s = ugSusulan(t);
  var lain = ['brankas', 'rekening', 'amplop'].filter(function (k) { return Math.abs(s[k]) >= 0.5; }); if (lain.length || Math.abs(s.laci) >= 0.5) hasil.patokan.push({ tanggal: d.tanggal, jam: d.jam, laci: s.laci, brankas: s.brankas, rekening: s.rekening, amplop: s.amplop }); }); } catch (e) { galat.push('patokan: ' + e.message); }
try { var T = ambilTitikKas(); var su = ugSusulan(T); var S = saldoKantong(); hasil.tutupBerikut = { titik: T.tanggal, susulan: su, brankasLama: S.brankas, brankasBaru: S.brankas + su.brankas, rekeningLama: S.rekening, rekeningBaru: S.rekening + su.rekening, amplopLama: S.amplop, amplopBaru: S.amplop + su.amplop }; } catch (e) { galat.push('tutup berikut: ' + e.message); }
try { var W = { tanggal: akhir, jam: '20:00', kini: new Date(akhir + 'T20:00:00+07:00').toISOString() }; var S0 = saldoKantong(); var su0 = ugSusulan(ambilTitikKas()); var H = hitungTitikTempat('brankas', String(Math.round(S0.brankas + su0.brankas)), W); hasil.catat = { tolak: H.tolak || '', selisih: H.selisih }; } catch (e) { galat.push('catat isi: ' + e.message); }
print(JSON.stringify({ galat: galat, akhir: akhir, hasil: hasil }));
"""

RUSAK = [
    ('susulan tanpa amplop & pindah', UG, "  const jamT = ugJamPasang(t);\n  if (jamT) {", "  const jamT = '';\n  if (jamT) {"),
    ('tutup: titik brankas/rekening/amplop tanpa catatan susulan (cacat lama)', TH, "const rekening = S.ada ? S.rekening + su.rekening : 0; const amplop = S.ada ? S.amplop + su.amplop : 0; const brankas = S.ada ? S.brankas + su.brankas : 0;", "const rekening = S.ada ? S.rekening : 0; const amplop = S.ada ? S.amplop : 0; const brankas = S.ada ? S.brankas : 0;"),
    ('tutup: laci seharusnya hanya gerakan susulan (pindah/amplop sesudah tutup jadi kurang kas palsu)', TH, "seharusnya: S1.laci + su.laci, baris, teks: 'seharusnya ' + RP(S1.laci + su.laci)", "seharusnya: S1.laci + nSusul, baris, teks: 'seharusnya ' + RP(S1.laci + nSusul)"),
    ('tutup: kas seharusnya total tanpa susulan tempat lain', TH, "kasTotal: S1.total + suTotal,", "kasTotal: S1.total + nSusul,"),
    ('tutup: baris kertas pindah sesudah tutup hilang', TH, "if (p.dari === 'laci') dorong('Dipindah ke ' + ugNamaTempat(p.ke).toLowerCase() + kataSusul, -1, Number(p.nominal) || 0);", ""),
    ('catat isi: tempat lain tanpa catatan susulan', UG, "const lain = (k) => Math.round(dasar[k] + su[k]);", "const lain = (k) => Math.round(dasar[k]);"),
    ('catat isi: angka diketik tanpa gerakan hari ini', UG, "isi = n - (S[tempat] - dasar[tempat]);", "isi = n;"),
    ('catat isi: tanpa patokan tidak ditolak', UG, "if (!S.ada) return { n, tolak: 'Titik kas belum disetel — Tutup hari dulu malam ini, sesudahnya isi ' + C.nama + ' bisa dicatat', S, belumPernah: true };", ""),
    ('buku kas harian: aturan susulan sendiri (tanpa amplop/pindah)', KR, "export function khSusulan(t) { return ugSusulan(t); }", "export function khSusulan(t) { const s = ugSusulan(Object.assign({}, t, { diubahPada: '' })); return s; }"),
]
STATIS = [
    ('Pindah uang: tombol & lembar Catat isi brankas', 'uang', ['data-aksi="puBrkBuka"', 'data-k="lembar-brk"', 'data-aksi="puBrkSimpan"', 'UG.susunTitikBrankas(', "UG.hitungTitikTempat('brankas'"]),
    ('uang-logika: satu aturan susulan dipakai catat isi', 'ug', ['export function ugSusulan(t)', 'export function hitungTitikTempat(tempat, ketik, w)', 'export const susunTitikBrankas']),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_brankas_susulan.py && python3 alat-uji/uji_brankas_susulan.py --kontrol']),
    ('BACA-DULU menyebut paket ini', 'baca', ['## Brankas & catatan sesudah tutup', 'ugSusulan', 'Catat isi brankas']),
]
RUSAK_STATIS = [
    ('Pindah uang tanpa tombol brankas', 'uang', 'data-aksi="puBrkBuka"', 'data-aksi="x"'),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_brankas_susulan.py', 'true'),
    ('rules disentuh', 'rules', 'match /pengaturan/{id} {', 'match /pengaturan/{id} { // brankas'),
]


def bundel(teks):
    return bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in bundel_baru.lengkapi(MODUL))


def jalan(teks, isi=None):
    js = JAM + bundel(teks) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + (isi or SKENARIO)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return None, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    return json.loads(out), None


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    if src['rules'].count('match /pengaturan/{id} {') != 1 or 'brankas' in src['rules'].split('match /pengaturan/{id} {')[1][:600]: g.append('rules disentuh — paket ini sengaja tanpa rules baru (pengaturan/titikKas sudah owner)')
    return len(STATIS) - len(g), g


def muat():
    sumber = set(bundel_baru.lengkapi(MODUL))
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in sumber), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama + ' (' + str(teks[berkas].count(a)) + '×)'); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b); h, e = jalan(T); g = e if h is None else h['gagal']
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_STATIS:
            if src[berkas].count(a) < 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            S = dict(src); S[berkas] = S[berkas].replace(a, b); l, g = statis(S)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h, e = jalan(teks); ls, gs = statis(src)
    g = e if h is None else h['gagal']
    print('KOTAK PASIR: %d lulus · %d gagal' % (0 if h is None else h['lulus'], len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '..', '..', '..', '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and '--tanpa-asap' not in sys.argv:
        ha, ea = jalan(teks, ASAP.replace('__CAD__', open(cad[-1], encoding='utf-8').read()))
        if ha is None: print('ASAP DATA TOKO: JSC JATUH ' + ea[0][:600]); g = list(g) + ['asap']
        else:
            H = ha['hasil']; beres = not ha['galat'] and H['catat'] and not H['catat']['tolak'] and abs(H['catat']['selisih']) < 0.5
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s · galat %s' % (os.path.basename(cad[-1]), ha['akhir'], 'LULUS' if beres else 'GAGAL', json.dumps(H, ensure_ascii=False), json.dumps(ha['galat'], ensure_ascii=False)))
            if not beres: g = list(g) + ['asap']
    sys.exit(1 if g or gs else 0)
