# Uji rules v16 di server — tutup hari dari tablet (DRAF 22 Nov 2026)

v16 = v15 FINAL + **satu fungsi baru dan dua ubahan baris** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v15`).
Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v15.

## Yang berubah v15 → v16

1. **(v16-1) `persetujuan` create + `stafHitungLaci(['ben']) && tglStaf('tanggal')`** — HITUNGAN LACI dari tablet oleh Penjaga laci: tindakan `hitungLaci`,
   status `menunggu`, atas nama penulisnya (`mintaUid`), hitungan rupiah bulat 1 – 1.000.000.000, yang sudah dipindah ke brankas (`amankan`) bulat 0 –
   hitungan, tanpa kolom keputusan; bulan tidak terkunci. **Hari ditutup owner**: `tutupHari`, titik kas, amplop, pindah uang, dan penyesuaian stok tetap
   ditulis owner saja.
2. **(v16-2) `aturanToko` read + dokumen `tutupHari` untuk Penjaga laci (ben)** — tablet memakai **uang kembalian** yang owner setel untuk
   "pindahkan Rp… ke brankas". Karyawan tidak membacanya; menulis aturan tetap owner.

Karyawan, kasir@, dan akun nonaktif = sama dengan v15 (ditolak).

## Urutan (± 10 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus, akun owner). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish**.
4. Baru sesudah itu cabangnya digabung (merge). Kalau dibalik, hitungan laci dari tablet ditolak server ("ditolak server" di Perangkat & antrean), dan
   tablet tidak bisa membaca uang kembalian (langkah amankan laci dilewati). Tidak ada yang rusak.
5. Sesudah merge: owner menjalankan ulang pemasangan fungsi notifikasi sekali di Cloud Shell (`cd Toko-Beras-M.IQBAL && git pull && bash functions/pasang.sh`)
   supaya notifikasi HP menyebut "Hitungan laci". Tanpa itu notifikasinya tetap datang, judulnya saja yang umum.

## Wajib owner (3 kasus — akun owner, tanpa dokumen uji)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★Y1 | owner@ | create `tutupHari/2026-10-09` | tutup hari biasa | LOLOS | owner tetap menutup hari |
| 2 | ★Y2 | owner@ | update `persetujuan/uji-v16-hl` | hitungan laci → disetujui | LOLOS | owner memakai hitungan tablet |
| 3 | ★Y3 | owner@ | update `aturanToko/tutupHari` | uang kembalian 200.000 | LOLOS | aturan tutup hari tetap ditulis owner |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben). Tanpa itu cukup percaya bukti emulator di bawah
(mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★Y4 | Penjaga laci | create `persetujuan/uji-v16-hl` | hitungan laci (menunggu) | LOLOS | hitungan dari tablet |
| ★Y5 | Penjaga laci | get `aturanToko/tutupHari` | — | LOLOS | tablet membaca uang kembalian |
| ★Y6 | karyawan | create `persetujuan/uji-v16-hl` | hitungan laci | DITOLAK | penghitung = Penjaga laci saja |
| ★Y7 | karyawan | get `aturanToko/tutupHari` | — | DITOLAK | setelan uang = Penjaga laci & owner |
| ★Y8 | Penjaga laci | create `persetujuan/uji-v16-hl` | hitungan 0 | DITOLAK | hitungan wajib berisi |
| ★Y9 | Penjaga laci | create `persetujuan/uji-v16-hl` | brankas 700.000 > hitungan | DITOLAK | yang dipindah ≤ yang dihitung |
| ★Y10 | Penjaga laci | create `persetujuan/uji-v16-hl` | hitungan pecahan | DITOLAK | rupiah bulat |
| ★Y11 | Penjaga laci | create `persetujuan/uji-v16-hl` | tanpa kolom brankas | DITOLAK | bentuk tablet lengkap |
| ★Y12 | Penjaga laci | create `persetujuan/uji-v16-hl` | sudah diputus | DITOLAK | keputusan = owner |
| ★Y13 | Penjaga laci | create `persetujuan/uji-v16-hl` | atas nama orang lain | DITOLAK | penghitung = penulis |
| ★Y14 | Penjaga laci | create `persetujuan/uji-v16-hl` | bulan lewat tenggang | DITOLAK | bulan lama = owner |
| ★Y15 | Penjaga laci | update `persetujuan/uji-v16-hl` | memutus sendiri | DITOLAK | memutus = owner |
| ★Y16 | Penjaga laci | create `tutupHari/2026-10-09` | menutup hari sendiri | DITOLAK | hari ditutup owner |
| ★Y17 | Penjaga laci | update `pengaturan/titikKas` | memajukan titik kas | DITOLAK | titik kas = owner |
| ★Y18 | Penjaga laci | update `aturanToko/tutupHari` | uang kembalian 0 | DITOLAK | aturan = owner |
| ★Y19 | kasir@ | create `persetujuan/uji-v16-hl` | hitungan laci | DITOLAK | kasir darurat tidak menutup hari |

Di **v15** kasus ★Y4 & ★Y5 DITOLAK (v16 yang membukanya); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V16** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): ke-19 kasus di
atas atas `firestore.rules` (v16) dan atas `firestore.rules.v15` — yang berbeda wajib persis kasus yang dibuka v16 — plus kontrol (satu suku v16 dirusak →
kasus sasarannya wajib berbalik). Semua kasus v15, v14, v13, v12, v11, v10, v9, v8 & v7 lama tetap dijalankan atas v16 dan wajib sama hasilnya.
