# Peta harga beli per kelas mutu — putaran 30, Tahap 0

**Status (28 Sep 2026): peta selesai, belum ada perubahan perilaku.** Tidak ada syarat berhenti yang terpicu: ketiga bagian bisa dibangun **tanpa
koleksi baru**, **tanpa mengubah `firestore.rules` v4**, dan **tanpa menyentuh 28 mesin beku**. Yang perlu jawaban owner sebelum dibangun ada di §11.

Sumber: kode di `main` 2d6cc4e (sesudah PR #50), `firestore.rules` v4, dan cadangan toko 28 Sep 2026 sore (`_privat/`, tidak masuk repo; berisi
kedatangan pemasok siang itu). Angka di dokumen ini kg dan jumlah catatan, **bukan rupiah**. Nama orang dan nama pemasok tidak disebut
(pemasok A = yang biasa bon, pemasok B = yang biasa tunai).

## 0. Masalah (owner 28 Sep)

Pemasok mengganti nama merek walau barang dan harganya sama. Kedatangan pemasok A 28 Sep membawa **tujuh nama baru** (TH, SR, HSj, SB, II, MTJ, CM)
+ satu nama lama; kedatangan 18 Sep dan 21 Sep sebelumnya juga membawa nama baru (AKM, PM, NG; KI, Kumala, Tawon). Petunjuk "Harga / kg · lalu …"
di Barang masuk dicari lewat **nama merek**, jadi tiap nama baru tidak punya "lalu", dan riwayat harga satu jenis barang terputus tiap ganti nama.
Owner ingin (1) harga beli terakhir tetap terlihat saat mengisi Barang masuk walau mereknya baru, (2) bisa membaca harga beli mana yang naik/turun
dari waktu ke waktu **per kelas**.

## 1. Jalur yang ada sekarang (dari kode)

| Apa | Di mana | Cara kerja | Kenapa tidak cukup |
|---|---|---|---|
| "lalu …" di Barang masuk | `stok-catat-logika.js hargaSebelumnya(merk)` → `hitungStokKarungPerMerk()[merk].hargaTerakhirPerKg` (mesin beku) | harga/kg baris karung dari batch **ber-id terbesar** yang memuat merek itu (fondasi ikut); dipakai `hitungMasuk()` sebagai `hargaLalu` per baris | per merek; tanpa tanggal & pemasok; merek baru → 0 → petunjuk tidak muncul |
| Peringatan beda > 10 % | `stok.js` baris ±573 | `|harga − hargaLalu| ÷ hargaLalu > 0,1` → "beda N % dari harga lalu" (tampilan saja, tidak memblokir) | hilang bersama "lalu" |
| Pertanyaan varian | `varian-logika.js vrPerluTanya` (`aturanToko/catatStok.batasVarian`, bawaan 5 %) | nama yang **sudah punya buku**: beda harga beli vs **modal rata-rata** > batas → "sama barangnya / beda mutu" (simpan ditolak sampai dijawab) | hanya nama yang punya buku; merek baru tidak ditanya apa-apa |
| Harga terakhir per pemasok | `bon-pemasok-logika.js daftarPemasok().hargaPerMerk[merk].riwayat/terakhir` → `belanja-logika.js` | tiap pemasok × merek: riwayat {tanggal, id, hargaPerKg, kg}, fondasi tidak ikut; dipakai kertas belanja | per pemasok × merek; tanpa bongkar; tidak tahu kelas |
| Garis waktu modal | `stok-hpp-logika.js riwayatModal(merk)` (Stok › HPP / modal › Garis waktu) | tiap kedatangan satu nama, lama → baru: {tanggal, jam, pemasok, fondasi, dikoreksi, hargaPerKg, hppPerKg (+bongkar), totalKg, batchId} + pindah buku | per nama; tidak menggabung nama-nama satu kelas |
| Nama kelas di Barang masuk | `hitungMasuk` + `wbNamaKelas()` | nama wadah yang bukan `merekKarung` DITOLAK sebagai merek (keputusan owner 27 Sep, peta stok §13.3) | tetap — tidak diubah putaran ini |

Kesimpulan: bahan riwayatnya sudah ada di `riwayatModal` (per nama, sudah menyaring bal, membawa pemasok + tanggal + jam + fondasi). Yang belum ada hanya
**peta merek → kelas** dan **lapisan baca yang menggabung riwayat anggota satu kelas**.

