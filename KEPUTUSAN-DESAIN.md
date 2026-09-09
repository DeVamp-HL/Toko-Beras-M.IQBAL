# Keputusan desain — penyimpangan yang SUDAH disetujui

Tiga belas keputusan sadar tentang **di mana sistem sengaja TIDAK mengikuti berkas desain**.
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

---

## Cara memakai berkas ini

- Menambah butir: hanya sesudah pemilik menyetujuinya, dan **sertakan alasannya**. Daftar
  tanpa alasan akan dicabut orang berikutnya yang merasa sedang merapikan.
- Mencabut butir: berarti sistem kembali mengikuti desain di titik itu. Itu keputusan
  pemilik, bukan keputusan yang boleh diambil sambil mengerjakan hal lain.
- Butir bertanda **DICORET** artinya elemen desainnya **tidak dibangun sama sekali** —
  bukan dibangun lalu disembunyikan. Jangan cari kodenya; tidak ada.
