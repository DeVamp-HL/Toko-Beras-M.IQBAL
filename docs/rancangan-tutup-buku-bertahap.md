# Rancangan: Tutup buku BERTAHAP (K6) — siap sebelum Desember 2026

Dasar: main `7de3e7a` (worktree baca), cadangan toko `_privat/backup-batch-miqbal-2026-10-01.json` (diunduh 1 Okt 02.06 WIB), keputusan owner 1 Okt:
"atur saja dengan semestinya; lolosin dulu 18 nama yang berhutang" → batas **18 pemeriksaan kunci per kiriman TETAP**, saldo pembuka dipecah.
Semua hitungan memakai `jsc` atas bundel modul `/baru/` (kotak pasir). **Tidak ada peramban yang dinyalakan.** Mesin beku tidak disentuh (28/28 byte-identik).

---

## 0. Ringkas untuk owner

- **Masih nyata: YA.** Kalau tutup buku 2026 dijalankan dengan data toko 1 Okt (seolah 5 Jan 2027): saldo pembuka = **57 dokumen**, **24** di antaranya
  diperiksa kunci oleh server (**19 nama berutang** — tanggalnya ikut utang tertua, **4 bon pemasok** — ikut tanggal bon, **1 titik kas 31 Des**). 24 > 18 →
  hari ini layar menolak ("Saldo pembuka menyentuh 24 catatan…"). Kalau dijalankan 1–3 Jan, titik kas tidak diperiksa → 23, tetap > 18.
  "Batalkan tutup buku" juga butuh 24 → ditolak penjaga, jadi seandainya terkunci pun tidak bisa dibatalkan.
- **Rancangan:** saldo pembuka dikirim **2 kiriman (18 + 6)**; berita acara `berjalan` (berisi rencana lengkap) ikut kiriman pertama; **penanda** (titik kas
  31 Des · `pengaturan/tutupBuku` · berita acara `terkunci`) ikut kiriman TERAKHIR. Sampai penanda masuk, saldo pembuka yang sudah masuk **tidak terlihat**
  mesin & era → tahun 2026 utuh, tidak dobel, tidak FINAL. Terputus di tengah → **Lanjutkan** dari perangkat mana pun (id tetap, yang sudah masuk tidak dikirim
  ulang) atau **Batalkan** (juga per ≤ 18). Layar K6: "kiriman n dari N", "arsip m dari M".
- **Titik kas 31 Des:** hitungan tutup hari 31 Des disimpan di dokumen `tutupHari` (kolom `titik`) → walau tutup hari Januari sudah memajukan titik kas,
  uang per tempat 31 Des tetap bisa dihitung; titik Januari tidak ditimpa.
- **Rules TIDAK berubah. Mesin beku TIDAK berubah.** Asap laporan semua bulan (cadangan) **byte-sama** dengan main.
- **Ditemukan sekalian (cacat lama K6, ditambal di rancangan ini):** (1) arsip yang terputus tidak bisa dilanjutkan ("ulangi Kunci" ditolak karena layar sudah
  pindah ke 2027); (2) langkah 7 "cadangan sesudah & selesai" memakai tahun 2027 → "Kunci tahunnya dulu", berita acara 2026 tidak pernah selesai;
  (3) pemeriksaan ulang sesudah kunci berbunyi palsu bila ada penjualan 1 Jan.
- **TETAP menunggu owner (paling penting):** kalau **satu saja bulan 2026 dikunci** (mis. September, paling cepat 4 Okt), tutup buku 2026 **tetap tidak bisa**:
  23 saldo pembuka bertanggal lama dan 6.849 dari 6.850 hapus-arsip jatuh di bulan terkunci (kunci = awalan, 2022 ikut terkunci). Rancangan bertahap hanya
  menyelesaikan batas 18. Lihat §3(g).

---

## 1. Bukti di main sekarang (reproduksi)

Skrip bukti `rencana/tutup-buku/*.py` dijalankan di salinan kerja saat rancangan disusun (jsc, tanpa peramban; nama orang tidak dicetak) dan TIDAK ikut repo; penjaga tetapnya `alat-uji/uji_tutup_buku_bertahap.py` (+ `--kontrol`) di CI.

**1a. Data toko** — `python3 rencana/tutup-buku/ukur_cadangan.py` (kode main, cadangan 1 Okt):
```
jan5 {"nPembuka": 57, "perKoleksi": {"batchMasuk": 1, "produksiKemasan": 19, "stokBahanKemasan": 7, "stokBahanLiteran": 3, "piutangMutasi": 19,
      "kasbonMutasi": 2, "utangPemasokMutasi": 4, "amplopLaba": 1, "utangOwnerMutasi": 1}, "perluGet": 23, "getPerKoleksi": {"piutangMutasi": 19,
      "utangPemasokMutasi": 4}, "titikGet": 1, "total": 24, "nArsip": 6850, "potonganArsip": 381, "kasAda": true, "titikSekarang": "2026-09-26"}
jan2 { … "perluGet": 23, "titikGet": 0, "total": 23 … }
susunKunci → "Saldo pembuka menyentuh 24 catatan bertanggal lama … server hanya sanggup memeriksa 18 sekali kirim. Tidak ada yang dikirim."
```
Bulan pemeriksaan (pembuka piutang + bon): 2022-07 ×1, 2022-12 ×1, 2025-02 ×2, 2025-03 ×2, 2025-06 ×1, 2026-05 ×2, 2026-07 ×1, 2026-08 ×5, 2026-09 ×8.

**1b. Batalkan dengan data toko** — `python3 rencana/tutup-buku/ukur_batal_main.py`:
```
{"pembuka":57,"hapus":57,"pemeriksaan":24,"penjaga":"Kiriman ini menyentuh 24 catatan bulan lampau — server hanya sanggup memeriksa 18 sekali kirim. …"}
```

