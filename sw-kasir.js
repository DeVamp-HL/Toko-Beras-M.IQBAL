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
const VERSI = 'kasir-v17';
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
