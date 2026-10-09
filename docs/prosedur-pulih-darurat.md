# Prosedur pulih darurat — memulihkan data dari berkas cadangan (sesudah sistem lama pensiun, 3 Okt 2026)

**Kapan dipakai:** data di server hilang atau rusak, dan harus dikembalikan dari berkas cadangan (`backup-batch-miqbal-….json`). Ini jalan
**darurat**, bukan pekerjaan rutin.

> **3 Okt 2026 — sistem lama & `kasir.html` pensiun** (owner: "bumi hanguskan"). `index.html` dan `kasir.html` di situs kini hanya halaman pengalih
> ke `/baru/`. Satu-satunya pemulih dari berkas (`muatDariFile`, Setelan › Muat cadangan, mode PULIHKAN) ada di sistem lama — jadi sistem lama
> **dijalankan di komputer dari tag git**, tidak lagi dibuka dari situs. Versi terakhirnya utuh di tag **`sistem-lama-terakhir`** (commit `48a694d`).
> Sebelum 3 Okt prosedur ini membuka sistem lama dari situs dan memakai rules v4; sekarang rules yang terpasang = `firestore.rules` (v7, terbit 7 Okt
> 2026 18.25 WIB).

> **9 Okt 2026 — Firebase pindah ke paket Blaze (bayar sesuai pakai).** Keputusan owner 9 Okt, berlaku untuk semua bab di bawah:
> - **Kuota harian bukan lagi batas.** Jatah gratis harian tetap sama (50 rb baca, 20 rb tulis, 20 rb hapus); lewat dari itu **ditagih**, tidak
>   ditolak. Perkiraan: hari terboros yang pernah tercatat (78–103 rb baca) ± Rp16.000 kalau terjadi tiap hari sebulan; hari biasa Rp0; ritual tutup buku
>   di bawah Rp1.000 (tarif termahal resmi US$0,06 per 100 rb baca, kurs ±Rp16.500 — perkiraan, bukan tagihan). **Anggaran peringatan Rp50.000/bulan**
>   (email di 50 / 90 / 100%) terpasang di Console › Usage and billing — itu ALARM, bukan rem: Firestore tidak punya batas belanja.
> - **Hemat baca MATI SELAMANYA** — jangan dinyalakan di perangkat mana pun (bab "Hemat baca" di bawah tinggal catatan teknis).
> - **K11 DICABUT:** toko tidak perlu tutup sesudah hari ritual. Arsip tutup buku tidak lagi berhenti di tengah karena kuota.
> - Kartu **"Perkiraan kuota Firestore"** di Uang › Tutup buku masih menghitung batas Spark: **"MEPET" / "TIDAK MUAT" di kartu itu boleh diabaikan.**
>   Angkanya tetap berguna sebagai ukuran besar-kecilnya ritual (persen dari jatah gratis sehari).

## Kenapa perlu prosedur

- Sistem lama hanya-baca sejak 25b; satu-satunya jalan tulis catatan yang tetap terbuka di sana adalah **Setelan › Muat cadangan**, dan itu pun harus
  mengetik **PULIHKAN** dulu (keputusan owner 26 Sep 2026). `/baru/` belum punya pemulih dari berkas.
- Di bawah aturan server sekarang (`firestore.rules` v7), memulihkan **pasti ditolak** untuk semua catatan yang bertanggal di bulan terkunci. Kunci
  bulan menolak siapa pun, termasuk owner.
- Karena itu, pemulihan hanya bisa berjalan selama **aturan darurat** terpasang. Aturan darurat = isi `firestore.rules.v3`: aturan akun per orang
  tetap berlaku, kunci bulan tidak ada.

> **Selama aturan darurat aktif, KUNCI BULAN TIDAK BERLAKU.** Semua bulan, termasuk yang sudah dikunci, bisa ditulis owner dan kasir darurat. Jendelanya
> harus **sesingkat mungkin**: pasang, pulihkan, langsung kembalikan `firestore.rules`.

## Keterbatasan yang WAJIB diketahui sebelum mulai

- **Hanya 27 koleksi lama yang dipulihkan.** Pemulih sistem lama (`muatDariFile`, daftar koleksinya di `index.html` tag `sistem-lama-terakhir`) hanya
  mengenal koleksi yang ada sebelum `/baru/`. `/baru/` punya 56 koleksi (`baru/js/data/koleksi.js`); ±29 koleksi milik `/baru/` — antara lain
  `wadahLiteran`, `hargaTerbit`, `pindahUang`, `slipUpah`, `absenKaryawan`, `tutupBukuAcara`, `aturanToko`, `hargaWadah`, `bukuHapus` — **TIDAK ikut
  pulih** lewat jalan ini. Kalau yang hilang termasuk koleksi itu, jalan ini tidak cukup: berhenti dan putuskan dulu (owner) sebelum menyentuh rules.
- Katalog kasir (`ringkasanKasir`) tidak ikut dipulihkan dari berkas; `/baru/` menerbitkannya ulang sendiri begitu data termuat.
- Sekali membuka sistem lama ≈ **7,4 rb baca** dokumen (jatah gratis 50 rb baca/hari; sejak Blaze lewat dari itu ditagih, tidak ditolak). Jangan dimuat ulang berkali-kali.
- **Kunci API web Firebase DIBATASI referrer.** Terbukti 1 Okt 2026: masuk dari pratinjau `localhost` (port lain) dijawab 403 "Requests from referer …
  are blocked". `localhost:8731` belum pernah dicoba — anggap ditolak sampai terbukti bisa masuk. Tempat memeriksa & mengubahnya: Google Cloud Console ›
  APIs & Services › Credentials › kunci browser ("Browser key …") › Website restrictions. "Authorized domains" (Authentication › Settings) TIDAK berlaku
  untuk masuk email + sandi. Jalannya: langkah 0, butir terakhir. Daftarnya dilihat (hanya dilihat) paling lambat 15 Des — butir di daftar periksa ritual
  tutup buku.

## Langkah (semua dikerjakan owner sendiri — sejak 13 Okt 2026 tidak ada pemeriksa dari luar; yang bisa diperiksa aplikasi disebut di langkahnya)

