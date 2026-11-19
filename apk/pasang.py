#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pasang.py — dijalankan GitHub Actions (apk.yml) SESUDAH `npx cap add android`: memasang bagian tablet kasir ke proyek Android yang baru dibuat.

  · SEMUA plugin perangkat + MainActivity (apk/tambahan/*.java) ke paket id.miqbal.tokoberas
  · izin & penyaring USB: printer Sunmi / kelas printer membuka aplikasi saat dicolok ("selalu" = izin tersimpan)
  · paket S1 (19 Nov 2026) — cangkang SUNMI: pustaka resmi SUNMI (printer luar + SunmiCustomer API) di app/build.gradle; <queries> layanan
    scanner & layanan perangkat SUNMI; penjaga "Hapus data" (manageSpaceActivity); allowBackup mati; configChanges anti layar kedip saat USB dicolok
  · paket S2a (19 Nov 2026) — izin NFC (pembaca NFC bawaan tablet; tidak wajib ada di perangkat)
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
# Pustaka resmi SUNMI di Maven Central (versi dikunci; naikkan dengan sengaja sesudah diuji di CPad):
#   external-printerlibrary2 = "Cloud Printer SDK for Android" (NT21x/NT31x/NT32x lewat USB/LAN/BT: keadaan printer, hasil cetak, laci)
#   customerservice          = SunmiCustomer API (TMSApi: lampu LED CPad, info perangkat) — tersedia di Maven sejak 1.3.82.0
PUSTAKA = ('com.sunmi:external-printerlibrary2:1.0.16', 'com.sunmi:customerservice:1.3.82.1')
# paket yang harus terlihat aplikasi ini di Android 11+ (tanpa <queries> layanannya dianggap tidak terpasang)
TANYA_PAKET = ('com.sunmi.scanner', 'com.sunmi.tmservice')
PENJAGA_DATA = PAKET + '.KelolaRuangActivity'
ANTI_KEDIP = ('navigation', 'keyboard', 'keyboardHidden')
IZIN_NFC = 'android.permission.NFC'


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
    daftar = sorted(os.path.basename(f) for f in glob.glob(os.path.join(APK, 'tambahan', '*.java')))
    if 'MainActivity.java' not in daftar: gagal('apk/tambahan/MainActivity.java tidak ada')
    for nama in daftar:
        shutil.copyfile(os.path.join(APK, 'tambahan', nama), os.path.join(tujuan, nama)); print('  java:', nama)
    shutil.copyfile(os.path.join(APK, 'tambahan', 'res', 'xml', 'device_filter.xml'), os.path.join(UTAMA, 'res', 'xml', 'device_filter.xml'))
    print('  res/xml/device_filter.xml')


class Tolak(Exception):
    """Pola berkas Capacitor tidak seperti yang dikenal — lebih baik bangun GAGAL daripada APK diam-diam tanpa bagian ini."""


def ubah_manifest(m):
    """AndroidManifest.xml Capacitor → manifest tablet kasir. Murni (teks → teks) supaya bisa diuji tanpa proyek Android; boleh dijalankan ulang."""
    if 'android.hardware.usb.host' not in m:
        m = m.replace('<application', '<uses-feature android:name="android.hardware.usb.host" android:required="false" />\n\n    <application', 1)
    if 'USB_DEVICE_ATTACHED' not in m:
        if m.count('</activity>') != 1: raise Tolak('AndroidManifest punya %d aktivitas — pola Capacitor berubah' % m.count('</activity>'))
        tambah = ('    <intent-filter>\n'
                  '                <action android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED" />\n'
                  '            </intent-filter>\n'
                  '            <meta-data android:name="android.hardware.usb.action.USB_DEVICE_ATTACHED" android:resource="@xml/device_filter" />\n'
                  '        </activity>')
        m = m.replace('</activity>', tambah, 1)
    # paket S2a: pembaca NFC bawaan tablet (kartu pelanggan). required="false" = aplikasi tetap bisa dipasang di perangkat tanpa NFC
    if IZIN_NFC not in m:
        if m.count('<application') != 1: raise Tolak('AndroidManifest punya %d <application' % m.count('<application'))
        m = m.replace('<application', '<uses-permission android:name="%s" />\n    <uses-feature android:name="android.hardware.nfc" android:required="false" />\n\n    <application' % IZIN_NFC, 1)
    # paket S1: layanan SUNMI yang ditanya aplikasi (scanner, layanan perangkat)
    kurang = [p for p in TANYA_PAKET if ('<package android:name="%s"' % p) not in m]
    if kurang:
        if m.count('<application') != 1: raise Tolak('AndroidManifest punya %d <application' % m.count('<application'))
        blok = '<queries>\n' + ''.join('        <package android:name="%s" />\n' % p for p in kurang) + '    </queries>\n\n    '
        m = m.replace('<application', blok + '<application', 1)
    # paket S1: "Hapus data" di Setelan tidak menghapus akun tablet, antrean, setelan printer (aktivitasnya langsung menutup diri)
    if 'android:manageSpaceActivity' not in m:
        m = m.replace('<application', '<application\n        android:manageSpaceActivity="%s"' % PENJAGA_DATA, 1)
    if ('android:name="%s"' % PENJAGA_DATA) not in m:
        if m.count('</application>') != 1: raise Tolak('AndroidManifest punya %d </application>' % m.count('</application>'))
        m = m.replace('</application>', '    <activity android:name="%s" android:exported="false" />\n    </application>' % PENJAGA_DATA, 1)
    # paket S1: data aplikasi tidak ikut cadangan perangkat (syarat uji App Store SUNMI untuk perangkat keuangan; di sini sekadar rapi)
    m = m.replace('android:allowBackup="true"', 'android:allowBackup="false"')
    # paket S1: mencolok USB (printer, scanner HID, papan ketik) tidak memuat ulang halaman — tips resmi SUNMI "avoid app interface flickering"
    cocok = re.search(r'android:configChanges="([^"]*)"', m)
    if not cocok: raise Tolak('android:configChanges tidak ada di aktivitas utama')
    bagian = [x for x in cocok.group(1).split('|') if x]
    lengkap = bagian + [x for x in ANTI_KEDIP if x not in bagian]
    m = m[:cocok.start(1)] + '|'.join(lengkap) + m[cocok.end(1):]
    wajib = ['android.hardware.usb.host', 'USB_DEVICE_ATTACHED', '@xml/device_filter', 'android:allowBackup="false"',
             'android:manageSpaceActivity="%s"' % PENJAGA_DATA, '<activity android:name="%s"' % PENJAGA_DATA]
    wajib += ['<package android:name="%s"' % p for p in TANYA_PAKET]
    wajib += ['<uses-permission android:name="%s" />' % IZIN_NFC, '<uses-feature android:name="android.hardware.nfc" android:required="false" />']
    for w in wajib:
        if w not in m: raise Tolak('manifest tidak memuat ' + w)
    return m


def ubah_gradle(g, versi):
    """app/build.gradle Capacitor → versi dari nomor jalan + pustaka resmi SUNMI. Murni; boleh dijalankan ulang."""
    g2, n1 = re.subn(r'versionCode\s+\d+', 'versionCode %d' % versi, g, count=1)
    g2, n2 = re.subn(r'versionName\s+"[^"]*"', 'versionName "1.%d"' % versi, g2, count=1)
    if n1 != 1 or n2 != 1: raise Tolak('versionCode/versionName tidak ditemukan di app/build.gradle')
    kurang = [p for p in PUSTAKA if p not in g2]
    if kurang:
        blok = re.findall(r'(?m)^dependencies\s*\{[ \t]*$', g2)
        if len(blok) != 1: raise Tolak('app/build.gradle punya %d blok dependencies di tepi kiri — pola Capacitor berubah' % len(blok))
        sisip = ''.join("    implementation '%s'\n" % p for p in kurang)
        g2 = re.sub(r'(?m)^(dependencies\s*\{[ \t]*\n)', lambda mm: mm.group(1) + sisip, g2, count=1)
    for p in PUSTAKA:
        if g2.count("implementation '%s'" % p) != 1: raise Tolak('pustaka %s tidak tepat satu kali di app/build.gradle' % p)
    return g2


def pasang_manifest():
    p = os.path.join(UTAMA, 'AndroidManifest.xml')
    try: m = ubah_manifest(baca(p))
    except Tolak as e: gagal(str(e))
    tulis(p, m); print('  AndroidManifest.xml: usb.host + USB_DEVICE_ATTACHED + <queries> SUNMI + izin NFC + penjaga data + allowBackup mati + configChanges')


def pasang_versi(versi):
    p = os.path.join(ANDROID, 'app', 'build.gradle')
    try: g = ubah_gradle(baca(p), versi)
    except Tolak as e: gagal(str(e))
    tulis(p, g); print('  versi: 1.%d (kode %d) · pustaka: %s' % (versi, versi, ', '.join(PUSTAKA)))


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
