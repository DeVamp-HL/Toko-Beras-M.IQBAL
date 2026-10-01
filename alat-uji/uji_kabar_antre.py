#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_kabar_antre.py — audit 39b no. 28: kabar sesudah kiriman TIDAK berkata "Tercatat" selama server belum mengaku. Statis + jsc, tanpa peramban.
KOTAK PASIR (angka & nama CONTOH, bukan data toko), jam dikunci Kamis 24 Sep 2026 10:00 WIB.
  · toko.js: kabarKiriman(x, kabar) = SATU kalimat untuk semua layar — server mengaku → kabar apa adanya; antre → "Tersimpan di perangkat, menunggu server"
    (kata Tercatat/Tersimpan di depan kabar dibuang); simulasi cadangan → "SIMULASI — ".
  · toko.js: kiriman bertahap membawa tanda antre (dulu potongan yang masih antre dihitung "selesai" tanpa tanda).
  · penolong tulis ENAM layar (Stok, Uang, Harga, Pelanggan, Menu, Laporan) + panel isi ulang wadah di Jual (tulisWadah) + Menu "lanjutkan bertahap":
    fungsinya diambil dari sumber dan dijalankan di jsc atas toko.js yang sungguhan, penulis Firestore diganti tiruan (antre / ok / ditolak).
  · app.js: pil kepala (statusRingkas) menyebut kiriman yang DITOLAK server; layar Pelanggan ikut digambar ulang saat keadaan sambungan berubah.

    python3 alat-uji/uji_kabar_antre.py            → N lulus · 0 gagal
    python3 alat-uji/uji_kabar_antre.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/arsip-logika.js', 'baru/js/layar/harga-logika.js', 'baru/js/layar/bon-pemasok-logika.js',
                                  'baru/js/layar/uang-logika.js']
LAYAR = ['stok', 'uang', 'harga', 'pelanggan', 'menu', 'laporan', 'jual']
BERKAS = MODUL + ['baru/js/app.js'] + ['baru/js/layar/%s.js' % n for n in LAYAR]
JAM = "var __KINI = new Date('2026-09-24T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def baca(ganti=None):
    t = {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in BERKAS}
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def potong(teks, pola):
    m = re.search(pola, teks, re.S)
    return m.group(1) if m else ''


def penolong(t):
    """Sumber penolong tulis tiap layar (fungsi bersarang di pasangLayar…, indentasi dua spasi) → {nama: teks}."""
    P = {}
    for n in ['stok', 'uang', 'harga', 'pelanggan', 'menu', 'laporan']:
        P[n] = potong(t['baru/js/layar/%s.js' % n], r'\n(  async function tulis\(r(?:, tanpaKabar)?\) \{\n.*?\n  \}\n)')
    P['wadah'] = potong(t['baru/js/layar/jual.js'], r'\n(  async function tulisWadah\(r\) \{\n.*?\n  \}\n)')
    # saudara di Jual dengan cacat sebentuk (ikut ditambal di cabang no. 28): tulisUmum, tulisSetelan, tulisPesanan, kirimUrung
    for n, f in (('jualUmum', 'tulisUmum\\(r\\)'), ('jualSetelan', 'tulisSetelan\\(r\\)'), ('jualPesanan', 'tulisPesanan\\(r\\)'), ('jualUrung', 'kirimUrung\\(r, tambah\\)')):
        P[n] = potong(t['baru/js/layar/jual.js'], r'\n(  async function ' + f + r' \{\n.*?\n  \}\n)')
    return P


