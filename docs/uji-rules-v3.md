# Uji rules v3 di server — putaran 23

`alat-uji/periksa_rules.py` memeriksa **bentuk** rules (statis, di CI). Berkas ini untuk **perilaku server**: yang benar-benar diizinkan
atau ditolak Firestore. Dua alat, keduanya dijalankan owner di Firebase Console — Claude Code tidak memegang sandi & tidak masuk Console.

1. **Rules Playground** (Console › Firestore › Rules › *Rules Playground*): menguji SATU operasi pada satu dokumen, dengan rules di editor
   (belum diterbitkan). Tidak bisa menguji batch.
2. **Proyek Firebase kedua** (khusus uji, gratis): tempat menguji kiriman nyata dari `/baru/`, termasuk batch terbesar. Emulator tidak dipasang
   (keputusan owner 24 Sep), jadi inilah satu-satunya uji batch di server.

**Urutan dipecah dua (owner 24 Sep, putaran 23c):**

- **SEKARANG** — belum ada akun bukan-owner, yang masuk `/baru/` cuma owner: kasus ★ di Playground dengan v3 di editor proyek toko (A),
  tempel v3, satu nota kasir darurat masuk (C).
- **GERBANG TABLET** — wajib lulus SEBELUM akun bukan-owner pertama disetujui: proyek Firebase kedua (A 11–24 + B), harga beli tidak
  terkirim ke staf, cache dibersihkan saat Keluar, jaga CI ≤ 18 tetap hijau, lalu akun dibuat (email huruf kecil) & disetujui (D).

---

## A · Kasus Playground (★ = SEKARANG di editor proyek toko sebelum menempel v3; 11–24 = gerbang tablet, di proyek uji)

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
   akun ini terpisah dari proyek toko), satu akun untuk peran ben, satu untuk karyawan — email huruf kecil semua. Sandi bebas, cuma untuk proyek uji.
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
   - ben: nota **7 baris literan berkantong**, dibayar sebagian, dari pesanan yang ada (7 × 2 + bayar sebagian + pesanan = 16 dokumen + 1 jejak
     = **17**, terburuk yang mungkin — `python3 alat-uji/peta_akses.py --kiriman`) → wajib masuk;
   - karyawan: nota tunai 7 baris literan berkantong dari pesanan (15 dokumen + 1 = **16**) → wajib masuk; baris ke-8 → wajib ditolak di
     perangkat dengan kalimat "Satu nota paling banyak 7 baris untuk akun bukan-owner — batas sekali kirim ke server…";
   - karyawan: nota Bon → wajib ditolak di perangkat ("Perlu persetujuan owner");
   - ben/karyawan: adukan 8 hasil berkantong (**17**) → wajib masuk; hasil ke-9 → ditolak dengan kalimatnya;
   - ben & karyawan: terima bayar bon, adukan 2 hasil, pelanggan baru → wajib masuk;
   - ben: Stok › Barang masuk → wajib mati dengan kalimatnya; Menu tidak memajang angka uang;
   - owner: Menu › Sistem › Jejak menampilkan SATU baris per kiriman bukan-owner yang menyebut semua dokumennya.
8. **Ditolak server tidak hilang**: nonaktifkan akun karyawan saat perangkatnya OFFLINE, buat satu nota di perangkat itu, sambungkan lagi →
   kiriman itu tampil di Menu › Sistem › Perangkat › Antrean sebagai **ditolak server** (owner: tulis ulang atas nama owner / buang).
9. Semua lulus → **Kembali ke data toko**, lanjut ke D.

---

## C · SEKARANG di proyek TOKO (sesudah kasus ★ di A sesuai semua)

0. Pendaftaran mandiri MATI & daftar Users sudah diperiksa (owner, 24 Sep: sudah).
1. Tempel `firestore.rules` v3 di Console proyek toko.
2. **Buat SATU nota dari kasir darurat** (akun kasir@) dan pastikan nota itu masuk di layar Jual `/baru/` owner. Tidak masuk → langsung tempel
   `firestore.rules.v2` (jalan mundur) dan kabari Claude Code.

## D · GERBANG TABLET (semua lulus SEBELUM akun bukan-owner pertama disetujui)

1. Proyek Firebase kedua: kasus A 11–24 + seluruh B lulus.
2. **Harga beli / modal tidak terkirim ke Ben/karyawan.** Kisi SS2 bilang `hargaBeli` = tidak boleh, tapi tujuh koleksi yang dibaca staf
   membawanya (`batchMasuk`, `penjualan.hppTotalSaatJual`, `produksiKemasan`, `penyesuaianStok/Kemasan`, `stokBahanKemasan/Literan` —
   `docs/peta-hak-akses.md` §8). Layar tidak memajangnya, server tetap mengirimnya. Rancang ringkasan stok tanpa harga beli DAN siapa yang
   mengisi HPP nota staf, lalu cabut baca itu untuk staf. (Putaran tablet — belum dikerjakan.)
3. **Cache Firestore dibersihkan saat Keluar** di perangkat bersama. Sampai itu ada: owner tidak masuk `/baru/` di tablet bersama.
4. Jaga CI kiriman bukan-owner ≤ 18 access call tetap hijau (`alat-uji/peta_akses.py --kiriman`, terpasang putaran 23c).
5. Buat akun orangnya di Authentication › Add user — **email selalu huruf kecil semua** (rules permintaan akses membandingkan email di token
   dengan yang ditulis aplikasi, yang selalu huruf kecil). Owner yang memegang sandinya.
6. Orangnya masuk `/baru/` → "Minta didaftarkan"; owner menyetujui di Menu › Sistem › Peran.

**Mundur** = tempel `firestore.rules.v2` — hanya selama pendaftaran mandiri mati (v2 membuka jalur kasir untuk siapa pun yang login).
