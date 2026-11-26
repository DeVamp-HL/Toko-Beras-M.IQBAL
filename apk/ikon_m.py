#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ikon_m.py — logo toko di semua ikon. Owner 24–26 Nov 2026: padi emas (geometri persis logo "B" papan 23 Nov) + huruf M stensil tebal miring
bergaris bawah, ikon tablet TANPA LATAR ("transparan seperti SunmiSubScreen", juga di mode gelap), "samakan semua" (struk, layar, ikon).
Menggantikan logo "M" bercincin 23 Nov. Geometri = baru/js/inti/logo-toko.js (dicocokkan alat-uji/uji_tablet_tampilan.py); satuan kotak 108.

Satu sumber geometri → semua berkas ikon, TANPA Pillow / numpy (Mac owner tidak punya; CI tidak perlu):
    icon-sistem.svg                vektor (latar ubin hitam + logo emas; geometri sama persis)
    icon-sistem-512.png / -192     PWA "any maskable" — ubin hitam PENUH (peramban/iOS mengisi bagian bening dengan warnanya sendiri), logo di zona aman
    icon-sistem-180.png            apple-touch-icon        icon-sistem-32.png   favicon (logo diperbesar)
    icon-kasir-180.png / -32.png   ikon kasir darurat — sama dengan ikon sistem
    apk/ikon-depan-432.png         latar DEPAN ikon adaptif Android, BENING, emas gelap (terbaca di peluncur terang), di dalam lingkar aman 66/108
    apk/ikon-depan-malam-432.png   idem emas asli — dipasang ke mipmap-night-* (peluncur/sistem mode gelap)
    apk/ikon-pembuka-432.png       logo emas bening untuk layar pembuka (pasang.py menaruhnya di atas LATAR_APK)
Latar BELAKANG ikon adaptif = LATAR_ADAPTIF (bening) → peluncur menampilkan logo saja, tanpa kotak.

    python3 apk/ikon_m.py            → tulis ulang semua berkas di atas
    python3 apk/ikon_m.py --periksa  → keluar 1 bila berkas di repo berbeda dari hasil geometri ini (dipakai uji)
