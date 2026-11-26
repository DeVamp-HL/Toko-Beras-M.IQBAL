# Uji rules v23 di server — karcis ambil nanti & cek bon dari HP (DRAF 26 Nov 2026)

v23 = v22 FINAL + **satu fungsi baru (`stafAmbilBarang`) dan dua blok baru (`ambilBarang`, `bonPublik`)** (berkas kanonik `firestore.rules`; pembanding
`firestore.rules.v22`). Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v22.

## Yang berubah v22 → v23

1. **(v23-1) blok `ambilBarang`** — karcis ambil nanti, keputusan owner 26 Nov 2026: "stok berkurang saat bayar + daftar titipan", boleh diambil sebagian.
   Catatan tambah-saja `titip` (barang nota yang ditinggal di toko, ditulis bersama notanya) dan `ambil` (barang yang diserahkan):
   - read: owner, Penjaga laci, karyawan;
   - create: owner, atau Penjaga laci / karyawan atas nama penulisnya (`olehUid`) dengan bentuk tetap — `id` = id dokumen, tanggal `YYYY-MM-DD`, `jenis`
     `titip` atau `ambil`, `trxId` nota 1–60 huruf, `isi` daftar 1–20 baris, catatan ≤ 160 huruf, kolom dibatasi;
   - ubah & hapus: owner saja.
2. **(v23-2) blok `bonPublik`** — cek sisa bon dari HP pelanggan (owner 26 Nov 2026: "bangun bareng"). Satu dokumen ringkas per pelanggan bernama **kode acak**
   (22 huruf); isinya salinan nama panggilan, sisa bon, nota terbuka, jam diperbarui:
   - get: **siapa pun yang tahu kodenya, tanpa login** (halaman `baru/bon.html`), asal kodenya ≥ 20 huruf;
   - list: owner saja — tidak ada yang bisa menelusuri kode orang lain;
   - tulis & hapus (cabut tautan): owner saja.

Tidak ada rupiah toko yang bisa diubah dari luar: stok & uang titipan tetap di nota (penjualan), dan ringkasan bon hanya ditulis HP/Mac owner. **Terbitkan v23
SEBELUM PR paket QR kedua digabung** — tanpa v23 pendengar `ambilBarang` di tablet ditolak server (tercatat di Sistem › Perangkat), titipan & cek bon dari HP
tidak bisa dipakai; layar lain tetap jalan.

## Urutan (± 5 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (empat kasus). ★C4 = matikan **Authenticated** (tamu tanpa login). Hasilnya harus sama
   dengan kolom Wajib.
3. Klik **Publish** — sebelum PR digabung.
4. Sesudah terbit dan PR digabung: di tablet Jual › Bayar nyalakan **Diambil nanti**, catat nota karung; scan struknya → **Serahkan barang titipan**. Di HP owner
   Pelanggan › Bon › orang ber-bon → **Buat tautan cek bon**, buka tautannya di HP lain (tanpa login) — sisa bonnya tampil.

## Wajib owner (4 kasus — tanpa dokumen uji staf)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★C1 | owner@ | create `ambilBarang/ab-2026-12-01-uji1` | titipan 3 karung | LOLOS | owner mencatat titipan |
| 2 | ★C2 | owner@ | get `ambilBarang/ab-2026-12-01-uji1` | — | LOLOS | owner membaca catatan ambil barang |
| 3 | ★C3 | owner@ | create `bonPublik/Kb7Qp2Xz9LmN4rT8vW1yZa` | ringkasan bon contoh | LOLOS | owner menulis ringkasan cek bon |
| 4 | ★C4 | tamu (Authenticated mati) | get `bonPublik/Kb7Qp2Xz9LmN4rT8vW1yZa` | — | LOLOS | pelanggan membuka cek bon tanpa login |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator di bawah
(mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★C5 | Penjaga laci | create `ambilBarang/ab-2026-12-01-uji1` | titipan atas namanya | LOLOS | nota titip dari tablet |
| ★C6 | Penjaga laci | create `ambilBarang/ab-2026-12-01-uji1` | barang diambil | LOLOS | menyerahkan barang dari tablet |
| ★C7 | karyawan | create `ambilBarang/ab-2026-12-01-uji1` | barang diambil | LOLOS | karyawan ikut menyerahkan |
| ★C8 | Penjaga laci | get `ambilBarang/ab-2026-12-01-uji1` | — | LOLOS | tablet membaca daftar titipan |
| ★C9 | Penjaga laci | create `ambilBarang/ab-2026-12-01-uji1` | olehUid orang lain | DITOLAK | atas nama penulisnya |
| ★C10 | Penjaga laci | create `ambilBarang/ab-2026-12-01-uji1` | id ab-lain | DITOLAK | id = id dokumen |
| ★C11 | Penjaga laci | create `ambilBarang/ab-2026-12-01-uji1` | jenis 'batal' | DITOLAK | hanya titip / ambil |
| ★C12 | Penjaga laci | create `ambilBarang/ab-2026-12-01-uji1` | + hargaTotal | DITOLAK | kolom dibatasi, tanpa rupiah |
| ★C13 | Penjaga laci | create `ambilBarang/ab-2026-12-01-uji1` | isi kosong | DITOLAK | minimal satu barang |
| ★C14 | Penjaga laci | update `ambilBarang/ab-2026-12-01-uji1` | catatan diubah | DITOLAK | ubah = owner |
| ★C15 | Penjaga laci | delete `ambilBarang/ab-2026-12-01-uji1` | — | DITOLAK | hapus = owner |
| ★C16 | kasir@ | create `ambilBarang/ab-2026-12-01-uji1` | titipan | DITOLAK | kasir darurat tidak mencatat titipan |
| ★C17 | Penjaga laci nonaktif | create `ambilBarang/ab-2026-12-01-uji1` | titipan | DITOLAK | akun yang dinonaktifkan owner |
| ★C18 | tamu | list `bonPublik` | — | DITOLAK | tidak ada yang bisa menelusuri kode |
| ★C19 | tamu | create `bonPublik/Kb7Qp2Xz9LmN4rT8vW1yZa` | ringkasan | DITOLAK | ringkasan ditulis owner |
| ★C20 | Penjaga laci | create `bonPublik/Kb7Qp2Xz9LmN4rT8vW1yZa` | ringkasan | DITOLAK | ringkasan ditulis owner |
| ★C21 | Penjaga laci | list `bonPublik` | — | DITOLAK | daftar kode = owner saja |
| ★C22 | tamu | get `bonPublik/abc123` | — | DITOLAK | kode pendek (tebakan) ditolak |
| ★C23 | tamu | get `ambilBarang/ab-2026-12-01-uji1` | — | DITOLAK | catatan toko butuh login |
| ★C24 | owner@ | list `bonPublik` | — | LOLOS | owner melihat semua tautan cek bon |

Di **v22** kasus ★C1, ★C2, ★C3, ★C4, ★C5, ★C6, ★C7, ★C8, ★C24 DITOLAK (kedua koleksi belum ada); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V23** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): kedua puluh empat kasus
di atas atas `firestore.rules` (v23) dan atas `firestore.rules.v22` — yang berbeda wajib persis ★C1–★C8 dan ★C24 — plus kontrol (ubahan v23 dirusak → kasus
sasarannya wajib berbalik). Semua kasus v22 sampai v7 lama tetap dijalankan atas v23 dan wajib sama hasilnya.

## Hasil Playground & terbit

Belum — diisi sesudah owner menjalankan Wajib owner dan menerbitkan.
