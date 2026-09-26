# Peta pindahan terakhir — putaran 25c, Tahap 0

**Status (27 Sep 2026): Tahap 0 sempat BERHENTI di dua titik; owner memilih hari itu juga (§7), lalu Bagian A–D dibangun (§8).** Katalog kasir
memuat modal, dan modal itu **dipakai** oleh HP kasir untuk mencatat modal nota; PIN operator kasir tersimpan tanpa diacak di dokumen yang bisa
dibaca akun kasir. Dua-duanya menyentuh bentuk dokumen dan aturan server, jadi tidak dipindah sebelum owner memilih.

Sumber: kode di `main` 60a55f0, `firestore.rules` (v4), dan cadangan toko 27 Sep 2026 05.18 WIB (di `_privat/`, tidak masuk repo).
Angka di dokumen ini **jumlah catatan**, bukan rupiah. Nama orang tidak disebut.

## 1. Katalog kasir — `ringkasanKasir/aktif`

**Penulis satu-satunya:** `index.html`. `susunIsiKatalogKasir()` (baris 11664) menyusun isinya, `terbitkanRingkasanKasir()` (11714) menulisnya
dengan `setDoc` langsung (tidak lewat antrean, tidak ada jejak `logAktivitas`). Isi yang sama dengan terbitan terakhir di HP itu tidak ditulis ulang
(pembanding: localStorage `miqbal_ringkasan_terakhir`). Sejak 25b jalurnya lewat `penjagaTulis('katalog')` dan **selalu lolos**.

**Bentuk dokumen:**

| Field | Isi | Asal (mesin yang sama di `/baru/`) |
|---|---|---|
| `id` | `'aktif'` | — |
| `diperbaruiPada` | ISO, jam HP penerbit | — |
| `kemasan[]` | `kunci, namaProduk, ukuran, sisaUnit, `**`hppPerUnit`**`, hargaPerUnit` | `hitungStokKemasan` (beku), `ambilHargaKemasan` |
| `merkKarung[]` | `merk, sisaKg, `**`hppPerKg`**`, beratKarung (50), karung50, karung25, hargaKarung25, hargaKarung50, hargaPerKg, hargaPerLiter, rasio` | `hitungStokKarungPerMerk` (beku), `merkPunyaKarungBerat`, `hargaKarungUtuh`, `cariHargaKarungPerKg`, `ambilHargaLiteran`, `RASIO_KONVERSI` |
| `bahanLiteran{jenis}` | `sisaPcs, `**`hargaPerPcs`** (harga beli kantong) | `hitungStokBahanLiteran` (beku) |
| `piutang[]` | **`nama, sisa`** — pelanggan yang masih punya bon | `hitungPiutang` (beku) |

Semua fungsi asalnya sudah ada di `/baru/` (salinan byte-sama `baru/js/mesin/*`, dan `data/toko.js`). Jadi penyusun yang byte-sama bisa dibuat di
`/baru/` tanpa menyentuh mesin beku.

**Siapa yang membaca:** keduanya lewat REST dengan akun **kasir@** (`EMAIL_TOKO`, `kasir.html` 482 dan `kasir-darurat-nominal.html` 340; login
dipakai bersama). Aturan v4: `ringkasanKasir` dibaca `owner() || kasir()` (`firestore.rules` 465–468).

| Pembaca | Field yang dipakai | Untuk apa | Baris |
|---|---|---|---|
| `kasir.html` (alat owner) | harga, sisa, **`hppPerKg`, `hppPerUnit`, `bahanLiteran.hargaPerPcs`**, **`piutang`** | tuts barang; **`hppTotalSaatJual` tiap nota** (literan: modal beras + harga kantong → `biayaKemasanLiteran`); daftar bon & saran nama | 530–532, 652–683, 1740–1763, 1532 |
| `kasir-darurat-nominal.html` (HP penjaga) | `kemasan`, `merkKarung` (harga, **`hppPerUnit`, `hppPerKg`**) | tuts bernama barang → nota berbentuk sama dengan kasir biasa, **`hppTotalSaatJual`** diisi dari katalog | 791–812, 1030–1043 |

### Apakah modal dipakai HP kasir? **Ya — bukan cuma ikut terkirim.**

