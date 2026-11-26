// RIWAYAT SETELAN — pencatat perubahan (owner 22 Nov 2026, paket riwayat & pembatalan tahap 3 "Setelan & harga, lihat saja"). Murni: tanpa DOM & tanpa Firebase;
// awalan rsd. Dipanggil penulis owner (firebase.js tulisBerkas) untuk tiap dokumen yang ditulis; dijaga alat-uji/uji_riwayat_setelan.py.
//
// Kenapa: dokumen setelan (aturanToko/…) DITIMPA tiap simpan — isi lamanya tidak pernah tersimpan (sensus 22 Nov: 2 dari 21 dokumen punya riwayat sendiri).
// Mulai sekarang tiap simpan owner menambah satu entri { pada, tanggal, jam, oleh, perangkat, ubah: [{ k, dari, ke }] } ke kolom `riwayatUbah` dokumen itu
// sendiri (paling banyak RSD_MAKS entri, yang tertua dibuang) — tanpa koleksi baru, tanpa rules baru, tanpa baca tambahan. Penulis yang menyusun dokumen dari
// nol (tanpa riwayatUbah) tidak menghapus riwayat: riwayat lama selalu dibawa dari salinan cache.
// Yang dicatat: aturanToko (kecuali draf kerja katalog harga & kunci periode — kunci punya rules & jejak nilai lama sendiri) dan hargaWadah. Katalog harga
// TIDAK (dibaca katalog HP kasir apa adanya; riwayatnya = hargaTerbit). Kolom dibandingkan sampai dua tingkat (peta di dalam peta jadi 'induk.anak');
// cap penulis, tanggal/jam simpan, dan riwayat sendiri tidak dihitung perubahan.

export const RSD_MAKS = 30;
export const RSD_KOLEKSI = { aturanToko: true, hargaWadah: true };
export const RSD_LEWAT = { 'aturanToko/hargaDraf': true, 'aturanToko/hargaLabel': true, 'aturanToko/hargaSengaja': true, 'aturanToko/kunciPeriode': true };
const RSD_ABAI = { id: 1, diubahOleh: 1, diubahOlehUid: 1, diubahPada: 1, diubahPerangkat: 1, oleh: 1, olehUid: 1, perangkat: 1, tanggal: 1, jam: 1, pada: 1, riwayatUbah: 1, riwayat: 1, capServer: 1, pencatatAsli: 1 };
const rsdPeta = (v) => !!v && typeof v === 'object' && !Array.isArray(v);
const rsdJ = (v) => (v === undefined ? undefined : JSON.stringify(v));
/** Nilai yang disimpan di entri: angka / teks / ya-tidak apa adanya (teks ≤ 200 huruf), selain itu JSON ≤ 300 huruf. */
const rsdNilai = (v) => (v === undefined || v === null ? null : typeof v === 'number' || typeof v === 'boolean' ? v : typeof v === 'string' ? v.slice(0, 200) : String(rsdJ(v)).slice(0, 300));
/** Peta kolom → nilai sampai dua tingkat. */
function rsdRata(d) {
  const o = {}; Object.keys(d || {}).forEach((k) => { if (RSD_ABAI[k]) return; const v = d[k];
    if (rsdPeta(v) && Object.keys(v).length) Object.keys(v).forEach((s) => { o[k + '.' + s] = v[s]; }); else o[k] = v; });
  return o;
}
/** Kolom yang berubah antara lama dan baru → [{ k, dari, ke }] (urut nama kolom, paling banyak 20). */
export function rsdBeda(lama, baru) {
  const a = rsdRata(lama), b = rsdRata(baru); const kunci = Object.keys(a).concat(Object.keys(b)).filter((k, i, s) => s.indexOf(k) === i).sort();
  return kunci.filter((k) => rsdJ(a[k]) !== rsdJ(b[k])).slice(0, 20).map((k) => ({ k, dari: rsdNilai(a[k]), ke: rsdNilai(b[k]) }));
}
/** Dicatat? (owner, koleksi setelan, bukan draf/kunci) */
// owner 26 Nov 2026: aturanToko/cocokRek-YYYY-MM = centang & hasil cocok rekening satu bulan — CATATAN (bukan setelan), tiap centang menulisnya: tidak dicatat
// (setelannya sendiri — toleransi, jenis penjelasan, bentuk berkas — ada di aturanToko/rekening dan tetap dicatat)
// paket Banding pemasok (owner 26 Nov 2026): aturanToko/banding-YYYY-MM = catatan harga tawaran & acuan satu bulan (CATATAN, bukan setelan) dan
// aturanToko/acuanTarik = hasil tarik otomatis fungsi server (bukan tulisan owner) — tidak dicatat; setelannya (aturanToko/bandingPemasok) tetap dicatat
export const RSD_LEWAT_AWALAN = ['aturanToko/cocokRek-', 'aturanToko/banding-', 'aturanToko/acuanTarik'];
export const rsdDicatat = (koleksi, id, owner) => !!owner && !!RSD_KOLEKSI[koleksi] && !RSD_LEWAT[koleksi + '/' + String(id)] && !RSD_LEWAT_AWALAN.some((a) => (koleksi + '/' + String(id)).indexOf(a) === 0);
/**
 * Dokumen d (sudah bercap penulis) + entri riwayatUbah bila ada kolom yang berubah dari `lama` (salinan cache; tidak ada = dokumen baru).
 * Riwayat lama selalu dibawa. Tidak dicatat / tidak berubah & tanpa riwayat = d apa adanya (objek yang sama).
 */
export function rsdSertakan(koleksi, d, lama, owner, kini) {
  if (!d || !rsdDicatat(koleksi, d.id, owner)) return d;
  const dulu = Array.isArray(lama && lama.riwayatUbah) ? lama.riwayatUbah : Array.isArray(d.riwayatUbah) ? d.riwayatUbah : [];
  const ubah = rsdBeda(lama || {}, d);
  if (!ubah.length && !dulu.length) return d;
  const t = String(kini || new Date().toISOString());
  const entri = ubah.length ? [Object.assign({ pada: t, tanggal: String(d.tanggal || ''), jam: String(d.jam || ''), oleh: String(d.diubahOleh || d.oleh || ''), perangkat: String(d.diubahPerangkat || d.perangkat || ''), ubah }, lama ? {} : { baru: true })] : [];
  return Object.assign({}, d, { riwayatUbah: dulu.concat(entri).slice(-RSD_MAKS) });
}
