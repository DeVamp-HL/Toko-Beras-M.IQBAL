// FUNGSI SERVER — notifikasi HP owner saat aplikasi tertutup (owner 21 Nov 2026: "Langsung sampai push HP").
// Satu fungsi: begitu tablet menulis permintaan baru ke koleksi persetujuan (titipan uang keluar, pesan, minta nego, usul harga, minta bon), isi
// pendeknya dikirim lewat Firebase Cloud Messaging ke setiap token di koleksi notifOwner (HP / Mac owner yang menyalakan notifikasi di Menu ›
// Toko ini › Perangkat & antrean). Fungsi ini TIDAK menulis data toko: ia hanya membaca persetujuan yang baru lahir dan token, lalu membuang token
// yang sudah mati. Admin SDK melewati rules — yang boleh menulis persetujuan & token tetap diatur firestore.rules (v13).
// Lokasi fungsi WAJIB sama dengan lokasi database Firestore (pemicu Eventarc). functions/pasang.sh membacanya dari server dan menulis LOKASI ke
// functions/.env sebelum deploy; tanpa .env = asia-southeast2 (Jakarta).
'use strict';

const { onDocumentCreated } = require('firebase-functions/v2/firestore');
const { setGlobalOptions } = require('firebase-functions/v2');
const { initializeApp } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const { getMessaging } = require('firebase-admin/messaging');
const { pesanNotif, tokenMati } = require('./pesan');

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