- **HP penjaga** memakai modal hanya untuk tuts bernama. Di seluruh cadangan: **1** nota tuts bernama (25 Sep, karcis uji aturan, sudah dibatalkan).
  Karcis angka polos 30 hari terakhir: **794**, tanpa modal (dirinci owner di `/baru/`). Jadi kodenya memakai modal, pemakaiannya praktis nol.
- **`kasir.html`** (alat owner, masuk sebagai kasir@) memakai modal di **setiap** nota: 86 nota di cadangan, semuanya bermodal; 22 nota literan
  membawa harga kantong. Terakhir dipakai **19 Sep 2026** (hari `/baru/` hidup).
- Daftar bon pelanggan (`piutang`: nama + sisa) juga terkirim ke akun kasir. Dipakai `kasir.html` saja; HP penjaga tidak membacanya.

Kalau modal dicabut dari dokumen yang dibaca kasir@, kedua berkas kasir mencatat nota **tanpa modal**. Mesin laba tidak menghitungnya nol — nota
tanpa modal dikeluarkan dari margin dan disebut di Laporan › Laba ("nota tanpa modal"). Karena `kasir.html` masuk dengan akun yang sama, ia ikut
kehilangan modal, walaupun itu alat owner.

→ **Supaya modal tidak terkirim, bentuk katalog harus berubah.** Sesuai prompt: berhenti, pilihannya di §6.

### HP kasir kapan mengambil katalog baru

| Berkas | Kapan menyegarkan | Baris |
|---|---|---|
| `kasir.html` | saat dibuka, saat sinyal kembali, **tiap 2 menit**, ketuk bilah harga | 1872–1879 |
| `kasir-darurat-nominal.html` | **hanya** saat dibuka dan saat sinyal kembali | 1134, 1138 |

Jalur 25b (denyut + pemeriksaan versi `sw-kasir.js`) **tidak** mengambil katalog: pemeriksaan versi memuat ulang halaman hanya kalau `sw-kasir.js`
berubah, dan perubahan harga tidak mengubahnya. Denyut hanya mengirim, tidak membaca. Akibatnya: **HP penjaga yang aplikasinya terus terbuka
memegang katalog lama sampai dibuka ulang** (peringatan "salinan N jam lalu" baru muncul sesudah 6 jam). Syarat prompt "HP kasir memuat katalog baru
tanpa membuka ulang aplikasi" untuk HP penjaga **tidak bisa dipenuhi tanpa menyentuh `kasir-darurat-nominal.html`** (§6 B).

## 2. Kapan katalog harus segar

Isi katalog = stok (kemasan, karung per nama beras, kantong literan) + harga jual (tiga katalog) + modal + bon pelanggan. `index.html` tidak memilih
kejadian: **setiap** perubahan koleksi apa pun (`pasangSinkronisasi` 11279, dan sesudah tiap `simpanKeFirestore`/`hapusDariFirestore`) menjadwalkan
penyusunan ulang 4 detik kemudian; yang terbit hanya kalau isinya berbeda.

Kejadian di `/baru/` yang mengubah isi katalog (koleksi → field katalog):

| Layar `/baru/` | Kejadian | Mengubah |
|---|---|---|
| Harga › Katalog | **terbit harga** (satu batch tiga katalog) | `hargaPerUnit`, `hargaKarung50/25`, `hargaPerKg`, `hargaPerLiter` |
| Stok › Barang masuk | catat / koreksi / hapus kedatangan | `sisaKg`, `hppPerKg`, nama beras baru (`merkKarung` bertambah) |
| Stok › Adukan | adukan, koreksi, hapus | `kemasan` (nama & ukuran baru, `sisaUnit`, `hppPerUnit`), `sisaKg` |
| Stok › Cocokkan · Kantong · Karantina · HPP · Wadah (takar/buka karung) | hitung fisik, beli/opname kantong, keputusan karantina, koreksi modal, pindah buku | `sisaKg`, `sisaUnit`, `sisaPcs`, `hargaPerPcs`, `hppPerKg` |
| Jual | nota, retur, tukar, batalkan, rinci karcis | stok, `piutang` |
| Pelanggan › Bon | terima bon, bon lama, hapus buku | `piutang` |
| Uang › Tutup hari · Tutup buku | selisih stok saat tutup, saldo pembuka | stok, `piutang` |
| (HP kasir sendiri) | nota & bayar bon dari kasir@ | stok, `piutang` — sampai ke katalog begitu perangkat owner melihatnya |
| (putaran 27) | arsip barang | ketersediaan |

