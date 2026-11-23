# Teks halaman aplikasi di Google Play

Disalin owner ke Play Console › **Grow users › Store presence › Main store listing** (bahasa: Indonesia – id-ID).
Untuk **uji internal** halaman ini tidak wajib lengkap — penguji memasang lewat tautan undangan. Disiapkan supaya siap bila Play Console memintanya.
Batas panjang Play dijaga `alat-uji/uji_google_play.py` (judul ≤ 30, pendek ≤ 80, lengkap ≤ 4000 huruf). Tanpa nama orang, tanpa angka rupiah toko.

## Nama aplikasi (≤ 30)

<!-- judul -->
Kasir Toko Beras
<!-- /judul -->

## Deskripsi pendek (≤ 80)

<!-- pendek -->
Kasir tablet toko beras: jual, stok, bon, struk, dan laporan harian.
<!-- /pendek -->

## Deskripsi lengkap (≤ 4000)

<!-- lengkap -->
Aplikasi kasir untuk tablet di meja toko beras. Dipakai pemilik toko dan penjaga yang akunnya dibuat oleh pemilik — bukan aplikasi umum, tidak bisa dipakai tanpa akun toko.

Yang bisa dilakukan:
• Jual: keranjang per merek dan ukuran, eceran literan, harga grosir per tingkat pelanggan, bayar tunai, QRIS, transfer, atau bon.
• Struk: cetak lewat printer struk toko (USB atau jaringan), dengan kode QR nomor nota untuk membuka nota kembali.
• Stok: barang masuk dari pemasok, kemasan ulang, wadah literan, hitung fisik dan susut.
• Bon dan tagihan: utang pelanggan, faktur jatuh tempo, pembayaran sebagian, surat jalan antar barang dengan tanda tangan penerima.
• Tutup hari: hitung laci dan timbang, langsung dilaporkan ke pemilik.
• Kabar toko: notifikasi persetujuan dan pesan antara pemilik dan tablet.
• Perangkat tablet: pemindai kode batang, kartu NFC pelanggan, lampu status, sidik jari pemilik.

Data toko disimpan di server milik pemilik toko (Firebase). Tanpa iklan, tanpa pelacak pihak ketiga.
<!-- /lengkap -->

## Isian lain

| Isian | Jawaban |
|---|---|
| Kategori aplikasi | Bisnis |
| Jenis | Aplikasi · Gratis |
| Email kontak | email akun pengembang owner (diisi owner di Play Console — tidak ditulis di repo) |
| Situs web | `https://devamp-hl.github.io/Toko-Beras-M.IQBAL/privasi.html` (boleh dikosongkan) |
| Kebijakan privasi | `https://devamp-hl.github.io/Toko-Beras-M.IQBAL/privasi.html` |
| Ikon (512 × 512) | `docs/google-play/ikon-512.png` |
| Grafis unggulan (1024 × 500) | `docs/google-play/grafis-unggulan-1024x500.png` |
| Tangkapan layar | **owner ambil sendiri dari CPad** (minimal 2; tablet 7"/10" boleh) — pakai layar yang TIDAK menampilkan nama pelanggan, nomor HP, atau angka uang toko (mis. layar masuk / Menu kosong). Untuk uji internal tidak wajib. |
