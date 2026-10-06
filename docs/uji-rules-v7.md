# Uji rules v7 FINAL di server — terbit SEKALI (DRAF 7 Okt 2026, belum terbit)

`alat-uji/periksa_rules.py` memeriksa **bentuk** rules di CI: v7 = `firestore.rules.v6` + PERSIS lima ubahan di bawah (dibandingkan tanpa komentar &
spasi, blok demi blok), dan sejak v7 juga **menilai teks rules** dengan penafsir mini (`alat-uji/rules_mini.py`) pada SEMUA kasus ★ di berkas ini, dengan
dokumen uji yang sama — kolom "Wajib" di tabel sudah lulus model di CI. `alat-uji/uji_tutup_buku_2027.py` menjalankan ritual tutup buku 2027 sungguhan
di kotak pasir dan menilai TIAP batch-nya dengan teks rules yang sama. Model bukan server: berkas ini untuk **perilaku server** — kasus yang dijalankan
owner di **Rules Playground** (Console › Firestore › Rules) dengan v7 di EDITOR, **sebelum** Publish. Claude Code tidak memegang sandi dan tidak mengetik
apa pun di Console; Claude hanya MEMBACA Console lewat Chrome owner pada langkah yang disebut. Rules = TUGAS OWNER. Kasus v6 tetap di `docs/uji-rules-v6.md`.

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
5. **Pintu tutup buku** (keputusan owner 7 Okt, K8 "pengecualian sempit"): tanpa ini, begitu satu bulan 2027 dikunci, tutup buku 2027 mustahil (rules
   menolak tulis/hapus bulan terkunci) dan butir A2 menahan kunci 2028 → buntu Januari 2028. Dokumen `pengaturan/pintuBuku` = `{ tahun: Y, status:
   'berjalan', sampai: <timestamp> }` dibuat **owner** hanya selagi berita acara `tutupBukuAcara/Y` berjalan / terkunci / membatalkan (dinilai sesudah batch —
   aplikasi membukanya di kiriman pertama ritual), `Y` < tahun ini, `sampai` ≤ jam server + **72 jam**. Selama terbuka & belum lewat `sampai`, owner boleh —
   hanya untuk catatan bertanggal ≤ Desember Y di bulan terkunci:
   - **menghapus** catatan yang salinannya ADA di `arsipTahun/'Y|koleksi|id'` sesudah batch itu (arsip = pindah, bukan buang), atau saldo pembuka tahun Y
     itu sendiri (tarik saat Batalkan);
   - **membuat** saldo pembuka tahun Y (`tutupBuku: true`, `tahunDari: Y`) — piutang bertanggal utang tertua, bon pemasok bertanggal bonnya, modal owner
     31 Des — atau **mengembalikan** catatan dari arsip Y yang isinya SAMA dengan salinannya (hanya `capServer` boleh beda; Batalkan);
   - **titik kas** `pengaturan/titikKas` bertanggal ≤ 31 Des Y (titik 31 Des & pengembaliannya saat Batalkan).

   **Tidak ada pintu** untuk UBAH catatan apa pun, untuk catatan bulan terkunci lainnya, untuk `pindahUang` / `slipUpah` (tidak diarsip), untuk kasir@ /
   staf. Status `'tutup'` (aplikasi menutup pintu saat selesai / dibatalkan) boleh kapan saja. Access call jalur pintu (cache tidak diandalkan): buat /
   hapus saldo pembuka & titik kas 2, hapus arsip & kembalikan 3, buka pintu 1 — aplikasi memecah kiriman ≤ 18.

**Aman diterbitkan SEBELUM cabang digabung**: kode yang tayang (main) tidak memakai kelima hal itu — kasir darurat tetap jalan (nota, denyut, katalog),
permintaan nego staf belum dikirim (tombolnya masih mati), foto bon & pintu belum ditulis siapa pun. Urutannya tetap: **v7 terbit dulu, baru PR #111
digabung** (owner bilang "merge").

**Mundur**: JANGAN tempel `firestore.rules.v6` selama kode cabang ini berjalan (hapus /baru/ ber-batu nisan, permintaan nego staf, foto bon, dan tutup buku
2027 ditolak). Mundur hemat baca = saklar (Menu › Sistem › Perangkat › Hemat baca, atau `/baru/?hemat=mati`). v6 baru boleh ditempel balik SESUDAH cabang
dibalik (git revert) dan HP kasir kembali ke kasir-v32.

---

## Urutan (satu kali duduk ± 45 menit, saat toko tutup; jangan klik **Publish** sebelum langkah 5)

