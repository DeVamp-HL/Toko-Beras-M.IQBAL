#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
modul_es.py — pemuat modul ES mini untuk jsc: layar ASLI /baru/ (stok.js, harga.js, …) dijalankan dengan lingkup modul masing-masing.

Kenapa bukan bundel_baru.py: bundel_baru membuang semua `import` dan menaruh semua berkas di SATU lingkup — nama lokal dua layar bertabrakan
(tiap layar punya `gambar`, `set`, `st`, …), dan impor bernama lain (`import { a as b }`) hilang artinya. Di sini tiap berkas dibungkus
generatornya sendiri (lingkup modul utuh, 'use strict' seperti modul ES di peramban — mengubah objek beku MELEMPAR), fungsi yang diekspor tersedia
sebelum badan modul berjalan (siklus impor seperti ESM), dan tiap impor = variabel penutup yang disambung ulang sesudah semua modul jalan.
Baris berkas asli tetap (baris bundel = awal modul + baris − 1) supaya galat bisa dipetakan balik.

    from modul_es import bundel
    js, peta, urut = bundel(['baru/js/layar/stok.js', ...], tambah_depan='', ganti={'baru/js/data/toko.js': [(lama, baru)]})
    # modul tersedia di jsc sebagai __E['baru/js/data/toko.js'].namaEkspor; mengganti __E[m][f] lalu __sambungSemua() = membungkus fungsi itu untuk semua pengimpor
