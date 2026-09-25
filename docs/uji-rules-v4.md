# Uji rules v4 di server — putaran 25 (kunci periode)

`alat-uji/periksa_rules.py` memeriksa **bentuk** rules v4 (statis, di CI). Berkas ini untuk **perilaku server**: kasus yang dijalankan owner di
**Rules Playground** (Console › Firestore › Rules), dengan v4 di EDITOR proyek toko, **sebelum** v4 diterbitkan. Claude Code tidak memegang sandi
dan tidak mengetik apa pun di Console; Claude hanya MEMBACA Console lewat Chrome owner di langkah 4. Kasus v3 ada di `docs/uji-rules-v3.md`.

Rules Playground membaca data sungguhan lewat `get()`. Ada dua keadaan yang wajib diuji:
- **A · dengan dokumen kunci** (dokumen uji `sampaiBulan: '2026-07'`): kunci benar-benar menolak.
- **B · TANPA dokumen kunci** — keadaan server yang sebenarnya sesudah v4 terbit: tidak ada bulan terkunci, jadi tidak ada fitur yang mati.

Tenggang minimal = **3 hari** (owner 25 Sep): tanggal 1–3 bulan baru, catatan bertanggal bulan lalu tidak diperiksa kunci sama sekali; bulan M paling
cepat dikunci tanggal **4** bulan M+1.

---

## Urutan (satu per satu; jangan klik **Publish** sebelum langkah 7)

1. **Persiapan** — v3 masih yang terbit. Console › Firestore › Data: buat dokumen **`aturanToko/kunciPeriode`**: field `sampaiBulan` (string) =
   `2026-07`, field `riwayat` (array) = kosong. Selama v3 terbit, dokumen ini tidak dibaca siapa pun.
2. **Bagian A** di Playground (v4 di editor). Isian **Firebase UID** owner = **`uid-uji`**.
3. **Hapus dokumen `aturanToko/kunciPeriode`.** Di bawah v4 dokumen itu tidak bisa dihapus siapa pun; kalau tertinggal, Juli & bulan sebelumnya
   terkunci dan kasus B/C salah.
4. **Bilang ke Claude "dokumen uji sudah dihapus".** Claude membuka Console › Firestore › Data lewat Chrome owner (hanya membaca) dan memastikan
   `aturanToko/kunciPeriode` **tidak ada**. Baru sesudah itu Claude bilang "lanjut B".
5. **Bagian B** lalu **Bagian C** — masih di Playground, v4 masih di editor, masih BELUM Publish.
6. **Merge cabang** `tulang-punggung/25-kunci-periode` (owner bilang "merge"; Claude yang menggabung & push) dan tunggu Pages hijau. v4 wajib terbit
   SESUDAH `/baru/` versi ini live — `/baru/` lama belum memecah kiriman besar dan belum menolak catatan staf yang lewat tenggang di perangkat.
7. **Claude bilang "siap Publish"** (semua ★ sesuai, dokumen kunci tidak ada, Pages hijau) → owner **Publish** v4. Isi editor harus persis sama dengan
   `firestore.rules` di repo.
8. **Satu nota dari kasir darurat** (kasir@) → pastikan masuk di layar Jual `/baru/`. Tidak masuk → tempel `firestore.rules.v3`.
9. **Kunci bulan pertama baru sesudah putaran 25b**, dan hanya kalau daftar periksanya bersih (Uang › Tutup buku › Kunci bulan). Butir ⛔
   "putaran 25b" menahannya sampai itu.

**Mundur** = tempel `firestore.rules.v3` (kunci periode mati; aturan akun v3 tetap).

Dokumen nyata yang dipakai (dari cadangan 25 Sep):
- `pengeluaranHarian/1787308559387.802` bertanggal **28 Jul 2026**.
- `pengeluaranHarian/1786284868188.7153` bertanggal **9 Agu 2026**.

Isian *Auth token payload* sama seperti v3: tambahkan `"email": "owner@tokoberasmiqbal.web.app"` atau `"email": "kasir@tokoberasmiqbal.web.app"`.
"Error running simulation … Null value error" = DITOLAK di server, bukan lolos (sama seperti v3). Playground tidak mengubah apa pun di database.

**Cara Playground menilai *update* (terbukti 25 Sep):** isian *Build document* DIGABUNG ke dokumen yang sudah ada. Mengisi field dengan nilai yang
sama = dokumen tidak berubah = `tulisUlangSama()` benar = LOLOS dengan sengaja. Untuk menguji perubahan, isi field yang BERUBAH (mis. `nominal`).
Pada kasus owner, rules hanya menilai field tanggal; field lain cukup yang perlu untuk membuat perubahan.

## A · Dengan dokumen kunci uji (Juli terkunci, Agustus terbuka)

