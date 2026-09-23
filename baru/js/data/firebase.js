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
import { pasok, setelSumber, setelPenulis, dokDiCache } from './toko.js';
import { EMAIL_OWNER, keadaanAkun, bisaBekerja, pendengarPeran, periksaKiriman, beriAtribusiAkun, jejakKiriman, ringkasDok, susunPermintaan } from './akses.js';
import { buatAntre, cekDariCache } from './antre-lokal.js';

const firebaseConfig = {
  apiKey: 'AIzaSyAQ0DL-RnOa4gwSpvaNf1FMVlSNWla3RzA',
  authDomain: 'toko-beras-m-iqbal.firebaseapp.com',
  projectId: 'toko-beras-m-iqbal',
  storageBucket: 'toko-beras-m-iqbal.firebasestorage.app',
  messagingSenderId: '149034588465',
  appId: '1:149034588465:web:42316713d21c6fc994b810',
};
// ---- PROYEK UJI (putaran 23, gerbang owner 24 Sep): SEBELUM akun bukan-owner pertama disetujui, rules v3 diuji di proyek Firebase KEDUA.
// Satu setelan per perangkat yang mudah dikembalikan: /baru/?pasangProyekUji=<config JSON proyek uji> menyimpannya, ?lepasProyekUji=1 membuangnya.
// Proyek toko asli DITOLAK sebagai proyek uji. Selama aktif, app.js memasang bilah merah "PROYEK UJI" di setiap layar. docs/uji-rules-v3.md.
export const KUNCI_PROYEK_UJI = 'miqbal_baru_proyek_uji';
const PROYEK_TOKO = firebaseConfig.projectId;
export function aturProyekUjiDariAlamat(q) {
  try {
    if (q.get('lepasProyekUji')) { localStorage.removeItem(KUNCI_PROYEK_UJI); return 'lepas'; }
    const t = q.get('pasangProyekUji'); if (!t) return '';
    const c = JSON.parse(t); if (!c || !c.projectId || !c.apiKey || !c.appId) return 'Config proyek uji tidak lengkap (perlu projectId, apiKey, appId)';
    if (c.projectId === PROYEK_TOKO) return 'Itu proyek TOKO, bukan proyek uji — ditolak';
    localStorage.setItem(KUNCI_PROYEK_UJI, JSON.stringify({ apiKey: c.apiKey, authDomain: c.authDomain || c.projectId + '.firebaseapp.com', projectId: c.projectId, appId: c.appId, messagingSenderId: c.messagingSenderId || '', storageBucket: c.storageBucket || '' }));
    return 'pasang';
  } catch (e) { return 'Config proyek uji tidak terbaca: ' + String(e.message || e); }
}
export function proyekUji() { try { const c = JSON.parse(localStorage.getItem(KUNCI_PROYEK_UJI) || 'null'); return c && c.projectId && c.projectId !== PROYEK_TOKO ? c : null; } catch (e) { return null; } }

// Putaran 23 (24 Sep 2026): masuk PER ORANG. Owner dikenali lewat email (akses.js); akun lain lewat dokumen aksesAkun/{uid} yang ditulis owner.
// Sandi TIDAK ada di kode dan tidak pernah disimpan di sini; diketik sekali per sesi, sesinya disimpan peramban (browserLocalPersistence).

let app = null, db = null, auth = null;
// antre = catatan yang sudah tersimpan di perangkat ini tapi BELUM diakui server (hasPendingWrites) — putaran 14, layar Sistem → Perangkat
// akun = keadaanAkun() dari akses.js; ditolak = koleksi yang pendengarnya ditolak rules (disebut di SS1, aplikasi tetap jalan); lokal = salinan antre (antre-lokal.js)
const status = { masuk: false, email: '', akun: null, koleksiSiap: 0, koleksiTotal: KOLEKSI.length, galat: '', ditolak: [], offline: false, menunggu: 0, antre: [], lokal: { belum: 0, ditolak: 0 } };
const _antrePerKoleksi = {};
const OLEH_TETAP = 'Owner';                 // sama dengan index.html (alat owner)
const SESI = 's-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 6);   // salinan antre sesi ini masih ditunggu jawabannya oleh tab ini
const _penyimpan = { baca: (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } }, tulis: (k, v) => localStorage.setItem(k, v) };
const antre = buatAntre(_penyimpan, SESI);
const segarkanLokal = () => { status.lokal = { belum: antre.belumTerkirim().length, ditolak: antre.ditolak().length }; };
let _sumberHak = () => ({});   // kisi SS2 peran yang masuk ({ tindakan: 'sendiri'|'owner'|'tidak' }) — disetel app.js dari sistem-logika
export function setelSumberHak(f) { _sumberHak = typeof f === 'function' ? f : () => ({}); }
const KOLEKSI_LOG = 'logAktivitas';
const pendengarStatus = new Set();
const beriTahu = () => pendengarStatus.forEach((f) => f(Object.assign({}, status)));
let _pendengarKoleksi = [];

