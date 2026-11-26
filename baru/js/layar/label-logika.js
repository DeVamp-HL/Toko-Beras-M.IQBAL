// LABEL & KEDALUWARSA (owner 26 Nov 2026, sensus ulang 1c: A49 A62 A78). Tanpa DOM, awalan lb. Keputusan owner:
//   · label kemasan adukan = LENGKAP: merek, kelas mutu, berat bersih, nama & alamat toko, tanggal kemas, "baik dipakai sebelum", QR toko — dicetak sesudah adukan
//     disimpan atau ulang dari Jual › Label & kartu;
//   · label tanggal masuk tumpukan karung = sesudah Barang masuk (per merek: merek, tanggal masuk, berat asli per karung) + cetak ulang dari Jual › Label.
// Setelan (umur simpan, ambang "dekat", kelas mutu per kemasan, cetak "baik dipakai sebelum") = aturanToko/catatStok.label — dokumen yang SUDAH dibaca tablet
// (rules v7+, DOK_STAF), jadi tablet yang mencetak label memakai setelan owner tanpa rules baru. Penulis catatStok lain menyalin dokumen utuh (Object.assign lama).
// Alamat toko di label = kop struk (aturanToko/struk, dibaca tablet; susunIdentitas menyalinnya dari Identitas usaha).
// KEDALUWARSA: tidak ada kolom baru di dokumen adukan — "baik dipakai sebelum" = tanggal kemas (tanggal adukan) + umur simpan setelan owner (bawaan 6 bulan).
// Mengubah umur simpan menggeser tanggal semua kemasan yang belum laku (disebut di Atur). Kemasan stok awal (beli jadi 8 Agu) = tanggal kemas TIDAK diketahui.
// UMUR KEMASAN (FEFO): sisa unit tiap kemasan = mesin beku (ingatStokKemasan, sumber yang sama dengan Gudang); sisa diisikan ke adukan dari yang TERBARU mundur
// (yang terjual = yang paling lama, sama dengan umur karung FIFO di Stok › Umur & putaran). Adukan tertua yang masih tersisa = yang paling cepat lewat → dikeluarkan dulu.
import { kunciKemasan } from '../mesin/pembantu.js';
import { ambilProduksiBerlaku, ingatStokKemasan, cacheMentah, ambilSemuaBatch } from '../data/toko.js';
import { hariIniIso, tanggalPendek, ANGKA, KG } from '../inti/format.js';

export const LB_KELAS = ['Premium', 'Medium', 'Submedium', 'Pecah'];
export const LB_BAWAAN = { umurBulan: 6, ambangHari: 30, kedaluwarsa: true };
export const LB_BATAS = { umurBulan: [1, 24], ambangHari: [1, 180] };
const LB_NAMA = { umurBulan: 'Umur simpan', ambangHari: 'Tanda "dekat"' };
const lbHariKe = (iso) => Math.round(new Date(String(iso) + 'T00:00:00Z').getTime() / 86400000);
const lbB2 = (n) => Math.round((Number(n) || 0) * 100) / 100;
const lbDok = () => cacheMentah('aturan').find((d) => String(d.id) === 'catatStok') || null;
/** Tambah n bulan kalender ke 'YYYY-MM-DD'; tanggal yang tidak ada di bulan tujuan (31 → Feb) = hari terakhir bulan itu. */
export function lbTambahBulan(iso, n) {
  const [y, m, d] = String(iso).split('-').map(Number); const t = y * 12 + (m - 1) + Number(n); const Y = Math.floor(t / 12), M = t % 12;
  const akhir = new Date(Date.UTC(Y, M + 1, 0)).getUTCDate(); return Y + '-' + String(M + 1).padStart(2, '0') + '-' + String(Math.min(d, akhir)).padStart(2, '0');
}

