#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_ringkas_tablet.py — RINGKAS HARI INI di tablet (owner 21 Nov 2026), dijalankan ASLI di jsc dengan data contoh yang laci & kasnya sudah dihitung
tangan (bahan uji_uang_baru.py), ditambah pemeriksaan pemasangannya.

Kenapa ada: kartu ini memajang LACI & UANG KELUAR di tablet toko — data yang sampai v13 tidak pernah boleh dibaca akun tablet. Keputusan owner 21 Nov:
dibuka (rules v14) untuk akun tablet yang ditandai owner, tampil hanya saat orang pilihan owner jaga lewat PIN-nya. Yang paling mahal kalau salah: angka
laci yang beda dengan HP owner, angka uang yang ditebak saat datanya belum ada, dan data uang yang tertinggal di layar orang lain.

Yang dipegang:
  · laci = rumus Tutup hari yang SAMA (semalam + masuk − keluar), dikurangi titipan tablet yang belum diputus; uang keluar dikelompokkan kamus yang sama
  · data uang belum siap / ditolak server / akun belum ditandai = laci & uang keluar TIDAK dihitung (null + kalimat), bukan Rp0
  · kartu hanya untuk orang pilihan owner; data uang hanya bila akun tabletnya bertanda bacaUang (Penjaga laci saja — karyawan tidak pernah)
  · akses.js: tanda bacaUang hanya untuk Penjaga laci; pendengar uang TIDAK masuk pendengarPeran (layar staf lain tetap memperlakukan uang di luar haknya)
  · sistem-logika: orang pilihan owner wajib ada di daftar tablet & ikut terbawa saat setelan peran lain disimpan; menandai akun = dua ketukan,
    peran turun dari Penjaga laci = tanda ikut mati
  · pemasangan: rules v14 (baca saja, daftar koleksi = akses.js BACA_UANG), firebase.js memasang/mencabut & mengosongkan memori, app.js menyegarkan
    tiap ganti orang / data, Menu menggambar kartu di atas titipan hanya lewat gerbang rtTampil, owner mengatur di Orang di tablet

    python3 alat-uji/uji_ringkas_tablet.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_ringkas_tablet.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json, copy, glob, subprocess, tempfile

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru as UB  # noqa: E402   bahan: daftar modul uang + kotak data yang laci & kasnya sudah dihitung tangan
JSC = UB.JSC
RTL = 'baru/js/layar/ringkas-tablet-logika.js'; RTP = 'baru/js/layar/ringkas-tablet-panel.js'; AK = 'baru/js/data/akses.js'; SL = 'baru/js/layar/sistem-logika.js'
FB = 'baru/js/data/firebase.js'; APP = 'baru/js/app.js'; MN = 'baru/js/layar/menu.js'; RULES = 'firestore.rules'; TH = 'baru/js/layar/tutup-hari-logika.js'; CSS = 'baru/css/menu.css'
# stok-hpp-logika SENGAJA tidak ikut: teksMargin-nya bertabrakan dengan harga-logika di satu lingkup; daftarBarang tidak memakainya (riwayatModal)
MODUL = list(dict.fromkeys(UB.MODUL + ['baru/js/data/hemat-baca.js', 'baru/js/layar/stok-logika.js', 'baru/js/layar/titipan-logika.js',
                                       AK, SL, RTL]))
STATIS = [RTP, FB, APP, MN, RULES, CSS]
DOM = 'baru/js/inti/dom.js'

HEX32 = '0' * 32; HEX64 = 'a' * 64
OPERATOR = {'oown1': {'nama': 'Owner', 'peran': 'ben', 'aktif': True, 'garam': 'g' + HEX32, 'acak': HEX64, 'iterasi': 100000},
            'oben1': {'nama': 'Ben', 'peran': 'ben', 'aktif': True, 'garam': 'g' + HEX32, 'acak': HEX64, 'iterasi': 100000}}


