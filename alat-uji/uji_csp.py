#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_csp.py — Content-Security-Policy /baru/ (keputusan owner 1 Okt 2026: "Pasang"; temuan HawkScan). Statis, tanpa peramban.

  · META: <meta http-equiv="Content-Security-Policy"> ada di <head>, SEBELUM script & stylesheet pertama (CSP lewat meta hanya berlaku untuk yang sesudahnya).
  · HASH: tiap <script> sebaris di baru/index.html punya 'sha256-…' yang SAMA dengan isinya (ubah script sebaris → `--pasang` menulis hash baru).
  · SUMBER: tiap <script src>, import modul dari luar (baru/js/**), <link rel=modulepreload|stylesheet> ada di direktif yang benar.
  · KONEKSI: Firestore & Auth Firebase (firestore / identitytoolkit / securetoken) ada di connect-src; tidak ada host lain yang tidak dipakai.
  · SEBARIS: script-src tanpa 'unsafe-inline' → TIDAK boleh ada on…="…" atau javascript: di index.html maupun templat baru/js/**.
  · DASAR: object-src 'none', base-uri 'self', form-action 'self'.
PENGALIH (3 Okt 2026, owner: sistem lama & kasir.html "bumi hanguskan"): index.html & kasir.html di akar = halaman pengalih ke baru/.
  · TANPA <script> sama sekali (juga tanpa on…= / javascript:); meta refresh "0; url=baru/" + tautan <a href="baru/">.
  · CSP ketat, persis: default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none' — + manifest-src 'self'
    HANYA kalau halaman menautkan manifest. Meta CSP sebelum <link>/<style> pertama.
  · tiap <link href> / <img src> lokal dan berkasnya ADA di repo (ikon & manifest yang dihapus bersama sistem lama tidak boleh dirujuk).

    python3 alat-uji/uji_csp.py            → N lulus · 0 gagal
    python3 alat-uji/uji_csp.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
    python3 alat-uji/uji_csp.py --pasang   → tulis ulang hash script sebaris di meta CSP baru/index.html
"""
import os, re, sys, glob, base64, hashlib
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
HTML = 'baru/index.html'
PENGALIH = ['index.html', 'kasir.html']
CSP_PENGALIH = {'default-src': ["'none'"], 'img-src': ["'self'"], 'style-src': ["'unsafe-inline'"], 'base-uri': ["'none'"], 'form-action': ["'none'"]}
FIREBASE = ['https://firestore.googleapis.com', 'https://identitytoolkit.googleapis.com', 'https://securetoken.googleapis.com']


def baca(ganti=None):
    t = {HTML: open(os.path.join(AKAR, HTML), encoding='utf-8').read()}
    for b in PENGALIH: t[b] = open(os.path.join(AKAR, b), encoding='utf-8').read()
    for p in sorted(glob.glob(os.path.join(AKAR, 'baru/js/**/*.js'), recursive=True)):
        t[os.path.relpath(p, AKAR)] = open(p, encoding='utf-8').read()
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def csp_dari(html):
    m = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)">', html)
    if not m: return None, -1
    d = {}
    for bag in m.group(1).split(';'):
        k = bag.strip().split()
        if k: d[k[0]] = k[1:]
    return d, m.start()


def hash_sebaris(html):
    return ["'sha256-" + base64.b64encode(hashlib.sha256(x.encode('utf-8')).digest()).decode() + "'" for x in re.findall(r'<script>(.*?)</script>', html, re.S)]


def asal(url):
    m = re.match(r'(https?://[^/]+)', url); return m.group(1) if m else None


