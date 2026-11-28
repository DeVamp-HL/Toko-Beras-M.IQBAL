#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_serah_laci.py — SERAH TERIMA LACI SAAT GANTI JAGA + DAFTAR BELANJA TABLET PER HARGA (owner 28 Nov 2026), dijalankan ASLI di jsc di atas data contoh
uji_tutup_tablet.py (uji_uang_baru: hari 19 Sep, titik kas 15 Sep, setelan tutup hari owner), ditambah pemeriksaan pemasangannya.

Keputusan owner (ditanya di depan): orang yang DATANG menghitung sebelum mulai jaga · WAJIB (tablet tertahan di Menu sampai terkirim) · per pecahan seperti
Tutup hari · tablet hitung BUTA (seharusnya & selisih hanya di HP owner) · daftar belanja tablet per HARGA seperti daftar owner, harga per kg selalu tampil.

Yang dipegang:
  · pemicu: orang pertama hari itu tidak menghitung; orang yang sama masuk lagi tidak; orang LAIN di hari yang sama = wajib (dari = orang sebelumnya);
    serah terima yang belum dikirim bertahan (orang berikutnya yang menghitung); kemarin = gugur
  · hitungan per pecahan + receh = Tutup hari; tanpa seharusnya / selisih di tablet
  · kiriman = persetujuan kabarToko jenis serahLaci (rules v27 stafUsulTablet, tanpa rules baru), tanpa kolom keputusan; owner / tanpa serah / hitungan 0 ditolak
  · owner: seharusnya pada jam serah = rumus laci − uang laci yang tercatat SESUDAH jam itu; nota sesudahnya tidak mengubah selisih; papan = "Serah terima laci",
    bukan uang, ditandai dibaca; push HP berjudul "Serah terima laci"
  · layar: app.js menahan layar lain di Menu selama wajib, owner tidak pernah; kartu paling atas Menu tablet; Belanja tablet per baris harga (+ − sama dengan owner)

    python3 alat-uji/uji_serah_laci.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_serah_laci.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, sys, json, subprocess, tempfile

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru as UB  # noqa: E402
import uji_tutup_tablet as TT  # noqa: E402
JSC = UB.JSC
SLL = 'baru/js/layar/serah-laci-logika.js'; SLP = 'baru/js/layar/serah-laci-panel.js'; SIS = 'baru/js/layar/sistem-logika.js'; FP = 'functions/pesan.js'
APP = 'baru/js/app.js'; MN = 'baru/js/layar/menu.js'; HG = 'baru/js/layar/harga.js'; IDX = 'baru/index.html'; MCSS = 'baru/css/menu.css'
MODUL = list(dict.fromkeys(TT.MODUL + [SLL]))
STATIS = [SLP, APP, MN, HG, IDX, FP, MCSS]

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket === undefined ? '' : ' → ' + (typeof ket === 'string' ? ket : J(ket)).slice(0, 600))); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var _id = 0; var W = { tanggal: '2026-09-19', jam: '13:05', kini: '2026-09-19T06:05:00.000Z', idUnik: function () { return 'sl' + (++_id); } };
var BEN = { jenis: 'aktif', peran: 'ben', nama: 'Jaga Sore', operatorId: 'o2', uid: 'uid-tablet' }; var OWNER = { jenis: 'owner', nama: 'Owner', uid: 'uid-owner' };
var A = { id: 'o1', nama: 'Jaga Pagi' }, B = { id: 'o2', nama: 'Jaga Sore' };

// ---- pemicu
var P1 = slSesudahPin(null, A, { tanggal: '2026-09-19', jam: '07:00' }, null);
ok('orang pertama hari itu: tidak menghitung; tablet mengingat orangnya', P1.wajib === null && P1.terakhir.orangId === 'o1' && P1.terakhir.tanggal === '2026-09-19', P1);
ok('orang yang sama masuk lagi: tidak menghitung', slSesudahPin(P1.terakhir, A, { tanggal: '2026-09-19', jam: '09:40' }, null).wajib === null);
var P2 = slSesudahPin(P1.terakhir, B, { tanggal: '2026-09-19', jam: '13:05' }, null);
ok('orang LAIN di hari yang sama: wajib serah terima, dari = orang sebelumnya, ke = yang datang', P2.wajib && P2.wajib.dari === 'Jaga Pagi' && P2.wajib.ke === 'Jaga Sore' && P2.wajib.sejak === '13:05' && P2.terakhir.orangId === 'o2', P2);
ok('orang lain di hari BERIKUTNYA: tidak menghitung (laci semalam = Tutup hari)', slSesudahPin(P1.terakhir, B, { tanggal: '2026-09-20', jam: '07:00' }, null).wajib === null);
var P3 = slSesudahPin(P2.terakhir, { id: 'o3', nama: 'Jaga Malam' }, { tanggal: '2026-09-19', jam: '13:20' }, P2.wajib);
ok('serah terima yang belum dikirim bertahan: orang berikutnya yang menghitung, "dari" tetap orang sebelumnya', P3.wajib && P3.wajib.dari === 'Jaga Pagi' && P3.wajib.ke === 'Jaga Malam', P3);
ok('serah terima kemarin yang belum dikirim gugur', slMasihWajib(P2.wajib, '2026-09-20') === null && slMasihWajib(P2.wajib, '2026-09-19') === P2.wajib);

