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
import { hitungStokKarungPerMerk, hitungStokBahanLiteran } from '../mesin/beku.js';
import { RASIO_KONVERSI, RASIO_DEFAULT, hargaKarungUtuh, cariHargaKarungPerKg } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilWadahLiteran, ambilHargaLiteran, ambilSemuaBatch, ambilProduksiBerlaku, ambilPenyesuaianStok, ambilBahanLiteran, cacheMentah, tolakKunci, denganCacheSementara, kunciStokWadah, petaStokWadah, kunciKarungWadah, kunciKarungBelakang, merkAsalKunci, petaBukuWadah, petaUkuran, indukTerpisah, ingatStokKarung } from '../data/toko.js';
import { aturWadah, karungUntukWadah, karungBelakang, semuaKarungTerbuka, wdSesudah, wdTerbaru, tinggiWadah, beratKarungBuka, DAFTAR_WADAH, kolamDitutup, wdLokasiDoc, wdLokasiSumber } from './jual-logika.js';
import { RP, tanggalPendek } from '../inti/format.js';
import { hppKeluar, modalRataPerKg, nilaiSelisihKg } from '../mesin/modal-fifo.js';

const wbB3 = (n) => Math.round(n * 1000) / 1000;
const wbB2 = (n) => Math.round(n * 100) / 100;

// ---------- STOK WADAH SENDIRI (putaran 28, owner 28 Sep 2026) ----------
// "Gua mau semua wadah kotak literan itu punya stok tersendiri" — sumbernya karung 50 kg di BELAKANG wadah; karung itu dari tumpukan gudang, kiriman
// pemasok, atau hasil adukan. Wadah yang kunci bukunya ('Wadah <nama>', data/toko.js) sudah lahir = AKTIF:
//   · takar dari karung → buku merek karung turun, buku wadah naik, modal ikut (produksiKemasan jadi-karung-utuh, dibaca mesin beku apa adanya);
//   · literan terjual → hanya buku wadah turun (baris literan merkSumber = kunci wadah) — buku merek tidak menahan penjualan wadah lagi;
//   · cocokkan wadah → penyesuaianStok atas kunci wadah (susut wadah itu sendiri).
// Komposisi wadah aktif = 100 % kuncinya sendiri (wbKomposisi), jadi pemecah, langit-langit, modal, dan rincian karcis putaran 27 berjalan tanpa diubah.
// Wadah yang belum dipindahkan (tombol owner "Pindahkan isi wadah ke stok wadah") tetap memakai model putaran 27.
/** Kunci buku stok wadah W ('Wadah <nama>'). */
export const wbKunci = (W) => kunciStokWadah(W);
/** Wadah W sudah punya stok sendiri (kunci bukunya sudah lahir). peta = petaStokWadah() bila sudah dihitung pemanggil. */
export function wbAktif(W, peta) { return !!(peta || petaStokWadah())[kunciStokWadah(W)]; }

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
  if (wbAktif(W)) {   // putaran 28: stok wadah sendiri — isi = buku kunci wadah (dikurangi yang dipegang keranjang aktif & struk parkir)
    const k = wbKunci(W); const st = ingatStokKarung()[k]; let kg = st ? st.sisaKg || 0 : 0;
    if (s) { const pegang = (daftar) => (daftar || []).forEach((b) => wbPecahanBaris(b.trx, W).forEach((x) => { kg -= x.kg; })); pegang(s.keranjang); (s.antrean || []).forEach((a) => pegang(a.beku && a.beku.items)); }
    kg = wbB3(kg); const bagian = {}; if (Math.abs(kg) >= 0.0005) bagian[k] = kg;
    // "sejak" = titik samakan NYATA terakhir (pindahan awal cuma memindah angka tercatat — susut wajar dihitung dari hitungan sebelumnya)
    const nyata = wdTerbaru(ambilWadahLiteran().filter((d) => d.wadah === W && d.tipe === 'isi' && !d.pindahAwal)) || tanda;
    return { wadah: W, diketahui: true, stokSendiri: true, kunci: k, bagian, totalKg: kg, positif: kg > 0 ? [{ merk: k, kg }] : [], sejak: nyata ? nyata.tanggal || '' : '', sejakJam: nyata ? nyata.jam || '' : '' };
  }
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
export function wbMerkCadangan(W) { if (wbAktif(W)) return wbKunci(W); const k = karungUntukWadah(W); return k && k.merk ? String(k.merk) : String(W); }

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
  const stok = ingatStokKarung(); const K = wbKomposisi(W, s); const hpp = (m) => modalRataPerKg(stok[m]);   // wadah campuran = rata-rata (owner 9 Okt)
  const kg = K.positif.reduce((a, x) => a + x.kg, 0);
  if (kg > 0) return K.positif.reduce((a, x) => a + x.kg * hpp(x.merk), 0) / kg;
  return hpp(wbMerkCadangan(W)) || hpp(W);
}
/** Harga BELI terbaru per kg isi wadah = rata-rata tertimbang harga beli terakhir tiap merek asal (penanda "harga beli naik" di katalog). */
export function wbBeliPerKg(W) {
  const stok = ingatStokKarung(); const K = wbKomposisi(W); const beli = (m) => (stok[m] || {}).hargaTerakhirPerKg || 0;
  if (K.stokSendiri) { const kn = karungUntukWadah(W); return beli(wbMerkAsal(kn.merk)) || wbModalPerKg(W); }   // buku wadah tidak pernah dibeli — harga beli karung di belakangnya (39: lewat merek asalnya)
  const kg = K.positif.reduce((a, x) => a + x.kg, 0);
  if (kg > 0) return K.positif.reduce((a, x) => a + x.kg * beli(x.merk), 0) / kg;
  return beli(wbMerkCadangan(W)) || beli(W);
}
/** Komposisi sesudah isi wadah dihitung ulang jadi `isiKg` (cocokkan): selisih dibagi sebanding bagian positif; tanpa bagian positif → merek cadangan. */
export function wbKomposisiBaru(W, isiKg) {
  const K = wbKomposisi(W); const isi = wbB2(Number(isiKg) || 0); const dasar = {};
  // putaran 28: wadah berstok sendiri — komposisinya 100 % kuncinya sendiri, jadi selisih jatuh ke buku wadah itu (susut wadah) lewat jalan yang sama
  Object.keys(K.bagian).forEach((m) => { if (K.bagian[m] > 0) dasar[m] = K.bagian[m]; });
  const ada = Object.keys(dasar).reduce((a, m) => a + dasar[m], 0); const out = {}; const alokasi = {};
  // audit 39b no. 5 (G2): buku wadah 0 / minus — selisihnya tetap jatuh ke buku wadah itu (dulu alokasi kosong: hitungan hilang, buku tetap 0)
  if (K.stokSendiri && !(ada > 0)) { if (isi > 0) out[K.kunci] = isi; const d = wbB2(isi - (K.totalKg || 0)); if (Math.abs(d) >= 0.005) alokasi[K.kunci] = d; return { komposisi: out, alokasi, dasar: K }; }
  if (!K.diketahui || !(ada > 0)) { const m = K.diketahui ? wbMerkCadangan(W) : (hitungStokKarungPerMerk()[W] ? String(W) : wbMerkCadangan(W)); if (isi > 0) out[m] = isi; return { komposisi: out, alokasi, dasar: K }; }
  const urut = Object.keys(dasar).sort((a, b) => dasar[b] - dasar[a] || a.localeCompare(b)); let jalan = 0;
  urut.forEach((m, i) => { const k = i === urut.length - 1 ? wbB2(isi - jalan) : wbB2(isi * dasar[m] / ada); jalan = wbB2(jalan + k); if (k > 0) out[m] = k; });
  // alokasi selisih per merek = bagian baru − bagian lama (termasuk bagian minus yang dibuang ke nol)
  Object.keys(K.bagian).concat(Object.keys(out)).forEach((m) => { if (alokasi[m] !== undefined) return; const d = wbB2((out[m] || 0) - (K.bagian[m] || 0)); if (Math.abs(d) >= 0.005) alokasi[m] = d; });
  return { komposisi: out, alokasi, dasar: K };
}

// ---------- STOK WADAH: lahir, pindah buku, pindahan awal, katalog HP kasir (putaran 28) ----------
const wbKG = (n) => String(wbB2(n)).replace('.', ',') + ' kg';
/**
 * Batch LAHIR (stokAwal 0 kg — tidak masuk kas, utang, maupun belanja) untuk nama buku yang belum pernah muncul di batchMasuk. baris = [{merk, stokWadah?}];
 * null bila semuanya sudah lahir. Tanpa baris ini mesin beku tidak memotong penjualan, penyesuaian, maupun takar dari nama itu (uji 28 Sep: nama yang
 * lahir cuma lewat produksi jadi-karung-utuh — masuk 10, jual 2 → tetap 10).
 */
export function wbDokLahir(baris, w) {
  const ada = {}; ambilSemuaBatch().forEach((b) => (b.merkList || []).forEach((m) => { if (m && m.merk) ada[String(m.merk)] = true; }));
  const rows = [];
  (baris || []).forEach((x) => { if (!x || !x.merk || ada[x.merk] || rows.some((r) => r.merk === x.merk)) return;
    // buku per ukuran (karung 25 kg): baris lahir satuan 'karung' berat itu, supaya "punya karung 25 kg" terbaca (0 karung, 0 kg — tanpa kas/utang)
    if (x.indukUkuran) { rows.push({ id: String(rows.length + 1), merk: String(x.merk), satuan: 'karung', beratKarung: Number(x.berat) || 25, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, indukUkuran: String(x.indukUkuran) }); return; }
    rows.push(Object.assign({ id: String(rows.length + 1), merk: String(x.merk), satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0 },
      x.stokWadah ? { stokWadah: String(x.stokWadah) } : x.karungWadah ? { karungWadah: String(x.karungWadah) } : x.bukuAdukan ? { bukuAdukan: String(x.bukuAdukan) }
      : x.karungBelakang ? { karungBelakang: String(x.karungBelakang), merkAsal: String(x.merkAsal || '') } : {})); });   // putaran 39: karung di belakang wadah = buku sendiri
  if (!rows.length) return null;
  return { koleksi: 'batchMasuk', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, pemasok: 'LAHIR BUKU', caraBayar: 'tunai', biayaBongkar: 0, stokAwal: true, lahirBuku: true, merkList: rows } };
}
/**
 * PINDAH BUKU: kg keluar dari buku-buku sumber [{merk, kg}] dan masuk ke buku `tujuan` dengan modal rata-rata tertimbang sumbernya — satu dokumen
 * produksiKemasan jadi-karung-utuh (bentuk simpanProduksi index.html, sama dengan pindah buku takar 22 Sep; mesin beku membacanya apa adanya).
 * Nilai yang keluar = nilai yang masuk: laba dan neraca tidak berubah.
 */
export function wbDokPindah(sumber, tujuan, w, ekstra) {
  const stok = hitungStokKarungPerMerk();
  const list = (sumber || []).filter((x) => x && x.merk && Math.abs(Number(x.kg) || 0) >= 0.005).map((x) => ({ merk: String(x.merk), kg: wbB2(Number(x.kg)) }));
  // modal FIFO (owner 9 Okt 2026): kg yang ditakar dari karung = karung TERLAMA (mesin/modal-fifo.js), urut sumber; kg minus = kembali ke depan antrean.
  // Isi wadah sesudahnya tetap rata-rata (wadah campuran, owner 9 Okt). Saklar mati = kg × modal rata-rata persis seperti dulu.
  const fifoAmbil = {};
  const nilaiSumber = (x) => { const st = stok[x.merk]; if (x.kg < 0) return -nilaiSelisihKg(st, -x.kg); const v = hppKeluar(st, x.kg, fifoAmbil[x.merk]); fifoAmbil[x.merk] = (fifoAmbil[x.merk] || 0) + x.kg; return v; };
  const kg = wbB2(list.reduce((a, x) => a + x.kg, 0)); const nilai = list.reduce((a, x) => a + nilaiSumber(x), 0); const id = w.idUnik();
  return { koleksi: 'produksiKemasan', data: Object.assign({ id, tanggal: w.tanggal, jam: w.jam, merkSumber: list.map((x) => x.merk).join(' + '), namaProduk: tujuan, ukuranKemasan: kg, jumlahUnit: 1,
    biayaKemasan: 0, upahRepacking: 0, kantongJenis: null, kantongJumlah: 0, hppSumberPerKgDipakai: kg > 0 ? nilai / kg : 0, hppPerUnit: nilai, sumberList: list, kgDipakai: kg, sumberKemasanList: [], kgKemasanDipakai: 0,
    batchProduksi: id, barisKe: 1, jumlahBaris: 1, jadiKarungUtuh: true, merkTujuan: tujuan, dariTakar: true }, ekstra || {}) };
}
/**
 * PINDAHAN AWAL (keputusan owner 28 Sep: "pindah dari buku merek"): isi tercatat tiap wadah yang belum punya stok sendiri dipindah ke buku wadahnya —
 * buku merek asal turun sebesar bagiannya, buku wadah naik, modal ikut. Satu kiriman: satu batch lahir + satu pindah buku per wadah + titik samakan isi.
 * Wadah yang isinya belum pernah dicocokkan, tercatat minus, atau bagiannya milik nama tanpa buku DILEWATI dan disebut (tidak ditebak).
 * hanya = satu nama wadah saja (kosong = semua).
 */
