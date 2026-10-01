# Peta hak akses — putaran 23, Tahap 0

Dasar `firestore.rules` v3. **Rules yang tidak bisa ditelusuri ke satu baris peta ini = cacat.** Lapisan berikutnya: v4 = kunci periode
(`docs/peta-kunci-periode.md`), **v5 = §9 (putaran 39, karyawan menuang & mengecek wadah literan)**.
Disusun dari KODE di `main` ad8baea (24 Sep 2026), bukan dari ingatan:

- inventaris tulis & baca: `python3 alat-uji/peta_akses.py` (tulis) dan `--baca` (baca per layar, graf panggilan fungsi);
- tulisan tiap tindakan bukan-owner dibaca tangan dari fungsi `susun*`-nya (baris & kolom disebut);
- ukuran kiriman diukur dari cadangan toko terbaru (24 Sep 00.34), tanpa menyebut isi.

Keputusan owner 24 Sep yang berlaku di atas teks prompt: pendaftaran mandiri mati dan akun tanpa `aksesAkun` aktif = nol akses (kecuali `permintaanAkses` miliknya);
jalur kasir dipersempit ke email kasir@; update pendamping saat jual boleh bila dibatasi per kolom dan tidak mengubah uang/berat tercatat;
access call dianggap TANPA cache; satu baris jejak per kiriman bukan-owner yang memuat daftar semua dokumennya; yang login 1–2 bulan ke depan hanya owner.

## 1 · Tindakan SS2 → fungsi → tulisan

Kisi `SS_TINDAKAN` (13) × hak bawaan `SS_HAK_BAWAAN`. `sendiri` = boleh sendiri, `owner` = minta owner, `tidak` = tidak boleh.
Server putaran ini menegakkan **baca & catat baru**. `owner`/`tidak` tertutup bagi bukan-owner (tombol mati + kalimat sebabnya).
Audit 39b no. 22: penjaga penulis pusat (`periksaKiriman` → `tindakanKiriman`) menegakkan kisi untuk TIAP kiriman, bukan cuma tombol — hak yang diputar owner
langsung berlaku di perangkat. Rules tidak membaca kisi (tanpa `get()` ke `aturanToko/peran`); yang ditegakkan server tetap kolom kanan.

| Tindakan | ben | karyawan | Fungsi | Koleksi · operasi (per kiriman) | Server putaran ini |
|---|---|---|---|---|---|
| jualTunai | sendiri | sendiri | `simpanNota` → `susunNotaDokumen`; lalu `susunStrukKeluar` | `penjualan` create (1 per baris) · `stokBahanLiteran` create `tipe:'pakai'` (literan berkantong, id = baris+1) · `stokBahanKemasan`/`stokBahanLiteran` create `tipe:'pakai'` (baris wadah & repack, id+1) · `pesanan` **update** (kalau keranjang dari pesanan) · `strukKeluar` create (kiriman terpisah) | BUKA untuk ben & karyawan |
| jualBon | sendiri | owner | sama + `piutangMutasi` create `tipe:'bayar'` (bayar sebagian di tempat) | seperti jualTunai + 1 | BUKA untuk ben; karyawan tertutup |
| nego | owner | tidak | harga di bawah jatah (persetujuan) — nego baris (`negoSelisih` ≠ 0) & potongan nota (`potonganTransaksi`) | `penjualan` create (kolom itu) | tertutup di perangkat (penjaga `periksaKiriman` + tombol, audit 39b no. 22); rules belum menolak kolomnya |
| terimaBon | sendiri | sendiri | `susunBayarBon` (bon-logika) | `piutangMutasi` create `tipe:'bayar'` | BUKA |
| hitungLaci | sendiri | tidak | `susunTutup` (tutup-hari-logika) | `pengaturan/titikKas` **timpa** (laci, rekening, amplop, brankas) · `amplopLaba`/`setoranKas`/`modalOwner`/`pindahUang`/`pengeluaranHarian` ber-id per tanggal (tutup ulang = **timpa**) · `penyesuaianStok`, `pengeluaranHarian` **hapus** | **TERTUTUP** — lihat §6 |
| uangKeluar | owner | tidak | `susunKeluar` | `pengeluaranHarian`, `kasbonMutasi` | tertutup |
| adukan | sendiri | sendiri | `susunSimpanAdukan` | `produksiKemasan` create (1 per hasil) · `stokBahanKemasan` create `tipe:'pakai'` (kantong per hasil, id+1) | BUKA |
| kedatangan | sendiri | sendiri | `susunSimpanMasuk` | `batchMasuk` create — **wajib `hargaPerKg`**; `caraBayar:'tunai'` = uang keluar di buku kas | **TERTUTUP** — lihat §6 |
| hargaBeli | tidak | tidak | `susunKoreksiHpp`, katalog | `batchMasuk`, `koreksiHpp`, katalog | tertutup |
| koreksi | owner | tidak | `susunPembatalan`, `susunKoreksiAdukan`, karcis | update/hapus | tertutup |
| hapus | tidak | tidak | `susunHapus*` | hapus | tertutup |
| pelangganBaru | sendiri | sendiri | `susunOrangBaru` | `pelangganCatatan` create (id = kunci nama; ditolak kalau sudah ada) | BUKA |
| atur | tidak | tidak | `susunAtur*` | `aturanToko` | tertutup |

Tulisan sistem untuk semua akun bukan-owner yang aktif: `logAktivitas` create (SATU baris per kiriman, memuat daftar dokumen) ·
`perangkatStatus` create/update dokumen perangkatnya sendiri (denyut) · `permintaanAkses/{uid}` create (hanya akun yang belum punya `aksesAkun`).

## 2 · Tindakan di luar kisi SS2 = owner saja (putaran ini)

Kode menulis lewat fungsi-fungsi ini, tapi kisi SS2 tidak punya barisnya. Bukan-owner tidak mendapat jalurnya di rules; tombolnya mati
dengan kalimat "Perlu persetujuan owner — alurnya menyusul". Yang berdampak ke pekerjaan harian staf ditandai ◆ (usul masuk kisi di putaran tablet).

