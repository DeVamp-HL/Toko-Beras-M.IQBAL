#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_cap_langganan.py — CAP LANGGANAN (owner 26 Nov 2026, paket QR kedua: "adakan aja dulu"). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  CH hitung: satu NOTA atas nama pelanggan sejak tanggal mulai = satu cap (baris senota tidak dihitung dua kali), nota dibatalkan / sebelum mulai / orang lain /
     di bawah belanja minimal tidak dihitung, tiap `penuh` cap = satu hadiah, hadiah yang ditandai (capDitukar) mengurangi yang tersedia, belum dimulai = null.
  ST setelan: bawaan belum dimulai, simpan cap menulis dokumen setelan pelanggan UTUH (kolom lain tetap), penuh di luar 2–100 ditolak, hentikan = mulai kosong,
     simpan Atur pelanggan yang lain TIDAK menghapus setelan cap.
  NT nota: tanda "hadiah cap diberikan" (capTukar) menulis capDitukar di baris nota bernama saja; ganti pembeli melepas tandanya; kalimat lembar Bayar & struk.

    python3 alat-uji/uji_cap_langganan.py            → N lulus · 0 gagal
    python3 alat-uji/uji_cap_langganan.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_faktur  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
CG = 'baru/js/layar/cap-logika.js'; JL = 'baru/js/layar/jual-logika.js'; PL = 'baru/js/layar/pelanggan-logika.js'; STL = 'baru/js/layar/struk-logika.js'
MODUL = bundel_baru.lengkapi([m for m in uji_faktur.MODUL if m != CG] + [CG])
SUMBER = {'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'jual': 'baru/js/layar/jual.js', 'pelanggan': 'baru/js/layar/pelanggan.js', 'rules': 'firestore.rules'}
JAM = "var __KINI = new Date('2026-11-28T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(i, tgl, nama, trx, n, **x):
    d = {'id': i, 'tanggal': tgl, 'jam': '09:00', 'caraBayar': 'Tunai', 'namaPelanggan': nama, 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 10, 'hargaTotal': n,
         'hppTotalSaatJual': round(n * 0.9), 'trxId': trx}
    d.update(x); return d


KOTAK = {
    'penjualan': [
        jual(101, '2026-10-30', 'Bu Sari', 's0', 100000),                                          # sebelum mulai
        jual(102, '2026-11-01', 'Bu Sari', 's1', 60000), jual(103, '2026-11-01', 'Bu Sari', 's1', 40000),   # satu nota dua baris = 1 cap
        jual(104, '2026-11-05', 'bu sari ', 's2', 80000),                                          # ejaan nama lain, orang yang sama
        jual(105, '2026-11-08', 'Bu Sari', 's3', 20000),                                           # di bawah minimal bila minRp 50.000
        jual(106, '2026-11-10', 'Bu Sari', 's4', 90000, dibatalkan=True),                          # dibatalkan
        jual(107, '2026-11-12', 'Bu Sari', 's5', 75000, capDitukar=1),                             # hadiah diberikan di nota ini
        jual(108, '2026-11-15', 'Pak Budi', 'b1', 75000),
        jual(109, '2026-11-20', '', 'k1', 75000),
    ],
    'piutangMutasi': [], 'pelangganCatatan': [{'id': 'bu sari', 'nama': 'Bu Sari', 'catatan': 'warung'}],
    'aturanToko': [{'id': 'pelanggan', 'tagihHari': 9, 'hariTagih': 2, 'cap': {'mulai': '2026-11-01', 'minRp': 0, 'penuh': 2, 'hadiah': 'potongan Rp5.000'}}],
}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); };
var nId = 900000; var W = { tanggal: '2026-11-28', jam: '10:00', kini: '2026-11-28T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var K0 = JSON.parse(J(KOTAK)); Object.keys(K0).forEach(function (n) { pasok(n, K0[n]); }); setelSumber('cadangan', 'kotak pasir');
var atur = function (cap) { pasok('aturanToko', [Object.assign({}, K0.aturanToko[0], { cap: cap })]); };

// ==================== CH · HITUNG ====================
var C = capHitung('Bu Sari');
ok('CH: nota sejak mulai, per NOTA (s1 dua baris = 1), ejaan nama lain ikut, dibatalkan & sebelum mulai tidak: s1 s2 s3 s5 = 4 cap', C && C.n === 4, J(C));
ok('CH: penuh 2 → 2 hadiah diraih, 1 sudah ditandai diberikan (s5) → tersedia 1; putaran sekarang 0/2', C.dapat === 2 && C.ditukar === 1 && C.tersedia === 1 && C.menuju === 0 && C.penuh === 2 && C.hadiah === 'potongan Rp5.000', J(C));
ok('CH: orang lain & nota tanpa nama tidak ikut; tanpa nama → null', capHitung('Pak Budi').n === 1 && capHitung('') === null && capHitung(null) === null);
atur({ mulai: '2026-11-01', minRp: 50000, penuh: 2, hadiah: '' });
ok('CH: belanja minimal 50.000 → nota s3 (20.000) tidak dapat cap → 3 cap', capHitung('Bu Sari').n === 3, J(capHitung('Bu Sari')));
atur({ mulai: '', minRp: 0, penuh: 10, hadiah: '' });
ok('CH: belum dimulai → null (tidak tampil di mana pun)', capHitung('Bu Sari') === null);
atur(null); ok('ST: bawaan = belum dimulai, penuh 10, minimal 0', J(capAtur()) === J({ mulai: '', minRp: 0, penuh: 10, hadiah: '' }) && capHitung('Bu Sari') === null, J(capAtur()));
atur({ mulai: 'kemarin', minRp: -5, penuh: 1, hadiah: 'x' }); ok('ST: setelan rusak diabaikan → bawaan (tanggal tak terbaca = belum dimulai)', capAtur().mulai === '' && capAtur().minRp === 0 && capAtur().penuh === 10);
pasok('aturanToko', JSON.parse(J(KOTAK.aturanToko)));

// ==================== kalimat ====================
var C2 = capHitung('Bu Sari');
ok('teks: kartu / struk menyebut putaran & hadiah yang belum diberikan', capTeks(C2) === 'Cap langganan 0/2 · 1 hadiah belum diberikan (potongan Rp5.000)', capTeks(C2));
ok('teks: lembar Bayar — nota ini jadi 1/2', capTeksBayar(C2, 50000) === 'Cap Bu Sari: 0/2 → nota ini jadi 1/2', capTeksBayar(C2, 50000));
var C3 = Object.assign({}, C2, { n: 5, menuju: 1 });
ok('teks: lembar Bayar — nota yang memenuhkan cap disebut CAP PENUH', /nota ini jadi 2\/2 — CAP PENUH, dapat hadiah/.test(capTeksBayar(C3, 50000)), capTeksBayar(C3, 50000));
atur({ mulai: '2026-11-01', minRp: 50000, penuh: 2, hadiah: '' });
ok('teks: nota di bawah minimal disebut tidak dapat cap', /belum dapat cap \(belanja minimal Rp ?50\.000\)/.test(capTeksBayar(capHitung('Bu Sari'), 20000)), capTeksBayar(capHitung('Bu Sari'), 20000));
pasok('aturanToko', JSON.parse(J(KOTAK.aturanToko)));

// ==================== ST · SETELAN ====================
var S1 = susunAturCap({ minRp: '25.000', penuh: '8', hadiah: ' beras 1 kg ' }, W); var d1 = S1.dokumen && S1.dokumen[0].data;
ok('ST: simpan cap = dokumen setelan pelanggan UTUH (kolom lain tetap) + cap; mulai tetap', d1 && d1.id === 'pelanggan' && d1.tagihHari === 9 && d1.hariTagih === 2 && J(d1.cap) === J({ mulai: '2026-11-01', minRp: 25000, penuh: 8, hadiah: 'beras 1 kg' }), J(d1));
ok('ST: cap penuh di luar 2–100 DITOLAK', !!susunAturCap({ penuh: '1' }, W).tolak && !!susunAturCap({ penuh: '101' }, W).tolak && !susunAturCap({ penuh: '100' }, W).tolak);
ok('ST: hentikan = mulai kosong (cap lain tetap tersimpan)', susunAturCap({ mulai: '' }, W).dokumen[0].data.cap.mulai === '' && /dihentikan/.test(susunAturCap({ mulai: '' }, W).patch.kabar));
ok('ST: mulai baru', susunAturCap({ mulai: '2026-12-01' }, W).dokumen[0].data.cap.mulai === '2026-12-01' && !!susunAturCap({ mulai: '1 Des' }, W).tolak);
var AP = susunAturPelanggan({ tagihHari: '10' }, W); var dp = AP.dokumen && AP.dokumen[0].data;
ok('ST: SIMPAN ATURAN pelanggan yang lain tidak menghapus setelan cap', dp && dp.tagihHari === 10 && J(dp.cap) === J(KOTAK.aturanToko[0].cap), J(dp && dp.cap));
atur(null); var AP2 = susunAturPelanggan({}, W); ok('ST: tanpa setelan cap → dokumen tanpa kolom cap (bukan cap kosong / undefined)', !('cap' in AP2.dokumen[0].data));
pasok('aturanToko', JSON.parse(J(KOTAK.aturanToko)));

// ==================== NT · NOTA ====================
var item = { jenis: 'kemasan', namaProduk: 'Uji', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, hargaTotal: 70000, hppTotalSaatJual: 60000, label: 'Uji 5 kg', satuan: 'kemasan', jumlah: 1, hargaSatuan: 70000, hargaAsli: 70000 };
var sN = Object.assign(keadaanAwal(), { keranjang: [{ id: 'b1', trx: item }], pelanggan: 'Bu Sari', cara: 'QRIS', capTukar: true, sekarang: new Date('2026-11-28T10:00:00+07:00') });
var N1 = susunNotaDokumen(sN, W); var pj = (N1.dokumen || []).filter(function (x) { return x.koleksi === 'penjualan'; }).map(function (x) { return x.data; });
ok('NT: tanda hadiah → baris nota bernama membawa capDitukar 1', pj.length === 1 && pj[0].capDitukar === 1, J(N1.tolak || pj));
var N2 = susunNotaDokumen(Object.assign({}, sN, { capTukar: false }), W); ok('NT: tanpa tanda → tanpa kolom', N2.dokumen.filter(function (x) { return x.koleksi === 'penjualan'; }).every(function (x) { return !('capDitukar' in x.data); }));
var N3 = susunNotaDokumen(Object.assign({}, sN, { pelanggan: '' }), W); ok('NT: nota tanpa nama tidak pernah membawa capDitukar', N3.dokumen.filter(function (x) { return x.koleksi === 'penjualan'; }).every(function (x) { return !('capDitukar' in x.data); }));
ok('NT: ganti pembeli melepas tanda hadiah; keadaan awal tanpa tanda', gantiPelanggan(sN, 'Pak Budi').capTukar === false && keadaanAwal().capTukar === false);
terapkanKeCache(N1.dokumen); var C4 = capHitung('Bu Sari');
ok('NT: sesudah nota bertanda tercatat → cap +1, hadiah diberikan +1, tersedia 0', C4.n === 5 && C4.ditukar === 2 && C4.tersedia === 0, J(C4));
ok('NT: struk menulis baris cap pembeli bernama (saat struk disusun)', (function () { var n = notaDari({ trxId: pj[0].trxId }); var st = susunStruk(n, stAtur(), { kini: '2026-11-28' }); return st.teks.indexOf('Cap langganan 1/2') >= 0; })());
atur({ mulai: '', minRp: 0, penuh: 10, hadiah: '' });
ok('NT: cap belum dimulai → struk tanpa baris cap', (function () { var n = notaDari({ trxId: pj[0].trxId }); return susunStruk(n, stAtur(), { kini: '2026-11-28' }).teks.indexOf('Cap langganan') < 0; })());
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

RUSAK = [
    ('hitung: per baris, bukan per nota', CG, "const g = kunciNota(p); const x = per[g] || (per[g] = { total: 0, ditukar: 0 });", "const g = String(p.id); const x = per[g] || (per[g] = { total: 0, ditukar: 0 });"),
    ('hitung: nota sebelum mulai ikut', CG, " || String(p.tanggal || '') < S.mulai ||", " ||"),
    ('hitung: belanja minimal diabaikan', CG, "x.total > 0 && x.total >= S.minRp", "x.total > 0"),
    ('hitung: hadiah yang diberikan tidak mengurangi', CG, "tersedia: Math.max(0, dapat - ditukar)", "tersedia: dapat"),
    ('setelan: simpan cap menghapus kolom setelan lain', CG, "const data = Object.assign({}, d || { id: 'pelanggan' }, {", "const data = Object.assign({}, { id: 'pelanggan' }, {"),
    ('setelan: simpan Atur menghapus cap', PL, "am && am.cap && typeof am.cap === 'object' ? { cap: am.cap } : {})", "{})"),
    ('nota: tanda hadiah tidak ditulis', JL, "    if (s.capTukar && nama) d.capDitukar = 1;", "    if (false) d.capDitukar = 1;"),
    ('nota: tanda hadiah ditulis di nota tanpa nama', JL, "    if (s.capTukar && nama) d.capDitukar = 1;", "    if (s.capTukar) d.capDitukar = 1;"),
    ('nota: ganti pembeli tidak melepas tanda', JL, "const patch = { pelanggan: nm, capTukar: false };", "const patch = { pelanggan: nm };"),
    ('struk: baris cap hilang', STL, "if (nota.nama && nota.berlaku) { const C = capHitung(nota.nama); if (C) baris(capTeks(C), '', { jenis: 'catatan' }); }", ""),
]
STATIS = [
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_cap_langganan.py && python3 alat-uji/uji_cap_langganan.py --kontrol']),
    ('BACA-DULU menyebut cap langganan', 'baca', ['Cap langganan', 'capHitung', 'capDitukar']),
    ('Jual: kalimat cap & tanda hadiah di lembar Bayar; tanda hanya bila ada hadiah', 'jual', ['data-k="cap-bayar"', 'data-aksi="capTandai"', "if (!s.capTukar && !(C && C.tersedia > 0)) return set("]),
    ('Pelanggan: setelan cap di Atur & baris cap di kartu', 'pelanggan', ['${gambarAturCap(s)}', 'data-aksi="capSimpan"', 'data-aksi="capHenti"', 'data-k="kartu-cap"']),
]
RUSAK_STATIS = [
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_cap_langganan.py', 'true'),
    ('Jual: tanda hadiah tanpa syarat', 'jual', "if (!s.capTukar && !(C && C.tersedia > 0)) return set(", "if (false) return set("),
]


def bundel(teks):
    return bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)


def jalan(teks):
    js = JAM + bundel(teks) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO
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
    if 'capDitukar' in src['rules']: g.append('rules disentuh — cap langganan sengaja tanpa rules baru')
    return len(STATIS) - len(g), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


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
        print('KONTROL ' + ('LULUS' if kode == 0 else 'GAGAL'))
        sys.exit(kode)
    h, e = jalan(teks); ls, gs = statis(src)
    g = e if h is None else h['gagal']
    print('KOTAK PASIR: %d lulus · %d gagal' % (0 if h is None else h['lulus'], len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    sys.exit(1 if g or gs else 0)