export function wbSusunPindahAwal(w, hanya) {
  const A = aturWadah(); const peta = petaStokWadah(); const stok = hitungStokKarungPerMerk();
  const calon = A.daftar.filter((W) => !wbAktif(W, peta) && (!hanya || hanya === W));
  if (!calon.length) return { tolak: hanya ? 'Wadah ' + hanya + ' sudah punya stok sendiri' : 'Semua wadah sudah punya stok sendiri' };
  const lewati = []; const jadi = [];
  calon.forEach((W) => { const K = wbKomposisi(W);
    if (!K.diketahui) { lewati.push(W + ' — isinya belum pernah dicocokkan'); return; }
    const sumber = Object.keys(K.bagian).filter((m) => Math.abs(K.bagian[m]) >= 0.005).sort().map((m) => ({ merk: m, kg: wbB2(K.bagian[m]) }));
    const tanpaBuku = sumber.filter((x) => !stok[x.merk]);
    if (tanpaBuku.length) { lewati.push(W + ' — bagian ' + tanpaBuku.map((x) => x.merk).join(', ') + ' tidak punya buku'); return; }
    const kg = wbB2(sumber.reduce((a, x) => a + x.kg, 0));
    if (kg < -0.004) { lewati.push(W + ' — isi tercatat minus ' + wbKG(-kg) + ', cocokkan dulu'); return; }
    jadi.push({ W, sumber, kg }); });
  if (!jadi.length) return { tolak: 'Belum ada wadah yang bisa dipindah: ' + lewati.join('; ') };
  const dokumen = []; const lahir = wbDokLahir(jadi.map((x) => ({ merk: wbKunci(x.W), stokWadah: x.W })), w); if (lahir) dokumen.push(lahir);
  const turun = {}; let rp = 0;
  jadi.forEach((x) => { const k = wbKunci(x.W);
    if (x.kg > 0.004) { const p = wbDokPindah(x.sumber, k, w, { pindahAwalWadah: x.W, keterangan: 'Pindahan awal stok wadah ' + x.W + ': ' + x.sumber.map((y) => y.merk + ' ' + wbKG(y.kg)).join(' + ') + ' → ' + k });
      dokumen.push(p); rp += p.data.hppPerUnit; x.sumber.forEach((y) => { turun[y.merk] = wbB2((turun[y.merk] || 0) + y.kg); }); }
    dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: x.W, tipe: 'isi', isiKg: x.kg, stokWadah: k, pindahAwal: true } }); });
  return { dokumen, jadi, lewati, rp: Math.round(rp), turun,
    patch: { kabar: jadi.length + ' wadah kini punya stok sendiri: ' + jadi.map((x) => x.W + ' ' + wbKG(x.kg)).join(', ') + '. Buku merek turun: ' + (Object.keys(turun).length ? Object.keys(turun).sort().map((m) => m + ' −' + wbKG(turun[m])).join(', ') : 'tidak ada')
      + ' — modal ikut pindah (±Rp' + Math.round(rp).toLocaleString('id-ID') + '), laba & neraca tidak berubah.' + (lewati.length ? ' DILEWATI: ' + lewati.join('; ') + '.' : ''), kabarAwas: !!lewati.length } };
}
/**
 * Katalog HP kasir (keputusan owner 28 Sep "wadah ikut katalog"): baris buku stok wadah memakai harga liter WADAH-nya (katalogHargaLiteran ber-id nama wadah)
 * dan tidak punya karung / harga karung; nama wadah yang sudah punya stok sendiri tidak lagi menjual literan atas nama buku mereknya (harga liter 0),
 * kecuali merek itu ditandai literan langsung. Tanpa wadah aktif = isi apa adanya (byte-sama penyusun index.html).
 */
export function wbSaringKatalogKasir(isi) {
  if (!isi || !Array.isArray(isi.merkKarung)) return isi;
  const peta = petaStokWadah(); const bw = petaBukuWadah(); const uk = petaUkuran(); const tp = indukTerpisah(); if (!Object.keys(bw).length && !Object.keys(uk).length) return isi;
  const A = aturWadah(); const langsung = wbLiteranLangsung().daftar; const harga = ambilHargaLiteran(); const awal = kunciStokWadah('').length;
  const aktifNama = {}; A.daftar.forEach((W) => { if (peta[wbKunci(W)]) aktifNama[W] = true; });
  // kunci wadah lama (sudah ganti nama) yang bukunya nol tidak ditawarkan ke HP kasir
  // karung sisihan / bongkaran wadah & kemasan adukan yang dibuka tidak dijual dari HP kasir (dituang / ditakar ke wadah, atau jadi bahan adukan)
  const merkKarung = isi.merkKarung.filter((m) => !(bw[m.merk] && bw[m.merk].jenis !== 'wadah') && !(peta[m.merk] && A.daftar.indexOf(String(m.merk).slice(awal)) < 0 && Math.abs(m.sisaKg || 0) < 0.005)).map((m) => {
    if (peta[m.merk]) { const W = String(m.merk).slice(awal); const h = A.daftar.indexOf(W) >= 0 ? harga.find((x) => x.merk === W) : null;
      return Object.assign({}, m, { karung50: false, karung25: false, hargaKarung25: 0, hargaKarung50: 0, hargaPerKg: 0, hargaPerLiter: h ? Number(h.hargaPerLiter) || 0 : 0, rasio: wbRasio(W) }); }
    // putaran 28: buku per ukuran ('Merek 25 kg') = karung ukuran itu saja, harganya harga merek induk ukuran itu; induknya tidak lagi menawarkan ukuran itu
    if (uk[m.merk]) { const u = uk[m.merk]; const hg = (hargaKarungUtuh(u.induk, u.berat) || {}).perUnit || 0;
      return Object.assign({}, m, { karung50: u.berat === 50, karung25: u.berat === 25, hargaKarung25: u.berat === 25 ? hg : 0, hargaKarung50: u.berat === 50 ? hg : 0, hargaPerKg: cariHargaKarungPerKg(u.induk) || 0, hargaPerLiter: 0 }); }
    let x = m; if (tp[m.merk] && tp[m.merk][25]) x = Object.assign({}, x, { karung25: false, hargaKarung25: 0 });
    if (aktifNama[m.merk] && langsung.indexOf(m.merk) < 0 && x.hargaPerLiter) return Object.assign({}, x, { hargaPerLiter: 0 });
    return x; });
  return Object.assign({}, isi, { merkKarung });
}

// ---------- SISIHKAN · TUANG BALIK · BONGKAR (owner 28 Sep 2026) ----------
// "Buatkan stok terpisah untuk isi yang ada di dalam kotak wadah literan ketika isi dari wadah kotak literan itu dikosongkan": tiap tutup toko ±10 kg dari
// yang menggunung disisihkan ke karung wadah itu (60 → 50 + 10), besok dituang balik; setahun sekali wadah DIBONGKAR — isinya dikosongkan penuh ke karung.
// Karung itu = buku terpisah 'Karung wadah <nama>' (data/toko.js), kolamnya karung lepas (tidak menggeser karung merek di belakang wadah). Pindah buku
// dengan modal ikut → stok toko, laba, neraca tidak berubah; hanya bongkar yang menimbang, selisihnya jadi susut wadah (alasan di atas susut wajar).
const wbHariAntara = (dari, ke) => (dari && ke ? Math.round((new Date(ke + 'T00:00:00') - new Date(dari + 'T00:00:00')) / 86400000) : 0);
const wbAngkaKetik = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); return t === '' ? null : Number(t.replace(',', '.')); };
/** Karung sisihan / bongkaran wadah W: { kunci, lahir, bukuKg, sisaKg (kolam), diketahui }. */
export function wbKarungWadah(W) {
  const k = kunciKarungWadah(W); const st = ingatStokKarung()[k]; const kr = karungBelakang(k, '');
  return { kunci: k, lahir: !!st, bukuKg: st ? wbB2(st.sisaKg || 0) : 0, sisaKg: kr.diketahui ? wbB2(kr.sisaMentahKg) : 0, diketahui: kr.diketahui };
}
const wbDokKarungWadah = (W, kg, w, tanda) => ({ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karung', merk: kunciKarungWadah(W), kg: wbB2(kg), lepas: true, asal: 'wadah', dariWadah: W }, tanda || {}) });
/** SISIHKAN kg dari kotak wadah W ke karung wadahnya (kosong = angka owner di Aturan wadah, bawaan 10 kg). */
export function wbSusunSisih(W, kgKetik, w) {
  const A = aturWadah(); if (A.daftar.indexOf(W) < 0) return { tolak: W + ' bukan wadah' };
  if (!wbAktif(W)) return { tolak: 'Wadah ' + W + ' belum punya stok sendiri — pindahkan isi wadah ke stok wadah dulu (Stok › Wadah literan)' };
  const n = wbAngkaKetik(kgKetik); const kg = wbB2(n === null ? A.sisihKg : n);
  if (!(kg > 0)) return { tolak: 'Tulis berapa kg yang disisihkan ke karung' };
  const K = wbKomposisi(W);
  if (kg > K.totalKg + 0.004) return { tolak: 'Wadah ' + W + ' menurut bukunya cuma ±' + wbKG(K.totalKg) + ' — tidak bisa menyisihkan ' + wbKG(kg) + '. Kalau isinya memang lebih, cocokkan wadahnya dulu' };
  const k = kunciKarungWadah(W); const KW = wbKarungWadah(W); const dokumen = []; const lahir = wbDokLahir([{ merk: k, karungWadah: W }], w); if (lahir) dokumen.push(lahir);
  dokumen.push(wbDokPindah([{ merk: K.kunci, kg }], k, w, { sisihWadah: W, keterangan: 'Sisihkan dari wadah ' + W + ' ke karung wadahnya: ' + wbKG(kg) }));
  dokumen.push(wbDokKarungWadah(W, kg, w, { sisih: true }));
  return { dokumen, patch: { kabar: wbKG(kg) + ' dari wadah ' + W + ' disisihkan ke karung wadahnya — wadah ±' + wbKG(K.totalKg) + ' → ±' + wbKG(K.totalKg - kg) + ', karung sisihan ±' + wbKG(KW.sisaKg + kg)
    + '. Stok toko tidak berubah (buku pindah, modal ikut).', kabarAwas: false } };
}
/** TUANG BALIK karung wadah W ke kotaknya (kosong = seluruh isi karung). Tidak boleh melewati batas menggunung. */
export function wbSusunTuangBalik(W, kgKetik, w) {
  const A = aturWadah(); if (A.daftar.indexOf(W) < 0) return { tolak: W + ' bukan wadah' };
  if (!wbAktif(W)) return { tolak: 'Wadah ' + W + ' belum punya stok sendiri' };
  const KW = wbKarungWadah(W); if (!KW.lahir || !(KW.sisaKg > 0.004)) return { tolak: 'Karung sisihan wadah ' + W + ' kosong' };
  const n = wbAngkaKetik(kgKetik); const kg = wbB2(n === null ? KW.sisaKg : n);
  if (!(kg > 0)) return { tolak: 'Tulis berapa kg yang dituang balik' };
  if (kg > KW.sisaKg + 0.004) return { tolak: 'Karung sisihan wadah ' + W + ' cuma ±' + wbKG(KW.sisaKg) };
  const tw = tinggiWadah(W, null); const isiBaru = wbB2(tw.sisaNyataKg + kg);
  if (isiBaru > A.puncakKg + 0.0001) return { tolak: 'Dituang ' + wbKG(kg) + ', wadah jadi ±' + wbKG(isiBaru) + ' — melebihi ' + wbKG(A.puncakKg) + ' yang muat. Tulis kg yang dituang (paling banyak ±' + wbKG(Math.max(0, A.puncakKg - tw.sisaNyataKg)) + ')' };
  const idT = w.idUnik(); const pindah = wbDokPindah([{ merk: KW.kunci, kg }], wbKunci(W), w, { takarId: idT, tuangBalikWadah: W, keterangan: 'Tuang balik karung wadah ' + W + ' ke kotaknya: ' + wbKG(kg) });
  const dokumen = [{ koleksi: 'wadahLiteran', data: { id: idT, tanggal: w.tanggal, jam: w.jam, tipe: 'takar', wadah: W, takar: 0, kgPerTakar: A.takarKg, kg, sumber: [{ merk: KW.kunci, takar: 0, kg, dari: '' }],
    stokWadah: wbKunci(W), produksiId: pindah.data.id, tuangBalik: true } }, pindah];
  return { dokumen, patch: { kabar: wbKG(kg) + ' dari karung sisihan dituang balik ke wadah ' + W + ' — wadah ±' + wbKG(tw.sisaNyataKg) + ' → ±' + wbKG(isiBaru) + ', karung sisihan ±' + wbKG(KW.sisaKg - kg) + '. Stok toko tidak berubah.', kabarAwas: false } };
}
/**
 * BONGKAR wadah W (setahun sekali): seluruh isi kotak dikosongkan ke karung wadahnya. kgTimbang = hasil timbang; selisih dengan buku wadah = susut / lebih
 * wadah (penyesuaianStok, masuk laba) — di atas susut wajar × hari sejak hitungan terakhir wajib alasan. Dua ketukan. Wadah jadi kosong (titik samakan 0).
 */
export function wbSusunBongkar(W, kgTimbang, alasan, w, yakin) {
  const A = aturWadah(); if (A.daftar.indexOf(W) < 0) return { tolak: W + ' bukan wadah' };
  if (!wbAktif(W)) return { tolak: 'Wadah ' + W + ' belum punya stok sendiri — pindahkan isi wadah ke stok wadah dulu (Stok › Wadah literan)' };
  const X0 = wbAngkaKetik(kgTimbang); if (X0 === null) return { tolak: 'Timbang dulu hasil bongkarnya, lalu tulis kg-nya' };
  const X = wbB2(X0); if (!(X >= 0) || X > A.puncakKg + 20) return { tolak: 'Hasil timbang harus di antara 0 dan ' + wbKG(A.puncakKg + 20) };
  const K = wbKomposisi(W); const buku = wbB2(K.totalKg); const sel = wbB2(X - buku); const hpp = (hitungStokKarungPerMerk()[K.kunci] || {}).hppTerakhirPerKg || 0;
  const wajar = wbB2(A.susutWajarKg * Math.max(1, wbHariAntara(K.sejak, w.tanggal))); const al = String(alasan || '').trim();
  if (Math.abs(sel) > wajar + 0.0001 && !al) return { tolak: 'Hasil timbang ' + wbKG(X) + ', buku wadah ' + wbKG(buku) + ' — selisih ' + wbKG(sel) + ' di atas susut wajar ' + wbKG(wajar) + '. Tulis alasannya dulu' };
  if (!yakin) return { tolak: 'Bongkar wadah ' + W + ': ' + wbKG(X) + ' (ditimbang) pindah ke karung wadahnya, kotaknya jadi kosong' + (Math.abs(sel) >= 0.005 ? '; selisih ' + wbKG(sel) + ' dari buku jadi ' + (sel < 0 ? 'susut' : 'lebih') + ' wadah (±Rp' + Math.round(Math.abs(sel) * hpp).toLocaleString('id-ID') + ')' : '') + '. Ketuk sekali lagi', perluYakin: 'bongkar' };
  const k = kunciKarungWadah(W); const dokumen = []; const lahir = wbDokLahir([{ merk: k, karungWadah: W }], w); if (lahir) dokumen.push(lahir);
  if (Math.abs(sel) >= 0.005) dokumen.push({ koleksi: 'penyesuaianStok', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, merk: K.kunci, kgSistem: buku, kgFisik: X, selisihKg: sel, alasan: al || 'Susut wajar (bongkar wadah)',
    nilaiRp: Math.round(sel * hpp), hppPerKgSaatOpname: Math.round(hpp), bagian: 'wadah', wadah: W, bongkar: true } });
  if (X > 0.004) { dokumen.push(wbDokPindah([{ merk: K.kunci, kg: X }], k, w, { bongkarWadah: W, keterangan: 'Bongkar wadah ' + W + ': ' + wbKG(X) + ' (ditimbang) ke karung wadahnya' })); dokumen.push(wbDokKarungWadah(W, X, w, { bongkar: true })); }
  dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: W, tipe: 'isi', isiKg: 0, stokWadah: K.kunci, dariCocok: true, bongkar: true } });
  return { dokumen, patch: { kabar: 'Wadah ' + W + ' dibongkar: ' + wbKG(X) + ' ke karung wadahnya, kotaknya kosong' + (Math.abs(sel) >= 0.005 ? ' · selisih ' + wbKG(sel) + ' dari buku = ' + (sel < 0 ? 'susut' : 'lebih') + ' wadah (laba ' + (sel < 0 ? '−' : '+') + 'Rp' + Math.round(Math.abs(sel) * hpp).toLocaleString('id-ID') + ')' : ' · cocok dengan buku') + '.', kabarAwas: false } };
}

