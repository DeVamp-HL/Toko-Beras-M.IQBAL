#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_server_tiruan.py — SERVER TIRUAN /baru/ (gladi tutup buku di Firebase Emulator Suite, 7 Okt 2026). jsc + statis, TANPA peramban.

Yang dijaga (baru/js/data/server-tiruan.js dijalankan sungguhan di jsc; firebase.js, app.js, index.html dibaca sumbernya):
  · ?emulator=host:port hanya berlaku di halaman localhost / 127.0.0.1 — di situs sungguhan (github.io) DIABAIKAN (null, bukan galat);
  · alamat emulator wajib localhost / 127.0.0.1 + port angka 1–65535 — host lain / port rusak / kosong = ditolak, dan yang ditolak GAGAL-TERTUTUP:
    firebase.js mulai() berhenti SEBELUM initializeApp (tidak tersambung ke data toko maupun ke mana pun), app.js memasang bilah "SERVER TIRUAN DITOLAK";
  · Auth bawaan port 9099 di host yang sama; ?emulatorAuth= hanya alamat lokal;
  · proyeknya proyek "demo-…" yang BUKAN proyek toko, dan setelan aplikasinya tanpa kunci API toko;
  · firebase.js: emulator disambung HANYA di belakang serverTiruanAktif(), tepat sesudah initializeFirestore / getAuth (sebelum dipakai apa pun);
  · CSP situs (baru/index.html) TIDAK dilonggarkan: connect-src tanpa http://, localhost, 127.0.0.1 — salinan uji gladi yang melonggarkannya;
  · app.js memasang bilah "SERVER TIRUAN" selama aktif (orang tidak bisa mengira itu data toko).

    python3 alat-uji/uji_server_tiruan.py            → N lulus · 0 gagal
    python3 alat-uji/uji_server_tiruan.py --kontrol  → penjaga yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, shutil, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_csp  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
TIRUAN, FB, APP, HTML = 'baru/js/data/server-tiruan.js', 'baru/js/data/firebase.js', 'baru/js/app.js', 'baru/index.html'
PROYEK_TOKO = 'toko-beras-m-iqbal'

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 300) : '')); }
function Q(o) { return { get: function (k) { return Object.prototype.hasOwnProperty.call(o, k) ? o[k] : null; } }; }
var S = serverTiruan;
ok('tanpa ?emulator= → null (aplikasi ke data toko)', S(Q({}), 'localhost') === null && S(Q({}), 'tokoberasmiqbal.github.io') === null);
ok('situs sungguhan (github.io) dengan ?emulator=127.0.0.1:8080 → DIABAIKAN (null)', S(Q({ emulator: '127.0.0.1:8080' }), 'devamp-hl.github.io') === null
  && S(Q({ emulator: '127.0.0.1:8080' }), '') === null && S(Q({ emulator: 'localhost:8080' }), 'localhost.evil.example') === null, J(S(Q({ emulator: '127.0.0.1:8080' }), 'devamp-hl.github.io')));
var t = S(Q({ emulator: '127.0.0.1:8080' }), '127.0.0.1');
ok('halaman 127.0.0.1 + ?emulator=127.0.0.1:8080 → Firestore 127.0.0.1:8080, Auth http://127.0.0.1:9099, proyek demo', !!t && !t.tolak && t.firestore.host === '127.0.0.1'
  && t.firestore.port === 8080 && t.auth === 'http://127.0.0.1:9099' && t.proyek === PROYEK_TIRUAN, J(t));
var t2 = S(Q({ emulator: 'localhost:8181', emulatorAuth: 'LOCALHOST:9199' }), 'LocalHost');
ok('halaman localhost + ?emulatorAuth= lokal → dipakai (huruf besar/kecil bebas)', !!t2 && !t2.tolak && t2.firestore.host === 'localhost' && t2.firestore.port === 8181 && t2.auth === 'http://localhost:9199', J(t2));
['firestore.googleapis.com:443', 'evil.example:8080', '10.0.0.5:8080', '127.0.0.1', '127.0.0.1:0', '127.0.0.1:70000', '127.0.0.1:80a', 'http://127.0.0.1:8080', '127.0.0.1:8080/x', ' :8080']
  .forEach(function (a) { var r = S(Q({ emulator: a }), 'localhost'); ok('alamat emulator Firestore ' + J(a) + ' DITOLAK (bukan lokal / port rusak)', !!r && !!r.tolak && !r.firestore, J(r)); });
