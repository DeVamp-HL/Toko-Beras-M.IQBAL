// HET BERAS (paket brief awal butir 8, 9 Okt 2026) — harga eceran tertinggi pemerintah dibandingkan dengan Katalog harga. Logika tanpa DOM, nama berawalan het
// (bundel uji satu lingkup). Dijaga alat-uji/uji_harga_baru.py (kotak pasir + --kontrol + asap cadangan toko).
// SETELAN = dokumen aturanToko/het (owner saja; layar Harga memang owner saja, staf tidak membacanya): zona, HET medium & premium per kg, sumber angka,
// dan PETA { kelas/merek: 'premium' | 'medium' | 'bukan' }. Angka bawaan = dokumen owner (Kepbadan 299/2025, Zona I): medium Rp13.500/kg, premium
// Rp14.900/kg — bisa diubah owner di Atur; layar menyebut sumbernya. Menyimpan pemetaan TIDAK menulis angka: yang belum pernah diatur owner tetap bawaan.
// SATUAN PEMETAAN = KELAS TOKO (nama wadah IR64 Ascent/Elevate/Apex, IR42 Value/Select · kelas tanpa wadah · merek yang dipilih jadi kelas) atau MEREK tanpa
// kelas. Kelas sebuah merek = kmKelasMerk yang SUDAH dikonfirmasi owner (kmTerisi); kelas TEBAKAN tidak dipakai (sama dengan harga kelas di Belanja) —
// mereknya berdiri sendiri sampai owner memilih kelasnya. 'bukan' = bukan beras HET (ketan, beras khusus, …): tidak pernah dibandingkan.
// SEBELUM dipetakan tidak ada peringatan: baris itu "belum dipetakan", BUKAN "aman" (tiga keadaan kosong). Harga per kg = cara katalog menghitung
// (harga-logika nilaiHarga: harga ÷ kg satuannya — per kg ÷ 1 · kemasan/karung utuh ÷ ukuran · literan ÷ kg per liter RASIO_KONVERSI / 0,82).
// Di atas HET = per kg LEBIH dari HET (selisih pecahan literan tetap dihitung); tepat = HET tidak awas. Peringatan MEMPERINGATKAN, tidak memblokir
// terbit — owner yang memutuskan. Hitungan menutup: di atas + sama/di bawah + belum dipetakan + bukan beras HET + belum ada harga = semua baris katalog.
import { RP, DESIMAL } from '../inti/format.js';
import { cacheMentah } from '../data/toko.js';
import { hgSemua, nilaiHarga } from './harga-logika.js';
import { aturWadah } from './jual-logika.js';
import { kmKelasMerk, kmTerisi, kmPeta } from './kelas-merek-logika.js';

export const HET_ID = 'het';
export const HET_BAWAAN = { zona: 'Zona I', medium: 13500, premium: 14900, sumber: 'Kepbadan 299/2025' };
export const HET_KATEGORI = [['premium', 'premium'], ['medium', 'medium'], ['bukan', 'bukan beras HET']];
export const HET_JENIS_UNIT = { wadah: 'kelas berwadah', sendiri: 'kelas tanpa wadah', kelas: 'kelas', merek: 'merek tanpa kelas' };
const HET_NAMA = { premium: 'premium', medium: 'medium', bukan: 'bukan beras HET' };
const HET_KOLOM = ['zona', 'medium', 'premium', 'sumber'];
const hetBersih = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const hetKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const hetAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim().replace(/^rp\s*/i, ''); if (!t) return NaN;
  const n = Number(/^\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t.replace(',', '.')); return isFinite(n) ? n : NaN; };
/** Rupiah selisih: di bawah Rp1 tetap disebut pecahannya (tidak dibulatkan jadi "Rp0"). */
const hetRp = (x) => (Math.round(x) >= 1 ? RP(x) : 'Rp' + DESIMAL(x));
const hetDok = () => cacheMentah('aturan').find((d) => String(d.id) === HET_ID) || null;

