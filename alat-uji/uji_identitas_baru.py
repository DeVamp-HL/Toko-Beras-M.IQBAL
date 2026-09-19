#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_identitas_baru.py — BUKTI "angka identik": mesin beku di sistem baru (baru/js/mesin) diberi
data yang sama dengan mesin di index.html, hasilnya wajib sama byte demi byte (JSON).

Data = cadangan toko (backup-batch-*.json, TIDAK ada di repo — berkas ini lokal saja). Tanpa
berkas cadangan, uji dilewati dengan kode keluar 0 dan pesan yang jelas (CI tidak punya datanya).

    python3 alat-uji/uji_identitas_baru.py [backup.json]     → 0 identik · 2 beda · 0 (dilewati)
    python3 alat-uji/uji_identitas_baru.py --kontrol          → buktikan alat bisa MELIHAT beda

Sisi LAMA: fungsi & konstanta dipotong dari index.html apa adanya (alat yang sama dengan
pindah_mesin), dengan ambil*() sederhana atas cache yang diisi cadangan. Sisi BARU: bundel modul
baru/js (bundel_baru.py). Keduanya dijalankan di jsc, tanpa peramban.
"""
import os, sys, json, glob, subprocess, tempfile, re

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import beku2, pindah_mesin, bundel_baru  # noqa: E402

JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
# Mesin yang dibandingkan: yang murni data (tanpa titik kas/localStorage) — pembacaan JUAL & STOK & PIUTANG.
MESIN = ['hitungStokKarungPerMerk', 'hitungStokKemasan', 'hitungStokBahanLiteran', 'hitungStokBahanKemasan',
         'hitungPiutang', 'hitungKasbon', 'hitungUtangPemasok', 'hitungLajuPakai', 'hitungLabaRentang',
         'barisSusutStok', 'bagiBiayaAdukan', 'hitungHppMerkDalamBatch', 'pembulatanTunai', 'stokMaksJalur']
# Panggilan yang dijalankan di kedua sisi (argumen tetap supaya hasilnya bisa dibanding).
PANGGILAN = r"""
var H = {};
H.karung = hitungStokKarungPerMerk();
H.kemasan = hitungStokKemasan();
H.literan = hitungStokBahanLiteran();
H.bahanKemasan = hitungStokBahanKemasan();
H.piutang = hitungPiutang().map(function (p) { var q = {}; Object.keys(p).forEach(function (k) { if (k !== 'umurHari' && k !== 'tanggalJanggal') q[k] = p[k]; }); return q; });
H.kasbon = hitungKasbon();
H.utangPemasok = hitungUtangPemasok();
H.laju = hitungLajuPakai();
H.laba = hitungLabaRentang(function (t) { return String(t || '').slice(0, 7) === '2026-08'; });
H.susut = barisSusutStok(function (t) { return String(t || '').slice(0, 7) === '2026-09'; });
H.adukan = bagiBiayaAdukan([{ merk: 'A', kg: 30 }, { merk: 'B', kg: 20 }], 25000);
H.hpp = hitungHppMerkDalamBatch([{ merk: 'A', totalKg: 500, subtotalHarga: 6500000 }, { merk: 'B', totalKg: 250, subtotalHarga: 3400000 }], 150000);
H.bulat = [pembulatanTunai(49450, 'Tunai'), pembulatanTunai(49450, 'QRIS'), pembulatanTunai(49450, 'Kredit'), pembulatanTunai(700, 'tunai')];
__dom['jualKarungBerat'] = { value: '25' };
var merk = Object.keys(H.karung).sort();
H.maks = merk.map(function (m) { return [m, stokMaksJalur('karung', m)]; });
var kem = Object.keys(H.kemasan).sort();
H.maksKemasan = kem.map(function (k) { return [k, stokMaksJalur('kemasan', k)]; });
print(JSON.stringify(H));
"""


def sisi_lama(mod):
    """Fungsi & konstanta dari index.html apa adanya + ambil*() atas cache bernama koleksi."""
    tubuh, urutan, konst_pakai, impor, konst = pindah_mesin.kumpulkan(mod, MESIN)
    js = [bundel_baru.PRELUDE]
    for k in konst_pakai: js.append(konst[k])
    for n in urutan: js.append(tubuh[n])
    # batas data: cache per koleksi (nama koleksi Firestore), diisi dari cadangan
    js.append(r"""
