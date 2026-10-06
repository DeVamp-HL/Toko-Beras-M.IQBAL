// KELAS MUTU MEREK (putaran 30, owner 28 Sep 2026: pemasok mengganti nama merek walau barangnya sama — riwayat harga beli terputus tiap ganti nama).
// Peta & keputusan owner: docs/peta-harga-kelas.md. Kelas = nama WADAH (aturan wadah `daftar`; nama wadah yang juga merek karung = kelasnya sendiri)
// atau merek berbuku yang dipilih owner sebagai kelas. Dua macam kelas:
//   A. BERWADAH (IR64 Ascent/Elevate/Apex, IR42 Value/Select, …): karung tetap dibukukan per MEREK PEMASOK; peta merek → kelas cuma LAPISAN BACA
//      (dokumen aturanToko/kelasMerek { peta {merek: kelas}, asal {merek: 'owner'|'tebakan'}, kelasSendiri [] }, owner saja — rules v4 tidak berubah).
//   B. TANPA WADAH / KELAS SENDIRI (Ketan Putih, Beras Merah, …: sejak awal bukunya atas nama kelas): buku TETAP atas nama kelas, merek pemasok jadi
//      keterangan `merkPemasok` di baris batchMasuk (kolom baru per baris; mesin beku & cadangan mengabaikannya).
// Tidak ada pindah buku, modal tidak berubah. Harga lalu kelas MEMAKAI ULANG riwayatModal (stok-hpp-logika) — bukan sumber kebenaran ketiga.
// Tebakan kelas hanya dari tiga sumber: nama = nama wadah, catatan karung ber-`wadah`, resep wadah. Tidak dari harga, tidak dari jenis beras (petunjuk saja).
// Tanpa DOM; nama berawalan km (bundel uji satu lingkup). Dijaga alat-uji/uji_kelas_merek.py.
import { jenisUntukMerk } from '../mesin/pembantu.js';
import { cacheMentah, ambilWadahLiteran, ambilHargaKarung, petaBukuWadah, petaUkuran, ingatStokKarung } from '../data/toko.js';
import { RP } from '../inti/format.js';
import { aturWadah, wdTerbaru } from './jual-logika.js';
import { wbLiteranLangsung, wbSusunGantiNama } from './wadah-bernama-logika.js';
import { VR_PEMISAH, vrBatas } from './varian-logika.js';
import { riwayatModal } from './stok-hpp-logika.js';

export const KM_ID = 'kelasMerek';
const KM_BLN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
const kmBersih = (v) => String(v === undefined || v === null ? '' : v).replace(/\s+/g, ' ').trim();
const kmObj = (o) => (o && typeof o === 'object' && !Array.isArray(o) ? Object.assign({}, o) : {});
const kmUrut = (a, b) => String(a.tanggal || '').localeCompare(String(b.tanggal || '')) || String(a.jam || '').localeCompare(String(b.jam || '')) || (Number(a.batchId) || 0) - (Number(b.batchId) || 0);
const kmTgl = (t) => { const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(t || '')); return m ? Number(m[3]) + ' ' + KM_BLN[Number(m[2]) - 1] : String(t || ''); };
const kmBulan = (ym) => { const m = /^(\d{4})-(\d{2})$/.exec(String(ym || '')); return m ? KM_BLN[Number(m[2]) - 1] + ' ' + m[1] : String(ym || ''); };

