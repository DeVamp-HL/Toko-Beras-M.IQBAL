// LAYAR HARGA & PEMASOK — H1 KATALOG HARGA (dikunci owner 18 Sep 2026: gabungan Papan Kapur · Satu Kalimat · Timbang Dampak · Modal dan Pasar ·
// Karung Dibelah · Label Rak; "Biarkan — ini sengaja" susulan V6). Logika tanpa DOM, nama pembantu berawalan hg (bundel uji satu lingkup).
// Katalog = TIGA koleksi sistem lama: katalogHargaKarung (per kg) · katalogHargaKemasan (per unit) · katalogHargaLiteran (per liter) — dokumen persis
// simpanHargaKarung/Kemasan/Literan index.html (+ kolom baru modalSaatSetel = harga beli terbaru saat harga disetel, supaya "modal naik sesudah harga
// disetel" terbaca tanpa menebak; dokumen lama membacanya dari kedatangan terakhir sebelum diubahPada).
// Perubahan harga = DRAF (aturanToko/hargaDraf, ikut ke semua perangkat) sampai DITERBITKAN — terbit = SATU writeBatch untuk semuanya
// (memori katalog-harga-tulis-massal): kasir tidak pernah melihat katalog separuh baru separuh lama.
// RUGI hanya bila modal > harga (tegas `>`); harga = modal = "untung nol", keadaan yang boleh dipilih sadar (memori harga-karung-ir64-elevate-ditunda).
// Target untung bawaan = rata-rata untung yang SEDANG berlaku, bukan angka karangan — layar yang menyalakan alarm di semua baris akan diabaikan.
// Modal per kg = modal rata-rata di buku (mesin yang sama dengan laba & neraca; sama dengan layar HPP), harga beli terbaru dibawa sebagai pembanding.
import { hitungStokKarungPerMerk, hitungStokKemasan } from '../mesin/beku.js';
import { RASIO_DEFAULT, RASIO_KONVERSI, kunciKemasan } from '../mesin/pembantu.js';
import { ambilHargaKarung, ambilHargaKemasan, ambilHargaLiteran, ambilSemuaBatch, ambilPenjualan, ambilHargaPasar, ambilHargaTerbit, cacheMentah } from '../data/toko.js';
import { RP, hariIniIso } from '../inti/format.js';

export const ATUR_HARGA_BAWAAN = { targetPerKg: 0, bulatLiter: 500, bulatKemasan: 1000, bulatKarung: 100, langkahRp: 50, ambangDampak: 50000, bongkarKg: 0, mdrPersen: 30, mdrBatas: 500000 };
export const TAB_HARGA = [['papan', 'Papan'], ['kalimat', 'Kalimat'], ['dampak', 'Dampak'], ['pasar', 'Pasar'], ['belah', 'Belah'], ['label', 'Label']];
export const HG_PERLU = ['lubang', 'rugi', 'dimakan', 'bawah'];
export const HG_JUDUL = { lubang: 'Belum ada harganya', rugi: 'Dijual di bawah modal', dimakan: 'Modal naik sesudah harga disetel', bawah: 'Untungnya di bawah target', nol: 'Untung nol — harga sama dengan modal', tanpaModal: 'Modalnya belum tercatat', aman: 'Aman' };
export const HG_CAP = { lubang: 'belum ada harga', rugi: 'rugi', dimakan: 'modal naik', bawah: 'di bawah target', nol: 'untung nol', tanpaModal: 'tanpa modal', aman: '' };
const HG_HARI_LAKU = 30;
const hgAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const hgKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const hgRasio = (merk) => RASIO_KONVERSI[merk] || RASIO_DEFAULT;
const hgBulatAtas = (x, k) => (k > 0 ? Math.ceil(x / k - 1e-9) * k : Math.round(x));
const hgBulatBawah = (x, k) => (k > 0 ? Math.floor(x / k + 1e-9) * k : Math.round(x));
const hgAturDok = (id) => cacheMentah('aturan').find((d) => String(d.id) === id) || null;
export const kunciHarga = (merk, satuan) => merk + '|' + satuan;
/** Satuan sebuah baris: L = per liter (katalogHargaLiteran), K<ukuran> = per kantong/karung utuh (katalogHargaKemasan), S = per kg (katalogHargaKarung). */
export function satuanHarga(id, merk) {
  if (id === 'L') return { id, nama: 'Literan', pendek: 'liter', per: 'liter', kg: hgRasio(merk), bulat: 'bulatLiter', koleksi: 'katalogHargaLiteran' };
  if (id === 'S') return { id, nama: 'Karung per kg', pendek: '/kg', per: 'kg', kg: 1, bulat: 'bulatKarung', koleksi: 'katalogHargaKarung' };
  const u = Number(String(id).slice(1)); return { id, nama: (u >= 25 ? 'Karung ' : 'Kemasan ') + String(u).replace('.', ',') + ' kg', pendek: String(u).replace('.', ',') + ' kg', per: u >= 25 ? 'karung' : 'kantong', kg: u, bulat: 'bulatKemasan', koleksi: 'katalogHargaKemasan' };
}
const hgUrutSatuan = (a, b) => { const r = (s) => (s === 'L' ? 0 : s === 'S' ? 1000 : Number(s.slice(1))); return r(a) - r(b); };

