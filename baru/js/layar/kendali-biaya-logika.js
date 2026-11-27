// LOGIKA KENDALI BIAYA (putaran 38, 29 Sep 2026) — cost controlling, tanpa DOM. Lima bagian yang menjadi satu layar Laporan › Biaya:
//   1. JENIS BIAYA — tiap rupiah di bawah margin kotor punya kelompok: upah & gaji · tagihan tetap (listrik · internet · akses · keamanan) · karyawan di
//      luar upah · dapur toko (bahan masak) · bahan pakai & kresek · bensin & angkut · potongan QRIS & biaya bank · lain-lain. Di bawahnya hapus buku piutang
//      dan susut & selisih stok (mesin menaruh keduanya di BAWAH laba kotor). Uang keluar dipilah dari kolom `untuk` (putaran 29), tanda `mdr`/biaya bank,
//      lalu KATA KUNCI (bawaan + tambahan owner di aturanToko/kendaliBiaya.kata). Yang tidak cocok kata mana pun TETAP dihitung — di baris "Lain-lain" dan
//      DISEBUT jumlahnya sebagai "jenisnya belum dikenali" (39b no. 25: bukan "belum dipilah" — itu tujuan toko/karyawan di Uang); tidak ada catatan yang hilang dari jumlah, dan tidak ada tebakan yang disembunyikan.
//   2. ANGGARAN — angka per jenis per bulan MILIK OWNER (aturanToko/kendaliBiaya.anggaran; 0 = belum diatur). Tanpa anggaran tidak ada lampu — hanya
//      "acuan terukur" = median bulan-bulan sebelumnya yang punya catatan, disebut begitu. Tombol "isi dari acuan" mengisi FORMULIR; yang menjadi anggaran
//      tetap yang owner simpan. Anggaran bukan larangan (aturan jatah 22 Agu 2026): lewat tetap tersimpan, bedanya ketahuan malam itu.
//   3. AKTUAL vs ANGGARAN — selisih, lampu (hijau ≤ anggaran · amber ≤ anggaran + ambang % · merah di atasnya), bulan berjalan: jenis variabel dibanding
//      jatah SAMPAI HARI KE-N (anggaran × hari jalan ÷ hari bulan) dan diberi PERKIRAAN sebulan (linear, disebut perkiraan); jenis tetap dibanding anggaran
//      sebulan. Upah bulan berjalan ditambah upah yang BELUM DIBAYAR (dari absen, upah-logika) sebelum dibandingkan — supaya "upah baru Rp240 rb" tidak
//      dibaca sebagai hemat padahal cuma belum gajian.
//   4. PEMICU BIAYA — biaya per satuan bulan ini vs bulan lalu: biaya toko per kg terjual · HPP & harga jual per kg · bongkar per kg kedatangan · harga beli
//      per kg · potongan QRIS % omzet QRIS · biaya karyawan per hari kerja · harga kantong per lembar. Naik di atas ambang pemicu → disebut.
//   5. TITIK IMPAS & PERINGATAN — omzet yang harus dicapai supaya margin kotor menutup biaya di bawahnya (biaya ÷ rasio margin), per hari, dan apakah bulan
//      berjalan SAMPAI HARI INI sudah menutup (dari mesin, rentang awal bulan → hari ini). Peringatan = daftar yang bengkak/hilang/belum lengkap, tiap baris
//      menunjuk layar tempat membereskannya. Pareto = catatan terbesar yang membentuk 80 % biaya.
// SEMUA angka uang dari mesin beku yang sama (hitungLabaBersihRentang lewat ugLabaBersih = + lebih/kurang kas, bayaranBiayaBulanan, hitungArusKasInti) — modul ini hanya MEMILAH lalu MEMBANDINGKAN.
// Wajib MENUTUP: Σ jenis harian = harianToko mesin; upah + tagihan tetap = jatahBulanan mesin; margin − Σ jenis − hapus buku + susut = laba bersih mesin.
// Tidak ada perilaku uang yang berubah; yang BARU ditulis hanya aturanToko/kendaliBiaya. Nama pembantu diprefiks `kb` (bundel uji jsc satu lingkup).
// Paket B (siap 2027): bulan di tahun yang sudah ditutup buku = POTRET saat kunci (kendaliPotret di bawah, ditulis tutup buku) — jumlah per jenis & bahan pemicu
// tetap, rincian per catatan sudah diarsip (disebut, bukan digambar kosong). Bulan lalu (Desember) untuk pemicu & acuan Januari ikut membaca potret.
import { hitungArusKasInti, bayaranBiayaBulanan } from '../mesin/beku.js';
import { akhirBulanIso, bulanDari, POS_BIAYA_BULANAN, hppTercatat, caraBayarKunci } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPengeluaranHarian, ambilSemuaBatch, ambilBahanKemasan, ambilBahanLiteran, ambilBiayaBulanan, ambilPiutangMutasi, ambilKasbonMutasi, potretBulan } from '../data/toko.js';
import { RP, ANGKA, DESIMAL, hariIniIso, tanggalPendek } from '../inti/format.js';
import { ugAturDok, ugAngka, ugKosong, ugUntukDok, adalahMdr, ugLabaBersih, ugBayaran, ugEfekAset } from './uang-logika.js';
import { lpFinal, lpNamaBulan, lpBulanPendek, daftarBulan, lpAwalBuku, lpKetSebelumBuku } from './laporan-logika.js';
import { semuaUpah } from './upah-logika.js';
// B3 (owner 18 Nov 2026): ongkir antar yang DITAGIH ke pembeli dibaca di samping biaya Bensin & angkut (ongkir = pendapatan nota, bukan pengurang biaya)
import { ajOngkirRentang } from './antar-logika.js';

// ---------- jenis biaya: urutan = urutan pemilahan (yang di atas menang) & urutan baris di layar ----------
export const JENIS_BIAYA = [
  { id: 'upah', nama: 'Upah & gaji', sifat: 'tetap', ket: 'baris gaji Tagihan bulanan, gaji KOTOR sebelum potongan kasbon (mesin laba)', kata: [] },
  { id: 'tetap', nama: 'Tagihan tetap', sifat: 'tetap', ket: 'listrik · internet · akses/gapura · keamanan (Tagihan bulanan)', kata: [] },
  { id: 'keuangan', nama: 'Potongan QRIS & biaya bank', sifat: 'variabel', ket: 'catatan bertanda MDR, biaya admin bayar bon / pindah uang, atau kata kunci', kata: ['potongan', 'mdr', 'qris', 'biaya admin', 'admin bank', 'admin transfer'] },
  { id: 'karyawan', nama: 'Karyawan di luar upah', sifat: 'variabel', ket: 'catatan "untuk karyawan" (putaran 29) atau kata kunci', kata: ['kopi', 'roko', 'makan', 'jajan', 'nasi', 'mie'] },
  { id: 'bahan', nama: 'Bahan pakai & kresek', sifat: 'variabel', ket: 'kresek belanja, lakban, benang, rafia, staples — operasional, bukan HPP (keputusan 2 Agu 2026)', kata: ['plastik', 'kantong', 'kresek', 'lakban', 'benang', 'rafia', 'staples', 'tali', 'wipol', 'sabun', 'pulpen', 'kertas', 'tinta', 'baterai'] },
  { id: 'angkut', nama: 'Bensin & angkut', sifat: 'variabel', ket: 'bensin antar, ongkos, kuli, parkir — bongkar mobil pemasok TIDAK di sini (sudah di dalam HPP)', kata: ['bensin', 'ongkos', 'angkut', 'kuli', 'bongkar', 'parkir', 'tol', 'antar'] },
  { id: 'dapur', nama: 'Dapur toko (bahan masak)', sifat: 'variabel', ket: 'bahan mentah untuk memasak di toko = biaya toko (owner 27 Sep 2026)', kata: ['kebutuhan masak', 'kebutuhan dapur', 'bahan masak', 'masak', 'telur', 'gas', 'gula', 'minyak', 'bawang', 'tahu', 'tempe', 'sayur', 'roti', 'ikan', 'ayam', 'garam', 'kecap', 'cabai', 'cabe', 'galon', 'air minum'] },
  { id: 'lain', nama: 'Lain-lain', sifat: 'variabel', ket: 'tidak cocok kata kunci mana pun — tetap dihitung, disebut "jenisnya belum dikenali"', kata: [] },
];
/** Dua baris yang mesin taruh di BAWAH laba kotor tapi bukan biaya toko: hapus buku piutang & susut. Susut boleh diberi anggaran (= toleransi). */
export const JENIS_BAWAH = [{ id: 'hapus', nama: 'Hapus buku piutang', sifat: 'lain', ket: 'piutangMutasi tipe hapusBuku (mesin laba)' }, { id: 'susut', nama: 'Susut & selisih stok', sifat: 'lain', ket: 'penyesuaian stok/kemasan & opname kantong (mesin laba) — positif = stok berkurang = biaya' }];
export const ID_ANGGARAN = JENIS_BIAYA.filter((j) => j.id !== 'lain').map((j) => j.id).concat(['susut']);
/** A47 (owner 27 Nov 2026): PPh final (perkiraan) = POS ANGGARAN SENDIRI — anggarannya disimpan di dokumen yang sama (anggaran.pph), tapi BUKAN baris biaya
 *  (tidak ikut Σ jenis = biaya mesin, laba bersih, titik impas; keputusan owner: pos sisihan). Angkanya: kpi-laba-logika klPph. */
