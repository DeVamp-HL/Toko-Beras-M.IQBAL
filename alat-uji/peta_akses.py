#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
peta_akses.py — PETA TULIS dari KODE (putaran 23, Tahap 0). Statis, tanpa Node.

Membaca tiap fungsi `export function susun*` / pembantu tulis di baru/js/layar/*-logika.js,
lalu mendaftar koleksi yang ditulisnya dan bentuk tulisannya:
  buat   = dokumen ber-id baru (w.idUnik(), id + 1, id bentukan) → di rules = create
  ubah   = salinan dokumen yang sudah ada (Object.assign({}, dok, …)) → di rules = update
  buat?  = tidak bisa dipastikan statis (upsert / id dari luar) → diperiksa tangan di peta
  hapus  = masuk daftar `hapus: [...]`                            → di rules = delete
  kolom  = `ubahKolom` (perbaruiKolom: update kolom tertentu saja)
Pemanggilan fungsi susun lain di badan fungsi ikut digabung (graf panggilan, satu berkas + impor).

    python3 alat-uji/peta_akses.py            → tabel markdown ke stdout
    python3 alat-uji/peta_akses.py --json     → bentuk mentah (dipakai uji_akses_baru.py)
    python3 alat-uji/peta_akses.py --baca     → koleksi yang dibaca tiap layar (lampiran B peta)
    python3 alat-uji/peta_akses.py --kiriman  → ACCESS CALL TERBURUK per jenis kiriman bukan-owner (putaran 23c, CI): fungsi ASLI dijalankan di jsc
                                                 dengan masukan terburuk di batasnya; GAGAL (keluar 2) bila ada yang > 18 (batas Firebase 20, sisa 2)
    python3 alat-uji/peta_akses.py --kiriman --kontrol → sumber yang dirusak WAJIB membuat pemeriksa gagal (keluar 3 kalau ada yang lolos)
"""
import os, re, sys, json, glob

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
LAYAR = os.path.join(AKAR, 'baru', 'js', 'layar')
KOLEKSI_WADAH = ['stokBahanKemasan', 'stokBahanLiteran']   # koleksiWadah(jenis) → salah satu dari dua ini (wadah-jual-logika.js)


def badan(teks, awal):
    """Badan fungsi dari posisi `function NAMA(` — cocokkan kurung kurawal, lompati string & komentar."""
    i = teks.index('(', awal); d = 0
    while True:   # lewati parameter (boleh berisi { } default)
        c = teks[i]
        if c == '(': d += 1
        elif c == ')':
            d -= 1
            if d == 0: break
        i += 1
    i = teks.index('{', i); mulai = i; d = 0; n = len(teks)
    while i < n:
        c = teks[i]
        if c in '\'"`':
            q = c; i += 1
            while i < n and teks[i] != q:
                if teks[i] == '\\': i += 1
                i += 1
        elif c == '/' and i + 1 < n and teks[i + 1] == '/':
            i = teks.index('\n', i)
        elif c == '/' and i + 1 < n and teks[i + 1] == '*':
            i = teks.index('*/', i) + 1
        elif c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return teks[mulai:i + 1]
        i += 1
    return teks[mulai:]


def jenis_data(potong):
    """Bentuk dokumen dari potongan teks sesudah `data:`."""
    p = potong.lstrip()
    if p.startswith('Object.assign({}, {') or p.startswith('{'):
        head = p[:160]
        if re.search(r"id:\s*(w\.idUnik\(\)|[a-zA-Z_.]+\s*\+\s*1\b|id\b|idBaru|idUnik|String\(w\.idUnik)", head) or 'idUnik' in head: return 'buat'
        return 'buat?'
    if p.startswith('Object.assign({}, '): return 'ubah'
    return 'buat?'


