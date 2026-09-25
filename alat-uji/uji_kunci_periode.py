#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_kunci_periode.py — putaran 25: KUNCI PERIODE BULANAN di jsc (logika sistem baru + penjaga pusat + keputusan owner K1–K6).
KOTAK PASIR (ANGKA & NAMA CONTOH, bukan angka toko), jam dikunci Kamis 24 Sep 2026 10:00 WIB (bisa digeser per skenario).
Yang dijaga: bulan WIB & tenggang minimal (sama dengan rules v4); daftar periksa (tiap ⛔ memblokir; tenggang; hari tanpa tutup: libur hanya hari tanpa
nota, "diterima apa adanya" wajib alasan; karcis belum dirinci; perangkat antre / tanpa denyut); kunci → sampaiBulan naik; buka hanya satu langkah, alasan
≥ 10, bulan bersetoran minta ketik ulang; tiap tombol koreksi di bulan terkunci jadi pembalik; pembalik bertanggal HARI INI dan memakai jenis lama; omzet
bulan terkunci tidak berubah sesudah pembalik, bulan ini berubah sebesar pembaliknya; lpFinal bulanan & tahun final (era ATAU 12 bulan); peringatan pajak;
penjaga pusat (bulan terkunci / > 18 pemeriksaan tidak dikirim), kirim bertahap yang bisa dilanjutkan; bukan-owner hanya bulan berjalan / masa tenggang.

    python3 alat-uji/uji_kunci_periode.py            → N lulus · 0 gagal (+ uji asap cadangan toko lokal bila ada)
    python3 alat-uji/uji_kunci_periode.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_laporan_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
_M = uji_laporan_baru.MODUL + ['baru/js/layar/stok-logika.js', 'baru/js/layar/stok-catat-logika.js', 'baru/js/layar/stok-adukan-logika.js', 'baru/js/layar/stok-karantina-logika.js',
                                'baru/js/layar/stok-kantong-logika.js', 'baru/js/layar/stok-tempat-logika.js', 'baru/js/layar/stok-hpp-logika.js', 'baru/js/layar/karcis-logika.js',
                                'baru/js/data/akses.js', 'baru/js/layar/kunci-periode-logika.js']
MODUL = [m for i, m in enumerate(_M) if m not in _M[:i]]
JAM_TETAP = "var __KINI = new Date('2026-09-24T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(id, tgl, harga, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': '10:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 50, 'beratKarungAcuan': 50, 'jumlahKarung': 1,
         'hargaTotal': harga, 'hppTotalSaatJual': round(harga * 0.95), 'trxId': 't-' + str(id), 'hargaAsliSatuan': harga}
    d.update(k); return d


def batch(id, tgl, merk, kg, harga):
    return {'id': id, 'tanggal': tgl, 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'jam': '08:00',
            'merkList': [{'merk': merk, 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': kg / 50, 'totalKg': kg, 'hargaPerKg': harga, 'subtotalHarga': kg * harga}]}


def hasil(id, tgl, batchP, baris, ke):
    return {'id': id, 'tanggal': tgl, 'jam': '11:00', 'merkSumber': 'Angsa', 'namaProduk': 'Kemasan Contoh', 'ukuranKemasan': 5, 'jumlahUnit': 10, 'hppPerUnit': 70000, 'kgDipakai': 50,
            'biayaKemasan': 0, 'upahRepacking': 0, 'hppSumberPerKgDipakai': 13000, 'kantongJenis': '', 'kantongJumlah': 0, 'batchProduksi': batchP, 'jumlahBaris': baris, 'barisKe': ke,
            'sumberList': [{'merk': 'Angsa', 'kg': 50}]}


# ANGKA CONTOH. Agustus (akan dikunci): nota tunai & bon, karcis darurat belum dirinci, rincian karcis yang sudah jadi, kedatangan, adukan 2 hasil, beli kantong,
# retur tidak utuh. September (bulan berjalan): nota, kedatangan (terakhir untuk merek Beo), karcis.
KOTAK = {
  'penjualan': [jual('a1', '2026-08-10', 700000), jual('a2', '2026-08-12', 650000, caraBayar='Kredit', namaPelanggan='Bu Sari'), jual('a3', '2026-08-20', 300000, namaPelanggan='Pak Tunai'),
                jual('k1', '2026-08-25', 250000, jenis='kasir_darurat_nominal', merkSumber=None, totalKg=0),
                jual('k2', '2026-08-26', 100000, jenis='kasir_darurat_nominal', merkSumber=None, totalKg=0, dikoreksiOleh='r1', alasanKoreksi='Dirinci jadi 1 barang'),
                jual('r1', '2026-08-26', 100000, grupNota='g1', koreksiDari='k2', rinciDari='k2', asalDarurat=True, dirinciPada='2026-09-24T02:00:00.000Z'),
                jual('s1', '2026-09-05', 500000), jual('s2', '2026-09-20', 400000, namaPelanggan='Pak Tunai'), jual('k3', '2026-09-22', 80000, jenis='kasir_darurat_nominal', merkSumber=None, totalKg=0)],
  'batchMasuk': [batch('b1', '2026-08-08', 'Angsa', 5000, 13000), batch('b2', '2026-09-10', 'Beo', 2500, 12000)],
  'produksiKemasan': [hasil('p1', '2026-08-15', 'ad1', 2, 1), hasil('p2', '2026-08-15', 'ad1', 2, 2)],
  'stokBahanKemasan': [{'id': 'kb1', 'tipe': 'beli', 'jenis': 'paperbag5l', 'jumlah': 100, 'hargaTotal': 100000, 'tanggal': '2026-08-09', 'catatan': 'beli contoh'}],
  'stokBahanLiteran': [],
  'retur': [{'id': 'rt1', 'tanggal': '2026-08-21', 'jam': '09:00', 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'totalKg': 10, 'jumlahKarung': 0.2, 'beratKarungAcuan': 50, 'kondisi': 'tidak_utuh',
             'penyelesaian': 'refund', 'nominalRefund': 140000, 'nilaiDikembalikan': 140000, 'notaAsalId': 'a1', 'notaAsalTanggal': '2026-08-10', 'catatan': 'basah'}],
  'karantina': [{'id': 'rt1', 'tanggal': '2026-08-21', 'asalRetur': True, 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'totalKg': 10, 'statusTindakan': 'belum_diputuskan', 'catatan': 'basah'}],
  'piutangMutasi': [{'id': 'pm1', 'tipe': 'bayar', 'namaPelanggan': 'Ibu Sari', 'nominal': 50000, 'tanggal': '2026-09-02', 'caraBayar': 'Tunai', 'catatan': ''},
                    {'id': 'pm2', 'tipe': 'saldoAwal', 'namaPelanggan': 'Ibu Sari', 'nominal': 50000, 'tanggal': '2026-09-01', 'catatan': 'saldo contoh'}],
  'tutupHari': [{'id': d, 'tanggal': d, 'jam': '21:00', 'omzet': 0, 'kasFisikLaci': 0} for d in ['2026-08-08', '2026-08-09', '2026-08-10', '2026-08-11', '2026-08-13', '2026-08-15', '2026-08-21', '2026-08-25', '2026-08-26']],
  'perangkatStatus': [{'id': 'hp-owner', 'nama': 'HP owner', 'pada': '2026-09-24T02:50:00.000Z', 'antrean': 0, 'gagal': 0, 'aplikasi': 'baru'},
                      {'id': 'tab-lama', 'nama': 'Tablet lama', 'pada': '2026-09-20T02:00:00.000Z', 'antrean': 0, 'gagal': 0, 'aplikasi': 'darurat'},
                      {'id': 'tab-kasir', 'nama': 'Tablet kasir', 'pada': '2026-09-24T02:40:00.000Z', 'antrean': 2, 'gagal': 0, 'aplikasi': 'darurat'}],
  'aturanToko': [{'id': 'upah', 'tarif': 60000, 'orang': [{'nama': 'Pekerja Contoh', 'status': 'aktif', 'masuk': '2026-08-20'}]}],
  'absenKaryawan': [{'id': 'pekerja contoh|2026-08', 'nama': 'Pekerja Contoh', 'bulan': '2026-08', 'hari': dict(('2026-08-%02d' % d, 1) for d in range(20, 32))},
                    {'id': 'pekerja contoh|2026-09', 'nama': 'Pekerja Contoh', 'bulan': '2026-09', 'hari': dict(('2026-09-%02d' % d, 1) for d in range(1, 24))}],
  'pajakSetoran': [], 'pajakOmzetLuar': [], 'pelangganCatatan': [], 'pengeluaranHarian': [], 'biayaBulanan': [], 'kasbonMutasi': [], 'slipUpah': [], 'utangPemasokMutasi': [],
  'penyesuaianStok': [], 'penyesuaianKemasan': [], 'pengaturan': [], 'dokumenCetak': [], 'tutupBukuAcara': [], 'pesanan': [], 'thrPelanggan': [], 'tagihPelanggan': [], 'pelangganTitip': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 400) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var n = 9000; var W = { tanggal: '2026-09-24', jam: '10:00', kini: '2026-09-24T03:00:00.000Z', idUnik: function () { n += 1; return n; } };
var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
var BEN = keadaanAkun('ben.contoh@tokoberasmiqbal.web.app', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true });
function pada(iso) { __KINI = new Date(iso).getTime(); }
function kini() { return new Date(Date.now()); }
function kunciKe(bulan, riwayat) { terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'kunciPeriode', sampaiBulan: bulan, riwayat: riwayat || [] } }]); }
function bukaSemua() { pasok('aturanToko', cacheMentah('aturan').filter(function (d) { return d.id !== 'kunciPeriode'; })); }
function tulis(r) { if (!r || r.tolak) throw new Error('DITOLAK: ' + (r && r.tolak)); var ops = (r.dokumen || []).concat((r.hapus || []).map(function (h) { return { koleksi: h.koleksi, hapus: h.id }; })); terapkanKeCache(ops); return r; }
var BERSIH = { lokal: { antreLokal: { belum: [], ditolak: [] }, antre: [] }, parkir: [], putusanHari: {}, centang: {}, siap25b: true };
function K(tambah) { var k = JSON.parse(JSON.stringify(BERSIH)); Object.keys(tambah || {}).forEach(function (x) { k[x] = tambah[x]; }); return k; }
var butir = function (D, id) { return D.butir.find(function (b) { return b.id === id; }); };
var semula = {}; ['perangkat'].forEach(function (c) { semula[c] = cacheMentah(c).slice(); });

