# Prosedur pulih darurat — memulihkan data dari berkas cadangan (sesudah sistem lama pensiun, 3 Okt 2026)

**Kapan dipakai:** data di server hilang atau rusak, dan harus dikembalikan dari berkas cadangan (`backup-batch-miqbal-….json`). Ini jalan
**darurat**, bukan pekerjaan rutin.

> **3 Okt 2026 — sistem lama & `kasir.html` pensiun** (owner: "bumi hanguskan"). `index.html` dan `kasir.html` di situs kini hanya halaman pengalih
> ke `/baru/`. Satu-satunya pemulih dari berkas (`muatDariFile`, Setelan › Muat cadangan, mode PULIHKAN) ada di sistem lama — jadi sistem lama
> **dijalankan di komputer dari tag git**, tidak lagi dibuka dari situs. Versi terakhirnya utuh di tag **`sistem-lama-terakhir`** (commit `48a694d`).
> Sebelum 3 Okt prosedur ini membuka sistem lama dari situs dan memakai rules v4; sekarang rules yang terpasang = `firestore.rules` (v6).

## Kenapa perlu prosedur

- Sistem lama hanya-baca sejak 25b; satu-satunya jalan tulis catatan yang tetap terbuka di sana adalah **Setelan › Muat cadangan**, dan itu pun harus
  mengetik **PULIHKAN** dulu (keputusan owner 26 Sep 2026). `/baru/` belum punya pemulih dari berkas.
- Di bawah aturan server sekarang (`firestore.rules` v6), memulihkan **pasti ditolak** untuk semua catatan yang bertanggal di bulan terkunci. Kunci
  bulan menolak siapa pun, termasuk owner.
- Karena itu, pemulihan hanya bisa berjalan selama **aturan darurat** terpasang. Aturan darurat = isi `firestore.rules.v3`: aturan akun per orang
  tetap berlaku, kunci bulan tidak ada.

> **Selama aturan darurat aktif, KUNCI BULAN TIDAK BERLAKU.** Semua bulan, termasuk yang sudah dikunci, bisa ditulis owner dan kasir darurat. Jendelanya
> harus **sesingkat mungkin**: pasang, pulihkan, langsung kembalikan `firestore.rules`.

## Keterbatasan yang WAJIB diketahui sebelum mulai

- **Hanya 27 koleksi lama yang dipulihkan.** Pemulih sistem lama (`muatDariFile`, daftar koleksinya di `index.html` tag `sistem-lama-terakhir`) hanya
  mengenal koleksi yang ada sebelum `/baru/`. `/baru/` punya 56 koleksi (`baru/js/data/koleksi.js`); ±29 koleksi milik `/baru/` — antara lain
  `wadahLiteran`, `hargaTerbit`, `pindahUang`, `slipUpah`, `absenKaryawan`, `tutupBukuAcara`, `aturanToko`, `hargaWadah`, `bukuHapus` — **TIDAK ikut
  pulih** lewat jalan ini. Kalau yang hilang termasuk koleksi itu, jalan ini tidak cukup: berhenti dan putuskan dulu (owner) sebelum menyentuh rules.
- Katalog kasir (`ringkasanKasir`) tidak ikut dipulihkan dari berkas; `/baru/` menerbitkannya ulang sendiri begitu data termuat.
- Sekali membuka sistem lama ≈ **7,4 rb baca** dokumen (kuota Spark 50 rb baca/hari, reset 14.00 WIB). Jangan dimuat ulang berkali-kali.
- [BELUM TERVERIFIKASI] Apakah kunci API web Firebase dibatasi referrer/domain. Kalau ya, masuk dari `localhost` ditolak — periksa dulu di Console
  (Authentication › Settings › Authorized domains; Google Cloud › Credentials) sebelum jendela darurat dibuka.

## Langkah (owner yang menempel aturan; Claude hanya membaca dan memeriksa)