SKENARIO = r"""
var CEK = [], J = JSON.stringify;
function ok(nama, syarat, ket) { CEK.push([nama, !!syarat, syarat ? '' : String(ket || '')]); }
var ANTRE = 'Tersimpan di perangkat, menunggu server';
var PENULIS = { antre: { tulis: function () { return Promise.resolve({ antre: true }); } }, ok: { tulis: function () { return Promise.resolve({ ok: true }); } },
  tolak: { tulis: function () { return Promise.resolve({ gagal: true, pesan: 'tulis ditolak: permission-denied' }); } } };
var DOK = function (id) { return [{ koleksi: 'pengeluaranHarian', data: { id: id, kategori: 'toko', tanggal: '2026-09-24', jam: '10:00', keterangan: 'Contoh', nominal: 1000 } }]; };
var R_CONTOH = function () { return { dokumen: DOK('c-' + Math.random()), patch: { kabar: 'Tercatat · contoh 1.000' } }; };
// bentuk susunan bertahap yang sungguhan (pelanggan-logika SATUKAN / hapus nama, stok koreksi adukan): dokumen + hapus + kelompok
var R_KELOMPOK = function () { var a = DOK('k1-' + Math.random()), b = DOK('k2-' + Math.random()); return { dokumen: a.concat(b), hapus: [], kelompok: [{ dokumen: a, hapus: [] }, { dokumen: b, hapus: [] }], judulBertahap: 'Contoh bertahap', patch: { kabar: 'Tercatat · contoh bertahap' } }; };

// ---- 1 · kalimat bersama (toko.js)
var adaKK = typeof kabarKiriman === 'function';
ok('toko.js: kabarKiriman ada (satu kalimat kiriman untuk semua layar)', adaKK);
if (adaKK) {
  ok('kabarKiriman: server mengaku → kabar apa adanya; antre → "' + ANTRE + ' — …" dan kata Tercatat di depan dibuang; simulasi → "SIMULASI — "; kabar "Tersimpan" saja → kalimat antre saja',
    kabarKiriman({ ok: true }, 'Tercatat · Kasbon 1') === 'Tercatat · Kasbon 1' && kabarKiriman({ antre: true }, 'Tercatat · Kasbon 1') === ANTRE + ' — Kasbon 1'
    && kabarKiriman({ simulasi: true }, 'Tercatat · Kasbon 1') === 'SIMULASI — Tercatat · Kasbon 1' && kabarKiriman({ antre: true }, 'Tersimpan') === ANTRE
    && kabarKiriman(null, 'Rework tercatat: 2 kg') === 'Rework tercatat: 2 kg' && kabarKiriman({ antre: 2 }, 'Rework tercatat: 2 kg') === ANTRE + ' — Rework tercatat: 2 kg',
    J([kabarKiriman({ antre: true }, 'Tercatat · Kasbon 1'), kabarKiriman({ antre: true }, 'Tersimpan')]));
}

// ---- 2 · kiriman bertahap membawa tanda antre
var BT = {};
setelPenulis(PENULIS.antre); tulisBertahap('uji antre', R_KELOMPOK().kelompok).then(function (r) { BT.antre = r; });
drainMicrotasks(); setelPenulis(PENULIS.ok); tulisBertahap('uji ok', R_KELOMPOK().kelompok).then(function (r) { BT.ok = r; }); drainMicrotasks(); setelPenulis(null);
ok('bertahap: potongan yang masih antre → hasil membawa antre (dulu "ok" polos = layar berkata selesai); server mengaku → tanpa antre',
  !!BT.antre && BT.antre.ok === true && BT.antre.antre > 0 && !!BT.ok && BT.ok.ok === true && !BT.ok.antre, J(BT));

// ---- 3 · penolong tulis tiap layar (sumber asli, toko.js asli, penulis tiruan)
var HASIL = {};
function coba(nama, buat, keadaan, r) {
  var kabar = {}; var set = function (p) { Object.assign(kabar, p); };
  var f = buat(set); setelPenulis(PENULIS[keadaan]);
  var jadi; f(r).then(function (x) { jadi = x; }); drainMicrotasks(); setelPenulis(null);
  HASIL[nama + '|' + keadaan] = { kabar: String(kabar.kabar || ''), awas: !!kabar.kabarAwas, jadi: jadi };
  return HASIL[nama + '|' + keadaan];
}
PENOLONG.forEach(function (p) {
  if (!p.buat) { ok('penolong tulis ' + p.nama + ' terbaca dari sumber', false); return; }
  var A = coba(p.nama, p.buat, 'antre', R_CONTOH()), O = coba(p.nama, p.buat, 'ok', R_CONTOH()), T = coba(p.nama, p.buat, 'tolak', R_CONTOH());
  ok(p.nama + ': kiriman antre → kabar "' + ANTRE + '", tanpa "Tercatat"; server mengaku → kabar susunan apa adanya; ditolak → DITOLAK (awas)',
    A.kabar.indexOf(ANTRE) === 0 && A.kabar.indexOf('Tercatat') < 0 && /contoh 1\.000/.test(A.kabar) && O.kabar === 'Tercatat · contoh 1.000' && /^DITOLAK/.test(T.kabar) && T.awas, J([A.kabar, O.kabar, T.kabar]));
  if (p.bertahap) { var B = coba(p.nama + '-bertahap', p.buat, 'antre', R_KELOMPOK()); var BO = coba(p.nama + '-bertahap', p.buat, 'ok', R_KELOMPOK());
    ok(p.nama + ': jalur BERTAHAP (r.kelompok) yang masih antre → kabar antre; yang sampai → kabar apa adanya', B.kabar.indexOf(ANTRE) === 0 && B.kabar.indexOf('Tercatat') < 0 && BO.kabar.indexOf('Tercatat · contoh bertahap') === 0, J([B.kabar, BO.kabar])); }
});
var U = susunKeluar({ untuk: 'toko', dari: 'dompet', perlu: 'Bensin antar', ketik: '30.000' }, { tanggal: '2026-09-24', jam: '10:00', kini: '2026-09-24T03:00:00.000Z', idUnik: function () { return 'u-' + Math.random(); } });
var pUang = PENOLONG.filter(function (p) { return p.nama === 'uang'; })[0];
if (pUang && pUang.buat) { var UA = coba('uang-susunKeluar', pUang.buat, 'antre', U), UO = coba('uang-susunKeluar', pUang.buat, 'ok', U);
  ok('Uang › uang keluar (susunKeluar asli): kabar susunan "Tercatat · …"; selama antre layar berkata menunggu server', /^Tercatat · /.test(U.patch.kabar) && UA.kabar.indexOf(ANTRE + ' — ') === 0 && UA.kabar.indexOf('Tercatat') < 0 && UO.kabar === U.patch.kabar, J([U.patch.kabar, UA.kabar])); }

// ---- 4 · Menu › lanjutkan kiriman bertahap
if (LANJUT) {
  var lanjut = function (keadaan) { var kabar = {}; var set = function (p) { Object.assign(kabar, p); };
    simpanBertahapUji({ id: 'bt-uji', judul: 'Contoh bertahap', pada: '2026-09-24T03:00:00.000Z', potongan: [{ dokumen: DOK('l1-' + keadaan), hapus: [] }, { dokumen: DOK('l2-' + keadaan), hapus: [] }], sudah: 0 });
    var f = LANJUT(set); setelPenulis(PENULIS[keadaan]); f(); drainMicrotasks(); setelPenulis(null); return String(kabar.kabar || ''); };
  var LA = lanjut('antre'), LO = lanjut('ok');
  ok('Menu › lanjutkan bertahap: potongan antre → kabar menunggu server, bukan "selesai" polos; sampai → "Kiriman bertahap selesai"', LA.indexOf(ANTRE) === 0 && /^Kiriman bertahap selesai/.test(LO), J([LA, LO]));
} else ok('Menu: penangan lanjutBertahap terbaca dari sumber', false);

// ---- 5 · pil kepala (app.js statusRingkas)
var PIL = {};
if (typeof statusRingkas === 'function') {
  var pil = function (nama, fb) { statusFb = fb; PIL[nama] = statusRingkas(); };
  var dasar = { masuk: true, koleksiSiap: 56, koleksiTotal: 56, menunggu: 0, offline: false, galat: '', ditolak: [], lokal: { belum: 0, ditolak: 0 } };
  pil('normal', dasar); pil('menunggu', Object.assign({}, dasar, { menunggu: 1, lokal: { belum: 1, ditolak: 0 } })); pil('memuat', Object.assign({}, dasar, { koleksiSiap: 10 }));
  pil('ditolak', Object.assign({}, dasar, { galat: 'tulis ditolak: permission-denied', lokal: { belum: 0, ditolak: 2 } })); pil('ditolakOffline', Object.assign({}, dasar, { offline: true, lokal: { belum: 3, ditolak: 1 } }));
  ok('pil: kiriman DITOLAK server tampil di pil tiap layar ("2 DITOLAK server"), juga tanpa internet; normal / menunggu / memuat tidak berubah',
    PIL.normal === 'OWNER' && PIL.menunggu === 'OWNER · menunggu server' && PIL.memuat === 'OWNER · memuat…' && PIL.ditolak === 'OWNER · 2 DITOLAK server' && PIL.ditolakOffline === 'OWNER · 1 DITOLAK server · tanpa internet', J(PIL));
} else ok('app.js: statusRingkas terbaca', false);
print(J({ cek: CEK, contoh: HASIL['uang-susunKeluar|antre'] || null }));
"""