Kesimpulan untuk Bagian A: `/baru/` sebaiknya meniru `index.html` — susun ulang sesudah **setiap** perubahan data (pendengar yang sudah ada di
`data/toko.js`), bandingkan isinya dengan dokumen di server, tulis hanya kalau berbeda. Daftar kejadian di atas menjadi daftar uji, bukan daftar
pemicu (daftar pemicu yang dipilih tangan pasti tertinggal satu kejadian).

Sama seperti sekarang: katalog hanya diperbarui selama ada perangkat owner yang membuka aplikasinya. Penjualan dari HP kasir baru mengurangi stok di
katalog sesudah owner membuka `/baru/`.

## 3. Setelan jenis beras — `pengaturan/jenisBeras`

**Bentuk:** `{ id: 'jenisBeras', peta: { <nama beras>: <jenis> }, diubahPada }` + atribusi `simpanKeFirestore` (`oleh`, `perangkat`,
`diubahOleh`, `diubahPerangkat`). Cadangan 27 Sep: **16** nama beras di peta, tiga nilai: `IR64`, `Pandan Wangi`, dan kosong. Terakhir diubah
**22 Sep 2026** dari sistem lama.

- Nilai kosong `''` = owner sengaja mengosongkan (tampil "belum diisi", menimpa tebakan). Nama yang **tidak ada** di peta memakai tebakan dari
  namanya (`tebakJenisBeras`, 33153: IR64…, IR42…, Ketan…, Pandan Wangi, Beras Merah, Rojolele).
- Pilihan tetap di kode: `PILIHAN_JENIS_BERAS` (33149), tujuh jenis; owner juga boleh mengetik nama jenis lain.
- Penulis: `simpanJenisBeras` (33180) lewat `ubahJenisBeras` (prompt nomor/nama) — dari kaca Harga (pil "varietas?") dan kartu Jenis Beras.
  Tidak ada "hapus" atau "nonaktifkan"; yang ada hanya mengganti nilai per nama beras.

**Siapa yang membaca:**

| Pembaca | Untuk apa | Baris |
|---|---|---|
| `index.html` Jual (penyihir kemasan, langkah 2 "Jenis berasnya?") | mengelompokkan kemasan per jenis | 18649–18677 |
| `index.html` Stok | total kg per jenis | 21206 |
| `index.html` Harga (kaca) | pil jenis per nama beras | 31177, 31365 |
| `/baru/` | **hanya cadangan** (`sistem-logika.js` 205), dari salinan localStorage `miqbal_jenis_beras_v1` | `data/toko.js` 92 |
| kasir.html, kasir darurat, katalog kasir | **tidak ada** | — |

**Akibat salah isi:** hanya pengelompokan di layar sistem lama (kemasan muncul di kelompok jenis yang salah, total kg per jenis bergeser). Tidak
ada angka uang, stok, atau harga yang berubah. `/baru/` tidak menampilkan jenis beras di layar mana pun, dan katalog kasir tidak memuatnya.

**Temuan:** salinan localStorage yang dibaca `/baru/` untuk cadangan **hanya diperbarui pendengar `index.html`** (33168). Sesudah sistem lama tidak
dibuka lagi, cadangan dari `/baru/` membawa peta basi — atau kosong di perangkat yang belum pernah membuka sistem lama. `/baru/` sudah memuat koleksi
`pengaturan` (untuk `tempatSimpan`), jadi dokumen `jenisBeras` sebenarnya sudah ada di cachenya.

Catatan prompt: skenario uji "jenis beras baru muncul di Jual dan katalog" tidak bisa dipenuhi apa adanya — Jual `/baru/` dan katalog kasir tidak
memakai jenis beras (§6 D).

## 4. Operator & PIN

### Daftar & PIN operator kasir — `pengaturan/aksesKasir`

