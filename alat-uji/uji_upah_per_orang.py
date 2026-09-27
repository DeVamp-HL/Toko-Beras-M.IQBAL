#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_upah_per_orang.py — putaran 29 Bagian 2 (owner 27 Sep 2026): UPAH PER ORANG di dokumen bersama aturanToko/upah.
  · orang[].upah[] = {mulai, satuan hari|minggu|bulan, tarif}; tarif per hari suatu tanggal = entri terbaru yang mulai ≤ tanggal; tanpa entri → tarif bersama (bawaan lama).
  · Minggu ÷ 7, bulan ÷ jumlah hari bulan itu (28–31), DIBULATKAN ke rupiah dulu → slip bisa dihitung ulang pembaca; setengah hari = separuh dibulatkan.
  · Upah baru berlaku HANYA sesudah tanggalnya: gajian yang melintasi tanggal berlaku membayar dua tarif dan slipnya merinci keduanya (rincianTarif).
  · Riwayat tidak ditulis ulang: slip yang sudah dibayar tetap; gajian dua orang dengan upah berbeda; baris gaji per bulan = Σ rupiah per hari.
  · Atur: entri tanpa tanggal / tarif nol / satuan asing / dua entri bertanggal sama DITOLAK (bukan dibuang diam-diam). Tanpa dokumen per orang, tanpa mesin baru.
KOTAK PASIR (ANGKA CONTOH, nama rekaan), jam dikunci 19 Sep 2026 10:00 WIB.

    python3 alat-uji/uji_upah_per_orang.py            → N lulus · 0 gagal
    python3 alat-uji/uji_upah_per_orang.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = uji_uang_baru.MODUL
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def absen(nama, bulan, hari):
    return {'id': nama.lower() + '|' + bulan, 'nama': nama, 'bulan': bulan, 'hari': hari}


# ---- ANGKA CONTOH. Gaji Agustus dua orang dibayar 31 Agu (sistem lama) → hari yang belum dibayar mulai 1 Sep.
#      Pekerja A: 1–18 Sep penuh kecuali 7 Sep setengah; upah sendiri 60.000/hari sejak 1 Sep, naik 70.000/hari sejak 11 Sep.
#      Pekerja B: hitung upah sejak 10 Sep, 10–18 Sep penuh; upah sendiri 2.500.000/BULAN sejak 10 Sep (÷ 30 hari Sep = 83.333/hari). Pekerja C: sejak 15 Sep, tanpa upah sendiri → bawaan bersama 60.000.
KOTAK = {
  'penjualan': [], 'pengeluaranHarian': [], 'kasbonMutasi': [], 'slipUpah': [], 'modalOwner': [], 'utangOwnerMutasi': [], 'amplopLaba': [], 'pindahUang': [], 'tutupHari': [], 'setoranKas': [], 'piutangMutasi': [], 'penyesuaianStok': [], 'pengaturan': [],
  'biayaBulanan': [{'id': '2026-08', 'bulan': '2026-08', 'listrik': 0, 'internet': 0, 'akses': 0, 'keamanan': 0, 'tanggalBayarPos': {'gaji': '2026-08-31'},
                    'rincianGaji': [{'nama': 'Pekerja A', 'hari': 26, 'gaji': 1560000}, {'nama': 'Pekerja B', 'hari': 10, 'gaji': 600000}, {'nama': 'Pekerja C', 'hari': 5, 'gaji': 300000}], 'tanggalBayarGaji': {'Pekerja A': '2026-08-31', 'Pekerja B': '2026-08-31', 'Pekerja C': '2026-08-31'}, 'gaji': 2460000, 'gajiHariOrang': 41}],
  'absenKaryawan': [absen('Pekerja A', '2026-09', {('2026-09-%02d' % d): (0.5 if d == 7 else 1) for d in range(1, 19)}),
                    absen('Pekerja B', '2026-09', {('2026-09-%02d' % d): 1 for d in range(10, 19)}),
                    absen('Pekerja C', '2026-09', {('2026-09-%02d' % d): 1 for d in range(15, 19)})],
  'aturanToko': [{'id': 'upah', 'tarif': 60000, 'alasan': ['Lain-lain'], 'orang': [
      {'nama': 'Pekerja A', 'peran': 'Tetap', 'status': 'aktif', 'masuk': '', 'upah': [{'mulai': '2026-09-11', 'satuan': 'hari', 'tarif': 70000}, {'mulai': '2026-09-01', 'satuan': 'hari', 'tarif': 60000}]},
      {'nama': 'Pekerja B', 'peran': 'Giliran', 'status': 'aktif', 'masuk': '', 'mulaiHitung': '2026-09-10', 'upah': [{'mulai': '2026-09-10', 'satuan': 'bulan', 'tarif': 2500000}]},
      {'nama': 'Pekerja C', 'peran': 'Giliran', 'status': 'aktif', 'masuk': '', 'mulaiHitung': '2026-09-15', 'upah': []}]}],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 5000000, brankas: 10000000, rekening: 3000000, amplop: 0 }));
