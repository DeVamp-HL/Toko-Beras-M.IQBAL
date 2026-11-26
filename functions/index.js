// FUNGSI SERVER — notifikasi HP owner saat aplikasi tertutup (owner 21 Nov 2026: "Langsung sampai push HP").
// Satu fungsi: begitu tablet menulis permintaan baru ke koleksi persetujuan (titipan uang keluar, pesan, minta nego, usul harga, minta bon), isi
// pendeknya dikirim lewat Firebase Cloud Messaging ke setiap token di koleksi notifOwner (HP / Mac owner yang menyalakan notifikasi di Menu ›
// Toko ini › Perangkat & antrean). Fungsi ini TIDAK menulis data toko: ia hanya membaca persetujuan yang baru lahir dan token, lalu membuang token
// yang sudah mati. Admin SDK melewati rules — yang boleh menulis persetujuan & token tetap diatur firestore.rules (v13).
// Lokasi fungsi WAJIB sama dengan lokasi database Firestore (pemicu Eventarc). functions/pasang.sh membacanya dari server dan menulis LOKASI ke
// functions/.env sebelum deploy; tanpa .env = asia-southeast2 (Jakarta).
'use strict';

const { onDocumentCreated, onDocumentUpdated } = require('firebase-functions/v2/firestore');
const { setGlobalOptions } = require('firebase-functions/v2');
const { initializeApp } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const { getMessaging } = require('firebase-admin/messaging');
const { pesanNotif, pesanPutus, pesanDariOwner, kirimanTablet, tokenMati } = require('./pesan');
const { onSchedule } = require('firebase-functions/v2/scheduler');
const { ACUAN_ALAMAT, ACUAN_LEVEL, dokTarik } = require('./acuan');

initializeApp();
setGlobalOptions({ region: process.env.LOKASI || 'asia-southeast2', maxInstances: 2, memory: '256MiB' });

exports.kabarOwner = onDocumentCreated('persetujuan/{id}', async (event) => {
  const snap = event.data; if (!snap) return;
  const p = pesanNotif(snap.data(), event.params.id); if (!p) return;
  const q = await getFirestore().collection('notifOwner').get();
  const tujuan = q.docs.map((d) => ({ ref: d.ref, token: d.get('token') })).filter((x) => typeof x.token === 'string' && x.token);
  if (!tujuan.length) return;
  const r = await getMessaging().sendEachForMulticast({
    tokens: tujuan.map((x) => x.token),
    // pesan DATA saja: service worker halaman (baru/notif/sw-notif.js) yang menampilkannya — sama di Chrome, Safari, dan HP
    data: { judul: p.judul, isi: p.isi, tag: p.tag, layar: p.layar },
    webpush: { headers: { Urgency: 'high', TTL: '86400' } },
  });
  const mati = [];
  r.responses.forEach((x, i) => { if (!x.success && x.error && tokenMati(x.error.code)) mati.push(tujuan[i].ref); });
  await Promise.all(mati.map((ref) => ref.delete()));
  console.log('kabarOwner', event.params.id, 'terkirim', r.successCount, 'gagal', r.failureCount, 'token mati dibuang', mati.length);
});

// owner 23 Nov 2026 ("Push penuh lewat Google"): JAWABAN OWNER ke aplikasi tablet — begitu permintaan yang menunggu diputus (disetujui / ditolak /
// dibaca + balasan), isi pendeknya dikirim ke token Android di notifPerangkat milik akun yang memintanya (rules v17). Token kosong (dimatikan dari tablet)
// dilewati; token mati dibuang. Tidak menulis data toko.
exports.kabarTablet = onDocumentUpdated('persetujuan/{id}', async (event) => {
  const ch = event.data; if (!ch || !ch.before || !ch.after) return;
  const p = pesanPutus(ch.before.data(), ch.after.data(), event.params.id); if (!p) return;
  const q = await getFirestore().collection('notifPerangkat').where('uid', '==', p.uid).get();
  const tujuan = q.docs.map((d) => ({ ref: d.ref, token: d.get('token') })).filter((x) => typeof x.token === 'string' && x.token);
  if (!tujuan.length) return;
  const r = await getMessaging().sendEachForMulticast(kirimanTablet(p, tujuan.map((x) => x.token)));
  const mati = [];
  r.responses.forEach((x, i) => { if (!x.success && x.error && tokenMati(x.error.code)) mati.push(tujuan[i].ref); });
  await Promise.all(mati.map((ref) => ref.delete()));
  console.log('kabarTablet', event.params.id, 'terkirim', r.successCount, 'gagal', r.failureCount, 'token mati dibuang', mati.length);
});

// owner 23 Nov 2026 ("gimana gua kirim pesan lewat mac/HP ke tablet?"): PESAN OWNER KE TABLET — begitu owner menulis persetujuan bertindakan 'pesanOwner'
// (lonceng › Kirim pesan ke tablet), isinya dikirim ke token Android di notifPerangkat (semua tablet yang menyalakan notifikasi, atau satu akun bila
// untukUid diisi). Token kosong dilewati, token mati dibuang. Tidak menulis data toko.
exports.kabarDariOwner = onDocumentCreated('persetujuan/{id}', async (event) => {
  const snap = event.data; if (!snap) return;
  const p = pesanDariOwner(snap.data(), event.params.id); if (!p) return;
  const kol = getFirestore().collection('notifPerangkat');
  const q = await (p.untukUid ? kol.where('uid', '==', p.untukUid) : kol).get();
  const tujuan = q.docs.map((d) => ({ ref: d.ref, token: d.get('token') })).filter((x) => typeof x.token === 'string' && x.token);
  if (!tujuan.length) return;
  const r = await getMessaging().sendEachForMulticast(kirimanTablet(p, tujuan.map((x) => x.token)));
  const mati = [];
  r.responses.forEach((x, i) => { if (!x.success && x.error && tokenMati(x.error.code)) mati.push(tujuan[i].ref); });
  await Promise.all(mati.map((ref) => ref.delete()));
  console.log('kabarDariOwner', event.params.id, 'terkirim', r.successCount, 'gagal', r.failureCount, 'token mati dibuang', mati.length);
});

