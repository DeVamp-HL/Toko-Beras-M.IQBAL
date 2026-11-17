# Uji rules v9 di server — B2 faktur bertempo & batas kredit (DRAF 17 Nov 2026, belum terbit)

v9 = v8 FINAL + **satu ubahan kecil** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v8`). Tidak ada yang lain berubah —
`alat-uji/periksa_rules.py` mencabut balik ubahan ini lalu membandingkan sisanya huruf demi huruf dengan v8.

## Yang berubah v8 → v9 (satu)

1. **(v9-1) Permintaan bon dari Ben.** `persetujuan` create: selain permintaan nego (v7) dan usul harga pelanggan (v8), **ben** boleh mengirim
   **permintaan persetujuan bon** waktu batas kredit pelanggan terlewati — tindakan `kredit`, status `menunggu`, `mintaUid` = uid penulis, tanpa kolom
   keputusan (`stafMintaKredit`). Karyawan tidak (bon memang hanya ben, sejak v3). Memutus (setuju / tolak) tetap owner. Nama pelanggan & nominal tidak diikat
   rules — papan Persetujuan owner menghitung ulang kalimatnya dari buku bon sekarang sebelum owner memutus.

Faktur sendiri **tidak butuh ubahan rules**: nomor faktur, jatuh tempo, dan tempo hanyalah kolom di baris penjualan (`noFaktur`, `jatuhTempo`, `tempoHari`),
dan pembayaran yang memilih faktur membawa `untukFaktur` — keduanya lewat jalur tulis yang sudah ada.

## Urutan (± 10 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (dua kasus, akun owner). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish**.
4. Baru sesudah itu cabang B2 digabung (merge). **Jangan dibalik**: kalau aplikasi baru tayang sebelum v9 terbit, tombol "Minta persetujuan owner"
   di tablet Ben ditolak server (pil status menyebut "ditolak") sampai v9 terbit. Jual, faktur, dan pembayaran tetap jalan.

## Wajib owner (2 kasus — akun owner, tanpa dokumen uji)

Isi "MINTA": `{ id: "uji-v9-kredit", tindakan: "kredit", status: "menunggu", mintaUid: "uid-uji-b", olehUid: "uid-uji-b", pelanggan: "Contoh", nominal: 50000, teks: "uji" }`.

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★K2 | owner@ | create `persetujuan/uji-v9-kredit` | MINTA | LOLOS | owner selalu boleh menulis persetujuan |
| 2 | ★K3 | owner@ | update `persetujuan/uji-v9-kredit` | MINTA dengan `status: "disetujui"`, `diputusPada: "x"` | LOLOS | owner memutus |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator di bawah
(mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★K1 | staf aktif (ben) | create `persetujuan/uji-v9-kredit` | MINTA | LOLOS | Ben meminta persetujuan bon (v9-1) |
| ★K4 | staf aktif (ben) | create `persetujuan/uji-v9-kredit` | MINTA dengan `mintaUid: "uid-lain"` | DITOLAK | permintaan atas nama orang lain |
| ★K5 | staf aktif (ben) | create `persetujuan/uji-v9-kredit` | MINTA dengan `status: "disetujui"` | DITOLAK | staf tidak menyetujui sendiri |
| ★K6 | staf aktif (ben) | create `persetujuan/uji-v9-kredit` | MINTA dengan `diputusPada` | DITOLAK | kolom keputusan milik owner |
| ★K7 | staf aktif (ben) | update `persetujuan/uji-v9-kredit` | MINTA dengan `status: "disetujui"` | DITOLAK | memutus = owner |
| ★K8 | staf aktif peran **karyawan** | create `persetujuan/uji-v9-kredit` | MINTA | DITOLAK | bon (dan memintanya) = ben saja |
| ★K9 | akun tanpa aksesAkun (`baru1`) | create `persetujuan/uji-v9-kredit` | MINTA dengan `mintaUid` & `olehUid` "baru1" | DITOLAK | bukan staf aktif |
| ★K10 | staf aktif (ben) | create `persetujuan/uji-v9-kredit` | MINTA dengan `olehUid: "uid-lain"` | DITOLAK | penulis bukan yang mengaku |
| ★K11 | kasir@ | create `persetujuan/uji-v9-kredit` | MINTA dengan `mintaUid` & `olehUid` = uid kasir | DITOLAK | kasir darurat tidak meminta |

Di **v8**, ★K1 DITOLAK (itulah yang dibuka v9); semua kasus lain hasilnya sama dengan v8.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V9** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): kesebelas kasus di
atas atas `firestore.rules` (v9) dan atas `firestore.rules.v8` — yang berbeda wajib persis ★K1 — plus kontrol (satu suku v9 dirusak → kasus sasarannya
wajib berbalik). Semua kasus v8 & v7 lama tetap dijalankan atas v9 dan wajib sama hasilnya.
