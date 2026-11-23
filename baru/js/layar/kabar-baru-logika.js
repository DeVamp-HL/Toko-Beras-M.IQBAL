// NOTIFIKASI DALAM APLIKASI (owner 21 Nov 2026: "kalo bisa ada notifikasi di aplikasi ini"). Logika tanpa DOM; awalan kb.
// Sumbernya satu: koleksi persetujuan (permintaan dari tablet ke owner) yang sudah didengarkan aplikasi.
//  - OWNER (HP / Mac): permintaan BARU yang menunggu — titipan uang keluar, pesan, minta nego, usul harga pelanggan, minta bon lewat batas.
//  - AKUN TABLET: permintaan MILIK akun ini yang baru diputus owner — disetujui / ditolak (beserta alasannya) / pesan dibaca (beserta balasannya).
// Pembanding = sidik sebelumnya. Sidik pertama sesudah data lengkap TIDAK berbunyi (membuka aplikasi bukan kabar baru). Bunyi, getar, lampu CPad, dan pita
// di layar ada di app.js; push ke HP saat aplikasi tertutup dikirim fungsi server (functions/), bukan dari sini.
import { cacheMentah } from '../data/toko.js';
import { RP, tanggalPendek } from '../inti/format.js';
import { tpTeks, TP_TINDAKAN, TP_PESAN, TP_KABAR, TP_BATAS } from './titipan-logika.js';

export const KB_JUDUL = { uangKeluar: 'Titipan uang keluar', pesan: 'Pesan dari tablet', barangMasuk: 'Barang masuk dari tablet', hitungLaci: 'Hitungan laci dari tablet', nego: 'Minta nego harga', hargaPelanggan: 'Usul harga pelanggan', kredit: 'Minta bon lewat batas kredit', pesanOwner: 'Pesan dari owner' };
// owner 23 Nov 2026 ("gimana gua kirim pesan lewat mac/HP ke tablet?"): PESAN OWNER KE TABLET — dokumen persetujuan bertindakan 'pesanOwner', status
// 'terkirim' (BUKAN 'menunggu': tidak masuk daftar menunggu owner, tidak memicu push ke HP owner, tidak ikut papan Persetujuan). Rules tetap v17: owner
// menulis persetujuan, akun tablet (ben/karyawan) membacanya. Tablet tidak bisa menandai dibaca di server (update = owner) — "sudah dibuka" dicatat
// lonceng per perangkat. Push ke tablet = fungsi server kabarDariOwner (functions/).
export const KB_PESAN_OWNER = 'pesanOwner';
export const KB_STATUS_TERKIRIM = 'terkirim';
/** Susun pesan owner untuk tablet. teks 1–500 huruf (TP_BATAS.pesan). w = waktuSekarang(). Hasil { dokumen, patch } atau { tolak }. */
export function kbSusunPesanOwner(teks, w, akun) {
  if (!akun || akun.jenis !== 'owner') return { tolak: 'Pesan ke tablet hanya dari akun owner' };
  const isi = String(teks || '').replace(/\s+/g, ' ').trim(); if (!isi) return { tolak: 'Tulis dulu pesannya' };
  if (isi.length > TP_BATAS.pesan) return { tolak: 'Pesan terlalu panjang — paling banyak ' + TP_BATAS.pesan + ' huruf' };
  const data = { id: w.idUnik(), tindakan: KB_PESAN_OWNER, status: KB_STATUS_TERKIRIM, untuk: 'tablet', teks: isi, dari: 'Owner', tanggal: w.tanggal, jam: w.jam, dibuatPada: w.kini };
  return { dokumen: [{ koleksi: 'persetujuan', data }], patch: { kabar: 'Pesan terkirim ke tablet — muncul di lonceng & bilah notifikasi tablet', kabarAwas: false } };
}
const KB_PUTUS = { disetujui: 'disetujui owner', ditolak: 'DITOLAK owner', dibaca: 'dibaca owner' };
const uidPeminta = (m) => String(m.mintaUid || m.negoUid || m.usulUid || '');
/** Isi satu permintaan untuk kabar (tanpa kolom yang tidak ada). */
export function kbIsi(m) {
  const dari = m.dari ? m.dari + ': ' : '';
  if (m.tindakan === TP_TINDAKAN) return dari + tpTeks(m);
  if (m.tindakan === TP_PESAN || m.tindakan === TP_KABAR || m.tindakan === KB_PESAN_OWNER) return dari + String(m.teks || '').replace(/\s+/g, ' ').slice(0, 120);
  // owner 22 Nov 2026 (paket ④): hitungan laci — jumlah dihitung & yang dipindah ke brankas (tanpa selisih: tablet hitung buta, owner melihatnya di Tutup hari)
  if (m.tindakan === 'hitungLaci') return dari + 'laci ' + tanggalPendek(m.tanggal || '') + ' dihitung ' + RP(Math.round(Number(m.hitung) || 0)) + (Number(m.amankan) ? ' · ' + RP(Math.round(Number(m.amankan))) + ' ke brankas' : '');
  const n = Math.round(Number(m.nominal) || 0);
  return dari + (String(m.teks || '').slice(0, 100) || KB_JUDUL[m.tindakan] || 'permintaan') + (n > 0 && !/Rp/.test(String(m.teks || '')) ? ' · ' + RP(n) : '');
}
/** Layar tujuan ketukan: titipan & pesan → Uang (owner) / Menu (tablet); lainnya → Menu (papan Persetujuan). */
const layarOwner = (m) => (m.tindakan === TP_TINDAKAN || m.tindakan === TP_PESAN || m.tindakan === TP_KABAR || m.tindakan === 'hitungLaci' ? 'uang' : 'menu');

