#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_bayar_bon_terkunci.py — putaran 25b Bagian C: MEMBAYAR BON DARI BULAN TERKUNCI HARUS LOLOS (rules v4 + sistem baru).
Bon yang PASTI dibayar sesudah bulannya dikunci: bon lama pemasok (tipe saldoAwal, bonTanggal 31 Jul) dan bon kedatangan 25 Agu; pelanggan yang
membayar bon lama; kasbon & utang owner (jalur sejenis). Tidak ada emulator Firestore di mesin ini (tanpa Node/Java), jadi dua lapis:

  1 · RULES (statis + model): teks firestore.rules untuk jalur-jalur ini DICOCOKKAN huruf per huruf dengan bentuk yang dimodelkan di sini; model yang sama
      menilai bentuk dokumen nyata dengan Agustus terkunci (sampaiBulan '2026-08', 26 Sep 10:00 WIB). Kalau teks rules berubah, pencocokan gagal lebih dulu
      — model tidak bisa diam-diam basi. Pembuktian di server sungguhan: Playground ★D1–★D9 (docs/uji-rules-v4.md, bagian D).
  2 · SISTEM BARU (jsc, KOTAK PASIR — nama & angka contoh): lembar bayar bon pemasok & bayar bon pelanggan membuat dokumen BARU bertanggal HARI INI,
      dan penjaga pusat (jagaKunci — yang dipakai tulisDokumen) meloloskannya walau Agustus terkunci. Kontrol di dalam skenario: bon lama BARU bertanggal
      Agustus, bayar bertanggal Agustus, dan mengubah bon lama WAJIB ditolak (membuktikan penjaganya memang menilai).
  + ASAP DATA TOKO (lokal saja, cadangan di _privat/): SEMUA bon pemasok yang masih terbuka dibayar lunas di kotak pasir dengan Agustus terkunci → tak satu
    pun ditolak. Keluaran tanpa rupiah.

    python3 alat-uji/uji_bayar_bon_terkunci.py            → N lulus · 0 gagal
    python3 alat-uji/uji_bayar_bon_terkunci.py --kontrol  → rules / sistem baru yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kunci_periode  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
JAM = "var __KINI = new Date('2026-09-26T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"

# ---------- 1 · RULES: teks yang dimodelkan (WAJIB ada persis di firestore.rules) ----------
TEKS_WAJIB = {
    'bulanNilai': "function bulanNilai(v) { return v is string && v.matches('[0-9]{4}-[0-9]{2}(-[0-9]{2})?') ? bulanDari(v) : 0; }",
    'bulanDok': "function bulanDok(d, f) { return bulanNilai(d.get(f, null)); }",
    'bulanUP (K4: HANYA saldoAwal dinilai dari bonTanggal)': "function bulanUP(d) { return d.get('tipe', '') == 'saldoAwal' ? bulanNilai(d.get('bonTanggal', null)) : bulanDok(d, 'tanggal'); }",
    'bebas (bulan berjalan / tenggang)': "function bebas(b) { return b >= bulanIni() || (b == bulanIni() - 1 && wib().day() <= tenggangMin()); }",
    'bolehBulan': "function bolehBulan(b) { return bebas(b) || !terkunci(b); }",
    'tglBaru': "function tglBaru(f) { return bolehBulan(bulanDok(request.resource.data, f)); }",
    'upBaru': "function upBaru() { return bolehBulan(bulanUP(request.resource.data)); }",
    'upUbah': "function upUbah() { return tulisUlangSama() || bolehBulan(lebihTua(bulanUP(request.resource.data), bulanUP(resource.data))); }",
}
BLOK_WAJIB = {  # koleksi → baris create (dan update bila dinilai) yang dimodelkan
    'utangPemasokMutasi': ["allow create: if owner() && upBaru();", "allow update: if owner() && upUbah();"],
    'piutangMutasi': ["allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (stafBuatTipe(['ben', 'karyawan'], 'bayar') && tglStaf('tanggal'));"],
    'kasbonMutasi': ["allow create: if owner() && tglBaru('tanggal');"],
    'utangOwnerMutasi': ["allow create: if owner() && tglBaru('tanggal');"],
    'pengeluaranHarian': ["allow create: if owner() && tglBaru('tanggal');"],
}


