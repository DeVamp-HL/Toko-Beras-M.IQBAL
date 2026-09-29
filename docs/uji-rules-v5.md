# Uji rules v5 di server — putaran 39 (karyawan menuang & mengecek wadah literan)

`alat-uji/periksa_rules.py` memeriksa **bentuk** rules (statis, di CI). Berkas ini untuk **perilaku server**: kasus yang dijalankan owner di
**Rules Playground** (Console › Firestore › Rules), dengan v5 di EDITOR proyek toko, **sebelum** v5 diterbitkan. Claude Code tidak memegang sandi
dan tidak mengetik apa pun di Console; Claude hanya MEMBACA Console lewat Chrome owner di langkah yang disebut. Kasus v4 (kunci periode) ada di
`docs/uji-rules-v4.md`, v3 (akun & peran) di `docs/uji-rules-v3.md`.

**Yang berubah v4 → v5** (kepala `firestore.rules`, `docs/peta-hak-akses.md` §9): `wadahLiteran` create oleh `ben` / `karyawan` hanya tipe
`takar` · `karung` · `karungIsi` · `cek` (`stafBuatWadah`); `batchMasuk` create oleh `ben` / `karyawan` hanya batch LAHIR BUKU 0 kg (`stafBuatLahir`:
`lahirBuku`, `stokAwal`, `biayaBongkar == 0`, `pemasok == 'LAHIR BUKU'`, `tglStaf`). `olehUid` wajib, tanpa update / delete. Selebihnya byte-sama
dengan v4. **Mundur** = tempel `firestore.rules.v4` (karyawan tidak bisa menuang / mengecek dari akunnya; kirimannya masuk daftar ditolak).

Rules Playground membaca data sungguhan lewat `get()`: kasus peran butuh dokumen `aksesAkun/{uid}` yang SUDAH ADA. "Error running simulation … Null
value error" = DITOLAK di server (bukan lolos). Playground tidak mengubah apa pun di database, tetapi ikut kuota baca harian (Spark) — cek
Console › Firestore › **Usage** dulu.

---

## Urutan (satu per satu; jangan klik **Publish** sebelum langkah 6)

1. **Persiapan** — v4 masih yang terbit. Console › Firestore › Data (Console menulis sebagai admin, rules tidak menilai): buat tiga dokumen uji
   - `aksesAkun/uid-uji-k` = `{uid:'uid-uji-k', nama:'UJI K', email:'uji.k@contoh.com', peran:'karyawan', aktif:true}`
   - `aksesAkun/uid-uji-b` = `{uid:'uid-uji-b', nama:'UJI B', email:'uji.b@contoh.com', peran:'ben', aktif:true}`
   - `aksesAkun/uid-uji-n` = `{uid:'uid-uji-n', nama:'UJI N', email:'uji.n@contoh.com', peran:'karyawan', aktif:false}`

   Catat juga keadaan `aturanToko/kunciPeriode` (ada bulan terkunci atau tidak) — hanya mempengaruhi ★A17.
2. **Tempel `firestore.rules`** (repo, cabang putaran 39 yang akan di-merge) ke editor — **belum Publish**. Verifikasi di editor: baris 2 berbunyi
   `ATURAN FIRESTORE v5 — … (putaran 39, 29 Sep 2026)`, ada fungsi `stafBuatWadah` dan `stafBuatLahir`, blok `wadahLiteran` & `batchMasuk` memanggilnya.
3. **Bagian A** (karyawan & ben), **Bagian B** (owner tetap semua), **Bagian C** (regresi v4 / v3) di Playground.
4. **Owner menghapus tiga dokumen uji `aksesAkun/uid-uji-*`** di tab Data (Claude tidak boleh menghapus data). **Bilang ke Claude "dokumen uji sudah
   dihapus"** → Claude membuka Console › Firestore › Data lewat Chrome owner (hanya membaca) dan memastikan ketiganya **tidak ada**.
5. **Merge cabang putaran 39** (owner bilang "merge"; Claude yang menggabung & push) dan tunggu Pages hijau. v5 boleh terbit sebelum atau sesudah
   `/baru/` versi ini live — akun karyawan belum ada (gerbang tablet), jadi tidak ada kiriman yang menunggu v5.
6. **Claude bilang "siap Publish"** (semua ★ sesuai, dokumen uji tidak ada, Pages hijau) → owner **Publish** v5. Isi editor harus persis sama dengan
   `firestore.rules` di repo.
