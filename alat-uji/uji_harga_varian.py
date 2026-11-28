#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_harga_varian.py — HARGA BELI PER KELAS + VARIAN & TERLARIS PER VARIAN (owner 28 Nov 2026).
Owner: "tambahkan Harga beli per merek mutu karena saat ini merek itu sering berubah-ubah. Agar ketahuan mana yang naik harga dari pemasok dan mana yang paling
laris terjual … Grand, Royal, Signature itu nama merek yang ada di sistem yang gua namai sendiri (varian merek)". Keputusan owner: kelompok = KELAS + VARIAN.

Yang dipegang (kelas-merek-logika km… · laporan-logika lp… · stok-catat hitungMasuk · layar Laporan & Stok):
  · kunci: "AJ · Royal" (IR64 Apex) → IR64 Apex · Royal; "Pamanukan · Royal" (IR42 Select) → IR42 Select · Royal — TIDAK digabung; buku per ukuran ikut induk;
    nama tanpa varian = dirinya; varian tanpa kelas = "tanpa kelas · …"
  · riwayat = riwayatModal (kedatangan nyata saja — stok awal / fondasi & buku lahir 0 kg tidak ikut); satu kedatangan × satu kelompok = satu garis (kg dijumlah,
    harga rata-rata tertimbang); ▲▼= dibanding garis SEBELUMNYA di kelompok yang sama, pemasok mana pun
  · rentang: perubahan = harga terakhir di rentang vs kedatangan terakhir SEBELUM rentang; daftar naik terbesar dulu
  · Barang masuk: tanda "Varian ▲ naik … dari IR64 Apex · Royal terakhir" (cuma tanda)
  · Laporan › Harga beli: jualan per kelompok = merekRentang digulung lpGabungMerek; Σ kelompok + di luar varian = omzet mesin (penjaga menutup)
KOTAK PASIR (angka contoh), jam dikunci 28 Nov 2026 10:00 WIB.

    python3 alat-uji/uji_harga_varian.py            → N lulus · 0 gagal
    python3 alat-uji/uji_harga_varian.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kunci_periode, uji_laporan_baru, uji_kelas_merek  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = list(dict.fromkeys(uji_laporan_baru.MODUL + uji_kelas_merek.MODUL))
KM = 'baru/js/layar/kelas-merek-logika.js'; LG = 'baru/js/layar/laporan-logika.js'; LJ = 'baru/js/layar/laporan.js'; SK = 'baru/js/layar/stok.js'; SC = 'baru/js/layar/stok-catat-logika.js'
LAYAR = [LJ, SK]
JAM_TETAP = "var __KINI = new Date('2026-11-28T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def baris(merk, n, harga, berat=50, ekstra=None):
    return dict({'id': str(n) + merk, 'merk': merk, 'satuan': 'karung', 'beratKarung': berat, 'jumlahKarung': n, 'totalKg': n * berat, 'hargaPerKg': harga, 'subtotalHarga': n * berat * harga}, **(ekstra or {}))


