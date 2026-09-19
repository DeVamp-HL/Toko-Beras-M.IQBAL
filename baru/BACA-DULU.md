# Sistem baru — `baru/`

Tampilan baru di atas **data yang sama** dengan `index.html` (Firestore proyek `toko-beras-m-iqbal`, 28 koleksi, akun owner yang sama).
Hidup berdampingan di alamat `/baru/`; `index.html` tetap alat yang dipakai toko sampai yang baru terbukti.
Keputusan owner 13 Sep 2026: desain ulang termasuk UI **tanpa mengubah data toko**; 17 Sep: *"mulai sambungkan ke data asli"*.

## Putaran 1 (19 Sep 2026) — layar JUAL, baca
- Rak (Sering · Literan · Kemasan · Karung) dibaca dari data toko lewat **mesin beku yang sama** dengan `index.html`.
- Keranjang, nego, potongan, antrean (struk parkir **memegang** stoknya), bayar (Tunai/QRIS/Bon), nama pembeli, kartu Hari ini.
- Aturan owner yang dipasang: pembulatan Rp500 ke atas untuk **Tunai dan Bon**, QRIS persis (17 Sep); uang kurang → sisanya jadi bon atas nama (17 Sep); siapa cepat dia dapat (17 Sep).
- Belum: Wadah, Repack, Retur, Pesanan, cetak struk, dan semua layar lain (masih di sistem lama).

## Putaran 2 (19 Sep 2026) — nota DICATAT
- Satu pintu tulis `toko.tulisDokumen()` → Firestore `writeBatch` (semua dokumen satu nota masuk bersama; index.html menulis satu per satu) + satu baris `logAktivitas` per dokumen; atribusi `oleh/perangkat/diubah*` persis `simpanKeFirestore()` lama. Tanpa internet: tulisan mengantre di cache tetap Firestore, layar bilang "menunggu server".
- Bentuk dokumen = `simpanKeranjangJual()` index.html: potongan dibagi proporsional (sisa ke baris terakhir), pembulatan melekat ke baris terakhir bernilai (`pembulatan`), `uangDiterima`/`kembalian` di tiap baris tunai, `hargaAsliSatuan` + `negoSelisih`, `trxId` satu nota; **uang kurang** = semua baris `Kredit` + satu `piutangMutasi` tipe `bayar` sebesar uang yang diterima; literan berkantong = `stokBahanLiteran {id: id+1, tipe 'pakai'}`. Diuji: kunci dokumen yang dihasilkan ⊆ kunci baris nyata di cadangan toko.
- KR1 untuk bon murni (belum terdaftar / batas belum terbentuk / lewat batas 2× belanja bulanan) — owner bisa **buka kredit sekali** (tanda `kreditDibukaOwner`), tanpa PIN karena ini alat owner sendiri. Bayar sebagian tidak kena KR1 (sama dengan live).
- Stok dicek ULANG saat mencatat (bisa berubah sejak dimasukkan). Belum ada jalur "tembus stok" — kalau kurang, ditahan.
- **Batalkan nota barusan** (90 detik): baris ditandai `dibatalkan` + `alasanKoreksi` (tidak dihapus, seperti `mulaiBatalkanTrx` live); kantong literan `id+1` dan pelunasan sebagiannya dilepas.
- Mode `?cadangan=` = SIMULASI: menulis ke cache lokal saja, dilabeli di layar.
- Belum: Wadah, Retur/Tukar, cetak struk, janji bayar, urungkan sesudah 90 detik (lewat sistem lama).

