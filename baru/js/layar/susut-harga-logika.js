// SUSUT · HPP & HARGA MINIMUM (owner 26 Nov 2026, sensus ulang bagian 1c — satu paket). Logika tanpa DOM, nama berawalan sh (bundel uji jsc satu lingkup).
// Dijaga alat-uji/uji_susut_harga.py (kotak pasir + --kontrol + asap cadangan toko).
//
// KEPUTUSAN OWNER (AskUserQuestion 26 Nov 2026): (1) target susut se-toko per bulan = susut 3 bulan terakhir yang tercatat (TERUKUR) sampai owner mengetik
// angka sendiri; ambang per merek kuning 0,5 % · merah 1 % (setelan aturanToko/merekLaporan, laporan-logika aturMerek). (2) penyebut susut % TETAP "beras yang
// keluar" (laporan-logika LP_RUMUS_SUSUT). (3) harga jual minimum = modal + biaya toko per kg (rata-rata 3 bulan terakhir yang SELESAI) + target laba per kg
// (bawaan Rp0 = impas) — di bawah minimum DITANDAI, tetap boleh terbit. (4) alarm "modal + biaya per kg mendekati HET" bawaan Rp500/kg dari HET.
// Angka kebijakan = setelan owner (aturanToko/hargaMinimum), bukan konstanta. Peringatan memperingatkan, tidak memblokir.
//
// ATURAN: TIDAK ADA RUMUS UANG BARU yang menulis. Modul ini membaca fungsi sumber layar lain apa adanya: merekBulan / susutRentang (Laporan › Laba › Per merek),
// kbBiayaKgBulan (Laporan › Biaya: biaya toko ÷ kg terjual), hgSemua (Harga › Katalog: modal per kg buku, FIFO bila saklar menyala), hetKatalog (HET),
// barangCocok (Stok › Cocokkan), rekapTimbangMutu (Barang masuk), ingatNeraca (neraca per tanggal), ugLabaBersih (mesin laba). Satu-satunya dokumen yang
// ditulis = setelan aturanToko/hargaMinimum. Kalkulator sebelum beli TIDAK menulis apa pun.
//
// SUSUT di harga: TIDAK masuk harga minimum (rumus yang owner setujui: modal + biaya + laba). Ditampilkan di sampingnya sebagai "HPP layak jual" (A64) = modal
// beras ÷ (1 − target susut) dan "minimum kalau susut ikut" — angka bantu, tidak menyalakan tanda. Kemasan hasil adukan tidak dikenai: susut adukannya sudah di modalnya.
import { akhirBulanIso, MULAI_SUSUT_LABA, batchDiutang } from '../mesin/pembantu.js';
import { ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilSemuaBatch, ambilBahanKemasan, ambilBahanLiteran, ambilProduksiBerlaku, ingatPerVersi, ingatNeraca, tahunDiarsip, catatanPertama, ambilAbsenKaryawan } from '../data/toko.js';
import { RP, KG, hariIniIso, tanggalPendek } from '../inti/format.js';
import { ugAturDok, ugAngka, ugKosong, ugLabaBersih, ugTambahHari } from './uang-logika.js';
import { aturMerek, merekBulan, susutRentang, lpPersenTeks, daftarBulan, lpNamaBulan, daftarMinggu } from './laporan-logika.js';
import { kbBiayaKgBulan } from './kendali-biaya-logika.js';
import { hgSemua } from './harga-logika.js';
import { hetKatalog, hetAtur } from './het-logika.js';
import { barangCocok, rekapTimbangMutu } from './stok-catat-logika.js';
import { hitunganFisik } from './jual-logika.js';

export const SH_ID = 'hargaMinimum';
export const SH_BAWAAN = { targetLabaPerKg: 0, jarakHet: 500 };
export const SH_BULAN = 3;   // target susut terukur & biaya per kg = 3 bulan terakhir yang selesai (keputusan owner 26 Nov 2026)
export const SH_RUMUS_MINIMUM = 'Harga minimum per kg = modal per kg + biaya toko per kg terjual (rata-rata 3 bulan terakhir yang selesai) + target laba per kg';
export const SH_RUMUS_LAYAK = 'HPP layak jual = modal per kg ÷ (1 − target susut) — beras yang hilang di gudang ikut ditanggung beras yang terjual';
export const SH_SARAN_HET = ['tawar harga beli atau cari pemasok lain untuk kelas ini', 'geser porsi jualan ke kelas premium (HET-nya lebih tinggi)', 'tekan biaya toko per kg (lihat Laporan › Biaya)', 'kurangi susut gudang (Cocokkan lebih sering, cek karung bocor)'];
const shBulat = (n) => Math.round(n * 100) / 100;
const shKini = (kini) => kini || new Date();

// ==================== SETELAN harga minimum (owner) ====================
/** Setelan aturanToko/hargaMinimum: target laba per kg (Rp, bawaan 0 = impas) & jarak alarm ke HET (Rp/kg, bawaan 500). */
export function shAtur() {
  const d = ugAturDok(SH_ID); const a = d || {}; const ambil = (k, b) => { const n = Number(a[k]); return a[k] !== undefined && a[k] !== null && a[k] !== '' && isFinite(n) && n >= 0 ? n : b; };
  return { targetLabaPerKg: ambil('targetLabaPerKg', SH_BAWAAN.targetLabaPerKg), jarakHet: ambil('jarakHet', SH_BAWAAN.jarakHet), dariOwner: !!d, tanggal: d ? String(d.tanggal || '') : '' };
}
/** Simpan setelan (isi = ketikan; kosong = bawaan). Satu dokumen milik toko — tidak menyentuh harga, stok, maupun uang. */
export function susunAturMinimum(isi, w) {
  const I = isi || {}; const t = ugKosong(I.targetLabaPerKg) ? SH_BAWAAN.targetLabaPerKg : ugAngka(I.targetLabaPerKg); const j = ugKosong(I.jarakHet) ? SH_BAWAAN.jarakHet : ugAngka(I.jarakHet);
  if (!(isFinite(t) && t >= 0 && t <= 100000)) return { tolak: 'Target laba per kg ditulis dalam rupiah: 0 sampai 100.000 (0 = harga minimum sama dengan impas)' };
  if (!(isFinite(j) && j >= 0 && j <= 100000)) return { tolak: 'Jarak alarm ke HET ditulis dalam rupiah per kg: 0 sampai 100.000 (500 = menyala kalau modal + biaya tinggal Rp500 dari HET)' };
  const tb = Math.round(t), jb = Math.round(j);
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: SH_ID, tanggal: w.tanggal, jam: w.jam, targetLabaPerKg: tb, jarakHet: jb } }],
    patch: { aturMin: null, kabar: 'Setelan harga minimum tersimpan — target laba ' + RP(tb) + '/kg' + (tb ? '' : ' (harga minimum = impas)') + ' · alarm HET menyala ' + RP(jb) + '/kg sebelum HET', kabarAwas: false } };
}