export const ID_ANGGARAN_PAJAK = 'pph';
const KB_ID_SIMPAN = ID_ANGGARAN.concat([ID_ANGGARAN_PAJAK]);
export const ATUR_KENDALI_BAWAAN = { anggaran: {}, ambang: 10, ambangPemicu: 10, kata: {} };
const KB_POS_TETAP = POS_BIAYA_BULANAN.map((p) => p.kunci);

const kbPolos = (s) => String(s || '').toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
const kbBulat = (n) => Math.round(Number(n) || 0);
const kbKey = (iso) => String(iso).slice(0, 7);
const kbGeser = (key, n) => { const y = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)) - 1 + n; const d = new Date(Date.UTC(y + Math.floor(m / 12), ((m % 12) + 12) % 12, 1)); return d.toISOString().slice(0, 7); };
const kbPct = (a, b) => (b > 0 ? Math.round(a / b * 1000) / 10 : null);
export const kbPctTeks = (p) => (p === null || p === undefined || !isFinite(p) ? '—' : (p < 0 ? '−' : '') + DESIMAL(Math.abs(Math.round(p * 10) / 10)) + '%');
const kbMedian = (arr) => { const s = arr.slice().sort((a, b) => a - b); return s.length ? (s.length % 2 ? s[(s.length - 1) / 2] : Math.round((s[s.length / 2 - 1] + s[s.length / 2]) / 2)) : null; };
const kbBiayaBank = (h) => !!(h.dariBayarBon || h.dariPindah) || /^biaya admin/i.test(String(h.keterangan || ''));

// ---------- aturan owner ----------
export function aturKendali() {
  const a = ugAturDok('kendaliBiaya') || {}; const anggaran = {}; KB_ID_SIMPAN.forEach((id) => { const n = Number(a.anggaran && a.anggaran[id]); anggaran[id] = isFinite(n) && n > 0 ? Math.round(n) : 0; });
  const persen = (v, b) => (isFinite(Number(v)) && Number(v) >= 0 && Number(v) <= 100 ? Math.round(Number(v) * 10) / 10 : b);
  const kata = {}; JENIS_BIAYA.forEach((j) => { const d = a.kata && Array.isArray(a.kata[j.id]) ? a.kata[j.id] : []; kata[j.id] = d.map(kbPolos).filter(Boolean); });
  return { anggaran, ambang: persen(a.ambang, ATUR_KENDALI_BAWAAN.ambang), ambangPemicu: persen(a.ambangPemicu, ATUR_KENDALI_BAWAAN.ambangPemicu), kata, dariOwner: !!ugAturDok('kendaliBiaya'), nAnggaran: ID_ANGGARAN.filter((id) => anggaran[id] > 0).length, tanggal: a.tanggal || '' };
}
/** Kata kunci satu jenis = kata owner (didahulukan) + kata bawaan. */
export const kataJenis = (A, id) => (A.kata[id] || []).concat((JENIS_BIAYA.find((j) => j.id === id) || { kata: [] }).kata);
/** Kata pertama dari `kata` yang cocok sebagai AWALAN KATA di batas kata ('roko' kena 'rokok', 'biaya admin' kena 'biaya admin bi-fast'); '' bila tidak ada. */
const kbCocokKata = (polos, kata) => { const t = ' ' + polos; for (const k of kata) { if (k && t.indexOf(' ' + k) >= 0) return k; } return ''; };
const kbAdaMdr = (h) => adalahMdr(h);   // 39b no. 24: satu pengenal dengan laporan & pilah harian (uang-logika.js)
/** Jenis satu catatan uang keluar (kategori toko/tokoDompet). Urutan: tanda MDR/bank → kolom `untuk` karyawan → kata owner tiap jenis → kata bawaan tiap jenis → lain.
 *  Mengembalikan { id, dari: tanda|untuk|kataOwner|kataBawaan|belum, kata (yang cocok), kunci (untuk pengelompokan pareto), mdr }. */
export function jenisCatatan(h, A) {
  const polos = kbPolos(h.keterangan); const mdr = kbAdaMdr(h, polos);
  if (h.mdr || kbBiayaBank(h)) return { id: 'keuangan', dari: 'tanda', kata: '', kunci: mdr ? 'potongan qris' : 'biaya admin bank', mdr };
  if (ugUntukDok(h) === 'karyawan') return { id: 'karyawan', dari: 'untuk', kata: '', kunci: polos || '(tanpa keterangan)', mdr: false };
  for (const j of JENIS_BIAYA) { if (j.id === 'lain' || j.id === 'upah' || j.id === 'tetap') continue; const k = kbCocokKata(polos, A.kata[j.id] || []); if (k) return { id: j.id, dari: 'kataOwner', kata: k, kunci: k, mdr }; }
  for (const j of JENIS_BIAYA) { if (j.id === 'lain' || j.id === 'upah' || j.id === 'tetap') continue; const k = kbCocokKata(polos, j.kata); if (k) return { id: j.id, dari: 'kataBawaan', kata: k, kunci: k, mdr }; }
  return { id: 'lain', dari: 'belum', kata: '', kunci: polos || '(tanpa keterangan)', mdr: false };
}

// ---------- inti satu bulan (dipakai bulan ini, bulan lalu, acuan, tren) ----------
function kbInti(key, kini, B, A) {
  const Pt = potretBulan(key); if (Pt && Pt.kb) return kbDariPotret(key, kini, Pt);   // Paket B: tahun yang sudah ditutup buku
  const iso = hariIniIso(kini); const awal = key + '-01', akhir = akhirBulanIso(key); const L = ugLabaBersih(awal, akhir, B);
  const berjalan = key === kbKey(iso); const nHari = Number(akhir.slice(8, 10)); const hariJalan = berjalan ? Math.max(1, Math.min(nHari, Number(iso.slice(8, 10)))) : nHari;
  const per = {}; JENIS_BIAYA.forEach((j) => { per[j.id] = { n: 0, jumlah: 0, catatan: [] }; });
  const rows = B.filter((x) => x.bulan === key); const gaji = rows.filter((x) => String(x.pos || '').indexOf('gaji:') === 0); const tetapRows = rows.filter((x) => KB_POS_TETAP.indexOf(x.pos) >= 0);
  const kotor = (x) => (x.nominalKotor === undefined ? x.nominal : x.nominalKotor);
  per.upah.n = gaji.reduce((a, x) => a + kotor(x), 0); per.upah.jumlah = gaji.length; per.upah.catatan = gaji.map((x) => ({ nama: x.labelLaba || x.label, n: kotor(x), tanggal: x.tanggal || '', dari: 'gaji' }));
  per.tetap.n = L.jatahBulanan - per.upah.n; per.tetap.jumlah = tetapRows.filter((x) => kotor(x) > 0).length;
  const posSemua = KB_POS_TETAP.map((k) => { const r = tetapRows.find((x) => x.pos === k); const p = POS_BIAYA_BULANAN.find((x) => x.kunci === k); return { id: k, nama: p ? p.label : k, n: r ? kotor(r) : 0, tanggal: r ? r.tanggal || '' : '', ada: !!r && kotor(r) > 0 }; });
  per.tetap.catatan = posSemua.filter((p) => p.ada).map((p) => ({ nama: p.nama, n: p.n, tanggal: p.tanggal, dari: 'pos' }));
  const cocokTetap = Math.abs(posSemua.reduce((a, p) => a + p.n, 0) - per.tetap.n) < 0.5;
  let belumDipilah = 0, nBelum = 0; const dariKata = { tanda: 0, untuk: 0, kataOwner: 0, kataBawaan: 0, belum: 0 };
  ambilPengeluaranHarian().forEach((h) => { if (!(h.kategori === 'toko' || h.kategori === 'tokoDompet') || !h.tanggal || h.tanggal < awal || h.tanggal > akhir) return; const n = Number(h.nominal) || 0; const J = jenisCatatan(h, A);
    per[J.id].n += n; per[J.id].jumlah += 1; per[J.id].catatan.push({ id: h.id, nama: String(h.keterangan || '').trim() || '(tanpa keterangan)', n, tanggal: h.tanggal, dari: J.dari, kunci: J.kunci, mdr: J.mdr, dompet: h.kategori === 'tokoDompet' }); dariKata[J.dari] += 1; if (J.dari === 'belum') { belumDipilah += n; nBelum += 1; } });
  const harian = JENIS_BIAYA.filter((j) => j.sifat === 'variabel').reduce((a, j) => a + per[j.id].n, 0); const cocokHarian = Math.abs(harian - L.harianToko) < 0.5;
  const susut = -(L.susutStok || 0); const hapus = L.hapusBuku || 0; const semuaBiaya = L.biayaToko + hapus + susut;
  let kgTerjual = 0, kgHitung = 0, nKg = 0; ambilPenjualan().forEach((p) => { if (!p.tanggal || p.tanggal < awal || p.tanggal > akhir) return; const kg = Number(p.totalKg) || 0; if (kg > 0) { kgTerjual += kg; nKg += 1; if (hppTercatat(p)) kgHitung += kg; } });
  const menutup = Math.abs(L.margin - L.biayaToko - hapus + (L.susutStok || 0) + L.lebihKurangKas + ugEfekAset(L) - L.labaBersih) < 0.5 && Math.abs(per.upah.n + per.tetap.n - L.jatahBulanan) < 0.5 && cocokHarian && cocokTetap;
  const tanpaCatatan = L.jumlahTrx === 0 && L.nHarian === 0 && L.nSusut === 0 && !rows.length;
  return { key, nama: lpNamaBulan(key), pendek: lpBulanPendek(key, true), berjalan, final: lpFinal(key), nHari, hariJalan, L, per, posSemua, susut, hapus, semuaBiaya, biayaToko: L.biayaToko, omzet: L.omzetPenuh, omzetHitung: L.omzetHitung, margin: L.margin, labaBersih: L.labaBersih,
    kgTerjual, kgHitung, nKg, belumDipilah, nBelum, dariKata, menutup, cocokHarian, cocokTetap, tanpaCatatan, cakupan: L.omzetHitung + L.omzetTanpaHpp > 0 ? L.omzetHitung / (L.omzetHitung + L.omzetTanpaHpp) : null, awal, akhir };
}
/** Paket B · inti satu bulan dari potret (tahun yang ditutup): bentuk sama dengan kbInti; rincian per catatan kosong (sudah diarsip) dan `diarsip` menyebutnya. */
function kbDariPotret(key, kini, Pt) {
  const X = Pt.kb; const awal = key + '-01', akhir = akhirBulanIso(key); const per = {};
  JENIS_BIAYA.forEach((j) => { const p = (X.per && X.per[j.id]) || {}; per[j.id] = { n: Number(p.n) || 0, jumlah: Number(p.jumlah) || 0, catatan: [] }; });
  return Object.assign({}, X, { key, nama: lpNamaBulan(key), pendek: lpBulanPendek(key, true), berjalan: key === kbKey(hariIniIso(kini)), final: lpFinal(key), L: Object.assign({ dariIso: awal, sampaiIso: akhir }, Pt.L), per, awal, akhir, diarsip: true });
}
/** Bahan pemicu satu bulan (kedatangan, kantong, hari kerja, uang QRIS, potongan QRIS) dari catatan; bulan yang sudah ditutup memakai potretnya. */
function kbDasarPemicu(X, B) {
  if (X.pemicu) return X.pemicu;
  const Ka = hitungArusKasInti((t) => !!t && t >= X.awal && t <= X.akhir, B);
  return { D: kbKedatangan(X.key), T: kbKantong(X.key), hk: kbHariKerja(X.key), qris: Ka.pos.qris, qrisLain: kbQrisLain(X), mdr: X.per.keuangan.catatan.filter((c) => c.mdr).reduce((a, c) => a + c.n, 0) };
}
/** Paket B · POTRET kendali biaya satu bulan untuk berita acara tutup buku: kbInti (jumlah per jenis, tanpa rincian per catatan) + bahan pemicu. L ikut potret bulan. */
export function kendaliPotret(key, kini, bayaran) {
  const B = bayaran || ugBayaran(); const X = kbInti(key, kini, B, aturKendali()); const per = {}; JENIS_BIAYA.forEach((j) => { per[j.id] = { n: X.per[j.id].n, jumlah: X.per[j.id].jumlah }; });
  const out = {}; Object.keys(X).forEach((k) => { if (['key', 'nama', 'pendek', 'berjalan', 'final', 'L', 'per', 'awal', 'akhir'].indexOf(k) < 0) out[k] = X[k]; });
  return Object.assign(out, { per, pemicu: kbDasarPemicu(X, B) });
}
/** paket HPP & harga minimum (owner 26 Nov 2026, A97): biaya toko & kg terjual satu bulan — angka yang SAMA dengan pemicu "Biaya toko per kg terjual"
 *  (biaya toko mesin = harian + jatah bulanan; kg = semua nota ber-kg). Tanpa hapus buku & susut: susut dihitung terpisah lewat target susut. */
