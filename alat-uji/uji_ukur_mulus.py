#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_ukur_mulus.py — KELANCARAN PERANGKAT (owner 19 Nov 2026: "masih berat di Android, terutama tablet Sunmi CPad 11").
baru/js/inti/ukur-mulus.js mencatat DI PERANGKAT tiap layar tersendat (reaksi ketukan ≥ 150 ms, layar macet ≥ 100 ms): berapa lama, di layar mana.
Dibaca di Menu › Sistem › Perangkat. Yang dijaga di sini (jsc, tanpa peramban):
  · catat: di bawah ambang tidak dicatat; hitungan / jumlah / terlama per jenis & per tempat menutup; daftar paling banyak 40, tempat paling banyak 30;
    hari berganti = mulai dari nol; isi lama tidak diubah di tempat.
  · baca: simpanan rusak / hari lain / bentuk asing → kosong; angka & teks dirapikan (tidak ada HTML, tidak ada angka minus).
  · satu ketukan = SATU kejadian (pointerup + click, keydown + input digabung, diambil yang terlama); ketukan berikutnya dihitung sendiri.
  · kalimat kartu & teks salin (bahasa biasa; tanpa rupiah).
  · statis: dipasang app.js, kartunya di Sistem › Perangkat, dipramuat index.html; berkasnya TIDAK menulis ke server (tanpa toko.js / firebase.js),
    simpanan lokal di dalam try/catch, dan tidak ada pengganti berbasis requestAnimationFrame yang jalan terus.

    python3 alat-uji/uji_ukur_mulus.py            → N lulus · 0 gagal
    python3 alat-uji/uji_ukur_mulus.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
UM = 'baru/js/inti/ukur-mulus.js'; FM = 'baru/js/inti/format.js'; AP = 'baru/js/app.js'; MN = 'baru/js/layar/menu.js'; IX = 'baru/index.html'

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
var H = '2026-11-19'; var D = { ketuk: true, macet: true };
// ---- catat
var a = lcKosong(H);
ok('kosong: hari, dua penghitung nol, tanpa tempat, tanpa daftar', J(a) === J({ hari: H, ketuk: { n: 0, total: 0, terlama: 0 }, macet: { n: 0, total: 0, terlama: 0 }, tempat: {}, daftar: [] }), J(a));
var b = lcCatat(a, { jenis: 'ketuk', ms: 149, tempat: 'Jual', aksi: 'x', jam: '10:00' }, H); var c = lcCatat(a, { jenis: 'macet', ms: 99, tempat: 'Jual', jam: '10:00' }, H);
ok('di bawah ambang (ketuk 149 ms, macet 99 ms) tidak dicatat — isi yang sama dikembalikan', b === a && c === a);
var d = lcCatat(a, { jenis: 'ketuk', ms: 150, tempat: 'Jual › Riwayat', aksi: 'rwBuka', jam: '10:01' }, H);
ok('tepat di ambang dicatat: ketuk 150 ms → n 1, total 150, terlama 150; tempat & daftar ikut; isi lama TIDAK berubah', d.ketuk.n === 1 && d.ketuk.total === 150 && d.ketuk.terlama === 150 && d.macet.n === 0 && J(d.tempat) === J({ 'Jual › Riwayat': { n: 1, total: 150, terlama: 150 } }) && J(d.daftar) === J([{ jam: '10:01', ms: 150, jenis: 'ketuk', tempat: 'Jual › Riwayat', aksi: 'rwBuka' }]) && a.ketuk.n === 0 && !a.daftar.length && !Object.keys(a.tempat).length, J([d, a]));
var e = lcCatat(lcCatat(lcCatat(d, { jenis: 'macet', ms: 820.4, tempat: 'Jual › Riwayat', aksi: '', jam: '10:02' }, H), { jenis: 'macet', ms: 100, tempat: 'Stok', jam: '10:03' }, H), { jenis: 'ketuk', ms: 400, tempat: 'Stok', aksi: 'tab', jam: '10:04' }, H);
ok('isi lama tidak diubah di tempat: sesudah tiga catatan berikutnya, isi sebelumnya (d) & isi kosong (a) masih seperti semula', J(d.tempat) === J({ 'Jual › Riwayat': { n: 1, total: 150, terlama: 150 } }) && d.daftar.length === 1 && d.ketuk.n === 1 && !Object.keys(a.tempat).length, J([d, a]));
ok('menutup: Σ per tempat = Σ per jenis (n 4, total 1.470 ms); terlama per jenis & per tempat; pecahan dibulatkan', e.ketuk.n === 2 && e.macet.n === 2 && e.ketuk.total === 550 && e.macet.total === 920 && e.macet.terlama === 820 && e.ketuk.terlama === 400
  && Object.keys(e.tempat).reduce(function (x, k) { return x + e.tempat[k].total; }, 0) === 1470 && Object.keys(e.tempat).reduce(function (x, k) { return x + e.tempat[k].n; }, 0) === 4 && e.tempat['Jual › Riwayat'].terlama === 820 && e.tempat.Stok.n === 2 && e.daftar.length === 4, J(e));
