// RIWAYAT & BATAL — SETELAN & HARGA, LIHAT SAJA (owner 22 Nov 2026, paket riwayat & pembatalan tahap 3). Logika tanpa DOM; awalan rs.
// Dijaga alat-uji/uji_riwayat_setelan.py. Tidak ada tombol batal: setelan & harga dibetulkan di layarnya masing-masing (keputusan owner 22 Nov: "lihat saja").
// Sumber, terbaru di atas:
//  · HARGA katalog = tiap terbitan katalog (hargaTerbit: harga lama → baru per baris, sejak 26 Sep 2026) · harga wadah (riwayatUbah, atau hargaSebelum → harga);
//  · SETELAN = riwayatUbah di dokumen aturanToko (dicatat penulis owner mulai 22 Nov 2026 — data/riwayat-setelan.js) + riwayat lama milik dokumen itu sendiri
//    (nilai karung bekas, identitas, kunci bulan). Setelan tanpa catatan: satu baris "terakhir disimpan" (kapan & oleh siapa) — isi sebelumnya memang tidak
//    pernah tersimpan, dan itu dikatakan apa adanya.
import { cacheMentah, ambilHargaTerbit } from '../data/toko.js';
import { RSD_LEWAT } from '../data/riwayat-setelan.js';
import { RP, ANGKA, tanggalPendek, hariIniIso, jamSetempat } from '../inti/format.js';

export const RS_MULAI = '2026-11-22';   // pencatatan setelan dari → ke mulai hari ini
export const RS_SARING = [['', 'Semua'], ['harga', 'Harga'], ['setelan', 'Setelan']];
export const RS_JUDUL = { bandingPemasok: 'Banding pemasok', catatStok: 'Pencatatan stok', tutupHari: 'Tutup hari', uangKeluar: 'Uang keluar', peran: 'Peran & persetujuan', struk: 'Struk', notif: 'Notifikasi',
  upah: 'Upah', pindahUang: 'Pindah uang', bonPemasok: 'Bon pemasok', tempat: 'Tempat simpan', karungBekas: 'Nilai karung bekas', identitas: 'Identitas toko',
  hargaTingkat: 'Harga tingkat (warung · catering · instansi)', het: 'HET', kelasMerek: 'Kelas merek', pengingat: 'Pengingat', pelangganKembar: 'Pelanggan kembar',
  produkArsip: 'Produk diarsipkan', harga: 'Aturan harga', kendaliBiaya: 'Kendali biaya', kantong: 'Kantong', laporan: 'Laporan', dokumen: 'Dokumen', stokUmur: 'Umur stok',
  hpp: 'Modal (HPP)', hargaMinimum: 'Harga minimum & HET', merekLaporan: 'Susut & per merek', kepatuhan: 'Kalender kepatuhan', tutupBuku: 'Tutup buku', pelanggan: 'Pelanggan', kunciPeriode: 'Kunci bulan', perangkat: 'Perangkat' };
