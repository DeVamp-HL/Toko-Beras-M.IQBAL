# Sistem baru — `baru/`

Tampilan baru di atas **data yang sama** dengan `index.html` (Firestore proyek `toko-beras-m-iqbal`, 28 koleksi, akun owner yang sama).
Hidup berdampingan di alamat `/baru/`; `index.html` tetap alat yang dipakai toko sampai yang baru terbukti.
Keputusan owner 13 Sep 2026: desain ulang termasuk UI **tanpa mengubah data toko**; 17 Sep: *"mulai sambungkan ke data asli"*.

## Putaran 1 (19 Sep 2026) — layar JUAL, baca saja
- Rak (Sering · Literan · Kemasan · Karung) dibaca dari data toko lewat **mesin beku yang sama** dengan `index.html`.
- Keranjang, nego, potongan, antrean (struk parkir **memegang** stoknya), bayar (Tunai/QRIS/Bon), nama pembeli, kartu Hari ini.
- Aturan owner yang dipasang: pembulatan Rp500 ke atas untuk **Tunai dan Bon**, QRIS persis (17 Sep); uang kurang → sisanya jadi bon atas nama (17 Sep); siapa cepat dia dapat (17 Sep).
- **Tidak menulis apa pun** ke Firestore (nol `setDoc`). Tombol "Catat nota" memeriksa notanya lalu mengaku: putaran ini baca saja.
- Belum: Wadah, Repack, Retur, Pesanan, cetak struk, dan semua layar lain (masih di sistem lama).

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
| `alat-uji/uji_jual_baru.py` (+ `--kontrol`) | 46 skenario logika Jual di kotak pasir; 11 kontrol positif berbunyi |
| `alat-uji/uji_identitas_baru.py` (+ `--kontrol`) | mesin lama & baru diberi cadangan toko yang sama → hasil identik (lokal saja; 5 kontrol) |

Memindahkan mesin ulang (sesudah `index.html` berubah): `python3 alat-uji/pindah_mesin.py`.
