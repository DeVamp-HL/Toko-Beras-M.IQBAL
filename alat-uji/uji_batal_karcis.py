#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_batal_karcis.py — putaran 25b: BATALKAN KARCIS KASIR DARURAT di /baru/ (Jual › Karcis kasir) — padanan mulaiBatalkanTrx() index.html.
KOTAK PASIR (nama & angka contoh) di jsc, jam dikunci Sabtu 26 Sep 2026 10:00 WIB.

Yang dijaga:
  · BENTUK DOKUMEN SAMA dengan sistem lama: field yang DITAMBAHKAN pembatalan = persis yang ditulis mulaiBatalkanTrx() di index.html (dibaca dari
    sumbernya, bukan disalin ke sini) — dibatalkan, alasanKoreksi, dikoreksiPada, dibatalkanPada; tanpa jenis baru; baris TIDAK dihapus; field lain utuh.
    Atribusi penulis pusat = diubahOleh / diubahPerangkat / diubahPada (sama dengan simpanKeFirestore) + diubahOlehUid (identitas akun, putaran 23).
  · Bila cadangan toko ada di _privat/: dokumen pembatalan sungguhan yang ditulis sistem lama (karcis uji v4, 25 Sep) punya himpunan field yang sama.
  · Hanya catatan kasir darurat (karcis nominal, sisa karcis, tuts bernama viaDarurat, perangkat d-); alasan wajib; tidak dua kali; karcis yang sudah
    dirinci ditolak (tarik balik dulu); bulan terkunci ditolak dengan kalimat; bulan lalu yang belum dikunci boleh; kantong literan id+1 ikut dicabut.
  · Daftar "kasir darurat hari ini" memuat catatan darurat hari ini yang masih berlaku saja.
  · Sesudah dibatalkan, omzet hari itu turun sebesar karcisnya (mesin beku yang sama membaca penanda dibatalkan).

    python3 alat-uji/uji_batal_karcis.py            → N lulus · 0 gagal
    python3 alat-uji/uji_batal_karcis.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kunci_periode  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
JAM = "var __KINI = new Date('2026-09-26T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def field_sistem_lama():
    """Field yang DITAMBAHKAN mulaiBatalkanTrx() index.html ke {...p} — dibaca dari sumbernya."""
    src = open(os.path.join(AKAR, 'index.html'), encoding='utf-8').read()
    m = re.search(r'async function mulaiBatalkanTrx\(\) \{.*?simpanKeFirestore\(KOLEKSI_PENJUALAN, \{\s*\.\.\.p, (.*?)\n\s*\}\);', src, re.S)
    if not m: return None
    return sorted(set(re.findall(r'(\w+):', m.group(1))))


def cadangan_toko():
    c = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')), key=os.path.basename)
    return c[-1] if c else None


def contoh_asli():
    """Karcis uji v4 yang dibatalkan owner LEWAT SISTEM LAMA (25 Sep 18:19 WIB) — field-nya saja, tanpa nilai."""
    p = cadangan_toko()
    if not p: return None
    d = json.load(open(p, encoding='utf-8'))
    x = next((x for x in d.get('penjualan', []) if str(x.get('id', '')).startswith('1790333361985') and x.get('dibatalkan')), None)
    return sorted(x.keys()) if x else None


def jual(id, tgl, harga, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': '09:15', 'caraBayar': 'Tunai', 'jenis': 'kasir_darurat_nominal', 'namaProduk': '(tidak tercatat — kasir darurat)', 'hargaTotal': harga,
         'namaPelanggan': '', 'grupNota': id, 'oleh': '(darurat tanpa nama)', 'perangkat': 'd-contoh'}
    d.update(k); return d


