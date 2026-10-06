#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_hemat_baca.py — HEMAT BACA tahap 1–2 (owner 7 Okt 2026, siap 2027; spesifikasi docs/rancangan-hemat-baca.md). jsc + statis, TANPA peramban.

  A · MURNI (baru/js/data/hemat-baca.js di jsc): hari kuota Pasifik (reset 14.00 WIB s/d 31 Okt, 15.00 WIB sesudahnya), tanda air & batas delta (tetap sehari,
      geser > 8 jam ≤ 3×), batas nisan (tidak pernah 0), jepit jam server + 10 menit, saring batu nisan, nilai hitungan server, penulis tanpa cap (kasir darurat
      < kasir-v33, kasir.html, tab /baru/ lama, sistem lama), pendeteksi tanpa cap (+ penjaga banjir simpanan kosong), rencana per koleksi, rem kuota, klaim
      baca penuh harian per toko, ayunan katalog, kunci tab, pendengar simpanan hidup, daftar siap-nyala.
  B · SERVER MAINAN (hbSesi asli + "SDK" tiruan: simpanan per perangkat, pendengar simpanan / delta capServer / baca penuh dengan limbo / nisan, hitungan server,
      jam server & jam perangkat terpisah): perangkat baru, buka lagi (delta + nisan), catatan lama diubah perangkat lain, catatan dihapus (dalam & di luar
      jendela delta), Console tanpa cap → pendeteksi harian menyentuh, nota HP kasir lama (gerbang penulis → dengar penuh; tanpa gerbang → hitungan beda →
      baca penuh), jam perangkat mundur 3 hari & maju 2 hari, perangkat lama tutup > 14 hari, jadwal baca penuh harian per toko (Okt & Nov), tab yang turun
      dari primer (pendengar simpanan mati), rem kuota.
  C · firebase.js DIJALANKAN di jsc dengan SDK palsu: saklar MATI = pendengar persis sebelum 7 Okt (satu pendengar penuh per koleksi + katalog, tanpa
      source 'cache' / where capServer / limit 1.000.000), capServer dikupas sebelum memori; saklar NYALA = koleksi hemat lewat pendengar simpanan, koleksi
      tetap penuh; tulisBerkas: cap HANYA koleksi hemat (bukan berita acara tutup buku, pesanan, setelan, katalog, jejak), salinan antre tanpa sentinel,
      batu nisan di batch yang sama HANYA sesudah aturan v7 terbukti, uang-kritis ditolak bila belum segar, tab yang kalah tidak menulis; denyut owner bercap.
  D · STATIS: SETIAP jalan tulis SDK di baru/js membawa capServer atau tercatat sengaja tanpa cap (koleksi tetap / jejak / katalog / arsip) beserta alasannya;
      adaptor SDK (simpanan tanpa GC, delta capServer, baca penuh kueri sendiri, nisan); kasir darurat: nota lewat :commit + REQUEST_TIME tanpa updateMask,
      denyut tetap PATCH; rantai versi kasir-v33.
KOTAK PASIR saja (nama & angka contoh, bukan data toko).

    python3 alat-uji/uji_hemat_baca.py            → N lulus · 0 gagal (keluar 1 bila gagal)
    python3 alat-uji/uji_hemat_baca.py --kontrol  → tiap kerusakan WAJIB berbunyi (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MURNI = ['baru/js/data/koleksi.js', 'baru/js/data/kunci-periode.js', 'baru/js/data/hemat-baca.js']
_M = ['baru/js/data/koleksi.js', 'baru/js/data/kunci-periode.js', 'baru/js/mesin/pembantu.js', 'baru/js/data/toko.js', 'baru/js/mesin/beku.js', 'baru/js/inti/format.js',
      'baru/js/layar/arsip-logika.js', 'baru/js/layar/wadah-bernama-logika.js', 'baru/js/data/akses.js', 'baru/js/data/antre-lokal.js', 'baru/js/data/katalog-kasir.js',
      'baru/js/data/hemat-baca.js', 'baru/js/data/firebase.js']
BERKAS = sorted(set(_M + MURNI + ['kasir-darurat-nominal.html', 'sw-kasir.js']))


def baca_semua():
    t = {p: open(os.path.join(AKAR, p), encoding='utf-8').read() for p in BERKAS}
    for akar, _, berkas in os.walk(os.path.join(AKAR, 'baru', 'js')):
        for b in berkas:
            if b.endswith('.js'):
                p = os.path.relpath(os.path.join(akar, b), AKAR)
                if p not in t: t[p] = open(os.path.join(AKAR, p), encoding='utf-8').read()
    return t


def bundel(t, daftar):
    return '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in daftar])


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return None, ((r.stderr or '') + (r.stdout or ''))[-1500:]
    return json.loads(baris[-1]), ''


ALAT = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket !== undefined ? ' → ' + String(typeof ket === 'string' ? ket : JSON.stringify(ket)).slice(0, 600) : '')); }
function J(x) { return JSON.stringify(x); }
function salin(x) { return JSON.parse(JSON.stringify(x)); }
var MNT = 60000, JM = 3600000, HR = 86400000;
var Z = function (iso) { return Date.parse(iso); };
"""

# ---------------------------------------------------------------------------------------------------------------------------------------------------
SKENARIO_MURNI = r"""
// ===================== A · fungsi murni =====================
ok('hari kuota: 2 Okt 06.59Z = 1 Okt (sebelum reset 14.00 WIB), 07.00Z = 2 Okt', hbHariKuota(Z('2026-10-02T06:59:00Z')) === '2026-10-01' && hbHariKuota(Z('2026-10-02T07:00:00Z')) === '2026-10-02');
ok('hari kuota: 31 Okt→1 Nov reset 07.00Z (14.00 WIB): 1 Nov 06.59Z = 31 Okt, 07.30Z = 1 Nov; 1 Nov 08.59Z & 09.00Z = 1 Nov (jam musim panas AS selesai di tengah hari kuota)',
  hbHariKuota(Z('2026-11-01T06:59:00Z')) === '2026-10-31' && hbHariKuota(Z('2026-11-01T07:30:00Z')) === '2026-11-01' && hbHariKuota(Z('2026-11-01T08:59:00Z')) === '2026-11-01' && hbHariKuota(Z('2026-11-01T09:00:00Z')) === '2026-11-01');
ok('hari kuota: mulai 2 Nov reset 08.00Z = 15.00 WIB: 2 Nov 07.30Z = 1 Nov, 08.00Z = 2 Nov', hbHariKuota(Z('2026-11-02T07:30:00Z')) === '2026-11-01' && hbHariKuota(Z('2026-11-02T08:00:00Z')) === '2026-11-02');
ok('jam reset WIB: Okt 14.00, Nov–Mar 15.00; musim panas AS 2027 mulai 14 Mar 10.00Z', hbJamResetWib(Z('2026-10-15T00:00:00Z')) === '14.00' && hbJamResetWib(Z('2026-11-15T00:00:00Z')) === '15.00' && hbJamResetWib(Z('2027-01-01T08:00:00Z')) === '15.00'
  && !hbMusimPanasAS(Z('2027-03-14T09:59:00Z')) && hbMusimPanasAS(Z('2027-03-14T10:00:00Z')) && hbHariKuota(Z('2027-01-01T07:59:00Z')) === '2026-12-31' && hbHariKuota(Z('2027-01-01T08:00:00Z')) === '2027-01-01');
var T0 = Z('2026-10-07T03:00:00Z');
// batas delta
var rk1 = { Wt: T0 - 5 * HR, Wd: T0 - 2 * JM };
var b1 = hbBatasDelta(rk1, T0, '2026-10-06');
ok('batas delta: B = max(Wt, Wd) − 60 menit, dicatat untuk hari kuota itu', b1.B === T0 - 3 * JM && b1.hariB === '2026-10-06' && b1.baru === true, J(b1));
var rk2 = { Wt: T0 - 5 * HR, Wd: T0 + 30 * MNT, B: T0 - 3 * JM, hariB: '2026-10-06', nB: 0 };
var b2 = hbBatasDelta(rk2, T0 + 2 * JM, '2026-10-06'), b3 = hbBatasDelta(rk2, T0 + 6 * JM, '2026-10-06'), b4 = hbBatasDelta(Object.assign({}, rk2, { nB: 3 }), T0 + 6 * JM, '2026-10-06');
ok('batas delta: TETAP sehari (target S yang sama dipakai ulang); digeser maju bila > 8 jam di belakang & tanda air maju; paling banyak 3 kali sehari',
  b2.B === rk2.B && !b2.baru && b3.B === T0 - 30 * MNT && b3.baru && b3.nB === 1 && b4.B === rk2.B && !b4.baru, J([b2, b3, b4]));
var b5 = hbBatasDelta(rk2, T0 + 20 * JM, '2026-10-07');
ok('batas delta: hari kuota baru → dihitung ulang dari tanda air; tanpa tanda air → null (wajib baca penuh); jam server belum diketahui → B lama dipakai (aman)',
  b5.B === T0 - 30 * MNT && b5.hariB === '2026-10-07' && hbBatasDelta({}, T0, '2026-10-07').B === null && hbBatasDelta(rk2, null, '').B === rk2.B, J([b5, hbBatasDelta(rk2, null, '')]));
ok('batas nisan: min(Wt) − 60 menit (Wd TIDAK dipakai), koleksi tanpa Wt diabaikan, jam server − 60 menit sebagai batas atas; tidak pernah 0; tanpa apa pun = tunggu',
  hbBatasNisan([T0 - 2 * HR, null, T0 - 1 * HR], T0) === T0 - 2 * HR - JM && hbBatasNisan([null, null], T0) === T0 - JM && hbBatasNisan([null], null) === null && hbBatasNisan([0, undefined], T0) === T0 - JM);
ok('jepit: cap 2099 (Console) dijepit ke jam server + 10 menit; koleksi kosong = jam server', hbJepit(Z('2099-01-01T00:00:00Z'), T0) === T0 + 10 * MNT && hbJepit(null, T0) === T0 && hbJepit(T0 - HR, T0) === T0 - HR);
// cap & kupas
var dk = { id: 5, a: 1, capServer: { toMillis: function () { return T0; } }, padaServer: 'x' }; var ck = hbKupas(dk);
ok('kupas: capServer & padaServer DIBUANG dari isi, nilainya → ms; null = tertunda; angka/teks/peta = "peta"; tidak ada = undefined',
  ck === T0 && !('capServer' in dk) && !('padaServer' in dk) && dk.a === 1 && hbCapMs(null) === null && hbCapMs(123) === 'peta' && hbCapMs({ seconds: 1, nanoseconds: 0 }) === 'peta' && hbCapMs(undefined) === undefined);
// saring nisan
var V = [{ id: 'a', cap: T0 - HR, data: {} }, { id: 'b', cap: T0 + HR, data: {} }, { id: 'c', cap: null, tunda: true, data: {} }, { id: 'd', cap: undefined, data: {} }, { id: 'e', cap: 'peta', data: {} }, { id: 'f', cap: T0, data: {} }, { id: 'g', cap: T0, data: {} }];
var SN = hbSaringNisan(V, { a: T0, b: T0, c: T0, d: T0, e: T0, f: T0 });
ok('saring nisan: dihapus → sembunyi; dibuat ULANG bercap lebih baru → tampil; dibuat ulang tapi masih tertunda → tampil; tanpa cap / "peta" / cap sama → sembunyi; tanpa nisan → tampil',
  J(SN.tampil.map(function (x) { return x.id; })) === '["b","c","g"]' && SN.tersembunyi === 4, J(SN));
// hitungan
ok('nilai hitungan: cocok bila server = mentah − tersembunyi; kurang / lebih; ada tulisan / hapus tertunda atau galat = belum',
  hbNilaiHitung({ server: 10, mentah: 12, tersembunyi: 2 }) === 'cocok' && hbNilaiHitung({ server: 11, mentah: 12, tersembunyi: 2 }) === 'kurang' && hbNilaiHitung({ server: 9, mentah: 12, tersembunyi: 2 }) === 'lebih'
  && hbNilaiHitung({ server: 10, mentah: 12, tersembunyi: 2, tunda: 1 }) === 'belum' && hbNilaiHitung({ server: 10, mentah: 10, hapusTunda: 1 }) === 'belum' && hbNilaiHitung({ galat: 'x' }) === 'belum');
