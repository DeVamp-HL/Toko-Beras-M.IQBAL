# Peta uang & karyawan — putaran 29, Tahap 0

**Status (28 Sep 2026): peta selesai, belum ada perubahan perilaku.** Syarat berhenti **tidak terpicu**: keempat bagian bisa dibangun
**tanpa jenis dokumen baru**, **tanpa mengubah arti field yang dibaca mesin**, dan **tanpa menyentuh 28 mesin beku**. Bagian 2 (upah per orang)
dibangun **di dalam dokumen bersama `aturanToko/upah` yang sudah ada** — tidak ada dokumen per orang, jadi syarat "dokumen per orang hanya
sesudah Tahap 0 disetujui" tidak tersentuh. Yang baru hanya **kolom** di dokumen yang sudah ada (§7), semuanya kolom yang mesin beku
abaikan; rules v4 tidak mengenumerasi kolom koleksi-koleksi ini, jadi rules dan `periksa_rules.py` **tidak berubah** (§6).

Sumber: kode di `main` befb7b0 (sesudah 28b), `firestore.rules` v4, dan cadangan toko 28 Sep 2026 (di `_privat/`, tidak masuk repo).
Angka di dokumen ini **jumlah catatan**, bukan rupiah. Nama orang tidak disebut.

## 1. Mesin laba dan `pengeluaranHarian` — field mana yang menentukan "biaya toko"

Satu-satunya pembaca uang keluar harian di mesin laba adalah `hitungLabaBersihRentang` (`baru/js/mesin/beku.js` 193):

```
harianRows = pengeluaranHarian.filter(kategori === 'toko' || kategori === 'tokoDompet')   → biaya toko (laba turun)
kategori === 'owner'                                                                      → tidak dibaca laba sama sekali (prive)
labaBersih = margin − (harianToko + jatahBulanan) − hapusBuku + susutStok
```

`hitungArusKasInti` (kas) membaca `'toko'` sebagai uang keluar dan `'owner'` sebagai prive dari laci; `'tokoDompet'` sengaja tidak punya baris kas
(toko berutang ke owner lewat `hitungUtangOwner`). Jadi **field yang menentukan arti = `kategori`**, tiga nilainya = empat arti K1 (toko dari
kantong toko · toko dari dompet owner · pribadi · bukan urusan toko = tidak ditulis). Tidak ada field kategori kedua.

Kolom lain yang sudah hidup di dokumen ini dan **diabaikan mesin** (dipakai layar `/baru/` saja): `dari` (laci/brankas/rekening — saldo per
tempat), `mdr` (potongan QRIS, dipisah di layar Laba), `dariBayarBon`, `dariPindah` (biaya admin bank menunjuk pembayarannya), `dariTutup`,
`alasanAman`, `dariPersetujuan`, `oleh`. Di cadangan 28 Sep: 135 catatan, 84 `toko`, 51 `owner`, 0 `tokoDompet`; 8 punya `dari`.

**Kesimpulan §1:** pemilahan "untuk toko / untuk karyawan" bisa ditambahkan sebagai **kolom baru `untuk`** tanpa mengubah arti: catatan
"untuk karyawan" tetap `kategori 'toko'` (atau `'tokoDompet'` bila dari dompet), jadi laba bersih **tidak berubah artinya** — yang bertambah
hanya pemilahannya di kartu laporan. Mesin, `index.html` (hanya-baca sejak 25b), dan `kasir*.html` (tidak membaca koleksi ini) tidak melihat
kolom itu. Catatan lama tanpa `untuk` = **belum dipilah** (bukan "toko" dan bukan "karyawan" — tiga keadaan kosong); di kartu ia dihitung di
biaya toko (arti yang selama ini ia punya) dan jumlahnya disebut. Di cadangan, 12 dari 84 catatan `toko` menyebut kopi/rokok/makan — itulah
yang selama ini "dinikmati karyawan" tapi tercampur di biaya toko.

## 2. Upah hari ini — satu aturan untuk semua, orangnya sudah per orang

`aturanToko/upah` (satu dokumen): `tarif` = **satu angka per hari untuk semua orang**; `orang[]` = daftar per orang `{nama, peran, status
aktif|berhenti, masuk, berhenti, mulaiHitung, catatan}` (putaran 21); `alasan[]` = alasan kasbon. Di cadangan: 2 orang aktif, satu `tarif`.

Hitungan (`upah-logika.js`): `hitungUpah(nama)` menyusuri hari sejak terakhir dibayar (`mulaiUpah`: slip terakhir → gaji lama sistem lama →
hari kerja pertama; dinaikkan `mulaiHitung`/`masuk`), membaca `absenKaryawan` (1 · 0,5 · 0 per tanggal), lalu `upah = penuh × tarif + setengah ×
tarif/2` — **tarif diambil sekali dari aturan bersama**, bukan per hari dan bukan per orang.