def blok(rules, koleksi):
    m = re.search(r'match /' + koleksi + r'/\{id\} \{(.*?)\n    \}', rules, re.S); return m.group(1) if m else ''


def periksa_rules(rules):
    out = []; ok = lambda n, c, k='': out.append(('rules · ' + n, bool(c), k))
    for n, t in TEKS_WAJIB.items(): ok('teks ' + n + ' sama dengan yang dimodelkan', t in rules, t[:90])
    for k, baris in BLOK_WAJIB.items():
        b = blok(rules, k)
        for x in baris: ok('blok ' + k + ': ' + x[:70], x in b, b[:160])
    # ---- model (mengikuti teks di atas): 26 Sep 2026 10:00 WIB, Agustus terkunci
    idx = lambda s: int(s[:4]) * 12 + int(s[5:7]) if isinstance(s, str) and re.fullmatch(r'\d{4}-\d{2}(-\d{2})?', s) else 0
    INI, HARI, SAMPAI, TENGGANG = idx('2026-09'), 26, idx('2026-08'), 3
    bebas = lambda b: b >= INI or (b == INI - 1 and HARI <= TENGGANG)
    boleh = lambda b: bebas(b) or not b <= SAMPAI
    bulanUP = lambda d: idx(d.get('bonTanggal')) if d.get('tipe', '') == 'saldoAwal' else idx(d.get('tanggal'))
    up_baru = lambda d: boleh(bulanUP(d))
    up_ubah = lambda d, lama: d == lama or boleh(min(bulanUP(d), bulanUP(lama)))
    tgl_baru = lambda d: boleh(idx(d.get('tanggal')))
    H = '2026-09-26'
    bayarRM = {'tipe': 'bayar', 'tanggal': H, 'bonTanggal': '2026-08-25', 'pemasok': 'PEMASOK CONTOH A', 'nominal': 1, 'bonId': 'b1'}
    bayarSJ = {'tipe': 'bayar', 'tanggal': H, 'bonTanggal': '2026-07-31', 'pemasok': 'PEMASOK CONTOH B', 'nominal': 1, 'bonId': 's1'}
    saldoSJ = {'tipe': 'saldoAwal', 'tanggal': '2026-08-25', 'bonTanggal': '2026-07-31', 'pemasok': 'PEMASOK CONTOH B', 'nominal': 100}
    ok('bayar bon kedatangan 25 Agu (tanggal hari ini, bonTanggal 2026-08-25), Agustus terkunci → LOLOS', up_baru(bayarRM))
    ok('bayar bon lama 31 Jul (tanggal hari ini, bonTanggal 2026-07-31), Agustus terkunci → LOLOS', up_baru(bayarSJ))
    ok('pelanggan membayar bon lama (piutangMutasi bayar, tanggal hari ini) → LOLOS', tgl_baru({'tipe': 'bayar', 'tanggal': H, 'namaPelanggan': 'Contoh', 'nominal': 1}))
    ok('kasbon kembali / utang owner dibayar / biaya admin bayar bon (tanggal hari ini) → LOLOS', all(tgl_baru({'tipe': 'bayar', 'tanggal': H}) for _ in range(3)))
    ok('KONTROL model: bon lama BARU dengan bonTanggal 25 Agu (saldoAwal) → DITOLAK', not up_baru({'tipe': 'saldoAwal', 'tanggal': H, 'bonTanggal': '2026-08-25'}))
    ok('KONTROL model: bayar bertanggal 25 Agu → DITOLAK', not up_baru(dict(bayarRM, tanggal='2026-08-25')))
    ok('KONTROL model: mengubah bon lama 31 Jul (nominal) → DITOLAK; tulis-ulang identik → LOLOS', not up_ubah(dict(saldoSJ, nominal=1), saldoSJ) and up_ubah(dict(saldoSJ), saldoSJ))
    ok('KONTROL model: pelanggan membayar dengan tanggal 20 Agu → DITOLAK', not tgl_baru({'tipe': 'bayar', 'tanggal': '2026-08-20'}))
    return out


