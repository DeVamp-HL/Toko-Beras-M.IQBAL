// ASET TETAP & PENYUSUTAN (modul ERP no. 70, owner 26 Nov 2026 — sensus ulang 26 Nov bagian 2). Logika tanpa DOM, modul DAUN (data/toko.js + inti/format.js saja,
// karena uang-logika.js memakainya untuk laba bersih); nama pembantu berawalan `ast` (bundel uji jsc satu lingkup).
//
// Keputusan owner (satu AskUserQuestion, 26 Nov 2026):
//  - daftar aset = ISIAN OWNER + BAWAAN: per barang nama, jenis, harga beli, tanggal beli; bawaan yang bisa diubah per barang = umur per jenis (peralatan kecil 4 th ·
//    peralatan besar & mesin 8 th · kendaraan 8 th · bangunan 20 th), nilai sisa 0, garis lurus (satu-satunya metode).
//  - barang yang dulu dibeli pakai uang toko (sudah tercatat di Uang keluar = BIAYA) boleh MENUNJUK catatannya: harga ≤ nominal catatan itu dikeluarkan dari laba
//    bulan catatannya ("dipindah jadi aset tetap"), diganti penyusutan. Tanpa tunjuk = dibawa owner / dibeli sebelum sistem (modal berupa barang): uang toko tidak bergerak.
//  - penyusutan MEMOTONG laba bersih — lewat satu pintu ugLabaBersih (uang-logika.js), jadi semua layar ikut; mesin beku tidak disentuh.
//  - mulai 1 Des 2026 (bawaan, setelan owner `mulai`): penyusutan sebelum tanggal itu (dihitung dari tanggal beli) mengurangi nilai aset tetapi TIDAK memotong laba bulan
//    mana pun. Isian lama aturanToko/laporan.asetTetap (satu angka) tidak dipakai Neraca lagi begitu daftar ini punya satu barang.
// Tafsir sesi (disebut di laporan ke owner): uang keluar yang ditunjuk tetap dikeluarkan dari laba BULAN CATATANNYA walau sebelum tanggal mulai; bulan yang sudah
// dikunci / ditutup buku TIDAK boleh berubah — setiap simpan / hapus / ganti tanggal mulai yang menggeser laba bulan terkunci DITOLAK.
//
// Penyusutan harian garis lurus, persis & menutup: susut terkumpul s.d. akhir hari t = round((harga − sisa) × hari terpakai / hari umur), hari umur = tanggal beli
// sampai tanggal beli + umur bulan. Penyusutan rentang [a, b] = S(b) − S(a − 1), jadi Σ hari = Σ minggu = bulan = tahun persis (aturan yang sama dengan jatah biaya
// bulanan mesin). Dokumen: aturanToko/asetTetap { mulai, aset: [...] } — owner saja (rules TIDAK berubah; staf tidak membacanya).
import { cacheMentah, ambilPengeluaranHarian, kunciSampai, eraBuku, ingatPerVersi } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';

export const AST_ID = 'asetTetap';
export const AST_MULAI_BAWAAN = '2026-12-01';
export const AST_MAKS = 80;   // penjaga ukuran satu dokumen
export const AST_HARGA_MAKS = 10000000000;
export const AST_JENIS = [['kecil', 'Peralatan kecil', 48, 'timbangan, rak, etalase, alat jahit karung, tablet'], ['besar', 'Peralatan besar & mesin', 96, 'mesin, genset, lemari pendingin'],
  ['kendaraan', 'Kendaraan', 96, 'motor, mobil antar'], ['bangunan', 'Bangunan & renovasi', 240, 'bangunan permanen, renovasi toko']].map((x) => ({ id: x[0], nama: x[1], umurBulan: x[2], contoh: x[3] }));
export const AST_KATEGORI_TUNJUK = ['toko', 'tokoDompet'];   // uang keluar yang dibaca laba mesin sebagai biaya toko (hitungLabaBersihRentang)

