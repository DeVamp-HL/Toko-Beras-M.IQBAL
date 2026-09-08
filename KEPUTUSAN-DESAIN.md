# Keputusan desain — penyimpangan yang SUDAH disetujui

Sebelas keputusan sadar tentang **di mana sistem sengaja TIDAK mengikuti berkas desain**.
Semuanya sudah diperiksa dan disetujui pemilik. **Membetulkannya ke prototipe = merusak.**

Berkas ini ada di repo dengan sengaja. Perintah kerja (`PROMPT-*.md`) dan catatan bisnis
(`NN-*.md`) semuanya di-*gitignore* — repo ini kode saja. Akibatnya keputusan-keputusan di
bawah hidup cuma di satu mesin, dan siapa pun yang meng-*clone* akan melihat sistem
menyimpang dari desain **tanpa tahu bahwa itu disengaja**, lalu "membetulkannya".
Berkas inilah yang menutup celah itu.

Kalau ada elemen desain yang **bertabrakan** dengan salah satu butir di bawah: jangan
diam-diam memilih. Sebut di laporan, biarkan pemilik yang memutuskan.

---

## Yang berbeda dari desain, dan alasannya

1. **Setelan tidak bergembok** meski prototipe menggemboknya.
   Setelan satu-satunya pintu menyetel PIN; menggemboknya saat PIN belum disetel mengunci
   owner dari luar rumahnya sendiri.

2. **Pelanggan tetap bergembok** meski prototipe membukanya.

3. **Jaga Toko tetap terkunci.**

4. **Tangani lima kelompok**, bukan empat — tambahan "Mesin".
   Tombol **Buka** menandai *sudah dibuka*, bukan *beres*: yang menentukan beres tetap
   datanya sendiri.

5. **Pemasok: kolom cari tetap tampil.**

6. **Harga: kartu Jenis Beras lama disembunyikan di HP.**

7. **Belanja: keterangan wajib diisi**; prefix kelas `bj-`.

8. **Laporan: "Uang masuk/keluar" owner-saja.**

9. **Jejak disaring per jenis**, bukan per perangkat — Setelan sudah menyerahkan zonanya.

10. **Potret tersegel (Laporan, sumbu H/P) — DICORET.**
    Desain menjanjikannya dua kali; tidak ada penyimpanan apa pun yang menopangnya. Sistem
    **selalu** menghitung ulang dari data, dan tidak ada satu laporan pun yang tersimpan.
    Janji "ini potret yang tidak berubah" di atas angka yang dihitung ulang tiap kali
    dibuka adalah kebohongan yang paling sulit ketahuan.

11. **QR keaslian (Laporan, sudut lembar) — DICORET.**
    Ia menjanjikan pemeriksaan keaslian yang tidak punya pemeriksa. Sistem ini sudah bayar
    mahal untuk pelajaran sejenis: **aturan di repo adalah niat, bukan bukti, karena
    deploy-nya manual.** Janji keaslian yang tidak bisa ditepati **lebih berbahaya**
    daripada tidak ada janji — orang yang menerima laporannya akan mempercayainya justru
    karena ada QR-nya.

**Butir 10 dan 11 sejenis, dan bedanya dari butir lain di daftar ini penting:** cacat
seperti "Rework ke stok karung" dan "Buang (catat kerugian)" punya jalur yang **salah** dan
bisa dibetulkan. Dua ini **tidak punya jalur sama sekali**. Kalau keaslian dokumen memang
mau dibuktikan kelak, itu **gelombang sendiri dengan penyimpanannya lebih dulu** — bukan
gambar QR yang tidak menunjuk ke mana-mana.

---

## Cara memakai berkas ini

- Menambah butir: hanya sesudah pemilik menyetujuinya, dan **sertakan alasannya**. Daftar
  tanpa alasan akan dicabut orang berikutnya yang merasa sedang merapikan.
- Mencabut butir: berarti sistem kembali mengikuti desain di titik itu. Itu keputusan
  pemilik, bukan keputusan yang boleh diambil sambil mengerjakan hal lain.
- Butir bertanda **DICORET** artinya elemen desainnya **tidak dibangun sama sekali** —
  bukan dibangun lalu disembunyikan. Jangan cari kodenya; tidak ada.
