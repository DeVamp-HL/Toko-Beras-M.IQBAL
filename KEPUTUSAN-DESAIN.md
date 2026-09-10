# Keputusan desain — penyimpangan yang SUDAH disetujui

Delapan belas keputusan sadar tentang **di mana sistem sengaja TIDAK mengikuti berkas desain**.
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

12. **Harian tidak menawarkan "dibayar pakai apa" (Laci toko / Uang pribadi), meski berkas
    desainnya menyebut sumbu itu "tulang halaman ini".**
    Harian cuma punya **satu sumbu pertanyaan** — *untuk siapa belanjanya* (Toko / Owner).
    Sel `tokoDompet` (belanja **toko** yang dibayar **dompet pribadi**) butuh **dua** sumbu
    sekaligus, dan memasang sumbu kedua di layar satu-sumbu membuat empat kombinasi yang
    tiga di antaranya harus ditolak di tempat. Pintunya sengaja ditaruh di layar **Belanja**,
    yang memang dibangun sebagai kisi 2×2 (untuk siapa × uang dari mana) dan sudah melahirkan
    kolom utang toko ke owner di data dan neraca.

    Akibatnya kartu akibat di Harian punya **dua** baris, bukan tiga: baris "Utang toko ke
    owner" tidak pernah tergambar di sana. Itu benar — di Harian utang itu memang tidak bisa
    lahir.

    Penolakan ini sudah tertulis panjang sebagai komentar kode di `index.html` (dekat
    `kategoriHarianAktif`), tapi komentar tidak ikut ter-*clone* sebagai keputusan. Dicatat di
    sini supaya orang berikutnya tidak "melengkapi" Harian dan diam-diam membuat satu layar
    menjawab dua pertanyaan dengan satu tombol.

13. **Tutup Hari: tiga dari lima baris "Pagar" sengaja TIDAK menggembok** — sisihan amplop,
    hal menggantung, dan opname gudang. Ketiganya mengembalikan `ok: true` tanpa syarat apa
    pun; yang benar-benar bisa menolak cuma pagar 2 (kas & selisih) dan pagar 5 (setoran
    melebihi isi laci).

    **Kenapa tidak digerbangkan, dan kenapa ini beda dari gerbang antrean Tutup Buku** —
    dua perkara yang terlihat kembar tapi berpisah di satu titik yang menentukan:

    | | antrean tunda | Pagar 1, 3, 4 |
    |---|---|---|
    | kondisinya | **sudah ada**, sudah dihitung, sudah tergambar dengan tanda `!` | **belum ada sama sekali** |
    | menambahkannya berarti | memakai fakta yang sudah diukur | **mengarang tiga aturan baru** |
    | kalau macet | ritual setahun sekali tertunda | **tutup hari gagal, saldo awal besok salah** |

    Menggerbangkan yang tiga itu adalah **keputusan kebijakan tentang kapan toko boleh
    menutup harinya**, dan itu jatuh tiap malam. Preseden yang berlaku di sini `hppBolong`
    (pemeriksaan yang tidak menggembok, tapi mengaku di labelnya sendiri), bukan antrean.

    **Yang DIKERJAKAN sebagai gantinya:** berhenti menggambarnya seperti gerbang. Kelimanya
    dulu memakai `✓` yang sama di panel bernama "Pagar" — satu lambang, dua arti. Sekarang
    dua tanda: `✓` untuk yang benar-benar memeriksa, titik netral untuk "sudah dilewati",
    plus satu baris legenda. Panelnya **tetap** bernama Pagar: di dalamnya memang ada pagar
    sungguhan, dan menamai ulang seluruh panel akan menurunkan dua yang asli demi menemani
    tiga yang bukan.

    Ini **penundaan sadar, bukan cacat**. Tanpa butir ini, sapuan berikutnya akan
    "membetulkannya" dengan mengarang tiga kondisi yang belum pernah diputuskan siapa pun.


14. **Sack Utuh menerima SETENGAHAN** — 0,5 / 1,5 / 2,5 sack — meski desain menyatakan sack
    utuh bilangan bulat. Steppernya melangkah 0,5 dan kolomnya menerima koma
    (`WZ_PETA_JUMLAH`, 14513-14517); langit-langitnya dibulatkan ke bawah ke kelipatan 0,5
    supaya stok tidak pernah minus — sisa 629,84 kg / 50 = 12,596 jadi **12,5** sack, bukan
    12,59 (`stokMaksJalur`, 13129-13134).

    **Kenapa ini penting lebih dari kelihatannya:** halaman desain membangun seluruh
    argumennya di atas sack yang bulat — "begitu sacknya dibuka, dia berhenti jadi sack",
    karena itu setengah karung dialihkan ke Repacking atau Literan. Butir ini **mencabut
    alasan itu**. Toko sudah berjalan dengan setengahan; mengembalikannya ke bulat bukan
    mempercantik, tapi **mengubah cara penjualan dicatat**.

    **Saksinya:** dua komentar kode, 13129 dan 14514, dua-duanya menyebut "permintaan
    pemilik"; yang di 13129 bertanggal **21 Agustus 2026** dan menyebut contoh angkanya.
    Sebelum butir ini, aturannya hidup HANYA di sana — persis celah yang berkas ini dibuat
    untuk menutup.