**1c. Kotak pasir (angka & nama CONTOH)** — `python3 rencana/tutup-buku/bukti_sekarang.py` (keluaran utuh: `bukti_sekarang.out.json`):
| | Keadaan | Hasil di main |
|---|---|---|
| S1 | 40 nama berutang | `susunKunci` menolak: "menyentuh 43 catatan" — tidak ada jalan selain latihan |
| S2 | 10 nama: kunci lalu arsip putus sesudah potongan 1 | layar pindah ke **2027**; "ulangi Kunci" → "Tahun 2027 belum lewat 31 Desember"; 9 catatan 2026 tertinggal (dobel) — **tidak bisa dilanjutkan** |
| S3 | 19 nama + 1 bon, sesudah terkunci | Batalkan butuh 21 pemeriksaan → penjaga pusat menolak |
| S4 | SATU dokumen pembuka saja masuk | `bkEra` null → **2026**, K6 pindah ke 2027, Agustus 2026 jadi **FINAL** (alasan pembuka tidak boleh ditulis sepotong-sepotong dengan kode sekarang) |
| S5 | ada penjualan 1 Jan (kotak: Rp700.000 tunai, angka contoh) | pemeriksaan ulang sesudah kunci: "Stok beras 17.166.300 vs 16.516.300", "Uang di laci 2.000.000 vs 2.700.000" → kabar "BATALKAN" **palsu** |
| S6 | sesudah kunci & arsip, langkah 7 | tahun dipakai = 2027 → `susunSelesai` "Kunci tahunnya dulu"; berita acara 2026 tetap `terkunci` selamanya |

**1d. Bulan terkunci** — `python3 rencana/tutup-buku/bukti_bulan_terkunci.py` (kode RANCANGAN, data toko, September 2026 terkunci):
```
{"tanpaKunci":[18,6], "septemberTerkunci_layar":"Tahun 2026 punya bulan terkunci (sampai 2026-09) — tutup buku sungguhan ditolak …",
 "septemberTerkunci_pembukaDitolakServer":23, "arsip":6850, "arsipHapusDiBulanTerkunci":6849}
```
Cadangan 1 Okt **tidak punya** `aturanToko/kunciPeriode` → belum ada bulan terkunci hari ini.

---

## 2. Sebab di kode (main 7de3e7a, dicek `grep -n`)

| Berkas:baris | Apa |
|---|---|
| `baru/js/layar/tutup-buku-logika.js:104,106` | pembuka piutang bertanggal `tanggalTertua`, bon pemasok `bonTanggal` lama → 1 pemeriksaan kunci per nama/bon (keputusan owner: umur jujur) |
| `baru/js/layar/tutup-buku-logika.js:150-151` | `butuhGet(dokumen)` > `KP_BATAS_GET` → tolak; semua dokumen satu kiriman, tidak ada pemecah |
| `baru/js/layar/tutup-buku-logika.js:22` (+ `sistem-logika.js:198`) | era = ada-tidaknya dokumen ber-`tutupBuku` → satu pembuka saja sudah memindah era (S4) |
| `baru/js/layar/tutup-buku-logika.js:35,39` | tahun layar = era + 1 → sesudah pembuka masuk, K6 menunjuk tahun berikutnya; berita acara tahun lama tak terjangkau (S2, S6) |
| `baru/js/layar/uang.js:220` | kalimat "ulangi Kunci; yang sudah pindah tidak diulang" — `bkKunci` memanggil `susunKunci(T.tahun=2027)` → ditolak (S2) |
| `baru/js/layar/uang.js:208` | langkah 7: `tahun = T.acara terkunci ? … : T.tahun` → 2027 (S6) |
| `baru/js/layar/tutup-buku-logika.js:159-165` | batal: semua tarik pembuka satu kiriman (S3); titik dikembalikan walau tutup hari sudah memajukannya |
| `baru/js/layar/tutup-buku-logika.js:131` + `uang.js:221` | `sesudahHidup` mengevaluasi 1 Jan dan dibandingkan dengan 31 Des → transaksi 1 Jan = "tidak sama" (S5) |
| `baru/js/layar/uang-logika.js:59` + `baru/js/mesin/beku.js:767` | kas tidak dihitung mundur dari titik; tutup hari Januari memajukan titik (`tutup-hari-logika.js:161`) → kas 31 Des "tidak bisa dihitung" (39b no. 12) |
| `baru/js/data/firebase.js:307` | tulis menunggu server 1,5 detik lalu "antre" — ritual berkiriman banyak butuh pengakuan server per kiriman |
| `baru/js/data/toko.js:262-271` | `tulisBertahap` yang ada: rencana hanya di localStorage perangkat, maju walau masih "antre", ada "buang sisanya" → tidak cocok untuk tutup buku (membuang sisa = tahun setengah tertutup) |

---

## 3. Rancangan

### (a) Pemecahan & urutan yang aman

`susunKunci(tahun, D, w)` tidak menolak lagi karena > 18; ia menyusun **kiriman** dengan `kpPotong` (pemecah yang sudah dipakai SATUKAN dll., aturan hitung
= penjaga pusat = rules):

| Kiriman | Isi | Pemeriksaan |
|---|---|---|
| 1 | berita acara `tutupBukuAcara/{tahun}` status **`berjalan`** (tak bertanggal: 0) berisi `rencana` (tiap kiriman: daftar `{koleksi,id}` + hitungan), `pembuka` (dokumen lengkap), `penanda`, `sebelum` (12 baris 31 Des), `titikTahun`, `hariIni` (12 baris hari mulai) **+** potongan pembuka pertama | ≤ 18 |
| 2 … N−1 | potongan pembuka berikutnya (urutan `pembukaBuku`; dokumen 0-pemeriksaan menumpang di mana saja) | ≤ 18 |
| N | potongan terakhir **+ PENANDA**: titik kas 31 Des (bila ditulis, §d) · `pengaturan/tutupBuku` · berita acara **`terkunci`** | ≤ 18 |

- Satu kiriman saja (≤ 18) = persis seperti dulu (tanpa `berjalan`).
- Data toko 1 Okt @5 Jan 2027: **2 kiriman, 18 + 6**; 61 dokumen (57 pembuka + berita acara berjalan + titik + era + berita acara terkunci) = 49 + 12. Kiriman 1 = 49
  dokumen + 49 jejak = ±98 tulisan (batas batch Firestore 500).
- **Penanda paling akhir** = titik balik tahun: era pindah, tahun baru terlihat, semua dalam SATU batch atomik.
- Tiap kiriman **menunggu pengakuan server** (`tulisDokumen(…, { tunggu: true })` → `firebase.js` tanpa batas 1,5 detik, 30 detik lalu berhenti) sebelum yang
  berikutnya. Sesudah penanda: arsip per 18 seperti sekarang (`arsipkanBerkas`), lalu pemeriksaan ulang.

