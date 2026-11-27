// STOK, GUDANG & PRODUKSI — PAKET P5 (owner 27 Nov 2026, sensus ulang 27 Nov: A20 A43 A50 A56 A70 A92 A125 A127 B51 B72). Tanpa DOM, awalan sg.
// HANYA MEMBACA, kecuali SATU setelan owner (aturanToko/opnameKejutan, susunAturKejutan). Tidak ada rumus stok / uang baru: tiap angka diambil dari sumber yang
// sudah dipakai layar lain, dan uji_stok_p5 memeriksa tiap angka MENUTUP ke sumbernya:
//   · kartu stok per merek (A56)       → gerak buku karung PERSIS aturan mesin beku hitungStokKarungPerMerk (kedatangan, nota karung/repack/literan, adukan &
//                                         pindah buku, retur utuh, cocokkan, adukan jadi karung utuh); sisa berjalan terakhir = buku mesin (penjaga `menutup`).
//   · barang masuk hari itu (A125)     → kedatangan bertanggal itu + timbang & mutu per kedatangan (tmKedatangan, angka Stok › Barang masuk); Σ = rekapTimbangMutu.
//   · hitung karung mingguan (A127)    → hitungan tumpukan Cocokkan (penyesuaianStok bagian tumpukan) Senin–Minggu: buku vs dihitung, siapa & didampingi (A70).
//   · opname kejutan (A92)             → tanggal & merek DIUNDI dari benih rahasia owner (aturanToko/opnameKejutan — staf tidak bisa membacanya, rules aturanToko
//                                         read = daftar id); tiap bulan kaliSebulan tanggal, tiap tanggal nMerek merek berisi. Selesai = merek itu dihitung di Cocokkan.
//   · rencana beli bulanan (A20)       → pemakaian per merek (nota + adukan / pindah buku − retur utuh) rata-rata bulan selesai, tanpa musim (owner 27 Nov 2026).
//   · stok yang dipesan (B51)          → pesanan pelanggan yang belum jadi nota × modal per kg / unit di buku (nilai yang sama dengan neraca).
//   · produksi per bulan (B72)         → kemasRentang (Laporan › Pondasi, angka di catatan adukannya) + per adukan: susut %, sampel isi & oplos (A50); rencana produksi
//                                         = "aduk N unit" yang sama dengan Stok › Gudang (laju 14 hari × HARI_TARGET − sisa).
import { ambilSemuaBatch, ambilPenjualan, ambilProduksiBerlaku, ambilRetur, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ingatStokKarung, ingatStokKemasan, cacheMentah, ambilPesanan,
  stokMerekSaja, petaBukuWadah, catatanPertama, ingatPerVersi } from '../data/toko.js';
import { hitungHppMerkDalamBatch, hitungStokBahanKemasan } from '../mesin/beku.js';
import { pesananBelumTuntas, kunciKemasan, LABEL_BAHAN_KEMASAN } from '../mesin/pembantu.js';
import { RP, KG, ANGKA, hariIniIso, tanggalPendek } from '../inti/format.js';
import { aturCatat, tmKedatangan, rekapTimbangMutu } from './stok-catat-logika.js';
import { hitunganFisik } from './jual-logika.js';
import { umAtur, daftarBarang, HARI_TARGET } from './stok-logika.js';
import { poBarisSah } from './pesanan-logika.js';
import { kemasRentang } from './laporan-logika.js';
import { jenisProduksi } from './stok-adukan-logika.js';

const sgB2 = (n) => Math.round((Number(n) || 0) * 100) / 100;
const sgMili = (n) => Math.round((Number(n) || 0) * 1000);   // kg → gram bulat: penjumlahan panjang tanpa ekor pecahan (data kg ≤ 3 desimal)
const sgHariKe = (iso) => Math.round(new Date(String(iso) + 'T00:00:00Z').getTime() / 86400000);
const sgIso = (n) => new Date(n * 86400000).toISOString().slice(0, 10);
const sgGeser = (iso, n) => sgIso(sgHariKe(iso) + n);
const sgAkhirBulan = (key) => { const [y, m] = String(key).split('-').map(Number); return key + '-' + String(new Date(Date.UTC(y, m, 0)).getUTCDate()).padStart(2, '0'); };
const sgGeserBulan = (key, n) => { const [y, m] = String(key).split('-').map(Number); const t = y * 12 + (m - 1) + n; return Math.floor(t / 12) + '-' + String((t % 12) + 1).padStart(2, '0'); };
const sgTgl = (iso) => tanggalPendek(iso).replace(/ \d{4}$/, '');
const sgUrut = (a, b) => String(a.tanggal).localeCompare(String(b.tanggal)) || String(a.jam || '').localeCompare(String(b.jam || '')) || (Number(a.id) || 0) - (Number(b.id) || 0) || String(a.id).localeCompare(String(b.id));
export const SG_NAMA_BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
const sgNamaBulan = (key) => SG_NAMA_BULAN[Number(String(key).slice(5, 7)) - 1] + ' ' + String(key).slice(0, 4);

// ==================== A56 · KARTU STOK PER MEREK (kg, kronologis) ====================
export const SG_JENIS_GERAK = { masuk: 'Barang masuk', jual: 'Terjual', aduk: 'Diaduk / dipindah buku', retur: 'Retur pembeli (utuh)', cocok: 'Hitungan gudang', tutup: 'Timbang tutup hari', sesuai: 'Penyesuaian', karung: 'Adukan jadi karung utuh' };
const SG_JUAL = { karung: 'karung', repacking: 'repack', literan: 'literan' };
/**
 * Semua gerak buku karung sampai `sampai` (inklusif; kosong = semua), dikelompokkan per kunci buku — aturan PERSIS hitungStokKarungPerMerk (mesin beku tidak
 * diubah): buku lahir dari baris kedatangan (bukan bal); nota, adukan, retur utuh & cocokkan hanya memotong buku yang sudah lahir dari kedatangan; adukan jadi
 * karung utuh menambah merkTujuan (dan melahirkan bukunya bila belum ada — sesudah nota dkk. dihitung, persis urutan mesin). Diingat per versi data.
 */
