# Peta wadah literan SATU BUKU per kotak — putaran 39, Tahap 0

**Status (29 Sep 2026): §1–§7 = Tahap 0 (akar ditemukan, belum ada perubahan perilaku); §8 = enam jawaban owner & yang dibangun di cabang
`wadah/39-satu-buku`.** Dokumen ini = bukti dari cadangan, akar (fakta / dugaan / asumsi), pemetaan
keputusan owner 29 Sep (butir a–f) ke yang sudah ada dan yang belum, daftar tafsiran, dan pertanyaan yang jawabannya mengubah hasil.
Sumber: kode `main` b77606b, `firestore.rules` v4, cadangan toko 29 Sep 2026 sore (`_privat/`, tidak masuk repo), dijalankan lewat jsc dengan harness
alat uji yang sama (`uji_wadah_stok_sendiri`). Angka di sini **kg, liter, dan jumlah catatan — bukan rupiah**. Nama orang tidak disebut.

## 1. Bukti dari cadangan (FAKTA)

Kartu Jual W5 "IR64 Elevate" menulis *±16,8 L · wadah ±58,87 kg*; panel wadah yang sama *bebas dijual 16,8 L* tetapi *Isi wadah ±58,9 kg · isi terakhir
29 Sep 17:37*; permintaan 20 L ditahan. Dari cadangan:

| Wadah | Buku `'Wadah <nama>'` lahir? | Komposisi isi tercatat (kg, per merek asal) | Isi tercatat | Bebas dijual (L) | Buku merek asal yang membatasi |
|---|---|---|---|---|---|
| W1 IR64 Apex | tidak | IR64 Apex 27,58 · Kumala 15,90 | 43,48 | 46,1 | Kumala 13,85 ÷ porsi 0,366 |
| W2 Angsa | tidak | Angsa 34,80 · IR64 Apex 16,48 | 51,28 | 382,6 | IR64 Apex 100,84 ÷ porsi 0,321 (kotak cuma 51 kg!) |
| W3 Perahu Layar | tidak | Perahu Layar 45,99 | 45,99 | 84,8 | Perahu Layar 69,56 |
| W4 IR42 Select | tidak | IR42 Select 50,72 · IR42 Value 9,00 | 59,72 | 95,4 | IR42 Select 66,48 ÷ porsi 0,849 |
| **W5 IR64 Elevate** | **tidak** | **Kumala 58,87** | **58,87** | **16,8** | **Kumala 13,85** |
| W6 IR64 Ascent | tidak | IR64 Ascent 35,86 | 35,86 | 208,3 | IR64 Ascent 170,86 |
| W7 Pandan Wangi | tidak | Pandan Wangi 15,50 | 15,50 | 12,4 | Pandan Wangi 10,19 |
| W8 IR42 Value | tidak | IR42 Value 18,84 | 18,84 | 284,6 | IR42 Value 233,42 |

- **Kedelapan wadah belum aktif** (`wbAktif` = false semua): tidak ada baris `batchMasuk` ber-`lahirBuku`, tidak ada `produksiKemasan` ber-`pindahAwalWadah`.
  Tombol "Pindahkan isi wadah ke stok wadah" (putaran 28, Stok › Wadah literan) belum pernah ditekan sesudah merge 28 Sep.
- Karena belum aktif, kartu Jual masih memakai `bebasLiterWadah` **putaran 27**: kg ≤ min(buku bebas merek asal ÷ porsinya) — ini **langit-langit
  buku**, bukan isi kotak. Angsa boleh dijual 382,6 L (buku IR64 Apex ÷ porsi) padahal kotaknya 51 kg; W5 hanya 16,8 L (= buku Kumala 13,85 ÷ 0,82).
- Panel wadah memakai `tinggiWadah` non-aktif: isi = tanda `isi` 28 Sep 02:20 (0 kg) + takar sesudahnya − literan terjual sesudahnya. Takar ke W5 sejak
  tanda itu: 48,6 (28 Sep 02:21) + 39,6 (28 Sep 22:06) + 25,2 (29 Sep 17:37) = 113,4 kg Kumala, semuanya bertanda `bukuAsal`.
- **Kejadian 17:37** = karung Kumala 50 kg dibuka otomatis di belakang W5 (`karung`, `otomatis`) + 14 takar × 1,8 = 25,2 kg (`takar`, `bukuAsal`). Takar
  `bukuAsal` **tidak memotong buku merek asal**; buku Kumala baru dipotong saat literan W5 terjual (baris nota dipecah `merkSumber` = Kumala).
- **Rantai stok** (`susunLokasi`, tumpukan = buku − karung terbuka − bagian di wadah) menunjukkan tiga merek MINUS: Kumala −97,52 (buku 13,85 − karung
  terbuka 36,6 − di wadah 74,77), IR42 Select −32,04, Pandan Wangi −28,31. Minus = fisik yang tercatat di alat ukur lebih besar dari buku.
- **Buku Kumala 13,85** = cocokkan 27 Sep 09:46 (fisik 175, satu angka tanpa `bagian`) − 136,15 terjual sebagai Kumala − 25 ke adukan. **Sesudah**
  hitungan itu 4 karung Kumala (200 kg) dibuka di belakang W5 dan 149,4 kg ditakar ke W5/W1. Hitungan 175 tidak mungkin memuat 200 kg yang dibuka
  sesudahnya → salah satu: hitungan 175 terlalu rendah, atau ada kedatangan Kumala yang belum dicatat. Dari data tidak bisa dibedakan.