1. **Persiapan** — v6 masih yang terbit. Cek Console › Firestore › **Usage** dulu (Playground ikut kuota baca Spark; kerjakan sesudah 14.00 WIB bila kuota
   hari itu menipis). Console › Firestore › **Data** (Console menulis sebagai admin, rules tidak menilai): buat **sepuluh dokumen uji** (U1–U10) di tabel "Dokumen uji".
   Selama dokumen uji ada, aplikasi bisa menampilkan hal aneh (kunci "sampai Desember 2021", pita "Tutup buku 2021", nota contoh bertanggal 2021) —
   **jangan ketuk apa pun di aplikasi**, selesaikan langkah 1–4 dalam satu duduk.
2. **Tempel `firestore.rules`** dari cabang ke editor — **belum Publish**. Salin tanpa merusak huruf:
   `git show origin/perbaikan/hemat-baca:firestore.rules | LANG=en_US.UTF-8 pbcopy` (sesudah merge: `origin/main`). Verifikasi di editor: baris 2
   berbunyi `ATURAN FIRESTORE v7 FINAL`, ada fungsi `ulangKasirBercap`, `stafMintaNego`, `pintuTahun`, `pintuSah`, dan blok `match /fotoBon/{id}`.
   Editor yang menolak menyimpan (garis merah) = berhenti, kirim tangkapan layar ke Claude.
3. Jalankan bagian **A, B, N, F, K, R, P** di Playground — kolom "Wajib". ★P19 PALING AKHIR (mengubah dokumen uji pintu).
4. **Owner menghapus SEPULUH dokumen uji** (U1–U10) di tab Data (Claude tidak boleh menghapus data). **`aturanToko/kunciPeriode` WAJIB hilang**: kalau tertinggal,
   bulan sampai Desember 2021 terkunci dan kunci bulan pertama Januari 2027 DITOLAK (kunci hanya boleh naik satu bulan dari Desember 2021) — dan di bawah
   rules dokumen itu tidak bisa dihapus dari aplikasi, hanya dari Console. Bilang ke Claude "dokumen uji sudah dihapus" → Claude membuka Console ›
   Firestore › Data lewat Chrome owner (hanya membaca) dan memastikan kesepuluhnya **tidak ada** (tanpa Claude: owner memeriksa sendiri daftar yang sama).
5. **Publish** (owner). Isi editor harus persis `firestore.rules` di repo. Lalu Console › Rules menampilkan versi aktif — baris 2 `ATURAN FIRESTORE v7
   FINAL` (Claude membaca lewat Chrome owner, atau owner melihatnya sendiri).
6. **Sesudah terbit**: satu nota dari kasir darurat (HP penjaga, MASIH versi lama) → pastikan masuk di layar Jual `/baru/`. Tidak masuk → tempel
   `firestore.rules.v6` (kode cabang belum digabung, jadi masih aman) dan kabari Claude.
7. Baru sesudah itu **PR #111 digabung** (owner bilang "merge"; Pages hijau). HP penjaga dibuka sekali sampai bilah atas berbunyi **"versi 7 Okt"**
   (kasir-v33). Langkah sesudahnya (hemat baca, foto bon, nego staf): lihat isi PR #111.

### Isian Playground

*Authenticated* on, provider password. **Firebase UID** & **Auth token payload** (`"email"`, huruf kecil) per akun:

| Akun | Firebase UID | email di payload |
|---|---|---|
| owner@ | `uid-uji` | `owner@tokoberasmiqbal.web.app` |
| kasir@ | `uid-kasir-uji` | `kasir@tokoberasmiqbal.web.app` |
| staf aktif | **UID akun ben/karyawan AKTIF yang sudah terdaftar** (salin dari Console › Authentication; `aksesAkun/<uid>` harus ada) | email akun itu |
| akun tanpa aksesAkun | `baru1` | `uji.baru1@contoh.com` |

Di kasus staf, `<uid staf>` = UID itu (ketik di isian dokumen yang memintanya). "Error running simulation … Null value error" = **DITOLAK** di server
(bukan lolos). Playground tidak mengubah apa pun di database.

**Cara Playground menilai *update* (terbukti 25 Sep)**: isian *Build document* DIGABUNG ke dokumen yang sudah ada — kolom yang diisi saja yang berubah;
kolom tidak bisa DIBUANG. Untuk kasus update, isi hanya kolom yang disebut. *Create* memakai isian apa adanya.

### Dokumen uji (tab Data; HAPUS lagi di langkah 4)

Tahun **2021** sengaja: tidak ada catatan toko bertanggal ≤ 2021 (piutang tertua Juli 2022), jadi kunci uji `2021-12` tidak mengunci catatan sungguhan.