## Putaran 3 (19 Sep 2026) — paritas layar Jual lama
- **Repacking Dadakan** (jalur `repack`): kg bebas dari kolam karung merek itu (kolam yang sama dengan karung & literan), harga per kg katalog (`cariHargaKarungPerKg`), nama jual bebas (kosong = nama merek). Dokumen `jenis 'repacking'` persis `bangunTrxJualDariForm` 19333: `{merkSumber, namaProduk, totalKg, hppTotalSaatJual, hargaTotal, …}`.
- **Bonus kemasan +1** (pil di baris keranjang): `bonusUnit 1`, `jumlahUnit` = unit bayar + 1 → stok & HPP ikut, uang tidak (`wzTambahItem` 17633). Langit-langit stok dan pemeriksaan ulang saat mencatat menghitung bonusnya.
- **Pengganti retur** (pil di baris; cara lama untuk tukar TANPA nota): `penggantiRetur true`, `nilaiBarangPengganti` = nilai, `hargaTotal 0` — omzet & kas Rp0, HPP tetap keluar, baris ini tidak dapat potongan/pembulatan (19383). Penjaga model B: kalau hari ini ada tukar bernota (`tukarModel 'kreditBarang'`), ketukan pertama cuma memperingatkan.
- **Pesanan** (tombol di keranjang → lembar): catat pesanan baru (bentuk `simpanPesanan` 16224), dipesan → diantar, batalkan; **"catat jualnya"** mengikat keranjang ke pesanan (nama ikut, ikatan ikut diparkir) dan saat nota dicatat, dokumen pesanan `status 'dibayar'` + `trxIdJual` masuk **dalam batch yang sama** (index.html menulisnya terpisah sesudah nota — 16272). Batalkan nota barusan memulihkan statusnya. Pesanan BUKAN uang & BUKAN stok sampai notanya dicatat (G5).
- Belum: Wadah dijual (fitur baru, mesin laba harus diajari dulu), cetak/kirim struk.

## Putaran 4 (19 Sep 2026) — Retur menunjuk nota: uang kembali & tukar
- Jalur **Retur** di layar Jual: daftar nota karung/kemasan 60 hari terakhir (bisa dicari) → ketuk → lembar retur. Nilainya dihitung dari NOTA-nya oleh `rtDasarNota()` yang **dipindah verbatim** (`pembantu.js`): hargaTotal − pembulatan tunai, potongan nota diprorata, ÷ banyaknya; sisa yang boleh kembali = nota − yang sudah diretur di seluruh rantai koreksi. Nota KREDIT / ber-bonus / perlu-koreksi ditolak dengan sebabnya (jalan ketik-tangan masih di sistem lama).
- Wajib: berapa yang kembali (karung boleh sebagian kg, kemasan unit utuh), **boleh dijual lagi?** (layak → kembali ke stok; rusak/ragu → dokumen `karantina` ber-id sama), **alasan** (KR3).
- **Uang kembali**: dokumen `retur` bentuk `simpanRetur()` cabang bernota; boleh ditimpa hanya ke BAWAH dengan alasan (`nominalSistem` + `alasanTimpaNominal`).
- **Tukar**: retur TIDAK ditulis saat itu — diikat ke keranjang (`tukarModel 'kreditBarangGabung'`); nilai barang kembali dipotong sebelum pembulatan (pembulatan atas selisih bersih); saat nota dicatat, penjualan pengganti (`tukarReturId`) + retur (`penjualanPenggantiTrxId`, `hitunganTukarSistem`) + karantina masuk **dalam SATU batch** (index.html menulis berurutan dan menjaga dengan jurnal localStorage; di sini tidak bisa setengah jadi). Tukar tidak bisa bon, tidak bisa bayar sebagian, pengganti tidak boleh lebih murah dari barang kembali; draf dibaca ulang saat mencatat; ikatan ikut diparkir; tukar & pesanan saling meniadakan. Batalkan nota barusan mencabut retur + karantinanya juga.
- Belum: retur TANPA nota (ketik tangan), retur tukar lama yang "yatim" (catat penggantinya / pengganti sudah tercatat) — tetap lewat sistem lama.