- **Dry-run pindahan awal putaran 28** di cadangan: 8/8 wadah jadi, 17 dokumen, tidak ada yang dilewati — tetapi buku Kumala 13,85 → **−60,92** dan Pandan
  Wangi 10,19 → **−5,31**. Kalau tombol itu ditekan hari ini, dua buku merek jadi minus tanpa ada yang memutuskan (menulis hantu).

## 2. Akar

| | |
|---|---|
| FAKTA | Dua angka di kartu beda sifat: "bebas dijual" = langit-langit **buku merek asal** (model 27), "isi wadah" = **alat ukur** (tanda + takar − terjual). Keduanya benar menurut rumusnya masing-masing dan tidak pernah disebut selisihnya. |
| FAKTA | Model 28 (satu buku per wadah, "isi = buku") sudah ada di kode dan LULUS uji, tetapi belum aktif di data toko karena langkah owner sesudah merge (pindahan awal) tidak dilakukan. |
| FAKTA | Isi ulang 17:37 TERCATAT (takar 25,2 kg) tetapi hanya di alat ukur; tidak ada mekanisme yang menaikkan buku Kumala saat menuang (memang bukan desainnya — buku dipotong saat jual). |
| DUGAAN (owner) | "barang masuk dari pemasok belum tercatat" — cocok dengan data (200 kg dibuka sesudah hitungan 175), tetapi hitungan 27 Sep yang terlalu rendah juga cocok. Tidak bisa diputuskan dari data. |
| ASUMSI | Kotak W5 memang berisi ±59 kg (keterangan owner 29 Sep). Dipakai untuk menyimpulkan bahwa BUKU (Kumala) yang kurang, bukan alat ukur wadah. |

## 3. Keputusan owner (29 Sep) dipetakan ke kode

| Butir | Sudah ada (putaran 28, dormant) | Belum ada / berbeda |
|---|---|---|
| a. satu buku per wadah, semua peristiwa menulis ke buku itu, tanpa estimasi terpisah | buku `'Wadah <nama>'`, takar = pindah buku, literan memotong buku wadah, cocokkan wadah = penyesuaian buku wadah, `tinggiWadah`/`wbKomposisi` membaca buku saat aktif | aktivasi per wadah dengan **daftar keputusan** (bukan satu tombol untuk semua) bila buku merek asal kurang |
| b. isi ulang tiga ketukan di Jual (juga Stok): kotak ← merek asal dari rak × 1 karung / ½ karung / kg · jam · oleh siapa | takar dari karung yang **sudah dibuka** di belakang wadah (dua tingkat: buka karung → − / + takar 1,8 kg); atribusi `oleh`/`olehUid`/`jam` pusat | pilih merek asal langsung dari rak, takaran karung/½/kg tanpa mengetik, satu kiriman = takar + pindah buku; pintu Stok untuk owner |
| c. komposisi & banding turunan isi ulang, tampil di Jual · Stok · dashboard | komposisi per merek asal ada untuk model 27; saat aktif komposisi = 100 % buku wadah | komposisi turunan dari riwayat takar untuk wadah aktif + banding sederhana (3 : 2) + jam & siapa |
| d. buku merek asal kurang → tawarkan catat barang masuk / tandai untuk dicocokkan, sebut selisih | jalur 31b `perluCocokkan` + `selisihKg` untuk **nota** (owner saja) | jalur yang sama untuk **dokumen pindah buku takar**; kartu "belum dicocokkan" & pita membaca tanda dari takar |
| e. cek wadah di Tutup Hari (K5): sesuai / lupa isi ulang / dikosongkan, siapa & jam | K5 menulis `tutupHari` + langkah lain satu kiriman; sisihkan/tuang balik/bongkar karung wadah | kartu cek per wadah aktif di K5; tempat simpannya (§5 no. 4) |
| f. dua angka masih bisa beda → sebut selisihnya | — | kalimat selisih di kartu Jual, panel wadah, Stok, dashboard (wadah belum aktif: buku merek asal vs isi tercatat; wadah aktif: buku wadah vs hitungan fisik terakhir) |

Rules v4 hari ini: `wadahLiteran` **dan** `tutupHari` hanya boleh ditulis owner. Seluruh 27 takar di cadangan ditulis akun owner.

## 4. Tafsiran yang dipakai (dilanjutkan tanpa bertanya — jawabannya tidak mengubah hasil, biaya, atau risiko)

1. **Buku wadah = mekanisme putaran 28 yang sudah ada** (`'Wadah <nama>'`, lahir lewat batch 0 kg, pindah buku takar). Tidak ada koleksi baru.
2. **Aktivasi jadi per wadah**, lewat daftar: tiap wadah menulis isi tercatat, merek asal & bukunya, dan kekurangan (bila ada). Pilihan per wadah:
   *pindahkan* (buku cukup) · *catat barang masuk dulu* · *tandai untuk dicocokkan* (buku merek asal minus sebesar itu, bertanda) · *biarkan* (belum aktif).
   Wadah yang belum aktif tetap memakai model 27 sampai diputuskan; kartunya menyebut selisih (butir f).
3. **"Rak" untuk memilih merek asal** = calon yang sama dengan tiga pintu karung putaran 28: tumpukan gudang merek, kedatangan 14 hari, kemasan
   hasil adukan (buku sendiri), karung wadah. Karung yang sudah terbuka di belakang wadah tampil paling atas.
