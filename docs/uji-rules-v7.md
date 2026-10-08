# Uji rules v7 FINAL di server — terbit SEKALI (TERBIT 7 Okt 2026 18.25 WIB)

`alat-uji/periksa_rules.py` memeriksa **bentuk** rules di CI: v7 = `firestore.rules.v6` + PERSIS lima ubahan di bawah (dibandingkan tanpa komentar &
spasi, blok demi blok), dan sejak v7 juga **menilai teks rules** dengan penafsir mini (`alat-uji/rules_mini.py`) pada SEMUA kasus ★ di berkas ini, dengan
dokumen uji yang sama — kolom "Wajib" di tabel sudah lulus model di CI. `alat-uji/uji_tutup_buku_2027.py` menjalankan ritual tutup buku 2027 sungguhan
di kotak pasir dan menilai TIAP batch-nya dengan teks rules yang sama. Model bukan server: sejak 7 Okt **semua** kasus di berkas ini juga dijalankan di
**Firebase Emulator** — mesin rules yang sama dengan server produksi — dan lulus (bagian "Bukti emulator" di bawah). Kasus yang dijalankan owner di **Rules
Playground** (Console › Firestore › Rules, v7 di EDITOR, **sebelum** Publish) menilai teks itu atas data proyek toko, tetapi Playground punya sifat sendiri
yang BUKAN sifat server (isian *update* digabung ke dokumen lama; teks jam ISO `…Z` diubah jadi *timestamp*, di isian maupun di dokumen yang dibaca) — kasus
yang tidak bisa dinilai jujur di sana tidak masuk "Wajib owner" (lihat bagian T). Claude Code tidak memegang sandi dan tidak mengetik apa pun di Console;
Claude hanya MEMBACA Console lewat Chrome owner pada langkah yang disebut. Rules = TUGAS OWNER. Kasus v6 tetap di `docs/uji-rules-v6.md`.

## Yang berubah v6 → v7 (lima)

1. **Hemat baca** (cabang `perbaikan/hemat-baca`): fungsi `ulangKasirBercap()` + satu suku di `allow update` penjualan — kirim ulang karcis kasir darurat
   `kasir-v33` (REST `:commit`, `capServer = REQUEST_TIME`) isinya sama kecuali `capServer`, dan `capServer` itu jam server ATAU tidak ada (HP yang masih
   `kasir-v32` mengirim ulang nota yang sudah disentuh perangkat owner). Blok `batuNisan`: baca & hapus owner; buat/ubah owner dan `capServer == request.time`.