Yang ditulis saat gajian (`susunBayarUpah`), semuanya dokumen mesin lama + koleksi sistem baru yang sudah ada:

| Dokumen | Isi | Dibaca mesin? |
|---|---|---|
| `biayaBulanan/<bulan hari kerja>` (bulan terkunci → bulan bayar, K5 putaran 25) | baris `rincianGaji` berkunci `"Nama · tanggal bayar"` `{hari, gaji, orang, dari, sampai, sistemBaru, bonus?}`, `tanggalBayarGaji[kunci]`, `dariPos['gaji:'+kunci] = laci` | ya — laba: gaji KOTOR dibagi rata per hari sebulan (`jatahBiayaBulananHari`); kas: keluar di tanggal bayar |
| `kasbonMutasi` `{tipe bayar, caraBayar 'Dipotong upah'}` | potongan kasbon = kas MASUK sebesar potongan hari itu (kas bersih = yang diterima) | ya |
| `slipUpah` | jejak pembayaran: rentang, hitungan, `tarif`, potongan, teks slip | tidak (koleksi sistem baru) |

Bonus (putaran 22) ikut baris gaji bulan terakhir; bonus tanpa hari kerja = baris gaji hari 0.

**Kesimpulan §2:** "upah per orang dengan tanggal mulai berlaku" cukup dengan **daftar `upah[]` di tiap baris `orang[]`** dokumen bersama itu:
`{mulai: 'YYYY-MM-DD', satuan: 'hari'|'minggu'|'bulan', tarif}`. Tarif per hari suatu tanggal = entri terbaru yang `mulai ≤ tanggal`; tanpa
entri → `tarif` bersama (bawaan lama tetap berlaku). Hitungan per hari (bukan sekali per rentang) membuat gajian yang melintasi tanggal berlaku
membayar dua tarif dan slipnya merinci keduanya. Slip yang sudah tertulis adalah dokumen — riwayat tidak ditulis ulang. Rules: `aturanToko`
owner saja, tanpa enumerasi kolom → tidak berubah. `kunci-periode-logika.js` dan `tutup-buku-logika.js` memakai `aturUpah()`/`hitungUpah()`
hanya untuk daftar orang & upah belum dibayar — bentuk kembaliannya tetap.

[ASUMSI] Satuan minggu/bulan diturunkan ke **tarif per hari kalender**: minggu ÷ 7, bulan ÷ jumlah hari bulan itu (28–31), **dibulatkan ke rupiah
dulu** supaya slip bisa dihitung ulang pembaca (hari × tarif harian = angka yang tercetak). Hari tidak masuk tidak dibayar. Kalau owner memakai
pembagi lain (mis. 26 hari kerja), angkanya diatur di Karyawan sebagai tarif harian langsung.

## 3. Kasbon — cara dibedakan dari uang keluar, cara dipotong

Kasbon = `kasbonMutasi` (bukan `pengeluaranHarian`): `tipe 'ambil'` = kas keluar, laba tidak berubah (piutang ke karyawan; masuk neraca lewat
`hitungKasbon`). Owner: a.n. Owner + `owner: true`. Dua cara lunas: (a) `tipe 'bayar'` tunai = kas masuk; (b) potong upah — dua generasi:
`'Potong gaji'` (sistem lama; bukan kas; mesin mengalokasikannya ke baris gaji bernama polos yang masih punya ruang) dan `'Dipotong upah'`
(sistem baru; kas masuk hari bayar, baris gaji berkunci bertanggal kebal alokasi lama). Di cadangan: 25 ambil, 4 'Potong gaji', 1 bayar tunai.
**Tidak ada yang perlu diubah** untuk putaran ini; kasbon tetap di luar tiga tujuan uang keluar.

## 4. Bayar bon pemasok — field, kantong, cara mesin membacanya

`bon-pemasok-logika.js susunBayar` menulis `utangPemasokMutasi {id, tanggal, jam, tipe 'bayar', pemasok, nominal, catatan, bonId, bonTanggal,
dari, biayaAdmin?, adminNama?}`; mesin `hitungUtangPemasok` membaca `tipe`, `pemasok`, `nominal`, `bonId` (sisa bon = nilai − Σ bayar) dan
`hitungArusKasInti`/`daftarGerakanKas` membaca `tanggal` + `nominal` (kas keluar). `dari`, `biayaAdmin`, `adminNama` = kolom sistem baru,
diabaikan mesin. Di cadangan: 10 mutasi, **0 punya `dari`** (semua dari sistem lama); `aturanToko/bonPemasok.admin` = 3 pilihan biaya admin.

