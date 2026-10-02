#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_kinerja_gerak.py — PUTARAN 33 (owner 29 Sep 2026): gerbang masuk G4, kinerja (lag pindah layar, freeze saat refresh/buka), gerak.
  · PRELOAD: tiap modul yang terjangkau dari baru/js/app.js ada di <link rel="modulepreload"> index.html, dan sebaliknya (satu kebenaran:
    graf impor; daftar lama = muat berlapis ±8 bolak-balik jaringan di HP).
  · JADWAL (jsc, jam palsu): permintaan gambar yang sama digabung SEKALI per bingkai; masa muat dijarangkan (±320 ms); selesai muat → langsung.
  · SAMBUNGAN: bunyi data (dengarkan) di KEDELAPAN layar & bunyi status di app.js lewat nanti(); Jual tidak digambar saat tersembunyi dan
    pindah() memberi tahu Jual; ketukan pemakai (K.dengar) tetap seketika.
  · GERBANG: ID formulir putaran 23 utuh (app.js & uji_layar_kunci membacanya); 'tampil' dicabut SEKETIKA saat membuka (gerak di kelas lain);
    tanpa angka rupiah; semua gerak berulang berhenti saat "kurangi gerakan".
  · PENUTUP OMZET: Hari ini ditahan selama adegan, adeganNota mengembalikan lamanya, penjaga waktu melepas angka walau tab disembunyikan.
  · TUMPUKAN RAK JUAL (jsc, gambarChipBarang): rangka SVG karung & kemasan sama di semua tingkat sisa (morf mempertahankan elemen →
    transisi lapis berjalan); selalu TUMPUK_N lapis, yang tampak mengikuti tabel & tidak pernah melebihi sisa; urutan pergi dari --j.

    python3 alat-uji/uji_kinerja_gerak.py                 → N lulus · 0 gagal
    python3 alat-uji/uji_kinerja_gerak.py --kontrol       → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
    python3 alat-uji/uji_kinerja_gerak.py --pasang-preload → tulis ulang daftar modulepreload dari graf impor
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
LAYAR = ['harga', 'laporan', 'menu', 'pelanggan', 'uang', 'stok', 'ringkasan', 'jual']
ID_MASUK = ['modalMasuk', 'formMasuk', 'pesanMasuk', 'isianEmail', 'ingatEmail', 'lupakanEmail', 'isianSandi', 'salahMasuk', 'tombolMasuk',
            'panelAkun', 'judulAkun', 'pesanAkun', 'mintaAkun', 'isianNamaAkun', 'tombolMinta', 'hasilAkun', 'tombolKeluarAkun']


def graf_impor(teks_berkas):
    lihat, antre, luar = [], ['baru/js/app.js'], set()
    while antre:
        f = antre.pop(0)
        if f in lihat: continue
        lihat.append(f)
        for m in re.findall(r"^\s*import\s[^;]*?from\s+['\"]([^'\"]+)['\"]", teks_berkas(f), flags=re.M | re.S):
            if m.startswith('http'): luar.add(m); continue
            antre.append(os.path.normpath(os.path.join(os.path.dirname(f), m)))
    return [os.path.relpath(f, 'baru') for f in lihat], sorted(luar)


def baca(ganti=None):
    t = {}
    def teks(b):
        if b not in t: t[b] = open(os.path.join(AKAR, b), encoding='utf-8').read()
        return t[b]
    for b in ['baru/index.html', 'baru/js/app.js', 'baru/js/inti/jadwal.js', 'baru/js/inti/gerbang.js', 'baru/js/inti/gerak.js', 'baru/css/gerbang.css', 'baru/css/gerak.css',
              'baru/js/layar/gambar.js', 'baru/css/jual.css'] + ['baru/js/layar/%s.js' % n for n in LAYAR]:
        teks(b)
    for b, pasangan in (ganti or {}).items():
        teks(b)
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t, teks