def pindai():
    fungsi = {}   # nama → {berkas, tulis: {(koleksi, bentuk)}, panggil: set()}
    for f in sorted(glob.glob(os.path.join(LAYAR, '*-logika.js'))):
        teks = open(f, encoding='utf-8').read(); berkas = os.path.basename(f)
        for m in re.finditer(r'(?:export\s+)?function\s+([A-Za-z_]\w*)\s*\(', teks):
            nama = m.group(1)
            try: b = badan(teks, m.start())
            except (ValueError, IndexError): continue
            tulis = set()
            for k in re.finditer(r"koleksi:\s*('(\w+)'|koleksiWadah\([^)]*\)|(\w+))", b):
                if k.group(2): kol = [k.group(2)]
                elif k.group(1).startswith('koleksiWadah'): kol = KOLEKSI_WADAH
                else: continue   # variabel: diurus lewat pemanggilan
                sesudah = b[k.end():k.end() + 400]; sebelum = b[max(0, k.start() - 120):k.start()]
                if re.match(r"\s*,\s*id:", sesudah) and 'data' not in sesudah[:30]:
                    bentuk = 'hapus' if re.search(r'hapus', sebelum + sesudah[:60]) or 'hapus' in b else 'hapus'
                else:
                    md = re.search(r'data:\s*', sesudah); bentuk = jenis_data(sesudah[md.end():]) if md else 'buat?'
                for kk in kol: tulis.add((kk, bentuk))
            if 'ubahKolom' in b:
                for k in re.finditer(r"koleksi:\s*'(\w+)',\s*id:[^}]*kolom:", b): tulis.add((k.group(1), 'kolom'))
            panggil = set(re.findall(r'\b([a-z]\w*)\s*\(', b)) - {nama}
            fungsi[nama] = {'berkas': berkas, 'tulis': tulis, 'panggil': panggil}
    # graf panggilan: gabung tulisan fungsi yang dipanggil (sampai tetap)
    ubah = True
    while ubah:
        ubah = False
        for nama, f in fungsi.items():
            for p in f['panggil']:
                if p in fungsi and not fungsi[p]['tulis'] <= f['tulis']:
                    f['tulis'] |= fungsi[p]['tulis']; ubah = True
    return {n: f for n, f in fungsi.items() if f['tulis'] and (n.startswith('susun') or n.startswith('simpan'))}


# ====================== PETA BACA: graf panggilan fungsi lintas berkas (nama unik se-bundel) ======================
JS = os.path.join(AKAR, 'baru', 'js')
LAYAR_UTAMA = ['ringkasan', 'stok', 'jual', 'pelanggan', 'harga', 'uang', 'laporan', 'menu']


def peta_koleksi():
    k = open(os.path.join(JS, 'data', 'koleksi.js'), encoding='utf-8').read()
    kol = dict((c, n) for n, c in re.findall(r"\{ nama: '(\w+)',\s*urut: '?\w*'?,\s*cache: '(\w+)'", k))
    t = open(os.path.join(JS, 'data', 'toko.js'), encoding='utf-8').read()
    ambil = {}
    for m in re.finditer(r'export function (ambil\w+)\(\)\s*\{\s*return (?:_cache\.(\w+)|(ambil\w+)\(\))', t):
        ambil[m.group(1)] = m.group(2) or ('@' + m.group(3))
    for a, c in list(ambil.items()):
        while c and c.startswith('@'): c = ambil.get(c[1:])
        ambil[a] = c
    ambil['ambilTitikKas'] = 'pengaturan'
    return kol, ambil


def fungsi_dari(teks):
    g = {}
    for m in re.finditer(r'(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)\s*\(', teks):
        try: g.setdefault(m.group(1), badan(teks, m.start()))
        except (ValueError, IndexError): pass
    for m in re.finditer(r'(?:export\s+)?const\s+([A-Za-z_]\w*)\s*=\s*(?:async\s*)?\(?[^=;\n]*\)?\s*=>', teks):
        akhir = teks.find('\n', m.end()); akhir = len(teks) if akhir < 0 else akhir
        g.setdefault(m.group(1), teks[m.end():akhir])
    return g


def modul_ui(f):
    """Berkas layar (bukan *-logika.js) — nama fungsinya LOKAL (tiap layar punya `gambar` sendiri)."""
    b = os.path.basename(f); return os.path.dirname(f).endswith('layar') and not b.endswith('-logika.js')


