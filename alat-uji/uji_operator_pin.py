#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_operator_pin.py — putaran 25c Bagian C: OPERATOR KASIR & PIN OWNER pindah ke /baru/ (Menu › Peran & persetujuan › Kasir & PIN).
Keputusan owner 27 Sep 2026: PIN operator DICABUT dari dokumen pengaturan/aksesKasir (dibaca akun kasir@, PIN-nya tersimpan tanpa diacak, dan tidak
dipakai kasir mana pun); daftar nama + aktif/libur pindah; PIN owner (pengaturan/keamanan, hanya hasil acak, owner saja) pindah dengan bentuk sama.
KOTAK PASIR (nama contoh, PIN contoh) di jsc; SHA-256 peramban diganti implementasi JS yang DICOCOKKAN dengan hashlib Python dulu.

STATIS:
  · acakPin /baru/ HURUF DEMI HURUF = acakPin() index.html (pindah_mesin.py)
  · index.html: operator & PIN owner tidak lagi di daftar tulis terbuka; bukaModalJaga, simpanModalJaga, bukaSetelPin, simpanPinOwnerBaru bertanya ke
    penjaga SEBELUM apa pun diubah (salinan HP juga)
  · menu.js: tab "Kasir & PIN" di Peran & persetujuan; kolom PIN berjenis sandi tanpa isi otomatis; isiannya dijaga penjaga isian
JSC:
  · daftar operator dari dokumen (nama = kunci peta, tidak ada nama di kode); isi PIN tidak pernah keluar dari logika; jumlah PIN terbuka dihitung
  · cabut PIN / aktif-libur / hapus (dua ketukan): dokumen berkunci sama dengan simpanModalJaga() index.html, TANPA satu pun field pin; TIDAK ada
    "tambah operator" (nama baru tidak sampai ke kasir mana pun: kasir.html memakai daftar nama tetap, kasir darurat tidak membaca dokumen ini)
  · kasir.html SUNGGUHAN (infoOperator dari teks kasir.html) membaca dokumen /baru/: aktif/libur terbaca, PIN = tidak ada (dokumen lama: PIN terbaca)
  · PIN owner: dokumen berkunci sama dengan simpanPinOwnerBaru() index.html; acak = SHA-256(garam|PIN) (dicek hashlib); pinOwnerBenar() index.html menerima
    PIN baru dari dokumen /baru/; PIN sekarang wajib benar; 4–8 angka; ulangan sama; dokumen tanpa PIN terbuka
  · (cadangan toko di _privat/, lokal) dokumen aksesKasir sungguhan: PIN terbuka terhitung, cabut → nol, nama & aktif utuh — tanpa mencetak nama/PIN

    python3 alat-uji/uji_operator_pin.py            → N lulus · 0 gagal
    python3 alat-uji/uji_operator_pin.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob, hashlib, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, beku2  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/akses-kasir-logika.js']
BERKAS = list(dict.fromkeys(MODUL + ['index.html', 'kasir.html', 'baru/js/layar/menu.js']))
JAM = "var __KINI = new Date('2026-09-27T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
HASH_UJI = hashlib.sha256('g-uji|4321'.encode()).hexdigest()
HASH_LAMA = hashlib.sha256('g-lama|2468'.encode()).hexdigest()

