// Sambungan ke Firestore toko. Putaran 1 baca; putaran 2 (19 Sep 2026) MENULIS nota lewat SATU pintu:
// tulisBerkas() = writeBatch — semua dokumen satu nota masuk bersama atau tidak sama sekali (index.html
// menulis satu per satu dengan setDoc; nota tiga baris bisa tersimpan separuh kalau internet putus di tengah).
// Proyek, koleksi, akun, dan atribusi (oleh/perangkat/diubah*) sama dengan index.html; jalan tanpa internet
// diserahkan ke cache tetap Firestore (tulisan mengantre sendiri, terkirim begitu tersambung).
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js';
import { initializeFirestore, persistentLocalCache, persistentMultipleTabManager, collection, onSnapshot, writeBatch, doc }
  from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-firestore.js';
import { getAuth, signInWithEmailAndPassword, onAuthStateChanged, setPersistence, browserLocalPersistence, signOut }
  from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-auth.js';
import { KOLEKSI } from './koleksi.js';
import { pasok, setelSumber, setelPenulis } from './toko.js';

const firebaseConfig = {
  apiKey: 'AIzaSyAQ0DL-RnOa4gwSpvaNf1FMVlSNWla3RzA',
  authDomain: 'toko-beras-m-iqbal.firebaseapp.com',
  projectId: 'toko-beras-m-iqbal',
  storageBucket: 'toko-beras-m-iqbal.firebasestorage.app',
  messagingSenderId: '149034588465',
  appId: '1:149034588465:web:42316713d21c6fc994b810',
};
// index.html = alat OWNER → akun owner. Sandi TIDAK ada di kode dan tidak pernah disimpan di sini;
// diketik owner sekali per perangkat, sesinya disimpan peramban (browserLocalPersistence).
const EMAIL_TOKO = 'owner@tokoberasmiqbal.web.app';

let app = null, db = null, auth = null;
const status = { masuk: false, email: '', koleksiSiap: 0, koleksiTotal: KOLEKSI.length, galat: '', offline: false, menunggu: 0 };
const OLEH_TETAP = 'Owner';                 // sama dengan index.html (alat owner)
const KOLEKSI_LOG = 'logAktivitas';
const pendengarStatus = new Set();
const beriTahu = () => pendengarStatus.forEach((f) => f(Object.assign({}, status)));
let _pendengarKoleksi = [];

export function dengarkanStatus(f) { pendengarStatus.add(f); f(Object.assign({}, status)); return () => pendengarStatus.delete(f); }

export function mulai(saatPerluSandi) {
  if (app) return;
  app = initializeApp(firebaseConfig);
  db = initializeFirestore(app, { localCache: persistentLocalCache({ tabManager: persistentMultipleTabManager() }) });
  auth = getAuth(app);
  setPersistence(auth, browserLocalPersistence).catch(() => {});
  onAuthStateChanged(auth, (u) => {
    const email = String((u && u.email) || '').toLowerCase();
    status.masuk = !!u && email === EMAIL_TOKO; status.email = email;
    if (status.masuk) { pasangPendengar(); setelSumber('firestore', 'Firestore toko'); setelPenulis({ tulis: tulisBerkas, hapus: hapusBerkas }); }
    else saatPerluSandi(u ? 'Perangkat ini masih masuk sebagai ' + email + '. Masukkan sandi OWNER.' : 'Masukkan sandi OWNER. Cukup sekali per perangkat.');
    beriTahu();
  });
  window.addEventListener('online', () => { status.offline = false; beriTahu(); });
  window.addEventListener('offline', () => { status.offline = true; beriTahu(); });
  status.offline = typeof navigator !== 'undefined' && navigator.onLine === false;
}

/** Dipanggil dari formulir masuk; sandi diteruskan ke Firebase Auth lalu dilupakan. */
export async function masuk(sandi) {
  if (!auth) throw new Error('belum mulai');
  try { await signInWithEmailAndPassword(auth, EMAIL_TOKO, sandi); return { ok: true }; }
  catch (e) {
    const kode = String(e.code || '');
    return { ok: false, pesan: /wrong-password|invalid-credential|user-not-found/.test(kode) ? 'Sandi salah. Coba lagi.' : 'Gagal masuk — cek internet, lalu coba lagi.' };
  }
}
export function keluar() { return auth ? signOut(auth) : Promise.resolve(); }

