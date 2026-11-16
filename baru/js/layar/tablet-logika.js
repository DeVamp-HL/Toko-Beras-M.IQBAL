// TABLET KASIR — SATU AKUN TABLET + PIN PER ORANG (putaran T1 langkah 3, 16 Nov 2026). Logika TANPA DOM & tanpa Firebase — dijaga
// alat-uji/uji_tablet_pin.py (jsc + kontrol). Gambar: layar Menu › Toko ini › Peran & persetujuan › Orang di tablet (owner) dan panel "Siapa yang jaga?" (app.js).
//
// Keputusan owner 16 Nov 2026: salah PIN 5 kali → nama itu terkunci 5 menit (orang lain tetap bisa masuk dengan PIN-nya); layar kembali ke "Siapa yang
// jaga?" sesudah 5 menit tidak disentuh; modal boleh tersimpan di tablet asal tidak tampil di layar staf; owner di tablet jualan saja pakai PIN — urusan
// owner (uang, harga, laporan) tetap di HP/Mac owner.
//
// Tempat: aturanToko/peran.operator = { <id>: { nama, peran: 'ben'|'karyawan', aktif, garam, acak, iterasi, dibuat, diubah } } — dokumen yang SUDAH dibaca
// akun staf (rules v7 aturanToko 'peran') dan hanya ditulis owner. Tanpa ubahan rules.
// Orang yang jaga menggantikan NAMA akun tablet (oleh / diubahOleh di tiap catatan, pemegang di denyut) dan PERAN LAYAR-nya (kisi SS2); uid tetap uid
// akun tablet (rules jujur()), server tetap menegakkan peran akun tablet. Peran orang tidak pernah lebih tinggi dari peran akun tablet.
// PIN = siapa yang mencatat, BUKAN pengaman data: sandi akun tablet yang menjaga data toko. Disimpan sebagai PBKDF2-SHA256 (garam acak per orang).
import { ssAtur, susunAturSistem, SS_MAKS_ORANG_TABLET } from './sistem-logika.js';
import { PERAN_BUKAN_OWNER, NAMA_PERAN, bisaBekerja } from '../data/akses.js';

export const TB_BATAS_SALAH = 5;                    // owner 16 Nov
export const TB_LAMA_KUNCI_MS = 5 * 60 * 1000;      // owner 16 Nov
export const TB_LAMA_DIAM_MS = 5 * 60 * 1000;       // owner 16 Nov
export const TB_ITERASI = 100000;                   // PBKDF2-SHA256; ±0,1–0,3 detik sekali periksa di tablet
export const TB_MAKS_ORANG = SS_MAKS_ORANG_TABLET;   // bentuk yang ditulis dijaga sistem-logika ssBersihkanOrangTablet (susunAturSistem 'peran')
export const TB_KUNCI_SALAH = 'miqbal_tablet_pin_salah_v1';   // localStorage PERANGKAT (app.js): { <id>: { n, sampai } } — tahan muat ulang
export const TB_PERAN = PERAN_BUKAN_OWNER.map((p) => ({ id: p, nama: NAMA_PERAN[p] || p }));

const tbTeks = (v) => String(v === undefined || v === null ? '' : v).trim();

/** Daftar orang di tablet, urut nama. peta = aturanToko/peran.operator (kosong = dari cache: ssAtur('peran')). */
export function tbDaftar(peta) {
  const P = peta === undefined ? (ssAtur('peran').operator || {}) : (peta || {});
  return Object.keys(P).map((id) => { const o = P[id] || {}; return { id, nama: tbTeks(o.nama), peran: PERAN_BUKAN_OWNER.indexOf(o.peran) >= 0 ? o.peran : 'karyawan',
    namaPeran: NAMA_PERAN[o.peran] || 'Karyawan', aktif: o.aktif !== false, garam: tbTeks(o.garam), acak: tbTeks(o.acak), iterasi: Number(o.iterasi) || TB_ITERASI,
    dibuat: tbTeks(o.dibuat), diubah: tbTeks(o.diubah) }; })
    .filter((o) => o.nama).sort((a, b) => a.nama.localeCompare(b.nama, 'id'));
}

/**
 * Keadaan gerbang orang untuk akun yang masuk. daftar = tbDaftar(); siap = data toko sudah termuat (koleksi lengkap) — sebelum itu daftar bisa belum datang.
 * 'bukan' = tidak ada gerbang (owner, belum bisa bekerja, atau akun staf tanpa daftar orang) · 'muat' = akun staf, daftar belum datang · 'pilih' = wajib PIN.
 * Ada satu orang saja di daftar (meski libur) = gerbang menyala: owner yang meliburkan semua orang tidak membuka tablet tanpa PIN.
 */