4. **Takaran**: "1 karung" = berat karung buku merek itu (50 atau 25 kg, `beratKarungBuka`); "½ karung" = separuhnya; "kg" = tuts angka (tanpa
   papan ketik). Melewati batas menggunung DITOLAK dengan kalimat, seperti sekarang.
5. **Komposisi turunan (butir c)** untuk wadah aktif = takar per merek sejak titik terakhir wadah kosong / dibongkar / disamakan, disebar sebanding ke
   buku wadah sekarang (campur rata — dasar putaran 27, `wbPecah` sebanding komposisi); banding = perbandingan takar disederhanakan (3 : 2, 1 : 1).
   Bukan lapisan (LIFO). Ditampilkan sebagai "Kumala 3 : NG 2 · ±58,9 kg ≈ 71,8 L · diisi 17:37 oleh …".
6. **Butir d untuk owner**: pola 31b — ketukan pertama menyebut "Buku Kumala tinggal 13,85 kg, dituang 25,2 kg — kurang 11,35 kg", dua tombol.
   "Tandai" = dokumen pindah buku membawa `perluCocokkan` + `selisihKg`; tuntas = cocokkan merek itu bertanggal ≥ dokumen. Tidak ada koleksi baru.
7. **Asap cadangan**: (i) tiap wadah aktif: Σ takar masuk − Σ literan keluar ± penyesuaian = buku wadah; (ii) tiap merek asal: tumpukan + karung terbuka
   + Σ bagian merek itu di wadah (komposisi turunan) = buku merek + Σ pindah keluar ke wadah − Σ pindah masuk; (iii) ASAP GLOBAL laba/neraca/nilai stok
   byte-sama dengan `main` selama tidak ada dokumen baru ditulis.
8. **Data lama tidak diubah diam-diam**: tidak ada migrasi; daftar §6 = pekerjaan owner.

## 5. Pertanyaan untuk owner — mengubah hasil

1. **Karung di belakang wadah: buku mesin sendiri atau tetap kolam?** Catatan owner 29 Sep: "tumpukan di gudang > karung di belakang wadah > wadah, setiap
   stok punya bukunya masing-masing". Dua cara: (A) karung di belakang tetap **kolam alat ukur di dalam buku merek** (seperti sekarang: buka karung =
   tumpukan turun di layar, buku merek tetap; takar = pindah buku merek → wadah); atau (B) karung di belakang jadi **buku mesin** `'Karung belakang <wadah>'`
   (buka karung = pindah buku merek → karung belakang; takar = pindah buku karung belakang → wadah; dua dokumen pindah per isi ulang; identitas asap
   bertambah satu tingkat). A lebih sedikit dokumen dan tidak menyentuh laporan; B membuat sisa karung di belakang wadah ikut dinilai sebagai buku sendiri.
2. **Siapa boleh menandai "untuk dicocokkan" saat isi ulang?** 31b memutuskan owner saja untuk nota. Kalau karyawan yang menuang dan buku merek kurang,
   pilihannya: (A) karyawan hanya boleh "catat barang masuk dulu" / memanggil owner, (B) karyawan boleh menandai dengan namanya tercatat.
3. **Rules v5?** Hari ini `wadahLiteran` dan `tutupHari` hanya owner. Butir b ("tempat karyawan menuang") dan e (karyawan mengonfirmasi tiap kotak) butuh
   karyawan menulis: (A) rules v5 — `wadahLiteran` boleh ditulis karyawan (`olehUid` wajib, tanpa hapus), cek wadah ikut di `tutupHari` yang ditulis owner
   saat menutup; atau (B) tanpa rules baru — isi ulang & cek tetap ditulis akun owner (seperti 27 takar di cadangan), karyawan memberi tahu owner.
   Rules diterbitkan owner lewat Console (pola putaran 25).
4. **Arti "dikosongkan" di cek Tutup Hari**: (A) seluruh isi disisihkan ke karung wadah (pindah buku, tanpa timbang — pola *sisihkan* 28), atau (B) bongkar
   ditimbang (selisih = susut wadah — pola *bongkar* 28).
5. **Panel "− / + takar" 1,8 kg** yang ada: dicabut (diganti tiga ketukan) atau tetap tersedia sebagai "takaran lain"?
6. **Aktivasi W5 dan W7 hari ini** (§6): pilih *tandai untuk dicocokkan* (buku Kumala jadi −45,0 & Pandan Wangi −5,3, bertanda) atau *hitung / catat
   barang masuk dulu* lalu pindahkan. Ini keputusan data, bukan desain.

## 6. Data lama yang sudah terlanjur berbeda — daftar per wadah (owner memutuskan)

| Wadah | Isi tercatat | Dipindah dari | Buku merek asal sekarang | Kekurangan bila dipindahkan |
|---|---|---|---|---|
| W1 IR64 Apex | 43,48 | IR64 Apex 27,58 · Kumala 15,90 | 100,84 · 13,85 | Kumala **−2,05** (bersama W5) |
| W2 Angsa | 51,28 | Angsa 34,80 · IR64 Apex 16,48 | 491,72 · 100,84 | — |
| W3 Perahu Layar | 45,99 | Perahu Layar 45,99 | 69,56 | — |
| W4 IR42 Select | 59,72 | IR42 Select 50,72 · IR42 Value 9,00 | 66,48 · 233,42 | — |
| W5 IR64 Elevate | 58,87 | Kumala 58,87 | 13,85 | Kumala **−45,02** (−60,92 bersama W1) |
| W6 IR64 Ascent | 35,86 | IR64 Ascent 35,86 | 170,86 | — |
| W7 Pandan Wangi | 15,50 | Pandan Wangi 15,50 | 10,19 | **−5,31** |
| W8 IR42 Value | 18,84 | IR42 Value 18,84 | 233,42 | — |

