# Notifikasi aplikasi tablet — langkah pasang (sekali)

Tujuannya: jawaban owner atas titipan, pesan, dan permintaan dari tablet (disetujui, ditolak + alasannya, dibaca + balasannya) muncul di **bilah notifikasi
tablet** walau aplikasi tablet ditutup — sama seperti notifikasi HP / Mac owner (`docs/notifikasi-hp.md`).

Kenapa perlu langkah sendiri: aplikasi tablet adalah cangkang Android, bukan peramban, jadi push peramban (yang dipakai HP & Mac) tidak ada di sana — dulu
kartunya menulis "Peramban ini tidak mendukung notifikasi push". Aplikasi tablet sekarang memakai **plugin push resmi Capacitor** (Firebase Cloud Messaging
untuk Android). Jalurnya: owner memutus permintaan (Uang › titipan, Menu › Toko ini › Peran & persetujuan › Persetujuan, atau lonceng) → **fungsi server** `kabarTablet` (folder
`functions/`) → Google → tablet yang menyalakan notifikasi (token di koleksi `notifPerangkat`, rules v17).

Saat aplikasi **terbuka**, kabar tetap lewat pita di atas layar, bunyi, lampu CPad, dan **lonceng** (tanpa langkah di bawah ini).

## Urutan (± 20 menit, semua dari peramban — Mac tidak perlu memasang apa pun)

1. **Daftarkan aplikasi Android di Firebase** — Console Firebase › ⚙ Project settings › tab **General** › bagian **Your apps** › **Add app** › ikon
   **Android**:
   - Android package name: `id.miqbal.tokoberas` (harus persis — sama dengan aplikasi tablet yang sudah terpasang)
   - App nickname: bebas, mis. `Tablet kasir`. SHA-1 **dikosongkan**.
   - **Register app** → **Download google-services.json** → langkah "Add Firebase SDK" dan seterusnya **dilewati** (Next / Continue to console) — itu sudah
     diurus pembangun APK.
2. **Simpan isi berkas itu di rahasia repo** — GitHub › repo › **Settings** › **Secrets and variables** › **Actions** › **New repository secret**:
   - Name: `GOOGLE_SERVICES_JSON`
   - Secret: buka `google-services.json` dengan TextEdit, pilih semua, salin, tempel **seluruhnya**.
   Berkas itu tidak masuk repo (repo publik). Isinya bukan sandi, tapi tetap disimpan sebagai rahasia supaya rapi.
3. **Terbitkan rules v17** — `docs/uji-rules-v17.md` (salin `firestore.rules`, Playground tiga kasus owner, Publish).
4. **Merge PR-nya.** Workflow **Bangun APK tablet kasir** jalan sendiri di main (berkas `apk/` berubah). Di halaman run-nya, ringkasan harus menulis
   **"Push tablet: berkas Firebase TERPASANG"**. Kalau menulis "TANPA berkas Firebase" (rahasia dibuat sesudah merge): Actions › Bangun APK tablet kasir ›
   **Run workflow** (cabang main) sekali lagi.
5. **Pasang APK baru di CPad** — unduh artefak `apk-tablet-kasir` dari run itu, pasang menimpa yang lama (kunci tanda tangan sama — data, akun tablet, dan
   setelan printer tetap). Pastikan antrean kosong dulu (Menu tablet, kartu "Catatan dari perangkat ini": "semua sudah sampai server").
6. **Pasang ulang fungsi server** — Cloud Shell (`console.cloud.google.com` › proyek toko › ikon `>_`), di folder yang sudah ada:

   ```bash
   cd Toko-Beras-M.IQBAL && git pull && bash functions/pasang.sh
   ```

   (Kalau foldernya sudah tidak ada: `git clone https://github.com/DeVamp-HL/Toko-Beras-M.IQBAL.git && cd Toko-Beras-M.IQBAL && bash functions/pasang.sh`.)
   Yang terpasang: `kabarOwner` (lama) + **`kabarTablet`** (baru). Bila ditolak "Eventarc Service Agent", tunggu ±2 menit lalu jalankan baris yang sama lagi.