// penulis tanpa cap
var KOLH = ['penjualan', 'stokBahanLiteran', 'piutangMutasi', 'batchMasuk'];
var den = function (id, app, versi, menitLalu) { return { id: id, nama: id, aplikasi: app, versi: versi, pada: new Date(T0 - menitLalu * MNT).toISOString() }; };
var GP1 = hbGerbangPenulis([den('hp1', 'darurat', 'kasir-v32', 60), den('hp2', 'darurat', 'kasir-v33', 5), den('hp3', 'darurat', 'kasir-v30', 15 * 24 * 60)], T0, KOLH);
ok('gerbang penulis: HP kasir < kasir-v33 berdenyut ≤ 14 hari → penjualan DENGAR PENUH (nota tanpa cap); v33 atau > 14 hari → tidak', !!GP1.penuh.penjualan && /hp1/.test(GP1.penuh.penjualan) && !GP1.penuh.stokBahanLiteran && !GP1.peristiwa.length, J(GP1));
var GP2 = hbGerbangPenulis([den('k1', 'kasir', 'kasir-v30', 3 * 24 * 60)], T0, KOLH);
ok('gerbang penulis: kasir.html (pensiun) ≤ 14 hari → tiga koleksi REST dengar penuh', !!GP2.penuh.penjualan && !!GP2.penuh.stokBahanLiteran && !!GP2.penuh.piutangMutasi && !GP2.penuh.batchMasuk, J(GP2));
var GP3 = hbGerbangPenulis([den('mac', 'baru', 'baru', 10)], T0, KOLH), GP4 = hbGerbangPenulis([den('mac', 'baru', 'baru', 40), den('ipad', 'sistem', '', 120)], T0, KOLH), GP5 = hbGerbangPenulis([den('mac', 'baru', 'baru-c1', 1)], T0, KOLH);
ok('gerbang penulis: tab /baru/ versi lama ≤ 15 menit → SEMUA koleksi hemat dengar penuh; lebih lama = peristiwa tahan lama (juga sistem lama); baru-c1 = bercap, tidak apa-apa',
  KOLH.every(function (k) { return !!GP3.penuh[k]; }) && !Object.keys(GP4.penuh).length && GP4.peristiwa.length === 2 && !Object.keys(GP5.penuh).length && !GP5.peristiwa.length, J([GP3, GP4, GP5]));
var pr = GP4.peristiwa[0];
ok('peristiwa tahan lama: perangkat yang baca penuh terakhirnya < peristiwa + 15 menit WAJIB baca penuh sekali; sesudah dibereskan / baca penuh lebih baru → lepas',
  !!hbTotalDariPeristiwa({ Wt: pr.T - HR }, [pr]) && !hbTotalDariPeristiwa({ Wt: pr.T + 20 * MNT }, [pr]) && !hbTotalDariPeristiwa({ Wt: pr.T - HR, gerbangBeres: (function () { var o = {}; o[pr.kunci] = 1; return o; })() }, [pr]));
// pendeteksi tanpa cap
var aw = { u1: { cap: T0 - HR, sidik: 'A' }, u2: { cap: undefined, sidik: 'B' }, u3: { cap: 'peta', sidik: 'C' }, u4: { cap: T0 - HR, sidik: 'D' }, u5: { cap: T0 - HR, sidik: 'E' }, h1: { cap: T0 - HR, sidik: 'F' }, h2: { cap: T0 - HR, sidik: 'G' }, h3: { cap: T0 - HR, sidik: 'H' } };
var ak = { u1: { cap: T0 - HR, sidik: 'A2' }, u2: { cap: undefined, sidik: 'B2' }, u3: { cap: 'peta', sidik: 'C2' }, u4: { cap: T0, sidik: 'D2' }, u5: { cap: T0 - 2 * HR, sidik: 'E2' }, n1: { cap: undefined, sidik: 'N' }, n2: { cap: T0, sidik: 'M' } };
var TC = hbPeriksaTanpaCap(aw, ak, { h2: T0 }, true, { h3: true }), TC0 = hbPeriksaTanpaCap({}, ak, {}, false, {});
ok('pendeteksi: ubah = isi berubah dengan cap sama / hilang / "peta" / MUNDUR; cap maju = sah; baru = lahir tanpa cap; hilang = tanpa nisan & bukan hapus sesi ini',
  J(TC.ubah.sort()) === '["u1","u2","u3","u5"]' && J(TC.baru) === '["n1"]' && J(TC.hilang) === '["h1"]', J(TC));
ok('pendeteksi: simpanan kosong / dasar tidak dipercaya → 7 rb catatan lama TIDAK dianggap "baru tanpa cap" (tanpa banjir sentuh)', !TC0.baru.length, J(TC0));
var many = { ubah: [], baru: [], hilang: [] }; for (var i = 0; i < 401; i++) many.ubah.push('x' + i);
ok('rencana sentuh: > 400 temuan → gen baru (semua perangkat baca penuh), bukan 401 tulisan; tutup buku berjalan → tidak menyentuh apa pun; ubah+baru disentuh, hilang dapat nisan',
  hbRencanaSentuh(many, false).gen === true && !hbRencanaSentuh(TC, true).sentuh.length && J(hbRencanaSentuh(TC, false).sentuh.sort()) === '["n1","u1","u2","u3","u5"]' && J(hbRencanaSentuh(TC, false).nisan) === '["h1"]');
// rencana
var RK = { totalPada: T0 - HR, Wt: T0 - HR, gen: '', bk: '' };
var R0 = function (x) { return hbRencana('penjualan', Object.assign({ rk: RK, dipercaya: true, kiniS: T0, gerbang: { penuh: {}, peristiwa: [] }, gen: '' }, x || {})); };
ok('rencana: biasa → dengar ubahan (delta)', R0().mode === 'delta', J(R0()));
ok('rencana: tanpa rekam / simpanan tidak dipercaya → baca penuh; gen beda ("semua perangkat") → baca penuh; tutup buku berubah → baca penuh; > 14 hari → baca penuh; harian toko → baca penuh',
  hbRencana('penjualan', { rk: {}, dipercaya: false, sebabDasar: 'x' }).mode === 'total' && R0({ gen: 'g1|' }).mode === 'total' && R0({ bkBeda: true }).mode === 'total'
  && R0({ kiniS: T0 + 15 * HR }).mode === 'total' && R0({ harian: true }).mode === 'total' && R0({ kiniS: T0 + 13 * HR }).mode === 'delta');
ok('rencana: tutup buku berjalan / penulis tanpa cap aktif / perangkat tanpa simpanan → DENGAR PENUH; minta manual → baca penuh bukan otomatis',
  R0({ bkAktif: true }).mode === 'penuh' && R0({ gerbang: { penuh: { penjualan: 'HP' }, peristiwa: [] } }).mode === 'penuh' && R0({ jalurPenuh: 'x' }).mode === 'penuh'
  && R0({ minta: { penjualan: { sebab: 'tombol', manual: true } } }).mode === 'total' && R0({ minta: { penjualan: { sebab: 'tombol', manual: true } } }).otomatis === false);
// dasar dipercaya, tutup buku
ok('dasar dipercaya: belum pernah baca penuh / simpanan kosong padahal n ≥ 1 / tinggal < separuh (n ≥ 20) → tidak; selain itu ya',
  !hbDasarDipercaya({}, 5).ya && !hbDasarDipercaya({ totalPada: 1, n: 3 }, 0).ya && !hbDasarDipercaya({ totalPada: 1, n: 100 }, 49).ya && hbDasarDipercaya({ totalPada: 1, n: 100 }, 60).ya && hbDasarDipercaya({ totalPada: 1, n: 0 }, 0).ya);
ok('tutup buku: berjalan/terkunci/membatalkan = aktif; sidik berita acara berubah saat status/paraf berubah', hbBkAktif([{ tahun: 2026, status: 'terkunci' }]) && !hbBkAktif([{ tahun: 2026, status: 'selesai' }])
  && hbSidikBk([{ tahun: 2026, status: 'berjalan', paraf: { pada: 'p' } }]) !== hbSidikBk([{ tahun: 2026, status: 'selesai', paraf: { pada: 'p' } }]));
// rem
ok('rem kuota: perkiraan + ukuran > 40 rb → ditunda; tombol manual menembus; ≤ 2 baca penuh otomatis per koleksi per hari; 3× mulai tanpa selesai → berhenti',
  !hbRem({ perkiraan: 35000, ukuran: 6000 }).boleh && hbRem({ perkiraan: 35000, ukuran: 6000, manual: true }).boleh && !hbRem({ otomatisK: 2 }).boleh && !hbRem({ mulaiK: 3 }).boleh && hbRem({ perkiraan: 10000, ukuran: 6000 }).boleh);
ok('perkiraan baca toko: denyut owner perangkat LAIN hari kuota ini + perangkat ini + 200 HP kasir', hbPerkiraanToko([{ id: 'a', hemat: { hari: 'H', baca: 1000 } }, { id: 'b', hemat: { hari: 'X', baca: 9000 } }, { id: 'ini', hemat: { hari: 'H', baca: 5000 } }], 'H', 'ini', 300) === 1500);
// klaim harian
var hk = hbHariKuota(T0);
ok('klaim harian: hari kuota beda → klaim; sudah selesai → tidak; perangkat lain sedang < 30 menit → tidak; > 30 menit belum selesai → klaim; milik sendiri belum selesai → lanjut; jam server belum diketahui → tidak',
  hbKlaimHarian({ hari: '2026-10-05', selesai: 1 }, T0, 'A').klaim && !hbKlaimHarian({ hari: hk, selesai: T0 }, T0, 'A').klaim && !hbKlaimHarian({ hari: hk, perangkat: 'B', mulai: T0 - 10 * MNT }, T0, 'A').klaim
  && hbKlaimHarian({ hari: hk, perangkat: 'B', mulai: T0 - 31 * MNT }, T0, 'A').klaim && hbKlaimHarian({ hari: hk, perangkat: 'A', mulai: T0 - MNT }, T0, 'A').klaim && !hbKlaimHarian(null, null, 'A').klaim);
ok('gen: "<semua>|<koleksi>" dari dokumen klaim; tanpa gen = ""', hbGen({ gen: { '*': 'g1', penjualan: 'g2' } }, 'penjualan') === 'g1|g2' && hbGen({ gen: { '*': 'g1' } }, 'retur') === 'g1|' && hbGen(null, 'x') === '');
// ayunan katalog
var AY = hbAyunanBaru(); hbCatatTerbitKatalog(AY, 'K1', T0); hbNilaiKatalogServer(AY, 'K1', 'K1', T0 + MNT);
var gema = !AY.berhenti; hbNilaiKatalogServer(AY, 'K2', 'K1', T0 + 5 * MNT);
ok('ayunan katalog: gema terbit sendiri bukan ayunan; isi LAIN ≤ 15 menit sesudah terbit sendiri & beda hitungan perangkat ini → berhenti terbit', gema && !!AY.berhenti && !hbBolehTerbitKatalog(AY, T0).boleh, J(AY));
var AY2 = hbAyunanBaru(); for (var i2 = 0; i2 < 6; i2++) hbCatatTerbitKatalog(AY2, 'K' + i2, T0 + i2 * MNT);
ok('plafon katalog: ≤ 6 terbit otomatis per jam per perangkat', !hbBolehTerbitKatalog(AY2, T0 + 10 * MNT).boleh && hbBolehTerbitKatalog(AY2, T0 + 2 * JM).boleh);
// kunci tab
var LSK = {}; var penyK = { baca: function (k) { return LSK[k] === undefined ? null : LSK[k]; }, tulis: function (k, v) { LSK[k] = String(v); }, hapus: function (k) { delete LSK[k]; } };
var jamK = T0; var kA = hbKunciTab(penyK, function () { return jamK; }, 'sesiA'), kB = hbKunciTab(penyK, function () { return jamK; }, 'sesiB');
var k0 = kB.keadaan(); kA.ambil(); jamK += 4000; var k1 = kB.keadaan(); jamK += 13000; var k2 = kB.keadaan(); kB.ambil(); var k3 = kA.milik(), k4 = kB.milik();
ok('kunci tab: bebas → tab A ambil; tab B melihat "lain" selama A berdetak < 12 detik; A diam > 12 detik → "basi"; B ambil (Pakai di sini) → A bukan pemilik lagi (storage) → A berhenti',
  k0 === 'bebas' && k1 === 'lain' && k2 === 'basi' && k3 === false && k4 === true, J([k0, k1, k2, k3, k4]));
// pendengar hidup
var PH = hbPenjagaHidup(); PH.catat('penjualan', 'x1', { cap: T0 }, T0); PH.catat('penjualan', 'x2', { cap: T0 }, T0); PH.catat('penjualan', 'x3', { cap: T0 }, T0); PH.catat('retur', 'r1', { hilang: true }, T0);
PH.cocokkan('penjualan', function (id) { return id === 'x2' ? { cap: null, tunda: true } : id === 'x1' ? { cap: T0 } : null; }, function (id) { return id === 'x3'; });
PH.cocokkan('retur', function () { return null; }, function () { return false; });
var mati0 = PH.mati(T0 + 1000); PH.catat('penjualan', 'x9', { cap: T0 }, T0); var mati1 = PH.mati(T0 + 6000);
ok('pendengar simpanan hidup: ubahan yang dibawa server terlihat di simpanan (atau tertunda / disembunyikan nisan / hilang sesuai) → bukan mati; tidak terlihat 5 detik → MATI',
  !mati0.length && J(mati1) === '["penjualan"]', J([mati0, mati1]));
