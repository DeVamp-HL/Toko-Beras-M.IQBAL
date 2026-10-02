# Sistem Toko Beras M.IQBAL — panduan proyek

Sistem kasir + pembukuan toko beras yang berbicara langsung ke Firebase Firestore, diterbitkan lewat GitHub Pages dari cabang `main`.
Sistem yang hidup: `baru/` (sistem utama owner) + kasir darurat staf. Sistem lama (`index.html`, satu berkas) dan kasir owner (`kasir.html`)
**pensiun 3 Okt 2026** (owner: "bumi hanguskan"): keduanya kini halaman pengalih ke `baru/`; versi terakhirnya utuh di tag git `sistem-lama-terakhir`
(commit `48a694d`) — jalan mundur di `docs/prosedur-pulih-darurat.md`.
Tidak ada build, tidak ada framework, tidak ada Node. Dokumen ini tentang *cara kerja repo*;
keputusan desain produk ada di `KEPUTUSAN-DESAIN.md`.

## Berkas

| Berkas | Peran |
|---|---|
| `baru/` | **Sistem utama owner** (sejak Sep 2026; panduannya `baru/BACA-DULU.md`). Kelak dibungkus menjadi aplikasi native — lihat bagian Arah di bawah. |
| `index.html` | **Halaman pengalih** ke `baru/` (sejak 3 Okt 2026): tanpa script, CSP `default-src 'none'` (dijaga `alat-uji/uji_csp.py`). Sengaja tidak dihapus — perangkat tanpa service worker yang membuka alamat lama tidak kena 404. `manifest-sistem.json` tetap ditautkan supaya ikon yang sudah terpasang sah. Sistem lamanya ada di tag `sistem-lama-terakhir`. |
| `kasir.html` | **Halaman pengalih** ke `baru/` (sejak 3 Okt 2026; dulu kasir ringan alat pemilik). `sw-kasir.js` v31 tidak lagi menyimpannya di cache, jadi pengalih selalu datang dari jaringan. |
| `kasir-darurat-nominal.html` + `sw-kasir.js` | Kasir **staf** (PWA offline). Kelak digantikan tablet kasir (lihat Arah) — **jangan disentuh** sampai itu. Setiap perubahan `kasir-darurat-nominal.html` wajib menaikkan `VERSI` di `sw-kasir.js` (bersama `VERSI_APLIKASI` + `LABEL_VERSI` darurat dan `KK_VERSI_KASIR_TERBARU` di `baru/js/data/katalog-kasir.js`). `FILES` service worker hanya boleh berisi berkas yang ADA (`alat-uji/uji_pensiun_sistem_lama.py`). |
| `firestore.rules` + `firebase.json` | Aturan akses Firestore. Rules dipasang ke Console oleh pemilik. |
| ~~`lib/`~~, ~~`manifest-kasir.json`~~, ~~`icon-kasir-192/512.png`~~ | **Dihapus 3 Okt 2026** bersama sistem lama (hanya dipakai `index.html` / `kasir.html` lama). Ada di tag `sistem-lama-terakhir` — prosedur pulih mengambil POHON tag, bukan `index.html` saja, supaya `lib/` ikut. |
| `alat-uji/` | Jaring pengaman yang dijalankan CI sebelum terbit (lihat bawah). |
| `alat-audit/audit.py` | Pemeriksa independen (Python) yang menghitung ulang uang dari berkas backup. |
| `.github/workflows/pages.yml` | CI: job `uji` di setiap push/PR; `terbitkan` hanya di `main` sesudah `uji` hijau. |
| `docs/` | Dokumen proyek (tanpa angka bisnis). |

Catatan bisnis (omzet, piutang, utang, harga beli) **tidak pernah** masuk repo — lihat `.gitignore`.

## Arah (keputusan owner 24 Sep 2026)

- **`baru/` = sistem utama owner**, kelak dibungkus menjadi aplikasi native. Catatan lama tanggal 13 Sep (di mesin owner,
  `_privat/rapikan-2026-09-13/peta_native.md` dan `skeptis_native.md`: Capacitor, Ad Hoc/TestFlight + APK, tanpa App Store) masih menyebut
  `index.html` — itu **bahan, bukan keputusan**.
- **Tablet kasir = offline-first**, satu perangkat dipakai bergantian, semua akun seizin owner. Pilihan identitasnya (login per orang, atau satu
  akun tablet + PIN per orang) diputuskan di putaran tablet; putaran 23 (akun per orang) sengaja tidak menutup salah satunya.
- **`index.html` & `kasir.html` pensiun 3 Okt 2026** (owner: "bumi hanguskan"; prasyarat owner beres hari itu: HP kasir melapor 0 antrean / 0 ditolak,
  perangkat lama ditandai tidak dipakai). Rincian & yang ikut hilang: `docs/peta-pensiun-sistem-lama.md` §8.

## Jaring pengaman (`alat-uji/`)

Semua bisa dijalankan dari folder mana pun, tanpa Node, cukup macOS (jsc bawaan) + Python 3.