Biaya admin transfer = dokumen `pengeluaranHarian {kategori 'toko', keterangan 'Biaya admin <nama> — bayar bon …', nominal, dariBayarBon}` dalam
kiriman yang sama — persis yang diminta owner (dicatat terpisah, utang pemasok turun sebesar nominal bayar). Urung ≤ 90 detik menghapus keduanya.

**Dari kantong mana:** `saldoKantong()` (`uang-logika.js`) meletakkan mutasi utang pemasok di kantong `dari` (`ugPetaKantong` membaca
`utangPemasokMutasi[].dari`); tanpa `dari` → laci. **Cacat yang ketemu:** dokumen biaya admin dari bayar bon **tidak membawa `dari`** →
biaya adminnya dipotong dari **laci** di saldo per tempat, padahal uangnya keluar dari rekening (dokumen admin dari Pindah uang K4 dan MDR
Tutup hari sudah benar membawa `dari: 'rekening'`). Penjaga cukupnya pun hanya **total kas** (`kasPada`), bukan isi kantong yang dipilih
(`hitungBayar`: `n + admin > B.kas`). Di cadangan, titik kas 26 Sep mencatat **rekening 0** — jadi begitu kantong rekening dijaga, transfer akan
ditolak sampai isi rekening dicatat; `/baru/` belum punya tempat mencatat isi rekening (Tutup hari K5 hanya menghitung laci dan mengurangi MDR).

**Kesimpulan §4:** Bagian 4 = (a) pilihan **tunai (laci/brankas) atau transfer (rekening)** di lembar bayar — cukup dari `dari` (rekening = transfer),
tanpa kolom baru di `utangPemasokMutasi`; (b) dokumen admin membawa `dari: 'rekening'` + `untuk: 'toko'`; (c) penjaga isi kantong yang dipilih
(`saldoKantong`), dengan kalimat & tawaran **catat isi rekening** bila rekening belum pernah diisi; (d) riwayat/buku bon menyebut tunai/transfer +
admin. Mencatat isi rekening = dokumen `pengaturan/titikKas` (jenis yang sudah ada; arus kas berkop sudah menggambar titik yang disetel ulang
sebagai baris penyesuaian bernama).

## 5. Susut & selisih stok — di BAWAH laba kotor

`labaBersih = margin − biayaToko − hapusBuku + susutStok` (beku.js 221; `margin` = laba kotor). Susut (`barisSusutStok`, sejak 1 Sep 2026,
`nilaiRp` negatif = laba turun) dan hapus buku piutang sama-sama **di bawah laba kotor**, terpisah dari biaya toko. Layar Laba sudah
menggambarnya begitu (tangga "Dari kotor turun ke bersih"). → Kartu "Laba kotor → ke mana" **memuat** baris susut & selisih stok (dan hapus buku
bila ada), supaya menjumlah persis ke laba bersih mesin.

Susunan kartu per bulan (semua angka dari `hitungLabaBersihRentang` + `bayaranBiayaBulanan` yang sama, dipilah): laba kotor → biaya toko
(harian bukan-karyawan + jatah pos bulanan bukan gaji; di antaranya potongan QRIS `mdr`, biaya bank `dariBayarBon`/`dariPindah`, catatan belum
dipilah) → biaya karyawan (upah = jatah gaji KOTOR bulan itu; non-upah = harian `untuk 'karyawan'`) → hapus buku → susut & selisih (tanda apa
adanya) → **= laba bersih mesin** → ambil pribadi owner (`priveRentang`: prive laci + kasbon owner dialihkan + tarik modal) → sisa. Bulan terkunci /
sudah tutup buku = final (`lpFinal`). Bulan tanpa satu catatan pun disebut begitu, bukan nol.

## 6. Kunci bulan (putaran 25) — semua dokumen baru bertanggal hari ini

| Jalur | Dokumen | Tanggal | Bulan terkunci |
|---|---|---|---|
| Uang keluar (tiga tujuan) | `pengeluaranHarian` | hari ini | tidak tersentuh; salah catat = urung ≤ 90 dtk, sesudahnya catatan hari ini |
| Bayar bon transfer + admin | `utangPemasokMutasi` bayar + `pengeluaranHarian` | hari ini (`bonTanggal` boleh lama — ★D1/★D9 sudah lolos) | — |
| Catat isi rekening | `pengaturan/titikKas` | kemarin (atau hari ini bila titik sudah hari ini) | nilai BARU dinilai; tenggang 3 hari melindungi tanggal 1–3 |
| Upah per orang | `aturanToko/upah` | setelan, bukan koleksi bertanggal | — |
| Gajian | `biayaBulanan`, `kasbonMutasi`, `slipUpah` | seperti sekarang (K5: bulan terkunci → bulan bayar) | — |

