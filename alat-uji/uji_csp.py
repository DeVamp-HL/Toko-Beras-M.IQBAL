#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_csp.py — Content-Security-Policy halaman yang terbit, ATURAN PER HALAMAN. Statis, tanpa peramban.

/baru/ (keputusan owner 1 Okt 2026: "Pasang"; temuan HawkScan) — baru/index.html:
  · META: <meta http-equiv="Content-Security-Policy"> ada di <head>, SEBELUM script & stylesheet pertama (CSP lewat meta hanya berlaku untuk yang sesudahnya).
  · HASH: tiap <script> sebaris di baru/index.html punya 'sha256-…' yang SAMA dengan isinya (ubah script sebaris → `--pasang` menulis hash baru).
  · SUMBER: tiap <script src>, import modul dari luar (baru/js/**), <link rel=modulepreload|stylesheet> ada di direktif yang benar.
  · KONEKSI: Firestore & Auth Firebase (firestore / identitytoolkit / securetoken) ada di connect-src; tidak ada host lain yang tidak dipakai.
  · SEBARIS: script-src tanpa 'unsafe-inline' → TIDAK boleh ada on…= (huruf besar/kecil, berkutip atau tanpa kutip) atau javascript: di
    index.html maupun templat baru/js/**.
  · DASAR: object-src 'none', base-uri 'self', form-action 'self'.
KASIR DARURAT (3 Okt 2026, sisa owner "hapus sistem lama + kasir.html + CSP kasir darurat") — kasir-darurat-nominal.html, HP penjaga, kasir-v32:
  · META sebelum <script>/<style>/<link> pertama.
  · HASH: script-src PERSIS hash script sebaris (satu script klasik) — tanpa 'unsafe-inline', 'unsafe-eval', 'self', host; tanpa <script src>;
    jumlah tag <script> = jumlah yang di-hash (script sebaris = SEMUA <script> tanpa src: atribut apa pun seperti type="…", huruf besar/kecil bebas).
  · KONEKSI: connect-src PERSIS 'self' + Firestore/identitytoolkit/securetoken (REST tanpa SDK → TANPA gstatic, beda dengan /baru/); tiap alamat https
    di script & preconnect tercakup; jaringan hanya lewat fetch (tanpa XMLHttpRequest / WebSocket / EventSource / sendBeacon / import()).
  · SW: worker-src 'self' — tanpa itu register jatuh ke script-src (cuma hash) dan service worker DIBLOKIR; register ke berkas situs sendiri yang ADA.
  · GAYA: style-src 'self' 'unsafe-inline' (blok <style> + atribut style); img-src 'self'; rujukan <link>/<img> lokal ada di repo.
  · SEBARIS: tidak ada atribut on… di HTML statis MAUPUN di string innerHTML / setAttribute('on…') di script (handler sebaris DIBLOKIR diam-diam:
    tombol tampil tapi mati tanpa galat). Huruf besar/kecil bebas (onClick) dan nilai berkutip ATAU tanpa kutip (onclick=simpan()) — peramban
    menerima keduanya. Pola yang sama dipakai periksa.sh bagian 4 (cari_sebaris diimpor, bukan disalin).
  · DATA-AKSI: tiap data-aksi / data-aksi-ketik punya penangan di AKSI; tiap penangan dipakai; tiap <button> (HTML & string innerHTML) membawa
    data-aksi; satu pendengar delegasi untuk click & input di document.
  · DASAR: default-src 'self', object-src 'none', base-uri 'none', form-action 'none'; tidak ada direktif lain.
PENGALIH (3 Okt 2026, owner: sistem lama & kasir.html "bumi hanguskan"): index.html & kasir.html di akar = halaman pengalih ke baru/.
  · TANPA <script> sama sekali (juga tanpa on…= / javascript:); meta refresh "0; url=baru/" + tautan <a href="baru/">.
  · CSP ketat, persis: default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none' — + manifest-src 'self'
    HANYA kalau halaman menautkan manifest. Meta CSP sebelum <link>/<style> pertama.
  · tiap <link href> / <img src> lokal dan berkasnya ADA di repo (ikon & manifest yang dihapus bersama sistem lama tidak boleh dirujuk).
  · 404.html (owner 7 Okt, sisa pensiun #103): aturan yang sama, tujuan = jalur penuh situs /Toko-Beras-M.IQBAL/baru/ (disajikan di alamat mana pun yang
    tidak ada — "baru/" relatif meleset), tanpa <link>/<img>; di CI jalurnya dicocokkan ke GITHUB_REPOSITORY.

KONTROL kasir darurat yang mengubah script menulis ulang hash di salinannya ('hash': True) — supaya yang berbunyi cacat yang dituju, bukan hash basi —
dan wajib menjatuhkan pemeriksaan yang namanya memuat 'harap' (bukan sembarang pemeriksaan).

    python3 alat-uji/uji_csp.py            → N lulus · 0 gagal
    python3 alat-uji/uji_csp.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
    python3 alat-uji/uji_csp.py --pasang   → tulis ulang hash script sebaris di meta CSP baru/index.html & kasir-darurat-nominal.html
"""
import os, re, sys, glob, base64, hashlib
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
HTML = 'baru/index.html'
DARURAT = 'kasir-darurat-nominal.html'
HALAMAN_HASH = [HTML, DARURAT]   # halaman ber-script sebaris yang hash-nya ditulis --pasang
PENGALIH = ['index.html', 'kasir.html']
# owner 7 Okt (sisa pensiun #103): 404.html = pengalih yang disajikan GitHub Pages di alamat MANA PUN yang tidak ada → tujuannya jalur penuh situs, bukan
# "baru/" relatif (di /Toko-Beras-M.IQBAL/lib/x.js "baru/" jadi /lib/baru/). Jalur situs = /<nama repo>/ (GitHub Pages proyek); di CI dicocokkan ke
# GITHUB_REPOSITORY. Tanpa <link>/<img> (rujukan relatif juga meleset di alamat dalam).
PENGALIH_404 = '404.html'
TUJUAN_404 = '/Toko-Beras-M.IQBAL/baru/'
CSP_PENGALIH = {'default-src': ["'none'"], 'img-src': ["'self'"], 'style-src': ["'unsafe-inline'"], 'base-uri': ["'none'"], 'form-action': ["'none'"]}
FIREBASE = ['https://firestore.googleapis.com', 'https://identitytoolkit.googleapis.com', 'https://securetoken.googleapis.com']
# Kasir darurat: direktif selain script-src, PERSIS (urutan sumber diabaikan). script-src = hash script sebaris saja.
CSP_DARURAT = {'default-src': ["'self'"], 'style-src': ["'self'", "'unsafe-inline'"], 'img-src': ["'self'"], 'connect-src': ["'self'"] + FIREBASE,
               'worker-src': ["'self'"], 'object-src': ["'none'"], 'base-uri': ["'none'"], 'form-action': ["'none'"]}
# Nama atribut handler peramban yang dicari di dalam script (string yang dirangkai / setAttribute) — atribut sebaris diblokir CSP tanpa 'unsafe-inline'.
ON_PERISTIWA = (r'on(?:click|dblclick|input|change|key\w+|submit|load|error|focus\w*|blur|mouse\w+|touch\w+|pointer\w+|scroll|wheel|contextmenu|'
                r'toggle|reset|select|paste|copy|cut|drag\w*|drop|beforeinput|invalid|search|animation\w+|transition\w+)')
# owner 3 Okt (perkuat, temuan tinjauan): nama atribut HTML tidak peka huruf besar (onClick = onclick bagi peramban) dan nilainya boleh TANPA kutip
# (onclick=simpanNominal()). Dulu regex peka huruf & mewajibkan kutip — dua bentuk itu lolos padahal tombolnya mati di HP. Nilai = kutip, kutip ber-escape
# (\" di string JS), atau awal nilai tanpa kutip. Semua pola sebaris di bawah memakai re.I.
NILAI_ATRIBUT = r'''\s*=\s*(?:\\?["']|[^\s"'<>=`])'''
ATRIBUT_ON = re.compile(r'''<[a-zA-Z][^<>]*\son[a-z]+''' + NILAI_ATRIBUT, re.I)
PERISTIWA_JS = re.compile(r'''(?:^|[\s'"])''' + ON_PERISTIWA + NILAI_ATRIBUT, re.I | re.M)
SET_ON = re.compile(r'''setAttribute\(\s*['"]on''', re.I)
# Script sebaris = SEMUA <script> tanpa src, apa pun atributnya (type="…", nonce, …) dan huruf besarnya; penutup boleh berspasi (</script >) seperti
# yang diterima peramban. Dulu hanya '<script>' polos yang di-hash & dipindai: <script type="text/javascript"> sebaris lolos dua-duanya, lalu DIBLOKIR.
SCRIPT_SEBARIS = re.compile(r'<script\b(?![^>]*\ssrc\s*=)[^>]*>(.*?)</script\s*>', re.S | re.I)
TAG_SCRIPT_SEBARIS = re.compile(r'<script\b(?![^>]*\ssrc\s*=)', re.I)


def baca(ganti=None, hash_ulang=False):
    t = {HTML: open(os.path.join(AKAR, HTML), encoding='utf-8').read(), DARURAT: open(os.path.join(AKAR, DARURAT), encoding='utf-8').read()}
    for b in PENGALIH + [PENGALIH_404]: t[b] = open(os.path.join(AKAR, b), encoding='utf-8').read()
    for p in sorted(glob.glob(os.path.join(AKAR, 'baru/js/**/*.js'), recursive=True)):
        t[os.path.relpath(p, AKAR)] = open(p, encoding='utf-8').read()
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
        if hash_ulang and b in HALAMAN_HASH: t[b] = tulis_hash(t[b])
    return t


def csp_dari(html):
    m = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)">', html)
    if not m: return None, -1
    d = {}
    for bag in m.group(1).split(';'):
        k = bag.strip().split()
        if k: d[k[0]] = k[1:]
    return d, m.start()