export function sgGerak(sampai) { return ingatPerVersi('sgGerak|' + (sampai || ''), () => sgGerakHitung(sampai || '')); }
function sgGerakHitung(sampai) {
  const ok = (x) => !sampai || String(x.tanggal || '') <= sampai; const out = {}; const lahir = {};
  const taruh = (k, r) => { (out[k] = out[k] || []).push(r); };
  ambilSemuaBatch().filter(ok).forEach((b) => {
    const ket = b.lahirBuku ? 'buku lahir' : b.tutupBuku ? 'saldo pembuka' : b.stokAwal ? 'stok awal' : (b.pemasok || 'kedatangan');
    hitungHppMerkDalamBatch(b.merkList, b.biayaBongkar).forEach((m) => { if (m.bentuk === 'bal') return; lahir[m.merk] = true;
      taruh(m.merk, { tanggal: b.tanggal || '', jam: b.jam || '', id: b.id, jenis: 'masuk', kg: Number(m.totalKg) || 0, harga: Number(m.hargaPerKg) || 0, modal: Number(m.hppPerKg) || 0, ket, batchId: b.id }); }); });
  ambilPenjualan().filter(ok).forEach((p) => { if (!SG_JUAL[p.jenis] || !p.merkSumber || !lahir[p.merkSumber]) return;
    taruh(p.merkSumber, { tanggal: p.tanggal || '', jam: p.jam || '', id: p.id, jenis: 'jual', kg: -(Number(p.totalKg) || 0), ket: SG_JUAL[p.jenis], jalur: p.jenis, nota: 1 }); });
  const prod = ambilProduksiBerlaku().filter(ok);
  prod.forEach((pr) => { const jp = jenisProduksi(pr); const ket = jp === 'adukan' ? 'adukan → ' + (pr.namaProduk || '') + ' ' + String(pr.ukuranKemasan || '').replace('.', ',') + ' kg' : jp === 'rework' ? 'rework karantina' : jp === 'gabungKarung' ? 'gabung karung' : 'pindah buku';
    const tujuan = pr.jadiKarungUtuh && pr.merkTujuan ? String(pr.merkTujuan) : '';   // pindah buku ke buku lain (karung belakang / wadah / merek lain)
    if (Array.isArray(pr.sumberList) && pr.sumberList.length > 0) pr.sumberList.forEach((s) => { if (s.merk && lahir[s.merk]) taruh(s.merk, { tanggal: pr.tanggal || '', jam: pr.jam || '', id: pr.id, jenis: 'aduk', kg: -(s.kg || 0), ket: tujuan ? 'pindah buku → ' + tujuan : ket, produksi: jp, tujuan }); });
    else if (pr.merkSumber && lahir[pr.merkSumber]) taruh(pr.merkSumber, { tanggal: pr.tanggal || '', jam: pr.jam || '', id: pr.id, jenis: 'aduk', kg: -(pr.kgDipakai || 0), ket: tujuan ? 'pindah buku → ' + tujuan : ket, produksi: jp, tujuan }); });
  ambilRetur().filter(ok).forEach((r) => { if (r.jenisAsal === 'karung' && r.kondisi === 'utuh' && r.merkSumber && lahir[r.merkSumber]) taruh(r.merkSumber, { tanggal: r.tanggal || '', jam: r.jam || '', id: r.id, jenis: 'retur', kg: Number(r.totalKg) || 0, ket: r.namaPelanggan || 'pembeli' }); });
  ambilPenyesuaianStok().filter(ok).forEach((o) => { if (!o.merk || !lahir[o.merk]) return; const fisik = hitunganFisik(o);
    taruh(o.merk, { tanggal: o.tanggal || '', jam: o.jam || '', id: o.id, jenis: o.dariTutup ? 'tutup' : fisik ? 'cocok' : 'sesuai', kg: Number(o.selisihKg) || 0, ket: String(o.alasan || '').slice(0, 80) + (o.bagian === 'wadah' ? ' (wadah ' + (o.wadah || '') + ')' : ''),
      dihitungOleh: o.dihitungOleh || '', didampingi: o.didampingi || '' }); });
  prod.forEach((pr) => { if (!pr.jadiKarungUtuh || !pr.merkTujuan) return; const kg = (pr.ukuranKemasan || 0) * (pr.jumlahUnit || 0); if (kg <= 0) return;
    taruh(pr.merkTujuan, { tanggal: pr.tanggal || '', jam: pr.jam || '', id: pr.id, jenis: 'karung', kg, ket: pr.merkSumber ? 'dari ' + pr.merkSumber : 'pindah buku masuk', modal: pr.kgDipakai > 0 && kg > 0 ? (pr.hppSumberPerKgDipakai || 0) * (pr.kgDipakai || 0) / kg : 0 }); });
  Object.keys(out).forEach((k) => out[k].sort(sgUrut));
  return out;
}
/** Daftar buku untuk dipilih di kartu stok: merek (bukan buku wadah / karung belakang) dulu menurut sisa terbanyak, lalu buku wadah. */
export function sgDaftarKartu() {
  const st = ingatStokKarung(); const bw = petaBukuWadah();
  return Object.keys(st).map((k) => ({ kunci: k, sisa: sgB2(st[k].sisaKg), wadah: !!bw[k] })).sort((a, b) => (a.wadah ? 1 : 0) - (b.wadah ? 1 : 0) || b.sisa - a.sisa || a.kunci.localeCompare(b.kunci));
}
export const SG_KARTU_HARI = 30;
/**
 * Kartu stok satu buku, dari–sampai (inklusif): saldo awal (semua gerak sebelum `dari`), lalu tiap gerak: tanggal · masuk · keluar · sisa berjalan · harga beli/kg
 * (dan modal/kg = harga + bongkar, baris barang masuk). rinci=false: nota satu jalur pada satu hari digabung jadi satu baris (N nota). Sisa akhir = buku mesin
 * sampai tanggal itu (ingatStokKarung(sampai)) → `menutup`; kalau tidak, disebut (jangan dipakai memutuskan).
 */
export function sgKartuStok(kunci, dari, sampai, rinci) {
  const s = sampai || hariIniIso(); const d = dari || sgGeser(s, -(SG_KARTU_HARI - 1)); const semua = (sgGerak(s)[kunci] || []);
  let awal = 0; const tampil = []; semua.forEach((r) => { if (r.tanggal < d) awal += sgMili(r.kg); else tampil.push(r); });
  let baris = tampil;
  if (!rinci) { const g = {}; baris = []; tampil.forEach((r) => { if (r.jenis !== 'jual') { baris.push(r); return; } const k = r.tanggal + '|' + r.jalur; if (!g[k]) { g[k] = Object.assign({}, r, { nota: 0, kg: 0 }); baris.push(g[k]); } g[k].nota += 1; g[k].kg += r.kg; }); }
  let jalan = awal; let masuk = 0, keluar = 0;   // gram bulat
  const out = baris.map((r) => { const g = sgMili(r.kg); jalan += g; if (g > 0) masuk += g; else keluar -= g;
    return { tanggal: r.tanggal, jam: r.jenis === 'jual' && !rinci && r.nota > 1 ? '' : String(r.jam || '').slice(0, 5), jenis: r.jenis, nama: SG_JENIS_GERAK[r.jenis], ket: r.jenis === 'jual' ? (r.nota > 1 ? r.nota + ' nota ' + r.ket : 'nota ' + r.ket) : r.ket,
      masuk: g > 0 ? sgB2(g / 1000) : 0, keluar: g < 0 ? sgB2(-g / 1000) : 0, sisa: sgB2(jalan / 1000), harga: r.jenis === 'masuk' ? r.harga : null, modal: r.jenis === 'masuk' || r.jenis === 'karung' ? r.modal : null,
      dihitungOleh: r.dihitungOleh || '', didampingi: r.didampingi || '' }; });
  const buku = ingatStokKarung(s)[kunci]; const mesin = buku ? sgB2(buku.sisaKg) : null; const akhir = sgB2(jalan / 1000);
  // mesin menjumlah pecahan kg dengan angka desimal komputer lalu membulatkan ke 0,01 kg; di sini dijumlah per gram. Beda ≤ 0,01 kg = pembulatan setengah sen (disebut).
  const beda = mesin === null ? 0 : Math.abs(akhir - mesin); const menutup = mesin === null ? !semua.length : beda < 0.0101;
  return { kunci, dari: d, sampai: s, rinci: !!rinci, saldoAwal: sgB2(awal / 1000), baris: out, masukKg: sgB2(masuk / 1000), keluarKg: sgB2(keluar / 1000), sisaAkhir: akhir, mesin, menutup, pembulatan: menutup && beda > 0.005, ada: !!buku,
    hargaTerakhir: buku ? buku.hargaTerakhirPerKg || 0 : 0, modalBuku: buku ? buku.hppTerakhirPerKg || 0 : 0,
    kalimat: !buku ? kunci + ' tidak ada di buku gudang' : (menutup ? 'Sisa berjalan ' + KG(akhir) + (beda > 0.005 ? ' ≈ buku gudang ' + KG(mesin) + ' (beda 0,01 kg = pembulatan)' : ' = buku gudang ' + KG(mesin)) + ' (mesin yang sama dengan Stok › Gudang).' : 'TIDAK MENUTUP: sisa berjalan ' + KG(akhir) + ' ≠ buku ' + KG(mesin) + ' — jangan dipakai memutuskan, laporkan.') };
}