// ==================== SUSUT: target, tren, opname, per pemasok ====================
/** merekBulan diingat per versi data & hari (dipakai target, tren, dasbor — tidak dihitung berkali-kali). */
function shMerekBulan(key, kini) { return ingatPerVersi('shMerekBulan|' + key + '|' + hariIniIso(shKini(kini)), () => merekBulan(key, shKini(kini))); }
/**
 * TARGET SUSUT se-toko per bulan (A8). Owner mengetik angka → itu; kosong → TERUKUR = susut beras 3 bulan terakhir yang SELESAI dan susutnya tercatat,
 * digabung (Σ kg hilang ÷ Σ (kg keluar + kg hilang) — rumus % yang sama dengan Per merek, bukan rata-rata persen). Tanpa satu pun bulan tercatat = null
 * ("belum bisa dihitung", bukan 0 %).
 */
export function shTarget(kini) { const iso = hariIniIso(shKini(kini)); return ingatPerVersi('shTarget|' + iso, () => shTargetHitung(shKini(kini))); }
function shTargetHitung(kini) {
  const A = aturMerek(); const kunci = hariIniIso(kini).slice(0, 7); const dipakai = [];
  daftarBulan(kini, 15).forEach((b) => { if (dipakai.length >= SH_BULAN || b.key >= kunci || akhirBulanIso(b.key) < MULAI_SUSUT_LABA || tahunDiarsip(b.key)) return;
    const M = shMerekBulan(b.key, kini); if (!M || M.diarsip || !M.susut || !M.susut.dihitung || M.susut.pct === null) return; dipakai.push({ key: b.key, nama: M.nama, kg: M.susut.kg, kgJual: M.susut.kgJual, pct: M.susut.pct }); });
  const kg = dipakai.reduce((a, x) => a + x.kg, 0); const jual = dipakai.reduce((a, x) => a + x.kgJual, 0); const terukur = dipakai.length && jual + kg > 0 ? kg / (jual + kg) * 100 : null;
  const pct = A.targetSusutPersen !== null ? A.targetSusutPersen : terukur;
  const asal = A.targetSusutPersen !== null ? 'angka owner' : terukur === null ? 'belum bisa dihitung — belum ada bulan selesai yang susutnya tercatat' : 'susut ' + dipakai.map((x) => x.nama).join(', ') + ' digabung (' + KG(kg) + ' hilang dari ' + KG(jual + kg) + ' beras keluar)';
  return { pct, dariOwner: A.targetSusutPersen !== null, terukur: { pct: terukur, bulan: dipakai, n: dipakai.length }, kuning: A.ambangSelidikPersen, merah: A.ambangSusutPersen, asal,
    teks: pct === null ? 'Target susut belum bisa dihitung — belum ada bulan selesai yang susutnya tercatat; isi sendiri di Atur.' : 'Target susut se-toko ' + lpPersenTeks(pct) + ' per bulan (' + asal + ').' };
}
/** Banding satu persen dengan target: 'diAtas' (lebih dari target) · 'diBawah' (sama atau kurang) · null (salah satunya belum bisa dihitung). */
export const shBandingTarget = (pct, target) => (pct === null || pct === undefined || target === null || target === undefined ? null : pct > target ? 'diAtas' : 'diBawah');
/** Barang yang DIHITUNG fisik di rentang itu (Cocokkan tumpukan / kemasan — termasuk yang cocok persis sejak jejak cocokPersis): nama buku → tanggal terakhir. */
function shDihitung(awal, akhir) {
  const tump = {}; const kem = {}; const dalam = (t) => !!t && t >= awal && t <= akhir;
  ambilPenyesuaianStok().forEach((d) => { if (!hitunganFisik(d) || !d.merk || d.bagian === 'wadah' || !dalam(d.tanggal)) return; const cap = d.tanggal + ' ' + (d.jam || ''); if (!tump[d.merk] || cap > tump[d.merk]) tump[d.merk] = cap; });
  ambilPenyesuaianKemasan().forEach((d) => { if (!d.namaProduk || !dalam(d.tanggal) || d.dariRework) return; const k = String(d.namaProduk) + '|' + Number(d.ukuranKemasan); const cap = d.tanggal + ' ' + (d.jam || ''); if (!kem[k] || cap > kem[k]) kem[k] = cap; });
  return { tump, kem };
}
/**
 * TREN susut % per bulan vs target (A8): n bulan terakhir (yang punya susut tercatat sejak 1 Sep 2026), tiap bulan dari merekBulan apa adanya + berapa buku
 * beras yang dihitung fisik bulan itu. Bulan tahun yang sudah ditutup buku = diarsip (disebut).
 */
export function shTren(kini, n) {
  const k = shKini(kini); const iso = hariIniIso(k); return ingatPerVersi('shTren|' + iso + '|' + (n || 6), () => {
    const T = shTarget(k); const bulan = daftarBulan(k, n || 6).filter((b) => akhirBulanIso(b.key) >= MULAI_SUSUT_LABA).map((b) => {
      if (tahunDiarsip(b.key)) return { key: b.key, nama: b.nama, pendek: b.pendek, berjalan: b.berjalan, diarsip: true, pct: null, status: null };
      const M = shMerekBulan(b.key, k); const S = M.susut || {}; const D = shDihitung(b.key + '-01', akhirBulanIso(b.key));
      return { key: b.key, nama: b.nama, pendek: b.pendek, berjalan: b.berjalan, diarsip: false, pct: S.pct === undefined ? null : S.pct, kg: S.kg || 0, rp: S.rp || 0, laporan: S.laporan || 0, nDicocok: S.nDicocok || 0,
        nKuning: (S.selidik || []).length, nMerah: (S.tinggi || []).length, nHitung: Object.keys(D.tump).length, status: shBandingTarget(S.pct === undefined ? null : S.pct, T.pct) }; }).reverse();
    const maks = Math.max(0.0001, T.pct || 0, ...bulan.map((b) => (b.pct > 0 ? b.pct : 0)));
    return { target: T, bulan, maks };
  });
}
/**
 * OPNAME BULAN INI (A135): tiap buku beras yang punya stok (Stok › Cocokkan › Tumpukan) dan tiap kemasan yang punya stok — sudah dihitung fisik bulan ini atau
 * belum (terakhir dihitung kapan). Hitungan yang cocok persis meninggalkan jejak sejak paket ini (penyesuaian bertanda cocokPersis); yang lebih lama tidak —
 * disebut di kalimatnya, tidak ditebak.
 */