var KINI = new Date(Date.now()); var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 9000; return function () { n += 1; return n; }; })() };
var tulis = function (r) { if (r.tolak) throw new Error('DITOLAK: ' + r.tolak); if (r.hapus) terapkanKeCache(r.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); if (r.dokumen) terapkanKeCache(r.dokumen); return r; };
var ORANG = function () { return JSON.parse(J(aturUpah().orang)); };

// ---- tarif per hari menurut tanggal & sumbernya
var T = tarifHariPada('Pekerja A', '2026-09-10'), T2 = tarifHariPada('Pekerja A', '2026-09-11'), TB = tarifHariPada('Pekerja B', '2026-09-10'), TC = tarifHariPada('Pekerja C', '2026-09-10');
ok('A 10 Sep = 60.000 (entri 1 Sep), 11 Sep = 70.000 (entri 11 Sep) — entri diurutkan dari dokumen yang ditulis terbalik; sumber orang', T.tarifHari === 60000 && T.mulai === '2026-09-01' && T2.tarifHari === 70000 && T2.mulai === '2026-09-11' && T.sumber === 'orang', J([T, T2]));
ok('B bulanan 2.500.000 ÷ 30 hari Sep = 83.333 sehari (dibulatkan ke rupiah dulu), teksnya menyebut pembaginya; sebelum 10 Sep B ikut bawaan bersama', TB.tarifHari === 83333 && TB.satuan === 'bulan' && TB.pembagi === 30 && TB.teks === 'Rp2.500.000 sebulan ÷ 30 hari = Rp83.333 sehari' && tarifHariPada('Pekerja B', '2026-09-09').sumber === 'bersama', J(TB));
ok('C tanpa upah sendiri → tarif bersama 60.000 (sumber bersama, teks menyebut bawaan); Februari 2027 (28 hari) → 2.500.000 ÷ 28 = 89.286; minggu ÷ 7', TC.tarifHari === 60000 && TC.sumber === 'bersama' && /bawaan bersama/.test(TC.teks) && tarifHariPada('Pekerja B', '2027-02-10').tarifHari === 89286 && tarifHariPada('Pekerja B', '2027-02-10').pembagi === 28 && upPembagi('minggu', '2026-09-10') === 7);

