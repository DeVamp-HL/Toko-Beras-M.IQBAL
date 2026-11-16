#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pasang.py — dijalankan GitHub Actions (apk.yml) SESUDAH `npx cap add android`: memasang bagian tablet kasir ke proyek Android yang baru dibuat.

  · plugin CetakUsb + MainActivity (apk/tambahan/*.java) ke paket id.miqbal.tokoberas
  · izin & penyaring USB: printer Sunmi / kelas printer membuka aplikasi saat dicolok ("selalu" = izin tersimpan)
  · ikon & layar pembuka dari icon-sistem-512.png toko
  · versionCode/versionName dari nomor jalan Actions (APK baru bisa dipasang menimpa yang lama bila kuncinya sama)

    python3 apk/pasang.py --versi 12
"""
import argparse, glob, os, re, shutil, sys

APK = os.path.dirname(os.path.abspath(__file__))
AKAR = os.path.dirname(APK)
ANDROID = os.path.join(APK, 'android')
PAKET = 'id.miqbal.tokoberas'
UTAMA = os.path.join(ANDROID, 'app', 'src', 'main')


def gagal(pesan):
    print('GAGAL:', pesan); sys.exit(1)


def tulis(p, isi):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f: f.write(isi)


def baca(p):
    with open(p, encoding='utf-8') as f: return f.read()


def pasang_java():
    tujuan = os.path.join(UTAMA, 'java', *PAKET.split('.'))
    if not os.path.isdir(tujuan): gagal('folder paket tidak ada: ' + tujuan + ' (appId di capacitor.config.json berubah?)')
    for nama in ('CetakUsbPlugin.java', 'MainActivity.java'):
        shutil.copyfile(os.path.join(APK, 'tambahan', nama), os.path.join(tujuan, nama)); print('  java:', nama)
    shutil.copyfile(os.path.join(APK, 'tambahan', 'res', 'xml', 'device_filter.xml'), os.path.join(UTAMA, 'res', 'xml', 'device_filter.xml'))
    print('  res/xml/device_filter.xml')


def pasang_manifest():
    p = os.path.join(UTAMA, 'AndroidManifest.xml'); m = baca(p)
    if 'android.hardware.usb.host' not in m:
        m = m.replace('<application', '<uses-feature android:name="android.hardware.usb.host" android:required="false" />\n\n    <application', 1)
    if 'USB_DEVICE_ATTACHED' not in m:
        if m.count('</activity>') != 1: gagal('AndroidManifest punya %d aktivitas — pola Capacitor berubah' % m.count('</activity>'))
        tambah = ('    <intent-filter>\n'
                  '                <action android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED" />\n'
                  '            </intent-filter>\n'
                  '            <meta-data android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED" android:resource="@xml/device_filter" />\n'
                  '        </activity>')
        m = m.replace('</activity>', tambah, 1)
    for wajib in ('android.hardware.usb.host', 'USB_DEVICE_ATTACHED', '@xml/device_filter'):
        if wajib not in m: gagal('manifest tidak memuat ' + wajib)
    tulis(p, m); print('  AndroidManifest.xml: usb.host + USB_DEVICE_ATTACHED')


def pasang_versi(versi):
    p = os.path.join(ANDROID, 'app', 'build.gradle'); g = baca(p)
    g2 = re.sub(r'versionCode\s+\d+', 'versionCode %d' % versi, g, count=1)
    g2 = re.sub(r'versionName\s+"[^"]*"', 'versionName "1.%d"' % versi, g2, count=1)
    if g2 == g and versi != 1: gagal('versionCode/versionName tidak ditemukan di app/build.gradle')
    tulis(p, g2); print('  versi: 1.%d (kode %d)' % (versi, versi))


def pasang_ikon():
    try:
        from PIL import Image
    except ImportError:
        print('  ikon: Pillow tidak ada — ikon bawaan Capacitor dipakai'); return
    sumber = Image.open(os.path.join(AKAR, 'icon-sistem-512.png')).convert('RGBA')
    ukuran = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
    for d, n in ukuran.items():
        for nama in ('ic_launcher.png', 'ic_launcher_round.png'):
            p = os.path.join(UTAMA, 'res', 'mipmap-' + d, nama)
            if os.path.exists(p): sumber.resize((n, n), Image.LANCZOS).save(p)
        # latar depan ikon adaptif: logo di tengah area aman (66 %) kanvas 108 dp
        p = os.path.join(UTAMA, 'res', 'mipmap-' + d, 'ic_launcher_foreground.png')
        if os.path.exists(p):
            kanvas = Image.new('RGBA', Image.open(p).size, (0, 0, 0, 0)); s = int(kanvas.size[0] * 0.66)
            kanvas.paste(sumber.resize((s, s), Image.LANCZOS), ((kanvas.size[0] - s) // 2, (kanvas.size[1] - s) // 2)); kanvas.save(p)
    latar = os.path.join(UTAMA, 'res', 'values', 'ic_launcher_background.xml')
    if os.path.exists(latar): tulis(latar, re.sub(r'#[0-9A-Fa-f]{6,8}', '#E2E7EC', baca(latar)))
    for p in glob.glob(os.path.join(UTAMA, 'res', 'drawable*', 'splash.png')):
        w, h = Image.open(p).size; kanvas = Image.new('RGB', (w, h), (226, 231, 236)); s = int(min(w, h) * 0.32)
        kanvas.paste(sumber.resize((s, s), Image.LANCZOS), ((w - s) // 2, (h - s) // 2), sumber.resize((s, s), Image.LANCZOS)); kanvas.save(p)
    print('  ikon & layar pembuka dari icon-sistem-512.png')


def main():
    a = argparse.ArgumentParser(); a.add_argument('--versi', type=int, default=1); x = a.parse_args()
    if not os.path.isdir(ANDROID): gagal('apk/android belum ada — jalankan `npx cap add android` dulu')
    print('Memasang tablet kasir ke proyek Android:')
    pasang_java(); pasang_manifest(); pasang_versi(max(1, x.versi)); pasang_ikon()
    print('SELESAI')


if __name__ == '__main__':
    main()