def graf_fungsi():
    """Graf GLOBAL: logika, mesin, data, inti — nama unik se-bundel (bundel_baru menjamin satu lingkup)."""
    g = {}
    for f in glob.glob(os.path.join(JS, '**', '*.js'), recursive=True):
        if modul_ui(f): continue
        for n, t in fungsi_dari(open(f, encoding='utf-8').read()).items(): g.setdefault(n, t)
    return g


def impor_ui(f, kunjung=None):
    """Berkas layar + modul layar lain yang diimpornya (mis. jual.js → wadah-panel.js, adegan.js)."""
    kunjung = kunjung if kunjung is not None else []
    if f in kunjung or not os.path.exists(f): return kunjung
    kunjung.append(f)
    for m in re.finditer(r"from '\./([\w-]+\.js)'", open(f, encoding='utf-8').read()):
        g = os.path.join(os.path.dirname(f), m.group(1))
        if modul_ui(g): impor_ui(g, kunjung)
    return kunjung


def baca_dari(teks_awal, g, kol, ambil, lokal=None):
    lokal = lokal or {}; kunjung, antre, baca = set(), [teks_awal], set()
    while antre:
        t = antre.pop()
        for a in re.findall(r'\b(ambil\w+)\s*\(', t):
            if ambil.get(a): baca.add(kol.get(ambil[a], ambil[a]))
        for c in re.findall(r"cacheMentah\('(\w+)'\)", t): baca.add(kol.get(c, c))
        for n in set(re.findall(r'\b([A-Za-z_]\w*)\s*\(', t)):
            if n in kunjung: continue
            badan_n = lokal.get(n, g.get(n))
            if badan_n is not None: kunjung.add(n); antre.append(badan_n)
    return baca


def baca_per_layar():
    kol, ambil = peta_koleksi(); g = graf_fungsi(); out = {}
    for l in LAYAR_UTAMA:
        f = os.path.join(JS, 'layar', l + '.js')
        if not os.path.exists(f): continue
        berkas = impor_ui(f); teks = '\n'.join(open(x, encoding='utf-8').read() for x in berkas)
        out[l] = sorted(baca_dari(teks, g, kol, ambil, fungsi_dari(teks)))
    return out, sorted(kol.values())


# ====================== KIRIMAN BUKAN-OWNER: access call terburuk (putaran 23c, owner 24 Sep) ======================
# Tiap dokumen kiriman bukan-owner memeriksa aksesAkun sekali (1 get()) + 1 baris jejak kiriman → access call = dokumen + 1 (peta §7).
# Angka di bawah BUKAN deklarasi: dihitung dari susunNotaDokumen / susunSimpanAdukan / susunBayarBon / susunOrangBaru / susunStrukKeluar
# ASLI, dan tiap kiriman dilewatkan periksaKiriman ASLI (yang bukan-owner memang tidak boleh kirim → dilewati, bukan dihitung).
BATAS_CI = 18   # batas Firebase 20 per batch − sisa 2 (keputusan owner). Sengaja TIDAK dibaca dari akses.js: menaikkan batas di sana tidak melonggarkan CI.
MODUL_KIRIM = ['baru/js/data/koleksi.js', 'baru/js/data/kunci-periode.js', 'baru/js/mesin/pembantu.js', 'baru/js/data/toko.js', 'baru/js/mesin/beku.js', 'baru/js/inti/format.js', 'baru/js/data/akses.js',
               'baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/struk-logika.js', 'baru/js/layar/jual-logika.js',
               'baru/js/layar/stok-adukan-logika.js', 'baru/js/layar/pelanggan-logika.js', 'baru/js/layar/bon-logika.js']
SUMBER_UI = ['baru/js/layar/jual.js', 'baru/js/layar/stok.js', 'baru/js/data/firebase.js']
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'