## 2. Kelas mutu = nama wadah (konsep yang dipakai, tidak ada konsep baru)

- Daftar kelas = `aturWadah().daftar` (dokumen `wadahLiteran` tipe `atur` terbaru). Di cadangan 28 Sep: 8 wadah — **5 kelas murni** (IR64 Apex,
  IR64 Elevate, IR64 Ascent, IR42 Select, IR42 Value) + **3 nama wadah yang sekaligus merek karung** (`merekKarung`: Angsa, Perahu Layar, Pandan
  Wangi) = kelasnya sendiri.
- **Merek karung tetap kunci buku stok** (peta stok §1). Kelas hanya **lapisan baca**: peta `{merek → nama wadah}`. Tidak ada pindah buku, modal per
  nama tidak berubah, laba/neraca/nilai stok byte-sama.
- **Kedatangan lama atas nama kelas itu sendiri** (IR64 Apex dkk. sebelum 18 Sep — 10 kedatangan Apex, 10 Elevate, 5 Ascent, 4 Select, 6 Value) =
  riwayat kelas itu; tidak dibuang, tidak dipetakan (nama = nama wadah → anggota otomatis).
- Nama wadah / buku khusus (`'Wadah …'`, `'Karung wadah …'`, `'Adukan … kg'`) / buku ukuran (`'Merek 25 kg'`) **tidak dipetakan** — ikut induknya
  (`petaBukuWadah`, `petaUkuran`; pola `jbDaftar()`).
- Barang masuk tetap **menolak nama kelas** sebagai merek — tidak diubah.

## 3. Tempat peta merek → kelas (jawaban 1)

**Pilihan: `aturanToko/kelasMerek { id: 'kelasMerek', peta: { <merek>: <nama wadah> }, diubahPada, tanggal, jam }`** — satu dokumen, owner saja.

| | `aturanToko/kelasMerek` (dipilih) | kolom `kelasMerek` di dokumen aturan wadah (`wadahLiteran` tipe `atur`) |
|---|---|---|
| Rules v4 | `match /aturanToko/{id}`: owner `read/create/update/delete` untuk id apa pun; staf hanya membaca id yang terdaftar (kelasMerek **tidak** terdaftar → tertutup). **Tidak perlu diubah**, `periksa_rules.py` lulus apa adanya | `wadahLiteran` terbaca karyawan (rak Jual) — peta kelas ikut terbaca staf padahal tidak dibutuhkan |
| Bentuk tulis | pola `pengaturan/jenisBeras` (peta utuh ditulis ulang, kunci lain utuh) — pola yang sudah diuji `uji_setelan_jenis_beras.py` | aturan wadah ditulis sebagai **dokumen baru** tiap perubahan (riwayat); peta kelas ikut disalin ke tiap dokumen atur → membengkak |
| Satu kiriman dengan Simpan barang masuk | satu dokumen tambahan di `dokumen[]` `susunSimpanMasuk` (seperti `vrDokJenis`) | juga bisa, tapi menulis seluruh aturan wadah dari layar Barang masuk |
| Siapa membaca | Barang masuk (owner), Stok › HPP (owner), daftar "Kelas mutu" (owner) — semua layar owner | — |
| Cadangan versi 5 | koleksi `aturanToko` sudah ikut cadangan utuh (13 dokumen di cadangan 28 Sep); dokumen baru = satu entri lagi; **cadangan tanpa dokumen ini tetap terbaca** (peta kosong → semua "belum dipetakan"/tebakan) | sama |
| Ganti nama wadah | nilai peta menunjuk nama wadah → `wbSusunGantiNama` harus **menyertakan dokumen kelasMerek yang nilainya diganti** di kiriman yang sama (satu tempat: `kmDokGantiNama(dari, ke, w)`), seperti harga liter & resep ikut pindah | kolomnya ada di dokumen yang sama, ikut ditulis — tapi alasan di atas menang |

Kalau owner memilih alternatif, bagian §5–§8 tidak berubah (hanya `kmDaftar`/`susunKelasMerk` yang membaca/menulis tempat lain).

## 4. Tebakan kelas untuk merek yang belum dipetakan (jawaban 2)