// ---- 1 · bulan WIB & tenggang minimal (sama dengan rules v4)
ok('WIB: 1 Sep 00:30 WIB (31 Agu 17:30 UTC) = September hari 1; tanpa get() untuk Agustus HANYA di tanggal 1 (tenggang minimal 1); bulan berjalan & sesudahnya selalu tanpa get(); dua bulan lalu tidak pernah',
  kpWib(new Date('2026-08-31T17:30:00Z')).bulan === '2026-09' && kpWib(new Date('2026-08-31T17:30:00Z')).hari === 1
  && kpBebas(kpIdx('2026-08'), new Date('2026-09-01T10:00:00+07:00')) && !kpBebas(kpIdx('2026-08'), new Date('2026-09-02T10:00:00+07:00'))
  && kpBebas(kpIdx('2026-09'), kini()) && kpBebas(kpIdx('2026-10'), kini()) && kpBebas(kpIdx('2026-07'), new Date('2026-08-01T10:00:00+07:00')) && !kpBebas(kpIdx('2026-06'), new Date('2026-08-01T10:00:00+07:00')) && KP_TENGGANG_MIN === 1);
ok('bolehDikunci: Agustus TIDAK pada 1 Sep; pada 2 Sep hanya dengan tenggang 1; tenggang bawaan 2 → mulai 3 Sep; bulan berjalan tidak pernah; tenggang di bawah minimal dinaikkan ke minimal',
  !kpBolehDikunci('2026-08', new Date('2026-09-01T10:00:00+07:00'), 1) && kpBolehDikunci('2026-08', new Date('2026-09-02T10:00:00+07:00'), 1)
  && !kpBolehDikunci('2026-08', new Date('2026-09-02T10:00:00+07:00'), 2) && kpBolehDikunci('2026-08', new Date('2026-09-03T08:00:00+07:00'), 2)
  && !kpBolehDikunci('2026-09', kini(), 1) && !kpBolehDikunci('2026-08', new Date('2026-09-01T10:00:00+07:00'), 0) && KP_TENGGANG_BAWAAN === 2 && kunciTenggang() === 2);
ok('bulan tertua yang dinilai: update = min(lama, baru); hapus = nilai lama; titik kas = nilai BARU saja; bon lama pemasok = bonTanggal (K4); pajak & jejak tidak dikunci (K6)',
  kpBulanOp({ koleksi: 'penjualan', data: { id: 1, tanggal: '2026-09-24' }, lama: { id: 1, tanggal: '2026-08-10' } }) === kpIdx('2026-08')
  && kpBulanOp({ koleksi: 'penjualan', lama: { id: 1, tanggal: '2026-08-10' }, hapus: true }) === kpIdx('2026-08')
  && kpBulanOp({ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: '2026-09-23' }, lama: { id: 'titikKas', tanggal: '2026-08-30' } }) === kpIdx('2026-09')
  && kpBulanOp({ koleksi: 'utangPemasokMutasi', data: { id: 2, tipe: 'saldoAwal', tanggal: '2026-09-24', bonTanggal: '2026-07-01' } }) === kpIdx('2026-07')
  && kpBulanOp({ koleksi: 'utangPemasokMutasi', data: { id: 3, tipe: 'saldoAwal', tanggal: '2026-09-24', bonTanggal: null } }) === 0
  && kpBulanOp({ koleksi: 'pajakSetoran', data: { id: 'ps', tanggalSetor: '2026-08-15' } }) === null && kpBulanOp({ koleksi: 'logAktivitas', data: { id: 1, pada: '2026-08-01T00:00:00Z' } }) === null
  && kpBulanOp({ koleksi: 'penjualan', data: { id: 1, tanggal: '2026-08-10', x: 1 }, lama: { x: 1, id: 1, tanggal: '2026-08-10' } }) === 'sama');

