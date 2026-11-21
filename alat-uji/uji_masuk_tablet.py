#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_masuk_tablet.py — BARANG MASUK & BAYAR SUPIR dari tablet (owner 22 Nov 2026, paket ③; rules v15), dijalankan ASLI di jsc di atas data contoh
uji_uang_baru.py (kedatangan RODA CONTOH 20 Agu: Angsa Rp13.000/kg, IR64 Apex Rp14.000/kg; hari ini 19 Sep), ditambah pemeriksaan pemasangannya.

Kenapa ada: kedatangan dari tablet langsung mengubah STOK, MODAL & BON pemasok, dan uang yang keluar dari laci (upah bongkar, bayar ke supir) jadi titipan yang
owner tulis ke kedatangan / bon. Yang paling mahal kalau salah: kedatangan tablet yang tercatat tunai (laci berkurang tanpa titipan), upah bongkar yang
terhitung dua kali, bayar supir yang masuk bon yang salah / bertanggal hari owner menyetujui, dan harga beda yang tidak sampai ke owner.

Yang dipegang:
  · kiriman tablet = kedatangan (bon, hari ini, bongkar 0, dariTablet) + titipan upah bongkar (batchId) + titipan bayar supir (pemasok, batchId) + kabar owner
  · bentuknya lolos penjaga kiriman akses.js (= rules v15); karyawan / kisi kedatangan "tidak" ditolak
  · merek baru / arsip ditolak dengan kalimat (owner dari HP); harga beda dari harga lalu ditandai & disebut di kabar; beda jauh dari modal = digabung, ditandai
  · owner menyetujui upah bongkar → biayaBongkar kedatangan itu (laci keluar sekali, bertanggal datang); dua kali tidak bisa
  · owner menyetujui bayar supir → bon kedatangan itu (bawaan) atau bon pilihan owner; bertanggal TITIPAN; sisa bon turun; melebihi sisa ditolak
  · titipan yang menunggu ikut perkiraan laci (laci fisik sudah berkurang); tanda terima tablet menyebut uang yang dibayar ke supir

    python3 alat-uji/uji_masuk_tablet.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_masuk_tablet.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json, copy, subprocess, tempfile

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru as UB  # noqa: E402
JSC = UB.JSC
MT = 'baru/js/layar/masuk-tablet-logika.js'; TPL = 'baru/js/layar/titipan-logika.js'; AK = 'baru/js/data/akses.js'; TBL = 'baru/js/layar/terima-barang-logika.js'
SC = 'baru/js/layar/stok-catat-logika.js'; STK = 'baru/js/layar/stok.js'; UG = 'baru/js/layar/uang.js'; SL = 'baru/js/layar/sistem-logika.js'; KB = 'baru/js/layar/kabar-baru-logika.js'
TBP = 'baru/js/layar/terima-barang-panel.js'; TPP = 'baru/js/layar/titipan-panel.js'; IDX = 'baru/index.html'; FN = 'functions/pesan.js'; RULES = 'firestore.rules'
# stok-hpp-logika SENGAJA tidak ikut (teksMargin bertabrakan dengan harga-logika di satu lingkup) — pola uji_ringkas_tablet.py
import uji_stok_baru as SB  # noqa: E402   urutan modul Stok (varian-logika sebelum stok-catat: konstanta tingkat atas)
MODUL = [m for m in dict.fromkeys(SB.MODUL + UB.MODUL + ['baru/js/data/hemat-baca.js', TPL, AK, 'baru/js/layar/sistem-logika.js', TBL, MT]) if not m.endswith('harga-logika.js') or m.endswith('stok-hpp-logika.js')]
STATIS = [STK, UG, SL, KB, TBP, TPP, IDX, FN, RULES]