/** Setelan label owner (aturanToko/catatStok.label); belum diatur / di luar batas → bawaan. kelas = { kunci kemasan: kelas mutu } (kosong = tidak dicetak). */
export function lbAtur() {
  const d = lbDok(); const a = d && d.label && typeof d.label === 'object' ? d.label : null; const o = {};
  Object.keys(LB_BATAS).forEach((k) => { const n = a ? Number(a[k]) : NaN; const b = LB_BATAS[k]; o[k] = isFinite(n) && Math.round(n) === n && n >= b[0] && n <= b[1] ? n : LB_BAWAAN[k]; });
  o.kedaluwarsa = a && typeof a.kedaluwarsa === 'boolean' ? a.kedaluwarsa : LB_BAWAAN.kedaluwarsa;
  const kelas = {}; if (a && a.kelas && typeof a.kelas === 'object') Object.keys(a.kelas).forEach((k) => { if (LB_KELAS.indexOf(a.kelas[k]) >= 0) kelas[k] = a.kelas[k]; });
  return Object.assign(o, { kelas, dariOwner: !!a, sejak: a ? String(a.tanggal || '') : '' });
}
/**
 * Simpan setelan label. isi = { umurBulan, ambangHari, kedaluwarsa (bool), kelas: { kunci: kelas | '' } }. Kosong = angka sekarang; pecahan / di luar batas DITOLAK
 * dengan kalimat. Dokumen catatStok DISALIN utuh, hanya kolom label yang ditimpa (setelan pencatatan stok, modal FIFO, ukuran karung tetap).
 */
export function susunAturLabel(isi, w) {
  const kini = lbAtur(); const a = isi || {}; const o = {}; let tolak = '';
  Object.keys(LB_BATAS).forEach((k) => { if (tolak) return; const t = String(a[k] === undefined || a[k] === null ? '' : a[k]).trim().replace(',', '.'); const b = LB_BATAS[k];
    if (!t) { o[k] = kini[k]; return; } const n = Number(t);
    if (!isFinite(n) || Math.round(n) !== n || n < b[0] || n > b[1]) tolak = LB_NAMA[k] + ' harus bilangan bulat ' + b[0] + '–' + b[1] + (k === 'umurBulan' ? ' bulan' : ' hari'); else o[k] = n; });
  if (tolak) return { tolak };
  const kelas = Object.assign({}, kini.kelas); Object.keys(a.kelas || {}).forEach((k) => { const v = String(a.kelas[k] || ''); if (!v) delete kelas[k]; else if (LB_KELAS.indexOf(v) >= 0) kelas[k] = v; else tolak = 'Kelas mutu "' + v + '" tidak dikenal'; });
  if (tolak) return { tolak };
  const lama = lbDok() || { id: 'catatStok' };
  const label = { umurBulan: o.umurBulan, ambangHari: o.ambangHari, kedaluwarsa: typeof a.kedaluwarsa === 'boolean' ? a.kedaluwarsa : kini.kedaluwarsa, kelas, tanggal: w.tanggal };
  const geser = label.umurBulan !== kini.umurBulan;
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({}, lama, { id: 'catatStok', tanggal: w.tanggal, jam: w.jam, label }) }],
    patch: { aturLb: null, kabarAwas: false, kabar: 'Setelan label disimpan — umur simpan ' + label.umurBulan + ' bulan · tanda dekat ' + label.ambangHari + ' hari' + (label.kedaluwarsa ? '' : ' · "baik dipakai sebelum" TIDAK dicetak')
      + (geser ? '. Tanggal "baik dipakai sebelum" semua kemasan yang belum laku ikut bergeser.' : '') } };
}