/** Sidik keadaan sekarang untuk akun ini. owner: { menunggu: { id: kabar } } · tablet: { milik: { id: { status, kabar } } }. */
export function kbSidik(akun, daftar) {
  const D = daftar || cacheMentah('persetujuan'); const owner = !!akun && akun.jenis === 'owner'; const uid = String((akun && akun.uid) || '');
  const out = { owner, uid, menunggu: {}, milik: {}, pesan: {}, n: 0 };
  D.forEach((m) => {
    if (!m || m.id === undefined) return; const id = String(m.id); const st = m.status || 'menunggu';
    if (owner) { if (st === 'menunggu') { out.menunggu[id] = { judul: KB_JUDUL[m.tindakan] || 'Permintaan dari tablet', isi: kbIsi(m), layar: layarOwner(m), tindakan: String(m.tindakan || '') }; out.n += 1; } return; }
    if (m.tindakan === KB_PESAN_OWNER) { out.pesan[id] = { isi: String(m.teks || '').replace(/\s+/g, ' ').slice(0, 160) }; return; }   // owner 23 Nov 2026: pesan owner untuk tablet
    if (uid && uidPeminta(m) === uid) out.milik[id] = { status: st, tindakan: String(m.tindakan || ''), isi: kbIsi(m), alasan: String(m.alasanTolak || ''), balasan: String(m.balasan || '') };
  });
  return out;
}
/** Kabar baru = beda sidik lama → baru. lama null / akun lain = belum ada pembanding → tidak berbunyi. */
export function kbBanding(lama, baru) {
  if (!lama || !baru || lama.owner !== baru.owner || lama.uid !== baru.uid) return [];
  if (baru.owner) return Object.keys(baru.menunggu).filter((id) => !lama.menunggu[id]).map((id) => Object.assign({ id, jenis: 'masuk' }, baru.menunggu[id]));
  const putus = Object.keys(baru.milik).filter((id) => lama.milik[id] && lama.milik[id].status === 'menunggu' && baru.milik[id].status !== 'menunggu').map((id) => {
    const x = baru.milik[id]; const judul = (KB_JUDUL[x.tindakan] || 'Permintaan') + ' ' + (KB_PUTUS[x.status] || x.status);
    return { id, jenis: 'putus', status: x.status, judul, isi: x.isi + (x.alasan ? ' — alasan: ' + x.alasan : '') + (x.balasan ? ' — balasan: ' + x.balasan : ''), layar: 'menu' };
  });
  // owner 23 Nov 2026: pesan owner yang BARU muncul (tidak ada di sidik lama) = kabar masuk untuk tablet
  const pesan = Object.keys(baru.pesan || {}).filter((id) => !(lama.pesan || {})[id]).map((id) => ({ id, jenis: 'masuk', judul: KB_JUDUL.pesanOwner, isi: baru.pesan[id].isi, layar: 'menu' }));
  return pesan.concat(putus);
}
/** Satu kalimat untuk beberapa kabar sekaligus (mis. data menyusul sesudah internet kembali). */
export function kbRingkas(ev) {
  if (!ev.length) return null;
  if (ev.length === 1) return { judul: ev[0].judul, isi: ev[0].isi, layar: ev[0].layar, awas: ev[0].status === 'ditolak' };
  return { judul: ev.length + ' kabar baru', isi: ev.slice(0, 3).map((e) => e.judul).join(' · ') + (ev.length > 3 ? ' · …' : ''), layar: ev[0].layar, awas: ev.some((e) => e.status === 'ditolak') };
}

