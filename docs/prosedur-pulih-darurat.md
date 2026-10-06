# Prosedur pulih darurat — memulihkan data dari berkas cadangan (sesudah sistem lama pensiun, 3 Okt 2026)

**Kapan dipakai:** data di server hilang atau rusak, dan harus dikembalikan dari berkas cadangan (`backup-batch-miqbal-….json`). Ini jalan
**darurat**, bukan pekerjaan rutin.

> **3 Okt 2026 — sistem lama & `kasir.html` pensiun** (owner: "bumi hanguskan"). `index.html` dan `kasir.html` di situs kini hanya halaman pengalih
> ke `/baru/`. Satu-satunya pemulih dari berkas (`muatDariFile`, Setelan › Muat cadangan, mode PULIHKAN) ada di sistem lama — jadi sistem lama
> **dijalankan di komputer dari tag git**, tidak lagi dibuka dari situs. Versi terakhirnya utuh di tag **`sistem-lama-terakhir`** (commit `48a694d`).
> Sebelum 3 Okt prosedur ini membuka sistem lama dari situs dan memakai rules v4; sekarang rules yang terpasang = `firestore.rules` (v6).

## Kenapa perlu prosedur

- Sistem lama hanya-baca sejak 25b; satu-satunya jalan tulis catatan yang tetap terbuka di sana adalah **Setelan › Muat cadangan**, dan itu pun harus
  mengetik **PULIHKAN** dulu (keputusan owner 26 Sep 2026). `/baru/` belum punya pemulih dari berkas.
- Di bawah aturan server sekarang (`firestore.rules` v6), memulihkan **pasti ditolak** untuk semua catatan yang bertanggal di bulan terkunci. Kunci
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
- Sekali membuka sistem lama ≈ **7,4 rb baca** dokumen (kuota Spark 50 rb baca/hari, reset 15.00 WIB November–Maret, 14.00 WIB selebihnya). Jangan dimuat ulang berkali-kali.
- [BELUM TERVERIFIKASI] Apakah kunci API web Firebase dibatasi referrer/domain. Kalau ya, masuk dari `localhost` ditolak — periksa dulu di Console
  (Authentication › Settings › Authorized domains; Google Cloud › Credentials) sebelum jendela darurat dibuka.

## Langkah (owner yang menempel aturan; Claude hanya membaca dan memeriksa)

0. **Sebelum mulai**
   - Unduh cadangan keadaan sekarang (Menu › Sistem › Cadangan di `/baru/`), walaupun datanya sedang kacau — **dua kali cadangan**: sebelum dan sesudah.
   - Catat **jam mulai**.
   - Minta penjaga berhenti mencatat sebentar. Karcis kasir darurat tetap aman di antrean HP.
   - Siapkan dua berkas aturan dari repo: `firestore.rules.v3` (darurat) dan `firestore.rules` (yang berlaku, v6).
     Salin tanpa merusak huruf: `git show origin/main:firestore.rules.v3 | LANG=en_US.UTF-8 pbcopy`.
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
1. **Pasang aturan darurat.** Console › Firestore › Rules → tempel isi `firestore.rules.v3` → **Publish**. Catat jam. Sidik v3 yang benar:
   SHA-256 berawalan `32c55d58`.
2. **Pulihkan.**
   - Di folder sistem lama: `python3 -m http.server 8731 --bind 127.0.0.1` → buka `http://localhost:8731/index.html`, masuk dengan akun owner.
     Simpanan lokal peramban untuk alamat `localhost` kosong — itu wajar.
   - Gerbang "Sistem utama khusus owner" → tombol **Owner** → ketik PIN owner (lihat langkah 0). Seluruh sistem lama, termasuk Setelan › Muat
     cadangan, ada di balik gerbang ini.
   - Setelan › Muat cadangan → pilih berkas → ketik **PULIHKAN** → tunggu kalimat "Berhasil diunggah …".
   - Sistem lama hanya **menambah** catatan yang id-nya belum ada. Tidak menimpa, tidak menghapus.
   - Berkas dari era tutup buku yang lain ditolak sendiri (penjaga era).
   - Sesudahnya: tutup tab, **matikan server** (Ctrl-C), hapus folder (`git worktree remove /tmp/sistem-lama` atau `rm -rf /tmp/sistem-lama`).
