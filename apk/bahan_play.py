#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bahan_play.py — gambar halaman aplikasi di Google Play (docs/google-play.md) dari logo toko (apk/ikon_m.py — owner 26 Nov 2026: padi + M stensil,
"samakan semua"; dulu logo "M" bercincin). Tanpa Pillow / numpy: geometri & perender diambil dari ikon_m.py, PNG ditulis lewat zlib.

    docs/google-play/ikon-512.png                   ikon Play: 512 × 512, PNG 32-bit. Play memotong sudut & memberi bayangan sendiri → latar PENUH
                                                    (sama persis dengan icon-sistem-512.png), logo di dalam zona aman.
    docs/google-play/grafis-unggulan-1024x500.png   feature graphic: 1024 × 500, PNG 24-bit TANPA alfa (syarat Play). Logo emas di tengah latar
                                                    hitam kecokelatan + garis emas tipis. Sengaja TANPA tulisan: Play bisa menimpa/memotong tepi grafis.

    python3 apk/bahan_play.py            → tulis ulang kedua berkas
    python3 apk/bahan_play.py --periksa  → keluar 1 bila berkas di repo berbeda dari hasil geometri ini (dipakai alat-uji/uji_google_play.py)
"""
import os, sys, zlib, struct, math

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
try:
    import ikon_m  # noqa: E402  (apk/ikon_m.py — logo toko)
except ImportError:
    ikon_m = None

KELUAR = os.path.join(AKAR, 'docs', 'google-play')
IKON = os.path.join(KELUAR, 'ikon-512.png')
GRAFIS = os.path.join(KELUAR, 'grafis-unggulan-1024x500.png')
G_LEBAR, G_TINGGI = 1024, 500
G_TINGGI_LOGO = 0.62  # tinggi isi logo terhadap tinggi grafis
G_GARIS = 0.55        # kekuatan garis emas kiri-kanan
LATAR_DALAM, LATAR_LUAR = (0x24, 0x1e, 0x16), (0x0e, 0x0c, 0x09)   # gradasi radial di belakang logo


def png_rgb(w, h, px):
    """PNG 24-bit (tipe warna 2, tanpa alfa). px = daftar [r, g, b, a] 0..1 di atas latar opak (a selalu 1) → r, g, b langsung."""
    baris = bytearray()
    for y in range(h):
        baris.append(0)
        for x in range(w):
            r, g, b, _ = px[y * w + x]
            baris += bytes((min(255, round(r * 255)), min(255, round(g * 255)), min(255, round(b * 255))))
    def potong(jenis, isi): return struct.pack('>I', len(isi)) + jenis + isi + struct.pack('>I', zlib.crc32(jenis + isi) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + potong(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + potong(b'IDAT', zlib.compress(bytes(baris), 9)) + potong(b'IEND', b'')


def campur(a, b, t):
    t = max(0.0, min(1.0, t)); return tuple(a[k] + (b[k] - a[k]) * t for k in range(3))


def grafis():
    """Feature graphic: latar radial hitam kecokelatan, logo emas di tengah, dua garis emas tipis memudar ke tepi."""
    W, H = G_LEBAR, G_TINGGI; N = 4; off = [(i + 0.5) / N for i in range(N)]
    px = [None] * (W * H)
    cx, cy = W / 2.0, H / 2.0; R = W * 0.62
    for y in range(H):
        for x in range(W):
            c = campur(LATAR_DALAM, LATAR_LUAR, math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.6) / R)
            px[y * W + x] = [c[0] / 255, c[1] / 255, c[2] / 255, 1.0]

    def tumpuk(i, rgb, a):
        if a <= 0: return
        q = px[i]; r = 1 - a
        q[0] = rgb[0] / 255 * a + q[0] * r; q[1] = rgb[1] / 255 * a + q[1] * r; q[2] = rgb[2] / 255 * a + q[2] * r

    tinggi = H * G_TINGGI_LOGO
    ikon_m.lukis(px, W, H, cx, cy, tinggi, ikon_m.EMAS)
    # garis emas tipis kiri & kanan logo, memudar ke tepi kanvas
    rl = tinggi * 0.5 + 30; tebal = 1.1
    for sisi in (-1, 1):
        mulai, ujung = cx + sisi * rl, (60 if sisi < 0 else W - 60)
        panjang = abs(ujung - mulai)
        for x in range(int(min(mulai, ujung)), int(max(mulai, ujung)) + 1):
            u = abs(x + 0.5 - mulai) / panjang
            if u > 1: continue
            a = G_GARIS * (1 - u) ** 1.6
            for y in range(int(cy) - 2, int(cy) + 3):
                n = sum(1 for oy in off if abs(y + oy - cy) <= tebal / 2)
                if n: tumpuk(y * W + x, campur(ikon_m.EMAS[0], ikon_m.EMAS[1], 0.25 + 0.5 * u), a * n / N)
    return png_rgb(W, H, px)


def ikon():
    return ikon_m.png(512, ikon_m.render(512))


def main():
    if ikon_m is None:
        print('GAGAL: apk/ikon_m.py (logo toko) belum ada di cabang ini — gambar Play dibuat dari geometrinya'); sys.exit(2)
    hasil = {IKON: ikon(), GRAFIS: grafis()}
    if '--periksa' in sys.argv:
        beda = [os.path.relpath(p, AKAR) for p, isi in hasil.items() if not os.path.exists(p) or open(p, 'rb').read() != isi]
        print('bahan Play: ' + ('BEDA dari geometri logo toko: ' + ', '.join(beda) if beda else 'sama dengan geometri logo toko')); sys.exit(1 if beda else 0)
    os.makedirs(KELUAR, exist_ok=True)
    for p, isi in hasil.items():
        with open(p, 'wb') as f: f.write(isi)
        print('  %s (%d byte)' % (os.path.relpath(p, AKAR), len(isi)))


if __name__ == '__main__':
    main()
