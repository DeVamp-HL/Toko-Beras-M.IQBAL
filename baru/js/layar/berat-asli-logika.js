// STOK IKUT TIMBANG — BERAT ASLI KARUNG (Tahap 6, owner 25 Nov 2026). Tanpa DOM, tanpa Firestore; mesin beku tidak disentuh.
//
// Kata owner: "50 kg hanya tampilan saja, padahal isinya bukan benar-benar 50 kg, termasuk ketika jual ke customer … aslinya yang terjual 49,8 kg sesuai
// hasil timbang sewaktu kedatangan." Keputusan: stok satu nama dari beberapa kedatangan berberat beda → karung TERLAMA dulu (FIFO per kedatangan), bukan
// rata-rata buku.
//
// Bahan: baris kedatangan yang ikut timbang menyimpan `kgTerima` (kg hasil timbang / perkiraan sampel yang dibukukan). Faktor baris = kgTerima ÷ (jumlah
// karung × isi karung nota) — mis. 15 karung 50 kg, sampel rata-rata 49,8 → kgTerima 747 → faktor 0,996 → satu karung "50 kg" = 49,8 kg. Baris lama tanpa
// kgTerima (dan karung hasil adukan) faktornya 1: berat asli = isi karung nota, persis seperti dulu.
//
// Urutan karung: LAPISAN = baris kedatangan (+ karung utuh hasil adukan) per nama buku, diurut tanggal lalu id — sama dengan lapisan modal FIFO mesin
// (modal-fifo.js). Sisa buku S kg selalu = S kg TERAKHIR dari jejeran itu (yang keluar selalu yang paling lama), jadi yang keluar berikutnya berada di
// depan sisa itu. Nota karung utuh n × "50 kg" = jumlah kg asli yang diambil dari depan: tiap bagian lapisan menyumbang (kg nominal × faktornya).
// Buku yang TIDAK punya satu pun baris ikut timbang → angka lama persis (karung × isi), supaya data tanpa kolom baru byte-sama.
import { ambilSemuaBatch, ambilProduksiBerlaku, ingatStokKarung, ingatPerVersi } from '../data/toko.js';

const baB2 = (n) => Math.round(n * 100) / 100;
const BA_EPS = 1e-9;

/** Faktor berat asli satu baris kedatangan (kgTerima ÷ kg nota); baris tanpa kgTerima = 1. */
export function baFaktorBaris(m) {
  const kt = Number(m && m.kgTerima); const nota = (Number(m && m.jumlahKarung) || 0) * (Number(m && m.beratKarung) || 0);
  return isFinite(kt) && kt > 0 && nota > 0 ? kt / nota : 1;
}

/** { nama buku: [{ kg, faktor, id, tanggal }] } — lapisan terlama dulu. Diingat per versi data. */
export function baLapisan() {
  return ingatPerVersi('baLapisan', () => {
    const daftar = [];
    ambilSemuaBatch().forEach((b) => (b.merkList || []).forEach((m, i) => {
      if (!m || m.bentuk === 'bal' || !m.merk || !(Number(m.totalKg) > 0)) return;
      daftar.push({ merk: String(m.merk), kg: Number(m.totalKg), faktor: baFaktorBaris(m), id: Number(b.id) || 0, tanggal: String(b.tanggal || ''), i });
    }));
    ambilProduksiBerlaku().forEach((pr) => { if (!pr || !pr.jadiKarungUtuh || !pr.merkTujuan) return; const kg = (Number(pr.ukuranKemasan) || 0) * (Number(pr.jumlahUnit) || 0);
      if (kg > 0) daftar.push({ merk: String(pr.merkTujuan), kg, faktor: 1, id: Number(pr.id) || 0, tanggal: String(pr.tanggal || ''), i: 0 }); });
    daftar.sort((x, y) => x.tanggal.localeCompare(y.tanggal) || x.id - y.id || x.i - y.i);
    const out = {}; daftar.forEach((x) => { (out[x.merk] = out[x.merk] || []).push({ kg: x.kg, faktor: x.faktor, id: x.id, tanggal: x.tanggal }); });
    return out;
  });
}

/** Buku ini punya baris kedatangan yang ikut timbang (faktor ≠ 1)? Tidak → semua pembaca memakai angka lama persis. */
export function baAda(merk) { const L = baLapisan()[String(merk || '')]; return !!L && L.some((x) => Math.abs(x.faktor - 1) > BA_EPS); }

/**
 * Sisa buku sesudah `dipegang` kg keluar lebih dulu, sebagai potongan lapisan dari yang TERLAMA: [{ kg, faktor, i, penuh }]. Sisa melebihi jejeran
 * (retur / opname lebih) dianggap di depan lapisan pertama, berfaktor lapisan pertama (sama dengan modal FIFO). fAkhir = faktor lapisan terbaru.
 */