7. **Sesudah terbit**: Console › Rules menampilkan versi yang aktif — kepala harus `v5` (Claude membaca lewat Chrome owner). Lalu **satu nota dari kasir
   darurat** (kasir@) → pastikan masuk di layar Jual `/baru/` (regresi jalur kasir@). Tidak masuk → tempel `firestore.rules.v4`.

Isian Playground seperti v3/v4: *Simulation type* = get / create / update / delete · *Location* = jalur dokumen · *Authenticated* on, *Provider*
password, *Firebase UID* = uid akun, **Auth token payload** tambah `"email": "…"` (owner@ / kasir@ / email uji, huruf kecil). `<hari ini>` = tanggal
WIB hari uji. `<jam>` = `'10:00'`. Isian *Build document* = kolom di tabel; kolom lain (mis. `keterangan`) boleh ditambah.

## A · karyawan & ben (v5 di editor)

`K` = UID `uid-uji-k`, email `uji.k@contoh.com` · `B` = UID `uid-uji-b`, email `uji.b@contoh.com` · `N` = UID `uid-uji-n` (nonaktif).

| # | Akun | Operasi · jalur · isi (*Build document*) | Wajib |
|---|---|---|---|
| ★A1 | K | create `/wadahLiteran/uji-a1` `{id:'uji-a1', tanggal:'<hari ini>', jam:'<jam>', tipe:'takar', wadah:'UJI', takar:1, kgPerTakar:1.8, kg:1.8, takaran:'kg', sumber:[{merk:'Karung belakang UJI · MEREK', merkAsal:'MEREK', takar:1, kg:1.8, dari:'UJI'}], stokWadah:'Wadah UJI', olehUid:'uid-uji-k'}` | LOLOS (tuang) |
| ★A2 | K | create `/wadahLiteran/uji-a2` `{id:'uji-a2', tanggal:'<hari ini>', jam:'<jam>', tipe:'karung', merk:'Karung belakang UJI · MEREK', merkAsal:'MEREK', kg:50, wadah:'UJI', bukuBelakang:true, olehUid:'uid-uji-k'}` | LOLOS (karung dibuka di belakang wadah) |
| ★A3 | K | create `/wadahLiteran/uji-a3` `{id:'uji-a3', tanggal:'<hari ini>', jam:'<jam>', tipe:'karungIsi', merk:'Karung belakang UJI · MEREK', merkAsal:'MEREK', isiKg:20, wadah:'UJI', olehUid:'uid-uji-k'}` | LOLOS (samakan karung terbuka) |
| ★A4 | K | create `/wadahLiteran/uji-a4` `{id:'uji-a4', tanggal:'<hari ini>', jam:'<jam>', tipe:'cek', wadah:'UJI', hasil:'sesuai', bukuKg:40, olehUid:'uid-uji-k'}` | LOLOS (cek tutup toko) |
| ★A5 | K | create `/wadahLiteran/uji-a5` `{id:'uji-a5', tanggal:'<hari ini>', jam:'<jam>', tipe:'atur', daftar:['UJI'], penuhKg:50, olehUid:'uid-uji-k'}` | **DITOLAK** (aturan wadah = owner) |
| ★A6 | K | create `/wadahLiteran/uji-a6` `{id:'uji-a6', tanggal:'<hari ini>', jam:'<jam>', tipe:'isi', wadah:'UJI', isiKg:50, olehUid:'uid-uji-k'}` | **DITOLAK** (titik samakan isi = owner) |
| ★A7 | K | seperti ★A1 tetapi **tanpa** `olehUid` (id `uji-a7`) | **DITOLAK** (`jujur()`) |
| ★A8 | K | seperti ★A1 tetapi `olehUid:'uid-uji-b'` (id `uji-a8`) | **DITOLAK** (uid orang lain) |
| ★A9 | K | update `/wadahLiteran/<dokumen takar nyata mana pun>`: `kg` diubah | **DITOLAK** (update = owner) |
| ★A10 | K | delete `/wadahLiteran/<dokumen nyata yang sama>` | **DITOLAK** (delete = owner) |
| ★A11 | K | create `/batchMasuk/uji-a11` `{id:'uji-a11', tanggal:'<hari ini>', jam:'<jam>', pemasok:'LAHIR BUKU', caraBayar:'tunai', biayaBongkar:0, stokAwal:true, lahirBuku:true, merkList:[{id:'1', merk:'Karung belakang UJI · MEREK', satuan:'lahir', beratKarung:0, jumlahKarung:0, totalKg:0, hargaPerKg:0, subtotalHarga:0, karungBelakang:'UJI', merkAsal:'MEREK'}], olehUid:'uid-uji-k'}` | LOLOS (batch lahir buku 0 kg) |
| ★A12 | K | create `/batchMasuk/uji-a12` `{id:'uji-a12', tanggal:'<hari ini>', jam:'<jam>', pemasok:'UJI PEMASOK', caraBayar:'tunai', biayaBongkar:0, merkList:[{id:'1', merk:'MEREK', satuan:'karung', beratKarung:50, jumlahKarung:1, totalKg:50, hargaPerKg:1, subtotalHarga:50}], olehUid:'uid-uji-k'}` | **DITOLAK** (kedatangan berisi kg = owner) |
| ★A13 | K | seperti ★A11 tetapi `biayaBongkar:1` (id `uji-a13`) | **DITOLAK** |
| ★A14 | K | seperti ★A11 tetapi `pemasok:'UJI PEMASOK'` (id `uji-a14`) | **DITOLAK** |
| ★A15 | K | seperti ★A11 tetapi `lahirBuku:false` (id `uji-a15`) | **DITOLAK** |
| ★A16 | K | seperti ★A11 tetapi **tanpa** `olehUid` (id `uji-a16`) | **DITOLAK** (`jujur()`) |
| ★A17 | K | seperti ★A11 tetapi `tanggal:'2026-08-20'` (id `uji-a17`) | **DITOLAK** (bukan-owner hanya bulan berjalan / tenggang — `tglStaf`, tanpa get()) |
| ★A18 | B | seperti ★A1 (id `uji-a18`, `olehUid:'uid-uji-b'`) | LOLOS (peran `ben` di daftar yang sama) |
| ★A19 | B | seperti ★A11 (id `uji-a19`, `olehUid:'uid-uji-b'`) | LOLOS |
| ★A20 | N | seperti ★A1 (id `uji-a20`, `olehUid:'uid-uji-n'`) | **DITOLAK** (akun nonaktif) |
| ★A21 | kasir@ | seperti ★A1 (id `uji-a21`, tanpa `olehUid`) | **DITOLAK** (kasir@ tidak di daftar `wadahLiteran`) |
| ★A22 | akun tanpa `aksesAkun` (uid `baru1`, email `uji.baru1@contoh.com`) | seperti ★A1 (id `uji-a22`, `olehUid:'baru1'`) | **DITOLAK** (Null value error) |
| ★A23 | K | create `/produksiKemasan/uji-a23` `{id:'uji-a23', tanggal:'<hari ini>', jam:'<jam>', dariTakar:true, jadiKarungUtuh:true, merkSumber:'MEREK', namaProduk:'Karung belakang UJI · MEREK', merkTujuan:'Karung belakang UJI · MEREK', ukuranKemasan:50, jumlahUnit:1, sumberList:[{merk:'MEREK', kg:50}], kgDipakai:50, bukaKarung:'UJI', merkAsal:'MEREK', olehUid:'uid-uji-k'}` | LOLOS (pindah buku menumpang `produksiKemasan` yang terbuka sejak v3 — tidak berubah di v5) |
| ★A24 | K | create `/tutupHari/uji-a24` `{id:'uji-a24', tanggal:'<hari ini>', olehUid:'uid-uji-k'}` | **DITOLAK** (tutup hari tetap owner) |
| ★A25 | K | create `/penyesuaianStok/uji-a25` `{id:'uji-a25', tanggal:'<hari ini>', merk:'MEREK', bagian:'wadah', olehUid:'uid-uji-k'}` | **DITOLAK** (cocokkan tetap owner) |
| ★A26 | K | get `/wadahLiteran/<dokumen nyata mana pun>` · get `/batchMasuk/<dokumen nyata mana pun>` | LOLOS (baca staf, tidak berubah sejak v3) |