7. **Nyalakan di tablet** — aplikasi tablet (akun tablet, orang siapa pun yang jaga) › **Menu** › kartu **Notifikasi di tablet ini** (di bawah "Catatan
   dari perangkat ini") › **Nyalakan notifikasi tablet** → Android bertanya izin notifikasi → **Izinkan**. Kartu berubah jadi "MENYALA di tablet ini
   sejak …". Token tersimpan atas nama AKUN tablet, jadi cukup sekali untuk semua orang yang jaga.

## Uji (5 menit)

1. Di tablet: kirim pesan ke owner (Menu › kartu "Uang keluar & pesan untuk owner"), lalu **tutup penuh** aplikasi tablet (geser dari daftar aplikasi terbuka).
2. Di HP owner: buka lonceng (pojok kanan atas layar mana pun) → tab **Obrolan** → pesan itu tampil (di tablet berubah ✓✓) → ketik balasan → kirim.
3. Di tablet: bunyi + notifikasi "Pesan dari owner" berisi balasan itu muncul di bilah notifikasi. Ketuk = aplikasi terbuka di Menu.

## Obrolan owner ↔ tablet (owner 23 Nov 2026: "seperti WhatsApp")

Ketuk **lonceng** (pojok kanan atas layar mana pun, Mac / HP / tablet) › tab **Obrolan**: satu utas owner ↔ tablet — gelembung kiri (lawan bicara) dan
kanan (sendiri), label hari, nama orang yang jaga di atas gelembung tablet, kotak ketik di bawah (paling banyak 500 huruf; di Mac Enter = kirim,
Shift+Enter = baris baru; di layar sentuh tombol kirim bulat). Tab **Kabar** berisi titipan uang, barang masuk, nego, usul harga, minta bon.

- **Owner menulis** → pesan owner (`persetujuan` bertindakan `pesanOwner`, status `terkirim`) → muncul di obrolan semua akun tablet, pita di atas layar
  tablet yang terbuka, dan bilah notifikasi tablet walau aplikasinya ditutup (fungsi server `kabarDariOwner`).
- **Tablet menulis** → pesan ke owner (tindakan `pesan`, sama dengan Menu › kartu pesan untuk owner) → lonceng owner berangka + notifikasi HP / Mac owner.
- **Centang di gelembung tablet**: ✓ = terkirim, ✓✓ = **dibaca owner**. Owner membuka tab Obrolan = semua pesan tablet yang menunggu ditandai dibaca
  (tanpa balasan) — tablet hanya melihat ✓✓, **tanpa** notifikasi "dibaca". Membaca di HP ikut membersihkan angka di Mac (keadaannya di server).
- Pesan owner tidak punya ✓✓: akun tablet tidak boleh mengubah dokumen persetujuan (rules v17), jadi "sudah dibuka" dicatat di tablet itu sendiri.
- Balasan lama (pesan ditandai dibaca + balasan dari Uang › titipan) tampil sebagai gelembung owner pada jam balasannya.

Tidak ada koleksi atau rules baru (tetap v17). Sesudah merge, fungsi server dipasang ulang sekali di Cloud Shell (baris yang sama dengan langkah 6 di atas)
supaya tanda dibaca dari obrolan tidak mengirim notifikasi ke tablet.

## Layar penuh (APK yang sama)

Menu (akun tablet) › kartu **Layar penuh** › **Nyalakan layar penuh**: bilah jam/baterai dan tombol kembali/beranda Android disembunyikan.
Tombol Android muncul sebentar kalau layar digeser dari tepi bawah (atau atas), lalu hilang lagi — tombol kembali & beranda tetap bisa dipakai lewat geseran
itu. Matikan dari kartu yang sama. Menu bawah (Ringkasan · Stok · Jual · Pelanggan · Menu) bisa dilipat lewat pegangan kecil di atasnya, di semua perangkat
(HP & tablet), tanpa APK baru.

## Kalau tidak jalan

- Kartu menulis "belum membawa notifikasi" → APK lama masih terpasang (langkah 5).
- Kartu menulis "dibangun tanpa berkas Firebase" → rahasia belum ada saat APK dibangun (langkah 2 lalu 4).
- "Notifikasi tablet BELUM menyala: …permission…" → rules v17 belum terbit (langkah 3).
- Menyala tapi notifikasi tidak datang saat owner menjawab → fungsi server belum dipasang ulang (langkah 6); lihat log di Cloud Shell:
  `gcloud functions logs read kabarTablet --region=asia-southeast2 --limit=20` (baris "kabarTablet … terkirim N").
- Izin ditolak di tablet → Setelan Android › Aplikasi › Toko Beras M.IQBAL › Notifikasi › izinkan, lalu Nyalakan lagi.