### (b) Bisa dilanjutkan (idempoten)

- Rencana disimpan **di server** (berita acara `berjalan`), bukan di perangkat → lanjut dari HP/Mac mana pun. Id dokumen ditetapkan sekali saat mulai.
- `lanjutBuku(tahun)` membangun ulang kiriman dari berita acara (`bkKirimanDari`) dan mengirim yang **belum masuk** saja: kiriman dianggap masuk bila
  semua dokumen pembukanya ada (cache mentah, per id); kiriman yang hanya penanda = berita acara sudah `terkunci`. Batch Firestore atomik → tidak ada
  kiriman setengah. Yang sudah masuk **tidak pernah dikirim ulang** (mengirim ulang = ubah dokumen bertanggal lama = pemeriksaan tambahan).
- **Penjaga perubahan** (`bkBerubah`): sebelum melanjutkan, 12 baris 31 Des dihitung ulang (pembuka yang sudah masuk tidak terlihat, patokan kas sama) dan
  dibandingkan dengan `sebelum` di berita acara. Beda (mis. ada nota 20 Des yang baru tiba dari HP lain) → **tidak dilanjutkan**: "Catatan tahun 2026 berubah
  sejak tutup buku dimulai (…) — Batalkan, lalu mulai lagi."
- Mulai baru ditolak (`bkTertunda`) selama ada `berjalan` / `membatalkan`, atau masih ada saldo pembuka tahun itu dari percobaan sebelumnya.
- Arsip terputus: sisa dihitung ulang dari catatan tahun itu yang masih ada (`arsipBuku`) → dilanjutkan dengan tombol yang sama; id arsip `tahun|koleksi|id`
  (tulis ulang = isi sama).
- **Batal** juga bertahap (`susunBatal`): kiriman 1 = berita acara **`membatalkan`** (+ era & titik bila tahun sempat terkunci) + potongan tarik pertama →
  pembuka langsung tak terlihat; lalu tarik sisanya, kembalikan arsip, terakhir berita acara **`dibatalkan`**. Bisa dilanjutkan (yang sudah ditarik/dikembalikan
  tidak diulang). Titik kas dikembalikan **hanya** bila titik sekarang masih titik 31 Des tulisan tutup buku itu.

### (c) Kemajuan di layar K6

`kemajuanBuku()` → pita di atas K6 (kartu awas):
- **pembuka**: "Tutup buku 2026: 1 dari 2 kiriman saldo pembuka sudah masuk. Tahun 2026 MASIH TERBUKA (saldo pembuka yang sudah masuk belum dihitung) sampai
  kiriman terakhir masuk — lanjutkan atau batalkan." + batang kemajuan.
- **arsip**: "Tahun 2026 terkunci; N catatan 2026 belum pindah ke arsip (k kiriman lagi). Sampai habis, stok, piutang & utang terhitung DOBEL — lanjutkan arsip
  atau batalkan." + "m / M dokumen dipindah ke arsip".
- **selesaikan**: arsip habis → tombol "unduh cadangan sesudah · selesai" langsung (langkah 7 memakai tahun yang TERKUNCI, tidak bergantung langkah lokal /
  mode latihan perangkat itu).
- **batal**: "Pembatalan tutup buku 2026 belum selesai: n saldo pembuka belum ditarik …" + lanjutkan.
- Tombol: `lanjutkan` (`bkLanjut`), `batalkan` (dua ketukan). Batang progres menyebut satuannya (kiriman / dokumen).
- Kabar bila berhenti: "Berhenti di kiriman 2 dari 2 — <sebab>. Tahun 2026 BELUM tertutup (yang sudah masuk belum dihitung). Ketuk "Lanjutkan" — yang sudah masuk
  tidak dikirim ulang — atau "Batalkan"."
- (Pilihan, belum dibangun: satu baris di Beranda › Perlu perhatian dari `kemajuanBuku()`.)

### (d) Titik kas 31 Des = hitungan tutup hari 31 Des

- Tutup hari menulis kolom baru **`titik`** di dokumen `tutupHari` = isi tempat uang SESUDAH tutup malam itu (persis `pengaturan/titikKas` yang ditulis bersama).
  Bertanggal hari itu → tanpa pemeriksaan kunci.
- `titikTahun(tahun)`: titik kas sekarang bila tanggalnya ≤ 31 Des; kalau tutup hari Januari sudah memajukannya → `titik` dokumen tutupHari terakhir ≤ 31 Des
  (biasanya 31 Des; toko libur 31 Des → 30 Des + gerakan 31 Des). `saldoKantong(sampai, titikPakai)` dan `barisTahun(tahun)` memakainya; layar K6 juga.
- Ditulis saat penanda: titik kas **31 Des** hanya bila patokan sekarang belum melewati 31 Des (seperti dulu). Kalau titik sudah di Januari, **tidak ditulis** —
  hitungan fisik Januari lebih baru dan tidak tersentuh arsip (arsip hanya catatan ≤ 31 Des).
- Pemeriksaan ulang (`periksaUlangBuku`, ganti `sesudahHidup`): 12 baris pada **hari tutup buku dimulai** (disimpan di berita acara) dibanding sesudah kunci &
  arsip. Kas selalu terhitung (titik ≤ hari ini), transaksi 1 Jan tidak membuat beda palsu. Bila dilanjutkan hari lain dan titik kas sudah maju, baris kas bisa
  "?" — kalimatnya menyebut barisnya, tidak lagi "BATALKAN".
- Celah yang diakui: dokumen tutupHari sebelum rancangan ini tidak punya `titik`; isi rekening yang dicatat ulang (`susunTitikRekening`) SESUDAH tutup hari 31 Des
  tidak ikut `titik` 31 Des. Rancangan harus terbit sebelum 31 Des 2026.

### (e) Tahun lama sampai semua kiriman selesai — tidak ada "setengah"

