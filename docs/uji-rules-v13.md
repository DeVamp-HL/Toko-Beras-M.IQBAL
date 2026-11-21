# Uji rules v13 di server — titipan uang keluar & pesan dari tablet + notifikasi HP owner (DRAF 21 Nov 2026)

v13 = v12 FINAL + **satu ubahan, dua fungsinya, dan satu blok baru** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v12`). Tidak ada
yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v12.

## Yang berubah v12 → v13

1. **(v13-1) `persetujuan` create** + `stafMintaKeluar(['ben', 'karyawan'])` + `stafKirimPesan(['ben', 'karyawan'])`:
   - **Titipan uang keluar** dari tablet: `tindakan: "uangKeluar"`, `status: "menunggu"`, `mintaUid` = penulisnya, `jenis` = `toko` / `karyawan` /
     `kasbon`, `nominal` bilangan bulat > 0, tanpa kolom keputusan (`diputusPada`, `diputusTanggal`, `diputusJam`, `alasanTolak`) dan tanpa kolom
     betulan owner (`koreksiOwner`, `balasan`). **Bukan dokumen uang**: uangnya (`pengeluaranHarian` / `kasbonMutasi`) ditulis OWNER saat
     menyetujui. Rules uang tidak berubah — akun tablet tetap tidak bisa menulis dokumen uang.
   - **Pesan untuk owner**: `tindakan: "pesan"`, `status: "menunggu"`, `mintaUid` = penulisnya, `teks` 1–500 huruf, tanpa kolom keputusan dan tanpa
     `balasan`. Owner menandai dibaca & membalas lewat update (owner saja, sejak v7).
2. **(v13-2) Blok `notifOwner`** (koleksi baru): token notifikasi HP / Mac owner untuk push saat aplikasi tertutup. Baca & tulis **owner saja**.
   Fungsi server membacanya lewat Admin SDK (tidak lewat rules).

## Urutan (± 10 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus, akun owner). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish**.
4. Baru sesudah itu cabangnya digabung (merge). **Jangan dibalik**: kalau aplikasi baru tayang sebelum v13 terbit, titipan dan pesan dari tablet
   ditolak server ("DITOLAK"), dan tombol "Notifikasi di HP ini" gagal menyimpan token. Jual, stok, dan uang owner tidak bergantung padanya.

## Wajib owner (3 kasus — akun owner, tanpa dokumen uji)

Isi "TT" (titipan): `{ id: "uji-v13-tt", tindakan: "uangKeluar", status: "menunggu", jenis: "toko", nominal: 50000, teks: "Kantong 5 kg", dariTempat: "laci", mintaUid: "uid-uji-b", olehUid: "uid-uji-b", dari: "Uji", peran: "ben", tanggal: "2026-10-09", jam: "10:00" }`.
Isi "HP" (token): `{ id: "uji-v13-hp", token: "token-uji", perangkat: "HP uji", pada: "2026-10-09T03:00:00.000Z" }`.
`nominal` = bilangan bulat (integer), bukan teks.

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★U1 | owner@ | update `persetujuan/uji-v13-tt` | TT dengan `status: "disetujui"`, `diputusTanggal: "2026-10-09"` | LOLOS | owner memutus titipan (sama dengan v12) |
| 2 | ★U2 | owner@ | create `notifOwner/uji-v13-hp` | HP | LOLOS | blok baru v13 — HP owner menyimpan tokennya |
| 3 | ★U3 | owner@ | delete `notifOwner/uji-v13-hp` | — | LOLOS | owner mematikan notifikasi di HP itu |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben; ★U5 memakai peran **karyawan**) dan dokumen
`persetujuan/uji-v13-tt` = TT / `notifOwner/uji-v13-hp` = HP untuk kasus update / baca. Tanpa itu cukup percaya bukti emulator di bawah (mesin rules
yang sama dengan server). "PS" (pesan) = `{ id: "uji-v13-ps", tindakan: "pesan", status: "menunggu", teks: "Kantong 5 kg tinggal 20 lembar", mintaUid: "uid-uji-b", olehUid: "uid-uji-b", dari: "Uji", peran: "ben", tanggal: "2026-10-09", jam: "10:00" }`.

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★U4 | staf aktif (ben) | create `persetujuan/uji-v13-tt` | TT | LOLOS | titipan belanja toko dari tablet (v13-1) |
| ★U5 | staf aktif peran **karyawan** | create `persetujuan/uji-v13-tt` | TT dengan `jenis: "kasbon"`, `namaPegawai: "Uji"`, `peran: "karyawan"` | LOLOS | titipan kasbon dari tablet |
| ★U6 | staf aktif (ben) | create `persetujuan/uji-v13-ps` | PS | LOLOS | pesan untuk owner (v13-1) |
| ★U7 | staf aktif (ben) | create `persetujuan/uji-v13-tt` | TT dengan `mintaUid: "uid-lain"` | DITOLAK | titipan atas nama akun lain |
| ★U8 | staf aktif (ben) | create `persetujuan/uji-v13-tt` | TT dengan `status: "disetujui"` | DITOLAK | tablet tidak menyetujui sendiri |
| ★U9 | staf aktif (ben) | create `persetujuan/uji-v13-tt` | TT dengan `koreksiOwner: true` | DITOLAK | kolom betulan hanya ditulis owner |
| ★U10 | staf aktif (ben) | create `persetujuan/uji-v13-tt` | TT dengan `jenis: "pribadi"` | DITOLAK | hanya belanja toko, untuk karyawan, kasbon |
| ★U11 | staf aktif (ben) | create `persetujuan/uji-v13-tt` | TT dengan `nominal: 0` | DITOLAK | nominal wajib > 0 |
| ★U12 | staf aktif (ben) | create `persetujuan/uji-v13-tt` | TT dengan `nominal: 50000.5` | DITOLAK | nominal wajib bilangan bulat |
| ★U13 | staf aktif (ben) | create `persetujuan/uji-v13-tt` | TT dengan `nominal: "50000"` (teks) | DITOLAK | nominal wajib angka, bukan teks |
| ★U14 | staf aktif (ben) | create `persetujuan/uji-v13-tt` | TT dengan `olehUid: "uid-lain"` | DITOLAK | penulis bukan yang mengaku |
| ★U15 | staf aktif (ben) | create `persetujuan/uji-v13-ps` | PS dengan `balasan: "Oke"` | DITOLAK | balasan hanya ditulis owner |
| ★U16 | staf aktif (ben) | create `persetujuan/uji-v13-ps` | PS dengan `teks: ""` | DITOLAK | pesan kosong |
| ★U17 | staf aktif (ben) | create `persetujuan/uji-v13-ps` | PS dengan `teks` 501 huruf | DITOLAK | pesan paling panjang 500 huruf |
| ★U18 | staf aktif (ben) | create `persetujuan/uji-v13-ps` | PS dengan `mintaUid: "uid-lain"` | DITOLAK | pesan atas nama akun lain |
| ★U19 | staf aktif (ben) | update `persetujuan/uji-v13-tt` | TT dengan `status: "disetujui"` | DITOLAK | memutus titipan = owner |
| ★U20 | staf aktif (ben) | get `notifOwner/uji-v13-hp` | — | DITOLAK | token HP owner tidak dibaca tablet |
| ★U21 | staf aktif (ben) | create `notifOwner/uji-v13-hp` | HP | DITOLAK | token HP owner tidak ditulis tablet |
| ★U22 | kasir@ | create `persetujuan/uji-v13-tt` | TT | DITOLAK | kasir darurat tidak menitip uang |

Di **v12** kasus ★U2 ★U3 ★U4 ★U5 ★U6 DITOLAK (bloknya / bentuknya belum ada; v13 yang membukanya); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V13** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): ke-22 kasus di
atas atas `firestore.rules` (v13) dan atas `firestore.rules.v12` — yang berbeda wajib persis kasus yang dibuka v13 — plus kontrol (satu suku v13
dirusak → kasus sasarannya wajib berbalik). Semua kasus v12, v11, v10, v9, v8 & v7 lama tetap dijalankan atas v13 dan wajib sama hasilnya.

## Hasil Playground & terbit

Belum — diisi sesudah owner menjalankan Wajib owner dan menekan Publish.