**Bentuk:** `{ id: 'aksesKasir', operator: { <nama>: { aktif: bool, pin: '<angka>' } }, diubahPada }` + atribusi. Tiga operator, daftarnya
tetap di kode. Terakhir diubah **5 Sep 2026**. (Nama operator dan isi PIN sengaja tidak ditulis di sini — repo publik.)

**TEMUAN: PIN tersimpan tanpa diacak, dan dokumen ini bisa dibaca akun kasir@** (`firestore.rules` 387: `id == 'aksesKasir' && kasir()`).
Siapa pun yang memegang sandi toko HP kasir bisa membaca PIN ketiga operator.

**Bagaimana kasir memakainya:**

| Berkas | Membaca? | Memakai? |
|---|---|---|
| `kasir.html` | ya — tiap penyegaran ke localStorage `kasir_roster_v1` (700–713) | **tidak**: layar "Siapa yang jaga kasir?" (`pilihOperatorIdx` 768) tidak punya pintu sejak 9 Agu — chip nama di bilah atas (288) tidak bisa diketuk; semua nota atas nama Owner (755) |
| `kasir-darurat-nominal.html` | **tidak** | nama operator diambil dari localStorage `kasir_operator_v1` (353) yang hanya diisi layar pilih operator `kasir.html` tadi |

Di cadangan: HP penjaga mencatat **786** karcis dalam 30 hari, **semuanya** `oleh: "(darurat tanpa nama)"`, tanpa field `operator`. 9 karcis
bernama operator berasal dari HP uji. Jadi daftar operator dan PIN-nya **tidak dipakai kasir mana pun** saat ini; yang tersisa hanya PIN yang ikut
terunduh ke `kasir.html`.

→ Sesuai prompt Bagian C: dilaporkan, **tidak dipindah** sampai owner memutuskan bentuk penyimpanannya (§6 C).

### PIN owner — `pengaturan/keamanan`

**Bentuk:** `{ id: 'keamanan', garam, acak, diubahPada }` — **hanya hasil acak** (`acakPin`), PIN-nya sendiri tidak pernah disimpan. Dibaca
owner saja (rules 387). Terakhir diubah **14 Agu 2026**.

Dipakai **hanya `index.html`**: gerbang & gembok Menu sistem lama (`mintaPinOwner`, `pinOwnerBenar` 33134; salinan lokal lewat
`pasangPendengarPin` 33284). `/baru/` tidak memakai PIN — pintunya akun (owner@ + sandi). Kasir tidak membacanya. Sesudah sistem lama tinggal
untuk membaca riwayat, PIN ini hanya menjaga gembok Menu sistem lama itu.

## 5. Pulihkan dari cadangan — tetap di sistem lama

Keputusan owner 26 Sep. `muatDariFile` berjalan dengan `_modePulih = true` (12340), dan `penjagaTulis` meloloskan **semua** tulisan selama mode
itu (12055) — tidak bergantung pada daftar `TULIS_TERBUKA`. Pemulihan juga menulis `pengaturan/jenisBeras` dan `pengaturan/tempatSimpan` dari
berkas (12377–12384) lewat jalan yang sama.

Jadi mengunci penulis jenis beras, operator, dan PIN owner di `index.html` **tidak mengubah** pemulihan. Syarat di `docs/prosedur-pulih-darurat.md`
(unduh cadangan dulu, tempel `firestore.rules.v3` sebentar, ketik PULIHKAN, kembalikan v4, ulang ★ v4, catat jendela darurat) **tetap sama**.

## 6. Pilihan untuk owner

### A · Bentuk katalog kasir

