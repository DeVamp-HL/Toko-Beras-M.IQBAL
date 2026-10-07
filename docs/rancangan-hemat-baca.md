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
- **N** = batu nisan `batuNisan` `capServer > Bn`, Bn = min(jam baca penuh terakhir tiap koleksi, jam server) − 60 menit (tidak pernah 0). Nisan hanya
  menyembunyikan versi yang LEBIH TUA darinya: bercap lebih baru, atau terlihat masih ADA di baca penuh server (lahir ulang tanpa cap) → tampil.

Penjaga yang berbunyi (semuanya di `hbSesi`, diuji `alat-uji/uji_hemat_baca.py`):

- **Hitungan server** tiap buka (sesudah S & N terkini) dan tiap 30 menit untuk koleksi tulisan HP kasir: beda → hitung ulang 15 detik → baca penuh.
- **Pendeteksi tanpa cap** di setiap snapshot server F: catatan yang berubah / lahir / hilang tanpa cap → disentuh `capServer` (atau diberi nisan) supaya
  perangkat lain menerimanya lewat S. > 400 temuan → gen koleksi itu dinaikkan (semua perangkat baca penuh). Tidak jalan bila dasar perangkat tidak
  dipercaya (tidak membanjiri) atau tutup buku berjalan. Catatan yang LAHIR tanpa cap di koleksi yang dengar penuh karena penulis tanpa cap TIDAK disentuh
  (semua perangkat owner sudah mendengarnya penuh); catatan yang hilang sesudah tutup buku berubah = diarsipkan, bukan "hilang tanpa kabar". Catatan yang
  LAHIR ULANG (ada di snapshot server padahal nisannya berlaku) dicatat di rekam & disentuh. Temuan yang gagal dikirim disimpan di rekam, diulang tiap
  menit (≤ 5 kali).
- **Penulis tanpa cap** dari denyut: kasir darurat < `kasir-v33` ≤ 14 hari → penjualan dengar penuh; `kasir.html` ≤ 14 hari → tiga koleksi REST; tab
  `/baru/` versi lama / sistem lama ≤ 15 menit → semua dengar penuh, lebih lama → baca penuh sekali. Umur denyut = jam SERVER saat perangkat ini melihat
  denyut itu berubah (tersimpan di rekam); `pada` (jam perangkat penulis) hanya bila perubahannya tidak terlihat.
- **Pendengar simpanan hidup**: ubahan yang dibawa S/F wajib terlihat di V dalam 5 detik; tidak → tirai "muat ulang", penulis menolak.
- **Satu klien Firestore per peramban** (kunci tab localStorage): tab kedua bertanya "Pakai di sini"; tab yang kalah `terminate()`.
- **Rem kuota**: baca penuh OTOMATIS ditunda bila perkiraan baca toko hari ini > 80% kuota; ≤ 2 otomatis/koleksi/hari; 3× mulai tanpa selesai → berhenti.
  Tombol manual menembus.
- **Uang-kritis** (tutup hari, titik kas, kunci bulan, tutup buku): hitungan server ≤ 2 menit untuk semua koleksi hemat, kalau tidak DITOLAK dengan kalimat.
- **Katalog kasir**: terbit hanya bila semua koleksi hemat terperiksa, hitungan koleksi HP kasir ≤ 35 menit, kunci tab dipegang, tanpa ayunan antarperangkat
  (dua perangkat berbeda hitungan → berhenti + baca penuh), ≤ 6 terbit otomatis per jam.
- **Jam**: semua batas memakai cap SERVER. Selisih jam perangkat HANYA dari gema `capServer` denyut owner sendiri (cap di data — bisa tahun 2099 dari
  Console — tidak pernah menggesernya); tanda air dijepit ≤ jam server + 10 menit.

## Tahap 1–2 (cabang `perbaikan/hemat-baca`) — yang dibangun