/** Ongkos bongkar per kg yang TERUKUR dari kedatangan nyata (Σ upah bongkar ÷ Σ kg kedatangan yang berupah) — bukan angka karangan. */
export function bongkarTerukur() {
  let rp = 0, kg = 0; ambilSemuaBatch().forEach((b) => { if (b.stokAwal || !(Number(b.biayaBongkar) > 0)) return; const k = (b.merkList || []).reduce((a, m) => a + (Number(m.totalKg) || 0), 0); if (k > 0) { rp += Number(b.biayaBongkar); kg += k; } });
  return kg > 0 ? Math.round(rp / kg) : 0;
}
/** Target untung bawaan = rata-rata untung per kg katalog KARUNG yang sedang berlaku (dibulatkan ke Rp50). Tanpa katalog bermodal → 0. */
export function targetTerukur() {
  const stokK = hitungStokKarungPerMerk(); const u = [];
  ambilHargaKarung().forEach((h) => { const m = (stokK[h.merk] || {}).hppTerakhirPerKg || 0; if (m > 0 && Number(h.hargaPerKg) > 0) u.push(Number(h.hargaPerKg) - m); });
  if (!u.length) return 0; const rata = u.reduce((a, x) => a + x, 0) / u.length; return Math.max(0, Math.round(rata / 50) * 50);
}
export function aturHarga() {
  const a = hgAturDok('harga'); const ambil = (k, syarat) => (a && isFinite(Number(a[k])) && syarat(Number(a[k])) ? Number(a[k]) : null);
  const t = ambil('targetPerKg', (n) => n >= 0); const bk = ambil('bongkarKg', (n) => n >= 0);
  return { targetPerKg: t === null ? targetTerukur() : t, targetDariRata: t === null, bulatLiter: ambil('bulatLiter', (n) => n >= 0) ?? ATUR_HARGA_BAWAAN.bulatLiter, bulatKemasan: ambil('bulatKemasan', (n) => n >= 0) ?? ATUR_HARGA_BAWAAN.bulatKemasan,
    bulatKarung: ambil('bulatKarung', (n) => n >= 0) ?? ATUR_HARGA_BAWAAN.bulatKarung, langkahRp: ambil('langkahRp', (n) => n > 0) ?? ATUR_HARGA_BAWAAN.langkahRp, ambangDampak: ambil('ambangDampak', (n) => n >= 0) ?? ATUR_HARGA_BAWAAN.ambangDampak,
    bongkarKg: bk === null ? bongkarTerukur() : bk, bongkarTerukur: bk === null, mdrPersen: ambil('mdrPersen', (n) => n >= 0 && n <= 1000) ?? ATUR_HARGA_BAWAAN.mdrPersen, mdrBatas: ambil('mdrBatas', (n) => n >= 0) ?? ATUR_HARGA_BAWAAN.mdrBatas, dariOwner: !!a };
}
export function susunAturHarga(isi, w) {
  const kini = aturHarga(); const data = { id: 'harga', tanggal: w.tanggal, jam: w.jam };
  const baca = (k, syarat, teks) => { if (hgKosong(isi[k])) { data[k] = kini[k]; return ''; } const n = hgAngka(isi[k]); if (!syarat(n)) return teks; data[k] = n; return ''; };
  const salah = baca('targetPerKg', (n) => n >= 0 && n <= 100000, 'Target untung per kg harus 0–100.000') || baca('bulatLiter', (n) => n >= 0 && n <= 10000, 'Pembulatan literan harus 0–10.000') || baca('bulatKemasan', (n) => n >= 0 && n <= 50000, 'Pembulatan kemasan harus 0–50.000')
    || baca('bulatKarung', (n) => n >= 0 && n <= 10000, 'Pembulatan per kg harus 0–10.000') || baca('langkahRp', (n) => n > 0 && n <= 10000, 'Langkah naik-turun per kg harus 1–10.000 (tidak boleh nol)') || baca('ambangDampak', (n) => n >= 0, 'Batas "tidak seberapa" tidak boleh minus')
    || baca('bongkarKg', (n) => n >= 0 && n <= 5000, 'Ongkos bongkar per kg harus 0–5.000') || baca('mdrPersen', (n) => n >= 0 && n <= 1000, 'Potongan QRIS: ketik angkanya saja, 30 = 0,30 % (0–1000)') || baca('mdrBatas', (n) => n >= 0, 'Batas bebas potongan tidak boleh minus');
  if (salah) return { tolak: salah };
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { aturH: null, kabar: 'Aturan harga disimpan — target untung ' + RP(data.targetPerKg) + '/kg · langkah ' + RP(data.langkahRp) + ' · ongkos bongkar ' + RP(data.bongkarKg) + '/kg · potongan QRIS ' + hgPct(data.mdrPersen) + ' di atas ' + RP(data.mdrBatas), kabarAwas: false } };
}
export const hgPct = (n) => (n / 100).toFixed(2).replace('.', ',') + ' %';

// ---- keadaan bersama (ikut ke semua perangkat): draf, "sengaja", label rak, harga pasar
export function drafHarga() { const d = hgAturDok('hargaDraf'); const o = d && d.draf && typeof d.draf === 'object' ? d.draf : {}; const out = {}; Object.keys(o).forEach((k) => { if (Number(o[k]) > 0) out[k] = Math.round(Number(o[k])); }); return out; }
export function petaSengaja() { const d = hgAturDok('hargaSengaja'); return d && d.peta && typeof d.peta === 'object' ? d.peta : {}; }
export function daftarLabel() { const d = hgAturDok('hargaLabel'); return Array.isArray(d && d.daftar) ? d.daftar : []; }
export function petaPasar() { const p = {}; ambilHargaPasar().forEach((x) => { if (Number(x.harga) > 0) p[String(x.kunci || x.id)] = { harga: Math.round(Number(x.harga)), tanggal: x.tanggal || '' }; }); return p; }
const hgDokDraf = (draf, w) => ({ koleksi: 'aturanToko', data: { id: 'hargaDraf', tanggal: w.tanggal, jam: w.jam, draf } });

