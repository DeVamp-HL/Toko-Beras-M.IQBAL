// BANDING PEMASOK — CATATAN (owner 26 Nov 2026, sensus ulang bagian 1c: A18 harga tawaran, A19 harga acuan resmi). Logika tanpa DOM, awalan bc
// (bundel uji jsc satu lingkup). Modul DAUN: hanya data/toko.js, mesin/pembantu.js, inti/format.js — supaya sistem-logika (pengingat, papan Persetujuan)
// boleh mengimpornya tanpa menarik mesin laporan. Hitungan banding (modal sampai toko, layak jual, rapor) ada di banding-pemasok-logika.js.
//
// KEPUTUSAN OWNER (AskUserQuestion 26 Nov 2026):
//  1. Yang mencatat harga TAWARAN (harga dari pemasok yang ditanya tapi tidak jadi dibeli) dan harga ACUAN resmi = OWNER langsung + PENJAGA LACI (Ben)
//     lewat USUL dari tablet: satu dokumen persetujuan bertindakan 'hargaBanding' (rules v21 stafUsulBanding), owner SETUJUI → baru catatannya ditulis
//     atas nama owner (bentuk yang sama dengan titipan & usul harga pelanggan). Akun tablet tidak pernah menulis catatan banding.
//  2. Pengingat: tiap JUMAT catat harga ≥ N pemasok minggu ini (sebelum belanja Senin), tiap TANGGAL 1 banding bulan lalu. Hari, tanggal & N = setelan owner.
//  4. Harga acuan: KETIK MANUAL (sumber, tingkat, medium/premium, wilayah — daftar sumber diatur owner) + TARIK OTOMATIS dicoba: fungsi server mingguan
//     (functions/index.js tarikAcuan) menulis aturanToko/acuanTarik; layar menampilkannya sebagai USULAN yang owner PAKAI satu per satu (tidak masuk banding
//     sendiri). Format jawaban server Bapanas belum pernah terlihat dari sini — fungsi menyimpan apa yang ia temukan + pesannya.
//
// PENYIMPANAN tanpa koleksi baru: aturanToko/bandingPemasok (setelan, ikut riwayat setelan) + aturanToko/banding-YYYY-MM (catatan satu bulan:
// entri tawaran & acuan + tanda "sudah dibanding" bulan itu — CATATAN, dilewati riwayat setelan seperti cocokRek-). Bulan = bulan TANGGAL harganya.
import { cacheMentah, ambilSemuaBatch, namaSistemPemasok } from '../data/toko.js';
import { kunciPelanggan } from '../mesin/pembantu.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';

export const BC_ATUR_ID = 'bandingPemasok';
export const BC_AWALAN = 'banding-';
export const BC_DOK = (bulan) => BC_AWALAN + String(bulan).slice(0, 7);
export const BC_TARIK_ID = 'acuanTarik';
export const BC_TINDAKAN = 'hargaBanding';
export const BC_JENIS = [['tawaran', 'Harga tawaran pemasok'], ['acuan', 'Harga acuan resmi']];
export const BC_HARI = [[1, 'Senin'], [2, 'Selasa'], [3, 'Rabu'], [4, 'Kamis'], [5, 'Jumat'], [6, 'Sabtu'], [0, 'Minggu']];
// tanda mutu AWAS yang boleh diberi potongan Rp/kg (keputusan owner 26 Nov 2026: "plus potongan mutu Rp") — id = tanda tmBaris (stok-catat-logika)
export const BC_TANDA = [['kadarAir', 'kadar air lewat batas'], ['butirPatah', 'butir patah lewat batas'], ['menir', 'menir lewat batas kelas'], ['kuning', 'butir kuning / rusak lewat batas kelas'],
  ['butirLain', 'butir lain / benda lain lewat batas kelas'], ['gabah', 'gabah lewat batas kelas'], ['kutu', 'ada kutu'], ['bau', 'bau apek / tidak normal']];
export const BC_TINGKAT = [['produsen', 'produsen / penggilingan'], ['grosir', 'pedagang besar / grosir'], ['eceran', 'eceran / konsumen']];
export const BC_MUTU = [['medium', 'medium'], ['premium', 'premium']];
export const BC_SUMBER_BAWAAN = ['Panel Harga Bapanas', 'PIHPS BI', 'BPS'];
export const BC_BAWAAN = { minPemasok: 3, hariMinggu: 5, tanggalBulan: 1, wilayah: '' };
export const BC_SUSUL = 7;   // banding bulan lalu ditagih paling lama 7 hari sesudah tanggalnya (pola tinjauan bulanan — bukan pengingat abadi)
export const BC_BATAS = { pemasok: 60, kelas: 60, merek: 60, catatan: 160, wilayah: 60, sumber: 40, nSumber: 12, hargaMin: 1000, hargaMaks: 100000, ongkirMaks: 5000, potongMaks: 5000, mundur: 62, entriBulan: 400, teks: 300 };

