#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_owner_tablet.py — PUTUSAN OWNER DI TABLET, sidik jari Tahap B (owner 23 Nov 2026). jsc + statis, KOTAK PASIR (angka & nama contoh).

Yang dijaga:
  · logika (baru/js/layar/owner-tablet-logika.js, dijalankan ASLI di jsc): yang boleh diputus di tablet = titipan uang keluar, pesan & kabar barang masuk, nego,
    bon lewat batas, usul harga pelanggan; hitungan laci = TOLAK saja (tutup hari tetap di HP/Mac); jenis lain = hanya HP/Mac. Putusan lewat
    susunPutusPersetujuan yang sama dengan HP (uang titipan ikut di kiriman yang sama) + cap diputusDi; menolak butuh alasan; yang sudah diputus ditolak;
    simpanan perangkat (sandi TERKUNCI) dibaca aman; arti tolakan plugin (hangus / kunci berganti = simpanan dibuang);
  · kartu Menu tablet dirender asli: tombol per jenis, yang tidak boleh disebut "di HP/Mac", kolom sandi bertipe password;
  · penulis (firebase.js tulisSebagaiOwner): sesi owner SEMENTARA di app kedua, auth di MEMORI, cache memori, offline ditolak SEBELUM masuk, penjaga bulan
    terkunci, pencatat setelan, jejak bertanda `lewat`, server mengaku (commit) lalu KELUAR di finally;
  · jembatan (app.js ownerTablet): sandi diperiksa ke server SEBELUM dikunci jari; yang disimpan hanya {data, iv, uid, dipasang}; tiap putusan: periksa →
    tempel jari → dihitung ulang → kirim → sandi dibuang; kunci dipasang ulang = Tahap A ditandai mati dulu;
  · Menu: sandi tidak pernah jadi isian / draf.

    python3 alat-uji/uji_owner_tablet.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/uji_owner_tablet.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_uang_baru as UB  # noqa: E402

OWL = 'baru/js/layar/owner-tablet-logika.js'; MN = 'baru/js/layar/menu.js'; FB = 'baru/js/data/firebase.js'; APP = 'baru/js/app.js'; IDX = 'baru/index.html'; PR = 'baru/js/inti/perangkat.js'
# pola uji_menu_baru: sistem-logika butuh akses, nego, wadah-jual (lengkapi() tidak mengikuti impor)
MODUL = list(dict.fromkeys(UB.MODUL + ['baru/js/data/hemat-baca.js', 'baru/js/data/akses.js', 'baru/js/layar/nego-logika.js', 'baru/js/layar/wadah-jual-logika.js',
                                       'baru/js/layar/titipan-logika.js', 'baru/js/layar/sistem-logika.js', OWL]))

KOTAK_TAMBAH = {'persetujuan': [
    {'id': 'tt1', 'tindakan': 'uangKeluar', 'status': 'menunggu', 'jenis': 'toko', 'teks': 'Kantong 5 kg', 'nominal': 25000, 'tanggal': '2026-09-19', 'jam': '10:00', 'dari': 'Penjaga A', 'peran': 'ben', 'mintaUid': 'uid-tablet'},
    {'id': 'ps1', 'tindakan': 'pesan', 'status': 'menunggu', 'teks': 'Beras IR64 tinggal 2 karung', 'tanggal': '2026-09-19', 'jam': '10:05', 'dari': 'Penjaga A', 'peran': 'ben', 'mintaUid': 'uid-tablet'},
    {'id': 'hl1', 'tindakan': 'hitungLaci', 'status': 'menunggu', 'hitung': 500000, 'amankan': 0, 'tanggal': '2026-09-19', 'jam': '21:00', 'dari': 'Penjaga A', 'peran': 'ben', 'mintaUid': 'uid-tablet'},
    {'id': 'x1', 'tindakan': 'hapusNota', 'status': 'menunggu', 'teks': 'hapus nota contoh', 'nominal': 0, 'tanggal': '2026-09-19', 'jam': '10:10', 'dari': 'Penjaga A', 'peran': 'ben', 'mintaUid': 'uid-tablet'},
    {'id': 'old', 'tindakan': 'uangKeluar', 'status': 'disetujui', 'jenis': 'toko', 'teks': 'lama', 'nominal': 1000, 'tanggal': '2026-09-18', 'jam': '10:00', 'dari': 'Penjaga A'}]}

