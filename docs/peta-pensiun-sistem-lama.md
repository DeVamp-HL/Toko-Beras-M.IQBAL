# Peta pensiun sistem lama — putaran 25b, Tahap 0

**Status: BERHENTI sebelum mematikan apa pun.** Daftar fitur yang menulis data dan hanya ada di `index.html` (§3) berisi **lebih dari**
pembatalan karcis kasir darurat. Sesuai prompt 25b, `index.html` **belum** dijadikan hanya-baca (Bagian B.3–B.4 menunggu keputusan owner, §5).
Yang tidak mematikan apa pun tetap dikerjakan: pembatalan karcis darurat di `/baru/` (§4) dan antrean kasir (Bagian A).

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

## 5. Keputusan owner yang dibutuhkan sebelum B.3–B.4

1. **Kunci tulis penuh**, fitur #2–#16 hilang dari sistem lama. Risiko terbesar #2 (pulihkan dari cadangan): sesudah dikunci, memulihkan data
   dari berkas tidak bisa lagi lewat aplikasi mana pun.
2. **Kunci dengan satu pengecualian sempit**: hanya "pulihkan dari berkas cadangan" yang tetap lewat penjaga, dengan konfirmasi ketik. Sisanya
   hanya-baca. #11 (jenis beras) perlu tempat di `/baru/` atau diterima hanya-baca.
3. **Bangun dulu di `/baru/`** fitur yang dianggap perlu (mis. #3 batal nota lama, #6 bon lama pelanggan, #11 jenis beras), lalu kunci.

Selama belum diputuskan, `KP_SIAP_25B` tetap `false`. Butir ⛔ pertama daftar periksa kunci bulan tetap memblokir, karena antrean `index.html`
masih macet di catatan yang ditolak.
