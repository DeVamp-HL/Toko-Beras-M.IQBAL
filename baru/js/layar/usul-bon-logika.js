// USUL BATAS BON BULANAN (paket P7, owner 27 Nov 2026; sensus ulang 27 Nov A108). Logika tanpa DOM, nama berawalan ul (bundel uji jsc satu lingkup).
// Dijaga alat-uji/uji_pelanggan_het_p7.py (kotak pasir + statis + --kontrol + asap cadangan toko).
//
// Keputusan owner 27 Nov 2026 ("pakai aturan bawaan itu" + "bon barunya ditahan"): tiap bulan Pelanggan › Bon › Usul batas menyusun daftar orang ber-bon
// dengan usul NAIK / TURUN / HENTI / TETAP + alasannya. Tidak ada yang berubah sendiri: owner mengetuk "Pakai usul" → kartu orang itu (pelangganCatatan, tulisan
// owner) berganti batasnya atau ditandai bonDihentikan. Angka aturannya = SETELAN owner (aturanToko/usulBon, owner saja); nilai awal = "bawaan":
//   periode 3 bulan terakhir · NAIK 25 % bila 3 bon terakhir yang lunas semuanya tepat waktu DAN sisa bon pernah menyentuh ≥ 80 % batas dalam periode ·
//   TURUN 25 % bila paling sedikit 2 dari 3 bon terakhir lunas lewat jatuh tempo (satu rumus dengan "diperkirakan telat" B35: pnKebiasaanBayar) ·
//   HENTI bila bon tertua sudah lewat batas stop bon (Pelanggan › Atur, bawaan 30 hari; fkStopBon) atau statusnya macet (Pelanggan › Atur, bawaan 180 hari; semuaBon).
//   Batas baru dibulatkan ke kelipatan langkah (bawaan Rp10.000): naik ke ATAS, turun ke BAWAH (paling rendah satu langkah).
// Batas yang dinilai = batas yang berlaku di kasir (fkInfoKredit: angka owner di kartu, kosong = 2× rata belanja bulanan 90 hari). Memakai usul naik/turun atas
// batas rumus = menuliskan ANGKA owner di kartu (batas owner juga meloloskan syarat bon baru — disebut di kalimatnya). HENTI = bon baru ditahan (fkHentiBon,
// gerbang KR1 kunciKr1) sampai owner membuka lagi; pintu owner yang sudah ada tetap berlaku.
// Riwayat bayar yang dipakai: 3 bon terakhir yang LUNAS lewat pembayaran (pnKebiasaanBayar) — kurang dari 3 = "riwayat belum cukup" (tidak diusulkan naik).
import { kunciPelanggan } from '../mesin/pembantu.js';
import { cacheMentah, ambilPelangganCatatan } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { fkInfoKredit, fkStopBon, fkStopBonHari, fkHentiBon, fkMundurBulan, fkSumberBatas } from './faktur-logika.js';
import { semuaBon, pnKebiasaanBayar, PN_TELAT_TIGA, PN_TELAT_MIN } from './bon-logika.js';
import { aturPelanggan, kartuTersimpan } from './pelanggan-logika.js';

export const UL_ID = 'usulBon';
export const UL_BAWAAN = { bulan: 3, naikPersen: 25, ambangPakaiPersen: 80, turunPersen: 25, langkah: 10000 };
export const UL_BATAS = { bulan: [1, 12], naikPersen: [1, 200], ambangPakaiPersen: [1, 100], turunPersen: [1, 90], langkah: [1000, 1000000] };
export const UL_NAMA = { naik: 'naik', turun: 'turun', henti: 'henti bon', tetap: 'tetap', dihentikan: 'bon dihentikan' };
export const UL_URUT = ['henti', 'turun', 'naik', 'dihentikan', 'tetap'];
const ulBersih = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const ulAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim().replace(/^rp\s*/i, ''); if (!t) return NaN; const n = Number(/^\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t.replace(',', '.')); return isFinite(n) ? n : NaN; };
const ulDok = () => cacheMentah('aturan').find((d) => String(d.id) === UL_ID) || null;