- Jual: ◆ isi ulang / takar wadah literan (`susunTakarWadah`, `susunIsiUlangWadah`), ◆ retur & tukar (`susunRetur`, `susunReturTanpaNota`, `susunPenggantiTercatat`), ◆ pesanan baru/antar/batal (`susunPesanan*`), rak wadah (`susunRak`), rinci karcis (`susunRinciDokumen`, `susunUrungRinci`, `susunPerbaikanKarcis`), urungkan nota (`susunPembatalan`), setelan struk & harga wadah.
- Pelanggan: ubah kartu/ciri (`susunSimpanKartu` — upsert), benang titipan (`susunTitip*`, `susunBuangTitip`), tagih (`susunTagih`), hapus buku (`susunHapusBon`), satukan/bukan kembar/hapus nama, THR, "ini dia" (tempel nama ke nota), Bersihkan ciri.
- Stok: ◆ buka/samakan/kembalikan karung (`susunBukaKarung`, `susunSamakanKarung`, `susunKembalikanKarung`), cocokkan/opname, beli kantong, karantina, tempat simpan & tumpukan, HPP, hapus/koreksi adukan & kedatangan.
- Harga & Pemasok, Uang, Laporan, Menu › Sistem: semuanya owner.

## 3 · Baca per layar → daftar baca per peran

Graf panggilan dari berkas layar (+ modul layar yang diimpornya) ke fungsi logika & mesin, mengikuti tiap `ambil*()` / `cacheMentah()`.
Tabel lengkap per layar di Lampiran B. Bukan-owner (Tahap 3 tipis) hanya membuka **Jual, Pelanggan, Stok**, dan **Menu** (masuk sebagai · keluar · antrean · "ditolak server").

Daftar baca **ben & karyawan** = gabungan Jual (19) + Pelanggan (10) + Stok (20), dikurangi bagian owner:

- transaksi & orang: `penjualan`, `piutangMutasi`, `pelangganCatatan`, `pelangganTitip`, `pesanan`, `tagihPelanggan`, `strukKeluar`;
- stok: `batchMasuk`, `produksiKemasan`, `penyesuaianStok`, `penyesuaianKemasan`, `retur`, `karantina`, `stokBahanKemasan`, `stokBahanLiteran`, `wadahLiteran`, `pindahTempat`;
- harga jual: `katalogHargaKarung`, `katalogHargaKemasan`, `katalogHargaLiteran`, `hargaWadah`;
- setelan PER DOKUMEN (bukan seluruh koleksi — koleksinya bercampur tarif upah, NPWP, titik kas, PIN):
  `aturanToko/{struk, pelanggan, pelangganKembar, catatStok, kantong, tempat, peran, perangkat}` dan `pengaturan/tempatSimpan`;
- dirinya sendiri: `aksesAkun/{uid}`.

Dikurangi dengan sengaja: `koreksiHpp` & `aturanToko/hpp` (HPP = hargaBeli `tidak`), `thrPelanggan`, `cadanganCatatan` & `logAktivitas`
(dibaca lembar Bersihkan & Sistem — owner), `bukuHapus` (riwayat hapus — owner). Semua koleksi uang (`pengeluaranHarian`, `modalOwner`, `amplopLaba`,
`setoranKas`, `tutupHari`, `pindahUang`, `kasbonMutasi`, `biayaBulanan`, `slipUpah`, `absenKaryawan`, `utangOwnerMutasi`, `utangPemasokMutasi`, `pemasokCatatan`,
`titipanHarian`, `tutupBukuAcara`, `persetujuan`, `pengingat`, `pindahStok`, `tembusanStok`, `dokumenCetak`, `hargaPasar`, `hargaTerbit`, `pesananPemasok`) **tidak dibaca**.
Akibat untuk pendengar (Tahap 3): `aturanToko` & `pengaturan` untuk bukan-owner didengarkan **per dokumen**, bukan per koleksi — rules
tidak menyaring, jadi pendengar koleksi akan ditolak utuh.

## 4 · Peran × koleksi × operasi

`O` = owner (email, payung — sejak 23e payung TIDAK mencakup `aksesAkun` & `permintaanAkses`, yang bloknya membatasi owner; payung dihapus di putaran 25). `K` = kasir@ (jalur v2, disalin, dipersempit ke email). `B` = ben. `W` = karyawan.

| Koleksi | baca | create | update | delete |
|---|---|---|---|---|
| penjualan | O · B W | O · K · B W (W: `caraBayar` ≠ Kredit; tanpa `dibatalkan`/`dikoreksiOleh`) | O · K (tulis-ulang-sama) | O |
| piutangMutasi | O · B W | O · K · B W (`tipe:'bayar'` saja) | O · K (tulis-ulang-sama) | O |
| stokBahanLiteran | O · B W | O · K · B W (`tipe:'pakai'` saja) | O · K (tulis-ulang-sama) | O |
| stokBahanKemasan | O · B W | O · B W (`tipe:'pakai'` saja) | O | O |
| produksiKemasan | O · B W | O · B W | O | O |
| pelangganCatatan | O · B W | O · B W (dokumen belum ada) | O | O |
| strukKeluar | O · B W | O · B W | O | O |
| pesanan | O · B W | O | O · **B W: §5 baris 1** | O |
| logAktivitas | O | O · K · B W (1 per kiriman, `dokumen[]`) | O | O |
| perangkatStatus | O | O · K · B W (dokumen perangkatnya, §5 baris 2) | O · K · **B W: §5 baris 2** | O |
| aksesAkun/{uid} | O · pemiliknya | O (`peran` ∈ ben/karyawan; tak pernah owner) | O | O |
| permintaanAkses/{uid} | O | pemilik uid, selama `aksesAkun`-nya belum ada | — | O |
| aturanToko/{8 dok §3} | O · B W | O | O | O |
| pengaturan/tempatSimpan | O · B W | O | O | O |
| pengaturan/aksesKasir | O · K | O | O | O |
| ringkasanKasir | O · K | O | O | O |
| tagihPelanggan, pelangganTitip, batchMasuk, penyesuaianStok, penyesuaianKemasan, retur, karantina, wadahLiteran, pindahTempat, katalog ×3, hargaWadah | O · B W | O | O | O |
| 28 koleksi lain di `koleksi.js` (termasuk `pajakOmzetLuar`, `pajakSetoran` — putaran 24) + `arsipTahun` | O | O | O | O |