/** Adukan (dokumen produksi berlaku, bukan pindahan ke karung utuh) yang MENAMBAH satu kemasan: lapisan { tanggal, jam, id, unit, tanpaTanggal }. */
function lbLapisan(kunci) {
  return ambilProduksiBerlaku().filter((p) => p && !p.jadiKarungUtuh && kunciKemasan(p.namaProduk, p.ukuranKemasan) === kunci && (Number(p.jumlahUnit) || 0) > 0)
    .map((p) => ({ tanggal: String(p.tanggal || ''), jam: String(p.jam || ''), id: p.id, unit: Number(p.jumlahUnit) || 0, tanpaTanggal: !p.tanggal || !!p.stokAwal || !!p.beliJadi }))
    .sort((a, b) => a.tanggal.localeCompare(b.tanggal) || a.jam.localeCompare(b.jam) || (Number(a.id) || 0) - (Number(b.id) || 0));
}
/**
 * FIFO unit: sisa diisikan ke lapisan dari yang TERBARU mundur. Lapisan tanpa tanggal kemas (stok awal / beli jadi) ikut antrean di tempatnya tetapi tidak bertanggal.
 * Sisa yang melebihi semua lapisan (cocokkan plus) = tanpa tanggal. → { tersisa: [{ tanggal, unit, utuh, tanpaTanggal }] (terbaru dulu), tanpaUnit }. Menutup persis.
 */
export function lbFifo(lapisan, sisa) {
  let s = Math.max(0, Math.round((Number(sisa) || 0) * 1000)); const out = [];
  for (let i = lapisan.length - 1; i >= 0 && s > 0; i--) { const L = lapisan[i]; const u = Math.round(L.unit * 1000); const ambil = Math.min(u, s); s -= ambil;
    out.push({ tanggal: L.tanggal, jam: L.jam, id: L.id, unit: ambil / 1000, unitMasuk: L.unit, utuh: ambil === u, tanpaTanggal: L.tanpaTanggal }); }
  return { tersisa: out, tanpaUnit: s / 1000 + out.filter((x) => x.tanpaTanggal).reduce((a, x) => a + x.unit, 0) };
}
/** Keadaan satu lapisan bertanggal: kedaluwarsa = tanggal kemas + umur simpan; sisaHari terhadap hari ini; status lewat | dekat | aman. */
export function lbKeadaan(tanggalKemas, iso, A) {
  const kedaluwarsa = lbTambahBulan(tanggalKemas, A.umurBulan); const sisaHari = lbHariKe(kedaluwarsa) - lbHariKe(iso); const umur = lbHariKe(iso) - lbHariKe(tanggalKemas);
  return { kedaluwarsa, sisaHari, umur, status: sisaHari < 0 ? 'lewat' : sisaHari <= A.ambangHari ? 'dekat' : 'aman' };
}

/**
 * A62 — kemasan bertanggal per kemasan jadi yang masih bersisa: lapisan adukan tersisa (FIFO), adukan tertua = keluarkan dulu, "baik dipakai sebelum" & sisa hari.
 * → { iso, umurBulan, ambang, daftar (urut paling cepat lewat), lewat, dekat, nBertanggal, tanpa (kemasan yang sisanya tanpa tanggal kemas sama sekali) }.
 */
