// JENIS BERAS (putaran 25c, owner 27 Sep 2026: tampil di Harga + Stok + Jual) — setelan pindah dari sistem lama (simpanJenisBeras / ubahJenisBeras
// index.html). Dokumen SAMA: pengaturan/jenisBeras { id, peta: { <nama beras>: <jenis> }, diubahPada } + atribusi penulis pusat.
// Aturan membaca verbatim dari index.html (pindah_mesin.py): jenisUntukMerk = isi peta kalau ada (termasuk '' = sengaja dikosongkan), selain itu
// tebakan dari namanya (tebakJenisBeras); daftar nama = semuaMerkDikenal (stok karung, kemasan, katalog karung); pilihan = PILIHAN_JENIS_BERAS.
// Salah isi hanya menggeser pengelompokan — tidak ada angka uang, stok, atau harga yang berubah (docs/peta-pindahan-terakhir.md §3).
// Tanpa DOM; nama berawalan jb (bundel uji satu lingkup). Dijaga alat-uji/uji_setelan_jenis_beras.py.
import { jenisUntukMerk, semuaMerkDikenal, PILIHAN_JENIS_BERAS } from '../mesin/pembantu.js';
import { hitungStokKarungPerMerk } from '../mesin/beku.js';
import { ambilPetaJenisBeras, petaStokWadah, kunciStokWadah } from '../data/toko.js';

export const JB_BELUM = 'Belum diisi jenisnya';   // sama dengan layar Stok sistem lama
export const jbJenisMerk = (merk) => jenisUntukMerk(merk);
export const JB_BATAS = 40;
const jbBersih = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();

/** Pilihan jenis: tujuh bawaan sistem lama, lalu jenis lain yang pernah diketik owner (masih dipakai di peta). */
export function jbPilihan() {
  const lain = []; const peta = ambilPetaJenisBeras();
  Object.keys(peta).forEach((m) => { const j = jbBersih(peta[m]); if (j && PILIHAN_JENIS_BERAS.indexOf(j) < 0 && lain.indexOf(j) < 0) lain.push(j); });
  return PILIHAN_JENIS_BERAS.slice().concat(lain.sort((a, b) => a.localeCompare(b)));
}
/** Semua nama beras yang dikenal + jenisnya: asal = 'owner' (diisi), 'kosong' (sengaja dikosongkan), 'tebakan' (dari nama), '' (belum ada). */
export function jbDaftar() {
  const peta = ambilPetaJenisBeras();
  const baris = semuaMerkDikenal().map((m) => {
    const ada = Object.prototype.hasOwnProperty.call(peta, m); const jenis = jenisUntukMerk(m);
    return { merk: m, jenis, asal: ada ? (jenis ? 'owner' : 'kosong') : jenis ? 'tebakan' : '' };
  });
  return { baris, terisi: baris.filter((b) => b.jenis).length, total: baris.length };
}
/** Satu nama beras → satu jenis ('' = kosongkan: tidak masuk kelompok mana pun, menimpa tebakan). → { tolak } | { dokumen, patch }. */
export function susunJenisBeras(merk, jenis, w) {
  const m = String(merk || ''); const j = jbBersih(jenis);
  if (!m) return { tolak: 'Nama berasnya kosong' };
  if (semuaMerkDikenal().indexOf(m) < 0) return { tolak: m + ' tidak dikenal di stok maupun katalog — jenisnya diisi sesudah namanya muncul di Barang masuk, Adukan, atau Katalog' };
  if (j.length > JB_BATAS) return { tolak: 'Nama jenis paling panjang ' + JB_BATAS + ' huruf' };
  const peta = ambilPetaJenisBeras();
  if (Object.prototype.hasOwnProperty.call(peta, m) && String(peta[m]) === j) return { tolak: m + ' sudah ' + (j ? 'berjenis ' + j : 'dikosongkan') };
  peta[m] = j;
  return { dokumen: [{ koleksi: 'pengaturan', data: { id: 'jenisBeras', peta, diubahPada: w.kini } }],
    patch: { jbUbah: null, jbKetik: '', kabar: j ? m + ' → ' + j + '. Pengelompokan di Harga, Stok, dan Jual ikut berganti.' : m + ' dikosongkan — tidak masuk kelompok jenis mana pun.', kabarAwas: false } };
}
/** Stok › Gudang: total kg karung per jenis — urutan sistem lama (IR64 dulu, yang belum diisi paling bawah). Nama bersisa 0 tidak ikut. */
export function jbKelompokStok() {
  const stok = hitungStokKarungPerMerk(); const per = {}; const wadahStok = petaStokWadah();
  // putaran 28: buku stok wadah ('Wadah <nama>') ikut jenis NAMA wadahnya (isinya beras jenis itu)
  Object.keys(stok).filter((m) => stok[m].sisaKg !== 0).forEach((m) => { const j = jenisUntukMerk(wadahStok[m] ? String(m).slice(kunciStokWadah('').length) : m) || JB_BELUM; (per[j] = per[j] || []).push(m); });
  return Object.keys(per).sort((a, b) => (a === JB_BELUM) - (b === JB_BELUM) || (b === 'IR64') - (a === 'IR64') || a.localeCompare(b))
    .map((j) => ({ jenis: j, kg: per[j].reduce((x, m) => x + (stok[m].sisaKg || 0), 0), merk: per[j].slice().sort((a, b) => a.localeCompare(b)) }));
}
/** Nama beras sebuah chip Jual: karung/literan/repack = kunci (nama beras); kemasan = namaProduk (kunci "nama|ukuran", seperti index.html). */
export const jbMerkChip = (c) => (c && c.jalur === 'kemasan' ? String(c.kunci || '').split('|')[0] : String((c && c.kunci) || ''));
export const jbJenisChip = (c) => jenisUntukMerk(jbMerkChip(c)) || JB_BELUM;
/** Jual: jenis yang ADA di satu jalur rak + banyaknya barang, urutan sama dengan Stok. */
export function jbJenisRak(daftar) {
  const n = {}; (daftar || []).forEach((c) => { const j = jbJenisChip(c); n[j] = (n[j] || 0) + 1; });
  return Object.keys(n).sort((a, b) => (a === JB_BELUM) - (b === JB_BELUM) || (b === 'IR64') - (a === 'IR64') || a.localeCompare(b)).map((j) => ({ jenis: j, n: n[j] }));
}
/** Jual: saring satu jalur rak ke satu jenis ('' = semua). Urutan rak (per ukuran, termurah dulu — desain Jual yang dikunci) TIDAK diubah. */
export function jbSaringRak(daftar, jenis) { return !jenis ? (daftar || []) : (daftar || []).filter((c) => jbJenisChip(c) === jenis); }
