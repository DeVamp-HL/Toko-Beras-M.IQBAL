// ABSEN JAGA (owner 28 Nov 2026, rules v27): satu catatan jagaLog tiap orang berhasil masuk di tablet (PIN / sidik jari "Siapa yang jaga?") — nama, peran,
// tanggal & jam setempat tablet. Di sini hanya DIBACA untuk owner: siapa yang jaga dari jam berapa, ganti ke siapa jam berapa. Tidak mengubah upah, kalender
// hari kerja, atau uang apa pun — bahan owner saat mengisi kalender upah. Jam "sampai" = jam orang BERIKUTNYA masuk; jaga terakhir hari itu tidak punya jam
// selesai (tablet tidak mencatat tutup jaga), jadi tertulis "sampai tutup" — bukan ditebak.
import { cacheMentah } from '../data/toko.js';

const jgKeMenit = (j) => { const m = /^([01]\d|2[0-3]):([0-5]\d)$/.exec(String(j || '')); return m ? Number(m[1]) * 60 + Number(m[2]) : null; };
export const jgLama = (menit) => (menit === null || menit === undefined || !(menit >= 0) ? '' : (Math.floor(menit / 60) ? Math.floor(menit / 60) + ' j ' : '') + (menit % 60) + ' m');
/** Nama absen (orang di tablet) cocok dengan nama upah: sama persis, atau nama yang lebih pendek = kata-kata AWAL nama yang lebih panjang ("Pagi" = "Pagi Contoh";
 *  "Karyawan Satu" ≠ "Karyawan Dua"). Huruf besar/kecil diabaikan. */
export function jgSamaNama(a, b) {
  const x = String(a || '').trim().toLowerCase().split(/\s+/).filter(Boolean); const y = String(b || '').trim().toLowerCase().split(/\s+/).filter(Boolean); if (!x.length || !y.length) return false;
  const p = x.length <= y.length ? x : y; const q = p === x ? y : x; return p.every((w, i) => q[i] === w);
}
/** Per tanggal: deret jaga berurutan { nama, peran, mulai, sampai ('' = sampai tutup), menit (null bila sampai tutup), kali (PIN berturut-turut orang yang sama) }. */
export function jgSegmen(daftar) {
  const perHari = {};
  (daftar || cacheMentah('jagaLog')).forEach((d) => { if (!d || !/^\d{4}-\d{2}-\d{2}$/.test(String(d.tanggal || '')) || jgKeMenit(d.jam) === null || !String(d.nama || '').trim()) return; (perHari[d.tanggal] = perHari[d.tanggal] || []).push(d); });
  const out = {};
  Object.keys(perHari).forEach((t) => {
    const L = perHari[t].slice().sort((a, b) => String(a.jam).localeCompare(String(b.jam)) || String(a.pada || '').localeCompare(String(b.pada || '')));
    const seg = [];
    L.forEach((d) => { const k = seg[seg.length - 1]; const nm = String(d.nama).trim();
      if (k && k.nama === nm) { k.kali += 1; return; }
      if (k) k.sampai = d.jam; seg.push({ nama: nm, peran: String(d.peran || ''), mulai: d.jam, sampai: '', kali: 1 }); });
    seg.forEach((x) => { x.menit = x.sampai ? jgKeMenit(x.sampai) - jgKeMenit(x.mulai) : null; });
    out[t] = seg;
  });
  return out;
}
const jgGeser = (iso, n) => { const d = new Date(iso + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
/**
 * Rekap satu orang untuk nHari terakhir s.d. sampaiIso (terbaru dulu). Tiap hari: { tanggal, jaga: [segmen orang itu], teks }. Hari tanpa catatan = teks
 * "tidak ada PIN" (BUKAN "tidak masuk": tablet bisa mati, atau orangnya jaga tanpa PIN). nHari 1–31.
 */
export function jgRekapOrang(nama, sampaiIso, nHari, daftar) {
  const S = jgSegmen(daftar); const n = Math.max(1, Math.min(31, Math.round(Number(nHari) || 7))); const out = [];
  for (let i = 0; i < n; i++) {
    const t = jgGeser(sampaiIso, -i); const semua = S[t] || []; const jaga = semua.filter((x) => jgSamaNama(x.nama, nama));
    const teks = !jaga.length ? (semua.length ? 'tidak jaga (' + semua.map((x) => x.nama).filter((x, j, a) => a.indexOf(x) === j).join(', ') + ')' : 'tidak ada PIN di tablet')
      : jaga.map((x) => x.mulai + '–' + (x.sampai || 'tutup') + (x.menit !== null ? ' (' + jgLama(x.menit) + ')' : '')).join(' · ');
    out.push({ tanggal: t, jaga, teks, ada: jaga.length > 0 });
  }
  return { hari: out, nHari: n, nJaga: out.filter((x) => x.ada).length };
}