// ---- hitungan per orang: tarif dibaca PER HARI, ruas tarif dirinci
var HA = hitungUpah('Pekerja A', KINI, 'semua');
ok('A 1–18 Sep: 1–10 @60.000 (9 penuh + setengah 7 Sep = 570.000) + 11–18 @70.000 (8 penuh = 560.000) = 1.130.000; dua ruas tarif; tarif hari ini 70.000; hari ini kosong', HA.upah === 1130000 && HA.rincianTarif.length === 2 && HA.tarifBeragam && HA.rincianTarif[0].upah === 570000 && HA.rincianTarif[0].penuh === 9 && HA.rincianTarif[0].setengah === 1 && HA.rincianTarif[0].sampai === '2026-09-10' && HA.rincianTarif[1].mulai === '2026-09-11' && HA.rincianTarif[1].upah === 560000 && HA.tarif === 70000 && HA.kosong === 1, J(HA.rincianTarif));
var HB = hitungUpah('Pekerja B', KINI, 'semua'); var HC = hitungUpah('Pekerja C', KINI, 'semua');
ok('B 10–18 Sep = 9 penuh × 83.333 = 749.997 (satuan bulan); C 15–18 = 4 × 60.000 bawaan = 240.000 — dua orang, tiga upah berbeda dalam satu daftar', HB.upah === 749997 && HB.satuan === 'bulan' && HB.tarifAsli === 2500000 && HC.upah === 240000 && HC.sumberTarif === 'bersama' && semuaUpah(KINI).map(function (o) { return o.nama + ':' + o.upah; }).join() === 'Pekerja A:1130000,Pekerja B:749997,Pekerja C:240000', J([HB.upah, HC.upah]));
ok('hariList membawa tarifHari & rupiah tiap hari (7 Sep setengah = 30.000); Σ rp = upah', HA.hariList.find(function (d) { return d.iso === '2026-09-07'; }).rp === 30000 && HA.hariList.find(function (d) { return d.iso === '2026-09-12'; }).tarifHari === 70000 && HA.hariList.reduce(function (a, d) { return a + d.rp; }, 0) === HA.upah);
var BU = bukuUpah('Pekerja A', KINI);
ok('buku upah A terbelah di pergantian tarif: "6 hari penuh × Rp60.000" (1–6), "1 setengah hari × Rp30.000", "3 hari penuh × Rp60.000" (8–10), "8 hari penuh × Rp70.000" (11–18); saldo berjalan 1.130.000', BU.rows.some(function (r) { return r.ket === '6 hari penuh × Rp60.000'; }) && BU.rows.some(function (r) { return r.ket === '1 setengah hari × Rp30.000'; }) && BU.rows.some(function (r) { return r.ket === '8 hari penuh × Rp70.000' && r.tgl === '11 Sep 2026 – 18 Sep 2026'; }) && BU.jalan === 1130000, J(BU.rows));
var KR = daftarKaryawan(KINI);
ok('daftar karyawan menyebut upah yang berlaku sekarang per orang (A 70.000 sehari · B bulanan · C bawaan)', KR.baris.find(function (b) { return b.nama === 'Pekerja A'; }).upahKini.tarifHari === 70000 && KR.baris.find(function (b) { return b.nama === 'Pekerja B'; }).upahKini.satuan === 'bulan' && KR.baris.find(function (b) { return b.nama === 'Pekerja C'; }).upahKini.sumber === 'bersama');

// ---- upah baru berlaku HANYA sesudah tanggalnya
var O = ORANG(); O[1].upah.push({ mulai: '2026-09-15', satuan: 'hari', tarif: 90000 }); tulis(susunAturUpah({ orang: O }, W));
HB = hitungUpah('Pekerja B', KINI, 'semua');
ok('B naik 90.000/hari mulai 15 Sep: 10–14 (5 × 83.333 = 416.665) + 15–18 (4 × 90.000 = 360.000) = 776.665; ruas pertama tetap bulanan', HB.upah === 776665 && HB.rincianTarif.length === 2 && HB.rincianTarif[0].satuan === 'bulan' && HB.rincianTarif[0].sampai === '2026-09-14' && HB.rincianTarif[1].mulai === '2026-09-15' && HB.rincianTarif[1].tarifHari === 90000, J(HB.rincianTarif));
O = ORANG(); O[1].upah.push({ mulai: '2026-09-25', satuan: 'hari', tarif: 200000 }); tulis(susunAturUpah({ orang: O }, W));
ok('entri bertanggal masa depan (25 Sep) tidak mengubah hitungan hari ini; tarifHariPada 25 Sep sudah 200.000', hitungUpah('Pekerja B', KINI, 'semua').upah === 776665 && tarifHariPada('Pekerja B', '2026-09-25').tarifHari === 200000);
O = ORANG(); O[1].upah = O[1].upah.filter(function (u) { return u.tarif !== 200000; }); tulis(susunAturUpah({ orang: O }, W));

