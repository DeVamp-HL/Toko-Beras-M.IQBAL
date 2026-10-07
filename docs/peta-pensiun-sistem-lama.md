# Peta pensiun sistem lama — putaran 25b, Tahap 0

> **Status terbaru:** sistem lama & `kasir.html` PENSIUN (keputusan owner 3 Okt 2026, PR #103): `index.html` kini halaman pengalih tanpa script — tidak
> ada lagi baca riwayat atau pulihkan di sana; versi terakhirnya di tag git `sistem-lama-terakhir`, jalan darurat `docs/prosedur-pulih-darurat.md`. Isi di
> bawah = sejarah 25b/25c, tidak ditulis ulang.

**Status (27 Sep 2026, putaran 25c): yang tersisa di `index.html` hanya MEMBACA riwayat dan PULIHKAN dari berkas cadangan (§7).** Sebelumnya
(26 Sep): `index.html` hanya-baca lewat satu penjaga — keputusan owner (b) dipersempit, §5–§6. Tahap 0 sempat berhenti karena daftar
fitur tulis yang hanya ada di `index.html` (§3) berisi lebih dari pembatalan karcis darurat; owner lalu memutuskan mana yang dikunci dan mana yang tetap
terbuka. Pembatalan karcis darurat pindah ke `/baru/` (§4).

Sumber: kode di cabang `tulang-punggung/25b-antrean`, dan cadangan toko 26 Sep 2026 00.12 WIB (di `_privat/`, tidak masuk repo).
Angka di dokumen ini **jumlah catatan**, bukan rupiah.

## 1. Kode perangkat → aplikasi

| Kode di field `perangkat` | Aplikasi | Bukti di kode | `aplikasi` di denyut |
|---|---|---|---|
| `d-…` | `kasir-darurat-nominal.html` (HP penjaga) | `idPerangkatD()` baris 433–440: kunci `darurat_perangkat_v1`, awalan `'d-'` | `'darurat'` (baris 508) |
| `k-…` | `kasir.html` (alat owner) | `idPerangkat()` baris 796–803: kunci `kasir_perangkat_v1`, awalan `'k-'` | `'kasir'` (baris 840) |
| `p-…` | `index.html` **atau** `/baru/` | `index.html` `idPerangkat()` baris 11898–11906 dan `baru/js/data/firebase.js` baris 180–187: **kunci sama** `miqbal_perangkat_v1`, awalan sama `'p-'` | `'sistem'` (`index.html` 11743) / `'baru'` (`firebase.js` 213) |
| nama bebas: "Web Owner", "Iphone Owner", "Mac Owner", "Web Oener" | `index.html` **atau** `/baru/` | `perangkatRingkas()` di kedua aplikasi menulis nama perangkat (kunci `miqbal_perangkat_label_v1`) menggantikan kode `p-` kalau sudah dinamai. Nama diisi di Setelan sistem lama (`ubahNamaPerangkat`, 11911) atau Menu › Sistem › Perangkat (`namaiPerangkat`, `firebase.js` 188) | seperti baris di atas |

Sistem lama dan sistem baru berada di alamat yang sama, jadi **satu peramban = satu kode `p-` dan satu nama untuk dua aplikasi**. Akibatnya:

- Dari dokumennya saja, tulisan kedua aplikasi hanya bisa dibedakan lewat `olehUid` / `diubahOlehUid`. Field ini ditulis `/baru/` sejak putaran 23
  dan pertama terlihat **24 Sep 2026 17.20 WIB**. Sebelum waktu itu, tulisan sistem baru dan sistem lama tidak bisa dipisahkan. [ASUMSI] Tidak ada
  penanda lain yang andal. Kalau sistem lama menulis ulang dokumen buatan `/baru/`, uid lama ikut terbawa, jadi hitungan "/baru/" bisa sedikit lebih.
- Denyut kedua aplikasi menulis dokumen `perangkatStatus/{p-…}` yang **sama**, sehingga isi `aplikasi` bergantian antara `'sistem'` dan `'baru'`.

Perangkat pencipta catatan dalam 30 hari terakhir: `d-mthwn92b-05z6o` (kasir darurat, HP penjaga) 732 · `k-mtazqwgj-9henx` (kasir.html) 106 ·
`d-mtb1harl-k9qe5` (kasir darurat, dipakai untuk uji) 10 · `d-mtaz2lwz-23dbh` 2 · sisanya `p-…` dan nama perangkat owner.

## 2. Tulisan 30 hari per aplikasi & jenis tindakan

Jendela: 27 Agu 2026 00.12 → 26 Sep 2026 00.12 WIB. "Diubah" = tulisan terakhir dokumen berbeda dari saat dibuat (> 10 menit). Hapus (deleteDoc)
tidak terlihat di cadangan, dan `logAktivitas` tidak ikut diunduh. [BELUM TERVERIFIKASI] Jumlah penghapusan per aplikasi.

**Ringkas 30 hari** (baris "index.html" = sistem lama **atau** sistem baru sebelum 24 Sep 17.20, karena tidak bisa dipisah):

| Aplikasi | Dibuat | Diubah | Jenis terbanyak |
|---|---:|---:|---|
| kasir darurat (`d-`) | 744 | 0 | karcis nominal 743 · barang tuts bernama 1 |
| kasir.html (`k-`) | 106 | 0 | nota 86 · kantong literan 20 |
| /baru/ (ber-uid) | 166 | 68 | rincian karcis 61 · nota 45 · tandai dirinci 51 |
| index.html · atau /baru/ sebelum 24 Sep 17.20 | 2.526 | 795 | nota 852 · rincian karcis 848 · tandai dirinci 670 · kantong literan 414 · adukan 71 · uang keluar 65 · bayar bon 53 · **batal karcis darurat 9** · **batal nota lain 5** |

**Sejak 24 Sep 2026 17.20 WIB** (±31 jam; di sini "tanpa uid" pasti sistem lama):

| Aplikasi | Jenis tindakan | Dibuat | Diubah |
|---|---|---:|---:|
| kasir darurat | karcis nominal / barang tuts bernama | 8 | 0 |
| /baru/ | rincian karcis 61 · nota 45 · kantong literan 23 · adukan 8 · cocokkan 10 · wadah 11 · cadangan 3 · bayar bon 2 · retur 1 · uang keluar 1 · kantong kemasan 1 | 166 | — |
| /baru/ | tandai dirinci 51 · kartu pelanggan 5 · setelan 4 · absen 2 · tutup hari, setoran, amplop, modal, titik kas, pindah uang 1 masing-masing | — | 68 |
| **index.html** | **batal karcis kasir darurat** (2 karcis nominal + 1 barang tuts bernama, alasan "uji rules") | **0** | **3** |

Jadi, dalam jendela yang atribusinya pasti, sistem lama **tidak membuat satu catatan pun**. Yang diubahnya hanya pembatalan karcis kasir darurat.
Ini cocok dengan keterangan owner (25 Sep). Keterbatasannya, jendela bersih ini baru ±31 jam.

## 3. Fitur yang menulis data dan HANYA ada di `index.html`

Sensus: 75 fungsi di `index.html` memanggil `setDoc` / `deleteDoc` / `runTransaction` (langsung atau lewat `simpanKeFirestore` /
`hapusDariFirestore`). Tiap fungsi dicocokkan dengan jalur tulis di `baru/js/layar/*.js`. Yang **tidak punya padanan**:

| # | Fitur | Fungsi `index.html` (baris) | Koleksi | Di `/baru/` | Dipakai 30 hari? |
|---|---|---|---|---|---|
| 1 | **Batalkan karcis kasir darurat** yang salah ketik | `mulaiBatalkanTrx` (32117) | penjualan | **dibangun putaran ini (§4)** | 9 · sejak 24 Sep: 3 |
| 2 | **Pulihkan data dari berkas cadangan** | `muatDariFile` (12170) | semua | tidak ada, **keputusan owner** (BACA-DULU, SS3: "memulihkan dari berkas TETAP lewat Setelan sistem lama") | tidak terukur |
| 3 | Batalkan nota **selain** karcis darurat, sesudah 90 detik | `mulaiBatalkanTrx` (32117) | penjualan | hanya "batalkan nota barusan" ≤ 90 detik | 5 (sebelum 24 Sep) |
| 4 | Hapus nota | `hapusPenjualan` (12432) | penjualan | tidak ada | tidak terukur |
| 5 | Koreksi jumlah / barang nota lama | `simpanKoreksiTrx` (31990) | penjualan | tidak ada (jalan lain: retur hari ini) | 1 |
| 6 | Catat bon lama pelanggan (saldo awal piutang, tanggal bebas) | `simpanPiutangAwal` (29697) | piutangMutasi | hanya saldo pembuka tutup buku | 0 (terakhir ±20 Agu) |
| 7 | Hapus uang keluar lama | `hapusHarian` (13994) | pengeluaranHarian | hanya urungkan yang barusan | tidak terukur |
| 8 | Hapus tagihan bulanan | `hapusBulanan` (13055) | biayaBulanan | tidak ada | tidak terukur |
| 9 | Hapus retur | `hapusRetur` (16195) | retur, karantina | hanya ikut nota tukar yang barusan dibatalkan | tidak terukur |
| 10 | Hapus harga katalog | `hapusHargaLiteran/Karung/Kemasan` (30434/30460/30489) | katalogHarga* | tidak ada | tidak terukur |
| 11 | Jenis beras per merek | `simpanJenisBeras` (33061) | pengaturan/jenisBeras | dibaca saja | **ya**, terakhir 22 Sep (tanpa uid) |
| 12 | Daftar & PIN operator kasir | `simpanModalJaga` (33308) | pengaturan/aksesKasir | tidak ada | terakhir 5 Sep |
| 13 | PIN owner | `simpanPinOwnerBaru` (33174) | pengaturan/keamanan | tidak ada (sistem baru memakai akun) | terakhir 14 Agu |
| 14 | Titipan uang keluar (titip / setujui / tolak) | `titipkanPengeluaranHarian` (13426), `setujuiTitipan` (13386), `tolakTitipan` (13414) | titipanHarian | tidak ada | 0 dokumen sepanjang masa |
| 15 | Tembusan stok | `catatTembusanStok` (15460) | tembusanStok | tidak ada | 0 dokumen sepanjang masa |
| 16 | Alat perbaikan massal: isi HPP nota lama, perbaiki cara bayar lama, perbaiki total kg | `simpanIsiHpp` (29089), `perbaikiCaraBayarLama` (22738), `perbaikiTotalKgSemua` (30217) | penjualan | tidak ada | tidak terukur |

Punya padanan di `/baru/` (tidak masuk daftar): jual & keranjang, kasir darurat (rinci, perbaiki, tarik balik), retur & tukar & karantina,
pesanan, kedatangan (catat/koreksi/hapus), adukan, HPP, kantong (beli/opname), cocokkan, harga & terbitkan ringkasan kasir, bon pemasok (bayar, bon lama),
bon pelanggan (bayar, hapus buku), kartu pelanggan & THR, uang keluar & tagihan bulanan (catat), kasbon, amplop, modal & utang owner, pindah uang,
tutup hari & titik kas, tempat simpan, tutup buku tahunan (cara baru: arsip, bukan hapus). Infrastruktur (antrean tunda, denyut, jejak) ikut aplikasinya.

**Kesimpulan Tahap 0:** daftar di atas berisi 15 fitur selain pembatalan karcis darurat. Yang terlihat dipakai dalam 30 hari: #3, #5, #11, dan #12.
Sesudah 24 Sep 17.20 tidak ada satu pun yang dipakai. **Kunci tulis `index.html` tidak dipasang** sampai owner memutuskan (§5).

## 4. Pembatalan karcis darurat di `/baru/` (B.2)

**Letak:** Jual → pita *"N karcis kasir belum dirinci … ketuk untuk merinci atau membatalkan yang salah ketik"*. Kalau tidak ada karcis yang
menunggu, pitanya *"N catatan kasir darurat hari ini — ketuk untuk melihat / membatalkan yang salah ketik"*.
**Ketukan 1** membuka lembar **Karcis kasir**. **Ketukan 2** adalah **batalkan** di baris karcisnya, lalu alasan (wajib) dan
**Batalkan karcis ini**. Barang dari tuts bernama kasir darurat hari ini punya daftar sendiri di lembar yang sama.

**Kode:** `baru/js/layar/karcis-logika.js` → `susunBatalKarcis`, `karcisDaruratHari`, `kcDariDarurat`. `baru/js/layar/jual.js` → aksi `kcBatal*`.
Keadaan `kcBatal` dijaga penjaga isian (`ISIAN_JUAL_LAIN`), jadi alasan yang sedang diketik tidak terbawa ke akun berikutnya.

**Bentuk dokumen sama dengan sistem lama:**

| | `index.html` `mulaiBatalkanTrx` | `/baru/` `susunBatalKarcis` |
|---|---|---|
| Dokumen | `{ ...p, dibatalkan: true, alasanKoreksi, dikoreksiPada, dibatalkanPada }`, id sama, baris tidak dihapus | sama persis (uji membaca daftar field dari sumber `index.html`) |
| Kantong literan pasangan | `hapusDariFirestore(stokBahanLiteran, p.id + 1)` | `hapus: [{ stokBahanLiteran, p.id + 1 }]` |
| Atribusi | `diubahOleh`, `diubahPerangkat`, `diubahPada` (`simpanKeFirestore`) | sama, **ditambah** `diubahOlehUid` (atribusi akun putaran 23, ada di semua tulisan `/baru/`) |
| Jenis baru | tidak ada | tidak ada |

Dibandingkan dengan pembatalan sungguhan dari sistem lama, `penjualan/1790333361985.6816` (karcis uji v4, dibatalkan 25 Sep 18.19 WIB): himpunan
field-nya **sama**, kecuali `diubahOlehUid`. Dijaga oleh `alat-uji/uji_batal_karcis.py` (CI, dengan kontrol).
Aturan: owner mengubah `penjualan` lewat `tglUbah` tanpa batasan field. Bulan terkunci ditolak di layar dengan kalimat, dan di server oleh rules v4.

## 5. Keputusan owner (26 Sep 2026): pilihan (b), dipersempit

Alasan owner: antrean hanya macet karena **tulisan bertanggal** yang ditolak; setelan tidak pernah ditolak.

| | Fitur (§3) |
|---|---|
| **DIKUNCI** | semua jalan tulis catatan bertanggal — batal/hapus/koreksi nota selain karcis (#3–#5), catat bon lama pelanggan (#6), hapus uang keluar / tagihan bulanan / retur / harga lama (#7–#10), titipan uang keluar (#14), tembusan stok (#15), alat perbaikan massal (#16). Batal karcis darurat (#1) juga dikunci di sini — jalannya sekarang di `/baru/`. |
| **TETAP TERBUKA** | setelan jenis beras (#11), daftar & PIN operator kasir (#12), PIN owner (#13), dan "pulihkan dari berkas cadangan" (#2) lewat **konfirmasi ketik** PULIHKAN — prosedurnya `docs/prosedur-pulih-darurat.md` (di bawah v4 pemulihan pasti ditolak; butuh aturan darurat sebentar). |
| **Putaran tersendiri** | setelan jenis beras, operator kasir, dan PIN **dipindah ke `/baru/`**; sesudah itu ketiganya ikut dikunci di sini. |

Semua jalan tulis lain yang sudah punya padanan di `/baru/` (jual, kedatangan, harga, kartu pelanggan, pesanan, tutup hari, titik kas, tempat simpan,
dll.) ikut dikunci — yang terbuka hanya daftar di atas.

## 6. Yang terpasang (B.3–B.4)

- **Satu penjaga:** `penjagaTulis(jalur, koleksi, id)` di `index.html`. Dipanggil di baris pertama `simpanKeFirestore` dan `hapusDariFirestore`,
  sebelum ketiga `runTransaction` (layak jual karantina, pengganti tukar, tutup hari), di penerbit katalog kasir, di denyut, dan di antrean lama.
  Ditolak = modal "Sistem lama sekarang hanya-baca. Catat dan batalkan di /baru/" dengan tombol ke `/baru/`; tidak ada yang ditulis dan tidak ada yang
  masuk antrean. Alert lama "gagal simpan (cek internet)" yang datang tepat sesudahnya diredam, karena kalimat itu salah di sini.
- **Terbuka persis** `pengaturan/jenisBeras`, `pengaturan/aksesKasir`, `pengaturan/keamanan`, plus mode pulih selama `muatDariFile` sesudah PULIHKAN.
- **Bukan catatan, tetap jalan:** katalog kasir (`ringkasanKasir/aktif`), denyut perangkat, antrean lama sekali. **Temuan:** `/baru/` tidak punya
  penerbit katalog kasir — `ringkasanKasir` hanya diterbitkan `index.html`, otomatis tiap data berubah selama halaman itu terbuka. Kalau jalur ini ikut
  dikunci, harga & modal di tuts kasir membeku. Memindahkan penerbitnya ke `/baru/` = putaran tersendiri.
- **Pita permanen** di atas halaman dengan tautan ke `/baru/`. Fitur baca (laporan, riwayat) tetap jalan.
- **Antrean lama:** dikirim **sekali** sesudah masuk (dan sekali saat sinyal kembali kalau belum sempat). Berhasil = selesai. Ditolak server = daftar
  "ditolak" di perangkat itu (`miqbal_antrean_ditolak_v1`, ditulis dulu baru dicabut dari antrean), tampil di pita untuk dicatat ulang di `/baru/`.
  Sinyal putus = tetap di antrean; pita menawarkan "kirim sekali lagi". Perulangan tiap 30 detik dan modal sandi "Database terkunci" dari antrean
  sudah dicabut. Denyut sistem lama kini melaporkan jumlah yang ditolak (`gagal`).
- **Mesin beku tidak disentuh:** `beku2.py --sidik` 28/28.
- **Dijaga:** `alat-uji/uji_sistem_lama_bacasaja.py` (statis: tiap `setDoc`/`deleteDoc`/`runTransaction` di fungsi berpenjaga, daftar terbuka persis
  keputusan owner; peramban: `index.html` sungguhan + Firebase palsu — antrean sekali, 35 koleksi ditolak, tombol sungguhan, yang terbuka, pulihkan,
  baca riwayat). `KP_SIAP_25B = true`.

## 7. Putaran 25c (27 Sep 2026): pindahan terakhir — tinggal baca riwayat & pulihkan

Yang di §5 masih "TETAP TERBUKA" dan di §6 "bukan catatan, tetap jalan" pindah ke `/baru/` (rincian: `docs/peta-pindahan-terakhir.md`):

| Dulu di `index.html` | Sekarang di `/baru/` | Di `index.html` |
|---|---|---|
| Katalog kasir (`ringkasanKasir/aktif`) diterbitkan tiap data berubah | diterbitkan `/baru/` tiap data berubah + ikut kiriman terbit harga; bentuk sama persis | ditutup TANPA modal (`JALUR_DIAM`) |
| Setelan jenis beras (#11) | Harga & Pemasok › Katalog harga › Jenis beras (tampil juga di Stok & Jual) | ditolak penjaga, modal menunjuk tempat barunya |
| Daftar & PIN operator kasir (#12) | Menu › Peran & persetujuan › Kasir & PIN — **tanpa PIN** (keputusan owner: dicabut) | ditolak penjaga |
| PIN owner (#13) | Menu › Peran & persetujuan › Kasir & PIN (bentuk sama, hanya hasil acak) | ditolak penjaga |

**Yang tersisa di sistem lama:** membaca (riwayat, laporan), denyut perangkat, antrean lama yang dikirim sekali, dan **pulihkan dari berkas cadangan**
lewat ketik PULIHKAN (mode pulih meloloskan semua tulisan, tidak bergantung pada daftar terbuka — `docs/prosedur-pulih-darurat.md` tidak berubah).
`TULIS_TERBUKA` kosong. Pita: **"Sistem lama hanya untuk membaca riwayat dan pemulihan darurat."** Dijaga `alat-uji/uji_sistem_lama_bacasaja.py`
(diperbarui ke keputusan ini, jumlah pemeriksaan sama) dan `alat-uji/uji_katalog_kasir.py`.

## 8. Dihapus 3 Okt 2026 (perintah owner: "bumi hanguskan")

Owner memutuskan sistem lama (`index.html` di akar) **dan** `kasir.html` dibumihanguskan. Prasyarat owner beres hari itu: HP kasir melapor 0 antrean /
0 ditolak, dan perangkat lama ditandai "sudah tidak dipakai" di `/baru/` (tanpa itu daftar periksa kunci bulan bisa macet permanen, karena perangkat
yang denyut terakhirnya melapor antrean/ditolak tidak bisa dinyatakan tidak dipakai lagi).

- **Versi terakhir keduanya utuh** di tag git **`sistem-lama-terakhir`** (commit `48a694d`, beserta `lib/`, `manifest-kasir.json`, ikon kasir 192/512).
  §1–7 di atas = sejarah sampai tag itu.
- **Di situs:** `index.html` & `kasir.html` kini **halaman pengalih** ke `/baru/` — tanpa script, meta refresh + tautan, CSP
  `default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'` (+ `manifest-src 'self'` di `index.html`, yang
  tetap menautkan `manifest-sistem.json`). Sengaja tidak dihapus: perangkat tanpa service worker yang membuka alamat lama tidak kena 404. Dijaga
  `alat-uji/uji_csp.py` + `alat-uji/uji_pensiun_sistem_lama.py`.
- **`sw-kasir.js` v31:** `FILES` hanya berkas yang ada (kasir darurat + ikon 180/32); `kasir.html` tidak lagi disimpan/disajikan dari cache, jadi
  pengalih terbaru dari jaringan yang tampil. Cache v30 (berisi `kasir.html` lama) terhapus saat v31 aktif. Kasir darurat hanya ikut naik versi
  (`VERSI_APLIKASI` kasir-v31, label "versi 3 Okt"); `KK_VERSI_KASIR_TERBARU` = kasir-v31; lantai kunci bulan `KP_VERSI_KASIR_25B` tetap kasir-v26.
  Beranda `/baru/` tidak lagi menyebut perangkat `kasir.html` (aplikasi `kasir`, kode k-) sebagai "versi baru terpasang saat dibuka ulang".
- **Ikut dihapus dari repo:** `lib/lz-string.js`, `lib/kemas-worker.js`, `manifest-kasir.json`, `icon-kasir-192.png`, `icon-kasir-512.png`;
  alat uji yang objeknya hilang: `alat-uji/harness/`, `pindah_mesin.py`, `uji_sistem_lama_bacasaja.py`, `uji_dua_arah.py`, `uji_gagal_tertutup.py`,
  `uji_onclick_aman.py`, `uji_stok_minus.py`, `ukur_jepitan.sh`.
- **Pembanding uji yang dulu membaca `index.html`/`kasir.html`:** penyusun & aturan sistem lama di `baru/js/mesin/pembantu.js` kini **terkunci sidik**
  (`alat-uji/pembantu.sha256`, 55 fungsi + 36 konstanta — dicatat saat terbukti byte-sama dengan `index.html` di tag); kunci dokumen yang ditulis
  sistem lama (katalog kasir, jenis beras, operator & PIN, pembatalan karcis, retur & karantina) dibekukan di uji masing-masing, diekstrak dari tag.
  Sumber kebenaran mesin beku = `baru/js/mesin/beku.js` + `pembantu.js`, gerbang `beku2.py --sidik`; `tulisSaldoPembuka` & `thPagar` pensiun
  (baris acuannya di `beku.sha256` dibiarkan, dilewati).
- **Jalan mundur:** `docs/prosedur-pulih-darurat.md` — sistem lama dijalankan di komputer dari POHON tag (bukan diterbitkan lagi), hanya untuk
  memulihkan dari berkas cadangan; keterbatasannya (27 dari 56 koleksi) tertulis di sana.

**Tindak lanjut yang SENGAJA tidak dikerjakan di putaran ini (keputusan owner):** tab Menu › Kasir & PIN di `/baru/` kehilangan pembaca
(`pengaturan/aksesKasir` & `pengaturan/keamanan`); katalog kasir masih membawa `piutang` + `bayarBon*` yang kini tanpa pembaca (dibaca akun kasir@);
hak kasir@ di rules (baca `aksesKasir`, create `piutangMutasi`/`stokBahanLiteran`) tidak dipakai lagi; salinan lokal sistem lama di localStorage tidak
punya tombol pembersih; `/baru/` belum punya pemulih dari berkas; `404.html` di akar (opsional).