function pasangPendengar() {
  if (_pendengarKoleksi.length) return;   // sudah terpasang
  status.koleksiSiap = 0;
  KOLEKSI.forEach((k) => {
    const lepas = onSnapshot(collection(db, k.nama), { includeMetadataChanges: true }, (snap) => {
      const daftar = []; snap.forEach((d) => daftar.push(d.data()));
      pasok(k.nama, daftar);
      if (!k._siap) { k._siap = true; status.koleksiSiap += 1; }
      // dariCache = angka dari simpanan perangkat (belum tentu terbaru) — layar diberi tahu supaya jujur
      status.offline = !!(snap.metadata && snap.metadata.fromCache && typeof navigator !== 'undefined' && navigator.onLine === false);
      beriTahu();
    }, (err) => {
      status.galat = k.nama + ': ' + String(err && err.code || err);
      if (String(err && err.code || '').includes('permission-denied')) { status.masuk = false; }
      beriTahu();
    });
    _pendengarKoleksi.push(lepas);
  });
}

// ---- identitas perangkat: kunci localStorage SAMA dengan index.html supaya satu HP = satu nama ----
function idPerangkat() {
  let d = null;
  try { d = localStorage.getItem('miqbal_perangkat_v1'); } catch (e) { /* terkunci */ }
  if (!d) { d = 'p-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 7); try { localStorage.setItem('miqbal_perangkat_v1', d); } catch (e) { /* abaikan */ } }
  return d;
}
export function perangkatRingkas() { try { return localStorage.getItem('miqbal_perangkat_label_v1') || idPerangkat(); } catch (e) { return idPerangkat(); } }
const idUnik = () => Date.now() + Math.random();   // bentuk id yang sama dengan index.html
function ringkasDok(d) {
  if (!d) return '';
  const n = (d.hargaTotal !== undefined && d.hargaTotal !== null) ? d.hargaTotal : ((d.nominal !== undefined && d.nominal !== null) ? d.nominal : '');
  const nm = d.namaProduk || d.namaPelanggan || d.namaPegawai || d.pemasok || d.merkSumber || d.keterangan || d.catatan || '';
  return (String(nm).slice(0, 40) + (n !== '' ? ' · Rp' + Math.round(n).toLocaleString('id-ID') : '')).trim();
}
/** Atribusi satu pintu, persis simpanKeFirestore() index.html: pencipta hanya diisi bila kosong, diubah* selalu ditimpa. */
function beriAtribusi(data) {
  const d = Object.assign({}, data);
  if (!d.oleh) d.oleh = OLEH_TETAP;
  if (!d.perangkat) d.perangkat = perangkatRingkas();
  d.diubahOleh = OLEH_TETAP; d.diubahPerangkat = perangkatRingkas(); d.diubahPada = new Date().toISOString();
  Object.keys(d).forEach((k) => { if (d[k] === undefined) delete d[k]; });   // Firestore menolak undefined
  return d;
}

/**
 * Tulis sekumpulan dokumen SEKALIGUS: daftar = [{ koleksi, data }], data.id wajib.
 * Satu writeBatch + satu baris log per dokumen (koleksi logAktivitas, seperti catatLogAktivitas index.html).
 * Mengembalikan { antre: true } segera bila tulisan masuk antrean (offline/menunggu server) — datanya sudah
 * hidup di cache lokal dan onSnapshot sudah menggambarkannya; { ok: true } bila server sudah mengaku.
 */
export async function tulisBerkas(daftar) {
  if (!db) throw new Error('belum tersambung');
  if (!status.masuk) throw new Error('belum masuk sebagai owner');
  const b = writeBatch(db);
  daftar.forEach(({ koleksi, data }) => {
    const d = beriAtribusi(data);
    b.set(doc(db, koleksi, String(d.id)), d);
    const log = { id: idUnik(), pada: new Date().toISOString(), aksi: d.dibatalkan ? 'batalkan' : (d.dikoreksiOleh ? 'tandai-koreksi' : 'tulis'),
      koleksi, idDok: String(d.id), oleh: OLEH_TETAP, perangkat: perangkatRingkas(), ringkas: ringkasDok(d) };
    b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
  });
  status.menunggu += 1; beriTahu();
  const janji = b.commit().then(() => ({ ok: true }))
    .catch((e) => { status.galat = 'tulis ditolak: ' + String((e && e.code) || e); beriTahu(); return { gagal: true, pesan: status.galat }; })
    .finally(() => { status.menunggu = Math.max(0, status.menunggu - 1); beriTahu(); });
  // tunggu sebentar: kalau server mengaku dalam 1,5 detik → ok; kalau tidak → antre (offline / lambat), bukan gagal
  return Promise.race([janji, new Promise((r) => setTimeout(() => r({ antre: true }), 1500))]);
}
export async function hapusBerkas(daftar) {
  if (!db) throw new Error('belum tersambung');
  const b = writeBatch(db);
  daftar.forEach(({ koleksi, id }) => b.delete(doc(db, koleksi, String(id))));
  return Promise.race([b.commit().then(() => ({ ok: true })), new Promise((r) => setTimeout(() => r({ antre: true }), 1500))]);
}

