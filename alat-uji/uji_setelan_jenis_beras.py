#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_setelan_jenis_beras.py — putaran 25c Bagian B: SETELAN JENIS BERAS pindah ke /baru/ (Harga & Pemasok › Katalog harga › Jenis beras), tampil di
Harga + Stok + Jual (keputusan owner 27 Sep 2026). KOTAK PASIR (nama & angka contoh) di jsc, jam dikunci.

STATIS:
  · aturan membaca = aturan sistem lama: jenisUntukMerk, tebakJenisBeras, semuaMerkDikenal, PILIHAN_JENIS_BERAS di baru/js/mesin/pembantu.js
    TERKUNCI SIDIK (alat-uji/pembantu.sha256, beku2.py). Sampai 2 Okt dibandingkan huruf demi huruf dengan teks index.html; sejak sistem lama
    dipensiunkan (3 Okt 2026) kunci sidik itulah pembandingnya — dicatat saat isinya terbukti byte-sama dengan index.html di tag sistem-lama-terakhir.
  · bentuk dokumen: kunci yang ditulis simpanJenisBeras() index.html = KUNCI_LAMA (dibekukan 3 Okt dari tag sistem-lama-terakhir) = kunci dokumen
    /baru/ (dibandingkan di jsc)
  · (pensiun 3 Okt) pemeriksaan "index.html: jalan tulis jenis beras DITUTUP" dihapus bersama objeknya — index.html kini halaman pengalih tanpa script
  · layar: Harga (pil + lembar + daftar), Stok (kartu per jenis), Jual (baris saring) memakai logika jenis-beras-logika.js; cadangan /baru/ membawa peta
JSC:
  · membaca: dokumen pengaturan/jenisBeras MENANG atas salinan localStorage; tanpa dokumen → salinan; '' = sengaja dikosongkan (menimpa tebakan)
  · menulis: ubah satu nama → peta lain utuh; kosongkan; jenis lain yang diketik jadi pilihan; nama tak dikenal / sama / terlalu panjang ditolak
  · jenis beras BARU muncul di Jual (baris saring rak karung, rak disaring persis), di Harga (daftar), di Stok (kelompok & total kg), dan di cadangan

    python3 alat-uji/uji_setelan_jenis_beras.py            → N lulus · 0 gagal
    python3 alat-uji/uji_setelan_jenis_beras.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, beku2, uji_jual_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_jual_baru.MODUL + ['baru/js/layar/jenis-beras-logika.js']
BERKAS = list(dict.fromkeys(MODUL + ['baru/js/mesin/pembantu.js', 'baru/js/layar/harga.js', 'baru/js/layar/stok.js', 'baru/js/layar/jual.js', 'baru/js/layar/sistem-logika.js']))
JAM = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
KOTAK = json.loads(json.dumps(uji_jual_baru.KOTAK))
KOTAK['pengaturan'] = []


def baca(ganti=None):
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in BERKAS)
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert lama in t[b], 'kontrol basi: ' + b + ' · ' + lama[:80]
            t[b] = t[b].replace(lama, baru, 1)
    return t


# Kunci dokumen pengaturan/jenisBeras yang ditulis simpanJenisBeras() index.html, urut. Dibekukan 3 Okt 2026 (sistem lama dipensiunkan): diekstrak dari
# `git show sistem-lama-terakhir:index.html` (commit 48a694d), pola lama simpanKeFirestore('pengaturan', { id: 'jenisBeras', … }).
KUNCI_LAMA = ['id', 'peta', 'diubahPada']
# Aturan membaca yang dulu dibandingkan huruf demi huruf dengan index.html — kini terkunci sidik pembantu.sha256.
ATURAN_TERKUNCI = ['jenisUntukMerk', 'tebakJenisBeras', 'semuaMerkDikenal', 'PILIHAN_JENIS_BERAS']


def kunci_lama(t):
    return list(KUNCI_LAMA)


SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: function () { return 1; } };
var dok = function (peta) { return { id: 'jenisBeras', peta: peta, diubahPada: '2026-09-18T01:00:00.000Z', oleh: 'Owner' }; };
// ---- 1 · membaca
localStorage.setItem('miqbal_jenis_beras_v1', J({ 'Angsa': 'Salinan Lama' }));
ok('tanpa dokumen di server: salinan perangkat (localStorage, cadangan lama) dipakai', ambilPetaJenisBeras().Angsa === 'Salinan Lama' && jbJenisMerk('Angsa') === 'Salinan Lama');
pasok('pengaturan', [dok({ 'Angsa': 'IR64', 'Kembang': 'Pandan Wangi' })]);
ok('dokumen pengaturan/jenisBeras MENANG atas salinan perangkat (dulu /baru/ hanya membaca salinan yang diperbarui sistem lama)', ambilPetaJenisBeras().Angsa === 'IR64' && jbJenisMerk('Angsa') === 'IR64');
ok('nama yang tidak ada di peta memakai tebakan dari namanya (IR64 Apex → IR64); tebakan ditandai di daftar', jbJenisMerk('IR64 Apex') === 'IR64' && jbDaftar().baris.find(function (b) { return b.merk === 'IR64 Apex'; }).asal === 'tebakan', J(jbDaftar()));
pasok('pengaturan', [dok({ 'Angsa': 'IR64', 'Kembang': 'Pandan Wangi', 'IR64 Apex': '' })]);
ok('nilai kosong "" = sengaja dikosongkan: menimpa tebakan, tampil belum diisi (sama dengan sistem lama)', jbJenisMerk('IR64 Apex') === '' && jbDaftar().baris.find(function (b) { return b.merk === 'IR64 Apex'; }).asal === 'kosong');
ok('daftar nama = nama yang dikenal stok & katalog (semuaMerkDikenal verbatim): Angsa, IR64 Apex, Kembang; 2 dari 3 terisi', J(jbDaftar().baris.map(function (b) { return b.merk; })) === J(['Angsa', 'IR64 Apex', 'Kembang']) && jbDaftar().terisi === 2 && jbDaftar().total === 3, J(jbDaftar()));
// ---- 2 · menulis (bentuk sistem lama)
var R = susunJenisBeras('Angsa', 'Setra Ramos', W); var d = R.dokumen ? R.dokumen[0] : {};
ok('ubah satu nama → SATU dokumen pengaturan/jenisBeras; kunci = simpanJenisBeras() sistem lama (' + KUNCI_LAMA.join(', ') + ')', !R.tolak && R.dokumen.length === 1 && d.koleksi === 'pengaturan' && J(Object.keys(d.data)) === J(KUNCI_LAMA) && d.data.id === 'jenisBeras' && d.data.diubahPada === W.kini, J(R));
ok('peta: nama yang diubah berganti, nama lain UTUH (termasuk yang sengaja dikosongkan)', d.data.peta.Angsa === 'Setra Ramos' && d.data.peta.Kembang === 'Pandan Wangi' && d.data.peta['IR64 Apex'] === '', J(d.data.peta));
ok('nama tak dikenal ditolak; jenis yang sama ditolak; lebih dari 40 huruf ditolak', /tidak dikenal/.test(susunJenisBeras('Beras Hantu', 'IR64', W).tolak || '') && /sudah berjenis IR64/.test(susunJenisBeras('Angsa', 'IR64', W).tolak || '')
  && /40 huruf/.test(susunJenisBeras('Angsa', new Array(42).join('x'), W).tolak || ''));