def susun(t):
    js = _bundel(t)
    P = penolong(t); bagian = []
    for n in ['stok', 'uang', 'harga', 'pelanggan', 'menu', 'laporan', 'wadah', 'jualUmum', 'jualSetelan', 'jualPesanan', 'jualUrung']:
        nama_f = {'wadah': 'tulisWadah', 'jualUmum': 'tulisUmum', 'jualSetelan': 'tulisSetelan', 'jualPesanan': 'tulisPesanan', 'jualUrung': 'kirimUrung'}.get(n, 'tulis')
        buat = ('function (set) {\n' + P[n] + '\n  return ' + nama_f + ';\n}') if P[n] else 'null'
        bagian.append('{ nama: %s, bertahap: %s, buat: %s }' % (json.dumps(n), 'true' if n in ('stok', 'pelanggan') else 'false', buat))
    lanjut = potong(t['baru/js/layar/menu.js'], r'\n    lanjutBertahap: (async \(\) => \{.*?\}),\n')
    app = t['baru/js/app.js']
    label = potong(app, r'\n(const labelAkun = \(\) => \{.*?\};\n)'); ringkas = potong(app, r'\n(function statusRingkas\(\) \{\n.*?\n\}\n)')
    stub = ("var statusFb = {}; function akunKini() { return { jenis: 'owner', nama: 'Owner' }; } function bisaBekerja() { return true; }\n"
            "function simpanBertahapUji(r) { localStorage.setItem(KUNCI_BERTAHAP, JSON.stringify(r)); }\n")
    return (JAM + js + '\n' + stub + label + ringkas + '\nvar PENOLONG = [' + ',\n'.join(bagian) + '];\n'
            + 'var LANJUT = ' + (('function (set) { return ' + lanjut + '; }') if lanjut else 'null') + ';\n' + SKENARIO)