0. **Sebelum mulai**
   - Unduh cadangan keadaan sekarang (Menu › Sistem › Cadangan di `/baru/`), walaupun datanya sedang kacau — **dua kali cadangan**: sebelum dan sesudah.
   - Catat **jam mulai**.
   - Minta penjaga berhenti mencatat sebentar. Karcis kasir darurat tetap aman di antrean HP.
   - Siapkan dua berkas aturan dari repo: `firestore.rules.v3` (darurat) dan `firestore.rules` (yang berlaku, v6).
     Salin tanpa merusak huruf: `git show origin/main:firestore.rules.v3 | LANG=en_US.UTF-8 pbcopy`.
   - Siapkan sistem lama di komputer — ambil **POHON tag**, bukan `index.html` saja (supaya `lib/lz-string.js` & `lib/kemas-worker.js` ikut;
     tanpa itu cadangan lokal terkompres tidak terbaca):
     ```
     git fetch origin tag sistem-lama-terakhir     # kalau tag belum ada di komputer ini
     git worktree add /tmp/sistem-lama sistem-lama-terakhir
     # atau tanpa worktree:  mkdir /tmp/sistem-lama && git archive sistem-lama-terakhir | tar -x -C /tmp/sistem-lama
     ```
     **Tidak diterbitkan, tidak di-commit.**
1. **Pasang aturan darurat.** Console › Firestore › Rules → tempel isi `firestore.rules.v3` → **Publish**. Catat jam. Sidik v3 yang benar:
   SHA-256 berawalan `32c55d58`.
2. **Pulihkan.**
   - Di folder sistem lama: `python3 -m http.server 8731 --bind 127.0.0.1` → buka `http://localhost:8731/index.html`, masuk dengan akun owner.
     Simpanan lokal peramban untuk alamat `localhost` kosong — itu wajar.
   - Setelan › Muat cadangan → pilih berkas → ketik **PULIHKAN** → tunggu kalimat "Berhasil diunggah …".
   - Sistem lama hanya **menambah** catatan yang id-nya belum ada. Tidak menimpa, tidak menghapus.
   - Berkas dari era tutup buku yang lain ditolak sendiri (penjaga era).
   - Sesudahnya: tutup tab, **matikan server** (Ctrl-C), hapus folder (`git worktree remove /tmp/sistem-lama` atau `rm -rf /tmp/sistem-lama`).
3. **Kembalikan `firestore.rules` SEGERA.** Tempel isi `firestore.rules` → **Publish**. Cocokkan isi editor dengan repo: SHA-256 dihitung dari repo
   SAAT ITU (`shasum -a 256 firestore.rules`; per 3 Okt 2026 = v6, berawalan `4289d24c`). Catat jam. Jendela darurat = jam langkah 1 sampai jam
   langkah 3.
4. **Jalankan ulang ★ aturan yang berlaku.** Pakai `docs/uji-rules-v6.md` (tanpa dokumen kunci uji), lalu satu karcis dari kasir darurat. Kalau ada ★
   yang tidak sesuai: tempel lagi `firestore.rules` dari repo, jangan dibiarkan.
5. **Periksa & catat.**
   - Unduh cadangan kedua (sesudah).
   - Di `/baru/`: daftar periksa kunci bulan, dan angka bulan terkunci (laba, neraca) — bandingkan dengan sebelum kejadian.
   - Tulis kejadiannya di `docs/peta-kunci-periode.md`: tanggal, jam buka dan tutup jendela darurat, alasan, berkas cadangan yang dipakai, dan siapa
     yang menempel aturan.

## Yang tidak boleh

- Membiarkan aturan darurat terpasang melewati hari itu.
- Menerbitkan sistem lama ke situs lagi (mengembalikan `index.html` lama ke `main`) untuk memulihkan. Jalankan di komputer dari tag.
- Memulihkan lewat aturan yang berlaku lalu "mengulang sampai berhasil". Catatan bulan terkunci tidak akan pernah lolos.
- Menghapus `aturanToko/kunciPeriode` supaya pemulihan lolos. Dokumen kunci tidak pernah dihapus (rules menolaknya, dan menghapus lewat Console =
  membuka semua bulan tanpa jejak).