3. **Kembalikan `firestore.rules` SEGERA.** Tempel isi `firestore.rules` → **Publish**. Cocokkan isi editor dengan repo: SHA-256 dihitung dari repo
   SAAT ITU (`shasum -a 256 firestore.rules`; per 3 Okt 2026 = v6, berawalan `4289d24c`). Catat jam. Jendela darurat = jam langkah 1 sampai jam
   langkah 3.
4. **Jalankan ulang ★ aturan yang berlaku.** Pakai `docs/uji-rules-v6.md` (tanpa dokumen kunci uji), lalu satu karcis dari kasir darurat. Kalau ada ★
   yang tidak sesuai: tempel lagi `firestore.rules` dari repo, jangan dibiarkan.
5. **Periksa & catat.**
   - Unduh cadangan kedua (sesudah).
   - Di `/baru/`: daftar periksa kunci bulan, dan angka bulan terkunci (laba, neraca) — bandingkan dengan sebelum kejadian.
   - Tulis kejadiannya di `docs/peta-kunci-periode.md`: tanggal, jam buka dan tutup jendela darurat, alasan, berkas cadangan yang dipakai, dan siapa
     yang menempel aturan.

## Yang tidak boleh

- Membiarkan aturan darurat terpasang melewati hari itu.
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
- **Kuota:** pembatalan sesudah arsip penuh butuh ± sebesar ritualnya lagi — angkanya tampil di langkah 1 ("Kalau dibatalkan sesudah arsip"). Di Spark
  itu tidak muat di hari yang sama dengan ritualnya: toko tidak buka sampai pembatalan tuntas sesudah reset kuota berikutnya.
- Catatan bertanggal tahun lama yang mendarat SESUDAH penanda (karcis HP penjaga yang tertahan tanpa sinyal) tidak ikut diarsip; pita menyebutnya dan
  jalannya ("sudah dicatat" — catatannya tidak dihapus). Itu bukan alasan membatalkan. Kalimatnya per jenis: nota (uang di laci LEBIH, omzet tahun itu
  kurang), pengeluaran (uang KURANG, biaya tahun itu kurang → labanya terlihat lebih besar), catatan lain (selisih uang muncul di tutup hari berikutnya).
- **Pesanan** bertanggal Desember yang belum tuntas saat ritual memang TIDAK diarsip (masih berjalan). Dicatat di hasil periksa saat arsip habis dan
  di berita acara saat selesai (`tertinggal`); kalau dibayar / dibatalkan di Januari, ia **bukan** catatan susulan — pesanan bukan uang & bukan stok,
  notanya bertanggal hari bayar.

### 3. Sesudah "selesai"

- Tidak ada tombol, dan aturan server (v6) menolak berita acara `selesai` diubah dari aplikasi. **Anggap tahun itu final:** kesalahan yang ketahuan
  belakangan dibetulkan dengan catatan HARI INI (Stok › Cocokkan, bayar bon, catat bon yang terlupa) — bukan dengan membuka tahun lama.
