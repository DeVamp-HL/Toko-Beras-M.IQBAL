#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_jual_baru.py — uji logika layar JUAL sistem baru (baru/js/layar/jual-logika.js) di jsc, tanpa peramban.
Data = KOTAK PASIR kecil (ANGKA CONTOH) supaya bisa jalan di CI; kalau ada backup-batch-*.json lokal,
ditambah uji asap atas data toko (rak terisi, tidak melempar).

    python3 alat-uji/uji_jual_baru.py            → 0 lulus · 2 gagal
    python3 alat-uji/uji_jual_baru.py --kontrol  → kontrol positif: logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/jual-logika.js']

# KOTAK PASIR — angka contoh, bukan angka toko
KOTAK = {
  'batchMasuk': [
    {'id': 'b1', 'tanggal': '2026-09-01', 'caraBayar': 'utang', 'biayaBongkar': 100000, 'merkList': [
      {'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'totalKg': 500, 'subtotalHarga': 6500000, 'hargaPerKg': 13000},
      {'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 25, 'totalKg': 250, 'subtotalHarga': 3300000, 'hargaPerKg': 13200},
      {'merk': 'IR64 Apex', 'satuan': 'karung', 'beratKarung': 50, 'totalKg': 300, 'subtotalHarga': 4200000, 'hargaPerKg': 14000}]},
  ],
  'katalogHargaKarung': [{'id': 'hk1', 'merk': 'Angsa', 'hargaPerKg': 13800}, {'id': 'hk2', 'merk': 'IR64 Apex', 'hargaPerKg': 14600}],
  'katalogHargaKemasan': [{'id': 'hm1', 'merk': 'Kembang', 'ukuran': 5, 'hargaPerUnit': 72000}, {'id': 'hm2', 'merk': 'Angsa', 'ukuran': 25, 'hargaPerUnit': 340000}],
  'katalogHargaLiteran': [{'id': 'hl1', 'merk': 'Angsa', 'hargaPerLiter': 13500}],
  'produksiKemasan': [{'id': 'p1', 'tanggal': '2026-09-02', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 40, 'hppPerUnit': 66000, 'merkSumber': 'IR64 Apex', 'kgDipakai': 200}],
  'stokBahanLiteran': [{'id': 'l1', 'tanggal': '2026-09-01', 'jenis': 'paperbag5l', 'tipe': 'beli', 'jumlah': 100, 'hargaTotal': 30500},
                       {'id': 'l2', 'tanggal': '2026-09-01', 'jenis': 'paperbag10l', 'tipe': 'beli', 'jumlah': 100, 'hargaTotal': 39500}],
  'penjualan': [
    {'id': 's1', 'tanggal': '2026-09-19', 'jam': '08:10', 'caraBayar': 'Tunai', 'namaPelanggan': 'Bu Suti', 'jenis': 'kemasan', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 2, 'totalKg': 10, 'hargaTotal': 144000, 'hppTotalSaatJual': 132000, 'grupNota': 'g1'},
    {'id': 's2', 'tanggal': '2026-09-19', 'jam': '09:00', 'caraBayar': 'Kredit', 'namaPelanggan': 'Deka', 'jenis': 'karung', 'merkSumber': 'Angsa', 'beratKarungAcuan': 50, 'jumlahKarung': 1, 'totalKg': 50, 'hargaTotal': 690000, 'hppTotalSaatJual': 660000, 'grupNota': 'g2'},
    {'id': 's3', 'tanggal': '2026-09-18', 'jam': '10:00', 'caraBayar': 'Tunai', 'namaPelanggan': 'Bu Suti', 'jenis': 'kemasan', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 1, 'totalKg': 5, 'hargaTotal': 72000, 'hppTotalSaatJual': 66000, 'grupNota': 'g3'},
    {'id': 's4', 'tanggal': '2026-09-19', 'jam': '11:00', 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': 'literan', 'merkSumber': 'Angsa', 'jumlahLiter': 3, 'totalKg': 2.46, 'hargaTotal': 40500, 'hppTotalSaatJual': 32000, 'grupNota': 'g4', 'dibatalkan': True},
  ],
  'piutangMutasi': [{'id': 'm1', 'tanggal': '2026-08-20', 'namaPelanggan': 'Deka', 'tipe': 'saldoAwal', 'nominal': 200000}],
  'pelangganCatatan': [{'id': 'bu suti', 'nama': 'Bu Suti', 'catatan': 'warung depan pasar'}],
}

SKENARIO = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
setelSumber('cadangan', 'kotak pasir');
var s = keadaanAwal(); s.sekarang = new Date('2026-09-19T10:00:00');
function terap(p) { s = Object.assign({}, s, p); sinkronKeranjang(s); return p; }
function chip(jalur, kunci, berat) { var r = susunRak(s); return r[jalur].find(function (c) { return c.kunci === kunci && (!berat || c.berat === berat); }); }

// ---- rak dibaca dari mesin (bukan hitungan sendiri)
var rak = susunRak(s);
ok('rak karung: Angsa 50 & 25, Apex 50 — tiga chip berharga', rak.karung.length === 3 && rak.karung.map(function (c) { return c.nama + c.berat; }).join() === 'Angsa50,Angsa25,IR64 Apex50', JSON.stringify(rak.karung.map(function (c) { return c.nama + c.berat; })));
ok('harga karung Angsa 25 dari katalog KEMASAN (menang atas per kg): 340.000; Angsa 50 = 13.800 × 50', chip('karung', 'Angsa', 25).harga === 340000 && chip('karung', 'Angsa', 50).harga === 690000, chip('karung', 'Angsa', 50).harga);
ok('sisa Angsa: (750 − 50 terjual) / 50 = 14 karung; per 25 = 28', chip('karung', 'Angsa', 50).sisa === 14 && chip('karung', 'Angsa', 25).sisa === 28, chip('karung', 'Angsa', 50).sisa + '/' + chip('karung', 'Angsa', 25).sisa);
ok('kemasan Kembang 5: 40 dibuat − 3 terjual = 37, harga 72.000', rak.kemasan.length === 1 && rak.kemasan[0].sisa === 37 && rak.kemasan[0].harga === 72000, JSON.stringify(rak.kemasan));
ok('literan Angsa 13.500/L, sisa ±853 L (700 kg / 0,82)', rak.literan.length === 1 && rak.literan[0].harga === 13500 && rak.literan[0].sisa === 853.6, JSON.stringify(rak.literan));
ok('sering tanpa nama = yang laku 28 hari (Kembang 5 kg 2×, Angsa 50 1×; yang dibatalkan tidak dihitung)', rak.sering.length === 2 && rak.sering[0].nama === 'Kembang' && rak.sering[0].kali === 2, JSON.stringify(rak.sering.map(function (c) { return c.nama + ':' + c.kali; })));
terap({ pelanggan: 'bu suti' }); ok('sering untuk Bu Suti (kunci nama tak peduli huruf besar): Kembang 5 kg 2×', susunRak(s).sering.length === 1 && susunRak(s).sering[0].kali === 2); terap({ pelanggan: '' });

// ---- keranjang: ketuk chip → jumlah → masuk
terap(ketukChip(s, chip('karung', 'Angsa', 50))); ok('ketuk chip membuka lembar jumlah', s.lembar === 'jumlah' && s.pilih.kunci === 'Angsa');
terap(tekanTuts(s, '2')); terap(masukkan(s));
ok('2 karung Angsa 50 masuk: hargaTotal 1.380.000, totalKg 100, hpp dari mesin', s.keranjang.length === 1 && s.keranjang[0].trx.hargaTotal === 1380000 && s.keranjang[0].trx.totalKg === 100 && s.keranjang[0].trx.hppTotalSaatJual > 0 && s.keranjang[0].trx.jenis === 'karung', JSON.stringify(s.keranjang[0]));
ok('sesudah masuk, chip Angsa 50 bebas tinggal 12 (langit-langit ikut keranjang aktif)', chip('karung', 'Angsa', 50).sisa === 12, chip('karung', 'Angsa', 50).sisa);
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '13' }); var p = masukkan(s);
ok('minta 13 padahal bebas 12 → DITOLAK, kalimat menyebut yang bebas', s.keranjang.length === 1 && /bebas dijual sekarang 12 karung/.test(p.kabar) && p.kabarAwas, p.kabar); terap(p);
terap({ ketik: '1,5' }); terap(masukkan(s)); ok('1,5 karung boleh (setengah sack) → baris kedua 75 kg', s.keranjang.length === 2 && s.keranjang[1].trx.totalKg === 75, JSON.stringify(s.keranjang.map(function (b) { return b.trx.totalKg; })));
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '0,3' }); p = masukkan(s); ok('0,3 karung ditolak (bukan kelipatan setengah)', s.keranjang.length === 2 && /setengah/.test(p.kabar), p.kabar); terap({ lembar: null, pilih: null, ketik: '' });

