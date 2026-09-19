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
- Belum: Retur/Tukar (subsistem sendiri — putaran 4), Wadah dijual (fitur baru, mesin laba harus diajari dulu), cetak/kirim struk.

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
| `alat-uji/uji_jual_baru.py` (+ `--kontrol`) | 116 skenario logika Jual (baca + catat + batalkan + repack/bonus/pengganti retur/pesanan) di kotak pasir; 32 kontrol positif berbunyi; kunci dokumen vs baris nyata |
| `alat-uji/uji_identitas_baru.py` (+ `--kontrol`) | mesin lama & baru diberi cadangan toko yang sama → hasil identik (lokal saja; 5 kontrol) |

Memindahkan mesin ulang (sesudah `index.html` berubah): `python3 alat-uji/pindah_mesin.py`.
