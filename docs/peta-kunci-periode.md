# Peta kunci periode: putaran 25, Tahap 0

Dibuat 25 Sep 2026 di cabang `tulang-punggung/25-kunci-periode`. Commit ini **tidak mengubah perilaku apa pun**: tidak ada rules, layar, atau
logika yang berubah. Sumbernya: kode `baru/` di main `a339f51`, `index.html` dan `kasir*.html` (hanya dibaca), dokumentasi resmi Firebase
(URL di §1), dan cadangan toko 25 Sep 2026 (hanya untuk pratinjau di §8; berkas cadangan tidak masuk repo).

> **STATUS: BERHENTI DI TAHAP 0.** Kolom "tanpa padanan" di §3 **tidak kosong**. Menurut prompt putaran 25 ("Kalau tidak kosong, berhenti dan
> lapor"), Tahap 1–5 **belum dikerjakan**. Enam keputusan yang dibutuhkan ada di §4, masing-masing dengan pilihan dan usulan.

## 0. Ringkas

1. **Menghitung bulan WIB di rules bisa dilakukan** hanya dengan fungsi yang terdokumentasi, tanpa aritmetika timestamp:
   `timestamp.value(request.time.toMillis() + 25200000)` lalu `.year()` / `.month()` / `.day()`. Tulisan bertanggal bulan berjalan tidak memanggil
   `get()` sama sekali (§1).
2. **Koleksi yang dikunci:** 20 koleksi dibaca mesin uang, stok, atau pajak menurut tanggalnya. Nama field tanggalnya ada 5: `tanggal`, `bulan`,
   `bonTanggal`, `dicatatPada`, dan `tanggal` pada titik kas. Semua koleksi lain adalah setelan, jejak, atau catatan kerja (§2).
3. **Ada tiga jenis jalur tanpa padanan pembalik** (§3–§4): (a) **tutup buku tahunan**, yang memindahkan seluruh dokumen setahun ke arsip, jadi
   menghapus dokumen bulan terkunci; (b) **angka uang di catatan pembelian** bulan terkunci (harga modal kedatangan/adukan, utang pemasok, uang beli kantong); (c) **ganti nama pelanggan**
   (SATUKAN, hapus nama) yang menulis ulang nota bulan terkunci.
4. Dua koleksi "catatan tentang masa lalu" **justru menggeser neraca bulan lampau**: bon lama pemasok (mesin memakai `bonTanggal`) dan saldo awal
   piutang (mesin memakai `tanggal` sebagai umur utang). Perlakuannya tidak bisa disamakan dengan `pajakOmzetLuar` tanpa keputusan owner (§4 K4).
5. **Sistem lama macet, tidak sekadar gagal.** `index.html` memasukkan tulisan yang ditolak ke antrean tunda, mengirim ulang kepala antrean tiap 30
   detik, dan memunculkan *"Database terkunci. Masukkan sandi OWNER untuk lanjut."* berulang-ulang. `kasir-darurat-nominal.html` dan `kasir.html`
   memperlakukan penolakan server (HTTP 403) sebagai "belum masuk": layar masuk muncul, dan **semua nota berikutnya tertahan di belakang nota yang
   ditolak** (§5).
6. **Access call:** memasang v4 saja, tanpa satu bulan pun dikunci, sudah membuat beberapa kiriman owner ditolak karena menyentuh lebih dari 20
   dokumen bulan lampau: SATUKAN, hapus nama, arsip tutup buku, dan rinci karcis besar. Kiriman tablet yang tertunda melewati pergantian bulan
   menjadi 2 access call per dokumen (§6).

## 1. Rules: bulan WIB, `get()`, dan batas access call

Dokumentasi resmi (dibuka 25 Sep 2026):

| Fakta | Sumber |
|---|---|
| `rules.Timestamp` adalah *"A timestamp in UTC with nanosecond accuracy."* Metodenya `year()`, `month()`, `day()`, `toMillis()`, dan lainnya. Halaman ini **tidak menyebut** operator `timestamp + duration`. | https://firebase.google.com/docs/reference/rules/rules.Timestamp_ |
| `timestamp.value(epochMillis)` membuat timestamp dari milidetik epoch. | https://firebase.google.com/docs/reference/rules/rules.timestamp_ |
| Integer mendukung `+ - * / %`; `int("2") == 2`. | https://firebase.google.com/docs/reference/rules/rules.Integer |
| String bisa dibandingkan leksikografis (`< <= > >=`); ada operator rentang `s[i:j]` (j tidak termasuk). | https://firebase.google.com/docs/reference/rules/rules.String |
| `get(path)` mengembalikan *"the document, or null if it does not exist."* | https://firebase.google.com/docs/reference/rules/rules.firestore |
| `let` **langsung** menjalankan pencarian (*"the isAdmin assignment enforces a lookup"*). Untuk menunda `get()`, pakai `&&` / `\|\|`. Kedalaman panggilan maksimal 20; `let` maksimal 10 per fungsi. | https://firebase.google.com/docs/rules/rules-language |
| Batas access call: *"10 for single-document requests and query requests. 20 for multi-document reads, transactions, and batched writes. The previous limit of 10 also applies to each operation."* *"Some document access calls may be cached"* (tidak diandalkan, keputusan owner 24 Sep). Melewati batas berarti *permission denied*. | https://firebase.google.com/docs/firestore/security/rules-conditions#access_calls |
| `duration.value(magnitude, unit)` ada (w/d/h/m/s/ms/ns), tapi penjumlahannya dengan timestamp tidak didokumentasikan, jadi **tidak dipakai**. | https://firebase.google.com/docs/reference/rules/rules.duration_ |

**Cara menghitung (sketsa; belum ditulis ke `firestore.rules`):**

```
function wib()              { return timestamp.value(request.time.toMillis() + 25200000); }   // UTC+7, WIB tanpa musim panas
function bulanIni()         { return wib().year() * 100 + wib().month(); }                  // mis. 202609
function bulanDari(s)       { return int(s[0:4]) * 100 + int(s[5:7]); }                     // 'YYYY-MM' atau 'YYYY-MM-DD'
function terkunci(b)        { return b <= bulanDari(get(/databases/$(database)/documents/aturanToko/kunciPeriode).data.get('sampaiBulan', '0000-00')); }
```

- `get()` **hanya** di `terkunci()`, dan `terkunci()` hanya dipanggil di belakang `&&` sesudah terbukti `bulanDari(tgl) < bulanIni()`. Tulisan
  bertanggal bulan berjalan atau sesudahnya tidak memanggil `get()`.
- Pembaruan cukup **satu** `get()`: kunci berbentuk awalan (semua bulan ≤ `sampaiBulan`), jadi yang dinilai cukup bulan terkecil di antara
  tanggal lama dan tanggal baru.
- Dokumen kunci belum ada → `get()` bernilai null → tulisan bulan lampau **ditolak** (gagal tertutup). Karena itu, dokumen kunci harus dibuat
  (dengan `sampaiBulan: null`) **sebelum** v4 ditempel. `.get('sampaiBulan', '0000-00')` membuat null berarti "tidak ada yang terkunci".
- Penghematan tambahan yang bisa dipilih: rules hanya mengizinkan mengunci bulan M mulai **tanggal 2** bulan M+1 (tenggang minimal 1). Dengan
  begitu, tulisan bertanggal bulan lalu yang tiba pada **tanggal 1** tidak perlu `get()`. Contohnya nota tablet yang tertahan offline lewat
  tengah malam.
- Tulis-ulang yang **isinya sama persis** (`request.resource.data == resource.data`) bisa dibebaskan dari kunci karena tidak mengubah apa pun.
  Ini melindungi kirim-ulang idempoten kasir@ dan "muat cadangan" atas dokumen yang sudah ada.

**Kesimpulan §1:** keputusan desain 4 **bisa dilaksanakan**. Masalahnya ada di jalur tanpa padanan (§4), bukan di rules.

## 2. Koleksi: bertanggal atau tidak

Kolom "mesin" = dibaca menurut tanggalnya oleh 28 mesin beku (`baru/js/mesin/beku.js`, `pembantu.js`) atau oleh layar uang/pajak sistem baru
(`uang-logika`, `upah-logika`, `laporan-logika`, `pajak-logika`, `tutup-hari-logika`). Usul **KUNCI** = kena `bolehTanggal()`.

| # | Koleksi | Field tanggal | Format | Mesin | Usul | Catatan |
|---|---|---|---|---|---|---|
| 1 | penjualan | `tanggal` | YYYY-MM-DD | laba, stok, piutang, kas | **KUNCI** | karcis darurat bertanggal hari karcis |
| 2 | retur | `tanggal` | YYYY-MM-DD | laba, stok, kas | **KUNCI** | `notaAsalTanggal` = tanggal nota asal, **bukan** tanggal kunci |
| 3 | pengeluaranHarian | `tanggal` | YYYY-MM-DD | laba, kas, utang owner | **KUNCI** | |
| 4 | piutangMutasi | `tanggal` | YYYY-MM-DD | piutang, kas, laba (hapus buku) | **KUNCI** | saldoAwal: `tanggal` = umur utang (18 dok, sejak 2022) → K4 |
| 5 | kasbonMutasi | `tanggal` | YYYY-MM-DD | kasbon, kas | **KUNCI** | |
| 6 | utangPemasokMutasi | `tanggal` | YYYY-MM-DD | utang pemasok, kas | **KUNCI** | saldoAwal: mesin memakai `bonTanggal` → K4 |
| 7 | utangOwnerMutasi | `tanggal` | YYYY-MM-DD | utang owner | **KUNCI** | |
| 8 | batchMasuk | `tanggal` | YYYY-MM-DD | stok, modal, utang, kas | **KUNCI** | |
| 9 | produksiKemasan | `tanggal` | YYYY-MM-DD | stok kemasan, modal | **KUNCI** | |
| 10 | stokBahanKemasan | `tanggal` | YYYY-MM-DD | stok bahan, kas | **KUNCI** | |
| 11 | stokBahanLiteran | `tanggal` | YYYY-MM-DD | stok bahan, kas | **KUNCI** | kasir@ ikut menulis (`id+1` tipe pakai) |
| 12 | penyesuaianStok | `tanggal` | YYYY-MM-DD | stok, susut laba | **KUNCI** | |
| 13 | penyesuaianKemasan | `tanggal` | YYYY-MM-DD | stok kemasan, susut laba | **KUNCI** | |
| 14 | amplopLaba | `tanggal` | YYYY-MM-DD | amplop, kas | **KUNCI** | |
| 15 | modalOwner | `tanggal` | YYYY-MM-DD | modal owner | **KUNCI** | |
| 16 | setoranKas | `tanggal` | YYYY-MM-DD | modal owner | **KUNCI** | |
| 17 | biayaBulanan | `bulan` (= id) | YYYY-MM | jatah biaya per hari di laba | **KUNCI** | bayar upah menulis bulan hari kerjanya → K5 |
| 18 | tutupHari | `tanggal` (= id) | YYYY-MM-DD | Harian, Tutup hari | **KUNCI** | bukti hitung laci |
| 19 | pindahUang | `tanggal` | YYYY-MM-DD | saldo per tempat | **KUNCI** | |
| 20 | slipUpah | `tanggal` | YYYY-MM-DD | bukti bayar upah | **KUNCI** | uangnya di biayaBulanan + kasbon |
| 21 | pajakSetoran | `dicatatPada` | YYYY-MM-DD | status pajak | **KUNCI (tanggal catat)** | bukan `masaPajak` (keputusan 9); `tanggalSetor` boleh mundur |
| 22 | pengaturan | `tanggal` hanya di dok `titikKas` | YYYY-MM-DD | kasPada | **khusus** | titikKas: hanya nilai **baru** yang dinilai (titik boleh maju dari bulan terkunci). Dok lain = setelan |
| 23 | pajakOmzetLuar | id `YYYY-MM\|sumber` | YYYY-MM | pajak | **tidak** | keputusan 9: angka pemilik lama boleh datang kapan saja |
| 24 | arsipTahun | `tahun` | YYYY | — | **→ K1** | tutup buku |
| 25 | karantina | `tanggal` | YYYY-MM-DD | hanya tbDaftarKoleksi | tidak | keputusan (statusTindakan) memperbarui dok lama; uangnya di retur/penyesuaian |
| 26 | pesanan | `tanggal` | YYYY-MM-DD | hanya tbDaftarKoleksi | tidak | status berubah belakangan (dibayar/antar/batal); uangnya di nota |
| 27 | titipanHarian | `tanggal` | YYYY-MM-DD | tidak (sengaja terpisah dari mesin) | tidak | belum jadi uang sampai disetujui |
| 28 | tembusanStok | `tanggal` | YYYY-MM-DD | hanya tbDaftarKoleksi | tidak | jejak |
| 29 | absenKaryawan | `bulan` | YYYY-MM | upah (hitungan) | tidak | uangnya lahir saat bayar upah (biayaBulanan + slipUpah) |
| 30 | tutupBukuAcara | `tanggal` | YYYY-MM-DD | tidak | tidak | berita acara; statusnya berubah per langkah |
| 31–36 | logAktivitas · strukKeluar · dokumenCetak · cadanganCatatan · hargaTerbit · bukuHapus | `pada`/`tanggal` | ISO / YYYY-MM-DD | tidak | tidak | **jejak**: urusan putaran 26 (append-only) |
| 37–45 | wadahLiteran · pindahTempat · pindahStok · pelangganTitip · tagihPelanggan · thrPelanggan · pengingat · persetujuan · pesananPemasok | `tanggal` / tidak ada | — | tidak | tidak | catatan kerja; banyak yang diperbarui belakangan |
| 46–59 | aturanToko · katalogHargaKarung/Kemasan/Literan · hargaWadah · hargaPasar · pelangganCatatan · pemasokCatatan · aksesAkun · permintaanAkses · perangkatStatus · ringkasanKasir | ada yang punya `tanggal` = tanggal diubah | — | tidak | tidak | **setelan**. `aturanToko` dan `hargaWadah` punya `tanggal`; kalau dinilai, setelan yang terakhir diubah bulan lalu jadi tidak bisa diubah lagi. `aturanToko/kunciPeriode` punya aturan sendiri |

Di luar Firestore: `petaJenisBeras` (localStorage), tidak kena.
Di cadangan 25 Sep, **semua dokumen yang ada** di koleksi 1–21 punya field tanggalnya dengan format di atas (diperiksa per koleksi). Dokumen tanpa tanggal
akan ditolak (gagal tertutup).

## 3. Jalur yang mengubah atau menghapus dokumen lama

"Padanan" = pembalik bertanggal hari ini memakai **jenis dokumen yang sudah dikenal mesin beku**. Rujukan ke catatan asal memakai field yang
**sudah ada** (disebut). Baris yang ditandai **TANPA PADANAN** menjadi alasan berhenti.

### 3a. Sistem baru (`baru/js/layar/*-logika.js`)

| Jalur (fungsi) | Koleksi yang diubah/dihapus | Di bulan terkunci | Padanan pembalik (jenis lama · field rujukan) |
|---|---|---|---|
| Batalkan nota ≤ 90 detik (`jual-logika` 722) | penjualan `dibatalkan`, hapus kantong id+1, piutang, retur, karantina | praktis tak terjadi (kunci paling cepat tanggal 2) | — |
| Rinci karcis (`karcis-logika susunRinciDokumen`) | penjualan baru bertanggal karcis + karcis asal `dikoreksiOleh` | ditolak — sesuai prompt: *"sesudah dikunci, karcis ini tidak bisa dirinci lagi"* | tidak perlu: omzet sudah tercatat nominal; stok dibetulkan lewat **penyesuaianStok hari ini** saat cocokkan |
| Perbaiki cara bayar / nama karcis (`susunPerbaikanKarcis`) | penjualan pengganti + asal `dikoreksiOleh` | ditolak | Tunai→Bon: **piutangMutasi `saldoAwal` hari ini** (bon yang belum tercatat; kas yang terlanjur lebih muncul di selisih laci). Bon→Tunai: **piutangMutasi `bayar` hari ini** — awas dobel bila selisih laci Agustus sudah menyerapnya. `catatan` menyebut id karcis |
| Tarik balik rincian (`susunUrungRinci`) | penjualan `dibatalkan`, hapus kantong, pulihkan karcis | ditolak | **retur hari ini** (`notaAsalId`, `notaAsalTanggal`) |
| Retur (`retur-logika`) | **membuat** retur hari ini, menunjuk nota lama | boleh; ini justru pembaliknya | `notaAsalId` · `notaAsalTanggal` · `notaAsalKunci` (sudah ada) |
| Tukar yatim: pengganti sudah tercatat (`susunPenggantiTercatat`) | retur lama + `penggantiDikonfirmasi` | ditolak bila returnya di bulan terkunci | tidak mengubah angka; cukup ditolak dengan kalimat yang jelas |
| Keputusan karantina "layak jual" (`susunPutusKarantina`) | retur lama `kondisi: utuh` | ditolak bila returnya di bulan terkunci | **penyesuaianStok hari ini** + kg (seperti jalur rework yang sudah ada: `dariRework`, `alasan` menyebut id retur) |
| Keputusan karantina lain (buang/balik/rework) | karantina `statusTindakan` | tidak kena (karantina tidak dikunci) | — |
| Hapus buku piutang (`bon-logika susunHapusBon`) | **membuat** piutangMutasi hari ini | boleh | — |
| Bayar bon pemasok, urungkan ≤ 90 detik (`bon-pemasok-logika`) | hapus utangPemasokMutasi + biaya admin barusan | praktis tak terjadi | — |
| Bon lama pemasok (`susunBonLama`) | **membuat** saldoAwal, `tanggal` hari ini, `bonTanggal` lama | **→ K4** | — |
| Koreksi kedatangan (`stok-catat susunSimpanMasuk` dengan `lama`) | batchMasuk lama ditimpa (kg, harga, cara bayar) | ditolak | kg: **penyesuaianStok hari ini**. **Harga modal & utang/kas: TANPA PADANAN → K2** (`bayar` utang pemasok = kas keluar, bukan pembetul) |
| Hapus kedatangan (`susunHapusKedatangan`) | hapus batchMasuk + produksi pasangan | ditolak | kg: **penyesuaianStok hari ini**. **Utang/kas: TANPA PADANAN → K2** |
| Koreksi HPP satuan & massal (`stok-hpp-logika`) | batchMasuk lama ditimpa harganya | ditolak | **TANPA PADANAN → K2** |
| Koreksi adukan (`susunKoreksiAdukan`) | produksiKemasan pengganti **bertanggal adukan** + asal `dikoreksiOleh` | ditolak | **TANPA PADANAN → K2** (modal per unit) |
| Hapus adukan (`susunHapusAdukan`) | hapus produksiKemasan + kantong id+1 | ditolak | **penyesuaianStok** (+ kg bahan) & **penyesuaianKemasan** (− unit) hari ini, `alasan` menyebut id adukan |
| Hapus beli kantong (`stok-kantong susunHapusBeli`) | hapus stokBahan* tipe beli | ditolak | lembar: **stokBahan\* hari ini tipe `opname`** (dikenal kedua mesin bahan). **Uangnya: TANPA PADANAN → K2** |
| Tutup hari ulang (`tutup-hari susunTutup`) | tutupHari/amplop/setoran/modal/titik hari ini, hapus mdr & timbang hari ini | selalu **hari ini** (tanggal perangkat); tidak menyentuh bulan lalu | — |
| Bayar tagihan bulanan (`uang-logika susunBayarTagihan`) | biayaBulanan **bulan ini** | tidak kena | — |
| Bayar upah (`upah-logika susunBayarUpah`) | biayaBulanan **tiap bulan hari kerjanya** | ditolak bila hari kerjanya di bulan terkunci | **→ K5** |
| Absen (`susunAbsen`) | absenKaryawan | tidak kena (tidak dikunci) | — |
| Pindah uang / uang keluar, urungkan ≤ 90 detik | hapus dok barusan | praktis tak terjadi | — |
| Setoran pajak, hapus (`pajak-logika susunHapusSetoran`) | hapus pajakSetoran | ditolak bila dicatat di bulan terkunci | tidak ada jenis "setoran negatif"; salah catat di bulan terkunci tetap tinggal (setoran sungguhan ada di Coretax) → K6 |
| Omzet luar, hapus (`susunHapusOmzetLuar`) | hapus pajakOmzetLuar | tidak kena (keputusan 9) | — |
| **SATUKAN nama** (`pelanggan-logika susunGabung`) | penjualan, piutangMutasi, pesanan, thr, tagih, titip, kartu: tulis ulang nama | ditolak untuk dok bulan terkunci | **TANPA PADANAN → K3** |
| **Hapus nama salah ketik** (`susunHapusNama`) | penjualan `namaPelanggan: ''` | ditolak untuk dok bulan terkunci | **TANPA PADANAN → K3** |
| "Ini dia" (`susunIniDia`) | penjualan **hari ini** saja | tidak kena | — |
| **Tutup buku tahunan** (`tutup-buku-logika susunKunci`, `arsipkanDokumen`) | saldo pembuka (piutang bertanggal **utang tertua**), **hapus seluruh dokumen setahun** (pindah ke arsipTahun) | ditolak | **TANPA PADANAN → K1** |
| Batalkan tutup buku (`susunBatal`, `pulihkanArsip`) | hapus saldo pembuka, **tulis ulang** dokumen setahun | ditolak | **TANPA PADANAN → K1** |
| Pesanan, pesanan pemasok, THR serah, tagih, titip, pengingat, persetujuan, wadah, tempat, kartu pelanggan, setelan | koleksi yang tidak dikunci | tidak kena | — |

### 3b. Sistem lama (`index.html`, hanya dibaca)

Semua tulisan lewat `simpanKeFirestore` (setDoc) atau `hapusDariFirestore` (deleteDoc). Jalur yang menyentuh dokumen **bertanggal bulan lampau**:

| Fungsi `index.html` | Koleksi | Padanan di sistem baru |
|---|---|---|
| `simpanKoreksiTrx`, `mulaiBatalkanTrx`, `hapusPenjualan`, `urungkanTransaksi` | penjualan, kantong id+1, retur, karantina | retur hari ini |
| `simpanRinciTrx`, `urungkanRinciTrx`, `simpanPerbaikanDarurat` | penjualan (karcis) | seperti 3a |
| `simpanIsiHpp`, `perbaikiTotalKgSemua`, `perbaikiCaraBayarLama` | penjualan lama (massal) | HPP: **K2**. Cara bayar Bon→Tunai: piutangMutasi `bayar` hari ini |
| `simpanKedatangan` (edit), `hapusBatch` | batchMasuk, produksi pasangan | seperti 3a (**K2** untuk harga) |
| `simpanProduksi` (edit), `hapusProduksi`, `simpanKoreksiHpp` | produksiKemasan, bahan | seperti 3a (**K2** untuk modal) |
| `simpanBiayaBulanan`, `hapusBulanan` | biayaBulanan bulan lampau | pengeluaranHarian hari ini |
| `tulisPengeluaranHarian` (tanggal bisa dipilih), `hapusHarian`, `lanjutkanPaksaPrive` | pengeluaranHarian | arah yang sama: pengeluaranHarian hari ini; arah sebaliknya: **K2** |
| `hapusRetur`, `returJadiLayakJual`, `putuskanKarantina` | retur, karantina, penyesuaian | penyesuaianStok hari ini |
| `simpanTutupHari`, `simpanTitikKas` | tutupHari, setoran/modal/amplop, titikKas (tanggal bisa dipilih) | tutup hari hari ini |
| `simpanPiutangAwal` (tanggal dipilih), `simpanSaldoAwalUtang` (bonTanggal) | piutangMutasi, utangPemasokMutasi | **K4** |
| `tulisSaldoPembuka`, `hapusDokumenTahun` | tutup buku lama (menghapus, bukan mengarsip) | **K1** |
| `muatDariFile` (muat cadangan: jalur pemulihan yang **sengaja tetap di sistem lama**) | semua koleksi | tulis-ulang yang isinya sama bisa dibebaskan (§1); pemulihan ke basis data kosong untuk bulan terkunci = tempel v3 sementara |

## 4. Tanpa padanan: enam keputusan owner

**K1 · Tutup buku tahunan vs kunci bulanan.** Ritual K6 menulis saldo pembuka piutang bertanggal **utang tertua**. Di cadangan 25 Sep ada 19 nama
berbon, dan semuanya bertanggal bulan lampau, termasuk 2022, 2025, dan Agustus 2026. Ritual itu juga **memindahkan seluruh dokumen setahun ke
arsipTahun**, artinya menghapusnya dari koleksi asal, 200 dokumen per kiriman. "Batalkan" menulis ulang semuanya. Dokumen setahun itu harus
dihapus karena mesin beku membaca semua dokumen dan akan menghitung saldo dua kali. Mesin tidak boleh diubah.
Akibatnya, sesudah Januari–November terkunci, Tutup Buku 2026 (Januari 2027) **tidak bisa berjalan**. Bahkan tanpa satu bulan pun terkunci, v4
menolak kiriman arsip 200 dokumen karena access call melebihi 20.
- (a) Pengecualian sempit di rules. Hapus dokumen bulan terkunci hanya boleh bila kiriman yang sama menulis `arsipTahun/{tahun|koleksi|id}`
  berisi `dok` yang identik, diperiksa dengan `getAfter`. Biayanya 2 access call per dokumen, jadi maksimal 9 dokumen per kiriman: ribuan
  kiriman per tahun. Saldo pembuka piutang juga butuh pengecualian.
- (b) Saldo pembuka piutang diberi tanggal 1 Januari, umurnya pindah ke `catatan` (field sudah ada). Umur piutang di layar jadi tidak jujur.
- (c) **Usul:** kunci bulanan jalan dulu. K6 menolak dengan kalimat jelas selama ada bulan terkunci di tahun itu. Tutup buku dirancang ulang di
  putaran sendiri **sebelum Januari 2027**, dengan (a) atau bentuk lain.

**K2 · Angka uang di catatan pembelian bulan terkunci** (harga modal kedatangan/adukan, utang pemasok yang salah catat, uang beli kantong,
pengeluaran harian yang salah). Koreksi HPP, koreksi/hapus kedatangan, koreksi biaya adukan, dan hapus beli kantong semuanya menulis ulang atau
menghapus dokumen lama. Jenis yang dikenal mesin tidak punya arah sebaliknya: `penyesuaianStok.nilaiRp` memotong laba (susut) tapi tidak
mengubah modal per kg di rak; `koreksiHpp` hanya dibaca layar; `bayar` utang pemasok dihitung kas keluar; `pengeluaranHarian` cuma punya
kategori `toko` dan `owner` (tidak ada "uang kembali"). Yang punya jalan sendiri hanya **kas**: tutup hari berikutnya menghitung laci dan
memasang titik kas baru dari hitungan fisik, jadi salah uang laci di bulan terkunci muncul sebagai selisih laci hari itu.
- (a) **Usul:** ditolak, dengan kalimat *"harga modal / utang bulan terkunci tidak bisa dikoreksi; selisih modal terbawa ke HPP penjualan sisa
  stoknya, selisih kas muncul di tutup hari berikutnya"*. Utang pemasok yang terlanjur salah tetap salah sampai ada jenis pembetulnya.
- (b) Jenis dokumen baru (mis. pembetul utang pemasok tanpa kas, nilai ulang modal): dilarang putaran ini, jadi butuh izin owner dan
  pembekuan ulang mesin.

**K3 · Ganti nama pelanggan lintas bulan terkunci** (SATUKAN, hapus nama salah ketik). Mesin piutang mengelompokkan bon menurut **nama**. Nama di
nota bulan terkunci tidak bisa ditulis ulang.
- (a) **Usul:** hanya dokumen di bulan terbuka yang ditulis ulang. Kalau nama lama masih punya bon **lahir di bulan terkunci**, SATUKAN ditolak
  dan menyebut bulannya. Hapus nama hanya menyentuh bulan terbuka; nota di bulan terkunci tetap bernama lama.
- (b) Pindahkan sisa bon: piutangMutasi saldoAwal **negatif** atas nama lama dan positif atas nama baru, bertanggal hari ini. Jenisnya dikenal,
  tapi nominal negatif tidak pernah dipakai. Ini mengarang, jadi tidak diusulkan.

**K4 · Catatan tentang masa lalu yang menggeser neraca bulan lampau.** Keputusan 9 menyamakannya dengan pajak (dinilai menurut tanggal catat).
Untuk dua koleksi ini, itu berarti **neraca bulan terkunci berubah**:
- bon lama pemasok: `tanggal` = hari dicatat, tapi mesin memakai `bonTanggal` sebagai umur bon;
- saldo awal piutang (`index.html simpanPiutangAwal`, tanggal dipilih bebas): `tanggal` = umur utang dan sekaligus tanggal yang dibaca mesin.
- (a) Dinilai menurut tanggal yang dibaca mesin (`bonTanggal` / `tanggal`). Neraca bulan terkunci tetap, tapi bon lama yang baru ketahuan harus
  bertanggal bulan terbuka dan umurnya hilang.
- (b) Dinilai menurut tanggal catat. Umur tetap jujur, tapi laporan bulan terkunci **tidak lagi final** untuk utang/piutang.
- Usul: (a) untuk bulan yang sudah dilaporkan ke bank/pajak. Owner yang memutuskan.

**K5 · Upah yang dibayar sesudah bulannya terkunci.** `susunBayarUpah` menulis gaji ke `biayaBulanan` **bulan hari kerjanya**. Upah 20 Agu–4 Sep yang
dibayar 5 Sep, sesudah Agustus terkunci, akan ditolak.
- (a) Butir ⛔ daftar periksa: "upah hari kerja Agustus sudah dibayar semua".
- (b) **Usul:** hari kerja bulan terkunci dibukukan ke `biayaBulanan` **bulan pembayaran**. `rincianGaji` sudah membawa `dari`/`sampai`, jadi tanpa
  field baru. Laba bulan terkunci tidak bergeser; biayanya muncul di bulan bayar. Ditambah butir daftar periksa (bukan ⛔): "N hari kerja
  Agustus belum dibayar — akan masuk biaya bulan pembayaran".

**K6 · Catatan setoran pajak yang salah catat di bulan terkunci.** Status pajak **menjumlah** semua setoran per masa (`pajak-logika.js:182`),
dan tidak ada jenis "setoran negatif". Catatan salah yang tidak bisa dihapus membuat "sudah disetor" terbaca lebih besar selamanya.
- (a) Hapus tetap ditolak (keputusan 9 apa adanya); layar menyebut catatan itu, angkanya tetap terjumlah.
- (b) **Usul:** `pajakSetoran` tidak dikunci. Catatan setoran tidak mengubah angka uang toko, dan jejak hapusnya tetap ada di `logAktivitas`.
  Ini mengubah keputusan 9, jadi butuh persetujuan owner.

## 5. Sistem lama yang gagal di bulan terkunci

Semua ini **dilaporkan, tidak diperbaiki** (prompt: `index.html` dan `kasir*.html` jangan disentuh).

| Berkas | Yang terjadi | Kalimat yang dilihat |
|---|---|---|
| `index.html` simpan (setDoc) | Penolakan ditangkap, lalu dokumen masuk **antrean tunda** dan modal masuk muncul. `kirimAntreanTunda` mengirim ulang **kepala** antrean tiap 30 detik; kepala yang ditolak selamanya membuat semua tulisan offline di belakangnya **tidak pernah terkirim**. Jejak `logAktivitas` sudah tertulis "tulis" sebelum ditolak. | *"Database terkunci. Masukkan sandi OWNER untuk lanjut."* — berulang, walau sandinya benar |
| `index.html` hapus (deleteDoc) | Ditolak, lalu alert. Jejak "hapus" sudah tertulis duluan. Hapus bertahap (batch lalu pasangannya) berhenti di langkah pertama. | *"Gagal hapus dari database (offline?). Coba lagi kalau internet sudah nyambung."* — menyalahkan internet |
| `kasir-darurat-nominal.html` | Nota yang tertahan offline, lalu tiba sesudah bulannya terkunci, dijawab server **403**. Berkas ini memperlakukan 403 sebagai "belum masuk": `sedangKirim` berhenti dan layar masuk tampil. Nota itu tetap di **kepala** antrean, jadi **semua nota berikutnya tertahan** di tablet itu. Tidak masuk daftar "ditolak" (daftar itu hanya untuk 4xx selain 401/403). | layar masuk + chip *"Offline · N menunggu · belum masuk"* |
| `kasir.html` (alat owner) | Pola 403 yang sama (baris 690 dan 846). | layar masuk |
| `index.html` tutup buku lama | Langkah 2 menulis saldo pembuka; langkah 3 (`hapusDokumenTahun`) menghapus satu per satu dan berhenti di dokumen bulan terkunci pertama. Stok dan piutang **terhitung dua kali** (R6). | alert galat (isinya tidak diperiksa) |
| `index.html` muat cadangan | Dokumen bulan terkunci yang berbeda dari server ditolak dan masuk antrean tunda (lihat baris pertama). | modal yang sama |

Karena `kasir*.html` tidak boleh disentuh, satu-satunya pengaman adalah **daftar periksa**: sebelum mengunci, semua perangkat kasir harus
antre = 0 dan sudah berdenyut. Prompt menjadikan butir itu *bukan* ⛔. Dengan akibat seperti di atas, usul saya: **⛔**, atau perbaiki
penanganan 403 di kedua berkas kasir dalam putaran kecil sebelum kunci pertama.

## 6. Access call

Aturan v4 yang diusulkan: owner 0 access call untuk bulan berjalan dan **1 per operasi** yang menyentuh bulan lampau. Bukan-owner: 1 (`aksesAkun`) + 1
bila bulan lampau. `logAktivitas` tidak dikunci, jadi 0.

| Kiriman | Operasi bulan lampau | Terburuk | Batas 20 |
|---|---|---|---|
| Owner, nota hari ini | 0 | 0 | aman |
| Owner, rinci karcis bulan lalu (n barang) | n baris + ≤ n kantong + sisa + karcis asal | 2n + 2 | n ≤ 8 aman (sisa 2); **tanpa batas baris owner** |
| Owner, tarik balik rincian | n + n kantong + asal | 2n + 1 | seperti di atas |
| Owner, koreksi/hapus adukan (h hasil) | 2h | 2h | h ≤ 9; **owner tanpa batas hasil** |
| Owner, bayar upah lintas bulan | biayaBulanan bulan lalu | 1 | aman |
| Owner, **SATUKAN / hapus nama** | semua nota nama itu di bulan lampau | sampai 180 | **ditolak walau tanpa kunci** |
| Owner, **tutup buku** (saldo pembuka) | 1 per nama berbon (19 di cadangan 25 Sep) | 19 dan tumbuh | **di ambang** |
| Owner, **tutup buku** (arsip) | 200 per kiriman | 200 | **ditolak** |
| Bukan-owner (tablet; belum dipakai), nota tertahan offline lewat pergantian bulan | 17 dokumen × (akses + kunci) + jejak | **35** | **ditolak** (v3: 18). Perlu batas baru (≤ 8 dokumen) atau pengecualian tanggal 1 (§1) |
| kasir@, karcis | 1 dokumen (+ kantong) | 2 | aman |

Tutup hari sistem baru selalu memakai tanggal **hari ini** menurut perangkat. Menutup lewat tengah malam artinya menutup hari yang baru, jadi
tidak menyentuh bulan lalu (dan tidak memakai access call).

## 7. `lpFinal`: pemakai dan perubahannya (bahan Tahap 4, belum dikerjakan)

`lpFinal(key)` (`laporan-logika.js:53`) sekarang = tahun ≤ era tutup buku. Pemakainya:

| Baris | Pemakai | Bila jadi "tahun ≤ era ATAU bulan ≤ sampaiBulan" |
|---|---|---|
| 72 `labaBulan` | tanda FINAL/DRAF di Laba | bulan terkunci jadi FINAL |
| 102 `bulanan` | Laporan Bulanan | idem |
| 118 rekap omzet DK3 | tanda final per bulan | idem |
| 128 `susunTandaLapor` | **tanda lapor DK3** | bisa dipasang per bulan terkunci (tujuan keputusan 7) |
| 207 `susunCetakan` | cetakan / paket bank tanpa cap DRAF | final bila **semua** bulannya terkunci |
| 311 `daftarTahun`, 318/323 tahunan | memanggil `lpFinal(tahun + '-01')` | **JEBAKAN:** Januari terkunci akan menandai **setahun penuh** final tanpa kunci. Harus diganti dengan "12 bulan terkunci atau tahun ≤ era" |

## 8. Pratinjau daftar periksa Agustus 2026 (cadangan 25 Sep 06.04 WIB)

- Hari berjualan Agustus: 24. **Tanpa tutup hari: 5** (8, 9, 10, 11, 20 Agu). Harus diisi, atau owner menandainya libur.
- Karcis/nota rapikan Agustus yang belum dirinci: **0** (semua 46 yang menunggu bertanggal September).
- Setoran pajak & omzet luar: koleksinya masih kosong. "Omzet di luar sistem Agustus: belum diisi".
- Denyut perangkat & antrean: tidak ada di cadangan (`perangkatStatus` tidak diunduh). Hanya bisa dibaca di layar sesudah dibangun.
- Upah: `biayaBulanan/2026-08` tidak punya baris gaji sistem baru, dan `absenKaryawan` hanya ada untuk September. Hari kerja Agustus mungkin
  memang belum tercatat di sistem baru → **K5**.
- Titik kas: 23 Sep. `kasPada` untuk tanggal sebelum titik bernilai **"tidak bisa dihitung"**, jadi kas akhir Agustus sudah tidak terbaca hari
  ini, sebelum ada kunci (R3).

## 9. Risiko & yang belum terverifikasi

- **R1 [BELUM TERVERIFIKASI]** Semua kutipan di §1 dari halaman referensi resmi. Perilaku sungguhan (misalnya apakah `get()` yang sama di satu
  kiriman di-cache) hanya bisa dipastikan di Rules Playground / proyek uji. Playground ★ v4 belum ditulis.
- **R2 [ASUMSI]** WIB tanpa musim panas = UTC+7 tetap (25200000 ms).
- **R3** Kas bulan terkunci sudah tidak terbaca sekarang: mesin beku hanya punya **satu** titik kas yang maju tiap tutup hari. Laporan bank
  "final" untuk bulan lampau memuat kas *tidak bisa dihitung*, kecuali angkanya dipotret saat mengunci (misalnya di `riwayat` dokumen kunci;
  bukan dokumen yang dibaca mesin). Belum diputuskan.
- **R4** Pratinjau §8 dihitung dengan rumus sederhana di luar mesin (penjualan berlaku = tidak dikoreksi & tidak dibatalkan). Angka di layar
  nanti dihitung ulang oleh mesin.
- **R5 [BELUM TERVERIFIKASI]** Apakah layar `index.html` tetap menggambar perubahan yang tertahan di antrean tunda (memori: "polaritas
  masihTertunda beda per jalur"). Kalau ya, owner melihat koreksi bulan terkunci seolah tersimpan.
- **R6** Tutup buku lama (`index.html`) menulis saldo pembuka **dulu** (langkah 2), lalu menghapus dokumen satu per satu (langkah 3). Hapus
  berhenti di dokumen bulan terkunci pertama, sehingga saldo pembuka dan sisa dokumen lama hidup bersamaan dan stok/piutang terhitung dua kali. Di
  sistem baru urutannya sama (pembuka dulu, arsip belakangan), tapi pembukanya ditolak lebih dulu kalau ada piutang bertanggal bulan terkunci.
