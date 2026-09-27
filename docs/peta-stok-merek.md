# Peta stok & merek — putaran 27, Tahap 0

**Status (27 Sep 2026): peta selesai, belum ada perubahan perilaku.** Tidak ada syarat berhenti yang terpicu: kelima bagian bisa dibangun
**tanpa jenis dokumen baru** dan **tanpa menyentuh 28 mesin beku**, dan penyusun katalog kasir (`susunIsiKatalogKasir`) tidak perlu diubah.
Yang perlu izin owner sebelum dibangun: beberapa **kolom baru** di dokumen yang sudah ada (§11), **tempat penanda arsip** (§11), dan **nama wadah
yang sekaligus merek karung** (§12).

Sumber: kode di `main` 4bdb5b9 (sesudah 25c), `firestore.rules` v4, dan cadangan toko 27 Sep 2026 sesudah 25c (di `_privat/`, tidak masuk repo).
Angka di dokumen ini kg dan jumlah catatan, **bukan rupiah**. Nama orang dan nama pemasok tidak disebut.

## 1. Identitas nama — nama barang adalah kuncinya

Tidak ada id produk. Di seluruh sistem kuncinya **teks nama** (karung: nama merek; kemasan: `nama|ukuran`; wadah: nama wadah). Sejak 25b
`index.html` hanya-baca, jadi semua penulis ada di `/baru/`.

| Tempat | Kunci | Penulis `/baru/` |
|---|---|---|
| Buku stok karung (`hitungStokKarungPerMerk`, beku) | `batchMasuk.merkList[].merk`; dikurangi `penjualan.merkSumber`, `produksiKemasan.sumberList[].merk`/`merkSumber`, `penyesuaianStok.merk`; ditambah `produksiKemasan.merkTujuan` (jadi karung utuh), `retur.merkSumber` (utuh) | Barang masuk, Jual, Adukan, Cocokkan, Wadah (pindah buku takar) |
| Buku kemasan (`hitungStokKemasan`, beku) | `produksiKemasan.namaProduk` + `ukuranKemasan` (`kunciKemasan`); dikurangi `penjualan` jenis kemasan, `sumberKemasanList` | Adukan, Jual, Cocokkan |
| Katalog harga | `katalogHargaKarung` id = merek (per kg) · `katalogHargaLiteran` id = merek (per liter) · `katalogHargaKemasan` merek + ukuran (per unit; 50/25 = harga karung utuh) | Harga › Katalog (draf → terbit satu batch) |
| Label rak | `aturanToko/hargaLabel.daftar[].k` = `merek|satuan` | terbit harga |
| Katalog HP kasir | `ringkasanKasir/aktif.merkKarung[].merk`, `.kemasan[].kunci` | `firebase.js` (25c), isinya `susunIsiKatalogKasir` |
| Laba | `penjualan.hppTotalSaatJual` per baris (dikunci saat jual) — nama tidak dipakai | Jual |
| Tempat simpan | `pengaturan/tempatSimpan.peta` `K:<nama>` / `M:<nama|ukuran>` | Stok › Tempat |
| Jenis beras | `pengaturan/jenisBeras.peta[<nama>]` | Harga › Katalog (25c) |
| Wadah literan | `wadahLiteran.wadah` (nama wadah), `.merk` (nama karung), `takar.sumber[].merk` | Stok › Wadah, Jual (isi ulang) |
| Rasio liter→kg | `RASIO_KONVERSI[<nama>]` (tetap di kode), selain itu 0,82 | — |

**Nama baru muncul** (barang masuk dengan nama yang belum pernah ada): buku stok langsung punya nama itu (modal = kedatangan itu). Di Jual ia baru
tampil sebagai karung kalau ada harga karung utuh / per kg, sebagai literan kalau ada harga liter, sebagai repack kalau ada harga per kg. Katalog
harga langsung menampilkan barisnya sebagai "belum ada harga" (termasuk **baris literan** — lihat §7). Katalog kasir langsung memuatnya (harga 0).
Label baru ada sesudah harga terbit. Jenis beras ditebak dari namanya (§8). Tempat simpan kosong.

## 2. Modal — rata-rata tertimbang SEJAK AWAL, bukan per kedatangan