// siap-nyala
var SNY = hbSiapNyala({ perangkat: [den('mac', 'baru', 'baru-c1', 5), den('hp', 'darurat', 'kasir-v33', 30)].map(function (p) { p.akun = p.id === 'mac' ? 'owner@tokoberasmiqbal.web.app' : 'kasir@x'; p.antrean = 0; return p; }), kiniMs: T0, nisanSah: true, statis: 0, ownerEmail: 'owner@tokoberasmiqbal.web.app' });
var SNY2 = hbSiapNyala({ perangkat: [den('mac', 'baru', 'baru', 5), den('hp', 'darurat', 'kasir-v32', 30)].map(function (p) { p.akun = p.id === 'mac' ? 'owner@tokoberasmiqbal.web.app' : 'kasir@x'; p.antrean = 0; return p; }), kiniMs: T0, nisanSah: false, statis: 3, ownerEmail: 'owner@tokoberasmiqbal.web.app' });
ok('daftar siap-nyala: aturan v7 · tanpa tab lama / sistem lama 7 hari · HP kasir ≥ kasir-v33 14 hari · owner baru-c1 antrean 0 · tanpa catatan baru tak bercap → hijau semua / merah semua',
  SNY.every(function (x) { return x.ok; }) && SNY2.every(function (x) { return !x.ok; }), J([SNY, SNY2]));
ok('saklar: bawaan MATI (tidak ada / rusak / penyimpanan diblokir); disetel per perangkat', !hbSaklar({ baca: function () { return null; } }) && !hbSaklar({ baca: function () { throw new Error('blokir'); } }) && hbSaklar({ baca: function () { return 'nyala'; } }) && !hbSaklar({ baca: function () { return 'ya'; } }));
ok('kelas koleksi: 48 hemat, tetap = setelan/berita acara/denyut/akun/pesanan, jejak = logAktivitas', hbKoleksiHemat().length === 48 && hbKelas('tutupBukuAcara') === 'tetap' && hbKelas('pesanan') === 'tetap' && hbKelas('logAktivitas') === 'jejak' && hbHemat('penjualan') && !hbHemat('aturanToko') && !hbHemat('ringkasanKasir'), hbKoleksiHemat().length);

// ===================== B · SERVER MAINAN =====================
var TS = function (ms) { return { toMillis: function () { return ms; } }; };
var __q = [];
function antri(f) { __q.push(f); }
function tuntas() { for (var n = 0; n < 5000; n++) { while (__q.length) __q.shift()(); drainMicrotasks(); if (!__q.length) return; } throw new Error('antrean mainan tidak berhenti'); }
function Server(jam) { this.jam = jam; this.k = {}; this.nisan = {}; this.dev = []; this.klaim = null; this.perangkat = []; this.acara = []; }
Server.prototype.kol = function (k) { return k === 'batuNisan' ? this.nisan : (this.k[k] || (this.k[k] = {})); };
// cap: true = jam server (kode bercap) · false = TANPA cap (HP kasir lama / Console membuat baru) · 'tetap' = Console mengubah isi, cap lama dibiarkan
Server.prototype.tulis = function (k, id, data, cap) { var K = this.kol(k); var l = K[id]; K[id] = { data: salin(data), cap: cap === false ? undefined : cap === 'tetap' ? (l ? l.cap : undefined) : this.jam }; this.siar(k, id); };
Server.prototype.hapus = function (k, id, nisan) { delete this.kol(k)[id]; this.siar(k, id); if (nisan) { this.nisan[k + '|' + id] = { data: { id: k + '|' + id, koleksi: k, idDok: String(id) }, cap: this.jam }; this.siar('batuNisan', k + '|' + id); } };
Server.prototype.siar = function (k, id) { this.dev.forEach(function (p) { p.dariServer(k, id); }); };
Server.prototype.ids = function (k) { return Object.keys(this.kol(k)).sort(); };
var S;
function cocokL(L, e) { return L.jenis === 'penuh' ? true : (typeof e.cap === 'number' && e.cap > L.B); }
function Perangkat(nama, geser) { this.nama = nama; this.geser = geser || 0; this.online = true; this.cache = {}; this.L = []; this.ls = {}; this.timer = []; this.vBeku = false; this.antre = []; S.dev.push(this); }
Perangkat.prototype.jam = function () { return S.jam + this.geser; };
Perangkat.prototype.c = function (k) { return this.cache[k] || (this.cache[k] = {}); };
Perangkat.prototype.bentuk = function (id, e) { return { id: id, tunda: !!e.tunda, capMentah: e.cap === null ? null : e.cap === undefined ? undefined : TS(e.cap),
  isi: function () { var x = salin(e.data); if (e.cap !== undefined) x.capServer = e.cap === null ? null : TS(e.cap); return x; } }; };
Perangkat.prototype.snap = function (L) { var C = this.c(L.k), self = this, dok = [];
  Object.keys(C).forEach(function (id) { var e = C[id]; if ((L.jenis === 'delta' || L.jenis === 'nisan') && (e.tunda || !cocokL(L, e))) return; dok.push(self.bentuk(id, e)); });
  return { dariCache: L.jenis === 'cache' ? true : !(self.online && L.terkini), dok: dok }; };
Perangkat.prototype.emit = function (k) { var self = this; this.L.forEach(function (L) { if (!L.aktif || L.k !== k || (L.jenis === 'cache' && self.vBeku)) return; antri(function () { if (L.aktif) L.cb(self.snap(L)); }); }); };
// server → simpanan untuk kueri L, + LIMBO: dokumen simpanan yang cocok kueri tapi tidak ada di server dibuang (perilaku SDK yang diandalkan rancangan)
Perangkat.prototype.sinkron = function (L) { var C = this.c(L.k), K = S.kol(L.k);
  Object.keys(K).forEach(function (id) { var e = K[id]; if (!cocokL(L, e) || (C[id] && C[id].tunda)) return; C[id] = { data: salin(e.data), cap: e.cap }; });
  Object.keys(C).forEach(function (id) { var c = C[id]; if (c.tunda || K[id] || !cocokL(L, c)) return; delete C[id]; }); L.terkini = true; };
Perangkat.prototype.dengar = function (jenis, k, B, cb) { var self = this; var L = { jenis: jenis, k: k, B: B, cb: cb, aktif: true, terkini: false }; this.L.push(L);
  antri(function () { if (!L.aktif) return;
    if (jenis === 'cache') { if (!self.vBeku) cb(self.snap(L)); return; }
    if (jenis === 'penuh' && Object.keys(self.c(k)).length) cb(self.snap(L));   // snapshot SIMPANAN dulu (pendeteksi membandingkannya)
    if (self.online) { self.sinkron(L); self.emit(k); } else cb(self.snap(L)); });
  return function () { L.aktif = false; }; };
Perangkat.prototype.dariServer = function (k, id) { if (!this.online) return; var K = S.kol(k), e = K[id], C = this.c(k), c = C[id];
  var kena = this.L.some(function (L) { return L.aktif && L.k === k && L.jenis !== 'cache' && L.terkini && ((e && cocokL(L, e)) || (!e && c && cocokL(L, c))); });
  if (!kena || (c && c.tunda)) return; if (e) C[id] = { data: salin(e.data), cap: e.cap }; else delete C[id]; this.emit(k); };
Perangkat.prototype.putus = function () { var self = this; this.online = false; this.L.forEach(function (L) { if (L.jenis !== 'cache') { L.terkini = false; if (L.aktif) antri(function () { if (L.aktif) L.cb(self.snap(L)); }); } }); if (this.sesi) this.sesi.online(false); };
Perangkat.prototype.sambung = function () { var self = this; this.online = true; this.L.forEach(function (L) { if (L.aktif && L.jenis !== 'cache') self.sinkron(L); }); Object.keys(this.cache).forEach(function (k) { self.emit(k); }); this.kirim(); if (this.sesi) this.sesi.online(true); };
// tulisan perangkat ini: tampil seketika di simpanan (tertunda, cap null), dikirim saat tersambung (cap = jam SERVER saat diterima)
Perangkat.prototype.tulis = function (k, id, data) { this.c(k)[id] = { data: salin(data), cap: null, tunda: true }; this.antre.push({ k: k, id: id, data: data }); this.emit(k); if (this.online) this.kirim(); };
Perangkat.prototype.hapusDok = function (k, id) { delete this.c(k)[id]; this.antre.push({ k: k, id: id, hapus: true }); if (this.sesi) this.sesi.catatHapus(k, id); this.emit(k); if (this.online) this.kirim(); };
Perangkat.prototype.kirim = function () { var self = this; var q = this.antre; this.antre = [];
  q.forEach(function (x) { if (x.hapus) { S.hapus(x.k, x.id, true); return; } S.tulis(x.k, x.id, x.data, true); var e = S.kol(x.k)[x.id]; self.c(x.k)[x.id] = { data: salin(e.data), cap: e.cap }; self.emit(x.k); }); };
Perangkat.prototype.jadwal = function (f, ms) { var h = { f: f, pada: this.jam() + ms, aktif: true }; this.timer.push(h); return h; };
Perangkat.prototype.tutup = function () { if (this.sesi) this.sesi.berhenti(); this.L.forEach(function (L) { L.aktif = false; }); this.L = []; this.timer = []; this.sesi = null; };
Perangkat.prototype.tetap = function () { if (this.sesi) this.sesi.setelTetap({ perangkat: salin(S.perangkat), acara: salin(S.acara), klaim: S.klaim ? salin(S.klaim) : null }); };
Perangkat.prototype.gema = function () { if (this.sesi) this.sesi.gemaServer(S.jam, this.jam()); };
var KOL = ['penjualan', 'stokBahanLiteran', 'piutangMutasi', 'pengeluaranHarian'];
var NAMA_K = KOL.slice();
Perangkat.prototype.buka = function (opsi) {
  var self = this; this.tutup(); this.mem = {}; this.siap = {}; this.periksa = {}; this.mati = []; this.klaimTulis = 0; this.sentuhN = 0;
  var peny = { baca: function (k) { return self.ls[k] === undefined ? null : self.ls[k]; }, tulis: function (k, v) { self.ls[k] = String(v); }, hapus: function (k) { delete self.ls[k]; } };
  var R = hbBacaRekam(peny, 'proyek-uji', 'uid-owner'); this.R = R;
  this.sesi = hbSesi({ koleksi: NAMA_K, R: R, simpan: function () { hbSimpanRekam(peny, R, self.jam()); }, jam: function () { return self.jam(); },
    jadwal: function (f, ms) { return self.jadwal(f, ms); }, batal: function (h) { if (h) h.aktif = false; }, idPerangkat: self.nama, namaPerangkat: self.nama, online: self.online,
    milikTab: function () { return true; }, hapusTunda: function () { return 0; },
    sdk: { cache: function (k, cb) { return self.dengar('cache', k, null, cb); }, delta: function (k, B, cb) { return self.dengar('delta', k, B, cb); },
      penuh: function (k, cb) { return self.dengar('penuh', k, null, cb); }, nisan: function (B, cb) { return self.dengar('nisan', 'batuNisan', B, cb); },
      hitung: function (k) { return self.online ? Promise.resolve(S.ids(k).length) : Promise.reject({ code: 'unavailable' }); },
      klaim: function (dok) { self.klaimTulis++; S.klaim = salin(dok); antri(function () { S.dev.forEach(function (p) { p.tetap(); }); }); return Promise.resolve(); },
      sentuh: function (k, ids) { self.sentuhN += ids.length; ids.forEach(function (id) { var e = S.kol(k)[id]; if (e) { e.cap = S.jam; S.siar(k, id); } }); return Promise.resolve({ n: ids.length }); },
      tulisNisan: function (k, ids) { ids.forEach(function (id) { S.nisan[k + '|' + id] = { data: { id: k + '|' + id, koleksi: k, idDok: String(id) }, cap: S.jam }; S.siar('batuNisan', k + '|' + id); }); return Promise.resolve({ n: ids.length }); } },
    keluar: { pasok: function (k, data) { self.mem[k] = data; }, tunda: function () {}, siap: function (k) { self.siap[k] = true; }, periksa: function (k, ya) { self.periksa[k] = ya; }, berubah: function () {}, mati: function (k) { self.mati.push(k); } } }).mulai();
  if (opsi && opsi.tetap === false) return this.sesi;
  tuntas(); if (!(opsi && opsi.tanpaGema)) this.gema(); this.tetap(); tuntas(); return this.sesi;
};
function maju(ms) { var akhir = S.jam + ms; while (true) { var due = null, dev = null;
    S.dev.forEach(function (p) { p.timer.forEach(function (h) { var t = h.pada - p.geser; if (h.aktif && t <= akhir && (due === null || t < due.t)) { due = { t: t, h: h }; dev = p; } }); });
    if (!due) break; S.jam = Math.max(S.jam, due.t); due.h.aktif = false; dev.timer = dev.timer.filter(function (h) { return h.aktif; }); due.h.f(); tuntas(); }
  S.jam = akhir; tuntas(); }