| | Pilihan | Akibat di toko | Yang disentuh |
|---|---|---|---|
| A1 | **Bentuk tetap, penulisnya pindah ke `/baru/`.** Modal & daftar bon tetap ikut terkirim ke akun kasir seperti sejak Agustus; dicabut di putaran tablet, bersama keputusan "siapa mengisi modal nota staf" (`peta-hak-akses.md` §8). | Owner tidak perlu membuka sistem lama untuk harga. Tidak ada yang berubah di HP kasir. | `/baru/`, penjaga `index.html`. Tanpa rules baru, tanpa `kasir*.html`. |
| A2 | **Dua dokumen.** `ringkasanKasir/aktif` tanpa modal & tanpa daftar bon (dibaca kasir@) + dokumen modal khusus owner. | Nota dari tuts bernama HP penjaga tercatat tanpa modal → tampil "nota tanpa modal" di Laba sampai dilengkapi. `kasir.html` ikut kehilangan modal & daftar bon (akunnya sama), kecuali ia pindah masuk sebagai owner. | rules v5 + Playground ★, `kasir*.html` (bacaan katalog), `sw-kasir` v27, alat "lengkapi modal" di `/baru/` |
| A3 | **Cabut modal saja, tanpa dokumen owner.** | Sama dengan A2 untuk nota kasir, tapi tanpa dokumen baru. | `kasir*.html`, `sw-kasir` v27, alat "lengkapi modal" |

### B · HP penjaga mengambil katalog baru tanpa dibuka ulang

- **B1** Izinkan satu perubahan kecil di `kasir-darurat-nominal.html`: ambil katalog juga saat layar HP dinyalakan dan tiap 5 menit selagi terlihat
  (jadwal yang sama dengan denyut), plus `sw-kasir` v27. Tidak mengubah bentuk nota.
- **B2** Jangan sentuh berkas kasir. HP penjaga dapat harga baru saat aplikasinya dibuka ulang atau sinyal kembali. `kasir.html` tetap tiap 2 menit.

### C · PIN operator kasir

- **C1** Tetap di sistem lama sampai putaran tablet. Identitas tablet (akun per orang **atau** satu akun tablet + PIN per orang) belum diputuskan
  (putaran 23), dan bentuk PIN ikut keputusan itu.
- **C2** Pindah ke Menu › Akses **tanpa PIN terbuka**: nama & aktif tetap; PIN disimpan teracak seperti PIN owner, atau dibuang (tidak dipakai kasir
  mana pun). Dokumen berubah bentuk → rules & pembacaan `kasir.html` ikut.
- **C3** Pindah apa adanya (PIN terbuka, dibaca kasir@) — tidak disarankan.

PIN owner (`keamanan`) hanya dipakai sistem lama. Pilihan terpisah: pindah ke Menu › Akses dengan bentuk sama (hash), atau biarkan & ikut dikunci.

### D · Jenis beras

Tidak ada syarat berhenti. Letak di `/baru/` mengikuti cara owner memakainya 22 Sep: pil jenis di **Harga › Katalog** per nama beras + daftar di
**Harga › Atur**; bentuk dokumen sama persis. Pertanyaan: jenis beras juga ditampilkan di Jual & Stok `/baru/` (desain Jual dikunci), atau cukup
di Harga?

## 7. Keputusan owner (27 Sep 2026, kotak pilihan)

| | Pilihan owner | Artinya |
|---|---|---|
| A · bentuk katalog | **A1 — bentuk tetap dulu** | `/baru/` menulis dokumen yang sama persis; modal & daftar bon tetap terkirim ke akun kasir sampai putaran tablet |
| B · HP penjaga | **B1 — boleh ubah** | kasir darurat mengambil katalog saat layar dinyalakan & tiap 5 menit (jadwal denyut); `sw-kasir` v27 |
| C · PIN operator | **dicabut** | PIN dibuang dari dokumen; daftar nama + aktif/libur pindah ke Menu › Peran & persetujuan › Kasir & PIN; tanpa aturan server baru |
| D · jenis beras | **Harga + Stok + Jual** | pil jenis & daftar di Harga, total per jenis di Stok, baris saring di Jual (owner tahu desain Jual dikunci) |

PIN owner (hash, dibaca owner saja) tidak memicu syarat berhenti — dipindah sesuai prompt, bentuk sama.

## 8. Yang dibangun