`data/toko.js pembukaBerlaku` (satu tempat): saldo pembuka tahun yang berita acaranya `berjalan` / `membatalkan` / `dibatalkan` **disaring** dari 9 `ambil*`
koleksi pembuka (batch, produksi, bahan kemasan/literan, piutang, kasbon, amplop, utang owner, utang pemasok) dan dari era (`bkEra`, `ssEraTutupBuku`,
`bkEraTanpa`). Pembuka sistem lama (tanpa berita acara) dan yang `terkunci`/`selesai` tetap terlihat. Tanpa berita acara seperti itu, `ambil*` mengembalikan
larik yang SAMA (asap global byte-sama dengan main).

| Keadaan | Berita acara | Era | Yang dihitung mesin | Layar |
|---|---|---|---|---|
| Terbuka | — / `dibatalkan` bersih | lama | tahun lama | K6 tahun 2026 |
| **Berjalan** (kiriman n/N) | `berjalan` | **lama** | **tahun lama saja** (pembuka tersembunyi) — tidak dobel, tidak FINAL | pita "MASIH TERBUKA", lanjut/batal |
| Terkunci, arsip m/M | `terkunci` | 2026 | pembuka + sisa catatan 2026 → **DOBEL** (perilaku lama, sekarang tertulis jelas) | pita "DOBEL", lanjut arsip / batal |
| Selesaikan | `terkunci`, arsip habis | 2026 | tahun baru saja | pita selesaikan |
| Selesai | `selesai` | 2026 | tahun baru | — |
| Membatalkan | `membatalkan` | lama | catatan 2026 yang sudah kembali (pembuka tersembunyi) → KURANG sampai arsip kembali | pita batal, lanjut |

Dua tahun tidak pernah sama-sama "setengah": sampai penanda, 2027 belum lahir (pembuka tak terlihat); sejak penanda, 2026 tertutup sekaligus. Satu-satunya
jendela yang tersisa = arsip (dobel) — sudah ada sejak putaran 18, sekarang bisa dilanjutkan dan disebut di layar. Menutupnya juga = §(g) pilihan C.

Sistem lama (`index.html`, hanya-baca) dan cadangan yang diunduh DI TENGAH tutup buku tidak kenal berita acara → melihat pembuka setengah (dobel). Jangan
memulihkan cadangan yang diambil saat pita tutup buku masih tampil.

### (f) Uji

**Baru:** `alat-uji/uji_tutup_buku_bertahap.py` (+ `--kontrol`, masuk CI `pages.yml`) — kotak pasir jsc, jam 5 Jan 2027:
- T0 5 nama → 1 kiriman (seperti dulu). T1 **40 nama → 3 kiriman (18 + 18 + 7)**, tiap kiriman lolos penjaga pusat, berita acara berjalan di kiriman 1,
  penanda hanya di kiriman 3, tiap pembuka tepat sekali.
- T2 sesudah kiriman 1: era null, `ssEraTutupBuku` null, K6 tetap 2026, Agustus tidak FINAL, 12 baris 31 Des & piutang tidak berubah, kemajuan 1/3,
  mulai baru ditolak.
- T3 **putus di kiriman 2 → lanjut**: tinggal kiriman 2 & 3 (id & isi sama), lalu tinggal 3; sesudahnya terkunci, era 2026, pembuka tidak dobel.
- T4 arsip putus sesudah 18 → kemajuan 18/57 → lanjut habis → periksa ulang sama → langkah 7 memakai 2026 → selesai, tidak ada yang tertunda.
- T5 batal dari berjalan (+ pembatalan putus di tengah → mulai baru ditolak → dilanjutkan) → bersih, mulai lagi bisa.
- T6 batal dari terkunci 19 nama + bon → dipecah, tiap ≤ 18, data kembali utuh.
- T7 titik kas 2 Jan → patokan dari tutupHari 31 Des, titik 2 Jan tidak ditimpa; `susunTutup` 31 Des menulis kolom `titik` = titik kas.
- T8 penjualan 1 Jan → periksa ulang tidak berbunyi palsu. T9 nota 20 Des masuk di tengah → lanjut ditolak.
- 4 pemeriksaan statis `uang.js` (tunggu pengakuan server, pita lanjut/batal/selesaikan, langkah 7 tahun terkunci, patokan kas tahun di layar).
- Asap data toko (lokal, `_privat/`): `{"kiriman": [18, 6], "pembuka": 57, "arsip": 6850, "batal": [18, 6], "salah": []}`.
- **Kontrol (17, semua BERBUNYI):** pembuka tidak dipecah · saringan data mati · era menghitung pembuka berjalan · rencana tidak ikut kiriman 1 · lanjut
  mengirim ulang · lanjut tanpa penjaga perubahan · mulai baru saat pembatalan belum tuntas · batal tidak dipecah · titik tahun hanya dari titik kas · titik 2 Jan
  ditimpa · tutup hari tanpa kolom titik · periksa ulang kembali ke 1 Jan · kemajuan menyebut tahun berjalan · 4 jangkar statis uang.js dibuang.

**Hasil:**
```
uji baru atas MAIN (python3 rencana/tutup-buku/uji_baru_di_main.py):      MAIN: TUTUP BUKU BERTAHAP 0 lulus · 14 gagal
uji baru atas RANCANGAN (cd rencana/tutup-buku/kerja; python3 alat-uji/uji_tutup_buku_bertahap.py): 34 lulus · 0 gagal ; --kontrol 17 BERBUNYI, keluar 0
```
**Disesuaikan:** `uji_uang_baru.py` (periksa ulang = `periksaUlangBuku`; batal = `membatalkan` → `akhir` `dibatalkan`; 2 jangkar kontrol) 151/0, kontrol 0 ·
`uji_kunci_periode.py` (asap: tidak ditolak lagi → 2 kiriman `[18, 6]` diukur PADA 5 Jan; dulu `butuhGet` dihitung sesudah jam dikembalikan ke 24 Sep) 45/0 ·
`peta_akses.py --kiriman` (`r.kiriman` diukur per kiriman; 25 nama → "18 / 20 · 2 tahap"; kontrol "tidak dipecah") LULUS, kontrol 0.
**Tetap hijau di salinan rancangan (jsc saja):** jual 355, ringkasan 46, stok 149, pelanggan 71, menu 64, harga 106, laporan 84, pajak 43, akses 33, isian lokal,
batal karcis 19, bayar bon terkunci 33, jam tampil 8, jenis beras 23, operator 27, cocokkan 23, varian 27, arsip produk 19, setengah 18, wadah bernama 28,
wadah stok sendiri 55, buku ukuran 30, uang karyawan 28, upah 20, bayar pemasok 29, kelas merek 56, pemantapan 31 18, tandai cocok 20, riwayat 20, kendali biaya 48,
wadah satu buku 134, kinerja gerak 74, tata letak 37/17/9, periksa impor/komentar/penangan ganda/rules/onclick, `beku2.py --sidik` 28/28 byte-identik,
`uji_identitas_baru` identik — semua dengan `--kontrol` keluar 0. ASAP GLOBAL tanpa git (`python3 rencana/tutup-buku/asap_global_vs_main.py`):
**BYTE-SAMA** — 3 bulan (2026-08 … 2026-10), laba/inti/neraca/omzet. Uji yang menyalakan Chrome TIDAK dijalankan (aturan CLAUDE.md) — CI runner.

