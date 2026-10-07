// Sambungan ke Firestore toko. Putaran 1 baca; putaran 2 (19 Sep 2026) MENULIS nota lewat SATU pintu:
// tulisBerkas() = writeBatch — semua dokumen satu nota masuk bersama atau tidak sama sekali (index.html
// menulis satu per satu dengan setDoc; nota tiga baris bisa tersimpan separuh kalau internet putus di tengah).
// Proyek, koleksi, akun, dan atribusi (oleh/perangkat/diubah*) sama dengan index.html; jalan tanpa internet
// diserahkan ke cache tetap Firestore (tulisan mengantre sendiri, terkirim begitu tersambung).
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js';
import { initializeFirestore, persistentLocalCache, persistentMultipleTabManager, collection, onSnapshot, writeBatch, doc, setDoc, query, orderBy, limit, where, getDocs, waitForPendingWrites, connectFirestoreEmulator,
  getDocsFromServer, getCountFromServer, serverTimestamp, Timestamp, CACHE_SIZE_UNLIMITED, terminate }
  from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-firestore.js';
import { getAuth, signInWithEmailAndPassword, onAuthStateChanged, setPersistence, browserLocalPersistence, signOut, connectAuthEmulator }
  from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-auth.js';
import { KOLEKSI } from './koleksi.js';
import { pasok, setelSumber, setelPenulis, dokDiCache, jagaKunci, dengarkan, sumberData, setelTertunda, setelDariCache, setelHapusTertunda, hapusTertunda, cacheMentah, tolakKunci } from './toko.js';
import { EMAIL_OWNER, keadaanAkun, bisaBekerja, pendengarPeran, periksaKiriman, beriAtribusiAkun, jejakKiriman, ringkasDok, susunPermintaan } from './akses.js';
import { buatAntre, cekDariCache, susunTulisUlang, jejakTulisUlang } from './antre-lokal.js';
import { KP_BATAS_GET, kpPecahBiaya } from './kunci-periode.js';
import { KK_KOLEKSI, KK_ID, KK_JEDA_MS, kkSetelServer, kkLupakanServer, kkIsi, kkDokumen, kkTertinggal, kkBolehTerbit, kkMentah, kkCatatTerbit, kkPasangGerbang, kkKanon } from './katalog-kasir.js';
import { HB_VERSI, HB_LIMIT_F, HB_KOLEKSI_NISAN, HB_ID_KLAIM, HB_MULAI_MS, hbHemat, hbKoleksiHemat, hbKupas, hbSaklar, hbSetelSaklar, hbNisanSah, hbTandaiNisanSah, hbBacaRekam, hbSimpanRekam,
  hbSesi, hbKunciTab, hbAyunanBaru, hbCatatTerbitKatalog, hbNilaiKatalogServer, hbBolehTerbitKatalog, hbSiapNyala, hbTanpaCapStatis } from './hemat-baca.js';
import { serverTiruan, configTiruan } from './server-tiruan.js';

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
// ---- SERVER TIRUAN (gladi tutup buku di runner GitHub, 7 Okt 2026): server-tiruan.js. Aktif HANYA di halaman localhost / 127.0.0.1 dengan
// ?emulator=host:port — Firestore & Auth ke Firebase Emulator Suite, proyek demo. Di situs sungguhan parameter ini diabaikan (dan CSP situs memblokirnya).
// Diminta di halaman lokal tapi alamatnya ditolak = GAGAL-TERTUTUP: mulai() tidak menyambung ke server mana pun (tinjauan 7 Okt: dulu jatuh ke proyek toko).
let _tiruan;
function bacaTiruan() {
  if (_tiruan !== undefined) return _tiruan;
  try { _tiruan = serverTiruan(new URLSearchParams(location.search), location.hostname); } catch (e) { _tiruan = null; }
  return _tiruan;
}
/** Setelan server tiruan yang berlaku ({ firestore, auth, proyek }) atau null. app.js memasang bilah "SERVER TIRUAN" selama aktif. */
export function serverTiruanAktif() { const t = bacaTiruan(); return t && !t.tolak ? t : null; }
/** Kalimat penolakan kalau ?emulator= diminta di halaman lokal tapi alamatnya salah ('' = tidak ada). */
export function tolakServerTiruan() { const t = bacaTiruan(); return t && t.tolak ? t.tolak : ''; }

// Putaran 23 (24 Sep 2026): masuk PER ORANG. Owner dikenali lewat email (akses.js); akun lain lewat dokumen aksesAkun/{uid} yang ditulis owner.
// Sandi TIDAK ada di kode dan tidak pernah disimpan di sini; diketik sekali per sesi, sesinya disimpan peramban (browserLocalPersistence).

let app = null, db = null, auth = null;
// antre = catatan yang sudah tersimpan di perangkat ini tapi BELUM diakui server (hasPendingWrites) — putaran 14, layar Sistem → Perangkat
// akun = keadaanAkun() dari akses.js; ditolak = koleksi yang pendengarnya ditolak rules (disebut di SS1, aplikasi tetap jalan); lokal = salinan antre (antre-lokal.js)
const status = { masuk: false, email: '', akun: null, koleksiSiap: 0, koleksiTotal: KOLEKSI.length, galat: '', ditolak: [], offline: false, menunggu: 0, antre: [], lokal: { belum: 0, ditolak: 0 } };
const _antrePerKoleksi = {};
const _dariCache = {};   // 25c: koleksi yang jawaban terakhirnya dari SALINAN PERANGKAT (belum dijawab server) — katalog kasir tidak terbit dari data itu
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

// ---- HEMAT BACA (owner 7 Okt 2026, siap 2027 — baru/js/data/hemat-baca.js, docs/rancangan-hemat-baca.md) ----
// Saklar PER PERANGKAT, dibaca sekali saat aplikasi dimuat (ganti saklar = muat ulang). MATI (bawaan) = pendengar penuh seperti sebelumnya; yang tetap jalan:
// kupas capServer sebelum memori, cap jam server di tulisan koleksi hemat, batu nisan (sesudah aturan v7 terbukti), versi denyut baru-c1.
const _penyimpanHemat = { baca: (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } }, tulis: (k, v) => localStorage.setItem(k, v), hapus: (k) => localStorage.removeItem(k) };
const _hematNyala = hbSaklar(_penyimpanHemat);
let _hemat = null;          // sesi hemat (hbSesi) — hanya saklar nyala + owner + aturan v7 terbukti
let _proyek = '';           // projectId yang dipakai (toko / proyek uji) — rekam & tanda aturan v7 per proyek
let _nisanSah = false;      // aturan v7 terpasang (owner bisa membaca batuNisan): hapus koleksi hemat ditulis BERSAMA batu nisannya
let _nisanKabar = '';
let _berhenti = '';         // kunci tab kalah: klien Firestore tab ini dihentikan (terminate) — tulisan ditolak, layar menyuruh muat ulang
const _cap = {};            // peta samping kupas: koleksi → id → cap (ms / null tertunda / 'peta' / undefined) — pendeteksi statis & gema jam server
const _kunciTab = hbKunciTab(_penyimpanHemat, () => Date.now(), SESI);   // satu klien Firestore per peramban (dipakai hanya saat saklar nyala, app.js)
const _ayunan = hbAyunanBaru();
let _kodeBercap = 0;        // jam pertama kali kode bercap jalan di peramban ini (pendeteksi statis: catatan tanpa cap SESUDAH ini = penulis lama)
export const hematNyala = () => _hematNyala;
export const kunciTabHemat = () => _kunciTab;

export function dengarkanStatus(f) { pendengarStatus.add(f); f(Object.assign({}, status)); return () => pendengarStatus.delete(f); }