Tumpukan yang sudah minus di layar hari ini (belum dipindahkan apa pun): Kumala −97,52 · IR42 Select −32,04 · Pandan Wangi −28,31 — ketiganya perlu
hitung fisik (tumpukan + karung terbuka) atau kedatangan yang belum dicatat. Tabel ini hanya menghitung isi kotak; sesudah jawaban no. 1 (§8) daftar
aktivasi juga memindahkan karung terbuka di belakang wadah, jadi kekurangan yang tampil di layar lebih besar — angkanya di §8.4 no. 4.

## 7. Uji yang direncanakan

`uji_wadah_stok_sendiri.py` & `uji_wadah_bernama.py` diperluas (+ kontrol): aktivasi per wadah & daftar keputusan; isi ulang tiga ketukan (1 karung / ½ /
kg) = takar + pindah buku satu kiriman; buku kurang → kalimat selisih & dua jalur; komposisi turunan & banding; cek Tutup Hari; kalimat selisih (butir f).
Asap cadangan seperti §4 no. 7. Uji baru `uji_wadah_satu_buku.py` untuk yang tidak muat di keduanya.

## 8. Keputusan owner (29 Sep) & yang dibangun — cabang `wadah/39-satu-buku`

Enam pertanyaan §5 dijawab owner 29 Sep 2026. Inti logika ada di dua commit cabang ini: `de65807` (peta §1–§7) dan `c079fa8` (rules v5 + akses +
`toko.js` + `wadah-bernama-logika.js` + `jual-logika.js`). Layar sudah digabung ke cabang ini: `5971250` (Stok › Wadah literan), `b5d4dc0` (Jual + panel wadah),
`e215c1c` (Uang › Tutup hari K5), `041b9c2` (tambalan silang layar) — rinciannya di §8.2 baris "Layar". Uji `uji_wadah_satu_buku.py` disusun di cabang uji
putaran 39 (step CI-nya sudah ada di `pages.yml`; sampai berkasnya digabung, step itu merah). Angka di §8 **kg**; tanpa rupiah; tanpa nama orang.

### 8.1 Enam jawaban owner → nomor pertanyaan §5

| §5 | Jawaban owner | Yang dibangun |
|---|---|---|
| **1** karung di belakang wadah | **(B) buku mesin sendiri** — "karung di belakang wadah jadikan buku mesin tersendiri; diambil dari tumpukan gudang, tumpukannya berkurang" | Buku `'Karung belakang <wadah> · <merek>'` per wadah × merek asal (`data/toko.js`: `kunciKarungBelakang`, `petaBukuWadah()` jenis `'belakang'` + `merk`, `merkAsalKunci`). Buka karung = pindah buku merek → karung belakang (tumpukan gudang turun **di buku** saat itu juga); tuang / takar = pindah buku karung belakang → wadah. Catatan kolam `karung` / `takar` tetap ditulis (bernama kunci bukunya, `merkAsal` = merek pemasok) supaya deretan karung, panel, dan tanggal tetap terbaca; selisih kolam vs buku DISEBUT (butir f). Karung LAMA bernama merek (dibuka sebelum putaran ini) di belakang wadah aktif dipakai sampai habis lewat jalur lama; karung berikutnya lahir sebagai buku. |
| **2** siapa boleh menandai | **(B) karyawan boleh menandai, namanya tercatat** | `{ tolak, perluTandai: [{ merk, buku, butuh, kurang }] }` dari `wbDokBukaKB` / `wbSusunIsiUlangTiga` / `susunTakarWadah` / `susunBukaKarung` / `wbSusunAktifkan`; ketukan kedua `opsi { tandai: true }` → dokumen pindah buku bertanda `perluCocokkan` + `selisihKg` + `selisihPerMerk`; `oleh` / `olehUid` diisi atribusi pusat (`beriAtribusiAkun`). Rules v5 membuka `wadahLiteran` takar/karung dan `produksiKemasan` (sudah sejak v3) untuk karyawan, jadi tandanya ditulis akun yang menuang. Tuntas = cocokkan merek itu bertanggal ≥ dokumen (pola 31b): `wbPindahTembusBelumCocok()` digabung ke `L.notaTembusBelumCocok()` → pita Jual & kartu keempat Gudang otomatis. |
| **3** rules v5? | **(A) rules v5, diterbitkan owner lewat Console** | `firestore.rules` v5: `wadahLiteran` create oleh `ben` / `karyawan` hanya tipe `takar` · `karung` · `karungIsi` · `cek` (`stafBuatWadah`); `batchMasuk` create hanya batch LAHIR BUKU 0 kg (`stafBuatLahir`); `olehUid` wajib (`jujur()`), tanpa update / delete. **Tafsiran:** cek wadah disimpan sebagai `wadahLiteran` tipe `'cek'` — bukan di `tutupHari` — supaya karyawan mencatatnya sendiri saat tutup toko dan `tutupHari` tetap owner. Penjaga perangkat berkata sama (`akses.js`: `TIPE_WADAH_STAF`, `batchLahir`, `SERVER_BUKA.isiUlang`); kisi SS2 dapat tindakan ke-14 `isiUlang`. Jalan mundur `firestore.rules.v4`. Kasus Playground: `docs/uji-rules-v5.md`; rincian hak: `docs/peta-hak-akses.md` §9. |
| **4** arti "dikosongkan" | **(A) seluruh isi disisihkan ke karung wadah tanpa timbang** (pola *sisihkan* 28) | `wbSusunCek(W, 'kosong', w)` = `wbSusunSisih(W, seluruh buku wadah)` + catatan `cek`; kotak jadi 0, karung wadah naik sebesar itu, stok toko tidak berubah (pindah buku, modal ikut). Butuh wadah aktif; wadah belum aktif ditolak dengan kalimat. |
| **5** panel − / + takar 1,8 kg | **tetap tersedia sebagai "takaran lain"** | `susunTakarWadah` tetap (catatan `takar` ber-`takaran: 'takar'`); tiga ketukan = `wbSusunIsiUlangTiga` (`takaran: 'karung'` \| `'setengah'` \| `'kg'`). Di wadah aktif keduanya memindah buku lewat karung belakang. |
| **6** aktivasi W5 & W7 | **hitung fisik / catat barang masuk DULU, baru pindahkan** (bukan "tandai") | Daftar aktivasi per wadah (`wbDaftarAktivasi()` → `wbSusunAktifkan(W, w, opsi)`) menyebut kekurangan tiap wadah dan menolak tanpa `opsi.tandai`; W5 & W7 = tugas owner §8.6 dengan angka §6. `wbSusunPindahAwal` (28, semua wadah sekaligus) tidak dipakai layar lagi. |