def _bundel(t):
    return '\n'.join([bundel_baru.PRELUDE] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL])


def jsc(kode):
    fd, p = tempfile.mkstemp(suffix='.js'); os.write(fd, kode.encode('utf-8')); os.close(fd)
    try:
        r = subprocess.run([JSC, p], capture_output=True, text=True, timeout=60, env=dict(os.environ, TZ='Asia/Jakarta'))
        return r.stdout.strip(), r.stderr.strip()
    finally: os.unlink(p)


def periksa(t):
    c = []
    out, err = jsc(susun(t))
    try: H = json.loads(out.split('\n')[-1])
    except Exception: return [('jsc jalan', False, (err or out)[:600])], None
    c += [(n, ok, k) for n, ok, k in H['cek']]
    jl = t['baru/js/layar/jual.js']
    c.append(('Jual › batalkan nota & retur tanpa nota: kabar lewat kabarKiriman (antre = menunggu server), tidak ada lagi "SIMULASI —" buatan sendiri untuk kiriman',
              "kabar: kabarKiriman(h, 'Nota dibatalkan — '" in jl and "(h && h.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar" not in jl, ''))
    app = t['baru/js/app.js']
    c.append(('app.js: layar Pelanggan ikut digambar ulang saat keadaan sambungan berubah (pilnya ikut berganti)', re.search(r'const GAMBAR_STATUS = \[[^\]]*\bpelanggan\.gambar\b', app) is not None, ''))
    return c, H.get('contoh')