def periksa(t):
    c = []; html = t[HTML]; D, pos = csp_dari(html)
    c.append(('meta CSP ada di baru/index.html', D is not None, ''))
    if D is None: return c
    kepala = html[:html.find('</head>')] if '</head>' in html else html
    pertama = [i for i in (kepala.find('<script'), kepala.find('<link rel="stylesheet"'), kepala.find('<link rel="modulepreload"')) if i >= 0]
    c.append(('meta CSP di <head> sebelum script & stylesheet pertama', 0 <= pos < min(pertama) if pertama else pos >= 0, (pos, pertama)))
    ss = D.get('script-src', []); st = D.get('style-src', []); cs = D.get('connect-src', [])
    hs = hash_sebaris(html)
    c.append(('script sebaris: hash di script-src = isinya (' + str(len(hs)) + ' script)', all(h in ss for h in hs) and len([x for x in ss if x.startswith("'sha256-")]) == len(hs), (hs, [x for x in ss if x.startswith("'sha256-")])))
    c.append(("script-src tanpa 'unsafe-inline' & 'unsafe-eval'", "'unsafe-inline'" not in ss and "'unsafe-eval'" not in ss, ss))
    luar_script = set(asal(x) for x in re.findall(r'<script[^>]*\ssrc="(https?://[^"]+)"', html))
    luar_script |= set(asal(x) for x in re.findall(r'<link rel="modulepreload" href="(https?://[^"]+)"', html))
    for p, isi in t.items():
        if p.endswith('.js'): luar_script |= set(asal(x) for x in re.findall(r"""(?:from|import)\s*\(?\s*['"](https?://[^'"]+)['"]""", isi))
    luar_script.discard(None)
    c.append(('script dari luar (src, modulepreload, import modul) semuanya diizinkan script-src', all(h in ss for h in luar_script), sorted(h for h in luar_script if h not in ss)))
    luar_gaya = set(asal(x) for x in re.findall(r'<link rel="stylesheet" href="(https?://[^"]+)"', html)); luar_gaya.discard(None)
    c.append(('stylesheet dari luar diizinkan style-src; font Google diizinkan font-src', all(h in st for h in luar_gaya)
              and (('https://fonts.googleapis.com' not in luar_gaya) or 'https://fonts.gstatic.com' in D.get('font-src', [])), sorted(luar_gaya)))
    c.append(('connect-src: Firestore & Auth Firebase (' + ', '.join(x.split('//')[1].split('.')[0] for x in FIREBASE) + ')', all(h in cs for h in FIREBASE), cs))
    # SDK Firebase dimuat dari gstatic; host lain di connect-src = celah tanpa guna
    lebih = [h for h in cs if h not in FIREBASE + ["'self'", 'https://www.gstatic.com']]
    c.append(('connect-src tidak membuka host lain', not lebih, lebih))
    sebaris = []
    for p, isi in t.items():
        for m in re.finditer(r'''<[a-zA-Z][^<>]*\son[a-z]+\s*=\s*["']''', isi): sebaris.append(p + ':' + str(isi[:m.start()].count('\n') + 1))
        for m in re.finditer(r'''href\s*=\s*["']javascript:''', isi): sebaris.append(p + ':' + str(isi[:m.start()].count('\n') + 1) + ' javascript:')
    c.append(('tidak ada on…="…" / javascript: sebaris (diblokir CSP tanpa unsafe-inline)', not sebaris, sebaris[:8]))
    c.append(("dasar: object-src 'none', base-uri 'self', form-action 'self', default-src 'self'", D.get('object-src') == ["'none'"] and D.get('base-uri') == ["'self'"]
              and D.get('form-action') == ["'self'"] and D.get('default-src') == ["'self'"], {k: D.get(k) for k in ('object-src', 'base-uri', 'form-action', 'default-src')}))
    for b in PENGALIH: c += periksa_pengalih(b, t[b])
    return c


def periksa_pengalih(b, html):
    """Halaman pengalih (3 Okt 2026): tanpa script, CSP ketat, mengalihkan ke baru/, rujukan lokal yang ada."""
    c = []; D, pos = csp_dari(html)
    c.append((b + ' (pengalih): TANPA <script> sama sekali', '<script' not in html.lower(), html.lower().count('<script')))
    c.append((b + ' (pengalih): meta refresh "0; url=baru/" + tautan <a href="baru/">',
              '<meta http-equiv="refresh" content="0; url=baru/">' in html and '<a href="baru/">' in html, ''))
    if D is None: return c + [(b + ' (pengalih): meta CSP ada', False, '')]
    kepala = html[:html.find('</head>')] if '</head>' in html else html
    pertama = [i for i in (kepala.find('<link'), kepala.find('<style')) if i >= 0]
    c.append((b + ' (pengalih): meta CSP sebelum <link>/<style> pertama', 0 <= pos < min(pertama) if pertama else pos >= 0, (pos, pertama)))
    manifest = re.search(r'<link rel="manifest" href="([^"]+)"', html)
    harap = dict(CSP_PENGALIH, **({'manifest-src': ["'self'"]} if manifest else {}))
    c.append((b + " (pengalih): CSP persis default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none' (+ manifest-src 'self' hanya bila menautkan manifest)",
              D == harap, D))
    rujuk = re.findall(r'<(?:link|img)\b[^>]*\s(?:href|src)="([^"]+)"', html)
    salah = [x for x in rujuk if re.match(r'[a-z]+:|//', x) or not os.path.isfile(os.path.join(AKAR, x.split('?')[0].split('#')[0]))]
    c.append((b + ' (pengalih): tiap <link>/<img> lokal & berkasnya ada (' + str(len(rujuk)) + ' rujukan)', not salah, salah))
    return c


