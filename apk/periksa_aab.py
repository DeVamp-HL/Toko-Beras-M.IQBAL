#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
periksa_aab.py — pemeriksa AAB (Android App Bundle) untuk Google Play, dijalankan apk.yml SESUDAH AAB ditandatangani. Tanpa pustaka luar.

Yang dipegang (supaya penolakan Play ketahuan di runner, bukan saat owner mengunggah):
  · berkas ZIP berbentuk bundel: base/manifest/AndroidManifest.xml + BundleConfig.pb
  · bertanda tangan JAR (META-INF/*.SF + *.RSA/*.EC) — Play menolak bundel tanpa tanda tangan kunci unggah
  · pustaka native 64-bit (base/lib/arm64-v8a, x86_64) mendukung halaman memori 16 KB: tiap segmen PT_LOAD p_align >= 16384
    (Play: aplikasi yang menyasar Android 15+ wajib mendukung 16 KB di perangkat 64-bit). Hari ini bundel kita TANPA pustaka native
    (Capacitor, Firebase, pustaka SUNMI semuanya Java/Kotlin) — pemeriksaan ini penjaga kalau suatu hari ada pustaka ber-.so masuk.

    python3 apk/periksa_aab.py apk/keluaran/toko-beras-kasir-1.40.aab   → 0 = lulus, 1 = gagal
"""
import re, struct, sys, zipfile

HALAMAN_16K = 16384
ABI_64 = ('arm64-v8a', 'x86_64')


def ratakan_elf(data):
    """(kelas_bit, [p_align tiap PT_LOAD]) dari isi berkas .so; None bila bukan ELF."""
    if len(data) < 0x40 or data[:4] != b'\x7fELF': return None
    kelas, urut = data[4], data[5]
    e = '<' if urut == 1 else '>'
    if kelas == 2:
        phoff = struct.unpack_from(e + 'Q', data, 0x20)[0]; phentsize, phnum = struct.unpack_from(e + 'HH', data, 0x36)
        bentuk, i_align = e + 'IIQQQQQQ', 7
    elif kelas == 1:
        phoff = struct.unpack_from(e + 'I', data, 0x1C)[0]; phentsize, phnum = struct.unpack_from(e + 'HH', data, 0x2A)
        bentuk, i_align = e + 'IIIIIIII', 7
    else:
        return None
    rata = []
    for k in range(phnum):
        o = phoff + k * phentsize
        if o + struct.calcsize(bentuk) > len(data): break
        f = struct.unpack_from(bentuk, data, o)
        if f[0] == 1: rata.append(f[i_align])   # PT_LOAD
    return (64 if kelas == 2 else 32), rata


def periksa(jalur):
    """Daftar (ok, kalimat). Murni terhadap isi berkas; dipakai juga oleh alat-uji/uji_google_play.py."""
    h = []
    try: z = zipfile.ZipFile(jalur)
    except Exception as e: return [(False, 'bukan berkas ZIP/AAB: %r' % e)]
    with z:
        nama = z.namelist()
        h.append(('base/manifest/AndroidManifest.xml' in nama and 'BundleConfig.pb' in nama,
                  'berbentuk bundel (base/manifest/AndroidManifest.xml + BundleConfig.pb)'))
        sf = [n for n in nama if re.match(r'^META-INF/[^/]+\.SF$', n)]
        blok = [n for n in nama if re.match(r'^META-INF/[^/]+\.(RSA|EC|DSA)$', n)]
        h.append((bool(sf) and bool(blok), 'bertanda tangan kunci unggah (META-INF/*.SF + *.RSA/*.EC: %d + %d)' % (len(sf), len(blok))))
        so = [n for n in nama if re.match(r'^[^/]+/lib/[^/]+/[^/]+\.so$', n)]
        buruk = []
        for n in so:
            abi = n.split('/')[2]; hasil = ratakan_elf(z.read(n))
            if hasil is None: buruk.append(n + ' (bukan ELF)'); continue
            bit, rata = hasil
            if abi in ABI_64 and (bit != 64 or not rata or min(rata) < HALAMAN_16K):
                buruk.append('%s (p_align %s)' % (n, ', '.join(str(x) for x in rata) or 'tanpa PT_LOAD'))
        h.append((not buruk, 'pustaka native 64-bit siap halaman 16 KB (%d .so%s)' % (len(so), '; GAGAL: ' + '; '.join(buruk) if buruk else '')))
    return h


def main():
    if len(sys.argv) != 2: print(__doc__); sys.exit(2)
    h = periksa(sys.argv[1])
    for ok, k in h: print(('  ok  ' if ok else 'GAGAL ') + k)
    sys.exit(0 if all(ok for ok, _ in h) else 1)


if __name__ == '__main__':
    main()
