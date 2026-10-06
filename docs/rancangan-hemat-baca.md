# Hemat baca — rancangan & tahap 1–2 (owner 7 Okt 2026, siap 2027)

**Kenapa.** Proyek Firebase toko memakai paket Spark: 50 rb baca/hari, reset "around midnight Pacific" (14.00 WIB sampai 31 Okt, 15.00 WIB
mulai hari kuota 2 Nov). Tiap buka `/baru/` membaca SEMUA catatan toko (±7,4 rb baca, tumbuh ±140 catatan/hari); kuota terlewati 25 Sep, 27 Sep,
1 Okt. Upgrade Blaze gagal (kartu). Keputusan owner (3 Okt, dikukuhkan 7 Okt — K1: tetap Spark + hemat baca, menyala ≤ 20 Nov):

1. **Baca penuh harian per TOKO** — perangkat owner PERTAMA yang terbuka sesudah reset kuota; tiap perangkat lain tetap baca penuh sendiri paling lambat
   14 hari sekali.
2. **Yang didengar = `capServer`** (jam SERVER saat tulisan diterima), bukan `diubahPada` (jam HP penulis; nota HP kasir lama malah tanpa cap).
3. **Urutan nyala**: rules v7 → kode (saklar MATI) → HP penjaga versi baru → daftar siap-nyala hijau 3 hari → owner menyalakan. Aturan pakai: satu tab
   `/baru/` per peramban; tutup hari / kunci bulan / tutup buku butuh internet saat menekan tombolnya; jangan buka sistem lama (sudah pensiun 3 Okt).

Spesifikasi lengkap (rancangan 6 agen + 2 penyanggah, dibuktikan di berkas SDK 10.13.0): di `_privat/serah-terima-2026-10-03/hemat_baca_rancangan.json`
kunci `akhir` (tidak di repo publik). Ringkasan yang dibangun ada di bawah.

## Kerangka

Satu berkas logika MURNI `baru/js/data/hemat-baca.js` (tanpa Firebase, tanpa DOM, jam & jadwal disuntikkan — diuji jsc dengan server mainan) +
adaptor SDK di `baru/js/data/firebase.js`.

| Kelas koleksi (`koleksi.js` `kelas`) | Isi | Saklar NYALA |
|---|---|---|
| (tanpa kelas) = **hemat** — 48 koleksi | catatan toko | V + S + N (+ F) |
| `tetap` | aturanToko, pengaturan, tutupBukuAcara, perangkatStatus, aksesAkun, permintaanAkses, pesanan | pendengar penuh seperti dulu |
| `jejak` | logAktivitas | pendengar berbatas 150 seperti dulu |

Pendengar koleksi hemat saat saklar NYALA:

- **V** = `onSnapshot(collection(k), { source: 'cache' })` — SATU-SATUNYA pemasok memori, 0 baca; isi dikupas lalu disaring batu nisan.
- **S** = `where('capServer', '>', B)` — B = tanda air koleksi itu di perangkat ini − 60 menit; menarik ubahan bercap ke simpanan (V ikut berubah).
  B tetap sehari (target yang sama dipakai ulang), digeser maju > 8 jam sekali (≤ 3×/hari).
- **F** = baca penuh `query(collection(k), limit(1.000.000))` — kueri SENDIRI (bukan `collection(k)` polos yang berbagi view dengan V dan bisa "selesai"
  tanpa server). Selesai = snapshot server + `getCountFromServer` sama. Dipakai: perangkat baru / simpanan tidak dipercaya, gen "semua perangkat", tutup buku
  berubah, > 14 hari, baca penuh harian toko, hitungan server beda, penulis tanpa cap (tahan lama), tombol. Mode `penuh` (F menempel) selama tutup buku
  berjalan atau penulis tanpa cap aktif.
- **N** = batu nisan `batuNisan` `capServer > Bn`, Bn = min(Wt baca penuh terakhir, jam server) − 60 menit (tidak pernah 0).

Penjaga yang berbunyi (semuanya di `hbSesi`, diuji `alat-uji/uji_hemat_baca.py`):

- **Hitungan server** tiap buka (sesudah S & N terkini) dan tiap 30 menit untuk koleksi tulisan HP kasir: beda → hitung ulang 15 detik → baca penuh.
- **Pendeteksi tanpa cap** di setiap snapshot server F: catatan yang berubah / lahir / hilang tanpa cap → disentuh `capServer` (atau diberi nisan) supaya
  perangkat lain menerimanya lewat S. > 400 temuan → gen koleksi itu dinaikkan (semua perangkat baca penuh). Tidak jalan bila dasar perangkat tidak
  dipercaya (tidak membanjiri) atau tutup buku berjalan.
- **Penulis tanpa cap** dari denyut: kasir darurat < `kasir-v33` ≤ 14 hari → penjualan dengar penuh; `kasir.html` ≤ 14 hari → tiga koleksi REST; tab
  `/baru/` versi lama / sistem lama ≤ 15 menit → semua dengar penuh, lebih lama → baca penuh sekali.
