// WADAH BERNAMA — isi kotak wadah literan PER MEREK ASAL (putaran 27, koreksi owner 27 Sep atas model putaran 9–10 "pindah nama").
// Wadah = TEMPAT bernama (W1–W8). Nama seperti "IR64 Apex" = nama wadah / kelas mutu, bukan merek; isinya boleh dari beberapa merek karung sekaligus.
// Buku stok hanya per merek karung (mesin beku memotong `merkSumber` tiap baris nota, bukan `namaProduk` — docs/peta-stok-merek.md §7).
//
// KOMPOSISI satu wadah = titik samakan terakhir (dokumen wadahLiteran tipe 'isi'; kolom `komposisi {merek: kg}` sejak putaran 27, dokumen lama tanpa
// komposisi = SELURUH isinya milik NAMA WADAH — persis cara buku lama menghitungnya) + takar sesudahnya − baris literan dari wadah itu sesudahnya:
//   · takar model baru (`bukuAsal: true`) → kg milik MEREK ASAL karungnya (bukunya tidak dipindah);
//   · takar lama (sebelum putaran 27: senama, atau lintas nama yang bukunya dipindah lewat produksiKemasan jadi-karung-utuh) → milik NAMA WADAH;
//   · baris literan ber-`dariWadah` (model baru, satu takaran dipecah per merek asal) → mengurangi bagian `merkSumber`-nya;
//     baris lama tanpa `dariWadah` dengan merkSumber = nama wadah (juga kasir.html) → mengurangi bagian nama wadah.
// Urutan kejadian tidak mengubah hasil (tiap kejadian menyebut sendiri bagian siapa yang bertambah/berkurang). Angka MENTAH boleh minus
// (lupa mencatat isi ulang) — tidak dijepit diam-diam; pemecah penjualan hanya membagi bagian yang positif.
// Identitas yang dijaga uji: untuk tiap merek M, tumpukan(M) + karung terbuka(M) + Σ bagian M di semua wadah = buku(M) (− pindah nama lama).
// Tanpa DOM; nama berawalan wb (bundel uji satu lingkup). Dijaga alat-uji/uji_wadah_bernama.py & uji_cocokkan_terpisah.py.
import { hitungStokKarungPerMerk } from '../mesin/beku.js';
import { RASIO_KONVERSI, RASIO_DEFAULT } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilWadahLiteran } from '../data/toko.js';
import { aturWadah, karungUntukWadah, wdSesudah, wdTerbaru } from './jual-logika.js';

const wbB3 = (n) => Math.round(n * 1000) / 1000;
const wbB2 = (n) => Math.round(n * 100) / 100;

/** Baris literan yang MENGURANGI isi wadah W: model baru (`dariWadah` = W) atau model lama (tanpa `dariWadah`, merkSumber = nama wadah). */
export function wbDariWadah(p, W) { return !!p && p.jenis === 'literan' && (p.dariWadah ? String(p.dariWadah) === String(W) : String(p.merkSumber || '') === String(W)); }
/** Bagian baris keranjang/struk parkir yang dipegang dari wadah W: [{merk, kg}]. Baris wadah model baru membawa `pecahan`. */
export function wbPecahanBaris(t, W) {
  if (!t || t.jenis !== 'literan') return [];
  if (t.dariWadah) return String(t.dariWadah) === String(W) ? (Array.isArray(t.pecahan) && t.pecahan.length ? t.pecahan.map((x) => ({ merk: String(x.merk), kg: Number(x.kg) || 0 })) : [{ merk: String(t.merkSumber || W), kg: t.totalKg || 0 }]) : [];
  return String(t.merkSumber || '') === String(W) ? [{ merk: String(W), kg: t.totalKg || 0 }] : [];
}
/** Titik samakan terakhir wadah W (dokumen 'isi'), atau null. */
export function wbTanda(W) { return wdTerbaru(ambilWadahLiteran().filter((d) => d.wadah === W && d.tipe === 'isi')); }
/** Isi dasar dokumen 'isi': kolom komposisi (putaran 27) atau seluruh isiKg milik nama wadah (dokumen lama). */
export function wbDasar(tanda, W) {
  const out = {}; if (!tanda) return out;
  const k = tanda.komposisi && typeof tanda.komposisi === 'object' && !Array.isArray(tanda.komposisi) ? tanda.komposisi : null;
  if (k) { Object.keys(k).forEach((m) => { const n = Number(k[m]) || 0; if (m && n) out[m] = (out[m] || 0) + n; }); return out; }
  const isi = tanda.isiKg !== undefined && tanda.isiKg !== null && Number(tanda.isiKg) >= 0 ? Number(tanda.isiKg) : aturWadah().penuhKg;
  if (isi) out[String(W)] = isi;
  return out;
}

