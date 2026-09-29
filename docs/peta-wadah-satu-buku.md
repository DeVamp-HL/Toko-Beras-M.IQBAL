# Peta wadah literan SATU BUKU per kotak — putaran 39, Tahap 0

**Status (29 Sep 2026): akar ditemukan, belum ada perubahan perilaku.** Dokumen ini = bukti dari cadangan, akar (fakta / dugaan / asumsi), pemetaan
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
hitung fisik (tumpukan + karung terbuka) atau kedatangan yang belum dicatat.

## 7. Uji yang direncanakan

`uji_wadah_stok_sendiri.py` & `uji_wadah_bernama.py` diperluas (+ kontrol): aktivasi per wadah & daftar keputusan; isi ulang tiga ketukan (1 karung / ½ /
kg) = takar + pindah buku satu kiriman; buku kurang → kalimat selisih & dua jalur; komposisi turunan & banding; cek Tutup Hari; kalimat selisih (butir f).
Asap cadangan seperti §4 no. 7. Uji baru `uji_wadah_satu_buku.py` untuk yang tidak muat di keduanya.