function memId(p, k) { return (p.mem[k] || []).map(function (d) { return String(d.id); }).sort(); }
function memDok(p, k, id) { return (p.mem[k] || []).find(function (d) { return String(d.id) === String(id); }) || null; }
function semua(p, f) { return NAMA_K.every(function (k) { return f(k); }); }
function samaServer(p) { return NAMA_K.every(function (k) { return J(memId(p, k)) === J(S.ids(k)); }); }
function beda(p) { var o = {}; NAMA_K.forEach(function (k) { if (J(memId(p, k)) !== J(S.ids(k))) o[k] = { mem: memId(p, k), server: S.ids(k) }; }); return o; }
function keadaanK(p, k) { return p.sesi.keadaan().koleksi.find(function (x) { return x.k === k; }); }

// ---- data awal toko (contoh): sebagian catatan lama TANPA cap (sebelum 7 Okt), sebagian bercap
S = new Server(Z('2026-10-07T03:00:00Z'));   // 10.00 WIB
var nota = function (id, n, tgl) { return { id: id, tanggal: tgl || '2026-10-01', hargaTotal: n, namaProduk: 'Beras Contoh', namaPelanggan: 'Pembeli Contoh' }; };
S.tulis('penjualan', 'p1', nota('p1', 10000), false); S.tulis('penjualan', 'p2', nota('p2', 20000), false);
S.jam -= 3 * HR; S.tulis('penjualan', 'p3', nota('p3', 30000), true); S.tulis('stokBahanLiteran', 's1', { id: 's1', tanggal: '2026-10-04', kg: 5 }, true); S.jam += 3 * HR;
S.jam -= JM; S.tulis('stokBahanLiteran', 's2', { id: 's2', tanggal: '2026-10-07', kg: 3 }, true); S.jam += JM;   // s2 baru → tanda air koleksi ini jauh di depan s1
S.jam -= 2 * JM; S.tulis('penjualan', 'p4', nota('p4', 40000), true); S.tulis('piutangMutasi', 'u1', { id: 'u1', tanggal: '2026-10-07', nominal: 5000 }, true); S.jam += 2 * JM;
S.tulis('pengeluaranHarian', 'h1', { id: 'h1', tanggal: '2026-10-07', nominal: 7000 }, false);
S.klaim = { id: 'hematHarian', hari: '2026-10-06', perangkat: 'lama', selesai: Z('2026-10-06T08:00:00Z') };

// ---- B1 · perangkat BARU (tanpa rekam): simpanan kosong → baca penuh semua; tirai "memuat" tidak terangkat dari simpanan kosong
var A = new Perangkat('mac');
A.buka({ tetap: false }); tuntas();
ok('B1 perangkat baru: simpanan kosong TIDAK menandai siap (tirai memuat), belum ada baca penuh sebelum masukan koleksi tetap', !Object.keys(A.siap).length, J(A.siap));
A.gema(); A.tetap(); tuntas();
ok('B1: sesudah baca penuh semua koleksi: siap, memori = server, semua terperiksa', samaServer(A) && semua(A, function (k) { return A.siap[k] && A.periksa[k] === true; }), J({ beda: beda(A), periksa: A.periksa }));
var rkp = A.R.k.penjualan;
ok('B1: rekam per koleksi per perangkat — Wt = cap server tertinggi (BUKAN jam perangkat), n = jumlah server, baca penuh = jam server', rkp && rkp.Wt === S.jam - 2 * JM && rkp.n === 4 && rkp.totalPada === S.jam, J(rkp));
ok('B1: pendengar sesudahnya = simpanan (V) + delta capServer > Wt − 60 menit + nisan; baca penuh (F) sudah dilepas', A.L.filter(function (L) { return L.aktif && L.jenis === 'penuh'; }).length === 0
  && A.L.some(function (L) { return L.aktif && L.jenis === 'delta' && L.k === 'penjualan' && L.B === rkp.Wt - JM; }) && A.L.some(function (L) { return L.aktif && L.jenis === 'nisan'; }), J(A.L.filter(function (L) { return L.aktif; }).map(function (L) { return [L.jenis, L.k, L.B]; })));
ok('B1: memori tanpa capServer (dikupas)', (A.mem.penjualan || []).every(function (d) { return !('capServer' in d); }));
// perangkat kedua owner (iPad), juga baru
var B = new Perangkat('ipad'); B.buka();
ok('B1: perangkat kedua juga baca penuh sendiri (tiap perangkat ≥ sekali)', samaServer(B), J(beda(B)));

// ---- B2 · buka lagi 2 jam kemudian: simpanan dipercaya (tirai terangkat seketika), lalu delta + nisan dari server
A.tutup(); maju(2 * JM);
S.tulis('penjualan', 'p5', nota('p5', 50000), true);                                   // nota baru (bercap)
S.tulis('penjualan', 'p3', nota('p3', 31000), true);                                   // nota LAMA diubah perangkat lain (bercap)
S.hapus('stokBahanLiteran', 's1', true);                                                // hapus catatan lama (cap < B) — perlu nisan
S.hapus('penjualan', 'p4', true);                                                       // hapus catatan dalam jendela delta (cap > B)
A.buka({ tetap: false }); tuntas();
ok('B2 buka lagi: simpanan perangkat DIPERCAYA → siap seketika dari simpanan (sebelum server menjawab)', semua(A, function (k) { return A.siap[k]; }) && memId(A, 'penjualan').indexOf('p5') < 0, J(A.siap));
A.gema(); A.tetap(); tuntas();
ok('B2: delta membawa nota baru & nota lama yang diubah; nota yang dihapus di jendela delta hilang (limbo); catatan lama yang dihapus disembunyikan BATU NISAN',
  memId(A, 'penjualan').indexOf('p5') >= 0 && memDok(A, 'penjualan', 'p3').hargaTotal === 31000 && memId(A, 'penjualan').indexOf('p4') < 0 && memId(A, 'stokBahanLiteran').indexOf('s1') < 0 && samaServer(A), J(beda(A)));
ok('B2: s1 masih MENTAH di simpanan perangkat (disembunyikan, bukan dibaca ulang) dan hitungan server tetap cocok (yang tersembunyi dikurangkan) → terperiksa tanpa baca penuh',
  !!A.c('stokBahanLiteran').s1 && A.periksa.stokBahanLiteran === true && keadaanK(A, 'stokBahanLiteran').mode === 'delta', J(keadaanK(A, 'stokBahanLiteran')));
ok('B2: tidak ada baca penuh sama sekali (hari kuota sama, rekam dipercaya)', !A.L.some(function (L) { return L.jenis === 'penuh'; }));

// ---- B3 · perangkat lain menulis selagi A terbuka: catatan lama diubah, dibuat ulang sesudah dihapus
B.tulis('penjualan', 'p2', nota('p2', 22000)); tuntas();
ok('B3: catatan LAMA (lahir tanpa cap) diubah lewat /baru/ perangkat lain → sampai seketika (cap jam server baru)', memDok(A, 'penjualan', 'p2').hargaTotal === 22000);
maju(1000); B.tulis('stokBahanLiteran', 's1', { id: 's1', tanggal: '2026-10-07', kg: 9 }); tuntas();
ok('B3: catatan yang dihapus lalu dibuat ULANG (cap lebih baru dari nisannya) tampil lagi', memDok(A, 'stokBahanLiteran', 's1') && memDok(A, 'stokBahanLiteran', 's1').kg === 9, J(memId(A, 'stokBahanLiteran')));
A.tulis('pengeluaranHarian', 'h2', { id: 'h2', tanggal: '2026-10-07', nominal: 1000 }); tuntas();
ok('B3: tulisan perangkat ini sendiri tampil & sampai ke perangkat lain', memId(A, 'pengeluaranHarian').indexOf('h2') >= 0 && memId(B, 'pengeluaranHarian').indexOf('h2') >= 0);

// ---- B4 · jam perangkat MUNDUR 3 hari & MAJU 2 hari: tanda air & hari kuota dari jam SERVER
var C = new Perangkat('hp-mundur', -3 * HR); C.buka();
var D = new Perangkat('hp-maju', 2 * HR); D.buka();
ok('B4: jam perangkat mundur/maju — baca penuh tercatat dengan jam SERVER, tanda air = cap server (bukan jam perangkat)', C.R.k.penjualan.totalPada === S.jam && D.R.k.penjualan.totalPada === S.jam && C.R.k.penjualan.Wt <= S.jam && D.R.k.penjualan.Wt <= S.jam, J([C.R.k.penjualan, D.R.k.penjualan]));
ok('B4: hari kuota perangkat = hari kuota server', C.sesi.keadaan().hari === hbHariKuota(S.jam) && D.sesi.keadaan().hari === hbHariKuota(S.jam), J([C.sesi.keadaan().hari, D.sesi.keadaan().hari, hbHariKuota(S.jam)]));
C.tutup(); D.tutup(); maju(30 * MNT);
C.tulis('penjualan', 'c1', nota('c1', 11000, '2026-10-04')); D.tulis('penjualan', 'd1', nota('d1', 12000)); tuntas();
C.buka(); D.buka();
ok('B4: perangkat berjam maju 2 hari TIDAK kehilangan ubahan perangkat lain (B dari cap server, bukan jam perangkat yang di masa depan); perangkat berjam mundur juga lengkap',
  memId(D, 'penjualan').indexOf('c1') >= 0 && memId(C, 'penjualan').indexOf('d1') >= 0 && samaServer(C) && samaServer(D), J([beda(C), beda(D)]));
ok('B4: nota bertanggal mundur dari HP berjam salah tetap sampai ke Mac (cap = jam server saat diterima)', memId(A, 'penjualan').indexOf('c1') >= 0 && memId(A, 'penjualan').indexOf('d1') >= 0);
C.tutup(); D.tutup(); S.dev = S.dev.filter(function (p) { return p !== C && p !== D; });

// ---- B5 · nota HP kasir LAMA (kasir-v32, tanpa cap)
S.tulis('penjualan', 'k1', nota('k1', 15000), false); tuntas();
ok('B5 tanpa gerbang: nota tanpa cap TIDAK lewat delta (ini sebabnya HP kasir wajib v33)', memId(A, 'penjualan').indexOf('k1') < 0);
maju(31 * MNT); A.sesi.tik(); tuntas();
var kp = keadaanK(A, 'penjualan');
ok('B5: hitungan berkala (30 menit, koleksi HP kasir) melihat server lebih banyak → belum terperiksa, dihitung ulang 15 detik', A.periksa.penjualan === false || kp.bacaJalan || memId(A, 'penjualan').indexOf('k1') >= 0, J(kp));
maju(20 * 1000);
ok('B5: hitungan masih beda → baca penuh penjualan (otomatis, rem berlaku) → nota HP lama masuk, terperiksa lagi', memId(A, 'penjualan').indexOf('k1') >= 0 && A.periksa.penjualan === true && samaServer(A), J([beda(A), keadaanK(A, 'penjualan')]));
// dengan gerbang penulis: denyut HP kasir v32 → penjualan dengar penuh, nota tanpa cap terlihat SEKETIKA
S.perangkat = [{ id: 'hp-kasir', nama: 'HP penjaga', aplikasi: 'darurat', versi: 'kasir-v32', pada: new Date(S.jam - 10 * MNT).toISOString(), akun: 'kasir@x' }]; A.tetap(); tuntas();
ok('B5 gerbang penulis: HP kasir < kasir-v33 berdenyut → penjualan DENGAR PENUH (koleksi lain tetap delta)', keadaanK(A, 'penjualan').mode === 'penuh' && keadaanK(A, 'stokBahanLiteran').mode === 'delta', J(keadaanK(A, 'penjualan')));
S.tulis('penjualan', 'k2', nota('k2', 16000), false); tuntas();
ok('B5 gerbang: nota tanpa cap terlihat seketika & tetap terperiksa', memId(A, 'penjualan').indexOf('k2') >= 0 && A.periksa.penjualan === true);
S.perangkat = [{ id: 'hp-kasir', nama: 'HP penjaga', aplikasi: 'darurat', versi: 'kasir-v33', pada: new Date(S.jam).toISOString(), akun: 'kasir@x' }]; A.tetap(); B.tetap(); tuntas();
ok('B5 gerbang: HP sudah kasir-v33 → kembali dengar ubahan (delta), memori tetap lengkap', keadaanK(A, 'penjualan').mode === 'delta' && samaServer(A) && A.periksa.penjualan === true, J([keadaanK(A, 'penjualan'), beda(A)]));