SKENARIO_KIRIM = r"""
var hasil = { baris: [], salah: [], perBaris: {}, perHasil: 0 };
function salah(t) { hasil.salah.push(t); }
var W = { tanggal: '2026-09-24', jam: '10:00', kini: '2026-09-24T03:00:00.000Z', idUnik: (function () { var n = 5000; return function () { n += 1; return n; }; })() };
var KINI = new Date(Date.now());
var AKUN = { ben: keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true }),
  karyawan: keadaanAkun('kry.contoh@tokoberasmiqbal.web.app', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true }) };
// KOTAK PASIR — angka & nama contoh, bukan data toko
pasok('pesanan', [{ id: 'ps1', namaPelanggan: 'Pembeli Contoh', status: 'dipesan', isi: 'contoh', nilai: 100000, tanggal: '2026-09-23' }]);
pasok('penjualan', [{ id: 11, trxId: 11, tanggal: '2026-09-20', jam: '09:00', caraBayar: 'Kredit', namaPelanggan: 'Pembeli Contoh', hargaTotal: 500000, jenis: 'karung', merkSumber: 'Angsa', totalKg: 50 }]);
pasok('batchMasuk', [{ id: 'b1', tanggal: '2026-09-01', merkList: [{ merk: 'Angsa', satuan: 'karung', beratKarung: 50, totalKg: 5000, subtotalHarga: 65000000, hargaPerKg: 13000 }] }]);
function kirim(peran, dok) {   // → { ac } dihitung, atau { dilewati: alasan } kalau peran ini memang tidak boleh mengirimnya
  var D = dok.map(function (x) { var ada = x.koleksi === 'pesanan'; return { koleksi: x.koleksi, data: x.data, ada: ada, lama: ada ? ambilPesananDoc(String(x.data.id)) : null }; });
  var r = periksaKiriman(AKUN[peran], D, [], {});
  if (r.tolak && !/pecah jadi dua nota/.test(r.tolak)) return { dilewati: r.tolak };
  return { ac: D.length + 1, dok: D.length, ditolakPerangkat: !!r.tolak };
}
function catat(jenis, peran, rincian, k) { if (k.dilewati) return; hasil.baris.push({ jenis: jenis, peran: peran, rincian: rincian, ac: k.ac, dok: k.dok, ditolakPerangkat: k.ditolakPerangkat }); }

// ---- 1 · NOTA: dokumen per baris diukur per jenis baris (bentuk trx = bangunBaris), lalu nota terburuk di batas baris
var BARIS = {
  'literan berkantong': function () { return { jenis: 'literan', merkSumber: 'Angsa', namaProduk: 'Angsa', jumlahLiter: 5, totalKg: 4, kemasanLiteran: 'paperbag5l', jumlahKemasanLiteranDipakai: 1, hargaTotal: 70000, hargaSatuan: 14000, hargaAsli: 14000, jumlah: 5 }; },
  'repack, wadah ditanggung toko': function () { return { jenis: 'repacking', merkSumber: 'Angsa', namaProduk: 'Angsa', totalKg: 10, kemasanRepack: '5kg_kembangbmw', jumlahKemasanRepackDipakai: 2, hargaTotal: 140000, hargaSatuan: 14000, hargaAsli: 14000, jumlah: 10 }; },
  'wadah dijual': function () { return { jenis: 'wadah', jenisWadah: '5kg_kembangbmw', jumlahUnit: 3, namaProduk: 'Kantong', hargaTotal: 6000, hargaSatuan: 2000, hargaAsli: 2000, jumlah: 3 }; },
  'karung utuh': function () { return { jenis: 'karung', merkSumber: 'Angsa', jumlahKarung: 1, totalKg: 50, hargaTotal: 690000, hargaSatuan: 690000, hargaAsli: 690000, jumlah: 1 }; },
  'kemasan': function () { return { jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, hargaTotal: 72000, hargaSatuan: 72000, hargaAsli: 72000, jumlah: 1 }; }
};
function keranjang(jenis, n) { var k = []; for (var i = 0; i < n; i++) k.push({ id: 'b' + i, trx: BARIS[jenis]() }); return k; }
var CARA = { 'tunai': { cara: 'Tunai', uang: 1e9 }, 'QRIS': { cara: 'QRIS', uang: 0 }, 'bon': { cara: 'Kredit', uang: 0 }, 'bayar sebagian (sisa jadi bon)': { cara: 'Tunai', uang: 1000 } };
var NB = BATAS_BARIS_NOTA_STAF;
Object.keys(BARIS).forEach(function (j) { hasil.perBaris[j] = susunNotaDokumen({ keranjang: keranjang(j, 1), pelanggan: 'Pembeli Contoh', cara: 'Tunai', uang: 1e9, potongan: 0 }, W).dokumen.length; });
['ben', 'karyawan'].forEach(function (p) {
  Object.keys(BARIS).forEach(function (j) { Object.keys(CARA).forEach(function (c) { [false, true].forEach(function (ps) {
    var s = { keranjang: keranjang(j, NB), pelanggan: 'Pembeli Contoh', cara: CARA[c].cara, uang: CARA[c].uang, potongan: 0, pesananId: ps ? 'ps1' : null, batasBaris: NB };
    catat('nota', p, NB + ' baris ' + j + ' · ' + c + (ps ? ' · dari pesanan' : ''), kirim(p, susunNotaDokumen(s, W).dokumen));
  }); }); });
});
// penjaga baris: tepat di batas masih muat, satu lebih → ditolak dengan kalimatnya (di tambah-baris DAN saat nota dicatat)
var sLebih = { keranjang: keranjang('literan berkantong', NB + 1), pelanggan: 'Pembeli Contoh', cara: 'Tunai', uang: 1e9, potongan: 0, batasBaris: NB };
if (alasanBatasBaris({ batasBaris: NB }, NB) !== '') salah('nota ' + NB + ' baris ditolak padahal masih di batas');
if (!/paling banyak \d+ baris/.test(alasanBatasBaris({ batasBaris: NB }, NB + 1))) salah('nota ' + (NB + 1) + ' baris TIDAK ditolak penjaga baris');
if (alasanTolak(sLebih) !== alasanBatasBaris(sLebih, NB + 1)) salah('alasanTolak tidak memakai penjaga baris (nota ' + (NB + 1) + ' baris lolos saat dicatat): ' + alasanTolak(sLebih));
if (alasanBatasBaris({ batasBaris: 0 }, 99) !== '') salah('owner (batas 0) ikut dibatasi');
// tukar (retur + karantina) bukan kiriman bukan-owner: server tidak memberi create retur
var kt = kirim('ben', susunNotaDokumen({ keranjang: keranjang('karung utuh', 1), pelanggan: 'Pembeli Contoh', cara: 'Tunai', uang: 1e9, potongan: 0 }, W).dokumen.concat([{ koleksi: 'retur', data: { id: 77 } }]));
if (!kt.dilewati) salah('nota tukar (ada retur) dihitung sebagai kiriman bukan-owner — server tidak membukanya');

// ---- 2 · ADUKAN: h hasil berkantong di batas hasil
var NH = BATAS_HASIL_ADUKAN_STAF; var YAKIN = { bahan: true, kemasan: true, kantongKosong: true, kantong: true, susut: true };
function drafAduk(n, batas) { var hs = []; for (var i = 0; i < n; i++) hs.push({ nama: 'Hasil Contoh ' + i, ukuran: '5', unit: '2', kantongJenis: '5kg_kembangbmw', kantongJumlah: '2' });
  return { tanggal: '2026-09-24', bahan: [{ merk: 'Angsa', kg: String(n * 10) }], bahanKemasan: [], hasil: hs, upah: '0', batasHasil: batas }; }
var a1 = susunSimpanAdukan(drafAduk(1, NH), W, YAKIN); hasil.perHasil = a1.dokumen ? a1.dokumen.length : -1; if (!a1.dokumen) salah('adukan 1 hasil ditolak: ' + a1.tolak);
['ben', 'karyawan'].forEach(function (p) { var a = susunSimpanAdukan(drafAduk(NH, NH), W, YAKIN); if (!a.dokumen) { salah('adukan ' + NH + ' hasil ditolak: ' + a.tolak); return; }
  catat('adukan', p, NH + ' baris hasil, semua berkantong', kirim(p, a.dokumen)); });
var aL = susunSimpanAdukan(drafAduk(NH + 1, NH), W, YAKIN);
if (!/paling banyak \d+ baris hasil/.test(aL.tolak || '')) salah('adukan ' + (NH + 1) + ' hasil TIDAK ditolak penjaga hasil');
if (!susunSimpanAdukan(drafAduk(NH + 1, 0), W, YAKIN).dokumen) salah('owner (batas 0) ikut dibatasi di adukan');

// ---- 3 · kiriman satu dokumen
['ben', 'karyawan'].forEach(function (p) {
  var bb = susunBayarBon(KINI, 'pembeli contoh', '100.000', 'Tunai', '', '', W); if (bb.tolak) salah('terima bon ditolak: ' + bb.tolak); else catat('terima bon', p, 'satu pembayaran', kirim(p, bb.dokumen));
  var ob = susunOrangBaru(KINI, 'Orang Baru Contoh', W); if (ob.tolak) salah('pelanggan baru ditolak: ' + ob.tolak); else catat('pelanggan baru', p, 'satu kartu', kirim(p, ob.dokumen));
  catat('struk', p, 'satu struk cetak/WA', kirim(p, [susunStrukKeluar({ trxId: 11, nama: 'Pembeli Contoh', total: 70000 }, 'cetak', W, '')]));
});

// ---- 4 · tiap tindakan yang DIBUKA server untuk bukan-owner wajib punya hitungan di atas
var DIHITUNG = { jualTunai: 'nota', jualBon: 'nota', terimaBon: 'terima bon', adukan: 'adukan', pelangganBaru: 'pelanggan baru' };
Object.keys(SERVER_BUKA).forEach(function (t) { if (!DIHITUNG[t] || !hasil.baris.some(function (b) { return b.jenis === DIHITUNG[t]; })) salah('tindakan "' + t + '" dibuka server untuk bukan-owner, tapi kirimannya tidak dihitung di sini'); });
hasil.batas = { kirim: BATAS_KIRIM_STAF, firebase: BATAS_ACCESS_CALL, baris: NB, hasil: NH };
print(JSON.stringify(hasil));
"""


