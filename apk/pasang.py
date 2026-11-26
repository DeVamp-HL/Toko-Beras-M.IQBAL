#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pasang.py — dijalankan GitHub Actions (apk.yml) SESUDAH `npx cap add android`: memasang bagian tablet kasir ke proyek Android yang baru dibuat.

  · SEMUA plugin perangkat + MainActivity (apk/tambahan/*.java) ke paket id.miqbal.tokoberas
  · izin & penyaring USB: printer Sunmi / kelas printer membuka aplikasi saat dicolok ("selalu" = izin tersimpan)
  · paket S1 (19 Nov 2026) — cangkang SUNMI: pustaka resmi SUNMI (printer luar + SunmiCustomer API) di app/build.gradle; <queries> layanan
    scanner & layanan perangkat SUNMI; penjaga "Hapus data" (manageSpaceActivity); allowBackup mati; configChanges anti layar kedip saat USB dicolok
  · paket S2a (19 Nov 2026) — izin NFC (pembaca NFC bawaan tablet; tidak wajib ada di perangkat)
  · paket S4 (19 Nov 2026) — pustaka AndroidX Biometric + izin USE_BIOMETRIC (sensor sidik jari; tidak wajib ada di perangkat). Izin Bluetooth
    (BLUETOOTH_CONNECT dkk.) TIDAK ditambahkan di sini: manifest pustaka printer SUNMI sudah membawanya
  · owner 23 Nov 2026 — PUSH APLIKASI TABLET: berkas Firebase google-services.json dari rahasia repo GOOGLE_SERVICES_JSON (tanpa rahasia = APK tanpa push,
    tombol notifikasi tablet menolak dengan kalimat yang jelas), izin POST_NOTIFICATIONS (Android 13+), ikon & saluran bawaan notifikasi "Kabar toko"
  · ikon & layar pembuka: logo padi + M stensil, ikon bening + varian malam (apk/ikon-*.png, dibuat apk/ikon_m.py)
  · versionCode/versionName dari nomor jalan Actions (APK baru bisa dipasang menimpa yang lama bila kuncinya sama)
  · Google Play (23 Nov 2026): compileSdk & targetSdk = SDK_SASARAN (36) di variables.gradle — aplikasi BARU di Play wajib menyasar Android 16 sejak
    31 Agu 2026 (Capacitor 7 bawaannya 35). Perilaku baru Android 15/16 hanya berlaku di perangkat Android 15/16; CPad = Android 14 → tidak berubah
  · Google Play (26 Nov 2026): minSdk = SDK_MINIMUM (24) — unggahan AAB 1.43 DITOLAK: "Perlindungan otomatis Google Play memerlukan versi SDK minimum
    24 atau yang lebih tinggi" (Capacitor 7 bawaannya 23 = Android 6). 24 = Android 7.0; CPad = Android 14 → tidak berubah

    python3 apk/pasang.py --versi 12
"""
import argparse, glob, json, os, re, shutil, sys

APK = os.path.dirname(os.path.abspath(__file__))
AKAR = os.path.dirname(APK)
ANDROID = os.path.join(APK, 'android')
PAKET = 'id.miqbal.tokoberas'
UTAMA = os.path.join(ANDROID, 'app', 'src', 'main')
# Pustaka resmi SUNMI di Maven Central (versi dikunci; naikkan dengan sengaja sesudah diuji di CPad):
#   external-printerlibrary2 = "Cloud Printer SDK for Android" (NT21x/NT31x/NT32x lewat USB/LAN/BT: keadaan printer, hasil cetak, laci)
#   customerservice          = SunmiCustomer API (TMSApi: lampu LED CPad, info perangkat) — tersedia di Maven sejak 1.3.82.0
PUSTAKA = ('com.sunmi:external-printerlibrary2:1.0.16', 'com.sunmi:customerservice:1.3.82.1')
# Pustaka bukan-SUNMI (versi dikunci): androidx.biometric = BiometricPrompt/BiometricManager, jalur sidik jari yang diwajibkan SUNMI
# (dokumen "Biometric (Fingerprint) Development Guide" menyebut versi ini)
PUSTAKA_LAIN = ('androidx.biometric:biometric:1.1.0',)
# paket yang harus terlihat aplikasi ini di Android 11+ (tanpa <queries> layanannya dianggap tidak terpasang)
TANYA_PAKET = ('com.sunmi.scanner', 'com.sunmi.tmservice')
PENJAGA_DATA = PAKET + '.KelolaRuangActivity'
ANTI_KEDIP = ('navigation', 'keyboard', 'keyboardHidden')
IZIN_NFC = 'android.permission.NFC'
IZIN_BIOMETRIK = 'android.permission.USE_BIOMETRIC'
# owner 23 Nov 2026: push aplikasi tablet (plugin resmi @capacitor/push-notifications = Firebase Cloud Messaging)
IZIN_NOTIF = 'android.permission.POST_NOTIFICATIONS'
META_IKON = '<meta-data android:name="com.google.firebase.messaging.default_notification_icon" android:resource="@drawable/ic_kabar" />'
META_SALURAN = '<meta-data android:name="com.google.firebase.messaging.default_notification_channel_id" android:value="kabar" />'
GS_PLUGIN = 'com.google.gms.google-services'
GS_CLASSPATH = "classpath 'com.google.gms:google-services:4.4.2'"


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
    os.makedirs(os.path.join(UTAMA, 'res', 'drawable'), exist_ok=True)
    shutil.copyfile(os.path.join(APK, 'tambahan', 'res', 'drawable', 'ic_kabar.xml'), os.path.join(UTAMA, 'res', 'drawable', 'ic_kabar.xml'))
    print('  res/drawable/ic_kabar.xml (ikon notifikasi)')


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
    # paket S4: sensor sidik jari (BiometricPrompt). required="false" = aplikasi tetap bisa dipasang di tablet tanpa sensor
    if IZIN_BIOMETRIK not in m:
        if m.count('<application') != 1: raise Tolak('AndroidManifest punya %d <application' % m.count('<application'))
        m = m.replace('<application', '<uses-permission android:name="%s" />\n    <uses-feature android:name="android.hardware.fingerprint" android:required="false" />\n\n    <application' % IZIN_BIOMETRIK, 1)
    # owner 23 Nov 2026: push aplikasi tablet — izin tampil notifikasi (Android 13+ wajib diminta saat jalan; diminta dari ketukan Nyalakan)
    if IZIN_NOTIF not in m:
        if m.count('<application') != 1: raise Tolak('AndroidManifest punya %d <application' % m.count('<application'))
        m = m.replace('<application', '<uses-permission android:name="%s" />\n\n    <application' % IZIN_NOTIF, 1)
    # ikon kecil & saluran bawaan untuk notifikasi yang ditampilkan Firebase saat aplikasi tertutup (ikon warna-warni = kotak putih di bilah notifikasi)
    for meta in (META_IKON, META_SALURAN):
        if meta not in m:
            if m.count('</application>') != 1: raise Tolak('AndroidManifest punya %d </application>' % m.count('</application>'))
            m = m.replace('</application>', '    ' + meta + '\n    </application>', 1)
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
    # paket jaringan (20 Nov 2026): printer toko di jaringan lokal hanya bicara HTTP POLOS (http://<alamat>/cgi-bin/print.cgi — dokumen SUNMI
    # "Cloud Printer Over LAN HTTP"); Android menolak HTTP polos kecuali diizinkan di sini. Yang memakainya hanya permintaan ke printer lewat
    # plugin inti CapacitorHttp (perangkat.js membatasi alamatnya ke IPv4 pribadi). Halaman toko sendiri tetap https: isi campuran di WebView
    # tetap ditolak (capacitor.config.json › allowMixedContent false). networkSecurityConfig akan mengalahkan atribut ini — kalau cetakan
    # Capacitor suatu hari memakainya, perakitan DIHENTIKAN supaya tidak diam-diam tanpa izin.
    if 'android:networkSecurityConfig' in m: raise Tolak('AndroidManifest memakai networkSecurityConfig — izin HTTP polos untuk printer jaringan harus diatur di berkas itu')
    if 'android:usesCleartextTraffic' not in m:
        if m.count('<application') != 1: raise Tolak('AndroidManifest punya %d <application' % m.count('<application'))
        m = m.replace('<application', '<application\n        android:usesCleartextTraffic="true"', 1)
    m = m.replace('android:usesCleartextTraffic="false"', 'android:usesCleartextTraffic="true"')
    # paket S1: data aplikasi tidak ikut cadangan perangkat (syarat uji App Store SUNMI untuk perangkat keuangan; di sini sekadar rapi)
    m = m.replace('android:allowBackup="true"', 'android:allowBackup="false"')
    # paket S1: mencolok USB (printer, scanner HID, papan ketik) tidak memuat ulang halaman — tips resmi SUNMI "avoid app interface flickering"
    cocok = re.search(r'android:configChanges="([^"]*)"', m)
    if not cocok: raise Tolak('android:configChanges tidak ada di aktivitas utama')
    bagian = [x for x in cocok.group(1).split('|') if x]
    lengkap = bagian + [x for x in ANTI_KEDIP if x not in bagian]
    m = m[:cocok.start(1)] + '|'.join(lengkap) + m[cocok.end(1):]
    wajib = ['android.hardware.usb.host', 'USB_DEVICE_ATTACHED', '@xml/device_filter', 'android:allowBackup="false"', 'android:usesCleartextTraffic="true"',
             'android:manageSpaceActivity="%s"' % PENJAGA_DATA, '<activity android:name="%s"' % PENJAGA_DATA]
    wajib += ['<package android:name="%s"' % p for p in TANYA_PAKET]
    wajib += ['<uses-permission android:name="%s" />' % IZIN_NFC, '<uses-feature android:name="android.hardware.nfc" android:required="false" />']
    wajib += ['<uses-permission android:name="%s" />' % IZIN_BIOMETRIK, '<uses-feature android:name="android.hardware.fingerprint" android:required="false" />']
    wajib += ['<uses-permission android:name="%s" />' % IZIN_NOTIF, META_IKON, META_SALURAN]
    for w in wajib:
        if w not in m: raise Tolak('manifest tidak memuat ' + w)
    return m


def ubah_gradle(g, versi):
    """app/build.gradle Capacitor → versi dari nomor jalan + pustaka resmi SUNMI. Murni; boleh dijalankan ulang."""
    g2, n1 = re.subn(r'versionCode\s+\d+', 'versionCode %d' % versi, g, count=1)
    g2, n2 = re.subn(r'versionName\s+"[^"]*"', 'versionName "1.%d"' % versi, g2, count=1)
    if n1 != 1 or n2 != 1: raise Tolak('versionCode/versionName tidak ditemukan di app/build.gradle')
    kurang = [p for p in PUSTAKA + PUSTAKA_LAIN if p not in g2]
    if kurang:
        blok = re.findall(r'(?m)^dependencies\s*\{[ \t]*$', g2)
        if len(blok) != 1: raise Tolak('app/build.gradle punya %d blok dependencies di tepi kiri — pola Capacitor berubah' % len(blok))
        sisip = ''.join("    implementation '%s'\n" % p for p in kurang)
        g2 = re.sub(r'(?m)^(dependencies\s*\{[ \t]*\n)', lambda mm: mm.group(1) + sisip, g2, count=1)
    for p in PUSTAKA + PUSTAKA_LAIN:
        if g2.count("implementation '%s'" % p) != 1: raise Tolak('pustaka %s tidak tepat satu kali di app/build.gradle' % p)
    return g2


# Google Play (23 Nov 2026): "Starting August 31, 2026: New apps and app updates must target Android 16 (API level 36) or higher" (Play Console Help
# 11926878; perpanjangan sampai 1 Nov 2026 sudah lewat). Satu angka untuk APK & AAB — keduanya dari satu bangun, versionCode sama.
SDK_SASARAN = 36
# Google Play (26 Nov 2026, Play Console saat unggah AAB pertama): "Perlindungan otomatis Google Play memerlukan versi SDK minimum 24 atau yang lebih
# tinggi. App Bundle yang diupload memiliki versi SDK minimum 23." Capacitor 7 bawaannya 23.
SDK_MINIMUM = 24


def ubah_variabel(v, sdk=SDK_SASARAN, minimum=SDK_MINIMUM):
    """apk/android/variables.gradle Capacitor → minSdkVersion = minimum, compileSdkVersion & targetSdkVersion = sdk (tidak pernah MENURUNKAN).
    Murni; boleh dijalankan ulang."""
    for nama, angka in (('minSdkVersion', minimum), ('compileSdkVersion', sdk), ('targetSdkVersion', sdk)):
        pola = r'(?m)^([ \t]*%s[ \t]*=[ \t]*)(\d+)([ \t]*)$' % nama
        cocok = re.findall(pola, v)
        if len(cocok) != 1: raise Tolak('variables.gradle punya %d baris %s — pola Capacitor berubah, sasaran SDK Play tidak bisa dipasang' % (len(cocok), nama))
        v = re.sub(pola, lambda mm: mm.group(1) + str(max(angka, int(mm.group(2)))) + mm.group(3), v, count=1)
    return v


def pasang_sdk():
    p = os.path.join(ANDROID, 'variables.gradle')
    try: v = ubah_variabel(baca(p))
    except Tolak as e: gagal(str(e))
    tulis(p, v); print('  SDK: minSdk, compileSdk, targetSdk = %s (syarat Google Play)' % ', '.join(re.findall(r'(?m)^[ \t]*(?:min|compile|target)SdkVersion[ \t]*=[ \t]*(\d+)', v)))


def periksa_gs(teks):
    """Isi rahasia GOOGLE_SERVICES_JSON → teks JSON rapi. Wajib JSON berkas google-services Firebase yang memuat aplikasi Android paket ini
    (salah tempel = bangun GAGAL dengan kalimat jelas, bukan APK yang diam-diam tanpa push)."""
    try: d = json.loads(teks)
    except Exception: raise Tolak('rahasia GOOGLE_SERVICES_JSON bukan JSON — salin SELURUH isi berkas google-services.json dari Firebase Console')
    nama = [((c.get('client_info') or {}).get('android_client_info') or {}).get('package_name') for c in (d.get('client') or []) if isinstance(c, dict)]
    if PAKET not in nama: raise Tolak('google-services.json tidak memuat aplikasi Android %s (ada: %s) — daftarkan aplikasi Android dengan nama paket itu di Firebase Console' % (PAKET, ', '.join(x for x in nama if x) or 'tidak ada'))
    if not (d.get('project_info') or {}).get('project_id'): raise Tolak('google-services.json tanpa project_id')
    return json.dumps(d, indent=2, ensure_ascii=False) + '\n'


def ubah_gradle_gs(app_g, akar_g):
    """Pastikan plugin google-services terpasang (cetakan Capacitor 7 sudah membawanya: classpath di build.gradle akar, apply bersyarat di app). Murni."""
    if GS_PLUGIN not in app_g:
        app_g = app_g.rstrip('\n') + "\n\napply plugin: '%s'\n" % GS_PLUGIN
    if 'com.google.gms:google-services' not in akar_g:
        cocok = re.search(r"(?m)^([ \t]*)classpath ['\"]com\.android\.tools\.build:gradle:[^'\"]+['\"][ \t]*$", akar_g)
        if not cocok: raise Tolak('build.gradle akar tanpa classpath Android Gradle — pola Capacitor berubah, plugin google-services tidak bisa dipasang')
        akar_g = akar_g[:cocok.end()] + '\n' + cocok.group(1) + GS_CLASSPATH + akar_g[cocok.end():]
    return app_g, akar_g


def pasang_firebase():
    """owner 23 Nov 2026: berkas Firebase untuk push tablet dari rahasia repo. Tanpa rahasia = APK tetap jadi, push tablet mati (dikabarkan di layar)."""
    teks = os.environ.get('GOOGLE_SERVICES_JSON', '').strip()
    if not teks: print('  push tablet: TANPA berkas Firebase (rahasia GOOGLE_SERVICES_JSON kosong) — notifikasi tablet tidak bisa dinyalakan di APK ini'); return False
    try:
        isi = periksa_gs(teks)
        pa = os.path.join(ANDROID, 'app', 'build.gradle'); pr = os.path.join(ANDROID, 'build.gradle')
        app_g, akar_g = ubah_gradle_gs(baca(pa), baca(pr))
    except Tolak as e: gagal(str(e))
    tulis(os.path.join(ANDROID, 'app', 'google-services.json'), isi); tulis(pa, app_g); tulis(pr, akar_g)
    print('  push tablet: google-services.json terpasang (paket %s) + plugin google-services' % PAKET); return True


def pasang_manifest():
    p = os.path.join(UTAMA, 'AndroidManifest.xml')
    try: m = ubah_manifest(baca(p))
    except Tolak as e: gagal(str(e))
    tulis(p, m); print('  AndroidManifest.xml: usb.host + USB_DEVICE_ATTACHED + <queries> SUNMI + izin NFC + izin sidik jari + izin notifikasi + ikon/saluran notifikasi + penjaga data + allowBackup mati + HTTP polos (printer jaringan) + configChanges')


def pasang_versi(versi):
    p = os.path.join(ANDROID, 'app', 'build.gradle')
    try: g = ubah_gradle(baca(p), versi)
    except Tolak as e: gagal(str(e))
    tulis(p, g); print('  versi: 1.%d (kode %d) · pustaka: %s' % (versi, versi, ', '.join(PUSTAKA + PUSTAKA_LAIN)))


LATAR_IKON = '#14110d'      # = apk/ikon_m.py LATAR_APK (layar pembuka; hitam kecokelatan logo B)
LATAR_ADAPTIF = '#00000000' # = apk/ikon_m.py LATAR_ADAPTIF — latar belakang ikon adaptif BENING (owner 26 Nov: "transparan seperti SunmiSubScreen")


def pasang_ikon():
    """Logo toko padi + M stensil (owner 26 Nov 2026, menggantikan logo "M" bercincin 23 Nov). Ikon adaptif Android = latar DEPAN bening
    (apk/ikon-depan-432.png, emas gelap — terbaca di peluncur terang) di atas latar BELAKANG BENING → peluncur menampilkan logonya saja, tanpa kotak.
    Mode gelap: mipmap-night-* memakai apk/ikon-depan-malam-432.png (emas asli). Ikon lama (Android < 8) = gambar yang sama (bening).
    Layar pembuka = logo emas (apk/ikon-pembuka-432.png) di atas LATAR_IKON. Semua gambar dibuat apk/ikon_m.py."""
    try:
        from PIL import Image
    except ImportError:
        print('  ikon: Pillow tidak ada — ikon bawaan Capacitor dipakai'); return
    depan = Image.open(os.path.join(AKAR, 'apk', 'ikon-depan-432.png')).convert('RGBA')
    malam = Image.open(os.path.join(AKAR, 'apk', 'ikon-depan-malam-432.png')).convert('RGBA')
    pembuka = Image.open(os.path.join(AKAR, 'apk', 'ikon-pembuka-432.png')).convert('RGBA')
    ukuran = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
    for d, n in ukuran.items():
        for gambar, folder in ((depan, 'mipmap-' + d), (malam, 'mipmap-night-' + d)):
            for nama in ('ic_launcher.png', 'ic_launcher_round.png', 'ic_launcher_foreground.png'):
                asal = os.path.join(UTAMA, 'res', 'mipmap-' + d, nama)
                if not os.path.exists(asal): continue
                ke = os.path.join(UTAMA, 'res', folder, nama); os.makedirs(os.path.dirname(ke), exist_ok=True)
                w = Image.open(asal).size if nama == 'ic_launcher_foreground.png' else (n, n)
                gambar.resize(w, Image.LANCZOS).save(ke)
    latar = os.path.join(UTAMA, 'res', 'values', 'ic_launcher_background.xml')
    if os.path.exists(latar): tulis(latar, re.sub(r'#[0-9A-Fa-f]{6,8}', LATAR_ADAPTIF, baca(latar)))
    warna = tuple(int(LATAR_IKON[i:i + 2], 16) for i in (1, 3, 5))
    for p in glob.glob(os.path.join(UTAMA, 'res', 'drawable*', 'splash.png')):
        w, h = Image.open(p).size; kanvas = Image.new('RGB', (w, h), warna); s = int(min(w, h) * 0.5); g = pembuka.resize((s, s), Image.LANCZOS)
        kanvas.paste(g, ((w - s) // 2, (h - s) // 2), g); kanvas.save(p)
    print('  ikon (logo padi + M stensil, latar bening, varian malam) & layar pembuka (latar ' + LATAR_IKON + ') dari apk/ikon-*.png')


def main():
    a = argparse.ArgumentParser(); a.add_argument('--versi', type=int, default=1); x = a.parse_args()
    if not os.path.isdir(ANDROID): gagal('apk/android belum ada — jalankan `npx cap add android` dulu')
    print('Memasang tablet kasir ke proyek Android:')
    pasang_java(); pasang_manifest(); pasang_versi(max(1, x.versi)); pasang_sdk(); pasang_firebase(); pasang_ikon()
    print('SELESAI')


if __name__ == '__main__':
    main()