KONTROL = [
    ('script sebaris berubah tanpa hash baru', {HTML: [('  // Sesudah versi baru terbit,', '  // (diubah) Sesudah versi baru terbit,')]}),
    ('script-src kehilangan gstatic (SDK Firebase diblokir)', {HTML: [("script-src 'self' https://www.gstatic.com", "script-src 'self'")]}),
    ("script-src diberi 'unsafe-inline'", {HTML: [("script-src 'self' https://www.gstatic.com", "script-src 'self' 'unsafe-inline' https://www.gstatic.com")]}),
    ('connect-src kehilangan Firestore', {HTML: [('connect-src \'self\' https://firestore.googleapis.com ', 'connect-src \'self\' ')]}),
    ('connect-src membuka host lain', {HTML: [('https://securetoken.googleapis.com https://www.gstatic.com;', 'https://securetoken.googleapis.com https://www.gstatic.com https://contoh.example;')]}),
    ('font Google tidak diizinkan', {HTML: [("font-src 'self' https://fonts.gstatic.com;", "font-src 'self';")]}),
    ('onclick sebaris di templat layar', {'baru/js/layar/jual.js': [('<div class="kaca-btn" data-aksi="pecahan"', '<div class="kaca-btn" onclick="x()" data-aksi="pecahan"')]}),
    ('meta CSP sesudah stylesheet', {HTML: [('<meta http-equiv="Content-Security-Policy"', '<link rel="stylesheet" href="css/x.css">\n<meta http-equiv="Content-Security-Policy"')]}),
    ("object-src bukan 'none'", {HTML: [("object-src 'none';", "object-src 'self';")]}),
    # pengalih (3 Okt 2026)
    ('pengalih index.html diberi script', {'index.html': [('<main>', '<main><script>location.href = "baru/";</script>')]}),
    ('pengalih kasir.html diberi onclick', {'kasir.html': [('<a href="baru/">', '<a href="baru/" onclick="x()">')]}),
    ('pengalih kasir.html tanpa meta refresh', {'kasir.html': [('<meta http-equiv="refresh" content="0; url=baru/">\n', '')]}),
    ('pengalih index.html mengalihkan ke tempat lain', {'index.html': [('content="0; url=baru/"', 'content="0; url=kasir-darurat-nominal.html"')]}),
    ("pengalih index.html CSP default-src 'self'", {'index.html': [("content=\"default-src 'none';", "content=\"default-src 'self';")]}),
    ("pengalih kasir.html CSP diberi script-src", {'kasir.html': [("form-action 'none'\">", "form-action 'none'; script-src 'self'\">")]}),
    ('pengalih kasir.html menautkan manifest tanpa manifest-src', {'kasir.html': [('<link rel="icon"', '<link rel="manifest" href="manifest-sistem.json">\n<link rel="icon"')]}),
    ('pengalih index.html merujuk ikon yang sudah dihapus', {'index.html': [('href="icon-sistem-180.png"', 'href="icon-kasir-512.png"')]}),
    ('pengalih kasir.html meta CSP sesudah stylesheet', {'kasir.html': [('<meta http-equiv="Content-Security-Policy"', '<link rel="icon" href="icon-kasir-32.png">\n<meta http-equiv="Content-Security-Policy"')]}),
]


def pasang():
    p = os.path.join(AKAR, HTML); s = open(p, encoding='utf-8').read(); D, _ = csp_dari(s)
    lama = [x for x in D.get('script-src', []) if x.startswith("'sha256-")]; baru = hash_sebaris(s)
    m = re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(">)', s)
    isi = m.group(2)
    for x in lama: isi = isi.replace(' ' + x, '')
    isi = isi.replace("script-src 'self' https://www.gstatic.com", "script-src 'self' https://www.gstatic.com " + ' '.join(baru), 1)
    s = s[:m.start(2)] + isi + s[m.end(2):]; open(p, 'w', encoding='utf-8').write(s); print('hash script sebaris ditulis:', ' '.join(baru))


def main():
    if '--pasang' in sys.argv: pasang(); return 0
    if '--kontrol' in sys.argv:
        diam = []; dasar = {n for n, ok, k in periksa(baca()) if ok}
        for nama, g in KONTROL:
            try: hasil = periksa(baca(g))
            except AssertionError as e: print('KONTROL BASI ' + nama + ' — ' + str(e)); diam.append(nama); continue
            gagal = [n for n, ok, k in hasil if not ok and n in dasar]
            print(('BERBUNYI ' if gagal else 'DIAM     ') + nama + ('  → ' + gagal[0] if gagal else ''))
            if not gagal: diam.append(nama)
        print('kontrol: %d/%d berbunyi' % (len(KONTROL) - len(diam), len(KONTROL))); return 3 if diam else 0
    hasil = periksa(baca())
    for n, ok, k in hasil:
        if not ok: print('GAGAL:', n, '→', str(k)[:400])
    lulus = sum(1 for _, ok, _ in hasil if ok); print('CSP /baru/ + pengalih index.html & kasir.html: %d lulus · %d gagal' % (lulus, len(hasil) - lulus))
    return 0 if lulus == len(hasil) else 1


if __name__ == '__main__':
    sys.exit(main())