JADWAL_UJI = r"""
var __jam = 0, __timer = [], __raf = [], __nomor = 1; var document = { hidden: false };
function setTimeout(f, ms) { __timer.push({ id: __nomor++, at: __jam + (ms || 0), f: f }); return __nomor; }
function requestAnimationFrame(f) { __raf.push(f); return 1; }
function bingkai() { var r = __raf; __raf = []; __jam += 16; r.forEach(function (f) { f(__jam); }); jalanTimer(); }
function jalanTimer() { __timer.sort(function (a, b) { return a.at - b.at; }); while (__timer.length && __timer[0].at <= __jam) { var t = __timer.shift(); t.f(); } }
function maju(ms) { __jam += ms; jalanTimer(); }
var console = { error: function () {} };
""" + '%JADWAL%' + r"""
var hasil = {};
var n = 0; var gambar = function () { n += 1; };
for (var i = 0; i < 108; i++) nanti(gambar);
bingkai(); hasil.satuBingkai = n; maju(500); hasil.sesudahPenjaga = n;
n = 0; setelMuat(true); for (var i = 0; i < 20; i++) nanti(gambar); bingkai(); hasil.muatBingkai = n; maju(84); hasil.muat100 = n; maju(300); hasil.muat400 = n;
n = 0; for (var i = 0; i < 5; i++) nanti(gambar); setelMuat(false); hasil.selesaiMuat = n;
n = 0; var m = 0; var lain = function () { m += 1; }; nanti(gambar); nanti(lain); nanti(gambar); bingkai(); hasil.dua = [n, m];
document.hidden = true; n = 0; nanti(gambar); maju(1); hasil.tersembunyi = n; document.hidden = false;
n = 0; m = 0; setelMuat(true); nanti(lain); segera(gambar); bingkai(); hasil.segeraMuat = [n, m]; maju(400); hasil.segeraMuatSesudah = [n, m]; setelMuat(false);
print(JSON.stringify(hasil));
"""

# Tumpukan rak Jual: gambarChipBarang untuk karung 50 kg & kemasan 5 kg di beberapa sisa. Dua rak: terbanyak 40 (skala akar membedakan
# sisa 14 dari sisa 3) dan terbanyak 4 (skala akar memberi lebih banyak lapis daripada barangnya — harus dijepit ke sisa).
TUMPUK_SISA = {40: [40, 14, 3, 1, 0], 4: [4, 3, 2, 1, 0]}
TUMPUK_TABEL = {40: {40: 6, 14: 4, 3: 2, 1: 1, 0: 0}, 4: {4: 4, 3: 3, 2: 2, 1: 1, 0: 0}}
TUMPUK_UJI = r"""
var SISA = %SISA%; var H = { karung: [], kemasan: [], papan: {} };
[40, 4].forEach(function (penuh) {
  SISA[penuh].forEach(function (sisa) {
    H.karung.push({ penuh: penuh, sisa: sisa, svg: gambarChipBarang({ jalur: 'karung', kunci: 'IR64', berat: 50, sisa: sisa }, penuh) });
    H.kemasan.push({ penuh: penuh, sisa: sisa, svg: gambarChipBarang({ jalur: 'kemasan', kunci: 'IR64', ukuranKg: 5, sisa: sisa }, penuh) });
  });
});
['5', '2.5', '0.25'].forEach(function (u) { H.papan[u] = gambarChipBarang({ jalur: 'kemasan', kunci: 'Pandan', ukuranKg: Number(u), sisa: 3 }, 9); });
print(JSON.stringify(H));
"""


