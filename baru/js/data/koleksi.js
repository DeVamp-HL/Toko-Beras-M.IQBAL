// Daftar koleksi Firestore yang dibaca sistem baru — SATU tabel, tanpa impor.
// `urut` = kolom pengurut (terbaru dulu), sama dengan pasangSinkronisasi() di index.html.
// `cache` = nama cache di toko.js yang diisi koleksi itu.
export const KOLEKSI = [
  { nama: 'batchMasuk',          urut: 'id',    cache: 'batch' },
  { nama: 'biayaBulanan',        urut: 'bulan', cache: 'bulanan' },
  { nama: 'penjualan',           urut: 'id',    cache: 'penjualan' },
  { nama: 'produksiKemasan',     urut: 'id',    cache: 'produksi' },
  { nama: 'retur',               urut: 'id',    cache: 'retur' },
  { nama: 'karantina',           urut: 'id',    cache: 'karantina' },
  { nama: 'pengeluaranHarian',   urut: 'id',    cache: 'harian' },
  { nama: 'stokBahanKemasan',    urut: 'id',    cache: 'bahanKemasan' },
  { nama: 'stokBahanLiteran',    urut: 'id',    cache: 'bahanLiteran' },
  { nama: 'katalogHargaLiteran', urut: 'merk',  cache: 'hargaLiteran' },
  { nama: 'katalogHargaKemasan', urut: 'id',    cache: 'hargaKemasan' },
  { nama: 'katalogHargaKarung',  urut: 'merk',  cache: 'hargaKarung' },
  { nama: 'piutangMutasi',       urut: 'id',    cache: 'piutang' },
  { nama: 'kasbonMutasi',        urut: 'id',    cache: 'kasbon' },
  { nama: 'penyesuaianStok',     urut: 'id',    cache: 'penyesuaian' },
  { nama: 'tutupHari',           urut: 'id',    cache: 'tutup' },
  { nama: 'pelangganCatatan',    urut: 'id',    cache: 'pelangganCat' },
  { nama: 'pesanan',             urut: 'id',    cache: 'pesanan' },
  { nama: 'titipanHarian',       urut: 'id',    cache: 'titipan' },
  { nama: 'setoranKas',          urut: 'id',    cache: 'setoran' },
  { nama: 'penyesuaianKemasan',  urut: 'id',    cache: 'penyKemasan' },
  { nama: 'amplopLaba',          urut: 'id',    cache: 'amplop' },
  { nama: 'modalOwner',          urut: 'id',    cache: 'modal' },
  { nama: 'utangOwnerMutasi',    urut: 'id',    cache: 'utangOwner' },
  { nama: 'tembusanStok',        urut: 'id',    cache: 'tembusan' },
  { nama: 'utangPemasokMutasi',  urut: 'id',    cache: 'utangPemasok' },
  { nama: 'thrPelanggan',        urut: 'id',    cache: 'thr' },
  { nama: 'pemasokCatatan',      urut: 'id',    cache: 'pemasokCat' },
  // KOLEKSI BARU milik sistem baru (19 Sep 2026) — sistem lama tidak mengenalnya dan cadangan sistem lama TIDAK memuatnya.
  // Isinya catatan wadah literan: samakan isi, TAKAR isi ulang (dengan merek asalnya), karung yang dibuka di belakang wadah, dan aturan
  // owner (posisi, campuran, angka). ALAT UKUR kapan harus isi ulang, BUKAN pencatatan stok/uang (stok literan tetap dipotong dari
  // kolam merek saat TERJUAL). Aturan Firestore: jatuh ke aturan umum "owner saja".
  { nama: 'wadahLiteran',        urut: 'id',    cache: 'wadah' },
  // KOLEKSI BARU sistem baru (23 Sep 2026): angka kebijakan owner untuk pencatatan stok (id tetap, mis. 'catatStok') dan jejak kedatangan
  // yang dihapus (beralasan). Sistem lama tidak membacanya; aturan Firestore jatuh ke "owner saja".
  { nama: 'aturanToko',          urut: 'id',    cache: 'aturan' },
  { nama: 'bukuHapus',           urut: 'id',    cache: 'bukuHapus' },
  { nama: 'tagihPelanggan',      urut: 'id',    cache: 'tagih' },       // tagihan bon lewat WhatsApp + janji bayar (putaran 13)
  { nama: 'pelangganTitip',      urut: 'id',    cache: 'titip' },       // yang datang bukan orangnya (benang merah)
  // Putaran 14 (23 Sep 2026) — layar MENU & SISTEM:
  //  perangkatStatus = denyut tiap perangkat (koleksi sistem lama; sistem baru ikut menulis denyutnya sendiri, `aplikasi: 'baru'`).
  //  logAktivitas    = jejak siapa menulis apa (koleksi sistem lama); DIBACA TERBATAS `batas` baris terbaru — bukan seluruh koleksi.
  //  cadanganCatatan, pengingat, persetujuan, pindahStok = koleksi BARU sistem baru (aturan Firestore jatuh ke "owner saja").
  { nama: 'perangkatStatus',     urut: 'pada',  cache: 'perangkat' },
  { nama: 'logAktivitas',        urut: 'pada',  cache: 'log', batas: 150 },
  { nama: 'cadanganCatatan',     urut: 'id',    cache: 'cadangan' },     // tiap cadangan berkas yang diunduh dari sistem baru
  { nama: 'pengingat',           urut: 'id',    cache: 'pengingat' },    // keadaan tiap pengingat (selesai / ditunda / WA hari ini)
  { nama: 'persetujuan',         urut: 'id',    cache: 'persetujuan' },  // permintaan "minta owner" dari tablet/Mac + keputusannya
  { nama: 'pindahStok',          urut: 'id',    cache: 'pindahStok' },   // pindah stok antarlokasi: dua catatan (keluar & masuk)
];