/** Terjual 30 hari terakhir per kunci harga, dalam SATUAN barisnya (liter · kantong · kg). */
export function lakuHarga(kini) {
  const mulai = hariIniIso(new Date((kini ? kini.getTime() : Date.now()) - HG_HARI_LAKU * 86400000)); const o = {};
  ambilPenjualan().forEach((p) => { if ((p.tanggal || '') < mulai) return;
    if (p.jenis === 'literan' && p.merkSumber) o[kunciHarga(p.merkSumber, 'L')] = (o[kunciHarga(p.merkSumber, 'L')] || 0) + (Number(p.jumlahLiter) || 0);
    else if ((p.jenis === 'karung' || p.jenis === 'repacking') && p.merkSumber) o[kunciHarga(p.merkSumber, 'S')] = (o[kunciHarga(p.merkSumber, 'S')] || 0) + (Number(p.totalKg) || 0);
    else if (p.jenis === 'kemasan' && p.namaProduk) { const u = Number(p.ukuranKemasan); if (isFinite(u) && u > 0) o[kunciHarga(p.namaProduk, 'K' + u)] = (o[kunciHarga(p.namaProduk, 'K' + u)] || 0) + (Number(p.jumlahUnit) || 0); } });
  return o;
}
/** Harga beli per kg yang berlaku saat sebuah harga disetel: kolom modalSaatSetel (sistem baru) atau kedatangan terakhir merk itu di/sebelum diubahPada. 0 = tidak diketahui. */
function hgModalSetel(dok, merk) {
  if (!dok) return 0; if (Number(dok.modalSaatSetel) > 0) return Number(dok.modalSaatSetel);
  const iso = String(dok.diubahPada || dok.diperbaruiPada || '').slice(0, 10); if (!iso) return 0; let pilih = null;
  ambilSemuaBatch().forEach((b) => { if (b.stokAwal || (b.tanggal || '') > iso) return; (b.merkList || []).forEach((m) => { if (m.merk !== merk || !(Number(m.hargaPerKg) > 0)) return; if (!pilih || (b.tanggal || '') > pilih.t || ((b.tanggal || '') === pilih.t && (Number(b.id) || 0) > pilih.id)) pilih = { t: b.tanggal || '', id: Number(b.id) || 0, h: Number(m.hargaPerKg) }; }); });
  return pilih ? pilih.h : 0;
}
/** SATU tempat menilai sebuah harga (dipakai papan, lembar ubah, kalimat, terbit). */
export function nilaiHarga(n, modalUnit, kg, target, naik) {
  if (!(n > 0)) return { status: 'lubang', perKg: 0, margin: 0 };
  const perKg = n / kg; if (!(modalUnit > 0)) return { status: 'tanpaModal', perKg, margin: 0 };
  const margin = (n - modalUnit) / kg;
  const status = margin < -0.5 ? 'rugi' : Math.abs(margin) <= 0.5 ? 'nol' : margin < target && naik ? 'dimakan' : margin < target ? 'bawah' : 'aman';
  return { status, perKg, margin };
}
/** Semua baris harga SEKALI: tiap merek × satuan yang ada di katalog atau di buku stok. */
export function hgSemua(kini) {
  const atur = aturHarga(); const target = atur.targetPerKg; const stokK = hitungStokKarungPerMerk(); const stokM = hitungStokKemasan();
  const draf = drafHarga(); const sengaja = petaSengaja(); const pasar = petaPasar(); const laku = lakuHarga(kini); const labelBasi = daftarLabel();
  const kK = ambilHargaKarung(), kM = ambilHargaKemasan(), kL = ambilHargaLiteran();
  const modalKg = (m) => (stokK[m] || {}).hppTerakhirPerKg || 0; const beliTerbaru = (m) => (stokK[m] || {}).hargaTerakhirPerKg || 0;
  const daftar = {};   // merk -> [satuan]
  const tambah = (m, s) => { if (!m) return; (daftar[m] = daftar[m] || []).indexOf(s) < 0 && daftar[m].push(s); };
  Object.keys(stokK).forEach((m) => { tambah(m, 'L'); tambah(m, 'S'); }); kK.forEach((h) => tambah(h.merk, 'S')); kL.forEach((h) => tambah(h.merk, 'L'));
  kM.forEach((h) => { const u = Number(h.ukuran); if (isFinite(u) && u > 0) tambah(h.merk, 'K' + u); });
  Object.keys(stokM).forEach((k) => { const x = stokM[k]; const u = Number(x.ukuranKemasan); if (isFinite(u) && u > 0 && ((x.sisaUnit || 0) > 0 || (x.unitDibuat || 0) > 0)) tambah(x.namaProduk, 'K' + u); });
  const baris = [];
  Object.keys(daftar).sort((a, b) => a.localeCompare(b)).forEach((m) => daftar[m].sort(hgUrutSatuan).forEach((sid) => {
    const st = satuanHarga(sid, m); const k = kunciHarga(m, sid);
    const dok = sid === 'L' ? kL.find((h) => h.merk === m) : sid === 'S' ? kK.find((h) => h.merk === m) : kM.find((h) => h.merk === m && Number(h.ukuran) === st.kg);
    const lamaN = dok ? Math.round(Number(sid === 'L' ? dok.hargaPerLiter : sid === 'S' ? dok.hargaPerKg : dok.hargaPerUnit) || 0) : 0;
    let modalUnit = 0, modalDari = '';
    if (sid === 'L' || sid === 'S') { modalUnit = modalKg(m) * st.kg; modalDari = modalUnit > 0 ? 'beras' : ''; }
    else { const x = stokM[kunciKemasan(m, st.kg)]; if (x && x.hppRataRataPerUnit > 0) { modalUnit = x.hppRataRataPerUnit; modalDari = 'adukan'; } else if (modalKg(m) > 0) { modalUnit = modalKg(m) * st.kg; modalDari = 'beras'; } }
    const setel = hgModalSetel(dok, m); const naik = setel > 0 && beliTerbaru(m) > setel + 0.5; const naikRp = naik ? beliTerbaru(m) - setel : 0;
    const n = draf[k] !== undefined ? draf[k] : lamaN; const N = nilaiHarga(n, modalUnit, st.kg, target, naik);
    const usul = modalUnit > 0 ? hgBulatAtas(modalUnit + target * st.kg, atur[st.bulat]) : 0;
    const sj = sengaja[k]; const sengajaAktif = !!sj && draf[k] === undefined && Number(sj.modal) === Math.round(modalUnit) && Number(sj.n) === lamaN && HG_PERLU.indexOf(N.status) >= 0;
    const NT = modalDari === 'beras' && beliTerbaru(m) > 0 && n > 0 ? nilaiHarga(n, beliTerbaru(m) * st.kg, st.kg, target, false) : null;
    baris.push({ k, merk: m, st, judul: m + ' · ' + st.nama, n, lamaN, adaDraf: draf[k] !== undefined, status: N.status, perKg: N.perKg, margin: N.margin, marginTerbaru: NT ? NT.margin : null, modalUnit, modalDari, modalKg: modalKg(m), beliTerbaru: beliTerbaru(m),
      usul, setelTanggal: dok ? String(dok.diubahPada || '').slice(0, 10) : '', naik, naikRp, naikTeks: naik ? 'harga beli naik ' + RP(naikRp) + '/kg sejak harga ini disetel' + (dok && dok.diubahPada ? ' ' + String(dok.diubahPada).slice(0, 10) : '') : '',
      sengaja: sengajaAktif, dok: dok || null, koleksi: st.koleksi, laku: Math.round((laku[k] || 0) * 100) / 100, pasar: pasar[k] || null, labelBasi: labelBasi.find((x) => x.k === k) || null, cap: HG_CAP[N.status] });
  }));
  const hit = (u) => baris.filter((b) => b.status === u && !b.sengaja).length;
  const perlu = baris.filter((b) => !b.adaDraf && !b.sengaja && HG_PERLU.indexOf(b.status) >= 0);
  return { baris, atur, target, draf, nDraf: Object.keys(draf).length, perlu, ringkas: [['lubang', 'belum ada harga'], ['dimakan', 'modal naik'], ['bawah', 'di bawah target'], ['rugi', 'rugi']].map((r) => ({ id: r[0], a: hit(r[0]), l: r[1], nyala: hit(r[0]) > 0 && r[0] !== 'bawah' })),
    merk: Object.keys(daftar).sort((a, b) => a.localeCompare(b)), tanpaModal: hit('tanpaModal') };
}
export const cariBaris = (S, k) => S.baris.find((b) => b.k === k) || null;
export const teksMargin = (b) => (b.status === 'lubang' ? 'belum ada harga' : b.status === 'tanpaModal' ? RP(b.perKg) + '/kg · modal belum tercatat' : RP(b.perKg) + '/kg · ' + (b.margin < -0.5 ? 'RUGI ' + RP(-b.margin) : 'untung ' + RP(b.margin)) + '/kg' + (b.marginTerbaru !== null && Math.round(b.marginTerbaru) !== Math.round(b.margin) ? ' (vs beli terbaru ' + (b.marginTerbaru < -0.5 ? 'rugi ' : 'untung ') + RP(Math.abs(b.marginTerbaru)) + ')' : ''));