### 8.2 Bagian → berkas → fungsi → uji

| Bagian | Berkas | Fungsi | Uji |
|---|---|---|---|
| Kunci & peta buku karung belakang | `baru/js/data/toko.js` | `kunciKarungBelakang(W, merk)`, `petaBukuWadah()` (jenis `'belakang'`), `merkAsalKunci(kunci)` | `uji_wadah_satu_buku.py`; `uji_wadah_stok_sendiri.py` (tutup buku membawa tanda) |
| Karung belakang: buku vs kolam | `baru/js/layar/wadah-bernama-logika.js` | `wbKunciKB`, `wbMerkAsal`, `wbBukuKhusus`, `wbKarungBelakang(W, M)`, `wbKarungBelakangWadah(W)` | `uji_wadah_satu_buku.py` |
| Buka karung di belakang wadah aktif | `wadah-bernama-logika.js`, `jual-logika.js` | `wbDokBukaKB(W, M, n, w, opsi, sesudah)`; `susunBukaKarung(merk, w, wadah, asal, opsi)`; `beratKarungBuka` (lewat merek asal); `deretanKarung` (label merek asal, `k.merk` = kunci) | `uji_wadah_satu_buku.py`; `uji_jual_baru.py` (jangkar kontrol) |
| Isi ulang tiga ketukan | `wadah-bernama-logika.js` | `WB_TAKARAN`, `wbSusunIsiUlangTiga(W, M, takaran, w, s, opsi)` | `uji_wadah_satu_buku.py`; `peta_akses.py --kiriman` (isi ulang wadah 6 / 20) |
| Panel − / + takar (takaran lain) | `jual-logika.js` | `susunTakarWadah(merk, baris, w, s, opsi)`, `hitungTakar` (`bukuBelakang`, `merkAsal`) | `uji_jual_baru.py`, `uji_wadah_stok_sendiri.py` |
| Aktivasi per wadah | `wadah-bernama-logika.js` | `wbDaftarAktivasi()`, `wbSusunAktifkan(W, w, opsi)` | `uji_wadah_satu_buku.py` (asap cadangan: kekurangan W5 & W7 disebut, tidak ditulis) |
| Buku kurang → tandai untuk dicocokkan | `wadah-bernama-logika.js`, `jual-logika.js` | `{ tolak, perluTandai }` + `opsi.tandai` di kelima penyusun; `wbPindahTembusBelumCocok()`; `notaTembusBelumCocok()` (gabungan) | `uji_wadah_satu_buku.py`; `uji_jual_tandai_cocok.py` (pita & kartu keempat) |
| Komposisi turunan & banding | `wadah-bernama-logika.js` | `wbKomposisiTurunan(W, s)` | `uji_wadah_satu_buku.py` |
| Cek wadah tutup toko | `wadah-bernama-logika.js` | `WB_CEK`, `wbCekHari(iso)`, `wbSusunCek(W, hasil, w)` | `uji_wadah_satu_buku.py`; `peta_akses.py --kiriman` (cek dikosongkan / lupa) |
| Dua angka satu kotak → selisih | `wadah-bernama-logika.js` | `wbSelisihWadah(W, s, bebasLiter)` | `uji_wadah_satu_buku.py` |
| Layar Stok & Papan Kapur | `baru/js/layar/stok-logika.js` | `susunWadah` (`karungAsal`, tumpukan merek asal), `susunKapur` (baris buka karung berbuku, cek, tanda KURANG) | `uji_stok_baru.py` (jangkar kontrol) |
| Tebakan kelas mutu | `kelas-merek-logika.js` | `kmTebak` (mengenal `merkAsal`) | `uji_kelas_merek.py` |
| Tutup buku | `tutup-buku-logika.js` | `pembukaBuku` (baris membawa `karungBelakang` + `merkAsal`) | `uji_wadah_stok_sendiri.py` (kontrol "tutup buku kehilangan tanda stok wadah") |
| Akses & rules v5 | `baru/js/data/akses.js`, `sistem-logika.js`, `firestore.rules`, `firestore.rules.v4` | `BUAT_STAF` (+ `wadahLiteran`, `batchMasuk`), `TIPE_WADAH_STAF`, `batchLahir`, `SERVER_BUKA.isiUlang`, `TINDAKAN_DARI`; `SS_TINDAKAN` ke-14; `stafBuatWadah`, `stafBuatLahir` | `periksa_rules.py`, `uji_akses_baru.py`, `uji_menu_baru.py`, `peta_akses.py --kiriman`; server: `docs/uji-rules-v5.md` |
| Layar Stok › Wadah literan | `stok.js`, `stok.css` | kartu "Aktivasi buku wadah — per wadah, owner memutuskan" (`wbDaftarAktivasi`: satu baris per wadah · status · isi tercatat · tabel sumber merek asal di wadah / di karung / buku / kurang · AKTIFKAN dua ketukan · TANDAI UNTUK DICOCOKKAN lewat pita `pita-tandai` (`tandaiMasuk` / `tandaiTulis` / `tandaiBatal`) · "Hitung fisik <merek> dulu" ke Cocokkan › Tumpukan gudang · "Catat barang masuk"; tombol lama "semua sekaligus" dicabut); kartu "Karung di belakang wadah … · buku sendiri per merek" (`wbKarungBelakangWadah`: buku · catatan · selisih → `samakanKarung` dengan merk = kunci buku); komposisi turunan, selisih, status cek hari ini; bukan-owner: tombol MATI dengan kalimat | `uji_stok_baru.py`, `uji_wadah_stok_sendiri.py`, `uji_isian_lokal.py`, `uji_kinerja_gerak.py`, `uji_onclick_aman.py`, `uji_akses_baru.py` |
| Panel wadah (Jual & Stok) | `wadah-panel.js`, `jual.css` | tiga ketukan `wdMerkTiga` (rak: karung terbuka di belakang wadah dulu, lalu tumpukan gudang; karung wadah diarahkan ke Stok) → `wdTakaranTiga` / `wdTutsTiga` (1 karung · ½ karung · kg lewat tuts angka ke draf panel) → `wdIsiTiga` (`wbSusunIsiUlangTiga`, satu kiriman); kepala "Isi wadah = buku ±X kg" + komposisi turunan + selisih karung belakang; pita dua pintu `wdKeStok` / `wdTandaiBatal`; panel − / + tetap sebagai "Takaran lain" (`wdCatat` meneruskan opsi); wadah belum aktif = panel lama + "aktifkan di Stok › Wadah literan" | `uji_jual_baru.py`, `uji_isian_lokal.py`, `uji_kinerja_gerak.py` |
| Layar Jual › Literan | `jual.js` | chip wadah: baris komposisi (merek asal · jam · siapa) + awas selisih dua angka; tombol "Cek wadah · N/M hari ini" → lembar `cekWadah` (per wadah aktif: buku · status cek · sesuai / lupa isi ulang / dikosongkan dua ketukan menyebut kg; "lupa" membuka chip wadah dengan panel isi ulang terbuka; wadah belum aktif redup); kepala lembar jumlah menyebut "(buku merek asal)" bila belum aktif | `uji_jual_baru.py` |
| Uang › Tutup hari (K5) | `uang.js`, `uang.css`, `app.js` | kartu "Cek wadah" di antara Timbang cepat & Amankan laci — kartu, bukan langkah `LANGKAH_TUTUP` (rekap & indeks tidak bergeser; belum semua dicek tidak menahan tutup hari, hanya disebut N dari M); per wadah aktif tiga tombol → `wbSusunCek` lewat pintu tulis `uang.js`; "lupa" sukses → tombol ke Stok › Wadah literan (`bukaStok` dari `app.js`); Timbang cepat menyaring kunci `petaBukuWadah` | `uji_uang_baru.py` |
| Tambalan silang layar (`041b9c2`) | `app.js`, `jual-logika.js`, `stok.js` | panel Stok meneruskan akun (`opsi.akun`) → tombol mati untuk peran tanpa hak; `susunSamakanKarung` untuk buku karung belakang: batas sisa = yang lebih besar antara berat satu karung merek asal dan bukunya (dua karung dibuka menumpuk); K5 → `bukaStok` | `uji_jual_baru.py`, `uji_stok_baru.py` |