| Bagian | Saklar MATI (bawaan) | Saklar NYALA |
|---|---|---|
| Pendengar | persis sebelum 7 Okt (dicek jsc: satu pendengar penuh per koleksi + katalog) | V/S/F/N untuk 48 koleksi hemat, tetap & jejak seperti dulu |
| Kupas `capServer` sebelum memori | ya | ya |
| Cap jam server di tulisan koleksi hemat (`tulisBerkas`, `perbaruiBerkas`, `pulihkanBerkas`) | ya | ya |
| Batu nisan di batch hapus (koleksi hemat) | ya, **sesudah aturan v7 terbukti** di perangkat itu (1 baca sekali) | ya |
| Denyut owner `capServer` + versi `baru-c1` | ya | ya (+ ringkasan baca hari ini) |
| Kasir darurat `kasir-v33`: nota lewat REST `:commit` + `REQUEST_TIME`; ditolak → cara lama (PATCH, `updateMask` = kolom karcis) | ya | ya |
| Kunci tab, rem, gerbang uang-kritis & katalog tambahan | tidak | ya |
| `cacheSizeBytes: CACHE_SIZE_UNLIMITED` | tidak (bawaan) | ya |

**Tidak dicap (sengaja, dijaga uji statis):** tutupBukuAcara (kirim ulang identik SDK harus lolos `tulisUlangSama` v6), pesanan & denyut staf (rules
membatasi kolomnya), setelan/akun/permintaan (`tetap`, selalu didengar penuh), logAktivitas (jejak berbatas), ringkasanKasir (bentuk beku = sistem lama),
arsipTahun (tidak didengar).

**Rules v7** (`firestore.rules`; `firestore.rules.v6` disimpan utuh) — HANYA menambah: `ulangKasirBercap()` di update penjualan untuk kasir@ (hanya
`capServer` yang berbeda: jam server permintaan itu, atau dibuang oleh kiriman ulang HP kasir-v32), dan blok `batuNisan` (owner, `capServer == request.time`).
Uji server: `docs/uji-rules-v7.md`.

## Tinjauan 7 Okt (penyanggah) — yang dibetulkan sebelum PR

| Temuan | Akibat sebelum dibetulkan | Perbaikan | Uji (`uji_hemat_baca.py`, kecuali disebut) |
|---|---|---|---|
| Kirim ulang HP < kasir-v33 saat NYALA | nota yang sudah disentuh perangkat owner, dikirim ulang tanpa cap → ditolak → "ditolak" di HP → catat ulang (dobel) | rules: `ulangKasirBercap` menerima cap yang dibuang; pendeteksi tidak menyentuh catatan lahir tanpa cap di koleksi yang dengar penuh karena gerbang penulis | T1 + kontrol; `periksa_rules.py` + kontrol; Playground ★A5/★B8 |
| `capServer` di masa depan (2099) | jam server perangkat ikut 2099 → tanda air & batas delta 2098 → ubahan biasa tidak terdengar | jam server hanya dari gema denyut; cap data tidak menggeser jam | T2 + kontrol |
| Lahir ulang tanpa cap sesudah nisannya | tersembunyi selamanya; hitungan beda → baca penuh tiap hari; gerbang katalog & uang-kritis tertutup | bukti "masih ada di server" dari baca penuh (rekam, tahan muat ulang) + sentuh lewat isi MENTAH; nisan baru → hitungan dinilai ulang | murni + T3 + C8 + kontrol |
| Temuan gagal dikirim | dibuang diam-diam | antrean di rekam, diulang tiap menit ≤ 5 kali, sisanya disebut di layar | T4 + C9 + kontrol |
| kasir-v33 bergantung urutan "v7 dulu" | di v6 / v3 kirim ulang `:commit` ditolak → "ditolak" → dobel | `:commit` ditolak → cara lama PATCH + `updateMask` (cap yang ada dibiarkan) → lolos `tulisUlangSama` | E (fungsi asli di jsc, rules v3/v6/v7) + kontrol; peramban CI `uji_antrean_kasir.py` |
| Baris "statis" siap-nyala saat NYALA | semua catatan hemat terhitung "tanpa cap" | cap dari simpanan sesi hemat | C10 + kontrol |
| Bn tertahan koleksi sepi | nisan berbulan-bulan dibaca ulang tiap buka | Bn = jam baca penuh terakhir tiap koleksi − 60 menit; jam itu dijepit ≤ jam server gema denyut terakhir + 10 menit (jam perangkat yang melompat maju tidak menaruh Bn di masa depan) | T5 + kontrol |
| Sesudah tutup buku | catatan arsip = "hilang tanpa kabar" → batu nisan massal / gen | bagian "hilang" dilewati selama tutup buku berubah sejak baca penuh terakhir | T6 + kontrol |
| Kontrol (c) | berbunyi karena SyntaxError | kerusakan semantik, berbunyi di saringan nisan | kontrol (c), (c2)–(c5) |
| Umur denyut dari jam penulis | tab lama berjam terlambat > 15 menit dianggap "sudah lama" | jam server saat denyut terlihat berubah | murni + T7 + kontrol |