// ---- 2 · daftar periksa Agustus (24 Sep): tiap ⛔ memblokir
var D0 = kpDaftarPeriksa('2026-08', kini(), K({ siap25b: false }));
ok('⛔ putaran 25b: selama sistem lama & kasir belum siap, butir pertama memblokir (keputusan owner 25 Sep) dan kunci ditolak', !butir(D0, 'siap25b').ok && butir(D0, 'siap25b').blokir && !D0.boleh && KP_SIAP_25B === false && /25b/.test(butir(D0, 'siap25b').teks));
pada('2026-09-02T10:00:00+07:00'); var DT = kpDaftarPeriksa('2026-08', kini(), K()); pada('2026-09-24T10:00:00+07:00');
ok('⛔ tenggang: 2 Sep (tenggang 2 hari) belum boleh, kalimatnya menyebut tanggal mulai 3 Sep', !butir(DT, 'tenggang').ok && /3 Sep/.test(butir(DT, 'tenggang').ket), butir(DT, 'tenggang').ket);
var agustusBelum = { koleksi: 'penjualan', data: { id: 'x1', tanggal: '2026-08-31' } }, septBelum = { koleksi: 'penjualan', data: { id: 'x2', tanggal: '2026-09-24' } };
var DA = kpDaftarPeriksa('2026-08', kini(), K({ lokal: { antreLokal: { belum: [{ id: 'k', akunNama: 'Owner', keadaan: 'antre', dokumen: [agustusBelum] }], ditolak: [] }, antre: [] } }));
var DA2 = kpDaftarPeriksa('2026-08', kini(), K({ lokal: { antreLokal: { belum: [{ id: 'k', dokumen: [septBelum] }], ditolak: [{ id: 'd', keadaan: 'ditolak', dokumen: [agustusBelum] }] }, antre: [] } }));
var DA3 = kpDaftarPeriksa('2026-08', kini(), K({ lokal: { antreLokal: { belum: [{ id: 'k', dokumen: [septBelum] }], ditolak: [] }, antre: [] } }));
ok('⛔ catatan Agustus yang tertahan / DITOLAK di perangkat ini memblokir; yang bertanggal September tidak', !butir(DA, 'antreIni').ok && !butir(DA2, 'antreIni').ok && butir(DA3, 'antreIni').ok);
var DP = kpDaftarPeriksa('2026-08', kini(), K({ parkir: [{ pada: '2026-08-31T13:00:00.000Z', pelanggan: 'X', n: 2 }] })), DP2 = kpDaftarPeriksa('2026-08', kini(), K({ parkir: [{ pada: null, pelanggan: 'Y', n: 1 }] })), DP3 = kpDaftarPeriksa('2026-08', kini(), K({ parkir: [{ pada: '2026-09-23T03:00:00.000Z', n: 1 }] }));
ok('⛔ nota parkir Agustus (dan parkir tanpa cap waktu) memblokir; parkir September tidak', !butir(DP, 'parkir').ok && !butir(DP2, 'parkir').ok && butir(DP3, 'parkir').ok);
var D1 = kpDaftarPeriksa('2026-08', kini(), K());
ok('⛔ perangkat yang melaporkan antre > 0 memblokir, namanya disebut, dengan kalimat "akan ditolak sesudah dikunci"', !butir(D1, 'perangkatAntre').ok && butir(D1, 'perangkatAntre').blokir && /Tablet kasir/.test(butir(D1, 'perangkatAntre').rincian.join()) && /akan ditolak sesudah dikunci/.test(butir(D1, 'perangkatAntre').ket));
ok('⛔ perangkat tanpa denyut 24 jam memblokir; "sudah tidak dipakai" hanya ditawarkan untuk perangkat yang antre & ditolaknya 0',
  !butir(D1, 'perangkatDenyut').ok && /Tablet lama/.test(butir(D1, 'perangkatDenyut').rincian.join()) && butir(D1, 'perangkatDenyut').aksi.length === 1 && butir(D1, 'perangkatDenyut').aksi[0].id === 'tab-lama'
  && /antrean/.test(susunLupakanPerangkat('tab-kasir', true).tolak || '') && !!susunLupakanPerangkat('tab-lama', false).perluYakin && susunLupakanPerangkat('tab-lama', true).hapus[0].id === 'tab-lama');
ok('hari tanpa tutup: hari BERNOTA hanya bisa "diterima apa adanya" (bukan libur); hari tanpa nota boleh libur; tutup hari tidak dibuat mundur',
  D1.hari.some(function (h) { return h.iso === '2026-08-12' && h.adaJual && J(h.pilihan) === '["diterima"]'; }) && D1.hari.some(function (h) { return h.iso === '2026-08-14' && !h.adaJual && h.pilihan.indexOf('libur') >= 0; })
  && /TIDAK dibuat mundur/.test(butir(D1, 'hari').ket) && !butir(D1, 'hari').ok, J(D1.hari.slice(0, 6)));
var putusSemua = {}; D1.hari.forEach(function (h) { putusSemua[h.iso] = h.adaJual ? { jenis: 'diterima', alasan: 'hari pertama, laci belum dihitung' } : { jenis: 'libur' }; });
var libSalah = Object.assign({}, putusSemua, { '2026-08-12': { jenis: 'libur' } }), alasanPendek = Object.assign({}, putusSemua, { '2026-08-12': { jenis: 'diterima', alasan: 'ok' } });
ok('hari tanpa tutup: libur pada hari bernota DITOLAK; "diterima" tanpa alasan ≥ 5 huruf DITOLAK; semua diputuskan → butir beres',
  !butir(kpDaftarPeriksa('2026-08', kini(), K({ putusanHari: libSalah })), 'hari').ok && !butir(kpDaftarPeriksa('2026-08', kini(), K({ putusanHari: alasanPendek })), 'hari').ok && butir(kpDaftarPeriksa('2026-08', kini(), K({ putusanHari: putusSemua })), 'hari').ok);
ok('karcis darurat Agustus yang belum dirinci disebut jumlahnya dengan kalimat "sesudah dikunci, karcis ini tidak bisa dirinci lagi" (butir centang, bukan ⛔)',
  !butir(D1, 'karcis').ok && !butir(D1, 'karcis').blokir && butir(D1, 'karcis').perluCentang && /^1 karcis/.test(butir(D1, 'karcis').teks) && /sesudah dikunci, karcis ini tidak bisa dirinci lagi/.test(butir(D1, 'karcis').ket));
ok('butir centang owner: omzet luar belum diisi ("angka pajak … belum lengkap"), periksa ulang kedatangan/adukan/bon (K2), nama mirip berbon (K3), upah belum dibayar (K5)',
  butir(D1, 'omzetLuar').perluCentang && /belum lengkap/.test(butir(D1, 'omzetLuar').ket) && /sesudah dikunci tidak bisa dibetulkan/.test(butir(D1, 'pembelian').ket) && /1 kedatangan · 1 adukan/.test(butir(D1, 'pembelian').ket)
  && /Bu Sari/.test(butir(D1, 'namaMirip').rincian.join()) && /satukan dulu sebelum dikunci/.test(butir(D1, 'namaMirip').ket) && /Pekerja Contoh/.test(butir(D1, 'upah').rincian.join()) && /bulan pembayaran/.test(butir(D1, 'upah').ket), J(D1.butir.map(function (b) { return [b.id, b.ok, b.ket]; })));
pasok('perangkatStatus', semula.perangkat.filter(function (p) { return p.id === 'hp-owner'; }));
var C_SEMUA = { karcis: true, omzetLuar: true, pembelian: true, namaMirip: true, upah: true };
var DOK = kpDaftarPeriksa('2026-08', kini(), K({ putusanHari: putusSemua, centang: C_SEMUA }));
ok('semua ⛔ beres + semua keputusan & centang → boleh dikunci', DOK.boleh && DOK.belum === 0, J(DOK.butir.filter(function (b) { return !b.ok; })));
ok('kunci hanya bulan calon: September (belum lewat) & Juli (bukan urutannya) ditolak; bukan-owner ditolak',
  !!susunKunciBulan('2026-09', K(), W, OWN, kini()).tolak && !!susunKunciBulan('2026-07', K(), W, OWN, kini()).tolak && !!susunKunciBulan('2026-08', K({ putusanHari: putusSemua, centang: C_SEMUA }), W, BEN, kini()).tolak);