export function lbRingkasKemasan(kini) {
  const iso = hariIniIso(kini); const A = lbAtur(); const S = ingatStokKemasan(); const daftar = []; const tanpa = [];
  Object.keys(S).forEach((k) => { const st = S[k]; const sisa = Number(st.sisaUnit) || 0; if (!(sisa > 0.0005)) return;
    const nama = st.namaProduk + ' ' + String(st.ukuranKemasan).replace('.', ',') + ' kg'; const F = lbFifo(lbLapisan(k), sisa);
    const bertanggal = F.tersisa.filter((x) => !x.tanpaTanggal).map((x) => Object.assign(x, lbKeadaan(x.tanggal, iso, A)));
    if (!bertanggal.length) { tanpa.push({ kunci: k, nama, sisa }); return; }
    const tua = bertanggal[bertanggal.length - 1];
    daftar.push({ kunci: k, nama, namaProduk: st.namaProduk, ukuran: Number(st.ukuranKemasan) || 0, sisa, lapisan: bertanggal, tanpaUnit: lbB2(F.tanpaUnit), tertua: tua, status: tua.status,
      kelas: A.kelas[k] || '', teks: 'keluarkan dulu kemasan ' + tanggalPendek(tua.tanggal) + ' (' + ANGKA(tua.unit) + ' kantong) · baik dipakai sebelum ' + tanggalPendek(tua.kedaluwarsa)
        + ' · ' + (tua.sisaHari < 0 ? 'LEWAT ' + (-tua.sisaHari) + ' hari' : tua.sisaHari + ' hari lagi') + (F.tanpaUnit > 0.0005 ? ' · ' + ANGKA(lbB2(F.tanpaUnit)) + ' kantong tanpa tanggal kemas' : '') }); });
  daftar.sort((a, b) => a.tertua.sisaHari - b.tertua.sisaHari || a.nama.localeCompare(b.nama));
  return { iso, umurBulan: A.umurBulan, ambang: A.ambangHari, cetakKedaluwarsa: A.kedaluwarsa, daftar, lewat: daftar.filter((x) => x.status === 'lewat'), dekat: daftar.filter((x) => x.status === 'dekat'),
    nBertanggal: daftar.length, tanpa, sumber: 'Stok › Tugas gudang', tujuan: { ke: 'stok', tab: 'tugas' } };
}
/** Sumber pengingat jenis 'kemasan' (app.js lewat lokal.gudang): satu per kemasan yang lewat / dekat — jatuh = "baik dipakai sebelum" adukan tertuanya. */
export function lbSumberPengingat(kini) {
  const R = lbRingkasKemasan(kini);
  return R.lewat.concat(R.dekat).map((x) => ({ id: 'kemasan|' + x.kunci + '|' + x.tertua.kedaluwarsa, jenis: 'kemasan', kunci: x.kunci, teks: x.nama + ' baik dipakai sebelum ' + tanggalPendek(x.tertua.kedaluwarsa),
    siapa: 'stok', jatuh: x.tertua.kedaluwarsa, hariSebelum: R.ambang, n: 0, ket: x.teks }));
}

/** Pilihan tanggal kemas untuk label satu kemasan: lapisan adukan yang masih tersisa (terbaru dulu) — bawaan = adukan terbaru (yang baru dibungkus). */
export function lbPilihanKemas(kunci, kini) {
  const iso = hariIniIso(kini); const A = lbAtur(); const st = ingatStokKemasan()[kunci]; const L = lbLapisan(kunci);
  const F = lbFifo(L, st ? Number(st.sisaUnit) || 0 : 0); const ada = F.tersisa.filter((x) => !x.tanpaTanggal);
  // adukan HARI INI selalu ditawarkan walau stoknya sudah dipotong jual (label dicetak sesudah adukan disimpan)
  const hariIni = L.filter((x) => !x.tanpaTanggal && x.tanggal === iso).reverse();
  const seen = {}; const out = [];
  hariIni.concat(ada).forEach((x) => { if (seen[x.tanggal]) return; seen[x.tanggal] = 1; out.push(Object.assign({ tanggal: x.tanggal, unit: x.unit }, lbKeadaan(x.tanggal, iso, A))); });
  return out;
}

/** Kop di label: nama & alamat toko dari kop struk (dibaca tablet). */
export function lbKop() {
  const d = cacheMentah('aturan').find((x) => String(x.id) === 'struk') || {}; const k = d.kop || {};
  return { nama: String(k.nama || 'TOKO BERAS M.IQBAL').trim(), alamat: String(k.alamat || '').trim() };
}
/**
 * A49 — isi label kemasan adukan LENGKAP. sasaran = tanda kenal (jalur 'kemasan', kunci kemasan, nama). pilih = { tanggal (tanggal kemas) }. Bentuk sama dengan
 * tkIsiLabel + `baris` (baris kecil tambahan; printer lama tanpa `baris` = cetakan lama persis). Kelas kosong / alamat kosong / umur tidak dicetak = baris itu
 * dilewati dan `kurang` menyebutnya (layar memperingatkan sebelum mencetak).
 */