/** Dokumen aturanToko/kelasMerek yang berlaku. Tanpa dokumen (cadangan lama) → semuanya kosong: tiap merek "belum dipetakan" / tebakan. */
export function kmPeta() {
  const d = cacheMentah('aturan').find((x) => String(x.id) === KM_ID) || null;
  return { peta: kmObj(d && d.peta), asal: kmObj(d && d.asal), kelasSendiri: d && Array.isArray(d.kelasSendiri) ? d.kelasSendiri.map(String) : [], ada: !!d };
}
/** Nama kelas tanpa wadah (bukunya atas nama kelas) → { nama: true }. */
export function kmKelasSendiri() { const out = {}; kmPeta().kelasSendiri.forEach((n) => { out[n] = true; }); return out; }
const kmWadah = () => { const out = {}; aturWadah().daftar.forEach((w) => { out[w] = true; }); return out; };
/** Nama beras berbuku karung (buku stok atau katalog per kg) tanpa buku khusus wadah & buku per ukuran — calon anggota / calon kelas. */
export function kmNamaBerbuku() {
  const bw = petaBukuWadah(); const uk = petaUkuran(); const out = {};
  Object.keys(ingatStokKarung()).forEach((m) => { out[m] = true; }); ambilHargaKarung().forEach((h) => { if (h.merk) out[String(h.merk)] = true; });
  return Object.keys(out).filter((m) => !bw[m] && !uk[m]).sort((a, b) => a.localeCompare(b));
}
/** Boleh jadi kelas? Nama wadah, atau merek berbuku; bukan varian ("X · Y"), bukan buku khusus / buku ukuran. */
export function kmBolehJadiKelas(nama) {
  const n = kmBersih(nama); if (!n) return { boleh: false, sebab: 'nama kelasnya kosong' };
  if (n.indexOf(VR_PEMISAH) >= 0) return { boleh: false, sebab: n + ' itu VARIAN — kelas harus nama induk / nama wadah' };
  if (petaBukuWadah()[n]) return { boleh: false, sebab: n + ' itu buku KHUSUS (isi wadah / karung sisihan / kemasan adukan) — bukan kelas' };
  if (petaUkuran()[n]) return { boleh: false, sebab: n + ' itu buku per ukuran — kelasnya ikut ' + petaUkuran()[n].induk };
  if (kmWadah()[n]) return { boleh: true, jenis: 'wadah' };
  if (kmNamaBerbuku().indexOf(n) >= 0) return { boleh: true, jenis: kmKelasSendiri()[n] ? 'sendiri' : 'merek' };
  return { boleh: false, sebab: n + ' tidak dikenal — kelas harus nama wadah atau merek yang sudah punya buku' };
}
/** Pil kelas: nama wadah (urutan kotak di toko), lalu kelas tanpa wadah, lalu merek berbuku lain yang bukan varian & tidak sedang dipetakan ke kelas lain. */
export function kmCalonKelas() {
  const P = kmPeta(); const sendiri = kmKelasSendiri(); const W = kmWadah(); const dipetakan = {}; Object.keys(P.peta).forEach((m) => { if (P.peta[m]) dipetakan[m] = true; });
  const out = aturWadah().daftar.map((w) => ({ nama: w, jenis: 'wadah' }));
  P.kelasSendiri.slice().sort((a, b) => a.localeCompare(b)).forEach((n) => { if (!W[n]) out.push({ nama: n, jenis: 'sendiri' }); });
  kmNamaBerbuku().forEach((m) => { if (!W[m] && !sendiri[m] && m.indexOf(VR_PEMISAH) < 0 && !dipetakan[m]) out.push({ nama: m, jenis: 'merek' }); });
  return out;
}
/** Tebakan kelas satu merek — tiga sumber saja, urut: nama = nama wadah · karung ber-wadah (catatan terbaru, belum dikembalikan) · resep wadah. '' = tidak ada petunjuk. */
export function kmTebak(merk) {
  const m = kmBersih(merk); const A = aturWadah(); if (!m) return '';
  if (A.daftar.indexOf(m) >= 0) return m;
  // putaran 39: catatan karung di belakang wadah aktif bernama kunci bukunya, merek pemasoknya di merkAsal
  const k = wdTerbaru(ambilWadahLiteran().filter((d) => (d.tipe === 'karung' || d.tipe === 'karungIsi') && !d.dikembalikan && (String(d.merk || '') === m || String(d.merkAsal || '') === m) && d.wadah && A.daftar.indexOf(String(d.wadah)) >= 0));
  if (k) return String(k.wadah);
  const r = A.daftar.find((W) => (A.resep[W] || []).some((x) => String(x.merk) === m)); return r || '';
}
/**
 * Kelas satu merek → { kelas, asal }. asal: 'wadah' (nama = nama wadah) · 'sendiri' (kelas tanpa wadah) · 'dipakai' (merek ini dipilih jadi kelas merek lain)
 * · 'owner' (dipetakan owner; kelas '' = sengaja tanpa kelas) · 'tebakan' (peta menyimpan tebakan yang ikut Simpan barang masuk, atau tebakan hidup) · '' (tidak ada).
 */