// ---- gajian: baris gaji = Σ rupiah per hari; slip merinci tiap ruas; dua orang dengan upah berbeda
var kas0 = kasPada(); var RA = tulis(susunBayarUpah('Pekerja A', 'semua', W));
var bA = RA.dokumen.find(function (d) { return d.koleksi === 'biayaBulanan'; }).data; var rA = bA.rincianGaji.find(function (x) { return x.orang === 'Pekerja A'; }); var sA = RA.slip;
ok('bayar A: baris gaji Sep hari 17,5 gaji 1.130.000 (Σ per hari, BUKAN 17,5 × tarif hari ini); kas turun 1.130.000; slipUpah membawa satuan & rincianTarif 2 ruas (yang terpotong di 18 Sep), tarif 70.000', rA.hari === 17.5 && rA.gaji === 1130000 && kasPada() === kas0 - 1130000 && sA.satuan === 'hari' && sA.rincianTarif.length === 2 && sA.rincianTarif[1].sampai === '2026-09-18' && sA.rincianTarif[0].upah + sA.rincianTarif[1].upah === 1130000 && sA.tarif === 70000 && sA.upah === 1130000, J([rA, sA.rincianTarif]));
ok('slip A merinci dua tarif dan tiap hitungannya bisa diulang pembaca: "1 Sep 2026 – 10 Sep 2026 · Rp60.000 sehari", "9 hari penuh × Rp60.000 = Rp540.000", "1 setengah hari × Rp30.000 = Rp30.000", "11 Sep 2026 – 18 Sep 2026 · Rp70.000 sehari", "8 hari penuh × Rp70.000 = Rp560.000", Upah Rp1.130.000', /1 Sep 2026 – 10 Sep 2026 · Rp60\.000 sehari/.test(sA.teks) && /9 hari penuh × Rp60\.000 = Rp540\.000/.test(sA.teks) && /1 setengah hari × Rp30\.000 = Rp30\.000/.test(sA.teks) && /11 Sep 2026 – 18 Sep 2026 · Rp70\.000 sehari/.test(sA.teks) && /8 hari penuh × Rp70\.000 = Rp560\.000/.test(sA.teks) && /Upah\s+Rp1\.130\.000/.test(sA.teks) && /dua tarif/.test(RA.patch.kabar), sA.teks);
var RB = tulis(susunBayarUpah('Pekerja B', 'semua', W)); var sB = RB.slip; var rB = RB.dokumen.find(function (d) { return d.koleksi === 'biayaBulanan'; }).data.rincianGaji.find(function (x) { return x.orang === 'Pekerja B'; });
ok('bayar B (bulanan lalu harian): baris gaji 776.665 hari 9; slip menyebut "Rp2.500.000 sebulan ÷ 30 hari = Rp83.333 sehari" & "5 hari penuh × Rp83.333 = Rp416.665" & "4 hari penuh × Rp90.000 = Rp360.000"; baris A tetap di dokumen yang sama', rB.gaji === 776665 && rB.hari === 9 && /Rp2\.500\.000 sebulan ÷ 30 hari = Rp83\.333 sehari/.test(sB.teks) && /5 hari penuh × Rp83\.333 = Rp416\.665/.test(sB.teks) && /4 hari penuh × Rp90\.000 = Rp360\.000/.test(sB.teks) && RB.dokumen.find(function (d) { return d.koleksi === 'biayaBulanan'; }).data.rincianGaji.some(function (x) { return x.orang === 'Pekerja A' && x.gaji === 1130000; }), sB.teks);
ok('laba Sep memuat kedua gaji KOTOR (1.130.000 + 776.665 dibagi rata per hari; Σ jatah sebulan = 1.906.665); kas turun kedua-duanya', Math.abs(hitungLabaBersihRentang('2026-09-01', '2026-09-30').jatahBulanan - 1906665) < 0.5 && kasPada() === kas0 - 1130000 - 776665);
// satu ruas & satuan hari → slip berbentuk lama (tanpa baris rentang), kompatibel dengan pembaca DK4
var RC = tulis(susunBayarUpah('Pekerja C', 'semua', W));
ok('slip C (satu tarif harian bawaan): baris "4 hari penuh × Rp60.000 = Rp240.000" tanpa baris rentang tarif; rincianTarif 1 ruas', /^4 hari penuh × Rp60\.000 = Rp240\.000$/m.test(RC.slip.teks) && !/–.*sehari/.test(RC.slip.teks) && RC.slip.rincianTarif.length === 1, RC.slip.teks);

