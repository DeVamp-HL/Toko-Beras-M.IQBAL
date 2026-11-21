# Notifikasi HP / Mac owner — langkah pasang (sekali)

Tujuannya: titipan uang keluar, pesan, dan permintaan lain dari tablet muncul di HP / Mac owner walau aplikasinya tertutup.
Jalurnya: tablet menulis permintaan ke `persetujuan` → **fungsi server** `kabarOwner` (folder `functions/`) → Firebase Cloud Messaging → HP / Mac
yang menyalakan notifikasi (token di koleksi `notifOwner`, rules v13: owner saja).

Saat aplikasi **terbuka**, notifikasi dalam aplikasi (pita di atas layar, getar, bunyi, lampu CPad) sudah jalan tanpa langkah di bawah ini.

## Urutan

1. **Rules v13 terbit dulu** (`docs/uji-rules-v13.md`). Tanpa itu token tidak bisa disimpan dan tablet tidak bisa menitip.
2. **Kunci notifikasi proyek (VAPID)** — Console Firebase › ⚙ Project settings › tab **Cloud Messaging** › bagian **Web configuration / Web Push
   certificates** › **Generate key pair**. Salin teks "Key pair" (diawali `B…`, ±87 huruf). Ini kunci PUBLIK, bukan rahasia.
3. Di aplikasi (HP atau Mac, akun owner): **Menu › Toko ini › Perangkat & antrean** › kartu **Notifikasi di perangkat ini** › tempel kunci itu ›
   **Simpan**. Cukup sekali untuk semua perangkat owner.
4. **Pasang fungsi server** — sekali, dari browser, tanpa memasang apa pun di Mac:
   - buka `console.cloud.google.com`, pilih proyek **toko-beras-m-iqbal**, klik ikon **Cloud Shell** (`>_`, kanan atas);
   - salin-tempel satu baris ini **di terminal Cloud Shell** (bukan Terminal Mac / kotak perintah lain — di Mac tidak ada `gcloud` & `node`, skripnya
     berhenti di langkah pertama tanpa mengubah apa pun), Enter:

     ```bash
     git clone https://github.com/DeVamp-HL/Toko-Beras-M.IQBAL.git && cd Toko-Beras-M.IQBAL && bash functions/pasang.sh
     ```

   - Klik **Authorize** kalau Cloud Shell meminta izin memakai akun Google. Di Cloud Shell Firebase CLI biasanya **tidak** meminta login lagi (memakai
     akun Cloud Shell); kalau tetap meminta, ikuti tautannya, pilih akun Google pemilik proyek, salin kodenya kembali.
   - Layanan yang dibutuhkan (Cloud Functions, Cloud Build, Artifact Registry, Eventarc, Cloud Run, Pub/Sub) dinyalakan sendiri; kalau ditanya, jawab `Y`.
   - Skrip membaca lokasi database Firestore dan memasang fungsi di lokasi yang sama (wajib untuk pemicu Firestore).
   - **Pemasangan PERTAMA biasanya ditolak** dengan "Permission denied while using the Eventarc Service Agent … Retry the deployment in a few minutes"
     (izin Eventarc baru menyebar beberapa menit). Tunggu ±2 menit lalu jalankan lagi di folder yang sama: `bash functions/pasang.sh` (21 Nov 2026: sekali
     dicoba ulang → berhasil).
   - Di akhir ditanya **"How many days do you want to keep container images before they're deleted?"** — jawab `1` (keputusan owner 21 Nov 2026: salinan
     lama paket fungsi dihapus otomatis tiap 1 hari; fungsi yang berjalan tidak terpengaruh).
   - Selesai bila muncul `Deploy complete!` dan baris `Selesai.` (21 Nov 2026: `kabarOwner` terpasang di asia-southeast2 = lokasi database.)
5. **Nyalakan di tiap perangkat owner** — kartu yang sama › **Nyalakan notifikasi** › izinkan.
   - **iPhone / iPad:** hanya bisa dari ikon aplikasi di **Layar Utama** (iOS 16.4 ke atas). Kalau masih dibuka di tab Safari: tombol Bagikan ›
     Tambah ke Layar Utama, buka dari ikon itu, lalu nyalakan.
   - **Mac:** Chrome / Safari biasa bisa langsung. Aplikasi yang dipasang di Dock (Safari › Tambah ke Dock) yang sudah terbuka SEBELUM pembaruan masih
     versi lama — kartu Notifikasi belum ada. Tutup penuh (klik kanan ikon › Quit / ⌘Q) lalu buka lagi.
6. **Coba:** di tablet kirim pesan "uji notifikasi" (Menu › kartu Uang keluar & pesan › Pesan). HP owner harus berbunyi dalam beberapa detik
   walau aplikasinya ditutup. Ketuk notifikasinya → aplikasi terbuka di layar Uang.

## Biaya & data

- Blaze sudah aktif. Satu fungsi kecil yang hidup hanya saat ada permintaan dari tablet (puluhan kali sehari) — jauh di bawah jatah gratis
  Cloud Functions; Cloud Messaging gratis.
- Isi notifikasi (nama orang yang jaga, jenis, nominal, isi pesan) lewat layanan push Google / Apple. Fungsi tidak menulis data toko: ia hanya
  membaca permintaan baru dan token, lalu membuang token yang sudah mati.
- Mengubah fungsi nanti = jalankan langkah 4 lagi (Cloud Shell menyimpan folder `Toko-Beras-M.IQBAL`; cukup `cd Toko-Beras-M.IQBAL && git pull &&
  bash functions/pasang.sh`).

## Mematikan

- Satu perangkat: kartu yang sama › **Matikan**.
- Semua: Console Firebase › Functions › `kabarOwner` › hapus. Notifikasi dalam aplikasi tetap jalan.