// ---- LONCENG (owner 23 Nov 2026: "ada ikon notifikasi untuk pesan di aplikasi sistem mac/hp/tablet" — pilihan "Lonceng + balas langsung") ----
// Ikon lonceng di kepala tiap layar; angka = kabar yang BELUM DIBUKA di perangkat ini (peta dilihat { id: status } per akun di localStorage).
//  - OWNER: semua permintaan yang menunggu (pesan, titipan, barang masuk, hitungan laci, nego, usul harga, minta bon). Pesan & kabar barang masuk bisa
//    langsung ditandai dibaca + dibalas dari lonceng (lonceng.js → tpSusunPutus, pintu yang sama dengan Uang). Lainnya = tombol buka layarnya.
//  - AKUN TABLET: permintaan milik akun ini, yang menunggu dan yang sudah diputus owner (alasan tolak / balasan ikut). Baru = putusan yang belum dibuka.
export const KB_LIHAT = 'miqbal_lonceng_v1';
export const KB_MAKS = 30;
const KB_STATUS = { menunggu: 'menunggu owner', disetujui: 'disetujui', ditolak: 'DITOLAK', dibaca: 'dibaca owner' };
export const KB_NAMA_LAYAR = { uang: 'Uang', menu: 'Menu', jual: 'Jual' };
const urutBuat = (m) => String(m.tanggal || '') + ' ' + String(m.jam || '');
const urutPutus = (m) => String(m.diputusTanggal || m.tanggal || '') + ' ' + String(m.diputusJam || m.jam || '');
const waktuTampil = (tgl, jam) => (tgl ? tanggalPendek(tgl) : '') + (jam ? ' ' + jam : '');
/**
 * Isi lonceng untuk akun ini. daftar = persetujuan (bawaan: cache), dilihat = { id: status } yang sudah dibuka di perangkat ini.
 * Hasil { owner, daftar: [{ id, status, tindakan, judul, isi, alasan, balasan, waktu, layar, bisaBalas, baru }] (terbaru dulu, paling banyak KB_MAKS),
 * n (belum dibuka, dari SEMUA), menunggu, lebih, lihat: { id: status } semua (untuk kbTandai) }.
 */
export function kbLonceng(akun, daftar, dilihat) {
  const D = daftar || cacheMentah('persetujuan'); const L = dilihat || {}; const owner = !!akun && akun.jenis === 'owner'; const uid = String((akun && akun.uid) || '');
  const out = []; const terkirim = [];
  D.forEach((m) => {
    if (!m || m.id === undefined) return; const id = String(m.id); const st = m.status || 'menunggu'; const t = String(m.tindakan || '');
    if (t === KB_PESAN_OWNER) {   // owner 23 Nov 2026: owner = daftar "terkirim" (tidak dihitung); tablet = kabar masuk (dihitung bila belum dibuka)
      const x = { id, status: st, tindakan: t, judul: KB_JUDUL.pesanOwner, isi: String(m.teks || ''), alasan: '', balasan: '', waktu: waktuTampil(m.tanggal, m.jam), urut: urutBuat(m), layar: 'menu', bisaBalas: false, baru: !owner && L[id] !== st };
      (owner ? terkirim : out).push(x); return;
    }
    if (owner) {
      if (st !== 'menunggu') return;
      out.push({ id, status: st, tindakan: t, judul: KB_JUDUL[t] || 'Permintaan dari tablet', isi: kbIsi(m), alasan: '', balasan: '', waktu: waktuTampil(m.tanggal, m.jam), urut: urutBuat(m),
        layar: layarOwner(m), bisaBalas: t === TP_PESAN || t === TP_KABAR, baru: L[id] !== st });
      return;
    }
    if (!uid || uidPeminta(m) !== uid) return;
    const putus = st !== 'menunggu';
    out.push({ id, status: st, tindakan: t, judul: (KB_JUDUL[t] || 'Permintaan') + ' · ' + (KB_STATUS[st] || st), isi: kbIsi(m), alasan: String(m.alasanTolak || ''), balasan: String(m.balasan || ''),
      waktu: putus ? waktuTampil(m.diputusTanggal || m.tanggal, m.diputusJam || m.jam) : waktuTampil(m.tanggal, m.jam), urut: putus ? urutPutus(m) : urutBuat(m), layar: 'menu', bisaBalas: false, baru: putus && L[id] !== st });
  });
  out.sort((a, b) => (a.urut < b.urut ? 1 : a.urut > b.urut ? -1 : 0));
  const lihat = {}; out.forEach((x) => { lihat[x.id] = x.status; });
  terkirim.sort((a, b) => (a.urut < b.urut ? 1 : a.urut > b.urut ? -1 : 0));
  return { owner, daftar: out.slice(0, KB_MAKS), n: out.filter((x) => x.baru).length, menunggu: out.filter((x) => x.status === 'menunggu').length, lebih: Math.max(0, out.length - KB_MAKS), lihat,
    terkirim: terkirim.slice(0, 3) };
}
/** Semua isi lonceng sekarang = sudah dibuka. Peta baru { id: status } — id yang sudah tidak ada ikut terbuang. */
export function kbTandai(isi) { return Object.assign({}, (isi && isi.lihat) || {}); }
/** Peta dilihat tersimpan untuk akun `uid` (teks localStorage → peta, rusak = null = belum pernah: semua yang ada sekarang dianggap sudah dibuka). */
export function kbBacaLihat(teks, uid) {
  try { const x = JSON.parse(teks || 'null'); const p = x && typeof x === 'object' ? x[String(uid || '')] : null; return p && typeof p === 'object' ? p : null; } catch (e) { return null; }
}
/** Teks localStorage baru sesudah peta akun `uid` diganti (akun lain di perangkat ini tetap). */
export function kbTulisLihat(teks, uid, peta) {
  let x = {}; try { x = JSON.parse(teks || '{}') || {}; } catch (e) { x = {}; } if (typeof x !== 'object' || Array.isArray(x)) x = {};
  x[String(uid || '')] = peta || {}; return JSON.stringify(x);
}