// ---- LEMBAR UBAH satu harga → DRAF (atau catatan harga pasar)
export function hitungUbah(S, k, ketik, mode) {
  const b = cariBaris(S, k); if (!b) return { tolak: 'Harga itu sudah tidak ada di daftar' };
  const n = Math.round(hgAngka(ketik)); const pasar = b.pasar ? b.pasar.harga : 0; const modeP = mode === 'pasar';
  let tolak = ''; if (!(n > 0)) tolak = 'Ketik harganya dulu'; else if (modeP && n === pasar) tolak = 'Sama dengan catatan pasar sekarang'; else if (!modeP && n === b.lamaN && !b.adaDraf) tolak = 'Sama dengan harga yang sedang berlaku';
  const N = n > 0 && !modeP ? nilaiHarga(n, b.modalUnit, b.st.kg, S.target, b.naik) : null;
  const arti = !(n > 0) ? '' : modeP ? (b.modalUnit > 0 ? RP(n / b.st.kg) + '/kg · pasar ' + (n < b.modalUnit - 0.5 ? 'DI BAWAH modal lu ' + RP((b.modalUnit - n) / b.st.kg) : RP((n - b.modalUnit) / b.st.kg) + ' di atas modal lu') + '/kg' : RP(n / b.st.kg) + '/kg (modal belum tercatat)')
    : N.status === 'tanpaModal' ? RP(N.perKg) + '/kg · modal belum tercatat, untungnya belum bisa disebut' : RP(N.perKg) + '/kg · ' + (N.status === 'rugi' ? 'RUGI ' + RP(-N.margin) + '/kg — dijual di bawah modal' : N.status === 'nol' ? 'untung nol — sama dengan modal' : 'untung ' + RP(N.margin) + '/kg' + (N.margin < S.target ? ' · masih di bawah target ' + RP(S.target) : ''));
  return { b, n, tolak, arti, awas: !!N && N.status === 'rugi' || (modeP && b.modalUnit > 0 && n > 0 && n < b.modalUnit - 0.5), N, pasar,
    modalTeks: b.modalUnit > 0 ? (b.modalDari === 'adukan' ? 'modal kemasan ' + RP(b.modalUnit) + ' per ' + b.st.per + ' (beras + kantong + upah kemas, dari adukan)' : RP(b.modalKg) + '/kg' + (b.st.kg !== 1 ? ' × ' + String(b.st.kg).replace('.', ',') + ' kg = ' + RP(b.modalUnit) + ' per ' + b.st.per : '')) + (b.beliTerbaru > 0 && b.modalDari === 'beras' && Math.round(b.beliTerbaru) !== Math.round(b.modalKg) ? ' · beli terbaru ' + RP(b.beliTerbaru) + '/kg' : '') : 'modal belum tercatat (belum ada kedatangan / adukan)',
    usulTeks: b.usul > 0 ? 'modal + ' + RP(S.target) + '/kg, dibulatkan ke atas ke ' + RP(S.atur[b.st.bulat]) : 'belum bisa diusulkan — modalnya belum tercatat',
    label: tolak || (modeP ? 'SIMPAN HARGA PASAR · cuma catatan' : 'SIMPAN SEBAGAI DRAF · belum sampai ke kasir') };
}
export function susunUbah(k, ketik, mode, w) {
  const S = hgSemua(new Date(w.kini)); const u = hitungUbah(S, k, ketik, mode); if (u.tolak) return { tolak: u.tolak };
  if (mode === 'pasar') return { dokumen: [{ koleksi: 'hargaPasar', data: { id: k, kunci: k, harga: u.n, tanggal: w.tanggal, jam: w.jam } }], patch: { ubah: null, ketik: '', kabar: 'Harga pasar ' + u.b.judul + ' dicatat ' + RP(u.n) + ' — ini catatan lu, kasir tidak terpengaruh', kabarAwas: false } };
  const d = Object.assign({}, S.draf); if (u.n === u.b.lamaN) delete d[k]; else d[k] = u.n;
  return { dokumen: [hgDokDraf(d, w)], patch: { ubah: null, ketik: '', kabar: u.n === u.b.lamaN ? 'Draf ' + u.b.judul + ' dibuang — kembali ke harga yang berlaku' : 'Disimpan sebagai draf: ' + u.b.judul + ' ' + RP(u.n) + ' — ' + (u.b.lamaN ? 'kasir masih memakai ' + RP(u.b.lamaN) : 'kasir masih tanpa harga untuk ini') + ' sampai diterbitkan', kabarAwas: false } };
}
export function susunHapusPasar(k, w) { const p = petaPasar(); if (!p[k]) return { tolak: 'Tidak ada catatan pasar untuk harga ini' }; return { hapus: [{ koleksi: 'hargaPasar', id: k }], patch: { ubah: null, ketik: '', kabar: 'Catatan harga pasar dihapus', kabarAwas: false } }; }
export function susunBuangDraf(k, w) {
  const draf = drafHarga(); if (k && draf[k] === undefined) return { tolak: 'Tidak ada draf untuk harga ini' }; if (!k && !Object.keys(draf).length) return { tolak: 'Tidak ada draf' };
  const d = k ? Object.assign({}, draf) : {}; if (k) delete d[k];
  return { dokumen: [hgDokDraf(d, w)], patch: { ubah: null, terbit: false, yakinRugi: false, kabar: k ? 'Draf dibuang — kembali ke harga yang berlaku' : 'Semua draf dibuang — tidak ada yang berubah', kabarAwas: false } };
}
/** "Biarkan — ini sengaja" DIINGAT (aturanToko/hargaSengaja): layar berhenti menagih sampai modal atau harganya berubah lagi. Ketuk lagi = tagih lagi. */
export function susunSengaja(k, w) {
  const S = hgSemua(new Date(w.kini)); const b = cariBaris(S, k); if (!b) return { tolak: 'Harga itu sudah tidak ada di daftar' };
  const peta = Object.assign({}, petaSengaja());
  if (b.sengaja) { delete peta[k]; return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'hargaSengaja', tanggal: w.tanggal, jam: w.jam, peta } }], patch: { ubah: null, ketik: '', kabar: b.judul + ' ditagih lagi', kabarAwas: false } }; }
  if (b.adaDraf) return { tolak: 'Harga ini sedang jadi draf — buang drafnya dulu kalau mau dibiarkan' };
  if (HG_PERLU.indexOf(b.status) < 0) return { tolak: 'Harga ini tidak sedang ditagih' };
  peta[k] = { modal: Math.round(b.modalUnit), n: b.lamaN, tanggal: w.tanggal };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'hargaSengaja', tanggal: w.tanggal, jam: w.jam, peta } }], patch: { ubah: null, ketik: '', kabar: 'Dicatat sebagai keputusan lu: ' + b.judul + (b.status === 'lubang' ? ' memang tidak dijual' : ' dibiarkan di ' + RP(b.lamaN)) + '. Layar berhenti menagihnya sampai modal atau harganya berubah lagi.', kabarAwas: false } };
}
/** Pakai usul untuk semua yang perlu → tetap DRAF, bukan terbit. */
export function susunUsulSemua(w) {
  const S = hgSemua(new Date(w.kini)); const perlu = S.perlu.filter((b) => b.usul > 0); if (!perlu.length) return { tolak: 'Tidak ada harga yang bisa diusulkan — semua di target, sudah jadi draf, sengaja dibiarkan, atau modalnya belum tercatat' };
  const d = Object.assign({}, S.draf); perlu.forEach((b) => { if (b.usul !== b.lamaN) d[b.k] = b.usul; });
  return { dokumen: [hgDokDraf(d, w)], patch: { kabar: perlu.length + ' usul dijadikan draf. Periksa dulu, baru terbitkan.', kabarAwas: false } };
}