export function lbIsiKemasan(sasaran, kode, pilih, A, kop, teksKode) {
  const S = sasaran || {}; const K = kop || lbKop(); const P = pilih || {}; const At = A || lbAtur(); const kurang = [];
  const ukuran = Number(String(S.kunci || '').split('|')[1]) || 0; const kelas = At.kelas[String(S.kunci || '')] || '';
  const baris = [];
  if (kelas) baris.push('Kelas mutu: ' + kelas); else kurang.push('kelas mutu (Atur label)');
  if (ukuran > 0) baris.push('Berat bersih: ' + String(ukuran).replace('.', ',') + ' kg');
  if (P.tanggal) { baris.push('Dikemas: ' + tanggalPendek(P.tanggal)); if (At.kedaluwarsa) baris.push('Baik dipakai sebelum: ' + tanggalPendek(lbTambahBulan(P.tanggal, At.umurBulan))); }
  else kurang.push('tanggal kemas');
  if (K.alamat) baris.push(K.alamat); else kurang.push('alamat toko (Laporan › Identitas usaha)');
  return { judul: String(S.nama || '').slice(0, 80), ket: K.nama, kode: String(kode || ''), teksKode: teksKode !== undefined ? teksKode : String(kode || ''), baris, kurang };
}

/** Baris kedatangan yang bisa diberi label tumpukan (karung, bukan bal): { merk, karung, kgKarung (berat asli rata-rata per karung), ikutTimbang }. */
export function lbBarisKedatangan(batch) {
  return ((batch && batch.merkList) || []).filter((m) => m && m.merk && m.bentuk !== 'bal' && (Number(m.jumlahKarung) || 0) > 0).map((m) => {
    const n = Number(m.jumlahKarung) || 0; const kg = m.kgTerima !== undefined && m.kgTerima !== null && Number(m.kgTerima) > 0 ? Number(m.kgTerima) : Number(m.totalKg) || n * (Number(m.beratKarung) || 50);
    return { merk: String(m.merk), karung: n, beratNota: Number(m.beratKarung) || 50, kgKarung: lbB2(kg / n), ikutTimbang: m.kgTerima !== undefined && m.kgTerima !== null }; });
}
/** Kedatangan pemasok sungguhan yang memuat merek itu, terbaru dulu (untuk cetak ulang label tumpukan dari Jual › Label). */
export function lbKedatanganMerek(merk, n) {
  return ambilSemuaBatch().filter((b) => b && !b.stokAwal && !b.tutupBuku && (b.merkList || []).some((m) => m && m.merk === merk && m.bentuk !== 'bal'))
    .sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || (Number(b.id) || 0) - (Number(a.id) || 0)).slice(0, n || 4)
    .map((b) => ({ id: String(b.id), tanggal: String(b.tanggal || ''), pemasok: String(b.pemasok || ''), baris: lbBarisKedatangan(b).filter((x) => x.merk === merk)[0] || null })).filter((x) => x.baris);
}
/**
 * A78 — isi label TANGGAL MASUK satu tumpukan: merek (besar), tanggal masuk, berat asli per karung (hasil timbang kedatangan; nota bila belum ditimbang), jumlah
 * karung, kalimat FIFO. Tanpa QR (bukan barang yang dipindai kasir). Bentuk = tkIsiLabel + baris.
 */
export function lbIsiTumpukan(merk, tanggal, b, kop) {
  const K = kop || lbKop(); const B = b || {}; const baris = ['Masuk: ' + tanggalPendek(tanggal)];
  if (B.kgKarung) baris.push((B.ikutTimbang ? 'Berat asli ±' : 'Berat nota ') + KG(B.kgKarung) + '/karung');
  if (B.karung) baris.push(ANGKA(B.karung) + ' karung datang');
  baris.push('Keluarkan yang lebih lama dulu');
  return { judul: String(merk || '').slice(0, 80), ket: K.nama, kode: '', teksKode: '', baris, kurang: [] };
}
