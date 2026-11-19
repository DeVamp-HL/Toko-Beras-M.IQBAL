#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_identitas_baru.py — BUKTI "angka identik": mesin beku di sistem baru (baru/js/mesin) diberi
data yang sama dengan mesin di index.html, hasilnya wajib sama byte demi byte (JSON).

Data = cadangan toko (backup-batch-*.json, TIDAK ada di repo — berkas ini lokal saja). Tanpa
berkas cadangan, uji dilewati dengan kode keluar 0 dan pesan yang jelas (CI tidak punya datanya).

Sejak 3 Okt 2026 index.html di pohon kerja hanya halaman pengalih (sistem lama dipensiunkan). Sisi LAMA dibaca dari riwayat git:
`git show sistem-lama-terakhir:index.html` (tag = commit 48a694d, commit terakhir sistem lama). Checkout CI berkedalaman 1
tidak membawa tag itu → uji dilewati dengan pesan (sama dengan tanpa cadangan). Yang dijaga tetap nyata: lapisan data /baru/
(toko.js: ambil*() + saringan + urutan cache) memberi mesin beku data yang sama dengan pembaca polos sistem lama.

    python3 alat-uji/uji_identitas_baru.py [backup.json]     → 0 identik · 2 beda · 0 (dilewati)
    python3 alat-uji/uji_identitas_baru.py --kontrol          → buktikan alat bisa MELIHAT beda

DUA PERUBAHAN SENGAJA SESUDAH SISTEM LAMA DIPENSIUNKAN (19 Nov 2026). Sisi lama dibekukan di tag 3 Okt; mesin sistem baru sesudah itu dibuka dua kali atas
keputusan owner, jadi "byte-sama" mentah tidak mungkin lagi di dua tempat ini. Keduanya DISETARAKAN dengan aturan tertulis (setarakan() di bawah), bukan dilewati:
  1. Modal FIFO (9 Okt): bila saklar menyala, buku karung ber-FIFO membawa hppTerakhirPerKg = nilai sisa menurut lapisan + kolom FIFO. Mesin baru tetap membawa
     angka lamanya di hppRataPerKg → yang dibandingkan dengan sisi lama = hppRataPerKg; kolom FIFO dilepas. Lalu saklar DIMATIKAN di salinan cadangan: sisi baru
     MENTAH (tanpa penyetaraan apa pun di karung) wajib sama dengan sisi lama — "saklar mati = rumus lama persis".
  2. Buku kantong per merek (11 Okt): daftar jenis kantong mesin baru lebih panjang, jadi buku KOSONG lahir di satu sisi saja. Buku yang hanya ada di satu sisi
     boleh dilepas HANYA bila tidak punya satu dokumen pun di cadangan dan seluruh angkanya nol; selain itu = BEDA.
Aturan penyetaraan itu sendiri diuji tiap kali alat ini jalan (uji_setarakan, data karangan, tanpa cadangan & tanpa jsc) — termasuk di CI.