- Jalan pulang darurat (keputusan owner; belum pernah diuji di server; Claude hanya membaca & memeriksa):
  1. Unduh cadangan keadaan sekarang — dua kali (sebelum & sesudah).
  2. Lewat Console, hapus saldo pembuka tahun itu: dokumen ber-`tutupBuku: true` dan `tahunDari: <tahun>` di `batchMasuk` (batch `penandaBuku`
     PERTAMA), `piutangMutasi`, `kasbonMutasi`, `produksiKemasan`, `stokBahanKemasan`, `stokBahanLiteran`, `utangPemasokMutasi`, `utangOwnerMutasi`,
     `amplopLaba`, `modalOwner` (daftar = `CACHE_PEMBUKA` di `baru/js/data/toko.js`). Sesudah itu era mundur.
  3. Kembalikan catatan tahun itu: tiap dokumen `arsipTahun` bertahun itu → tulis `dok` ke koleksi `koleksi` dengan id `idAsli`, lalu hapus salinan
     arsipnya. **Belum ada alat** untuk ribuan dokumen; alternatifnya pemulih berkas (bab di atas) dengan cadangan SEBELUM — baru diterima sesudah
     langkah 2, dan hanya 27 koleksi lama yang pulih.
  4. Lewat Console: `pengaturan/tutupBuku` (`tahunDitutup` = tahun sebelumnya) dan berita acara (`status: 'dibatalkan'`). Titik kas: tulis ulang dari
     hitungan laci terakhir.
  5. Cocokkan 14 baris (Uang › Tutup buku, latihan) dengan berita acara lama, lalu catat kejadiannya di `docs/peta-kunci-periode.md`.
- Bulan yang sudah dikunci tidak bisa ditulis siapa pun. Kunci Januari tahun baru baru boleh **sesudah** tutup buku selesai (daftar periksa kunci bulan
  menolak sendiri) — jadi kalau jalan pulang ini dipakai, jalankan SEBELUM ada bulan tahun baru yang dikunci.

## Daftar periksa ritual tutup buku 2026 (1 Jan 2027)

**Sampai 31 Des (owner):**
- [ ] Tutup hari setiap malam sampai 31 Des. Tutup hari 31 Des = tulisan TERAKHIR bertanggal 2026.
- [ ] Hari berjualan tanpa tutup hari: Uang › Tutup buku › langkah 1 → tiap tanggal "tidak ditutup — diterima apa adanya" + alasan (min. 5 huruf),
      **Simpan putusan** (tersimpan sungguhan, juga dari latihan; ikut berita acara). Tutup hari tidak dibuat mundur.
- [ ] Tidak ada buku beras / kemasan / kantong yang minus, tidak ada kelebihan bayar pelanggan, bayar lebih ke pemasok / owner, atau kasbon dibayar
      lebih (langkah 1, butir g6 menyebut buku/namanya dan jalannya: opname di Stok › Cocokkan, catat bon / kedatangan / kasbon yang terlupa).
- [ ] Semua karcis kasir darurat dirinci; nama kembar disatukan; piutang lama diputuskan.
- [ ] Upah karyawan dibayar & dicatat sampai 31 Des bila bisa. Yang belum dibayar tercatat di berita acara (baris "Upah karyawan yang belum dibayar");
      kalau dibayar Januari, biayanya masuk Januari (bukan 2026).
- [ ] (Cadangan kertas, disarankan) Laporan › Pajak › Rekap pajak untuk konsultan 2026 + Laporan › Tahunan 2026 → simpan PDF. Sejak Paket B (Okt 2026)
      layar Pajak, Laporan & Dasbor membaca tahun yang sudah ditutup dari **potret** di berita acara (lihat "Sesudahnya"); PDF ini pegangan kalau potretnya
      kelak tidak terbaca.
- [ ] LATIHAN sekali (16–30 Des). Layar selalu membuka di LATIHAN. Langkah 6 (Kunci) latihan menyusun **potret 2026** tanpa menulis apa pun dan
      menyebut hasilnya ("Potret 2026: 12 bulan & … hari berjualan · omzet sistem … · laba bersih … · neraca 31 Des …"). "Potret 2026 GAGAL" = kunci
      sungguhan akan DITOLAK sampai dibetulkan — kirim tangkapan layarnya.
- [ ] 31 Des malam: Menu › Sistem › Perangkat — tiap perangkat antrean 0 dan ditolak 0; HP penjaga lalu dimatikan.

**1 Jan 2027 (Jumat, toko tutup), sesudah 15.00 WIB:**
- [ ] Kuota Spark harian kembali penuh pukul **15.00 WIB** (tengah malam waktu Pasifik; 15.00 WIB dari Senin sesudah Minggu pertama November sampai
      Minggu kedua Maret, selain itu 14.00 WIB — layar menghitungnya dari zona America/Los_Angeles, juga di hari pergantian). Console › Firestore ›
      Usage: kuota hari itu belum terpakai.