SKENARIO = r"""
var hasil = []; var J = JSON.stringify;
function cek(nama, ok, ket) { hasil.push({ nama: nama, ok: !!ok, ket: ket === undefined ? '' : (typeof ket === 'string' ? ket : J(ket)) }); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var _id = 0; var W = { tanggal: '2026-09-19', jam: '22:00', kini: '2026-09-19T15:00:00.000Z', idUnik: function () { return 'ow' + (++_id); } };
var B = function (t) { return J(owBoleh({ tindakan: t })); };
cek('yang boleh di tablet: titipan uang, nego, bon lewat batas, usul harga = setujui & tolak; pesan & kabar barang = dibaca; hitungan laci = tolak saja; lainnya = tidak',
  B('uangKeluar') === J({ setuju: true, tolak: true, dibaca: false }) && B('nego') === B('uangKeluar') && B('kredit') === B('uangKeluar') && B('hargaPelanggan') === B('uangKeluar')
  && B('pesan') === J({ setuju: false, tolak: false, dibaca: true }) && B('barangMasuk') === B('pesan') && B('hitungLaci') === J({ setuju: false, tolak: true, dibaca: false })
  && B('hapusNota') === J({ setuju: false, tolak: false, dibaca: false }) && B('') === B('hapusNota'));
var D = owDaftar(new Date(W.kini)); var dx = function (id) { return D.find(function (m) { return m.id === id; }); };
cek('daftar: hanya yang menunggu (4 buatan uji, yang sudah disetujui tidak), yang tidak boleh disebut "di HP/Mac", hitungan laci menyebut lembar Tutup hari', D.filter(function (m) { return ['tt1', 'ps1', 'hl1', 'x1'].indexOf(m.id) >= 0; }).length === 4 && !dx('old') && /HP\/Mac owner/.test(dx('x1').hanyaHp) && /Tutup hari/.test(dx('hl1').hanyaHp) && dx('tt1').hanyaHp === '', D.map(function (m) { return [m.id, m.boleh, m.hanyaHp]; }));
var R1 = owSusunPutus('tt1', 'setuju', '', W); var p1 = (R1.dokumen || []).find(function (d) { return d.koleksi === 'persetujuan'; }); var u1 = (R1.dokumen || []).find(function (d) { return d.koleksi === 'pengeluaranHarian'; });
cek('setujui titipan uang di tablet: jalur yang sama dengan HP — uang keluarnya ikut di kiriman yang sama, permintaan disetujui bercap "tablet · sidik jari owner"',
  !R1.tolak && !!p1 && p1.data.status === 'disetujui' && p1.data.diputusDi === OW_DI && OW_DI === 'tablet · sidik jari owner' && !!u1 && u1.data.nominal === 25000 && u1.data.dariPersetujuan === 'tt1', R1);
var R2 = owSusunPutus('ps1', 'dibaca', 'Oke', W); var p2 = (R2.dokumen || [])[0];
cek('pesan: tandai dibaca (+ balasan), bercap; "setujui" pesan ditolak', !R2.tolak && p2.data.status === 'dibaca' && p2.data.diputusDi === OW_DI && !!owSusunPutus('ps1', 'setuju', '', W).tolak, R2);
cek('hitungan laci: setujui DITOLAK (tutup hari di lembar Tutup hari HP/Mac); tolak tanpa alasan ditolak', /Tutup hari/.test(owSusunPutus('hl1', 'setuju', '', W).tolak || '') && /alasan/.test(owSusunPutus('hl1', 'tolak', ' ', W).tolak || ''));
var R3 = owSusunPutus('hl1', 'tolak', 'Hitung ulang, kurang 50 rb', W);
cek('hitungan laci: tolak dengan alasan = minta hitung ulang (ditolak + alasan + cap), tanpa dokumen uang', !R3.tolak && R3.dokumen.length === 1 && R3.dokumen[0].data.status === 'ditolak' && R3.dokumen[0].data.alasanTolak === 'Hitung ulang, kurang 50 rb' && R3.dokumen[0].data.diputusDi === OW_DI, R3);
cek('jenis lain: setujui & tolak di tablet ditolak (putuskan di HP/Mac)', /HP\/Mac/.test(owSusunPutus('x1', 'setuju', '', W).tolak || '') && /HP\/Mac/.test(owSusunPutus('x1', 'tolak', 'x', W).tolak || ''));
cek('yang sudah diputus / tidak ada: ditolak', /sudah diputus/.test(owSusunPutus('old', 'setuju', '', W).tolak || '') && /sudah diputus/.test(owSusunPutus('tidakada', 'setuju', '', W).tolak || ''));
var L = { data: 'AAA', iv: 'BBB', uid: 'uid-tablet', dipasang: '2026-11-23T01:00:00.000Z' };
cek('simpanan perangkat: rusak / tanpa data / iv / uid = null; menyala hanya untuk akun tablet yang menyalakannya', owBaca('{x') === null && owBaca(J({ data: 'a', iv: 'b' })) === null && J(owBaca(J(L))) === J(L)
  && owNyala(L, { uid: 'uid-tablet' }) && !owNyala(L, { uid: 'lain' }) && !owNyala(null, { uid: 'uid-tablet' }));
cek('keadaan kartu: APK lama = tidak, mati, menyala', owKeadaan(L, { uid: 'uid-tablet' }, false).st === 'tidak' && owKeadaan(null, { uid: 'uid-tablet' }, true).st === 'mati' && owKeadaan(L, { uid: 'uid-tablet' }, true).st === 'nyala');
cek('tolakan plugin: hangus = buang simpanan + tandai hangus; kunci berganti / rusak = buang; batal tempel jari = simpanan tetap',
  owArtiGagal({ code: 'BIOMETRIK_HANGUS' }).matikan && owArtiGagal({ code: 'BIOMETRIK_HANGUS' }).hangus && owArtiGagal({ code: 'PENANDA_GAGAL' }).matikan && owArtiGagal({ code: 'RAHASIA_RUSAK' }).matikan
  && !owArtiGagal({ code: 'BIOMETRIK_13' }).matikan && !owArtiGagal({ code: 'BIOMETRIK_10' }).matikan);
/*TAMPILAN*/
print(J(hasil));
"""