/** Setelan yang berlaku: angka owner bila sah, selain itu bawaan. dariOwner = owner pernah menyimpan setelan ini. */
export function ulAtur() {
  const d = ulDok() || {}; const out = { dariOwner: !!ulDok() };
  Object.keys(UL_BAWAAN).forEach((k) => { const n = Number(d[k]); const [lo, hi] = UL_BATAS[k]; out[k] = d[k] !== undefined && d[k] !== null && d[k] !== '' && Number.isInteger(n) && n >= lo && n <= hi ? n : UL_BAWAAN[k]; });
  return out;
}
/** Simpan setelan (owner). isi = { bulan, naikPersen, ambangPakaiPersen, turunPersen, langkah } (teks); kosong = nilai yang berlaku. */
export function ulSusunAtur(isi, w) {
  const o = isi || {}; const A = ulAtur(); const data = { id: UL_ID, tanggal: w.tanggal, jam: w.jam, diubahPada: w.kini };
  const nama = { bulan: 'Periode (bulan)', naikPersen: 'Naik (%)', ambangPakaiPersen: 'Pemakaian batas (%)', turunPersen: 'Turun (%)', langkah: 'Pembulatan (Rp)' };
  for (const k of Object.keys(UL_BAWAAN)) {
    const t = ulBersih(o[k]); if (!t) { data[k] = A[k]; continue; } const n = ulAngka(t); const [lo, hi] = UL_BATAS[k];
    if (!(Number.isInteger(n) && n >= lo && n <= hi)) return { tolak: nama[k] + ' harus bilangan bulat ' + lo + '–' + hi.toLocaleString('id-ID') };
    data[k] = n;
  }
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { ulAtur: null, kabar: 'Aturan usul batas bon disimpan — periode ' + data.bulan + ' bulan · naik ' + data.naikPersen + ' % bila pernah ≥ ' + data.ambangPakaiPersen + ' % batas · turun ' + data.turunPersen + ' % · dibulatkan ' + RP(data.langkah), kabarAwas: false } };
}

const ulBulat = (x, L, naik) => Math.max(L, (naik ? Math.ceil(x / L - 1e-9) : Math.floor(x / L + 1e-9)) * L);
const ulUrut = (m) => String(m.tanggal || '') + ' ' + String(m.jam || '');
/** Sisa bon tertinggi sejak `dari` (termasuk sisa yang dibawa dari sebelumnya), menurut urutan waktu buku bon mesin (bon dulu bila jamnya sama). */
export function ulPuncak(mutasi, dari) {
  const ev = (mutasi || []).map((m, i) => ({ m, i, utang: m.jenis === 'jual' || m.jenis === 'saldoAwal' })).sort((a, b) => ulUrut(a.m).localeCompare(ulUrut(b.m)) || (a.utang === b.utang ? a.i - b.i : a.utang ? -1 : 1));
  let sisa = 0, puncak = null;
  ev.forEach((e) => { const t = String(e.m.tanggal || ''); if (t >= dari && puncak === null) puncak = Math.max(0, sisa); sisa += (e.utang ? 1 : -1) * (Number(e.m.nominal) || 0); if (t >= dari) puncak = Math.max(puncak, sisa); });
  return puncak === null ? Math.max(0, sisa) : Math.round(puncak * 100) / 100;
}

/**
 * Daftar bulan ini. → { bulan 'YYYY-MM', iso, dari, atur, daftar: [{ kunci, nama, sisa, batas, sumber, puncak, pakai (%), kebiasaan { n, nTelat, rataTelat },
 *   stop, macet, dihentikan, usul 'naik'|'turun'|'henti'|'tetap'|'dihentikan', ke (batas baru), alasan, kurangRiwayat, sudah (usul yang sama sudah dipakai bulan ini) }],
 *   hit { naik, turun, henti, tetap, dihentikan }, kalimat }.
 * Yang masuk daftar: punya bon dalam periode, sisa bon > 0, punya batas owner, atau sedang dihentikan.
 */