// ---- riwayat tidak ditulis ulang
O = ORANG(); O[0].upah = [{ mulai: '2026-09-01', satuan: 'hari', tarif: 80000 }]; tulis(susunAturUpah({ orang: O }, W));
ok('mengubah upah A jadi 80.000 sejak 1 Sep SESUDAH gajian: slip A tetap 1.130.000, baris gaji tetap; A kini mulai 19 Sep (sejak slip), upah 0; 19 Sep akan dihitung 80.000', ambilSlipUpah().find(function (s) { return s.nama === 'Pekerja A'; }).upah === 1130000 && ambilBiayaBulanan().find(function (b) { return b.bulan === '2026-09'; }).rincianGaji.find(function (x) { return x.orang === 'Pekerja A'; }).gaji === 1130000 && hitungUpah('Pekerja A', KINI, 'semua').mulai === '2026-09-19' && hitungUpah('Pekerja A', KINI, 'semua').upah === 0 && tarifHariPada('Pekerja A', '2026-09-19').tarifHari === 80000);
tulis(susunAturUpah({ tarif: '65.000' }, W));
ok('mengubah tarif BERSAMA hanya menyentuh orang tanpa upah sendiri: C 65.000, A tetap 80.000, B tetap 90.000', tarifHariPada('Pekerja C', '2026-09-19').tarifHari === 65000 && tarifHariPada('Pekerja A', '2026-09-19').tarifHari === 80000 && tarifHariPada('Pekerja B', '2026-09-19').tarifHari === 90000 && aturUpah().tarif === 65000);

