#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ikon_m.py — logo aplikasi "M" (owner 23 Nov 2026: "Ikon logo aplikasi gak rapi di tablet … ganti logo" → "logo M aja gak perlu IQ").
Huruf M bergaya serif kontras tinggi (batang tipis–tebal) berwarna emas di dalam cincin tipis, di atas latar hitam malam (identitas Kaca Emas Malam).

Satu sumber geometri → semua berkas ikon, TANPA Pillow / numpy (Mac owner tidak punya; CI tidak perlu):
    icon-sistem.svg            vektor (sumber yang bisa dilihat; geometri sama persis)
    icon-sistem-512.png        PWA "any maskable" (latar penuh; simbol di dalam zona aman 80 %)
    icon-sistem-192.png        PWA + ikon notifikasi
    icon-sistem-180.png        apple-touch-icon
    icon-sistem-32.png         favicon (tanpa cincin — terlalu tipis di 32 px; huruf diperbesar)
    apk/ikon-depan-432.png     latar DEPAN ikon adaptif Android (transparan, simbol saja, di dalam lingkar aman 66 dp dari kanvas 108 dp)
Latar BELAKANG ikon adaptif = warna polos LATAR_APK (apk/pasang.py). Dulu pasang.py menempel ikon 512 utuh (dengan kotak & lingkaran krem) ke latar
depan → "kotak di dalam kotak" di peluncur tablet; sekarang simbol transparan + latar warna = rapi di bentuk apa pun (lingkaran, squircle, kotak).

    python3 apk/ikon_m.py            → tulis ulang semua berkas di atas
    python3 apk/ikon_m.py --periksa  → keluar 1 bila berkas di repo berbeda dari hasil geometri ini (dipakai uji)