export function dengarkanStatus(f) { pendengarStatus.add(f); f(Object.assign({}, status)); return () => pendengarStatus.delete(f); }

let _lepasAkses = null;   // pendengar dokumen aksesAkun milik akun bukan-owner yang sedang masuk
/** saatAkun(akun) dipanggil tiap keadaan akun berubah (keluar · belum terdaftar · nonaktif · kasir@ · owner · aktif) — app.js menggambar layar masuknya. */
export function mulai(saatAkun) {
  if (app) return;
  app = initializeApp(proyekUji() || firebaseConfig);   // proyek uji (kalau disetel di perangkat ini) — cache & sesi Firebase terpisah per proyek
  db = initializeFirestore(app, { localCache: persistentLocalCache({ tabManager: persistentMultipleTabManager() }) });
  auth = getAuth(app);
  setPersistence(auth, browserLocalPersistence).catch(() => {});
  segarkanLokal();
  const terapkan = (akun) => {
    const tadi = status.akun; status.akun = akun; status.masuk = bisaBekerja(akun); status.email = akun.email || '';
    if (status.masuk) {
      if (!tadi || tadi.uid !== akun.uid || tadi.peran !== akun.peran) { cabutPendengar(); pasangPendengar(akun); }
      setelSumber('firestore', 'Firestore toko'); setelPenulis({ tulis: tulisBerkas, hapus: hapusBerkas, arsipkan: arsipkanBerkas, bacaArsip: bacaArsipBerkas, pulihkan: pulihkanBerkas, perbarui: perbaruiBerkas });
      pasangDenyut();
    } else { cabutPendengar(); }   // nonaktif / belum terdaftar / keluar: NOL pendengar koleksi toko, dan angka di memori dikosongkan
    saatAkun(akun); beriTahu();
  };
  onAuthStateChanged(auth, (u) => {
    if (_lepasAkses) { _lepasAkses(); _lepasAkses = null; }
    if (!u) return terapkan(keadaanAkun('', '', null));
    const email = String(u.email || '').toLowerCase();
    if (email === EMAIL_OWNER) return terapkan(keadaanAkun(email, u.uid, null));
    // bukan owner: peran dari aksesAkun/{uid}. Didengarkan terus — dinonaktifkan owner saat orangnya di layar = langsung terasa.
    _lepasAkses = onSnapshot(doc(db, 'aksesAkun', u.uid), (snap) => terapkan(keadaanAkun(email, u.uid, snap.exists() ? snap.data() : null)),
      () => terapkan(keadaanAkun(email, u.uid, null)));   // ditolak (mis. rules v2 belum dipasang v3) = dianggap belum terdaftar
  });
  window.addEventListener('online', () => { status.offline = false; beriTahu(); });
  window.addEventListener('offline', () => { status.offline = true; beriTahu(); });
  status.offline = typeof navigator !== 'undefined' && navigator.onLine === false;
}

/** Dipanggil dari formulir masuk; email + sandi diteruskan ke Firebase Auth lalu sandinya dilupakan. */
export async function masuk(email, sandi) {
  if (!auth) throw new Error('belum mulai');
  const e = String(email || '').trim().toLowerCase(); if (!e || e.indexOf('@') < 1) return { ok: false, pesan: 'Ketik email akun lu.' };
  try { await signInWithEmailAndPassword(auth, e, sandi); return { ok: true }; }
  catch (err) {
    const kode = String(err.code || '');
    return { ok: false, pesan: /wrong-password|invalid-credential|user-not-found|invalid-email/.test(kode) ? 'Email atau sandi salah. Coba lagi.' : /too-many-requests/.test(kode) ? 'Terlalu banyak percobaan — tunggu sebentar.' : /user-disabled/.test(kode) ? 'Akun ini dimatikan di Firebase. Hubungi owner.' : 'Gagal masuk — cek internet, lalu coba lagi.' };
  }
}
/** Keluar = ganti orang. Salinan antre TIDAK pernah dihapus di sini (app.js menanyakannya dulu kalau masih ada yang belum terkirim). */
export function keluar() { return auth ? signOut(auth) : Promise.resolve(); }
/** Akun yang belum terdaftar menulis permintaanAkses/{uid} (rules: create oleh pemilik uid, selama aksesAkun-nya belum ada). */
export async function mintaDidaftarkan(nama) {
  const r = susunPermintaan(status.akun, nama, new Date().toISOString()); if (r.tolak) return { gagal: true, pesan: r.tolak };
  try { await setDoc(doc(db, 'permintaanAkses', r.data.uid), r.data); return { ok: true }; }
  catch (e) { return { gagal: true, pesan: 'Permintaan ditolak server (' + String((e && e.code) || e) + '). Mungkin rules v3 belum dipasang — hubungi owner.' }; }
}

