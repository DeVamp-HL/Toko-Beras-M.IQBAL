# Uji rules v17 di server — push aplikasi tablet (DRAF 23 Nov 2026)

v17 = v16 FINAL + **satu fungsi baru dan satu blok baru** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v16`).
Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v16.

## Yang berubah v16 → v17

1. **(v17-1) blok `notifPerangkat`** — token push Android aplikasi tablet (owner 23 Nov 2026: "Push penuh lewat Google"). Satu dokumen per akun ×
   perangkat, id = uid penulis + `_` + `perangkatId`. **create / update**: owner, atau `stafTokenPush(['ben', 'karyawan'], id)` — akun staf aktif menulis
   dokumennya SENDIRI (uid & olehUid = penulis), kolom hanya `id, uid, olehUid, perangkatId, token, platform, perangkat, pada`, platform `android`, token
   ≤ 4096 huruf (token kosong = notifikasi dimatikan). **read & delete**: owner saja. Fungsi server `kabarTablet` membacanya lewat Admin SDK untuk
   mengirim jawaban owner (disetujui / ditolak / dibaca + balasan) ke akun yang meminta.

Bukan data toko: tidak ada uang, stok, tanggal buku, atau kunci periode yang tersentuh. Kasir@ dan akun nonaktif = ditolak.

## Urutan (± 10 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus, akun owner). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish**.
4. Sesudah itu baru tombol **Nyalakan notifikasi tablet** di tablet bisa menyimpan token (tanpa v17: "Notifikasi tablet BELUM menyala: …permission…").
   Halaman boleh digabung lebih dulu — tidak ada yang rusak, tombolnya saja yang ditolak server.
5. Sesudah merge: owner memasang ulang fungsi server sekali di Cloud Shell (`cd Toko-Beras-M.IQBAL && git pull && bash functions/pasang.sh`) supaya
   fungsi baru `kabarTablet` terpasang. Langkah lengkap: `docs/notifikasi-tablet.md`.

## Wajib owner (3 kasus — akun owner, tanpa dokumen uji)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★Z1 | owner@ | create `notifPerangkat/uid-uji_p-uji-1` | token android atas nama owner | LOLOS | owner boleh menulis token |
| 2 | ★Z2 | owner@ | get `notifPerangkat/uid-uji-b_p-uji-1` | — | LOLOS | owner boleh membaca token |
| 3 | ★Z3 | owner@ | delete `notifPerangkat/uid-uji-b_p-uji-1` | — | LOLOS | owner boleh membuang token |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator di bawah
(mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★Z4 | Penjaga laci | create `notifPerangkat/uid-uji-b_p-uji-1` | token android atas namanya | LOLOS | tablet menyalakan notifikasi |
| ★Z5 | Penjaga laci | update `notifPerangkat/uid-uji-b_p-uji-1` | token dikosongkan | LOLOS | tablet mematikan notifikasi |
| ★Z6 | karyawan | create `notifPerangkat/uid-uji-b_p-uji-1` | token atas namanya | LOLOS | akun karyawan di aplikasi tablet |
| ★Z7 | Penjaga laci | create `notifPerangkat/uid-uji-b_p-uji-1` | kolom uid = akun lain | DITOLAK | token = milik penulis |
| ★Z8 | Penjaga laci | create `notifPerangkat/uid-lain_p-uji-1` | id bukan uid penulis | DITOLAK | id = uid + perangkat |
| ★Z9 | Penjaga laci | create `notifPerangkat/uid-uji-b_p-uji-1` | membawa kolom nominal | DITOLAK | kolom dibatasi |
| ★Z10 | Penjaga laci | create `notifPerangkat/uid-uji-b_p-uji-1` | platform web | DITOLAK | koleksi ini untuk aplikasi tablet |
| ★Z11 | Penjaga laci | get `notifPerangkat/uid-uji-b_p-uji-1` | — | DITOLAK | token dibaca server saja |
| ★Z12 | Penjaga laci | delete `notifPerangkat/uid-uji-b_p-uji-1` | — | DITOLAK | bukan-owner tidak menghapus |
| ★Z13 | kasir@ | create `notifPerangkat/uid-uji-b_p-uji-1` | token | DITOLAK | kasir darurat tanpa push |
| ★Z14 | Penjaga laci nonaktif | create `notifPerangkat/uid-uji-b_p-uji-1` | token | DITOLAK | akun yang dinonaktifkan owner |
| ★Z15 | Penjaga laci | create `notifPerangkat/uid-uji-b_p-uji-1` | tanpa olehUid | DITOLAK | penulis tercatat |

Di **v16** kasus ★Z1–★Z6 DITOLAK (koleksi baru — v17 yang membukanya); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V17** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): ke-15 kasus di
atas atas `firestore.rules` (v17) dan atas `firestore.rules.v16` — yang berbeda wajib persis kasus yang dibuka v17 — plus kontrol (satu suku v17 dirusak →
kasus sasarannya wajib berbalik). Semua kasus v16 sampai v7 lama tetap dijalankan atas v17 dan wajib sama hasilnya.
