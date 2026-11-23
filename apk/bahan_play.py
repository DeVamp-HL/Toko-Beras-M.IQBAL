#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bahan_play.py — gambar halaman aplikasi di Google Play (23 Nov 2026, docs/google-play.md) dari logo "M" (apk/ikon_m.py — PR #188, cabang
paket/obrolan-logo-wadah). Tanpa Pillow / numpy: geometri, gradasi & perender diambil dari ikon_m.py, PNG ditulis lewat zlib.

    docs/google-play/ikon-512.png                   ikon Play: 512 × 512, PNG 32-bit. Play memotong sudut & memberi bayangan sendiri → latar PENUH
                                                    (sama persis dengan icon-sistem-512.png logo M), simbol di dalam zona aman.
    docs/google-play/grafis-unggulan-1024x500.png   feature graphic: 1024 × 500, PNG 24-bit TANPA alfa (syarat Play). Lambang M bercincin di tengah
                                                    latar hitam malam + garis emas tipis. Sengaja TANPA tulisan: Play bisa menimpa/memotong tepi grafis.

    python3 apk/bahan_play.py            → tulis ulang kedua berkas
    python3 apk/bahan_play.py --periksa  → keluar 1 bila berkas di repo berbeda dari hasil geometri ini (dipakai alat-uji/uji_google_play.py)
"""
import os, sys, zlib, struct, math

SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
try:
    import ikon_m  # noqa: E402  (apk/ikon_m.py — logo M)
except ImportError:
    ikon_m = None

KELUAR = os.path.join(AKAR, 'docs', 'google-play')
IKON = os.path.join(KELUAR, 'ikon-512.png')
GRAFIS = os.path.join(KELUAR, 'grafis-unggulan-1024x500.png')
G_LEBAR, G_TINGGI = 1024, 500
G_SKALA = 0.74          # lambang (cincin Ø 380 pada kanvas 512) → Ø ≈ 281 px di grafis setinggi 500
G_GARIS = 0.55          # kekuatan garis emas kiri-kanan


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


def grafis():
    """Feature graphic: latar radial hitam malam, cincin + M emas di tengah, dua garis emas tipis memudar ke tepi."""
    W, H = G_LEBAR, G_TINGGI; N = 4; off = [(i + 0.5) / N for i in range(N)]
    px = [None] * (W * H)
    cx, cy = W / 2.0, H / 2.0; R = W * 0.62
    for y in range(H):
        for x in range(W):
            t = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.6) / R
            c = ikon_m.campur([(0, ikon_m.LATAR_DALAM), (1, ikon_m.LATAR_LUAR)], t)
            px[y * W + x] = [c[0] / 255, c[1] / 255, c[2] / 255, 1.0]

    def tumpuk(i, rgb, a):
        if a <= 0: return
        q = px[i]; r = 1 - a
        q[0] = rgb[0] / 255 * a + q[0] * r; q[1] = rgb[1] / 255 * a + q[1] * r; q[2] = rgb[2] / 255 * a + q[2] * r

    s = H / 512.0 * G_SKALA   # satuan geometri ikon 512 → piksel grafis
    # cincin: (jari-jari, tebal, alfa) dalam satuan geometri 512 — dua cincin logo + satu gema samar di luar
    for r0, w0, alfa in ((190, 5, 0.95), (176, 1.6, 0.42), (214, 1.0, 0.16)):
        r = r0 * s; w = max(0.9, w0 * s)
        a0, a1 = r - w / 2, r + w / 2
        for y in range(max(0, int(cy - a1 - 1)), min(H, int(cy + a1 + 2))):
            for x in range(max(0, int(cx - a1 - 1)), min(W, int(cx + a1 + 2))):
                dd = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if dd < a0 - 1 or dd > a1 + 1: continue
                n = sum(1 for oy in off for ox in off if a0 <= math.hypot(x + ox - cx, y + oy - cy) <= a1)
                if n: tumpuk(y * W + x, ikon_m.campur(ikon_m.EMAS, ((x - (cx - a1)) + (y - (cy - a1))) / (4 * a1)), alfa * n / (N * N))
    # huruf M (skala_m 1.12 seperti ikon)
    sm = s * 1.12; x0 = cx - ikon_m.M_LEBAR * sm / 2; y0 = cy - ikon_m.M_TINGGI * sm / 2
    poli = [[(x0 + px_ * sm, y0 + py_ * sm) for (px_, py_) in p] for p in ikon_m.M_BENTUK]
    xs = [a for p in poli for (a, _) in p]; ys = [b for p in poli for (_, b) in p]; bx0, by0, bx1, by1 = min(xs), min(ys), max(xs), max(ys)
    for y in range(max(0, int(by0) - 1), min(H, int(by1) + 2)):
        for x in range(max(0, int(bx0) - 1), min(W, int(bx1) + 2)):
            n = sum(1 for oy in off for ox in off if any(ikon_m.dalam_poligon(p, x + ox, y + oy) for p in poli))
            if n: tumpuk(y * W + x, ikon_m.campur(ikon_m.EMAS, (x - bx0) / (bx1 - bx0) * 0.6 + (y - by0) / (by1 - by0) * 0.4), n / (N * N))
    # garis emas tipis kiri & kanan lambang, memudar ke tepi kanvas
    rl = 214 * s + 14; tebal = 1.1
    for sisi in (-1, 1):
        mulai, ujung = cx + sisi * rl, (60 if sisi < 0 else W - 60)
        panjang = abs(ujung - mulai)
        for x in range(int(min(mulai, ujung)), int(max(mulai, ujung)) + 1):
            u = abs(x + 0.5 - mulai) / panjang
            if u > 1: continue
            a = G_GARIS * (1 - u) ** 1.6
            for y in range(int(cy) - 2, int(cy) + 3):
                n = sum(1 for oy in off if abs(y + oy - cy) <= tebal / 2)
                if n: tumpuk(y * W + x, ikon_m.campur(ikon_m.EMAS, 0.25 + 0.5 * u), a * n / N)
    return png_rgb(W, H, px)


def ikon():
    return ikon_m.png(512, ikon_m.render(512, ikon_m.susun(512)))


def main():
    if ikon_m is None:
        print('GAGAL: apk/ikon_m.py (logo M, PR #188) belum ada di cabang ini — gambar Play dibuat dari geometrinya'); sys.exit(2)
    hasil = {IKON: ikon(), GRAFIS: grafis()}
    if '--periksa' in sys.argv:
        beda = [os.path.relpath(p, AKAR) for p, isi in hasil.items() if not os.path.exists(p) or open(p, 'rb').read() != isi]
        print('bahan Play: ' + ('BEDA dari geometri logo M: ' + ', '.join(beda) if beda else 'sama dengan geometri logo M')); sys.exit(1 if beda else 0)
    os.makedirs(KELUAR, exist_ok=True)
    for p, isi in hasil.items():
        with open(p, 'wb') as f: f.write(isi)
        print('  %s (%d byte)' % (os.path.relpath(p, AKAR), len(isi)))


if __name__ == '__main__':
    main()
