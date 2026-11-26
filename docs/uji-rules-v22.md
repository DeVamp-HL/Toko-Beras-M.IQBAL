# Uji rules v22 di server — kalender kepatuhan dari tablet (DRAF 26 Nov 2026)

v22 = v21 FINAL + **satu nama dokumen di baris baca `aturanToko`, satu fungsi baru (`stafCekPatuh`), dan satu blok baru (`kepatuhanCek`)** (berkas kanonik
`firestore.rules`; pembanding `firestore.rules.v21`). Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan
sisanya huruf demi huruf dengan v21.

## Yang berubah v21 → v22

1. **(v22-1) `aturanToko` read: + dokumen `kepatuhan` untuk Penjaga laci** — paket Stok minus, label & kepatuhan, keputusan owner 26 Nov 2026: "Owner + Ben dari
   tablet". Dokumen itu = daftar butir kalender kepatuhan (SPT Tahunan, cek aturan bulanan, izin & legalitas, periksa label, tera ulang timbangan, THR, tutup
   buku) + bentuk usaha, yang diisi owner. Karyawan TIDAK membacanya. Baris tulis `aturanToko` TIDAK berubah (owner saja).
2. **(v22-2) blok `kepatuhanCek`** — satu dokumen per tanda "sudah dikerjakan" satu putaran butir, tambah-saja:
   - read: owner atau Penjaga laci (karyawan tidak);
   - create: owner, atau Penjaga laci atas nama penulisnya (`olehUid`) dengan bentuk tetap — `id` = id dokumen, tanggal `YYYY-MM-DD`, `butir` = id butir
     `[a-z0-9-]` 1–40 huruf, `periode` 4–10 huruf `[0-9K-]` (mis. `2026-12`, `2027-K1`, `2027`, `2027-03-31`), catatan ≤ 160 huruf, kolom dibatasi;
   - ubah & hapus: owner saja.

Bukan data uang / stok: tidak ada rupiah, kg, atau tanggal buku yang dikunci periode. **Terbitkan v22 SEBELUM PR Stok minus, label & kepatuhan digabung** — tanpa
v22 pendengar `aturanToko/kepatuhan` dan `kepatuhanCek` di tablet Penjaga laci ditolak server (tercatat di Sistem › Perangkat) dan tanda "sudah dikerjakan" dari
tablet DITOLAK; layar owner (kalender, Atur, tanda dari HP) tetap jalan.

## Urutan (± 5 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish** — sebelum PR digabung.
4. Sesudah terbit dan PR digabung: di tablet (akun Penjaga laci) buka Menu › Sistem › Pengingat, pilih satu butir kalender, ketuk **Sudah dikerjakan**; di HP
   owner buka Laporan › Pajak › Kalender kepatuhan — butir itu tertulis "terakhir … (nama Penjaga laci)".