export function shOpname(kini) { const k = shKini(kini); const iso = hariIniIso(k); return ingatPerVersi('shOpname|' + iso, () => shOpnameHitung(k, iso)); }
function shOpnameHitung(kini, iso) {
  const key = iso.slice(0, 7); const awal = key + '-01'; const D = shDihitung(awal, iso); const S = shDihitung('0000-00-00', iso); const daftar = [];
  const hari = (cap) => { if (!cap) return null; const a = Date.UTC(Number(cap.slice(0, 4)), Number(cap.slice(5, 7)) - 1, Number(cap.slice(8, 10))); const b = Date.UTC(Number(iso.slice(0, 4)), Number(iso.slice(5, 7)) - 1, Number(iso.slice(8, 10))); return Math.round((b - a) / 86400000); };
  barangCocok('tumpukan').forEach((b) => { if (!(b.buku > 0.004)) return; const t = S.tump[b.nama] || ''; daftar.push({ nama: b.nama, jenis: 'karung', kg: b.buku, dihitung: !!D.tump[b.nama], terakhir: t.slice(0, 10), hari: hari(t) }); });
  barangCocok('kemasan').forEach((b) => { if (!(b.sistem > 0)) return; const k = String(b.namaProduk) + '|' + Number(b.ukuranKemasan); const t = S.kem[k] || ''; daftar.push({ nama: b.nama, jenis: 'kemasan', unit: b.sistem, dihitung: !!D.kem[k], terakhir: t.slice(0, 10), hari: hari(t) }); });
  const belum = daftar.filter((x) => !x.dihitung).sort((a, b) => (b.hari === null ? 1e9 : b.hari) - (a.hari === null ? 1e9 : a.hari) || a.nama.localeCompare(b.nama)); const sudah = daftar.filter((x) => x.dihitung);
  const n = daftar.length; const persen = n ? sudah.length / n * 100 : null;
  return { key, nama: lpNamaBulan(key), sampai: iso, n, nDihitung: sudah.length, nBelum: belum.length, belum, sudah, persen, lengkap: n > 0 && !belum.length,
    nKarung: daftar.filter((x) => x.jenis === 'karung').length, nKarungDihitung: sudah.filter((x) => x.jenis === 'karung').length,
    kalimat: !n ? 'Tidak ada stok beras maupun kemasan menurut buku — tidak ada yang perlu dihitung.' : !belum.length ? 'Opname ' + lpNamaBulan(key) + ' lengkap: ' + n + ' barang sudah dihitung fisik bulan ini.'
      : sudah.length + ' dari ' + n + ' barang sudah dihitung fisik ' + lpNamaBulan(key) + '; ' + belum.length + ' belum. Hitungan yang cocok persis baru tercatat sejak pembaruan ini — yang lebih lama tidak meninggalkan jejak.' };
}
/**
 * SUSUT PER PEMASOK (A73). Tiap baris susut & selisih stok beras (penyesuaianStok, nilaiRp terkunci, sejak 1 Sep 2026) dibagi ke KEDATANGAN yang masih ada di
 * tumpukan saat dihitung: karung terlama keluar dulu, jadi buku sebelum dihitung (kgSistem) = kedatangan TERBARU buku itu sampai tanggal hitung, mundur sampai
 * kg-nya tertutup; selisihnya dibagi sebanding kg tiap kedatangan → pemasoknya. Buku tanpa kedatangan (stok awal, wadah, pindahan) = kelompok sendiri.
 * PENJAGA: Σ pemasok = Σ baris susut beras rentang itu, persis sampai rupiah. Pembanding: kg yang datang dari pemasok itu di rentang yang sama + kurang timbang
 * saat datang (rekapTimbangMutu, Barang masuk).
 */
export function shSusutPemasok(awal, akhir) { return ingatPerVersi('shSusutPemasok|' + awal + '|' + akhir, () => shSusutPemasokHitung(String(awal), String(akhir))); }
export const SH_TANPA_KEDATANGAN = '(tanpa kedatangan: stok awal · wadah · pindahan)';
function shSusutPemasokHitung(awal, akhir) {
  const lapis = {}; const nmPem = (b) => (b.stokAwal || b.tutupBuku ? '(stok awal / saldo pembuka)' : String(b.pemasok || '').trim() || '(tanpa nama pemasok)');
  ambilSemuaBatch().forEach((b) => { if (!b || b.lahirBuku) return; (b.merkList || []).forEach((m, i) => { if (!m || m.bentuk === 'bal' || !m.merk || !(Number(m.totalKg) > 0)) return;
    (lapis[m.merk] = lapis[m.merk] || []).push({ kg: Number(m.totalKg), tanggal: String(b.tanggal || ''), id: Number(b.id) || 0, i, pemasok: nmPem(b) }); }); });
  Object.keys(lapis).forEach((k) => lapis[k].sort((x, y) => x.tanggal.localeCompare(y.tanggal) || x.id - y.id || x.i - y.i));
  const per = {}; const pem = (n) => (per[n] = per[n] || { pemasok: n, nBaris: 0, susutKg: 0, susutRp: 0, naikKg: 0, naikRp: 0, kgMasuk: 0, kgKurangDatang: 0, nKedatangan: 0 });
  let total = 0, n = 0;
  ambilPenyesuaianStok().forEach((x) => { const rp = x.nilaiRp; if (typeof rp !== 'number' || !isFinite(rp) || rp === 0 || !x.tanggal || x.tanggal < MULAI_SUSUT_LABA || x.tanggal < awal || x.tanggal > akhir) return;
    total += rp; n += 1; const sk = Number(x.selisihKg) || 0;
    const L = (lapis[x.merk] || []).filter((l) => l.tanggal <= x.tanggal); let sisa = Number(x.kgSistem); const ambil = [];
    if (isFinite(sisa) && sisa > 0.004) for (let j = L.length - 1; j >= 0 && sisa > 0.004; j--) { const t = Math.min(L[j].kg, sisa); ambil.push({ pemasok: L[j].pemasok, kg: t }); sisa -= t; }
    const tot = ambil.reduce((a, y) => a + y.kg, 0); const bagi = tot > 0 ? ambil : [{ pemasok: SH_TANPA_KEDATANGAN, kg: 1 }]; const tb = tot > 0 ? tot : 1;
    // pembagian rupiah: bagian terakhir menerima sisa pembulatan — Σ bagian = nilaiRp baris persis
    let rpJalan = 0; bagi.forEach((y, j) => { const g = pem(y.pemasok); const akhirB = j === bagi.length - 1; const r = akhirB ? rp - rpJalan : rp * y.kg / tb; rpJalan += r; const kg = sk * y.kg / tb;
      g.nBaris += 1; if (sk < 0 || (sk === 0 && rp < 0)) { g.susutKg -= kg; g.susutRp += r; } else { g.naikKg += kg; g.naikRp += r; } }); });
  ambilSemuaBatch().forEach((b) => { if (!b || b.lahirBuku || b.stokAwal || b.tutupBuku || !b.tanggal || b.tanggal < awal || b.tanggal > akhir) return; const kg = (b.merkList || []).reduce((a, m) => a + (m && m.bentuk !== 'bal' ? Number(m.totalKg) || 0 : 0), 0);
    if (kg > 0) { const g = pem(nmPem(b)); g.kgMasuk += kg; g.nKedatangan += 1; } });
  let R = null; try { R = rekapTimbangMutu({ dari: awal, sampai: akhir }); } catch (e) { R = null; }
  if (R) R.pemasok.forEach((p) => { if (per[p.pemasok]) per[p.pemasok].kgKurangDatang = p.kgKurang; });
  const daftar = Object.keys(per).map((k) => per[k]).map((g) => Object.assign(g, { susutKg: shBulat(g.susutKg), naikKg: shBulat(g.naikKg), pct: g.kgMasuk > 0 && g.susutKg > 0 ? g.susutKg / g.kgMasuk * 100 : null }))
    .filter((g) => g.nBaris || g.kgMasuk).sort((a, b) => b.susutKg - a.susutKg || b.kgMasuk - a.kgMasuk || a.pemasok.localeCompare(b.pemasok));
  const jumlah = daftar.reduce((a, g) => a + g.susutRp + g.naikRp, 0); const menutup = Math.abs(jumlah - total) < 0.5;
  return { awal, akhir, pemasok: daftar, total, nBaris: n, jumlah, menutup,
    kalimat: menutup ? (n ? 'Σ pemasok = susut & selisih stok beras ' + RP(total) + ' (' + n + ' baris) — menutup persis sampai rupiah.' : 'Belum ada susut beras tercatat di rentang ini.') : 'TIDAK MENUTUP: Σ pemasok ' + RP(jumlah) + ' ≠ baris susut beras ' + RP(total) + ' — laporkan.',
    rumus: 'Susut tiap hitungan dibagi ke kedatangan yang masih di tumpukan saat dihitung (karung terlama sudah keluar dulu). Persen = susut kg ÷ kg yang datang dari pemasok itu di rentang yang sama.' };
}
/** Rentang 3 bulan terakhir (awal bulan ke-3 dari belakang → hari ini) untuk kartu susut per pemasok. */
export function shRentang3(kini) { const iso = hariIniIso(shKini(kini)); const y = Number(iso.slice(0, 4)), m = Number(iso.slice(5, 7)) - 1 - (SH_BULAN - 1); const d = new Date(Date.UTC(y, m, 1)); return { awal: d.toISOString().slice(0, 10), akhir: iso }; }