var f = e; for (var i = 0; i < 60; i++) f = lcCatat(f, { jenis: 'macet', ms: 200 + i, tempat: 'T' + i, jam: '11:00' }, H);
ok('batas: daftar paling banyak 40 (yang terbaru), tempat paling banyak 30 (tempat ke-31 dst tidak menambah kunci, penghitung jenis tetap jalan)', f.daftar.length === 40 && f.daftar[39].ms === 259 && Object.keys(f.tempat).length === 30 && f.macet.n === 62, J([f.daftar.length, Object.keys(f.tempat).length, f.macet.n]));
var g = lcCatat(e, { jenis: 'macet', ms: 300, tempat: 'Jual', jam: '00:01' }, '2026-11-20');
ok('hari berganti: mulai dari nol untuk hari baru (yang kemarin tidak terbawa)', g.hari === '2026-11-20' && g.macet.n === 1 && g.ketuk.n === 0 && g.daftar.length === 1 && Object.keys(g.tempat).length === 1, J(g));
ok('tanpa tempat → "lainnya"; teks dirapikan (tanda HTML dibuang, dipotong)', lcCatat(a, { jenis: 'macet', ms: 500, tempat: '', jam: '10:00' }, H).daftar[0].tempat === 'lainnya' && lcCatat(a, { jenis: 'macet', ms: 500, tempat: '<b>Jual</b>', aksi: '"><script>', jam: '10:00' }, H).daftar[0].tempat === 'bJual/b' && lcCatat(a, { jenis: 'macet', ms: 500, tempat: 'x', aksi: '"><script>', jam: '10:00' }, H).daftar[0].aksi === 'script');
// ---- baca
ok('baca: teks JSON sah hari yang sama → isi yang sama', J(lcBaca(J(e), H)) === J(e), J(lcBaca(J(e), H)));
ok('baca: rusak / kosong / hari lain / bentuk asing → kosong hari ini', [null, '', '{', '[]', '{"hari":"2026-11-19"}', J(Object.assign({}, e, { hari: '2026-11-18' })), J(Object.assign({}, e, { daftar: 'x' })), J(Object.assign({}, e, { tempat: null }))].every(function (x) { return J(lcBaca(x, H)) === J(lcKosong(H)); }));
var kotor = lcBaca(J({ hari: H, ketuk: { n: -3, total: 'abc', terlama: 12.6 }, macet: { n: 2, total: 400, terlama: 300 }, tempat: { '<i>Jual</i>': { n: 1, total: 5, terlama: 5 } }, daftar: [{ jam: '10:00<', ms: -5, jenis: 'aneh', tempat: '<x>', aksi: null }] }), H);
ok('baca: angka minus / bukan angka → 0, dibulatkan; teks dirapikan; jenis asing → macet', kotor.ketuk.n === 0 && kotor.ketuk.total === 0 && kotor.ketuk.terlama === 13 && kotor.macet.n === 2 && Object.keys(kotor.tempat)[0] === 'iJual/i' && kotor.daftar[0].jam === '10:00' && kotor.daftar[0].ms === 0 && kotor.daftar[0].jenis === 'macet' && kotor.daftar[0].tempat === 'x' && kotor.daftar[0].aksi === '', J(kotor));
// ---- satu ketukan = satu kejadian
var K = lcKelompokKetuk([{ nama: 'pointerdown', mulai: 1000, ms: 900, aksi: 'a' }, { nama: 'pointerup', mulai: 1090, ms: 200, aksi: 'a' }, { nama: 'click', mulai: 1092, ms: 640, aksi: 'rwBuka' }, { nama: 'mouseup', mulai: 1091, ms: 999, aksi: 'a' }], -1e9);
ok('ketukan: pointerup + click satu ketukan → SATU kejadian, yang terlama (640 ms) + nama tombolnya; pointerdown / mouseup tidak dihitung', K.length === 1 && K[0].ms === 640 && K[0].aksi === 'rwBuka' && K[0].mulai === 1092, J(K));
var K2 = lcKelompokKetuk([{ nama: 'click', mulai: 5000, ms: 300, aksi: 'satu' }, { nama: 'keydown', mulai: 5400, ms: 180, aksi: 'ketik rwCari' }, { nama: 'input', mulai: 5404, ms: 260, aksi: 'ketik rwCari' }, { nama: 'click', mulai: 6000, ms: 150, aksi: '' }], -1e9);
ok('dua ketukan + satu ketikan (keydown + input) berjauhan → tiga kejadian; urutan masuk tidak menentukan', K2.length === 3 && K2[0].ms === 300 && K2[1].ms === 260 && K2[1].aksi === 'ketik rwCari' && K2[2].ms === 150 && J(lcKelompokKetuk([{ nama: 'input', mulai: 5404, ms: 260, aksi: 'q' }, { nama: 'keydown', mulai: 5400, ms: 180, aksi: 'q' }], -1e9).map(function (x) { return x.ms; })) === '[260]', J(K2));
ok('susulan ketukan yang SUDAH dicatat (≤ 80 ms dari kejadian terakhir) tidak dihitung lagi; yang lebih jauh dihitung', lcKelompokKetuk([{ nama: 'click', mulai: 1150, ms: 700, aksi: 'x' }], 1092).length === 0 && lcKelompokKetuk([{ nama: 'click', mulai: 1173, ms: 700, aksi: 'x' }], 1092).length === 1 && lcKelompokKetuk([], 0).length === 0 && lcKelompokKetuk(null, 0).length === 0);
// ---- kalimat
var R = lcRingkas(e, D);
ok('ringkas: "Tersendat hari ini: 4 kali · terlama 0,8 dtk"; dua baris jenis; tiga tempat terberat menurut jumlah waktu', R.n === 4 && R.terlama === 820 && R.judul === 'Tersendat hari ini: 4 kali · terlama 0,8 dtk' && R.baris[0] === 'Reaksi ketukan telat (0,15 detik ke atas): 2 kali · terlama 0,4 dtk' && R.baris[1] === 'Layar macet (0,1 detik ke atas): 2 kali · terlama 0,8 dtk'
  && R.tempat[0].nama === 'Jual › Riwayat' && R.tempat[0].teks === '2 kali · terlama 0,8 dtk · jumlah 1 dtk' && R.tempat[1].nama === 'Stok' && R.adaIsi === true, J(R));