`kmDaftar()` pola `jbDaftar()`: tiap merek yang dikenal (`semuaMerkDikenal()` − buku wadah − buku ukuran − nama kelas) → `{merk, kelas, asal}`, asal =
`'owner'` (ada di peta), `'kosong'` (owner sengaja: `''` = tanpa kelas), `'tebakan'`, `''` (tidak ada petunjuk). Sumber tebakan, urutannya:

1. **nama = nama wadah** (termasuk `merekKarung`) → kelas = dirinya;
2. **catatan `karung`/`karungIsi` `wadahLiteran` ber-`wadah`** (karung merek itu tercatat berdiri di belakang wadah X, catatan terbaru menang; yang
   `dikembalikan` tidak ikut) → kelas X;
3. **`resep` wadah** (`aturWadah().resep[X]` memuat merek itu) → kelas X.

Tidak ada tebakan dari harga atau dari jenis beras: jenis beras (`pengaturan/jenisBeras`) hanya **petunjuk** di daftar ("jenis IR42 — kelas IR42
Value atau IR42 Select?"), bukan tebakan yang mengisi.

**Ukuran di cadangan 28 Sep** — 29 merek dengan kedatangan nyata (13 kedatangan, 2 pemasok, 10 Agu–28 Sep):

| Asal | n | Merek |
|---|---|---|
| nama = nama wadah | 8 | IR64 Apex, IR64 Elevate, IR64 Ascent, IR42 Select, IR42 Value, Angsa, Perahu Layar, Pandan Wangi |
| karung ber-wadah | 3 | Kumala → IR64 Elevate, PM → IR64 Elevate, Bahan campuran standar → IR64 Ascent |
| resep wadah | 0 | (resep kosong di cadangan) |
| **tertebak** | **11** | |
| **tidak tertebak** | **18** | TH, SR, HSj, SB, II, MTJ, CM (28 Sep) · AKM, NG (18 Sep) · KI, Tawon (21 Sep) · OJ (4 Sep) · IR64 LL · Ketan Putih, Ketan Putih Paris, Ketan Hitam PK, Ketan Hitam Sosoh, Beras Merah |

Dari 18 yang tidak tertebak, **6 memang tidak akan pernah berkelas** (ketan & beras merah: literan langsung, bukan barang wadah) → jawaban yang benar
untuknya adalah `''` "tanpa kelas". Sisanya 12 merek karung yang **owner harus memetakan sekali** lewat daftar "Kelas mutu" (petunjuk jenis beras:
7 IR64, 2 IR42, 1 Pandan Wangi, 1 Ketan Putih, 1 sengaja kosong). Sesudah dipetakan, kedatangan berikutnya atas nama yang sama langsung dikenali.

## 5. Rumus "harga lalu kelas" (jawaban 3)

`kmRiwayatKelas(kelas)` = gabungan `riwayatModal(m)` untuk setiap `m` anggota (peta owner + tebakan + nama = kelas), disaring `jenis === 'kedatangan'`
dan `!fondasi` (bukan stokAwal / tutupBuku / lahirBuku — `riwayatModal` sudah membuang baris bal), diurutkan **tanggal + jam + id**; tiap baris membawa
`{merk, tanggal, jam, pemasok, hargaPerKg, hppPerKg, totalKg, batchId}`.

`kmHargaLaluKelas(kelas, pemasokDipilih, kecualiBatchId)`:
- buang baris `batchId === kecualiBatchId` (batch yang sedang dikoreksi, `draf.id`);
- `utama` = baris terbaru dari **pemasok yang sedang dipilih** di draf (kalau ada); `lain[]` = baris terbaru tiap pemasok lain (≤ 2, terbaru dulu);
  tanpa pemasok dipilih / pemasok itu belum pernah → `utama` = baris terbaru siapa pun, `lain[]` sisanya;
- hasil `{kelas, harga: utama.hargaPerKg, tanggal, pemasok, merk (nama asal), lain: [{pemasok, harga, tanggal, merk}]}` atau `null` bila kelas belum
  punya kedatangan.

**Bedanya dari yang sudah ada (bukan sumber kebenaran ketiga):**

| Sumber | Lingkup | Urutan | Fondasi | Bongkar | Dipakai untuk |
|---|---|---|---|---|---|
| `hitungStokKarungPerMerk().hargaTerakhirPerKg` (mesin) | per **merek** | **id** terbesar | ikut | tidak | "lalu" merek + 10 % (tetap) |
| `daftarPemasok().hargaPerMerk` (bon-pemasok) | per **pemasok × merek** | tanggal + id | tidak | tidak | kertas belanja (tetap) |
| `riwayatModal(merk)` (stok-hpp) | per **merek**, tiap kedatangan | tanggal + id | ditandai | keduanya | garis waktu HPP (tetap) |
| **`kmRiwayatKelas`** = `riwayatModal` × anggota | per **kelas** | tanggal + jam + id | dibuang | keduanya, dipakai **hargaPerKg** (harga beli, sebanding dengan yang diketik) | harga lalu kelas, kartu per kelas |

Jadi lapisan kelas **memakai ulang** `riwayatModal`; tidak menghitung sendiri dari `batchMasuk`. Uji asap wajib: untuk tiap merek di cadangan,
`kmRiwayatKelas` yang disaring ke satu merek = `riwayatModal` merek itu, dan baris terbarunya berharga = `hargaTerakhirPerKg` mesin (di cadangan 28 Sep
urutan id dan urutan tanggal memberi jawaban yang sama untuk semua 29 merek; kalau ada kedatangan bertanggal mundur, keduanya bisa beda — kalimat
petunjuk menyebut tanggalnya, jadi owner melihatnya).

"Lalu" untuk **merek yang dikenal** tetap `hargaSebelumnya(merk)` (mesin) — hanya ditambah tanggal + pemasok dari baris `riwayatModal` terbaru merek itu
(satu angka, dua sumber yang sama-sama sudah ada; uji menjaga keduanya sama).

## 6. Peringatan & tanda (jawaban 4) — tanpa angka Atur baru

| Keadaan | Sekarang | Usul |
|---|---|---|
| merek dikenal, harga diketik | "beda N % dari harga lalu" bila > 10 % (`stok.js`) | tetap; + tanda **▲ naik Rp… / ▼ turun Rp… / = sama** vs harga lalu merek (kalimat, bukan angka Atur) |
| merek dikenal, beda > `batasVarian` dari **modal** | pertanyaan sama barangnya / beda mutu (memblokir sampai dijawab) | tetap, tidak disentuh |
| merek BARU, kelas dipilih / tertebak, harga diketik | tidak ada apa-apa | ▲▼= vs **harga lalu kelas**; bila beda > `batasVarian` (angka yang sudah ada, 5 %) → kalimat lunak **"beda N % dari kelas X (lalu … · tanggal · pemasok) — kelasnya benar?"**; **tidak memblokir simpan** |
| merek BARU tanpa kelas | tidak ada apa-apa | "Merek baru — kelas mana?" + pil; tanpa kelas boleh; simpan tidak pernah ditolak hanya karena kelas |
| koreksi kedatangan lama | seperti biasa | harga lalu kelas mengecualikan batch yang sedang dikoreksi (`draf.id`) |

Kenapa `batasVarian`, bukan 10 %: 10 % adalah "harga beda dari **harga lalu merek yang sama**" (barang yang sama berubah harga); `batasVarian` adalah
"barang ini mungkin **bukan barang yang sama**" — pertanyaan kelas sama sifatnya dengan pertanyaan varian. Tidak ada angka baru.

## 7. Kartu "Harga beli per kelas" (jawaban 5)

- **Tempat**: Stok › HPP / modal, **tab baru "Per kelas"** di samping Garis waktu (`TAB_HPP` + satu), karena bahan & tampilannya sama dengan Garis
  waktu (kedatangan → bar). Alternatif: Harga › Katalog (ditolak: layar itu tentang harga **jual**).
- **Isi per kelas**: judul + anggota ("IR64 Elevate · 3 nama: IR64 Elevate, PM, Kumala"), lalu **tiap kedatangan merek apa pun di kelas itu = satu
  garis** (tanggal · nama asal · pemasok · harga/kg · kg; bar relatif ke tertinggi, pola `garisWaktu()`), koreksi diwarnai, lonjakan ▲▼ vs
  kedatangan sebelumnya di kelas itu.
- **Per bulan**: rata-rata **tertimbang kg** (Σ harga × kg ÷ Σ kg) tiap bulan yang punya kedatangan, ▲▼ vs bulan sebelumnya (persen, dibulatkan).
  Bulan tanpa kedatangan = "tidak ada kedatangan" (bukan nol — tiga keadaan kosong).
- **Batas periode data disebut**: "data kedatangan 10 Agu–28 Sep 2026 (2 bulan) — per kuartal belum bisa dibandingkan". Kartu **menyebut**, tidak
  menampilkan kuartal nol. Kuartal muncul sendiri sesudah ≥ 2 kuartal berisi.
- **Merek tanpa kelas** disebut di bawah kartu: "N merek belum berkelas: …" + tautan ke daftar Kelas mutu (§8).
- Di cadangan 28 Sep: 8 kelas semuanya punya kedatangan Agu & Sep; sesudah tebakan 2 kelas beranggota > 1 nama (IR64 Elevate 3 nama, IR64 Ascent 2),
  6 kelas lain beranggota satu nama (dirinya sendiri).

## 8. Layar & dokumen yang disentuh (rencana bangun)

**Bagian 1 — `kelas-merek-logika.js`** (awalan `km`, tanpa DOM): `kmPeta()` (dokumen `aturanToko/kelasMerek` → `{merek: kelas}`), `kmKelasMerk(merk)`
→ `{kelas, asal}`, `kmDaftar()` → `{baris, terisi, total}`, `susunKelasMerk(merk, kelas, w)` → `{dokumen: [aturanToko/kelasMerek], patch}` (kelas
wajib nama wadah yang ada atau `''`; nama wadah / buku khusus / buku ukuran / nama tak dikenal ditolak dengan kalimat; sama → ditolak),
`kmDokKelas(pasangan, w)` (peta + beberapa kunci, untuk Simpan barang masuk), `kmDokGantiNama(dari, ke, w)` (nilai peta ikut ganti nama wadah),
`kmRiwayatKelas`, `kmHargaLaluKelas`, `kmKartuKelas()` (§7).
Daftar **"Kelas mutu · N/M terisi"** untuk memetakan merek lama sekaligus: **di Harga › Katalog, di samping "Jenis beras · N/M terisi"** (pola
`jbDaftar`/`gambarJenisDaftar`: pil kelas per nama, "tanpa kelas", tebakan ditandai "tebakan"; petunjuk jenis beras di baris). Bukan di Stok › Wadah
literan › Atur (itu tempat aturan fisik wadah). Pintu kedua: Stok › HPP › Per kelas → "N merek belum berkelas" → daftar itu.

**Bagian 2 — Barang masuk** (`stok-catat-logika.js hitungMasuk` + `stok.js`): tiap baris menambah `hargaLaluKelas` (§5) dan `arah` (`'naik'|'turun'|
'sama'|''`, selisih rupiah); draf baris menambah `kelas` (pilihan owner) — ikut `KUNCI_DRAF_MASUK` localStorage (pola `isian.js`, penjaga isian sudah
memuat kunci itu). Tiga keadaan di bawah Harga / kg:
- a. merek dikenal: "lalu … · 21 Sep · pemasok" (+ ▲▼= sesudah harga diketik);
- b. merek baru tanpa kelas: "Merek baru — kelas mana?" + pil nama wadah + "tanpa kelas"; sesudah dipilih: "merek baru · kelas IR64 Elevate lalu … (PM ·
  18 Sep · pemasok)"; pilihan ditulis **DALAM kiriman Simpan barang masuk yang sama** (`susunSimpanMasuk` menambah `kmDokKelas` ke `dokumen[]`; simpan
  ditolak → peta tidak tertulis);