def isi_sebaris(html):
    """Isi tiap script sebaris (tanpa src, atribut & huruf besar apa pun), urut kemunculan."""
    return SCRIPT_SEBARIS.findall(html)


def hash_sebaris(html):
    return ["'sha256-" + base64.b64encode(hashlib.sha256(x.encode('utf-8')).digest()).decode() + "'" for x in isi_sebaris(html)]


def cari_sebaris(html):
    """Handler sebaris di halaman ber-script → [(baris, potongan)]: atribut on… di tag (HTML statis & string innerHTML), nama peristiwa sebelum '='
    di string script yang dirangkai, setAttribute('on…'), javascript:. Huruf besar/kecil bebas, berkutip atau tanpa kutip (owner 3 Okt, perkuat).
    Dipakai pemeriksaan kasir darurat di sini DAN periksa.sh bagian 4 — satu pola, dijaga di satu tempat."""
    out = []; baris = lambda i: html[:i].count('\n') + 1
    for m in ATRIBUT_ON.finditer(html): out.append((baris(m.start()), m.group(0)[-40:].replace('\n', ' ')))
    for s in SCRIPT_SEBARIS.finditer(html):
        for pola in (PERISTIWA_JS, SET_ON):
            for m in pola.finditer(s.group(1)): out.append((baris(s.start(1) + m.start()), 'script: ' + m.group(0).strip()[:40]))
    for m in re.finditer(r'javascript:', html): out.append((baris(m.start()), 'javascript:'))
    return out


