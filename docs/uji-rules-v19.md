# Uji rules v19 di server — cek mingguan timbangan & gudang dari tablet (DRAF 24 Nov 2026)

v19 = v18 FINAL + **satu fungsi baru dan satu blok baru** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v18`).
Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v18.

## Yang berubah v18 → v19

1. **(v19-1) blok `cekGudang` + fungsi `stafCekGudang(peranBoleh, id)`** — paket KPI laba butir 14, keputusan owner 24 Nov 2026: "Ben juga dari tablet".
   - satu dokumen per cek mingguan (tambah-saja): `{ id, tanggal, jam, minggu, cek: { timbangan, palet, bocor, lembap, kutu }, catatan }` + kolom atribusi penulis;
   - **baca**: owner, Penjaga laci & karyawan (jadwal cek berikutnya tampil di tablet);
   - **buat**: owner, atau Penjaga laci aktif atas namanya sendiri (`olehUid`), kolom `id` = id dokumen, tanggal `YYYY-MM-DD`, kelima hal bernilai benar/salah,
     catatan ≤ 160 huruf, tidak ada kolom lain;
   - **ubah & hapus**: owner saja.

Bukan data toko yang dikunci: tidak ada rupiah, kg, stok, atau tanggal buku. **Terbitkan v19 SEBELUM PR paket KPI laba digabung** — halaman baru mendengar
koleksi `cekGudang` di HP/tablet staf; tanpa v19 pendengarnya ditolak server (aplikasi tetap jalan, tapi Sistem › Perangkat di perangkat itu menyebut
"cekGudang ditolak") dan tombol **Simpan cek** di tablet ditolak. Owner tetap bisa mencatat cek dari HP / Mac.

## Urutan (± 5 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish** — sebelum PR digabung.
4. Sesudah terbit: di tablet (akun Penjaga laci) buka Menu › kartu **Cek mingguan timbangan & gudang**, jawab kelima hal, ketuk **Simpan cek** — kabar "tersimpan" muncul,
   dan di HP owner Menu › Toko ini › Pengingat menampilkan cek berikutnya 7 hari lagi.

## Wajib owner (3 kasus — tanpa dokumen uji staf)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★G1 | owner@ | create `cekGudang/cg-2026-10-09-uji1` | cek atas nama owner | LOLOS | owner mencatat cek |
| 2 | ★G2 | owner@ | get `cekGudang/cg-2026-10-09-uji1` | — | LOLOS | owner membaca |
| 3 | ★G3 | owner@ | delete `cekGudang/cg-2026-10-09-uji1` | — | LOLOS | owner menghapus salah catat |

Untuk ★G2 & ★G3 buat dulu dokumennya lewat ★G1 (Playground tidak menyimpan; jalankan ★G1 sebagai `set` di Data bila ingin menguji get/delete sungguhan, lalu hapus).

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator di bawah
(mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★G4 | Penjaga laci | create `cekGudang/cg-2026-10-09-uji1` | cek atas namanya | LOLOS | tablet mencatat cek |
| ★G5 | Penjaga laci | get `cekGudang/cg-2026-10-09-uji1` | — | LOLOS | tablet melihat cek terakhir |
| ★G6 | karyawan | get `cekGudang/cg-2026-10-09-uji1` | — | LOLOS | jadwal cek tampil |
| ★G7 | karyawan | create `cekGudang/cg-2026-10-09-uji1` | cek | DITOLAK | yang mencatat Penjaga laci (owner 24 Nov) |
| ★G8 | Penjaga laci | create `cekGudang/cg-2026-10-09-uji1` | olehUid akun lain | DITOLAK | atas nama penulisnya |
| ★G9 | Penjaga laci | create `cekGudang/cg-2026-10-09-uji1` | kolom id beda dari id dokumen | DITOLAK | id terikat |
| ★G10 | Penjaga laci | create `cekGudang/cg-2026-10-09-uji1` | + kolom nominal | DITOLAK | kolom dibatasi |
| ★G11 | Penjaga laci | create `cekGudang/cg-2026-10-09-uji1` | + hal "atap" | DITOLAK | lima hal saja |
| ★G12 | Penjaga laci | create `cekGudang/cg-2026-10-09-uji1` | hal bernilai teks "ya" | DITOLAK | benar/salah saja |
| ★G13 | Penjaga laci | create `cekGudang/cg-2026-10-09-uji1` | catatan 161 huruf | DITOLAK | ≤ 160 huruf |
| ★G14 | Penjaga laci | update `cekGudang/cg-2026-10-09-uji1` | catatan diubah | DITOLAK | tambah-saja; ubah = owner |
| ★G15 | Penjaga laci | delete `cekGudang/cg-2026-10-09-uji1` | — | DITOLAK | hapus = owner |
| ★G16 | kasir@ | create `cekGudang/cg-2026-10-09-uji1` | cek | DITOLAK | kasir darurat bukan pencatat cek |
| ★G17 | Penjaga laci nonaktif | create `cekGudang/cg-2026-10-09-uji1` | cek | DITOLAK | akun yang dinonaktifkan owner |
| ★G18 | Penjaga laci | create `cekGudang/cg-2026-10-09-uji1` | tanggal "9 Okt" | DITOLAK | tanggal YYYY-MM-DD |

Di **v18** kasus ★G1–★G6 DITOLAK (koleksi belum punya blok → semua ditolak); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V19** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): ke-18 kasus di
atas atas `firestore.rules` (v19) dan atas `firestore.rules.v18` — yang berbeda wajib persis ★G1–★G6 — plus kontrol (satu suku v19 dirusak → kasus sasarannya
wajib berbalik). Semua kasus v18 sampai v7 lama tetap dijalankan atas v19 dan wajib sama hasilnya.