- c. merek baru yang kelasnya tertebak: ditandai "tebakan", bisa diganti; tebakan yang dibiarkan **ikut ditulis** ke peta saat simpan (supaya
  kedatangan berikutnya tidak menebak lagi) — atau tidak ditulis (§11 no. 4).
Koreksi kedatangan lama: kelas tidak ditanya (seperti varian).

**Bagian 3 — kartu per kelas** (`stok-hpp-logika.js` + `stok.js` tab): §7.

**Dokumen/kolom baru**: hanya `aturanToko/kelasMerek` (dokumen baru di koleksi yang sudah ada). Tidak ada kolom baru di `batchMasuk`.

## 9. Yang tidak disentuh

28 mesin beku · `index.html`, `kasir*.html`, `sw-kasir.js` · `firestore.rules` v4 · kunci buku stok, modal, laba, neraca, nilai stok (ASAP GLOBAL
byte-sama) · penolakan nama kelas di Barang masuk (§13.3) · pertanyaan varian & `batasVarian` · kertas belanja & `daftarPemasok` · `ringkasanKasir`.

## 10. Uji yang direncanakan

`alat-uji/uji_kelas_merek.py` (+ `--kontrol`, masuk CI) pola `uji_setelan_jenis_beras.py` / `uji_varian_merek.py`:
- jsc kotak pasir: peta baca/tulis (kunci lain utuh, `''` = tanpa kelas, nama wadah/buku khusus/ukuran/tak dikenal ditolak); tebakan tiga sumber &
  urutannya; `kmRiwayatKelas` = gabungan `riwayatModal` (fondasi & bal tidak ikut, batch dikoreksi dikecualikan); pemasok dipilih diutamakan, `lain[]`;
  Barang masuk tiga keadaan a/b/c, ▲▼=, kalimat lunak > `batasVarian` **tidak memblokir**, simpan menulis peta + batch **satu kiriman**, simpan ditolak →
  tanpa dokumen peta; draf localStorage membawa kelas per baris; kartu per kelas: garis, rata-rata tertimbang per bulan, ▲▼ bulan, "per kuartal belum
  bisa", bulan tanpa kedatangan ≠ nol; ganti nama wadah → nilai peta ikut.