- [ ] Mac, tab peramban (bukan web app iPhone/iPad), SATU perangkat, jangan muat ulang aplikasi.
- [ ] Uang › Tutup buku › **SUNGGUHAN** → langkah 1: g1–g6 semua ✓. Baca kartu **Perkiraan kuota Firestore**: "TIDAK MUAT" = jangan mulai hari itu;
      "MEPET" = mulai hanya kalau toko tutup.
- [ ] Langkah 2: cadangan SEBELUM → cek berkasnya ada di Unduhan, salin ke luar Mac.
- [ ] Langkah 3: arsip → cek berkasnya ada.
- [ ] Langkah 4: saldo pembuka → semua 14 baris ✓ (12 baris harta & utang + modal owner + upah belum dibayar).
- [ ] Langkah 5: paraf owner + saksi. Langkah 6: kunci (dua ketukan) → tunggu kiriman & arsip habis. Terhenti → Lanjutkan dari perangkat yang sama.
- [ ] Pita "terkunci dan arsipnya habis … semua baris sama" → cocokkan utang pemasok & utang toko ke owner dengan catatan kertas.
- [ ] Pita catatan susulan ("… masuk SESUDAH tutup buku …") → ikuti jalannya, ketuk "sudah dicatat".
- [ ] Langkah 7: cadangan SESUDAH & selesai. Salin cadangan SEBELUM, berkas arsip, dan cadangan SESUDAH ke ≥ 2 tempat di luar Mac (simpan 10 tahun).

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
      perlu membuka kredit per nota sampai April.
- [ ] Kunci bulan Januari 2027 paling cepat 4 Feb, HANYA sesudah tutup buku 2026 "selesai" (daftar periksa kunci bulan menolak sendiri, Beranda
      tidak menyuruh mengunci selama itu).
- Saldo pembuka **modal owner** bertanggal 31 Des 00.00 (`modalOwner`, `tutupBuku: true`) membawa JUMLAH modal yang tertanam — bukan setoran atau
  penarikan. Ambil pribadi Desember, buku Owner & toko ("Modal owner dibawa dari tahun lalu"), bukti setoran, dan buku kas harian 31 Des tidak
  menghitungnya sebagai gerakan uang. Laporan arus kas mesin (Desember / 31 Des tahun yang sudah ditutup) masih menyebutnya "Modal owner disetor/
  ditarik — Saldo pembuka…": itu **bukan** uang yang bergerak; angka tahun yang ditutup dibaca dari berita acara sampai layar Laporan & Pajak bisa
  membaca tahun yang ditutup (paket B).

## Buntu Januari 2028 — dicatat, BELUM dibangun (7 Okt 2026)

Mulai 2027 kunci bulan berjalan (keputusan owner 1 Okt). Begitu SATU bulan 2027 dikunci, tutup buku 2027 sungguhan ditolak (`tahunBuku`: tahun yang
punya bulan terkunci — arsipnya memindah catatan bulan terkunci, saldo pembuka piutang bertanggal utang tertua). Di saat yang sama butir ⛔
"Tutup buku 2027 sudah selesai" (siap 2027 A2) menahan kunci bulan 2028 mana pun dan menyuruh menyelesaikan tutup buku di Uang › Tutup buku — yang
justru mustahil. Akibatnya Januari 2028: tutup buku 2027 tidak bisa jalan, kunci bulan 2028 tidak bisa jalan.

Penutupnya = **paket tutup buku 2027** (keputusan owner: pengecualian sempit; bentuknya dirancang di paket itu — bandingkan pilihan C/D di
`docs/peta-kunci-periode.md`), harus siap **sebelum ritual 1 Jan 2028**. Sampai paket itu ada, butir itu di Januari 2028 memang belum punya jalan
keluar dari layar.
