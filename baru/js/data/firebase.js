// Sambungan ke Firestore toko — BACA SAJA di putaran ini (tidak ada satu pun setDoc/deleteDoc).
// Proyek, koleksi, dan akun sama dengan index.html; yang berbeda: cache tetap Firestore (IndexedDB)
// dipakai apa adanya supaya layar tetap terbaca tanpa internet, tanpa cadangan localStorage buatan sendiri.
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js';
import { initializeFirestore, persistentLocalCache, persistentMultipleTabManager, collection, onSnapshot }
  from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-firestore.js';
import { getAuth, signInWithEmailAndPassword, onAuthStateChanged, setPersistence, browserLocalPersistence, signOut }
  from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-auth.js';
import { KOLEKSI } from './koleksi.js';
import { pasok, setelSumber } from './toko.js';

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
const status = { masuk: false, email: '', koleksiSiap: 0, koleksiTotal: KOLEKSI.length, galat: '', offline: false };
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
    if (status.masuk) { pasangPendengar(); setelSumber('firestore', 'Firestore toko'); }
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
