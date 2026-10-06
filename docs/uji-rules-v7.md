# Uji rules v7 di server — hemat baca: kirim ulang kasir@ bercap + batu nisan (DRAF 7 Okt 2026, belum terbit)

`alat-uji/periksa_rules.py` memeriksa **bentuk** rules di CI (v7 = v6 + dua tambahan, selebihnya sama dengan `firestore.rules.v6` tanpa komentar).
Berkas ini untuk **perilaku server**: kasus yang dijalankan owner di **Rules Playground** (Console › Firestore › Rules) dengan v7 di EDITOR, sebelum
Publish. Claude Code tidak memegang sandi dan tidak mengetik di Console; Claude hanya MEMBACA Console lewat Chrome owner pada langkah yang disebut.
Rules = TUGAS OWNER. Kasus v6 tetap di `docs/uji-rules-v6.md`.

## Yang berubah v6 → v7 (HANYA menambah)

1. Fungsi `ulangKasirBercap()` = isi baru sama persis dengan isi lama kecuali `capServer`, dan `capServer == request.time`. Dipakai SATU tempat: suku
   `(kasir() && ulangKasirBercap())` di `allow update` **penjualan**. Kasir darurat `kasir-v33` mengirim nota lewat REST `:commit` dengan transform
   `capServer = REQUEST_TIME`; kalau jawaban server hilang (sinyal putus) lalu karcis dikirim ulang, isinya sama tetapi `capServer` berbeda — di v6 itu
   DITOLAK (`tulisUlangSama`) dan karcis pindah ke daftar "ditolak" padahal sudah masuk.
2. Blok `batuNisan/{id}`: read & delete owner; create/update owner **dan** `capServer == request.time`. `/baru/` menulis satu batu nisan per catatan
   koleksi hemat yang dihapus, di writeBatch yang sama dengan hapusnya. Tanpa blok ini rules v6 menolak SELURUH batch (hapus tidak jalan).

Tidak berubah: create penjualan kasir@ (`capServer` boleh ada atau tidak — HP yang masih v32 tetap masuk), stokBahanLiteran & piutangMutasi kasir@ (tetap
tulis-ulang identik), semua aturan staf, tutupBukuAcara, perangkatStatus, aturanToko. Tanpa `get()` baru: access call tidak bertambah.

**Kode aman sebelum v7 terbit**: `/baru/` baru menulis batu nisan sesudah owner TERBUKTI bisa membaca `batuNisan` (aturan v7) di perangkat itu — sebelum
itu hapus berjalan seperti dulu. Yang belum aman: **kasir darurat kasir-v33** (kirim ulang karcis yang sama ditolak v6). Karena itu v7 diterbitkan
**sebelum** cabang `perbaikan/hemat-baca` digabung.

**Mundur**: JANGAN tempel `firestore.rules.v6` selama kode bercap berjalan (hapus /baru/ ber-batu nisan & kirim ulang karcis kasir-v33 ditolak). Mundur
hemat baca = saklar (Menu › Sistem › Perangkat › Hemat baca, atau `/baru/?hemat=mati`). v6 hanya boleh ditempel balik sesudah kode bercap dibalik.

## Urutan

1. Cek Console › Firestore › **Usage** dulu (Playground ikut kuota baca Spark; kerjakan sesudah 14.00 WIB bila kuota hari itu menipis).
2. **Tempel `firestore.rules`** dari cabang ke editor — **belum Publish**: `git show perbaikan/hemat-baca:firestore.rules | LANG=en_US.UTF-8 pbcopy`.
   Verifikasi: kepala berbunyi `ATURAN FIRESTORE v7`, ada fungsi `ulangKasirBercap`, ada blok `match /batuNisan/{id}` dengan tiga baris `allow`.
3. Jalankan **A** (wajib LOLOS), **B** (wajib DITOLAK), **C** (regresi = suite ★ `docs/uji-rules-v6.md` bagian A–C, diulang dengan v7 di editor).
4. **Publish** (owner). Claude membaca Console › Rules lewat Chrome owner: kepala versi aktif = `v7`.
5. Sesudah terbit: satu nota dari kasir darurat yang MASIH v32 masuk (create tanpa cap tetap boleh) → lihat di Jual `/baru/`.
6. Baru sesudah itu cabang digabung (owner bilang "merge"). HP penjaga dibuka sekali sampai bilah atas berbunyi **"versi 7 Okt"** (kasir-v33).