## Wajib owner (3 kasus — tanpa dokumen uji staf)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★Q1 | owner@ | create `kepatuhanCek/kp-2026-12-01-uji1` | tanda cek HET Des 2026 | LOLOS | owner menandai butir dikerjakan |
| 2 | ★Q2 | owner@ | get `kepatuhanCek/kp-2026-12-01-uji1` | — | LOLOS | owner membaca tanda kalender |
| 3 | ★Q3 | owner@ | create `aturanToko/kepatuhan` | satu butir SPT + bentuk usaha | LOLOS | owner menyimpan setelan kalender |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator di bawah
(mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★Q4 | Penjaga laci | get `aturanToko/kepatuhan` | — | LOLOS | tablet membaca daftar butir |
| ★Q5 | Penjaga laci | create `kepatuhanCek/kp-2026-12-01-uji1` | tanda atas namanya | LOLOS | Ben menandai dari tablet |
| ★Q6 | Penjaga laci | get `kepatuhanCek/kp-2026-12-01-uji1` | — | LOLOS | tablet melihat yang sudah ditandai |
| ★Q7 | karyawan | get `aturanToko/kepatuhan` | — | DITOLAK | kalender = Penjaga laci saja |
| ★Q8 | karyawan | create `kepatuhanCek/kp-2026-12-01-uji1` | tanda | DITOLAK | menandai = Penjaga laci saja |
| ★Q9 | karyawan | get `kepatuhanCek/kp-2026-12-01-uji1` | — | DITOLAK | kalender = Penjaga laci saja |
| ★Q10 | Penjaga laci | create `kepatuhanCek/kp-2026-12-01-uji1` | olehUid orang lain | DITOLAK | atas nama penulisnya |
| ★Q11 | Penjaga laci | create `kepatuhanCek/kp-2026-12-01-uji1` | id kp-lain | DITOLAK | id = id dokumen |
| ★Q12 | Penjaga laci | create `kepatuhanCek/kp-2026-12-01-uji1` | + nominal | DITOLAK | kolom dibatasi |
| ★Q13 | Penjaga laci | create `kepatuhanCek/kp-2026-12-01-uji1` | butir 'Cek HET' | DITOLAK | id butir huruf kecil, angka, strip |
| ★Q14 | Penjaga laci | create `kepatuhanCek/kp-2026-12-01-uji1` | periode '2026/12' | DITOLAK | bentuk putaran tetap |
| ★Q15 | Penjaga laci | create `kepatuhanCek/kp-2026-12-01-uji1` | catatan 161 huruf | DITOLAK | paling banyak 160 huruf |
| ★Q16 | Penjaga laci | create `kepatuhanCek/kp-2026-12-01-uji1` | tanggal '1 Des' | DITOLAK | tanggal YYYY-MM-DD |
| ★Q17 | Penjaga laci | update `kepatuhanCek/kp-2026-12-01-uji1` | catatan diubah | DITOLAK | ubah = owner |
| ★Q18 | Penjaga laci | delete `kepatuhanCek/kp-2026-12-01-uji1` | — | DITOLAK | hapus = owner |
| ★Q19 | Penjaga laci | create `aturanToko/kepatuhan` | setelan kalender | DITOLAK | setelan ditulis owner |
| ★Q20 | kasir@ | create `kepatuhanCek/kp-2026-12-01-uji1` | tanda | DITOLAK | kasir darurat tidak menandai |
| ★Q21 | Penjaga laci nonaktif | create `kepatuhanCek/kp-2026-12-01-uji1` | tanda | DITOLAK | akun yang dinonaktifkan owner |

Di **v21** kasus ★Q1, ★Q2, ★Q4, ★Q5, ★Q6 DITOLAK (koleksi `kepatuhanCek` belum ada, dokumen `kepatuhan` belum dibaca ben); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V22** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): kedua puluh satu kasus
di atas atas `firestore.rules` (v22) dan atas `firestore.rules.v21` — yang berbeda wajib persis ★Q1, ★Q2, ★Q4, ★Q5, ★Q6 — plus kontrol (ubahan v22 dirusak →
kasus sasarannya wajib berbalik). Semua kasus v21 sampai v7 lama tetap dijalankan atas v22 dan wajib sama hasilnya.

## Hasil Playground & terbit

**v22 TERBIT 26 Nov 2026 12.03 WIB** (riwayat Console "Today • 12:03 PM"). Isi editor sebelum Publish dan isi yang terbit sesudah halaman dimuat ulang sama
persis dengan `firestore.rules` cabang ini: SHA-256 berawalan `5a4939e817f96951`, 82.629 byte, baris 2 `ATURAN FIRESTORE v22 FINAL`.
Playground (akun uji owner: UID `uid-uji`, email `owner@tokoberasmiqbal.web.app`): ★Q2 get → *Simulated read allowed* · ★Q1 create (butir, periode) →
*Simulated write allowed* · ★Q3 create `aturanToko/kepatuhan` → *Simulated write allowed* — ketiganya sesuai kolom Wajib.