Hak bawaan ben & karyawan SAMA di tingkat koleksi, kecuali penjualan Kredit (jualBon: ben `sendiri`, karyawan `owner`).
Menambah peran nanti (mis. `kasir`) = menambah satu nama di daftar peran tiap koleksi yang boleh — tidak menulis ulang rules.

## 5 · Pengecualian UPDATE bukan-owner (2 baris)

| # | Dokumen | Kolom (`affectedKeys().hasOnly`) | Kenapa tidak bisa create |
|---|---|---|---|
| 1 | `pesanan/{id}` yang belum tuntas (`status` ∉ dibayar, batal) | `status` (→ `'dibayar'` saja), `riwayatStatus`, `trxIdJual`, `diubahOleh`, `diubahOlehUid`, `diubahPerangkat`, `diubahPada` — kolom pencipta (`oleh`, `olehUid`, `perangkat`, `lokasi`) tidak pernah ditambah bukan-owner; banyak dokumen lama tanpa `oleh` (cadangan toko: 2.481 dari 4.544 baris penjualan) | Pesanannya sudah ada (dicatat owner saat dipesan). Menjualnya harus menandai dokumen yang SAMA "dibayar" supaya keluar dari daftar pesanan menunggu — sistem lama (`majukanPesanan`) & layar pesanan membaca status di dokumen itu. Dokumen baru terpisah tidak dikenal keduanya. Tidak ada uang/berat yang berubah: nilai pesanan tidak disentuh. |
| 2 | `perangkatStatus/{idPerangkat}~{uid}` milik akun itu (`akunUid` = uid; owner tetap `{idPerangkat}`) — satu dokumen per perangkat × akun, tablet bergiliran tidak terkunci ke akun pertama (audit 39b no. 23) | `id`, `nama`, `akun`, `akunUid`, `aplikasi`, `pada`, `antrean`, `gagal`, `versi`, `pemegang`, `lokasi` | Denyut = satu dokumen per perangkat yang ditimpa tiap ≤ 5 menit (SS1 membaca "terakhir terlihat"). Create per denyut membuat koleksi tumbuh tanpa batas. Bukan data toko. |

Tidak ada DELETE untuk bukan-owner.

## 6 · Tertutup walau kisi bilang `sendiri`

- **hitungLaci** (ben `sendiri`). `susunTutup` menimpa `pengaturan/titikKas` (angka laci, rekening, amplop, brankas) dan memakai id per tanggal untuk amplop, setoran, modal, pindah uang, MDR — menutup ulang hari = **mengubah angka uang yang sudah tercatat**; juga menghapus `penyesuaianStok` & `pengeluaranHarian` lama. Tidak bisa dibatasi per kolom tanpa mengubah artinya. Syarat berhenti owner (poin 3) berlaku → tertutup untuk bukan-owner sampai alur persetujuan (mis. ben mencatat hitungan, owner yang menutup hari).
- **kedatangan** (ben & karyawan `sendiri`). `susunSimpanMasuk` menolak baris tanpa `hargaPerKg`, padahal `hargaBeli` = `tidak` untuk keduanya; dan kedatangan tunai langsung jadi uang keluar di buku kas. Rules tidak bisa menerima kedatangan sambil melarang harga di dokumen yang sama → tertutup sampai ada draf kedatangan tanpa harga yang dilengkapi owner.

## 7 · Access call (dianggap TANPA cache)

Tiap dokumen bukan-owner memeriksa `aksesAkun` sekali (1 `get()`); baris jejak kiriman juga 1. Jadi **access call = dokumen + 1**.
Batas Firebase: 10 per permintaan dokumen tunggal / tiap operasi, 20 per batch/transaksi. **Owner 24 Sep (putaran 23c): sisa 2 → paling
banyak 18.** Tabel ini dihasilkan `python3 alat-uji/peta_akses.py --kiriman` (CI): fungsi ASLI dijalankan dengan masukan terburuk di
batasnya, tiap kiriman lewat `periksaKiriman` asli; gagal bila ada yang > 18.

| Kiriman bukan-owner | Peran | Dokumen | Access call | Yang mencapainya |
|---|---|---|---|---|
| Nota | Ben | 16 | **17 / 20** | 7 baris literan berkantong · bayar sebagian (sisa jadi bon) · dari pesanan |
| Nota | karyawan | 15 | **16 / 20** | 7 baris literan berkantong · tunai/QRIS · dari pesanan (karyawan tidak bisa bon) |
| Adukan | Ben, karyawan | 16 | **17 / 20** | 8 baris hasil, semua berkantong |
| Isi ulang wadah (− / + takar) | Ben, karyawan | 17 | **18 / 20** | 5 merek, karung belakang baru semua (lahir + pindah + karung per merek, + takar + pindah); 6 merek = 20 → ditolak layar (39b no. 21) |
| Terima bon · pelanggan baru · struk | Ben, karyawan | 1 | 2 / 20 | satu dokumen |
| Denyut perangkat | Ben, karyawan | 1 | 1 / 20 | satu dokumen, tanpa jejak |

Dokumen per baris nota: karung utuh & kemasan 1; literan berkantong, repack dengan wadah ditanggung toko, wadah dijual 2.
Nota nyata terpanjang di cadangan toko: 7 baris (2.434 nota).

**Sebelum 23c** (batas 20 tanpa sisa, tanpa batas baris) yang tepat 20/20: nota **9 baris** berdokumen dua (mis. literan berkantong) + satu
tambahan — karyawan tunai dari pesanan, atau Ben dengan bayar sebagian. Ben 9 baris + bayar sebagian + pesanan = 21 → ditolak di perangkat.

Pagar berlapis:
1. **Batas per akun** (`akses.js`): 7 baris per nota (`alasanBatasBaris` di tambah-baris & saat dicatat), 8 hasil per adukan — kalimatnya
   "Satu nota paling banyak 7 baris untuk akun bukan-owner — batas sekali kirim ke server. Simpan nota ini dulu, sisanya jadi nota kedua."
   Audit 39b no. 21: baris ≠ dokumen (literan wadah campuran belum aktif = satu baris penjualan per merek asal; isian − / + takar = per karung belakang
   baru lahir + pindah + karung) → `batasDokumenKirim` 17 dokumen per nota (`alasanBatasDokumen`, di tambah-baris & saat dicatat) dan per isian takar
   (`susunTakarWadah`), kalimatnya kalimat nota / kalimat takar.