// ==================== HPP & HARGA MINIMUM ====================
/**
 * BIAYA TOKO PER KG TERJUAL (A97): 3 bulan terakhir yang SELESAI (bukan bulan berjalan) yang punya kg terjual — biaya toko (harian + jatah bulanan, mesin laba)
 * ÷ kg semua nota ber-kg, DIGABUNG (Σ biaya ÷ Σ kg). Angka per bulan = pemicu "Biaya toko per kg terjual" Laporan › Biaya. Tanpa bulan selesai = null.
 */
export function shBiayaKg(kini) { const k = shKini(kini); return ingatPerVersi('shBiayaKg|' + hariIniIso(k), () => {
  const kunci = hariIniIso(k).slice(0, 7); const bulan = [];
  daftarBulan(k, 15).forEach((b) => { if (bulan.length >= SH_BULAN || b.key >= kunci) return; const X = kbBiayaKgBulan(b.key, k); if (X.kgTerjual > 0) bulan.push({ key: b.key, nama: b.nama, biayaToko: X.biayaToko, kg: X.kgTerjual, perKg: X.biayaToko / X.kgTerjual }); });
  const biaya = bulan.reduce((a, x) => a + x.biayaToko, 0); const kg = bulan.reduce((a, x) => a + x.kg, 0); const perKg = kg > 0 ? biaya / kg : null;
  return { perKg, bulan, n: bulan.length, biaya, kg, teks: perKg === null ? 'Biaya toko per kg belum bisa dihitung — belum ada bulan selesai yang punya penjualan.' : 'Biaya toko ' + RP(Math.round(perKg)) + '/kg terjual = ' + RP(biaya) + ' ÷ ' + KG(kg) + ' (' + bulan.map((x) => x.nama).join(', ') + ').' };
}); }
/** Rincian per kg dari modal per kg → { modal, biaya, laba, minimum = modal + biaya + laba (null bila biaya belum bisa dihitung), layak = modal ÷ (1 − susut)
 *  (beras saja; kemasan adukan tidak), susut = layak − modal, minimumSusut = layak + biaya + laba (angka bantu, bukan dasar tanda) }. */
export function shMinimumKg(modalKg, beras, susutPct, biayaKg, labaKg) {
  const s = beras && susutPct !== null && susutPct !== undefined && susutPct > 0 && susutPct < 100 ? susutPct : 0; const layak = modalKg / (1 - s / 100); const ada = !(biayaKg === null || biayaKg === undefined);
  return { modal: modalKg, susut: layak - modalKg, layak, biaya: biayaKg, laba: labaKg, susutPct: s, minimum: ada ? modalKg + biayaKg + labaKg : null, minimumSusut: ada ? layak + biayaKg + labaKg : null };
}
/**
 * HARGA MINIMUM tiap baris katalog (A64 · A97). S = hgSemua(kini) (dibawa dari layar; satu hitungan). pakai: 'tampil' (harga di papan owner, draf ikut) ·
 * 'terbit' (harga yang dipakai kasir — Dasbor). Status: bawah (harga < minimum, tegas) · aman · lubang (belum ada harga) · tanpaModal · tanpaBiaya.
 * Peringatan saja — terbit tidak pernah ditahan (keputusan owner 26 Nov 2026).
 */
export function shMinimumKatalog(S, kini, pakai) {
  const T = shTarget(kini); const B = shBiayaKg(kini); const A = shAtur(); const terbit = pakai === 'terbit'; const per = {};
  const baris = S.baris.map((b) => { const n = terbit ? b.lamaN : b.n; const kg = b.st.kg; const beras = b.modalDari === 'beras';
    if (!(b.modalUnit > 0)) return (per[b.k] = { k: b.k, merk: b.merk, judul: b.judul, n, status: 'tanpaModal' });
    const R = shMinimumKg(b.modalUnit / kg, beras, T.pct, B.perKg, A.targetLabaPerKg); const minimum = R.minimum === null ? null : R.minimum * kg;
    const status = minimum === null ? 'tanpaBiaya' : !(n > 0) ? 'lubang' : n + 0.5 < minimum ? 'bawah' : 'aman';
    return (per[b.k] = { k: b.k, merk: b.merk, judul: b.judul, satuan: b.st.id, per: b.st.per, kg, n, beras, rinci: R, minimum, minimumBulat: minimum === null ? null : Math.ceil(minimum - 1e-9), kurang: status === 'bawah' ? minimum - n : 0, status, adaDraf: b.adaDraf }); });
  const bawah = baris.filter((x) => x.status === 'bawah').sort((a, b) => b.kurang / b.kg - a.kurang / a.kg || a.judul.localeCompare(b.judul));
  return { pakai: terbit ? 'terbit' : 'tampil', baris, per, bawah, nBawah: bawah.length, target: T, biaya: B, atur: A, rumus: SH_RUMUS_MINIMUM,
    keadaan: B.perKg === null ? 'tanpaBiaya' : 'ada', kalimat: B.perKg === null ? B.teks : bawah.length ? bawah.length + ' harga ' + (terbit ? 'yang dipakai kasir ' : '') + 'di bawah harga minimum — boleh; owner yang memutuskan.' : 'Tidak ada harga di bawah harga minimum.' };
}
/**
 * ALARM MODAL + BIAYA PER KG MENDEKATI HET (A98): tiap merek beras (baris per kg katalog) yang kelas/mereknya sudah dipetakan ke HET medium / premium.
 * Biaya per kg = modal per kg + biaya toko per kg (susut disebut di rinciannya). ≥ HET = 'lewat' (dijual tepat HET pun rugi) · ≥ HET − jarak = 'dekat' · selain itu aman.
 * Belum dipetakan / bukan beras HET / biaya belum bisa dihitung = disebut, tidak dinilai.
 */