const bcBersih = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const bcKosong = (v) => bcBersih(v) === '';
const bcNama = (daftar, id) => (daftar.find((x) => String(x[0]) === String(id)) || ['', ''])[1];
export const bcHariKe = (iso) => Math.round(Date.UTC(+String(iso).slice(0, 4), +String(iso).slice(5, 7) - 1, +String(iso).slice(8, 10)) / 86400000);
export const bcTambahHari = (iso, n) => new Date((bcHariKe(iso) + n) * 86400000).toISOString().slice(0, 10);
const bcIsoSah = (t) => /^\d{4}-\d{2}-\d{2}$/.test(String(t || '')) && bcTambahHari(String(t), 0) === String(t);
/** Hari dalam minggu 0 (Minggu) … 6 (Sabtu) untuk tanggal ISO. */
export const bcHariMinggu = (iso) => new Date(String(iso) + 'T00:00:00Z').getUTCDay();
/** Senin minggu itu (minggu = Senin–Minggu). */
export const bcSenin = (iso) => bcTambahHari(iso, -((bcHariMinggu(iso) + 6) % 7));
export const bcBulanGeser = (key, n) => { const i = Number(String(key).slice(0, 4)) * 12 + Number(String(key).slice(5, 7)) - 1 + n; return Math.floor(i / 12) + '-' + String(i % 12 + 1).padStart(2, '0'); };
/**
 * Rupiah bulat dari ketikan: "14500", "14.500", "Rp 14.500" → 14500. Pecahan ("14,5"), huruf, minus → NaN (DITOLAK, bukan dibulatkan diam-diam).
 * Kosong → null.
 */
export function bcRupiah(v) {
  if (typeof v === 'number') return Number.isInteger(v) ? v : NaN; const t = String(v === undefined || v === null ? '' : v).replace(/rp/i, '').replace(/\s/g, '');
  if (!t) return null; if (/^\d+$/.test(t)) return Number(t); if (/^\d{1,3}(\.\d{3})+$/.test(t)) return Number(t.replace(/\./g, '')); return NaN;
}
export const bcPemasokSungguhan = (nama) => { const n = bcBersih(nama); return n !== '' && !namaSistemPemasok(n); };