Perender: poligon cembung + cincin, 4×4 sampel per piksel (tepi halus), PNG lewat zlib.
"""
import os, sys, zlib, struct, math

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))

LATAR_DALAM = (0x1d, 0x21, 0x22); LATAR_LUAR = (0x08, 0x0a, 0x0b)   # gradasi radial hitam malam
LATAR_APK = '#101314'                                                 # warna latar belakang ikon adaptif Android (rata-rata gradasi)
EMAS = [(0.0, (0xf8, 0xe7, 0xb4)), (0.55, (0xd6, 0xb0, 0x5a)), (1.0, (0xa8, 0x7f, 0x2f))]   # gradasi emas diagonal

# Huruf M dalam kotak 202 × 176 (titik kiri-atas = 0,0): batang kiri tipis, diagonal kiri tebal, diagonal kanan tipis, batang kanan tebal, kaki (serif) rambut.
M_LEBAR, M_TINGGI = 202.0, 176.0
M_BENTUK = [
    [(16, 0), (25, 0), (25, 176), (16, 176)],                 # batang kiri (tipis)
    [(18, 0), (51, 0), (107, 160), (100, 176), (93, 176)],    # diagonal kiri (tebal)
    [(95, 168), (170, 0), (180, 0), (104, 176), (99, 176)],   # diagonal kanan (tipis)
    [(154, 0), (186, 0), (186, 176), (154, 176)],             # batang kanan (tebal)
    [(2, 0), (25, 0), (25, 4), (2, 4)],                       # kaki atas kiri
    [(0, 172), (42, 172), (42, 176), (0, 176)],               # kaki bawah kiri
    [(138, 172), (202, 172), (202, 176), (138, 176)],         # kaki bawah kanan
    [(186, 0), (202, 0), (202, 4), (186, 4)],                 # kaki atas kanan
]


def campur(stops, t):
    t = max(0.0, min(1.0, t))
    for i in range(1, len(stops)):
        if t <= stops[i][0]:
            a, ca = stops[i - 1]; b, cb = stops[i]; u = (t - a) / (b - a) if b > a else 0
            return tuple(ca[k] + (cb[k] - ca[k]) * u for k in range(3))
    return stops[-1][1]


def susun(ukuran, cincin=True, skala_m=1.12, latar=True, skala_simbol=1.0):
    """Daftar lapisan dalam koordinat piksel kanvas `ukuran`. skala_simbol mengecilkan simbol (cincin + M) terhadap pusat (ikon adaptif)."""
    k = ukuran / 512.0; c = ukuran / 2.0; s = k * skala_simbol
    lap = []
    if latar: lap.append(('latar', None))
    if cincin:
        lap.append(('cincin', (c, c, 190 * s, 5 * s, 0.95)))
        lap.append(('cincin', (c, c, 176 * s, 1.6 * s, 0.42)))
    sm = s * skala_m; x0 = c - M_LEBAR * sm / 2; y0 = c - M_TINGGI * sm / 2
    lap.append(('m', [[(x0 + x * sm, y0 + y * sm) for (x, y) in p] for p in M_BENTUK]))
    return lap


def dalam_poligon(p, x, y):
    """Poligon cembung searah jarum jam (sumbu y ke bawah): semua sisi di kanan."""
    n = len(p)
    for i in range(n):
        ax, ay = p[i]; bx, by = p[(i + 1) % n]
        if (bx - ax) * (y - ay) - (by - ay) * (x - ax) < 0: return False
    return True


def render(ukuran, lapisan):
    N = 4; off = [(i + 0.5) / N for i in range(N)]
    px = [[0.0, 0.0, 0.0, 0.0] for _ in range(ukuran * ukuran)]   # RGBA premultiplied 0..1
    def tumpuk(i, rgb, a):
        if a <= 0: return
        q = px[i]; r = 1 - a
        q[0] = rgb[0] / 255 * a + q[0] * r; q[1] = rgb[1] / 255 * a + q[1] * r; q[2] = rgb[2] / 255 * a + q[2] * r; q[3] = a + q[3] * r
    for jenis, d in lapisan:
        if jenis == 'latar':
            c = ukuran / 2.0; R = ukuran * 0.72
            for y in range(ukuran):
                for x in range(ukuran):
                    t = math.hypot(x + 0.5 - c, y + 0.5 - ukuran * 0.42) / R
                    tumpuk(y * ukuran + x, campur([(0, LATAR_DALAM), (1, LATAR_LUAR)], t), 1.0)
        elif jenis == 'cincin':
            cx, cy, r, w, alfa = d; r0, r1 = r - w / 2, r + w / 2
            lo, hi = max(0, int(cx - r1 - 1)), min(ukuran, int(cx + r1 + 2))
            for y in range(lo, hi):
                for x in range(lo, hi):
                    dd = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                    if dd < r0 - 1 or dd > r1 + 1: continue
                    n = 0
                    for oy in off:
                        for ox in off:
                            e = math.hypot(x + ox - cx, y + oy - cy)
                            if r0 <= e <= r1: n += 1
                    if n:
                        t = ((x - (cx - r1)) + (y - (cy - r1))) / (4 * r1)
                        tumpuk(y * ukuran + x, campur(EMAS, t), alfa * n / (N * N))
        elif jenis == 'm':
            xs = [x for p in d for (x, _) in p]; ys = [y for p in d for (_, y) in p]
            bx0, by0, bx1, by1 = min(xs), min(ys), max(xs), max(ys)
            for y in range(max(0, int(by0) - 1), min(ukuran, int(by1) + 2)):
                for x in range(max(0, int(bx0) - 1), min(ukuran, int(bx1) + 2)):
                    n = 0
                    for oy in off:
                        for ox in off:
                            sx, sy = x + ox, y + oy
                            if any(dalam_poligon(p, sx, sy) for p in d): n += 1
                    if n:
                        t = ((x - bx0) / (bx1 - bx0) * 0.6 + (y - by0) / (by1 - by0) * 0.4)
                        tumpuk(y * ukuran + x, campur(EMAS, t), n / (N * N))
    return px


def png(ukuran, px):
    baris = bytearray()
    for y in range(ukuran):
        baris.append(0)
        for x in range(ukuran):
            r, g, b, a = px[y * ukuran + x]
            if a > 0: r, g, b = r / a, g / a, b / a
            baris += bytes((min(255, round(r * 255)), min(255, round(g * 255)), min(255, round(b * 255)), min(255, round(a * 255))))
    def potong(jenis, isi): return struct.pack('>I', len(isi)) + jenis + isi + struct.pack('>I', zlib.crc32(jenis + isi) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + potong(b'IHDR', struct.pack('>IIBBBBB', ukuran, ukuran, 8, 6, 0, 0, 0)) + potong(b'IDAT', zlib.compress(bytes(baris), 9)) + potong(b'IEND', b'')


def svg():
    hx = lambda c: '#%02x%02x%02x' % c
    sm = 1.12; x0 = 256 - M_LEBAR * sm / 2; y0 = 256 - M_TINGGI * sm / 2   # = skala_m bawaan susun()
    m = ''.join('<polygon points="%s"/>' % ' '.join('%g,%g' % (round(x0 + x * sm, 2), round(y0 + y * sm, 2)) for (x, y) in p) for p in M_BENTUK)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n'
            '  <!-- Logo "M" (owner 23 Nov 2026). Dibuat apk/ikon_m.py — ubah geometrinya DI SANA, lalu jalankan ulang (PNG ikut). -->\n'
            '  <defs><radialGradient id="malam" cx="50%%" cy="42%%" r="72%%"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>\n'
            '    <linearGradient id="emas" x1="0" y1="0" x2="1" y2="1">%s</linearGradient></defs>\n'
            '  <rect width="512" height="512" fill="url(#malam)"/>\n'
            '  <circle cx="256" cy="256" r="190" fill="none" stroke="url(#emas)" stroke-width="5" opacity=".95"/>\n'
            '  <circle cx="256" cy="256" r="176" fill="none" stroke="url(#emas)" stroke-width="1.6" opacity=".42"/>\n'
            '  <g fill="url(#emas)">%s</g>\n</svg>\n') % (hx(LATAR_DALAM), hx(LATAR_LUAR), ''.join('<stop offset="%g" stop-color="%s"/>' % (o, hx(c)) for o, c in EMAS), m)


BERKAS = [
    ('icon-sistem-512.png', 512, {}),
    ('icon-sistem-192.png', 192, {}),
    ('icon-sistem-180.png', 180, {}),
    ('icon-sistem-32.png', 32, {'cincin': False, 'skala_m': 1.95}),
    ('apk/ikon-depan-432.png', 432, {'latar': False, 'skala_simbol': 0.78}),   # cincin luar Ø ≈ 0,59 kanvas — di dalam lingkar aman 66/108 dp = 0,61
]


def semua():
    out = {'icon-sistem.svg': svg().encode('utf-8')}
    for nama, n, o in BERKAS: out[nama] = png(n, render(n, susun(n, **o)))
    return out


def main():
    hasil = semua()
    if '--periksa' in sys.argv:
        beda = [n for n, b in hasil.items() if not os.path.exists(os.path.join(AKAR, n)) or open(os.path.join(AKAR, n), 'rb').read() != b]
        print('IKON M: ' + ('SAMA dengan geometri' if not beda else 'BEDA: ' + ', '.join(beda))); sys.exit(1 if beda else 0)
    for n, b in hasil.items():
        with open(os.path.join(AKAR, n), 'wb') as f: f.write(b)
        print('  tulis %s (%d byte)' % (n, len(b)))


if __name__ == '__main__':
    main()