// ---- IDE G · SATU KALIMAT: perintah massal yang BERANGKAT dari harga sekarang; dibulatkan SEARAH perintahnya
export function hitungKalimat(S, kal) {
  const K = Object.assign({ arah: 'naik', merek: 'semua', satuan: 'semua', rp: 100 }, kal || {}); const rp = Math.round(hgAngka(K.rp));
  const cocokSat = (b) => K.satuan === 'semua' || (K.satuan === 'K' ? b.st.id.charAt(0) === 'K' : b.st.id === K.satuan);
  const kena = S.baris.filter((b) => (K.merek === 'semua' || b.merk === K.merek) && cocokSat(b)); const lubang = kena.filter((b) => b.status === 'lubang').length;
  const hitung = kena.filter((b) => b.status !== 'lubang').map((b) => { const mentah = b.n + (K.arah === 'naik' ? 1 : -1) * rp * b.st.kg; const baru = K.arah === 'naik' ? hgBulatAtas(mentah, S.atur[b.st.bulat]) : hgBulatBawah(mentah, S.atur[b.st.bulat]); return { b, baru }; });
  const hasil = rp > 0 ? hitung.filter((x) => x.baru > 0 && x.baru !== x.b.n) : []; const habis = hitung.length - hasil.length;
  const satNama = K.satuan === 'semua' ? 'semua harga' : K.satuan === 'L' ? 'harga literan' : K.satuan === 'S' ? 'harga karung per kg' : K.satuan === 'K' ? 'harga kemasan' : 'harga ' + satuanHarga(K.satuan, '').nama.toLowerCase();
  return { K, rp, kalimat: (K.arah === 'naik' ? 'Naikkan ' : 'Turunkan ') + satNama + ' ' + (K.merek === 'semua' ? 'di semua merek' : K.merek) + ' ' + RP(rp) + ' per kg.',
    hasil: hasil.map((x) => { const N = nilaiHarga(x.baru, x.b.modalUnit, x.b.st.kg, S.target, x.b.naik); const beda = Math.abs(x.baru - x.b.n);
      return { k: x.b.k, judul: x.b.judul, lama: x.b.n, baru: x.baru, rugi: N.status === 'rugi', ket: (K.arah === 'naik' ? 'naik ' : 'turun ') + RP(beda) + ' per ' + x.b.st.per + (Math.abs(beda / x.b.st.kg - rp) > 0.5 ? ' (= ' + RP(beda / x.b.st.kg) + '/kg sesudah dibulatkan)' : '') + ' · ' + (N.status === 'rugi' ? 'jadi RUGI ' + RP(-N.margin) + '/kg' : N.status === 'tanpaModal' ? 'modal belum tercatat' : 'untung jadi ' + RP(N.margin) + '/kg') }; }),
    kosongTeks: !(rp > 0) ? 'Ketik berapa rupiah per kg.' : kena.length && kena.length === lubang ? 'Tidak ada harga yang kena — semua yang terpilih belum punya harga. Isi dulu harganya.' : 'Tidak ada harga yang berubah dengan perintah ini.',
    lewat: (lubang ? lubang + ' harga belum ada, jadi tidak ikut. ' : '') + (habis > 0 && rp > 0 ? habis + ' harga tidak ikut karena hasilnya tidak berubah atau habis jadi nol. ' : '') + 'Dibulatkan searah perintahnya — naik ke atas, turun ke bawah — memakai pembulatan di Atur.' };
}
export function susunKalimatDraf(kal, w) {
  const S = hgSemua(new Date(w.kini)); const K = hitungKalimat(S, kal); if (!K.hasil.length) return { tolak: K.kosongTeks };
  const d = Object.assign({}, S.draf); K.hasil.forEach((x) => { const b = cariBaris(S, x.k); if (x.baru === b.lamaN) delete d[x.k]; else d[x.k] = x.baru; });
  return { dokumen: [hgDokDraf(d, w)], patch: { kabar: K.hasil.length + ' harga dijadikan draf. Ketuk lagi kalau mau ' + (K.K.arah === 'naik' ? 'naik' : 'turun') + ' selangkah lagi — terbitkan kalau sudah pas.', kabarAwas: false } };
}