// ==================== SETELAN (aturanToko/bandingPemasok) ====================
const bcDok = (id) => cacheMentah('aturan').find((d) => d && String(d.id) === id) || null;
/** Setelan berlaku: berapa pemasok minimal, hari pengingat mingguan, tanggal banding bulanan, potongan mutu Rp/kg per tanda, daftar sumber acuan, wilayah. */
export function bcAtur() {
  const d = bcDok(BC_ATUR_ID); const a = d || {}; const bil = (k, min, maks, b) => { const n = Number(a[k]); return a[k] !== undefined && a[k] !== null && a[k] !== '' && Number.isInteger(n) && n >= min && n <= maks ? n : b; };
  const pm = a.potongMutu && typeof a.potongMutu === 'object' && !Array.isArray(a.potongMutu) ? a.potongMutu : {}; const potongMutu = {};
  BC_TANDA.forEach(([id]) => { const n = Number(pm[id]); potongMutu[id] = Number.isInteger(n) && n >= 0 && n <= BC_BATAS.potongMaks ? n : 0; });
  const sumber = Array.isArray(a.sumber) ? a.sumber.map(bcBersih).filter((s, i, x) => s && x.indexOf(s) === i).slice(0, BC_BATAS.nSumber) : BC_SUMBER_BAWAAN.slice();
  return { minPemasok: bil('minPemasok', 1, 10, BC_BAWAAN.minPemasok), hariMinggu: bil('hariMinggu', 0, 6, BC_BAWAAN.hariMinggu), tanggalBulan: bil('tanggalBulan', 1, 28, BC_BAWAAN.tanggalBulan),
    potongMutu, adaPotong: BC_TANDA.some(([id]) => potongMutu[id] > 0), sumber: sumber.length ? sumber : BC_SUMBER_BAWAAN.slice(), wilayah: bcBersih(a.wilayah).slice(0, BC_BATAS.wilayah),
    dariOwner: !!d, tanggal: d ? String(d.tanggal || '') : '' };
}
/** Simpan setelan. isi = ketikan lembar Atur (kosong = bawaan). Satu dokumen setelan — tidak menyentuh stok, harga, maupun uang. */
export function susunAturBanding(isi, w) {
  const I = isi || {}; const A = bcAtur(); const bil = (v, b) => (bcKosong(v) ? b : Number(String(v).trim()));
  const min = bil(I.minPemasok, BC_BAWAAN.minPemasok); if (!(Number.isInteger(min) && min >= 1 && min <= 10)) return { tolak: 'Pemasok minimal per minggu / bulan: bilangan bulat 1–10' };
  const hari = bil(I.hariMinggu, BC_BAWAAN.hariMinggu); if (!(Number.isInteger(hari) && hari >= 0 && hari <= 6)) return { tolak: 'Hari pengingat mingguan tidak dikenal — pilih Senin sampai Minggu' };
  const tgl = bil(I.tanggalBulan, BC_BAWAAN.tanggalBulan); if (!(Number.isInteger(tgl) && tgl >= 1 && tgl <= 28)) return { tolak: 'Tanggal banding bulanan: 1–28 (29–31 tidak ada di tiap bulan)' };
  const potongMutu = {}; for (const [id, nm] of BC_TANDA) { const v = (I.potongMutu || {})[id]; const n = bcKosong(v) ? 0 : bcRupiah(v);
    if (!(Number.isInteger(n) && n >= 0 && n <= BC_BATAS.potongMaks)) return { tolak: 'Potongan mutu "' + nm + '" ditulis rupiah bulat per kg: 0 sampai ' + RP(BC_BATAS.potongMaks) + ' (0 = tidak dipotong)' };
    potongMutu[id] = n; }
  const sumber = (Array.isArray(I.sumber) ? I.sumber : A.sumber).map(bcBersih).filter(Boolean);
  if (!sumber.length) return { tolak: 'Daftar sumber harga acuan tidak boleh kosong — sisakan paling sedikit satu' };
  if (sumber.length > BC_BATAS.nSumber) return { tolak: 'Sumber harga acuan paling banyak ' + BC_BATAS.nSumber };
  const panjang = sumber.find((s) => s.length > BC_BATAS.sumber); if (panjang) return { tolak: 'Nama sumber "' + panjang.slice(0, 20) + '…" terlalu panjang (paling banyak ' + BC_BATAS.sumber + ' huruf)' };
  const kembar = sumber.find((s, i) => sumber.findIndex((x) => x.toLowerCase() === s.toLowerCase()) !== i); if (kembar) return { tolak: 'Sumber "' + kembar + '" tertulis dua kali' };
  const wilayah = bcBersih(I.wilayah === undefined ? A.wilayah : I.wilayah); if (wilayah.length > BC_BATAS.wilayah) return { tolak: 'Wilayah paling banyak ' + BC_BATAS.wilayah + ' huruf' };
  const lama = bcDok(BC_ATUR_ID) || {};
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, lama, { id: BC_ATUR_ID, tanggal: w.tanggal, jam: w.jam, minPemasok: min, hariMinggu: hari, tanggalBulan: tgl, potongMutu, sumber, wilayah }) }],
    patch: { aturBd: null, kabar: 'Setelan banding pemasok tersimpan — minimal ' + min + ' pemasok · pengingat tiap ' + bcNama(BC_HARI, hari) + ' & tanggal ' + tgl
      + ' · potongan mutu ' + (BC_TANDA.some(([id]) => potongMutu[id] > 0) ? BC_TANDA.filter(([id]) => potongMutu[id] > 0).map(([id, nm]) => nm.split(' ')[0] + ' ' + RP(potongMutu[id]) + '/kg').join(', ') : 'belum diatur (Rp0)'), kabarAwas: false } };
}