export function shDekatHet(S, kini) {
  const T = shTarget(kini); const B = shBiayaKg(kini); const A = shAtur(); const H = hetKatalog(S, 'tampil'); const daftar = []; let nBelum = 0, nNilai = 0;
  S.baris.forEach((b) => { if (b.st.id !== 'S' || b.modalDari !== 'beras' || !(b.modalUnit > 0)) return; const x = H.per[b.k]; if (!x) return;
    if (x.kategori !== 'medium' && x.kategori !== 'premium') { if (!x.kategori) nBelum += 1; return; }
    if (B.perKg === null) return; nNilai += 1;
    const R = shMinimumKg(b.modalUnit, true, T.pct, B.perKg, 0); const biayaKg = R.minimum; const het = x.het; const jarak = het - biayaKg;   // modal + biaya toko (A98); susut di rinci.layak
    const status = biayaKg >= het - 1e-6 ? 'lewat' : jarak <= A.jarakHet + 1e-6 ? 'dekat' : 'aman';
    daftar.push({ k: b.k, merk: b.merk, kategori: x.kategori, unit: x.unit, het, rinci: R, biayaKg, jarak, status }); });
  const alarm = daftar.filter((x) => x.status !== 'aman').sort((a, b) => a.jarak - b.jarak || a.merk.localeCompare(b.merk));
  return { daftar, alarm, nLewat: alarm.filter((x) => x.status === 'lewat').length, nDekat: alarm.filter((x) => x.status === 'dekat').length, nNilai, nBelum, atur: A, het: hetAtur(), saran: SH_SARAN_HET,
    keadaan: B.perKg === null ? 'tanpaBiaya' : !nNilai ? 'belumDipetakan' : 'ada',
    kalimat: B.perKg === null ? B.teks : !nNilai ? 'Belum ada merek beras per kg yang kelasnya dipetakan ke HET — petakan di kartu HET.' : alarm.length ? alarm.length + ' merek modal + biayanya ≤ ' + RP(A.jarakHet) + '/kg dari HET (' + alarm.filter((x) => x.status === 'lewat').length + ' sudah lewat HET).' : 'Semua ' + nNilai + ' merek yang dinilai masih lebih dari ' + RP(A.jarakHet) + '/kg di bawah HET.' };
}
/** Ringkasan untuk Dasbor: harga yang DIPAKAI KASIR di bawah minimum + alarm HET. Satu hitungan katalog per hari & versi data. */
export function shRingkasHarga(kini) { const k = shKini(kini); return ingatPerVersi('shRingkasHarga|' + hariIniIso(k), () => { const S = hgSemua(k); const M = shMinimumKatalog(S, k, 'terbit'); const H = shDekatHet(S, k);
  return { nBawah: M.nBawah, bawah: M.bawah.slice(0, 5).map((x) => ({ judul: x.judul, n: x.n, minimum: x.minimumBulat })), keadaanMin: M.keadaan, kalimatMin: M.kalimat, nDekat: H.nDekat, nLewat: H.nLewat, keadaanHet: H.keadaan, kalimatHet: H.kalimat,
    alarm: H.alarm.slice(0, 5).map((x) => ({ merk: x.merk, kategori: x.kategori, het: x.het, biayaKg: x.biayaKg, status: x.status })), biayaKg: M.biaya.perKg, target: M.target.pct }; }); }
/**
 * KALKULATOR SEBELUM BELI (A65 · A66) — TIDAK menulis dokumen. isi (ketikan): hargaKg, jumlahKarung, isiKarung (bawaan 50), timbangKarung (rata-rata kg per karung
 * hasil timbang, boleh kosong), bongkarKg (kosong = bongkar terukur Harga › Atur), ongkir (Rp seluruh muatan), susut (% — kosong = target), kelas ('medium' |
 * 'premium' | ''), hargaJual (Rp/kg, boleh kosong). Modal per kg = (nilai nota + bongkar + ongkir) ÷ kg BUKU — kg timbang bila diisi (stok ikut timbang, #211),
 * jadi kurang timbang menaikkan modal per kg. Modal per karung = modal per kg × kg satu karung (timbang).
 */
export function shHitungBeli(isi, kini, bongkarBawaan) {
  const I = isi || {}; const ang = (v) => (ugKosong(v) ? null : ugAngka(v)); const T = shTarget(kini); const B = shBiayaKg(kini); const A = shAtur(); const H = hetAtur();
  const harga = ang(I.hargaKg), j = ang(I.jumlahKarung), isiK = ang(I.isiKarung) === null ? 50 : ang(I.isiKarung), tb = ang(I.timbangKarung);
  const bk = ang(I.bongkarKg) === null ? (Number(bongkarBawaan) || 0) : ang(I.bongkarKg), ong = ang(I.ongkir) === null ? 0 : ang(I.ongkir), sus = ang(I.susut) === null ? T.pct : ang(I.susut);
  const jual = ang(I.hargaJual); const kelas = I.kelas === 'medium' || I.kelas === 'premium' ? I.kelas : '';
  if (harga === null || j === null) return { siap: false, kalimat: 'Isi harga beli per kg dan jumlah karung dulu.' };
  if (!(harga > 0) || !(j > 0) || !(isiK > 0) || (tb !== null && !(tb > 0)) || !(bk >= 0) || !(ong >= 0) || (sus !== null && !(sus >= 0 && sus < 100)) || (jual !== null && !(jual > 0))) return { siap: false, kalimat: 'Ada angka yang tidak masuk akal — harga, jumlah, isi & timbang lebih dari 0; bongkar & ongkir 0 atau lebih; susut 0 sampai di bawah 100 %.' };
  const kgNota = j * isiK; const kgBuku = tb !== null ? j * tb : kgNota; const nilaiNota = harga * kgNota; const bongkar = bk * kgNota; const modal = nilaiNota + bongkar + ong;
  const modalKg = modal / kgBuku; const perKarung = modalKg * (tb !== null ? tb : isiK); const R = shMinimumKg(modalKg, true, sus, B.perKg, A.targetLabaPerKg);
  // impas = modal + biaya toko (rumus harga minimum owner); impasSusut = HPP layak jual + biaya toko — kalau susut gudang ikut ditanggung
  const impas = B.perKg === null ? null : modalKg + B.perKg; const impasSusut = B.perKg === null ? null : R.layak + B.perKg;
  const het = kelas ? H[kelas] : null; const sel = (x, y) => (x === null || y === null ? null : x - y);
  return { siap: true, kgNota, kgBuku, kurangKg: kgNota - kgBuku, nilaiNota, bongkar, bongkarKg: bk, ongkir: ong, modal, modalKg, perKarung, isiKarung: tb !== null ? tb : isiK, ditimbang: tb !== null, susutPct: R.susutPct, layak: R.layak, biayaKg: B.perKg, impas, impasSusut,
    minimum: R.minimum, minimumSusut: R.minimumSusut, labaKg: A.targetLabaPerKg, kelas, het, untungHet: sel(het, impas), untungHetSusut: sel(het, impasSusut), hargaJual: jual, untungJual: sel(jual, impas), untungJualSusut: sel(jual, impasSusut),
    untungHetTotal: het === null || impas === null ? null : (het - impas) * kgBuku, untungJualTotal: jual === null || impas === null ? null : (jual - impas) * kgBuku,
    target: T, biaya: B, kalimat: impas === null ? B.teks : 'Modal sampai toko ' + RP(Math.round(modalKg)) + '/kg' + (tb !== null && Math.abs(kgNota - kgBuku) > 0.004 ? ' (kg timbang ' + KG(kgBuku) + ', nota ' + KG(kgNota) + ')' : '') + ' → impas ' + RP(Math.round(impas)) + '/kg dengan biaya toko; ' + RP(Math.round(impasSusut)) + '/kg kalau susut ' + lpPersenTeks(R.susutPct) + ' ikut ditanggung.' };
}
/**
 * HPP PERIODE (A11) — pembanding, bukan angka laba: nilai stok awal + pembelian − nilai stok akhir (neraca per tanggal: beras × modal rata-rata buku, kemasan,
 * kantong & bahan) dibanding HPP nota (modal tersimpan di nota, sesudah retur utuh) + susut & selisih stok. Bedanya BUKAN kebocoran otomatis: nilai stok neraca
 * memakai modal rata-rata terbaru (harga beli berubah = stok dinilai ulang), nota tanpa modal mengeluarkan barang tanpa HPP, koreksi modal & upah adukan
 * menggeser nilai stok. Disebut semua, tidak disembunyikan. Bulan berjalan = sampai hari ini. Tahun yang sudah ditutup buku = diarsip.
 */