export function tbKeadaan(akun, daftar, siap) {
  if (!akun || !bisaBekerja(akun) || akun.jenis === 'owner') return 'bukan';
  if ((daftar || []).length) return 'pilih';
  return siap ? 'bukan' : 'muat';
}
/** Akun yang dipakai layar & penulis selagi orang `op` jaga: nama & peran orang itu, uid/email akun tablet. Peran tidak pernah melebihi akun tablet. */
export function tbEfektif(akun, op) {
  if (!akun || !op) return akun;
  const peran = akun.peran === 'karyawan' ? 'karyawan' : op.peran;
  return Object.assign({}, akun, { nama: op.nama, peran, operatorId: op.id, akunNama: akun.nama });
}
/** Akun tablet yang menunggu orang (gerbang 'pilih' / 'muat'): TIDAK bisa bekerja → tirai menutup layar, isian tidak dibuang. */
export function tbMenunggu(akun, keadaan) {
  return Object.assign({}, akun, { jenis: 'pilihOrang', peran: null, akunNama: akun.nama, kalimat: keadaan === 'muat' ? 'Memuat daftar orang…' : 'Siapa yang jaga?' });
}

// ---------- PIN ----------
/** PIN boleh dipakai? '' = boleh; selain itu kalimatnya. 4–6 angka; bukan angka kembar semua (0000) dan bukan urutan (1234, 9876). */
export function tbPinSah(pin) {
  const p = String(pin === undefined || pin === null ? '' : pin);
  if (!/^[0-9]{4,6}$/.test(p)) return 'PIN harus 4–6 angka';
  if (/^(\d)\1+$/.test(p)) return 'PIN tidak boleh angka kembar semua — terlalu mudah ditebak';
  const naik = p.split('').every((c, i) => i === 0 || Number(c) === (Number(p[i - 1]) + 1) % 10);
  const turun = p.split('').every((c, i) => i === 0 || Number(c) === (Number(p[i - 1]) + 9) % 10);
  if (naik || turun) return 'PIN tidak boleh angka berurutan — terlalu mudah ditebak';
  return '';
}
const tbHex = (buf) => Array.prototype.map.call(new Uint8Array(buf), (b) => ('0' + b.toString(16)).slice(-2)).join('');
const tbBait = (s) => { const t = String(s); const u = new Uint8Array(t.length); for (let i = 0; i < t.length; i++) u[i] = t.charCodeAt(i) & 0xff; return u; };   // PIN & garam = ASCII
const tbSubtleBawaan = () => (typeof crypto !== 'undefined' && crypto && crypto.subtle ? crypto.subtle : null);
/** PIN → 64 huruf hex: PBKDF2-SHA256(pin, garam, iterasi), 256 bit. subtle = crypto.subtle (diganti di uji). */
export async function tbTurunkan(pin, garam, iterasi, subtle) {
  const S = subtle || tbSubtleBawaan(); if (!S) throw new Error('Perangkat ini tidak bisa memeriksa PIN (butuh alamat https)');
  const kunci = await S.importKey('raw', tbBait(pin), { name: 'PBKDF2' }, false, ['deriveBits']);
  const bit = await S.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt: tbBait(garam), iterations: Number(iterasi) || TB_ITERASI }, kunci, 256);
  return tbHex(bit);
}
/** Garam acak per orang: 'g' + 32 huruf tbHex (16 bait acak). acak = crypto.getRandomValues (diganti di uji). */
export function tbGaram(acak) {
  const u = new Uint8Array(16); const f = acak || (typeof crypto !== 'undefined' && crypto && crypto.getRandomValues ? (x) => crypto.getRandomValues(x) : null);
  if (!f) throw new Error('Perangkat ini tidak punya pembangkit acak'); f(u); return 'g' + tbHex(u.buffer);
}
const tbSama = (a, b) => { const x = String(a), y = String(b); if (x.length !== y.length) return false; let d = 0; for (let i = 0; i < x.length; i++) d |= x.charCodeAt(i) ^ y.charCodeAt(i); return d === 0; };