2. **Pagar umum penulis pusat**: kiriman bukan-owner apa pun yang > 18 access call ditolak di perangkat ("pecah jadi dua nota" bila ada penjualan,
   selain itu "catat dalam dua kali").
3. **Rules**: baris jejak bukan-owner paling banyak 17 dokumen (`stafJejak`).

Kiriman terbesar (17) **belum diuji di server** — gerbang tablet, proyek Firebase kedua di `docs/uji-rules-v3.md`.

## 8 · Gerbang tablet (owner 24 Sep, putaran 23c — syarat, BELUM dikerjakan)

Wajib lulus sebelum akun bukan-owner pertama disetujui (urutan lengkap: kepala `firestore.rules`, `docs/uji-rules-v3.md` bagian D).

- **Harga beli / modal tidak terkirim ke staf.** Kisi SS2 bilang `hargaBeli` = tidak, jadi server juga tidak boleh mengirimnya. Sensus nama
  kolom (cadangan toko 24 Sep, nama kolom saja) — koleksi yang dibaca staf (§3) dan membawa harga beli/modal:

  | Koleksi | Kolom harga beli / modal |
  |---|---|
  | `batchMasuk` | `merkList[].hargaPerKg`, `merkList[].subtotalHarga`, `biayaBongkar` |
  | `penjualan` | `hppTotalSaatJual`, `biayaKemasanLiteran` |
  | `produksiKemasan` | `hppPerUnit`, `modalPerUnit`, `hppSumberPerKgDipakai`, `biayaKemasan`, `sumberKemasanList[].hppPerUnitSaatDipakai` |
  | `penyesuaianStok` · `penyesuaianKemasan` | `hppPerKgSaatOpname` / `hppPerUnitSaatOpname`, `nilaiRp` |
  | `stokBahanKemasan` · `stokBahanLiteran` | `hargaTotal` (baris beli kantong) |

  Katalog harga, `hargaWadah`, `retur` = harga JUAL (boleh). **Masalah rancangannya:** `hppTotalSaatJual` di nota dihitung di perangkat
  penjual saat itu juga, dari harga beli (mesin laba yang dibekukan membacanya). Jadi ringkasan stok tanpa harga saja belum cukup; putaran
  tablet harus memutuskan siapa yang mengisi HPP nota staf (mis. perangkat owner melengkapinya sesudahnya) sebelum baca koleksi-koleksi
  di atas dicabut untuk staf.
- **Katalog kasir tanpa modal & tanpa daftar bon — WAJIB diputus sebelum akun staf pertama.** Sampai sekarang **modal** (`hppPerUnit`, `hppPerKg`,
  harga kantong `bahanLiteran.hargaPerPcs`) dan **daftar bon pelanggan** (nama + sisa) masih terkirim ke akun kasir@ lewat `ringkasanKasir/aktif`
  (keputusan owner 27 Sep: **tetap dulu**, pilihan A1 di `docs/peta-pindahan-terakhir.md` §6). Modal itu DIPAKAI kedua berkas kasir untuk mengisi modal
  nota (§1 peta itu), jadi memutusnya = memilih salah satu jalan di §6 A (dua dokumen / cabut modal) + siapa yang mengisi modal nota staf (butir di atas).
- **Denyut akun kasir dipersempit — WAJIB sebelum akun staf pertama.** Aturan server v4 membolehkan akun kasir@ menulis kolom denyut
  (`perangkatStatus`) APA SAJA (`allow create, update: if owner() || kasir() || …`, tanpa daftar kolom). Staf sudah dibatasi `affectedKeys().hasOnly`
  (§5 baris 2); kasir@ belum. Kolom yang kini dikirim kasir: `id, nama, akun, aplikasi, pada, antrean, gagal, versi` + `katalog` (kasir darurat, 25c) —
  daftar itulah batasnya.
- **PIN operator dicabut (25c, 27 Sep):** `pengaturan/aksesKasir` (dibaca kasir@) ditulis `/baru/` tanpa `pin` — nama + aktif/libur saja. PIN yang sudah
  tersimpan hilang dari server sesudah owner menekan "Cabut PIN operator" di Menu › Peran & persetujuan › Kasir & PIN.
- **Daftar arsip produk belum terbaca staf (putaran 27).** `aturanToko/produkArsip` tidak ada di `DOK_STAF.aturanToko` (`data/akses.js`) dan tidak
  ada di daftar dokumen `aturanToko` yang boleh dibaca staf di rules v4. Akun staf tidak mendengarkannya sama sekali, jadi tidak ada penolakan server
  dan Jual tidak macet: daftar arsip terbaca KOSONG (`arPeta()` = `{}`), nama yang diarsipkan owner tetap tampil di rak Jual staf (biasanya chip
  habis, stok 0). Diperbarui di putaran tablet: `produkArsip` masuk daftar baca staf di rules + `DOK_STAF`.
- **Cache Firestore dibersihkan saat Keluar** di perangkat bersama. Sampai itu ada, owner tidak masuk `/baru/` di tablet bersama.
- **Jaga CI kiriman ≤ 18** tetap hijau.
- **Email akun selalu huruf kecil** saat dibuat di Console.

Tambahan owner 24 Sep (sesudah 23d — dokumen saja, BELUM dikerjakan):

- **a · Titik kas lokal.** Beranda untuk akun bukan-owner TIDAK PERNAH menggambar kas dari penyimpanan perangkat (`miqbal_titik_kas_v1`, dibaca
  `ambilTitikKas` di `data/toko.js`). Uji: owner masuk → titik kas tersimpan di perangkat → Keluar → karyawan masuk → 0 angka kas di DOM.
  Kontrol positif wajib berbunyi (mis. penjaganya dilepas → angka kas muncul).
- **b · Catatan tertahan milik akun lain.** Layar owner menampilkan "N catatan milik <nama> tertahan di perangkat ini, terakhir <waktu>" (salinan
  antre, `data/antre-lokal.js`), beserta pilihan owner: tunggu akunnya masuk lagi, atau tulis ulang atas nama owner dengan `olehUid` asli dicatat
  di jejak.