def kotak():
    K = copy.deepcopy(UB.KOTAK)
    # IR64 Apex di kotak uang = nama WADAH (bukan merek karung) → kedatangan tablet memakai merek karung yang punya buku: Pandan Contoh (datang TUNAI 10 Agu, Rp14.000/kg)
    K['batchMasuk'].append({'id': 'b0', 'tanggal': '2026-08-10', 'jam': '09:00', 'pemasok': 'RODA CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
                            'merkList': [{'id': '1', 'merk': 'Pandan Contoh', 'satuan': 'karung', 'jumlahKarung': 10, 'beratKarung': 50, 'totalKg': 500, 'hargaPerKg': 14000, 'subtotalHarga': 7000000}]})
    # titik kas dari DOKUMEN (pola uji_ringkas_tablet): laci 2.000.000 dst. per 15 Sep — rumus laci tanggal 19 Sep terhitung
    K['pengaturan'] = [{'id': 'titikKas', 'tanggal': '2026-09-15', 'laci': 2000000, 'brankas': 10000000, 'rekening': 3000000, 'amplop': 1000000, 'diubahPada': '2026-09-15T14:00:00.000Z'}]
    K['aksesAkun'] = [{'id': 'uid-tablet', 'uid': 'uid-tablet', 'nama': 'Tablet', 'email': 'tablet@contoh.com', 'peran': 'ben', 'aktif': True}]
    return K