// ---- tagihan & pembulatan (Tunai + Bon dibulatkan, QRIS persis)
terap({ keranjang: [], potongan: 0 }); terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '1,3' }); terap(masukkan(s));
var t = hitungTagihan(s);
ok('1,3 L × 13.500 = 17.550 → tunai ditagih 18.000 (bulat +450)', t.subtotal === 17550 && t.bulat === 450 && t.total === 18000, JSON.stringify(t));
ok('literan 1,3 L: totalKg = 1,3 × 0,82 = 1,066; di bawah 5 L tanpa kantong', s.keranjang[0].trx.totalKg === 1.066 && !s.keranjang[0].trx.kemasanLiteran, JSON.stringify(s.keranjang[0].trx));
terap(pilihCara(s, 'Kredit')); t = hitungTagihan(s); ok('BON ikut dibulatkan: 18.000', t.total === 18000 && t.bulat === 450);
terap(pilihCara(s, 'QRIS')); t = hitungTagihan(s); ok('QRIS persis 17.550', t.total === 17550 && t.bulat === 0);
terap(pilihCara(s, 'Tunai')); terap(setelPotongan(s, 2550)); t = hitungTagihan(s); ok('potongan 2.550 → bersih 15.000, pas bulat, total 15.000', t.potongan === 2550 && t.bersih === 15000 && t.bulat === 0 && t.total === 15000, JSON.stringify(t));
terap(setelPotongan(s, 99999999)); ok('potongan dijepit ke subtotal (tidak bisa minus)', hitungTagihan(s).potongan === 17550); terap(setelPotongan(s, 0));