| No | Jalur | Isi (jenis kolom) |
|---|---|---|
| U1 | `penjualan/uji-v7-nota` | `id` "uji-v7-nota" · `tanggal` "<hari ini YYYY-MM-DD>" · `hargaTotal` 1000 (number) · `namaProduk` "Contoh" |
| U2 | `penjualan/uji-v7-bercap` | isi U1 dengan `id` "uji-v7-bercap" + `capServer` (timestamp, jam berapa saja) |
| U3 | `aturanToko/kunciPeriode` | `sampaiBulan` "2021-12" · `riwayat` (array) kosong — **WAJIB dihapus lagi** |
| U4 | `tutupBukuAcara/2021` | `tahun` 2021 (number) · `status` "terkunci" |
| U5 | `pengaturan/pintuBuku` | `id` "pintuBuku" · `tahun` 2021 (number) · `status` "berjalan" · `sampai` (timestamp) 1 Jan 2100 00:00 |
| U6 | `penjualan/uji-v7-lama` | `id` "uji-v7-lama" · `tanggal` "2021-06-15" · `hargaTotal` 1000 |
| U7 | `penjualan/uji-v7-tanpa` | `id` "uji-v7-tanpa" · `tanggal` "2021-06-16" · `hargaTotal` 1000 |
| U8 | `arsipTahun/2021\|penjualan\|uji-v7-lama` | `id` "2021\|penjualan\|uji-v7-lama" · `tahun` 2021 · `koleksi` "penjualan" · `idAsli` "uji-v7-lama" · `dok` (map) = isi U6 persis |
| U9 | `arsipTahun/2021\|penjualan\|uji-v7-pulih` | `id` "2021\|penjualan\|uji-v7-pulih" · `tahun` 2021 · `koleksi` "penjualan" · `idAsli` "uji-v7-pulih" · `dok` (map) `{ id "uji-v7-pulih", tanggal "2021-03-01", hargaTotal 500 }` |
| U10 | `piutangMutasi/uji-v7-pembuka` | `id` "uji-v7-pembuka" · `tipe` "saldoAwal" · `tutupBuku` true (boolean) · `tahunDari` 2021 · `tanggal` "2021-03-01" · `nominal` 1000 |
Garis tegak di jalur arsip memang bagian id dokumen (`2021|penjualan|uji-v7-lama`); di tabel ditulis `\|` hanya karena format tabel. ★P5 memakai
dokumen NYATA `pengaturan/titikKas` tanpa mengubahnya (Playground tidak menulis) — dokumen itu BUKAN dokumen uji, JANGAN dihapus.

## A · hemat baca — wajib LOLOS

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★A1 | kasir@ | create `penjualan/uji-v7-baru` | `{ id: "uji-v7-baru", tanggal: <hari ini>, hargaTotal: 1000, namaProduk: "Contoh" }` tanpa `capServer` | LOLOS | HP kasir v32 tetap masuk |
| ★A2 | kasir@ | update `penjualan/uji-v7-nota` | isi SAMA PERSIS dengan U1 | LOLOS | kirim ulang identik (v2) tetap boleh |
| ★A3 | owner@ | get `batuNisan/uji-v7` | — | LOLOS | owner membaca batu nisan |
| ★A4 | owner@ | delete `batuNisan/uji-v7` | — | LOLOS | owner boleh membereskan |
| ★A5 | kasir@ | update `penjualan/uji-v7-bercap` | isi U2 tanpa `capServer` (kolom lain sama) | LOLOS | HP kasir-v32 kirim ulang nota yang sudah disentuh. Playground tidak bisa MEMBUANG kolom (isian digabung): bila hasilnya sama dengan ★A2 (lolos karena identik) itu wajar; model CI menilai bentuk tanpa `capServer` |