export function kbBiayaKgBulan(key, kini, bayaran) { const X = kbInti(key, kini, bayaran || ugBayaran(), aturKendali()); return { key, nama: X.nama, biayaToko: X.biayaToko, kgTerjual: X.kgTerjual, tanpaCatatan: !!X.tanpaCatatan, diarsip: !!X.diarsip }; }
/** Upah bulan `key` yang BELUM DIBAYAR sampai hari ini (dari absen, upah-logika: hari sejak terakhir dibayar) — [PERKIRAAN] bukan angka mesin laba. */
export function upahMenggantung(key, kini) {
  const iso = hariIniIso(kini); const awal = key + '-01', akhir = akhirBulanIso(key); const batas = akhir < iso ? akhir : iso; const orang = []; let total = 0, nHari = 0;
  let semua = []; try { semua = semuaUpah(kini); } catch (e) { semua = []; }
  semua.forEach((u) => { let rp = 0, h = 0; (u.hariList || []).forEach((d) => { if (d.iso >= awal && d.iso <= batas && (d.nilai === 1 || d.nilai === 0.5)) { rp += d.rp || 0; h += d.nilai; } }); if (rp > 0) { orang.push({ nama: u.nama, rp, hari: h }); total += rp; nHari += h; } });
  return { total, nHari, orang, teks: total > 0 ? 'upah ' + DESIMAL(nHari) + ' hari kerja (' + orang.map((o) => o.nama).join(', ') + ') belum dibayar — belum masuk biaya bulan ini' : '' };
}

// ---------- satu bulan lengkap: baris per jenis + anggaran + lampu + perkiraan + acuan ----------
/** Kendali biaya satu bulan. `kini` = jam layar. Acuan = median ≤ 3 bulan sebelumnya yang punya catatan (TERUKUR, bukan angka ideal). */
export function kendaliBulan(key, kini, bayaran) {
  // P2 (owner 27 Nov 2026): anggaran umum ditimpa ANGKA KHUSUS bulan itu bila owner mengisinya (aturanToko/anggaranBulan.perBulan) — kata kunci & ambang tetap umum
  const B = bayaran || ugBayaran(); const A = aturKendaliBulan(key); const K = kbInti(key, kini, B, A); const KL = kbInti(kbGeser(key, -1), kini, B, A);
  const sebelum = daftarBulan(kini, 36).map((b) => b.key).filter((k) => k < key).slice(0, 3).map((k) => (k === KL.key ? KL : kbInti(k, kini, B, A))).filter((x) => !x.tanpaCatatan);
  const U = upahMenggantung(key, kini), UL = upahMenggantung(KL.key, kini);   // bulan lampau yang upahnya belum dibayar TETAP terlihat (hariList upah-logika membentang sejak terakhir dibayar)
  const nilaiJenis = (X, id) => (id === 'susut' ? X.susut : id === 'hapus' ? X.hapus : X.per[id].n);
  const baris = JENIS_BIAYA.map((j) => ({ id: j.id, nama: j.nama, sifat: j.sifat, ket: j.ket, n: K.per[j.id].n, jumlah: K.per[j.id].jumlah, catatan: K.per[j.id].catatan }))
    .concat(JENIS_BAWAH.map((j) => ({ id: j.id, nama: j.nama, sifat: j.sifat, ket: j.ket, n: nilaiJenis(K, j.id), jumlah: j.id === 'susut' ? K.L.nSusut : K.L.nHapus, catatan: [] })));
  baris.forEach((r) => {
    r.nLalu = nilaiJenis(KL, r.id); r.pctOmzet = kbPct(r.n, K.omzet); r.perKg = K.kgTerjual > 0 ? Math.round(r.n / K.kgTerjual) : null;
    const acuanArr = sebelum.map((x) => nilaiJenis(x, r.id)).filter((n) => n > 0); r.acuan = acuanArr.length ? kbMedian(acuanArr) : null; r.acuanTeks = acuanArr.length ? (acuanArr.length === 1 ? 'bulan lalu' : 'median ' + acuanArr.length + ' bulan lalu') + ' (terukur)' : 'belum ada bulan sebelumnya';
    r.proyeksi = K.berjalan && r.sifat === 'variabel' && K.hariJalan > 0 ? Math.round(r.n / K.hariJalan * K.nHari) : null;
    r.menggantung = r.id === 'upah' ? U.total : 0; r.pakai = r.n + r.menggantung;   // yang dibandingkan
    r.anggaran = ID_ANGGARAN.indexOf(r.id) >= 0 ? A.anggaran[r.id] : 0;
    if (!(r.anggaran > 0)) { r.lampu = 'tanpa'; r.dasar = null; r.selisih = null; r.selisihPct = null; r.lampuTeks = ID_ANGGARAN.indexOf(r.id) >= 0 ? 'anggaran belum diatur' : 'tidak dianggarkan'; }
    else { r.dasar = K.berjalan && r.sifat === 'variabel' ? Math.round(r.anggaran * K.hariJalan / K.nHari) : r.anggaran; r.selisih = r.pakai - r.dasar; r.selisihPct = kbPct(r.selisih, r.dasar);
      r.lampu = r.selisih <= 0 ? 'hijau' : r.selisihPct <= A.ambang ? 'amber' : 'merah';
      r.lampuTeks = (K.berjalan && r.sifat === 'variabel' ? 'jatah sampai hari ke-' + K.hariJalan + ' ' + RP(r.dasar) : 'anggaran ' + RP(r.anggaran)) + ' · ' + (r.selisih <= 0 ? 'sisa ' + RP(-r.selisih) : 'LEWAT ' + RP(r.selisih) + ' (' + kbPctTeks(r.selisihPct) + ')'); }
    r.khusus = !!(A.khusus && A.khusus[r.id]); if (r.khusus) r.lampuTeks += ' · angka khusus ' + K.nama;
    r.belumTercatat = r.id === 'tetap' && K.berjalan ? K.posSemua.filter((p) => !(p.n > 0)).length : 0; if (r.belumTercatat) r.lampuTeks += ' · ' + r.belumTercatat + ' pos belum dicatat bulan ini';
    const banding = r.proyeksi !== null ? r.proyeksi : r.pakai; r.delta = r.nLalu > 0 ? kbPct(banding - r.nLalu, r.nLalu) : null; r.deltaDari = r.proyeksi !== null ? 'perkiraan' : 'aktual';
    if (r.id === 'angkut') { const O = ajOngkirRentang(key + '-01', akhirBulanIso(key)); r.ongkirMasuk = O.rp; r.nAntar = O.nNota;
      if (O.rp) r.lampuTeks += ' · ongkir antar ditagih ' + RP(O.rp) + ' (' + O.nNota + ' nota; masuk omzet nota, bukan pengurang biaya ini)'; }
  });
  const merah = baris.filter((r) => r.lampu === 'merah').length, amber = baris.filter((r) => r.lampu === 'amber').length, hijau = baris.filter((r) => r.lampu === 'hijau').length;
  const terjun = [{ nama: 'Margin kotor', n: K.margin, kelas: 'jumlah', ket: 'omzet ber-HPP − HPP (mesin laba)' }]
    .concat(JENIS_BIAYA.map((j) => ({ nama: j.nama, n: -K.per[j.id].n, ket: K.per[j.id].jumlah + ' catatan' })))
    .concat([{ nama: 'Hapus buku piutang', n: -K.hapus, ket: K.L.nHapus + ' catatan' }, { nama: 'Susut & selisih stok', n: -K.susut, ket: K.L.nSusut + ' baris' }]).concat(K.L.lebihKurangKas ? [{ nama: 'Lebih/kurang kas', n: K.L.lebihKurangKas, ket: 'selisih laci tutup hari · ' + K.L.nLebihKurang + ' malam' }] : []).concat(K.L.asetDariBiaya ? [{ nama: 'Uang keluar dipindah jadi aset tetap', n: K.L.asetDariBiaya, ket: K.L.nAsetDariBiaya + ' catatan · sudah ada di jenis biayanya, dikeluarkan dari laba' }] : []).concat(K.L.penyusutan ? [{ nama: 'Penyusutan aset tetap', n: -K.L.penyusutan, ket: 'garis lurus, dibagi rata per hari' }] : []).concat([{ nama: 'Laba bersih', n: K.labaBersih, kelas: 'jumlah', ket: 'mesin yang sama dengan Laba' }]);
  return Object.assign(K, { A, KL, U, UL, baris, terjun, merah, amber, hijau, nLampu: merah + amber + hijau, sebelum: sebelum.map((x) => x.key), pctBiaya: kbPct(K.semuaBiaya, K.omzet), pctBiayaToko: kbPct(K.biayaToko, K.omzet), biayaPerKg: K.kgTerjual > 0 ? Math.round(K.semuaBiaya / K.kgTerjual) : null,
    pct: (a) => kbPctTeks(kbPct(a, K.omzet)) });
}
/** Formulir anggaran diisi dari acuan terukur tiap jenis — mengisi DRAF, bukan menyimpan (yang menjadi anggaran = yang owner simpan). */
export function drafDariAcuan(K, draf) { const d = Object.assign({}, draf || {}); const ang = Object.assign({}, d.anggaran || {}); let n = 0; K.baris.forEach((r) => { if (ID_ANGGARAN.indexOf(r.id) >= 0 && r.acuan > 0) { ang[r.id] = String(Math.round(r.acuan / 1000) * 1000); n += 1; } }); d.anggaran = ang; return { draf: d, n }; }

