# Uji rules v6 di server — berita acara tutup buku hanya maju (DRAF, belum terbit)

`alat-uji/periksa_rules.py` memeriksa **bentuk** rules di CI, dan untuk v6 juga menilai fungsi rules `tutupBukuAcara` APA ADANYA (diterjemahkan ke
Python) pada semua kasus di bawah — itu model, bukan server. Berkas ini untuk **perilaku server**: kasus yang dijalankan owner di **Rules Playground**
(Console › Firestore › Rules), dengan v6 di EDITOR proyek toko, **sebelum** v6 diterbitkan. Claude Code tidak memegang sandi dan tidak mengetik apa pun
di Console; Claude hanya MEMBACA Console lewat Chrome owner di langkah yang disebut. Rules = TUGAS OWNER; berkas `firestore.rules` di repo hanya draf
kanonik sampai owner menekan **Publish**. Kasus v5 ada di `docs/uji-rules-v5.md`, v4 di `docs/uji-rules-v4.md`.

## Yang berubah v5 → v6

Hanya **update** `tutupBukuAcara` (berita acara tutup buku per tahun) + enam fungsi kecil tepat di atas bloknya. Baca, create, delete tetap owner saja,
blok lain byte-sama dengan v5 (`git diff firestore.rules.v5 firestore.rules` = kepala berkas + blok ini saja).

- **Satu percobaan tutup buku** ditandai jam paraf/kunci (`paraf.pada`, ditulis `toISOString()`: selalu 24 huruf, berakhiran `Z`, jadi urutan huruf =
  urutan waktu). Jam itu sama di semua tulisan satu percobaan dan baru tiap kali tutup buku dimulai lagi.
- Dalam satu percobaan status **hanya maju**: `berjalan → terkunci → selesai`, atau `berjalan / terkunci → membatalkan → dibatalkan`. Satu-satunya
  langkah "mundur" yang sah: `dibatalkan → membatalkan` (sisa saldo pembuka mendarat belakangan, ditarik lagi) — jam batalnya harus sama.
- **Percobaan baru** hanya di atas `dibatalkan`, dimulai `berjalan` (banyak kiriman) atau langsung `terkunci` (satu kiriman), dan jam mulainya harus
  lebih baru dari percobaan yang dibatalkan.
- **Pemegang** (perangkat yang memulai) tidak berganti, kecuali lewat ambil alih (status sama, `pemegangLama` = pemegang sekarang, jam ambil alih lebih
  baru) atau pembatalan lanjutan dari `dibatalkan`.
- **Kirim ulang identik** (isi baru = isi lama, `tulisUlangSama()`) selalu boleh — SDK bisa mengulang mutasi yang jawabannya hilang (mis. `selesai` /
  `dibatalkan` sudah masuk server tapi sinyal putus); tidak mengubah apa pun.
- Tanpa `get()`: 0 access call tambahan; kiriman tutup buku tetap ≤ 18 pemeriksaan.

Kenapa (`docs/rancangan-tutup-buku-bertahap.md` §11): kiriman yang tertahan di antrean Firestore perangkat lain bisa mendarat belakangan dan menimpa
berita acara — (1) jalan MULAI: kiriman pertama tertahan di HP A, owner menuntaskan di Mac B sampai `selesai`, HP A hidup lagi → `selesai` mundur;
(2) ambil alih: HP lama masih menyimpan kiriman; (3) ekor pembatalan HP beku menulis `dibatalkan` di atas percobaan baru yang `selesai`. Di v6 tulisan
berita acara itu DITOLAK server (untuk (3) hanya berita acaranya — pengembalian arsip tetap mendarat, lihat "Batas yang diketahui"); karena kiriman tutup buku satu writeBatch, saldo pembuka yang ikut di kiriman itu juga tidak masuk (tidak ada "setengah").

**Mundur** = tempel `firestore.rules.v5` (berita acara kembali owner-saja tanpa urutan; kiriman telat bisa menimpa lagi).

**Kapan**: tidak mendesak — berita acara hanya ditulis saat tutup buku sungguhan (paling cepat sesudah 31 Des 2026). v6 harus sudah terbit **sebelum**
owner menekan "Kunci tahun 2026".