/** Setelan HET yang berlaku: angka owner bila ada, selain itu angka bawaan (dokumen owner). angkaOwner = owner pernah menyimpan angka/zona/sumber. */
export function hetAtur() {
  const d = hetDok(); const angka = (k) => (d && isFinite(Number(d[k])) && Number(d[k]) > 0 ? Math.round(Number(d[k])) : null);
  const teks = (k) => (d && hetBersih(d[k]) ? hetBersih(d[k]) : null);
  const p = d && d.peta && typeof d.peta === 'object' && !Array.isArray(d.peta) ? d.peta : {}; const peta = {};
  Object.keys(p).forEach((u) => { if (HET_NAMA[p[u]]) peta[u] = p[u]; });
  const medium = angka('medium'), premium = angka('premium'), zona = teks('zona'), sumber = teks('sumber');
  const angkaOwner = medium !== null || premium !== null || zona !== null || sumber !== null;
  const A = { zona: zona === null ? HET_BAWAAN.zona : zona, medium: medium === null ? HET_BAWAAN.medium : medium, premium: premium === null ? HET_BAWAAN.premium : premium,
    sumber: sumber === null ? HET_BAWAAN.sumber : sumber, peta, angkaOwner, ada: !!d, tanggal: d ? String(d.tanggal || '') : '' };
  A.sumberTeks = angkaOwner ? 'angka owner' + (A.tanggal ? ' (disimpan ' + A.tanggal + ')' : '') + ' · sumber: ' + A.sumber + ' · ' + A.zona
    : 'angka bawaan dari dokumen owner: ' + HET_BAWAAN.sumber + ', ' + HET_BAWAAN.zona + ' — bisa diubah di Atur';
  return A;
}

/** Satuan pemetaan satu merek → { unit, jenis, tebakan }. Kelas yang sudah dikonfirmasi owner; selain itu merek itu sendiri (tebakan disebut). */
export function hetUnit(merk) {
  const m = hetBersih(merk); if (!m) return { unit: '', jenis: '', tebakan: '' };
  const K = kmKelasMerk(m);
  if (K.kelas && kmTerisi(K.asal)) {
    const wadah = aturWadah().daftar.indexOf(K.kelas) >= 0; const sendiri = kmPeta().kelasSendiri.indexOf(K.kelas) >= 0;
    return { unit: K.kelas, jenis: wadah ? 'wadah' : sendiri ? 'sendiri' : 'kelas', tebakan: '' };
  }
  return { unit: m, jenis: 'merek', tebakan: K.asal === 'tebakan' && K.kelas ? K.kelas : '' };
}

/** SATU tempat menilai harga per kg terhadap HET kategori itu. status: atas · dalam · belum (belum dipetakan) · bukan (bukan beras HET) · kosong (belum ada harga). */
export function hetNilai(perKg, kategori, A) {
  if (!HET_NAMA[kategori]) return { status: 'belum', het: 0, lebih: 0, lebihTeks: '', teks: 'HET: kelas/merek ini belum dipetakan' };
  if (kategori === 'bukan') return { status: 'bukan', het: 0, lebih: 0, lebihTeks: '', teks: 'bukan beras HET — tidak dibandingkan' };
  const het = A[kategori]; if (!(perKg > 0)) return { status: 'kosong', het, lebih: 0, lebihTeks: '', teks: 'belum ada harga — HET ' + kategori + ' ' + RP(het) + '/kg' };
  const lebih = perKg - het;
  if (lebih > 1e-6) return { status: 'atas', het, lebih, lebihTeks: hetRp(lebih), teks: 'di atas HET ' + RP(het) + '/kg (+' + hetRp(lebih) + ')' };
  return { status: 'dalam', het, lebih, lebihTeks: '', teks: lebih > -1e-6 ? 'tepat HET ' + kategori + ' ' + RP(het) + '/kg' : 'di bawah HET ' + kategori + ' ' + RP(het) + '/kg (−' + hetRp(-lebih) + ')' };
}

/** Harga per kg satu baris katalog = nilaiHarga (harga-logika) — satu cara hitung dengan papan & lembar ubah. */
const hetPerKg = (n, st) => (n > 0 ? nilaiHarga(n, 0, st.kg, 0, false).perKg : 0);
const hetHargaTeks = (n, st, perKg) => (!(n > 0) ? 'belum ada harga' : st.id === 'S' ? RP(n) + '/kg' : RP(n) + (st.id === 'L' ? '/L' : ' per ' + st.per + ' ' + st.pendek) + ' = ' + RP(perKg) + '/kg');

/**
 * Katalog vs HET. S = hgSemua(kini). pakai: 'tampil' (bawaan — harga yang tampil di papan owner, draf ikut) · 'terbit' (harga yang dipakai kasir, untuk dasbor).
 * → { atur, baris, per {k: baris}, units, unitBelum, tidakDipakai, hit {atas, dalam, belum, bukan, kosong}, total, keadaan, judul, rincian, atas }.
 */
