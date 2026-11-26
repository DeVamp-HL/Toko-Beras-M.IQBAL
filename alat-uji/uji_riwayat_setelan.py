#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_riwayat_setelan.py — RIWAYAT SETELAN & HARGA, LIHAT SAJA (owner 22 Nov 2026, paket riwayat & pembatalan tahap 3). jsc + statis, KOTAK PASIR (angka contoh).

Yang dijaga:
  · pencatat (baru/js/data/riwayat-setelan.js) dipanggil penulis owner (firebase.js) untuk tiap dokumen: aturanToko & hargaWadah dapat entri riwayatUbah
    {pada, oleh, perangkat, ubah: [{k, dari, ke}]} hanya bila ada kolom yang BERUBAH (cap penulis, tanggal/jam simpan tidak dihitung); riwayat lama SELALU dibawa
    (penulis yang menyusun dokumen dari nol tidak menghapusnya); paling banyak 30; dua tingkat ('induk.anak'); bukan owner / katalog harga / draf katalog / kunci
    bulan = tidak disentuh (objek yang sama);
  · tampilan (baru/js/layar/riwayat-setelan-logika.js): terbitan katalog (lama → baru), harga wadah, setelan ber-riwayat, riwayat lama milik dokumen (nilai
    karung bekas), setelan tanpa catatan = "terakhir disimpan — isi sebelumnya tidak tercatat"; jam UTC digambar setempat; saring harga / setelan; dokumen sistem
    tidak tampil; panel Menu tab "Setelan & harga" dirender asli (lihat saja: tanpa tombol batal).

    python3 alat-uji/uji_riwayat_setelan.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_riwayat_setelan.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru as UB  # noqa: E402