**Jam perangkat**: setelan waktu HP / Mac harus **otomatis**. v6 membandingkan jam yang ditulis perangkat: mulai lagi sesudah dibatalkan ditolak bila
jam perangkat yang memulai lebih lambat dari jam mulai percobaan yang dibatalkan; ambil alih ditolak bila jamnya lebih lambat dari ambil alih
sebelumnya (jaraknya minimal 60 menit, jadi selisih jam kecil tidak berpengaruh).

---

## Urutan (satu per satu; jangan klik **Publish** sebelum langkah 6)

1. **Persiapan** — v5 masih yang terbit. Cek Console › Firestore › **Usage** dulu (Playground ikut kuota baca harian Spark). Console › Firestore ›
   Data (Console menulis sebagai admin, rules tidak menilai): buat **tujuh dokumen uji** di koleksi `tutupBukuAcara` (tabel di bawah). Tahun `1990`
   sengaja: aplikasi bisa menampilkan pita "Tutup buku 1990 …" selama dokumen uji ada — **jangan ketuk apa pun di pita itu**, kerjakan saat toko
   tutup, dan selesaikan langkah 1–4 dalam satu duduk.
2. **Tempel `firestore.rules`** dari cabang yang diserahkan Claude ke editor — **belum Publish**. Salin tanpa merusak huruf:
   `git show <cabang>:firestore.rules | LANG=en_US.UTF-8 pbcopy` (sesudah merge: `origin/main`). Verifikasi di editor: baris 2 berbunyi
   `ATURAN FIRESTORE v6 — … (DRAF 1 Okt 2026, BELUM TERBIT)`, ada fungsi `ubahBukuSah`, dan blok `tutupBukuAcara` punya empat baris `allow`.
3. Jalankan **Bagian A** (semua wajib LOLOS), **Bagian B** (semua wajib DITOLAK), **Bagian C** (regresi) di Playground.
4. **Owner menghapus tujuh dokumen uji** `tutupBukuAcara/uji-v6-*` di tab Data (Claude tidak boleh menghapus data). Bilang ke Claude "dokumen uji sudah
   dihapus" → Claude membuka Console › Firestore › Data lewat Chrome owner (hanya membaca) dan memastikan ketujuhnya **tidak ada**.
5. **Merge cabang** (owner bilang "merge"; Claude yang menggabung & push) dan tunggu Pages hijau. Kode aplikasi tidak berubah di cabang ini.
6. **Claude bilang "siap Publish"** (semua ★ sesuai, dokumen uji tidak ada, Pages hijau) → owner **Publish** v6. Isi editor harus persis sama dengan
   `firestore.rules` di repo. Kata "DRAF … BELUM TERBIT" di kepala diganti Claude di repo (satu commit, komentar saja) sebelum merge; owner menempel
   ulang berkas itu ke editor sebelum Publish.
7. **Sesudah terbit**: Console › Rules menampilkan versi aktif — kepala harus `v6` (Claude membaca lewat Chrome owner). Lalu **satu nota dari kasir
   darurat** (kasir@) → pastikan masuk di layar Jual `/baru/` (regresi jalur kasir@). Tidak masuk → tempel `firestore.rules.v5`.

### Isian Playground

*Simulation type* = update (kecuali disebut lain) · *Location* = `/tutupBukuAcara/<dokumen uji>` · *Authenticated* on, *Provider* password,
*Firebase UID* bebas (mis. `uid-owner-uji`), **Auth token payload** tambah `"email": "owner@tokoberasmiqbal.web.app"` (huruf kecil).
*Build document* = SEMUA kolom di baris kasus; `paraf` dan `pemegang` / `pemegangLama` = kolom **map** dengan anak `pada` / `id` (+ `nama` boleh).
Kolom lain dokumen uji boleh ikut atau tidak — hasilnya sama (diperiksa: tiap kasus menghasilkan keputusan yang sama apakah Playground mengganti
dokumen atau menggabungnya dengan dokumen lama). Semua jam diketik **persis 24 huruf**:

