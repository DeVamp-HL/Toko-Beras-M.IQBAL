#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ukur_kinerja_baru.py — MENGUKUR ongkos hitung layar sistem baru dengan data toko asli (cadangan _privat/, lokal saja).
Owner 29 Sep 2026: "perpindahan layar ada lag, kurang smooth, suka nge-freeze apalagi waktu refresh & pertama buka".
Tanpa peramban (jsc) — mengukur HITUNGAN yang dijalankan tiap kali layar digambar ulang, bukan menggambar DOM-nya:
  · pasok: mengurutkan satu koleksi saat datang dari server (56× saat membuka aplikasi)
  · Jual:  hitungan yang dijalankan gambar() Jual setiap kali dipanggil
  · Ringkasan: bangunIndeks + susunRingkasan
  · simulasi BUKA APLIKASI: koleksi datang satu per satu; dulu tiap kedatangan = 2 gambar Jual penuh.

    python3 alat-uji/ukur_kinerja_baru.py            → tabel ms (median dari beberapa putaran)
"""
import os, re, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kunci_periode, uji_riwayat_penjualan  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
TAMBAH = ['baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/struk-logika.js', 'baru/js/layar/jenis-beras-logika.js',
          'baru/js/layar/arsip-logika.js', 'baru/js/layar/setengah-logika.js', 'baru/js/layar/ringkasan-logika.js', 'baru/js/layar/pajak-logika.js',
          'baru/js/data/katalog-kasir.js']
MODUL = list(dict.fromkeys(uji_riwayat_penjualan.MODUL + TAMBAH))

SKENARIO = r"""
function ukur(f, n) { var t = []; for (var i = 0; i < n; i++) { var a = Date.now(); f(); t.push(Date.now() - a); } t.sort(function (x, y) { return x - y; }); return t[Math.floor(t.length / 2)]; }
var hasil = {}; var nama = Object.keys(CADANGAN);
var nDok = 0; nama.forEach(function (k) { nDok += CADANGAN[k].length; });
hasil.koleksi = nama.length; hasil.dokumen = nDok; hasil.penjualan = (CADANGAN.penjualan || []).length;
var a = Date.now(); nama.forEach(function (k) { pasok(k, CADANGAN[k]); }); hasil.pasok_semua_ms = Date.now() - a;
var s = keadaanAwal(); s.sekarang = new Date(TGL_CAD + 'T18:00:00+07:00');
// hitungan yang dijalankan gambar() Jual (baru/js/layar/jual.js) — dipanggil berurutan persis seperti di sana
function gambarJual() {
  var rak = susunRak(s); var t = hitungTagihan(s); var hari = hariIni(s); var info = infoPelanggan(s.pelanggan); var nP = daftarPesanan('').length;
  var kc = daftarKarcis(s.sekarang); var kh = hitungKarcis(s); var tb = notaTembusBelumCocok(); var kd = karcisDaruratHari(s.sekarang);
  return [rak, t, hari, info, nP, kc, kh, tb, kd];
}
hasil.jual_susunRak_ms = ukur(function () { susunRak(s); }, 5);
hasil.jual_hariIni_ms = ukur(function () { hariIni(s); }, 5);
hasil.jual_karcis_ms = ukur(function () { daftarKarcis(s.sekarang); hitungKarcis(s); karcisDaruratHari(s.sekarang); }, 5);
hasil.jual_tembus_ms = ukur(function () { notaTembusBelumCocok(); }, 5);
hasil.jual_gambar_penuh_ms = ukur(gambarJual, 7);
var k = s.sekarang;
hasil.ringkasan_indeks_ms = ukur(function () { bangunIndeks(); }, 5);
var ix = bangunIndeks();
hasil.ringkasan_susun_ms = ukur(function () { susunRingkasan('hari', ix, k); susunKas(k); susunPerhatian(); }, 5);
// BUKA APLIKASI (dulu): tiap koleksi datang → pasok (+ pendengar data: Jual gambar) + status berubah (Jual gambar lagi)
var tot = 0; a = Date.now();
nama.forEach(function (k2) { pasok(k2, CADANGAN[k2]); gambarJual(); gambarJual(); });
hasil.buka_lama_ms = Date.now() - a;
// BUKA APLIKASI (usulan): koleksi masuk tanpa menggambar; SATU gambar sesudah semuanya siap
a = Date.now(); nama.forEach(function (k2) { pasok(k2, CADANGAN[k2]); }); gambarJual(); hasil.buka_baru_ms = Date.now() - a;
print(JSON.stringify(hasil));
"""


def main():
    c = glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json'))
    if not c:
        print('LEWAT: tidak ada cadangan toko di _privat/ (alat ini lokal saja)'); return 0
    p = max(c, key=os.path.getmtime); d = json.load(open(p, encoding='utf-8'))
    kol = re.findall(r"\{ nama: '(\w+)'", open(os.path.join(AKAR, 'baru/js/data/koleksi.js'), encoding='utf-8').read())
    cad = json.dumps(dict((n, d[n]) for n in kol if isinstance(d.get(n), list)))
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in MODUL)
    js = uji_kunci_periode.satu_lingkup('\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL]))
    kode = js + '\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(str(d.get('diunduhPada', ''))[:10]) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(kode); jalur = f.name
    r = subprocess.run([JSC, jalur], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(jalur)
    out = (r.stdout or '').strip().split('\n')
    if not out or not out[-1].startswith('{'):
        print('JATUH:', (r.stderr or r.stdout)[-1500:]); return 2
    h = json.loads(out[-1]); print('cadangan:', os.path.basename(p))
    for k, v in h.items(): print(f'  {k:26s} {v}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