/**
 * KOMPOSISI isi wadah W sekarang: { diketahui, bagian {merek: kg MENTAH}, totalKg, positif [{merk, kg}] (terbesar dulu), sejak }.
 * s (keadaan Jual) → bagian yang sedang dipegang keranjang aktif & struk parkir ikut dikurangi (pratinjau yang sama dengan tinggi wadah).
 * Belum pernah disamakan → diketahui:false (tidak ditebak).
 */
export function wbKomposisi(W, s) {
  const tanda = wbTanda(W);
  if (!tanda) return { wadah: W, diketahui: false, bagian: {}, totalKg: 0, positif: [], sejak: '' };
  const bagian = wbDasar(tanda, W); const tambah = (m, kg) => { if (!m || !kg) return; bagian[m] = (bagian[m] || 0) + kg; };
  ambilWadahLiteran().forEach((t) => { if (t.tipe !== 'takar' || t.wadah !== W || !wdSesudah(t, tanda)) return;
    (t.sumber || []).forEach((x) => tambah(t.bukuAsal ? String(x.merk || '') : String(W), Number(x.kg) || 0)); });
  ambilPenjualan().forEach((p) => { if (wbDariWadah(p, W) && wdSesudah(p, tanda)) tambah(String(p.merkSumber || W), -(p.totalKg || 0)); });
  if (s) { const pegang = (daftar) => (daftar || []).forEach((b) => wbPecahanBaris(b.trx, W).forEach((x) => tambah(x.merk, -x.kg)));
    pegang(s.keranjang); (s.antrean || []).forEach((a) => pegang(a.beku && a.beku.items)); }
  Object.keys(bagian).forEach((m) => { bagian[m] = wbB3(bagian[m]); if (Math.abs(bagian[m]) < 0.0005) delete bagian[m]; });
  const positif = Object.keys(bagian).filter((m) => bagian[m] > 0).map((m) => ({ merk: m, kg: bagian[m] })).sort((a, b) => b.kg - a.kg || a.merk.localeCompare(b.merk));
  return { wadah: W, diketahui: true, bagian, totalKg: wbB3(Object.keys(bagian).reduce((a, m) => a + bagian[m], 0)), positif, sejak: tanda.tanggal || '', sejakJam: tanda.jam || '' };
}
/** Σ bagian tiap merek di SEMUA wadah (yang isinya diketahui) — rantai stok: tumpukan = buku − karung terbuka − bagian ini. */
export function wbBagianMerk() {
  const out = {}; aturWadah().daftar.forEach((W) => { const K = wbKomposisi(W); if (!K.diketahui) return; Object.keys(K.bagian).forEach((m) => { out[m] = wbB3((out[m] || 0) + K.bagian[m]); }); });
  return out;
}
/** Wadah-wadah yang (menurut komposisinya) memegang beras merek M. */
export function wbWadahBerisi(M) { return aturWadah().daftar.filter((W) => { const K = wbKomposisi(W); return K.diketahui && Math.abs(K.bagian[M] || 0) > 0.0005; }); }
/** Rasio liter → kg untuk wadah W (rasio nama wadahnya, sama dengan cara lama; selain itu bawaan 0,82). */
export function wbRasio(W) { return RASIO_KONVERSI[W] || RASIO_DEFAULT; }
/** Merek yang dipotong untuk kg yang MELEBIHI isi tercatat (isi ulang lupa dicatat): karung di belakang wadah (bawaan: nama wadahnya). */
export function wbMerkCadangan(W) { const k = karungUntukWadah(W); return k && k.merk ? String(k.merk) : String(W); }