SKENARIO = r"""
var hasil = []; var J = JSON.stringify;
function cek(nama, ok, ket) { hasil.push({ nama: nama, ok: !!ok, ket: ket === undefined ? '' : (typeof ket === 'string' ? ket : J(ket)) }); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var _id = 0; var W = { tanggal: '2026-09-19', jam: '10:30', kini: '2026-09-19T03:30:00.000Z', idUnik: function () { return 'mt' + (++_id); } };
var W2 = { tanggal: '2026-09-20', jam: '08:00', kini: '2026-09-20T01:00:00.000Z', idUnik: function () { return 'ow' + (++_id); } };   // owner menyetujui BESOKNYA
var BEN = { jenis: 'aktif', peran: 'ben', nama: 'Penjaga A', operatorId: 'o1', uid: 'uid-tablet' };
var KRY = { jenis: 'aktif', peran: 'karyawan', nama: 'Orang B', uid: 'uid-k' };
var HAK_BEN = { jualTunai: 'sendiri', jualBon: 'sendiri', nego: 'owner', terimaBon: 'sendiri', hitungLaci: 'sendiri', uangKeluar: 'owner', adukan: 'sendiri', kedatangan: 'sendiri', hargaBeli: 'tidak', koreksi: 'owner', hapus: 'tidak', pelangganBaru: 'sendiri', atur: 'tidak', isiUlang: 'sendiri' };
var HAK_KRY = Object.assign({}, HAK_BEN, { uangKeluar: 'tidak', jualBon: 'owner', hitungLaci: 'tidak' });
var kirim = function (akun, r, hak) { return periksaKiriman(akun, (r.dokumen || []).map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false }; }), [], hak); };
var CACHE = { batchMasuk: 'batch', utangPemasokMutasi: 'utangPemasok', persetujuan: 'persetujuan' };   // nama simpanan = koleksi.js (cache)
var tulis = function (r) { (r.dokumen || []).forEach(function (x) { var a = cacheMentah(CACHE[x.koleksi] || x.koleksi).slice(); var i = a.findIndex(function (d) { return String(d.id) === String(x.data.id); }); if (i >= 0) a[i] = x.data; else a.push(x.data); pasok(x.koleksi, a); }); return r; };
var DRAF = { pemasok: 'RODA CONTOH', caraBayar: 'tunai', tanggal: '2026-09-01', bongkar: '70.000', bayarSupir: '1.000.000',
  baris: [{ merk: 'Angsa', jumlahKarung: '60', beratKarung: 50, hargaPerKg: '13000' }, { merk: 'Pandan Contoh', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '14.500' }] };

// ---------- kiriman tablet ----------
var titip0 = tpMenungguSampai('2026-09-19').rp; var laci0 = rumusLaci('2026-09-19'); var bon0 = hitungUtangPemasok().find(function (p) { return p.pemasok === 'RODA CONTOH'; });
var R = mtSusunSimpan(DRAF, BEN, W, false);
cek('kiriman tablet: 4 dokumen — kedatangan, titipan upah bongkar, titipan bayar supir, kabar owner', R.dokumen && J(R.dokumen.map(function (x) { return x.koleksi + (x.data.jenis ? ':' + x.data.jenis : x.data.tindakan === 'barangMasuk' ? ':kabar' : ''); })) === J(['batchMasuk', 'persetujuan:bongkar', 'persetujuan:bayarBon', 'persetujuan:kabar']), R.tolak || (R.dokumen || []).map(function (x) { return x.koleksi; }));
if (!R.dokumen || R.dokumen.length < 4) { print(J(hasil)); throw new Error('kiriman tablet tidak tersusun: ' + (R.tolak || J(R))); }
var BM = R.dokumen[0].data; var TB = R.dokumen[1].data; var TS = R.dokumen[2].data; var KBR = R.dokumen[3].data;
cek('kedatangan: BON (bukan tunai yang ada di draf), tanggal HARI INI (bukan tanggal draf), bongkar 0, bertanda dariTablet', BM.caraBayar === 'utang' && BM.tanggal === '2026-09-19' && BM.biayaBongkar === 0 && BM.dariTablet === true, BM);
cek('kedatangan: 60 karung Angsa 3.000 kg Rp39.000.000 + 10 karung Pandan Contoh 500 kg Rp7.250.000', BM.merkList.length === 2 && BM.merkList[0].totalKg === 3000 && BM.merkList[0].subtotalHarga === 39000000 && BM.merkList[1].totalKg === 500 && BM.merkList[1].subtotalHarga === 7250000, BM.merkList);
cek('harga beda dari harga lalu ditandai di kedatangan: Pandan Contoh 14.500 (lalu 14.000); Angsa sama → tidak', J(BM.hargaBeda) === J([{ merk: 'Pandan Contoh', harga: 14500, lalu: 14000, persen: 3.6 }]), BM.hargaBeda);
cek('titipan upah bongkar: 70.000, menunjuk kedatangannya, menunggu owner', TB.tindakan === 'uangKeluar' && TB.jenis === 'bongkar' && TB.nominal === 70000 && TB.batchId === String(BM.id) && TB.status === 'menunggu' && TB.mintaUid === 'uid-tablet', TB);
cek('titipan bayar supir: 1.000.000, pemasok & kedatangan ikut', TS.jenis === 'bayarBon' && TS.nominal === 1000000 && TS.pemasok === 'RODA CONTOH' && TS.batchId === String(BM.id), TS);
cek('kabar owner: barangMasuk menunggu, menunjuk kedatangan, menyebut harga beda, bongkar & bayar supir', KBR.tindakan === 'barangMasuk' && KBR.batchId === String(BM.id) && /Pandan Contoh Rp14\.500 \(lalu Rp14\.000\)/.test(KBR.teks) && /bongkar Rp70\.000/.test(KBR.teks) && /supir Rp1\.000\.000/.test(KBR.teks), KBR.teks);
cek('kiriman lolos penjaga kiriman akses.js (bentuk rules v15)', !kirim(BEN, R, HAK_BEN).tolak, kirim(BEN, R, HAK_BEN));
cek('kiriman yang sama dari karyawan / Penjaga laci berkisi kedatangan "tidak" ditolak', !!kirim(KRY, R, HAK_KRY).tolak && !!kirim(BEN, R, Object.assign({}, HAK_BEN, { kedatangan: 'tidak' })).tolak);
cek('penjaga kiriman: kedatangan tablet yang TUNAI atau membawa upah bongkar ditolak (= rules v15)', !!kirim(BEN, { dokumen: [{ koleksi: 'batchMasuk', data: Object.assign({}, BM, { caraBayar: 'tunai' }) }] }, HAK_BEN).tolak
  && !!kirim(BEN, { dokumen: [{ koleksi: 'batchMasuk', data: Object.assign({}, BM, { biayaBongkar: 70000 }) }] }, HAK_BEN).tolak);
cek('akses.js: kedatangan tablet = tindakan kedatangan (bukan isi ulang)', J(tindakanKiriman(R.dokumen.slice(0, 1).map(function (x) { return { koleksi: x.koleksi, data: x.data, ada: false }; }))) === J(['kedatangan']));

// ---------- tolakan tablet ----------
var Rb = mtSusunSimpan(Object.assign({}, DRAF, { baris: [{ merk: 'Merek Contoh Baru', jumlahKarung: '60', beratKarung: 50, hargaPerKg: '12000' }] }), BEN, W, false);
cek('merek baru → ditolak, owner yang mencatat dari HP', /belum punya buku stok/.test(Rb.tolak || ''), Rb.tolak);
var Rk = mtSusunSimpan(Object.assign({}, DRAF, { baris: [{ merk: 'Angsa', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '13000' }] }), BEN, W, false);
cek('karung sedikit → ketuk sekali lagi; ketukan kedua tersimpan', !!Rk.perluYakin && !!(mtSusunSimpan(Object.assign({}, DRAF, { baris: [{ merk: 'Angsa', jumlahKarung: '10', beratKarung: 50, hargaPerKg: '13000' }] }), BEN, W, true).dokumen), Rk.tolak);
var Rj = mtSusunSimpan(Object.assign({}, DRAF, { baris: [{ merk: 'Angsa', jumlahKarung: '60', beratKarung: 50, hargaPerKg: '15000' }] }), BEN, W, false);
cek('harga jauh dari modal (Angsa 15.000 vs 13.000) → dicatat sebagai Angsa yang sama (tablet tidak memutus mutu), ditandai hargaJauh & disebut di kabar', Rj.dokumen && Rj.dokumen[0].data.merkList[0].merk === 'Angsa' && J(Rj.dokumen[0].data.hargaJauh) === J(['Angsa']) && /digabung: Angsa/.test(Rj.dokumen[3].data.teks), Rj.tolak || Rj.dokumen[0].data);
cek('upah bongkar / bayar supir bukan angka → ditolak; kosong → tanpa titipan', /Upah bongkar hanya angka/.test(mtSusunSimpan(Object.assign({}, DRAF, { bongkar: 'tujuh puluh' }), BEN, W, false).tolak || '')
  && mtSusunSimpan(Object.assign({}, DRAF, { bongkar: '', bayarSupir: '' }), BEN, W, false).dokumen.length === 2);
cek('tanpa orang yang jaga → ditolak', !!mtSusunSimpan(DRAF, null, W, false).tolak);

// ---------- tersimpan: laci fisik & buku ----------
tulis(R);
cek('titipan yang menunggu ikut perkiraan laci: + upah bongkar 70.000 + bayar supir 1.000.000', tpMenungguSampai('2026-09-19').rp - titip0 === 1070000, [titip0, tpMenungguSampai('2026-09-19').rp]);
var laci1 = rumusLaci('2026-09-19');
cek('kedatangan bon tidak mengurangi laci di buku sebelum owner menyetujui', laci1.ada && laci0.ada && laci1.seharusnya === laci0.seharusnya, [laci0.seharusnya, laci1.seharusnya]);
var bon1 = hitungUtangPemasok().find(function (p) { return p.pemasok === 'RODA CONTOH'; });
cek('bon RODA CONTOH bertambah persis nilai nota kedatangan tablet (46.250.000)', Math.round(bon1.bon.reduce(function (a, b) { return a + b.sisa; }, 0) - bon0.bon.reduce(function (a, b) { return a + b.sisa; }, 0)) === 46250000, [bon0.bon, bon1.bon]);

// ---------- tanda terima di tablet ----------
var TT = tbmData(BM, { terbaca: false, titipSupir: 1000000 }); var GT = tbmGaris(TT, { nama: 'Toko Contoh' }, 'pemasok', { tanggal: W.tanggal, jam: W.jam, oleh: 'Penjaga A' });
cek('tanda terima tablet: bon, angka buku tidak terbaca, uang ke supir 1.000.000 tertulis; sisa ditulis tangan', TT.bayar.keadaan === 'takTerbaca' && TT.bayar.titipSupir === 1000000 && GT.some(function (g) { return g.kiri === 'Dibayar ke supir' && g.kanan === 'Rp1.000.000'; }) && GT.some(function (g) { return g.kiri === 'Sisa: Rp'; }), GT.filter(function (g) { return !g.garis; }).map(function (g) { return g.kiri + ' | ' + g.kanan; }));

// ---------- owner menyetujui upah bongkar ----------
var PB = tpSusunPutus(TB.id, 'setuju', {}, W2);
cek('setujui upah bongkar = kedatangan ditulis ulang dengan biayaBongkar 70.000 & bongkarTitipan; tanpa dokumen uang lain', PB.dokumen && PB.dokumen.length === 2 && PB.dokumen[1].koleksi === 'batchMasuk' && PB.dokumen[1].data.biayaBongkar === 70000 && J(PB.dokumen[1].data.bongkarTitipan) === J([TB.id]) && PB.dokumen[1].data.tanggal === '2026-09-19', PB.tolak || PB.dokumen[1].data);
tulis(PB);
var laci2 = rumusLaci('2026-09-19');
cek('sesudah disetujui: laci di buku tanggal DATANG berkurang tepat 70.000 (bongkar dari laci), titipannya keluar dari perkiraan', laci1.seharusnya - laci2.seharusnya === 70000 && tpMenungguSampai('2026-09-19').rp - titip0 === 1000000, [laci1.seharusnya, laci2.seharusnya]);
cek('upah bongkar tidak bisa ditulis dua kali', (function () { var m = cacheMentah('persetujuan').find(function (x) { return x.id === TB.id; }); var lama = m.status; m.status = 'menunggu'; var x = tpSusunPutus(TB.id, 'setuju', {}, W2); m.status = lama; return /dua kali/.test(x.tolak || ''); })());

// ---------- owner menyetujui bayar supir ----------
var PL = tpBonPilihan(TS.id, new Date(W2.kini));
cek('pilihan bon: bon RODA CONTOH yang bersisa (20 Agu + kedatangan tablet), bawaan = kedatangan tablet', PL.bon.length === 2 && PL.bawaan === String(BM.id) && PL.bon[0].tanggal === '2026-08-20', PL);
var PS = tpSusunPutus(TS.id, 'setuju', {}, W2);
cek('setujui bayar supir = bayar bon kedatangan tablet 1.000.000 dari laci, bertanggal TITIPAN (19 Sep), bukan hari owner menyetujui', PS.dokumen && PS.dokumen[1].koleksi === 'utangPemasokMutasi' && PS.dokumen[1].data.bonId === String(BM.id) && PS.dokumen[1].data.nominal === 1000000 && PS.dokumen[1].data.dari === 'laci' && PS.dokumen[1].data.tanggal === '2026-09-19' && PS.dokumen[1].data.dariPersetujuan === TS.id, PS.tolak || PS.dokumen[1].data);
var PS2 = tpSusunPutus(TS.id, 'setuju', { bonId: 'b1' }, W2);
cek('owner memilih bon lama 20 Agu → pembayarannya ke bon itu', PS2.dokumen && PS2.dokumen[1].data.bonId === 'b1' && PS2.dokumen[0].data.bonId === 'b1', PS2.tolak || PS2.dokumen[1].data);
cek('bayar melebihi sisa bon yang dipilih → ditolak', /Melebihi sisa/.test(tpSusunPutus(TS.id, 'setuju', { bonId: 'b1', nominal: '25.000.000' }, W2).tolak || ''));
tulis(PS);
var bon2 = hitungUtangPemasok().find(function (p) { return p.pemasok === 'RODA CONTOH'; }); var bn = bon2.bon.find(function (b) { return String(b.id) === String(BM.id); });
cek('sesudah disetujui: sisa bon kedatangan tablet = 46.250.000 − 1.000.000; laci tanggal titipan berkurang 1.000.000; titipan keluar dari perkiraan', bn && Math.round(bn.sisa) === 45250000 && laci2.seharusnya - rumusLaci('2026-09-19').seharusnya === 1000000 && tpMenungguSampai('2026-09-19').rp === titip0, [bn, laci2.seharusnya, rumusLaci('2026-09-19').seharusnya]);
var TT2 = tbmData(BM, { terbaca: false, titipSupir: 1000000 }); cek('kalimat layar tanda terima tablet menyebut uang ke supir', /dibayar ke supir Rp1\.000\.000/.test(tbmKalimatBayar(TT2)), tbmKalimatBayar(TT2));

// ---------- kabar owner ----------
cek('kabar barang masuk tampil di daftar owner sebagai kabar (bukan uang); ditandai sudah diperiksa', tpMenunggu().some(function (b) { return b.id === KBR.id && b.kabar && b.pesan; }) && tpSusunPutus(KBR.id, 'dibaca', {}, W2).dokumen[0].data.status === 'dibaca');
print(J(hasil));
"""