export function shHppPeriode(key, kini) { const k = shKini(kini); return ingatPerVersi('shHppPeriode|' + key + '|' + hariIniIso(k), () => shHppPeriodeHitung(String(key), k)); }
function shHppPeriodeHitung(key, kini) {
  const iso = hariIniIso(kini); const awal = key + '-01'; const akhirB = akhirBulanIso(key); const sampai = akhirB < iso ? akhirB : iso; const nama = lpNamaBulan(key);
  if (tahunDiarsip(key)) return { key, nama, diarsip: true, kalimat: 'Catatan ' + nama + ' ikut arsip tutup buku — HPP periode tidak bisa disusun.' };
  if (awal > iso) return { key, nama, depan: true, kalimat: nama + ' belum datang.' };
  const d = new Date(Date.UTC(Number(awal.slice(0, 4)), Number(awal.slice(5, 7)) - 1, 1) - 86400000).toISOString().slice(0, 10); const pertama = catatanPertama() || '';
  const N0 = pertama && d >= pertama ? ingatNeraca(d) : null; const N1 = ingatNeraca(sampai); const dalam = (t) => !!t && t >= awal && t <= sampai;
  let beli = 0, dicatat = 0, nBeli = 0;
  // paket sisa sensus (owner 27 Nov 2026, B68): satu aturan nilai kedatangan dengan grafik pembelian (shNilaiKedatangan) — "+ Pembelian" = batang bulannya
  ambilSemuaBatch().forEach((b) => { if (!dalam(b && b.tanggal)) return; const V = shNilaiKedatangan(b); if (V.jenis === 'lewat') return;
    if (V.jenis === 'dicatat') dicatat += V.rp; else { beli += V.rp; nBeli += 1; } });
  const bahan = ambilBahanKemasan().concat(ambilBahanLiteran()).reduce((a, x) => a + (x.tipe === 'beli' && dalam(x.tanggal) && Number(x.jumlah) > 0 ? Number(x.hargaTotal) || 0 : 0), 0);
  const upah = ambilProduksiBerlaku().reduce((a, p) => a + (dalam(p.tanggal) ? Number(p.upahRepacking) || 0 : 0), 0);
  const stokAwal = N0 ? N0.stok : 0; const stokAkhir = N1.stok; const hppPeriode = stokAwal + beli + dicatat + bahan + upah - stokAkhir;
  const L = ugLabaBersih(awal, sampai); const susut = -(L.susutStok || 0); const pembanding = L.hpp + susut; const beda = hppPeriode - pembanding;
  const minus = !!((N0 && N0.adaStokMinus) || N1.adaStokMinus); const nmMinus = [];
  [N0, N1].forEach((N) => { if (N) (N.sackMinus || []).concat(N.bagsMinus || []).forEach((n) => { if (nmMinus.indexOf(n) < 0) nmMinus.push(n); }); });
  return { key, nama, berjalan: sampai < akhirB, awal, sampai, sebelum: d, sebelumBuku: !N0, stokAwal, beli, nBeli, dicatat, bahan, upah, stokAkhir, hppPeriode, hppNota: L.hpp, returHpp: L.returHpp || 0, susut, pembanding, beda,
    bedaPct: Math.abs(pembanding) > 0.5 ? beda / pembanding * 100 : null, nTanpaHpp: L.jumlahTanpaHpp || 0, omzetTanpaHpp: L.omzetTanpaHpp || 0, minus,
    rumus: 'HPP periode = nilai stok ' + tanggalPendek(d) + ' + pembelian + stok yang dicatat (stok awal / saldo pembuka) + beli kantong & bahan + upah adukan − nilai stok ' + tanggalPendek(sampai),
    minusNama: nmMinus.slice(0, 4),
    kalimat: (minus ? 'Ada buku stok MINUS' + (nmMinus.length ? ' (' + nmMinus.slice(0, 3).join(', ') + (nmMinus.length > 3 ? ', …' : '') + ')' : '') + ' di awal atau akhir periode — nilainya ikut minus seperti di neraca; cocokkan di Stok supaya angka ini makin tepat. ' : '')
      + 'Beda ' + RP(Math.round(beda)) + ' antara HPP periode (dari nilai stok) dan HPP nota + susut. Asalnya: harga beli berubah (stok dinilai ulang dengan modal rata-rata terbaru)' + (L.jumlahTanpaHpp ? ', ' + L.jumlahTanpaHpp + ' baris nota tanpa modal (' + RP(L.omzetTanpaHpp) + ' omzet) mengeluarkan barang tanpa HPP' : '') + ', koreksi modal, dan catatan yang belum lengkap.' };
}

// ==================== DASBOR ====================
/** Susut untuk Dasbor (Mutu usaha): target, merek kuning / merah bulan ini, opname bulan ini — apa adanya dari fungsi di atas. M = merekBulan bulan ini (dbMutu). */
export function shDasborSusut(M, kini) {
  const T = shTarget(kini); const S = M && M.susut ? M.susut : null; const O = shOpname(kini);
  return { pct: S ? S.pct : null, target: T.pct, targetDariOwner: T.dariOwner, targetAsal: T.asal, status: shBandingTarget(S ? S.pct : null, T.pct), kuning: S ? (S.selidik || []).map((g) => g.merek) : [], merah: S ? (S.tinggi || []).map((g) => g.merek) : [],
    ambangKuning: T.kuning, ambangMerah: T.merah, opname: { n: O.n, nDihitung: O.nDihitung, nBelum: O.nBelum, belum: O.belum.slice(0, 5).map((x) => x.nama), kalimat: O.kalimat } };
}
/** Laporan › Mingguan: susut per merek minggu itu (susutRentang apa adanya) + target untuk pembanding. */
export function shMinggu(awal, akhir, kini) { const R = susutRentang(awal, akhir); const T = shTarget(kini); return Object.assign({}, R, { target: T, status: R.susut ? shBandingTarget(R.susut.pct, T.pct) : null }); }

