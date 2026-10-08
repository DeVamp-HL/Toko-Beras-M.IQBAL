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
  Tombol manual menembus; baca penuh WAJIB karena tutup buku berubah juga (audit P5, bagian di bawah).
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

## Hemat baca × arsip tutup buku (audit P5, 8 Okt) — perangkat yang tertutup selama ritual

**Celah.** Arsip tutup buku menghapus TANPA batu nisan (`firebase.js arsipkanBerkas`), jadi catatan tahun lalu di simpanan perangkat owner yang tertutup
selama ritual hanya dibuang baca penuh (F); catatan yang lebih tua dari jendela S tidak dibuang S maupun N. Saldo pembukanya bercap baru → datang lewat S.
Dulu: V pertama → simpanan "dipercaya" (hanya jumlah yang dibandingkan) → siap, pil "memuat…" lepas SEBELUM berita acara terbaca; S membawa saldo pembuka →
memori = catatan tahun lalu + saldo pembuka = stok, bon & utang **DOBEL** di Jual, Gudang, Pelanggan, bon (uang-kritis, katalog & kartu Paket C sudah
tertahan). Baca penuh karena tutup buku berubah tergolong otomatis → bisa ditahan rem kuota (denyut perangkat ritual ±45 rb baca hari itu) → dobel bertahan
sampai reset kuota. Berita acara dari SIMPANAN dulu (basi) → tutup buku tampak tidak berubah → F tidak jalan sama sekali sampai jawaban server tiba.

**Obat (`hemat-baca.js`, `firebase.js`).**