# SHA-256 + TextEncoder untuk jsc (peramban punya crypto.subtle; jsc tidak). Hasilnya dicocokkan dengan hashlib sebelum dipakai.
POLYFILL = r"""
var TextEncoder = function () {}; TextEncoder.prototype.encode = function (s) { var u = unescape(encodeURIComponent(String(s))); var a = new Uint8Array(u.length); for (var i = 0; i < u.length; i++) a[i] = u.charCodeAt(i); return a; };
var crypto = { subtle: { digest: function (alg, data) {
  var K = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  var H = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  var b = Array.prototype.slice.call(data); var l = b.length * 8; b.push(0x80); while (b.length % 64 !== 56) b.push(0);
  for (var s = 56; s >= 0; s -= 8) b.push(s >= 32 ? 0 : (l >>> s) & 0xff);
  var r = function (x, n) { return (x >>> n) | (x << (32 - n)); };
  for (var o = 0; o < b.length; o += 64) {
    var w = []; for (var t = 0; t < 16; t++) w[t] = (b[o + 4 * t] << 24) | (b[o + 4 * t + 1] << 16) | (b[o + 4 * t + 2] << 8) | b[o + 4 * t + 3];
    for (t = 16; t < 64; t++) { var s0 = r(w[t - 15], 7) ^ r(w[t - 15], 18) ^ (w[t - 15] >>> 3), s1 = r(w[t - 2], 17) ^ r(w[t - 2], 19) ^ (w[t - 2] >>> 10); w[t] = (w[t - 16] + s0 + w[t - 7] + s1) | 0; }
    var a = H[0], c = H[1], d = H[2], e = H[3], f = H[4], g = H[5], h = H[6], k = H[7];
    for (t = 0; t < 64; t++) { var S1 = r(f, 6) ^ r(f, 11) ^ r(f, 25), ch = (f & g) ^ (~f & h), t1 = (k + S1 + ch + K[t] + w[t]) | 0, S0 = r(a, 2) ^ r(a, 13) ^ r(a, 22), mj = (a & c) ^ (a & d) ^ (c & d), t2 = (S0 + mj) | 0;
      k = h; h = g; g = f; f = (e + t1) | 0; e = d; d = c; c = a; a = (t1 + t2) | 0; }
    H = [H[0] + a, H[1] + c, H[2] + d, H[3] + e, H[4] + f, H[5] + g, H[6] + h, H[7] + k].map(function (x) { return x | 0; });
  }
  var out = new Uint8Array(32); H.forEach(function (x, i) { out[4 * i] = (x >>> 24) & 255; out[4 * i + 1] = (x >>> 16) & 255; out[4 * i + 2] = (x >>> 8) & 255; out[4 * i + 3] = x & 255; });
  return Promise.resolve(out.buffer); } } };
"""


def baca(ganti=None):
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in BERKAS)
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert lama in t[b], 'kontrol basi: ' + b + ' · ' + lama[:80]
            t[b] = t[b].replace(lama, baru, 1)
    return t


def modul_index(t):
    s = t['index.html']; return s[s.index('<script type="module">'):s.rindex('</script>')]


def kunci_obj(teks, pola):
    m = re.search(pola, teks); return [re.match(r'\s*(\w+)', x).group(1) for x in m.group(1).split(',')] if m else None


def cadangan_akses():
    c = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if not c: return None
    d = json.load(open(c[-1], encoding='utf-8'))
    return next((x for x in d.get('pengaturan', []) if x.get('id') == 'aksesKasir'), None)


SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 500) : '')); }
var W = { tanggal: '2026-09-27', jam: '10:00', kini: '2026-09-27T03:00:00.000Z', idUnik: function () { return 1; } };
var adaPin = function (x) { var s = J(x); return /"pin"\s*:/.test(s); };
var DOK_LAMA = { id: 'aksesKasir', operator: { 'Penjaga Contoh A': { aktif: true, pin: '5801' }, 'Penjaga Contoh B': { aktif: false, pin: '6902' }, 'Penjaga Contoh C': { aktif: true, pin: '9753' } },
  diubahPada: '2026-09-05T14:23:17.923Z', oleh: 'Owner' };