// ---------- literan LANGSUNG dari karungnya sendiri (tidak lewat wadah) ----------
/**
 * Merek yang dijual literan langsung dari karungnya (owner menandai di Harga › Literan; disimpan di aturan wadah — dokumen wadahLiteran tipe 'atur' kolom
 * literanLangsung, yang juga terbaca karyawan, supaya rak Jual owner & karyawan sama). Belum pernah
 * ditandai → bawaan TERUKUR: merek (bukan nama wadah) yang punya harga liter DAN pernah terjual literan langsung (baris literan tanpa dariWadah,
 * merkSumber = merek itu). Merek yang cuma lewat wadah tidak butuh harga liter sendiri — harga liter melekat pada WADAH.
 */
export function wbLiteranLangsung() {
  const A = aturWadah(); const wadah = A.daftar;
  if (A.literanLangsung) return { daftar: A.literanLangsung.filter((m) => wadah.indexOf(m) < 0), dariOwner: true };
  const berharga = {}; ambilHargaLiteran().forEach((h) => { if (Number(h.hargaPerLiter) > 0) berharga[String(h.merk)] = true; });
  const pernah = {}; ambilPenjualan().forEach((p) => { if (p.jenis === 'literan' && !p.dariWadah && p.merkSumber) pernah[String(p.merkSumber)] = true; });
  return { daftar: Object.keys(berharga).filter((m) => pernah[m] && wadah.indexOf(m) < 0).sort(), dariOwner: false };
}
/** Dokumen aturan wadah BARU (tipe 'atur') = aturan yang berlaku sekarang + perubahan `ubah` (riwayat aturan tersimpan; yang terbaru berlaku). */
export function wbDokAtur(ubah, w) {
  const A = aturWadah();
  const data = { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'atur', penuhKg: A.penuhKg, puncakKg: A.puncakKg, isiUlangKg: A.isiUlangKg, takarKg: A.takarKg, susutWajarKg: A.susutWajarKg, sisihKg: A.sisihKg,
    merekKarung: A.merekKarung.slice(), daftar: A.daftar.slice(), resep: Object.assign({}, A.resep) };
  if (A.literanLangsung) data.literanLangsung = A.literanLangsung.slice();
  return { koleksi: 'wadahLiteran', data: Object.assign(data, ubah || {}) };
}
/** Tandai / lepas satu merek sebagai literan-langsung: aturan wadah baru (kolom lain dibawa apa adanya). */
export function wbSusunLiteranLangsung(merk, nyala, w) {
  const m = String(merk || ''); if (!m) return { tolak: 'Pilih mereknya dulu' };
  if (aturWadah().daftar.indexOf(m) >= 0) return { tolak: m + ' adalah nama WADAH — harga litrnya harga wadah itu' };
  const L = wbLiteranLangsung(); const set = L.daftar.slice(); const ada = set.indexOf(m) >= 0;
  if (!!nyala === ada) return { tolak: m + (ada ? ' sudah' : ' belum') + ' ditandai literan langsung' };
  const daftar = nyala ? set.concat([m]).sort() : set.filter((x) => x !== m);
  return { dokumen: [wbDokAtur({ literanLangsung: daftar }, w)],
    patch: { kabar: m + (nyala ? ' ditandai: dijual literan LANGSUNG dari karungnya — butuh harga liter sendiri, tampil di rak Literan.' : ' tidak lagi dijual literan langsung — literannya lewat wadah saja (harga liter wadah).'), kabarAwas: false } };
}

// ---------- nama kelas mutu / nama wadah: TIDAK dibukukan lewat barang masuk ----------
export const MEREK_KARUNG_BAWAAN = ['Angsa', 'Perahu Layar', 'Pandan Wangi'];   // keputusan owner 27 Sep: nama wadah yang sekaligus merek karung pemasok
/** Nama yang ditolak barang masuk: semua nama wadah (sekarang & yang pernah dipakai di aturan wadah) kecuali yang juga merek karung (Aturan wadah). */
export function wbNamaKelas() {
  const A = aturWadah(); const merek = {}; A.merekKarung.forEach((m) => { merek[m] = true; }); const out = {};
  A.daftar.concat(DAFTAR_WADAH).forEach((m) => { if (!merek[m]) out[m] = true; });
  ambilWadahLiteran().forEach((d) => { if (d.tipe === 'atur' && Array.isArray(d.daftar)) d.daftar.forEach((m) => { if (!merek[m]) out[String(m)] = true; }); });
  return out;
}

// ---------- GANTI NAMA WADAH (owner 27 Sep: "wadah kotak literan Angsa/Perahu Layar dll bisa diganti") ----------
/**
 * Wadah = tempat; namanya boleh diganti. Isi, karung di belakangnya, dan harga liternya IKUT pindah ke nama baru di kiriman yang sama: aturan wadah dengan
 * nama baru di posisi yang sama, titik samakan isi untuk nama baru (isi & komposisi sekarang, mentah), titik samakan karung terbuka di belakangnya
 * (sisa sekarang), dan harga liter nama baru = harga nama lama (kalau nama baru belum punya). Buku stok tidak disentuh.
 */
export function wbSusunGantiNama(lama, baru, w) {
  const L = String(lama || ''); const B = String(baru || '').replace(/\s+/g, ' ').trim(); const A = aturWadah(); const i = A.daftar.indexOf(L);
  if (i < 0) return { tolak: L + ' bukan wadah' };
  if (!B) return { tolak: 'Tulis nama wadah yang baru' };
  if (B.length > 40) return { tolak: 'Nama wadah paling panjang 40 huruf' };
  if (B === L) return { tolak: 'Namanya sama' };
  if (A.daftar.indexOf(B) >= 0) return { tolak: B + ' sudah jadi nama wadah lain' };
  const daftar = A.daftar.slice(); daftar[i] = B; const resep = Object.assign({}, A.resep); if (resep[L]) { resep[B] = resep[L]; delete resep[L]; }
  const K = wbKomposisi(L);
  // putaran 28: wadah berstok sendiri — stoknya ikut pindah ke buku nama baru (lahir + pindah buku); stok minus harus dicocokkan dulu (tidak dipindah diam-diam)
  if (K.stokSendiri && K.totalKg < -0.004) return { tolak: 'Stok wadah ' + L + ' tercatat minus ' + wbKG(-K.totalKg) + ' — cocokkan wadahnya dulu, baru ganti nama' };
  // 39b no. 6: buku KARUNG DI BELAKANG (putaran 39, per merek asal) ikut nama baru — dulu tertinggal sebagai buku yatim 'Karung belakang <lama> · M'
  // dan isi ulang sesudahnya membuka karung BARU dari tumpukan gudang (tumpukan turun tanpa karung diambil). Buku minus dicocokkan dulu, tidak dipindah diam-diam.
  const KBL = K.stokSendiri ? wbKarungBelakangWadah(L) : [];
  const kbMinus = KBL.filter((k) => k.bukuKg < -0.004);
  if (kbMinus.length) return { tolak: 'Karung di belakang ' + L + ' tercatat minus (' + kbMinus.map((k) => k.merk + ' ' + wbKG(k.bukuKg)).join(', ') + ') — samakan karungnya dulu, baru ganti nama' };
  const dokumen = [wbDokAtur({ daftar, resep, gantiNama: { dari: L, ke: B } }, w)];
  if (K.stokSendiri) { const lahir = wbDokLahir([{ merk: wbKunci(B), stokWadah: B }], w); if (lahir) dokumen.push(lahir);
    if (K.totalKg > 0.004) dokumen.push(wbDokPindah([{ merk: K.kunci, kg: K.totalKg }], wbKunci(B), w, { gantiNamaWadah: { dari: L, ke: B }, keterangan: 'Ganti nama wadah ' + L + ' → ' + B + ': stok wadah ' + wbKG(K.totalKg) + ' ikut pindah' }));
    // 39b no. 6: komposisi turunan (merek asal) ikut dibawa titik samakan nama baru — riwayat isi ulangnya bernama L, jadi tanpa ini B "belum ada isi ulang"
    const kmp = wbKomposisiTurunanKg(L, K.totalKg);
    dokumen.push({ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: B, tipe: 'isi', isiKg: wbB2(K.totalKg), stokWadah: wbKunci(B), gantiNamaDari: L }, Object.keys(kmp).length ? { komposisi: kmp } : {}) }); }
  else if (K.diketahui) dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: B, tipe: 'isi', isiKg: wbB2(K.totalKg), komposisi: Object.assign({}, K.bagian), gantiNamaDari: L } });
  const kn = karungUntukWadah(L); const kbBuku = K.stokSendiri && KBL.some((k) => k.kunci === kn.merk); const kb = kn.dariCatatan && !kbBuku ? karungBelakang(kn.merk, L) : null;   // karung berbuku: dipindah di bawah (nama kunci baru)
  const sebelum = {}; semuaKarungTerbuka().forEach((k) => { sebelum[k.merk + '|' + k.lokasi] = k.sisaMentahKg; });
  if (kb && kb.diketahui) { dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk: kn.merk, isiKg: wbB2(kb.sisaMentahKg), wadah: B, gantiNamaDari: L } });
    sebelum[kn.merk + '|' + L] = 0; }   // kolam di belakang L PINDAH ke B
  // Catatan karung lama tanpa kolom wadah dibaca menurut daftar wadah SEKARANG: sesudah nama berganti, kolamnya bisa tertinggal di nama lama atau terbaca
  // jadi karung lepas → terhitung dua kali. Tiap kolam (selain B) yang berubah karena ganti nama disamakan lagi ke angkanya sebelum ganti nama (0 bila dulu
  // tidak ada): jumlah karung terbuka sebelum = sesudah, tumpukan gudang tidak bergeser.
  const sesudah = denganCacheSementara(dokumen, () => semuaKarungTerbuka());
  sesudah.forEach((k) => { if (k.lokasi === B) return; const lama = sebelum[k.merk + '|' + k.lokasi] || 0; if (Math.abs(k.sisaMentahKg - lama) < 0.005) return;
    dokumen.push({ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk: k.merk, isiKg: wbB2(lama), gantiNamaDari: L }, k.lokasi ? { wadah: k.lokasi } : { lepas: true }) }); });
  // putaran 28: karung sisihan / bongkaran wadah ikut nama baru (bukunya dipindah, kolamnya dipindah) — ditulis SESUDAH penyamaan kolam di atas
  const KWL = K.stokSendiri ? wbKarungWadah(L) : null; let kwPindah = 0;
  if (KWL && KWL.lahir && (KWL.bukuKg > 0.004 || KWL.sisaKg > 0.004)) {
    const kB = kunciKarungWadah(B); const lahirK = wbDokLahir([{ merk: kB, karungWadah: B }], w); if (lahirK) dokumen.push(lahirK);
    if (KWL.bukuKg > 0.004) { kwPindah = KWL.bukuKg; dokumen.push(wbDokPindah([{ merk: KWL.kunci, kg: KWL.bukuKg }], kB, w, { gantiNamaWadah: { dari: L, ke: B }, keterangan: 'Ganti nama wadah ' + L + ' → ' + B + ': karung wadahnya ' + wbKG(KWL.bukuKg) + ' ikut pindah' })); }
    if (KWL.sisaKg > 0.004) { dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk: KWL.kunci, isiKg: 0, lepas: true, gantiNamaDari: L } });
      dokumen.push(wbDokKarungWadah(B, KWL.sisaKg, w, { gantiNamaDari: L })); }
  }
  // 39b no. 6 (sesudah penyamaan kolam di atas, seperti karung sisihan): tiap buku karung belakang → 'Karung belakang <baru> · M' (lahir + pindah buku, modal ikut);
  // kolam catatannya pindah bernama kunci baru di belakang B, kolam lama dinolkan. Karung yang BERDIRI di belakang (karungUntukWadah) ditulis terakhir supaya tetap berdiri.
  // tinjauan W1: kolam yang sudah DITUTUP (dikembalikan / dihapus habis) tidak dihidupkan lagi di nama baru — buku sisanya (bila ada) tinggal di kunci lama
  // (Stok › Wadah literan › buku karung yang tertinggal). W2: urutan tulis = urutan karung itu dibuka / disamakan di nama lama (lama → baru), terdepan paling akhir
  // (catatan bertanda diamSlot tidak dihitung — sama dengan cara karungUntukWadah memilih karung terdepan)
  const saat = (k) => wdTerbaru(ambilWadahLiteran().filter((x) => (x.tipe === 'karung' || x.tipe === 'karungIsi') && x.merk === k.kunci && x.wadah === L && !x.diamSlot));
  const urutSaat = (a, b) => { const x = saat(a), y = saat(b); return !x || !y ? (x ? 1 : 0) - (y ? 1 : 0) : wdSesudah(x, y) ? 1 : wdSesudah(y, x) ? -1 : 0; };
  KBL.filter((k) => !(k.diketahui && kolamDitutup(k.kunci, L))).sort((a, b) => (a.kunci === kn.merk ? 1 : 0) - (b.kunci === kn.merk ? 1 : 0) || urutSaat(a, b)).forEach((k) => {
    const kB = wbKunciKB(B, k.merk); const lahirB = wbDokLahir([{ merk: kB, karungBelakang: B, merkAsal: k.merk }], w); if (lahirB) dokumen.push(lahirB);
    if (k.bukuKg > 0.004) dokumen.push(wbDokPindah([{ merk: k.kunci, kg: k.bukuKg }], kB, w, { gantiNamaWadah: { dari: L, ke: B }, merkAsal: k.merk, keterangan: 'Ganti nama wadah ' + L + ' → ' + B + ': karung di belakang ' + k.merk + ' ' + wbKG(k.bukuKg) + ' ikut pindah (' + k.kunci + ' → ' + kB + ')' }));
    // kolam lama dinolkan DI TEMPATNYA (di belakang L) — dulu ditulis lepas, catatan di belakang L tetap berisi → karung hantu "dulu di belakang wadah L"
    if (k.diketahui) { dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk: k.kunci, merkAsal: k.merk, isiKg: 0, wadah: L, selesai: true, gantiNamaDari: L } });
      dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk: kB, merkAsal: k.merk, isiKg: wbB2(k.kolamKg), wadah: B, bukuBelakang: true, gantiNamaDari: L } }); } });
  const hL = ambilHargaLiteran().find((h) => h.merk === L); const hB = ambilHargaLiteran().find((h) => h.merk === B);
  if (hL && Number(hL.hargaPerLiter) > 0 && !hB) dokumen.push({ koleksi: 'katalogHargaLiteran', data: { id: B, merk: B, hargaPerLiter: Number(hL.hargaPerLiter), diubahPada: w.kini, modalSaatSetel: 0 } });
  return { dokumen, patch: { kabar: 'Wadah ' + L + ' sekarang bernama ' + B + ' — isi' + (K.diketahui ? ' ±' + String(wbB2(K.totalKg)).replace('.', ',') + ' kg' : '') + ', karung di belakangnya' + (hL ? ', dan harga liternya' : '') + ' ikut pindah. ' + (K.stokSendiri ? 'Stok wadahnya pindah dari buku ' + K.kunci + ' ke ' + wbKunci(B) + (kwPindah ? ', karung wadahnya ' + wbKG(kwPindah) + ' ikut' : '') + ' (modal ikut).' : 'Buku stok tidak berubah.'), kabarAwas: false } };
}