`hitungStokKarungPerMerk` (beku): modal per kg = Σ(nilai tiap kedatangan nama itu, termasuk bagian upah bongkar lewat `hitungHppMerkDalamBatch`)
÷ Σ kg kedatangan. **Seluruh riwayat**, bukan sisa stok. Dua kedatangan senama dengan harga beda (misalnya satu karung 700 rb/50 kg lalu 800 rb/50 kg)
langsung melebur jadi satu angka; kg yang keluar tidak mengubah rata-ratanya. Selisih cocokkan lewat `terpakai`, jadi modal tidak tersentuh.
"Harga beli terakhir" (`hargaTerakhirPerKg`) disimpan terpisah sebagai pembanding.

Dipakai oleh: `hppTotalSaatJual` tiap baris nota (`/baru/` `bangunBaris`, dikunci saat jual → laba `hitungLabaRentang`), nilai stok neraca
(`hitungNeraca.nilaiSack`), nilai rupiah cocokkan (`nilaiRp` dikunci saat cocokkan → `barisSusutStok`), nilai bahan adukan, pindah buku takar
(`hppSumberPerKgDipakai`), katalog kasir (`hppPerKg`), layar HPP & katalog harga (modal).

→ **Bagian 2 (varian)** tidak mengubah rumus ini; ia hanya mencegah dua barang berbeda melebur di satu nama.

## 3. Cocokkan hari ini (Stok › Cocokkan, tab Beras (kg))

Satu angka per nama beras: layar menjumlah "karung × isi (50/25) + kg lepas" menjadi `kgFisik` untuk **seluruh** nama itu (tumpukan, karung
terbuka, dan isi wadah sekaligus). Baris yang punya wadah menampilkan rincian rantai stok sebagai bantuan, tapi yang disimpan tetap satu angka.

Dokumen: `penyesuaianStok {id, tanggal, jam, merk, kgSistem, kgFisik, selisihKg, alasan, nilaiRp, hppPerKgSaatOpname}` (+ atribusi). Mesin memakai
**hanya `selisihKg`** (lewat `terpakai`). Laba: sejak 1 Sep, `nilaiRp` negatif = baris "Susut & selisih stok" di laba bulan itu
(`barisSusutStok`); positif = stok naik tanpa mengubah modal. Kas & omzet tidak bergerak. Penjaga: selisih > batas % (bawaan 3 %) wajib alasan,
angka aneh, stok bertambah > ambang rupiah, sebagian, ganda < 10 menit — semuanya dua ketukan.

Di cadangan: 30 catatan; lima dari 25 Sep beralasan "salah hitung wadah literan yang dicampur" — satu angka untuk tumpukan + wadah campuran
membuat owner menebak nama mana yang harus disesuaikan.

→ **Bagian 1** tetap menulis `penyesuaianStok` yang sama; yang berubah hanya cara menghitung (tumpukan per karung utuh vs wadah per petak) dan
kolom penanda asalnya (§11).

## 4. Kemasan hasil adukan & jalur memecah kemasan

Kemasan jadi = `produksiKemasan {namaProduk, ukuranKemasan, jumlahUnit, hppPerUnit, sumberList, kgDipakai, sumberKemasanList, …}` (bentuk
`simpanProduksi`); modal per unit dari `bagiBiayaAdukan` (beku, dibagi menurut kg, sisa pembulatan ke baris terakhir → Σ persis).
Buku kemasan: modal rata-rata tertimbang per `nama|ukuran`.

**Jalur memecah sudah ada:** Adukan menerima **kemasan jadi 50/25 kg sebagai bahan** (`sumberKemasanList`, sejak 26 Agu). Membongkar
`X|50` × 1 menjadi `X|25` × 2 tanpa upah & tanpa kantong = satu adukan biasa; penolakan "lingkaran" hanya untuk nama+ukuran yang SAMA
(`X|50` → `X|50`), `X|50` → `X|25` lolos. Nilai: 1 × modal `X|50` dibagi dua ke dua unit `X|25` (Σ persis). `hitungStokKemasan` mengurangi
`X|50` lewat `unitDipakaiProduksi` tanpa menyentuh rata-ratanya.

Di cadangan: empat kemasan 50 kg bersisa; tiga punya harga 25 kg di katalog, satu tidak (usul = ½ harga 50 kg).

→ **Bagian 4** memakai jalur ini (produksi + penjualan dalam satu kiriman), tanpa dokumen baru.

## 5. Habis & hilang dari layar (hari ini)