- **c · Uji isian lewat kolom sungguhan.** Tambahkan data contoh minimal di Firebase palsu (`alat-uji/uji_layar_kunci.py`) supaya tiap layar yang
  punya isian punya minimal satu form yang diisi lewat kolom sungguhan (ketikan di DOM), bukan lewat keadaan layar seperti bagian ISIAN 23d.

## 9 · v5 (putaran 39, 29 Sep 2026) — karyawan menuang & mengecek wadah literan

Keputusan owner 29 Sep (`docs/peta-wadah-satu-buku.md` §8.1 no. 2–3): karyawan boleh mengisi ulang wadah dari akunnya sendiri, boleh menandai "untuk
dicocokkan" dengan namanya tercatat, dan mengecek tiap kotak saat tutup toko. Rules v5 diterbitkan owner lewat Console (pola putaran 25; kasus Playground
`docs/uji-rules-v5.md`). Jalan mundur = tempel `firestore.rules.v4`. Selain dua blok di bawah, v5 byte-sama dengan v4 (kunci periode, akun, kasir@).

### 9.1 Koleksi & tipe yang dibuka untuk `ben` dan `karyawan` (create saja; update & delete tetap owner)

| Koleksi | v4 | v5 | Fungsi rules | Penyusun yang menulisnya |
|---|---|---|---|---|
| `wadahLiteran` | owner saja | create tipe `takar` · `karung` · `karungIsi` · `cek` (`olehUid` = uid penulis; tanpa penilaian kunci periode — koleksi ini tidak bertanggal di `kunci-periode.js`) | `stafBuatWadah(['ben', 'karyawan'])` = `stafBuat()` + `tipe in [...]` | tiga ketukan `wbSusunIsiUlangTiga` (`karung`, `takar`) · panel − / + `susunTakarWadah` (`takar`, `karung` otomatis) · buka karung `susunBukaKarung` / `wbDokBukaKB` (`karung`) · samakan karung terbuka (`karungIsi`) · cek tutup toko `wbSusunCek` (`cek`; "dikosongkan" + `karung` sisihan lewat `wbSusunSisih`) |
| `batchMasuk` | owner saja | create **batch LAHIR BUKU 0 kg** saja: `lahirBuku == true`, `stokAwal == true`, `biayaBongkar == 0`, `pemasok == 'LAHIR BUKU'` (+ `olehUid`, `tglStaf('tanggal')`) | `stafBuatLahir(['ben', 'karyawan'])` | `wbDokLahir` — buku karung belakang / karung wadah yang lahir di kiriman isi ulang & cek |
| `produksiKemasan` | create (adukan, sejak v3) | **tidak berubah** — pindah buku (`wbDokPindah`: `dariTakar`, `jadiKarungUtuh`) menumpang jalur yang sudah ada | `stafBuat` + `tglStaf` | `wbDokBukaKB`, tuang, sisihkan, aktivasi (owner) |
| tetap owner | | `wadahLiteran` tipe `atur` (aturan wadah) & `isi` (titik samakan isi) · `batchMasuk` kedatangan sungguhan · `tutupHari` · `penyesuaianStok` (cocokkan) · `kembalikan karung` (menghapus catatan) | | |

Cek wadah disimpan sebagai `wadahLiteran` tipe `'cek'` (bukan di `tutupHari`) supaya karyawan mencatatnya sendiri saat tutup toko; `tutupHari` tetap
ditulis owner saat menutup hari. Peran ketiga nanti = tambah satu nama di kedua daftar (`stafBuatWadah` / `stafBuatLahir` di rules dan `BUAT_STAF` di
`akses.js`) — `periksa_rules.py` memastikan keduanya sama.

### 9.2 Tindakan SS2 ke-14: `isiUlang`

| Tindakan | ben | karyawan | Fungsi | Koleksi · operasi (per kiriman) | Server v5 |
|---|---|---|---|---|---|
| isiUlang · "Isi ulang & cek wadah literan" (modul Stok) | sendiri | sendiri | `wbSusunIsiUlangTiga`, `susunTakarWadah`, `susunBukaKarung`, `wbSusunCek` | `batchMasuk` create lahir 0 kg (≤ 1) · `produksiKemasan` create pindah buku (≤ 2) · `wadahLiteran` create (`karung` × n, `takar`, `cek`) | **BUKA** (`SERVER_BUKA.isiUlang = ['ben', 'karyawan']`) |

`SS_TINDAKAN` jadi 14 baris, `SS_HAK_BAWAAN` `sendiri` untuk keduanya (owner boleh memutarnya di SS2). Kalimat penolakan: `TINDAKAN_DARI.wadahLiteran =
'isiUlang'` → "isi ulang & cek wadah literan"; tipe `atur` / `isi` yang salah kirim jatuh ke kalimat tindakan `atur`, batch berisi kg ke kalimat
`kedatangan`. Tabel §1 (13 tindakan, v3) tidak ditulis ulang; baris ini pelengkapnya.

### 9.3 Penjaga perangkat = rules (kiriman yang pasti ditolak server tidak pernah dikirim)

- `akses.js`: `BUAT_STAF.wadahLiteran` & `BUAT_STAF.batchMasuk` = `['ben', 'karyawan']`; `TIPE_WADAH_STAF` = daftar `stafBuatWadah`; `batchLahir(d)` =
  syarat `stafBuatLahir` **ditambah** `merkList` tanpa `totalKg` / `subtotalHarga`. Yang terakhir hanya dijaga perangkat: rules v5 tidak membaca isi
  `merkList` (batas yang diketahui — kasus Playground V16 di `docs/uji-rules-v5.md`; batch bertanda LAHIR BUKU tetap 0 kg karena penyusunnya
  `wbDokLahir` dan penjaga perangkat, bukan karena server).