// ==================== PAKET SISA SENSUS (owner 27 Nov 2026) · B68 PEMBELIAN & A74 SUSUT PER PENJAGA ====================
/**
 * B68 — SATU KEDATANGAN SEBAGAI PEMBELIAN: rupiah = Σ harga beras di nota pemasok (merkList.subtotalHarga) + bongkar — aturan yang SAMA dengan baris "+ Pembelian"
 * HPP periode (shHppPeriode memanggil fungsi ini). Kedatangan "lahir buku" (bukan barang datang) = 'lewat'; stok awal / saldo pembuka tutup buku = 'dicatat'
 * (bukan belanja). bon = kedatangan yang dibayar nanti (caraBayar utang, pembantu batchDiutang — sama dengan Bon pemasok); selain itu dibayar langsung.
 */
export function shNilaiKedatangan(b) {
  if (!b || b.lahirBuku) return { jenis: 'lewat', rp: 0, kg: 0, bon: false };
  const rp = (b.merkList || []).reduce((a, m) => a + (Number(m && m.subtotalHarga) || 0), 0) + (Number(b.biayaBongkar) || 0);
  const kg = (b.merkList || []).reduce((a, m) => a + (m && m.bentuk !== 'bal' ? Number(m.totalKg) || 0 : 0), 0);
  return { jenis: b.stokAwal || b.tutupBuku ? 'dicatat' : 'beli', rp, kg, bon: batchDiutang(b) };
}
const shNamaPemasok = (b) => String(b.pemasok || '').trim() || '(tanpa nama pemasok)';
/** Pembelian rentang [dari, sampai]: rupiah, kg, jumlah kedatangan, BON vs dibayar langsung, pemasok terbesar. Menyentuh tahun yang diarsip tutup buku = disebut. */
export function shPembelian(dari, sampai) { return ingatPerVersi('shPembelian|' + dari + '|' + sampai, () => shPembelianHitung(String(dari), String(sampai))); }
function shPembelianHitung(dari, sampai) {
  const dalam = (t) => !!t && t >= dari && t <= sampai; const out = { dari, sampai, rp: 0, kg: 0, n: 0, bon: { rp: 0, n: 0 }, langsung: { rp: 0, n: 0 }, dicatat: 0, nDicatat: 0, pemasok: [] }; const per = {};
  ambilSemuaBatch().forEach((b) => { if (!dalam(b && b.tanggal)) return; const V = shNilaiKedatangan(b); if (V.jenis === 'lewat') return;
    if (V.jenis === 'dicatat') { out.dicatat += V.rp; out.nDicatat += 1; return; }
    out.rp += V.rp; out.kg += V.kg; out.n += 1; const c = V.bon ? out.bon : out.langsung; c.rp += V.rp; c.n += 1;
    const nm = shNamaPemasok(b); const g = per[nm] || (per[nm] = { pemasok: nm, rp: 0, kg: 0, n: 0 }); g.rp += V.rp; g.kg += V.kg; g.n += 1; });
  out.kg = shBulat(out.kg); out.pemasok = Object.keys(per).map((k) => per[k]).sort((a, b) => b.rp - a.rp || a.pemasok.localeCompare(b.pemasok));
  out.diarsip = tahunDiarsip(dari) || tahunDiarsip(sampai);
  return out;
}
export const SH_RENTANG_BELI = [['hari', 'Hari'], ['minggu', 'Minggu'], ['bulan', 'Bulan']];
/** Grafik pembelian per hari (14) · minggu (8, Senin–Minggu) · bulan (6) — rentang sama dengan tren omzet Dasbor (Laporan › Harian/Mingguan/Bulanan). Batang bulan
 *  menutup ke "+ Pembelian" HPP periode bulan itu. Sebelum toko mencatat / tahun yang diarsip = absen (disebut), bukan Rp0. */
export function shTrenBeli(rentang, kini) {
  const k = shKini(kini); const iso = hariIniIso(k); const pertama = catatanPertama() || '';
  const satu = (dari, sampai, x) => { const absen = !pertama || sampai < pertama || tahunDiarsip(sampai); const P = absen ? null : shPembelian(dari, sampai);
    return Object.assign({ dari, sampai, absen, rp: P ? P.rp : 0, bon: P ? P.bon.rp : 0, langsung: P ? P.langsung.rp : 0, kg: P ? P.kg : 0, n: P ? P.n : 0, nBon: P ? P.bon.n : 0 }, x); };
  let batang; const r = SH_RENTANG_BELI.some((x) => x[0] === rentang) ? rentang : 'bulan';
  if (r === 'minggu') batang = daftarMinggu(k, 8).reverse().map((m) => satu(m.awal, m.akhir, { id: m.awal, label: m.pendek, panjang: 'Minggu ' + m.label, berjalan: m.berjalan, tujuan: { ke: 'stok', lembar: 'masuk' } }));
  else if (r === 'hari') { batang = []; for (let i = 13; i >= 0; i--) { const t = ugTambahHari(iso, -i); batang.push(satu(t, t, { id: t, label: String(Number(t.slice(8, 10))), panjang: tanggalPendek(t) + (i === 0 ? ' · hari ini' : ''), berjalan: i === 0, tujuan: { ke: 'stok', lembar: 'masuk' } })); } }
  else batang = daftarBulan(k, 6).reverse().map((b) => satu(b.key + '-01', akhirBulanIso(b.key), { id: b.key, label: b.pendek, panjang: b.nama, berjalan: b.berjalan, tujuan: { ke: 'laporan', keluarga: 'bulanan', bulan: b.key } }));
  const ada = batang.filter((b) => !b.absen);
  return { rentang: r, batang, maks: Math.max(1, ...ada.map((b) => b.rp)), rp: ada.reduce((a, b) => a + b.rp, 0), bon: ada.reduce((a, b) => a + b.bon, 0), n: ada.reduce((a, b) => a + b.n, 0),
    periode: r === 'hari' ? '14 hari terakhir' : r === 'minggu' ? batang.length + ' minggu terakhir (Senin–Minggu)' : batang.length + ' bulan terakhir', sumber: 'Stok › Barang masuk', tujuan: { ke: 'stok', lembar: 'masuk' },
    rumus: 'Pembelian = Σ harga beras di nota pemasok + bongkar per kedatangan (stok awal & saldo pembuka bukan belanja) — sama dengan "+ Pembelian" HPP periode Laporan › Bulanan' };
}

/**
 * A74 — SUSUT PER PENJAGA (keputusan owner 27 Nov 2026: "yang jaga di rentang itu"; cuma laporan, TIDAK memotong upah). Tiap baris susut & selisih stok
 * (baris yang sama dengan Laporan: hitungan beras karung, kemasan, kantong & bahan bernilai Rp ≠ 0 sejak MULAI_SUSUT_LABA) dibagi ke orang yang MASUK KERJA
 * menurut hari kerja (absenKaryawan: 1 = sehari, ½ = setengah) SESUDAH hitungan sebelumnya barang yang sama sampai hari hitungan ini — hitungan cocok persis
 * (Rp0) ikut jadi batas. Belum pernah dihitung sebelumnya = sejak catatan pertama toko. Owner tidak tercatat di hari kerja → tidak kebagian. Rentang tanpa satu
 * pun hari kerja tercatat = "tanpa catatan hari kerja". Bagian terakhir menerima sisa pembulatan: Σ orang + tanpa catatan = Σ baris susut, persis.
 */