0. **Sebelum mulai**
   - Unduh cadangan keadaan sekarang (Menu › Toko ini › Cadangan & simpanan di `/baru/`), walaupun datanya sedang kacau — **dua kali cadangan**:
     sebelum dan sesudah.
   - Catat **jam mulai**.
   - Minta penjaga berhenti mencatat sebentar. Karcis kasir darurat tetap aman di antrean HP.
   - Siapkan dua berkas aturan dari repo: `firestore.rules.v3` (darurat) dan `firestore.rules` (yang berlaku, v7).
     Salin tanpa merusak huruf: `git show origin/main:firestore.rules.v3 | LANG=en_US.UTF-8 pbcopy` (yang berlaku: `…:firestore.rules`).
   - Siapkan sistem lama di komputer — ambil **POHON tag**, bukan `index.html` saja (supaya `lib/lz-string.js` & `lib/kemas-worker.js` ikut;
     tanpa itu cadangan lokal terkompres tidak terbaca):
     ```
     git fetch origin tag sistem-lama-terakhir     # kalau tag belum ada di komputer ini
     git worktree add /tmp/sistem-lama sistem-lama-terakhir
     # atau tanpa worktree:  mkdir /tmp/sistem-lama && git archive sistem-lama-terakhir | tar -x -C /tmp/sistem-lama
     ```
     **Tidak diterbitkan, tidak di-commit.**
   - **Pastikan ingat PIN owner.** Tombol **Owner** di gerbang sistem lama ("Sistem utama khusus owner") meminta PIN owner — PIN yang disetel 13 Agu
     2026, tersimpan teracak di `pengaturan/keamanan` dan disalin ke peramban sesudah masuk. Sejak 7 Okt 2026 `/baru/` tidak punya layar untuk
     menggantinya (tab Kasir & PIN dicabut; dokumennya tidak dihapus), dan aplikasi yang tayang tidak membacanya — gerbang ini satu-satunya pembacanya.
     Kalau lupa, bereskan SEBELUM langkah 1 (jendela darurat jangan dibuka dulu): gerbang itu hanya kunci layar, datanya dijaga akun owner. Di Console ›
     Firestore › `pengaturan/keamanan`, hapus field `acak`. Gerbang sistem lama meloloskan pemilik kalau PIN belum pernah tersalin ke peramban itu
     (`mintaPinOwner` → `pinSudahDisetel` di tag), dan simpanan `localhost` memang kosong — kalau peramban komputer itu pernah membuka sistem lama di
     `localhost:8731`, hapus dulu data situs `localhost` di setelan peramban. (Dibaca dari kode tag, belum dicoba di Console.)
   - **Izinkan `localhost:8731` di kunci API (bersyarat — lihat "Keterbatasan").** Kalau kunci browser memakai Website restrictions dan daftarnya
     belum memuat `http://localhost:8731/*`: TAMBAHKAN satu baris itu (baris lain jangan diubah) → Save, catat jamnya; perubahannya bisa butuh beberapa
     menit sampai berlaku. (Kuncinya tidak dibatasi sama sekali → lewati butir ini: menambah satu baris justru membatasi kunci itu ke `localhost` saja.)
     Lalu coba masuk SEBELUM langkah 1: jalankan server sistem lama (perintah `python3 -m http.server …` di langkah 2) dan masuk dengan akun owner —
     masuk tidak butuh aturan darurat. Ditolak (pesannya menyebut referer / 403) → tunggu beberapa menit, coba sekali lagi; tetap ditolak → jendela
     darurat (langkah 1) jangan dibuka, prosedur BERHENTI di sini: cabut baris `localhost:8731/*` itu sekarang (Save), catat jamnya, matikan server.
     Masuk berhasil → tab itu sudah memuat seluruh data sistem lama sekali (≈ 7,4 rb baca): biarkan TETAP TERBUKA, jangan dimuat ulang, dan pakai tab
     itu juga untuk langkah 2. Baris itu (hanya baris itu) DICABUT lagi di langkah 3.
1. **Pasang aturan darurat.** Console › Firestore › Rules → tempel isi `firestore.rules.v3` → **Publish**. Catat jam. Sidik v3 yang benar:
   SHA-256 berawalan `32c55d58`.
2. **Pulihkan.**
   - Tab sistem lama yang sudah masuk di langkah 0 masih terbuka → pakai tab itu (jangan dimuat ulang). Kalau belum ada: di folder sistem lama
     `python3 -m http.server 8731 --bind 127.0.0.1` → buka `http://localhost:8731/index.html`, masuk dengan akun owner.
     Simpanan lokal peramban untuk alamat `localhost` kosong — itu wajar.
   - Gerbang "Sistem utama khusus owner" → tombol **Owner** → ketik PIN owner (lihat langkah 0). Seluruh sistem lama, termasuk Setelan › Muat
     cadangan, ada di balik gerbang ini.
   - Setelan › Muat cadangan → pilih berkas → ketik **PULIHKAN** → tunggu kalimat "Berhasil diunggah …".
   - Sistem lama hanya **menambah** catatan yang id-nya belum ada. Tidak menimpa, tidak menghapus.
   - Berkas dari era tutup buku yang lain ditolak sendiri (penjaga era).
   - Sesudahnya: tutup tab, **matikan server** (Ctrl-C), hapus folder (`git worktree remove /tmp/sistem-lama` atau `rm -rf /tmp/sistem-lama`).
3. **Kembalikan `firestore.rules` SEGERA.** Tempel isi `firestore.rules` → **Publish**. Sidiknya dihitung dari repo SAAT ITU
   (`shasum -a 256 firestore.rules`; per 7 Okt 2026 = v7, berawalan `e0ed6a97`, 49.960 byte; baris 2 editor `ATURAN FIRESTORE v7 FINAL`). Catat jam.
   Jendela darurat = jam langkah 1 sampai jam langkah 3. Kalau langkah 0 menambahkan `localhost:8731` di kunci API: cabut barisnya sekarang, catat jamnya.
4. **Periksa aturan yang berlaku — owner sendiri, empat hal:**
   - (a) **Isi editor = berkas repo.** Di Console › Rules klik di editor → ⌘A → ⌘C, lalu di Terminal (folder repo, sesudah `git fetch origin`):
     `LANG=en_US.UTF-8 pbpaste | shasum -a 256` harus sama dengan `git show origin/main:firestore.rules | shasum -a 256`. Beda →
     `LANG=en_US.UTF-8 pbpaste | diff - <(git show origin/main:firestore.rules)`: kalau yang beda hanya baris terakhir dengan catatan
     `\ No newline at end of file`, itu soal baris baru di akhir, bukan beda isi [BELUM TERVERIFIKASI: belum pernah diamati apakah editor Console
     menambah / membuang baris baru terakhir].
   - (b) Baris 2 editor berbunyi `ATURAN FIRESTORE v7 FINAL` (= baris 2 berkas repo saat itu).
   - (c) **Rules Playground — HANYA empat kasus:** ★A1 LOLOS, ★K3 DITOLAK, ★F1 LOLOS, ★R1 LOLOS. Isian & akunnya di `docs/uji-rules-v7.md` (tabel
     "Wajib owner" no. 1, 3, 4, 5; bagian "Isian Playground"); keempatnya lulus di Playground 7 Okt (bagian "Hasil Playground"). Keempatnya kasus *create*
     tanpa dokumen uji, dan Playground tidak menulis apa pun. Kasus lain di berkas itu JANGAN dijalankan saat darurat: sebagian tidak bisa dinilai
     Playground (`getAfter`, *timestamp* ketikan), sebagian butuh dokumen uji U1–U11 — dan dokumen uji tidak boleh dibuat (lihat "Yang tidak boleh").
   - (d) Satu nota dari kasir darurat (HP penjaga) → masuk di Jual `/baru/`.

   Ada yang tidak sesuai → tempel lagi `firestore.rules` dari repo → Publish, ulangi (a)–(d) **sekali**. Masih tidak sesuai:
   - **(b) baris 2 BUKAN `ATURAN FIRESTORE v7 FINAL`** (aturan darurat atau aturan lain masih terpasang) → JANGAN berhenti. Salin ulang dengan
     `git show origin/main:firestore.rules | LANG=en_US.UTF-8 pbcopy`, tempel, Publish, baca pesan galat Publish kalau ada, ulangi sampai baris 2 =
     v7 FINAL. Selama itu penjaga tetap berhenti mencatat dan aplikasi di perangkat lain jangan dibuka: aturan darurat tidak boleh tertinggal (lihat
     "Yang tidak boleh").
   - **Baris 2 = `ATURAN FIRESTORE v7 FINAL`**, bedanya hanya di sidik / komentar (a) atau di (c) / (d) → berhenti menempel (jangan v3 lagi, jangan v6):
     biarkan yang terpasang, tulis hal yang tidak sesuai + tangkapan layarnya di catatan langkah 5. Kalau yang gagal (d): penjaga mencatat di kertas,
     owner memindahkannya ke `/baru/`.