Sisi LAMA: fungsi & konstanta dipotong dari index.html (tag sistem-lama-terakhir) apa adanya (cara yang sama
dengan pindah_mesin.py yang sudah pensiun — pembantunya disalin ke sini), dengan ambil*() sederhana atas cache yang diisi cadangan. Sisi BARU: bundel modul
baru/js (bundel_baru.py). Keduanya dijalankan di jsc, tanpa peramban.
"""
import os, sys, json, glob, subprocess, tempfile, re

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import beku2, bundel_baru  # noqa: E402

# Sisi lama: index.html dari riwayat git (sistem lama dipensiunkan 3 Okt 2026). Tag dulu; commit-nya sebagai cadangan nama.
REF_LAMA = ['sistem-lama-terakhir', '48a694d']

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


# ---- pembantu pemotong (salinan dari pindah_mesin.py, pensiun 3 Okt 2026) ----
KW = set('function return const let var if else for while do switch case break continue new this typeof instanceof '
         'in of true false null undefined try catch finally throw async await class extends super import export default '
         'delete void yield Math Number String Array Object JSON Date parseInt parseFloat isNaN isFinite Set Map console '
         'Promise Error Boolean RegExp Infinity NaN'.split())
# Pembaca polos sisi lama (di bawah) memakai saringan & penjumlah ini — ikut dipotong walau tidak dipanggil mesin.
TAMBAHAN = ['penjualanMasihBerlaku', 'produksiMasihBerlaku', 'wzJumlahDiDaftar']


def modul_lama():
    """<script type="module"> index.html dari tag sistem lama; None kalau riwayatnya tidak ada (checkout dangkal)."""
    for ref in REF_LAMA:
        try:
            teks = subprocess.check_output(['git', '-C', AKAR, 'show', ref + ':index.html'], stderr=subprocess.DEVNULL).decode('utf-8')
        except (subprocess.CalledProcessError, OSError):
            continue
        if '<script type="module">' in teks:
            return teks[teks.index('<script type="module">'):teks.rindex('</script>')], ref
    return None, None


def batas(nama):
    return nama.startswith('ambil') or nama in ('bacaCadanganLokal', 'wzDiKeranjangAktif', 'wzDiKeranjangParkir')


def tanpa_komentar(b):
    b = re.sub(r'/\*.*?\*/', '', b, flags=re.S)
    return re.sub(r'(^|[^:\\])//[^\n]*', r'\1', b)


def deklarasi(mod):
    fn = set(re.findall(r'\n  (?:async\s+)?function\s+(\w+)\s*\(', mod))
    konst = dict((n, t.lstrip('\n')) for n, t in beku2.konstanta(mod).items())
    return fn, konst


def pengenal(tubuh):
    return set(re.findall(r'(?<![.\w$])([A-Za-z_$][\w$]*)', tanpa_komentar(tubuh))) - KW


def kumpulkan(mod, mesin):
    fn, konst = deklarasi(mod)
    tubuh, urutan, pakai_konst = {}, [], set()

    def masuk(nama):
        if nama in tubuh or batas(nama): return
        b = beku2.potong(mod, nama)
        if b is None: raise SystemExit('tidak ketemu fungsi ' + nama)
        tubuh[nama] = b
        ids = pengenal(b)
        for d in sorted(ids & fn):
            if d != nama: masuk(d)
        for k in sorted(ids & set(konst)): pakai_konst.add(k)
        urutan.append(nama)
    for n in list(mesin) + TAMBAHAN: masuk(n)
    tambah = True
    while tambah:   # konstanta bisa merujuk konstanta lain
        tambah = False
        for k in list(pakai_konst):
            for d in pengenal(konst[k]) & set(konst):
                if d not in pakai_konst: pakai_konst.add(d); tambah = True
    return tubuh, urutan, sorted(pakai_konst), konst


def sisi_lama(mod):
    """Fungsi & konstanta dari index.html (tag sistem lama) apa adanya + ambil*() atas cache bernama koleksi."""
    tubuh, urutan, konst_pakai, konst = kumpulkan(mod, MESIN)
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


# Kolom yang ditambahkan mfPasang (baru/js/mesin/modal-fifo.js) ke buku karung ber-FIFO — tidak dikenal sistem lama.
FIFO_KOLOM = ['metode', 'fifoMulai', 'hppKeluarPerKg', 'posKeluar', 'hppRataPerKg', 'lapisan']


def kanon(x):
    return json.dumps(x, sort_keys=True)


def setarakan(A, B, cadangan, fifo_boleh=True):
    """Menyetarakan dua perubahan sengaja (lihat kepala berkas). Mengembalikan (A', B', catatan, salah). `salah` = pelanggaran aturan penyetaraan.
    fifo_boleh=False (saklar sudah dimatikan di salinan cadangan): buku karung TIDAK disetarakan — sisa kolom FIFO apa pun jadi beda mentah."""
    A2, B2 = dict(A), dict(B); cat = {'fifo': 0, 'kantongKosong': 0}; salah = []
    if fifo_boleh and isinstance(B.get('karung'), dict):
        kr = {}
        for m, s in B['karung'].items():
            if isinstance(s, dict) and s.get('metode') == 'fifo':
                if 'hppRataPerKg' not in s: salah.append('karung.%s ber-FIFO tanpa hppRataPerKg (angka lama)' % m); kr[m] = s; continue
                s2 = dict((k, v) for k, v in s.items() if k not in FIFO_KOLOM); s2['hppTerakhirPerKg'] = s['hppRataPerKg']; kr[m] = s2; cat['fifo'] += 1
            else: kr[m] = s
        B2['karung'] = kr
    ka, kb = A.get('bahanKemasan'), B.get('bahanKemasan')
    if isinstance(ka, dict) and isinstance(kb, dict):
        berdok = set(str(d.get('jenis')) for d in (cadangan.get('stokBahanKemasan') or []) if isinstance(d, dict))
        ka2, kb2 = dict(ka), dict(kb)
        for sisi, punya, lawan in (('lama', ka2, kb), ('baru', kb2, ka)):
            for j in sorted(set(punya) - set(lawan)):
                v = punya[j]; nol = isinstance(v, dict) and all(isinstance(x, (int, float)) and x == 0 for x in v.values())
                if j in berdok or not nol: salah.append('bahanKemasan.%s hanya di sisi %s padahal %s' % (j, sisi, 'punya dokumen di cadangan' if j in berdok else 'angkanya tidak nol'))
                else: del punya[j]; cat['kantongKosong'] += 1
        A2['bahanKemasan'], B2['bahanKemasan'] = ka2, kb2
    return A2, B2, cat, salah


def beda_kunci(A, B):
    return [k for k in A if kanon(A[k]) != kanon(B.get(k))] + [k for k in B if k not in A]


def tanpa_fifo(cadangan):
    """Salinan cadangan dengan saklar modal FIFO dimatikan (aturanToko/catatStok: hari mulai & masa yang sudah ditutup dikosongkan)."""
    c = dict(cadangan); c['aturanToko'] = [dict(d, modalFifoMulai='', modalFifoMasa=[]) if isinstance(d, dict) and str(d.get('id')) == 'catatStok' else d for d in (cadangan.get('aturanToko') or [])]
    return c


def uji_setarakan():
    """Aturan penyetaraan atas data KARANGAN (bukan angka toko): yang sengaja disetarakan lolos, yang lain tetap terlihat. Mengembalikan (jumlah diperiksa, daftar yang gagal)."""
    rata = {'sisaKg': 90, 'hargaTerakhirPerKg': 13500, 'hppTerakhirPerKg': 13045.5}
    fifo = dict(rata, hppTerakhirPerKg=13500, hppRataPerKg=13045.5, metode='fifo', fifoMulai='2026-09-01', hppKeluarPerKg=13500, posKeluar=710, lapisan=[{'kg': 700, 'harga': 13000}])
    nol = {'totalBeli': 0, 'totalTerpakai': 0, 'totalHargaBeli': 0, 'sisaPcs': 0, 'hppPerPcs': 0}; isi = dict(nol, totalBeli=5, sisaPcs=5)
    cad = {'stokBahanKemasan': [{'jenis': 'gabung', 'tipe': 'beli', 'jumlah': 5}]}

    def hasil(A, B, c=cad, fifo_boleh=True):
        A2, B2, cat, salah = setarakan(A, B, c, fifo_boleh); return beda_kunci(A2, B2), salah, cat
    g = []
    b, s, c = hasil({'karung': {'X': rata}}, {'karung': {'X': fifo}})
    if b or s or c['fifo'] != 1: g.append('buku ber-FIFO yang angka lamanya = sisi lama harus setara')
    b, s, c = hasil({'karung': {'X': rata}}, {'karung': {'X': dict(fifo, hppRataPerKg=13045.6)}})
    if not b: g.append('angka lama FIFO yang bergeser harus terlihat')
    b, s, c = hasil({'karung': {'X': rata}}, {'karung': {'X': dict(fifo, sisaKg=91)}})
    if not b: g.append('sisa kg buku ber-FIFO yang beda harus terlihat')
    b, s, c = hasil({'karung': {'X': rata}}, {'karung': {'X': dict(rata, lapisan=[])}})
    if not b: g.append('kolom FIFO pada buku yang BUKAN ber-FIFO harus terlihat')
    b, s, c = hasil({'karung': {'X': rata}}, {'karung': {'X': fifo}}, fifo_boleh=False)
    if not b: g.append('saklar dimatikan: buku yang masih ber-FIFO harus terlihat (tanpa penyetaraan)')
    b, s, c = hasil({'karung': {'X': rata}}, {'karung': {'X': dict((k, v) for k, v in fifo.items() if k != 'hppRataPerKg')}})
    if not s: g.append('buku ber-FIFO tanpa angka lama harus ditolak')
    b, s, c = hasil({'bahanKemasan': {'gabung': isi}}, {'bahanKemasan': {'gabung': isi, 'permerek': nol}})
    if b or s or c['kantongKosong'] != 1: g.append('buku kantong kosong tanpa dokumen di satu sisi harus setara')
    b, s, c = hasil({'bahanKemasan': {'gabung': isi}}, {'bahanKemasan': {'gabung': isi, 'permerek': isi}})
    if not s: g.append('buku kantong satu sisi yang BERISI harus terlihat')
    b, s, c = hasil({'bahanKemasan': {}}, {'bahanKemasan': {'gabung': nol}})
    if not s: g.append('buku kantong satu sisi yang PUNYA dokumen di cadangan harus terlihat')
    b, s, c = hasil({'bahanKemasan': {'gabung': isi}}, {'bahanKemasan': {'gabung': dict(isi, totalTerpakai=1)}})
    if not b: g.append('buku kantong di kedua sisi yang beda harus terlihat')
    b, s, c = hasil({'kemasan': {'a': 1}}, {'kemasan': {'a': 2}})
    if not b: g.append('kunci lain yang beda harus terlihat')
    return 11, g


def banding(cadangan, mod, js_baru):
    a, ea = jalankan(sisi_lama(mod), cadangan)
    b, eb = jalankan(js_baru, cadangan)
    if a is None or b is None:
        return False, 'JSC JATUH lama=' + ea + ' | baru=' + eb
    A, B = json.loads(a), json.loads(b)
    ringkas = ('%d merek karung · %d kemasan · %d piutang · %d kasbon · %d pemasok · laba Agu %s baris · %d maks karung'
               % (len(A['karung']), len(A['kemasan']), len(A['piutang']), len(A['kasbon']), len(A['utangPemasok']), 'ada' if A['laba'] else 'kosong', len(A['maks'])))
    if a == b: return True, 'identik: ' + ringkas
    A2, B2, cat, salah = setarakan(A, B, cadangan)
    beda = beda_kunci(A2, B2)
    if beda or salah: return False, 'BEDA di: ' + ', '.join(beda + salah)
    setara = []
    if cat['fifo']:
        # saklar FIFO dimatikan di salinan cadangan → sisi baru MENTAH wajib = sisi lama (sisi lama tidak membaca aturanToko, jadi hasilnya tetap A)
        b0, e0 = jalankan(js_baru, tanpa_fifo(cadangan))
        if b0 is None: return False, 'JSC JATUH (saklar FIFO dimatikan) baru=' + e0
        A3, B3, cat3, salah3 = setarakan(A, json.loads(b0), cadangan, fifo_boleh=False)
        beda3 = beda_kunci(A3, B3)
        if beda3 or salah3: return False, 'BEDA sesudah saklar FIFO dimatikan (mestinya rumus lama persis) di: ' + ', '.join(beda3 + salah3)
        setara.append('%d buku karung ber-FIFO: angka rata-rata lamanya (hppRataPerKg) = sistem lama, dan dengan saklar dimatikan seluruh buku karung sama mentah' % cat['fifo'])
    if cat['kantongKosong']: setara.append('%d buku kantong kosong tanpa dokumen hanya ada di satu sisi (daftar jenis per merek)' % cat['kantongKosong'])
    return True, 'identik: ' + ringkas + ' · disetarakan: ' + '; '.join(setara)


def cari_cadangan(argv):
    for x in argv[1:]:
        if x.endswith('.json'): return x
    kandidat = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')), key=os.path.basename)   # cadangan toko boleh di akar, _privat/ atau _arsip-mockup/ (semua di-gitignore); yang terbaru menurut tanggal di namanya
    return kandidat[-1] if kandidat else None


if __name__ == '__main__':
    ns, gs = uji_setarakan()
    print('ATURAN PENYETARAAN (data karangan): %d lulus · %d gagal' % (ns - len(gs), len(gs)) + (' — ' + ' | '.join(gs) if gs else ''))
    if gs: sys.exit(2)
    if '--kontrol' in sys.argv:
        # aturan penyetaraan yang dilonggarkan wajib ketahuan uji_setarakan (murni Python — jalan juga tanpa cadangan)
        asli = setarakan; kode0 = 0
        def longgar_fifo(A, B, c, fifo_boleh=True): return asli(A, B, c, True)
        def longgar_kantong(A, B, c, fifo_boleh=True):
            A2, B2, cat, salah = asli(A, B, c, fifo_boleh)
            for X, Y in ((A2, B2), (B2, A2)):
                if isinstance(X.get('bahanKemasan'), dict) and isinstance(Y.get('bahanKemasan'), dict): X['bahanKemasan'] = dict((k, v) for k, v in X['bahanKemasan'].items() if k in Y['bahanKemasan'])
            return A2, B2, cat, [x for x in salah if not x.startswith('bahanKemasan.')]
        def buta_rata(A, B, c, fifo_boleh=True):
            A2, B2, cat, salah = asli(A, B, c, fifo_boleh)
            if isinstance(B2.get('karung'), dict) and isinstance(A2.get('karung'), dict):
                B2['karung'] = dict((m, dict(s, hppTerakhirPerKg=A2['karung'].get(m, {}).get('hppTerakhirPerKg')) if isinstance(B['karung'].get(m), dict) and B['karung'][m].get('metode') == 'fifo' else s) for m, s in B2['karung'].items())
            return A2, B2, cat, salah
        for nama, palsu in [('penyetaraan FIFO tetap dipakai walau saklar sudah dimatikan', longgar_fifo), ('buku kantong satu sisi dilepas tanpa syarat (berisi / berdokumen ikut lolos)', longgar_kantong), ('angka lama buku ber-FIFO tidak dibandingkan', buta_rata)]:
            setarakan = palsu; gk = uji_setarakan()[1]; setarakan = asli
            print(('BERBUNYI ' if gk else 'DIAM!!   ') + 'aturan: ' + nama + ' → ' + (gk[0][:110] if gk else '-'))
            if not gk: kode0 = 3
        if kode0: sys.exit(kode0)
    berkas = cari_cadangan(sys.argv)
    if not berkas:
        print('DILEWATI: tidak ada backup-batch-*.json (uji identitas hanya jalan di mesin yang punya cadangan toko)'); sys.exit(0)
    cadangan = json.load(open(berkas, encoding='utf-8'))
    mod, ref = modul_lama()
    if not mod:
        print('DILEWATI: index.html sistem lama tidak ada di riwayat git ini (tag %s; checkout dangkal di CI tidak membawanya)' % REF_LAMA[0]); sys.exit(0)
    if '--kontrol' in sys.argv:
        # Kontrol positif: rusakkan SATU mesin di sisi baru (dalam memori), alat wajib melihat bedanya.
        js = sisi_baru()
        rusak = {
            'HPP kemasan dibulatkan salah': js.replace("const hppRataRata = stok[kunci].unitDibuat > 0 ? Math.round(", "const hppRataRata = stok[kunci].unitDibuat > 0 ? Math.floor("),
            # (retur di cadangan 11 Sep kosong → kontrol retur akan DIAM; dipakai opname yang ada 10 dokumen)
            'opname stok diabaikan': js.replace("if (o.merk && stok[o.merk]) stok[o.merk].terpakai -= (o.selisihKg || 0);", "if (o.merk && stok[o.merk]) stok[o.merk].terpakai -= 0;"),
            'pembayaran piutang diabaikan': js.replace("if (m.tipe === 'bayar') {\n        s.bayar += n;", "if (m.tipe === 'bayar') {\n        s.bayar += 0;"),
            'penjualan batal ikut dihitung (ambilPenjualan tanpa saringan)': js.replace("ingatPerVersi('ambilPenjualan', () => ambilPenjualanSemua().filter(penjualanMasihBerlaku));", "ingatPerVersi('ambilPenjualan', () => ambilPenjualanSemua());"),
            'urutan cache dibalik (harga terakhir jadi salah batch)': js.replace("_cache[k.cache] = urutkanTerbaru(dokumen || [], k.urut);", "_cache[k.cache] = urutkanTerbaru(dokumen || [], k.urut).reverse();"),
            # penyetaraan kantong tidak boleh membutakan: buku per jenis yang lahir BERISI wajib terlihat (di kedua sisi maupun di satu sisi)
            'kantong: buku per jenis lahir berisi 1 lembar (bukan kosong)': js.replace("JENIS_BAHAN_KEMASAN.forEach(j => { stok[j] = { totalBeli: 0, totalTerpakai: 0, totalHargaBeli: 0 }; });", "JENIS_BAHAN_KEMASAN.forEach(j => { stok[j] = { totalBeli: 1, totalTerpakai: 0, totalHargaBeli: 0 }; });"),
            'kantong & bahan literan: pemakaian diabaikan': js.replace("stok[b.jenis].totalTerpakai += b.jumlah;", "stok[b.jenis].totalTerpakai += 0;"),
        }
        # dua kontrol ini hanya bermakna bila saklar modal FIFO menyala di cadangan yang dipakai (tanpa itu mesin tidak pernah masuk jalur FIFO)
        mulai_fifo = [str(d.get('modalFifoMulai')) for d in (cadangan.get('aturanToko') or []) if isinstance(d, dict) and str(d.get('id')) == 'catatStok' and re.match(r'^\d{4}-\d{2}-\d{2}$', str(d.get('modalFifoMulai') or ''))]
        if mulai_fifo:
            rusak['modal FIFO: angka rata-rata lama yang dibawa mesin digeser'] = js.replace("h.hppRataPerKg = h.hppTerakhirPerKg;", "h.hppRataPerKg = h.hppTerakhirPerKg + 1;")
            # buku HARI INI dipaksa tetap FIFO walau saklar kosong (buku ber-`sampai` dibiarkan: lapisan pembuka menghitung buku sehari sebelum mulai)
            rusak['modal FIFO: saklar dimatikan tetapi mesin tetap FIFO'] = js.replace("const masa = mfMasaBerlaku(cacheMentah('aturan'), sampai);", "const masa = mfMasaBerlaku(cacheMentah('aturan'), sampai) || (sampai ? null : { mulai: '%s', selesai: '' });" % mulai_fifo[0])
        else: print('DILEWATI 2 kontrol modal FIFO: saklar FIFO mati di cadangan ini')
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            ok, ket = banding(cadangan, mod, isi)
            print(('DIAM!!   ' if ok else 'BERBUNYI ') + nama + ' → ' + ket[:140])
            if ok: kode = 3
        sys.exit(kode)
    ok, ket = banding(cadangan, mod, sisi_baru())
    print(('IDENTIK ' if ok else 'BEDA ') + '(' + os.path.basename(berkas) + ' · sisi lama ' + ref + ':index.html) ' + ket)
    sys.exit(0 if ok else 2)
