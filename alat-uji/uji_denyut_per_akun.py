#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_denyut_per_akun.py — audit 39b no. 23: denyut /baru/ di perangkat yang dipakai BERGILIRAN (jsc, TANPA peramban).

Yang dijalankan sungguhan (bukan dibaca sumbernya):
  · baru/js/data/firebase.js kirimDenyut() — dibundel dengan pengganti Firebase SDK (doc/setDoc palsu);
  · rules ASLI: kondisi `allow create, update, delete` blok perangkatStatus + fungsi stafDenyut/owner/kasir/masuk diambil
    APA ADANYA dari firestore.rules dan dinilai di jsc (hanya get(aksesAkun) & `in` daftar yang diterjemahkan tangan);
  · layar owner: SS1 ssPerangkat (sistem-logika.js), daftar periksa kunci bulan + "sudah tidak dipakai" (kunci-periode-logika.js),
    gerbang tutup buku g3 (tutup-buku-logika.js).
KOTAK PASIR saja (akun, uid, nama CONTOH — bukan orang toko). Denyut tidak ikut berkas cadangan, jadi tidak ada asap data toko.

    python3 alat-uji/uji_denyut_per_akun.py            → N lulus · 0 gagal
    python3 alat-uji/uji_denyut_per_akun.py --kontrol  → denyut / rules yang dirusak wajib ketahuan
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_kunci_periode  # noqa: E402
import periksa_rules  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
_M = uji_kunci_periode.MODUL + ['baru/js/layar/pelanggan-logika.js', 'baru/js/layar/bon-logika.js', 'baru/js/layar/bon-pemasok-logika.js', 'baru/js/data/akses.js',
                                'baru/js/layar/sistem-logika.js', 'baru/js/data/antre-lokal.js', 'baru/js/data/katalog-kasir.js', 'baru/js/data/hemat-baca.js', 'baru/js/data/firebase.js']   # hemat-baca SEBELUM firebase (owner 7 Okt: konstanta dipakai saat modul firebase dimuat)
MODUL = [m for i, m in enumerate(_M) if m not in _M[:i]]

JAM = ("var __RealDate = Date; var __KINI = new __RealDate('2026-10-01T08:00:00+07:00').getTime();\n"
       "Date = function (a, b, c, d, e, f, g) { if (!(this instanceof Date)) return new __RealDate(__KINI).toString(); if (arguments.length === 0) return new __RealDate(__KINI); if (arguments.length === 1) return new __RealDate(a); return new __RealDate(a, b, c === undefined ? 1 : c, d || 0, e || 0, f || 0, g || 0); };\n"
       "Date.prototype = __RealDate.prototype; Date.now = function () { return __KINI; }; Date.UTC = __RealDate.UTC; Date.parse = __RealDate.parse;\n")

# pengganti Firebase SDK: hanya doc/setDoc yang dipakai kirimDenyut; sisanya tidak pernah dipanggil di uji ini (mulai() tidak dijalankan)
SDK = r"""
var __gudang = { perangkatStatus: {} }, __catat = [], __sesi = { uid: '' };
function __diam() { throw new Error('SDK palsu: tidak dipakai di uji ini'); }
var initializeApp = __diam, initializeFirestore = __diam, persistentLocalCache = __diam, persistentMultipleTabManager = __diam, collection = __diam, onSnapshot = __diam,
  writeBatch = __diam, query = __diam, orderBy = __diam, limit = __diam, where = __diam, getDocs = __diam, waitForPendingWrites = __diam, getAuth = __diam,
  signInWithEmailAndPassword = __diam, onAuthStateChanged = __diam, setPersistence = __diam, browserLocalPersistence = {}, signOut = __diam;
// hemat baca (owner 7 Okt 2026): permukaan SDK baru yang diimpor firebase.js — serverTimestamp dipakai denyut OWNER (capServer = jam server), sisanya tidak di uji ini
var getDocsFromServer = __diam, getCountFromServer = __diam, terminate = __diam, CACHE_SIZE_UNLIMITED = -1, Timestamp = { fromMillis: __diam };
function serverTimestamp() { return { __capServerPalsu: true }; }
function doc(db, kol, id) { return { kol: kol, id: String(id) }; }
function setDoc(ref, data) {
  var ada = !!(__gudang[ref.kol] || {})[ref.id];
  var izin = __izin(ada ? 'update' : 'create', ref.kol, ref.id, data, __sesi.uid);
  __catat.push({ kol: ref.kol, id: ref.id, izin: izin, oleh: __sesi.uid, op: ada ? 'update' : 'create' });
  if (izin) { (__gudang[ref.kol] = __gudang[ref.kol] || {})[ref.id] = JSON.parse(JSON.stringify(data)); return Promise.resolve(); }
  return Promise.reject({ code: 'permission-denied' });
}
"""