### 8.3 Dokumen yang ditulis tiap jalur (bentuk persis)

Semua dokumen: `id: w.idUnik()`, `tanggal`, `jam` dari `L.waktuSekarang(...)`. `oleh` / `olehUid` / `perangkat` / `diubah*` diisi penulis pusat
(`beriAtribusiAkun`) — logika & layar tidak mengisinya; tampilan "oleh …" toleran kosong (cadangan tanpa atribusi).

1. **Batch lahir buku** (`batchMasuk`, `wbDokLahir`) — satu per kiriman bila ada buku baru:
   `{ pemasok: 'LAHIR BUKU', caraBayar: 'tunai', biayaBongkar: 0, stokAwal: true, lahirBuku: true, merkList: [{ id: '1', merk: <kunci>, satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, … }] }`
   dengan tanda per jenis buku di barisnya: `stokWadah: W` (buku wadah) · `karungWadah: W` (karung wadah, 28) · `bukuAdukan` (28) · **`karungBelakang: W` + `merkAsal: M`** (39).
   Rules v5 `stafBuatLahir` menilai `lahirBuku`, `stokAwal`, `biayaBongkar == 0`, `pemasok == 'LAHIR BUKU'`; perangkat (`batchLahir`) juga menolak `merkList` ber-`totalKg` / `subtotalHarga`.