def periksa(t, teks):
    out = []; ok = lambda n, c, k='': out.append((n, bool(c), k))
    html = t['baru/index.html']; app = t['baru/js/app.js']; gcss = t['baru/css/gerbang.css']; gjs = t['baru/js/inti/gerbang.js']; jl = t['baru/js/layar/jual.js']
    # --- preload = graf impor
    lokal, luar = graf_impor(teks)
    ada = re.findall(r'<link rel="modulepreload" href="([^"]+)">', html)
    kurang = [m for m in lokal + luar if m not in ada]; lebih = [m for m in ada if m not in lokal + luar]
    ok('preload: tiap modul yang terjangkau dari app.js dipramuat (%d modul)' % len(lokal + luar), not kurang, 'kurang: ' + ', '.join(kurang))
    ok('preload: tidak ada modul yatim / salah nama di daftar', not lebih, 'lebih: ' + ', '.join(lebih))
    ok('preload: preconnect ke gstatic & firestore', 'rel="preconnect" href="https://www.gstatic.com"' in html and 'rel="preconnect" href="https://firestore.googleapis.com"' in html)
    # --- jadwal di jsc
    jadwal = re.sub(r'^export\s+', '', t['baru/js/inti/jadwal.js'], flags=re.M)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(JADWAL_UJI.replace('%JADWAL%', jadwal)); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True); os.unlink(p)
    try: h = json.loads((r.stdout or '').strip().split('\n')[-1])
    except Exception: h = None
    ok('jadwal jsc jalan', h is not None, (r.stderr or r.stdout)[-400:])
    if h:
        ok('jadwal: 108 permintaan gambar yang sama → SEKALI di bingkai berikutnya (dulu 108 gambar ulang)', h['satuBingkai'] == 1, h)
        ok('jadwal: penjaga setTimeout tidak menggambar DUA kali sesudah bingkai', h['sesudahPenjaga'] == 1, h)
        ok('jadwal: masa muat → TIDAK di bingkai berikutnya, belum di 100 ms, sekali di ±320 ms', h['muatBingkai'] == 0 and h['muat100'] == 0 and h['muat400'] == 1, h)
        ok('jadwal: selesai muat → yang menunggu langsung digambar', h['selesaiMuat'] == 1, h)
        ok('jadwal: dua fungsi berbeda di satu bingkai → masing-masing sekali', h['dua'] == [1, 1], h)
        ok('jadwal: tab tersembunyi (rAF beku) → tetap digambar lewat setTimeout', h['tersembunyi'] == 1, h)
        ok('jadwal: ketukan (segera) di masa muat → tergambar di bingkai BERIKUTNYA, antrean data ikut sekali, tanpa ganda sesudahnya', h['segeraMuat'] == [1, 1] and h['segeraMuatSesudah'] == [1, 1], h)
    # --- tumpukan rak Jual (gambar.js di jsc lewat bundel)
    gb = t['baru/js/layar/gambar.js']; jcss = t['baru/css/jual.css']
    mN = re.search(r'^const TUMPUK_N = (\d+);', gb, flags=re.M); N = int(mN.group(1)) if mN else -1
    drv = bundel_baru.polos(gb) + TUMPUK_UJI.replace('%SISA%', json.dumps({str(k): v for k, v in TUMPUK_SISA.items()}))
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(drv); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True); os.unlink(p)
    try: G = json.loads((r.stdout or '').strip().split('\n')[-1])
    except Exception: G = None
    ok('tumpukan: gambar.js jalan di jsc (TUMPUK_N = %d)' % N, G is not None and N > 0, (r.stderr or r.stdout)[-400:])
    if G:
        for jalur in ('karung', 'kemasan'):
            rangka = [re.sub(r'\s(?:class|style)="[^"]*"', '', x['svg']) for x in G[jalur]]
            beda = [('%d/%d' % (x['sisa'], x['penuh'])) for x, rk in zip(G[jalur], rangka) if rk != rangka[0]]
            ok('tumpukan %s: rangka SVG tanpa class/style SAMA di semua tingkat sisa (morf mempertahankan elemen → lapis bertransisi, bukan diganti)' % jalur, not beda, 'beda: ' + ', '.join(beda))
            hitung = [(x['penuh'], x['sisa'], len(re.findall(r'class="lapis[" ]', x['svg'])), len(re.findall(r'class="lapis"', x['svg'])), 'tumpuk-habis' in x['svg'].split('>')[0]) for x in G[jalur]]
            ok('tumpukan %s: selalu %d lapis di DOM (yang tidak tampak = .pergi)' % (jalur, N), all(h[2] == N for h in hitung), hitung)
            ok('tumpukan %s: lapis tampak sesuai tabel (rak 40: 40→6 · 14→4 · 3→2 · 1→1 · 0→0; rak 4: 4→4 · 3→3 · 2→2 · 1→1 · 0→0)' % jalur,
               all(h[3] == TUMPUK_TABEL[h[0]][h[1]] for h in hitung), hitung)
            ok('tumpukan %s: lapis tampak tidak pernah melebihi sisa; sisa 1 → satu lapis' % jalur, all(h[3] <= h[1] for h in hitung) and all(h[3] == 1 for h in hitung if h[1] == 1), hitung)
            ok('tumpukan %s: habis → nol lapis + kelas tumpuk-habis; masih ada → tanpa tumpuk-habis' % jalur, all((h[3] == 0 and h[4]) if h[1] == 0 else (h[3] > 0 and not h[4]) for h in hitung), hitung)
            urut = re.findall(r'style="--i: (\d+); --j: (\d+);"', G[jalur][0]['svg'])
            ok('tumpukan %s: tiap lapis membawa --i naik & --j = TUMPUK_N − 1 − i' % jalur, len(urut) == N and all(int(a) == i and int(b) == N - 1 - i for i, (a, b) in enumerate(urut)), urut)
        ok('tumpukan papan: huruf tiga tingkat ("5" biasa, "2,5" tiga-huruf, "0,25" empat-huruf)', 'class="ukuran">5<' in G['papan']['5'] and 'class="ukuran tiga-huruf">2,5<' in G['papan']['2.5'] and 'class="ukuran empat-huruf">0,25<' in G['papan']['0.25'],
           [re.search(r'<text[^>]*>[^<]*<', G['papan'][u]).group(0) for u in ('5', '2.5', '0.25')])
    ok('tumpukan css: yang pergi berurutan dari --j kiriman JS (bukan salinan angka TUMPUK_N − 1 di CSS)', '.gb.tumpuk .lapis.pergi { opacity: 0; transform: translateY(-9px); transition-delay: calc(var(--j, 0) * 45ms); }' in jcss and not re.search(r'calc\(\(\d+ - var\(--i', jcss))
    # --- sambungan ke layar
    for n in LAYAR:
        s = t['baru/js/layar/%s.js' % n]
        pend = re.findall(r'dengarkan\(\(\) => \{?([^;]*;?[^;]*;?)', s)
        ok('%s: bunyi data lewat nanti() (bukan gambar langsung)' % n, "from '../inti/jadwal.js'" in s and pend and all('nanti(' in x for x in pend) and not re.search(r'dengarkan\(\(\) => gambar\(\)\)', s), pend)
    ok('jual: tersembunyi → cukup ditandai kotor, digambar saat dibuka', "if (!_tampil) { _kotor = true; return; }" in jl and 'tampilkan, belumDisimpan' in jl)
    ok('jual: ketukan pemakai tetap seketika (K.dengar menggambar langsung)', "K.dengar(() => { gambar(); gulirkan(akar, RP); });" in jl)
    ok('app: pindah() memberi tahu Jual kapan terlihat', "layar.tampilkan(tujuan === 'jual');" in app)
    ok('app: status sambungan mengantre fungsi gambar YANG SAMA dengan pendengar data (tanpa gambar ganda) lalu setelMuat', 'const GAMBAR_STATUS = [layar.gambarGulir, ringkasan.gambar, stok.gambar, pelanggan.gambar, menu.gambar, harga.gambar, uang.gambar, laporan.gambar];' in app
       and re.search(r"fb\.dengarkanStatus\(\(st\) => \{ statusFb = st; gambarChipDanNav\(\); GAMBAR_STATUS\.forEach\(nanti\); setelMuat\([^;]*\); \}\)", app) is not None and 'gambar: perbaruiData,' in t['baru/js/layar/ringkasan.js'])
    ok('app: tidak ada lagi gambar ulang SEMUA layar langsung di bunyi status', 'fb.dengarkanStatus((st) => { statusFb = st; gambarChipDanNav(); layar.gambar();' not in app)
    # --- gerak
    ok('gerak: layar datang dari arah tab (datangkan) & penanda meluncur (geserPenanda)', 'datangkan(LAYAR_ADA[tujuan], dari, tujuan); requestAnimationFrame(geserPenanda);' in app)
    ok('gerak: geser lewat Web Animations pada ANAK <main> (tanpa kelas CSS yang memutar ulang animasi dasar; elemen fixed dikecualikan)',
       "const DATANG_KECUALI = '.latar-bola, .jual-keranjang, .lembar, .tetes-terbang, input';" in app and "c.animate([{ opacity: 0, transform: 'translateX(' + geser + 'px)' }" in app and 'datang-kanan' not in t['baru/css/gerak.css'] and "classList.add(arah)" not in app)
    ok('gerak: gulirkan mulai dari angka LAMA & bertahan saat dimorf ulang di tengah gulir', 'if (el.__gulir && dari === ke) { el.textContent = format(el.__tampil); return; }' in t['baru/js/inti/gerak.js'] and 'el.__gulir = true; el.__tampil = awal; el.textContent = format(awal);' in t['baru/js/inti/gerak.js'])
    for n in ['stok', 'pelanggan', 'menu', 'harga', 'uang', 'laporan']:
        sx = t['baru/js/layar/%s.js' % n]
        ok('%s: dibuka lagi → digambar HANYA kalau kotor atau DOM-nya kosong (dikosongkan tirai), lewat segera' % n, 'if (!tampil || terkunci()) { _kotor = true; return; } _kotor = false;' in sx and 'if (tampil && (_kotor || !akar.firstElementChild)) segera(gambar); } }' in sx)
    ok('ringkasan: dibuka lewat segera (dulu ±80 ms menahan ketukan)', 'segera(perbaruiTampil); } },' in t['baru/js/layar/ringkasan.js'])
    ok('app: layar dimatikan HANYA saat mengunci (akses karyawan berubah saat bekerja tidak membekukan layar)', "if (kunci) { Object.keys(LAYAR_ADA).forEach((k) => { LAYAR_ADA[k].innerHTML = ''; }); SEMUA_LAYAR().forEach((l) => l.tampilkan(false));" in app and app.count('SEMUA_LAYAR().forEach((l) => l.tampilkan(false));') == 1)
    ok('tirai: lapisan uang di luar <main> dicabut saat mengunci & disembunyikan CSS', "['omzetPil', 'omzetToast', 'omzetNaik', 'koinOmzet', 'cincinOmzet', 'kilauOmzet', 'panggung'].forEach((id) => { const el = document.getElementById(id); if (el) el.remove(); });" in app
       and 'body.terkunci #panggung, body.terkunci .koin-omzet, body.terkunci .omzet-pil' in t['baru/css/gerak.css'])
    # --- gerbang
    for i in ID_MASUK: ok('gerbang: id="%s" tetap ada' % i, html.count('id="%s"' % i) == 1)
    blok = html[html.index('id="modalMasuk"'):html.index('<!-- putaran 23c: Keluar dengan keranjang')]
    ok('gerbang: tanpa angka rupiah', not re.search(r'Rp\s?\d', blok))
    ok('gerbang: kalimat sandi bahasa toko (owner 29 Sep)', 'Sandi tidak disimpan di perangkat ini — langsung dicek server, lalu dilupakan.' in blok and 'Firebase' not in blok.split('-->')[-1])
    ok('gerbang: membuka mencabut "tampil" SEKETIKA (layar sudah boleh diketuk), gerak di kelas "membuka" tanpa menghalangi ketukan',
       "g.classList.remove('tampil'); g.classList.add('membuka');" in gjs and '.gerbang-masuk.membuka { pointer-events: none; }' in gcss)
    ok('gerbang: app.js memanggil gerbang.akun di gambarAkun, mulai() sebelum Firebase', 'gerbang.akun(akun, bisa)' in app and 'gerbang.mulai();' in app and "modal.classList.toggle('tampil', !bisa);" not in app)
    ok('gerbang: sandi kosong → berdenyut (owner 29 Sep: boleh)', "if (!sandi) { gerbang.mintaSandi(); return; }" in app)
    ok('gerbang: "kurangi gerakan" menghentikan gerak berulang (iteration-count 1)', 'animation-iteration-count: 1 !important' in gcss)
    ok('gerbang: kata "Bapak" tidak dipakai', 'Bapak' not in blok)
    ok('gerbang: kelas getar dilepas di luar keadaan salah (tidak bergetar lagi sesudah Keluar)', "(t !== 'salah' && /^goyang[12]$/.test(c))" in gjs)
    ok('gerbang: sesi dipulihkan (cepat) → formulir tidak pernah tampil', '.gerbang-masuk.t-membuka.cepat .gm-pelat { visibility: hidden; animation: none; }' in gcss)
    ok('gerbang: fokus kolom ditunda sampai pintu selesai merapat', 'const tundaFokus = gerbang.akun(akun, bisa) || 0;' in app and 'focus(), tundaFokus + 50)' in app and 'return LAMA.tutup;' in gjs)
    ok('gerbang: HP mendatar pendek → cincin & kotak Masuk berdampingan (aturan di AKHIR berkas)', gcss.rstrip().endswith('.gm-padi, .gm-capung { display: none; } }') and '@media (orientation: landscape) and (max-height: 560px)' in gcss)
    # --- penutup omzet
    ok('penutup: Hari ini ditahan selama adegan', "const hari = _tahanHari && Date.now() < _tahanHari.sampai ? _tahanHari.hari : L.hariIni(s);" in jl)
    ok('penutup: adeganNota mengembalikan lama cerita', 'return lamaUang + 200 + lamaBarang;' in jl and 'return barang() ? lamaBarang : 0;' in jl)
    ok('penutup: penjaga waktu melepas angka walau animasi tak selesai', 'anim.onfinish = mendarat; setTimeout(mendarat, 1400);' in jl)
    ok('penutup: nota batal SEBELUM koin terbang → tidak dirayakan', "if (document.hidden || !(naikSungguh > 0)" in jl)
    ok('penutup: penahan dipasang SEBELUM menulis (snapshot lokal Firestore tidak menaikkan angka lebih dulu)', 0 <= jl.find("const token = ++_tokenPenutup; _tahanHari = { hari: hariTadi, sampai: Date.now() + 5000, token };") < jl.find("const h = await tulisDokumen(r.dokumen);\n        if (h && h.gagal) { lepasBila();"))
    ok('penutup: nota berdekatan → patokan terlama, hanya token terakhir yang melepas', "const hariTadi = _tahanHari && Date.now() < _tahanHari.sampai ? _tahanHari.hari : L.hariIni(S());" in jl and "if (!tahan || tahan.token !== token) return;" in jl and "if (!_tahanHari || _tahanHari.token !== token) {" in jl)
    ok('penutup: dihitung ULANG saat mendarat (batal selagi koin terbang → tanpa +Rp)', "const naik = L.hariIni(S()).omzet - tahan.hari.omzet;" in jl and "if (!(naik > 0)) return;" in jl)
    ok('penutup: terkunci (sudah Keluar) → berhenti, tidak menggambar apa pun', jl.count("if (terkunci()) { _tahanHari = null;") == 2)
    ok('penutup 39b-19: tanpa adegan (kurangi gerakan) yang dirayakan = kenaikan SUNGGUHAN Hari ini (nota tukar membawa retur), bukan Σ hargaTotal nota', "setTimeout(() => rayakanOmzet(L.hariIni(S()).omzet - hariTadi.omzet), 80);" in jl and 'rayakanOmzet(tambahOmzet)' not in jl)
    ok('penutup: lembar terbuka (Mac) → koin ke pil, bukan ke kartu yang tertutup', "const terlihat = !!r && r.width > 0 && r.top >= 0 && r.bottom <= innerHeight - 90 && !adaLembar;" in jl)
    return out