def _bundel_teks(teks):
    import bundel_baru
    return '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL_KIRIM])


def sumber_kirim():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL_KIRIM + SUMBER_UI)


def periksa_kiriman(src):
    """→ (baris hasil, daftar cacat). src = {jalur: teks} — kontrol mengirim sumber yang dirusak."""
    import subprocess, tempfile
    sys.path.insert(0, SINI)
    cacat = []
    # (a) statis: dokumen per baris nota & per hasil adukan — tiap dokumen.push di loop per baris harus ada jenis baris yang memicunya di skenario
    jl = src['baru/js/layar/jual-logika.js']; nd = badan(jl, jl.index('export function susunNotaDokumen('))
    i = nd.index('items.forEach((t) => {'); loop = ''; d = 0; j = nd.index('{', i)
    for k in range(j, len(nd)):
        if nd[k] == '{': d += 1
        elif nd[k] == '}':
            d -= 1
            if d == 0: loop = nd[j:k + 1]; break
    push_baris = loop.count('dokumen.push(')
    sa = src['baru/js/layar/stok-adukan-logika.js']; ad = badan(sa, sa.index('export function susunSimpanAdukan('))
    push_hasil = ad[ad.index('h.sahH.forEach((x, i) => {'):].split('\n  });')[0].count('dokumen.push(')
    # (b) statis: layar menyerahkan batasnya ke logika (kalau tidak, batasnya mati dan yang tersisa cuma pagar umum "pecah jadi dua nota")
    J = src['baru/js/layar/jual.js']; S = src['baru/js/layar/stok.js']
    if "const SB = () => Object.assign({}, K.baca(), { batasBaris: batasBarisNota(opsi.akun ? opsi.akun() : null) });" not in J: cacat.append('jual.js tidak menyerahkan batas baris akun ke logika')
    for pang in ['L.simpanNota(SB())', 'L.masukkan(SB(), Number(n))', 'L.masukkan(SB())', 'L.ulangiPembelian(SB(), rakKini(), g)']:
        if pang not in J: cacat.append('jual.js: ' + pang + ' tidak ada — jalur itu melewati batas baris')
    if 'L.simpanNota(S())' in J or re.search(r'L\.masukkan\(S\(\)', J): cacat.append('jual.js masih memanggil logika nota tanpa batas baris (S() bukan SB())')
    if "A.susunSimpanAdukan(Object.assign({}, d, { batasHasil: batasHasilAdukan(opsi.akun ? opsi.akun() : null) })" not in S: cacat.append('stok.js tidak menyerahkan batas hasil adukan ke logika')
    if 'const masuk = [], lewat = [];' not in jl or 'const r = masukkan(Object.assign(sn, ' not in jl: cacat.append('ulangiPembelian tidak lagi lewat masukkan() — batas baris bisa terlewati')
    # (c) jsc: fungsi asli, masukan terburuk
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write("var __KINI = new Date('2026-09-24T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" + _bundel_teks(src) + SKENARIO_KIRIM); jalur = f.name
    r = subprocess.run([JSC, jalur], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(jalur)
    keluar = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not keluar.startswith('{'): return [], cacat + ['JSC JATUH: ' + (r.stderr or r.stdout)[:600]]
    H = json.loads(keluar); cacat += H['salah']
    dua = [j for j, n in H['perBaris'].items() if n >= 2]
    if push_baris - 1 != len(dua): cacat.append('susunNotaDokumen punya %d dokumen tambahan per baris, skenario cuma memicu %d (%s) — jenis baris baru belum dihitung' % (push_baris - 1, len(dua), ', '.join(dua)))
    if push_hasil != H['perHasil']: cacat.append('susunSimpanAdukan menulis %d dokumen per hasil, skenario mengukur %d' % (push_hasil, H['perHasil']))
    if H['batas']['kirim'] > BATAS_CI: cacat.append('pagar perangkat akses.js BATAS_KIRIM_STAF = %d, lebih dari %d' % (H['batas']['kirim'], BATAS_CI))
    for b in H['baris']:
        if b['ac'] > BATAS_CI: cacat.append('%s · %s · %s: %d access call > %d' % (b['jenis'], b['peran'], b['rincian'], b['ac'], BATAS_CI))
    return H, cacat


def terburuk(H):
    out = {}
    for b in H['baris']:
        k = (b['jenis'], b['peran'])
        if k not in out or b['ac'] > out[k]['ac']: out[k] = dict(b, sama=[b['rincian']])
        elif b['ac'] == out[k]['ac']: out[k]['sama'].append(b['rincian'])
    return out


if __name__ == '__main__':
    if '--kiriman' in sys.argv:
        S0 = sumber_kirim()
        if '--kontrol' in sys.argv:
            def rusak(p, a, b): assert a in S0[p], 'kontrol basi: ' + a[:60]; return dict(S0, **{p: S0[p].replace(a, b, 1)})
            AK = 'baru/js/data/akses.js'; JL = 'baru/js/layar/jual-logika.js'; SA = 'baru/js/layar/stok-adukan-logika.js'
            K = {
                'batas baris nota dinaikkan ke 8': rusak(AK, 'export const BATAS_BARIS_NOTA_STAF = 7;', 'export const BATAS_BARIS_NOTA_STAF = 8;'),
                'batas hasil adukan dinaikkan ke 9': rusak(AK, 'export const BATAS_HASIL_ADUKAN_STAF = 8;', 'export const BATAS_HASIL_ADUKAN_STAF = 9;'),
                'pagar perangkat dikembalikan ke 20': rusak(AK, 'export const BATAS_KIRIM_STAF = BATAS_ACCESS_CALL - CADANGAN_ACCESS_CALL;', 'export const BATAS_KIRIM_STAF = BATAS_ACCESS_CALL;'),
                'penjaga baris selalu kosong': rusak(JL, "return b > 0 && nBaris > b ?", "return false && nBaris > b ?"),
                'alasanTolak tanpa penjaga baris': rusak(JL, "const lewat = alasanBatasBaris(s, s.keranjang.length); if (lewat) return lewat;", ""),
                'baris literan menulis dokumen ketiga': rusak(JL, "    // PUTARAN 15: wadah yang DIJUAL", "    if (d.kemasanLiteran) dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: d.id + 2, tipe: 'pakai' } });\n    // PUTARAN 15: wadah yang DIJUAL"),
                'adukan tanpa penjaga hasil': rusak(SA, "if (Number(draf.batasHasil) > 0 && h.sahH.length > Number(draf.batasHasil)) return", "if (false) return"),
                'tindakan baru dibuka server tanpa hitungan': rusak(AK, "pelangganBaru: ['ben', 'karyawan'] };", "pelangganBaru: ['ben', 'karyawan'], isiUlang: ['ben'] };"),
                'jual.js mencatat nota tanpa batas baris': rusak('baru/js/layar/jual.js', 'L.simpanNota(SB())', 'L.simpanNota(S())'),
                'stok.js menyimpan adukan tanpa batas hasil': rusak('baru/js/layar/stok.js', "Object.assign({}, d, { batasHasil: batasHasilAdukan(opsi.akun ? opsi.akun() : null) })", 'd'),
            }
            kode = 0
            for nama, src in K.items():
                _, c = periksa_kiriman(src)
                print(('BERBUNYI ' if c else 'DIAM!!   ') + nama + ' → ' + (c[0][:130] if c else '-'))
                if not c: kode = 3
            sys.exit(kode)
        H, c = periksa_kiriman(S0)
        if H:
            print('Kiriman bukan-owner — access call TERBURUK (batas Firebase %d, CI gagal bila > %d; batas nota %d baris, adukan %d hasil)' % (H['batas']['firebase'], BATAS_CI, H['batas']['baris'], H['batas']['hasil']))
            print('| kiriman | peran | dokumen | access call | yang mencapainya |'); print('|---|---|---|---|---|')
            for (j, p), b in sorted(terburuk(H).items()):
                print('| %s | %s | %d | **%d / 20** | %s |' % (j, p, b['dok'], b['ac'], b['sama'][0] + (' (+%d kombinasi lain)' % (len(b['sama']) - 1) if len(b['sama']) > 1 else '')))
            print('| denyut perangkat | ben, karyawan | 1 | 1 / 20 | satu dokumen perangkatStatus, tanpa jejak |')
            print('\ndokumen per baris nota: ' + ', '.join('%s %d' % x for x in sorted(H['perBaris'].items())) + ' · per hasil adukan: %d' % H['perHasil'])
        if c: print('\nGAGAL:'); [print('   ✗ ' + x) for x in c]; sys.exit(2)
        print('\nLULUS: tidak ada kiriman bukan-owner di atas %d access call' % BATAS_CI); sys.exit(0)

    if '--baca' in sys.argv:
        B, semua = baca_per_layar()
        print('| layar | koleksi dibaca (dari %d) |' % len(semua)); print('|---|---|')
        for l, v in B.items(): print('| %s | %d: %s |' % (l, len(v), ', '.join(v)))
        tak = [k for k in semua if not any(k in v for v in B.values())]
        print('\ntidak dibaca layar mana pun:', ', '.join(tak) or '-'); sys.exit(0)
    F = pindai()
    if '--json' in sys.argv:
        print(json.dumps({n: {'berkas': f['berkas'], 'tulis': sorted(list(t) for t in f['tulis'])} for n, f in sorted(F.items())}, ensure_ascii=False, indent=1)); sys.exit(0)
    print('| berkas | fungsi | koleksi · bentuk |'); print('|---|---|---|')
    for n, f in sorted(F.items(), key=lambda x: (x[1]['berkas'], x[0])):
        per = {}
        for kol, b in sorted(f['tulis']): per.setdefault(kol, []).append(b)
        print('| %s | `%s` | %s |' % (f['berkas'].replace('-logika.js', ''), n, ' · '.join('%s %s' % (k, '/'.join(v)) for k, v in sorted(per.items()))))
    print('\n%d fungsi yang menulis' % len(F))
