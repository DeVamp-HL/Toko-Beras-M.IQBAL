#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_ringkasan_baru.py — uji logika layar RINGKASAN sistem baru (baru/js/layar/ringkasan-logika.js) di jsc.
KOTAK PASIR (ANGKA CONTOH, bukan angka toko) dengan jam tetap; kalau ada backup-batch-*.json lokal ditambah uji asap:
angka Ringkasan harus SAMA dengan jumlah langsung dari baris penjualan cadangan itu.

    python3 alat-uji/uji_ringkasan_baru.py            → N lulus · 0 gagal
    python3 alat-uji/uji_ringkasan_baru.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/ringkasan-logika.js']


def jual(id, tgl, jam, rp, trx=None, cara='Tunai', hpp=None, jenis='kemasan'):
    d = {'id': id, 'tanggal': tgl, 'jam': jam, 'caraBayar': cara, 'namaPelanggan': '', 'jenis': jenis, 'namaProduk': 'Kembang', 'ukuranKemasan': 5,
         'jumlahUnit': 1, 'totalKg': 5, 'hargaTotal': rp, 'hppTotalSaatJual': int(rp * 0.9) if hpp is None else hpp}
    if trx: d['trxId'] = trx
    return d


# Sabtu 19 Sep 2026 14:07 = "sekarang". Catatan toko contoh mulai 25 Agu 2026.
KOTAK = {
  'produksiKemasan': [{'id': 'p1', 'tanggal': '2026-08-25', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 500, 'hppPerUnit': 66000}],
  'penjualan': [
    jual('a1', '2026-09-19', '08:10', 100000), jual('a2', '2026-09-19', '08:40', 50000, trx='T2'), jual('a3', '2026-09-19', '08:40', 25000, trx='T2'),
    jual('a4', '2026-09-19', '13:20', 200000, cara='QRIS'), jual('a5', '2026-09-19', '13:55', 40000), jual('a6', '2026-09-19', '14:05', 60000),
    jual('a7', '2026-09-19', '15:30', 999000),                       # SESUDAH "sekarang" (jam perangkat lain maju) — tetap omzet hari ini, tapi bukan 60 menit terakhir
    jual('x1', '2026-09-19', '09:00', 777000) | {'dibatalkan': True},  # baris mati: tidak boleh ikut
    jual('k1', '2026-09-18', '09:00', 300000), jual('k2', '2026-09-18', '13:30', 80000), jual('k3', '2026-09-18', '16:00', 500000),
    jual('s1', '2026-09-14', '10:00', 1000000),                       # Senin minggu ini
    jual('l1', '2026-09-12', '10:00', 700000), jual('l2', '2026-09-07', '10:00', 400000), jual('l3', '2026-09-13', '18:00', 150000),   # minggu lalu: Sen 7 & Sab 12 (& Min 13 sesudah titik)
    jual('b1', '2026-09-01', '10:00', 250000),
    jual('g1', '2026-08-25', '10:00', 600000), jual('g2', '2026-08-30', '10:00', 350000),
  ],
  'piutangMutasi': [{'id': 'm1', 'tanggal': '2026-08-10', 'namaPelanggan': 'Deka', 'tipe': 'saldoAwal', 'nominal': 200000}],
  'pesanan': [{'id': 'ps1', 'tanggal': '2026-09-19', 'namaPelanggan': 'Bu Ani', 'isi': 'x', 'status': 'diantar'}, {'id': 'ps2', 'tanggal': '2026-09-18', 'namaPelanggan': 'B', 'isi': 'y', 'status': 'dibayar'}],
}