// ---- B6 · Console mengubah catatan LAMA tanpa cap → pendeteksi baca penuh harian menyentuh → semua perangkat menerimanya
S.tulis('penjualan', 'p1', nota('p1', 99000), 'tetap'); tuntas();
ok('B6: ubahan Console tanpa cap belum terlihat lewat delta (hitungan tetap cocok — batas yang diakui)', memDok(A, 'penjualan', 'p1').hargaTotal === 10000, J(memDok(A, 'penjualan', 'p1')));
// reset kuota: 7 Okt 07.00Z = 14.00 WIB → hari kuota 2026-10-07
var sebelumReset = Z('2026-10-07T06:58:00Z') - S.jam; if (sebelumReset > 0) maju(sebelumReset);
B.gema(); A.gema(); B.sesi.tik(); A.sesi.tik(); tuntas();
ok('B7 jadwal: sebelum 14.00 WIB (hari kuota 6 Okt sudah dibaca penuh) → tidak ada klaim baru', S.klaim.hari === '2026-10-06' && !A.klaimTulis && !B.klaimTulis, J(S.klaim));
maju(Z('2026-10-07T07:05:00Z') - S.jam); B.gema(); B.sesi.tik(); tuntas(); A.gema(); A.sesi.tik(); tuntas();
ok('B7 jadwal: sesudah 14.00 WIB perangkat owner PERTAMA (iPad) mengklaim & membaca penuh untuk toko; Mac TIDAK membaca penuh lagi (per TOKO, bukan per perangkat)',
  S.klaim.hari === '2026-10-07' && S.klaim.perangkat === 'ipad' && !!S.klaim.selesai && B.klaimTulis === 2 && !A.klaimTulis, J([S.klaim, A.klaimTulis, B.klaimTulis]));
ok('B6: pendeteksi (iPad) menemukan p1 berubah tanpa cap → disentuh capServer → Mac menerimanya lewat delta', B.sentuhN >= 1 && memDok(A, 'penjualan', 'p1').hargaTotal === 99000 && memDok(B, 'penjualan', 'p1').hargaTotal === 99000, J([B.sentuhN, memDok(A, 'penjualan', 'p1')]));
// Console menghapus catatan TANPA nisan → pendeteksi menulis nisannya (hari berikutnya)
S.hapus('pengeluaranHarian', 'h1', false); tuntas();
ok('B6: hapus lewat Console tanpa nisan belum terlihat (h1 masih di memori Mac)', memId(A, 'pengeluaranHarian').indexOf('h1') >= 0);
maju(Z('2026-10-08T07:02:00Z') - S.jam); A.gema(); A.sesi.tik(); tuntas(); B.gema(); B.sesi.tik(); tuntas();
ok('B7 jadwal hari berikutnya: perangkat pertama (Mac) mengklaim hari kuota 8 Okt; pendeteksi menulis nisan untuk h1 → iPad ikut menyembunyikannya',
  S.klaim.hari === '2026-10-08' && S.klaim.perangkat === 'mac' && memId(A, 'pengeluaranHarian').indexOf('h1') < 0 && memId(B, 'pengeluaranHarian').indexOf('h1') < 0 && !!S.nisan['pengeluaranHarian|h1'], J([S.klaim, memId(B, 'pengeluaranHarian')]));
// November: reset 15.00 WIB
A.tutup(); B.tutup(); S.dev = S.dev.filter(function (p) { return p !== A && p !== B; });
S.jam = Z('2026-11-01T09:30:00Z'); S.klaim = { id: 'hematHarian', hari: '2026-11-01', perangkat: 'lama', selesai: Z('2026-11-01T07:10:00Z') };
var E = new Perangkat('mac-nov'); E.ls = salin(A.ls); E.buka(); var klaimE0 = E.klaimTulis;
maju(Z('2026-11-02T07:50:00Z') - S.jam); E.gema(); E.sesi.tik(); tuntas(); var klaimE1 = E.klaimTulis;
maju(Z('2026-11-02T08:05:00Z') - S.jam); E.gema(); E.sesi.tik(); tuntas();
ok('B7 November: 2 Nov 14.50 WIB (07.50Z) masih hari kuota 1 Nov → tidak klaim; 15.05 WIB (08.05Z) → klaim hari kuota 2 Nov',
  klaimE1 === klaimE0 && S.klaim.hari === '2026-11-02' && S.klaim.perangkat === 'mac-nov', J([klaimE0, klaimE1, S.klaim]));
ok('B8 perangkat lama tutup > 14 hari (Mac terakhir baca penuh 8 Okt, buka 1 Nov): baca penuh lagi walau simpanannya dipercaya', E.R.k.penjualan.totalPada >= Z('2026-11-01T09:30:00Z') && samaServer(E), J(E.R.k.penjualan));
ok('B8: catatan yang dihapus TANPA nisan selagi perangkat absen ikut terbuang oleh baca penuh (limbo)', !E.c('pengeluaranHarian').h1 && samaServer(E));

// ---- B9 · tab yang turun dari primer: pendengar simpanan berhenti menerima → penjaga hidup BERBUNYI dalam 5 detik
E.vBeku = true; S.tulis('penjualan', 'p9', nota('p9', 9000), true); tuntas(); maju(6000);
ok('B9 pendengar simpanan MATI: ubahan yang dibawa delta tidak terlihat di simpanan 5 detik → koleksi itu mati (tirai muat ulang), tidak terperiksa',
  E.mati.indexOf('penjualan') >= 0 && E.periksa.penjualan === false && E.sesi.adaMati(), J([E.mati, E.periksa.penjualan]));
E.vBeku = false;

// ---- B10 · rem kuota: baca penuh otomatis yang ke-3 hari ini ditunda (gerbang tertutup, layar mengaku), tombol manual menembus
E.tutup(); E.buka(); var H0 = E.R.hari; H0.otomatis.penjualan = 2; E.sesi.bacaPenuh(['penjualan'], 'uji', false); tuntas();
var F0 = new Perangkat('mac-rem'); F0.ls = salin(E.ls); var RR = JSON.parse(F0.ls.miqbal_hemat_v2); RR.isi['proyek-uji|uid-owner'].k.penjualan.gen = 'beda'; F0.ls.miqbal_hemat_v2 = J(RR);
RR.isi['proyek-uji|uid-owner'].hari = { H: hbHariKuota(S.jam), otomatis: { penjualan: 2 }, mulai: { penjualan: 2 }, baca: 0 }; F0.ls.miqbal_hemat_v2 = J(RR);
F0.buka(); var kr = keadaanK(F0, 'penjualan');
ok('B10 rem: baca penuh OTOMATIS ke-3 untuk koleksi yang sama hari ini ditunda → koleksi belum terperiksa, sebabnya disebut ("menunggu kuota besok")', !kr.terperiksa && /kuota besok/.test(kr.wajibTotal) && !F0.L.some(function (L) { return L.aktif && L.jenis === 'penuh'; }), J(kr));
F0.sesi.bacaPenuh(['penjualan'], 'tombol'); tuntas();
ok('B10 rem: tombol "Baca penuh sekarang" menembus rem → terperiksa', keadaanK(F0, 'penjualan').terperiksa === true, J(keadaanK(F0, 'penjualan')));

// ---- B11 · uang-kritis: hitungan segar ≤ 2 menit; offline → ditolak dengan kalimat; katalog: gerbang tertutup saat hitungan galat
var US = null; F0.sesi.pastikanSegar().then(function (r) { US = r; }); tuntas();
ok('B11 uang-kritis: tersambung & cocok → boleh (hitungan server segar)', US && US.ok === true, J(US));
F0.putus(); tuntas(); maju(3 * MNT); var US2 = null; F0.sesi.pastikanSegar().then(function (r) { US2 = r; }); tuntas();
ok('B11 uang-kritis: tanpa internet → DITOLAK "sambungkan internet" (draf tetap di layar)', US2 && !US2.ok && /internet/.test(US2.pesan), J(US2));
ok('B11 katalog: tanpa internet / belum terperiksa → gerbang katalog TERTUTUP', F0.sesi.bolehKatalog().boleh === false, J(F0.sesi.bolehKatalog()));
F0.sambung(); tuntas();
ok('B11 katalog: tersambung & semua terperiksa & hitungan koleksi HP kasir ≤ 35 menit → gerbang terbuka', F0.sesi.bolehKatalog().boleh === true, J(F0.sesi.bolehKatalog()));
maju(36 * MNT); var KL = F0.sesi.bolehKatalog(); F0.sesi.tik(); tuntas(); var KL2 = F0.sesi.bolehKatalog();
ok('B11 katalog: hitungan koleksi HP kasir lebih dari 35 menit (tab tidak berdetak) → gerbang TERTUTUP; hitungan berkala segar lagi → terbuka', KL.boleh === false && /35 menit/.test(KL.sebab) && KL2.boleh === true, J([KL, KL2]));
S.tulis('penjualan', 'k3', nota('k3', 17000), false); tuntas(); var US3 = null; maju(3 * MNT); F0.sesi.pastikanSegar().then(function (r) { US3 = r; }); tuntas();
ok('B11 uang-kritis: hitungan server BEDA (nota tanpa cap) → DITOLAK "belum cocok — sedang dibaca ulang" dan koleksinya dibaca penuh', US3 && !US3.ok && /belum cocok/.test(US3.pesan), J(US3));
maju(20000);
ok('B11: sesudah dibaca ulang nota itu masuk', memId(F0, 'penjualan').indexOf('k3') >= 0, J(beda(F0)));

print(J({ lulus: lulus, gagal: gagal }));
"""

# ---------------------------------------------------------------------------------------------------------------------------------------------------
SDK_PALSU = r"""
var __rek = { dengar: [], tulis: [], init: null, cacheOpsi: null };
var __timer = []; var setTimeout = function (f, ms) { __timer.push({ f: f, ms: ms }); return __timer.length; }; var clearTimeout = function () {};
function initializeApp(c) { return { c: c }; } function initializeFirestore(a, o) { __rek.init = o; return { palsu: true }; }
function persistentLocalCache(o) { __rek.cacheOpsi = o; return { cache: o }; } function persistentMultipleTabManager() { return { tab: 'banyak' }; }
function collection(db, nama) { return { jenis: 'koleksi', nama: nama }; } function doc(db, nama, id) { return { jenis: 'dok', nama: nama, id: String(id) }; }
function query(c) { var q = { jenis: 'kueri', nama: c.nama, syarat: [] }; for (var i = 1; i < arguments.length; i++) q.syarat.push(arguments[i]); return q; }
function where(f, op, v) { return { where: [f, op, v] }; } function orderBy(f, a) { return { orderBy: [f, a] }; } function limit(n) { return { limit: n }; }
function onSnapshot(ref, a, b, c) { var opsi = a && typeof a === 'object' ? a : null; var cb = typeof a === 'function' ? a : b; var L = { ref: ref, opsi: opsi, cb: cb, aktif: true }; __rek.dengar.push(L); return function () { L.aktif = false; }; }
function writeBatch() { var ops = []; return { set: function (r, d) { ops.push(['set', r.nama, r.id, d]); }, update: function (r, d) { ops.push(['update', r.nama, r.id, d]); }, delete: function (r) { ops.push(['delete', r.nama, r.id]); },
  commit: function () { __rek.tulis.push(ops); return __rek.tahan ? new Promise(function () {}) : Promise.resolve(); } }; }
