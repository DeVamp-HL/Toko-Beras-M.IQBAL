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
      T (tinjauan 7 Okt): gerbang HP kasir lama tidak menyentuh nota baru tanpa cap; cap 2099 tidak menggeser jam server perangkat; catatan LAHIR ULANG tanpa
      cap sesudah nisannya tampil lagi (juga bulan terkunci, tahan muat ulang, dihapus lagi → sembunyi); temuan gagal dikirim diulang; Bn = jam baca penuh
      terakhir; arsip tutup buku bukan "hilang"; umur denyut = jam server saat terlihat berubah.
      T6b–T6g (audit P5, 8 Okt) hemat baca × arsip tutup buku, baca penuh LAMBAT (jawaban server masuk simpanan sebelum limbo membuang catatan arsip): perangkat
      owner yang tertutup selama ritual tidak pernah menggambar catatan 2026 + saldo pembuka sekaligus (memori BEKU sampai baca penuh selesai — /baru/ tidak punya tirai penutup layar; "siap" = pil memuat), tanpa S; baca
      penuh karena tutup buku WAJIB (menembus rem kuota); berita acara dari simpanan dulu; baca penuh terputus → sesi berikut memori kosong; perangkat yang
      menjalankan ritual tidak dibekukan; baca penuh wajib gagal → jeda 10 menit; tanpa internet pil tidak menggantung. B1/B2: pil memuat menunggu berita acara dari server.
      T6e2–T6j (sanggahan P5, 8 Okt): Mac ritual ditutup di tengah ritual & dibuka lagi (memori = simpanannya, bukan kosong), berita acara berganti (memori beku
      ditentukan ulang), putus di tengah baca penuh wajib & hapus sendiri selagi ditahan, dengar penuh karena kasir.html tetap ditahan & lepas saat terkini,
      server DIAM (kuota habis, tersambung) → pil lepas sesudah 30 detik dengan sebabnya. Pendengar simpanan mainan berbunyi HANYA bila isinya berubah (SDK).
      T6k–T6v (sanggahan kedua P5, 8 Okt — /baru/ tidak punya tirai penutup layar, MEMORI satu-satunya pelindung): PENGHALANG BERSAMA lintas koleksi (stok =
      batchMasuk − penjualan tidak terpotong dua kali; putus di tengah tetap beku bersama), ditutup di tengah penghalang (beda zaman → disembunyikan), sesi HIDUP
      yang putus selama ritual (beku saat putus, dua urutan, kuota habis), TIDUR tanpa kabar (berita acara berganti selagi S menempel → disembunyikan), F wajib
      macet sebelum membawa apa pun (tidak bercampur), bercampur + kuota habis (kabar "disembunyikan" didahulukan), perangkat LAIN dengan berita acara simpanan
      "terkunci" (kosong, bukan dobel — hanya pemegang ritual memakai simpanan), server diam + simpanan tidak dipercaya (M14), tanda server diam dari masa tanpa
      internet, pemegang yang ritualnya diambil alih, semua koleksi dengar penuh (lepas sebelum hitungan), uang-kritis selagi berita acara belum dijawab lagi.
      Server mainan: putus = kabar peramban + SDK menandai berita acara "dari simpanan"; tidur/bangun = tanpa kabar apa pun; jawab = tanpa kabar peramban.
  K · KELENGKAPAN (#111 × Paket C, 7 Okt) — SATU sumber hbBelumLengkap: murni (tiap sebab "periksa" + "harian" belum dibaca penuh sejak kuota baca
      direset — jam resetnya disebut, baca penuh harian toko selesai / belum / selesai dengan temuanTunda, dengar penuh = lengkap, 429 kuota habis, jam server
      belum diterima, tab berhenti; "terperiksa" = rumus 7 Okt + tab berhenti di 16384 kombinasi; pemilih & kalimat — sebab tidak dipinjamkan, jumlah sebelum
      petunjuk), server mainan (perangkat baru, hari kuota berganti selagi baca penuh harian toko dipegang perangkat lain, selesai, tombol baca penuh, HP kasir
      lama = dengar penuh, batu nisan belum dicocokkan, rem kuota, tanpa internet; terperiksa di keadaan() dibandingkan dengan rumus 7 Okt yang DITULIS ULANG
      atas keadaan sesi nyata) + firebase.js hematKeadaan (mati: tanpa belumLengkap; nyala: semua koleksi hemat, koleksi tetap tidak).
      Sanggahan 7 Okt: K4 baca penuh sesi ini + putus internet · K5 tab kalah kunci tab (berhenti) · K6 baca penuh harian toko "selesai" baru sesudah antrean
      temuan habis (sentuhan gagal sekali → diulang; gagal permanen → temuanTunda; bulan terkunci → `lewat` dilaporkan) · C12 sentuhCap melaporkan `lewat` ·
      C13 firebase.js berhenti → hematKeadaan semua "periksa". Audit P5: C14 asal berita acara (fromCache) diteruskan — kembali "dari simpanan" = tidak dijawab lagi;
      denyut / setelan dari server tidak dianggap jawaban berita acara (M31) — C15 tulisBerkas → catatTulis.
  C · firebase.js DIJALANKAN di jsc dengan SDK palsu: saklar MATI = pendengar persis sebelum 7 Okt (satu pendengar penuh per koleksi + katalog, tanpa
      source 'cache' / where capServer / limit 1.000.000), capServer dikupas sebelum memori; saklar NYALA = koleksi hemat lewat pendengar simpanan, koleksi
      tetap penuh; tulisBerkas: cap HANYA koleksi hemat (bukan berita acara tutup buku, pesanan, setelan, katalog, jejak), salinan antre tanpa sentinel,
      batu nisan di batch yang sama HANYA sesudah aturan v7 terbukti, uang-kritis ditolak bila belum segar, tab yang kalah tidak menulis; denyut owner bercap.
  C (tinjauan 7 Okt): penyentuh memakai isi MENTAH sesi hemat (lahir ulang), tab tanpa hak tulis mengembalikan temuan sebagai "tunda", baris statis siap-nyala.
  E · KASIR DARURAT di jsc: kirimAntrean ASLI (dipotong dari halaman) + Firestore REST palsu bermodel rules v3/v6/v7 — jawaban :commit hilang lalu kirim
      ulang: v6/v3 → cara lama PATCH updateMask MASUK (bukan "ditolak"), v7 → :commit diterima; bulan terkunci → kedua cara ditolak → "ditolak".
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
ok('batas nisan: min(jam baca penuh terakhir tiap koleksi) − 60 menit, koleksi yang belum pernah dibaca penuh diabaikan, jam server − 60 menit sebagai batas atas; tidak pernah 0; tanpa apa pun = tunggu',
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
// tinjauan 7 Okt: catatan yang LAHIR ULANG tanpa cap sesudah nisannya (HP kasir lama kirim ulang, Console) dulu tersembunyi selamanya
var SN2 = hbSaringNisan(V, { a: T0, b: T0, c: T0, d: T0, e: T0, f: T0 }, { d: T0, e: T0 - 1, f: T0 });
ok('saring nisan: LAHIR ULANG terbukti baca penuh server (bukti = nisan yang berlaku saat itu) → tampil walau tanpa cap / "peta" / cap sama; nisan LEBIH BARU dari buktinya (dihapus lagi) → sembunyi',
  J(SN2.tampil.map(function (x) { return x.id; })) === '["b","c","d","f","g"]' && SN2.tersembunyi === 2, J(SN2));
var LU = hbLahirUlang({ a: { cap: T0 - HR }, b: { cap: T0 + HR }, d: { cap: undefined }, t1: { tunda: true }, z: { cap: undefined }, e: { cap: 'peta' } }, { a: T0, b: T0, d: T0, t1: T0, e: T0 }, { d: T0 });
ok('lahir ulang: ada di snapshot SERVER padahal nisannya akan menyembunyikannya (cap lebih tua / tanpa / "peta"); bukan: cap lebih baru, sudah terbukti, tertunda, tanpa nisan',
  J(LU.sort()) === '["a","e"]', J(LU));
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
// tinjauan 7 Okt: umur denyut = jam SERVER saat denyut terlihat BERUBAH di perangkat ini, bukan `pada` (jam perangkat penulis — tab lama jamnya bisa terlambat)
var tabL = function (menitLalu) { return { id: 'tab', nama: 'tab', aplikasi: 'baru', versi: 'baru', pada: new Date(T0 - menitLalu * MNT).toISOString() }; };
var LD = {}, sesiD = {};
var ld0 = hbLihatDenyut(LD, sesiD, [tabL(60)], T0 - 30 * MNT);          // pertama terlihat: berubah selagi perangkat ini tidak mendengar → jam tidak diketahui
var ld1 = hbLihatDenyut(LD, sesiD, [tabL(20)], T0);                     // BERUBAH selagi didengar; jam tab itu terlambat 20 menit
var GP6 = hbGerbangPenulis([tabL(20)], T0 + MNT, KOLH, ld1), GP7 = hbGerbangPenulis([tabL(20)], T0 + MNT, KOLH);
ok('umur denyut: tab /baru/ lama yang jamnya terlambat 20 menit dan BARU SAJA menulis (perubahan denyutnya terlihat) → SEMUA koleksi dengar penuh; tanpa jam terlihat dulu = peristiwa saja',
  !('tab' in ld0) && ld1.tab === T0 && KOLH.every(function (k) { return !!GP6.penuh[k]; }) && !Object.keys(GP7.penuh).length && GP7.peristiwa.length === 1, J([ld0, ld1, GP6, GP7]));
var ld2 = hbLihatDenyut(LD, {}, [tabL(20)], T0 + 2 * HR), ld3 = hbLihatDenyut(LD, {}, [tabL(5)], T0 + 3 * HR), ld4 = hbLihatDenyut({ tab: { pada: 'x', s: T0 - 20 * HR } }, {}, [], T0);
ok('umur denyut: jam yang terlihat TAHAN muat ulang (rekam) selama `pada` sama; berubah selagi tidak didengar → dibuang (kembali ke `pada`); > 15 hari → dibuang',
  ld2.tab === T0 && !('tab' in ld3) && !('tab' in ld4), J([ld2, ld3, ld4]));
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
var Rbk = R0({ bkBeda: true }), RbkM = R0({ bkBeda: true, minta: { penjualan: { sebab: 'hitungan server beda', manual: false } } }), Rcm = R0({ bkCampur: true });
ok('rencana (audit P5): tutup buku berubah sejak baca penuh terakhir / baca penuh sesudah tutup buku terputus → baca penuh WAJIB (bukan otomatis — menembus rem kuota), juga bila ada permintaan otomatis (hitungan beda); tutup buku BERJALAN tetap dengar penuh',
  Rbk.mode === 'total' && Rbk.wajib === true && Rbk.otomatis === false && Rbk.sebab === HB_SEBAB_BK && RbkM.wajib === true && RbkM.sebab === HB_SEBAB_BK && Rcm.wajib === true && Rcm.sebab === HB_SEBAB_BK_CAMPUR
  && R0({ bkBeda: true, bkAktif: true }).mode === 'penuh' && !R0({ minta: { penjualan: { sebab: 'x', manual: false } } }).wajib && R0({ minta: { penjualan: { sebab: 'x', manual: false } } }).otomatis === true, J([Rbk, RbkM, Rcm]));
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
var tabLama8 = { id: 'tab', nama: 'tab', aplikasi: 'baru', versi: 'baru', pada: new Date(T0 - 8 * HR).toISOString() };
var SNY3 = hbSiapNyala({ perangkat: [tabLama8], kiniMs: T0, lihat: { tab: T0 - HR }, nisanSah: true, statis: 0, ownerEmail: 'x' }), SNY4 = hbSiapNyala({ perangkat: [tabLama8], kiniMs: T0, nisanSah: true, statis: 0, ownerEmail: 'x' });
ok('daftar siap-nyala: tab lama yang `pada`-nya 8 hari lalu (jam tab terlambat) tapi terlihat BERUBAH kemarin → merah; tanpa jam terlihat → menurut `pada`',
  !SNY3.find(function (x) { return x.id === 'lama'; }).ok && SNY4.find(function (x) { return x.id === 'lama'; }).ok, J([SNY3[1], SNY4[1]]));
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
// diam (sanggahan P5) = tersambung tapi server tidak menjawab (kuota baca habis sampai reset / sinyal lemah): pendengar hanya memberi snapshot simpanan, hitungan
// ditolak resource-exhausted, tulisan menunggu di antrean. hitungTahan = [] → hitungan server menunggu dilepas uji (jawaban lambat).
function Perangkat(nama, geser) { this.nama = nama; this.geser = geser || 0; this.online = true; this.diam = false; this.hitungTahan = null; this.cache = {}; this.L = []; this.ls = {}; this.timer = []; this.vBeku = false; this.antre = []; S.dev.push(this); }
Perangkat.prototype.jam = function () { return S.jam + this.geser; };
Perangkat.prototype.c = function (k) { return this.cache[k] || (this.cache[k] = {}); };
Perangkat.prototype.bentuk = function (id, e) { return { id: id, tunda: !!e.tunda, capMentah: e.cap === null ? null : e.cap === undefined ? undefined : TS(e.cap),
  isi: function () { var x = salin(e.data); if (e.cap !== undefined) x.capServer = e.cap === null ? null : TS(e.cap); return x; } }; };
Perangkat.prototype.snap = function (L) { var C = this.c(L.k), self = this, dok = [];
  Object.keys(C).forEach(function (id) { var e = C[id]; if ((L.jenis === 'delta' || L.jenis === 'nisan') && (e.tunda || !cocokL(L, e))) return; dok.push(self.bentuk(id, e)); });
  return { dariCache: L.jenis === 'cache' ? true : !(self.online && L.terkini), dok: dok }; };
// pendengar SIMPANAN (source 'cache') berbunyi HANYA bila isi simpanan koleksinya berubah (dokumen, isi, cap, tertunda) — seperti SDK. Sanggahan P5: dulu dikabari
// ulang tiap S/F dipasang atau tersinkron, jadi memori ikut segar lewat jalan itu dan baris pelepas memori beku di hbSesi (selesaiF, lepasTahan) tidak teruji
Perangkat.prototype.kabarV = function (L) { if (!L.aktif || this.vBeku) return; var s = this.snap(L); var kunci = J(s.dok.map(function (d) { var c = d.capMentah; return [d.id, d.tunda, c && c.toMillis ? c.toMillis() : c === null ? null : 'tanpa', d.isi()]; }));
  if (kunci === L.kunci) return; L.kunci = kunci; L.cb(s); };
Perangkat.prototype.emit = function (k) { var self = this; this.L.forEach(function (L) { if (!L.aktif || L.k !== k || (L.jenis === 'cache' && self.vBeku)) return;
  antri(function () { if (!L.aktif) return; if (L.jenis === 'cache') self.kabarV(L); else L.cb(self.snap(L)); }); }); };
// server → simpanan untuk kueri L, + LIMBO: dokumen simpanan yang cocok kueri tapi tidak ada di server dibuang (perilaku SDK yang diandalkan rancangan)
Perangkat.prototype.sinkron = function (L) { var C = this.c(L.k), K = S.kol(L.k);
  Object.keys(K).forEach(function (id) { var e = K[id]; if (!cocokL(L, e) || (C[id] && C[id].tunda)) return; C[id] = { data: salin(e.data), cap: e.cap }; });
  Object.keys(C).forEach(function (id) { var c = C[id]; if (c.tunda || K[id] || !cocokL(L, c)) return; delete C[id]; }); L.terkini = true; };
Perangkat.prototype.dengar = function (jenis, k, B, cb) { var self = this; var L = { jenis: jenis, k: k, B: B, cb: cb, aktif: true, terkini: false }; this.L.push(L);
  antri(function () { if (!L.aktif) return;
    if (jenis === 'cache') { self.kabarV(L); return; }
    if (jenis === 'penuh' && Object.keys(self.c(k)).length) cb(self.snap(L));   // snapshot SIMPANAN dulu (pendeteksi membandingkannya)
    if (self.online && !self.diam) { self.sinkron(L); self.emit(k); } else cb(self.snap(L)); });
  return function () { L.aktif = false; }; };
Perangkat.prototype.dariServer = function (k, id) { if (!this.online || this.diam) return; var K = S.kol(k), e = K[id], C = this.c(k), c = C[id];
  var kena = this.L.some(function (L) { return L.aktif && L.k === k && L.jenis !== 'cache' && L.terkini && ((e && cocokL(L, e)) || (!e && c && cocokL(L, c))); });
  if (!kena || (c && c.tunda)) return; if (e) C[id] = { data: salin(e.data), cap: e.cap }; else delete C[id]; this.emit(k); };
// putus (sanggahan kedua P5): peramban memberi kabar offline DAN SDK menandai pendengar berita acara "dari simpanan" (fromCache) — firebase.js kabariTetap meneruskan
// acaraServer false. sambung: peramban online → SDK tersambung lagi → server menjawab berita acara (acaraServer true) sesudah data tersinkron ke simpanan.
Perangkat.prototype.putus = function () { var self = this; this.online = false; this.L.forEach(function (L) { if (L.jenis !== 'cache') { L.terkini = false; if (L.aktif) antri(function () { if (L.aktif) L.cb(self.snap(L)); }); } });
  if (this.sesi) { this.sesi.online(false); this.sesi.setelTetap({ acaraServer: false }); } };
Perangkat.prototype.sambung = function () { var self = this; this.online = true; this.L.forEach(function (L) { if (L.aktif && L.jenis !== 'cache') self.sinkron(L); }); Object.keys(this.cache).forEach(function (k) { self.emit(k); }); this.kirim(); if (this.sesi) { this.sesi.online(true); this.tetap(); } };
// TIDUR (sanggahan kedua P5): sambungan mati TANPA kabar apa pun (Mac tidur dengan tab terbuka; peramban tidak memberi kabar offline, SDK tidak sempat menandai
// fromCache). BANGUN: SDK tersambung lagi, server → simpanan untuk semua pendengar server (S membawa saldo pembuka; catatan arsip di luar jendela S tidak terbuang),
// lalu berita acara dijawab server LEBIH DULU dari kabar simpanan (pendengarnya didaftarkan lebih awal — urutan SDK), baru kabar simpanan
Perangkat.prototype.tidur = function () { this.online = false; };
Perangkat.prototype.bangun = function () { var self = this; this.online = true; this.L.forEach(function (L) { if (L.aktif && L.jenis !== 'cache' && (self.fTahan || []).indexOf(L) < 0) self.sinkron(L); });
  Object.keys(this.cache).forEach(function (k) { self.emit(k); }); this.tetap(); tuntas(); };
// tulisan perangkat ini: tampil seketika di simpanan (tertunda, cap null), dikirim saat tersambung (cap = jam SERVER saat diterima)
Perangkat.prototype.tulis = function (k, id, data) { if (this.sesi && this.sesi.catatTulis) this.sesi.catatTulis(k, id); this.c(k)[id] = { data: salin(data), cap: null, tunda: true }; this.antre.push({ k: k, id: id, data: data }); this.emit(k); if (this.online && !this.diam) this.kirim(); };
Perangkat.prototype.hapusDok = function (k, id) { delete this.c(k)[id]; this.antre.push({ k: k, id: id, hapus: true }); if (this.sesi) this.sesi.catatHapus(k, id); this.emit(k); if (this.online && !this.diam) this.kirim(); };
// server mulai menjawab lagi (kuota baca direset): data server → simpanan, kiriman antre terkirim, berita acara dijawab server. TANPA kabar sambungan peramban
// (sanggahan kedua P5: peramban online selama server diam — dulu lewat sambung(), yang ikut mengabari online(true) dan menutupi kabar basi)
Perangkat.prototype.jawab = function () { var self = this; this.diam = false; this.L.forEach(function (L) { if (L.aktif && L.jenis !== 'cache') self.sinkron(L); });
  Object.keys(this.cache).forEach(function (k) { self.emit(k); }); this.kirim(); this.tetap(); };
Perangkat.prototype.kirim = function () { var self = this; var q = this.antre; this.antre = [];
  q.forEach(function (x) { if (x.hapus) { S.hapus(x.k, x.id, true); return; } S.tulis(x.k, x.id, x.data, true); var e = S.kol(x.k)[x.id]; self.c(x.k)[x.id] = { data: salin(e.data), cap: e.cap }; self.emit(x.k); }); };
Perangkat.prototype.jadwal = function (f, ms) { var h = { f: f, pada: this.jam() + ms, aktif: true }; this.timer.push(h); return h; };
Perangkat.prototype.tutup = function () { if (this.sesi) this.sesi.berhenti(); this.L.forEach(function (L) { L.aktif = false; }); this.L = []; this.timer = []; this.sesi = null; };
// berita acara dari SERVER mainan (acaraServer: true — firebase.js: jawaban terakhir pendengar tutupBukuAcara bukan dari simpanan perangkat; audit P5)
Perangkat.prototype.tetap = function () { if (this.sesi) this.sesi.setelTetap({ perangkat: salin(S.perangkat), acara: salin(S.acara), klaim: S.klaim ? salin(S.klaim) : null, acaraServer: true }); };
Perangkat.prototype.gema = function () { if (this.sesi) this.sesi.gemaServer(S.jam, this.jam()); };
var KOL = ['penjualan', 'stokBahanLiteran', 'piutangMutasi', 'pengeluaranHarian'];
var NAMA_K = KOL.slice();
Perangkat.prototype.buka = function (opsi) {
  var self = this; this.tutup(); this.mem = {}; this.siap = {}; this.periksa = {}; this.mati = []; this.klaimTulis = 0; this.sentuhN = 0; this.nisanTulis = 0; this.sentuhGagal = this.sentuhGagal || 0; this.berubahN = 0;
  var peny = { baca: function (k) { return self.ls[k] === undefined ? null : self.ls[k]; }, tulis: function (k, v) { self.ls[k] = String(v); }, hapus: function (k) { delete self.ls[k]; } };
  var R = hbBacaRekam(peny, 'proyek-uji', 'uid-owner'); this.R = R;
  this.sesi = hbSesi({ koleksi: NAMA_K, R: R, simpan: function () { hbSimpanRekam(peny, R, self.jam()); }, jam: function () { return self.jam(); },
    jadwal: function (f, ms) { return self.jadwal(f, ms); }, batal: function (h) { if (h) h.aktif = false; }, idPerangkat: self.nama, namaPerangkat: self.nama, online: self.online,
    milikTab: function () { return true; }, hapusTunda: function () { return 0; },
    sdk: { cache: function (k, cb) { return self.dengar('cache', k, null, cb); }, delta: function (k, B, cb) { return self.dengar('delta', k, B, cb); },
      // fGalat = server menolak baca penuh (mis. 'unavailable') — galat F dikabarkan seperti SDK
      penuh: function (k, cb, galat) { if (self.fGalat) { var kode = self.fGalat; antri(function () { galat({ code: kode }); }); return function () {}; } return self.dengar('penuh', k, null, cb); }, nisan: function (B, cb) { return self.dengar('nisan', 'batuNisan', B, cb); },
      hitung: function (k) { if (!self.online || self.diam) return Promise.reject({ code: self.diam ? 'resource-exhausted' : 'unavailable' });
        if (self.hitungTahan) return new Promise(function (r) { self.hitungTahan.push(function () { r(S.ids(k).length); }); }); return Promise.resolve(S.ids(k).length); },
      klaim: function (dok) { self.klaimTulis++; S.klaim = salin(dok); antri(function () { S.dev.forEach(function (p) { p.tetap(); }); }); return Promise.resolve(); },
      // penyentuh SEPERTI firebase.js sentuhCap: hanya catatan yang ada di isi MENTAH (lihat — sebelum saringan nisan); bulan terkunci (S.kunci) DILEWATI dan
      // dilaporkan sebagai `lewat` (sanggahan 7 Okt — dulu dibuang diam-diam); sentuhGagal = potongan ditolak / tab tidak boleh menulis → { tunda } (diulang)
      sentuh: function (k, ids, lihat) { if (self.sentuhGagal > 0) { self.sentuhGagal--; return Promise.resolve({ n: 0, tunda: ids.slice() }); }
        var ada = ids.filter(function (id) { return !!(lihat ? lihat(id) : memDok(self, k, id)); }); var lewat = ada.filter(function (id) { return !!(S.kunci && S.kunci[id]); });
        var boleh = ada.filter(function (id) { return lewat.indexOf(id) < 0; });
        self.sentuhN += boleh.length; boleh.forEach(function (id) { var e = S.kol(k)[id]; if (e) { e.cap = S.jam; S.siar(k, id); } }); return Promise.resolve({ n: boleh.length, tunda: [], lewat: lewat }); },
      tulisNisan: function (k, ids) { self.nisanTulis += ids.length; ids.forEach(function (id) { S.nisan[k + '|' + id] = { data: { id: k + '|' + id, koleksi: k, idDok: String(id) }, cap: S.jam }; S.siar('batuNisan', k + '|' + id); }); return Promise.resolve({ n: ids.length, tunda: [] }); } },
    keluar: { pasok: function (k, data) { self.mem[k] = data; }, tunda: function () {}, siap: function (k) { self.siap[k] = true; }, periksa: function (k, ya) { self.periksa[k] = ya; }, berubah: function () { self.berubahN += 1; }, mati: function (k) { self.mati.push(k); } } }).mulai();
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
// Rumus "terperiksa" sejak 7 Okt DITULIS ULANG di uji (bukan diturunkan dari belumK) + tab yang berhenti (sanggahan 7 Okt) — pembanding SATU sumber kelengkapan.
function lamaT(x) { if (x.vMati || x.berhenti || !x.vAda || !x.nTerkini) return false; if (x.mode === 'penuh') return !!x.fTerkini && (x.fSelesai || x.fMode === 'penuh');
  if (x.wajibTotal || !x.sTerkini) return false; if (x.fJalan) return false; return !!x.fSelesai || !!x.cocok; }
/** Rumus 7 Okt atas keadaan sesi NYATA koleksi k (bagian dalam hbSesi, bukan keadaan()/belumLengkap()). */
function lamaSesi(p, k) { var st = p.sesi._K[k], G = p.sesi._G; return lamaT({ vMati: st.vMati, berhenti: G.berhenti, vAda: st.vAda, nTerkini: G.nTerkini, mode: st.mode, fTerkini: st.fTerkini,
  fSelesai: st.fSelesai, fMode: st.fMode, wajibTotal: st.wajibTotal, sTerkini: st.sTerkini, fJalan: !!(st.fLepas && st.fMode === 'total' && !st.fSelesai), cocok: st.cocokPada > 0 }); }
// #111 × Paket C (sanggahan 7 Okt: dulu tautologis — terperiksa & kelengkapan sama-sama dari belumK): terperiksa di keadaan(), kabar terperiksa ke layar
// (o.keluar.periksa; tab yang berhenti tidak dikabari lagi), jenis "periksa" di kelengkapan, dan belumLengkap di keadaan() WAJIB sama dengan rumus 7 Okt yang
// ditulis ulang, dihitung dari keadaan sesi nyata → [k yang menyimpang]
function cekSatuSumber(p) { var K = p.sesi.keadaan(); var bl = p.sesi.belumLengkap();
  return NAMA_K.filter(function (k) { var x = K.koleksi.find(function (y) { return y.k === k; }); var lama = lamaSesi(p, k);
    return x.terperiksa !== lama || !!(bl[k] && bl[k].jenis === 'periksa') === lama || (!p.sesi._G.berhenti && p.periksa[k] !== undefined && p.periksa[k] !== lama)
      || J((K.belumLengkap || {})[k] || null) !== J(bl[k] || null); }); }

// ---- data awal toko (contoh): sebagian catatan lama TANPA cap (sebelum 7 Okt), sebagian bercap
S = new Server(Z('2026-10-07T03:00:00Z'));   // 10.00 WIB
var nota = function (id, n, tgl) { return { id: id, tanggal: tgl || '2026-10-01', hargaTotal: n, namaProduk: 'Beras Contoh', namaPelanggan: 'Pembeli Contoh' }; };
S.tulis('penjualan', 'p1', nota('p1', 10000), false); S.tulis('penjualan', 'p2', nota('p2', 20000), false);
S.jam -= 3 * HR; S.tulis('penjualan', 'p3', nota('p3', 30000), true); S.tulis('stokBahanLiteran', 's1', { id: 's1', tanggal: '2026-10-04', kg: 5 }, true); S.jam += 3 * HR;
S.jam -= JM; S.tulis('stokBahanLiteran', 's2', { id: 's2', tanggal: '2026-10-07', kg: 3 }, true); S.jam += JM;   // s2 baru → tanda air koleksi ini jauh di depan s1
S.jam -= 2 * JM; S.tulis('penjualan', 'p4', nota('p4', 40000), true); S.tulis('piutangMutasi', 'u1', { id: 'u1', tanggal: '2026-10-07', nominal: 5000 }, true); S.jam += 2 * JM;
S.tulis('pengeluaranHarian', 'h1', { id: 'h1', tanggal: '2026-10-07', nominal: 7000 }, false);
S.klaim = { id: 'hematHarian', hari: '2026-10-06', perangkat: 'lama', selesai: Z('2026-10-06T08:00:00Z') };

// ---- B1 · perangkat BARU (tanpa rekam): simpanan kosong → baca penuh semua; pil "memuat…" tidak lepas dari simpanan kosong
var A = new Perangkat('mac'); fLambat(A);   // baca penuh lambat (fLambat/fTiba/fLimbo di bagian T6b)
A.buka({ tetap: false }); tuntas();
ok('B1 perangkat baru: simpanan kosong TIDAK menandai siap (pil memuat), belum ada baca penuh sebelum masukan koleksi tetap', !Object.keys(A.siap).length, J(A.siap));
A.gema(); A.tetap(); tuntas();
ok('B1: berita acara dari server, baca penuh masih berjalan → pil memuat TETAP (simpanan kosong tidak dipercaya)', !Object.keys(A.siap).length && A.L.some(function (L) { return L.aktif && L.jenis === 'penuh'; }), J(A.siap));
fTiba(A); fLimbo(A);
ok('B1: sesudah baca penuh semua koleksi: siap, memori = server, semua terperiksa', samaServer(A) && semua(A, function (k) { return A.siap[k] && A.periksa[k] === true; }), J({ beda: beda(A), periksa: A.periksa }));
var rkp = A.R.k.penjualan;
ok('B1: rekam per koleksi per perangkat — Wt = cap server tertinggi (BUKAN jam perangkat), n = jumlah server, baca penuh = jam server', rkp && rkp.Wt === S.jam - 2 * JM && rkp.n === 4 && rkp.totalPada === S.jam, J(rkp));
ok('B1: pendengar sesudahnya = simpanan (V) + delta capServer > Wt − 60 menit + nisan; baca penuh (F) sudah dilepas', A.L.filter(function (L) { return L.aktif && L.jenis === 'penuh'; }).length === 0
  && A.L.some(function (L) { return L.aktif && L.jenis === 'delta' && L.k === 'penjualan' && L.B === rkp.Wt - JM; }) && A.L.some(function (L) { return L.aktif && L.jenis === 'nisan'; }), J(A.L.filter(function (L) { return L.aktif; }).map(function (L) { return [L.jenis, L.k, L.B]; })));
ok('B1: memori tanpa capServer (dikupas)', (A.mem.penjualan || []).every(function (d) { return !('capServer' in d); }));
// perangkat kedua owner (iPad), juga baru
var B = new Perangkat('ipad'); B.buka();
ok('B1: perangkat kedua juga baca penuh sendiri (tiap perangkat ≥ sekali)', samaServer(B), J(beda(B)));

// ---- B2 · buka lagi 2 jam kemudian: simpanan dipercaya (memori seketika), lalu delta + nisan dari server
A.tutup(); maju(2 * JM);
S.tulis('penjualan', 'p5', nota('p5', 50000), true);                                   // nota baru (bercap)
S.tulis('penjualan', 'p3', nota('p3', 31000), true);                                   // nota LAMA diubah perangkat lain (bercap)
S.hapus('stokBahanLiteran', 's1', true);                                                // hapus catatan lama (cap < B) — perlu nisan
S.hapus('penjualan', 'p4', true);                                                       // hapus catatan dalam jendela delta (cap > B)
A.buka({ tetap: false }); tuntas();
// audit P5 (8 Okt): dulu "siap seketika dari simpanan" — kini memori tetap seketika dari simpanan, tapi pil "memuat…" menunggu berita acara tutup buku
// dijawab SERVER (berita acara dari simpanan bisa basi: tutup buku tampak tidak berubah → catatan yang sudah diarsipkan + saldo pembuka = DOBEL)
ok('B2 buka lagi: simpanan perangkat DIPERCAYA → memori dari simpanan seketika (sebelum server menjawab, BEKU sampai itu); pil "memuat…" menunggu berita acara tutup buku dari SERVER',
  semua(A, function (k) { return !A.siap[k] && (A.mem[k] || []).length > 0; }) && memId(A, 'penjualan').indexOf('p5') < 0, J({ siap: A.siap, mem: NAMA_K.map(function (k) { return memId(A, k); }) }));
A.gema(); A.tetap(); tuntas();
ok('B2: berita acara dari server (tutup buku tidak berubah) → siap tanpa baca penuh', semua(A, function (k) { return A.siap[k]; }) && !A.L.some(function (L) { return L.jenis === 'penuh'; }), J(A.siap));
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
var blR = F0.sesi.belumLengkap().penjualan;
ok('K (B10) rem: kelengkapan penjualan = "periksa" dengan sebab toko (ditunda supaya kuota tidak habis → ketuk baca penuh sekarang); sama dengan terperiksa', blR && blR.jenis === 'periksa' && /^perlu dibaca penuh, tapi ditunda supaya kuota baca hari ini tidak habis — ketuk "baca penuh sekarang"/.test(blR.sebab) && !cekSatuSumber(F0).length, J([blR, cekSatuSumber(F0)]));
F0.sesi.bacaPenuh(['penjualan'], 'tombol'); tuntas();
ok('B10 rem: tombol "Baca penuh sekarang" menembus rem → terperiksa', keadaanK(F0, 'penjualan').terperiksa === true, J(keadaanK(F0, 'penjualan')));

// ---- B11 · uang-kritis: hitungan segar ≤ 2 menit; offline → ditolak dengan kalimat; katalog: gerbang tertutup saat hitungan galat
var US = null; F0.sesi.pastikanSegar().then(function (r) { US = r; }); tuntas();
ok('B11 uang-kritis: tersambung & cocok → boleh (hitungan server segar)', US && US.ok === true, J(US));
F0.putus(); tuntas(); maju(3 * MNT); var US2 = null; F0.sesi.pastikanSegar().then(function (r) { US2 = r; }); tuntas();
ok('B11 uang-kritis: tanpa internet → DITOLAK "sambungkan internet" (draf tetap di layar)', US2 && !US2.ok && /internet/.test(US2.pesan), J(US2));
var blL = F0.sesi.belumLengkap(); var k4 = keadaanK(F0, 'penjualan');
ok('K4 (B11) penjualan sudah DIBACA PENUH SESI INI (tombol), lalu putus internet → tetap BELUM terperiksa: keadaan(), kabar ke layar & kelengkapan ("periksa", tanpa internet) sama dengan rumus 7 Okt yang ditulis ulang',
  F0.sesi._K.penjualan.fSelesai === true && k4.terperiksa === false && F0.periksa.penjualan === false && lamaSesi(F0, 'penjualan') === false && !!blL.penjualan && blL.penjualan.jenis === 'periksa' && /tanpa internet/.test(blL.penjualan.sebab),
  J([k4, F0.periksa.penjualan, blL.penjualan]));
ok('K (B11) tanpa internet: SEMUA koleksi belum lengkap jenis "periksa" dengan sebab "perangkat ini tanpa internet"; terperiksa sama dengan kelengkapan (juga koleksi yang tadi dibaca penuh)',
  NAMA_K.every(function (k) { return blL[k] && blL[k].jenis === 'periksa' && /tanpa internet/.test(blL[k].sebab); }) && !cekSatuSumber(F0).length, J([blL, cekSatuSumber(F0)]));
ok('B11 katalog: tanpa internet / belum terperiksa → gerbang katalog TERTUTUP', F0.sesi.bolehKatalog().boleh === false, J(F0.sesi.bolehKatalog()));
F0.sambung(); tuntas();
ok('B11 katalog: tersambung & semua terperiksa & hitungan koleksi HP kasir ≤ 35 menit → gerbang terbuka', F0.sesi.bolehKatalog().boleh === true, J(F0.sesi.bolehKatalog()));
maju(36 * MNT); var KL = F0.sesi.bolehKatalog(); F0.sesi.tik(); tuntas(); var KL2 = F0.sesi.bolehKatalog();
ok('B11 katalog: hitungan koleksi HP kasir lebih dari 35 menit (tab tidak berdetak) → gerbang TERTUTUP; hitungan berkala segar lagi → terbuka', KL.boleh === false && /35 menit/.test(KL.sebab) && KL2.boleh === true, J([KL, KL2]));
S.tulis('penjualan', 'k3', nota('k3', 17000), false); tuntas(); var US3 = null; maju(3 * MNT); F0.sesi.pastikanSegar().then(function (r) { US3 = r; }); tuntas();
ok('B11 uang-kritis: hitungan server BEDA (nota tanpa cap) → DITOLAK "belum cocok — sedang dibaca ulang" dan koleksinya dibaca penuh', US3 && !US3.ok && /belum cocok/.test(US3.pesan), J(US3));
maju(20000);
ok('B11: sesudah dibaca ulang nota itu masuk', memId(F0, 'penjualan').indexOf('k3') >= 0, J(beda(F0)));

// ===================== T · TINJAUAN 7 OKT (temuan penyanggah) =====================
function tokoBaru(iso) { S = new Server(Z(iso)); S.klaim = { id: 'hematHarian', hari: hbHariKuota(S.jam), perangkat: 'lain', selesai: S.jam }; }
function klaimHariIni() { S.klaim = { id: 'hematHarian', hari: hbHariKuota(S.jam), perangkat: 'lain', selesai: S.jam }; }
var notaN = function (id, n, tgl) { return { id: id, tanggal: tgl || '2026-11-10', hargaTotal: n, namaPelanggan: 'Pembeli Contoh' }; };
var hpKasir = function (versi) { return { id: 'd-hp', nama: 'HP contoh', aplikasi: 'darurat', versi: versi, pada: new Date(S.jam - 5 * MNT).toISOString(), akun: 'kasir@x' }; };

// ---- T1 · HP kasir < kasir-v33 (gerbang dengar penuh): nota baru tanpa cap TIDAK disentuh; perangkat yang absen menangkapnya lewat hitungan server
tokoBaru('2026-11-10T03:00:00Z'); S.tulis('penjualan', 'p1', notaN('p1', 1000), true);
var A1 = new Perangkat('mac-t1'); A1.buka(); var B1 = new Perangkat('ipad-t1'); B1.buka(); B1.tutup(); maju(MNT);
S.perangkat = [hpKasir('kasir-v32')]; A1.tetap(); tuntas();
S.tulis('penjualan', 'k1', notaN('k1', 15000), false); tuntas(); maju(2000);
ok('T1 gerbang HP kasir lama: nota tanpa cap terlihat seketika (dengar penuh) dan TIDAK disentuh — tanpa tulisan ganda, dan kirim ulang HP v32 tidak bertabrakan dengan cap',
  keadaanK(A1, 'penjualan').mode === 'penuh' && memId(A1, 'penjualan').indexOf('k1') >= 0 && A1.sentuhN === 0 && S.kol('penjualan').k1.cap === undefined && (A1.sesi._G.temuan.penjualan || {}).lewat === 1,
  J([A1.sentuhN, S.kol('penjualan').k1, A1.sesi._G.temuan]));
S.perangkat = [hpKasir('kasir-v33')]; A1.tetap(); tuntas(); maju(2 * JM); klaimHariIni(); B1.buka(); maju(20000); tuntas();
ok('T1: perangkat yang ABSEN selama gerbang (iPad) menangkap nota tanpa cap itu lewat hitungan server → baca penuh', memId(B1, 'penjualan').indexOf('k1') >= 0 && samaServer(B1) && B1.periksa.penjualan === true, J(beda(B1)));
A1.tutup(); B1.tutup();

// ---- T2 · satu catatan ber-capServer tahun 2099 (Console / klien rusak — rules tidak memeriksa cap koleksi hemat)
tokoBaru('2026-11-10T03:00:00Z'); S.tulis('penjualan', 'p1', notaN('p1', 1000), true);
var A2 = new Perangkat('mac-t2'); A2.buka(); var B2 = new Perangkat('ipad-t2'); B2.buka(); var skew2 = A2.sesi._G.skew;
S.kol('penjualan').z = { data: notaN('z', 5), cap: Z('2099-01-01T00:00:00Z') }; S.siar('penjualan', 'z'); tuntas();
// tanpa gema denyut baru di antaranya: hitungan berkala (30 menit) mencatat tanda air Wd dengan jam server perangkat ini
maju(31 * MNT); A2.sesi.tik(); tuntas(); maju(20000); tuntas();
var rk2 = A2.R.k.penjualan;
ok('T2 cap 2099: jam server perangkat TIDAK ikut ke 2099 (selisih jam hanya dari gema denyut), tanda air ≤ jam server + 10 menit, batas delta di masa kini, hari kuota benar',
  A2.sesi._G.skew === skew2 && Math.max(rk2.Wt || 0, rk2.Wd || 0) <= S.jam + 10 * MNT && rk2.B < S.jam && A2.sesi.keadaan().hari === hbHariKuota(S.jam) && memId(A2, 'penjualan').indexOf('z') >= 0,
  J({ skew: A2.sesi._G.skew, Wt: rk2.Wt, Wd: rk2.Wd, B: rk2.B, jam: S.jam, hari: A2.sesi.keadaan().hari }));
A2.tutup(); maju(26 * JM); klaimHariIni(); B2.tulis('penjualan', 'p2', notaN('p2', 2000)); tuntas(); A2.buka(); maju(5000); tuntas();
var dA2 = A2.L.filter(function (L) { return L.aktif && L.jenis === 'delta' && L.k === 'penjualan'; });
ok('T2: besoknya nota baru dari perangkat lain sampai lewat DELTA (batas delta sekitar jam server, bukan tahun 2098), tanpa baca penuh',
  memId(A2, 'penjualan').indexOf('p2') >= 0 && dA2.length === 1 && dA2[0].B < S.jam && dA2[0].B > S.jam - 3 * HR && !A2.L.some(function (L) { return L.aktif && L.jenis === 'penuh'; }),
  J({ delta: dA2.map(function (L) { return new Date(L.B).toISOString(); }), mem: memId(A2, 'penjualan') }));
A2.tutup(); B2.tutup();

// ---- T3 · catatan LAHIR ULANG tanpa cap sesudah batu nisannya (HP kasir v32 mengirim ulang karcis yang jawabannya hilang, sesudah owner menghapusnya)
tokoBaru('2026-11-10T03:00:00Z');
S.jam -= 3 * HR; S.tulis('penjualan', 'x', notaN('x', 7000), false); S.tulis('penjualan', 'y', notaN('y', 8000, '2026-08-31'), false); S.jam += 3 * HR;   // nota lama tanpa cap
S.tulis('penjualan', 'p1', notaN('p1', 1000), true);
var A3 = new Perangkat('mac-t3'); A3.buka(); var B3 = new Perangkat('ipad-t3'); B3.buka();
A3.hapusDok('penjualan', 'x'); tuntas(); maju(1000);
ok('T3: owner menghapus nota lama x (batu nisan di batch yang sama) → hilang di kedua perangkat', memId(A3, 'penjualan').indexOf('x') < 0 && memId(B3, 'penjualan').indexOf('x') < 0 && !!S.nisan['penjualan|x']);
S.tulis('penjualan', 'x', notaN('x', 7000), false); tuntas();
maju(31 * MNT); A3.sesi.tik(); B3.sesi.tik(); tuntas(); maju(20000); tuntas();
ok('T3 LAHIR ULANG: hitungan server beda → baca penuh → nota ADA di snapshot server padahal nisannya berlaku → tampil lagi di kedua perangkat & disentuh (cap jam server > nisan)',
  memId(A3, 'penjualan').indexOf('x') >= 0 && memId(B3, 'penjualan').indexOf('x') >= 0 && typeof S.kol('penjualan').x.cap === 'number' && S.kol('penjualan').x.cap > S.nisan['penjualan|x'].cap && samaServer(A3) && samaServer(B3),
  J({ A: memId(A3, 'penjualan'), B: memId(B3, 'penjualan'), x: S.kol('penjualan').x, nisan: S.nisan['penjualan|x'], kA: keadaanK(A3, 'penjualan'), kB: keadaanK(B3, 'penjualan') }));
// bulan terkunci (Console): tidak bisa disentuh → tiap perangkat memegang BUKTI dari baca penuhnya sendiri; hitungan cocok, tidak membaca penuh berulang
// (hari kuota berikutnya — hari ini dua baca penuh otomatis per koleksi sudah terpakai: perangkat baru + x)
maju(24 * JM); klaimHariIni(); A3.gema(); B3.gema(); A3.tetap(); B3.tetap(); tuntas();
S.kunci = { y: true }; S.hapus('penjualan', 'y', true); tuntas(); maju(1000); var tY = S.nisan['penjualan|y'].cap;
S.tulis('penjualan', 'y', notaN('y', 8000, '2026-08-31'), false); tuntas();
maju(31 * MNT); A3.sesi.tik(); B3.sesi.tik(); tuntas(); maju(20000); tuntas();
var mulaiA3 = A3.R.hari.mulai.penjualan || 0, mulaiB3 = B3.R.hari.mulai.penjualan || 0;
maju(31 * MNT); A3.sesi.tik(); B3.sesi.tik(); tuntas(); maju(20000); tuntas();
ok('T3 lahir ulang di bulan TERKUNCI (tidak bisa disentuh): bukti baca penuh server di rekam tiap perangkat → tampil; hitungan server cocok → tidak membaca penuh berulang',
  S.kol('penjualan').y.cap === undefined && memId(A3, 'penjualan').indexOf('y') >= 0 && memId(B3, 'penjualan').indexOf('y') >= 0 && A3.R.k.penjualan.lahir.y === tY && B3.R.k.penjualan.lahir.y === tY
  && (A3.R.hari.mulai.penjualan || 0) === mulaiA3 && (B3.R.hari.mulai.penjualan || 0) === mulaiB3 && A3.periksa.penjualan === true && B3.periksa.penjualan === true,
  J({ A: memId(A3, 'penjualan'), lahirA: A3.R.k.penjualan.lahir, mulai: [mulaiA3, A3.R.hari.mulai.penjualan, mulaiB3, B3.R.hari.mulai.penjualan], kA: keadaanK(A3, 'penjualan') }));
A3.tutup(); A3.buka(); maju(5000); tuntas();
ok('T3: bukti lahir ulang TAHAN muat ulang (rekam) — sesudah dibuka lagi y tetap tampil', memId(A3, 'penjualan').indexOf('y') >= 0 && samaServer(A3), J(beda(A3)));
S.hapus('penjualan', 'y', true); tuntas(); maju(1000);
ok('T3: dihapus LAGI (nisan lebih baru dari buktinya) → tersembunyi lagi, bukti lama dibuang', memId(A3, 'penjualan').indexOf('y') < 0 && memId(B3, 'penjualan').indexOf('y') < 0 && !('y' in (A3.R.k.penjualan.lahir || {})), J([memId(A3, 'penjualan'), A3.R.k.penjualan.lahir]));
A3.tutup(); B3.tutup(); S.kunci = null;

// ---- T4 · temuan pendeteksi yang GAGAL dikirim disimpan & dicoba lagi (dulu dibuang diam-diam)
tokoBaru('2026-11-10T03:00:00Z');
S.jam -= 3 * HR; S.tulis('penjualan', 'p1', notaN('p1', 1000), true); S.jam += 3 * HR; S.tulis('penjualan', 'p0', notaN('p0', 500), true);
var A4 = new Perangkat('mac-t4'); A4.buka(); var B4 = new Perangkat('ipad-t4'); B4.buka();
S.tulis('penjualan', 'p1', notaN('p1', 99000), 'tetap'); tuntas();   // Console mengubah nota LAMA (cap di luar jendela delta) tanpa menyentuh cap
A4.sentuhGagal = 1; A4.sesi.bacaPenuh(['penjualan'], 'owner mengubah data lewat Console', true); tuntas(); maju(20000); tuntas();
var u4 = J(A4.R.ulang || {});
ok('T4: sentuhan yang gagal dikirim DISIMPAN di rekam perangkat (bukan dibuang); perangkat lain belum menerimanya', /"p1"/.test(u4) && memDok(B4, 'penjualan', 'p1').hargaTotal === 1000 && memDok(A4, 'penjualan', 'p1').hargaTotal === 99000, u4);
maju(MNT); A4.sesi.tik(); tuntas();
ok('T4: dicoba lagi (tiap menit) → tersentuh → perangkat lain menerimanya lewat delta; antrean temuan kosong', memDok(B4, 'penjualan', 'p1').hargaTotal === 99000 && !/"p1"/.test(J(A4.R.ulang || {})), J([memDok(B4, 'penjualan', 'p1'), A4.R.ulang]));
A4.tutup(); B4.tutup();

// ---- T5 · batas pendengar nisan = jam baca penuh terakhir (koleksi yang sepi tidak menahan Bn di tulisan terakhirnya)
tokoBaru('2026-10-08T03:00:00Z'); S.tulis('pengeluaranHarian', 'h1', { id: 'h1', tanggal: '2026-10-08', nominal: 1 }, true);
S.jam = Z('2027-03-01T03:00:00Z'); S.tulis('penjualan', 'p1', notaN('p1', 1, '2027-03-01'), true); klaimHariIni();
var A5 = new Perangkat('mac-t5'); A5.buka();
var N5 = A5.L.filter(function (L) { return L.aktif && L.jenis === 'nisan'; }).map(function (L) { return L.B; });
ok('T5 batas nisan dari jam baca penuh terakhir (1 Mar 2027 − 60 menit), BUKAN cap tertinggi pengeluaranHarian (8 Okt 2026) — nisan tidak dibaca ulang berbulan-bulan tiap buka',
  N5.length === 1 && N5[0] >= S.jam - JM - MNT && A5.R.k.pengeluaranHarian.Wt < Z('2026-10-09T00:00:00Z'), J({ N: N5.map(function (x) { return new Date(x).toISOString(); }) }));
// jam perangkat MELOMPAT maju 1 hari sesudah gema denyut, lalu baca penuh selesai: "baca penuh terakhir" tidak tercatat di masa depan (Bn tetap di masa kini)
A5.geser += HR; A5.sesi.bacaPenuh(['penjualan'], 'tombol', true); tuntas(); maju(1000);
ok('T5: jam perangkat melompat maju sesudah gema → jam baca penuh terakhir dijepit ≤ jam server gema terakhir + 10 menit (batas nisan tidak pernah di masa depan)',
  A5.R.k.penjualan.totalPada <= S.jam + 10 * MNT && A5.R.k.penjualan.totalPada >= S.jam - 10 * MNT, J({ total: new Date(A5.R.k.penjualan.totalPada).toISOString(), jam: new Date(S.jam).toISOString() }));
A5.tutup();

// ---- T6 · sesudah tutup buku: catatan yang DIARSIPKAN (hilang dari server tanpa batu nisan) bukan "hilang tanpa kabar"
tokoBaru('2027-01-02T09:00:00Z');
S.jam -= 2 * HR * 24; ['a1', 'a2', 'a3'].forEach(function (id, i) { S.tulis('penjualan', id, notaN(id, 100 + i, '2026-12-3' + i), true); }); S.jam += 2 * HR * 24;
S.tulis('penjualan', 'b1', notaN('b1', 9, '2027-01-02'), true);
var A6 = new Perangkat('mac-t6'); A6.buka(); A6.tutup(); var n6 = Object.keys(S.nisan).length;
S.acara = [{ tahun: 2026, status: 'selesai', paraf: { pada: '2027-01-02T10:00:00Z' } }]; ['a1', 'a2', 'a3'].forEach(function (id) { S.hapus('penjualan', id, false); });
maju(2 * JM); klaimHariIni(); A6.buka(); maju(20000); tuntas();
ok('T6 tutup buku berubah selagi perangkat tertutup: baca penuh, catatan 2026 yang diarsipkan hilang dari memori TANPA batu nisan baru (bukan temuan "hilang tanpa kabar")',
  samaServer(A6) && Object.keys(S.nisan).length === n6 && A6.nisanTulis === 0 && (A6.sesi._G.temuan.penjualan || {}).arsip === 3 && !(A6.sesi._G.temuan.penjualan || {}).hilang,
  J({ beda: beda(A6), nisan: Object.keys(S.nisan), temuan: A6.sesi._G.temuan }));
A6.tutup();

// ---- T6b–T6g · (audit P5, 8 Okt) hemat baca × arsip tutup buku. Perangkat owner yang TERTUTUP selama ritual masih menyimpan catatan 2026 yang diarsipkan (arsip
//      TANPA batu nisan — hanya baca penuh yang membuangnya); saldo pembukanya bercap baru. Dulu: pil "memuat…" lepas dari simpanan, S membawa saldo pembuka
//      → memori DOBEL (catatan 2026 + saldo pembuka); baca penuh karena tutup buku tergolong otomatis → ditahan rem kuota → dobel bertahan sampai reset kuota;
//      berita acara dari simpanan (basi) → tutup buku tampak tidak berubah → S jalan, dobel juga. Angka KOTAK PASIR.
var nT6 = 0, LAMA6 = ['a1', 'a2', 'a3', 'r1'];
var pm6 = function (id, n, tgl, x) { return Object.assign({ id: id, tanggal: tgl, nominal: n, namaPelanggan: 'Pelanggan Contoh' }, x || {}); };
var jml6 = function (p) { return (p.mem.piutangMutasi || []).reduce(function (a, d) { return a + (Number(d.nominal) || 0); }, 0); };
// DOBEL = memori memuat saldo pembuka DAN catatan 2026 yang sudah diarsipkan sekaligus
var dobel6 = function (p) { var m = memId(p, 'piutangMutasi'); return m.indexOf('pb2027') >= 0 && LAMA6.some(function (id) { return m.indexOf(id) >= 0; }); };
var aktif6 = function (p, jenis) { return p.L.some(function (L) { return L.aktif && L.jenis === jenis && L.k === 'piutangMutasi'; }); };
function bonLama6() {
  tokoBaru('2027-01-02T09:00:00Z');
  S.jam -= 30 * HR; ['a1', 'a2', 'a3'].forEach(function (id, i) { S.tulis('piutangMutasi', id, pm6(id, 100001, '2026-12-0' + (i + 1)), true); }); S.jam += 30 * HR;
  S.jam -= 2 * JM; S.tulis('piutangMutasi', 'r1', pm6('r1', 0, '2026-12-31'), true); S.jam += 2 * JM;
}
function ritual6() {
  bonLama6(); nT6 += 1; var P = new Perangkat('hp-owner-t6-' + nT6); P.buka(); maju(20000); P.tutup(); maju(30 * MNT);
  // RITUAL di perangkat lain: saldo pembuka (bercap) ditulis, catatan 2026 DIARSIPKAN = dihapus TANPA batu nisan, berita acara selesai
  S.acara = [{ tahun: 2026, status: 'berjalan', paraf: { pada: '2027-01-02T09:30:00Z' } }];
  S.tulis('piutangMutasi', 'pb2027', pm6('pb2027', 300003, '2026-12-31', { tutupBuku: true, tahunDari: 2026 }), true);
  LAMA6.forEach(function (id) { S.hapus('piutangMutasi', id, false); });
  S.acara = [{ tahun: 2026, status: 'selesai', paraf: { pada: '2027-01-02T09:30:00Z' } }];
  maju(JM); klaimHariIni(); return P;
}
// baca penuh LAMBAT seperti SDK: dipasang → hanya snapshot simpanan; fTiba → jawaban server masuk simpanan (saldo pembuka ikut) tapi catatan yang tidak ada di
// server MENUNGGU limbo (snapshot F masih "dari simpanan"); fLimbo → limbo selesai: catatan arsip dibuang, F terkini
function fLambat(P) { P.fTahan = []; P.dengar = function (jenis, k, B, cb) {
  if (jenis !== 'penuh') return Perangkat.prototype.dengar.call(this, jenis, k, B, cb);
  var self = this; var L = { jenis: jenis, k: k, B: B, cb: cb, aktif: true, terkini: false }; this.L.push(L); this.fTahan.push(L);
  antri(function () { if (L.aktif && Object.keys(self.c(k)).length) cb(self.snap(L)); }); return function () { L.aktif = false; }; }; }
function fTiba(P) { P.fTahan.forEach(function (L) { if (!L.aktif) return; var C = P.c(L.k), K = S.kol(L.k);
  Object.keys(K).forEach(function (id) { if (!(C[id] && C[id].tunda)) C[id] = { data: salin(K[id].data), cap: K[id].cap }; }); P.emit(L.k); }); tuntas(); }
function fLimbo(P) { P.fTahan.forEach(function (L) { if (!L.aktif) return; var C = P.c(L.k), K = S.kol(L.k);
  Object.keys(C).forEach(function (id) { if (!C[id].tunda && !K[id]) delete C[id]; }); L.terkini = true; P.emit(L.k); }); P.fTahan = []; delete P.dengar; tuntas(); }

// T6b · baca penuh LAMBAT: memori tidak pernah dobel, pil memuat tetap, tanpa S, sampai baca penuh selesai
var P6 = ritual6(); fLambat(P6); P6.buka(); maju(3000);
var K6b = keadaanK(P6, 'piutangMutasi'), bl6b = P6.sesi.belumLengkap().piutangMutasi || null;
var s6b0 = { dobel: dobel6(P6), mem: memId(P6, 'piutangMutasi'), siap: !!P6.siap.piutangMutasi, mode: K6b.mode, sebab: K6b.sebab, S: aktif6(P6, 'delta'), F: aktif6(P6, 'penuh'), belum: bl6b };
ok('T6b (audit P5) tertutup selama ritual, baca penuh lambat: memori = isi simpanan (catatan 2026 TANPA saldo pembuka — tidak dobel), pil MEMUAT tetap, tanpa pendengar ubahan (S), baca penuh karena tutup buku berjalan; kelengkapan "sedang dibaca penuh"',
  !s6b0.dobel && J(s6b0.mem) === J(LAMA6) && !s6b0.siap && s6b0.mode === 'total' && s6b0.sebab === HB_SEBAB_BK && !s6b0.S && s6b0.F && !!bl6b && bl6b.jenis === 'periksa' && /sedang dibaca penuh/.test(bl6b.sebab), J(s6b0));
P6.tulis('piutangMutasi', 'w1', pm6('w1', 7, '2027-01-02')); tuntas();
fTiba(P6); maju(1000);
var s6b1 = { dobel: dobel6(P6), mem: memId(P6, 'piutangMutasi'), simpanan: Object.keys(P6.c('piutangMutasi')).sort(), siap: !!P6.siap.piutangMutasi };
ok('T6b: jawaban server tiba SEBELUM limbo membuang catatan arsip (simpanan = catatan 2026 + saldo pembuka) → memori TETAP beku (tidak dobel), tulisan perangkat ini sendiri tetap tampil, pil memuat tetap',
  !s6b1.dobel && s6b1.simpanan.indexOf('pb2027') >= 0 && s6b1.simpanan.indexOf('a1') >= 0 && J(s6b1.mem) === J(LAMA6.concat(['w1']).sort()) && !s6b1.siap, J(s6b1));
fLimbo(P6); maju(20000);
var s6b2 = { mem: memId(P6, 'piutangMutasi'), jml: jml6(P6), siap: semua(P6, function (k) { return P6.siap[k]; }), periksa: P6.periksa.piutangMutasi, temuan: P6.sesi._G.temuan.piutangMutasi || {},
  nisanTulis: P6.nisanTulis, rk: P6.R.k.piutangMutasi, S: aktif6(P6, 'delta') };
ok('T6b: baca penuh selesai → memori = server (saldo pembuka + tulisan baru; catatan 2026 hilang), siap, terperiksa, S terpasang; arsip tanpa batu nisan; rekam mencatat tutup bukunya & tidak bercampur',
  J(s6b2.mem) === '["pb2027","w1"]' && s6b2.jml === 300010 && s6b2.siap && s6b2.periksa === true && s6b2.temuan.arsip === 4 && !s6b2.temuan.hilang && s6b2.nisanTulis === 0
  && s6b2.rk.bk === hbSidikBk(S.acara) && !s6b2.rk.bkCampur && s6b2.S && samaServer(P6), J(s6b2));
P6.tutup();
// T6b · rem kuota AKTIF: perangkat ritual melapor ±45 rb baca hari kuota ini → baca penuh OTOMATIS ditunda; baca penuh karena tutup buku TIDAK
var Q6 = ritual6();
S.perangkat = [{ id: 'mac-ritual', nama: 'Mac contoh', aplikasi: 'baru', versi: 'baru-c1', pada: new Date(S.jam - MNT).toISOString(), akun: 'owner@x', hemat: { nyala: true, hari: hbHariKuota(S.jam), baca: 45000 } }];
fLambat(Q6); Q6.buka(); maju(3000);
var KQ6 = keadaanK(Q6, 'piutangMutasi');
var q6a = { rem: hbRem({ perkiraan: hbPerkiraanToko(S.perangkat, hbHariKuota(S.jam), Q6.nama, 0), ukuran: 4 }).boleh, wajib: KQ6.wajibTotal, mode: KQ6.mode, F: aktif6(Q6, 'penuh'), dobel: dobel6(Q6), siap: !!Q6.siap.piutangMutasi,
  otomatis: (Q6.R.hari.otomatis || {}).piutangMutasi || 0 };
fTiba(Q6); fLimbo(Q6); maju(20000);
var q6b = { mem: memId(Q6, 'piutangMutasi'), siap: !!Q6.siap.piutangMutasi, wajib: keadaanK(Q6, 'piutangMutasi').wajibTotal, otomatis: (Q6.R.hari.otomatis || {}).piutangMutasi || 0 };
ok('T6b rem kuota AKTIF (denyut perangkat ritual 45 rb baca hari ini — baca penuh otomatis ditunda): baca penuh karena tutup buku TETAP jalan seperti tombol (tidak turun ke delta, tidak dobel, tidak dihitung otomatis) dan selesai tanpa ketukan',
  q6a.rem === false && q6a.wajib === '' && q6a.mode === 'total' && q6a.F && !q6a.dobel && !q6a.siap && J(q6b.mem) === '["pb2027"]' && q6b.siap && q6b.wajib === '' && q6b.otomatis === q6a.otomatis, J([q6a, q6b]));
Q6.tutup(); S.perangkat = [];

// T6c · berita acara dari SIMPANAN dulu (basi: belum ada tutup buku → tampak tidak berubah), baru kemudian dari server
var C6 = ritual6(); C6.buka({ tetap: false }); tuntas(); C6.gema();
C6.sesi.setelTetap({ perangkat: [], acara: [], klaim: salin(S.klaim), acaraServer: false }); tuntas(); maju(1000);
var c6a = { dobel: dobel6(C6), mem: memId(C6, 'piutangMutasi'), simpanan: Object.keys(C6.c('piutangMutasi')).sort(), siap: !!C6.siap.piutangMutasi, S: aktif6(C6, 'delta'), periksa: C6.periksa.piutangMutasi };
ok('T6c (audit P5) berita acara dari SIMPANAN dulu (basi — tutup buku tampak tidak berubah): tanpa pendengar ubahan (S), saldo pembuka tidak masuk simpanan maupun memori (tidak dobel), pil memuat tetap, belum terperiksa',
  !c6a.dobel && J(c6a.mem) === J(LAMA6) && c6a.simpanan.indexOf('pb2027') < 0 && !c6a.siap && !c6a.S && c6a.periksa === false, J(c6a));
C6.tetap(); maju(20000);
var c6b = { mem: memId(C6, 'piutangMutasi'), siap: !!C6.siap.piutangMutasi, rk: C6.R.k.piutangMutasi };
ok('T6c: berita acara dari SERVER tiba → tutup buku berubah → baca penuh → memori = server (saldo pembuka saja), siap', J(c6b.mem) === '["pb2027"]' && c6b.siap && c6b.rk.bk === hbSidikBk(S.acara) && samaServer(C6), J(c6b));
C6.tutup();

// T6d · baca penuh sesudah tutup buku TERPUTUS (aplikasi ditutup di tengah limbo — simpanan kini catatan 2026 + saldo pembuka): sesi berikut memori mulai KOSONG
var D6 = ritual6(); fLambat(D6); D6.buka(); maju(3000); fTiba(D6); maju(1000);
var d6a = { simpanan: Object.keys(D6.c('piutangMutasi')).sort(), campur: !!D6.R.k.piutangMutasi.bkCampur };
D6.tutup(); maju(5 * MNT); fLambat(D6); D6.buka(); maju(3000);
var d6b = { mem: memId(D6, 'piutangMutasi'), dobel: dobel6(D6), siap: !!D6.siap.piutangMutasi, F: aktif6(D6, 'penuh'), S: aktif6(D6, 'delta') };
ok('T6d (audit P5) baca penuh sesudah tutup buku terputus di tengah limbo: rekam menandai simpanan BERCAMPUR; sesi berikut memori KOSONG (bukan simpanan yang memuat keduanya — tidak dobel), pil memuat, baca penuh wajib, tanpa S',
  J(d6a.simpanan) === J(LAMA6.concat(['pb2027']).sort()) && d6a.campur && !d6b.dobel && J(d6b.mem) === '[]' && !d6b.siap && d6b.F && !d6b.S, J([d6a, d6b]));
fTiba(D6); fLimbo(D6); maju(20000);
ok('T6d: baca penuh selesai → memori = server, siap, tanda bercampur dibuang dari rekam', J(memId(D6, 'piutangMutasi')) === '["pb2027"]' && !!D6.siap.piutangMutasi && !D6.R.k.piutangMutasi.bkCampur && samaServer(D6),
  J([memId(D6, 'piutangMutasi'), D6.R.k.piutangMutasi]));
fLambat(D6); D6.sesi.bacaPenuh(['piutangMutasi'], 'tombol "Baca penuh sekarang"', true); maju(1000);
// sanggahan P5: catatan baru dari perangkat lain tiba lewat S selama tombol baca penuh → simpanan berubah → memori dihitung ulang (pendengar simpanan kini hanya
// berbunyi bila simpanannya berubah — tanpa ini kerusakan "bercampur sepanjang sesi" diam)
S.tulis('piutangMutasi', 'x6', pm6('x6', 5, '2027-01-02'), true); tuntas();
var d6c = { mem: memId(D6, 'piutangMutasi'), F: aktif6(D6, 'penuh') };
fTiba(D6); maju(1000); d6c.tiba = memId(D6, 'piutangMutasi'); d6c.S = aktif6(D6, 'delta'); fLimbo(D6); maju(20000);
ok('T6d: tombol baca penuh sesudahnya di sesi yang sama → memori TETAP selama baca penuh itu (tidak dikosongkan lagi — simpanan sudah tidak bercampur), catatan baru perangkat lain masuk seketika, S tetap terpasang',
  J(d6c.mem) === '["pb2027","x6"]' && d6c.F && J(d6c.tiba) === '["pb2027","x6"]' && d6c.S && J(memId(D6, 'piutangMutasi')) === '["pb2027","x6"]', J(d6c));
D6.tutup();
// T6g · simpanan bercampur dibuka TANPA internet: pil tidak menggantung, memori kosong (bukan dobel), kabar mengaku; tersambung → baca penuh wajib → server
var H6 = ritual6(); fLambat(H6); H6.buka(); maju(3000); fTiba(H6); maju(1000); H6.tutup(); delete H6.dengar;
H6.online = false; H6.buka({ tetap: false }); tuntas();
var h6a = { siap: !!H6.siap.piutangMutasi, mem: memId(H6, 'piutangMutasi'), dobel: dobel6(H6), kabar: H6.sesi.keadaan().kabar, belum: H6.sesi.belumLengkap().piutangMutasi || null };
H6.sambung(); H6.gema(); H6.tetap(); maju(20000);
ok('T6g (audit P5) simpanan BERCAMPUR dibuka tanpa internet: siap (pil tidak menggantung) dengan memori KOSONG (tidak dobel); kabar & kelengkapan "disembunyikan … tanpa internet" (sanggahan kedua: kosong DISEBUT); tersambung → baca penuh → memori = server',
  h6a.siap && J(h6a.mem) === '[]' && !h6a.dobel && /^Angka disembunyikan/.test(h6a.kabar) && /tanpa internet/.test(h6a.kabar) && !!h6a.belum && /^disembunyikan/.test(h6a.belum.sebab) && /tanpa internet/.test(h6a.belum.sebab)
  && J(memId(H6, 'piutangMutasi')) === '["pb2027"]' && samaServer(H6), J([h6a, memId(H6, 'piutangMutasi')]));
H6.tutup();

// T6e · perangkat yang MENJALANKAN ritual (dengar penuh selama berjalan, baca penuhnya belum selesai): memori mengikuti tulisan ritualnya sendiri seperti dulu
bonLama6(); var E6 = new Perangkat('mac-ritual-t6e'); E6.buka(); maju(20000);
fLambat(E6); S.acara = [{ tahun: 2026, status: 'berjalan', paraf: { pada: '2027-01-02T09:30:00Z' } }]; E6.tetap(); maju(1000);
var e6a = { mode: keadaanK(E6, 'piutangMutasi').mode, siap: !!E6.siap.piutangMutasi, campur: !!E6.R.k.piutangMutasi.bkCampur };
E6.tulis('piutangMutasi', 'pb2027', pm6('pb2027', 300003, '2026-12-31', { tutupBuku: true, tahunDari: 2026 })); tuntas();
// arsip (firebase.js arsipkanBerkas): hapus di simpanan perangkat ini sendiri, TANPA batu nisan dan tanpa catatHapus
LAMA6.forEach(function (id) { delete E6.c('piutangMutasi')[id]; S.hapus('piutangMutasi', id, false); }); E6.emit('piutangMutasi'); tuntas();
var e6b = { mem: memId(E6, 'piutangMutasi'), dobel: dobel6(E6) };
fTiba(E6); fLimbo(E6); maju(20000);
S.acara = [{ tahun: 2026, status: 'selesai', paraf: { pada: '2027-01-02T09:30:00Z' } }]; E6.tetap(); maju(20000);
var e6c = { mode: keadaanK(E6, 'piutangMutasi').mode, campur: !!E6.R.k.piutangMutasi.bkCampur, F: aktif6(E6, 'penuh'), bk: E6.R.k.piutangMutasi.bk };
ok('T6e (audit P5) perangkat yang MENJALANKAN ritual (dengar penuh, baca penuhnya belum selesai): memori mengikuti tulisan ritualnya sendiri (saldo pembuka masuk, catatan arsip keluar) — TIDAK dibekukan, tidak dobel; sesudah selesai kembali delta tanpa baca penuh lagi, rekam tidak bercampur',
  e6a.mode === 'penuh' && e6a.siap && e6a.campur && !e6b.dobel && J(e6b.mem) === '["pb2027"]' && e6c.mode === 'delta' && !e6c.campur && !e6c.F && e6c.bk === hbSidikBk(S.acara) && samaServer(E6), J([e6a, e6b, e6c]));
E6.tutup();

// T6f · baca penuh wajib karena tutup buku GAGAL (server menolak): pil lepas dengan kabar, memori tetap beku (tidak dobel); diulang sesudah 10 menit seperti baca
//       penuh otomatis — bukan di tiap kabar koleksi tetap (tiap ulang = seluruh koleksi dibaca lagi)
var G6 = ritual6(); G6.fGalat = 'unavailable'; G6.buka(); maju(3000);
var g6m = function () { return (G6.R.hari.mulai || {}).piutangMutasi || 0; };
var g6a = { siap: !!G6.siap.piutangMutasi, dobel: dobel6(G6), mem: memId(G6, 'piutangMutasi'), mulai: g6m(), wajib: keadaanK(G6, 'piutangMutasi').wajibTotal, belum: G6.sesi.belumLengkap().piutangMutasi || null, S: aktif6(G6, 'delta') };
for (var i6f = 0; i6f < 3; i6f++) { maju(MNT); G6.tetap(); tuntas(); }
var g6b = { mulai: g6m(), dobel: dobel6(G6) };
G6.fGalat = null; maju(10 * MNT); G6.tetap(); maju(20000);
var g6c = { mem: memId(G6, 'piutangMutasi'), mulai: g6m() };
ok('T6f (audit P5) baca penuh karena tutup buku GAGAL: pil lepas (tidak menggantung), memori tetap catatan 2026 tanpa saldo pembuka (tidak dobel), tanpa S, kelengkapan "gagal dibaca penuh"; tidak diulang tiap kabar sebelum 10 menit; sesudahnya dibaca penuh lagi → memori = server',
  g6a.siap && !g6a.dobel && J(g6a.mem) === J(LAMA6) && !g6a.S && /^baca penuh gagal \(unavailable\)/.test(g6a.wajib) && !!g6a.belum && /^gagal dibaca penuh/.test(g6a.belum.sebab)
  && g6b.mulai === g6a.mulai && !g6b.dobel && J(g6c.mem) === '["pb2027"]' && g6c.mulai === g6a.mulai + 1, J([g6a, g6b, g6c]));
G6.tutup();
// ---- T6e2–T6j · sanggahan P5 (8 Okt). Angka KOTAK PASIR.
// T6e2 · perangkat yang MENJALANKAN ritual ditutup di tengah ritual (K11 TIDAK MUAT: arsip berhenti, Lanjutkan sesudah reset kuota) lalu dibuka lagi selagi
//        server DIAM (kuota baca habis): berita acara dari simpanan menyebut tutup buku berjalan → memori = simpanannya (sisa arsip terbaca), bukan kosong; pil
//        lepas sesudah 30 detik dengan kabar, uang-kritis menolak; server menjawab (masih terkunci) → dengar penuh, memori = simpanan = server
bonLama6(); var M2 = new Perangkat('mac-ritual-t6e2'); M2.buka(); maju(20000); var pgM2 = { id: 'mac-ritual-t6e2', nama: 'Mac contoh' };
S.acara = [{ tahun: 2026, status: 'berjalan', paraf: { pada: '2027-01-02T09:30:00Z' }, pemegang: pgM2 }]; M2.tetap(); maju(20000);
M2.tulis('piutangMutasi', 'pb2027', pm6('pb2027', 300003, '2026-12-31', { tutupBuku: true, tahunDari: 2026 })); tuntas();
S.acara = [{ tahun: 2026, status: 'terkunci', paraf: { pada: '2027-01-02T09:30:00Z' }, pemegang: pgM2 }]; M2.tetap(); tuntas();
delete M2.c('piutangMutasi').a1; S.hapus('piutangMutasi', 'a1', false); M2.emit('piutangMutasi'); tuntas();   // arsip berhenti sesudah a1 (kuota habis)
var e2a = { campur: !!M2.R.k.piutangMutasi.bkCampur, simpanan: Object.keys(M2.c('piutangMutasi')).sort(), mem: memId(M2, 'piutangMutasi') }, acaraM2 = salin(S.acara);
M2.tutup(); maju(JM); M2.diam = true; M2.buka({ tetap: false }); tuntas();
var e2b = memId(M2, 'piutangMutasi');
M2.sesi.setelTetap({ perangkat: [], acara: acaraM2, klaim: salin(S.klaim), acaraServer: false }); tuntas(); maju(1000);
var e2c = { mem: memId(M2, 'piutangMutasi'), siap: !!M2.siap.piutangMutasi, mode: keadaanK(M2, 'piutangMutasi').mode };
maju(30000);
var e2d = { siap: semua(M2, function (k) { return M2.siap[k]; }), mem: memId(M2, 'piutangMutasi'), kabar: M2.sesi.keadaan().kabar, belum: M2.sesi.belumLengkap().piutangMutasi || null, periksa: M2.periksa.piutangMutasi };
var US2e = null; M2.sesi.pastikanSegar().then(function (r) { US2e = r; }); tuntas();
M2.jawab(); M2.gema(); M2.tetap(); maju(20000);
var e2e = { mode: keadaanK(M2, 'piutangMutasi').mode, mem: memId(M2, 'piutangMutasi'), periksa: M2.periksa.piutangMutasi, kabar: M2.sesi.keadaan().kabar };
ok('T6e2 (sanggahan P5) Mac PEMEGANG ritual ditutup di tengah ritual (simpanan bertanda bercampur), dibuka lagi saat server diam: sebelum berita acara terbaca memori kosong; berita acara dari simpanan "terkunci" dengan pemegang = Mac ini → memori = simpanannya (sisa arsip a2, a3, r1 terbaca — dulu KOSONG), pil memuat',
  e2a.campur && J(e2a.simpanan) === '["a2","a3","pb2027","r1"]' && J(e2a.mem) === J(e2a.simpanan) && J(e2b) === '[]' && J(e2c.mem) === J(e2a.simpanan) && !e2c.siap && e2c.mode === 'penuh', J([e2a, e2b, e2c]));
ok('T6e2: server diam 30 detik → pil lepas (tidak menunggu reset kuota berjam-jam), memori tetap simpanannya, kabar & kelengkapan "server belum menjawab", belum terperiksa, uang-kritis menolak dengan sebab yang sama; server menjawab (masih terkunci) → dengar penuh, memori = server, terperiksa, kabar basi dibuang',
  e2d.siap && J(e2d.mem) === J(e2a.simpanan) && /^Server belum menjawab/.test(e2d.kabar) && !!e2d.belum && e2d.belum.sebab === HB_SEBAB_SERVER_DIAM && e2d.periksa === false
  && US2e && !US2e.ok && /server belum menjawab/.test(US2e.pesan) && e2e.mode === 'penuh' && J(e2e.mem) === J(e2a.simpanan) && e2e.periksa === true && !/Server belum menjawab/.test(e2e.kabar) && samaServer(M2),
  J([e2d, US2e, e2e]));
M2.tutup();
// T6e3 · perangkat LAIN yang terbuka selama ritual (dengar penuh), ditutup di tengah ritual, ritual SELESAI selagi tertutup: berita acara dari simpanan masih
//        "terkunci" → memori = keadaan ritual yang terakhir diikutinya; server menjawab "selesai" → memori beku ditentukan ULANG: kosong (bukan catatan 2026 +
//        saldo pembuka) sampai baca penuh selesai → memori = server
bonLama6(); var X3 = new Perangkat('ipad-t6e3'); X3.buka(); maju(20000);
S.acara = [{ tahun: 2026, status: 'terkunci', paraf: { pada: '2027-01-02T09:30:00Z' } }]; X3.tetap(); maju(20000);
S.tulis('piutangMutasi', 'pb2027', pm6('pb2027', 300003, '2026-12-31', { tutupBuku: true, tahunDari: 2026 }), true); S.hapus('piutangMutasi', 'a1', false); tuntas();
var acaraX3 = salin(S.acara), e3a = { campur: !!X3.R.k.piutangMutasi.bkCampur, mem: memId(X3, 'piutangMutasi') };
X3.tutup(); ['a2', 'a3', 'r1'].forEach(function (id) { S.hapus('piutangMutasi', id, false); }); S.acara = [{ tahun: 2026, status: 'selesai', paraf: { pada: '2027-01-02T09:30:00Z' } }];
maju(JM); klaimHariIni();
fLambat(X3); X3.buka({ tetap: false }); tuntas(); X3.gema();
X3.sesi.setelTetap({ perangkat: [], acara: acaraX3, klaim: salin(S.klaim), acaraServer: false }); tuntas(); maju(1000);
var e3b = { mem: memId(X3, 'piutangMutasi'), siap: !!X3.siap.piutangMutasi, kabar: X3.sesi.keadaan().kabar };
X3.tetap(); maju(1000);
var e3c = { mem: memId(X3, 'piutangMutasi'), dobel: dobel6(X3), siap: !!X3.siap.piutangMutasi, mode: keadaanK(X3, 'piutangMutasi').mode, F: aktif6(X3, 'penuh'), S: aktif6(X3, 'delta') };
fTiba(X3); maju(1000); var e3d = memId(X3, 'piutangMutasi'); fLimbo(X3); maju(20000);
var e3e = { mem: memId(X3, 'piutangMutasi'), siap: !!X3.siap.piutangMutasi, campur: !!X3.R.k.piutangMutasi.bkCampur };
ok('T6e3 (sanggahan P5 · kedua) perangkat lain ditutup di tengah ritual, ritual selesai selagi tertutup: berita acara dari simpanan "terkunci" (bukan pemegang, belum dijawab server) → memori KOSONG + kabar "disembunyikan" (dulu = keadaan ritual terakhir = DOBEL bila server tak menjawab); server menjawab "selesai" → tetap kosong selama baca penuh wajib, tanpa S; selesai → memori = server, tanda bercampur dibuang',
  e3a.campur && J(e3a.mem) === '["a2","a3","pb2027","r1"]' && J(e3b.mem) === '[]' && /^Angka disembunyikan/.test(e3b.kabar) && !e3b.siap && J(e3c.mem) === '[]' && !e3c.dobel && !e3c.siap && e3c.mode === 'total' && e3c.F && !e3c.S
  && J(e3d) === '[]' && J(e3e.mem) === '["pb2027"]' && e3e.siap && !e3e.campur && samaServer(X3), J([e3a, e3b, e3c, e3d, e3e]));
X3.tutup();
// T6h · putus internet DI TENGAH baca penuh wajib (koleksi ditahan): pil lepas, kabar mengaku, memori tetap beku (tidak dobel); catatan yang DIHAPUS perangkat
//       ini selagi ditahan hilang dari memori beku; tersambung → baca penuh selesai → memori = server
var P6h = ritual6(); fLambat(P6h); P6h.buka(); maju(3000); fTiba(P6h); maju(1000);
var h6a = { siap: !!P6h.siap.piutangMutasi, dobel: dobel6(P6h), simpanan: Object.keys(P6h.c('piutangMutasi')).sort() };
P6h.putus(); tuntas(); P6h.hapusDok('piutangMutasi', 'r1'); tuntas();
var h6b = { siap: !!P6h.siap.piutangMutasi, mem: memId(P6h, 'piutangMutasi'), dobel: dobel6(P6h), kabar: P6h.sesi.keadaan().kabar, belum: P6h.sesi.belumLengkap().piutangMutasi || null };
P6h.sambung(); P6h.fTahan = []; delete P6h.dengar; maju(20000);
maju(2 * JM); var h6c = { mem: memId(P6h, 'piutangMutasi'), siap: !!P6h.siap.piutangMutasi, periksa: P6h.periksa.piutangMutasi, kabar: P6h.sesi.keadaan().kabar };
ok('T6h (sanggahan P5) putus internet di tengah baca penuh wajib (jawaban server sudah masuk simpanan, limbo belum): pil lepas, kabar "tutup buku berubah … sampai tersambung", memori tetap beku tanpa saldo pembuka (tidak dobel); catatan yang dihapus perangkat ini selagi ditahan hilang dari memori beku; tersambung → memori = server, kabar "tanpa internet" tidak tertinggal (2 jam kemudian kosong)',
  !h6a.siap && !h6a.dobel && h6a.simpanan.indexOf('pb2027') >= 0 && h6b.siap && J(h6b.mem) === '["a1","a2","a3"]' && !h6b.dobel && /^Tanpa internet: tutup buku berubah/.test(h6b.kabar) && !!h6b.belum && /tanpa internet/.test(h6b.belum.sebab)
  && J(h6c.mem) === '["pb2027"]' && h6c.siap && h6c.periksa === true && h6c.kabar === '' && samaServer(P6h), J([h6a, h6b, h6c]));
P6h.tutup();
// T6i · perangkat tertutup selama ritual, koleksinya DENGAR PENUH karena penulis tanpa cap (kasir.html berdenyut semenit lalu): tetap DITAHAN — tanpa S, memori
//       beku (tidak dobel) selama limbo; dengar penuh terkini → memori = server & siap SEBELUM hitungan server menjawab (gerbang uang-kritis menganggap dengar penuh
//       terkini segar — memori tidak boleh tertinggal beku)
var I6 = ritual6(); S.perangkat = [{ id: 'hp-kasir-lama', nama: 'HP kasir contoh', aplikasi: 'kasir', versi: 'kasir-v30', pada: new Date(S.jam - MNT).toISOString(), akun: 'kasir@x' }];
fLambat(I6); I6.hitungTahan = []; I6.buka(); maju(3000);
var KI6 = keadaanK(I6, 'piutangMutasi');
var i6a = { mode: KI6.mode, sebab: KI6.sebab, S: aktif6(I6, 'delta'), siap: !!I6.siap.piutangMutasi, dobel: dobel6(I6), mem: memId(I6, 'piutangMutasi') };
fTiba(I6); maju(1000); var i6b = { dobel: dobel6(I6), mem: memId(I6, 'piutangMutasi'), siap: !!I6.siap.piutangMutasi };
fLimbo(I6); tuntas();
var US6i = null; I6.sesi.pastikanSegar().then(function (r) { US6i = r; }); tuntas();
var i6c = { mem: memId(I6, 'piutangMutasi'), siap: !!I6.siap.piutangMutasi, S: aktif6(I6, 'delta'), tunggu: I6.hitungTahan.length, selesai: !!I6.sesi._K.piutangMutasi.fSelesai, periksa: I6.periksa.piutangMutasi,
  bl: I6.sesi.belumLengkap().piutangMutasi || null, uang: US6i };
I6.hitungTahan.forEach(function (f) { f(); }); I6.hitungTahan = null; maju(20000);
var i6d = { mem: memId(I6, 'piutangMutasi'), mode: keadaanK(I6, 'piutangMutasi').mode, bk: I6.R.k.piutangMutasi.bk, campur: !!I6.R.k.piutangMutasi.bkCampur, S: aktif6(I6, 'delta') };
ok('T6i (sanggahan P5 · kedua) tertutup selama ritual + koleksi dengar penuh karena kasir.html berdenyut: tetap ditahan (tanpa S, pil memuat, memori beku tanpa saldo pembuka — dulu DOBEL selama limbo); dengar penuh terkini → siap, tapi memori TETAP beku selama pengeluaranHarian (baca penuh wajib) belum menjawab — penghalang bersama: belum terperiksa ("menunggu jenis catatan lain"), uang-kritis menolak, tanpa S; semua selesai → serentak: memori = server, S terpasang, rekam mencatat tutup bukunya',
  i6a.mode === 'penuh' && /kasir\.html/.test(i6a.sebab) && !i6a.S && !i6a.siap && !i6a.dobel && J(i6a.mem) === J(LAMA6) && !i6b.dobel && J(i6b.mem) === J(LAMA6) && !i6b.siap
  && J(i6c.mem) === J(LAMA6) && i6c.siap && !i6c.S && i6c.tunggu > 0 && !i6c.selesai && i6c.periksa === false && !!i6c.bl && /jenis catatan lain/.test(i6c.bl.sebab) && i6c.uang && !i6c.uang.ok
  && J(i6d.mem) === '["pb2027"]' && i6d.mode === 'penuh' && i6d.S && i6d.bk === hbSidikBk(S.acara) && !i6d.campur && samaServer(I6),
  J([i6a, i6b, i6c, i6d]));
I6.tutup(); S.perangkat = [];
// T6j · dibuka saat server DIAM (kuota baca habis sampai reset; tersambung), tanpa tutup buku apa pun: pil memuat lepas sesudah 30 detik (dulu menunggu
//       jawaban berita acara dari server TANPA BATAS), memori dari simpanan, belum terperiksa, kelengkapan & uang-kritis menyebut server belum menjawab; server
//       menjawab → terperiksa seperti biasa, kabar basi dibuang
bonLama6(); var J6 = new Perangkat('mac-t6j'); J6.buka(); maju(20000); J6.tutup(); maju(JM);
J6.diam = true; J6.buka({ tetap: false }); tuntas(); J6.sesi.setelTetap({ perangkat: [], acara: [], klaim: salin(S.klaim), acaraServer: false }); tuntas(); maju(29000);
var j6a = { siap: !!J6.siap.piutangMutasi, belum: J6.sesi.belumLengkap().piutangMutasi || null, berubah: J6.berubahN };
maju(2000);
// sanggahan kedua P5 (M20): layar DIKABARI (keluar.berubah → firebase.js jadwalBeriTahu) saat pil lepas sesudah 30 detik — siap saja hanya menaikkan hitungan koleksi
var j6b = { siap: semua(J6, function (k) { return J6.siap[k]; }), mem: memId(J6, 'piutangMutasi'), kabar: J6.sesi.keadaan().kabar, belum: J6.sesi.belumLengkap().piutangMutasi || null, periksa: J6.periksa.piutangMutasi,
  dikabari: J6.berubahN > j6a.berubah };
var US6j = null; J6.sesi.pastikanSegar().then(function (r) { US6j = r; }); tuntas();
J6.jawab(); J6.gema(); J6.tetap(); maju(20000);
var j6c = { periksa: semua(J6, function (k) { return J6.periksa[k] === true; }), belum: J(J6.sesi.belumLengkap()), kabar: J6.sesi.keadaan().kabar };
ok('T6j (sanggahan P5) dibuka saat server diam tanpa tutup buku: 29 detik pil memuat; 30 detik → siap (layar dikabari) dengan memori dari simpanan, kabar & kelengkapan "server belum menjawab" (bukan "tunggu sebentar"), belum terperiksa, uang-kritis menolak; server menjawab → semua terperiksa, kabar basi dibuang',
  !j6a.siap && !!j6a.belum && j6a.belum.sebab !== HB_SEBAB_SERVER_DIAM && j6b.siap && J(j6b.mem) === J(LAMA6) && /^Server belum menjawab/.test(j6b.kabar) && !!j6b.belum && j6b.belum.sebab === HB_SEBAB_SERVER_DIAM
  && j6b.periksa === false && j6b.dikabari && US6j && !US6j.ok && /server belum menjawab/.test(US6j.pesan) && j6c.periksa && !/server belum menjawab/i.test(j6c.belum + j6c.kabar) && samaServer(J6), J([j6a, j6b, US6j, j6c]));
J6.tutup();

// ---- T6k–T6v · SANGGAHAN KEDUA P5 (8 Okt). /baru/ TIDAK punya tirai yang menutup layar: "siap" hanya pil kepala "memuat…" & gambar yang dijarangkan
//      (inti/jadwal.js setelMuat) — layar tetap menggambar memori. MEMORI adalah satu-satunya pelindung: tidak pernah campuran; kosong hanya bila tidak ada keadaan
//      utuh di perangkat, dan itu DISEBUT (kabar & kelengkapan "disembunyikan"). Angka KOTAK PASIR.
var fTibaK = function (P, kk) { P.fTahan.forEach(function (L) { if (!L.aktif || (kk && L.k !== kk)) return; var C = P.c(L.k), K = S.kol(L.k);
  Object.keys(K).forEach(function (id) { if (!(C[id] && C[id].tunda)) C[id] = { data: salin(K[id].data), cap: K[id].cap }; }); P.emit(L.k); }); tuntas(); };
var fLimboK = function (P, kk) { P.fTahan.forEach(function (L) { if (!L.aktif || (kk && L.k !== kk)) return; var C = P.c(L.k), K = S.kol(L.k);
  Object.keys(C).forEach(function (id) { if (!C[id].tunda && !K[id]) delete C[id]; }); L.terkini = true; P.emit(L.k); }); tuntas(); };
// T6k · LINTAS KOLEKSI: stok = Σ batchMasuk (punya saldo pembuka) − Σ penjualan (diarsip, TANPA saldo pembuka). batchMasuk selesai dibaca penuh lebih dulu dari
//       penjualan (limbo terpanjang). Dulu tahan dilepas PER koleksi → stok terpotong DUA KALI (saldo pembuka − penjualan 2026 yang sudah diarsip) tanpa kabar.
//       Kini PENGHALANG BERSAMA: semua koleksi hemat beku (keadaan sebelum ritual) sampai koleksi terakhir selesai, lalu dilepas serentak; putus di tengah → tetap beku
NAMA_K = ['penjualan', 'batchMasuk', 'piutangMutasi', 'pengeluaranHarian'];
var stokKg = function (P) { var m = (P.mem.batchMasuk || []).reduce(function (a, d) { return a + (Number(d.kg) || 0); }, 0); return m - (P.mem.penjualan || []).reduce(function (a, d) { return a + (Number(d.kg) || 0); }, 0); };
function stokLama6k() {
  tokoBaru('2027-01-02T09:00:00Z');
  S.jam -= 30 * HR; S.tulis('batchMasuk', 'b26', { id: 'b26', tanggal: '2026-12-01', merk: 'Contoh', kg: 100 }, true); S.tulis('penjualan', 'j26', { id: 'j26', tanggal: '2026-12-05', merk: 'Contoh', kg: 30, hargaTotal: 1 }, true); S.jam += 30 * HR;
}
function ritual6k() {   // ritual di perangkat lain: saldo pembuka stok (bercap), catatan 2026 diarsip TANPA batu nisan
  S.acara = [{ tahun: 2026, status: 'berjalan', paraf: { pada: '2027-01-02T09:30:00Z' } }];
  S.tulis('batchMasuk', 'pbB', { id: 'pbB', tanggal: '2026-12-31', merk: 'Contoh', kg: 70, tutupBuku: true, tahunDari: 2026 }, true);
  S.acara = [{ tahun: 2026, status: 'terkunci', paraf: { pada: '2027-01-02T09:30:00Z' } }];
  S.hapus('batchMasuk', 'b26', false); S.hapus('penjualan', 'j26', false);
  S.acara = [{ tahun: 2026, status: 'selesai', paraf: { pada: '2027-01-02T09:30:00Z' } }];
}
stokLama6k(); var K6 = new Perangkat('ipad-t6k'); K6.buka(); maju(20000); K6.tutup(); maju(30 * MNT); ritual6k(); maju(JM); klaimHariIni();
fLambat(K6); K6.buka(); maju(3000);
var k6a = { batch: memId(K6, 'batchMasuk'), jual: memId(K6, 'penjualan'), kg: stokKg(K6) };
fTibaK(K6); maju(1000);
fLimboK(K6, 'batchMasuk'); fLimboK(K6, 'piutangMutasi'); fLimboK(K6, 'pengeluaranHarian'); maju(20000);   // penjualan (ribuan nota arsip) belum
var bl6k = K6.sesi.belumLengkap(), US6k = null; K6.sesi.pastikanSegar().then(function (r) { US6k = r; }); tuntas();
var k6b = { batch: memId(K6, 'batchMasuk'), jual: memId(K6, 'penjualan'), kg: stokKg(K6), simpananBatch: Object.keys(K6.c('batchMasuk')).sort(), selesai: !!K6.sesi._K.batchMasuk.fSelesai,
  belum: K6.sesi.keadaan().belum, blBatch: bl6k.batchMasuk || null, S: K6.L.some(function (L) { return L.aktif && L.jenis === 'delta'; }) };
K6.putus(); tuntas(); maju(MNT);
var k6c = { batch: memId(K6, 'batchMasuk'), jual: memId(K6, 'penjualan'), kg: stokKg(K6), siap: semua(K6, function (k) { return K6.siap[k]; }) };
K6.sambung(); tuntas(); maju(20000);
var k6d = { batch: memId(K6, 'batchMasuk'), jual: memId(K6, 'penjualan'), kg: stokKg(K6), periksa: semua(K6, function (k) { return K6.periksa[k] === true; }),
  S: NAMA_K.every(function (k) { return K6.L.some(function (L) { return L.aktif && L.jenis === 'delta' && L.k === k; }); }) };
ok('T6k (sanggahan kedua P5) LINTAS KOLEKSI: batchMasuk (saldo pembuka) selesai dibaca penuh lebih dulu dari penjualan → SEMUA koleksi tetap beku (stok = keadaan sebelum ritual, tidak terpotong dua kali), batchMasuk belum terperiksa ("menunggu jenis catatan lain"), tanpa S, uang-kritis menolak',
  k6a.kg === 70 && J(k6b.batch) === '["b26"]' && J(k6b.jual) === '["j26"]' && k6b.kg === 70 && J(k6b.simpananBatch) === '["pbB"]' && k6b.selesai && k6b.belum.indexOf('batchMasuk') >= 0 && !!k6b.blBatch
  && /jenis catatan lain/.test(k6b.blBatch.sebab) && !k6b.S && US6k && !US6k.ok, J([k6a, k6b, US6k]));
ok('T6k: putus di tengah → tetap beku BERSAMA (pil lepas, stok tetap keadaan sebelum ritual — tidak dilepas sebagian); tersambung → baca penuh penjualan selesai → semua dilepas SERENTAK: memori = server, S terpasang, terperiksa',
  J(k6c.batch) === '["b26"]' && J(k6c.jual) === '["j26"]' && k6c.kg === 70 && k6c.siap && J(k6d.batch) === '["pbB"]' && J(k6d.jual) === '[]' && k6d.kg === 70 && k6d.S && k6d.periksa && samaServer(K6), J([k6c, k6d]));
K6.tutup();
// T6l · aplikasi DITUTUP di tengah penghalang (batchMasuk sudah dibaca penuh sesudah tutup buku, penjualan belum), dibuka lagi: simpanan kini beda ZAMAN (batchMasuk
//       sesudah ritual, penjualan sebelum ritual) — tidak ada keadaan utuh di perangkat → SEMUA koleksi disembunyikan (kosong + kabar & kelengkapan), bukan campuran
//       (dulu: batchMasuk sesudah ritual + penjualan kosong/sebelum ritual)
stokLama6k(); var L6 = new Perangkat('ipad-t6l'); L6.buka(); maju(20000); L6.tutup(); maju(30 * MNT); ritual6k();
S.tulis('penjualan', 'j27', { id: 'j27', tanggal: '2027-01-02', merk: 'Contoh', kg: 5, hargaTotal: 1 }, true); maju(JM); klaimHariIni();
fLambat(L6); L6.buka(); maju(3000); fTibaK(L6, 'batchMasuk'); fLimboK(L6, 'batchMasuk'); fLimboK(L6, 'piutangMutasi'); fLimboK(L6, 'pengeluaranHarian'); maju(20000);
var l6a = { rkBatch: L6.R.k.batchMasuk.bk === hbSidikBk(S.acara), rkJual: L6.R.k.penjualan.bk === hbSidikBk(S.acara), kg: stokKg(L6) };
L6.tutup(); delete L6.dengar; maju(5 * MNT); fLambat(L6); L6.buka(); maju(3000);
var l6b = { batch: memId(L6, 'batchMasuk'), jual: memId(L6, 'penjualan'), simpananBatch: Object.keys(L6.c('batchMasuk')).sort(), simpananJual: Object.keys(L6.c('penjualan')).sort(),
  kabar: L6.sesi.keadaan().kabar, bl: L6.sesi.belumLengkap().batchMasuk || null };
fTibaK(L6); fLimboK(L6); maju(20000);
var l6c = { batch: memId(L6, 'batchMasuk'), jual: memId(L6, 'penjualan'), kg: stokKg(L6) };
ok('T6l (sanggahan kedua P5) ditutup di tengah penghalang lalu dibuka lagi (batchMasuk sudah sesudah ritual, penjualan masih sebelum ritual): SEMUA disembunyikan (kosong), kabar & kelengkapan "disembunyikan" — bukan campuran zaman; baca penuh selesai → server',
  l6a.rkBatch && !l6a.rkJual && l6a.kg === 70 && J(l6b.simpananBatch) === '["pbB"]' && J(l6b.simpananJual) === '["j26"]' && J(l6b.batch) === '[]' && J(l6b.jual) === '[]' && /disembunyikan/i.test(l6b.kabar)
  && !!l6b.bl && /^disembunyikan/.test(l6b.bl.sebab) && J(l6c.batch) === '["pbB"]' && J(l6c.jual) === '["j27"]' && l6c.kg === 65 && samaServer(L6), J([l6a, l6b, l6c]));
L6.tutup(); NAMA_K = KOL.slice();
// T6m · SESI HIDUP (aplikasi terbuka sebelum ritual) yang putus selama ritual di perangkat lain, lalu tersambung. Dulu tahan baru mulai sesudah berita acara terbaca
//       dan memori dibekukan MALAS dari simpanan yang sudah dibawa S (saldo pembuka) + catatan arsip di luar jendela S = DOBEL berjam-jam (kuota habis). Kini putus =
//       server berhenti menjawab → memori dibekukan SAAT ITU (keadaan terakhir yang dijawab server); tersambung → ditahan sampai berita acara dijawab server lagi.
//       Dua urutan (berita acara dulu / simpanan dulu) + kuota habis di tengah baca penuh wajib
function hidupRitual6m(nama, simpananDulu, kuotaHabis) {
  bonLama6(); var P = new Perangkat(nama); P.buka(); maju(20000);
  var awal = { mem: memId(P, 'piutangMutasi'), S: aktif6(P, 'delta') };
  P.putus(); tuntas(); maju(30 * MNT);
  S.acara = [{ tahun: 2026, status: 'berjalan', paraf: { pada: '2027-01-02T09:30:00Z' } }];
  S.tulis('piutangMutasi', 'pb2027', pm6('pb2027', 300003, '2026-12-31', { tutupBuku: true, tahunDari: 2026 }), true);
  S.acara = [{ tahun: 2026, status: 'terkunci', paraf: { pada: '2027-01-02T09:30:00Z' } }]; LAMA6.forEach(function (id) { S.hapus('piutangMutasi', id, false); });
  S.acara = [{ tahun: 2026, status: 'selesai', paraf: { pada: '2027-01-02T09:30:00Z' } }]; maju(JM); klaimHariIni();
  fLambat(P);
  // SDK tersambung lagi: server → simpanan (S membawa saldo pembuka; catatan arsip di luar jendela S tetap di simpanan)
  P.online = true; P.L.forEach(function (L) { if (L.aktif && L.jenis !== 'cache' && P.fTahan.indexOf(L) < 0) P.sinkron(L); });
  if (simpananDulu) { Object.keys(P.cache).forEach(function (k) { P.emit(k); }); tuntas(); }
  P.sesi.online(true); var pra = { mem: memId(P, 'piutangMutasi'), dobel: dobel6(P) };
  P.gema(); P.tetap(); if (!simpananDulu) Object.keys(P.cache).forEach(function (k) { P.emit(k); }); tuntas(); maju(3000);
  var x = { awal: awal, pra: pra, simpanan: Object.keys(P.c('piutangMutasi')).sort(), mem: memId(P, 'piutangMutasi'), dobel: dobel6(P), jml: jml6(P), F: aktif6(P, 'penuh'), S: aktif6(P, 'delta'), periksa: P.periksa.piutangMutasi };
  if (kuotaHabis) { P.diam = true; maju(5 * JM); x.lama = { mem: memId(P, 'piutangMutasi'), dobel: dobel6(P) }; var u = null; P.sesi.pastikanSegar().then(function (r) { u = r; }); tuntas(); x.uang = u; P.diam = false; }
  else { maju(10 * MNT); x.lama = { mem: memId(P, 'piutangMutasi'), dobel: dobel6(P) }; }
  fTiba(P); fLimbo(P); maju(20000); x.akhir = { mem: memId(P, 'piutangMutasi'), sama: samaServer(P) }; P.tutup(); return x;
}
var m6a = hidupRitual6m('ipad-t6m-a', false, false), m6b = hidupRitual6m('ipad-t6m-b', true, false), m6c = hidupRitual6m('ipad-t6m-c', false, true);
ok('T6m (sanggahan kedua P5) sesi hidup putus selama ritual, tersambung — berita acara dijawab LEBIH DULU dari kabar simpanan: memori = keadaan saat putus (catatan 2026, tanpa saldo pembuka — tidak dobel; S yang tetap menempel hanya mengisi simpanan) selama baca penuh wajib, belum terperiksa; selesai → server',
  J(m6a.awal.mem) === J(LAMA6) && m6a.awal.S && m6a.simpanan.indexOf('pb2027') >= 0 && m6a.simpanan.indexOf('a1') >= 0 && J(m6a.mem) === J(LAMA6) && !m6a.dobel && m6a.F && m6a.periksa === false
  && J(m6a.lama.mem) === J(LAMA6) && J(m6a.akhir.mem) === '["pb2027"]' && m6a.akhir.sama, J(m6a));
ok('T6m: urutan sebaliknya (kabar simpanan berisi saldo pembuka tiba SEBELUM berita acara): memori tetap keadaan saat putus, tidak dobel di tiap tahap; selesai → server',
  !m6b.pra.dobel && J(m6b.pra.mem) === J(LAMA6) && !m6b.dobel && J(m6b.mem) === J(LAMA6) && !m6b.lama.dobel && J(m6b.akhir.mem) === '["pb2027"]' && m6b.akhir.sama, J(m6b));
ok('T6m: kuota baca habis di tengah baca penuh wajib → 5 jam kemudian memori masih keadaan saat putus (tidak dobel), uang-kritis menolak', !m6c.dobel && J(m6c.lama.mem) === J(LAMA6) && !m6c.lama.dobel && m6c.uang && !m6c.uang.ok, J(m6c));
// T6n · TIDUR tanpa kabar putus (peramban & SDK tidak sempat memberi kabar): berita acara berganti tiba ketika S masih menempel dan simpanan bisa sudah membawa saldo
//       pembuka → tahan yang mulai DI TENGAH sesi memakai memori KOSONG (disembunyikan, disebut), bukan simpanan; rekam menandai bercampur (muat ulang juga kosong)
bonLama6(); var N6 = new Perangkat('mac-t6n'); N6.buka(); maju(20000); N6.tidur(); maju(30 * MNT);
S.acara = [{ tahun: 2026, status: 'berjalan', paraf: { pada: '2027-01-02T09:30:00Z' } }]; S.tulis('piutangMutasi', 'pb2027', pm6('pb2027', 300003, '2026-12-31', { tutupBuku: true, tahunDari: 2026 }), true);
LAMA6.forEach(function (id) { S.hapus('piutangMutasi', id, false); }); S.acara = [{ tahun: 2026, status: 'selesai', paraf: { pada: '2027-01-02T09:30:00Z' } }]; maju(JM); klaimHariIni();
fLambat(N6); N6.gema(); N6.bangun(); maju(3000);
var n6a = { simpanan: Object.keys(N6.c('piutangMutasi')).sort(), mem: memId(N6, 'piutangMutasi'), dobel: dobel6(N6), kabar: N6.sesi.keadaan().kabar, bl: N6.sesi.belumLengkap().piutangMutasi || null,
  campur: !!N6.R.k.piutangMutasi.bkCampur };
maju(10 * MNT); var n6b = { mem: memId(N6, 'piutangMutasi'), dobel: dobel6(N6) };
fTiba(N6); fLimbo(N6); maju(20000);
var n6c = { mem: memId(N6, 'piutangMutasi'), sama: samaServer(N6), campur: !!N6.R.k.piutangMutasi.bkCampur, kabar: N6.sesi.keadaan().kabar };
ok('T6n (sanggahan kedua P5) TIDUR tanpa kabar putus, bangun: berita acara berganti selagi S menempel → memori DISEMBUNYIKAN (kosong + tulisan sendiri), kabar & kelengkapan "disembunyikan", rekam bercampur — bukan catatan 2026 + saldo pembuka; selesai → server, kabar dibuang',
  n6a.simpanan.indexOf('pb2027') >= 0 && n6a.simpanan.indexOf('a1') >= 0 && J(n6a.mem) === '[]' && !n6a.dobel && /disembunyikan/i.test(n6a.kabar) && !!n6a.bl && /^disembunyikan/.test(n6a.bl.sebab) && n6a.campur
  && J(n6b.mem) === '[]' && J(n6c.mem) === '["pb2027"]' && n6c.sama && !n6c.campur && !/disembunyikan/i.test(n6c.kabar), J([n6a, n6b, n6c]));
N6.tutup();
// T6o · baca penuh wajib macet SEBELUM membawa apa pun (kuota habis), owner memuat ulang saat server diam: simpanan masih bersih (sebelum ritual) → TIDAK ditandai
//       bercampur (dulu ditandai saat F dipasang → memori KOSONG dengan kabar "angka dari simpanan perangkat ini") → memori = simpanan, kabar server diam jujur
var Y6 = ritual6(); fLambat(Y6); Y6.buka(); maju(3000); var o6a = { campur: !!Y6.R.k.piutangMutasi.bkCampur, F: aktif6(Y6, 'penuh') };
Y6.diam = true; maju(MNT); Y6.tutup(); delete Y6.dengar; maju(MNT); Y6.buka({ tetap: false }); tuntas();
Y6.sesi.setelTetap({ perangkat: [], acara: salin(S.acara), klaim: salin(S.klaim), acaraServer: false }); tuntas(); maju(31000);
var o6b = { campurAwal: !!Y6.sesi._K.piutangMutasi.campurAwal, mem: memId(Y6, 'piutangMutasi'), simpanan: Object.keys(Y6.c('piutangMutasi')).sort(), siap: semua(Y6, function (k) { return Y6.siap[k]; }),
  kabar: Y6.sesi.keadaan().kabar, bl: Y6.sesi.belumLengkap().piutangMutasi || null };
Y6.jawab(); Y6.gema(); maju(20000); var o6c = { mem: memId(Y6, 'piutangMutasi'), sama: samaServer(Y6) };
ok('T6o (sanggahan kedua P5) baca penuh wajib macet sebelum membawa apa pun, dimuat ulang saat server diam: simpanan TIDAK ditandai bercampur → memori = simpanan (catatan 2026, tanpa saldo pembuka), kabar & kelengkapan "server belum menjawab" (jujur: memang dari simpanan); server menjawab → baca penuh → server',
  !o6a.campur && o6a.F && !o6b.campurAwal && J(o6b.mem) === J(LAMA6) && J(o6b.simpanan) === J(LAMA6) && o6b.siap && /^Server belum menjawab/.test(o6b.kabar) && !!o6b.bl && o6b.bl.sebab === HB_SEBAB_SERVER_DIAM
  && J(o6c.mem) === '["pb2027"]' && o6c.sama, J([o6a, o6b, o6c]));
Y6.tutup();
// T6p · simpanan BERCAMPUR (baca penuh wajib sesi lalu terputus SESUDAH membawa saldo pembuka), dibuka lagi, baca penuh wajib ditolak kuota habis: memori kosong →
//       kabar & kelengkapan "disembunyikan … kuota baca hari ini habis" (didahulukan), bukan "angka dari simpanan perangkat" (dulu)
var Q6p = ritual6(); fLambat(Q6p); Q6p.buka(); maju(3000); fTiba(Q6p); maju(1000); var p6a = { campur: !!Q6p.R.k.piutangMutasi.bkCampur };
Q6p.tutup(); delete Q6p.dengar; maju(10 * MNT); Q6p.fGalat = 'resource-exhausted'; Q6p.buka(); maju(3000);
var p6b = { mem: memId(Q6p, 'piutangMutasi'), siap: !!Q6p.siap.piutangMutasi, kabar: Q6p.sesi.keadaan().kabar, bl: Q6p.sesi.belumLengkap().piutangMutasi || null };
ok('T6p (sanggahan kedua P5) simpanan bercampur + baca penuh wajib ditolak kuota habis: memori kosong (tidak dobel), kabar & kelengkapan "disembunyikan … kuota baca hari ini habis", tidak mengaku "angka dari simpanan perangkat"',
  p6a.campur && J(p6b.mem) === '[]' && p6b.siap && /disembunyikan/i.test(p6b.kabar) && /kuota baca hari ini habis/.test(p6b.kabar) && !/angka dari simpanan perangkat/.test(p6b.kabar)
  && !!p6b.bl && /^disembunyikan/.test(p6b.bl.sebab) && /kuota baca hari ini habis/.test(p6b.bl.sebab), J([p6a, p6b]));
Q6p.fGalat = null; Q6p.tutup();
// T6q · perangkat LAIN yang ikut dengar penuh selama ritual, ditutup di tengah ritual, ritual selesai di perangkat pemegang; dibuka lagi saat server DIAM / TANPA
//       internet: berita acara di simpanan masih "terkunci" (pemegang = perangkat lain). Dulu pengecualian "berita acara menyebut tutup buku berjalan → memori =
//       simpanan" berlaku untuk SEMUA perangkat → catatan 2026 + saldo pembuka DOBEL berjam-jam. Kini hanya PEMEGANG ritual (atau berita acara dari server): perangkat
//       lain memori kosong (disembunyikan) sampai baca penuh wajib selesai
function lainTutup6q(nama) {
  bonLama6(); var P = new Perangkat(nama); P.buka(); maju(20000);
  S.acara = [{ tahun: 2026, status: 'terkunci', paraf: { pada: '2027-01-02T09:30:00Z' }, pemegang: { id: 'mac-pemegang', nama: 'Mac contoh' } }]; P.tetap(); maju(20000);
  S.tulis('piutangMutasi', 'pb2027', pm6('pb2027', 300003, '2026-12-31', { tutupBuku: true, tahunDari: 2026 }), true); S.hapus('piutangMutasi', 'a1', false); tuntas();
  var acara = salin(S.acara); P.tutup(); ['a2', 'a3', 'r1'].forEach(function (id) { S.hapus('piutangMutasi', id, false); });
  S.acara = [{ tahun: 2026, status: 'selesai', paraf: { pada: '2027-01-02T09:30:00Z' } }]; maju(JM); klaimHariIni(); return { P: P, acara: acara };
}
var q6 = lainTutup6q('ipad-t6q'); q6.P.diam = true; q6.P.buka({ tetap: false }); tuntas(); q6.P.sesi.setelTetap({ perangkat: [], acara: q6.acara, klaim: salin(S.klaim), acaraServer: false }); tuntas(); maju(31000);
var q6a = { mem: memId(q6.P, 'piutangMutasi'), simpanan: Object.keys(q6.P.c('piutangMutasi')).sort(), dobel: dobel6(q6.P), siap: semua(q6.P, function (k) { return q6.P.siap[k]; }), kabar: q6.P.sesi.keadaan().kabar };
maju(3 * JM); var q6b = { mem: memId(q6.P, 'piutangMutasi'), dobel: dobel6(q6.P) };
q6.P.jawab(); q6.P.gema(); maju(20000); var q6c = { mem: memId(q6.P, 'piutangMutasi'), sama: samaServer(q6.P) }; q6.P.tutup();
var q6o = lainTutup6q('ipad-t6q-offline'); q6o.P.online = false; q6o.P.buka({ tetap: false }); tuntas(); q6o.P.sesi.setelTetap({ perangkat: [], acara: q6o.acara, klaim: salin(S.klaim), acaraServer: false }); tuntas();
var q6d = { mem: memId(q6o.P, 'piutangMutasi'), dobel: dobel6(q6o.P), siap: !!q6o.P.siap.piutangMutasi, kabar: q6o.P.sesi.keadaan().kabar }; q6o.P.tutup();
ok('T6q (sanggahan kedua P5) perangkat LAIN ditutup di tengah ritual, dibuka saat server diam / tanpa internet dengan berita acara simpanan "terkunci" (pemegang perangkat lain): memori KOSONG (disembunyikan, tidak dobel), juga 3 jam kemudian; server menjawab → baca penuh → server',
  q6a.simpanan.indexOf('pb2027') >= 0 && q6a.simpanan.indexOf('a2') >= 0 && J(q6a.mem) === '[]' && !q6a.dobel && q6a.siap && /disembunyikan/i.test(q6a.kabar) && J(q6b.mem) === '[]' && !q6b.dobel
  && J(q6c.mem) === '["pb2027"]' && q6c.sama && J(q6d.mem) === '[]' && !q6d.dobel && q6d.siap && /disembunyikan/i.test(q6d.kabar), J([q6a, q6b, q6c, q6d]));
// T6r · server DIAM + simpanan perangkat TIDAK dipercaya (simpanan peramban hilang, rekam n ≥ 1): tetap memuat (bukan siap dengan memori kosong), kelengkapan & kabar
//       menyebut sebab sebenarnya, tidak mengaku "angka dari simpanan perangkat ini" (mutasi M14 — siap walau tidak dipercaya — dulu lolos semua uji)
bonLama6(); var R6 = new Perangkat('mac-t6r'); R6.buka(); maju(20000); R6.tutup(); maju(JM); R6.cache = {};
R6.diam = true; R6.buka({ tetap: false }); tuntas(); R6.sesi.setelTetap({ perangkat: [], acara: [], klaim: salin(S.klaim), acaraServer: false }); tuntas(); maju(31000);
var r6a = { dipercaya: R6.sesi._K.piutangMutasi.dipercaya, siap: !!R6.siap.piutangMutasi, mem: memId(R6, 'piutangMutasi'), bl: R6.sesi.belumLengkap().piutangMutasi || null, kabar: R6.sesi.keadaan().kabar };
R6.jawab(); R6.gema(); maju(20000); var r6b = { siap: !!R6.siap.piutangMutasi, sama: samaServer(R6) }; R6.tutup();
ok('T6r (sanggahan kedua P5) server diam + simpanan tidak dipercaya (kosong padahal rekam ≥ 1): sesudah 31 detik TETAP memuat, kelengkapan menyebut "simpanan perangkat kosong" + server belum menjawab, kabar & kelengkapan tidak mengaku "angka dari simpanan perangkat ini"; server menjawab → baca penuh → siap',
  r6a.dipercaya === false && !r6a.siap && J(r6a.mem) === '[]' && !!r6a.bl && /simpanan perangkat kosong/.test(r6a.bl.sebab) && /server belum menjawab/.test(r6a.bl.sebab) && !/angka dari simpanan perangkat ini/.test(r6a.bl.sebab + r6a.kabar)
  && r6b.siap && r6b.sama, J([r6a, r6b]));
// T6s · dibuka TANPA internet lebih dari 30 detik lalu tersambung: "server belum menjawab sejak aplikasi dibuka" tidak muncul sebelum 30 detik SESUDAH tersambung (dulu
//       tanda server diam terpasang selagi tanpa internet dan tidak pernah dibersihkan saat tersambung — sebab yang menyesatkan)
bonLama6(); var T6s = new Perangkat('mac-t6s'); T6s.buka(); maju(20000); T6s.tutup(); maju(JM);
T6s.online = false; T6s.buka({ tetap: false }); tuntas(); maju(31000);
T6s.online = true; T6s.sesi.online(true); tuntas(); maju(1000);   // tersambung; berita acara belum dijawab server (baru tersambung)
var s6a = { bl: T6s.sesi.belumLengkap().piutangMutasi || null, kabar: T6s.sesi.keadaan().kabar }; var US6s = null; T6s.sesi.pastikanSegar().then(function (r) { US6s = r; }); tuntas();
maju(31000); var s6b = { bl: T6s.sesi.belumLengkap().piutangMutasi || null };
T6s.gema(); T6s.tetap(); maju(20000); var s6c = J(T6s.sesi.belumLengkap()); T6s.tutup();
ok('T6s (sanggahan kedua P5) dibuka tanpa internet > 30 detik, lalu tersambung: sebelum 30 detik sesudah tersambung TIDAK menyebut "server belum menjawab" (kelengkapan, kabar, uang-kritis); 30 detik sesudah tersambung tanpa jawaban → baru menyebutnya; server menjawab → lengkap',
  !!s6a.bl && s6a.bl.sebab !== HB_SEBAB_SERVER_DIAM && !/server belum menjawab/i.test(s6a.bl.sebab + s6a.kabar) && US6s && !US6s.ok && !/server belum menjawab/.test(US6s.pesan) && !!s6b.bl && s6b.bl.sebab === HB_SEBAB_SERVER_DIAM
  && s6c === '{}', J([s6a, US6s, s6b, s6c]));
// T6t · Mac PEMEGANG ritual ditutup di tengah ritual, ritual DIAMBIL ALIH perangkat lain dan selesai di sana; Mac dibuka lagi saat server diam: berita acara simpanan
//       "terkunci" (pemegang = Mac ini) → memori = simpanannya; server menjawab "selesai" → memori beku ditentukan ULANG selagi masih ditahan: disembunyikan (kosong)
//       sampai baca penuh selesai — bukan simpanan setengah ritual (catatan 2026 sisa + saldo pembuka)
bonLama6(); var T6t = new Perangkat('mac-t6t'); T6t.buka(); maju(20000); var pgT = { id: 'mac-t6t', nama: 'Mac contoh' };
S.acara = [{ tahun: 2026, status: 'terkunci', paraf: { pada: '2027-01-02T09:30:00Z' }, pemegang: pgT }]; T6t.tetap(); maju(20000);
T6t.tulis('piutangMutasi', 'pb2027', pm6('pb2027', 300003, '2026-12-31', { tutupBuku: true, tahunDari: 2026 })); tuntas();
delete T6t.c('piutangMutasi').a1; S.hapus('piutangMutasi', 'a1', false); T6t.emit('piutangMutasi'); tuntas();
var acaraT = salin(S.acara); T6t.tutup(); ['a2', 'a3', 'r1'].forEach(function (id) { S.hapus('piutangMutasi', id, false); });
S.acara = [{ tahun: 2026, status: 'selesai', paraf: { pada: '2027-01-02T09:30:00Z' }, pemegang: { id: 'ipad-lain', nama: 'iPad contoh' }, pemegangLama: pgT }]; maju(JM); klaimHariIni();
T6t.diam = true; T6t.buka({ tetap: false }); tuntas(); T6t.sesi.setelTetap({ perangkat: [], acara: acaraT, klaim: salin(S.klaim), acaraServer: false }); tuntas(); maju(31000);
var t6a = { mem: memId(T6t, 'piutangMutasi'), siap: !!T6t.siap.piutangMutasi };
T6t.hitungTahan = []; T6t.jawab(); T6t.gema(); maju(3000);
var t6b = { mem: memId(T6t, 'piutangMutasi'), dobel: dobel6(T6t), simpanan: Object.keys(T6t.c('piutangMutasi')).sort(), kabar: T6t.sesi.keadaan().kabar };
T6t.hitungTahan.forEach(function (f) { f(); }); T6t.hitungTahan = null; maju(20000);
var t6c = { mem: memId(T6t, 'piutangMutasi'), sama: samaServer(T6t) }; T6t.tutup();
ok('T6t (sanggahan kedua P5) Mac pemegang dibuka lagi sesudah ritualnya diambil alih & selesai di perangkat lain: berita acara simpanan "terkunci" (pemegang = Mac ini) → memori = simpanannya; server menjawab "selesai" → memori beku ditentukan ULANG: disembunyikan (kosong, tidak dobel) selama baca penuh; selesai → server',
  J(t6a.mem) === '["a2","a3","pb2027","r1"]' && t6a.siap && J(t6b.mem) === '[]' && !t6b.dobel && J(t6b.simpanan) === '["pb2027"]' && /^Angka disembunyikan/.test(t6b.kabar) && J(t6c.mem) === '["pb2027"]' && t6c.sama, J([t6a, t6b, t6c]));
// T6u · tertutup selama ritual, SEMUA koleksi dengar penuh (tab /baru/ versi lama baru saja menulis): dengar penuh terkini di semua koleksi = semua simpanan = server →
//       dilepas serentak SEBELUM hitungan server menjawab (gerbang uang-kritis menganggap dengar penuh terkini segar — memori tidak boleh tertinggal beku)
var U6 = ritual6(); S.perangkat = [{ id: 'tab-lama', nama: 'Laptop contoh', aplikasi: 'baru', versi: 'baru', pada: new Date(S.jam - MNT).toISOString(), akun: 'owner@x' }];
fLambat(U6); U6.hitungTahan = []; U6.buka(); maju(3000);
var u6a = { mode: NAMA_K.map(function (k) { return keadaanK(U6, k).mode; }), mem: memId(U6, 'piutangMutasi'), siap: !!U6.siap.piutangMutasi, dobel: dobel6(U6) };
fTiba(U6); var u6t = { mem: memId(U6, 'piutangMutasi'), dobel: dobel6(U6) }; fLimbo(U6); tuntas();
var u6b = { mem: memId(U6, 'piutangMutasi'), siap: semua(U6, function (k) { return U6.siap[k]; }), S: aktif6(U6, 'delta'), tunggu: U6.hitungTahan.length };
U6.hitungTahan.forEach(function (f) { f(); }); U6.hitungTahan = null; maju(20000); var u6c = { mem: memId(U6, 'piutangMutasi'), sama: samaServer(U6) }; U6.tutup(); S.perangkat = [];
ok('T6u (sanggahan kedua P5) tertutup selama ritual, SEMUA koleksi dengar penuh karena tab /baru/ lama: ditahan bersama (memori sebelum ritual, tidak dobel selama limbo); dengar penuh terkini di semua koleksi → dilepas serentak SEBELUM hitungan server menjawab (memori = server, siap, S terpasang)',
  u6a.mode.every(function (m) { return m === 'penuh'; }) && J(u6a.mem) === J(LAMA6) && !u6a.siap && !u6a.dobel && !u6t.dobel && J(u6b.mem) === '["pb2027"]' && u6b.siap && u6b.S && u6b.tunggu > 0
  && J(u6c.mem) === '["pb2027"]' && u6c.sama, J([u6a, u6t, u6b, u6c]));
// T6v · tersambung lagi sesudah putus, berita acara BELUM dijawab server lagi, padahal S & hitungan koleksi sudah cocok: memori masih beku → kelengkapan "belum
//       dicocokkan dengan server (baru dibuka atau baru tersambung)", uang-kritis tetap MENOLAK (dulu: dengar ubahan & hitungan cocok = segar); server menjawab → boleh
bonLama6(); var V6 = new Perangkat('mac-t6v'); V6.buka(); maju(20000); V6.putus(); tuntas(); maju(5 * MNT);
V6.online = true; V6.L.forEach(function (L) { if (L.aktif && L.jenis !== 'cache') V6.sinkron(L); }); Object.keys(V6.cache).forEach(function (k) { V6.emit(k); }); V6.sesi.online(true); tuntas(); maju(3000);
var US6v = null; V6.sesi.pastikanSegar().then(function (r) { US6v = r; }); tuntas();
var v6a = { sTerkini: !!V6.sesi._K.piutangMutasi.sTerkini, cocok: V6.sesi._K.piutangMutasi.cocokPada > 0, bl: V6.sesi.belumLengkap().piutangMutasi || null, periksa: V6.periksa.piutangMutasi, uang: US6v };
V6.tetap(); maju(20000); var US6v2 = null; V6.sesi.pastikanSegar().then(function (r) { US6v2 = r; }); tuntas(); V6.tutup();
ok('T6v (sanggahan kedua P5) tersambung lagi, berita acara belum dijawab server lagi (S & hitungan sudah cocok): belum terperiksa, kelengkapan "baru tersambung", uang-kritis MENOLAK; server menjawab → uang-kritis boleh',
  v6a.sTerkini && v6a.cocok && v6a.periksa === false && !!v6a.bl && v6a.bl.sebab === HB_SEBAB_TUNGGU_ACARA && v6a.uang && !v6a.uang.ok && US6v2 && US6v2.ok === true, J([v6a, US6v2]));

// ---- T7 · umur denyut tab /baru/ lama dinilai dengan jam SERVER saat perubahannya terlihat (jam tab terlambat 20 menit)
tokoBaru('2026-11-10T03:00:00Z'); S.tulis('penjualan', 'p1', notaN('p1', 1000), true);
var A7 = new Perangkat('mac-t7'); A7.buka();
var tabT7 = function (lalu) { return { id: 'tab-lama', nama: 'Laptop contoh', aplikasi: 'baru', versi: 'baru', pada: new Date(S.jam - lalu).toISOString(), akun: 'owner@x' }; };
S.perangkat = [tabT7(3 * JM)]; A7.tetap(); tuntas(); var m7 = keadaanK(A7, 'penjualan').mode;
maju(5 * MNT); S.perangkat = [tabT7(20 * MNT)]; A7.tetap(); tuntas();
ok('T7: tab lama terakhir terlihat 3 jam lalu → biasa (delta); tab itu MENULIS LAGI sekarang dengan jam terlambat 20 menit → SEMUA koleksi dengar penuh (dulu dianggap "sudah lama")',
  m7 === 'delta' && NAMA_K.every(function (k) { return keadaanK(A7, k).mode === 'penuh'; }), J([m7, NAMA_K.map(function (k) { return keadaanK(A7, k).mode; })]));
A7.tutup();

// ===================== K · KELENGKAPAN — SATU sumber hbBelumLengkap (#111 × Paket C, 7 Okt) =====================
var KH = hbHariKuota(Z('2026-11-10T03:00:00Z')); var kemarinK = Z('2026-11-08T03:00:00Z'); var SH = hbSebabHarian(KH);
var BLd = { vAda: true, nTerkini: true, online: true, mode: 'delta', sTerkini: true, cocok: true, fSelesai: false, totalPada: Z('2026-11-10T02:00:00Z'), hari: KH, klaim: null };
var bl = function (p) { return hbBelumLengkap(Object.assign({}, BLd, p || {})); };
// kerusakan bisa membuat hasilnya null — dibaca lewat jn / sb supaya ujinya BERBUNYI di baris yang benar, bukan jsc jatuh
var jn = function (b) { return b ? b.jenis : null; }, sb = function (b) { return b ? String(b.sebab) : ''; };
ok('K murni: terperiksa & dibaca penuh perangkat ini pada hari kuota ini → lengkap (null)', bl() === null, J(bl()));
ok('K murni: terperiksa (hitungan cocok) tapi baca penuh terakhir hari kuota LALU & baca penuh harian toko belum ada → "harian": "belum dibaca penuh sejak kuota baca direset pukul 15.00 WIB — ketuk "baca penuh sekarang" (Menu › Toko ini › Perangkat & antrean › Hemat baca)"',
  (function () { var b = bl({ totalPada: kemarinK }); return !!b && b.jenis === 'harian' && b.sebab === SH && b.sebab === 'belum dibaca penuh sejak kuota baca direset pukul 15.00 WIB — ketuk "baca penuh sekarang" (Menu › Toko ini › Perangkat & antrean › Hemat baca)'; })(), J(bl({ totalPada: kemarinK })));
// sanggahan 7 Okt (d): "hari ini" = hari KUOTA — owner membaca penuh 10.00 WIB, 14.30 WIB hari yang sama kalimatnya menyebut jam reset, bukan "hari ini"
var X3 = hbBelumLengkap(Object.assign({}, BLd, { totalPada: Z('2026-10-08T03:00:00Z'), hari: hbHariKuota(Z('2026-10-08T07:30:00Z')) }));
ok('K murni (sanggahan 7 Okt): baca penuh 10.00 WIB, dilihat 14.30 WIB HARI YANG SAMA (kuota sudah direset 14.00) → "harian" yang MENYEBUT jam resetnya ("sejak kuota baca direset pukul 14.00 WIB"), tidak bilang "hari ini"',
  jn(X3) === 'harian' && sb(X3) === 'belum dibaca penuh sejak kuota baca direset pukul 14.00 WIB — ' + 'ketuk "baca penuh sekarang" (Menu › Toko ini › Perangkat & antrean › Hemat baca)' && !/hari ini/.test(sb(X3)), J(X3));
ok('K murni: jam reset per hari kuota — Okt 14.00, 1 Nov 14.00 (jam musim panas AS berakhir siang itu), 2 Nov 15.00, 14 Mar 2027 15.00, 15 Mar 2027 14.00; tanggal rusak = ""',
  hbJamResetHariWib('2026-10-08') === '14.00' && hbJamResetHariWib('2026-11-01') === '14.00' && hbJamResetHariWib('2026-11-02') === '15.00' && hbJamResetHariWib('2027-03-14') === '15.00'
  && hbJamResetHariWib('2027-03-15') === '14.00' && hbJamResetHariWib('') === '' && hbJamResetHariWib('x') === '',
  J(['2026-10-08', '2026-11-01', '2026-11-02', '2027-03-14', '2027-03-15', ''].map(hbJamResetHariWib)));
// sanggahan 7 Okt (d): baca penuh ditolak 429 (kuota habis) — mengetuk tidak menolong sampai reset berikutnya; kalimatnya menyebut jamnya
var X6 = bl({ fSelesai: false, fGalat: 'resource-exhausted', totalPada: kemarinK }), X6p = bl({ wajibTotal: 'baca penuh gagal (resource-exhausted) — dicoba lagi sebentar' }), X6g = bl({ wajibTotal: 'baca penuh gagal (unavailable) — dicoba lagi sebentar' });
ok('K murni (sanggahan 7 Okt): baca penuh gagal karena KUOTA BACA HABIS (429) → "kuota baca hari ini habis — ketuk baca penuh sekarang sesudah pukul 15.00 WIB" ("harian" bila hitungan cocok, "periksa" bila wajib); galat lain tetap "dicoba lagi sebentar"',
  jn(X6) === 'harian' && sb(X6) === hbSebabHabis(KH) && /^belum bisa dibaca penuh karena kuota baca hari ini habis — ketuk "baca penuh sekarang" sesudah pukul 15\.00 WIB/.test(sb(X6))
  && jn(X6p) === 'periksa' && sb(X6p) === hbSebabHabis(KH) && /^gagal dibaca penuh — dicoba lagi sebentar/.test(sb(X6g)) && /sesudah pukul 14\.00 WIB/.test(hbSebabHabis('2026-10-30')) && /sesudah pukul 15\.00 WIB/.test(hbSebabHabis('2026-11-01')),
  J([X6, X6p, X6g]));
// sanggahan 7 Okt (a): baca penuh harian toko "selesai" dengan temuan yang tidak bisa sampai ke perangkat lain (gagal permanen / bulan terkunci) = bukan bukti lengkap
var KT = { hari: KH, selesai: 1, temuanTunda: { penjualan: 2 } };
ok('K murni (sanggahan 7 Okt): baca penuh harian toko selesai TAPI temuanTunda untuk jenis catatan ini → "harian" (ubahan toko belum sampai ke perangkat ini — ketuk baca penuh sekarang); jenis lain lengkap; dibaca penuh sendiri hari ini = lengkap',
  jn(bl({ koleksi: 'penjualan', totalPada: kemarinK, klaim: KT })) === 'harian' && sb(bl({ koleksi: 'penjualan', totalPada: kemarinK, klaim: KT })) === HB_SEBAB_TOKO_TUNDA
  && bl({ koleksi: 'retur', totalPada: kemarinK, klaim: KT }) === null && bl({ koleksi: 'penjualan', klaim: KT }) === null && bl({ koleksi: 'penjualan', totalPada: kemarinK, klaim: { hari: KH, selesai: 1, temuanTunda: null } }) === null,
  J([bl({ koleksi: 'penjualan', totalPada: kemarinK, klaim: KT }), bl({ koleksi: 'retur', totalPada: kemarinK, klaim: KT })]));
ok('K murni: baca penuh harian TOKO selesai hari kuota ini (perangkat lain) → lengkap; klaim hari ini BELUM selesai / klaim kemarin → "harian"',
  bl({ totalPada: kemarinK, klaim: { hari: KH, selesai: 1 } }) === null && jn(bl({ totalPada: kemarinK, klaim: { hari: KH, selesai: null, perangkat: 'lain' } })) === 'harian'
  && jn(bl({ totalPada: kemarinK, klaim: { hari: '2026-11-08', selesai: 1 } })) === 'harian');
ok('K murni: dengar penuh terkini → lengkap walau tanpa baca penuh hari ini; belum terkini → "periksa" sedang dibaca penuh; galat → "gagal dibaca penuh"',
  bl({ mode: 'penuh', fTerkini: true, fMode: 'penuh', totalPada: kemarinK }) === null && jn(bl({ mode: 'penuh', fTerkini: false, fMode: 'penuh' })) === 'periksa'
  && /^sedang dibaca penuh/.test(sb(bl({ mode: 'penuh', fTerkini: false }))) && /^gagal dibaca penuh/.test(sb(bl({ mode: 'penuh', fTerkini: false, fGalat: 'unavailable' }))));
ok('K murni: jam server belum diterima (hari kuota tidak diketahui) → "harian" belum bisa dipastikan', jn(bl({ hari: '' })) === 'harian' && /jam server belum diterima/.test(sb(bl({ hari: '' }))));
var pkK = [[{ vMati: true }, /muat ulang aplikasi/], [{ berhenti: true }, /muat ulang aplikasi/], [{ vAda: false }, /simpanan perangkat/], [{ nTerkini: false }, /catatan yang dihapus/],
  [{ wajibTotal: 'perkiraan baca hari ini melewati 80% kuota — menunggu kuota besok (baca penuh harian toko)' }, /ditunda supaya kuota baca hari ini tidak habis/],
  [{ wajibTotal: 'baca penuh gagal (unavailable) — dicoba lagi sebentar' }, /^gagal dibaca penuh/], [{ sTerkini: false }, /ubahan terbaru/], [{ fJalan: true }, /sedang dibaca penuh/], [{ cocok: false }, /belum dicocokkan dengan server/]];
ok('K murni: tiap keadaan BELUM TERPERIKSA = jenis "periksa" dengan sebab kalimat toko (tanpa nama koleksi / bahasa mesin)',
  pkK.every(function (x) { var b = bl(x[0]); return !!b && b.jenis === 'periksa' && x[1].test(b.sebab) && !/koleksi|cache|snapshot|delta|nisan|capServer|server F/.test(b.sebab); }), J(pkK.map(function (x) { return bl(x[0]); })));
ok('K murni: tanpa internet → sebab "perangkat ini tanpa internet" (tab yang berhenti / kalah kunci tab tetap "muat ulang")', /tanpa internet/.test(sb(bl({ online: false, sTerkini: false }))) && /muat ulang/.test(sb(bl({ online: false, vMati: true }))) && sb(bl({ online: false, berhenti: true })) === HB_SEBAB_TAB_BERHENTI);
// arti "terperiksa" sejak 7 Okt (rumus lama ditulis ulang: lamaT di bagian B, + tab yang berhenti 7 Okt) = bukan jenis "periksa" — di SEMUA kombinasi keadaan
var nBandingK = 0, bedaK = [];
[false, true].forEach(function (berhenti) { [false, true].forEach(function (vMati) { [false, true].forEach(function (vAda) { [false, true].forEach(function (nT) { ['delta', 'total', 'penuh', null].forEach(function (mode) { [false, true].forEach(function (fT) { [false, true].forEach(function (fS) {
  ['penuh', 'total'].forEach(function (fM) { ['', 'x'].forEach(function (wt) { [false, true].forEach(function (sT) { [false, true].forEach(function (fJ) { [false, true].forEach(function (cc) { [true, false].forEach(function (on) {
    var x = { berhenti: berhenti, vMati: vMati, vAda: vAda, nTerkini: nT, online: on, mode: mode, fTerkini: fT, fSelesai: fS, fMode: fM, wajibTotal: wt, sTerkini: sT, fJalan: fJ, cocok: cc, totalPada: kemarinK, hari: KH };
    var b = hbBelumLengkap(x); nBandingK++; if ((!b || b.jenis !== 'periksa') !== lamaT(x)) bedaK.push(x); }); }); }); }); }); }); }); }); }); }); }); }); });
ok('K: "terperiksa" = bukan jenis "periksa" — SAMA dengan rumus terperiksa sejak 7 Okt (+ tab yang berhenti, 7 Okt) di ' + nBandingK + ' kombinasi (gerbang katalog, uang-kritis & pil kepala tidak bergeser)', !bedaK.length && nBandingK === 16384, J(bedaK.slice(0, 2)));
var PBk = { penjualan: { jenis: 'harian', sebab: SH }, retur: { jenis: 'periksa', sebab: 'sedang dibaca penuh — tunggu sampai selesai' } };
ok('K hbBelumUntuk: hanya koleksi yang diminta; "periksa" lebih berat dari "harian"; tanpa / "*" = semua; kosong / koleksi lain lengkap → null',
  J(hbBelumUntuk(PBk, ['penjualan', 'modalOwner'])) === J({ koleksi: ['penjualan'], jenis: 'harian', sebab: SH, utama: ['penjualan'], lain: [], sebabLain: '' }) && (hbBelumUntuk(PBk, null) || {}).jenis === 'periksa' && ((hbBelumUntuk(PBk, ['*']) || {}).koleksi || []).length === 2
  && /sedang dibaca penuh/.test((hbBelumUntuk(PBk, null) || {}).sebab) && hbBelumUntuk({}, null) === null && hbBelumUntuk(PBk, ['modalOwner']) === null, J([hbBelumUntuk(PBk, ['penjualan']), hbBelumUntuk(PBk, null)]));
// sanggahan 7 Okt (d): sebab SATU jenis catatan ("sedang dibaca penuh — tunggu") dulu dipinjamkan ke SEMUA — owner menunggu, padahal dua lainnya butuh ketukan
var PX4 = { penjualan: { jenis: 'periksa', sebab: 'sedang dibaca penuh — tunggu sampai selesai' }, retur: { jenis: 'harian', sebab: SH }, modalOwner: { jenis: 'harian', sebab: SH } };
var X4 = hbBelumUntuk(PX4, null) || {};
ok('K hbBelumUntuk (sanggahan 7 Okt): sebab tidak dipinjamkan — penjualan "sedang dibaca penuh" = utama; retur & modal owner (belum dibaca penuh sejak reset) = lain dengan sebabnya sendiri',
  J(X4.koleksi) === '["penjualan","retur","modalOwner"]' && J(X4.utama) === '["penjualan"]' && J(X4.lain) === '["retur","modalOwner"]' && X4.sebab === 'sedang dibaca penuh — tunggu sampai selesai' && X4.sebabLain === SH && X4.jenis === 'periksa', J(X4));
var KX4 = hbKalimatBelum(PX4, null), K3H = hbKalimatBelum({ penjualan: { jenis: 'harian', sebab: SH }, retur: { jenis: 'harian', sebab: SH }, modalOwner: { jenis: 'harian', sebab: SH } }, null);
var KCampur = hbKalimatBelum({ a: { jenis: 'periksa', sebab: 'sedang dibaca penuh — tunggu sampai selesai' }, b: { jenis: 'harian', sebab: SH }, c: { jenis: 'periksa', sebab: 'belum dicocokkan dengan ubahan terbaru di server — tunggu sebentar' } }, null);
ok('K hbKalimatBelum: "data perangkat ini <keadaan> (n jenis catatan) — <petunjuk>; m jenis catatan lainnya <sebabnya>" — tanpa kurung ganda, tanpa "bagian data"; satu jenis = tanpa hitungan; lengkap / saklar mati = ""',
  KX4 === 'data perangkat ini sedang dibaca penuh (1 jenis catatan) — tunggu sampai selesai; 2 jenis catatan lainnya ' + SH
  && K3H === 'data perangkat ini belum dibaca penuh sejak kuota baca direset pukul 15.00 WIB (3 jenis catatan) — ketuk "baca penuh sekarang" (Menu › Toko ini › Perangkat & antrean › Hemat baca)'
  && KCampur === 'data perangkat ini sedang dibaca penuh (1 jenis catatan) — tunggu sampai selesai; 2 jenis catatan lainnya juga belum lengkap — lihat Menu › Toko ini › Perangkat & antrean › Hemat baca'
  && hbKalimatBelum(PBk, ['penjualan']) === 'data perangkat ini ' + SH && hbKalimatBelum({}, null) === '' && hbKalimatBelum(null, null) === '' && ![KX4, K3H, KCampur].some(function (s) { return /\) \(|bagian data/.test(s); }),
  J([KX4, K3H, KCampur]));

// ---- K1 · sesi hbSesi ASLI di server mainan: perangkat baru (belum terbaca) → baca penuh hari ini = lengkap → hari kuota berganti, baca penuh harian toko
//      dipegang perangkat lain & BELUM selesai = "harian" (hitungan tetap cocok, gerbang lain tidak berubah) → selesai = lengkap; tombol baca penuh = lengkap sendiri
tokoBaru('2026-11-10T03:00:00Z'); S.tulis('penjualan', 'p1', notaN('p1', 1000), true); S.tulis('pengeluaranHarian', 'h1', { id: 'h1', tanggal: '2026-11-10', nominal: 500 }, true);
var K1 = new Perangkat('mac-k1'); K1.buka({ tetap: false }); var blK0 = K1.sesi.belumLengkap();
ok('K1 sebelum simpanan perangkat terbaca: SEMUA koleksi belum lengkap ("periksa", belum terbaca dari simpanan perangkat)', NAMA_K.every(function (k) { return blK0[k] && blK0[k].jenis === 'periksa' && /simpanan perangkat/.test(blK0[k].sebab); }), J(blK0));
tuntas(); K1.gema(); K1.tetap(); tuntas();
ok('K1 perangkat baru sesudah baca penuh semua koleksi (hari kuota ini) → kelengkapan KOSONG (semua lengkap), keadaan() membawanya, terperiksa sama', J(K1.sesi.belumLengkap()) === '{}' && J(K1.sesi.keadaan().belumLengkap) === '{}' && !cekSatuSumber(K1).length, J(K1.sesi.belumLengkap()));
S.klaim = { id: 'hematHarian', hari: '2026-11-10', perangkat: 'ipad-lain', nama: 'iPad contoh', mulai: Z('2026-11-10T08:05:00Z'), selesai: null };
maju(Z('2026-11-10T08:10:00Z') - S.jam); K1.tetap(); K1.gema(); tuntas();
var blK1 = K1.sesi.belumLengkap();
ok('K1 hari kuota baru (15.10 WIB), baca penuh harian toko masih dipegang perangkat lain: SEMUA koleksi "harian" — belum dibaca penuh sejak kuota baca direset pukul 15.00 WIB, ketuk baca penuh sekarang; tetap terperiksa (katalog & uang-kritis tidak berubah)',
  S.klaim.perangkat === 'ipad-lain' && !K1.klaimTulis && NAMA_K.every(function (k) { return blK1[k] && blK1[k].jenis === 'harian' && blK1[k].sebab === hbSebabHarian('2026-11-10') && keadaanK(K1, k).terperiksa === true && K1.periksa[k] === true; }) && !cekSatuSumber(K1).length,
  J([blK1, K1.klaimTulis, cekSatuSumber(K1)]));
S.klaim = Object.assign({}, S.klaim, { selesai: S.jam }); K1.tetap(); tuntas();
ok('K1 baca penuh harian toko SELESAI (perangkat lain) → perangkat ini lengkap tanpa membaca penuh sendiri', J(K1.sesi.belumLengkap()) === '{}' && !K1.L.some(function (L) { return L.aktif && L.jenis === 'penuh'; }), J(K1.sesi.belumLengkap()));
S.klaim = { id: 'hematHarian', hari: '2026-11-11', perangkat: 'ipad-lain', nama: 'iPad contoh', mulai: Z('2026-11-11T08:05:00Z'), selesai: null };
maju(Z('2026-11-11T08:10:00Z') - S.jam); K1.tetap(); K1.gema(); tuntas(); var blK2 = K1.sesi.belumLengkap();
K1.sesi.bacaPenuh(null, 'tombol "Baca penuh sekarang"', true); tuntas(); maju(20000);
ok('K1 hari berikutnya "harian" lagi; tombol "baca penuh sekarang" → dibaca penuh hari ini → lengkap walau baca penuh harian toko belum selesai', NAMA_K.every(function (k) { return blK2[k] && blK2[k].jenis === 'harian'; }) && J(K1.sesi.belumLengkap()) === '{}' && !S.klaim.selesai,
  J([blK2, K1.sesi.belumLengkap()]));
// ---- K2 · dengar penuh karena penulis tanpa cap (HP kasir < kasir-v33) = lengkap tanpa baca penuh harian; koleksi lain tetap "harian"
S.klaim = { id: 'hematHarian', hari: '2026-11-12', perangkat: 'ipad-lain', nama: 'iPad contoh', mulai: Z('2026-11-12T08:05:00Z'), selesai: null };
maju(Z('2026-11-12T08:10:00Z') - S.jam); S.perangkat = [hpKasir('kasir-v32')]; K1.tetap(); K1.gema(); tuntas(); maju(2000); var blK3 = K1.sesi.belumLengkap();
ok('K2 HP kasir lama → penjualan DENGAR PENUH = lengkap; koleksi lain "harian"', keadaanK(K1, 'penjualan').mode === 'penuh' && !blK3.penjualan && blK3.pengeluaranHarian && blK3.pengeluaranHarian.jenis === 'harian' && !cekSatuSumber(K1).length, J(blK3));
// ---- K3 · batu nisan belum dicocokkan (pendengar nisan galat) → "periksa"
K1.sesi._G.nTerkini = false; var blK4 = K1.sesi.belumLengkap(); K1.sesi._G.nTerkini = true;
ok('K3 batu nisan belum dicocokkan → semua koleksi "periksa" (catatan yang dihapus di server)', NAMA_K.every(function (k) { return blK4[k] && blK4[k].jenis === 'periksa' && /catatan yang dihapus/.test(blK4[k].sebab); }), J(blK4));
K1.tutup(); S.perangkat = [];

// ---- K5 · tab KALAH kunci tab (sanggahan 7 Okt): firebase.js berhenti() → _hemat.berhenti() + terminate, _hemat TIDAK di-null-kan (layar tetap membacanya).
//      Dulu kelengkapan tetap {} (lengkap) padahal tab itu tidak menerima data lagi — kartu pemeriksaan "beres", rekap pajak & dokumen Laporan tidak ditahan
tokoBaru('2026-11-20T09:00:00Z');
S.tulis('penjualan', 'q1', notaN('q1', 1000), true); S.tulis('stokBahanLiteran', 't1', { id: 't1', kg: 1 }, true); S.tulis('piutangMutasi', 'm1', { id: 'm1', nominal: 1 }, true); S.tulis('pengeluaranHarian', 'e1', { id: 'e1', nominal: 1 }, true);
var K5 = new Perangkat('mac-k5'); K5.buka(); var blK5a = K5.sesi.belumLengkap();
K5.sesi.berhenti(); tuntas(); S.tulis('penjualan', 'q2', notaN('q2', 2000), true); tuntas(); maju(5 * MNT);
var blK5 = K5.sesi.belumLengkap(), kdK5 = K5.sesi.keadaan(); var US5 = null; K5.sesi.pastikanSegar().then(function (r) { US5 = r; }); tuntas();
ok('K5 tab KALAH kunci tab: sebelum = lengkap; sesudah berhenti = SEMUA jenis catatan "periksa" (tidak diperbarui lagi di tab ini — muat ulang aplikasi), keadaan().belum semua, katalog & uang-kritis menolak — memori membeku (q2 server tidak ada)',
  J(blK5a) === '{}' && NAMA_K.every(function (k) { return blK5[k] && blK5[k].jenis === 'periksa' && blK5[k].sebab === HB_SEBAB_TAB_BERHENTI; }) && kdK5.belum.length === NAMA_K.length
  && J(memId(K5, 'penjualan')) === '["q1"]' && J(S.ids('penjualan')) === '["q1","q2"]' && K5.sesi.bolehKatalog().boleh === false && US5 && !US5.ok && /berhenti menerima data/.test(US5.pesan) && !cekSatuSumber(K5).length,
  J([blK5a, blK5, kdK5.belum, US5, cekSatuSumber(K5)]));
K5.tutup(); S.dev = [];

// ---- K6 · baca penuh harian TOKO ditulis "selesai" hanya sesudah temuan pendeteksi terkirim (sanggahan 7 Okt). Dulu "selesai" langsung: perangkat lain
//      melapor LENGKAP (klaim hari ini selesai) padahal ubahan Console itu tidak pernah sampai lewat delta — kunci bulan bisa membekukan potret tanpa ubahan itu
S = new Server(Z('2026-11-20T03:00:00Z'));   // 10.00 WIB, hari kuota 19 Nov
// r1, r3, r4 = nota LAMA (cap 3 jam sebelum perangkat dibuka — selalu di luar jendela delta kedua perangkat); r2 = nota baru
S.jam -= 3 * HR; ['r1', 'r3', 'r4'].forEach(function (id, i) { S.tulis('penjualan', id, notaN(id, 10000 * (i + 1)), true); }); S.jam += 3 * HR;
S.tulis('penjualan', 'r2', notaN('r2', 5000), true); S.tulis('stokBahanLiteran', 'u1', { id: 'u1', kg: 1 }, true);
S.tulis('piutangMutasi', 'v1', { id: 'v1', nominal: 1 }, true); S.tulis('pengeluaranHarian', 'w1', { id: 'w1', nominal: 1 }, true); klaimHariIni();
var A6 = new Perangkat('mac-k6'); A6.buka(); var B6 = new Perangkat('ipad-k6'); B6.buka();
maju(2 * JM); S.tulis('penjualan', 'r1', notaN('r1', 99000), 'tetap'); tuntas();   // Console: isi nota LAMA berubah (di luar jendela delta), cap lama dibiarkan
A6.sentuhGagal = 1;                                                                   // sentuhan pertama ditolak, berikutnya berhasil
maju(Z('2026-11-20T08:10:00Z') - S.jam); A6.gema(); A6.tetap(); A6.sesi.tik(); tuntas(); maju(20000); B6.gema(); B6.tetap(); tuntas();
var kl6a = salin(S.klaim), blB6a = B6.sesi.belumLengkap();
ok('K6 baca penuh harian toko (Mac) menemukan ubahan Console, sentuhannya GAGAL sekali → "selesai" BELUM ditulis (antrean temuan belum habis); iPad: penjualan "harian" (belum dibaca penuh sejak 15.00 WIB), bukan lengkap',
  kl6a.perangkat === 'mac-k6' && kl6a.hari === '2026-11-20' && !kl6a.selesai && /"r1"/.test(J(A6.R.ulang || {})) && !!blB6a.penjualan && blB6a.penjualan.jenis === 'harian' && blB6a.penjualan.sebab === hbSebabHarian('2026-11-20')
  && memDok(B6, 'penjualan', 'r1').hargaTotal === 10000, J([kl6a, A6.R.ulang, blB6a]));
maju(MNT); A6.sesi.tik(); tuntas(); maju(1000); B6.tetap(); tuntas();
var kl6b = salin(S.klaim), blB6b = B6.sesi.belumLengkap();
ok('K6: dicoba lagi semenit kemudian → tersentuh → iPad menerima ubahannya lewat delta → "selesai" ditulis TANPA temuan tertunda → iPad lengkap DAN isinya benar',
  !!kl6b.selesai && !kl6b.temuanTunda && memDok(B6, 'penjualan', 'r1').hargaTotal === 99000 && J(blB6b) === '{}' && !cekSatuSumber(B6).length, J([kl6b, blB6b, memDok(B6, 'penjualan', 'r1')]));
// K6b · sentuhan gagal PERMANEN (5 kali) → "selesai" dengan temuanTunda per jenis catatan
maju(Z('2026-11-21T07:00:00Z') - S.jam); S.tulis('penjualan', 'r3', notaN('r3', 77000), 'tetap'); tuntas(); A6.sentuhGagal = 999;
maju(Z('2026-11-21T08:10:00Z') - S.jam); A6.gema(); A6.tetap(); A6.sesi.tik(); tuntas(); maju(20000); B6.gema(); B6.tetap(); tuntas();
var kl6c0 = salin(S.klaim); for (var i6 = 0; i6 < 6; i6++) { maju(MNT); A6.sesi.tik(); tuntas(); }
B6.tetap(); tuntas(); var kl6c = salin(S.klaim), blB6c = B6.sesi.belumLengkap();
ok('K6b sentuhan gagal PERMANEN (5 kali): selama dicoba belum "selesai"; lalu "selesai" dengan temuanTunda { penjualan: 1 } → iPad: penjualan "harian" (ubahan yang ditemukan baca penuh harian toko belum sampai ke perangkat ini), jenis lain lengkap; Mac mengaku di kabarnya',
  !kl6c0.selesai && !!kl6c.selesai && J(kl6c.temuanTunda) === '{"penjualan":1}' && !!blB6c.penjualan && blB6c.penjualan.jenis === 'harian' && blB6c.penjualan.sebab === HB_SEBAB_TOKO_TUNDA && Object.keys(blB6c).length === 1
  && memDok(B6, 'penjualan', 'r3').hargaTotal === 20000 && /gagal ditandai/.test(A6.sesi.keadaan().kabar), J([kl6c0, kl6c, blB6c, A6.sesi.keadaan().kabar]));
A6.sentuhGagal = 0; B6.sesi.bacaPenuh(null, 'tombol', true); tuntas(); maju(20000);
ok('K6b: iPad membaca penuh sendiri (ketukan yang disebut kalimatnya) → lengkap & isinya benar', J(B6.sesi.belumLengkap()) === '{}' && memDok(B6, 'penjualan', 'r3').hargaTotal === 77000, J([B6.sesi.belumLengkap(), memDok(B6, 'penjualan', 'r3')]));
// K6c · ubahan Console di bulan TERKUNCI: penyentuh melewatinya (tidak bisa disentuh) — dulu dibuang diam-diam, kini dilaporkan & dihitung
maju(Z('2026-11-22T07:00:00Z') - S.jam); S.kunci = { r4: true }; S.tulis('penjualan', 'r4', notaN('r4', 98000), 'tetap'); tuntas();
maju(Z('2026-11-22T08:10:00Z') - S.jam); A6.gema(); A6.tetap(); A6.sesi.tik(); tuntas(); maju(20000); B6.gema(); B6.tetap(); tuntas();
var kl6d = salin(S.klaim), blB6d = B6.sesi.belumLengkap();
ok('K6c ubahan Console di bulan TERKUNCI (tidak bisa disentuh): DILAPORKAN penyentuh → "selesai" dengan temuanTunda { penjualan: 1 }, iPad penjualan "harian"; kabar Mac menyebut bulan terkunci; tidak diulang-ulang',
  kl6d.hari === '2026-11-22' && !!kl6d.selesai && J(kl6d.temuanTunda) === '{"penjualan":1}' && !!blB6d.penjualan && blB6d.penjualan.sebab === HB_SEBAB_TOKO_TUNDA && /bulan terkunci/.test(A6.sesi.keadaan().kabar)
  && !/"r4"/.test(J(A6.R.ulang || {})) && memDok(B6, 'penjualan', 'r4').hargaTotal === 30000, J([kl6d, blB6d, A6.sesi.keadaan().kabar, A6.R.ulang]));
S.kunci = null; A6.tutup(); B6.tutup(); S.dev = [];

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
  var HKm = hematKeadaan();
  ok('C11 saklar MATI: hematKeadaan() = { nyala: false } TANPA belumLengkap — layar (kartu pemeriksaan, kunci bulan, pajak, tutup buku) menghitung persis seperti dulu', HKm.nyala === false && !('belumLengkap' in HKm), J(HKm));
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
  var HKn = hematKeadaan(); var blN = HKn.belumLengkap || {};
  ok('C11 saklar NYALA: hematKeadaan().belumLengkap = SATU sumber (sesi hemat) — sebelum simpanan terbaca SEMUA koleksi hemat belum lengkap ("periksa"), koleksi tetap tidak disebut',
    HKn.nyala === true && Object.keys(blN).sort().join(',') === hbKoleksiHemat().slice().sort().join(',') && Object.keys(blN).every(function (k) { return blN[k].jenis === 'periksa' && /simpanan perangkat/.test(blN[k].sebab); }) && !blN.tutupBukuAcara && !blN.aturanToko,
    J([HKn.nyala, Object.keys(blN).length]));
  // gema jam server: denyut LAMA (dari sesi sebelumnya) TIDAK dipakai; denyut yang dikirim sesi ini dan diakui server → selisih jam server − jam perangkat
  var Lps = D5.find(function (L) { return L.ref.nama === 'perangkatStatus'; }); var idP = idPerangkat();
  var snapP = function (pada, ms) { return { metadata: { fromCache: false }, forEach: function (f) { f({ id: idP, data: function () { return { id: idP, pada: pada, aplikasi: 'baru', versi: 'baru-c1', capServer: { toMillis: function () { return ms; } } }; }, metadata: { hasPendingWrites: false } }); } }; };
  Lps.cb(snapP('2026-10-01T00:00:00.000Z', 1000)); var skew0 = _hemat._G.skew;
  kirimDenyut(true); Lps.cb(snapP(_denyutKirim.pada, _denyutKirim.ms + 777));
  ok('C7 gema jam server: denyut lama (sesi sebelumnya, cap berjam-jam lalu) TIDAK dipakai; denyut sesi ini yang diakui server → selisih jam = cap − jam kirim', skew0 === null && _hemat._G.skew === 777, J([skew0, _hemat._G.skew]));
  ok('C7: memori denyut tanpa capServer (dikupas)', !('capServer' in (cacheMentah('perangkat')[0] || {})));
  // ---- C8 · penyentuh memakai isi MENTAH sesi hemat: catatan LAHIR ULANG yang tersembunyi nisan tidak ada di memori (dokDiCache) — dulu tidak pernah disentuh
  var Vp = D5.find(function (L) { return L.opsi && L.opsi.source === 'cache' && L.ref.nama === 'penjualan'; });
  var T8 = Date.UTC(2026, 9, 8, 3);
  var mk8 = function (id, cap) { return { id: id, metadata: { hasPendingWrites: false }, get: function (f) { return f === 'capServer' ? cap : undefined; },
    data: function () { var x = { id: id, tanggal: '2026-10-08', hargaTotal: 1000, namaPelanggan: 'Pembeli Contoh', diubahPada: '2099-01-01T00:00:00.000Z' }; if (cap !== undefined) x.capServer = cap; return x; } }; };
  _hemat._G.nisan = { penjualan: { x1: T8 } };
  Vp.cb({ metadata: { fromCache: true }, docs: [mk8('x1', undefined), mk8('x2', { toMillis: function () { return T8 - 5000; } }), mk8('x3', undefined)] }); drainMicrotasks();
  __rek.tulis = []; var s8a = null, s8b = null;
  sentuhCap('penjualan', ['x1']).then(function (r) { s8a = r; }); drainMicrotasks();
  sentuhCap('penjualan', ['x1'], function (id) { var v = _hemat._K.penjualan.v[id]; return v ? v.data : null; }).then(function (r) { s8b = r; }); drainMicrotasks();
  var op8 = (__rek.tulis[0] || [])[0] || [];
  ok('C8 penyentuh: catatan LAHIR ULANG (tersembunyi nisan, tidak di memori) disentuh lewat isi mentah simpanan sesi hemat — tanpa isi mentah nol tulisan',
    cacheMentah('penjualan').map(function (d) { return String(d.id); }).sort().join() === 'x2,x3' && s8a && s8a.n === 0 && s8b && s8b.n === 1 && __rek.tulis.length === 1
    && op8[0] === 'update' && op8[1] === 'penjualan' && op8[2] === 'x1' && CAP(op8[3]), J([s8a, s8b, __rek.tulis]));
  // ---- C10 · daftar siap-nyala "statis" saat nyala: cap dari simpanan sesi hemat (peta samping _cap hanya diisi pendengar penuh)
  var st10 = hematSiapNyala().find(function (x) { return x.id === 'statis'; });
  ok('C10 siap-nyala saat NYALA: catatan BERCAP tidak dihitung "tanpa cap" (x2), catatan tanpa cap yang tampil dihitung (x3) — baris statis tidak berbohong',
    hitungStatis() === 1 && st10 && !st10.ok && /^1 catatan/.test(st10.ket), J([hitungStatis(), st10]));
  // ---- C14 · (audit P5) berita acara tutup buku dari SIMPANAN perangkat bukan jawaban server: sesi hemat menahan koleksinya (pil memuat, tanpa S, memori
  //      beku) sampai pendengar tutupBukuAcara dijawab SERVER — sekali dijawab, tetap (jawaban berikutnya dari simpanan karena putus tidak membatalkannya)
  var Lacara = D5.find(function (L) { return L.ref.nama === 'tutupBukuAcara'; }), Latur = D5.find(function (L) { return L.ref.nama === 'aturanToko'; });
  var snapTetap = function (dariCache) { return { metadata: { fromCache: dariCache }, forEach: function () {} }; };
  Latur.cb(snapTetap(false)); Lacara.cb(snapTetap(true)); var c14a = { ada: _hemat._G.tetap.ada, server: _hemat._G.bkServer };
  Lacara.cb(snapTetap(false)); var c14b = _hemat._G.bkServer; Lacara.cb(snapTetap(true)); var c14c = _hemat._G.bkServer;
  // sanggahan kedua P5 (M31): koleksi tetap LAIN (denyut, setelan) dijawab server selagi berita acara masih dari simpanan → BUKAN jawaban berita acara
  Lps.cb(snapTetap(false)); var c14d = _hemat._G.bkServer; Latur.cb(snapTetap(false)); var c14e = _hemat._G.bkServer; Lacara.cb(snapTetap(false)); var c14f = _hemat._G.bkServer;
  ok('C14 (audit P5 · sanggahan kedua) firebase.js meneruskan asal berita acara tutup buku: dari simpanan perangkat → sesi hemat belum menganggapnya jawaban server; dari server → ya; kembali "dari simpanan" (server berhenti menjawab) → tidak lagi; denyut / setelan dari server selagi berita acara masih dari simpanan → tetap tidak',
    c14a.ada === true && c14a.server === false && c14b === true && c14c === false && c14d === false && c14e === false && c14f === true, J([c14a, c14b, c14c, c14d, c14e, c14f]));
  // uang-kritis & kunci tab di penulis pusat
  var asli = _hemat, dicatat = []; _hemat = { pastikanSegar: function () { return Promise.resolve({ ok: false, pesan: 'data penjualan belum cocok dengan server — uji' }); }, adaMati: function () { return false; }, catatHapus: function () {},
    catatTulis: function (k, id) { dicatat.push(k + '|' + id); }, keadaan: asli.keadaan, ringkasDenyut: asli.ringkasDenyut };
  var u1 = null, u2 = null; __rek.tulis = [];
  tulisBerkas([{ koleksi: 'tutupHari', data: { id: '2026-10-07', tanggal: '2026-10-07' } }], []).then(function (r) { u1 = r; }); drainMicrotasks();
  tulisBerkas([{ koleksi: 'penjualan', data: { id: 'n5', tanggal: '2026-10-07', hargaTotal: 5000 } }], []).then(function (r) { u2 = r; }); drainMicrotasks();
  ok('C6 uang-kritis: tutup hari saat hitungan server belum segar → DITOLAK dengan kalimatnya, tidak ada yang dikirim; nota biasa tetap jalan',
    u1 && u1.gagal && /belum cocok/.test(u1.pesan) && u2 && !u2.gagal && __rek.tulis.length === 1 && __rek.tulis[0][0][1] === 'penjualan', J([u1, u2, __rek.tulis.length]));
  // sanggahan kedua P5: memori juga beku saat putus di hari biasa — ubah kolom lewat perbaruiBerkas ("Bersihkan ciri") ikut dicatat
  perbaruiBerkas([[{ koleksi: 'pelangganCatatan', id: 'pc9', kolom: { ciri: [] } }]], 'uji'); drainMicrotasks();
  ok('C15 (audit P5 · sanggahan kedua) tulisBerkas & perbaruiBerkas mencatat tulisan perangkat ini ke sesi hemat (tetap tampil di memori yang dibekukan selama ditahan); kiriman UANG-KRITIS yang ditolak sebelum dikirim tidak dicatat',
    dicatat.indexOf('penjualan|n5') >= 0 && dicatat.indexOf('pelangganCatatan|pc9') >= 0 && !dicatat.some(function (x) { return /^tutupHari/.test(x); }), J(dicatat));
  __ls[HB_KUNCI_TAB] = J({ sesi: 'tab-lain', detak: Date.now() }); var u3 = null;
  tulisBerkas([{ koleksi: 'penjualan', data: { id: 'n6', tanggal: '2026-10-07', hargaTotal: 6000 } }], []).then(function (r) { u3 = r; }); drainMicrotasks();
  ok('C6 kunci tab: tab yang KALAH (tab lain menekan "Pakai di sini") tidak menulis apa pun', u3 && u3.gagal && /tab lain/.test(u3.pesan), J(u3));
  _hemat = asli;
  // ---- C9 · penyentuh di tab yang tidak boleh menulis: temuannya DIKEMBALIKAN (tunda) supaya sesi hemat mengulangnya — dulu { n: 0 } = dibuang diam-diam
  __rek.tulis = []; var s9 = null, n9 = null;
  sentuhCap('penjualan', ['x2'], function () { return { id: 'x2', tanggal: '2026-10-08' }; }).then(function (r) { s9 = r; }); tulisNisanSaja('penjualan', ['h9']).then(function (r) { n9 = r; }); drainMicrotasks();
  ok('C9 tab kalah kunci: sentuhan & batu nisan pendeteksi tidak ditulis, id-nya kembali sebagai "tunda" (diulang sesi hemat)', s9 && s9.n === 0 && J(s9.tunda) === '["x2"]' && n9 && J(n9.tunda) === '["h9"]' && !__rek.tulis.length, J([s9, n9]));
  // ---- C12 · (sanggahan 7 Okt) penyentuh: catatan di bulan TERKUNCI tidak bisa disentuh — DILAPORKAN sebagai `lewat` (dulu dibuang diam-diam: bukan n, bukan tunda)
  _kunciTab.ambil(); pasok('aturanToko', [{ id: 'kunciPeriode', sampaiBulan: '2026-09', riwayat: [] }]); __rek.tulis = []; var s12 = null;
  sentuhCap('penjualan', ['k9', 'k10'], function (id) { return { id: id, tanggal: id === 'k9' ? '2026-09-10' : '2026-10-08' }; }).then(function (r) { s12 = r; }); drainMicrotasks();
  var op12 = (__rek.tulis[0] || []).filter(function (o) { return o[1] === 'penjualan'; });
  ok('C12 penyentuh: catatan bulan terkunci (Sep 2026) DILEWATI dan dilaporkan `lewat` (sesi hemat menghitungnya); catatan bulan terbuka disentuh', s12 && s12.n === 1 && J(s12.tunda) === '[]' && J(s12.lewat) === '["k9"]'
    && op12.length === 1 && op12[0][2] === 'k10', J([s12, __rek.tulis]));
  pasok('aturanToko', []);
  // ---- C13 · (sanggahan 7 Okt) tab KALAH kunci tab: berhenti() → sesi hemat berhenti, _hemat tidak di-null-kan → hematKeadaan().belumLengkap = SEMUA koleksi hemat
  //      "periksa — tidak diperbarui lagi di tab ini" (dulu tetap {} / keadaan lama: kartu pemeriksaan, pajak & dokumen Laporan tidak ditahan)
  berhenti('uji: tab lain menekan Pakai di sini'); drainMicrotasks(); var H13 = hematKeadaan(); var bl13 = H13.belumLengkap || {};
  ok('C13 tab kalah (firebase.js berhenti): hematKeadaan().belumLengkap = semua koleksi hemat "periksa" dengan sebab muat ulang; tulisan ditolak',
    H13.nyala === true && Object.keys(bl13).length === hbKoleksiHemat().length && Object.keys(bl13).every(function (k) { return bl13[k].jenis === 'periksa' && bl13[k].sebab === HB_SEBAB_TAB_BERHENTI; }) && !!jagaTulisHemat(),
    J([H13.nyala, Object.keys(bl13).length, bl13.penjualan]));
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
    (r"b\.set\(doc\(db, KOLEKSI_FOTO_BON, String\(d\.id\)\), d\)", 'fotoBon (paket E-2): tidak didengar & bukan koleksi.js (dibaca sekali saat bon dibuka); rules v7 blok fotoBon membatasi bentuk & ukuran, tanpa ubah'),
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


# ---------- E · KASIR DARURAT di jsc: fungsi ASLI kirimAntrean (dipotong dari halaman) + Firestore REST palsu bermodel rules (v3 / v6 / v7) ----------
# Tinjauan 7 Okt: kasir-v33 mengirim nota lewat :commit + capServer REQUEST_TIME. Jawaban :commit yang HILANG (sinyal putus) lalu kirim ulang :commit = cap lain
# → rules v6 / v3 (sebelum v7 terbit, atau aturan darurat) MENOLAK padahal notanya sudah masuk → dulu pindah ke "ditolak" → catat ulang → omzet dobel.
# Kini nota yang :commit-nya ditolak dikirim sekali lagi dengan CARA LAMA (PATCH, updateMask = kolom karcis) sebelum dinyatakan ditolak. Peramban asli: CI.
KASIR_FUNGSI = ['keFs', 'ambilAntrean', 'simpanAntrean', 'ambilGagal', 'golonganJawaban', 'pindahKeDitolak', 'cabutDariAntrean', 'kirimAntrean', 'kolomLama']
KASIR_VAR = ['PROYEK', 'KUNCI_API', 'DASAR', 'URL_COMMIT', 'NAMA_DOK', 'K_ANTREAN', 'K_GAGAL', 'sedangKirim']
KASIR_PRA = r"""
var __ls = {}; var localStorage = { getItem: function (k) { return Object.prototype.hasOwnProperty.call(__ls, k) ? __ls[k] : null; }, setItem: function (k, v) { __ls[k] = String(v); }, removeItem: function (k) { delete __ls[k]; } };
var navigator = { onLine: true }; var __login = 0;
function setStatus() {} function kirimDenyutD() {} function gambarPitaDitolak() {} function lupakanKunciSesi() {} function tampilkanLayarLogin() { __login++; }
function sudahLogin() { return true; }
function denganAuth(opsi) { opsi = opsi || {}; opsi.headers = opsi.headers || {}; opsi.headers.Authorization = 'Bearer t-uji'; return Promise.resolve(opsi); }
// ---- Firestore REST palsu: dokumen tersimpan, rules kasir@ penjualan: create = bulan tidak terkunci; update = tulisUlangSama (v3, v6) atau + ulangKasirBercap (v7)
var SRV = { aturan: 'v7', dok: {}, hilang: 0, kunciBulan: '2026-08', minta: [], jam: 1000 };
function nilaiFs(v) { if (!v) return null; if ('stringValue' in v) return v.stringValue; if ('integerValue' in v) return Number(v.integerValue); if ('doubleValue' in v) return v.doubleValue;
  if ('booleanValue' in v) return v.booleanValue; if ('nullValue' in v) return null; if ('mapValue' in v) { var o = {}, f = v.mapValue.fields || {}; for (var k in f) o[k] = nilaiFs(f[k]); return o; } return null; }
function urut(v) { return v && typeof v === 'object' ? Object.keys(v).sort().reduce(function (o, k) { o[k] = urut(v[k]); return o; }, {}) : v; }
function sama(a, b) { return JSON.stringify(urut(a)) === JSON.stringify(urut(b)); }
function jawab(status, isi) { return Promise.resolve({ status: status, json: function () { return Promise.resolve(isi || {}); } }); }
function fetch(url, opsi) {
  var komit = url.indexOf('/documents:commit') >= 0, nama, fields, cap = false, mask = null;
  if (komit) { var w = JSON.parse(opsi.body).writes; if (w.length !== 1) return jawab(400, {}); w = w[0]; nama = w.update.name.split('/documents/')[1]; fields = w.update.fields;
    cap = (w.updateTransforms || []).some(function (x) { return x.fieldPath === 'capServer' && x.setToServerValue === 'REQUEST_TIME'; }); if (w.updateMask) mask = w.updateMask.fieldPaths; }
  else { var u = url.split('/documents/')[1]; nama = decodeURIComponent(u.split('?')[0]); fields = JSON.parse(opsi.body).fields;
    var ms = (u.split('?')[1] || '').split('&').filter(function (x) { return x.indexOf('updateMask.fieldPaths=') === 0; }).map(function (x) { return decodeURIComponent(x.slice(22)); }); if (ms.length) mask = ms; }
  var data = {}; for (var k in fields) data[k] = nilaiFs(fields[k]);
  var lama = SRV.dok[nama], jamMinta = ++SRV.jam, baru;
  if (mask) { baru = Object.assign({}, lama || {}); mask.forEach(function (f) { if (f in data) baru[f] = data[f]; else delete baru[f]; }); } else baru = data;
  if (cap) baru.capServer = { jam: jamMinta };
  SRV.minta.push(komit ? 'commit' : mask ? 'patch-mask' : 'patch');
  var boleh;
  if (!lama) boleh = String(data.tanggal || '').slice(0, 7) > SRV.kunciBulan;
  else { var beda = Object.keys(Object.assign({}, lama, baru)).filter(function (x) { return !sama(lama[x], baru[x]); });
    var ukb = beda.every(function (x) { return x === 'capServer'; }) && (!('capServer' in baru) || (baru.capServer && baru.capServer.jam === jamMinta));
    boleh = !beda.length || (SRV.aturan === 'v7' && ukb); }
  if (!boleh) return jawab(403, { error: { code: 403, status: 'PERMISSION_DENIED' } });
  SRV.dok[nama] = baru;
  if (SRV.hilang > 0) { SRV.hilang--; return Promise.reject(new TypeError('Failed to fetch')); }   // tulisan MASUK, jawabannya hilang di jalan
  return jawab(200, {});
}
"""
KASIR_SKENARIO = r"""
var gagal = [], lulus = 0; function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket !== undefined ? ' → ' + String(typeof ket === 'string' ? ket : JSON.stringify(ket)).slice(0, 500) : '')); }
var J = JSON.stringify;
function karcis(id, h, tgl) { return { koleksi: 'penjualan', docId: String(id), data: { id: id, tanggal: tgl || '2026-10-07', jam: '10:00', jenis: 'kasir_darurat_nominal', namaProduk: '(tidak tercatat — kasir darurat)',
  hargaTotal: h, caraBayar: 'Tunai', namaPelanggan: '', grupNota: id, oleh: '(darurat tanpa nama)', perangkat: 'd-uji' } }; }
function mulaiE(aturan, antrean) { SRV.aturan = aturan; SRV.dok = {}; SRV.minta = []; SRV.hilang = 0; __ls = {}; localStorage.setItem(K_ANTREAN, J(antrean)); sedangKirim = false; }
function jalanE() { kirimAntrean(true); drainMicrotasks(); }
function potret() { var d = SRV.dok; var ks = Object.keys(d); return { antrean: ambilAntrean().length, ditolak: ambilGagal().map(function (x) { return x.ditolak && x.ditolak.status; }), minta: SRV.minta.slice(),
  server: ks.length, cap: ks.map(function (k) { return d[k].capServer ? d[k].capServer.jam : null; }) }; }
var ID = 1791331200001.25, ID2 = 1791331200002.5;
['v6', 'v3'].forEach(function (a) {
  mulaiE(a, [karcis(ID, 6100)]); SRV.hilang = 1; jalanE(); var p0 = potret(); jalanE(); var p1 = potret();
  ok('E1 rules ' + a + ' (v7 belum terbit / aturan darurat): jawaban :commit HILANG → kirim ulang :commit ditolak (cap beda) → CARA LAMA (PATCH, updateMask) MASUK — nota tidak pindah ke "ditolak", cap pertama tetap',
    p0.antrean === 1 && p0.server === 1 && p1.antrean === 0 && !p1.ditolak.length && J(p1.minta) === '["commit","commit","patch-mask"]' && p1.server === 1 && J(p1.cap) === J(p0.cap) && p1.cap[0] !== null, J([p0, p1]));
});
mulaiE('v7', [karcis(ID, 6100)]); SRV.hilang = 1; jalanE(); jalanE(); var e2 = potret();
ok('E2 rules v7: kirim ulang :commit (hanya cap berbeda) diterima ulangKasirBercap — tanpa cara lama, nota bercap', e2.antrean === 0 && !e2.ditolak.length && J(e2.minta) === '["commit","commit"]' && e2.cap[0] !== null, J(e2));
['v6', 'v7'].forEach(function (a) {
  mulaiE(a, [karcis(ID, 5100), karcis(ID2, 5200, '2026-08-31'), karcis(ID2 + 1, 5300)]); jalanE(); var e3 = potret(); jalanE(); var e3b = potret();
  ok('E3 rules ' + a + ': karcis bulan TERKUNCI — :commit ditolak, cara lama juga ditolak → baru masuk daftar "ditolak" (403); karcis lain jalan; tidak dikirim ulang',
    e3.antrean === 0 && J(e3.ditolak) === '[403]' && J(e3.minta) === '["commit","commit","patch-mask","commit"]' && e3.server === 2 && J(e3b.minta) === J(e3.minta), J([e3, e3b]));
});
// HP baru naik dari kasir-v32 ke v33 dengan karcis yang SUDAH masuk lewat PATCH v32 (tanpa cap) tapi jawabannya hilang
mulaiE('v6', [karcis(ID, 6100)]); SRV.dok['penjualan/' + ID] = (function () { var x = karcis(ID, 6100).data; return JSON.parse(J(x)); })(); jalanE(); var e4 = potret();
ok('E4 rules v6: nota yang sudah masuk lewat PATCH v32 (tanpa cap) dikirim ulang kasir-v33 → :commit ditolak → cara lama identik → MASUK (tanpa cap, seperti dulu)',
  e4.antrean === 0 && !e4.ditolak.length && J(e4.minta) === '["commit","patch-mask"]' && e4.cap[0] === null, J(e4));
mulaiE('v7', [karcis(ID, 6100)]); SRV.dok['penjualan/' + ID] = JSON.parse(J(karcis(ID, 6100).data)); jalanE(); var e5 = potret();
ok('E5 rules v7: nota v32 tanpa cap dikirim ulang kasir-v33 → :commit diterima (cap ditambahkan = jam server permintaan itu)', e5.antrean === 0 && !e5.ditolak.length && J(e5.minta) === '["commit"]' && e5.cap[0] !== null, J(e5));
ok('E kolomLama: updateMask = tepat kolom karcis; nama kolom di luar huruf/angka/garis bawah dikutip backtick', kolomLama({ a: 1, b_2: 1, 'x-y': 1 }) === '&updateMask.fieldPaths=a&updateMask.fieldPaths=b_2&updateMask.fieldPaths=' + encodeURIComponent('`x-y`'), kolomLama({ a: 1, b_2: 1, 'x-y': 1 }));
print(J({ lulus: lulus, gagal: gagal }));
"""


def kasir_jsc(t):
    """E · kirimAntrean ASLI kasir darurat (fungsi & var dipotong dari script halaman) di jsc dengan Firestore REST palsu bermodel rules."""
    d = t['kasir-darurat-nominal.html']; potong = []
    for v in KASIR_VAR:
        m = re.search(r'^var ' + v + r' = [^\n]*;', d, re.M)
        if not m: return [('E · kasir darurat: var ' + v + ' ditemukan', False, '')]
        potong.append(m.group(0))
    for f in KASIR_FUNGSI:
        m = re.search(r'\nfunction ' + f + r'\([^)]*\) \{.*?\n\}\n', d, re.S)
        if not m: return [('E · kasir darurat: function ' + f + ' ditemukan', False, '')]
        potong.append(m.group(0))
    h, e = jalan(KASIR_PRA + '\n'.join(potong) + '\n' + KASIR_SKENARIO)
    if h is None: return [('E · kasir darurat jsc jalan', False, e)]
    return [('E · ' + str(i), True, '') for i in range(h['lulus'])] + [('E · ' + x, False, '') for x in h['gagal']]


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
    hasil = statis(t) + kasir_jsc(t)
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
    # tinjauan 7 Okt: dulu penggantinya menghasilkan "&& ) n += 1;" — SyntaxError, berbunyi karena jsc gagal jalan, bukan karena saringan nisan. Kini kerusakan SEMANTIK.
    ('(c) batu nisan tanpa banding cap → catatan yang dibuat ulang bercap lebih baru tetap tersembunyi', {HB: [("  if (typeof d.cap === 'number' && typeof t === 'number' && d.cap > t) return false;\n", "")]}),
    ('(c2) batu nisan mengabaikan bukti LAHIR ULANG (catatan tanpa cap yang dibuat lagi sesudah dihapus tersembunyi selamanya)', {HB: [("  if (typeof lahirT === 'number' && typeof t === 'number' && lahirT >= t) return false;\n", "")]}),
    ('(c3) pendeteksi tidak mencatat lahir ulang dari snapshot server baca penuh', {HB: [("    const lahir = catatLahir(k, peta);", "    const lahir = [];")]}),
    ('(c4) penyentuh memeriksa memori yang sudah disaring nisan (catatan lahir ulang tidak pernah disentuh)', {FB: [("const isi = (id) => (typeof lihat === 'function' ? lihat(id) : dokDiCache(koleksi, id));", "const isi = (id) => dokDiCache(koleksi, id);")]}),
    ('(c5) bukti lahir ulang tidak dibuang saat dihapus LAGI (nisan lebih baru)', {HB: [("if (t === undefined || t > L[id]) { delete L[id]; ubah = true; }", "if (t === undefined) { delete L[id]; ubah = true; }")]}),
    ('(d) Bn = 0 bila Wt kosong (seluruh riwayat nisan dibaca tiap buka)', {HB: [("  return c.length ? Math.min.apply(null, c) : null;\n}", "  return c.length ? Math.min.apply(null, c) : 0;\n}"), ("if (hbAngka(kiniS) > 0) c.push(kiniS - HB_MARGIN_MS);", "")]}),
    ('(e) tanda air dari jam PERANGKAT (bukan cap server)', {HB: [("Object.assign(r, { Wt: hbJepit(st.fMaks, s), n: st.fN, totalPada: kiniSTercatat(),", "Object.assign(r, { Wt: jam(), n: st.fN, totalPada: kiniSTercatat(),")]}),
    ('(f) jepit + 10 menit dibuang (cap 2099 membekukan delta)', {HB: [("const c = hbAngka(capMaks); if (c === null) return kiniS; return Math.min(c, kiniS + HB_JEPIT_MS);", "const c = hbAngka(capMaks); if (c === null) return kiniS; return c;")]}),
    ('(g) hari kuota selalu UTC−7 (reset 15.00 WIB sesudah 1 Nov terlewat)', {HB: [("export function hbMusimPanasAS(ms) { const y = new Date(ms).getUTCFullYear(); return ms >= hbMingguKe(y, 2, 2, 10) && ms < hbMingguKe(y, 10, 1, 9); }", "export function hbMusimPanasAS(ms) { return true; }")]}),
    ('(h) hitungan server tanpa mengurangi yang tersembunyi nisan', {HB: [("const lokal = (h.mentah || 0) - (h.tersembunyi || 0);", "const lokal = (h.mentah || 0);")]}),
    ('(i) siap (pil memuat lepas) dari simpanan KOSONG', {HB: [("if (st.dipercaya && !tahanSendiri(k)) { siapK(k); return; }", "if (!tahanSendiri(k)) { siapK(k); return; }")]}),
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
    ('(z) pendeteksi tidak menyentuh (ubahan Console tak pernah sampai ke perangkat lain)', {HB: [("kirimTemuan(k, 's', sentuh, lihat); kirimTemuan(k, 'n', r.nisan);", "kirimTemuan(k, 'n', r.nisan);")]}),
    # ---- tinjauan 7 Okt (penyanggah): tiap perbaikan wajib berbunyi karena SEBAB yang benar ----
    ('(T1) pendeteksi menyentuh nota HP kasir lama di koleksi yang DENGAR PENUH karena gerbang (tulisan ganda; kirim ulang HP v32 bertabrakan)', {HB: [("    if (G.gerbang.penuh[k] && t.baru.length) { tm.lewat = (tm.lewat || 0) + t.baru.length; t.baru = []; }\n", "")]}),
    ('(T2) cap data (tahun 2099) menggeser jam server perangkat (catatCap lama)', {HB: [("if (maks !== null) st.wdCalon = Math.max(st.wdCalon || 0, maks); tambahBaca(baru);",
        "if (maks !== null) { st.wdCalon = Math.max(st.wdCalon || 0, maks); if (G.skew !== null && jam() + G.skew < maks) G.skew = maks - jam(); } tambahBaca(baru);")]}),
    ('(T4) temuan pendeteksi yang gagal dikirim dibuang (tidak diulang)', {HB: [("        else if (tunda.indexOf(id) < 0) delete m[id];", "        else if (true) delete m[id];")]}),
    ('(T4) penyentuh mengembalikan { n: 0 } di tab yang tidak boleh menulis (temuan hilang)', {FB: [("  if (jagaTulisHemat()) return { n: 0, tunda: (ids || []).slice() };\n  const isi = ", "  if (jagaTulisHemat()) return { n: 0, tunda: [] };\n  const isi = ")]}),
    ('(T5) batas nisan dari cap tertinggi di data (Wt), bukan jam baca penuh terakhir', {HB: [("const Bn = hbBatasNisan(o.koleksi.map((k) => rk(k).totalPada), kiniS());", "const Bn = hbBatasNisan(o.koleksi.map((k) => rk(k).Wt), kiniS());")]}),
    ('(T5) jam baca penuh terakhir dari jam perangkat yang melompat (tanpa jepit gema terakhir) — Bn bisa di masa depan', {HB: [("totalPada: kiniSTercatat(), gen:", "totalPada: s, gen:")]}),
    ('(T6) catatan yang DIARSIPKAN tutup buku dianggap "hilang tanpa kabar" (batu nisan massal)', {HB: [("    if (bkBeda(k) && t.hilang.length) { tm.arsip = (tm.arsip || 0) + t.hilang.length; t.hilang = []; }\n", "")]}),
    ('(T7) umur denyut dari `pada` (jam perangkat penulis), bukan jam server saat terlihat berubah', {HB: [("const s = lihat ? hbAngka(lihat[String(p && p.id)]) : null;", "const s = null;")]}),
    # ---- audit P5 (8 Okt): hemat baca × arsip tutup buku — perangkat yang tertutup selama ritual tidak boleh menggambar catatan arsip + saldo pembuka sekaligus ----
    ('(P5a) rem kuota menahan baca penuh WAJIB karena tutup buku (angka DOBEL bertahan sampai reset kuota)', {HB: [("const rem = hbRem({ manual: !p.otomatis, otomatisK:", "const rem = hbRem({ manual: !p.otomatis && !p.wajib, otomatisK:")]}),
    ('(P5a) baca penuh karena tutup buku kembali "otomatis" di rencana', {HB: [("otomatis: false, wajib: true };", "otomatis: true };")]}),
    ('(P5a) baca penuh wajib yang gagal diulang di tiap kabar koleksi tetap (tanpa jeda 10 menit — seluruh koleksi dibaca berulang)', {HB: [("if ((p.otomatis || p.wajib) && st.fGagalPada && jam() - st.fGagalPada < 10 * hbMenit) {", "if (p.otomatis && st.fGagalPada && jam() - st.fGagalPada < 10 * hbMenit) {")]}),
    ('(P5b) pil memuat lepas walau koleksi ditahan tutup buku', {HB: [("if (st.dipercaya && !tahanSendiri(k)) { siapK(k); return; }", "if (st.dipercaya) { siapK(k); return; }")]}),
    ('(P5b) S dipasang walau koleksi ditahan tutup buku (saldo pembuka masuk simpanan & memori)', {HB: [("if (st.sLepas || G.berhenti || ditahan()) return;", "if (st.sLepas || G.berhenti) return;")]}),
    ('(P5b) memori tidak dibekukan selama ditahan (jawaban server tiba sebelum limbo → DOBEL)', {HB: [("    cekEpisode();\n    if (ditahan()) {\n", "    cekEpisode();\n    if (false) {\n")]}),
    ('(P5b) tulisan perangkat ini hilang dari memori yang dibekukan', {HB: [("catatTulis(k, id) { if (!K[k]) return; (K[k].milik = K[k].milik || {})[String(id)] = true; },", "catatTulis(k, id) { if (!K[k]) return; },")]}),
    ('(P5b) firebase.js tidak mencatat tulisan perangkat ini ke sesi hemat', {FB: [("    if (_hemat) _hemat.catatTulis(x.koleksi, d.id);\n", "")]}),
    ('(P5b) perbaruiBerkas tidak mencatat ubahan kolom perangkat ini (memori beku tidak menampilkannya)', {FB: [("pasangCap(x.koleksi, x.kolom)); if (_hemat) _hemat.catatTulis(x.koleksi, x.id); });", "pasangCap(x.koleksi, x.kolom)); });")]}),
    ('(P5b) kelengkapan menyebut "ubahan terbaru" padahal baca penuh sedang berjalan (koleksi yang ditahan belum memasang S)', {HB: [(
        "  if (x.fJalan) return P('sedang dibaca penuh — tunggu sampai selesai');\n  if (!x.sTerkini) return P('belum dicocokkan dengan ubahan terbaru di server — tunggu sebentar');\n",
        "  if (!x.sTerkini) return P('belum dicocokkan dengan ubahan terbaru di server — tunggu sebentar');\n  if (x.fJalan) return P('sedang dibaca penuh — tunggu sampai selesai');\n")]}),
    ('(P5b) baca penuh wajib yang gagal tidak menyebut sebabnya (koleksi ditahan tampak "tunggu sebentar")', {HB: [("if (st.rencana && st.rencana.wajib && st.mode !== 'penuh') { st.mode = 'delta';", "if (false) { st.mode = 'delta';")]}),
    ('(P5c) berita acara dari SIMPANAN dianggap jawaban server (tutup buku basi tampak tidak berubah)', {HB: [("if ('acaraServer' in x) G.acaraSrv = x.acaraServer === true;", "if ('acaraServer' in x) G.acaraSrv = true;")]}),
    ('(P5c) firebase.js menyebut berita acara selalu dari server', {FB: [("acaraServer: _dariCache.tutupBukuAcara === false });", "acaraServer: true });")]}),
    ('(P5d) simpanan BERCAMPUR (baca penuh sesudah tutup buku terputus) dipakai sebagai dasar memori', {HB: [("campurAwal: !!(R.k[k] && R.k[k].bkCampur) };", "campurAwal: false };")]}),
    ('(P5d) tanda bercampur tidak pernah dibuang sesudah baca penuh selesai', {HB: [("if (!G.bkAktif) { delete r.bkCampur; st.campurAwal = false; }", "if (!G.bkAktif) { st.campurAwal = false; }")]}),
    ('(P5d) simpanan dianggap bercampur sepanjang sesi (tombol baca penuh berikutnya mengosongkan memori lagi)', {HB: [("if (!G.bkAktif) { delete r.bkCampur; st.campurAwal = false; }", "if (!G.bkAktif) { delete r.bkCampur; }")]}),
    ('(P5e) perangkat yang MENJALANKAN ritual (dengar penuh) ikut dibekukan — memorinya dobel di tengah ritual', {HB: [("!fBeres(st) && (st.mode !== 'penuh' || !G.bkAktif) && tbBeda(k);", "!fBeres(st) && tbBeda(k);")]}),
    ('(P5f) tanpa internet pil memuat menggantung selagi ditahan tutup buku', {HB: [("    if (G.online && !diam) return;\n    siapK(k);\n", "    if (G.online && !diam) return;\n    if (!G.online) return;\n    siapK(k);\n")]}),
    # sanggahan P5 (8 Okt): baris pelepas memori beku & pil memuat yang dulu tidak dijaga uji apa pun, Mac ritual dibuka ulang, dengar penuh karena penulis tanpa cap,
    # server diam (kuota baca habis) — tiap baris wajib berbunyi
    ('(P5b) selesaiF tidak melepas memori beku (uang-kritis lolos di atas angka sebelum ritual)', {HB: [("    simpan(); nilaiTahanSemua(false);\n    if (G.klaimSaya) cekKlaimSelesai();", "    simpan();\n    if (G.klaimSaya) cekKlaimSelesai();")]}),
    ('(P5b) pelepas serentak tidak memasok ulang memori (berita acara terjawab / berganti, semua selesai)', {HB: [("if (h ? (!st.beku || st.bekuKosong !== sembunyi()) : !!st.beku) pasokK(k);", "if (h && !st.beku) pasokK(k);")]}),
    ('(P5b) catatan yang dihapus perangkat ini sendiri tetap tampil di memori beku', {HB: [("      Object.keys(hapus).forEach((id) => { delete isi[id]; });\n", "")]}),
    ('(P5d) simpanan bercampur selalu kosong walau berita acara menyebut tutup buku berjalan (Mac ritual dibuka ulang: sisa arsip terbaca habis)', {HB: [("const sembunyi = () => !!G.sembunyiEp && !ikutRitual();", "const sembunyi = () => !!G.sembunyiEp;")]}),
    ('(P5d) memori beku tidak ditentukan ulang saat berita acara berganti (server: ritual sudah selesai → catatan 2026 + saldo pembuka tetap tampil)', {HB: [("if (!st.beku || st.bekuKosong !== kosong) {", "if (!st.beku) {")]}),
    ('(P5e) dengar penuh karena penulis tanpa cap dikecualikan dari tahan (perangkat tertutup selama ritual DOBEL selama limbo)', {HB: [("!fBeres(st) && (st.mode !== 'penuh' || !G.bkAktif) && tbBeda(k);", "!fBeres(st) && st.mode !== 'penuh' && tbBeda(k);")]}),
    ('(P5e) dengar penuh terkini tidak mengakhiri tahan (memori tertinggal beku padahal uang-kritis menganggapnya segar)', {HB: [("const fBeres = (st) => !!st.fSelesai || (st.mode === 'penuh' && !!st.fTerkini);", "const fBeres = (st) => !!st.fSelesai;")]}),
    ('(P5e) dengar penuh menjadi terkini tidak melepas penahanan (menunggu hitungan / kabar simpanan berikutnya)', {HB: [("    if (!tadi) nilaiTahanSemua(false);\n", "")]}),
    ('(P5f) putus internet di tengah baca penuh wajib: pil memuat menggantung', {HB: [("    o.koleksi.forEach(nilaiSiap); o.koleksi.forEach((k) => nilaiPeriksa(k, true)); o.keluar.berubah();", "    o.koleksi.forEach((k) => nilaiPeriksa(k, true)); o.keluar.berubah();")]}),
    ('(P5f) server diam (kuota baca habis): pil memuat menggantung sampai reset', {HB: [("const diam = serverDiam() && st.dipercaya;", "const diam = false;")]}),
    ('(P5f) server diam: jadwal 30 detik tidak menandai apa pun', {HB: [("G.serverDiam = true; o.koleksi.forEach(nilaiSiap);", "o.koleksi.forEach(nilaiSiap);")]}),
    ('(P5f) server diam: kelengkapan berbunyi "tunggu sebentar"', {HB: [("serverDiam: serverDiam() && h, tidakDipercaya:", "serverDiam: false, tidakDipercaya:")]}),
    ('(P5f) server diam: uang-kritis berbunyi "tunggu sebentar"', {HB: [("      if (serverDiam()) return Promise.resolve(", "      if (false) return Promise.resolve(")]}),
    ('(P5f) server diam: kabar "server belum menjawab" tertinggal sesudah server menjawab', {HB: [("if (serverDiam() && h) return kurang ? HB_KABAR_DIAM_KOSONG : HB_KABAR_SERVER_DIAM;", "if (G.serverDiam) return kurang ? HB_KABAR_DIAM_KOSONG : HB_KABAR_SERVER_DIAM;")]}),
    # ---- sanggahan kedua P5 (8 Okt): memori satu-satunya pelindung (tidak ada tirai yang menutup layar) — tiap baris wajib berbunyi di kasusnya sendiri ----
    ('(P5g) penghalang dilepas begitu SATU koleksi selesai, bukan yang terakhir — stok terpotong dua kali (saldo pembuka − penjualan 2026 yang sudah diarsip)', {HB: [
        ("const ditahan = () => !G.bkServer || o.koleksi.some(tahanTb);", "const ditahan = () => !G.bkServer || o.koleksi.every(tahanTb);")]}),
    ('(P5g) koleksi yang hanya menunggu penghalang bersama dianggap lengkap (memori beku tapi terperiksa)', {HB: [("tahanTb(k) ? '' : HB_SEBAB_TUNGGU_LAIN });", "tahanTb(k) ? '' : '' });")]}),
    ('(P5g) uang-kritis lolos selagi memori beku (dengar ubahan & hitungan cocok dianggap segar)', {HB: [("      if (ditahan() && !G.berhenti && !o.koleksi.some((k) => K[k].vMati)) {", "      if (false) {")]}),
    ('(P5h) server berhenti menjawab tidak membekukan memori ("sekali dijawab, tetap dijawab")', {HB: [
        ("      G.bkServer = G.acaraSrv && G.online;\n", "      G.bkServer = G.bkServer || (G.acaraSrv && G.online);\n"), ("const srvLama = G.bkServer; G.bkServer = G.acaraSrv && G.online;", "const srvLama = G.bkServer; G.bkServer = G.bkServer || (G.acaraSrv && G.online);")]}),
    ('(P5h) penahanan yang mulai di tengah sesi tidak dibekukan SAAT ITU (beku malas di kabar simpanan berikutnya)', {HB: [
        ("    if (h) o.koleksi.forEach((k) => { const st = K[k]; if (st && st.vAda && !st.beku && st.lepasPernah) mulaiTahanTengah(k, aman); });\n", "")]}),
    ('(P5h) berita acara berganti selagi S menempel: simpanan dipakai sebagai memori beku (catatan 2026 + saldo pembuka = DOBEL)', {HB: [("K[k].lepasPernah = false; if (!aman || G.bkAktif) tandaiCampur(k); }", "K[k].lepasPernah = false; }")]}),
    ('(P5h) putus dianggap tidak aman (tiap putus memori disembunyikan, bukan keadaan terakhir yang dijawab server)', {HB: [("K[k].lepasPernah = false; if (!aman || G.bkAktif) tandaiCampur(k); }", "K[k].lepasPernah = false; tandaiCampur(k); }")]}),
    ('(P5i) pengecualian "tutup buku berjalan" untuk SEMUA perangkat (perangkat lain DOBEL saat server diam / tanpa internet)', {HB: [("const ikutRitual = () => G.bkAktif && (G.bkServer || pemegangIni());", "const ikutRitual = () => G.bkAktif;")]}),
    ('(P5i) pemegang ritual tidak dikenali (Mac pemegang dibuka ulang: sisa arsip kosong)', {HB: [("a.pemegang && String(a.pemegang.id) === String(o.idPerangkat));", "false);")]}),
    ('(P5j) kabar "disembunyikan" tidak didahulukan (memori kosong mengaku "angka dari simpanan perangkat")', {HB: [("    if (h && sembunyi()) return HB_KABAR_SEMBUNYI + ' — ' + petunjukTahan();\n", "")]}),
    ('(P5j) kelengkapan "disembunyikan" tidak didahulukan', {HB: [("  if (x.sembunyi) return { jenis: 'periksa', sebab: String(x.sembunyi) };\n", "")]}),
    ('(P5j) bercampur ditandai saat baca penuh dipasang (F macet sebelum membawa apa pun → muat ulang kosong)', {HB: [("    if (G.bkAktif && !rk(k).bkCampur) { rk(k).bkCampur = 1; simpan(); }", "    if ((G.bkAktif || tbBeda(k)) && !rk(k).bkCampur) { rk(k).bkCampur = 1; simpan(); }")]}),
    ('(P5j) simpanan yang berubah selama ditahan tidak menandai bercampur (muat ulang di tengah limbo = DOBEL)', {HB: [("    if (st.ubahTahan && (tbBeda(k) || G.bkAktif) && !rk(k).bkCampur) { rk(k).bkCampur = 1; simpan(); }", "    if (false) { rk(k).bkCampur = 1; simpan(); }")]}),
    ('(P5k) jenis catatan beda zaman (ditutup di tengah penghalang) tidak disembunyikan — campuran sesudah/sebelum ritual', {HB: [("G.sembunyiEp = eraBeda() || o.koleksi.some(", "G.sembunyiEp = o.koleksi.some(")]}),
    ('(P5k) disembunyikan dinilai ulang di tengah penahanan (koleksi yang selesai lebih dulu membuat semua kosong / campuran)', {HB: [("const sembunyi = () => !!G.sembunyiEp && !ikutRitual();", "const sembunyi = () => (eraBeda() || o.koleksi.some((k) => !!K[k].campurAwal)) && !ikutRitual();")]}),
    ('(M31) firebase.js: acaraServer dari snapshot koleksi tetap mana pun yang sedang dikabarkan, bukan pendengar berita acara', {FB: [("kabariTetap(k.nama, snap, tunda);", "kabariTetap(k.nama, snap, tunda, !(snap.metadata && snap.metadata.fromCache));"),
        ("function kabariTetap(nama, snap, tunda) {", "function kabariTetap(nama, snap, tunda, dariServerIni) {"), ("acaraServer: _dariCache.tutupBukuAcara === false });", "acaraServer: !!dariServerIni });")]}),
    ('(M14) server diam: siap walau simpanan tidak dipercaya (memori kosong tanpa pil memuat)', {HB: [("const diam = serverDiam() && st.dipercaya;", "const diam = serverDiam();")]}),
    ('(M14) server diam + simpanan tidak dipercaya: kelengkapan mengaku "angka dari simpanan perangkat ini"', {HB: [("return P(x.tidakDipercaya ? hbSebabDiamKosong(x.tidakDipercaya) : HB_SEBAB_SERVER_DIAM);", "return P(HB_SEBAB_SERVER_DIAM);")]}),
    ('(M20) pil memuat lepas sesudah 30 detik server diam tanpa mengabari layar (layar tetap "memuat")', {HB: [("G.serverDiam = true; o.koleksi.forEach(nilaiSiap); o.koleksi.forEach(nilaiPeriksa); }", "G.serverDiam = true; o.koleksi.forEach(nilaiSiap); }")]}),
    ('(P5l) tersambung lagi: tanda "server diam" dari masa tanpa internet menempel (sebab menyesatkan)', {HB: [("if (ya) { G.serverDiam = false; mulaiTunggu();", "if (ya) {")]}),
    ('(P5l) kabar "Tanpa internet: tutup buku berubah" tertinggal sesudah tersambung & selesai', {HB: [("if (!G.online && h && ada.some(tbBeda)) return", "if (ada.some((k) => !!rk(k).bk)) return")]}),
    ('(statis) daftar siap-nyala saat nyala membaca peta samping pendengar penuh (_cap) — semua catatan hemat "tanpa cap"', {FB: [("const c = (_hemat ? _hemat.capPeta(nama) : _cap[nama]) || {};", "const c = _cap[nama] || {};")]}),
    ('(kasir) nota yang :commit-nya ditolak langsung dinyatakan ditolak (tanpa cara lama — kirim ulang di rules v6 / v3 jadi "ditolak", omzet dobel)', {KD: [("          if (bercap) { kirimItem(item, false, true); return; }   // :commit ditolak → cara lama sekali (lihat kirimItem), baru dinyatakan ditolak\n", "")]}),
    ('(kasir) cara lama tanpa updateMask (PATCH utuh membuang capServer kiriman pertama → v6 menolak)', {KD: [("+ (caraLama ? kolomLama(fields) : '')", "+ ''")]}),
    ('(z) baca penuh harian per PERANGKAT diam-diam berhenti (klaim tidak pernah ditulis)', {HB: [("if (k.hari !== hari) return { klaim: true, hari, sebab:", "if (false) return { klaim: true, hari, sebab:")]}),
    # ---- #111 × Paket C (7 Okt): SATU sumber kelengkapan — tiap kerusakan wajib berbunyi karena sebab yang benar ----
    ('(K1) kelengkapan mengabaikan "belum dibaca penuh hari ini" (hitungan cocok dianggap lengkap)', {HB: [("  if (hbAngka(x.totalPada) > 0 && hbHariKuota(x.totalPada) === x.hari) return null;\n", "  return null;\n")]}),
    ('(K2) baca penuh harian toko yang BELUM selesai dianggap selesai', {HB: [("const k = x.klaim || {}; const tokoHariIni = k.hari === x.hari && !!k.selesai;", "const k = x.klaim || {}; const tokoHariIni = k.hari === x.hari;")]}),
    ('(K3) baca penuh perangkat ini dari hari kuota mana pun dianggap "hari ini"', {HB: [("if (hbAngka(x.totalPada) > 0 && hbHariKuota(x.totalPada) === x.hari) return null;", "if (hbAngka(x.totalPada) > 0) return null;")]}),
    # sanggahan 7 Okt: dulu (K4) merusak dengan `|| fSelesai` dan berbunyi di B9 (pendengar simpanan mati) — kini HANYA tanpa internet, berbunyi di kasus K4 (B11)
    ('(K4) terperiksa menyimpang dari sumber kelengkapan (baca penuh sesi ini = terperiksa walau tanpa internet)', {HB: [("function terperiksaK(k) { const b = belumK(k); return !b || b.jenis !== 'periksa'; }", "function terperiksaK(k) { const b = belumK(k); return !b || b.jenis !== 'periksa' || (!G.online && !!K[k].fSelesai); }")]}),
    ('(K5) dengar penuh tidak dianggap lengkap (koleksi yang didengar penuh ikut "belum dibaca penuh hari ini")', {HB: [("if (x.mode === 'penuh') return x.fTerkini && (x.fSelesai || x.fMode === 'penuh') ? (x.tertahan ? P(x.tertahan) : null) : P(", "if (x.mode === 'penuh' && !(x.fTerkini && (x.fSelesai || x.fMode === 'penuh'))) return P(")]}),
    ('(K6) keadaan() tidak membawa kelengkapan (layar tidak pernah melihatnya)', {HB: [(", belumLengkap: sesi.belumLengkap() };", " };")]}),
    ('(K7) sebab rem kuota disamaratakan jadi "tunggu sebentar" (owner menunggu selamanya)', {HB: [("'perlu dibaca penuh, tapi ditunda supaya kuota baca hari ini tidak habis — ' + HB_KE_MENU", "'belum dicocokkan dengan server — tunggu sebentar'")]}),
    # ---- sanggahan 7 Okt (adversarial adc85b3): tiap perbaikan berbunyi di kasusnya sendiri ----
    ('(K8) tab yang KALAH kunci tab tetap melapor lengkap (belumK tidak tahu sesi berhenti)', {HB: [("vMati: st.vMati, berhenti: G.berhenti, vAda:", "vMati: st.vMati, vAda:")]}),
    ('(K9) baca penuh harian toko "selesai" tanpa menunggu antrean temuan (perangkat lain lengkap padahal ubahan Console belum sampai)', {HB: [("    if (antreTemuan()) { G.klaimKabar =", "    if (false) { G.klaimKabar =")]}),
    ('(K10) temuanTunda baca penuh harian toko diabaikan (klaim selesai = lengkap)', {HB: [("  if (tokoHariIni && !(tunda > 0)) return null;", "  if (tokoHariIni) return null;")]}),
    ('(K11) sesi hemat mengabaikan `lewat` penyentuh (bulan terkunci dibuang diam-diam)', {HB: [("const lewat = (h && h.lewat) || [];", "const lewat = [];")]}),
    ('(K11) firebase.js sentuhCap membuang catatan bulan terkunci diam-diam (tidak dilaporkan)', {FB: [("if (tolakKunci(koleksi, d)) { lewat.push(id); return false; }", "if (tolakKunci(koleksi, d)) return false;")]}),
    ('(K12) sebab SATU jenis catatan dipinjamkan ke semua (owner menunggu padahal yang lain butuh ketukan)', {HB: [("const utama = ks.filter((k) => teks(k) === sebab); const lain = ks.filter((k) => teks(k) !== sebab);", "const utama = ks; const lain = [];")]}),
    ('(K13) "belum dibaca penuh hari ini" padahal yang dihitung hari KUOTA (jam reset tidak disebut)', {HB: [("return 'belum dibaca penuh sejak kuota baca direset' + (j ? ' pukul ' + j + ' WIB' : '') + ' — ' + HB_KE_MENU; }", "return 'belum dibaca penuh hari ini — ' + HB_KE_MENU; }")]}),
    ('(K14) kuota baca habis (429) disamaratakan "dicoba lagi sebentar / ketuk sekarang"', {HB: [("  const habis = /resource-exhausted/.test(", "  const habis = false && /resource-exhausted/.test(")]}),
    ('(K15) jumlah jenis catatan menempel di belakang kurung menu (kurung ganda)', {HB: [("return 'data perangkat ini ' + (B.koleksi.length > 1 ? hbSisipJumlah(B.sebab, B.utama.length) : B.sebab) + hbEkorLain(B);", "return 'data perangkat ini ' + B.sebab + (B.koleksi.length > 1 ? ' (' + B.utama.length + ' jenis catatan)' : '') + hbEkorLain(B);")]}),
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