5. **Periksa & catat.**
   - Unduh cadangan kedua (sesudah).
   - Di `/baru/`: daftar periksa kunci bulan, dan angka bulan terkunci (laba, neraca) — bandingkan dengan sebelum kejadian.
   - Kalau kejadiannya sesudah tutup buku (Januari–Februari, atau sebelum berita acara "selesai"): Uang › Tutup buku › kartu **Pemeriksaan sesudah tutup
     buku** harus kembali "Semua … pemeriksaan sama". Unduh hasilnya (tombol "unduh hasil pemeriksaan (berkas)") dan simpan bersama cadangan kedua.
   - Masuk ke sistem lama ikut menulis denyut perangkat (sistem lama di `localhost`, tanpa nama). Sesudah 24 jam: Uang › Tutup buku › kartu **Kunci
     bulan**, butir "Semua perangkat berdenyut dalam 24 jam terakhir" → ketuk "<…> sudah tidak dipakai" untuk perangkat itu (dua ketukan). Tanpa itu
     butir ⛔ itu menahan kunci bulan. Tombolnya tidak muncul → jalannya
     di butir "Perangkat hilang atau rusak" (daftar periksa ritual, Sampai 31 Des).
   - Tulis kejadiannya di `docs/peta-kunci-periode.md`: tanggal, jam buka dan tutup jendela darurat, alasan, berkas cadangan yang dipakai, siapa
     yang menempel aturan, jam `localhost:8731` ditambah & dicabut di kunci API (kalau langkah 0 memakainya), dan hasil langkah 4.

## Yang tidak boleh

- Membiarkan aturan darurat terpasang melewati hari itu.
- Membuat dokumen uji U1–U11 dari `docs/uji-rules-v7.md`, atau membuat / mengubah / menghapus `aturanToko/kunciPeriode`, selama darurat. Dokumen uji
  hanya untuk menerbitkan rules BARU (toko tutup, satu duduk); U2 = `aturanToko/kunciPeriode` uji yang menimpa kunci bulan sungguhan.
- Menerbitkan sistem lama ke situs lagi (mengembalikan `index.html` lama ke `main`) untuk memulihkan. Jalankan di komputer dari tag.
- Memulihkan lewat aturan yang berlaku lalu "mengulang sampai berhasil". Catatan bulan terkunci tidak akan pernah lolos.
- Menghapus `aturanToko/kunciPeriode` supaya pemulihan lolos. Dokumen kunci tidak pernah dihapus (rules menolaknya, dan menghapus lewat Console =
  membuka semua bulan tanpa jejak).


---

## Jalan mundur tutup buku (siap 2027, owner 7 Okt 2026)

Tutup buku tahunan (Uang › Tutup buku, `baru/js/layar/tutup-buku-logika.js`) menulis **saldo pembuka** tahun baru lalu **memindah** semua catatan tahun
lama ke koleksi `arsipTahun` (tidak dihapus). Titik baliknya satu: **kiriman penanda** — kiriman TERAKHIR saldo pembuka (batch pembuka bertanda
`penandaBuku` + `pengaturan/tutupBuku` + berita acara `terkunci`). Jalan mundurnya tergantung di mana ritual berhenti:

| Keadaan (pita di Uang › Tutup buku) | Angka toko | Jalan mundur | Cadangan SEBELUM |
|---|---|---|---|
| **Sebelum penanda** — "Tutup buku 2026: n dari N saldo pembuka sudah masuk. Tahun 2026 MASIH TERBUKA" | utuh tahun lama (saldo pembuka yang sudah masuk tidak dihitung) | **batalkan** di pita | masih sah |
| **Sesudah penanda, sebelum selesai** — "Tahun 2026 terkunci; … catatan belum pindah ke arsip" / "… arsipnya habis" | selama arsip berjalan: stok, piutang & utang **DOBEL** | **batalkan** di pita (dua ketukan) | berkas sejarah — ditolak penjaga era |
| **Sesudah "selesai"** | buku tahun baru | **tidak ada tombol** (lihat 3) | berkas sejarah |

### 1. Sebelum penanda masuk

- Ketuk **batalkan** di pita, dari perangkat yang memulai (pemegang). Saldo pembuka yang sudah masuk ditarik, per kiriman ≤ 18 pemeriksaan. Tidak ada
  arsip yang perlu dikembalikan. Kuotanya kecil (± dua kali jumlah saldo pembuka, tulis & hapus).
- Atau **lanjutkan** — kiriman yang sudah masuk tidak dikirim ulang.

### 2. Sesudah penanda, sebelum "selesai"

- **Jangan berjualan atau menagih** selama arsip belum habis (angka DOBEL) atau selama pembatalan berjalan (angka KURANG: bagian yang belum kembali
  terbaca nol).
- **Batalkan** (dua ketukan): berita acara `membatalkan` + era mundur + titik kas 31 Des dikembalikan (kalau titiknya belum maju) → saldo pembuka
  ditarik → SELURUH arsip tahun itu dibaca dan dikembalikan → berita acara `dibatalkan`. Terhenti di tengah → **Lanjutkan** dari perangkat yang sama;
  yang sudah ditarik / dikembalikan tidak diulang.
- **Kuota:** pembatalan sesudah arsip penuh butuh ± sebesar ritualnya lagi — angkanya tampil di langkah 1 ("Kalau dibatalkan sesudah arsip"). Sejak
  Blaze (9 Okt 2026) itu tidak lagi tertahan kuota — kelebihannya ditagih (kecil). Toko tetap tidak buka sampai pembatalan tuntas (angka KURANG).
- Catatan bertanggal tahun lama yang mendarat SESUDAH penanda (karcis HP penjaga yang tertahan tanpa sinyal) tidak ikut diarsip; pita menyebutnya dan
  jalannya ("sudah dicatat" — catatannya tidak dihapus). Itu bukan alasan membatalkan. Kalimatnya per jenis: nota (uang di laci LEBIH, omzet tahun itu
  kurang), pengeluaran (uang KURANG, biaya tahun itu kurang → labanya terlihat lebih besar), catatan lain (selisih uang muncul di tutup hari berikutnya).
- **Pesanan** bertanggal Desember yang belum tuntas saat ritual memang TIDAK diarsip (masih berjalan). Dicatat di hasil periksa saat arsip habis dan
  di berita acara saat selesai (`tertinggal`); kalau dibayar / dibatalkan di Januari, ia **bukan** catatan susulan — pesanan bukan uang & bukan stok,
  notanya bertanggal hari bayar.

### 3. Sesudah "selesai"

- Tidak ada tombol, dan aturan server (v7) menolak berita acara `selesai` diubah dari aplikasi. **Anggap tahun itu final:** kesalahan yang ketahuan
  belakangan dibetulkan dengan catatan HARI INI (Stok › Cocokkan, bayar bon, catat bon yang terlupa) — bukan dengan membuka tahun lama.
- Jalan pulang darurat (keputusan owner; belum pernah diuji di server; dikerjakan owner sendiri lewat Console — tidak ada pemeriksa dari luar sesudah
  13 Okt 2026; yang dicocokkan sesudahnya ada di langkah 5):
  1. Unduh cadangan keadaan sekarang — dua kali (sebelum & sesudah).
  2. Lewat Console, hapus saldo pembuka tahun itu: dokumen ber-`tutupBuku: true` dan `tahunDari: <tahun>` di `batchMasuk` (batch `penandaBuku`
     PERTAMA), `piutangMutasi`, `kasbonMutasi`, `produksiKemasan`, `stokBahanKemasan`, `stokBahanLiteran`, `utangPemasokMutasi`, `utangOwnerMutasi`,
     `amplopLaba`, `modalOwner` (daftar = `CACHE_PEMBUKA` di `baru/js/data/toko.js`). Sesudah itu era mundur.
  3. Kembalikan catatan tahun itu: tiap dokumen `arsipTahun` bertahun itu → tulis `dok` ke koleksi `koleksi` dengan id `idAsli`, lalu hapus salinan
     arsipnya. **Belum ada alat** untuk ribuan dokumen; alternatifnya pemulih berkas (bab di atas) dengan cadangan SEBELUM — baru diterima sesudah
     langkah 2, dan hanya 27 koleksi lama yang pulih.
  4. Lewat Console: `pengaturan/tutupBuku` (`tahunDitutup` = tahun sebelumnya) dan berita acara (`status: 'dibatalkan'`). Titik kas: tulis ulang dari
     hitungan laci terakhir.
  5. Cocokkan 14 baris (Uang › Tutup buku, latihan) dengan berita acara lama, lalu catat kejadiannya di `docs/peta-kunci-periode.md`. Kalau sesudahnya
     tutup buku tahun itu diulang sampai selesai, kartu **Pemeriksaan sesudah tutup buku** harus "Semua … pemeriksaan sama" (lihat bab di bawah).
