# Peta "Jual dulu, tandai untuk dicocokkan" — putaran 31.2, Tahap 0

**Status (28 Sep 2026): peta saja, belum ada perubahan perilaku. Dibangun HANYA sesudah owner menjawab §5.**
Sumber: kode di cabang `pemantapan/31-empat-kecil` (di atas putaran 30), `firestore.rules` v4, cadangan toko 28 Sep sore (`_privat/`). Angka di sini kg dan
jumlah catatan, bukan rupiah. Nama orang tidak disebut.

## 1. Yang berlaku sekarang (dari kode)

- **Rak Jual** membaca langit-langit stok tiap chip lewat mesin beku yang sama dengan `index.html` (`stokMaksJalur`, sudah dikurangi keranjang aktif +
  parkir). `masukkan()` menolak jumlah di atas langit-langit dengan kalimat ("yang bebas dijual tinggal …"), tidak memotong diam-diam.
- **Saat mencatat nota**, stok dicek ULANG (`periksaStokKeranjang`: baris pertama yang melampaui langit-langit → nota DITAHAN). BACA-DULU Putaran 2:
  *"Belum ada jalur tembus stok — kalau kurang, ditahan."* Sama untuk HP kasir lewat katalog (`ringkasanKasir` membawa sisa; kasir menahan).
- Aturan owner: **jangan dibuka dengan isi ulang / hitungan palsu**. Cara yang selama ini dipakai di lapangan (Cocokkan dulu supaya bukunya naik, lalu
  jual) memaksa owner menulis hitungan fisik yang tidak dilakukan — itu yang dilarang.
- Kejadian nyata yang melahirkan permintaan ini: wadah kelihatan penuh tetapi buku merek asalnya kurang (tumpukan salah catat) — putaran 28 menutup jalur
  wadah (buku wadah sendiri); sisa kasusnya = **karung / kemasan di tumpukan yang nyata ada tetapi bukunya kurang** (belum tercatat masuk, salah nama,
  cocokkan yang meleset).

## 2. Jalur jujur yang diusulkan

Nota tercatat apa adanya, baris yang melampaui buku **ditandai**, buku dibiarkan MINUS sampai dicocokkan, dan tandanya tampil sebagai pekerjaan rumah.

| Langkah | Usulan | Alasan |
|---|---|---|
| Tanda di nota | kolom baru di dokumen `penjualan` yang sudah ada: `perluCocokkan: true` + `kurangKg` (karung/literan/repack) atau `kurangUnit` (kemasan) = selisih saat dicatat | tanpa koleksi baru; mesin beku mengabaikan kolom asing (pola `jam`, `alasanKoreksi`); laporan tetap membaca baris seperti nota lain |
| Siapa memutuskan | ketukan kedua di tombol CATAT NOTA: "Buku X kurang N kg — jual dulu, tandai untuk dicocokkan?" (kalimat menyebut nama & selisih) | jalur tembus yang SADAR, bukan penjaga yang dilemahkan |
| Buku sesudahnya | tetap minus sebesar selisih (mesin memotong penjualan seperti biasa) | tidak ada isi ulang palsu; angka minus = kebenaran buku vs fisik |
| Pekerjaan rumah | Stok › Gudang kartu keempat "Mana yang belum dicocokkan?" mendapat item **"belum dicocokkan: N nota tembus stok"** (daftar nama + kg dari baris `perluCocokkan` yang bukunya masih minus) | pola `jbKelompokStok`/kartu cocok yang ada; tidak ada layar baru |
| Menutup tanda | Cocokkan (Stok › Cocokkan › Tumpukan gudang / Kemasan) atas nama itu SESUDAH nota → tanda dianggap tuntas (dibaca dari `penyesuaianStok`/`penyesuaianKemasan` bertanggal ≥ nota; tidak menulis ulang notanya) | satu pintu yang sudah ada; nota tidak disunting |
| Katalog HP kasir | tidak diubah (kasir tetap menahan; tembus hanya dari `/baru/` oleh yang berhak) | kasir tanpa penjaga dua ketukan |
| Retur / batal nota bertanda | seperti nota biasa; tanda ikut hilang bersama notanya | tidak ada keadaan yang hidup lebih lama dari notanya |

Yang **tidak** diusulkan: menaikkan buku otomatis, menulis `penyesuaianStok` dari layar Jual, mengubah `periksaStokKeranjang` untuk karyawan.

## 3. Pemeriksaan ulang stok saat mencatat — apa yang berubah

`periksaStokKeranjang` tetap berjalan pertama. Bila menemukan baris yang melampaui: (a) tanpa hak tembus → ditahan seperti sekarang; (b) dengan hak
tembus dan belum ketukan kedua → kalimat + `perluYakin`; (c) ketukan kedua → nota dicatat, baris itu diberi `perluCocokkan` + `kurangKg/Unit`. Langit-langit
rak (`masukkan`) tidak berubah: jumlah yang dimasukkan ke keranjang tetap boleh melebihi HANYA lewat jalur ini (bukan dari rak).

## 4. Yang tidak disentuh

28 mesin beku · `index.html`, `kasir*.html`, `ringkasanKasir` · `firestore.rules` v4 (kolom baru di `penjualan` tidak butuh aturan baru; hak siapa yang boleh =
pemeriksaan di layar + `periksaKiriman` untuk bukan-owner, bukan rules) · laba (baris bertanda dihitung seperti nota biasa) · putaran 28 (wadah).

## 5. Pertanyaan untuk owner — mengubah hasil

1. **Siapa boleh menembus**: owner saja, atau juga staf (akun per orang)? Kalau staf boleh: apakah tandanya wajib menyebut siapa yang menembus (`olehUid`
   sudah ada di atribusi pusat — cukup itu?).
2. **Bentuk tanda**: kolom `perluCocokkan` + `kurangKg/kurangUnit` di baris nota (usulan), atau dokumen catatan terpisah per kejadian (lebih mudah dicari,
   tapi koleksi/dokumen baru)?
3. **Apakah ini mengubah pemeriksaan ulang stok saat mencatat?** Usulan: tidak — tetap menahan lebih dulu; tembus = ketukan kedua yang menyebut selisih.
   Alternatif: tidak menahan sama sekali untuk owner (tanda otomatis) — tidak diusulkan.
4. **Kapan tanda dianggap tuntas**: cocokkan apa pun atas nama itu sesudah nota (usulan), atau hanya cocokkan yang membuat bukunya ≥ 0?
5. **Kartu keempat**: item "belum dicocokkan: N nota tembus stok" cukup, atau perlu pita di Jual juga (seperti karcis)?