def potong(teks, awal, akhir):
    i = teks.find(awal); j = teks.find(akhir, i + 1) if i >= 0 else -1
    return teks[i:j] if i >= 0 and j > i else ''


def tampilan(t):
    K = potong(t[MN], '  function kartuOwnerTablet(s) {', '  function gambarStaf(')
    if not K: return "cek('tampilan: kartuOwnerTablet ada di menu.js', false);"
    D = open(os.path.join(AKAR, 'baru/js/inti/dom.js'), encoding='utf-8').read(); a = D.find('export const esc'); b = D.find('export const mentah')
    return ("(function () {\n" + D[a:b].replace('export ', '') + "\nvar OW = { owKeadaan: owKeadaan };\nvar KEAD = { st: 'nyala', teks: 'Menyala' };\n"
            "var ow = function () { return { keadaan: function () { return KEAD; }, daftar: function () { return owDaftar(new Date('2026-09-19T15:00:00.000Z')); } }; };\n" + K + r"""
try {
  var g = kartuOwnerTablet({ owTolak: 'hl1', owAlasan: '', owSibuk: false }).html;
  var blok = function (id) { var i = g.indexOf('data-k="ow-' + id + '"'); var j = g.indexOf('data-k="ow-', i + 5); return i < 0 ? '' : g.slice(i, j < 0 ? g.length : j); };
  cek('kartu menyala: titipan = Setujui · jari + Tolak; pesan = Dibaca · jari; hitungan laci = Tolak saja (+ alasan & TOLAK · jari); jenis lain = tanpa tombol, disebut HP/Mac',
    /data-a="setuju"/.test(blok('tt1')) && /data-aksi="owBukaTolak"/.test(blok('tt1')) && /data-a="dibaca"/.test(blok('ps1')) && !/data-a="setuju"/.test(blok('ps1'))
    && !/data-a="setuju"/.test(blok('hl1')) && /data-a="tolak"/.test(blok('hl1')) && /data-ketik="owAlasanKetik"/.test(blok('hl1'))
    && !/data-aksi="ow(Putus|BukaTolak)"/.test(blok('x1')) && /HP\/Mac owner/.test(blok('x1')) && /data-aksi="owMatikan"/.test(g) && !/undefined|NaN|\[object/.test(g), g.slice(0, 1500));
  KEAD = { st: 'mati', teks: 'Mati' };
  var m = kartuOwnerTablet({ owBukaNyala: true, owSandi: '' }).html;
  cek('kartu mati: kolom sandi bertipe password tanpa isi otomatis + NYALAKAN · tempel jari; APK lama = tanpa kartu', /type="password" autocomplete="off"/.test(m) && /data-ketik="owSandiKetik"/.test(m) && /data-aksi="owNyalakan"/.test(m)
    && (KEAD = { st: 'tidak', teks: '' }, kartuOwnerTablet({}) === ''), m.slice(0, 600));
} catch (e) { cek('tampilan: kartuOwnerTablet jalan tanpa galat', false, String(e && e.stack || e)); }
})();
""")