| Layar | Nama beras stok 0 | Kemasan stok 0 |
|---|---|---|
| Jual | kartu karung/literan/repack TETAP tampil selama ada harganya, abu-abu "habis" | tetap tampil selama ada harganya, "habis" |
| Katalog harga | tiap nama di buku (termasuk 0) mendapat baris per kg **dan** per liter | baris selama pernah dibuat |
| Label rak | tugas label muncul saat harganya terbit | sama |
| Katalog kasir | `merkKarung` memuat **semua** nama di buku (juga 0) | `kemasan` memuat semua kunci |

Tidak ada cara menyingkirkan nama dari layar tanpa menghapus catatan. Di cadangan: 4 nama beras bersisa 0 kg, 1 kemasan bersisa 0.

## 6. Kunci periode

Semua dokumen yang akan ditulis putaran ini sudah bertanggal dan ada di `KP_KOLEKSI` (`penjualan`, `produksiKemasan`, `penyesuaianStok`,
`batchMasuk`) → penjaga pusat `jagaKunci` menolaknya di bulan terkunci; pembaliknya tetap cocokkan / retur HARI INI. `wadahLiteran`, `aturanToko`,
`pengaturan/jenisBeras`, dan katalog harga tidak dikunci (alat ukur & setelan, sama seperti sekarang). Arsip tidak mengubah catatan bertanggal.

## 7. Literan dari wadah — mesin memotong `merkSumber`, bukan nama tampil

`hitungStokKarungPerMerk`: baris `jenis 'literan'` memotong `stok[p.merkSumber].terpakai += p.totalKg`. `namaProduk` **tidak dipakai** mesin
stok, laba (`hppTotalSaatJual` per baris), maupun laju (`hitungLajuPakai` per `merkSumber`).

- **Satu baris menampilkan nama wadah tapi memotong merek asal: BISA** — `namaProduk` = nama wadah, `merkSumber` = merek asal.
- **Satu takaran dipecah jadi beberapa baris internal (satu per merek asal): BISA tanpa mengubah mesin.** Tiap baris berdiri sendiri di mesin; Σ
  `totalKg` = kg takaran, Σ `hargaTotal` = harga takaran, Σ `hppTotalSaatJual` = HPP tertimbang. Yang harus diajari (semuanya di `/baru/`, bukan
  mesin): penyusun nota (bagi kg & rupiah, sisa pembulatan ke baris terakhir, kantong literan hanya di satu baris), struk (baris internal
  digabung jadi satu baris bernama wadah), batalkan nota, rinci karcis, "Belanja terakhir", laku per harga di katalog, papan kapur.
- Gerbang mesin beku di prompt **tidak** terpicu: tidak ada mesin yang perlu diubah.

**Nama jual yang hari ini punya buku stok padahal nama wadah / kelas mutu** (cadangan 27 Sep sesudah 25c; tumpukan = buku − karung terbuka − isi
wadah menurut layar):

| Nama | Buku | Di wadah (W) | Karung terbuka senama | Tumpukan menurut layar |
|---|---|---|---|---|
| IR64 Apex | 151,96 kg | 19,8 (W1) | 6,4 | 125,8 |
| IR64 Ascent | 174,96 kg | 40,0 (W6) | — (W6 memegang karung Bahan campuran standar) | 135,0 |
| IR64 Elevate | 4,04 kg | 42,5 (W5) | 13,6 (yatim) | **−52,0** (buku kurang dari isi wadah) |
| IR42 Select | 127,96 kg | 38,8 (W4) | 21,2 | 68,0 |
| IR42 Value | 257,2 kg | 42,6 (W8) | 47,8 | 166,8 |

Tiga nama wadah lain — **Angsa** (716 kg), **Perahu Layar** (365,48 kg), **Pandan Wangi** (94,13 kg) — juga nama merek karung yang masuk lewat barang
masuk; lihat §12 pertanyaan 2.

Isi W5 "IR64 Elevate" sekarang sebagian besar beras Kumala yang **bukunya sudah dipindah** ke nama IR64 Elevate lewat takar (pilihan A, 22 Sep —
24 dokumen pindah buku di cadangan). Itulah sebab buku IR64 Elevate lebih kecil dari isi wadahnya.

**Kasir.** `kasir-darurat-nominal.html` tidak punya tuts literan bernama. `kasir.html` (alat owner) punya: tuts literan per nama di `merkKarung`
yang berharga liter, satu baris per penjualan dengan `merkSumber` = nama itu (71 baris literan tidak batal di cadangan, terakhir 19 Sep). Kasir tidak bisa
memecah takaran — lihat §10 risiko.

## 8. Jenis beras varian

