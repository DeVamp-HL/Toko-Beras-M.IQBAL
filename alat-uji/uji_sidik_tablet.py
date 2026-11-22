#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_sidik_tablet.py — SIDIK JARI OWNER DI TABLET, Tahap A (owner 22 Nov 2026), dijalankan ASLI di jsc (sidik-logika, sistem-logika, akses) + pemeriksaan
pemasangan di app.js / menu.js.

Kenapa ada: Android hanya tahu "jari terdaftar", bukan jari siapa, dan PIN layar kunci tablet bukan pengaman. Sidik jari owner aman HANYA bila tiap masuk
& intip lewat KUNCI PENANDA (sidik jari kuat, hangus bila ada jari baru) dan hangusnya mematikan fitur + mengabari owner. Yang paling mahal kalau salah:
masuk lewat jalur "cocok/tidak" (jari siapa pun yang terdaftar), sidik jari yang tetap menyala sesudah penanda hangus, intip uang yang tidak tertutup
sendiri / terbuka untuk akun yang tidak ditandai owner, dan jejak yang tidak menyebut jari.

Yang dipegang:
  · orang yang dibuka jari = orang pembuka Ringkas (ringkasOrang); nyala hanya untuk orang itu, akun tablet yang sama, belum hangus
  · lama intip = setelan owner 15–600 detik (bawaan 60), tertutup tepat pada batasnya; intip hanya untuk orang LAIN yang jaga + akun tablet bacaUang
  · hangus → tandai + pesan otomatis ke owner sekali (bentuk rules v13 stafKirimPesan, lolos penjaga kiriman)
  · jejak kiriman bertanda "sidik jari" & terbaca di Jejak pencatat
  · app.js: masuk / intip / nyalakan lewat sidikJariKunci (bukan sidikJariUji), nyalakan gagal = penanda dihapus, hangus / tidak ada = mati,
    intip tertutup sendiri (interval, tirai, ganti orang), data uang ikut intip; Menu: kartu nyalakan / matikan, tombol intip, setelan owner

    python3 alat-uji/uji_sidik_tablet.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_sidik_tablet.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json, copy, subprocess, tempfile

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru as UB  # noqa: E402
JSC = UB.JSC
SJL = 'baru/js/layar/sidik-logika.js'; SL = 'baru/js/layar/sistem-logika.js'; AK = 'baru/js/data/akses.js'
APP = 'baru/js/app.js'; MN = 'baru/js/layar/menu.js'; RTP = 'baru/js/layar/ringkas-tablet-panel.js'; IDX = 'baru/index.html'
MODUL = list(dict.fromkeys(UB.MODUL + ['baru/js/data/hemat-baca.js', 'baru/js/layar/titipan-logika.js', AK, SL, SJL]))
STATIS = [APP, MN, RTP, IDX]


def kotak():
    K = copy.deepcopy(UB.KOTAK)
    pin = {'peran': 'ben', 'aktif': True, 'garam': 'g' + '0' * 32, 'acak': 'a' * 64, 'iterasi': 100000}   # bentuk PIN sah (ssBersihkanOrangTablet) — PIN tidak diuji di sini
    K['aturanToko'] = [{'id': 'peran', 'operator': {'oown1': dict(pin, nama='Owner'), 'oben1': dict(pin, nama='Ben')}, 'ringkasOrang': 'oown1'}]
    K['aksesAkun'] = [{'id': 'uid-tablet', 'uid': 'uid-tablet', 'nama': 'Tablet', 'email': 'tablet@contoh.com', 'peran': 'ben', 'aktif': True, 'bacaUang': True}]
    return K