## B · hemat baca — wajib DITOLAK

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★B1 | kasir@ | update `penjualan/uji-v7-nota` | `hargaTotal: 2000` + `capServer` (timestamp ketikan) | DITOLAK | kirim ulang yang mengubah isi |
| ★B2 | kasir@ | update `penjualan/uji-v7-nota` | `capServer` = timestamp **ketikan** | DITOLAK | cap dari jam HP tidak diterima |
| ★B3 | kasir@ | update `stokBahanLiteran/<dokumen apa pun>` | isi sama + `capServer` | DITOLAK | v7: jalur stokBahanLiteran kasir@ dicabut |
| ★B4 | staf aktif | get `batuNisan/uji-v7` | — | DITOLAK | staf tidak membaca batu nisan |
| ★B5 | staf aktif | create `batuNisan/uji-v7` | `{ capServer: <timestamp> }` | DITOLAK | staf tidak menulis batu nisan |
| ★B6 | owner@ | create `batuNisan/uji-v7` | `{ id: "penjualan\|x", koleksi: "penjualan", idDok: "x", capServer: <timestamp ketikan> }` | DITOLAK | cap nisan wajib jam server |
| ★B7 | kasir@ | get `batuNisan/uji-v7` | — | DITOLAK | kasir@ tidak membaca batu nisan |
| ★B8 | kasir@ | update `penjualan/uji-v7-bercap` | `hargaTotal: 2000` | DITOLAK | membuang / membawa cap tidak membuka jalan mengubah isi |

## N · permintaan nego staf (persetujuan)

Isi dasar permintaan (sebut "MINTA"): `{ id: "uji-v7-minta", tindakan: "nego", status: "menunggu", negoUid: "<uid staf>", olehUid: "<uid staf>", teks: "uji" }`.

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

## F · foto bon

Isi dasar ("FOTO"): `{ id: "uji-v7-foto", idBon: "b-uji", jenis: "image/jpeg", base64: "QUJD" }`.

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★F1 | owner@ | create `fotoBon/uji-v7-foto` | FOTO | LOLOS | owner menyimpan foto |
| ★F2 | owner@ | list `fotoBon` | — | LOLOS | foto dibaca saat bon dibuka |
| ★F3 | owner@ | delete `fotoBon/uji-v7-foto` | — | LOLOS | foto salah dihapus |
| ★F4 | owner@ | update `fotoBon/uji-v7-foto` | `idBon: "b-lain"` | DITOLAK | foto tidak diubah |
| ★F5 | owner@ | create `fotoBon/uji-v7-foto` | FOTO dengan `jenis: "text/html"` | DITOLAK | hanya gambar |
| ★F6 | owner@ | create `fotoBon/uji-v7-foto` | FOTO dengan `id: "lain"` | DITOLAK | id isi = id dokumen |
| ★F7 | owner@ | create `fotoBon/uji-v7-foto` | FOTO tanpa `idBon` | DITOLAK | foto harus menunjuk bon |
| ★F8 | staf aktif | list `fotoBon` | — | DITOLAK | owner saja |

(Model CI juga menolak `base64` di atas 960.000 huruf — terlalu panjang untuk diketik di Playground.)

## K · kasir@ dipangkas (kasir darurat saja)

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★K1 | kasir@ | create `perangkatStatus/d-uji` | `{ id: "d-uji", aplikasi: "darurat", pada: "2026-10-09T03:00:00Z" }` | LOLOS | denyut HP penjaga |
| ★K2 | kasir@ | get `ringkasanKasir/aktif` | — | LOLOS | katalog kasir darurat |
| ★K3 | kasir@ | create `piutangMutasi/uji-v7-k` | `{ id: "uji-v7-k", tipe: "bayar", tanggal: <hari ini>, nominal: 1000 }` | DITOLAK | v7: dicabut (kasir.html pensiun) |
| ★K4 | kasir@ | create `stokBahanLiteran/uji-v7-k` | `{ id: "uji-v7-k", tipe: "pakai", tanggal: <hari ini>, jumlah: 1 }` | DITOLAK | v7: dicabut |
| ★K5 | kasir@ | create `logAktivitas/uji-v7-k` | `{ id: "uji-v7-k", aksi: "tulis" }` | DITOLAK | v7: dicabut |
| ★K6 | kasir@ | get `pengaturan/aksesKasir` | — | DITOLAK | v7: dicabut |
| ★K7 | kasir@ | get `pengaturan/keamanan` | — | DITOLAK | PIN owner: owner saja |

## R · regresi singkat

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★R1 | owner@ | create `penjualan/uji-v7-r1` | `{ id: "uji-v7-r1", tanggal: <hari ini>, hargaTotal: 1000 }` | LOLOS | tulisan biasa owner tidak berubah |
| ★R2 | staf aktif | create `penjualan/uji-v7-r2` | `{ id: "uji-v7-r2", tanggal: <hari ini>, hargaTotal: 1000, caraBayar: "Tunai", olehUid: "<uid staf>" }` | LOLOS | nota staf tidak berubah |
| ★R3 | staf aktif | get `penjualan/uji-v7-nota` | — | LOLOS | staf membaca nota |

## P · pintu tutup buku (U3 kunci uji `2021-12`, U5 pintu 2021 terbuka)

