# Uji rules v12 di server — paket S2b tanda kenal (BELUM TERBIT)

v12 = v11 FINAL + **satu blok baru**, tanpa fungsi baru (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v11`). Tidak ada yang lain berubah —
`alat-uji/periksa_rules.py` mencabut balik blok itu lalu membandingkan sisanya huruf demi huruf dengan v11.

## Yang berubah v11 → v12 (satu)

1. **(v12-1) Tanda kenal** (`tandaKenal`, koleksi baru): pasangan kode → sasaran. `jenis: "barcode"` = barcode kemasan → barang di rak Jual;
   `jenis: "nfc"` = nomor seri kartu NFC → pembeli. Dibaca owner, ben, karyawan (tablet mengenali kode yang di-scan / ditempel); dibuat owner atau
   **ben / karyawan** atas nama sendiri — scanner dan pembaca NFC hanya ada di tablet, jadi pendaftaran harus bisa dari akun tablet; ubah & hapus owner.
   Catatan tambah-saja: memasangkan ulang = dokumen baru, yang terbaru menang. Bukan uang, bukan stok.

## Urutan (± 10 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus, akun owner). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish**.
4. Baru sesudah itu cabang S2b digabung (merge). **Jangan dibalik**: kalau aplikasi baru tayang sebelum v12 terbit, tablet (akun bukan-owner) ditolak
   server saat mendengarkan koleksi `tandaKenal`, dan pendaftaran barcode / kartu tidak bisa disimpan. Jual, struk, dan uang tidak bergantung padanya.

## Wajib owner (3 kasus — akun owner, tanpa dokumen uji)

Isi "TK": `{ id: "uji-v12-tk", jenis: "barcode", kode: "8990000000017", sasaran: { jalur: "kemasan", kunci: "Uji 5", berat: "", nama: "Uji 5 kg" }, tanggal: "2026-10-09", jam: "10:00", olehUid: "uid-uji-b" }`.
`sasaran` = map; semua nilainya string.

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★S1 | owner@ | create `tandaKenal/uji-v12-tk` | TK | LOLOS | blok baru v12 — owner mendaftarkan barcode |
| 2 | ★S2 | owner@ | update `tandaKenal/uji-v12-tk` | TK dengan `sasaran: null` | LOLOS | owner melepas pasangan |
| 3 | ★S3 | owner@ | delete `tandaKenal/uji-v12-tk` | — | LOLOS | owner menghapus pasangan |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben; ★S5 ★S9 memakai peran **karyawan**) dan dokumen
`tandaKenal/uji-v12-tk` = TK untuk kasus update / baca / hapus. Tanpa itu cukup percaya bukti emulator di bawah (mesin rules yang sama dengan server).
"KARTU" = TK dengan `jenis: "nfc"`, `kode: "04A1B2C3D4E5F6"`, `sasaran: { nama: "Contoh" }`.

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★S4 | staf aktif (ben) | create `tandaKenal/uji-v12-tk` | TK | LOLOS | barcode didaftarkan dari tablet (v12-1) |
| ★S5 | staf aktif peran **karyawan** | create `tandaKenal/uji-v12-tk` | KARTU | LOLOS | kartu pelanggan didaftarkan dari tablet |
| ★S6 | staf aktif (ben) | create `tandaKenal/uji-v12-tk` | TK dengan `olehUid: "uid-lain"` | DITOLAK | penulis bukan yang mengaku |
| ★S7 | staf aktif (ben) | update `tandaKenal/uji-v12-tk` | TK dengan `kode: "8990000000024"` | DITOLAK | pasangan yang tercatat tidak diubah staf (pasang ulang = dokumen baru) |
| ★S8 | staf aktif (ben) | delete `tandaKenal/uji-v12-tk` | — | DITOLAK | hapus = owner |
| ★S9 | staf aktif peran **karyawan** | get `tandaKenal/uji-v12-tk` | — | LOLOS | tablet mengenali kode yang di-scan / ditempel |
| ★S10 | kasir@ | get `tandaKenal/uji-v12-tk` | — | DITOLAK | kasir darurat tidak membaca tanda kenal |
| ★S11 | kasir@ | create `tandaKenal/uji-v12-tk` | TK | DITOLAK | kasir darurat tidak mendaftarkan |

Di **v11** kasus ★S1 ★S2 ★S3 ★S4 ★S5 ★S9 DITOLAK (bloknya belum ada; v12 yang membukanya); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V12** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): ke-11 kasus di
atas atas `firestore.rules` (v12) dan atas `firestore.rules.v11` — yang berbeda wajib persis kasus yang dibuka v12 — plus kontrol (satu suku v12 dirusak →
kasus sasarannya wajib berbalik). Semua kasus v11, v10, v9, v8 & v7 lama tetap dijalankan atas v12 dan wajib sama hasilnya.

## Hasil Playground & terbit

Belum diterbitkan. Diisi sesudah owner mengizinkan terbit: sidik isi editor, hasil tiga kasus Wajib owner, jam Publish.
