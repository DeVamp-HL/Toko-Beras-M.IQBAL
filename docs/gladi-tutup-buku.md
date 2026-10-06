# Gladi tutup buku di server tiruan (Firebase Emulator)

Mulai 7 Okt 2026. Tujuannya: sebelum owner menjalankan tutup buku 2026 sungguhan pada 1 Jan 2027 tanpa Claude, ritual penuh dan aturan servernya
sudah pernah dijalankan di server tiruan, lewat layar /baru/ yang asli.

## Tempat jalannya

**Hanya di runner GitHub Actions**, lewat workflow **Gladi tutup buku** (`.github/workflows/gladi-tutup-buku.yml`). Alasannya ada di `CLAUDE.md`:
peramban dan emulator tidak boleh dijalankan di Mac owner. Workflow ini bisa dijalankan manual dari tab Actions, dan berjalan sendiri di PR yang
menyentuh tutup buku, kunci periode, layar Uang, aturan server, atau sambungan Firebase.

Di Mac hanya boleh menjalankan pemeriksaan yang tidak menyalakan peramban:

    python3 alat-uji/uji_server_tiruan.py            # + --kontrol
    python3 alat-uji/gladi_data_contoh.py --periksa  # + --kontrol
    python3 alat-uji/gladi_tutup_buku.py --periksa-salinan

`alat-uji/gladi_tutup_buku.py` menolak jalan di luar GitHub Actions.

## Isinya

- **Server tiruan**: Firestore + Auth emulator dengan aturan `firestore.rules` repo. Proyeknya `demo-gladi-toko`, tanpa kredensial, dan tidak
  bisa menyentuh data toko.
- **Data contoh**: dibuat `alat-uji/gladi_data_contoh.py` dengan benih tetap. Isinya ±17 rb dokumen, 8 Agu–31 Des 2026, dengan bentuk dokumen
  yang sama dengan cadangan. Semua nama dan angka rupiahnya karangan. Cadangan asli tidak pernah dibaca dan tidak pernah dikirim ke runner. Ada dua
  varian:
  - `macet`: ada 23 hari berjualan tanpa tutup hari, polanya sama dengan keadaan toko 6 Okt.
  - `bersih`: semua gerbang beres.
- **Akun**: owner contoh (`owner@…`, dikenali aturan lewat email) dan satu karyawan contoh beserta dokumen `aksesAkun`-nya. Sandi dibuat ulang tiap
  run dan tidak pernah dicetak.
- **Jalan masuk /baru/ ke emulator**: `?emulator=127.0.0.1:8080`, diatur di `baru/js/data/server-tiruan.js`. Jalan ini hanya berlaku kalau
  halamannya dibuka dari `localhost`/`127.0.0.1` dan alamat emulatornya juga lokal. Selama aktif, layar memasang bilah merah **SERVER TIRUAN**.
  CSP situs tidak dilonggarkan. Yang menambahkan alamat emulator ke `connect-src` hanya salinan uji.

## Skenario

| skenario | data | jam halaman | yang dibuktikan |
|---|---|---|---|
| `latihan` | macet | 31 Des 2026 21.45 | Muat penuh. LATIHAN tujuh langkah sampai "Latihan selesai" tanpa satu pun tulisan ke server. Denyut perangkat dan katalog kasir tidak dihitung, karena keduanya tulisan latar. |
| `gerbang` | macet | 1 Jan 2027 15.30 | SUNGGUHAN boleh dipilih. Gerbang g1 "23 hari belum ditutup" tampil memblokir. Tombolnya berbunyi "1 hal belum beres — bereskan dulu". Mengetuknya tidak memajukan langkah dan tidak menulis apa pun. |
| `ritual` | bersih | 1 Jan 2027 15.30 | SUNGGUHAN sampai paraf, lalu kunci. Server menolak kiriman saldo pembuka ke-2, lalu kartu **lanjutkan / batalkan** muncul. BATALKAN sebelum penanda. Mulai lagi, lalu arsip ditolak server dan kartu **lanjutkan / batalkan** muncul lagi. LANJUTKAN sampai arsip habis. BATALKAN sesudah penanda: isi server sama dengan sebelum ritual (dokumen dan isinya). Mulai lagi sampai **selesai**. |

Untuk memotong ritual di tengah, aturan emulator diganti sementara dengan salinan `firestore.rules` yang ditambah satu baris penolak. Setelah itu
teks repo dipasang lagi. Berkas `firestore.rules` sendiri tidak diubah.

## Laporan

Ringkasan tiap run ada di halaman ringkasan run, lengkap dengan tabel per langkah. Artefak `laporan-gladi-tutup-buku` berisi JSON lengkap dan log
emulator. Angka di tiap langkah:

- **baca**: dokumen yang diterima pendengar halaman dari server. Dihitung lewat penghitung di salinan SDK uji. Pembacaan `get()` di dalam aturan
  tidak ikut terhitung, karena `:ruleCoverage` emulator hanya berisi posisi ekspresi, tanpa jumlah. Perkiraan jumlah `get()` ada di audit kesiapan.
- **tulis / hapus**: selisih isi emulator antara sebelum dan sesudah langkah, diambil lewat REST.

Ketiganya dijumlah dan dibandingkan dengan batas Spark per hari: 50 rb baca, 20 rb tulis, 20 rb hapus.

Keterbatasan:

- **Jam server emulator adalah jam runner, bukan jam halaman.** Pemeriksaan kunci periode di aturan (`get()` bulan lampau) karena itu dinilai
  dengan bulan runner.
- **Antrean WebChannel emulator dibatasi 10.000 pesan per kanal.** Run 7 Okt memakai data 17 rb dokumen. Hasilnya: "too many pending messagings in
  the back channel (10001)", kanal Listen diputus berulang, dan halaman tidak pernah menerima data. `--help` emulator tidak punya setelan untuk
  batas ini, dan server sungguhan tidak punya batas itu. Karena itu data gladi dibuat ±9 rb dokumen (`GLADI_SKALA` 0,65, bisa diubah dari input
  workflow). Ringkasan menambahkan baris *perkiraan skala toko*: hasil gladi × (17.000 ÷ dokumen arsip gladi).
- **Tiap skenario jalan di emulator sendiri.** Emulator tetap mengirimi sesi halaman yang sudah ditutup sampai kanalnya kedaluwarsa, sehingga
  skenario berikutnya bisa terganggu. Laporan per skenario digabung di akhir (`--gabung`). Tiap langkah mencatat berapa kali antrean emulator
  penuh. Nilai itu **wajib 0 sampai muat penuh selesai**, karena kalau penuh saat muat, halaman tidak pernah menerima data. Sesudah muat penuh
  angkanya hanya dilaporkan. Asalnya sesi kanal yang sudah ditinggal halaman: SDK menyambung ulang dengan token lanjut, sedangkan emulator terus
  mengirimi kanal lama. Run 7 Okt mencatat jutaan baris di satu run dan nol di run lain, dan di keduanya semua cek isi tetap lulus.

## Sesudah Paket A

Paket A mengubah gerbang tutup buku, misalnya putusan per tanggal. Yang perlu disesuaikan ada di dua tempat, keduanya di `alat-uji/gladi_tutup_buku.py`:

- fungsi langkah di `SKENARIO_JS` (`sampaiParaf`, `gerbangDiblokir`, dan seterusnya);
- urutan langkah di `SKENARIO`.

Cek per skenario ada di `cek_*`.
