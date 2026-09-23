// Sambungan ke Firestore toko. Putaran 1 baca; putaran 2 (19 Sep 2026) MENULIS nota lewat SATU pintu:
// tulisBerkas() = writeBatch — semua dokumen satu nota masuk bersama atau tidak sama sekali (index.html
// menulis satu per satu dengan setDoc; nota tiga baris bisa tersimpan separuh kalau internet putus di tengah).
// Proyek, koleksi, akun, dan atribusi (oleh/perangkat/diubah*) sama dengan index.html; jalan tanpa internet
// diserahkan ke cache tetap Firestore (tulisan mengantre sendiri, terkirim begitu tersambung).
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js';
import { initializeFirestore, persistentLocalCache, persistentMultipleTabManager, collection, onSnapshot, writeBatch, doc, setDoc, query, orderBy, limit, where, getDocs, waitForPendingWrites }
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
// antre = catatan yang sudah tersimpan di perangkat ini tapi BELUM diakui server (hasPendingWrites) — putaran 14, layar Sistem → Perangkat
const status = { masuk: false, email: '', koleksiSiap: 0, koleksiTotal: KOLEKSI.length, galat: '', offline: false, menunggu: 0, antre: [] };
const _antrePerKoleksi = {};
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
    if (status.masuk) { pasangPendengar(); setelSumber('firestore', 'Firestore toko'); setelPenulis({ tulis: tulisBerkas, hapus: hapusBerkas, arsipkan: arsipkanBerkas, bacaArsip: bacaArsipBerkas, pulihkan: pulihkanBerkas }); pasangDenyut(); }
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
    // koleksi berbatas (jejak logAktivitas): hanya `batas` baris terbaru yang dibaca — bukan seluruh riwayat tulisan
    const sumber = k.batas ? query(collection(db, k.nama), orderBy(k.urut, 'desc'), limit(k.batas)) : collection(db, k.nama);
    const lepas = onSnapshot(sumber, { includeMetadataChanges: true }, (snap) => {
      const daftar = [], tunda = [];
      snap.forEach((d) => { const x = d.data(); daftar.push(x); if (d.metadata && d.metadata.hasPendingWrites) tunda.push({ koleksi: k.nama, id: d.id, ringkas: ringkasDok(x), pada: x.diubahPada || x.pada || '', oleh: x.oleh || x.diubahOleh || '', perangkat: x.diubahPerangkat || x.perangkat || '' }); });
      _antrePerKoleksi[k.nama] = tunda; status.antre = Object.keys(_antrePerKoleksi).reduce((a, n) => a.concat(_antrePerKoleksi[n]), []);
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
export { idPerangkat };
export function namaiPerangkat(nama) { try { if (String(nama || '').trim()) localStorage.setItem('miqbal_perangkat_label_v1', String(nama).trim()); else localStorage.removeItem('miqbal_perangkat_label_v1'); } catch (e) { /* abaikan */ } kirimDenyut(true); }
// ---- siapa yang mencatat di perangkat ini (SS1, sensus 61) & lokasi perangkat ini (SS4, sensus 65) — keduanya setelan PER PERANGKAT ----
const KUNCI_PEMEGANG = 'miqbal_baru_pemegang', KUNCI_LOKASI = 'miqbal_baru_lokasi';
export function pemegangPerangkat() { try { return localStorage.getItem(KUNCI_PEMEGANG) || OLEH_TETAP; } catch (e) { return OLEH_TETAP; } }
export function setelPemegang(nama) { try { if (nama && nama !== OLEH_TETAP) localStorage.setItem(KUNCI_PEMEGANG, String(nama)); else localStorage.removeItem(KUNCI_PEMEGANG); } catch (e) { /* abaikan */ } kirimDenyut(true); }
export function lokasiPerangkat() { try { return localStorage.getItem(KUNCI_LOKASI) || ''; } catch (e) { return ''; } }
export function setelLokasi(id) { try { if (id) localStorage.setItem(KUNCI_LOKASI, String(id)); else localStorage.removeItem(KUNCI_LOKASI); } catch (e) { /* abaikan */ } kirimDenyut(true); }
/** Sudahkah semua catatan perangkat ini diakui server? Menunggu paling lama `ms`; jawabannya jujur: sampai / masih menunggu / belum tersambung. */
export async function periksaSambungan(ms) {
  if (!db || !status.masuk) return { hasil: 'belum', teks: 'Belum masuk / belum tersambung ke Firestore' };
  const tunggu = waitForPendingWrites(db).then(() => 'sampai').catch(() => 'gagal');
  const habis = new Promise((r) => setTimeout(() => r('menunggu'), ms || 4000));
  const hasil = await Promise.race([tunggu, habis]);
  return { hasil, teks: hasil === 'sampai' ? 'Semua catatan perangkat ini sudah sampai server' : hasil === 'menunggu' ? 'Masih menunggu server — catatan aman di perangkat, dikirim sendiri begitu tersambung' : 'Server menolak — cek jejak' };
}
// ---- denyut perangkat: dokumen perangkatStatus yang sama dengan sistem lama (denyut-hp-gono), ditambah aplikasi 'baru', pemegang & lokasi ----
const KOLEKSI_PERANGKAT = 'perangkatStatus';
let _denyutTerakhir = 0, _denyutTerpasang = false;
export function kirimDenyut(paksa) {
  if (!db || !status.masuk) return;
  const kini = Date.now(); if (!paksa && kini - _denyutTerakhir < 60000) return; _denyutTerakhir = kini;
  let akun = ''; try { akun = String((auth && auth.currentUser && auth.currentUser.email) || ''); } catch (e) { /* abaikan */ }
  let nama = ''; try { nama = localStorage.getItem('miqbal_perangkat_label_v1') || ''; } catch (e) { /* abaikan */ }
  try { setDoc(doc(db, KOLEKSI_PERANGKAT, idPerangkat()), { id: idPerangkat(), nama, akun, aplikasi: 'baru', pada: new Date().toISOString(), antrean: status.antre.length, gagal: 0, versi: 'baru', pemegang: pemegangPerangkat(), lokasi: lokasiPerangkat() || '' }).catch(() => {}); }
  catch (e) { /* denyut bukan data uang — gagal = diam */ }
}
function pasangDenyut() {
  if (_denyutTerpasang) { kirimDenyut(); return; }
  _denyutTerpasang = true; kirimDenyut();
  document.addEventListener('visibilitychange', () => { if (!document.hidden) kirimDenyut(); });
  window.addEventListener('online', () => kirimDenyut());
  setInterval(() => { if (!document.hidden) kirimDenyut(); }, 300000);
}
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
  // `oleh` = siapa yang memegang perangkat ini (SS1; bawaan Owner = sama dengan sistem lama); `lokasi` = lokasi perangkat ini (SS4, fondasi) — hanya bila owner sudah menyetelnya
  const siapa = pemegangPerangkat(); const lok = lokasiPerangkat();
  if (!d.oleh) d.oleh = siapa;
  if (!d.perangkat) d.perangkat = perangkatRingkas();
  if (lok && !d.lokasi) d.lokasi = lok;
  d.diubahOleh = siapa; d.diubahPerangkat = perangkatRingkas(); d.diubahPada = new Date().toISOString();
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
      koleksi, idDok: String(d.id), oleh: d.diubahOleh, perangkat: perangkatRingkas(), ringkas: ringkasDok(d) };
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

// ---- ARSIP TAHUN (putaran 18, Tutup buku): pindah ke koleksi arsipTahun per potongan 200 dokumen (400 tulisan < batas 500 writeBatch) ----
// Langsung ke server (menunggu commit, bukan 1,5 detik): ritual ini wajib internet & satu perangkat. Satu baris log per potongan, bukan per dokumen.
const KOLEKSI_ARSIP = 'arsipTahun';
const POTONG = 200;
export async function arsipkanBerkas(tahun, daftar, progres) {
  if (!db) throw new Error('belum tersambung');
  if (!status.masuk) throw new Error('belum masuk sebagai owner');
  let sudah = 0;
  for (let i = 0; i < daftar.length; i += POTONG) {
    const b = writeBatch(db); const potong = daftar.slice(i, i + POTONG);
    potong.forEach((x) => {
      b.set(doc(db, KOLEKSI_ARSIP, tahun + '|' + x.koleksi + '|' + x.id), { id: tahun + '|' + x.koleksi + '|' + x.id, tahun, koleksi: x.koleksi, idAsli: String(x.id), dok: x.data, pada: new Date().toISOString(), oleh: pemegangPerangkat(), perangkat: perangkatRingkas() });
      b.delete(doc(db, x.koleksi, String(x.id)));
    });
    const log = { id: idUnik(), pada: new Date().toISOString(), aksi: 'arsip', koleksi: KOLEKSI_ARSIP, idDok: String(tahun), oleh: pemegangPerangkat(), perangkat: perangkatRingkas(), ringkas: 'tutup buku ' + tahun + ': ' + potong.length + ' dokumen diarsipkan' };
    b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
    await b.commit();
    sudah += potong.length; if (progres) progres(sudah, daftar.length);
  }
  return { ok: true, n: sudah };
}
export async function bacaArsipBerkas(tahun) {
  if (!db) throw new Error('belum tersambung');
  const snap = await getDocs(query(collection(db, KOLEKSI_ARSIP), where('tahun', '==', tahun)));
  const out = []; snap.forEach((d) => { const a = d.data(); out.push({ koleksi: a.koleksi, idAsli: a.idAsli, dok: a.dok }); });
  return out;
}
export async function pulihkanBerkas(tahun, daftar, progres) {
  if (!db) throw new Error('belum tersambung');
  if (!status.masuk) throw new Error('belum masuk sebagai owner');
  let sudah = 0;
  for (let i = 0; i < daftar.length; i += POTONG) {
    const b = writeBatch(db); const potong = daftar.slice(i, i + POTONG);
    potong.forEach((x) => { b.set(doc(db, x.koleksi, String(x.idAsli)), x.dok); b.delete(doc(db, KOLEKSI_ARSIP, tahun + '|' + x.koleksi + '|' + x.idAsli)); });
    const log = { id: idUnik(), pada: new Date().toISOString(), aksi: 'pulihkan', koleksi: KOLEKSI_ARSIP, idDok: String(tahun), oleh: pemegangPerangkat(), perangkat: perangkatRingkas(), ringkas: 'batal tutup buku ' + tahun + ': ' + potong.length + ' dokumen dikembalikan' };
    b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
    await b.commit();
    sudah += potong.length; if (progres) progres(sudah, daftar.length);
  }
  return { ok: true, n: sudah };
}

