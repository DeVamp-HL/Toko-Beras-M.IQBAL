#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_pindai_struk.py — QR SATU PINTU bagian B (owner 26 Nov 2026): struk di-scan di tablet → keadaan nota MENURUT DATA TOKO (pindai-logika.js). KOTAK PASIR
(nama & angka CONTOH, bukan angka toko), jsc saja, TANPA peramban. Jam dikunci Sabtu 28 Nov 2026 10:00 WIB.
  KN keadaan: berlaku / dibatalkan / dikoreksi, tanggal & umur, total yang tercatat, retur yang sudah terjadi (notaAsalId), lunas saat beli.
  BN bon: sisa nota ini = pembagian buku bon (pnNota, menutup ke mesin) · faktur = sisa fakturnya · nota yang sudah tertutup · tanpa nama = tidak ada bon;
     isian bayar: orang, faktur terpilih, nominal HANYA bila jelas (faktur, atau bon eceran yang memang tertua — bayar bon menutup yang tertua dulu).
  SJ surat jalan: keadaan antar & uang bayar di tempat yang belum pulang.
  ST setelan struk: nomor WhatsApp toko dibakukan (0858… → 62…), salah ketik ditolak, kosong = QR lama.

    python3 alat-uji/uji_pindai_struk.py            → N lulus · 0 gagal
    python3 alat-uji/uji_pindai_struk.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_faktur  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
