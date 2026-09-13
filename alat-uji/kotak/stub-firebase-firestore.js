// Kotak pasir tulis-nol: pengganti firebase-firestore. "Server"-nya adalah window.__data
// (benih dari berkas backup). setDoc/deleteDoc MENERAPKAN ke server kotak lalu menggema ke
// pendengar — seperti Firestore — dan semuanya tercatat di window.__rekam.
//   window.__terapkan(nama, arr)   snapshot koleksi dari "server" (SINKRON: galat di callback
//                                  naik ke pemanggil supaya bisa diukur)
//   window.__terapkanDok(kol, id)  snapshot dokumen (mis. pengaturan/titikKas)
//   window.__setDocGagal = true    simulasi offline: setDoc menolak
//   window.__urutanAwal            'koleksiDulu' (bawaan) | 'pengaturanDulu' — urutan snapshot awal
const D = () => (window.__data || (window.__data = {}));
const pendengar = {}, pendengarDok = {};
window.__rekam = [];
window.__setDocGagal = false;
window.__urutanAwal = window.__urutanAwal || 'koleksiDulu';
function dokPeta(nama, id) {
  const arr = D()[nama] || [];
  let x = arr.find(y => String(y.id) === String(id));
  if (!x && nama === 'pengaturan' && window.__peta) {
    if (window.__peta[id]) x = window.__peta[id];                                   // mis. titikKas: dokumen apa adanya
    else { const p = window.__peta['peta' + id.charAt(0).toUpperCase() + id.slice(1)]; if (p) x = { id: id, peta: p }; }   // jenisBeras/tempatSimpan: bentuk dokumen {id, peta}
  }
  return x;
}
function snapKoleksi(nama) {
  const arr = D()[nama] || [];
  const docs = arr.map(x => ({ data: () => x, id: String(x.id) }));
  return { forEach(f) { docs.forEach(f); }, docs, size: docs.length, empty: docs.length === 0 };
}
function snapDok(nama, id) { const x = dokPeta(nama, id); return { exists: () => !!x, data: () => x, id: String(id) }; }
export function getFirestore() { return {}; }
export function collection(db, n) { return { _kol: n }; }
export function doc(db, n, id) { return { _kol: n, _id: String(id) }; }
export function query(q) { return q; }
export function orderBy() { return {}; }
export function limit() { return {}; }
export function onSnapshot(ref, cb) {
  const dokDulu = window.__urutanAwal === 'pengaturanDulu';
  if (ref._id) {
    const k = ref._kol + '/' + ref._id;
    (pendengarDok[k] = pendengarDok[k] || []).push(cb);
    setTimeout(() => cb(snapDok(ref._kol, ref._id)), dokDulu ? 0 : 5);
  } else {
    (pendengar[ref._kol] = pendengar[ref._kol] || []).push(cb);
    setTimeout(() => cb(snapKoleksi(ref._kol)), dokDulu ? 5 : 0);
  }
  return () => {};
}
window.__terapkan = (nama, arr) => { D()[nama] = arr; (pendengar[nama] || []).forEach(cb => cb(snapKoleksi(nama))); };
window.__terapkanDok = (kol, id) => { (pendengarDok[kol + '/' + id] || []).forEach(cb => cb(snapDok(kol, id))); };
function terapkanTulis(kol, id, data) {
  const arr = D()[kol] || (D()[kol] = []);
  const salinan = JSON.parse(JSON.stringify(data));
  const i = arr.findIndex(x => String(x.id) === String(id));
  if (i >= 0) arr[i] = salinan; else arr.push(salinan);
  window.__terapkan(kol, arr);
  window.__terapkanDok(kol, id);
}
// CATATAN: gema ke pendengar di sini SINKRON di dalam panggilan setDoc — beda dari Firestore (pendengar
// dijalankan belakangan, terpisah dari pemanggil). Akibatnya galat di pendengar bocor ke catch pemanggil
// (simpanKeFirestore lalu memasukkannya ke antrean tunda). Uji tulis WAJIB menegaskan __antrean().length === 0
// di akhir. window.__setDocLambat = ms menunda resolve untuk mengeksekusi jalur timeout (4/8 dtk).
export function setDoc(ref, data) {
  window.__rekam.push({ kol: ref._kol, id: ref._id, data });
  if (window.__setDocGagal) return Promise.reject(new Error('kotak: setDoc dimatikan (simulasi offline)'));
  terapkanTulis(ref._kol, ref._id, data);
  const lambat = Number(window.__setDocLambat) || 0;
  return lambat ? new Promise(r => setTimeout(r, lambat)) : Promise.resolve();
}
export function deleteDoc(ref) {
  window.__rekam.push({ hapus: true, kol: ref._kol, id: ref._id });
  const arr = (D()[ref._kol] || []).filter(x => String(x.id) !== String(ref._id));
  window.__terapkan(ref._kol, arr);
  return Promise.resolve();
}
export function runTransaction(db, fn) {
  const tx = { get: r => Promise.resolve(snapDok(r._kol, r._id)),
    set: (r, d) => { window.__rekam.push({ tx: true, kol: r._kol, id: r._id, data: d }); terapkanTulis(r._kol, r._id, d); },
    update: (r, d) => { window.__rekam.push({ tx: true, kol: r._kol, id: r._id, data: d }); const lama = dokPeta(r._kol, r._id) || {}; terapkanTulis(r._kol, r._id, Object.assign({}, lama, d)); },
    delete: () => {} };
  return fn(tx);
}