// ==================== A125 · BARANG MASUK HARI ITU ====================
const sgKedatanganSungguhan = (b) => !!b && !b.lahirBuku && !b.stokAwal && !b.tutupBuku;
/** Kedatangan bertanggal `iso`: per kedatangan pemasok · karung · kg buku · nilai · timbang & mutu (tmKedatangan); total; teks WA satu baris. Σ = rekapTimbangMutu hari itu. */
export function sgMasukHari(iso) {
  const A = aturCatat(); const daftar = ambilSemuaBatch().filter((b) => sgKedatanganSungguhan(b) && b.tanggal === iso).slice().sort(sgUrut).map((b) => {
    const rows = (b.merkList || []).filter((m) => m && m.bentuk !== 'bal'); const bal = (b.merkList || []).filter((m) => m && m.bentuk === 'bal'); const T = tmKedatangan(b, A);
    return { id: b.id, jam: String(b.jam || '').slice(0, 5), pemasok: b.pemasok || '(tanpa nama pemasok)', karung: rows.reduce((a, m) => a + (Number(m.jumlahKarung) || 0), 0), bal: bal.reduce((a, m) => a + (Number(m.jumlahBal) || 0), 0),
      kg: sgB2(rows.reduce((a, m) => a + (Number(m.totalKg) || 0), 0)), nilai: (b.merkList || []).reduce((a, m) => a + (Number(m && m.subtotalHarga) || 0), 0) + (Number(b.biayaBongkar) || 0), cara: b.caraBayar === 'utang' ? 'bon' : 'tunai',
      merek: rows.map((m) => m.merk + ' ' + (m.jumlahKarung || 0) + '×' + (m.beratKarung || '?')).concat(bal.map((m) => m.merk + ' ' + (m.jumlahBal || 0) + ' bal')).join(' · '), timbang: T, awas: T.awas.length > 0 }; });
  const sig = (f) => daftar.reduce((a, x) => a + f(x), 0); const R = rekapTimbangMutu({ dari: iso, sampai: iso });
  const total = { n: daftar.length, karung: sig((x) => x.karung), bal: sig((x) => x.bal), kg: sgB2(sig((x) => x.kg)), nilai: sig((x) => x.nilai), kgNota: sgB2(sig((x) => x.timbang.kgNota)), kgTimbang: sgB2(sig((x) => x.timbang.kgTimbang)),
    selisihKg: sgB2(sig((x) => x.timbang.selisihKg)), ditimbang: daftar.filter((x) => x.timbang.nBaris && x.timbang.ditimbang === x.timbang.nBaris).length, belum: daftar.filter((x) => x.timbang.nBaris && !x.timbang.ditimbang).length, awas: daftar.filter((x) => x.awas).length };
  // penjaga: kedatangan berbaris karung & selisih timbangnya = rekap Stok › Barang masuk hari yang sama
  const menutup = R.total.kedatangan === daftar.filter((x) => x.timbang.nBaris > 0).length && Math.abs(R.total.selisihKg - total.selisihKg) < 0.006;
  const teks = !daftar.length ? 'Barang masuk: tidak ada kedatangan' : 'Barang masuk: ' + total.n + ' kedatangan · ' + (total.karung ? ANGKA(total.karung) + ' karung · ' : '') + (total.bal ? ANGKA(total.bal) + ' bal · ' : '') + KG(total.kg)
    + (total.kgNota > 0 ? ' · timbang ' + (total.selisihKg === 0 ? 'pas' : (total.selisihKg > 0 ? 'lebih ' : 'kurang ') + KG(Math.abs(total.selisihKg))) : '') + (total.belum ? ' · ' + total.belum + ' belum ditimbang' : '') + (total.awas ? ' · ' + total.awas + ' mutu AWAS' : '');
  return { iso, daftar, total, rekap: R.total, menutup, teks, sumber: 'Stok › Barang masuk', tujuan: { ke: 'stok', lembar: 'masuk' } };
}

// ==================== A127 · HITUNG KARUNG MINGGUAN vs KARTU STOK (+ A70 didampingi) ====================
/** Hitungan tumpukan gudang (Cocokkan › Tumpukan, juga hitungan lama satu angka per nama) — bukan timbang tutup hari, bukan wadah, bukan rework. */
export const sgHitungTumpukan = (d) => !!d && !!d.merk && hitunganFisik(d) && !d.dariTutup && d.bagian !== 'wadah' && d.bagian !== 'karung';
const sgSenin = (iso) => { const n = sgHariKe(iso); return sgIso(n - (((n + 3) % 7) + 7) % 7); };   // 1970-01-01 = Kamis
/**
 * Satu minggu Senin–Minggu (awal = tanggal mana pun di minggu itu): tiap merek yang dihitung — kali, terakhir, buku vs dihitung (kg) & selisih kg + karung (÷ berat
 * karung merek), siapa menghitung & didampingi; merek berisi yang TIDAK dihitung minggu itu; kemasan yang dihitung; opname kejutan minggu itu & selesai/tidak.
 */
