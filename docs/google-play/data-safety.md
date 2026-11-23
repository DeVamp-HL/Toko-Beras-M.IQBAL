# Jawaban formulir Google Play (App content)

Dipakai owner di Play Console › **Policy and programs › App content**. Untuk **uji internal** bagian ini umumnya belum diminta; bila Play Console menahan
peluncuran karena "App content" belum lengkap, isi dengan jawaban di bawah. Jawaban disusun dari apa yang aplikasi SUNGGUH kirim ke server (diperiksa di kode
`baru/` 23 Nov 2026) — lebih baik menyatakan terlalu banyak daripada kurang. Bila fitur baru mengirim jenis data lain, perbarui berkas ini dan `privasi.html`.

## Kebijakan privasi

`https://devamp-hl.github.io/Toko-Beras-M.IQBAL/privasi.html` (berkas `privasi.html` di akar repo, terbit lewat Pages).

## Akses aplikasi (App access)

Semua fungsi butuh masuk akun toko. **Uji internal tidak ditinjau Google**, jadi tidak perlu memberi akun ke peninjau. Bila suatu hari pindah ke uji
tertutup, Google meminta akun uji untuk peninjau — siapkan akun yang TIDAK bisa membaca data toko sungguhan (mis. di proyek Firebase contoh), jangan akun toko.

## Iklan

Tidak ada iklan.

## Data safety

| Pertanyaan | Jawaban |
|---|---|
| Apakah aplikasi mengumpulkan atau membagikan jenis data pengguna yang wajib dilaporkan? | **Ya** |
| Apakah semua data dienkripsi saat dikirim? | **Ya** (HTTPS / Firebase) |
| Apakah pengguna bisa meminta datanya dihapus? | **Ya** — lewat pemilik toko; alamat: `…/privasi.html#hapus` |
| Dibagikan ke pihak ketiga? | **Tidak** (Firebase/Google = penyedia layanan untuk pemilik toko, bukan "berbagi" menurut definisi Play) |
| Diproses sementara saja (ephemeral)? | Tidak |
| Wajib atau boleh dipilih? | Wajib (alat kerja toko) |

Jenis data yang **dikumpulkan** (semuanya untuk tujuan **Fungsi aplikasi**; akun juga **Pengelolaan akun**; tidak ada analitik, iklan, pemasaran,
personalisasi, pencegahan penipuan):

| Kelompok Play | Jenis | Isi sebenarnya |
|---|---|---|
| Info pribadi | Nama | nama penjaga, nama pelanggan & pemasok yang dicatat toko |
| Info pribadi | Alamat email | email akun masuk (Firebase Authentication) |
| Info pribadi | ID pengguna | id akun Firebase (uid) pada tiap catatan |
| Info pribadi | Alamat | alamat antar di surat jalan / data pelanggan |
| Info pribadi | Nomor telepon | nomor HP/WA pelanggan & pemasok yang dicatat toko |
| Info keuangan | Riwayat pembelian | nota penjualan per pelanggan |
| Info keuangan | Info keuangan lain | bon, utang-piutang, pembayaran, tutup hari |
| Foto dan video | Foto | foto kertas bon / nota, foto lembar surat jalan & tanda tangan penerima |
| Pesan | Pesan lain dalam aplikasi | pesan & persetujuan antara pemilik dan tablet |
| Aktivitas aplikasi | Interaksi aplikasi | log aktivitas (siapa mengerjakan apa, kapan) |
| Aktivitas aplikasi | Konten buatan pengguna lain | catatan pada nota, alasan, balasan |
| Info & performa aplikasi | Diagnostik | status perangkat (terakhir aktif, versi, kelancaran layar) |
| ID perangkat atau lainnya | ID perangkat atau lainnya | token notifikasi Firebase Cloud Messaging per perangkat |

**Tidak** dikumpulkan: lokasi, kontak telepon, kalender, SMS/log panggilan, berkas & dokumen lain, audio, kesehatan, data biometrik (sidik jari diproses
sensor Android di perangkat; aplikasi hanya menerima "cocok / tidak"), riwayat penelusuran, daftar aplikasi terpasang.

## Rating konten (kuesioner IARC)

Kategori: **Semua jenis aplikasi lain** (alat bisnis). Kekerasan, seksual, bahasa kasar, narkoba, judi: **Tidak**. Pengguna berinteraksi / bertukar konten:
**Ya** (pesan internal pemilik ↔ tablet). Berbagi lokasi: **Tidak**. Pembelian digital: **Tidak**.

## Target audiens

18 tahun ke atas. Bukan untuk anak.

## Deklarasi lain

| Deklarasi | Jawaban |
|---|---|
| Aplikasi berita | Tidak |
| Aplikasi pemerintah | Tidak |
| Fitur keuangan (Financial features) | Tidak menyediakan layanan keuangan (pinjaman, bank, investasi, kripto). Mencatat penjualan & bon toko sendiri. |
| Aplikasi kesehatan | Tidak |
| ID iklan (Advertising ID) | Tidak dipakai |
| Izin sensitif (SMS, log panggilan, semua berkas, aksesibilitas, lokasi latar) | Tidak ada — izin yang dipakai: internet, notifikasi, Bluetooth (printer), NFC, USB, sidik jari |
