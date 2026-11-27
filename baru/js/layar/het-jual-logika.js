// HET DI NOTA & REKAP HET PER MINGGU (paket P7, owner 27 Nov 2026; sensus ulang 27 Nov A15 · A132). Logika tanpa DOM, BACA SAJA, nama berawalan hj (bundel uji
// jsc satu lingkup). Dijaga alat-uji/uji_pelanggan_het_p7.py (kotak pasir + statis + --kontrol + asap cadangan toko).
//
// Keputusan owner 27 Nov 2026: baris beras di nota yang harga per kg-nya DI ATAS HET = CUMA DITANDAI — nota tetap tersimpan siapa pun yang mencatat; tandanya
// tampil di Bayar (lembar nego ikut menyebutnya) dan di rekap HET Laporan › Mingguan. Tidak ada yang ditahan, tidak ada kolom baru di nota: tanda = penilaian
// ulang baris nota dengan aturan Harga › HET (satu sumber: hetAtur · hetUnit · hetNilai di het-logika.js — tidak ada rumus HET kedua).
//
// HARGA PER KG satu baris = harga satuan yang dibayar ÷ kg satu satuannya (cara katalog menghitung, harga-logika nilaiHarga):
//   karung ÷ berat label karung (beratKarungAcuan, bawaan 50) · kemasan ÷ ukuran kemasan · literan ÷ kg per liter yang dipakai nota (rasioPakai) · repack = per kg.
//   Harga satuan: baris keranjang = hargaSatuan (sesudah harga pelanggan usaha / grosir / nego); nota tersimpan = hargaAsliSatuan + negoSelisih (kolom yang ditulis
//   susunNotaDokumen). Potongan nota TIDAK dihitung (harga di rak yang dinilai, potongan hanya menurunkan). Kemasan berbonus: harga per unit yang dibayar.
// MEREK untuk HET = nama yang dipakai baris katalognya: kemasan = nama produk, literan dari wadah = nama wadah, selain itu merek karungnya — buku per ukuran
// ('Merek 25 kg', petaUkuran) memakai harga merek INDUKNYA di katalog, jadi kelas HET-nya juga kelas induknya.
// TIDAK DINILAI: wadah/kantong yang dijual (bukan beras), barang pengganti retur (harganya Rp0), nota nominal kasir darurat & nota lama tanpa harga satuan
// ("tidak bisa dinilai" — disebut jumlahnya, bukan dianggap patuh). Kelas/merek yang belum dipetakan owner = "belum dipetakan" — BUKAN patuh.
// Akun staf tidak membaca setelan HET (aturanToko/het, rules) → di perangkat staf tanda Bayar tidak digambar; rekap mingguan (owner) menilai SEMUA nota.
import { ambilPenjualan, tahunDiarsip, petaUkuran, ingatPerVersi } from '../data/toko.js';
import { RP, DESIMAL, KG, tanggalPendek } from '../inti/format.js';
import { hetAtur, hetUnit, hetNilai } from './het-logika.js';

export const HJ_JENIS = ['karung', 'kemasan', 'literan', 'repacking'];
export const HJ_STATUS = [['atas', 'di atas HET'], ['dalam', 'sama/di bawah HET'], ['belum', 'kelas belum dipetakan'], ['bukan', 'bukan beras HET'], ['takBisa', 'tidak bisa dinilai']];
const hjBersih = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const hjAngka = (v) => { const n = Number(v); return v !== undefined && v !== null && v !== '' && isFinite(n) ? n : null; };
const hjRp = (x) => (Math.round(x) >= 1 ? RP(x) : 'Rp' + DESIMAL(x));