`jenisUntukMerk` (salinan index.html): isi peta `pengaturan/jenisBeras` kalau ada kuncinya (termasuk `''`), selain itu `tebakJenisBeras(nama)`
(`^IR64`, Angsa, Perahu Layar → IR64; `^IR42`; `^Ketan Hitam`; `^Ketan`; Pandan Wangi; Beras Merah; Rojolele). Untuk nama varian:
`IR64 LL · Premium` → tebakan **IR64** (awalannya), tapi `LL · Premium`, `Kumala · Premium`, `NG · 27 Sep` → tebakan **kosong** (belum diisi).
Karena itu varian **wajib menulis kuncinya sendiri** di peta dengan jenis induknya (keputusan prompt: satu kunci baru di peta yang sama).

Tampil sekarang: Harga › Katalog (pil jenis + daftar "Jenis beras · N/M terisi"), Stok › Gudang ("Beras di buku per jenis", nama bersisa 0 tidak
ikut), Jual (baris saring rak per jenis). Keputusan owner 27 Sep: nonaktif = jenis per merek dikosongkan (`''`); mereknya tetap terdaftar.
`susunJenisBeras` menolak nama yang belum dikenal stok/kemasan/katalog karung — varian yang dibuat dari Harga sebelum barangnya masuk harus
ditulis lewat jalur varian, bukan lewat pil jenis.

## 9. Katalog kasir (sejak 25c)

`kkIsi()` = `susunIsiKatalogKasir()` (salinan huruf demi huruf `index.html`, dijaga `pindah_mesin.py`). Ditulis `firebase.js` 4 detik sesudah
**setiap** perubahan data (bukan daftar kejadian), hanya kalau isinya beda dari dokumen server, hanya dari perangkat owner yang semua koleksinya
dijawab server; terbit harga menyertakannya di kiriman yang sama (`kkSertakan` → `denganCacheSementara(…, kkIsi)`).

**Titik saring nama arsip:** di `kkIsi()`, pada HASIL penyusun, sebelum dokumen dibentuk. Menyaring DATA sebelum penyusun tidak aman: satu
`produksiKemasan` membawa beberapa nama sekaligus (`sumberList`), jadi membuang dokumen nama arsip ikut mengubah stok nama lain. Nama arsip
selalu bersisa 0, jadi membuang barisnya dari hasil = persis katalog seandainya nama itu tidak pernah ada. Fungsi salinan tidak disentuh;
`uji_katalog_kasir.py` tetap membandingkan `/baru/` dengan penyusun `index.html` (tanpa arsip: byte-sama; dengan arsip: byte-sama sesudah baris
nama arsip dibuang dari hasil lama).

**Bagian 5 dan isi katalog:** harga per liter wadah disimpan di tempat yang sama dengan sekarang — `katalogHargaLiteran` ber-id **nama wadah**
(delapan dokumennya sudah ada). Penyusun tidak berubah dan datanya berbentuk sama, jadi uji byte-sama tetap berlaku. Yang berubah hanya
**datanya** kalau owner mengubahnya (mis. mencabut harga liter merek yang hanya lewat wadah → `hargaPerLiter` jadi 0 di katalog kasir).

## 10. Rencana per bagian (dokumen yang ditulis) & peralihan

| Bagian | Yang ditulis | Jenis dokumen baru? |
|---|---|---|
| 1 Cocokkan tumpukan | `penyesuaianStok` per nama (selisih karung utuh × isi) | tidak |
| 1 Cocokkan wadah | `penyesuaianStok` per merek asal (bagian wadah & karung terbuka), `wadahLiteran` `isi` + `karungIsi` (titik samakan) | tidak |
| 2 Varian | `batchMasuk` dengan nama varian; draf harga (`aturanToko/hargaDraf`) / terbit; `pengaturan/jenisBeras` kunci varian | tidak |
| 3 Arsip | penanda arsip di setelan (§11) | tidak |
| 4 Setengah karung | `produksiKemasan` (bongkar 1 × 50 → 2 × 25, jalur Adukan) + `penjualan` kemasan 25 kg, satu kiriman | tidak |
| 5 Wadah bernama | `penjualan` literan dipecah per merek asal; `wadahLiteran` takar TANPA pindah buku; `katalogHargaLiteran` per nama wadah | tidak |

**Peralihan Bagian 5 (tanpa migrasi data):**
1. Sejak putaran ini, takar dari karung nama lain **tidak lagi** menulis `produksiKemasan` pindah buku; dokumen takar baru ditandai (§11) dan
   kg-nya dihitung milik **merek asal** di komposisi wadah.