export function ulDaftar(kini) {
  const iso = hariIniIso(kini); const A = ulAtur(); const dari = fkMundurBulan(iso, A.bulan); const bulan = iso.slice(0, 7); const atur = aturPelanggan();
  const B = semuaBon(kini); const K = pnKebiasaanBayar(kini); const sudahAda = {}; const daftar = [];
  const satu = (kunci, nama, b) => {
    const kartu = kartuTersimpan(kunci); const dok = kartu ? kartu.dok : null; const H = fkHentiBon(nama); const info = fkInfoKredit(nama) || {};
    const batas = Number(info.batas) > 0 ? Math.round(Number(info.batas)) : 0; const sumber = info.sumber === 'owner' ? 'owner' : 'rumus';
    const sisa = b ? Math.max(0, Number(b.sisa) || 0) : 0; const puncak = b ? ulPuncak(b.mutasi, dari) : 0; const pakai = batas > 0 ? puncak / batas * 100 : null;
    const kb = K[kunci] || { n: 0, nTelat: 0, rataTelat: null, tiga: [] }; const stop = fkStopBon(nama); const macet = !!(b && b.status === 'macet');
    const o = { kunci, nama, sisa, batas, sumber, sumberTeks: fkSumberBatas(info), puncak, pakai, kebiasaan: { n: kb.n || 0, nTelat: kb.nTelat || 0, rataTelat: kb.rataTelat }, stop, macet,
      dihentikan: H, umur: b ? b.umur : null, usul: 'tetap', ke: batas, alasan: '', kurangRiwayat: (kb.n || 0) < PN_TELAT_TIGA, catatan: [] };
    const telatTeks = o.kebiasaan.nTelat + ' dari ' + o.kebiasaan.n + ' bon terakhir lunas lewat jatuh tempo' + (o.kebiasaan.rataTelat !== null && o.kebiasaan.rataTelat !== undefined ? ' (rata-rata telat ' + String(Math.round(o.kebiasaan.rataTelat * 10) / 10).replace('.', ',') + ' hari)' : '');
    if (H) { o.usul = 'dihentikan'; o.ke = batas; o.alasan = 'bon dihentikan sejak ' + tanggalPendek(H.tanggal) + (H.alasan ? ' · ' + H.alasan : '') + ' — bon baru ditahan sampai dibuka lagi'; }
    else if (stop || macet) { o.usul = 'henti'; o.ke = 0; o.alasan = macet ? 'bon macet: ' + (b ? b.ket : '') + ' (Pelanggan › Atur: macet sesudah ' + atur.macetHari + ' hari)' : 'bon tertua belum lunas sejak ' + tanggalPendek(stop.tanggal) + ' (' + stop.umur + ' hari, batas stop bon ' + stop.hari + ' hari)'; }
    else if (batas > 0 && kb.nTelat >= PN_TELAT_MIN) { o.usul = 'turun'; o.ke = ulBulat(batas * (1 - A.turunPersen / 100), A.langkah, false); o.alasan = telatTeks; }
    else if (batas > 0 && (kb.n || 0) >= PN_TELAT_TIGA && kb.nTelat === 0 && pakai !== null && pakai >= A.ambangPakaiPersen - 1e-9) {
      o.usul = 'naik'; o.ke = ulBulat(batas * (1 + A.naikPersen / 100), A.langkah, true);
      o.alasan = '3 bon terakhir lunas tepat waktu · sisa bon pernah ' + RP(Math.round(puncak)) + ' = ' + Math.round(pakai) + ' % batas (aturan ≥ ' + A.ambangPakaiPersen + ' %)'; }
    else { o.alasan = !batas ? 'batas belum terbentuk (belum ada belanja 90 hari terakhir)' : o.kurangRiwayat ? 'riwayat bayar belum cukup (' + (kb.n || 0) + ' bon lunas, perlu 3)' : (kb.nTelat ? telatTeks + ' — belum sampai ' + PN_TELAT_MIN + ' dari 3' : 'bayar tepat waktu') + (pakai !== null ? ' · pemakaian batas paling tinggi ' + Math.round(pakai) + ' %' : ''); }
    if ((o.usul === 'naik' || o.usul === 'turun') && sumber === 'rumus') o.catatan.push('batas sekarang dari rumus (2× rata belanja bulanan) — memakai usul menuliskan angka owner di kartu, dan batas owner juga meloloskan syarat bon baru');
    const U = dok && dok.usulBon; o.sudah = !!(U && U.bulan === bulan && U.jenis === o.usul);
    daftar.push(o); sudahAda[kunci] = 1;
  };
  B.forEach((b) => { const aktif = (b.sisa || 0) > 0.5 || (b.mutasi || []).some((m) => String(m.tanggal || '') >= dari && (m.jenis === 'jual' || m.jenis === 'bayar')) || fkHentiBon(b.nama) || (kartuTersimpan(b.kunci) && Number((kartuTersimpan(b.kunci).dok || {}).batasKredit) > 0);
    if (aktif) satu(b.kunci, b.nama, b); });
  // kartu yang dihentikan / berbatas owner tanpa catatan buku bon sama sekali
  (ambilPelangganCatatan() || []).forEach((c) => { const k = kunciPelanggan(c.nama || c.id); if (!k || sudahAda[k]) return; if ((c.bonDihentikan && c.bonDihentikan.tanggal) || Number(c.batasKredit) > 0) satu(k, String(c.nama || c.id), null); });
  daftar.sort((a, b) => UL_URUT.indexOf(a.usul) - UL_URUT.indexOf(b.usul) || b.sisa - a.sisa || a.nama.localeCompare(b.nama));
  const hit = { naik: 0, turun: 0, henti: 0, tetap: 0, dihentikan: 0 }; daftar.forEach((o) => { hit[o.usul] += 1; });
  const ubah = hit.naik + hit.turun + hit.henti; const belumDipakai = daftar.filter((o) => ['naik', 'turun', 'henti'].indexOf(o.usul) >= 0 && !o.sudah).length;
  const kalimat = !daftar.length ? 'Belum ada pelanggan ber-bon dalam ' + A.bulan + ' bulan terakhir.'
    : ubah ? ubah + ' usul bulan ini (' + [['naik', 'naik'], ['turun', 'turun'], ['henti', 'henti']].filter((x) => hit[x[0]]).map((x) => hit[x[0]] + ' ' + x[1]).join(' · ') + ')' + (belumDipakai < ubah ? ', ' + (ubah - belumDipakai) + ' sudah dipakai' : '') + ' — tidak ada yang berubah sebelum owner mengetuk "Pakai usul".'
      : 'Tidak ada usul bulan ini — ' + daftar.length + ' orang ber-bon, semua tetap.';
  return { bulan, iso, dari, atur: A, daftar, hit, kalimat, nUsul: ubah, nBelum: belumDipakai };
}

