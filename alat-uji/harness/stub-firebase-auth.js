export function getAuth() { return { currentUser: null }; }
export function signInWithEmailAndPassword() { return Promise.resolve({}); }
export function onAuthStateChanged() { return () => {}; }
export function setPersistence() { return Promise.resolve(); }
export const browserLocalPersistence = {};