// ---------- SATU BUKU PER KOTAK (putaran 39, keputusan owner 29 Sep 2026) ----------
// (a) satu buku per wadah — semua peristiwa menulis ke buku itu (isi ulang masuk, literan keluar, cocokkan sebagai penyesuaian bertanda); tidak ada estimasi
//     isi wadah terpisah dari buku. Mekanismenya buku 'Wadah <nama>' putaran 28, diaktifkan PER WADAH lewat daftar (wbDaftarAktivasi / wbSusunAktifkan).
// (1) karung di belakang wadah = BUKU MESIN sendiri per wadah × merek asal ('Karung belakang <W> · <merek>', data/toko.js): buka karung = pindah buku
//     merek → karung belakang (tumpukan gudang turun di buku), takar/tuang = pindah buku karung belakang → wadah. Kolam catatan 'karung'/'takar' tetap
//     ditulis (bernama kunci bukunya, merkAsal = merek pemasok) supaya deretan, panel, dan tanggal tetap terbaca; selisih kolam vs buku DISEBUT (f).
// (b) isi ulang TIGA KETUKAN (Jual & Stok): kotak ← merek asal dari rak × takaran (1 karung / ½ karung / kg) — wbSusunIsiUlangTiga; jam & siapa dari
//     atribusi pusat (oleh/olehUid). Panel − / + takar lama tetap ada sebagai takaran lain (susunTakarWadah, jual-logika.js).
// (c) komposisi & banding = TURUNAN isi ulang sejak titik samakan terakhir, disebar sebanding ke buku wadah (wbKomposisiTurunan) — bukan angka kedua.
// (d) buku merek asal kurang → tidak diam & tidak menulis hantu: { tolak, perluTandai } = "catat barang masuk dulu" atau "tandai untuk dicocokkan"
//     (opsi.tandai → dokumen pindah bertanda perluCocokkan + selisihKg + selisihPerMerk; buku merek dibiarkan minus; boleh karyawan, namanya tercatat).
// (e) cek wadah tutup toko: sesuai · lupa isi ulang · dikosongkan (= seluruh isi disisihkan ke karung wadah tanpa timbang) — wadahLiteran tipe 'cek'.
// Mesin beku tidak disentuh: semua lewat batch lahir 0 kg, produksiKemasan jadi-karung-utuh, wadahLiteran, penyesuaianStok (bentuk yang sudah dibaca).
export const WB_CEK = [['sesuai', 'Sesuai'], ['lupa', 'Lupa isi ulang'], ['kosong', 'Dikosongkan']];
export const WB_TAKARAN = [['karung', '1 karung'], ['setengah', '½ karung'], ['kg', 'kg']];
/** Kunci buku karung di belakang wadah W untuk merek asal M. */
export const wbKunciKB = (W, M) => kunciKarungBelakang(W, M);
/** Merek asal di balik satu nama kolam / kunci buku (karung belakang → merek pemasok; selain itu nama itu sendiri). */
export const wbMerkAsal = (kunci, peta) => merkAsalKunci(kunci, peta);
/** Kunci ini buku KHUSUS (wadah / karung wadah / adukan / karung belakang)? */
export const wbBukuKhusus = (kunci, peta) => !!(peta || petaBukuWadah())[String(kunci)];
const wbAngkaKg = (v) => Number(String(v === undefined || v === null ? '' : v).trim().replace(',', '.')) || 0;

/** Karung belakang wadah W merek M: buku (mesin) vs kolam (catatan) — dua sisi, selisihnya disebut. */
export function wbKarungBelakang(W, M) {
  const k = wbKunciKB(W, M); const st = ingatStokKarung()[k]; const kr = karungBelakang(k, W);
  const bukuKg = st ? wbB2(st.sisaKg || 0) : 0; const kolamKg = kr.diketahui ? wbB2(kr.sisaMentahKg) : 0;
  return { kunci: k, wadah: W, merk: M, lahir: !!st, bukuKg, kolamKg, diketahui: kr.diketahui, selisihKg: kr.diketahui ? wbB2(kolamKg - bukuKg) : 0, hpp: st ? st.hppTerakhirPerKg || 0 : 0, penuhKg: beratKarungBuka(M) };
}
/** Semua karung belakang wadah W yang bukunya sudah lahir: [wbKarungBelakang] (yang bukunya > 0 dulu). */
export function wbKarungBelakangWadah(W) {
  const bw = petaBukuWadah(); return Object.keys(bw).filter((k) => bw[k].jenis === 'belakang' && bw[k].wadah === W && bw[k].merk).map((k) => wbKarungBelakang(W, bw[k].merk)).sort((a, b) => b.bukuKg - a.bukuKg || a.merk.localeCompare(b.merk));
}
/**
 * BUKA n karung merek M dari tumpukan gudang di belakang wadah AKTIF W. Dokumen: lahir buku karung belakang (bila belum) → pindah buku M → karung belakang
 * (n × berat karung M) → catatan 'karung' per karung (kolam bernama kunci bukunya). Buku M kurang → { tolak, perluTandai } kecuali opsi.tandai (pindah
 * bertanda perluCocokkan + selisihKg). sesudah = dokumen kiriman yang sama yang sudah disusun (keadaan dihitung seolah sudah tertulis).
 */