// ---------- salah PIN (per perangkat, per orang) ----------
/** Keadaan salah satu orang: { terkunci, sisaMs, salah } — kunci yang sudah lewat = bersih lagi. */
export function tbStatusSalah(peta, id, kini) {
  const r = (peta || {})[id] || {}; const t = Number(kini) || 0; const sampai = Number(r.sampai) || 0;
  if (sampai > t) return { terkunci: true, sisaMs: sampai - t, salah: TB_BATAS_SALAH };
  if (sampai) return { terkunci: false, sisaMs: 0, salah: 0 };
  return { terkunci: false, sisaMs: 0, salah: Math.max(0, Number(r.n) || 0) };
}
/** Catat satu salah → peta baru. Salah ke-5 = terkunci 5 menit (hitungan mulai dari nol lagi sesudahnya). */
export function tbCatatSalah(peta, id, kini) {
  const P = Object.assign({}, peta || {}); const s = tbStatusSalah(P, id, kini); if (s.terkunci) return P;
  const n = s.salah + 1; P[id] = n >= TB_BATAS_SALAH ? { n: 0, sampai: (Number(kini) || 0) + TB_LAMA_KUNCI_MS } : { n, sampai: 0 }; return P;
}
export function tbBersihSalah(peta, id) { const P = Object.assign({}, peta || {}); delete P[id]; return P; }
const tbMenit = (ms) => Math.max(1, Math.ceil(ms / 60000));

/**
 * Periksa PIN orang `op`. Kembali { ok, peta (salah PIN sesudahnya), kalimat }. Libur / terkunci = tidak diperiksa (tidak menambah hitungan salah).
 * subtle = crypto.subtle (diganti di uji).
 */
export async function tbPeriksa(op, pin, peta, kini, subtle) {
  if (!op) return { ok: false, peta: peta || {}, kalimat: 'Pilih nama dulu' };
  if (!op.aktif) return { ok: false, peta: peta || {}, kalimat: op.nama + ' sedang libur — minta owner mengaktifkan di Menu › Toko ini › Peran & persetujuan' };
  const s = tbStatusSalah(peta, op.id, kini);
  if (s.terkunci) return { ok: false, peta: peta || {}, kalimat: op.nama + ' terkunci karena salah PIN ' + TB_BATAS_SALAH + ' kali — coba lagi ' + tbMenit(s.sisaMs) + ' menit lagi' };
  if (!/^[0-9]{4,6}$/.test(String(pin || ''))) return { ok: false, peta: peta || {}, kalimat: 'PIN 4–6 angka' };
  if (!op.garam || !/^[0-9a-f]{64}$/.test(op.acak)) return { ok: false, peta: peta || {}, kalimat: 'PIN ' + op.nama + ' belum diatur — minta owner mengaturnya' };
  const acak = await tbTurunkan(pin, op.garam, op.iterasi, subtle);
  if (tbSama(acak, op.acak)) return { ok: true, peta: tbBersihSalah(peta, op.id), kalimat: '' };
  const P = tbCatatSalah(peta, op.id, kini); const s2 = tbStatusSalah(P, op.id, kini);
  return { ok: false, peta: P, kalimat: s2.terkunci ? 'PIN salah ' + TB_BATAS_SALAH + ' kali — ' + op.nama + ' terkunci ' + tbMenit(TB_LAMA_KUNCI_MS) + ' menit. Orang lain tetap bisa masuk.'
    : 'PIN salah — sisa ' + (TB_BATAS_SALAH - s2.salah) + ' kali sebelum ' + op.nama + ' terkunci ' + tbMenit(TB_LAMA_KUNCI_MS) + ' menit' };
}
/** Sudah waktunya layar kembali ke "Siapa yang jaga?" (tidak disentuh 5 menit)? */
export const tbHarusKunci = (terakhirSentuh, kini) => (Number(kini) || 0) - (Number(terakhirSentuh) || 0) >= TB_LAMA_DIAM_MS;

// ---------- owner: mengatur orang di tablet (dokumen aturanToko/peran lewat susunAturSistem — kolom lain ikut utuh) ----------
const tbSalinPeta = () => JSON.parse(JSON.stringify(ssAtur('peran').operator || {}));
const tbSimpan = (peta, w, kabar) => { const r = susunAturSistem('peran', { operator: peta }, w); if (r.tolak) return r; r.patch = { kabar, kabarAwas: false }; return r; };
function tbNamaSah(nama, peta, kecuali) {
  const n = tbTeks(nama); if (n.length < 2) return 'Ketik nama orangnya (minimal dua huruf)'; if (n.length > 30) return 'Nama paling panjang 30 huruf';
  if (Object.keys(peta).some((id) => id !== kecuali && tbTeks(peta[id].nama).toLowerCase() === n.toLowerCase())) return 'Nama "' + n + '" sudah ada di daftar';
  return '';
}
const tbIdBaru = (w) => 'o' + (Date.parse(w.kini) || Date.now()).toString(36) + Math.floor(Math.random() * 1296).toString(36);