export function sgHitungMinggu(awal, kini) {
  const sen = sgSenin(awal); const akhir = sgGeser(sen, 6); const hari = hariIniIso(kini); const sampai = akhir < hari ? akhir : hari; const per = {};
  ambilPenyesuaianStok().forEach((d) => { if (!sgHitungTumpukan(d) || d.tanggal < sen || d.tanggal > sampai) return; const p = per[d.merk] || (per[d.merk] = { merk: d.merk, kali: 0, selisihKg: 0, rp: 0, hitungan: [] });
    p.kali += 1; p.selisihKg += Number(d.selisihKg) || 0; p.rp += Number(d.nilaiRp) || 0;
    p.hitungan.push({ tanggal: d.tanggal, jam: String(d.jam || '').slice(0, 5), id: d.id, bukuKg: d.bagianSistemKg !== undefined ? Number(d.bagianSistemKg) : Number(d.kgSistem) || 0, dihitungKg: d.bagianFisikKg !== undefined ? Number(d.bagianFisikKg) : Number(d.kgFisik) || 0,
      selisihKg: Number(d.selisihKg) || 0, oleh: d.dihitungOleh || '', akun: d.oleh || '', didampingi: d.didampingi || '', hama: d.hama && d.hama !== 'tidak' ? d.hama : '', persis: !!d.cocokPersis }); });
  const stok = stokMerekSaja(ingatStokKarung(sampai)); const brt = {}; daftarBarang().forEach((b) => { if (b.jenis === 'karung') brt[b.kunci] = b.beratKarung || 50; });
  const daftar = Object.keys(per).map((m) => { const p = per[m]; p.hitungan.sort(sgUrut); const t = p.hitungan[p.hitungan.length - 1]; const berat = brt[m] || 50;
    return Object.assign(p, { selisihKg: sgB2(p.selisihKg), selisihKarung: Math.round(p.selisihKg / berat * 10) / 10, berat, terakhir: t, tanpaPendamping: p.hitungan.filter((x) => !x.didampingi).length }); })
    .sort((a, b) => a.selisihKg - b.selisihKg || a.merk.localeCompare(b.merk));
  const belum = Object.keys(stok).filter((m) => !per[m] && (Number(stok[m].sisaKg) || 0) > 0.05).sort((a, b) => (stok[b].sisaKg || 0) - (stok[a].sisaKg || 0)).map((m) => ({ merk: m, sisaKg: sgB2(stok[m].sisaKg) }));
  const kemasan = ambilPenyesuaianKemasan().filter((d) => d && d.namaProduk && d.tanggal >= sen && d.tanggal <= sampai).length;
  const K = sgKejutanAtur(); const kej = K.aktif ? sgKejutanRentang(sen, sampai, kini) : [];
  const nHit = daftar.reduce((a, p) => a + p.kali, 0); const nTanpa = daftar.reduce((a, p) => a + p.tanpaPendamping, 0);
  const total = { merek: daftar.length, hitungan: nHit, tanpaPendamping: nTanpa, selisihKg: sgB2(daftar.reduce((a, p) => a + p.selisihKg, 0)), rp: daftar.reduce((a, p) => a + p.rp, 0), belum: belum.length, kemasan };
  return { awal: sen, akhir, sampai, berjalan: akhir >= hari, daftar, belum, total, kejutan: kej,
    kalimat: !nHit ? 'Minggu ' + sgTgl(sen) + '–' + sgTgl(akhir) + ': belum ada tumpukan yang dihitung' + (belum.length ? ' · ' + belum.length + ' merek berisi belum dihitung' : '')
      : nHit + ' hitungan · ' + daftar.length + ' merek · selisih ' + (total.selisihKg > 0 ? '+' : '') + KG(total.selisihKg) + (nTanpa ? ' · ' + nTanpa + ' tanpa pendamping' : ' · semua didampingi') + (belum.length ? ' · ' + belum.length + ' merek belum dihitung' : ''),
    sumber: 'Stok › Cocokkan', tujuan: { ke: 'stok', lembar: 'cocok' } };
}

// ==================== A92 · OPNAME KEJUTAN (tanggal & merek diundi) ====================
export const SG_KEJUTAN_ID = 'opnameKejutan';
export const SG_KEJUTAN_BAWAAN = { kaliSebulan: 2, nMerek: 3 };   // bawaan — pilihan owner 27 Nov 2026 ("dua-duanya"), bisa diubah di Stok › Tugas gudang
export const SG_KEJUTAN_BATAS = { kaliSebulan: [1, 8], nMerek: [1, 10] };
export const SG_KEJUTAN_TENGGANG = 2;   // hitungan merek itu sampai 2 hari sesudah tanggal kejutan masih dihitung "selesai"; sesudahnya "terlewat"
const SG_KEJUTAN_NAMA = { kaliSebulan: 'Opname kejutan per bulan', nMerek: 'Merek per kejutan' };
const sgDokAtur = (id) => cacheMentah('aturan').find((d) => String(d.id) === id) || null;
/** Setelan opname kejutan: aktif hanya bila owner menyalakannya (dokumen ber-benih). Tanpa dokumen = mati (bukan bawaan menyala). */
export function sgKejutanAtur() {
  const d = sgDokAtur(SG_KEJUTAN_ID); const o = {};
  Object.keys(SG_KEJUTAN_BAWAAN).forEach((k) => { const n = d ? Number(d[k]) : NaN; const b = SG_KEJUTAN_BATAS[k]; o[k] = isFinite(n) && Math.round(n) === n && n >= b[0] && n <= b[1] ? n : SG_KEJUTAN_BAWAAN[k]; });
  const benih = d && typeof d.benih === 'string' && d.benih.length >= 8 ? d.benih : '';
  return Object.assign(o, { aktif: !!d && d.aktif !== false && !!benih, benih, ada: !!d, sejak: d ? String(d.mulai || d.tanggal || '') : '', dariOwner: !!d });
}
/**
 * Simpan setelan (owner). isi = { aktif, kaliSebulan, nMerek, benih }. Benih = rahasia pengundi (dibuat layar dengan crypto.getRandomValues, ≥ 8 huruf); setelan
 * yang sudah ada mempertahankan benihnya (undian bulan berjalan tidak berubah), kecuali `undiUlang`. Pecahan / di luar batas DITOLAK dengan kalimat.
 */