| Nama | Jam (ketik persis) | Arti |
|---|---|---|
| P0 | `2027-01-04T03:00:00.000Z` | jam mulai percobaan yang LEBIH LAMA |
| P1 | `2027-01-05T03:00:00.000Z` | jam mulai percobaan di dokumen uji |
| P2 | `2027-01-06T03:00:00.000Z` | jam mulai percobaan yang LEBIH BARU |
| T1 / T2 | `2027-01-05T05:00:00.000Z` / `2027-01-05T07:00:00.000Z` | jam batal (`dibatalkanPada`) |
| X0 / X1 / X2 | `2027-01-05T05:30:00.000Z` / `2027-01-05T06:00:00.000Z` / `2027-01-05T08:00:00.000Z` | jam ambil alih (`diambilAlihPada`) |

### Tujuh dokumen uji (tab Data, koleksi `tutupBukuAcara`)

Semua dokumen: `tahun: 1990` (number). `hp-a` / `mac-b` = id perangkat contoh.

| Id dokumen | Isi |
|---|---|
| `uji-v6-berjalan` | `status:'berjalan'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}` |
| `uji-v6-terkunci` | `status:'terkunci'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}` |
| `uji-v6-membatalkan` | `status:'membatalkan'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}`, `dibatalkanPada:T1` |
| `uji-v6-dibatalkan` | `status:'dibatalkan'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}`, `dibatalkanPada:T1` |
| `uji-v6-selesai` | `status:'selesai'`, `paraf:{pada:P1}`, `pemegang:{id:'mac-b'}` |
| `uji-v6-alih` | `status:'berjalan'`, `paraf:{pada:P1}`, `pemegang:{id:'mac-b'}`, `pemegangLama:{id:'hp-a'}`, `diambilAlihPada:X1` |
| `uji-v6-alih-batal` | `status:'dibatalkan'`, `paraf:{pada:P1}`, `pemegang:{id:'mac-b'}`, `pemegangLama:{id:'hp-a'}`, `diambilAlihPada:X1`, `dibatalkanPada:T2` |

## A · tulisan SAH dari kode — wajib LOLOS (owner@, v6 di editor)