ok('ringkas kosong: "Hari ini belum pernah tersendat"; tanpa alat ukur: "Peramban ini tidak punya alat ukurnya" (tanpa baris); hanya satu alat → satu baris', lcRingkas(a, D).judul === 'Hari ini belum pernah tersendat' && lcRingkas(a, D).adaIsi === false && lcRingkas(a, D).baris[1] === 'Layar macet (0,1 detik ke atas): tidak ada'
  && lcRingkas(e, { ketuk: false, macet: false }).judul === 'Peramban ini tidak punya alat ukurnya' && !lcRingkas(e, { ketuk: false, macet: false }).baris.length && lcRingkas(a, { ketuk: false, macet: true }).baris.length === 1);
ok('lama (sepersepuluh detik): 99 → "99 ms"; 150 → "0,2 dtk"; 820 → "0,8 dtk"; 1000 → "1 dtk"; 1250 → "1,3 dtk"; 12.345 → "12,3 dtk"', lcLama(99) === '99 ms' && lcLama(150) === '0,2 dtk' && lcLama(820) === '0,8 dtk' && lcLama(1000) === '1 dtk' && lcLama(1250) === '1,3 dtk' && lcLama(12345) === '12,3 dtk');
var T = lcTeksSalin(e, D, { perangkat: 'Tablet kasir', peramban: 'UA x', layarPx: '1280×800 @1.5' });
ok('teks salin: kepala hari + perangkat, peramban, layar, ringkasan, per tempat (terberat dulu), kejadian terakhir; tanpa "Rp"', T.split('\n')[0] === 'KELANCARAN 2026-11-19 · Tablet kasir' && /peramban: UA x/.test(T) && /layar: 1280×800 @1.5/.test(T) && /Jual › Riwayat: 2 · 820 ms · 970 ms/.test(T) && /10:02 macet 820 ms · Jual › Riwayat/.test(T) && /10:01 ketuk 150 ms · Jual › Riwayat · rwBuka/.test(T) && T.indexOf('Rp') < 0
  && T.indexOf('Jual › Riwayat: 2') < T.indexOf('Stok: 2'), T);