2. **Pindah buku** (`produksiKemasan`, `wbDokPindah(sumber, tujuan, w, ekstra)`), inti:
   `{ dariTakar: true, jadiKarungUtuh: true, merkSumber: 'M' (dua sumber: 'M1 + M2'), namaProduk: <tujuan>, merkTujuan: <tujuan>, ukuranKemasan: kg, jumlahUnit: 1, sumberList: [{ merk, kg }], kgDipakai: kg, hppSumberPerKgDipakai, hppPerUnit (modal yang ikut), batchProduksi: id, barisKe: 1, jumlahBaris: 1, biayaKemasan: 0, upahRepacking: 0, kantongJenis: null, kantongJumlah: 0, sumberKemasanList: [], kgKemasanDipakai: 0 }` + tanda jalur:
   - buka karung di belakang wadah aktif: `{ bukaKarung: W, merkAsal: M, keterangan }` (+ **`perluCocokkan: true, selisihKg, selisihPerMerk: { M: kurang }`** bila ditandai);
   - tuang tiga ketukan: `{ takarId: <id catatan takar>, merkAsal: M, keterangan }`; panel − / +: `{ takarId, keterangan }`;
   - aktivasi — isi kotak: `{ pindahAwalWadah: W, keterangan }` (+ tanda); karung terbuka lama: `{ bukaKarung: W, merkAsal: M, pindahAwalWadah: W, keterangan }` (+ tanda);
   - sisihkan (cek "dikosongkan"): `{ sisihWadah: W, keterangan }` (28).
3. **`wadahLiteran`** per tipe:
   - `karung` berbuku (satu catatan per karung): `{ tipe: 'karung', merk: 'Karung belakang W · M', merkAsal: M, kg: <berat karung M>, wadah: W, bukuBelakang: true, produksiId }` (+ `otomatis: true` bila dibuka karena karung habis saat takar; + `asal: 'masuk', batchId` dari pintu "baru datang").
   - `takar` tiga ketukan: `{ tipe: 'takar', wadah: W, takar, kgPerTakar, kg, takaran: 'karung' | 'setengah' | 'kg', sumber: [{ merk: 'Karung belakang W · M', merkAsal: M, takar, kg, dari: W }], stokWadah: 'Wadah W', produksiId }`; panel − / +: `takaran: 'takar'`, `sumber[].merkAsal` hanya bila beda dari `merk`.
   - `karungIsi` aktivasi (dua per karung terbuka lama): `{ tipe: 'karungIsi', merk: M, isiKg: 0, wadah: W, pindahAwal: true }` (kolam lama bernama merek ditutup) dan `{ tipe: 'karungIsi', merk: 'Karung belakang W · M', merkAsal: M, isiKg: kg, wadah: W, bukuBelakang: true, pindahAwal: true }`.
   - `karungIsi` samakan karung belakang berbuku (`susunSamakanKarung` — tombol "samakan karungnya" di Stok, `wdSamakan` di panel): `{ tipe: 'karungIsi', merk: 'Karung belakang W · M', isiKg, wadah: W }` — tanpa `merkAsal` (merek asal dibaca dari kuncinya, `merkAsalKunci`); batas `isiKg` = yang lebih besar antara berat satu karung merek asal dan buku karung belakang itu (dua karung dibuka menumpuk, `041b9c2`).
   - `isi` aktivasi: `{ tipe: 'isi', wadah: W, isiKg, stokWadah: 'Wadah W', pindahAwal: true, komposisi: { M: kg, … } }` — komposisi awal = bahan komposisi turunan.
   - `cek`: `{ tipe: 'cek', wadah: W, hasil: 'sesuai' | 'lupa' | 'kosong', bukuKg }` (+ `stokWadah` bila wadah aktif).
   - sisihan di cek "dikosongkan": `{ tipe: 'karung', merk: 'Karung wadah W', kg, lepas: true, asal: 'wadah', dariWadah: W, sisih: true }` (28).
4. **Satu kiriman per jalur** (urutan dokumen):
   - isi ulang tiga ketukan, karung belakang kosong: [lahir (bila buku belum ada), pindah M → karung belakang, `karung` × n, `takar`, pindah karung belakang → wadah] = 4–5 dokumen; dari karung yang sudah terbuka: [`takar`, pindah] = 2;
   - aktivasi satu wadah: [lahir (wadah + tiap karung belakang), pindah isi, `isi`, per karung terbuka lama: pindah + 2 `karungIsi`];
   - cek: [`cek`]; "dikosongkan": [lahir karung wadah (bila belum), pindah, `karung` sisihan, `cek`].

### 8.4 Identitas asap (`uji_wadah_satu_buku.py`, cadangan toko; dilewati di CI)