| # | Akun | Operasi · jalur · isi (*Build document*) | Wajib |
|---|---|---|---|
| ★A1 | owner@ | create `/penjualan/uji-a1` `{id:'uji-a1', tanggal:'2026-07-20', hargaTotal:1000}` — bertanggal bulan terkunci | **DITOLAK** |
| ★A2 | owner@ | update `/pengeluaranHarian/1787308559387.802` (28 Jul): isi dokumen yang sama, `nominal` diubah | **DITOLAK** (nilai LAMA di bulan terkunci) |
| ★A3 | owner@ | update `/pengeluaranHarian/1786284868188.7153` (9 Agu): `tanggal` diubah ke `'2026-07-30'` | **DITOLAK** (nilai BARU di bulan terkunci) |
| ★A4 | owner@ | delete `/pengeluaranHarian/1787308559387.802` | **DITOLAK** |
| ★A5 | owner@ | create `/penjualan/uji-a5` `{id:'uji-a5', tanggal:'<tanggal hari ini>', hargaTotal:1000}` | LOLOS (bulan berjalan, tanpa get()) |
| ★A6 | owner@ | update `/pengeluaranHarian/1786284868188.7153` (9 Agu): `nominal` diubah, tanggal tetap | LOLOS (Agustus belum terkunci; satu get()) |
| ★A7 | kasir@ | create `/penjualan/uji-a7` `{id:'uji-a7', tanggal:'<tanggal KEMARIN>', hargaTotal:1000, jenis:'kasir_darurat_nominal'}` | LOLOS |
| ★A8 | kasir@ | create `/penjualan/uji-a8` `{id:'uji-a8', tanggal:'2026-07-31', hargaTotal:1000}` | **DITOLAK** — kasir@ TIDAK bebas dari kunci |
| ★A9 | owner@ | delete `/penjualan/tidak-ada-xyz` (dokumen yang tidak ada) | LOLOS (tidak ada yang berubah) |
| ★A10 | owner@ | create `/pajakSetoran/uji-a10` `{id:'uji-a10', masaPajak:'2026-07', tanggalSetor:'2026-07-15', jumlah:1}` | LOLOS (pajak tidak dikunci, K6) |
| ★A11 | owner@ | update `/pengaturan/titikKas`: isi sama, `tanggal` = `'<tanggal hari ini>'` | LOLOS (titik kas boleh maju) |
| ★A12 | owner@ | get `/koleksiUji/x` (koleksi yang TIDAK punya blok) | **DITOLAK** (payung dihapus; di v3 ★11 LOLOS) |
| ★A13 | owner@ (UID `uid-uji`) | update `/aturanToko/kunciPeriode` → `{sampaiBulan:'2026-06', riwayat:[{aksi:'buka', bulan:'2026-07', olehUid:'uid-uji', alasan:'uji playground satu langkah'}]}` | LOLOS (turun satu bulan dengan alasan) |
| ★A14 | owner@ (UID `uid-uji`) | update `/aturanToko/kunciPeriode` → `{sampaiBulan:'2026-05', riwayat:[{aksi:'buka', bulan:'2026-07', olehUid:'uid-uji', alasan:'uji playground dua langkah'}]}` | **DITOLAK** (turun dua bulan) |
| ★A15 | owner@ (UID `uid-uji`) | update `/aturanToko/kunciPeriode` → `{sampaiBulan:'2026-06', riwayat:[{aksi:'buka', bulan:'2026-07', olehUid:'uid-uji', alasan:'pendek'}]}` | **DITOLAK** (alasan < 10 huruf) |
| ★A16 | owner@ (UID `uid-uji`) | update `/aturanToko/kunciPeriode` → `{sampaiBulan:'2026-09', riwayat:[{aksi:'kunci', bulan:'2026-09', olehUid:'uid-uji', alasan:''}]}` | **DITOLAK** (melompati Agustus) |
| ★A17 | owner@ | delete `/aturanToko/kunciPeriode` | **DITOLAK** (dokumen kunci tidak pernah dihapus) |
| ★A2b | owner@ | update `/pengeluaranHarian/1787308559387.802` (28 Jul): `tanggal` diubah ke `'<tanggal hari ini>'` | **DITOLAK** (memindah catatan KELUAR dari bulan terkunci — nilai LAMA dinilai) |
| ★A13b | owner@ (UID `uid-uji`) | SESUDAH A1–A17: ubah dokumen uji di tab Data → `riwayat` = satu map `{aksi:'kunci', bulan:'2026-07', olehUid:'uid-uji'}` (bentuk nyata: kunci pertama selalu menulis satu entri). Lalu update → `{sampaiBulan:'2026-06', riwayat:[<entri itu persis>, {aksi:'buka', bulan:'2026-07', olehUid:'uid-uji', alasan:'uji playground satu langkah'}]}` | LOLOS (jalur nyata: irisan `riwayat[0:1]`) |

Temuan Playground 25 Sep: ★A13 versi pertama (riwayat kosong) GALAT "line 136 … Index out of bound error. Index: [-1], size: [1]" — di server irisan
`list[0:0]` galat, bukan list kosong. Ditambal di rules: `(lama.size() == 0 || d.riwayat[0:lama.size()] == lama)`; `periksa_rules.py` kini gagal bila
penjaga itu hilang. Sesudah tambalan, ★A13–★A16 diulang dengan rules baru di editor.