// ---------- titik impas ----------
/** Omzet yang harus dicapai supaya margin kotor menutup biaya di bawahnya: biaya ÷ rasio margin (margin ÷ omzet ber-HPP). Bulan berjalan: juga "sampai hari ini" dari mesin (awal bulan → hari ini). */
export function titikImpas(K, kini, bayaran) {
  // aset tetap (owner 26 Nov 2026): penyusutan ikut biaya di bawah margin; uang keluar yang dipindah jadi aset bukan biaya lagi (0 tanpa aset)
  const rasio = K.omzetHitung > 0 ? K.margin / K.omzetHitung : null; const biaya = K.semuaBiaya - ugEfekAset(K.L); const omzetImpas = rasio > 0 ? Math.round(biaya / rasio) : null;
  // Paket B: bulan yang sudah ditutup buku (catatannya diarsip) = laba sebulan penuh dari potret, bentuk sama dengan ugLabaBersih
  const iso = hariIniIso(kini); const sampai = K.berjalan ? (iso < K.akhir ? iso : K.akhir) : K.akhir; const Lj = K.diarsip && !K.berjalan ? K.L : ugLabaBersih(K.awal, sampai, bayaran || ugBayaran());
  // 39b no. 38: impas = margin kotor menutup biaya — lebih/kurang kas bukan biaya, jadi dihitung dari laba mesin; laba bersih yang DISEBUT = laba bersih toko
  const labaImpas = Lj.labaMesin + ugEfekAset(Lj); const menutupKini = labaImpas >= 0; const kurang = menutupKini ? 0 : -labaImpas; const omzetKurang = kurang > 0 && rasio > 0 ? Math.round(kurang / rasio) : 0;
  const hariSisa = K.berjalan ? K.nHari - K.hariJalan : 0;
  const teks = rasio === null ? 'Belum ada omzet ber-HPP bulan ini — rasio margin tidak bisa dihitung.' : rasio <= 0 ? 'Margin kotor bulan ini nol atau minus — berapa pun omzetnya biaya tidak tertutup; bahasannya harga jual, bukan jatah.'
    : 'Dari tiap Rp1.000.000 omzet tersisa ' + RP(Math.round(rasio * 1000000)) + ' sebelum biaya. Biaya di bawah margin ' + RP(biaya) + ' → butuh omzet ' + RP(omzetImpas) + ' sebulan (' + RP(Math.round(omzetImpas / K.nHari)) + ' per hari).';
  return { rasio, rasioTeks: rasio === null ? '—' : kbPctTeks(rasio * 100), biaya, omzetImpas, omzetImpasHari: omzetImpas !== null ? Math.round(omzetImpas / K.nHari) : null, omzetHari: K.hariJalan > 0 ? Math.round(K.omzetHitung / K.hariJalan) : 0,
    sampai, menutupKini, kurang, omzetKurang, hariSisa, labaSampai: Lj.labaBersih, marginSampai: Lj.margin, biayaSampai: Lj.biayaToko + (Lj.hapusBuku || 0) - (Lj.susutStok || 0) - ugEfekAset(Lj), teks,
    kiniTeks: K.berjalan ? (menutupKini ? 'Sampai ' + tanggalPendek(sampai) + ' margin kotor ' + RP(Lj.margin) + ' sudah menutup biaya sampai hari itu — laba bersih ' + RP(Lj.labaBersih) + '.' : 'Sampai ' + tanggalPendek(sampai) + ' biaya masih lebih besar ' + RP(kurang) + ' dari margin kotor' + (omzetKurang ? ' — kira-kira butuh omzet tambahan ' + RP(omzetKurang) + (hariSisa ? ' dalam ' + hariSisa + ' hari tersisa' : '') : '') + '.')
      : (menutupKini ? 'Bulan ini menutup: laba bersih ' + RP(Lj.labaBersih) + '.' : 'Bulan ini TIDAK menutup: biaya lebih besar ' + RP(kurang) + ' dari margin kotor.'),
    catatan: [K.cakupan !== null && K.cakupan < 0.999 ? 'Rasio margin dari omzet ber-HPP saja (' + kbPctTeks(K.cakupan * 100) + ' omzet) — ' + K.L.jumlahTanpaHpp + ' baris tanpa modal belum ikut.' : '', K.U && K.U.total > 0 ? 'Belum termasuk ' + K.U.teks + ' (' + RP(K.U.total) + ').' : ''].filter(Boolean) };
}

// ---------- pemicu biaya: biaya per satuan, bulan ini vs bulan lalu ----------
function kbKedatangan(key) { let kg = 0, rp = 0, bongkar = 0, n = 0; ambilSemuaBatch().forEach((b) => { if (b.stokAwal || b.tutupBuku || !b.tanggal || bulanDari(b.tanggal) !== key) return; n += 1; bongkar += Number(b.biayaBongkar) || 0; (b.merkList || []).forEach((m) => { kg += Number(m.totalKg) || 0; rp += Number(m.subtotalHarga) || 0; }); }); return { kg, rp, bongkar, n }; }
function kbKantong(key) { let lembar = 0, rp = 0; ambilBahanKemasan().concat(ambilBahanLiteran()).forEach((x) => { if (x.tipe !== 'beli' || !x.tanggal || bulanDari(x.tanggal) !== key) return; const j = Number(x.jumlah) || 0; if (j > 0) { lembar += j; rp += Number(x.hargaTotal) || 0; } }); return { lembar, rp }; }
/* audit 39b no. 3: dokumen potongan tutup hari (mdr-<tanggal>) memuat potongan SEMUA uang QRIS — penjualan + bayar bon + kasbon kembali — maka
   penyebut rasionya juga semua uang QRIS itu (Ka.pos.qris mesin = penjualan saja). */