/** Nama yang dipakai baris katalog untuk barang ini (penentu kelas HET). */
export function hjMerk(p, U0) {
  if (!p) return ''; if (p.jenis === 'kemasan') return hjBersih(p.namaProduk);
  const m = hjBersih(p.jenis === 'literan' ? p.dariWadah || p.merkSumber : p.merkSumber); const U = U0 || petaUkuran();
  return U[m] && U[m].induk ? hjBersih(U[m].induk) : m;
}
/** Kg satu satuan harga baris ini; null = tidak diketahui. */
export function hjKgSatuan(p) {
  if (!p) return null; const a = (v) => { const n = hjAngka(v); return n !== null && n > 0 ? n : null; };
  if (p.jenis === 'karung') return a(p.beratKarungAcuan) || 50;
  if (p.jenis === 'kemasan') return a(p.ukuranKemasan);
  if (p.jenis === 'literan') return a(p.rasioPakai);
  if (p.jenis === 'repacking') return 1;
  return null;
}
/** Harga satuan yang dibayar: baris keranjang (hargaSatuan) atau nota tersimpan (hargaAsliSatuan + negoSelisih). null = nota lama / nominal. */
export function hjHargaSatuan(p) {
  if (!p) return null; const hs = hjAngka(p.hargaSatuan); if (hs !== null) return hs;
  const asli = hjAngka(p.hargaAsliSatuan); if (asli === null) return null; return asli + (hjAngka(p.negoSelisih) || 0);
}
/** Banyak satuan yang DIBAYAR (bonus kemasan tidak). keranjang: jumlah · nota: kolom per jenis. */
function hjJumlahBayar(p) {
  const j = hjAngka(p.jumlah); if (j !== null && hjAngka(p.hargaSatuan) !== null) return j;
  if (p.jenis === 'karung') return hjAngka(p.jumlahKarung) || 0;
  if (p.jenis === 'kemasan') return Math.max(0, (hjAngka(p.jumlahUnit) || 0) - (hjAngka(p.bonusUnit) || 0));
  if (p.jenis === 'literan') return hjAngka(p.jumlahLiter) || 0;
  return hjAngka(p.totalKg) || 0;
}

/**
 * Nilai satu baris (keranjang atau nota) terhadap HET. A = hetAtur(), U = petaUkuran() (boleh dikirim supaya satu rekap memakai satu setelan & satu peta).
 * → null (bukan baris beras: wadah, pengganti retur) | { status 'atas'|'dalam'|'belum'|'bukan'|'takBisa', merk, unit, kategori, perKg, het, lebih, kg, rpLebih, teks, sebab }.
 */
export function hjNilaiBaris(p, A0, U0, M0) {
  if (!p || p.penggantiRetur || p.jenis === 'wadah') return null;
  if (HJ_JENIS.indexOf(p.jenis) < 0) return { status: 'takBisa', sebab: p.jenis === 'kasir_darurat_nominal' ? 'nota nominal (tanpa barang)' : 'jenis ' + hjBersih(p.jenis || '?'), merk: '', unit: '', kategori: '', perKg: 0, het: 0, lebih: 0, kg: 0, rpLebih: 0, teks: 'tidak bisa dinilai' };
  const A = A0 || hetAtur(); const merk = hjMerk(p, U0); const U = M0 ? M0[merk] || (M0[merk] = hetUnit(merk)) : hetUnit(merk); const kategori = A.peta[U.unit] || '';
  const harga = hjHargaSatuan(p); const kgS = hjKgSatuan(p);
  const dasar = { merk, unit: U.unit, kategori, perKg: 0, het: 0, lebih: 0, kg: 0, rpLebih: 0 };
  if (harga === null || !(harga > 0) || kgS === null) return Object.assign(dasar, { status: 'takBisa', sebab: harga === null ? 'nota lama tanpa harga satuan' : !(harga > 0) ? 'harga Rp0' : 'berat satuan tidak diketahui', teks: 'tidak bisa dinilai' });
  const perKg = harga / kgS; const N = hetNilai(perKg, kategori, A); const kg = hjJumlahBayar(p) * kgS;
  const status = N.status === 'kosong' ? 'takBisa' : N.status;
  return Object.assign(dasar, { status, perKg, het: N.het, lebih: N.lebih, kg, rpLebih: status === 'atas' ? N.lebih * kg : 0, teks: N.teks, sebab: '' });
}
/** Harga yang SEDANG diketik untuk satu baris keranjang (lembar nego) dinilai terhadap HET. */
export function hjSatuHarga(t, harga, A) { return t ? hjNilaiBaris(Object.assign({}, t, { hargaSatuan: Math.round(Number(harga) || 0) }), A, null) : null; }