// ---- IDE H · TIMBANG DAMPAK: urut menurut RUPIAH per bulan (selisih × terjual 30 hari); anggapan pembeli tidak berkurang DISEBUT
export function susunDampak(S) {
  const dampak = (b) => (!b.adaDraf && !b.sengaja && ['rugi', 'dimakan', 'bawah'].indexOf(b.status) >= 0 && b.usul > 0 ? Math.round((b.usul - b.n) * b.laku) : 0);
  const drafDampak = (b) => (b.adaDraf && b.lamaN > 0 ? Math.round((b.n - b.lamaN) * b.laku) : 0);
  const untungBulan = (b) => (b.status === 'lubang' || b.status === 'tanpaModal' ? 0 : Math.round((b.n - b.modalUnit) * b.laku));
  const totalTinggal = S.baris.reduce((a, b) => a + dampak(b), 0), totalDraf = S.baris.reduce((a, b) => a + drafDampak(b), 0);
  const maks = Math.max(1, ...S.baris.map((b) => Math.max(dampak(b), Math.abs(drafDampak(b))))); const laku = (b) => String(b.laku).replace('.', ',') + ' ' + b.st.per + ' sebulan';
  const baris = (b, angka, kecil, sub) => ({ k: b.k, judul: b.judul, cap: b.adaDraf ? 'draf' : b.sengaja ? 'sengaja' : b.cap, status: b.status, sub, angka, kecil, lebar: Math.round(Math.max(dampak(b), Math.abs(drafDampak(b))) / maks * 100), adaPakai: dampak(b) > 0, usul: b.usul });
  const kelompok = []; const tambah = (judul, ket, awas, isi) => { if (isi.length) kelompok.push({ judul, ket, awas, isi }); };
  const terasa = S.baris.filter((b) => dampak(b) > 0).sort((a, b) => dampak(b) - dampak(a)); const subPerlu = (b) => laku(b) + ' · ' + (b.status === 'rugi' ? 'RUGI ' + RP(-b.margin) + '/kg' : 'kurang ' + RP(S.target - b.margin) + '/kg dari target');
  const besar = terasa.filter((b) => dampak(b) >= S.atur.ambangDampak), kecil = terasa.filter((b) => dampak(b) < S.atur.ambangDampak);
  tambah('Paling terasa di kantong', RP(besar.reduce((a, b) => a + dampak(b), 0)) + '/bulan', true, besar.map((b) => baris(b, '+' + RP(dampak(b)), '/bulan', subPerlu(b))));
  tambah('Tidak seberapa', 'di bawah ' + RP(S.atur.ambangDampak) + '/bulan', false, kecil.map((b) => baris(b, '+' + RP(dampak(b)), '/bulan', subPerlu(b))));
  tambah('Sudah jadi draf', (totalDraf > 0 ? '+' : '') + RP(totalDraf) + '/bulan', false, S.baris.filter((b) => b.adaDraf).map((b) => baris(b, b.lamaN > 0 ? (drafDampak(b) > 0 ? '+' : '') + RP(drafDampak(b)) : 'harga baru', b.lamaN > 0 ? '/bulan' : '', b.lamaN > 0 ? laku(b) + ' · ' + RP(b.lamaN) + ' → ' + RP(b.n) : 'belum pernah dijual dari katalog — belum bisa dibandingkan')));
  tambah('Belum ada harganya', 'belum bisa dihitung', true, S.baris.filter((b) => !b.adaDraf && !b.sengaja && b.status === 'lubang').map((b) => baris(b, 'isi harga', '', b.laku > 0 ? 'terjual ' + laku(b) + ' lewat harga ketikan' : 'belum pernah dijual dari katalog' + (b.usul ? ' · usul ' + RP(b.usul) : ''))));
  tambah('Di bawah target, tapi tidak ada yang terjual', 'tidak ada yang tertinggal', false, S.baris.filter((b) => !b.adaDraf && !b.sengaja && ['rugi', 'dimakan', 'bawah'].indexOf(b.status) >= 0 && dampak(b) === 0).map((b) => baris(b, RP(b.n), '', laku(b) + (b.usul ? ' · tidak ada yang terjual, jadi tidak ada yang tertinggal' : ' · modal belum tercatat'))));
  tambah('Sudah di target', 'untung kotor sebulan', false, S.baris.filter((b) => !b.adaDraf && (b.status === 'aman' || b.status === 'nol')).sort((a, b) => untungBulan(b) - untungBulan(a)).map((b) => baris(b, RP(untungBulan(b)), '/bulan', laku(b) + ' · untung ' + RP(b.margin) + '/kg')));
  tambah('Modalnya belum tercatat', 'belum bisa dinilai', false, S.baris.filter((b) => !b.adaDraf && b.status === 'tanpaModal').map((b) => baris(b, RP(b.n), '', laku(b) + ' · belum ada kedatangan / adukan yang memberi modal')));
  tambah('Sengaja dibiarkan', 'tidak ditagih lagi', false, S.baris.filter((b) => b.sengaja).map((b) => baris(b, b.status === 'lubang' ? 'tidak dijual' : RP(b.n), '', b.status === 'lubang' ? 'ukuran ini memang tidak dijual' : laku(b) + ' · untung ' + RP(b.margin) + '/kg — keputusan lu')));
  return { totalTinggal, totalDraf, kelompok, untungBulan: S.baris.reduce((a, b) => a + untungBulan(b), 0),
    label: totalTinggal > 0 ? 'per bulan tertinggal di meja' : 'tidak ada yang tertinggal — semua harga sudah di target atau sudah jadi draf',
    syarat: 'Dihitung dari yang terjual ' + HG_HARI_LAKU + ' hari terakhir, dengan anggapan pembelinya TIDAK berkurang. Harga naik bisa membuat sebagian pindah — itu lu yang tahu, bukan layar ini.' };
}
export function susunPakaiUsul(k, w) {
  const S = hgSemua(new Date(w.kini)); const b = cariBaris(S, k); if (!b) return { tolak: 'Harga itu sudah tidak ada' }; if (!(b.usul > 0)) return { tolak: 'Belum bisa diusulkan — modalnya belum tercatat' };
  const d = Object.assign({}, S.draf); if (b.usul === b.lamaN) delete d[k]; else d[k] = b.usul;
  return { dokumen: [hgDokDraf(d, w)], patch: { kabar: b.judul + ' dijadikan draf ' + RP(b.usul), kabarAwas: false } };
}

// ---- IDE I · MODAL DAN PASAR: harga pasar = CATATAN owner (koleksi hargaPasar), tak pernah jadi draf, tak pernah sampai ke kasir
export function susunPasar(S) {
  const info = (b) => { const P = b.pasar ? b.pasar.harga : 0; const mu = b.modalUnit; const tu = mu + S.target * b.st.kg; const ada = b.status !== 'lubang';
    const ps = !P ? 'kosong' : !(mu > 0) ? 'tanpaModal' : P < mu - 0.5 ? 'bawahModal' : ada && b.n > P ? 'atas' : b.usul > P ? 'sempit' : 'ruang';
    const teks = ps === 'kosong' ? 'pasar belum diisi' : ps === 'tanpaModal' ? 'pasar ' + RP(P) + ' · modal belum tercatat' : ps === 'bawahModal' ? 'pasar ' + RP(P) + ' — DI BAWAH modal lu ' + RP((mu - P) / b.st.kg) + '/kg' : ps === 'atas' ? RP(b.n - P) + ' DI ATAS pasar (' + RP(P) + ')'
      : ps === 'sempit' ? 'target tidak muat — pasar cuma ' + RP((P - mu) / b.st.kg) + '/kg di atas modal' : !ada ? 'pasar ' + RP(P) : b.n === P ? 'sama dengan pasar' : RP(P - b.n) + ' di bawah pasar — masih ada ruang';
    const titik = (mu > 0 ? [mu, tu] : []).concat(P ? [P] : []).concat(ada ? [b.n] : []); const lo = titik.length ? Math.min(...titik) : 0, hi = titik.length ? Math.max(...titik) : 0; const pos = (x) => (hi - lo < 1 ? 50 : Math.round((6 + (x - lo) / (hi - lo) * 88) * 10) / 10);
    return { ps, teks, awas: ps === 'bawahModal' || ps === 'atas', pM: mu > 0 ? pos(mu) : 0, pT: mu > 0 ? pos(tu) : 0, pP: P ? pos(P) : 0, pN: ada ? pos(b.n) : 0, adaPasar: P > 0, adaTitik: ada, adaModal: mu > 0, zKiri: mu > 0 && P >= mu ? pos(mu) : 0, zLebar: mu > 0 && P >= mu ? Math.round((pos(P) - pos(mu)) * 10) / 10 : 0, pasarTanggal: b.pasar ? b.pasar.tanggal : '' }; };
  const baris = S.baris.map((b) => Object.assign({ k: b.k, merk: b.merk, judul: b.judul, satuan: b.st.nama, n: b.n, status: b.status, cap: b.adaDraf ? 'draf' : b.cap, margin: b.margin }, info(b)));
  const hit = (u) => baris.filter((x) => x.ps === u).length;
  return { baris, ringkas: [['atas', 'di atas pasar'], ['bawahModal', 'pasar di bawah modal'], ['sempit', 'target tidak muat'], ['kosong', 'pasar belum diisi']].map((r) => ({ id: r[0], a: hit(r[0]), l: r[1], nyala: hit(r[0]) > 0 && (r[0] === 'atas' || r[0] === 'bawahModal') })) };
}

