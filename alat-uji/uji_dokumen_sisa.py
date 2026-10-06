#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_dokumen_sisa.py — PAKET DOKUMEN & SISA (owner 7 Okt 2026: "harus selesai semua sebelum tanggal 13"). jsc (kotak pasir, ANGKA CONTOH) + statis.

D1 PUSAT DOKUMEN — yang kurang dari visi owner 17 Sep, dibangun di Laporan › Dokumen › Dokumen kecil (pola kertas berkop yang sama: cetak/PDF/WA, bernomor):
  · DAFTAR HARGA untuk pelanggan = katalog yang SEDANG dipakai kasir (sudah terbit; draf tidak ikut, jumlah drafnya disebut), dikelompokkan per merek,
    pilihan kelompok (semua / per kg / per liter / kemasan & karung utuh) dengan jumlah harga (bukan rupiah).
  · HARGA YANG NAIK = katalog sekarang dibanding harga sebelum periode (riwayat terbit `hargaTerbit`): hanya yang naik; turun / kembali / baru diberi
    harga dihitung & disebut; barang baru yang lalu dinaikkan dibanding harga pertamanya; periode 7/30/90 hari/sejak awal tahun; riwayat yang mulai di
    dalam periode disebut; tanpa riwayat sama sekali → ditolak dengan sebabnya. Teks WA: "(+RpX)", bukan "(saldo …)".
  · kop ringkas (DOKUMEN_KOP 'harga'); paket bank: SEMUA nomor dihitung dulu (susunPaketCetakan, urut dari nomor berikut, bentuk = susunCetakan).
  · jalan pintas: Harga › WA → dokumen harga/naik; Pelanggan › lembar bon → Kartu piutang dengan nama itu terpilih (app.js meneruskan keTujuan,
    Laporan.buka menerima `pilih`); pilihan bukan-rupiah digambar teksN.