# ---------- 2 · SISTEM BARU (jsc) ----------
KOTAK = {
    'batchMasuk': [{'id': 'b1', 'tanggal': '2026-08-25', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH A', 'caraBayar': 'utang', 'biayaBongkar': 0,
                    'merkList': [{'merk': 'Beras Contoh', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 10, 'totalKg': 500, 'hargaPerKg': 10000, 'subtotalHarga': 5000000}]}],
    'utangPemasokMutasi': [{'id': 's1', 'tanggal': '2026-08-25', 'jam': '23:00', 'tipe': 'saldoAwal', 'pemasok': 'PEMASOK CONTOH B', 'nominal': 7000000, 'bonTanggal': '2026-07-31', 'catatan': 'bon lama contoh'}],
    'penjualan': [{'id': 'j1', 'tanggal': '2026-08-12', 'jam': '10:00', 'caraBayar': 'Kredit', 'namaPelanggan': 'Pelanggan Contoh', 'jenis': 'karung', 'merkSumber': 'Beras Contoh',
                   'totalKg': 50, 'jumlahKarung': 1, 'beratKarungAcuan': 50, 'hargaTotal': 600000, 'hppTotalSaatJual': 500000, 'trxId': 't1'}],
    'piutangMutasi': [], 'kasbonMutasi': [], 'pengeluaranHarian': [], 'aturanToko': [], 'pengaturan': [], 'pelangganCatatan': [],
}
SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 400) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var kini = new Date(__KINI); var n = 5000;
var W = { tanggal: '2026-09-26', jam: '10:00', kini: '2026-09-26T03:00:00.000Z', idUnik: function () { n += 1; return n; } };
terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'kunciPeriode', sampaiBulan: '2026-08', riwayat: [{ aksi: 'kunci', bulan: '2026-08', olehUid: 'uid-owner' }] } }]);
ok('Agustus terkunci di kotak pasir', kunciSampai() === '2026-08');
var B = susunBon(kini); var bonA = B.bon.find(function (b) { return b.pemasok === 'PEMASOK CONTOH A'; }); var bonB = B.bon.find(function (b) { return b.pemasok === 'PEMASOK CONTOH B'; });
ok('daftar bon terbuka: bon kedatangan 25 Agu & bon lama 31 Jul', bonA && bonA.tanggal === '2026-08-25' && bonB && bonB.tanggal === '2026-07-31' && bonB.jenis === 'saldoAwal', J(B.bon));
function bayar(bon, dari) { return susunBayar({ pemasok: bon.pemasok, bonId: bon.id, ketik: String(bon.sisa), dari: dari || 'laci' }, W); }
[[bonA, '2026-08-25', 'kedatangan 25 Agu'], [bonB, '2026-07-31', 'bon lama 31 Jul']].forEach(function (x) {
  var r = bayar(x[0]); var d = r.dokumen ? r.dokumen[0].data : {};
  ok('bayar ' + x[2] + ': satu dokumen BARU utangPemasokMutasi tipe bayar, tanggal HARI INI, bonTanggal ' + x[1], !r.tolak && r.dokumen.length === 1 && d.tipe === 'bayar' && d.tanggal === W.tanggal && d.bonTanggal === x[1] && !dokDiCache('utangPemasokMutasi', d.id), J(r));
  var j = jagaKunci(r.dokumen || [], []);
  ok('bayar ' + x[2] + ': penjaga pusat (dipakai tulisDokumen) MELOLOSKAN walau Agustus terkunci, tanpa pemeriksaan kunci di server', !r.tolak && j === null && kpNilaiKiriman([{ koleksi: 'utangPemasokMutasi', data: d }], kunciSampai(), kini).perluGet === 0, J(j));
});
ok('KONTROL: bon lama BARU dengan bonTanggal 25 Agu (saldoAwal) DITOLAK penjaga — bonTanggal memang dinilai untuk saldoAwal', !!jagaKunci([{ koleksi: 'utangPemasokMutasi', data: { id: 777, tipe: 'saldoAwal', tanggal: W.tanggal, bonTanggal: '2026-08-25', pemasok: 'X', nominal: 1 } }], []));
ok('KONTROL: bayar bertanggal 25 Agu DITOLAK penjaga', !!jagaKunci([{ koleksi: 'utangPemasokMutasi', data: { id: 778, tipe: 'bayar', tanggal: '2026-08-25', bonTanggal: '2026-08-25', pemasok: 'X', nominal: 1 } }], []));
ok('KONTROL: mengubah bon lama 31 Jul (nominal) DITOLAK penjaga', !!jagaKunci([{ koleksi: 'utangPemasokMutasi', data: Object.assign({}, dokDiCache('utangPemasokMutasi', 's1'), { nominal: 1 }) }], []));
print(J({ lulus: lulus, gagal: gagal }));
"""
# bagian PELANGGAN — bundel kunci periode (bon-logika.js: susunBon pelanggan; bon-pemasok-logika punya susunBon sendiri, jadi dua bundel terpisah)
SKENARIO_PELANGGAN = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 400) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var kini = new Date(__KINI); var n = 6000;
var W = { tanggal: '2026-09-26', jam: '10:00', kini: '2026-09-26T03:00:00.000Z', idUnik: function () { n += 1; return n; } };
terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'kunciPeriode', sampaiBulan: '2026-08', riwayat: [{ aksi: 'kunci', bulan: '2026-08', olehUid: 'uid-owner' }] } }]);
var kunciP = kunciPelanggan('Pelanggan Contoh'); var rb = susunBayarBon(kini, kunciP, 200000, 'Tunai', '', '', W); var db = rb.dokumen ? rb.dokumen[0].data : {};
ok('pelanggan membayar bon dari nota Kredit 12 Agu: piutangMutasi BARU tipe bayar tanggal HARI INI; penjaga meloloskan', !rb.tolak && db.tipe === 'bayar' && db.tanggal === W.tanggal && jagaKunci(rb.dokumen, []) === null, J(rb));
ok('KONTROL: pembayaran pelanggan bertanggal 20 Agu DITOLAK penjaga', !!jagaKunci([{ koleksi: 'piutangMutasi', data: { id: 779, tipe: 'bayar', namaPelanggan: 'Pelanggan Contoh', nominal: 1, tanggal: '2026-08-20' } }], []));
print(J({ lulus: lulus, gagal: gagal }));
"""
ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(__KINI); var n = 900000; var W = { tanggal: '2026-09-26', jam: '10:00', kini: '2026-09-26T03:00:00.000Z', idUnik: function () { n += 1; return n; } };
terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'kunciPeriode', sampaiBulan: '2026-08', riwayat: [] } }]);
// Rp1.000 per bon: yang diuji KUNCInya, bukan cukup-tidaknya uang laci (pelunasan penuh ditolak layar kalau uang toko kurang — itu penjaga lain)
var hasil = susunBon(kini).bon.map(function (b) { var r = susunBayar({ pemasok: b.pemasok, bonId: b.id, ketik: String(Math.min(1000, b.sisa)), dari: 'laci' }, W);
  var j = r.tolak ? null : jagaKunci(r.dokumen, []); var d = r.dokumen ? r.dokumen[0].data : {};
  return { pemasok: b.pemasok, bonTanggal: b.tanggal, jenis: b.jenis, tanggalBayar: d.tanggal || '', lolos: !r.tolak && j === null && d.tanggal === W.tanggal, sebab: r.tolak ? 'layar: ' + String(r.tolak).replace(/Rp[\d.]+/g, 'Rp…') : (j && j.pesan) || '' }; });
