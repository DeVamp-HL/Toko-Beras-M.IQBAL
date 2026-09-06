// Service worker kasir M.IQBAL — kasir kebuka INSTAN di HP lemah & tetap jalan offline.
// v4 (4 Agustus 2026): strategi kasir.html diganti network-first -> CACHE DULU, perbarui
// di belakang layar (stale-while-revalidate). Alasan: di HP kentang + sinyal jelek,
// network-first membuat halaman menunggu jaringan gagal dulu baru buka — bisa belasan
// detik. Sekarang: buka langsung dari cache (<1 detik), versi baru diunduh diam-diam
// untuk pembukaan berikutnya. kasir-darurat-nominal.html ikut di-cache — katup darurat
// justru paling wajib bisa kebuka saat jaringan mati.
// v5 (9 Agustus 2026): kasir dapat kolom nama pembeli (wajib, ketiga cara bayar) dan
// layar UTANG. VERSI dinaikkan supaya perubahan sebesar ini langsung terpasang begitu
// kasir dibuka — kalau tidak, strategi "cache dulu" di bawah menyajikan kasir LAMA satu
// kali dulu, dan kasir sempat menyimpan penjualan tanpa nama pelanggan.
// v6 (9 Agustus 2026): kasir darurat ikut dapat pilihan Tunai/QRIS/Kredit + nama
// pembeli (sebelumnya caraBayar DIPAKU 'Tunai', jadi QRIS/kredit tercatat keliru).
// v7 (9 Agustus 2026): kasir.html jadi alat OWNER — gerbang jam operasional & wajib
// pilih operator dicabut, harga di luar katalog diterima (ditanya barangnya nanti).
// v8 (9 Agustus 2026): nama pembeli tidak lagi wajib untuk Tunai/QRIS — cuma Kredit.
// v9 (9 Agustus 2026): panel tuts nama produk dibuang dari kasir owner.
// v10 (9 Agustus 2026): layar KEMBALIAN — sebut lembar uang yang harus diambil.
// v11 (9 Agustus 2026): kasir darurat mencatat PER BARANG (tombol +), bukan satu total —
// supaya tiap harga bisa dicocokkan ke produk tanpa mengandalkan ingatan Gono.
// v12 (9 Agustus 2026): tuts harga cepat di kasir darurat — sekali ketuk jadi satu barang.
// v13 (10 Agustus 2026): karung bekas dihitung 1 lembar tiap 65 liter, bukan 1 lembar
// berapa pun liternya.
// v14 (11 Agustus 2026): opsi karung 25 kg dicabut dari Jual Karung Utuh — cuma 50 kg.
// v15 (11 Agustus 2026): layar KEMBALIAN dapat tombol konfirmasi "Sudah saya kasih ke
// pembeli" — statusnya ikut tersimpan ke transaksi supaya bisa dicek lagi kalau pembeli
// belakangan nanya soal kembaliannya.
// v16 (11 Agustus 2026): ejaan caraBayar dibakukan jadi 'QRIS' (kapital) di kasir dan
// kasir darurat. WAJIB naik: dengan cache lama, kasir masih menyimpan 'Qris' walau
// berkasnya sudah diperbarui — terbukti saat pengujian, v15 menyajikan versi lama.
// v17 (12 Agustus 2026): kasir memberi tahu umur harganya sendiri. Kasir MEMBEKUKAN
// harga & HPP dari ringkasan yang di-cache; kalau penyegaran gagal berjam-jam, kasir
// tetap jualan pakai harga lama tanpa ada yang memberi tahu. Sekarang ada bilah yang
// diam selama masih segar dan menyela di atas 6 jam / sehari.
// v18 (12 Agustus 2026): struk digital — sesudah transaksi tersimpan muncul bilah
// "Struk terakhir", ketuk untuk mengirimkannya lewat WhatsApp. Tautannya wa.me tanpa
// nomor tujuan, jadi nomor pembeli tidak perlu diminta apalagi disimpan.
// v19 (13 Agustus 2026): kasir darurat dapat TUTS BERNAMA BARANG — kalau HP punya
// salinan katalog (ringkasan kasir), sekali ketuk = barang + harga + HPP tercatat
// sebagai penjualan lengkap yang tidak perlu dirinci. Ditambah kolom catatan nego
// untuk angka polos. WAJIB naik: dengan cache lama, darurat masih menyimpan
// nominal-tanpa-barang walau berkasnya sudah diperbarui.
// v20 (13 Agustus 2026): SACK 25 hidup lagi + istilah sack. Toko mulai membeli
// sack 25 kg (Angsa, Perahu Layar) dan menjualnya utuh. Kasir & darurat dapat
// tombol SACK25 per merk yang memang punya, harga & HPP dari ringkasan.
// v21 (26 Agustus 2026): kasir darurat — tombol "Lewati" tidak lagi bisa membuat
// antrean menggunung diam-diam. Bilah merah permanen menghitung catatan yang belum
// terkirim, dan layar sandi muncul lagi tiap selesai mencatat selama belum masuk.
// WAJIB naik: tanpa ini HP pegawai tetap menyajikan darurat lama dari cache.
// v22 (26 Agustus 2026): Fase 1 identitas — kasir & darurat menyuntik oleh+perangkat
// ke tiap catatan. WAJIB naik supaya HP lama tidak menyajikan versi tanpa atribusi.
// v23 (5 September 2026): pembulatan KE ATAS Rp500 untuk TUNAI di kasir.html — LCD, layar
// KEMBALIAN, struk WA, dan dokumen yang diantrekan memakai tagihan yang sudah dibulatkan
// (field `pembulatan` menempel ke barang terakhir). WAJIB naik: aturan yang sama masuk
// index.html pada push yang sama; dengan cache lama, kasir.html masih menagih Rp51.750
// sementara layar owner menagih Rp52.000 untuk barang yang sama — dua pintu beda angka,
// persis penyakit yang perubahan ini dibuat untuk menyembuhkan, dan diamnya sempurna.
// v24 (6 September 2026): DENYUT PERANGKAT di KEDUA berkas — kasir-darurat-nominal.html
// (dipegang Gono & Hasan sejak pembagian 9 Agu 2026) DAN kasir.html (alat owner) menulis
// perangkatStatus/{id} tiap 5 menit selagi layarnya terlihat, membawa cacah antrean
// tertahan. Yang menentukan adalah berkas DARURAT: itu satu-satunya cara owner tahu DARI
// JAUH bahwa penjualan di HP pegawai berhenti diam-diam. Tanpa ini HP pegawai tidak
// pernah muncul sama sekali di layar Akun & Perangkat — dan memasangnya cuma di
// kasir.html akan memajang HP owner saja sambil diam soal HP yang justru perlu dipantau.
// Denyutnya sengaja DI LUAR antrean (tembak-lalu-lupa, gagal = diam) supaya satu denyut
// yang ditolak tidak pernah membekukan penjualan di belakangnya. WAJIB naik: dengan cache
// lama HP pegawai tetap menjalankan berkas tanpa denyut, jadi di layar owner ia terbaca
// "tidak pernah terhubung" — persis kebalikan dari keadaan sebenarnya, dan diamnya
// sempurna. Kedua berkas sudah ada di FILES, jadi satu kenaikan versi menyegarkan dua-duanya.
const VERSI = 'kasir-v24';
const FILES = ['kasir.html', 'kasir-darurat-nominal.html', 'manifest-kasir.json', 'icon-kasir-192.png', 'icon-kasir-512.png', 'icon-kasir-180.png', 'icon-kasir-32.png'];
const HTML_SWR = ['kasir.html', 'kasir-darurat-nominal.html'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSI).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSI).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  // Hanya tangani file kasir sendiri. Firestore, index.html, dan lainnya lewat jaringan biasa.
  if (url.origin !== location.origin) return;
  const nama = url.pathname.split('/').pop();
  if (!FILES.includes(nama)) return;
  if (HTML_SWR.includes(nama)) {
    // cache dulu (instan), lalu perbarui di belakang layar untuk buka berikutnya
    e.respondWith(
      caches.match(e.request).then((tersimpan) => {
        const dariJaringan = fetch(e.request).then((r) => {
          if (r && r.ok) {
            const salinan = r.clone();
            caches.open(VERSI).then((c) => c.put(e.request, salinan));
          }
          return r;
        }).catch(() => tersimpan);
        return tersimpan || dariJaringan;
      })
    );
  } else {
    e.respondWith(caches.match(e.request).then((r) => r || fetch(e.request)));
  }
});