"""
import os, re

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
RX_IMPOR = re.compile(r"^import\s+(.*?)\s+from\s+'([^']+)';", re.M | re.S)
RX_IMPOR_POLOS = re.compile(r"^import\s+'([^']+)';", re.M)
RX_EKSPOR_DAFTAR = re.compile(r"^export\s*\{([^}]*)\}\s*;?", re.M)


def baca(f, akar=None):
    return open(os.path.join(akar or AKAR, f), encoding='utf-8').read()


def impor(f, teks):
    return [os.path.normpath(os.path.join(os.path.dirname(f), m.group(2))) for m in RX_IMPOR.finditer(teks)]


def urut_evaluasi(lihat, mulai):
    """Urutan ESM: pasca-urut DFS, impor dikunjungi berurutan; siklus = modul yang sedang berjalan dilewati."""
    keadaan, out = {}, []
    def kunjungi(f):
        keadaan[f] = 1
        for g in lihat[f]:
            if g not in keadaan: kunjungi(g)
        keadaan[f] = 2; out.append(f)
    for m in mulai:
        if m not in keadaan: kunjungi(m)
    return out


def ganti_sama_baris(teks, m, isi=''):
    return teks[:m.start()] + isi + '\n' * teks[m.start():m.end()].count('\n') + teks[m.end():]


def ubah(f, teks):
    """Satu berkas → kode bungkus (jumlah baris sama dengan aslinya; kepala & ekor di baris pertama/terakhir)."""
    pengikat = []   # (namaLokal, modul, namaEkspor | None = namespace)
    while True:
        m = RX_IMPOR.search(teks)
        if not m: break
        spes, dari = m.group(1).strip(), os.path.normpath(os.path.join(os.path.dirname(f), m.group(2)))
        mns = re.match(r'^\*\s+as\s+(\w+)$', spes)
        if mns: pengikat.append((mns.group(1), dari, None))
        else:
            mb = re.match(r'^(?:(\w+)\s*,\s*)?\{(.*)\}$', spes, re.S)
            if not mb: raise SystemExit('impor tak dikenal di ' + f + ': ' + spes)
            if mb.group(1): pengikat.append((mb.group(1), dari, 'default'))
            for x in [y.strip() for y in mb.group(2).replace('\n', ' ').split(',') if y.strip()]:
                a = re.match(r'^(\w+)(?:\s+as\s+(\w+))?$', x)
                pengikat.append((a.group(2) or a.group(1), dari, a.group(1)))
        teks = ganti_sama_baris(teks, m)
    while True:
        m = RX_IMPOR_POLOS.search(teks)
        if not m: break
        teks = ganti_sama_baris(teks, m)
    ekspor = []   # (namaEkspor, namaLokal)
    while True:
        m = RX_EKSPOR_DAFTAR.search(teks)
        if not m: break
        for x in [y.strip() for y in m.group(1).replace('\n', ' ').split(',') if y.strip()]:
            a = re.match(r'^(\w+)(?:\s+as\s+(\w+))?$', x); ekspor.append((a.group(2) or a.group(1), a.group(1)))
        teks = ganti_sama_baris(teks, m)
    fungsi = set()
    for m in re.finditer(r'^export\s+(?:async\s+)?function\s*\*?\s*(\w+)', teks, re.M): ekspor.append((m.group(1), m.group(1))); fungsi.add(m.group(1))
    for m in re.finditer(r'^export\s+(?:const|let|var|class)\s+(\w+)', teks, re.M): ekspor.append((m.group(1), m.group(1)))
    if re.search(r'^export\s+default', teks, re.M): raise SystemExit('export default di ' + f)
    teks = re.sub(r'^export\s+(?=(?:async\s+)?function|const\b|let\b|var\b|class\b)', '', teks, flags=re.M)
    for e, l in ekspor:   # fungsi lokal yang diekspor lewat export { … } juga terangkat
        if re.search(r'^(?:async\s+)?function\s*\*?\s*' + re.escape(l) + r'\b', teks, re.M): fungsi.add(l)
    nama_var = sorted(set(n for n, _, _ in pengikat))
    sambung = ' '.join(('%s = __E[%r];' % (n, d)) if e is None else ('%s = __E[%r].%s;' % (n, d, e)) for n, d, e in pengikat)
    fn = ', '.join('%s: %s' % (e, l) for e, l in ekspor if l in fungsi)
    kepala = ("__def(%r, function* () { 'use strict'; %s yield { fn: function () { return { %s }; }, link: function () { %s } }; "
              % (f, ('var ' + ', '.join(nama_var) + ';') if nama_var else '', fn, sambung))
    ekor = '\n;return { %s };\n});\n' % ', '.join('%s: %s' % (e, l) for e, l in ekspor)
    return kepala + teks + ekor


PEMUAT = r"""
var __E = {}, __G = {}, __Y = {};
function __def(id, gen) { __G[id] = gen; __E[id] = __E[id] || {}; }
function __sambungSemua() { Object.keys(__Y).forEach(function (id) { __Y[id].y.link(); }); }
function __lade(urut) {
  urut.forEach(function (id) { var g = __G[id](); var y = g.next().value; __Y[id] = { g: g, y: y }; Object.assign(__E[id], y.fn()); });
  __sambungSemua();
  urut.forEach(function (id) { __Y[id].y.link(); var r = __Y[id].g.next(); Object.assign(__E[id], r.value); });
  __sambungSemua();
}
"""


def bundel(mulai, tambah_depan='', ganti=None, akar=None):
    """→ (js, peta, urut). peta = [(baris_awal_bundel, berkas, n_baris)]. ganti = {berkas: [(lama, baru)]} — tiap `lama` wajib tepat SATU kali (kontrol basi = AssertionError)."""
    lihat, antre, teks = {}, list(mulai), {}
    while antre:
        f = antre.pop(0)
        if f in lihat: continue
        t = baca(f, akar)
        for lama, baru in (ganti or {}).get(f, []):
            assert t.count(lama) == 1, 'kontrol basi: ' + f + ' · ' + lama[:90] + ' (' + str(t.count(lama)) + '×)'
            t = t.replace(lama, baru)
        teks[f] = t; lihat[f] = impor(f, t); antre += lihat[f]
    for f in (ganti or {}):
        assert f in teks, 'kontrol basi: ' + f + ' tidak termuat'
    urut = urut_evaluasi(lihat, mulai)
    bagian = [tambah_depan, PEMUAT]; peta = []
    baris = sum(x.count('\n') for x in bagian) + 1
    for f in urut:
        kode = ubah(f, teks[f])
        peta.append((baris, f, kode.count('\n')))
        bagian.append(kode); baris += kode.count('\n')
    bagian.append('\n__lade(%s);\n' % repr(urut).replace("'", '"'))
    return ''.join(bagian), peta, urut


def petakan(peta, baris):
    for awal, f, n in peta:
        if awal <= baris < awal + n + 1: return f, baris - awal + 1
    return None, baris