export function wbDokBukaKB(W, M, nKarung, w, opsi, sesudah) {
  const n = Math.max(1, Math.round(Number(nKarung) || 1)); const berat = beratKarungBuka(M); const kg = wbB2(berat * n); const k = wbKunciKB(W, M);
  return denganCacheSementara(sesudah || [], () => {
    const st = hitungStokKarungPerMerk()[M];
    if (!st) return { tolak: M + ' tidak ada di buku gudang — karung di belakang wadah diambil dari karung yang tercatat masuk gudang (catat barang masuknya dulu)' };
    const buku = wbB2(st.sisaKg || 0); const kurang = wbB2(kg - buku);
    if (kurang > 0.004 && !(opsi && opsi.tandai)) return { tolak: 'Buku ' + M + ' tinggal ' + wbKG(buku) + ', mau dibuka ' + n + ' karung (' + wbKG(kg) + ') — kurang ' + wbKG(kurang) + '. Catat barang masuk dulu, atau tandai untuk dicocokkan (buku ' + M + ' dibiarkan minus sampai dihitung)',
      perluTandai: [{ merk: M, buku, butuh: kg, kurang }] };
    const dokumen = []; const lahir = wbDokLahir([{ merk: k, karungBelakang: W, merkAsal: M }], w); if (lahir) dokumen.push(lahir);
    const p = wbDokPindah([{ merk: M, kg }], k, w, Object.assign({ bukaKarung: W, merkAsal: M, keterangan: 'Buka ' + n + ' karung ' + M + ' (' + wbKG(kg) + ') dari tumpukan gudang di belakang wadah ' + W + ' → ' + k },
      kurang > 0.004 ? { perluCocokkan: true, selisihKg: kurang, selisihPerMerk: { [M]: kurang } } : {}));
    dokumen.push(p);
    for (let i = 0; i < n; i++) dokumen.push({ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karung', merk: k, merkAsal: M, kg: berat, wadah: W, bukuBelakang: true, produksiId: p.data.id }, opsi && opsi.otomatis ? { otomatis: true } : {}, opsi && opsi.asal ? opsi.asal : {}) });
    return { dokumen, kunci: k, kg, berat, n, buku, sesudahKg: wbB2(buku - kg), kurang: Math.max(0, kurang), tandai: kurang > 0.004 };
  });
}
/** TUANG kg dari karung belakang (W, M) ke buku wadah W: satu catatan 'takar' + satu pindah buku (modal karung belakang ikut). */
function wbDokTuangKB(W, M, kg, w, takaran, sesudah) {
  const k = wbKunciKB(W, M); const kunci = wbKunci(W); const idT = w.idUnik(); const A = aturWadah();
  return denganCacheSementara(sesudah || [], () => {
    const p = wbDokPindah([{ merk: k, kg }], kunci, w, { takarId: idT, merkAsal: M, keterangan: 'Isi ulang wadah ' + W + ': ' + wbKG(kg) + ' ' + M + ' dari karung di belakangnya → ' + kunci });
    const takar = Math.round(kg / A.takarKg * 10) / 10;
    return { dokumen: [{ koleksi: 'wadahLiteran', data: { id: idT, tanggal: w.tanggal, jam: w.jam, tipe: 'takar', wadah: W, takar, kgPerTakar: A.takarKg, kg, takaran: takaran || 'kg', sumber: [{ merk: k, merkAsal: M, takar, kg, dari: W }], stokWadah: kunci, produksiId: p.data.id } }, p], pindah: p.data };
  });
}
/**
 * ISI ULANG TIGA KETUKAN (owner 29 Sep b): wadah AKTIF W ← merek asal M dari rak × takaran { jenis: 'karung' | 'setengah' | 'kg', kg? }. Karung di belakang
 * wadah (buku 'Karung belakang W · M') dipakai dulu; kurang → karung baru dibuka dari tumpukan gudang M (pindah buku, sebanyak yang perlu); lalu kg-nya
 * dituang (pindah buku karung belakang → wadah). Melewati batas menggunung DITOLAK. Buku M kurang → { tolak, perluTandai } kecuali opsi.tandai.
 * Satu kiriman: [lahir?, pindah M → karung belakang?, karung…, takar, pindah karung belakang → wadah].
 */
export function wbSusunIsiUlangTiga(W, M, takaran, w, s, opsi) {
  const A = aturWadah(); if (A.daftar.indexOf(W) < 0) return { tolak: W + ' bukan wadah' };
  if (!wbAktif(W)) return { tolak: 'Wadah ' + W + ' belum punya buku sendiri — aktifkan dulu di Stok › Wadah literan (daftar aktivasi), atau isi ulang lewat − / + takar' };
  const merk = String(M || '').trim(); if (!merk) return { tolak: 'Pilih dulu beras apa yang dituang' };
  const bw = petaBukuWadah(); if (bw[merk] && bw[merk].jenis === 'wadah') return { tolak: merk + ' adalah buku wadah — pilih merek karungnya' };
  const t = takaran || {}; const berat = beratKarungBuka(merk);
  let kg = t.jenis === 'karung' ? berat : t.jenis === 'setengah' ? wbB2(berat / 2) : wbB2(wbAngkaKg(t.kg));
  if (!(kg > 0)) return { tolak: t.jenis === 'kg' ? 'Ketik berapa kg yang dituang (tuts angka)' : 'Pilih takarannya: 1 karung, ½ karung, atau kg' };
  const tw = tinggiWadah(W, s || null); let isiBaru = wbB2(tw.sisaNyataKg + kg);
  if (isiBaru > A.puncakKg + 0.0001) return { tolak: 'Kalau dituang ' + wbKG(kg) + ', wadah ' + W + ' jadi ±' + wbKG(isiBaru) + ' — melebihi ' + wbKG(A.puncakKg) + ' yang muat. Paling banyak ±' + wbKG(Math.max(0, A.puncakKg - tw.sisaNyataKg)) + ' (pilih takaran kg) — layar tidak memotong diam-diam' };
  const stok0 = hitungStokKarungPerMerk(); const bukuM0 = stok0[merk] ? wbB2(stok0[merk].sisaKg || 0) : null;
  const KB = wbKarungBelakang(W, merk); const dokumen = []; let dibuka = 0, kurang = 0, tandai = false;
  // 39c (owner 30 Sep): karung di belakang dihabiskan dulu sampai bersih 0 — bukunya masih bersisa tapi kurang dari yang diminta → tuang SEADANYA sebesar sisanya, tanpa membuka karung baru
  const seadanya = KB.bukuKg > 0.004 && KB.bukuKg + 0.004 < kg; const kgMinta = kg; if (seadanya) { kg = wbB2(KB.bukuKg); isiBaru = wbB2(tw.sisaNyataKg + kg); }
  const butuhBuka = wbB2(kg - Math.max(0, KB.bukuKg));
  if (butuhBuka > 0.004) { const n = Math.ceil((butuhBuka - 0.0001) / berat); const b = wbDokBukaKB(W, merk, n, w, opsi, dokumen); if (b.tolak) return b; b.dokumen.forEach((d) => dokumen.push(d)); dibuka = n; kurang = b.kurang; tandai = b.tandai; }
  const tg = wbDokTuangKB(W, merk, kg, w, t.jenis || 'kg', dokumen); if (seadanya) tg.dokumen[0].data.seadanya = true, tg.dokumen[0].data.kgMinta = kgMinta; tg.dokumen.forEach((d) => dokumen.push(d));
  const sisaKB = wbB2(Math.max(0, KB.bukuKg) + dibuka * berat - kg); const bukuM1 = bukuM0 === null ? null : wbB2(bukuM0 - dibuka * berat);
  const takaranTeks = t.jenis === 'karung' ? '1 karung' : t.jenis === 'setengah' ? '½ karung' : wbKG(kgMinta);   // yang DIMINTA (seadanya: kg sudah dikurangi)
  // owner 7 Okt: karung di belakang yang dituang habis = karung bekas +1 di kiriman yang sama (akun bukan-owner: dititip, owner mencatatnya)
  return wbSertakanKarungBekas({ dokumen, hitung: { wadah: tw, kg, kgMinta, seadanya, isiBaru, takar: Math.round(kg / A.takarKg), banding: '', merk, dibuka, sisaKB, takaran: t.jenis || 'kg' }, pindahBuku: tg.pindah, tandai, kurang,
    patch: { kabar: 'Wadah ' + W + (seadanya ? ' diisi SEADANYA ' + wbKG(kg) + ' ' + merk + ' (minta ' + takaranTeks + (t.jenis === 'kg' ? '' : ' = ' + wbKG(kgMinta)) + '; karung di belakang bersih 0 — ketuk lagi untuk karung baru dari tumpukan)' : ' diisi ' + takaranTeks + ' ' + merk + (t.jenis === 'kg' ? '' : ' (' + wbKG(kg) + ')')) + ' → isinya ±' + wbKG(isiBaru) + ' (buku wadah)'
      + (dibuka ? ' · ' + dibuka + ' karung ' + merk + ' dibuka dari tumpukan gudang: buku ' + merk + ' ' + wbKG(bukuM0 || 0) + ' → ' + wbKG(bukuM1 || 0) : ' · dari karung yang sudah terbuka di belakangnya')
      + ' · sisa di karung belakang ±' + wbKG(sisaKB)
      + (tandai ? ' · buku ' + merk + ' KURANG ' + wbKG(kurang) + ' — DITANDAI untuk dicocokkan (buku dibiarkan minus sampai dihitung)' : ''), kabarAwas: tandai } }, w, { staf: Number(s && s.batasDok) > 0 });
}

/**
 * DAFTAR AKTIVASI per wadah (owner 29 Sep: data lama yang sudah terlanjur berbeda tidak diubah diam-diam — daftar per wadah, owner memutuskan).
 * Tiap wadah yang belum aktif: isi tercatat per merek asal + karung terbuka (bernama merek) di belakangnya = yang harus pindah dari buku merek asal;
 * dibandingkan dengan buku merek itu → kekurangan. bisa = boleh diaktifkan (isi diketahui, tidak minus, semua merek punya buku); cukup = tanpa kekurangan.
 */
export function wbDaftarAktivasi() {
  const A = aturWadah(); const peta = petaStokWadah(); const stok = ingatStokKarung(); const bw = petaBukuWadah(); const semuaKolam = semuaKarungTerbuka();
  return A.daftar.map((W, i) => {
    const aktif = wbAktif(W, peta); const K = wbKomposisi(W);
    const kolam = semuaKolam.filter((k) => k.lokasi === W && !bw[k.merk] && k.sisaMentahKg > 0.004).map((k) => ({ merk: k.merk, kg: wbB2(k.sisaMentahKg) }));
    const butuh = {}; Object.keys(K.bagian).forEach((m) => { if (K.bagian[m] > 0.004) butuh[m] = wbB2((butuh[m] || 0) + K.bagian[m]); });
    kolam.forEach((k) => { butuh[k.merk] = wbB2((butuh[k.merk] || 0) + k.kg); });
    const sumber = Object.keys(butuh).sort().map((m) => { const b = stok[m] ? wbB2(stok[m].sisaKg || 0) : null; const diK = wbB2(kolam.filter((k) => k.merk === m).reduce((a, k) => a + k.kg, 0));
      return { merk: m, kg: butuh[m], diWadah: wbB2(K.bagian[m] > 0 ? K.bagian[m] : 0), diKarung: diK, buku: b, kurang: b === null ? butuh[m] : wbB2(Math.max(0, butuh[m] - b)), tanpaBuku: b === null }; });
    const minus = Object.keys(K.bagian).filter((m) => K.bagian[m] < -0.004); const kurang = sumber.filter((x) => x.kurang > 0.004); const tanpa = sumber.filter((x) => x.tanpaBuku);
    const alasan = aktif ? 'sudah punya buku sendiri' : !K.diketahui ? 'isinya belum pernah dicocokkan — samakan dulu (rata / menggunung / angka)' : minus.length ? 'bagian ' + minus.join(', ') + ' tercatat minus — cocokkan wadahnya dulu'
      : tanpa.length ? 'bagian ' + tanpa.map((x) => x.merk).join(', ') + ' tidak punya buku — catat barang masuknya dulu' : kurang.length ? 'buku ' + kurang.map((x) => x.merk + ' kurang ' + wbKG(x.kurang)).join(', ') + ' — hitung fisik / catat barang masuk dulu, atau tandai untuk dicocokkan' : '';
    return { no: 'W' + (i + 1), W, aktif, diketahui: K.diketahui, isiKg: wbB2(K.totalKg), sumber, kolam, minus, kurang, bisa: !aktif && K.diketahui && !minus.length && !tanpa.length, cukup: !kurang.length, alasan };
  });
}
/**
 * AKTIFKAN satu wadah (per wadah, bukan sekaligus): buku wadah lahir, isi tercatat pindah dari buku merek asal (modal ikut), karung terbuka bernama merek di
 * belakangnya jadi buku karung belakang. Buku merek kurang → { tolak, perluTandai } kecuali opsi.tandai (pindah bertanda perluCocokkan + selisihPerMerk).
 * Nilai stok, laba, dan neraca tidak berubah (pindah buku dengan modal ikut). Komposisi awal disimpan di titik samakan (bahan komposisi turunan).
 */
export function wbSusunAktifkan(W, w, opsi) {
  const d = wbDaftarAktivasi().find((x) => x.W === W); if (!d) return { tolak: W + ' bukan wadah' };
  if (!d.bisa) return { tolak: 'Wadah ' + W + ': ' + d.alasan };
  if (!d.cukup && !(opsi && opsi.tandai)) return { tolak: 'Wadah ' + W + ': ' + d.alasan, perluTandai: d.kurang.map((x) => ({ merk: x.merk, buku: x.buku, butuh: x.kg, kurang: x.kurang })) };
  const kunci = wbKunci(W); const K = wbKomposisi(W); const dokumen = [];
  const lahir = wbDokLahir([{ merk: kunci, stokWadah: W }].concat(d.kolam.map((k) => ({ merk: wbKunciKB(W, k.merk), karungBelakang: W, merkAsal: k.merk }))), w); if (lahir) dokumen.push(lahir);
  const sisaKurang = {}; d.sumber.forEach((x) => { sisaKurang[x.merk] = x.kurang; });
  const tanda = (list) => { const per = {}; let tot = 0; list.forEach((x) => { const n = Math.min(x.kg, sisaKurang[x.merk] || 0); if (n > 0.004) { per[x.merk] = wbB2(n); tot += n; sisaKurang[x.merk] = wbB2(sisaKurang[x.merk] - n); } }); return tot > 0.004 ? { perluCocokkan: true, selisihKg: wbB2(tot), selisihPerMerk: per } : {}; };
  const sumberW = Object.keys(K.bagian).filter((m) => K.bagian[m] > 0.004).sort().map((m) => ({ merk: m, kg: wbB2(K.bagian[m]) })); const komposisi = {}; sumberW.forEach((x) => { komposisi[x.merk] = x.kg; });
  if (sumberW.length) dokumen.push(wbDokPindah(sumberW, kunci, w, Object.assign({ pindahAwalWadah: W, keterangan: 'Aktivasi buku wadah ' + W + ': ' + sumberW.map((y) => y.merk + ' ' + wbKG(y.kg)).join(' + ') + ' → ' + kunci }, tanda(sumberW))));
  dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: W, tipe: 'isi', isiKg: d.isiKg, stokWadah: kunci, pindahAwal: true, komposisi } });
  // 39b no. 5 tinjauan S8: karung yang TADINYA terdepan di belakang W ditulis TERAKHIR supaya tetap terdepan (dulu urut abjad: terdepan berganti diam-diam)
  const depan0 = karungUntukWadah(W).merk;
  d.kolam.slice().sort((a, b) => (a.merk === depan0 ? 1 : 0) - (b.merk === depan0 ? 1 : 0)).forEach((k) => { const kb = wbKunciKB(W, k.merk);
    dokumen.push(wbDokPindah([{ merk: k.merk, kg: k.kg }], kb, w, Object.assign({ bukaKarung: W, merkAsal: k.merk, pindahAwalWadah: W, keterangan: 'Aktivasi buku wadah ' + W + ': karung terbuka ' + k.merk + ' ' + wbKG(k.kg) + ' di belakangnya → ' + kb }, tanda([k]))));
    dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk: k.merk, isiKg: 0, wadah: W, pindahAwal: true } });
    dokumen.push({ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'karungIsi', merk: kb, merkAsal: k.merk, isiKg: k.kg, wadah: W, bukuBelakang: true, pindahAwal: true } }); });
  const rp = dokumen.filter((x) => x.koleksi === 'produksiKemasan').reduce((a, x) => a + (x.data.hppPerUnit || 0), 0); const turun = d.sumber.map((x) => x.merk + ' −' + wbKG(x.kg)).join(', ');
  return { dokumen, jadi: d, rp: Math.round(rp), tandai: !d.cukup,
    patch: { kabar: 'Wadah ' + W + ' kini punya buku sendiri: isi ' + wbKG(d.isiKg) + (d.kolam.length ? ' + karung di belakangnya ' + d.kolam.map((k) => k.merk + ' ' + wbKG(k.kg)).join(', ') + ' (buku sendiri)' : '') + '. Buku merek turun: ' + (turun || 'tidak ada') + ' — modal ikut, laba & neraca tidak berubah.'
      + (!d.cukup ? ' Buku ' + d.kurang.map((x) => x.merk + ' KURANG ' + wbKG(x.kurang)).join(', ') + ' — DITANDAI untuk dicocokkan (dibiarkan minus sampai dihitung).' : ''), kabarAwas: !d.cukup } };
}

/**
 * KOMPOSISI TURUNAN (owner 29 Sep c): merek asal isi wadah W sekarang, dari riwayat isi ulang sejak titik samakan terakhir (komposisi awal di titik itu +
 * tiap takar per merek asal), disebar sebanding ke isi/buku wadah sekarang; banding disederhanakan ("Kumala 3 : NG 2"), plus jam & siapa isi ulang terakhir.
 * Wadah belum aktif → komposisi putaran 27 apa adanya. Bukan angka kedua: totalnya = buku/isi wadah.
 */
export function wbKomposisiTurunan(W, s) {
  const K = wbKomposisi(W, s); const bw = petaBukuWadah(); const asal = (m) => wbMerkAsal(m, bw); const T = {}; let terakhir = null; const semua = ambilWadahLiteran();
  const tambah = (m, n) => { if (m && n > 0) T[m] = wbB3((T[m] || 0) + n); };
  if (K.stokSendiri) {
    const tanda = wbTanda(W); const base = tanda && tanda.komposisi && typeof tanda.komposisi === 'object' && !Array.isArray(tanda.komposisi) ? tanda.komposisi : null;
    if (base) Object.keys(base).forEach((m) => tambah(asal(m), Number(base[m]) || 0));
    semua.forEach((t) => { if (t.tipe !== 'takar' || t.wadah !== W || (tanda && !wdSesudah(t, tanda))) return; if (!terakhir || wdSesudah(t, terakhir)) terakhir = t;
      (t.sumber || []).forEach((x) => tambah(x.merkAsal ? String(x.merkAsal) : asal(String(x.merk || '')), Number(x.kg) || 0)); });
  } else {
    K.positif.forEach((x) => tambah(asal(x.merk), x.kg));
    semua.forEach((t) => { if (t.tipe === 'takar' && t.wadah === W && (!terakhir || wdSesudah(t, terakhir))) terakhir = t; });
  }
  const tot = Object.keys(T).reduce((a, m) => a + T[m], 0); const isi = Math.max(0, K.totalKg);
  const daftar = Object.keys(T).filter((m) => T[m] > 0).sort((a, b) => T[b] - T[a] || a.localeCompare(b)).map((m) => ({ merk: m, kg: tot > 0 ? wbB2(isi * T[m] / tot) : 0, porsi: tot > 0 ? T[m] / tot : 0 }));
  let banding = ''; if (daftar.length > 1) { const min = Math.min(...daftar.map((x) => x.porsi)); const r = daftar.map((x) => x.porsi / min);
    let k = 0; for (let c = 1; c <= 9 && !k; c++) { const v = r.map((x) => x * c); if (v.every((x) => Math.abs(x - Math.round(x)) < 0.15 && Math.round(x) <= 9)) k = c; }   // pengali terkecil yang membulatkan semua (1,5 : 1 → 3 : 2)
    banding = k ? daftar.map((x, i) => x.merk + ' ' + Math.round(r[i] * k)).join(' : ') : daftar.map((x) => x.merk + ' ' + Math.round(x.porsi * 100) + ' %').join(' : '); }
  const tk = terakhir ? { tanggal: String(terakhir.tanggal || ''), jam: String(terakhir.jam || ''), oleh: String(terakhir.oleh || terakhir.diubahOleh || ''), kg: wbB2(Number(terakhir.kg) || 0), takaran: String(terakhir.takaran || '') } : null;
  const nama = daftar.length ? (banding || daftar[0].merk) : (K.diketahui ? 'belum ada isi ulang tercatat' : 'isi belum ditandai');
  return { wadah: W, stokSendiri: !!K.stokSendiri, diketahui: K.diketahui, totalKg: wbB2(K.totalKg), liter: Math.round(Math.max(0, K.totalKg) / wbRasio(W) * 10) / 10, daftar, banding, terakhir: tk, nama,
    teks: nama + (K.diketahui ? ' · ±' + wbKG(Math.max(0, K.totalKg)) + ' ≈ ' + String(Math.round(Math.max(0, K.totalKg) / wbRasio(W) * 10) / 10).replace('.', ',') + ' L' : '') + (tk ? ' · diisi ' + tk.jam + (tk.oleh ? ' oleh ' + tk.oleh : '') : '') };
}

/**
 * Komposisi turunan W SEKARANG sebagai { merek asal: kg } untuk isi `isiKg` (bawaan: isi wadah sekarang), Σ persis — dibawa titik samakan baru (ganti nama,
 * cocokkan wadah) supaya riwayat isi ulang tidak terputus (39b no. 6 / 16: dulu titik baru tanpa komposisi → "belum ada isi ulang", lalu 100 % merek terakhir).
 */
export function wbKomposisiTurunanKg(W, isiKg, s) {
  const T = wbKomposisiTurunan(W, s); const isi = wbB2(Math.max(0, isiKg === undefined || isiKg === null ? T.totalKg : Number(isiKg) || 0)); const out = {}; let jalan = 0;
  T.daftar.forEach((x, i) => { const k = i === T.daftar.length - 1 ? wbB2(isi - jalan) : wbB2(isi * x.porsi); jalan = wbB2(jalan + k); if (k > 0) out[x.merk] = k; });
  return out;
}

/**
 * Pindah buku bertanda "tandai untuk dicocokkan" (owner 29 Sep d) yang belum tuntas, per merek asal — tuntas = cocokkan merek itu (penyesuaianStok bukan rework)
 * bertanggal ≥ dokumennya (pola 31b). Digabung notaTembusBelumCocok (jual-logika.js) supaya pita Jual & kartu keempat Gudang membacanya.
 */