const astIso = (t) => /^\d{4}-\d\d-\d\d$/.test(String(t || ''));
const astHari = (iso) => Math.round(Date.UTC(Number(iso.slice(0, 4)), Number(iso.slice(5, 7)) - 1, Number(iso.slice(8, 10))) / 86400000);
const astDariHari = (n) => new Date(n * 86400000).toISOString().slice(0, 10);
export const astGeser = (iso, n) => astDariHari(astHari(iso) + n);
/** Tanggal + n bulan (hari dijepit ke akhir bulan: 31 Jan + 1 = 28/29 Feb). */
export function astTambahBulan(iso, n) {
  const y = Number(iso.slice(0, 4)), m = Number(iso.slice(5, 7)) - 1 + n, d = Number(iso.slice(8, 10)); const Y = y + Math.floor(m / 12), M = ((m % 12) + 12) % 12;
  const akhir = new Date(Date.UTC(Y, M + 1, 0)).getUTCDate(); return Y + '-' + String(M + 1).padStart(2, '0') + '-' + String(Math.min(d, akhir)).padStart(2, '0');
}
export const astAkhirBulan = (key) => astGeser(astTambahBulan(String(key).slice(0, 7) + '-01', 1), -1);
const astBulanBerikut = (key) => astTambahBulan(String(key).slice(0, 7) + '-01', 1).slice(0, 7);
const AST_BLN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
export const astNamaBulan = (key) => AST_BLN[Number(String(key).slice(5, 7)) - 1] + ' ' + String(key).slice(0, 4);
/** Angka ketikan owner (1.500.000 · 1500000 · 1,5) → bilangan; kosong / ngawur = NaN. Aturan baca yang sama dengan ugAngka (modul daun tidak boleh mengimpor uang-logika). */
export function astAngka(v) {
  const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return NaN;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : NaN;
}
export const astJenis = (id) => AST_JENIS.find((j) => j.id === id) || AST_JENIS[0];

function astBaku(x) {
  const J = astJenis(x && x.jenis); const harga = Math.round(Number(x && x.harga)); const umur = Math.round(Number(x && x.umurBulan)); const sisa = Math.round(Number(x && x.sisa));
  const h = isFinite(harga) && harga > 0 ? harga : 0;
  return { id: String((x && x.id) || ''), nama: String((x && x.nama) || '').trim().slice(0, 60), jenis: J.id, harga: h, tanggalBeli: astIso(x && x.tanggalBeli) ? x.tanggalBeli : '',
    umurBulan: isFinite(umur) && umur >= 1 && umur <= 600 ? umur : J.umurBulan, sisa: isFinite(sisa) && sisa >= 0 && sisa < h ? sisa : 0,
    dariKeluar: x && x.dariKeluar !== undefined && x.dariKeluar !== null && String(x.dariKeluar) !== '' ? String(x.dariKeluar) : null, catatan: String((x && x.catatan) || '').slice(0, 120),
    dicatat: String((x && x.dicatat) || ''), diubah: String((x && x.diubah) || '') };
}
/** Setelan & daftar aset: { mulai, aset: [barang sah], dok (dokumen mentah | null), dariOwner }. Barang tanpa harga / tanggal beli sah dilewati (disebut nBuang). */
export function astAtur() {
  return ingatPerVersi('astAtur', () => {
    const d = cacheMentah('aturan').find((x) => x && String(x.id) === AST_ID) || null; const mentah = d && Array.isArray(d.aset) ? d.aset : [];
    const aset = mentah.map(astBaku).filter((a) => a.id && a.harga > 0 && a.tanggalBeli);
    return { mulai: d && astIso(d.mulai) ? d.mulai : AST_MULAI_BAWAAN, aset, dok: d, dariOwner: !!d, nBuang: mentah.length - aset.length };
  });
}
/** Susut terkumpul satu barang s.d. AKHIR hari t (rupiah bulat). Sebelum tanggal beli 0; sesudah umur habis = harga − sisa. */
export function astSusut(a, t) {
  if (!astIso(t) || !a.tanggalBeli || t < a.tanggalBeli) return 0; const dep = Math.max(0, a.harga - a.sisa); if (!dep) return 0;
  const h0 = astHari(a.tanggalBeli); const umur = Math.max(1, astHari(astTambahBulan(a.tanggalBeli, a.umurBulan)) - h0); const k = astHari(t) - h0 + 1;
  return k >= umur ? dep : Math.round(dep * k / umur);
}
/** Kira-kira penyusutan sebulan (untuk kalimat layar; angka laba memakai hitungan harian astSusut). */
export const astPerBulan = (a) => Math.round(Math.max(0, a.harga - a.sisa) / Math.max(1, a.umurBulan));
/** Tanggal umur barang habis (hari terakhir disusutkan). */
export const astHabis = (a) => astGeser(astTambahBulan(a.tanggalBeli, a.umurBulan), -1);

