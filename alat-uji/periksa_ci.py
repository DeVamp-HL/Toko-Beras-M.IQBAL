#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
periksa_ci.py — penjaga PEMBAGIAN CI (owner 22 Nov 2026: "bisa dipercepat?"). Tanpa jaringan, tanpa PyYAML (baca baris).

Kenapa ada: job `uji` (102 langkah) dibagi tiga job paralel, `uji-peramban` dua, dan gladi tutup buku tujuh — tiap langkah memilih bagiannya lewat
`if: matrix.bagian == N`. Bahaya terbesar pembagian ini = HIJAU PALSU: langkah yang bagiannya tidak ada di matriks tidak pernah jalan dan tidak ada yang
berbunyi. Langkah TANPA `if:` justru jalan di semua bagian (boros, tidak hilang) — tetap ditolak supaya pembagian tetap disengaja.

Yang dipegang:
  · pages.yml: push diuji hanya di main (cabang lewat pull_request); job uji = matriks [1, 2, 3], uji-peramban = [1, 2]; tiap langkah (kecuali ambil repo)
    punya TEPAT SATU `if: matrix.bagian == N` dengan N di matriks; tiap bagian berisi ≥ 1 langkah; ambil tag sistem-lama SEBELUM & SEBAGIAN dengan uji
    dokumen sisa (--wajib-tag); terbitkan menunggu uji & uji-peramban (semua bagian) dan hanya di main.
  · gladi-tutup-buku.yml: matriks memuat SEMUA skenario bawaan alat gladi + kontrol-1..K, K = KELOMPOK di langkah kontrol (nomor modulo K); langkah gladi
    hanya di bagian skenario yang dipilih; artefak bernama per bagian (bentrok nama = artefak hilang).

    python3 alat-uji/periksa_ci.py            → 0 = lulus, 1 = gagal
    python3 alat-uji/periksa_ci.py --kontrol  → tiap kerusakan WAJIB ketahuan; 0 = semua tertangkap, 3 = ada yang lolos
