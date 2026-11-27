# Uji rules v24 di server — janji datang pemasok dari tablet (DRAF 27 Nov 2026)

v24 = v23 FINAL + **satu fungsi baru (`stafJanjiPemasok`) dan blok `pesananPemasok` yang dipecah** (berkas kanonik `firestore.rules`; pembanding
`firestore.rules.v23`). Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v23.

## Yang berubah v23 → v24

1. **(v24-1) `pesananPemasok` read: + Penjaga laci** — paket tanggal janji, keputusan owner 27 Nov 2026: "Owner + Penjaga laci dari tablet". Tablet (akun Penjaga laci)
   menampilkan pesanan ke pemasok yang masih menunggu datang di Barang masuk — pemasok, isi karung, tanggal pesan, janji datang. Karyawan TIDAK membacanya.
   Buat & hapus pesanan TETAP owner saja (Harga › Belanja).
2. **(v24-2) `pesananPemasok` update: + `stafJanjiPemasok(['ben'])`** — Penjaga laci mengisi / menggeser **janji datang** pesanan yang masih menunggu
   (status tersimpan `menunggu`), atas nama pengubahnya (`diubahOlehUid`): hanya kolom `janjiTanggal` (`YYYY-MM-DD`) dan `janjiRiwayat` (daftar, paling banyak
   30 baris) + kolom atribusi. Isi pesanan, jumlah karung, status, dan rupiah tidak bisa diubah dari tablet.

Bukan data uang / stok: janji datang tidak mengubah bon, kas, stok, atau laba. **Terbitkan v24 SEBELUM PR paket tanggal janji digabung** — tanpa v24 pendengar
`pesananPemasok` di tablet Penjaga laci ditolak server (tercatat di Sistem › Perangkat) dan janji datang dari tablet DITOLAK; Belanja owner (termasuk isi
janji dari HP / Mac), isian "dijanjikan sampai" di Bayar › Antar, tanggal kirim pesanan, dan hitungan tepat janji tetap jalan.

## Urutan (± 5 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish** — sebelum PR digabung.
4. Sesudah terbit dan PR digabung: di HP owner buka Harga › Belanja, kirim satu pesanan dengan janji "besok"; di tablet (akun Penjaga laci) buka Stok › Barang
   masuk — pesanan itu tampil di "Pesanan ke pemasok yang menunggu" dengan janjinya; geser ke "lusa", simpan; di HP owner pesanan itu tertulis "digeser".

## Wajib owner (3 kasus — tanpa dokumen uji staf)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★I1 | owner@ | create `pesananPemasok/1796090000000.5` | pesanan contoh 10 karung | LOLOS | owner mencatat pesanan ke pemasok |
| 2 | ★I2 | owner@ | get `pesananPemasok/1796090000000.5` | — | LOLOS | owner membaca pesanan |
| 3 | ★I3 | owner@ | update `pesananPemasok/1796090000000.5` | janjiTanggal 2026-12-03 + janjiRiwayat | LOLOS | owner mengisi janji datang |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator di bawah
(mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★I4 | Penjaga laci | get `pesananPemasok/1796090000000.5` | — | LOLOS | tablet melihat pesanan yang menunggu |
| ★I5 | Penjaga laci | update `pesananPemasok/1796090000000.5` | janji pertama atas namanya | LOLOS | Penjaga laci mengisi janji dari tablet |
| ★I6 | Penjaga laci | update `pesananPemasok/1796090000000.5` | janji 3 → 5 Des | LOLOS | Penjaga laci menggeser janji |
| ★I7 | karyawan | get `pesananPemasok/1796090000000.5` | — | DITOLAK | pesanan pemasok = Penjaga laci saja |
| ★I8 | karyawan | update `pesananPemasok/1796090000000.5` | janji | DITOLAK | janji = Penjaga laci saja |
| ★I9 | Penjaga laci | update `pesananPemasok/1796090000000.5` | karung 10 → 12 | DITOLAK | isi pesanan = owner |
| ★I10 | Penjaga laci | update `pesananPemasok/1796090000000.5` | status batal | DITOLAK | membatalkan = owner |
| ★I11 | Penjaga laci | update `pesananPemasok/1796090000000.5` | janji pesanan yang sudah batal | DITOLAK | hanya pesanan yang menunggu |
| ★I12 | Penjaga laci | update `pesananPemasok/1796090000000.5` | janji '3 Des' | DITOLAK | tanggal YYYY-MM-DD |
| ★I13 | Penjaga laci | update `pesananPemasok/1796090000000.5` | diubahOlehUid orang lain | DITOLAK | atas nama pengubahnya |
| ★I14 | Penjaga laci | update `pesananPemasok/1796090000000.5` | riwayat bukan daftar | DITOLAK | bentuk riwayat tetap |
| ★I15 | Penjaga laci | update `pesananPemasok/1796090000000.5` | riwayat 31 baris | DITOLAK | paling banyak 30 baris |
| ★I16 | Penjaga laci | create `pesananPemasok/1796090000000.5` | pesanan baru | DITOLAK | membuat pesanan = owner |
| ★I17 | Penjaga laci | delete `pesananPemasok/1796090000000.5` | — | DITOLAK | hapus = owner |
| ★I18 | kasir@ | get `pesananPemasok/1796090000000.5` | — | DITOLAK | kasir darurat tidak membaca pesanan |
| ★I19 | Penjaga laci nonaktif | update `pesananPemasok/1796090000000.5` | janji | DITOLAK | akun yang dinonaktifkan owner |

Di **v23** kasus ★I4, ★I5, ★I6 DITOLAK (pesananPemasok owner saja); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V24** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): kesembilan belas kasus
di atas atas `firestore.rules` (v24) dan atas `firestore.rules.v23` — yang berbeda wajib persis ★I4, ★I5, ★I6 — plus kontrol (ubahan v24 dirusak → kasus
sasarannya wajib berbalik). Semua kasus v23 sampai v7 lama tetap dijalankan atas v24 dan wajib sama hasilnya.

## Hasil Playground & terbit

**v24 TERBIT 27 Nov 2026 ±05.35 WIB.** Owner menempel isi `firestore.rules` (commit `e2bc820`, berkas mentah GitHub di tab Chrome Claude — sidiknya dicek lebih
dulu = repo) ke editor Rules Console. Isi editor sebelum Publish dan isi yang aktif sesudah halaman dimuat ulang sama persis dengan `firestore.rules` cabang ini:
SHA-256 berawalan `d7e257189bce8abf`, 88.131 byte, baris 2 `ATURAN FIRESTORE v24 FINAL` (sebelumnya aktif v23 `a0dbb75b`, 85.924 byte).
Playground (akun uji owner: UID `uid-uji`, email `owner@tokoberasmiqbal.web.app`): ★I2 get `pesananPemasok/1796090000000.5` → *Simulated read allowed* ·
★I1 create (dokumen contoh `status` menunggu) → *Simulated write allowed* · ★I3 update (`janjiTanggal` 2026-12-03) → *Simulated write allowed* — ketiganya
sesuai kolom Wajib. Kasus staf (★I4–★I19) dibuktikan emulator CI bagian V24.