- kontrol positif (≥ 12): tebakan dari harga; fondasi ikut riwayat kelas; batch dikoreksi ikut; simpan diblokir karena kelas; peta ditulis walau simpan
  ditolak; kelas ditulis sebagai kolom di batchMasuk; nama kelas lolos jadi merek; ▲▼ terbalik; rata-rata bulan tidak tertimbang; kuartal nol digambar;
  rules: staf boleh membaca kelasMerek; ganti nama wadah meninggalkan nama lama di peta.
- asap cadangan (lokal, `_privat/`): 11 tertebak / 18 tidak (§4) — sesudah 7 merek 28 Sep dipetakan **di kotak pasir uji** (bukan ditulis ke toko),
  harga lalu kelas tiap merek = kedatangan nyata terakhir kelas itu sebelum 28 Sep; ASAP GLOBAL omzet/laba/neraca/nilai stok byte-sama dengan `main`.
- `periksa_rules.py`, `pindah_mesin.py --periksa`, `uji_stok_baru.py`, `uji_harga_baru.py`, `uji_isian_lokal.py` (kunci draf baru), `peta_akses.py
  --kiriman` (Simpan barang masuk + 1 dokumen) tetap hijau.

## 11. Pertanyaan untuk owner — mengubah hasil

1. **Tempat peta**: `aturanToko/kelasMerek` (§3, usulan) — setuju? Alternatif: kolom di dokumen aturan wadah.
2. **Merek yang tidak berkelas** (ketan, beras merah, dan merek yang owner tidak mau kelaskan): **dibiarkan tanpa kelas** (`''`, tampil "tanpa kelas";
   harga lalu = merek itu sendiri saja) — usulan — atau **kelas = namanya sendiri** (tiap merek jadi kelas, kartu per kelas berisi puluhan kelas
   beranggota satu)?
3. **Daftar "Kelas mutu"** di Harga › Katalog di samping Jenis beras (§8) — setuju? Alternatif: Stok › Wadah literan › Atur.
4. **Tebakan yang dibiarkan saat Simpan barang masuk** (keadaan c): ikut ditulis ke peta sebagai pilihan owner (usulan: ya — satu ketukan Simpan =
   mengiyakan), atau tetap "tebakan" sampai owner memilih sendiri di daftar?
5. **Kartu per kelas** di Stok › HPP / modal tab "Per kelas" (§7) — setuju?
6. **Kalimat lunak** merek baru beda > `batasVarian` dari harga lalu kelas, tidak memblokir (§6) — setuju? (Tidak ada angka Atur baru.)
7. **Pemetaan 12 merek karung yang belum berkelas** (§4) dikerjakan owner lewat daftar sesudah putaran ini hidup — bukan diisi Claude. Setuju?
8. **Ganti nama wadah** membawa nilai peta kelas di kiriman yang sama (§3) — setuju?

Sesudah jawaban owner: bangun Bagian 1–3, uji, BACA-DULU "Putaran 30" + baris gerbang.