- `periksa_rules.py`: `FUNGSI_JUJUR` + `stafBuatWadah`, `stafBuatLahir` (keduanya lewat `stafBuat()` → `jujur()`); daftar peran di kedua blok = `BUAT_STAF`.
- `peta_akses.py --kiriman`: mengukur kiriman isi ulang & cek (9.4) dan menuntut tiga kiriman terlarang **dilewati di perangkat**: aturan wadah (`atur`),
  titik samakan isi (`isi`), batch lahir berisi kg; dua kontrol baru ("karyawan boleh menulis aturan wadah", "karyawan boleh menulis kedatangan
  sungguhan sebagai batch lahir").
- `uji_akses_baru.py` / `uji_menu_baru.py`: 14 tindakan; sel `sendiri` yang ditutup server tetap nol (isiUlang dibuka, jadi tidak ada "tertutup server" baru).
- Layar (putaran 39): tombol yang tidak boleh untuk akun ini MATI dengan kalimat (`tombolMati` / `data-kal`), bukan hilang — kartu Aktivasi & panel
  wadah di Stok menerima akun dari layar (`opsi.akun`, `041b9c2`), panel wadah di Jual, lembar Cek wadah di Jual, kartu Cek wadah K5. Aktivasi per
  wadah = owner (`tombolLuarKisi`); isi ulang & cek = kisi `isiUlang`.

### 9.4 Access call terukur (CI `peta_akses.py --kiriman`; batas 18 = 20 − sisa 2)

| Kiriman bukan-owner | Peran | Dokumen | Access call | Isinya |
|---|---|---|---|---|
| Isi ulang **½ karung** dari tumpukan (karung belakang belum berbuku) | ben, karyawan | 5 | **6 / 20** | batch lahir + pindah merek → karung belakang + 1 `karung` + `takar` + pindah karung belakang → wadah + jejak |
| Isi ulang **kg** dari karung yang sudah terbuka | ben, karyawan | 2 | 3 / 20 | `takar` + pindah + jejak |
| Cek tutup toko **dikosongkan** | ben, karyawan | ≤ 4 | ≤ 5 / 20 | lahir karung wadah (bila belum) + pindah + `karung` sisihan + `cek` + jejak |
| Cek **sesuai** / **lupa isi ulang** | ben, karyawan | 1 | 2 / 20 | `cek` + jejak |

Keempat baris diukur `peta_akses.py --kiriman` di bawah satu jenis "isi ulang wadah"; tabel CI memajang yang terburuk = ½ karung **6 / 20** (keluaran
29 Sep: `isi ulang wadah | ben · karyawan | 5 | 6 / 20`). Jumlah dokumen tetap per tindakan (tidak ada perulangan yang membesar): takaran
"1 karung" paling banyak membuka 1 karung (`n = ceil((kg − buku karung belakang) ÷ berat)`). Panel − / + takar dengan **beberapa merek sumber** menulis
[lahir?, pindah, `karung`…] per merek — belum diukur untuk akun staf di `--kiriman` (hari ini panel itu dipakai owner; tiga ketukan satu merek).

### 9.5 Gerbang tablet (§8) tidak berubah

Rules v5 tidak membuka akun staf pertama: semua butir §8 tetap wajib sebelum akun bukan-owner disetujui. Sampai ada akun staf, dokumen isi ulang &
cek ditulis akun owner (seperti 27 catatan takar di cadangan 29 Sep). Bila v4 ditempel kembali, kiriman isi ulang / cek dari akun karyawan ditolak
server dan masuk daftar ditolak (`antre-lokal.js`), tidak hilang diam.

## Lampiran A · Inventaris tulis (`python3 alat-uji/peta_akses.py`)

| berkas | fungsi | koleksi · bentuk |
|---|---|---|
| belanja | `susunAturBelanja` | aturanToko buat? |
| belanja | `susunPesanan` | pesananPemasok buat? |
| belanja | `susunUbahPesanan` | pesananPemasok buat? |
| bon | `susunBayarBon` | piutangMutasi buat? |
| bon | `susunHapusBon` | piutangMutasi buat? |
| bon | `susunTagih` | tagihPelanggan buat |
| bon-pemasok | `susunAturBon` | aturanToko buat? |
| bon-pemasok | `susunBayar` | pengeluaranHarian buat · utangPemasokMutasi buat? |
| bon-pemasok | `susunBonLama` | utangPemasokMutasi buat? |
| bon-pemasok | `susunKartu` | pemasokCatatan buat? |
| bon-pemasok | `susunUrungBayar` | pengeluaranHarian hapus · utangPemasokMutasi hapus |
| harga | `susunAturHarga` | aturanToko buat? |
| harga | `susunHapusPasar` | hargaPasar hapus |
| harga | `susunKalimatDraf` | katalogHargaKarung buat? · katalogHargaKemasan buat? · katalogHargaLiteran buat? |
| harga | `susunLabelSelesai` | aturanToko buat? |
| harga | `susunPakaiUsul` | katalogHargaKarung buat? · katalogHargaKemasan buat? · katalogHargaLiteran buat? |
| harga | `susunSengaja` | aturanToko buat? · katalogHargaKarung buat? · katalogHargaKemasan buat? · katalogHargaLiteran buat? |
| harga | `susunTerbit` | aturanToko buat? · hargaTerbit buat · katalogHargaKarung buat? · katalogHargaKemasan buat? · katalogHargaLiteran buat? |
| harga | `susunUbah` | hargaPasar buat? · katalogHargaKarung buat? · katalogHargaKemasan buat? · katalogHargaLiteran buat? |
| harga | `susunUsulSemua` | katalogHargaKarung buat? · katalogHargaKemasan buat? · katalogHargaLiteran buat? |
| jual | `simpanNota` | karantina buat? · penjualan buat? · pesanan buat? · piutangMutasi buat? · retur buat? · stokBahanKemasan buat/buat? · stokBahanLiteran buat/buat? |
| jual | `susunAturWadah` | wadahLiteran buat |
| jual | `susunBukaKarung` | wadahLiteran buat? |
| jual | `susunIsiUlangWadah` | wadahLiteran buat |
| jual | `susunKembalikanKarung` | wadahLiteran buat?/hapus |
| jual | `susunNotaDokumen` | karantina buat? · penjualan buat? · pesanan buat? · piutangMutasi buat? · retur buat? · stokBahanKemasan buat/buat? · stokBahanLiteran buat/buat? |
| jual | `susunPembatalan` | karantina hapus · penjualan ubah · pesanan buat? · piutangMutasi hapus · retur hapus · stokBahanKemasan buat?/hapus · stokBahanLiteran buat?/hapus |
| jual | `susunPesananAntar` | pesanan buat? |
| jual | `susunPesananBaru` | pesanan buat? |
| jual | `susunPesananBatal` | pesanan buat? |
| jual | `susunRak` | stokBahanKemasan buat? · stokBahanLiteran buat? |
| jual | `susunSamakanKarung` | wadahLiteran buat? |
| jual | `susunTakarWadah` | produksiKemasan buat? · wadahLiteran buat? |
| karcis | `susunPerbaikanKarcis` | penjualan buat? |
| karcis | `susunRinciDokumen` | penjualan buat? · stokBahanKemasan buat? · stokBahanLiteran buat? |
| karcis | `susunUrungRinci` | penjualan buat?/ubah · stokBahanKemasan buat?/hapus · stokBahanLiteran buat?/hapus |
| laporan | `susunAturDokumen` | aturanToko buat? |
| laporan | `susunAturLaporan` | aturanToko buat? |
| laporan | `susunAturRekap` | aturanToko buat? |
| laporan | `susunCetakan` | dokumenCetak buat |
| laporan | `susunIdentitas` | aturanToko buat? |
| laporan | `susunTandaLapor` | aturanToko buat? |
| pajak | `susunHapusOmzetLuar` | pajakOmzetLuar hapus |
| pajak | `susunHapusSetoran` | pajakSetoran hapus |
| pajak | `susunOmzetLuar` | pajakOmzetLuar buat? |
| pajak | `susunPakaiAturan` | aturanToko buat? |
| pajak | `susunProfilPajak` | aturanToko buat? |
| pajak | `susunSetoran` | pajakSetoran buat? |
| pelanggan | `susunAturPelanggan` | aturanToko buat? |
| pelanggan | `susunBeriThr` | thrPelanggan buat? |
| pelanggan | `susunBersihkanCiri` | aturanToko hapus/kolom · pelangganCatatan hapus/kolom |
| pelanggan | `susunBuangTitip` | pelangganTitip hapus |
| pelanggan | `susunBukanKembar` | aturanToko buat? |
| pelanggan | `susunGabung` | pelangganCatatan buat?/hapus · pelangganTitip hapus/ubah · penjualan ubah · pesanan ubah · piutangMutasi ubah · tagihPelanggan ubah · thrPelanggan ubah |
| pelanggan | `susunHapusNama` | pelangganCatatan hapus · pelangganTitip hapus · penjualan ubah |
| pelanggan | `susunHapusThr` | thrPelanggan hapus |
| pelanggan | `susunIniDia` | penjualan ubah |
| pelanggan | `susunOrangBaru` | pelangganCatatan buat? |
| pelanggan | `susunSerahThr` | thrPelanggan ubah |
| pelanggan | `susunSimpanKartu` | pelangganCatatan buat? |
| pelanggan | `susunTitip` | pelangganTitip buat? |
| pelanggan | `susunTitipLagi` | pelangganTitip buat? |
| pelanggan | `susunUsulThr` | thrPelanggan buat? |
| retur | `susunPenggantiTercatat` | retur ubah |
| retur | `susunRetur` | karantina buat? · retur buat? |
| retur | `susunReturTanpaNota` | karantina buat? · retur buat? |
| sistem | `susunAturSistem` | aturanToko buat? |
| sistem | `susunCatatCadangan` | cadanganCatatan buat |
| sistem | `susunDaftarkan` | aksesAkun buat? · permintaanAkses hapus |
| sistem | `susunJadikanUtama` | aturanToko buat? |
| sistem | `susunKePengingat` | aturanToko buat? |
| sistem | `susunPindahStok` | pindahStok buat? |
| sistem | `susunPutarHak` | aturanToko buat? |
| sistem | `susunPutusPersetujuan` | persetujuan ubah |
| sistem | `susunSaklarPengingat` | aturanToko buat? |
| sistem | `susunSetujuiKecil` | persetujuan ubah |
| sistem | `susunTolakAkses` | permintaanAkses hapus |
| sistem | `susunUbahAkun` | aksesAkun buat? |
| stok-adukan | `susunHapusAdukan` | bukuHapus buat · produksiKemasan buat?/hapus · stokBahanKemasan hapus |
| stok-adukan | `susunKoreksiAdukan` | produksiKemasan buat?/ubah |
| stok-adukan | `susunSimpanAdukan` | produksiKemasan buat? · stokBahanKemasan buat |
| stok-catat | `susunAturCatat` | aturanToko buat? |
| stok-catat | `susunCocok` | stokBahanKemasan buat? · stokBahanLiteran buat? |
| stok-catat | `susunHapusKedatangan` | batchMasuk buat?/hapus · bukuHapus buat · produksiKemasan hapus |
| stok-catat | `susunSimpanCocok` | penyesuaianKemasan buat · penyesuaianStok buat · stokBahanKemasan buat? · stokBahanLiteran buat? |
| stok-catat | `susunSimpanMasuk` | batchMasuk buat? |
| stok-hpp | `susunAturHpp` | aturanToko buat? |
| stok-hpp | `susunKoreksiHpp` | batchMasuk buat? · koreksiHpp buat |
| stok-hpp | `susunKoreksiMassal` | batchMasuk buat? · koreksiHpp buat |
| stok-kantong | `susunAturKantong` | aturanToko buat? |
| stok-kantong | `susunHapusBeli` | bukuHapus buat · stokBahanKemasan buat? · stokBahanLiteran buat? |
| stok-kantong | `susunSimpanBeli` | stokBahanKemasan buat? · stokBahanLiteran buat? |
| stok-karantina | `susunPutusKarantina` | karantina ubah · penyesuaianStok buat · produksiKemasan buat · retur ubah |
| stok-tempat | `susunAturTempat` | aturanToko buat? · pengaturan buat? · pindahTempat buat |
| stok-tempat | `susunGeserTumpukan` | aturanToko buat? |
| stok-tempat | `susunTempatBaru` | aturanToko buat? |
| struk | `susunAturStruk` | aturanToko buat? |
| struk | `susunStrukKeluar` | strukKeluar buat |
| tutup-buku | `susunAturBuku` | aturanToko buat? |
| tutup-buku | `susunBatal` | pengaturan buat? · tutupBukuAcara ubah |
| tutup-buku | `susunKunci` | amplopLaba buat? · batchMasuk buat? · kasbonMutasi buat? · pengaturan buat? · piutangMutasi buat? · produksiKemasan buat? · stokBahanKemasan buat? · stokBahanLiteran buat? · tutupBukuAcara buat? · utangOwnerMutasi buat? · utangPemasokMutasi buat? |
| tutup-buku | `susunSelesai` | tutupBukuAcara ubah |
| tutup-hari | `susunAturTutup` | aturanToko buat? |
| tutup-hari | `susunTutup` | amplopLaba buat? · modalOwner buat? · pengaturan buat? · pengeluaranHarian buat?/hapus · penyesuaianStok buat/hapus · pindahUang buat? · setoranKas buat? · tutupHari buat? |
| uang | `susunAturKeluar` | aturanToko buat? |
| uang | `susunAturPindah` | aturanToko buat? |
| uang | `susunBayarTagihan` | biayaBulanan buat? · pengeluaranHarian buat? |
| uang | `susunKeluar` | kasbonMutasi buat? · pengeluaranHarian buat? |
| uang | `susunPindah` | pengeluaranHarian buat?/hapus · pindahUang buat? |
| uang | `susunPutusTitipan` | pengeluaranHarian buat · persetujuan ubah |
| uang | `susunUrungPindah` | pengeluaranHarian hapus · pindahUang hapus |
| upah | `susunAbsen` | absenKaryawan buat? |
| upah | `susunAturUpah` | aturanToko buat? |
| upah | `susunBayarUpah` | biayaBulanan buat · kasbonMutasi buat · slipUpah buat? |
| upah | `susunBonus` | biayaBulanan buat? · slipUpah buat? |
| upah | `susunKaryawan` | aturanToko buat? |
| upah | `susunKasbonKaryawan` | kasbonMutasi buat? |
| wadah-jual | `susunAturHargaWadah` | hargaWadah buat? · stokBahanKemasan buat? · stokBahanLiteran buat? |
| wadah-jual | `susunRakWadah` | stokBahanKemasan buat? · stokBahanLiteran buat? |

119 fungsi yang menulis

## Lampiran B · Baca per layar (`python3 alat-uji/peta_akses.py --baca`)

| layar | koleksi dibaca (dari 56) |
|---|---|
| ringkasan | 23: aturanToko, batchMasuk, biayaBulanan, kasbonMutasi, modalOwner, pajakOmzetLuar, pajakSetoran, pengaturan, pengeluaranHarian, penjualan, penyesuaianKemasan, penyesuaianStok, perangkatStatus, pesanan, pindahStok, piutangMutasi, produksiKemasan, retur, setoranKas, stokBahanKemasan, stokBahanLiteran, utangOwnerMutasi, utangPemasokMutasi |
| stok | 20: aturanToko, batchMasuk, bukuHapus, karantina, katalogHargaKarung, katalogHargaKemasan, katalogHargaLiteran, koreksiHpp, pengaturan, penjualan, penyesuaianKemasan, penyesuaianStok, pesanan, pindahTempat, piutangMutasi, produksiKemasan, retur, stokBahanKemasan, stokBahanLiteran, wadahLiteran |
| jual | 19: aturanToko, batchMasuk, hargaWadah, katalogHargaKarung, katalogHargaKemasan, katalogHargaLiteran, pelangganCatatan, pelangganTitip, penjualan, penyesuaianKemasan, penyesuaianStok, pesanan, piutangMutasi, produksiKemasan, retur, stokBahanKemasan, stokBahanLiteran, strukKeluar, wadahLiteran |
| pelanggan | 10: aturanToko, cadanganCatatan, logAktivitas, pelangganCatatan, pelangganTitip, penjualan, pesanan, piutangMutasi, tagihPelanggan, thrPelanggan |
| harga | 28: aturanToko, batchMasuk, biayaBulanan, hargaPasar, hargaTerbit, kasbonMutasi, katalogHargaKarung, katalogHargaKemasan, katalogHargaLiteran, modalOwner, pelangganCatatan, pemasokCatatan, pengaturan, pengeluaranHarian, penjualan, penyesuaianKemasan, penyesuaianStok, pesanan, pesananPemasok, piutangMutasi, produksiKemasan, retur, setoranKas, stokBahanKemasan, stokBahanLiteran, tagihPelanggan, utangOwnerMutasi, utangPemasokMutasi |
| uang | 32: absenKaryawan, amplopLaba, aturanToko, batchMasuk, biayaBulanan, karantina, kasbonMutasi, katalogHargaKarung, modalOwner, pengaturan, pengeluaranHarian, penjualan, penyesuaianKemasan, penyesuaianStok, perangkatStatus, persetujuan, pesanan, pindahStok, pindahUang, piutangMutasi, produksiKemasan, retur, setoranKas, slipUpah, stokBahanKemasan, stokBahanLiteran, tembusanStok, tutupBukuAcara, tutupHari, utangOwnerMutasi, utangPemasokMutasi, wadahLiteran |
| laporan | 32: amplopLaba, aturanToko, batchMasuk, biayaBulanan, dokumenCetak, kasbonMutasi, modalOwner, pajakOmzetLuar, pajakSetoran, pelangganCatatan, pemasokCatatan, pengaturan, pengeluaranHarian, penjualan, penyesuaianKemasan, penyesuaianStok, perangkatStatus, pesanan, pindahStok, pindahUang, piutangMutasi, produksiKemasan, retur, setoranKas, slipUpah, stokBahanKemasan, stokBahanLiteran, tagihPelanggan, tutupHari, utangOwnerMutasi, utangPemasokMutasi, wadahLiteran |
| menu | 36: aksesAkun, amplopLaba, aturanToko, batchMasuk, biayaBulanan, cadanganCatatan, kasbonMutasi, katalogHargaKarung, katalogHargaKemasan, katalogHargaLiteran, logAktivitas, modalOwner, pelangganCatatan, pemasokCatatan, pengaturan, pengeluaranHarian, pengingat, penjualan, penyesuaianKemasan, penyesuaianStok, perangkatStatus, permintaanAkses, persetujuan, pesanan, pindahStok, pindahUang, piutangMutasi, produksiKemasan, retur, setoranKas, stokBahanKemasan, stokBahanLiteran, tagihPelanggan, utangOwnerMutasi, utangPemasokMutasi, wadahLiteran |

tidak dibaca layar mana pun: titipanHarian
