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
  tidak pernah dikirim ke runner. Ada tiga varian:
  - `macet`: ada 23 hari berjualan tanpa tutup hari, polanya sama dengan keadaan toko 6 Okt. Tanpa putusan, gerbang g1 memblokir dan `susunKunci`
    menolak. Sesudah putusan per tanggal (Paket A), semua gerbang beres. **Ketiga skenario memakai varian ini**, seperti keadaan toko yang akan
    dihadapi owner pada 1 Jan.
  - `bersih`: semua hari ditutup. Hanya dinilai `--periksa`; tidak dipakai skenario.
  - `terkunci` (rules v7): data `macet` (benih & 23 hari macet yang sama, skala 0,05 ≈ 1,7 rb dokumen — `GLADI_SKALA_PINTU`), ditambah **kunci
    periode sampai Desember 2026** (`aturanToko/kunciPeriode`, dikunci 4 Jan 2027 — semua bulan tahun yang ditutup terkunci) dan dua pindahan uang
    laci ↔ brankas bertanggal Okt & Nov. Skalanya kecil karena tiap catatan bulan terkunci butuh 5 pemeriksaan server (arsip 3 catatan per kiriman,
    bukan 9): di skala toko satu arsip ±3 rb kiriman, dan skenario `pintu` mengarsip dua kali plus membatalkan sekali. Yang diuji mekanisme pintu;
    angka kuota tetap diproyeksikan ke skala toko. Pindahan uang **tidak
    diarsip** tutup buku dan tidak berpintu, jadi wajib tetap utuh selama pintu terbuka. `--periksa` menilainya di jam 5 Jan 2027 15.30: tahun
    2026 boleh ditutup sungguhan **lewat pintu**; sesudah putusan, `susunKunci` = kiriman 1 berita acara "berjalan" sendirian, kiriman 2 membuka
    pintu (tahun 2026, 48 jam), titik kas 31 Des ikut lewat pintu, tiap kiriman ≤ 18 pemeriksaan. Dipakai skenario `pintu`. Titik kas SEBELUM
    ritual di varian ini = hitungan tutup hari terakhir sebelum 31 Des (30 Des, bulan terkunci), bukan 31 Des: BATALKAN mengembalikannya lewat
    cabang `titikSebelum` rules v7 (`pintuTitik`), bukan cabang "31 Des" (sanggahan 7 Okt — dulu titik kas contoh kebetulan 31 Des, cabang itu
    tidak pernah tertempuh; `--kontrol` data contoh membuktikan titik kas 31 Des ketahuan).
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

`latihan`, `gerbang`, dan `ritual` memakai data `macet`; `pintu` memakai data `terkunci`.

| skenario | jam halaman | yang dibuktikan |
|---|---|---|
| `latihan` | 31 Des 2026 21.45 | Muat penuh. LATIHAN tujuh langkah sampai "Latihan selesai", lalu diam 5 detik, tanpa satu pun tulisan ke server. Kunci latihan juga menyusun potret 2026 (Paket B) tanpa menulis. Denyut perangkat dan katalog kasir tidak dihitung, karena keduanya tulisan latar. |
| `gerbang` | 1 Jan 2027 15.30 | SUNGGUHAN boleh dipilih. Gerbang g1 "23 hari belum ditutup & belum diputus" tampil memblokir. Tombolnya berbunyi "1 hal belum beres — bereskan dulu", dan mengetuknya tidak memajukan langkah dan tidak menulis apa pun. Lalu alasan diketik untuk tiap tanggal dan **Simpan putusan** diketuk: tepat satu dokumen `aturanToko/putusanHari` (isinya dicek di server), g1 beres, periksa lolos, lalu diam tanpa tulisan. |
| `ritual` | 1 Jan 2027 15.30 | SUNGGUHAN, putusan per tanggal, sampai paraf, lalu kunci. Server menolak kiriman saldo pembuka ke-2, lalu kartu **lanjutkan / batalkan** muncul. BATALKAN sebelum penanda. Mulai lagi, lalu arsip ditolak server dan kartu **lanjutkan / batalkan** muncul lagi. LANJUTKAN sampai arsip habis. BATALKAN sesudah penanda. Mulai lagi sampai **selesai**, lalu diam. |
| `pintu` | 5 Jan 2027 15.30 | **Rules v7, semua bulan 2026 terkunci.** SUNGGUHAN, putusan per tanggal, sampai paraf, lalu kunci penuh **lewat pintu tutup buku**: berita acara "berjalan" sendirian dulu, kiriman berikutnya membuka pintu, saldo pembuka & titik kas 31 Des lewat pintu, arsip memindah catatan bulan terkunci. BATALKAN sesudah penanda (pengembalian arsip & penarikan saldo pembuka lewat pintu, pintu ditutup). Mulai lagi, kunci penuh lagi, lalu **selesai menutup pintu**, lalu diam. Sesudah halaman ditutup, lewat REST dengan token owner contoh: pintu yang dibuat **kedaluwarsa** → mengembalikan catatan dari arsip dan menghapus catatan bulan terkunci yang salinannya ada **ditolak server**; pintu yang sama dengan `sampai` besok → diterima (kontrol: sebabnya memang jam pintu). |