// ---- hitung buta
var D1 = { lembar: { 100000: 5, 50000: 2, 2000: 3 }, receh: '1.500' };
var H1 = slHitung(D1, new Date('2026-09-19T13:05:00'));
ok('hitungan per pecahan + receh = Rp607.500 (pecahan Tutup hari)', H1.hitung === 607500 && !H1.tolak, H1);
ok('HITUNG BUTA: hitungan tablet tanpa seharusnya / selisih', J(H1).indexOf('seharusnya') < 0 && J(H1).indexOf('selisih') < 0, Object.keys(H1));

// ---- kiriman
var R1 = slSusunKirim(D1, P2.wajib, BEN, W, new Date('2026-09-19T13:05:00')); var M1 = R1.dokumen ? R1.dokumen[0].data : {};
ok('kiriman: SATU persetujuan kabarToko jenis serahLaci menunggu, atas nama yang jaga', R1.dokumen && R1.dokumen.length === 1 && M1.tindakan === 'kabarToko' && M1.jenis === 'serahLaci' && M1.status === 'menunggu' && M1.mintaUid === 'uid-tablet' && M1.dari === 'Jaga Sore', M1);
ok('kiriman: hitungan 607.500, lembar, receh, dari → ke, jam 13:05; teks menyebutnya', M1.hitung === 607500 && J(M1.lembar) === J({ 2000: 3, 50000: 2, 100000: 5 }) && M1.receh === 1500 && M1.dariOrang === 'Jaga Pagi' && M1.keOrang === 'Jaga Sore' && M1.jam === '13:05'
  && /Jaga Pagi → Jaga Sore jam 13:05 · dihitung Rp607\.500/.test(M1.teks), M1);
ok('kiriman sah rules v27 (usul tablet) & lolos penjaga kiriman Penjaga laci; tanpa kolom keputusan / seharusnya', usulTabletSah(M1, 'uid-tablet') && !periksaKiriman(BEN, [{ koleksi: 'persetujuan', data: M1, ada: false }], [], { hitungLaci: 'sendiri' }).tolak
  && !['diputusPada', 'balasan', 'seharusnya', 'selisih'].some(function (k) { return k in M1; }), M1);
ok('ditolak: akun owner, tanpa serah terima yang menunggu, hitungan kosong', !!slSusunKirim(D1, P2.wajib, OWNER, W).tolak && !!slSusunKirim(D1, null, BEN, W).tolak && !!slSusunKirim({ lembar: {} }, P2.wajib, BEN, W).tolak);

// ---- owner: seharusnya & selisih
var RL = rumusLaci('2026-09-19').seharusnya; var S0 = tdSesudahHitung('2026-09-19', '2026-09-19', '13:05');
var X1 = slSelisih(M1);
ok('owner: seharusnya pada 13:05 = rumus laci − uang laci yang tercatat SESUDAH 13:05; selisih = hitungan − seharusnya', X1.ada && X1.seharusnya === Math.round(RL - S0.net) && X1.selisih === 607500 - X1.seharusnya && /Seharusnya Rp/.test(X1.teks), [X1, RL, S0]);
var jual = cacheMentah('penjualan').slice(); var j4 = jual.find(function (p) { return String(p.id) === 'j4'; });
pasok('penjualan', jual.concat([Object.assign({}, j4, { id: 'j-sesudah', jam: '15:30', totalKg: 3.5, jumlahKarung: 0.07, hargaTotal: 50000, hppTotalSaatJual: 45500 })]));
var X2 = slSelisih(M1);
ok('nota tunai SESUDAH serah terima (15.30) tidak mengubah seharusnya / selisih pada 13:05', X2.seharusnya === X1.seharusnya && X2.selisih === X1.selisih && rumusLaci('2026-09-19').seharusnya === RL + 50000, [X1, X2]);
ok('selisih disebut LEBIH / KURANG / PAS dengan jaga siapa', /(LEBIH|KURANG) Rp[\d.]+ \(jaga Jaga Pagi\)|PAS/.test(X2.teks), X2.teks);
ok('bukan serah terima / tanpa jam = tidak dihitung', slSelisih({ jenis: 'habis', tanggal: '2026-09-19', jam: '13:05' }).ada === false && slSelisih(Object.assign({}, M1, { jam: '' })).ada === false);