/** Keranjang (Bayar): tiap baris dinilai → { baris: [{ id, label, nilai }], nAtas, nBelum, nBeras, atas: [...], keadaan, teks }. */
export function hjKeranjang(keranjang, A0) {
  const A = A0 || hetAtur(); const U = petaUkuran(); const M = {}; const baris = [];
  (keranjang || []).forEach((b) => { const t = b && b.trx; const v = hjNilaiBaris(t, A, U, M); if (v) baris.push({ id: b.id, label: hjBersih(t.label || v.merk), nilai: v }); });
  const atas = baris.filter((x) => x.nilai.status === 'atas'); const belum = baris.filter((x) => x.nilai.status === 'belum');
  const unitBelum = belum.map((x) => x.nilai.unit).filter((u, i, a) => u && a.indexOf(u) === i);
  const keadaan = !baris.length ? 'kosong' : atas.length ? 'atas' : belum.length === baris.length ? 'belum' : 'aman';
  const teks = atas.length ? atas.length + ' baris di atas HET: ' + atas.map((x) => x.label + ' ' + RP(Math.round(x.nilai.perKg)) + '/kg (HET ' + x.nilai.kategori + ' ' + RP(x.nilai.het) + ', +' + hjRp(x.nilai.lebih) + '/kg)').join(' · ')
      + ' — nota tetap boleh dicatat; barisnya ditandai di rekap HET Laporan › Mingguan.'
    : keadaan === 'belum' ? 'HET belum bisa dibandingkan: kelas ' + unitBelum.join(', ') + ' belum dipetakan (Harga › HET).' : '';
  return { baris, atas, nAtas: atas.length, nBelum: belum.length, nBeras: baris.length, unitBelum, keadaan, teks, atur: A };
}

// ---------- REKAP PER MINGGU (A132) ----------
const hjHari = (iso) => Math.round(Date.parse(String(iso).slice(0, 10) + 'T00:00:00Z') / 86400000);
const hjIso = (n) => new Date(n * 86400000).toISOString().slice(0, 10);
/** Senin minggu yang memuat iso (minggu toko = Senin–Minggu, sama dengan Laporan › Mingguan). */
export function hjSenin(iso) { const n = hjHari(iso); return hjIso(n - ((((n + 3) % 7) + 7) % 7)); }
const hjLabel = (awal) => tanggalPendek(awal).replace(/ \d{4}$/, '') + '–' + tanggalPendek(hjIso(hjHari(awal) + 6)).replace(/ \d{4}$/, '');
/** Kunci satu baris NOTA: literan wadah campuran dipecah jadi baris internal per merek asal (takaranId sama) = satu baris yang dilihat pembeli. */
const hjKunciBaris = (p) => (p.takaranId ? 't:' + String(p.takaranId) : String(p.id));

/**
 * Rekap satu minggu (Senin awal … Minggu): semua baris nota yang berlaku dinilai dengan HET & peta kelas yang berlaku SEKARANG.
 * → { awal, akhir, label, keadaan 'kosong'|'belum'|'sebagian'|'lengkap'|'diarsip', hit {atas, dalam, belum, bukan, takBisa}, nBaris, nDinilai, kgAtas, rpLebih, nNotaAtas,
 *     merek: [baris di atas HET per merek], unitBelum, takBisa {sebab: n}, judul, rincian, hetTeks, menutup }.
 */