2. Isi wadah SEBELUM peralihan (titik samakan terakhir + takar lama + takar pindah buku lama) dihitung milik **nama wadah** — persis seperti buku
   lama menghitungnya. Jadi buku lama "IR64 Apex" dst. tetap terpotong saat isinya terjual, sampai bagian itu habis dari wadah.
3. Penjualan literan dari wadah dipecah menurut komposisi saat itu: bagian nama wadah (sisa lama) + bagian tiap merek asal (takar baru).
4. Barang masuk tidak lagi membukukan nama kelas mutu (§12 pertanyaan 2); sisa buku lama dijual sampai habis lalu diarsipkan (Bagian 3).
5. Buku yang meleset seperti IR64 Elevate (§7) dibetulkan owner lewat cocokkan tumpukan + cocokkan wadah (Bagian 1), bukan otomatis.

**Identitas yang dijaga uji (Bagian 5):** untuk setiap merek M: `tumpukan(M) + karung terbuka(M) + Σ bagian M di semua wadah = buku(M)`.

**Risiko yang sudah terlihat:**
- `kasir.html` menjual literan satu baris per nama → memotong buku NAMA WADAH (model lama). Sesudah sisa lama nama itu habis & diarsipkan, tutsnya
  hilang dari kasir.html. HP penjaga (tuts angka, dirinci di `/baru/`) tidak terpengaruh. [ASUMSI] kasir.html tetap tidak dipakai untuk literan.
- Nama wadah yang juga nama merek (Angsa dkk.): arsip merek itu tidak boleh menghapus harga liter wadahnya (§12).

## 11. Kolom & dokumen setelan baru — minta izin owner

Tidak ada koleksi baru. Aturan server v4 tidak membatasi kolom di dokumen-dokumen ini (owner menulis bebas; `wadahLiteran`, `aturanToko`,
katalog harga, `pengaturan/jenisBeras`), jadi `firestore.rules` tidak berubah. Kolom tambahan diabaikan mesin beku dan `index.html`.

| Di mana | Kolom baru | Untuk apa |
|---|---|---|
| `aturanToko/catatStok` | `batasVarian` (bawaan 5 %) | batas selisih harga beli yang memicu "sama barangnya / beda mutu?" |
| `wadahLiteran` tipe `atur` | `susutWajarKg` (bawaan 1 kg per wadah per hari) | batas susut takar yang tidak minta alasan |
| `wadahLiteran` tipe `isi` | `komposisi {merek: kg}` | isi wadah sesudah dicocokkan, per merek asal |
| `wadahLiteran` tipe `takar` | `bukuAsal: true` | takar model baru: kg tetap milik merek asal (tidak pindah buku) |
| `penjualan` (baris literan wadah) | `dariWadah` (nama wadah), `takaranId` (pengikat baris internal satu takaran) | struk menggabung; komposisi wadah berkurang dari baris ini |
| `penyesuaianStok` | `bagian: 'tumpukan' \| 'wadah'`, `wadah` | papan kapur memisahkan dua kejadian cocokkan |
| `penjualan` (kemasan ½) & `produksiKemasan` | `dariSetengah` (id produksi pemecah) | batalkan nota mencabut pemecahnya juga |
| `wadahLiteran` tipe `atur` (bukan `aturanToko/harga` — lihat §13) | `literanLangsung: [merek]`, `merekKarung: [nama wadah]` | merek yang dijual literan dari karungnya sendiri (tetap butuh harga liter); nama wadah yang juga merek karung pemasok |
| `wadahLiteran` tipe `atur` / `isi` / `karungIsi` | `gantiNama {dari, ke}`, `gantiNamaDari` | jejak ganti nama wadah (isi & karung terbuka ikut pindah) |
| `aturanToko/produkArsip` | `daftar [{kunci, nama, tanggal, jam}]` | penanda arsip (jawaban §12 no. 4) |

## 12. Pertanyaan untuk owner

1. **Kolom baru di §11 — boleh?** Semuanya di dokumen yang sudah ada; tanpa koleksi baru, tanpa rules baru.
2. **Nama wadah yang juga merek karung.** "IR64 Apex/Ascent/Elevate, IR42 Select/Value" = kelas mutu → barang masuk menolak nama ini (minta nama
   karung aslinya). Angsa, Perahu Layar, Pandan Wangi masuk dari pemasok dengan nama itu — tetap boleh dicatat sebagai merek karung?