/** Tambah orang: isi = { nama, peran, pin, pin2 }. alat = { subtle, acak } (uji). Kembali { dokumen, patch } | { tolak }. */
export async function tbSusunTambah(isi, w, alat) {
  const A = alat || {}; const peta = tbSalinPeta(); const i = isi || {};
  if (Object.keys(peta).length >= TB_MAKS_ORANG) return { tolak: 'Paling banyak ' + TB_MAKS_ORANG + ' orang di tablet' };
  const tn = tbNamaSah(i.nama, peta, null); if (tn) return { tolak: tn };
  if (PERAN_BUKAN_OWNER.indexOf(i.peran) < 0) return { tolak: 'Pilih perannya: ' + TB_PERAN.map((p) => p.nama).join(' atau ') };
  const tp = tbPinSah(i.pin); if (tp) return { tolak: tp }; if (String(i.pin) !== String(i.pin2)) return { tolak: 'PIN kedua tidak sama dengan yang pertama' };
  const garam = tbGaram(A.acak); const acak = await tbTurunkan(String(i.pin), garam, TB_ITERASI, A.subtle);
  const id = A.id || tbIdBaru(w); peta[id] = { nama: tbTeks(i.nama), peran: i.peran, aktif: true, garam, acak, iterasi: TB_ITERASI, dibuat: w.kini, diubah: w.kini };
  return tbSimpan(peta, w, tbTeks(i.nama) + ' bisa masuk di tablet dengan PIN-nya — berlaku begitu tablet tersambung');
}
/** Ganti PIN satu orang (owner). */
export async function tbSusunGantiPin(id, pin, pin2, w, alat) {
  const A = alat || {}; const peta = tbSalinPeta(); const o = peta[id]; if (!o) return { tolak: 'Orang ini tidak ada di daftar' };
  const tp = tbPinSah(pin); if (tp) return { tolak: tp }; if (String(pin) !== String(pin2)) return { tolak: 'PIN kedua tidak sama dengan yang pertama' };
  const garam = tbGaram(A.acak); o.garam = garam; o.acak = await tbTurunkan(String(pin), garam, TB_ITERASI, A.subtle); o.iterasi = TB_ITERASI; o.diubah = w.kini;
  return tbSimpan(peta, w, 'PIN ' + o.nama + ' diganti — PIN lama tidak berlaku lagi begitu tablet tersambung');
}
/** Aktif / libur (owner). Libur = namanya tetap tampil di tablet tapi tidak bisa masuk. */
export function tbSusunAktif(id, aktif, w) {
  const peta = tbSalinPeta(); const o = peta[id]; if (!o) return { tolak: 'Orang ini tidak ada di daftar' };
  o.aktif = !!aktif; o.diubah = w.kini;
  return tbSimpan(peta, w, o.nama + (aktif ? ' aktif lagi di tablet' : ' diliburkan — tidak bisa masuk di tablet sampai diaktifkan lagi'));
}
/** Ubah peran (owner). */
export function tbSusunPeran(id, peran, w) {
  const peta = tbSalinPeta(); const o = peta[id]; if (!o) return { tolak: 'Orang ini tidak ada di daftar' };
  if (PERAN_BUKAN_OWNER.indexOf(peran) < 0) return { tolak: 'Peran tidak dikenal' };
  o.peran = peran; o.diubah = w.kini; return tbSimpan(peta, w, o.nama + ' kini ' + (NAMA_PERAN[peran] || peran) + ' di tablet');
}
/** Hapus orang (owner, dua ketukan di layar). Catatan lama tetap menyebut namanya (nama tertulis di catatannya, bukan diambil dari daftar ini). */
export function tbSusunHapus(id, w) {
  const peta = tbSalinPeta(); const o = peta[id]; if (!o) return { tolak: 'Orang ini tidak ada di daftar' };
  delete peta[id];
  return tbSimpan(peta, w, o.nama + ' dihapus dari tablet' + (Object.keys(peta).length ? '' : ' — daftar kosong: akun tablet kembali bekerja TANPA PIN'));
}