RSD = 'baru/js/data/riwayat-setelan.js'; RSL = 'baru/js/layar/riwayat-setelan-logika.js'; MN = 'baru/js/layar/menu.js'; FB = 'baru/js/data/firebase.js'; IDX = 'baru/index.html'
MODUL = list(dict.fromkeys(bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', RSD, RSL]))

KOTAK = {
  'hargaTerbit': [{'id': 't1', 'tanggal': '2026-10-05', 'jam': '09:00', 'diubahOleh': 'Owner', 'n': 2, 'daftar': [
      {'kunci': 'NG|S', 'nama': 'NG · Karung per kg', 'lama': 13000, 'baru': 13500, 'koleksi': 'katalogHargaKarung'},
      {'kunci': 'Baru|L', 'nama': 'Baru · Literan', 'lama': 0, 'baru': 12000, 'koleksi': 'katalogHargaLiteran'}]}],
  'hargaWadah': [{'id': 'karungbekas', 'jenis': 'karungbekas', 'harga': 2000, 'hargaSebelum': 1500, 'tanggal': '2026-10-07', 'jam': '10:00', 'diubahOleh': 'Owner'}],
  'aturanToko': [
      {'id': 'catatStok', 'minKarung': 50, 'tempoHari': 21, 'tanggal': '2026-11-22', 'jam': '10:00', 'diubahPada': '2026-11-22T03:00:00.000Z', 'diubahOleh': 'Owner',
       'riwayatUbah': [{'pada': '2026-11-22T03:00:00.000Z', 'tanggal': '2026-11-22', 'jam': '10:00', 'oleh': 'Owner', 'perangkat': 'HP owner', 'ubah': [{'k': 'minKarung', 'dari': 60, 'ke': 50}]}]},
      {'id': 'tutupHari', 'kembalian': 192500, 'diubahPada': '2026-11-20T23:30:00.000Z', 'diubahOleh': 'Owner'},
      {'id': 'karungBekas', 'nilai': 2000, 'diubahPada': '2026-10-07T03:00:00.000Z', 'diubahOleh': 'Owner', 'riwayat': [{'tanggal': '2026-10-07', 'jam': '10:00', 'dari': 1500, 'ke': 2000, 'bukuDari': 1500}]},
      {'id': 'hematHarian', 'gen': 3, 'diubahPada': '2026-10-09T01:00:00.000Z'},
      {'id': 'hargaDraf', 'draf': {'NG|S': 14000}, 'diubahPada': '2026-11-21T01:00:00.000Z'}],
}

# Penghitung asap (satu-satunya; dipakai asap data toko DAN kotak pasir). Tiap dokumen setelan disimpan ulang apa adanya: riwayatUbah hasilnya WAJIB sama persis
# dengan riwayatUbah dokumen itu sebelumnya (riwayat lama dibawa, tidak ada entri baru) — beda sedikit saja = catatan palsu. Dulu dihitung "ada riwayatUbah =
# palsu", sehingga setelan yang sudah punya riwayat ASLI (23 Nov: satu setelan yang diubah owner) terhitung palsu padahal riwayatnya cuma dibawa — celah alat
# uji, bukan cacat pencatat. Lalu tambah satu kolom: tepat satu entri baru {ujiAsap: kosong → 1} di ujung, riwayat lama tetap utuh di depannya.
HITUNG = r"""
function hitungAsap(CAD, catat) {
  var J = JSON.stringify, kini = '2026-12-31T16:00:00.000Z', palsu = 0, baru = 0, dibawa = 0, galat = [], contoh = [];
  var semua = (CAD.aturanToko || []).map(function (d) { return ['aturanToko', d]; }).concat((CAD.hargaWadah || []).map(function (d) { return ['hargaWadah', d]; }));
  semua.forEach(function (p) { var k = p[0], d = p[1];
    try {
      var lamaR = Array.isArray(d.riwayatUbah) ? d.riwayatUbah : [];
      var x = Object.assign({}, d, { tanggal: '2026-12-31', jam: '23:00', diubahPada: kini }); var r = catat(k, x, d, true, kini);
      if (J((r && r.riwayatUbah) || []) !== J(lamaR)) { palsu++; contoh.push(k + '/' + d.id + ': ' + lamaR.length + ' → ' + (((r && r.riwayatUbah) || []).length) + ' entri'); }
      else if (lamaR.length) dibawa++;
      if (!rsdDicatat(k, d.id, true)) return;
      var R2 = (catat(k, Object.assign({}, x, { ujiAsap: 1 }), d, true, kini) || {}).riwayatUbah || [];
      if (R2.length === Math.min(RSD_MAKS, lamaR.length + 1) && J(R2[R2.length - 1].ubah) === J([{ k: 'ujiAsap', dari: null, ke: 1 }]) && J(R2.slice(0, -1)) === J(lamaR.slice(-(RSD_MAKS - 1)))) baru++;
      else galat.push(k + '/' + d.id + ': perubahan satu kolom tidak tercatat persis (atau riwayat lama tidak utuh)');
    } catch (e) { galat.push(k + '/' + d.id + ': ' + e); } });
  return { palsu: palsu, baru: baru, dibawa: dibawa, galat: galat, contoh: contoh };
}
"""

SKENARIO = HITUNG + r"""
var hasil = []; var J = JSON.stringify;
function cek(nama, ok, ket) { hasil.push({ nama: nama, ok: !!ok, ket: ket === undefined ? '' : (typeof ket === 'string' ? ket : J(ket)) }); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var KINI = '2026-11-22T05:00:00.000Z';
var cap = function (d) { return Object.assign({}, d, { diubahOleh: 'Owner', diubahPada: KINI, diubahPerangkat: 'HP owner', oleh: 'Owner', perangkat: 'HP owner' }); };

// ---------- pencatat ----------
var a0 = cap({ id: 'catatStok', minKarung: 60, tempoHari: 21 });
cek('bukan owner: dokumen apa adanya (objek yang sama)', rsdSertakan('aturanToko', a0, null, false, KINI) === a0);
var kt = cap({ id: 'NG', merk: 'NG', hargaPerKg: 13000 });
cek('katalog harga tidak disentuh (dibaca katalog HP kasir apa adanya)', rsdSertakan('katalogHargaKarung', kt, cap({ id: 'NG', merk: 'NG', hargaPerKg: 12000 }), true, KINI) === kt);
var df = cap({ id: 'hargaDraf', draf: { 'NG|S': 1 } });
cek('draf kerja katalog & kunci bulan tidak dicatat', rsdSertakan('aturanToko', df, cap({ id: 'hargaDraf', draf: {} }), true, KINI) === df
  && rsdSertakan('aturanToko', cap({ id: 'kunciPeriode', sampaiBulan: '2026-10' }), null, true, KINI).riwayatUbah === undefined);
var b1 = rsdSertakan('aturanToko', a0, null, true, KINI);
cek('dokumen baru: satu entri "baru" memuat semua kolom isi (tanpa cap penulis / id)', Array.isArray(b1.riwayatUbah) && b1.riwayatUbah.length === 1 && b1.riwayatUbah[0].baru === true
  && J(b1.riwayatUbah[0].ubah) === J([{ k: 'minKarung', dari: null, ke: 60 }, { k: 'tempoHari', dari: null, ke: 21 }]) && b1.riwayatUbah[0].oleh === 'Owner' && b1.riwayatUbah[0].pada === KINI, b1);
var b2 = rsdSertakan('aturanToko', cap({ id: 'catatStok', minKarung: 50, tempoHari: 21, tanggal: '2026-11-22', jam: '12:00' }), b1, true, '2026-11-22T05:10:00.000Z');
cek('ubah satu kolom: entri kedua hanya kolom itu (60 → 50); tanggal/jam simpan tidak dihitung; penulis menyusun dari nol → riwayat lama tetap dibawa',
  b2.riwayatUbah.length === 2 && J(b2.riwayatUbah[1].ubah) === J([{ k: 'minKarung', dari: 60, ke: 50 }]) && !b2.riwayatUbah[1].baru && b2.riwayatUbah[1].jam === '12:00', b2.riwayatUbah);
var b3 = rsdSertakan('aturanToko', cap({ id: 'catatStok', minKarung: 50, tempoHari: 21, tanggal: '2026-11-23', jam: '08:00' }), b2, true, '2026-11-23T01:00:00.000Z');
cek('simpan tanpa perubahan isi: tidak ada entri baru, riwayat tetap', (b3.riwayatUbah || []).length === 2 && J(b3.riwayatUbah) === J(b2.riwayatUbah), b3.riwayatUbah);
var p0 = cap({ id: 'upah', tarif: { harian: 100000, lembur: 20000 } }); var p1 = rsdSertakan('aturanToko', cap({ id: 'upah', tarif: { harian: 110000, lembur: 20000 } }), p0, true, KINI);
cek('peta di dalam dokumen: yang dicatat cuma anak yang berubah (tarif.harian)', J(p1.riwayatUbah[0].ubah) === J([{ k: 'tarif.harian', dari: 100000, ke: 110000 }]), p1.riwayatUbah);
var L = { id: 'tempat', daftar: [] }; for (var i = 0; i < 35; i++) { L = rsdSertakan('aturanToko', cap({ id: 'tempat', daftar: [{ nama: 'T' + i }], batasTumpuk: 50 }), L, true, KINI); }
cek('paling banyak 30 entri (yang tertua dibuang); daftar disimpan sebagai teks ≤ 300 huruf', L.riwayatUbah.length === 30 && /T34/.test(L.riwayatUbah[29].ubah[0].ke) && String(L.riwayatUbah[29].ubah[0].ke).length <= 300, L.riwayatUbah.length);
var hw = rsdSertakan('hargaWadah', cap({ id: 'karungbekas', jenis: 'karungbekas', harga: 2500, hargaSebelum: 2000 }), KOTAK.hargaWadah[0], true, KINI);
cek('harga wadah dicatat juga (harga 2.000 → 2.500)', hw.riwayatUbah && hw.riwayatUbah[0].ubah.some(function (u) { return u.k === 'harga' && u.dari === 2000 && u.ke === 2500; }), hw.riwayatUbah);
// penghitung asap yang sama dengan asap data toko, dijalankan atas KOTAK (catatStok sudah ber-riwayat; 5 dokumen dicatat: 4 setelan + 1 harga wadah, draf dilewati)
var hk = hitungAsap(KOTAK, rsdSertakan);
cek('asap di kotak pasir: setelan yang SUDAH ber-riwayat disimpan ulang apa adanya = riwayatnya dibawa utuh, bukan catatan palsu; tambah satu kolom = tercatat persis',
  hk.palsu === 0 && hk.dibawa === 1 && hk.baru === 5 && !hk.galat.length, hk);
var entriKosong = function (k, d, l, o, t) { var r = rsdSertakan(k, d, l, o, t); return rsdDicatat(k, d && d.id, o) ? Object.assign({}, r, { riwayatUbah: (r.riwayatUbah || []).concat([{ pada: t, ubah: [] }]) }) : r; };
cek('penghitung asap tidak buta: pencatat yang menambah entri tanpa perubahan → 5 catatan palsu terhitung', hitungAsap(KOTAK, entriKosong).palsu === 5, hitungAsap(KOTAK, entriKosong));

// ---------- tampilan ----------
var S = rsSemua(); var cari = function (re) { return S.find(function (r) { return re.test(r.judul); }); };
var rt = cari(/^Katalog harga terbit/), rc = cari(/^Pencatatan stok/), rh = cari(/^Tutup hari/), rk = cari(/^Nilai karung bekas/), rw = cari(/^Harga wadah/);
cek('terbitan katalog: satu baris, tiap harga lama → baru ("belum ada" untuk yang baru)', !!rt && rt.golong === 'harga' && rt.judul === 'Katalog harga terbit · 2 harga'
  && J(rt.rinci) === J(['NG · Karung per kg: Rp13.000 → Rp13.500', 'Baru · Literan: belum ada → Rp12.000']), rt);
cek('setelan ber-riwayat: kolom dibaca orang ("min karung: 60 → 50"), jam UTC digambar setempat (10:00 WIB)', !!rc && rc.golong === 'setelan' && rc.tanggal === '2026-11-22' && rc.jam === '10:00' && J(rc.rinci) === J(['min karung: 60 → 50']), rc);
cek('setelan tanpa catatan: "terakhir disimpan", tanggal setempat (23.30 UTC = 21 Nov 06:30 WIB), isi lama dikatakan tidak tercatat', !!rh && rh.akhir && rh.tanggal === '2026-11-21' && rh.jam === '06:30' && /tidak tercatat/.test(rh.rinci[0]), rh);
cek('riwayat lama milik dokumen: nilai karung bekas Rp1.500 → Rp2.000 (golongan harga)', !!rk && rk.golong === 'harga' && J(rk.rinci) === J(['nilai per lembar: Rp1.500 → Rp2.000']) && !rk.akhir, rk);
cek('harga wadah tanpa riwayatUbah: hargaSebelum → harga', !!rw && J(rw.rinci) === J(['harga: Rp1.500 → Rp2.000']), rw);
cek('dokumen sistem (klaim baca) & draf katalog tidak tampil', !S.some(function (r) { return /hemat|draf/i.test(r.judul); }), S.map(function (r) { return r.judul; }));
cek('urut terbaru di atas', S.every(function (r, i) { return i === 0 || (S[i - 1].tanggal + S[i - 1].jam) >= (r.tanggal + r.jam); }), S.map(function (r) { return r.tanggal + ' ' + r.jam; }));
cek('saring: harga = terbitan + wadah + karung bekas; setelan = sisanya; n membatasi', rsDaftar('harga', 40).total === 3 && rsDaftar('setelan', 40).total === S.length - 3 && rsDaftar('', 2).baris.length === 2 && rsDaftar('', 2).total === S.length);
cek('nilai dibaca orang: ya/tidak, kosong, angka bertitik, daftar & peta', rsNilai(true) === 'ya' && rsNilai(null) === 'kosong' && rsNilai(192500) === '192.500' && rsNilai('[1,2]') === '1, 2' && rsNilai('[{"nama":"A"},{"nama":"B"}]') === '2 baris (A, B)' && rsNilai('{"harian":1}') === 'harian: 1');
/*TAMPILAN*/
print(J(hasil));
"""


def tampilan(t):
    M = t[MN]; i = M.find('  function gambarRiwayat(s, tab) {'); j = M.find('  function gambarPengingat(', i)
    if i < 0 or j < 0: return "cek('tampilan: gambarRiwayat ada di menu.js', false);"
    D = open(os.path.join(AKAR, 'baru/js/inti/dom.js'), encoding='utf-8').read(); a = D.find('export const esc'); b = D.find('export const mentah')
    return ("(function () {\n" + D[a:b].replace('export ', '') + "\nvar RS = { RS_SARING: RS_SARING, RS_MULAI: RS_MULAI, rsDaftar: rsDaftar };\n" + M[i:j] + r"""
try {
  var g = gambarRiwayat({ rsSaring: '', rsN: 4 }, 'setelan').html;
  cek('tampilan Setelan & harga: saring, baris + rinci, "tampilkan lagi", TANPA tombol batal', /data-aksi="rsSaring" data-g="harga"/.test(g) && /Pencatatan stok/.test(g) && /min karung: 60 → 50/.test(g) && /tampilkan 1 lagi/.test(g) && !/Katalog harga terbit/.test(g)
    && !/data-aksi="ruBuka"|BATALKAN/.test(g) && /Lihat saja/.test(g) && !/undefined|NaN|\[object/.test(g), g.slice(0, 900));
} catch (e) { cek('tampilan: tab Setelan & harga jalan tanpa galat', false, String(e && e.stack || e)); }
})();
""")


def baca_semua():
    return dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in [RSD, RSL, MN, FB, IDX])


def rakit(t):
    isi = lambda m: t[m] if m in t else open(os.path.join(AKAR, m), encoding='utf-8').read()
    return '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(isi(m)) for m in bundel_baru.lengkapi(MODUL)])


def jalankan(t):
    js = UB.JAM_TETAP + rakit(t) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO.replace('/*TAMPILAN*/', tampilan(t))
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([UB.JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    keluar = (r.stdout or '').strip().split('\n')[-1] if r.stdout else ''
    if r.returncode != 0 or not keluar.startswith('['): return [{'nama': 'jsc jalan', 'ok': False, 'ket': ((r.stderr or '') + (r.stdout or ''))[-1500:]}]
    return json.loads(keluar)


def periksa_statis(t):
    c = []; ok = lambda n, x, k='': c.append({'nama': 'statis: ' + n, 'ok': bool(x), 'ket': k})
    F = t[FB]
    ok('firebase.js: penulis owner memanggil pencatat di titik cap penulis (dokumen yang ditulis = dokumen bercatatan)', "import { rsdSertakan } from './riwayat-setelan.js';" in F
       and "const d = rsdSertakan(x.koleksi, beriAtribusiAkun(x.data, akun, k, x.ada), x.lama, owner, k.kini);" in F
       and F.find("const d = rsdSertakan(") < F.find("b.set(doc(db, x.koleksi, String(d.id)), pasangCap(x.koleksi, d)); ditulis.push({ koleksi: x.koleksi, data: d });"))
    ok('pencatat & tampilan tidak menulis sendiri / tidak menyentuh Firebase', not re.search(r'tulisDokumen|setDoc|writeBatch|import .*firebase', t[RSD] + t[RSL]))
    ok('Menu: tab Setelan & harga, lihat saja', "['setelan', 'Setelan & harga']" in t[MN] and "import * as RS from './riwayat-setelan-logika.js';" in t[MN] and "if (tab === 'setelan') {" in t[MN])
    ok('index.html memuat kedua modul (modulepreload)', '<link rel="modulepreload" href="js/layar/riwayat-setelan-logika.js">' in t[IDX] and '<link rel="modulepreload" href="js/data/riwayat-setelan.js">' in t[IDX])
    return c


ASAP = HITUNG + r"""
var J = JSON.stringify; Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var galat = []; var S = []; try { S = rsSemua(); } catch (e) { galat.push('rsSemua: ' + e); }
var h = hitungAsap(CAD, rsdSertakan); galat = galat.concat(h.contoh.map(function (c) { return 'catatan palsu ' + c; }), h.galat);
if (S.some(function (r) { return /undefined|NaN|\[object/.test(r.judul + r.rinci.join(' ')); })) galat.push('kalimat cacat: ' + J(S.filter(function (r) { return /undefined|NaN|\[object/.test(r.judul + r.rinci.join(' ')); }).slice(0, 2)));
print(J({ baris: S.length, harga: S.filter(function (r) { return r.golong === 'harga'; }).length, akhir: S.filter(function (r) { return r.akhir; }).length, palsu: h.palsu, baru: h.baru, dibawa: h.dibawa, galat: galat.slice(0, 6), nGalat: galat.length }));
"""


def asap(t):
    """Cadangan data toko lokal (_privat/, tidak di git): tampilan memuat semua setelan & terbitan tanpa galat / kalimat cacat; simpan ulang tiap setelan apa adanya
    = tidak ada catatan palsu; tambah satu kolom = tercatat persis. Hanya dihitung — tidak menulis apa pun."""
    import glob
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')), key=os.path.basename)
    if not cad: return [], None
    js = UB.JAM_TETAP + rakit(t) + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([UB.JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    k = (r.stdout or '').strip().split('\n')[-1] if r.stdout else ''
    if r.returncode != 0 or not k.startswith('{'): return [{'nama': 'asap data toko: jsc jalan', 'ok': False, 'ket': ((r.stderr or '') + (r.stdout or ''))[-1200:]}], None
    h = json.loads(k)
    return [{'nama': 'asap data toko: riwayat setelan & harga tergambar, simpan ulang tanpa catatan palsu', 'ok': h['nGalat'] == 0 and h['baris'] > 0 and h['baru'] > 0, 'ket': h}], (os.path.basename(cad[-1]), h)


def periksa(t, diam=False):
    c = jalankan(t) + periksa_statis(t)
    g = [x for x in c if not x['ok']]
    if not diam:
        for x in c: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:900]))
        print('RIWAYAT SETELAN & HARGA: %d lulus · %d gagal' % (len(c) - len(g), len(g)))
        a, info = asap(t)
        for x in a: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + json.dumps(x['ket'], ensure_ascii=False)[:1200]))
        g = g + [x for x in a if not x['ok']]
        if info: print('ASAP DATA TOKO (%s): %d baris riwayat (%d harga, %d setelan "terakhir disimpan"), %d setelan dicatat persis, %d setelan ber-riwayat dibawa utuh, %d catatan palsu' % (info[0], info[1]['baris'], info[1]['harga'], info[1]['akhir'], info[1]['baru'], info[1]['dibawa'], info[1]['palsu']))
    return g