export function hetKatalog(S, pakai) {
  const A = hetAtur(); const terbit = pakai === 'terbit'; const memo = {}; const unit = (m) => memo[m] || (memo[m] = hetUnit(m));
  const units = {}; const per = {};
  const baris = S.baris.map((b) => {
    const U = unit(b.merk); const kategori = A.peta[U.unit] || ''; const n = terbit ? b.lamaN : b.n; const perKg = hetPerKg(n, b.st); const N = hetNilai(perKg, kategori, A);
    const u = units[U.unit] || (units[U.unit] = { unit: U.unit, jenis: U.jenis, jenisTeks: HET_JENIS_UNIT[U.jenis] || '', tebakan: U.tebakan, kategori, anggota: [], nBaris: 0, nAtas: 0 });
    if (u.anggota.indexOf(b.merk) < 0) u.anggota.push(b.merk); u.nBaris += 1; if (N.status === 'atas') u.nAtas += 1;
    const x = Object.assign({ k: b.k, merk: b.merk, judul: b.judul, satuan: b.st.id, n, perKg, unit: U.unit, jenisUnit: U.jenis, kategori, adaDraf: b.adaDraf, hargaTeks: hetHargaTeks(n, b.st, perKg) }, N);
    per[b.k] = x; return x;
  });
  const W = aturWadah().daftar; const rank = (u) => (u.jenis === 'wadah' ? 0 : u.jenis === 'sendiri' ? 1 : u.jenis === 'kelas' ? 2 : 3);
  const daftarUnit = Object.keys(units).map((k) => units[k]).sort((a, b) => rank(a) - rank(b) || (a.jenis === 'wadah' ? W.indexOf(a.unit) - W.indexOf(b.unit) : 0) || a.unit.localeCompare(b.unit));
  const unitBelum = daftarUnit.filter((u) => !u.kategori).map((u) => u.unit);
  const tidakDipakai = Object.keys(A.peta).filter((u) => !units[u]).sort((a, b) => a.localeCompare(b));
  const hit = { atas: 0, dalam: 0, belum: 0, bukan: 0, kosong: 0 }; baris.forEach((x) => { hit[x.status] += 1; });
  const total = baris.length; const atas = baris.filter((x) => x.status === 'atas').sort((a, b) => b.lebih - a.lebih);
  const keadaan = !total ? 'kosong' : unitBelum.length === daftarUnit.length ? 'belum' : unitBelum.length ? 'sebagian' : 'lengkap';
  const belumTeks = 'belum dipetakan: ' + unitBelum.length + ' kelas/merek';
  const judul = keadaan === 'kosong' ? 'Katalog belum punya baris harga' : keadaan === 'belum' ? belumTeks + ' — peringatan HET belum menyala'
    : (hit.atas ? hit.atas + ' harga di atas HET' : keadaan === 'lengkap' ? 'tidak ada harga di atas HET' : 'tidak ada harga di atas HET dari yang sudah dipetakan') + (unitBelum.length ? ' · ' + belumTeks : '');
  const bagian = [[hit.atas, 'di atas HET'], [hit.dalam, 'sama/di bawah HET'], [hit.belum, 'belum dipetakan'], [hit.bukan, 'bukan beras HET'], [hit.kosong, 'belum ada harga']].filter((x) => x[0] > 0);
  const rincian = !total ? '' : 'Dari ' + total + ' harga' + (terbit ? ' yang dipakai kasir' : '') + ': ' + bagian.map((x) => x[0] + ' ' + x[1]).join(' · ') + '.';
  return { atur: A, pakai: terbit ? 'terbit' : 'tampil', baris, per, units: daftarUnit, unitBelum, tidakDipakai, hit, total, keadaan, judul, rincian, atas, nAtas: hit.atas };
}
/** Untuk dasbor kelak: harga yang SEDANG dipakai kasir (sudah terbit) vs HET. */
export function hetHargaKasir(kini) { return hetKatalog(hgSemua(kini), 'terbit'); }

