# Gladi tutup buku di server tiruan (Firebase Emulator)

Mulai 7 Okt 2026. Tujuannya: sebelum owner menjalankan tutup buku 2026 sungguhan pada 1 Jan 2027 tanpa Claude, ritual penuh dan aturan servernya
sudah pernah dijalankan di server tiruan, lewat layar /baru/ yang asli.

## Tempat jalannya

**Hanya di runner GitHub Actions**, lewat workflow **Gladi tutup buku** (`.github/workflows/gladi-tutup-buku.yml`). Alasannya ada di `CLAUDE.md`:
peramban dan emulator tidak boleh dijalankan di Mac owner. Workflow ini bisa dijalankan manual dari tab Actions, dan berjalan sendiri di PR yang
menyentuh tutup buku, kunci periode, layar Uang, aturan server, atau sambungan Firebase.

Di Mac hanya boleh menjalankan pemeriksaan yang tidak menyalakan peramban:

    python3 alat-uji/uji_server_tiruan.py            # + --kontrol
    python3 alat-uji/gladi_data_contoh.py --periksa  # + --kontrol
    python3 alat-uji/gladi_tutup_buku.py --periksa-salinan

`alat-uji/gladi_tutup_buku.py` menolak jalan di luar GitHub Actions.

## Isinya

- **Server tiruan**: Firestore + Auth emulator dengan aturan `firestore.rules` repo. Proyeknya `demo-gladi-toko`, tanpa kredensial, dan tidak
  bisa menyentuh data toko.
- **Data contoh**: dibuat `alat-uji/gladi_data_contoh.py` dengan benih tetap. Isinya ±9 rb dokumen (skala bawaan 0,65, lihat keterbatasan),
  8 Agu–31 Des 2026, dengan bentuk dokumen yang sama dengan cadangan. Semua nama dan angka rupiahnya karangan. Cadangan asli tidak pernah dibaca dan
  tidak pernah dikirim ke runner. Ada dua varian:
  - `macet`: ada 23 hari berjualan tanpa tutup hari, polanya sama dengan keadaan toko 6 Okt. Tanpa putusan, gerbang g1 memblokir dan `susunKunci`
    menolak. Sesudah putusan per tanggal (Paket A), semua gerbang beres. **Ketiga skenario memakai varian ini**, seperti keadaan toko yang akan
    dihadapi owner pada 1 Jan.
  - `bersih`: semua hari ditutup. Hanya dinilai `--periksa`; tidak dipakai skenario.
- **Akun**: owner contoh (`owner@…`, dikenali aturan lewat email) dan satu karyawan contoh beserta dokumen `aksesAkun`-nya. Sandi dibuat ulang tiap
  run dan tidak pernah dicetak.
- **Jalan masuk /baru/ ke emulator**: `?emulator=127.0.0.1:8080`, diatur di `baru/js/data/server-tiruan.js`. Jalan ini hanya berlaku kalau
  halamannya dibuka dari `localhost`/`127.0.0.1` dan alamat emulatornya juga lokal. Selama aktif, layar memasang bilah merah **SERVER TIRUAN**.
  Kalau `?emulator=` diminta di halaman lokal tetapi alamatnya ditolak (bukan lokal, port rusak, kosong), aplikasi **gagal-tertutup**: tidak
  tersambung ke server mana pun (tidak jatuh ke data toko), gerbang masuk tetap tertutup, dan bilah merah **SERVER TIRUAN DITOLAK** menyebut
  sebabnya. Gladi juga baru mengetik email & sandi owner contoh sesudah bilah **SERVER TIRUAN demo-gladi-toko** tampil.
  CSP situs tidak dilonggarkan. Salinan uji mengganti `connect-src`: host Firebase sungguhan (`*.googleapis.com`) dibuang, alamat emulator
  ditambahkan.

## Skenario

Semua skenario memakai data `macet`.