def kotak():
    K = copy.deepcopy(UB.KOTAK)
    oleh = {'j3': 'Owner', 'j4': 'Ben', 'j5': 'Ben'}
    for p in K['penjualan']:
        if p['id'] in oleh: p['oleh'] = oleh[p['id']]
    # 19 Sep: uang keluar laci hari ini = belanja toko 30.000 + kasbon 50.000 (dikelompokkan kamus rumus laci)
    K['pengeluaranHarian'].append({'id': 'h6', 'kategori': 'toko', 'tanggal': '2026-09-19', 'jam': '10:05', 'keterangan': 'Kantong plastik', 'nominal': 30000})
    K['kasbonMutasi'].append({'id': 703, 'tipe': 'ambil', 'namaPegawai': 'Gama', 'nominal': 50000, 'tanggal': '2026-09-19', 'jam': '10:10', 'catatan': 'Bensin'})
    K['pesanan'] = [{'id': 'ps1', 'namaPelanggan': 'Bu Contoh', 'isi': '2 karung Angsa', 'status': 'dipesan', 'tanggalKirim': '2026-09-19'},
                    {'id': 'ps2', 'namaPelanggan': 'Pak Contoh', 'isi': '1 karung IR64', 'status': 'diantar', 'tanggalKirim': '2026-09-18'},
                    {'id': 'ps3', 'namaPelanggan': 'Tuntas', 'isi': 'x', 'status': 'dibayar', 'tanggalKirim': '2026-09-19'},
                    {'id': 'ps4', 'namaPelanggan': 'Besok', 'isi': 'x', 'status': 'dipesan', 'tanggalKirim': '2026-09-20'}]
    K['suratJalan'] = [{'id': 'sj1', 'noSJ': 'SJ26-X-0001', 'status': 'berangkat', 'namaPelanggan': 'Pak Contoh'}, {'id': 'sj2', 'noSJ': 'SJ26-X-0002', 'status': 'diterima'}]
    # titik kas dari DOKUMEN (tablet tidak pernah punya salinan perangkat) — sama dengan uji_uang_baru: laci 2.000.000 · brankas 10 jt · rekening 3 jt · amplop 1 jt
    K['pengaturan'] = [{'id': 'titikKas', 'tanggal': '2026-09-15', 'laci': 2000000, 'brankas': 10000000, 'rekening': 3000000, 'amplop': 1000000, 'diubahPada': '2026-09-15T14:00:00.000Z'}]
    K['aturanToko'] = [{'id': 'peran', 'ringkasOrang': 'oown1', 'operator': OPERATOR}]
    K['aksesAkun'] = [{'id': 'uid-tablet', 'uid': 'uid-tablet', 'nama': 'Tablet', 'email': 'tablet@contoh.com', 'peran': 'ben', 'aktif': True},
                      {'id': 'uid-k', 'uid': 'uid-k', 'nama': 'Karyawan', 'email': 'k@contoh.com', 'peran': 'karyawan', 'aktif': True}]
    return K


