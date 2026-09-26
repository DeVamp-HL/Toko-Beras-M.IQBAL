# Prosedur pulih darurat — memulihkan data dari berkas cadangan (sesudah putaran 25b)

**Kapan dipakai:** data di server hilang atau rusak, dan harus dikembalikan dari berkas cadangan (`backup-batch-miqbal-….json`). Ini jalan
**darurat**, bukan pekerjaan rutin.

## Kenapa perlu prosedur

- Sejak 25b, sistem lama (`index.html`) hanya-baca. Satu-satunya jalan tulis catatan yang tetap terbuka di sana adalah **Setelan › Muat cadangan**,
  dan itu pun harus mengetik **PULIHKAN** dulu (keputusan owner 26 Sep 2026).
- Di bawah aturan server **v4** (`firestore.rules`), memulihkan **pasti ditolak** untuk semua catatan yang bertanggal di bulan terkunci. Kunci bulan
  menolak siapa pun, termasuk owner. Kiriman sistem baru yang menggabungkan banyak catatan bulan lampau juga ditolak kalau butuh lebih dari 18
  pemeriksaan kunci sekali kirim.
- Karena itu, pemulihan hanya bisa berjalan selama **aturan darurat** terpasang. Aturan darurat = isi `firestore.rules.v3`: aturan akun per orang
  tetap berlaku, kunci bulan tidak ada.

> **Selama aturan darurat aktif, KUNCI BULAN TIDAK BERLAKU.** Semua bulan, termasuk yang sudah dikunci, bisa ditulis owner dan kasir darurat. Jendelanya
> harus **sesingkat mungkin**: pasang, pulihkan, langsung kembalikan v4.

## Langkah (owner yang menempel aturan; Claude hanya membaca dan memeriksa)

0. **Sebelum mulai**
   - Unduh cadangan keadaan sekarang (Menu › Sistem › Cadangan di `/baru/`), walaupun datanya sedang kacau.
   - Catat **jam mulai**.
   - Minta penjaga berhenti mencatat sebentar. Karcis kasir darurat tetap aman di antrean HP.
   - Siapkan dua berkas dari repo: `firestore.rules.v3` (darurat) dan `firestore.rules` (v4).
     Salin tanpa merusak huruf: `git show origin/main:firestore.rules.v3 | LANG=en_US.UTF-8 pbcopy`.
1. **Pasang aturan darurat.** Console › Firestore › Rules → tempel isi `firestore.rules.v3` → **Publish**. Catat jam. Sidik v3 yang benar:
   SHA-256 berawalan `32c55d58`.
2. **Pulihkan.** Buka sistem lama → Setelan › Muat cadangan → pilih berkas → ketik **PULIHKAN** → tunggu kalimat "Berhasil diunggah …".
   - Sistem lama hanya **menambah** catatan yang id-nya belum ada. Tidak menimpa, tidak menghapus.
   - Berkas dari era tutup buku yang lain ditolak sendiri (penjaga era).
3. **Kembalikan v4 SEGERA.** Tempel isi `firestore.rules` → **Publish**. Cocokkan isi editor dengan repo (SHA-256 berawalan `bf0ade38`, cara yang
   sama dengan putaran 25). Catat jam. Jendela darurat = jam langkah 1 sampai jam langkah 3.
4. **Jalankan ulang ★ v4.** Pakai `docs/uji-rules-v4.md` bagian B dan C (tanpa dokumen kunci uji), lalu satu karcis dari kasir darurat. Kalau ada ★
   yang tidak sesuai: tempel lagi v4 dari repo, jangan dibiarkan.
5. **Periksa & catat.**
   - Di `/baru/`: daftar periksa kunci bulan, dan angka bulan terkunci (laba, neraca) — bandingkan dengan sebelum kejadian.
   - Tulis kejadiannya di `docs/peta-kunci-periode.md`: tanggal, jam buka dan tutup jendela darurat, alasan, berkas cadangan yang dipakai, dan siapa
     yang menempel aturan.

## Yang tidak boleh

- Membiarkan aturan darurat terpasang melewati hari itu.
- Memulihkan lewat v4 lalu "mengulang sampai berhasil". Catatan bulan terkunci tidak akan pernah lolos, dan yang ditolak masuk daftar "ditolak" di
  perangkat itu.
- Menghapus `aturanToko/kunciPeriode` supaya pemulihan lolos. Dokumen kunci tidak pernah dihapus (rules v4 menolaknya, dan menghapus lewat Console =
  membuka semua bulan tanpa jejak).