// ---- literan ≥ 5 L membawa kantong (biaya masuk HPP, bukan harga)
terap({ keranjang: [] }); terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '6' }); terap(masukkan(s));
ok('6 L: kantong 10 L × 1 masuk HPP (395), harga tetap 6 × 13.500', s.keranjang[0].trx.kemasanLiteran === 'paperbag10l' && s.keranjang[0].trx.biayaKemasanLiteran === 395 && s.keranjang[0].trx.hargaTotal === 81000 && s.keranjang[0].trx.hppTotalSaatJual - Math.round(chip('literan', 'Angsa').hppPerKg * s.keranjang[0].trx.totalKg) === 395, JSON.stringify(s.keranjang[0].trx));

// ---- uang, kembalian, kurang → sisa jadi bon
terap({ keranjang: [] }); terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '3' }); terap(masukkan(s)); // 216.000
terap(tambahUang(s, 100000)); terap(tambahUang(s, 100000)); t = hitungTagihan(s);
ok('bayar 200.000 dari 216.000 → kurang 16.000, sisa jadi bon', t.kurang === 16000 && t.sisaJadiBon === true && t.kembalian === 0, JSON.stringify(t));
ok('tanpa nama: nota DITAHAN, alasannya sisa jadi bon', /sisanya jadi bon/.test(alasanTolak(s)), alasanTolak(s));
terap({ pelanggan: 'Deka' }); ok('ada nama: sah', alasanTolak(s) === '');
p = simpan(s); ok('BACA SAJA: simpan tidak menulis, hanya mengaku', /BACA SAJA/.test(p.kabar) && /216\.000/.test(p.kabar), p.kabar);
terap(uangPas(s)); t = hitungTagihan(s); ok('PAS → kembalian 0, tidak kurang', t.uang === 216000 && t.kembalian === 0 && t.kurang === 0);
terap({ uang: 0 }); terap(tambahUang(s, 100000)); terap(tambahUang(s, 100000)); terap(tambahUang(s, 20000)); ok('220.000 → kembalian 4.000', hitungTagihan(s).kembalian === 4000);
terap({ uang: 0 }); ok('tunai tanpa uang diterima ditolak', /uang yang diterima/.test(alasanTolak(s)));
terap(pilihCara(s, 'Kredit')); terap({ pelanggan: '' }); ok('bon tanpa nama ditolak', /nama/.test(alasanTolak(s))); terap({ pelanggan: 'Deka' }); ok('bon Deka sah', alasanTolak(s) === '');
var info = infoPelanggan('Deka'); ok('info kredit Deka: sisa bon 890.000 (saldo awal 200.000 + kredit 690.000), rata 90 hari dari mesin', info.sisa === 890000 && info.rataBulanan === 230000, JSON.stringify(info));