SKENARIO = r"""
var hasil = []; var J = JSON.stringify;
function cek(nama, ok, ket) { hasil.push({ nama: nama, ok: !!ok, ket: ket === undefined ? '' : (typeof ket === 'string' ? ket : J(ket)) }); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var KINI = new Date(Date.now());
var OWNER_JAGA = { jenis: 'aktif', peran: 'ben', nama: 'Owner', operatorId: 'oown1', uid: 'uid-tablet', bacaUang: true };
var BEN_JAGA = { jenis: 'aktif', peran: 'ben', nama: 'Ben', operatorId: 'oben1', uid: 'uid-tablet', bacaUang: true };
var SIAP = { nyala: true, siap: 11, total: 11, ditolak: [] };

// ---------- gerbang kartu & data uang ----------
cek('kartu tampil saat orang pilihan owner jaga', rtTampil(OWNER_JAGA) === true);
cek('kartu TIDAK tampil saat orang lain jaga di akun yang sama', rtTampil(BEN_JAGA) === false);
cek('kartu tidak tampil untuk akun owner (HP / Mac) atau akun tanpa orang jaga', rtTampil({ jenis: 'owner', peran: 'owner', nama: 'Owner', uid: 'u' }) === false && rtTampil({ jenis: 'aktif', peran: 'ben', nama: 'T', uid: 'u' }) === false);
cek('owner mematikan (ringkasOrang kosong) = kartu hilang', rtTampil(OWNER_JAGA, '') === false);
cek('data uang dimuat hanya bila kartu tampil DAN akun tablet bertanda', rtBukaUang(OWNER_JAGA) === true && rtBukaUang(BEN_JAGA) === false && rtBukaUang(Object.assign({}, OWNER_JAGA, { bacaUang: false })) === false);

// ---------- keadaan data uang: tidak pernah ditebak ----------
cek('akun belum bertanda → mati', rtKeadaanUang(Object.assign({}, OWNER_JAGA, { bacaUang: false }), SIAP).st === 'mati');
cek('ditolak server → ditolak (sebut aturan v14)', rtKeadaanUang(OWNER_JAGA, { nyala: true, siap: 11, total: 11, ditolak: ['pengeluaranHarian: permission-denied'] }).st === 'ditolak' && /v14/.test(rtKeadaanUang(OWNER_JAGA, { nyala: true, siap: 11, total: 11, ditolak: ['x'] }).teks));
cek('belum lengkap → muat (bukan Rp0)', rtKeadaanUang(OWNER_JAGA, { nyala: true, siap: 4, total: 11, ditolak: [] }).st === 'muat' && rtKeadaanUang(OWNER_JAGA, null).st === 'muat');
var Rm = rtHitung(KINI, OWNER_JAGA, { nyala: true, siap: 4, total: 11, ditolak: [] });
cek('data uang belum siap: laci & uang keluar null (tidak dihitung), omzet tetap', Rm.laci === null && Rm.keluar === null && Rm.omzet === 1150000, { laci: Rm.laci, keluar: Rm.keluar, omzet: Rm.omzet });

// ---------- angka hari 19 Sep (dihitung tangan) ----------
var R = rtHitung(KINI, OWNER_JAGA, SIAP);
cek('omzet 1.150.000 · 3 nota (tunai 250.000, QRIS 600.000, bon 300.000)', R.omzet === 1150000 && R.nota === 3 && R.tunai === 250000 && R.qris === 600000 && R.bon === 300000, { omzet: R.omzet, nota: R.nota, tunai: R.tunai, qris: R.qris, bon: R.bon });
cek('laci = rumus Tutup hari: semalam 2.230.000 + masuk 250.000 − keluar 80.000 = 2.400.000', R.laci && R.laci.ada && R.laci.awal === 2230000 && R.laci.masuk === 250000 && R.laci.keluar === 80000 && R.laci.seharusnya === 2400000, R.laci);
cek('seharusnya di kartu = seharusnya di Tutup hari (satu rumus)', R.laci && R.laci.seharusnya === rumusLaci('2026-09-19').seharusnya, { kartu: R.laci && R.laci.seharusnya, tutup: rumusLaci('2026-09-19').seharusnya });
cek('perkiraan isi laci = seharusnya − titipan tablet belum diputus (15.000) = 2.385.000', R.laci && R.laci.titipan === 15000 && R.laci.kira === 2385000, R.laci);
cek('uang keluar hari ini 80.000: belanja toko 30.000 + kasbon 50.000 (kelompok kamus rumus laci)', R.keluar && R.keluar.total === 80000 && J(R.keluar.daftar.map(function (x) { return [x.nama, x.rp]; })) === J([['Kasbon karyawan/owner', 50000], ['Uang keluar toko', 30000]]), R.keluar);
cek('uang keluar kemarin tidak ikut', R.keluar && !R.keluar.daftar.some(function (x) { return /Prive|Ambil pribadi/.test(x.nama); }));
cek('titipan menunggu disebut: 1 · 15.000', R.titipan.n === 1 && R.titipan.rp === 15000, R.titipan);
cek('per orang: Owner 1 nota 600.000, Ben 2 nota 550.000 (urut rupiah)', J(R.perOrang) === J([{ nama: 'Owner', nota: 1, rp: 600000 }, { nama: 'Ben', nota: 2, rp: 550000 }]), R.perOrang);
cek('terlaris: IR64 Apex 40 kg di atas Angsa 39,2 kg', R.terlaris.length === 2 && R.terlaris[0].nama === 'IR64 Apex' && R.terlaris[0].kg === 40 && R.terlaris[1].nama === 'Angsa' && R.terlaris[1].kg === 39.2, R.terlaris);
cek('pesanan: yang lewat (18 Sep, diantar) lalu hari ini; tuntas & besok tidak ikut', R.pesanan.length === 2 && R.pesanan[0].nama === 'Pak Contoh' && R.pesanan[0].lewat && R.pesanan[1].nama === 'Bu Contoh' && !R.pesanan[1].lewat, R.pesanan);
cek('surat jalan masih di jalan: 1', R.jalan.length === 1 && R.jalan[0].no === 'SJ26-X-0001', R.jalan);
cek('stok tipis terbaca tanpa galat (daftar)', Array.isArray(R.tipis));

// ---------- cetak ----------
var T = rtTeksCetak(R, { nama: 'Toko Contoh' }, { tanggal: '2026-09-19', jam: '10:30', oleh: 'Owner' });
cek('cetak: omzet, perkiraan isi laci, uang keluar, per orang, pencetak', /Omzet · 3 nota  Rp1\.150\.000/.test(T) && /PERKIRAAN ISI LACI  Rp2\.385\.000/.test(T) && /Uang keluar hari ini Rp80\.000/.test(T) && /Owner · 1 nota  Rp600\.000/.test(T) && /Dicetak .* 10:30, Owner/.test(T), T);
var Tm = rtTeksCetak(Rm, null, { tanggal: '2026-09-19', jam: '10:30', oleh: 'Owner' });
cek('cetak tanpa data uang: laci disebut belum terbaca, tidak ada angka laci', /Laci: data uang belum terbaca/.test(Tm) && !/PERKIRAAN ISI LACI/.test(Tm), Tm);

// ---------- akses.js ----------
var aBen = keadaanAkun('tablet@contoh.com', 'uid-tablet', { peran: 'ben', aktif: true, nama: 'Tablet', bacaUang: true });
var aKar = keadaanAkun('k@contoh.com', 'uid-k', { peran: 'karyawan', aktif: true, nama: 'K', bacaUang: true });
cek('keadaanAkun: tanda bacaUang hanya untuk Penjaga laci', aBen.bacaUang === true && aKar.bacaUang === false && keadaanAkun('t@c', 'u', { peran: 'ben', aktif: true, nama: 'T' }).bacaUang === false);
cek('pendengarUang: 10 koleksi uang + pengaturan/titikKas untuk akun bertanda; kosong untuk yang lain', pendengarUang(aBen).length === 11 && pendengarUang(aBen).some(function (p) { return p.nama === 'pengaturan' && J(p.dok) === J(['titikKas']); }) && pendengarUang(aKar).length === 0 && pendengarUang(null).length === 0);
cek('pendengarPeran (dasar) TIDAK memuat koleksi uang', !pendengarPeran(aBen).some(function (p) { return BACA_UANG.indexOf(p.nama) >= 0 || (p.dok || []).indexOf('titikKas') >= 0; }));
cek('angkaBoleh tetap: uang di luar hak akun tablet (layar staf lain)', angkaBoleh(aBen, ['pengeluaranHarian']) !== '');

// ---------- sistem-logika (owner mengatur) ----------
var W = { tanggal: '2026-09-19', jam: '10:30', kini: '2026-09-19T03:30:00.000Z', idUnik: function () { return 'id' + Math.random(); } };
var r1 = susunAturSistem('peran', { ringkasOrang: 'oxxx9' }, W);
cek('orang Ringkas yang tidak ada di daftar tablet ditolak', !!r1.tolak && /tidak ada di daftar/.test(r1.tolak), r1.tolak);
var r2 = susunAturSistem('peran', { ringkasOrang: 'oben1' }, W);
cek('orang Ringkas yang ada → tertulis', !r2.tolak && r2.dokumen && r2.dokumen[0].data.ringkasOrang === 'oben1', r2.tolak || r2.dokumen);
var r3 = susunAturSistem('peran', { jatahBen: 5 }, W);
cek('menyimpan setelan peran lain membawa orang Ringkas utuh', !r3.tolak && r3.dokumen && r3.dokumen[0].data.ringkasOrang === 'oown1', r3.tolak || (r3.dokumen && r3.dokumen[0].data.ringkasOrang));
var r4 = susunAturSistem('peran', { ringkasOrang: '' }, W);
cek('mematikan = kosong', !r4.tolak && r4.dokumen[0].data.ringkasOrang === '');
var u1 = susunUbahAkun('uid-tablet', { bacaUang: true }, W, false);
cek('menandai akun membaca data uang = dua ketukan', !!u1.perluYakin && /MEMBACA data uang/.test(u1.tolak), u1);
var u2 = susunUbahAkun('uid-tablet', { bacaUang: true }, W, true);
cek('ketukan kedua → aksesAkun bacaUang true, peran & aktif utuh', u2.dokumen && u2.dokumen[0].koleksi === 'aksesAkun' && u2.dokumen[0].data.bacaUang === true && u2.dokumen[0].data.peran === 'ben' && u2.dokumen[0].data.aktif === true, u2);
cek('akun karyawan tidak bisa ditandai', /hanya untuk akun Penjaga laci/.test(susunUbahAkun('uid-k', { bacaUang: true }, W, true).tolak || ''));
cek('mencabut tanda = sekali ketuk', (function () { var x = susunUbahAkun('uid-tablet', { bacaUang: false }, W, false); return x.dokumen && x.dokumen[0].data.bacaUang === false; })());
pasok('aksesAkun', [{ id: 'uid-tablet', uid: 'uid-tablet', nama: 'Tablet', email: 'tablet@contoh.com', peran: 'ben', aktif: true, bacaUang: true }]);
var u5 = susunUbahAkun('uid-tablet', { peran: 'karyawan' }, W, false);
cek('peran turun dari Penjaga laci = tanda baca uang ikut mati', u5.dokumen && u5.dokumen[0].data.peran === 'karyawan' && u5.dokumen[0].data.bacaUang === false, u5);
cek('daftar akun owner menyebut tanda', ssAkun().akun[0].bacaUang === true);
print(J(hasil));
"""