var __c = {};
function __k(n) { return __c[n] || []; }
function urutkanTerbaru(arr, field) { return [...arr].sort((a, b) => (b[field] > a[field] ? 1 : b[field] < a[field] ? -1 : 0)); }
function ambilSemuaBatch() { return __k('batchMasuk'); }
function ambilBiayaBulanan() { return __k('biayaBulanan'); }
function ambilPenjualanSemua() { return __k('penjualan'); }
function ambilPenjualan() { return ambilPenjualanSemua().filter(penjualanMasihBerlaku); }
function ambilProduksi() { return __k('produksiKemasan'); }
function ambilProduksiBerlaku() { return ambilProduksi().filter(produksiMasihBerlaku); }
function ambilRetur() { return __k('retur'); }
function ambilKarantina() { return __k('karantina'); }
function ambilPengeluaranHarian() { return __k('pengeluaranHarian'); }
function ambilBahanKemasan() { return __k('stokBahanKemasan'); }
function ambilBahanLiteran() { return __k('stokBahanLiteran'); }
function ambilHargaLiteran() { return __k('katalogHargaLiteran'); }
function ambilHargaKemasan() { return __k('katalogHargaKemasan'); }
function ambilHargaKarung() { return __k('katalogHargaKarung'); }
function ambilPiutangMutasi() { return __k('piutangMutasi'); }
function ambilKasbonMutasi() { return __k('kasbonMutasi'); }
function ambilPenyesuaianStok() { return __k('penyesuaianStok'); }
function ambilPenyesuaianKemasan() { return __k('penyesuaianKemasan'); }
function ambilTutupHari() { return __k('tutupHari'); }
function ambilPelangganCatatan() { return __k('pelangganCatatan'); }
function ambilPesanan() { return __k('pesanan'); }
function ambilSetoranKas() { return __k('setoranKas'); }
function ambilAmplopLaba() { return __k('amplopLaba'); }
function ambilModalOwner() { return __k('modalOwner'); }
function ambilUtangOwnerMutasi() { return __k('utangOwnerMutasi'); }
function ambilTembusanStok() { return __k('tembusanStok'); }
function ambilUtangPemasokMutasi() { return __k('utangPemasokMutasi'); }
function ambilTitikKas() { return null; }
var _wzItems = [], _wzAntre = [];
function wzDiKeranjangAktif(jalur, kunci) { return wzJumlahDiDaftar(_wzItems || [], jalur, kunci); }
function wzDiKeranjangParkir(jalur, kunci) { return (_wzAntre || []).reduce(function (a, x) { return a + wzJumlahDiDaftar(((x || {}).beku || {}).items || [], jalur, kunci); }, 0); }
""")
    # wzJumlahDiDaftar & pengurut dipakai batas data sisi lama — potong dari index.html juga
    for n in ['wzJumlahDiDaftar']:
        if n not in tubuh: js.append(beku2.potong(mod, n))
    js.append("function __isi(cad) { Object.keys(cad).forEach(function (n) { if (Array.isArray(cad[n])) { var u = { biayaBulanan: 'bulan', katalogHargaLiteran: 'merk', katalogHargaKarung: 'merk' }[n] || 'id'; __c[n] = urutkanTerbaru(cad[n], u); } }); }")
    return '\n'.join(js)


def sisi_baru():
    js = bundel_baru.bundel(bundel_baru.MODUL_DATA)
    js += "\nfunction __isi(cad) { Object.keys(cad).forEach(function (n) { if (Array.isArray(cad[n])) pasok(n, cad[n]); }); }\n"
    # Sisi baru mengisi keranjang lewat setelKeranjang(); di sisi lama _wzItems kosong → sama-sama kosong.
    return js


def jalankan(js, cadangan):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(js + '\nvar __cad = ' + json.dumps(cadangan) + ';\n__isi(__cad);\n' + PANGGILAN)
        p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'):
        return None, (r.stderr or r.stdout)[:600]
    return r.stdout.strip().split('\n')[-1], ''


def banding(cadangan, mod, js_baru):
    a, ea = jalankan(sisi_lama(mod), cadangan)
    b, eb = jalankan(js_baru, cadangan)
    if a is None or b is None:
        return False, 'JSC JATUH lama=' + ea + ' | baru=' + eb
    if a == b:
        H = json.loads(a)
        return True, ('identik: %d merek karung · %d kemasan · %d piutang · %d kasbon · %d pemasok · laba Agu %s baris · %d maks karung'
                      % (len(H['karung']), len(H['kemasan']), len(H['piutang']), len(H['kasbon']), len(H['utangPemasok']),
                         'ada' if H['laba'] else 'kosong', len(H['maks'])))
    A, B = json.loads(a), json.loads(b)
    beda = [k for k in A if json.dumps(A[k], sort_keys=True) != json.dumps(B.get(k), sort_keys=True)]
    return False, 'BEDA di: ' + ', '.join(beda)


def cari_cadangan(argv):
    for x in argv[1:]:
        if x.endswith('.json'): return x
    kandidat = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')))
    return kandidat[-1] if kandidat else None


if __name__ == '__main__':
    berkas = cari_cadangan(sys.argv)
    if not berkas:
        print('DILEWATI: tidak ada backup-batch-*.json (uji identitas hanya jalan di mesin yang punya cadangan toko)'); sys.exit(0)
    cadangan = json.load(open(berkas, encoding='utf-8'))
    mod = pindah_mesin.modul_index()
    if '--kontrol' in sys.argv:
        # Kontrol positif: rusakkan SATU mesin di sisi baru (dalam memori), alat wajib melihat bedanya.
        js = sisi_baru()
        rusak = {
            'HPP kemasan dibulatkan salah': js.replace("const hppRataRata = stok[kunci].unitDibuat > 0 ? Math.round(", "const hppRataRata = stok[kunci].unitDibuat > 0 ? Math.floor("),
            # (retur di cadangan 11 Sep kosong → kontrol retur akan DIAM; dipakai opname yang ada 10 dokumen)
            'opname stok diabaikan': js.replace("if (o.merk && stok[o.merk]) stok[o.merk].terpakai -= (o.selisihKg || 0);", "if (o.merk && stok[o.merk]) stok[o.merk].terpakai -= 0;"),
            'pembayaran piutang diabaikan': js.replace("if (m.tipe === 'bayar') {\n        s.bayar += n;", "if (m.tipe === 'bayar') {\n        s.bayar += 0;"),
            'penjualan batal ikut dihitung (ambilPenjualan tanpa saringan)': js.replace("function ambilPenjualan() { return ambilPenjualanSemua().filter(penjualanMasihBerlaku); }", "function ambilPenjualan() { return ambilPenjualanSemua(); }"),
            'urutan cache dibalik (harga terakhir jadi salah batch)': js.replace("_cache[k.cache] = urutkanTerbaru(dokumen || [], k.urut);", "_cache[k.cache] = urutkanTerbaru(dokumen || [], k.urut).reverse();"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            ok, ket = banding(cadangan, mod, isi)
            print(('DIAM!!   ' if ok else 'BERBUNYI ') + nama + ' → ' + ket[:100])
            if ok: kode = 3
        sys.exit(kode)
    ok, ket = banding(cadangan, mod, sisi_baru())
    print(('IDENTIK ' if ok else 'BEDA ') + '(' + os.path.basename(berkas) + ') ' + ket)
    sys.exit(0 if ok else 2)