// ---- IDE J · LABEL RAK: harga TERBIT meninggalkan tugas ganti label; yang diingat = angka yang masih TERTULIS di label
export function susunLabelTugas(S) {
  const tugas = daftarLabel().map((t) => { const b = cariBaris(S, t.k); return { k: t.k, judul: b ? b.judul : t.k, lama: Number(t.lama) || 0, tanggal: t.tanggal || '', tulis: b ? b.lamaN : 0 }; });
  return { tugas, ada: tugas.length > 0, judul: tugas.length + ' label di toko masih harga lama', arti: 'Harga yang terbit langsung dipakai kasir, tapi label di rak dan papan harga masih tulisan lama sampai ada yang menggantinya. Draf tidak membuat tugas — cuma yang sudah terbit.' };
}
export function susunLabelSelesai(k, w) {
  const daftar = daftarLabel(); if (!daftar.length) return { tolak: 'Tidak ada label yang menunggu diganti' }; if (k !== 'semua' && !daftar.some((x) => x.k === k)) return { tolak: 'Label itu sudah tidak ada di daftar' };
  const sisa = k === 'semua' ? [] : daftar.filter((x) => x.k !== k);
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'hargaLabel', tanggal: w.tanggal, jam: w.jam, daftar: sisa } }], patch: { kabar: k === 'semua' ? 'Semua label dicatat sudah diganti' : 'Label dicatat sudah diganti', kabarAwas: false } };
}

// ---- IDE K · PAPAN KAPUR: papan harga toko sebagai bendanya; sisi pembeli = HANYA harga yang sudah terbit; teks daftar harga untuk WhatsApp
export function susunPapan(S, sisi) {
  const owner = sisi !== 'pembeli';
  const baris = S.merk.map((m) => { const sel = S.baris.filter((b) => b.merk === m).map((b) => { const tampil = owner ? b.n : b.lamaN; const kosong = !(tampil > 0);
    return { k: b.k, satuan: b.st.pendek, harga: kosong ? (owner && !b.sengaja ? 'isi' : '—') : tampil, kosong, untung: owner && !kosong && b.status !== 'tanpaModal' ? (b.margin >= 0 ? '+' : '−') + Math.round(Math.abs(b.margin)) : '', lama: owner && b.adaDraf && b.lamaN ? b.lamaN : 0,
      kelas: !owner ? '' : b.adaDraf ? 'draf' : kosong ? (b.sengaja ? '' : 'lubang') : !b.sengaja && (b.status === 'rugi' || b.status === 'dimakan') ? 'awas' : '' }; });
    const modal = S.baris.find((b) => b.merk === m && b.modalKg > 0); return { merk: m, modal: modal ? modal.modalKg : 0, sel }; });
  return { owner, baris, sub: owner ? 'kuning = draf · merah = rugi atau modal naik · bertepi putus = belum ada harga · angka kecil = untung per kg' : 'persis seperti yang digantung — draf belum tampil' };
}
export function teksWaHarga(S, tanggal) {
  const baris = ['*HARGA BERAS HARI INI*', 'Toko Beras M.IQBAL · ' + (tanggal || '')];
  S.merk.forEach((m) => { const ada = S.baris.filter((b) => b.merk === m && b.lamaN > 0); if (ada.length) baris.push('• ' + m + ' — ' + ada.map((b) => b.st.pendek + ' ' + RP(b.lamaN).replace('Rp', '')).join(' · ')); });
  return { baris, arti: S.nDraf ? 'Yang dikirim cuma harga yang SUDAH terbit. ' + S.nDraf + ' draf lu belum ikut — terbitkan dulu kalau mau ikut.' : 'Yang dikirim = harga yang sedang dipakai kasir.', tautan: 'https://wa.me/?text=' + encodeURIComponent(baris.join('\n')) };
}

// ---- IDE L · KARUNG DIBELAH: dari satu harga, berapa yang pergi dan berapa yang TINGGAL — semua komponen bilangan bulat, sisa = harga − komponen (menutup)
export function susunBelah(S, bedah) {
  const B = Object.assign({ merek: '', satuan: '', bayar: 'tunai' }, bedah || {}); const b = cariBaris(S, kunciHarga(B.merek, B.satuan)) || S.baris.find((x) => x.merk === B.merek) || S.baris[0] || null;
  if (!b) return { ada: false, kosongTeks: 'Belum ada baris harga.' };
  const ada = b.status !== 'lubang'; const harga = ada ? b.n : 0; const kg = b.st.kg;
  const beras = b.modalDari === 'adukan' ? (b.modalKg > 0 ? Math.min(Math.round(b.modalUnit), Math.round(b.modalKg * kg)) : Math.round(b.modalUnit)) : Math.round(b.modalUnit);
  const wadah = b.modalDari === 'adukan' ? Math.round(b.modalUnit) - beras : 0; const kemasanUtuh = b.modalDari === 'adukan' && !(b.modalKg > 0);
  const bongkar = Math.round(S.atur.bongkarKg * kg); const kenaMdr = B.bayar === 'qris' && harga > S.atur.mdrBatas; const mdr = kenaMdr ? Math.round(harga * S.atur.mdrPersen / 10000) : 0;
  const makan = bongkar + wadah + mdr; const modal = beras + wadah; const kotor = harga - modal; const sisa = harga - modal - bongkar - mdr; const persen = (x) => (harga > 0 ? (x / harga * 100).toFixed(1).replace('.', ',') + ' %' : '');
  const rinci = [{ nama: kemasanUtuh ? 'modal kemasan (beras + kantong + upah, dari adukan)' : 'ke pemasok (beras)', n: beras, jenis: 'pemasok', ket: kemasanUtuh ? 'dari adukan' : b.modalKg > 0 ? 'modal ' + RP(b.modalKg) + '/kg' : 'modal belum tercatat' },
    { nama: 'kantong + upah kemas', n: wadah, jenis: 'makan', ket: wadah ? 'ikut modal kemasan (adukan)' : b.st.id.charAt(0) === 'K' ? 'belum terpisah dari modal' : 'ukuran ini tidak pakai' },
    { nama: 'ongkos bongkar', n: bongkar, jenis: 'makan', ket: RP(S.atur.bongkarKg) + '/kg' + (S.atur.bongkarTerukur ? ' (terukur dari kedatangan)' : ' (setelan owner)') },
    { nama: 'potongan QRIS', n: mdr, jenis: 'makan', ket: B.bayar !== 'qris' ? 'tunai — tidak dipotong' : kenaMdr ? hgPct(S.atur.mdrPersen) + ' dari harganya' : 'bebas sampai ' + RP(S.atur.mdrBatas) }].map((r) => Object.assign(r, { persen: r.n ? persen(r.n) : '' }));
  return { ada, b, harga, sisa, modal, kotor, makan, beras, wadah, bongkar, mdr, rinci, persen: persen(sisa), perKg: sisa / kg, bayar: B.bayar, kaleng: b.st.id === 'L', skala: b.st.id === 'S' || b.st.kg >= 50 ? 1 : b.st.kg >= 25 ? 0.86 : 0.7,
    judul: ada ? 'Dari tiap ' + b.st.per + ' ' + RP(harga) + (b.adaDraf ? ' (draf)' : '') + ', yang tinggal di toko' : '', sisaTeks: ada ? (sisa >= 0 ? RP(sisa / kg) + ' per kg · ' + persen(sisa) + ' dari harganya' : 'toko NOMBOK ' + RP(-sisa) + ' tiap ' + b.st.per) : '',
    kosongTeks: ada ? '' : b.judul + ' belum punya harga — belum ada yang bisa dibelah.' + (b.usul ? ' Usulnya ' + RP(b.usul) + '.' : ''), awas: ada && sisa < 0, awasTeks: kotor <= 0 ? 'Harga ini tidak menutup harga belinya — tidak ada yang bisa dibagi.' : 'Selisihnya ' + RP(kotor) + ' habis dimakan ongkos ' + RP(makan) + '.',
    fPemasok: Math.max(0, Math.min(modal, harga)), fMakan: kotor > 0 ? Math.min(bongkar + mdr, kotor) : 0, fSisa: Math.max(0, sisa), satuan: S.baris.filter((x) => x.merk === b.merk).map((x) => ({ id: x.st.id, nama: x.st.pendek, aktif: x.k === b.k })), tanpaModal: !(modal > 0) };
}