export function susunAturKejutan(isi, w) {
  const I = isi || {}; const kini = sgKejutanAtur(); const o = {}; let tolak = '';
  Object.keys(SG_KEJUTAN_BAWAAN).forEach((k) => { if (tolak) return; const t = String(I[k] === undefined || I[k] === null ? '' : I[k]).trim().replace(',', '.'); const b = SG_KEJUTAN_BATAS[k];
    if (!t) { o[k] = kini[k]; return; } const n = Number(t); if (!isFinite(n) || Math.round(n) !== n || n < b[0] || n > b[1]) tolak = SG_KEJUTAN_NAMA[k] + ' harus bilangan bulat ' + b[0] + '–' + b[1]; else o[k] = n; });
  if (tolak) return { tolak };
  const aktif = I.aktif === undefined ? true : !!I.aktif; const baru = String(I.benih || '');
  const benih = kini.benih && !I.undiUlang ? kini.benih : baru;
  if (aktif && benih.length < 8) return { tolak: 'Pengundi opname kejutan belum siap — coba sekali lagi' };
  const d = sgDokAtur(SG_KEJUTAN_ID);
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: SG_KEJUTAN_ID, tanggal: w.tanggal, jam: w.jam, aktif, kaliSebulan: o.kaliSebulan, nMerek: o.nMerek, benih: benih || '', mulai: d && d.mulai && !I.undiUlang ? d.mulai : w.tanggal } }],
    patch: { aturKj: null, kabar: aktif ? 'Opname kejutan menyala — ' + o.kaliSebulan + '× sebulan, ' + o.nMerek + ' merek tiap kali, tanggal & merek diundi. Pengingatnya hanya di perangkat owner; staf tidak melihat jadwalnya.' : 'Opname kejutan dimatikan — pengingat rutin tiap N hari tetap jalan.', kabarAwas: false } };
}
/** FNV-1a 32 bit — pengundi tetap: benih + tanggal yang sama selalu memberi undian yang sama (tanpa menulis apa pun tiap bulan). */
export function sgAcak(s) { let h = 0x811c9dc5; const t = String(s); for (let i = 0; i < t.length; i++) { h ^= t.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; } return h >>> 0; }
/** Tanggal kejutan satu bulan ('YYYY-MM') — kaliSebulan hari berbeda, urut. Bulan sebelum owner menyalakan = tidak ada; bulan mulai = hanya tanggal sesudah mulai. */
export function sgKejutanTanggal(key, A0) {
  const A = A0 || sgKejutanAtur(); if (!A.aktif) return []; const n = Number(sgAkhirBulan(key).slice(8)); const pilih = [];
  for (let i = 0; pilih.length < Math.min(A.kaliSebulan, n) && i < 200; i++) { const d = 1 + (sgAcak(A.benih + '|' + key + '|' + i) % n); if (pilih.indexOf(d) < 0) pilih.push(d); }
  return pilih.sort((a, b) => a - b).map((d) => key + '-' + String(d).padStart(2, '0')).filter((t) => !A.sejak || t >= A.sejak);
}
/** Merek yang diundi untuk tanggal itu: nMerek buku merek (bukan wadah) yang berisi pada pagi hari itu (buku sampai kemarin), diundi tetap dari benih. */
export function sgKejutanMerek(iso, A0) {
  const A = A0 || sgKejutanAtur(); if (!A.aktif) return []; const st = stokMerekSaja(ingatStokKarung(sgGeser(iso, -1)));
  const kolam = Object.keys(st).filter((m) => (Number(st[m].sisaKg) || 0) > 0.05).sort(); const out = [];
  for (let i = 0; out.length < Math.min(A.nMerek, kolam.length) && i < 300; i++) { const m = kolam[sgAcak(A.benih + '|' + iso + '|m' + i) % kolam.length]; if (out.indexOf(m) < 0) out.push(m); }
  return out.sort();
}
/** Tiap tanggal kejutan dari–sampai: merek yang diundi, yang sudah dihitung (Cocokkan tumpukan, tanggal itu s.d. + tenggang), keadaan nanti · hari ini · selesai · terlewat. */
export function sgKejutanRentang(dari, sampai, kini) {
  const A = sgKejutanAtur(); if (!A.aktif) return []; const hari = hariIniIso(kini); const out = [];
  for (let k = String(dari).slice(0, 7); k <= String(sampai).slice(0, 7); k = sgGeserBulan(k, 1)) sgKejutanTanggal(k, A).forEach((t) => { if (t < dari || t > sampai) return;
    const merek = t <= hari ? sgKejutanMerek(t, A) : []; const batas = sgGeser(t, SG_KEJUTAN_TENGGANG);
    const sudah = merek.filter((m) => ambilPenyesuaianStok().some((d) => sgHitungTumpukan(d) && d.merk === m && d.tanggal >= t && d.tanggal <= batas));
    const keadaan = t > hari ? 'nanti' : sudah.length === merek.length && merek.length ? 'selesai' : hari > batas ? 'terlewat' : t === hari ? 'hari ini' : 'menunggu';
    out.push({ tanggal: t, merek, sudah, belum: merek.filter((m) => sudah.indexOf(m) < 0), keadaan, batas }); });
  return out;
}
/** Ringkas untuk Stok › Tugas gudang (OWNER saja — layar tidak memanggilnya untuk akun staf): bulan ini & depan, kejutan yang masih harus dikerjakan. */
export function sgKejutanStatus(kini) {
  const A = sgKejutanAtur(); const hari = hariIniIso(kini); const key = hari.slice(0, 7);
  const daftar = A.aktif ? sgKejutanRentang(key + '-01', sgAkhirBulan(sgGeserBulan(key, 1)), kini) : [];
  const harus = daftar.filter((x) => x.keadaan === 'hari ini' || x.keadaan === 'menunggu');
  return { atur: A, daftar, harus, berikut: daftar.find((x) => x.keadaan === 'nanti') || null, terlewat: daftar.filter((x) => x.keadaan === 'terlewat').length,
    kalimat: !A.aktif ? 'Opname kejutan mati — nyalakan supaya sistem mengundi tanggal & merek' : harus.length ? 'Hari ini: hitung ' + harus.map((x) => x.belum.join(', ')).join(' · ') : 'Tidak ada opname kejutan yang menunggu' };
}
/** Sumber pengingat jenis 'kejutan' (diteruskan app.js lewat lokal.kejutan HANYA di perangkat owner): kejutan yang jatuh hari ini / masih dalam tenggang dan belum selesai. */
export function sgSumberPengingat(kini) {
  return sgKejutanStatus(kini).harus.map((x) => ({ id: 'kejutan|' + x.tanggal, jenis: 'kejutan', kunci: x.tanggal, teks: 'Opname kejutan: hitung ' + x.belum.join(', '), siapa: 'stok', jatuh: x.tanggal, n: 0,
    ket: 'diundi ' + x.merek.length + ' merek · hitung tumpukannya di Stok › Cocokkan sampai ' + sgTgl(x.batas) + (x.sudah.length ? ' · sudah: ' + x.sudah.join(', ') : '') }));
}

// ==================== A20 · RENCANA BELI BULANAN (tanpa musim) ====================
export const SG_RENCANA_BULAN = 3;   // rata-rata pemakaian dari 3 bulan selesai terakhir (keputusan owner 27 Nov 2026: bangun sekarang, tanpa musim)
/**
 * Rencana beli bulan DEPAN per merek: pemakaian (nota karung/repack/literan + adukan & pindah buku − retur utuh; BUKAN selisih cocokkan) per hari, rata-rata atas
 * hari tercatat dalam SG_RENCANA_BULAN bulan selesai terakhir (bulan sebelum catatan pertama toko dilewati, bulan pertama dipendekkan). Kebutuhan = laju × hari bulan
 * depan; perkiraan sisa awal bulan depan = sisa sekarang − laju × hari tersisa bulan ini; cadangan akhir = laju × batas bawah hari stok (Stok › Umur, P1).
 * Beli = kebutuhan + cadangan − sisa awal, dibulatkan ke karung penuh; rupiah = perkiraan atas harga beli terakhir. Tanpa penyesuaian musim (disebut).
 */
