# Uji rules v14 di server — data uang untuk Ringkas hari ini di tablet (DRAF 21 Nov 2026)

v14 = v13 FINAL + **dua fungsi baru dan sebelas baris baca** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v13`). Tidak ada yang lain
berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v13. **Tulis tidak berubah**: uang tetap
hanya ditulis owner.

## Yang berubah v13 → v14

1. **(v14-1) `stafBacaUang()` + `bacaUangDari()`** — akun Penjaga laci (peran `ben`, aktif) yang **ditandai owner** di `aksesAkun/{uid}.bacaUang == true`.
   Tanda itu ditulis owner saja (blok `aksesAkun` owner-saja sejak v3). Karyawan, akun tanpa tanda, akun nonaktif, kasir@ = sama dengan v13 (ditolak).
2. **(v14-2) baca** `+ stafBacaUang()` di `biayaBulanan`, `pengeluaranHarian`, `kasbonMutasi`, `tutupHari`, `setoranKas`, `amplopLaba`, `modalOwner`,
   `utangOwnerMutasi`, `utangPemasokMutasi`, `pindahUang`, dan `pengaturan/titikKas` — data yang dipakai rumus laci seharusnya & uang keluar (sama dengan
   Tutup hari di HP). Dokumen `pengaturan` lain (keamanan, aksesKasir, pintuBuku) dan slip upah tetap owner saja.

Di aplikasi: data uang itu **dimuat ke tablet hanya selama orang pilihan owner jaga** (Menu › Toko ini › Peran & persetujuan › Orang di tablet › Ringkas hari
ini) dan dibuang dari layar begitu orang lain jaga. Yang menjaga datanya tetap server: tanpa tanda `bacaUang`, akun tablet tidak bisa membacanya sama sekali.

## Urutan (± 10 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus, akun owner). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish**.
4. Baru sesudah itu cabangnya digabung (merge). Kalau dibalik, kartu Ringkas di tablet menyebut "Server menolak data uang" — tidak ada yang rusak, laci saja
   yang tidak dihitung. Jual, stok, dan uang owner tidak bergantung padanya.
5. Sesudah merge: owner menandai akun tablet (**baca data uang**, dua ketukan) dan memilih **Dibuka oleh** = dirinya di Orang di tablet.

## Wajib owner (3 kasus — akun owner, tanpa dokumen uji)

`pengaturan/titikKas` = dokumen NYATA toko (isinya tidak dinilai). Dua jalur lain boleh belum ada dokumennya — baca owner tidak membaca isi.

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★W1 | owner@ | get `pengeluaranHarian/uji-v14-u` | — | LOLOS | owner tetap membaca uang keluar (baris baca baru tidak mengunci owner) |
| 2 | ★W2 | owner@ | get `pengaturan/titikKas` | — | LOLOS | owner tetap membaca titik kas |
| 3 | ★W3 | owner@ | get `tutupHari/uji-v14-u` | — | LOLOS | owner tetap membaca tutup hari |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben) **dengan `bacaUang: true`** ("bertanda"), dan
dokumen uang uji `uji-v14-u` di koleksinya. Tanpa itu cukup percaya bukti emulator di bawah (mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★W4 | staf bertanda | get `biayaBulanan/uji-v14-u` | — | LOLOS | upah & biaya bulanan masuk rumus laci |
| ★W5 | staf bertanda | get `pengeluaranHarian/uji-v14-u` | — | LOLOS | uang keluar harian |
| ★W6 | staf bertanda | get `kasbonMutasi/uji-v14-u` | — | LOLOS | kasbon diambil / kembali |
| ★W7 | staf bertanda | get `tutupHari/uji-v14-u` | — | LOLOS | tutup hari |
| ★W8 | staf bertanda | get `setoranKas/uji-v14-u` | — | LOLOS | setoran lama (modal owner) |
| ★W9 | staf bertanda | get `amplopLaba/uji-v14-u` | — | LOLOS | sisihan amplop laba (laci ↔ amplop) |
| ★W10 | staf bertanda | get `modalOwner/uji-v14-u` | — | LOLOS | modal owner masuk / ditarik |
| ★W11 | staf bertanda | get `utangOwnerMutasi/uji-v14-u` | — | LOLOS | bayar utang ke owner |
| ★W12 | staf bertanda | get `utangPemasokMutasi/uji-v14-u` | — | LOLOS | bayar bon pemasok |
| ★W13 | staf bertanda | get `pindahUang/uji-v14-u` | — | LOLOS | pindah uang laci ↔ brankas / rekening |
| ★W14 | staf bertanda | get `pengaturan/titikKas` | — | LOLOS | patokan laci |
| ★W15 | staf (ben) TANPA tanda | get `pengeluaranHarian/uji-v14-u` | — | DITOLAK | tanpa tanda owner = sama dengan v13 |
| ★W16 | staf peran **karyawan** bertanda | get `pengeluaranHarian/uji-v14-u` | — | DITOLAK | tanda hanya berarti untuk Penjaga laci |
| ★W17 | staf bertanda **nonaktif** | get `pengeluaranHarian/uji-v14-u` | — | DITOLAK | akun nonaktif tidak membaca apa pun |
| ★W18 | staf bertanda | create `pengeluaranHarian/uji-v14-u` | uang uji | DITOLAK | v14 hanya membuka BACA |
| ★W19 | staf bertanda | update `pengaturan/titikKas` | `laci: 999` | DITOLAK | titik kas ditulis owner |
| ★W20 | staf bertanda | get `pengaturan/keamanan` | — | DITOLAK | pengaturan lain tetap owner |
| ★W21 | staf bertanda | get `slipUpah/uji-v14-u` | — | DITOLAK | slip upah bukan bagian rumus laci |
| ★W22 | kasir@ | get `pengeluaranHarian/uji-v14-u` | — | DITOLAK | kasir darurat tidak membaca uang |

Di **v13** kasus ★W4–★W14 DITOLAK (v14 yang membukanya); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V14** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): ke-22 kasus di
atas atas `firestore.rules` (v14) dan atas `firestore.rules.v13` — yang berbeda wajib persis kasus yang dibuka v14 — plus kontrol (satu suku v14 dirusak →
kasus sasarannya wajib berbalik). Semua kasus v13, v12, v11, v10, v9, v8 & v7 lama tetap dijalankan atas v14 dan wajib sama hasilnya.

## Hasil Playground & terbit

Belum — diisi sesudah owner menjalankan Wajib owner dan menekan Publish.