- Bulan yang sudah dikunci tidak bisa ditulis siapa pun. Kunci Januari tahun baru baru boleh **sesudah** tutup buku selesai (daftar periksa kunci bulan
  menolak sendiri) — jadi kalau jalan pulang ini dipakai, jalankan SEBELUM ada bulan tahun baru yang dikunci.

## Daftar periksa ritual tutup buku 2026 (1 Jan 2027)

> Tempat di Menu: laci **Toko ini** › **Perangkat & antrean** (tab Perangkat · Antrean kirim · Hemat baca) dan **Cadangan & simpanan**. Kalimat layar
> yang masih menulis "Menu › Sistem › Perangkat …" menunjuk tempat yang sama.

**Sampai 31 Des (owner):**
- [ ] Tutup hari setiap malam sampai 31 Des. Tutup hari 31 Des = tulisan TERAKHIR bertanggal 2026.
- [ ] **Cara hitung modal (FIFO, keputusan owner 9 Okt):** Stok › HPP / modal › kartu "Cara hitung modal". Pilih hari mulai (besok, atau
      **1 Jan 2027** = tahun buku baru) → PAKAI FIFO → ketuk sekali lagi. Mau mulai 1 Jan: tekan paling lambat 31 Des, dari satu perangkat online —
      HP karyawan menerima setelannya sebelum hari itu. Nota yang sudah tercatat tidak berubah; pajak omzet tidak berubah. Kembali ke rata-rata = tombol
      yang sama (dua ketukan).
- [ ] **HET (Harga & Pemasok › Katalog › Atur HET):** petakan tiap kelas/merek ke premium / medium / bukan beras HET. Sebelum dipetakan, peringatan
      HET tidak menyala ("belum dipetakan", bukan "aman").
- [ ] Hari berjualan tanpa tutup hari: Uang › Tutup buku › langkah 1 → tiap tanggal "tidak ditutup — diterima apa adanya" + alasan (min. 5 huruf),
      **Simpan putusan** (tersimpan sungguhan, juga dari latihan; ikut berita acara). Tutup hari tidak dibuat mundur.
- [ ] Tidak ada buku beras / kemasan / kantong yang minus, tidak ada kelebihan bayar pelanggan, bayar lebih ke pemasok / owner, atau kasbon dibayar
      lebih (langkah 1, butir g6 menyebut buku/namanya dan jalannya: opname di Stok › Cocokkan, catat bon / kedatangan / kasbon yang terlupa).
      - **Kelebihan bayar pelanggan** — g6 menyuruh "kembalikan uangnya" atau "balik hapus bukunya", tapi tombol untuk keduanya belum ada di `/baru/`.
        Jalannya: kalau orang itu belanja Kredit lagi sebelum 31 Des, kelebihannya terpakai sendiri (nota Kredit berikutnya memakainya lebih dulu).
        Kalau uangnya sudah dikembalikan tunai, atau ternyata bayar ganda: unduh cadangan dulu, lalu di Console › Firestore › Data › `piutangMutasi`
        kecilkan `nominal` (atau hapus) dokumen pembayaran orang itu (`tipe` "bayar", bertanggal ≤ 31 Des) sebesar kelebihannya. Hapus buku yang
        ternyata dibayar: kecilkan / hapus dokumen `tipe` "hapusBuku" orang itu sebesar yang dibayar — atau, untuk hapus buku yang ternyata
        dibayar, pakai tombol **"Balik hapus buku"** di lembar orang itu (Paket F2, tanpa Console). Ubahan lewat Console sampai sendiri ke semua perangkat
        (hemat baca mati — aplikasi mendengarkan semua catatan), lalu periksa g6 di LATIHAN.
        Console hanya membereskan sisi bon, bukan sisi laci. Uang yang dikembalikan tunai tidak punya catatan di sistem baru, jadi tutup hari pada hari
        uangnya diserahkan KURANG sebesar itu: pilih alasan yang paling dekat (bawaan: "Ada pengeluaran belum dicatat") dan tulis di kertas untuk
        konsultan (tanggal, nama, berapa). Laba bersih bulan itu ikut turun sebesar itu di baris "Lebih/kurang kas", padahal bukan rugi toko. Bayar
        ganda (tercatat dua kali, uangnya sekali): tutup hari tanggal aslinya sudah menyimpan selisih kurang itu, dan selisihnya tidak hilang walau
        bayarnya dikecilkan — sebut juga ke konsultan.
      - **Pencegahan:** jangan mencatat bayar bon atau hapus buku untuk SATU nama dari dua perangkat sekaligus, atau dari perangkat yang tanpa internet.