## B · owner tetap semua

| # | Akun | Operasi · jalur · isi (*Build document*) | Wajib |
|---|---|---|---|
| ★B1 | owner@ | create `/wadahLiteran/uji-b1` `{id:'uji-b1', tanggal:'<hari ini>', jam:'<jam>', tipe:'atur', daftar:['UJI'], penuhKg:50}` | LOLOS (aturan wadah) |
| ★B2 | owner@ | create `/wadahLiteran/uji-b2` `{id:'uji-b2', tanggal:'<hari ini>', jam:'<jam>', tipe:'isi', wadah:'UJI', isiKg:50}` | LOLOS (titik samakan isi) |
| ★B3 | owner@ | update `/wadahLiteran/<dokumen takar nyata mana pun>`: `kg` diubah | LOLOS |
| ★B4 | owner@ | delete `/wadahLiteran/tidak-ada-xyz` (dokumen yang tidak ada) | LOLOS (tidak ada yang berubah) |
| ★B5 | owner@ | create `/batchMasuk/uji-b5` isi seperti ★A12 (kedatangan berisi kg, id `uji-b5`, tanpa `olehUid`) | LOLOS (kedatangan sungguhan) |
| ★B6 | owner@ | create `/batchMasuk/uji-b6` isi seperti ★A11 (batch lahir 0 kg, id `uji-b6`, tanpa `olehUid`) | LOLOS |
| ★B7 | owner@ | create `/tutupHari/uji-b7` `{id:'uji-b7', tanggal:'<hari ini>'}` | LOLOS |