def baca_semua():
    return dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(MODUL + STATIS + [TH])))


def rakit(t):
    isi = lambda m: t[m] if m in t else open(os.path.join(AKAR, m), encoding='utf-8').read()   # modul yang ditambah lengkapi() dibaca dari berkas
    return '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(isi(m)) for m in bundel_baru.lengkapi(MODUL)])


def jalankan(t):
    js = UB.JAM_TETAP + rakit(t) + '\nvar KOTAK = ' + json.dumps(kotak()) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    keluar = (r.stdout or '').strip().split('\n')[-1] if r.stdout else ''
    if r.returncode != 0 or not keluar.startswith('['): return [{'nama': 'jsc jalan', 'ok': False, 'ket': ((r.stderr or '') + (r.stdout or ''))[-1500:]}]
    return json.loads(keluar)


def periksa_statis(t):
    c = []; ok = lambda n, x, k='': c.append({'nama': n, 'ok': bool(x), 'ket': k})
    R = t[RULES]; rata = lambda s: re.sub(r'\s+', ' ', s)
    tanpa = re.sub(r'//[^\n]*', '', R)
    ok('rules v14: stafBacaUang() = masuk() + bacaUangDari(akun()); bacaUangDari = aktif + peran ben + bacaUang (default false)',
       'function stafBacaUang() { return masuk() && bacaUangDari(akun()); }' in tanpa and "function bacaUangDari(a) { return a.aktif == true && a.peran == 'ben' && a.get('bacaUang', false) == true; }" in tanpa)
    blok = dict((m.group(1), m.group(2)) for m in re.finditer(r'\n    match /(\w+)/\{\w+\} \{\n(.*?)\n    \}', tanpa, re.S))
    dibuka = sorted(n for n, b in blok.items() if re.search(r'allow read: if owner\(\) \|\| stafBacaUang\(\);', b))
    m = re.search(r"export const BACA_UANG = \[([^\]]*)\];", t[AK]); baca_uang = sorted(re.findall(r"'(\w+)'", m.group(1))) if m else []
    ok('rules v14: koleksi yang dibuka baca = akses.js BACA_UANG (10 koleksi)', dibuka == baca_uang and len(dibuka) == 10, {'rules': dibuka, 'akses': baca_uang})
    ok("rules v14: pengaturan/titikKas dibaca akun bertanda (= DOK_UANG)", "(id == 'titikKas' && stafBacaUang())" in blok.get('pengaturan', '') and "export const DOK_UANG = { pengaturan: ['titikKas'] };" in t[AK])
    tulis_uang = [n for n, b in blok.items() if re.search(r'allow (create|update|delete|write)[^;]*stafBacaUang', b, re.S)]
    ok('rules v14: stafBacaUang hanya di baris BACA (tulis uang tetap owner)', not tulis_uang, tulis_uang)
    F = t[FB]
    ok('firebase.js: setelDataUang memasang hanya untuk akun bertanda (bacaUangAkun) & sekali per perubahan',
       'export function setelDataUang(nyala)' in F and 'const boleh = !!nyala && !!db && status.masuk && bacaUangAkun(status.akun);' in F and 'if (boleh === _uangNyala) return;' in F)
    ok('firebase.js: cabut = lepas pendengar + KOSONGKAN memori koleksi uang & titikKas', "BACA_UANG.forEach((n) => pasok(n, []));" in F and "DOK_UANG[n].forEach((id) => { delete peta[id]; });" in F)
    ok('firebase.js: cabut semua pendengar (keluar / ganti peran) ikut mencabut data uang', 'cabutUang(false);' in (re.search(r'\nfunction cabutPendengar\(\) \{\n(.*?)\n\}\n', F, re.S) or re.search('', '')).group(0))
    ok('firebase.js: titikKas berbagi peta setelan per dokumen dengan pendengar dasar (tempatSimpan tidak tertimpa)', 'const perDok = {}; _perDok = perDok;' in F and 'const peta = _perDok[p.nama] = _perDok[p.nama] || {};' in F)
    A = t[APP]
    ok('app.js: segarkanUang = setelDataUang(rtBukaUang(akun efektif))', 'function segarkanUang() { try { fb.setelDataUang(rtBukaUang(akunKini())); }' in A)
    ok('app.js: disegarkan tiap ganti orang (gambarAkun) & tiap data/status', re.search(r'akun = efektifDari\(asli\); _tandaAkun = tandaAkun\(\);\n  segarkanUang\(\);', A) is not None and 'fb.dengarkanStatus(() => segarkanUang());' in A)
    ok('app.js: Menu diberi status data uang', 'statusUang: () => statusFb.uang' in A)
    M = t[MN]
    i_rt = M.find('${RT.rtTampil(akunM) ? kartuRingkas('); i_tp = M.find('${kartuTitipan(s, { akun: akunM')
    ok('Menu: kartu Ringkas hanya lewat gerbang rtTampil, paling atas (di atas titipan)', 0 < i_rt < i_tp and M.count('kartuRingkas(') == 1, (i_rt, i_tp))
    ok('Menu: owner memilih orang & menandai akun di Orang di tablet', '${gambarRingkasOwner(s, D)}' in M and "rtPilihOrang: ({ id }) => tulis(S.susunAturSistem('peran', { ringkasOrang: id === '-' ? '' : id }, waktu()))" in M and "S.susunUbahAkun(uid, { bacaUang: nyala === '1' }, waktu(), st().yakinRt === kunci)" in M)
    P = t[RTP]
    ok('panel: angka besar bergulir (omzet & laci) — layar baru wajib hidup', 'data-gulir="${Math.round(R.omzet)}"' in P and 'data-gulir="${Math.round(L.kira)}"' in P)
    ok('panel: cetak hanya untuk orang pilihan owner', "if (!RT.rtTampil(a)) return set({ kabar: 'Ringkas hari ini hanya untuk orang pilihan owner'" in P)
    ok('panel & logika tidak menulis apa pun', not re.search(r'tulis\(|dokumen:\s*\[', P + t[RTL]))
    ok('CSS: kartu dua lajur di tablet, baris masuk bergiliran, hormat reduced-motion', '.layar-menu .rt-dua' in t[CSS] and 'animation: masuk' in t[CSS].split('.layar-menu .rt-baris {')[1].split('\n')[0] and '.layar-menu .rt-baris { animation: none; }' in t[CSS])
    return c