15. **Nominal → liter dibulatkan KE BAWAH** (`Math.floor`, dengan epsilon `1e-9` supaya tahan
    galat pecahan biner), bukan `Math.round` seperti desain — `wzLiterDariNominal`, 14580-14583.
    Alasannya: yang tercatat **tidak boleh lebih besar dari uang yang disebut pembeli**.
    Selisihnya tidak disembunyikan — baris konversi mengakuinya sendiri ("Rp200 lebih sedikit
    dari yang diketik"). Untuk contoh desain (Rp200.000 @ Rp13.500) hasil floor dan round
    kebetulan sama; di harga lain keduanya berbeda 0,1 L.

16. **Jalur jual ada LIMA, bukan empat** — keempat jalur desain plus **Retur**
    (`wzPilihJalur('retur')`, 14919). Berkas desainnya sendiri mengakui `#halamanJual` punya
    lima kolom lalu memilih menggambar empat. Retur memakai form lama apa adanya lewat kelas
    `.wz-retur` (CSS 2982-2984); mencabutnya berarti menghapus satu-satunya pintu retur di HP.

17. **Ada kolom angka KEDUA yang tidak ada di desain** — harga satuan boleh **diketik langsung**
    untuk nego (`#wzHargaInput` di `#wzNegoBlok`, 14743-14761; `wzHargaDiketik` 14788,
    `wzNegoUbah` 14306), dengan tombol ±500 tetap ada. Desain hanya punya satu kolom angka.
    Nego adalah perbuatan sehari-hari di toko beras; tanpa kolom ini harga nego harus dihitung
    mundur jadi jumlah, dan itu yang dulu memisahkan jumlah dari uang.


18. **Jual memakai WADAH SATU HALAMAN dengan bagian-bagian wizard — bukan wizard bertanya
    satu-satu, dan bukan pula form satu-halaman lama.** Ini keadaan KETIGA, dan ia lahir
    dari perbandingan gambar-lawan-gambar antara prototipe dan sistem, 10 September 2026.

    **Apa yang sebenarnya berbeda.** Selama tiga gelombang tiap ELEMEN Jual dicocokkan ke
    desain sampai habis, dan layarnya tetap tidak terlihat seperti rancangan. Sebabnya bukan
    bagian-bagiannya melainkan wadahnya: rancangan `Jual - Gabungan` menaruh SEMUANYA di satu
    gulungan — jalur, rak, "Berapa", struk, cara bayar — sedangkan sistem bertanya satu per
    satu dengan tombol "← balik". Memasang bagian yang benar ke bangunan yang berbeda tetap
    menghasilkan bangunan yang berbeda.

    **Yang dipilih.** Cangkang wizard DIPERTAHANKAN — kartu, rak beras, chip takaran, struk
    hidup, saklar L⇄Rp, dasar harga, semuanya tetap milik langkahnya masing-masing dan nol
    yang dibuang. Yang berhenti cuma MENYEMBUNYIKANNYA satu per satu: seluruh rantai langkah
    digambar bertumpuk di satu halaman, tiap bagian masih bisa diubah di tempat.

    **Kenapa bukan A (pertahankan wizard apa adanya):** rupanya tidak akan pernah menjadi
    rancangan itu, dan gelombang berikutnya akan mengejar bayangan yang sama lagi.
    **Kenapa bukan B murni (bangun ulang jadi form satu-halaman):** form ≥700px memang punya
    susunannya, tapi kulitnya desktop lama — sidebar, kartu lebar, skala huruf desktop —
    bukan Kaca Emas. Mengambilnya utuh berarti membuang rupa yang sudah benar.

    **Yang TIDAK diketahui, dan sengaja ditulis di sini sebagai lubang:** *kenapa wizard dulu
    dipasang.* Tidak ada satu baris pun di repo yang menyebutkan alasannya — cuma satu
    komentar HTML yang menyatakan keberadaannya. Kalau ternyata ada alasan lapangan (jempol,
    salah pencet, kecepatan di jam ramai), alasan itu mengubah butir ini dan wajib ditulis
    ke sini. Butir ini mencatat KEPUTUSANNYA, bukan berpura-pura tahu sebab aslinya.

---

## Cara memakai berkas ini

- Menambah butir: hanya sesudah pemilik menyetujuinya, dan **sertakan alasannya**. Daftar
  tanpa alasan akan dicabut orang berikutnya yang merasa sedang merapikan.
- Mencabut butir: berarti sistem kembali mengikuti desain di titik itu. Itu keputusan
  pemilik, bukan keputusan yang boleh diambil sambil mengerjakan hal lain.
- Butir bertanda **DICORET** artinya elemen desainnya **tidak dibangun sama sekali** —
  bukan dibangun lalu disembunyikan. Jangan cari kodenya; tidak ada.
