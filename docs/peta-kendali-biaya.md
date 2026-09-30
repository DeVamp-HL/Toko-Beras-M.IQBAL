# Peta kendali biaya (cost controlling) — putaran 38

**Status (29 Sep 2026): dibangun di cabang `kendali/38-kendali-biaya`, menunggu pemeriksaan owner sebelum merge.** Tidak ada perilaku uang yang
berubah: 28 mesin beku utuh, dan `uji_kendali_biaya.py` membuktikan laba tiap bulan **byte-sama** dengan `main` (ASAP GLOBAL). Yang baru:
satu keluarga di Laporan (**Biaya**), satu modul logika tanpa DOM (`baru/js/layar/kendali-biaya-logika.js`), satu dokumen setelan owner
(`aturanToko/kendaliBiaya`). Angka di dokumen ini **jumlah catatan atau contoh**, bukan rupiah toko.

## 1. Apa itu kendali biaya, dalam bahasa toko

Cost controlling (kendali biaya) bukan "hemat". Ia lima kebiasaan yang, kalau jalan, membuat owner tahu **ke mana margin kotor pergi sebelum
bulannya habis**, bukan sesudahnya:

| # | Kebiasaan | Dalam bahasa toko | Yang dibutuhkan |
|---|---|---|---|
| 1 | Klasifikasi biaya | tiap rupiah keluar punya *jenis* (upah, listrik, kresek, kopi karyawan, potongan QRIS…) | pemilahan yang konsisten |
| 2 | Anggaran (standar) | angka yang *diputuskan* per jenis per bulan — bukan angka yang *kejadian* | keputusan owner, ditulis |
| 3 | Aktual vs anggaran | selisihnya kelihatan tiap hari, bukan akhir bulan; lampu, bukan tabel | jatah sampai hari ke-N |
| 4 | Pemicu (cost driver) | biaya per satuan yang membuat rupiahnya naik: per kg, per hari kerja, per lembar, per kedatangan | kg & hari, bukan cuma rupiah |
| 5 | Titik impas & peringatan | omzet berapa supaya margin menutup biaya; siapa yang bengkak; ke mana harus dilihat | rasio margin + peringatan bertujuan |

Sistem sudah punya sebagian besar bahan mentahnya sejak putaran 19 (mesin laba, HPP tertimbang), 24 (jatah bulanan), dan 29 (`untuk` = toko /
karyawan, kartu "Laba kotor → ke mana"). Yang belum ada: pemilahan **jenis**, **anggaran owner**, **selisih & lampu**, **pemicu bertren**, dan
**titik impas**. Putaran 38 menambahkan kelimanya sebagai lapisan baca di atas mesin yang sama.

## 2. Jenis biaya & urutan pemilahan

Baris di bawah margin kotor, urutannya = urutan pemilahan (yang di atas menang):

| Jenis | Sifat | Dari mana |
|---|---|---|
| Upah & gaji | tetap | baris gaji Tagihan bulanan, **kotor** sebelum potongan kasbon (sama dengan mesin laba) |
| Tagihan tetap | tetap | listrik · internet · akses/gapura · keamanan (Tagihan bulanan) |
| Potongan QRIS & biaya bank | variabel | catatan bertanda `mdr`, biaya admin bayar bon / pindah uang, atau kata kunci |
| Karyawan di luar upah | variabel | kolom `untuk` = karyawan (putaran 29) atau kata kunci (kopi, rokok, makan…) |
| Bahan pakai & kresek | variabel | kata kunci (plastik, kantong, lakban, benang…) — operasional, bukan HPP (keputusan 2 Agu 2026) |
| Bensin & angkut | variabel | kata kunci (bensin, ongkos, kuli…) — bongkar mobil pemasok **tidak** di sini, sudah di HPP |
| Dapur toko | variabel | kata kunci (kebutuhan masak, telur, gas…) — bahan masak = biaya toko (owner 27 Sep 2026) |
| Lain-lain | variabel | tidak cocok kata mana pun — **tetap dihitung**, disebut "belum dipilah" |
| Hapus buku piutang | — | mesin laba (di bawah laba kotor) |
| Susut & selisih stok | — | mesin laba; positif = stok berkurang = biaya; boleh diberi anggaran = toleransi |

Urutan pemilahan satu catatan uang keluar (`kategori` toko / tokoDompet; `owner` = prive, bukan biaya):
**tanda MDR / biaya bank → `untuk` = karyawan → kata kunci owner (semua jenis) → kata kunci bawaan → lain-lain.**
Kata dicocokkan sebagai **awalan kata di batas kata**: "roko" kena "rokok" dan "rokok mang X", "biaya admin" kena "biaya admin bi-fast",
tetapi "donasi" tidak kena "nasi". Kata kunci bawaan adalah tebakan awal; owner menimpanya lewat kartu Atur atau kartu "Belum dipilah"
(ketuk keterangan → pilih jenis → keterangannya jadi kata kunci owner, berlaku untuk semua catatan yang keterangannya diawali kata itu,
sekarang dan seterusnya). Satu kata hanya boleh hidup di satu jenis.

Pemilahan **wajib menutup** ke mesin laba, dan layar berkata terus terang kalau tidak:
`Σ jenis harian = harianToko` · `upah + tetap = jatahBulanan` · `margin − Σ jenis − hapus buku − susut = laba bersih`.

## 3. Anggaran, lampu, perkiraan, acuan