def baca_semua():
    return dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in [OWL, MN, FB, APP, IDX, PR, 'alat-uji/uji_isian_lokal.py'])


def rakit(t):
    isi = lambda m: t[m] if m in t else open(os.path.join(AKAR, m), encoding='utf-8').read()
    return '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(isi(m)) for m in bundel_baru.lengkapi(MODUL)])


def jalankan(t):
    K = json.loads(json.dumps(UB.KOTAK)); K['persetujuan'] = K.get('persetujuan', []) + KOTAK_TAMBAH['persetujuan']
    js = UB.JAM_TETAP + rakit(t) + '\nvar KOTAK = ' + json.dumps(K) + ';\n' + SKENARIO.replace('/*TAMPILAN*/', tampilan(t))
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([UB.JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    keluar = (r.stdout or '').strip().split('\n')[-1] if r.stdout else ''
    if r.returncode != 0 or not keluar.startswith('['): return [{'nama': 'jsc jalan', 'ok': False, 'ket': ((r.stderr or '') + (r.stdout or ''))[-1500:]}]
    return json.loads(keluar)


def periksa_statis(t):
    c = []; ok = lambda n, x, k='': c.append({'nama': 'statis: ' + n, 'ok': bool(x), 'ket': k})
    F = potong(t[FB], 'export async function tulisSebagaiOwner(', 'export async function simpanFotoBon(')
    ok('penulis owner: app kedua, auth di MEMORI, cache memori, impor SDK dinamis (SDK palsu uji peramban tetap)', "initializeApp(app.options, 'ownerTablet')" in F
       and 'A.initializeAuth(a2, { persistence: A.inMemoryPersistence })' in F and 'F.initializeFirestore(a2, { localCache: F.memoryLocalCache() })' in F
       and "await import('https://www.gstatic.com/firebasejs/10.13.0/firebase-auth.js')" in F and 'localStorage' not in F and 'browserLocalPersistence' not in F)
    ok('penulis owner: offline ditolak SEBELUM masuk, penjaga bulan terkunci, masuk sebagai EMAIL_OWNER', F.find("navigator.onLine === false") >= 0 and F.find("navigator.onLine === false") < F.find('signInWithEmailAndPassword')
       and 'const j = jagaKunci(daftar || [], hapus || [], {}); if (j) return j;' in F and 'A.signInWithEmailAndPassword(au, EMAIL_OWNER, String(sandi || \'\'))' in F)
    ok('penulis owner: pencatat setelan, jejak bertanda lewat, menunggu server (commit), KELUAR di finally', 'rsdSertakan(koleksi, beriAtribusiAkun(data, akunO, k, !!lama), lama, true, k.kini)' in F
       and F.count('lewat: OWNER_TABLET_LEWAT') == 2 and 'await b.commit();' in F and re.search(r"\} finally \{\s*try \{ await A\.signOut\(au\); \}", F) is not None)
    A = potong(t[APP], 'const ownerTablet = {', '// Menu (putaran 14)')
    ok('jembatan: sandi diperiksa ke server SEBELUM dikunci jari; yang disimpan hanya data, iv, uid, dipasang', A.find('fb.tulisSebagaiOwner(sandi, [], [])') >= 0 and A.find('fb.tulisSebagaiOwner(sandi, [], [])') < A.find('rahasiaSimpan(sandi)')
       and 'owSimpan({ data: r.data, iv: r.iv, uid: a.uid, dipasang: new Date().toISOString() });' in A and not re.search(r'owSimpan\([^)]*sandi', A) and 'localStorage' not in A.replace('localStorage.getItem(OW.OW_KUNCI)', '').replace('localStorage.setItem(OW.OW_KUNCI, JSON.stringify(o))', '').replace('localStorage.removeItem(OW.OW_KUNCI)', ''))
    pt = potong(A, 'async putus(id, aksi, alasan) {', '\n  },')
    ok('jembatan: putusan = periksa → tempel jari → dihitung ulang → kirim → sandi dibuang; gagal kunci = simpanan dibuang', 0 <= pt.find('const cek = OW.owSusunPutus(') < pt.find('rahasiaBuka(L,') < pt.find('const R = OW.owSusunPutus(') < pt.find('fb.tulisSebagaiOwner(sandi, R.dokumen') < pt.find("sandi = '';", pt.find('fb.tulisSebagaiOwner(sandi, R.dokumen'))
       and 'if (g.matikan) owSimpan(null);' in pt and 'if (h.salahSandi) owSimpan(null);' in pt)
    ok('jembatan: kunci dipasang ulang → Tahap A ditandai mati dulu (hangus = kabar owner)', re.search(r"if \(c\.hangus\) sjMatiHangus\(true\); else if \(!c\.ada\) sjMatiHangus\(false\); if \(!c\.ada \|\| c\.hangus\) \{ await penandaPasang\(\);", A) is not None)
    M = t[MN]
    ok('Menu: kartu di layar tablet; sandi = kolom password, dikosongkan SEBELUM menunggu; sandi & alasan tidak pernah jadi isian / draf',
       '${kartuOwnerTablet(s)}' in potong(M, '  function gambarStaf(s, d, akunM) {', '  function ') and "set({ owSibuk: true, owSandi: '' }); const r = await X.nyalakan(sandi);" in M
       and not re.search(r"pasangIsian\([^;]*'owSandi'", M) and "'owSandi': 'sandi akun owner" in t['alat-uji/uji_isian_lokal.py'])
    ok('index.html memuat owner-tablet-logika (modulepreload); perangkat.js punya rahasiaSimpan/Buka + adaMetode', '<link rel="modulepreload" href="js/layar/owner-tablet-logika.js">' in t[IDX]
       and 'export function adaMetode(nama, metode)' in t[PR] and "panggilAsli('Biometrik', 'rahasiaBuka'," in t[PR])
    ok('logika putusan tablet tidak menulis sendiri', not re.search(r'tulisDokumen|setDoc|writeBatch|import .*firebase|localStorage\.', t[OWL]))
    return c


def periksa(t, diam=False):
    c = jalankan(t) + periksa_statis(t)
    g = [x for x in c if not x['ok']]
    if not diam:
        for x in c: print(('✓ ' if x['ok'] else '✗ ') + x['nama'] + ('' if x['ok'] else ' → ' + str(x['ket'])[:900]))
        print('PUTUSAN OWNER DI TABLET: %d lulus · %d gagal' % (len(c) - len(g), len(g)))
    return g


def main():
    t = baca_semua()
    if '--kontrol' in sys.argv:
        O = t[OWL]; F = t[FB]; A = t[APP]; M = t[MN]
        rusak = [
            ('hitungan laci boleh disetujui di tablet (tutup hari tanpa data uang lengkap)', OWL, O.replace("if (t === SS_HITUNG_LACI) return { setuju: false, tolak: true, dibaca: false };", "if (t === SS_HITUNG_LACI) return { setuju: true, tolak: true, dibaca: false };")),
            ('jenis lain boleh diputus di tablet', OWL, O.replace("  return { setuju: false, tolak: false, dibaca: false };\n}", "  return { setuju: true, tolak: true, dibaca: false };\n}")),
            ('putusan tanpa cap tablet', OWL, O.replace("data: Object.assign({}, d.data, { diputusDi: OW_DI })", "data: Object.assign({}, d.data)")),
            ('alasan menolak tidak diteruskan ke jalur HP', OWL, O.replace("aksi === 'dibaca' ? String(alasan || '') : alasan, w)", "aksi === 'dibaca' ? String(alasan || '') : '', w)")),
            ('batal tempel jari membuang simpanan', OWL, O.replace("return { matikan: false, kalimat: '' };", "return { matikan: true, kalimat: '' };")),
            ('auth owner tersimpan di tablet (bukan memori)', FB, F.replace('A.initializeAuth(a2, { persistence: A.inMemoryPersistence })', 'A.initializeAuth(a2, { persistence: A.browserLocalPersistence })')),
            ('sesi owner tidak keluar sesudah kiriman', FB, F.replace('    try { await A.signOut(au); } catch (e) {', '    try { } catch (e) {')),
            ('offline tidak ditolak (putusan menggantung di antrean)', FB, F.replace("if (typeof navigator !== 'undefined' && navigator.onLine === false) return { gagal: true, pesan: 'Putusan owner di tablet butuh internet", "if (false) return { gagal: true, pesan: 'Putusan owner di tablet butuh internet")),
            ('sandi dikunci tanpa diperiksa ke server', APP, A.replace("const v = await fb.tulisSebagaiOwner(sandi, [], []); if (!v.ok) return", "const v = { ok: true }; if (!v.ok) return")),
            ('sandi ikut disimpan terbuka', APP, A.replace("owSimpan({ data: r.data, iv: r.iv, uid: a.uid, dipasang: new Date().toISOString() });", "owSimpan({ data: r.data, iv: r.iv, uid: a.uid, dipasang: new Date().toISOString(), sandi });")),
            ('putusan tidak dihitung ulang sesudah jari', APP, A.replace("const R = OW.owSusunPutus(id, aksi, alasan, sjWaktu()); if (R.tolak) { sandi = ''; return { ok: false, kalimat: R.tolak }; }", "const R = cek;")),
            ('pemasangan ulang kunci tidak mematikan Tahap A', APP, A.replace("if (c.hangus) sjMatiHangus(true); else if (!c.ada) sjMatiHangus(false); ", "")),
            ('kolom sandi bukan password', MN, M.replace('type="password" autocomplete="off" placeholder="sandi akun owner"', 'type="text" placeholder="sandi akun owner"')),
            ('kartu tablet menampilkan Setujui untuk hitungan laci', MN, M.replace("${m.boleh.setuju ? h`<div class=\"kaca-btn kecil aktif emas\" data-aksi=\"owPutus\"", "${m.boleh.setuju || m.boleh.tolak ? h`<div class=\"kaca-btn kecil aktif emas\" data-aksi=\"owPutus\"")),
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