// ---- mulus Android paket 3: PENYEBAB bingkai panjang (long animation frame) per tempat
var B0 = lcCatatBingkai(e, { ms: 99, skrip: 99, gaya: 0, tempat: 'Jual', fungsi: [] }, H);
ok('bingkai: di bawah 100 ms tidak dicatat — isi yang sama', B0 === e);
var B1 = lcCatatBingkai(e, { ms: 400, skrip: 300, gaya: 80, tempat: 'Jual › Sering', fungsi: [{ nama: 'gambarGulir (jual.js)', ms: 250 }, { nama: 'susunRak (jual-logika.js)', ms: 50 }] }, H);
var B2 = lcCatatBingkai(B1, { ms: 200, skrip: 20, gaya: 170, tempat: 'Jual › Sering', fungsi: [{ nama: 'gambarGulir (jual.js)', ms: 20 }] }, H);
var B3 = lcCatatBingkai(B2, { ms: 300, skrip: 900, gaya: 0, tempat: 'Ringkasan › Cincin', fungsi: [{ nama: '<b>x</b>', ms: 300 }] }, H);
ok('bingkai: per tempat — kali, jumlah, skrip, gaya & tata letak menutup; fungsi dijumlah per nama; skrip tidak melebihi lama bingkai; isi lama tidak berubah',
  J(B2.bingkai['Jual › Sering']) === J({ n: 2, total: 600, skrip: 320, gaya: 250, fungsi: { 'gambarGulir (jual.js)': 270, 'susunRak (jual-logika.js)': 50 } }) && B3.bingkai['Ringkasan › Cincin'].skrip === 300
  && !e.bingkai && Object.keys(B1.bingkai).length === 1 && B3.bingkai['Ringkasan › Cincin'].fungsi['bx/b'] === 300, J(B3.bingkai));
ok('bingkai: catatan ketuk/macet sesudahnya MEMBAWA penyebabnya; hari berganti = kosong', J(lcCatat(B3, { jenis: 'macet', ms: 300, tempat: 'Jual', jam: '10:09' }, H).bingkai) === J(B3.bingkai)
  && !lcCatatBingkai(B3, { ms: 50, tempat: 'x' }, '2026-11-20').bingkai && !lcCatat(B3, { jenis: 'macet', ms: 300, tempat: 'Jual', jam: '00:01' }, '2026-11-20').bingkai);
ok('bingkai: baca/simpan pulang-pergi sama; isi rusak dirapikan (angka minus → 0, teks bersih); tanpa bingkai tetap tanpa kunci bingkai', J(lcBaca(J(B3), H)) === J(B3)
  && J(lcBaca(J(Object.assign({}, e, { bingkai: { '<i>J</i>': { n: -2, total: 'a', skrip: 5, gaya: 1, fungsi: { '<x>': -9 } } } })), H).bingkai) === J({ 'iJ/i': { n: 0, total: 0, skrip: 5, gaya: 1, fungsi: { x: 0 } } })
  && !('bingkai' in lcBaca(J(e), H)), J(lcBaca(J(B3), H)));
