// JADWAL GAMBAR — owner 29 Sep 2026: "perpindahan layar ada lag, kurang smooth, suka nge-freeze apalagi waktu refresh & pertama buka".
// Penyebab terukur (alat-uji/ukur_kinerja_baru.py, cadangan toko 28 Sep, 54 koleksi / 6.916 dokumen): tiap koleksi yang datang dari
// Firestore (dari simpanan perangkat LALU dari server, ±108 kali saat membuka) memanggil gambar ulang SEMUA layar secara langsung, dan
// layar Jual menyusun ulang raknya (±50 ms di Mac) tiap kali — ±3 detik hitungan beruntun sebelum layar sempat dicat.
// Di sini: permintaan gambar DIGABUNG — fungsi yang sama diminta berkali-kali dalam satu bingkai dijalankan SEKALI.
// Yang tetap langsung: tanda "perlu hitung ulang" (mis. rak) dipasang oleh pemanggil sebelum meminta; ketukan pemakai tetap
// menggambar seketika (K.dengar), yang ditunda hanya bunyi dari data & status sambungan.
const _antre = new Set();
let _token = 0, _muat = false, _menunggu = false;
const JEDA_MUAT_MS = 320;   // selama data awal masih berdatangan: paling banyak ±3 gambar per detik

function jalankan(t) {
  if (t !== _token) return;   // sudah dijalankan jalur lain (rAF vs penjaga setTimeout)
  _token += 1; _menunggu = false;
  const daftar = Array.from(_antre); _antre.clear();
  daftar.forEach((f) => { try { f(); } catch (e) { console.error('gambar tertunda', e); } });
}

/** Minta f dijalankan di bingkai berikutnya (digabung). Tab tersembunyi: requestAnimationFrame tidak jalan → penjaga setTimeout. */
export function nanti(f) {
  _antre.add(f);
  if (_menunggu) return;   // sudah ada jadwal yang menunggu — f ikut di dalamnya
  _menunggu = true; const t = _token;
  if (_muat) { setTimeout(() => jalankan(t), JEDA_MUAT_MS); return; }
  const tersembunyi = typeof document !== 'undefined' && document.hidden;
  if (typeof requestAnimationFrame === 'function' && !tersembunyi) requestAnimationFrame(() => jalankan(t));
  setTimeout(() => jalankan(t), tersembunyi ? 0 : 120);
}

/** Jalur KETUKAN (tinjauan 29 Sep: selama masa muat, layar yang baru diketuk tampil kosong sampai 320 ms): selalu di bingkai berikutnya,
 *  walau sedang masa muat. Yang menunggu di antrean ikut tergambar di bingkai itu (sekali saja — tanda giliran mencegah ganda). */
export function segera(f) {
  _antre.add(f);
  if (_menunggu && !_muat) return;   // bingkai berikutnya sudah dijadwalkan
  _menunggu = true; const t = _token;
  const tersembunyi = typeof document !== 'undefined' && document.hidden;
  if (typeof requestAnimationFrame === 'function' && !tersembunyi) requestAnimationFrame(() => jalankan(t));
  setTimeout(() => jalankan(t), tersembunyi ? 0 : 120);
}

/** Masa muat awal (koleksi belum lengkap): gambar dijarangkan. Saat selesai, yang menunggu langsung digambar. */
export function setelMuat(ya) {
  const tadi = _muat; _muat = !!ya;
  if (tadi && !_muat && _menunggu) jalankan(_token);
}
export const sedangMuat = () => _muat;