1. Tiap wadah aktif: Σ takar masuk − Σ literan keluar ± penyesuaian bertanda wadah = buku `'Wadah W'` (`hitungStokKarungPerMerk`); Σ komposisi turunan = buku itu (bukan angka kedua).
2. Tiap pindah buku: Σ kg sumber = kg tujuan dan modal ikut → Σ nilai stok seluruh buku tetap. Per merek asal: buku merek + Σ buku karung belakang merek itu + Σ bagian merek itu di wadah (turunan) = buku merek sebelum pindah (kg).
3. Tiap karung belakang: kolam (catatan `karung` − takar) vs buku — selisih disebut lewat `wbSelisihWadah`, tidak dijumlah dua kali di rantai stok.
4. Daftar aktivasi di cadangan 29 Sep menghitung isi kotak **+ karung terbuka di belakangnya** (jawaban no. 1), jadi kekurangannya lebih besar dari §6 yang
   hanya menghitung isi kotak: W1 Kumala kurang 2,05 · W4 IR42 Select kurang 32,04 (50,72 + karung 47,8 lawan buku 66,48) · W5 Kumala kurang 81,62 (58,87 +
   karung 36,6 lawan buku 13,85) · W7 Pandan Wangi kurang 28,31 (15,5 + karung 23 lawan buku 10,19); W2 W3 W6 W8 cukup. Tidak ada dokumen yang ditulis tanpa `opsi.tandai`.
5. ASAP GLOBAL: laba / neraca / nilai stok tiap bulan byte-sama dengan `main` selama tidak ada dokumen baru ditulis (semua bentuk dokumen sudah dibaca mesin sejak 28).

### 8.5 Yang TIDAK berubah

- **28 mesin beku** (`js/mesin/beku.js` byte-identik, `pindah_mesin.py --periksa`); tidak ada koleksi baru; bentuk dokumen = putaran 28 (batch lahir 0 kg, `produksiKemasan` jadi-karung-utuh, `wadahLiteran`, `penyesuaianStok`).
- **Laba & neraca**: pindah buku membawa modal (`hppPerUnit`), nilai stok total tetap; literan memotong buku wadah seperti 28; tanda `perluCocokkan` tidak mengubah angka (buku dibiarkan minus, seperti 31b).
- `index.html` / `kasir*.html` / katalog kasir tidak disentuh. Kunci periode v4 tetap: `wadahLiteran` tetap tidak dikunci periode; batch lahir & pindah buku dinilai `tglStaf` / `tglBaru` seperti biasa.
- Wadah yang belum aktif tetap model 27 (`bebasLiterWadah` = langit-langit buku merek asal) — kini dengan kalimat selisih (`wbSelisihWadah`) yang mengajak mengaktifkan.
- Tetap owner: `tutupHari`, aturan wadah (`atur`), titik samakan isi (`isi`), cocokkan (`penyesuaianStok`), kedatangan sungguhan (`batchMasuk` berisi kg / harga).

### 8.6 Tugas owner sesudah merge

1. **Terbitkan rules v5 lewat Console** — urutan & kasus ★ di `docs/uji-rules-v5.md`: salin-tempel `firestore.rules` utuh, pastikan kepala editor
   "ATURAN FIRESTORE v5", Playground ★ dulu, baru Publish. Mundur = tempel `firestore.rules.v4`. Sampai v5 terbit, isi ulang & cek dari akun karyawan
   ditolak server (masuk daftar ditolak); akun karyawan belum ada (gerbang tablet), jadi tidak ada antrean yang macet.
2. **Aktivasi per wadah dari daftar** (Stok › Wadah literan). Menurut §6: W2 Angsa · W3 Perahu Layar · W4 IR42 Select · W6 IR64 Ascent · W8 IR42 Value
   bukunya cukup → pindahkan. W1 IR64 Apex kurang Kumala 2,05 bersama W5 → sesudah W5 beres.
3. **W1, W4, W5, W7: hitung fisik / catat barang masuk DULU** (jawaban no. 6): daftar aktivasi memindahkan isi kotak + karung terbuka di belakangnya
   (§8.4 no. 4), jadi yang kurang: W1 Kumala 2,05 · W4 IR42 Select 32,04 · W5 Kumala 81,62 · W7 Pandan Wangi 28,31 (angka §6 hanya isi kotaknya);
   tumpukan yang sudah minus di layar: Kumala −97,52 · IR42 Select −32,04 · Pandan Wangi −28,31. Hitung tumpukan + karung terbuka di Stok › Cocokkan ›
   Tumpukan gudang, atau catat kedatangan yang belum tercatat di Stok › Barang masuk — baru pindahkan dari daftar (tanpa "tandai"). W2, W3, W6, W8 cukup.
4. Sesudah wadah aktif: isi ulang lewat **tiga ketukan** (panel wadah di Jual › Literan & Stok › Wadah literan) — merek asal dari rak × 1 karung / ½ karung /
   kg; **cek tiap wadah aktif** saat tutup toko di Uang › Tutup hari (K5) atau lembar "Cek wadah" di Jual › Literan: sesuai / lupa isi ulang / dikosongkan.
   "Lupa isi ulang" langsung menawarkan pintu ke wadahnya (K5 → Stok › Wadah literan; Jual → chip wadah dengan panel isi ulang terbuka).
5. Karung lama bernama merek di belakang wadah aktif dipakai sampai habis; karung berikutnya lahir sebagai buku karung belakang. Selisih kolam vs buku
   yang disebut kartu → samakan karungnya.