var RK = susunJenisBeras('Kembang', '', W); ok('kosongkan → nilai "" (bukan dihapus dari peta)', !RK.tolak && RK.dokumen[0].data.peta.Kembang === '' && ('Kembang' in RK.dokumen[0].data.peta), J(RK));
terapkanKeCache(R.dokumen);
ok('jenis lain yang diketik owner (Setra Ramos) jadi pilihan, sesudah tujuh jenis bawaan sistem lama', J(jbPilihan().slice(0, 7)) === J(PILIHAN_JENIS_BERAS) && jbPilihan().indexOf('Setra Ramos') === 7, J(jbPilihan()));
// ---- 3 · jenis beras baru MUNCUL di Jual, Harga, Stok, cadangan
var s = keadaanAwal(); s.sekarang = new Date('2026-09-19T10:00:00'); var rak = susunRak(s);
var JR = jbJenisRak(rak.karung); var saring = jbSaringRak(rak.karung, 'Setra Ramos');
ok('Jual: baris saring rak karung menyebut jenis baru (Setra Ramos) dan kelompok "Belum diisi" (IR64 Apex, sengaja dikosongkan) dengan jumlah barangnya', JR.some(function (x) { return x.jenis === 'Setra Ramos' && x.n >= 1; }) && JR.some(function (x) { return x.jenis === JB_BELUM && x.n >= 1; }) && JR[JR.length - 1].jenis === JB_BELUM, J(JR));
ok('Jual: saring Setra Ramos → hanya chip Angsa; tanpa saring → rak utuh dengan urutan desain yang sama', saring.length > 0 && saring.every(function (c) { return c.kunci === 'Angsa'; }) && J(jbSaringRak(rak.karung, '')) === J(rak.karung), J(saring.map(function (c) { return c.kunci + ' ' + c.berat; })));
ok('Jual: kemasan dikenali lewat nama produknya (Kembang|5 → jenis Kembang = Pandan Wangi)', jbJenisChip({ jalur: 'kemasan', kunci: 'Kembang|5' }) === 'Pandan Wangi' && jbJenisChip({ jalur: 'karung', kunci: 'Kembang' }) === 'Pandan Wangi');
ok('Harga: daftar jenis menyebut Angsa · Setra Ramos (diisi owner)', jbDaftar().baris.some(function (b) { return b.merk === 'Angsa' && b.jenis === 'Setra Ramos' && b.asal === 'owner'; }));
var ST = jbKelompokStok();
ok('Stok: kelompok Setra Ramos berisi Angsa dengan total kg = sisa buku Angsa; IR64 lebih dulu dari jenis lain; yang belum diisi paling bawah', ST.some(function (x) { return x.jenis === 'Setra Ramos' && J(x.merk) === J(['Angsa']) && Math.abs(x.kg - hitungStokKarungPerMerk().Angsa.sisaKg) < 1e-9; })
  && (ST[0].jenis === 'IR64' || !ST.some(function (x) { return x.jenis === 'IR64'; })) && ST.every(function (x, i) { return x.jenis !== JB_BELUM || i === ST.length - 1; }), J(ST));
