# Uji rules v3 di server — putaran 23

`alat-uji/periksa_rules.py` memeriksa **bentuk** rules (statis, di CI). Berkas ini untuk **perilaku server**: yang benar-benar diizinkan
atau ditolak Firestore. Dua alat, keduanya dijalankan owner di Firebase Console — Claude Code tidak memegang sandi & tidak masuk Console.

1. **Rules Playground** (Console › Firestore › Rules › *Rules Playground*): menguji SATU operasi pada satu dokumen, dengan rules di editor
   (belum diterbitkan). Tidak bisa menguji batch.
2. **Proyek Firebase kedua** (khusus uji, gratis): tempat menguji kiriman nyata dari `/baru/`, termasuk batch terbesar. Emulator tidak dipasang
   (keputusan owner 24 Sep), jadi inilah satu-satunya uji batch di server.

**Gerbang (keputusan owner 24 Sep): SEBELUM akun bukan-owner pertama disetujui di proyek toko, bagian B wajib selesai & lulus.**

---

## A · Kasus Playground (jalankan di proyek UJI dulu, lalu yang bertanda ★ juga di proyek toko sebelum menempel v3)

Cara isi: *Simulation type* = get / create / update / delete · *Location* = jalur dokumen · *Authenticated* = on, *Provider* = password,
*Firebase UID* = uid akunnya, lalu di **Auth token payload** tambahkan `"email": "…"`. Untuk create/update isi *Build document* dengan kolom di tabel.
Kasus peran ben/karyawan butuh dokumen `aksesAkun/{uid}` yang SUDAH ADA (Playground membaca data sungguhan lewat `get()`).

| # | Akun | Operasi · jalur · isi | Wajib |
|---|---|---|---|
| ★1 | owner@ | get `/modalOwner/x` | LOLOS |
| ★2 | owner@ | delete `/penjualan/x` | LOLOS |
| ★3 | kasir@ | create `/penjualan/uji1` `{id:'uji1', hargaTotal: 1000}` | LOLOS |
| ★4 | kasir@ | create `/piutangMutasi/uji1` · `/stokBahanLiteran/uji1` · `/logAktivitas/uji1` | LOLOS (tiga-tiganya) |
| ★5 | kasir@ | get `/ringkasanKasir/x` · get `/pengaturan/aksesKasir` · create `/perangkatStatus/p1` | LOLOS |
| ★6 | kasir@ | get `/penjualan/x` · get `/pengaturan/keamanan` · create `/pengeluaranHarian/x` · delete `/penjualan/x` | DITOLAK (semua) |
| ★7 | akun tanpa `aksesAkun` (uid `baru1`, email lain) | get `/penjualan/x` · create `/penjualan/x` `{olehUid:'baru1'}` · get `/aturanToko/struk` | DITOLAK (semua) |
| ★8 | akun tanpa `aksesAkun` (uid `baru1`) | create `/permintaanAkses/baru1` `{uid:'baru1', email:'<email token, huruf kecil>', nama:'Uji', pada:'2026-09-24T00:00:00Z'}` | LOLOS |
| ★9 | akun tanpa `aksesAkun` (uid `baru1`) | create `/permintaanAkses/lain` (uid orang lain) · create `/permintaanAkses/baru1` dengan kolom tambahan `peran` | DITOLAK |
| ★10 | owner@ | create `/aksesAkun/u1` `{uid:'u1', peran:'owner', aktif:true}` | DITOLAK |
| 11 | owner@ | create `/aksesAkun/u1` `{uid:'u1', nama:'Uji', peran:'karyawan', aktif:true}` | LOLOS |
| 12 | ben (aktif) | get `/penjualan/x` · get `/aturanToko/struk` · get `/pengaturan/tempatSimpan` | LOLOS |
| 13 | ben (aktif) | get `/pengeluaranHarian/x` · get `/aturanToko/upah` · get `/pengaturan/titikKas` · get `/logAktivitas/x` | DITOLAK |
| 14 | ben (aktif) | create `/penjualan/j1` `{olehUid:'<uid ben>', caraBayar:'Kredit'}` | LOLOS |
| 15 | ben (aktif) | create `/penjualan/j2` `{olehUid:'<uid LAIN>'}` · create `/penjualan/j3` `{olehUid:'<uid ben>', dibatalkan:true}` | DITOLAK |
| 16 | ben (aktif) | create `/piutangMutasi/b1` `{olehUid, tipe:'bayar'}` → LOLOS · sama dengan `tipe:'hapusBuku'` → DITOLAK | sesuai |
| 17 | ben (aktif) | create `/stokBahanKemasan/k1` `{olehUid, tipe:'pakai'}` → LOLOS · `tipe:'beli'` → DITOLAK | sesuai |
| 18 | ben (aktif) | update `/pesanan/<yang status 'dipesan'>`: ubah `status:'dibayar'`, `riwayatStatus`, `trxIdJual`, `diubahOlehUid:'<uid ben>'` | LOLOS |
| 19 | ben (aktif) | update pesanan yang sama tapi ikut mengubah `nilai` / `namaPelanggan` · atau pesanan yang sudah `dibayar` | DITOLAK |
| 20 | ben (aktif) | create `/logAktivitas/l1` `{olehUid, dokumen:[{koleksi:'penjualan', id:'j1'}]}` → LOLOS · tanpa `dokumen` → DITOLAK | sesuai |
| 21 | ben (aktif) | delete `/penjualan/j1` · write `/aksesAkun/<uid ben>` `{peran:'karyawan'}` | DITOLAK |
| 22 | karyawan (aktif) | create `/penjualan/j4` `{olehUid, caraBayar:'Kredit'}` → DITOLAK · `caraBayar:'Tunai'` → LOLOS | sesuai |
| 23 | ben NONAKTIF (`aktif:false`) | get `/penjualan/x` · create `/penjualan/j5` `{olehUid}` | DITOLAK |
| 24 | ben (aktif) | create `/perangkatStatus/p9` `{id:'p9', akunUid:'<uid ben>', pada:'…'}` → LOLOS · dengan `akunUid` orang lain → DITOLAK | sesuai |