/** Sebelum terbit: tiap baris DRAF dinilai dengan harga barunya. Memperingatkan, tidak memblokir. */
export function hetDraf(S) {
  const H = hetKatalog(S, 'tampil'); const daftar = H.baris.filter((x) => x.adaDraf); const nAtas = daftar.filter((x) => x.status === 'atas').length; const nBelum = daftar.filter((x) => x.status === 'belum').length;
  const teks = (nAtas ? nAtas + ' harga draf di atas HET ' + H.atur.zona + ' — boleh terbit; owner yang memutuskan.' : '') + (nBelum ? (nAtas ? ' ' : '') + nBelum + ' harga draf belum bisa dibandingkan dengan HET (kelas/merek belum dipetakan).' : '');
  return { daftar, per: H.per, nAtas, nBelum, teks, atur: H.atur };
}
/** Lembar ubah: harga yang sedang diketik untuk satu baris (b dari hgSemua) dinilai terhadap HET kelasnya. */
export function hetSatuHarga(b, n) {
  if (!b) return null; const A = hetAtur(); const U = hetUnit(b.merk); const perKg = hetPerKg(Math.round(Number(n) || 0), b.st);
  return Object.assign({ unit: U.unit, kategori: A.peta[U.unit] || '', perKg }, hetNilai(perKg, A.peta[U.unit] || '', A));
}

/** Simpan setelan HET (owner): zona, medium, premium, sumber. Kolom kosong = nilai yang berlaku. Peta ikut utuh. */
export function susunAturHet(isi, w) {
  const o = isi || {}; const kini = hetAtur();
  const baca = (k, nama) => { if (hetKosong(o[k])) return { n: kini[k] }; const n = hetAngka(o[k]); if (!(n > 0 && n <= 100000 && Math.round(n) === n)) return { tolak: 'HET ' + nama + ' harus rupiah bulat per kg, 1–100.000' }; return { n }; };
  const M = baca('medium', 'medium'); if (M.tolak) return { tolak: M.tolak }; const P = baca('premium', 'premium'); if (P.tolak) return { tolak: P.tolak };
  if (P.n < M.n) return { tolak: 'HET premium ' + RP(P.n) + ' lebih rendah dari medium ' + RP(M.n) + ' — tertukar?' };
  const zona = hetBersih(o.zona).slice(0, 24) || kini.zona; const sumber = hetBersih(o.sumber).slice(0, 80) || kini.sumber;
  const data = { id: HET_ID, tanggal: w.tanggal, jam: w.jam, diubahPada: w.kini, zona, medium: M.n, premium: P.n, sumber, peta: Object.assign({}, kini.peta) };
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { hetBuka: false, aturHet: null, kabar: 'HET disimpan — ' + zona + ': medium ' + RP(M.n) + '/kg · premium ' + RP(P.n) + '/kg (sumber: ' + sumber + '). Tanda HET di katalog ikut berganti.', kabarAwas: false } };
}
/** Owner memetakan satu kelas/merek katalog → premium · medium · bukan; '' = lepas (kembali belum dipetakan). Angka setelan tidak ikut ditulis bila belum pernah diatur. */
export function susunPetaHet(unit, kategori, w) {
  const u = hetBersih(unit); const k = String(kategori || '');
  if (!u) return { tolak: 'Pilih kelas/merek-nya dulu' }; if (k && !HET_NAMA[k]) return { tolak: 'Pilihan HET tidak dikenal: ' + k };
  const A = hetAtur(); const H = hetKatalog(hgSemua(new Date(w.kini))); const ada = H.units.find((x) => x.unit === u);
  if (!ada && !(k === '' && A.peta[u])) return { tolak: u + ' tidak ada di katalog — HET dipetakan untuk kelas/merek yang punya baris harga' };
  if ((A.peta[u] || '') === k) return { tolak: u + (k ? ' sudah ' + HET_NAMA[k] : ' memang belum dipetakan') };
  const peta = Object.assign({}, A.peta); if (k) peta[u] = k; else delete peta[u];
  const d = hetDok(); const data = { id: HET_ID, tanggal: w.tanggal, jam: w.jam, diubahPada: w.kini, peta };
  HET_KOLOM.forEach((x) => { if (d && d[x] !== undefined && d[x] !== null) data[x] = d[x]; });
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { kabar: !k ? u + ' dilepas — kembali belum dipetakan, harganya tidak dibandingkan dengan HET' : u + ' → ' + HET_NAMA[k] + (k === 'bukan' ? ' — harganya tidak dibandingkan dengan HET' : ' — dibandingkan dengan HET ' + RP(A[k]) + '/kg'), kabarAwas: false } };
}
