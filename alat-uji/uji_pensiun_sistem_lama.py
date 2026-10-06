#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_pensiun_sistem_lama.py — PENSIUN SISTEM LAMA & kasir.html (owner 3 Okt 2026: "bumi hanguskan"). Statis, tanpa peramban, tanpa jsc.

index.html & kasir.html di akar kini halaman PENGALIH ke baru/ (CSP & isinya dijaga uji_csp.py). Versi terakhir keduanya utuh di tag git
sistem-lama-terakhir (commit 48a694d; jalan mundur docs/prosedur-pulih-darurat.md). Yang dijaga di sini = tidak ada yang masih MENUNJUK berkas
yang ikut dihapus, dan HP kasir tidak tertahan di versi lama:
  · pengalih ADA (bukan dihapus): perangkat tanpa service worker yang membuka alamat lama tidak kena 404
  · sw-kasir.js: tiap berkas di FILES ADA di repo (satu saja hilang → cache.addAll ditolak, SW baru tidak pernah terpasang, HP penjaga terjebak di
    versi lama tanpa tanda); kasir.html TIDAK di FILES maupun HTML_SWR (pengalih selalu dari jaringan, tidak dari cache); HTML_SWR ⊆ FILES;
    fetch berhenti untuk berkas di luar FILES; activate menghapus cache yang namanya ≠ VERSI (cache lama berisi kasir.html lama ikut hilang)
  · langkah CI (pages.yml, uji-beban-peramban.yml, hawkscan.yml, gladi-tutup-buku.yml — baris perintah & paths, bukan komentar) hanya menunjuk alat-uji/ yang ADA,
    dan berkas yang di-shasum uji beban ADA (langkah yang menunjuk berkas hilang = main tidak terbit)
  · seed HawkScan (.github/stackhawk.yml) dan manifest-sistem.json (ikon, start_url) menunjuk berkas yang ADA
  · /baru/ tidak lagi menautkan sistem lama (../index.html)
  · (owner 7 Okt) 404.html ADA: pengalih tanpa script ke jalur penuh situs /Toko-Beras-M.IQBAL/baru/, tidak di FILES service worker
Versi kasir (sw = kasir darurat = KK_VERSI_KASIR_TERBARU) dijaga uji_antrean_kasir.py & uji_katalog_kasir.py (job uji-peramban).

    python3 alat-uji/uji_pensiun_sistem_lama.py            → N lulus · 0 gagal
    python3 alat-uji/uji_pensiun_sistem_lama.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, glob, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
PENGALIH = ['index.html', 'kasir.html']
WORKFLOW = ['.github/workflows/pages.yml', '.github/workflows/uji-beban-peramban.yml', '.github/workflows/hawkscan.yml', '.github/workflows/gladi-tutup-buku.yml']
BERKAS = PENGALIH + WORKFLOW + ['sw-kasir.js', '.github/stackhawk.yml', 'manifest-sistem.json', 'baru/index.html', '404.html']
# owner 7 Okt (sisa pensiun #103): 404.html = pengalih untuk alamat yang tidak ada (berkas yang dihapus bersama sistem lama, tautan lama di HP).
# Disajikan di jalur mana pun → tujuannya jalur penuh situs; CSP & isinya dijaga uji_csp.py, keberadaannya & tujuannya di sini.
TUJUAN_404 = '/Toko-Beras-M.IQBAL/baru/'