export function sgRencanaBeli(kini, nBulan) {
  const hari = hariIniIso(kini); const key = hari.slice(0, 7); const depan = sgGeserBulan(key, 1); const N = Math.max(1, Math.min(6, Number(nBulan) || SG_RENCANA_BULAN));
  const pertama = catatanPertama() || ''; const bulan = [];
  for (let i = N; i >= 1; i--) { const k = sgGeserBulan(key, -i); const a = k + '-01', b = sgAkhirBulan(k); if (pertama && b < pertama) continue; const d = pertama && pertama > a ? pertama : a; bulan.push({ key: k, dari: d, sampai: b, hari: sgHariKe(b) - sgHariKe(d) + 1 }); }
  const nHari = bulan.reduce((a, x) => a + x.hari, 0); const G = sgGerak(hari); const st = stokMerekSaja(ingatStokKarung()); const bw = petaBukuWadah(); const brt = {}; daftarBarang().forEach((b) => { if (b.jenis === 'karung') brt[b.kunci] = b.beratKarung || 50; });
  const A = umAtur(); const hariDepan = Number(sgAkhirBulan(depan).slice(8)); const sisaHari = sgHariKe(sgAkhirBulan(key)) - sgHariKe(hari);   // hari sesudah hari ini sampai akhir bulan
  const daftar = Object.keys(st).filter((m) => !bw[m]).map((m) => {
    // pemakaian: nota, adukan, pindah ke karung belakang / wadah (beras yang akan dijual literan) − retur utuh. Pindah buku ke MEREK lain (ganti nama, gabung ukuran) bukan pemakaian.
    const pakaiR = (r) => r.jenis === 'jual' || r.jenis === 'retur' || (r.jenis === 'aduk' && (!r.tujuan || !!bw[r.tujuan]));
    const perBulan = bulan.map((b) => sgB2((G[m] || []).reduce((a, r) => a + (r.tanggal >= b.dari && r.tanggal <= b.sampai && pakaiR(r) ? -r.kg : 0), 0)));
    const ini = sgB2((G[m] || []).reduce((a, r) => a + (r.tanggal >= key + '-01' && r.tanggal <= hari && pakaiR(r) ? -r.kg : 0), 0));
    // nama yang BERHENTI dipakai (bulan selesai terakhir & bulan ini tanpa pemakaian, mis. nama lama yang sudah diganti) tidak diramal dari bulan-bulan sebelumnya
    const berhenti = bulan.length > 0 && !(perBulan[perBulan.length - 1] > 0.05) && !(ini > 0.05);
    const pakai = perBulan.reduce((a, x) => a + x, 0); const lajuRata = nHari > 0 && !berhenti ? Math.max(0, pakai) / nHari : 0; const sisa = sgB2(st[m].sisaKg);
    // pemakaian bulan selesai terakhir yang BERUBAH TAJAM (< ½ atau > 2× rata-rata — merek baru, nama yang diganti) → laju bulan terakhir itu saja (disebut "naik" / "turun")
    const bA = bulan[bulan.length - 1]; const lajuAkhir = bA && bA.hari > 0 ? Math.max(0, perBulan[perBulan.length - 1]) / bA.hari : 0;
    const arah = berhenti || bulan.length < 2 || !(lajuRata > 0) ? '' : lajuAkhir < lajuRata * 0.5 ? 'turun' : lajuAkhir > lajuRata * 2 ? 'naik' : '';
    const laju = arah ? lajuAkhir : lajuRata;
    const butuh = laju * hariDepan; const sisaAwal = Math.max(0, sisa - laju * sisaHari); const cadangan = laju * A.targetHariMin; const kurang = Math.max(0, butuh + cadangan - sisaAwal);
    const berat = brt[m] || 50; const karung = kurang > 0.05 ? Math.ceil(kurang / berat - 1e-9) : 0; const harga = Number(st[m].hargaTerakhirPerKg) || 0;
    return { merk: m, perBulan, ini, berhenti, arah, lajuRata, pakai: sgB2(pakai), laju, sisa, butuh: sgB2(butuh), sisaAwal: sgB2(sisaAwal), cadangan: sgB2(cadangan), kurang: sgB2(kurang), berat, karung, kg: karung * berat, harga, rp: Math.round(karung * berat * harga) };
  }).filter((x) => x.pakai > 0.05 || x.karung > 0).sort((a, b) => b.kg - a.kg || b.butuh - a.butuh || a.merk.localeCompare(b.merk));
  const berhenti = daftar.filter((x) => x.berhenti); const dipakai = daftar.filter((x) => !x.berhenti);
  const sig = (f) => dipakai.reduce((a, x) => a + x[f], 0);
  const total = { merek: daftar.filter((x) => x.karung > 0).length, karung: sig('karung'), kg: sig('kg'), rp: sig('rp'), butuh: sgB2(sig('butuh')), pakai: sgB2(sig('pakai')), tanpaHarga: daftar.filter((x) => x.karung > 0 && !(x.harga > 0)).length };
  return { hari, key, depan, namaDepan: sgNamaBulan(depan), bulan: bulan.map((b) => Object.assign({ nama: sgNamaBulan(b.key) }, b)), nHari, targetHariMin: A.targetHariMin, daftar: dipakai, berhenti, total,
    musim: 'Belum memperhitungkan musim (panen / paceklik) — penyesuaian musim baru bisa dihitung sesudah data setahun (±Agustus 2027).',
    rumus: 'pemakaian per hari = (terjual + diaduk / dipindah ke wadah − retur utuh) ÷ ' + nHari + ' hari tercatat (' + bulan.map((b) => sgNamaBulan(b.key)).join(', ') + '); bulan terakhir berubah tajam (< ½ atau > 2× rata-rata) = laju bulan terakhir saja; nama tanpa pemakaian bulan terakhir & bulan ini = berhenti dipakai · butuh ' + sgNamaBulan(depan) + ' = laju × ' + hariDepan + ' hari · beli = butuh + cadangan ' + A.targetHariMin + ' hari − perkiraan sisa 1 ' + SG_NAMA_BULAN[Number(depan.slice(5)) - 1] + ', dibulatkan ke karung penuh · rupiah = perkiraan dengan harga beli terakhir',
    kalimat: !nHari ? 'Belum ada bulan selesai yang tercatat — rencana belum bisa dihitung' : total.karung ? 'Rencana beli ' + sgNamaBulan(depan) + ': ' + ANGKA(total.karung) + ' karung · ' + KG(total.kg) + ' · ±' + RP(total.rp) + ' (' + total.merek + ' merek)' : 'Stok sekarang cukup untuk ' + sgNamaBulan(depan) + ' menurut rata-rata pemakaian' };
}

// ==================== B51 · STOK YANG SUDAH DIPESAN (pesanan pelanggan belum jadi nota) ====================
/** Per barang: kg / unit yang dipesan (pesanan belum tuntas, baris katalog), nilai MODAL di buku (karung hppTerakhirPerKg, kemasan hppRataRataPerUnit = neraca),
 *  sisa buku, kurang; nilai jual perkiraan pesanan; pesanan tanpa barang katalog disebut (tidak bisa dinilai). Literan wadah dinilai dari bukunya bila ada. */
