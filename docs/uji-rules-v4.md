# Uji rules v4 di server — putaran 25 (kunci periode)

`alat-uji/periksa_rules.py` memeriksa **bentuk** rules v4 (statis, di CI). Berkas ini untuk **perilaku server**: kasus yang dijalankan owner di
**Rules Playground** (Console › Firestore › Rules), dengan v4 di EDITOR proyek toko, **sebelum** v4 diterbitkan. Claude Code tidak memegang sandi
dan tidak masuk Console. Kasus v3 ada di `docs/uji-rules-v3.md` dan diulang di bagian B.

Rules Playground membaca data sungguhan lewat `get()`. Kasus kunci periode membutuhkan dokumen kunci **di database**. Selama v3 yang terbit,
dokumen itu tidak dibaca siapa pun, jadi aman dibuat sementara untuk uji.

---

## Persiapan (sekali, di Console › Firestore › Data — v3 masih yang terbit)

1. Buat dokumen **`aturanToko/kunciPeriode`**: field `sampaiBulan` (string) = `2026-07`, field `riwayat` (array) = kosong.
   Artinya untuk uji: Juli 2026 dan sebelumnya TERKUNCI. Agustus = bulan lampau yang belum terkunci. September = bulan berjalan.
2. Di Playground, isian **Firebase UID** untuk owner diisi **`uid-uji`**. Kasus A13 dan A14 memakai uid ini di dalam `riwayat`.
3. **SESUDAH semua kasus selesai dan SEBELUM menempel v4: HAPUS dokumen `aturanToko/kunciPeriode`.** Di bawah v4 dokumen itu tidak bisa dihapus
   siapa pun. Kalau tertinggal, Juli dan bulan-bulan sebelumnya ikut terkunci, dan kunci pertama yang sungguhan tidak lagi mulai dari Agustus.

Dokumen nyata yang dipakai (dari cadangan 25 Sep):
- `pengeluaranHarian/1787308559387.802` bertanggal **28 Jul 2026**, di bulan terkunci uji.
- `pengeluaranHarian/1786284868188.7153` bertanggal **9 Agu 2026**, bulan lampau yang belum terkunci.

Isian *Auth token payload* sama seperti v3: tambahkan `"email": "owner@tokoberasmiqbal.web.app"` atau `"email": "kasir@tokoberasmiqbal.web.app"`.

## A · Kasus ★ baru (kunci periode, payung dihapus)