export function hjMinggu(awal0) { const awal = hjSenin(awal0); return ingatPerVersi('hjMinggu|' + awal, () => hjMingguHitung(awal, hetAtur(), petaUkuran(), {})); }
function hjMingguHitung(awal, A, U, M) {
  const akhir = hjIso(hjHari(awal) + 6);
  const dasar = { awal, akhir, label: hjLabel(awal), hetTeks: 'HET ' + A.zona + ': medium ' + RP(A.medium) + '/kg · premium ' + RP(A.premium) + '/kg (' + (A.angkaOwner ? 'angka owner' : 'angka bawaan') + ')' };
  if (tahunDiarsip(awal) && tahunDiarsip(akhir)) return Object.assign(dasar, { keadaan: 'diarsip', hit: { atas: 0, dalam: 0, belum: 0, bukan: 0, takBisa: 0 }, nBaris: 0, nDinilai: 0, kgAtas: 0, rpLebih: 0, nNotaAtas: 0, merek: [], unitBelum: [], takBisa: {}, menutup: true,
    judul: 'Minggu ini sudah tutup buku — rincian notanya ikut arsip', rincian: '' });
  const grup = {};
  ambilPenjualan().forEach((p) => { const t = String(p.tanggal || ''); if (t < awal || t > akhir) return; const v = hjNilaiBaris(p, A, U, M); if (!v) return;
    const k = hjKunciBaris(p); const g = grup[k];
    if (!g) { grup[k] = { v: Object.assign({}, v), nota: String(p.grupNota || p.trxId || p.id) }; return; }
    g.v.kg += v.kg; g.v.rpLebih += v.rpLebih; });   // baris internal satu takaran: kg & rupiah lebih dijumlah, status sama (satu harga per liter wadah)
  const hit = { atas: 0, dalam: 0, belum: 0, bukan: 0, takBisa: 0 }; const per = {}; const belum = {}; const tak = {}; const notaAtas = {}; let kgAtas = 0, rpLebih = 0;
  Object.keys(grup).forEach((k) => { const { v, nota } = grup[k]; hit[v.status] += 1;
    if (v.status === 'atas') { kgAtas += v.kg; rpLebih += v.rpLebih; notaAtas[nota] = 1; const m = per[v.merk] || (per[v.merk] = { merk: v.merk, unit: v.unit, kategori: v.kategori, het: v.het, n: 0, kg: 0, rpLebih: 0, perKgMaks: 0 });
      m.n += 1; m.kg += v.kg; m.rpLebih += v.rpLebih; if (v.perKg > m.perKgMaks) m.perKgMaks = v.perKg; }
    if (v.status === 'belum' && v.unit) belum[v.unit] = (belum[v.unit] || 0) + 1;
    if (v.status === 'takBisa') tak[v.sebab] = (tak[v.sebab] || 0) + 1; });
  const nBaris = Object.keys(grup).length; const nDinilai = hit.atas + hit.dalam;
  const jumlahHit = HJ_STATUS.reduce((a, x) => a + hit[x[0]], 0);
  const keadaan = !nBaris ? 'kosong' : !nDinilai && hit.belum ? 'belum' : hit.belum ? 'sebagian' : nDinilai ? 'lengkap' : 'kosong';
  const merek = Object.keys(per).map((k) => per[k]).sort((a, b) => b.rpLebih - a.rpLebih || b.n - a.n || a.merk.localeCompare(b.merk));
  const unitBelum = Object.keys(belum).sort((a, b) => belum[b] - belum[a] || a.localeCompare(b));
  const judul = keadaan === 'kosong' ? 'Tidak ada baris beras yang bisa dinilai minggu ini'
    : keadaan === 'belum' ? 'Kelas belum dipetakan — ' + hit.belum + ' baris belum bisa dinilai (BUKAN berarti patuh)'
      : (hit.atas ? hit.atas + ' baris di atas HET' + (Object.keys(notaAtas).length ? ' (' + Object.keys(notaAtas).length + ' nota)' : '') : 'Tidak ada baris di atas HET' + (keadaan === 'sebagian' ? ' dari yang sudah dipetakan' : ''))
        + (hit.belum ? ' · ' + hit.belum + ' baris kelasnya belum dipetakan' : '');
  const rincian = nBaris ? 'Dari ' + nBaris + ' baris beras: ' + HJ_STATUS.filter((x) => hit[x[0]] > 0).map((x) => hit[x[0]] + ' ' + x[1]).join(' · ') + '.' : '';
  return Object.assign(dasar, { keadaan, hit, nBaris, nDinilai, kgAtas, rpLebih, nNotaAtas: Object.keys(notaAtas).length, merek, unitBelum, belumPer: belum, takBisa: tak, judul, rincian, menutup: jumlahHit === nBaris });
}
/** Riwayat n minggu sampai minggu yang memuat iso (terbaru di belakang): satu baris ringkas per minggu. */
export function hjRiwayat(iso, n) {
  const akhir = hjSenin(iso); const out = [];
  for (let i = (n || 8) - 1; i >= 0; i--) { const R = hjMinggu(hjIso(hjHari(akhir) - 7 * i));
    out.push({ awal: R.awal, label: R.label, keadaan: R.keadaan, nBaris: R.nBaris, nDinilai: R.nDinilai, nAtas: R.hit.atas, nBelum: R.hit.belum, rpLebih: R.rpLebih, kgAtas: R.kgAtas, terakhir: i === 0 }); }
  return out;
}
/** Kalimat satu baris riwayat (layar & uji memakai yang sama). */
export function hjRiwayatTeks(r) {
  if (r.keadaan === 'diarsip') return 'diarsip'; if (r.keadaan === 'kosong') return 'tidak ada baris beras';
  if (r.keadaan === 'belum') return r.nBelum + ' baris belum dipetakan';
  return (r.nAtas ? r.nAtas + ' di atas HET · ' + KG(r.kgAtas) + ' · lebih ' + RP(Math.round(r.rpLebih)) : 'patuh') + ' dari ' + r.nDinilai + ' dinilai' + (r.nBelum ? ' · ' + r.nBelum + ' belum dipetakan' : '');
}
