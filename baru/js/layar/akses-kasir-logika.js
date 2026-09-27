// OPERATOR KASIR & PIN OWNER (putaran 25c, owner 27 Sep 2026) — pindah dari sistem lama (bukaModalJaga/simpanModalJaga dan
// bukaSetelPin/simpanSetelPin index.html) ke Menu › Sistem › Peran & akses › Kasir & PIN.
//
// OPERATOR — dokumen pengaturan/aksesKasir { id, operator: { <nama>: { aktif } }, diubahPada } + atribusi penulis pusat. Bentuk sistem lama MINUS
// field `pin` (keputusan owner 27 Sep: "cabut PIN"): PIN operator tersimpan TANPA diacak di dokumen yang dibaca akun kasir@ (rules v4 baris
// pengaturan), padahal tidak dipakai kasir mana pun — layar pilih operator kasir.html tidak punya pintu sejak 9 Agu 2026, kasir darurat tidak membaca
// dokumen ini (docs/peta-pindahan-terakhir.md §4). Setiap simpan dari sini menulis dokumen TANPA pin; kasir.html (infoOperator) membacanya sebagai
// "tanpa PIN". Nama operator = kunci peta di dokumen — tidak ada nama orang di kode ini (repo publik).
// PIN OWNER — dokumen pengaturan/keamanan { id, garam, acak, diubahPada }: hanya hasil acak (acakPin VERBATIM index.html: SHA-256 dari garam|PIN),
// dibaca owner saja. Dipakai gembok Menu sistem lama; sistem baru memakai akun. Aturan sama dengan simpanSetelPin: PIN sekarang wajib benar
// kalau sudah disetel, PIN baru 4–8 angka, diketik dua kali.
// Tanpa DOM; nama berawalan op (bundel uji satu lingkup). Dijaga alat-uji/uji_operator_pin.py.
import { cacheMentah } from '../data/toko.js';
import { acakPin } from '../mesin/pembantu.js';

const opDok = (id) => cacheMentah('pengaturan').find((d) => String(d.id) === id) || null;
const opPeta = () => { const d = opDok('aksesKasir'); return d && d.operator && typeof d.operator === 'object' && !Array.isArray(d.operator) ? d.operator : {}; };
const opAdaPin = (x) => !!x && x.pin !== undefined && x.pin !== null && String(x.pin) !== '';
const opBersih = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();

/** Daftar operator: { baris: [{ nama, aktif }], berPin: jumlah PIN terbuka yang masih tersimpan, ada, diubahPada }. Isi PIN TIDAK pernah dikembalikan. */
export function opDaftar() {
  const d = opDok('aksesKasir'); const o = opPeta();
  const baris = Object.keys(o).sort((a, b) => a.localeCompare(b)).map((n) => ({ nama: n, aktif: !o[n] || o[n].aktif !== false }));
  return { baris, berPin: Object.keys(o).filter((n) => opAdaPin(o[n])).length, ada: !!d, diubahPada: d ? String(d.diubahPada || '') : '' };
}
// Dokumen baru — peta TANPA pin (semua operator ditulis ulang { aktif } saja, jadi PIN lama ikut tercabut di simpan mana pun)
function opKirim(ubah, w, kabar) {
  const o = {}; opDaftar().baris.forEach((b) => { o[b.nama] = { aktif: b.aktif }; }); ubah(o);
  return { dokumen: [{ koleksi: 'pengaturan', data: { id: 'aksesKasir', operator: o, diubahPada: w.kini } }], patch: { opYakin: null, kabar, kabarAwas: false } };
}
export function susunCabutPinOperator(w) {
  const D = opDaftar(); if (!D.ada) return { tolak: 'Dokumen operator kasir belum ada — tidak ada PIN yang tersimpan' };
  if (!D.berPin) return { tolak: 'Tidak ada PIN operator yang tersimpan' };
  return opKirim(() => {}, w, D.berPin + ' PIN operator dicabut dari dokumen yang dibaca akun kasir. Nama & aktif/libur tetap.');
}
export function susunOperatorAktif(nama, aktif, w) {
  const D = opDaftar(); const b = D.baris.find((x) => x.nama === nama); if (!b) return { tolak: 'Operator itu tidak ada di daftar' };
  if (b.aktif === !!aktif) return { tolak: nama + ' sudah ' + (aktif ? 'aktif' : 'libur') };
  return opKirim((o) => { o[nama] = { aktif: !!aktif }; }, w, nama + (aktif ? ' aktif lagi' : ' libur') + (D.berPin ? ' · PIN operator yang masih tersimpan ikut dicabut' : ''));
}
// TIDAK ADA "tambah operator" (owner 27 Sep, sesudah pemeriksaan): nama baru tidak akan muncul di kasir mana pun — layar pilih operator kasir.html
// menggambar daftar nama TETAP dari kodenya (dan tidak punya pintu sejak 9 Agu), kasir darurat tidak membaca dokumen ini. Tombol yang hasilnya tidak
// sampai ke mana pun = layar yang berbohong.
/** Hapus = dua ketukan (ketukan pertama → { perluYakin }). */
export function susunOperatorHapus(nama, w, yakin) {
  const D = opDaftar(); if (!D.baris.some((x) => x.nama === nama)) return { tolak: 'Operator itu tidak ada di daftar' };
  if (!yakin) return { perluYakin: true };
  return opKirim((o) => { delete o[nama]; }, w, nama + ' dihapus dari daftar operator');
}

/** Keadaan PIN owner — tanpa isi garam/acak. */
export function opPinOwner() { const d = opDok('keamanan'); return { disetel: !!(d && d.acak && d.garam), diubahPada: d ? String(d.diubahPada || '') : '' }; }
/** isi = { lama, baru, ulang }. ASYNC (acakPin memakai SHA-256 peramban). garamBaru boleh diberikan uji; bawaan = bentuk garam index.html. */
export async function susunPinOwner(isi, w, garamBaru) {
  const d = opDok('keamanan'); const disetel = !!(d && d.acak && d.garam);
  const lama = opBersih(isi && isi.lama); const baru = opBersih(isi && isi.baru); const ulang = opBersih(isi && isi.ulang);
  if (disetel && (!lama || (await acakPin(lama, d.garam)) !== d.acak)) return { tolak: 'PIN sekarang salah.' };
  if (!/^[0-9]{4,8}$/.test(baru)) return { tolak: 'PIN baru harus 4 sampai 8 angka.' };
  if (baru !== ulang) return { tolak: 'Ulangan PIN tidak sama.' };
  const garam = garamBaru || ('g' + Date.now().toString(36) + Math.random().toString(36).slice(2, 10));
  const acak = await acakPin(baru, garam);
  return { dokumen: [{ koleksi: 'pengaturan', data: { id: 'keamanan', garam, acak, diubahPada: w.kini } }],
    patch: { pinIsi: { lama: '', baru: '', ulang: '' }, kabar: 'PIN owner ' + (disetel ? 'diganti' : 'disetel') + '. Berlaku di gembok sistem lama begitu perangkatnya online.', kabarAwas: false } };
}