/** Pendengar PER PERAN (akses.js pendengarPeran; peta §3). Satu pendengar yang ditolak rules tidak mematikan aplikasi: disebut di SS1, sisanya jalan. */
function pasangPendengar(akun) {
  if (_pendengarKoleksi.length) return;   // sudah terpasang
  const daftarP = pendengarPeran(akun); const siap = {}; const perDok = {};
  status.koleksiSiap = 0; status.koleksiTotal = daftarP.length; status.ditolak = []; status.galat = '';
  const tandaiSiap = (nama) => { if (!siap[nama]) { siap[nama] = true; status.koleksiSiap += 1; } };
  const tolak = (nama, err) => { const kode = String((err && err.code) || err); if (status.ditolak.indexOf(nama) < 0) status.ditolak.push(nama); status.galat = nama + ': ' + kode; tandaiSiap(nama); beriTahu(); };
  daftarP.forEach((p) => {
    const k = KOLEKSI.find((x) => x.nama === p.nama) || { nama: p.nama };
    if (p.dok) {   // setelan per dokumen (bukan-owner): tiap dokumen didengar sendiri, cache koleksinya = gabungan yang ada
      perDok[p.nama] = {};
      p.dok.forEach((id) => {
        const lepas = onSnapshot(doc(db, p.nama, id), (snap) => {
          if (snap.exists()) perDok[p.nama][id] = snap.data(); else delete perDok[p.nama][id];
          pasok(p.nama, Object.keys(perDok[p.nama]).map((x) => perDok[p.nama][x])); tandaiSiap(p.nama); beriTahu();
        }, (err) => tolak(p.nama + '/' + id, err));
        _pendengarKoleksi.push(lepas);
      });
      return;
    }
    // koleksi berbatas (jejak logAktivitas): hanya `batas` baris terbaru yang dibaca — bukan seluruh riwayat tulisan
    const sumber = k.batas ? query(collection(db, k.nama), orderBy(k.urut, 'desc'), limit(k.batas)) : collection(db, k.nama);
    const lepas = onSnapshot(sumber, { includeMetadataChanges: true }, (snap) => {
      const daftar = [], tunda = [];
      snap.forEach((d) => { const x = d.data(); daftar.push(x); if (d.metadata && d.metadata.hasPendingWrites) tunda.push({ koleksi: k.nama, id: d.id, ringkas: ringkasDok(x), pada: x.diubahPada || x.pada || '', oleh: x.oleh || x.diubahOleh || '', perangkat: x.diubahPerangkat || x.perangkat || '' }); });
      _antrePerKoleksi[k.nama] = tunda; status.antre = Object.keys(_antrePerKoleksi).reduce((a, n) => a.concat(_antrePerKoleksi[n]), []);
      pasok(k.nama, daftar); tandaiSiap(k.nama);
      // dariCache = angka dari simpanan perangkat (belum tentu terbaru) — layar diberi tahu supaya jujur
      status.offline = !!(snap.metadata && snap.metadata.fromCache && typeof navigator !== 'undefined' && navigator.onLine === false);
      if (status.koleksiSiap >= status.koleksiTotal && !status.offline && !status.antre.length) cocokkanAntre();
      beriTahu();
    }, (err) => tolak(k.nama, err));
    _pendengarKoleksi.push(lepas);
  });
}
/** Cabut SEMUA pendengar koleksi toko & kosongkan angka di memori (keluar, belum terdaftar, dinonaktifkan). */
function cabutPendengar() {
  _pendengarKoleksi.forEach((f) => { try { f(); } catch (e) { /* abaikan */ } }); _pendengarKoleksi = [];
  Object.keys(_antrePerKoleksi).forEach((n) => { delete _antrePerKoleksi[n]; }); status.antre = [];
  status.koleksiSiap = 0; status.ditolak = []; status.galat = '';
  KOLEKSI.forEach((k) => pasok(k.nama, []));
}
// ---- salinan antre: sesudah semua pendengar siap, online, dan tidak ada tulisan tertunda — kiriman sesi lain dicocokkan ke server ----
let _cocokJalan = false;
function cocokkanAntre() {
  if (_cocokJalan || !antre.belumTerkirim().some((x) => x.sesi !== SESI)) return;
  _cocokJalan = true;
  waitForPendingWrites(db).then(() => { antre.cocokkanSesudahSinkron(cekDariCache(dokDiCache), new Date().toISOString()); segarkanLokal(); beriTahu(); })
    .catch(() => {}).finally(() => { _cocokJalan = false; });
}
export function antreLokal() { return { belum: antre.belumTerkirim(), ditolak: antre.ditolak() }; }
export function buangDitolak(id) { const ok = antre.buang(id); segarkanLokal(); beriTahu(); return ok; }
/** Owner menulis ulang kiriman yang ditolak ATAS NAMANYA: kolom penulis lama dibuang, atribusi owner dipasang penulis pusat, salinannya dihapus bila berhasil. */
export async function tulisUlangDitolak(id) {
  if (!status.akun || status.akun.jenis !== 'owner') return { gagal: true, pesan: 'Hanya owner yang boleh menulis ulang kiriman yang ditolak' };
  const x = antre.ditolak().find((y) => y.id === id); if (!x) return { gagal: true, pesan: 'Kiriman itu sudah tidak ada' };
  const bersih = (x.dokumen || []).map((d) => { const data = Object.assign({}, d.data); ['oleh', 'olehUid', 'diubahOleh', 'diubahOlehUid', 'diubahPerangkat', 'diubahPada'].forEach((k) => delete data[k]); return { koleksi: d.koleksi, data }; });
  const r = await tulisBerkas(bersih); if (r && r.gagal) return r;
  antre.buang(id); segarkanLokal(); beriTahu(); return r;
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
// Putaran 23: yang mencatat = AKUN yang masuk (bukti), bukan pilihan nama di perangkat (pengakuan). Kunci lama KUNCI_PEMEGANG dibiarkan, tidak dibaca lagi.
export function pemegangPerangkat() { return status.akun && bisaBekerja(status.akun) ? status.akun.nama : OLEH_TETAP; }
export function akunSekarang() { return status.akun; }
void KUNCI_PEMEGANG;
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
  if (!db || !status.masuk || !status.akun) return;
  const kini = Date.now(); if (!paksa && kini - _denyutTerakhir < 60000) return; _denyutTerakhir = kini;
  let akun = ''; try { akun = String((auth && auth.currentUser && auth.currentUser.email) || ''); } catch (e) { /* abaikan */ }
  let nama = ''; try { nama = localStorage.getItem('miqbal_perangkat_label_v1') || ''; } catch (e) { /* abaikan */ }
  try { setDoc(doc(db, KOLEKSI_PERANGKAT, idPerangkat()), { id: idPerangkat(), nama, akun, akunUid: status.akun.uid, aplikasi: 'baru', pada: new Date().toISOString(), antrean: status.antre.length, gagal: status.lokal.ditolak, versi: 'baru', pemegang: pemegangPerangkat(), lokasi: lokasiPerangkat() || '' }).catch(() => {}); }
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
const konteksTulis = () => ({ perangkat: perangkatRingkas(), lokasi: lokasiPerangkat(), kini: new Date().toISOString() });
const pemilikSaja = () => (status.akun && status.akun.jenis === 'owner' ? '' : 'Hanya owner yang boleh melakukan ini');

/**
 * Tulis sekumpulan dokumen SEKALIGUS: daftar = [{ koleksi, data }], data.id wajib.
 * Satu writeBatch + satu baris log per dokumen (koleksi logAktivitas, seperti catatLogAktivitas index.html).
 * Mengembalikan { antre: true } segera bila tulisan masuk antrean (offline/menunggu server) — datanya sudah
 * hidup di cache lokal dan onSnapshot sudah menggambarkannya; { ok: true } bila server sudah mengaku.
 */
export async function tulisBerkas(daftar, hapus, opsi) {
  if (!db) throw new Error('belum tersambung');
  if (!status.masuk || !status.akun) throw new Error('belum masuk');
  const akun = status.akun; const owner = akun.jenis === 'owner'; const k = konteksTulis();
  // create atau update ditentukan dari cache (dokumen sudah ada?) — sama dengan cara server menilai set()
  const isi = daftar.map(({ koleksi, data }) => { const lama = dokDiCache(koleksi, data.id); return { koleksi, data, ada: !!lama, lama }; });
  const H = hapus || [];
  if (!owner) { const p = periksaKiriman(akun, isi, H, _sumberHak()); if (p.tolak) return { gagal: true, pesan: p.tolak }; }   // pasti ditolak rules → tidak dikirim
  const b = writeBatch(db); const ditulis = [];
  isi.forEach((x) => {
    const d = beriAtribusiAkun(x.data, akun, k, x.ada);
    b.set(doc(db, x.koleksi, String(d.id)), d); ditulis.push({ koleksi: x.koleksi, data: d });
    if (owner) {   // owner: satu baris jejak per dokumen, seperti catatLogAktivitas index.html (+ olehUid)
      const log = { id: idUnik(), pada: k.kini, aksi: d.dibatalkan ? 'batalkan' : (d.dikoreksiOleh ? 'tandai-koreksi' : 'tulis'),
        koleksi: x.koleksi, idDok: String(d.id), oleh: d.diubahOleh, olehUid: akun.uid, perangkat: k.perangkat, ringkas: ringkasDok(d) };
      b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
    }
  });
  H.forEach((x) => {   // hanya owner sampai di sini (periksaKiriman menolak hapus bukan-owner)
    b.delete(doc(db, x.koleksi, String(x.id)));
    const log = { id: idUnik(), pada: k.kini, aksi: 'hapus', koleksi: x.koleksi, idDok: String(x.id), oleh: akun.nama, olehUid: akun.uid, perangkat: k.perangkat, ringkas: String((opsi && opsi.jejakHapus) || 'dihapus').slice(0, 200) };
    b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
  });
  if (!owner) { const log = jejakKiriman(akun, ditulis, Object.assign({ idJejak: idUnik() }, k)); b.set(doc(db, KOLEKSI_LOG, String(log.id)), log); }   // SATU baris per kiriman, memuat daftar dokumennya
  // salinan antre SEBELUM dikirim; penuh = tidak dikirim (tidak ada salinan lama yang dibuang)
  const idKiriman = 'k-' + idUnik(); const s0 = antre.tambah({ id: idKiriman, pada: k.kini, akunUid: akun.uid, akunNama: akun.nama, peran: akun.peran, dokumen: ditulis });
  if (s0.tolak) return { gagal: true, pesan: s0.tolak };
  segarkanLokal(); status.menunggu += 1; beriTahu();
  const janji = b.commit().then(() => { antre.konfirmasi(idKiriman); return { ok: true }; })
    .catch((e) => { const kode = String((e && e.code) || e); antre.tandaiDitolak(idKiriman, kode, new Date().toISOString()); status.galat = 'tulis ditolak: ' + kode; beriTahu(); return { gagal: true, pesan: status.galat + ' — salinannya ada di Sistem › Perangkat (ditolak server)' }; })
    .finally(() => { segarkanLokal(); status.menunggu = Math.max(0, status.menunggu - 1); beriTahu(); });
  // tunggu sebentar: kalau server mengaku dalam 1,5 detik → ok; kalau tidak → antre (offline / lambat), bukan gagal
  return Promise.race([janji, new Promise((r) => setTimeout(() => r({ antre: true }), 1500))]);
}
export async function hapusBerkas(daftar) {
  if (!db) throw new Error('belum tersambung');
  if (!status.akun || status.akun.jenis !== 'owner') { const p = periksaKiriman(status.akun, [], daftar, _sumberHak()); return { gagal: true, pesan: p.tolak || 'Hanya owner yang boleh menghapus' }; }   // bukan-owner tidak pernah DELETE (peta §5)
  const b = writeBatch(db);
  daftar.forEach(({ koleksi, id }) => b.delete(doc(db, koleksi, String(id))));
  return Promise.race([b.commit().then(() => ({ ok: true })), new Promise((r) => setTimeout(() => r({ antre: true }), 1500))]);
}

/** Putaran 23b (Bersihkan ciri yang dicabut): UPDATE kolom tertentu saja — TANPA beriAtribusi, supaya kolom lain byte-sama sebelum & sesudah.
 *  Satu writeBatch per potongan (≤ 200 dokumen); SATU baris log (jumlah saja, tanpa isi cip) di potongan terakhir. Berhenti di potongan yang ditolak. */
export async function perbaruiBerkas(potongan, ringkas) {
  if (!db) throw new Error('belum tersambung');
  if (!status.masuk) throw new Error('belum masuk sebagai owner');
  if (pemilikSaja()) return { gagal: true, potongan: [], pesan: pemilikSaja() };
  const hasil = [];
  for (let i = 0; i < potongan.length; i++) {
    const p = potongan[i]; const b = writeBatch(db);
    p.forEach((x) => b.update(doc(db, x.koleksi, String(x.id)), x.kolom));
    if (i === potongan.length - 1) { const log = { id: idUnik(), pada: new Date().toISOString(), aksi: 'bersihkan', koleksi: 'pelangganCatatan', idDok: 'ciri-dicabut', oleh: pemegangPerangkat(), olehUid: status.akun.uid, perangkat: perangkatRingkas(), ringkas: String(ringkas || '') }; b.set(doc(db, KOLEKSI_LOG, String(log.id)), log); }
    status.menunggu += 1; beriTahu();
    const janji = b.commit().then(() => ({ n: p.length, keadaan: 'ok' }))
      .catch((e) => { status.galat = 'bersihkan ditolak: ' + String((e && e.code) || e); beriTahu(); return { n: p.length, keadaan: 'gagal', pesan: status.galat }; })
      .finally(() => { status.menunggu = Math.max(0, status.menunggu - 1); beriTahu(); });
    const h = await Promise.race([janji, new Promise((r) => setTimeout(() => r({ n: p.length, keadaan: 'antre' }), 1500))]);
    hasil.push(h); if (h.keadaan === 'gagal') break;
  }
  return { potongan: hasil, gagal: hasil.some((h) => h.keadaan === 'gagal') };
}

// ---- ARSIP TAHUN (putaran 18, Tutup buku): pindah ke koleksi arsipTahun per potongan 200 dokumen (400 tulisan < batas 500 writeBatch) ----
// Langsung ke server (menunggu commit, bukan 1,5 detik): ritual ini wajib internet & satu perangkat. Satu baris log per potongan, bukan per dokumen.
const KOLEKSI_ARSIP = 'arsipTahun';
const POTONG = 200;
export async function arsipkanBerkas(tahun, daftar, progres) {
  if (!db) throw new Error('belum tersambung');
  if (!status.masuk) throw new Error('belum masuk sebagai owner');
  if (pemilikSaja()) throw new Error(pemilikSaja());
  let sudah = 0;
  for (let i = 0; i < daftar.length; i += POTONG) {
    const b = writeBatch(db); const potong = daftar.slice(i, i + POTONG);
    potong.forEach((x) => {
      b.set(doc(db, KOLEKSI_ARSIP, tahun + '|' + x.koleksi + '|' + x.id), { id: tahun + '|' + x.koleksi + '|' + x.id, tahun, koleksi: x.koleksi, idAsli: String(x.id), dok: x.data, pada: new Date().toISOString(), oleh: pemegangPerangkat(), olehUid: status.akun.uid, perangkat: perangkatRingkas() });
      b.delete(doc(db, x.koleksi, String(x.id)));
    });
    const log = { id: idUnik(), pada: new Date().toISOString(), aksi: 'arsip', koleksi: KOLEKSI_ARSIP, idDok: String(tahun), oleh: pemegangPerangkat(), olehUid: status.akun.uid, perangkat: perangkatRingkas(), ringkas: 'tutup buku ' + tahun + ': ' + potong.length + ' dokumen diarsipkan' };
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
  if (pemilikSaja()) throw new Error(pemilikSaja());
  let sudah = 0;
  for (let i = 0; i < daftar.length; i += POTONG) {
    const b = writeBatch(db); const potong = daftar.slice(i, i + POTONG);
    potong.forEach((x) => { b.set(doc(db, x.koleksi, String(x.idAsli)), x.dok); b.delete(doc(db, KOLEKSI_ARSIP, tahun + '|' + x.koleksi + '|' + x.idAsli)); });
    const log = { id: idUnik(), pada: new Date().toISOString(), aksi: 'pulihkan', koleksi: KOLEKSI_ARSIP, idDok: String(tahun), oleh: pemegangPerangkat(), olehUid: status.akun.uid, perangkat: perangkatRingkas(), ringkas: 'batal tutup buku ' + tahun + ': ' + potong.length + ' dokumen dikembalikan' };
    b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
    await b.commit();
    sudah += potong.length; if (progres) progres(sudah, daftar.length);
  }
  return { ok: true, n: sudah };
}