SKENARIO = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var KINI = new Date('2026-09-19T14:07:30'); var ix = bangunIndeks();
ok('indeks: catatan mulai 25 Agu; baris dibatalkan tidak ikut; hari ini 7 baris / 6 nota (T2 dua baris = satu nota)', ix.mulai === '2026-08-25' && ix.perHari['2026-09-19'].baris.length === 7 && ix.perHari['2026-09-19'].nota.size === 6, JSON.stringify([ix.mulai, ix.perHari['2026-09-19'].baris.length]));
var R = susunRingkasan('jam', ix, KINI);
ok('jam: angka = omzet HARI INI 1.474.000 (termasuk nota berjam 15:30), 6 nota, judul "Hari ini · per jam"', R.angka === 1474000 && R.judul === 'Hari ini · per jam' && /6 nota/.test(R.sub), JSON.stringify([R.angka, R.sub]));
ok('jam: margin kotor dari mesin laba (10% dari harga contoh) disebut dengan persennya', /margin kotor Rp147\.400 · 10%/.test(R.sub), R.sub);
ok('jam: pembanding menyebut jam berjalan 14 (60.000 · 1 nota) dan jam tersibuk 15', /Jam 14 berjalan Rp60\.000 · 1 nota/.test(R.banding) && /tersibuk 15 · Rp999\.000/.test(R.banding), R.banding);
ok('jam: tiga lapis = jam (luar) · hari (induk) · bulan (kakek)', R.lapisan.length === 3 && /^Luar · Jam 14/.test(R.lapisan[0].nama) && /^Induk · Hari ini/.test(R.lapisan[1].nama) && /^Kakek · September/.test(R.lapisan[2].nama), JSON.stringify(R.lapisan.map(function (l) { return l.nama; })));
ok('jam: induk menyebut kemarin JAM SEGINI (s/d 14:07 = 380.000, bukan 880.000 sehari penuh)', /kemarin jam segini Rp380\.000/.test(R.lapisan[1].ket), R.lapisan[1].ket);
var sJam = R.sektor.filter(function (x) { return x.lapis === 'jam'; }), sHari = R.sektor.filter(function (x) { return x.lapis === 'hari'; }), sBulan = R.sektor.filter(function (x) { return x.lapis === 'bulan'; });
ok('cincin: 17 sel jam (05–21) r=86, 30 sel hari r=66, 12 sel bulan r=49', sJam.length === 17 && sJam[0].r === 86 && sHari.length === 30 && sHari[0].r === 66 && sBulan.length === 12 && sBulan[0].r === 49, [sJam.length, sHari.length, sBulan.length].join());
ok('cincin jam: sel 14 BERJALAN (tepi putus), jam 15–21 rel (belum terjadi) walau ada nota berjam 15:30, jam 08 emas', sJam[9].kelas === 'berjalan' && sJam.slice(10).every(function (x) { return x.kelas === 'rel'; }) && sJam[3].kelas === 'emas', JSON.stringify(sJam.map(function (x) { return x.kelas; })));
ok('cincin hari: hari sebelum 25 Agu ABSEN (bukan nol), hari ini berjalan, hari tanpa jualan = rel tipis', sHari[0].kelas === 'absen' && sHari[29].kelas === 'berjalan' && sHari.filter(function (x) { return x.kelas === 'absen'; }).length === 4 && sHari[28].kelas === 'emas', JSON.stringify(sHari.map(function (x) { return x.kelas; })));
ok('cincin bulan: Jan–Jul absen, Agu emas, Sep berjalan, Okt–Des rel', sBulan.slice(0, 7).every(function (x) { return x.kelas === 'absen'; }) && sBulan[7].kelas === 'emas' && sBulan[8].kelas === 'berjalan' && sBulan.slice(9).every(function (x) { return x.kelas === 'rel'; }), JSON.stringify(sBulan.map(function (x) { return x.kelas; })));
ok('cincin: tebal ∝ akar nilai dan tak pernah melebihi tebal maksimum lapisnya', sJam.every(function (x) { return x.w <= 13; }) && sHari.every(function (x) { return x.w <= 11; }) && sJam[10 - 0] && sJam.filter(function (x) { return x.kelas === 'emas'; })[0].w > 1.5);
ok('cincin: KETUJUH lapis selalu ada (147 sel + tahun); yang tak berperan menunggu di luar r=108 (lebih halus dari skala) atau di dalam r=22, opasitas 0', R.sektor.length === 15 + 60 + 17 + 30 + 12 + 12 + 1 && R.sektor.filter(function (x) { return x.lapis === 'menit'; }).every(function (x) { return x.r === 108 && x.op === 0; }) && R.sektor.filter(function (x) { return x.lapis === 'tahun'; }).every(function (x) { return x.r === 22 && x.op === 0; }) && sJam.every(function (x) { return x.op === 1; }), String(R.sektor.length));
ok('cincin: identitas sel tetap antar skala (lapis:urutan) — syarat cincin bisa BERGESER, bukan digambar ulang', JSON.stringify(R.sektor.map(function (x) { return x.id; })) === JSON.stringify(susunRingkasan('tahun', ix, KINI).sektor.map(function (x) { return x.id; })));
ok('cincin: sel membawa label & nilai untuk diketuk — hari ke-29 (kemarin) "Jumat, 18 Sep" Rp880.000; sel bulan Agustus 950.000; hari sebelum catatan nilai null', sHari[28].label === 'Jumat, 18 Sep' && sHari[28].nilai === 880000 && sBulan[7].label === 'Agustus 2026' && sBulan[7].nilai === 950000 && sHari[0].nilai === null && sHari[0].keadaan === 'absen', JSON.stringify([sHari[28].label, sHari[28].nilai, sBulan[7].label, sBulan[7].nilai]));
var kt = selDariKetukan(R.sektor, 86, 0); ok('ketukan: jam 12 di cincin luar = sel BERJALAN (jam 14)', kt && kt.lapis === 'jam' && kt.i === 9, JSON.stringify(kt && [kt.lapis, kt.i]));
kt = selDariKetukan(R.sektor, 64, -12); ok('ketukan: cincin induk, satu sel ke kiri dari jam 12 = KEMARIN (Jumat, 18 Sep)', kt && kt.lapis === 'hari' && kt.label === 'Jumat, 18 Sep', JSON.stringify(kt && [kt.lapis, kt.label]));
ok('ketukan: di luar semua cincin (jarak 130) atau di pusat (jarak 10) → tidak memilih apa-apa; lapis tersembunyi tak bisa diketuk', selDariKetukan(R.sektor, 130, 0) === null && selDariKetukan(R.sektor, 10, 0) === null && selDariKetukan(R.sektor, 108, 0) === null);
ok('lapisan menyebut lapisnya → ketuk "Induk · Hari ini" pindah ke skala hari', R.lapisan[1].lapis === 'hari' && SKALA_DARI_LAPIS[R.lapisan[1].lapis] === 'hari' && SKALA_DARI_LAPIS.m15 === 'langsung');
R = susunRingkasan('menit', ix, KINI);
ok('menit: 60 menit terakhir (13:08–14:07) = 200.000 + 40.000 + 60.000 = 300.000, 3 nota; nota 15:30 TIDAK ikut', R.angka === 300000 && /3 nota/.test(R.sub) && /Rp100\.000\/nota/.test(R.sub), JSON.stringify([R.angka, R.sub]));
ok('menit: pembanding = kemarin jendela yang sama (13:30 → 80.000, 1 nota, +275%)', /kemarin jendela ini 1 nota · Rp80\.000 \(\+275%\)/.test(R.banding), R.banding);
R = susunRingkasan('langsung', ix, KINI);
ok('langsung: nota ke-6 hari ini · kemarin jam segini nota ke-2; lapis luar = 15 menit terakhir (13:55 + 14:05 → 100.000, 2 nota)', /Nota ke-6 hari ini · kemarin jam segini nota ke-2/.test(R.banding) && /15 menit terakhir/.test(R.lapisan[0].nama) && R.lapisan[0].nilai === 'Rp100.000' && R.lapisan[0].ket === '2 nota', R.banding + ' | ' + JSON.stringify(R.lapisan[0]));
ok('langsung: umpan = nota hari ini terbaru dulu, nota dua baris digabung (+1), QRIS disebut', R.umpan.length === 6 && R.umpan[0].jam === '15:30' && R.umpan.some(function (u) { return /\+1/.test(u.isi) && u.rp === 75000; }) && R.umpan.some(function (u) { return /QRIS/.test(u.isi); }), JSON.stringify(R.umpan));
ok('langsung: sejak nota terakhir = 2 menit (14:05), nota berjam 15:30 tidak membuatnya negatif', R.sejakNotaMenit === 2, String(R.sejakNotaMenit));
R = susunRingkasan('hari', ix, KINI);
ok('hari: angka = MINGGU INI berjalan (Sen 14 → Sab 19) = 1.000.000 + 880.000 + 1.474.000 = 3.354.000', R.angka === 3354000 && R.judul === 'Minggu ini · per hari · berjalan', String(R.angka));
ok('hari: pembanding minggu lalu SAMPAI Sabtu jam segini = 400.000 + 700.000 = 1.100.000 (Minggu 13 tidak ikut), +204,9%', /minggu lalu sampai Sabtu jam segini: Rp1\.100\.000 \(\+204,9%\)/.test(R.banding), R.banding);
R = susunRingkasan('bulan', ix, KINI);
ok('bulan: September berjalan = 5.854.000; Agustus hanya sejak tanggal 25 → MENOLAK membandingkan', R.angka === 3354000 + 1250000 + 250000 + 1000000 * 0 && /Agustus 2026 hanya sejak tanggal 25 · belum bisa dibandingkan/.test(R.banding), R.angka + ' | ' + R.banding);
ok('bulan: dua lapis saja (bulan · tahun), hari buka dihitung dari hari yang ada jualannya', R.lapisan.length === 2 && /7 hari buka/.test(R.sub), R.sub);
R = susunRingkasan('tahun', ix, KINI);
ok('tahun: 2026 · sejak 25 Agustus; 9 hari buka; pembanding tahun lalu DITOLAK dengan sebabnya', /2026 · sejak 25 Agustus/.test(R.judul) && /9 hari buka/.test(R.sub) && /belum ada/.test(R.banding) && R.lapisan.length === 1 && R.sektor.filter(function (x) { return x.op === 1; }).length === 1, R.judul + ' | ' + R.sub + ' | ' + R.banding);
ok('tahun: angka = semua baris berlaku 2026 = 5.804.000', R.angka === 5804000, String(R.angka));
var P = susunPerhatian();
ok('perhatian: bon belum lunas 1 nama Rp200.000 (tertua ≥ 30 hari → awas); pesanan belum dibayar 1 (1 sudah diantar)', P.some(function (x) { return /Bon belum lunas · 1 nama/.test(x.teks) && x.nilai === 'Rp200.000' && x.awas; }) && P.some(function (x) { return /Pesanan belum dibayar · 1 sudah diantar/.test(x.teks) && x.nilai === '1 pesanan'; }), JSON.stringify(P));
var K = susunKas(KINI);
ok('kas: tanpa titik kas di perangkat → MENOLAK menyebut saldo; arus hari ini tetap dari buku kas: laci 1.274.000 · rekening 200.000', K.adaTitik === false && K.total === null && K.masukLaci === 1274000 && K.masukRek === 200000 && K.keluar === 0, JSON.stringify(K));
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-18', laci: 1000000, rekening: 500000, amplop: 0, brankas: 0 }));
K = susunKas(KINI); ok('kas: dengan titik kas 18 Sep (1.500.000) → saldo = titik + gerakan SESUDAH titik = 1.500.000 + 1.474.000', K.adaTitik === true && K.total === 2974000, JSON.stringify(K));
ok('kelompok angka untuk animasi: "Rp 5.804.000" → [Rp, 5, .804, .000]', JSON.stringify(kelompokAngka(5804000)) === JSON.stringify(['Rp', '5', '.804', '.000']), JSON.stringify(kelompokAngka(5804000)));
ok('salam & tanggal: 14:07 → Selamat siang · Sabtu, 19 September 2026', salam(KINI) === 'Selamat siang' && tanggalPanjang(KINI) === 'Sabtu, 19 September 2026', salam(KINI) + ' ' + tanggalPanjang(KINI));
// toko kosong: tidak melempar, semuanya nol/ditolak
pasok('penjualan', []); var ix0 = bangunIndeks(); var R0 = susunRingkasan('hari', ix0, KINI);
ok('toko tanpa penjualan: angka 0, semua sel hari ABSEN, pembanding ditolak — tidak melempar', R0.angka === 0 && R0.sektor.filter(function (x) { return x.lapis === 'hari'; }).every(function (x) { return x.kelas === 'absen'; }) && /belum bisa dibandingkan/.test(R0.banding), JSON.stringify([R0.angka, R0.banding]));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var hidup = (CAD.penjualan || []).filter(function (p) { return !p.dikoreksiOleh && !p.dibatalkan; });
var tgl = hidup.map(function (p) { return p.tanggal || ''; }).sort(); var akhir = tgl[tgl.length - 1];
var KINI = new Date(akhir + 'T23:59:00'); var ix = bangunIndeks();
var R = susunRingkasan('jam', ix, KINI); var B = susunRingkasan('bulan', ix, KINI); var T = susunRingkasan('tahun', ix, KINI);
var langsungHari = hidup.filter(function (p) { return p.tanggal === akhir; }).reduce(function (a, p) { return a + (p.hargaTotal || 0); }, 0);
var langsungBulan = hidup.filter(function (p) { return (p.tanggal || '').slice(0, 7) === akhir.slice(0, 7) && p.tanggal <= akhir; }).reduce(function (a, p) { return a + (p.hargaTotal || 0); }, 0);
var langsungTahun = hidup.filter(function (p) { return (p.tanggal || '').slice(0, 4) === akhir.slice(0, 4); }).reduce(function (a, p) { return a + (p.hargaTotal || 0); }, 0);
var semuaSkala = SKALA.map(function (s) { var r = susunRingkasan(s[0], ix, KINI); return r.sektor.length > 0 && typeof r.angka === 'number' && !!r.judul; });
print(JSON.stringify({ akhir: akhir, hariCocok: R.angka === langsungHari, bulanCocok: B.angka === langsungBulan, tahunCocok: T.angka === langsungTahun, skala: semuaSkala.filter(Boolean).length, perhatian: susunPerhatian().length, mulai: ix.mulai }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
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
            'baris yang dibatalkan ikut dihitung': js.replace("ambilPenjualan().forEach((p) => {\n    const t = p.tanggal || ''; if (!t) return;", "ambilPenjualanSemua().forEach((p) => {\n    const t = p.tanggal || ''; if (!t) return;"),
            'nota dua baris dihitung dua nota': js.replace("const rkKunciNota = (p) => String(p.trxId || p.grupNota || p.id);", "const rkKunciNota = (p) => String(p.id);"),
            'pembanding kemarin memakai SEHARI PENUH (bukan jam segini)': js.replace("const kmrSegini = adaSejak(kemarin) ? rkJumlahRentang(ix, kemarin, kemarin, menitKini) : null;", "const kmrSegini = adaSejak(kemarin) ? rkJumlahRentang(ix, kemarin, kemarin) : null;"),
            'pembanding minggu lalu memakai seminggu penuh': js.replace("rkJumlahRentang(ix, rkIso(aMgLalu), rkIso(rkGeser(kini, -7)), menitKini)", "rkJumlahRentang(ix, rkIso(aMgLalu), rkIso(rkGeser(aMgLalu, 6)))"),
            'bulan lalu yang tidak lengkap tetap dibandingkan': js.replace("const blLalu = adaSejak(rkIso(blLaluAwal)) ?", "const blLalu = true ?"),
            'hari sebelum ada catatan digambar NOL (bukan absen)': js.replace("sel.push(t < ix.mulai || !ix.mulai ? { v: null, kelas: 'absen' } :", "sel.push(false ? { v: null, kelas: 'absen' } :"),
            'jam yang belum terjadi digambar sebagai nol-emas': js.replace(": j > jamKini ? { v: 'rel', kelas: 'rel' } :", ": false ? { v: 'rel', kelas: 'rel' } :"),
            'minggu dimulai hari Minggu (bukan Senin)': js.replace("x.setDate(x.getDate() - ((x.getDay() + 6) % 7));", "x.setDate(x.getDate() - x.getDay());"),
            '60 menit terakhir memuat nota berjam sesudah sekarang': js.replace("if (m !== null && menitKini - m >= 0 && menitKini - m < 60) { o += p.hargaTotal || 0; n.add(rkKunciNota(p)); } }); return { omzet: o, nota: n.size }; })();\n  const M15", "if (m !== null && menitKini - m < 60) { o += p.hargaTotal || 0; n.add(rkKunciNota(p)); } }); return { omzet: o, nota: n.size }; })();\n  const M15"),
            'saldo kas ditebak walau titik kas belum disetel': js.replace("return { adaTitik: !!titik && total !== null, total,", "return { adaTitik: true, total: total === null ? 0 : total,"),
            'margin tidak menyebut persennya': js.replace("' · ' + pct + '%'", "''"),
            'tebal cincin linear melebihi batas lapis': js.replace("w = Math.max(1.5, wmax * Math.sqrt(Math.min(1, v / d.vmax)));", "w = Math.max(1.5, wmax * 2 * (v / d.vmax));"),
            'sejak-nota-terakhir memakai nota berjam sesudah sekarang': js.replace("return m !== null && m <= menitKini && m > a ? m : a; }, -1);", "return m !== null && m > a ? m : a; }, -1);"),
            'lapis yang tak berperan ikut tampak (opasitas 1)': js.replace("wmax = idx >= 0 ? WMAX[idx] : 6, op = idx >= 0 ? 1 : 0;", "wmax = idx >= 0 ? WMAX[idx] : 6, op = 1;"),
            'ketukan memilih sel yang salah (tidak digeser ke sel berjalan)': js.replace("let i = Math.round(((sudutDerajat % 360) + 360) % 360 / langkah) + jalan;", "let i = Math.round(((sudutDerajat % 360) + 360) % 360 / langkah);"),
            'label sel hari meleset sehari': js.replace("if (nama === 'hari') { const d = rkGeser(kini, -(n - 1 - i));", "if (nama === 'hari') { const d = rkGeser(kini, -(n - i));"),
            'pesanan yang sudah dibayar ikut "belum dibayar"': js.replace("const ps = ambilPesanan().filter(pesananBelumTuntas);", "const ps = ambilPesanan();"),
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
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')), key=os.path.basename)   # cadangan toko boleh di akar, _privat/ atau _arsip-mockup/ (semua di-gitignore); yang terbaru menurut tanggal di namanya
    if cad:
        c = json.load(open(cad[-1], encoding='utf-8'))
        h, e = jalan(js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP)
        if h is None: print('ASAP DATA TOKO: JSC JATUH ' + e); g.append('asap')
        else:
            print('ASAP DATA TOKO (%s, hari terakhir %s, catatan mulai %s): omzet hari/bulan/tahun = jumlah langsung baris cadangan: %s/%s/%s · %d skala tergambar · %d hal perlu perhatian'
                  % (os.path.basename(cad[-1]), h['akhir'], h['mulai'], h['hariCocok'], h['bulanCocok'], h['tahunCocok'], h['skala'], h['perhatian']))
            if not (h['hariCocok'] and h['bulanCocok'] and h['tahunCocok'] and h['skala'] == 7): g.append('asap: angka Ringkasan tidak sama dengan jumlah langsung baris cadangan')
    sys.exit(2 if g else 0)