KOTAK = {'penjualan': [
    jual(1001, '2026-09-26', 390000, operator='Penjaga Contoh'),
    jual(1002, '2026-09-26', 52000, jenis='kemasan', namaProduk='Beras Contoh', ukuranKemasan=5, jumlahUnit=1, totalKg=5, hppTotalSaatJual=50000, viaDarurat=True),
    jual(1003, '2026-09-26', 70000, jenis='karung', namaProduk='Beras Contoh (karung utuh)', perangkat='p-owner', oleh='Owner', merkSumber='Contoh', totalKg=50, jumlahKarung=1),
    jual(1004, '2026-09-26', 15000, dibatalkan=True, alasanKoreksi='sudah dibatalkan'),
    jual(1005, '2026-09-25', 20000),
    jual(1006, '2026-08-20', 25000),
    jual(1007, '2026-09-26', 60000, dikoreksiOleh=1008, alasanKoreksi='Dirinci jadi 1 barang'),
    jual(1008, '2026-09-26', 60000, jenis='karung', asalDarurat=True, rinciDari=1007, koreksiDari=1007, grupNota=77, dirinciPada='2026-09-26T02:00:00.000Z', perangkat='p-owner', oleh='Owner'),
    jual(1009, '2026-09-26', 18000, jenis='literan', kemasanLiteran='paperbag5l', jumlahKemasanLiteranDipakai=1, perangkat='d-contoh', namaProduk='Literan Contoh'),
    jual(1010, '2026-09-26', 9000, asalDarurat=True, rinciDari=1011, koreksiDari=1011)],
  'stokBahanLiteran': [{'id': 1010, 'tipe': 'pakai', 'jenis': 'paperbag5l', 'jumlah': 1, 'hargaTotal': 0, 'tanggal': '2026-09-26'}], 'aturanToko': []}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 400) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var W = { tanggal: '2026-09-26', jam: '10:00', kini: '2026-09-26T03:00:00.000Z', idUnik: function () { return 9999; } };
var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
function asli(id) { return ambilPenjualanSemua().find(function (p) { return String(p.id) === String(id); }); }
function tambahan(lama, baru) { return Object.keys(baru).filter(function (k) { return !(k in lama); }).sort(); }

var r = susunBatalKarcis(1001, 'salah ketik, harusnya 39.000', W); var d = r.dokumen ? r.dokumen[0].data : {}; var a = asli(1001);
ok('karcis nominal hari ini → satu dokumen penjualan, id SAMA (baris ditandai, bukan dokumen baru), tanpa hapus', !r.tolak && r.dokumen.length === 1 && r.dokumen[0].koleksi === 'penjualan' && d.id === 1001 && r.hapus.length === 0, J(r));
ok('field yang DITAMBAHKAN = persis mulaiBatalkanTrx() index.html: ' + FIELD_LAMA.join(', '), J(tambahan(a, d)) === J(FIELD_LAMA), J(tambahan(a, d)));
ok('isi penanda: dibatalkan true, alasan apa adanya, dua cap waktu sama dengan jam catat', d.dibatalkan === true && d.alasanKoreksi === 'salah ketik, harusnya 39.000' && d.dikoreksiPada === W.kini && d.dibatalkanPada === W.kini);
ok('field lama UTUH (jenis tetap kasir_darurat_nominal, nominal, tanggal, jam, perangkat, oleh, operator) — tanpa jenis baru',
  Object.keys(a).every(function (k) { return J(a[k]) === J(d[k]); }) && d.jenis === 'kasir_darurat_nominal', J(d));
var at = beriAtribusiAkun(d, OWN, { perangkat: 'Mac Contoh', kini: W.kini }, true);
ok('sesudah penulis pusat: atribusi = diubahOleh/diubahPerangkat/diubahPada (sama dengan simpanKeFirestore sistem lama) + diubahOlehUid; pencipta (oleh/perangkat) tidak ditimpa',
  J(tambahan(d, at)) === J(['diubahOleh', 'diubahOlehUid', 'diubahPada', 'diubahPerangkat']) && at.oleh === '(darurat tanpa nama)' && at.perangkat === 'd-contoh', J(tambahan(d, at)));
