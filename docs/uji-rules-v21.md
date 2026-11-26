# Uji rules v21 di server — usul harga banding dari tablet (DRAF 26 Nov 2026)

v21 = v20 FINAL + **satu fungsi baru (`stafUsulBanding`) dan satu sambungan di baris create `persetujuan`** (berkas kanonik `firestore.rules`; pembanding
`firestore.rules.v20`). Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v20.

## Yang berubah v20 → v21

1. **(v21-1) `persetujuan` create: + `stafUsulBanding(['ben'])`** — paket Banding pemasok, keputusan owner 26 Nov 2026: "Owner + Ben lewat usul".
   - Penjaga laci mengetik di tablet harga yang ditawarkan pemasok (tidak / belum dibeli) atau harga acuan resmi (Panel Harga Bapanas, PIHPS BI, BPS);
   - yang terkirim SATU dokumen `persetujuan` bertindakan `hargaBanding`, status `menunggu`, atas nama penulisnya (`mintaUid`), jenis `tawaran` | `acuan`,
     harga per kg rupiah bulat Rp1.000–Rp100.000, kalimat 1–300 huruf, tanpa kolom keputusan;
   - **catatan bandingnya** (`aturanToko/banding-YYYY-MM`) ditulis **owner** saat menyetujui di Menu › Toko ini › Peran & persetujuan › Persetujuan — baris tulis
     `aturanToko` TIDAK berubah (owner saja). Tablet tidak membaca catatan banding toko.

Bukan data uang / stok: tidak ada uang keluar, kg buku, atau tanggal buku. **Terbitkan v21 SEBELUM PR Banding pemasok digabung** — tanpa v21 kartu "Harga dari
pemasok lain" di tablet ditolak server saat mengirim (kiriman tercatat DITOLAK di Sistem › Perangkat); layar owner (catat langsung, banding, rapor) tetap jalan.

## Urutan (± 5 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish** — sebelum PR digabung.
4. Sesudah terbit dan PR digabung: di tablet (akun Penjaga laci) buka Menu › kartu **Harga dari pemasok lain**, kirim satu usul; di HP owner buka Menu › Peran &
   persetujuan › Persetujuan → Setujui — usul itu tampil di Harga & Pemasok › Banding pemasok › Minggu ini.

## Wajib owner (3 kasus — tanpa dokumen uji staf)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★E1 | owner@ | create `aturanToko/banding-2026-10` | satu entri tawaran | LOLOS | owner mencatat harga tawaran |
| 2 | ★E2 | owner@ | update `persetujuan/uji-v21-ub` | status disetujui | LOLOS | owner menyetujui usul tablet |
| 3 | ★E3 | owner@ | get `aturanToko/banding-2026-10` | — | LOLOS | owner membaca catatan banding |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator di bawah
(mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★E4 | Penjaga laci | create `persetujuan/uji-v21-ub` | usul tawaran Rp12.900/kg | LOLOS | tablet mengusulkan harga tawaran |
| ★E5 | Penjaga laci | create `persetujuan/uji-v21-ub` | usul acuan Rp13.100/kg | LOLOS | tablet mengusulkan harga acuan |
| ★E6 | karyawan | create `persetujuan/uji-v21-ub` | usul tawaran | DITOLAK | usul = Penjaga laci saja |
| ★E7 | Penjaga laci | create `persetujuan/uji-v21-ub` | harga 12.900,5 | DITOLAK | rupiah bulat |
| ★E8 | Penjaga laci | create `persetujuan/uji-v21-ub` | harga 999 | DITOLAK | di bawah Rp1.000/kg |
| ★E9 | Penjaga laci | create `persetujuan/uji-v21-ub` | harga 645.000 | DITOLAK | harga karung, bukan per kg |
| ★E10 | Penjaga laci | create `persetujuan/uji-v21-ub` | jenis 'jual' | DITOLAK | jenis hanya tawaran / acuan |
| ★E11 | Penjaga laci | create `persetujuan/uji-v21-ub` | kalimat kosong | DITOLAK | owner wajib bisa membaca usulnya |
| ★E12 | Penjaga laci | create `persetujuan/uji-v21-ub` | kalimat 301 huruf | DITOLAK | paling banyak 300 huruf |
| ★E13 | Penjaga laci | create `persetujuan/uji-v21-ub` | mintaUid orang lain | DITOLAK | atas nama penulisnya |
| ★E14 | Penjaga laci | create `persetujuan/uji-v21-ub` | status disetujui | DITOLAK | tablet tidak memutus |
| ★E15 | Penjaga laci | update `persetujuan/uji-v21-ub` | status disetujui | DITOLAK | memutus = owner |
| ★E16 | Penjaga laci | create `aturanToko/banding-2026-10` | catatan banding | DITOLAK | catatan ditulis owner |
| ★E17 | Penjaga laci | get `aturanToko/banding-2026-10` | — | DITOLAK | catatan banding tidak dibaca tablet |
| ★E18 | kasir@ | create `persetujuan/uji-v21-ub` | usul tawaran | DITOLAK | kasir darurat tidak mengusulkan |
| ★E19 | Penjaga laci nonaktif | create `persetujuan/uji-v21-ub` | usul tawaran | DITOLAK | akun yang dinonaktifkan owner |

Di **v20** kasus ★E4 & ★E5 DITOLAK (bentuk usul banding belum dibuka); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V21** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): kesembilan belas kasus
di atas atas `firestore.rules` (v21) dan atas `firestore.rules.v20` — yang berbeda wajib persis ★E4 & ★E5 — plus kontrol (ubahan v21 dirusak → kasus
sasarannya wajib berbalik). Semua kasus v20 sampai v7 lama tetap dijalankan atas v21 dan wajib sama hasilnya.

## Hasil Playground & terbit

**v21 TERBIT 26 Nov 2026 07.56 WIB** (riwayat Console "Today • 7:56 AM"). Isi editor sebelum Publish dan isi yang terbit sesudah halaman dimuat ulang sama
persis dengan `firestore.rules` cabang ini: SHA-256 berawalan `2d076497ff87cf6a`, 80.082 byte, baris 2 `ATURAN FIRESTORE v21 FINAL`.
Playground (akun uji owner: UID `uid-uji`, email `owner@tokoberasmiqbal.web.app`): ★E3 get → *Simulated read allowed* · ★E1 create (id, bulan) →
*Simulated write allowed* · ★E2 update (status disetujui) → *Simulated write allowed* — ketiganya sesuai kolom Wajib.