// ---- nego
terap(pilihCara(s, 'Tunai')); var id = s.keranjang[0].id;
p = terapkanNego(s, id, 200); ok('nego di bawah lantai Rp500 ditolak', /paling rendah Rp500/.test(p.kabar) && s.keranjang[0].trx.hargaSatuan === 72000);
terap(terapkanNego(s, id, 70000)); ok('nego 70.000 → total 210.000, ditandai nego', s.keranjang[0].trx.hargaTotal === 210000 && s.keranjang[0].trx.nego === true && !s.kabarAwas);
terap(terapkanNego(s, id, 60000)); ok('nego di bawah modal (66.000) tidak ditolak tapi DIBERI TAHU', s.keranjang[0].trx.hargaTotal === 180000 && s.kabarAwas && /DI BAWAH MODAL/.test(s.kabar), s.kabar);
terap(ubahJumlahBaris(s, id, 1)); ok('+1 unit memakai harga nego: 4 × 60.000', s.keranjang[0].trx.jumlah === 4 && s.keranjang[0].trx.hargaTotal === 240000, JSON.stringify(s.keranjang[0].trx));
terap(ubahJumlahBaris(s, id, -4)); ok('−4 → baris hilang', s.keranjang.length === 0);

// ---- antrean: parkir MEMEGANG stok
terap({ keranjang: [], pelanggan: 'Bu Ani', uang: 0, cara: 'Tunai' }); terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '5' }); terap(masukkan(s));
terap(parkir(s)); ok('parkir: keranjang kosong, antrean 1 bernama, id aktif baru', s.keranjang.length === 0 && s.antrean.length === 1 && s.antrean[0].beku.pelanggan === 'Bu Ani' && s.aktifId === 2 && s.pelanggan === '');
ok('chip Angsa 50 sekarang bebas 9 (14 − 5 yang dipegang Bu Ani) dan menyebut yang dipegang', chip('karung', 'Angsa', 50).sisa === 9 && chip('karung', 'Angsa', 50).dipegang === 250, chip('karung', 'Angsa', 50).sisa + '/' + chip('karung', 'Angsa', 50).dipegang);
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '10' }); p = masukkan(s);
ok('Pak Budi minta 10 → ditolak, kalimat menyebut BU ANI memegang 250 kg', /bebas dijual sekarang 9 karung/.test(p.kabar) && /Bu Ani masih memegang 250 kg/.test(p.kabar), p.kabar);
terap({ ketik: '3' }); terap(masukkan(s)); ok('3 karung boleh untuk pembeli kedua', s.keranjang.length === 1);
ok('literan Angsa juga berkurang karena kolam kg sama: (700 − 250 − 150) / 0,82', chip('literan', 'Angsa').sisa === Math.floor(300 / 0.82 * 10) / 10, chip('literan', 'Angsa').sisa);
terap(pakaiAntrean(s, 1)); ok('membuka struk Bu Ani MEMARKIR yang sedang jalan (bukan dibuang) dan memulihkan 5 karung', s.keranjang.length === 1 && s.keranjang[0].trx.jumlahKarung === 5 && s.pelanggan === 'Bu Ani' && s.antrean.length === 1 && s.antrean[0].beku.items[0].trx.jumlahKarung === 3, JSON.stringify(s.antrean));
terap(buangAntrean(s, s.antrean[0].id)); ok('buang struk → stoknya bebas lagi: 14 − 5 aktif = 9', s.antrean.length === 0 && chip('karung', 'Angsa', 50).sisa === 9);
terap(pembeliLain(s)); ok('pembeli lain = parkir', s.antrean.length === 1 && s.keranjang.length === 0);