function setDoc(r, d) { __rek.tulis.push([['set', r.nama, r.id, d]]); return Promise.resolve(); }
function serverTimestamp() { return { __sentinel: 'serverTimestamp' }; }
var Timestamp = { fromMillis: function (ms) { return { toMillis: function () { return ms; } }; } };
var CACHE_SIZE_UNLIMITED = -1;
function getDocs() { return Promise.resolve({ forEach: function () {} }); } function getDocsFromServer() { return Promise.resolve({ docs: [] }); }
function getCountFromServer() { return Promise.resolve({ data: function () { return { count: 0 }; } }); } function waitForPendingWrites() { return Promise.resolve(); } function terminate() { return Promise.resolve(); }
function getAuth() { return {}; } function signInWithEmailAndPassword() { return Promise.reject({}); } function onAuthStateChanged() {} function setPersistence() { return Promise.resolve(); } var browserLocalPersistence = {}; function signOut() { return Promise.resolve(); }
"""

SKENARIO_FB = r"""
var CAP = function (d) { return !!(d && d.capServer && d.capServer.__sentinel === 'serverTimestamp'); };
db = { palsu: true }; auth = { currentUser: { email: 'owner@tokoberasmiqbal.web.app', uid: 'uid-owner' } };
status.akun = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null); status.masuk = true;
if (__MODE === 'mati') {
  // ---- C1 · saklar MATI: pendengar persis sebelum 7 Okt
  ok('C1 saklar bawaan MATI (tidak ada di penyimpanan)', hematNyala() === false);
  pasangPendengar(status.akun);
  var D = __rek.dengar.filter(function (L) { return L.aktif; });
  var kol = D.filter(function (L) { return L.ref.jenis !== 'dok'; });
  ok('C1 mati: SATU pendengar server per koleksi (' + KOLEKSI.length + ') + dokumen katalog kasir — tanpa source "cache", tanpa where capServer, tanpa limit 1.000.000',
    kol.length === KOLEKSI.length && D.length === KOLEKSI.length + 1 && D.every(function (L) { return !(L.opsi && L.opsi.source === 'cache'); })
    && kol.every(function (L) { var s = L.ref.syarat || []; return L.ref.jenis === 'koleksi' || (L.ref.nama === 'logAktivitas' && J(s) === J([{ orderBy: ['pada', 'desc'] }, { limit: 150 }])); }), J(D.map(function (L) { return [L.ref.nama, L.ref.jenis, L.opsi]; }).slice(0, 8)));
  // snapshot server berisi capServer → memori TANPA capServer, cap di peta samping
  var Lp = kol.find(function (L) { return L.ref.nama === 'penjualan'; });
  var ts = { toMillis: function () { return 1759806000000; } };
  var docsP = [{ id: 'n1', data: function () { return { id: 'n1', tanggal: '2026-10-07', hargaTotal: 1000, capServer: ts }; }, metadata: { hasPendingWrites: false } }];
  Lp.cb({ metadata: { fromCache: false }, forEach: function (f) { docsP.forEach(f); } });
  ok('C1 kupas: dokumen di memori TANPA capServer (mesin, cadangan, katalog tidak pernah melihatnya); nilai cap di peta samping', cacheMentah('penjualan').length === 1 && !('capServer' in cacheMentah('penjualan')[0]) && _cap.penjualan.n1 === 1759806000000);
  ok('C1 mati: simpanan Firestore bawaan (tanpa cacheSizeBytes) — sama dengan sebelum 7 Okt', __rek.cacheOpsi === null || !('cacheSizeBytes' in (__rek.cacheOpsi || {})));
  // ---- C2 · tulisBerkas (aturan v7 BELUM terbukti): cap koleksi hemat saja, tanpa batu nisan
  __rek.tulis = []; var tb = null; __rek.tahan = true;   // server belum mengaku → salinan antre masih ada untuk diperiksa
  tulisBerkas([{ koleksi: 'penjualan', data: { id: 'n2', tanggal: '2026-10-07', hargaTotal: 2000 } }, { koleksi: 'tutupBukuAcara', data: { id: '2026', tahun: 2026, status: 'berjalan' } },
    { koleksi: 'pesanan', data: { id: 'ps1', status: 'baru' } }, { koleksi: 'aturanToko', data: { id: 'struk', a: 1 } }, { koleksi: 'ringkasanKasir', data: { id: 'aktif', kemasan: [] } }],
    [{ koleksi: 'stokBahanLiteran', id: 's9' }, { koleksi: 'aturanToko', id: 'lama' }]).then(function (r) { tb = r; }); drainMicrotasks();
  var ops = __rek.tulis[0] || []; var op = function (jenis, nama, id) { return ops.find(function (o) { return o[0] === jenis && o[1] === nama && o[2] === id; }); };
  ok('C2 tulisBerkas: koleksi HEMAT bercap jam server; berita acara tutup buku, pesanan, setelan, katalog kasir, baris jejak TIDAK bercap',
    CAP(op('set', 'penjualan', 'n2')[3]) && !CAP(op('set', 'tutupBukuAcara', '2026')[3]) && !CAP(op('set', 'pesanan', 'ps1')[3]) && !CAP(op('set', 'aturanToko', 'struk')[3]) && !CAP(op('set', 'ringkasanKasir', 'aktif')[3])
    && ops.filter(function (o) { return o[1] === 'logAktivitas'; }).every(function (o) { return !CAP(o[3]); }), J(ops.map(function (o) { return [o[0], o[1], o[2], CAP(o[3])]; })));
  ok('C2: aturan v7 BELUM terbukti di perangkat ini → hapus TANPA batu nisan (persis sebelum 7 Okt — aman bila rules v6 masih terbit)', !ops.some(function (o) { return o[1] === 'batuNisan'; }) && !!op('delete', 'stokBahanLiteran', 's9'));
  var salinan = JSON.parse(__ls.miqbal_baru_antre_v1 || '[]'); var sal = (salinan[salinan.length - 1] || {}).dokumen || [];
  ok('C2: salinan antre lokal TANPA sentinel cap (bisa ditulis ulang / dibandingkan apa adanya)', sal.length >= 1 && sal.every(function (x) { return !('capServer' in (x.data || {})); }), J(sal).slice(0, 300));
  // ---- C3 · aturan v7 terbukti: batu nisan di batch YANG SAMA dengan hapusnya (koleksi hemat saja)
  _nisanSah = true; __rek.tulis = [];
  tulisBerkas([], [{ koleksi: 'stokBahanLiteran', id: 's10' }, { koleksi: 'aturanToko', id: 'lama2' }]); drainMicrotasks();
  var ops3 = __rek.tulis[0] || []; var nis = ops3.find(function (o) { return o[1] === 'batuNisan'; });
  ok('C3 aturan v7 terbukti: hapus koleksi hemat + batu nisan "<koleksi>|<id>" bercap jam server di batch yang sama; hapus koleksi tetap tanpa nisan',
    !!nis && nis[2] === 'stokBahanLiteran|s10' && CAP(nis[3]) && nis[3].koleksi === 'stokBahanLiteran' && nis[3].idDok === 's10' && nis[3].olehUid === 'uid-owner' && ops3.filter(function (o) { return o[1] === 'batuNisan'; }).length === 1, J(ops3));
  __rek.tulis = []; perbaruiBerkas([[{ koleksi: 'pelangganCatatan', id: 'pc1', kolom: { ciri: [] } }, { koleksi: 'aturanToko', id: 'pelanggan', kolom: { ciri: [] } }]], 'uji'); drainMicrotasks();
  var ops4 = __rek.tulis[0] || [];
  ok('C3 perbaruiBerkas (bersihkan ciri): ubah kolom koleksi hemat bercap, setelan tidak', CAP(ops4[0][3]) && !CAP(ops4[1][3]) && ops4[0][3].ciri !== undefined, J(ops4));
  __rek.tulis = []; pulihkanBerkas('2025', [{ koleksi: 'penjualan', idAsli: 'old1', dok: { id: 'old1', tanggal: '2025-12-31' } }]); drainMicrotasks();
  var ops5 = __rek.tulis[0] || [];
  ok('C3 pulihkanBerkas (batal tutup buku): catatan yang dikembalikan bercap jam server BARU, isinya tetap', CAP(ops5[0][3]) && ops5[0][3].tanggal === '2025-12-31', J(ops5));
  // ---- C4 · denyut
  __rek.tulis = []; kirimDenyut(true); var dn = (__rek.tulis[0] || [])[0];
  ok('C4 denyut owner: versi baru-c1 (kode bercap) + capServer (gema jam server)', dn && dn[3].versi === 'baru-c1' && CAP(dn[3]) && !('hemat' in dn[3]), J(dn));
} else {
  // ---- C5 · saklar NYALA (owner, aturan v7 terbukti, memegang kunci tab): koleksi hemat lewat simpanan perangkat, koleksi tetap penuh
  ok('C5 saklar nyala terbaca dari penyimpanan perangkat', hematNyala() === true);
  _nisanSah = true; _kunciTab.ambil();
  pasangPendengar(status.akun);
  var D5 = __rek.dengar.filter(function (L) { return L.aktif; });
  var vV = D5.filter(function (L) { return L.opsi && L.opsi.source === 'cache'; }); var penuh = D5.filter(function (L) { return L.ref.jenis !== 'dok' && !(L.opsi && L.opsi.source === 'cache'); });
  ok('C5 nyala: tiap koleksi HEMAT punya pendengar SIMPANAN (source cache); koleksi tetap & jejak tetap pendengar server penuh; tidak ada pendengar server penuh atas koleksi hemat',
    vV.length === hbKoleksiHemat().length && penuh.map(function (L) { return L.ref.nama; }).sort().join(',') === KOLEKSI.filter(function (k) { return k.kelas; }).map(function (k) { return k.nama; }).sort().join(','),
    J({ v: vV.length, penuh: penuh.map(function (L) { return L.ref.nama; }) }));
  ok('C5 nyala: simpanan Firestore TANPA GC (cacheSizeBytes = CACHE_SIZE_UNLIMITED) — tidak bisa diuji sesudah mulai(); diperiksa statis', true);
  // gema jam server: denyut LAMA (dari sesi sebelumnya) TIDAK dipakai; denyut yang dikirim sesi ini dan diakui server → selisih jam server − jam perangkat
  var Lps = D5.find(function (L) { return L.ref.nama === 'perangkatStatus'; }); var idP = idPerangkat();
  var snapP = function (pada, ms) { return { metadata: { fromCache: false }, forEach: function (f) { f({ id: idP, data: function () { return { id: idP, pada: pada, aplikasi: 'baru', versi: 'baru-c1', capServer: { toMillis: function () { return ms; } } }; }, metadata: { hasPendingWrites: false } }); } }; };
  Lps.cb(snapP('2026-10-01T00:00:00.000Z', 1000)); var skew0 = _hemat._G.skew;
  kirimDenyut(true); Lps.cb(snapP(_denyutKirim.pada, _denyutKirim.ms + 777));
  ok('C7 gema jam server: denyut lama (sesi sebelumnya, cap berjam-jam lalu) TIDAK dipakai; denyut sesi ini yang diakui server → selisih jam = cap − jam kirim', skew0 === null && _hemat._G.skew === 777, J([skew0, _hemat._G.skew]));
  ok('C7: memori denyut tanpa capServer (dikupas)', !('capServer' in (cacheMentah('perangkat')[0] || {})));
  // uang-kritis & kunci tab di penulis pusat
  var asli = _hemat; _hemat = { pastikanSegar: function () { return Promise.resolve({ ok: false, pesan: 'data penjualan belum cocok dengan server — uji' }); }, adaMati: function () { return false; }, catatHapus: function () {}, keadaan: asli.keadaan, ringkasDenyut: asli.ringkasDenyut };
  var u1 = null, u2 = null; __rek.tulis = [];
  tulisBerkas([{ koleksi: 'tutupHari', data: { id: '2026-10-07', tanggal: '2026-10-07' } }], []).then(function (r) { u1 = r; }); drainMicrotasks();
  tulisBerkas([{ koleksi: 'penjualan', data: { id: 'n5', tanggal: '2026-10-07', hargaTotal: 5000 } }], []).then(function (r) { u2 = r; }); drainMicrotasks();
  ok('C6 uang-kritis: tutup hari saat hitungan server belum segar → DITOLAK dengan kalimatnya, tidak ada yang dikirim; nota biasa tetap jalan',
    u1 && u1.gagal && /belum cocok/.test(u1.pesan) && u2 && !u2.gagal && __rek.tulis.length === 1 && __rek.tulis[0][0][1] === 'penjualan', J([u1, u2, __rek.tulis.length]));
  __ls[HB_KUNCI_TAB] = J({ sesi: 'tab-lain', detak: Date.now() }); var u3 = null;
  tulisBerkas([{ koleksi: 'penjualan', data: { id: 'n6', tanggal: '2026-10-07', hargaTotal: 6000 } }], []).then(function (r) { u3 = r; }); drainMicrotasks();
  ok('C6 kunci tab: tab yang KALAH (tab lain menekan "Pakai di sini") tidak menulis apa pun', u3 && u3.gagal && /tab lain/.test(u3.pesan), J(u3));
  _hemat = asli;
}
print(J({ lulus: lulus, gagal: gagal }));
"""


def fungsi(teks, nama):
    m = re.search(r'\n(?:export )?(?:async )?function ' + nama + r'\([^)]*\) \{.*?\n\}\n', teks, re.S); return m.group(0) if m else ''


# ---------- D · STATIS: setiap jalan tulis SDK membawa capServer atau tercatat sengaja tanpa cap ----------
TULIS = re.compile(r'\b(setDoc|updateDoc|addDoc)\(|\bb\.(set|update)\(')
# (pola baris, alasan) — tulisan SENGAJA tanpa cap: koleksinya bukan hemat (didengar penuh / tidak didengar), atau bentuknya dikunci aturan lain
TANPA_CAP = [
    (r"if \(kkMentah\(x\.koleksi\)\) \{ b\.set\(doc\(db, x\.koleksi, String\(x\.data\.id\)\), x\.data\)", 'katalog kasir (ringkasanKasir): bentuk dokumen beku = sistem lama, didengar sebagai satu dokumen'),
    (r"b\.set\(doc\(db, KOLEKSI_LOG, ", 'jejak logAktivitas: kelas jejak (pendengar berbatas 150, tidak lewat delta)'),
    (r"setDoc\(doc\(db, 'permintaanAkses', ", 'permintaanAkses: kelas tetap; rules keys().hasOnly menolak kolom lain'),
    (r"setDoc\(doc\(db, KK_KOLEKSI, KK_ID\), kkDokumen\(isi, kini\)\)", 'katalog kasir: bentuk dokumen beku (uji_katalog_kasir)'),
    (r"setDoc\(doc\(db, KOLEKSI_PERANGKAT, id\), isi\)", 'denyut perangkatStatus: kelas tetap; staf dibatasi keys().hasOnly — owner menambah capServer (gema jam server)'),
    (r"b\.set\(doc\(db, KOLEKSI_ARSIP, ", 'arsipTahun: tidak didengar (dibaca sekali saat batal tutup buku)'),
    (r"klaim: \(dok\) => setDoc\(doc\(db, 'aturanToko', HB_ID_KLAIM\), dok\)", 'aturanToko/hematHarian: kelas tetap (didengar penuh semua perangkat owner)'),
]
DENGAN_CAP = ['pasangCap(', 'capServer: serverTimestamp()', 'nisanDok(']
KOLEKSI_KONSTAN = {'KOLEKSI_LOG': 'logAktivitas', 'KOLEKSI_PERANGKAT': 'perangkatStatus', 'KOLEKSI_ARSIP': 'arsipTahun', 'KK_KOLEKSI': 'ringkasanKasir'}


def statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    kol = t['baru/js/data/koleksi.js']; kelas = {}
    for m in re.finditer(r"\{ nama: '(\w+)',([^}]*)\}", kol): km = re.search(r"kelas: '(\w+)'", m.group(2)); kelas[m.group(1)] = km.group(1) if km else 'hemat'
    for nama, kls in (('logAktivitas', 'jejak'), ('perangkatStatus', 'tetap'), ('aturanToko', 'tetap'), ('permintaanAkses', 'tetap'), ('pesanan', 'tetap'), ('tutupBukuAcara', 'tetap')):
        ok('koleksi.js: %s kelas %s (tidak dicap, didengar penuh)' % (nama, kls), kelas.get(nama) == kls, kelas.get(nama))
    ok('koleksi.js: ringkasanKasir & arsipTahun & batuNisan bukan koleksi yang didengar', all(n not in kelas for n in ('ringkasanKasir', 'arsipTahun', 'batuNisan')))
    # setiap situs tulis di baru/js
    situs = []
    for p, teks in sorted(t.items()):
        if not p.startswith('baru/js/') or '/mesin/' in p: continue
        for i, baris in enumerate(teks.split('\n')):
            for m in TULIS.finditer(baris):
                situs.append((p, i + 1, baris.strip()))
    liar = []
    for p, n, baris in situs:
        if p != 'baru/js/data/firebase.js': liar.append('%s:%d tulis SDK di luar penulis pusat: %s' % (p, n, baris[:140])); continue
        if any(x in baris for x in DENGAN_CAP): continue
        alasan = next((a for pola, a in TANPA_CAP if re.search(pola, baris)), None)
        if not alasan: liar.append('%s:%d tulis tanpa capServer & tanpa alasan tercatat: %s' % (p, n, baris[:160]))
    ok('SETIAP jalan tulis SDK di /baru/ (%d situs) membawa capServer atau tercatat sengaja tanpa cap beserta alasannya; tidak ada tulis SDK di luar firebase.js' % len(situs), not liar and len(situs) >= 14, liar)
    fb = t['baru/js/data/firebase.js']
    ok('pasangCap hanya untuk koleksi HEMAT (hbHemat), nisanDok selalu capServer jam server', "const pasangCap = (koleksi, d) => (hbHemat(koleksi) ? Object.assign({}, d, { capServer: serverTimestamp() }) : d);" in fb
       and re.search(r"const nisanDok = \(koleksi, id, uid\) => \(\{ id: nisanId\(koleksi, id\), koleksi, idDok: String\(id\), capServer: serverTimestamp\(\), olehUid: uid \}\);", fb))
    tb = fungsi(fb, 'tulisBerkas')
    ok('tulisBerkas: cap dipasang SESUDAH penjaga kiriman; salinan antre (`ditulis`) tanpa sentinel; batu nisan di batch yang sama hanya bila aturan v7 terbukti; penjaga tab & uang-kritis sebelum batch',
       tb.find('periksaKiriman(akun, isi, H') < tb.find("b.set(doc(db, x.koleksi, String(d.id)), pasangCap(x.koleksi, d)); ditulis.push({ koleksi: x.koleksi, data: d });") and 'const pakaiNisan = _nisanSah && ' in tb
       and 'if (pakaiNisan && hbHemat(x.koleksi)) b.set(doc(db, HB_KOLEKSI_NISAN' in tb and tb.find('jagaTulisHemat()') < tb.find('const b = writeBatch(db)') and tb.find('kirimanUangKritis(daftar)') < tb.find('const b = writeBatch(db)'), tb[:200])
    mu = fungsi(fb, 'mulai')
    ok('simpanan Firestore TANPA GC hanya saat saklar nyala (pendengar simpanan tidak menahan dokumennya); mati = bawaan', "const cacheOpsi = { tabManager: persistentMultipleTabManager() }; if (_hematNyala) cacheOpsi.cacheSizeBytes = CACHE_SIZE_UNLIMITED;" in mu
       and 'persistentLocalCache(cacheOpsi)' in mu)
    ph = fungsi(fb, 'pasangHemat')
    ok('adaptor sesi hemat: V = simpanan (source cache), S = where capServer > B (jam server), F = kueri SENDIRI limit(HB_LIMIT_F) (bukan collection polos — tidak "selesai" dari view lama), N = batu nisan capServer > Bn, hitungan = getCountFromServer',
       "cache: (k, cb, galat) => dengar(collection(db, k), { source: 'cache', includeMetadataChanges: true }, cb, galat)" in ph and "const lewat = (B) => where('capServer', '>', Timestamp.fromMillis(B));" in ph
       and "penuh: (k, cb, galat) => dengar(query(collection(db, k), limit(HB_LIMIT_F)), { includeMetadataChanges: true }, cb, galat)" in ph and "nisan: (B, cb, galat) => dengar(query(collection(db, HB_KOLEKSI_NISAN), lewat(B))" in ph
       and 'getCountFromServer(collection(db, k))' in ph, ph[:300])
    pp = fungsi(fb, 'pasangPendengar')
    ok('pasangPendengar: kupas SEBELUM pasok (pendengar penuh & per dokumen staf); jalur hemat hanya saklar nyala + owner + aturan v7 + kunci tab',
       "snap.forEach((d) => { const x = d.data(); capK[d.id] = hbKupas(x); daftar.push(x);" in pp and "const x = snap.data(); hbKupas(x); perDok[p.nama][id] = x;" in pp
       and "const hemat = _hematNyala && akun.jenis === 'owner' && _nisanSah && !_berhenti && _kunciTab.milik();" in pp, pp[:200])
    ok('cabutPendengar: pendengar simpanan yang mati → muat ulang (bukan unlisten — SDK 10.13 TypeError)', 'if (_hemat && _hemat.adaMati() && typeof location !== \'undefined\' && location.reload) { location.reload(); return; }' in fungsi(fb, 'cabutPendengar'))
    ok('katalog kasir: gerbang tambahan hemat (gerbangHemat) ikut kkBolehTerbit — satu penilai untuk terbit otomatis & kkSertakan', 'hemat: gerbangHemat() });' in fungsi(fb, 'gerbangKatalog')
       and "if (k.hemat && !k.hemat.boleh) return" in t['baru/js/data/katalog-kasir.js'])
    # kasir darurat
    d = t['kasir-darurat-nominal.html']; ks = d[d.find('var kirimSatu = function () {'):d.find('kirimSatu();\n}', d.find('var kirimSatu = function () {'))]
    ok('kasir darurat: nota (penjualan) lewat REST :commit + updateTransforms capServer = REQUEST_TIME, TANPA updateMask (ditimpa utuh seperti PATCH dulu); koleksi lain tetap PATCH',
       "var URL_COMMIT = 'https://firestore.googleapis.com/v1/projects/' + PROYEK + '/databases/(default)/documents:commit';" in d and "var bercap = item.koleksi === 'penjualan';" in ks
       and "updateTransforms: [{ fieldPath: 'capServer', setToServerValue: 'REQUEST_TIME' }]" in ks and "method: 'POST'" in ks and "method: 'PATCH'" in ks and not re.search(r'updateMask\s*:', d)
       and "fetch(bercap ? URL_COMMIT + '?key=' + KUNCI_API : DASAR + item.koleksi" in ks, ks[:200])
    kd = d[d.find('function kirimDenyutD() {'):d.find('function ambilAntrean()')]
    ok('kasir darurat: denyut TETAP PATCH ke perangkatStatus (tanpa cap, tanpa antrean)', "denganAuth({ method: 'PATCH'" in kd and "'perangkatStatus/'" in kd and 'commit' not in kd)
    vs = re.search(r"const VERSI = '([^']+)';", t['sw-kasir.js']); va = re.search(r"var VERSI_APLIKASI = '([^']+)';", d); kk = re.search(r"export const KK_VERSI_KASIR_TERBARU = '([^']+)';", t['baru/js/data/katalog-kasir.js'])
    hc = re.search(r"export const HB_VERSI_KASIR_CAP = '([^']+)';", t['baru/js/data/hemat-baca.js'])
    nilai = [x.group(1) if x else None for x in (vs, va, kk, hc)]
    ok('rantai versi: sw-kasir VERSI = VERSI_APLIKASI = KK_VERSI_KASIR_TERBARU = HB_VERSI_KASIR_CAP = kasir-v33 (gerbang penulis mengenali HP yang sudah mengecap)', nilai == ['kasir-v33'] * 4, nilai)
    ap = t['baru/js/app.js']; mf = fungsi(ap, 'mulaiFirebase'); jk = fungsi(ap, 'jagaKunciTab')
    kunci_tab = re.search(r"export const HB_KUNCI_TAB = '([^']+)';", t['baru/js/data/hemat-baca.js'])
    ok('app.js: saklar MATI → Firebase dimulai persis seperti sebelumnya; NYALA → kunci tab diambil SEBELUM Firebase dimulai, tab kedua ditanya "Pakai di sini"',
       "if (!fb.hematNyala()) { fb.mulai(gambarAkun); return; }" in mf and "const pakai = () => { kt.ambil(); jagaKunciTab(kt); fb.mulai(gambarAkun); };" in mf and "if (kt.keadaan() !== 'lain') return pakai();" in mf
       and 'if (!hematMatiDariAlamat) mulaiFirebase();' in ap and 'fb.mulai(gambarAkun)' not in ap.replace(mf, ''), mf[:200])
    ok('app.js: tab yang kalah kunci (storage / terlihat lagi / detak gagal) menghentikan Firestore-nya (fb.berhenti) dan menyuruh muat ulang; pagehide melepas kunci; ?hemat=mati mematikan saklar',
       bool(kunci_tab) and "e.key === '" + kunci_tab.group(1) + "'" in jk and 'fb.berhenti(' in jk and "window.addEventListener('pagehide'" in jk and "setInterval(() => { if (!kalah && !dilepas && !kt.detak()) cek(); }, 4000);" in jk
       and "if (hematMatiDariAlamat) { fb.setelSaklarHemat(false); location.replace(location.pathname); }" in ap, jk[:200])
    ok('saklar bawaan MATI: hbSaklar hanya "nyala" yang tersimpan', "export function hbSaklar(penyimpan) { try { return penyimpan.baca(HB_KUNCI_SAKLAR) === 'nyala'; } catch (e) { return false; } }" in t['baru/js/data/hemat-baca.js'])
    return out


SDK_URL = 'https://www.gstatic.com/firebasejs/10.13.0/'


def tautan_modul(t):
    """SEMUA modul /baru/ yang terjangkau dari app.js DIURAI & DITAUTKAN jsc sebagai modul ES (impor URL Firebase → modul palsu yang mengekspor tepat nama
    yang diimpor). SyntaxError (mis. komentar // yang menelan sisa baris — 7 Okt: TAB_SISTEM menu.js) atau nama impor yang tidak diekspor = GAGAL.
    Galat saat DIJALANKAN (DOM tidak ada di jsc) bukan urusan pemeriksaan ini."""
    import shutil
    d = tempfile.mkdtemp()
    try:
        for p, isi in t.items():
            if not p.startswith('baru/js/'): continue
            tujuan = os.path.join(d, p); os.makedirs(os.path.dirname(tujuan), exist_ok=True)
            for m in re.finditer(r"import \{([^}]*)\}\s*from '" + re.escape(SDK_URL) + r"([\w-]+\.js)';", isi):
                nama = [x.strip() for x in m.group(1).split(',') if x.strip()]
                palsu = os.path.join(d, '_palsu', m.group(2)); os.makedirs(os.path.dirname(palsu), exist_ok=True)
                lama = open(palsu).read() if os.path.exists(palsu) else ''
                open(palsu, 'w').write(lama + ''.join('export const %s = () => {};\n' % n for n in nama if 'const %s ' % n not in lama))
            naik = '/'.join(['..'] * (p.count('/') - 0))
            isi = isi.replace(SDK_URL, naik + '/_palsu/')
            open(tujuan, 'w', encoding='utf-8').write(isi)
        open(os.path.join(d, 'baru', 'masuk.js'), 'w').write("import * as A from './js/app.js';\n")
        r = subprocess.run([JSC, '-m', os.path.join(d, 'baru', 'masuk.js')], capture_output=True, text=True, cwd=os.path.join(d, 'baru'))
        keluaran = (r.stdout or '') + (r.stderr or '')
        return 'SyntaxError' not in keluaran and 'not found' not in keluaran, keluaran.strip()[-400:]
    finally:
        shutil.rmtree(d, ignore_errors=True)


def utama(t):
    hasil = statis(t)
    ok_t, ket_t = tautan_modul(t)
    hasil.append(('statis · semua modul /baru/ dari app.js terurai & tertaut di jsc (modul ES, SDK palsu) — tanpa SyntaxError / impor yang tidak diekspor', ok_t, ket_t))
    js = bundel(t, MURNI)
    h, e = jalan(ALAT + js + '\n' + SKENARIO_MURNI)
    if h is None: hasil.append(('jsc A+B (murni + server mainan) jalan', False, e))
    else: hasil += [('A/B · ' + str(i), True, '') for i in range(h['lulus'])] + [('A/B · ' + g, False, '') for g in h['gagal']]
    for mode in ('mati', 'nyala'):
        pra = "var __MODE = '" + mode + "';\n" + ("__ls['miqbal_hemat_saklar_v1'] = 'nyala';\n" if mode == 'nyala' else '')
        js2 = bundel(t, _M)
        js2 = js2.replace(bundel_baru.PRELUDE, bundel_baru.PRELUDE + SDK_PALSU + pra, 1)
        h, e = jalan(ALAT + js2 + '\n' + SKENARIO_FB)
        if h is None: hasil.append(('jsc C (firebase.js, saklar ' + mode + ') jalan', False, e))
        else: hasil += [('C ' + mode + ' · ' + str(i), True, '') for i in range(h['lulus'])] + [('C ' + mode + ' · ' + g, False, '') for g in h['gagal']]
    return hasil


def rusak(t, ganti):
    t = dict(t)
    for b, gs in ganti.items():
        for lama, baru in gs:
            assert lama in t[b], 'kontrol basi: ' + b + ' · ' + lama[:90]
            t[b] = t[b].replace(lama, baru)
    return t


HB = 'baru/js/data/hemat-baca.js'; FB = 'baru/js/data/firebase.js'; KD = 'kasir-darurat-nominal.html'
KONTROL = [
    ('(a) delta mendengar diubahPada (jam HP), bukan capServer', {FB: [("const lewat = (B) => where('capServer', '>', Timestamp.fromMillis(B));", "const lewat = (B) => where('diubahPada', '>', new Date(B).toISOString());")]}),
    ('(b) baca penuh = collection(k) polos (berbagi view simpanan — "selesai" tanpa server)', {FB: [("penuh: (k, cb, galat) => dengar(query(collection(db, k), limit(HB_LIMIT_F)),", "penuh: (k, cb, galat) => dengar(collection(db, k),")]}),
    ('(c) batu nisan tanpa banding cap → catatan yang dibuat ulang tetap tersembunyi', {HB: [("!(typeof d.cap === 'number' && typeof t === 'number' && d.cap > t)) n += 1;", ") n += 1;")]}),
    ('(d) Bn = 0 bila Wt kosong (seluruh riwayat nisan dibaca tiap buka)', {HB: [("  return c.length ? Math.min.apply(null, c) : null;\n}", "  return c.length ? Math.min.apply(null, c) : 0;\n}"), ("if (hbAngka(kiniS) > 0) c.push(kiniS - HB_MARGIN_MS);", "")]}),
    ('(e) tanda air dari jam PERANGKAT (bukan cap server)', {HB: [("Object.assign(r, { Wt: hbJepit(st.fMaks, s), n: st.fN, totalPada: s,", "Object.assign(r, { Wt: jam(), n: st.fN, totalPada: s,")]}),
    ('(f) jepit + 10 menit dibuang (cap 2099 membekukan delta)', {HB: [("const c = hbAngka(capMaks); if (c === null) return kiniS; return Math.min(c, kiniS + HB_JEPIT_MS);", "const c = hbAngka(capMaks); if (c === null) return kiniS; return c;")]}),
    ('(g) hari kuota selalu UTC−7 (reset 15.00 WIB sesudah 1 Nov terlewat)', {HB: [("export function hbMusimPanasAS(ms) { const y = new Date(ms).getUTCFullYear(); return ms >= hbMingguKe(y, 2, 2, 10) && ms < hbMingguKe(y, 10, 1, 9); }", "export function hbMusimPanasAS(ms) { return true; }")]}),
    ('(h) hitungan server tanpa mengurangi yang tersembunyi nisan', {HB: [("const lokal = (h.mentah || 0) - (h.tersembunyi || 0);", "const lokal = (h.mentah || 0);")]}),
    ('(i) siap (tirai terangkat) dari simpanan KOSONG', {HB: [("if (d.ya) siapK(k); else if (!G.online)", "if (true) siapK(k); else if (!G.online)")]}),
    ('(j) capServer tidak dikupas (masuk memori, cadangan, katalog)', {HB: [("cap = hbCapMs(x.capServer); delete x.capServer; }", "cap = hbCapMs(x.capServer); }")]}),
    ('(k) cap dipasang di SEMUA koleksi (berita acara tutup buku — kirim ulang identik SDK ditolak v6)', {FB: [("const pasangCap = (koleksi, d) => (hbHemat(koleksi) ?", "const pasangCap = (koleksi, d) => (true ?")]}),
    ('(l) gerbang penulis mengabaikan kasir.html', {HB: [("if (app === 'kasir') { tandai(HB_KOLEKSI_REST, 'kasir.html di ' + nama + ' masih berdenyut'); return; }", "if (app === 'kasir') return;")]}),
    ('(l) gerbang penulis mengabaikan tab /baru/ versi lama', {HB: [("if (app === 'baru' && /^baru-c\\d+$/.test(String(p.versi || ''))) return;", "if (app === 'baru') return;")]}),
    ('(l) gerbang /baru/ lama menempel sampai sesi berakhir (tanpa lepas sesudah baca penuh)', {HB: [("const p = (peristiwa || []).find((x) => !beres[x.kunci] && !(hbAngka(r.Wt) >= x.T + HB_BARU_MENIT * hbMenit));", "const p = (peristiwa || [])[0];")]}),
    ('(m) simpanan Firestore bawaan (GC 40 MiB) saat nyala', {FB: [("if (_hematNyala) cacheOpsi.cacheSizeBytes = CACHE_SIZE_UNLIMITED;", "")]}),
    ('(n) kasir darurat masih PATCH untuk nota', {KD: [("var bercap = item.koleksi === 'penjualan';", "var bercap = false;")]}),
    ('(n) kasir darurat memakai updateMask', {KD: [("updateTransforms: [{ fieldPath: 'capServer', setToServerValue: 'REQUEST_TIME' }] }] })", "updateTransforms: [{ fieldPath: 'capServer', setToServerValue: 'REQUEST_TIME' }], updateMask: { fieldPaths: Object.keys(fields) } }] })")]}),
    ('(o) saklar bawaan NYALA', {HB: [("return penyimpan.baca(HB_KUNCI_SAKLAR) === 'nyala'; } catch (e) { return false; }", "return penyimpan.baca(HB_KUNCI_SAKLAR) !== 'mati'; } catch (e) { return false; }")]}),
    ('(p) gerbang katalog terbuka walau hitungan koleksi HP kasir galat / lama', {HB: [("if (lama.length) return { boleh: false, sebab: 'hitungan server ' + lama.join(', ') + ' lebih dari 35 menit' };", "")]}),
    ('(q) "baru tanpa cap" dihitung walau simpanan kosong (banjir sentuh)', {HB: [("if (typeof b.cap === 'number' || !dipercaya) return; baru.push(id);", "if (typeof b.cap === 'number') return; baru.push(id);")]}),
    ('(r) penjaga ayunan katalog dibuang', {HB: [("if (akhir && kini - akhir.pada <= 15 * hbMenit && kanonS !== kanonIni) A.berhenti =", "if (false) A.berhenti =")]}),
    ('(s) penjaga pendengar simpanan hidup dibuang', {HB: [("mati(kini) { return Object.keys(harap).filter((k) => Object.keys(harap[k]).some((id) => harap[k][id].batas < kini)); },", "mati(kini) { return []; },")]}),
    ('(t) rem kuota dibuang', {HB: [("if ((x.otomatisK || 0) >= 2) return { boleh: false,", "if (false) return { boleh: false,")]}),
    ('(u) uang-kritis tidak dijaga di penulis pusat', {FB: [("if (_hemat && status.akun.jenis === 'owner' && kirimanUangKritis(daftar)) { const g = await _hemat.pastikanSegar(); if (!g.ok) return { gagal: true, pesan: 'Belum disimpan — ' + g.pesan }; }", "")]}),
    ('(v) satu setDoc koleksi hemat TANPA cap ditambahkan di firebase.js', {FB: [("export function hematMintaSemua() {", "export function tulisCepat(id) { return setDoc(doc(db, 'penjualan', String(id)), { id }); }\nexport function hematMintaSemua() {")]}),
    ('(v) tulisBerkas kehilangan pasangCap', {FB: [("b.set(doc(db, x.koleksi, String(d.id)), pasangCap(x.koleksi, d)); ditulis.push", "b.set(doc(db, x.koleksi, String(d.id)), d); ditulis.push")]}),
    ('(v) tulis SDK langsung dari layar (melewati penulis pusat)', {'baru/js/layar/menu-logika.js': [("export ", "const __tulisLiar = () => setDoc(doc(db, 'penjualan', 'x'), {});\nexport ", )]}),
    ('(w) saklar mati tetapi koleksi hemat lewat pendengar simpanan', {FB: [("const hemat = _hematNyala && akun.jenis === 'owner' && _nisanSah && !_berhenti && _kunciTab.milik();", "const hemat = akun.jenis === 'owner' && !_berhenti;")]}),
    ('(x) batu nisan ditulis walau aturan v7 belum terbukti (rules v6 menolak seluruh batch hapus)', {FB: [("const pakaiNisan = _nisanSah && ", "const pakaiNisan = true && ")]}),
    ('(y) hari kuota & umur baca penuh dari jam PERANGKAT (bukan jam server)', {HB: [("const kiniS = () => (G.skew === null ? null : jam() + G.skew);", "const kiniS = () => jam();")]}),
    ('(gema) denyut LAMA dari sesi sebelumnya dipakai sebagai jam server (selisih jam salah berjam-jam)', {FB: [
        ("if (nama === KOLEKSI_PERANGKAT && !(snap.metadata && snap.metadata.fromCache) && _denyutKirim.pada) {", "if (nama === KOLEKSI_PERANGKAT && !(snap.metadata && snap.metadata.fromCache)) {"),
        ("if (typeof c === 'number' && d && d.pada === _denyutKirim.pada && _gemaTerakhir !== _denyutKirim.pada && !tunda.some((t) => t.id === id)) { _gemaTerakhir = _denyutKirim.pada; _hemat.gemaServer(c, _denyutKirim.ms); }",
         "if (typeof c === 'number' && d && _gemaTerakhir !== c && !tunda.some((t) => t.id === id)) { _gemaTerakhir = c; _hemat.gemaServer(c, Date.now()); }")]}),
    ('(urai) komentar // menelan sisa baris objek (cacat 7 Okt di TAB_SISTEM menu.js — periksa_komentar tidak melihat lanjutan objek)', {'baru/js/layar/menu.js': [(
        "['hemat', 'Hemat baca']], peran:", "['hemat', 'Hemat baca']],   // hemat baca peran:")]}),
    ('(urai) firebase.js mengimpor nama yang tidak diekspor hemat-baca.js', {FB: [("hbSiapNyala, hbTanpaCapStatis } from './hemat-baca.js';", "hbSiapNyala, hbTanpaCapStatis, hbTidakAda } from './hemat-baca.js';")]}),
    ('(tab) kunci tab diambil SESUDAH Firestore dimulai (dua klien sempat hidup)', {'baru/js/app.js': [("const pakai = () => { kt.ambil(); jagaKunciTab(kt); fb.mulai(gambarAkun); };", "const pakai = () => { fb.mulai(gambarAkun); kt.ambil(); jagaKunciTab(kt); };")]}),
    ('(tab) tab yang kalah tidak menghentikan Firestore-nya', {'baru/js/app.js': [("    fb.berhenti('Aplikasi dipakai di tab lain peramban ini", "    void ('Aplikasi dipakai di tab lain peramban ini")]}),
    ('(tab) saklar mati tetap memakai kunci tab', {'baru/js/app.js': [("  if (!fb.hematNyala()) { fb.mulai(gambarAkun); return; }\n", "")]}),
    ('(z) pendeteksi tidak menyentuh (ubahan Console tak pernah sampai ke perangkat lain)', {HB: [("if (r.sentuh.length) o.sdk.sentuh(k, r.sentuh).catch(() => {});", "")]}),
    ('(z) baca penuh harian per PERANGKAT diam-diam berhenti (klaim tidak pernah ditulis)', {HB: [("if (k.hari !== hari) return { klaim: true, hari, sebab:", "if (false) return { klaim: true, hari, sebab:")]}),
]


if __name__ == '__main__':
    T = baca_semua()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti in KONTROL:
            try: h = utama(rusak(T, ganti))
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' · ' + str(e)); kode = 3; continue
            g = [x for x in h if not x[1]]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h = utama(T)
    g = [x for x in h if not x[1]]
    for x in g: print('✗ ' + x[0] + (' → ' + str(x[2])[:900] if x[2] else ''))
    print('HEMAT BACA (jsc + statis, kotak pasir): %d lulus · %d gagal' % (len(h) - len(g), len(g)))
    sys.exit(1 if g else 0)