# ---- ASAP DATA TOKO (opsional, hanya di Mac owner: _privat/backup-batch-*.json; CI tidak punya cadangan → dilewati). Kartu dihitung & DIRAKIT jadi HTML di atas
# cadangan sungguhan pada hari dagang terakhir di cadangan itu: angka laci = rumus Tutup hari, omzet & cara bayar = ringkasHari Tutup hari, tanpa "undefined"/"NaN".
# Yang dicetak hanya lulus/gagal — angka toko tidak keluar ke layar uji.
ASAP = r"""
var hasil = []; var J = JSON.stringify;
function cek(nama, ok, ket) { hasil.push({ nama: nama, ok: !!ok, ket: ket === undefined ? '' : String(ket) }); }
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
if (CAD.titikKas) pasok('pengaturan', [Object.assign({ id: 'titikKas' }, CAD.titikKas)].concat((CAD.pengaturan || []).filter(function (d) { return String(d.id) !== 'titikKas'; })));
var unduh = hariIniIso(new Date(CAD.diunduhPada)); var iso = ambilPenjualan().map(function (p) { return p.tanggal || ''; }).filter(function (x) { return x && x <= unduh; }).sort().pop() || unduh;
var KINI = new Date(iso + 'T20:00:00'); var AK = { jenis: 'aktif', peran: 'ben', nama: 'Owner', operatorId: 'oasap', uid: 'uid-tablet', bacaUang: true };
var SIAP = { nyala: true, siap: 11, total: 11, ditolak: [] }; var R = null;
try { R = rtHitung(KINI, AK, SIAP); cek('data toko: ringkas terhitung tanpa galat (hari dagang terakhir di cadangan)', true); } catch (e) { cek('data toko: ringkas terhitung tanpa galat', false, String(e && e.stack || e).slice(0, 400)); }
if (R) {
  var RL = rumusLaci(iso); var RH = ringkasHari(iso);
  cek('data toko: laci seharusnya kartu = rumus laci Tutup hari', R.laci && (RL.ada ? R.laci.ada && R.laci.seharusnya === RL.seharusnya : !R.laci.ada));
  cek('data toko: omzet, nota, tunai, QRIS, bon kartu = ringkasHari Tutup hari', R.omzet === RH.omzet && R.nota === RH.nota && R.tunai === RH.tunai && R.qris === RH.qrisJual && R.bon === RH.kredit);
  cek('data toko: titipan menunggu = Tutup hari', R.titipan.rp === tpMenungguSampai(iso).rp);
  var html = ''; try { html = kartuRingkas({ rtRinci: true }, { akun: AK, uang: SIAP, kini: KINI }).html; } catch (e) { html = 'GALAT ' + String(e && e.stack || e); }
  cek('data toko: kartu dirakit jadi HTML (rincian laci terbuka) tanpa galat, tanpa "undefined" / "NaN"', html && html.indexOf('GALAT') !== 0 && !/undefined|NaN/.test(html), html.slice(0, 200));
  cek('data toko: kartu memuat omzet & perkiraan laci (angka yang sama dengan hitungan)', html.indexOf(RP(R.omzet)) >= 0 && (!R.laci || !R.laci.ada || html.indexOf(RP(R.laci.kira)) >= 0));
  var tk = rtTeksCetak(R, null, { tanggal: iso, jam: '20:00', oleh: 'Owner' });
  cek('data toko: teks cetak tanpa "undefined" / "NaN"', !/undefined|NaN/.test(tk));
  var Rm = rtHitung(KINI, AK, { nyala: true, siap: 3, total: 11, ditolak: [] }); var hm = kartuRingkas({}, { akun: AK, uang: { nyala: true, siap: 3, total: 11, ditolak: [] }, kini: KINI }).html;
  cek('data toko: data uang belum lengkap → kartu menyebut memuat, tanpa angka laci', Rm.laci === null && /Memuat data uang/.test(hm) && !/Perkiraan isi laci sekarang/.test(hm));
}
print(J(hasil));
"""