var RK = susunKunciBulan('2026-08', K({ putusanHari: putusSemua, centang: C_SEMUA }), W, OWN, kini()); var dk = RK.dokumen && RK.dokumen[0].data;
ok('kunci Agustus: SATU dokumen aturanToko/kunciPeriode, sampaiBulan 2026-08, riwayat +1 (aksi kunci, olehUid owner, butir periksa, keputusan per hari, potret angka)',
  !!dk && RK.dokumen.length === 1 && RK.dokumen[0].koleksi === 'aturanToko' && dk.id === 'kunciPeriode' && dk.sampaiBulan === '2026-08' && dk.riwayat.length === 1 && dk.riwayat[0].aksi === 'kunci'
  && dk.riwayat[0].olehUid === 'uid-owner' && dk.riwayat[0].periksa.length === DOK.butir.length && dk.riwayat[0].hari.length === D1.hari.length && dk.riwayat[0].potret && typeof dk.riwayat[0].potret.omzet === 'number', J(RK.tolak || dk));
tulis(RK);
ok('sesudah kunci: sampaiBulan naik ke Agustus; calon berikutnya belum ada (September masih berjalan); pada 3 Okt calon = September',
  kpKeadaan().sampai === '2026-08' && kpCalon(kini()) === null && (function () { pada('2026-10-03T10:00:00+07:00'); var c = kpCalon(kini()); pada('2026-09-24T10:00:00+07:00'); return c === '2026-09'; })());

