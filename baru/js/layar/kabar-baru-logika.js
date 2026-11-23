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
  const isi = String(teks || '').replace(/\r/g, '').replace(/[ \t\f\v]+/g, ' ').replace(/ *\n */g, '\n').replace(/\n{3,}/g, '\n\n').trim(); if (!isi) return { tolak: 'Tulis dulu pesannya' };   // baris baru dipertahankan (obrolan)
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
  // obrolan (owner 23 Nov 2026): pesan dibaca TANPA balasan = centang dua di obrolan, bukan kabar berbunyi
  const putus = Object.keys(baru.milik).filter((id) => lama.milik[id] && lama.milik[id].status === 'menunggu' && baru.milik[id].status !== 'menunggu'
    && !(baru.milik[id].tindakan === TP_PESAN && baru.milik[id].status === 'dibaca' && !baru.milik[id].balasan)).map((id) => {
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
// ---- OBROLAN (owner 23 Nov 2026: "notifikasi & kabar di tablet dan Mac/HP bisa balas pesan … seperti WhatsApp … chattingan" — pilihan "Obrolan di
// lonceng"). TIDAK ada koleksi baru: satu utas owner ↔ tablet disusun dari dokumen persetujuan yang sudah ada —
//  - pesan tablet → owner = tindakan 'pesan' (tpSusunPesan; status menunggu = ✓ terkirim, dibaca = ✓✓ dibaca owner),
//  - pesan owner → tablet = tindakan 'pesanOwner' (kbSusunPesanOwner; status terkirim = ✓; tablet tidak bisa menulis "dibaca" ke server),
//  - balasan lama (pesan ditandai dibaca + balasan, jalur Uang › titipan) = gelembung owner pada jam putusannya.
// Owner: semua pesan tablet. Akun tablet: pesan milik akun ini + semua pesan owner. Belum dibaca — owner: pesan tablet yang masih MENUNGGU (keadaan server,
// jadi membaca di HP ikut membersihkan Mac); tablet: pesan owner yang belum dibuka di perangkat ini (peta dilihat, sama dengan kabar).
export const KB_MAKS_OBROLAN = 80;
const urutWaktu = (tgl, jam, iso) => String(tgl || '') + ' ' + String(jam || '') + ' ' + String(iso || '');
const HARI_INI = 'Hari ini'; const KEMARIN = 'Kemarin';
function kbLabelHari(tgl, hariIni) {
  if (!tgl) return ''; if (hariIni && tgl === hariIni) return HARI_INI;
  if (hariIni) { const d = new Date(hariIni + 'T00:00:00Z'); if (isFinite(d.getTime())) { d.setUTCDate(d.getUTCDate() - 1); if (d.toISOString().slice(0, 10) === tgl) return KEMARIN; } }
  return tanggalPendek(tgl);
}
/** Satu gelembung. dari 'owner' | 'tablet'; centang 1 = terkirim, 2 = dibaca owner (hanya pesan tablet). */
const gelembung = (o) => ({ id: o.id, kunci: o.kunci || o.id, dari: o.dari, nama: o.nama, teks: String(o.teks || '').replace(/\r/g, '').trim(), tanggal: String(o.tanggal || ''),
  jam: String(o.jam || ''), urut: o.urut, status: o.status, centang: o.centang || 1, baru: !!o.baru, lihat: !!o.lihat });
/**
 * Isi lonceng untuk akun ini. daftar = persetujuan (bawaan: cache), dilihat = { id: status } yang sudah dibuka di perangkat ini, hariIni = 'YYYY-MM-DD' (label hari
 * obrolan). Hasil { owner, daftar (KABAR: permintaan selain pesan, terbaru dulu, ≤ KB_MAKS), obrolan (utas, terlama dulu, ≤ KB_MAKS_OBROLAN), n (belum dibuka,
 * kabar + obrolan), nKabar, nObrolan, menunggu, lebih, lebihObrolan, belumDibaca (owner: id pesan tablet yang menunggu), lihat / lihatObrolan / dilihat (kbTandai) }.
 */
export function kbLonceng(akun, daftar, dilihat, hariIni) {
  const D = daftar || cacheMentah('persetujuan'); const L = dilihat || {}; const owner = !!akun && akun.jenis === 'owner'; const uid = String((akun && akun.uid) || '');
  const out = []; const ob = [];
  D.forEach((m) => {
    if (!m || m.id === undefined) return; const id = String(m.id); const st = m.status || 'menunggu'; const t = String(m.tindakan || '');
    if (t === KB_PESAN_OWNER) {   // pesan owner: owner = gelembung sendiri; tablet = masuk (belum dibuka bila peta dilihat belum mencatatnya)
      ob.push(gelembung({ id, dari: 'owner', nama: 'Owner', teks: m.teks, tanggal: m.tanggal, jam: m.jam, urut: urutWaktu(m.tanggal, m.jam, m.dibuatPada), status: st, baru: !owner && L[id] !== st, lihat: !owner }));
      return;
    }
    if (t === TP_PESAN) {
      if (!owner && (!uid || uidPeminta(m) !== uid)) return;
      ob.push(gelembung({ id, dari: 'tablet', nama: m.dari || 'Tablet', teks: m.teks, tanggal: m.tanggal, jam: m.jam, urut: urutWaktu(m.tanggal, m.jam, m.pada), status: st,
        centang: st === 'menunggu' ? 1 : 2, baru: owner && st === 'menunggu' }));
      const bal = String(m.balasan || '').trim();
      if (bal && st !== 'menunggu') ob.push(gelembung({ id, kunci: id + '-balas', dari: 'owner', nama: 'Owner', teks: bal, tanggal: m.diputusTanggal || m.tanggal, jam: m.diputusJam || m.jam,
        urut: urutWaktu(m.diputusTanggal || m.tanggal, m.diputusJam || m.jam, m.diputusPada), status: st, baru: !owner && L[id] !== st, lihat: !owner }));
      return;
    }
    if (owner) {
      if (st !== 'menunggu') return;
      out.push({ id, status: st, tindakan: t, judul: KB_JUDUL[t] || 'Permintaan dari tablet', isi: kbIsi(m), alasan: '', balasan: '', waktu: waktuTampil(m.tanggal, m.jam), urut: urutBuat(m),
        layar: layarOwner(m), bisaBalas: t === TP_KABAR, baru: L[id] !== st });
      return;
    }
    if (!uid || uidPeminta(m) !== uid) return;
    const putus = st !== 'menunggu';
    out.push({ id, status: st, tindakan: t, judul: (KB_JUDUL[t] || 'Permintaan') + ' · ' + (KB_STATUS[st] || st), isi: kbIsi(m), alasan: String(m.alasanTolak || ''), balasan: String(m.balasan || ''),
      waktu: putus ? waktuTampil(m.diputusTanggal || m.tanggal, m.diputusJam || m.jam) : waktuTampil(m.tanggal, m.jam), urut: putus ? urutPutus(m) : urutBuat(m), layar: 'menu', bisaBalas: false, baru: putus && L[id] !== st });
  });
  out.sort((a, b) => (a.urut < b.urut ? 1 : a.urut > b.urut ? -1 : 0));
  ob.sort((a, b) => (a.urut < b.urut ? -1 : a.urut > b.urut ? 1 : 0));
  const lihat = {}; out.forEach((x) => { lihat[x.id] = x.status; });
  const lihatObrolan = {}; ob.forEach((x) => { if (x.lihat) lihatObrolan[x.id] = x.status; });
  const nKabar = out.filter((x) => x.baru).length; const nObrolan = ob.filter((x) => x.baru).length;
  const utas = ob.slice(Math.max(0, ob.length - KB_MAKS_OBROLAN));
  utas.forEach((x, i) => { const s = utas[i - 1]; x.pisah = !s || s.tanggal !== x.tanggal ? kbLabelHari(x.tanggal, hariIni) : ''; x.namaTampil = !s || !!x.pisah || s.dari !== x.dari || s.nama !== x.nama; });
  return { owner, daftar: out.slice(0, KB_MAKS), obrolan: utas, n: nKabar + nObrolan, nKabar, nObrolan, menunggu: out.filter((x) => x.status === 'menunggu').length,
    lebih: Math.max(0, out.length - KB_MAKS), lebihObrolan: ob.length - utas.length,
    belumDibaca: owner ? ob.filter((x) => x.dari === 'tablet' && x.status === 'menunggu').map((x) => x.id) : [], lihat, lihatObrolan, dilihat: L };
}
/**
 * Isi lonceng yang tampil = sudah dibuka. bagian 'kabar' | 'obrolan' = hanya bagian itu (tab yang sedang dilihat); kosong = keduanya. Peta baru { id: status }:
 * catatan lama untuk id yang masih ada ikut dibawa, id yang sudah tidak ada terbuang.
 */
export function kbTandai(isi, bagian) {
  const I = isi || {}; const L = I.dilihat || {}; const kab = I.lihat || {}; const ob = I.lihatObrolan || {}; const out = {};
  Object.keys(kab).concat(Object.keys(ob)).forEach((id) => { if (L[id] !== undefined) out[id] = L[id]; });
  if (bagian !== 'obrolan') Object.assign(out, kab);
  if (bagian !== 'kabar') Object.assign(out, ob);
  return out;
}
/** Peta dilihat tersimpan untuk akun `uid` (teks localStorage → peta, rusak = null = belum pernah: semua yang ada sekarang dianggap sudah dibuka). */
export function kbBacaLihat(teks, uid) {
  try { const x = JSON.parse(teks || 'null'); const p = x && typeof x === 'object' ? x[String(uid || '')] : null; return p && typeof p === 'object' ? p : null; } catch (e) { return null; }
}
/** Teks localStorage baru sesudah peta akun `uid` diganti (akun lain di perangkat ini tetap). */
export function kbTulisLihat(teks, uid, peta) {
  let x = {}; try { x = JSON.parse(teks || '{}') || {}; } catch (e) { x = {}; } if (typeof x !== 'object' || Array.isArray(x)) x = {};
  x[String(uid || '')] = peta || {}; return JSON.stringify(x);
}