const astPetaKeluar = () => ingatPerVersi('astPetaKeluar', () => { const p = {}; ambilPengeluaranHarian().forEach((h) => { if (h && h.id !== undefined && h.id !== null) p[String(h.id)] = h; }); return p; });
/** Uang keluar yang ditunjuk sebagai aset: [{ aset, idKeluar, tanggal, n = min(harga, nominal), ada }] — catatan yang sudah tidak ada / bukan biaya toko: ada = false, n = 0. */
export function astDariBiaya(A0) {
  const A = A0 || astAtur(); const peta = astPetaKeluar(); const out = [];
  A.aset.forEach((a) => { if (!a.dariKeluar) return; const h = peta[a.dariKeluar]; const sah = !!h && AST_KATEGORI_TUNJUK.indexOf(h.kategori) >= 0 && astIso(h.tanggal) && !h.mdr;
    out.push({ aset: a.id, nama: a.nama, idKeluar: a.dariKeluar, tanggal: sah ? h.tanggal : '', n: sah ? Math.min(a.harga, Math.round(Number(h.nominal) || 0)) : 0, ada: sah, kategori: h ? h.kategori : '' }); });
  return out;
}
/**
 * Akibat aset tetap pada LABA rentang [dari, sampai]: penyusutan (hari ≥ mulai) dan uang keluar yang dipindah jadi aset (tanggal catatannya di rentang). Daftar kosong →
 * ada = false (ugLabaBersih tidak menambah kolom apa pun — angka & bentuk byte-sama dengan sebelum modul ini). `sebelum` = bagian penyusutan rentang itu yang jatuh
 * SEBELUM mulai (tidak memotong laba; dipakai jurnal).
 */
export function astEfekLaba(dari, sampai, A0) {
  const A = A0 || astAtur(); if (!A.aset.length) return { ada: false, penyusutan: 0, dariBiaya: 0, nDariBiaya: 0, sebelum: 0 };
  if (!astIso(dari) || !astIso(sampai) || dari > sampai) return { ada: true, penyusutan: 0, dariBiaya: 0, nDariBiaya: 0, sebelum: 0 };
  const m = A.mulai; const awal = dari > m ? dari : m; const akhirSeb = sampai < m ? sampai : astGeser(m, -1); let pen = 0, seb = 0;
  A.aset.forEach((a) => { if (awal <= sampai) pen += astSusut(a, sampai) - astSusut(a, astGeser(awal, -1)); if (dari <= akhirSeb) seb += astSusut(a, akhirSeb) - astSusut(a, astGeser(dari, -1)); });
  let db = 0, n = 0; astDariBiaya(A).forEach((x) => { if (x.ada && x.tanggal >= dari && x.tanggal <= sampai && x.n > 0) { db += x.n; n += 1; } });
  return { ada: true, penyusutan: pen, dariBiaya: db, nDariBiaya: n, sebelum: seb };
}
/**
 * Keadaan aset pada akhir hari t (Neraca): barang yang sudah dibeli s.d. t — harga beli, susut terkumpul, nilai buku; `sebelum` = susut terkumpul sebelum mulai
 * (tidak pernah memotong laba), `dibawa` = harga barang yang TIDAK menunjuk uang keluar yang sah (modal berupa barang). ada = daftar tidak kosong.
 */
export function astPada(t, A0) {
  const A = A0 || astAtur(); const iso = astIso(t) ? t : hariIniIso(); const sebT = iso < A.mulai ? iso : astGeser(A.mulai, -1); const tunjuk = {}; astDariBiaya(A).forEach((x) => { if (x.ada) tunjuk[x.aset] = x; });
  const daftar = A.aset.filter((a) => a.tanggalBeli <= iso).map((a) => { const s = astSusut(a, iso); const T = tunjuk[a.id] || null;
    return Object.assign({}, a, { susut: s, buku: a.harga - s, sebelum: astSusut(a, sebT), habis: s >= a.harga - a.sisa && a.harga - a.sisa > 0, tunjuk: T, perBulan: astPerBulan(a) }); });
  const jml = (f) => daftar.reduce((x, a) => x + a[f], 0);
  return { ada: A.aset.length > 0, n: daftar.length, harga: jml('harga'), susut: jml('susut'), buku: jml('buku'), sebelum: jml('sebelum'), dibawa: daftar.filter((a) => !a.tunjuk).reduce((x, a) => x + a.harga, 0),
    dariBiaya: daftar.filter((a) => a.tunjuk).reduce((x, a) => x + a.tunjuk.n, 0), daftar, mulai: A.mulai, tanggal: iso };
}

