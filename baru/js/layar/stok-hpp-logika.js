// LAYAR STOK — HPP / MODAL (ST6-A+B, dikunci owner 19 Sep 2026): kartu modal per nama beras + garis waktu + koreksi (satu nama / massal).
// Kejujuran mesin: MODAL yang dipakai laba & neraca = RATA-RATA TERTIMBANG seluruh kedatangan (hitungStokKarungPerMerk.hppTerakhirPerKg — namanya menyesatkan,
// isinya rata-rata). Aturan owner 13 Sep "penilaian = harga beli TERBARU" belum diterapkan ke mesin (keputusan owner; mengubahnya menggeser laba historis) →
// kartu memajang KEDUANYA berlabel. HPP tidak disimpan sebagai angka sendiri: ia TURUNAN kedatangan. Maka "koreksi HPP" di sini = mengoreksi HARGA BELI PER KG
// pada kedatangan TERAKHIR nama itu (dokumen batchMasuk yang sama, lewat susunSimpanMasuk: alasan wajib, riwayat tercatat) — bukan menimpa angka di tempat lain.
// Angka aneh DITOLAK dengan kalimat (bukan dipotong diam-diam); lonjakan > batas ditanya; di atas harga jual boleh tapi diperingatkan RUGI; margin Rp0 = "disengaja?" (ambang `>`).
// Tiap koreksi menulis perubahan nilai rak (Δ modal rata-rata × sisa kg) ke koleksi baru koreksiHpp. Massal = semua-atau-tidak-sama-sekali (satu writeBatch).
import { hitungStokKarungPerMerk, hitungHppMerkDalamBatch } from '../mesin/beku.js';
import { cariHargaKarungPerKg } from '../mesin/pembantu.js';
import { ambilSemuaBatch, ambilProduksiBerlaku, cacheMentah } from '../data/toko.js';
import { RP } from '../inti/format.js';
import { drafDariKedatangan, susunSimpanMasuk } from './stok-catat-logika.js';

export const ATUR_HPP_BAWAAN = { batasLonjak: 10, lantaiHpp: 5000, kaliMaks: 3 };
export const TAB_HPP = [['kartu', 'Kartu modal'], ['garis', 'Garis waktu'], ['massal', 'Koreksi massal']];
const hpAngka = (v) => { const t = String(v === undefined || v === null ? '' : v).trim(); if (!t) return 0;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : 0; };
const hpKosong = (v) => v === undefined || v === null || String(v).trim() === '';
const hpKG = (n) => String(Math.round(n * 10) / 10).replace('.', ',') + ' kg';
const hpFondasi = (b) => !!(b && (b.stokAwal || b.tutupBuku));
const hpUrutLama = (a, b) => String(a.tanggal || '').localeCompare(String(b.tanggal || '')) || (Number(a.id) || 0) - (Number(b.id) || 0);

export function aturHpp() {
  const a = cacheMentah('aturan').find((d) => String(d.id) === 'hpp') || null;
  const ambil = (k, syarat) => (a && isFinite(Number(a[k])) && syarat(Number(a[k])) ? Number(a[k]) : ATUR_HPP_BAWAAN[k]);
  return { batasLonjak: ambil('batasLonjak', (n) => n >= 0 && n <= 100), lantaiHpp: ambil('lantaiHpp', (n) => n >= 0), kaliMaks: ATUR_HPP_BAWAAN.kaliMaks, dariOwner: !!a, sejak: a ? (a.tanggal || '') : '' };
}
export function susunAturHpp(isi, w) {
  const kini = aturHpp(); const baca = (k, syarat, teks) => { if (hpKosong(isi[k])) return { nilai: kini[k] }; const n = hpAngka(isi[k]); return syarat(n) ? { nilai: n } : { tolak: teks }; };
  const l = baca('batasLonjak', (n) => n >= 0 && n <= 100, 'Batas lonjakan HPP harus 0–100 %'); if (l.tolak) return { tolak: l.tolak };
  const t = baca('lantaiHpp', (n) => n >= 0 && n <= 1000000, 'Lantai HPP per kg harus 0–1.000.000'); if (t.tolak) return { tolak: t.tolak };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'hpp', tanggal: w.tanggal, jam: w.jam, batasLonjak: l.nilai, lantaiHpp: t.nilai } }],
    patch: { aturHp: null, kabar: 'Aturan HPP disimpan — koreksi yang mengubah modal > ' + l.nilai + ' % ditanya · HPP di bawah ' + RP(t.nilai) + '/kg ditolak', kabarAwas: false } };
}