- **Pendengar simpanan hidup**: ubahan yang dibawa S/F wajib terlihat di V dalam 5 detik; tidak → tirai "muat ulang", penulis menolak.
- **Satu klien Firestore per peramban** (kunci tab localStorage): tab kedua bertanya "Pakai di sini"; tab yang kalah `terminate()`.
- **Rem kuota**: baca penuh OTOMATIS ditunda bila perkiraan baca toko hari ini > 80% kuota; ≤ 2 otomatis/koleksi/hari; 3× mulai tanpa selesai → berhenti.
  Tombol manual menembus.
- **Uang-kritis** (tutup hari, titik kas, kunci bulan, tutup buku): hitungan server ≤ 2 menit untuk semua koleksi hemat, kalau tidak DITOLAK dengan kalimat.
- **Katalog kasir**: terbit hanya bila semua koleksi hemat terperiksa, hitungan koleksi HP kasir ≤ 35 menit, kunci tab dipegang, tanpa ayunan antarperangkat
  (dua perangkat berbeda hitungan → berhenti + baca penuh), ≤ 6 terbit otomatis per jam.
- **Jam**: semua batas memakai cap SERVER. Selisih jam perangkat dari gema `capServer` denyut owner sendiri; tanda air dijepit ≤ jam server + 10 menit.

## Tahap 1–2 (cabang `perbaikan/hemat-baca`) — yang dibangun

| Bagian | Saklar MATI (bawaan) | Saklar NYALA |
|---|---|---|
| Pendengar | persis sebelum 7 Okt (dicek jsc: satu pendengar penuh per koleksi + katalog) | V/S/F/N untuk 48 koleksi hemat, tetap & jejak seperti dulu |
| Kupas `capServer` sebelum memori | ya | ya |
| Cap jam server di tulisan koleksi hemat (`tulisBerkas`, `perbaruiBerkas`, `pulihkanBerkas`) | ya | ya |
| Batu nisan di batch hapus (koleksi hemat) | ya, **sesudah aturan v7 terbukti** di perangkat itu (1 baca sekali) | ya |
| Denyut owner `capServer` + versi `baru-c1` | ya | ya (+ ringkasan baca hari ini) |
| Kasir darurat `kasir-v33`: nota lewat REST `:commit` + `REQUEST_TIME` | ya | ya |
| Kunci tab, rem, gerbang uang-kritis & katalog tambahan | tidak | ya |
| `cacheSizeBytes: CACHE_SIZE_UNLIMITED` | tidak (bawaan) | ya |

**Tidak dicap (sengaja, dijaga uji statis):** tutupBukuAcara (kirim ulang identik SDK harus lolos `tulisUlangSama` v6), pesanan & denyut staf (rules
membatasi kolomnya), setelan/akun/permintaan (`tetap`, selalu didengar penuh), logAktivitas (jejak berbatas), ringkasanKasir (bentuk beku = sistem lama),
arsipTahun (tidak didengar).

**Rules v7** (`firestore.rules`; `firestore.rules.v6` disimpan utuh) — HANYA menambah: `ulangKasirBercap()` di update penjualan untuk kasir@, dan blok
`batuNisan` (owner, `capServer == request.time`). Uji server: `docs/uji-rules-v7.md`.

## Keputusan tahap ini yang diambil sendiri (bukan dari spesifikasi kata per kata)

- **Saklar per perangkat** (localStorage `miqbal_hemat_saklar_v1`, tombol di Menu › Sistem › Perangkat › Hemat baca, dua ketukan, lalu muat ulang) — bukan
  dokumen toko `aturanToko/hematBaca`. Jalan darurat: `/baru/?hemat=mati`. Mematikan = kembali dengar penuh, tanpa terbit ulang.
- **Batu nisan menunggu bukti aturan v7** (owner bisa membaca `batuNisan`) — kode ini aman walau tergabung sebelum rules v7 terbit: hapus tetap seperti dulu.
  Saklar NYALA juga butuh bukti itu.
- **Kunci tab hanya saat NYALA** (MATI = tidak berubah apa-apa).
- **Pendeteksi jalan di setiap baca penuh**, bukan hanya baca penuh harian — tanpa itu baca penuh perangkat mana pun "menelan" ubahan Console diam-diam
  sebelum perangkat pendeteksi melihatnya (temuan uji server mainan B6).
- `capServer` denyut owner dipakai sebagai gema jam server (spesifikasi: `padaServer`); `padaServer` tetap ikut dikupas.

## Belum dibangun (tahap berikut / bila perlu)

- Jejak (logAktivitas) atas permintaan saja saat nyala (±150 baca per buka masih dibayar).
- Pembersih nisan per dokumen (`getDocFromServer`) & `nisanTuntas`; arsip besar → `clearIndexedDbPersistence`.
- Deteksi "antrean warisan" (mutasi kode lama di antrean IndexedDB) — pendeteksi statis & pendeteksi F menangkap akibatnya.
- Uji peramban CI dengan emulator Firestore (demosi tab, F berkueri sendiri, limbo, REST `:commit` terhadap rules v7) — kasus B1–B12 spesifikasi.
- Perkiraan baca toko dari denyut adalah perkiraan; tagihan sebenarnya dibaca di tab Usage Console sehari sebelum & sesudah nyala.
