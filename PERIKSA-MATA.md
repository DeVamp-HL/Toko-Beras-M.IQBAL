# Periksa mata — yang tidak bisa dibuktikan kode

Daftar **kumulatif** untuk gelombang "samakan UI dengan desain". Satu berkas, bukan tersebar
di pesan commit.

Isinya HANYA hal yang butuh mata: tata letak di lebar HP, kepadatan, keterbacaan, apakah dua
sasaran sentuh bersinggungan, apakah empat jenis uang benar-benar terlihat beda. Yang bisa
dibuktikan kode — logika cabang, `disabled`, ekspor `window`, cacah elemen,
`toLocaleString('id-ID')`, identitas mesin, id menggantung — **tidak masuk sini**; itu
dikerjakan dan dibuktikan tanpa peramban.

**Cara memakainya:** buka di HP di lebar aslinya (iPhone 13, 390x844) dengan data asli.
Butir yang lulus dicoret; yang tidak cocok disebut apa adanya. Simulasi lebar jendela di
komputer TIDAK menggantikan ini — dan itu justru sebabnya berkas ini ada.

---

## Jual  ·  `3e5c761`  ·  10 Sep 2026

| # | elemen | apa yang harus dilihat | keadaan |
|---|---|---|---|
| J1 | Kartu **dasar harga** (`.wz-dasar`) di langkah "Berapa" | Muat satu-dua baris, atau menghimpit saklar di bawahnya? Tinta cukup terbaca di atas kartu kaca? | sudah dilihat di kotak pasir 390px — **rapi**; belum dilihat dengan data toko |
| J2 | **Delapan chip nominal** (20rb·50rb·100rb·200rb·**250rb**·**300rb**·500rb·**620rb**) | Hanya muncul di **Literan + mode RUPIAH**. Masih satu baris menggulir yang rapi, atau sudah berdesakan? Tiga yang tebal itu baru. | **BELUM TERLIHAT** — kotak pasir tidak punya harga literan, jadi RUPIAH mati di sana |
| J3 | Nota `Nominal dibagi Rp…/liter, dibulatkan ke bawah ke 0,1 L. Yang tercatat tetap liter` | Terbaca, atau terlalu kecil/pudar? Muncul bersama J2. | **BELUM TERLIHAT** — sebab sama dengan J2 |
| J4 | Judul baris chip (`Takaran yang sering` / `Nominal yang sering`) | Berganti kata saat saklar dipindah ke RUPIAH? | sisi "Takaran" sudah dilihat; sisi "Nominal" belum |
| J5 | Baris **selisih dua katalog** (tinta oksida terang, di dalam `.wz-dasar`) | Muncul HANYA di Sack Utuh yang harganya beda antara Katalog Kemasan dan Karung. Kalau muncul: **angkanya benar?** Ini pertanyaan kebijakan "per karung atau per kg", bukan pertanyaan tampilan. | **BELUM TERLIHAT** — perlu merk yang dua katalognya berselisih |
| J6 | Chip **`0,5 sack`** di jalur Sack Utuh | Ini sengaja (butir 14). Kalau di layar bikin bingung, sebut — itu keputusan, bukan cacat. | sudah dilihat — tergambar |
| J7 | Saklar `LITER / RUPIAH` | Dua tombol 44px bersebelahan: jempol pernah kena yang salah? RUPIAH benar-benar mati (bukan cuma abu) saat merk tanpa harga liter. | mati-nya sudah diverifikasi; **bersinggungan atau tidak — belum** |
| J8 | Empat jenis uang di satu layar Jual | kas · omzet · margin kotor · laba bersih benar-benar terlihat beda, atau masih mirip-mirip? | belum |

---

## Cara menambah layar berikutnya

Satu tabel per layar, dengan nomor berawalan huruf layarnya (Jual = J, Arus Kas = A, dst).
Butir masuk sini HANYA kalau jawabannya tidak bisa diambil dari kode. Kalau ragu: coba dulu
buktikan lewat kode; kalau bisa, ia bukan butir di sini.
