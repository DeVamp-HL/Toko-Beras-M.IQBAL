#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_jam_tampil.py — JAM YANG TAMPIL di sistem baru (/baru/): rinci karcis & cap waktu (perbaikan 27 Sep 2026). KOTAK PASIR — angka & id contoh.

Aturan owner: tiap baris rincian membawa JAM KARCIS ASLI (saat penjualan terjadi di kasir), jam merinci terpisah (dirinciPada); jam yang tampil WIB,
bukan UTC. Bagian jsc dijalankan DUA KALI — TZ=Asia/Jakarta dan TZ=UTC — dan di WIB ada "gigi": cara lama (memotong string ISO) dibuktikan
meleset, supaya uji ini tidak hijau palsu di runner yang zonanya UTC.
  · jamSetempat / waktuSetempat (inti/format.js): cap waktu ISO → jam dinding setempat; 00.00–06.59 WIB bertanggal hari WIB; kosong/cacat → ''
  · Rincian hari ini (karcis-logika riwayatRinci): jam & tanggal = KARCIS ASLI; jamRinci = dirinciPada setempat; hari = hari WIB; urut menurut
    kapan dirinci (bukan jam karcis)
  · PENJAGA STATIS: tidak ada kode /baru/js yang memotong string ISO jadi jam tampilan (slice(11, 16), slice(0, 16).replace('T', ' '), substr(11, 5))
  · periksa_jam_rinci.py (laporan cadangan, tidak menulis): pola benar / jam merinci WIB / jam merinci UTC / geser 7 jam / kosong / karcis hilang;
    bulan terkunci → tidak diusulkan dikoreksi
Baris rincian yang DITULIS (susunRinciDokumen: jam = jam karcis, sisa ikut) dijaga uji_jual_baru.py (+ kontrolnya).

    python3 alat-uji/uji_jam_tampil.py            → N lulus · 0 gagal (keluar 1 bila ada yang gagal)
    python3 alat-uji/uji_jam_tampil.py --kontrol  → tiap kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, subprocess, tempfile

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru          # noqa: E402
import periksa_jam_rinci    # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/struk-logika.js',
                                  'baru/js/layar/jual-logika.js', 'baru/js/layar/karcis-logika.js']
ZONA = ['Asia/Jakarta', 'UTC']

SKENARIO = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push('[' + TZ + '] ' + nama + (ket !== undefined ? ' → ' + ket : '')); }
var WIB = TZ === 'Asia/Jakarta';
var ISO = '2026-09-25T15:41:08.012Z';     // 22:41 WIB
var MALAM = '2026-09-25T18:30:00.000Z';   // 26 Sep 01:30 WIB — tanggal UTC-nya masih 25 Sep
var PAGI = '2026-09-25T02:00:00.000Z';    // 09:00 WIB
// ---- penampil cap waktu
ok('jamSetempat: ISO → jam dinding setempat', jamSetempat(ISO) === (WIB ? '22:41' : '15:41'), jamSetempat(ISO));
ok('waktuSetempat: ISO → tanggal & jam setempat', waktuSetempat(ISO) === (WIB ? '25 Sep 2026 22:41' : '25 Sep 2026 15:41'), waktuSetempat(ISO));
ok('00.00–06.59 WIB bertanggal HARI WIB, bukan tanggal UTC kemarin', waktuSetempat(MALAM) === (WIB ? '26 Sep 2026 01:30' : '25 Sep 2026 18:30'), waktuSetempat(MALAM));
ok('kosong / cacat → kosong, tidak melempar', jamSetempat('') === '' && jamSetempat(null) === '' && jamSetempat('bukan waktu') === '' && waktuSetempat(undefined) === '');
if (WIB) ok('GIGI: cara lama (memotong string ISO) memang meleset 7 jam di WIB — uji ini tidak hijau palsu', ISO.slice(11, 16) === '15:41' && jamSetempat(ISO) === '22:41');
// ---- Rincian hari ini: 3 grup contoh
pasok('penjualan', [
  { id: 'k9', tanggal: '2026-09-24', jam: '16:33', jenis: 'kasir_darurat_nominal', hargaTotal: 100000, caraBayar: 'Tunai', dikoreksiOleh: 9001 },
  { id: 9001, tanggal: '2026-09-24', jam: '16:33', jenis: 'literan', merkSumber: 'Angsa', totalLiter: 5, hargaTotal: 67500, caraBayar: 'Tunai', grupNota: 'g1', asalDarurat: true, rinciDari: 'k9', koreksiDari: 'k9', dirinciPada: ISO },
  { id: 9002, tanggal: '2026-09-24', jam: '16:33', jenis: 'kasir_darurat_nominal', hargaTotal: 32500, caraBayar: 'Tunai', grupNota: 'g1', asalDarurat: true, rinciDari: 'k9', koreksiDari: 'k9', dirinciPada: ISO },
  { id: 'k8', tanggal: '2026-09-25', jam: '08:05', jenis: 'kasir_darurat_nominal', hargaTotal: 50000, caraBayar: 'Tunai', dikoreksiOleh: 9101 },
  { id: 9101, tanggal: '2026-09-25', jam: '08:05', jenis: 'literan', merkSumber: 'Angsa', totalLiter: 4, hargaTotal: 50000, caraBayar: 'Tunai', grupNota: 'g2', asalDarurat: true, rinciDari: 'k8', koreksiDari: 'k8', dirinciPada: MALAM },
  { id: 'k7', tanggal: '2026-09-24', jam: '23:10', jenis: 'kasir_darurat_nominal', hargaTotal: 27000, caraBayar: 'Tunai', dikoreksiOleh: 9201 },
  { id: 9201, tanggal: '2026-09-24', jam: '23:10', jenis: 'literan', merkSumber: 'Angsa', totalLiter: 2, hargaTotal: 27000, caraBayar: 'Tunai', grupNota: 'g3', asalDarurat: true, rinciDari: 'k7', koreksiDari: 'k7', dirinciPada: PAGI }]);