def baca_semua():
    return dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(MODUL + STATIS)))


def rakit(t):
    isi = lambda m: t[m] if m in t else open(os.path.join(AKAR, m), encoding='utf-8').read()
    return '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(isi(m)) for m in bundel_baru.lengkapi(MODUL)])


def jalankan(t):
    js = UB.JAM_TETAP + rakit(t) + '\nvar KOTAK = ' + json.dumps(kotak()) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    keluar = (r.stdout or '').strip().split('\n')[-1] if r.stdout else ''
    if r.returncode != 0 or not keluar.startswith('['): return [{'nama': 'jsc jalan', 'ok': False, 'ket': ((r.stderr or '') + (r.stdout or ''))[-1500:]}]
    return json.loads(keluar)


def periksa_statis(t):
    c = []; ok = lambda n, x, k='': c.append({'nama': 'statis: ' + n, 'ok': bool(x), 'ket': k})
    S = t[STK]
    ok('Stok: akun tablet menyimpan lewat mtSusunSimpan (owner tetap susunSimpanMasuk)', "const r = bukanOwner(akM) ? MT.mtSusunSimpan(d, akM, waktu(), st().yakinM) : C.susunSimpanMasuk(d, waktu(), st().yakinM);" in S)
    ok('Stok: akun tablet menggambar form tablet', "if (bukanOwner(opsi.akun ? opsi.akun() : null)) return gambarMasukTablet(s);" in S)
    m = re.search(r'\n  function gambarMasukTablet\(s\) \{\n(.*?)\n  \}\n', S, re.S); f = m.group(1) if m else ''
    ok('form tablet: tanpa pilihan cara bayar / tanggal / koreksi / hapus / aturan; ada upah bongkar & bayar ke supir', f and not re.search(r"caraBayar|mTanggal|mKoreksi|mHapus|bukaAturC|mKelas|mVarian", f) and 'data-kolom="bongkar"' in f and 'data-kolom="bayarSupir"' in f, len(f))
    ok('Stok: draf kosong tablet = mtDrafKosong (selalu bon)', "bukanOwner(opsi.akun ? opsi.akun() : null) ? MT.mtDrafKosong(waktu()) : C.drafMasukKosong(waktu())" in S)
    U = t[UG]
    ok('Uang: owner memilih bon untuk bayar supir & melihat ke mana titipan barang masuk ditulis', 'ukTtBon: ({ b }) =>' in U and 'bonId: t.bonId || \'\'' in U and 'function tujuanTitip(t)' in U and '${tujuanTitip(t)}' in U)
    ok('Uang: kabar barang masuk ditandai "Sudah diperiksa"', "p.kabar ? 'Sudah diperiksa' : 'Tandai dibaca'" in U)
    ok('papan Persetujuan & notifikasi dalam aplikasi mengenal kabar barang masuk', "m.tindakan === TP_PESAN || m.tindakan === TP_KABAR) return tpSusunPutus(id, 'dibaca'" in t[SL] and "barangMasuk: 'Barang masuk dari tablet'" in t[KB])
    ok('tanda terima: titipan bayar supir ikut (menunggu selalu; disetujui hanya bila buku bon tak terbaca)', "titipSupir: titipSupir(batch, terbaca)" in t[TBP] and "m.jenis === 'bayarBon' && String(m.batchId || '') === String(batch.id)" in t[TBP])
    ok('kartu titipan tablet: bayar bon pemasok memilih / mengetik pemasok', "data-aksi=\"tpPemasok\"" in t[TPP] and "tpPemasok: ({ p }) =>" in t[TPP])
    ok('index.html memuat masuk-tablet-logika lebih dulu (modulepreload)', '<link rel="modulepreload" href="js/layar/masuk-tablet-logika.js">' in t[IDX])
    ok('push HP menyebut upah bongkar, bayar bon pemasok, barang masuk', "bongkar: 'Upah bongkar', bayarBon: 'Bayar bon pemasok'" in t[FN] and "barangMasuk: 'Barang masuk'" in t[FN])
    ok('rules v15: kedatangan tablet lewat stafCatatMasuk([ben]); kabar lewat stafKabarMasuk([ben])', "(stafCatatMasuk(['ben']) && tglStaf('tanggal'))" in t[RULES] and "stafKabarMasuk(['ben']);" in t[RULES])
    ok('logika tablet tidak menulis sendiri (hanya menyusun)', not re.search(r'tulisDokumen|setDoc|import .*firebase', t[MT]))
    return c