(async function () {
  try {
    // ---- 0 · SHA-256 jsc = hashlib (pengganti crypto.subtle peramban)
    ok('SHA-256 pengganti di jsc = hashlib Python (garam|PIN contoh)', (await acakPin('4321', 'g-uji')) === HASH_UJI, await acakPin('4321', 'g-uji'));
    // ---- 1 · daftar operator
    pasok('pengaturan', [DOK_LAMA]);
    var D = opDaftar();
    ok('daftar: nama dari dokumen (kunci peta), urut abjad, aktif/libur terbaca; 3 PIN terbuka terhitung', J(D.baris.map(function (b) { return b.nama + ':' + b.aktif; })) === J(['Penjaga Contoh A:true', 'Penjaga Contoh B:false', 'Penjaga Contoh C:true']) && D.berPin === 3 && D.ada, J(D));
    ok('isi PIN tidak pernah keluar dari logika daftar', !adaPin(D) && !/5801|6902|9753/.test(J(D)));
    // ---- 2 · cabut PIN (keputusan owner)
    var C = susunCabutPinOperator(W); var dc = C.dokumen ? C.dokumen[0] : {};
    ok('cabut PIN: SATU dokumen pengaturan/aksesKasir; kunci = simpanModalJaga() index.html (' + KUNCI_OPERATOR.join(', ') + ')', !C.tolak && C.dokumen.length === 1 && dc.koleksi === 'pengaturan' && J(Object.keys(dc.data)) === J(KUNCI_OPERATOR) && dc.data.id === 'aksesKasir', J(C));
    ok('cabut PIN: TIDAK ADA satu pun field pin; nama & aktif/libur utuh', !adaPin(dc) && J(dc.data.operator) === J({ 'Penjaga Contoh A': { aktif: true }, 'Penjaga Contoh B': { aktif: false }, 'Penjaga Contoh C': { aktif: true } }), J(dc.data));
    terapkanKeCache(C.dokumen);
    ok('sesudah dicabut: 0 PIN terbuka; cabut lagi ditolak dengan kalimat', opDaftar().berPin === 0 && /Tidak ada PIN/.test(susunCabutPinOperator(W).tolak || ''));
    // ---- 3 · aktif/libur · tambah · hapus
    pasok('pengaturan', [DOK_LAMA]);
    var A = susunOperatorAktif('Penjaga Contoh B', true, W);
    ok('aktifkan yang libur: dokumen tanpa pin (PIN lama ikut tercabut), yang lain utuh', !A.tolak && !adaPin(A.dokumen) && A.dokumen[0].data.operator['Penjaga Contoh B'].aktif === true && A.dokumen[0].data.operator['Penjaga Contoh A'].aktif === true && /ikut dicabut/.test(A.patch.kabar), J(A));
    ok('aktif/libur yang sama ditolak; nama yang tidak ada ditolak', /sudah aktif/.test(susunOperatorAktif('Penjaga Contoh A', true, W).tolak || '') && /tidak ada/.test(susunOperatorAktif('Orang Lain', false, W).tolak || ''));
    ok('tidak ada logika "tambah operator" (nama baru tidak sampai ke kasir mana pun)', typeof susunOperatorTambah === 'undefined');
    var H1 = susunOperatorHapus('Penjaga Contoh C', W, false); var H2 = susunOperatorHapus('Penjaga Contoh C', W, true);
    ok('hapus: ketukan pertama hanya minta yakin; kedua menulis dokumen tanpa nama itu & tanpa pin', H1.perluYakin && !H1.dokumen && !H2.tolak && !('Penjaga Contoh C' in H2.dokumen[0].data.operator) && !adaPin(H2.dokumen), J([H1, H2]));
    // ---- 4 · kasir.html SUNGGUHAN membaca dokumen /baru/
    var bacaKasir = function (dok) { __ls['kasir_roster_v1'] = J(dok); return [infoOperator('Penjaga Contoh A'), infoOperator('Penjaga Contoh B')]; };
    var lama = bacaKasir(DOK_LAMA);
    ok('kasir.html + dokumen LAMA: PIN operator terbaca di HP kasir (itulah yang dicabut)', lama[0].pin === '5801' && lama[1].pin === '6902');
    var kini = bacaKasir(dc.data);
    ok('kasir.html + dokumen /baru/: aktif/libur terbaca, PIN = tidak ada (layar pilih operator tidak meminta PIN)', kini[0].aktif === true && kini[0].pin === null && kini[1].aktif === false && kini[1].pin === null, J(kini));
    // ---- 5 · PIN owner
    pasok('pengaturan', []);
    ok('PIN owner belum disetel → keadaannya "belum"; garam & acak tidak pernah keluar', opPinOwner().disetel === false && !/garam|acak/.test(J(opPinOwner())));
    var P = await susunPinOwner({ lama: '', baru: '4321', ulang: '4321' }, W, 'g-uji'); var dp = P.dokumen ? P.dokumen[0] : {};
    ok('setel PIN owner: dokumen pengaturan/keamanan; kunci = simpanPinOwnerBaru() index.html (' + KUNCI_PIN.join(', ') + ')', !P.tolak && dp.koleksi === 'pengaturan' && J(Object.keys(dp.data)) === J(KUNCI_PIN) && dp.data.id === 'keamanan', J(P));
    ok('isinya hanya hasil acak: acak = SHA-256(garam|PIN) (hashlib), PIN-nya sendiri TIDAK tersimpan', dp.data.garam === 'g-uji' && dp.data.acak === HASH_UJI && !/4321/.test(J(dp)), J(dp));
    ok('garam bawaan berbentuk garam sistem lama ("g" + base36)', /^g[0-9a-z]+$/.test((await susunPinOwner({ baru: '5555', ulang: '5555' }, W)).dokumen[0].data.garam));
    ok('pinOwnerBenar() index.html (acakPin sistem lama) menerima PIN baru dari dokumen /baru/, menolak PIN lain', (await acakPinLama('4321', dp.data.garam)) === dp.data.acak && (await acakPinLama('1234', dp.data.garam)) !== dp.data.acak);
    ok('PIN baru bukan 4–8 angka ditolak; ulangan beda ditolak', /4 sampai 8 angka/.test((await susunPinOwner({ baru: '12a4', ulang: '12a4' }, W)).tolak || '') && /4 sampai 8 angka/.test((await susunPinOwner({ baru: '123', ulang: '123' }, W)).tolak || '')
      && /tidak sama/.test((await susunPinOwner({ baru: '1234', ulang: '1235' }, W)).tolak || ''));
    pasok('pengaturan', [{ id: 'keamanan', garam: 'g-lama', acak: HASH_LAMA, diubahPada: '2026-08-14T07:14:56.013Z' }]);
    ok('PIN sudah disetel: PIN sekarang salah / kosong DITOLAK', /PIN sekarang salah/.test((await susunPinOwner({ lama: '1357', baru: '4321', ulang: '4321' }, W)).tolak || '') && /PIN sekarang salah/.test((await susunPinOwner({ baru: '4321', ulang: '4321' }, W)).tolak || ''));
    var G = await susunPinOwner({ lama: '2468', baru: '4321', ulang: '4321' }, W, 'g-uji');
    ok('PIN sudah disetel: PIN sekarang benar → diganti, garam baru', !G.tolak && G.dokumen[0].data.acak === HASH_UJI && G.dokumen[0].data.garam === 'g-uji' && opPinOwner().disetel === true, J(G));
    // ---- 6 · cadangan toko (lokal): dokumen sungguhan — hanya jumlah, tanpa nama/PIN
    if (ASLI) {
      pasok('pengaturan', [ASLI]); var DA = opDaftar(); var CA = susunCabutPinOperator(W);
      ok('DATA TOKO: PIN terbuka terhitung (' + DA.berPin + ' dari ' + DA.baris.length + ' operator); cabut → dokumen tanpa pin, jumlah operator & aktif/libur utuh',
        DA.berPin > 0 && !CA.tolak && !adaPin(CA.dokumen) && Object.keys(CA.dokumen[0].data.operator).length === DA.baris.length
        && DA.baris.every(function (b) { return CA.dokumen[0].data.operator[b.nama].aktif === b.aktif; }), 'jumlah saja');
    }
  } catch (e) { gagal.push('JATUH: ' + (e && (e.stack || e.message) || e)); }
  print(J({ lulus: lulus, gagal: gagal }));
})();
"""


def jalan_jsc(t):
    mi = modul_index(t)
    ko = kunci_obj(beku2.potong(mi, 'simpanModalJaga') or '', r"const data = \{ (id: 'aksesKasir', [^}]*) \};")
    kp = kunci_obj(beku2.potong(mi, 'simpanPinOwnerBaru') or '', r"const data = \{ (id: 'keamanan', [^}]*) \};")
    if not ko or not kp: return 0, ['bentuk dokumen simpanModalJaga / simpanPinOwnerBaru index.html tidak terbaca']
    acak_lama = beku2.potong(mi, 'acakPin')
    ks = t['kasir.html']; ik = beku2.potong(ks, 'infoOperator'); rk = beku2.potong(ks, 'rosterKasir')
    if not (acak_lama and ik and rk): return 0, ['acakPin (index.html) / infoOperator, rosterKasir (kasir.html) tidak ditemukan']
    js = '\n'.join([bundel_baru.PRELUDE, POLYFILL] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL])
    kasir = "var K_ROSTER = 'kasir_roster_v1';\n" + rk + '\n' + ik + '\n'
    asli = cadangan_akses()
    isi = (JAM + js + '\n' + acak_lama.replace('function acakPin(', 'function acakPinLama(', 1) + '\n' + kasir
           + 'var KUNCI_OPERATOR = ' + json.dumps(ko) + '; var KUNCI_PIN = ' + json.dumps(kp) + "; var HASH_UJI = '" + HASH_UJI + "'; var HASH_LAMA = '" + HASH_LAMA + "';\n"
           + 'var ASLI = ' + json.dumps(asli) + ';\n' + SKENARIO)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(isi); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(baris[-1]); return h['lulus'], h['gagal']


def periksa_statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    mi = modul_index(t)
    ok('acakPin /baru/ HURUF DEMI HURUF = acakPin() index.html', (beku2.potong(mi, 'acakPin') or 'A').strip() == (beku2.potong(t['baru/js/mesin/pembantu.js'], 'acakPin') or 'B').strip())
    tb = re.search(r"const TULIS_TERBUKA = \{([^}]*)\};", mi)
    ok('index.html: operator kasir & PIN owner TIDAK lagi di daftar tulis terbuka', tb and 'aksesKasir' not in tb.group(1) and 'keamanan' not in tb.group(1), tb.group(1) if tb else '')
    pj = {'bukaModalJaga': ("'aksesKasir'", 'rosterCache('), 'simpanModalJaga': ("'aksesKasir'", 'simpanKeFirestore('), 'bukaSetelPin': ("'keamanan'", 'pinSudahDisetel('),
          'simpanPinOwnerBaru': ("'keamanan'", 'simpanLokal(')}
    salah = []
    for f, (dok, sesudah) in pj.items():
        b = beku2.potong(mi, f) or ''; i = b.find("penjagaTulis('simpan', 'pengaturan', " + dok + ')')
        if i < 0 or i > b.find(sesudah): salah.append(f)
    ok('index.html: buka & simpan operator, buka setel PIN, simpan PIN owner bertanya ke penjaga SEBELUM apa pun diubah (salinan HP juga)', not salah, salah)
    mn = t['baru/js/layar/menu.js']
    ok('menu.js: tab "Kasir & PIN" di Peran & persetujuan; aksi memakai OP.susun*', "['kasir', 'Kasir & PIN']" in mn and 'OP.susunCabutPinOperator(waktu())' in mn and 'OP.susunOperatorAktif(' in mn and 'OP.susunOperatorHapus(' in mn and 'await OP.susunPinOwner(' in mn)
    ok('menu.js: TIDAK ada tombol/kolom tambah operator; layar menyebut terus terang daftar ini tidak sampai ke kasir mana pun', 'opTambah' not in mn and 'nama operator baru' not in mn and 'menambah nama tidak disediakan' in mn)
    ok('menu.js: kolom PIN berjenis sandi, angka, tanpa isi otomatis; isian PIN dijaga penjaga isian (ganti orang)', 'type="password" inputmode="numeric" autocomplete="off"' in mn and "['pinIsi', (v) =>" in mn)
    return out


def semua(ganti=None, bagian=('statis', 'jsc')):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        l, g = jalan_jsc(t); out += [('jsc · ' + x, False, '') for x in g] + [('__jsc', not g, l)]
    return out


KONTROL = [
    ('cabut PIN membiarkan pin', {'baru/js/layar/akses-kasir-logika.js': [("opDaftar().baris.forEach((b) => { o[b.nama] = { aktif: b.aktif }; }); ubah(o);", "Object.keys(opPeta()).forEach((n) => { o[n] = Object.assign({}, opPeta()[n]); }); ubah(o);")]}, ('jsc',)),
    ('daftar operator membawa isi PIN keluar', {'baru/js/layar/akses-kasir-logika.js': [(".map((n) => ({ nama: n, aktif: !o[n] || o[n].aktif !== false }));", ".map((n) => ({ nama: n, aktif: !o[n] || o[n].aktif !== false, pin: (o[n] || {}).pin }));")]}, ('jsc',)),
    ('dokumen operator berbentuk lain', {'baru/js/layar/akses-kasir-logika.js': [("data: { id: 'aksesKasir', operator: o, diubahPada: w.kini } }]", "data: { id: 'aksesKasir', daftar: o, diubahPada: w.kini } }]")]}, ('jsc',)),
    ('hapus operator tanpa ketukan kedua', {'baru/js/layar/akses-kasir-logika.js': [("if (!yakin) return { perluYakin: true };", "")]}, ('jsc',)),
    ('tombol tambah operator kembali (nama yang tidak sampai ke kasir mana pun)', {'baru/js/layar/menu.js': [("    opCabutPin: () => tulis(OP.susunCabutPinOperator(waktu())),", "    opCabutPin: () => tulis(OP.susunCabutPinOperator(waktu())),\n    opTambah: () => {},")]}, ('statis',)),
    ('PIN owner tersimpan terbuka', {'baru/js/layar/akses-kasir-logika.js': [("data: { id: 'keamanan', garam, acak, diubahPada: w.kini } }]", "data: { id: 'keamanan', garam, acak, pin: baru, diubahPada: w.kini } }]")]}, ('jsc',)),
    ('PIN owner diganti tanpa PIN sekarang', {'baru/js/layar/akses-kasir-logika.js': [("if (disetel && (!lama || (await acakPin(lama, d.garam)) !== d.acak)) return", "if (false) return")]}, ('jsc',)),
    ('PIN owner tanpa ulangan', {'baru/js/layar/akses-kasir-logika.js': [("if (baru !== ulang) return { tolak: 'Ulangan PIN tidak sama.' };", "")]}, ('jsc',)),
    ('acakPin /baru/ beda dari sistem lama', {'baru/js/mesin/pembantu.js': [("new TextEncoder().encode(String(garam) + '|' + String(pin));", "new TextEncoder().encode(String(pin) + '|' + String(garam));")]}, ('statis', 'jsc')),
    ('index.html: operator dibuka lagi', {'index.html': [("  const TULIS_TERBUKA = {};", "  const TULIS_TERBUKA = { 'pengaturan/aksesKasir': 'daftar & PIN operator kasir' };")]}, ('statis',)),
    ('index.html: PIN owner diubah di HP walau server menolak', {'index.html': [("    if (!penjagaTulis('simpan', 'pengaturan', 'keamanan')) throw galatHanyaBaca();   // 25c: diatur di /baru/ — salinan HP ini juga tidak diubah\n", "")]}, ('statis',)),
    ('menu: kolom PIN teks biasa', {'baru/js/layar/menu.js': [('type="password" inputmode="numeric" autocomplete="off"', 'type="text" inputmode="numeric"')]}, ('statis',)),
]

if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti, bagian in KONTROL:
            try: h = semua(ganti, bagian)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' · ' + str(e)[:120]); kode = 3; continue
            g = [x for x in h if not x[1]]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h = semua(); g = [x for x in h if not x[1]]
    n = sum(1 for x in h if x[1] and x[0] != '__jsc') + next((x[2] for x in h if x[0] == '__jsc'), 0)
    for x in g: print('   ✗ ' + x[0] + (' → ' + json.dumps(x[2], ensure_ascii=False)[:300] if x[2] not in ('', None) else ''))
    print('OPERATOR KASIR & PIN di /baru/ (25c)%s: %d lulus · %d gagal' % (' + dokumen toko dari cadangan' if cadangan_akses() else '', n, len(g)))
    sys.exit(1 if g else 0)