- [ ] Semua karcis kasir darurat dirinci; nama kembar disatukan; piutang lama (piutang mati) diputuskan jauh sebelum latihan 16 Des.
      - **DIPUTUSKAN owner 8 Okt 2026:** hapus buku SEMUA nama yang tidak pernah membayar / mencicil selama berutang; yang masih mencicil tetap ditagih.
        Catatannya JANGAN hilang: sebelum menghapus, buka Pelanggan › Bon › nama › **Kartu piutang berkop** › simpan PDF (jejak tetap — sesudah tutup buku
        2026 catatan tahun 2026 ikut diarsip). Hapus buku sendiri tidak menghapus apa pun: ia menambah satu catatan, riwayatnya tetap di lembar orang itu,
        dan namanya tampil di daftar **"Dihapus dari buku"** di atas tab Bon.
      - **Kalau orang yang sudah dihapus buku datang membayar** (Paket F2): Pelanggan › Bon › daftar "Dihapus dari buku" › nama › **"Dibayar sesudah dihapus
        buku"** → jumlah (paling banyak sebesar yang dulu dihapus), Tunai / QRIS → ketuk dua kali. Hapus buku lama TETAP ada; dibalik dengan catatan baru,
        jadi laba bulan itu NAIK sebesar uang yang kembali, laci / rekening bertambah. Kalau pembayarannya terlanjur dicatat dari HP kasir (pita "hapus buku
        yang ternyata dibayar"), tombol yang sama berbunyi **"Balik hapus buku"** — cukup dibalik, uangnya tidak dicatat dua kali.
        **Batas:** sesudah tutup buku 2026, hapus buku tahun 2026 ikut diarsip — pembayaran tahun 2027 untuk nama yang dihapus 2026 belum punya tombol;
        jejaknya ada di PDF kartu piutang. Jangan dicatat sebagai pembayaran bon (jadi kelebihan bayar) atau penjualan; catat di buku kertas dan sebut ke
        konsultan.
- [ ] **Karcis kasir darurat yang isinya tidak sama dengan nominalnya — DIPUTUSKAN owner 8 Okt 2026: diterima apa adanya, per kelompok.** Kelompok
      Agustus: isinya lebih kecil dari nominal (karcis hari-hari pertama sistem). Kelompok September: isinya lebih besar, karena karcisnya dirinci dua
      kali oleh sistem lama yang sudah pensiun. Alasan tertulisnya = butir ini; angkanya diserahkan ke konsultan **paling lambat 31 Jan 2027**. Daftar
      per karcis (tanggal, nominal, isi yang berlaku) ada di berkas privat owner di Mac (`_privat/kesiapan-2027/karcis-isi-beda.json`, tidak masuk repo),
      bukan di dokumen ini. **JANGAN dirinci ulang** — merinci ulang
      memotong stok dua kali. Koreksi lewat aplikasi memang tidak tersedia, dan sistem baru menolak merinci karcis yang sudah dirinci, jadi kelompok ini
      tidak bertambah. g4 hanya menghitung karcis yang BELUM dirinci, jadi kelompok ini tidak menahan ritual.
- [ ] **Modal awal 8 Agu 2026 — DIPUTUSKAN owner 8 Okt 2026: dibiarkan, tidak dicatat.** Tidak ada catatan modal yang dibuat untuk posisi toko
      sebelum sistem mulai mencatat, jadi neraca tetap menulis selisih "belum terjelaskan buku" dan selisih itu ikut terbawa di potret 2026. Kalimat
      tetapnya SATU bunyi dan dipasang di aplikasi oleh PR #121 (`LP_KALIMAT_MODAL_AWAL` di `baru/js/layar/laporan-logika.js`): tercetak di Neraca
      berkop dan berita acara tutup buku. Dokumen ini sengaja tidak menyalin bunyinya, supaya tidak ada dua bunyi. Selama PR #121 belum digabung, kalimat
      itu belum tercetak: sampaikan sendiri ke konsultan bersama PDF Neraca 31 Des.
- [ ] Upah karyawan dibayar & dicatat sampai 31 Des bila bisa. Yang belum dibayar tercatat di berita acara (baris "Upah karyawan yang belum dibayar");
      kalau dibayar Januari, biayanya masuk Januari (bukan 2026).
- [ ] (Cadangan kertas, disarankan) simpan PDF, dari tombol **simpan PDF** di bawah kertasnya:
      - Laporan › Pajak › Rekap pajak untuk konsultan 2026;
      - Laporan › Dokumen › Laporan berkop › Laba-Rugi › bulan akhir **Desember 2026** › **12 bulan**;
      - Laporan › Neraca › tanggal **31 Des 2026** (sesudah tutup hari 31 Des, atau 1 Jan sebelum ritual).

      Layar Laporan › Tahunan TIDAK punya tombol simpan PDF, dan ⌘P bisa mencetak struk terakhir, bukan laporannya. Sejak Paket B (Okt 2026) layar
      Pajak, Laporan & Dasbor membaca tahun yang sudah ditutup dari **potret** di berita acara (lihat "Sesudahnya"); PDF ini pegangan kalau potretnya
      kelak tidak terbaca.
- [ ] LATIHAN sekali (16–30 Des). Layar selalu membuka di LATIHAN. Langkah 6 (Kunci) latihan menyusun **potret 2026** tanpa menulis apa pun dan
      menyebut hasilnya ("Potret 2026: 12 bulan & … hari berjualan · omzet sistem … · laba bersih … · neraca 31 Des …"). "Potret 2026 GAGAL" = kunci
      sungguhan akan DITOLAK. Yang bisa dikerjakan sendiri: tutup lalu buka lagi aplikasinya, ulangi latihan sekali. Kalau tetap GAGAL: tutup buku 2026
      jangan dipaksakan — toko tetap boleh berjualan dengan buku 2026 terbuka (Laporan & Pajak 2026 tetap membaca catatannya), simpan ketiga PDF di
      butir atas (Rekap pajak, Laba-Rugi 12 bulan, Neraca 31 Des) dan cadangan; kunci bulan Januari 2027 menunggu sampai tutup buku 2026 selesai (daftar
      periksa kunci bulan menolak sendiri).
- [ ] Retur barang yang sudah diketahui dicatat SEBELUM ritual (Jual › Retur, selagi notanya masih di daftar) — sesudah ritual nota 2026 tidak muncul
      lagi di daftar Retur (lihat "Sesudahnya").
- [ ] **Perangkat hilang atau rusak** (tidak bisa dinyalakan lagi). Perangkat yang diam lebih dari 24 jam ditawari tombol "<nama> sudah tidak dipakai"
      di kartu **Kunci bulan** (Uang › Tutup buku, butir "Semua perangkat berdenyut dalam 24 jam terakhir") — TAPI hanya kalau laporan terakhirnya
      menyebut antrean 0 dan ditolak 0. Kalau laporan terakhirnya menyebut antrean / ditolak lebih dari 0, tombol itu TIDAK MUNCUL untuk perangkat itu
      (jangan dicari), dan butir ⛔ itu (juga butir "Tidak ada perangkat yang masih menyimpan antrean" kalau antreannya > 0) menahan kunci bulan
      selamanya. Jalannya (owner, Console):
      1. Foto baris perangkat itu di Menu › Toko ini › Perangkat & antrean (nama, denyut terakhir, antrean, ditolak). Foto itu satu-satunya bukti berapa
         catatan ikut hilang bersama perangkatnya: `perangkatStatus` TIDAK ikut berkas cadangan.
      2. Console › Firestore › Data › `perangkatStatus` › dokumen perangkat itu (kolom `nama`, `pada` = denyut terakhir, `antrean`, `gagal` = ditolak;
         cocokkan dengan foto) › **Delete document**. Daftar di `/baru/` ikut berubah sendiri; kalau perangkatnya ternyata hidup lagi, denyutnya tercatat
         ulang sendiri.

      Kerjakan di Desember, paling lambat sebelum kunci Januari 2027 (4 Feb).
- [ ] **Paling lambat 15 Des: LIHAT (jangan ubah) daftar referrer kunci API** — Google Cloud Console › APIs & Services › Credentials › kunci browser ›
      Website restrictions: apakah `http://localhost:8731/*` ada di daftar, atau kuncinya tidak dibatasi. Catat hasilnya bersama cadangan. Ini menentukan
      apakah jalan pulih darurat dari berkas (bab paling atas) bisa masuk; kalau barisnya tidak ada, langkah 0 butir terakhir yang menambahkannya saat
      darurat.
- [ ] 31 Des malam: Menu › Toko ini › Perangkat & antrean › tab Perangkat — tiap perangkat "semua sampai" dan tanpa "ditolak server"; HP penjaga lalu
      dimatikan.

**1 Jan 2027 (Jumat, toko tutup):**
- [ ] **Mulai dini hari 1 Jan, langsung sesudah tutup hari 31 Des** (keputusan owner K3, 9 Okt 2026). (Dulu "sesudah 15.00 WIB" karena kuota Spark
      baru penuh lagi jam itu — sejak Blaze 9 Okt 2026 kuota bukan batas.) Mulai dini hari supaya arsip pasti habis jauh sebelum toko buka 2 Jan.
- [ ] Mac, tab peramban (bukan web app iPhone/iPad), SATU perangkat, jangan muat ulang aplikasi.
- [ ] Sebelum langkah 1: **TUTUP aplikasi di iPhone / iPad / HP lain** (geser keluar dari daftar aplikasi, tab peramban ditutup — layar mati saja tidak
      cukup) dan jangan dibuka sampai pita "Tahun 2026 terkunci dan arsipnya habis". Bukan lagi soal kuota: selama arsip berjalan stok, piutang & utang
      terhitung DOBEL di perangkat mana pun, dan perangkat lain yang terbuka bisa dipakai berjualan atau menagih dengan angka DOBEL itu.
- [ ] Uang › Tutup buku › **SUNGGUHAN** → langkah 1: g1–g6 semua ✓ (g7 tidak muncul — hemat baca mati). Kartu **Perkiraan kuota Firestore**:
      "Muat dalam kuota satu hari", "MEPET", atau "TIDAK MUAT" — **ketiganya: mulai** (kartu masih menghitung batas Spark; sejak Blaze kelebihannya
      ditagih, tidak menghentikan arsip). K11 (toko tutup 2 Jan) DICABUT 9 Okt 2026. Arsip terhenti karena sebab lain (internet putus, Mac tertidur, aplikasi
      tertutup) → **Lanjutkan** dari Mac yang sama; sampai pita "Tahun 2026 terkunci dan arsipnya habis" toko jangan berjualan atau menagih. Tutup buku
      2027 (ritual Sabtu 1 Jan 2028) sama: mulai hari itu, tunggu arsip habis — arsip setahun penuh lebih lama, tapi tidak menunggu reset kuota.
- [ ] Langkah 2: cadangan SEBELUM → cek berkasnya ada di Unduhan, salin ke luar Mac.
- [ ] Langkah 3: arsip → cek berkasnya ada.
- [ ] Langkah 4: saldo pembuka → semua 14 baris ✓ (12 baris harta & utang + modal owner + upah belum dibayar).
- [ ] Langkah 5: paraf owner + saksi. Langkah 6: kunci (dua ketukan) → tunggu kiriman & arsip habis. Terhenti → Lanjutkan dari perangkat yang sama.
      - Truk datang sebelum pita "Tahun 2026 terkunci dan arsipnya habis" (ritual tertunda)? Kedatangannya dicatat SESUDAH pita itu — barangnya boleh
        diturunkan, bon kertasnya disimpan dulu; jangan dicatat sebelum langkah 6, jangan juga selama arsip berjalan. Sudah terlanjur dicatat sebelum
        langkah 6: bab "Pemeriksaan sesudah tutup buku", butir **"Stok beras" beda karena kedatangan Januari yang dicatat SEBELUM kunci**.
- [ ] Pita "terkunci dan arsipnya habis … semua baris sama" → cocokkan utang pemasok & utang toko ke owner dengan catatan kertas.
- [ ] Pita catatan susulan ("… masuk SESUDAH tutup buku …") → ikuti jalannya, ketuk "sudah dicatat".
- [ ] **Kartu "Pemeriksaan sesudah tutup buku 2026"** (paling atas di Uang › Tutup buku, muncul sendiri begitu arsip habis) — ini pengganti pemeriksaan
      cadangan SESUDAH yang dulu dikerjakan di luar aplikasi. Harus berbunyi **"Semua 27 pemeriksaan sama — tutup buku 2026 beres"** (jumlahnya bisa beda
      kalau barisnya bertambah; yang penting "Semua … sama"). Lihat bab "Pemeriksaan sesudah tutup buku" di bawah untuk arti tiap baris dan jalannya.
      - "… pemeriksaan beda — jangan jualan/menagih dulu" → JANGAN ketuk "selesai". Ikuti petunjuk di kartu: batalkan (pita, dua ketukan, dari perangkat
        yang memulai), tunggu tuntas, ulangi ritual dari langkah 1.
      - "… belum bisa diperiksa" → BUKAN lulus. Tunggu sampai data selesai dimuat & antrean kosong (Menu › Toko ini › Perangkat & antrean › Antrean
        kirim), lalu buka Tutup buku lagi.
- [ ] Langkah 7: cadangan SESUDAH & selesai. Lalu di kartu pemeriksaan ketuk **"unduh hasil pemeriksaan (berkas)"**
      (`pemeriksaan-tutup-buku-2026-miqbal.json`). Salin cadangan SEBELUM, berkas arsip, cadangan SESUDAH, dan hasil pemeriksaan ke ≥ 2 tempat di luar Mac
      (simpan 10 tahun).
- [ ] **Perangkat lain sesudah ritual** (iPhone, iPad, HP lain yang membuka `/baru/` dan tertutup selama ritual — termasuk yang aplikasinya tetap
      terbuka tapi tidur / tanpa internet selama ritual): buka satu per satu, sekali, dan biarkan membaca penuh sendiri.
      Perangkat itu membuka dengan catatan 2026 di simpanannya SEKALIGUS saldo pembuka, jadi angkanya DOBEL sementara sampai bacanya selesai. Pil
      "memuat…" TIDAK bisa dipegang — ia sudah hilang begitu simpanan perangkat terbaca, sebelum server selesai mengirim arsip & saldo pembuka. SEBELUM
      dipakai untuk Jual, bayar bon, bayar bon pemasok, atau membaca stok: buka dengan internet, tunggu ±1 menit sesudah "memuat…" hilang, lalu
      cocokkan satu angka dengan Mac (mis. bon satu pelanggan di Pelanggan). Sama → boleh dipakai.

**Sesudahnya:**
- [ ] Laporan › Pajak membuka **2026** dengan sendirinya selama Januari–Maret masih ada masa terutang (pilihan tahun di atas kartu). Angka sistem 2026 =
      potret saat kunci (sama rupiah demi rupiah dengan sebelum ritual); omzet di luar sistem & setoran 2026 tetap bisa dicatat. Catat setoran masa
      **Desember 2026** (tempo 15 Jan 2027) beserta NTPN; cetak Rekap pajak 2026 untuk konsultan / SPT Tahunan (31 Mar 2027).
- [ ] Laporan (Laba, Biaya, Bulanan, Tahunan, Neraca akhir bulan, Dokumen berkop) & Dasbor 2026 dari potret. Yang ikut arsip dan TIDAK di potret:
      daftar per nota (nota rugi, tanpa modal, susut), rincian uang keluar per catatan, buku kas & per jam tiap hari, neraca tanggal selain akhir bulan —
      layar menyebut "sudah diarsip", tidak menggambar Rp0. Rinciannya di berkas arsip & cadangan SEBELUM.
- [ ] Profil pajak: "Omzet tahun 2026" untuk batas Rp4,8 miliar 2027 — layar 2027 menawarkan angka dari sistem (potret + isian di luar sistem);
      angka konsultan menang. Aturan pajak bertanda "diisi untuk tahun 2026" sampai owner/konsultan memastikan aturan 2027 lalu menekan "Pakai aturan"
      dari layar 2027.
- [ ] Bon pelanggan langganan, saran belanja (laju 14 hari), dan daftar pelanggan memakai ringkasan tahun 2026 yang dibawa batch penanda — tidak
      perlu membuka kredit per nota sampai April. Harga & Pemasok › Belanja juga dari ringkasan itu: pemasok di truk, harga beli terakhir per merek
      (tanggalnya tetap tanggal kiriman 2026), muatan truk, saran, dan pesanan Desember yang barangnya sudah datang — sama dengan sebelum ritual; kiriman
      Januari menggantikan harga merek yang dikirimnya. Kalau Belanja kosong pemasok & harga, ringkasannya tidak terbaca: harga terakhir ada di bon kertas
      atau cadangan SEBELUM.
- [ ] Kunci bulan Januari 2027 paling cepat 4 Feb, HANYA sesudah tutup buku 2026 "selesai" (daftar periksa kunci bulan menolak sendiri, Beranda
      tidak menyuruh mengunci selama itu). Sebelum mengetuk kunci: buka Uang › Tutup buku sekali lagi — kartu **Pemeriksaan sesudah tutup buku 2026**
      (tampil sampai akhir Februari) harus tetap "Semua … sama". Kuncinya sendiri di kartu **Kunci bulan** di layar yang sama: centang butir yang diminta,
      putuskan tiap hari tanpa tutup hari, lalu "KUNCI JANUARI 2027" dua ketukan. Tidak butuh Console — kecuali butir ⛔ perangkat yang tidak
      berdenyut menyebut perangkat hilang yang laporan terakhirnya masih antrean / ditolak: jalannya di butir "Perangkat hilang atau rusak" (Sampai 31 Des).
- [ ] **Retur barang 2026** yang baru datang sesudah ritual: notanya sudah diarsip, jadi tidak ada di daftar Jual › Retur. Pakai Jual › Retur ›
      **"Tidak ada notanya? Retur ketik tangan"**. Retur ketik tangan hanya menerima karung (utuh atau setengah) dan kemasan per unit; retur literan /
      eceran tidak punya jalan di layar Retur — kalau terjadi, uang yang diserahkan membuat tutup hari malam itu KURANG: pilih alasan yang paling dekat
      dan catat di kertas untuk konsultan. Kalau notanya nota BON, urutannya:
      1. Pastikan dulu barangnya bisa dicatat lewat retur ketik tangan (karung utuh / setengah, atau kemasan per unit). Tidak bisa → jangan catat apa pun.
      2. Catat pembayaran **Tunai** di bon orang itu (Pelanggan › Bon › Catat pembayaran) sebesar nilai barangnya, tapi **paling banyak sebesar sisa
         bonnya** — aplikasi menolak pembayaran yang melebihi sisa, dan bon yang sudah lunas tidak punya tombol Catat pembayaran (lewati langkah ini).
      3. Catat retur ketik tangan dengan **Uang kembali** sebesar nilai barangnya.
      4. Uang yang benar-benar diserahkan ke pembeli = nilai barang − yang dicatat sebagai bayar di langkah 2 (nol kalau sisa bonnya cukup). Dua catatan
         itu saling menutup di laci sebesar bayarnya, dan bonnya berkurang sebesar itu.

      JANGAN pakai hapus buku untuk retur.
- Saldo pembuka **modal owner** bertanggal 31 Des 00.00 (`modalOwner`, `tutupBuku: true`) membawa JUMLAH modal yang tertanam — bukan setoran atau
  penarikan. Ambil pribadi Desember, buku Owner & toko ("Modal owner dibawa dari tahun lalu"), bukti setoran, dan buku kas harian 31 Des tidak
  menghitungnya sebagai gerakan uang. Laporan arus kas mesin (Desember / 31 Des tahun yang sudah ditutup) masih menyebutnya "Modal owner disetor/
  ditarik — Saldo pembuka…": itu **bukan** uang yang bergerak; angka tahun yang ditutup dibaca dari berita acara sampai layar Laporan & Pajak bisa
  membaca tahun yang ditutup (paket B).

## Pemeriksaan sesudah tutup buku — kartu di Uang › Tutup buku (Paket C, 7 Okt 2026)

Pengganti butir "cadangan SESUDAH diperiksa (hanya baca)" di rencana tutup buku: aplikasi memeriksa sendiri, owner membaca hasilnya. Kartu
**"Pemeriksaan sesudah tutup buku <tahun>"** muncul begitu tahun dikunci & arsipnya habis, dan tetap ada sepanjang Januari–Februari tahun berikutnya
(ritual telat: 30 hari sesudah selesai). Tahun berikutnya pun sama (tahun = yang terakhir ditutup). Kartu HANYA MEMBACA data yang sudah ada di perangkat:
tidak membaca server lagi, tidak menulis apa pun.

**Tiga keadaan tiap baris** — ✓ **sama** · ✗ **beda** (dua angkanya: sebelum → sesudah; baris rak Jual & stok minus: keadaannya sekarang) · ? **belum bisa
diperiksa** (sebabnya ditulis: data belum dimuat, ditolak server, perangkat tanpa internet, data masih simpanan perangkat, atau masih menunggu server). "?"
BUKAN lulus.
Ringkasan di atas: "Semua N pemeriksaan sama — tutup buku 2026 beres", "K pemeriksaan beda — jangan jualan/menagih dulu, lihat barisnya", atau "M dari N
pemeriksaan belum bisa diperiksa …". Tombol "lihat semua N baris" menampilkan baris yang sama; "unduh hasil pemeriksaan (berkas)" menyimpan hasilnya
(`pemeriksaan-tutup-buku-<tahun>-miqbal.json`) — simpan bersama cadangan SESUDAH.

| Kelompok | Yang diperiksa | Kalau ✗ beda |
|---|---|---|
| 1 · Baris perbandingan | stok beras, kemasan, kantong, kasbon, uang per tempat, modal, upah belum dibayar: angka mesin sebelum = sesudah ritual pada hari tutup buku (hasil yang dibekukan saat arsip habis) | belum selesai → batalkan di pita, ulangi; sudah selesai → lihat "Jalan keluar" |
| 2 · Modal owner | saldo pembuka modal (dibaca mesin) = modal di neraca 31 Des yang tersimpan di potret | sama |
| 3 · Saldo pembuka & rak Jual | semua saldo pembuka yang direncanakan berita acara ada di buku, dijumlah lagi = berita acara 31 Des (bon lama pemasok yang dibetulkan owner sesudahnya dibandingkan dengan nilainya saat kunci, dan disebut); buku beras per merek & kemasan per produk saat tahun baru dibuka = sisa per merek / produk di catatan 31 Des yang disimpan berita acara saat kunci; tanda buku 25 kg / wadah / adukan / karung belakang terbaca; buku 25 kg tampil di rak Jual atas nama induknya, merek berharga tidak hilang dari rak | jangan jual merek yang disebut; jalan seperti kelompok 1 |
| 4 · Pajak dari potret | 12 bulan potret lengkap; omzet Laporan › Pajak = potret; setoran yang tercatat saat dikunci masih ada — jumlahnya dan tiap NTPN-nya (setoran sesudahnya boleh menambah, tapi tidak menutupi bukti setor yang hilang); 12 masa bertanda "tutup buku" | SPT & setoran Desember pakai PDF yang disimpan sebelum ritual (Rekap pajak, Laba-Rugi 12 bulan, Neraca 31 Des); setoran yang hilang dicatat lagi dari bukti setornya (NTPN) di Laporan › Pajak |
| 5 · Stok minus | saldo pembuka tidak membawa stok minus (merek, wadah, kemasan, kantong). Minus HARI INI karena catatan sesudahnya disebut di keterangan, bukan ✗ | hitung isinya di Stok › Cocokkan / Stok › Kantong |
| 6 · Utang & piutang | utang pemasok, utang toko ke owner, piutang pelanggan sebelum = sesudah ritual (baris yang sama dengan kelompok 1, tidak dihitung dua kali); bon per pelanggan, kasbon per orang, utang per pemasok saat tahun baru dibuka = catatan 31 Des (total sama tapi pindah orang tetap berbunyi) | cocokkan dengan catatan kertas; jangan menagih / memotong upah / bayar bon yang disebut dulu; jalan seperti kelompok 1 |

**Catatan yang masuk SESUDAH kunci** (karcis HP penjaga yang tertahan tanpa sinyal: bertanggal 2026, atau bertanggal hari ritual tapi ditulis sebelum kunci)
TIDAK ikut dibandingkan — bukan bagian ritual. Kartu menyebut jumlahnya ("… catatan masuk SESUDAH tutup buku 2026 dikunci … Itu bukan alasan
membatalkan") dan tetap boleh "Semua … sama"; yang bertanggal 2026 diurus pita catatan susulan ("sudah dicatat"). Nota yang ditulis SESUDAH jam kunci di
hari ritual tetap terhitung — jangan berjualan selama arsip berjalan.

**"Stok beras" beda karena kedatangan Januari yang dicatat SEBELUM kunci** (ritual tertunda: langkah 6 baru jalan sesudah toko menerima truk Januari).
Nilai stok dihitung dari rata-rata harga beli. Sebelum ritual rata-rata itu memakai seluruh pembelian tahun lalu, sesudahnya mulai dari saldo pembuka
31 Des — kedatangan Januari dirata-rata dengan dasar lain, jadi rupiah baris Stok beras beda walau kg beras dan uangnya tidak berubah. Kedatangan itu tetap
ada, jadi membatalkan lalu mengulang ritual akan beda LAGI. Kalau yang ✗ HANYA baris **Stok beras** (kartu: "1 pemeriksaan beda — jangan jualan/menagih
dulu"; pita: "1 baris TIDAK SAMA (Stok beras)") dan semua baris lain ✓ — termasuk kelompok 3 (buku beras per merek = catatan 31 Des) — itu BUKAN alasan
membatalkan: ketuk "selesai" dua kali (ketukan kedua menerima beda itu dan mencatatnya di berita acara) dan tulis tanggal kedatangannya di catatan kertas
tutup buku. Kartu tetap menyebut "1 pemeriksaan beda" sampai akhir Februari; untuk kasus ini itu bukan penghalang berjualan, menagih, atau kunci bulan Januari.
Ada baris lain yang ikut ✗ → jalan keluar biasa di bawah. Supaya tidak terjadi: kedatangan Januari dicatat SESUDAH pita "Tahun … terkunci dan arsipnya
habis" (barang boleh diturunkan, bon kertasnya disimpan dulu) — jangan sebelum kunci, jangan selama arsip berjalan.

**Jalan keluar (tanpa orang luar):**
- Berita acara **belum selesai** (pita "terkunci dan arsipnya habis"): JANGAN ketuk "selesai". Ketuk **batalkan** di pita (dua ketukan, dari perangkat yang
  memulai), tunggu sampai tuntas, ulangi ritual dari langkah 1 — kuotanya lihat "Kalau dibatalkan sesudah arsip" di langkah 1.
- Berita acara **sudah selesai**: beda kecil yang jelas sebabnya dibetulkan dengan catatan HARI INI (Stok › Cocokkan, catat bon / bayar bon yang terlupa).
  Beda besar → bab "Jalan mundur tutup buku" no. 3 (lewat Console).
- **"? belum bisa diperiksa"**: sambungkan internet, tunggu data selesai dimuat & antrean kosong (Menu › Toko ini › Perangkat & antrean › Antrean
  kirim), lalu buka Tutup buku lagi. Kalau sebabnya "titik kas sudah maju": angka "sebelum" di baris uang dicocokkan sendiri dengan hitungan tutup hari tanggal itu (Uang › Tutup hari › riwayat).
- Kartu menulis "Pemeriksaan tidak bisa dijalankan di perangkat ini": tutup lalu buka lagi aplikasinya sekali; kalau tetap, pegangannya pita tutup buku
  ("… semua baris sama") dan kedua berkas cadangan.

## Buntu Januari 2028 — DITUTUP oleh pintu tutup buku (rules v7, owner 7 Okt 2026)

Mulai 2027 kunci bulan berjalan (keputusan owner 1 Okt). Dulu, begitu SATU bulan 2027 dikunci, tutup buku 2027 sungguhan ditolak, sementara butir ⛔
"Tutup buku 2027 sudah selesai" (siap 2027 A2) menahan kunci bulan 2028 → buntu. Sejak rules v7 (K8, pengecualian sempit) ritualnya membuka **pintu tutup
buku** (`pengaturan/pintuBuku`, owner, ≤ 72 jam, hanya untuk TAHUN LALU dan hanya di atas berita acara tahun itu yang SUDAH tercatat berjalan / terkunci /
membatalkan): kiriman 1 = berita acara "berjalan" sendirian, pintu dibuka di kiriman 2. Selama terbuka server menerima saldo pembuka tahun itu (10 koleksi
yang memang punya saldo pembuka), arsip catatan bulan terkunci (salinannya ditulis di batch yang sama dan WAJIB sama persis dengan catatannya),
pengembalian arsip saat Batalkan (isi sama), dan titik kas 31 Des / titik sebelum tutup buku — catatan bulan terkunci lainnya tetap tidak bisa diubah.
Berita acara baru bisa "selesai" / "dibatalkan" hanya bersama pintu yang ditutup (aplikasi menutupnya di kiriman yang sama); berita acara yang selesai
tidak bisa dihapus, jadi pintu tahun itu tidak bisa dibuka lagi.

Yang perlu diingat saat ritual Januari 2028 (dan sesudahnya):
- **Rules v7 harus yang terbit** (Console › Rules, baris 2 `ATURAN FIRESTORE v7 FINAL`). Rules v3 (aturan darurat) dan v6 lama TIDAK punya pintu:
  di bawahnya tutup buku tahun berbulan terkunci ditolak di kiriman pertama (tidak ada yang tertulis) — tempel v7 lagi dulu.
- Arsip bulan terkunci = 5 access call per catatan (hapus 3 + salinan 2; tagihan Firestore menghitungnya sebagai baca) dan 3 catatan per kiriman — lebih
  lambat dan lebih banyak baca dari ritual 2026 (2 per catatan, 9 per kiriman). Perkiraan kuota di langkah 1 sudah menghitungnya; sejak Blaze (9 Okt
  2026) "TIDAK MUAT" boleh diabaikan — kelebihannya ditagih, arsip tidak berhenti karena kuota. Terhenti karena sebab lain → Lanjutkan (pintu dibuka lagi
  sendiri bila tinggal < 12 jam). Jangan berjualan sampai pita "… terkunci dan arsipnya habis".
- Batalkan juga lewat pintu (dibuka lagi di kiriman pembatalan pertama bila perlu). Pintu yang tertinggal terbuka (aplikasi tertutup di tengah) habis
  sendiri paling lama 72 jam sesudah dibuka.

## Hemat baca — MATI SELAMANYA (keputusan owner 9 Okt 2026, sesudah Blaze aktif)

Hemat baca dibangun 7 Okt (`docs/rancangan-hemat-baca.md`) karena paket Spark menolak baca lewat 50 rb sehari. Sejak 9 Okt 2026 proyek memakai **Blaze**
(baca lewat jatah gratis ditagih, tidak ditolak), dan owner memutuskan hemat baca **tidak pernah dinyalakan** — tugas lama "nyalakan ≤ 20 Nov", daftar
siap-nyala, dan perbandingan Usage harian GUGUR. Saklarnya bawaan MATI di tiap perangkat; dengan saklar mati aplikasi mendengarkan SEMUA catatan langsung
dari server (seperti sebelum 7 Okt), jadi ubahan lewat Console atau pemulihan dari berkas sampai sendiri ke semua perangkat — tidak ada tombol yang perlu
ditekan.

`firestore.rules` di repo tetap **v7** (terbit 7 Okt 2026 18.25 WIB: v6 + kirim ulang kasir@ bercap & batu nisan, permintaan nego staf, foto bon, kasir@
dipangkas, pintu tutup buku — `docs/uji-rules-v7.md`). Langkah 3 & 4 di atas memakai berkas itu (sidik dihitung dari repo saat itu) dan hanya empat kasus ★
Playground di langkah 4 (c). Yang tetap berlaku walau hemat baca mati:

- **Selama aturan darurat (v3) terpasang**, hapus dari `/baru/` yang membawa batu nisan DITOLAK server (v3 tidak mengenal `batuNisan`; batu nisan tetap
  ditulis selama v7 terpasang, saklar hemat baca tidak berpengaruh) — kirimannya pindah ke Menu › Toko ini › Perangkat & antrean › Antrean kirim, kartu
  "kiriman DITOLAK SERVER". Jangan menghapus apa pun di `/baru/` selama jendela darurat; jendelanya tetap sesingkat mungkin. Kirim ulang karcis kasir
  darurat kasir-v33 yang jawabannya hilang TIDAK ikut ditolak (tinjauan 7 Okt): `:commit` yang ditolak v3 dikirim sekali lagi dengan cara lama (PATCH,
  `updateMask` = kolom karcis — cap yang sudah ada dibiarkan), dan itu lolos `tulisUlangSama` v3. Kalau HP tetap menyebut karcis "ditolak" (versi lama),
  cocokkan dulu dengan Jual `/baru/` sebelum dicatat ulang.
- **JANGAN tempel `firestore.rules.v6`** sebagai "mundur" (lihat kepala `firestore.rules`): kode yang berjalan tetap mengecap tulisannya untuk v7.
- **Kalau satu perangkat ternyata menyala hemat bacanya** (panel Menu › Toko ini › Perangkat & antrean › Hemat baca menyebut "nyala"): ketuk
  "matikan hemat baca di perangkat ini", atau buka `/baru/?hemat=mati` di perangkat itu. Perangkat itu kembali membaca semua catatan tiap dibuka.