## Putaran 5 (19 Sep 2026) — layar RINGKASAN (R2 "Cincin Bersarang"), baca saja
- Desain yang dikunci owner 13 Sep: tujuh skala (Langsung · Menit · Jam · Hari · Minggu · Bulan · Tahun), tiap skala tiga lapis cincin (luar · induk · kakek) + satu angka besar; geometri cincin = rumus papan R2 (tebal ∝ akar nilai, sel berjalan di jam 12).
- Angka dari data toko lewat mesin yang sama: omzet = baris penjualan berlaku; **margin kotor** (K1) dari `hitungLabaRentang` dan layar menyebut baris tanpa modal yang tidak ikut; bon dari `hitungPiutang`, utang pemasok dari `hitungUtangPemasok`, menipis = sisa ÷ laju jual (`hitungLajuPakai`) ≤ `AMBANG_HARI_KRITIS` (verbatim), kas dari `kasPada()`.
- Kejujuran: pembanding selalu **sampai titik yang sama** (kemarin jam segini · minggu lalu sampai hari & jam yang sama · bulan lalu sampai tanggal yang sama) dan **ditolak** kalau jendelanya mendahului catatan pertama toko; periode berjalan bertepi putus, yang belum terjadi tipis, yang sebelum ada catatan "absen" (bukan nol); saldo kas **tidak ditebak** kalau titik kas belum disetel di perangkat itu (titik kas = localStorage sistem lama, asal-usul sama).
- **Gerak & interaksi (putaran 5b — owner 13 Sep: "lebih interaktif, lebih hidup, ada animasi motion dibanding sistem lama")**: layar ini TIDAK digambar ulang; kerangkanya dibangun sekali dan elemennya hidup terus supaya perubahan bisa bertransisi.
  - Ketujuh lapis cincin selalu ada dengan identitas sel tetap (`lapis:urutan`); yang tak berperan menunggu di luar (r 108) / di dalam (r 22) beropasitas 0 → ganti skala = cincin **bergeser masuk/keluar** (transisi `r`, `stroke-dasharray`, `stroke-dashoffset`, tebal, opasitas). Saat pertama tampil cincin **menggambar dirinya** bergiliran.
  - Angka besar **bergulir** ke nilai barunya (rAF, kurva tenggelam); kilau menyapu kartu; teks judul/sub berganti dengan geser halus; kartu-kartu naik bergiliran saat layar dibuka.
  - **Jarum detik** berdetak tiap detik (sudut selalu maju); tiap menit sel berjalan & jendela 60 menit bergeser.
  - Nota baru: tetes emas **terbang** dari tombol Jual ke angka → kartu "mendarat" (pegas + tepi emas) → chip +Rp naik → baris umpan masuk hangat.
  - Interaktif: **ketuk sel cincin** → label & nilainya (mis. "Kamis, 10 Sep · Rp…"), sel lain meredup; **ketuk lapis** (Luar/Induk/Kakek) → pindah ke skala itu; **geser kiri/kanan** di kartu besar → skala berikut/sebelumnya.
  - Penjaga: tab tersembunyi (rAF & transisi beku) → nilai akhir ditulis langsung dan diselaraskan saat tab kembali tampil; `prefers-reduced-motion` dihormati.
- Perpindahan layar: tiap layar punya `<main>` sendiri yang disembunyikan — keranjang Jual tidak hilang saat pindah; layar terakhir diingat per perangkat. Stok · Pelanggan · Menu masih di sistem lama.
- Yang sengaja beda dari papan: kartu "Kas laci / Rekening" diganti "Kas tercatat · semua kantong" + "Uang hari ini (laci · rekening)" — sistem lama tidak punya saldo per kantong, jadi tidak dikarang.