def tulis_hash(s):
    """Teks halaman dengan hash script sebaris TERBARU di script-src meta CSP. Hash lama dibuang, sumber lain & urutannya tetap, hash baru di ujung."""
    m = re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(">)', s)
    isi = m.group(2); d = re.search(r'script-src[^;]*', isi)
    k = [x for x in d.group(0).split() if not x.startswith("'sha256-")] + hash_sebaris(s)
    isi = isi[:d.start()] + ' '.join(k) + isi[d.end():]
    return s[:m.start(2)] + isi + s[m.end(2):]


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
    hs = hash_sebaris(html); n_tag = len(TAG_SCRIPT_SEBARIS.findall(html))
    # nama TETAP (jumlah script di keterangan): kontrol membandingkan nama pemeriksaan yang lulus sebelum & sesudah kerusakan
    c.append(('script sebaris: hash di script-src = isinya; tiap tag <script> tanpa src ter-hash', all(h in ss for h in hs) and len([x for x in ss if x.startswith("'sha256-")]) == len(hs)
              and n_tag == len(hs), (hs, [x for x in ss if x.startswith("'sha256-")], 'tag <script> tanpa src: %d' % n_tag)))
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
    # semua halaman ber-CSP (/baru/ + templatnya, kasir darurat, pengalih): handler sebaris diblokir
    sebaris = []
    for p, isi in t.items():
        for m in ATRIBUT_ON.finditer(isi): sebaris.append(p + ':' + str(isi[:m.start()].count('\n') + 1))
        for m in re.finditer(r'''href\s*=\s*["']javascript:''', isi): sebaris.append(p + ':' + str(isi[:m.start()].count('\n') + 1) + ' javascript:')
    c.append(('tidak ada on…= (huruf besar/kecil, berkutip atau tanpa kutip) / javascript: sebaris di /baru/, kasir darurat & pengalih (diblokir CSP tanpa unsafe-inline)',
              not sebaris, sebaris[:8]))
    c.append(("dasar: object-src 'none', base-uri 'self', form-action 'self', default-src 'self'", D.get('object-src') == ["'none'"] and D.get('base-uri') == ["'self'"]
              and D.get('form-action') == ["'self'"] and D.get('default-src') == ["'self'"], {k: D.get(k) for k in ('object-src', 'base-uri', 'form-action', 'default-src')}))
    c += periksa_darurat(t[DARURAT])
    for b in PENGALIH: c += periksa_pengalih(b, t[b])
    c += periksa_pengalih(PENGALIH_404, t[PENGALIH_404], TUJUAN_404)
    h4 = t[PENGALIH_404]
    c.append((PENGALIH_404 + ' (pengalih): tanpa <link>/<img> — rujukan relatif meleset di alamat dalam', not re.search(r'<(?:link|img)\b', h4, re.I), re.findall(r'<(?:link|img)\b[^>]*>', h4, re.I)))
    repo = os.environ.get('GITHUB_REPOSITORY', '')
    harap = '/' + repo.split('/', 1)[1] + '/baru/' if '/' in repo else TUJUAN_404
    c.append((PENGALIH_404 + ' (pengalih): tujuan = jalur situs (/<nama repo>/baru/)' + (' — dicocokkan ke GITHUB_REPOSITORY' if repo else ''),
              TUJUAN_404 == harap and TUJUAN_404.startswith('/') and TUJUAN_404.endswith('/baru/') and os.path.isfile(os.path.join(AKAR, 'baru', 'index.html')), (TUJUAN_404, harap)))
    return c


def periksa_darurat(html):
    """Kasir darurat (3 Okt 2026): CSP ketat hash-saja, koneksi persis Firebase REST, tombol lewat data-aksi. Nama pemeriksaan TETAP (angka di keterangan)."""
    b = 'kasir darurat: '; c = []; D, pos = csp_dari(html)
    c.append((b + 'meta CSP ada', D is not None, ''))
    if D is None: return c
    kepala = html[:html.find('</head>')] if '</head>' in html else html
    pertama = [i for i in (kepala.find('<script'), kepala.find('<style'), kepala.find('<link')) if i >= 0]
    c.append((b + 'meta CSP di <head> sebelum <script>/<style>/<link> pertama', 0 <= pos < min(pertama) if pertama else pos >= 0, (pos, pertama)))
    ss = D.get('script-src', []); hs = hash_sebaris(html)
    # owner 3 Okt (perkuat): jumlah tag <script> (huruf besar/kecil) WAJIB = jumlah yang di-hash — tag yang tidak tertangkap pola (tanpa penutup,
    # bentuk aneh) berarti script yang tidak ber-hash, dan peramban memblokirnya diam-diam.
    n_tag = len(re.findall(r'<script\b', html, re.I))
    c.append((b + "script-src PERSIS hash script sebaris — tanpa 'unsafe-inline' / 'unsafe-eval' / 'self' / host; tiap tag <script> ter-hash",
              bool(hs) and sorted(ss) == sorted(hs) and n_tag == len(hs), (hs, ss, 'tag <script>: %d' % n_tag)))
    src = re.findall(r'<script\b[^>]*\ssrc\s*=', html, re.I)
    c.append((b + 'tanpa <script src> (script-src cuma hash — berkas script akan diblokir)', not src, src))
    js = '\n'.join(isi_sebaris(html))
    cs = D.get('connect-src', [])
    c.append((b + "connect-src PERSIS 'self' + Firestore / identitytoolkit / securetoken (REST tanpa SDK — tanpa gstatic)", sorted(cs) == sorted(CSP_DARURAT['connect-src']), cs))
    alamat = set(asal(x) for x in re.findall(r"""['"](https?://[^'"\s]+)""", js))
    alamat |= set(asal(x) for x in re.findall(r'<link rel="preconnect" href="(https?://[^"]+)"', html)); alamat.discard(None)
    c.append((b + 'tiap alamat https di script & preconnect tercakup connect-src', alamat and all(h in cs for h in alamat), sorted(h for h in alamat if h not in cs) or sorted(alamat)))
    lain = re.findall(r'\bXMLHttpRequest\b|\bnew\s+WebSocket\b|\bEventSource\b|\bsendBeacon\b|\bimport\s*\(|\bimportScripts\b', js)
    c.append((b + 'jaringan hanya lewat fetch (tanpa XMLHttpRequest / WebSocket / EventSource / sendBeacon / import())', 'fetch(' in js and not lain, lain))
    reg = re.findall(r"""navigator\.serviceWorker\.register\(\s*['"]([^'"]+)['"]""", js)
    reg_salah = [r for r in reg if re.match(r'[a-z]+:|//', r) or not os.path.isfile(os.path.join(AKAR, r))]
    c.append((b + "worker-src 'self' & service worker didaftarkan dari berkas situs sendiri yang ADA (tanpa worker-src: register jatuh ke script-src hash → diblokir)",
              D.get('worker-src') == ["'self'"] and reg and not reg_salah, (D.get('worker-src'), reg, reg_salah)))
    c.append((b + "style-src 'self' 'unsafe-inline' (blok <style> & atribut style); img-src 'self'",
              sorted(D.get('style-src', [])) == sorted(CSP_DARURAT['style-src']) and D.get('img-src') == CSP_DARURAT['img-src'], (D.get('style-src'), D.get('img-src'))))
    harap = sorted(list(CSP_DARURAT) + ['script-src'])
    c.append((b + "dasar: default-src 'self', object-src 'none', base-uri 'none', form-action 'none'; tidak ada direktif lain",
              all(D.get(k) == CSP_DARURAT[k] for k in ('default-src', 'object-src', 'base-uri', 'form-action')) and sorted(D) == harap,
              {k: D.get(k) for k in sorted(set(D) | set(harap))}))
    rujuk = re.findall(r'<(?:link|img)\b[^>]*\s(?:href|src)="([^"]+)"', html)
    salah = [x for x in rujuk if not re.match(r'https?:', x) and not os.path.isfile(os.path.join(AKAR, x.split('?')[0].split('#')[0]))]
    c.append((b + 'tiap <link>/<img> lokal & berkasnya ada', rujuk and not salah, salah))
    # SEBARIS: atribut on… di HTML statis & string innerHTML (pola tag utuh), string yang dirangkai, setAttribute('on…'), javascript: — huruf
    # besar/kecil bebas, berkutip atau tanpa kutip (cari_sebaris; periksa.sh bagian 4 memakai fungsi yang sama)
    sebaris = ['baris %d · %s' % x for x in cari_sebaris(html)]
    c.append((b + 'tidak ada atribut on… di HTML statis maupun string innerHTML / setAttribute di script (handler sebaris diblokir diam-diam)', not sebaris, sebaris[:8]))
    # DATA-AKSI ↔ penangan
    blok = re.search(r'\nvar AKSI = \{\n(.*?)\n\};', js, re.S)
    kunci = re.findall(r'^\s*([A-Za-z_$][\w$]*):\s*function\b', blok.group(1), re.M) if blok else []
    dipakai = re.findall(r'data-aksi(?:-ketik)?="([^"]*)"', html)
    c.append((b + 'tiap data-aksi / data-aksi-ketik punya penangan di AKSI (tanpa penangan = tombol mati)', kunci and dipakai and all(x in kunci for x in dipakai),
              sorted(set(x for x in dipakai if x not in kunci)) or (len(dipakai), len(kunci))))
    c.append((b + 'tiap penangan di AKSI dipakai data-aksi (penangan yatim = tombolnya hilang / salah nama)', kunci and all(k in dipakai for k in kunci) and len(set(kunci)) == len(kunci),
              sorted(k for k in kunci if k not in dipakai)))
    tombol = re.findall(r'<button\b[^>]*>', html)
    tanpa = [x[:70] for x in tombol if 'data-aksi="' not in x]
    c.append((b + 'tiap <button> (HTML & string innerHTML) membawa data-aksi', tombol and not tanpa, tanpa or len(tombol)))
    c.append((b + 'pendengar delegasi: satu fungsi untuk click & input di document',
              "document.addEventListener('click', jalankanAksi);" in js and "document.addEventListener('input', jalankanAksi);" in js and 'function jalankanAksi(e)' in js, ''))
    return c


def periksa_pengalih(b, html, tujuan='baru/'):
    """Halaman pengalih (3 Okt 2026): tanpa script, CSP ketat, mengalihkan ke baru/ (404.html: jalur penuh situs), rujukan lokal yang ada."""
    c = []; D, pos = csp_dari(html)
    c.append((b + ' (pengalih): TANPA <script> sama sekali', '<script' not in html.lower(), html.lower().count('<script')))
    c.append((b + ' (pengalih): meta refresh "0; url=' + tujuan + '" + tautan <a href="' + tujuan + '">',
              '<meta http-equiv="refresh" content="0; url=' + tujuan + '">' in html and '<a href="' + tujuan + '">' in html, ''))
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
    ('onClick tanpa kutip di templat layar (owner 3 Okt, perkuat)', {'baru/js/layar/jual.js': [('<div class="kaca-btn" data-aksi="pecahan"', '<div class="kaca-btn" onClick=x() data-aksi="pecahan"')]}),
    ('<script type="text/javascript"> sebaris tanpa hash (owner 3 Okt, perkuat)', {HTML: [('<script type="module" src="js/app.js"></script>',
                                                                                        '<script type="text/javascript">window.x = 1;</script>\n<script type="module" src="js/app.js"></script>')]}),
    ('meta CSP sesudah stylesheet', {HTML: [('<meta http-equiv="Content-Security-Policy"', '<link rel="stylesheet" href="css/x.css">\n<meta http-equiv="Content-Security-Policy"')]}),
    ("object-src bukan 'none'", {HTML: [("object-src 'none';", "object-src 'self';")]}),
    # kasir darurat (3 Okt 2026) — (nama, ganti, opsi): 'hash' = salinan ditulis ulang hash-nya sesudah diubah; 'harap' = pemeriksaan yang wajib jatuh
    ('kasir darurat: script berubah tanpa hash baru', {DARURAT: [('// ---------- papan angka ----------', '// ---------- papan angka (diubah) ----------')]},
     {'harap': 'script-src PERSIS hash'}),
    ("kasir darurat: script-src diberi 'unsafe-inline'", {DARURAT: [("script-src 'sha256-", "script-src 'unsafe-inline' 'sha256-")]}, {'harap': 'script-src PERSIS hash'}),
    ("kasir darurat: script-src diberi 'unsafe-eval'", {DARURAT: [("script-src 'sha256-", "script-src 'unsafe-eval' 'sha256-")]}, {'harap': 'script-src PERSIS hash'}),
    ('kasir darurat: <script src> ditambahkan (diblokir script-src hash)', {DARURAT: [('\n</body>', '\n<script src="tambahan.js"></script>\n</body>')]}, {'harap': 'tanpa <script src>'}),
    ('kasir darurat: connect-src kehilangan identitytoolkit (masuk dengan sandi diblokir)', {DARURAT: [(" https://identitytoolkit.googleapis.com https://securetoken", " https://securetoken")]},
     {'harap': 'connect-src PERSIS'}),
    ('kasir darurat: connect-src membuka gstatic (host yang tidak dipakai)', {DARURAT: [("https://securetoken.googleapis.com; worker-src", "https://securetoken.googleapis.com https://www.gstatic.com; worker-src")]},
     {'harap': 'connect-src PERSIS'}),
    ('kasir darurat: fetch ke host yang tidak ada di connect-src', {DARURAT: [("var K_AUTH = 'kasir_auth_v1';", "var URL_LAIN = 'https://contoh.example/v1/x';\nvar K_AUTH = 'kasir_auth_v1';")]},
     {'hash': True, 'harap': 'tiap alamat https'}),
    ('kasir darurat: jaringan lewat XMLHttpRequest', {DARURAT: [("var _tokenSedangSegar = null;", "var _tokenSedangSegar = null; var _xhrLain = typeof XMLHttpRequest;")]},
     {'hash': True, 'harap': 'jaringan hanya lewat fetch'}),
    ("kasir darurat: worker-src dicabut (SW diblokir script-src hash)", {DARURAT: [(" worker-src 'self';", "")]}, {'harap': 'worker-src'}),
    ('kasir darurat: service worker didaftarkan dari host lain', {DARURAT: [("navigator.serviceWorker.register('sw-kasir.js')", "navigator.serviceWorker.register('https://contoh.example/sw-kasir.js')")]},
     {'hash': True, 'harap': 'worker-src'}),
    ("kasir darurat: style-src tanpa 'unsafe-inline' (blok <style> mati)", {DARURAT: [("style-src 'self' 'unsafe-inline';", "style-src 'self';")]}, {'harap': 'style-src'}),
    ("kasir darurat: base-uri 'self'", {DARURAT: [("base-uri 'none'", "base-uri 'self'")]}, {'harap': 'dasar'}),
    ('kasir darurat: direktif tambahan (frame-src)', {DARURAT: [("object-src 'none';", "object-src 'none'; frame-src https://contoh.example;")]}, {'harap': 'dasar'}),
    ('kasir darurat: meta CSP sesudah <style>', {DARURAT: [('<meta http-equiv="Content-Security-Policy"', '<style></style>\n<meta http-equiv="Content-Security-Policy"')]}, {'harap': 'sebelum'}),
    ('kasir darurat: ikon dirujuk ke berkas yang tidak ada', {DARURAT: [('href="icon-kasir-32.png"', 'href="icon-kasir-64.png"')]}, {'harap': '<link>/<img>'}),
    ('kasir darurat: onclick sebaris kembali di tombol SIMPAN', {DARURAT: [('id="btnSimpan" data-aksi="simpan"', 'id="btnSimpan" onclick="simpanNominal()"')]}, {'harap': 'atribut on'}),
    ('kasir darurat: onclick di string innerHTML (tuts bernama)', {DARURAT: [("""'<button type="button" data-aksi="produk" data-nilai="' + i + '">'""",
                                                                             """'<button type="button" onclick="tambahProdukD(' + i + ')">'""")]},
     {'hash': True, 'harap': 'atribut on'}),
    ('kasir darurat: onclick dirangkai dari potongan string', {DARURAT: [("""'<button type="button" data-aksi="hargaCepat" data-nilai="' + h + '">'""",
                                                                          """'<button type="button" ' + 'onclick="tambahHargaCepat(' + h + ')" data-aksi="hargaCepat" data-nilai="' + h + '">'""")]},
     {'hash': True, 'harap': 'atribut on'}),
    ('kasir darurat: handler dipasang lewat setAttribute', {DARURAT: [("    wadah.className = 'produk';", "    wadah.className = 'produk'; wadah.setAttribute('onclick', 'gambarTutsCepat()');")]},
     {'hash': True, 'harap': 'atribut on'}),
    # owner 3 Okt (perkuat, temuan tinjauan): bentuk yang dulu DIAM — script sebaris ber-type tidak di-hash & tidak dipindai, onClick (huruf besar),
    # on…= tanpa kutip; + tag <script> yang tidak tertangkap pola (tanpa penutup) — jumlah tag wajib = jumlah yang di-hash
    ('kasir darurat: <script type="text/javascript"> sebaris ditambahkan tanpa hash baru (diblokir)',
     {DARURAT: [('\n</body>', '\n<script type="text/javascript">tampilkanLayarLogin(false);</script>\n</body>')]}, {'harap': 'script-src PERSIS hash'}),
    ('kasir darurat: <script> tanpa penutup (menelan sisa halaman, tidak ter-hash)', {DARURAT: [('\n</body>', '\n<script type="module">\n</body>')]},
     {'hash': True, 'harap': 'script-src PERSIS hash'}),
    ('kasir darurat: onClick (huruf besar) di tombol SIMPAN', {DARURAT: [('id="btnSimpan" data-aksi="simpan"', 'id="btnSimpan" onClick="simpanNominal()" data-aksi="simpan"')]},
     {'harap': 'atribut on'}),
    ('kasir darurat: onclick TANPA kutip di tombol SIMPAN', {DARURAT: [('id="btnSimpan" data-aksi="simpan"', 'id="btnSimpan" onclick=simpanNominal() data-aksi="simpan"')]},
     {'harap': 'atribut on'}),
    ('kasir darurat: onkeydown TANPA kutip di kolom sandi', {DARURAT: [('<input type="password" id="inputSandiLogin"', '<input type="password" onkeydown=kirimLogin() id="inputSandiLogin"')]},
     {'harap': 'atribut on'}),
    ('kasir darurat: onClick tanpa kutip di string innerHTML (tuts harga)', {DARURAT: [("""'<button type="button" data-aksi="hargaCepat" data-nilai="' + h + '">'""",
                                                                                       """'<button type="button" onClick=tambahHargaCepat(' + h + ') data-aksi="hargaCepat" data-nilai="' + h + '">'""")]},
     {'hash': True, 'harap': 'atribut on'}),
    ('kasir darurat: data-aksi tanpa penangan (HAPUS mati)', {DARURAT: [('data-aksi="hapusAngka"', 'data-aksi="hapusAngkaLama"')]}, {'harap': 'punya penangan'}),
    ('kasir darurat: penangan yatim (tidak dipakai tombol mana pun)', {DARURAT: [("  simpan: function () { simpanNominal(); },", "  simpan: function () { simpanNominal(); },\n  simpanLagi: function () { simpanNominal(); },")]},
     {'hash': True, 'harap': 'penangan di AKSI dipakai'}),
    ('kasir darurat: tombol tanpa data-aksi (Tutup mati)', {DARURAT: [('<button type="button" data-aksi="tutupDitolak">Tutup</button>', '<button type="button">Tutup</button>')]},
     {'harap': 'tiap <button>'}),
    ('kasir darurat: tombol hapus barang (innerHTML) tanpa data-aksi', {DARURAT: [("""'<button type="button" data-aksi="hapusBaris" data-nilai="' + i + '""", """'<button type="button" data-nilai="' + i + '""")]},
     {'hash': True, 'harap': 'tiap <button>'}),
    ('kasir darurat: pendengar delegasi click dicabut (semua tombol mati)', {DARURAT: [("document.addEventListener('click', jalankanAksi);\n", "")]}, {'hash': True, 'harap': 'pendengar delegasi'}),
    ('kasir darurat: pendengar ketikan dicabut (kolom nama tidak dibersihkan)', {DARURAT: [("document.addEventListener('input', jalankanAksi);\n", "")]}, {'hash': True, 'harap': 'pendengar delegasi'}),
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
    # 404.html (owner 7 Okt, sisa pensiun #103)
    ('404.html diberi script', {'404.html': [('<main>', '<main><script>location.href = "/Toko-Beras-M.IQBAL/baru/";</script>')]}, {'harap': '404.html'}),
    ('404.html mengalihkan ke "baru/" relatif (meleset di alamat dalam)', {'404.html': [('content="0; url=/Toko-Beras-M.IQBAL/baru/"', 'content="0; url=baru/"')]}, {'harap': '404.html'}),
    ('404.html tautan tombol ke "baru/" relatif', {'404.html': [('<a href="/Toko-Beras-M.IQBAL/baru/">', '<a href="baru/">')]}, {'harap': '404.html'}),
    ('404.html merujuk ikon relatif', {'404.html': [('<meta name="theme-color"', '<link rel="icon" href="icon-sistem-32.png">\n<meta name="theme-color"')]}, {'harap': '404.html'}),
    ("404.html CSP default-src 'self'", {'404.html': [("content=\"default-src 'none';", "content=\"default-src 'self';")]}, {'harap': '404.html'}),
    ('404.html onclick di tombol', {'404.html': [('<a href="/Toko-Beras-M.IQBAL/baru/">', '<a href="/Toko-Beras-M.IQBAL/baru/" onclick="x()">')]}, {'harap': 'on…='}),
]


