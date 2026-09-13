// Kotak pasir tulis-nol: pengganti firebase-auth. Akun owner dianggap sudah masuk.
export function getAuth() { return { currentUser: null }; }
export function setPersistence() { return Promise.resolve(); }
export function signInWithEmailAndPassword() { return Promise.resolve({}); }
export const browserLocalPersistence = {};
export function onAuthStateChanged(auth, cb) {
  setTimeout(() => cb({ email: window.__emailKotak || 'owner@tokoberasmiqbal.web.app' }), 0);
  return () => {};
}