let _lepasAkses = null;   // pendengar dokumen aksesAkun milik akun bukan-owner yang sedang masuk
/** saatAkun(akun) dipanggil tiap keadaan akun berubah (keluar · belum terdaftar · nonaktif · kasir@ · owner · aktif) — app.js menggambar layar masuknya. */
export function mulai(saatAkun) {
  if (app) return;
  // server tiruan diminta tapi ditolak: tidak tersambung ke mana pun — gerbang masuk tetap tertutup tanpa formulir, bilah merah menyebut sebabnya (app.js)
  const tolakT = tolakServerTiruan(); if (tolakT) { status.galat = tolakT; beriTahu(); return; }
  const T = serverTiruanAktif();
  // server tiruan (gladi) > proyek uji (kalau disetel di perangkat ini) > proyek toko — cache & sesi Firebase terpisah per proyek
  app = initializeApp(T ? configTiruan(T) : (proyekUji() || firebaseConfig));
  _proyek = T ? T.proyek : (proyekUji() || firebaseConfig).projectId; _nisanSah = hbNisanSah(_penyimpanHemat, _proyek);
  try { _kodeBercap = Number(localStorage.getItem('miqbal_kode_bercap_v1')) || 0; if (!_kodeBercap) { _kodeBercap = Date.now(); localStorage.setItem('miqbal_kode_bercap_v1', String(_kodeBercap)); } } catch (e) { _kodeBercap = Date.now(); }
  // hemat baca nyala: simpanan TANPA GC — pendengar simpanan (source 'cache') tidak menahan dokumennya, GC bawaan (40 MiB) bisa membuangnya diam-diam.
  // Mati: setelan bawaan seperti sebelum 7 Okt.
  const cacheOpsi = { tabManager: persistentMultipleTabManager() }; if (_hematNyala) cacheOpsi.cacheSizeBytes = CACHE_SIZE_UNLIMITED;
  db = initializeFirestore(app, { localCache: persistentLocalCache(cacheOpsi) });
  // emulator wajib disambung SEBELUM db / auth dipakai apa pun
  if (T) connectFirestoreEmulator(db, T.firestore.host, T.firestore.port);
  auth = getAuth(app);
  if (T) connectAuthEmulator(auth, T.auth, { disableWarnings: true });
  setPersistence(auth, browserLocalPersistence).catch(() => {});
  segarkanLokal();
  const terapkan = (akun) => {
    const tadi = status.akun; status.akun = akun; status.masuk = bisaBekerja(akun); status.email = akun.email || '';
    if (status.masuk) {
      if (!tadi || tadi.uid !== akun.uid || tadi.peran !== akun.peran) { cabutPendengar(); pasangPendengar(akun); }
      setelSumber('firestore', 'Firestore toko'); setelPenulis({ tulis: tulisBerkas, hapus: hapusBerkas, arsipkan: arsipkanBerkas, bacaArsip: bacaArsipBerkas, pulihkan: pulihkanBerkas, perbarui: perbaruiBerkas });
      pasangDenyut(); pasangPenerbitKatalog();
      if (akun.jenis === 'owner') periksaNisanSah();
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
  window.addEventListener('online', () => { status.offline = false; if (_hemat) _hemat.online(true); if (status.akun && status.akun.jenis === 'owner') periksaNisanSah(); beriTahu(); });
  window.addEventListener('offline', () => { status.offline = true; if (_hemat) _hemat.online(false); beriTahu(); });
  status.offline = typeof navigator !== 'undefined' && navigator.onLine === false;
}
// ---- aturan v7 terpasang? (owner) Sekali terbukti per proyek di peramban ini, tidak diperiksa lagi (1 baca). Sebelum terbukti, hapus TANPA batu nisan —
// persis seperti sebelum 7 Okt — jadi kode ini aman walau digabung sebelum rules v7 diterbitkan (rules v6 menolak seluruh batch yang memuat batu nisan).
let _nisanJalan = false;
function periksaNisanSah() {
  if (_nisanSah || _nisanJalan || !db) return;
  _nisanJalan = true;
  getDocsFromServer(query(collection(db, HB_KOLEKSI_NISAN), limit(1)))
    .then(() => { _nisanSah = true; _nisanKabar = ''; hbTandaiNisanSah(_penyimpanHemat, _proyek, Date.now()); beriTahu(); })
    .catch((e) => { _nisanKabar = String((e && e.code) || e) === 'permission-denied' ? 'aturan server belum v7 (batu nisan ditolak) — hapus ditulis tanpa batu nisan' : 'belum terperiksa (' + String((e && e.code) || e) + ')'; beriTahu(); })
    .finally(() => { _nisanJalan = false; });
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
  // hemat baca (owner 7 Okt): saklar nyala + owner + aturan v7 terbukti → koleksi hemat didengar sesi hemat (V/S/F/N); sisanya (tetap & jejak) persis di bawah
  const hemat = _hematNyala && akun.jenis === 'owner' && _nisanSah && !_berhenti && _kunciTab.milik();
  const kHemat = hemat ? hbKoleksiHemat().filter((n) => daftarP.some((p) => p.nama === n && !p.dok)) : [];
  daftarP.forEach((p) => {
    const k = KOLEKSI.find((x) => x.nama === p.nama) || { nama: p.nama };
    if (kHemat.indexOf(p.nama) >= 0) return;
    if (p.dok) {   // setelan per dokumen (bukan-owner): tiap dokumen didengar sendiri, cache koleksinya = gabungan yang ada
      perDok[p.nama] = {};
      p.dok.forEach((id) => {
        const lepas = onSnapshot(doc(db, p.nama, id), (snap) => {
          if (snap.exists()) { const x = snap.data(); hbKupas(x); perDok[p.nama][id] = x; } else delete perDok[p.nama][id];   // owner 7 Okt: cap jam server tidak masuk memori
          pasok(p.nama, Object.keys(perDok[p.nama]).map((x) => perDok[p.nama][x])); tandaiSiap(p.nama); beriTahu();
        }, (err) => tolak(p.nama + '/' + id, err));
        _pendengarKoleksi.push(lepas);
      });
      return;
    }
    // koleksi berbatas (jejak logAktivitas): hanya `batas` baris terbaru yang dibaca — bukan seluruh riwayat tulisan
    const sumber = k.batas ? query(collection(db, k.nama), orderBy(k.urut, 'desc'), limit(k.batas)) : collection(db, k.nama);
    const lepas = onSnapshot(sumber, { includeMetadataChanges: true }, (snap) => {
      const daftar = [], tunda = []; const capK = {};
      // owner 7 Okt (hemat baca): KUPAS — capServer/padaServer dibuang dari isi sebelum memori (mesin beku, cadangan, katalog, penjaga kiriman tidak melihatnya);
      // nilainya disimpan di peta samping _cap (pendeteksi catatan tanpa cap & gema jam server). Saklar mati: isi memori sama dengan sebelum 7 Okt.
      snap.forEach((d) => { const x = d.data(); capK[d.id] = hbKupas(x); daftar.push(x); if (d.metadata && d.metadata.hasPendingWrites) tunda.push({ koleksi: k.nama, id: d.id, ringkas: ringkasDok(x), pada: x.diubahPada || x.pada || '', oleh: x.oleh || x.diubahOleh || '', perangkat: x.diubahPerangkat || x.perangkat || '' }); });
      _cap[k.nama] = capK;
      _antrePerKoleksi[k.nama] = tunda; status.antre = Object.keys(_antrePerKoleksi).reduce((a, n) => a.concat(_antrePerKoleksi[n]), []);
      // §8 no. 4: tutup buku bertahap tidak menghitung dokumen yang masih menunggu server sebagai "masuk" (toko.js dokTertunda)
      setelTertunda(k.nama, tunda.map((t) => t.id));
      _dariCache[k.nama] = !!(snap.metadata && snap.metadata.fromCache);
      // putaran 3 AAL4: tutup buku membaca tanda ini (toko.js koleksiDariCache) — Lanjutkan & Batalkan tidak jalan dari salinan perangkat
      setelDariCache(k.nama, _dariCache[k.nama]);
      pasok(k.nama, daftar); tandaiSiap(k.nama);
      // dariCache = angka dari simpanan perangkat (belum tentu terbaru) — layar diberi tahu supaya jujur
      status.offline = !!(snap.metadata && snap.metadata.fromCache && typeof navigator !== 'undefined' && navigator.onLine === false);
      if (_hemat) kabariTetap(k.nama, snap, tunda);
      if (status.koleksiSiap >= status.koleksiTotal && !status.offline && !status.antre.length && (!_hemat || !adaDariCache())) cocokkanAntre();
      beriTahu();
    }, (err) => tolak(k.nama, err));
    _pendengarKoleksi.push(lepas);
  });
  if (kHemat.length) pasangHemat(kHemat, tandaiSiap);
  if (akun.jenis === 'owner') pasangPendengarKatalog();
}
const adaDariCache = () => Object.keys(_dariCache).some((n) => _dariCache[n]);
// ---- sesi hemat: adaptor SDK (hemat-baca.js tidak mengimpor Firebase) ----
const TETAP_HEMAT = { perangkatStatus: 1, tutupBukuAcara: 1, aturanToko: 1 };   // masukan sesi hemat dari koleksi tetap: denyut, berita acara, klaim harian
let _tetapAda = {}, _gemaTerakhir = null, _denyutKirim = { pada: '', ms: 0 };
function kabariTetap(nama, snap, tunda) {
  if (!TETAP_HEMAT[nama]) return;
  _tetapAda[nama] = true;
  // gema jam server: capServer denyut yang DIKIRIM SESI INI (kolom `pada` = yang terakhir dikirim), sudah diakui server — selisih jam server & jam perangkat
  // dihitung dari jam perangkat SAAT dikirim. Denyut lama dari sesi sebelumnya (cap berjam-jam lalu) tidak pernah dipakai.
  if (nama === KOLEKSI_PERANGKAT && !(snap.metadata && snap.metadata.fromCache) && _denyutKirim.pada) {
    const id = idPerangkat(); const c = (_cap[nama] || {})[id]; const d = dokDiCache(nama, id);
    if (typeof c === 'number' && d && d.pada === _denyutKirim.pada && _gemaTerakhir !== _denyutKirim.pada && !tunda.some((t) => t.id === id)) { _gemaTerakhir = _denyutKirim.pada; _hemat.gemaServer(c, _denyutKirim.ms); }
  }
  if (!Object.keys(TETAP_HEMAT).every((n) => _tetapAda[n])) return;
  _hemat.setelTetap({ perangkat: cacheMentah('perangkat'), acara: cacheMentah('tutupBukuAcara'), klaim: dokDiCache('aturanToko', HB_ID_KLAIM) });
}
const snapPolos = (snap) => ({ dariCache: !!(snap.metadata && snap.metadata.fromCache),
  dok: snap.docs.map((d) => ({ id: d.id, tunda: !!(d.metadata && d.metadata.hasPendingWrites), capMentah: d.get('capServer'), isi: () => d.data() })) });
function pasangHemat(koleksi, tandaiSiap) {
  const R = hbBacaRekam(_penyimpanHemat, _proyek, status.akun.uid);
  const dengar = (sumber, opsi, cb, galat) => { const lepas = onSnapshot(sumber, opsi, (s) => cb(snapPolos(s)), galat); return lepas; };
  const lewat = (B) => where('capServer', '>', Timestamp.fromMillis(B));
  _tetapAda = {}; _gemaTerakhir = null;
  _hemat = hbSesi({
    koleksi, R, simpan: () => hbSimpanRekam(_penyimpanHemat, R, Date.now()), jam: () => Date.now(), jadwal: (f, ms) => setTimeout(f, ms), batal: (h) => clearTimeout(h),
    idPerangkat: idPerangkat(), namaPerangkat: perangkatRingkas(), online: !(typeof navigator !== 'undefined' && navigator.onLine === false),
    milikTab: () => _kunciTab.milik(), hapusTunda: (k) => hapusTertunda(k),
    sdk: {
      cache: (k, cb, galat) => dengar(collection(db, k), { source: 'cache', includeMetadataChanges: true }, cb, galat),
      delta: (k, B, cb, galat) => dengar(query(collection(db, k), lewat(B)), { includeMetadataChanges: true }, cb, galat),
      penuh: (k, cb, galat) => dengar(query(collection(db, k), limit(HB_LIMIT_F)), { includeMetadataChanges: true }, cb, galat),
      nisan: (B, cb, galat) => dengar(query(collection(db, HB_KOLEKSI_NISAN), lewat(B)), { includeMetadataChanges: true }, cb, galat),
      hitung: (k) => getCountFromServer(collection(db, k)).then((s) => s.data().count),
      klaim: (dok) => setDoc(doc(db, 'aturanToko', HB_ID_KLAIM), dok),   // klaim baca penuh harian: dokumen setelan (tetap), tanpa jejak — seperti katalog kasir
      sentuh: (k, ids, lihat) => sentuhCap(k, ids, lihat),
      tulisNisan: (k, ids) => tulisNisanSaja(k, ids),
    },
    keluar: {
      pasok: (k, data) => pasok(k, data),
      tunda: (k, dok) => {
        const tunda = dok.map(({ id, data: x }) => ({ koleksi: k, id, ringkas: ringkasDok(x), pada: x.diubahPada || x.pada || '', oleh: x.oleh || x.diubahOleh || '', perangkat: x.diubahPerangkat || x.perangkat || '' }));
        _antrePerKoleksi[k] = tunda; status.antre = Object.keys(_antrePerKoleksi).reduce((a, n) => a.concat(_antrePerKoleksi[n]), []); setelTertunda(k, tunda.map((t) => t.id));
      },
      siap: (k) => tandaiSiap(k),
      // TERPERIKSA (S & N terkini dari server + baca penuh sesi ini / hitungan server cocok) = arti "dijawab server" lama: gerbang katalog, tutup buku, cocokkanAntre
      periksa: (k, ya) => { _dariCache[k] = !ya; setelDariCache(k, !ya); },
      berubah: () => {
        status.offline = typeof navigator !== 'undefined' && navigator.onLine === false;
        if (status.koleksiSiap >= status.koleksiTotal && !status.offline && !status.antre.length && !adaDariCache()) cocokkanAntre();
        // pil kepala (app.js statusRingkas): data yang belum terperiksa dengan server disebut — kalau ragu, layar mengaku
        const H = _hemat ? _hemat.keadaan() : null; status.hematPil = !H ? '' : H.vMati ? ' · MUAT ULANG' : H.belum.length ? ' · memeriksa data (' + H.belum.length + ')' : '';
        jadwalBeriTahu();
      },
      mati: () => { status.hematMati = true; status.galat = 'Tab ini berhenti menerima data dari server — muat ulang aplikasi (catatan di antrean aman)'; beriTahu(); },
    },
  }).mulai();
}
let _beriTahuH = null;
function jadwalBeriTahu() { if (_beriTahuH) return; _beriTahuH = setTimeout(() => { _beriTahuH = null; beriTahu(); }, 50); }
// ---- KATALOG KASIR (25c): /baru/ penerbitnya. Dokumen di server didengar (owner saja — rules: owner & kasir@), isinya dibandingkan tiap data berubah,
// ditulis hanya kalau berbeda; gerbangnya kkBolehTerbit (katalog-kasir.js). Dokumen turunan: setDoc apa adanya, tanpa jejak — sama dengan index.html.
function pasangPendengarKatalog() {
  const lepas = onSnapshot(doc(db, KK_KOLEKSI, KK_ID), { includeMetadataChanges: true }, (snap) => {
    kkSetelServer(snap.exists() ? snap.data() : null, !(snap.metadata && snap.metadata.fromCache));
    // hemat baca nyala: katalog server berganti ke isi LAIN ≤ 15 menit sesudah perangkat ini terbit (bukan gemanya) = dua perangkat owner berbeda hitungan
    // → berhenti terbit otomatis, perangkat ini membaca penuh (P2-4: tanpa ini dua HP owner saling timpa katalog tanpa henti)
    if (_hemat && snap.exists() && !(snap.metadata && snap.metadata.fromCache) && _ayunan.terbit.length && !_ayunan.berhenti) {
      const isiIni = kkIsi(); hbNilaiKatalogServer(_ayunan, kkKanon(snap.data()), isiIni ? kkKanon(isiIni) : '', Date.now());
      if (_ayunan.berhenti) _hemat.bacaPenuh(null, 'katalog kasir berayun antarperangkat', false);
    }
    jadwalkanKatalog(); beriTahu();
  }, () => { kkLupakanServer(); beriTahu(); });   // ditolak / galat: keadaan katalog tidak diketahui → tidak terbit
  _pendengarKoleksi.push(lepas);
}
let _kkTimer = null, _kkJalan = false, _kkDipasang = false;
function jadwalkanKatalog() { clearTimeout(_kkTimer); _kkTimer = setTimeout(terbitkanKatalogOtomatis, KK_JEDA_MS); }
// hemat baca nyala: gerbang tambahan (semua koleksi hemat terperiksa, hitungan koleksi HP kasir ≤ 35 menit, kunci tab, tanpa ayunan, ≤ 6 terbit/jam). Mati = null.
function gerbangHemat() {
  if (!_hemat) return null;
  if (!_kunciTab.milik()) return { boleh: false, sebab: 'aplikasi dipakai di tab lain peramban ini' };
  const a = hbBolehTerbitKatalog(_ayunan, Date.now()); if (!a.boleh) return a;
  return _hemat.bolehKatalog();
}
// gerbang terbit katalog kasir — SATU penilai untuk terbit otomatis DAN katalog yang ikut kiriman terbit harga (kkSertakan; audit 39b no. 17: dulu jalur itu
// melewati gerbang → katalog HP kasir bisa disusun dari data yang belum termuat penuh / masih salinan perangkat)
function gerbangKatalog() {
  return kkBolehTerbit({ owner: !!status.akun && status.akun.jenis === 'owner', sumber: sumberData().jenis, koleksiSiap: status.koleksiSiap, koleksiTotal: status.koleksiTotal,
    dariCache: Object.keys(_dariCache).filter((n) => _dariCache[n]).length, ditolak: status.ditolak.length, online: !status.offline && !(typeof navigator !== 'undefined' && navigator.onLine === false), hemat: gerbangHemat() });
}
kkPasangGerbang(gerbangKatalog);
async function terbitkanKatalogOtomatis() {
  if (!db || _kkJalan) return;
  const g = gerbangKatalog();
  if (!g.boleh) return;
  const isi = kkIsi(); if (!isi || kkTertinggal(isi) !== true) return;
  _kkJalan = true; const kini = new Date().toISOString();
  try {
    await Promise.race([setDoc(doc(db, KK_KOLEKSI, KK_ID), kkDokumen(isi, kini)), new Promise((_, t) => setTimeout(() => t(new Error('belum diakui server dalam 8 detik')), 8000))]);
    kkCatatTerbit(kini, '');
    if (_hemat) hbCatatTerbitKatalog(_ayunan, kkKanon(isi), Date.now());
  } catch (e) { kkCatatTerbit('', String((e && (e.code || e.message)) || e)); }
  finally { _kkJalan = false; beriTahu(); }
}
function pasangPenerbitKatalog() { if (_kkDipasang) return; _kkDipasang = true; dengarkan(() => jadwalkanKatalog()); window.addEventListener('online', () => jadwalkanKatalog()); }
/** Cabut SEMUA pendengar koleksi toko & kosongkan angka di memori (keluar, belum terdaftar, dinonaktifkan). */
function cabutPendengar() {
  // hemat baca: pendengar simpanan yang MATI (tab turun dari primer) tidak dilepas lewat unlisten (SDK 10.13 membaca targetId-nya tanpa penjaga → TypeError) —
  // aplikasi dimuat ulang; catatan di antrean Firestore tetap aman di perangkat
  if (_hemat && _hemat.adaMati() && typeof location !== 'undefined' && location.reload) { location.reload(); return; }
  if (_hemat) { _hemat.berhenti(); _hemat = null; status.hematPil = ''; status.hematMati = false; }
  _pendengarKoleksi.forEach((f) => { try { f(); } catch (e) { /* abaikan */ } }); _pendengarKoleksi = [];
  Object.keys(_antrePerKoleksi).forEach((n) => { delete _antrePerKoleksi[n]; }); status.antre = [];
  Object.keys(_dariCache).forEach((n) => { delete _dariCache[n]; }); kkLupakanServer(); clearTimeout(_kkTimer);
  status.koleksiSiap = 0; status.ditolak = []; status.galat = '';
  KOLEKSI.forEach((k) => { pasok(k.nama, []); setelTertunda(k.nama, []); });
}
// ---- salinan antre: sesudah semua pendengar siap, online, dan tidak ada tulisan tertunda — kiriman sesi lain dicocokkan ke server ----
let _cocokJalan = false;
function cocokkanAntre() {
  if (_cocokJalan || !antre.belumTerkirim().some((x) => x.sesi !== SESI)) return;
  _cocokJalan = true;
  waitForPendingWrites(db).then(() => { antre.cocokkanSesudahSinkron(cekDariCache(dokDiCache, kkMentah), new Date().toISOString()); segarkanLokal(); beriTahu(); })
    .catch(() => {}).finally(() => { _cocokJalan = false; });
}
export function antreLokal() { return { belum: antre.belumTerkirim(), ditolak: antre.ditolak() }; }
export function buangDitolak(id) { const ok = antre.buang(id); segarkanLokal(); beriTahu(); return ok; }
/** Owner menulis ulang kiriman yang ditolak ATAS NAMANYA (audit 39b no. 45): pencatat asli IKUT — kolom pencipta dibiarkan + pencatatAsli (susunTulisUlang);
 *  owner = penulis ulang (diubah* dari penulis pusat + baris jejak yang menyebut pencatat aslinya); salinannya dihapus bila berhasil. */
/** ubah (opsional, putaran 25): fungsi dokumen → dokumen, mis. kpKeHariIni (catatan bulan terkunci dicatat ulang bertanggal hari ini). Lewat penjaga pusat toko.js. */
export async function tulisUlangDitolak(id, ubah) {
  if (!status.akun || status.akun.jenis !== 'owner') return { gagal: true, pesan: 'Hanya owner yang boleh menulis ulang kiriman yang ditolak' };
  const x = antre.ditolak().find((y) => y.id === id); if (!x) return { gagal: true, pesan: 'Kiriman itu sudah tidak ada' };
  const T = susunTulisUlang(x); let bersih = T.dokumen;
  if (typeof ubah === 'function') bersih = ubah(bersih);
  const j = jagaKunci(bersih, []); if (j) return j;   // bulan terkunci / terlalu banyak pemeriksaan → tidak dikirim
  const r = await tulisBerkas(bersih, [], { pencatatAsli: T.asli }); if (r && r.gagal) return r;
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
// ---- denyut perangkat: dokumen perangkatStatus yang sama dengan sistem lama (denyut HP kasir), ditambah aplikasi 'baru', pemegang & lokasi ----
const KOLEKSI_PERANGKAT = 'perangkatStatus';
// Audit 39b no. 23: rules (stafDenyut) hanya membolehkan bukan-owner menimpa dokumen denyut yang akunUid-nya akun itu sendiri.
// Satu tablet dipakai bergiliran → dokumen {idPerangkat} terkunci ke akun pertama, akun berikutnya ditolak diam-diam.
// Bukan-owner menulis dokumen per (perangkat, akun) = {idPerangkat}~{uid}; owner tetap {idPerangkat} (rules: owner boleh menimpa).
// Antrean Firestore memang per akun (catatan akun yang keluar menunggu akun itu masuk lagi), jadi angka antrean per akun yang jujur.
const idDenyut = () => (status.akun && status.akun.jenis !== 'owner' ? idPerangkat() + '~' + status.akun.uid : idPerangkat());
let _denyutTerakhir = 0, _denyutTerpasang = false;
export function kirimDenyut(paksa) {
  if (!db || !status.masuk || !status.akun) return;
  const kini = Date.now(); if (!paksa && kini - _denyutTerakhir < 60000) return; _denyutTerakhir = kini;
  let akun = ''; try { akun = String((auth && auth.currentUser && auth.currentUser.email) || ''); } catch (e) { /* abaikan */ }
  let nama = ''; try { nama = localStorage.getItem('miqbal_perangkat_label_v1') || ''; } catch (e) { /* abaikan */ }
  // owner 7 Okt (hemat baca): versi HB_VERSI ('baru-c1') = perangkat ini menjalankan kode yang MENGECAP tulisannya (daftar siap-nyala; versi lain = penulis tanpa cap).
  // Denyut OWNER membawa capServer (jam server, gema = selisih jam perangkat — tanda air tidak memakai jam perangkat) + ringkasan hemat (perkiraan baca toko).
  // Denyut staf: kolom tetap (rules stafDenyut keys().hasOnly), hanya nilai versinya yang baru.
  try { const id = idDenyut(); const isi = { id, nama, akun, akunUid: status.akun.uid, aplikasi: 'baru', pada: new Date().toISOString(), antrean: status.antre.length, gagal: status.lokal.ditolak, versi: HB_VERSI, pemegang: pemegangPerangkat(), lokasi: lokasiPerangkat() || '' };
    if (status.akun.jenis === 'owner') { isi.capServer = serverTimestamp(); _denyutKirim = { pada: isi.pada, ms: Date.now() }; if (_hemat) isi.hemat = Object.assign({ nyala: true }, _hemat.ringkasDenyut()); }
    setDoc(doc(db, KOLEKSI_PERANGKAT, id), isi).catch(() => {}); }
  catch (e) { /* denyut bukan data uang — gagal = diam */ }
}
function pasangDenyut() {
  if (_denyutTerpasang) { kirimDenyut(); return; }
  _denyutTerpasang = true; kirimDenyut();
  document.addEventListener('visibilitychange', () => { if (!document.hidden) kirimDenyut(); if (_hemat) _hemat.terlihat(!document.hidden); });
  window.addEventListener('online', () => kirimDenyut());
  setInterval(() => { if (!document.hidden) kirimDenyut(); }, 300000);
  // hemat baca nyala: hitungan berkala koleksi HP kasir (30 menit), geser batas delta, klaim baca penuh harian (jam reset kuota), pendengar simpanan hidup
  setInterval(() => { if (_hemat && !document.hidden) _hemat.tik(); }, 60000);
}
const idUnik = () => Date.now() + Math.random();   // bentuk id yang sama dengan index.html
const konteksTulis = () => ({ perangkat: perangkatRingkas(), lokasi: lokasiPerangkat(), kini: new Date().toISOString() });
const pemilikSaja = () => (status.akun && status.akun.jenis === 'owner' ? '' : 'Hanya owner yang boleh melakukan ini');

// K6 (owner 25 Sep): pajakSetoran & pajakOmzetLuar TIDAK dikunci, jadi tiap ubah/hapus di sana menulis jejak lengkap dengan NILAI LAMA-nya (jejak penuh
// append-only = putaran 26). Dokumen kunci periode ikut: riwayatnya sudah di dokumennya, tapi jejak memegang salinan sebelum diubah.
const JEJAK_NILAI_LAMA = { pajakSetoran: 1, pajakOmzetLuar: 1, 'aturanToko/kunciPeriode': 1 };
const jejakKunci = (koleksi, id) => (JEJAK_NILAI_LAMA[koleksi] ? koleksi : koleksi + '/' + String(id));
/**
 * Tulis sekumpulan dokumen SEKALIGUS: daftar = [{ koleksi, data }], data.id wajib.
 * Satu writeBatch + satu baris log per dokumen (koleksi logAktivitas, seperti catatLogAktivitas index.html).
 * Mengembalikan { antre: true } segera bila tulisan masuk antrean (offline/menunggu server) — datanya sudah
 * hidup di cache lokal dan onSnapshot sudah menggambarkannya; { ok: true } bila server sudah mengaku.
 */
export async function tulisBerkas(daftar, hapus, opsi) {
  if (!db) throw new Error('belum tersambung');
  if (!status.masuk || !status.akun) throw new Error('belum masuk');
  const tolakHemat = jagaTulisHemat(); if (tolakHemat) return { gagal: true, pesan: tolakHemat };
  // owner 7 Okt (hemat baca nyala): tutup hari, titik kas, kunci bulan, tutup buku = UANG-KRITIS → semua koleksi hemat dipastikan cocok dengan server dulu
  // (hitungan ≤ 2 menit); belum bisa / beda = tidak dikirim (draf layar tetap ada). Saklar mati: _hemat null, baris ini tidak berbuat apa-apa.
  if (_hemat && status.akun.jenis === 'owner' && kirimanUangKritis(daftar)) { const g = await _hemat.pastikanSegar(); if (!g.ok) return { gagal: true, pesan: 'Belum disimpan — ' + g.pesan }; }
  const akun = status.akun; const owner = akun.jenis === 'owner'; const k = konteksTulis();
  // create atau update ditentukan dari cache (dokumen sudah ada?) — sama dengan cara server menilai set()
  const isi = daftar.map(({ koleksi, data }) => { const lama = dokDiCache(koleksi, data.id); return { koleksi, data, ada: !!lama, lama }; });
  const H = hapus || [];
  if (!owner) { const p = periksaKiriman(akun, isi, H, _sumberHak(), new Date()); if (p.tolak) return { gagal: true, pesan: p.tolak }; }   // pasti ditolak rules → tidak dikirim
  const b = writeBatch(db); const ditulis = [];
  isi.forEach((x) => {
    if (kkMentah(x.koleksi)) { b.set(doc(db, x.koleksi, String(x.data.id)), x.data); ditulis.push({ koleksi: x.koleksi, data: x.data }); return; }   // 25c: katalog kasir apa adanya — tanpa atribusi & jejak
    const d = beriAtribusiAkun(x.data, akun, k, x.ada);
    // owner 7 Okt: koleksi hemat bercap jam server (SESUDAH penjaga kiriman; salinan antre & `ditulis` tetap tanpa sentinel)
    b.set(doc(db, x.koleksi, String(d.id)), pasangCap(x.koleksi, d)); ditulis.push({ koleksi: x.koleksi, data: d });
    if (owner) {   // owner: satu baris jejak per dokumen, seperti catatLogAktivitas index.html (+ olehUid)
      const log = { id: idUnik(), pada: k.kini, aksi: d.dibatalkan ? 'batalkan' : (d.dikoreksiOleh ? 'tandai-koreksi' : 'tulis'),
        koleksi: x.koleksi, idDok: String(d.id), oleh: d.diubahOleh, olehUid: akun.uid, perangkat: k.perangkat, ringkas: ringkasDok(d) };
      if (x.lama && JEJAK_NILAI_LAMA[jejakKunci(x.koleksi, d.id)]) { log.aksi = 'ubah'; log.lama = x.lama; }   // K6: ubah pajak & dokumen kunci → nilai lamanya ikut di jejak
      // audit 39b no. 45: kiriman ditolak yang ditulis ulang owner — baris jejaknya menyebut pencatat asli
      // tinjauan P45-a: pencatat asli DOKUMENNYA bila sudah ada (tulis ulang kedua kali: kiriman yang ditolak itu milik owner, dokumennya tetap menyebut karyawan)
      const logT = opsi && opsi.pencatatAsli ? jejakTulisUlang(log, d.pencatatAsli || opsi.pencatatAsli) : log;
      b.set(doc(db, KOLEKSI_LOG, String(logT.id)), logT);
    }
  });
  // owner 7 Okt: tiap hapus koleksi hemat + BATU NISAN di batch yang SAMA (kabar hapus untuk perangkat yang hemat baca) — hanya sesudah aturan v7 terbukti,
  // dan hanya kalau batch tetap muat (≤ 490 tulisan; batas Firestore 500): tidak muat = hapus seperti dulu, nisannya ditulis pendeteksi harian
  const pakaiNisan = _nisanSah && isi.length * 2 + H.length * 2 + 1 + H.filter((x) => hbHemat(x.koleksi)).length <= 490;
  H.forEach((x) => {   // hanya owner sampai di sini (periksaKiriman menolak hapus bukan-owner)
    b.delete(doc(db, x.koleksi, String(x.id)));
    if (pakaiNisan && hbHemat(x.koleksi)) b.set(doc(db, HB_KOLEKSI_NISAN, nisanId(x.koleksi, x.id)), nisanDok(x.koleksi, x.id, akun.uid));
    if (_hemat) _hemat.catatHapus(x.koleksi, x.id);
    const log = { id: idUnik(), pada: k.kini, aksi: 'hapus', koleksi: x.koleksi, idDok: String(x.id), oleh: akun.nama, olehUid: akun.uid, perangkat: k.perangkat, ringkas: String((opsi && opsi.jejakHapus) || 'dihapus').slice(0, 200) };
    const lamaH = dokDiCache(x.koleksi, x.id); if (lamaH && JEJAK_NILAI_LAMA[jejakKunci(x.koleksi, x.id)]) log.lama = lamaH;   // K6: yang dihapus tetap terbaca di jejak
    b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
  });
  if (!owner) { const log = jejakKiriman(akun, ditulis, Object.assign({ idJejak: idUnik() }, k)); b.set(doc(db, KOLEKSI_LOG, String(log.id)), log); }   // SATU baris per kiriman, memuat daftar dokumennya
  // salinan antre SEBELUM dikirim; penuh = tidak dikirim (tidak ada salinan lama yang dibuang)
  const idKiriman = 'k-' + idUnik(); const s0 = antre.tambah({ id: idKiriman, pada: k.kini, akunUid: akun.uid, akunNama: akun.nama, peran: akun.peran, dokumen: ditulis });
  if (s0.tolak) return { gagal: true, pesan: s0.tolak };
  // putaran 3 AAL5: hapus di kiriman ini dicatat menunggu server sampai commit selesai (dokumennya sudah hilang dari cache — tutup buku menghitungnya 'tunggu')
  setelHapusTertunda(idKiriman, H); segarkanLokal(); status.menunggu += 1; beriTahu();
  const janji = b.commit().then(() => { antre.konfirmasi(idKiriman); return { ok: true }; })
    .catch((e) => { const kode = String((e && e.code) || e); antre.tandaiDitolak(idKiriman, kode, new Date().toISOString()); status.galat = 'tulis ditolak: ' + kode; beriTahu(); return { gagal: true, pesan: status.galat + ' — salinannya ada di Sistem › Perangkat (ditolak server)' }; })
    .finally(() => { setelHapusTertunda(idKiriman, null); segarkanLokal(); status.menunggu = Math.max(0, status.menunggu - 1); beriTahu(); });
  // tutup buku bertahap (opsi.tunggu): kiriman berikutnya hanya sesudah server MENGAKU yang ini — 30 detik tanpa jawaban = berhenti (kirimannya tetap di antrean
  // perangkat; kalau belakangan masuk, "Lanjutkan" melihatnya dari id-nya dan tidak mengirim ulang)
  if (opsi && opsi.tunggu) return Promise.race([janji, new Promise((r) => setTimeout(() => r({ antre: true, pesan: 'server belum mengaku dalam 30 detik' }), 30000))]);
  // tunggu sebentar: kalau server mengaku dalam 1,5 detik → ok; kalau tidak → antre (offline / lambat), bukan gagal
  return Promise.race([janji, new Promise((r) => setTimeout(() => r({ antre: true }), 1500))]);
}
export async function hapusBerkas(daftar) {
  if (!db) throw new Error('belum tersambung');
  if (!status.akun || status.akun.jenis !== 'owner') { const p = periksaKiriman(status.akun, [], daftar, _sumberHak()); return { gagal: true, pesan: p.tolak || 'Hanya owner yang boleh menghapus' }; }   // bukan-owner tidak pernah DELETE (peta §5)
  const tolakHemat = jagaTulisHemat(); if (tolakHemat) return { gagal: true, pesan: tolakHemat };
  const b = writeBatch(db);
  // owner 7 Okt: batu nisan ikut batch yang sama (lihat tulisBerkas)
  daftar.forEach(({ koleksi, id }) => { b.delete(doc(db, koleksi, String(id))); if (_nisanSah && hbHemat(koleksi) && daftar.length <= 240) b.set(doc(db, HB_KOLEKSI_NISAN, nisanId(koleksi, id)), nisanDok(koleksi, id, status.akun.uid)); if (_hemat) _hemat.catatHapus(koleksi, id); });
  return Promise.race([b.commit().then(() => ({ ok: true })), new Promise((r) => setTimeout(() => r({ antre: true }), 1500))]);
}
// ---- hemat baca: cap jam server, batu nisan, penjaga tulis (owner 7 Okt 2026, siap 2027) ----
// CAP: hanya koleksi HEMAT (koleksi.js tanpa `kelas`). Koleksi tetap TIDAK dicap: tutupBukuAcara (kirim ulang identik SDK wajib lolos tulisUlangSama v6),
// pesanan & perangkatStatus staf (rules membatasi kolomnya), aturanToko/pengaturan/aksesAkun/permintaanAkses (selalu didengar penuh), logAktivitas (jejak
// berbatas), ringkasanKasir (bentuk dokumen beku = sistem lama), arsipTahun (tidak didengar). alat-uji/uji_hemat_baca.py memeriksa SETIAP jalan tulis.
const pasangCap = (koleksi, d) => (hbHemat(koleksi) ? Object.assign({}, d, { capServer: serverTimestamp() }) : d);
const nisanId = (koleksi, id) => koleksi + '|' + String(id);
const nisanDok = (koleksi, id, uid) => ({ id: nisanId(koleksi, id), koleksi, idDok: String(id), capServer: serverTimestamp(), olehUid: uid });   // rules v7: capServer == request.time
const UANG_KRITIS = { tutupHari: () => true, tutupBukuAcara: () => true, pengaturan: (d) => String(d.id) === 'titikKas', aturanToko: (d) => String(d.id) === 'kunciPeriode' };
const kirimanUangKritis = (daftar) => (daftar || []).some((x) => UANG_KRITIS[x.koleksi] && UANG_KRITIS[x.koleksi](x.data || {}));
/** Saklar nyala: tab yang kalah kunci / pendengar simpanannya mati TIDAK menulis (datanya bisa basi). Mati: selalu ''. */
function jagaTulisHemat() {
  if (_berhenti) return _berhenti;
  if (!_hemat) return '';
  if (!_kunciTab.milik()) return 'Aplikasi sedang dipakai di tab lain peramban ini — tulisan dari tab ini ditolak. Pakai tab itu, atau muat ulang tab ini.';
  if (_hemat.adaMati()) return 'Tab ini berhenti menerima data dari server — muat ulang aplikasi dulu (catatan di antrean aman).';
  return '';
}
/** Pendeteksi (perangkat yang baca penuh harian / tombol Console): catatan yang berubah / lahir / LAHIR ULANG tanpa cap disentuh capServer — perangkat lain
 *  menerimanya lewat delta. Owner saja, per potongan KP_BATAS_GET (≤ 18 pemeriksaan kunci), catatan bulan terkunci dilewati, satu baris jejak per potongan.
 *  lihat(id) = isi MENTAH (snapshot server F / simpanan perangkat, SEBELUM saringan batu nisan): catatan lahir ulang yang tersembunyi nisan TIDAK ada di memori
 *  (dokDiCache), dan dulu tidak pernah disentuh (tinjauan 7 Okt). → { n, tunda, lewat }: tunda = id yang belum terkirim (tab tidak boleh menulis / potongan
 *  ditolak) — sesi hemat menyimpan & mengulangnya; lewat = id di bulan TERKUNCI (tidak bisa disentuh — perangkat lain tidak menerimanya lewat delta): dulu
 *  dibuang diam-diam, kini dilaporkan supaya sesi hemat menghitungnya (baca penuh harian toko `temuanTunda`, sanggahan 8 Okt). */
async function sentuhCap(koleksi, ids, lihat) {
  if (!db || !status.akun || status.akun.jenis !== 'owner' || !hbHemat(koleksi)) return { n: 0, tunda: [] };
  if (jagaTulisHemat()) return { n: 0, tunda: (ids || []).slice() };
  const isi = (id) => (typeof lihat === 'function' ? lihat(id) : dokDiCache(koleksi, id));
  const lewat = [];
  const boleh = (ids || []).filter((id) => { const d = isi(id); if (!d) return false; if (tolakKunci(koleksi, d)) { lewat.push(id); return false; } return true; });
  let n = 0; const tunda = [];
  for (let i = 0; i < boleh.length; i += POTONG) {
    const b = writeBatch(db); const potong = boleh.slice(i, i + POTONG);
    potong.forEach((id) => b.update(doc(db, koleksi, String(id)), { capServer: serverTimestamp() }));
    const log = { id: idUnik(), pada: new Date().toISOString(), aksi: 'sentuh-cap', koleksi, idDok: String(potong[0]), oleh: pemegangPerangkat(), olehUid: status.akun.uid, perangkat: perangkatRingkas(), ringkas: 'sentuh cap ' + potong.length + ' catatan (berubah / lahir tanpa cap jam server)' };
    b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
    try { await b.commit(); n += potong.length; } catch (e) { potong.forEach((id) => tunda.push(id)); }
  }
  return { n, tunda, lewat };
}
/** Pendeteksi: catatan yang hilang dari server tanpa batu nisan (Console, perangkat sebelum aturan v7) → nisannya ditulis sekarang. → { n, tunda } (lihat sentuhCap). */
async function tulisNisanSaja(koleksi, ids) {
  if (!db || !_nisanSah || !status.akun || status.akun.jenis !== 'owner' || !hbHemat(koleksi)) return { n: 0, tunda: [] };
  if (jagaTulisHemat()) return { n: 0, tunda: (ids || []).slice() };
  let n = 0; const tunda = [];
  for (let i = 0; i < (ids || []).length; i += 400) {
    const b = writeBatch(db); const potong = ids.slice(i, i + 400);
    potong.forEach((id) => b.set(doc(db, HB_KOLEKSI_NISAN, nisanId(koleksi, id)), nisanDok(koleksi, id, status.akun.uid)));
    const log = { id: idUnik(), pada: new Date().toISOString(), aksi: 'nisan', koleksi, idDok: String(potong[0]), oleh: pemegangPerangkat(), olehUid: status.akun.uid, perangkat: perangkatRingkas(), ringkas: 'batu nisan ' + potong.length + ' catatan yang hilang dari server tanpa kabar' };
    b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
    try { await b.commit(); n += potong.length; } catch (e) { potong.forEach((id) => tunda.push(id)); }
  }
  return { n, tunda };
}
/** Kunci tab kalah (tab lain menekan "Pakai di sini"): klien Firestore tab ini dihentikan — antrean IndexedDB dikirim klien pemegang. */
export async function berhenti(sebab) {
  _berhenti = String(sebab || 'Aplikasi dipakai di tab lain — tab ini berhenti. Muat ulang untuk memakainya di sini.');
  // _hemat sengaja TIDAK di-null-kan (layar tetap membaca keadaannya): sesi yang berhenti melapor SEMUA koleksi hemat "periksa — tidak diperbarui lagi di tab
  // ini" (hemat-baca.js belumK, sanggahan 8 Okt) — kartu pemeriksaan, kunci bulan, pajak & dokumen Laporan tidak lagi "lengkap" dari data yang membeku
  if (_hemat) { _hemat.berhenti(); }
  try { if (db) await terminate(db); } catch (e) { /* abaikan */ }
  status.galat = _berhenti; beriTahu();
}
// ---- hemat baca untuk layar (Menu › Sistem › Perangkat › Hemat baca) ----
export function setelSaklarHemat(nyala) { return hbSetelSaklar(_penyimpanHemat, !!nyala); }
/** Catatan koleksi hemat di perangkat ini TANPA cap jam server yang lahir/diubah sesudah kode bercap jalan di peramban ini (7 hari terakhir). Cap dari peta
 *  samping pendengar penuh (_cap, saklar mati) atau dari simpanan sesi hemat (saklar nyala — _cap koleksi hemat kosong, dulu SEMUA catatan terhitung
 *  "tanpa cap" dan baris statis berbohong; tinjauan 7 Okt). */
function hitungStatis() {
  const batas = Math.max(HB_MULAI_MS, _kodeBercap || 0, Date.now() - 7 * 86400000); let n = 0;
  hbKoleksiHemat().forEach((nama) => { const k = KOLEKSI.find((x) => x.nama === nama); const c = (_hemat ? _hemat.capPeta(nama) : _cap[nama]) || {}; if (!k) return; cacheMentah(k.cache).forEach((d) => { if (hbTanpaCapStatis(d, c[String(d.id)], batas)) n += 1; }); });
  return n;
}
/** Keadaan hemat baca perangkat ini untuk layar. Saklar nyala: `belumLengkap` = { koleksi: { jenis, sebab } } dari SATU sumber (hemat-baca.js hbBelumLengkap) —
 *  app.js lokalPerangkat meneruskannya ke Uang (kartu pemeriksaan sesudah tutup buku, kunci bulan, tutup buku) dan Laporan › Pajak. Mati / staf: { nyala: false }
 *  tanpa `belumLengkap` (pendengar penuh seperti sebelum 7 Okt — layar menghitung persis seperti dulu). */
export function hematKeadaan() {
  const owner = !!status.akun && status.akun.jenis === 'owner';
  const dasar = { saklar: _hematNyala, nisanSah: _nisanSah, nisanKabar: _nisanKabar, owner, berhenti: _berhenti, tabMilik: _kunciTab.milik(), ayunan: _ayunan.berhenti || '' };
  if (!_hemat) return Object.assign({ nyala: false, kabarMati: !_hematNyala ? '' : !owner ? 'akun staf selalu dengar penuh' : !_nisanSah ? 'menunggu aturan server v7 terbukti — muat ulang sesudah owner menerbitkannya' : 'muat ulang aplikasi untuk menyalakan' }, dasar);
  return Object.assign(_hemat.keadaan(), dasar);
}
export function hematSiapNyala() {
  // saklar nyala: umur denyut dinilai dengan jam SERVER saat denyut itu terlihat berubah (bukan `pada` = jam perangkat penulis); mati: seperti sebelumnya
  const s = _hemat ? _hemat.keadaan().kiniS : null;
  return hbSiapNyala({ perangkat: cacheMentah('perangkat'), kiniMs: s !== null ? s : Date.now(), lihat: _hemat ? _hemat.lihatDenyut() : null, nisanSah: _nisanSah, statis: hitungStatis(), ownerEmail: EMAIL_OWNER });
}
// tombol owner = manual (menembus rem kuota); tiap baca penuh juga mendeteksi & menyentuh ubahan tanpa cap (Console)
export function hematBacaPenuh(sebab) { if (!_hemat) return false; _hemat.bacaPenuh(null, sebab || 'tombol "Baca penuh sekarang"', true); beriTahu(); return true; }
export function hematMintaSemua() { if (!_hemat) return Promise.resolve({ gagal: true, pesan: 'Hemat baca belum menyala di perangkat ini' }); return _hemat.mintaSemua().then(() => ({ ok: true }), (e) => ({ gagal: true, pesan: String((e && e.code) || e) })); }

/** Putaran 23b (Bersihkan ciri yang dicabut): UPDATE kolom tertentu saja — TANPA beriAtribusi, supaya kolom lain byte-sama sebelum & sesudah.
 *  Satu writeBatch per potongan (≤ 200 dokumen); SATU baris log (jumlah saja, tanpa isi cip) di potongan terakhir. Berhenti di potongan yang ditolak. */
export async function perbaruiBerkas(potongan, ringkas) {
  if (!db) throw new Error('belum tersambung');
  if (!status.masuk) throw new Error('belum masuk sebagai owner');
  if (pemilikSaja()) return { gagal: true, potongan: [], pesan: pemilikSaja() };
  const hasil = [];
  for (let i = 0; i < potongan.length; i++) {
    const p = potongan[i]; const b = writeBatch(db);
    p.forEach((x) => b.update(doc(db, x.koleksi, String(x.id)), pasangCap(x.koleksi, x.kolom)));   // owner 7 Okt: ubah kolom koleksi hemat ikut bercap
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

// ---- ARSIP TAHUN (putaran 18, Tutup buku): pindah ke koleksi arsipTahun per potongan ----
// Langsung ke server (menunggu commit, bukan 1,5 detik): ritual ini wajib internet & satu perangkat. Satu baris log per potongan, bukan per dokumen.
// Putaran 25: rules v4 memeriksa kunci periode untuk tiap dokumen bulan lampau yang dihapus/ditulis ulang (1 get() per dokumen, cache tidak diandalkan),
// jadi potongan dari 200 turun ke KP_BATAS_GET (18) — kalau tidak, kiriman arsip pertama ditolak sesudah saldo pembuka terlanjur tertulis (stok dobel).
// rules v7 (owner 7 Okt, K8; sanggahan 7 Okt): bulan TERKUNCI tahun itu lewat PINTU TUTUP BUKU — hapus 3 access call (kunci + pintu + salinan arsip sesudah batch)
// + tulis salinan 2 (kunci + catatan asli); bulan lampau terbuka 1 + 1. biaya = access call per catatan dari toko.js (kunci-periode.js); potongan ≤ 18 catatan
// DAN ≤ 18 access call (kpPecahBiaya). Tanpa biaya = 1 per catatan (seperti dulu).
const KOLEKSI_ARSIP = 'arsipTahun';
const POTONG = KP_BATAS_GET;
export async function arsipkanBerkas(tahun, daftar, progres, biaya) {
  if (!db) throw new Error('belum tersambung');
  if (!status.masuk) throw new Error('belum masuk sebagai owner');
  if (pemilikSaja()) throw new Error(pemilikSaja());
  let sudah = 0;
  for (const [i, j] of kpPecahBiaya(biaya || daftar.map(() => 1), POTONG, KP_BATAS_GET)) {
    const b = writeBatch(db); const potong = daftar.slice(i, j);
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
export async function pulihkanBerkas(tahun, daftar, progres, biaya) {
  if (!db) throw new Error('belum tersambung');
  if (!status.masuk) throw new Error('belum masuk sebagai owner');
  if (pemilikSaja()) throw new Error(pemilikSaja());
  let sudah = 0;
  for (const [i, j] of kpPecahBiaya(biaya || daftar.map(() => 1), POTONG, KP_BATAS_GET)) {
    const b = writeBatch(db); const potong = daftar.slice(i, j);
    // owner 7 Okt: catatan yang dikembalikan bercap jam server BARU (isinya tetap isi lama) — perangkat hemat baca menerimanya lewat delta
    potong.forEach((x) => { b.set(doc(db, x.koleksi, String(x.idAsli)), pasangCap(x.koleksi, x.dok)); b.delete(doc(db, KOLEKSI_ARSIP, tahun + '|' + x.koleksi + '|' + x.idAsli)); });
    const log = { id: idUnik(), pada: new Date().toISOString(), aksi: 'pulihkan', koleksi: KOLEKSI_ARSIP, idDok: String(tahun), oleh: pemegangPerangkat(), olehUid: status.akun.uid, perangkat: perangkatRingkas(), ringkas: 'batal tutup buku ' + tahun + ': ' + potong.length + ' dokumen dikembalikan' };
    b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
    await b.commit();
    sudah += potong.length; if (progres) progres(sudah, daftar.length);
  }
  return { ok: true, n: sudah };
}

// ---- FOTO BON (owner 7 Okt 2026): koleksi `fotoBon` TIDAK ada di KOLEKSI → tidak didengar, tidak ikut baca penuh harian, cache TOKO (toko.js), maupun cadangan
// berkas. Dibaca SEKALI saat lembar bon dibuka; ditulis/dihapus langsung tanpa salinan antre lokal milik aplikasi (satu foto ±300 KB — kuota localStorage).
// JUJURNYA: db memakai persistentLocalCache (atas), jadi Firestore sendiri menyimpan foto yang pernah dibaca & yang menunggu kirim di IndexedDB perangkat
// (dibersihkan Firestore sesuai batas cache bawaannya, ±40 MB). Kiriman yang belum diakui dalam 20 detik → { antre, selesai } — `selesai` = janji akhir
// kiriman itu (diakui / ditolak), supaya layar tidak menyebut foto tersimpan sebelum server mengakuinya. Foto yang dibaca dari cache dengan kiriman yang
// belum diakui bertanda `antre`. Owner saja. Butuh blok rules `fotoBon` (rules v7, diterbitkan owner) — sebelum terbit server menolak (permission-denied).
const KOLEKSI_FOTO_BON = 'fotoBon';
const tungguServer = (janji, ms) => Promise.race([janji.then((x) => ({ x })), new Promise((r) => setTimeout(() => r({ lewat: true }), ms))]);
export async function bacaFotoBon(idBon) {
  if (!db) throw new Error('belum tersambung');
  if (pemilikSaja()) throw new Error(pemilikSaja());
  const h = await tungguServer(getDocs(query(collection(db, KOLEKSI_FOTO_BON), where('idBon', '==', String(idBon)))), 15000);
  if (h.lewat) throw new Error('server belum menjawab dalam 15 detik');
  const out = []; h.x.forEach((d) => out.push(Object.assign({}, d.data(), d.metadata && d.metadata.hasPendingWrites ? { antre: true } : {}))); out.dariCache = !!(h.x.metadata && h.x.metadata.fromCache); return out;
}
export async function simpanFotoBon(data) {
  if (!db) throw new Error('belum tersambung');
  if (pemilikSaja()) return { gagal: true, pesan: pemilikSaja() };
  const akun = status.akun; const k = konteksTulis(); const d = beriAtribusiAkun(data, akun, k, false);
  const b = writeBatch(db); b.set(doc(db, KOLEKSI_FOTO_BON, String(d.id)), d);
  const log = { id: idUnik(), pada: k.kini, aksi: 'tulis', koleksi: KOLEKSI_FOTO_BON, idDok: String(d.id), oleh: akun.nama, olehUid: akun.uid, perangkat: k.perangkat, ringkas: 'foto bon ' + String(d.idBon) + ' · ' + Math.round((Number(d.byte) || 0) / 1024) + ' KB' };
  b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
  const janji = b.commit();
  try { const h = await tungguServer(janji, 20000); return h.lewat ? { antre: true, data: d, selesai: janji.then(() => ({ ok: true }), (e) => ({ gagal: true, pesan: String((e && (e.code || e.message)) || e) })) } : { ok: true, data: d }; }
  catch (e) { return { gagal: true, pesan: String((e && (e.code || e.message)) || e) }; }
}
export async function hapusFotoBon(id, idBon) {
  if (!db) throw new Error('belum tersambung');
  if (pemilikSaja()) return { gagal: true, pesan: pemilikSaja() };
  const akun = status.akun; const k = konteksTulis(); const b = writeBatch(db); b.delete(doc(db, KOLEKSI_FOTO_BON, String(id)));
  const log = { id: idUnik(), pada: k.kini, aksi: 'hapus', koleksi: KOLEKSI_FOTO_BON, idDok: String(id), oleh: akun.nama, olehUid: akun.uid, perangkat: k.perangkat, ringkas: 'foto bon ' + String(idBon || '') + ' dihapus' };
  b.set(doc(db, KOLEKSI_LOG, String(log.id)), log);
  try { const h = await tungguServer(b.commit(), 20000); return h.lewat ? { antre: true } : { ok: true }; }
  catch (e) { return { gagal: true, pesan: String((e && (e.code || e.message)) || e) }; }
}