Memilah ulang catatan lama (mengubah `untuk`) = update dokumen lama; di bulan terkunci ditolak rules. Putaran ini **tidak** membangun pemilah
ulang: catatan lama tinggal "belum dipilah" dan disebut jumlahnya.

Rules v4: blok `pengeluaranHarian`, `utangPemasokMutasi`, `aturanToko`, `slipUpah`, `pengaturan` tidak mengenumerasi kolom → **tidak ada
perubahan rules**, `periksa_rules.py` tetap, tidak ada kasus Playground ★ baru. `uji_isian_lokal.py`: kolom ketik baru menulis ke kunci keadaan
yang sudah dijaga (`aturK`, `karyawanDraf`, `bayar`, `pindah`).

## 7. Kolom baru (semua di dokumen yang sudah ada; mesin beku mengabaikannya)

| Dokumen | Kolom | Nilai | Alasan |
|---|---|---|---|
| `pengeluaranHarian` | `untuk` | `'toko'` · `'karyawan'` | pemilahan biaya toko tanpa mengubah `kategori` (arti laba tetap). Catatan `kategori 'owner'` tidak diberi `untuk` (bentuknya tetap sistem lama). Semua penulis otomatis (`mdr-`, admin K4/H2, tagihan tambahan, titipan tablet) menulis `'toko'` supaya tumpukan "belum dipilah" tidak bertambah |
| `pengeluaranHarian` (biaya admin bayar bon) | `dari` | `'rekening'` | perbaikan cacat §4 |
| `aturanToko/uangKeluar` | `perluKaryawan[]` | `{nama, biasa}` | tombol rutin tujuan karyawan; owner memindahkan tombol antar tujuan di Atur |
| `aturanToko/upah.orang[]` | `upah[]` | `[{mulai, satuan, tarif}]` | upah per orang bertanggal berlaku, di dokumen bersama |
| `slipUpah` | `rincianTarif[]`, `satuan` | `[{mulai, sampai, penuh, setengah, tarifHari, satuan, tarif}]` | slip merinci tiap tarif yang berlaku di rentangnya; `tarif` lama tetap diisi (tarif harian terakhir) |

Tidak ada koleksi baru. Tidak ada kolom baru di `utangPemasokMutasi`, `biayaBulanan`, `kasbonMutasi`.

## 8. Yang tidak disentuh

28 mesin beku (`beku.js`, `pembantu.js`) · `index.html`, `kasir*.html` · arti empat "arti uang keluar" · model stok wadah putaran 28 ·
`firestore.rules`.

## 9. Yang dibangun (28 Sep 2026, cabang `tulang-punggung/29-uang-karyawan`)

Semua sesuai §1–§8; tidak ada syarat berhenti yang terpicu. Penyimpangan kecil dari rencana: tidak ada.

| Bagian | Berkas | Uji |
|---|---|---|
| 1 · tiga tujuan | `uang-logika.js` (TUJUAN_KELUAR, `untuk`, perluKaryawan, `pilahHarian`, `priveRentang`), `uang.js` K1 & Atur (tombol "→"), `tutup-hari-logika.js` (MDR `untuk`) | `uji_uang_karyawan.py` |
| 2 · upah per orang | `upah-logika.js` (`tarifHariPada`, `upNilaiHari`, `rincianTarif`, slip, atur), `uang.js` K2 lembar Karyawan | `uji_upah_per_orang.py` |
| 3 · kartu ke mana | `laporan-logika.js` (`keManaLabaKotor`), `laporan.js` (Laba & Bulanan), `laporan.css` | `uji_uang_karyawan.py` |
| 4 · tunai/transfer | `bon-pemasok-logika.js` (`hitungBayar(d, kini, S)`, `caraDari`, admin `dari`+`untuk`), `harga.js` lembar bayar, `uang-logika.js` (`susunTitikRekening`), `uang.js` K4, `app.js` (keTujuan ke Harga) | `uji_bayar_pemasok_transfer.py` |

Uji lama yang disesuaikan (kontrol yang berubah teksnya, asersi kalimat, kolom `untuk` dikenal): `uji_uang_baru.py`, `uji_harga_baru.py`, `peta_akses.py` (OWNER_JALUR:
`susunTitikRekening`, 1 dokumen). Rules v4 & `periksa_rules.py` tidak berubah. Cadangan 28 Sep: 84 catatan toko semuanya "belum dipilah" (wajar — kolomnya baru lahir),
ASAP GLOBAL laba/inti/neraca/omzet tiap bulan byte-sama dengan `main`.