print(JSON.stringify(hasil));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1][:1] in '{[': return None, (r.stderr or r.stdout)[:800]
    return json.loads(baris[-1]), ''


MODUL_PEMASOK = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/harga-logika.js', 'baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/belanja-logika.js']   # = uji_harga_baru


def bundel_dua():
    return bundel_baru.bundel(MODUL_PEMASOK), uji_kunci_periode.satu_lingkup(bundel_baru.bundel(uji_kunci_periode.MODUL))


def periksa_baru(js2):
    out = []
    for bagian, js, sk in (('pemasok', js2[0], SKENARIO), ('pelanggan', js2[1], SKENARIO_PELANGGAN)):
        h, e = jalan(JAM + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + sk)
        if h is None: out.append(('sistem baru (' + bagian + ') · jsc jalan', False, e)); continue
        out += [('sistem baru (' + bagian + ') · ' + x, False, '') for x in h['gagal']] + [('sistem baru (' + bagian + ') · kasus %d' % (i + 1), True, '') for i in range(h['lulus'])]
    return out


def semua(rules=None, js2=None):
    rules = rules if rules is not None else open(os.path.join(AKAR, 'firestore.rules'), encoding='utf-8').read()
    return periksa_rules(rules) + periksa_baru(js2 or bundel_dua())