## Putaran 6 (19 Sep 2026) — layar Jual yang HIDUP + gambar barang + wadah literan bergunung
- **Layar dimorf, bukan digambar ulang** (`inti/dom.js` `pasang()`): pohon HTML baru dibandingkan dengan yang hidup, atribut/teks diselaraskan di tempat, anak dicocokkan lewat `data-k`/`id`. Elemen yang sama tetap hidup → isi gambar, gunung beras, dan angka bisa **bertransisi**; animasi masuk hanya berjalan saat elemen benar-benar lahir (chip per jalur, baris keranjang, lembar per jenis). Kotak isian yang sedang diketik tidak ditimpa.
- `inti/gerak.js`: `gulirkan()` (angka ber-`data-gulir` bergulir dari nilai lama ke baru: total keranjang, ditagih, diterima, kembalian, omzet hari ini), `terbangkan()` (tetes emas dari tombol yang diketuk ke bilah keranjang, bilahnya memegas), `sekali()`. Tab tersembunyi & "kurangi gerakan" → nilai akhir langsung.
- **Gambar sesuai barang** (SVG, isi naik-turun lewat `transform` supaya bertransisi di semua peramban): karung utuh (berangka 50/25), kemasan (kantong berlabel angka ukurannya), karung terbuka + serok (repack & literan yang diserok dari karung), dan **kotak wadah literan** dengan **gunung beras**.
- **Wadah literan** (keterangan owner 14 & 19 Sep; foto kotak kayu bergunung): delapan wadah (`DAFTAR_WADAH`), penuh ±50 kg, isi ulang saat tersisa ≤ 10 kg, di atas 60% masih menggunung lalu rata lalu turun (`WADAH_*` — angka KEBIJAKAN owner, kelak diatur dari layar Stok khusus wadah). Tinggi isi = isi saat terakhir **ditandai isi ulang** − literan merek itu yang terjual sesudahnya − literan di keranjang/struk parkir. Tombol "Wadah baru diisi ulang" ada di lembar jumlah literan → dokumen koleksi BARU `wadahLiteran` `{wadah, tipe 'isi', isiKg, tanggal, jam}`. **Alat ukur, BUKAN stok**: stok literan tetap dipotong dari kolam merek oleh mesin yang sama; sistem lama tidak mengenal koleksi ini dan cadangan sistem lama tidak memuatnya. Belum pernah ditandai → kotak bergaris putus bertanda "?" (tidak ditebak penuh); terjual melebihi isi tanda → selisihnya dilaporkan.
- **Tata letak seperti papan harga toko**: kemasan dikelompokkan per ukuran (5 · 10 · 20 · 25 · … kg), karung per 50/25 kg, tiap kelompok **dari yang termurah**; literan & repack dari yang termurah.

## Putaran 6b (19 Sep 2026) — kinerja di Mac + adegan cerita
- **Patah-patah di Mac** (`css/kinerja.css`): penyebabnya elemen ber-`backdrop-filter` yang bergerak / berisi gerak (belasan chip kaca buram masuk bergiliran, bola cahaya ber-`filter: blur`, latar `background-attachment: fixed`) → tiap bingkai latar dikaburkan & dicat ulang. Kini kaca buram hanya untuk permukaan besar yang diam (nav bawah, laci keranjang HP); chip/kartu/lembar memakai kaca tanpa buram (`--kaca-chip`, `--kaca-kartu`), latar jadi satu lapisan fixed (`body::after`), bola tanpa blur/transisi, chip `contain: layout paint`. Ringkasan: lapis cincin yang tetap tersembunyi pindah tanpa transisi (kelas `diam`).
- **Adegan** (`js/layar/adegan.js`, `css/adegan.css`; hanya `transform` & `opacity`, tidak menghalangi ketukan, dilewati saat tab tersembunyi / "kurangi gerakan"):
  - literan & repack masuk keranjang → **serok** dari wadah kotak (atau karung terbuka) → dituang ke kantong kertas (1–3 serokan menurut kg) → **diikat** → memegas; ≥ 13 L memakai karung kecil.
  - kemasan masuk keranjang → kemasan berlabel ukurannya jatuh ke **keranjang belanja** yang memantul.
  - nota dicatat (literan/kemasan) → **serah terima**: dua tangan toko (lengan emas, atas & bawah kemasan) → dua tangan pembeli (lengan platina) → berubah jadi alat bayarnya.
  - nota dicatat (karung terbesar nilainya) → karung **diangkut** dua tangan → tangan pembeli memberi → tangan toko menerima → jadi alat bayarnya.
  - Kejujuran: hanya **Tunai** yang jadi uang; **QRIS** = ponsel ber-centang; **BON** = kertas bon bertulis "belum ada uang". Adegan nota hanya main sesudah tulisan SUNGGUH berhasil.