// ---- atur: entri cacat ditolak, bukan dibuang
var dasar = function () { return ORANG(); };
var o1 = dasar(); o1[2].upah = [{ mulai: '', satuan: 'hari', tarif: '50.000' }];
var o2 = dasar(); o2[2].upah = [{ mulai: '2026-09-01', satuan: 'hari', tarif: '0' }];
var o3 = dasar(); o3[2].upah = [{ mulai: '2026-09-01', satuan: 'tahun', tarif: '50.000' }];
var o4 = dasar(); o4[2].upah = [{ mulai: '2026-09-01', satuan: 'hari', tarif: '50.000' }, { mulai: '2026-09-01', satuan: 'bulan', tarif: '1.000.000' }];
var o5 = dasar(); o5[2].upah = [{ mulai: '2026-09-01', satuan: 'bulan', tarif: '200.000.000' }];
ok('ditolak: tanpa tanggal mulai · tarif 0 · satuan asing · dua entri bertanggal sama · tarif > 100 jt', /belum punya tanggal mulai/.test(susunAturUpah({ orang: o1 }, W).tolak) && /1–100\.000\.000/.test(susunAturUpah({ orang: o2 }, W).tolak) && /satuan upah tidak dikenal/.test(susunAturUpah({ orang: o3 }, W).tolak) && /dua upah mulai berlaku tanggal yang sama/.test(susunAturUpah({ orang: o4 }, W).tolak) && /1–100\.000\.000/.test(susunAturUpah({ orang: o5 }, W).tolak), J([susunAturUpah({ orang: o1 }, W).tolak, susunAturUpah({ orang: o4 }, W).tolak]));
var o6 = dasar(); o6[2].upah = [{ mulai: '', satuan: 'hari', tarif: '' }, { mulai: '2026-09-01', satuan: 'minggu', tarif: '420.000' }]; var R6 = tulis(susunAturUpah({ orang: o6 }, W));
ok('baris kosong (mulai & tarif kosong, dari tombol "＋ upah baru" yang belum diisi) diabaikan; mingguan 420.000 → 60.000/hari; dokumen tetap aturanToko/upah satu dokumen bersama (tanpa dokumen per orang); kabar menyebut orang berupah sendiri', R6.dokumen.length === 1 && R6.dokumen[0].koleksi === 'aturanToko' && R6.dokumen[0].data.id === 'upah' && R6.dokumen[0].data.orang[2].upah.length === 1 && tarifHariPada('Pekerja C', '2026-09-19').tarifHari === 60000 && tarifHariPada('Pekerja C', '2026-09-19').satuan === 'minggu' && /3 orang punya upah sendiri/.test(R6.patch.kabar), J([R6.dokumen[0].data.orang[2], R6.patch.kabar]));
ok('bentuk lama tetap terbaca: dokumen upah TANPA kolom upah[] per orang → semua ikut tarif bersama', (function () { pasok('aturanToko', [{ id: 'upah', tarif: 55000, orang: [{ nama: 'Pekerja A', status: 'aktif' }] }]); var t = tarifHariPada('Pekerja A', '2026-09-19'); return t.tarifHari === 55000 && t.sumber === 'bersama' && aturUpah().orang[0].upah.length === 0; })());
print(J({ lulus: lulus, gagal: gagal }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def utama(js):
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            'upah per orang diabaikan (selalu tarif bersama)': js.replace("(O ? O.upah : []).forEach((x) => { if (x.mulai <= iso) u = x; });", ""),
            'tanggal berlaku diabaikan (entri terbaru dipakai untuk semua hari)': js.replace("(O ? O.upah : []).forEach((x) => { if (x.mulai <= iso) u = x; });", "(O ? O.upah : []).forEach((x) => { u = x; });"),
            'bulanan tidak dibagi per hari': js.replace("const pembagi = upPembagi(u.satuan, iso); const tarifHari = Math.round(u.tarif / pembagi);", "const pembagi = 1; const tarifHari = u.tarif;"),
            'pembagi bulan angka mati 30 (Februari salah)': js.replace("satuan === 'bulan' ? Number(akhirBulanIso(String(iso).slice(0, 7)).slice(8, 10)) : 1", "satuan === 'bulan' ? 30 : 1"),
            'tarif harian tidak dibulatkan dulu (slip tidak bisa diulang pembaca)': js.replace("const tarifHari = Math.round(u.tarif / pembagi);", "const tarifHari = u.tarif / pembagi;"),
            'baris gaji per bulan = hari × tarif hari ini (bukan Σ rupiah per hari)': js.replace("perBulan[b].upah += d.rp;", "perBulan[b].upah += d.nilai * H.tarif;"),
            'slip tidak merinci ruas tarif': js.replace("ruas.forEach((r) => { if (ruas.length > 1 || r.satuan !== 'hari') L.push(", "[].forEach((r) => { if (ruas.length > 1 || r.satuan !== 'hari') L.push("),
            'entri upah tanpa tanggal dibuang diam-diam': js.replace("if (!mulai) return { tolak: nm + ': upah ' + (n > 0 ? RP(n) : '') + ' belum punya tanggal mulai berlaku' };", ""),
            'dua entri bertanggal sama diterima': js.replace("if (mulaiSemua.indexOf(mulai) >= 0) return { tolak: nm + ': dua upah mulai berlaku tanggal yang sama (' + tanggalPendek(mulai) + ')' };", ""),
            'setengah hari dibayar penuh': js.replace("const upNilaiHari = (x, th) => (x === 1 ? th : x === 0.5 ? Math.round(th / 2) : 0);", "const upNilaiHari = (x, th) => (x === 1 ? th : x === 0.5 ? th : 0);"),
            'buku upah tidak terbelah di pergantian tarif': js.replace("if (a !== null && (x !== nilai || d.tarifHari !== th)) tutup(ugTambahHari(d.iso, -1));", "if (a !== null && x !== nilai) tutup(ugTambahHari(d.iso, -1));"),
            'slipUpah kehilangan rincian tarif': js.replace("tarif: H.tarif, satuan: H.satuan, rincianTarif, upah: H.upah,", "tarif: H.tarif, satuan: H.satuan, rincianTarif: [], upah: H.upah,"),
            'daftar upah tidak diurutkan (entri terbalik di dokumen menang)': js.replace(".filter((u) => u.mulai && u.tarif > 0).sort((a, b) => a.mulai.localeCompare(b.mulai));", ".filter((u) => u.mulai && u.tarif > 0);"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    print('UPAH PER ORANG (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    sys.exit(0 if not g else 2)