def aturan_js(rules):
    """Kondisi allow perangkatStatus + fungsi rules yang dipakainya, APA ADANYA dari firestore.rules → satu fungsi JS __izin."""
    R = periksa_rules.tanpa_komentar(rules)
    blok = periksa_rules.blok_rules(R)['perangkatStatus']; F = periksa_rules.fungsi_rules(R)
    kond = {op: [re.sub(r'^\s*if\s+', '', x) for x in periksa_rules.allow(blok, op)] for op in ('create', 'update', 'delete')}
    for op, k in kond.items():
        assert len(k) == 1, 'perangkatStatus: allow %s tidak tunggal — perbarui alat uji' % op
        sisa = re.sub(r"\b(owner|kasir|stafDenyut)\(\[?[^)]*\]?\)", '', k[0])
        assert re.fullmatch(r'[\s|&()!]*', sisa), 'perangkatStatus: kondisi %s memakai fungsi yang belum diterjemahkan: %r' % (op, k[0])
    for f in ('masuk', 'owner', 'kasir', 'stafDenyut'):
        assert 'get(/' not in F[f] and 'exists(' not in F[f] and ' in ' not in F[f] and 'let ' not in F[f], 'fungsi %s memakai bentuk rules yang tidak diterjemahkan' % f
    return ("function __bungkus(d) { var o = {}; Object.keys(d).forEach(function (k) { o[k] = d[k]; });\n"
            "  Object.defineProperty(o, 'get', { value: function (k, b) { return Object.prototype.hasOwnProperty.call(d, k) ? d[k] : b; } });\n"
            "  Object.defineProperty(o, 'keys', { value: function () { var ks = Object.keys(d); return { hasOnly: function (z) { return ks.every(function (x) { return z.indexOf(x) >= 0; }); } }; } }); return o; }\n"
            "function __izin(op, kol, id, dataBaru, uid) {\n"
            "  if (kol !== 'perangkatStatus') throw new Error('uji ini hanya menilai perangkatStatus');\n"
            "  var lama = (__gudang[kol] || {})[id] || null;\n"
            "  var request = { auth: uid ? { uid: uid, token: { email: EMAIL[uid] } } : null, resource: dataBaru ? { data: __bungkus(dataBaru) } : null };\n"
            "  var resource = lama ? { data: __bungkus(lama) } : null;\n"
            "  function masuk() {" + F['masuk'] + "}\n"
            "  function owner() {" + F['owner'] + "}\n"
            "  function kasir() {" + F['kasir'] + "}\n"
            "  function akun() { var a = AKSES[request.auth.uid]; if (!a) throw new Error('get() aksesAkun tidak ada → ditolak'); return __bungkus(a); }\n"
            "  function aktifDengan(a, peranBoleh) { return a.aktif == true && peranBoleh.indexOf(a.peran) >= 0; }\n"
            "  function stafDenyut(peranBoleh) {" + F['stafDenyut'] + "}\n"
            "  try {\n"
            "    if (op === 'create') return !!(" + kond['create'][0] + ");\n"
            "    if (op === 'update') return !!(" + kond['update'][0] + ");\n"
            "    if (op === 'delete') return !!(" + kond['delete'][0] + ");\n"
            "  } catch (e) { return false; }\n"
            "  throw new Error('op? ' + op);\n"
            "}\n")