| # | Akun | Operasi · jalur · isi (*Build document*) | Wajib |
|---|---|---|---|
| ★A1 | owner@ | create `/penjualan/uji-a1` `{id:'uji-a1', tanggal:'2026-07-20', hargaTotal:1000}` — bertanggal bulan terkunci | **DITOLAK** |
| ★A2 | owner@ | update `/pengeluaranHarian/1787308559387.802` (28 Jul): isi dokumen yang sama, `nominal` diubah | **DITOLAK** (nilai LAMA di bulan terkunci) |
| ★A3 | owner@ | update `/pengeluaranHarian/1786284868188.7153` (9 Agu): `tanggal` diubah ke `'2026-07-30'` | **DITOLAK** (nilai BARU di bulan terkunci) |
| ★A4 | owner@ | delete `/pengeluaranHarian/1787308559387.802` | **DITOLAK** |
| ★A5 | owner@ | create `/penjualan/uji-a5` `{id:'uji-a5', tanggal:'<tanggal hari ini>', hargaTotal:1000}` | LOLOS (bulan berjalan, tanpa get()) |
| ★A6 | owner@ | update `/pengeluaranHarian/1786284868188.7153` (9 Agu): `nominal` diubah, tanggal tetap | LOLOS (Agustus belum terkunci; satu get()) |
| ★A7 | kasir@ | create `/penjualan/uji-a7` `{id:'uji-a7', tanggal:'<tanggal KEMARIN>', hargaTotal:1000, jenis:'kasir_darurat_nominal'}` | LOLOS |
| ★A8 | kasir@ | create `/penjualan/uji-a8` `{id:'uji-a8', tanggal:'2026-07-31', hargaTotal:1000}` | **DITOLAK** |
| ★A9 | owner@ | delete `/penjualan/tidak-ada-xyz` (dokumen yang tidak ada) | LOLOS (tidak ada yang berubah) |
| ★A10 | owner@ | create `/pajakSetoran/uji-a10` `{id:'uji-a10', masaPajak:'2026-07', tanggalSetor:'2026-07-15', jumlah:1}` | LOLOS (pajak tidak dikunci, K6) |
| ★A11 | owner@ | update `/pengaturan/titikKas`: isi sama, `tanggal` = `'<tanggal hari ini>'` | LOLOS (titik kas boleh maju) |
| ★A12 | owner@ | get `/koleksiUji/x` (koleksi yang TIDAK punya blok) | **DITOLAK** (payung dihapus; di v3 ★11 LOLOS) |
| ★A13 | owner@ (UID `uid-uji`) | update `/aturanToko/kunciPeriode` → `{sampaiBulan:'2026-06', riwayat:[{aksi:'buka', bulan:'2026-07', olehUid:'uid-uji', alasan:'uji playground satu langkah'}]}` | LOLOS (turun satu bulan dengan alasan) |
| ★A14 | owner@ (UID `uid-uji`) | update `/aturanToko/kunciPeriode` → `{sampaiBulan:'2026-05', riwayat:[{aksi:'buka', bulan:'2026-07', olehUid:'uid-uji', alasan:'uji playground dua langkah'}]}` | **DITOLAK** (turun dua bulan) |
| ★A15 | owner@ (UID `uid-uji`) | update `/aturanToko/kunciPeriode` → `{sampaiBulan:'2026-06', riwayat:[{aksi:'buka', bulan:'2026-07', olehUid:'uid-uji', alasan:'pendek'}]}` | **DITOLAK** (alasan < 10 huruf) |
| ★A16 | owner@ (UID `uid-uji`) | update `/aturanToko/kunciPeriode` → `{sampaiBulan:'2026-09', riwayat:[{aksi:'kunci', bulan:'2026-09', olehUid:'uid-uji', alasan:''}]}` | **DITOLAK** (bulan berjalan / melompati Agustus) |
| ★A17 | owner@ | delete `/aturanToko/kunciPeriode` | **DITOLAK** (dokumen kunci tidak pernah dihapus) |

Catatan:
- "Error running simulation … Null value error" = DITOLAK di server, bukan lolos (sama seperti v3).
- A6 memakai satu access call (get dokumen kunci). Playground menampilkan jumlahnya di rincian hasil, kalau ada.
- A13–A16 tidak mengubah apa pun di database; Playground hanya menilai.

## B · Kasus ★ v3 diulang dengan v4 di editor

Semua ★ di `docs/uji-rules-v3.md` §A dijalankan ulang, dengan hasil wajib yang sama, **kecuali ★11**. Di v4, ★11 wajib **DITOLAK** (= ★A12 di atas).
Catatan untuk ★2 (owner delete `/penjualan/x`): tetap LOLOS, karena dokumen `x` tidak ada (= ★A9).

## C · Sesudah semua ★ sesuai

1. **Hapus** dokumen `aturanToko/kunciPeriode` (Persiapan langkah 3).
2. Tempel `firestore.rules` v4 ke Console proyek toko. Isi editor harus persis sama dengan berkas di repo.
3. **Buat SATU nota dari kasir darurat** (kasir@) dan pastikan nota itu masuk di layar Jual `/baru/`. Tidak masuk → tempel `firestore.rules.v3`.
4. Kunci bulan pertama **baru sesudah putaran 25b**, dan hanya kalau daftar periksanya bersih (Uang › Tutup buku › Kunci bulan). Butir
   ⛔ "putaran 25b" menahannya sampai itu.

**Mundur** = tempel `firestore.rules.v3` (kunci periode mati; aturan akun v3 tetap).