// ==================== CATATAN: tawaran & acuan ====================
/** Dokumen satu bulan (aturanToko/banding-YYYY-MM) atau null. */
export const bcDokBulan = (bulan) => bcDok(BC_DOK(bulan));
const bcUrut = (a, b) => String(a.tanggal).localeCompare(String(b.tanggal)) || String(a.dicatatPada || '').localeCompare(String(b.dicatatPada || '')) || String(a.id).localeCompare(String(b.id));
/** Semua entri (tawaran & acuan) bertanggal dari..sampai (inklusif), lama → baru. Entri rusak (tanpa harga / tanggal) dilewati dan DIHITUNG. */
export function bcEntri(dari, sampai) {
  const out = []; let rusak = 0;
  cacheMentah('aturan').forEach((d) => { if (!d || String(d.id).indexOf(BC_AWALAN) !== 0 || !Array.isArray(d.entri)) return;
    d.entri.forEach((e) => { if (!e || !bcIsoSah(e.tanggal) || !(Number(e.hargaPerKg) > 0) || (e.jenis !== 'tawaran' && e.jenis !== 'acuan')) { rusak += 1; return; }
      if ((dari && e.tanggal < dari) || (sampai && e.tanggal > sampai)) return; out.push(Object.assign({}, e, { hargaPerKg: Math.round(Number(e.hargaPerKg)), ongkirPerKg: Math.round(Number(e.ongkirPerKg) || 0) })); }); });
  out.sort(bcUrut); out.rusak = rusak; return out;
}
/** Kalimat satu entri: "Tawaran 21 Nov · Pemasok X · IR64 (merek Y) · Rp12.900/kg + ongkir Rp150" / "Acuan 21 Nov · Panel Harga Bapanas · grosir medium · Rp13.100/kg". */
export function bcTeks(e) {
  if (!e) return ''; const tgl = tanggalPendek(e.tanggal).replace(/ \d{4}$/, '');
  if (e.jenis === 'acuan') return 'Acuan ' + tgl + ' · ' + e.sumber + ' · ' + bcNama(BC_TINGKAT, e.tingkat).split(' /')[0] + ' ' + e.mutu + (e.wilayah ? ' · ' + e.wilayah : '') + ' · ' + RP(e.hargaPerKg) + '/kg' + (e.otomatis ? ' (tarik otomatis)' : '');
  return 'Tawaran ' + tgl + ' · ' + e.pemasok + ' · ' + e.kelas + (e.merek ? ' (merek ' + e.merek + ')' : '') + ' · ' + RP(e.hargaPerKg) + '/kg'
    + (e.sampaiToko ? ' sampai toko' : Number(e.ongkirPerKg) > 0 ? ' + ongkir ' + RP(e.ongkirPerKg) + '/kg' : ' (ongkos belum diketahui)');
}
/**
 * SATU penjaga isian untuk owner, tablet, dan saat owner menyetujui usul. jenis 'tawaran' | 'acuan'; isi = ketikan; kini = tanggal hari ini (ISO).
 * → { tolak } | { data } (bentuk entri tanpa id & cap penulis). Tanggal: hari ini atau mundur paling lama 62 hari (salah ketik tahun ditolak).
 */