export function wbPindahTembusBelumCocok() {
  const PS = ambilPenyesuaianStok().filter((q) => !q.dariRework); const out = [];
  ambilProduksiBerlaku().forEach((p) => { if (!p.perluCocokkan || !p.dariTakar) return; const tgl = String(p.tanggal || '');
    const per = p.selisihPerMerk && typeof p.selisihPerMerk === 'object' && !Array.isArray(p.selisihPerMerk) ? p.selisihPerMerk : null;
    const daftar = per ? Object.keys(per).map((m) => ({ merk: m, kg: Number(per[m]) || 0 })) : [{ merk: String(((p.sumberList || [])[0] || {}).merk || p.merkSumber || ''), kg: Number(p.selisihKg) || 0 }];
    daftar.forEach((x) => { if (!x.merk || !(x.kg > 0)) return; if (PS.some((q) => String(q.merk) === x.merk && String(q.tanggal || '') >= tgl)) return;
      out.push({ id: p.id, trxId: '', tanggal: tgl, jam: String(p.jam || ''), nama: x.merk, jenis: 'takar', selisihKg: wbB2(x.kg), namaPelanggan: '', wadah: String(p.bukaKarung || p.pindahAwalWadah || ''), oleh: String(p.oleh || p.diubahOleh || '') }); }); });
  return out;
}

/** CEK WADAH tutup toko hari `iso` (owner 29 Sep e): per wadah — sudah dicek atau belum, hasilnya, jam, siapa. */
export function wbCekHari(iso) {
  // audit 39b no. 1: cek tutup toko milik HARI DAGANG yang sedang ditutup — ditulis sebelum jam 12 siang = cek hari kemarin (aturan tanggalTutupAktif), satu hari saja
  const A = aturWadah(); const peta = petaStokWadah(); const semua = ambilWadahLiteran();
  const hariCek = (d) => { if (String(d.jam || '') >= '12:00' || !d.jam) return String(d.tanggal || ''); const t = new Date(String(d.tanggal) + 'T12:00:00'); t.setDate(t.getDate() - 1); return t.getFullYear() + '-' + String(t.getMonth() + 1).padStart(2, '0') + '-' + String(t.getDate()).padStart(2, '0'); };
  const daftar = A.daftar.map((W, i) => { const aktif = wbAktif(W, peta); const c = wdTerbaru(semua.filter((d) => d.tipe === 'cek' && d.wadah === W && hariCek(d) === iso)); const K = wbKomposisi(W);
    return { no: 'W' + (i + 1), W, aktif, diketahui: K.diketahui, bukuKg: wbB2(K.totalKg), dicek: !!c, hasil: c ? String(c.hasil || '') : '', hasilTeks: c ? (WB_CEK.find((x) => x[0] === c.hasil) || ['', ''])[1] : '', jam: c ? String(c.jam || '') : '', oleh: c ? String(c.oleh || c.diubahOleh || '') : '', bukuSaatCek: c ? wbB2(Number(c.bukuKg) || 0) : null }; });
  return { iso, daftar, nAktif: daftar.filter((x) => x.aktif).length, nDicek: daftar.filter((x) => x.dicek).length, belum: daftar.filter((x) => x.aktif && !x.dicek).map((x) => x.W) };
}
/** CATAT cek satu wadah: sesuai (buku = kotak) · lupa (isi ulang belum dicatat — catat sesudah ini) · kosong (seluruh isi disisihkan ke karung wadah tanpa timbang). */
export function wbSusunCek(W, hasil, w) {
  const A = aturWadah(); if (A.daftar.indexOf(W) < 0) return { tolak: W + ' bukan wadah' };
  const h = String(hasil || ''); if (!WB_CEK.some((x) => x[0] === h)) return { tolak: 'Pilih hasil ceknya: sesuai · lupa isi ulang · dikosongkan' };
  const K = wbKomposisi(W); const aktif = wbAktif(W); const dokumen = []; let sisih = 0;
  if (h === 'kosong') { if (!aktif) return { tolak: 'Wadah ' + W + ' belum punya buku sendiri — "dikosongkan" baru bisa dicatat sesudah wadahnya aktif (Stok › Wadah literan)' };
    if (K.totalKg > 0.004) { const r = wbSusunSisih(W, String(wbB2(K.totalKg)), w); if (r.tolak) return r; r.dokumen.forEach((d) => dokumen.push(d)); sisih = wbB2(K.totalKg); } }
  dokumen.push({ koleksi: 'wadahLiteran', data: Object.assign({ id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, tipe: 'cek', wadah: W, hasil: h, bukuKg: wbB2(K.totalKg) }, aktif ? { stokWadah: wbKunci(W) } : {}) });
  return { dokumen, hasil: h, sisihKg: sisih, patch: { kabar: 'Cek wadah ' + W + ' ' + w.jam + ': ' + (h === 'sesuai' ? 'sesuai — isi kotak = buku ±' + wbKG(K.totalKg) : h === 'lupa' ? 'lupa isi ulang — catat isi ulangnya sekarang (tiga ketukan), supaya buku ikut naik' : 'dikosongkan — ' + (sisih ? wbKG(sisih) + ' disisihkan ke karung wadahnya tanpa timbang, kotak jadi 0' : 'menurut buku kotaknya memang sudah kosong')), kabarAwas: h !== 'sesuai' } };
}

/**
 * DUA ANGKA SATU KOTAK yang masih bisa berbeda (owner 29 Sep f) — disebut selisihnya, tidak dibiarkan berdampingan diam-diam.
 * Wadah belum aktif: "bebas dijual" (langit-langit BUKU merek asal, bebasLiter dari rak) vs isi tercatat kotak (alat ukur). Wadah aktif: tiap karung
 * belakang — catatan kolam vs buku.
 */
export function wbSelisihWadah(W, s, bebasLiter) {
  const K = wbKomposisi(W, s); const tw = tinggiWadah(W, s || null); const out = []; if (!tw) return { ada: false, baris: [], teks: '' };
  if (!K.stokSendiri) {
    if (tw.diketahui && bebasLiter !== undefined && bebasLiter !== null) { const bebasKg = wbB2(Number(bebasLiter) * wbRasio(W)); const sel = wbB2(tw.sisaNyataKg - bebasKg);
      if (Math.abs(sel) > 0.05) { const stok = ingatStokKarung(); const pembatas = K.positif.map((x) => 'buku ' + x.merk + ' ' + wbKG((stok[x.merk] || {}).sisaKg || 0)).join(', ') || 'buku ' + wbMerkCadangan(W);
        out.push({ jenis: 'buku-merek', selisihKg: sel, teks: 'bebas dijual ' + String(Number(bebasLiter)).replace('.', ',') + ' L (' + pembatas + ') ≠ isi kotak ±' + wbKG(tw.sisaNyataKg) + ' — selisih ' + wbKG(Math.abs(sel)) + (sel > 0 ? ' lebih di kotak' : ' lebih di buku') + ' → aktifkan buku wadah (Stok › Wadah literan)' }); } }
  } else {
    // tinjauan K4: karung yang sudah dikembalikan tidak disuruh ditimbang; sisa pengembalian lama → kartu "Buku karung yang tertinggal"; selisih biasa → samakan
    const KT = wbKarungTertinggal(); const tutup = {}; const diri = {}; KT.tertutup.forEach((x) => { tutup[x.kunci] = 1; }); KT.berdiri.forEach((x) => { diri[x.kunci] = 1; });
    wbKarungBelakangWadah(W).forEach((KB) => { if (!KB.diketahui || Math.abs(KB.selisihKg) <= 0.05) return;
      const teks = tutup[KB.kunci] ? 'karung ' + KB.merk + ' sudah dikembalikan ke tumpukan, bukunya masih ' + wbKG(KB.bukuKg) + ' — pindah balik (Stok › Wadah literan › Buku karung yang tertinggal)'
        : 'karung ' + KB.merk + ' di belakang: catatan ±' + wbKG(KB.kolamKg) + ' vs buku ' + wbKG(KB.bukuKg) + ' — selisih ' + wbKG(Math.abs(KB.selisihKg)) + (diri[KB.kunci] ? ', sisa pengembalian lama — pindah balik dulu (Stok › Wadah literan › Buku karung yang tertinggal)' : ', timbang karungnya (Stok › Cocokkan › Wadah literan)');
      out.push({ jenis: 'karung-belakang', merk: KB.merk, selisihKg: KB.selisihKg, teks }); });
  }
  return { ada: out.length > 0, baris: out, teks: out.map((x) => x.teks).join(' · ') };
}

// ---------- 39b no. 5 · keputusan owner 1 Okt: buku karung belakang yang TERTINGGAL sesudah dikembalikan dengan kode lama ----------
const WB_TAMBALAN_KEMBALI = '2026-10-01';   // no. 5 tayang: sejak tanggal ini pengembalian karung memindah bukunya sendiri di kiriman yang sama
/**
 * Sisa pengembalian lama satu buku karung belakang = FAKTA dokumen: pengembalian sebelum tambalan (karungIsi dikembalikan, sisaSebelumKg > 0) yang di
 * kiriman yang sama (tanggal + jam + tempat) tidak disertai pindah buku balik sebesar sisanya, dikurangi pembetulan (betulkanTertinggal) yang sudah ditulis.
 * 0 = tidak ada sisa lama: selisih buku − catatan dari "samakan sisa" biasa BUKAN sisa lama (tinjauan L2) — itu urusan Cocokkan.
 */
function wbSisaKembaliLama(kunci, prod) {
  // pemeriksa d2f3a29 T3: karung itu sudah DITUTUP lagi dengan kode baru (dikembalikan / dihapus habis sejak tambalan) → kode baru memindah / membukukan
  // SELURUH bukunya saat itu, sisa lama ikut habis — tidak dihitung lagi (dulu terpindah dua kali)
  if (ambilWadahLiteran().some((r) => r.tipe === 'karungIsi' && r.merk === kunci && (r.dikembalikan || r.selesai) && String(r.tanggal || '') >= WB_TAMBALAN_KEMBALI)) return 0;
  const dari = (p) => (p.sumberList || []).reduce((a, x) => a + (x.merk === kunci ? Number(x.kg) || 0 : 0), 0);
  const balik = prod.filter((p) => p && p.kembaliTumpukan !== undefined && p.kembaliTumpukan !== null); let lama = 0;
  ambilWadahLiteran().forEach((r) => { if (r.tipe !== 'karungIsi' || r.merk !== kunci || !r.dikembalikan || !(Number(r.sisaSebelumKg) > 0)) return;   // yang sesudah tambalan sudah membuat fungsi ini 0 (di atas)
    const ikut = balik.filter((p) => !p.betulkanTertinggal && p.kembaliTumpukan === r.wadah && p.tanggal === r.tanggal && p.jam === r.jam).reduce((a, p) => a + dari(p), 0);
    lama += Math.max(0, Number(r.sisaSebelumKg) - ikut); });
  return wbB2(Math.max(0, lama - balik.filter((p) => p.betulkanTertinggal).reduce((a, p) => a + dari(p), 0)));
}
/**
 * Buku 'Karung belakang W · M' yang masih memuat sisa pengembalian lama (30 Sep, sebelum tambalan no. 5: kode lama tidak memindah bukunya balik).
 * Keputusan owner 1 Okt: SEMUA dipindah balik (berasnya sudah di tumpukan gudang — terbukti dari dokumen pengembaliannya). Hanya yang sisanya MASIH UTUH:
 *   tertutup = karungnya sudah tidak di belakang wadah dan bukunya persis sisa lama → seluruh buku pindah balik;
 *   berdiri  = karungnya masih berdiri, catatannya tidak minus, dan buku − catatan ≥ sisa lama (belum termakan isi ulang) → sisa lama pindah balik,
 *              buku karung jadi = catatannya. Timbang karungnya sesudah itu lewat Cocokkan biasa (tinjauan putaran 2: alur timbang khusus dibuang).
 * Yang tidak utuh lagi (sudah dikembalikan dengan kode baru, termakan isi ulang, dsb.) TIDAK disentuh — urusan Cocokkan.
 */
export function wbKarungTertinggal() {
  const bw = petaBukuWadah(); const stok = ingatStokKarung(); const kolam = semuaKarungTerbuka(); const prod = ambilProduksiBerlaku(); const tertutup = []; const berdiri = [];
  Object.keys(bw).sort().forEach((k) => { const b = bw[k]; if (b.jenis !== 'belakang' || !b.merk || !stok[k]) return; const buku = wbB2(stok[k].sisaKg || 0); if (buku <= 0.004) return;
    const lama = wbSisaKembaliLama(k, prod); if (lama <= 0.05) return;
    const di = kolam.filter((x) => x.merk === k); const hidup = di.filter((x) => !kolamDitutup(k, x.lokasi));
    // pemeriksa d2f3a29 T1: karungnya sudah tidak ada → buku yang tersisa (≤ sisa lama; mis. sesudah isi ulang dari buku itu) SELURUHNYA dari pengembalian itu
    if (!hidup.length) { if (di.length && buku <= lama + 0.05) tertutup.push({ kunci: k, merk: b.merk, wadah: b.wadah, bukuKg: buku, lamaKg: lama, pindahKg: buku }); return; }
    // pemeriksa d2f3a29 T2: yang dipindah = sisa lama, paling banyak buku − catatan (catatan yang naik sedikit tidak membuang sisa lama); catatan minus = tidak utuh
    if (hidup.length !== 1) return; const cat = wbB2(hidup[0].sisaMentahKg || 0); const r = wbB2(Math.min(lama, buku - cat));
    if (cat >= 0 && r > 0.05) berdiri.push({ kunci: k, merk: b.merk, wadah: b.wadah, lokasi: hidup[0].lokasi, bukuKg: buku, catatanKg: cat, lamaKg: lama, pindahKg: r }); });
  const semua = tertutup.concat(berdiri);
  return { tertutup, berdiri, semua, kgTertutup: wbB2(tertutup.reduce((a, x) => a + x.pindahKg, 0)), kgSemua: wbB2(semua.reduce((a, x) => a + x.pindahKg, 0)) };
}
const wbDiMana = (x) => (x.lokasi === '' ? '(karung lepas)' : 'di belakang ' + (x.lokasi || x.wadah));
/** Pindah balik sisa pengembalian lama SEMUA karung di daftar ke buku merek asalnya (modal ikut; laba tidak berubah). Satu kiriman. */
export function wbSusunPindahTertinggal(w) {
  const T = wbKarungTertinggal(); if (!T.semua.length) return { tolak: 'Tidak ada buku karung yang tertinggal' };
  const dokumen = [];
  T.semua.forEach((x) => { const ket = 'Betulkan buku karung tertinggal: karung ' + x.merk + ' ' + wbDiMana(x) + ' — sisa pengembalian lama (sebelum tambalan 1 Okt) ' + wbKG(x.pindahKg) + ' → ' + x.merk;
    dokumen.push(denganCacheSementara(dokumen, () => wbDokPindah([{ merk: x.kunci, kg: x.pindahKg }], x.merk, w, { kembaliTumpukan: x.lokasi === undefined ? x.wadah : x.lokasi, betulkanTertinggal: true, keterangan: ket }))); });
  return { dokumen, patch: { ttgYakin: false, kabar: 'Sisa pengembalian lama dipindah balik ke mereknya: ' + T.semua.map((x) => x.merk + ' ' + wbKG(x.pindahKg)).join(', ') + ' (total ' + wbKG(T.kgSemua) + '). Buku tumpukan merek-merek itu naik sebesar itu; laba tidak berubah (pindah buku, modal ikut).'
    + (T.berdiri.length ? ' Karung yang masih berdiri: sisa lamanya sudah keluar dari bukunya; kalau mau ditimbang, pakai Stok › Cocokkan.' : ''), kabarAwas: false } };
}