export function kmKelasMerk(merk) {
  const m = kmBersih(merk); if (!m) return { kelas: '', asal: '' };
  if (kmWadah()[m]) return { kelas: m, asal: 'wadah' };
  const P = kmPeta(); if (P.kelasSendiri.indexOf(m) >= 0) return { kelas: m, asal: 'sendiri' };
  if (Object.prototype.hasOwnProperty.call(P.peta, m)) return { kelas: kmBersih(P.peta[m]), asal: P.asal[m] === 'tebakan' ? 'tebakan' : 'owner' };
  if (Object.keys(P.peta).some((x) => kmBersih(P.peta[x]) === m)) return { kelas: m, asal: 'dipakai' };
  const t = kmTebak(m); return { kelas: t, asal: t ? 'tebakan' : '' };
}
/** Merek yang belum dikonfirmasi owner = asal 'tebakan' atau '' (bukan wadah, bukan kelas sendiri, bukan dipakai). */
export const kmTerisi = (asal) => asal === 'owner' || asal === 'wadah' || asal === 'sendiri' || asal === 'dipakai';
/** Daftar "Kelas mutu · N/M terisi": tiap merek berbuku + kelas & asalnya + petunjuk jenis beras; usulan kelas tanpa wadah = literan langsung yang belum ditandai. */
export function kmDaftar() {
  const sendiri = kmKelasSendiri(); const W = kmWadah(); const L = wbLiteranLangsung().daftar;
  const baris = kmNamaBerbuku().map((m) => { const K = kmKelasMerk(m); return { merk: m, kelas: K.kelas, asal: K.asal, petunjuk: jenisUntukMerk(m) || '', sendiri: !!sendiri[m], wadah: !!W[m], varian: m.indexOf(VR_PEMISAH) >= 0 }; });
  const usulSendiri = baris.filter((b) => !b.wadah && !b.sendiri && !b.varian && L.indexOf(b.merk) >= 0 && !(b.kelas && b.asal === 'owner')).map((b) => b.merk);
  return { baris, terisi: baris.filter((b) => kmTerisi(b.asal)).length, total: baris.length, belumKonfirmasi: baris.filter((b) => !kmTerisi(b.asal)).map((b) => b.merk), usulSendiri };
}
/** Dokumen aturanToko/kelasMerek utuh (peta & asal disalin, kunci lain utuh). */
export function kmDokMentah(P, w) {
  return { koleksi: 'aturanToko', data: { id: KM_ID, tanggal: w.tanggal, jam: w.jam, diubahPada: w.kini, peta: kmObj(P.peta), asal: kmObj(P.asal), kelasSendiri: (P.kelasSendiri || []).slice() } };
}
/** Owner memetakan satu merek → kelas ('' = tanpa kelas, menimpa tebakan). → { tolak } | { dokumen, patch }. */
export function susunKelasMerk(merk, kelas, w) {
  const m = kmBersih(merk); const k = kmBersih(kelas);
  if (!m) return { tolak: 'Nama mereknya kosong' };
  if (kmWadah()[m]) return { tolak: m + ' adalah nama WADAH — kelasnya dirinya sendiri, tidak perlu dipetakan' };
  if (petaBukuWadah()[m] || petaUkuran()[m]) return { tolak: m + ' itu buku khusus / buku per ukuran — kelasnya ikut induknya' };
  if (kmNamaBerbuku().indexOf(m) < 0) return { tolak: m + ' tidak dikenal di buku maupun katalog — kelas dipilih sesudah namanya muncul (Barang masuk / Katalog)' };
  const P = kmPeta();
  if (P.kelasSendiri.indexOf(m) >= 0) return { tolak: m + ' sudah ditandai KELAS tanpa wadah — lepaskan tandanya dulu kalau mau memetakannya ke kelas lain' };
  if (k) { if (k === m) return { tolak: m + ' tidak bisa jadi kelas dirinya sendiri — biarkan tanpa kelas, atau tandai "nama ini kelas, bukan merek"' }; const b = kmBolehJadiKelas(k); if (!b.boleh) return { tolak: b.sebab }; }
  const kini = kmKelasMerk(m); if (kini.asal === 'owner' && kini.kelas === k) return { tolak: m + ' sudah ' + (k ? 'berkelas ' + k : 'ditandai tanpa kelas') };
  P.peta[m] = k; P.asal[m] = 'owner';
  return { dokumen: [kmDokMentah(P, w)], patch: { kmUbah: null, kabar: k ? m + ' → kelas ' + k + '. Harga lalu kelas & kartu Per kelas ikut; buku stok ' + m + ' tidak berubah.' : m + ' tanpa kelas — harga lalunya dari merek itu sendiri saja.', kabarAwas: false } };
}
/** Tandai / lepas satu merek sebagai KELAS tanpa wadah (bukunya atas nama itu; merek pemasok jadi keterangan). */
export function susunKelasSendiri(nama, nyala, w) {
  const n = kmBersih(nama); if (!n) return { tolak: 'Pilih namanya dulu' };
  if (kmWadah()[n]) return { tolak: n + ' adalah nama WADAH — sudah kelas dengan sendirinya' };
  if (n.indexOf(VR_PEMISAH) >= 0) return { tolak: n + ' itu varian — tidak bisa jadi kelas' };
  if (petaBukuWadah()[n] || petaUkuran()[n]) return { tolak: n + ' itu buku khusus / buku per ukuran — bukan kelas' };
  if (kmNamaBerbuku().indexOf(n) < 0) return { tolak: n + ' tidak dikenal di buku maupun katalog' };
  const P = kmPeta(); const ada = P.kelasSendiri.indexOf(n) >= 0;
  if (!!nyala === ada) return { tolak: n + (ada ? ' sudah' : ' belum') + ' ditandai kelas' };
  if (nyala) { P.kelasSendiri = P.kelasSendiri.concat([n]).sort((a, b) => a.localeCompare(b)); delete P.peta[n]; delete P.asal[n]; }
  else { if (Object.keys(P.peta).some((x) => kmBersih(P.peta[x]) === n)) return { tolak: n + ' masih dipakai sebagai kelas merek lain — pindahkan merek itu dulu' }; P.kelasSendiri = P.kelasSendiri.filter((x) => x !== n); }
  return { dokumen: [kmDokMentah(P, w)], patch: { kabar: n + (nyala ? ' ditandai KELAS tanpa wadah: kedatangan merek pemasok apa pun yang dipilih ke kelas ini dibukukan atas nama ' + n + ', merek pemasoknya dicatat sebagai keterangan.' : ' tidak lagi ditandai kelas — kembali jadi merek biasa.'), kabarAwas: false } };
}
/** Dokumen peta dari beberapa pasangan {merk, kelas, asal} (Simpan barang masuk: tebakan yang dibiarkan ikut ditulis SEBAGAI tebakan). null = tidak ada yang berubah. */
export function kmDokKelas(pasangan, w) {
  const P = kmPeta(); let ubah = false;
  (pasangan || []).forEach((x) => { const m = kmBersih(x && x.merk); const k = kmBersih(x && x.kelas); const asal = x && x.asal === 'tebakan' ? 'tebakan' : 'owner';
    if (!m || kmWadah()[m] || P.kelasSendiri.indexOf(m) >= 0) return;
    const ada = Object.prototype.hasOwnProperty.call(P.peta, m);
    if (ada && P.asal[m] !== 'tebakan' && asal === 'tebakan') return;   // keputusan owner tidak ditimpa tebakan
    if (ada && kmBersih(P.peta[m]) === k && (P.asal[m] === 'tebakan') === (asal === 'tebakan')) return;
    if (!ada && !k && asal === 'tebakan') return;   // tidak ada petunjuk & tidak dipilih: tidak ditulis
    P.peta[m] = k; P.asal[m] = asal; ubah = true; });
  return ubah ? kmDokMentah(P, w) : null;
}
/** Ganti nama WADAH: peta kelas ikut (merek berkelas nama lama → nama baru) di kiriman yang sama; nama baru yang sudah jadi kelas lain ditolak. */
export function kmSusunGantiNamaWadah(lama, baru, w) {
  const L = kmBersih(lama); const B = kmBersih(baru); const P = kmPeta();
  const r = wbSusunGantiNama(L, B, w); if (r.tolak) return r;   // aturan ganti nama yang ada dulu (nama wadah lain, stok minus, …)
  if (P.kelasSendiri.indexOf(B) >= 0 || Object.keys(P.peta).some((x) => kmBersih(P.peta[x]) === B)) return { tolak: B + ' sudah jadi kelas lain (merek pemasok dipetakan ke sana) — pilih nama lain' };
  const ikut = Object.keys(P.peta).filter((x) => kmBersih(P.peta[x]) === L);
  if (ikut.length) { ikut.forEach((x) => { P.peta[x] = B; }); r.dokumen.push(kmDokMentah(P, w)); r.patch = Object.assign({}, r.patch, { kabar: r.patch.kabar + ' Kelas ' + ikut.length + ' merek (' + ikut.join(', ') + ') ikut jadi ' + B + '.' }); }
  return r;
}
/** Anggota satu kelas: kelas itu sendiri (kedatangan lama atas nama kelas) + merek yang kelasnya ke sana (owner / tebakan). */
export function kmAnggota(kelas) {
  const k = kmBersih(kelas); if (!k) return []; const semua = {}; kmNamaBerbuku().forEach((m) => { semua[m] = true; }); Object.keys(kmPeta().peta).forEach((m) => { semua[m] = true; });
  return [k].concat(Object.keys(semua).filter((m) => m !== k && kmKelasMerk(m).kelas === k).sort((a, b) => a.localeCompare(b)));
}
/** Riwayat kedatangan satu kelas = gabungan riwayatModal tiap anggota, kedatangan nyata saja (fondasi & bal tidak ikut), lama → baru. */
export function kmRiwayatKelas(kelas) {
  const out = []; kmAnggota(kelas).forEach((m) => { riwayatModal(m).forEach((r) => { if (r.jenis !== 'kedatangan' || r.fondasi) return; out.push(Object.assign({}, r, { merk: m, merkPemasok: String(r.merkPemasok || '') })); }); });
  return out.sort(kmUrut);
}
/** Harga lalu satu KELAS: pemasok yang dipilih diutamakan, pemasok lain di sebelahnya; batch yang sedang dikoreksi tidak dipakai. null = kelas belum punya kedatangan. */
export function kmHargaLaluKelas(kelas, pemasok, kecualiBatchId) {
  const p = kmBersih(pemasok); const semua = kmRiwayatKelas(kelas).filter((r) => !kecualiBatchId || String(r.batchId) !== String(kecualiBatchId)); if (!semua.length) return null;
  const bentuk = (r) => ({ merk: r.merk, merkPemasok: r.merkPemasok, harga: Math.round(r.hargaPerKg), tanggal: r.tanggal, tanggalTeks: kmTgl(r.tanggal), pemasok: r.pemasok });
  const per = {}; semua.forEach((r) => { per[kmBersih(r.pemasok)] = r; });   // terbaru menang (urut lama → baru)
  const utama = (p && per[p]) || semua[semua.length - 1];
  const lain = Object.keys(per).filter((x) => x !== kmBersih(utama.pemasok)).map((x) => per[x]).sort((a, b) => kmUrut(b, a)).slice(0, 2).map(bentuk);
  return Object.assign({ kelas: kmBersih(kelas), dariPemasokDipilih: !!(p && per[p]), lain }, bentuk(utama));
}
/** Harga lalu satu MEREK: angka = mesin (hargaTerakhirPerKg, urutan id), tanggal & pemasok dari riwayatModal; saat koreksi (kecualiBatchId) = kedatangan sebelum batch itu. */
export function kmHargaLaluMerk(merk, kecualiBatchId) {
  const m = kmBersih(merk); if (!m) return null; const riw = riwayatModal(m).filter((r) => r.jenis === 'kedatangan' && (!kecualiBatchId || String(r.batchId) !== String(kecualiBatchId)));
  const st = ingatStokKarung()[m]; const akhir = riw[riw.length - 1] || null;
  const harga = kecualiBatchId ? (akhir ? Math.round(akhir.hargaPerKg) : 0) : (st ? Math.round(st.hargaTerakhirPerKg || 0) : 0);
  if (!(harga > 0)) return null;
  return { merk: m, harga, tanggal: akhir ? akhir.tanggal : '', tanggalTeks: akhir ? kmTgl(akhir.tanggal) : '', pemasok: akhir ? akhir.pemasok : '', fondasi: !!(akhir && akhir.fondasi), merkPemasok: akhir ? String(akhir.merkPemasok || '') : '' };
}
/** Arah harga yang diketik vs harga lalu: ▲ naik Rp… / ▼ turun Rp… / = sama. */
export function kmArah(harga, lalu) {
  const h = Math.round(Number(harga) || 0); const l = Math.round(Number(lalu) || 0); if (!(h > 0) || !(l > 0)) return { arah: '', selisih: 0, persen: 0, teks: '' };
  const d = h - l; const p = Math.round(Math.abs(d) / l * 1000) / 10;
  return { arah: d > 0 ? 'naik' : d < 0 ? 'turun' : 'sama', selisih: d, persen: p, teks: d > 0 ? '▲ naik ' + RP(d) + ' dari lalu' : d < 0 ? '▼ turun ' + RP(-d) + ' dari lalu' : '= sama dengan harga lalu' };
}
/** Kalimat lunak merek baru yang harganya beda > batasVarian dari harga lalu kelasnya (TIDAK memblokir simpan). '' = wajar. */
export function kmKalimatKelas(harga, laluKelas) {
  if (!laluKelas || !(Number(harga) > 0)) return ''; const A = kmArah(harga, laluKelas.harga); const batas = vrBatas();
  return A.persen > batas + 1e-9 ? 'beda ' + String(A.persen).replace('.', ',') + ' % dari kelas ' + laluKelas.kelas + ' (lalu ' + RP(laluKelas.harga) + ' · ' + laluKelas.merk + (laluKelas.merkPemasok ? ' (' + laluKelas.merkPemasok + ')' : '') + ' · ' + laluKelas.tanggalTeks + ' · ' + laluKelas.pemasok + ') — kelasnya benar?' : '';
}
/** Kartu "Harga beli per kelas": tiap kedatangan anggota satu garis, rata-rata tertimbang kg per bulan ▲▼, batas periode data DISEBUT (per kuartal hanya bila ≥ 2 kuartal berisi). */
export function kmKartuKelas() {
  const P = kmPeta(); const W = aturWadah().daftar; const nama = W.slice(); P.kelasSendiri.forEach((n) => { if (nama.indexOf(n) < 0) nama.push(n); });
  Object.keys(P.peta).forEach((m) => { const k = kmBersih(P.peta[m]); if (k && nama.indexOf(k) < 0) nama.push(k); });
  let dari = '', sampai = ''; const bulanSemua = {}; const kuartalSemua = {};
  const kartu = nama.map((k) => { const riw = kmRiwayatKelas(k); const anggota = kmAnggota(k); const maks = Math.max(...riw.map((r) => r.hargaPerKg), 1);
    const baris = riw.map((r, i) => { const lalu = i > 0 ? riw[i - 1].hargaPerKg : 0; const p = lalu > 0 ? Math.round((r.hargaPerKg - lalu) / lalu * 100) : 0;
      if (!dari || r.tanggal < dari) dari = r.tanggal; if (r.tanggal > sampai) sampai = r.tanggal; bulanSemua[String(r.tanggal).slice(0, 7)] = 1; kuartalSemua[String(r.tanggal).slice(0, 4) + '-K' + (Math.floor((Number(String(r.tanggal).slice(5, 7)) - 1) / 3) + 1)] = 1;
      return { tanggal: r.tanggal, tanggalTeks: kmTgl(r.tanggal), merk: r.merk, merkPemasok: r.merkPemasok, pemasok: r.pemasok, harga: Math.round(r.hargaPerKg), hpp: Math.round(r.hppPerKg), kg: r.totalKg, lebar: Math.round(r.hargaPerKg / maks * 1000) / 10, koreksi: !!r.dikoreksi, lonjak: i > 0 && p !== 0 ? (p > 0 ? '▲' : '▼') + Math.abs(p) + ' %' : '' }; });
    const per = {}; riw.forEach((r) => { const b = String(r.tanggal).slice(0, 7); per[b] = per[b] || { kg: 0, nilai: 0, n: 0 }; per[b].kg += r.totalKg; per[b].nilai += r.hargaPerKg * r.totalKg; per[b].n += 1; });
    const perBulan = Object.keys(per).sort().map((b, i, arr) => { const rata = per[b].kg > 0 ? per[b].nilai / per[b].kg : 0; const lalu = i > 0 && per[arr[i - 1]].kg > 0 ? per[arr[i - 1]].nilai / per[arr[i - 1]].kg : 0; const p = lalu > 0 ? Math.round((rata - lalu) / lalu * 1000) / 10 : 0;
      return { bulan: b, bulanTeks: kmBulan(b), rata: Math.round(rata), kg: Math.round(per[b].kg * 100) / 100, n: per[b].n, arah: i === 0 ? '' : p > 0 ? 'naik' : p < 0 ? 'turun' : 'sama', persen: Math.abs(p), teks: i === 0 ? 'bulan pertama berdata' : p > 0 ? '▲ ' + String(p).replace('.', ',') + ' % dari ' + kmBulan(arr[i - 1]) : p < 0 ? '▼ ' + String(-p).replace('.', ',') + ' % dari ' + kmBulan(arr[i - 1]) : '= sama dengan ' + kmBulan(arr[i - 1]) }; });
    const jenis = W.indexOf(k) >= 0 ? 'wadah' : P.kelasSendiri.indexOf(k) >= 0 ? 'sendiri' : 'merek';
    return { kelas: k, jenis, anggota, ketAnggota: anggota.length + ' nama: ' + anggota.join(', '), baris, perBulan, n: riw.length, kosong: !riw.length, ketKosong: !riw.length ? 'belum ada kedatangan nyata di kelas ini' : '' }; });
  const nBulan = Object.keys(bulanSemua).length; const nKuartal = Object.keys(kuartalSemua).length;
  const periodeTeks = !dari ? 'belum ada kedatangan nyata' : 'data kedatangan ' + kmTgl(dari) + ' ' + String(dari).slice(0, 4) + '–' + kmTgl(sampai) + ' ' + String(sampai).slice(0, 4) + ' (' + nBulan + ' bulan' + (nKuartal >= 2 ? ', ' + nKuartal + ' kuartal' : '') + ')' + (nKuartal < 2 ? ' — per kuartal belum bisa dibandingkan' : '');
  const D = kmDaftar(); const tanpaKelas = D.baris.filter((b) => !b.wadah && !b.sendiri && !b.kelas && !b.varian).map((b) => b.merk);
  return { kartu, periode: { dari, sampai, nBulan, nKuartal, kuartalBisa: nKuartal >= 2 }, periodeTeks, tanpaKelas, belumKonfirmasi: D.belumKonfirmasi };
}