ok('cadangan /baru/ membawa peta dari DOKUMEN (bukan salinan perangkat yang basi)', ambilPetaJenisBeras().Angsa === 'Setra Ramos');
print(J({ lulus: lulus, gagal: gagal }));
"""


def jalan_jsc(t):
    kl = kunci_lama(t)
    if not kl: return 0, ['kunci dokumen jenisBeras sistem lama kosong — pemeriksa bentuk tidak sah']
    js = uji_jual_baru.__dict__.get('satu_lingkup', lambda x: x)('\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL]))
    isi = JAM + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar KUNCI_LAMA = ' + json.dumps(kl) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(isi); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(baris[-1]); return h['lulus'], h['gagal']


def periksa_statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    pb = t['baru/js/mesin/pembantu.js']
    beda = [n for n in ATURAN_TERKUNCI if not beku2.terkunci(n, pb)]
    ok('aturan membaca = sistem lama: jenisUntukMerk, tebakJenisBeras, semuaMerkDikenal, PILIHAN_JENIS_BERAS di pembantu.js terkunci sidik (pembantu.sha256)', not beda, beda)
    hg = t['baru/js/layar/harga.js']
    ok('Harga: pil jenis per nama beras (papan owner), lembar pilih/ketik/kosongkan, daftar lengkap — semuanya lewat susunJenisBeras',
       'data-aksi="jbBuka"' in hg and 'JB.susunJenisBeras(m, j, waktu())' in hg and "JB.susunJenisBeras(m, '', waktu())" in hg and 'gambarJenisDaftar(s)' in hg and re.search(r"pasangIsian\(K, awal, \[[^\n]*'jbKetik'", hg) is not None)   # jbKetik terdaftar di daftar isian (bukan harus paling akhir)
    ok('Stok: kartu beras per jenis dari jbKelompokStok', 'const JB = jbKelompokStok();' in t['baru/js/layar/stok.js'])
    jl = t['baru/js/layar/jual.js']
    ok('Jual: baris saring per jenis (jbJenisRak) & rak disaring (jbSaringRak) — juga rak yang dikelompokkan per ukuran', 'jbJenisRak(daftarRak)' in jl and 'jbSaringRak(daftarRak, jenisAktif)' in jl and 'jbSaringRak(g.daftar, jenisAktif)' in jl)
    ok('cadangan /baru/: peta jenis beras dari ambilPetaJenisBeras() (dokumen dulu)', 'isi.petaJenisBeras = ambilPetaJenisBeras();' in t['baru/js/layar/sistem-logika.js'])
    return out


def semua(ganti=None, bagian=('statis', 'jsc')):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        l, g = jalan_jsc(t); out += [('jsc · ' + x, False, '') for x in g] + [('__jsc', not g, l)]
    return out


KONTROL = [
    ('tebakan /baru/ beda dari sistem lama (sidik pembantu)', {'baru/js/mesin/pembantu.js': [("if (/^IR42/i.test(m)) return 'IR42';", "if (/^IR42/i.test(m)) return 'IR64';")]}, ('statis',)),
    ('salinan perangkat menang atas dokumen', {'baru/js/data/toko.js': [("  if (dok && dok.peta && typeof dok.peta === 'object' && !Array.isArray(dok.peta)) return Object.assign({}, dok.peta);\n", "")]}, ('jsc',)),
    ('dokumen jenis beras berbentuk lain (kolom tambahan)', {'baru/js/layar/jenis-beras-logika.js': [("data: { id: 'jenisBeras', peta, diubahPada: w.kini } }]", "data: { id: 'jenisBeras', peta, diubahPada: w.kini, versi: 2 } }]")]}, ('jsc',)),
    ('nama tak dikenal boleh diisi', {'baru/js/layar/jenis-beras-logika.js': [("if (ingatMerkDikenal().indexOf(m) < 0) return", "if (false) return")]}, ('jsc',)),
    ('jenis lain yang diketik tidak jadi pilihan', {'baru/js/layar/jenis-beras-logika.js': [("return PILIHAN_JENIS_BERAS.slice().concat(lain.sort((a, b) => a.localeCompare(b)));", "return PILIHAN_JENIS_BERAS.slice();")]}, ('jsc',)),
    ('saring rak Jual tidak menyaring', {'baru/js/layar/jenis-beras-logika.js': [("return !jenis ? (daftar || []) : (daftar || []).filter((c) => jbJenisChip(c) === jenis);", "return daftar || [];")]}, ('jsc',)),
    ('kemasan di Jual dibaca sebagai nama utuh "Kembang|5"', {'baru/js/layar/jenis-beras-logika.js': [("(c && c.jalur === 'kemasan' ? String(c.kunci || '').split('|')[0] : String((c && (c.indukUkuran || c.kunci)) || ''))", "String((c && c.kunci) || '')")]}, ('jsc',)),
    ('Stok: yang belum diisi tidak paling bawah', {'baru/js/layar/jenis-beras-logika.js': [("return Object.keys(per).sort((a, b) => (a === JB_BELUM) - (b === JB_BELUM) || (b === 'IR64')", "return Object.keys(per).sort((a, b) => (b === JB_BELUM) - (a === JB_BELUM) || (b === 'IR64')")]}, ('jsc',)),
    ('pilihan jenis beras /baru/ beda dari sistem lama (sidik konstanta)', {'baru/js/mesin/pembantu.js': [("const PILIHAN_JENIS_BERAS = ['IR64', 'Pandan Wangi',", "const PILIHAN_JENIS_BERAS = ['Pandan Wangi', 'IR64',")]}, ('statis',)),
    # (pensiun 3 Okt 2026) kontrol "index.html: jenis beras dibuka lagi" & "salinan HP diubah walau server menolak" dihapus bersama objeknya (index.html)
    ('Jual tanpa baris saring jenis', {'baru/js/layar/jual.js': [("const daftar = jbSaringRak(daftarRak, jenisAktif);", "const daftar = daftarRak;")]}, ('statis',)),
]

if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti, bagian in KONTROL:
            try: h = semua(ganti, bagian)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' · ' + str(e)[:120]); kode = 3; continue
            g = [x for x in h if not x[1]]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h = semua(); g = [x for x in h if not x[1]]
    n = sum(1 for x in h if x[1] and x[0] != '__jsc') + next((x[2] for x in h if x[0] == '__jsc'), 0)
    for x in g: print('   ✗ ' + x[0] + (' → ' + json.dumps(x[2], ensure_ascii=False)[:300] if x[2] not in ('', None) else ''))
    print('SETELAN JENIS BERAS di /baru/ (25c): %d lulus · %d gagal' % (n, len(g)))
    sys.exit(1 if g else 0)
