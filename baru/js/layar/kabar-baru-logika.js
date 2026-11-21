// NOTIFIKASI DALAM APLIKASI (owner 21 Nov 2026: "kalo bisa ada notifikasi di aplikasi ini"). Logika tanpa DOM; awalan kb.
// Sumbernya satu: koleksi persetujuan (permintaan dari tablet ke owner) yang sudah didengarkan aplikasi.
//  - OWNER (HP / Mac): permintaan BARU yang menunggu — titipan uang keluar, pesan, minta nego, usul harga pelanggan, minta bon lewat batas.
//  - AKUN TABLET: permintaan MILIK akun ini yang baru diputus owner — disetujui / ditolak (beserta alasannya) / pesan dibaca (beserta balasannya).
// Pembanding = sidik sebelumnya. Sidik pertama sesudah data lengkap TIDAK berbunyi (membuka aplikasi bukan kabar baru). Bunyi, getar, lampu CPad, dan pita
// di layar ada di app.js; push ke HP saat aplikasi tertutup dikirim fungsi server (functions/), bukan dari sini.
import { cacheMentah } from '../data/toko.js';
import { RP } from '../inti/format.js';
import { tpTeks, TP_TINDAKAN, TP_PESAN } from './titipan-logika.js';

export const KB_JUDUL = { uangKeluar: 'Titipan uang keluar', pesan: 'Pesan dari tablet', nego: 'Minta nego harga', hargaPelanggan: 'Usul harga pelanggan', kredit: 'Minta bon lewat batas kredit' };
const KB_PUTUS = { disetujui: 'disetujui owner', ditolak: 'DITOLAK owner', dibaca: 'dibaca owner' };
const uidPeminta = (m) => String(m.mintaUid || m.negoUid || m.usulUid || '');
/** Isi satu permintaan untuk kabar (tanpa kolom yang tidak ada). */
export function kbIsi(m) {
  const dari = m.dari ? m.dari + ': ' : '';
  if (m.tindakan === TP_TINDAKAN) return dari + tpTeks(m);
  if (m.tindakan === TP_PESAN) return dari + String(m.teks || '').replace(/\s+/g, ' ').slice(0, 120);
  const n = Math.round(Number(m.nominal) || 0);
  return dari + (String(m.teks || '').slice(0, 100) || KB_JUDUL[m.tindakan] || 'permintaan') + (n > 0 && !/Rp/.test(String(m.teks || '')) ? ' · ' + RP(n) : '');
}
/** Layar tujuan ketukan: titipan & pesan → Uang (owner) / Menu (tablet); lainnya → Menu (papan Persetujuan). */
const layarOwner = (m) => (m.tindakan === TP_TINDAKAN || m.tindakan === TP_PESAN ? 'uang' : 'menu');

/** Sidik keadaan sekarang untuk akun ini. owner: { menunggu: { id: kabar } } · tablet: { milik: { id: { status, kabar } } }. */
export function kbSidik(akun, daftar) {
  const D = daftar || cacheMentah('persetujuan'); const owner = !!akun && akun.jenis === 'owner'; const uid = String((akun && akun.uid) || '');
  const out = { owner, uid, menunggu: {}, milik: {}, n: 0 };
  D.forEach((m) => {
    if (!m || m.id === undefined) return; const id = String(m.id); const st = m.status || 'menunggu';
    if (owner) { if (st === 'menunggu') { out.menunggu[id] = { judul: KB_JUDUL[m.tindakan] || 'Permintaan dari tablet', isi: kbIsi(m), layar: layarOwner(m), tindakan: String(m.tindakan || '') }; out.n += 1; } return; }
    if (uid && uidPeminta(m) === uid) out.milik[id] = { status: st, tindakan: String(m.tindakan || ''), isi: kbIsi(m), alasan: String(m.alasanTolak || ''), balasan: String(m.balasan || '') };
  });
  return out;
}
/** Kabar baru = beda sidik lama → baru. lama null / akun lain = belum ada pembanding → tidak berbunyi. */
export function kbBanding(lama, baru) {
  if (!lama || !baru || lama.owner !== baru.owner || lama.uid !== baru.uid) return [];
  if (baru.owner) return Object.keys(baru.menunggu).filter((id) => !lama.menunggu[id]).map((id) => Object.assign({ id, jenis: 'masuk' }, baru.menunggu[id]));
  return Object.keys(baru.milik).filter((id) => lama.milik[id] && lama.milik[id].status === 'menunggu' && baru.milik[id].status !== 'menunggu').map((id) => {
    const x = baru.milik[id]; const judul = (KB_JUDUL[x.tindakan] || 'Permintaan') + ' ' + (KB_PUTUS[x.status] || x.status);
    return { id, jenis: 'putus', status: x.status, judul, isi: x.isi + (x.alasan ? ' — alasan: ' + x.alasan : '') + (x.balasan ? ' — balasan: ' + x.balasan : ''), layar: 'menu' };
  });
}
/** Satu kalimat untuk beberapa kabar sekaligus (mis. data menyusul sesudah internet kembali). */
export function kbRingkas(ev) {
  if (!ev.length) return null;
  if (ev.length === 1) return { judul: ev[0].judul, isi: ev[0].isi, layar: ev[0].layar, awas: ev[0].status === 'ditolak' };
  return { judul: ev.length + ' kabar baru', isi: ev.slice(0, 3).map((e) => e.judul).join(' · ') + (ev.length > 3 ? ' · …' : ''), layar: ev[0].layar, awas: ev.some((e) => e.status === 'ditolak') };
}