def periksa(t, diam=False):
    c = jalankan(t) + periksa_statis(t)
    g = [x for x in c if not x['ok']]
    if not diam:
        for x in c: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:700]))
        print('BARANG MASUK DARI TABLET: %d lulus · %d gagal' % (len(c) - len(g), len(g)))
    return g


def main():
    t = baca_semua()
    if '--kontrol' in sys.argv:
        M = t[MT]; T = t[TPL]; A = t[AK]; TB = t[TBL]
        rusak = [
            ('kedatangan tablet tercatat tunai (laci berkurang tanpa titipan)', MT, M.replace("d.id = null; d.tanggal = w.tanggal; d.caraBayar = 'utang';", "d.id = null; d.tanggal = w.tanggal;").replace("{ dariTablet: true, biayaBongkar: 0, caraBayar: 'utang' }", "{ dariTablet: true, biayaBongkar: 0 }")),
            ('kedatangan tablet memakai tanggal draf', MT, M.replace("d.id = null; d.tanggal = w.tanggal;", "d.id = null;")),
            ('upah bongkar ikut ditulis di kedatangan (terhitung dua kali sesudah disetujui)', MT, M.replace("{ dariTablet: true, biayaBongkar: 0, caraBayar: 'utang' }", "{ dariTablet: true, biayaBongkar: bongkar, caraBayar: 'utang' }")),
            ('tanpa kabar owner', MT, M.replace("  dokumen.push(tpDokKabarMasuk({ batchId: id, pemasok, nominal: h.nilaiBeras, teks: teksKabar, hargaBeda: beda }, akun, w));\n", "")),
            ('merek baru boleh dari tablet', MT, M.replace("if (b.terisi && !b.masalah && b.baru) b.masalahTablet", "if (false) b.masalahTablet")),
            ('harga beda tidak ditandai', MT, M.replace("if (beda.length) bm.hargaBeda = beda;", "")),
            ('upah bongkar disetujui tanpa menambah kedatangan', TPL, T.replace("biayaBongkar: (Number(b.biayaBongkar) || 0) + n,", "biayaBongkar: (Number(b.biayaBongkar) || 0),")),
            ('bayar supir mengabaikan bon pilihan owner', TPL, T.replace("const bonId = KOSONG(o.bonId) ? P.bawaan : String(o.bonId);", "const bonId = P.bawaan;")),
            ('bayar supir bertanggal hari owner menyetujui', TPL, T.replace("uang = { koleksi: 'utangPemasokMutasi', data: { id: w.idUnik(), tanggal: tgl, jam,", "uang = { koleksi: 'utangPemasokMutasi', data: { id: w.idUnik(), tanggal: w.tanggal, jam,")),
            ('penjaga kiriman: kedatangan tablet boleh tunai', AK, A.replace("d.dariTablet === true && d.caraBayar === 'utang' && d.biayaBongkar === 0", "d.dariTablet === true && d.biayaBongkar === 0")),
            ('tanda terima melupakan uang ke supir', TBL, TB.replace("hasil.titipSupir = bon ? Math.max(0, Math.round(bil(B.titipSupir))) : 0;", "hasil.titipSupir = 0;")),
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