## C · regresi v4 & v3 (v5 di editor)

- ★A12 v4 (owner get `/koleksiUji/x`, koleksi tanpa blok) → **DITOLAK** (tanpa payung).
- ★B1, ★B2, ★B6 v4 (owner & kasir@ menulis tanpa bulan terkunci) → LOLOS; kalau `aturanToko/kunciPeriode` ada, ★A1 & ★A8 v4 → **DITOLAK**.
- ★3 v3 (kasir@ create `/penjualan/uji1`), ★6 v3 (kasir@ selain jalurnya), ★10 v3 (owner memberi peran `owner` lewat `aksesAkun`) → hasil sama dengan v4.
- 14, 15, 22 v3 (staf create `penjualan`: `olehUid` sendiri LOLOS, uid lain DITOLAK, karyawan Kredit DITOLAK) dengan uid `uid-uji-k` / `uid-uji-b` → hasil sama.

Satu saja ★ yang meleset = **jangan Publish**; kirim nomornya ke Claude Code.

## Kasus yang bukan ★ — batas yang diketahui (dicatat, bukan syarat Publish)

| # | Akun | Operasi · jalur · isi | Hasil server | Keterangan |
|---|---|---|---|---|
| V16 | K | seperti ★A11 tetapi `merkList[0]` diberi `totalKg:50, subtotalHarga:50` (id `uji-v16`) | LOLOS | rules v5 tidak membaca isi `merkList` (biaya evaluasi); yang menahannya penjaga perangkat `batchLahir` (`akses.js`) — CI `peta_akses.py --kiriman` memastikan kiriman ini tidak pernah dikirim. Kalau owner mau server juga menilai `merkList`, itu perubahan rules (v5b), bukan dokumen ini. |

## Hasil Playground

Belum dijalankan (dokumen ini dibuat 29 Sep 2026 di cabang dokumen putaran 39). Isi tabel hasil di sini sesudah owner menjalankannya, pola
`docs/uji-rules-v4.md` "Hasil Playground": bagian · kasus · hasil, plus tanggal & sidik commit `firestore.rules` yang ada di editor.

## Perlakuan yang TIDAK berubah di v5 — persis

| Siapa | Apa | Aturan |
|---|---|---|
| kasir@ | `penjualan`, `piutangMutasi`, `stokBahanLiteran` create; tulis-ulang-sama; denyut; baca `ringkasanKasir` & `pengaturan/aksesKasir` | sama dengan v4 (`docs/uji-rules-v4.md` "Perlakuan kasir@") — `wadahLiteran` & `batchMasuk` tetap tertutup untuk kasir@ |
| `ben` / `karyawan` | 11 koleksi create v3 (`penjualan`, `piutangMutasi` bayar, `stokBahan*` pakai, `produksiKemasan`, `pelangganCatatan`, `strukKeluar`, `logAktivitas`, `perangkatStatus`) + 2 update (`pesanan`, `perangkatStatus`) | sama dengan v3/v4 |
| owner | kunci periode (`aturanToko/kunciPeriode` naik / turun satu bulan, tenggang 3 hari), payung tidak ada | sama dengan v4 |
| semua | `wadahLiteran` tidak dinilai kunci periode (bukan koleksi bertanggal di `kunci-periode.js`); `batchMasuk` & `produksiKemasan` dinilai (`tglBaru` owner, `tglStaf` staf) | sama dengan v4 |