def asap(t):
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')))
    if not cad: return [], 'tanpa cadangan toko di mesin ini — dilewati'
    isi = lambda m: t[m] if m in t else open(os.path.join(AKAR, m), encoding='utf-8').read()
    modul = list(dict.fromkeys(bundel_baru.lengkapi(MODUL) + [DOM, RTP]))
    js = '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(isi(m)) for m in modul])
    js += '\nvar RT = { rtHitung: rtHitung, rtTampil: rtTampil, rtTeksCetak: rtTeksCetak, rtKeadaanUang: rtKeadaanUang };\n'   # import * as RT (panel) di satu lingkup
    js = UB.JAM_TETAP + js + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    keluar = (r.stdout or '').strip().split('\n')[-1] if r.stdout else ''
    if r.returncode != 0 or not keluar.startswith('['): return [{'nama': 'data toko: jsc jalan', 'ok': False, 'ket': ((r.stderr or '') + (r.stdout or ''))[-800:]}], os.path.basename(cad[-1])
    return json.loads(keluar), os.path.basename(cad[-1])


def periksa(t, diam=False):
    c = jalankan(t) + periksa_statis(t)
    if not diam:
        ca, sumber = asap(t); c += ca
        print('asap data toko: ' + sumber)
    g = [x for x in c if not x['ok']]
    if not diam:
        for x in c: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:600]))
        print('RINGKAS HARI INI DI TABLET: %d lulus · %d gagal' % (len(c) - len(g), len(g)))
    return g