def kedatangan(id, tgl, pemasok, rows, **k):
    return dict({'id': id, 'tanggal': tgl, 'jam': '09:00', 'pemasok': pemasok, 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': rows}, **k)


def jual(id, tgl, merk, kg, harga, hpp, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': '10:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': merk, 'totalKg': kg, 'beratKarungAcuan': 50, 'jumlahKarung': kg / 50, 'hargaTotal': harga, 'hppTotalSaatJual': hpp, 'trxId': 't' + id}
    d.update(k); return d


PETA = {'AJ · Royal': 'IR64 Apex', '55 · Royal': 'IR64 Apex', 'Ikan Mas · Royal': 'IR64 Apex', 'TH · Grand': 'IR64 Apex', 'Pamanukan · Royal': 'IR42 Select', 'SB · Royal': 'IR42 Select'}
KOTAK = {
  'batchMasuk': [
    kedatangan(900, '2026-10-01', 'STOK AWAL', [baris('TH · Grand', 2, 14000)], stokAwal=True),
    kedatangan(901, '2026-10-26', 'RODA MAS', [baris('SB · Royal', 4, 16300), baris('TH · Grand', 5, 14200)]),
    kedatangan(902, '2026-11-02', 'RODA MAS', [baris('Pamanukan · Royal', 3, 16300)]),
    kedatangan(903, '2026-11-09', 'RODA MAS', [baris('Pamanukan · Royal', 2, 16300), baris('TH · Grand', 4, 14300)]),
    kedatangan(904, '2026-11-20', 'RODA MAS', [baris('55 · Royal', 4, 14500), baris('Pamanukan · Royal', 2, 16200)]),
    kedatangan(905, '2026-11-22', 'LAHIR BUKU', [dict(baris('Karung belakang IR64 Apex · AJ · Royal', 0, 0), totalKg=0)], stokAwal=True, lahirBuku=True),
    kedatangan(906, '2026-11-25', 'U.D. SEJATI JAYA', [baris('AJ · Royal', 4, 14500), baris('Perahu Layar', 15, 15200),
                                                       baris('Perahu Layar 25 kg', 16, 15200, berat=25, ekstra={'indukUkuran': 'Perahu Layar', 'berat': 25})]),
    kedatangan(907, '2026-11-24', 'U.D. SEJATI JAYA', [baris('TH · Grand', 2, 14250)]),   # ▼50 dari kedatangan SEBELUMNYA (14.300), ▲50 dari yang pertama (14.200)
  ],
  'wadahLiteran': [{'id': 5000, 'tanggal': '2026-09-01', 'jam': '08:00', 'tipe': 'atur', 'penuhKg': 50, 'puncakKg': 60, 'isiUlangKg': 10, 'takarKg': 1.8, 'susutWajarKg': 1, 'sisihKg': 10,
                    'daftar': ['IR64 Apex', 'IR42 Select'], 'merekKarung': [], 'resep': {}, 'literanLangsung': []}],
  'aturanToko': [{'id': 'kelasMerek', 'peta': PETA, 'asal': dict((k, 'owner') for k in PETA), 'kelasSendiri': []},
                 {'id': 'harga', 'targetPerKg': 500, 'bulatKarung': 100, 'bulatLiter': 500, 'bulatKemasan': 1000, 'langkahRp': 50, 'ambangDampak': 50000, 'bongkarKg': 0, 'mdrPersen': 30, 'mdrBatas': 500000}],
  'penjualan': [jual('n1', '2026-11-21', '55 · Royal', 50, 800000, 725000), jual('n2', '2026-11-26', 'AJ · Royal', 100, 1560000, 1450000),
                jual('n3', '2026-11-22', 'Pamanukan · Royal', 50, 850000, 810000), jual('n4', '2026-11-23', 'TH · Grand', 50, 760000, 715000),
                jual('n5', '2026-11-27', 'Perahu Layar 25 kg', 25, 400000, 380000), jual('n6', '2026-11-27', '', 0, 15000, 0, jenis='wadah', namaProduk='Karung bekas'),
                jual('o1', '2026-10-28', 'SB · Royal', 50, 840000, 815000)],
  'katalogHargaKarung': [], 'pengaturan': [], 'hargaTerbit': [],
}

SKENARIO = bundel_baru.TIMBANG_PAS + r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var kunci = function (m) { var K = kmKunciVarian(m); return K ? K.kunci : null; };

// ---- 1 · kunci kelas + varian
ok('kunci: AJ · Royal & 55 · Royal → IR64 Apex · Royal; Pamanukan & SB · Royal → IR42 Select · Royal (dua Royal TIDAK digabung); TH · Grand → IR64 Apex · Grand',
  kunci('AJ · Royal') === 'IR64 Apex · Royal' && kunci('55 · Royal') === 'IR64 Apex · Royal' && kunci('Pamanukan · Royal') === 'IR42 Select · Royal' && kunci('SB · Royal') === 'IR42 Select · Royal' && kunci('TH · Grand') === 'IR64 Apex · Grand',
  J(['AJ · Royal', 'Pamanukan · Royal', 'TH · Grand'].map(kunci)));
ok('kunci: buku per ukuran ikut induk (Perahu Layar 25 kg → Perahu Layar); nama tanpa varian = dirinya; varian tanpa kelas = "tanpa kelas · Royal"; kosong = null',
  kunci('Perahu Layar 25 kg') === 'Perahu Layar' && kunci('Perahu Layar') === 'Perahu Layar' && kunci('XX · Royal') === 'tanpa kelas · Royal' && kmKunciVarian('') === null && kmKunciVarian('AJ · Royal').varian === 'Royal' && kmKunciVarian('AJ · Royal').induk === 'AJ',
  J(['Perahu Layar 25 kg', 'XX · Royal'].map(kunci)));

// ---- 2 · riwayat per kelompok
var R = kmRiwayatVarian(); var g = function (k) { return (R[k] || { garis: [] }).garis; };
var r42 = g('IR42 Select · Royal'), r64 = g('IR64 Apex · Royal'), gr = g('IR64 Apex · Grand'), pl = g('Perahu Layar');
ok('riwayat IR42 Select · Royal: 26 Okt 16.300 (SB, pertama) → 2 Nov = → 9 Nov = → 20 Nov ▼100 (Pamanukan)', J(r42.map(function (x) { return [x.tanggal, x.harga, x.arah, x.selisih]; })) === J([['2026-10-26', 16300, '', 0], ['2026-11-02', 16300, 'sama', 0], ['2026-11-09', 16300, 'sama', 0], ['2026-11-20', 16200, 'turun', -100]])
  && r42[0].merk === 'SB · Royal' && r42[3].merk === 'Pamanukan · Royal' && r42[3].pemasok === 'RODA MAS' && /▼ turun Rp100/.test(r42[3].teks), J(r42));
ok('riwayat IR64 Apex · Royal: 55 · Royal 20 Nov 14.500 → AJ · Royal 25 Nov 14.500 (=, pemasok lain); buku lahir 0 kg (Karung belakang …) tidak ikut', J(r64.map(function (x) { return [x.tanggal, x.merk, x.pemasok, x.harga, x.arah]; })) === J([['2026-11-20', '55 · Royal', 'RODA MAS', 14500, ''], ['2026-11-25', 'AJ · Royal', 'U.D. SEJATI JAYA', 14500, 'sama']]), J(r64));
ok('riwayat IR64 Apex · Grand: stok awal (fondasi) tidak ikut; 26 Okt 14.200 → 9 Nov ▲100 (0,7 %) → 24 Nov ▼50 dari kedatangan SEBELUMNYA (bukan dari yang pertama)', J(gr.map(function (x) { return [x.tanggal, x.harga, x.arah, x.selisih, x.persen]; })) === J([['2026-10-26', 14200, '', 0, 0], ['2026-11-09', 14300, 'naik', 100, 0.7], ['2026-11-24', 14250, 'turun', -50, 0.3]]), J(gr));
ok('satu kedatangan × satu kelompok = satu garis: Perahu Layar + Perahu Layar 25 kg 25 Nov = 1.150 kg, 15.200', pl.length === 1 && pl[0].kg === 1150 && pl[0].harga === 15200 && pl[0].merk === 'Perahu Layar, Perahu Layar 25 kg', J(pl));

// ---- 3 · rentang
var H = kmHargaVarian('2026-11-01', '2026-11-28'); var kel = function (k) { return H.kelompok.find(function (x) { return x.kunci === k; }); };
ok('rentang Nov: Grand naik Rp50 (terakhir 14.250) dari 14.200 (26 Okt, sebelum rentang); IR42 Select · Royal turun Rp100 dari 16.300 (26 Okt); IR64 Apex · Royal = sama (dibanding kedatangan pertama di rentang)',
  kel('IR64 Apex · Grand').ubah.arah === 'naik' && kel('IR64 Apex · Grand').ubah.selisih === 50 && kel('IR64 Apex · Grand').ubah.dari.tanggal === '2026-10-26'
  && kel('IR42 Select · Royal').ubah.arah === 'turun' && kel('IR42 Select · Royal').ubah.selisih === -100 && kel('IR42 Select · Royal').n === 3 && kel('IR64 Apex · Royal').ubah.arah === 'sama', J(H.kelompok.map(function (x) { return [x.kunci, x.ubah.arah, x.ubah.selisih, x.n]; })));
ok('rentang Nov: 5 kedatangan unik (2, 9, 20, 25, 24 Nov — bukan jumlah baris per kelompok); daftar naik = Grand 9 Nov (+100) saja; rata-rata tertimbang IR42 Select · Royal = (150×16.300 + 100×16.300 + 100×16.200) ÷ 350 = 16.271',
  H.nKedatangan === 5 && H.naik.length === 1 && H.naik[0].kunci === 'IR64 Apex · Grand' && H.naik[0].tanggal === '2026-11-09' && kel('IR42 Select · Royal').rata === Math.round((150 * 16300 + 100 * 16300 + 100 * 16200) / 350), J([H.nKedatangan, H.naik, kel('IR42 Select · Royal').rata]));
var H10 = kmHargaVarian('2026-10-01', '2026-10-31');
ok('rentang Okt: hanya kelompok yang sudah datang s.d. 31 Okt (Grand & IR42 Select · Royal); satu kedatangan = "belum ada pembanding"', H10.kelompok.length === 2 && H10.kelompok.every(function (x) { return x.n === 1 && /belum ada pembanding/.test(x.ubah.teks); }), J(H10.kelompok.map(function (x) { return [x.kunci, x.ubah.teks]; })));

// ---- 4 · Barang masuk: tanda varian
ok('banding varian: Ikan Mas · Royal 14.600 di IR64 Apex → ▲ naik Rp100 dari IR64 Apex · Royal terakhir (AJ · Royal 25 Nov, U.D. SEJATI JAYA); nama tanpa varian → null; kelas pilihan menimpa kelas buku',
  (function () { var B = kmBandingVarian('Ikan Mas · Royal', 14600); var B2 = kmBandingVarian('Baru · Royal', 16300, null, 'IR42 Select'); return B && B.arah === 'naik' && B.selisih === 100 && /IR64 Apex · Royal terakhir \(Rp14\.500 · AJ · Royal · 25 Nov · U\.D\. SEJATI JAYA\)/.test(B.teks)
    && kmBandingVarian('Perahu Layar', 15300) === null && B2 && B2.arah === 'naik' && B2.lalu.harga === 16200; })(), J([kmBandingVarian('Ikan Mas · Royal', 14600), kmBandingVarian('Baru · Royal', 16300, null, 'IR42 Select')]));
var HM = hitungMasuk({ id: null, tanggal: '2026-11-28', pemasok: 'RODA MAS', caraBayar: 'tunai', bongkar: '', alasan: '', baris: [{ merk: '55 · Royal', jumlahKarung: '2', beratKarung: 50, hargaPerKg: '14600' }] });
ok('hitungMasuk: baris 55 · Royal 14.600 membawa arahVarian ▲100 dari IR64 Apex · Royal terakhir (AJ 25 Nov)', HM.baris[0].arahVarian && HM.baris[0].arahVarian.arah === 'naik' && HM.baris[0].arahVarian.lalu.tanggal === '2026-11-25', J(HM.baris[0].arahVarian));

// ---- 5 · Laporan › Harga beli
var RG = lpRentangHargaBeli('bulan', new Date()), RL = lpRentangHargaBeli('lalu', new Date()), R3 = lpRentangHargaBeli('3', new Date()), RS = lpRentangHargaBeli('semua', new Date());
ok('rentang pilihan: bulan ini 1–28 Nov; bulan lalu 1–31 Okt; 3 bulan 1 Sep–28 Nov; semua s.d. hari ini', RG.dari === '2026-11-01' && RG.sampai === '2026-11-28' && RL.dari === '2026-10-01' && RL.sampai === '2026-10-31' && R3.dari === '2026-09-01' && RS.sampai === '2026-11-28', J([RG, RL, R3, RS]));
var HB = lpHargaBeli('2026-11-01', '2026-11-28', 'laris'); var bk = function (k) { return HB.baris.find(function (x) { return x.kunci === k; }); };
ok('terlaris Nov: IR64 Apex · Royal paling atas (AJ 1.560.000 + 55 800.000 = 2.360.000, 150 kg, anggota AJ & 55); IR42 Select · Royal 850.000; Perahu Layar terjual dari buku 25 kg',
  HB.baris[0].kunci === 'IR64 Apex · Royal' && HB.baris[0].jual.omzet === 2360000 && HB.baris[0].jual.kg === 150 && J(HB.baris[0].anggota) === J(['55 · Royal', 'AJ · Royal'])
  && bk('IR42 Select · Royal').jual.omzet === 850000 && bk('Perahu Layar').jual.kg === 25 && bk('IR64 Apex · Grand').jual.omzet === 760000, J(HB.baris.map(function (x) { return [x.kunci, x.jual && x.jual.omzet]; })));
ok('laba kotor per varian = Σ anggota (omzet − modal tersimpan di nota): IR64 Apex · Royal 2.360.000 − 2.175.000 = 185.000 → 1.233/kg', HB.baris[0].jual.margin === 185000 && Math.round(HB.baris[0].jual.marginKg) === 1233, J(HB.baris[0].jual));
ok('penjaga: Σ kelompok + di luar varian (karung bekas 15.000) = omzet mesin; menutup; Okt (SB · Royal) tidak ikut', HB.menutup === true && HB.luar === 15000 && HB.total === 2360000 + 850000 + 760000 + 400000 + 15000 && /menutup persis/.test(HB.kalimat), J([HB.total, HB.luar, HB.kalimat]));
var HN = lpHargaBeli('2026-11-01', '2026-11-28', 'naik');
ok('urut naik terbesar: Grand (+50 di rentang) paling atas; jumlah naik 1, turun 1 (IR42 Select · Royal)', HN.baris[0].kunci === 'IR64 Apex · Grand' && HN.nNaik === 1 && HN.nTurun === 1, J(HN.baris.map(function (x) { return [x.kunci, x.beli && x.beli.ubah.arah]; })));
ok('kartu Per kelas ikut tampil dari sumber yang sama (kmKartuKelas)', J(lpKartuKelas().kartu.map(function (k) { return k.kelas; })) === J(kmKartuKelas().kartu.map(function (k) { return k.kelas; })));
print(J({ lulus: lulus, gagal: gagal }));
"""


def baca(ganti=None):
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(MODUL + LAYAR)))
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def jalan(t):
    js = JAM_TETAP + uji_kunci_periode.satu_lingkup('\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL])) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def statis(t):
    out = []; ok = lambda n, c: out.append(('statis · ' + n, bool(c)))
    lg, lj, sk, km = t[LG], t[LJ], t[SK], t[KM]
    ok('Laporan punya tab "Harga beli" sesudah Kuartal', "['kuartal', 'Kuartal'], ['hargabeli', 'Harga beli'], ['pajak', 'Pajak']" in lg)
    ok('Laporan menggambar tab itu dari lpHargaBeli + lpRentangHargaBeli (tanpa rumus di layar)', "s.keluarga === 'hargabeli' ? gambarHargaBeli(s, L) :" in lj and 'LP.lpHargaBeli(RG.dari, RG.sampai, s.hbUrut)' in lj and 'LP.lpRentangHargaBeli(s.hbRentang, kini())' in lj)
    ok('Laporan: rentang, urutan, buka riwayat, lihat semua punya aksi', all(x in lj for x in ['hbRentang: ({ r }) =>', 'hbUrut: ({ u }) =>', 'hbBuka: ({ kunci }) =>', 'hbSemua: () =>', 'data-aksi="hbBuka" data-kunci="${r.kunci}"']))
    ok('Barang masuk owner & tablet menampilkan tanda varian', 'data-k="mav-${i}">Varian ${b.arahVarian.teks}' in sk and 'data-k="mt-av-${i}">Varian ${b.arahVarian.teks}' in sk)
    ok('harga beli per varian memakai riwayatModal (bukan menghitung batchMasuk sendiri) & tanpa DOM', 'riwayatModal(m).forEach((r) =>' in km and 'document.' not in km)
    ok('jualan per varian = merekRentang digulung lpGabungMerek, penjaga lpJagaRentang', 'const G = lpGabungMerek(I.daftar, I.nama, false, 0, false);' in lg and 'const J = lpJagaRentang(R, a, b);' in lg)
    return out


def semua(ganti=None):
    t = baca(ganti); out = statis(t); h, e = jalan(t)
    if h is None: return out + [('JSC JATUH: ' + e, False)]
    return out + [('jsc · ' + x, False) for x in h['gagal']] + [('__jsc', not h['gagal'], h['lulus'])]


RUSAK = [
    ('kelompok tanpa kelas (Royal IR64 & IR42 digabung)', KM, "const depan = kelas || 'tanpa kelas';", "const depan = 'semua';"),
    ('buku per ukuran tidak ikut induk', KM, "const uk = petaUkuran(); if (uk[n] && uk[n].induk) n = kmBersih(uk[n].induk);", "const uk = petaUkuran();"),
    ('stok awal (fondasi) ikut riwayat', KM, "if (r.jenis !== 'kedatangan' || r.fondasi || !(r.totalKg > 0)", "if (r.jenis !== 'kedatangan' || !(r.totalKg > 0)"),
    ('satu kedatangan jadi beberapa garis', KM, "const id = String(r.batchId);", "const id = String(r.batchId) + m;"),
    ('perubahan rentang tidak dibanding kedatangan sebelum rentang', KM, "const dasar = sebelum.length ? sebelum[sebelum.length - 1] : di.length > 1 ? di[0] : null;", "const dasar = di.length > 1 ? di[0] : null;"),
    ('arah dibanding kedatangan pertama, bukan sebelumnya', KM, "i > 0 ? g.garis[i - 1].harga : 0", "i > 0 ? g.garis[0].harga : 0"),
    ('kedatangan dihitung per baris kelompok, bukan per mobil', KM, "nKedatangan: Object.keys(batch).length,", "nKedatangan: kelompok.reduce((t, x) => t + x.n, 0),"),
    ('kelas pilihan baris diabaikan', KM, "const kp = kmBersih(kelasPakai);", "const kp = '';"),
    ('Barang masuk tanpa tanda varian', SC, "merkPemasok, lalu, laluKelas, arah, arahVarian, kelasTanya,", "merkPemasok, lalu, laluKelas, arah, kelasTanya,"),
    ('jualan tidak digulung ke varian', LG, "const k = K ? K.kunci : m;", "const k = m;"),
    ('urutan naik tidak diurut', LG, "u === 'naik' ? naikRp(y) - naikRp(x)", "u === 'naik' ? 0"),
    ('rentang bulan lalu salah', LG, "const dari = awalBulan(y, m - 1);", "const dari = awalBulan(y, m);"),
    ('Laporan tidak menggambar tab', LJ, "s.keluarga === 'hargabeli' ? gambarHargaBeli(s, L) :", ""),
    ('tablet tanpa tanda varian', SK, "data-k=\"mt-av-${i}\">Varian ${b.arahVarian.teks}", "data-k=\"mt-av-${i}\">${b.arahVarian.teks}"),
]


def utama():
    if '--kontrol' in sys.argv:
        lolos = []
        for nama, b, lama, baru in RUSAK:
            hasil = semua({b: [(lama, baru)]})
            if all(x[1] for x in hasil): lolos.append(nama); print('LOLOS (seharusnya gagal):', nama)
            else: print('  tertangkap:', nama)
        if not all(x[1] for x in semua()): print('GAGAL: salinan utuh tidak lulus'); return 3
        print('KONTROL ' + ('LULUS' if not lolos else 'GAGAL') + ' ' + str(len(RUSAK) - len(lolos)) + '/' + str(len(RUSAK)))
        return 0 if not lolos else 3
    hasil = semua(); gagal = [x for x in hasil if not x[1]]; n = sum(1 for x in hasil if x[1] and not x[0].startswith('__')) + next((x[2] for x in hasil if x[0] == '__jsc'), 0)
    for x in gagal: print('GAGAL', x[0])
    print('HARGA BELI PER VARIAN: ' + str(n) + ' lulus · ' + str(len(gagal)) + ' gagal')
    return 0 if not gagal else 1


if __name__ == '__main__':
    sys.exit(utama())