/**
 * PECAH satu takaran literan dari wadah W (kg) menurut komposisi SAAT ITU: bagian positif dibagi sebanding, sisa pembulatan ke bagian terakhir
 * (Σ persis). Kg yang melebihi isi tercatat (wadah "minus" / belum pernah disamakan) dipotong dari karung di belakangnya dan DISEBUT (lewatKg).
 * → { bagian: [{merk, kg}], lewatKg, komposisi }.
 */
export function wbPecah(W, kg, s) {
  const K = wbKomposisi(W, s); const total = wbB3(Number(kg) || 0);
  const pos = K.positif; const adaKg = wbB3(pos.reduce((a, x) => a + x.kg, 0)); const ambil = Math.min(total, adaKg);
  const out = []; let jalan = 0;
  pos.forEach((x, i) => { const k = i === pos.length - 1 ? wbB3(ambil - jalan) : wbB3(ambil * x.kg / adaKg); jalan = wbB3(jalan + k); if (k > 0) out.push({ merk: x.merk, kg: k }); });
  const lewat = wbB3(total - jalan);
  if (lewat > 0) { const m = wbMerkCadangan(W); const ada = out.find((x) => x.merk === m); if (ada) ada.kg = wbB3(ada.kg + lewat); else out.push({ merk: m, kg: lewat }); }
  return { bagian: out, lewatKg: lewat, komposisi: K };
}
/** Modal per kg isi wadah SEKARANG = rata-rata tertimbang bagian positif (kg × modal buku tiap merek asal). Kosong → modal karung di belakangnya. */
export function wbModalPerKg(W, s) {
  const stok = hitungStokKarungPerMerk(); const K = wbKomposisi(W, s); const hpp = (m) => (stok[m] || {}).hppTerakhirPerKg || 0;
  const kg = K.positif.reduce((a, x) => a + x.kg, 0);
  if (kg > 0) return K.positif.reduce((a, x) => a + x.kg * hpp(x.merk), 0) / kg;
  return hpp(wbMerkCadangan(W)) || hpp(W);
}
/** Komposisi sesudah isi wadah dihitung ulang jadi `isiKg` (cocokkan): selisih dibagi sebanding bagian positif; tanpa bagian positif → merek cadangan. */
export function wbKomposisiBaru(W, isiKg) {
  const K = wbKomposisi(W); const isi = wbB2(Number(isiKg) || 0); const dasar = {};
  Object.keys(K.bagian).forEach((m) => { if (K.bagian[m] > 0) dasar[m] = K.bagian[m]; });
  const ada = Object.keys(dasar).reduce((a, m) => a + dasar[m], 0); const out = {}; const alokasi = {};
  if (!K.diketahui || !(ada > 0)) { const m = K.diketahui ? wbMerkCadangan(W) : (hitungStokKarungPerMerk()[W] ? String(W) : wbMerkCadangan(W)); if (isi > 0) out[m] = isi; return { komposisi: out, alokasi, dasar: K }; }
  const urut = Object.keys(dasar).sort((a, b) => dasar[b] - dasar[a] || a.localeCompare(b)); let jalan = 0;
  urut.forEach((m, i) => { const k = i === urut.length - 1 ? wbB2(isi - jalan) : wbB2(isi * dasar[m] / ada); jalan = wbB2(jalan + k); if (k > 0) out[m] = k; });
  // alokasi selisih per merek = bagian baru − bagian lama (termasuk bagian minus yang dibuang ke nol)
  Object.keys(K.bagian).concat(Object.keys(out)).forEach((m) => { if (alokasi[m] !== undefined) return; const d = wbB2((out[m] || 0) - (K.bagian[m] || 0)); if (Math.abs(d) >= 0.005) alokasi[m] = d; });
  return { komposisi: out, alokasi, dasar: K };
}