## Struktur
```
baru/
  index.html            cangkang: nav bawah (HP/Tablet), menu samping (Mac), formulir masuk, <main id="layar">
  css/identitas.css     token C1 (kaca buram emas/sampanye/platina, Bodoni Moda + Jost, body / body.gelap) + komponen dasar
  css/kerangka.css      SATU markup tiga lebar: HP < 720 · Tablet 720–1099 · Mac ≥ 1100
  css/jual.css          bagian khas layar Jual
  js/app.js             pintu masuk: mode, sumber data (Firestore / ?cadangan=), masuk, nav
  js/inti/{format,dom,keadaan}.js   pemformat, penggambar (escape + delegasi data-aksi), penyimpan keadaan
  js/data/koleksi.js    tabel 28 koleksi + kolom pengurut
  js/data/toko.js       cache di memori + ambil*() (nama = index.html) + keranjang aktif/parkir
  js/data/firebase.js   Firestore BACA SAJA, cache tetap IndexedDB (jalan tanpa internet), masuk akun owner
  js/data/cadangan.js   sumber pengganti: berkas backup-batch-*.json (lokal, tidak di repo)
  js/mesin/beku.js      26 dari 28 MESIN UANG BEKU — DIBUAT ALAT (alat-uji/pindah_mesin.py), byte-identik, JANGAN DISUNTING
  js/mesin/pembantu.js  fungsi & konstanta pembantu mesin — DIBUAT ALAT juga
  js/layar/jual-logika.js   logika Jual tanpa DOM (diuji di jsc)
  js/layar/jual.js          gambar & ketukan
```
Belum dipindah (terikat layar lama): `tulisSaldoPembuka` (ritual Tutup Buku), `thPagar` (Tutup Hari).
Jangkar warisan: `stokMaksJalur()` membaca `#jualKarungBerat` dari DOM — layar menyediakan `<input type="hidden" id="jualKarungBerat">`.

## Menjalankan di komputer (tanpa Firestore)
```
python3 -m http.server 8760 --directory .
```
lalu buka `http://localhost:8760/baru/index.html?cadangan=/backup-batch-miqbal-YYYY-MM-DD.json` (berkas cadangan diunduh dari index.html; tidak pernah masuk repo).
Tanpa `?cadangan=`, halaman memakai Firestore toko dan meminta sandi owner (diteruskan ke Firebase Auth, tidak disimpan).

## Gerbang (jalan di CI)
| alat | membuktikan |
|---|---|
| `alat-uji/pindah_mesin.py --periksa` | tiap mesin di `js/mesin/beku.js` = sidik `alat-uji/beku.sha256` |
| `alat-uji/uji_jual_baru.py` (+ `--kontrol`) | 171 skenario logika Jual (baca + catat + batalkan + repack/bonus/pengganti retur/pesanan + retur & tukar) + tata letak & wadah literan) di kotak pasir; 66 kontrol positif berbunyi; kunci dokumen vs baris nyata & vs yang ditulis index.html |
| `alat-uji/uji_ringkasan_baru.py` (+ `--kontrol`) | 28 skenario logika Ringkasan (jam tetap, zona waktu dikunci WIB) + 14 kontrol; di cadangan toko: omzet hari/bulan/tahun = jumlah langsung barisnya |
| `alat-uji/uji_identitas_baru.py` (+ `--kontrol`) | mesin lama & baru diberi cadangan toko yang sama → hasil identik (lokal saja; 5 kontrol) |

Memindahkan mesin ulang (sesudah `index.html` berubah): `python3 alat-uji/pindah_mesin.py`.
