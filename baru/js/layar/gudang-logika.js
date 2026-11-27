// GUDANG — STOK MINUS · BARANG HILANG & RUSAK PER JENIS · TUGAS GUDANG YANG TERBUKA (owner 26 Nov 2026, sensus ulang 1c: B49 B50 B53 B54). Tanpa DOM, BACA SAJA,
// awalan gd. TIDAK ADA RUMUS UANG / STOK BARU: tiap angka diambil apa adanya dari sumber yang sudah dipakai layar lain (satu sumber), dan uji_gudang_label_patuh
// memeriksa tiap kelompok MENUTUP ke sumbernya.
//   · stok minus  → buku yang sama dengan gerbang tutup buku (minusBuku, tutup-buku-logika): ingatStokKarung (merek + buku wadah), ingatStokKemasan, kantong
//                   kemasan & literan (mesin beku). Rupiah = sisa × nilai per satuan yang dipakai neraca (barisBuku): karung hppTerakhirPerKg, kemasan
//                   hppRataRataPerUnit, kantong hppPerPcs / hargaPerPcs. Urut dari rupiah paling dalam; tanpa nilai (belum ada harga beli) di belakang, menurut jumlah.
//   · hilang & rusak per JENIS beras → Laporan › Laba › Per merek (merekBulan: susut & selisih stok kurang/lebih, menutup ke "Susut & selisih stok" Laporan) +
//                   retur yang tidak layak jual (kg & taksiran modal hppTaksiranRetur — modalnya TIDAK dibatalkan mesin, kerugiannya sudah di nota aslinya) + nasibnya
//                   di karantina (dibuang · balik ke pemasok · rework · ternyata layak · menunggu). Jenis = setelan Jenis beras (jenisUntukMerk, sama dengan Harga/Stok/Jual).
//   · tugas gudang → hitungan per jenis dari layarnya masing-masing: kabar barang masuk dari tablet yang menunggu, pesanan ke pemasok yang belum datang,
//                   pesanan pelanggan yang belum dikirim, antar yang masih di jalan / gagal, karantina, opname rutin & cek mingguan yang jatuh, wadah perlu diisi,
//                   buku minus, kemasan yang lewat / dekat "baik dipakai sebelum". Pindah stok antar lokasi: toko satu lokasi → tidak berlaku (disebut, bukan 0).
import { hitungStokBahanKemasan, hitungStokBahanLiteran } from '../mesin/beku.js';
import { labelBahan, jenisUntukMerk, hppTaksiranRetur } from '../mesin/pembantu.js';
import { ingatStokKarung, ingatStokKemasan, ambilRetur, ambilKarantina, cacheMentah, petaBukuWadah, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilBahanKemasan, ambilBahanLiteran } from '../data/toko.js';
import { RP, ANGKA, KG, hariIniIso, tanggalPendek } from '../inti/format.js';
import { merekBulan } from './laporan-logika.js';
import { JB_BELUM } from './jenis-beras-logika.js';
import { pesananSemua } from './belanja-logika.js';
import { ajDaftar } from './antar-logika.js';
import { poDaftarAktif, poHariKe } from './pesanan-logika.js';
// paket tanggal janji (owner 27 Nov 2026, sensus B55): kedatangan & antaran yang LEWAT JANJI — satu sumber dengan Laporan › Pondasi › Tepat janji
import { jnLewat, jnKataJanji } from './janji-logika.js';
import { daftarKarantina } from './stok-karantina-logika.js';
import { susunWadah } from './stok-logika.js';
import { lbRingkasKemasan } from './label-logika.js';
// paket P3 (owner 27 Nov 2026, sensus B129): nota "jual dulu, tandai untuk dicocokkan" yang belum tuntas — satu sumber dengan pita Jual & kartu Gudang (jual-logika)
import { notaTembusBelumCocok } from './jual-logika.js';