KONTROL = [
    ('bertahap membuang tanda antre', {'baru/js/data/toko.js': [("if (h && h.antre) antre += 1;", '')]}),
    ('kalimat bersama memperlakukan antre = sampai', {'baru/js/data/toko.js': [("if (!(x && x.antre)) return k;", 'return k;')]}),
    ('kalimat bersama tidak membuang "Tercatat"', {'baru/js/data/toko.js': [("const sisa = k.replace(/^(Tercatat|Tersimpan)(\\s*[·—:.]\\s*|$)/, '');", 'const sisa = k;')]}),
    ('Stok kembali ke kabar lama', {'baru/js/layar/stok.js': [("kabar: kabarKiriman(x, r.patch.kabar) + (x && x.potongan > 1", "kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar + (x && x.potongan > 1")]}),
    ('Uang kembali ke kabar lama', {'baru/js/layar/uang.js': [("kabar: kabarKiriman(x, (r.patch || {}).kabar || ''), kabarAwas", "kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + ((r.patch || {}).kabar || ''), kabarAwas")]}),
    ('Harga kembali ke kabar lama', {'baru/js/layar/harga.js': [("kabar: kabarKiriman(x, (r.patch || {}).kabar || ''), kabarAwas", "kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + ((r.patch || {}).kabar || ''), kabarAwas")]}),
    ('Pelanggan kembali ke kabar lama', {'baru/js/layar/pelanggan.js': [("kabar: kabarKiriman(x, (r.patch && r.patch.kabar) || 'Tersimpan') + (tahap > 1", "kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + ((r.patch && r.patch.kabar) || 'Tersimpan') + (tahap > 1")]}),
    ('Menu kembali ke kabar lama', {'baru/js/layar/menu.js': [("kabar: kabarKiriman(x, (r.patch && r.patch.kabar) || 'Tersimpan') })); return true; }", "kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + ((r.patch && r.patch.kabar) || 'Tersimpan') })); return true; }")]}),
    ('Laporan kembali ke kabar lama', {'baru/js/layar/laporan.js': [("kabar: kabarKiriman(x, (r.patch || {}).kabar || ''), kabarAwas", "kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + ((r.patch || {}).kabar || ''), kabarAwas")]}),
    ('panel isi ulang wadah (Jual) kembali ke kabar lama', {'baru/js/layar/jual.js': [("set(Object.assign({}, r.patch, { kabar: kabarKiriman(x, r.patch.kabar) })); return true; }", "set(Object.assign({}, r.patch, { kabar: (x && x.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar })); return true; }")]}),
    ('Menu lanjutkan bertahap berkata selesai polos', {'baru/js/layar/menu.js': [("kabarKiriman(r, 'Kiriman bertahap selesai (' + (r.total || 0) + ' tahap)')", "'Kiriman bertahap selesai (' + (r.total || 0) + ' tahap)'")]}),
    ('Jual tulisUmum kembali ke kabar lama', {'baru/js/layar/jual.js': [("      if (h && h.gagal) return set({ kabar: 'DITOLAK: ' + h.pesan, kabarAwas: true });\n      set(Object.assign({}, r.patch, { kabar: kabarKiriman(h, r.patch.kabar) }));\n    } catch (e) { set({ kabar: 'GAGAL menulis: '", "      if (h && h.gagal) return set({ kabar: 'DITOLAK: ' + h.pesan, kabarAwas: true });\n      set(Object.assign({}, r.patch, { kabar: (h && h.simulasi ? 'SIMULASI — ' : '') + r.patch.kabar }));\n    } catch (e) { set({ kabar: 'GAGAL menulis: '")]}),
    ('Jual tarik balik rincian kembali ke kabar lama', {'baru/js/layar/jual.js': [("{ kabar: kabarKiriman(h, r.patch.kabar + (h && h.potongan > 1 ? ' (dikirim ' + h.potongan + ' tahap)' : '')) }", "{ kabar: r.patch.kabar }")]}),
    ('Jual batalkan nota kembali ke kabar lama', {'baru/js/layar/jual.js': [("kabar: kabarKiriman(h, 'Nota dibatalkan — '", "kabar: ('Nota dibatalkan — '")]}),
    ('pil tidak menyebut yang ditolak', {'baru/js/app.js': [("(tolak ? ' · ' + tolak + ' DITOLAK server' : '') + kirim", 'kirim')]}),
    ('pil: ditolak menelan "tanpa internet"', {'baru/js/app.js': [("(tolak ? ' · ' + tolak + ' DITOLAK server' : '') + kirim", "(tolak ? ' · ' + tolak + ' DITOLAK server' : kirim)")]}),
    ('Pelanggan tidak digambar ulang saat status berubah', {'baru/js/app.js': [('stok.gambar, pelanggan.gambar, menu.gambar', 'stok.gambar, menu.gambar')]}),
]


def main():
    if not os.path.exists(JSC): print('jsc tidak ada — uji dilewati' + (' (CI: GAGAL)' if os.environ.get('CI') else '')); return 2 if os.environ.get('CI') else 0
    if '--kontrol' in sys.argv:
        diam = []; dasar = {n for n, ok, k in periksa(baca())[0] if ok}
        for nama, g in KONTROL:
            gagal = [n for n, ok, k in periksa(baca(g))[0] if not ok and (n in dasar or n == 'jsc jalan')]
            print(('BERBUNYI ' if gagal else 'DIAM     ') + nama + ('  → ' + gagal[0][:110] if gagal else ''))
            if not gagal: diam.append(nama)
        print('kontrol: %d/%d berbunyi' % (len(KONTROL) - len(diam), len(KONTROL))); return 3 if diam else 0
    hasil, contoh = periksa(baca())
    for n, ok, k in hasil:
        if not ok: print('GAGAL:', n, '→', str(k)[:400])
    if contoh: print('contoh Uang (antre):', contoh['kabar'])
    lulus = sum(1 for _, ok, _ in hasil if ok); print('%d lulus · %d gagal' % (lulus, len(hasil) - lulus))
    return 0 if lulus == len(hasil) else 1


if __name__ == '__main__':
    sys.exit(main())