- Anggaran = **setelan owner** per jenis per bulan di `aturanToko/kendaliBiaya` (dibaca `aturKendali()`), 0/kosong = belum diatur = lampu mati.
  Ikut: ambang lampu (%), ambang pemicu (%), kata kunci tambahan per jenis. Rules v4 sudah mengizinkan owner menulis id apa pun di `aturanToko`.
- Tanpa anggaran, yang tampil hanya **acuan terukur** = median ≤ 3 bulan sebelumnya yang punya catatan jenis itu (bulan sebelum awal buku tidak
  ikut). "Isi dari acuan" mengisi *formulir* (dibulatkan ke ribuan) — yang menjadi anggaran adalah yang owner SIMPAN.
- Lampu: hijau (≤ dasar) · amber (lewat ≤ ambang %) · merah. **Dasar** bulan berjalan untuk jenis variabel = anggaran × hari jalan ÷ hari bulan
  (jatah sampai hari ke-N); jenis tetap & bulan lampau = anggaran sebulan. Baris variabel bulan berjalan juga diberi **perkiraan sebulan**
  (linear dari hari yang sudah jalan — perkiraan, bukan ramalan).
- Upah: yang dibandingkan = upah dibayar **+ upah yang belum dibayar** (dari absen & tarif, `upah-logika`), supaya bulan yang belum gajian tidak
  terbaca hemat. Ini [PERKIRAAN] — bukan angka mesin laba, dan disebut begitu di layar.
- Anggaran bukan larangan (aturan jatah 22 Agu 2026): lewat tetap tersimpan; bedanya kelihatan hari itu di lampu & kartu "Yang perlu dilihat".

## 4. Pemicu biaya (per satuan, bulan ini vs bulan lalu)

| Pemicu | Rumus | Arah buruk |
|---|---|---|
| Biaya toko per kg terjual | biaya toko mesin ÷ kg semua nota ber-kg | naik |
| HPP per kg · harga jual per kg · margin per kg | dari nota ber-HPP (kg & rupiahnya) | HPP naik · jual **turun** · margin **turun** |
| Harga beli per kg kedatangan · bongkar per kg | Σ rupiah ÷ Σ kg batch bulan itu (bongkar tertanam di HPP — disebut supaya kelihatan) | naik |
| Potongan QRIS dari uang QRIS | catatan bertanda MDR ÷ semua uang QRIS (penjualan arus kas mesin + bayar bon + kasbon kembali lewat QRIS; audit 39b no. 3) | naik |
| Biaya karyawan per hari kerja | (upah dibayar + belum dibayar + di luar upah) ÷ (hari rincian gaji + hari belum dibayar) | naik |
| Harga kantong per lembar | Σ harga ÷ Σ lembar pembelian kantong bulan itu | naik |
| Susut per kg terjual | susut & selisih ÷ kg terjual | naik |

Naik (atau turun, untuk jual & margin) di atas ambang pemicu → masuk "Yang perlu dilihat" dengan pintunya (Stok › HPP, Stok › Kantong, Harga, Uang).

## 5. Titik impas & peringatan

- Rasio margin = margin kotor ÷ **omzet ber-HPP** (nota tanpa modal tidak ikut dan disebut). Omzet impas = biaya di bawah margin ÷ rasio; per hari = ÷
  hari bulan; dibandingkan dengan omzet nyata per hari.
- "Sampai hari ini" = mesin laba rentang awal bulan → hari ini: sudah menutup (laba bersih ≥ 0) atau kurang berapa & omzet tambahan yang kira-kira
  dibutuhkan dalam hari tersisa. Bulan lampau = bulan penuh.
- Peringatan berurutan (awas dulu, info kemudian), tiap baris menunjuk layar: lampu merah/amber → Uang; pos tetap ada bulan lalu tapi belum bulan
  ini → Uang › Tagihan; upah belum dibayar → Uang › Upah; susut ≥ 20 % margin (tanpa toleransi) → Stok › Cocokkan; > 25 % biaya harian belum
  dipilah → Atur; cakupan HPP < 95 % → Jual (rinci karcis); pemicu naik → layarnya; belum impas → Laporan › Laba; TIDAK MENUTUP → jangan dipakai.
- Pareto: pos terbesar (dikelompokkan per kata kunci yang cocok / per pos gaji & tagihan / susut / hapus buku) yang membentuk 80 % biaya.
- Tren 6 bulan: margin (emas) vs biaya di bawahnya (platina; merah bila lebih besar); ketuk bulan = pindah.

## 6. Yang tidak dilakukan, dan kenapa

- Tidak mengubah 28 mesin beku, tidak menambah kolom pada catatan uang, tidak mengubah rules. Kendali biaya adalah lapisan baca + satu dokumen setelan.
- Tidak menebak jenis diam-diam: catatan yang tidak cocok kata tetap ada di Lain-lain dan dihitung; owner yang memutuskan lewat kata kunci.
- Tidak memakai rata-rata industri sebagai anggaran; acuan selalu **terukur** dari bulan-bulan toko sendiri, dan anggaran tetap keputusan owner.
- Sepuluh pertanyaan Menu tidak ditambah (terkunci owner); jalan masuknya Laporan › Biaya dan Menu › cari "biaya".

## 7. Uji

`alat-uji/uji_kendali_biaya.py` (+ `--kontrol`, CI): 45 skenario kotak pasir dengan angka contoh dan jam dikunci 19 Sep 2026; 23 kontrol positif
(logika yang dirusak wajib ketahuan); asap cadangan toko (lokal): tiap bulan menutup ke mesin laba, rasio impas = margin ÷ omzet ber-HPP,
pareto total = biaya; ASAP GLOBAL: laba/inti/neraca/omzet tiap bulan byte-sama dengan `main`.