### (g) Yang perlu owner

1. **Rules: TIDAK perlu diterbitkan** untuk rancangan ini (berita acara & `pengaturan/tutupBuku` sudah owner-only; tiap kiriman ≤ 18 = batas yang sama).
2. **KEPUTUSAN SEBELUM KUNCI BULAN PERTAMA** (paling cepat 4 Okt untuk September): kunci berbentuk awalan — mengunci September 2026 ikut mengunci semua bulan
   sebelumnya, termasuk 2022 & 2025. Akibatnya saldo pembuka bertanggal lama (23 dari data toko) dan hapus-arsip (6.849 dari 6.850) **pasti ditolak server**,
   dan K6 menolak tutup buku selama tahun itu punya bulan terkunci (K1). Pilihan:
   - **A.** Jangan kunci bulan 2026 sampai tutup buku 2026 selesai (kunci bulanan mulai Januari 2027). Tanpa kode. Bulan 2026 tidak terlindung kunci.
   - **B.** Kunci jalan, lalu dibuka sebelum tutup buku: kunci hanya turun SATU bulan per langkah (alasan ≥ 10 huruf); untuk pembuka bertanggal Juli 2022 harus
     turun sampai Juni 2022 (±51 langkah). Praktis tidak bisa.
   - **C.** Pembuka piutang & bon pemasok bertanggal 1 Januari (tanggal utang asli pindah ke kolom yang tidak dibaca mesin; layar umur membacanya) **dan** arsip
     tidak menghapus: catatan tahun lama disaring di lapisan data begitu penanda masuk (perluasan `pembukaBerlaku` ke semua koleksi bertanggal) — tidak ada
     tulisan ke bulan terkunci, 0 pemeriksaan, tidak ada jendela dobel, sesuai K1 "salinan + penanda, simpan 10 tahun". Biaya: umur bon/piutang menurut mesin
     mulai 1 Jan (owner menolak ini 25 Sep), dan catatan lama tetap dimuat tiap buka aplikasi (kuota baca naik; ±3.600 dokumen/bulan menurut cadangan) kecuali
     pendengar dibatasi tanggal.
   - **D.** Rules v6 (owner terbitkan lewat Console): pengecualian sempit — create saldo pembuka (`tipe` saldoAwal, `tutupBuku` true, `tahunDari` = tahun lalu)
     boleh di bulan terkunci; hapus-arsip di bulan terkunci hanya bila salinan arsipnya ditulis di kiriman yang sama (`getAfter`, 2 pemeriksaan/dokumen → 9 per
     kiriman → ±760 kiriman untuk 6.850 dokumen, ±2.000 untuk setahun penuh). Playground ★ wajib.
   - Saran Claude: **A** untuk 2026 (paling sedikit yang bisa salah, tenggat Desember), C dirancang di putaran sendiri untuk 2027.
3. **Kuota tulis (perkiraan, belum diukur di server):** arsip setahun = ±17.700 dokumen bila laju ±3.600/bulan (Sep 2026) berlanjut sampai Desember → ±985
   kiriman → ±18.700 tulis + ±17.700 hapus. Batas Spark menurut dokumentasi Firebase 20 rb tulis & 20 rb hapus per hari (direset ±14.00 WIB) → arsip bisa
   berhenti di tengah karena kuota. Rancangan ini bisa melanjutkannya besok, tapi angka DOBEL semalaman. Pilih hari & jam (sesudah reset, toko tutup), atau
   naikkan ke Blaze sehari. "Batalkan" sesudah arsip penuh = ±17.700 baca + tulis lagi.
4. **Kapan:** 1 Jan sesudah tutup hari 31 Des, sebelum toko buka (gerbang: perangkat lain mati, antrean 0, internet). Kalau toko sudah berjualan di Januari,
   tetap bisa (patokan kas dari tutup hari 31 Des; pemeriksaan ulang pada hari mulai).
5. **Latihan:** mode LATIHAN K6 (tidak menulis) + uji kotak pasir CI sudah mencakup logikanya. Proyek Firebase uji untuk gladi sungguhan = belum ada jalurnya
   (aplikasi satu konfigurasi); tidak wajib. Sesudah terbit: owner menjalankan LATIHAN sekali di Desember (daftar periksa & 12 baris).
6. **Tugas data:** tidak ada sekarang. Sesudah terbit, cadangan sesudah tiap tutup hari Desember tetap wajib (dua cadangan K6).

---

## 4. Perbaikan — berkas & diff

Diff persis: **`rencana/tutup-buku/rancangan.diff`** (14 berkas, +487 −77; `git apply --check` bersih atas main 7de3e7a). Salinan yang sudah diterapkan &
diuji: `rencana/tutup-buku/kerja/`.