// paket Banding pemasok (owner 26 Nov 2026: "Ketik manual + coba tarik otomatis"): TARIK HARGA ACUAN beras dari Panel Harga Bapanas tiap Jumat 06.00 WIB —
// hasilnya SATU dokumen aturanToko/acuanTarik (dibaca owner saja). Layar Harga & Pemasok › Banding › Harga acuan menampilkannya sebagai USULAN yang owner
// Pakai satu per satu; fungsi ini tidak pernah menulis catatan banding. Gagal (server tidak menjawab / bentuk jawaban tidak dikenali) = status 'gagal' + pesan.
// Hanya membaca alamat publik pemerintah (GET, tanpa kunci rahasia). Bentuk jawaban terlihat 26 Nov 2026 (level 1 produsen & 3 eceran terbukti, 2 tebakan) — acuan.js.
exports.tarikAcuan = onSchedule({ schedule: 'every friday 06:00', timeZone: 'Asia/Jakarta', timeoutSeconds: 120, retryCount: 0 }, async () => {
  const hasil = [];
  for (const L of ACUAN_LEVEL) {
    try {
      const r = await fetch(ACUAN_ALAMAT + '?province_id=&city_id=&level_harga_id=' + L.id, { headers: { Accept: 'application/json' }, signal: AbortSignal.timeout(30000) });
      if (!r.ok) { hasil.push({ tingkat: L.tingkat, tebak: L.tebak, galat: 'server menjawab ' + r.status }); continue; }
      hasil.push({ tingkat: L.tingkat, tebak: L.tebak, json: await r.json() });
    } catch (e) { hasil.push({ tingkat: L.tingkat, tebak: L.tebak, galat: String((e && e.message) || e) }); }
  }
  const d = dokTarik(hasil, new Date());
  await getFirestore().collection('aturanToko').doc('acuanTarik').set(d);
  console.log('tarikAcuan', d.status, d.harga.length, 'harga', d.pesan);
});

// paket Stok minus, label & kepatuhan (owner 26 Nov 2026: "Oh iya adakan/pasang notifikasi"): PUSH PAGI KALENDER KEPATUHAN tiap hari 07.00 WIB — butir kalender
// (aturanToko/kepatuhan; belum ada = butir bawaan) yang belum ditandai dikerjakan (kepatuhanCek) dan sedang dalam jendela ingatnya. Satu notifikasi ringkas ke HP /
// Mac owner (notifOwner, pesan data seperti kabarOwner) dan ke tablet Penjaga laci yang aktif (aksesAkun peran ben → notifPerangkat). Kapan mengirim & isinya:
// functions/patuh.js (murni, diuji). Tidak menulis data toko; token mati dibuang.
const { pesanPatuh, hariWib } = require('./patuh');
exports.kabarPatuh = onSchedule({ schedule: 'every day 07:00', timeZone: 'Asia/Jakarta', timeoutSeconds: 60, retryCount: 0 }, async () => {
  const db = getFirestore(); const W = hariWib(new Date());
  const dok = await db.collection('aturanToko').doc('kepatuhan').get(); const cek = await db.collection('kepatuhanCek').get();
  const p = pesanPatuh(dok.exists ? dok.data() : null, cek.docs.map((d) => d.data()), W.iso, W.hari);
  if (!p.kirim) { console.log('kabarPatuh', W.iso, 'tidak dikirim', p.n, 'urusan dalam jendela'); return; }
  const owner = (await db.collection('notifOwner').get()).docs.map((d) => ({ ref: d.ref, token: d.get('token') })).filter((x) => typeof x.token === 'string' && x.token);
  const ben = (await db.collection('aksesAkun').where('peran', '==', 'ben').where('aktif', '==', true).get()).docs.map((d) => d.id).slice(0, 30);
  const tablet = ben.length ? (await db.collection('notifPerangkat').where('uid', 'in', ben).get()).docs.map((d) => ({ ref: d.ref, token: d.get('token') })).filter((x) => typeof x.token === 'string' && x.token) : [];
  const mati = []; let kirim = 0;
  if (owner.length) { const r = await getMessaging().sendEachForMulticast({ tokens: owner.map((x) => x.token), data: { judul: p.judul, isi: p.isi, tag: p.tag, layar: p.layar }, webpush: { headers: { Urgency: 'normal', TTL: '43200' } } });
    kirim += r.successCount; r.responses.forEach((x, i) => { if (!x.success && x.error && tokenMati(x.error.code)) mati.push(owner[i].ref); }); }
  if (tablet.length) { const r = await getMessaging().sendEachForMulticast(kirimanTablet({ judul: p.judul, isi: p.isi, tag: p.tag, layar: p.layar }, tablet.map((x) => x.token)));
    kirim += r.successCount; r.responses.forEach((x, i) => { if (!x.success && x.error && tokenMati(x.error.code)) mati.push(tablet[i].ref); }); }
  await Promise.all(mati.map((ref) => ref.delete()));
  console.log('kabarPatuh', W.iso, p.n, 'urusan · terkirim', kirim, '· token mati dibuang', mati.length);
});
