// TIRAI LAYAR (putaran 23c, owner 24 Sep): selama belum masuk, atau akun belum disetujui / nonaktif / kasir@, layar di belakang formulir Masuk KOSONG —
// tidak ada angka, nama, atau kartu yang digambar dari cache (penyimpanan lokal peramban pun, mis. titik kas). Bawaan TERKUNCI: sebelum Firebase menjawab
// siapa yang masuk, tidak ada layar yang digambar. app.js membuka tirai hanya untuk owner / akun aktif (atau mode cadangan di komputer), dan saat menutupnya
// mengosongkan isi setiap <main>. Tiap layar memeriksa terkunci() sebelum menggambar. Diuji di peramban sungguhan: alat-uji/uji_layar_kunci.py.
let _kunci = true;
export const terkunci = () => _kunci;
export function setelKunci(ya) { _kunci = !!ya; }
