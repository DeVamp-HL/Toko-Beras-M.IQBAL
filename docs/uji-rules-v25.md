# Uji rules v25 di server — daftar centang rutin dari tablet / HP staf (DRAF 27 Nov 2026)

v25 = v24 FINAL + **satu nama dokumen di baris baca `aturanToko`, satu fungsi baru (`stafCekRutin`), dan satu blok baru (`rutinCek`)** (berkas kanonik
`firestore.rules`; pembanding `firestore.rules.v24`). Tidak ada yang lain berubah — `alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan
sisanya huruf demi huruf dengan v24.

## Yang berubah v24 → v25

1. **(v25-1) `aturanToko` read: + dokumen `rutin` untuk Penjaga laci & karyawan** — paket P6, keputusan owner 27 Nov 2026: yang boleh mencentang daftar rutin =
   "Owner + Ben + karyawan". Dokumen itu = daftar butir rutin harian / mingguan / bulanan (nama, jadwal, untuk siapa) yang diisi owner. Baris tulis `aturanToko`
   TIDAK berubah (owner saja).
2. **(v25-2) blok `rutinCek`** — satu dokumen per centang satu butir untuk satu putaran, tambah-saja:
   - read: owner, Penjaga laci, karyawan;
   - create: owner, atau Penjaga laci / karyawan atas nama penulisnya (`olehUid`) dengan bentuk tetap — `id` = id dokumen, tanggal `YYYY-MM-DD`, `butir` = id
     butir `[a-z0-9-]` 1–40 huruf, `periode` `YYYY-MM-DD` (hari, atau Senin untuk butir mingguan) atau `YYYY-MM` (butir bulanan), catatan ≤ 160 huruf, kolom
     dibatasi;
   - ubah & hapus: owner saja (membatalkan centang yang salah).

Bukan data uang / stok: tidak ada rupiah, kg, atau tanggal buku yang dikunci periode. Kalender kepatuhan (v22) TIDAK ikut terbuka untuk karyawan (★O23).
**Terbitkan v25 SEBELUM PR paket P6 digabung** — tanpa v25 pendengar `aturanToko/rutin` dan `rutinCek` di tablet / HP staf ditolak server (tercatat di
Menu › Toko ini › Perangkat & antrean) dan centang rutin dari staf DITOLAK; layar owner (Rutin, Atur daftar, centang dari HP), halaman tugas staf selain
baris rutin, dan semua bagian tutup hari tetap jalan.

## Urutan (± 5 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (tiga kasus). Hasilnya harus sama dengan kolom Wajib.
3. Klik **Publish** — sebelum PR digabung.
4. Sesudah terbit dan PR digabung: di tablet (orang yang jaga = karyawan) buka Menu — kartu **Tugas hari ini** paling atas, lalu kartu **Rutin**: ketuk
   **centang** pada satu butir "Semua yang jaga"; di HP owner buka Menu › Toko ini › Rutin › Siapa mencentang — butir itu tertulis atas nama orang tadi.

## Wajib owner (3 kasus — tanpa dokumen uji staf)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★O1 | owner@ | create `rutinCek/rc-2026-12-01-uji1` | centang Sapu & rapikan toko 1 Des | LOLOS | owner mencentang butir rutin |
| 2 | ★O2 | owner@ | get `rutinCek/rc-2026-12-01-uji1` | — | LOLOS | owner membaca centang |
| 3 | ★O3 | owner@ | create `aturanToko/rutin` | satu butir harian | LOLOS | owner menyimpan daftar rutin |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben; kasus karyawan = peran diganti karyawan). Tanpa itu
cukup percaya bukti emulator di bawah (mesin rules yang sama dengan server).

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★O4 | Penjaga laci | get `aturanToko/rutin` | — | LOLOS | tablet membaca daftar butir |
| ★O5 | Penjaga laci | create `rutinCek/rc-2026-12-01-uji1` | centang atas namanya | LOLOS | Ben mencentang dari tablet |
| ★O6 | Penjaga laci | get `rutinCek/rc-2026-12-01-uji1` | — | LOLOS | tablet melihat yang sudah dicentang |
| ★O7 | karyawan | get `aturanToko/rutin` | — | LOLOS | karyawan melihat butir untuknya |
| ★O8 | karyawan | create `rutinCek/rc-2026-12-01-uji1` | centang atas namanya | LOLOS | karyawan ikut mencentang (keputusan owner) |
| ★O9 | karyawan | get `rutinCek/rc-2026-12-01-uji1` | — | LOLOS | karyawan melihat yang sudah dicentang |
| ★O10 | Penjaga laci | create `rutinCek/rc-2026-12-01-uji1` | periode 2026-12 | LOLOS | putaran Senin / bulan |
| ★O11 | Penjaga laci | create `rutinCek/rc-2026-12-01-uji1` | olehUid orang lain | DITOLAK | atas nama penulisnya |
| ★O12 | Penjaga laci | create `rutinCek/rc-2026-12-01-uji1` | id rc-lain | DITOLAK | id = id dokumen |
| ★O13 | Penjaga laci | create `rutinCek/rc-2026-12-01-uji1` | + nominal | DITOLAK | kolom dibatasi |
| ★O14 | Penjaga laci | create `rutinCek/rc-2026-12-01-uji1` | butir 'Sapu Toko' | DITOLAK | id butir huruf kecil, angka, strip |
| ★O15 | Penjaga laci | create `rutinCek/rc-2026-12-01-uji1` | periode '2026-W49' | DITOLAK | putaran YYYY-MM-DD / YYYY-MM |
| ★O16 | Penjaga laci | create `rutinCek/rc-2026-12-01-uji1` | catatan 161 huruf | DITOLAK | paling banyak 160 huruf |
| ★O17 | Penjaga laci | create `rutinCek/rc-2026-12-01-uji1` | tanggal '1 Des' | DITOLAK | tanggal YYYY-MM-DD |
| ★O18 | Penjaga laci | update `rutinCek/rc-2026-12-01-uji1` | catatan diubah | DITOLAK | ubah = owner |
| ★O19 | Penjaga laci | delete `rutinCek/rc-2026-12-01-uji1` | — | DITOLAK | hapus = owner |
| ★O20 | Penjaga laci | create `aturanToko/rutin` | daftar rutin | DITOLAK | daftar ditulis owner |
| ★O21 | kasir@ | create `rutinCek/rc-2026-12-01-uji1` | centang | DITOLAK | kasir darurat tidak mencentang |
| ★O22 | Penjaga laci nonaktif | create `rutinCek/rc-2026-12-01-uji1` | centang | DITOLAK | akun yang dinonaktifkan owner |
| ★O23 | karyawan | get `aturanToko/kepatuhan` | — | DITOLAK | kalender kepatuhan tetap Penjaga laci saja (v22) |

Di **v24** kasus ★O1, ★O2, ★O4, ★O5, ★O6, ★O7, ★O8, ★O9, ★O10 DITOLAK (koleksi `rutinCek` belum ada, dokumen `rutin` belum dibaca staf); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V25** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): kedua puluh tiga kasus
di atas atas `firestore.rules` (v25) dan atas `firestore.rules.v24` — yang berbeda wajib persis ★O1, ★O2, ★O4, ★O5, ★O6, ★O7, ★O8, ★O9, ★O10 — plus kontrol (ubahan v25 dirusak → kasus sasarannya
wajib berbalik). Semua kasus v24 sampai v7 lama tetap dijalankan atas v25 dan wajib sama hasilnya.

## Hasil Playground & terbit

**v25 TERBIT 27 Nov 2026 ±13.07 WIB** — SESUDAH PR #236 (paket P6) digabung ke `main` (`44d580b`), bukan sebelumnya seperti urutan di atas. Di antara
gabung dan terbit, pendengar `aturanToko/rutin` & `rutinCek` di tablet / HP staf ditolak server dan centang rutin dari staf tidak tersimpan; layar owner tetap
jalan. Centang staf yang ditolak di jendela itu perlu dicentang ulang.
Owner menempel isi `firestore.rules` (commit `44d580b`, berkas mentah GitHub di tab Chrome Claude — sidiknya dicek lebih dulu = repo) ke editor Rules Console.
Isi editor sebelum Publish, sesudah uji Playground, dan isi yang aktif sesudah halaman dimuat ulang sama persis dengan `firestore.rules` di `main`:
SHA-256 berawalan `e6718c5577d2555f`, 90.788 byte, baris 2 `ATURAN FIRESTORE v25 FINAL` (sebelumnya aktif v24 `d7e25718`, 88.131 byte).
Playground (akun uji owner: UID `uid-uji`, email `owner@tokoberasmiqbal.web.app`, email terverifikasi): ★O2 get `rutinCek/rc-2026-12-01-uji1` →
*Simulated read allowed* · ★O1 create `rutinCek/rc-2026-12-01-uji1` (dokumen contoh `butir` bersih) → *Simulated write allowed* · ★O3 create
`aturanToko/rutin` → *Simulated write allowed* — ketiganya sesuai kolom Wajib. Kasus staf (★O4–★O23) dibuktikan emulator CI bagian V25.
