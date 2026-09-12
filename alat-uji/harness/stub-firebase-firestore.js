const noop = () => {};
export function getFirestore() { return {}; }
export function collection(db, n) { return { _n: n }; }
export function doc(db, n, id) { return { _n: n, _id: id }; }
export function setDoc() { return Promise.resolve(); }
export function deleteDoc() { return Promise.resolve(); }
export function onSnapshot() { return noop; }
export function runTransaction() { return Promise.resolve(); }
export function query(q) { return q; }
export function orderBy() { return {}; }
export function limit() { return {}; }