export function bcBacaIsi(jenis, isi, kini) {
  const I = isi || {}; const iso = String(kini || '').slice(0, 10); if (jenis !== 'tawaran' && jenis !== 'acuan') return { tolak: 'Pilih dulu: harga tawaran pemasok atau harga acuan resmi' };
  const tanggal = bcKosong(I.tanggal) ? iso : String(I.tanggal).trim();
  if (!bcIsoSah(tanggal)) return { tolak: 'Tanggal harganya tidak terbaca (tulis tahun-bulan-tanggal)' };
  if (tanggal > iso) return { tolak: 'Tanggal harga ' + tanggalPendek(tanggal) + ' belum terjadi' };
  if (bcHariKe(iso) - bcHariKe(tanggal) > BC_BATAS.mundur) return { tolak: 'Tanggal harga ' + tanggalPendek(tanggal) + ' sudah lebih dari ' + BC_BATAS.mundur + ' hari lalu — periksa ketikannya' };
  const h = bcRupiah(I.hargaPerKg); if (h === null) return { tolak: 'Harga per kg belum diisi' };
  if (!(Number.isInteger(h) && h >= BC_BATAS.hargaMin && h <= BC_BATAS.hargaMaks)) return { tolak: 'Harga per kg ditulis rupiah bulat ' + RP(BC_BATAS.hargaMin) + '–' + RP(BC_BATAS.hargaMaks) + ' (mis. 12900 atau 12.900) — bukan harga per karung' };
  const catatan = bcBersih(I.catatan); if (catatan.length > BC_BATAS.catatan) return { tolak: 'Catatan paling banyak ' + BC_BATAS.catatan + ' huruf' };
  if (jenis === 'tawaran') {
    const pemasok = bcBersih(I.pemasok); const kelas = bcBersih(I.kelas); const merek = bcBersih(I.merek);
    if (pemasok.length < 2) return { tolak: 'Nama pemasok yang menawarkan belum diisi' };
    if (pemasok.length > BC_BATAS.pemasok) return { tolak: 'Nama pemasok paling banyak ' + BC_BATAS.pemasok + ' huruf' };
    if (!bcPemasokSungguhan(pemasok)) return { tolak: '"' + pemasok + '" nama yang dipakai sistem, bukan pemasok' };
    if (kelas.length < 2) return { tolak: 'Kelas / jenis berasnya belum diisi — banding dilakukan per kelas (mis. IR64 medium)' };
    if (kelas.length > BC_BATAS.kelas || merek.length > BC_BATAS.merek) return { tolak: 'Kelas & merek masing-masing paling banyak ' + BC_BATAS.kelas + ' huruf' };
    const sampaiToko = I.sampaiToko === true || I.sampaiToko === 'ya';
    const o = sampaiToko ? 0 : bcRupiah(I.ongkirPerKg); const ongkir = o === null ? 0 : o;
    if (!(Number.isInteger(ongkir) && ongkir >= 0 && ongkir <= BC_BATAS.ongkirMaks)) return { tolak: 'Ongkos kirim per kg ditulis rupiah bulat 0–' + RP(BC_BATAS.ongkirMaks) + ' (kosong = belum diketahui)' };
    return { data: { jenis, tanggal, pemasok, kelas, merek, hargaPerKg: h, ongkirPerKg: ongkir, sampaiToko, ongkirDiketahui: sampaiToko || o !== null, catatan } };
  }
  const A = bcAtur(); const sumber = bcBersih(I.sumber); const tingkat = String(I.tingkat || ''); const mutu = String(I.mutu || ''); const wilayah = bcKosong(I.wilayah) ? A.wilayah : bcBersih(I.wilayah);
  if (!sumber) return { tolak: 'Sumber harga acuan belum dipilih' };
  if (sumber.length > BC_BATAS.sumber) return { tolak: 'Nama sumber paling banyak ' + BC_BATAS.sumber + ' huruf' };
  if (!BC_TINGKAT.some((x) => x[0] === tingkat)) return { tolak: 'Tingkat harganya belum dipilih: produsen, grosir, atau eceran' };
  if (!BC_MUTU.some((x) => x[0] === mutu)) return { tolak: 'Mutu berasnya belum dipilih: medium atau premium' };
  if (wilayah.length > BC_BATAS.wilayah) return { tolak: 'Wilayah paling banyak ' + BC_BATAS.wilayah + ' huruf' };
  return { data: { jenis, tanggal, sumber, tingkat, mutu, wilayah, hargaPerKg: h, catatan, otomatis: I.otomatis === true } };
}
const bcSama = (a, b) => a.jenis === b.jenis && a.tanggal === b.tanggal && Number(a.hargaPerKg) === Number(b.hargaPerKg)
  && (a.jenis === 'tawaran' ? kunciPelanggan(a.pemasok) === kunciPelanggan(b.pemasok) && bcBersih(a.kelas).toLowerCase() === bcBersih(b.kelas).toLowerCase()
    : bcBersih(a.sumber).toLowerCase() === bcBersih(b.sumber).toLowerCase() && a.tingkat === b.tingkat && a.mutu === b.mutu);