const kbQrisLain = (X) => ambilPiutangMutasi().concat(ambilKasbonMutasi()).filter((m) => m && m.tipe === 'bayar' && (m.tanggal || '') >= X.awal && (m.tanggal || '') <= X.akhir && Number(m.nominal) > 0 && caraBayarKunci(m) === 'qris').reduce((a, m) => a + (Number(m.nominal) || 0), 0);
function kbHariKerja(key) { let h = 0; ambilBiayaBulanan().forEach((b) => { if (b.bulan !== key) return; (b.rincianGaji || []).forEach((r) => { h += Number(r.hari) || 0; }); }); return h; }
export function pemicuBiaya(K, bayaran) {
  const B = bayaran || ugBayaran(); const KL = K.KL; const A = K.A;
  // Paket B: bahan pemicu (kedatangan, kantong, hari kerja, uang & potongan QRIS) lewat kbDasarPemicu — bulan yang sudah ditutup buku membaca potretnya
  const satu = (X, U) => { const Z = kbDasarPemicu(X, B); const D = Z.D; const T = Z.T; const hk = Z.hk + (U ? U.nHari : 0); const upahSemua = X.per.upah.n + (U ? U.total : 0); const mdr = Z.mdr;
    return { biayaKg: X.kgTerjual > 0 ? X.biayaToko / X.kgTerjual : null, hppKg: X.kgHitung > 0 ? X.L.hpp / X.kgHitung : null, jualKg: X.kgHitung > 0 ? X.omzetHitung / X.kgHitung : null, marginKg: X.kgHitung > 0 ? X.margin / X.kgHitung : null,
      bongkarKg: D.kg > 0 ? D.bongkar / D.kg : null, beliKg: D.kg > 0 ? D.rp / D.kg : null, mdrQris: Z.qris + Z.qrisLain > 0 ? mdr / (Z.qris + Z.qrisLain) * 100 : null, karyawanHari: hk > 0 ? (upahSemua + X.per.karyawan.n) / hk : null, kantongLembar: T.lembar > 0 ? T.rp / T.lembar : null, susutKg: X.kgTerjual > 0 ? X.susut / X.kgTerjual : null, D, T, hk, qris: Z.qris }; };
  const N = satu(K, K.U), NL = satu(KL, K.UL);
  const DAFTAR = [['biayaKg', 'Biaya toko per kg terjual', 'Rp/kg', 'biaya toko mesin ÷ kg semua nota ber-kg'], ['hppKg', 'HPP per kg terjual', 'Rp/kg', 'HPP mesin ÷ kg nota ber-HPP'], ['jualKg', 'Harga jual per kg', 'Rp/kg', 'omzet ber-HPP ÷ kg nota ber-HPP'], ['marginKg', 'Margin kotor per kg', 'Rp/kg', 'harga jual − HPP per kg'],
    ['beliKg', 'Harga beli per kg (kedatangan)', 'Rp/kg', 'Σ harga beras ÷ Σ kg kedatangan bulan itu'], ['bongkarKg', 'Bongkar per kg kedatangan', 'Rp/kg', 'Σ bongkar ÷ Σ kg kedatangan (tertanam di HPP)'], ['mdrQris', 'Potongan QRIS dari uang QRIS', '%', 'catatan bertanda MDR ÷ semua uang QRIS (penjualan + bayar bon + kasbon kembali)'],
    ['karyawanHari', 'Biaya karyawan per hari kerja', 'Rp/hari', '(upah kotor dibayar + belum dibayar + di luar upah) ÷ (hari kerja rincian gaji + hari belum dibayar)'], ['kantongLembar', 'Harga kantong per lembar', 'Rp/lembar', 'Σ harga ÷ Σ lembar beli kantong bulan itu'], ['susutKg', 'Susut per kg terjual', 'Rp/kg', 'susut & selisih ÷ kg terjual']];
  const baris = DAFTAR.map(([id, nama, satuan, sumber]) => { const n = N[id], l = NL[id]; const delta = n !== null && l !== null && l > 0 ? kbPct(n - l, l) : null; const naikBiaya = id !== 'jualKg' && id !== 'marginKg'; const turunBuruk = id === 'jualKg' || id === 'marginKg';
    return { id, nama, satuan, sumber, n: n === null ? null : Math.round(n * 10) / 10, nLalu: l === null ? null : Math.round(l * 10) / 10, delta, naik: delta !== null && ((naikBiaya && delta > A.ambangPemicu) || (turunBuruk && delta < -A.ambangPemicu)), teks: n === null ? 'belum bisa dihitung' : (satuan === '%' ? kbPctTeks(n) : RP(Math.round(n)) + (satuan === 'Rp/kg' ? '/kg' : satuan === 'Rp/hari' ? '/hari' : '/lembar')),
      teksLalu: l === null ? '—' : (satuan === '%' ? kbPctTeks(l) : RP(Math.round(l))), deltaTeks: delta === null ? (l === null ? 'bulan lalu belum ada' : '—') : (delta >= 0 ? '▲ ' : '▼ ') + kbPctTeks(Math.abs(delta)) + ' vs ' + KL.pendek }; });
  return { baris, naik: baris.filter((r) => r.naik), ambang: A.ambangPemicu, ini: { kedatangan: N.D, kantong: N.T, hariKerja: N.hk, qris: N.qris }, lalu: { kedatangan: NL.D, kantong: NL.T, hariKerja: NL.hk, qris: NL.qris }, keyLalu: KL.key, pendekLalu: KL.pendek };
}

// ---------- pareto: catatan terbesar yang membentuk 80 % biaya ----------
export function paretoBiaya(K, batasPct) {
  const batas = batasPct || 80; const peta = {};
  K.baris.forEach((r) => { if (r.id === 'susut' || r.id === 'hapus') { if (r.n > 0) peta[r.id] = { nama: r.nama, jenis: r.id, n: r.n, jumlah: r.jumlah }; return; }
    r.catatan.forEach((c) => { const kunci = c.kunci || kbPolos(c.nama); const k = r.id + '|' + kunci; if (!peta[k]) peta[k] = { nama: c.nama.length > 44 ? c.nama.slice(0, 43) + '…' : c.nama, jenis: r.id, n: 0, jumlah: 0, kunci }; peta[k].n += c.n; peta[k].jumlah += 1; }); });
  const semua = Object.keys(peta).map((k) => peta[k]).filter((x) => x.n > 0).sort((a, b) => b.n - a.n); const total = semua.reduce((a, x) => a + x.n, 0); let kum = 0;
  const daftar = semua.map((x) => { kum += x.n; const pct = kbPct(x.n, total); const kumPct = kbPct(kum, total); return Object.assign(x, { pct, kumPct, inti: kum - x.n < total * batas / 100, jenisNama: (JENIS_BIAYA.concat(JENIS_BAWAH).find((j) => j.id === x.jenis) || {}).nama || x.jenis }); });
  const inti = daftar.filter((x) => x.inti);
  // Paket B: bulan yang sudah ditutup buku — rincian per catatan ikut arsip, jadi pareto hanya dari baris susut/hapus buku; kalimatnya menyebut itu, bukan "belum ada biaya"
  const arsip = K.diarsip ? 'Rincian per catatan ' + K.nama + ' sudah diarsip (tutup buku) — jumlah per jenis di atas dari potret saat tahun dikunci.' : '';
  return { daftar, inti, total, batas, nInti: inti.length, nSemua: daftar.length, diarsip: !!K.diarsip, teks: arsip || (daftar.length ? inti.length + ' dari ' + daftar.length + ' pos membentuk ' + kbPctTeks(inti.length ? inti[inti.length - 1].kumPct : 0) + ' biaya (' + RP(total) + ')' : 'Belum ada biaya tercatat.') };
}

// ---------- peringatan: yang bengkak, hilang, atau belum lengkap — tiap baris menunjuk pintunya ----------
export function peringatanBiaya(K, P, T) {
  const out = []; const awas = (id, teks, tujuan, tingkat) => out.push({ id, teks, tujuan: tujuan || null, tingkat: tingkat || 'awas' }); const KL = K.KL;
  K.baris.forEach((r) => { if (r.lampu === 'merah' || r.lampu === 'amber') awas('lampu-' + r.id, r.nama + ' ' + (r.lampu === 'merah' ? 'LEWAT' : 'mendekati batas') + ' — ' + r.lampuTeks + (r.proyeksi !== null ? ' · perkiraan sebulan ' + RP(r.proyeksi) : ''), { ke: 'uang', keluarga: r.id === 'upah' ? 'upah' : 'keluar' }, r.lampu === 'merah' ? 'awas' : 'info'); });
  if (K.berjalan) K.posSemua.forEach((p) => { const lalu = KL.posSemua.find((x) => x.id === p.id); if (!(p.n > 0) && lalu && lalu.n > 0) awas('pos-' + p.id, p.nama + ' belum dicatat bulan ini (bulan lalu ' + RP(lalu.n) + ') — biaya bulan ini masih terlihat terlalu ringan', { ke: 'uang', keluarga: 'keluar', tab: 'tagihan' }, 'info'); });
  if (K.U && K.U.total > 0) awas('upah-gantung', 'Upah ' + RP(K.U.total) + ' (' + K.U.teks + ')', { ke: 'uang', keluarga: 'upah' }, 'info');
  if (K.susut > 0 && (K.margin > 0 ? K.susut / K.margin >= 0.2 : true) && !(K.baris.find((r) => r.id === 'susut').anggaran > 0)) awas('susut', 'Susut & selisih stok ' + RP(K.susut) + (K.margin > 0 ? ' = ' + kbPctTeks(kbPct(K.susut, K.margin)) + ' margin kotor bulan ini' : '') + ' — biaya terbesar yang tidak keluar dari laci; cari sebabnya di Cocokkan', { ke: 'stok', lembar: 'cocok' });
  if (K.nBelum > 0 && K.L.harianToko > 0 && K.belumDipilah / K.L.harianToko > 0.25) awas('belum-dipilah', K.nBelum + ' catatan uang keluar (' + RP(K.belumDipilah) + ', ' + kbPctTeks(kbPct(K.belumDipilah, K.L.harianToko)) + ' biaya harian) jenisnya belum dikenali — beri kata kunci di Atur supaya jenisnya kelihatan', null, 'info');
  if (K.cakupan !== null && K.cakupan < 0.95) awas('cakupan', kbPctTeks((1 - K.cakupan) * 100) + ' omzet (' + K.L.jumlahTanpaHpp + ' baris) tanpa modal — margin & titik impas bulan ini belum utuh; rinci karcis kasir dulu', { ke: 'jual' }, 'info');
  if (P) P.naik.forEach((r) => awas('pemicu-' + r.id, r.nama + ' ' + r.deltaTeks + ' (' + r.teksLalu + ' → ' + r.teks + ')', r.id === 'bongkarKg' || r.id === 'beliKg' ? { ke: 'stok', lembar: 'hpp' } : r.id === 'kantongLembar' ? { ke: 'stok', lembar: 'kantong' } : r.id === 'jualKg' || r.id === 'marginKg' || r.id === 'hppKg' ? { ke: 'harga', keluarga: 'katalog' } : { ke: 'uang', keluarga: 'keluar' }, 'info'));
  if (T && !T.menutupKini && T.rasio !== null) awas('impas', T.kiniTeks, { ke: 'laporan', keluarga: 'laba' });
  if (!K.menutup && !K.tanpaCatatan) awas('tidak-menutup', 'Pemilahan TIDAK MENUTUP ke mesin laba — jangan dipakai memutuskan; laporkan', null);
  const urut = { awas: 0, info: 1 }; return out.sort((a, b) => urut[a.tingkat] - urut[b.tingkat]);
}