Perender: elips, tangkai (kurva → ruas), huruf (poligon genap-ganjil), 4×4 sampel per piksel (tepi halus), PNG lewat zlib.
"""
import os, sys, zlib, struct, math, re

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))

LATAR_APK = '#14110d'          # ubin & layar pembuka (hitam kecokelatan logo B)
LATAR_ADAPTIF = '#00000000'    # latar belakang ikon adaptif Android: BENING
LATAR = (0x14, 0x11, 0x0d)
EMAS = ((0xc9, 0xb3, 0x7a), (0xe6, 0xd7, 0xad))          # [batang, bulir] — mode gelap / di atas latar gelap
EMAS_GELAP = ((0x7a, 0x5a, 0x2a), (0x9a, 0x7a, 0x44))    # [batang, bulir] — di atas latar terang

# ---- geometri (satuan 108) — SAMA dengan baru/js/inti/logo-toko.js ----
BATANG = ((38, 84), (50, 66), (58, 48), (70, 26)); BATANG_TEBAL = 2.4
BULIR = [(62, 36, 4, 8, 30), (71, 42, 4, 8, 70), (56, 48, 4, 8, 25), (65, 55, 4, 8, 70), (50, 61, 4, 8, 20), (59, 67, 4, 8, 70), (70, 28, 3.5, 7, 35)]
M_JALUR = ('M39.05 34.73 L38.33 37.6 Q38.2 38.11 38.51 38.29 Q38.63 38.37 38.8 38.42 L38.8 38.42 Q38.96 38.46 39.1 38.56 L38.98 39 L36.17 39 '
           'L36.28 38.56 Q36.43 38.46 36.62 38.41 L36.62 38.41 Q36.8 38.37 36.96 38.29 Q37.35 38.11 37.48 37.6 L38.77 32.46 L39.05 34.73Z'
           'M39.24 31.51 Q39.2 31.24 39.17 31.04 Q39.01 31 38.84 30.96 L38.84 30.96 Q38.68 30.93 38.52 30.89 Q38.17 30.79 37.99 30.71 L38.17 29.98 '
           'L41.23 29.98 L42.18 37.18 L41.27 39 L40.18 39 L39.24 31.51Z'
           'M42.51 35.15 L45.1 29.98 L48.45 29.98 L48.33 30.46 Q48.14 30.53 47.98 30.56 L47.98 30.56 Q47.81 30.6 47.66 30.66 Q47.35 30.8 47.25 31.2 '
           'L45.6 37.79 Q45.5 38.19 45.75 38.33 Q45.86 38.39 46.01 38.43 L46.01 38.43 Q46.16 38.46 46.31 38.53 L46.2 39 L42.33 39 L42.45 38.53 '
           'Q42.64 38.46 42.81 38.43 L42.81 38.43 Q42.98 38.39 43.12 38.33 Q43.44 38.19 43.54 37.79 L45.15 31.34 L45.12 31.34 L42.66 36.26 L42.51 35.15Z')
GARIS = (33.5, 48.5, 42, 0.72)
KOTAK = (33.5, 20.5, 79, 85.5)          # x0, y0, x1, y1 — isi logo; pusat & tinggi untuk menskala
PUSAT = ((KOTAK[0] + KOTAK[2]) / 2, (KOTAK[1] + KOTAK[3]) / 2); TINGGI = KOTAK[3] - KOTAK[1]


def _kontur():
    """M_JALUR → daftar poligon (kurva Q dipecah 6 ruas)."""
    out, cur, p = [], [], None
    for k, angka in re.findall(r'([MLQZ])([^MLQZ]*)', M_JALUR):
        v = [float(x) for x in angka.replace(',', ' ').split()]
        if k == 'M': cur = [(v[0], v[1])]; p = cur[-1]
        elif k == 'L': cur.append((v[0], v[1])); p = cur[-1]
        elif k == 'Q':
            for i in range(1, 7):
                t = i / 6; u = 1 - t
                cur.append((u * u * p[0] + 2 * u * t * v[0] + t * t * v[2], u * u * p[1] + 2 * u * t * v[1] + t * t * v[3]))
            p = cur[-1]
        elif k == 'Z': out.append(cur); cur = []
    return out


def _ruas_batang(n=24):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = BATANG; t_ = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        t_.append((u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3, u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3))
    return [(t_[i], t_[i + 1]) for i in range(n)]


KONTUR = _kontur(); RUAS = _ruas_batang()


def _dalam_poligon(polis, x, y):
    dalam = False
    for p in polis:
        n = len(p)
        for i in range(n):
            ax, ay = p[i]; bx, by = p[(i + 1) % n]
            if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay): dalam = not dalam
    return dalam


def _jarak_ruas(x, y, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / L)) if L else 0.0
    return math.hypot(x - a[0] - t * dx, y - a[1] - t * dy)


def lapisan(warna):
    """Daftar (warna, kotak satuan, uji(u, v) → bool) dari bawah ke atas."""
    batang, bulir = warna; r = BATANG_TEBAL / 2; L = []
    for a, b in RUAS:
        L.append((batang, (min(a[0], b[0]) - r, min(a[1], b[1]) - r, max(a[0], b[0]) + r, max(a[1], b[1]) + r), (lambda a, b: lambda u, v: _jarak_ruas(u, v, a, b) <= r)(a, b)))
    for cx, cy, rx, ry, sd in BULIR:
        c, s = math.cos(math.radians(sd)), math.sin(math.radians(sd)); ex = math.hypot(rx * c, ry * s); ey = math.hypot(rx * s, ry * c)
        L.append((bulir, (cx - ex, cy - ey, cx + ex, cy + ey), (lambda cx, cy, rx, ry, c, s: lambda u, v: (((u - cx) * c + (v - cy) * s) / rx) ** 2 + ((-(u - cx) * s + (v - cy) * c) / ry) ** 2 <= 1)(cx, cy, rx, ry, c, s)))
    xs = [x for p in KONTUR for x, _ in p]; ys = [y for p in KONTUR for _, y in p]
    L.append((batang, (min(xs), min(ys), max(xs), max(ys)), lambda u, v: _dalam_poligon(KONTUR, u, v)))
    x0, x1, gy, gt = GARIS
    L.append((batang, (x0, gy - gt / 2, x1, gy + gt / 2), lambda u, v: x0 <= u <= x1 and abs(v - gy) <= gt / 2))
    return L


def lukis(px, W, H, cx, cy, tinggi, warna):
    """Tumpuk logo (berpusat di cx, cy; tinggi isi `tinggi` piksel) ke px (RGBA premultiplied 0..1, W × H)."""
    N = 4; off = [(i + 0.5) / N for i in range(N)]; s = tinggi / TINGGI
    for rgb, (a0, b0, a1, b1), uji in lapisan(warna):
        X0 = max(0, int(cx + (a0 - PUSAT[0]) * s) - 1); X1 = min(W, int(cx + (a1 - PUSAT[0]) * s) + 2)
        Y0 = max(0, int(cy + (b0 - PUSAT[1]) * s) - 1); Y1 = min(H, int(cy + (b1 - PUSAT[1]) * s) + 2)
        for y in range(Y0, Y1):
            for x in range(X0, X1):
                n = 0
                for oy in off:
                    v = PUSAT[1] + (y + oy - cy) / s
                    for ox in off:
                        if uji(PUSAT[0] + (x + ox - cx) / s, v): n += 1
                if n:
                    a = n / (N * N); q = px[y * W + x]; k = 1 - a
                    q[0] = rgb[0] / 255 * a + q[0] * k; q[1] = rgb[1] / 255 * a + q[1] * k; q[2] = rgb[2] / 255 * a + q[2] * k; q[3] = a + q[3] * k


def render(ukuran, warna=EMAS, isi=0.6, latar=True):
    """Kanvas persegi `ukuran`: latar ubin penuh (latar=True) atau bening, logo setinggi isi × ukuran di tengah."""
    px = [[LATAR[0] / 255, LATAR[1] / 255, LATAR[2] / 255, 1.0] if latar else [0.0, 0.0, 0.0, 0.0] for _ in range(ukuran * ukuran)]
    lukis(px, ukuran, ukuran, ukuran / 2, ukuran / 2, ukuran * isi, warna)
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
    hx = lambda c: '#%02x%02x%02x' % c; b, u = hx(EMAS[0]), hx(EMAS[1])
    s = 512 * 0.6 / TINGGI; tx, ty = 256 - PUSAT[0] * s, 256 - PUSAT[1] * s
    bulir = ''.join('<ellipse cx="%g" cy="%g" rx="%g" ry="%g" transform="rotate(%g %g %g)"/>' % (x, y, rx, ry, a, x, y) for x, y, rx, ry, a in BULIR)
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = BATANG
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n'
            '  <!-- Logo toko: padi + M stensil (owner 26 Nov 2026). Dibuat apk/ikon_m.py — ubah geometrinya DI SANA (dan baru/js/inti/logo-toko.js), lalu jalankan ulang. -->\n'
            '  <rect width="512" height="512" fill="%s"/>\n'
            '  <g transform="translate(%.3f %.3f) scale(%.5f)">\n'
            '    <path d="M%g %g C %g %g, %g %g, %g %g" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round"/>\n'
            '    <g fill="%s">%s</g>\n    <path d="%s" fill="%s"/>\n'
            '    <path d="M%g %gL%g %g" stroke="%s" stroke-width="%g"/>\n  </g>\n</svg>\n') % (
        LATAR_APK, tx, ty, s, x0, y0, x1, y1, x2, y2, x3, y3, b, BATANG_TEBAL, u, bulir, M_JALUR, b, GARIS[0], GARIS[2], GARIS[1], GARIS[2], b, GARIS[3])


# nama, ukuran, warna, tinggi isi (bagian kanvas), latar ubin
BERKAS = [
    ('icon-sistem-512.png', 512, EMAS, 0.6, True),     # setengah diagonal isi ≈ 0,37 kanvas < lingkar aman maskable 0,4
    ('icon-sistem-192.png', 192, EMAS, 0.6, True),
    ('icon-sistem-180.png', 180, EMAS, 0.66, True),
    ('icon-sistem-32.png', 32, EMAS, 0.9, True),
    ('icon-kasir-180.png', 180, EMAS, 0.66, True),
    ('icon-kasir-32.png', 32, EMAS, 0.9, True),
    ('apk/ikon-depan-432.png', 432, EMAS_GELAP, 0.48, False),        # setengah diagonal isi ≈ 0,29 kanvas < lingkar aman 33/108 = 0,305
    ('apk/ikon-depan-malam-432.png', 432, EMAS, 0.48, False),
    ('apk/ikon-pembuka-432.png', 432, EMAS, 0.8, False),
]


def semua():
    out = {'icon-sistem.svg': svg().encode('utf-8')}
    for nama, n, w, isi, lt in BERKAS: out[nama] = png(n, render(n, w, isi, lt))
    return out


def main():
    hasil = semua()
    if '--periksa' in sys.argv:
        beda = [n for n, b in hasil.items() if not os.path.exists(os.path.join(AKAR, n)) or open(os.path.join(AKAR, n), 'rb').read() != b]
        print('IKON LOGO: ' + ('SAMA dengan geometri' if not beda else 'BEDA: ' + ', '.join(beda))); sys.exit(1 if beda else 0)
    for n, b in hasil.items():
        with open(os.path.join(AKAR, n), 'wb') as f: f.write(b)
        print('  tulis %s (%d byte)' % (n, len(b)))


if __name__ == '__main__':
    main()