export const GD_TOP = 10;
export const GD_JENIS_STOK = { beras: 'Beras (karung & wadah)', kemasan: 'Kemasan jadi', kantong: 'Kantong & paper bag' };
const gdTambahHari = (iso, n) => { const d = new Date(String(iso) + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const gdJenis = (nama) => String(jenisUntukMerk(nama) || '').trim() || JB_BELUM;
// Setelan pengingat & lokasi dibaca LANGSUNG dari aturanToko (bentuk ssAtur sistem-logika: nilai dokumen bila ada, selain itu bawaan) — gudang-logika dipakai Dasbor,
// yang bundel & impornya tidak memuat sistem-logika (sistem-logika memakai modul ini lewat lokal.gudang). uji_gudang_label_patuh membandingkan keduanya.
export const GD_PENGINGAT_BAWAAN = { opnameTiap: 14, gudangTiap: 7 };   // = SS_ATUR_BAWAAN.pengingat sistem-logika
const gdDokAtur = (id) => cacheMentah('aturan').find((x) => String(x.id) === id) || null;
function gdAturPengingat() { const d = gdDokAtur('pengingat') || {}; const o = {}; Object.keys(GD_PENGINGAT_BAWAAN).forEach((k) => { o[k] = d[k] !== undefined && d[k] !== null ? Number(d[k]) || GD_PENGINGAT_BAWAAN[k] : GD_PENGINGAT_BAWAAN[k]; }); return o; }
const gdHariKe = (iso) => Math.round(new Date(String(iso) + 'T00:00:00Z').getTime() / 86400000);
/** Cek mingguan timbangan & gudang: sama dengan ssCekGudang (terakhir = dokumen cekGudang terbaru; jatuh = terakhir + tiap; belum pernah = hari ini). */
export function gdCekGudang(kini) {
  const iso = hariIniIso(kini); const tiap = gdAturPengingat().gudangTiap;
  const t = cacheMentah('cekGudang').filter((d) => d && /^\d{4}-\d{2}-\d{2}$/.test(String(d.tanggal || ''))).slice().sort((a, b) => String(b.tanggal + ' ' + (b.jam || '')).localeCompare(String(a.tanggal + ' ' + (a.jam || ''))) || String(b.id).localeCompare(String(a.id)))[0] || null;
  const jatuh = t ? gdTambahHari(t.tanggal, tiap) : iso; const sisa = gdHariKe(jatuh) - gdHariKe(iso);
  return { jatuh, sisa, terakhir: t ? t.tanggal : '', teks: !t ? 'Belum pernah dicek — cek hari ini' : sisa < 0 ? 'Lewat ' + (-sisa) + ' hari (terakhir ' + tanggalPendek(t.tanggal) + ')' : sisa === 0 ? 'Waktunya hari ini (terakhir ' + tanggalPendek(t.tanggal) + ')' : 'Berikutnya ' + tanggalPendek(jatuh) + ' · ' + sisa + ' hari lagi' };
}

/**
 * B49 · B50 — semua buku yang MINUS (ambang yang SAMA dengan minusBuku: beras ≤ −0,01 kg, kemasan & kantong < −0,001), dengan rupiahnya.
 * → { n, perJenis: { beras, kemasan, kantong }, rp (Σ, minus), kgBeras, daftar (urut terdalam), top (GD_TOP pertama), kalimat }.
 */
export function gdMinus(kini) {
  const iso = hariIniIso(kini); const W = petaBukuWadah(); const d = [];
  const K = ingatStokKarung(iso); Object.keys(K).forEach((m) => { const s = K[m].sisaKg; if (!(s <= -0.01)) return; const v = Number(K[m].hppTerakhirPerKg) || 0;
    d.push({ jenis: 'beras', kunci: m, nama: m, wadah: !!W[m], jumlah: s, satuan: 'kg', teksJumlah: KG(s), nilai: v, rp: v > 0 ? Math.round(s * v) : 0, dinilai: v > 0,
      jalan: 'hitung isinya di Stok › Cocokkan, atau catat kedatangan / pindah buku yang terlupa', tujuan: { ke: 'stok', lembar: 'cocok' } }); });
  const KM = ingatStokKemasan(iso); Object.keys(KM).forEach((k) => { const s = KM[k]; if (!(s.sisaUnit < -0.001)) return; const v = Number(s.hppRataRataPerUnit) || 0;
    d.push({ jenis: 'kemasan', kunci: k, nama: s.namaProduk + ' ' + String(s.ukuranKemasan).replace('.', ',') + ' kg', wadah: false, jumlah: s.sisaUnit, satuan: 'kantong', teksJumlah: ANGKA(s.sisaUnit) + ' kantong', nilai: v,
      rp: v > 0 ? Math.round(s.sisaUnit * v) : 0, dinilai: v > 0, jalan: 'hitung kemasannya di Stok › Cocokkan › kemasan, atau catat adukan yang terlupa', tujuan: { ke: 'stok', lembar: 'cocok' } }); });
  [[hitungStokBahanKemasan(iso), 'hppPerPcs', 'kantong kemasan'], [hitungStokBahanLiteran(iso), 'hargaPerPcs', 'kantong literan']].forEach(([P, kol, jenis]) => Object.keys(P).forEach((j) => {
    const s = P[j].sisaPcs; if (!(s < -0.001)) return; const v = Number(P[j][kol]) || 0;
    d.push({ jenis: 'kantong', kunci: j, nama: labelBahan(j), wadah: false, jumlah: s, satuan: 'lembar', teksJumlah: ANGKA(s) + ' lembar', nilai: v, rp: v > 0 ? Math.round(s * v) : 0, dinilai: v > 0,
      jalan: 'hitung ' + jenis + ' di Stok › Kantong, atau catat pembelian kantong yang terlupa', tujuan: { ke: 'stok', lembar: 'kantong' } }); }));
  // terdalam dulu: rupiah paling minus; yang belum bisa dinilai di belakang (urut jumlahnya) — supaya "10 terbesar" tidak dikuasai buku tanpa harga beli
  d.sort((a, b) => (a.dinilai === b.dinilai ? (a.dinilai ? a.rp - b.rp : a.jumlah - b.jumlah) : a.dinilai ? -1 : 1) || a.nama.localeCompare(b.nama));
  const per = { beras: 0, kemasan: 0, kantong: 0 }; d.forEach((x) => { per[x.jenis] += 1; });
  const rp = d.reduce((a, x) => a + x.rp, 0); const kgBeras = d.filter((x) => x.jenis === 'beras').reduce((a, x) => a + x.jumlah, 0); const tanpa = d.filter((x) => !x.dinilai).length;
  const kalimat = !d.length ? 'Tidak ada buku yang minus — semua barang di buku ≥ 0.'
    : d.length + ' buku minus (' + Object.keys(per).filter((j) => per[j]).map((j) => per[j] + ' ' + GD_JENIS_STOK[j].toLowerCase()).join(' · ') + ') · nilai ' + RP(rp) + (tanpa ? ' · ' + tanpa + ' belum bisa dinilai (belum ada harga beli)' : '')
      + '. Buku minus ikut terbawa ke tutup buku 2026 sampai dicocokkan.';
  return { iso, n: d.length, perJenis: per, rp, kgBeras, tanpaNilai: tanpa, daftar: d, top: d.slice(0, GD_TOP), lebih: Math.max(0, d.length - GD_TOP), kalimat, sumber: 'Stok › Cocokkan', tujuan: { ke: 'stok', lembar: 'cocok' } };
}

/**
 * B53 — barang hilang & rusak per JENIS beras satu bulan ('YYYY-MM'). Hilang/lebih = baris merekBulan (susutKg/susutRp, naikKg/naikRp) dikelompokkan per jenis;
 * kantong & bahan = kelompok sendiri. Rusak = retur tidak layak jual bertanggal bulan itu (kg + taksiran modal), nasibnya dari karantina. PENJAGA: Σ rupiah semua
 * kelompok = "Susut & selisih stok" Laporan bulan itu (L.susutStok). Bulan yang sudah ditutup buku = ikut arsip (disebut).
 */
export function gdBuang(key, kini) {
  const M = merekBulan(key, kini); const dasar = { key, nama: M.nama, berjalan: !!M.berjalan, sumber: 'Laporan › Laba › Per merek', tujuan: { ke: 'laporan', keluarga: 'laba', bulan: key } };
  if (M.diarsip) return Object.assign(dasar, { diarsip: true, jenis: [], kalimat: M.kalimat, menutup: null });
  const per = {}; const g = (j) => (per[j] = per[j] || { jenis: j, hilangKg: 0, hilangRp: 0, naikKg: 0, naikRp: 0, rusakKg: 0, rusakRp: 0, nRusak: 0, merek: [] });
  M.merek.forEach((x) => { if (!(x.nSusut > 0) && !(x.susutKg || x.naikKg || x.susutRp || x.naikRp)) return; const G = g(gdJenis(x.merek));
    G.hilangKg += Number(x.susutKg) || 0; G.hilangRp += Number(x.susutRp) || 0; G.naikKg += Number(x.naikKg) || 0; G.naikRp += Number(x.naikRp) || 0;
    if ((x.susutKg || 0) > 0.004 && G.merek.indexOf(x.merek) < 0) G.merek.push(x.merek); });
  // di luar merek (kantong & bahan, nilai karung bekas, …) — rupiahnya ikut "Susut & selisih stok" Laporan, bukan beras
  const luar = M.luar && M.luar.rincian ? M.luar.rincian : []; const bahan = { hilangRp: 0, naikRp: 0, nama: 'Kantong, bahan & di luar merek' };
  luar.forEach((x) => { bahan.hilangRp += Number(x.susutRp) || 0; bahan.naikRp += Number(x.naikRp) || 0; });
  // retur tidak layak jual (rusak / diragukan) — kg & taksiran modalnya, nasibnya di karantina (id karantina = id retur)
  const awal = key + '-01', akhir = key + '-31'; const kar = {}; ambilKarantina().forEach((k) => { kar[String(k.id)] = k; });
  const stokK = ingatStokKarung(), stokM = ingatStokKemasan(); const nasib = { dibuang: 0, dikembalikan_pemasok: 0, dirework: 0, layak_jual: 0, belum_diputuskan: 0 };
  ambilRetur().forEach((r) => { const t = String(r.tanggal || ''); if (t < awal || t > akhir || r.kondisi === 'utuh') return; const kg = Number(r.totalKg) || 0;
    const nama = r.jenisAsal === 'karung' ? r.merkSumber : (r.namaProduk || r.merkSumber); const G = g(gdJenis(nama)); let rp = 0; try { rp = Math.round(hppTaksiranRetur(r, stokK, stokM) || 0); } catch (e) { rp = 0; }
    G.rusakKg += kg; G.rusakRp += rp; G.nRusak += 1; const k = kar[String(r.id)]; const st = k ? (k.statusTindakan || 'belum_diputuskan') : 'belum_diputuskan'; nasib[nasib[st] !== undefined ? st : 'belum_diputuskan'] += kg; });
  const jenis = Object.keys(per).map((j) => per[j]).sort((a, b) => a.hilangRp - b.hilangRp || b.rusakKg - a.rusakKg || a.jenis.localeCompare(b.jenis));
  const sig = (f) => jenis.reduce((a, x) => a + x[f], 0);
  const rpSusut = sig('hilangRp') + sig('naikRp') + bahan.hilangRp + bahan.naikRp; const laporan = M.L ? Number(M.L.susutStok) || 0 : 0;
  const menutup = Math.abs(rpSusut - laporan) < 0.5 && M.menutup !== false;
  const total = { hilangKg: sig('hilangKg'), hilangRp: sig('hilangRp'), naikKg: sig('naikKg'), naikRp: sig('naikRp'), rusakKg: sig('rusakKg'), rusakRp: sig('rusakRp'), nRusak: sig('nRusak') };
  const kalimat = (!jenis.length && !bahan.hilangRp && !bahan.naikRp ? 'Tidak ada beras yang hilang, lebih, atau rusak tercatat ' + M.nama + '.'
    : 'Hilang ' + KG(total.hilangKg) + ' (' + RP(total.hilangRp) + ')' + (total.naikKg ? ' · lebih dari buku ' + KG(total.naikKg) + ' (' + RP(total.naikRp) + ')' : '') + (total.rusakKg ? ' · rusak dikembalikan pembeli ' + KG(total.rusakKg) + ' (taksiran modal ' + RP(total.rusakRp) + ')' : ''))
    + (menutup ? ' — rupiah hilang & lebih menutup ke "Susut & selisih stok" Laporan ' + RP(laporan) + '.' : ' — TIDAK MENUTUP ke Laporan (' + RP(rpSusut) + ' ≠ ' + RP(laporan) + '); jangan dipakai memutuskan, laporkan.');
  return Object.assign(dasar, { diarsip: false, jenis, bahan, total, nasib, laporan, rpSusut, menutup, kalimat });
}

/** Opname terakhir & jatuh berikutnya — sumber yang SAMA dengan pengingat 'opname' (sistem-logika ssSumberPengingat): penyesuaian beras/kemasan (bukan rework) + opname kantong. */
export function gdOpname(kini) {
  const iso = hariIniIso(kini); const A = gdAturPengingat(); let akhir = '';
  ambilPenyesuaianStok().concat(ambilPenyesuaianKemasan()).forEach((x) => { if (x.dariRework) return; if ((x.tanggal || '') > akhir) akhir = x.tanggal; });
  ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((x) => { if (x.tipe === 'opname' && (x.tanggal || '') > akhir) akhir = x.tanggal; });
  const jatuh = akhir ? gdTambahHari(akhir, Number(A.opnameTiap) || 14) : iso; return { akhir, jatuh, perlu: jatuh <= iso, tiap: Number(A.opnameTiap) || 14 };
}

/**
 * B54 — tugas gudang yang masih terbuka, satu baris per jenis (n = jumlahnya; 0 = beres, tetap ditulis supaya owner tahu sudah dicek). Tiap baris membawa tujuan
 * (bentuk baris Menu) ke layar yang menyelesaikannya. `w` = { tanggal, jam } untuk penjaga karantina. Satu sumber galat tidak mematikan baris lain.
 */
export function gdTugas(kini, w) {
  const iso = hariIniIso(kini); const W = w || { tanggal: iso, jam: '12:00' }; const out = [];
  const baris = (id, nama, f) => { try { const r = f(); out.push(Object.assign({ id, nama }, r)); } catch (e) { out.push({ id, nama, n: null, ket: 'tidak terbaca: ' + String((e && e.message) || e), awas: false, galat: true }); } };
  baris('masuk', 'Kabar barang masuk dari tablet', () => { const d = cacheMentah('persetujuan').filter((m) => m && m.tindakan === 'barangMasuk' && (m.status || 'menunggu') === 'menunggu');
    return { n: d.length, ket: d.length ? 'menunggu diperiksa owner · ' + d.slice(0, 2).map((m) => String(m.teks || '').slice(0, 60)).join(' · ') : 'tidak ada yang menunggu', awas: d.length > 0, tujuan: { ke: 'stok', lembar: 'masuk' } }; });
  baris('pesanPemasok', 'Pesanan ke pemasok belum datang', () => { const d = pesananSemua().filter((p) => p.status === 'menunggu');
    // paket P3 (owner 27 Nov 2026, B67): + kg & perkiraan Rp yang masih menunggu (gdPesananPemasok — satu sumber dengan Dasbor › Pembelian)
    const P = gdPesananPemasok(d); return { n: d.length, kg: P.kg, rp: P.rp, ket: d.length ? P.kalimat + ' · ' + d.slice(0, 3).map((p) => (p.pemasok || 'pemasok') + ' ' + tanggalPendek(p.tanggal)).join(' · ') : 'tidak ada', awas: false, tujuan: { ke: 'harga', keluarga: 'belanja' } }; });
  // paket P3 (owner 27 Nov 2026, B129): nota "jual dulu, tandai untuk dicocokkan" yang belum dicocokkan — tuntas sendiri saat cocokkan nama itu bertanggal ≥ notanya
  baris('tembus', 'Nota "jual dulu, tandai" belum dicocokkan', () => { const T = notaTembusBelumCocok();
    return { n: T.n, ket: T.n ? T.nama.slice(0, 3).map((x) => x.nama + ' ' + KG(x.kg) + ' (' + x.n + ' nota)').join(' · ') + (T.nama.length > 3 ? ' · +' + (T.nama.length - 3) + ' nama' : '') + ' — cocokkan nama itu' : 'tidak ada', awas: T.n > 0, tujuan: { ke: 'stok', lembar: 'cocok' }, nama: T.nama }; });
  baris('pesanan', 'Pesanan pelanggan belum dikirim', () => { const hP = poHariKe(iso); const d = poDaftarAktif('').filter((o) => o.status === 'dipesan'); const segera = d.filter((o) => o.tanggalKirim && poHariKe(o.tanggalKirim) - hP <= 1);
    return { n: d.length, ket: d.length ? (segera.length ? segera.length + ' dikirim hari ini / besok · ' : '') + d.slice(0, 3).map((o) => o.nama + (o.tanggalKirim ? ' ' + tanggalPendek(o.tanggalKirim) : '')).join(' · ') : 'tidak ada', awas: segera.length > 0, tujuan: { ke: 'jual', lembar: 'pesanan' } }; });
  baris('janji', 'Lewat janji datang / antar', () => { const L = jnLewat(kini); const P = L.filter((x) => x.jenis === 'pemasok'); const A = L.filter((x) => x.jenis !== 'pemasok');
    return { n: L.length, ket: L.length ? [P.length ? P.length + ' pesanan pemasok' : '', A.length ? A.length + ' kiriman pelanggan' : ''].filter(Boolean).join(' · ') + ' · ' + L.slice(0, 3).map((x) => x.nama + ' ' + jnKataJanji(x.janji) + ' (telat ' + x.telat + ' hr)').join(' · ') : 'tidak ada yang lewat janji',
      awas: L.length > 0, tujuan: L.length ? L[0].tujuan : { ke: 'laporan', keluarga: 'pondasi' }, daftar: L }; });
  baris('antar', 'Antar masih di jalan / gagal', () => { const A = ajDaftar(iso, ''); const n = A.jalan.length + A.gagal.length;
    return { n, ket: n ? A.jalan.length + ' di jalan · ' + A.gagal.length + ' gagal belum dibereskan' : 'tidak ada', awas: A.gagal.length > 0, tujuan: { ke: 'jual', lembar: 'antar' } }; });
  baris('karantina', 'Karantina menunggu keputusan', () => { const K = daftarKarantina(W);
    return { n: K.antre.length, ket: K.antre.length ? KG(K.totalKg) + ' · ' + K.antre.slice(0, 3).map((x) => x.nama).join(', ') : 'kosong', awas: K.antre.length > 0, tujuan: { ke: 'stok', tab: 'karantina' } }; });
  baris('opname', 'Opname rutin', () => { const O = gdOpname(kini);
    return { n: O.perlu ? 1 : 0, ket: O.akhir ? 'terakhir ' + tanggalPendek(O.akhir) + ' · ' + (O.perlu ? 'sudah waktunya (tiap ' + O.tiap + ' hari)' : 'berikutnya ' + tanggalPendek(O.jatuh)) : 'belum pernah dicocokkan', awas: O.perlu, tujuan: { ke: 'stok', lembar: 'cocok' } }; });
  baris('cekGudang', 'Cek mingguan timbangan & gudang', () => { const G = gdCekGudang(kini); const perlu = G.sisa <= 0;
    return { n: perlu ? 1 : 0, ket: G.teks, awas: G.sisa < 0, tujuan: { ke: 'sistem', sistem: 'pengingat' } }; });
  baris('wadah', 'Wadah literan perlu diisi', () => { const S = susunWadah(null); const n = S.daftar.filter((x) => x.diketahui && x.perluIsi).length;
    return { n, ket: n ? S.daftar.filter((x) => x.diketahui && x.perluIsi).slice(0, 4).map((x) => x.nama).join(', ') : 'semua cukup', awas: false, tujuan: { ke: 'stok', tab: 'wadah' } }; });
  baris('minus', 'Buku minus perlu dicocokkan', () => { const M = gdMinus(kini); return { n: M.n, ket: M.n ? M.top.slice(0, 3).map((x) => x.nama + ' ' + x.teksJumlah).join(' · ') : 'tidak ada', awas: M.n > 0, tujuan: { ke: 'stok', tab: 'tugas' } }; });
  baris('kemasan', 'Kemasan lewat / dekat "baik dipakai sebelum"', () => { const R = lbRingkasKemasan(kini); const n = R.lewat.length + R.dekat.length;
    return { n, ket: n ? (R.lewat.length ? R.lewat.length + ' lewat · ' : '') + R.dekat.length + ' ≤ ' + R.ambang + ' hari · ' + R.lewat.concat(R.dekat).slice(0, 3).map((x) => x.nama).join(', ') : (R.nBertanggal ? 'aman' : 'belum ada kemasan bertanggal'), awas: R.lewat.length > 0, tujuan: { ke: 'stok', tab: 'tugas' } }; });
  const L = (() => { const d = gdDokAtur('lokasi'); return d && Array.isArray(d.daftar) && d.daftar.length ? d.daftar.length : 1; })();
  const terbuka = out.filter((x) => x.n > 0); const n = terbuka.reduce((a, x) => a + x.n, 0);
  return { iso, daftar: out, terbuka, n, nJenis: terbuka.length, awas: out.some((x) => x.awas), pindahLokasi: L < 2 ? 'Pindah stok antar lokasi: toko satu lokasi — tidak berlaku sampai lokasi kedua ditambahkan di Menu › Toko ini › Lokasi.' : '',
    kalimat: terbuka.length ? n + ' tugas terbuka di ' + terbuka.length + ' jenis' : 'Semua tugas gudang beres', sumber: 'Stok › Tugas gudang', tujuan: { ke: 'stok', tab: 'tugas' } };
}

/**
 * B67 (paket P3, owner 27 Nov 2026) — pesanan ke pemasok yang MASIH MENUNGGU: jumlah, karung, kg, dan perkiraan rupiah (harga beli terakhir yang dipakai saat
 * pesanan dibuat — kolom rp & kg dokumen pesananPemasok, Harga & Pemasok › Belanja). d = daftar menunggu (bawaan pesananSemua). Pesanan lama tanpa harga = disebut.
 */
export function gdPesananPemasok(d) {
  const D = d || pesananSemua().filter((p) => p.status === 'menunggu'); const per = {};
  D.forEach((p) => { const k = String(p.pemasok || 'pemasok'); const g = per[k] = per[k] || { pemasok: k, n: 0, kg: 0, rp: 0, karung: 0, janji: '' }; g.n += 1; g.kg += Number(p.kg) || 0; g.rp += Number(p.rp) || 0; g.karung += Number(p.karung) || 0;
    const jt = String(p.janjiTanggal || ''); if (jt && (!g.janji || jt < g.janji)) g.janji = jt; });
  const kg = D.reduce((a, p) => a + (Number(p.kg) || 0), 0), rp = D.reduce((a, p) => a + (Number(p.rp) || 0), 0), karung = D.reduce((a, p) => a + (Number(p.karung) || 0), 0); const tanpaHarga = D.filter((p) => !(Number(p.rp) > 0)).length;
  return { n: D.length, kg, rp, karung, tanpaHarga, pemasok: Object.keys(per).map((k) => per[k]).sort((a, b) => b.rp - a.rp || b.kg - a.kg || a.pemasok.localeCompare(b.pemasok)),
    kalimat: D.length ? KG(kg) + ' · ±' + RP(rp) + (tanpaHarga ? ' (' + tanpaHarga + ' pesanan tanpa harga)' : '') : 'tidak ada pesanan yang menunggu', sumber: 'Harga & Pemasok › Belanja', tujuan: { ke: 'harga', keluarga: 'belanja' } };
}

/** Sumber pengingat jenis 'minus' (diteruskan app.js lewat lokal.gudang, pola lokal.pajak): satu baris per HARI selama ada buku minus. */
export function gdSumberPengingat(kini) {
  const iso = hariIniIso(kini); const M = gdMinus(kini); if (!M.n) return [];
  return [{ id: 'minus|' + iso, jenis: 'minus', kunci: 'minus', teks: M.n + ' buku stok minus', siapa: 'stok', jatuh: iso, n: 0, ket: M.top.slice(0, 3).map((x) => x.nama + ' ' + x.teksJumlah).join(' · ') + ' — Stok › Cocokkan' }];
}

/** Dasbor (kelompok stok): angka yang SAMA dengan Stok › Tugas gudang — tidak dihitung ulang di dasbor-logika. */
export function gdDasbor(kini) {
  const M = gdMinus(kini); const T = gdTugas(kini); const B = gdBuang(hariIniIso(kini).slice(0, 7), kini);
  return { minus: { n: M.n, rp: M.rp, perJenis: M.perJenis, top: M.top.slice(0, 3).map((x) => ({ nama: x.nama, teks: x.teksJumlah, rp: x.rp, dinilai: x.dinilai })), kalimat: M.kalimat },
    tugas: { n: T.n, nJenis: T.nJenis, awas: T.awas, terbuka: T.terbuka.map((x) => ({ id: x.id, nama: x.nama, n: x.n, ket: x.ket, awas: !!x.awas, tujuan: x.tujuan })), kalimat: T.kalimat },
    buang: B.diarsip ? { diarsip: true, kalimat: B.kalimat } : { nama: B.nama, hilangKg: B.total.hilangKg, hilangRp: B.total.hilangRp, rusakKg: B.total.rusakKg, rusakRp: B.total.rusakRp, menutup: B.menutup,
      jenis: B.jenis.slice(0, 3).map((x) => ({ jenis: x.jenis, kg: x.hilangKg, rp: x.hilangRp, rusakKg: x.rusakKg })), kalimat: B.kalimat },
    kemasan: (() => { const R = lbRingkasKemasan(kini); return { lewat: R.lewat.length, dekat: R.dekat.length, ambang: R.ambang, nama: R.lewat.concat(R.dekat).slice(0, 3).map((x) => x.nama + ' ' + (x.tertua.sisaHari < 0 ? 'lewat' : x.tertua.sisaHari + ' hr')) }; })(),
    tujuan: { ke: 'stok', tab: 'tugas' } };
}
