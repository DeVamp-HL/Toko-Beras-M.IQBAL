# Uji rules v26 di server — foto nota kedatangan dari tablet & tautan beku Dasbor (DRAF 27 Nov 2026)

v26 = v25 FINAL (aktif sejak 27 Nov 2026 ±13.07 WIB) + **satu baris `create` fotoBon yang diperluas, dua fungsi baru (`stafFotoNota`, `stafTandaFoto`), dan dua
blok baru (`fotoTanda`, `dasborPublik`)** (berkas kanonik `firestore.rules`; pembanding `firestore.rules.v25`). Tidak ada yang lain berubah —
`alat-uji/periksa_rules.py` mencabut balik ubahan itu lalu membandingkan sisanya huruf demi huruf dengan v25.

## Yang berubah v25 → v26

1. **(v26-1) `fotoBon` create: + Penjaga laci** — paket P8, keputusan owner 27 Nov 2026 (A94): nota / bon kedatangan difoto owner + tablet Penjaga laci. Penjaga laci
   boleh MEMBUAT foto atas nama penulisnya (`olehUid`), `idBon` = id kedatangan (angka, bentuk id aplikasi), kolom dibatasi. Bentuk foto lama tetap (id = id dokumen,
   jenis gambar, base64 ≤ 960.000 huruf). **Baca & hapus foto TETAP owner saja.** Karyawan tidak boleh.
2. **(v26-2) blok `fotoTanda`** — satu dokumen ringan per foto (id = id foto; `idBon`, `jenis`, tanggal, ukuran — TANPA gambar) supaya Dasbor menghitung kedatangan
   yang belum berfoto tanpa membaca fotonya:
   - read: owner;
   - create: owner, atau Penjaga laci atas nama penulisnya — `id` = id dokumen, `idBon` = id kedatangan, `jenis` bon | tunai, tanggal `YYYY-MM-DD`, kolom dibatasi;
   - ubah & hapus: owner (tanda ikut terhapus bersama fotonya).
3. **(v26-3) blok `dasborPublik`** — tautan beku Dasbor untuk pihak luar (B103: owner saja, owner mencentang bagian yang ikut, berlaku 1 · 7 · 30 · 90 hari):
   - get: SIAPA PUN yang tahu kodenya (≥ 20 huruf, tanpa login — halaman `baru/dasbor-publik.html`) **selama jam server belum lewat `sampai`**; sesudahnya server
     menolak (bukan cuma halamannya);
   - list: owner (tidak ada yang bisa menelusuri kode orang lain);
   - create & update: owner, `sampai` wajib jam (timestamp) paling lama 91 hari dari jam server (90 hari + kelonggaran jam perangkat);
   - delete (cabut): owner.

Tidak ada rupiah, kg, atau tanggal buku yang dikunci periode di koleksi baru. Isi tautan Dasbor = angka yang dibekukan owner (tanpa nama orang).
**Terbitkan v26 SEBELUM PR paket P8 digabung** — tanpa v26: foto nota dari tablet ditolak server (layar tablet menyebutnya), pendengar `fotoTanda` &
`dasborPublik` di HP/Mac owner ditolak (tercatat di Menu › Toko ini › Perangkat & antrean; hitungan "belum berfoto" Dasbor menganggap semua kedatangan
belum berfoto), dan tautan Dasbor tidak bisa dibuat / dibuka. Foto bon pemasok & nota kas kecil dari HP owner, log, arsip foto, omzet per perangkat tetap jalan.

## Urutan (± 5 menit)

1. Console › Firestore › **Rules** — salin isi `firestore.rules` cabang ini (seluruhnya) ke editor.
2. Klik **Rules Playground**, jalankan bagian **Wajib owner** di bawah (dua kasus). Hasilnya harus sama dengan kolom Wajib. ★FD3 & ★FD4 TIDAK bisa dinilai Playground
   (timestamp dari "Build document" dikirim sebagai map → `is timestamp` salah = DITOLAK palsu; get tamu butuh dokumen nyata) — dibuktikan emulator CI bagian V26.
3. Klik **Publish** — sebelum PR digabung.
4. Sesudah terbit dan PR digabung: di tablet (Penjaga laci) catat satu Barang masuk → kartu **Foto nota** → Ambil foto. Di HP owner: Stok › Barang masuk ›
   koreksi kedatangan itu → **lihat foto**. Lalu Dasbor › **Bagikan** → buat tautan 1 hari → buka tautannya di jendela penyamaran (tanpa login).