var B4 = e; for (var q = 0; q < 45; q++) B4 = lcCatatBingkai(B4, { ms: 150, skrip: 100, gaya: 0, tempat: 'T' + q, fungsi: [{ nama: 'f' + (q % 9), ms: 100 }] }, H);
B4 = lcCatatBingkai(B4, { ms: 150, skrip: 100, gaya: 0, tempat: 'T0', fungsi: [{ nama: 'baru1', ms: 1 }, { nama: 'baru2', ms: 1 }, { nama: 'baru3', ms: 1 }, { nama: 'baru4', ms: 1 }, { nama: 'baru5', ms: 1 }, { nama: 'baru6', ms: 1 }] }, H);
ok('bingkai: batas — paling banyak 30 tempat, 6 nama fungsi per tempat (tempat lama tetap bertambah)', Object.keys(B4.bingkai).length === 30 && B4.bingkai.T0.n === 2 && Object.keys(B4.bingkai.T0.fungsi).length === 6 && !B4.bingkai.T44, J(B4.bingkai.T0));
var L1 = lcTeksBingkai('Jual › Sering', B2.bingkai['Jual › Sering']);
ok('bingkai: baris teks "kali · skrip % · gaya & tata letak % · lain % · terberat"', L1 === 'Jual › Sering: 2 · skrip 53% · gaya & tata letak 42% · lain 5% · terberat: gambarGulir (jual.js) 270 ms, susunRak (jual-logika.js) 50 ms', L1);
var U = lcUraiBingkai({ startTime: 1000, duration: 400, renderStart: 1300, styleAndLayoutStart: 1320, scripts: [{ duration: 200, sourceFunctionName: 'gambar', sourceURL: 'https://x/baru/js/layar/jual.js?v=1' }, { duration: 90, invoker: 'TimerHandler:setTimeout', sourceURL: '' }, { duration: 5, sourceFunctionName: 'kecil', sourceURL: 'a.js' }] });
ok('bingkai: urai entri peramban → skrip = Σ skrip, gaya = akhir − mulai gaya & tata letak, dua fungsi terberat (nama + berkas)', U.ms === 400 && U.skrip === 295 && U.gaya === 80 && J(U.fungsi) === J([{ nama: 'gambar (jual.js)', ms: 200 }, { nama: 'TimerHandler:setTimeout', ms: 90 }]), J(U));
var T3 = lcTeksSalin(B3, D, {}); var R3 = lcRingkas(B3, D);
ok('bingkai: teks salin punya bagian penyebab (terberat dulu); kartu menyebut penyebab gabungan', /— penyebab bingkai panjang per tempat \(kali · skrip · gaya & tata letak · lain\) —/.test(T3) && T3.indexOf('Jual › Sering: 2 · skrip') > 0
  && T3.indexOf('Jual › Sering: 2 · skrip') < T3.indexOf('Ringkasan › Cincin: 1 · skrip') && R3.baris[2] === 'Penyebab bingkai panjang: skrip 69% · gaya & tata letak 28% · lain 3%' && lcRingkas(e, D).baris.length === 2, T3 + ' || ' + J(R3.baris));