| skenario | jam halaman | yang dibuktikan |
|---|---|---|
| `latihan` | 31 Des 2026 21.45 | Muat penuh. LATIHAN tujuh langkah sampai "Latihan selesai", lalu diam 5 detik, tanpa satu pun tulisan ke server. Denyut perangkat dan katalog kasir tidak dihitung, karena keduanya tulisan latar. |
| `gerbang` | 1 Jan 2027 15.30 | SUNGGUHAN boleh dipilih. Gerbang g1 "23 hari belum ditutup & belum diputus" tampil memblokir. Tombolnya berbunyi "1 hal belum beres — bereskan dulu", dan mengetuknya tidak memajukan langkah dan tidak menulis apa pun. Lalu alasan diketik untuk tiap tanggal dan **Simpan putusan** diketuk: tepat satu dokumen `aturanToko/putusanHari` (isinya dicek di server), g1 beres, periksa lolos, lalu diam tanpa tulisan. |
| `ritual` | 1 Jan 2027 15.30 | SUNGGUHAN, putusan per tanggal, sampai paraf, lalu kunci. Server menolak kiriman saldo pembuka ke-2, lalu kartu **lanjutkan / batalkan** muncul. BATALKAN sebelum penanda. Mulai lagi, lalu arsip ditolak server dan kartu **lanjutkan / batalkan** muncul lagi. LANJUTKAN sampai arsip habis. BATALKAN sesudah penanda. Mulai lagi sampai **selesai**, lalu diam. |

Klaim ritual diperiksa **di server** lewat REST emulator, bukan dari cache halaman yang bisa berisi tulisan tertunda. Pemeriksanya menunggu berita
acara 2026 di server berstatus yang diharapkan, lalu menilai:

- **kiriman ke-2 ditolak**: berita acara "berjalan", saldo pembuka baru sebagian, arsip kosong, dokumen 2026 utuh;
- **sesudah BATALKAN sebelum penanda**: saldo pembuka ditarik habis, arsip kosong, penanda `tutupBuku` dan titik kas tidak tersentuh, isi 21
  koleksi 2026 sama persis dengan sebelum ritual;
- **arsip ditolak**: berita acara "terkunci", saldo pembuka lengkap, arsip kosong, dokumen 2026 masih di koleksi asal;
- **sesudah LANJUTKAN** dan **sesudah SELESAI**: `arsipTahun` = semua dokumen 2026 yang asli (= `nArsip` berita acara), 0 tersisa di koleksi
  asal, saldo pembuka = `nPembuka`, penanda `tutupBuku` 2026, dan pada SELESAI berita acara "selesai";
- **sesudah BATALKAN sesudah penanda**: isi 21 koleksi 2026 sama dengan sebelum ritual, `arsipTahun` kosong, saldo pembuka habis, uang di titik
  kas kembali seperti sebelum ritual, penanda `tutupBuku` dinetralkan (tahun 0, dibatalkan 2026). Di halaman, era kembali kosong.

Untuk memotong ritual di tengah, aturan emulator diganti sementara dengan salinan `firestore.rules` yang izin create/update satu bloknya dicabut.
Setelah itu teks repo dipasang lagi. Berkas `firestore.rules` sendiri tidak diubah.

**Kontrol** (`--kontrol`, tiap kontrol di emulator sendiri): salinan uji dirusak, lalu cek sasarannya wajib gagal. Kontrol dihitung berbunyi hanya
kalau skenarionya jalan sampai akhir, cek sasaran gagal bukan karena langkahnya tidak tercapai, cek lain tidak ikut gagal (kecuali yang memang
terkena), dan bukti kerusakannya terlihat di langkah yang benar. Ada lima kontrol:

- latihan yang menulis di langkah 4;
- latihan yang menulis 5,5 detik sesudah langkah terakhir (hanya langkah diam yang melihatnya);
- gerbang g1 yang tidak memblokir;
- salinan yang memuat satu koleksi tidak lengkap (hanya 10 dokumen terbaru);
- pemulihan arsip yang melewatkan satu dokumen (skenario `ritualPendek`: kunci penuh lalu BATALKAN sesudah penanda). Ini wajib ketahuan dari isi
  server.

## Laporan

Ringkasan tiap run ada di halaman ringkasan run. Artefak `laporan-gladi-tutup-buku` berisi JSON lengkap dan log emulator.

**Per langkah**: angka langkah itu saja, bukan jumlah berjalan.

- **baca**: dokumen yang diterima pendengar halaman dari server (penghitung di salinan SDK uji), ditambah tulisan halaman sendiri ke koleksi yang
  didengarnya. Firestore menagih tulisan sendiri itu sebagai baca, tetapi SDK tidak memunculkan perubahan baru saat server mengakuinya, jadi
  jumlahnya diambil dari REST. Termasuk di sini dokumen yang dikembalikan dari arsip saat dibatalkan. Pembacaan `get()` di dalam aturan **tidak**
  terhitung, karena `:ruleCoverage` emulator hanya berisi posisi ekspresi tanpa jumlah. Perkiraan kuota halaman memasukkannya.
- **tulis / hapus**: selisih isi emulator antara sebelum dan sesudah langkah, diambil lewat REST.