/** Riwayat modal satu nama, lama → baru: tiap kedatangan (baris karung) dengan harga/kg & HPP/kg (harga + bongkar), pindah buku dari takar. */
export function riwayatModal(merk) {
  const out = [];
  ambilSemuaBatch().slice().sort(hpUrutLama).forEach((k) => {
    hitungHppMerkDalamBatch((k.merkList || []).filter((m) => m.bentuk !== 'bal'), Number(k.biayaBongkar) || 0).forEach((m) => { if (m.merk !== merk || !(m.totalKg > 0)) return;
      out.push({ jenis: 'kedatangan', batchId: k.id, tanggal: k.tanggal || '', jam: k.jam || '', pemasok: k.pemasok || (k.stokAwal ? 'stok awal' : k.tutupBuku ? 'saldo pembuka' : '—'), fondasi: hpFondasi(k), dikoreksi: !!k.alasanKoreksi,
        hargaPerKg: Number(m.hargaPerKg) || 0, hppPerKg: m.hppPerKg, totalKg: m.totalKg, beratKarung: Number(m.beratKarung) || 50, sumber: (hpFondasi(k) ? (k.stokAwal ? 'stok awal (fondasi)' : 'saldo pembuka (fondasi)') : 'kedatangan ' + (k.pemasok || '')) + (k.alasanKoreksi ? ' · dikoreksi' : '') }); });
  });
  ambilProduksiBerlaku().filter((p) => p.jadiKarungUtuh && p.merkTujuan === merk).sort(hpUrutLama).forEach((p) => { const kg = (p.ukuranKemasan || 0) * (p.jumlahUnit || 0); if (kg <= 0) return;
    out.push({ jenis: 'pindah', batchId: null, tanggal: p.tanggal || '', jam: p.jam || '', pemasok: '', fondasi: true, hargaPerKg: p.hppSumberPerKgDipakai || 0, hppPerKg: p.hppSumberPerKgDipakai || 0, totalKg: kg, sumber: p.dariTakar ? 'pindah buku dari takar wadah' : 'jadi karung utuh dari adukan' }); });
  return out.sort(hpUrutLama);
}
/** Σ kg masuk & Σ nilai masuk satu nama — rumus yang sama dengan hitungStokKarungPerMerk (rata-rata = nilai ÷ kg). Dijaga uji: hasilnya = mesin. */
export function totalMasuk(merk) { let kg = 0, nilai = 0; riwayatModal(merk).forEach((r) => { kg += r.totalKg; nilai += r.hppPerKg * r.totalKg; }); return { kg, nilai, rata: kg > 0 ? nilai / kg : 0 }; }
const teksMargin = (m) => (m === null ? 'harga jual per kg belum ada di katalog' : m < 0 ? 'RUGI ' + RP(-m) + '/kg' : m === 0 ? 'margin Rp0/kg (disengaja?)' : 'margin ' + RP(m) + '/kg');
const kelasMargin = (m) => (m === null ? 'tanpa' : m < 0 ? 'rugi' : m === 0 ? 'nol' : 'untung');
/** Kartu modal tiap nama beras yang bersisa (atau punya kedatangan): modal rata-rata (buku), harga beli terbaru (aturan owner, pembanding), harga jual, margin, nilai rak. */
export function kartuHpp() {
  const stok = hitungStokKarungPerMerk(); const atur = aturHpp();
  const kartu = Object.keys(stok).sort().map((merk) => { const st = stok[merk]; const riw = riwayatModal(merk); const akhir = riw.filter((r) => r.jenis === 'kedatangan').slice(-1)[0] || null; const bisa = riw.filter((r) => r.jenis === 'kedatangan' && !r.fondasi).slice(-1)[0] || null;
    const sisa = st.sisaKg || 0; const modal = st.hppTerakhirPerKg || 0; const jual = cariHargaKarungPerKg(merk); const margin = jual !== null && jual > 0 ? Math.round(jual - modal) : null; const hppTerbaru = akhir ? akhir.hppPerKg : 0;
    const lonjak = riw.length > 1 && riw[riw.length - 2].hppPerKg > 0 ? Math.round((riw[riw.length - 1].hppPerKg - riw[riw.length - 2].hppPerKg) / riw[riw.length - 2].hppPerKg * 100) : 0;
    return { merk, sisa, modal, hargaTerbaru: st.hargaTerakhirPerKg || 0, hppTerbaru, jual, margin, teksMargin: teksMargin(margin), kelasMargin: kelasMargin(margin), nilaiRak: Math.max(0, sisa) * modal, nilaiTerbaru: Math.max(0, sisa) * hppTerbaru,
      sumber: akhir ? akhir.sumber + ' · ' + akhir.tanggal : 'belum ada kedatangan', nRiwayat: riw.length, bisaKoreksi: !!bisa, targetId: bisa ? bisa.batchId : null, bedaTerbaru: hppTerbaru - modal, lonjakTerakhir: Math.abs(lonjak) > atur.batasLonjak ? lonjak : 0, adaStok: sisa > 0.05 }; })
    .filter((k) => k.adaStok || k.nRiwayat);
  const berisi = kartu.filter((k) => k.adaStok);
  return { kartu, atur, ringkas: { nilai: berisi.reduce((a, k) => a + k.nilaiRak, 0), nilaiTerbaru: berisi.reduce((a, k) => a + k.nilaiTerbaru, 0), rugi: berisi.filter((k) => k.margin !== null && k.margin < 0).length, nol: berisi.filter((k) => k.margin === 0).length, tanpaJual: berisi.filter((k) => k.margin === null).length, n: berisi.length },
    ringkasTeks: 'Nilai rak (modal rata-rata, = Neraca) ' + RP(Math.round(berisi.reduce((a, k) => a + k.nilaiRak, 0))) + ' · bila dinilai harga beli terbaru ' + RP(Math.round(berisi.reduce((a, k) => a + k.nilaiTerbaru, 0))) + ' · ' + (berisi.filter((k) => k.margin !== null && k.margin < 0).length ? berisi.filter((k) => k.margin !== null && k.margin < 0).length + ' nama RUGI' : 'tidak ada yang rugi') + (berisi.filter((k) => k.margin === 0).length ? ' · ' + berisi.filter((k) => k.margin === 0).length + ' margin nol' : '') };
}
/** Garis waktu HPP semua nama (bar relatif ke tertinggi), lonjakan > batas ditandai, koreksi diwarnai. */
export function garisWaktu() {
  const atur = aturHpp(); const stok = hitungStokKarungPerMerk();
  return Object.keys(stok).sort().map((merk) => { const r = riwayatModal(merk); if (!r.length) return null; const maks = Math.max(...r.map((x) => x.hppPerKg), 1);
    return { merk, ket: r.length + ' catatan · modal rata-rata sekarang ' + RP(Math.round(stok[merk].hppTerakhirPerKg || 0)) + '/kg · terbaru ' + RP(Math.round(r[r.length - 1].hppPerKg)) + '/kg',
      baris: r.map((x, i) => { const lalu = i > 0 ? r[i - 1].hppPerKg : 0; const p = lalu > 0 ? Math.round((x.hppPerKg - lalu) / lalu * 100) : 0;
        return { tanggal: x.tanggal, lebar: Math.round(x.hppPerKg / maks * 1000) / 10, koreksi: x.dikoreksi, hpp: Math.round(x.hppPerKg), harga: Math.round(x.hargaPerKg), kg: x.totalKg, sumber: x.sumber, lonjak: i > 0 && Math.abs(p) > atur.batasLonjak ? (p > 0 ? '▲' : '▼') + Math.abs(p) + ' %' : '' }; }) }; }).filter(Boolean);
}
/** Nilai satu angka koreksi (harga beli per kg kedatangan terakhir nama itu): ditolak / lonjakan / rugi / Δ nilai rak — TANPA menulis apa pun. */
export function nilaiKoreksi(merk, hargaBaru) {
  const atur = aturHpp(); const K = kartuHpp().kartu.find((k) => k.merk === merk); if (!K) return { tolak: 'Nama beras itu tidak ada di buku' };
  const riw = riwayatModal(merk); const target = riw.filter((r) => r.jenis === 'kedatangan' && !r.fondasi).slice(-1)[0] || null;
  if (!target) return { tolak: merk + ' belum punya kedatangan yang bisa dikoreksi — modalnya dari stok awal / saldo pembuka (fondasi), tidak diubah dari sini' };
  const n = Math.round(hpAngka(hargaBaru)); if (!(n > 0)) return { tolak: 'Ketik harga beli per kg yang benar' };
  if (n < atur.lantaiHpp) return { tolak: RP(n) + '/kg di bawah lantai ' + RP(atur.lantaiHpp) + ' — tidak masuk akal untuk beras, ditolak (bukan dipotong diam-diam)' };
  if (K.modal > 0 && n > K.modal * atur.kaliMaks) return { tolak: RP(n) + ' lebih dari ' + atur.kaliMaks + '× modal sekarang (' + RP(Math.round(K.modal)) + ') — ditolak, cek angkanya' };
  const bongkarPerKg = target.hppPerKg - target.hargaPerKg; const hppBaru = n + bongkarPerKg;
  const T = totalMasuk(merk); const nilaiBaru = T.nilai - target.hppPerKg * target.totalKg + hppBaru * target.totalKg; const modalBaru = T.kg > 0 ? nilaiBaru / T.kg : 0;
  const pct = K.modal > 0 ? Math.round((modalBaru - K.modal) / K.modal * 100) : 0; const delta = (modalBaru - K.modal) * Math.max(0, K.sisa);
  return { tolak: '', merk, n, target, hppBaru, modalLama: K.modal, modalBaru, delta, sisa: K.sisa, sama: n === target.hargaPerKg,
    lonjak: Math.abs(pct) > atur.batasLonjak ? 'modal rata-rata ' + (pct > 0 ? 'naik ' : 'turun ') + Math.abs(pct) + ' % (' + RP(Math.round(K.modal)) + ' → ' + RP(Math.round(modalBaru)) + ')' : '',
    rugi: K.jual !== null && K.jual > 0 ? (hppBaru > K.jual ? 'HPP kedatangan ini ' + RP(Math.round(hppBaru)) + ' di atas harga jual ' + RP(K.jual) + '/kg — tiap kg dijual RUGI ' + RP(Math.round(hppBaru - K.jual)) : Math.round(hppBaru) === K.jual ? 'sama dengan harga jual — margin Rp0 (disengaja?)' : '') : '',
    teksTarget: 'kedatangan ' + target.pemasok + ' ' + target.tanggal + ' · ' + hpKG(target.totalKg) + ' · harga ' + RP(target.hargaPerKg) + '/kg' + (bongkarPerKg ? ' + bongkar ' + RP(Math.round(bongkarPerKg)) + '/kg' : ''),
    teksDelta: 'Nilai rak ' + merk + ' ' + (delta >= 0 ? 'naik ' : 'turun ') + RP(Math.round(Math.abs(delta))) + ' (' + RP(Math.round(modalBaru - K.modal)) + '/kg × ' + hpKG(Math.max(0, K.sisa)) + ') — kekayaan toko ikut ' + (delta >= 0 ? 'naik' : 'turun') };
}
function hpDrafUntuk(peta, w) {
  // kelompokkan koreksi per batch: dua nama di kedatangan yang sama → SATU dokumen; baris nama itu (semua beratnya) diberi harga baru
  const perBatch = {}; Object.keys(peta).forEach((merk) => { const v = peta[merk]; if (!perBatch[v.target.batchId]) perBatch[v.target.batchId] = {}; perBatch[v.target.batchId][merk] = v.n; });
  const hasil = [];
  Object.keys(perBatch).forEach((id) => { const d = drafDariKedatangan(id); if (!d) { hasil.push({ tolak: 'Kedatangan ' + id + ' sudah tidak ada' }); return; }
    d.baris.forEach((b) => { if (perBatch[id][b.merk] !== undefined) b.hargaPerKg = String(perBatch[id][b.merk]); }); d.alasan = 'koreksi HPP: ' + w.alasan;
    hasil.push(susunSimpanMasuk(d, w, true)); });
  return hasil;
}
/** Koreksi satu nama. yakin = sudah ditanya soal lonjakan. */
export function susunKoreksiHpp(merk, hargaBaru, alasan, w, yakin) {
  const v = nilaiKoreksi(merk, hargaBaru); if (v.tolak) return { tolak: v.tolak };
  if (v.sama) return { tolak: 'Harga yang diketik sama dengan yang tercatat (' + RP(v.n) + '/kg) — tidak ada yang dikoreksi' };
  if (hpKosong(alasan)) return { tolak: 'Koreksi HPP butuh alasan (mis. bongkar belum masuk, salah ketik harga)' };
  if (v.lonjak && !yakin) return { tolak: 'HPP: ' + v.lonjak + ' — ketuk sekali lagi kalau memang benar', perluYakin: true };
  const peta = {}; peta[merk] = v; const r = hpDrafUntuk(peta, { tanggal: w.tanggal, jam: w.jam, idUnik: w.idUnik, alasan: String(alasan).trim() })[0]; if (r.tolak) return { tolak: r.tolak };
  const log = { koleksi: 'koreksiHpp', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, merk, batchId: String(v.target.batchId), hargaDari: v.target.hargaPerKg, hargaKe: v.n, modalDari: Math.round(v.modalLama * 100) / 100, modalKe: Math.round(v.modalBaru * 100) / 100, sisaKg: Math.round(v.sisa * 100) / 100, deltaNilai: Math.round(v.delta), alasan: String(alasan).trim() } };
  return { dokumen: r.dokumen.concat([log]), nilai: v, patch: { hp: { merk, ketik: '', alasan: '', yakin: false, massal: {}, tab: 'kartu' }, kabar: merk + ': harga kedatangan ' + v.target.tanggal + ' ' + RP(v.target.hargaPerKg) + ' → ' + RP(v.n) + '/kg (' + String(alasan).trim() + '). Modal rata-rata ' + RP(Math.round(v.modalLama)) + ' → ' + RP(Math.round(v.modalBaru)) + '/kg; nilai rak ' + (v.delta >= 0 ? 'naik ' : 'turun ') + RP(Math.round(Math.abs(v.delta))) + '.', kabarAwas: false } };
}
/** Koreksi massal: peta {merk: harga}; SEMUA-ATAU-TIDAK — satu angka ditolak = tidak ada yang ditulis. Satu alasan. */
export function susunKoreksiMassal(petaHarga, alasan, w) {
  const merk = Object.keys(petaHarga || {}).filter((m) => !hpKosong(petaHarga[m]));
  if (!merk.length) return { tolak: 'Belum ada nama yang disiapkan' };
  const nilai = {}; const salah = [];
  merk.forEach((m) => { const v = nilaiKoreksi(m, petaHarga[m]); if (v.tolak) salah.push(m + ': ' + v.tolak); else if (v.sama) salah.push(m + ': sama dengan yang tercatat'); else nilai[m] = v; });
  if (salah.length) return { tolak: salah.join(' · ') + ' — TIDAK ADA yang disimpan sampai semuanya beres', salah };
  if (hpKosong(alasan)) return { tolak: 'Koreksi massal butuh satu alasan untuk semua' };
  const hasil = hpDrafUntuk(nilai, { tanggal: w.tanggal, jam: w.jam, idUnik: w.idUnik, alasan: String(alasan).trim() }); const gagal = hasil.find((r) => r.tolak); if (gagal) return { tolak: gagal.tolak };
  const delta = Object.keys(nilai).reduce((a, m) => a + nilai[m].delta, 0);
  const dokumen = []; hasil.forEach((r) => r.dokumen.forEach((d) => dokumen.push(d)));
  Object.keys(nilai).forEach((m) => { const v = nilai[m]; dokumen.push({ koleksi: 'koreksiHpp', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, merk: m, batchId: String(v.target.batchId), hargaDari: v.target.hargaPerKg, hargaKe: v.n, modalDari: Math.round(v.modalLama * 100) / 100, modalKe: Math.round(v.modalBaru * 100) / 100, sisaKg: Math.round(v.sisa * 100) / 100, deltaNilai: Math.round(v.delta), alasan: String(alasan).trim(), massal: merk.length } }); });
  return { dokumen, delta, n: merk.length, patch: { hp: { merk: null, ketik: '', alasan: '', yakin: false, massal: {}, tab: 'massal' }, kabar: merk.length + ' nama dikoreksi sekaligus (' + String(alasan).trim() + ') — nilai rak ' + (delta >= 0 ? 'naik ' : 'turun ') + RP(Math.round(Math.abs(delta))) + '. Semuanya masuk atau tidak sama sekali.', kabarAwas: false } };
}
/** Pratinjau massal untuk layar: tiap nama yang disiapkan dinilai; label tombol & Δ total. */
export function pratinjauMassal(petaHarga) {
  const merk = Object.keys(petaHarga || {}).filter((m) => !hpKosong(petaHarga[m])); const baris = merk.map((m) => { const v = nilaiKoreksi(m, petaHarga[m]); return { merk: m, harga: Math.round(hpAngka(petaHarga[m])), tolak: v.tolak || (v.sama ? 'sama dengan yang tercatat' : ''), ket: v.tolak || (v.sama ? 'sama dengan yang tercatat' : v.rugi || v.lonjak || 'wajar'), delta: v.tolak ? 0 : v.delta }; });
  const bermasalah = baris.filter((b) => b.tolak); const delta = baris.reduce((a, b) => a + b.delta, 0);
  return { baris, n: merk.length, bermasalah, delta, siap: merk.length > 0 && !bermasalah.length,
    teks: !merk.length ? 'Ketuk nama, ketik harga beli/kg baru, "siapkan" — lalu terapkan sekaligus' : bermasalah.length ? bermasalah.map((b) => b.merk).join(', ') + ' angkanya ditolak — TIDAK ADA yang disimpan sampai semuanya beres' : 'Disiapkan ' + merk.length + ' nama · nilai rak berubah ' + (delta >= 0 ? '+' : '−') + RP(Math.round(Math.abs(delta))) };
}
export function logKoreksi(n) { return cacheMentah('koreksiHpp').slice().sort((a, b) => (Number(b.id) || 0) - (Number(a.id) || 0)).slice(0, n || 10); }