/** Dokumen bulan dengan satu entri ditambahkan. tambahan = { oleh, dariUsul } (cap penulis asli). */
function bcTambahEntri(data, w, tambahan) {
  const bulan = data.tanggal.slice(0, 7); const lama = bcDokBulan(bulan) || {}; const entri = Array.isArray(lama.entri) ? lama.entri : [];
  const kembar = entri.find((e) => e && bcSama(e, data)); if (kembar) return { tolak: 'Sudah tercatat: ' + bcTeks(kembar) + ' — tidak dicatat dua kali' };
  if (entri.length >= BC_BATAS.entriBulan) return { tolak: 'Catatan banding ' + bulan + ' sudah ' + entri.length + ' baris (batas satu dokumen) — hapus yang salah dulu' };
  const e = Object.assign({ id: 'bd' + w.idUnik() }, data, { dicatatTanggal: w.tanggal, dicatatJam: w.jam, dicatatPada: w.kini }, tambahan || {});
  return { e, dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, lama, { id: BC_DOK(bulan), bulan, tanggal: w.tanggal, jam: w.jam, entri: entri.concat([e]) }) }] };
}
/** Owner mencatat langsung. → { dokumen, patch } | { tolak }. */
export function susunCatatBanding(jenis, isi, w, oleh) {
  const B = bcBacaIsi(jenis, isi, w.tanggal); if (B.tolak) return B;
  const T = bcTambahEntri(B.data, w, { oleh: bcBersih(oleh) || 'Owner' }); if (T.tolak) return T;
  return { dokumen: T.dokumen, patch: { bdCatat: null, kabar: 'Dicatat — ' + bcTeks(T.e), kabarAwas: false } };
}
/** Hapus satu entri (owner) dari dokumen bulannya. */
export function susunHapusBanding(id, w) {
  const d = cacheMentah('aturan').find((x) => x && String(x.id).indexOf(BC_AWALAN) === 0 && Array.isArray(x.entri) && x.entri.some((e) => e && String(e.id) === String(id)));
  if (!d) return { tolak: 'Catatan banding itu tidak ditemukan (mungkin sudah dihapus)' };
  const e = d.entri.find((x) => x && String(x.id) === String(id));
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, d, { tanggal: w.tanggal, jam: w.jam, entri: d.entri.filter((x) => !(x && String(x.id) === String(id))) }) }],
    patch: { bdYakinHapus: null, kabar: 'Dihapus — ' + bcTeks(e), kabarAwas: false } };
}
/** Tanda "bulan ini sudah dibanding" (ritual bulanan A95). catatan = keputusan / temuan singkat (boleh kosong). Bulan tidak boleh di depan bulan berjalan. */
export function susunTandaiBanding(bulan, catatan, w) {
  const b = String(bulan || '').slice(0, 7); if (!/^\d{4}-\d{2}$/.test(b)) return { tolak: 'Bulan tidak dikenal' };
  if (b > String(w.tanggal).slice(0, 7)) return { tolak: 'Bulan ' + b + ' belum berjalan' };
  const c = bcBersih(catatan); if (c.length > BC_BATAS.catatan) return { tolak: 'Catatan paling banyak ' + BC_BATAS.catatan + ' huruf' };
  const lama = bcDokBulan(b) || {};
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, lama, { id: BC_DOK(b), bulan: b, tanggal: w.tanggal, jam: w.jam, entri: Array.isArray(lama.entri) ? lama.entri : [], dibanding: { tanggal: w.tanggal, jam: w.jam, catatan: c } }) }],
    patch: { bdTandai: null, kabar: 'Banding pemasok ' + b + ' ditandai sudah dibaca' + (c ? ' — ' + c : ''), kabarAwas: false } };
}
/** Tanda banding satu bulan ({ tanggal, jam, catatan }) atau null. */
export const bcDibanding = (bulan) => { const d = bcDokBulan(bulan); return d && d.dibanding && typeof d.dibanding === 'object' && bcIsoSah(d.dibanding.tanggal) ? d.dibanding : null; };

// ==================== USUL DARI TABLET (Penjaga laci, rules v21 stafUsulBanding) ====================
const bcMilik = (m, akun) => !!akun && String(m.mintaUid || '') === String(akun.uid || '');
/**
 * Usul harga tawaran / acuan dari tablet → SATU dokumen persetujuan: tindakan 'hargaBanding', status 'menunggu', jenis, hargaPerKg (bulat 1.000–100.000),
 * teks (kalimat, ≤ 300 huruf), mintaUid = penulis, tanpa kolom keputusan — bentuk yang ditegakkan rules v21. Isian lain di peta `isi` (dicek ulang owner).
 */
export function bcSusunUsul(jenis, isi, akun, w) {
  if (!akun || !akun.uid) return { tolak: 'Belum masuk — usul butuh orang yang jaga' };
  const B = bcBacaIsi(jenis, Object.assign({}, isi || {}, { otomatis: false }), w.tanggal); if (B.tolak) return B;
  const teks = bcTeks(B.data).slice(0, BC_BATAS.teks);
  const ada = cacheMentah('persetujuan').find((m) => m && m.tindakan === BC_TINDAKAN && (m.status || 'menunggu') === 'menunggu' && bcMilik(m, akun) && bcSama(Object.assign({}, m.isi || {}, { jenis: m.jenis, hargaPerKg: m.hargaPerKg }), B.data));
  if (ada) return { tolak: 'Usul yang sama (jam ' + (ada.jam || '?') + ') masih menunggu owner — tidak dikirim dua kali' };
  const isiSimpan = Object.assign({}, B.data); delete isiSimpan.jenis; delete isiSimpan.hargaPerKg; delete isiSimpan.otomatis;
  return { dokumen: [{ koleksi: 'persetujuan', data: { id: 'ub' + w.idUnik(), tindakan: BC_TINDAKAN, status: 'menunggu', jenis, hargaPerKg: B.data.hargaPerKg, teks, isi: isiSimpan,
    mintaUid: String(akun.uid), dari: String(akun.nama || ''), peran: String(akun.peran || ''), tanggal: w.tanggal, jam: w.jam, pada: w.kini } }],
    patch: { kabar: 'Usul terkirim ke owner — ' + teks, kabarAwas: false } };
}
/** Kalimat usul di papan Persetujuan (dihitung ulang dari isinya, bukan teks kiriman). */
export function bcTeksUsul(m) { const B = bcBacaIsi(m && m.jenis, Object.assign({}, (m && m.isi) || {}, { hargaPerKg: m && m.hargaPerKg }), (m && m.tanggal) || ''); return B.data ? bcTeks(B.data) : String((m && m.teks) || '') + ' (isiannya tidak sah: ' + B.tolak + ')'; }
/**
 * Owner MENYETUJUI usul → catatannya ditulis (isian dicek ULANG terhadap hari ini) atas nama yang mengusulkan + persetujuan "disetujui" (ditulis pemanggil).
 * → { dokumen, kabar } | { tolak }.
 */
