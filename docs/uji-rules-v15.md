# Uji rules v15 di server — barang masuk & bayar supir dari tablet (DRAF 22 Nov 2026)

v15 = v14 FINAL + **dua fungsi baru, satu ubahan fungsi, dan dua baris tulis** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v14`).
Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v14.

## Yang berubah v14 → v15

1. **(v15-1) `batchMasuk` create + `stafCatatMasuk(['ben'])`** — kedatangan dari tablet oleh Penjaga laci: bertanda `dariTablet`, `caraBayar` **'utang'**
   (langsung jadi bon pemasok), `biayaBongkar` **0**, pemasok 1–60 huruf (bukan `LAHIR BUKU`), 1–20 baris barang, tanpa kolom buku baru / stok awal /
   tutup buku / koreksi owner (`riwayat`, `alasanKoreksi`, `noBon`, `bongkarTitipan`); bulan tidak terkunci (`tglStaf`). Ubah & hapus kedatangan tetap owner.
2. **(v15-2) `stafMintaKeluar`**: jenis titipan + **`bongkar`** (wajib `batchId` = kedatangannya) dan **`bayarBon`** (wajib nama pemasok). Uang ke kuli & supir
   dari laci tetap TITIPAN: owner yang menulis upah bongkar ke kedatangan / pembayaran bon (memilih bonnya) saat menyetujui.
3. **(v15-3) `persetujuan` create + `stafKabarMasuk(['ben'])`** — kabar barang masuk untuk owner (tindakan `barangMasuk`, menunjuk kedatangannya, tanpa keputusan).

Karyawan, kasir@, dan akun nonaktif = sama dengan v14 (ditolak). Tulis uang (pengeluaran, kasbon, bayar bon) tetap owner saja.

## Urutan (± 10 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus, akun owner). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish**.
4. Baru sesudah itu cabangnya digabung (merge). Kalau dibalik, kedatangan dari tablet ditolak server ("ditolak server" di Perangkat & antrean) — tidak ada yang
   rusak, kedatangan itu saja yang belum tercatat.
5. Sesudah merge: owner menjalankan ulang pemasangan fungsi notifikasi sekali di Cloud Shell (`cd Toko-Beras-M.IQBAL && git pull && bash functions/pasang.sh`)
   supaya notifikasi HP menyebut "Upah bongkar" / "Bayar bon pemasok" / "Barang masuk" — tanpa itu notifikasinya tetap datang, judulnya saja yang umum.

## Wajib owner (3 kasus — akun owner, tanpa dokumen uji)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★X1 | owner@ | create `batchMasuk/uji-v15-bo` | kedatangan tunai + upah bongkar | LOLOS | owner tetap mencatat kedatangan biasa |
| 2 | ★X2 | owner@ | update `persetujuan/uji-v15-ts` | titipan bayar supir → disetujui | LOLOS | owner memutus titipan barang masuk |
| 3 | ★X3 | owner@ | create `utangPemasokMutasi/uji-v15-up` | bayar bon dari laci (dari titipan) | LOLOS | owner menulis pembayaran bon saat menyetujui |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator di bawah
(mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★X4 | Penjaga laci | create `batchMasuk/uji-v15-bm` | kedatangan tablet (bon, bongkar 0) | LOLOS | barang masuk dari tablet |
| ★X5 | Penjaga laci | create `persetujuan/uji-v15-tb` | titipan upah bongkar + batchId | LOLOS | bongkar dari laci = titipan |
| ★X6 | Penjaga laci | create `persetujuan/uji-v15-ts` | titipan bayar supir + pemasok | LOLOS | bayar supir dari laci = titipan |
| ★X7 | Penjaga laci | create `persetujuan/uji-v15-kb` | kabar barang masuk | LOLOS | owner dikabari |
| ★X8 | karyawan | create `batchMasuk/uji-v15-bm` | kedatangan tablet | DITOLAK | pencatat = Penjaga laci saja |
| ★X9 | Penjaga laci | create `batchMasuk/uji-v15-bm` | caraBayar tunai | DITOLAK | tablet selalu bon |
| ★X10 | Penjaga laci | create `batchMasuk/uji-v15-bm` | biayaBongkar 50.000 | DITOLAK | bongkar lewat titipan |
| ★X11 | Penjaga laci | create `batchMasuk/uji-v15-bm` | tanpa dariTablet | DITOLAK | bentuk tablet wajib bertanda |
| ★X12 | Penjaga laci | create `batchMasuk/uji-v15-bm` | pemasok LAHIR BUKU | DITOLAK | nama sistem bukan pemasok |
| ★X13 | Penjaga laci | create `batchMasuk/uji-v15-bm` | tanpa baris barang | DITOLAK | kedatangan wajib berisi |
| ★X14 | Penjaga laci | create `batchMasuk/uji-v15-bm` | membawa `riwayat` | DITOLAK | kolom koreksi = owner |
| ★X15 | Penjaga laci | create `batchMasuk/uji-v15-bm` | tanggal bulan lewat tenggang | DITOLAK | bulan lama = owner |
| ★X16 | Penjaga laci | update `batchMasuk/uji-v15-bm` | menulis upah bongkar sendiri | DITOLAK | ubah kedatangan = owner |
| ★X17 | Penjaga laci | create `persetujuan/uji-v15-tb` | titipan bongkar tanpa batchId | DITOLAK | bongkar wajib menunjuk kedatangan |
| ★X18 | Penjaga laci | create `persetujuan/uji-v15-ts` | bayar supir tanpa pemasok | DITOLAK | bayar bon wajib bernama pemasok |
| ★X19 | Penjaga laci | create `persetujuan/uji-v15-kb` | kabar tanpa batchId | DITOLAK | kabar wajib menunjuk kedatangan |
| ★X20 | Penjaga laci | create `persetujuan/uji-v15-kb` | kabar sudah diputus | DITOLAK | keputusan = owner |
| ★X21 | Penjaga laci | create `utangPemasokMutasi/uji-v15-up` | bayar bon sendiri | DITOLAK | uang ditulis owner |
| ★X22 | kasir@ | create `batchMasuk/uji-v15-bm` | kedatangan | DITOLAK | kasir darurat tidak mencatat stok |
| ★X23 | karyawan | create `persetujuan/uji-v15-kb` | kabar barang masuk | DITOLAK | kabar = Penjaga laci saja |

Di **v14** kasus ★X4–★X7 DITOLAK (v15 yang membukanya); kasus lain sama hasilnya.

## Hasil Playground & terbit (22 Nov 2026)

- Isi editor Console sebelum uji = `firestore.rules` cabang ini (commit 40b10a0) tanpa baris kosong terakhir: SHA-256 berawalan `b3c512c8`, 69.344
  byte (berkas `9b212638`, 69.345 byte; satu-satunya beda = `\n` penutup yang hilang saat disalin dari halaman teks mentah GitHub — tidak mengubah
  aturan). Dibaca lewat JS dari editor; sebelumnya v14 aktif (`21cf7899`). Dicek ulang sesudah ★X3 — tetap sama.
- Wajib owner, akun owner (`uid-uji`, provider bawaan Playground google.com, email owner di payload), tanggal dokumen `2026-11-22` (= jam simulasi):
  ★X1 create `batchMasuk/uji-v15-bo` {tanggal, caraBayar `tunai`, biayaBongkar 50000 (int64)} → "Simulated write allowed" (LOLOS, sesuai);
  ★X2 update `persetujuan/uji-v15-ts` {status `disetujui`, jenis `bayarBon`, tindakan `uangKeluar`} → "Simulated write allowed" (LOLOS, sesuai);
  ★X3 create `utangPemasokMutasi/uji-v15-up` {tanggal, tipe `bayar`, dari `laci`} → "Simulated write allowed" (LOLOS, sesuai). Spanduk hasil ditutup
  dulu sebelum kasus berikutnya dijalankan.
- Kasus staf (Penjaga laci / karyawan / kasir@, bentuk kedatangan tablet, titipan bongkar & bayar supir, kabar) dibuktikan emulator: job `rules` di PR
  hijau sebelum terbit.
- Owner klik **Publish** 22 Nov 2026 ±05.30 WIB (riwayat Console "Today • 5:30 AM"; sebelumnya v14 "Today • 12:30 AM"). Sesudah halaman dimuat ulang,
  aturan yang berlaku = isi di atas (sidik `b3c512c8`, baris 2 `ATURAN FIRESTORE v15 FINAL`, tanpa draf tertunda).
- Urutan terhadap CI: saat Publish, job `rules` (emulator) sudah hijau pada commit 40b10a0; `uji`, `uji-peramban`, `gladi` masih berjalan (syarat merge).

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V15** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): ke-23 kasus di
atas atas `firestore.rules` (v15) dan atas `firestore.rules.v14` — yang berbeda wajib persis kasus yang dibuka v15 — plus kontrol (satu suku v15 dirusak →
kasus sasarannya wajib berbalik). Semua kasus v14, v13, v12, v11, v10, v9, v8 & v7 lama tetap dijalankan atas v15 dan wajib sama hasilnya.