## Wajib owner (2 kasus — tanpa dokumen uji staf, tanpa timestamp ketikan)

| # | Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|---|
| 1 | ★FD1 | owner@ | create `fotoTanda/fn-uji-1` | tanda foto kedatangan (dokumen kosong — owner tidak dibatasi bentuk) | LOLOS | owner mencatat tanda bersama fotonya |
| 2 | ★FD2 | owner@ | get `fotoTanda/fn-uji-1` | — | LOLOS | Dasbor owner membaca tanda |

## Opsional — sudah dinilai model CI & emulator

Kasus staf butuh akun uji staf aktif (U11 dari `docs/uji-rules-v7.md`: `aksesAkun/uid-uji-b`, peran ben; kasus karyawan = peran diganti karyawan). Tanpa itu
cukup percaya bukti emulator di bawah (mesin rules yang sama dengan server). ★FD3 & ★FD4 tidak bisa dinilai Playground (lihat Urutan no. 2) — emulator saja.

| Kasus | Akun | Operasi · jalur | Isi | Wajib | Kenapa |
|---|---|---|---|---|---|
| ★FD3 | owner@ | create `dasborPublik/Dp7Qp2Xz9LmN4rT8vW1yZb` | `sampai` = jam sekarang + 7 hari (tipe timestamp) | LOLOS | owner membuat tautan 7 hari |
| ★FD4 | tamu (tanpa login) | get `dasborPublik/Dp7Qp2Xz9LmN4rT8vW1yZb` | dokumen dengan `sampai` besok | LOLOS | pihak luar membuka tautan yang belum lewat |
| ★FD5 | Penjaga laci | create `fotoBon/fn-uji-1` | foto nota kedatangan atas namanya | LOLOS | Penjaga laci memotret nota dari tablet (keputusan owner) |
| ★FD6 | Penjaga laci | create `fotoTanda/fn-uji-1` | tanda bon atas namanya | LOLOS | tanda ikut kiriman foto |
| ★FD7 | karyawan | create `fotoBon/fn-uji-1` | foto | DITOLAK | memotret = owner & Penjaga laci saja |
| ★FD8 | karyawan | create `fotoTanda/fn-uji-1` | tanda | DITOLAK | idem |
| ★FD9 | Penjaga laci | create `fotoBon/fn-uji-1` | olehUid orang lain | DITOLAK | atas nama penulisnya |
| ★FD10 | Penjaga laci | create `fotoBon/fn-uji-1` | idBon `uk-501` | DITOLAK | nota kas kecil = owner (idBon wajib id kedatangan) |
| ★FD11 | Penjaga laci | create `fotoBon/fn-uji-1` | + hargaTotal | DITOLAK | kolom dibatasi |
| ★FD12 | Penjaga laci | create `fotoBon/fn-uji-1` | jenis `text/html` | DITOLAK | gambar saja (bentuk foto v7) |
| ★FD13 | Penjaga laci | get `fotoBon/fn-uji-1` | — | DITOLAK | baca foto = owner |
| ★FD14 | Penjaga laci | delete `fotoBon/fn-uji-1` | — | DITOLAK | hapus foto = owner |
| ★FD15 | Penjaga laci | create `fotoTanda/fn-uji-1` | jenis `kas` | DITOLAK | tanda tablet = kedatangan (bon / tunai) |
| ★FD16 | Penjaga laci | create `fotoTanda/fn-uji-1` | id `fn-lain` | DITOLAK | id = id dokumen |
| ★FD17 | Penjaga laci | get `fotoTanda/fn-uji-1` | — | DITOLAK | tanda dibaca owner |
| ★FD18 | tamu | get `dasborPublik/Dp7Qp2Xz9LmN4rT8vW1yZb` | `sampai` kemarin | DITOLAK | tautan yang sudah lewat ditolak SERVER |
| ★FD19 | tamu | list `dasborPublik` | — | DITOLAK | kode tidak bisa didaftar |
| ★FD20 | tamu | create `dasborPublik/Dp7Qp2Xz9LmN4rT8vW1yZb` | tautan | DITOLAK | tulis = owner |
| ★FD21 | Penjaga laci | create `dasborPublik/Dp7Qp2Xz9LmN4rT8vW1yZb` | tautan | DITOLAK | tulis = owner (keputusan owner) |
| ★FD22 | owner@ | create `dasborPublik/Dp7Qp2Xz9LmN4rT8vW1yZb` | `sampai` 1 Jan 2100 | DITOLAK | paling lama 91 hari, tidak ada yang abadi |
| ★FD23 | owner@ | create `dasborPublik/Dp7Qp2Xz9LmN4rT8vW1yZb` | `sampai` teks | DITOLAK | `sampai` wajib jam (timestamp) |
| ★FD24 | tamu | get `dasborPublik/abc123` | kode pendek | DITOLAK | kode ≥ 20 huruf |
| ★FD25 | Penjaga laci nonaktif | create `fotoBon/fn-uji-1` | foto | DITOLAK | akun yang dinonaktifkan owner |
| ★FD26 | kasir@ | create `fotoTanda/fn-uji-1` | tanda | DITOLAK | kasir darurat tidak memotret nota |
| ★FD27 | owner@ | list `dasborPublik` | — | LOLOS | owner mengelola daftar tautan |