def main():
    t = baca_semua()
    if '--kontrol' in sys.argv:
        R = t[RTL]; A = t[AK]; S = t[SL]; F = t[FB]; AP = t[APP]; M = t[MN]; RU = t[RULES]
        rusak = [
            ('kartu tampil untuk siapa pun yang jaga', RTL, R.replace('String(akun.operatorId) === o;', 'true;')),
            ('data uang dimuat tanpa tanda akun', RTL, R.replace('rtTampil(akun, orang) && akun.bacaUang === true;', 'rtTampil(akun, orang);')),
            ('laci dihitung walau data uang belum siap (Rp0 / angka karangan)', RTL, R.replace("if (K.st === 'siap') {", "if (true) {")),
            ('titipan belum diputus tidak dikurangkan dari laci', RTL, R.replace('kira: RL.seharusnya - T.rp,', 'kira: RL.seharusnya,')),
            ('uang keluar hari lain ikut', RTL, R.replace("if (r.t !== iso || !(r.keluar > 0)) return;", "if (!(r.keluar > 0)) return;")),
            ('per orang menghitung baris, bukan nota', RTL, R.replace('nota: orang[k].nota.size,', 'nota: orang[k].nota.size + 1,')),
            ('pesanan tuntas ikut', RTL, R.replace("['dipesan', 'diantar'].indexOf(String(x.status || '')) >= 0 && ", '')),
            ('tanda bacaUang untuk karyawan juga', AK, A.replace("bacaUang: peran === 'ben' && dok.bacaUang === true };", "bacaUang: dok.bacaUang === true };")),
            ('koleksi uang masuk pendengar dasar (layar staf lain ikut membaca uang)', AK, A.replace('const out = BACA_STAF.map((n) => ({ nama: n }));', 'const out = BACA_STAF.concat(BACA_UANG).map((n) => ({ nama: n }));')),
            ('orang Ringkas tidak diperiksa ada di daftar', SL, S.replace("if (ro && !(o.operator || {})[ro]) tolak = tolak || 'Orang pembuka Ringkas hari ini tidak ada di daftar tablet'; else o.ringkasOrang = ro;", 'o.ringkasOrang = ro;')),
            ('menandai akun tanpa ketukan kedua', SL, S.replace('if (U.bacaUang && !yakin) return', 'if (false) return')),
            ('peran turun tetap membaca uang', SL, S.replace("turunDariBen && a.bacaUang ? { bacaUang: false } : {}", '{}')),
            ('cabut tidak mengosongkan memori uang', FB, F.replace('BACA_UANG.forEach((n) => pasok(n, []));', '')),
            ('cabut semua pendengar lupa data uang', FB, F.replace('  cabutUang(false);\n  _pendengarKoleksi.forEach(', '  _pendengarKoleksi.forEach(')),
            ('app tidak menyegarkan data uang saat data / status berubah', APP, AP.replace('  fb.dengarkanStatus(() => segarkanUang());', '')),
            ('Menu menggambar kartu tanpa gerbang', MN, M.replace('${RT.rtTampil(akunM) ? kartuRingkas(', '${true ? kartuRingkas(')),
            ('rules: tanda dibaca untuk karyawan juga (peran tidak dinilai)', RULES, RU.replace("a.aktif == true && a.peran == 'ben' && a.get('bacaUang', false) == true", "a.aktif == true && a.get('bacaUang', false) == true")),
            ('rules: satu koleksi uang terbuka TULIS untuk akun bertanda', RULES, RU.replace("    match /pindahUang/{id} {\n      allow read: if owner() || stafBacaUang();\n      allow create: if owner() && tglBaru('tanggal');", "    match /pindahUang/{id} {\n      allow read: if owner() || stafBacaUang();\n      allow create: if (owner() || stafBacaUang()) && tglBaru('tanggal');")),
            ('rules: koleksi uang yang dibaca beda dengan akses.js', RULES, RU.replace("    match /tutupHari/{id} {\n      allow read: if owner() || stafBacaUang();", "    match /tutupHari/{id} {\n      allow read: if owner();")),
        ]
        kode = 0
        for nama, berkas, isi in rusak:
            if isi == t[berkas]: print('KONTROL BASI  ' + nama); kode = 3; continue
            t2 = dict(t); t2[berkas] = isi; g = periksa(t2, diam=True)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0]['nama'][:100] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    sys.exit(1 if periksa(t) else 0)


if __name__ == '__main__':
    main()