// ---------- tren beberapa bulan ----------
export function trenBiaya(kini, n, bayaran) {
  const B = bayaran || ugBayaran(); const A = aturKendali(); const akhir = kbKey(hariIniIso(kini)); const out = []; const ab = lpAwalBuku();
  for (let i = (n || 6) - 1; i >= 0; i--) { const k = kbGeser(akhir, -i); const X = kbInti(k, kini, B, A); out.push({ key: k, pendek: lpBulanPendek(k, k.slice(5, 7) === '01' || i === (n || 6) - 1), berjalan: X.berjalan, final: X.final, tanpaCatatan: X.tanpaCatatan, omzet: X.omzet, margin: X.margin, biayaToko: X.biayaToko, susut: X.susut, hapus: X.hapus, semuaBiaya: X.semuaBiaya, labaBersih: X.labaBersih, pctBiaya: kbPct(X.semuaBiaya, X.omzet), perJenis: JENIS_BIAYA.map((j) => ({ id: j.id, n: X.per[j.id].n })), sebelumBuku: k < ab }); }
  const maks = Math.max(1, ...out.map((b) => Math.max(b.semuaBiaya, b.margin)));
  // 39b no. 40: bulan sebelum awal buku tetap digambar (biayanya kelihatan), dengan keterangan — bukan bulan rugi
  const pra = out.filter((b) => b.sebelumBuku && !b.tanpaCatatan); const sebelumBuku = pra.length ? lpKetSebelumBuku(lpBulanPendek(pra[0].key, true) + (pra.length > 1 ? ' – ' + lpBulanPendek(pra[pra.length - 1].key, true) : ''), pra.reduce((a, b) => a + b.labaBersih, 0)) : '';
  return { daftar: out, maks, ada: out.some((b) => !b.tanpaCatatan), sebelumBuku };
}

// ---------- belum dipilah: daftar keterangan yang bisa diberi kata kunci ----------
export function belumDipilah(K, maks) {
  const peta = {}; K.per.lain.catatan.forEach((c) => { if (c.dari !== 'belum') return; const k = kbPolos(c.nama); if (!k) return; if (!peta[k]) peta[k] = { kata: k, nama: c.nama, n: 0, jumlah: 0 }; peta[k].n += c.n; peta[k].jumlah += 1; });
  return Object.keys(peta).map((k) => peta[k]).sort((a, b) => b.n - a.n).slice(0, maks || 12);
}

// ---------- atur: anggaran, ambang, kata kunci — satu dokumen aturanToko/kendaliBiaya ----------
export function drafAtur() { const A = aturKendali(); const anggaran = {}; KB_ID_SIMPAN.forEach((id) => { anggaran[id] = A.anggaran[id] ? String(A.anggaran[id]) : ''; }); const kata = {}; JENIS_BIAYA.forEach((j) => { kata[j.id] = (A.kata[j.id] || []).join(', '); }); return { anggaran, ambang: String(A.ambang), ambangPemicu: String(A.ambangPemicu), kata }; }
const kbPecahKata = (teks) => { const out = []; String(teks || '').split(/[,;\n]/).forEach((x) => { const k = kbPolos(x); if (k && out.indexOf(k) < 0) out.push(k); }); return out; };
export function susunAturKendali(isi, w) {
  const anggaran = {}; for (const id of KB_ID_SIMPAN) { const v = isi.anggaran ? isi.anggaran[id] : ''; const n = ugKosong(v) ? 0 : ugAngka(v); if (n < 0) return { tolak: 'Anggaran ' + id + ' tidak boleh minus' }; if (n > 1000000000) return { tolak: 'Anggaran ' + id + ' terlalu besar (maksimal Rp1.000.000.000 sebulan)' }; anggaran[id] = Math.round(n); }
  const ambang = ugKosong(isi.ambang) ? ATUR_KENDALI_BAWAAN.ambang : Number(String(isi.ambang).replace(',', '.')); if (!(isFinite(ambang) && ambang >= 0 && ambang <= 100)) return { tolak: 'Ambang lampu ditulis dalam persen 0–100 (10 = amber sampai 10 % di atas anggaran)' };
  const ambangPemicu = ugKosong(isi.ambangPemicu) ? ATUR_KENDALI_BAWAAN.ambangPemicu : Number(String(isi.ambangPemicu).replace(',', '.')); if (!(isFinite(ambangPemicu) && ambangPemicu >= 0 && ambangPemicu <= 100)) return { tolak: 'Ambang pemicu ditulis dalam persen 0–100' };
  const kata = {}; const punya = {}; let nKata = 0;
  for (const j of JENIS_BIAYA) { if (j.id === 'upah' || j.id === 'tetap' || j.id === 'lain') continue; const d = kbPecahKata(isi.kata ? isi.kata[j.id] : ''); for (const k of d) { if (k.length > 40) return { tolak: 'Kata kunci "' + k.slice(0, 20) + '…" terlalu panjang (maksimal 40 huruf)' }; if (punya[k] && punya[k] !== j.id) return { tolak: '"' + k + '" ada di ' + punya[k] + ' DAN ' + j.id + ' — satu kata satu jenis' }; punya[k] = j.id; } if (d.length > 40) return { tolak: 'Kata kunci ' + j.nama + ' lebih dari 40 — ringkas dulu' }; kata[j.id] = d; nKata += d.length; }
  const nAnggaran = ID_ANGGARAN.filter((id) => anggaran[id] > 0).length;
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'kendaliBiaya', tanggal: w.tanggal, jam: w.jam, anggaran, ambang: Math.round(ambang * 10) / 10, ambangPemicu: Math.round(ambangPemicu * 10) / 10, kata } }],
    patch: { aturB: null, kabar: 'Aturan kendali biaya disimpan — ' + nAnggaran + ' anggaran diisi' + (anggaran.pph > 0 ? ' · PPh final ' + RP(anggaran.pph) + ' sebulan' : '') + ' · ambang lampu ' + kbPctTeks(ambang) + ' · ambang pemicu ' + kbPctTeks(ambangPemicu) + ' · ' + nKata + ' kata kunci owner', kabarAwas: false } };
}
/** Satu keterangan "belum dipilah" diberi jenis = keterangannya (dipolos) ditambahkan ke kata kunci owner jenis itu; semua catatan seketerangan ikut berpindah (sekarang & seterusnya). */
export function susunTambahKata(jenis, teks, w) {
  const j = JENIS_BIAYA.find((x) => x.id === jenis && x.id !== 'upah' && x.id !== 'tetap' && x.id !== 'lain'); if (!j) return { tolak: 'Jenis tidak dikenal' };
  const k = kbPolos(teks).slice(0, 40); if (!k) return { tolak: 'Keterangan kosong — tidak ada kata yang bisa dijadikan kunci' };
  const A = aturKendali(); for (const x of JENIS_BIAYA) { if ((A.kata[x.id] || []).indexOf(k) >= 0) return x.id === jenis ? { tolak: '"' + k + '" sudah jadi kata kunci ' + j.nama } : { tolak: '"' + k + '" sudah dipakai ' + x.nama + ' — satu kata satu jenis' }; }
  const kata = {}; JENIS_BIAYA.forEach((x) => { kata[x.id] = (A.kata[x.id] || []).slice(); }); kata[jenis].push(k);
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'kendaliBiaya', tanggal: w.tanggal, jam: w.jam, anggaran: A.anggaran, ambang: A.ambang, ambangPemicu: A.ambangPemicu, kata } }], patch: { pilahK: null, kabar: '"' + k + '" → ' + j.nama + ' — berlaku untuk semua catatan yang keterangannya diawali kata itu', kabarAwas: false } };
}