export function bcPasangUsul(m, w) {
  const B = bcBacaIsi(m.jenis, Object.assign({}, m.isi || {}, { hargaPerKg: m.hargaPerKg, otomatis: false }), w.tanggal); if (B.tolak) return { tolak: 'Usul tidak bisa dipasang: ' + B.tolak };
  const T = bcTambahEntri(B.data, w, { oleh: bcBersih(m.dari) || 'tablet', dariUsul: String(m.id) }); if (T.tolak) return T;
  return { dokumen: T.dokumen, kabar: bcTeks(T.e) };
}
/** Usul milik akun ini (tablet): menunggu + 10 terakhir yang sudah diputus. */
export function bcUsulSaya(akun) {
  const semua = cacheMentah('persetujuan').filter((m) => m && m.tindakan === BC_TINDAKAN && bcMilik(m, akun)).slice().sort((a, b) => String(b.pada || b.tanggal || '').localeCompare(String(a.pada || a.tanggal || '')));
  const baris = (m) => ({ id: String(m.id), teks: m.teks || '', tanggal: m.tanggal || '', jam: m.jam || '', status: m.status || 'menunggu', alasan: m.alasanTolak || '' });
  return { menunggu: semua.filter((m) => (m.status || 'menunggu') === 'menunggu').map(baris), riwayat: semua.filter((m) => m.status && m.status !== 'menunggu').slice(0, 10).map(baris) };
}

// ==================== TARIK OTOMATIS (fungsi server → aturanToko/acuanTarik) ====================
/**
 * Hasil tarik otomatis terakhir: { ada, pada, status 'ok' | 'gagal', pesan, sumber, harga: [{ nama, mutu, tingkat, hargaPerKg, tanggal, wilayah, dipakai }] }.
 * dipakai = sudah ada entri acuan yang sama (tanggal, sumber, tingkat, mutu, harga). Fungsi belum pernah jalan → ada false.
 */
export function bcTarik() {
  const d = bcDok(BC_TARIK_ID); if (!d) return { ada: false, harga: [], kalimat: 'Tarik otomatis belum pernah jalan — fungsi server tarikAcuan belum dipasang (functions/pasang.sh) atau belum tiba jadwalnya.' };
  const sumber = bcBersih(d.sumber) || 'Panel Harga Bapanas'; const semua = bcEntri('', '');
  const harga = (Array.isArray(d.harga) ? d.harga : []).filter((x) => x && Number.isInteger(Number(x.hargaPerKg)) && Number(x.hargaPerKg) > 0 && BC_MUTU.some((m) => m[0] === x.mutu) && BC_TINGKAT.some((t) => t[0] === x.tingkat) && bcIsoSah(x.tanggal))
    .map((x) => { const h = { nama: bcBersih(x.nama).slice(0, 60), mutu: x.mutu, tingkat: x.tingkat, hargaPerKg: Number(x.hargaPerKg), tanggal: x.tanggal, wilayah: bcBersih(x.wilayah).slice(0, BC_BATAS.wilayah), sumber };
      return Object.assign(h, { dipakai: semua.some((e) => bcSama(e, Object.assign({ jenis: 'acuan' }, h))), tebakTingkat: x.tebakTingkat !== false }); });
  const status = d.status === 'ok' ? 'ok' : 'gagal';
  return { ada: true, pada: String(d.pada || ''), tanggal: String(d.tanggal || ''), status, pesan: bcBersih(d.pesan).slice(0, 300), sumber, harga,
    kalimat: status === 'ok' ? (harga.length ? harga.length + ' harga ditarik dari ' + sumber + ' (' + tanggalPendek(String(d.tanggal || '')) + ') — periksa, lalu Pakai yang benar.' : 'Tarik otomatis jalan tapi tidak menemukan harga beras medium / premium — ketik manual.')
      : 'Tarik otomatis GAGAL ' + tanggalPendek(String(d.tanggal || '')) + ': ' + (bcBersih(d.pesan) || 'tanpa keterangan') + ' — ketik manual.' };
}