Klaim ritual diperiksa **di server** lewat REST emulator, bukan dari cache halaman yang bisa berisi tulisan tertunda. Pemeriksanya menunggu berita
acara 2026 di server berstatus yang diharapkan, lalu menilai:

- **kiriman ke-2 ditolak**: berita acara "berjalan", saldo pembuka baru sebagian, arsip kosong, dokumen 2026 utuh;
- **sesudah BATALKAN sebelum penanda**: saldo pembuka ditarik habis, arsip kosong, penanda `tutupBuku` dan titik kas tidak tersentuh, isi 21
  koleksi 2026 sama persis dengan sebelum ritual;
- **arsip ditolak**: berita acara "terkunci", saldo pembuka lengkap, arsip kosong, dokumen 2026 masih di koleksi asal;
- **sesudah LANJUTKAN** dan **sesudah SELESAI**: `arsipTahun` = semua dokumen 2026 yang asli (= `nArsip` berita acara), 0 tersisa di koleksi
  asal, saldo pembuka = `nPembuka`, penanda `tutupBuku` 2026, potret 2026 di berita acara (12 bulan + omzet per hari, Paket B #114), dan pada
  SELESAI berita acara "selesai";
- **sesudah BATALKAN sesudah penanda**: isi 21 koleksi 2026 sama dengan sebelum ritual, `arsipTahun` kosong, saldo pembuka habis, uang di titik
  kas kembali seperti sebelum ritual, penanda `tutupBuku` dinetralkan (tahun 0, dibatalkan 2026). Di halaman, era kembali kosong.
- **skenario `pintu`**, tambahan di tiap titik: dokumen `pengaturan/pintuBuku` di server **terbuka** untuk 2026 dan `sampai`-nya ≤ 72 jam dari jam
  server (sesudah kunci) atau **tertutup** (sesudah BATALKAN dan SELESAI); `arsipTahun` = **isi** tiap catatan 2026 yang asli, bukan hanya id-nya
  (sesudah kunci & selesai); pindahan uang bulan terkunci (tidak diarsip) sama persis dengan sebelum ritual; titik kas di server bertanggal 31 Des 2026
  sesudah kunci & selesai, dan sesudah BATALKAN kembali ke titik kas sebelum ritual (30 Des — lewat cabang `titikSebelum`, bukan "31 Des").

Untuk memotong ritual di tengah, aturan emulator diganti sementara dengan salinan `firestore.rules` yang izin create/update satu bloknya dicabut.
Setelah itu teks repo dipasang lagi. Berkas `firestore.rules` sendiri tidak diubah.

**Kontrol** (`--kontrol`, tiap kontrol di emulator sendiri): salinan uji dirusak, lalu cek sasarannya wajib gagal. Kontrol dihitung berbunyi hanya
kalau skenarionya jalan sampai akhir, cek sasaran gagal bukan karena langkahnya tidak tercapai, cek lain tidak ikut gagal (kecuali yang memang
terkena), dan bukti kerusakannya terlihat di langkah yang benar. Kontrol yang skenarionya jatuh dihitung DIAM, bukan berbunyi. Run 7 Okt
membuktikan perlunya aturan ini: kontrol "satu koleksi tidak dimuat" yang lama ternyata membuat layar Uang tidak tampil, tetapi dulu tetap
dihitung berbunyi. Cek "tidak ada galat izin / penolakan server di halaman" membaca konsol, kabar halaman, galat status Firebase, dan daftar
"ditolak" antrean lokal per langkah (sanggahan 7 Okt: penolakan tulis yang ditangani aplikasi tidak sampai ke konsol, jadi dulu ✓ walau server
menolak); di skenario ritual langkah "… ditolak server" (penolakan sengaja) dikecualikan. Ada enam kontrol:

- latihan yang menulis di langkah 4;
- latihan yang menulis 5,5 detik sesudah langkah terakhir (hanya langkah diam yang melihatnya);
- gerbang g1 yang tidak memblokir;
- salinan yang memuat satu koleksi tidak lengkap (hanya 10 dokumen terbaru; skenario `muatSaja`, karena data yang kurang juga membuat kunci
  LATIHAN menolak "12 baris tidak sama");
- pemulihan arsip yang melewatkan satu dokumen (skenario `ritualPendek`: kunci penuh lalu BATALKAN sesudah penanda). Ini wajib ketahuan dari isi
  server.
- selesai yang **tidak menutup pintu** tutup buku (skenario `pintuPendek`, data terkunci: kunci penuh lalu selesai). Rules v7 (`acaraTutupPintu`)
  wajib menolak berita acara "selesai" di SERVER: berita acara tetap "terkunci" dan pintu tetap "berjalan". Kontrol ini juga pembukti cek izin
  halaman: cek itu WAJIB ikut gagal, dengan sebab di langkah SELESAI.

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
di skala toko (±90% dan ±85% pada skala ±17 rb catatan; dengan laju cadangan toko 6 Okt tulisnya kini ±98–104%, lihat paragraf berikut).
Pembatalan sesudah arsip penuh menambah kira-kira sebanyak itu lagi, ditambah ±17 rb baca. Kalau owner membatalkan sesudah penanda, pembatalannya
baru bisa tuntas sesudah kuota reset berikutnya (15.00 WIB), dan toko jangan berjualan sampai tuntas. Kartu
**Perkiraan kuota Firestore** di halaman menyebut hal yang sama.

**Tahun yang SEMUA bulannya terkunci (skenario `pintu`, rules v7) tidak muat satu hari meski tanpa pembatalan.** Catatan bulan terkunci dipindah 3 per
kiriman (5 pemeriksaan server per catatan), ditambah satu baris jejak per kiriman. Run 7 Okt (37568246193) diproyeksikan ke skala toko: ritual bersih
±23,5 rb tulis (117%), ±17 rb hapus (85%); kartu perkiraan kuota di halaman menghitung angka yang sama (1.844 tulis di skala gladi, terukur 1.854).
Ritual 2026 (tanpa bulan terkunci): proyeksi dari laju cadangan toko 6 Okt sekarang **±98–104%** batas tulis — bisa MEPET atau TIDAK MUAT (dulu
ditulis ±18,9 rb = 94%). Tutup buku 2027 di Januari 2028 karena itu akan berhenti di kuota hari itu dan diteruskan
dengan **Lanjutkan** sesudah reset 15.00 WIB — jangan berjualan sampai tuntas. Keputusan owner K11 (8 Okt 2026): kalau kartu kuota 1 Jan berbunyi
TIDAK MUAT, ritual tetap dimulai 1 Jan sesudah reset; toko TUTUP Sabtu 2 Jan 2027 (tidak jualan, tidak menagih) sampai sesudah 15.00 WIB,
Lanjutkan dari Mac yang sama, tunggu arsip habis — sama untuk Sabtu 1 Jan 2028.

**Jam server = jam halaman** (sejak rules v7). Rules v7 menilai berita acara baru (jam mulai = tanggal server ± 1 hari, tahun lampau), pintu
tutup buku (hanya tahun lalu, ≤ 72 jam dari jam server), dan kunci periode dengan **jam server**. Halaman gladi berjam palsu (31 Des 2026 / 1 Jan /
5 Jan 2027), sedangkan runner berjam Okt 2026: tanpa penyesuaian, rules v7 menolak ritual karena jamnya, bukan karena ritualnya. Karena itu
workflow menggeser **jam dinding JVM emulator saja** lewat `alat-uji/jam_geser.c` (pustaka kecil yang dikompilasi di runner): pembungkus `java`
di depan `PATH` memasang `LD_PRELOAD` bila `GLADI_GESER_JAM` diisi (detik, dari `gladi_tutup_buku.py --geser-jam <skenario>`). Hanya
`CLOCK_REALTIME`, `gettimeofday`, dan `time` yang digeser; jam monoton dan jam CPU diteruskan apa adanya. Chrome, node, dan alat gladi tetap
berjam runner. Jamnya
**diukur, bukan dipercaya**: sebelum skenario panjang ada uji cepat (`--cek-jam`), dan cek pertama tiap skenario menulis satu dokumen sementara
bercap `REQUEST_TIME`, membacanya, lalu menghapusnya sebelum langkah pertama diukur — selisih jam server dengan jam halaman wajib ≤ 15 menit
(biasanya ± 1 menit: emulator menyala sebelum halaman dimuat). Uji cepat juga membandingkan **kecepatan** emulator berjam palsu dengan emulator
biasa (150 commit + 1 query, wajib ≤ 3×): run 7 Okt dengan libfaketime (`libfaketimeMT` maupun `libfaketime.so.1`) membuat emulator ±9,5× lebih
lambat (150 commit: 2,05 → 19,4 detik) dan LANJUTKAN arsip tidak selesai dalam 47 menit — karena itu pemalsu jamnya dibuat sendiri. Tiap langkah kini juga mencatat waktu potret isi server (`ukur … dtk`).

Keterbatasan:
- **Antrean WebChannel emulator dibatasi 10.000 pesan per kanal.** Run 7 Okt memakai data 17 rb dokumen. Hasilnya: "too many pending messagings in
  the back channel (10001)", kanal Listen diputus berulang, dan halaman tidak pernah menerima data. `--help` emulator tidak punya setelan untuk
  batas ini, dan server sungguhan tidak punya batas itu. Karena itu data gladi dibuat ±9 rb dokumen (`GLADI_SKALA` 0,65, bisa diubah dari input
  workflow). Ringkasan menambahkan baris *perkiraan skala toko*: hasil gladi × (17.000 ÷ dokumen arsip gladi).
- **Muat penuh kadang macet di emulator.** Pada run 7 Okt ini terjadi 2 kali dari ±32 skenario: sebagian besar pendengar tidak pernah menerima
  data (misalnya 22 dari 56 koleksi siap dan 33 dokumen sampai), padahal antrean emulator tidak penuh dan tidak ada galat izin. Sebabnya belum
  diketahui. Skenario (atau kontrol) yang berhenti **di muat penuh**, sebelum langkah tutup buku mana pun, dicoba ulang **satu kali** di
  **emulator BARU** dengan Chrome baru: alatnya menyimpan catatan percobaan 1 dan keluar 75, workflow menjalankan `firebase emulators:exec` lagi
  dengan `--ulang-dari` (sanggahan 7 Okt: dulu percobaan kedua memakai emulator yang sama, sesi WebChannel percobaan pertama masih membanjirinya —
  "antrean penuh 7×" sebelum masuk — dan cek "tidak kewalahan saat muat" gagal karena caranya sendiri). Percobaan ulang itu **selalu tercatat**: ada baris `DICOBA ULANG` dan peringatan di halaman ringkasan run (lewat
  `alat-uji/coba_ulang.py`, keputusan owner 26 Sep), dan tanda ⚠ di ringkasan gladi. Galat di langkah lain tidak pernah dicoba ulang. Kalau
  peringatan ini sering muncul, itu masalah sungguhan yang perlu diselidiki: bahannya ada di log emulator per skenario dan per kontrol (artefak)
  dan di ekor catatan Chrome. Pelanggaran CSP salinan juga dicatat sejak awal halaman; sambungan yang ditolak `connect-src` menggagalkan cek.
- **Tiap skenario jalan di emulator sendiri.** Emulator tetap mengirimi sesi halaman yang sudah ditutup sampai kanalnya kedaluwarsa, sehingga
  skenario berikutnya bisa terganggu. Laporan per skenario digabung di akhir (`--gabung`). Tiap langkah mencatat berapa kali antrean emulator
  penuh. Nilai itu **wajib 0 sampai muat penuh selesai**, karena kalau penuh saat muat, halaman tidak pernah menerima data. Sesudah muat penuh
  angkanya hanya dilaporkan. Asalnya sesi kanal yang sudah ditinggal halaman: SDK menyambung ulang dengan token lanjut, sedangkan emulator terus
  mengirimi kanal lama. Run 7 Okt mencatat jutaan baris di satu run dan nol di run lain, dan di keduanya semua cek isi tetap lulus.

## Paket A dan sesudahnya

Gladi sudah disesuaikan dengan Paket A (#110): gerbang g1 dibuka lewat putusan per tanggal, `susunKunci` menolak tanpa putusan (dicek di
`--periksa`), dan ketiga skenario memakai data `macet`. Paket B (#114) juga sudah: kunci latihan menyusun potret, potret 2026 dicek di berita acara
server, dan `--periksa` mengukur besar dokumen berita acara "berjalan" (satu dokumen Firestore, batas 1 MiB; data contoh ±134 KB).

Rules v7 dan tahun yang bulannya terkunci digladikan di PR #111 (skenario `pintu`, data `terkunci`). Tahun yang ditutup di gladi adalah **2026
pada 5 Jan 2027** (data contoh 2026, kunci sampai Desember 2026, jam server digeser ke 5 Jan 2027) — mekanismenya sama dengan tutup buku 2027 pada
Januari 2028; skenario 2028 dengan data 2027 di kotak pasir ada di `alat-uji/uji_tutup_buku_2027.py`.

Kalau gerbang atau langkah tutup buku berubah lagi, yang perlu disesuaikan ada di `alat-uji/gladi_tutup_buku.py`:

- fungsi langkah di `SKENARIO_JS` (`putusanG1`, `sampaiParaf`, `gerbangDiblokir`, dan seterusnya);
- urutan langkah di `SKENARIO`;
- cek per skenario di `cek_*`, pemeriksa server di `keadaan_server`, dan kontrol di `KONTROL`.

`--periksa-salinan` (boleh di Mac) memastikan nama langkah yang dicek benar-benar dilaporkan skenario, dan jangkar kerusakan tiap kontrol masih ada
tepat satu kali.