SKENARIO = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
function J(x) { return JSON.stringify(x); }
function pada(iso) { __KINI = new __RealDate(iso).getTime(); }
function kini() { return new Date(Date.now()); }
var EMAIL = { 'uid-owner': 'owner@tokoberasmiqbal.web.app', 'uid-ben': 'ben.contoh@tokoberasmiqbal.web.app', 'uid-kry': 'kry.contoh@tokoberasmiqbal.web.app' };
var AKSES = { 'uid-ben': { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true }, 'uid-kry': { uid: 'uid-kry', nama: 'Karyawan Contoh', peran: 'karyawan', aktif: true } };
// tiap perangkat = isi localStorage-nya sendiri (kunci SAMA dengan peramban: miqbal_perangkat_v1 / _label_v1)
var LS = { tablet: { miqbal_perangkat_v1: 'p-tablet-uji', miqbal_perangkat_label_v1: 'Tablet uji' }, tablet2: { miqbal_perangkat_v1: 'p-tablet2-uji', miqbal_perangkat_label_v1: 'Tablet dua' },
  mac: { miqbal_perangkat_v1: 'p-mac-uji', miqbal_perangkat_label_v1: 'Mac owner' } };
db = { palsu: true };
function masukDi(perangkat, uid, nAntre) {
  __ls = LS[perangkat]; __sesi.uid = uid;
  status.akun = keadaanAkun(EMAIL[uid], uid, AKSES[uid] || null); status.masuk = bisaBekerja(status.akun); auth = { currentUser: { email: EMAIL[uid], uid: uid } };
  status.antre = []; for (var i = 0; i < (nAntre || 0); i++) status.antre.push({ koleksi: 'penjualan', id: 'q' + uid + i });
}
// denyut dari layar (paksa = sama dengan setelLokasi/namaiPerangkat) → keputusan rules untuk tulisan itu
function denyut() { var n = __catat.length; var lempar = null; try { kirimDenyut(true); } catch (e) { lempar = String(e); } var c = __catat[n] || null; return { izin: !!(c && c.izin), id: c ? c.id : null, lempar: lempar }; }
function ownerLihat() { pasok('perangkatStatus', Object.keys(__gudang.perangkatStatus).map(function (k) { return __gudang.perangkatStatus[k]; })); }
function baris(P, pemegang, nama) { return P.daftar.filter(function (d) { return d.pemegang === pemegang && (!nama || d.nama === nama); }); }
function lupakan(id) {
  var r = susunLupakanPerangkat(id, true); if (r.tolak) return r;
  r.hapus.forEach(function (h) { if (__izin('delete', h.koleksi, h.id, null, 'uid-owner')) delete __gudang[h.koleksi][h.id]; });
  ownerLihat(); return r;
}
var BERSIH = { lokal: { antreLokal: { belum: [], ditolak: [] }, antre: [] }, parkir: [], putusanHari: {}, centang: {}, siap25b: true };
var butir = function (D, id) { return D.butir.find(function (b) { return b.id === id; }); };

// ---- 1 · owner di Mac-nya: id dokumen = id perangkat (tidak berubah) → SS1 "perangkat ini" & gerbang tutup buku tetap mengenalinya
pada('2026-10-01T08:00:00+07:00'); masukDi('mac', 'uid-owner', 0); var dM = denyut();
ownerLihat(); var P0 = ssPerangkat(kini(), [], 'p-mac-uji');
ok('owner: denyut Mac diterima, dokumennya tetap perangkatStatus/{id perangkat}; SS1 menandai baris itu "perangkat ini"',
  dM.izin && dM.id === 'p-mac-uji' && P0.daftar.length === 1 && P0.daftar[0].ini && P0.daftar[0].nama === 'Mac owner', J(dM) + ' ' + J(P0.daftar));