// ---------- KARUNG BEKAS LAHIR DARI KARUNG HABIS (owner 7 Okt 2026) ----------
// Owner 7 Okt: "karung yang ada di belakang wadah literan ketika habis 0 kg jadi karung bekas, dan stok karung bekas bertambah." Keputusan owner 15 Sep:
// karung bekas tidak pernah dibeli — ia lahir dari karung yang dituang habis; bukunya DUA SISI (lahir dikreditkan, dipakai dibebankan).
//   · Satu karung = satu catatan 'karung' (buka karung) di kolam nama × tempat di belakang wadah; kolam lama tanpa catatan buka dikenali dari catatan isinya
//     yang pertama. Karung yang masih BERDIRI = karung terbaru di kolam itu sebanyak ⌈(sisa − 0,5 kg) ÷ berat karung⌉ (yang lebih tua dituang habis lebih
//     dulu); sisa ≤ 0,5 kg = HABIS (batas yang sama dengan deretan & "hapus karung habis"), karung terbarunya masih tegak sebagai karung kosong.
//   · Tiap kiriman yang menyentuh kolam di belakang wadah (isi ulang tiga ketukan, − / + takar, hapus karung habis, samakan, cocokkan wadah, kembalikan)
//     dibandingkan sebelum ⇄ sesudah pada himpunan karung yang SAMA — semua karung kolam itu sejak terakhir ditutup + yang dibuka di kiriman ini:
//       LAHIR = berdiri sebelumnya (atau dibuka di kiriman ini) ∧ tidak berdiri sesudahnya ∧ belum jadi karung bekas;
//       BATAL = sudah jadi karung bekas ∧ berdiri lagi sesudahnya (samakan / cocokkan menemukan isinya — juga karung yang lebih tua dari yang berdiri
//               sebelumnya), atau berdiri sebelumnya lalu dikembalikan ke tumpukan.
//   · Sekali saja: tiap kelahiran membawa `karungId` (id catatan buka karungnya). Urutan peristiwa per karung — dokumen kelahiran, catatan pembalik, tanda
//     titipan — menurut waktu (wdSesudah); peristiwa terakhir 'lahir' = karung itu sudah karung bekas.
//   · Dokumen kelahiran = stokBahanLiteran tipe 'opname' jumlah +1 jenis 'karungbekas' bertanda `lahirKarungBekas` — jalur mesin beku untuk lembar GRATIS
//     (menggeser sisa, tidak ikut membagi harga rata-rata; lihat hitungStokBahanLiteran). nilaiRp = harga per lembar karung bekas DI BUKU mesin (= yang dipakai
//     neraca dan HPP saat lembarnya dipakai): neraca naik = laba naik lewat baris "Susut & selisih stok" (sisi kredit keputusan 15 Sep). Harga buku itu = NILAI
//     KARUNG BEKAS setelan owner (wbKbNilai; bawaan = keputusan owner 15 Sep) begitu owner menerapkannya ke buku (wbSusunNilaiKarungBekas). Memasang setelan di
//     nilaiRp tanpa buku mesin ikut bergerak membuat neraca ≠ laba — jadi sebelum diterapkan kabarnya menyebut selisih itu terang.
//   · BATAL tidak pernah mengubah catatan bulan lampau: dokumen kelahiran bertanggal HARI INI yang nilainya masih = harga buku → dihapus di kiriman yang sama;
//     selain itu CATATAN PEMBALIK bertanggal hari ini (opname −1 bertanda `lahirKarungBekas` + `batal`, nilaiRp −harga buku) — kelahirannya tetap di tanggalnya,
//     laba bulan lalu tidak bergeser surut, bulan terkunci tidak tersentuh (kiriman tidak pernah ditolak kunci periode karena karung bekas).
//   · Akun bukan-owner belum boleh menulis stokBahanLiteran selain 'pakai' (rules v5) → kelahiran / pembatalan DITITIP sebagai tanda `karungBekas` di catatan
//     wadahLiteran kiriman itu sendiri; owner mencatatnya sekali ketuk (wbSusunKarungBekasTunda).
export const WB_KB_HABIS_KG = 0.5;
export const WB_KB_JENIS = 'karungbekas';
export const WB_KB_NILAI_BAWAAN = 1500;     // keputusan owner 15 Sep 2026: satu lembar karung bekas dihargai Rp1.500 — angka kebijakan, diubah owner di Stok › Wadah literan
export const WB_KB_NILAI_MAKS = 100000;
/** Nilai karung bekas: setelan owner (aturanToko/karungBekas.nilaiLembar; belum diatur → bawaan keputusan 15 Sep) ⇄ harga per lembar di buku mesin. */
export function wbKbNilai() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'karungBekas') || null; const n = a ? Math.round(Number(a.nilaiLembar)) : NaN; const diatur = isFinite(n) && n > 0;
  const st = hitungStokBahanLiteran()[WB_KB_JENIS] || {}; const buku = Math.round(Number(st.hargaPerPcs) || 0); const setelan = diatur ? n : WB_KB_NILAI_BAWAAN;
  return { setelan, diatur, buku, selaras: buku === setelan, sisa: Math.round(Number(st.sisaPcs) || 0), totalBeli: Number(st.totalBeli) || 0, totalHargaBeli: Number(st.totalHargaBeli) || 0, dok: a };
}
/** Kalimat nilai di kabar kelahiran / pembatalan: harga buku, dan bila belum = setelan owner, selisihnya disebut (tidak ada status yang berbohong soal uang). */
const wbKbKataNilai = (N) => (N.buku > 0 ? ', dinilai ' + RP(N.buku) + '/lembar' + (N.selaras ? ' (setelan owner)' : ' = harga buku karung bekas; setelan owner ' + RP(N.setelan) + ' belum diterapkan ke buku — Stok › Wadah literan') + '; ikut laba sebagai selisih stok'
  : ', harga buku karung bekas Rp0 — setelan owner ' + RP(N.setelan) + ' belum diterapkan ke buku (Stok › Wadah literan)');
/** Peristiwa karung bekas per karungId, lama → baru. → { akhir 'lahir' | 'batal', lahir: dokumen kelahiran yang BERLAKU di buku | null, tanda: tanda titipan terakhir | null }. */
function wbKbPeristiwa() {
  const ev = {}; const tambah = (id, e) => { (ev[id] = ev[id] || []).push(e); };
  ambilBahanLiteran().forEach((d) => { if (!d.lahirKarungBekas || d.karungId === undefined || d.karungId === null) return; tambah(String(d.karungId), { aksi: d.batal ? 'batal' : 'lahir', d, pada: d }); });
  ambilWadahLiteran().forEach((d) => (Array.isArray(d.karungBekas) ? d.karungBekas : []).forEach((t) => { if (!t || t.karungId === undefined || t.karungId === null) return;
    tambah(String(t.karungId), { aksi: t.aksi === 'batal' ? 'batal' : 'lahir', tanda: Object.assign({ dariId: d.id, tanggalAsal: d.tanggal || '', jamAsal: d.jam || '', olehAsal: d.oleh || '' }, t), pada: d }); }));
  const peta = {};
  Object.keys(ev).forEach((id) => { const E = ev[id].slice().sort((a, b) => (wdSesudah(a.pada, b.pada) ? 1 : wdSesudah(b.pada, a.pada) ? -1 : 0));
    const buku = E.filter((e) => e.d); const bAkhir = buku.length ? buku[buku.length - 1] : null; const tanda = E.filter((e) => e.tanda);
    peta[id] = { akhir: E[E.length - 1].aksi, lahir: bAkhir && bAkhir.aksi === 'lahir' ? bAkhir.d : null, tanda: tanda.length ? tanda[tanda.length - 1].tanda : null }; });
  return peta;
}
/** Karung di kolam (nama × tempat) sejak kolam itu terakhir ditutup — urut lama → baru. Kolam lama tanpa catatan buka: catatan isi pertamanya mewakili karungnya. */
function wbKbSegmen(merk, L, daftar, semua) {
  const di = semua.filter((d) => (d.tipe === 'karung' || d.tipe === 'karungIsi') && String(d.merk) === merk && wdLokasiDoc(d, daftar) === L).sort((a, b) => (wdSesudah(a, b) ? 1 : wdSesudah(b, a) ? -1 : 0));
  let mulai = 0; di.forEach((d, i) => { if (d.tipe === 'karungIsi' && !(Number(d.isiKg) > 0) && (d.dikembalikan || d.selesai || d.pindahAwal)) mulai = i + 1; });
  const seg = di.slice(mulai); const i0 = seg.findIndex((d) => d.tipe === 'karungIsi' && Number(d.isiKg) > 0); const k0 = seg.findIndex((d) => d.tipe === 'karung');
  return (i0 >= 0 && (k0 < 0 || i0 < k0) ? [seg[i0]] : []).concat(seg.filter((d) => d.tipe === 'karung'));
}
/**
 * Pembatalan satu kelahiran yang BERLAKU di buku (owner): dokumen kelahiran hari ini yang nilainya masih = harga buku → { hapus }; selain itu → { dokumen }
 * catatan pembalik bertanggal hari ini (opname −1, nilaiRp −harga buku). Tidak pernah menyentuh catatan bulan lampau.
 */
function wbKbCabut(x, lahirDok, w, sisa, harga, dariId) {
  if (String(lahirDok.tanggal || '') === String(w.tanggal) && Math.round(Number(lahirDok.nilaiRp) || 0) === harga && !tolakKunci('stokBahanLiteran', lahirDok)) return { hapus: { koleksi: 'stokBahanLiteran', id: lahirDok.id } };
  return { dokumen: { koleksi: 'stokBahanLiteran', data: { id: w.idUnik(), tipe: 'opname', jenis: WB_KB_JENIS, jumlah: -1, hargaTotal: 0, tanggal: w.tanggal, jam: w.jam, pcsSistem: sisa, pcsFisik: sisa - 1,
    catatan: 'Karung ' + (x.merkAsal || x.merk) + ' di belakang wadah ' + x.wadah + ' ' + (x.kembali ? 'dikembalikan ke tumpukan' : 'ternyata belum habis') + ' → karung bekas yang tercatat ' + (lahirDok.tanggal ? tanggalPendek(lahirDok.tanggal) : 'dulu') + ' dicabut (catatan pembalik hari ini)',
    nilaiRp: harga ? -harga : 0, hargaPerPcsSaatOpname: harga, lahirKarungBekas: true, batal: true, karungId: String(x.karungId), lahirId: lahirDok.id, kolam: x.merk, wadah: x.wadah, merkAsal: x.merkAsal || x.merk, ukuranKg: x.ukuranKg, dariId } } };
}
/**
 * Karung bekas yang LAHIR / DIBATALKAN oleh satu kiriman (dokumen = [{ koleksi, data }] yang akan ditulis). opsi.staf = akun bukan-owner (tanda titipan).
 * → { dokumen (kelahiran & catatan pembalik owner), hapus (kelahiran hari ini yang dicabut, owner), lahir [], batal [], kabar }. Tanda titipan ditulis ke catatan
 * wadahLiteran kiriman itu sendiri.
 */