if (CONTOH_ASLI) {
  var kunciKita = Object.keys(at).filter(function (k) { return k !== 'diubahOlehUid'; }).sort();
  var dasarAsli = CONTOH_ASLI.filter(function (k) { return ['keteranganDarurat'].indexOf(k) < 0; });
  ok('DATA TOKO: himpunan field = pembatalan sungguhan dari sistem lama (karcis uji v4 25 Sep), selain diubahOlehUid', J(kunciKita) === J(dasarAsli), J(kunciKita) + ' vs ' + J(dasarAsli));
}
var r2 = susunBatalKarcis(1002, 'salah tuts', W);
ok('barang dari TUTS BERNAMA kasir darurat (viaDarurat) bisa dibatalkan; jenis kemasan tetap', !r2.tolak && r2.dokumen[0].data.dibatalkan === true && r2.dokumen[0].data.jenis === 'kemasan', J(r2));
ok('nota BUKAN kasir darurat ditolak (jalurnya sendiri)', /bukan catatan kasir darurat/.test(susunBatalKarcis(1003, 'x salah', W).tolak || ''));
ok('yang sudah dibatalkan tidak dibatalkan dua kali', /sudah dibatalkan/.test(susunBatalKarcis(1004, 'lagi dong', W).tolak || ''));
ok('karcis yang sudah DIRINCI ditolak — tarik balik rinciannya dulu', /tarik balik/.test(susunBatalKarcis(1007, 'salah ketik', W).tolak || ''));
ok('alasan wajib (kosong / 2 huruf ditolak)', /alasan/i.test(susunBatalKarcis(1001, '', W).tolak || '') && /alasan/i.test(susunBatalKarcis(1001, ' x ', W).tolak || ''));
ok('karcis bulan lalu (Agustus) boleh dibatalkan selama bulannya belum dikunci', !susunBatalKarcis(1006, 'salah ketik', W).tolak);
terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'kunciPeriode', sampaiBulan: '2026-08', riwayat: [] } }]);
var rk = susunBatalKarcis(1006, 'salah ketik', W);
ok('karcis bulan TERKUNCI ditolak dengan kalimat yang jelas', rk.tolak && /Agustus 2026 terkunci/.test(rk.tolak) && /tidak bisa dibatalkan lagi/.test(rk.tolak), J(rk));
ok('bulan terkunci tidak menahan karcis bulan berjalan', !susunBatalKarcis(1001, 'salah ketik', W).tolak);
var rl = susunBatalKarcis(1009, 'salah ketik', W);
ok('literan kasir darurat: kantong pasangan (id+1) ikut dicabut, sama dengan sistem lama', !rl.tolak && rl.hapus.length === 1 && rl.hapus[0].koleksi === 'stokBahanLiteran' && rl.hapus[0].id === 1010, J(rl.hapus));
ok('sisa karcis yang belum diurai (asalDarurat) = catatan kasir darurat juga → bisa dibatalkan', !susunBatalKarcis(1010, 'sisanya fiktif', W).tolak);
var H = karcisDaruratHari(new Date(__KINI)); var ids = H.map(function (x) { return x.id; });
ok('daftar "kasir darurat hari ini": karcis & tuts bernama & sisa hari ini yang berlaku — bukan yang dibatalkan/dirinci, bukan hari lain, bukan nota owner',
  ids.indexOf('1001') >= 0 && ids.indexOf('1002') >= 0 && ids.indexOf('1009') >= 0 && ids.indexOf('1010') >= 0 && ids.indexOf('1003') < 0 && ids.indexOf('1004') < 0 && ids.indexOf('1005') < 0 && ids.indexOf('1007') < 0 && ids.indexOf('1008') < 0, J(ids));