// ---- 2 · tablet dipakai BERGILIRAN: Ben dulu (catatan offline tertahan saat keluar), lalu karyawan
pada('2026-10-01T08:05:00+07:00'); masukDi('tablet', 'uid-ben', 0); var dB1 = denyut();
pada('2026-10-01T12:00:00+07:00'); masukDi('tablet', 'uid-ben', 2); var dB2 = denyut();   // Ben keluar dengan 2 catatan belum terkirim ("Keluar tetap?" → ya)
pada('2026-10-01T12:05:00+07:00'); masukDi('tablet', 'uid-kry', 0); var dK1 = denyut();   // antrean Firestore per akun: punya karyawan kosong
pada('2026-10-01T12:10:00+07:00'); var dK2 = denyut();
ok('Ben (akun pertama di tablet): denyutnya diterima', dB1.izin && dB2.izin && !dB1.lempar, J([dB1, dB2]));
ok('karyawan masuk di tablet yang sama sesudah Ben: denyutnya DITERIMA server (rules apa adanya, tanpa terbit ulang)', dK1.izin && dK2.izin && !dK1.lempar, J([dK1, dK2, __catat.slice(-2)]));
ownerLihat(); var P1 = ssPerangkat(kini(), [], 'p-mac-uji');
var kryT = baris(P1, 'Karyawan Contoh', 'Tablet uji'), benT = baris(P1, 'Ben Contoh', 'Tablet uji');
ok('SS1 owner: tablet tampil "dipegang Karyawan Contoh", denyut barusan, akun karyawan', kryT.length === 1 && kryT[0].menitLalu === 0 && kryT[0].akun === EMAIL['uid-kry'] && kryT[0].hidup, J(P1.daftar));
ok('SS1 owner: 2 catatan Ben yang tertahan di tablet TETAP terlihat sesudah karyawan berdenyut (tidak ditimpa angka 0 karyawan)', benT.length === 1 && benT[0].antrean === 2 && P1.lainAntre === 2, J(P1.daftar));
ok('SS1 owner: baris tiap akun punya id sendiri (tidak ada dua baris ber-id sama) dan tidak ada yang mengaku "perangkat ini" selain Mac', P1.daftar.length === 3 && new Set(P1.daftar.map(function (d) { return d.id; })).size === 3 && P1.daftar.filter(function (d) { return d.ini; }).length === 1, J(P1.daftar));

// ---- 3 · penjaga rules masih berbunyi: bukan-owner tidak bisa menimpa dokumen denyut milik akun lain
var tiru = Object.assign({}, __gudang.perangkatStatus[benT.length ? benT[0].id : 'p-tablet-uji'], { akunUid: 'uid-kry', pemegang: 'Karyawan Contoh', antrean: 0 });
__sesi.uid = 'uid-kry'; var tolakTiru = !__izin('update', 'perangkatStatus', benT.length ? benT[0].id : 'p-tablet-uji', tiru, 'uid-kry');
ok('rules: karyawan TIDAK bisa menimpa dokumen denyut Ben (angka antrean Ben tidak bisa di-nol-kan akun lain)', tolakTiru);

// ---- 4 · kunci bulan sehari kemudian: Ben belum masuk lagi, karyawan tetap memakai tablet
pada('2026-10-02T12:30:00+07:00'); masukDi('tablet', 'uid-kry', 0); var dK3 = denyut(); masukDi('mac', 'uid-owner', 0); denyut(); ownerLihat();
var D1 = kpDaftarPeriksa('2026-09', kini(), JSON.parse(J(BERSIH)));
var diam = butir(D1, 'perangkatDenyut'), antreB = butir(D1, 'perangkatAntre');
ok('kunci bulan: tablet yang SEDANG dipakai karyawan tidak dicap "tanpa denyut 24 jam"; yang dicap = baris Ben di tablet itu, namanya disebut', dK3.izin && diam.rincian.length === 1 && /^Tablet uji \(Ben Contoh\) · terakhir 1 Okt/.test(diam.rincian[0]) && baris(ssPerangkat(kini(), [], 'p-mac-uji'), 'Karyawan Contoh', 'Tablet uji').length === 1
  && baris(ssPerangkat(kini(), [], 'p-mac-uji'), 'Karyawan Contoh', 'Tablet uji')[0].menitLalu === 0, J(diam) + ' ' + J(dK3));
