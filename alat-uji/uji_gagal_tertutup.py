#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_gagal_tertutup.py — penjaga untuk FALLBACK YANG GAGAL KE ARAH MEMBUKA.

Bentuk cacatnya: `typeof f === 'function' ? f() : <nilai>` di mana <nilai> berarti
"aman / bersih / tidak ada masalah", DAN nilai itu dipakai sebagai IZIN. Kalau cabang
cadangan pernah jalan, gerbangnya membuka justru saat sistemnya tidak bisa ditanya.

Alat ini TIDAK membaca bentuk kodenya. Ia MENJALANKAN fungsi gerbang yang asli
(dipotong dari index.html) lewat jsc, dengan dua keadaan, lalu menuntut:
   antrean = 0     -> gerbang BOLEH lanjut
   antrean = null  -> gerbang MENAHAN          (ini yang ditambal)
Kontrol positifnya: keadaan lama (cadangan memilih 0) HARUS terbaca sebagai "membuka",
supaya terbukti ujinya memang mengukur pintu, bukan mengukur dirinya sendiri.
"""
import io, re, subprocess, sys, tempfile, os, pathlib

AKAR = pathlib.Path(__file__).resolve().parent.parent
SRC = (AKAR / 'index.html').read_text(encoding='utf-8')

JSC = None
for c in ['/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc',
          '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc']:
    if os.access(c, os.X_OK): JSC = c; break
if not JSC: sys.exit('GAGAL: jsc tidak ditemukan')

def potong(nama):
    """Potong satu fungsi dari '{' pertama sesudah namanya, hitung kurung kurawal.
    'async ' WAJIB ikut terbawa: tanpa itu `await` di dalamnya jadi galat sintaks, dan
    galat sintaks di jsc pergi ke stderr — ujinya lalu terlihat 'tidak berbunyi'."""
    i = SRC.index('function ' + nama)
    if SRC[max(0, i - 6):i] == 'async ': i -= 6
    j = SRC.index('{', i)
    d = 0
    for k in range(j, len(SRC)):
        if SRC[k] == '{': d += 1
        elif SRC[k] == '}':
            d -= 1
            if d == 0: return SRC[i:k+1]
    sys.exit('GAGAL: tidak bisa memotong ' + nama)

gerbang = potong('tbKacaBolehLanjut')

# K yang SEMUA syaratnya lolos, kecuali antrean yang diuji.
UJI = r'''
%s
var _tbKaca = { latihan: false, lat: {}, paraf: {} };
function K(antrean) {
  return { jaga: { darurat: 0, rapikan: 0 }, cadangan: 0, daring: true,
           antrean: antrean, perangkat_semua_ok: true,
           ef: { arsip: true, saldo: true } };
}
var gagal = 0;
function cek(syarat, pesan) { if (!syarat) { print('  GAGAL: ' + pesan); gagal++; } else print('  ok  : ' + pesan); }

print('-- gerbang langkah 0 (Tutup Buku) --');
cek(tbKacaBolehLanjut(0, K(0)) === true,
    'antrean KOSONG (0) -> gerbang boleh lanjut');
cek(tbKacaBolehLanjut(0, K(3)) === false,
    'antrean BERISI (3) -> gerbang menahan');
cek(tbKacaBolehLanjut(0, K(null)) === false,
    'antrean TIDAK BISA DITANYA (null) -> gerbang MENAHAN  <-- inti tambalan');

print('-- kontrol positif: keadaan LAMA harus terbaca membuka --');
cek(tbKacaBolehLanjut(0, K(0)) === true,
    'cadangan lama memilih 0, dan 0 memang MEMBUKA — jadi uji ini mengukur pintunya');

print(gagal ? 'GAGAL ' + gagal : 'LULUS');
''' % gerbang

with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
    f.write(UJI); jalur = f.name
out = subprocess.run([JSC, jalur], capture_output=True, text=True)
os.unlink(jalur)
print(out.stdout.strip() or out.stderr.strip())

# --- pemeriksaan teks: cadangannya WAJIB null, bukan nilai yang meloloskan ---
print('-- bentuk cadangan di tiga tempat --')
sisa = 0
for nama, pola in [
    ('gerbang Tutup Buku (antrean)', r"antreanTundaRapuh\(\)\) \? (\w+) : ambilAntreanTunda\(\)\.length"),
    ('peta Tutup Hari (hari belum dikunci)', r"typeof hariBelumDitutup === 'function' \? \(hariBelumDitutup\(\) \|\| \[\]\) : (\w+)"),
]:
    m = re.search(pola, SRC)
    if not m: print('  GAGAL: jangkar hilang —', nama); sisa += 1
    elif m.group(1) != 'null': print('  GAGAL: %s cadangannya `%s`, bukan null' % (nama, m.group(1))); sisa += 1
    else: print('  ok  :', nama, '-> null')

for nama, frasa in [
    ('gerbang Tutup Buku', 'TIDAK BISA DITANYA — ritual ditahan'),
    ('peta Tutup Hari', 'TIDAK BISA DITANYA — jangan anggap bersih'),
    ('peringatan PIN di langkah hapus', 'Keadaan PIN owner TIDAK BISA DITANYA'),
]:
    if frasa in SRC: print('  ok  :', nama, '-> menyebut sebabnya di layar')
    else: print('  GAGAL: %s tidak menyebut sebabnya di layar' % nama); sisa += 1

# ============ RANTAI PIN: gagal dibaca TIDAK BOLEH jadi izin ============
# pinOwnerBenar memutuskan di DUA pagar paling awal, sebelum menyentuh crypto — jadi
# crypto tidak perlu distub sama sekali (dan jsc menolak `var crypto` menimpa globalnya).
pinSrc = '\n'.join([
    potong('pinLokal'),
    SRC[SRC.index('function pinTakTerbaca'):].split('\n')[0],
    potong('pinSudahDisetel'),
    potong('pinOwnerBenar'),
])

UJI2 = r"""
(function () {
  var KUNCI_PIN_LOKAL = 'miqbal_pin_lokal_v1';
  var _mode = 'ada';
  var localStorage = { getItem: function () {
    if (_mode === 'ada')    return '{"garam":"g","acak":"a"}';
    if (_mode === 'kosong') return null;
    if (_mode === 'rusak')  return '{"garam":"g","aca';     // terpotong -> JSON.parse melempar
    throw new Error('site data diblokir');                  // _mode === 'diblokir'
  } };
__PIN__
  var gagal = 0;
  function cek(syarat, pesan) { if (!syarat) { print('  GAGAL: ' + pesan); gagal++; } else print('  ok  : ' + pesan); }

  print('-- pinLokal membedakan TIGA keadaan --');
  _mode = 'ada';      cek(!!(pinLokal() || {}).acak, 'PIN tersimpan -> terbaca ada');
  _mode = 'kosong';   cek(pinLokal() === null, 'belum pernah disetel -> null');
  _mode = 'rusak';    cek(pinTakTerbaca() === true, 'JSON terpotong -> TAK TERBACA (dulu null, tak terbedakan dari belum disetel)');
  _mode = 'diblokir'; cek(pinTakTerbaca() === true, 'site data diblokir -> TAK TERBACA');

  print('-- pinOwnerBenar tidak boleh meloloskan saat tak terbaca --');
  _mode = 'kosong';
  pinOwnerBenar('apa saja').then(function (v) {
    cek(v === true, 'belum disetel -> lolos (kebijakan sadar 12 Agu: pemilik tidak boleh terkunci)');
    _mode = 'rusak';
    return pinOwnerBenar('apa saja');
  }).then(function (v) {
    cek(v === false, 'TAK TERBACA -> MENOLAK  <-- inti tambalan');
    print(gagal ? 'GAGAL ' + gagal : 'LULUS');
  });
})();
""".replace('__PIN__', pinSrc)

with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
    f.write(UJI2); jalur2 = f.name
out2 = subprocess.run([JSC, jalur2], capture_output=True, text=True)
os.unlink(jalur2)
print(out2.stdout.strip() or out2.stderr.strip())
if 'GAGAL' in out2.stdout or not out2.stdout.strip(): sisa += 1

print('-- gerbang PIN menyebut sebabnya --')
for frasa in ['TIDAK BISA DIBACA di HP ini',
              'function antreanTundaRapuh',
              'Penghapusan ditahan sampai antreannya kosong',
              'Keadaan antrean tunda TIDAK BISA DIBACA',
              'if (d && d.takTerbaca) return false;',
              'if (pinTakTerbaca()) {']:
    if frasa in SRC: print('  ok  :', frasa[:56])
    else: print('  GAGAL: hilang -', frasa[:56]); sisa += 1

if 'GAGAL' in out.stdout or sisa: sys.exit(1)
print('SEMUA LULUS')