export function sgPesananRp(kini) {
  const K = ingatStokKarung(); const M = ingatStokKemasan(); const per = {}; let nPesanan = 0, nTanpa = 0, rpJual = 0;
  (ambilPesanan() || []).forEach((p) => { if (!p || !pesananBelumTuntas(p)) return; nPesanan += 1; rpJual += Number(p.nilaiPerkiraan) || 0; const baris = poBarisSah(p.baris); if (!baris.length) { nTanpa += 1; return; }
    baris.forEach((b) => { const kem = b.jalur === 'kemasan'; const kunci = (kem ? 'kemasan|' : 'karung|') + b.kunci; const st = kem ? M[b.kunci] : K[b.kunci];
      const x = per[kunci] || (per[kunci] = { kunci, nama: kem ? (st ? st.namaProduk + ' ' + String(st.ukuranKemasan).replace('.', ',') + ' kg' : b.nama) : b.kunci, satuan: kem ? 'unit' : 'kg', jumlah: 0, pesanan: [], dikenal: !!st,
        sisa: st ? (kem ? Number(st.sisaUnit) || 0 : sgB2(st.sisaKg)) : null, modal: st ? (kem ? Number(st.hppRataRataPerUnit) || 0 : Number(st.hppTerakhirPerKg) || 0) : 0 });
      x.jumlah += kem ? Number(b.jumlah) || 0 : Number(b.kg) || 0; const nm = p.namaPelanggan || 'pesanan'; if (x.pesanan.indexOf(nm) < 0) x.pesanan.push(nm); }); });
  const daftar = Object.keys(per).map((k) => { const x = per[k]; return Object.assign(x, { jumlah: sgB2(x.jumlah), rp: Math.round(x.jumlah * x.modal), kurang: x.sisa === null ? null : sgB2(Math.max(0, x.jumlah - x.sisa)) }); })
    .sort((a, b) => b.rp - a.rp || a.nama.localeCompare(b.nama));
  const rp = daftar.reduce((a, x) => a + x.rp, 0); const kg = sgB2(daftar.filter((x) => x.satuan === 'kg').reduce((a, x) => a + x.jumlah, 0)); const unit = daftar.filter((x) => x.satuan === 'unit').reduce((a, x) => a + x.jumlah, 0);
  const kurang = daftar.filter((x) => x.kurang > 0);
  return { nPesanan, nTanpa, daftar, rp, rpJual, kg, unit, kurang,
    kalimat: !nPesanan ? 'Tidak ada pesanan pelanggan yang menunggu' : 'Dipesan ' + (kg ? KG(kg) : '') + (kg && unit ? ' + ' : '') + (unit ? ANGKA(unit) + ' kemasan' : '') + (kg || unit ? ' · modal ' + RP(rp) : '') + ' · ' + nPesanan + ' pesanan' + (nTanpa ? ' (' + nTanpa + ' tanpa barang katalog — tidak bisa dinilai)' : '') + (kurang.length ? ' · ' + kurang.length + ' barang KURANG di buku' : ''),
    sumber: 'Jual › Pesanan', tujuan: { ke: 'jual', lembar: 'pesanan' } };
}

// ==================== B72 · PRODUKSI PER BULAN + RENCANA PRODUKSI (+ A50 sampel isi & oplos) ====================
// Baris yang BUKAN pengemasan — aturan yang SAMA dengan kemasRentang (Laporan › Pondasi): adukan jadi karung utuh, takar ke wadah, beli jadi, stok awal, pindahan awal.
const sgBarisKemas = (pr) => !pr.jadiKarungUtuh && !pr.dariTakar && !pr.beliJadi && !pr.stokAwal && !pr.pindahAwalWadah && (Number(pr.jumlahUnit) || 0) > 0 && (Number(pr.ukuranKemasan) || 0) > 0;
/** Satu bulan ('YYYY-MM'; bulan berjalan = sampai hari ini): angka kemasRentang + tiap adukan (kg bahan → jadi, susut %, kantong, upah, sampel isi, oplos, lebih berat). */
export function sgProduksiBulan(key, kini) {
  const hari = hariIniIso(kini); const awal = key + '-01'; const akhir = sgAkhirBulan(key) < hari ? sgAkhirBulan(key) : hari; const R = kemasRentang(awal, akhir); const kel = {};
  ambilProduksiBerlaku().forEach((pr) => { const t = pr.tanggal || ''; if (t < awal || t > akhir || !sgBarisKemas(pr)) return; const k = String(pr.batchProduksi || pr.id);
    const g = kel[k] || (kel[k] = { batch: k, tanggal: t, jam: String(pr.jam || '').slice(0, 5), jenis: jenisProduksi(pr), kgBahan: 0, kgJadi: 0, kantongRp: 0, upahRp: 0, hasil: [], bahan: [], sampel: [], oplos: null });
    const unit = Number(pr.jumlahUnit) || 0, uk = Number(pr.ukuranKemasan) || 0; g.kgJadi += unit * uk; g.kgBahan += (Number(pr.kgDipakai) || 0) + (Number(pr.kgKemasanDipakai) || 0);
    g.kantongRp += Number(pr.biayaKemasan) || 0; g.upahRp += Number(pr.upahRepacking) || 0; g.hasil.push(unit + ' × ' + (pr.namaProduk || '') + ' ' + String(uk).replace('.', ',') + ' kg');
    (pr.sumberList || []).forEach((s) => { if (s && s.merk) g.bahan.push(KG(s.kg || 0) + ' ' + s.merk); }); (pr.sumberKemasanList || []).forEach((s) => { if (s && s.namaProduk) g.bahan.push((s.unit || 0) + ' × ' + s.namaProduk + ' ' + String(s.ukuranKemasan).replace('.', ',') + ' kg'); });
    const S = pr.sampelIsi; if (S && Number(S.unit) > 0 && Number(S.kg) > 0) { const rata = Number(S.kg) / Number(S.unit); g.sampel.push({ nama: (pr.namaProduk || '') + ' ' + String(uk).replace('.', ',') + ' kg', ukuran: uk, unit: Number(S.unit), kg: Number(S.kg), rata, kurang: rata < uk - 0.005, persen: Math.round((rata - uk) / uk * 1000) / 10 }); }
    if (pr.oplos && typeof pr.oplos === 'object') g.oplos = { teks: String(pr.oplos.teks || ''), alasan: String(pr.oplos.alasan || '') }; });
  const daftar = Object.keys(kel).map((k) => { const g = kel[k]; g.kgBahan = sgB2(g.kgBahan); g.kgJadi = sgB2(g.kgJadi); g.susutKg = sgB2(g.kgBahan - g.kgJadi); g.susutPersen = g.kgBahan > 0 ? Math.round(g.susutKg / g.kgBahan * 1000) / 10 : null;
    g.lebihBerat = g.kgBahan > 0 && g.kgJadi > g.kgBahan + 0.0005; g.kurangIsi = g.sampel.filter((x) => x.kurang).length; g.bahanTeks = g.bahan.join(' + ') || (g.jenis === 'rework' ? 'dari karantina' : '—'); g.hasilTeks = g.hasil.join(' + ');
    g.awas = g.lebihBerat || !!g.oplos || g.kurangIsi > 0; return g; }).sort(sgUrut);
  const kgBahan = sgB2(R.kgBahan), kgJadi = sgB2(R.kg); const susutKg = sgB2(kgBahan - kgJadi);
  // penjaga: Σ per adukan = kemasRentang (Laporan › Pondasi) rentang yang sama — satu sumber
  const menutup = Math.abs(daftar.reduce((a, g) => a + g.kgJadi, 0) - R.kg) < 0.01 && Math.abs(daftar.reduce((a, g) => a + g.kgBahan, 0) - R.kgBahan) < 0.01;
  const sampel = daftar.reduce((a, g) => a.concat(g.sampel), []);
  return { key, nama: sgNamaBulan(key), awal, akhir, berjalan: akhir < sgAkhirBulan(key), adukan: R.adukan, kgBahan, kgJadi, susutKg, susutPersen: kgBahan > 0 ? Math.round(susutKg / kgBahan * 1000) / 10 : null,
    kantongRp: R.kantongRp, upahRp: R.upahRp, biayaPerKg: kgJadi > 0 ? (R.kantongRp + R.upahRp) / kgJadi : null, perUkuran: R.perUkuran, daftar, menutup,
    tanda: { lebihBerat: daftar.filter((g) => g.lebihBerat).length, oplos: daftar.filter((g) => g.oplos).length, kurangIsi: sampel.filter((x) => x.kurang).length, sampel: sampel.length, adukanBersampel: daftar.filter((g) => g.sampel.length).length },
    sumber: 'Stok › Produksi', tujuan: { ke: 'stok', tab: 'produksi' } };
}
/** Deret n bulan terakhir (bulan ini ikut, sampai hari ini) — bulan sebelum catatan pertama toko = 'sebelum'. */
export function sgProduksiDeret(kini, n) {
  const key = hariIniIso(kini).slice(0, 7); const pertama = catatanPertama() || ''; const out = [];
  for (let i = (Number(n) || 6) - 1; i >= 0; i--) { const k = sgGeserBulan(key, -i); if (pertama && sgAkhirBulan(k) < pertama) { out.push({ key: k, nama: sgNamaBulan(k), sebelum: true }); continue; } out.push(sgProduksiBulan(k, kini)); }
  return out;
}
/**
 * Rencana produksi (B72 — "work order" sederhana, dihitung, tidak disimpan): kemasan yang pernah DIADUK sendiri (90 hari terakhir) & hampir habis — "aduk N unit"
 * aturan yang SAMA dengan Stok › Gudang (laju 14 hari × HARI_TARGET − sisa, bila habis ≤ HARI_TARGET hari), + bahan yang biasa dipakai (adukan terakhir hasil itu) dengan
 * sisa bukunya, kg bahan perkiraan (kg jadi ÷ (1 − susut adukan terakhir)), kantong yang biasa dipakai & sisanya.
 */