Isi "PEMBUKA BARU": isi U10 dengan `id: "uji-v7-pb-baru"`. Isi "PINTU": `{ id: "pintuBuku", tahun: 2021, status: "berjalan", sampai: <timestamp BESOK jam
yang sama> }` (pilih tanggal besok di pemilih tanggal *timestamp*).

| No | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★P1 | owner@ | delete `penjualan/uji-v7-lama` | — | LOLOS | arsip: salinannya ada (U8) |
| ★P2 | owner@ | create `piutangMutasi/uji-v7-pb-baru` | PEMBUKA BARU | LOLOS | saldo pembuka tahun pintu, bertanggal bulan terkunci |
| ★P3 | owner@ | delete `piutangMutasi/uji-v7-pembuka` | — | LOLOS | tarik saldo pembuka saat Batalkan |
| ★P4 | owner@ | create `penjualan/uji-v7-pulih` | `{ id: "uji-v7-pulih", tanggal: "2021-03-01", hargaTotal: 500 }` | LOLOS | Batalkan: kembali dari arsip (U9), isi sama |
| ★P5 | owner@ | update `pengaturan/titikKas` (dokumen nyata) | `tanggal: "2021-12-31"` | LOLOS | titik kas 31 Des tahun pintu |
| ★P6 | owner@ | create `pengaturan/pintuBuku` | PINTU | LOLOS | membuka pintu (berita acara U4 terkunci, ≤ 72 jam) |
| ★P7 | owner@ | update `pengaturan/pintuBuku` | `status: "tutup"` | LOLOS | menutup pintu kapan saja |
| ★P8 | owner@ | delete `penjualan/uji-v7-tanpa` | — | DITOLAK | tidak ada salinan arsipnya |
| ★P9 | owner@ | update `penjualan/uji-v7-lama` | `hargaTotal: 2000` | DITOLAK | pintu tidak membuka UBAH |
| ★P10 | owner@ | create `penjualan/uji-v7-baru2` | `{ id: "uji-v7-baru2", tanggal: "2021-06-20", hargaTotal: 1000 }` | DITOLAK | catatan biasa di bulan terkunci |
| ★P11 | owner@ | create `piutangMutasi/uji-v7-pb-lain` | isi U10 dengan `id: "uji-v7-pb-lain"`, `tahunDari: 2020` | DITOLAK | saldo pembuka tahun LAIN |
| ★P12 | owner@ | create `piutangMutasi/uji-v7-pb-tanpa` | isi U10 dengan `id: "uji-v7-pb-tanpa"` TANPA `tutupBuku` | DITOLAK | bukan saldo pembuka |
| ★P13 | owner@ | create `penjualan/uji-v7-pulih` | seperti ★P4 dengan `hargaTotal: 600` | DITOLAK | isi beda dari salinan arsip |
| ★P14 | kasir@ | create `piutangMutasi/uji-v7-pb-baru` | PEMBUKA BARU | DITOLAK | pintu owner saja |
| ★P15 | staf aktif | delete `penjualan/uji-v7-lama` | — | DITOLAK | pintu owner saja |
| ★P16 | owner@ | create `pengaturan/pintuBuku` | PINTU dengan `sampai` = 5 hari lagi | DITOLAK | lebih dari 72 jam |
| ★P17 | owner@ | create `pengaturan/pintuBuku` | PINTU dengan `tahun: <tahun ini>` | DITOLAK | tahun berjalan tidak ditutup |
| ★P18 | owner@ | create `pengaturan/pintuBuku` | PINTU dengan `tahun: 2020` | DITOLAK | tidak ada berita acara 2020 |
| ★P19 | owner@ | **TERAKHIR**: di tab Data ubah U5 `sampai` → 1 Jan 2020, lalu ulang ★P1 | — | DITOLAK | pintu kedaluwarsa |

Model CI juga menilai (tidak perlu di Playground): pintu berstatus `tutup` walau `sampai` jauh (M-P20), tanpa dokumen pintu (M-P21), catatan bertanggal
SESUDAH tahun pintu (M-P22, M-P25), `pindahUang` tidak berpintu (M-P23), titik kas mundur ke tahun sesudah pintu (M-P24), ubah catatan terkunci jadi sama
dengan salinannya (M-P26), pintu tahun berjalan walau berita acaranya ada (M-P27), foto bon kebesaran (M-F9).

## Hasil Playground

(diisi saat owner menjalankannya: tanggal · ★A/B/N/F/K/R/P sesuai kolom Wajib · dokumen uji U1–U10 dihapus, `aturanToko/kunciPeriode` tidak ada · Publish
jam berapa · kepala versi aktif dibaca)