setelSumber('cadangan', 'kotak pasir');
var hari = hariIniIso(new Date(ISO));
var R = riwayatRinci(hari); var g1 = R.find(function (r) { return r.grupNota === 'g1'; });
ok('Rincian hari ini: jam & tanggal = KARCIS ASLI (24 Sep 16:33), bukan jam merinci', !!g1 && g1.jam === '16:33' && g1.tanggal === '2026-09-24', JSON.stringify(g1));
ok('Rincian hari ini: jamRinci = jam merinci setempat', !!g1 && g1.jamRinci === (WIB ? '22:41' : '15:41'), g1 && g1.jamRinci);
ok('Rincian hari ini: grup berisi 2 baris, total 100.000, utuh', !!g1 && g1.n === 2 && g1.total === 100000 && g1.utuh === true, JSON.stringify(g1));
var hariMalam = WIB ? '2026-09-26' : '2026-09-25';
var g2 = riwayatRinci(hariMalam).find(function (r) { return r.grupNota === 'g2'; });
ok('rincian lewat tengah malam masuk hari setempatnya; jam karcis 08:05 tetap', !!g2 && g2.jam === '08:05' && g2.jamRinci === (WIB ? '01:30' : '18:30'), JSON.stringify(g2));
if (WIB) ok('… dan TIDAK ikut rincian 25 Sep (tanggal UTC-nya)', !riwayatRinci('2026-09-25').some(function (r) { return r.grupNota === 'g2'; }), JSON.stringify(riwayatRinci('2026-09-25')));
var urut = riwayatRinci('2026-09-25').map(function (r) { return r.grupNota; }).join();
ok('urutan = terbaru DIRINCI dulu (bukan jam karcis)', urut === (WIB ? 'g1,g3' : 'g2,g1,g3'), urut);
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

POLA_UTC = re.compile(r"slice\(\s*11\s*,\s*16\s*\)|slice\(\s*0\s*,\s*16\s*\)\s*\.replace\(\s*'T'|substr\(\s*11\s*,\s*5\s*\)")


def penjaga_statis(ganti=None):
    """→ [berkas:baris] yang memotong string ISO jadi jam tampilan (baris komentar dilewati). ganti = {berkas: [(lama, baru)]} untuk kontrol."""
    temu = []
    for akar, _, berkas in os.walk(os.path.join(AKAR, 'baru', 'js')):
        for b in berkas:
            if not b.endswith('.js'): continue
            p = os.path.join(akar, b); rel = os.path.relpath(p, AKAR); t = open(p, encoding='utf-8').read()
            for lama, baru in (ganti or {}).get(rel, []):
                assert lama in t, 'kontrol basi: ' + rel + ' · ' + lama[:60]; t = t.replace(lama, baru)
            for i, baris in enumerate(t.splitlines(), 1):
                s = baris.strip()
                if s.startswith(('*', '/*', '//')): continue
                if POLA_UTC.search(baris.split('//')[0] if "'//" not in baris and '"//' not in baris else baris): temu.append('%s:%d' % (rel, i))
    return temu