2. **Permintaan nego staf** (PR #109, JS2-C): `persetujuan` — ben/karyawan aktif boleh **membuat** permintaan nego (`tindakan 'nego'`, `status
   'menunggu'`, `negoUid` = `olehUid` = uid sendiri, tanpa `diputusPada` / `diputusTanggal` / `diputusJam` / `alasanTolak`) dan **membaca** koleksi
   persetujuan (keputusan owner). Memutus (ubah) & hapus = owner. Tombol MINTA OWNER di Jual hidup sesudah cabang ini digabung.
3. **Foto bon** (paket E-2): blok `fotoBon` — owner baca / buat / hapus, **tanpa ubah**; bentuk dibatasi: `id` isi = id dokumen, `idBon` teks, `jenis`
   gambar (jpeg / png / webp), `base64` ≤ 960.000 huruf (± 700 KB foto).
4. **kasir@ dipangkas** (kasir.html pensiun 3 Okt): kasir darurat hanya memakai nota `penjualan` (+ kirim ulangnya), denyut `perangkatStatus`, dan katalog
   `ringkasanKasir/aktif`. DICABUT: create & tulis-ulang `piutangMutasi` / `stokBahanLiteran`, create `logAktivitas`, baca `pengaturan/aksesKasir`
   (`pengaturan/keamanan` memang owner saja sejak v3). Diperiksa dari kodenya: `kasir-darurat-nominal.html` hanya memanggil auth, `perangkatStatus`,
   `penjualan`, dan `ringkasanKasir/aktif`.
5. **Pintu tutup buku** (keputusan owner 7 Okt, K8 "pengecualian sempit"; dipersempit sesudah sanggahan rules 7 Okt): tanpa ini, begitu satu bulan
   2027 dikunci, tutup buku 2027 mustahil (rules menolak tulis/hapus bulan terkunci) dan butir A2 menahan kunci 2028 → buntu Januari 2028. Dokumen
   `pengaturan/pintuBuku` = `{ tahun: Y, status: 'berjalan', sampai: <timestamp> }` dibuat **owner** hanya bila:
   - `Y` = **tahun lalu** dan `sampai` ≤ jam server + **72 jam**;
   - berita acara `tutupBukuAcara/Y` **sudah ada sebelum** kiriman itu (server membaca keadaan SEBELUM kiriman — berita acara dan pintu tidak bisa
     dikarang dalam satu kiriman), berstatus berjalan / terkunci / membatalkan, dan percobaannya dimulai sesudah 31 Desember Y.

   Berita acara baru wajib berbentuk tutup buku sungguhan (id = tahun, tahun lampau, `mode: 'sungguhan'`, berjalan / terkunci) dengan jam mulai
   (`paraf.pada`) = tanggal server ± 1 hari. Berita acara hanya bisa dihapus bila `dibatalkan` (yang `selesai` tidak bisa dihapus lalu dibuat lagi),
   dan baru boleh jadi `selesai` / `dibatalkan` bila pintu tahun itu **tertutup** sesudah kiriman itu (aplikasi menutupnya di kiriman yang sama) — jadi
   pintu tidak pernah terbuka untuk berita acara yang sudah selesai. Selama pintu terbuka & belum lewat `sampai`, owner boleh — hanya untuk catatan
   bertanggal ≤ Desember Y di bulan terkunci:
   - **menghapus** catatan yang salinannya di `arsipTahun/'Y|koleksi|id'` sesudah kiriman itu **sama persis** dengan catatan yang dihapus (arsip =
     pindah, bukan buang; salinan sampah / berisi lain = ditolak), atau saldo pembuka tahun Y (tarik saat Batalkan);
   - **membuat** saldo pembuka tahun Y (`tutupBuku: true`, `tahunDari: Y`) — hanya di 10 koleksi yang memang punya saldo pembuka (kedatangan, piutang,
     kasbon, produksi, bahan kemasan, bahan literan, bon pemasok, utang ke owner, amplop laba, modal owner); nota, retur, uang keluar dll. bertanda
     `tutupBuku` tetap ditolak — atau **mengembalikan** catatan dari arsip Y yang isinya SAMA dengan salinannya (Batalkan);
   - **titik kas** `pengaturan/titikKas` bertanggal **31 Des Y**, atau **persis** `titikSebelum` di berita acara Y (pengembaliannya saat Batalkan).

   **Salinan arsip terikat ke aslinya**: `arsipTahun` hanya menerima bentuk `'Y|koleksi|id'` untuk koleksi yang diarsip tutup buku, dan salinan catatan
   bulan terkunci wajib = catatan aslinya (arsip karangan tidak bisa dipakai untuk "mengembalikan" catatan baru). **Tidak ada pintu** untuk UBAH catatan
   apa pun, untuk catatan bulan terkunci lainnya, untuk `pindahUang` / `slipUpah` (tidak diarsip), untuk kasir@ / staf. Status `'tutup'` boleh kapan
   saja. Access call (cache tidak diandalkan): saldo pembuka & titik 31 Des 2, titik kembali 3, hapus arsip & kembalikan 3, salinan arsip 1–2, buka pintu
   1, berita acara selesai / dibatalkan 1 — aplikasi memecah kiriman ≤ 18.

**Sejarah 7 Okt — urutan ini sudah dijalankan** (v7 terbit 18.25 WIB, PR #111 digabung 21.25 WIB). **Aman diterbitkan SEBELUM cabang digabung**: kode
yang tayang (main) waktu itu tidak memakai kelima hal itu — kasir darurat tetap jalan (nota, denyut, katalog), permintaan nego staf belum dikirim (tombolnya
masih mati), foto bon & pintu belum ditulis siapa pun. Urutannya tetap: **v7 terbit dulu, baru PR #111 digabung** (owner bilang "merge").

**Mundur**: JANGAN tempel `firestore.rules.v6` selama kode cabang ini berjalan (hapus /baru/ ber-batu nisan, permintaan nego staf, foto bon, dan tutup buku
2027 ditolak). Mundur hemat baca = saklar (Menu › Toko ini › Perangkat & antrean › Hemat baca, atau `/baru/?hemat=mati`). v6 baru boleh ditempel balik
SESUDAH cabang dibalik (git revert) dan HP kasir kembali ke kasir-v32 — **sesudah 13 Okt itu bukan jalan owner** (tidak ada yang membalik cabang);
mundur yang tersedia untuk owner = saklar hemat baca di atas.

## Kalau kiriman tutup buku DITOLAK server (berlaku sejak v7 terbit)

Kabar layar Uang › Tutup buku menyebut kiriman ke-n "tulis ditolak: permission-denied", dan salinannya ada di Menu › Toko ini › Perangkat & antrean ›
Antrean kirim (ditolak server). **Jangan tulis ulang kiriman tutup buku yang ditolak**, jangan ketuk berulang-ulang, dan **jangan tempel rules lain**
(bagian "Mundur" di atas). Sejak 13 Okt 2026 owner mengerjakannya sendiri:
1. Catat kalimat kabarnya (foto layar untuk arsip sendiri). Penyebab yang diharapkan = kiriman yang memang telat (perangkat lain / percobaan lama — penjaga
   "hanya maju" berita acara, `docs/uji-rules-v6.md` bagian A/B, ikut di v7): pita tutup buku tetap benar, ikuti pitanya (Lanjutkan / Batalkan dari
   perangkat pemegang).
2. Penyebab lain yang bisa dibereskan sendiri: **jam perangkat**. v7 menilai jam mulai berita acara baru (tanggal server ± 1 hari) dan pintu tutup buku
   (≤ 72 jam dari jam server) dengan jam SERVER. Setel jam otomatis (Setelan › Umum › Tanggal & Waktu → "Setel otomatis" di iPhone/iPad; Pengaturan
   Sistem › Umum › Tanggal & Waktu di Mac), lalu ketuk Lanjutkan sekali (Lanjutkan membuka pintu lagi bila sudah kedaluwarsa). Tetap ditolak →
   **Batalkan** dari perangkat pemegang, tunggu tuntas, coba lagi besok sesudah reset kuota.

Langkah ini dulu hanya tertulis di `docs/uji-rules-v6.md` (berkas sejarah); langkah 3 di sana (tempel `firestore.rules.v5`) DICABUT.

---

## Urutan (satu kali duduk ± 35 menit, saat toko tutup; jangan klik **Publish** sebelum langkah 5)

> **SEJARAH — dijalankan 7 Okt 2026, jangan diulang.** v7 TERBIT 18.25 WIB (bagian "Hasil Playground"). Urutan di bawah menyerahkan beberapa
> pekerjaan ke Claude ("kirim ke Claude", "Claude membaca") karena waktu itu masih ada pembantu kode; sesudah 13 Okt tidak ada. Untuk memeriksa atau
> memulihkan rules yang terbit, JANGAN membuat dokumen uji U1–U11 di data toko dan jangan mengulang urutan ini — pakai `docs/prosedur-pulih-darurat.md`.

1. **Persiapan** — v6 masih yang terbit. Cek Console › Firestore › **Usage** dulu (Playground ikut kuota baca Spark; kerjakan sesudah 14.00 WIB bila kuota
   hari itu menipis). **Sebelum membuat apa pun, buka Console › Firestore › Data › `aturanToko` dan lihat apakah dokumen `kunciPeriode` SUDAH ADA.**
   Sudah ada (berarti kunci bulan sungguhan) → **BERHENTI**: jangan buat U2, jangan hapus dokumen itu, kirim tangkapan layarnya ke Claude (dokumen kunci
   tidak pernah dihapus lewat Console — `docs/prosedur-pulih-darurat.md`; kunci sungguhan juga sudah mengunci tahun 2021, jadi dokumen uji perlu disusun
   ulang). Sampai rules v7 terbit aplikasi belum mengunci bulan apa pun (kunci pertama Januari 2027), jadi biasanya dokumen itu belum ada. Belum ada →
   Console › Firestore › **Data** (Console menulis sebagai admin, rules tidak menilai): buat **sepuluh dokumen uji U1–U10** di tabel "Dokumen uji" (U11
   hanya kalau mau menjalankan kasus staf yang opsional). Selama dokumen uji ada, aplikasi bisa menampilkan hal aneh (kunci "sampai Desember 2021", pita
   "Tutup buku 2025", nota contoh bertanggal 2021) — **jangan ketuk apa pun di aplikasi**, selesaikan langkah 1–4 dalam satu duduk.
2. **Tempel `firestore.rules`** dari cabang ke editor Rules — **belum Publish**. Salin-tempel berkasnya utuh, salah satu cara:
   - Mac (Terminal): `git fetch origin && git show origin/perbaikan/hemat-baca:firestore.rules | LANG=en_US.UTF-8 pbcopy` (sesudah merge: `origin/main`),
     lalu di editor: pilih semua (⌘A) → tempel (⌘V);
   - GitHub: buka berkas `firestore.rules` di cabang `perbaikan/hemat-baca` → **Raw** → pilih semua → salin → tempel di editor.

   Periksa di editor: baris 2 berbunyi `ATURAN FIRESTORE v7 FINAL`, ada fungsi `pintuSah`, `arsipSah`, `acaraBaru`, `stafMintaNego`, dan blok `match
   /fotoBon/{id}`. Editor yang menolak menyimpan (garis merah) = berhenti, kirim tangkapan layar ke Claude.
3. Jalankan **17 kasus "Wajib owner"** di Playground, berurutan (nomor 17 PALING AKHIR — ia mengubah dokumen uji U5). Semua hasil harus sama dengan
   kolom "Wajib". Ada yang beda → **jangan Publish**, kirim tangkapan layar ke Claude. Ke-17 kasus itu (dan semua opsional) **sudah lulus di emulator**
   (bagian "Bukti emulator") dan dipilih yang hasilnya di Playground tidak terpengaruh sifat Playground; Playground menilainya atas data proyek toko dengan
   teks yang akan diterbitkan, jadi langkah ini TETAP dikerjakan. Bagian "Opsional" boleh dilewati — semuanya sudah dinilai model di CI
   (`alat-uji/periksa_rules.py`) dan dijalankan di emulator; jalankan kalau sempat.
4. **Owner menghapus dokumen uji** U1–U10 (dan U11 bila dibuat) di tab Data (Claude tidak boleh menghapus data). **`aturanToko/kunciPeriode` (U2 yang
   dibuat di langkah 1 — bukan kunci sungguhan; langkah 1 berhenti kalau kunci sungguhan sudah ada) WAJIB hilang**: kalau tertinggal, bulan sampai
   Desember 2021 terkunci dan kunci bulan pertama Januari 2027 DITOLAK — dan di bawah rules dokumen itu tidak bisa dihapus dari aplikasi, hanya dari
   Console. `tutupBukuAcara/2021` & `tutupBukuAcara/2025` juga wajib hilang (berita acara yang tidak dibatalkan
   tidak bisa dihapus dari aplikasi). Bilang ke Claude "dokumen uji sudah dihapus" → Claude membuka Console › Firestore › Data lewat Chrome owner (hanya
   membaca) dan memastikan semuanya **tidak ada** (tanpa Claude: owner memeriksa sendiri daftar yang sama).
5. **Publish** (owner). Isi editor harus persis `firestore.rules` di repo. Lalu Console › Rules menampilkan versi aktif — baris 2 `ATURAN FIRESTORE v7
   FINAL` (Claude membaca lewat Chrome owner, atau owner melihatnya sendiri).
6. **Sesudah terbit**: satu nota dari kasir darurat (HP penjaga, MASIH versi lama) → pastikan masuk di layar Jual `/baru/`. Tidak masuk → tempel
   `firestore.rules.v6` (kode cabang belum digabung, jadi masih aman) dan kabari Claude. **Hanya berlaku 7 Okt sebelum merge; sesudah #111
   digabung v6 TIDAK BOLEH ditempel** (bagian "Mundur" di atas).
7. Baru sesudah itu **PR #111 digabung** (owner bilang "merge"; Pages hijau). HP penjaga dibuka sekali sampai bilah atas berbunyi **"versi 7 Okt"**
   (kasir-v33). Langkah sesudahnya (hemat baca, foto bon, nego staf): lihat isi PR #111.

### Isian Playground

*Authenticated* on, provider password. **Firebase UID** & **Auth token payload** (`"email"`, huruf kecil) per akun:

| Akun | Firebase UID | email di payload |
|---|---|---|
| owner@ | `uid-uji` | `owner@tokoberasmiqbal.web.app` |
| kasir@ | `uid-kasir-uji` | `kasir@tokoberasmiqbal.web.app` |
| staf uji (opsional, butuh U11) | `uid-uji-b` | `uji.b@contoh.com` |
| akun tanpa aksesAkun | `baru1` | `uji.baru1@contoh.com` |

Belum ada akun karyawan sungguhan, jadi kasus staf memakai akun UJI: dokumen U11 `aksesAkun/uid-uji-b` (dibuat sementara, dihapus lagi di langkah 4).
UID `uid-uji-b` bukan akun Firebase Authentication siapa pun — tidak ada yang bisa masuk dengannya. Kasus staf semuanya **opsional** (sudah dinilai model
CI); tanpa U11 kasus staf yang "LOLOS" akan keluar DITOLAK — itu wajar, bukan cacat rules.

"Error running simulation … Null value error" = **DITOLAK** di server (bukan lolos). Playground tidak mengubah apa pun di database.

**Cara Playground menilai *update* (terbukti 25 Sep)**: isian *Build document* DIGABUNG ke dokumen yang sudah ada — kolom yang diisi saja yang berubah;
kolom tidak bisa DIBUANG. Untuk kasus update, isi hanya kolom yang disebut. *Create* memakai isian apa adanya. Map (mis. `paraf`, `dok`) diisi sebagai
jenis **map** dengan kolom di dalamnya.

### Dokumen uji (tab Data; HAPUS lagi di langkah 4)

Tahun **2021** sengaja: tidak ada catatan toko bertanggal ≤ 2021, jadi kunci uji `2021-12` tidak mengunci catatan sungguhan. **2025** = "tahun lalu"
(pintu hanya untuk tahun lalu) — kalau Playground dijalankan sesudah 1 Januari 2027, ganti 2025 dengan 2026 di U4 dan ★P6 (`paraf.pada` U4 = hari ini,
tetap berlaku). `paraf.pada` U3/U4 sengaja teks jam **bukan** ISO (`2026-10-01 00:00`, bukan `…T00:00:00.000Z`): Playground mengubah teks ISO menjadi
*timestamp* juga di dokumen yang dibaca `get()`, lalu perbandingan `timestamp ≥ teks` di `pintuSah` galat = DITOLAK palsu. Rules membandingkan teks, dan
urutan teks ini tetap sesudah `<tahun>-12-31T17:00:00.000Z`; bentuk ISO yang ditulis aplikasi dinilai M-P6b (model & emulator) dan gladi pintu.

| No | Jalur | Isi (jenis kolom) |
|---|---|---|
| U1 | `penjualan/uji-v7-nota` | `id` "uji-v7-nota" · `tanggal` "<hari ini YYYY-MM-DD>" · `hargaTotal` 1000 (number) · `namaProduk` "Contoh" |
| U2 | `aturanToko/kunciPeriode` | `sampaiBulan` "2021-12" · `riwayat` (array) kosong — **WAJIB dihapus lagi** |
| U3 | `tutupBukuAcara/2021` | `tahun` 2021 (number) · `status` "terkunci" · `paraf` (map) { `pada` "2026-10-01 00:00" } · `titikSebelum` (map) { `tanggal` "2021-06-30", `laci` 7, `brankas` 0 } |
| U4 | `tutupBukuAcara/2025` | `tahun` 2025 (number) · `mode` "sungguhan" · `status` "berjalan" · `paraf` (map) { `pada` "<hari ini YYYY-MM-DD> 00:00" } (mis. "2026-10-10 00:00") |
| U5 | `pengaturan/pintuBuku` | `id` "pintuBuku" · `tahun` 2021 (number) · `status` "berjalan" · `sampai` (timestamp) 1 Jan 2100 00:00 |
| U6 | `penjualan/uji-v7-lama` | `id` "uji-v7-lama" · `tanggal` "2021-06-15" · `hargaTotal` 1000 |
| U7 | `arsipTahun/2021\|penjualan\|uji-v7-lama` | `id` "2021\|penjualan\|uji-v7-lama" · `tahun` 2021 · `koleksi` "penjualan" · `idAsli` "uji-v7-lama" · `dok` (map) = isi U6 persis |
| U8 | `penjualan/uji-v7-beda` | `id` "uji-v7-beda" · `tanggal` "2021-06-16" · `hargaTotal` 1000 |
| U9 | `arsipTahun/2021\|penjualan\|uji-v7-beda` | `id` "2021\|penjualan\|uji-v7-beda" · `tahun` 2021 · `koleksi` "penjualan" · `idAsli` "uji-v7-beda" · `dok` (map) = isi U8 TETAPI `hargaTotal` **900** |
| U10 | `arsipTahun/2021\|penjualan\|uji-v7-pulih` | `id` "2021\|penjualan\|uji-v7-pulih" · `tahun` 2021 · `koleksi` "penjualan" · `idAsli` "uji-v7-pulih" · `dok` (map) `{ id "uji-v7-pulih", tanggal "2021-03-01", hargaTotal 500 }` |
| U11 | `aksesAkun/uid-uji-b` (opsional — kasus staf) | `uid` "uid-uji-b" · `nama` "UJI B" · `email` "uji.b@contoh.com" · `peran` "ben" · `aktif` true (boolean) |

Garis tegak di jalur arsip memang bagian id dokumen (`2021|penjualan|uji-v7-lama`); di tabel ditulis `\|` hanya karena format tabel. ★P5 memakai
dokumen NYATA `pengaturan/titikKas` tanpa mengubahnya (Playground tidak menulis) — dokumen itu BUKAN dokumen uji, JANGAN dihapus.

## Wajib owner (17 kasus — berurutan, nomor 17 paling akhir)

> **Catatan sesudah 7 Okt** (daftar & urutannya sengaja tidak diubah — `alat-uji/periksa_rules.py` & `alat-uji/uji_rules_emulator.py` membacanya):
> di Playground hanya #1–5, 8, 9 yang bisa dinilai (#2 pun tanpa bisa membedakan sebabnya); #6, 7, 10–17 **tidak bisa dinilai** (`getAfter` tidak
> didukung / *timestamp* ketikan bukan *timestamp* — bagian "Hasil Playground", batas a & b). Buktinya emulator (bagian "Bukti emulator").

Isi "PINTU": `{ id: "pintuBuku", tahun: 2025, status: "berjalan", sampai: <timestamp BESOK jam yang sama> }` (pilih tanggal besok di pemilih tanggal
*timestamp*). Isi "PEMBUKA": `{ id: "uji-v7-pb-baru", tipe: "saldoAwal", tutupBuku: true, tahunDari: 2021, tanggal: "2021-03-01", nominal: 1000 }`.

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★A1 | kasir@ | create `penjualan/uji-v7-baru` | `{ id: "uji-v7-baru", tanggal: <hari ini>, hargaTotal: 1000, namaProduk: "Contoh" }` | LOLOS | nota HP kasir tetap masuk |
| 2 | ★B2 | kasir@ | update `penjualan/uji-v7-nota` | `capServer` = timestamp **ketikan** | DITOLAK | cap dari jam HP tidak diterima |
| 3 | ★K3 | kasir@ | create `piutangMutasi/uji-v7-k` | `{ id: "uji-v7-k", tipe: "bayar", tanggal: <hari ini>, nominal: 1000 }` | DITOLAK | jalur kasir.html lama dicabut |
| 4 | ★F1 | owner@ | create `fotoBon/uji-v7-foto` | `{ id: "uji-v7-foto", idBon: "b-uji", jenis: "image/jpeg", base64: "QUJD" }` | LOLOS | owner menyimpan foto bon |
| 5 | ★R1 | owner@ | create `penjualan/uji-v7-r1` | `{ id: "uji-v7-r1", tanggal: <hari ini>, hargaTotal: 1000 }` | LOLOS | tulisan biasa owner tidak berubah |
| 6 | ★P1 | owner@ | delete `penjualan/uji-v7-lama` | — | LOLOS | pintu terbuka, salinan arsipnya (U7) SAMA persis |
| 7 | ★P20 | owner@ | delete `penjualan/uji-v7-beda` | — | DITOLAK | salinan arsipnya (U9) berisi lain — hapus lalu tulis ulang = ubah |
| 8 | ★P21 | owner@ | update `arsipTahun/2021\|penjualan\|uji-v7-lama` | `tahun: 2021` (Playground menggabungkannya dengan U7) | LOLOS | salinan arsip = catatan aslinya (U6) |
| 9 | ★P22 | owner@ | create `arsipTahun/2021\|penjualan\|uji-v7-karang` | `{ id: "2021\|penjualan\|uji-v7-karang", tahun: 2021, koleksi: "penjualan", idAsli: "uji-v7-karang", dok: { id: "uji-v7-karang", tanggal: "2021-05-01", hargaTotal: 777 } }` | DITOLAK | salinan karangan: catatan aslinya tidak ada |
| 10 | ★P4 | owner@ | create `penjualan/uji-v7-pulih` | `{ id: "uji-v7-pulih", tanggal: "2021-03-01", hargaTotal: 500 }` | LOLOS | Batalkan: kembali dari arsip (U10), isi sama |
| 11 | ★P2 | owner@ | create `piutangMutasi/uji-v7-pb-baru` | PEMBUKA | LOLOS | saldo pembuka tahun pintu, bertanggal bulan terkunci |
| 12 | ★P23 | owner@ | create `penjualan/uji-v7-pb-jual` | `{ id: "uji-v7-pb-jual", tanggal: "2021-03-01", hargaTotal: 1000, tutupBuku: true, tahunDari: 2021 }` | DITOLAK | nota bukan koleksi saldo pembuka |
| 13 | ★P5 | owner@ | update `pengaturan/titikKas` (dokumen nyata) | `tanggal: "2021-12-31"` | LOLOS | titik kas 31 Des tahun pintu |
| 14 | ★P6 | owner@ | create `pengaturan/pintuBuku` | PINTU | LOLOS | buka pintu tahun lalu: berita acara 2025 (U4) sudah ada & berjalan |
| 15 | ★P16 | owner@ | create `pengaturan/pintuBuku` | PINTU dengan `sampai` = 5 hari lagi | DITOLAK | lebih dari 72 jam |
| 16 | ★T3 | owner@ | update `tutupBukuAcara/2021` | `status: "selesai"` | DITOLAK | pintu 2021 (U5) masih terbuka — selesai wajib menutup pintunya |
| 17 | ★P19 | owner@ | **TERAKHIR**: di tab Data ubah U5 `sampai` → 1 Jan 2020, lalu ulang #6 (delete `penjualan/uji-v7-lama`) | — | DITOLAK | pintu kedaluwarsa |

## Opsional — sudah dinilai model CI & emulator (jalankan kalau sempat; hasilnya harus sama juga, kecuali ★T1 & ★T2 — bagian T)

Kasus berlabel "staf aktif" butuh U11 (lihat "Isian Playground").

### A · hemat baca — wajib LOLOS

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★A2 | kasir@ | update `penjualan/uji-v7-nota` | isi SAMA PERSIS dengan U1 | LOLOS | kirim ulang identik (v2) tetap boleh |
| ★A3 | owner@ | get `batuNisan/uji-v7` | — | LOLOS | owner membaca batu nisan |
| ★A4 | owner@ | delete `batuNisan/uji-v7` | — | LOLOS | owner boleh membereskan |

### B · hemat baca — wajib DITOLAK

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★B1 | kasir@ | update `penjualan/uji-v7-nota` | `hargaTotal: 2000` + `capServer` (timestamp ketikan) | DITOLAK | kirim ulang yang mengubah isi |
| ★B3 | kasir@ | update `stokBahanLiteran/<dokumen apa pun>` | isi sama + `capServer` | DITOLAK | v7: jalur stokBahanLiteran kasir@ dicabut |
| ★B4 | staf aktif | get `batuNisan/uji-v7` | — | DITOLAK | staf tidak membaca batu nisan |
| ★B5 | staf aktif | create `batuNisan/uji-v7` | `{ capServer: <timestamp> }` | DITOLAK | staf tidak menulis batu nisan |
| ★B6 | owner@ | create `batuNisan/uji-v7` | `{ id: "penjualan\|x", koleksi: "penjualan", idDok: "x", capServer: <timestamp ketikan> }` | DITOLAK | cap nisan wajib jam server |
| ★B7 | kasir@ | get `batuNisan/uji-v7` | — | DITOLAK | kasir@ tidak membaca batu nisan |

### N · permintaan nego staf (persetujuan) — staf = akun uji U11

Isi dasar permintaan (sebut "MINTA"): `{ id: "uji-v7-minta", tindakan: "nego", status: "menunggu", negoUid: "uid-uji-b", olehUid: "uid-uji-b", teks: "uji" }`.

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★N1 | staf aktif | create `persetujuan/uji-v7-minta` | MINTA | LOLOS | minta owner dari akun sendiri |
| ★N2 | staf aktif | list `persetujuan` (atau get `persetujuan/uji-v7-minta`) | — | LOLOS | yang meminta membaca keputusan owner |
| ★N3 | owner@ | update `persetujuan/uji-v7-minta` | `status: "disetujui"`, `diputusPada: "x"` | LOLOS | memutus = owner |
| ★N4 | staf aktif | create `persetujuan/uji-v7-minta` | MINTA dengan `negoUid: "uid-lain"` | DITOLAK | atas nama akun lain |
| ★N5 | staf aktif | create `persetujuan/uji-v7-minta` | MINTA dengan `status: "disetujui"` | DITOLAK | menyetujui sendiri |
| ★N6 | staf aktif | create `persetujuan/uji-v7-minta` | MINTA + `diputusPada: "2026-10-09T03:00:00Z"` | DITOLAK | kolom keputusan |
| ★N7 | staf aktif | create `persetujuan/uji-v7-minta` | MINTA dengan `tindakan: "hapus"` | DITOLAK | hanya nego |
| ★N8 | staf aktif | update `persetujuan/uji-v7-minta` | `status: "disetujui"` | DITOLAK | memutus = owner |
| ★N9 | staf aktif | create `persetujuan/uji-v7-minta` | MINTA dengan `olehUid: "uid-lain"` | DITOLAK | penulis harus dirinya |
| ★N10 | akun tanpa aksesAkun (`baru1`) | create `persetujuan/uji-v7-minta` | MINTA dengan `negoUid` & `olehUid` "baru1" | DITOLAK | bukan staf aktif |
| ★N11 | kasir@ | list `persetujuan` | — | DITOLAK | kasir@ tidak membaca persetujuan |

### F · foto bon

Isi dasar ("FOTO"): `{ id: "uji-v7-foto", idBon: "b-uji", jenis: "image/jpeg", base64: "QUJD" }`.

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★F2 | owner@ | list `fotoBon` | — | LOLOS | foto dibaca saat bon dibuka |
| ★F3 | owner@ | delete `fotoBon/uji-v7-foto` | — | LOLOS | foto salah dihapus |
| ★F4 | owner@ | update `fotoBon/uji-v7-foto` | `idBon: "b-lain"` | DITOLAK | foto tidak diubah |
| ★F5 | owner@ | create `fotoBon/uji-v7-foto` | FOTO dengan `jenis: "text/html"` | DITOLAK | hanya gambar |
| ★F6 | owner@ | create `fotoBon/uji-v7-foto` | FOTO dengan `id: "lain"` | DITOLAK | id isi = id dokumen |
| ★F7 | owner@ | create `fotoBon/uji-v7-foto` | FOTO tanpa `idBon` | DITOLAK | foto harus menunjuk bon |
| ★F8 | staf aktif | list `fotoBon` | — | DITOLAK | owner saja |

### K · kasir@ dipangkas (kasir darurat saja)

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★K1 | kasir@ | create `perangkatStatus/d-uji` | `{ id: "d-uji", aplikasi: "darurat", pada: "2026-10-09T03:00:00Z" }` | LOLOS | denyut HP penjaga |
| ★K2 | kasir@ | get `ringkasanKasir/aktif` | — | LOLOS | katalog kasir darurat |
| ★K4 | kasir@ | create `stokBahanLiteran/uji-v7-k` | `{ id: "uji-v7-k", tipe: "pakai", tanggal: <hari ini>, jumlah: 1 }` | DITOLAK | v7: dicabut |
| ★K5 | kasir@ | create `logAktivitas/uji-v7-k` | `{ id: "uji-v7-k", aksi: "tulis" }` | DITOLAK | v7: dicabut |
| ★K6 | kasir@ | get `pengaturan/aksesKasir` | — | DITOLAK | v7: dicabut |
| ★K7 | kasir@ | get `pengaturan/keamanan` | — | DITOLAK | PIN owner: owner saja |

### R · regresi staf

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★R2 | staf aktif | create `penjualan/uji-v7-r2` | `{ id: "uji-v7-r2", tanggal: <hari ini>, hargaTotal: 1000, caraBayar: "Tunai", olehUid: "uid-uji-b" }` | LOLOS | nota staf tidak berubah |
| ★R3 | staf aktif | get `penjualan/uji-v7-nota` | — | LOLOS | staf membaca nota |

### P · pintu tutup buku (U2 kunci uji `2021-12`, U5 pintu 2021 terbuka, U4 berita acara 2025 berjalan)

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★P7 | owner@ | update `pengaturan/pintuBuku` | `status: "tutup"` | LOLOS | menutup pintu kapan saja |
| ★P9 | owner@ | update `penjualan/uji-v7-lama` | `hargaTotal: 2000` | DITOLAK | pintu tidak membuka UBAH |
| ★P10 | owner@ | create `penjualan/uji-v7-baru2` | `{ id: "uji-v7-baru2", tanggal: "2021-06-20", hargaTotal: 1000 }` | DITOLAK | catatan biasa di bulan terkunci |
| ★P11 | owner@ | create `piutangMutasi/uji-v7-pb-lain` | PEMBUKA dengan `id: "uji-v7-pb-lain"`, `tahunDari: 2020` | DITOLAK | saldo pembuka tahun LAIN |
| ★P12 | owner@ | create `piutangMutasi/uji-v7-pb-tanpa` | PEMBUKA dengan `id: "uji-v7-pb-tanpa"` TANPA `tutupBuku` | DITOLAK | bukan saldo pembuka |
| ★P13 | owner@ | create `penjualan/uji-v7-pulih` | seperti #10 dengan `hargaTotal: 600` | DITOLAK | isi beda dari salinan arsip |
| ★P14 | kasir@ | create `piutangMutasi/uji-v7-pb-baru` | PEMBUKA | DITOLAK | pintu owner saja |
| ★P15 | staf aktif | delete `penjualan/uji-v7-lama` | — | DITOLAK | pintu owner saja |
| ★P17 | owner@ | create `pengaturan/pintuBuku` | PINTU dengan `tahun: <tahun ini>` | DITOLAK | tahun berjalan tidak ditutup |
| ★P18 | owner@ | create `pengaturan/pintuBuku` | PINTU dengan `tahun: 2020` | DITOLAK | bukan tahun lalu, tanpa berita acara |
| ★P24 | owner@ | create `pengaturan/pintuBuku` | PINTU dengan `tahun: 2021` | DITOLAK | berita acara 2021 (U3) ada, tapi bukan tahun lalu |
| ★P25 | owner@ | update `pengaturan/titikKas` (dokumen nyata) | `tanggal: "2021-06-30"`, `laci: 1` | DITOLAK | bukan 31 Des, bukan PERSIS titikSebelum berita acara (U3) |
| ★P26 | owner@ | **create** `pengaturan/titikKas` | `{ id: "titikKas", tanggal: "2021-06-30", laci: 7, brankas: 0 }` | LOLOS | Batalkan: titik kas kembali = titikSebelum U3 persis (create = isian apa adanya) |

### T · berita acara tutup buku

**★T1 & ★T2 tidak bisa dinilai jujur di Playground.** `acaraBaru` mewajibkan `paraf.pada` berupa TEKS jam ISO `…T…Z` (bentuk `toISOString()` yang ditulis
aplikasi). Playground mengubah teks seperti itu menjadi *timestamp* sebelum rules menilainya (`docs/uji-rules-v6.md` "Sifat Playground"), jadi di
Playground ★T1 keluar **DITOLAK** dan ★T2 DITOLAK karena sebab yang sama, bukan karena jam mulainya — keduanya tidak dihitung di Playground. Kolom "Wajib"
di bawah = perilaku SERVER; buktinya emulator (bagian "Bukti emulator": ★T1 LOLOS, ★T2 DITOLAK, dan kontrol "berita acara baru tanpa pemeriksa jam mulai"
membalik ★T2) dan gladi pintu (aplikasi asli membuat berita acara baru di server dengan jam server). ★T3–★T5 tidak memakai teks ISO di isiannya.

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★T1 | owner@ | create `tutupBukuAcara/2024` | `{ id: "2024", tahun: 2024, mode: "sungguhan", status: "berjalan", paraf: { pada: "<hari ini YYYY-MM-DD>T03:00:00.000Z" } }` (`paraf` = map, `pada` = string; mis. "2026-10-10T03:00:00.000Z" bila hari ini 10 Okt) | LOLOS | berita acara baru berbentuk benar, jam mulai hari ini (Playground: keluar ditolak — teks ISO) |
| ★T2 | owner@ | create `tutupBukuAcara/2024` | seperti ★T1 dengan `paraf: { pada: "2025-06-01T00:00:00.000Z" }` | DITOLAK | jam mulai jauh mundur (Juni tahun lalu) |
| ★T4 | owner@ | delete `tutupBukuAcara/2025` | — | DITOLAK | berita acara yang belum dibatalkan tidak dihapus |
| ★T5 | owner@ | create `tutupBukuAcara/<tahun ini>` | seperti ★T1 dengan `id` & `tahun` tahun ini | DITOLAK | tahun berjalan tidak ditutup |

Model CI juga menilai (tidak perlu di Playground): kirim ulang kasir-v32 tanpa `capServer` & buang cap + ubah isi (M-A5, M-B8 — Playground tidak bisa
membuang kolom), hapus tanpa salinan arsip (M-P8), salinan arsip berisi lain / koleksi tak diarsip / id tak cocok / bulan terbuka (M-P26b–e), tarik
saldo pembuka (M-P3), pintu di atas berita acara selesai / dimulai sebelum tahunnya berakhir (M-P24b, M-P24c), pintu di atas berita acara yang jam
mulainya berbentuk `toISOString()` seperti tulisan aplikasi (M-P6b, wajib LOLOS — Playground mengubah bentuk itu),
pintu tutup / tanpa pintu (M-P20, M-P21), catatan sesudah tahun pintu (M-P22, M-P25), `pindahUang` tidak berpintu (M-P23), titik kas mundur ke tahun
sesudah pintu (M-P24d), ubah catatan terkunci jadi sama dengan salinannya (M-P26), pintu tahun berjalan walau berita acaranya ada (M-P27), selesai
bersama pintu tertutup & hapus berita acara dibatalkan (M-T6, M-T7, wajib LOLOS), berita acara baru langsung selesai / id ≠ tahun (M-T8, M-T9), foto bon
kebesaran (M-F9). Ritual tutup buku 2027 seutuhnya (tiap kiriman, arsip, Batalkan, kiriman yang dikarang) dinilai `alat-uji/uji_tutup_buku_2027.py`.

## Bukti emulator

Workflow **Uji rules di emulator** (`.github/workflows/uji-rules-emulator.yml`, hanya di runner GitHub; alatnya `alat-uji/uji_rules_emulator.py`)
memasang teks `firestore.rules` cabang ini ke **Firebase Emulator Firestore** — penilai rules yang sama dengan server produksi, jadi salah tulis
yang tidak dimodelkan penafsir mini ikut ketahuan — lalu menjalankan **semua** kasus berkas ini lewat REST:

- dokumen uji **U1–U11 yang sama** (tabel "Dokumen uji"), diisi lewat jalur admin emulator; tiap kasus mulai dari emulator kosong;
- **token akun palsu** dengan uid & email persis "Isian Playground" (JWT tanpa tanda tangan — hanya emulator yang menerimanya, tidak pernah
  server toko);
- tanggal "hari ini", besok, 5 hari lagi, cap 1 jam lalu digeser ke jam runner; cap "jam server" dikirim sebagai transform `REQUEST_TIME`
  (yang tidak bisa diketik di Playground). **Tahun** dokumen uji digeser sebesar selisih tahun runner (WIB) − 2026: tahun lalu = tahun runner − 1,
  tahun berjalan = tahun runner, 2021 → 2021 + selisih, dst. Jadi bukti ini tetap mengukur sesudah 1 Januari 2027 — saat tutup buku 2026 berjalan
  dengan rules v7 dan perbaikan rules paling mungkin dibutuhkan (sebelum sanggahan 7 Okt alat ini melaporkan TIDAK TERUKUR di tahun lain dan
  gagal). `--periksa` (Mac & job uji) membuktikan model atas dokumen uji yang digeser = kolom Wajib di 1 Jan 2027 00.30 WIB, 2 Jan 2027, Juni 2027,
  dan Januari 2028; tanpa geser tahun model menyimpang di Juni 2027 (★P6, M-P6b, M-P27, ★T5), dan `--kontrol` membuktikan alat yang lupa menggeser
  tahun ketahuan.

Selain 69 kasus ★ (17 Wajib owner + 52 opsional), dijalankan juga 24 kasus model M-\* (yang tidak bisa di Playground, mis. membuang kolom, atau jam
mulai berbentuk ISO), 5 kasus server S-\* (kirim ulang kasir@ bercap jam server: nota baru, kirim ulang identik, atas nota yang sudah bercap; batu
nisan bercap jam server; batu nisan tanpa cap), dan **45 kasus H** = berita acara tutup buku **hanya maju** v6 (`docs/uji-rules-v6.md` A/B, model
`periksa_rules.KASUS_BUKU`: 19 boleh, 26 ditolak) atas teks v7, dengan dokumen ujinya sendiri (`tutupBukuAcara/1990` = isi lama, tanpa pintu) — v7
mengubah blok `tutupBukuAcara` (create `acaraBaru`, update + `acaraTutupPintu`, delete hanya dibatalkan), jadi "hanya maju" dibuktikan tetap di
server, bukan hanya di model. Kasus yang sama dijalankan atas `firestore.rules.v6`: yang berbeda wajib PERSIS 38 kasus akibat lima ubahan di atas
(bukti ubahan itulah yang membuat beda), selebihnya (termasuk ke-45 kasus H) sama. **Kontrol** (26 + 1 kasir): rules v7 dirusak satu suku → kasus
sasarannya wajib berbalik (LOLOS ↔ DITOLAK, bukan galat) — pintuSah selalu benar, ulangKasirBercap tanpa syarat capServer, salinan arsip tanpa
pembanding isi, pintu tanpa batas `sampai`, berita acara tanpa pemeriksa jam mulai, selesai walau pintu terbuka, kasir@ boleh lagi piutangMutasi,
foto bon jenis apa saja, nego atas nama orang lain, batu nisan tanpa cap jam server, saldo pembuka di koleksi mana pun, salinan arsip tidak diikat
ke aslinya, staf membaca batu nisan; sejak sanggahan 7 Okt juga suku yang dulu hanya diperiksa kasusnya: `pintuTitik` selalu benar (★P25 & M-P24d —
★P25 DITOLAK juga di v6, jadi kepekaannya pada suku v7 hanya terbukti lewat kontrol ini), `titikSebelum` tanpa pembanding kantong (★P25), tanpa
cabang `titikSebelum` (★P26), tanpa cabang 31 Des (★P5), `ulangKasirBercap` tanpa pembanding isi (★B1, M-B8), `acaraBaru` tanpa syarat mode &
status (M-T8) / tahun lampau (★T5) / id = tahun (M-T9), hapus berita acara tanpa syarat "dibatalkan" (★T4), permintaan nego staf tanpa syarat
status (★N5) / tindakan (★N7) / larangan kolom keputusan (★N6), dan berita acara boleh mundur selesai → terkunci (kasus H ★B16).

**Kasir darurat — kode ASLI** (skrip halaman `kasir-darurat-nominal.html` dijalankan di node dengan DOM tiruan, `alat-uji/kasir_emulator.js`;
alamat Firestore ditulis ulang ke emulator): kasir-v33 (cabang ini) mencatat nota lalu `:commit` bercap `REQUEST_TIME` → masuk; kirim ulang identik
(jawaban hilang) → `:commit` DITERIMA dengan cap jam server baru; kirim ulang yang mengubah isi → `:commit` & cara lama ditolak, karcis ke daftar
"ditolak", dokumen server tidak berubah. kasir-v32 (main 6 Okt) kirim ulang identik atas nota bercap → PATCH utuh diterima (capServer terbuang);
yang mengubah isi → ditolak; nota baru → masuk. Di v6: kirim ulang v33 jatuh ke cara lama dan tetap masuk tanpa dobel, v32 atas nota bercap ditolak
(sebab v7 perlu `ulangKasirBercap`). Kontrol: suku `(kasir() && ulangKasirBercap())` dicabut → berbunyi.

**Hasil** — workflow Uji rules di emulator, run **37567891588** (df71093) dan **37572040013** (3439466), keduanya sebelum sanggahan bukti emulator
7 Okt (`firestore.rules` sama persis dengan berkas ini; sesudah sanggahan pun rules tidak diubah):

- v7: **97/97 sesuai kolom Wajib** — Wajib owner (waktu itu 18, ★T1 ikut) **18/18**, opsional ★ **51/51**, model M **23/23**, server S **5/5**;
  0 tidak terukur;
- v6: 97/97 sesuai harapan — **38 kasus berbeda, tepat BEDA_V6** (lima ubahan), 59 sama;
- kontrol: **14/14 berbunyi**;
- kasir darurat (kode asli): rules v7 **6/6**, rules v6 **4/4** (perilaku v6 yang diharapkan), kontrol suku `ulangKasirBercap` dicabut berbunyi
  (kirim ulang v33 & v32 atas nota bercap jatuh).

Sesudah sanggahan (paraf U3/U4 bukan ISO, ★T1 keluar dari Wajib owner, ★T2 Juni tahun lalu, M-P6b, tahun digeser, 45 kasus H, 27 kontrol): hasil
run-nya di deskripsi PR #111 bagian "Bukti server: emulator".

**Gladi tutup buku lewat pintu** (workflow Gladi tutup buku, skenario `pintu`, `docs/gladi-tutup-buku.md`): /baru/ asli di Chrome headless menutup
buku tahun yang SEMUA bulannya terkunci, di emulator dengan rules v7 ini. Penyesuaian jam yang jujur: data contoh bertahun 2026 dengan kunci periode
sampai Desember 2026, dan jam JVM emulator **digeser ke 5 Jan 2027 15.30 WIB** (`alat-uji/jam_geser.c`, hanya jam dinding JVM emulator; jam server diukur lewat transform
`REQUEST_TIME` di tiap skenario) — mekanismenya sama dengan tutup buku 2027 pada Januari 2028. Run **37568246193** (7 Okt): **semua cek SERVER
skenario pintu lulus** — sesudah kunci pintu 2026 terbuka ≤ 72 jam dari jam server, `arsipTahun` = ISI 1.344 catatan asli, saldo pembuka = berita
acara, pindahan uang bulan terkunci (tidak diarsip) utuh, titik kas 31 Des; kunci kedua sesudah mulai lagi sama; selesai menutup pintu; sesudah
selesai, dengan token owner: pintu KEDALUWARSA menolak pengembalian dari arsip & penghapusan catatan bulan terkunci yang salinannya ada (403), pintu
yang sama dengan `sampai` besok menerimanya. Dua cek ALAT gladi (bukan rules) dibetulkan sesudah run itu: pembanding isi sesudah BATALKAN menghitung
`capServer` baru (hemat baca mengecap catatan yang dikembalikan) sebagai "berubah", dan pita "selesaikan" sesudah kunci dianggap tertunda. Hasil run
sesudah pembetulan: deskripsi PR #111.

**Temuan kuota (bukan rules)**: tutup buku tahun yang SEMUA bulannya terkunci memindah catatan 3 per kiriman (5 pemeriksaan per catatan) + satu baris
jejak per kiriman. Diproyeksikan ke skala ±17 rb catatan — itu catatan 2026 SAJA (8 Agu–31 Des), bukan setahun penuh — ritual bersih menulis **±23,5 rb
dokumen = 117% batas Spark sehari** (ritual 2026 tanpa bulan terkunci: proyeksi dari laju cadangan toko 6 Okt sekarang **±98–104%** batas tulis — bisa
MEPET atau TIDAK MUAT; dulu ditulis ±18,9 rb = 94%). Kartu "Perkiraan kuota Firestore" di halaman memperkirakan angka yang sama (1.844 vs terukur 1.854
di skala gladi).

**Setahun penuh 2027 (tutup buku Januari 2028) jauh lebih besar.** Dengan laju cadangan toko 6 Okt (±117–141 catatan sehari) arsipnya ±43–51 rb catatan,
±2,5–3× skala di atas. Rumus kartu, rata-rata per catatan setahun dengan Januari–November terkunci: tulis ±1,3 · hapus 1 · baca ±5,9 (5 pemeriksaan
server tiap catatan bulan terkunci, dihitung tanpa potongan cache, + sekali muat) — dihitung ulang dari kode oleh `alat-uji/uji_dokumen_owner.py`. Hasilnya
tulis **±280–335%**, hapus **±215–255%**, baca **±505–600%** batas Spark sehari: **BEBERAPA hari kuota, bukan satu** — tulis & hapus saja ±3–4 hari, baca
menurut kartu (perkiraan atas) ±6–7 hari (ukuran dalam jatah gratis harian Spark). Di Spark tiap kali kuota habis arsip berhenti dan diteruskan dengan "Lanjutkan" sesudah reset; **sejak Blaze (9 Okt 2026) arsip tidak berhenti karena
kuota** — kelebihannya ditagih (perkiraan di bawah Rp5.000 untuk seluruh ritual, tarif termahal resmi US$0,06 per 100 rb baca & US$0,18 per 100 rb tulis,
kurs ±Rp16.500). Angka sebenarnya = kartu "Perkiraan kuota
Firestore" di langkah 1 pada hari itu.

Keputusan owner K11 (8 Okt 2026) **DICABUT 9 Okt 2026**: proyek pindah ke paket **Blaze** — kuota harian bukan lagi batas (kelebihannya ditagih),
jadi arsip tidak berhenti di tengah karena kuota dan toko tidak perlu tutup sesudah hari ritual (dulu: toko TUTUP Sabtu 2 Jan 2027; tutup buku 2027 toko
tutup BEBERAPA hari). Ritual Jumat 1 Jan 2027 dan ritual Sabtu 1 Jan 2028 jam bebas; kartu "Perkiraan kuota Firestore" masih menghitung batas Spark —
MEPET / TIDAK MUAT boleh diabaikan, angkanya = ukuran ritual (persen jatah gratis sehari). Jangan berjualan sampai pita "… terkunci dan arsipnya habis"
(`docs/prosedur-pulih-darurat.md`, daftar periksa ritual).

Tidak ada kasus yang perilaku server-nya beda dari kolom Wajib → `firestore.rules` **tidak diubah** oleh bukti ini. Langkah owner di Playground
TETAP: emulator memakai mesin rules yang sama tetapi bukan proyek toko, sedangkan Playground menilai teks yang akan diterbitkan atas data proyek
toko. Playground sendiri BUKAN tiruan sempurna server (isian *update* digabung, teks jam ISO jadi *timestamp*), karena itu "Wajib owner" hanya memuat
kasus yang hasilnya tidak terpengaruh sifat itu.

## Hasil Playground

**7 Okt 2026 — v7 TERBIT 18.25 WIB.** Dokumen uji U1–U10 dibuat Claude lewat Console (Chrome owner; sebelum itu dicek `aturanToko/kunciPeriode` BELUM
ada — tidak ada kunci sungguhan), `firestore.rules` cabang ini ditempel ke editor dan sidik isi editor (SHA-256 `e0ed6a975dd5…`, 49.960 byte) = berkas repo;
Playground dijalankan Claude; owner menghapus kesepuluh dokumen uji (diperiksa Claude: semua tidak ada, `pengaturan/titikKas` utuh) lalu menekan Publish.
Sesudah muat ulang, versi aktif = sidik yang sama. Langkah 6: nota kasir darurat (HP penjaga, versi lama) tercatat 18.27 — masuk.

| # | Kasus | Wajib | Playground |
|---|---|---|---|
| 1 | ★A1 | LOLOS | LOLOS ✓ |
| 2 | ★B2 | DITOLAK | DITOLAK ✓ (lihat batas b) |
| 3 | ★K3 | DITOLAK | DITOLAK ✓ ("Null value error") |
| 4 | ★F1 | LOLOS | LOLOS ✓ |
| 5 | ★R1 | LOLOS | LOLOS ✓ |
| 8 | ★P21 | LOLOS | LOLOS ✓ |
| 9 | ★P22 | DITOLAK | DITOLAK ✓ |
| 6, 7, 10–13, 16, 17 | ★P1 ★P20 ★P4 ★P2 ★P23 ★P5 ★T3 ★P19 | — | **tidak bisa dinilai** (batas a) |
| 14, 15 | ★P6 ★P16 | — | **tidak bisa dinilai** (batas b) |

**Batas Rules Playground (terbukti 7 Okt, Console Firebase versi Okt 2026)** — bukan cacat rules; semua kasus di atas lulus di emulator (bagian "Bukti
emulator", mesin rules yang sama):

- (a) **`getAfter()` tidak didukung**: banner "Error running simulation — The simulator currently does not support the "getAfter" function" (kadang hanya
  "An unknown error occurred"). Semua jalur pintu memanggil `pintuTahun()` → `getAfter(pengaturan/pintuBuku)`, dan `acaraTutupPintu` juga.
- (b) **Timestamp dari "Build document" bukan Timestamp**: dikirim sebagai map `{type: "firestore/timestamp/1.0", seconds, nanoseconds}`, sehingga
  `… is timestamp` = false (rincian evaluasi ★P6: `is timestamp` false) → DITOLAK palsu. ★B2 tetap DITOLAK, tapi Playground tidak bisa membedakan
  sebabnya.
- Untuk rules berikutnya: daftar "Wajib owner" Playground hanya kasus tanpa `getAfter` dan tanpa timestamp ketikan; sisanya diwajibkan lulus di emulator
  (`alat-uji/uji_rules_emulator.py`, workflow "Uji rules di emulator"). Isi dialog Build document lewat rujukan elemen, bukan koordinat — klik yang jatuh
  saat dialog beranimasi bisa nyasar; periksa sidik isi editor sebelum Publish.
