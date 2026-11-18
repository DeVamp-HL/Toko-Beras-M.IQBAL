# Uji rules v11 di server — B4 pesanan, PO & order rutin (TERBIT 18 Nov 2026 ±12.38 WIB)

v11 = v10 FINAL + **tiga ubahan & tiga fungsinya** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v10`). Tidak ada yang lain berubah —
`alat-uji/periksa_rules.py` mencabut balik ketiga ubahan & ketiga fungsi itu lalu membandingkan sisanya huruf demi huruf dengan v10.

## Yang berubah v10 → v11 (tiga)

1. **(v11-1) Pesanan dibuat dari tablet** (`pesanan` create): owner atau **ben** (`stafBuatPesanan`) — atas nama penulisnya, status `dipesan`, belum
   bernota (`trxIdJual` kosong), tanpa kolom batal. Dulu (v1–v10) pesanan hanya bisa dibuat akun owner, jadi tablet kasir (akun peran Ben) ditolak.
2. **(v11-2) Pesanan diubah Ben** (`pesanan` update): + `stafAturPesanan` — Ben mengubah isi, nomor PO, tanggal kirim, alamat, catatan; menandai
   **diantar**; atau **membatalkan** pesanan yang belum jadi nota (status `dipesan` / `diantar` → `dipesan` / `diantar` / `batal`). Kolom yang boleh berubah
   dibatasi (nama pemesan, nota, pembuat tidak bisa diubah). Jadi nota tetap `stafUbahPesanan` (ben & karyawan) seperti sejak v1. **Uang muka** dicatat
   sebagai pelunasan piutang (`piutangMutasi` bayar) yang sudah terbuka untuk ben & karyawan sejak v3 — rules uang tidak berubah.
3. **(v11-3) Jadwal order rutin** (`orderRutin`, koleksi baru): dibaca owner, ben, karyawan (tablet menampilkan pengingat); dibuat owner atau **ben**
   atas nama sendiri; diubah owner atau ben (`stafUbahRutin`, kolom dibatasi — pembuat tidak bisa diganti); hapus owner.

## Urutan (± 10 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus, akun owner). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish**.
4. Baru sesudah itu cabang B4 digabung (merge). **Jangan dibalik**: kalau aplikasi baru tayang sebelum v11 terbit, pesanan yang dibuat / diubah dari
   tablet ditolak server dan jadwal order rutin tidak bisa disimpan. Jual biasa, antar, dan uang muka tetap jalan.

## Wajib owner (3 kasus — akun owner, tanpa dokumen uji)

Isi "PS": `{ id: "uji-v11-ps", tanggal: "2026-10-09", jam: "10:00", namaPelanggan: "Contoh", isi: "1 karung Uji 50 kg", alamat: "uji", nilaiPerkiraan: 0, status: "dipesan", riwayatStatus: [], noPO: "PO-UJI", tanggalKirim: "", catatan: "", olehUid: "uid-uji-b" }`.
Isi "RUTIN": `{ id: "uji-v11-rutin", namaPelanggan: "Contoh", isi: "1 karung Uji 50 kg", alamat: "uji", noPO: "", catatan: "", ulang: "mingguan", hari: 1, mulai: "2026-10-09", aktif: true, lewati: [], dibuatTanggal: "2026-10-09", olehUid: "uid-uji-b" }`.
Angka (`nilaiPerkiraan`, `hari`) diisi jenis **int64**; `riwayatStatus` & `lewati` = array kosong; `aktif` = boolean.

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★M2 | owner@ | create `pesanan/uji-v11-ps` | PS | LOLOS | owner selalu boleh membuat pesanan |
| 2 | ★M3 | owner@ | create `orderRutin/uji-v11-rutin` | RUTIN | LOLOS | blok baru v11 — owner membuat jadwal rutin |
| 3 | ★M4 | owner@ | update `pesanan/uji-v11-ps` | PS dengan `status: "batal"`, `alasanBatal: "uji"` | LOLOS | owner membatalkan pesanan |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben; ★M8 ★M9 ★M17 ★M21 ★M23 memakai peran
**karyawan**) dan dokumen `pesanan/uji-v11-ps` = PS / `orderRutin/uji-v11-rutin` = RUTIN untuk kasus update / baca / hapus. Tanpa itu cukup percaya bukti
emulator di bawah (mesin rules yang sama dengan server). "UBAH" = `isi: "2 karung Uji 50 kg"`, `noPO: "PO-UJI-2"`, `tanggalKirim: "2026-10-12"`,
`diubahOlehUid: "uid-uji-b"`, `diubahOleh: "UJI B"`.

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★M1 | staf aktif (ben) | create `pesanan/uji-v11-ps` | PS | LOLOS | pesanan dibuat dari tablet (v11-1) |
| ★M5 | staf aktif (ben) | update `pesanan/uji-v11-ps` | PS + UBAH | LOLOS | Ben mengubah isi, PO & tanggal kirim (v11-2) |
| ★M6 | staf aktif (ben) | update `pesanan/uji-v11-ps` | PS dengan `status: "batal"`, `alasanBatal`, `nasibUangMuka: "saldo"`, `diubahOlehUid` | LOLOS | Ben membatalkan, uang muka jadi saldo |
| ★M7 | staf aktif (ben) | update `pesanan/uji-v11-ps` | PS dengan `status: "diantar"`, `diubahOlehUid` | LOLOS | Ben menandai diantar |
| ★M8 | staf aktif peran **karyawan** | create `pesanan/uji-v11-ps` | PS | DITOLAK | bikin pesanan = owner & ben |
| ★M9 | staf aktif peran **karyawan** | update `pesanan/uji-v11-ps` | PS + UBAH | DITOLAK | karyawan cuma melihat |
| ★M10 | staf aktif (ben) | create `pesanan/uji-v11-ps` | PS dengan `trxIdJual: "1"` | DITOLAK | pesanan baru belum bernota |
| ★M11 | staf aktif (ben) | create `pesanan/uji-v11-ps` | PS dengan `status: "dibayar"` | DITOLAK | pesanan baru selalu "dipesan" |
| ★M12 | staf aktif (ben) | create `pesanan/uji-v11-ps` | PS dengan `nasibUangMuka: "saldo"` | DITOLAK | kolom batal tidak boleh di pesanan baru |
| ★M13 | staf aktif (ben) | update `pesanan/uji-v11-ps` | PS dengan `namaPelanggan: "Lain"`, `diubahOlehUid` | DITOLAK | nama pemesan (uang muka & bon) tidak bisa diganti |
| ★M14 | staf aktif (ben) | update `pesanan/uji-v11-ps` (sudah `dibayar`) | PS dengan `status: "dibayar"`, `trxIdJual: "1"`, `isi: "lain"` | DITOLAK | pesanan yang sudah jadi nota tidak diubah |
| ★M15 | staf aktif (ben) | update `pesanan/uji-v11-ps` (sudah `batal`) | PS dengan `status: "dipesan"` | DITOLAK | pesanan batal tidak dihidupkan lagi |
| ★M16 | staf aktif (ben) | update `pesanan/uji-v11-ps` | PS + UBAH dengan `diubahOlehUid: "uid-lain"` | DITOLAK | pengubah bukan yang mengaku |
| ★M17 | staf aktif peran **karyawan** | update `pesanan/uji-v11-ps` | PS dengan `status: "dibayar"`, `trxIdJual: "1"`, `diubahOlehUid` | LOLOS | catat jual pesanan (JADI NOTA) tetap jalan sejak v1 |
| ★M18 | staf aktif (ben) | create `orderRutin/uji-v11-rutin` | RUTIN | LOLOS | Ben membuat jadwal rutin (v11-3) |
| ★M19 | staf aktif (ben) | update `orderRutin/uji-v11-rutin` | RUTIN dengan `lewati: ["2026-10-12"]`, `aktif: false`, `diubahOlehUid` | LOLOS | lewati sekali & hentikan jadwal |
| ★M20 | staf aktif (ben) | update `orderRutin/uji-v11-rutin` | RUTIN dengan `olehUid: "uid-lain"`, `diubahOlehUid` | DITOLAK | pembuat jadwal tidak bisa diganti |
| ★M21 | staf aktif peran **karyawan** | create `orderRutin/uji-v11-rutin` | RUTIN | DITOLAK | bikin jadwal = owner & ben |
| ★M22 | staf aktif (ben) | delete `orderRutin/uji-v11-rutin` | — | DITOLAK | hapus = owner |
| ★M23 | staf aktif peran **karyawan** | get `orderRutin/uji-v11-rutin` | — | LOLOS | tablet menampilkan pengingat jadwal |
| ★M24 | kasir@ | get `orderRutin/uji-v11-rutin` | — | DITOLAK | kasir darurat tidak membaca jadwal |
| ★M25 | staf aktif (ben) | create `pesanan/uji-v11-ps` | PS dengan `olehUid: "uid-lain"` | DITOLAK | penulis bukan yang mengaku |

Di **v10** kasus ★M1 ★M3 ★M5 ★M6 ★M7 ★M18 ★M19 ★M23 DITOLAK (v11 yang membukanya); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V11** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): ke-25 kasus di
atas atas `firestore.rules` (v11) dan atas `firestore.rules.v10` — yang berbeda wajib persis kasus yang dibuka v11 — plus kontrol (satu suku v11 dirusak →
kasus sasarannya wajib berbalik). Semua kasus v10, v9, v8 & v7 lama tetap dijalankan atas v11 dan wajib sama hasilnya.

## Hasil Playground & terbit (18 Nov 2026)

- Isi editor Console sebelum uji = `firestore.rules` cabang ini, byte demi byte (SHA-256 berawalan `5940fcf8`, 60.151 byte; dibaca lewat JS dari editor),
  sebelumnya v10 aktif (`1665c3b8`, 56.847 byte); dicek ulang sesudah ketiga kasus.
- Wajib owner, akun owner (`uid-uji`, provider password, email owner di payload):
  ★M2 create `pesanan/uji-v11-ps` isian PS (13 kolom; `nilaiPerkiraan` int64, `riwayatStatus` array kosong) → "Simulated write allowed" (LOLOS, sesuai);
  ★M3 create `orderRutin/uji-v11-rutin` isian RUTIN (13 kolom; `hari` int64, `aktif` boolean, `lewati` array kosong) → "Simulated write allowed" (LOLOS,
  sesuai; rincian Playground menilai `... || stafBuat(['ben'])` = blok baru v11); ★M4 update `pesanan/uji-v11-ps` PS dengan `status: "batal"` +
  `alasanBatal: "uji"` → "Simulated write allowed" (LOLOS, sesuai; rincian menilai `... || stafUbahPesanan ...` & `... || stafAturPesanan ...`).
- Owner klik **Publish** 18 Nov 2026 ±12.38 WIB (riwayat Console "Today • 12:38 PM"; sebelumnya v10 "Today • 4:43 AM"). Sesudah halaman dimuat ulang,
  aturan yang berlaku = berkas ini (sidik sama, baris 2 `ATURAN FIRESTORE v11 FINAL`, tanpa draf tertunda).