export function wbKarungBekasKiriman(dokumen, w, opsi) {
  const O = opsi || {}; const daftar = aturWadah().daftar; const semua = ambilWadahLiteran();
  // buku khusus yang LAHIR di kiriman ini juga (karung belakang pertama di wadah itu) — dibaca seolah kirimannya sudah tertulis
  const bw = denganCacheSementara(dokumen || [], () => petaBukuWadah());
  const baru = (dokumen || []).filter((x) => x && x.koleksi === 'wadahLiteran' && x.data).map((x) => x.data);
  const kosong = { dokumen: [], hapus: [], lahir: [], batal: [], kabar: '' }; if (!baru.length) return kosong;
  const kolam = {}; const tambah = (m, L) => { const M = String(m || ''); const T = String(L || ''); if (!M || !T) return; const b = bw[M]; if (b && (b.jenis === 'wadah' || b.jenis === 'karung')) return; kolam[M + '|#|' + T] = { merk: M, L: T }; };
  baru.forEach((d) => { if (d.tipe === 'karung' || d.tipe === 'karungIsi') tambah(d.merk, wdLokasiDoc(d, daftar)); else if (d.tipe === 'takar') (d.sumber || []).forEach((x) => tambah(x.merk, wdLokasiSumber(x, daftar))); });
  const P = wbKbPeristiwa(); const sudah = (id) => !!P[id] && P[id].akhir === 'lahir'; const lahir = []; const batal = [];
  Object.keys(kolam).sort().forEach((kk) => { const { merk, L } = kolam[kk]; const diSini = (d) => String(d.merk) === merk && wdLokasiDoc(d, daftar) === L;
    // aktivasi: karung yang sama pindah kolam (buku), tidak habis
    if (baru.some((d) => d.tipe === 'karungIsi' && diSini(d) && d.pindahAwal)) return;
    const kembali = baru.some((d) => d.tipe === 'karungIsi' && diSini(d) && d.dikembalikan);
    const berat = beratKarungBuka(merk) || 50; const nKarung = (kg) => (kg > WB_KB_HABIS_KG ? Math.ceil((kg - WB_KB_HABIS_KG) / berat - 1e-9) : 0);
    const sebelum = karungBelakang(merk, L); const sesudah = denganCacheSementara(dokumen, () => karungBelakang(merk, L));
    const C0 = wbKbSegmen(merk, L, daftar, semua); const pre = sebelum.diketahui ? sebelum.sisaMentahKg : 0;
    const n0 = pre > WB_KB_HABIS_KG ? Math.min(C0.length, nKarung(pre)) : (C0.length ? 1 : 0);
    const dibuka = baru.filter((d) => d.tipe === 'karung' && diSini(d));
    const S = C0.concat(dibuka);                                   // semua karung kolam ini (lama → baru) — himpunan yang SAMA untuk sebelum & sesudah
    const calon = C0.slice(C0.length - n0).concat(dibuka);         // berdiri SEBELUM kiriman, atau dibuka di kiriman ini
    const nPost = kembali ? 0 : Math.min(S.length, nKarung(sesudah.diketahui ? sesudah.sisaMentahKg : 0));
    const berdiri = {}; S.slice(S.length - nPost).forEach((k) => { berdiri[String(k.id)] = k; });   // berdiri SESUDAH kiriman
    const asal = wbMerkAsal(merk, bw); const isi = (k) => ({ karungId: String(k.id), merk, wadah: L, merkAsal: asal, ukuranKg: k.tipe === 'karung' ? (Number(k.kg) || berat) : berat });
    const dicatat = {};
    calon.forEach((k) => { const id = String(k.id); if (kembali || berdiri[id] || sudah(id) || dicatat[id]) return; dicatat[id] = 1; lahir.push(Object.assign(isi(k), { punyaDok: !!(P[id] && P[id].lahir) })); });
    (kembali ? calon : S.filter((k) => berdiri[String(k.id)])).forEach((k) => { const id = String(k.id); if (!sudah(id) || dicatat[id]) return; dicatat[id] = 1; batal.push(Object.assign(isi(k), { dok: P[id].lahir, kembali })); }); });
  if (!lahir.length && !batal.length) return kosong;
  const host = baru.find((d) => d.tipe === 'takar') || baru[0]; const tanda = []; const out = { dokumen: [], hapus: [], lahir, batal, kabar: '' };
  const nama = (d) => d.map((x) => x.merkAsal + ' (' + x.wadah + ')').join(', ');
  const tandaDari = (x, aksi) => ({ aksi, karungId: x.karungId, merk: x.merk, wadah: x.wadah, merkAsal: x.merkAsal, ukuranKg: x.ukuranKg });
  const kataBatal = batal.length ? ' · karung ' + nama(batal) + ' ' + (batal[0].kembali ? 'dikembalikan ke tumpukan' : 'ternyata belum habis') : '';
  if (O.staf) {
    lahir.forEach((x) => tanda.push(tandaDari(x, 'lahir'))); batal.forEach((x) => tanda.push(tandaDari(x, 'batal')));
    out.kabar = (lahir.length ? ' · karung ' + nama(lahir) + ' habis → ' + lahir.length + ' karung bekas MENUNGGU owner mencatatnya ke buku (Stok › Wadah literan)' : '') + (batal.length ? kataBatal + ' → catatan karung bekasnya menunggu owner dicabut' : '');
  } else {
    const N = wbKbNilai(); const harga = N.buku; const s0 = N.sisa; let sisa = s0; let nPembalik = 0;
    lahir.forEach((x) => {
      // dokumen kelahirannya masih berlaku (pembatalan titipan belum dicatat owner) → cukup tanda, tidak dobel
      if (x.punyaDok) { tanda.push(tandaDari(x, 'lahir')); return; }
      out.dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: w.idUnik(), tipe: 'opname', jenis: WB_KB_JENIS, jumlah: 1, hargaTotal: 0, tanggal: w.tanggal, jam: w.jam, pcsSistem: sisa, pcsFisik: sisa + 1,
        catatan: 'Karung ' + x.merkAsal + ' di belakang wadah ' + x.wadah + ' habis → jadi karung bekas', nilaiRp: harga, hargaPerPcsSaatOpname: harga, lahirKarungBekas: true, karungId: x.karungId, kolam: x.merk, wadah: x.wadah,
        merkAsal: x.merkAsal, ukuranKg: x.ukuranKg, dariId: host.id } }); sisa += 1; });
    batal.forEach((x) => { if (x.dok) { const c = wbKbCabut(x, x.dok, w, sisa, harga, host.id); if (c.hapus) out.hapus.push(c.hapus); else { out.dokumen.push(c.dokumen); nPembalik += 1; } sisa -= 1; } tanda.push(tandaDari(x, 'batal')); });
    out.kabar = (lahir.length ? ' · karung ' + nama(lahir) + ' habis → +' + lahir.length + ' karung bekas' : '') + (batal.length ? kataBatal + ' → catatan karung bekasnya dicabut' + (nPembalik ? ' (catatan pembalik bertanggal hari ini — kelahirannya tetap di tanggalnya)' : '') : '')
      + (sisa !== s0 || out.hapus.length || nPembalik ? ' (buku karung bekas ' + s0 + ' → ' + sisa + ' lembar' + wbKbKataNilai(N) + ')' : '');
  }
  if (tanda.length) host.karungBekas = (Array.isArray(host.karungBekas) ? host.karungBekas : []).concat(tanda);
  return out;
}
/** Sertakan kelahiran / pembatalan karung bekas ke hasil susun* jalur karung di belakang wadah (r.dokumen, r.hapus + r.jejakHapus, kalimat kabar). r dikembalikan. */
export function wbSertakanKarungBekas(r, w, opsi) {
  if (!r || r.tolak || !Array.isArray(r.dokumen) || !r.dokumen.length) return r;
  const K = wbKarungBekasKiriman(r.dokumen, w, opsi); if (!K.lahir.length && !K.batal.length) return r;
  K.dokumen.forEach((d) => r.dokumen.push(d));
  if (K.hapus.length) { r.hapus = (r.hapus || []).concat(K.hapus); r.jejakHapus = (r.jejakHapus ? r.jejakHapus + ' · ' : '') + 'karung bekas dicabut (kelahiran hari ini): ' + K.batal.filter((x) => x.dok).map((x) => x.merkAsal + ' ' + x.wadah).join(', '); }
  r.karungBekas = { lahir: K.lahir.length, batal: K.batal.length, titip: !!(opsi && opsi.staf), hapus: K.hapus.length };
  if (r.patch) r.patch = Object.assign({}, r.patch, { kabar: String(r.patch.kabar || '') + K.kabar });
  return r;
}
/** Kelahiran / pembatalan karung bekas yang DITITIP akun bukan-owner dan belum dicatat owner. */
export function wbKarungBekasTunda() {
  const P = wbKbPeristiwa(); const lahir = []; const batal = [];
  Object.keys(P).sort().forEach((id) => { const p = P[id]; if (p.akhir === 'lahir' && !p.lahir && p.tanda) lahir.push(Object.assign({}, p.tanda, { karungId: id }));
    else if (p.akhir === 'batal' && p.lahir) batal.push(Object.assign({}, p.tanda || {}, { karungId: id, dok: p.lahir })); });
  return { lahir, batal, n: lahir.length + batal.length };
}
/**
 * Owner: catat semua titipan karung bekas sekali kirim — kelahiran bertanggal HARI INI (tanggal asal disebut di catatannya); pembatalan = kelahiran hari ini
 * dihapus, selain itu catatan pembalik hari ini (wbKbCabut — catatan bulan lampau tidak disentuh).
 */
export function wbSusunKarungBekasTunda(w) {
  const T = wbKarungBekasTunda(); if (!T.n) return { tolak: 'Tidak ada karung bekas yang menunggu dicatat' };
  const N = wbKbNilai(); const harga = N.buku; const s0 = N.sisa; let sisa = s0; const dokumen = []; const hapus = [];
  T.lahir.forEach((x) => { dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: w.idUnik(), tipe: 'opname', jenis: WB_KB_JENIS, jumlah: 1, hargaTotal: 0, tanggal: w.tanggal, jam: w.jam, pcsSistem: sisa, pcsFisik: sisa + 1,
    catatan: 'Karung ' + (x.merkAsal || x.merk) + ' di belakang wadah ' + x.wadah + ' habis' + (x.tanggalAsal ? ' ' + tanggalPendek(x.tanggalAsal) + (x.jamAsal ? ' ' + x.jamAsal : '') : '') + (x.olehAsal ? ' (dicatat ' + x.olehAsal + ')' : '') + ' → jadi karung bekas',
    nilaiRp: harga, hargaPerPcsSaatOpname: harga, lahirKarungBekas: true, karungId: x.karungId, kolam: x.merk, wadah: x.wadah, merkAsal: x.merkAsal || x.merk, ukuranKg: x.ukuranKg, dariId: x.dariId, dariTitipan: true } }); sisa += 1; });
  let nPembalik = 0;
  T.batal.forEach((x) => { const c = wbKbCabut(x, x.dok, w, sisa, harga, x.dariId || ''); if (c.hapus) hapus.push(c.hapus); else { dokumen.push(c.dokumen); nPembalik += 1; } sisa -= 1; });
  return { dokumen, hapus, jejakHapus: hapus.length ? 'karung bekas dibatalkan (titipan akun bukan-owner, kelahiran hari ini): ' + T.batal.filter((x) => hapus.some((h) => String(h.id) === String(x.dok.id))).map((x) => (x.merkAsal || x.merk) + ' ' + x.wadah).join(', ') : '',
    patch: { kbsYakin: false, kabar: 'Karung bekas dicatat: ' + (T.lahir.length ? '+' + T.lahir.length + ' lahir' : '') + (T.batal.length ? (T.lahir.length ? ', ' : '') + T.batal.length + ' dicabut' + (nPembalik ? ' (' + nPembalik + ' lewat catatan pembalik hari ini)' : '') : '') + ' — buku karung bekas ' + s0 + ' → ' + sisa + ' lembar'
      + wbKbKataNilai(N), kabarAwas: false } };
}
/**
 * Owner: setel NILAI KARUNG BEKAS per lembar (angka kebijakan; bawaan = keputusan owner 15 Sep) DAN terapkan ke buku mesin — supaya karung bekas yang lahir
 * dinilai setelan itu dan neraca = laba tetap menutup. Mesin menilai rak karung bekas dengan rata-rata (Σ harga ÷ Σ lembar baris beli / saldo awal); baris
 * lamanya TIDAK diubah. Yang ditambah, bertanggal HARI INI: satu catatan PENYETEL harga (tipe 'saldoAwal' jumlah 0 — bukan uang: pembaca kas hanya membaca
 * 'beli'; buku tanpa baris berharga: jumlah 1 dinetralkan opname −1) sebesar nilai × Σ lembar − Σ harga, dan satu catatan SELISIH NILAI (tipe 'opname'
 * jumlah 0) sebesar lembar di rak × (nilai baru − harga buku): neraca naik = laba HARI INI naik sebesar itu, bulan lalu tidak berubah. Keduanya bertanda
 * `nilaiKarungBekas` (bukan hitungan fisik). Dua ketukan bila rupiah bergerak. Hitungannya diperiksa ulang lewat mesin sebelum dikirim (harga buku = nilai,
 * sisa tetap, Δ nilai rak = Δ laba) — tidak menutup = ditolak, tidak ada yang dikirim.
 */
export function wbSusunNilaiKarungBekas(ketik, w, yakin) {
  const N = wbKbNilai(); const t = String(ketik === undefined || ketik === null ? '' : ketik).trim().replace(/^rp\s*/i, '');
  if (t !== '' && !/^\d{1,3}(\.\d{3})*$|^\d+$/.test(t)) return { tolak: 'Ketik nilai SATU lembar dalam rupiah, angka saja (mis. 1500)' };
  const v = t === '' ? N.setelan : Math.round(Number(t.replace(/\./g, '')));
  if (!(v >= 1 && v <= WB_KB_NILAI_MAKS)) return { tolak: 'Nilai satu lembar karung bekas harus ' + RP(1) + '–' + RP(WB_KB_NILAI_MAKS) };
  const ubahSetelan = !N.diatur || N.setelan !== v; const ubahBuku = N.buku !== v;
  if (!ubahSetelan && !ubahBuku) return { tolak: 'Nilai karung bekas sudah ' + RP(v) + '/lembar — di setelan dan di buku' };
  const riwayat = (N.dok && Array.isArray(N.dok.riwayat) ? N.dok.riwayat : []).concat([{ tanggal: w.tanggal, jam: w.jam, dari: N.diatur ? N.setelan : null, ke: v, bukuDari: N.buku }]).slice(-20);
  const dokumen = [{ koleksi: 'aturanToko', data: { id: 'karungBekas', tanggal: w.tanggal, jam: w.jam, nilaiLembar: v, riwayat } }];
  const rak = Math.max(0, N.sisa); const delta = ubahBuku ? rak * (v - N.buku) : 0;
  if (ubahBuku) {
    const tanpaHarga = !(N.totalBeli > 0); const catatan = 'Nilai karung bekas disetel ' + RP(N.buku) + ' → ' + RP(v) + '/lembar (setelan owner) — baris belanja lamanya tidak diubah';
    dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: w.idUnik(), tipe: 'saldoAwal', jenis: WB_KB_JENIS, jumlah: tanpaHarga ? 1 : 0, hargaTotal: tanpaHarga ? v : Math.round(v * N.totalBeli - N.totalHargaBeli), tanggal: w.tanggal, jam: w.jam, nilaiKarungBekas: true, catatan } });
    if (tanpaHarga || delta) dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: w.idUnik(), tipe: 'opname', jenis: WB_KB_JENIS, jumlah: tanpaHarga ? -1 : 0, hargaTotal: 0, tanggal: w.tanggal, jam: w.jam, pcsSistem: N.sisa + (tanpaHarga ? 1 : 0), pcsFisik: N.sisa,
      nilaiRp: delta, hargaPerPcsSaatOpname: v, nilaiKarungBekas: true, catatan: catatan + ' · ' + rak + ' lembar di rak' } });
  }
  // diperiksa ulang lewat mesin beku: harga buku = nilai, sisa tetap, Δ nilai rak (neraca) = Δ laba
  const S1 = denganCacheSementara(dokumen, () => { const s = hitungStokBahanLiteran()[WB_KB_JENIS] || {}; return { harga: Math.round(Number(s.hargaPerPcs) || 0), sisa: Math.round(Number(s.sisaPcs) || 0) }; });
  if (ubahBuku && (S1.harga !== v || S1.sisa !== N.sisa || Math.max(0, S1.sisa) * S1.harga - rak * N.buku !== delta)) return { tolak: 'Hitungan penyetel nilai karung bekas tidak menutup (buku jadi ' + RP(S1.harga) + ', sisa ' + S1.sisa + ') — tidak ada yang dikirim' };
  const arah = delta >= 0 ? 'naik' : 'turun';
  const akibat = !ubahBuku ? 'buku sudah ' + RP(v) + '/lembar, tidak ada rupiah yang bergerak'
    : 'buku karung bekas ' + RP(N.buku) + ' → ' + RP(v) + '/lembar: ' + rak + ' lembar di rak ' + arah + ' ' + RP(Math.abs(delta)) + ' = laba HARI INI ' + arah + ' ' + RP(Math.abs(delta)) + ' (selisih nilai, bukan uang masuk; bulan lalu & baris belanja lamanya tidak berubah). Sesudahnya karung bekas yang lahir dinilai ' + RP(v) + ' dan yang dipakai / dijual dibebankan ' + RP(v) + ' per lembar';
  if (ubahBuku && !yakin) return { tolak: 'Ketuk sekali lagi untuk menerapkan nilai karung bekas ' + RP(v) + '/lembar — ' + akibat, perluYakin: true };
  return { dokumen, hitung: { v, delta, rak, dari: N.buku }, patch: { kbNilai: '', kbNilaiYakin: false, kabar: 'Nilai karung bekas ' + RP(v) + '/lembar tersimpan sebagai setelan owner — ' + akibat, kabarAwas: false } };
}