const RS_GOLONG_HARGA = { harga: true, hargaTingkat: true, het: true, karungBekas: true, hargaMinimum: true };
const RS_SISTEM = { hematHarian: true, acuanTarik: true };   // dokumen sistem (klaim baca penuh harian · hasil tarik harga acuan fungsi server) — bukan setelan owner
const rsJam = (j) => String(j || '').slice(0, 5);
/** 'minKarung' → 'min karung', 'tarif.harian' → 'tarif › harian'. */
export const rsKolom = (k) => String(k || '').split('.').map((x) => x.replace(/([a-z0-9])([A-Z])/g, '$1 $2').toLowerCase()).join(' › ');
/** Nilai tersimpan → kalimat: angka ber-titik, ya/tidak, kosong; JSON (peta/daftar) dibaca jadi "a: 1, b: 2" atau "3 baris". */
export function rsNilai(v) {
  if (v === null || v === undefined || v === '') return 'kosong';
  if (typeof v === 'boolean') return v ? 'ya' : 'tidak';
  if (typeof v === 'number') return ANGKA(v);
  const s = String(v); if (!/^[[{]/.test(s)) return s;
  try { const o = JSON.parse(s);
    if (Array.isArray(o)) return o.length && o.every((x) => x === null || typeof x !== 'object') ? o.join(', ') : o.length + ' baris' + (o[0] && (o[0].nama || o[0].merk) ? ' (' + o.slice(0, 3).map((x) => x.nama || x.merk).join(', ') + (o.length > 3 ? ', …' : '') + ')' : '');
    return Object.keys(o).slice(0, 6).map((k) => rsKolom(k) + ': ' + (o[k] !== null && typeof o[k] === 'object' ? '…' : rsNilai(o[k]))).join(', ') + (Object.keys(o).length > 6 ? ', …' : '');
  } catch (e) { return s.slice(0, 120) + (s.length > 120 ? '…' : ''); }
}
const rsWaktu = (pada, tgl, jam) => { const d = pada ? new Date(pada) : null; const ok = d && isFinite(d.getTime()); return { tanggal: ok ? hariIniIso(d) : String(tgl || ''), jam: ok ? jamSetempat(pada) : rsJam(jam) }; };
const rsRp = (n) => (Number(n) > 0 ? RP(Number(n)) : 'belum ada');

/** Semua baris riwayat setelan & harga (belum disaring), terbaru di atas. */
export function rsSemua() {
  const out = [];
  // harga katalog: satu baris per terbitan
  ambilHargaTerbit().forEach((t) => { const D = Array.isArray(t.daftar) ? t.daftar : []; if (!D.length) return;
    out.push({ id: 'terbit|' + t.id, tanggal: String(t.tanggal || ''), jam: rsJam(t.jam), oleh: String(t.diubahOleh || t.oleh || ''), golong: 'harga', judul: 'Katalog harga terbit · ' + D.length + ' harga',
      rinci: D.map((x) => String(x.nama || x.kunci || '') + ': ' + rsRp(x.lama) + ' → ' + (Number(x.baru) > 0 ? RP(Number(x.baru)) : 'dihapus')) }); });
  // harga wadah
  (cacheMentah('hargaWadah') || []).forEach((h) => { const judul = 'Harga wadah · ' + String(h.jenis || h.id).replace(/_/g, ' ').replace(/^karungbekas$/, 'karung bekas');
    const R = Array.isArray(h.riwayatUbah) ? h.riwayatUbah : [];
    R.forEach((e, i) => { const w = rsWaktu(e.pada, e.tanggal, e.jam); out.push({ id: 'wadah|' + h.id + '|' + i, tanggal: w.tanggal, jam: w.jam, oleh: String(e.oleh || ''), golong: 'harga', judul,
      rinci: (e.ubah || []).map((u) => (u.k === 'harga' ? 'harga: ' + rsRp(u.dari) + ' → ' + rsRp(u.ke) : rsKolom(u.k) + ': ' + rsNilai(u.dari) + ' → ' + rsNilai(u.ke))) }); });
    if (!R.some((e) => rsWaktu(e.pada, e.tanggal, e.jam).tanggal === String(h.tanggal || '') && rsWaktu(e.pada, e.tanggal, e.jam).jam === rsJam(h.jam)))
      out.push({ id: 'wadah|' + h.id, tanggal: String(h.tanggal || ''), jam: rsJam(h.jam), oleh: String(h.diubahOleh || h.oleh || ''), golong: 'harga', judul, rinci: ['harga: ' + rsRp(h.hargaSebelum) + ' → ' + rsRp(h.harga)] }); });
  // setelan (aturanToko)
  (cacheMentah('aturan') || []).forEach((a) => { const id = String(a.id || ''); if (!id || RS_SISTEM[id] || (RSD_LEWAT['aturanToko/' + id] && id !== 'kunciPeriode')) return;
    const judul = RS_JUDUL[id] || rsKolom(id); const golong = RS_GOLONG_HARGA[id] ? 'harga' : 'setelan';
    const R = Array.isArray(a.riwayatUbah) ? a.riwayatUbah : [];
    R.forEach((e, i) => { const w = rsWaktu(e.pada, e.tanggal, e.jam); out.push({ id: 'atur|' + id + '|' + i, tanggal: w.tanggal, jam: w.jam, oleh: String(e.oleh || ''), golong, judul: judul + (e.baru ? ' · pertama kali disetel' : ''),
      rinci: (e.ubah || []).map((u) => rsKolom(u.k) + ': ' + rsNilai(u.dari) + ' → ' + rsNilai(u.ke)) }); });
    (Array.isArray(a.riwayat) ? a.riwayat : []).forEach((e, i) => { if (!e || typeof e !== 'object') return; const w = rsWaktu(e.pada, e.tanggal, e.jam);
      const rinci = id === 'karungBekas' && (e.dari !== undefined || e.ke !== undefined) ? ['nilai per lembar: ' + rsRp(e.dari) + ' → ' + rsRp(e.ke)]
        : Object.keys(e).filter((k) => ['tanggal', 'jam', 'pada', 'oleh', 'olehUid'].indexOf(k) < 0).slice(0, 6).map((k) => rsKolom(k) + ': ' + rsNilai(typeof e[k] === 'object' && e[k] !== null ? JSON.stringify(e[k]) : e[k]));
      out.push({ id: 'atur|' + id + '|lama|' + i, tanggal: w.tanggal, jam: w.jam, oleh: String(e.oleh || ''), golong, judul, rinci }); });
    // setelan tanpa catatan apa pun (punya riwayat sendiri = sudah tampil di atas): satu baris "terakhir disimpan"
    if (!R.length && !(Array.isArray(a.riwayat) && a.riwayat.length) && id !== 'kunciPeriode') { const w = rsWaktu(a.diubahPada, a.tanggal, a.jam);
      out.push({ id: 'atur|' + id + '|akhir', tanggal: w.tanggal, jam: w.jam, oleh: String(a.diubahOleh || a.oleh || ''), golong, judul, akhir: true,
        rinci: ['terakhir disimpan — isi sebelumnya tidak tercatat (perubahan dicatat dari → ke mulai ' + tanggalPendek(RS_MULAI) + ')'] }); }
  });
  return out.sort((a, b) => (b.tanggal + ' ' + b.jam).localeCompare(a.tanggal + ' ' + a.jam) || b.id.localeCompare(a.id));
}
/** Riwayat tersaring ('' semua · 'harga' · 'setelan'), n baris teratas → { baris, total }. */
export function rsDaftar(saring, n) {
  const S = rsSemua().filter((r) => !saring || r.golong === saring);
  return { baris: S.slice(0, Math.max(1, Number(n) || 40)), total: S.length };
}
