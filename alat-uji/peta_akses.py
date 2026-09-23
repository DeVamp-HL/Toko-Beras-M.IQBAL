#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
peta_akses.py — PETA TULIS dari KODE (putaran 23, Tahap 0). Statis, tanpa Node.

Membaca tiap fungsi `export function susun*` / pembantu tulis di baru/js/layar/*-logika.js,
lalu mendaftar koleksi yang ditulisnya dan bentuk tulisannya:
  buat   = dokumen ber-id baru (w.idUnik(), id + 1, id bentukan) → di rules = create
  ubah   = salinan dokumen yang sudah ada (Object.assign({}, dok, …)) → di rules = update
  buat?  = tidak bisa dipastikan statis (upsert / id dari luar) → diperiksa tangan di peta
  hapus  = masuk daftar `hapus: [...]`                            → di rules = delete
  kolom  = `ubahKolom` (perbaruiKolom: update kolom tertentu saja)
Pemanggilan fungsi susun lain di badan fungsi ikut digabung (graf panggilan, satu berkas + impor).

    python3 alat-uji/peta_akses.py            → tabel markdown ke stdout
    python3 alat-uji/peta_akses.py --json     → bentuk mentah (dipakai uji_akses_baru.py)
"""
import os, re, sys, json, glob

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
LAYAR = os.path.join(AKAR, 'baru', 'js', 'layar')
KOLEKSI_WADAH = ['stokBahanKemasan', 'stokBahanLiteran']   # koleksiWadah(jenis) → salah satu dari dua ini (wadah-jual-logika.js)


def badan(teks, awal):
    """Badan fungsi dari posisi `function NAMA(` — cocokkan kurung kurawal, lompati string & komentar."""
    i = teks.index('(', awal); d = 0
    while True:   # lewati parameter (boleh berisi { } default)
        c = teks[i]
        if c == '(': d += 1
        elif c == ')':
            d -= 1
            if d == 0: break
        i += 1
    i = teks.index('{', i); mulai = i; d = 0; n = len(teks)
    while i < n:
        c = teks[i]
        if c in '\'"`':
            q = c; i += 1
            while i < n and teks[i] != q:
                if teks[i] == '\\': i += 1
                i += 1
        elif c == '/' and i + 1 < n and teks[i + 1] == '/':
            i = teks.index('\n', i)
        elif c == '/' and i + 1 < n and teks[i + 1] == '*':
            i = teks.index('*/', i) + 1
        elif c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return teks[mulai:i + 1]
        i += 1
    return teks[mulai:]


def jenis_data(potong):
    """Bentuk dokumen dari potongan teks sesudah `data:`."""
    p = potong.lstrip()
    if p.startswith('Object.assign({}, {') or p.startswith('{'):
        head = p[:160]
        if re.search(r"id:\s*(w\.idUnik\(\)|[a-zA-Z_.]+\s*\+\s*1\b|id\b|idBaru|idUnik|String\(w\.idUnik)", head) or 'idUnik' in head: return 'buat'
        return 'buat?'
    if p.startswith('Object.assign({}, '): return 'ubah'
    return 'buat?'


def pindai():
    fungsi = {}   # nama → {berkas, tulis: {(koleksi, bentuk)}, panggil: set()}
    for f in sorted(glob.glob(os.path.join(LAYAR, '*-logika.js'))):
        teks = open(f, encoding='utf-8').read(); berkas = os.path.basename(f)
        for m in re.finditer(r'(?:export\s+)?function\s+([A-Za-z_]\w*)\s*\(', teks):
            nama = m.group(1)
            try: b = badan(teks, m.start())
            except (ValueError, IndexError): continue
            tulis = set()
            for k in re.finditer(r"koleksi:\s*('(\w+)'|koleksiWadah\([^)]*\)|(\w+))", b):
                if k.group(2): kol = [k.group(2)]
                elif k.group(1).startswith('koleksiWadah'): kol = KOLEKSI_WADAH
                else: continue   # variabel: diurus lewat pemanggilan
                sesudah = b[k.end():k.end() + 400]; sebelum = b[max(0, k.start() - 120):k.start()]
                if re.match(r"\s*,\s*id:", sesudah) and 'data' not in sesudah[:30]:
                    bentuk = 'hapus' if re.search(r'hapus', sebelum + sesudah[:60]) or 'hapus' in b else 'hapus'
                else:
                    md = re.search(r'data:\s*', sesudah); bentuk = jenis_data(sesudah[md.end():]) if md else 'buat?'
                for kk in kol: tulis.add((kk, bentuk))
            if 'ubahKolom' in b:
                for k in re.finditer(r"koleksi:\s*'(\w+)',\s*id:[^}]*kolom:", b): tulis.add((k.group(1), 'kolom'))
            panggil = set(re.findall(r'\b([a-z]\w*)\s*\(', b)) - {nama}
            fungsi[nama] = {'berkas': berkas, 'tulis': tulis, 'panggil': panggil}
    # graf panggilan: gabung tulisan fungsi yang dipanggil (sampai tetap)
    ubah = True
    while ubah:
        ubah = False
        for nama, f in fungsi.items():
            for p in f['panggil']:
                if p in fungsi and not fungsi[p]['tulis'] <= f['tulis']:
                    f['tulis'] |= fungsi[p]['tulis']; ubah = True
    return {n: f for n, f in fungsi.items() if f['tulis'] and (n.startswith('susun') or n.startswith('simpan'))}