ok('kunci bulan: catatan Ben yang tertahan di tablet tetap memblokir (memang belum sampai server), menyebut Ben', !antreB.ok && antreB.rincian.length === 1 && /^Tablet uji \(Ben Contoh\) · 2 antre/.test(antreB.rincian[0]), J(antreB));
var benId = benT.length ? benT[0].id : 'p-tablet-uji';
var tolakBen = lupakan(benId).tolak || '';
ok('"sudah tidak dipakai" untuk baris Ben ditolak selama 2 catatannya tertahan; kalimatnya menyebut SIAPA yang harus masuk & mengirim', /^Tablet uji \(Ben Contoh\) terakhir melaporkan 2 antrean .*kirim dulu/.test(tolakBen), tolakBen);

// ---- 5 · Ben masuk lagi → catatannya terkirim, denyutnya tercatat; karyawan tetap berdenyut sesudahnya (tidak ada akun yang terkunci)
pada('2026-10-02T13:00:00+07:00'); masukDi('tablet', 'uid-ben', 0); var dB3 = denyut();
pada('2026-10-02T17:00:00+07:00'); masukDi('tablet', 'uid-kry', 0); var dK4 = denyut(); ownerLihat();
var D2 = kpDaftarPeriksa('2026-09', kini(), JSON.parse(J(BERSIH)));
ok('Ben masuk lagi di tablet: denyutnya diterima, antreannya jadi 0 → butir antrean kunci bulan beres', dB3.izin && butir(D2, 'perangkatAntre').ok, J(dB3) + ' ' + J(butir(D2, 'perangkatAntre')));
ok('karyawan masuk lagi sesudah Ben: denyutnya tetap diterima (giliran ke-3, ke-4 … tidak terkunci)', dK4.izin, J(dK4));

// ---- 6 · "sudah tidak dipakai" tidak buntu: baris Ben yang diam dilupakan → hilang TEPAT baris itu; Ben masuk lagi kapan pun → tercatat ulang
pada('2026-10-04T09:00:00+07:00'); masukDi('tablet', 'uid-kry', 0); denyut(); masukDi('mac', 'uid-owner', 0); denyut(); ownerLihat();
var D3 = kpDaftarPeriksa('2026-09', kini(), JSON.parse(J(BERSIH))); var aksiBen = butir(D3, 'perangkatDenyut').aksi.filter(function (a) { return a.id === benId; });
var rL = aksiBen.length ? lupakan(benId) : { tolak: 'tidak ditawarkan' }; var P3 = ssPerangkat(kini(), [], 'p-mac-uji');
ok('kunci bulan: baris Ben yang diam (antrean 0) ditawarkan "sudah tidak dipakai"; dilupakan → baris Ben hilang, baris karyawan & Mac tetap',
  aksiBen.length === 1 && aksiBen[0].label === 'Tablet uji (Ben Contoh) sudah tidak dipakai' && !rL.tolak && !baris(P3, 'Ben Contoh').length && baris(P3, 'Karyawan Contoh', 'Tablet uji').length === 1 && P3.daftar.some(function (d) { return d.ini; }) && butir(kpDaftarPeriksa('2026-09', kini(), JSON.parse(J(BERSIH))), 'perangkatDenyut').ok,
  J(butir(D3, 'perangkatDenyut')) + ' ' + J(rL) + ' ' + J(P3.daftar));
pada('2026-10-04T10:00:00+07:00'); masukDi('tablet', 'uid-ben', 0); var dB4 = denyut(); pada('2026-10-04T10:30:00+07:00'); masukDi('tablet', 'uid-kry', 0); var dK5 = denyut();
ok('sesudah dilupakan: Ben DAN karyawan sama-sama tetap berdenyut di tablet itu (melupakan tidak memindah kunci ke akun lain)', dB4.izin && dK5.izin, J([dB4, dK5]));

// ---- 7 · tablet yang PERTAMA kali dipegang owner (menamai perangkat) lalu diserahkan ke Ben
pada('2026-10-04T11:00:00+07:00'); masukDi('tablet2', 'uid-owner', 0); var dO2 = denyut();
pada('2026-10-04T11:10:00+07:00'); masukDi('tablet2', 'uid-ben', 0); var dB5 = denyut(); ownerLihat();
ok('tablet yang lebih dulu dipegang owner: denyut Ben di tablet itu tetap DITERIMA; dokumen owner di tablet itu tetap ber-id perangkat',
  dO2.izin && dO2.id === 'p-tablet2-uji' && dB5.izin && baris(ssPerangkat(kini(), [], 'p-mac-uji'), 'Ben Contoh', 'Tablet dua').length === 1, J([dO2, dB5]));