KONTROL = [
    ('preload hilang satu', {'baru/index.html': [('<link rel="modulepreload" href="js/inti/jadwal.js">\n', '')]}),
    ('jadwal tidak menggabung (gambar langsung)', {'baru/js/inti/jadwal.js': [('  _antre.add(f);\n  if (_menunggu) return;', '  f(); return;\n  if (_menunggu) return;')]}),
    ('masa muat tidak dijarangkan', {'baru/js/inti/jadwal.js': [('  if (_muat) { setTimeout(() => jalankan(t), JEDA_MUAT_MS); return; }\n', '')]}),
    ('stok kembali menggambar langsung', {'baru/js/layar/stok.js': [('dengarkan(() => nanti(gambar));', 'dengarkan(() => gambar());')]}),
    ('jual digambar walau tersembunyi', {'baru/js/layar/jual.js': [('    if (!_tampil) { _kotor = true; return; }\n', '')]}),
    ('id formulir diganti', {'baru/index.html': [('id="tombolMasuk"', 'id="tombolMasukBaru"')]}),
    ('tampil tertahan selama membuka', {'baru/js/inti/gerbang.js': [("g.classList.remove('tampil'); g.classList.add('membuka');", "g.classList.add('membuka');")]}),
    ('rupiah di gerbang', {'baru/index.html': [('<div class="label">Akun per orang</div>', '<div class="label">Rp5.000</div>')]}),
    ('penutup tanpa penjaga waktu', {'baru/js/layar/jual.js': [('anim.onfinish = mendarat; setTimeout(mendarat, 1400);', 'anim.onfinish = mendarat;')]}),
    ('segera ikut dijarangkan di masa muat', {'baru/js/inti/jadwal.js': [('  if (_menunggu && !_muat) return;   // bingkai berikutnya sudah dijadwalkan\n', '  if (_muat) { nanti(f); return; }\n  if (_menunggu) return;\n')]}),
    ('penahan dipasang sesudah menulis lagi', {'baru/js/layar/jual.js': [("const token = ++_tokenPenutup; _tahanHari = { hari: hariTadi, sampai: Date.now() + 5000, token };", "const token = ++_tokenPenutup;")]}),
    ('tanpa token (nota berdekatan berebut)', {'baru/js/layar/jual.js': [("if (!tahan || tahan.token !== token) return;", "if (!tahan) return;")]}),
    ('lapisan uang tidak dicabut saat Keluar', {'baru/js/app.js': [("['omzetPil', 'omzetToast', 'omzetNaik', 'koinOmzet', 'cincinOmzet', 'kilauOmzet', 'panggung'].forEach((id) => { const el = document.getElementById(id); if (el) el.remove(); });", "")]}),
    ('gulirkan mulai dari angka akhir lagi', {'baru/js/inti/gerak.js': [("el.__gulir = true; el.__tampil = awal; el.textContent = format(awal);", "el.__gulir = true; el.__tampil = awal;")]}),
    ('getar menempel', {'baru/js/inti/gerbang.js': [("|| (t !== 'salah' && /^goyang[12]$/.test(c))", "")]}),
    ('formulir sekilas di jalur cepat', {'baru/css/gerbang.css': [('.gerbang-masuk.t-membuka.cepat .gm-pelat { visibility: hidden; animation: none; }\n', '')]}),
    ('harga digambar ulang tiap dibuka', {'baru/js/layar/harga.js': [('if (tampil && (_kotor || !akar.firstElementChild)) segera(gambar); } }', 'if (tampil) segera(gambar); } }')]}),
    ('39b-19: tanpa adegan merayakan Σ hargaTotal (tukar dirayakan penuh)', {'baru/js/layar/jual.js': [('setTimeout(() => rayakanOmzet(L.hariIni(S()).omzet - hariTadi.omzet), 80);', 'setTimeout(() => rayakanOmzet(tambahOmzet), 80);')]}),
    ('gambar ganda status', {'baru/js/app.js': [('const GAMBAR_STATUS = [layar.gambarGulir, ringkasan.gambar,', 'const GAMBAR_STATUS = [() => layar.gambar(), ringkasan.gambar,')]}),
    ('tumpukan: sisa terakhir tak tergambar (lantai, bukan paling sedikit satu lapis)', {'baru/js/layar/gambar.js': [('const k = Math.max(1, Math.round(Math.sqrt(bulat2(isi)) * TUMPUK_N));', 'const k = Math.max(0, Math.floor(Math.sqrt(bulat2(isi)) * TUMPUK_N));')]}),
    ('tumpukan: lapis tidak dijepit ke sisa', {'baru/js/layar/gambar.js': [('return Math.min(TUMPUK_N, adaJumlah ? Math.min(k, Math.ceil(j - 1e-9)) : k);', 'return Math.min(TUMPUK_N, k);')]}),
    ('tumpukan: kemasan hanya menggambar lapis yang tampak (rangka berubah, transisi mati)', {'baru/js/layar/gambar.js': [('for (let i = 0; i < TUMPUK_N; i++) semua.push(lapis(i, k, x0 + GESER_KANTONG[i]', 'for (let i = 0; i < k; i++) semua.push(lapis(i, k, x0 + GESER_KANTONG[i]')]}),
    ('tumpukan: CSS menyalin angka 5 lagi', {'baru/css/jual.css': [('transition-delay: calc(var(--j, 0) * 45ms);', 'transition-delay: calc((5 - var(--i, 0)) * 45ms);')]}),
]