print(J({ lulus: lulus, gagal: gagal }));
"""


def baca(ganti=None):
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in [UM, FM, AP, MN, IX])
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def periksa_statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    um = t[UM]; ap = t[AP]; mn = t[MN]; ix = t[IX]
    ok('dipasang app.js sekali, dengan nama layar + tab aktif sebagai tempat', "import { pasangUkurMulus } from './inti/ukur-mulus.js';" in ap and ap.count('pasangUkurMulus({ tempat: () => {') == 1 and "return NAMA_LAYAR[tabKini] + " in ap)
    ok('kartu "Kelancaran perangkat ini" di Sistem › Perangkat (tab Perangkat), dengan lihat / salin rincian & mulai dari nol',
       "import { ukurMulusRingkas, ukurMulusSalin, ukurMulusKosongkan } from '../inti/ukur-mulus.js';" in mn and mn.count('${gambarLancar(s)}') == 2 and '<div style="font-weight: 700;">Kelancaran perangkat ini</div>' in mn
       and 'data-aksi="lcBuka"' in mn and 'data-aksi="lcSalin"' in mn and 'data-aksi="lcNol"' in mn and 'lcNol: () => { ukurMulusKosongkan();' in mn)
    ok('mulus Android paket 3: kartu juga di Menu akun tablet (staf) — owner minta kartunya dari CPad', "${ntAplikasi() ? h`${gambarNotifTablet(s)}${gambarLayarPenuh(s)}` : ''}\n      ${gambarLancar(s)}" in mn)
    ok('mulus Android paket 3: penyebab bingkai dari long-animation-frame (peramban tanpa → tidak diukur)', "jenisAda.indexOf('long-animation-frame') >= 0" in um and "observe({ type: 'long-animation-frame', buffered: false })" in um and 'lcTerimaBingkai(e)' in um)
    ok('kartu menyebut apa yang dicatat & bahwa tidak dikirim ke server', 'Isi nota, nama, dan rupiah tidak ikut dicatat, dan tidak ada yang dikirim ke server.' in mn)
    ok('modul dipramuat index.html', '<link rel="modulepreload" href="js/inti/ukur-mulus.js">' in ix)
    ok('ukur-mulus TIDAK menulis ke server & tidak membaca data toko: hanya mengimpor format.js', um.count('import ') == 1 and "import { hariIniIso } from './format.js';" in um and 'firebase' not in um.replace('// ', '') and 'tulisDokumen' not in um and 'fetch(' not in um and 'sendBeacon' not in um)
    ok('simpanan lokal di dalam try/catch (simpanan penuh tidak menjatuhkan layar), satu kunci', um.count('localStorage.') == 2 and 'try { m = localStorage.getItem(LC_KUNCI); } catch (e)' in um and 'try { localStorage.setItem(LC_KUNCI, JSON.stringify(_isi)); } catch (e)' in um)
    ok('tidak ada pengganti yang jalan terus (requestAnimationFrame / setInterval) — hanya pengamat peramban yang berbunyi saat ada kejadian', 'requestAnimationFrame' not in um and 'setInterval' not in um and "type: 'longtask'" in um and "type: 'event', durationThreshold: LC_AMBANG_KETUK" in um)
    ok('pendengar ketukan pasif & hanya menyimpan nama tombol (data-aksi / data-tujuan / data-ketik), bukan isi layar', "{ capture: true, passive: true }" in um and "el.closest('[data-aksi], [data-tujuan], [data-ketik]')" in um and 'textContent' not in um and '.value' not in um)
    return out


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def semua(ganti=None, bagian=('statis', 'jsc')):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        h, e = jalan(bundel_baru.polos(t[FM]) + '\n' + bundel_baru.polos(t[UM]) + '\n' + SKENARIO)
        if h is None: out.append(('jsc · JATUH: ' + e, False, ''))
        else: out += [('jsc · ' + x, False, '') for x in h['gagal']] + [('__jsc', not h['gagal'], h['lulus'])]
    return out


KONTROL = [
    ('ambang ketukan diturunkan diam-diam (semua ketukan tercatat)', {UM: [("if (ms < (jenis === 'ketuk' ? LC_AMBANG_KETUK : LC_AMBANG_MACET)) return dasar;", "if (ms < 1) return dasar;")]}, ('jsc',)),
    ('hari berganti tidak mengosongkan', {UM: [("const dasar = isi && isi.hari === String(hari || '') ? isi : lcKosong(hari);", "const dasar = isi || lcKosong(hari);")]}, ('jsc',)),
    ('daftar tumbuh tanpa batas', {UM: [("aksi: lcTeks(e.aksi, 40) }]).slice(-LC_MAKS_DAFTAR);", "aksi: lcTeks(e.aksi, 40) }]);")]}, ('jsc',)),
    ('tempat tumbuh tanpa batas', {UM: [("if (tempat[nama] || Object.keys(tempat).length < LC_MAKS_TEMPAT) tempat[nama]", "tempat[nama]")]}, ('jsc',)),
    ('isi lama diubah di tempat', {UM: [("const tempat = Object.assign({}, dasar.tempat);", "const tempat = dasar.tempat;")]}, ('jsc',)),
    ('simpanan hari lain dipakai', {UM: [("String(o.hari || '') !== String(hari || '') || ", "")]}, ('jsc',)),
    ('teks tidak dirapikan (tanda HTML lolos)', {UM: [(".replace(/[^\\w ›·.,:()/+\\-\\u00C0-\\u024F]/g, '')", "")]}, ('jsc',)),
    ('satu ketukan dihitung dua kali (pointerup & click sendiri-sendiri)', {UM: [("if (g && e.mulai - g.akhir <= LC_JARAK_KETUK_MS) {", "if (g && e.mulai - g.akhir <= -1) {")]}, ('jsc',)),
    ('ketukan diambil yang pertama, bukan yang terlama', {UM: [("if (e.ms > g.ms) { g.ms = e.ms; g.aksi = e.aksi || g.aksi; }", "if (false) { g.ms = e.ms; }")]}, ('jsc',)),
    ('susulan kejadian yang sudah dicatat dihitung lagi', {UM: [("if (e.mulai - batas <= LC_JARAK_KETUK_MS) { batas = e.mulai; return; }", "")]}, ('jsc',)),
    ('tempat terberat diurut menurut nama, bukan jumlah waktu', {UM: [(".sort((a, b) => b.total - a.total || b.n - a.n || a.nama.localeCompare(b.nama)).slice(0, 3);", ".sort((a, b) => b.nama.localeCompare(a.nama)).slice(0, 3);")]}, ('jsc',)),
    ('pencatat tidak dipasang di app.js', {AP: [("pasangUkurMulus({ tempat: () => {", "(() => 0)({ tempat: () => {")]}, ('statis',)),
    ('kartu kelancaran hilang dari Sistem › Perangkat', {MN: [("      ${gambarNotifHp(s)}\n      ${gambarLancar(s)}\n", "      ${gambarNotifHp(s)}\n")]}, ('statis',)),
    ('kartu kelancaran hilang dari Menu staf', {MN: [("${gambarLayarPenuh(s)}` : ''}\n      ${gambarLancar(s)}\n", "${gambarLayarPenuh(s)}` : ''}\n")]}, ('statis',)),
    ('bingkai: skrip melebihi lama bingkai', {UM: [("skrip: lama.skrip + Math.min(ms, lcBulat(e.skrip))", "skrip: lama.skrip + lcBulat(e.skrip)")]}, ('jsc',)),
    ('bingkai: catatan ketuk/macet membuang penyebab', {UM: [("  if (dasar.bingkai) out.bingkai = dasar.bingkai;", "")]}, ('jsc',)),
    ('bingkai: tempat tumbuh tanpa batas', {UM: [("if (!bk[nama] && Object.keys(bk).length >= LC_MAKS_TEMPAT) return dasar;", "")]}, ('jsc',)),
    ('bingkai: hari berganti tidak mengosongkan', {UM: [("const dasar = isi && isi.hari === hariIni ? isi : lcKosong(hariIni);", "const dasar = isi || lcKosong(hariIni);")]}, ('jsc',)),
    ('bingkai: nama fungsi tanpa batas', {UM: [("if (fn[k] !== undefined || Object.keys(fn).length < LC_MAKS_FUNGSI) fn[k]", "fn[k]")]}, ('jsc',)),
    ('bingkai: tidak diamati', {UM: [("observe({ type: 'long-animation-frame', buffered: false })", "observe({ type: 'longtask-x', buffered: false })")]}, ('statis',)),
    ('bingkai: gaya dihitung dari mulai bingkai', {UM: [("const gaya = e.styleAndLayoutStart > 0 ? Math.max(0, akhir - e.styleAndLayoutStart) : 0;", "const gaya = e.duration;")]}, ('jsc',)),
    ('catatan dikirim ke server', {UM: [("function lcSimpan() { _jamSimpan = null; ", "function lcSimpan() { _jamSimpan = null; fetch('/x', { method: 'POST', body: JSON.stringify(_isi) }); ")]}, ('statis',)),
    ('simpanan lokal tanpa try/catch', {UM: [("try { localStorage.setItem(LC_KUNCI, JSON.stringify(_isi)); } catch (e) { /* simpanan penuh / dilarang: catatan hari ini tetap di ingatan */ }", "localStorage.setItem(LC_KUNCI, JSON.stringify(_isi));")]}, ('statis',)),
    ('pencatat membaca isi layar (teks tombol)', {UM: [("return a ? (a.dataset.aksi || ", "return a ? (a.textContent || a.dataset.aksi || ")]}, ('statis',)),
]

if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti, bagian in KONTROL:
            try: h = semua(ganti, bagian)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' · ' + str(e)[:160]); kode = 3; continue
            g = [x for x in h if not x[1]]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h = semua(); g = [x for x in h if not x[1]]
    n = sum(1 for x in h if x[1] and x[0] != '__jsc') + next((x[2] for x in h if x[0] == '__jsc'), 0)
    for x in g: print('   ✗ ' + x[0] + (' → ' + json.dumps(x[2], ensure_ascii=False)[:400] if x[2] not in ('', None) else ''))
    print('UKUR MULUS: %d lulus · %d gagal' % (n, len(g)))
    sys.exit(1 if g else 0)