**Tidak dikerjakan:** rules "capServer wajib == request.time di semua koleksi hemat" (48 blok, termasuk tulisan staf — terlalu lebar untuk tahap ini;
perangkat sudah kebal cap masa depan, catatannya tetap tampil dan tidak menggeser apa pun).

## Keputusan tahap ini yang diambil sendiri (bukan dari spesifikasi kata per kata)

- **Saklar per perangkat** (localStorage `miqbal_hemat_saklar_v1`, tombol di Menu › Toko ini › Perangkat & antrean › Hemat baca, dua ketukan, lalu
  muat ulang) — bukan dokumen toko `aturanToko/hematBaca`. Jalan darurat: `/baru/?hemat=mati`. Mematikan = kembali dengar penuh, tanpa terbit ulang.
- **Batu nisan menunggu bukti aturan v7** (owner bisa membaca `batuNisan`) — kode ini aman walau tergabung sebelum rules v7 terbit: hapus tetap seperti dulu.
  Saklar NYALA juga butuh bukti itu.
- **Kunci tab hanya saat NYALA** (MATI = tidak berubah apa-apa).
- **Pendeteksi jalan di setiap baca penuh**, bukan hanya baca penuh harian — tanpa itu baca penuh perangkat mana pun "menelan" ubahan Console diam-diam
  sebelum perangkat pendeteksi melihatnya (temuan uji server mainan B6).
- `capServer` denyut owner dipakai sebagai gema jam server (spesifikasi: `padaServer`); `padaServer` tetap ikut dikupas.

## Kelengkapan — SATU sumber (7 Okt, #111 × Paket C)

`hbBelumLengkap(c)` (murni) → `null` (lengkap) atau `{ jenis, sebab }`; `hbSesi.belumLengkap()` → `{ koleksi: { jenis, sebab } }`, ikut `keadaan()` dan
`firebase.js hematKeadaan()`. `terperiksaK` = bukan jenis "periksa" (rumus 7 Okt + tab yang berhenti — uji K: 16384 kombinasi; sesi nyata dibandingkan
dengan rumus yang ditulis ulang di uji).