D3 SISA PENSIUN SISTEM LAMA (#103):
  · tombol bersihkan simpanan lokal sistem lama (Menu › Toko ini › Cadangan & simpanan): daftar kunci DIBEKUKAN dari tag sistem-lama-terakhir (dicocokkan
    kalau tag ada di mesin ini; di CI checkout dangkal tanpa tag → dilewati & disebut), TIDAK memuat kunci /baru/ maupun kasir darurat; antrean lama yang
    masih berisi DIJAGA sampai salinannya diunduh; dua ketukan; layar hanya membaca/menghapus kunci dari daftar itu.
  · kalimat layar yang menyuruh "lewat sistem lama" (uang, harga, pelanggan, menu, akses-kasir-logika, sistem-logika) sudah diganti jalan di /baru/ atau
    kalimat jujur.
(D2 Safari = uji_safari_webkit.py; tab Kasir & PIN = uji_operator_pin.py; 404.html = uji_csp.py & uji_pensiun_sistem_lama.py.)

    python3 alat-uji/uji_dokumen_sisa.py            → N lulus · 0 gagal
    python3 alat-uji/uji_dokumen_sisa.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob, subprocess, tempfile, copy
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_laporan_baru as UL  # noqa: E402  (kotak pasir & daftar modul laporan yang sama)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = list(dict.fromkeys(UL.MODUL + ['baru/js/data/akses.js', 'baru/js/layar/sistem-logika.js']))
LL = 'baru/js/layar/laporan-logika.js'; LAP = 'baru/js/layar/laporan.js'; SL = 'baru/js/layar/sistem-logika.js'; MENU = 'baru/js/layar/menu.js'
HARGA = 'baru/js/layar/harga.js'; PEL = 'baru/js/layar/pelanggan.js'; APP = 'baru/js/app.js'; UANG = 'baru/js/layar/uang.js'; AKP = 'baru/js/layar/akses-kasir-logika.js'
DARURAT = 'kasir-darurat-nominal.html'

# ---- KOTAK PASIR tambahan (ANGKA CONTOH): katalog terbit + riwayat terbit + satu draf + kop lengkap. Jam dikunci 19 Sep 2026 (uji_laporan_baru).
#   t1 25 Agu: Angsa/kg 14.000 → 14.200 · IR64 Apex/kg baru diberi harga 15.000
#   t2 10 Sep: Angsa/kg 14.200 → 14.500 · Angsa 5 kg 70.000 → 73.000
#   t3 15 Sep: Angsa 5 kg 73.000 → 72.000 (turun sebagian)
#   t4 18 Sep: IR64 Apex/kg 15.000 → 15.200
#   katalog sekarang: Angsa/kg 14.500 (draf 14.800 belum terbit) · Angsa 5 kg 72.000 · IR64 Apex/kg 15.200
KOTAK = copy.deepcopy(UL.KOTAK)
KOTAK['katalogHargaKarung'] = [{'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 14500}, {'id': 'IR64 Apex', 'merk': 'IR64 Apex', 'hargaPerKg': 15200}]
KOTAK['katalogHargaKemasan'] = [{'id': 'angsa_5kg', 'merk': 'Angsa', 'ukuran': 5, 'hargaPerUnit': 72000}]
KOTAK['hargaTerbit'] = [
    {'id': 101, 'tanggal': '2026-08-25', 'jam': '09:00', 'n': 2, 'daftar': [{'kunci': 'Angsa|S', 'nama': 'Angsa · Karung per kg', 'lama': 14000, 'baru': 14200}, {'kunci': 'IR64 Apex|S', 'nama': 'IR64 Apex · Karung per kg', 'lama': 0, 'baru': 15000}]},
    {'id': 102, 'tanggal': '2026-09-10', 'jam': '10:00', 'n': 2, 'daftar': [{'kunci': 'Angsa|S', 'nama': 'Angsa · Karung per kg', 'lama': 14200, 'baru': 14500}, {'kunci': 'Angsa|K5', 'nama': 'Angsa · Kemasan 5 kg', 'lama': 70000, 'baru': 73000}]},
    {'id': 103, 'tanggal': '2026-09-15', 'jam': '10:00', 'n': 1, 'daftar': [{'kunci': 'Angsa|K5', 'nama': 'Angsa · Kemasan 5 kg', 'lama': 73000, 'baru': 72000}]},
    {'id': 104, 'tanggal': '2026-09-18', 'jam': '08:00', 'n': 1, 'daftar': [{'kunci': 'IR64 Apex|S', 'nama': 'IR64 Apex · Karung per kg', 'lama': 15000, 'baru': 15200}]}]
KOTAK['aturanToko'] = [{'id': 'hargaDraf', 'tanggal': '2026-09-19', 'jam': '09:00', 'draf': {'Angsa|S': 14800}},
                       {'id': 'identitas', 'tanggal': '2026-09-19', 'jam': '09:00', 'versi': 1, 'riwayat': [], 'nama': 'Toko Contoh', 'alamat': 'Jl. Contoh 1', 'telepon': '', 'npwp': '', 'nib': '', 'slogan': '', 'gaya': 'kiri'}]
KOTAK['dokumenCetak'] = [{'id': 'dc-1', 'nomor': 4, 'jenis': 'harian', 'judul': 'Rekap harian', 'periode': '', 'cara': 'cetak', 'kopVersi': 1, 'draf': False, 'tanggal': '2026-09-18', 'jam': '20:00'}]

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var KINI = new Date(Date.now()); var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 7000; return function () { n += 1; return n; }; })() };
var nm = function (D) { return D.baris.map(function (b) { return (b.kelas === 'kel' ? '#' : '') + b.nama + (b.teks ? '=' + b.teks : '') + (b.teksSaldo ? '|' + b.teksSaldo : ''); }); };
try {
  // ==================== D1 · DAFTAR HARGA ====================
  var DH = dokumenKecil('harga', null, '', KINI);
  ok('daftar harga: katalog yang DIPAKAI kasir (draf Angsa 14.800 belum terbit TIDAK ikut), per merek (urutan katalog: kemasan lalu per kg), satuan bahasa pembeli',
     J(nm(DH)) === J(['#Angsa', 'kemasan 5 kg=Rp72.000', 'per kg=Rp14.500', '#IR64 Apex', 'per kg=Rp15.200']) && DH.judul === 'Daftar Harga' && !DH.tolak, J(nm(DH)) + ' ' + DH.tolak);
  ok('daftar harga: jumlah draf yang belum ikut disebut; kop ringkas (setelan dokumen "harga")', /1 perubahan yang masih draf belum ikut/.test(DH.identitas) && DH.ragam === 'ringkas' && DH.kop.ragam === 'ringkas' && pakaiKop().pakai.harga === 'ringkas', DH.identitas);
  ok('daftar harga: pilihan kelompok = semua · per kg · kemasan (literan kosong tidak ditawarkan), angkanya JUMLAH harga (teksN), bukan rupiah',
     J(DH.pilihan.map(function (p) { return p.id + ':' + p.teksN + ':' + p.n; })) === J(['semua:3 harga:null', 'kg:2 harga:null', 'kemasan:1 harga:null']), J(DH.pilihan));
  var DK = dokumenKecil('harga', 'kemasan', '', KINI);
  ok('daftar harga kelompok kemasan: hanya kemasan, sub menyebut kelompoknya', J(nm(DK)) === J(['#Angsa', 'kemasan 5 kg=Rp72.000']) && /kemasan & karung utuh · 1 harga/.test(DK.sub), J(nm(DK)) + ' ' + DK.sub);
  // ==================== D1 · HARGA YANG NAIK ====================
  var N30 = dokumenKecil('naik', null, '', KINI);
  ok('harga naik 30 hari (bawaan): Angsa/kg 14.000 → 14.500 (+500, naik terakhir 10 Sep) · Angsa 5 kg 70.000 → 72.000 (+2.000; turun sebagian 15 Sep tidak menghapus naiknya) · IR64 Apex baru diberi harga 15.000 lalu 15.200 (+200)',
     J(nm(N30)) === J(['#Angsa', 'kemasan 5 kg · naik 10 Sep 2026=Rp70.000 → Rp72.000|+Rp2.000', 'per kg · naik 10 Sep 2026=Rp14.000 → Rp14.500|+Rp500', '#IR64 Apex', 'per kg · naik 18 Sep 2026=Rp15.000 → Rp15.200|+Rp200']) && N30.adaSaldo && N30.saldoPolos && !N30.tolak, J(nm(N30)) + ' ' + N30.tolak);
  ok('harga naik: kalimat jujur — riwayat tercatat sejak 25 Agu (periode 30 hari mulai 21 Agu), draf tidak ikut', /Riwayat harga tercatat sejak 25 Agu/.test(N30.identitas) && /Draf belum ikut/.test(N30.identitas) && /sejak 21 Agu/.test(N30.sub), N30.identitas + ' | ' + N30.sub);
  var N7 = dokumenKecil('naik', 'h7', '', KINI);
  ok('harga naik 7 hari (sejak 13 Sep): hanya IR64 Apex 15.000 → 15.200; Angsa 5 kg TURUN (73.000 → 72.000) dihitung, tidak dicantumkan; tanpa kalimat riwayat',
     J(nm(N7)) === J(['#IR64 Apex', 'per kg · naik 18 Sep 2026=Rp15.000 → Rp15.200|+Rp200']) && /1 harga turun/.test(N7.identitas) && !/Riwayat harga tercatat/.test(N7.identitas), J(nm(N7)) + ' ' + N7.identitas);
  ok('harga naik: pilihan periode = 30 · 7 · 90 hari · sejak awal tahun dengan jumlah yang naik (teksN)', J(N30.pilihan.map(function (p) { return p.id + ':' + p.teksN; })) === J(['h30:3 naik', 'h7:1 naik', 'h90:3 naik', 'tahun:3 naik']), J(N30.pilihan));
  var TX = teksDokumen(N30, 12, '2026-09-19');
  ok('harga naik WA: "(+Rp500)" — bukan "(saldo …)" seperti kartu piutang; kop & nomor ikut', /\(\+Rp500\)/.test(TX) && !/saldo/.test(TX) && /No\. 12/.test(TX) && /TOKO CONTOH/.test(TX), TX);
  var HN = hargaNaik('2026-09-01', KINI);
  ok('hargaNaik langsung: sejak 1 Sep — Angsa/kg 14.200 → 14.500 · Angsa 5 kg 70.000 → 72.000 · IR64 Apex 15.000 → 15.200; tidak ada yang "baru"/"tetap"',
     J(HN.naik.map(function (x) { return x.k + ':' + x.awal + '>' + x.n; })) === J(['Angsa|K5:70000>72000', 'Angsa|S:14200>14500', 'IR64 Apex|S:15000>15200']) && HN.nBaru === 0 && HN.nTetap === 0 && HN.pertama === '2026-08-25' && !HN.sebelumRiwayat, J(HN));
  pasok('hargaTerbit', KOTAK.hargaTerbit.concat([{ id: 105, tanggal: '2026-09-19', jam: '09:30', n: 1, daftar: [{ kunci: 'Angsa|K5', nama: 'Angsa · Kemasan 5 kg', lama: 72000, baru: 72000 }] }]));
  var HT = hargaNaik('2026-09-19', KINI);
  ok('harga naik: terbit hari ini dengan harga sama (72.000 → 72.000) dihitung "kembali ke harga semula", tidak dicantumkan', HT.nTetap === 1 && HT.naik.length === 0 && HT.nTurun === 0, J(HT));
  pasok('hargaTerbit', []);
  var N0 = dokumenKecil('naik', null, '', KINI);
  ok('harga naik tanpa riwayat terbit sama sekali: DITOLAK dengan sebabnya (bukan kertas kosong yang seolah "tidak ada yang naik")', /Belum ada riwayat harga/.test(N0.tolak), N0.tolak);
  pasok('hargaTerbit', KOTAK.hargaTerbit);
  pasok('katalogHargaKarung', []); pasok('katalogHargaKemasan', []);
  ok('daftar harga tanpa satu pun harga terbit: DITOLAK dengan arahan ke Katalog', /Belum ada harga yang terbit/.test(dokumenKecil('harga', null, '', KINI).tolak), dokumenKecil('harga', null, '', KINI).tolak);
  pasok('katalogHargaKarung', KOTAK.katalogHargaKarung); pasok('katalogHargaKemasan', KOTAK.katalogHargaKemasan);
  // ==================== D1/D2 · PAKET BANK: nomor dihitung dulu ====================
  var PK = susunPaketCetakan([{ jenis: 'labarugi', judul: 'Laporan Laba-Rugi', periode: 'Jul – Sep 26' }, { jenis: 'neraca', judul: 'Laporan Neraca', periode: 'Sep 2026' }, { jenis: 'omzet', judul: 'Rekap Omzet Bulanan', periode: '12 bulan' }], W);
  var C1 = susunCetakan({ jenis: 'labarugi', judul: 'Laporan Laba-Rugi', periode: 'Jul – Sep 26' }, 'pdf', W);
  ok('paket bank: nomor urut dari nomor berikut (cetakan terakhir No. 4 → 5, 6, 7), satu dokumenCetak per kertas, bentuk = susunCetakan (cara pdf)',
     PK.nomor === 5 && PK.nomorAkhir === 7 && J(PK.dokumen.map(function (d) { return d.data.nomor; })) === J([5, 6, 7]) && PK.dokumen.every(function (d) { return d.koleksi === 'dokumenCetak' && d.data.cara === 'pdf' && J(Object.keys(d.data)) === J(Object.keys(C1.dokumen[0].data)); })
     && PK.dokumen[2].data.jenis === 'omzet' && new Set(PK.dokumen.map(function (d) { return d.data.id; })).size === 3, J(PK));
  ok('paket bank kosong ditolak', !!susunPaketCetakan([], W).tolak);
  // ==================== D3 · SISA SIMPANAN SISTEM LAMA ====================
  var ISI = { miqbal_penjualan_v1: '\u0001LZ' + new Array(3001).join('x'), miqbal_antrean_tunda_v1: '[{"koleksi":"penjualan"},{"koleksi":"retur"}]', kasir_antrean_v1: '[]', kasir_gagal_v1: 'rusak{',
    miqbal_baru_antre_v1: '[1,2,3]', kasir_auth_v1: '{"u":1}', kasir_ringkasan_v1: '{}', miqbal_titik_kas_v1: '{}', miqbal_perangkat_v1: 'p-1', miqbal_jenis_beras_v1: '{}', darurat_antrean_v1: '[1]' };
  var L1 = ssSimpananLama(ISI, false);
  ok('sisa sistem lama: hanya kunci dari daftar beku — kunci /baru/, titik kas, perangkat, jenis beras & kasir darurat TIDAK terbaca walau ada',
     J(L1.ada.map(function (x) { return x.kunci; }).sort()) === J(['kasir_antrean_v1', 'kasir_gagal_v1', 'miqbal_antrean_tunda_v1', 'miqbal_penjualan_v1']), J(L1.ada));
  ok('antrean lama yang masih berisi (2 catatan) & yang tidak terbaca (dianggap berisi) DIJAGA sebelum salinan diunduh; antrean kosong & cache ikut dibersihkan',
     J(L1.dibersihkan.slice().sort()) === J(['kasir_antrean_v1', 'miqbal_penjualan_v1']) && L1.nCatatan === 3 && L1.dijaga.length === 2 && L1.kbBersih > 5 && L1.kb > L1.kbBersih, J([L1.dibersihkan, L1.nCatatan, L1.kb, L1.kbBersih]));
  var L2 = ssSimpananLama(ISI, true);
  ok('sesudah salinan diunduh: semua sisa sistem lama boleh dibersihkan (tetap hanya kunci daftar beku)', J(L2.dibersihkan.slice().sort()) === J(['kasir_antrean_v1', 'kasir_gagal_v1', 'miqbal_antrean_tunda_v1', 'miqbal_penjualan_v1']) && L2.dijaga.length === 0, J(L2.dibersihkan));
  ok('tanpa sisa: kalimatnya bilang tidak ada', ssSimpananLama({}, false).ada.length === 0 && /Tidak ada sisa/.test(ssSimpananLama({}, false).teks));
  var CD = ssCadangan(KINI, { lsKb: 4300, lamaKb: 3900 }); var CD0 = ssCadangan(KINI, { lsKb: 300, lamaKb: 0 });
  ok('kuota: kalimatnya menyebut sisa sistem lama yang TIDAK bertambah lagi (bukan ramalan "hari lagi penuh"); peringatan menunjuk tombol bersihkan, bukan "Setelan sistem lama"',
     /3\.900 KB di antaranya sisa sistem lama/.test(CD.kuota.ket) && !/hari lagi penuh/.test(CD.kuota.ket) && /bersihkan sisa sistem lama dengan tombol di bawah/.test(CD.kuota.awasTeks) && !/Setelan sistem lama/.test(CD.kuota.awasTeks) && /tidak ada lagi sisa sistem lama/.test(CD0.kuota.ket), J([CD.kuota.ket, CD.kuota.awasTeks, CD0.kuota.ket]));
} catch (e) { gagal.push('JATUH: ' + (e && (e.stack || e.message) || e)); }
print(J({ lulus: lulus, gagal: gagal }));
"""


def baca(ganti=None):
    t = {}
    for p in sorted(glob.glob(os.path.join(AKAR, 'baru/js/**/*.js'), recursive=True)) + [os.path.join(AKAR, 'baru/index.html'), os.path.join(AKAR, DARURAT)]:
        t[os.path.relpath(p, AKAR)] = open(p, encoding='utf-8').read()
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def jalan_jsc(t):
    js = '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL])
    isi = UL.JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(isi); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(baris[-1]); return h['lulus'], h['gagal']


def kunci_lama(t):
    m = re.search(r'export const SS_KUNCI_LAMA = \[(.*?)\];', t[SL], re.S)
    return re.findall(r"'([^']+)'", m.group(1)) if m else []


def kunci_baru(t):
    """Kunci simpanan yang dipakai /baru/: literal 'miqbal_…' di baru/js (kecuali daftar beku sistem lama itu sendiri) & script sebaris index.html."""
    out = set()
    for b, isi in t.items():
        if not (b.startswith('baru/js/') or b == 'baru/index.html'): continue
        if b == SL: isi = re.sub(r'export const SS_KUNCI_LAMA = \[.*?\];|export const SS_KUNCI_LAMA_ANTREAN = \[.*?\];', '', isi, flags=re.S)
        isi = re.sub(r'^\s*//.*$', '', isi, flags=re.M)
        out |= set(re.findall(r"""['"`](miqbal_[A-Za-z0-9_]+)['"`]""", isi))
    return out