// ==================== P2 (owner 27 Nov 2026) · TARGET BULANAN, ANGKA KHUSUS PER BULAN, SEBAB & TINDAKAN PER POS ====================
// Keputusan owner 27 Nov 2026: semua pos target dipakai (kg terjual & laba kotor · HPP/kg & margin kotor % · piutang akhir bulan · karcis belum dirinci) + usulan
// yang masuk akal (omzet, laba bersih, potongan & tawar %); anggaran SAMA tiap bulan, boleh diberi ANGKA KHUSUS per bulan. Semua angka = setelan owner; BAWAAN =
// belum diatur (lampu mati) — tombol "isi dari acuan" hanya mengisi formulir. Dokumen: aturanToko/anggaranBulan (target umum + angka khusus per bulan, juga untuk
// anggaran biaya per jenis & PPh) dan aturanToko/anggaranCatatan (sebab & tindakan per pos per bulan). Owner saja, tanpa rules baru; mesin uang tidak disentuh.
export const AB_ID = 'anggaranBulan';
export const AB_CATATAN_ID = 'anggaranCatatan';
/** Pos target. arah: 'min' = makin besar makin baik (target) · 'maks' = batas paling banyak. jalan = bulan berjalan dibanding jatah sampai hari ke-N. */
export const AB_TARGET = [
  { id: 'omzet', pendek: 'rupiah sebulan · sesudah potongan & retur', nama: 'Omzet (penjualan bersih)', arah: 'min', satuan: 'rp', jalan: true, ket: 'omzet mesin sesudah potongan & retur · bulan berjalan dibanding jatah sampai hari ke-N' },
  { id: 'kgTerjual', pendek: 'kg sebulan', nama: 'Kg terjual', arah: 'min', satuan: 'kg', jalan: true, ket: 'kg semua nota ber-kg · bulan berjalan dibanding jatah sampai hari ke-N' },
  { id: 'labaKotor', pendek: 'rupiah sebulan · Dasbor: ÷ jumlah hari = target harian', nama: 'Laba kotor', arah: 'min', satuan: 'rp', jalan: true, ket: 'omzet ber-HPP − HPP (mesin laba) · bulan berjalan dibanding jatah sampai hari ke-N · Dasbor: target per hari = sebulan ÷ jumlah hari' },
  { id: 'marginKotor', pendek: 'persen · laba kotor ÷ omzet ber-HPP', nama: 'Margin laba kotor', arah: 'min', satuan: 'pct', jalan: false, ket: 'laba kotor ÷ omzet ber-HPP (penyebut yang sama dengan Laporan › Laba)' },
  { id: 'labaBersih', pendek: 'rupiah sebulan', nama: 'Laba bersih', arah: 'min', satuan: 'rp', jalan: true, ket: 'mesin laba · bulan berjalan: laba bersih sampai hari ini dibanding jatah sampai hari ke-N' },
  { id: 'hppKg', pendek: 'rupiah per kg', nama: 'HPP rata-rata per kg', arah: 'maks', satuan: 'rpkg', jalan: false, ket: 'HPP mesin ÷ kg nota ber-HPP (= pemicu "HPP per kg terjual")' },
  { id: 'piutangAkhir', pendek: 'rupiah · sisa bon di akhir bulan', nama: 'Piutang akhir bulan', arah: 'maks', satuan: 'rp', jalan: false, ket: 'sisa bon pelanggan akhir bulan (bulan berjalan: hari ini) — mesin yang sama dengan neraca' },
  { id: 'potonganPct', pendek: 'persen dari penjualan kotor', nama: 'Potongan & tawar', arah: 'maks', satuan: 'pct', jalan: false, ket: 'potongan nota + tawar di bawah harga daftar ÷ penjualan kotor (Laporan › Pajak)' },
  { id: 'karcisBelum', pendek: 'jumlah karcis · posisi sekarang', nama: 'Karcis kasir belum dirinci', arah: 'maks', satuan: 'n', jalan: false, ket: 'jumlah karcis kasir yang menunggu dirinci — posisi sekarang (Jual › Karcis kasir)' },
];
/** Penjaga salah ketik (bukan kebijakan). */
export const AB_MAKS = { rp: 10000000000, kg: 10000000, rpkg: 1000000, pct: 100, n: 10000 };
export const AB_BULAN_MAKS = 24;   // angka khusus & catatan disimpan paling banyak 24 bulan terbaru (dokumen tidak membengkak)
export const AB_CATATAN_MAKS = 200;   // huruf per sebab / tindakan
/** Pos yang boleh diberi sebab & tindakan: jenis biaya, hapus buku, susut, PPh, pos target, susut %. */
export const AB_POS_CATATAN = JENIS_BIAYA.map((j) => j.id).concat(JENIS_BAWAH.map((j) => j.id), [ID_ANGGARAN_PAJAK], AB_TARGET.map((t) => t.id), ['susutPct', 'hariStok']);
const abBulanSah = (k) => /^\d{4}-(0[1-9]|1[0-2])$/.test(String(k || ''));
const abBulat = (n, satuan) => (satuan === 'pct' ? Math.round(n * 100) / 100 : satuan === 'kg' ? Math.round(n * 10) / 10 : Math.round(n));
const abSah = (v, satuan) => { const n = Number(v); return isFinite(n) && n > 0 && n <= AB_MAKS[satuan] ? abBulat(n, satuan) : 0; };
/** Angka tersimpan → teks formulir (koma desimal). */
export const abTeks = (n, satuan) => (n === null || n === undefined || n === '' ? '' : satuan === 'pct' || satuan === 'kg' ? String(n).replace('.', ',') : String(Math.round(n)));
const abUrut = (o) => { const out = {}; Object.keys(o || {}).sort().forEach((k) => { out[k] = o[k]; }); return out; };

/** Setelan P2: { target: { id: angka (0 = mati) }, perBulan: { 'YYYY-MM': { anggaran: { id: angka }, target: { id: angka } } } (yang diisi saja; 0 = mati bulan itu), dariOwner, nTarget }. */
export function aturAnggaranBulan() {
  const a = ugAturDok(AB_ID) || {}; const target = {}; AB_TARGET.forEach((t) => { target[t.id] = abSah(a.target && a.target[t.id], t.satuan); });
  const perBulan = {}; const pb = a.perBulan && typeof a.perBulan === 'object' ? a.perBulan : {};
  Object.keys(pb).filter(abBulanSah).sort().forEach((k) => { const x = pb[k] || {}; const ang = {}, tg = {}; const ada = (o, id) => o && o[id] !== undefined && o[id] !== null && o[id] !== '' && isFinite(Number(o[id])) && Number(o[id]) >= 0;
    KB_ID_SIMPAN.forEach((id) => { if (ada(x.anggaran, id)) ang[id] = Math.min(1000000000, Math.round(Number(x.anggaran[id]))); });
    AB_TARGET.forEach((t) => { if (ada(x.target, t.id)) tg[t.id] = Number(x.target[t.id]) > 0 ? abSah(x.target[t.id], t.satuan) : 0; });
    if (Object.keys(ang).length || Object.keys(tg).length) perBulan[k] = { anggaran: ang, target: tg }; });
  return { target, perBulan, dariOwner: !!ugAturDok(AB_ID), nTarget: AB_TARGET.filter((t) => target[t.id] > 0).length, tanggal: a.tanggal || '' };
}
/** Aturan kendali SATU bulan: aturKendali (anggaran umum) yang anggarannya ditimpa angka khusus bulan itu. khusus = { id: true } pos yang ditimpa. */
export function aturKendaliBulan(key) {
  const A = aturKendali(); const P = aturAnggaranBulan().perBulan[String(key)];
  if (!P || !Object.keys(P.anggaran).length) return Object.assign({}, A, { khusus: {} });
  const anggaran = Object.assign({}, A.anggaran); const khusus = {}; Object.keys(P.anggaran).forEach((id) => { anggaran[id] = P.anggaran[id]; khusus[id] = true; });
  return Object.assign({}, A, { anggaran, khusus, nAnggaran: ID_ANGGARAN.filter((id) => anggaran[id] > 0).length });
}
/** Target satu bulan per pos: angka khusus bulan itu bila diisi, selain itu angka umum. → { id: { nilai (0 = mati), khusus } } */
export function targetBulan(key) {
  const T = aturAnggaranBulan(); const P = T.perBulan[String(key)]; const out = {};
  AB_TARGET.forEach((t) => { const k = !!(P && P.target[t.id] !== undefined); out[t.id] = { nilai: k ? P.target[t.id] : T.target[t.id], khusus: k }; });
  return out;
}
/**
 * Lampu satu target. t = pos AB_TARGET (atau { arah, jalan }), nilai = target owner, aktual = angka mesin, X = { berjalan, hariJalan, nHari }, ambang = ambang lampu kendali (%).
 * min: HIJAU ≥ target · AMBER ≥ target − ambang % · MERAH di bawahnya. maks: HIJAU ≤ batas · AMBER ≤ batas + ambang % · MERAH di atasnya. Pos `jalan` di bulan berjalan
 * dibanding JATAH SAMPAI HARI KE-N (target × hari jalan ÷ hari bulan) — sama dengan biaya variabel. Target 0 = 'tanpa'; aktual belum bisa dihitung = 'belum'.
 */