/** Owner memakai usul satu orang → kartu pelangganCatatan (batasKredit baru / bonDihentikan) + jejak usulBon { bulan, jenis, dari, ke }. */
export function ulSusunPakai(kini, kunci, w) {
  const D = ulDaftar(kini); const o = D.daftar.find((x) => x.kunci === kunci);
  if (!o) return { tolak: 'Orang ini tidak ada di daftar usul bulan ini' };
  if (['naik', 'turun', 'henti'].indexOf(o.usul) < 0) return { tolak: o.nama + ': tidak ada usul yang bisa dipakai (' + UL_NAMA[o.usul] + ')' };
  if (o.sudah) return { tolak: 'Usul ' + UL_NAMA[o.usul] + ' untuk ' + o.nama + ' sudah dipakai bulan ini' };
  const lama = kartuTersimpan(kunci); const dasar = lama ? Object.assign({}, lama.dok) : { id: kunci, nama: o.nama, catatan: '', ciri: '', rute: '', cip: [], arah: '' };
  const jejak = { bulan: D.bulan, jenis: o.usul, dari: o.batas, sumberDari: o.sumber, ke: o.usul === 'henti' ? 0 : o.ke, tanggal: w.tanggal, jam: w.jam, alasan: o.alasan.slice(0, 200) };
  const data = Object.assign(dasar, { diubahPada: w.kini, usulBon: jejak });
  if (o.usul === 'henti') data.bonDihentikan = { tanggal: w.tanggal, jam: w.jam, alasan: o.alasan.slice(0, 160) };
  else data.batasKredit = o.ke;
  return { dokumen: [{ koleksi: 'pelangganCatatan', data }], patch: { kabar: o.usul === 'henti' ? 'Bon ' + o.nama + ' DIHENTIKAN — kasir menahan bon baru atas namanya sampai owner membuka lagi dari kartunya.'
    : 'Batas bon ' + o.nama + ' ' + (o.usul === 'naik' ? 'dinaikkan' : 'diturunkan') + ' ' + RP(o.batas) + ' → ' + RP(o.ke) + ' (angka owner di kartu).', kabarAwas: o.usul === 'henti' } };
}
/** Owner membuka lagi bon yang dihentikan (dari kartu atau daftar usul). Jejak usulBon tetap; kolom bonDihentikan dihapus, hentiDibuka mencatat kapan. */
export function ulSusunBuka(kunci, w) {
  const lama = kartuTersimpan(kunci); if (!lama || !lama.dok || !lama.dok.bonDihentikan) return { tolak: 'Bon orang ini tidak sedang dihentikan' };
  const data = Object.assign({}, lama.dok, { diubahPada: w.kini, hentiDibuka: { tanggal: w.tanggal, jam: w.jam, sejak: String(lama.dok.bonDihentikan.tanggal || '') } }); delete data.bonDihentikan;
  return { dokumen: [{ koleksi: 'pelangganCatatan', data }], patch: { kabar: 'Bon ' + lama.nama + ' dibuka lagi — batas & syarat bon biasa berlaku.', kabarAwas: false } };
}