def main():
    t = baca_semua()
    if '--kontrol' in sys.argv:
        D = t[RSD]; L = t[RSL]; M = t[MN]; F = t[FB]
        rusak = [
            ('riwayat lama tidak dibawa (penulis dari nol menghapusnya)', RSD, D.replace("const dulu = Array.isArray(lama && lama.riwayatUbah) ? lama.riwayatUbah : Array.isArray(d.riwayatUbah) ? d.riwayatUbah : [];", "const dulu = Array.isArray(d.riwayatUbah) ? d.riwayatUbah : [];")),
            ('jam simpan dihitung perubahan', RSD, D.replace("tanggal: 1, jam: 1, pada: 1,", "pada: 1,")),
            ('bukan owner ikut dicatat', RSD, D.replace("export const rsdDicatat = (koleksi, id, owner) => !!owner && ", "export const rsdDicatat = (koleksi, id, owner) => ")),
            ('katalog harga ikut dicatat', RSD, D.replace("export const RSD_KOLEKSI = { aturanToko: true, hargaWadah: true };", "export const RSD_KOLEKSI = { aturanToko: true, hargaWadah: true, katalogHargaKarung: true };")),
            ('draf katalog ikut dicatat', RSD, D.replace("'aturanToko/hargaDraf': true, ", "")),
            ('riwayat tanpa batas', RSD, D.replace("dulu.concat(entri).slice(-RSD_MAKS)", "dulu.concat(entri)")),
            ('simpan ulang tanpa perubahan menambah entri kosong', RSD, D.replace("const entri = ubah.length ? [", "const entri = true ? [")),
            ('riwayat lama tidak dibawa saat tidak ada perubahan', RSD, D.replace("if (!ubah.length && !dulu.length) return d;", "if (!ubah.length) return Object.assign({}, d, { riwayatUbah: [] });")),
            ('peta dibandingkan utuh (bukan per anak)', RSD, D.replace("if (rsdPeta(v) && Object.keys(v).length) Object.keys(v).forEach((s) => { o[k + '.' + s] = v[s]; }); else o[k] = v;", "o[k] = v;")),
            ('penulis owner tidak memanggil pencatat', FB, F.replace("const d = rsdSertakan(x.koleksi, beriAtribusiAkun(x.data, akun, k, x.ada), x.lama, owner, k.kini);", "const d = beriAtribusiAkun(x.data, akun, k, x.ada);")),
            ('setelan tanpa catatan tidak tampil', RSL, L.replace("if (!R.length && !(Array.isArray(a.riwayat) && a.riwayat.length) && id !== 'kunciPeriode') {", "if (false) {")),
            ('jam UTC tidak digambar setempat', RSL, L.replace("return { tanggal: ok ? hariIniIso(d) : String(tgl || ''), jam: ok ? jamSetempat(pada) : rsJam(jam) };", "return { tanggal: String(tgl || (pada || '').slice(0, 10)), jam: rsJam(jam || String(pada || '').slice(11, 16)) };")),
            ('dokumen sistem tampil', RSL, L.replace("const RS_SISTEM = { hematHarian: true, acuanTarik: true };", "const RS_SISTEM = {};")),
            ('urut terlama di atas', RSL, L.replace("return out.sort((a, b) => (b.tanggal + ' ' + b.jam).localeCompare(a.tanggal + ' ' + a.jam) || b.id.localeCompare(a.id));", "return out.sort((a, b) => (a.tanggal + ' ' + a.jam).localeCompare(b.tanggal + ' ' + b.jam));")),
            ('terbitan baru tanpa harga lama tertulis Rp0', RSL, L.replace("const rsRp = (n) => (Number(n) > 0 ? RP(Number(n)) : 'belum ada');", "const rsRp = (n) => RP(Number(n) || 0);")),
            ('panel tab setelan hilang', MN, M.replace("    if (tab === 'setelan') {", "    if (false) {")),
        ]
        kode = 0
        for nama, berkas, isi in rusak:
            if isi == t[berkas]: print('KONTROL BASI  ' + nama); kode = 3; continue
            t2 = dict(t); t2[berkas] = isi; g = periksa(t2, diam=True)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + (' → ' + g[0]['nama'][:100] if g else ''))
            if not g: kode = 3
        print('KONTROL: %d kerusakan' % len(rusak)); sys.exit(kode)
    sys.exit(1 if periksa(t) else 0)


if __name__ == '__main__':
    main()
