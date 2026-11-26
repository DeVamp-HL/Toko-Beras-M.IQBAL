# Google Play privat untuk tablet kasir

Tujuan (owner 23 Nov 2026): aplikasi tablet (`id.miqbal.tokoberas`, cangkang Capacitor) dipasang & diperbarui lewat **Play Store di CPad**, hanya untuk
akun owner — **tidak publik**. App Store SUNMI ternyata hanya kanal umum; APK 1.37 masih dipasang manual.

**Jalur yang dipakai: Play Console › Uji internal (Internal testing), akun developer pribadi.** Semua langkah berbayar, verifikasi identitas, perjanjian,
dan formulir di bawah adalah **langkah owner** — Claude tidak membuat akun, tidak membayar, tidak menerima perjanjian.

## Kenapa uji internal

| | Uji internal | Uji tertutup | Managed Google Play (aplikasi privat) |
|---|---|---|---|
| Siapa yang bisa memasang | ≤ 100 email penguji yang owner tulis | daftar email / Google Group | perangkat yang terdaftar di organisasi Android Enterprise |
| Ditinjau Google | tidak ada tinjauan panjang; versi sampai ke penguji dalam hitungan detik–menit | **ya** (bisa beberapa hari tiap versi) | otomatis disetujui (±10 menit) |
| Syarat di Play Console | AAB + daftar penguji; halaman toko & formulir belum wajib | halaman toko, kebijakan privasi, Data safety, rating konten, **akun uji untuk peninjau** (= membuka data toko ke Google) | akun Play Console + organisasi Android Enterprise + **CPad didaftarkan ke EMM** (profil kerja / dikelola penuh = reset pabrik) |
| Syarat "12 penguji × 14 hari" (akun pribadi baru) | **tidak** — syarat itu hanya untuk naik ke Produksi | sama, hanya untuk Produksi | tidak berlaku |
| targetSdk minimum | 36 (sudah dipenuhi PR ini) | 36 | dikecualikan |
| Cocok untuk 1 tablet milik owner | **ya** | berlebihan | terlalu berat |

Uji internal = paling cepat, paling sedikit formulir, tidak membuka data toko ke peninjau, dan tidak pernah tampil di pencarian Play. Batasnya: jangan
pernah menekan **Produksi** atau **Uji terbuka** (uji terbuka = siapa pun bisa bergabung).

## Yang sudah disiapkan di repo (PR ini)

| Bagian | Berkas |
|---|---|
| AAB bertanda tangan kunci toko, artefak terpisah **`aab-google-play`**, di samping APK yang tetap seperti biasa | `.github/workflows/apk.yml`, pemeriksa `apk/periksa_aab.py` |
| targetSdk & compileSdk **36** (syarat aplikasi baru di Play sejak 31 Agu 2026; Capacitor 7 bawaannya 35) | `apk/pasang.py` (`SDK_SASARAN`) |
| minSdk **24** = Android 7.0 (26 Nov 2026: unggahan AAB 1.43 ditolak — perlindungan otomatis Play wajib minSdk ≥ 24; Capacitor 7 bawaannya 23) | `apk/pasang.py` (`SDK_MINIMUM`) |
| Workflow sekali-jalan untuk menyerahkan **kunci toko** ke Play App Signing (alat PEPK Google, di runner — Mac tanpa Java) | `.github/workflows/play-kunci.yml` |
| Ikon 512, grafis unggulan 1024 × 500 (logo M, hitam malam + emas) | `docs/google-play/` (perender `apk/bahan_play.py` dari geometri logo M `apk/ikon_m.py`) |
| Nama, deskripsi pendek & lengkap | `docs/google-play/teks-toko.md` |
| Kebijakan privasi (Pages) | `privasi.html` → `https://devamp-hl.github.io/Toko-Beras-M.IQBAL/privasi.html` |
| Jawaban Data safety, rating konten, deklarasi | `docs/google-play/data-safety.md` |
| Uji statis + kontrol | `alat-uji/uji_google_play.py` |

**targetSdk 36 di CPad:** perilaku baru Android 15/16 (layar tepi-ke-tepi wajib, orientasi layar besar) hanya berlaku di perangkat **Android 15/16**.
CPad = Android 14 → aplikasi berperilaku sama. APK manual dari Actions ikut 36 (satu bangun untuk APK & AAB).

## Langkah owner (urut)

