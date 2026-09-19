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
  // Isinya penanda "wadah literan diisi ulang": ALAT UKUR kapan harus isi ulang, BUKAN pencatatan stok/uang (stok literan tetap
  // dipotong dari kolam merek seperti biasa). Aturan Firestore: jatuh ke aturan umum "owner saja".
  { nama: 'wadahLiteran',        urut: 'id',    cache: 'wadah' },
];