def baca(ganti=None):
    """{berkas: isi}; isi None = berkas tidak ada. ganti = {berkas: [(lama, baru)] | None (= berkas dihapus)} untuk kontrol."""
    t = {}
    for b in BERKAS + sorted(os.path.relpath(p, AKAR) for p in glob.glob(os.path.join(AKAR, 'baru/js/**/*.js'), recursive=True)):
        p = os.path.join(AKAR, b)
        t[b] = open(p, encoding='utf-8').read() if os.path.isfile(p) else None
    for b, pasangan in (ganti or {}).items():
        if pasangan is None: t[b] = None; continue
        for lama, baru in pasangan:
            assert t[b] is not None and t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str((t[b] or '').count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def ada(rel, t):
    """Berkas ada: di salinan teks (kalau ikut dibaca) atau di repo."""
    rel = rel.split('?')[0].split('#')[0]
    if rel in t: return t[rel] is not None
    return os.path.isfile(os.path.join(AKAR, rel))


def daftar_js(sw, nama):
    m = re.search(r'const ' + nama + r' = \[([^\]]*)\];', sw)
    return re.findall(r"'([^']+)'", m.group(1)) if m else None


def periksa(t):
    out = []; ok = lambda n, c, k='': out.append((n, bool(c), k))
    for b in PENGALIH:
        ok(b + ': halaman pengalih ADA (tidak dihapus — perangkat tanpa service worker tidak kena 404)', t.get(b) is not None)
    h4 = t.get('404.html')
    ok('404.html: pengalih ADA — alamat yang ikut hilang bersama sistem lama (lib/, manifest kasir, ikon besar, tautan lama di HP) tidak berhenti di 404 polos', h4 is not None)
    ok('404.html: tanpa script, meta refresh & tombol ke jalur penuh situs ' + TUJUAN_404 + ' (bukan "baru/" relatif yang meleset di alamat dalam)',
       h4 is not None and '<script' not in h4.lower() and '<meta http-equiv="refresh" content="0; url=' + TUJUAN_404 + '">' in h4 and '<a href="' + TUJUAN_404 + '">' in h4)
    # ---- service worker kasir
    sw = t['sw-kasir.js'] or ''
    F, H = daftar_js(sw, 'FILES'), daftar_js(sw, 'HTML_SWR')
    ok('sw-kasir.js: FILES & HTML_SWR terbaca', F is not None and H is not None, [F, H])
    F, H = F or [], H or []
    hilang = [f for f in F if not ada(f, t)]
    ok('sw-kasir.js: tiap berkas di FILES ADA di repo — satu hilang = install ditolak, HP tertahan di versi lama', F and not hilang, [len(F), hilang])
    ok('sw-kasir.js: kasir.html TIDAK di FILES maupun HTML_SWR (pengalih selalu dari jaringan, tidak disajikan dari cache)', 'kasir.html' not in F + H, [F, H])
    ok('sw-kasir.js: 404.html TIDAK di FILES (pengalih alamat hilang selalu dari jaringan)', '404.html' not in F + H, [F, H])
    ok('sw-kasir.js: HTML_SWR bagian dari FILES', all(h in F for h in H), H)
    i_luar = sw.find('  if (!FILES.includes(nama)) return;\n'); i_jawab = sw.find('e.respondWith(')
    ok('sw-kasir.js: fetch berhenti untuk berkas di luar FILES SEBELUM menjawab dari cache', 0 <= i_luar < i_jawab, [i_luar, i_jawab])
    ok('sw-kasir.js: activate menghapus cache yang namanya ≠ VERSI (cache lama berisi kasir.html lama ikut hilang)', 'ks.filter((k) => k !== VERSI).map((k) => caches.delete(k))' in sw)
    # ---- langkah CI: perintah & paths, bukan komentar / nama langkah
    salah = []
    for w in WORKFLOW:
        isi = t.get(w)
        if isi is None: salah.append(w + ' (tidak ada)'); continue
        for no, baris in enumerate(isi.split('\n'), 1):
            s = baris.strip()
            if not s or s.startswith('#') or s.startswith('- name:') or s.startswith('name:'): continue
            for r in re.findall(r'(?<![\w/.-])(alat-uji/[\w./-]+)', s):
                if not ada(r.rstrip('.'), t): salah.append('%s:%d %s' % (w, no, r))
            m = re.search(r'shasum -a 256 (.+)$', s)
            if m:
                for f in m.group(1).split():
                    if not ada(f, t): salah.append('%s:%d shasum %s' % (w, no, f))
    ok('langkah CI hanya menunjuk berkas yang ADA (alat-uji/…, berkas yang di-shasum uji beban)', not salah, salah)
    # ---- HawkScan & manifest
    sh = t.get('.github/stackhawk.yml') or ''
    blok = re.search(r'seedPaths:\n((?:\s+(?:- .*|#.*)\n)+)', sh)
    seed = re.findall(r'^\s+- (/\S*)', blok.group(1), re.M) if blok else []
    hs = [s for s in seed if not ada((s.lstrip('/') + 'index.html') if s.endswith('/') else s.lstrip('/'), t)]
    ok('seed HawkScan (stackhawk.yml) menunjuk berkas yang ADA', seed and not hs, [len(seed), hs])
    try: mf = json.loads(t.get('manifest-sistem.json') or '')
    except ValueError: mf = None
    mh = [x for x in ([i.get('src', '') for i in (mf or {}).get('icons', [])] + [(mf or {}).get('start_url', '')]) if not ada(re.sub(r'^\./', '', x), t)] if mf else ['tidak terbaca']
    ok('manifest-sistem.json: ikon & start_url menunjuk berkas yang ADA (aplikasi sistem yang sudah terpasang membuka pengalih)', not mh, mh)
    # ---- /baru/ tidak menautkan sistem lama
    tautan = [b for b, isi in t.items() if b.startswith('baru/') and isi and re.search(r'''["'`(]\.\./index\.html''', isi)]
    ok('/baru/ tidak lagi menautkan sistem lama (../index.html)', not tautan, tautan)
    return out


KONTROL = [
    ('kasir.html kembali ke FILES service worker', {'sw-kasir.js': [("const FILES = ['kasir-darurat-nominal.html',", "const FILES = ['kasir.html', 'kasir-darurat-nominal.html',")]}),
    ('FILES menyebut berkas yang sudah dihapus (install gagal diam-diam)', {'sw-kasir.js': [("'icon-kasir-32.png'];", "'icon-kasir-32.png', 'manifest-kasir.json'];")]}),
    ('kasir.html disajikan dari cache lagi (HTML_SWR)', {'sw-kasir.js': [("const HTML_SWR = ['kasir-darurat-nominal.html'];", "const HTML_SWR = ['kasir-darurat-nominal.html', 'kasir.html'];")]}),
    ('cache versi lama tidak dihapus saat aktif', {'sw-kasir.js': [('ks.filter((k) => k !== VERSI).map((k) => caches.delete(k))', '[].map((k) => caches.delete(k))')]}),
    ('fetch melayani berkas di luar FILES', {'sw-kasir.js': [('  if (!FILES.includes(nama)) return;\n', '')]}),
    ('pengalih kasir.html dihapus (perangkat tanpa SW kena 404)', {'kasir.html': None}),
    ('langkah CI menunjuk alat yang sudah dihapus', {'.github/workflows/pages.yml': [('run: python3 alat-uji/lingkup.py kasir-darurat-nominal.html', 'run: alat-uji/harness/jalankan.sh index.html')]}),
    ('uji beban men-shasum berkas yang tidak ada', {'.github/workflows/uji-beban-peramban.yml': [('        run: shasum -a 256 kasir-darurat-nominal.html', '        run: shasum -a 256 manifest-kasir.json kasir-darurat-nominal.html')]}),
    ('seed HawkScan ke berkas yang sudah dihapus', {'.github/stackhawk.yml': [('      - /sw-kasir.js\n', '      - /sw-kasir.js\n      - /lib/kemas-worker.js\n')]}),
    ('manifest sistem menunjuk ikon yang tidak ada', {'manifest-sistem.json': [('"src": "icon-sistem-512.png"', '"src": "icon-sistem-1024.png"')]}),
    ('tautan "Sistem lama" kembali di /baru/', {'baru/index.html': [('Sistem lama sudah pensiun (3 Okt 2026).', '<a href="../index.html">Sistem lama</a> tetap ada.')]}),
    ('404.html dihapus (alamat lama berhenti di 404 polos)', {'404.html': None}),
    ('404.html mengalihkan ke "baru/" relatif (meleset di alamat dalam)', {'404.html': [('content="0; url=/Toko-Beras-M.IQBAL/baru/"', 'content="0; url=baru/"')]}),
    ('404.html diberi script', {'404.html': [('<main>', '<main><script>location.href = "/Toko-Beras-M.IQBAL/baru/";</script>')]}),
    ('404.html masuk FILES service worker kasir', {'sw-kasir.js': [("const FILES = ['kasir-darurat-nominal.html',", "const FILES = ['404.html', 'kasir-darurat-nominal.html',")]}),
]


def main():
    if '--kontrol' in sys.argv:
        diam = []; dasar = {n for n, ok, _ in periksa(baca()) if ok}
        for nama, g in KONTROL:
            try: hasil = periksa(baca(g))
            except AssertionError as e: print('KONTROL BASI ' + nama + ' — ' + str(e)); diam.append(nama); continue
            gagal = [n for n, ok, _ in hasil if not ok and n in dasar]
            print(('BERBUNYI ' if gagal else 'DIAM!!   ') + nama + ('  → ' + gagal[0][:120] if gagal else ''))
            if not gagal: diam.append(nama)
        print('kontrol: %d/%d berbunyi' % (len(KONTROL) - len(diam), len(KONTROL))); return 3 if diam else 0
    hasil = periksa(baca())
    for n, ok, k in hasil:
        if not ok: print('   ✗ ' + n + (' → ' + json.dumps(k, ensure_ascii=False)[:400] if k not in ('', None) else ''))
    lulus = sum(1 for _, ok, _ in hasil if ok)
    print('PENSIUN SISTEM LAMA & kasir.html (3 Okt): %d lulus · %d gagal' % (lulus, len(hasil) - lulus))
    return 0 if lulus == len(hasil) else 1


if __name__ == '__main__':
    sys.exit(main())
