#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_uang_karyawan.py — putaran 29 Bagian 1 & 3 (owner 27 Sep 2026): TIGA TUJUAN uang keluar (toko · karyawan · pribadi) + kartu "LABA KOTOR → KE MANA".
  · "Untuk karyawan" = kolom `untuk` di pengeluaranHarian; kategorinya TETAP toko/tokoDompet → laba bersih turun SAMA seperti biaya toko (arti tidak berubah).
  · Pribadi tetap bentuk lama (kategori owner, tanpa `untuk`). Catatan lama tanpa `untuk` = BELUM DIPILAH: dihitung di biaya toko, jumlahnya disebut.
  · Atur: perluKaryawan; satu nama tidak boleh di toko DAN karyawan; tombol rutin punya tujuan; semua penulis otomatis (admin pindah, titipan, tagihan tambahan, MDR) menulis 'toko'.
  · Kartu per bulan: laba kotor → biaya toko → biaya karyawan (upah + non-upah, dipisah) → hapus buku → susut & selisih (di BAWAH laba kotor) → = laba bersih mesin →
    ambil pribadi owner → sisa. Semua dari hitungLabaBersihRentang + bayaranBiayaBulanan yang sama; wajib MENUTUP persis. Bulan terkunci = final; bulan tanpa catatan disebut.
KOTAK PASIR (ANGKA CONTOH, nama rekaan), jam dikunci 19 Sep 2026 10:00 WIB. Cadangan toko di _privat/ (asap): kartu tiap bulan menutup ke mesin laba, dan
ASAP GLOBAL: omzet/laba/inti/neraca tiap bulan BYTE-SAMA dengan kode main (kategori baru tidak boleh mengubah angka lama).

    python3 alat-uji/uji_uang_karyawan.py            → N lulus · 0 gagal
    python3 alat-uji/uji_uang_karyawan.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_laporan_baru  # noqa: E402