def jalankan_jsc(js, tz):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    try:
        r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ=tz))
    finally:
        os.unlink(p)
    baris = [b for b in r.stdout.strip().split('\n') if b.startswith('{')]
    if r.returncode != 0 or not baris: return None, (r.stderr or r.stdout)[-600:]
    return json.loads(baris[-1]), ''


def kotak_cadangan():
    """Cadangan buatan: satu baris tiap pola, satu grup di bulan terkunci (sampaiBulan 2026-08)."""
    k = lambda i, tgl, jam: {'id': i, 'tanggal': tgl, 'jam': jam, 'jenis': 'kasir_darurat_nominal', 'hargaTotal': 10000, 'dikoreksiOleh': 1}
    r = lambda i, dari, tgl, jam, pada: {'id': i, 'tanggal': tgl, 'jam': jam, 'jenis': 'literan', 'hargaTotal': 10000, 'asalDarurat': True, 'rinciDari': dari,
                                        'koreksiDari': dari, 'grupNota': 'g' + str(i), 'dirinciPada': pada}
    P = [k('a', '2026-09-20', '10:00'), r(1, 'a', '2026-09-20', '10:00', '2026-09-21T05:00:00Z'),      # benar
         k('b', '2026-09-20', '11:00'), r(2, 'b', '2026-09-20', '19:15', '2026-09-22T12:15:00Z'),      # jam merinci WIB (19:15)
         k('c', '2026-09-20', '12:00'), r(3, 'c', '2026-09-20', '12:15', '2026-09-22T12:15:00Z'),      # jam merinci UTC (12:15)
         k('d', '2026-09-20', '13:00'), r(4, 'd', '2026-09-20', '06:00', '2026-09-23T01:00:00Z'),      # geser 7 jam (13:00 − 7)
         k('e', '2026-09-20', '14:00'), r(5, 'e', '2026-09-20', '', '2026-09-23T01:00:00Z'),           # kosong
         r(6, 'hilang', '2026-09-20', '15:00', '2026-09-23T01:00:00Z'),                                # karcis asal tidak ada
         k('f', '2026-08-20', '09:00'), r(7, 'f', '2026-08-20', '16:30', '2026-09-01T09:30:00Z')]      # jam merinci WIB, bulan TERKUNCI
    return {'penjualan': P, 'aturanToko': [{'id': 'kunciPeriode', 'sampaiBulan': '2026-08'}]}


def periksa_laporan(mod):
    out = []; ok = lambda n, c, k='': out.append(('laporan cadangan · ' + n, bool(c), k))
    hitung, salah = mod.golongkan(kotak_cadangan())
    ok('tiap pola tergolong tepat (benar, jam merinci WIB ×2, UTC, geser 7 jam, kosong, karcis hilang)',
       dict(hitung) == {'benar': 1, 'jam merinci (WIB)': 2, 'jam merinci (UTC)': 1, 'bergeser ±7 jam': 1, 'kosong': 1, 'karcis asal tidak ada': 1}, dict(hitung))
    per = {s['id']: s for s in salah}
    ok('bulan terbuka → usulan jam := jam karcis asal', per.get(2, {}).get('usulan') == 'jam := 11:00' and per.get(4, {}).get('usulan') == 'jam := 13:00', per)
    ok('bulan TERKUNCI → tidak diusulkan dikoreksi', per.get(7, {}).get('terkunci') is True and per[7]['usulan'].startswith('TIDAK dikoreksi'), per.get(7))
    ok('yang benar & yang karcisnya hilang tidak masuk usulan', 1 not in per and 6 not in per, sorted(per))
    ok('laporan tidak menulis apa pun (tanpa pemanggilan tulis/simpan)', not re.search(r'open\([^)]*[\'"]w', open(mod.__file__, encoding='utf-8').read()))
    return out