3. **Tempat penanda arsip.** (a) satu dokumen setelan `aturanToko/produkArsip` berisi daftar nama arsip (satu tempat, ikut ke semua perangkat);
   atau (b) kolom `arsip` di tiap dokumen katalog harga nama itu (satu nama bisa punya 2–5 dokumen katalog: per kg, per liter, 50 kg, 25 kg,
   kemasan; nama tanpa katalog tidak bisa diarsipkan).

## 13. Keputusan owner (27 Sep 2026) & apa yang dibangun

Jawaban owner atas §12:

1. **Kolom baru — boleh semua.** Tidak ada koleksi baru; `firestore.rules` v4 tidak berubah (`periksa_rules.py` LULUS apa adanya).
2. **Nama wadah yang juga merek karung — boleh; wadah kotak literan (Angsa, Perahu Layar, dll.) bisa diganti namanya.** Bawaan merek karung:
   Angsa, Perahu Layar, Pandan Wangi (`MEREK_KARUNG_BAWAAN`); owner mengubahnya di Stok › Wadah literan › Atur ("Nama wadah yang juga MEREK
   KARUNG pemasok"). Ganti nama satu wadah ada di rincian wadah ("ganti nama wadah").
3. **Nama kelas — tolak, wajib nama karung.** Barang masuk (baru) dan varian dari layar Harga menolak nama wadah/kelas (juga yang pernah jadi
   nama wadah) dengan kalimat; koreksi kedatangan lama yang sudah memakai nama itu tetap boleh.
4. **Arsip — satu dokumen daftar arsip** (`aturanToko/produkArsip`).

Penyesuaian saat membangun Bagian 5:

- `literanLangsung` pindah dari `aturanToko/harga` (rencana §11) ke dokumen aturan wadah (`wadahLiteran` tipe `atur`): `aturanToko/harga` tidak
  terbaca akun karyawan (rules v4), sedangkan rak Jual karyawan harus sama dengan rak owner. Belum pernah ditandai → bawaan TERUKUR: merek (bukan
  nama wadah) yang punya harga liter DAN pernah terjual literan tanpa `dariWadah`. Di cadangan 27 Sep: Bahan campuran standar, Beras Merah,
  Ketan Hitam PK, Ketan Hitam Sosoh, Ketan Putih, Ketan Putih Paris.
- Takar model baru ditulis dengan `bukuAsal: true` dan TIDAK lagi menulis `produksiKemasan` pindah buku (keputusan 22 Sep "pindah buku"
  digantikan). Catatan takar lama (dengan/tanpa `produksiId`) tetap dibaca seperti dulu oleh `pindahNama` & komposisi.
- Pemecahan satu takaran (`pecahItemsWadah`, jual-logika.js) dipakai nota Jual DAN rinci karcis kasir; baris internal membawa `dariWadah` +
  `takaranId`; gabungan tampil (`gabungTakaran`) tinggal di struk-logika.js.
- Kolam karung terbuka saat ganti nama: catatan karung lama tanpa kolom `wadah` dibaca menurut daftar wadah sekarang, jadi sesudah ganti nama
  kolamnya bisa tertinggal/terbaca lepas. Ganti nama menyamakan kembali tiap kolam yang bergeser ke angkanya sebelum ganti nama (diuji di
  cadangan: 8/8 wadah diganti nama tanpa menggeser tumpukan, karung terbuka, atau isi wadah merek mana pun).
- Di cadangan 27 Sep "belum ada harga" katalog turun 11 → 5: enam tagihan harga liter untuk merek yang cuma lewat wadah hilang. Harga liter NG &
  Kumala (disetel 27 Sep) tidak dipakai rak — tercatat di Katalog › Literan sebagai "tidak dipakai".
- Harga › Literan › "Harga liter yang tidak dipakai" punya tombol **hapus** (dua ketukan; `susunHapusLiter`): yang dihapus hanya dokumen
  `katalogHargaLiteran` nama itu (+ drafnya), harga lamanya tercatat di jejak hapus; `hargaTerbit` dan nota lama tidak disentuh. Harga liter wadah &
  literan langsung tidak bisa dihapus dari sana. Katalog HP kasir sesudahnya: baris merek itu tetap ada dengan harga liter 0 — kasir.html
  menulis tuts literannya "harga?", pencocokan nominal otomatis melewatinya, dan kalau diketuk manual tanpa jumlah (×) liternya tidak bisa
  diturunkan dari nominal → nota tercatat 0 liter (stok tidak turun).
