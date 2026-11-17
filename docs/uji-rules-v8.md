# Uji rules v8 di server — B1 harga pelanggan usaha (TERBIT 17 Nov 2026 ±03.27 WIB; kini v9 = v8 + satu ubahan, lihat `docs/uji-rules-v9.md`)

v8 = v7 FINAL + **tiga ubahan kecil** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v7`). Tidak ada yang lain berubah —
`alat-uji/periksa_rules.py` mencabut balik tiga ubahan ini lalu membandingkan sisanya huruf demi huruf dengan v7.

## Yang berubah v7 → v8 (tiga)

1. **(v8-1) `aturanToko/hargaTingkat` dibaca ben/karyawan.** Setelan harga pelanggan usaha (tingkat Warung · Catering · Instansi, harga barang per
   tingkat, harga khusus per pelanggan, siapa di tingkat mana). Kasir di tablet butuh membacanya supaya harga di Jual ikut tingkat pembelinya.
   **Menulisnya tetap owner saja.**
2. **(v8-2) `aturanToko/produkArsip` dibaca ben/karyawan.** Barang yang diarsipkan owner tidak lagi tampil sebagai chip "habis" di rak Jual tablet.
3. **(v8-3) Usul harga dari staf.** `persetujuan` create: selain permintaan nego (v7), ben/karyawan boleh mengirim **usul harga pelanggan** —
   tindakan `hargaPelanggan`, status `menunggu`, `usulUid` = uid penulis, tanpa kolom keputusan (`stafUsulHarga`). Memutus (setuju / tolak) tetap
   owner; saat owner menyetujui, perangkat owner yang menulis `aturanToko/hargaTingkat`. Isi usulnya tidak diikat rules — papan Persetujuan owner
   menghitung ulang kalimatnya dari setelan sekarang sebelum owner memutus.

## Urutan (± 10 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (dua kasus, akun owner). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish**.
4. Baru sesudah itu cabang B1 digabung (merge). **Jangan dibalik**: kalau aplikasi baru tayang sebelum v8 terbit, tablet mencoba membaca
   `aturanToko/hargaTingkat` & `produkArsip` dan server menolaknya — pil status tablet menyebut "ditolak" sampai v8 terbit (data lain tetap jalan).

## Wajib owner (2 kasus — akun owner, tanpa dokumen uji)

Isi "SETELAN": `{ id: "hargaTingkat", tingkat: [{ id: "warung", nama: "Warung", potKg: 300 }], barang: {}, orang: {}, khusus: [] }`.

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★H5 | owner@ | update `aturanToko/hargaTingkat` | SETELAN dengan `orang: { contoh: "warung" }` | LOLOS | owner mengatur harga pelanggan |
| 2 | ★H6 | owner@ | create `aturanToko/hargaTingkat` | SETELAN | LOLOS | setelan pertama kali dibuat |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator
di bawah (mesin rules yang sama dengan server). Isi "USUL": `{ id: "uji-v8-usul", tindakan: "hargaPelanggan", status: "menunggu", usulUid: "uid-uji-b",
olehUid: "uid-uji-b", teks: "uji", ubah: { jenis: "orang", orang: "contoh", nama: "Contoh", tingkatId: "warung" } }`.

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★H1 | staf aktif | get `aturanToko/hargaTingkat` | — | LOLOS | kasir membaca harga pelanggan (v8-1) |
| ★H2 | staf aktif | get `aturanToko/produkArsip` | — | LOLOS | rak tablet tahu barang yang diarsip (v8-2) |
| ★H3 | staf aktif | create `persetujuan/uji-v8-usul` | USUL | LOLOS | Ben mengusulkan (v8-3) |
| ★H4 | owner@ | update `persetujuan/uji-v8-usul` | USUL dengan `status: "disetujui"`, `diputusPada: "x"` | LOLOS | owner memutus |
| ★H7 | staf aktif | create `persetujuan/uji-v8-usul` | USUL dengan `usulUid: "uid-lain"` | DITOLAK | usul atas nama orang lain |
| ★H8 | staf aktif | create `persetujuan/uji-v8-usul` | USUL dengan `status: "disetujui"` | DITOLAK | staf tidak menyetujui sendiri |
| ★H9 | staf aktif | create `persetujuan/uji-v8-usul` | USUL dengan `diputusPada` | DITOLAK | kolom keputusan milik owner |
| ★H10 | staf aktif | update `persetujuan/uji-v8-usul` | USUL dengan `status: "disetujui"` | DITOLAK | memutus = owner |
| ★H11 | staf aktif | update `aturanToko/hargaTingkat` | SETELAN | DITOLAK | setelan harga hanya ditulis owner |
| ★H12 | staf aktif | get `aturanToko/het` | — | DITOLAK | setelan lain tetap owner saja |
| ★H13 | akun tanpa aksesAkun (`baru1`) | create `persetujuan/uji-v8-usul` | USUL dengan `usulUid` & `olehUid` "baru1" | DITOLAK | bukan staf aktif |
| ★H14 | kasir@ | get `aturanToko/hargaTingkat` | — | DITOLAK | kasir darurat tidak membaca setelan |
| ★H15 | staf aktif | create `persetujuan/uji-v8-usul` | USUL dengan `olehUid: "uid-lain"` | DITOLAK | penulis bukan yang mengaku |

Di **v7**, ★H1, ★H2, ★H3 DITOLAK (itulah yang dibuka v8); semua kasus lain hasilnya sama dengan v7.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V8** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): kelima belas
kasus di atas atas `firestore.rules` (v8) dan atas `firestore.rules.v7` — yang berbeda wajib persis ★H1–★H3 — plus kontrol (satu suku v8 dirusak →
kasus sasarannya wajib berbalik). Semua kasus v7 lama tetap dijalankan atas v8 dan wajib sama hasilnya.