// ---- TERBITKAN: semua atau tidak sama sekali (satu writeBatch); rugi → dua ketukan; label rak dicatat; riwayat ke hargaTerbit
export function susunTerbit(w, yakin) {
  const S = hgSemua(new Date(w.kini)); const d = S.baris.filter((b) => b.adaDraf); if (!d.length) return { tolak: 'Tidak ada draf — tidak ada yang diterbitkan' };
  const rugi = d.filter((b) => b.status === 'rugi');
  if (rugi.length && !yakin) return { tolak: 'Ada harga di bawah modal: ' + rugi.map((b) => b.judul).join(', ') + '. Boleh — tapi ini keputusan, bukan kebetulan. Ketuk sekali lagi untuk menerbitkan.', perluYakin: true };
  const dokumen = d.map((b) => ({ koleksi: b.koleksi, data: hgDokKatalog(b, w) }));
  let label = daftarLabel().slice(); d.forEach((b) => { const ada = label.find((x) => x.k === b.k); const tertulis = ada ? Number(ada.lama) || 0 : b.lamaN; label = label.filter((x) => x.k !== b.k); if (tertulis !== b.n) label.push({ k: b.k, lama: tertulis, tanggal: w.tanggal }); });
  const sengaja = Object.assign({}, petaSengaja()); let sengajaBerubah = false; d.forEach((b) => { if (sengaja[b.k]) { delete sengaja[b.k]; sengajaBerubah = true; } });
  dokumen.push(hgDokDraf({}, w)); dokumen.push({ koleksi: 'aturanToko', data: { id: 'hargaLabel', tanggal: w.tanggal, jam: w.jam, daftar: label } });
  if (sengajaBerubah) dokumen.push({ koleksi: 'aturanToko', data: { id: 'hargaSengaja', tanggal: w.tanggal, jam: w.jam, peta: sengaja } });
  const daftar = d.map((b) => ({ kunci: b.k, nama: b.judul, lama: b.lamaN, baru: b.n, koleksi: b.koleksi }));
  dokumen.push({ koleksi: 'hargaTerbit', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, n: d.length, daftar } });
  return { dokumen, daftar, nLabel: label.length, patch: { terbit: false, yakinRugi: false, ubah: null, kabar: d.length + ' harga terbit sekaligus — katalog yang dibaca kasir berganti mulai sekarang' + (label.length ? ' · ' + label.length + ' label di toko perlu diganti' : '') + '. Ringkasan kasir HP (ringkasanKasir) diterbitkan ulang oleh sistem lama.', kabarAwas: false } };
}
/** Bentuk dokumen katalog persis simpanHarga* index.html; id lama dipakai lagi bila sudah ada. */
function hgDokKatalog(b, w) {
  const id = b.dok ? b.dok.id : b.st.id === 'K' + b.st.kg ? b.merk.toLowerCase().replace(/\s+/g, '_') + '_' + b.st.kg + 'kg' : b.merk;
  const dasar = { id, merk: b.merk, diubahPada: w.kini, modalSaatSetel: b.modalDari === 'beras' ? Math.round(b.beliTerbaru) : 0 };
  if (b.st.id === 'S') return Object.assign(dasar, { hargaPerKg: b.n }); if (b.st.id === 'L') return Object.assign(dasar, { hargaPerLiter: b.n });
  return Object.assign(dasar, { ukuran: b.st.kg, hargaPerUnit: b.n });
}
export function pratinjauTerbit(S) { const d = S.baris.filter((b) => b.adaDraf); return { daftar: d.map((b) => ({ k: b.k, judul: b.judul, lama: b.lamaN, baru: b.n, rugi: b.status === 'rugi', ket: b.status === 'rugi' ? 'RUGI ' + RP(-b.margin) + '/kg' : b.status === 'tanpaModal' ? 'modal belum tercatat' : 'untung ' + RP(b.margin) + '/kg' })), adaRugi: d.some((b) => b.status === 'rugi'), n: d.length }; }
export function riwayatTerbit(n) {
  const out = []; ambilHargaTerbit().slice().sort((a, b) => String(b.tanggal || '').localeCompare(String(a.tanggal || '')) || String(b.jam || '').localeCompare(String(a.jam || '')) || (Number(b.id) || 0) - (Number(a.id) || 0)).forEach((t) => (t.daftar || []).forEach((x) => out.push({ tanggal: t.tanggal || '', jam: t.jam || '', nama: x.nama, lama: Number(x.lama) || 0, baru: Number(x.baru) || 0, arah: !x.lama ? 'baru' : x.baru > x.lama ? 'naik ' + RP(x.baru - x.lama) : 'turun ' + RP(x.lama - x.baru) })));
  return out.slice(0, n || 12);
}
