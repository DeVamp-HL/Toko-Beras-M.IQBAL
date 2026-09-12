# Sistem Toko Beras M.IQBAL — panduan proyek

Sistem kasir + pembukuan toko beras: satu berkas `index.html` (HTML + CSS + satu modul JavaScript)
yang berbicara langsung ke Firebase Firestore, diterbitkan lewat GitHub Pages dari cabang `main`.
Tidak ada build, tidak ada framework, tidak ada Node. Dokumen ini tentang *cara kerja repo*;
keputusan desain produk ada di `KEPUTUSAN-DESAIN.md`.

## Berkas

| Berkas | Peran |
|---|---|
| `index.html` | **Sistem utama** (alat pemilik). Akan menjadi aplikasi native iOS/Android. |
| `kasir.html` | Kasir ringan **alat pemilik** (nama berkasnya menyesatkan). |
| `kasir-darurat-nominal.html` + `sw-kasir.js` + `manifest-kasir.json` | Kasir **staf** (PWA offline). Akan disatukan menjadi satu kasir tablet — **jangan disentuh** sampai sistem utama selesai dirapikan. Setiap perubahan `kasir*.html` wajib menaikkan `VERSI` di `sw-kasir.js`. |
| `firestore.rules` + `firebase.json` | Aturan akses Firestore. Rules dipasang ke Console oleh pemilik. |
| `alat-uji/` | Jaring pengaman yang dijalankan CI sebelum terbit (lihat bawah). |
| `alat-audit/audit.py` | Pemeriksa independen (Python) yang menghitung ulang uang dari berkas backup. |
| `.github/workflows/pages.yml` | CI: job `uji` di setiap push/PR; `terbitkan` hanya di `main` sesudah `uji` hijau. |
| `docs/` | Dokumen proyek (tanpa angka bisnis). |

Catatan bisnis (omzet, piutang, utang, harga beli) **tidak pernah** masuk repo — lihat `.gitignore`.

## Jaring pengaman (`alat-uji/`)

Semua bisa dijalankan dari folder mana pun, tanpa Node, cukup macOS (jsc bawaan) + Python 3.

| Perintah | Membuktikan | Gagal = |
|---|---|---|
| `alat-uji/periksa.sh index.html` | sintaks modul (jsc), tidak ada sintaks pasca-Chrome-80, id DOM unik, `onclick` menunjuk fungsi yang ada, `getElementById` menunjuk id yang ada | keluar ≠ 0 |
| `alat-uji/harness/jalankan.sh index.html` | **seluruh modul** bisa dievaluasi sampai baris terakhir di JavaScriptCore dengan DOM & Firebase palsu — satu ReferenceError/TDZ di lingkup modul mematikan seluruh aplikasi | 3 |
| `alat-uji/harness/jalankan.sh --kontrol` | harness itu sendiri bisa GAGAL: dua modul cacat sengaja (TDZ, referensi hilang) wajib gagal | 3 |
| `python3 alat-uji/beku2.py --sidik` | tubuh **28 mesin uang beku** byte-identik dengan `alat-uji/beku.sha256` | 2 |
| `python3 alat-uji/beku2.py --lama main` | sama, tapi dibandingkan ke `main` (dipakai di cabang kerja) | 2 |
| `python3 alat-uji/beku2.py --uji-diri` | alat pembanding terbukti MELIHAT perubahan (mutasi di memori pada satu mesin & satu kontrol) | 3 |
| `python3 alat-uji/lingkup.py index.html` | tidak ada nama fungsi yang dipanggil tanpa pernah dideklarasikan (statis, kasar) | 2 |
| `python3 alat-uji/lingkup.py --kontrol` | pemeriksa lingkup terbukti menangkap nama palsu | 3 |

Yang **tidak** dibuktikan alat-alat ini: tampilan, klik, dan angka. Untuk itu ada kotak pasir
tulis-nol di peramban (lihat `docs/` putaran berikutnya) dan uji identitas dari konsol
(`ujiUtangOwner()`, `ujiKonsistensiLaporan()`, `ujiPenjagaCadangan()`).

### Membekukan ulang mesin uang
`alat-uji/beku.sha256` hanya boleh berubah lewat `python3 alat-uji/beku2.py --catat`
**atas perintah pemilik**, dalam commit yang menyebut "membekukan ulang" dan mesin mana yang
berubah beserta alasannya. CI menolak deploy bila sidik tidak cocok.

## Prinsip kerja

1. **28 mesin uang beku byte-identik.** `beku2.py` dijalankan sebelum setiap commit; hasilnya
   ditempel di laporan putaran. Komentar di dalam tubuh mesin pun tidak disentuh.
2. **Satu putaran = satu cabang = satu gerbang pemilik.** Commit ke cabang, lapor, berhenti.
   Merge/push ke `main` hanya sesudah pemilik memeriksa putaran itu; izin tidak menyeberang
   antar putaran.
3. **Tidak ada perubahan perilaku uang tanpa perintah.** Perbaikan cacat yang mengubah angka
   di layar dilaporkan sebagai perbaikan cacat, bukan disembunyikan dalam "rapi-rapi".
4. **Lantai Chrome 80** untuk JavaScript: tanpa `??=` `||=` `&&=` `.at(` `.replaceAll(`
   `Object.hasOwn` `structuredClone` `.findLast` `.toSorted` `.flatMap(` `#private`.
   (`?.` dan `??` boleh — tepat di Chrome 80.)
5. **Klaim negatif wajib kontrol positif.** "Tidak ada X" hanya sah kalau pola yang sama
   terbukti menemukan sesuatu yang diketahui ada. Alat-alat di atas punya `--kontrol` /
   `--uji-diri` karena alasan ini.
6. **Kaca Emas (<700 px) adalah jalur utama**; jalur desktop dirawat, tidak diperluas.
7. **Yang bisa hilang ditulis terakhir.** Urutan tulis ke Firestore dan localStorage mengikuti
   aturan ini.
8. **Pesan commit tanpa nominal uang toko dan tanpa nama orang.** Repo ini publik.
9. **Angka rupiah di laporan selalu menyebut sumbernya**: angka toko, kotak pasir, konstanta
   kode, atau contoh hitung.

## Menjalankan secara lokal
`python3 -m http.server 8731` dari akar repo, lalu buka `http://localhost:8731/index.html`.
Login memakai akun Firebase toko; untuk uji tanpa menulis ke toko, pakai kotak pasir tulis-nol
(dibangun dari `index.html` dengan Firebase distub — dokumentasinya menyusul di `docs/`).