| Berkas | Perubahan |
|---|---|
| `baru/js/layar/tutup-buku-logika.js` | `susunKunci` → kiriman (`kpPotong`), berita acara berjalan/penanda, `hariIni`, `titikTahun`; `bkKirimanDari`, `bkMasuk`, `bkBerubah`, `lanjutBuku`, `bkPembukaTahun`, `bkTertunda`, `kemajuanBuku`; `susunBatal` bertahap (`membatalkan` → `akhir` `dibatalkan`, titik dikembalikan hanya bila masih 31 Des); `titikTahun`, `barisTahun`, `barisBuku(…, titikPakai)`; `periksaUlangBuku` ganti `sesudahHidup`; era & `bkEraTanpa` lewat `pembukaBerlaku` |
| `baru/js/data/toko.js` | `pembukaBerlaku` + saringan di 9 `ambil*` koleksi pembuka (aktif hanya bila ada berita acara berjalan/membatalkan/dibatalkan) |
| `baru/js/layar/sistem-logika.js` | `ssEraTutupBuku` lewat `pembukaBerlaku` |
| `baru/js/layar/uang-logika.js` | `saldoKantong(sampai, titikPakai)` |
| `baru/js/layar/tutup-hari-logika.js` | `dokTutup.titik` (salinan titik malam itu) |
| `baru/js/data/firebase.js` | `tulisBerkas` opsi `tunggu` (pengakuan server, 30 detik) |
| `baru/js/layar/uang.js` | `jalankanBuku` / `jalankanBatal` (kiriman berurutan, berhenti dengan kalimat), `bkLanjut`, `bkBatal` dua ketukan & bertahap, langkah 7 tahun terkunci, pita kemajuan, `barisTahun` di layar, satuan batang progres |
| `alat-uji/uji_tutup_buku_bertahap.py` (baru), `uji_uang_baru.py`, `uji_kunci_periode.py`, `peta_akses.py`, `.github/workflows/pages.yml` | §(f) |
| `baru/BACA-DULU.md`, `docs/peta-kunci-periode.md` | catatan rancangan & status K1 (jumlah saja, tanpa nama) |

`beku.js` & `pembantu.js` **tidak diubah** (`beku2.py --sidik` 28/28). `kasir*.html` tidak disentuh (sw-kasir VERSI tidak perlu naik). Rules tidak berubah.

---

## 5. Risiko

- **Saringan data menyentuh 9 `ambil*` yang dibaca mesin.** Diam (larik sama) tanpa berita acara berjalan/membatalkan/dibatalkan — asap global byte-sama &
  semua uji jsc hijau. Bila ada, pembuka tahun itu tak terlihat di SEMUA layar (disengaja). Berita acara `dibatalkan` lama tetap menyembunyikan pembuka tahun itu
  (seharusnya sudah tidak ada; kalau ada, K6 menawarkan lanjutkan pembatalan).
- **Jendela DOBEL arsip** tetap ada (perilaku lama) dan bisa lebih panjang karena kuota (§g.3); sekarang tertulis di layar & bisa dilanjutkan.
- Berita acara `berjalan` membawa salinan dokumen pembuka (±29 KB dengan data toko; yang `terkunci` ±6 KB; nama pelanggan berutang ikut — koleksi owner-only, sama dengan dokumen piutangnya).
- `tunggu` 30 detik: kiriman yang terlambat diakui tetap di antrean perangkat; "Lanjutkan" melihatnya dari id bila sudah masuk. Kiriman yang DITOLAK server masuk
  daftar "ditolak" seperti kiriman lain.
- Sistem lama / cadangan di tengah tutup buku melihat pembuka setengah (§e). Kolom `titik` hanya ada di tutup hari sesudah terbit (§d).
- Bagian layar (`uang.js`) hanya diperiksa sintaks (jsc `checkModuleSyntax`) & statis; perilaku tombol perlu dicoba di peramban — **di runner CI / oleh owner**,
  bukan di Mac owner dengan Chrome headless berulang.
- Tidak menyelesaikan K1 (§g.2) — tanpa keputusan owner, tutup buku 2026 tetap ditolak begitu satu bulan 2026 dikunci.

## 7. Keputusan owner sesudah rancangan ini ditulis