def pasang():
    for b in HALAMAN_HASH:
        p = os.path.join(AKAR, b); s = open(p, encoding='utf-8').read(); baru = tulis_hash(s)
        if baru != s: open(p, 'w', encoding='utf-8').write(baru)
        print(b + ': hash script sebaris ' + ('DITULIS' if baru != s else 'sudah sama') + ': ' + ' '.join(hash_sebaris(baru)))


def main():
    if '--pasang' in sys.argv: pasang(); return 0
    if '--kontrol' in sys.argv:
        diam = []; dasar = {n for n, ok, k in periksa(baca()) if ok}
        for butir in KONTROL:
            nama, g = butir[0], butir[1]; opsi = butir[2] if len(butir) > 2 else {}
            try: hasil = periksa(baca(g, hash_ulang=opsi.get('hash', False)))
            except AssertionError as e: print('KONTROL BASI ' + nama + ' — ' + str(e)); diam.append(nama); continue
            gagal = [n for n, ok, k in hasil if not ok and n in dasar]
            kena = [n for n in gagal if opsi.get('harap', '') in n]
            print(('BERBUNYI ' if kena else 'DIAM     ') + nama + ('  → ' + kena[0] if kena else ('  (jatuh yang lain: ' + gagal[0] + ')' if gagal else '')))
            if not kena: diam.append(nama)
        print('kontrol: %d/%d berbunyi' % (len(KONTROL) - len(diam), len(KONTROL))); return 3 if diam else 0
    hasil = periksa(baca())
    for n, ok, k in hasil:
        if not ok: print('GAGAL:', n, '→', str(k)[:400])
    lulus = sum(1 for _, ok, _ in hasil if ok); print('CSP /baru/ + kasir darurat + pengalih index.html, kasir.html & 404.html: %d lulus · %d gagal' % (lulus, len(hasil) - lulus))
    return 0 if lulus == len(hasil) else 1


if __name__ == '__main__':
    sys.exit(main())