**A · Katalog kasir.** Penyusun isi disalin apa adanya oleh `alat-uji/pindah_mesin.py` (`susunIsiKatalogKasir` → `baru/js/mesin/pembantu.js`).
`baru/js/data/katalog-kasir.js`: dokumen `kkDokumen` (kunci & urutan = index.html), pembanding isi yang tidak tertipu urutan kunci Firestore
(`kkKanon`), gerbang terbit `kkBolehTerbit` (owner · Firestore · tersambung · tidak ada koleksi ditolak · semua koleksi termuat dan **dijawab server**,
bukan salinan perangkat · katalog server sudah terbaca), `kkSertakan` (katalog SESUDAH kiriman ikut di kiriman yang sama), `kkBeranda`.
`firebase.js`: pendengar dokumen katalog (owner saja), penerbit otomatis 4 detik sesudah **setiap** perubahan data, hanya kalau isinya berbeda,
`setDoc` apa adanya tanpa jejak; penulis pusat menulis `ringkasanKasir` apa adanya (`kkMentah`). Terbit harga (Harga › Periksa & terbitkan)
menyertakan katalog di writeBatch yang sama. Beranda: baris "Katalog kasir: diperbarui …" + Perlu perhatian (perubahan yang belum sampai, terbit
gagal, HP kasir masih v26, HP penjaga yang masih memegang katalog lama menurut denyutnya). `index.html`: penerbit lama ditutup TANPA modal
(`JALUR_DIAM`), tombol "Terbitkan katalog sekarang" hanya menjelaskan. Kasir darurat (v27): ambil katalog saat layar dinyalakan & tiap 5 menit,
denyut membawa `katalog` (cap katalog yang dipegang).

**B · Jenis beras.** `jenisUntukMerk`, `tebakJenisBeras`, `semuaMerkDikenal`, `PILIHAN_JENIS_BERAS` disalin apa adanya. `ambilPetaJenisBeras()` membaca
**dokumen** dulu (salinan perangkat hanya kalau dokumennya belum ada — temuan §3 tertutup). `baru/js/layar/jenis-beras-logika.js`: daftar, pilihan
(7 bawaan + jenis yang pernah diketik), `susunJenisBeras` (dokumen `{ id, peta, diubahPada }` = sistem lama; "kosongkan" = nilai `''` seperti sistem
lama), kelompok Stok, saring rak Jual. Tampil: Harga › Katalog harga (pil per nama beras di papan owner, lembar pilih/ketik/kosongkan, daftar lengkap
"Jenis beras · N/M terisi"), Stok › Gudang (kartu "Beras di buku per jenis"), Jual (baris saring di atas rak literan/kemasan/karung/repack; urutan
rak tidak berubah). `index.html`: ubah & simpan jenis beras ditolak penjaga SEBELUM salinan HP berubah.

**C · Operator & PIN.** `baru/js/layar/akses-kasir-logika.js` + tab **Kasir & PIN** di Menu › Peran & persetujuan: daftar dari dokumen (nama = kunci
peta, tidak ada nama di kode), aktif/libur, tambah, hapus (dua ketukan), **Cabut PIN operator** (tampil selama masih ada PIN tersimpan); setiap simpan
menulis dokumen tanpa `pin`. PIN owner: ganti/setel dengan PIN sekarang (kalau sudah disetel), 4–8 angka, diulang; `acakPin` disalin apa adanya,
dokumen `{ id, garam, acak, diubahPada }`. `index.html`: buka/simpan operator dan setel/simpan PIN owner ditolak penjaga SEBELUM apa pun berubah.
**Belum dicabut di server:** PIN operator di dokumen sungguhan baru hilang sesudah owner menekan "Cabut PIN operator" di `/baru/` (langkah owner).

**D · Sistem lama.** `TULIS_TERBUKA` kosong; yang tersisa di `index.html`: membaca riwayat, denyut, antrean lama sekali, dan pulihkan (mode pulih).
Pita: "Sistem lama hanya untuk membaca riwayat dan pemulihan darurat."

**Gerbang uji:** `alat-uji/uji_katalog_kasir.py`, `uji_setelan_jenis_beras.py`, `uji_operator_pin.py` (+ `--kontrol`, di CI). Uji lama yang memegang
keputusan 25b diperbarui ke keputusan ini dengan jumlah pemeriksaan sama: `uji_sistem_lama_bacasaja.py` (setelan kini ditolak, katalog tidak terbit dari
sistem lama, pita baru) dan `uji_antrean_kasir.py` (label "versi 25c"; lantai kunci bulan `kasir-v26` ≤ versi yang disajikan = versi terbaru `/baru/`).
Aturan server v4 tidak berubah.

