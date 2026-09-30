// Pemformat angka & tanggal — satu tempat, dipakai semua layar. Bahasa toko: "Rp", "rb", "jt", "kg", "L".
export const RP = (n) => (n < 0 ? '−' : '') + 'Rp' + Math.round(Math.abs(n || 0)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
export const ANGKA = (n) => String(Math.round(n || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
export const RIBU = (n) => (Math.abs(n) < 1000 ? String(Math.round(n)) : Math.abs(n) >= 1e6
  ? (n / 1e6).toFixed(2).replace(/\.?0+$/, '').replace('.', ',') + ' jt'
  : (n / 1000).toFixed(1).replace(/\.0$/, '').replace('.', ',') + ' rb');
export const KG = (n) => (Math.round((n || 0) * 100) / 100).toString().replace('.', ',') + ' kg';
export const LITER = (n) => (Math.round((n || 0) * 10) / 10).toString().replace('.', ',') + ' L';
export const DESIMAL = (n) => (Math.round((n || 0) * 100) / 100).toString().replace('.', ',');
/** KELEBIHAN BAYAR PELANGGAN (audit 39b no. 4) — sisa mesin beku hitungPiutang boleh NEGATIF (pembayaran melebihi sisa, mis. HP kasir yang katalognya
 * basi). Dulu semua pembaca menyaring sisa > 0 / menjepit 0: nama bercap "lunas", hilang dari papan/katalog/Perlu perhatian, neraca turun hanya sebesar
 * sisa (kekayaan naik palsu) — penjaga yang diam. Aturannya SATU di sini (berkas ini ikut di semua bundel uji): ambang −0,5 = tekor pemasok (beku.js);
 * kata sama dengan sisi pemasok/owner. "titipan" sudah berarti lain (titipan tablet, urusan titipan) — jangan dipakai. Fungsi murni: pemanggil memberi
 * hasil hitungPiutang(sampai). Mesin & total uang TIDAK diubah. */
export const LEBIH_AMBANG = -0.5;
/** Sisa di bawah nol dipecah DUA bagian yang artinya beda (tinjauan no. 4 · B1): `uang` = pembayaran melebihi SEMUA bon (uang pelanggan sungguhan —
 * kekayaan neraca naik sebesar ini) · `hapus` = sisanya: hapus buku yang ternyata dibayar juga (BUKAN uang pelanggan; hapus bukunya yang perlu dibalik —
 * jangan dikembalikan). d = baris hitungPiutang / semuaBon: total = kredit + saldoAwal, bayar, dihapus, sisa. */
export function pecahLebih(d) {
  const lebih = d && d.sisa < LEBIH_AMBANG ? -d.sisa : 0; if (!lebih) return { lebih: 0, uang: 0, hapus: 0 };
  const uang = Math.min(lebih, Math.max(0, (Number(d.bayar) || 0) - (Number(d.total) || 0))); return { lebih, uang, hapus: lebih - uang };
}
/** Kalimat per orang: p = pecahLebih(…) (atau { uang, hapus }). */
export function kalimatLebih(p) {
  const u = p.uang > 0.5 ? 'kelebihan bayar ' + RP(p.uang) + ' — uang pelanggan dipegang toko' : '';
  const x = p.hapus > 0.5 ? RP(p.hapus) + ' dibayar padahal sudah dihapus dari buku — hapus bukunya yang perlu dibalik, bukan uang pelanggan' : '';
  return u && x ? u + '; ' + x : u || x;
}
/** Label pendek (daftar nama, tombol, pilihan dokumen). */
export function ringkasLebih(p) { return [p.uang > 0.5 ? 'kelebihan bayar ' + RP(p.uang) : '', p.hapus > 0.5 ? 'hapus buku terbayar ' + RP(p.hapus) : ''].filter(Boolean).join(' · '); }
export function lebihBayarDari(piutang) {
  const orang = (piutang || []).filter((d) => d && d.sisa < LEBIH_AMBANG).map((d) => Object.assign({ kunci: d.kunci, nama: d.nama }, pecahLebih(d)))
    .sort((a, b) => b.lebih - a.lebih || String(a.nama).localeCompare(String(b.nama)));
  const bagian = (k) => { const o = orang.filter((x) => x[k] > 0.5); return { n: o.length, jumlah: o.reduce((a, x) => a + x[k], 0), nama: o.map((x) => x.nama) }; };
  return { orang, n: orang.length, jumlah: orang.reduce((a, x) => a + x.lebih, 0), uang: bagian('uang'), hapus: bagian('hapus') };
}

export function hariIniIso(d) {
  d = d || new Date();
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}
/**
 * TANGGAL YANG DITUTUP (audit 39b no. 1 — aturan sistem lama `tanggalTutupAktif`, perbaikan 21 Agu 2026 sesudah 16–20 Agu omzet Rp0 & selisih palsu):
 * toko tutup malam dan ritual tutup sering lewat tengah malam; tutup SEBELUM jam 12 siang = menutup hari KEMARIN. Tidak ada yang menutup hari yang belum
 * selesai, jadi arah salahnya cuma satu. Dipakai tutup hari (K5), cek wadah tutup toko, dan kertas tutup — bukan untuk tanggal dokumen lain.
 */
export const JAM_BATAS_TUTUP = 12;
export function tanggalTutupAktif(d) { const n = d || new Date(); return n.getHours() < JAM_BATAS_TUTUP ? hariIniIso(new Date(n.getTime() - 86400000)) : hariIniIso(n); }
export function jamKini(d) { d = d || new Date(); return String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0'); }
/** Cap waktu ISO/UTC yang DISIMPAN (dirinciPada, dikoreksiPada, pada, …) → 'HH:MM' JAM DINDING SETEMPAT (WIB di perangkat toko). JANGAN memotong
 *  string ISO (slice(11, 16) / slice(0, 16).replace('T', ' ')) — itu memajang UTC, meleset 7 jam di WIB. Kosong / cacat → ''. */
export function jamSetempat(iso) { if (!iso) return ''; const d = new Date(iso); return isFinite(d.getTime()) ? jamKini(d) : ''; }
/** Cap waktu ISO/UTC → '25 Sep 2026 22:41' setempat (tanggal ikut setempat: 00.00–06.59 WIB bertanggal UTC kemarin). Kosong / cacat → ''. */
export function waktuSetempat(iso) { if (!iso) return ''; const d = new Date(iso); return isFinite(d.getTime()) ? tanggalPendek(hariIniIso(d)) + ' ' + jamKini(d) : ''; }
const BULAN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
export function tanggalPendek(iso) {
  if (!iso) return '';
  const [y, m, d] = String(iso).split('-').map(Number);
  return d + ' ' + (BULAN[m - 1] || '') + (y ? ' ' + y : '');
}