def semua(ganti=None):
    """→ [(nama, lulus, keterangan)]. ganti = {berkas: [(lama, baru)]} (kontrol) — berlaku untuk bundel jsc, penjaga statis, dan alat laporan."""
    ganti = ganti or {}; hasil = []
    js = bundel_baru.bundel(MODUL)
    for rel, gs in ganti.items():
        if rel not in MODUL: continue   # berkas tampilan (mis. menu.js) tidak masuk bundel jsc — kerusakannya hanya untuk penjaga statis
        for lama, baru in gs:
            assert lama in js, 'kontrol basi (jsc): ' + lama[:70]; js = js.replace(lama, baru)
    for tz in ZONA:
        h, e = jalankan_jsc(js + '\nvar TZ = ' + json.dumps(tz) + ';\n' + SKENARIO, tz)
        if h is None: hasil.append(('jsc [%s] jalan' % tz, False, e)); continue
        hasil += [('jsc [%s] %d pemeriksaan' % (tz, h['lulus']), True, '')] + [(g, False, '') for g in h['gagal']]
    temu = penjaga_statis(ganti)
    hasil.append(('penjaga statis: tidak ada kode /baru/js yang memotong string ISO jadi jam tampilan', not temu, temu))
    mod = periksa_jam_rinci
    if 'alat-uji/periksa_jam_rinci.py' in ganti:
        t = open(periksa_jam_rinci.__file__, encoding='utf-8').read()
        for lama, baru in ganti['alat-uji/periksa_jam_rinci.py']:
            assert lama in t, 'kontrol basi: ' + lama[:60]; t = t.replace(lama, baru)
        import types
        mod = types.ModuleType('periksa_jam_rinci_rusak'); mod.__file__ = periksa_jam_rinci.__file__; exec(compile(t, 'periksa_jam_rinci_rusak', 'exec'), mod.__dict__)
    hasil += periksa_laporan(mod)
    return hasil


KONTROL = [
    ('jamSetempat memotong string ISO (memajang UTC)', {'baru/js/inti/format.js': [
        ("function jamSetempat(iso) { if (!iso) return ''; const d = new Date(iso); return isFinite(d.getTime()) ? jamKini(d) : ''; }",
         "function jamSetempat(iso) { if (!iso) return ''; const d = new Date(iso); return isFinite(d.getTime()) ? String(iso).slice(11, 16) : ''; }")]}),
    ('waktuSetempat mengambil tanggal dari string UTC', {'baru/js/inti/format.js': [
        ("tanggalPendek(hariIniIso(d)) + ' ' + jamKini(d)", "tanggalPendek(String(iso).slice(0, 10)) + ' ' + jamKini(d)")]}),
    ('Rincian hari ini kembali menulis jam MERINCI di tempat jam karcis', {'baru/js/layar/karcis-logika.js': [
        ("jam: x.jam || '', tanggal: x.tanggal, jamRinci:", "jam: jamSetempat(x.dirinciPada), tanggal: x.tanggal, jamRinci:")]}),
    ('Rincian hari ini diurutkan menurut jam karcis, bukan kapan dirinci', {'baru/js/layar/karcis-logika.js': [
        ("sort((a, b) => b.dirinciPada.localeCompare(a.dirinciPada));", "sort((a, b) => b.jam.localeCompare(a.jam));")]}),
    ('Rincian hari ini memilih hari dari tanggal UTC', {'baru/js/layar/karcis-logika.js': [
        ("hariIniIso(kapan) !== iso) return;", "String(x.dirinciPada).slice(0, 10) !== iso) return;")]}),
    ('tampilan menu kembali memotong string ISO', {'baru/js/layar/menu.js': [
        ("${m.email} · ${waktuSetempat(m.pada)}", "${m.email} · ${String(m.pada).slice(0, 16).replace('T', ' ')}")]}),
    ('laporan cadangan: geser 7 jam dianggap benar', {'alat-uji/periksa_jam_rinci.py': [
        ("elif jam in (_geser(kj, 420), _geser(kj, -420)): g = 'bergeser ±7 jam'", "elif jam in (_geser(kj, 420), _geser(kj, -420)): g = 'benar'")]}),
    ('laporan cadangan: bulan terkunci tetap diusulkan dikoreksi', {'alat-uji/periksa_jam_rinci.py': [
        ("terkunci = bool(kunci) and str(x.get('tanggal') or '')[:7] <= kunci", "terkunci = False")]}),
]


if __name__ == '__main__':
    if not os.path.exists(JSC): print('jsc tidak ada — uji ini butuh macOS'); sys.exit(2)
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti in KONTROL:
            try:
                g = [x for x in semua(ganti) if not x[1]]
            except AssertionError as e:
                print('KONTROL BASI  ' + nama + ' · ' + str(e)); kode = 3; continue
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:110] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h = semua(); gagal = [x for x in h if not x[1]]
    for nama, lulus, ket in h: print(('✓ ' if lulus else '✗ ') + nama + ('' if lulus else ' → ' + json.dumps(ket, ensure_ascii=False)[:300]))
    print('JAM TAMPIL (rinci karcis & cap waktu): %d lulus · %d gagal' % (len(h) - len(gagal), len(gagal)))
    sys.exit(1 if gagal else 0)