**Per jalur** (skenario ritual), di skala gladi dan perkiraan skala toko (× 17.000 ÷ dokumen arsip gladi), dibandingkan dengan batas Spark per
hari (50 rb baca, 20 rb tulis, 20 rb hapus) dan dengan kartu **Perkiraan kuota Firestore** di halaman:

- **ritual bersih**: yang dikerjakan owner tanpa penolakan atau pembatalan: masuk, muat penuh, putusan, lalu langkah 1–7 percobaan terakhir sampai
  selesai, dan diam;
- **kunci yang berhenti di saldo pembuka + BATALKAN sebelum penanda**;
- **BATALKAN sesudah penanda** (arsip sudah penuh);
- **ritual bersih + BATALKAN sesudah penanda di hari yang sama**.

Jalur di atas 80% batas diberi peringatan ⚠, dan di atas 100% diberi ⛔.

**Batalkan sesudah penanda di hari yang sama dengan ritualnya tidak muat kuota Spark.** Ritual bersih sendiri sudah ±18 rb tulis dan ±17 rb hapus
di skala toko (±90% dan ±85%). Pembatalan sesudah arsip penuh menambah kira-kira sebanyak itu lagi, ditambah ±17 rb baca. Kalau owner membatalkan
sesudah penanda, pembatalannya baru bisa tuntas sesudah kuota reset berikutnya (15.00 WIB), dan toko jangan berjualan sampai tuntas. Kartu
**Perkiraan kuota Firestore** di halaman menyebut hal yang sama.

Keterbatasan:

- **Jam server emulator adalah jam runner, bukan jam halaman.** Pemeriksaan kunci periode di aturan (`get()` bulan lampau) karena itu dinilai
  dengan bulan runner. Pada gladi hanya dokumen Agu–Sep yang memicu `get()` itu; pada 1 Jan yang memicunya Agu–Nov.
- **Data contoh tanpa bulan terkunci** (`aturanToko/kunciPeriode`). Gerbang "tahun punya bulan terkunci" dan jalur aturan bulan terkunci belum
  digladikan.
- **Antrean WebChannel emulator dibatasi 10.000 pesan per kanal.** Run 7 Okt memakai data 17 rb dokumen. Hasilnya: "too many pending messagings in
  the back channel (10001)", kanal Listen diputus berulang, dan halaman tidak pernah menerima data. `--help` emulator tidak punya setelan untuk
  batas ini, dan server sungguhan tidak punya batas itu. Karena itu data gladi dibuat ±9 rb dokumen (`GLADI_SKALA` 0,65, bisa diubah dari input
  workflow). Ringkasan menambahkan baris *perkiraan skala toko*: hasil gladi × (17.000 ÷ dokumen arsip gladi).
- **Tiap skenario jalan di emulator sendiri.** Emulator tetap mengirimi sesi halaman yang sudah ditutup sampai kanalnya kedaluwarsa, sehingga
  skenario berikutnya bisa terganggu. Laporan per skenario digabung di akhir (`--gabung`). Tiap langkah mencatat berapa kali antrean emulator
  penuh. Nilai itu **wajib 0 sampai muat penuh selesai**, karena kalau penuh saat muat, halaman tidak pernah menerima data. Sesudah muat penuh
  angkanya hanya dilaporkan. Asalnya sesi kanal yang sudah ditinggal halaman: SDK menyambung ulang dengan token lanjut, sedangkan emulator terus
  mengirimi kanal lama. Run 7 Okt mencatat jutaan baris di satu run dan nol di run lain, dan di keduanya semua cek isi tetap lulus.

## Paket A dan sesudahnya

Gladi sudah disesuaikan dengan Paket A (#110): gerbang g1 dibuka lewat putusan per tanggal, `susunKunci` menolak tanpa putusan (dicek di
`--periksa`), dan ketiga skenario memakai data `macet`.

Belum digladikan: **tutup buku 2027 dengan bulan terkunci** dan **rules v7**. Keduanya ditambahkan sesudah PR rules v7 masuk.

Kalau gerbang atau langkah tutup buku berubah lagi, yang perlu disesuaikan ada di `alat-uji/gladi_tutup_buku.py`:

- fungsi langkah di `SKENARIO_JS` (`putusanG1`, `sampaiParaf`, `gerbangDiblokir`, dan seterusnya);
- urutan langkah di `SKENARIO`;
- cek per skenario di `cek_*`, pemeriksa server di `keadaan_server`, dan kontrol di `KONTROL`.

`--periksa-salinan` (boleh di Mac) memastikan nama langkah yang dicek benar-benar dilaporkan skenario, dan jangkar kerusakan tiap kontrol masih ada
tepat satu kali.