// ---- papan & push
pasok('persetujuan', [M1]);
var Q = ssPersetujuan(new Date('2026-09-19T14:00:00')); var q = Q.menunggu.find(function (x) { return x.id === String(M1.id); });
ok('papan Persetujuan: "Serah terima laci", bukan uang, tidak ikut setujui sekaligus, membawa jenisnya', q && q.namaTindakan === 'Serah terima laci' && q.n === 0 && q.sekaligus === false && q.jenis === 'serahLaci' && /Serah terima laci/.test(q.saran), q);
var PU = susunPutusPersetujuan(M1.id, true, 'oke', W);
ok('owner menandai dibaca (+ balasan), bukan disetujui', PU.dokumen && PU.dokumen[0].data.status === 'dibaca' && PU.dokumen[0].data.balasan === 'oke', PU);
var N = __fp.pesanNotif(M1, M1.id);
ok('push HP owner: "Serah terima laci · Jaga Sore"', N && N.judul === 'Serah terima laci · Jaga Sore' && /dihitung Rp607\.500/.test(N.isi), N);
ok('daftar serah terima per akun tablet', slDaftar('uid-tablet').length === 1 && slDaftar('uid-lain').length === 0);
print(J({ lulus: lulus, gagal: gagal }));
"""


def baca(ganti=None):
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(bundel_baru.lengkapi(MODUL) + STATIS)))
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def jalan(t):
    js = UB.JAM_TETAP + '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in bundel_baru.lengkapi(MODUL)])
    js += '\nvar __fp = (function () { var module = { exports: {} }; ' + t[FP] + '\n return module.exports; })();\n'
    js += '\nvar KOTAK = ' + json.dumps(TT.kotak()) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-1200:]
    return json.loads(out[-1]), ''


def statis(t):
    out = []; ok = lambda n, c: out.append(('statis · ' + n, bool(c)))
    app, mn, hg, idx, sp = t[APP], t[MN], t[HG], t[IDX], t[SLP]
    ok('app.js: serah terima dicek sesudah tiap PIN / sidik jari; owner & mode cadangan tidak pernah',
       'setTimeout(() => cekSerahLaci(op), 0);' in app and "if (!a || a.jenis === 'owner' || !op || sumberData().jenis === 'cadangan') return;" in app and "if (!a || a.jenis === 'owner' || sumberData().jenis === 'cadangan') return null;" in app)
    ok('app.js: WAJIB — layar lain tertahan di Menu selama serah terima belum terkirim', "if (tujuan !== 'menu' && serahWajib()) {" in app and "tujuan = 'menu'; }" in app)
    ok('Menu tablet: kartu serah terima PALING ATAS; papan owner menampilkan seharusnya & selisih', 'data-k="staf" style="display: flex; flex-direction: column; gap: 10px;">\n      ${kartuSerahLaci(' in mn and "${m.jenis === 'serahLaci' ? gambarSerahSelisih(m) : ''}" in mn)
    ok('panel tablet hitung buta: tidak memanggil slSelisih / rumus laci', 'slSelisih' not in sp and 'rumusLaci' not in sp and 'seharusnya' not in sp.lower().replace('"seharusnya"', ''))
    ok('Belanja tablet per baris harga: label harga, + − kelompok sama dengan owner, usul per harga', "blStafUbahG: ({ p, g, arah }) => { const H = BL.hitungBelanja(st().pesanStaf || {}, kini()); ubahPesanStaf(BL.ubahKelompok(" in hg
       and "' karung (' + p.g.filter((g) => g.k > 0).map((g) => g.label + ' ' + g.k + ' krg')" in hg and "<span class=\"nm ${g.kritis ? 'awas-teks' : ''}\">${g.label}" in hg)
    mc = t[MCSS]
    ok('Menu tablet punya gaya baris hitung laci, timbang cepat & cek wadah (Tutup hari & serah terima rapi, owner 28 Nov 2026)', all(x in mc for x in ['.layar-menu .th-pecah {', '.layar-menu .th-pecah .ketik-nama {', '.layar-menu .th-baris {', '.layar-menu .th-timb {', '.layar-menu .cw-baris {', '.layar-menu .cw-aksi { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));']))
    ok('modul baru dimuat paralel (modulepreload)', '<link rel="modulepreload" href="js/layar/serah-laci-logika.js">' in idx and '<link rel="modulepreload" href="js/layar/serah-laci-panel.js">' in idx)
    return out


def semua(ganti=None):
    t = baca(ganti); out = statis(t); h, e = jalan(t)
    if h is None: return out + [('JSC JATUH: ' + e, False)]
    return out + [('jsc · ' + x, False) for x in h['gagal']] + [('__jsc', not h['gagal'], h['lulus'])]


RUSAK = [
    ('orang pertama hari itu ikut menghitung', SLL, "const ganti = !!lalu && lalu.tanggal === w.tanggal && !!lalu.orangId && lalu.orangId !== terakhir.orangId;", "const ganti = true;"),
    ('orang yang sama masuk lagi ikut menghitung', SLL, "&& lalu.orangId !== terakhir.orangId;", ";"),
    ('serah terima kemarin tidak gugur', SLL, "(!!wajib && wajib.tanggal === tanggal ? wajib : null)", "(wajib || null)"),
    ('serah terima yang belum dikirim hilang saat orang lain masuk', SLL, "if (wajibLama && wajibLama.tanggal === w.tanggal) return", "if (false) return"),
    ('tablet membawa angka seharusnya', SLL, "return { pecahan: H.pecahan, receh: H.receh, hitung: H.hitung, tolak: H.tolakHitung };", "return { seharusnya: 0, pecahan: H.pecahan, receh: H.receh, hitung: H.hitung, tolak: H.tolakHitung };"),
    ('owner boleh mengirim serah terima', SLL, "if (!akun || !akun.uid || akun.jenis === 'owner') return", "if (!akun || !akun.uid) return"),
    ('nota sesudah serah terima mengubah selisih', SLL, "const seharusnya = Math.round(R.seharusnya - (Number(S.net) || 0));", "const seharusnya = Math.round(R.seharusnya);"),
    ('papan menamai kabar toko biasa', SIS, "namaTindakan: m.jenis === 'serahLaci' ? 'Serah terima laci' : SS_USUL_TABLET[m.tindakan],", "namaTindakan: SS_USUL_TABLET[m.tindakan],"),
    ('push tanpa judul serah terima', FP, ", serahLaci: 'Serah terima laci' };", " };"),
    ('layar tidak tertahan', APP, "if (tujuan !== 'menu' && serahWajib()) {", "if (false) {"),
    ('serah terima tidak dicek sesudah PIN', APP, "setTimeout(() => cekSerahLaci(op), 0);", ""),
    ('kartu serah terima tidak di atas', MN, "gap: 10px;\">\n      ${kartuSerahLaci(", "gap: 10px;\">\n      ${''}${kartuSerahLaci("),
    ('Menu tablet tanpa gaya cek wadah', MCSS, '.layar-menu .cw-aksi { display: grid;', '.layar-menu .cw-aksiX { display: grid;'),
    ('Menu tablet tanpa gaya baris pecahan', MCSS, '.layar-menu .th-pecah {', '.layar-menu .th-pecahX {'),
    ('Belanja tablet per merek lagi', HG, "' karung (' + p.g.filter((g) => g.k > 0).map((g) => g.label + ' ' + g.k + ' krg')", "' karung (' + p.d.map((b) => b.merk + ' ' + b.k)"),
    ('baris Belanja tablet bernama merek', HG, "<span class=\"nm ${g.kritis ? 'awas-teks' : ''}\">${g.label}", "<span class=\"nm ${g.kritis ? 'awas-teks' : ''}\">${g.merk[0].merk}"),
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
    print('SERAH TERIMA LACI & BELANJA PER HARGA: ' + str(n) + ' lulus · ' + str(len(gagal)) + ' gagal')
    return 0 if not gagal else 1


if __name__ == '__main__':
    sys.exit(utama())