| Jenis | Kapan | Sebab di layar (contoh) |
|---|---|---|
| periksa | tab berhenti menerima data (pendengar simpanan mati, atau kalah kunci tab — `berhenti`) | tidak diperbarui lagi di tab ini — muat ulang aplikasi |
| periksa | simpanan perangkat belum terbaca (V) | belum terbaca dari simpanan perangkat — tunggu sebentar |
| periksa | batu nisan (N) belum terkini | belum dicocokkan dengan catatan yang dihapus di server — tunggu sebentar |
| periksa | dengar penuh (F menempel) belum terkini / galat | sedang dibaca penuh — tunggu sampai selesai · gagal dibaca penuh — … · 429: belum bisa dibaca penuh karena kuota baca hari ini habis — ketuk "baca penuh sekarang" sesudah pukul 15.00 WIB (…) |
| periksa | baca penuh WAJIB tapi ditunda rem kuota / gagal (`wajibTotal`) | perlu dibaca penuh, tapi ditunda supaya kuota baca hari ini tidak habis — ketuk "baca penuh sekarang" (…) |
| periksa | ubahan bercap (S) belum terkini | belum dicocokkan dengan ubahan terbaru di server — tunggu sebentar |
| periksa | baca penuh sekali sedang berjalan · hitungan server belum cocok sesi ini | sedang dibaca penuh … · belum dicocokkan dengan server — tunggu sebentar |
| periksa | tanpa internet (keadaan apa pun di atas) | belum dicocokkan dengan server — perangkat ini tanpa internet |
| harian | terperiksa, tapi baca penuh terakhir perangkat ini BUKAN hari kuota ini dan baca penuh harian toko hari ini belum selesai | belum dibaca penuh sejak kuota baca direset pukul 14.00/15.00 WIB — ketuk "baca penuh sekarang" (Menu › Toko ini › Perangkat & antrean › Hemat baca — `HB_TEMPAT`, PR #121) |
| harian | baca penuh harian toko hari ini selesai, tapi `temuanTunda` jenis catatan ini > 0 (sentuhan gagal permanen / bulan terkunci) | punya ubahan yang ditemukan baca penuh harian toko tapi belum sampai ke perangkat ini — ketuk "baca penuh sekarang" (…) |
| harian | baca penuh terakhir gagal 429 (kuota habis), hitungan cocok | belum bisa dibaca penuh karena kuota baca hari ini habis — ketuk "baca penuh sekarang" sesudah pukul HH.MM WIB (…) |
| harian | jam server belum diterima (hari kuota tidak diketahui) | belum bisa dipastikan sudah dibaca penuh sejak kuota baca terakhir direset (jam server belum diterima) — tunggu sebentar |

Lengkap: dengar penuh terkini; atau terperiksa DAN (dibaca penuh perangkat ini pada hari kuota ini ATAU baca penuh harian toko hari ini selesai tanpa
`temuanTunda` jenis catatan itu). Baca penuh harian toko menulis `selesai` hanya sesudah antrean temuan pendeteksi habis (sanggahan 7 Okt); yang gagal permanen
atau dilewati karena bulannya terkunci (`sentuhCap` → `lewat`) dihitung per jenis catatan di `temuanTunda`. Kalimat untuk banyak jenis catatan
(`hbKalimatBelum`): "data perangkat ini <keadaan> (n jenis catatan) — <petunjuk>; m jenis catatan lainnya <sebabnya>" — sebab satu jenis tidak dipinjamkan ke
yang lain. Keputusan yang memakainya dan yang sengaja tidak: lihat `baru/BACA-DULU.md` bab Hemat baca, bagian "Kelengkapan".

## Belum dibangun (tahap berikut / bila perlu)

- Jejak (logAktivitas) atas permintaan saja saat nyala (±150 baca per buka masih dibayar).
- Pembersih nisan per dokumen (`getDocFromServer`) & `nisanTuntas`; arsip besar → `clearIndexedDbPersistence`.
- Deteksi "antrean warisan" (mutasi kode lama di antrean IndexedDB) — pendeteksi statis & pendeteksi F menangkap akibatnya.
- Uji peramban CI dengan emulator Firestore (demosi tab, F berkueri sendiri, limbo, REST `:commit` terhadap rules v7) — kasus B1–B12 spesifikasi.
- Perkiraan baca toko dari denyut adalah perkiraan; tagihan sebenarnya dibaca **owner** di Console › Firestore › Usage: patokan sehari sebelum perangkat
  pertama dinyalakan (panel hanya menampilkan "Perkiraan baca hari ini" saat nyala), hari nyala tidak dipakai pembanding, lalu Usage dicocokkan dengan
  perkiraan toko sesaat sebelum reset. Langkahnya: `docs/prosedur-pulih-darurat.md` bab "Hemat baca" dan `baru/BACA-DULU.md` bab Hemat baca, langkah 6.