export const SH_TANPA_JAGA = '(tanpa catatan hari kerja)';
export const SH_RUMUS_PENJAGA = 'Susut tiap hitungan dibagi ke yang masuk kerja (Uang › Upah › hari kerja) sejak hitungan sebelumnya barang itu sampai hari hitungan ini, sebanding hari kerjanya. Owner tidak tercatat di hari kerja, jadi tidak kebagian. Laporan saja — upah tidak dipotong.';
const shKunciHitung = (jenis, x) => (jenis === 'stok' ? 'k|' + String(x.merk || '') : jenis === 'kemasan' ? 'm|' + String(x.namaProduk || '') + '|' + String(x.ukuranKemasan || '') : 'b|' + jenis + '|' + String(x.jenis || ''));
/** Hari kerja per tanggal: { iso: { nama: bobot } } dari absenKaryawan (1 · 0,5; 0 / kosong = tidak masuk). */
function shPetaJaga() {
  const peta = {}; ambilAbsenKaryawan().forEach((d) => { const nm = String((d && d.nama) || '').trim(); if (!nm || !d.hari || typeof d.hari !== 'object') return;
    Object.keys(d.hari).forEach((t) => { const v = Number(d.hari[t]); if (!/^\d{4}-\d\d-\d\d$/.test(t) || !(v === 1 || v === 0.5)) return; const h = peta[t] || (peta[t] = {}); h[nm] = (h[nm] || 0) + v; }); });
  return peta;
}
export function shSusutPenjaga(awal, akhir) { return ingatPerVersi('shSusutPenjaga|' + awal + '|' + akhir, () => shSusutPenjagaHitung(String(awal), String(akhir))); }
function shSusutPenjagaHitung(awal, akhir) {
  // semua hitungan (juga yang cocok persis / sebelum MULAI_SUSUT_LABA / di luar rentang) = batas rentang jaga; rework karantina (kgFisik null) bukan hitungan
  const hitung = []; const tambah = (jenis, x, kg, nama, batas) => { if (!x || !x.tanggal) return; hitung.push({ jenis, x, kunci: shKunciHitung(jenis, x), tanggal: String(x.tanggal), jam: String(x.jam || ''), id: Number(x.id) || 0, kg, nama, batas: batas !== false }); };
  // rework karantina (kgFisik null) tetap baris susut Laporan, tapi bukan hitungan gudang → tidak menjadi batas rentang jaga
  ambilPenyesuaianStok().forEach((x) => tambah('stok', x, Number(x && x.selisihKg) || 0, String((x && x.merk) || '(karung)'), !(x && (x.dariRework || x.kgFisik === null))));
  ambilPenyesuaianKemasan().forEach((x) => tambah('kemasan', x, 0, String((x && x.namaProduk) || '') + ' ' + (x && x.ukuranKemasan) + ' kg'));
  ambilBahanKemasan().forEach((x) => { if (x && x.tipe === 'opname') tambah('bahanKemasan', x, 0, 'kantong & bahan'); });
  ambilBahanLiteran().forEach((x) => { if (x && x.tipe === 'opname') tambah('bahanLiteran', x, 0, 'kantong literan'); });
  hitung.sort((a, b) => a.tanggal.localeCompare(b.tanggal) || a.jam.localeCompare(b.jam) || a.id - b.id);
  const sebelum = {}; const pertama = catatanPertama() || ''; const J = shPetaJaga(); const per = {}; let total = 0, n = 0;
  const orang = (nm) => (per[nm] = per[nm] || { nama: nm, nBaris: 0, susutKg: 0, susutRp: 0, naikKg: 0, naikRp: 0, hariJaga: 0 });
  hitung.forEach((h) => {
    const lalu = sebelum[h.kunci]; if (h.batas) sebelum[h.kunci] = h.tanggal; const rp = h.x.nilaiRp;
    if (typeof rp !== 'number' || !isFinite(rp) || rp === 0 || h.tanggal < MULAI_SUSUT_LABA || h.tanggal < awal || h.tanggal > akhir) return;
    total += rp; n += 1;
    // rentang jaga: sesudah hari hitungan sebelumnya sampai hari ini (hitungan sebelumnya di hari yang sama → hari itu saja); belum pernah → sejak catatan pertama
    const mulai = lalu ? (lalu < h.tanggal ? ugTambahHari(lalu, 1) : h.tanggal) : (pertama && pertama <= h.tanggal ? pertama : h.tanggal);
    const bobot = {}; for (let t = mulai, i = 0; t <= h.tanggal && i < 400; t = ugTambahHari(t, 1), i++) { const d = J[t]; if (d) Object.keys(d).forEach((nm) => { bobot[nm] = (bobot[nm] || 0) + d[nm]; }); }
    const nama = Object.keys(bobot).sort(); const tot = nama.reduce((a, k) => a + bobot[k], 0); const bagi = tot > 0 ? nama.map((k) => ({ nama: k, w: bobot[k] })) : [{ nama: SH_TANPA_JAGA, w: 1 }]; const tb = tot > 0 ? tot : 1;
    let jalan = 0; bagi.forEach((y, j) => { const g = orang(y.nama); const r = j === bagi.length - 1 ? rp - jalan : rp * y.w / tb; jalan += r; const kg = h.kg * y.w / tb; g.nBaris += 1;
      if (h.kg < 0 || (h.kg === 0 && rp < 0)) { g.susutKg -= kg; g.susutRp += r; } else { g.naikKg += kg; g.naikRp += r; } });
  });
  // hari kerja tiap orang DI rentang laporan (bukan rentang jaga yang bertumpuk antar barang)
  Object.keys(J).forEach((t) => { if (t < awal || t > akhir) return; Object.keys(J[t]).forEach((nm) => { if (per[nm]) per[nm].hariJaga += J[t][nm]; }); });
  const daftar = Object.keys(per).map((k) => per[k]).map((g) => Object.assign(g, { susutKg: shBulat(g.susutKg), naikKg: shBulat(g.naikKg), bersih: g.susutRp + g.naikRp, tanpa: g.nama === SH_TANPA_JAGA }))
    .sort((a, b) => (a.tanpa ? 1 : 0) - (b.tanpa ? 1 : 0) || a.bersih - b.bersih || a.nama.localeCompare(b.nama));
  const jumlah = daftar.reduce((a, g) => a + g.bersih, 0); const menutup = Math.abs(jumlah - total) < 0.5;
  return { awal, akhir, orang: daftar, total, nBaris: n, jumlah, menutup, rumus: SH_RUMUS_PENJAGA, adaJaga: Object.keys(J).length > 0,
    kalimat: !n ? 'Belum ada susut & selisih stok tercatat di rentang ini.' : menutup ? 'Σ per penjaga = susut & selisih stok ' + RP(total) + ' (' + n + ' baris) — menutup persis sampai rupiah.' : 'TIDAK MENUTUP: Σ per penjaga ' + RP(jumlah) + ' ≠ baris susut ' + RP(total) + ' — laporkan.' };
}