// ---- 8 · gerbang tutup buku (owner di Mac): Mac sendiri bukan "perangkat lain"
var G = gerbangBuku(2026, kini(), { antre: [], menunggu: 0, offline: false, idPerangkat: 'p-mac-uji' }, {});
var g3 = G.daftar.find(function (x) { return x.id === 'g3'; });
ok('tutup buku g3: Mac owner sendiri tidak disebut "perangkat lain"; tablet yang berdenyut 15 menit terakhir disebut', !/Mac owner/.test(g3.ket) && /Tablet/.test(g3.ket), g3.ket);

// ---- 9 · tidak ada denyut akun sah yang ditolak diam-diam sepanjang skenario
var ditolak = __catat.filter(function (c) { return !c.izin; });
ok('sepanjang skenario: NOL denyut akun sah yang ditolak server (dulu ditelan .catch tanpa bekas)', ditolak.length === 0, J(ditolak));
print(J({ lulus: lulus, gagal: gagal, catat: __catat.length }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().split('\n')[-1].startswith('{'): return None, (r.stderr or r.stdout)[:1500]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js, rules):
    h, e = jalan(JAM + SDK + js + '\n' + aturan_js(rules) + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = uji_kunci_periode.satu_lingkup(bundel_baru.bundel(MODUL))
    rules = open(os.path.join(AKAR, 'firestore.rules'), encoding='utf-8').read()
    if '--kontrol' in sys.argv:
        BARIS = "try { const id = idDenyut(); const isi = { id, nama,"   # owner 7 Okt (hemat baca): isi denyut disusun dulu (owner menambah capServer)
        rusak = {
            'denyut kembali satu dokumen per perangkat untuk semua akun (keadaan main 7de3e7a)': (js.replace(
                "const idDenyut = () => (status.akun && status.akun.jenis !== 'owner' ? idPerangkat() + '~' + status.akun.uid : idPerangkat());",
                "const idDenyut = () => idPerangkat();"), rules),
            'id dokumen per akun tapi kolom id tetap id perangkat ("sudah tidak dipakai" menghapus dokumen yang salah)': (js.replace(
                BARIS, "try { const id = idDenyut(); const isi = { id: idPerangkat(), nama,"), rules),
            'owner ikut per akun (SS1 & gerbang tutup buku tidak lagi mengenali perangkat ini)': (js.replace(
                "status.akun && status.akun.jenis !== 'owner' ? idPerangkat() + '~' + status.akun.uid : idPerangkat()",
                "status.akun ? idPerangkat() + '~' + status.akun.uid : idPerangkat()"), rules),
            'jalan pintas di rules: penjaga pemilik dokumen dicabut, denyut tetap satu dokumen per perangkat (antrean Ben tertimpa 0)': (js.replace(
                "const idDenyut = () => (status.akun && status.akun.jenis !== 'owner' ? idPerangkat() + '~' + status.akun.uid : idPerangkat());",
                "const idDenyut = () => idPerangkat();"),
                rules.replace("        && (resource == null || resource.data.get('akunUid', request.auth.uid) == request.auth.uid)\n", "")),
            'nama baris denyut tanpa pemegang (dua baris tablet tak bisa dibedakan di daftar kunci bulan)': (js.replace(
                "const kpNamaDenyut = (p) => (p.nama || p.id) + (p.pemegang ? ' (' + p.pemegang + ')' : '');", "const kpNamaDenyut = (p) => (p.nama || p.id);"), rules),
            'rules: penjaga pemilik dokumen dicabut (akun lain bisa menimpa denyut Ben)': (js,
                rules.replace("        && (resource == null || resource.data.get('akunUid', request.auth.uid) == request.auth.uid)\n", "")),
        }
        kode = 0
        for nama, (isi, ru) in rusak.items():
            if isi == js and ru == rules: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi, ru)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:160] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js, rules)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    sys.exit(1 if g else 0)