def kunci_darurat(t):
    return set(re.findall(r"""['"`]((?:miqbal|kasir|darurat)_[A-Za-z0-9_]+)['"`]""", t[DARURAT])) - {'kasir_darurat_nominal'}


def kunci_tag():
    """Kunci simpanan sistem lama dari tag git sistem-lama-terakhir (index.html & kasir.html) — None kalau tag tidak ada (CI: checkout dangkal)."""
    out = set()
    for b in ('index.html', 'kasir.html'):
        r = subprocess.run(['git', '-C', AKAR, 'show', 'sistem-lama-terakhir:' + b], capture_output=True, text=True)
        if r.returncode != 0: return None
        out |= set(re.findall(r"""['"`]((?:miqbal|kasir)_[A-Za-z0-9_]+)['"`]""", r.stdout))
    return out - {'kasir_darurat_nominal'}


def potong(teks, pola):
    m = re.search(pola, teks, re.S | re.M); return m.group(0) if m else ''


def periksa_statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    # ---- D1 jalan pintas & gambar
    lap = t[LAP]
    ok('laporan.js: pilihan dokumen kecil yang bukan rupiah digambar teksN (jumlah harga / jumlah naik), sisanya tetap rupiah', "${p.teksN !== undefined ? p.teksN : RP(p.n)}" in lap)
    ok('laporan.js: buka(dokumen, { jenis, pilih }) memilih nama/periode yang dibawa (kartu piutang dari Pelanggan)', "if (t && t.jenis && t.pilih && keluarga === 'dokumen') set({ pilihK: Object.assign({}, st().pilihK, { [t.jenis]: t.pilih })" in lap)
    ok('harga.js: lembar WA punya jalan ke kertas berkop Daftar harga & Harga yang naik (Laporan › Dokumen)', "opsi.keTujuan({ ke: 'laporan', keluarga: 'dokumen', jenis: jenis === 'naik' ? 'naik' : 'harga' })" in t[HARGA]
       and 'data-aksi="hgKertas" data-jenis="harga"' in t[HARGA] and 'data-aksi="hgKertas" data-jenis="naik"' in t[HARGA])
    ok('pelanggan.js: lembar bon → Kartu piutang dengan nama itu terpilih; app.js meneruskan keTujuan ke Pelanggan',
       "opsi.keTujuan({ ke: 'laporan', keluarga: 'dokumen', jenis: 'piutang', pilih: kunci })" in t[PEL] and 'data-aksi="kartuPiutang" data-kunci="${O.kunci}"' in t[PEL]
       and re.search(r"const pelanggan = pasangLayarPelanggan\([^;]*keTujuan: \(t\) => keTujuan\(t\)", t[APP], re.S))
    ok("laporan-logika.js: JENIS_KECIL memuat 'harga' & 'naik'; DOKUMEN_KOP memuat 'harga' (ringkas)", "['harga', 'Daftar harga'," in t[LL] and "['naik', 'Harga yang naik'," in t[LL] and "['harga', 'Daftar harga & harga yang naik', 'ringkas']" in t[LL])
    # ---- D3 daftar kunci sistem lama
    KL = kunci_lama(t); KB = kunci_baru(t); KD = kunci_darurat(t)
    ok('daftar kunci sistem lama terbaca (' + str(len(KL)) + ' kunci), tanpa kembar', len(KL) >= 40 and len(KL) == len(set(KL)), KL[:5])
    ok('daftar kunci sistem lama TIDAK memuat kunci yang dipakai /baru/ (nomor & nama perangkat, titik kas, jenis beras, miqbal_baru_* …)', not (set(KL) & KB), sorted(set(KL) & KB))
    ok('daftar kunci sistem lama TIDAK memuat kunci kasir darurat (akun, operator, katalog HP kasir, antrean darurat …)', not (set(KL) & KD), sorted(set(KL) & KD))
    tag = kunci_tag()
    if tag is None:
        ok('daftar kunci = kunci sistem lama di tag sistem-lama-terakhir dikurangi /baru/ & kasir darurat — DILEWATI (tag tidak ada di checkout ini)', True)
    else:
        harap = tag - KB - KD
        ok('daftar kunci = kunci sistem lama di tag sistem-lama-terakhir (index.html & kasir.html) dikurangi /baru/ & kasir darurat (' + str(len(harap)) + ')', set(KL) == harap,
           {'kurang': sorted(harap - set(KL)), 'lebih': sorted(set(KL) - harap)})
    mn = t[MENU]
    ok('menu.js: layar hanya membaca kunci dari daftar beku (bacaLama → S.SS_KUNCI_LAMA)', "const bacaLama = () => { const o = {}; S.SS_KUNCI_LAMA.forEach((k) => { try { o[k] = localStorage.getItem(k); }" in mn)
    bersih = potong(mn, r"^    lamaBersih: \(\) => \{.*?ukurSimpanan\(\); \},$")
    i_yakin = bersih.find("if (st().yakinBuang !== 'lama') return set("); i_hapus = bersih.find('localStorage.removeItem(')
    ok('menu.js: BERSIHKAN = dua ketukan; yang dihapus hanya L.dibersihkan dari S.ssSimpananLama(bacaLama(), …)',
       bool(bersih) and 0 <= i_yakin < i_hapus and 'const L = S.ssSimpananLama(bacaLama(), st().lamaDiunduh);' in bersih and 'L.dibersihkan.forEach((k) => { try { localStorage.removeItem(k);' in bersih
       and bersih.count('localStorage.removeItem(') == 1, bersih[:200])
    ok('menu.js: unduh salinan menandai lamaDiunduh (antrean lama berisi baru boleh dibersihkan sesudahnya)', "set({ lamaDiunduh: true," in mn and 'data-aksi="lamaUnduh"' in mn and 'data-aksi="lamaBersih"' in mn)
    # ---- D3 kalimat layar "lewat sistem lama"
    LARANG = [r'lewat sistem lama', r'bereskan di sistem lama', r'tetap di sistem lama', r'Setelan sistem lama', r'bon pemasok \(sistem lama\)', r'gembok sistem lama',
              r'karcis darurat belum dirinci[^<]{0,12}\(sistem lama\)', r'kasir sistem lama', r'yang dicatat di sistem lama', r'sistem lama & baru', r'minta Claude']
    temu = []
    for b in (UANG, HARGA, PEL, MENU, AKP, SL, LAP):
        isi = re.sub(r'^\s*//.*$', '', t[b], flags=re.M)
        for pola in LARANG:
            for m in re.finditer(pola, isi): temu.append(b.split('/')[-1] + ':' + str(isi[:m.start()].count('\n') + 1) + ' «' + m.group(0) + '»')
    ok('kalimat layar tidak lagi menyuruh lewat sistem lama / minta Claude (uang, harga, pelanggan, menu, akses-kasir-logika, sistem-logika, laporan)', not temu, temu)
    return out