// ==================== PENGINGAT (dibaca sistem-logika ssSumberPengingat) ====================
/** Pemasok yang PUNYA HARGA dalam rentang: kedatangan nyata (bukan stok awal / saldo pembuka / lahir buku) + harga tawaran. → { kunci: nama }. */
export function bcPemasokBerharga(dari, sampai) {
  const out = {};
  ambilSemuaBatch().forEach((b) => { if (!b || b.stokAwal || b.tutupBuku || b.lahirBuku || !bcPemasokSungguhan(b.pemasok) || !b.tanggal || b.tanggal < dari || b.tanggal > sampai) return;
    if (!(b.merkList || []).some((m) => m && Number(m.hargaPerKg) > 0)) return; out[kunciPelanggan(b.pemasok)] = bcBersih(b.pemasok); });
  bcEntri(dari, sampai).forEach((e) => { if (e.jenis === 'tawaran') { const k = kunciPelanggan(e.pemasok); if (!out[k]) out[k] = e.pemasok; } });
  return out;
}
/**
 * Sumber pengingat banding untuk hari iso: (1) MINGGUAN — minggu ini (Senin–Minggu) belum punya harga dari N pemasok → jatuh = hari setelan minggu ini;
 * (2) BULANAN — bulan lalu belum ditandai "sudah dibanding" → jatuh = tanggal setelan bulan ini, ditagih paling lama BC_SUSUL hari sesudahnya dan
 * hanya bila bulan lalu ada kedatangan / tawaran.
 */
export function bcSumberPengingat(iso) {
  const A = bcAtur(); const out = []; const senin = bcSenin(iso); const minggu = bcTambahHari(senin, 6);
  const P = bcPemasokBerharga(senin, minggu); const n = Object.keys(P).length; const jatuh = bcTambahHari(senin, (A.hariMinggu + 6) % 7);
  if (n < A.minPemasok) out.push({ id: 'banding|' + senin, jenis: 'banding', kunci: senin, teks: 'Catat harga ' + A.minPemasok + ' pemasok minggu ini (baru ' + n + ')', siapa: 'banding', jatuh, n: 0,
    ket: 'minggu ' + tanggalPendek(senin).replace(/ \d{4}$/, '') + '–' + tanggalPendek(minggu) + ' · kedatangan + harga tawaran · Harga & Pemasok › Banding' });
  const blnLalu = bcBulanGeser(iso.slice(0, 7), -1); const jatuhB = iso.slice(0, 7) + '-' + String(A.tanggalBulan).padStart(2, '0');
  const awalL = blnLalu + '-01'; const akhirL = bcTambahHari(iso.slice(0, 7) + '-01', -1);
  if (!bcDibanding(blnLalu) && iso >= bcTambahHari(jatuhB, -7) && bcHariKe(iso) - bcHariKe(jatuhB) <= BC_SUSUL && Object.keys(bcPemasokBerharga(awalL, akhirL)).length)
    out.push({ id: 'bandingBulan|' + blnLalu, jenis: 'bandingBulan', kunci: blnLalu, teks: 'Banding pemasok bulan ' + blnLalu.slice(5, 7) + '/' + blnLalu.slice(0, 4), siapa: 'banding', jatuh: jatuhB, n: 0,
      ket: 'urutkan modal sampai toko layak jual minimal ' + A.minPemasok + ' pemasok, lalu tandai sudah dibanding — Harga & Pemasok › Banding › Bulan' });
  return out;
}
/** Kartu kecil untuk Menu / Dasbor: minggu ini sudah berapa pemasok berharga. */
export function bcStatusMinggu(iso) {
  const A = bcAtur(); const senin = bcSenin(iso); const P = bcPemasokBerharga(senin, bcTambahHari(senin, 6)); const n = Object.keys(P).length;
  return { senin, n, min: A.minPemasok, cukup: n >= A.minPemasok, nama: Object.keys(P).map((k) => P[k]).sort((a, b) => a.localeCompare(b)),
    kalimat: n >= A.minPemasok ? n + ' pemasok punya harga minggu ini — cukup (minimal ' + A.minPemasok + ')' : 'Minggu ini baru ' + n + ' dari ' + A.minPemasok + ' pemasok yang punya harga — tanya & catat harga tawaran' };
}
export const bcHariIni = (kini) => hariIniIso(kini || new Date());
/** Jumlah usul banding dari tablet yang masih menunggu owner (diputus di Menu › Toko ini › Peran & persetujuan › Persetujuan). */
export const bcUsulMenunggu = () => cacheMentah('persetujuan').filter((m) => m && m.tindakan === BC_TINDAKAN && (m.status || 'menunggu') === 'menunggu').length;
