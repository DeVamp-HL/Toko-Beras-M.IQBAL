# Uji rules v18 di server — denyut staf terikat penulisnya (DRAF 24 Nov 2026)

v18 = v17 FINAL + **satu ubahan fungsi dan satu baris pemanggilnya** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v17`).
Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v17.

## Yang berubah v17 → v18

1. **(v18-1) `stafDenyut(peranBoleh, id)`** — temuan tinjauan 30 Sep (d). Denyut akun ben / karyawan di `perangkatStatus` kini TERIKAT ke penulisnya:
   - id dokumen wajib `<perangkat>~<uid penulis>` (perangkat 1–40 huruf tanpa `~` atau `/`), dan kolom `id` = id dokumen;
   - dokumen yang sudah ada hanya bisa ditimpa bila `akunUid`-nya = penulis. Dulu dokumen TANPA `akunUid` (denyut kasir@ / bentuk lama) bisa ditimpa
     staf, dan id-nya bebas.
   - `perangkatStatus` create / update meneruskan `id` ke fungsinya. Owner dan kasir@ tidak berubah.

Halaman tidak berubah: perangkat staf sudah menulis denyutnya ke `perangkat~uid` dengan kolom `id` & `akunUid` = penulis. Bukan data toko: tidak ada uang,
stok, tanggal buku, atau kunci periode yang tersentuh.

## Urutan (± 5 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (dua kasus). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish**. Boleh kapan saja — sebelum atau sesudah PR digabung, tidak ada yang rusak.
4. Sesudah terbit: buka Menu › Perangkat & antrean di HP owner — denyut tablet & HP staf tetap muncul (berjalan seperti biasa).

## Wajib owner (2 kasus — tanpa dokumen uji)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★V1 | owner@ | create `perangkatStatus/p-uji-1` | denyut atas nama owner | LOLOS | owner tidak berubah |
| 2 | ★V2 | kasir@ | create `perangkatStatus/d-uji` | denyut kasir darurat | LOLOS | kasir@ tidak berubah |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator di bawah
(mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★V3 | Penjaga laci | create `perangkatStatus/p-uji-1~uid-uji-b` | denyut atas namanya | LOLOS | tablet berdenyut |
| ★V4 | Penjaga laci | update `perangkatStatus/p-uji-1~uid-uji-b` | antrean berubah | LOLOS | denyut berikutnya |
| ★V5 | karyawan | create `perangkatStatus/p-uji-1~uid-uji-b` | denyut atas namanya | LOLOS | HP karyawan berdenyut |
| ★V6 | Penjaga laci | update `perangkatStatus/p-uji-1` | menimpa denyut owner | DITOLAK | milik owner |
| ★V7 | Penjaga laci | update `perangkatStatus/p-uji-2` | menimpa denyut lama tanpa akunUid | DITOLAK | ditutup v18 |
| ★V8 | Penjaga laci | create `perangkatStatus/p-uji-1~uid-lain` | id milik akun lain | DITOLAK | ditutup v18 |
| ★V9 | Penjaga laci | create `perangkatStatus/p-uji-1~uid-uji-b` | kolom id beda dari id dokumen | DITOLAK | ditutup v18 |
| ★V10 | Penjaga laci | create `perangkatStatus/p-uji-3` | id tanpa ~uid | DITOLAK | ditutup v18 |
| ★V11 | Penjaga laci | create `perangkatStatus/p-uji-1~uid-uji-b` | akunUid akun lain | DITOLAK | denyut = milik penulis |
| ★V12 | Penjaga laci nonaktif | create `perangkatStatus/p-uji-1~uid-uji-b` | denyut | DITOLAK | akun yang dinonaktifkan owner |
| ★V13 | Penjaga laci | update `perangkatStatus/p-uji-1~uid-uji-b` | dokumen lama di id itu tanpa akunUid | DITOLAK | ditutup v18 (pemilik tidak tercatat) |

Di **v17** kasus ★V7–★V10 dan ★V13 LOLOS (yang ditutup v18); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V18** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): ke-13 kasus di
atas atas `firestore.rules` (v18) dan atas `firestore.rules.v17` — yang berbeda wajib persis kasus yang ditutup v18 — plus kontrol (satu suku v18 dirusak →
kasus sasarannya wajib berbalik). Semua kasus v17 sampai v7 lama tetap dijalankan atas v18 dan wajib sama hasilnya.