## B · TANPA dokumen kunci (sesudah langkah 3–4) — keadaan server sesudah v4 terbit

| # | Akun | Operasi · jalur · isi (*Build document*) | Wajib |
|---|---|---|---|
| ★B0 | owner@ (UID `uid-uji`) | ulang ★A13 persis (update turun satu bulan) | **DITOLAK** — tidak ada dokumen yang bisa diubah. LOLOS = dokumen uji MASIH ADA → berhenti, ulang langkah 3–4 |
| ★B1 | owner@ | update `/pengeluaranHarian/1786284868188.7153` (9 Agu, sudah lewat tenggang): `nominal` diubah, tanggal tetap | LOLOS (satu get(); dokumen kunci tidak ada = tidak ada bulan terkunci) |
| ★B2 | owner@ | create `/penjualan/uji-b2` `{id:'uji-b2', tanggal:'2026-08-20', hargaTotal:1000}` | LOLOS |
| ★B3 | owner@ (UID `uid-uji`) | create `/aturanToko/kunciPeriode` → `{sampaiBulan:'2026-08', riwayat:[{aksi:'kunci', bulan:'2026-08', olehUid:'uid-uji', alasan:''}]}` | LOLOS — kunci PERTAMA langsung ke Agustus dari dokumen yang belum ada (Playground tidak menyimpannya) |
| ★B4 | owner@ (UID `uid-uji`) | create `/aturanToko/kunciPeriode` → `{sampaiBulan:'<bulan berjalan, mis. 2026-09>', riwayat:[{aksi:'kunci', bulan:'<bulan yang sama>', olehUid:'uid-uji', alasan:''}]}` | **DITOLAK** — bulan yang belum lewat tenggang (bulan berjalan tidak pernah) |
| ★B5 | owner@ (UID `uid-uji`) | HANYA kalau hari ini tanggal 1, 2, atau 3: seperti ★B4 dengan `sampaiBulan` = **bulan lalu** | **DITOLAK** — bulan lalu masih dalam tenggang 3 hari. Tanggal 4 atau sesudahnya: lewati (★B3 sudah membuktikan sisi LOLOS-nya) |
| ★B6 | kasir@ | create `/penjualan/uji-b6` `{id:'uji-b6', tanggal:'2026-08-20', hargaTotal:1000, jenis:'kasir_darurat_nominal'}` | LOLOS — nota kasir darurat yang tertahan lama tidak macet selama tidak ada bulan terkunci |

## C · Kasus ★ v3 diulang (masih TANPA dokumen kunci)

Semua ★ di `docs/uji-rules-v3.md` §A dijalankan ulang dengan v4 di editor, hasil wajib sama, **kecuali ★11**: di v4 wajib **DITOLAK** (= ★A12).
- ★2 (owner delete `/penjualan/x`): tetap LOLOS — dokumen `x` tidak ada (= ★A9).
- ★3 / ★4 (kasir@ create tanpa `tanggal`): LOLOS **hanya** tanpa dokumen kunci. Catatan tanpa tanggal dinilai sebagai bulan paling tua, jadi begitu
  ada satu bulan terkunci, catatan tanpa tanggal ditolak. Karena itu bagian C dijalankan SESUDAH dokumen uji dihapus.

## Perlakuan kasir@ (kasir darurat) di v4 — persis

| Operasi | Koleksi | Aturan |
|---|---|---|
| create | `penjualan`, `piutangMutasi`, `stokBahanLiteran` | sama dengan owner (`tglBaru('tanggal')`): bulan berjalan atau bulan lalu tanggal 1–3 → tanpa get(); selain itu SATU get() dokumen kunci dan **DITOLAK** bila bulannya ≤ `sampaiBulan` (★A8). Tanpa bulan terkunci → LOLOS (★B6) |
| update | tiga koleksi yang sama | hanya tulis-ulang yang isinya **sama persis** (`tulisUlangSama()`, kirim-ulang antrean) — tidak mengubah apa pun, jadi tidak dinilai |
| delete | semua koleksi bertanggal | **tidak pernah** |
| create | `logAktivitas`, `perangkatStatus` | tidak dikunci (jejak & denyut) |

kasir*.html mengirim **satu dokumen per permintaan** (REST PATCH), jadi paling banyak 1 pemeriksaan kunci per permintaan (batas Firebase 10). CI
(`peta_akses.py --kiriman`) gagal kalau salah satu berkas kasir mulai mengirim banyak dokumen sekaligus; `periksa_rules.py` gagal kalau kasir@
boleh menghapus, mengubah selain tulis-ulang identik, atau membuat catatan bertanggal tanpa penilaian kunci.

Kenapa kasir@ tidak memakai aturan staf (hanya bulan berjalan + tenggang, tanpa get()): aturan itu menolak nota kasir darurat yang tertahan offline
lebih dari 3 hari melewati awal bulan **walau belum ada bulan terkunci** — dan kasir*.html (belum diubah sampai 25b) menganggap penolakan server
sebagai "belum masuk", sehingga seluruh antrean tablet macet. Dengan aturan owner, kasir@ tetap tidak bisa menulis ke bulan terkunci (★A8).