if __name__ == '__main__':
    R0 = open(os.path.join(AKAR, 'firestore.rules'), encoding='utf-8').read()
    J0 = bundel_dua()
    if '--kontrol' in sys.argv:
        rusak = [
            ('rules: bon pemasok selalu dinilai dari bonTanggal (bayar bon lama ikut ditolak)', 'r', "function bulanUP(d) { return d.get('tipe', '') == 'saldoAwal' ? bulanNilai(d.get('bonTanggal', null)) : bulanDok(d, 'tanggal'); }",
             "function bulanUP(d) { return bulanNilai(d.get('bonTanggal', d.get('tanggal', null))); }"),
            ('rules: create bon pemasok dinilai seperti update (bulan tertua)', 'r', "allow create: if owner() && upBaru();", "allow create: if owner() && upUbah();"),
            ('rules: pembayaran pelanggan kasir@ lepas dari kunci', 'r', "allow create: if ((owner() || kasir()) && tglBaru('tanggal')) || (stafBuatTipe(['ben', 'karyawan'], 'bayar')", "allow create: if (owner() && tglBaru('tanggal')) || kasir() || (stafBuatTipe(['ben', 'karyawan'], 'bayar')"),
            ('sistem baru: bayar bon ditulis bertanggal bon', 'j', "const bayar = { id, tanggal: w.tanggal, jam: w.jam, tipe: 'bayar',", "const bayar = { id, tanggal: H.bon.tanggal || w.tanggal, jam: w.jam, tipe: 'bayar',"),
            ('sistem baru: penjaga menilai bonTanggal untuk semua tipe', 'j', "if (koleksi === 'utangPemasokMutasi' && d.tipe === 'saldoAwal') return kpIdx(d.bonTanggal || null);", "if (koleksi === 'utangPemasokMutasi' && d.bonTanggal) return kpIdx(d.bonTanggal || null);"),
            ('sistem baru: pembayaran pelanggan bertanggal nota lama', 'j', "const data = { id: w.idUnik(), tipe: 'bayar', namaPelanggan: b.nama, nominal: n, tanggal: w.tanggal,", "const data = { id: w.idUnik(), tipe: 'bayar', namaPelanggan: b.nama, nominal: n, tanggal: '2026-08-12',"),
            ('sistem baru: penjaga pusat tidak memeriksa kunci', 'j', "  if (N.terkunci.length) return { gagal: true, terkunci: true,", "  if (false) return { gagal: true, terkunci: true,"),
        ]
        kode = 0
        for nama, jenis, lama, baru in rusak:
            if (jenis == 'r' and lama not in R0) or (jenis == 'j' and not any(lama in j for j in J0)): print('KONTROL BASI  ' + nama); kode = 3; continue
            h = semua(rules=R0.replace(lama, baru) if jenis == 'r' else R0, js2=tuple(j.replace(lama, baru) for j in J0) if jenis == 'j' else J0); g = [x for x in h if not x[1]]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:110] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h = semua(R0, J0); g = [x for x in h if not x[1]]
    for nama, _, k in g: print('   ✗ ' + nama + (' → ' + str(k)[:200] if k else ''))
    print('BAYAR BON DARI BULAN TERKUNCI (rules statis + model, sistem baru kotak pasir): %d lulus · %d gagal' % (len(h) - len(g), len(g)))
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and not g:
        a, e = jalan(JAM + J0[0] + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if a is None: print('ASAP JATUH: ' + e); sys.exit(2)
        tolak = [x for x in a if not x['lolos']]
        print('ASAP DATA TOKO (%s): %d bon pemasok terbuka, masing-masing dibayar Rp1.000 bertanggal hari ini, Agustus terkunci → %d lolos, %d ditolak · %s' % (
            os.path.basename(cad[-1]), len(a), len(a) - len(tolak), len(tolak), '; '.join('%s bon %s%s → %s' % (x['pemasok'], x['bonTanggal'] or 'tanpa tanggal', ' (bon lama)' if x['jenis'] == 'saldoAwal' else '', 'LOLOS' if x['lolos'] else 'DITOLAK: ' + x['sebab']) for x in a)))
        if tolak: sys.exit(2)
    sys.exit(1 if g else 0)