Satu saja yang meleset = **jangan tempel v3**; kirim nomornya ke Claude Code.

---

## B · Gerbang proyek Firebase kedua (batch & alur nyata)

Tujuannya: menjalankan transaksi terbesar tiap peran lewat `/baru/` sungguhan, di proyek yang BUKAN proyek toko. Data toko tidak disentuh.

1. **Buat proyek** (Console › Add project, paket gratis). Nyalakan *Authentication › Email/Password*; **matikan pendaftaran mandiri**
   (Settings › User actions). Buat *Firestore Database*.
2. **Buat akun uji** di Authentication › Add user: `owner@tokoberasmiqbal.web.app` (rules mengenali owner lewat email ini — di proyek uji
   akun ini terpisah dari proyek toko), satu akun untuk peran ben, satu untuk karyawan. Sandi bebas, cuma untuk proyek uji.
3. **Tempel rules v3** (`firestore.rules`) di proyek uji.
4. **Ambil config web** proyek uji (Project settings › Your apps › Web › `firebaseConfig`). Di perangkat yang dipakai menguji, buka
   `/baru/?pasangProyekUji=<config JSON>` — contoh: `/baru/?pasangProyekUji={"projectId":"uji-miqbal","apiKey":"…","appId":"…","authDomain":"uji-miqbal.firebaseapp.com"}`.
   Bilah merah **PROYEK UJI** muncul di setiap layar. Proyek toko ditolak sebagai proyek uji. **Kembali** = tombol "Kembali ke data toko"
   di bilah itu (atau `/baru/?lepasProyekUji=1`). Setelan ini hanya di perangkat itu.
5. **Isi data contoh sebagai owner** di `/baru/` proyek uji: Stok › Barang masuk (1 kedatangan, 1 nama beras), Harga › Katalog (terbitkan
   harga karung & literan nama itu), Stok › Kantong (beli kantong literan & 5 kg), Jual › pesanan baru untuk satu nama.
6. **Alur akun**: masuk sebagai akun ben → "Minta didaftarkan" → keluar → masuk owner → Menu › Sistem › Peran → Daftarkan sebagai Ben.
   Ulangi untuk karyawan. Nonaktifkan lalu aktifkan lagi satu akun (dua ketukan) sambil akun itu terbuka di perangkat lain — layarnya harus
   langsung tertutup.
7. **Kiriman terbesar tiap peran** (yang belum diuji di server; batas 20 access call):
   - karyawan: nota tunai **9 baris literan berkantong** dari pesanan yang ada (9 × 2 + pesanan = 19 dokumen + 1 jejak = **20**) → wajib masuk;
   - karyawan: nota Bon → wajib ditolak di perangkat ("Perlu persetujuan owner");
   - ben: nota Bon dibayar sebagian (baris + bayar sebagian) → wajib masuk;
   - ben & karyawan: terima bayar bon, adukan 2 hasil, pelanggan baru → wajib masuk;
   - ben: Stok › Barang masuk → wajib mati dengan kalimatnya; Menu tidak memajang angka uang;
   - owner: Menu › Sistem › Jejak menampilkan SATU baris per kiriman bukan-owner yang menyebut semua dokumennya.
8. **Ditolak server tidak hilang**: nonaktifkan akun karyawan saat perangkatnya OFFLINE, buat satu nota di perangkat itu, sambungkan lagi →
   kiriman itu tampil di Menu › Sistem › Perangkat › Antrean sebagai **ditolak server** (owner: tulis ulang atas nama owner / buang).
9. Semua lulus → **Kembali ke data toko**, lanjut ke C.

---

## C · Langkah pasang di proyek TOKO (sesudah A ★ & B lulus)

0. Pendaftaran mandiri MATI & daftar Users sudah diperiksa (owner, 24 Sep: sudah).
1. Tempel `firestore.rules` v3 di Console proyek toko.
2. **Buat SATU nota dari kasir darurat** (akun kasir@) dan pastikan nota itu masuk di layar Jual `/baru/` owner. Tidak masuk → langsung tempel
   `firestore.rules.v2` (jalan mundur) dan kabari Claude Code.
3. Buat akun orangnya di Authentication › Add user (email + sandi — owner yang memegang sandinya).
4. Orangnya masuk `/baru/` → "Minta didaftarkan"; owner menyetujui di Menu › Sistem › Peran.

**Mundur** = tempel `firestore.rules.v2` — hanya selama pendaftaran mandiri mati (v2 membuka jalur kasir untuk siapa pun yang login).