### Isian Playground

*Authenticated* on, provider password, *Firebase UID* bebas. **Auth token payload** tambah `"email": "kasir@tokoberasmiqbal.web.app"` (kasus kasir@)
atau `"owner@tokoberasmiqbal.web.app"` (kasus owner), huruf kecil. Untuk staf: email lain + dokumen `aksesAkun/<uid>` contoh seperti di uji v6.

Dokumen uji (tab Data, dibuat owner sebagai admin; **hapus lagi sesudahnya**): `penjualan/uji-v7-nota` = `{ id: "uji-v7-nota", tanggal: <hari ini
YYYY-MM-DD>, hargaTotal: 1000, namaProduk: "Contoh" }` (tanpa capServer).

> **Batas Playground**: `request.time` di Playground = jam simulasi; Playground tidak bisa mengisi kolom dengan transform server. Kasus yang menuntut
> `capServer == request.time` hanya bisa dibuktikan DITOLAK (nilai ketikan ≠ jam server). Bukti "diterima" = langkah 5–6 (nota sungguhan) dan, untuk batu
> nisan, hapus pertama dari `/baru/` sesudah merge (Menu › Sistem › Perangkat › Antrean: tidak ada kiriman ditolak).

## A · wajib LOLOS (v7 di editor)

| No | Siapa | Operasi & lokasi | Isi | Kenapa |
|---|---|---|---|---|
| ★A1 | kasir@ | create `penjualan/uji-v7-baru` | tanggal hari ini, tanpa `capServer` | HP kasir v32 tetap masuk |
| ★A2 | kasir@ | update `penjualan/uji-v7-nota` | isi SAMA PERSIS dengan dokumen uji | kirim ulang identik (v2) tetap boleh |
| ★A3 | owner@ | get `batuNisan/uji-v7` | — | owner membaca batu nisan (pendengar N) |
| ★A4 | owner@ | delete `batuNisan/uji-v7` | — | owner boleh membereskan |

## B · wajib DITOLAK

| No | Siapa | Operasi & lokasi | Isi | Kenapa |
|---|---|---|---|---|
| ★B1 | kasir@ | update `penjualan/uji-v7-nota` | isi dokumen uji + `hargaTotal: 2000` + `capServer` (timestamp ketikan) | kirim ulang yang mengubah isi selain cap |
| ★B2 | kasir@ | update `penjualan/uji-v7-nota` | isi dokumen uji + `capServer` = timestamp **ketikan** (bukan jam server) | cap dari jam HP tidak diterima |
| ★B3 | kasir@ | update `stokBahanLiteran/<dokumen apa pun>` | isi sama + `capServer` | kirim ulang bercap HANYA di penjualan |
| ★B4 | staf aktif | get `batuNisan/uji-v7` | — | staf tidak membaca batu nisan |
| ★B5 | staf aktif | create `batuNisan/uji-v7` | `{ capServer: <timestamp> }` | staf tidak menulis batu nisan |
| ★B6 | owner@ | create `batuNisan/uji-v7` | `{ id: "penjualan|x", koleksi: "penjualan", idDok: "x", capServer: <timestamp ketikan> }` | cap nisan wajib jam server |
| ★B7 | kasir@ | get `batuNisan/uji-v7` | — | kasir@ tidak membaca batu nisan |

## C · regresi

Ulangi suite ★ `docs/uji-rules-v6.md` (A, B, C) dengan v7 di editor — semuanya wajib sama hasilnya (v7 tidak menyentuh aturan lain; diperiksa juga
statis: `periksa_rules.py` menuntut isi selain dua tambahan sama dengan `firestore.rules.v6`).

## Hasil Playground

(diisi saat owner menjalankannya: tanggal, ★A1–A4 lolos, ★B1–B7 ditolak, regresi v6 sama, Publish jam berapa, kepala versi aktif dibaca Claude)