PD = 'baru/js/layar/pindai-logika.js'; STL = 'baru/js/layar/struk-logika.js'
MODUL = bundel_baru.lengkapi([m for m in uji_faktur.MODUL] + [PD])
SUMBER = {'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'rules': 'firestore.rules'}
JAM = "var __KINI = new Date('2026-11-28T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(i, tgl, cara, nama, trx, n, **x):
    d = {'id': i, 'tanggal': tgl, 'jam': '09:00', 'caraBayar': cara, 'namaPelanggan': nama, 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 10, 'hargaTotal': n,
         'hppTotalSaatJual': round(n * 0.9), 'trxId': trx}
    d.update(x); return d


KOTAK = {
    'penjualan': [
        jual(102, '2026-10-20', 'Kredit', 'Bu Sari', 'a1', 200000), jual(103, '2026-10-20', 'Kredit', 'Bu Sari', 'a1', 100000),
        jual(104, '2026-11-10', 'Kredit', 'Bu Sari', 'a2', 200000), jual(105, '2026-11-20', 'Kredit', 'Bu Sari', 'a3', 150000),
        jual(106, '2026-11-25', 'Tunai', 'Pak Budi', 't1', 90000),
        jual(107, '2026-11-26', 'Tunai', 'Pak Budi', 'x1', 45000, dibatalkan=True, dibatalkanPada='2026-11-26T03:00:00.000Z'),
        jual(108, '2026-11-26', 'Kredit', 'Bu Sari', 'x2', 70000, dibatalkan=True, dibatalkanPada='2026-11-26T04:00:00.000Z'),
        jual(109, '2026-11-27', 'Kredit', 'Warung Contoh', 'f1', 500000, noFaktur='F26-TES-0001', jatuhTempo='2026-12-27', tempoHari=30),
        jual(110, '2026-08-15', 'Tunai', 'Warung Contoh', 'f0', 500000), jual(111, '2026-10-15', 'Tunai', 'Warung Contoh', 'f9', 500000),
        jual(112, '2026-11-27', 'Kredit', 'Pak Budi', 'd1', 120000, noSJ='SJ26-AB-0001', bayarDiTempat=True),
        jual(113, '2026-11-28', 'Kredit', '', 'k1', 30000),
    ],
    'piutangMutasi': [
        {'id': 201, 'tanggal': '2026-11-12', 'jam': '10:00', 'tipe': 'bayar', 'namaPelanggan': 'Bu Sari', 'nominal': 350000, 'caraBayar': 'Tunai'},
    ],
    'retur': [{'id': 301, 'tanggal': '2026-11-26', 'jam': '11:00', 'notaAsalId': '106', 'namaPelanggan': 'Pak Budi', 'nominalRefund': 9000}],
    'suratJalan': [{'id': 'sj1', 'noSJ': 'SJ26-AB-0001', 'trxIdJual': 'd1', 'namaPelanggan': 'Pak Budi', 'tanggal': '2026-11-27', 'jam': '09:00', 'status': 'diterima',
                    'bayarDiTempat': True, 'tagihRp': 120000, 'isi': [], 'riwayatStatus': [{'status': 'berangkat'}, {'status': 'diterima'}]}],
    'pelangganCatatan': [{'id': 'bu sari', 'nama': 'Bu Sari', 'catatan': 'warung gang masjid'}, {'id': 'pak budi', 'nama': 'Pak Budi', 'catatan': 'tukang'},
                         {'id': 'warung contoh', 'nama': 'Warung Contoh', 'catatan': 'usaha'}],
    'aturanToko': [],
}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); };
var KINI = new Date('2026-11-28T10:00:00+07:00'); var nId = 900000;
var W = { tanggal: '2026-11-28', jam: '10:00', kini: '2026-11-28T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var K0 = JSON.parse(J(KOTAK)); Object.keys(K0).forEach(function (n) { pasok(n, K0[n]); }); setelSumber('cadangan', 'kotak pasir');
var K = function (trx) { return spKeadaanNota(notaDari({ trxId: trx }), KINI); };
var ada = function (k, re) { return k && k.baris.some(function (t) { return re.test(t); }); };

// ==================== KN · KEADAAN ====================
ok('KN: umur nota dalam kata', spUmurKata('2026-11-28', '2026-11-28') === 'hari ini' && spUmurKata('2026-11-27', '2026-11-28') === 'kemarin' && spUmurKata('2026-11-10', '2026-11-28') === '18 hari lalu' && spUmurKata('', '2026-11-28') === '');
var T1 = K('t1');
ok('KN: nota tunai berlaku = ASLI & masih berlaku, dibeli + umur + nama, total menurut data', T1 && T1.status === 'berlaku' && !T1.awas && /NOTA ASLI/.test(T1.judul) && ada(T1, /^Dibeli .*09:00 \(3 hari lalu\) · Pak Budi$/) && ada(T1, /Total menurut data toko Rp ?90\.000/), J(T1));
ok('KN: lunas saat beli disebut; tidak ada isian bayar', ada(T1, /^Dibayar Tunai saat beli$/) && T1.bayar === null && T1.bon === null, J(T1));
ok('KN: retur yang sudah terjadi dari nota ini disebut (1 kali, tanggalnya)', T1.retur === 1 && ada(T1, /Sudah 1 kali retur dari nota ini · terakhir .*26/), J(T1.baris));
var X1 = K('x1');
ok('KN: nota DIBATALKAN = awas, tidak berlaku, kertasnya tidak bisa dipakai; tanpa isian bayar', X1 && X1.status === 'batal' && X1.awas && /DIBATALKAN/.test(X1.judul) && ada(X1, /tidak bisa dipakai untuk retur atau tagihan/) && X1.bayar === null, J(X1));
ok('KN: retur nota lain tidak ikut terhitung', X1.retur === 0 && K('a2').retur === 0);
var X2 = K('x2');
ok('KN: nota BON yang dibatalkan tidak menawarkan bayar walau orangnya masih punya bon (bonnya sudah dicabut pembatalan)', X2 && X2.status === 'batal' && X2.bayar === null && X2.bon === null && !ada(X2, /^Bon nota ini/), J(X2));
ok('KN: tanpa nota → null', spKeadaanNota(null, KINI) === null);

// ==================== BN · BON ====================
var A2 = K('a2'), A3 = K('a3'), A1 = K('a1');
ok('BN: Bu Sari bayar 350.000 menutup nota 20 Okt + 50.000 nota 10 Nov → nota 10 Nov sisa 150.000, semua bon 300.000', A2.bon && A2.bon.sisaNota === 150000 && A2.bon.sisaOrang === 300000 && ada(A2, /^Bon nota ini: sisa Rp ?150\.000 · LEWAT jatuh tempo 4 hari · semua bon Bu Sari Rp ?300\.000$/), J(A2));
ok('BN: lewat jatuh tempo = awas', A2.awas === true && A3.awas === false, J([A2.awas, A3.awas]));
ok('BN: nota TERTUA → isian bayar terisi sisa nota itu (bayar menutup yang tertua dulu)', A2.bon.tertua && A2.bayar && A2.bayar.orang === 'bu sari' && A2.bayar.nominal === '150000' && J(A2.bayar.faktur) === '[]' && /^Scan struk nota No\. /.test(A2.bayar.catatan), J(A2.bayar));
ok('BN: nota BUKAN tertua → nominal kosong + kalimat sebabnya', !A3.bon.tertua && A3.bayar && A3.bayar.nominal === '' && ada(A3, /menutup nota TERTUA dulu/), J(A3));
ok('BN: nota yang sudah tertutup disebut tertutup (bukan "lunas dibayar"), bon lain orangnya disebut, tetap bisa bayar bon lain', A1.bon.sisaNota === 0 && ada(A1, /^Bon nota ini sudah tertutup · Bu Sari masih punya bon lain Rp ?300\.000$/) && A1.bayar && A1.bayar.nominal === '', J(A1));
var F1 = K('f1');
ok('BN: faktur → sisa FAKTURNYA, faktur terpilih, nominal = sisa faktur', F1.bon.faktur === 'F26-TES-0001' && ada(F1, /^Faktur F26-TES-0001: sisa Rp ?500\.000/) && J(F1.bayar.faktur) === '["F26-TES-0001"]' && F1.bayar.nominal === '500000' && F1.bayar.orang === 'warung contoh', J(F1));
var Kt = K('k1');
ok('BN: nota bon tanpa nama pembeli → tidak ada bon yang bisa dibayar dari sini', ada(Kt, /tanpa nama pembeli/) && Kt.bayar === null, J(Kt));
// pembayaran baru masuk → keadaan dihitung ulang (ingatan per versi data)
terapkanKeCache([{ koleksi: 'piutangMutasi', data: { id: 202, tanggal: '2026-11-28', jam: '09:30', tipe: 'bayar', namaPelanggan: 'Bu Sari', nominal: 150000, caraBayar: 'Tunai' } }]);
var A2b = K('a2'), A3b = K('a3');
ok('BN: sesudah pembayaran 150.000 nota 10 Nov tertutup, nota 20 Nov jadi yang tertua (nominal terisi)', A2b.bon.sisaNota === 0 && A3b.bon.tertua && A3b.bayar.nominal === '150000', J([A2b.bon, A3b.bayar]));

// ==================== SJ · SURAT JALAN ====================
var D1 = K('d1');
ok('SJ: nota diantar menyebut surat jalan, keadaannya, dan uang bayar di tempat yang belum pulang (awas)', ada(D1, /^Diantar · surat jalan SJ26-AB-0001 · diterima · uang bayar di tempat belum pulang Rp ?120\.000$/) && D1.awas, J(D1));

// ==================== ST · SETELAN STRUK ====================
var S1 = susunAturStruk({ kop: { nama: 'Toko Contoh', wa: '0812 0000 1111' }, kertas: 80, oto: { cetak: 'tidak', wa: 'tidak' } }, W);
ok('ST: nomor WA toko disimpan dalam bentuk wa.me', S1.dokumen && S1.dokumen[0].data.kop.wa === '6281200001111', J(S1));
ok('ST: nomor WA salah ketik DITOLAK dengan kalimat (tidak disimpan diam-diam)', /Nomor WhatsApp toko "abc" tidak dikenali/.test(String(susunAturStruk({ kop: { nama: 'Toko Contoh', wa: 'abc' }, kertas: 80, oto: { cetak: 'tidak', wa: 'tidak' } }, W).tolak)));
ok('ST: nomor WA kosong boleh (QR lama)', susunAturStruk({ kop: { nama: 'Toko Contoh', wa: '' }, kertas: 80, oto: { cetak: 'tidak', wa: 'tidak' } }, W).dokumen[0].data.kop.wa === '');
terapkanKeCache(S1.dokumen);
ok('ST: tersimpan → terbaca stAtur (kop.wa) → QR struk ber-WA', stAtur().kop.wa === '6281200001111' && tkQrStruk(notaDari({ trxId: 't1' }), { wa: stAtur().kop.wa, no: stNoNota(notaDari({ trxId: 't1' })), tgl: '2026-11-25' }).indexOf('https://wa.me/6281200001111?text=') === 0, stAtur().kop.wa);
ok('ST: bawaan tanpa setelan = kosong', (function () { pasok('aturanToko', []); return stAtur().kop.wa === ''; })());
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

RUSAK = [
    ('bayar: nominal diisi walau nota bukan yang tertua', PD, "sisaNota > 0 && tertua ? String(Math.min(sisaNota, sisaOrang)) : ''", "sisaNota > 0 ? String(Math.min(sisaNota, sisaOrang)) : ''"),
    ('bayar: faktur diabaikan', PD, "const fBuka = F && F.sisa > 0.5 ? F : null;", "const fBuka = null;"),
    ('retur: semua retur dihitung milik nota ini', PD, "&& ids.has(String(r.notaAsalId)))", ")"),
    ('keadaan: nota batal dianggap berlaku', PD, "const status = nota.berlaku ? 'berlaku' : nota.dibatalkan ? 'batal' : 'koreksi';", "const status = 'berlaku';"),
    ('surat jalan: uang bayar di tempat belum pulang tidak awas', PD, "    if (K && K.sisaTagih > 0 && K.status !== 'berangkat') awas = true;\n", ""),
    ('bon: lewat jatuh tempo tidak awas', PD, "      if (lewat) awas = true;\n", ""),
    ('bayar: nota batal tetap menawarkan bayar', PD, "else if (status === 'berlaku' && kunciPelanggan(nota.nama)) {", "else if (kunciPelanggan(nota.nama)) {"),
    ('bon: sisa nota memakai sisa semua bon', PD, "const sisaNota = x ? Math.round(x.sisa) : 0;", "const sisaNota = b ? Math.round(b.sisa) : 0;"),
    ('ingatan: keadaan tidak dihitung ulang sesudah data berubah', PD, "return ingatPerVersi('spKeadaan|' + kunci + '|' + iso, () => spHitung(nota, iso, kini || new Date()));", "if (!spKeadaanNota._i) spKeadaanNota._i = {}; return spKeadaanNota._i[kunci] || (spKeadaanNota._i[kunci] = spHitung(nota, iso, kini || new Date()));"),
    ('setelan: nomor WA disimpan apa adanya', STL, "const wa = waKetik ? tkWaNomor(waKetik) : '';", "const wa = waKetik;"),
    ('setelan: nomor WA salah ketik diterima', STL, "  if (waKetik && !wa) return { tolak:", "  if (false) return { tolak:"),
]
STATIS = [
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_pindai_struk.py && python3 alat-uji/uji_pindai_struk.py --kontrol']),
    ('BACA-DULU menyebut QR satu pintu', 'baca', ['QR satu pintu', 'spKeadaanNota', 'tkQrStruk', 'tkQrSJ', 'MIQ:J:']),
]
RUSAK_STATIS = [
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_pindai_struk.py', 'true'),
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
    if 'tkWaNomor' in src['rules'] or 'MIQ:J' in src['rules']: g.append('rules disentuh — paket ini sengaja tanpa rules baru')
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