Di **v25** kasus ★FD1, ★FD2, ★FD3, ★FD4, ★FD5, ★FD6, ★FD27 DITOLAK (koleksi `fotoTanda` & `dasborPublik` belum ada, `fotoBon` owner saja); kasus lain sama hasilnya.

## Bukti emulator

`alat-uji/uji_rules_emulator.py` bagian **V26** (workflow *Uji rules di emulator*, jalan otomatis di PR yang mengubah `firestore.rules`): kedua puluh tujuh kasus
di atas atas `firestore.rules` (v26) dan atas `firestore.rules.v25` — yang berbeda wajib persis ★FD1, ★FD2, ★FD3, ★FD4, ★FD5, ★FD6, ★FD27 — plus kontrol (ubahan v26
dirusak → kasus sasarannya wajib berbalik). Semua kasus v25 sampai v7 lama tetap dijalankan atas v26 dan wajib sama hasilnya. Jam di kasus (`sampai`) digeser ke
jam emulator, jadi ★FD4 / ★FD18 menguji "belum lewat" / "sudah lewat" terhadap jam server sungguhan.

## Hasil Playground & terbit

**v26 TERBIT 27 Nov 2026 ±16.02 WIB** — SEBELUM PR #239 (paket P8) digabung, sesuai urutan di atas. Owner menempel isi `firestore.rules` (commit `5becd54`, berkas
mentah GitHub di tab Chrome — sidiknya dicek lebih dulu = repo) ke editor Rules Console; Claude menjalankan Playground & menekan Publish atas permintaan owner
("gua copy-paste, sisanya lu yang kerjain"). Isi editor sebelum Publish, sesudah uji Playground, dan isi yang aktif sesudah halaman dimuat ulang sama persis dengan
`firestore.rules` cabang ini: SHA-256 berawalan `6e71bf925be5d78d`, 95.198 byte, baris 2 `ATURAN FIRESTORE v26 FINAL` (sebelumnya aktif v25 `e6718c55`, 90.788 byte).
Playground (akun uji owner: UID `uid-uji`, email `owner@tokoberasmiqbal.web.app`, email terverifikasi): ★FD2 get `fotoTanda/fn-uji-1` → *Simulated read allowed* ·
★FD1 create `fotoTanda/fn-uji-1` → *Simulated write allowed* — keduanya sesuai kolom Wajib. ★FD3 create `dasborPublik/Dp7Qp2Xz9LmN4rT8vW1yZb` dengan `sampai`
4 Des 2026 16.00 dari "Build document" → *Simulated write denied*, rincian evaluasi `… is timestamp` = **false**: batas Playground yang sudah tercatat sejak v7
(timestamp ketikan dikirim sebagai map `{type, seconds, nanoseconds}`), bukan hasil aturan. ★FD3, ★FD4 dan kasus staf (★FD5–★FD27) dibuktikan emulator CI
bagian V26 commit `5becd54` (run 45968139049): 27/27 lulus atas v26 · 27/27 sesuai atas v25 (berbeda tepat ★FD1–★FD6, ★FD27) · kontrol v26 9/9 berbunyi.