| Bagian | Sekarang |
|---|---|
| (a) rencana | tutup buku berubah sejak baca penuh terakhir (`bkBeda`), atau baca penuh sesudah tutup buku terputus di sesi lalu (`bkCampur`) → baca penuh **WAJIB**: seperti tombol (menembus rem, tidak turun ke delta, tidak dihitung otomatis), didahulukan dari permintaan otomatis (hitungan beda). Gagal → sebabnya disebut, dicoba lagi sesudah 10 menit seperti baca penuh otomatis (bukan tiap kabar koleksi tetap — tiap ulang = seluruh koleksi dibaca) |
| pelindung | **Tidak ada tirai yang menutup layar** (sanggahan kedua P5): "siap" hanya menurunkan pil kepala "memuat…" & melepas penjarangan gambar (`inti/jadwal.js setelMuat`); layar SELALU menggambar memori. Tirai sungguhan hanya `tiraiTab` (tab ganda / pendengar simpanan mati). Jadi MEMORI satu-satunya pelindung: tidak pernah campuran (catatan arsip + saldo pembuka, atau jenis catatan beda zaman); kosong hanya bila tidak ada keadaan utuh di perangkat, dan itu DISEBUT (kabar & kelengkapan "disembunyikan") |
| (b) TAHAN | memori BEKU = isi simpanan saat mulai ditahan, dengan catatan yang DISENTUH perangkat ini sendiri mengikuti simpanan perangkat — tulisan (`catatTulis` dari `tulisBerkas` & `perbaruiBerkas`; `pulihkanBerkas` tidak — berjalan saat tutup buku dibatalkan, yang didengar penuh) dan hapus (`catatHapus`): hapus hilang seketika (SDK membuangnya dari simpanan), catatan yang ditulis lagi dengan id sama / hapus yang DITOLAK server tampil (lensa hari biasa PR #122); tanpa S; belum terperiksa (uang-kritis, katalog, kunci bulan & pajak tertahan). DITAHAN selama: (1) berita acara tutup buku belum dijawab SERVER — saat dibuka, DAN sejak server berhenti menjawab di tengah sesi (lihat "berita acara"); (2) **PENGHALANG BERSAMA**: ada koleksi yang menunggu baca penuh karena tutup buku (`tahanTb`: baca penuh sesi ini belum menjawab koleksi itu DAN tutup buku berubah sejak baca penuh terakhirnya / simpanannya bisa bercampur — kecuali dengar penuh KARENA tutup buku berjalan) → SEMUA koleksi hemat ditahan, dilepas SERENTAK saat yang terakhir selesai. Stok, bon & utang dihitung lintas koleksi: saldo pembuka di `batchMasuk`/`piutangMutasi` dkk., catatan 2026 juga di `penjualan` yang tidak punya saldo pembuka — dulu dilepas per koleksi → stok terpotong DUA KALI tanpa kabar (sanggahan kedua). "Menjawab" = baca penuh sekali selesai, atau dengar penuh TERKINI (simpanan koleksi itu = server). Koleksi yang sudah menjawab tapi menunggu yang lain: pil lepas, kelengkapan "sudah dibaca penuh, menunggu jenis catatan lain …". Putus / baca penuh gagal di tengah = semua tetap beku (keadaan sebelum ritual), tidak dilepas sebagian. Koleksi yang dengar penuh karena penulis tanpa cap (HP kasir lama, kasir.html, tab lama) juga ditahan (sanggahan P5) |
| (b) berita acara | `firebase.js kabariTetap` meneruskan `acaraServer` = `fromCache` pendengar `tutupBukuAcara` SAJA (snapshot server koleksi tetap lain — denyut, setelan — bukan jawaban berita acara; mutasi M31 dulu lolos, kini C14 + kontrol). Sanggahan kedua: **tidak lagi "sekali benar, tetap benar"** — SDK menandai berita acara "dari simpanan" saat server berhenti menjawab, atau peramban mengabarkan offline → sesi menahan SAAT ITU (memori = keadaan terakhir yang dijawab server, aman: sejak itu tanpa data server baru); tersambung → ditahan sampai berita acara dijawab server lagi (bila SDK tidak sempat menandai "dari simpanan" — putus sebentar — jawaban terakhirnya masih berlaku). S tetap menempel selama ditahan: ubahannya hanya mengisi simpanan. Buka biasa: memori seketika dari simpanan (beku), pil memuat menunggu satu jawaban server berita acara |
| (b) di tengah sesi | penahanan yang mulai DI TENGAH sesi (memori tadinya hidup) dibekukan SEKETIKA untuk semua koleksi (dulu malas di kabar simpanan berikutnya — yang bisa sudah membawa saldo pembuka). Mulai karena berita acara berganti selagi S/F menempel (sambungan mati TANPA kabar: Mac tidur, tab ditangguhkan) atau selagi tutup buku berjalan → simpanan bisa campuran → **disembunyikan** + rekam `bkCampur` (muat ulang juga kosong) |
| (b) bercampur | rekam `bkCampur` dipasang: F selama tutup buku BERJALAN; simpanan yang benar-benar BERUBAH selama ditahan (data server lewat S/F/limbo — bukan tulisan/hapus sendiri) saat tutup buku berubah (sanggahan kedua: dulu dipasang saat F wajib dipasang → F yang macet sebelum membawa apa pun membuat muat ulang berikutnya kosong padahal simpanannya bersih); penahanan tengah sesi yang tidak aman. Dibuang saat F selesai tanpa tutup buku berjalan, atau dengar penuh terkini ketika ritual berakhir |
| disembunyikan | memori KOSONG (+ tulisan sendiri) untuk SEMUA koleksi hemat bila, saat penahanan mulai: ada koleksi bertanda `bkCampur`, atau jenis catatan BEDA ZAMAN (rekam `bk` tidak sama — aplikasi ditutup di tengah penghalang: sebagian sudah sesudah ritual, sebagian belum; sanggahan kedua), atau penahanan tengah sesi yang tidak aman. Ditetapkan sekali per penahanan (koleksi yang selesai lebih dulu tidak membuat campuran), padam saat dilepas. Kabar "Angka disembunyikan (tampil kosong — bukan nol) … — <yang ditunggu: tanpa internet / server belum menjawab / kuota baca habis, dibaca lagi sesudah pukul HH.00 WIB / tunggu>" dan kelengkapan "disembunyikan sampai dibaca penuh — …" DIDAHULUKAN dari kalimat server diam / F gagal / tanpa internet (dulu memori kosong mengaku "angka dari simpanan perangkat ini"). Pengecualian: berita acara menyebut tutup buku BERJALAN dan (dijawab server, atau perangkat ini PEMEGANG ritual — `acara.pemegang.id` = `idPerangkat`): memori = simpanan, keadaan ritual yang diikutinya (Mac pemegang yang ditutup di tengah ritual — K11 TIDAK MUAT: sisa arsip terbaca). Sanggahan kedua: dulu pengecualian ini untuk SEMUA perangkat → iPad yang ikut dengar penuh, ditutup di tengah ritual, dibuka tanpa internet / server diam = DOBEL berjam-jam. Berita acara berganti → ditentukan ulang |
| tidak ditahan | perangkat yang MENJALANKAN / terbuka selama ritual (dengar penuh KARENA tutup buku berjalan, berita acara terjawab server): memori mengikuti ritual seperti dulu — saldo pembuka masuk; catatan arsip keluar seketika di perangkat yang mengarsip, sedangkan perangkat yang dibuka di tengah ritual memegang catatan yang sudah diarsipkan sampai limbo baca penuhnya selesai |
| tanpa internet | pil tidak menggantung: siap (memori tetap beku), pil kepala & kabar mengaku. Juga saat putus di tengah baca penuh wajib. Hari biasa juga: putus = memori beku sampai berita acara dijawab server lagi (tulisan perangkat ini tetap tampil) |
| server diam | tersambung tapi berita acara belum dijawab server 30 detik sejak dibuka / tersambung lagi (kuota baca habis sampai reset 14.00/15.00 WIB, sinyal lemah — sanggahan P5): siap (memori tetap beku), belum terperiksa; kabar, kelengkapan & penolakan uang-kritis menyebut "server belum menjawab sejak aplikasi dibuka (kuota baca habis atau sinyal lemah)". Simpanan TIDAK dipercaya (kosong padahal rekam ≥ 1) → tetap memuat, kelengkapan "belum bisa dihitung (<sebabnya>) — server belum menjawab …" (M14). Tanda server diam dihitung lagi dari saat tersambung (dulu menempel dari masa tanpa internet → sebab menyesatkan) |
| kabar | DIHITUNG dari keadaan sekarang (dulu dicatat saat pil lepas lalu tertinggal basi — "Tanpa internet: tutup buku berubah …" berjam-jam sesudah baca penuh selesai): disembunyikan › server diam › tanpa internet › baca penuh gagal |
| kelengkapan | baca penuh yang sedang berjalan disebut lebih dulu dari "ubahan terbaru"; memori beku karena sebab di luar koleksi itu (berita acara belum dijawab server lagi, penghalang bersama) = belum lengkap walau dengar penuh terkini / hitungan cocok; uang-kritis menolak selama ditahan apa pun (juga dengar penuh terkini) |

**Uji** (`alat-uji/uji_hemat_baca.py`, jsc, server mainan dengan baca penuh LAMBAT: dipasang → jawaban server masuk simpanan → limbo membuang catatan arsip):
murni rencana wajib; B1 (perangkat baru: pil memuat tetap selama F berjalan walau berita acara terjawab), B2 (buka biasa: memori seketika, siap sesudah berita
acara dari server, tanpa baca penuh); **T6b** (tertutup selama ritual, F lambat: tidak pernah dobel di tiap tahap, pil memuat, tanpa S, tulisan sendiri
tampil; + rem kuota aktif dari denyut perangkat ritual: F tetap jalan & selesai tanpa ketukan); **T6c** (berita acara dari simpanan dulu); T6d (F terputus di
tengah limbo → sesi berikut memori kosong, bukan dobel); T6e (perangkat ritual sendiri tidak dibekukan); T6f (F wajib gagal: pil lepas, memori beku, jeda 10
menit); T6g (simpanan bercampur tanpa internet: pil lepas, memori kosong, kabar mengaku); C14 (`acaraServer` dari `fromCache`), C15 (`tulisBerkas` →
`catatTulis`; kiriman uang-kritis yang ditolak sebelum dikirim tidak dicatat). T6b & T6c MERAH di kode sebelum obat; 17 kontrol baru (P5a–P5f), kontrol (i)
disesuaikan. Limbo SDK sungguhan belum diuji di peramban (lihat "Belum dibangun"; uji peramban hanya di runner CI).

**Sanggahan P5 (8 Okt).** Server mainan: pendengar simpanan kini berbunyi HANYA bila isi simpanannya berubah (seperti SDK) — dulu dikabari ulang tiap S/F
dipasang, jadi baris pelepas memori beku (`selesaiF`, `lepasTahan`) tidak dijaga uji apa pun; mode "server diam" (tersambung, server tidak menjawab) dan
hitungan server yang dijawab belakangan. Uji baru: **T6e2** (Mac yang menjalankan ritual ditutup di tengah ritual, dibuka lagi saat server diam: memori =
simpanannya, bukan kosong; pil lepas sesudah 30 detik, kabar & kelengkapan "server belum menjawab", uang-kritis menolak), **T6e3** (perangkat lain ditutup di
tengah ritual, ritual selesai selagi tertutup: berita acara simpanan "terkunci" → simpanan; server "selesai" → kosong sampai baca penuh selesai), **T6h**
(putus internet di tengah baca penuh wajib: pil lepas, memori beku; hapus sendiri hilang dari memori beku), **T6i** (dengar penuh karena kasir.html di
perangkat tertutup selama ritual: ditahan, tidak dobel; terkini → memori = server sebelum hitungan menjawab), **T6j** (server diam tanpa tutup buku: 29 detik
memuat, 30 detik siap dengan sebabnya); T6d ditambah catatan baru perangkat lain selama tombol baca penuh. T6e2, T6e3, T6i & T6j MERAH di kode sebelum
sanggahan; 14 kontrol baru (P5b, P5d, P5e, P5f), 4 kontrol P5 disesuaikan — seluruh `--kontrol` berbunyi.

**Sanggahan kedua P5 (8 Okt).** Temuan: tidak ada tirai yang menutup layar (siap = pil saja), jadi semua keadaan yang dianggap "di balik tirai" tergambar;
tahan per koleksi padahal stok/bon/utang lintas koleksi (DOBEL di jalur utama: batchMasuk selesai lebih dulu dari penjualan); sesi HIDUP yang putus / tidur
selama ritual membekukan malas simpanan yang sudah dibawa S; pengecualian "berita acara menyebut tutup buku berjalan" untuk semua perangkat (iPad dibuka tanpa
internet / server diam = DOBEL); memori kosong mengaku "angka dari simpanan perangkat ini"; mutasi M31 (acaraServer dari koleksi tetap lain), M14 (server
diam + simpanan tidak dipercaya), M20 (layar tidak dikabari saat pil lepas) lolos uji. Obat: tabel di atas (pelindung, TAHAN penghalang bersama, berita acara
tidak lengket, di tengah sesi, bercampur bila berubah, disembunyikan + beda zaman + pemegang, kabar dihitung). Server mainan: `putus` = kabar peramban + SDK
menandai berita acara "dari simpanan"; `sambung` = server menjawab berita acara lagi; `tidur`/`bangun` = sambungan mati tanpa kabar apa pun; `jawab` (server
diam berakhir) tanpa kabar peramban; `keluar.berubah` dihitung. Uji baru **T6k** (lintas koleksi batchMasuk − penjualan, putus di tengah), **T6l** (ditutup di
tengah penghalang → beda zaman → disembunyikan), **T6m** (sesi hidup putus selama ritual: dua urutan + kuota habis), **T6n** (tidur tanpa kabar → disembunyikan),
**T6o** (F wajib macet sebelum membawa apa pun → muat ulang = simpanan), **T6p** (bercampur + kuota habis → kabar disembunyikan), **T6q** (perangkat lain,
berita acara simpanan "terkunci", server diam / tanpa internet → kosong), **T6r** (M14), **T6s** (tanda server diam dari masa tanpa internet), **T6t** (pemegang
yang ritualnya diambil alih → ditentukan ulang), **T6u** (semua koleksi dengar penuh → lepas sebelum hitungan), **T6v** (uang-kritis selagi berita acara belum
dijawab lagi); T6e2 (berita acara pemegang), T6e3, T6g, T6h (kabar tidak basi), T6i (penghalang bersama), T6j (layar dikabari — M20), C14 (tidak lengket + M31)
disesuaikan. T6k–T6t & T6v (+ T6e3, T6g, T6h, T6i, C14 yang disesuaikan) MERAH di kode sebelum obat — 19 merah; T6u & T6j (M20) penjaga baris;
kontrol baru P5g–P5l, M14, M20, M31 (+ 14 kontrol P5 disesuaikan ke baris barunya) — seluruh `--kontrol` (122) berbunyi.

**Lensa hari biasa (audit PR #122, 8 Okt).** Sejak sanggahan kedua, putus = memori beku juga di hari biasa (hemat baca NYALA, tanpa tutup buku).
Temuan berat: catatan yang DIHAPUS perangkat ini lalu DITULIS LAGI dengan id sama di sesi yang sama hilang dari memori selama beku (putus bisa berjam-jam, juga
jendela sesudah tersambung sebelum berita acara dijawab), begitu juga hapus yang DITOLAK server — `pasokK` membuang semua id `hapusSesi` SESUDAH memasukkan
tulisan sendiri. Jalur nyata dengan id tetap: katalog harga literan/karung (id = merek) & kemasan (merek_ukuran) — "Hapus" lalu harganya disetel lagi → tuts
Jual "harga?"; kartu pelanggan (id = kunci nama) — Satukan lalu nama lama ditambah lagi; MDR tutup hari diulang (`mdr-<tgl>`); harga pasar & pajak omzet luar.
Obat (satu putaran di `pasokK`): catatan yang disentuh perangkat ini (tulis ATAU hapus) mengikuti simpanan perangkat — hapus tetap hilang seketika, ditulis lagi /
hapus yang ditolak tampil. Tidak membuka jalan dobel: yang disentuh hanya catatan perangkat ini (saldo pembuka ditulis perangkat ritual, yang tidak ditahan).
Uji **T6w** (MDR dihapus lalu ditulis lagi, putus, ditulis lagi selagi putus, 3 jam; hapus selagi beku tetap hilang) & **T6x** (hapus ditolak server, putus 2
jam) MERAH sebelum obat; kontrol (P5b) "dihapus perangkat ini sendiri" disesuaikan ke baris baru, 2 kontrol baru P5m (putaran lama; obat hanya di tulis ulang —
hapus yang ditolak tetap hilang) — seluruh `--kontrol` (124) berbunyi.

**Sisa yang diakui.** Selama baca penuh wajib berjalan (detik sampai ± semenit untuk ±18 rb catatan; berjam-jam bila kuota habis di tengahnya), layar menggambar
isi simpanan perangkat itu saat terakhir dibuka / saat server berhenti menjawab, untuk SEMUA jenis catatan (tanpa catatan perangkat lain sesudahnya — saldo
stok, piutang & utang bisa beda dengan server, jangan dipakai) atau kosong (disembunyikan, dengan kabar), dengan "memuat…" / "memeriksa data (n)" di kepala.
Selama berita acara (dari server, atau milik perangkat ini sebagai pemegang) menyebut tutup buku berjalan, perangkat itu menggambar keadaan ritual yang terakhir
diikutinya (catatan tahun lalu yang belum diarsip + saldo pembuka — seperti perangkat yang terbuka selama ritual). Sambungan yang mati TANPA kabar (tidak ada
offline dari peramban, SDK tidak menandai "dari simpanan") lalu hidup lagi dengan kabar simpanan berisi saldo pembuka SEBELUM jawaban berita acara: campuran
bisa tergambar sesaat (antara dua kabar SDK; urutan SDK biasanya berita acara dulu karena pendengarnya didaftarkan lebih awal) — begitu berita acara tiba,
disembunyikan. Server diam: sesudah 30 detik angka simpanan tampil, dengan kabar & pil "memeriksa data"; baca penuh wajib yang macet karena kuota habis SESUDAH
berita acara terjawab tetap "memuat…" (dan tanpa kabar server diam) sampai reset — memorinya tetap utuh (beku). Hari biasa (hemat baca NYALA, tanpa tutup buku):
tiap buka & tiap tersambung lagi, memori beku ±1 jawaban server (berita acara); S baru dipasang SESUDAH jawaban itu, jadi nota perangkat lain tampil sesudah ±2
jawaban server (saklar MATI: 1). Server diam di hari biasa: kiriman sesi lalu yang tertunda lalu DITOLAK server tetap tampil di memori beku sampai server
menjawab (saklar MATI: hilang seketika) — kecil kemungkinannya. Butir "Perangkat lain sesudah ritual" di daftar periksa 1 Jan (`docs/prosedur-pulih-darurat.md`, PR #119) tetap berlaku sebagai
penjaga kedua: buka, tunggu "memuat" & pil hilang, baru berjualan.

**Sisa yang diakui — lensa hari biasa (audit PR #122, 8 Okt; temuan sedang/rendah, TIDAK dibetulkan di cabang ini).**

- (sedang) Memori beku bisa MACET sampai dimuat ulang bila kabar `online` peramban tidak sampai ke halaman (hilang saat tab ditangguhkan / dipulihkan dari
  bfcache, `navigator.onLine` tertinggal false) padahal SDK sudah tersambung dan berita acara sudah dijawab server: `bkServer = acaraSrv && G.online`, dan
  `G.online` hanya berubah dari kabar `online`/`offline` window (`firebase.js`). Selama macet nota perangkat lain & bayar bon dari iPad / HP kasir masuk simpanan
  tapi tidak tampil, kabar kosong, kelengkapan "perangkat ini tanpa internet", uang-kritis "sambungkan internet dulu". Jalan keluar: muat ulang (`G.online`
  dibaca ulang dari `navigator.onLine`). Sebelum P5 memori tetap hidup dari simpanan (hanya uang-kritis yang menolak). Premis "kabar online hilang" tidak bisa
  dibuktikan di jsc; mekanismenya terbukti. Kabar `offline` yang tidak disusul `online` (rendah) adalah bentuk yang sama: beku tanpa batas sampai kabar
  `online` berikutnya atau muat ulang — yang tidak disarankan kalimatnya.
- (sedang) Pendengar berita acara (`tutupBukuAcara`) mati sesudah hanya memberi jawaban dari simpanan, atau tidak pernah dijawab server → SEMUA koleksi hemat
  beku selamanya walau server tetap menjawab (`tolak()` di `firebase.js` tidak memasang ulang pendengar koleksi tetap; `setelTetap` tetap menerima
  `acaraServer` false). Akibatnya nota perangkat lain tidak tampil di Jual/Gudang/Pelanggan, uang-kritis ditolak terus, kabar & kelengkapan menyebut "server
  belum menjawab sejak aplikasi dibuka … tidak perlu muat ulang" padahal muat ulang justru jalan keluarnya; simpanan bercampur = memori kosong selamanya.
  Saklar MATI tidak terkena (hanya layar tutup buku kehilangan berita acara). Jarang: owner punya akses payung di rules v3/v7, dan SDK 10.13 mencoba ulang kuota
  habis tingkat aliran dengan backoff maksimum — kuota habis saja tidak mematikan pendengar ini. Jalan keluar owner: muat ulang, `?hemat=mati`, atau saklar panel.
- (rendah) Kalimat `HB_KABAR_SERVER_DIAM` / `HB_SEBAB_SERVER_DIAM` selalu berbunyi "sejak aplikasi dibuka", juga untuk server yang berhenti menjawab di TENGAH
  sesi (aplikasi sudah terbuka berjam-jam) dan untuk berita acara yang terlambat > 30 detik sesudah tersambung lagi — patokan waktunya salah (tanda server diam
  dihitung dari saat tersambung). Di keadaan macet butir pertama kabarnya malah kosong.
- (rendah, belum terbukti) Mematikan hemat baca saat server belum menjawab (kuota habis): pendengar penuh saklar MATI menggambar seluruh simpanan tanpa saringan
  batu nisan → catatan yang dihapus perangkat lain di luar jendela S sejak baca penuh terakhir (≤ 14 hari) bisa tampil lagi sampai server menjawab (sesudah
  reset). Prosedur bab Hemat baca butir 4 justru menganjurkan mematikan bila kuota habis (429). Bukan dari P5 (sudah ada sejak 7 Okt); hari ritual prosedur
  sudah melarang `?hemat=mati`.

## Belum dibangun (tahap berikut / bila perlu)

- Jejak (logAktivitas) atas permintaan saja saat nyala (±150 baca per buka masih dibayar).
- Pembersih nisan per dokumen (`getDocFromServer`) & `nisanTuntas`; arsip besar → `clearIndexedDbPersistence`.
- Deteksi "antrean warisan" (mutasi kode lama di antrean IndexedDB) — pendeteksi statis & pendeteksi F menangkap akibatnya.
- Uji peramban CI dengan emulator Firestore (demosi tab, F berkueri sendiri, limbo, REST `:commit` terhadap rules v7) — kasus B1–B12 spesifikasi.
- Perkiraan baca toko dari denyut adalah perkiraan; tagihan sebenarnya dibaca **owner** di Console › Firestore › Usage: patokan sehari sebelum perangkat
  pertama dinyalakan (panel hanya menampilkan "Perkiraan baca hari ini" saat nyala), hari nyala tidak dipakai pembanding, lalu Usage dicocokkan dengan
  perkiraan toko sesaat sebelum reset. Langkahnya: `docs/prosedur-pulih-darurat.md` bab "Hemat baca" dan `baru/BACA-DULU.md` bab Hemat baca, langkah 6.