SKENARIO = r"""
var hasil = []; var J = JSON.stringify;
function cek(nama, ok, ket) { hasil.push({ nama: nama, ok: !!ok, ket: ket === undefined ? '' : (typeof ket === 'string' ? ket : J(ket)) }); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var _id = 0; var W = { tanggal: '2026-09-19', jam: '21:00', kini: '2026-09-19T14:00:00.000Z', idUnik: function () { return 'sj' + (++_id); } };
var ASLI = { jenis: 'aktif', peran: 'ben', nama: 'Tablet', uid: 'uid-tablet', bacaUang: true };
var OWN = { jenis: 'aktif', peran: 'ben', nama: 'Owner', uid: 'uid-tablet', operatorId: 'oown1', bacaUang: true };
var BEN = { jenis: 'aktif', peran: 'ben', nama: 'Ben', uid: 'uid-tablet', operatorId: 'oben1', bacaUang: true };
var aturPeran = function (ubah) { var a = cacheMentah('aturan').filter(function (d) { return d.id !== 'peran'; }); pasok('aturanToko', a.concat([Object.assign({}, KOTAK.aturanToko[0], ubah || {})])); };

cek('orang yang dibuka jari = orang pembuka Ringkas (ringkasOrang)', sjOrang() === 'oown1');
cek('lama intip bawaan 60 detik; setelan owner 120 dipakai; di luar 15–600 = bawaan', (function () { var a = sjIntipDetik(); aturPeran({ intipDetik: 120 }); var b = sjIntipDetik(); aturPeran({ intipDetik: 5 }); var c = sjIntipDetik(); aturPeran(); return a === 60 && b === 120 && c === 60; })());
var A5 = susunAturSistem('peran', { intipDetik: 5 }, W); var A120 = susunAturSistem('peran', { intipDetik: 120 }, W);
cek('setelan owner: lama intip 5 detik ditolak, 120 tersimpan di aturanToko/peran', !!A5.tolak && /intipDetik/.test(A5.tolak) && A120.dokumen && A120.dokumen[0].data.intipDetik === 120, [A5.tolak, A120.dokumen && A120.dokumen[0].data.intipDetik]);

var N = sjSusunNyala(OWN, ASLI, W); var L = N.lokal;
cek('nyalakan: hanya orang pilihan owner yang sedang jaga → simpanan {orang, akun tablet}', L && L.orang === 'oown1' && L.uid === 'uid-tablet' && L.hangus === false && !!sjSusunNyala(BEN, ASLI, W).tolak, N);
cek('nyalakan ditolak bila owner belum memilih orang pembuka Ringkas', (function () { aturPeran({ ringkasOrang: '' }); var r = sjSusunNyala(OWN, ASLI, W); aturPeran(); return !!r.tolak; })());
cek('menyala: akun tablet sama, orang sama, belum hangus; akun lain / hangus / orang pilihan berganti = mati',
  sjNyala(L, ASLI) && !sjNyala(L, Object.assign({}, ASLI, { uid: 'uid-lain' })) && !sjNyala(sjTandaiHangus(L, W), ASLI) && (function () { aturPeran({ ringkasOrang: 'oben1' }); var x = sjNyala(L, ASLI); aturPeran(); return !x; })());
cek('tombol jari hanya untuk orang itu (aktif); Ben tidak', sjBolehMasuk({ id: 'oown1', aktif: true }, L, ASLI) && !sjBolehMasuk({ id: 'oben1', aktif: true }, L, ASLI) && !sjBolehMasuk({ id: 'oown1', aktif: false }, L, ASLI) && !sjBolehMasuk({ id: 'oown1', aktif: true }, null, ASLI));
cek('intip uang: hanya saat ORANG LAIN jaga, akun tablet ditandai membaca uang, sidik jari menyala',
  sjBolehIntip(BEN, L, ASLI) && !sjBolehIntip(OWN, L, ASLI) && !sjBolehIntip(BEN, L, Object.assign({}, ASLI, { bacaUang: false })) && !sjBolehIntip(BEN, sjTandaiHangus(L, W), ASLI) && !sjBolehIntip(BEN, null, ASLI));
cek('intip tertutup tepat pada batasnya (60 dtk): 59,999 dtk masih, 60 dtk tutup', !sjHarusTutupIntip(0, 59999, 60) && sjHarusTutupIntip(0, 60000, 60) && sjHarusTutupIntip(1000, 31000, 30));
var H = sjTandaiHangus(L, W);
cek('hangus: tandai + perlu kabar; sesudah dikabarkan tidak dikirim lagi', H.hangus === true && H.dikabarkan === false && sjPerluKabar(H) && !sjPerluKabar(Object.assign({}, H, { dikabarkan: true })) && !sjPerluKabar(L));
var KB = sjDokKabarHangus(H, BEN, W);
cek('kabar hangus = pesan otomatis ke owner (bentuk rules v13: menunggu, atas nama akun tablet, ≤ 500 huruf)', KB.koleksi === 'persetujuan' && KB.data.tindakan === 'pesan' && KB.data.status === 'menunggu' && KB.data.mintaUid === 'uid-tablet'
  && KB.data.dari === 'Tablet · otomatis' && KB.data.teks.length <= 500 && /ada jari baru didaftarkan/.test(KB.data.teks), KB.data);
cek('kabar hangus lolos penjaga kiriman akun tablet', !periksaKiriman(BEN, [{ koleksi: 'persetujuan', data: KB.data, ada: false }], [], { hitungLaci: 'sendiri', uangKeluar: 'owner' }).tolak);
cek('keadaan kartu: aplikasi lama = tidak · menyala · hangus · mati', sjKeadaan(L, ASLI, 'oown1', false).st === 'tidak' && sjKeadaan(L, ASLI, 'oown1', true).st === 'nyala' && sjKeadaan(H, ASLI, 'oown1', true).st === 'hangus' && sjKeadaan(null, ASLI, 'oown1', true).st === 'mati');
var JS = jejakKiriman(Object.assign({}, OWN, { lewat: SJ_LEWAT }), [{ koleksi: 'penjualan', data: { id: 'n1' } }], { idJejak: 'j1', kini: W.kini, perangkat: 'Tablet' });
var JP = jejakKiriman(OWN, [{ koleksi: 'penjualan', data: { id: 'n1' } }], { idJejak: 'j2', kini: W.kini, perangkat: 'Tablet' });
cek('jejak kiriman lewat jari bertanda "sidik jari"; lewat PIN tanpa tanda', JS.lewat === 'sidik jari' && !('lewat' in JP), [JS.lewat, JP]);
pasok('logAktivitas', [Object.assign({}, JS), Object.assign({}, JP)]);
var JJ = ssJejak(new Date('2026-09-19T21:05:00'), [], '');
cek('Jejak pencatat menyebut "[sidik jari]" pada kiriman lewat jari', JJ.tampil.some(function (x) { return x.id === 'j1' && /^\[sidik jari\] /.test(x.teks); }) && JJ.tampil.some(function (x) { return x.id === 'j2' && !/sidik jari/.test(x.teks); }), JJ.tampil.map(function (x) { return x.teks; }));
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


def blok(teks, awal):
    i = teks.find(awal)
    if i < 0: return ''
    j = teks.find('\n}\n', i); return teks[i:j + 2] if j > 0 else teks[i:]


def periksa_statis(t):
    c = []; ok = lambda n, x, k='': c.append({'nama': 'statis: ' + n, 'ok': bool(x), 'ket': k})
    A = t[APP]; M = t[MN]
    ms = blok(A, 'async function masukSidik() {')
    ok('masuk lewat jari = KUNCI PENANDA (sidikJariKunci), bukan "cocok/tidak" (sidikJariUji); hanya bila sjBolehMasuk',
       'await sidikJariKunci();' in ms and 'sidikJariUji' not in A and 'SJ.sjBolehMasuk(op, sjLokal(), akunAsli())' in ms, ms[:300])
    ok('masuk lewat jari: hangus = sidik jari mati + kabar; penanda hilang = mati tanpa kabar; sukses = jalur PIN yang sama (lanjutMasuk)',
       "sjMatiHangus(e.code === 'BIOMETRIK_HANGUS')" in ms and 'lanjutMasuk(op, true);' in ms and 'lanjutMasuk(op, false);' in A)
    ok('tombol jari di panel PIN hanya bila aplikasi punya penanda & orang itu boleh', "sb.hidden = !(_sjAda && SJ.sjBolehMasuk(op, sjLokal(), akunAsli()));" in A and "if (ev.target.closest && ev.target.closest('[data-sidik]')) masukSidik();" in A)
    ok('masuk lewat jari ditandai: _jaga.sidik → akun efektif lewat "sidik jari"', "_jaga = { id: op.id, uid: (akunAsli() || {}).uid || '', sidik: !!sidik };" in A and 'Object.assign(TB.tbEfektif(a, op), { lewat: SJ.SJ_LEWAT })' in A
       and "mulaiJaga(_tanyaGanti.op, _tanyaGanti.sidik)" in A)
    ny = A[A.find('  async nyalakan() {'):A.find('  async matikan() {')]
    ok('nyalakan = pasang penanda lalu tempel jari lewat kunci; gagal / batal = penanda dihapus, tetap mati', 'await penandaPasang(); await sidikJariKunci();' in ny and 'await penandaHapus();' in ny and 'sjSimpan(r.lokal);' in ny and ny.index('sjSimpan(r.lokal)') > ny.index('await sidikJariKunci()'))
    mi = A[A.find('  async mintaIntip() {'):A.find('// Menu (putaran 14)')]
    ok('intip = sjBolehIntip + tempel jari lewat kunci; hangus = mati + kabar', 'SJ.sjBolehIntip(akunKini(), sjLokal(), akunAsli())' in mi and 'await sidikJariKunci();' in mi and "sjMatiHangus(e.code === 'BIOMETRIK_HANGUS')" in mi and '_intip = true;' in mi)
    ok('intip tertutup sendiri: interval sjHarusTutupIntip(sentuh, kini, setelan owner), tirai / pindah aplikasi, ganti orang',
       'setInterval(() => { if (_intip && SJ.sjHarusTutupIntip(_sentuh, Date.now(), SJ.sjIntipDetik())) tutupIntip(); }, 5000);' in A
       and 'if (document.hidden && _intip) tutupIntip();' in A and "pesanOrang(''); _intip = false;" in A and "_sentuh = Date.now(); _intip = false;" in A)
    ok('data uang ikut intip & dinilai ulang tiap kali (orang berganti / sidik jari mati = tertutup)', 'fb.setelDataUang(rtBukaUang(akunKini()) || intipAktif())' in A and 'function intipAktif() { return _intip && SJ.sjBolehIntip(akunKini(), sjLokal(), akunAsli()); }' in A)
    ok('saat mulai & tiap ±1 menit di panel PIN: penanda dicek (hangus / hilang = mati)', 'if (asliAda()) penandaCek().then((r) => {' in A and 'if (_sjAda && Date.now() - _sjCekPada > 60000) cekPenandaDiam();' in A)
    ok('kabar hangus dikirim begitu ada orang jaga (sekali, ditandai sesudah terkirim)', 'setTimeout(kirimKabarHangus, 0);' in A and 'dikabarkan: true' in A and 'if (!ef || !bisaBekerja(ef) || !ef.operatorId) return;' in A)
    ok('Tahap B tidak ada: kode sidik jari tidak masuk akun owner & tidak memutus persetujuan', not re.search(r'signIn|tpSusunPutus|susunPutusPersetujuan|hlTerapkan', t[SJL] + ny + mi))
    ok('Menu tablet: kartu nyalakan / matikan (orang pilihan owner), tombol intip & tutup intip (orang lain), kartu Ringkas ikut intip',
       '${kartuSidik(s, akunM)}' in M and 'data-aksi="sjNyalakan"' in M and 'data-aksi="sjMatikan"' in M and 'data-aksi="sjIntip"' in M and 'data-aksi="sjTutupIntip"' in M
       and '${RT.rtTampil(akunM) || intipNyala() ? kartuRingkas(' in M and 'sidik: sidikMenu' in A)
    ok('Menu owner: lama intip diatur owner (aturanToko/peran.intipDetik)', "rtIntip: ({ d }) => tulis(S.susunAturSistem('peran', { intipDetik: Number(d) }, waktu()))" in M and 'data-aksi="rtIntip"' in M)
    ok('kartu Ringkas berjudul intip saat dibuka jari', "o.intip ? 'Intip uang · sidik jari owner · '" in t[RTP])
    ok('index.html memuat sidik-logika (modulepreload)', '<link rel="modulepreload" href="js/layar/sidik-logika.js">' in t[IDX])
    return c


def periksa(t, diam=False):
    c = jalankan(t) + periksa_statis(t)
    g = [x for x in c if not x['ok']]
    if not diam:
        for x in c: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:700]))
        print('SIDIK JARI OWNER DI TABLET: %d lulus · %d gagal' % (len(c) - len(g), len(g)))
    return g


def main():
    t = baca_semua()
    if '--kontrol' in sys.argv:
        S = t[SJL]; A = t[APP]; K = t[AK]; L = t[SL]; M = t[MN]
        rusak = [
            ('masuk lewat jari memakai "cocok/tidak" (jari siapa pun)', APP, A.replace("  try { await sidikJariKunci(); }\n  catch (e) {\n    _periksaPin = false;", "  try { await sidikJariUji(); }\n  catch (e) {\n    _periksaPin = false;")),
            ('sidik jari tetap menyala sesudah hangus', SJL, S.replace("return !!lokal && !lokal.hangus && !!akun", "return !!lokal && !!akun")),
            ('tombol jari untuk siapa saja', SJL, S.replace(" && String(op.id) === String(lokal.orang);", ";")),
            ('intip juga untuk owner sendiri', SJL, S.replace(" && String(efektif.operatorId) !== String(lokal.orang)", "")),
            ('intip tanpa tanda baca uang owner', SJL, S.replace(" && !!akunAsli && akunAsli.bacaUang === true;", ";")),
            ('intip tidak pernah tertutup', SJL, S.replace("export const sjHarusTutupIntip = (sentuh, kini, detik) => (Number(kini) || 0)", "export const sjHarusTutupIntip = (sentuh, kini, detik) => false && (Number(kini) || 0)")),
            ('lama intip mengabaikan setelan owner', SJL, S.replace("? Math.round(n) : SJ_INTIP_BAWAAN;", "? SJ_INTIP_BAWAAN : SJ_INTIP_BAWAAN;")),
            ('kabar hangus bukan pesan (tidak sampai owner)', SJL, S.replace("tindakan: 'pesan', status: 'menunggu', teks,", "tindakan: 'kabarSidik', status: 'menunggu', teks,")),
            ('kabar hangus terkirim berulang', SJL, S.replace("lokal.hangus === true && lokal.dikabarkan !== true;", "lokal.hangus === true;")),
            ('jejak tanpa tanda sidik jari', AK, K.replace("    ...(akun.lewat ? { lewat: String(akun.lewat) } : {}) };", "  };")),
            ('Jejak pencatat tidak menyebut sidik jari', SL, L.replace("teks: (l.lewat ? '[' + String(l.lewat) + '] ' : '') + (l.aksi", "teks: (l.aksi")),
            ('lama intip owner tanpa batas', SL, L.replace(" || angka('intipDetik', 15, 600, 'detik');", ";")),
            ('intip tidak tertutup sendiri (interval dicabut)', APP, A.replace("setInterval(() => { if (_intip && SJ.sjHarusTutupIntip(_sentuh, Date.now(), SJ.sjIntipDetik())) tutupIntip(); }, 5000);", "")),
            ('nyalakan gagal meninggalkan penanda', APP, A.replace("const t = penandaTolak(e); try { await penandaHapus(); } catch (x) { /* tidak ada yang perlu dihapus */ }", "const t = penandaTolak(e);")),
            ('masuk lewat jari tidak mematikan sidik jari saat hangus', APP, A.replace("if (e && (e.code === 'BIOMETRIK_HANGUS' || e.code === 'PENANDA_TIDAK_ADA')) { sjMatiHangus(e.code === 'BIOMETRIK_HANGUS'); pesanOrang(", "if (false) { pesanOrang(")),
            ('data uang tidak ikut intip', APP, A.replace("fb.setelDataUang(rtBukaUang(akunKini()) || intipAktif())", "fb.setelDataUang(rtBukaUang(akunKini()))")),
        ]
        kode = 0
        for nama, berkas, isi in rusak:
            if isi == t[berkas]: print('KONTROL BASI  ' + nama); kode = 3; continue
            t2 = dict(t); t2[berkas] = isi; g = periksa(t2, diam=True)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + (' → ' + g[0]['nama'][:100] if g else ''))
            if not g: kode = 3
        print('KONTROL: %d kerusakan' % len(rusak)); sys.exit(kode)
    sys.exit(1 if periksa(t) else 0)


if __name__ == '__main__':
    main()