# ====================== PETA BACA: graf panggilan fungsi lintas berkas (nama unik se-bundel) ======================
JS = os.path.join(AKAR, 'baru', 'js')
LAYAR_UTAMA = ['ringkasan', 'stok', 'jual', 'pelanggan', 'harga', 'uang', 'laporan', 'menu']


def peta_koleksi():
    k = open(os.path.join(JS, 'data', 'koleksi.js'), encoding='utf-8').read()
    kol = dict((c, n) for n, c in re.findall(r"\{ nama: '(\w+)',\s*urut: '?\w*'?,\s*cache: '(\w+)'", k))
    t = open(os.path.join(JS, 'data', 'toko.js'), encoding='utf-8').read()
    ambil = {}
    for m in re.finditer(r'export function (ambil\w+)\(\)\s*\{\s*return (?:_cache\.(\w+)|(ambil\w+)\(\))', t):
        ambil[m.group(1)] = m.group(2) or ('@' + m.group(3))
    for a, c in list(ambil.items()):
        while c and c.startswith('@'): c = ambil.get(c[1:])
        ambil[a] = c
    ambil['ambilTitikKas'] = 'pengaturan'
    return kol, ambil


def fungsi_dari(teks):
    g = {}
    for m in re.finditer(r'(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)\s*\(', teks):
        try: g.setdefault(m.group(1), badan(teks, m.start()))
        except (ValueError, IndexError): pass
    for m in re.finditer(r'(?:export\s+)?const\s+([A-Za-z_]\w*)\s*=\s*(?:async\s*)?\(?[^=;\n]*\)?\s*=>', teks):
        akhir = teks.find('\n', m.end()); akhir = len(teks) if akhir < 0 else akhir
        g.setdefault(m.group(1), teks[m.end():akhir])
    return g


def modul_ui(f):
    """Berkas layar (bukan *-logika.js) — nama fungsinya LOKAL (tiap layar punya `gambar` sendiri)."""
    b = os.path.basename(f); return os.path.dirname(f).endswith('layar') and not b.endswith('-logika.js')


def graf_fungsi():
    """Graf GLOBAL: logika, mesin, data, inti — nama unik se-bundel (bundel_baru menjamin satu lingkup)."""
    g = {}
    for f in glob.glob(os.path.join(JS, '**', '*.js'), recursive=True):
        if modul_ui(f): continue
        for n, t in fungsi_dari(open(f, encoding='utf-8').read()).items(): g.setdefault(n, t)
    return g


def impor_ui(f, kunjung=None):
    """Berkas layar + modul layar lain yang diimpornya (mis. jual.js → wadah-panel.js, adegan.js)."""
    kunjung = kunjung if kunjung is not None else []
    if f in kunjung or not os.path.exists(f): return kunjung
    kunjung.append(f)
    for m in re.finditer(r"from '\./([\w-]+\.js)'", open(f, encoding='utf-8').read()):
        g = os.path.join(os.path.dirname(f), m.group(1))
        if modul_ui(g): impor_ui(g, kunjung)
    return kunjung


def baca_dari(teks_awal, g, kol, ambil, lokal=None):
    lokal = lokal or {}; kunjung, antre, baca = set(), [teks_awal], set()
    while antre:
        t = antre.pop()
        for a in re.findall(r'\b(ambil\w+)\s*\(', t):
            if ambil.get(a): baca.add(kol.get(ambil[a], ambil[a]))
        for c in re.findall(r"cacheMentah\('(\w+)'\)", t): baca.add(kol.get(c, c))
        for n in set(re.findall(r'\b([A-Za-z_]\w*)\s*\(', t)):
            if n in kunjung: continue
            badan_n = lokal.get(n, g.get(n))
            if badan_n is not None: kunjung.add(n); antre.append(badan_n)
    return baca


def baca_per_layar():
    kol, ambil = peta_koleksi(); g = graf_fungsi(); out = {}
    for l in LAYAR_UTAMA:
        f = os.path.join(JS, 'layar', l + '.js')
        if not os.path.exists(f): continue
        berkas = impor_ui(f); teks = '\n'.join(open(x, encoding='utf-8').read() for x in berkas)
        out[l] = sorted(baca_dari(teks, g, kol, ambil, fungsi_dari(teks)))
    return out, sorted(kol.values())


if __name__ == '__main__':
    if '--baca' in sys.argv:
        B, semua = baca_per_layar()
        print('| layar | koleksi dibaca (dari %d) |' % len(semua)); print('|---|---|')
        for l, v in B.items(): print('| %s | %d: %s |' % (l, len(v), ', '.join(v)))
        tak = [k for k in semua if not any(k in v for v in B.values())]
        print('\ntidak dibaca layar mana pun:', ', '.join(tak) or '-'); sys.exit(0)
    F = pindai()
    if '--json' in sys.argv:
        print(json.dumps({n: {'berkas': f['berkas'], 'tulis': sorted(list(t) for t in f['tulis'])} for n, f in sorted(F.items())}, ensure_ascii=False, indent=1)); sys.exit(0)
    print('| berkas | fungsi | koleksi · bentuk |'); print('|---|---|---|')
    for n, f in sorted(F.items(), key=lambda x: (x[1]['berkas'], x[0])):
        per = {}
        for kol, b in sorted(f['tulis']): per.setdefault(kol, []).append(b)
        print('| %s | `%s` | %s |' % (f['berkas'].replace('-logika.js', ''), n, ' · '.join('%s %s' % (k, '/'.join(v)) for k, v in sorted(per.items()))))
    print('\n%d fungsi yang menulis' % len(F))