// ---------- bulan terkunci / ditutup tidak boleh bergeser ----------
/** Bulan (YYYY-MM) yang laba-nya sudah final: dikunci (Kunci bulan) atau tahunnya sudah ditutup buku. */
export function astTerkunci(key) { const era = eraBuku(); if (era !== null && Number(String(key).slice(0, 4)) <= era) return true; const s = kunciSampai(); return !!s && String(key).slice(0, 7) <= s; }
/** Bulan terkunci PERTAMA yang labanya berbeda antara setelan A1 dan A2 (null = tidak ada). */
export function astGeserKunci(A1, A2) {
  const era = eraBuku(); const s = kunciSampai(); const akhirKunci = [s, era !== null ? era + '-12' : null].filter(Boolean).sort().pop(); if (!akhirKunci) return null;
  const awal = [A1.mulai, A2.mulai].concat(astDariBiaya(A1).concat(astDariBiaya(A2)).filter((x) => x.ada).map((x) => x.tanggal)).filter(astIso).sort()[0]; if (!awal) return null;
  let k = awal.slice(0, 7); for (let i = 0; i < 1200 && k <= akhirKunci; i++, k = astBulanBerikut(k)) {
    if (!astTerkunci(k)) continue; const a = k + '-01', b = astAkhirBulan(k); const e1 = astEfekLaba(a, b, A1), e2 = astEfekLaba(a, b, A2);
    if (Math.round(e1.dariBiaya - e1.penyusutan) !== Math.round(e2.dariBiaya - e2.penyusutan)) return k; }
  return null;
}
const astTolakKunci = (k) => 'Laba ' + astNamaBulan(k) + ' akan berubah, padahal bulan itu sudah dikunci / ditutup buku — buka kuncinya dulu (Uang › Tutup buku) atau pilih tanggal / catatan lain';

// ---------- calon uang keluar yang bisa ditunjuk ----------
/** Uang keluar untuk toko (toko / dompet owner, bukan potongan QRIS) yang bisa ditunjuk sebagai pembelian aset — terbesar dulu (lalu terbaru); terkunci & sudah ditunjuk diberi tanda. */
export function astCalon(cari, kecualiAset, n) {
  const A = astAtur(); const dipakai = {}; A.aset.forEach((a) => { if (a.dariKeluar && a.id !== kecualiAset) dipakai[a.dariKeluar] = a.nama; }); const q = String(cari || '').trim().toLowerCase();
  return ambilPengeluaranHarian().filter((h) => h && AST_KATEGORI_TUNJUK.indexOf(h.kategori) >= 0 && !h.mdr && astIso(h.tanggal) && (Number(h.nominal) || 0) > 0 && (!q || String(h.keterangan || '').toLowerCase().indexOf(q) >= 0))
    .sort((a, b) => (Number(b.nominal) || 0) - (Number(a.nominal) || 0) || String(b.tanggal + (b.jam || '')).localeCompare(String(a.tanggal + (a.jam || '')))).slice(0, n || 30)
    .map((h) => ({ id: String(h.id), tanggal: h.tanggal, jam: h.jam || '', keterangan: String(h.keterangan || '(tanpa keterangan)'), nominal: Math.round(Number(h.nominal) || 0), kategori: h.kategori,
      dompet: h.kategori === 'tokoDompet', terkunci: astTerkunci(h.tanggal.slice(0, 7)), dipakai: dipakai[String(h.id)] || '' }));
}