var k0 = S(Q({ emulator: '' }), 'localhost');
ok('halaman lokal + ?emulator= KOSONG → tetap permintaan, DITOLAK (gagal-tertutup, bukan jatuh ke data toko)', !!k0 && !!k0.tolak && !k0.firestore, J(k0));
ok('situs sungguhan + ?emulator= kosong → diabaikan (null)', S(Q({ emulator: '' }), 'devamp-hl.github.io') === null);
var k1 = S(Q({ emulator: '127.0.0.1:8080', emulatorAuth: '' }), '127.0.0.1');
ok('?emulatorAuth= KOSONG → DITOLAK (bukan diam-diam port bawaan)', !!k1 && !!k1.tolak, J(k1));
['evil.example:9099', '127.0.0.1', '192.168.1.2:9099'].forEach(function (a) { var r = S(Q({ emulator: '127.0.0.1:8080', emulatorAuth: a }), 'localhost'); ok('alamat emulator Auth ' + J(a) + ' DITOLAK', !!r && !!r.tolak, J(r)); });
ok('proyek tiruan = proyek "demo-…" (Firebase tidak pernah menyambungkannya ke server sungguhan) dan BUKAN proyek toko', /^demo-/.test(PROYEK_TIRUAN) && PROYEK_TIRUAN !== PROYEK_TOKO, PROYEK_TIRUAN);
var c = configTiruan(t);
ok('setelan aplikasi tiruan: projectId proyek demo, tanpa kunci API & appId toko', c.projectId === PROYEK_TIRUAN && c.apiKey !== KUNCI_TOKO && c.appId !== APP_TOKO && c.authDomain.indexOf(PROYEK_TOKO) < 0, J(c));
ok('HOST_LOKAL hanya localhost & 127.0.0.1', J(HOST_LOKAL.slice().sort()) === J(['127.0.0.1', 'localhost']), J(HOST_LOKAL));
print(J({ lulus: lulus, gagal: gagal }));
"""


def baca(p, T=None):
    return (T or {}).get(p) if (T or {}).get(p) is not None else open(os.path.join(AKAR, p), encoding='utf-8').read()


def jalan_jsc(T):
    fb = baca(FB, T)
    kunci = re.search(r"apiKey: '([^']+)'", fb); app = re.search(r"appId: '([^']+)'", fb)
    js = (bundel_baru.PRELUDE + '\n' + bundel_baru.polos(baca(TIRUAN, T)) + '\nvar PROYEK_TOKO = ' + json.dumps(PROYEK_TOKO) + ', KUNCI_TOKO = '
          + json.dumps(kunci.group(1) if kunci else '?') + ', APP_TOKO = ' + json.dumps(app.group(1) if app else '?') + ';\n' + SKENARIO)
    if not os.path.exists(JSC):
        return 0, ['jsc tidak ada di mesin ini — uji ini butuh macOS (CI: job uji di macos-latest)']
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[:900]]
    h = json.loads(out); return h['lulus'], h['gagal']


def periksa_statis(T=None):
    c = []
    ti, fb, ap, html = baca(TIRUAN, T), baca(FB, T), baca(APP, T), baca(HTML, T)
    c.append(('server-tiruan.js tanpa impor (diuji apa adanya di jsc)', not re.search(r'^\s*import\b', ti, re.M), ''))
    m = re.search(r'export function mulai\(saatAkun\) \{(.*?)\n\}', fb, re.S); mulai = m.group(1) if m else ''
    i_tolak = mulai.find('const tolakT = tolakServerTiruan(); if (tolakT) { status.galat = tolakT; beriTahu(); return; }'); i_app = mulai.find('app = initializeApp(')
    c.append(('firebase.js mulai(): server tiruan DITOLAK → berhenti SEBELUM initializeApp (gagal-tertutup: tidak tersambung ke data toko maupun ke mana pun)',
              0 <= i_tolak < i_app, (i_tolak, i_app)))
    c.append(('firebase.js mulai(): T = serverTiruanAktif(); initializeApp(T ? configTiruan(T) : …) — proyek demo, bukan proyek toko, selama tiruan aktif',
              'const T = serverTiruanAktif();' in mulai and 'initializeApp(T ? configTiruan(T) : (proyekUji() || firebaseConfig))' in mulai, mulai[:200]))
    i_db = mulai.find('db = initializeFirestore('); i_fs = mulai.find('if (T) connectFirestoreEmulator(db, T.firestore.host, T.firestore.port);')
    i_au = mulai.find('auth = getAuth(app);'); i_ae = mulai.find('if (T) connectAuthEmulator(auth, T.auth, { disableWarnings: true });')
    c.append(('firebase.js: emulator disambung HANYA di belakang `if (T)`, tepat sesudah initializeFirestore / getAuth (sebelum db & auth dipakai)',
              0 <= i_db < i_fs < i_au < i_ae and mulai[i_fs:i_au].count('\n') <= 1 and mulai[i_ae:].find('setPersistence(auth') > 0, (i_db, i_fs, i_au, i_ae)))
    luar = [x for x in re.findall(r'connect(?:Firestore|Auth)Emulator\([^)]*\)', fb) if x not in ('connectFirestoreEmulator(db, T.firestore.host, T.firestore.port)', 'connectAuthEmulator(auth, T.auth, { disableWarnings: true })')]
    c.append(('firebase.js: tidak ada panggilan connect*Emulator lain', not luar and fb.count('connectFirestoreEmulator(') == 1 and fb.count('connectAuthEmulator(') == 1, luar))
    c.append(('firebase.js: alamat dibaca dari halaman (location.search + location.hostname) lewat serverTiruan(), tidak dari localStorage',
              'serverTiruan(new URLSearchParams(location.search), location.hostname)' in fb and not re.search(r'localStorage[^\n]*emulator', fb, re.I), ''))
    D, _ = uji_csp.csp_dari(html); cs = (D or {}).get('connect-src', [])
    lokal = [x for x in cs if re.search(r'^http:|localhost|127\.0\.0\.1|\[::1\]|:\d+$', x)]
    c.append(('CSP situs baru/index.html TIDAK dilonggarkan: connect-src tanpa http://, localhost, 127.0.0.1, port', bool(cs) and not lokal, lokal or cs))
    i = ap.find("const tolak = fb.tolakServerTiruan(); const T = fb.serverTiruanAktif(); if (!tolak && !T) return;"); blok = ap[i:ap.find('})();', i)] if i >= 0 else ''
    c.append(('app.js: bilah "SERVER TIRUAN" dipasang selama fb.serverTiruanAktif(), bilah "SERVER TIRUAN DITOLAK" yang menetap bila ditolak (bukan kabar sebentar)',
              "'<span>SERVER TIRUAN <b></b>" in blok and "'<span>SERVER TIRUAN DITOLAK — <b></b></span>'" in blok and 'document.body.appendChild(bilah);' in blok
              and 'kabarSebentar' not in blok, blok[:160]))
    c.append(('index.html: server-tiruan.js dipramuat (graf impor app.js)', '<link rel="modulepreload" href="js/data/server-tiruan.js">' in html, ''))
    return c


def semua(T=None):
    l, g = jalan_jsc(T)
    for nama, syarat, ket in periksa_statis(T):
        if syarat: l += 1
        else: g.append(nama + ' → ' + str(ket)[:200])
    return l, g


KONTROL = [
    ('halaman situs sungguhan ikut menyalakan emulator (penjaga hostname dibuang)', {TIRUAN: [("  if (HOST_LOKAL.indexOf(String(namaHost || '').toLowerCase()) < 0) return null;\n", '')]}),
    ('emulator boleh di host mana pun', {TIRUAN: [("if (HOST_LOKAL.indexOf(host) < 0 || !(port >= 1 && port <= 65535)) return null;", "if (!(port >= 1 && port <= 65535)) return null;")]}),
    ('port tidak diperiksa', {TIRUAN: [("if (HOST_LOKAL.indexOf(host) < 0 || !(port >= 1 && port <= 65535)) return null;", "if (HOST_LOKAL.indexOf(host) < 0) return null;")]}),
    ('proyek tiruan = proyek toko', {TIRUAN: [("export const PROYEK_TIRUAN = 'demo-gladi-toko';", "export const PROYEK_TIRUAN = 'toko-beras-m-iqbal';")]}),
    ('emulator Auth host bebas', {TIRUAN: [("const au = mintaAuth !== null && mintaAuth !== undefined ? alamatLokal(mintaAuth) :", "const au = mintaAuth ? { host: mintaAuth.split(':')[0], port: Number(mintaAuth.split(':')[1]) } :")]}),
    ('server tiruan yang ditolak jatuh ke proyek toko (gagal-terbuka)', {FB: [("  const tolakT = tolakServerTiruan(); if (tolakT) { status.galat = tolakT; beriTahu(); return; }\n", '')]}),
    ('?emulator= kosong dianggap tidak diminta', {TIRUAN: [("  if (minta === null || minta === undefined) return null;", "  if (!minta) return null;")]}),
    ('bilah DITOLAK hanya kabar sebentar', {APP: [("bilah.innerHTML = tolak ? '<span>SERVER TIRUAN DITOLAK — <b></b></span>' : ", "if (tolak) kabarSebentar(tolak); bilah.innerHTML = ")]}),
    ('firebase.js menyambung emulator tanpa penjaga', {FB: [('  if (T) connectFirestoreEmulator(db, T.firestore.host, T.firestore.port);', '  connectFirestoreEmulator(db, (T || { firestore: {} }).firestore.host, 8080);')]}),
    ('firebase.js memakai setelan toko walau tiruan aktif', {FB: [('initializeApp(T ? configTiruan(T) : (proyekUji() || firebaseConfig))', 'initializeApp(proyekUji() || firebaseConfig)')]}),
    ('emulator Auth disambung sesudah auth dipakai', {FB: [("  if (T) connectAuthEmulator(auth, T.auth, { disableWarnings: true });\n", ''),
                                                       ("  setPersistence(auth, browserLocalPersistence).catch(() => {});\n", "  setPersistence(auth, browserLocalPersistence).catch(() => {});\n  if (T) connectAuthEmulator(auth, T.auth, { disableWarnings: true });\n")]}),
    ('CSP situs dilonggarkan untuk emulator', {HTML: [("connect-src 'self' https://firestore.googleapis.com", "connect-src 'self' http://127.0.0.1:8080 https://firestore.googleapis.com")]}),
    ('bilah SERVER TIRUAN hilang', {APP: [("  document.body.appendChild(bilah); document.body.classList.add('proyek-uji');\n})();\n\nif (q.get('cadangan'))", "})();\n\nif (q.get('cadangan'))")]}),
]


def rusak(ganti):
    T = {}
    for p, pasangan in ganti.items():
        s = baca(p)
        for lama, baru in pasangan:
            assert s.count(lama) == 1, 'kontrol basi: ' + p + ' · ' + lama[:80] + ' (' + str(s.count(lama)) + '×)'
            s = s.replace(lama, baru, 1)
        T[p] = s
    return T


if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti in KONTROL:
            try: T = rusak(ganti)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' · ' + str(e)); kode = 3; continue
            l, g = semua(T)
            b = bool(g) and not any(x.startswith('JSC JATUH') for x in g)   # jsc yang jatuh bukan bunyi kontrol — penjaganya tidak dinilai sama sekali
            print(('BERBUNYI ' if b else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not b: kode = 3
        sys.exit(kode)
    l, g = semua()
    print('SERVER TIRUAN /baru/ (gladi emulator): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x[:400])
    sys.exit(2 if g else 0)