1. **Merge PR ini** (logo M PR #188 sudah di main: ikon aplikasi di tablet = ikon di Play). Sesudah merge, workflow **Bangun APK tablet kasir** jalan sendiri
   (atau tab Actions › Bangun APK tablet kasir › *Run workflow*). Di halaman run: artefak `apk-tablet-kasir` **dan** `aab-google-play`, dan di ringkasan
   ada baris *sidik SHA-256 sertifikat kunci* — catat.
2. **Buat akun Play Console** di <https://play.google.com/console/signup> dengan akun Google owner. Pilih akun **pribadi** ("Untuk diri sendiri").
   Akun organisasi butuh nomor D-U-N-S — tidak perlu untuk satu toko.
3. **Bayar biaya pendaftaran** sekali bayar (US$25 saat ditulis) dengan kartu owner.
4. **Verifikasi identitas**: nama resmi & alamat sesuai dokumen, email & nomor telepon. Google bisa meminta foto KTP; prosesnya bisa beberapa hari.
   (Ini sekaligus memenuhi **verifikasi developer Android** yang berlaku di Indonesia sejak 30 Sep 2026 untuk pemasangan dari Play di perangkat
   bersertifikat seperti CPad.)
5. **Verifikasi perangkat Android**: akun pribadi baru wajib membuktikan punya perangkat Android sungguhan lewat aplikasi **Play Console** (Android 10+,
   tidak di-root). CPad (Android 14) bisa dipakai: pasang *Google Play Console* dari Play Store, masuk dengan akun yang sama, ketuk *Verify*. Kalau
   aplikasinya menolak tablet, pakai HP Android mana pun sekali saja.
6. **Terima perjanjian** Developer Distribution Agreement saat diminta.
7. **Buat aplikasi**: *Create app* → nama `Kasir Toko Beras`, bahasa Indonesia, **App**, **Free**, centang deklarasi. (Nama paket mengikuti AAB pertama.)
8. **Serahkan kunci toko ke Play App Signing — SEBELUM AAB pertama diluncurkan.** Ini yang membuat APK 1.37 di CPad bisa diperbarui dari Play tanpa
   dihapus (lihat bagian di bawah).
   1. Play Console › aplikasi › **Test and release › Setup › App signing** (di versi baru: *Protected with Play › Play Store protection › Manage Play
      app signing*). Bila halaman belum ada, buka dulu *Internal testing › Create new release* — di sana ada tombol **Change app signing key** /
      *Choose signing key*.
   2. Pilih **Export and upload a key from Java keystore**. Play menampilkan perintah PEPK dengan **kunci enkripsi**: unduh `encryption_public_key.pem`
      lalu buka di TextEdit dan salin seluruh isinya (termasuk baris BEGIN/END) — atau, bila perintahnya memakai `--encryptionkey=…`, salin deret heksanya.
   3. GitHub › tab **Actions › Serahkan kunci aplikasi ke Google Play (sekali) › Run workflow** → tempel ke kotak *kunci_enkripsi* → Run.
   4. Sesudah hijau: unduh artefak **`kunci-terenkripsi-untuk-play`** (hidup 1 hari), buka zip unduhan itu **sekali** → di dalamnya
      `kunci-terenkripsi-untuk-play.zip` → unggah berkas itu di halaman Play Console yang sama (kotak unggah di bawah perintah PEPK) → Save.
   5. Play Console menampilkan **App signing key certificate › SHA-256** — harus sama dengan sidik yang dicatat di langkah 1. Beda = jangan lanjut.
9. **Daftar penguji**: *Test and release › Testing › Internal testing › Testers* → *Create email list* → isi email akun Google yang **masuk Play Store
   di CPad** (boleh tambah email owner sendiri) → Save → centang daftar itu → Save.
10. **Unggah AAB pertama**: *Internal testing › Create new release* → unggah `toko-beras-kasir-1.N.aab` dari artefak `aab-google-play` (unzip dulu) →
    catatan rilis singkat → *Next* → *Save and publish* / *Start rollout to Internal testing*. Bila Play menahan karena *App content* belum lengkap,
    isi dengan jawaban `docs/google-play/data-safety.md` (kebijakan privasi = alamat `privasi.html` di atas).
11. **Pasang di CPad**: Testers › **Copy link** (tautan bergabung) → buka di Chrome CPad (masuk akun Google penguji) → *Accept invite / Become a tester* →
    *download it on Google Play* → **Update** (atau *Install*). Bila Play Store belum menampilkan versi baru, tunggu beberapa menit lalu buka lagi.
12. **Pembaruan berikutnya**: tiap run *Bangun APK tablet kasir* yang hijau → unduh `aab-google-play` → *Internal testing › Create new release* → unggah →
    rollout. Play Store di CPad memperbarui otomatis (atau ketuk *Update*). Nomor versi = nomor run, selalu naik.

## Apa yang terjadi dengan APK yang sudah terpasang

| Pilihan di langkah 8 | Akibat di CPad |
|---|---|
| **Kunci toko diserahkan ke Play (disarankan)** | Play menandatangani dengan kunci yang **sama** dengan APK 1.37 → versi Play dipasang sebagai **pembaruan biasa**: masuk akun, antrean, setelan printer, layar penuh tetap. APK manual dari Actions juga tetap bisa dipasang menimpa versi Play (selama nomor versinya lebih besar — Android menolak turun versi). |
| Langkah 8 dilewati (Play memakai kunci buatannya sendiri — bawaan Play Console) | Tanda tangan beda → Play Store **tidak bisa menimpa** APK 1.37. Aplikasi harus **dihapus dulu** (masuk akun tablet, setelan printer, dan antrean yang belum terkirim hilang — pastikan antrean kosong), baru pasang dari Play. Sesudahnya APK manual dari Actions tidak bisa dipasang menimpa versi Play. |

Kalau langkah 8 terlewat dan versi pertama sudah diluncurkan di uji internal: kunci aplikasi masih bisa diganti selama aplikasi belum pernah ke uji
terbuka/produksi (Play app signing › *Change key*) — lalu unggah ulang dengan nomor versi baru.

Catatan kunci: dengan langkah 8, kunci toko menjadi kunci aplikasi **dan** kunci unggah (Google menyarankan keduanya beda, tidak mewajibkan). Rahasia
`APK_KEYSTORE_*` tetap satu-satunya salinan di luar Google — jangan dihapus. Firebase push tidak bergantung pada sidik kunci, jadi tidak ada yang perlu
didaftarkan ulang di Firebase Console.

## Yang dijaga otomatis

- `apk.yml`: AAB hanya dibangun dengan kunci toko (bundel bertanda tangan debug ditolak Play); targetSdk dibaca dari APK hasil bangun yang sama, < 36 =
  merah; kunci unggah wajib RSA ≥ 2048 bit; tanda tangan diverifikasi `jarsigner`; `apk/periksa_aab.py`: bentuk bundel, tanda tangan, pustaka native
  64-bit siap halaman 16 KB (hari ini bundel tanpa pustaka native). AAB gagal ≠ APK hilang (APK disimpan lebih dulu).
- `play-kunci.yml`: hanya bisa dijalankan manual; isian = kunci publik Google (PEM atau heksa), lain dari itu ditolak; `pepk.jar` dicocokkan sidik
  SHA-256; berkas kunci dihapus dari runner; artefak hidup 1 hari.
- `alat-uji/uji_google_play.py` (CI, dengan `--kontrol`): semua hal di atas + bahan toko (ukuran gambar, tanpa alfa di grafis, batas panjang teks, tanpa
  angka rupiah), halaman privasi (tanpa script, menyebut setiap kelompok data di Data safety).

## Sumber (dibaca 23 Nov 2026)

- Target API: <https://support.google.com/googleplay/android-developer/answer/11926878> — aplikasi baru & pembaruan wajib API 36 sejak 31 Agu 2026
  (perpanjangan sampai 1 Nov 2026); pengecualian: aplikasi privat permanen untuk satu organisasi.
- Syarat uji akun pribadi baru: <https://support.google.com/googleplay/android-developer/answer/14151465> — 12 penguji × 14 hari hanya untuk akses
  Produksi; uji internal bisa sebelum penyiapan aplikasi selesai.
- Play App Signing: <https://support.google.com/googleplay/android-developer/answer/9842756> — kunci unggah vs kunci aplikasi; aplikasi baru otomatis
  memakai kunci buatan Google kecuali diganti sebelum uji terbuka/produksi.
- Verifikasi developer Android: <https://android-developers.googleblog.com/2026/06/android-developer-verification.html> — 30 Sep 2026 Brasil,
  Indonesia, Singapura, Thailand untuk pemasangan dari toko peserta (termasuk Google Play); global 2027; akun Play Console memenuhi syaratnya.
- Verifikasi perangkat akun pribadi baru: <https://support.google.com/googleplay/android-developer/answer/14316361>.
- Aplikasi privat Managed Google Play: <https://support.google.com/googleplay/work/answer/6145139>.
- Capacitor 8 (targetSdk 36 bawaan; repo ini masih Capacitor 7 + angka SDK dinaikkan): <https://capacitorjs.com/docs/updating/8-0>.