var omzetSebelum = ambilPenjualan().filter(function (p) { return p.tanggal === '2026-09-26'; }).reduce(function (s, p) { return s + p.hargaTotal; }, 0);
terapkanKeCache(r.dokumen);
var omzetSesudah = ambilPenjualan().filter(function (p) { return p.tanggal === '2026-09-26'; }).reduce(function (s, p) { return s + p.hargaTotal; }, 0);
ok('sesudah dibatalkan: omzet hari itu turun persis sebesar karcisnya; barisnya tetap ada di data (ditandai)', omzetSebelum - omzetSesudah === 390000 && !!asli(1001) && asli(1001).dibatalkan === true, omzetSebelum + ' → ' + omzetSesudah);
ok('sesudah dibatalkan: hilang dari daftar kasir darurat hari ini & tidak bisa dibatalkan lagi', karcisDaruratHari(new Date(__KINI)).every(function (x) { return x.id !== '1001'; }) && !!susunBatalKarcis(1001, 'lagi dong', W).tolak);
print(J({ lulus: lulus, gagal: gagal }));
"""


def utama(js):
    fl = field_sistem_lama()
    if not fl: return 0, ['mulaiBatalkanTrx() tidak ditemukan di index.html — pemeriksa bentuk tidak sah']
    isi = JAM + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar FIELD_LAMA = ' + json.dumps(fl) + ';\nvar CONTOH_ASLI = ' + json.dumps(contoh_asli()) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(isi); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[:800]]
    h = json.loads(baris[-1]); return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = uji_kunci_periode.satu_lingkup(bundel_baru.bundel(uji_kunci_periode.MODUL))
    if '--kontrol' in sys.argv:
        rusak = {
            'baris DIHAPUS, bukan ditandai': js.replace("  return { dokumen: [{ koleksi: 'penjualan', data }], hapus, patch: { kcBatal: null,", "  return { dokumen: [], hapus: hapus.concat([{ koleksi: 'penjualan', id: p.id }]), patch: { kcBatal: null,"),
            'penanda dibatalkan hilang (jenis baru dipakai)': js.replace("const data = Object.assign({}, p, { dibatalkan: true, alasanKoreksi:", "const data = Object.assign({}, p, { jenis: 'batal_karcis', alasanKoreksi:"),
            'field tambahan di luar bentuk sistem lama': js.replace("dikoreksiPada: kini, dibatalkanPada: kini });\n  const hapus = p.jenis", "dikoreksiPada: kini, dibatalkanPada: kini, batalDariBaru: true });\n  const hapus = p.jenis"),
            'alasan tidak wajib': js.replace("if (a.length < 3) return { tolak: 'Tulis alasannya dulu", "if (false) return { tolak: 'Tulis alasannya dulu"),
            'bulan terkunci tidak diperiksa': js.replace("const kunci = tolakKunci('penjualan', p, KC_BATAL_TERKUNCI); if (kunci) return { tolak: kunci };", ""),
            'nota bukan kasir darurat ikut bisa dibatalkan': js.replace("if (!kcDariDarurat(p)) return { tolak:", "if (false) return { tolak:"),
            'dibatalkan dua kali': js.replace("if (!penjualanMasihBerlaku(p)) return { tolak: 'Karcis ' + kcEkor(p.id) + ' sudah '", "if (false) return { tolak: 'Karcis ' + kcEkor(p.id) + ' sudah '"),
            'kantong literan tidak dicabut': js.replace("const hapus = p.jenis === 'literan' && p.kemasanLiteran ? [{ koleksi: 'stokBahanLiteran', id: p.id + 1 }] : [];", "const hapus = [];"),
            'daftar hari ini memuat yang sudah dibatalkan': js.replace("return ambilPenjualan().filter((p) => kcDariDarurat(p) && p.tanggal === hari)", "return ambilPenjualanSemua().filter((p) => kcDariDarurat(p) && p.tanggal === hari)"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    print('BATAL KARCIS DARURAT (/baru/, kotak pasir%s): %d lulus · %d gagal' % (' + contoh sungguhan dari ' + os.path.basename(cadangan_toko()) if contoh_asli() else '', l, len(g)))
    [print('   ✗ ' + x) for x in g]
    print('field yang ditambahkan sistem lama (index.html mulaiBatalkanTrx): ' + ', '.join(field_sistem_lama() or []))
    sys.exit(1 if g else 0)