def semua(ganti=None, bagian=('statis', 'jsc')):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        l, g = jalan_jsc(t); out += [('jsc · ' + x, False, '') for x in g] + [('__jsc', not g, l)]
    return out


KONTROL = [
    ('daftar harga memakai harga draf', {LL: [("const semua = S.baris.filter((b) => b.lamaN > 0).map((b) => ({ k: b.k, merk: b.merk, satuan: lpSatuanPembeli(b.st), kelompok: lpKelompokHarga(b.st), n: b.lamaN, draf: b.adaDraf }));",
                                            "const semua = S.baris.filter((b) => b.n > 0).map((b) => ({ k: b.k, merk: b.merk, satuan: lpSatuanPembeli(b.st), kelompok: lpKelompokHarga(b.st), n: b.n, draf: b.adaDraf }));")]}, ('jsc',)),
    ('harga naik: harga sebelum diambil dari terbit TERAKHIR (bukan pertama) di periode', {LL: [("const baru0 = !(E[0].lama > 0); const awal = baru0 ? E[0].baru : E[0].lama;", "const baru0 = !(E[E.length - 1].lama > 0); const awal = baru0 ? E[E.length - 1].baru : E[E.length - 1].lama;")]}, ('jsc',)),
    ('harga naik: yang turun ikut dicantumkan', {LL: [("    if (b.n > awal) { const nk", "    if (b.n !== awal) { const nk")]}, ('jsc',)),
    ('harga naik: barang yang baru diberi harga lalu dinaikkan dibuang (dianggap "baru")', {LL: [("const awal = baru0 ? E[0].baru : E[0].lama;", "const awal = baru0 ? 0 : E[0].lama;")]}, ('jsc',)),
    ('harga naik: periode tidak menyaring tanggal (semua riwayat ikut)', {LL: [("T.forEach((t) => { if (String(t.tanggal || '') < sejak) return;", "T.forEach((t) => {")]}, ('jsc',)),
    ('harga naik: tanpa riwayat tidak ditolak (kertas kosong seolah "tidak ada yang naik")', {LL: [("saldoPolos = true; if (!X.pertama) tolak =", "saldoPolos = true; if (false) tolak =")]}, ('jsc',)),
    ('harga naik: kalimat riwayat yang mulai di dalam periode hilang', {LL: [("(X.sebelumRiwayat ? ' Riwayat harga tercatat sejak '", "(false ? ' Riwayat harga tercatat sejak '")]}, ('jsc',)),
    ('harga naik WA kembali menyebut "saldo"', {LL: [("(D.saldoPolos ? '  (' + b.teksSaldo + ')' : '  (saldo ' + b.teksSaldo + ')')", "'  (saldo ' + b.teksSaldo + ')'")]}, ('jsc',)),
    ('daftar harga: jumlah draf yang belum ikut tidak disebut', {LL: [("(H.nDraf ? '; ' + H.nDraf + ' perubahan yang masih draf belum ikut' : '')", "''")]}, ('jsc',)),
    ('paket bank: semua kertas memakai nomor yang sama', {LL: [("r.dokumen[0].data.nomor = awal + i;", "r.dokumen[0].data.nomor = awal;")]}, ('jsc',)),
    ('sisa lama: antrean berisi ikut dibersihkan sebelum salinan diunduh', {SL: [("const dijaga = ada.filter((x) => x.antrean && x.n > 0 && !sudahUnduh);", "const dijaga = [];")]}, ('jsc',)),
    ('sisa lama: antrean yang tidak terbaca dianggap kosong', {SL: [("} catch (e) { n = s.trim() ? 1 : 0; } }", "} catch (e) { n = 0; } }")]}, ('jsc',)),
    ('sisa lama: kunci titik kas masuk daftar (titik kas /baru/ ikut terhapus)', {SL: [("'miqbal_tukar_setengah_v1', 'miqbal_tutup_hari_v1',", "'miqbal_tukar_setengah_v1', 'miqbal_titik_kas_v1', 'miqbal_tutup_hari_v1',")]}, ('statis', 'jsc')),
    ('sisa lama: kunci akun kasir darurat masuk daftar', {SL: [("'kasir_antrean_v1', 'kasir_bayar_bon_v1',", "'kasir_antrean_v1', 'kasir_auth_v1', 'kasir_bayar_bon_v1',")]}, ('statis', 'jsc')),
    ('sisa lama: satu kunci sistem lama hilang dari daftar (sisanya tidak pernah dibersihkan)', {SL: [("'miqbal_penjualan_v1', ", "")]}, ('statis', 'jsc')),
    ('kuota: kembali meramal "hari lagi penuh" padahal sistem lama sudah pensiun', {SL: [("ket: lsKb === null ? '' : L.lamaKb > 0 ?", "ket: lsKb === null ? '' : true ? 'hari lagi penuh' : L.lamaKb > 0 ?")]}, ('jsc',)),
    ('menu: BERSIHKAN tanpa ketukan kedua', {MENU: [("      if (st().yakinBuang !== 'lama') return set(", "      if (false) return set(")]}, ('statis',)),
    ('menu: layar membaca seluruh localStorage, bukan hanya daftar beku', {MENU: [("S.SS_KUNCI_LAMA.forEach((k) => { try { o[k] = localStorage.getItem(k); }", "Object.keys(localStorage).forEach((k) => { try { o[k] = localStorage.getItem(k); }")]}, ('statis',)),
    ('laporan: pilihan bukan rupiah digambar sebagai rupiah lagi', {LAP: [("${p.teksN !== undefined ? p.teksN : RP(p.n)}", "${RP(p.n)}")]}, ('statis',)),
    ('laporan: buka() mengabaikan nama yang dibawa', {LAP: [("if (t && t.jenis && t.pilih && keluarga === 'dokumen') set({ pilihK: Object.assign({}, st().pilihK, { [t.jenis]: t.pilih }), kabar: '' }); ", "")]}, ('statis',)),
    ('app.js: Pelanggan tanpa keTujuan (tombol kartu piutang tidak tampil)', {APP: [("statusRingkas, pindah: (t) => pindah(t),\n  keTujuan: (t) => keTujuan(t) });   // owner 7 Okt: lembar bon", "statusRingkas, pindah: (t) => pindah(t) });   // owner 7 Okt: lembar bon")]}, ('statis',)),
    ('uang: kalimat "hapus lewat sistem lama" kembali', {UANG: [("Sistem baru belum punya tombol menghapus uang keluar yang lebih lama dari 90 detik", "kalau salah, hapus lewat sistem lama")]}, ('statis',)),
    ('menu: "bayar bon pemasok tetap di sistem lama" kembali', {MENU: [("bayar bon pemasok di Harga & Pemasok → Bon pemasok, bayar pelanggan", "bayar bon pemasok tetap di sistem lama, bayar pelanggan")]}, ('statis',)),
    ('sistem: "bersihkan dari Setelan sistem lama" kembali', {SL: [("bersihkan sisa sistem lama dengan tombol di bawah' :", "bersihkan cadangan lokalnya dari Setelan sistem lama' :")]}, ('statis', 'jsc')),
    ('pelanggan: "kasir sistem lama" kembali', {PEL: [("jadi tetap dikenali di Jual.'", "jadi tetap dikenal di kasir sistem lama.'")]}, ('statis',)),
]


if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        diam = []; dasar = {x[0] for x in semua() if x[1]}
        for nama, ganti, bagian in KONTROL:
            try: h = semua(ganti, bagian)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' · ' + str(e)[:160]); diam.append(nama); continue
            g = [x for x in h if not x[1] and (x[0] in dasar or x[0].startswith('jsc · '))]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:140] if g else '-'))
            if not g: diam.append(nama)
        print('kontrol: %d/%d berbunyi' % (len(KONTROL) - len(diam), len(KONTROL))); sys.exit(3 if diam else 0)
    h = semua(); g = [x for x in h if not x[1]]
    n = sum(1 for x in h if x[1] and x[0] != '__jsc') + next((x[2] for x in h if x[0] == '__jsc'), 0)
    for x in h:
        if x[0].startswith('statis · ') and x[1] and 'DILEWATI' in x[0]: print('   · ' + x[0])
    for x in g: print('   ✗ ' + x[0] + (' → ' + json.dumps(x[2], ensure_ascii=False)[:400] if x[2] not in ('', None) else ''))
    print('DOKUMEN & SISA (owner 7 Okt): %d lulus · %d gagal' % (n, len(g)))
    sys.exit(1 if g else 0)