// ---- 3 · tombol koreksi di bulan terkunci → pembalik
var KAL = /^Bulan Agustus 2026 terkunci — /;
var ikatK1 = ikatKarcis({ keranjang: [], antrean: [], aktifId: 1, idBerikut: 2 }, 'k1', kini());
var rinK1 = susunRinciDokumen(Object.assign({ keranjang: [{ id: 'b', trx: { jenis: 'karung', merkSumber: 'Angsa', jumlahKarung: 0.1, totalKg: 5, hargaTotal: 70000, hargaSatuan: 70000, hargaAsli: 70000 } }], cara: 'Tunai', pelanggan: '', potongan: 0 }, { karcis: ikatK1.karcis || { id: 'k1', nominal: 250000, jenisAsal: 'karcis' } }), W);
ok('rinci karcis Agustus → "Bulan Agustus 2026 terkunci — karcis ini tidak bisa dirinci lagi; … Cocokkan hari ini", pembalik = cocok', KAL.test(rinK1.tolak || '') && /tidak bisa dirinci lagi/.test(rinK1.tolak) && rinK1.pembalik === 'cocok', J(rinK1.tolak));
var perK1 = susunPerbaikanKarcis({ karcis: { id: 'k1' }, cara: 'Kredit', pelanggan: 'Bu Sari', keranjang: [] }, W);
var urung = susunUrungRinci({ grupNota: 'g1', asliId: 'k2' }, W);
ok('perbaiki cara bayar karcis Agustus ditolak; tarik balik rincian Agustus → pembalik RETUR hari ini', KAL.test(perK1.tolak || '') && KAL.test(urung.tolak || '') && urung.pembalik === 'retur' && /RETUR hari ini/.test(urung.tolak));
var kor = susunSimpanMasuk(Object.assign(drafDariKedatangan('b1'), { alasan: 'salah ketik harga' }), W, true), baruAgs = susunSimpanMasuk(Object.assign(drafDariKedatangan('b1'), { id: null, tanggal: '2026-08-30' }), W, true);
var hapusK = susunHapusKedatangan('b1', 'salah catat', W);
ok('kedatangan Agustus: koreksi & hapus ditolak dengan pembalik Cocokkan (K2); kedatangan BARU bertanggal Agustus juga ditolak', KAL.test(kor.tolak || '') && kor.pembalik === 'cocok' && KAL.test(hapusK.tolak || '') && hapusK.pembalik === 'cocok' && KAL.test(baruAgs.tolak || ''), J([kor.tolak, baruAgs.tolak]));
var hppA = susunKoreksiHpp('Angsa', '13500', 'salah ketik', W, true), hppB = susunKoreksiHpp('Beo', '12100', 'salah ketik', W, true);
ok('koreksi HPP: merek yang kedatangan terakhirnya di Agustus ditolak (K2: harga modal bulan terkunci); merek dengan kedatangan September tetap bisa', KAL.test(hppA.tolak || '') && /K2/.test(hppA.tolak) && !hppB.tolak, J([hppA.tolak, hppB.tolak]));
var korA = susunKoreksiAdukan('ad1', '1500000', 'lupa upah', W), hapA = susunHapusAdukan('ad1', 'salah catat', W), hapKt = susunHapusBeli('kb1', 'salah catat', W, true);
ok('adukan Agustus: koreksi biaya ditolak (K2); hapus ditolak → Cocokkan; hapus beli kantong Agustus ditolak → Cocokkan', KAL.test(korA.tolak || '') && KAL.test(hapA.tolak || '') && hapA.pembalik === 'cocok' && KAL.test(hapKt.tolak || '') && hapKt.pembalik === 'cocok');
var qk = daftarKarantina(W).antre[0]; var pLayak = qk.pilihan.find(function (p) { return p.tindakan === 'layak_jual'; }), pRework = qk.pilihan.find(function (p) { return p.tindakan === 'dirework'; });
ok('karantina: retur Agustus → "layak jual" MATI dengan kalimat kunci (pembalik = Rework hari ini); Rework tetap bisa', !pLayak.bisa && KAL.test(pLayak.sebab) && /Rework/.test(pLayak.sebab) && pRework.bisa, J([pLayak, pRework]));
var rw = susunPutusKarantina('rt1', 'dirework', 'ternyata kering', W, 'dirework');
ok('pembalik karantina: rework menulis penyesuaianStok bertanggal HARI INI (jenis lama, dariRework) — retur Agustus tidak disentuh', !rw.tolak && rw.dokumen.some(function (d) { return d.koleksi === 'penyesuaianStok' && d.data.tanggal === '2026-09-24' && d.data.dariRework; }) && !rw.dokumen.some(function (d) { return d.koleksi === 'retur'; }), J(rw.tolak || rw.dokumen));
var semuaO = semuaOrang(kini()); var kS = semuaO.find(function (o) { return o.nama === 'Bu Sari'; }), kIS = semuaO.find(function (o) { return o.nama === 'Ibu Sari'; }), kPT = semuaO.find(function (o) { return o.nama === 'Pak Tunai'; });
var gab = susunGabung(kini(), kIS.kunci, kS.kunci, W);
ok('SATUKAN (K3): nama yang bonnya lahir di bulan terkunci → ditolak dengan kalimat kunci, kedua nama dibiarkan terpisah', /^Bulan Agustus 2026 terkunci — "Bu Sari" punya bon/.test(gab.tolak || '') && /tidak bisa pindah nama/.test(gab.tolak), J(gab.tolak));
pasok('penjualan', cacheMentah('penjualan').concat([{ id: 'u1', tanggal: '2026-08-18', jam: '10:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 90000, hppTotalSaatJual: 85500, trxId: 't-u1', namaPelanggan: 'Pak Tunai Toko' }]));
var semuaO2 = semuaOrang(kini()); var kPTT = semuaO2.find(function (o) { return o.nama === 'Pak Tunai Toko'; }), kPT2 = semuaO2.find(function (o) { return o.nama === 'Pak Tunai'; });
var gab2 = susunGabung(kini(), kPT2.kunci, kPTT.kunci, W); var hn = rincianHapusNama(kini(), kPTT.kunci);
ok('SATUKAN / hapus nama tanpa bon: nota di bulan terkunci TIDAK ditulis ulang (tetap bernama lama), kalimatnya menyebutnya; nama yang semua notanya di bulan terkunci tidak bisa dihapus',
  !gab2.tolak && !gab2.dokumen.some(function (d) { return d.koleksi === 'penjualan'; }) && /bulan terkunci tetap bernama lama/.test(gab2.patch.kabar) && /Semua 1 nota/.test(hn.tolak || ''), J([gab2.tolak, gab2.patch && gab2.patch.kabar, hn.tolak]));
var up = susunBayarUpah('Pekerja Contoh', 'semua', W); var bb = (up.dokumen || []).filter(function (d) { return d.koleksi === 'biayaBulanan'; });
ok('upah (K5): hari kerja Agustus yang dibayar sesudah Agustus terkunci dibukukan ke biaya SEPTEMBER; rincian gajinya tetap membawa dari = 20 Agu; kalimatnya menyebut',
  !up.tolak && bb.length === 1 && bb[0].data.bulan === '2026-09' && bb[0].data.rincianGaji[0].dari === '2026-08-20' && bb[0].data.rincianGaji[0].hari === 35 && /Agustus|2026-08/.test(up.patch.kabar) && /bulan terkunci/.test(up.patch.kabar), J(up.tolak || bb));
var bl1 = susunBonLama({ pemasok: 'PEMASOK CONTOH', ketik: '5.000.000', tgl: '2026-08-10' }, W), bl2 = susunBonLama({ pemasok: 'PEMASOK CONTOH', ketik: '5.000.000', tgl: '2026-09-10' }, W), bl3 = susunBonLama({ pemasok: 'PEMASOK CONTOH', ketik: '5.000.000', tgl: '' }, W);
ok('bon lama pemasok (K4): bertanggal bulan terkunci / tanpa tanggal → bonTanggal HARI INI, tanggal aslinya di catatan; bertanggal bulan terbuka → apa adanya',
  bl1.dokumen[0].data.bonTanggal === '2026-09-24' && /tanggal bon asli 2026-08-10/.test(bl1.dokumen[0].data.catatan) && bl2.dokumen[0].data.bonTanggal === '2026-09-10' && bl3.dokumen[0].data.bonTanggal === '2026-09-24' && /tidak diketahui/.test(bl3.dokumen[0].data.catatan));
pada('2027-01-05T10:00:00+07:00'); var TB = tahunBuku(kini()); pada('2026-09-24T10:00:00+07:00');
ok('tutup buku (K1): tahun yang punya bulan terkunci → sungguhan DITOLAK dengan kalimat (arsip tidak boleh menghapus catatan)', !TB.bolehSungguhan && TB.adaKunci && /arsip tidak boleh menghapus/.test(TB.teks), J(TB));

// ---- 4 · penjaga pusat (toko.js) — semua tulisan layar
var a1 = ambilPenjualanSemua().find(function (p) { return p.id === 'a1'; });
var g1 = jagaKunci([{ koleksi: 'penjualan', data: Object.assign({}, a1, { hargaTotal: 1 }) }], []), g2 = jagaKunci([], [{ koleksi: 'penjualan', id: 'a1' }]), g3 = jagaKunci([{ koleksi: 'penjualan', data: { id: 'baru', tanggal: '2026-09-24' } }], []),
  g4 = jagaKunci([{ koleksi: 'penjualan', data: { id: 'mundur', tanggal: '2026-08-31' } }], []), g5 = jagaKunci([{ koleksi: 'pengaturan', data: { id: 'titikKas', tanggal: '2026-09-24' } }], []),
  g6 = jagaKunci([{ koleksi: 'pajakSetoran', data: { id: 'ps', masaPajak: '2026-08', tanggalSetor: '2026-08-15' } }], []);
ok('penjaga pusat: koreksi DI TEMPAT nota Agustus, hapus nota Agustus, dan nota BARU bertanggal Agustus → tidak dikirim ("terkunci"); nota hari ini, titik kas maju, pajak (K6) → boleh',
  !!(g1 && g1.terkunci) && !!(g2 && g2.terkunci) && !!(g4 && g4.terkunci) && g3 === null && g5 === null && g6 === null && KAL.test(g1.pesan), J([g1, g2, g4, g5]));
var besar = []; for (var i = 0; i < 19; i++) besar.push({ koleksi: 'penjualan', data: { id: 'v' + i, tanggal: '2026-09-01' } });
pada('2026-10-05T10:00:00+07:00'); var g7 = jagaKunci(besar.slice(0, 18), []), g8 = jagaKunci(besar, []); pada('2026-09-24T10:00:00+07:00');
ok('penjaga pusat: kiriman bulan lampau di luar tenggang ≤ 18 pemeriksaan boleh; 19 → tidak dikirim (batas 20, sisa 2 — cache tidak diandalkan)', g7 === null && !!g8 && /18/.test(g8.pesan), J(g8));
var PT = kpPotong(besar.concat(besar).map(function (d) { return { dokumen: [d], hapus: [] }; }), function () { return null; }, new Date('2026-10-05T10:00:00+07:00'));
var PT2 = kpPotong([{ dokumen: besar, hapus: [] }], function () { return null; }, new Date('2026-10-05T10:00:00+07:00'));
ok('kirim bertahap: 38 catatan bulan lampau → 3 potongan, tiap potongan ≤ 18 pemeriksaan; satu kelompok 19 tidak bisa dipecah → ditolak', PT.potongan.length === 3 && PT.potongan.every(function (p) { return p.get <= 18; }) && !!PT2.tolak, J(PT.potongan.map(function (p) { return p.get; })));
var terkirim = [], ke = 0, diTengah = null; setelPenulis({ tulis: function (d, h) { ke += 1; if (ke === 2) { diTengah = bertahapTertunda(); return Promise.resolve({ gagal: true, pesan: 'putus' }); } terkirim.push(d.map(function (x) { return x.data.id; }).concat((h || []).map(function (x) { return 'h' + x.id; })).join(',')); return Promise.resolve({ ok: true }); } });
var hasilBT = null, hasilLanjut = null; pada('2026-10-05T10:00:00+07:00');
tulisBertahap('uji bertahap', besar.concat(besar.map(function (d) { return { koleksi: d.koleksi, data: { id: d.data.id + 'b', tanggal: d.data.tanggal } }; })).map(function (d) { return { dokumen: [d], hapus: [] }; })).then(function (r) { hasilBT = r; });
drainMicrotasks(); var tertunda = bertahapTertunda(); lanjutkanBertahap().then(function (r) { hasilLanjut = r; }); drainMicrotasks(); pada('2026-09-24T10:00:00+07:00'); setelPenulis(null);
ok('kirim bertahap: kemajuan tersimpan SEBELUM potongan berikutnya dikirim (tab ditutup di tengah = bisa dilanjutkan); terputus di potongan 2 → berhenti (1 dari 3); dilanjutkan → potongan 2 & 3 terkirim, TIDAK ada yang dikirim dua kali; rencana dihapus sesudah selesai',
  !!hasilBT && hasilBT.gagal && diTengah && diTengah.sudah === 1 && tertunda && tertunda.sudah === 1 && tertunda.total === 3 && !!hasilLanjut && hasilLanjut.ok && terkirim.length === 3 && new Set(terkirim).size === 3 && bertahapTertunda() === null, J([hasilBT, tertunda, hasilLanjut, terkirim.length]));
var nStaf = [{ koleksi: 'penjualan', data: { id: 'sb1', tanggal: '2026-08-31', caraBayar: 'Tunai' }, ada: false, lama: null }];
pada('2026-09-01T09:00:00+07:00'); var st1 = periksaKiriman(BEN, nStaf, [], {}, kini()); pada('2026-09-02T09:00:00+07:00'); var st2 = periksaKiriman(BEN, nStaf, [], {}, kini()); pada('2026-09-24T10:00:00+07:00');
ok('bukan-owner: nota bertanggal 31 Agu yang tiba 1 Sep (masa tenggang) → boleh, 1 access call per dokumen; tiba 2 Sep → ditolak di perangkat ("lewat masa tenggang — owner yang mencatat"), rules tanpa get() kunci',
  !st1.tolak && st1.accessCall === 2 && /lewat masa tenggang/.test(st2.tolak || ''), J([st1, st2]));

// ---- 5 · pembalik bertanggal HARI INI dengan jenis lama; angka bulan terkunci tidak bergeser
var labaAgs = function () { return J([hitungLabaBersihRentang('2026-08-01', '2026-08-31'), hitungNeraca('2026-08-31')]); }; var omzetSep = function () { return hitungLabaRentang(function (t) { return !!t && t >= '2026-09-01' && t <= '2026-09-30'; }).omzetPenuh; };
var A0 = labaAgs(), S0 = omzetSep();
var RR = susunRetur(Object.assign(returAwal(), { rtNotaId: 'a1', ketik: '10', rtAlasan: 'kualitas', rtKondisi: 'utuh', rtPenyelesaian: 'refund' }), W);
ok('pembalik nota Agustus = RETUR bertanggal hari ini (jenis lama "retur"), menunjuk nota asalnya lewat field yang sudah ada (notaAsalId, notaAsalTanggal); penjaga pusat mengizinkannya',
  !RR.tolak && RR.dokumen[0].koleksi === 'retur' && RR.dokumen[0].data.tanggal === '2026-09-24' && RR.dokumen[0].data.notaAsalId === 'a1' && RR.dokumen[0].data.notaAsalTanggal === '2026-08-10' && jagaKunci(RR.dokumen, []) === null, J(RR.tolak || RR.dokumen));
tulis(RR); var A1 = labaAgs(), S1 = omzetSep();
ok('sesudah pembalik: laba & neraca Agustus BYTE-SAMA; omzet September turun persis sebesar uang kembalinya', A1 === A0 && S0 - S1 === RR.dokumen[0].data.nominalRefund && RR.dokumen[0].data.nominalRefund > 0, J([S0, S1, RR.dokumen[0].data.nominalRefund]));
var kh = kpKeHariIni([{ koleksi: 'penjualan', data: { id: 'z', tanggal: '2026-08-31', jam: '23:50', caraBayar: 'Tunai', hargaTotal: 1000 } }, { koleksi: 'stokBahanLiteran', data: { id: 'z1', tanggal: '2026-08-31', tipe: 'pakai', catatan: 'x' } }, { koleksi: 'strukKeluar', data: { id: 's', tanggal: '2026-08-31' } }], W);
ok('kiriman yang ditolak karena bulan terkunci → dicatat ulang HARI INI: tanggal & jam hari ini, tanggal asli di field teks yang SUDAH ADA (alasanKoreksi / catatan), tanpa field baru; koleksi tak dikunci tidak diubah',
  kh[0].data.tanggal === '2026-09-24' && /tanggal asli 2026-08-31 23:50/.test(kh[0].data.alasanKoreksi) && kh[1].data.tanggal === '2026-09-24' && /tanggal asli/.test(kh[1].data.catatan) && kh[2].data.tanggal === '2026-08-31'
  && Object.keys(kh[0].data).sort().join() === ['alasanKoreksi', 'caraBayar', 'hargaTotal', 'id', 'jam', 'tanggal'].join());
var dit = kpAlasanDitolak({ dokumen: [{ koleksi: 'penjualan', data: { id: 'z', tanggal: '2026-08-31' } }] }, function () { return false; }), dit2 = kpAlasanDitolak({ dokumen: [{ koleksi: 'tutupHari', data: { id: '2026-08-31', tanggal: '2026-08-31' } }] }, function () { return false; }), dit3 = kpAlasanDitolak({ dokumen: [septBelum] }, function () { return false; });
ok('daftar "ditolak server": alasan "bulan terkunci" + tawaran catat ulang hari ini untuk nota; tutup hari TIDAK ditawari catat ulang (tanggalnya bagian dari artinya); kiriman September bukan karena kunci',
  !!dit && dit.bisaHariIni && /^Bulan Agustus 2026 terkunci/.test(dit.kalimat) && !!dit2 && !dit2.bisaHariIni && dit3 === null);

// ---- 6 · buka kunci
pasok('pajakSetoran', [{ id: 'ps1', masaPajak: '2026-08', tanggalSetor: '2026-09-10', jumlah: 100000, dicatatPada: '2026-09-10' }]);
var b1 = susunBukaBulan('salah', '', W, OWN), b2 = susunBukaBulan('ada nota yang tertinggal', '', W, OWN), b3 = susunBukaBulan('ada nota yang tertinggal', 'agustus 2026', W, OWN), b4 = susunBukaBulan('ada nota yang tertinggal', 'agustus 2026', W, BEN);
ok('buka: alasan < 10 huruf ditolak; bulan yang punya setoran pajak → peringatan keras + wajib ketik ulang nama bulannya; bukan-owner ditolak', /minimal 10/.test(b1.tolak || '') && b2.perluKetik === 'Agustus 2026' && /AWAS/.test(b2.tolak) && !b3.tolak && !!b4.tolak);
var db3 = b3.dokumen[0].data;
ok('buka hanya SATU langkah: sampaiBulan 2026-08 → 2026-07; riwayat +1 entri buka dengan alasan & uid; entri lama utuh', db3.sampaiBulan === '2026-07' && db3.riwayat.length === 2 && db3.riwayat[1].aksi === 'buka' && db3.riwayat[1].bulan === '2026-08' && /tertinggal/.test(db3.riwayat[1].alasan) && J(db3.riwayat[0]) === J(dk.riwayat[0]));
tulis(b3);
ok('sesudah buka: nota Agustus bisa dikoreksi lagi; kunci berikutnya kembali ke Agustus (berurutan)', jagaKunci([{ koleksi: 'penjualan', data: Object.assign({}, a1, { hargaTotal: 1 }) }], []) === null && kpCalon(kini()) === '2026-08');

// ---- 7 · final bulanan & pajak
bukaSemua(); var f0 = lpFinal('2026-08'); kunciKe('2026-08'); var f1 = lpFinal('2026-08'), f2 = lpFinal('2026-09'), t1 = lpTahunFinal(2026); kunciKe('2026-12'); var t2 = lpTahunFinal(2026); kunciKe('2026-08');
ok('lpFinal bulanan: Agustus draf sebelum dikunci, FINAL sesudah; September draf; tahun 2026 final hanya kalau 12 bulannya terkunci (Januari–Agustus terkunci ≠ setahun final)', !f0 && f1 && !f2 && !t1 && t2);
ok('tanda lapor DK3 per bulan: Agustus terkunci boleh ditandai; September (belum dikunci) ditolak dengan kalimatnya', !susunTandaLapor('2026-08', W).tolak && /belum dikunci/.test(susunTandaLapor('2026-09', W).tolak || ''));
var TP = pjTahun(2026, kini()); var bA = TP.daftar.find(function (b) { return b.key === '2026-08'; }), bS = TP.daftar.find(function (b) { return b.key === '2026-09'; });
var sp = susunSetoran({ masaPajak: '2026-09', tanggalSetor: '2026-09-24', jumlah: '100.000', ntpn: '0123456789ABCDEF' }, W, kini()), sa = susunSetoran({ masaPajak: '2026-08', tanggalSetor: '2026-09-24', jumlah: '100.000', ntpn: '0123456789ABCDEF' }, W, kini());
ok('pajak: tiap bulan punya keadaan terkunci; setoran untuk bulan BELUM dikunci → peringatan "Kunci bulan … dulu supaya angkanya tidak bergeser"; bulan terkunci tanpa peringatan itu',
  bA.terkunci && !bS.terkunci && /Kunci bulan September 2026 dulu supaya angkanya tidak bergeser/.test(sp.peringatan) && !/Kunci bulan/.test(sa.peringatan || ''), J([sp.peringatan, sa.peringatan]));
ok('Beranda: satu baris "Kunci bulan" hanya bila bulan lalu sudah lewat tenggang & belum dikunci — dan diam selama kunci belum bisa dipakai (25b)',
  (function () { bukaSemua(); var a = kpPerhatian(kini(), { siap25b: true }), b = kpPerhatian(kini()); kunciKe('2026-08'); var c = kpPerhatian(kini(), { siap25b: true }); return a.length === 1 && /Agustus 2026/.test(a[0].teks) && b.length === 0 && c.length === 0; })());

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var salah = []; var J = JSON.stringify;
var angkaBulan = function (b) { var akhir = kpAkhirBulan(b); return J([hitungLabaBersihRentang(b + '-01', akhir), hitungLabaRentang(function (t) { return !!t && t >= b + '-01' && t <= akhir; }), hitungNeraca(akhir)]); };
var ASAP_BULAN = ['2026-07', '2026-08', '2026-09'];
var sebelum = ASAP_BULAN.map(angkaBulan);
terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'kunciPeriode', sampaiBulan: '2026-08', riwayat: [{ aksi: 'kunci', bulan: '2026-08', pada: 'uji', olehUid: 'uji' }] } }]);
var sesudahKunci = ASAP_BULAN.map(angkaBulan);
ASAP_BULAN.forEach(function (b, i) { if (sebelum[i] !== sesudahKunci[i]) salah.push(b + ': angka berubah hanya karena dikunci'); });
var nota = ambilPenjualan().filter(function (p) { return p.tanggal && p.tanggal.slice(0, 7) === '2026-08' && p.jenis === 'karung' && (p.hargaTotal || 0) > 0 && !p.namaPelanggan; })[0];
var n = 70000; var W = { tanggal: hariIniIso(new Date(Date.now())), jam: '10:00', kini: new Date(Date.now()).toISOString(), idUnik: function () { n += 1; return 'asap-' + n; } };
var koreksiDiTempat = jagaKunci([{ koleksi: 'penjualan', data: Object.assign({}, nota, { hargaTotal: 1 }) }], []);
if (!koreksiDiTempat || !koreksiDiTempat.terkunci) salah.push('koreksi di tempat nota Agustus TIDAK ditolak penjaga');
var R = susunRetur(Object.assign(returAwal(), { rtNotaId: nota.id, ketik: String(Math.min(5, nota.totalKg || 5)), rtAlasan: 'uji asap', rtKondisi: 'utuh', rtPenyelesaian: 'refund' }), W);
if (R.tolak) salah.push('pembalik ditolak: ' + R.tolak); else {
  if (jagaKunci(R.dokumen, [])) salah.push('pembalik hari ini ditolak penjaga');
  terapkanKeCache(R.dokumen);
  var sesudahPembalik = ASAP_BULAN.map(angkaBulan);
  if (sesudahPembalik[0] !== sebelum[0]) salah.push('Juli ikut berubah oleh pembalik September');
  if (sesudahPembalik[1] !== sebelum[1]) salah.push('Agustus ikut berubah oleh pembalik September');
  if (sesudahPembalik[2] === sebelum[2]) salah.push('September TIDAK berubah oleh pembaliknya');
  var dS = hitungLabaRentang(function (t) { return !!t && t.slice(0, 7) === '2026-09'; }).omzetPenuh;
}
print(JSON.stringify({ salah: salah, notaAgustus: nota ? nota.id : null, refund: R && R.dokumen ? R.dokumen[0].data.nominalRefund : null, tanggalPembalik: R && R.dokumen ? R.dokumen[0].data.tanggal : null,
  byteSama: { juli: sebelum[0] === sesudahKunci[0], agustus: sebelum[1] === sesudahKunci[1] }, bulanDiperiksa: ASAP_BULAN }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:1500]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def satu_lingkup(js):
    """teksMargin lokal stok-hpp bertabrakan dengan export teksMargin harga-logika bila keduanya dibundel satu lingkup —
    dinamai ulang HANYA di bundel uji (berkas aslinya tidak disentuh)."""
    assert js.count("const teksMargin = (m) =>") == 1 and js.count("teksMargin: teksMargin(margin)") == 1
    return js.replace("const teksMargin = (m) =>", "const hpTeksMargin = (m) =>").replace("teksMargin: teksMargin(margin)", "teksMargin: hpTeksMargin(margin)")


def utama(js):
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = satu_lingkup(bundel_baru.bundel(MODUL))
    if '--kontrol' in sys.argv:
        rusak = {
            # kontrol wajib prompt
            'koreksi di tempat pada bulan terkunci lolos (penjaga pusat tidak menilai tanggal lama)': js.replace("  if (!op.lama || (op.koleksi === 'pengaturan' && String(op.data.id) === 'titikKas')) return b;", "  return b;"),
            'pembalik bertanggal bulan terkunci (catat ulang tidak memindah tanggal)': js.replace("    data.tanggal = w.tanggal; if (data.jam !== undefined) data.jam = w.jam;", "    if (data.jam !== undefined) data.jam = w.jam;"),
            'buka dua bulan sekaligus': js.replace("sampaiBulan: kpGeser(bulan, -1), riwayat: riwayat.concat([{ aksi: 'buka'", "sampaiBulan: kpGeser(bulan, -2), riwayat: riwayat.concat([{ aksi: 'buka'"),
            'lpFinal final tanpa kunci': js.replace("const s = kunciSampai(); return !!s && String(key).slice(0, 7) <= s; }", "return true; }"),
            # daftar periksa
            '⛔ 25b diabaikan': js.replace("const siap = KP_SIAP_25B || !!K.siap25b;", "const siap = true;"),
            'tenggang tidak dinilai': js.replace("const bolehT = kpBolehDikunci(bulan, kini, tenggang);", "const bolehT = true;"),
            'tenggang minimal 0': js.replace("const KP_TENGGANG_MIN = 1;", "const KP_TENGGANG_MIN = 0;"),
            'catatan ditolak di perangkat tidak memblokir': js.replace("(AL.belum || []).concat(AL.ditolak || []).forEach(", "(AL.belum || []).forEach("),
            'parkir tanpa cap waktu dianggap aman': js.replace("const parkir = (K.parkir || []).filter((p) => !p.pada || ", "const parkir = (K.parkir || []).filter((p) => !!p.pada && "),
            'perangkat antre tidak memblokir': js.replace("tambah({ id: 'perangkatAntre', blokir: true, ok: !antreLain.length,", "tambah({ id: 'perangkatAntre', blokir: true, ok: true,"),
            'perangkat diam boleh dilupakan walau masih antre': js.replace("if (Number(p.antrean) > 0 || Number(p.gagal) > 0) return { tolak:", "if (false) return { tolak:"),
            'libur boleh di hari bernota': js.replace(": x.jenis === 'libur' && !jual[t]) ? x : null", ": x.jenis === 'libur') ? x : null"),
            '"diterima apa adanya" tanpa alasan': js.replace("x.jenis === 'diterima' ? !kpKosong(x.alasan) && String(x.alasan).trim().length >= 5", "x.jenis === 'diterima' ? true"),
            'kunci boleh bulan mana saja': js.replace("const c = kpCalon(kini); if (bulan !== c) return { tolak:", "const c = kpCalon(kini); if (false) return { tolak:"),
            'alasan buka tidak dinilai': js.replace("if (a.length < 10) return { tolak: 'Alasan membuka kunci wajib", "if (false) return { tolak: 'Alasan membuka kunci wajib"),
            'bulan bersetoran tanpa ketik ulang': js.replace("if (setor.length && String(ketikUlang || '').trim().toLowerCase() !== kpNamaBulan(bulan).toLowerCase())", "if (false)"),
            # jalur koreksi
            'rinci karcis bulan terkunci lolos': js.replace("const kunci = tolakKunci('penjualan', p, KC_TERKUNCI); if (kunci) return { tolak: kunci, pembalik: 'cocok' };", ""),
            'tarik balik rincian bulan terkunci lolos': js.replace("  if (terkunci) return { tolak: terkunci, pembalik: 'retur' };", ""),
            'koreksi kedatangan bulan terkunci lolos': js.replace("  if (kunci) return { tolak: kunci, pembalik: lama ? 'cocok' : '' };", ""),
            'koreksi HPP bulan terkunci lolos (penjaga HPP & penjaga koreksi kedatangan dicabut)': js.replace("const kunci = tolakKunciTanggal(target.tanggal, ", "const kunci = '' && tolakKunciTanggal(target.tanggal, ").replace("  if (kunci) return { tolak: kunci, pembalik: lama ? 'cocok' : '' };", ""),
            'adukan bulan terkunci lolos': js.replace("const adKunci = (batch, pembalik) => (adKelompok()[String(batch)] || [])", "const adKunci = (batch, pembalik) => ([])"),
            'karantina layak jual bulan terkunci lolos': js.replace("const kunci = tolakKunci('retur', r, 'retur ini tidak bisa diubah jadi \"utuh\"; pilih \"Rework\" — barangnya kembali ke stok HARI INI'); if (kunci) return kunci;", ""),
            'SATUKAN menulis ulang nota bulan terkunci': js.replace("const penjualan = semuaJual.filter((p) => !tolakKunci('penjualan', p, '')); const tetap = semuaJual.length - penjualan.length; const pesanan", "const penjualan = semuaJual; const tetap = 0; const pesanan"),
            'SATUKAN memindah bon bulan terkunci': js.replace("  if (bonKunci) return { tolak:", "  if (false) return { tolak:"),
            'upah menulis biaya bulan terkunci (K5)': js.replace("Object.keys(perBulan).forEach((b) => { if (b === bulanBayar || !tolakKunciTanggal(b + '-01', '')) return;", "Object.keys(perBulan).forEach((b) => { if (true) return;"),
            'bon lama tetap bertanggal bulan terkunci (K4)': js.replace("const keHariIni = !!sampai && (!D.tgl || D.tgl.slice(0, 7) <= sampai);", "const keHariIni = false;"),
            'tutup buku tidak peduli kunci (K1)': js.replace("const sampai = kunciSampai(); const adaKunci = !!sampai && sampai >= tahun + '-01';", "const sampai = kunciSampai(); const adaKunci = false;"),
            # penjaga pusat & bertahap
            'penjaga pusat tanpa batas pemeriksaan': js.replace("if (N.perluGet > KP_BATAS_GET) return { gagal: true,", "if (false) return { gagal: true,"),
            'pajak ikut dikunci (melawan K6)': js.replace("  biayaBulanan: 'bulan', tutupHari: 'tanggal',", "  biayaBulanan: 'bulan', pajakSetoran: 'tanggalSetor', tutupHari: 'tanggal',"),
            'kirim bertahap melebihi 18 per potongan': js.replace("if (kini_.get + g > KP_BATAS_GET && (kini_.dokumen.length || kini_.hapus.length))", "if (false)"),
            'kirim bertahap tidak menyimpan kemajuan': js.replace("    r.sudah += 1; simpanBertahap(r); if (progres)", "    r.sudah += 1; if (progres)"),
            'bukan-owner boleh menulis bulan lalu sesudah tenggang': js.replace("if (lewat.length) return { tolak: 'Catatan bertanggal ' + kpNamaBulan(lewat[0].bulan)", "if (false) return { tolak: 'Catatan bertanggal ' + kpNamaBulan(lewat[0].bulan)"),
            'WIB dihitung sebagai UTC': js.replace("export const KP_WIB_MS = 25200000;", "export const KP_WIB_MS = 0;").replace("const KP_WIB_MS = 25200000;", "const KP_WIB_MS = 0;"),
            'catat ulang ke tanggal tanpa jejak asli': js.replace("    data[f] = (data[f] ? String(data[f]) + ' · ' : '') + 'tanggal asli ' + asli + ' (bulan terkunci, dicatat ulang ' + w.tanggal + ')';", "    void asli;"),
            # final & pajak
            'tahun final dari Januari saja': js.replace("const s = kunciSampai(); return !!s && s >= tahun + '-12'; }", "const s = kunciSampai(); return !!s && s >= tahun + '-01'; }"),
            'peringatan pajak hilang': js.replace("return pjTerkunci(key) ? '' : 'Kunci bulan '", "return true ? '' : 'Kunci bulan '"),
            'Beranda diam walau siap': js.replace("  const c = kpCalon(kini); if (!c || !kpBolehDikunci(c, kini, kunciTenggang())) return [];", "  return [];"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, 'backup-batch-*.json')), key=os.path.basename)
    if cad and not g:
        h, e = jalan(JAM_TETAP.replace("'2026-09-24T10:00:00+07:00'", "'2026-09-25T10:00:00+07:00'") + js + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if h is None: print('ASAP JATUH: ' + e); sys.exit(2)
        print('ASAP DATA TOKO (%s): %s' % (os.path.basename(cad[-1]), json.dumps(h, ensure_ascii=False)))
        if h['salah']: sys.exit(2)
    sys.exit(1 if g else 0)