export function baAntre(merk, dipegang) {
  const L = baLapisan()[String(merk || '')] || []; const S = (((ingatStokKarung()[merk] || {}).sisaKg) || 0) - (Number(dipegang) || 0);
  const fAkhir = L.length ? L[L.length - 1].faktor : 1; const seg = [];
  let sisa = S;
  for (let i = L.length - 1; i >= 0 && sisa > BA_EPS; i--) { const k = Math.min(L[i].kg, sisa); seg.unshift({ kg: k, faktor: L[i].faktor, i, penuh: k >= L[i].kg - BA_EPS }); sisa -= k; }
  if (sisa > BA_EPS) seg.unshift({ kg: sisa, faktor: L.length ? L[0].faktor : 1, i: -1, penuh: true });
  return { seg, fAkhir, lapisan: L, sisaKg: S };
}

/**
 * Kg ASLI n karung berlabel `berat` kg (n kelipatan ½) yang keluar berikutnya dari buku merk, sesudah `dipegang` kg keluar lebih dulu.
 * Buku tanpa baris ikut timbang → n × berat (angka lama persis). Melewati sisa buku (jual dulu, cocokkan kemudian) → faktor kedatangan terbaru.
 */
export function baKgKarung(merk, berat, n, dipegang) {
  const N0 = (Number(n) || 0) * (Number(berat) || 0); if (!baAda(merk)) return (Number(n) || 0) * (Number(berat) || 0);
  const A = baAntre(merk, dipegang); let N = N0, kg = 0;
  for (let k = 0; k < A.seg.length && N > BA_EPS; k++) { const s = A.seg[k]; const cap = s.kg / s.faktor; const ambil = Math.min(N, cap); kg += ambil * s.faktor; N -= ambil; }
  if (N > BA_EPS) kg += N * A.fAkhir;
  return baB2(kg);
}

/** Langit-langit karung (kelipatan ½) dari sisa buku sesudah `dipegang` — null = buku tanpa baris ikut timbang (pakai rumus mesin stokMaksJalur). */
export function baMaksKarung(merk, berat, dipegang) {
  if (!baAda(merk) || !(Number(berat) > 0)) return null;
  const A = baAntre(merk, dipegang); const nominal = A.seg.reduce((a, s) => a + s.kg / s.faktor, 0);
  return Math.max(0, Math.floor(nominal / berat * 2 + 1e-6) / 2);
}

/** Kg nominal (label karung) dari `kg` kg asli TERBARU di buku (tumpukan gudang = karung yang paling akhir datang). */
function baNominalTerbaru(merk, kg) {
  const L = baLapisan()[String(merk || '')] || []; let sisa = Number(kg) || 0, nom = 0;
  for (let i = L.length - 1; i >= 0 && sisa > BA_EPS; i--) { const k = Math.min(L[i].kg, sisa); nom += k / L[i].faktor; sisa -= k; }
  if (sisa > BA_EPS) nom += sisa / (L.length ? L[0].faktor : 1);
  return nom;
}

/** Jumlah karung utuh berlabel `berat` di tumpukan berisi `kg` kg asli (karung terbaru). Buku tanpa baris ikut timbang = floor(kg ÷ berat) seperti dulu. */
export function baKarungTumpukan(merk, kg, berat) {
  if (!baAda(merk)) return Math.max(0, Math.floor((kg + 0.0001) / berat));
  return Math.max(0, Math.floor((baNominalTerbaru(merk, Math.max(0, kg)) + 0.0001) / berat));
}

/** Kg ASLI dari karung utuh yang DIHITUNG di tumpukan (n50 × 50 + n25 × 25 nominal) — karung yang paling akhir datang. Buku tanpa baris ikut timbang = nominal. */
export function baKgTumpukan(merk, nominal) {
  const N0 = Number(nominal) || 0; if (!baAda(merk)) return N0;
  const L = baLapisan()[String(merk || '')] || []; let N = N0, kg = 0;
  for (let i = L.length - 1; i >= 0 && N > BA_EPS; i--) { const cap = L[i].kg / L[i].faktor; const ambil = Math.min(N, cap); kg += ambil * L[i].faktor; N -= ambil; }
  if (N > BA_EPS) kg += N * (L.length ? L[0].faktor : 1);
  return baB2(kg);
}

/**
 * Kg ASLI karung yang KEMBALI ke buku tanpa nota (retur ketik tangan): karung yang terakhir keluar = lapisan tepat di depan sisa buku sekarang.
 * Buku tanpa baris ikut timbang = n × berat.
 */
export function baKgKembali(merk, berat, n) {
  const N0 = (Number(n) || 0) * (Number(berat) || 0); if (!baAda(merk)) return N0;
  const A = baAntre(merk, 0); let f;
  if (!A.seg.length) f = A.fAkhir;
  else { const d = A.seg[0]; f = d.i >= 0 && !d.penuh ? d.faktor : d.i > 0 ? A.lapisan[d.i - 1].faktor : d.faktor; }
  return baB2(N0 * f);
}

/** Berat asli satu karung berlabel `berat` yang keluar berikutnya (tampilan: "isi asli ± 49,8 kg"). */
export const baBeratBerikut = (merk, berat, dipegang) => baKgKarung(merk, berat, 1, dipegang);