export function sgRencanaProduksi(kini) {
  const hari = hariIniIso(kini); const dari = sgGeser(hari, -89); const terakhir = {};
  ambilProduksiBerlaku().forEach((pr) => { if ((pr.tanggal || '') < dari || !sgBarisKemas(pr) || jenisProduksi(pr) !== 'adukan') return; const k = kunciKemasan(pr.namaProduk, pr.ukuranKemasan);
    const lama = terakhir[k]; if (!lama || String(pr.tanggal + ' ' + (pr.jam || '')) > String(lama.tanggal + ' ' + (lama.jam || ''))) terakhir[k] = pr; });
  const batch = {}; ambilProduksiBerlaku().forEach((pr) => { const b = String(pr.batchProduksi || pr.id); (batch[b] = batch[b] || []).push(pr); });
  const K = ingatStokKarung(); const B = hitungStokBahanKemasan();
  const daftar = daftarBarang().filter((b) => b.jenis === 'kemasan' && terakhir[b.kunci] && b.laju > 0 && b.hariHabis !== null && b.hariHabis <= HARI_TARGET).map((b) => {
    const pr = terakhir[b.kunci]; const unit = Math.ceil(Math.max(0, b.laju * HARI_TARGET - b.sisa)); const uk = Number(pr.ukuranKemasan) || 0; const sekumpul = batch[String(pr.batchProduksi || pr.id)] || [pr];
    const bahanKg = sekumpul.reduce((a, x) => a + (Number(x.kgDipakai) || 0) + (Number(x.kgKemasanDipakai) || 0), 0); const jadiKg = sekumpul.reduce((a, x) => a + (Number(x.jumlahUnit) || 0) * (Number(x.ukuranKemasan) || 0), 0);
    const susut = bahanKg > 0 && jadiKg > 0 ? Math.max(0, (bahanKg - jadiKg) / bahanKg) : 0; const kgJadi = unit * uk; const kgBahan = susut < 0.5 ? kgJadi / (1 - susut) : kgJadi;
    const sumber = (sekumpul.find((x) => Array.isArray(x.sumberList) && x.sumberList.length) || {}).sumberList || []; const jumlahSumber = sumber.reduce((a, s) => a + (Number(s.kg) || 0), 0);
    const bahan = sumber.filter((s) => s && s.merk).map((s) => ({ merk: s.merk, kg: sgB2(jumlahSumber > 0 ? kgBahan * (Number(s.kg) || 0) / jumlahSumber : 0), sisa: K[s.merk] ? sgB2(K[s.merk].sisaKg) : null }));
    const kj = pr.kantongJenis || ''; return { kunci: b.kunci, nama: b.nama, ukuran: uk, sisa: b.sisa, laju: b.laju, hariHabis: Math.max(0, b.hariHabis), unit, kgJadi: sgB2(kgJadi), kgBahan: sgB2(kgBahan), susutPersen: Math.round(susut * 1000) / 10,
      bahan, bahanKurang: bahan.filter((x) => x.sisa !== null && x.sisa < x.kg).map((x) => x.merk), kantong: kj ? { jenis: kj, label: LABEL_BAHAN_KEMASAN[kj] || kj, sisa: (B[kj] || {}).sisaPcs || 0, kurang: ((B[kj] || {}).sisaPcs || 0) < unit } : null,
      terakhir: pr.tanggal || '' }; }).filter((x) => x.unit > 0).sort((a, b) => a.hariHabis - b.hariHabis || a.nama.localeCompare(b.nama));
  return { hari, targetHari: HARI_TARGET, daftar, kgJadi: sgB2(daftar.reduce((a, x) => a + x.kgJadi, 0)), kgBahan: sgB2(daftar.reduce((a, x) => a + x.kgBahan, 0)),
    kalimat: daftar.length ? 'Perlu diaduk: ' + daftar.slice(0, 3).map((x) => x.unit + ' × ' + x.nama).join(' · ') + (daftar.length > 3 ? ' + ' + (daftar.length - 3) + ' lagi' : '') : 'Tidak ada kemasan yang perlu diaduk untuk ' + HARI_TARGET + ' hari ke depan',
    rumus: 'aduk N unit = laju jual 14 hari × ' + HARI_TARGET + ' hari − sisa (sama dengan Stok › Gudang), hanya kemasan yang diaduk sendiri 90 hari terakhir · bahan = campuran adukan terakhir hasil itu, kg bahan memperhitungkan susut adukan terakhirnya' };
}