def pasang_preload():
    _, teks = baca(); lokal, luar = graf_impor(teks)
    p = os.path.join(AKAR, 'baru/index.html'); s = open(p, encoding='utf-8').read()
    s = re.sub(r'(<link rel="modulepreload" href="[^"]+">\n)+', lambda m: ''.join('<link rel="modulepreload" href="%s">\n' % x for x in luar + lokal), s, count=1)
    open(p, 'w', encoding='utf-8').write(s); print('modulepreload ditulis ulang:', len(luar + lokal))


def main():
    if '--pasang-preload' in sys.argv: return pasang_preload() or 0
    if '--kontrol' in sys.argv:
        diam = []
        for nama, g in KONTROL:
            t, teks = baca(g)
            asli = {}
            def teks2(b, t=t):
                if b not in t: t[b] = open(os.path.join(AKAR, b), encoding='utf-8').read()
                return t[b]
            gagal = [n for n, c, k in periksa(t, teks2) if not c]
            print(('BERBUNYI ' if gagal else 'DIAM     ') + nama + ('  → ' + gagal[0] if gagal else ''))
            if not gagal: diam.append(nama)
        print('kontrol: %d/%d berbunyi' % (len(KONTROL) - len(diam), len(KONTROL))); return 3 if diam else 0
    t, teks = baca(); hasil = periksa(t, teks)
    for n, c, k in hasil:
        if not c: print('GAGAL:', n, '→', str(k)[:500])
    lulus = sum(1 for _, c, _ in hasil if c); print('%d lulus · %d gagal' % (lulus, len(hasil) - lulus))
    return 0 if lulus == len(hasil) else 1


if __name__ == '__main__':
    sys.exit(main())
