#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_safari_webkit.py — cacat khas Safari/WebKit di /baru/ (owner 3 Okt 2026: /baru/ dipakai sebagai web app Safari di Mac + Safari iPhone/iPad,
"banyak bug"). Statis + jsc (JavaScriptCore = mesin Safari), TANPA peramban. Sembilan penjaga:

  1 SANDI    kolom sandi: readonly dilepas juga di pointerdown (sebelum fokus — papan ketik iPhone) & tidak dipasang lagi selagi kolom fokus
             (dulu sandi salah lewat Enter/Go → kolom terkunci, ketikan berikutnya tidak masuk). jsc: kunciSandi() diam selagi fokus.
  2 PONI     tiap main.layar-* (dari <main> di index.html) memberi jarak poni: padding-top … env(safe-area-inset-top) SESUDAH shorthand padding.
  3 HOVER    kerangka.css: :hover hanya di @media (hover: hover) and (pointer: fine) — iPad sentuh menempelkan :hover, menu samping tetap
             melebar & monogram tidak bisa menutupnya. .side.buka tetap membuka menu; Mac dengan kursor tetap menepi-membuka.
  4 BULAN    tidak ada <input type="month"/"week"> di /baru/ (Safari macOS: kotak teks biasa); Pajak › Omzet di luar sistem memilih bulan lewat pil
             (jsc: baris templat & penangan pjLuarPilih asli digambar/dijalankan dengan h asli dom.js).
  5 MEMBAL   satu pendengar touchstart PASIF di document (app.js, tingkat atas) — tanpa itu iOS tidak pernah menggambar :active.
  6 MUAT     penjaga muat-ulang modul (script sebaris index.html, dijalankan di jsc) mengenali kalimat galat Safari "Importing binding name …",
             Firefox "doesn't provide an export", Chrome, dan gagal unduh — sekali saja; galat biasa tidak memuat ulang.
  7 JARAK    kerangka.css: body digeser env(safe-area-inset-left/right) (iPhone miring), aturan ≥1100 body padding-left 72px tetap menang;
             lembar tablet ikut jarak aman kanan.
  8 MINUS    kolom yang menerima minus (#rtSelisih, placeholder "minus") tanpa inputmode angka — papan angka iPhone tidak punya '-'.
             (owner 7 Okt, sanggahan E2) kolom TANGGAL (id …Tgl / …Tanggal, data-kolom tgl / tanggal) = pemilih tanggal type="date", tidak pernah kotak teks
             inputmode angka — format 2026-08-31 butuh '-'.
  9 GESTUR   Laporan keluarkan(): WA / dialog cetak dibuka SINKRON di ketukan, baru nomornya dicatat (jsc dengan pemblokir jendela ala Safari);
             nomor dokumen = nomor yang dicatat, satu per ketukan; catatan gagal → kabar jujur; bukaWa tanpa 'noopener' (selalu null).
 10 WA LAIN  (owner 7 Okt, sisa #104) Uang & Harga: bukaWa tanpa 'noopener' — jsc: jendela yang terbuka DIKEMBALIKAN (bukan null) & opener-nya diputus;
             tidak ada 'noopener' di kode layar mana pun.
 11 PAKET    (owner 7 Okt) Laporan › Paket bank: dialog cetak dibuka SINKRON di ketukan (jsc, pemblokir ala Safari); nomor di tiap kertas = nomor yang
             dicatat (urut, satu kiriman); catatan gagal → kabar menyebut paketnya sudah keluar; paket ditolak → tidak mencetak & tidak mencatat.
 12 HOVER    (owner 7 Okt) SETIAP :hover di stylesheet /baru/ (jual, menu, pelanggan, stok, identitas, kerangka …) hanya di @media (hover: hover) and
             (pointer: fine) — iPad sentuh menempelkan :hover pada yang terakhir diketuk.

    python3 alat-uji/uji_safari_webkit.py            → N lulus · 0 gagal
    python3 alat-uji/uji_safari_webkit.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, glob, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
from uji_tata_letak_jual import aturan   # noqa: E402  (pengurai CSS yang sama)
import bundel_baru   # noqa: E402  (polos(): impor dibuang, export dicabut)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
HTML = 'baru/index.html'; APP = 'baru/js/app.js'; LAP = 'baru/js/layar/laporan.js'; JUAL = 'baru/js/layar/jual.js'; KER = 'baru/css/kerangka.css'
UANG = 'baru/js/layar/uang.js'; HARGA = 'baru/js/layar/harga.js'   # owner 7 Okt (sisa #104)


def baca(ganti=None):
    t = {HTML: open(os.path.join(AKAR, HTML), encoding='utf-8').read()}
    for p in sorted(glob.glob(os.path.join(AKAR, 'baru/js/**/*.js'), recursive=True)) + sorted(glob.glob(os.path.join(AKAR, 'baru/css/*.css'))):
        t[os.path.relpath(p, AKAR)] = open(p, encoding='utf-8').read()
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def jsc(kode):
    fd, p = tempfile.mkstemp(suffix='.js'); os.write(fd, kode.encode('utf-8')); os.close(fd)
    try:
        r = subprocess.run([JSC, p], capture_output=True, text=True, timeout=30)
        out = r.stdout.strip().splitlines()
        try: return json.loads(out[-1]) if out else None
        except ValueError: return {'galat': (r.stdout + r.stderr)[-400:]}
    finally: os.unlink(p)


def css_urut(t):
    """[(berkas, media, selektor, isi)] semua stylesheet lokal dalam urutan <link> di index.html (= urutan kaskade)."""
    out = []
    for href in re.findall(r'<link rel="stylesheet" href="(css/[^"]+)">', t[HTML]):
        b = 'baru/' + href
        out += [(b, m, s, isi) for m, s, isi in aturan(t.get(b, ''))]
    return out


def deklarasi(isi):
    """[(sifat, nilai)] berurutan — nilai terakhir yang menang di aturan yang sama."""
    out = []
    for d in isi.split(';'):
        if ':' in d:
            k, v = d.split(':', 1); out.append((k.strip(), v.strip()))
    return out


# ---------- jsc: potongan kode ASLI (kunciSandi, script sebaris, baris templat Bulan + pjLuarPilih, keluarkan) dijalankan dengan tiruan peramban ----------
SANDI_UJI = r"""
var isianSandi = { readOnly: false }, lain = {}; var document = { activeElement: isianSandi };
%s
var h = {}; kunciSandi(); h.fokus = isianSandi.readOnly; document.activeElement = lain; kunciSandi(); h.tidakFokus = isianSandi.readOnly;
print(JSON.stringify(h));
"""

MUAT_UJI = r"""
var H = [], muat = 0, simpan = {};
var window = { addEventListener: function (t, f) { if (t === 'error') H.push(f); } };
var location = { reload: function () { muat++; } };
var sessionStorage = { getItem: function (k) { return Object.prototype.hasOwnProperty.call(simpan, k) ? simpan[k] : null; }, setItem: function (k, v) { simpan[k] = String(v); } };
%s
var PICU = %s, DIAM = %s;
function coba(pesan) { simpan = {}; muat = 0; H.forEach(function (f) { f({ message: pesan }); }); return muat; }
var h = { picu: {}, diam: {}, nPenjaga: H.length };
PICU.forEach(function (p) { h.picu[p] = coba(p); });
DIAM.forEach(function (p) { h.diam[p] = coba(p); });
simpan = {}; muat = 0; H.forEach(function (f) { f({ message: PICU[0] }); }); H.forEach(function (f) { f({ message: PICU[0] }); }); h.sekali = muat;
print(JSON.stringify(h));
"""
PICU = ["SyntaxError: Importing binding name 'pasangLayarJual' is not found.",
        "SyntaxError: Importing binding name 'default' cannot be resolved by star export entries.",
        "SyntaxError: Importing binding name 'susunRak' cannot be resolved due to ambiguous multiple bindings.",
        "SyntaxError: The requested module './jual-logika.js' does not provide an export named 'susunRak'",
        "SyntaxError: The requested module './jual-logika.js' doesn't provide an export named: 'susunRak'",
        "TypeError: Importing a module script failed."]
DIAM = ["TypeError: undefined is not an object (evaluating 'a.b')", "ReferenceError: Can't find variable: susunRak", "SyntaxError: Unexpected token '}'"]

BULAN_UJI = r"""
%s
var T = { daftar: ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10'].map(function (m) { return { key: '2026-' + m, pendek: 'B' + m }; }) };
var dl = { bulan: '2026-09', sumber: 'catatanLama', jumlah: '5', keterangan: '' };
function bulanKini() { return '2026-10'; }
%s
var html = h`%s`.html;
var keadaan = { drafLuar: dl };
function st() { return keadaan; }
function set(p) { for (var k in p) keadaan[k] = p[k]; }
var pjLuarPilih = %s;
var m = /<div class="seg ?(?:aktif)?" data-aksi="pjLuarPilih" data-kunci="(\w+)" data-nilai="2026-08">/.exec(html);
if (m) pjLuarPilih({ kunci: m[1], nilai: '2026-08' });
print(JSON.stringify({ html: html, sesudah: keadaan.drafLuar }));
"""

# pemblokir jendela ala Safari: window.open hanya berhasil selagi gestur ketukan hidup (bagian sinkron penangan ketukan);
# fitur 'noopener' = selalu null walau jendelanya terbuka (aturan peramban)
GESTUR_UJI = r"""
var gestur = false, blokir = false, gagalTulis = false, dibuka = [], dicetak = [], tulisan = [], keadaan = {};
var window = { open: function (url, target, fitur) { var w = (!blokir && gestur) ? { opener: {} } : null; dibuka.push({ url: url, gestur: gestur, terbuka: !!w }); return /noopener/.test(fitur || '') ? null : w; },
  print: function () { dicetak.push(gestur); }, addEventListener: function () {}, removeEventListener: function () {} };
var document = { getElementById: function () { return { innerHTML: '' }; }, body: { classList: { add: function () {}, remove: function () {} } } };
setTimeout = function () {};
var LP = { susunCetakan: function (info, cara) { if (['cetak', 'pdf', 'wa'].indexOf(cara) < 0) return { tolak: 'Cara keluar tidak dikenal' }; return { nomor: 7, dokumen: [{ koleksi: 'dokumenCetak', data: { id: 'dc-1', nomor: 7, cara: cara } }], patch: { kabar: info.judul + ' — No. 7', kabarAwas: false } }; },
  teksDokumen: function (D, nomor) { return D.judul + ' No. ' + nomor; } };
function ANGKA(n) { return String(n); }
function waktu() { return { tanggal: '2026-10-03', jam: '10.00' }; }
function iso() { return '2026-10-03'; }
function kertas(D, nomor) { return { html: '<div>' + D.judul + ' No. ' + nomor + '</div>' }; }
function set(p) { for (var k in p) keadaan[k] = p[k]; }
function st() { return keadaan; }
async function tulis(r) { tulisan.push(r); await null; await null; if (gagalTulis) { set({ kabar: 'DITOLAK: server menolak', kabarAwas: true }); return false; } set({ kabar: r.patch.kabar, kabarAwas: false }); return true; }
%s
%s
%s
async function ketuk(cara, o) {
  o = o || {}; dibuka = []; dicetak = []; tulisan = []; keadaan = { kabar: '', kabarAwas: false }; blokir = !!o.blokir; gagalTulis = !!o.gagal;
  gestur = true; var p = keluarkan(o.D || { judul: 'Rekap', kop: {} }, { jenis: 'omzet', judul: 'Rekap' }, cara); gestur = false; await p;
  return { dibuka: dibuka, dicetak: dicetak, nTulis: tulisan.length, nomorTulis: tulisan.length ? tulisan[0].nomor : null, kabar: keadaan.kabar, awas: keadaan.kabarAwas };
}
(async function () { var h = {}; h.wa = await ketuk('wa'); h.cetak = await ketuk('cetak'); h.pdf = await ketuk('pdf'); h.gagalWa = await ketuk('wa', { gagal: true });
  h.gagalCetak = await ketuk('cetak', { gagal: true }); h.blokir = await ketuk('wa', { blokir: true }); h.tolak = await ketuk('wa', { D: { judul: 'X', tolak: 'Kop belum lengkap', kop: {} } });
  print(JSON.stringify(h)); })().catch(function (e) { print(JSON.stringify({ galat: String(e) })); });
"""


# owner 7 Okt (sisa #104): bukaWa Uang & Harga dengan pemblokir ala Safari — 'noopener' = selalu null walau jendelanya terbuka
WA_UJI = r"""
var gestur = true, dibuka = [];
var window = { open: function (url, target, fitur) { var w = gestur ? { opener: { asal: 'layar' } } : null; dibuka.push({ url: url, fitur: fitur || '' }); return /noopener/.test(fitur || '') ? null : w; } };
%s
var w = bukaWa(%s);
print(JSON.stringify({ kembali: !!w, opener: w ? (w.opener === null ? 'putus' : 'tersambung') : 'tidak ada', n: dibuka.length, url: dibuka.length ? dibuka[0].url : '' }));
"""

# owner 7 Okt: Laporan › Paket bank — penangan dkPaketSusun ASLI + cetakHtml ASLI; LP/kertas/tulis tiruan. window.print mencatat apakah gestur hidup.
PAKET_UJI = r"""
var gestur = false, gagalTulis = false, tolakPaket = false, dicetak = [], tulisan = [], keadaan = {};
var EL = { innerHTML: '' };
var window = { print: function () { dicetak.push(gestur); }, addEventListener: function () {}, removeEventListener: function () {} };
var document = { getElementById: function () { return EL; }, body: { classList: { add: function () {}, remove: function () {} } } };
setTimeout = function () {};
function ANGKA(n) { return String(n); }
function waktu() { return { tanggal: '2026-10-07', jam: '10.00' }; }
function kini() { return new Date(0); }
var DOKS = [{ jenis: 'labarugi', judul: 'Laporan Laba-Rugi', periode: 'Jul – Sep 26' }, { jenis: 'neraca', judul: 'Laporan Neraca', periode: 'Sep 2026' }, { jenis: 'omzet', judul: 'Rekap Omzet Bulanan', periode: '12 bulan', R: {} }];
var LP = { paketBank: function () { return tolakPaket ? { tolak: 'Belum ada bulan yang tutup buku' } : { daftar: DOKS }; },
  susunPaketCetakan: function (daftar) { return { nomor: 7, nomorAkhir: 7 + daftar.length - 1, dokumen: daftar.map(function (d, i) { return { koleksi: 'dokumenCetak', data: { nomor: 7 + i, jenis: d.jenis, judul: d.judul } }; }) }; } };
function dokRekap() { return { jenis: 'omzet', judul: 'Rekap Omzet Bulanan', periode: '12 bulan' }; }
// hemat baca (#111, sanggahan 8 Okt): penjaga kelengkapan paket bank SINKRON sebelum dialog cetak — di uji gestur ini saklar mati ('' = lengkap); dijaga uji_periksa_sesudah.py S7d
function hematBelum() { return ''; }
function kertas(D, nomor) { return { html: '<div class="dk-kertas" data-no="' + nomor + '">' + D.judul + '</div>' }; }
function set(p) { for (var k in p) keadaan[k] = p[k]; }
function st() { return keadaan; }
async function tulis(r) { tulisan.push(r); await null; await null; if (gagalTulis) { set({ kabar: 'DITOLAK: server menolak', kabarAwas: true }); return false; } return true; }
%s
var AKSI = { dkPaketSusun: %s };
async function ketuk(o) {
  o = o || {}; dicetak = []; tulisan = []; EL.innerHTML = ''; keadaan = { kabar: '', kabarAwas: false, paket: {} }; gagalTulis = !!o.gagal; tolakPaket = !!o.tolak;
  gestur = true; var p = AKSI.dkPaketSusun(); gestur = false; await p;
  return { dicetak: dicetak, nTulis: tulisan.length, nomorTulis: tulisan.length ? tulisan[0].dokumen.map(function (d) { return d.data.nomor; }) : [],
    nomorKertas: (EL.innerHTML.match(/data-no="\d+"/g) || []).map(function (x) { return Number(x.replace(/\D/g, '')); }), kabar: keadaan.kabar, awas: keadaan.kabarAwas };
}
(async function () { var h = {}; h.biasa = await ketuk(); h.gagal = await ketuk({ gagal: true }); h.tolak = await ketuk({ tolak: true }); print(JSON.stringify(h)); })().catch(function (e) { print(JSON.stringify({ galat: String(e) })); });
"""


def potong(teks, pola):
    m = re.search(pola, teks, re.S | re.M); return m.group(0) if m else ''


def periksa(t):
    c = []   # (nama, lulus, keterangan)
    A = css_urut(t)

    # ---- 1 SANDI ----
    app = t[APP]
    c.append(('1 sandi: readonly dilepas di pointerdown (sebelum fokus — papan ketik iPhone menimbang kolom yang bisa diketik)',
              bool(re.search(r"isianSandi\.addEventListener\('pointerdown',\s*\(\)\s*=>\s*\{\s*isianSandi\.readOnly\s*=\s*false;\s*\}\);", app)), ''))
    pasang = [m.group(0) for m in re.finditer(r'isianSandi\.readOnly\s*=\s*([^;=][^;]*);', app) if m.group(1).strip() != 'false']
    helper = potong(app, r"^const kunciSandi = \(\) => \{.*?\};$")
    c.append(('1 sandi: readonly dipasang di SATU tempat (kunciSandi), tidak ada pemasangan lain', len(pasang) == 1 and bool(helper) and pasang[0] in helper, pasang))
    h = jsc(SANDI_UJI % helper) if helper else None
    c.append(('1 sandi (jsc): kunciSandi() diam selagi kolom fokus, mengunci kalau tidak fokus', h == {'fokus': False, 'tidakFokus': True}, h))
    c.append(('1 sandi: sesudah percobaan masuk & saat formulir digambar ulang readonly lewat kunciSandi()',
              bool(re.search(r"await fb\.masuk\(email, sandi\);[^\n]*\bkunciSandi\(\);", app)) and bool(re.search(r"isianSandi\.value = '';\s*kunciSandi\(\); salahMasuk\.hidden = true;", app)), ''))

    # ---- 2 PONI ----
    layar = re.findall(r'<main\b[^>]*class="(layar-[\w-]+)"', t[HTML])
    tanpa = {}
    for n in layar:
        dk = [d for b, m, s, isi in A if not m and s.strip() == 'main.' + n for d in deklarasi(isi)]
        sh = max([i for i, (k, v) in enumerate(dk) if k == 'padding'] or [-1])
        pt = [i for i, (k, v) in enumerate(dk) if k == 'padding-top']
        if not pt or pt[-1] < sh or 'safe-area-inset-top' not in dk[pt[-1]][1]: tanpa[n] = dk[pt[-1]] if pt else 'tanpa padding-top'
    c.append(('2 poni: tiap main.layar-* (' + str(len(layar)) + ' layar) memberi jarak env(safe-area-inset-top) SESUDAH shorthand padding', len(layar) >= 8 and not tanpa, tanpa))

    # ---- 3 HOVER ----
    K = [(m, s, isi) for b, m, s, isi in A if b == KER]
    salah = [(m, s) for m, s, isi in K if ':hover' in s and not ('(hover: hover)' in m and '(pointer: fine)' in m)]
    c.append(('3 hover: tiap :hover di kerangka.css hanya di @media (hover: hover) and (pointer: fine)', not salah, salah))
    buka = [isi for m, s, isi in K if 'min-width: 1100px' in m and s.strip() == '.side.buka']
    teks = [isi for m, s, isi in K if 'min-width: 1100px' in m and s.strip() == '.side.buka .teks']
    c.append(('3 hover: .side.buka tetap membuka menu samping (236px, teks tampil) — jalan layar sentuh lewat monogram',
              any('width: 236px' in x for x in buka) and any('opacity: 1' in x for x in teks), (buka, teks)))
    kursor = [isi for m, s, isi in K if '(hover: hover)' in m and '(pointer: fine)' in m and 'min-width: 1100px' in m and s.strip() == '.side:hover']
    c.append(('3 hover: Mac dengan kursor tetap menepi-membuka (.side:hover 236px di media kursor)', any('width: 236px' in x for x in kursor), kursor))

    # ---- 4 BULAN ----
    bulan = [b + ':' + str(t[b][:m.start()].count('\n') + 1) for b in t if b.startswith('baru/') and not b.endswith('.css')
             for m in re.finditer(r'''type\s*=\s*["'](month|week)["']''', t[b])]
    c.append(('4 bulan: tidak ada kolom berjenis month/week di /baru/ (Safari macOS: kotak teks tanpa pemilih)', not bulan, bulan))
    # baris "Bulan" templat form Omzet di luar sistem + helper pil + penangan pjLuarPilih ASLI dijalankan di jsc dengan h/esc asli dom.js
    form = potong(t[LAP], r'data-k="pj-luar-form".*?data-aksi="pjLuarSimpan"')
    mb = re.search(r'^\s*<div class="label">Bulan</div>.*$', form, re.M); baris = mb.group(0).strip() if mb else ''   # SATU baris templat (tanpa re.S)
    pil = potong(t[LAP], r"const pil = \(v, id, aksi, kunci\) => h`[^`]*`;")
    pen = re.search(r'pjLuarPilih: (\(\{ kunci, nilai \}\) => \{ .*? \}), pjLuarSimpan', t[LAP])
    h = jsc(BULAN_UJI % (bundel_baru.polos(t['baru/js/inti/dom.js']), pil, baris, pen.group(1))) if baris and pil and pen else {'galat': 'potongan tidak ditemukan'}
    h = h or {}
    pils = re.findall(r'<div class="seg ?(aktif)?" data-aksi="([^"]+)" data-kunci="([^"]+)" data-nilai="([^"]+)">([^<]*)</div>', h.get('html') or '')
    c.append(("4 bulan (jsc): form Omzet di luar sistem menggambar pil bulan Jan–bulan ini (terbaru di depan), bulan draf menyala, tanpa kolom ketik",
              len(pils) == 10 and pils[0][3] == '2026-10' and pils[-1][3] == '2026-01' and all(p[1] == 'pjLuarPilih' and p[2] == 'bulan' for p in pils)
              and [p[3] for p in pils if p[0]] == ['2026-09'] and '<input' not in (h.get('html') or ''), h.get('galat') or (h.get('html') or '')[:300]))
    c.append(("4 bulan (jsc): ketuk pil Agustus → pjLuarPilih mengganti bulan draf (isian lain tetap)", h.get('sesudah') == {'bulan': '2026-08', 'sumber': 'catatanLama', 'jumlah': '5', 'keterangan': ''}, h.get('sesudah')))

    # ---- 5 MEMBAL ----
    sentuh = re.findall(r"^document\.addEventListener\('touchstart',\s*\(\)\s*=>\s*\{\s*\},\s*\{\s*passive:\s*true\s*\}\);", app, re.M)
    c.append(('5 membal: satu pendengar touchstart PASIF di document, tingkat atas app.js (iOS baru menggambar :active)', len(sentuh) == 1, sentuh))
    aktif = any(':active' in s for b, m, s, isi in A if b == 'baru/css/gerak.css')
    c.append(('5 membal: efek tekan :active masih ada di gerak.css (yang dijaga pendengar itu)', aktif, ''))

    # ---- 6 MUAT ULANG ----
    sebaris = re.findall(r'<script>(.*?)</script>', t[HTML], re.S)
    h = jsc(MUAT_UJI % ('\n'.join(sebaris), json.dumps(PICU), json.dumps(DIAM))) if sebaris else None
    h = h or {}
    picu = h.get('picu') or {}
    c.append(('6 muat: penjaga modul ada (satu pendengar error di script sebaris)', h.get('nPenjaga') == 1, h.get('nPenjaga')))
    c.append(('6 muat (jsc): kalimat Safari "Importing binding name … not found / cannot be resolved" memuat ulang', all(picu.get(p) == 1 for p in PICU[:3]), {p[:50]: picu.get(p) for p in PICU[:3]}))
    c.append(('6 muat (jsc): kalimat Chrome & Firefox (ekspor hilang) dan Safari gagal unduh memuat ulang', all(picu.get(p) == 1 for p in PICU[3:]), {p[:50]: picu.get(p) for p in PICU[3:]}))
    c.append(('6 muat (jsc): galat biasa TIDAK memuat ulang; muat ulang hanya sekali (tanda sessionStorage)',
              all((h.get('diam') or {}).get(p) == 0 for p in DIAM) and h.get('sekali') == 1, (h.get('diam'), h.get('sekali'))))

    # ---- 7 JARAK AMAN ----
    tubuh = [(i, d) for i, (b, m, s, isi) in enumerate(A) if not m and s.strip() == 'body' for d in deklarasi(isi) if d[0].startswith('padding')]
    kiri = [x for x in tubuh if x[1][0] in ('padding', 'padding-left')]; kanan = [x for x in tubuh if x[1][0] in ('padding', 'padding-right')]
    c.append(('7 jarak: body digeser env(safe-area-inset-left/right) (iPhone miring, viewport-fit=cover)',
              bool(kiri) and bool(kanan) and 'safe-area-inset-left' in kiri[-1][1][1] and 'safe-area-inset-right' in kanan[-1][1][1], tubuh))
    mac = [i for i, (b, m, s, isi) in enumerate(A) if m.strip() == '@media (min-width: 1100px)' and s.strip() == 'body' and re.search(r'padding-left:\s*72px', isi)]
    c.append(('7 jarak: aturan ≥1100 body padding-left 72px (menu samping) tetap ada & datang SESUDAH jarak aman → menang di Mac/iPad',
              bool(mac) and bool(kiri) and mac[-1] > kiri[-1][0], (mac, kiri[-1][0] if kiri else None)))
    lb = [isi for b, m, s, isi in A if b == KER and m.strip() == '@media (min-width: 720px)' and s.strip() == '.lembar:not(.tirai)']
    c.append(('7 jarak: lembar tablet ikut jarak aman kanan (tetap di atas kolom keranjang yang bergeser)', any(re.search(r'right:\s*calc\(14px \+ env\(safe-area-inset-right', x) for x in lb), lb))

    # ---- 8 MINUS ----
    salah = []
    for b in t:
        if not b.endswith('.js'): continue
        for m in re.finditer(r'<input\b[^>]*>', t[b]):
            tag = m.group(0)
            if ('id="rtSelisih"' in tag or re.search(r'placeholder="[^"]*\bminus\b', tag)) and re.search(r'inputmode="(numeric|decimal)"', tag): salah.append(b + ':' + str(t[b][:m.start()].count('\n') + 1))
    ada = '<input class="ketik-nama" id="rtSelisih"' in t[JUAL]
    c.append(('8 minus: #rtSelisih & kolom ber-placeholder "minus" tanpa inputmode angka (papan angka iPhone tanpa tanda minus)', ada and not salah, salah or ('rtSelisih ada' if ada else 'rtSelisih HILANG')))
    tgl = []; nTgl = 0
    for b in t:
        if not b.endswith('.js'): continue
        for m in re.finditer(r'<input\b[^>]*>', t[b]):
            tag = m.group(0)
            if re.search(r'\bid="\w*(Tgl|Tanggal)\w*"', tag) or re.search(r'\bdata-kolom="(tgl|tanggal)"', tag):
                nTgl += 1
                if 'type="date"' not in tag or re.search(r'inputmode="(numeric|decimal)"', tag): tgl.append(b + ':' + str(t[b][:m.start()].count('\n') + 1))
    c.append(('8 tanggal: kolom tanggal (#bpBetulTgl, #bpLamaTgl, …) = pemilih tanggal type="date", bukan kotak teks inputmode angka (format 2026-08-31 butuh "-")', nTgl >= 4 and not tgl and 'id="bpBetulTgl" type="date"' in t[HARGA], tgl or ('kolom tanggal ' + str(nTgl))))

    # ---- 9 GESTUR ----
    lap = t[LAP]
    wa = potong(lap, r'^  const bukaWa = \(teks\) => .*?$'); ce = potong(lap, r'^  const cetakHtml = \(html\) => .*?$')
    kel = potong(lap, r'^  async function keluarkan\(D, info, cara\) \{\n.*?\n  \}$')
    h = jsc(GESTUR_UJI % (wa, ce, kel)) if wa and ce and kel else {'galat': 'potongan tidak ditemukan'}
    h = h or {}
    W = h.get('wa') or {}; C = h.get('cetak') or {}; P = h.get('pdf') or {}
    c.append(('9 gestur (jsc): kirim WA membuka jendela SELAGI ketukan hidup — jendela terbuka, kabar tidak menyebut ditahan',
              len(W.get('dibuka') or []) == 1 and W['dibuka'][0]['gestur'] and W['dibuka'][0]['terbuka'] and 'menahan' not in W.get('kabar', '') and W.get('awas') is False, h.get('galat') or W))
    c.append(('9 gestur (jsc): CETAK & simpan PDF memanggil dialog cetak selagi ketukan hidup', C.get('dicetak') == [True] and P.get('dicetak') == [True], (C.get('dicetak'), P.get('dicetak'))))
    c.append(('9 gestur (jsc): nomor di teks WA = nomor yang dicatat, satu catatan per ketukan (cetak/PDF/WA)',
              W.get('nTulis') == 1 and W.get('nomorTulis') == 7 and 'No.%207' in ((W.get('dibuka') or [{}])[0].get('url') or '') and C.get('nTulis') == 1 and P.get('nTulis') == 1, (W.get('nTulis'), C.get('nTulis'), P.get('nTulis'))))
    G = h.get('gagalWa') or {}; GC = h.get('gagalCetak') or {}
    c.append(('9 gestur (jsc): catatan nomor gagal → kabar jujur: dokumen sudah keluar, nomornya TIDAK tercatat, alasan server ikut',
              all(x.get('awas') and 'No. 7' in x.get('kabar', '') and 'TIDAK tercatat' in x.get('kabar', '') and 'DITOLAK: server menolak' in x.get('kabar', '') for x in (G, GC))
              and 'WhatsApp' in G.get('kabar', '') and 'dialog cetak' in GC.get('kabar', ''), (G.get('kabar'), GC.get('kabar'))))
    B = h.get('blokir') or {}; T = h.get('tolak') or {}
    c.append(('9 gestur (jsc): jendela benar-benar ditahan → nomor tetap tercatat seperti dulu & kabar menyebut ditahan',
              B.get('nTulis') == 1 and B.get('awas') and 'menahan' in B.get('kabar', '') and 'No. 7' in B.get('kabar', ''), B.get('kabar')))
    c.append(('9 gestur (jsc): dokumen yang ditolak (kop belum lengkap) tidak membuka apa pun & tidak mencatat nomor',
              T.get('dibuka') == [] and T.get('nTulis') == 0 and T.get('kabar') == 'Kop belum lengkap', T))
    kode = re.sub(r'^\s*//.*$', '', lap, flags=re.M)   # komentar baris penuh dibuang (komentarnya menyebut 'noopener')
    c.append(("9 gestur: tidak ada window.open(…, 'noopener') di layar Laporan (selalu null → kabar \"ditahan\" palsu)", 'noopener' not in kode, ''))

    # ---- 10 WA LAIN (owner 7 Okt, sisa #104) ----
    for b, pola, arg in ((UANG, r'^  const bukaWa = \(teks\) => .*?$', "'rekap uji'"), (HARGA, r'^  const bukaWa = \(tautan\) => .*?$', "'https://wa.me/?text=uji'")):
        wa = potong(t[b], pola); h = (jsc(WA_UJI % (wa, arg)) if wa else None) or {'galat': 'bukaWa tidak ditemukan'}
        nm = b.split('/')[-1]
        c.append(('10 wa (jsc): ' + nm + ' bukaWa mengembalikan jendela yang terbuka (bukan null) & memutus opener-nya — kabar "ditahan" tidak palsu',
                  h.get('kembali') is True and h.get('opener') == 'putus' and h.get('n') == 1 and 'wa.me' in (h.get('url') or ''), h))
    tanpa = [b for b in t if b.startswith('baru/js/') and b.endswith('.js') and 'noopener' in re.sub(r'^\s*//.*$', '', t[b], flags=re.M)]
    c.append(("10 wa: tidak ada 'noopener' di kode /baru/ mana pun (window.open dengan 'noopener' selalu null)", not tanpa, tanpa))

    # ---- 11 PAKET BANK (owner 7 Okt) ----
    pk = re.search(r"^    dkPaketSusun: (async \(\) => \{.*?semua dari bulan FINAL', kabarAwas: false \}\); \}),$", lap, re.S | re.M)
    h = (jsc(PAKET_UJI % (ce, pk.group(1))) if pk and ce else None) or {'galat': 'dkPaketSusun / cetakHtml tidak ditemukan'}
    PB = h.get('biasa') or {}; PG = h.get('gagal') or {}; PT = h.get('tolak') or {}
    c.append(('11 paket (jsc): dialog cetak paket bank dibuka SELAGI ketukan hidup (Safari menahan dialog sesudah await)', PB.get('dicetak') == [True], h.get('galat') or PB))
    c.append(('11 paket (jsc): nomor di tiap kertas = nomor yang dicatat, urut, SATU kiriman untuk seluruh paket',
              PB.get('nTulis') == 1 and PB.get('nomorTulis') == [7, 8, 9] and PB.get('nomorKertas') == [7, 8, 9] and PB.get('awas') is False and 'No. 7–9' in (PB.get('kabar') or ''), PB))
    c.append(('11 paket (jsc): catatan nomor gagal → kabar jujur: paket sudah dibuka di dialog cetak, nomornya TIDAK tercatat, alasan server ikut',
              PG.get('dicetak') == [True] and PG.get('awas') is True and 'dibuka di dialog cetak' in (PG.get('kabar') or '') and 'TIDAK tercatat' in (PG.get('kabar') or '') and 'DITOLAK: server menolak' in (PG.get('kabar') or ''), PG))
    c.append(('11 paket (jsc): paket yang ditolak (belum ada bulan final) tidak membuka dialog & tidak mencatat nomor', PT.get('dicetak') == [] and PT.get('nTulis') == 0 and PT.get('awas') is True, PT))

    # ---- 12 HOVER di semua stylesheet (owner 7 Okt) ----
    salah = [(b, m, s) for b, m, s, isi in A if ':hover' in s and not ('(hover: hover)' in m and '(pointer: fine)' in m)]
    n_hover = sum(1 for b, m, s, isi in A if ':hover' in s)
    c.append(('12 hover: SETIAP :hover di stylesheet /baru/ (' + str(n_hover) + ' aturan) hanya di @media (hover: hover) and (pointer: fine) — iPad sentuh menempelkannya', n_hover >= 8 and not salah, salah))
    aktif = [isi for b, m, s, isi in A if b == 'baru/css/stok.css' and not m and s.strip() == '.layar-stok .iso-toko .zona-iso.aktif .lantai-zona']
    c.append(('12 hover: zona denah yang DIPILIH (.aktif) tetap menyala tanpa kursor (dipisah dari :hover)', any('fill: var(--seg-aktif)' in x for x in aktif), aktif))
    return c


KONTROL = [
    ('1 sandi: pendengar pointerdown dibuang', {APP: [("isianSandi.addEventListener('pointerdown', () => { isianSandi.readOnly = false; });\n", '')]}),
    ('1 sandi: kunciSandi tanpa penjaga fokus', {APP: [('if (document.activeElement !== isianSandi) isianSandi.readOnly = true;', 'isianSandi.readOnly = true;')]}),
    ('1 sandi: sesudah percobaan masuk readonly dipasang langsung (lama)', {APP: [("await fb.masuk(email, sandi); isianSandi.value = ''; kunciSandi();", "await fb.masuk(email, sandi); isianSandi.value = ''; isianSandi.readOnly = true;")]}),
    ('2 poni: Pelanggan tanpa jarak poni (lama)', {'baru/css/pelanggan.css': [('padding: 14px 16px 120px; padding-top: calc(14px + env(safe-area-inset-top, 0px));', 'padding: 14px 16px 120px;')]}),
    ('2 poni: Pelanggan jarak poni SEBELUM shorthand (tertimpa)', {'baru/css/pelanggan.css': [('padding: 14px 16px 120px; padding-top: calc(14px + env(safe-area-inset-top, 0px));', 'padding-top: calc(14px + env(safe-area-inset-top, 0px)); padding: 14px 16px 120px;')]}),
    ('3 hover: .side:hover kembali di aturan ≥1100 tanpa syarat kursor (lama)', {KER: [('  .side.buka { width: 236px;', '  .side.buka, .side:hover { width: 236px;')]}),
    ('3 hover: media kursor tanpa (pointer: fine)', {KER: [('@media (min-width: 1100px) and (hover: hover) and (pointer: fine) {', '@media (min-width: 1100px) and (hover: hover) {')]}),
    ('3 hover: .side.buka tidak lagi menampilkan teks', {KER: [('  .side.buka .teks { opacity: 1; transform: none; }', '  .side.tutup .teks { opacity: 1; transform: none; }')]}),
    ('3 hover: Mac dengan kursor kehilangan menepi-membuka', {KER: [('  .side:hover { width: 236px; box-shadow: 18px 0 40px -28px var(--bayang); background: var(--nav); }\n', '')]}),
    ('4 bulan: kolom berjenis month kembali (lama)', {LAP: [('<div class="lp-bulan" data-k="pj-luar-bulan">${T.daftar.slice().reverse().map((b) => h`${pil(dl.bulan, b.key, \'pjLuarPilih\', \'bulan\')}${b.pendek}</div>`)}</div>',
                                                              '<input class="ketik-nama" type="month" value="${dl.bulan}" max="${bulanKini()}" data-ketik="pjLuarKetik" data-kunci="bulan">')]}),
    ('4 bulan: pil yang menyala menurut sumber, bukan bulan draf', {LAP: [("pil(dl.bulan, b.key, 'pjLuarPilih', 'bulan')", "pil(dl.sumber, b.key, 'pjLuarPilih', 'bulan')")]}),
    ('4 bulan: deretan bulan terlama di depan (beda dengan form Setoran)', {LAP: [("T.daftar.slice().reverse().map((b) => h`${pil(dl.bulan", "T.daftar.map((b) => h`${pil(dl.bulan")]}),
    ('4 bulan: pjLuarPilih menimpa seluruh draf (jumlah & keterangan hilang)', {LAP: [("pjLuarPilih: ({ kunci, nilai }) => { const d = Object.assign({}, st().drafLuar);", "pjLuarPilih: ({ kunci, nilai }) => { const d = {};")]}),
    ('5 membal: pendengar touchstart dibuang', {APP: [("document.addEventListener('touchstart', () => {}, { passive: true });\n", '')]}),
    ('5 membal: pendengar touchstart tidak pasif (menahan gulir)', {APP: [("document.addEventListener('touchstart', () => {}, { passive: true });", "document.addEventListener('touchstart', () => {}, { passive: false });")]}),
    ('6 muat: kalimat Safari "Importing binding name" dibuang dari penjaga (lama)', {HTML: [('|Importing binding name|', '|')]}),
    ("6 muat: kalimat Firefox \"doesn't provide an export\" dibuang", {HTML: [("|doesn't provide an export|", '|')]}),
    ('6 muat: tanda sekali-saja di sessionStorage dibuang (putaran muat ulang tanpa henti)', {HTML: [("if (sessionStorage.getItem('miqbal_muat_ulang_modul')) return; ", '')]}),
    ('7 jarak: body tanpa jarak aman kiri/kanan (lama)', {KER: [('body { padding-left: env(safe-area-inset-left, 0px); padding-right: env(safe-area-inset-right, 0px); }\n', '')]}),
    ('7 jarak: aturan ≥1100 body padding-left 72px hilang (isi masuk ke bawah menu samping)', {KER: [('  body { padding-left: 72px; }\n', '')]}),
    ('7 jarak: lembar tablet tidak ikut jarak aman kanan', {KER: [('right: calc(14px + env(safe-area-inset-right, 0px)); top: 14px; bottom: 100px;', 'right: 14px; top: 14px; bottom: 100px;')]}),
    ('8 minus: #rtSelisih diberi inputmode angka lagi (lama)', {JUAL: [('<input class="ketik-nama" id="rtSelisih" type="text" value=', '<input class="ketik-nama" id="rtSelisih" type="text" inputmode="numeric" value=')]}),
    ('8 tanggal: tanggal bon lama di lembar Betulkan bon kembali ke kotak teks inputmode angka (sanggahan E2)', {HARGA: [('id="bpBetulTgl" type="date" value=', 'id="bpBetulTgl" type="text" inputmode="numeric" placeholder="2026-08-31" value=')]}),
    ('9 gestur: WA/cetak dibuka sesudah menunggu (gestur habis, seperti dulu)', {LAP: [('    let w = true;\n', '    await null; let w = true;\n')]}),
    ("9 gestur: bukaWa memakai 'noopener' lagi (selalu null → kabar ditahan palsu)", {LAP: [("encodeURIComponent(teks), '_blank'); if (w)", "encodeURIComponent(teks), '_blank', 'noopener'); if (w)")]}),
    ('9 gestur: catatan nomor gagal → diam (kabar tidak menyebut dokumen sudah keluar)', {LAP: [('if (!(await tulis(r))) { set({ kabar: (w ?', 'if (!(await tulis(r))) { return; set({ kabar: (w ?')]}),
    ('9 gestur: dokumen ditolak tetap membuka jendela', {LAP: [("    if (D.tolak) { set({ kabar: D.tolak, kabarAwas: true }); return; } const r = LP.susunCetakan(info, cara, waktu());",
                                                           "    const r = LP.susunCetakan(info, cara, waktu());")]}),
    # owner 7 Okt (sisa #104)
    ("10 wa: uang.js bukaWa memakai 'noopener' lagi (lama)", {UANG: [("encodeURIComponent(teks), '_blank'); if (w)", "encodeURIComponent(teks), '_blank', 'noopener'); if (w)")]}),
    ("10 wa: harga.js bukaWa memakai 'noopener' lagi (lama)", {HARGA: [("window.open(tautan, '_blank'); if (w)", "window.open(tautan, '_blank', 'noopener'); if (w)")]}),
    ('10 wa: harga.js bukaWa tidak memutus opener', {HARGA: [("window.open(tautan, '_blank'); if (w) { try { w.opener = null; }", "window.open(tautan, '_blank'); if (w) { try { void 0; }")]}),
    ('11 paket: dialog cetak dibuka sesudah menunggu (gestur habis, seperti dulu)', {LAP: [("      cetakHtml(dok.map(", "      await null; cetakHtml(dok.map(")]}),
    ('11 paket: semua kertas paket bernomor sama', {LAP: [("kertas(d, r.nomor + i, 'p' + (r.nomor + i))", "kertas(d, r.nomor, 'p' + r.nomor)")]}),
    ('11 paket: catatan nomor gagal → diam', {LAP: [("if (!(await tulis(r, true))) { set({ kabar: teks + ', tapi", "if (!(await tulis(r, true))) { return; set({ kabar: teks + ', tapi")]}),
    ('11 paket: paket ditolak tetap mencetak', {LAP: [("    dkPaketSusun: async () => { const P = LP.paketBank(st().paket, kini()); if (P.tolak) { set({ kabar: P.tolak, kabarAwas: true }); return; }",
                                                    "    dkPaketSusun: async () => { const P = LP.paketBank(st().paket, kini()); if (P.tolak) { set({ kabar: P.tolak, kabarAwas: true }); P.daftar = []; }")]}),
    ('12 hover: jual.css .buang:hover tanpa syarat kursor (lama)', {'baru/css/jual.css': [('@media (hover: hover) and (pointer: fine) { .tab-antre .buang:hover { opacity: 1; color: var(--awas); } }', '.tab-antre .buang:hover { opacity: 1; color: var(--awas); }')]}),
    ('12 hover: menu.css .mn-baris:hover tanpa syarat kursor (lama)', {'baru/css/menu.css': [('@media (hover: hover) and (pointer: fine) { .mn-baris:hover { border-color: var(--kaca-tepi); } }', '.mn-baris:hover { border-color: var(--kaca-tepi); }')]}),
    ('12 hover: pelanggan.css polaroid:hover tanpa syarat kursor (lama)', {'baru/css/pelanggan.css': [('@media (hover: hover) and (pointer: fine) { .layar-pelanggan .polaroid:hover { transform: rotate(0deg) translateY(-3px); } }', '.layar-pelanggan .polaroid:hover { transform: rotate(0deg) translateY(-3px); }')]}),
    ('12 hover: stok.css tumpukan:hover tanpa syarat kursor (lama)', {'baru/css/stok.css': [('@media (hover: hover) and (pointer: fine) { .layar-stok .iso-toko .tumpukan:hover .sisi-atas { fill: #f6ecc8; } }', '.layar-stok .iso-toko .tumpukan:hover .sisi-atas { fill: #f6ecc8; }')]}),
    ('12 hover: stok.css zona:hover tanpa syarat kursor (lama)', {'baru/css/stok.css': [('@media (hover: hover) and (pointer: fine) { .layar-stok .iso-toko .zona-iso:hover .lantai-zona { fill: var(--seg-aktif); stroke: var(--emas-garis); } }', '.layar-stok .iso-toko .zona-iso:hover .lantai-zona { fill: var(--seg-aktif); stroke: var(--emas-garis); }')]}),
    ('12 hover: identitas.css a:hover tanpa syarat kursor (lama)', {'baru/css/identitas.css': [('@media (hover: hover) and (pointer: fine) { a:hover { color: #2b241a; } }', 'a:hover { color: #2b241a; }')]}),
    ('12 hover: zona yang DIPILIH ikut masuk media kursor (iPad kehilangan tanda pilihan)', {'baru/css/stok.css': [('.layar-stok .iso-toko .zona-iso.aktif .lantai-zona { fill: var(--seg-aktif); stroke: var(--emas-garis); } @media (hover: hover) and (pointer: fine) { .layar-stok .iso-toko .zona-iso:hover .lantai-zona {',
                                                                                                                         '@media (hover: hover) and (pointer: fine) { .layar-stok .iso-toko .zona-iso.aktif .lantai-zona { fill: var(--seg-aktif); stroke: var(--emas-garis); } .layar-stok .iso-toko .zona-iso:hover .lantai-zona {')]}),
]


def main():
    if '--kontrol' in sys.argv:
        diam = []; dasar = {n for n, ok, k in periksa(baca()) if ok}
        for nama, g in KONTROL:
            try: hasil = periksa(baca(g))
            except AssertionError as e: print('KONTROL BASI ' + nama + ' — ' + str(e)); diam.append(nama); continue
            gagal = [n for n, ok, k in hasil if not ok and n in dasar]
            print(('BERBUNYI ' if gagal else 'DIAM     ') + nama + ('  → ' + gagal[0] if gagal else ''))
            if not gagal: diam.append(nama)
        print('kontrol: %d/%d berbunyi' % (len(KONTROL) - len(diam), len(KONTROL))); return 3 if diam else 0
    hasil = periksa(baca())
    for n, ok, k in hasil:
        print(('lulus  ' if ok else 'GAGAL  ') + n + ('' if ok else '  → ' + str(k)[:400]))
    lulus = sum(1 for _, ok, _ in hasil if ok); print('Safari/WebKit /baru/: %d lulus · %d gagal' % (lulus, len(hasil) - lulus))
    return 0 if lulus == len(hasil) else 1


if __name__ == '__main__':
    sys.exit(main())