// ---------- simpan / hapus / atur ----------
/** Draf lembar → barang baku atau { tolak }. draf: { id?, nama, jenis, harga, tanggalBeli, umurBulan, sisa, dariKeluar, catatan } (isian teks). */
export function astBacaDraf(draf, kini) {
  const D = draf || {}; const hari = hariIniIso(kini || new Date()); const A = astAtur(); const nama = String(D.nama || '').trim();
  if (nama.length < 2) return { tolak: 'Ketik nama barangnya (mis. timbangan digital 150 kg)' };
  const J = AST_JENIS.find((j) => j.id === D.jenis); if (!J) return { tolak: 'Pilih jenis barangnya' };
  let tanggal = String(D.tanggalBeli || ''); let batasHarga = AST_HARGA_MAKS; let tunjuk = null;
  if (D.dariKeluar !== undefined && D.dariKeluar !== null && String(D.dariKeluar) !== '') {
    const h = astPetaKeluar()[String(D.dariKeluar)]; if (!h) return { tolak: 'Catatan uang keluar itu sudah tidak ada — pilih lagi' };
    if (AST_KATEGORI_TUNJUK.indexOf(h.kategori) < 0 || h.mdr) return { tolak: 'Yang bisa ditunjuk hanya uang keluar untuk toko (bukan ambil pribadi / potongan QRIS)' };
    const lain = A.aset.find((a) => a.dariKeluar === String(D.dariKeluar) && a.id !== String(D.id || '')); if (lain) return { tolak: 'Catatan itu sudah ditunjuk oleh aset "' + lain.nama + '"' };
    tanggal = h.tanggal; batasHarga = Math.round(Number(h.nominal) || 0); tunjuk = h;
  }
  if (!astIso(tanggal) || tanggal > hari || tanggal < '1980-01-01') return { tolak: 'Tanggal beli belum benar (tidak boleh sesudah hari ini)' };
  const harga = astAngka(D.harga); if (!isFinite(harga) || harga <= 0 || Math.round(harga) !== harga) return { tolak: 'Harga beli harus rupiah bulat lebih dari nol' };
  if (harga > batasHarga) return { tolak: tunjuk ? 'Harga aset tidak boleh lebih besar dari catatan uang keluarnya (' + RP(batasHarga) + ')' : 'Harga beli terlalu besar' };
  const umurT = String(D.umurBulan === undefined || D.umurBulan === null ? '' : D.umurBulan).trim(); const umur = umurT ? astAngka(umurT) : J.umurBulan;
  if (!isFinite(umur) || Math.round(umur) !== umur || umur < 1 || umur > 600) return { tolak: 'Umur harus bulan bulat 1–600 (bawaan ' + J.nama.toLowerCase() + ' ' + J.umurBulan + ' bulan)' };
  const sisaT = String(D.sisa === undefined || D.sisa === null ? '' : D.sisa).trim(); const sisa = sisaT ? astAngka(sisaT) : 0;
  if (!isFinite(sisa) || Math.round(sisa) !== sisa || sisa < 0 || sisa >= harga) return { tolak: 'Nilai sisa harus rupiah bulat, 0 sampai di bawah harga beli (bawaan 0)' };
  return { aset: astBaku({ id: D.id, nama, jenis: J.id, harga, tanggalBeli: tanggal, umurBulan: umur, sisa, dariKeluar: tunjuk ? String(D.dariKeluar) : null, catatan: String(D.catatan || '').trim() }), tunjuk };
}
const astDokumen = (A, aset, mulai, w) => [{ koleksi: 'aturanToko', data: Object.assign({}, A.dok || {}, { id: AST_ID, tanggal: w.tanggal, jam: w.jam, mulai, aset: aset.map((a) => {
  const o = { id: a.id, nama: a.nama, jenis: a.jenis, harga: a.harga, tanggalBeli: a.tanggalBeli, umurBulan: a.umurBulan, sisa: a.sisa, dicatat: a.dicatat || w.tanggal, diubah: a.diubah || w.tanggal };
  if (a.dariKeluar) o.dariKeluar = a.dariKeluar; if (a.catatan) o.catatan = a.catatan; return o; }) }) }];
