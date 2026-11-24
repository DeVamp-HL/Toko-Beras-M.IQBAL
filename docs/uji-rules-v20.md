# Uji rules v20 di server — buku pegangan terbaca staf (DRAF 24 Nov 2026)

v20 = v19 FINAL + **satu nama dokumen di satu baris baca** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v19`).
Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v19.

## Yang berubah v19 → v20

1. **(v20-1) `aturanToko` read: + dokumen `bukuPegangan`** — Pondasi paket kedua bagian C, keputusan owner 24 Nov 2026: "Tetap rules v20".
   - dokumen `aturanToko/bukuPegangan` = aturan kerja tertulis toko (bab: judul, isi, untuk siapa), diisi owner di Menu › Toko ini › Buku pegangan;
   - **baca**: owner, Penjaga laci & karyawan (dibaca di tablet);
   - **tulis (buat · ubah · hapus)**: owner saja — baris tulis `aturanToko` TIDAK berubah.

Bukan data toko yang dikunci: tidak ada rupiah, kg, stok, atau tanggal buku. **Terbitkan v20 SEBELUM PR buku pegangan digabung** — halaman baru mendengar
dokumen `aturanToko/bukuPegangan` di HP/tablet staf; tanpa v20 pendengarnya ditolak server (aplikasi tetap jalan, tapi Sistem › Perangkat di perangkat itu
menyebut dokumennya ditolak) dan staf melihat "buku pegangan belum bisa dibaca". Owner tetap bisa mengisi dan membacanya dari HP / Mac.

## Urutan (± 5 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (dua kasus). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish** — sebelum PR digabung.
4. Sesudah terbit dan PR digabung: di HP owner buka Menu › Toko ini › **Buku pegangan**, tulis satu bab, simpan; di tablet (akun Penjaga laci atau karyawan)
   buka Menu › **Buku pegangan** — bab itu tampil.

## Wajib owner (2 kasus — tanpa dokumen uji staf)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★D1 | owner@ | create `aturanToko/bukuPegangan` | satu bab | LOLOS | owner menulis buku pegangan |
| 2 | ★D2 | owner@ | get `aturanToko/bukuPegangan` | — | LOLOS | owner membacanya |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator di bawah
(mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★D3 | Penjaga laci | get `aturanToko/bukuPegangan` | — | LOLOS | tablet membaca buku pegangan |
| ★D4 | karyawan | get `aturanToko/bukuPegangan` | — | LOLOS | karyawan juga membacanya |
| ★D5 | Penjaga laci | update `aturanToko/bukuPegangan` | bab dikosongkan | DITOLAK | tulis = owner saja |
| ★D6 | karyawan | create `aturanToko/bukuPegangan` | satu bab | DITOLAK | tulis = owner saja |
| ★D7 | Penjaga laci | delete `aturanToko/bukuPegangan` | — | DITOLAK | hapus = owner saja |
| ★D8 | kasir@ | get `aturanToko/bukuPegangan` | — | DITOLAK | kasir darurat tidak membaca setelan |
| ★D9 | Penjaga laci nonaktif | get `aturanToko/bukuPegangan` | — | DITOLAK | akun yang dinonaktifkan owner |
| ★D10 | Penjaga laci | get `aturanToko/pondasi` | — | DITOLAK | setelan yang tidak didaftar tetap tertutup |
| ★D11 | Penjaga laci | get `aturanToko/peran` | — | LOLOS | setelan yang sudah terbuka tidak berubah |

Di **v19** kasus ★D3 & ★D4 DITOLAK (dokumennya belum di daftar baca staf); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V20** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): kesebelas kasus di
atas atas `firestore.rules` (v20) dan atas `firestore.rules.v19` — yang berbeda wajib persis ★D3 & ★D4 — plus kontrol (ubahan v20 dirusak → kasus sasarannya
wajib berbalik). Semua kasus v19 sampai v7 lama tetap dijalankan atas v20 dan wajib sama hasilnya.