- **1 Okt 2026 — K1 (§3g.2): pilihan A.** Bulan 2026 tidak dikunci sampai tutup buku 2026 selesai (`KP_KUNCI_MULAI = '2027-01'`, PR #87).
  Pilihan C (pembuka 1 Jan + arsip tanpa hapus) dirancang di putaran sendiri untuk 2027.

## 8. Status 1 Okt 2026 — kode BELUM terbit; hasil tinjauan independen = syarat wajib sebelum terbit

Kode rancangan ini ada di cabang `audit/tutup-buku-bertahap` (f0992a1, di atas main 7de3e7a; uji `uji_tutup_buku_bertahap.py` 34 lulus,
asap laporan byte-sama). Tinjauan independen (2 peninjau + penyanggah, jsc, tanpa peramban) menemukan cacat yang LAHIR di cabang itu — tidak
digabung ke main sampai semuanya dibereskan (tenggat: sebelum Desember 2026). Satu putaran tersendiri, lalu tinjau ulang:

1. **HP staf melihat angka DOBEL selama `berjalan` / `membatalkan`.** Saringan `pembukaBerlaku` bergantung pada `tutupBukuAcara`, koleksi khusus
   owner (rules) yang tidak didengar HP staf → stok & piutang di HP staf terhitung dua kali sampai penanda masuk. Arah perbaikan: sumber status
   yang bisa dibaca staf (mis. pembuka disembunyikan selama dokumen penanda tahun itu belum ada di koleksi yang staf baca), atau minimal
   gerbang "perangkat lain mati" (g3) juga di Lanjutkan + kalimat di pita.
2. **Lanjutkan menimpa titik kas Januari** dengan titik 31 Des yang disusun saat mulai. Aturan §(d) harus dinilai saat KIRIM: titik kas sekarang
   sudah lewat 31 Des → `pengaturan/titikKas` dibuang dari kiriman penanda, `titikDitulis = false`.
3. **Kiriman dihitung dengan jam MULAI** — mulai 1–3 Jan (masa tenggang), lanjut sesudah tanggal 3 → kiriman tersimpan melebihi 18 pemeriksaan,
   Lanjutkan ditolak selamanya. Lanjutkan memecah ulang kiriman yang belum masuk dengan jam sekarang (id tetap, penanda tetap terakhir).
4. **Kiriman yang belum diakui server** (tunggu 30 detik habis, masih antre) sudah dihitung "masuk" oleh pita & Lanjutkan → Lanjutkan menolak
   selama antrean perangkat belum kosong, atau `bkMasuk` tidak menghitung dokumen yang masih menunggu server.
5. **Periksa ulang berbunyi palsu** bila dilanjutkan di hari mulai sesudah toko berjualan — patokan diambil tepat sebelum kiriman pertama sesi itu.
6. **"Selesaikan" bisa menutup tahun** walau periksa ulang belum jalan / hasilnya beda — pita fase selesaikan menjalankan periksa ulang dan
   menolak (atau minta ketukan kedua menyebut barisnya) bila tidak sama.
7. **Kalimat salah tombol:** pembatalan yang berhenti di kiriman pertama menyuruh "Lanjutkan" (yang justru meneruskan TUTUP BUKU) → kalimat
   menyuruh "Batalkan" lagi; tutup buku yang berhenti di kiriman pertama menyuruh "Kunci" lagi.
8. **Berita acara pembatalan kedua** mencatat tanggal pembatalan pertama → `dibatalkanPada/Tanggal` dibuang saat mulai baru.
9. (sesudah gabung main #87) butir ⛔ di daftar periksa Kunci bulan bila tutup buku belum tuntas (`kemajuanBuku()` tidak null), menutup varian
   kunci bulan 2027 di tengah tutup buku.

Tidak wajib (penyanggah: urutan rakitan tangan, jendela ±1 detik): batal dari HP lain yang cache-nya masih `berjalan` mendarat sesudah penanda —
`jalankanBuku` membaca ulang status sebelum arsip, `susunBatal` menolak bila cache sudah `selesai`.

## 9. Syarat §8 no. 1–9 dibereskan (1 Okt 2026, cabang `audit/tutup-buku-bertahap`, satu commit per butir)

Tiap butir: uji baru di `alat-uji/uji_tutup_buku_bertahap.py` (N1–N9) yang GAGAL di kode sebelum butir itu dan LULUS sesudahnya + kontrol yang berbunyi.
Rules TIDAK berubah, mesin beku TIDAK berubah, `kasir*.html` tidak disentuh. Semua lewat jsc; tidak ada peramban yang dinyalakan.

| No. | Perbaikan | Uji |
|---|---|---|
| 1 | Tanpa mengubah rules: semua pembuka tutup buku bertahap ber-`bertahap: true` dan baru terlihat bila PENANDA tahunnya ada = batch pembuka ber-`penandaBuku` (koleksi `batchMasuk`, dibaca staf menurut `akses.js BACA_STAF` & rules). Batch penanda ikut kiriman TERAKHIR; dihapus di kiriman PERTAMA pembatalan. Tanpa stok beras → batch kosong khusus penanda. Satu aturan (`toko.js pembukaBerlaku`) di semua perangkat. | N1: 12 titik putus (kiriman pembuka, arsip, batal dari terkunci & dari berjalan) — HP staf = HP owner |
| 2 | Aturan titik kas (d) dinilai saat KIRIM (`bkTitikKini`): titik kas sekarang lewat 31 Des → `pengaturan/titikKas` dibuang dari kiriman penanda, `titikDitulis` false | N2 |
| 3 | `lanjutBuku` mengambil dokumen yang BELUM ada (id & isi dari berita acara) dan memecah ulang dengan `kpPotong` pada jam sekarang; penanda tetap kelompok terakhir | N3 (mulai 2 Jan, lanjut 5 Jan) |
| 4 | `firebase.js` menyetor id dokumen yang menunggu server (hasPendingWrites) ke `toko.js` (`setelTertunda`/`dokTertunda`). Selama catatan tutup buku tahun itu masih menunggu: kemajuan = fase `tunggu`, Lanjutkan & Batalkan menolak | N4 (+ 2 statis) |
| 5 | `lanjutBuku` menghitung ulang patokan periksa ulang (12 baris hari ini) tepat sebelum kiriman pertama sesi itu → berita acara terkunci | N5 |
| 6 | `susunSelesai`: arsip harus habis; periksa ulang dijalankan — beda / tidak bisa diperiksa = ditolak menyebut barisnya, diterima pada ketukan kedua dan dicatat (`periksaUlang`). Pita fase selesaikan menyebut hasilnya; layar memeriksa sebelum berkas diunduh | N6 (+ 1 statis) |
| 7 | `kabarBerhentiBuku` (satu tempat): kiriman 1 tutup buku → "Kunci tahun" lagi; kiriman 1 pembatalan → "Batalkan" lagi; sesudahnya "Lanjutkan"; antre → tunggu antrean dulu | N7 (+ 1 statis) |
| 8 | `susunKunci` membuang `dibatalkanPada/Tanggal` dari berita acara yang dipakai ulang | N8 |
| 9 | Butir ⛔ `tutupBukuTuntas` di `kpDaftarPeriksa` (ok hanya bila `kemajuanBuku()` null) | N9 |

Hasil: `uji_tutup_buku_bertahap` 60 lulus · 0 gagal, `--kontrol` 36 berbunyi; asap data toko tetap `[18, 6]` / batal `[18, 6]`; `uji_uang_baru` 151/0
(asersi selesai tidak jatuh lagi bila ditolak), `uji_kunci_periode` 47/0, `peta_akses --kiriman --kontrol` 33 berbunyi (jangkar disesuaikan),
ASAP GLOBAL `uji_wadah_bernama` BYTE-SAMA dengan main (juga dibanding origin/main sesudah #90), seluruh perintah job `uji` di `pages.yml` keluar 0.
Uji peramban (`uji-peramban`) TIDAK dijalankan di Mac owner — CI runner.

Yang tetap diakui:
- Selama ARSIP tahun berikutnya berjalan (jendela DOBEL yang sudah ada), batch penanda tahun lama ikut diarsipkan lebih dulu daripada sebagian pembuka
  tahun lama → pembuka itu tak terlihat sampai ikut diarsipkan. Sama di semua perangkat; periksa ulang baru jalan sesudah arsip habis.
- Periksa ulang masih bisa berbunyi palsu bila toko berjualan di antara penanda dan LANJUT ARSIP pada hari yang sama (patokan hanya disegarkan saat
  kiriman pembuka dilanjutkan). Kalau itu terjadi, "selesai" meminta ketukan kedua yang menyebut barisnya (no. 6).
- Fase `tunggu` dihitung dari antrean perangkat ITU; perangkat lain tidak melihat tulisan yang tertunda (memang belum ada di server).

## 10. Putaran 3 (1 Okt 2026, tinjauan + sanggah sesudah §9): 9 cacat dibereskan

Tinjauan ulang atas §9 (jsc, tanpa peramban) menemukan 9 cacat yang tersisa / lahir dari §8. Satu commit per butir; tiap butir punya uji `P3-…` di
`alat-uji/uji_tutup_buku_bertahap.py` yang GAGAL di kode sebelum butir itu dan LULUS sesudahnya, + kontrol yang berbunyi. Rules, mesin beku, `kasir*.html`
tidak disentuh.

| Butir | Perbaikan | Uji |
|---|---|---|
| AAL1 | Arsip yang berjalan membaca ulang status berita acara sebelum & di antara potongan (`arsipBerhentiBuku`) — dibatalkan dari perangkat lain = berhenti. Tombol pita `.seg.mati` sungguh mati (CSS) dan Lanjutkan/Batalkan tidak jalan selagi sibuk. Susulan: potongan yang sudah terkirim sebelum pembatalan terlihat dikembalikan perangkat pengarsip (`arsipBalikBuku`, hanya bila dibatalkan — `selesai` tidak pernah), dan pembatalan membaca arsip ulang sekali sebelum berita acara `dibatalkan` | P3-AAL1, P3-AAL1b + 5 statis |
| UTBU-1 | Hasil periksa ulang DIBEKUKAN saat arsip habis (`susunPeriksaArsip` → berita acara `periksaArsip`: patokan & angka mesin per baris). "Selesai" & pita memakainya; belum ada = dihitung ulang seperti dulu | P3-UTBU1 |
| UTBU-2 | TIDAK SAMA hanya bila kedua sisi terhitung dan berbeda; sisi yang tidak bisa dihitung (titik kas sudah maju) = "belum bisa dihitung" — pita, "selesai", kabar sesudah arsip, berita acara (`periksaUlang.belumBisa`) | P3-UTBU2 |
| AAL2 | `arsipBuku` menaruh batch penanda tahun lalu PALING AKHIR → arsip tahun berikutnya yang putus lalu dilanjutkan tidak meninggalkan pembuka tahun lalu di koleksi hidup | P3-AAL2 |
| AAL3 | `terkunci` (tahun era sekarang) dengan saldo pembuka kurang dari `nPembuka` = fase `rusak` → "batalkan", Lanjutkan menolak (penanda yang tertahan di perangkat lain mendarat sesudah pembatalan; kiriman yang belakangan ditolak server) | P3-AAL3 |
| AAL4 | Lanjutkan & Batalkan hanya dari data server: tanpa internet, atau berita acara / pengaturan masih salinan perangkat (Firestore `fromCache` → `toko.js koleksiDariCache`) = ditolak | P3-AAL4 + 2 statis |
| AAL5 | Hapus yang menunggu server dicatat per kiriman (`firebase.js tulisBerkas` → `toko.js setelHapusTertunda`) → fase `tunggu`. Bukan tanda tingkat snapshot (saran tinjauan): dokumen yang dihapus sudah keluar dari hasil query, jadi kiriman yang isinya hapus saja tidak terlihat di sana | P3-AAL5 + statis |
| AAL6 | Tutup buku SATU kiriman yang antre: kalimat menyebut pita "Tahun … terkunci" → "Lanjutkan" (arsip) | P3-AAL6 |
| AAL7 | Satu satuan: pita = saldo pembuka yang sudah masuk (dokumen); Lanjutkan = "kiriman lanjutan i dari n" + jumlah itu | P3-AAL7; T2/T3/N3/N4 disesuaikan |

Hasil: `uji_tutup_buku_bertahap` 84 lulus · 0 gagal, `--kontrol` 60 berbunyi; asap data toko tetap `[18, 6]` / batal `[18, 6]`; `uji_uang_baru` 151/0,
`uji_kunci_periode` 47/0, `uji_denyut_per_akun` 17/0 (menangkap bentrok nama `_dariCache` toko.js vs firebase.js di bundel jsc → AAL4 susulan),
`peta_akses --kiriman --kontrol` 33 berbunyi; ASAP GLOBAL `uji_wadah_bernama` BYTE-SAMA dengan main dan dengan origin/main (tanpa perubahan disengaja);
`uji_csp` (baru ada di origin/main #91) lulus pada gabungan sementara cabang + origin/main (konflik hanya di `baru/BACA-DULU.md`); seluruh perintah job
`uji` di `pages.yml` keluar 0. Skrip repro tinjauan dijalankan ulang (lama 1548361 vs baru): yang memanggil lapisan logika berbalik benar; yang melewati
penjaga layar (memanggil arsip / pembatalan langsung) diulang dengan varian yang meniru `uang.js` dan berbalik benar. Uji peramban TIDAK dijalankan di Mac
owner — CI runner.

Yang tetap diakui (menggantikan daftar §9):
- Jendela §9 "batch penanda tahun lama diarsipkan lebih dulu" DITUTUP (AAL2).
- Periksa ulang dibekukan saat arsip habis: jualan di antara penanda dan arsip habis pada HARI yang sama masih membuat hasil beku "TIDAK SAMA" (ketukan
  kedua menyebut barisnya). Perubahan sesudah arsip habis tidak diperiksa lagi (disengaja). Tulisan hasil beku gagal → "selesai" menghitung ulang.
- Arsip dan pembatalan dari dua perangkat sekaligus: dua lapis penjaga (pengarsip mengembalikan potongan terakhirnya; pembatalan membaca arsip ulang).
  Yang tersisa hanya potongan dari tab yang beku lama dan mendarat sesudah keduanya.
- Batalkan dari perangkat yang data servernya baru tiba ±detik sebelum penanda perangkat lain masuk: arsip tidak jalan (AAL1), pita "batal" menuntun
  menarik sisa pembuka, tetapi `pengaturan/tutupBuku` (hanya dibaca sistem lama) & titik 31 Des dari penanda tidak dikembalikan. Tetap "tidak wajib"
  seperti §8.
- Fase `tunggu` untuk hapus hanya selama sesi itu (dimuat ulang = catatannya hilang; Firestore tetap mengirim antreannya berurutan).