/** Tambah / ubah satu barang (draf.id = barang lama). Tolak bila menggeser laba bulan terkunci. */
export function susunAset(draf, w, kini) {
  const R = astBacaDraf(draf, kini); if (R.tolak) return { tolak: R.tolak }; const A = astAtur(); const lama = draf && draf.id ? A.aset.find((a) => a.id === String(draf.id)) : null;
  if (draf && draf.id && !lama) return { tolak: 'Barang itu sudah tidak ada di daftar' }; if (!lama && A.aset.length >= AST_MAKS) return { tolak: 'Daftar aset sudah ' + AST_MAKS + ' barang — gabungkan yang kecil-kecil' };
  const a = Object.assign({}, R.aset, { id: lama ? lama.id : 'as-' + w.idUnik(), dicatat: lama ? lama.dicatat : w.tanggal, diubah: w.tanggal });
  const daftar = lama ? A.aset.map((x) => (x.id === lama.id ? a : x)) : A.aset.concat([a]); const A2 = { mulai: A.mulai, aset: daftar, dok: A.dok };
  const k = astGeserKunci(A, A2); if (k) return { tolak: astTolakKunci(k) };
  const sekarang = hariIniIso(kini || new Date()); const P = astPada(sekarang, A2).daftar.find((x) => x.id === a.id);
  const pindah = R.tunjuk ? ' · laba ' + astNamaBulan(R.tunjuk.tanggal) + ' naik ' + RP(Math.min(a.harga, Math.round(Number(R.tunjuk.nominal) || 0))) + ' (uang keluar ' + tanggalPendek(R.tunjuk.tanggal) + ' dipindah jadi aset tetap)' : ' · dibawa owner / dibeli sebelum sistem — uang toko tidak bergerak';
  return { dokumen: astDokumen(A, daftar, A.mulai, w), patch: { drafAs: null, kabar: 'Aset "' + a.nama + '" ' + (lama ? 'diubah' : 'dicatat') + ' — susut ±' + RP(astPerBulan(a)) + '/bulan, nilai sekarang ' + RP(P ? P.buku : a.harga) + pindah, kabarAwas: false } };
}
/** Hapus satu barang dari daftar (ketukan kedua = yakin). */
export function susunHapusAset(id, w, yakin) {
  const A = astAtur(); const a = A.aset.find((x) => x.id === String(id)); if (!a) return { tolak: 'Barang itu sudah tidak ada di daftar' };
  if (!yakin) return { perluYakin: true, tolak: 'Ketuk sekali lagi untuk menghapus "' + a.nama + '" dari daftar — penyusutannya keluar dari laba sejak ' + tanggalPendek(A.mulai) + (a.dariKeluar ? ' dan uang keluarnya kembali jadi biaya' : '') };
  const daftar = A.aset.filter((x) => x.id !== a.id); const k = astGeserKunci(A, { mulai: A.mulai, aset: daftar, dok: A.dok }); if (k) return { tolak: astTolakKunci(k) };
  return { dokumen: astDokumen(A, daftar, A.mulai, w), patch: { drafAs: null, yakinAs: null, kabar: 'Aset "' + a.nama + '" dihapus dari daftar', kabarAwas: false } };
}
/** Atur tanggal mulai penyusutan memotong laba. Tolak bila menggeser bulan terkunci. */
export function susunAturAset(isi, w) {
  const A = astAtur(); const m = String((isi && isi.mulai) || ''); if (!astIso(m) || m < '2000-01-01') return { tolak: 'Tanggal mulai belum benar' };
  const k = astGeserKunci(A, { mulai: m, aset: A.aset, dok: A.dok }); if (k) return { tolak: astTolakKunci(k) };
  return { dokumen: astDokumen(A, A.aset, m, w), patch: { aturAs: null, kabar: 'Penyusutan memotong laba mulai ' + tanggalPendek(m) + (m === AST_MULAI_BAWAAN ? ' (bawaan)' : ''), kabarAwas: false } };
}

// ---------- ringkasan layar ----------
/** Ringkasan Laporan › Aset tetap: keadaan hari ini, bulan ini, 12 bulan ke depan, isian lama, catatan yang ditunjuk. */
export function astRingkas(kini, asetLama) {
  const A = astAtur(); const hari = hariIniIso(kini || new Date()); const P = astPada(hari, A); const bulan = hari.slice(0, 7);
  const efekBulan = astEfekLaba(bulan + '-01', astAkhirBulan(bulan), A); const sdHariIni = astEfekLaba(bulan + '-01', hari, A);
  const depan = []; let k = bulan; for (let i = 0; i < 12; i++, k = astBulanBerikut(k)) { const e = astEfekLaba(k + '-01', astAkhirBulan(k), A); depan.push({ key: k, nama: astNamaBulan(k), n: e.penyusutan, mulai: k + '-01' >= A.mulai.slice(0, 7) + '-01' }); }
  const maks = Math.max(1, ...depan.map((x) => x.n)); const tunjuk = astDariBiaya(A);
  return { A, P, hari, mulai: A.mulai, mulaiBawaan: A.mulai === AST_MULAI_BAWAAN, belumMulai: hari < A.mulai, bulan: { key: bulan, nama: astNamaBulan(bulan), penuh: efekBulan.penyusutan, sdHariIni: sdHariIni.penyusutan, dariBiaya: efekBulan.dariBiaya },
    depan, maks, tunjuk, tunjukHilang: tunjuk.filter((x) => !x.ada), lama: asetLama && asetLama.asetTetap > 0 ? asetLama : null, nBuang: A.nBuang };
}