// ---- pelanggan & hari ini
var d = daftarPelanggan(''); ok('daftar pelanggan: Bu Suti (terdaftar ✓, 2× belanja) & Deka (bon 890.000)', d.length === 2 && d.find(function (o) { return o.nama === 'Bu Suti'; }).terdaftar === true && d.find(function (o) { return o.nama === 'Deka'; }).sisaBon === 890000, JSON.stringify(d));
ok('cari "dek" menyempit', daftarPelanggan('dek').length === 1);
var hi = hariIni(s); ok('hari ini 19 Sep: 2 baris, 2 nota, omzet 834.000, Tunai 144.000 · Kredit 690.000', hi.baris === 2 && hi.nota === 2 && hi.omzet === 834000 && hi.perCara.Tunai === 144000 && hi.perCara.Kredit === 690000, JSON.stringify(hi));

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var s = keadaanAwal(); sinkronKeranjang(s); var rak = susunRak(s); var hi = hariIni(s); var d = daftarPelanggan('');
print(JSON.stringify({ karung: rak.karung.length, kemasan: rak.kemasan.length, literan: rak.literan.length, sering: rak.sering.length, pelanggan: d.length, tanpaHarga: rak.karung.concat(rak.kemasan, rak.literan).filter(function (c) { return !(c.harga > 0); }).length }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:700]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js):
    h, e = jalan(js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            'QRIS ikut dibulatkan': js.replace("return (c === 'Tunai' || c === 'Kredit') && total > 0 ?", "return total > 0 ?"),
            'bon tidak dibulatkan (aturan lama)': js.replace("return (c === 'Tunai' || c === 'Kredit') && total > 0 ?", "return c === 'Tunai' && total > 0 ?"),
            'struk parkir tidak memegang stok': js.replace("s.antrean.map((a) => ({ beku: { items: a.beku.items.map((b) => ({ trx: b.trx })), nama: a.beku.pelanggan } }))", "[]"),
            'langit-langit stok diabaikan': js.replace("if (maks !== null && j > maks) {", "if (false) {"),
            'uang kurang dianggap lunas': js.replace("const kurang = s.cara === 'Tunai' && uang > 0 ? Math.max(0, total - uang) : 0;", "const kurang = 0;"),
            'sisa bon tanpa nama lolos': js.replace("if (t.sisaJadiBon && !nama) return", "if (false) return"),
            'nego di bawah modal tidak diberi tahu': js.replace("const awas = hppSatuan > 0 && hg < hppSatuan;", "const awas = false;"),
            'penjualan batal ikut dihitung di hari ini': js.replace("const baris = ambilPenjualan().filter((p) => p.tanggal === iso);", "const baris = ambilPenjualanSemua().filter((p) => p.tanggal === iso);"),
            'harga kemasan 25 kg diabaikan (per kg menang)': js.replace("const hg = hargaKarungUtuh(merk, berat);", "const hg = { perUnit: Math.round((cariHargaKarungPerKg(merk) || 0) * berat) };"),
            'kantong literan tidak masuk HPP': js.replace("hppTotalSaatJual: Math.round((chip.hppPerKg || 0) * totalKg) + biayaK,", "hppTotalSaatJual: Math.round((chip.hppPerKg || 0) * totalKg),"),
            'membuka struk lain MEMBUANG keranjang yang sedang jalan': js.replace("const dasar = s.keranjang.length ? parkir(s) : { antrean: s.antrean };", "const dasar = { antrean: s.antrean };"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:110] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')))
    if cad:
        c = json.load(open(cad[-1], encoding='utf-8'))
        h, e = jalan(js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP)
        if h is None: print('ASAP DATA TOKO: JSC JATUH ' + e); g.append('asap')
        else: print('ASAP DATA TOKO (%s): rak karung %d · kemasan %d · literan %d · sering %d · pelanggan %d · chip tanpa harga %d' % (os.path.basename(cad[-1]), h['karung'], h['kemasan'], h['literan'], h['sering'], h['pelanggan'], h['tanpaHarga']))
        if h and (h['karung'] == 0 or h['tanpaHarga'] > 0): g.append('asap: rak kosong atau ada chip tanpa harga')
    sys.exit(2 if g else 0)