"""
import os, re, sys

AKAR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PAGES = '.github/workflows/pages.yml'; GLADI = '.github/workflows/gladi-tutup-buku.yml'; ALAT_GLADI = 'alat-uji/gladi_tutup_buku.py'


def baca(p): return open(os.path.join(AKAR, p), encoding='utf-8').read()


def blok_job(teks, nama):
    """Isi job `nama` (baris '  nama:' sampai job berikutnya)."""
    m = re.search(r'\n  ' + re.escape(nama) + r':\n(.*?)(?=\n  [\w-]+:\n|\Z)', teks, re.S)
    return m.group(1) if m else ''


def langkah(blok):
    """Daftar langkah: {nama, if: [..], isi} — langkah mulai di baris '      - '."""
    out = []; cur = None
    for x in blok.split('\n'):
        if re.match(r'^      - ', x):
            cur = {'nama': '', 'if': [], 'isi': x}; out.append(cur)
            m = re.match(r'^      - name:\s*(.*)$', x)
            if m: cur['nama'] = m.group(1).strip().strip('"')
        elif cur is not None:
            cur['isi'] += '\n' + x
            m = re.match(r'^        if:\s*(.*)$', x)
            if m: cur['if'].append(re.sub(r'\s+#.*$', '', m.group(1)).strip())   # komentar YAML di ujung baris bukan bagian syarat
            m = re.match(r'^        name:\s*(.*)$', x)
            if m and not cur['nama']: cur['nama'] = m.group(1).strip().strip('"')
    return out


def matriks(blok):
    m = re.search(r'\n      matrix:\n        bagian: \[([^\]]*)\]', '\n' + blok)
    return [x.strip() for x in m.group(1).split(',')] if m else None


def periksa_bagi(blok, nama_job, harap, c):
    ok = lambda n, x, k='': c.append((nama_job + ': ' + n, bool(x), k))
    M = matriks(blok); ok('matriks bagian = %s' % harap, M == harap, M)
    L = [s for s in langkah(blok) if 'actions/checkout' not in s['isi']]
    tanpa = [s['nama'][:60] for s in L if len([i for i in s['if'] if i.startswith('matrix.bagian')]) != 1]
    ok('tiap langkah punya TEPAT SATU if: matrix.bagian == N (tanpa = jalan di semua bagian; dua = membingungkan)', not tanpa, tanpa[:5])
    salah = [(s['nama'][:50], i) for s in L for i in s['if'] if i.startswith('matrix.bagian') and not re.fullmatch(r'matrix\.bagian == (\d+)', i)]
    ok('bentuk if bagian persis "matrix.bagian == N"', not salah, salah[:3])
    bag = {}
    for s in L:
        for i in s['if']:
            m = re.fullmatch(r'matrix\.bagian == (\d+)', i)
            if m: bag.setdefault(m.group(1), []).append(s)
    asing = sorted(set(bag) - set(harap)); ok('tidak ada langkah di bagian yang tidak ada di matriks (HIJAU PALSU: langkah itu tidak pernah jalan)', not asing, [(k, [s['nama'][:40] for s in bag[k]]) for k in asing])
    kosong = [k for k in harap if k not in bag]; ok('tiap bagian matriks berisi langkah', not kosong, kosong)
    return L


def periksa(t):
    c = []; ok = lambda n, x, k='': c.append((n, bool(x), k))
    P = t[PAGES]
    on = re.search(r'\non:\n(.*?)\n\S', '\n' + P, re.S); on = on.group(1) if on else ''
    ok('pages.yml: push diuji hanya di main; cabang lewat pull_request (tanpa run ganda push + PR)', re.search(r'\n  push:\n    branches: \[main\]\n', '\n' + on + '\n') and '\n  pull_request:' in '\n' + on, on[:200])
    U = blok_job(P, 'uji'); R = blok_job(P, 'uji-peramban'); TB = blok_job(P, 'terbitkan')
    LU = periksa_bagi(U, 'uji', ['1', '2', '3'], c); periksa_bagi(R, 'uji-peramban', ['1', '2'], c)
    def bagian(s): return next((re.fullmatch(r'matrix\.bagian == (\d+)', i).group(1) for i in s['if'] if re.fullmatch(r'matrix\.bagian == (\d+)', i)), None)
    tag = [k for k, s in enumerate(LU) if 'refs/tags/sistem-lama-terakhir' in s['isi']]; dok = [k for k, s in enumerate(LU) if 'uji_dokumen_sisa.py --wajib-tag' in s['isi']]
    ok('uji: ambil tag sistem-lama SEBELUM uji dokumen sisa dan DI BAGIAN YANG SAMA (runner lain tidak punya tagnya)',
       len(tag) == 1 and len(dok) == 1 and tag[0] < dok[0] and bagian(LU[tag[0]]) == bagian(LU[dok[0]]), (tag, dok, [bagian(LU[k]) for k in tag + dok]))
    ok('uji: penjaga ini sendiri ikut dijalankan (+ kontrol)', any('python3 alat-uji/periksa_ci.py && python3 alat-uji/periksa_ci.py --kontrol' in s['isi'] for s in LU))
    ok('terbitkan: menunggu uji & uji-peramban (semua bagian) dan hanya di main', 'needs: [uji, uji-peramban]' in TB and "if: github.ref == 'refs/heads/main' && github.event_name != 'pull_request'" in TB)
    G = t[GLADI]; GB = blok_job(G, 'gladi'); A = t[ALAT_GLADI]
    m = re.search(r"^SKENARIO_BAWAAN = \[([^\]]*)\]", A, re.M); sk = re.findall(r"'(\w+)'", m.group(1)) if m else []
    M = matriks(GB) or []
    mk = re.search(r'KELOMPOK=(\d+)', GB); K = int(mk.group(1)) if mk else 0
    ok('gladi: matriks = semua skenario bawaan alat gladi + kontrol-1..K (K = KELOMPOK)', sk and M == sk + ['kontrol-%d' % i for i in range(1, K + 1)] and K >= 1, (M, sk, K))
    ok('gladi: kontrol dibagi nomor modulo KELOMPOK (tiap kontrol tepat satu bagian) dan bagian tanpa kontrol = gagal',
       '[ $(( (i - 1) % KELOMPOK )) -eq $(( K - 1 )) ] || continue' in GB and 'test "$jalan" -ge 1 || gagal=1' in GB)
    LG = langkah(GB); g = [s for s in LG if s['nama'].startswith('GLADI —')]; k_ = [s for s in LG if s['nama'].startswith('KONTROL —')]
    ok('gladi: langkah skenario hanya di bagian skenario yang dipilih; langkah kontrol hanya di bagian kontrol',
       len(g) == 1 and any("!startsWith(matrix.bagian, 'kontrol-')" in i and 'env.GLADI_PILIHAN' in i for i in g[0]['if'])
       and len(k_) == 1 and any("startsWith(matrix.bagian, 'kontrol-')" in i for i in k_[0]['if']), [s['if'] for s in g + k_])
    ok('gladi: artefak bernama per bagian (nama sama di job paralel = unggahan bentrok)', 'name: laporan-gladi-tutup-buku-${{ matrix.bagian }}' in GB)
    return c


def jalan(t, diam=False):
    c = periksa(t); g = [x for x in c if not x[1]]
    if not diam:
        for n, ok_, k in c: print(('✓ ' if ok_ else '✗ ') + n + ('' if ok_ else ' → ' + str(k)[:400]))
        print('PEMBAGIAN CI: %d lulus · %d gagal' % (len(c) - len(g), len(g)))
    return g


def main():
    t = dict((p, baca(p)) for p in (PAGES, GLADI, ALAT_GLADI))
    if '--kontrol' in sys.argv:
        P = t[PAGES]; G = t[GLADI]
        i1 = P.index('        if: matrix.bagian == 1\n')
        rusak = [
            ('satu langkah uji kehilangan if (jalan di semua bagian)', PAGES, P[:i1] + P[i1 + len('        if: matrix.bagian == 1\n'):]),
            ('satu langkah uji di bagian 4 (tidak pernah jalan)', PAGES, P[:i1] + '        if: matrix.bagian == 4\n' + P[i1 + len('        if: matrix.bagian == 1\n'):]),
            ('uji dokumen sisa di bagian lain dari ambil tag', PAGES, re.sub(r'(        if: matrix\.bagian == )(\d)(\n        run: python3 alat-uji/uji_dokumen_sisa\.py --wajib-tag)', lambda m: m.group(1) + ('1' if m.group(2) != '1' else '2') + m.group(3), P)),
            ('push kembali menguji semua cabang (run ganda)', PAGES, P.replace('  push:\n    branches: [main]\n', '  push:\n')),
            ('uji-peramban hanya satu bagian di matriks', PAGES, P.replace('        bagian: [1, 2]\n', '        bagian: [1]\n')),
            ('terbitkan tidak menunggu uji-peramban', PAGES, P.replace('needs: [uji, uji-peramban]', 'needs: [uji]')),
            ('penjaga ini dicabut dari CI', PAGES, P.replace('python3 alat-uji/periksa_ci.py && python3 alat-uji/periksa_ci.py --kontrol', 'true')),
            ('gladi: skenario ritual hilang dari matriks', GLADI, G.replace('[latihan, gerbang, ritual, pintu, kontrol-1', '[latihan, gerbang, pintu, kontrol-1')),
            ('gladi: kelompok kontrol 2 padahal ada 3 bagian kontrol (kontrol ke-3 tak pernah jalan)', GLADI, G.replace('KELOMPOK=3', 'KELOMPOK=2')),
            ('gladi: artefak bernama sama di semua bagian', GLADI, G.replace('name: laporan-gladi-tutup-buku-${{ matrix.bagian }}', 'name: laporan-gladi-tutup-buku')),
            ('gladi: langkah skenario jalan juga di bagian kontrol', GLADI, G.replace("if: ${{ !startsWith(matrix.bagian, 'kontrol-') && contains(", "if: ${{ contains(")),
        ]
        kode = 0
        for nama, berkas, isi in rusak:
            if isi == t[berkas]: print('KONTROL BASI  ' + nama); kode = 3; continue
            t2 = dict(t); t2[berkas] = isi; g = jalan(t2, diam=True)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + (' → ' + g[0][0][:100] if g else ''))
            if not g: kode = 3
        print('KONTROL: %d kerusakan' % len(rusak)); sys.exit(kode)
    sys.exit(1 if jalan(t) else 0)


if __name__ == '__main__':
    main()