| Perintah | Membuktikan | Gagal = |
|---|---|---|
| `alat-uji/periksa.sh` (bawaan `kasir-darurat-nominal.html`) | sintaks script (jsc), tidak ada sintaks pasca-Chrome-80, id DOM unik, handler sebaris menunjuk fungsi yang ada (kasir darurat sejak kasir-v32 tanpa handler sebaris — `data-aksi` dijaga `uji_csp.py`), `getElementById` menunjuk id yang ada, batas gerak kasir. Berkas tanpa `<script>` (pengalih) DITOLAK | keluar ≠ 0 |
| `alat-uji/periksa.sh --kontrol` | salinan rusak (sintaks, pasca-Chrome-80, id ganda, gerak) wajib gagal; salinan utuh lulus | 3 |
| `python3 alat-uji/beku2.py --sidik` | tubuh **26 mesin uang beku** (`baru/js/mesin/beku.js`) byte-identik dengan `alat-uji/beku.sha256`, dan **55 fungsi + 36 konstanta pembantu** (`pembantu.js`) dengan `alat-uji/pembantu.sha256` | 2 |
| `python3 alat-uji/beku2.py --lama main` | sama, tapi dibandingkan ke `main` (dipakai di cabang kerja) | 2 |
| `python3 alat-uji/beku2.py --uji-diri` | alat pembanding terbukti MELIHAT perubahan (mutasi di memori pada satu mesin, satu fungsi & satu konstanta pembantu, satu fungsi tanpa kunci) | 3 |
| `python3 alat-uji/lingkup.py` (bawaan `kasir-darurat-nominal.html`) | tidak ada nama fungsi yang dipanggil tanpa pernah dideklarasikan (statis, kasar) | 2 |
| `python3 alat-uji/lingkup.py --kontrol` | pemeriksa lingkup terbukti menangkap nama palsu | 3 |
| `python3 alat-uji/uji_pensiun_sistem_lama.py` (+ `--kontrol`) | pengalih ada; `FILES` service worker = berkas yang ada & tanpa `kasir.html`; langkah CI / seed HawkScan / manifest menunjuk berkas yang ada; `/baru/` tanpa tautan sistem lama | 1 / 3 |

Sisanya (kotak pasir `/baru/` di jsc, uji peramban di runner) terdaftar di `.github/workflows/pages.yml` dan `baru/BACA-DULU.md` › Gerbang.

**Pensiun 3 Okt 2026 — yang dihapus bersama objeknya** (alasan juga tertulis di `pages.yml`): `alat-uji/harness/` (mengevaluasi modul
`index.html`), `alat-uji/pindah_mesin.py` (menyalin mesin dari `index.html`; sumber kebenaran kini `baru/js/mesin/` + `beku2.py`),
`uji_sistem_lama_bacasaja.py` (penjaga tulis `index.html`), dan empat penjaga pola yang hanya membaca `index.html` dan tidak dijalankan CI:
`uji_dua_arah.py`, `uji_gagal_tertutup.py`, `uji_onclick_aman.py`, `uji_stok_minus.py` (+ `ukur_jepitan.sh`). Apakah keempat pola cacat itu
(jepitan dua arah, gerbang yang gagal membuka, onclick tanpa escape, stok minus dibaca "0") sudah punya penjaga setara di `/baru/` BELUM diperiksa
satu per satu; onclick sebaris di `/baru/` dan kasir darurat (kasir-v32) sudah tertutup CSP (`uji_csp.py`).

### Membekukan ulang mesin uang (= membuka mesin)
`alat-uji/beku.sha256` & `alat-uji/pembantu.sha256` hanya boleh berubah lewat `python3 alat-uji/beku2.py --catat`
**atas perintah pemilik**, dalam commit yang menyebut "membekukan ulang" dan mesin/pembantu mana yang
berubah beserta alasannya. CI menolak deploy bila sidik tidak cocok. Sejak 3 Okt 2026 mesinnya disunting langsung di
`baru/js/mesin/beku.js` / `pembantu.js` (dulu disalin dari `index.html` oleh `pindah_mesin.py`, kini pensiun). Kepala komentar kedua berkas
itu masih menyebut `pindah_mesin.py` — sengaja dibiarkan, karena berkas mesin hanya dibuka atas izin owner.

## Prinsip kerja

1. **26 mesin uang beku + pembantunya byte-identik.** `beku2.py --sidik` dijalankan sebelum setiap commit; hasilnya
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
`python3 -m http.server 8731 --bind 127.0.0.1` dari akar repo, lalu buka `http://localhost:8731/baru/index.html` (atau `/`, yang mengalihkan
ke sana). Login memakai akun Firebase toko — angka & tulisan sungguhan; untuk uji tanpa menulis ke toko pakai kotak pasir `alat-uji/uji_*_baru.py`.
Server dimatikan sesudah dipakai. Menjalankan **sistem lama** (darurat): `docs/prosedur-pulih-darurat.md`.