| # | Dokumen uji (lama) | *Build document* (baru) | Tulisan di kode (`baru/js/layar/tutup-buku-logika.js`) |
|---|---|---|---|
| ★A1 | `uji-v6-berjalan` | `status:'terkunci'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}` | kiriman penanda: `susunKunci` (kiriman terakhir) / `lanjutBuku` |
| ★A2 | `uji-v6-berjalan` | `status:'membatalkan'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}`, `dibatalkanPada:T1` | `susunBatal` kiriman 1 dari `berjalan` |
| ★A3 | `uji-v6-terkunci` | seperti ★A2 | `susunBatal` kiriman 1 dari `terkunci` |
| ★A4 | `uji-v6-terkunci` | `status:'selesai'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}` | `susunSelesai` |
| ★A5 | `uji-v6-membatalkan` | `status:'membatalkan'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}`, `dibatalkanPada:T1` | `susunBatal` lanjutan |
| ★A6 | `uji-v6-membatalkan` | `status:'dibatalkan'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}`, `dibatalkanPada:T1` | `susunBatal` → `akhir` |
| ★A7 | `uji-v6-dibatalkan` | `status:'membatalkan'`, `paraf:{pada:P1}`, `pemegang:{id:'mac-b'}`, `dibatalkanPada:T1` | `susunBatal` dari `dibatalkan` (P4-7, perangkat lain) |
| ★A8 | `uji-v6-dibatalkan` | `status:'berjalan'`, `paraf:{pada:P2}`, `pemegang:{id:'mac-b'}` | `susunKunci` mulai lagi (banyak kiriman) |
| ★A9 | `uji-v6-dibatalkan` | `status:'terkunci'`, `paraf:{pada:P2}`, `pemegang:{id:'mac-b'}` | `susunKunci` mulai lagi (satu kiriman) |
| ★A10 | `uji-v6-berjalan` | `status:'berjalan'`, `paraf:{pada:P1}`, `pemegang:{id:'mac-b'}`, `pemegangLama:{id:'hp-a'}`, `diambilAlihPada:X1` | `susunAmbilAlih` |
| ★A11 | `uji-v6-terkunci` | seperti ★A10 tetapi `status:'terkunci'` | `susunAmbilAlih` |
| ★A12 | `uji-v6-membatalkan` | seperti ★A10 tetapi `status:'membatalkan'`, + `dibatalkanPada:T1` | `susunAmbilAlih` |
| ★A13 | `uji-v6-alih` | `status:'terkunci'`, `paraf:{pada:P1}`, `pemegang:{id:'mac-b'}`, `pemegangLama:{id:'hp-a'}`, `diambilAlihPada:X1` | pemegang baru melanjutkan (`lanjutBuku`) |
| ★A14 | `uji-v6-alih` | `status:'berjalan'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}`, `pemegangLama:{id:'mac-b'}`, `diambilAlihPada:X2` | ambil alih kedua |
| ★A15 | *create* `/tutupBukuAcara/uji-v6-baru` (dokumen TIDAK ada) | `status:'berjalan'`, `tahun:1990`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}` | `susunKunci` pertama kali (create tetap owner) |
| ★A16 | `uji-v6-selesai` | isi PERSIS sama dengan dokumen `uji-v6-selesai` (salin semua kolomnya) | kirim ulang identik di atas `selesai` |
| ★A17 | `uji-v6-dibatalkan` | isi PERSIS sama dengan dokumen `uji-v6-dibatalkan` | kirim ulang identik di atas `dibatalkan` |

## B · tulisan TELAT / MUNDUR — wajib DITOLAK (owner@, v6 di editor)

| # | Dokumen uji (lama) | *Build document* (baru) | Kejadian |
|---|---|---|---|
| ★B1 | `uji-v6-selesai` | `status:'berjalan'`, `paraf:{pada:P0}`, `pemegang:{id:'hp-a'}` | jalan MULAI: kiriman pertama HP A mendarat sesudah Mac B selesai |
| ★B2 | `uji-v6-selesai` | `status:'terkunci'`, `paraf:{pada:P0}`, `pemegang:{id:'hp-a'}` | jalan MULAI, tutup buku satu kiriman |
| ★B3 | `uji-v6-dibatalkan` | `status:'berjalan'`, `paraf:{pada:P0}`, `pemegang:{id:'mac-b'}` | percobaan LAMA mendarat di atas percobaan lebih baru yang dibatalkan |
| ★B4 | `uji-v6-dibatalkan` | `status:'terkunci'`, `paraf:{pada:P0}`, `pemegang:{id:'mac-b'}` | sama, satu kiriman |
| ★B5 | `uji-v6-berjalan` | `status:'berjalan'`, `paraf:{pada:P0}`, `pemegang:{id:'mac-b'}` | percobaan lama di atas percobaan yang sedang berjalan |
| ★B6 | `uji-v6-terkunci` | seperti ★B5 | … di atas yang terkunci |
| ★B7 | `uji-v6-membatalkan` | seperti ★B5 | … di atas pembatalan |
| ★B8 | `uji-v6-selesai` | `status:'dibatalkan'`, `paraf:{pada:P0}`, `pemegang:{id:'hp-a'}`, `dibatalkanPada:T1` | ekor pembatalan HP beku di atas percobaan baru yang selesai |
| ★B9 | `uji-v6-terkunci` | `status:'dibatalkan'`, `paraf:{pada:P0}`, `pemegang:{id:'mac-b'}`, `dibatalkanPada:T1` | ekor pembatalan di atas percobaan baru yang terkunci |
| ★B10 | `uji-v6-alih` | `status:'terkunci'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}` | ambil alih: penanda HP lama mendarat sesudah Mac B mengambil alih |
| ★B11 | `uji-v6-alih-batal` | seperti ★B10 | ambil alih: penanda HP lama sesudah Mac B membatalkan tuntas (repro §11 E1, dulu fase `rusak`) |
| ★B12 | `uji-v6-alih-batal` | `status:'membatalkan'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}`, `dibatalkanPada:T1` | pembatalan HP lama (jam batalnya sendiri) di atas pembatalan Mac B yang tuntas |
| ★B13 | `uji-v6-alih` | `status:'membatalkan'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}`, `dibatalkanPada:T1` | pembatalan HP lama di atas tutup buku yang dipegang Mac B |
| ★B14 | `uji-v6-alih` | `status:'berjalan'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}`, `pemegangLama:{id:'mac-b'}`, `diambilAlihPada:X0` | ambil alih LAMA mendarat sesudah ambil alih yang lebih baru |
| ★B15 | `uji-v6-berjalan` | `status:'berjalan'`, `paraf:{pada:P1}`, `pemegang:{id:'mac-b'}` | ganti pemegang tanpa ambil alih |
| ★B16 | `uji-v6-selesai` | `status:'terkunci'`, `paraf:{pada:P1}`, `pemegang:{id:'mac-b'}` | `selesai` mundur jadi `terkunci` |
| ★B17 | `uji-v6-selesai` | `status:'membatalkan'`, `paraf:{pada:P1}`, `pemegang:{id:'mac-b'}`, `dibatalkanPada:T1` | tahun yang selesai dibatalkan |
| ★B18 | `uji-v6-dibatalkan` | `status:'terkunci'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}`, `dibatalkanPada:T1` | penanda telat sesudah pembatalan tuntas (pemegang sama) |
| ★B19 | `uji-v6-dibatalkan` | seperti ★B18 tetapi `status:'berjalan'` | kiriman pertama telat sesudah pembatalan tuntas |
| ★B20 | `uji-v6-terkunci` | `status:'berjalan'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}` | `terkunci` mundur jadi `berjalan` |
| ★B21 | `uji-v6-membatalkan` | `status:'terkunci'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}`, `dibatalkanPada:T1` | pembatalan tertimpa penanda |
| ★B22 | `uji-v6-membatalkan` | seperti ★B21 tetapi `status:'berjalan'` | pembatalan tertimpa kiriman pertama |
| ★B23 | `uji-v6-selesai` | `status:'berjalan'`, `paraf:{pada:P2}`, `pemegang:{id:'mac-b'}` | tahun yang selesai dibuka lagi dengan percobaan baru |
| ★B24 | `uji-v6-terkunci` | seperti ★B23 | percobaan baru di atas percobaan yang masih terkunci |
| ★B25 | `uji-v6-dibatalkan` | `status:'berjalan'`, `paraf:{pada:'2027-01-06'}`, `pemegang:{id:'mac-b'}` | jam mulai bukan bentuk `toISOString` |
| ★B26 | `uji-v6-berjalan` | `status:'ditutup'`, `paraf:{pada:P1}`, `pemegang:{id:'hp-a'}` | status asing |
| ★B27 | `uji-v6-berjalan` — akun **kasir@** (`"email": "kasir@tokoberasmiqbal.web.app"`) | seperti ★A1 | bukan owner (tidak berubah dari v5) |

## C · regresi (v6 di editor)

| # | Akun | Operasi · jalur · isi | Wajib |
|---|---|---|---|
| ★C1 | owner@ | get `/tutupBukuAcara/uji-v6-berjalan` | LOLOS |
| ★C2 | kasir@ | get `/tutupBukuAcara/uji-v6-berjalan` | **DITOLAK** |
| ★C3 | owner@ | delete `/tutupBukuAcara/uji-v6-selesai` (Playground tidak benar-benar menghapus) | LOLOS (delete sama dengan v5) |
| ★C4 | kasir@ | create `/penjualan/uji-v6-c4` `{id:'uji-v6-c4', tanggal:'<hari ini WIB>', jam:'10:00'}` | LOLOS (jalur kasir darurat, sama dengan v5) |

Satu saja ★ yang meleset = **jangan Publish**; kirim nomornya ke Claude Code. "Error running simulation … " = DITOLAK di server (bukan lolos).

## Batas yang diketahui (dicatat, bukan syarat Publish)

- **Kasus model M1, M2** (berita acara TANPA pemegang: perangkat tanpa id, data uji lama) tidak diulang di Playground — dokumen uji di atas semuanya
  berpemegang. Model di CI menilainya LOLOS.
- **V1 — pembatalan yang sama, jam batal sama.** HP A memulai pembatalan (jam batal T1 sudah tercatat di server), lalu beku dengan satu kiriman
  `membatalkan` lanjutan di antreannya; Mac B mengambil alih dan menuntaskan pembatalan (`dibatalkan`, jam batal tetap T1). Kiriman HP A mendarat →
  LOLOS (bentuknya sama dengan ★A7, pembatalan lanjutan yang sah): status kembali `membatalkan` dengan pemegang HP A. Angka tidak salah (yang ditarik
  memang sudah ditarik); pita menyebut "pembatalan belum selesai" dan menuntun ke perangkat itu / ambil alih lagi.
- **Yang TIDAK dijaga v6** (koleksi lain, rules owner-saja seperti v5): pemindahan & pengembalian arsip (`arsipTahun` dan dokumen yang dikembalikan
  `pulihkanArsip` ke koleksi asalnya), kiriman saldo pembuka di TENGAH (kiriman tanpa berita acara), `pengaturan/tutupBuku`, `pengaturan/titikKas`,
  `pengaturan/periksaArsip<tahun>`. Kiriman saldo pembuka di tengah (tanpa berita acara) dari HP lama yang mendarat sesudah diambil alih: selama
  tahun itu `berjalan` / `membatalkan` / `dibatalkan` saldo pembuka itu tersembunyi (toko.js `pembukaBerlaku`) dan pita "batal" menyebutnya untuk
  ditarik; tetapi kalau percobaan yang lebih baru sudah `terkunci` / `selesai`, saldo pembuka telat itu IKUT TERHITUNG (dobel) dan tidak ada pita yang
  menyebutnya. Pelindungnya tetap kalimat peringatan ambil alih ("pastikan HP lama mati / datanya dihapus").
- **Ekor pembatalan HP beku — v6 hanya menolak berita acaranya** (tinjauan rules v6, TRV6-EKOR-1). `uang.js` jalankanBatal mengembalikan arsip
  (`pulihkanArsip`, lalu `bacaArsipTahun` = SELURUH arsip tahun itu, lalu kembalikan sisanya) SEBELUM menulis `dibatalkan`, dan langkah itu tidak
  memeriksa pemegang/status lagi. HP A yang beku di tengah pengembalian lalu hidup lagi sesudah Mac B mengambil alih, memulai percobaan baru dan
  menuntaskannya sampai `selesai`: HP A mengembalikan seluruh arsip tahun itu (termasuk arsip percobaan baru) ke buku hidup; baru `dibatalkan`-nya
  ditolak v6. Hasil: berita acara tetap `selesai`, catatan tahun lama hidup lagi DI SAMPING saldo pembuka → angka DOBEL tanpa pita. (Di v5 hasilnya
  `dibatalkan` + dobel.) Pelindungnya kalimat peringatan ambil alih ("pastikan HP lama mati / datanya dihapus"). Perbaikan kode (penjaga pemegang &
  status sebelum / di antara potongan pengembalian arsip) = putaran terpisah, bukan rules.
- **Hapus lalu tulis baru**: delete berita acara tetap boleh owner (aplikasi tidak pernah menghapusnya). Kalau dokumen dihapus, tulisan telat yang
  mendarat sesudahnya = create = LOLOS.
- **Jam perangkat yang salah besar.** Percobaan yang dimulai dari perangkat berjam jauh di depan lalu dibatalkan membuat percobaan berikut dari perangkat
  berjam benar DITOLAK (jam mulainya "lebih lama"). Jalan keluar: owner menghapus berita acara `dibatalkan` itu di Console › Data (admin), sesudah
  memastikan pitanya tidak menyebut sisa saldo pembuka.

## Kalau sesudah v6 terbit tutup buku DITOLAK

Kabar layar K6 menyebut kiriman ke-n "tulis ditolak: permission-denied" dan salinannya ada di Menu › Sistem › Perangkat (ditolak server). **Jangan
tulis ulang kiriman tutup buku yang ditolak** dan jangan ketuk berulang-ulang: kirim kalimat kabar itu ke Claude Code. Penyebab yang diharapkan =
kiriman yang memang telat (perangkat lain / percobaan lama) — itu yang dijaga v6. Penyebab lain (mis. jam perangkat) dibereskan dulu; bila perlu tempel
`firestore.rules.v5`.

## Hasil Playground

2 Okt 2026 dini hari, Claude lewat Chrome owner (atas permintaan owner "lu aja yang kerjain"; owner menempel v6 ke editor, belum Publish). Isi editor
dicocokkan 3× dengan `firestore.rules` cabang ini (sidik `shasum` a083e3fa13bc = commit d97f03e; kepala berkas lalu diganti dari "DRAF … BELUM TERBIT",
komentar saja). Akun simulasi: owner@ (B27: kasir@). Dokumen uji di `tutupBukuAcara`: `uji-v6-berjalan`, `-terkunci`, `-dibatalkan`, `-selesai`,
`-alih` (tahun 1990; tanpa `uji-v6-membatalkan` & `uji-v6-alih-batal`).

| Bagian | Kasus | Hasil |
|---|---|---|
| A (wajib LOLOS) | ★A1 berjalan→terkunci · ★A2 berjalan→membatalkan · ★A4 terkunci→selesai · ★A7 dibatalkan→membatalkan pemegang lain · ★A10 ambil alih · ★A13 pemegang baru lanjut · ★A14 ambil alih kedua · ★A16 kirim ulang identik `selesai` · ★A17 kirim ulang identik `dibatalkan` | 9/9 LOLOS |
| B (wajib DITOLAK) | ★B1 percobaan lama di atas `selesai` · ★B10 penanda HP lama sesudah ambil alih · B12′ jam batal lain di atas `dibatalkan` · ★B14 ambil alih lama · ★B15 ganti pemegang tanpa ambil alih · ★B16 selesai→terkunci · ★B17 selesai→membatalkan · ★B19 dibatalkan→berjalan · ★B20 terkunci→berjalan · ★B26 status asing · ★B27 kasir@ | 11/11 DITOLAK |
| C | ★C1 owner@ baca berita acara | LOLOS |

**Sifat Playground yang ditemukan (bukan sifat server):**
- *update* = dokumen lama DIGABUNG dengan isian *Build document* (kolom yang tidak diisi diambil dari dokumen lama). Kasus diisi kolom yang berubah saja.
- Teks berbentuk jam ISO (`…T03:00:00.000Z`) diubah Playground menjadi *timestamp* — di isian MAUPUN di dokumen lama yang dibaca dari Data (panel
  *resource* menampilkan `2027-01-05T03:00:00Z`). Perbandingan jam ISO lalu galat (`timestamp > string`). Di server, kolom itu teks (ditulis
  `toISOString()` oleh aplikasi), jadi uji urutan jam memakai teks jam BUKAN ISO (`2027-01-05 06:00`) dengan perbandingan teks yang sama.
- Akibatnya jalur **mulai lagi sesudah `dibatalkan`** (★A8/★A9/★B3/★B25: `paraf.pada` wajib bentuk ISO 'Z' + lebih baru) TIDAK bisa diuji jujur di
  Playground; buktinya hanya model `periksa_rules.py` (CI). Jalur ini hanya dipakai sesudah satu percobaan tutup buku dibatalkan.
- Tidak diuji di Playground: ★A3, ★A5, ★A6, ★A11, ★A12, ★A15, ★B2–B9 (selain B10), ★B11, ★B12, ★B13, ★B18, ★B21–B24, ★C2–C4 — dinilai model CI;
  blok koleksi lain byte-sama v5 (jalur kasir@ tidak berubah).
- Tab Console yang tersembunyi (jendela tertutup) membuat dialog *Build document* tertahan; hasil dihitung hanya bila isian terbaca benar di pratinjau
  data DAN banner hasilnya baru (bukan "viewing outdated simulation").