export function kbLampuTarget(t, nilai, aktual, X, ambang) {
  if (!(nilai > 0)) return { lampu: 'tanpa', dasar: null, selisih: null, pct: null };
  const dasar = t.jalan && X && X.berjalan && X.nHari > 0 ? nilai * X.hariJalan / X.nHari : nilai;
  if (aktual === null || aktual === undefined || !isFinite(aktual)) return { lampu: 'belum', dasar, selisih: null, pct: null };
  const a = (isFinite(Number(ambang)) ? Number(ambang) : ATUR_KENDALI_BAWAAN.ambang) / 100;
  const lampu = t.arah === 'min' ? (aktual >= dasar - 1e-9 ? 'hijau' : aktual >= dasar * (1 - a) - 1e-9 ? 'amber' : 'merah') : (aktual <= dasar + 1e-9 ? 'hijau' : aktual <= dasar * (1 + a) + 1e-9 ? 'amber' : 'merah');
  return { lampu, dasar, selisih: aktual - dasar, pct: dasar ? (aktual - dasar) / dasar * 100 : null };
}
/** Draf formulir Atur lengkap: drafAtur (anggaran umum, ambang, kata) + target umum + angka khusus bulan `key`. Kosong = ikut angka umum. */
export function drafAturSemua(key) {
  const d = drafAtur(); const T = aturAnggaranBulan(); const P = T.perBulan[String(key)] || null;
  d.target = {}; AB_TARGET.forEach((t) => { d.target[t.id] = T.target[t.id] > 0 ? abTeks(T.target[t.id], t.satuan) : ''; });
  d.khususBulan = String(key); d.khususNyala = !!P; d.khususA = {}; d.khususT = {};
  KB_ID_SIMPAN.forEach((id) => { d.khususA[id] = P && P.anggaran[id] !== undefined ? String(P.anggaran[id]) : ''; });
  AB_TARGET.forEach((t) => { d.khususT[t.id] = P && P.target[t.id] !== undefined ? abTeks(P.target[t.id], t.satuan) : ''; });
  return d;
}
/** Satu ketikan target → { n } | { kosong } | { tolak }. Huruf / minus ditolak berkalimat (tidak dibulatkan diam-diam). */
function abBaca(v, t, label) {
  if (ugKosong(v)) return { kosong: true }; const s = String(v).trim();
  if (!/^[0-9][0-9.,]*$/.test(s)) return { tolak: label + ' ditulis dengan angka saja (' + (t.satuan === 'pct' ? '8,5 = 8,5 %' : t.satuan === 'kg' ? 'kg' : t.satuan === 'n' ? 'jumlah karcis' : 'rupiah') + ')' };
  const n = ugAngka(s); if (!(n >= 0) || n > AB_MAKS[t.satuan]) return { tolak: label + ' terlalu besar (paling banyak ' + (t.satuan === 'pct' ? '100 %' : ANGKA(AB_MAKS[t.satuan])) + ')' };
  if (t.satuan === 'n' && Math.round(n) !== n) return { tolak: label + ' ditulis bilangan bulat (jumlah karcis)' };
  return { n: abBulat(n, t.satuan) };
}
/**
 * SIMPAN Atur (anggaran biaya + target + angka khusus satu bulan) dalam satu ketukan: dokumen kendaliBiaya (susunAturKendali, apa adanya) + dokumen anggaranBulan
 * bila target / angka khusus berubah. isi = drafAturSemua yang diketik. Angka khusus: kosong = ikut angka umum, 0 = mati bulan itu; "angka khusus" dimatikan = dihapus.
 */
export function susunAturSemua(isi, w) {
  const K = susunAturKendali(isi, w); if (K.tolak) return K;
  const T = aturAnggaranBulan(); const target = {};
  for (const t of AB_TARGET) { const v = isi.target ? isi.target[t.id] : undefined; if (v === undefined) { target[t.id] = T.target[t.id]; continue; }
    const r = abBaca(v, t, 'Target ' + t.nama.toLowerCase()); if (r.tolak) return { tolak: r.tolak }; target[t.id] = r.kosong ? 0 : r.n; }
  const perBulan = JSON.parse(JSON.stringify(T.perBulan)); const key = String(isi.khususBulan || ''); let kataKhusus = '';
  if (abBulanSah(key)) {
    if (key > kbGeser(String(w.tanggal).slice(0, 7), 12)) return { tolak: 'Angka khusus paling jauh 12 bulan ke depan' };
    if (isi.khususNyala) { const ang = {}, tg = {};
      for (const id of KB_ID_SIMPAN) { const v = isi.khususA ? isi.khususA[id] : ''; if (ugKosong(v)) continue; const s = String(v).trim(); const n = ugAngka(s);
        if (!/^[0-9][0-9.,]*$/.test(s) || n > 1000000000) return { tolak: 'Angka khusus anggaran ' + id + ' ditulis rupiah 0 sampai Rp1.000.000.000 (0 = mati bulan itu)' }; ang[id] = Math.round(n); }
      for (const t of AB_TARGET) { const v = isi.khususT ? isi.khususT[t.id] : ''; const r = abBaca(v, t, 'Angka khusus ' + t.nama.toLowerCase()); if (r.tolak) return { tolak: r.tolak }; if (!r.kosong) tg[t.id] = r.n; }
      if (Object.keys(ang).length || Object.keys(tg).length) { perBulan[key] = { anggaran: ang, target: tg }; kataKhusus = ' · angka khusus ' + lpNamaBulan(key) + ' (' + (Object.keys(ang).length + Object.keys(tg).length) + ' pos)'; }
      else if (perBulan[key]) { delete perBulan[key]; kataKhusus = ' · angka khusus ' + lpNamaBulan(key) + ' dihapus (semua kosong)'; } }
    else if (perBulan[key]) { delete perBulan[key]; kataKhusus = ' · angka khusus ' + lpNamaBulan(key) + ' dihapus — bulan itu ikut angka umum'; }
  }
  const simpan = abUrut(perBulan); const kunci = Object.keys(simpan).sort().reverse().slice(0, AB_BULAN_MAKS); const pb = {}; kunci.sort().forEach((k) => { pb[k] = simpan[k]; });
  const berubah = JSON.stringify({ target: T.target, perBulan: abUrut(T.perBulan) }) !== JSON.stringify({ target, perBulan: pb });
  const nT = AB_TARGET.filter((t) => target[t.id] > 0).length;
  const dokumen = K.dokumen.concat(berubah ? [{ koleksi: 'aturanToko', data: { id: AB_ID, tanggal: w.tanggal, jam: w.jam, target, perBulan: pb } }] : []);
  return { dokumen, patch: Object.assign({}, K.patch, { kabar: K.patch.kabar + ' · ' + nT + ' target bulanan diisi' + kataKhusus }) };
}
/** Sebab & tindakan satu bulan: { pos: { sebab, tindakan, tanggal, jam } }. */
export function catatanPos(key) {
  const d = ugAturDok(AB_CATATAN_ID); const b = d && d.bulan && typeof d.bulan === 'object' ? d.bulan[String(key)] : null; const out = {};
  if (b && typeof b === 'object') Object.keys(b).forEach((p) => { if (AB_POS_CATATAN.indexOf(p) < 0 || !b[p]) return; const sebab = String(b[p].sebab || '').trim(), tindakan = String(b[p].tindakan || '').trim(); if (sebab || tindakan) out[p] = { sebab, tindakan, tanggal: String(b[p].tanggal || ''), jam: String(b[p].jam || '') }; });
  return out;
}
/** Tulis / ubah / hapus (dua-duanya kosong) sebab & tindakan satu pos satu bulan. Satu dokumen aturanToko/anggaranCatatan; 24 bulan terbaru disimpan. */
export function susunCatatanPos(key, pos, sebab, tindakan, w) {
  if (!abBulanSah(key)) return { tolak: 'Bulan tidak dikenal' }; if (AB_POS_CATATAN.indexOf(pos) < 0) return { tolak: 'Pos tidak dikenal' };
  if (key > String(w.tanggal).slice(0, 7)) return { tolak: 'Bulan itu belum berjalan' };
  const rapi = (t) => String(t || '').replace(/\r\n/g, '\n').trim(); const s = rapi(sebab), t = rapi(tindakan);
  if (s.length > AB_CATATAN_MAKS || t.length > AB_CATATAN_MAKS) return { tolak: 'Sebab dan tindakan paling panjang ' + AB_CATATAN_MAKS + ' huruf' };
  const d = ugAturDok(AB_CATATAN_ID); const bulan = JSON.parse(JSON.stringify(d && d.bulan && typeof d.bulan === 'object' ? d.bulan : {})); const lama = (bulan[key] || {})[pos] || null;
  if (!s && !t && !lama) return { tolak: 'Tulis sebabnya atau tindakannya dulu' };
  if (lama && String(lama.sebab || '').trim() === s && String(lama.tindakan || '').trim() === t) return { tolak: 'Tidak ada yang diubah' };
  const satu = Object.assign({}, bulan[key] || {}); if (s || t) satu[pos] = { sebab: s, tindakan: t, tanggal: w.tanggal, jam: w.jam }; else delete satu[pos];
  if (Object.keys(satu).length) bulan[key] = satu; else delete bulan[key];
  const kunci = Object.keys(bulan).filter(abBulanSah).sort().reverse().slice(0, AB_BULAN_MAKS).sort(); const simpan = {}; kunci.forEach((k) => { simpan[k] = bulan[k]; });
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: AB_CATATAN_ID, tanggal: w.tanggal, jam: w.jam, bulan: simpan } }],
    patch: { catAb: null, kabar: (s || t ? 'Sebab & tindakan disimpan' : 'Sebab & tindakan dihapus') + ' — ' + lpNamaBulan(key), kabarAwas: false } };
}