import uji_wadah_bernama  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_laporan_baru.MODUL
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(id, tgl, jam, cara, merk, kg, harga, hpp, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': jam, 'caraBayar': cara, 'jenis': 'karung', 'merkSumber': merk, 'totalKg': kg, 'beratKarungAcuan': 50, 'jumlahKarung': kg / 50, 'hargaTotal': harga, 'hppTotalSaatJual': hpp, 'trxId': 't' + str(id)}
    d.update(k); return d


# ---- ANGKA CONTOH. Sep: omzet 1.450.000 (j1 500.000 tunai · j2 700.000 QRIS · j4 250.000 tunai), HPP 1.345.500 → laba kotor 104.500.
#      Uang keluar Sep: h1 toko 'Bensin antar' 20.000 TANPA untuk (belum dipilah) · h2 owner 100.000 · mdr 1.800 (toko, rekening) · h4 tokoDompet lakban 120.000 untuk toko ·
#      h5 toko 'Rokok' 30.000 UNTUK KARYAWAN · h6 toko 'Biaya admin BI-FAST' 2.500 (dariBayarBon, untuk toko). Tagihan Sep: listrik 350.000 (10 Sep). Gaji Sep: Pekerja A 600.000 kotor (18 Sep).
#      Hapus buku 50.000 · susut −7.000 · tarik modal 50.000 (18 Sep) · kasbon A 200.000 (bukan biaya).
KOTAK = {
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-08-20', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'utang', 'biayaBongkar': 0,
                  'merkList': [{'id': 'b10', 'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 20, 'totalKg': 1000, 'hargaPerKg': 13000, 'subtotalHarga': 13000000}]}],
  'penjualan': [jual('a1', '2026-08-25', '09:00', 'Tunai', 'Angsa', 50, 700000, 650000), jual('j1', '2026-09-16', '09:00', 'Tunai', 'Angsa', 35.7, 500000, 464100),
                jual('j2', '2026-09-17', '10:00', 'QRIS', 'Angsa', 50, 700000, 650000), jual('j4', '2026-09-19', '09:40', 'Tunai', 'Angsa', 17.8, 250000, 231400)],
  'pengeluaranHarian': [{'id': 'h1', 'kategori': 'toko', 'tanggal': '2026-09-16', 'jam': '09:15', 'keterangan': 'Bensin antar', 'nominal': 20000},
                        {'id': 'h2', 'kategori': 'owner', 'tanggal': '2026-09-17', 'jam': '11:02', 'keterangan': 'Belanja dapur', 'nominal': 100000},
                        {'id': 'mdr-2026-09-17', 'kategori': 'toko', 'untuk': 'toko', 'tanggal': '2026-09-17', 'jam': '21:00', 'keterangan': 'Potongan QRIS (MDR)', 'nominal': 1800, 'mdr': True, 'dari': 'rekening'},
                        {'id': 'h4', 'kategori': 'tokoDompet', 'untuk': 'toko', 'tanggal': '2026-09-11', 'jam': '14:00', 'keterangan': 'Beli lakban', 'nominal': 120000},
                        {'id': 'h5', 'kategori': 'toko', 'untuk': 'karyawan', 'tanggal': '2026-09-12', 'jam': '15:00', 'keterangan': 'Rokok', 'nominal': 30000, 'dari': 'laci'},
                        {'id': 'h6', 'kategori': 'toko', 'untuk': 'toko', 'tanggal': '2026-09-14', 'jam': '10:00', 'keterangan': 'Biaya admin BI-FAST — bayar bon', 'nominal': 2500, 'dari': 'rekening', 'dariBayarBon': 'x'},
                        {'id': 'h7', 'kategori': 'toko', 'tanggal': '2026-08-25', 'jam': '08:00', 'keterangan': 'Bensin antar', 'nominal': 30000}],
  'biayaBulanan': [{'id': '2026-08', 'bulan': '2026-08', 'listrik': 350000, 'internet': 0, 'akses': 0, 'keamanan': 0, 'tanggalBayarPos': {'listrik': '2026-08-10', 'gaji': '2026-08-31'},
                    'rincianGaji': [{'nama': 'Pekerja A', 'hari': 26, 'gaji': 1560000}], 'tanggalBayarGaji': {'Pekerja A': '2026-08-31'}, 'gaji': 1560000, 'gajiHariOrang': 26},
                   {'id': '2026-09', 'bulan': '2026-09', 'listrik': 350000, 'internet': 0, 'akses': 0, 'keamanan': 0, 'tanggalBayarPos': {'listrik': '2026-09-10'},
                    'rincianGaji': [{'nama': 'Pekerja A · 18 Sep 2026', 'hari': 10, 'gaji': 600000, 'orang': 'Pekerja A', 'dari': '2026-09-01', 'sampai': '2026-09-18', 'sistemBaru': True}], 'tanggalBayarGaji': {'Pekerja A · 18 Sep 2026': '2026-09-18'}, 'gaji': 600000, 'gajiHariOrang': 10}],
  'kasbonMutasi': [{'id': 701, 'tipe': 'ambil', 'namaPegawai': 'Pekerja A', 'nominal': 200000, 'tanggal': '2026-09-05', 'catatan': 'Keperluan keluarga'}],
  'piutangMutasi': [{'id': 801, 'tipe': 'hapusBuku', 'namaPelanggan': 'Pembeli Contoh', 'nominal': 50000, 'tanggal': '2026-09-15', 'jam': '09:00'}],
  'penyesuaianStok': [{'id': 'ps1', 'tanggal': '2026-09-13', 'jam': '20:00', 'merk': 'Angsa', 'kgSistem': 100, 'kgFisik': 99.5, 'selisihKg': -0.5, 'alasan': 'Cocokkan', 'nilaiRp': -7000, 'hppPerKgSaatOpname': 14000}],
  'modalOwner': [{'id': 'm1', 'tanggal': '2026-08-08', 'jam': '08:00', 'tipe': 'setor', 'nominal': 25000000, 'catatan': 'Tabungan pribadi'}, {'id': 'm2', 'tanggal': '2026-09-18', 'jam': '17:00', 'tipe': 'tarik', 'nominal': 50000, 'catatan': 'Tarik'}],
  'utangPemasokMutasi': [], 'utangOwnerMutasi': [], 'amplopLaba': [], 'pindahUang': [], 'tutupHari': [], 'setoranKas': [], 'absenKaryawan': [], 'slipUpah': [], 'persetujuan': [], 'aturanToko': [], 'pengaturan': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
var KINI = new Date(Date.now()); var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 9000; return function () { n += 1; return n; }; })() };
var tulis = function (r) { if (r.tolak) throw new Error('DITOLAK: ' + r.tolak); if (r.hapus) terapkanKeCache(r.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (r.dokumen) terapkanKeCache(r.dokumen); return r; };
var LM = function () { return hitungLabaBersihRentang('2026-09-01', '2026-09-30'); };
var brs = function (M, id) { return M.baris.find(function (b) { return b.id === id; }); };
var menutup = function (M) { var jml = M.baris.filter(function (b) { return ['kotor', 'toko', 'upah', 'karyawan', 'hapus', 'susut'].indexOf(b.id) >= 0; }).reduce(function (a, b) { return a + b.n; }, 0); return Math.abs(jml - brs(M, 'bersih').n) < 0.5 && Math.abs(brs(M, 'bersih').n + brs(M, 'prive').n - brs(M, 'sisa').n) < 0.5; };

// ==================== BAGIAN 3 · LABA KOTOR → KE MANA (sebelum ada catatan hari ini) ====================
var L0 = LM(); var M = keManaLabaKotor('2026-09', KINI);
ok('kartu Sep: laba kotor = margin mesin 104.500; laba bersih = mesin; MENUTUP (kotor − toko − upah − karyawan − hapus buku + susut = bersih; bersih − prive = sisa) — dua penjumlahan pembaca', M.labaKotor === 104500 && M.labaKotor === L0.margin && M.labaBersih === L0.labaBersih && M.menutup && menutup(M), J(M.baris));
ok('biaya karyawan dipisah: upah = jatah gaji KOTOR Sep 600.000 (1 baris gaji); non-upah = 30.000 (1 catatan untuk karyawan: rokok); biaya toko = harian toko 20.000 + 120.000 + 1.800 + 2.500 + jatah listrik 350.000 = 494.300', M.upah === 600000 && M.nonUpah === 30000 && M.biayaKaryawan === 630000 && M.biayaToko === 494300 && M.posLain === 350000, J([M.upah, M.nonUpah, M.biayaToko, M.posLain, M.pilah]));
ok('biaya toko + biaya karyawan = biayaToko mesin (harian + jatah bulanan) — tidak ada rumus laba baru', Math.abs(M.biayaToko + M.biayaKaryawan - L0.biayaToko) < 0.5 && Math.abs(M.pilah.total - L0.harianToko) < 0.5, J([M.biayaToko, M.biayaKaryawan, L0.biayaToko]));
ok('catatan lama tanpa `untuk` = BELUM DIPILAH: 1 catatan 20.000, dihitung di biaya toko dan disebut di keterangan barisnya; potongan QRIS 1.800 & biaya bank 2.500 disebut di dalam biaya toko', M.belumDipilah === 1 && M.belumDipilahRp === 20000 && brs(M, 'toko').belumDipilah === 1 && /potongan QRIS Rp1\.800/.test(brs(M, 'toko').ket) && /biaya bank Rp2\.500/.test(brs(M, 'toko').ket) && M.pilah.mdr === 1800 && M.pilah.bank === 2500, J(brs(M, 'toko')));
ok('hapus buku 50.000 & susut −7.000 di BAWAH laba kotor (baris sendiri, tanda apa adanya); ambil pribadi = prive laci 100.000 + tarik modal 50.000 = 150.000; sisa = bersih − 150.000', brs(M, 'hapus').n === -50000 && brs(M, 'susut').n === -7000 && M.prive === 150000 && M.priveRinci.tarik === 50000 && M.sisa === M.labaBersih - 150000 && brs(M, 'sisa').n === M.sisa, J([M.prive, M.priveRinci, M.sisa]));
ok('urutan baris: kotor → toko → upah → karyawan → hapus → susut → bersih → prive → sisa; bersih & sisa & kotor berkelas jumlah', M.baris.map(function (b) { return b.id; }).join() === 'kotor,toko,upah,karyawan,hapus,susut,bersih,prive,sisa' && brs(M, 'kotor').kelas === 'jumlah' && brs(M, 'bersih').kelas === 'jumlah' && brs(M, 'sisa').kelas === 'jumlah');
ok('Sep = berjalan, belum final; Agustus tanpa kunci = belum final; Juli tanpa satu catatan pun → tanpaCatatan (bukan nol)', M.berjalan && !M.final && !keManaLabaKotor('2026-08', KINI).final && keManaLabaKotor('2026-07', KINI).tanpaCatatan && !M.tanpaCatatan);
pasok('aturanToko', [{ id: 'kunciPeriode', sampaiBulan: '2026-08', riwayat: [] }]);
var M8 = keManaLabaKotor('2026-08', KINI); ok('Agustus terkunci → FINAL; kartunya tetap menutup (harian 30.000 belum dipilah, gaji Agu 1.560.000, listrik 350.000)', M8.final && M8.menutup && menutup(M8) && M8.belumDipilah === 1 && M8.upah === 1560000 && M8.posLain === 350000, J(M8.baris));
pasok('aturanToko', []);
ok('pct: biaya karyawan 630.000 dari laba kotor 104.500 = 602,9%; laba kotor 0 → "—"', M.pct(630000) === '602,9%' && keManaLabaKotor('2026-07', KINI).pct(1) === '—');

// ==================== BAGIAN 1 · TIGA TUJUAN ====================
ok('tiga tujuan: toko · karyawan · pribadi', TUJUAN_KELUAR.map(function (t) { return t[0]; }).join() === 'toko,karyawan,pribadi');
var AK = aturKeluar('2026-09-19');
ok('keperluan TERUKUR per tujuan: toko dari catatan toko yang bukan karyawan (Bensin antar 2×, lakban, …); karyawan dari catatan untuk karyawan (Rokok 1× → biasa 0); biaya admin & potongan QRIS tidak masuk daftar', AK.terukurKaryawan && AK.perluKaryawan.length === 1 && AK.perluKaryawan[0].nama === 'Rokok' && AK.perluKaryawan[0].biasa === 0 && AK.perluToko.some(function (p) { return p.nama === 'Bensin antar'; }) && !AK.perluToko.some(function (p) { return /rokok|biaya admin|potongan/i.test(p.nama); }), J([AK.perluToko, AK.perluKaryawan]));
ok('perluUntuk memilih daftar menurut tujuan', perluUntuk(AK, 'karyawan') === AK.perluKaryawan && perluUntuk(AK, 'pribadi') === AK.perluPribadi && perluUntuk(AK, 'toko') === AK.perluToko);
var H = hitungKeluar({ untuk: 'karyawan', dari: 'laci', perlu: 'Rokok', ketik: '25.000' }, KINI);
ok('untuk karyawan dari laci: arti "beban" (biaya toko), cap "untuk karyawan", laci berkurang, LABA BERKURANG 25.000, disebut dipilah sebagai biaya karyawan', !H.tolak && H.arti.sel === 'beban' && H.arti.cap === 'untuk karyawan' && /Laci berkurang Rp25\.000/.test(H.arti.a) && /laba berkurang Rp25\.000/.test(H.arti.b) && /biaya karyawan/.test(H.arti.c), J(H.arti));
H = hitungKeluar({ untuk: 'karyawan', dari: 'dompet', perlu: 'Rokok', ketik: '25.000' }, KINI);
ok('untuk karyawan pakai dompet owner: toko berutang ke owner (sel utang), laba berkurang, dipilah karyawan', H.arti.sel === 'utang' && /tidak berkurang/.test(H.arti.a) && /berutang Rp25\.000 ke owner/.test(H.arti.c) && /biaya karyawan/.test(H.arti.c), J(H.arti));
ok('untuk toko & pribadi tidak berubah artinya (biaya toko · ambil pribadi · bukan urusan toko)', hitungKeluar({ untuk: 'toko', dari: 'laci', perlu: 'Bensin antar', ketik: '1000' }, KINI).arti.cap === 'biaya toko' && hitungKeluar({ untuk: 'pribadi', dari: 'laci', perlu: 'Belanja dapur', ketik: '1000' }, KINI).arti.sel === 'prive' && hitungKeluar({ untuk: 'pribadi', dari: 'dompet', perlu: 'x', ketik: '1000' }, KINI).arti.sel === 'luar');
// "untuk karyawan" mengurangi laba bersih SAMA seperti biaya toko
var Rk = tulis(susunKeluar({ untuk: 'karyawan', dari: 'laci', perlu: 'Rokok', ketik: '25.000' }, W)); var L1 = LM(); var Mk = keManaLabaKotor('2026-09', KINI);
ok('dokumen karyawan = pengeluaranHarian {kategori toko, untuk karyawan, dari laci} bentuk lama + dua kolom; laba bersih turun 25.000; kartu: non-upah +25.000, biaya toko TETAP, masih menutup', Rk.dokumen[0].koleksi === 'pengeluaranHarian' && Rk.dokumen[0].data.kategori === 'toko' && Rk.dokumen[0].data.untuk === 'karyawan' && Rk.dokumen[0].data.dari === 'laci' && L1.labaBersih === L0.labaBersih - 25000 && Mk.nonUpah === 55000 && Mk.biayaToko === M.biayaToko && Mk.menutup && menutup(Mk), J([Rk.dokumen, L1.labaBersih, L0.labaBersih, Mk.nonUpah]));
tulis(susunUrungKeluar(Rk.urung)); var Rt = tulis(susunKeluar({ untuk: 'toko', dari: 'laci', perlu: 'Bensin antar', ketik: '25.000' }, W)); var L2 = LM(); var Mt = keManaLabaKotor('2026-09', KINI);
ok('yang sama untuk toko: dokumen {kategori toko, untuk toko}; laba bersih turun 25.000 juga (arti sama, cuma pemilahan beda): biaya toko +25.000, non-upah tetap', Rt.dokumen[0].data.untuk === 'toko' && L2.labaBersih === L0.labaBersih - 25000 && Mt.biayaToko === M.biayaToko + 25000 && Mt.nonUpah === 30000 && Mt.menutup, J([L2.labaBersih, Mt.biayaToko]));
tulis(susunUrungKeluar(Rt.urung));
var Rd = tulis(susunKeluar({ untuk: 'karyawan', dari: 'dompet', perlu: 'Rokok', ketik: '10.000' }, W));
ok('karyawan pakai dompet → kategori tokoDompet + untuk karyawan, tanpa dari; utang toko ke owner 120.000 (lakban) + 10.000; laba turun 10.000; kartu non-upah 40.000', Rd.dokumen[0].data.kategori === 'tokoDompet' && Rd.dokumen[0].data.untuk === 'karyawan' && Rd.dokumen[0].data.dari === undefined && hitungUtangOwner().sisa === 130000 && LM().labaBersih === L0.labaBersih - 10000 && keManaLabaKotor('2026-09', KINI).nonUpah === 40000, J(Rd.dokumen));
tulis(susunUrungKeluar(Rd.urung));
var Rp = tulis(susunKeluar({ untuk: 'pribadi', dari: 'laci', perlu: 'Belanja dapur', ketik: '20.000' }, W, { alasan: 'Sudah diperhitungkan' }));   // laba bersih Sep minus → batas aman 0 → wajib alasan
ok('pribadi tetap bentuk lama: kategori owner TANPA kolom untuk; laba tidak berubah; kartu: ambil pribadi +20.000, sisa −20.000', Rp.dokumen[0].data.kategori === 'owner' && !('untuk' in Rp.dokumen[0].data) && LM().labaBersih === L0.labaBersih && keManaLabaKotor('2026-09', KINI).prive === 170000 && keManaLabaKotor('2026-09', KINI).sisa === M.sisa - 20000, J(Rp.dokumen));
var Rk2 = tulis(susunKeluar({ untuk: 'karyawan', dari: 'laci', perlu: 'Kopi', ketik: '12.000', catatan: 'dua gelas' }, W));
var BK = bukuKeluar('2026-09-19');
ok('buku hari ini: baris karyawan bercap "untuk karyawan" & untuk = karyawan; jumlah.karyawan 12.000; prive 20.000; baris pribadi tidak bercap "belum dipilah"', BK.rows.some(function (r) { return r.untuk === 'karyawan' && r.cap === 'untuk karyawan' && r.ket === 'Kopi — dua gelas'; }) && BK.jumlah.karyawan === 12000 && BK.jumlah.prive === 20000 && BK.rows.filter(function (r) { return r.sel === 'prive'; }).every(function (r) { return r.cap === 'ambil pribadi'; }), J(BK.rows));
pasok('pengeluaranHarian', ambilPengeluaranHarian().concat([{ id: 'h9', kategori: 'toko', tanggal: '2026-09-19', jam: '08:00', keterangan: 'Lakban', nominal: 3000 }]));
ok('catatan hari ini tanpa `untuk` (sistem lama) bercap "biaya toko · belum dipilah"', bukuKeluar('2026-09-19').rows.find(function (r) { return r.id === 'h9'; }).cap === 'biaya toko · belum dipilah');
pasok('pengeluaranHarian', ambilPengeluaranHarian().filter(function (h) { return h.id !== 'h9'; }));
// Atur: daftar karyawan, kembar ditolak, pindah tombol antar tujuan
ok('atur: nama yang ada di toko DAN karyawan ditolak', /ada di keperluan toko DAN karyawan/.test(susunAturKeluar({ perluToko: [{ nama: 'Kopi', biasa: '10.000' }], perluKaryawan: [{ nama: 'kopi', biasa: '' }], perluPribadi: [], bulanan: [] }, W).tolak));
var RA = tulis(susunAturKeluar({ perluToko: [{ nama: 'Bensin antar', biasa: '20.000' }, { nama: 'Telur 1 kg', biasa: '27.000' }], perluKaryawan: [{ nama: 'Kopi', biasa: '11.000' }, { nama: 'Rokok', biasa: '' }], perluPribadi: [{ nama: 'Belanja dapur', biasa: '' }], bulanan: [], aman: '', alasan: [] }, W));
AK = aturKeluar('2026-09-19');
ok('atur tersimpan: dokumen aturanToko/uangKeluar membawa perluKaryawan; dibaca kembali: 2 toko, 2 karyawan (Kopi biasa 11.000 = tombol rutin), 1 pribadi; kabar menyebut 2 karyawan', RA.dokumen[0].data.id === 'uangKeluar' && RA.dokumen[0].data.perluKaryawan.length === 2 && AK.perluKaryawan[0].nama === 'Kopi' && AK.perluKaryawan[0].biasa === 11000 && AK.perluToko.length === 2 && !AK.terukurKaryawan && /2 karyawan/.test(RA.patch.kabar), J([RA.dokumen[0].data, AK.perluKaryawan]));
// pindah tombol = daftar yang sama disimpan ulang dengan barisnya berpindah (layar: ukAturPindah)
var pindah = { perluToko: [{ nama: 'Bensin antar', biasa: '20.000' }], perluKaryawan: [{ nama: 'Kopi', biasa: '11.000' }, { nama: 'Rokok', biasa: '' }, { nama: 'Telur 1 kg', biasa: '27.000' }], perluPribadi: [{ nama: 'Belanja dapur', biasa: '' }], bulanan: [{ nama: 'Air PDAM', biasa: '80.000' }], aman: '', alasan: [] };
tulis(susunAturKeluar(pindah, W)); AK = aturKeluar('2026-09-19');
ok('memindahkan "Telur 1 kg" toko → karyawan: nama & nominal biasanya ikut; hitungKeluar untuk karyawan mengenalnya sebagai keperluan (biasa 27.000)', AK.perluKaryawan.some(function (p) { return p.nama === 'Telur 1 kg' && p.biasa === 27000; }) && !AK.perluToko.some(function (p) { return p.nama === 'Telur 1 kg'; }) && hitungKeluar({ untuk: 'karyawan', dari: 'laci', perlu: 'Telur 1 kg', ketik: '27.000' }, KINI).perlu.biasa === 27000, J(AK));
// penulis otomatis menulis tujuan toko
pasok('persetujuan', [{ id: 'p1', dari: 'Pekerja A', peran: 'karyawan', tindakan: 'uangKeluar', teks: 'Tali rafia', nominal: 15000, tanggal: '2026-09-19', jam: '10:42', status: 'menunggu', pada: '2026-09-19T03:42:00.000Z' }]);
var RT = susunPutusTitipan('p1', true, '', W); var RP1 = susunPindah({ dari: 'rekening', ke: 'laci', ketik: '100.000', alasan: 'Tarik tunai dari bank', adminI: 1 }, W);
var RB = susunBayarTagihan('tambahan:Air PDAM', '', 'laci', W);
ok('titipan tablet disetujui, biaya admin pindah uang, tagihan tambahan: semuanya untuk = toko (tumpukan belum dipilah tidak bertambah)', RT.dokumen[1].data.untuk === 'toko' && RP1.dokumen[1].data.untuk === 'toko' && RP1.dokumen[1].data.dari === 'rekening' && RB.dokumen[0].data.untuk === 'toko', J([RT.dokumen[1].data, RP1.dokumen[1].data, RB.dokumen[0].data]));
// pilahHarian langsung
var P = pilahHarian('2026-09-01', '2026-09-30');
ok('pilahHarian Sep: total = harianToko mesin; karyawan 42.000 (rokok 30.000 + kopi 12.000); belum dipilah 1 × 20.000; toko dipilah 124.300; mdr 1.800; bank 2.500; jumlah catatan menutup', Math.abs(P.total - LM().harianToko) < 0.5 && P.karyawan === 42000 && P.nBelum === 1 && P.belum === 20000 && P.toko === 124300 && P.mdr === 1800 && P.bank === 2500 && P.n === P.nToko + P.nKaryawan + P.nBelum, J(P));
ok('priveRentang Sep = 100.000 + 20.000 (laci) + 50.000 tarik modal = 170.000; priveBulan (sampai hari ini) sama', priveRentang('2026-09-01', '2026-09-30').total === 170000 && priveBulan('2026-09-19').total === 170000);

// ==================== ASAP: cadangan toko ====================
var asap = null;
if (CADANGAN) {
  Object.keys(CADANGAN).forEach(function (n) { if (Array.isArray(CADANGAN[n])) pasok(n, CADANGAN[n]); });
  localStorage.removeItem('miqbal_titik_kas_v1'); var kini2 = new Date(Date.now()); var bulan = daftarBulan(kini2, 36); var salah = [];
  var tiap = bulan.map(function (b) { var Mb = keManaLabaKotor(b.key, kini2); var LMb = hitungLabaBersihRentang(b.key + '-01', akhirBulanIso(b.key)); if (!Mb.tanpaCatatan && (!Mb.menutup || !menutup(Mb) || Mb.labaBersih !== LMb.labaBersih || Math.abs(Mb.biayaToko + Mb.biayaKaryawan - LMb.biayaToko) >= 0.5)) salah.push(b.key);
    return b.key + ': ' + (Mb.tanpaCatatan ? 'tanpa catatan' : 'menutup · belum dipilah ' + Mb.belumDipilah + ' · karyawan ' + Mb.pilah.nKaryawan + ' · ' + (Mb.final ? 'final' : 'draf')); });
  var Pc = pilahHarian('2000-01-01', '2099-12-31'); var AKc = aturKeluar(hariIniIso(kini2));
  asap = { salah: salah, tiap: tiap, semuaCatatan: { n: Pc.n, belumDipilah: Pc.nBelum, karyawan: Pc.nKaryawan, toko: Pc.nToko }, perluKaryawan: AKc.perluKaryawan.map(function (p) { return p.nama; }), terukurKaryawan: AKc.terukurKaryawan };
  ok('ASAP: kartu tiap bulan menutup ke mesin laba; biaya toko + karyawan = biaya toko mesin', !salah.length, J(asap));
}
print(J({ lulus: lulus, gagal: gagal, asap: asap }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def utama(js, pakai_cadangan):
    cad = 'null'; p = uji_wadah_bernama.cadangan_toko() if pakai_cadangan else None
    if p: cad = uji_wadah_bernama.cad_js(p)[0]
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar CADANGAN = ' + cad + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    return h['lulus'], h['gagal'], h.get('asap')


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            'untuk karyawan ditulis kategori owner (keluar dari laba)': js.replace("if (kategori !== 'owner') data.untuk = D.untuk === 'karyawan' ? 'karyawan' : 'toko';", "if (kategori !== 'owner') data.untuk = D.untuk === 'karyawan' ? 'karyawan' : 'toko'; if (D.untuk === 'karyawan') data.kategori = 'owner';"),
            'karyawan pakai dompet dianggap biaya dari laci': js.replace("if ((untuk === 'toko' || ky) && dari !== 'dompet') return { sel: 'beban',", "if (untuk === 'toko' || ky) return { sel: 'beban',"),
            'pemilahan membuang catatan yang belum dipilah': js.replace("if (u === 'toko') { P.toko += n; P.nToko += 1; } else { P.belum += n; P.nBelum += 1; }", "if (u === 'toko') { P.toko += n; P.nToko += 1; }"),
            'kartu memakai rumus laba sendiri (upah dihitung dua kali)': js.replace("const biayaToko = P.tokoSemua + posLain;", "const biayaToko = P.tokoSemua + posLain + upah;"),
            'nama kembar toko/karyawan diterima': js.replace("if (kembar.length) return { tolak: '\"' + kembar[0] + '\" ada di keperluan toko DAN karyawan — pilih salah satu tujuannya' };", ""),
            'keperluan karyawan terukur dari semua catatan toko (tidak dipilah)': js.replace("(kategori === 'karyawan' ? h.untuk === 'karyawan' : h.untuk !== 'karyawan')", "true"),
            'biaya admin pindah uang tanpa tujuan': js.replace("const adm = { id: w.idUnik(), kategori: 'toko', untuk: 'toko', tanggal: w.tanggal,", "const adm = { id: w.idUnik(), kategori: 'toko', tanggal: w.tanggal,"),
            'ambil pribadi kartu mengabaikan tarik modal': js.replace("const tarik = daftarModalOwner().filter((m) => m.tipe !== 'setor' && !m.pinjaman && dlm(m.tanggal))", "const tarik = daftarModalOwner().filter((m) => false)"),
            'bulan tanpa catatan digambar sebagai nol': js.replace("const tanpaCatatan = L.jumlahTrx === 0 && L.nHarian === 0 && L.nSusut === 0 && !gajiRows.length && !L.jatahBulanan;", "const tanpaCatatan = false;"),
            'bulan terkunci tidak ditandai final': js.replace("final: lpFinal(key), tanpaCatatan, L,", "final: false, tanpaCatatan, L,"),
            'susut dianggap di atas laba kotor (dimasukkan ke biaya toko)': js.replace("const biayaToko = P.tokoSemua + posLain; const nonUpah = P.karyawan;", "const biayaToko = P.tokoSemua + posLain - L.susutStok; const nonUpah = P.karyawan;"),
            'buku hari ini tidak menyebut belum dipilah': js.replace("cap: untuk || sel === 'prive' ? A.cap : A.cap + ' · belum dipilah',", "cap: A.cap,"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g, _ = utama(isi, False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    print('TIGA TUJUAN & LABA KOTOR → KE MANA (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    p = uji_wadah_bernama.cadangan_toko()
    if p and asap: print('ASAP DATA TOKO (%s): %s' % (os.path.basename(p), json.dumps(asap, ensure_ascii=False)[:1500]))
    if p:
        sama, ket = uji_wadah_bernama.asap_global(p)
        print('ASAP GLOBAL (kode main vs cabang, %s): %s' % (os.path.basename(p), ('BYTE-SAMA — ' + ket) if sama else ('GAGAL — ' + ket)))
        if sama is False: sys.exit(2)
    sys.exit(0 if not g else 2)
