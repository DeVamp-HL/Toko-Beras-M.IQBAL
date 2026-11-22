// RIWAYAT & BATAL — BARANG (owner 22 Nov 2026, paket riwayat & pembatalan tahap 2). Logika tanpa DOM & tanpa Firebase; awalan rb. Dijaga alat-uji/uji_riwayat_barang.py.
// Bentuk sama dengan tahap 1 uang (riwayat-uang-logika.js): membatalkan = catatan aslinya DIHAPUS dari buku (mesin stok beku tidak diubah: yang tidak ada tidak
// dihitung) dan SALINAN UTUHNYA disimpan di bukuHapus (jenisBatal 'barang') bersama alasan & koreksi; pulihkan = salinan ditulis kembali (id sama), koreksi dibalik.
//
// Keputusan owner 22 Nov 2026 (tahap 2):
//  (1) isi ulang wadah dibatalkan = SELURUH ketukan itu: karung yang dibuka dari tumpukan gudang balik ke tumpukan, tuangnya batal, karung bekas yang lahir di
//      situ ikut hilang. Satu ketukan = satu KIRIMAN: catatan-catatannya bertanggal & bermenit sama dan bernomor Date.now()+acak berurutan (selisih < 3 detik)
//      — kelompok dicari lewat kolom penghubung (takarId / produksiId / bukaKarung / dariWadah / dariId) DI DALAM kiriman yang sama.
//  (2) barang yang SUDAH DIHITUNG sesudah catatan yang dibatalkan (cocokkan, timbang tutup hari, bongkar wadah, karung habis): selisih hitungan BERIKUTNYA per
//      buku digeser sebesar catatan itu (kgSistem ikut, kgFisik tetap, nilai = selisih × modal per kg saat hitungan) — stok tetap = hitungan fisik dan susut /
//      lebih tidak menghitung salah catatnya dua kali (pola tutup hari di Uang). Jejak di koreksiBatal hitungan itu. Tanpa hitungan sesudahnya: bukunya saja
//      yang bergeser (boleh minus — tidak dijepit diam-diam; disebut di akibat).
//  (3) cocokkan dibatalkan PER BARANG: tumpukan satu merek, satu kemasan, satu kantong, satu wadah (penyesuaian + titik isi), satu karung terbuka (penyesuaian
//      + catatan isi + karung bekasnya).
// TIDAK lewat sini (disebut sebabnya di baris): kedatangan (Stok › Barang masuk: koreksi/hapus), adukan (Stok › Adukan), timbang tutup hari (tutup ulang),
// rework karantina, aktivasi wadah, pindah buku ganti nama / gabung / pisah ukuran, setelan wadah & nilai karung bekas (tahap 3), beli kantong. Bulan terkunci
// = ditolak. Batas yang diketahui: karung bekas hari yang sama yang DIHAPUS oleh kiriman (karung "ternyata belum habis") tidak bisa dikembalikan dari sini.
import { cacheMentah, ambilWadahLiteran, ambilProduksi, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilBahanLiteran, ambilBahanKemasan, ambilSemuaBatch, tolakKunci } from '../data/toko.js';
import { hitungStokKarungPerMerk } from '../mesin/beku.js';
import { kunciKemasan } from '../mesin/pembantu.js';
import { tanggalPendek, RP } from '../inti/format.js';
import { hitunganFisik } from './jual-logika.js';
import { petaTempat } from './stok-tempat-logika.js';
import { ssStokLokasi } from './sistem-logika.js';

const rbJam = (j) => String(j || '').slice(0, 5);
const rbB2 = (n) => Math.round((Number(n) || 0) * 100) / 100;
const rbAngka = (n) => String(rbB2(Math.abs(n))).replace('.', ',');
const rbNo = (id) => { const n = Number(id); return isFinite(n) && String(id).trim() !== '' ? n : null; };
/** Dua catatan lahir dari SATU ketukan (satu kiriman): tanggal & menit sama, nomor berselisih < 3 detik. */
const rbSeKiriman = (a, b) => { if (!a || !b || String(a.tanggal || '') !== String(b.tanggal || '') || rbJam(a.jam) !== rbJam(b.jam)) return false; const x = rbNo(a.id), y = rbNo(b.id); return x !== null && y !== null && Math.abs(x - y) < 3000; };
const rbUrut = (d) => String(d.tanggal || '') + ' ' + rbJam(d.jam);
/** d tercatat SESUDAH acuan (menit lebih akhir; menit sama → nomor lebih besar). */
const rbSesudah = (d, acuan) => { const a = rbUrut(d), b = rbUrut(acuan); if (a !== b) return a > b; const x = rbNo(d.id), y = rbNo(acuan.id); return x !== null && y !== null && x > y; };

const RB_AMBIL = {
  wadahLiteran: () => ambilWadahLiteran() || [], produksiKemasan: () => ambilProduksi() || [], penyesuaianStok: () => ambilPenyesuaianStok() || [],
  penyesuaianKemasan: () => ambilPenyesuaianKemasan() || [], stokBahanLiteran: () => ambilBahanLiteran() || [], stokBahanKemasan: () => ambilBahanKemasan() || [],
  pindahTempat: () => cacheMentah('pindahTempat') || [], pindahStok: () => cacheMentah('pindahStok') || [], batchMasuk: () => ambilSemuaBatch() || [],
};
export const RB_KOLEKSI = Object.keys(RB_AMBIL);
const rbCari = (koleksi, id) => (RB_AMBIL[koleksi] ? RB_AMBIL[koleksi]() : []).find((d) => String(d.id) === String(id)) || null;

// ---------- pengaruh ke buku (arah MAJU: apa yang dilakukan catatan itu ke stok) ----------
// buku: 'K|<nama buku karung/wadah>' kg · 'P|<kunci kemasan>' unit · 'BL|<jenis>' / 'BK|<jenis>' lembar (bahan literan / bahan kemasan)
const rbBukuKemasan = (n, u) => 'P|' + kunciKemasan(n, u);
const rbBukuBahan = (koleksi, j) => (koleksi === 'stokBahanLiteran' ? 'BL|' : 'BK|') + String(j || '');
/** Rumus mesin beku (hitungStokKarungPerMerk / kemasan / bahan): pindah buku = sumber −kg, tujuan +ukuran×unit; penyesuaian = +selisih; opname bahan = +jumlah. */
export function rbPengaruh(koleksi, d) {
  const e = {}; const t = (k, n) => { if (!k || !n) return; e[k] = rbB2((e[k] || 0) + n); };
  if (koleksi === 'produksiKemasan' && d.jadiKarungUtuh) {
    if (Array.isArray(d.sumberList) && d.sumberList.length) d.sumberList.forEach((s) => { if (s && s.merk) t('K|' + s.merk, -(Number(s.kg) || 0)); });
    else if (d.merkSumber) t('K|' + d.merkSumber, -(Number(d.kgDipakai) || 0));
    if (d.merkTujuan) t('K|' + d.merkTujuan, (Number(d.ukuranKemasan) || 0) * (Number(d.jumlahUnit) || 0));
  } else if (koleksi === 'penyesuaianStok' && d.merk) t('K|' + d.merk, Number(d.selisihKg) || 0);
  else if (koleksi === 'penyesuaianKemasan') t(rbBukuKemasan(d.namaProduk, d.ukuranKemasan), Number(d.selisihUnit) || 0);
  else if ((koleksi === 'stokBahanLiteran' || koleksi === 'stokBahanKemasan') && d.tipe === 'opname') t(rbBukuBahan(koleksi, d.jenis), Number(d.jumlah) || 0);
  return e;
}
const rbJumlahPengaruh = (A) => { const e = {}; A.forEach((x) => { const p = rbPengaruh(x.koleksi, x.data); Object.keys(p).forEach((k) => { e[k] = rbB2((e[k] || 0) + p[k]); }); }); Object.keys(e).forEach((k) => { if (Math.abs(e[k]) < 0.005) delete e[k]; }); return e; };
const rbNamaBuku = (bk) => { const i = bk.indexOf('|'); const j = bk.slice(0, i), n = bk.slice(i + 1); return j === 'BL' && n === 'karungbekas' ? 'karung bekas' : n; };
const rbSatuan = (bk) => (/^K\|/.test(bk) ? 'kg' : /^P\|/.test(bk) ? 'unit' : 'lembar');
const rbTeksJumlah = (bk, n) => (n > 0 ? '+' : '−') + rbAngka(n) + ' ' + rbSatuan(bk);
export const rbTeksPengaruh = (e) => Object.keys(e).sort().map((k) => rbNamaBuku(k) + ' ' + rbTeksJumlah(k, e[k])).join(' · ');

// ---------- hitungan fisik per buku (yang digeser bila catatan sebelumnya dibatalkan) ----------
function rbHitunganBuku(bk) {
  const i = bk.indexOf('|'); const j = bk.slice(0, i), n = bk.slice(i + 1);
  if (j === 'K') return RB_AMBIL.penyesuaianStok().filter((d) => String(d.merk || '') === n && hitunganFisik(d)).map((d) => ({ koleksi: 'penyesuaianStok', data: d }));
  if (j === 'P') return RB_AMBIL.penyesuaianKemasan().filter((d) => rbBukuKemasan(d.namaProduk, d.ukuranKemasan) === bk).map((d) => ({ koleksi: 'penyesuaianKemasan', data: d }));
  const koleksi = j === 'BL' ? 'stokBahanLiteran' : 'stokBahanKemasan';
  return RB_AMBIL[koleksi]().filter((d) => d.tipe === 'opname' && String(d.jenis || '') === n && !d.lahirKarungBekas && !d.nilaiKarungBekas && d.pcsFisik !== undefined && d.pcsFisik !== null).map((d) => ({ koleksi, data: d }));
}
/** Hitungan x sesudah selisihnya digeser +geser (sistem −geser, fisik tetap, nilai = selisih × modal per satuan saat hitungan) + jejak. */
function rbGeserHitungan(x, geser, jejak) {
  const d = Object.assign({}, x.data); const per = (lama, rp, simpan) => Math.abs(Number(simpan) || (lama ? (Number(rp) || 0) / lama : 0));
  if (x.koleksi === 'penyesuaianStok') { const lama = Number(d.selisihKg) || 0; const hpp = per(lama, d.nilaiRp, d.hppPerKgSaatOpname); d.selisihKg = rbB2(lama + geser);
    if (typeof d.kgSistem === 'number') d.kgSistem = rbB2(d.kgSistem - geser); if (d.nilaiRp !== undefined) d.nilaiRp = Math.round(d.selisihKg * hpp); }
  else if (x.koleksi === 'penyesuaianKemasan') { const lama = Number(d.selisihUnit) || 0; const hpp = per(lama, d.nilaiRp, d.hppPerUnitSaatOpname); d.selisihUnit = rbB2(lama + geser);
    if (typeof d.unitSistem === 'number') d.unitSistem = rbB2(d.unitSistem - geser); if (d.nilaiRp !== undefined) d.nilaiRp = Math.round(d.selisihUnit * hpp); }
  else { const lama = Number(d.jumlah) || 0; const hpp = per(lama, d.nilaiRp, d.hargaPerPcsSaatOpname); d.jumlah = rbB2(lama + geser);
    if (typeof d.pcsSistem === 'number') d.pcsSistem = rbB2(d.pcsSistem - geser); if (d.nilaiRp !== undefined) d.nilaiRp = Math.round(d.jumlah * hpp); }
  d.koreksiBatal = (Array.isArray(x.data.koreksiBatal) ? x.data.koreksiBatal : []).concat([jejak]);
  return { koleksi: x.koleksi, data: d };
}
const rbSelisih = (x) => Number(x.koleksi === 'penyesuaianStok' ? x.data.selisihKg : x.koleksi === 'penyesuaianKemasan' ? x.data.selisihUnit : x.data.jumlah) || 0;
// kolom yang digeser per jenis hitungan — disimpan di jejak (sebelum) supaya pulihkan mengembalikan angka ASLINYA persis (nilai FIFO tidak dihitung ulang)
const RB_KOLOM = { penyesuaianStok: ['selisihKg', 'kgSistem', 'nilaiRp'], penyesuaianKemasan: ['selisihUnit', 'unitSistem', 'nilaiRp'], stokBahanLiteran: ['jumlah', 'pcsSistem', 'nilaiRp'], stokBahanKemasan: ['jumlah', 'pcsSistem', 'nilaiRp'] };
const rbAmbilKolom = (x) => { const o = {}; (RB_KOLOM[x.koleksi] || []).forEach((k) => { if (x.data[k] !== undefined) o[k] = x.data[k]; }); return o; };
/**
 * Koreksi saat kelompok A (kepala = A[0]) DIBATALKAN (arah −1) atau DIPULIHKAN (+1): tiap buku yang tersentuh → hitungan fisik PERTAMA sesudah kepala
 * (di luar kelompok) digeser. e = pengaruh maju kelompok (pulihkan: dari salinannya). → { dokumen, akibat, geser: [{koleksi, id, buku, geser}] }
 */
function rbKoreksi(A, e, arah, idBatal, kini) {
  const kepala = A[0].data; const anggota = {}; A.forEach((x) => { anggota[x.koleksi + '|' + x.data.id] = true; });
  const dokumen = []; const akibat = []; const geserDaftar = []; const stok = hitungStokKarungPerMerk();
  Object.keys(e).sort().forEach((bk) => {
    const geser = arah < 0 ? e[bk] : -e[bk];   // selisih hitungan berikutnya += pengaruh maju yang hilang (batal) / −= pengaruh yang kembali (pulihkan)
    const H = rbHitunganBuku(bk).filter((x) => !anggota[x.koleksi + '|' + x.data.id] && rbSesudah(x.data, kepala)).sort((a, b) => rbUrut(a.data).localeCompare(rbUrut(b.data)) || (rbNo(a.data.id) || 0) - (rbNo(b.data.id) || 0));
    if (!H.length) {
      const buku = /^K\|/.test(bk) && stok[rbNamaBuku(bk)] ? rbB2(stok[rbNamaBuku(bk)].sisaKg || 0) : null; const sesudah = buku === null ? null : rbB2(buku - geser);
      akibat.push('Buku ' + rbNamaBuku(bk) + ' ' + rbTeksJumlah(bk, -geser) + (buku === null ? '' : ' (' + rbAngka(buku) + ' → ' + (sesudah < 0 ? '−' : '') + rbAngka(sesudah) + ' kg' + (sesudah < -0.004 ? ', MINUS — cocokkan sesudahnya' : '') + ')'));
      return;
    }
    const h = H[0]; const jejak = { batal: String(idBatal), geser, arah: arah < 0 ? 'batal' : 'pulih', pada: kini, sebelum: rbAmbilKolom(h) };
    // pulihkan: hitungan yang dulu digeser pembatalan INI dan belum berubah sesudahnya → angka aslinya dikembalikan persis
    const dulu = arah > 0 ? (Array.isArray(h.data.koreksiBatal) ? h.data.koreksiBatal : []).filter((j) => j && j.batal === String(idBatal) && j.arah === 'batal' && j.sebelum && j.sesudah).pop() : null;
    const persis = dulu && Object.keys(dulu.sesudah).every((k) => h.data[k] === dulu.sesudah[k]);
    const kembali = () => { const o = Object.assign({}, h.data); (RB_KOLOM[h.koleksi] || []).forEach((k) => { delete o[k]; }); return Object.assign(o, dulu.sebelum, { koreksiBatal: h.data.koreksiBatal.concat([jejak]) }); };
    const baru = persis ? { koleksi: h.koleksi, data: kembali() } : rbGeserHitungan(h, geser, jejak);
    if (!persis) jejak.sesudah = rbAmbilKolom(baru);
    dokumen.push(baru); geserDaftar.push({ koleksi: h.koleksi, id: String(h.data.id), buku: bk, geser });
    akibat.push('Hitungan ' + tanggalPendek(h.data.tanggal) + ' ' + rbJam(h.data.jam) + ' · ' + rbNamaBuku(bk) + ': selisih ' + rbTeksJumlah(bk, rbSelisih(h)).replace(/^\+0 |^−0 /, '0 ') + ' → '
      + (Math.abs(rbSelisih(baru)) < 0.005 ? '0' : rbTeksJumlah(bk, rbSelisih(baru))) + ' (' + (h.data.nilaiRp !== undefined ? 'nilai ' + RP(Number(h.data.nilaiRp) || 0) + ' → ' + RP(Number(baru.data.nilaiRp) || 0) + '; ' : '') + 'stok tetap = hitungan fisik)');
  });
  return { dokumen, akibat, geser: geserDaftar };
}

// ---------- kelompok per hari: satu baris = satu ketukan ----------
const RB_SEBAB = {
  kedatangan: 'kedatangan — koreksi / hapus di Stok › Barang masuk', adukan: 'adukan / produksi — koreksi / hapus di Stok › Adukan',
  tutup: 'timbang tutup hari — betulkan lewat tutup ulang (Uang › Tutup hari)', rework: 'rework karantina / penyesuaian sistem — lewat Stok › Karantina',
  aktivasi: 'aktivasi wadah (pindahan awal ke stok wadah) — tidak dibatalkan', pindahBuku: 'pindah buku (ganti nama / gabung / pisah ukuran / karung tertinggal) — tidak dibatalkan di sini',
  setelan: 'setelan — riwayatnya menyusul (tahap 3, lihat saja)', karungBekas: 'karung bekas lahir — ikut catatan asalnya', beli: 'beli kantong / bahan — hapus di Stok › Kantong',
  tempatDihapus: 'tempatnya dihapus dari daftar tempat — atur di Stok › Tempat simpan',
};
function rbSusunHari(iso) {
  const H = {}; RB_KOLEKSI.forEach((k) => { H[k] = RB_AMBIL[k]().filter((d) => String(d.tanggal || '') === iso); });
  const diambil = {}; const kk = (k, d) => k + '|' + d.id; const bebas = (k, d) => !diambil[kk(k, d)];
  const ambil = (k, d) => { diambil[kk(k, d)] = true; return { koleksi: k, data: d }; };
  const out = []; const tambah = (jenis, A, sebab) => out.push({ jenis, anggota: A, sebab: sebab || '' });
  const wl = H.wadahLiteran, pr = H.produksiKemasan, py = H.penyesuaianStok, bl = H.stokBahanLiteran;
  const kbDari = (ids) => bl.filter((b) => bebas('stokBahanLiteran', b) && b.jenis === 'karungbekas' && b.dariId !== undefined && ids.indexOf(String(b.dariId)) >= 0);
  const kbKolam = (merk, acuan) => bl.filter((b) => bebas('stokBahanLiteran', b) && b.jenis === 'karungbekas' && b.lahirKarungBekas && String(b.kolam || '') === String(merk) && rbSeKiriman(b, acuan));
  const pindah = (acuan, syarat) => pr.filter((p) => bebas('produksiKemasan', p) && p.jadiKarungUtuh && p.dariTakar && rbSeKiriman(p, acuan) && syarat(p));
  const karung = (acuan, syarat) => wl.filter((k) => bebas('wadahLiteran', k) && k.tipe === 'karung' && rbSeKiriman(k, acuan) && syarat(k));

  // aktivasi wadah (pindahan awal): seluruh kirimannya dikunci (tampil, tidak dibatalkan)
  wl.filter((d) => d.pindahAwal && bebas('wadahLiteran', d)).forEach((d) => { if (!bebas('wadahLiteran', d)) return; const A = [ambil('wadahLiteran', d)];
    wl.forEach((x) => { if (bebas('wadahLiteran', x) && x.pindahAwal && rbSeKiriman(x, d)) A.push(ambil('wadahLiteran', x)); });
    pindah(d, () => true).forEach((p) => A.push(ambil('produksiKemasan', p))); tambah('aktivasi', A, RB_SEBAB.aktivasi); });
  // isi ulang / takar / tuang balik: takar + pindah bukunya + karung yang dibuka di ketukan itu (+ pindah bukunya) + karung bekas yang lahir
  wl.filter((d) => d.tipe === 'takar' && bebas('wadahLiteran', d)).forEach((T) => {
    const A = [ambil('wadahLiteran', T)]; const W = String(T.wadah || ''); const asal = (T.sumber || []).map((s) => String((s && (s.merkAsal || s.merk)) || ''));
    const ids = [];
    pindah(T, (p) => String(p.takarId || '') === String(T.id) || String(T.produksiId || '') === String(p.id) || (!!p.bukaKarung && String(p.bukaKarung) === W && asal.indexOf(String(p.merkAsal || '')) >= 0))
      .forEach((p) => { A.push(ambil('produksiKemasan', p)); ids.push(String(p.id)); });
    karung(T, (k) => (k.produksiId !== undefined && ids.indexOf(String(k.produksiId)) >= 0) || (!!k.otomatis && (String(k.wadah || '') === W || asal.indexOf(String(k.merk || '')) >= 0))).forEach((k) => A.push(ambil('wadahLiteran', k)));
    kbDari([String(T.id)].concat(A.filter((x) => x.koleksi === 'wadahLiteran').map((x) => String(x.data.id)))).forEach((b) => A.push(ambil('stokBahanLiteran', b)));
    tambah(T.tuangBalik ? 'tuangBalik' : 'takar', A);
  });
  // bongkar wadah: titik isi 0 + penyesuaian susut/lebih + pindah ke karung wadah + catatan karungnya
  wl.filter((d) => d.tipe === 'isi' && d.bongkar && bebas('wadahLiteran', d)).forEach((I) => { const W = String(I.wadah || ''); const A = [ambil('wadahLiteran', I)];
    py.forEach((p) => { if (bebas('penyesuaianStok', p) && p.bongkar && String(p.wadah || '') === W && rbSeKiriman(p, I)) A.push(ambil('penyesuaianStok', p)); });
    pindah(I, (p) => String(p.bongkarWadah || '') === W).forEach((p) => A.push(ambil('produksiKemasan', p)));
    karung(I, (k) => !!k.bongkar && String(k.dariWadah || '') === W).forEach((k) => A.push(ambil('wadahLiteran', k)));
    tambah('bongkar', A); });
  // cek wadah (dikosongkan = sisih seluruh isi ikut)
  wl.filter((d) => d.tipe === 'cek' && bebas('wadahLiteran', d)).forEach((C) => { const W = String(C.wadah || ''); const A = [ambil('wadahLiteran', C)];
    if (C.hasil === 'kosong') { pindah(C, (p) => String(p.sisihWadah || '') === W).forEach((p) => A.push(ambil('produksiKemasan', p)));
      karung(C, (k) => !!k.sisih && String(k.dariWadah || '') === W).forEach((k) => A.push(ambil('wadahLiteran', k))); }
    tambah('cek', A); });
  // sisihkan ke karung wadah
  pr.filter((p) => p.sisihWadah && bebas('produksiKemasan', p)).forEach((S) => { const W = String(S.sisihWadah); const A = [ambil('produksiKemasan', S)];
    karung(S, (k) => !!k.sisih && String(k.dariWadah || '') === W).forEach((k) => A.push(ambil('wadahLiteran', k))); tambah('sisih', A); });
  // buka karung dari tumpukan (tanpa isi ulang): pindah buku + catatan karungnya + karung bekas
  pr.filter((p) => p.bukaKarung && bebas('produksiKemasan', p)).forEach((B) => { const A = [ambil('produksiKemasan', B)];
    karung(B, (k) => String(k.produksiId || '') === String(B.id)).forEach((k) => A.push(ambil('wadahLiteran', k)));
    kbDari(A.filter((x) => x.koleksi === 'wadahLiteran').map((x) => String(x.data.id))).forEach((b) => A.push(ambil('stokBahanLiteran', b))); tambah('buka', A); });
  // cocokkan: karung terbuka dulu (penyesuaian bermerek karung itu), lalu wadah (penyesuaian bagian wadah sisanya)
  wl.filter((d) => d.tipe === 'karungIsi' && d.dariCocok && bebas('wadahLiteran', d)).forEach((KI) => { const A = [ambil('wadahLiteran', KI)];
    py.forEach((p) => { if (bebas('penyesuaianStok', p) && p.bagian === 'wadah' && String(p.merk || '') === String(KI.merk || '') && rbSeKiriman(p, KI)) A.push(ambil('penyesuaianStok', p)); });
    kbKolam(KI.merk, KI).forEach((b) => A.push(ambil('stokBahanLiteran', b))); tambah('cocokKarung', A); });
  wl.filter((d) => d.tipe === 'isi' && d.dariCocok && bebas('wadahLiteran', d)).forEach((I) => { const W = String(I.wadah || ''); const A = [ambil('wadahLiteran', I)];
    py.forEach((p) => { if (bebas('penyesuaianStok', p) && p.bagian === 'wadah' && String(p.wadah || '') === W && rbSeKiriman(p, I)) A.push(ambil('penyesuaianStok', p)); });
    tambah('cocokWadah', A); });
  // karung terbuka: habis / dikembalikan / catat isinya (Jual & Stok) + karung bekas
  wl.filter((d) => d.tipe === 'karungIsi' && bebas('wadahLiteran', d)).forEach((KI) => { const A = [ambil('wadahLiteran', KI)];
    py.forEach((p) => { if (bebas('penyesuaianStok', p) && String(p.merk || '') === String(KI.merk || '') && Number(p.kgFisik) === 0 && rbSeKiriman(p, KI)) A.push(ambil('penyesuaianStok', p)); });
    kbDari([String(KI.id)]).concat(kbKolam(KI.merk, KI)).forEach((b) => { if (bebas('stokBahanLiteran', b)) A.push(ambil('stokBahanLiteran', b)); }); tambah('karungIsi', A); });
  wl.filter((d) => d.tipe === 'karung' && bebas('wadahLiteran', d)).forEach((K) => { const A = [ambil('wadahLiteran', K)];
    kbDari([String(K.id)]).forEach((b) => A.push(ambil('stokBahanLiteran', b))); tambah('karung', A); });
  wl.filter((d) => d.tipe === 'isi' && bebas('wadahLiteran', d)).forEach((I) => tambah('isi', [ambil('wadahLiteran', I)]));
  wl.filter((d) => bebas('wadahLiteran', d)).forEach((d) => tambah('setelan', [ambil('wadahLiteran', d)], RB_SEBAB.setelan));
  // penyesuaian stok sisanya
  py.filter((p) => bebas('penyesuaianStok', p)).forEach((p) => { const sebab = p.dariTutup ? RB_SEBAB.tutup : !hitunganFisik(p) ? RB_SEBAB.rework : '';
    tambah(sebab ? 'penyesuaian' : 'cocokTumpukan', [ambil('penyesuaianStok', p)], sebab); });
  H.penyesuaianKemasan.forEach((p) => tambah('cocokKemasan', [ambil('penyesuaianKemasan', p)]));
  ['stokBahanLiteran', 'stokBahanKemasan'].forEach((k) => H[k].filter((b) => bebas(k, b)).forEach((b) => {
    if (b.tipe === 'opname' && !b.lahirKarungBekas && !b.nilaiKarungBekas) return tambah('cocokBahan', [ambil(k, b)]);
    if (b.lahirKarungBekas) return tambah('karungBekas', [ambil(k, b)], RB_SEBAB.karungBekas);
    if (b.tipe === 'beli') return tambah('beliBahan', [ambil(k, b)], RB_SEBAB.beli);
    if (b.nilaiKarungBekas || b.tipe === 'saldoAwal') return tambah('setelan', [ambil(k, b)], RB_SEBAB.setelan);
  }));
  H.pindahTempat.forEach((p) => tambah('pindahTempat', [ambil('pindahTempat', p)], p.tempatDihapus ? RB_SEBAB.tempatDihapus : ''));
  H.pindahStok.filter((p) => p.tipe === 'keluar').forEach((p) => { const A = [ambil('pindahStok', p)];
    H.pindahStok.forEach((q) => { if (q.tipe === 'masuk' && bebas('pindahStok', q) && String(q.pasangan || '') === String(p.pasangan || p.id)) A.push(ambil('pindahStok', q)); }); tambah('pindahStok', A); });
  H.pindahStok.filter((p) => bebas('pindahStok', p)).forEach((p) => tambah('pindahStok', [ambil('pindahStok', p)]));
  H.batchMasuk.filter((b) => !b.lahirBuku && !b.stokAwal).forEach((b) => tambah('kedatangan', [{ koleksi: 'batchMasuk', data: b }], RB_SEBAB.kedatangan));
  pr.filter((p) => bebas('produksiKemasan', p)).forEach((p) => tambah(p.dariTakar ? 'pindahBuku' : 'adukan', [ambil('produksiKemasan', p)], p.dariTakar ? RB_SEBAB.pindahBuku : RB_SEBAB.adukan));
  return out;
}

// ---------- kalimat ----------
const rbKarungN = (A) => A.filter((x) => x.koleksi === 'wadahLiteran' && x.data.tipe === 'karung').length;
function rbJenis(g) {
  const d = g.anggota[0].data; const W = String(d.wadah || d.sisihWadah || '');
  switch (g.jenis) {
    case 'takar': { const n = rbKarungN(g.anggota); const s = (d.sumber || [])[0] || {}; return 'Isi ulang wadah ' + W + ' · ' + String(s.merkAsal || s.merk || '') + ' ' + rbAngka(d.kg) + ' kg' + (n ? ' (+' + n + ' karung dibuka dari tumpukan)' : ''); }
    case 'tuangBalik': return 'Tuang balik karung sisihan → wadah ' + W + ' · ' + rbAngka(d.kg) + ' kg';
    case 'bongkar': return 'Bongkar wadah ' + W;
    case 'cek': return 'Cek wadah ' + W + ' · ' + (d.hasil === 'sesuai' ? 'sesuai' : d.hasil === 'lupa' ? 'lupa isi ulang' : 'dikosongkan');
    case 'sisih': return 'Sisihkan wadah ' + W + ' → karung sisihan · ' + rbAngka(d.kgDipakai) + ' kg';
    case 'buka': return 'Buka ' + rbKarungN(g.anggota) + ' karung ' + String(d.merkAsal || '') + ' di belakang wadah ' + String(d.bukaKarung || '');
    case 'cocokKarung': return 'Cocokkan karung terbuka ' + String(d.merk || '') + ' · isi ' + rbAngka(d.isiKg) + ' kg';
    case 'cocokWadah': return 'Cocokkan wadah ' + W + ' · isi ' + rbAngka(d.isiKg) + ' kg';
    case 'karungIsi': return (d.selesai ? 'Karung habis · ' : d.dikembalikan ? 'Karung dikembalikan ke tumpukan · ' : 'Catat isi karung · ') + String(d.merk || '') + (d.selesai || d.dikembalikan ? '' : ' ' + rbAngka(d.isiKg) + ' kg');
    case 'karung': return 'Buka karung ' + String(d.merk || '') + (d.wadah ? ' di wadah ' + d.wadah : '') + ' · ' + rbAngka(d.kg) + ' kg';
    case 'isi': return 'Samakan isi wadah ' + W + ' · ' + rbAngka(d.isiKg) + ' kg';
    case 'cocokTumpukan': return 'Cocokkan ' + String(d.merk || '') + (d.bagian === 'tumpukan' ? ' (tumpukan)' : d.bagian === 'wadah' ? ' (wadah ' + String(d.wadah || 'lepas') + ')' : '') + ' · selisih ' + rbTeksJumlah('K|', Number(d.selisihKg) || 0);
    case 'cocokKemasan': return 'Cocokkan kemasan ' + String(d.namaProduk || '') + ' ' + String(d.ukuranKemasan || '').replace('.', ',') + ' kg · selisih ' + rbTeksJumlah('P|', Number(d.selisihUnit) || 0);
    case 'cocokBahan': return 'Cocokkan ' + String(d.jenis || '') + ' · selisih ' + rbTeksJumlah('B|', Number(d.jumlah) || 0);
    case 'pindahTempat': return 'Pindah tempat · ' + String(d.barang || d.kunci || '') + ': ' + (d.dari || 'tanpa tempat') + ' → ' + (d.ke || 'tanpa tempat');
    case 'pindahStok': return 'Pindah stok ' + String(d.merk || '') + ' ' + rbAngka(d.kg) + ' kg: ' + String(d.dari || '') + ' → ' + String(d.ke || '');
    case 'kedatangan': return 'Kedatangan · ' + String(d.pemasok || '') + ' · ' + (d.merkList || []).length + ' baris';
    case 'adukan': return 'Adukan · ' + String(d.namaProduk || d.merkTujuan || '');
    case 'penyesuaian': return 'Penyesuaian ' + String(d.merk || '') + ' · ' + rbTeksJumlah('K|', Number(d.selisihKg) || 0);
    case 'karungBekas': return 'Karung bekas ' + (d.batal ? 'dicabut' : 'lahir') + ' · ' + String(d.merkAsal || '');
    default: return g.jenis === 'aktivasi' ? 'Aktivasi wadah ' + W : g.jenis === 'beliBahan' ? 'Beli ' + String(d.jenis || '') : 'Setelan ' + String(d.tipe || d.jenis || '');
  }
}
function rbBaris(g) {
  const d = g.anggota[0].data; const e = rbJumlahPengaruh(g.anggota);
  return { kunci: 'barang|' + g.anggota[0].koleksi + '|' + String(d.id), koleksi: g.anggota[0].koleksi, id: String(d.id), tanggal: String(d.tanggal || ''), jam: rbJam(d.jam),
    oleh: String(d.oleh || d.diubahOleh || ''), jenis: rbJenis(g), ket: String(d.alasan || d.catatan || d.keterangan || '').slice(0, 80), efek: e, teksEfek: rbTeksPengaruh(e),
    anggota: g.anggota.length - 1, bisa: !g.sebab, sebab: g.sebab };
}
/** Riwayat barang hari `iso` (terbaru di atas). saring = nama orang ('' = semua). */
export function rbDaftar(iso, saring) {
  return rbSusunHari(iso).map(rbBaris).filter((b) => !saring || b.oleh === saring).sort((a, b) => b.jam.localeCompare(a.jam) || (rbNo(b.id) || 0) - (rbNo(a.id) || 0) || b.id.localeCompare(a.id));
}
export const rbOrang = (iso) => rbDaftar(iso, '').map((b) => b.oleh).filter((o, i, a) => o && a.indexOf(o) === i);
/** Kelompok yang dikepalai catatan koleksi|id (dicari di harinya). */
function rbKelompok(koleksi, id) {
  const d = rbCari(koleksi, id); if (!d) return null;
  return rbSusunHari(String(d.tanggal || '')).find((g) => g.anggota[0].koleksi === koleksi && String(g.anggota[0].data.id) === String(id)) || null;
}

// ---------- batal ----------
/** Periksa sebelum membatalkan. → { tolak } | { g, e, akibat } */
export function rbPeriksa(koleksi, id) {
  const g = rbKelompok(koleksi, id); if (!g) return { tolak: 'Catatan ini tidak ada (sudah dibatalkan / dihapus?), atau ikut kelompok catatan lain' };
  if (g.sebab) return { tolak: 'Tidak dibatalkan di sini: ' + g.sebab };
  for (const x of g.anggota) { const k = tolakKunci(x.koleksi, x.data, 'bulan itu sudah dikunci — catatan tidak bisa dibatalkan lagi'); if (k) return { tolak: k }; }
  const d = g.anggota[0].data;
  // karung yang dibuka di ketukan ini sudah punya catatan lanjutan (karung bekas lahir di ketukan lain) → yang terbaru dulu
  const ids = g.anggota.filter((x) => x.koleksi === 'wadahLiteran' && x.data.tipe === 'karung').map((x) => String(x.data.id));
  if (ids.length && RB_AMBIL.stokBahanLiteran().some((b) => b.karungId !== undefined && ids.indexOf(String(b.karungId)) >= 0 && !g.anggota.some((x) => x.koleksi === 'stokBahanLiteran' && String(x.data.id) === String(b.id))))
    return { tolak: 'Karung yang dibuka di sini sudah dicatat habis (karung bekas) di catatan lain sesudahnya — batalkan catatan yang terbaru dulu' };
  if (g.jenis === 'pindahTempat') {
    if (RB_AMBIL.pindahTempat().some((p) => String(p.kunci) === String(d.kunci) && String(p.id) !== String(d.id) && rbSesudah(p, d))) return { tolak: String(d.barang || 'Barang ini') + ' sudah dipindah lagi sesudahnya — batalkan pindahan terbarunya dulu' };
    if (String(petaTempat()[d.kunci] || '') !== String(d.ke || '')) return { tolak: String(d.barang || 'Barang ini') + ' sekarang tidak di ' + (d.ke || 'tanpa tempat') + ' — tempatnya sudah diubah lewat jalan lain' };
  }
  if (g.jenis === 'pindahStok') { const ke = g.anggota.find((x) => x.data.tipe === 'masuk'); if (ke) { const ada = (ssStokLokasi()[ke.data.merk] || {})[ke.data.lokasi] || 0;
    if (ada + 0.005 < (Number(ke.data.kg) || 0)) return { tolak: 'Di ' + ke.data.lokasi + ' tinggal ' + rbAngka(ada) + ' kg ' + ke.data.merk + ' — sebagian sudah terpakai, pindahan ini tidak bisa dibatalkan utuh' }; } }
  const e = rbJumlahPengaruh(g.anggota); const R = rbKoreksi(g.anggota, e, -1, 'cek', '');
  for (const x of R.dokumen) { const k = tolakKunci(x.koleksi, x.data, 'hitungan sesudahnya ada di bulan yang sudah dikunci — tidak bisa dibatalkan lagi'); if (k) return { tolak: k }; }
  const akibat = ['Dibatalkan: ' + rbJenis(g) + (g.anggota.length > 1 ? ' (' + g.anggota.length + ' catatan satu ketukan)' : '') + ' — tidak dihitung lagi, salinannya tetap di daftar Dibatalkan'];
  if (g.jenis === 'pindahTempat') akibat.push(String(d.barang || '') + ' kembali ke ' + (d.dari || 'tanpa tempat'));
  if (g.anggota.some((x) => x.koleksi === 'stokBahanLiteran' && x.data.lahirKarungBekas)) akibat.push('Karung bekas yang lahir / dicabut di ketukan itu ikut batal');
  return { g, e, akibat: akibat.concat(R.akibat) };
}
/** Batalkan kelompok barang `koleksi|id` dengan alasan. → { dokumen, hapus, jejakHapus, patch } | { tolak } */
export function rbSusunBatal(koleksi, id, alasan, w) {
  const a = String(alasan || '').trim().slice(0, 120); if (!a) return { tolak: 'Membatalkan butuh alasan' };
  const P = rbPeriksa(koleksi, id); if (P.tolak) return P;
  const g = P.g; const idBatal = 'bt-' + w.idUnik(); const R = rbKoreksi(g.anggota, P.e, -1, idBatal, w.kini); const d = g.anggota[0].data;
  const arsip = { id: idBatal, tanggal: w.tanggal, jam: w.jam, koleksi: g.anggota[0].koleksi, idDok: String(d.id), tanggalDok: String(d.tanggal || ''), pemasok: '',
    ringkas: rbJenis(g) + (g.anggota.length > 1 ? ' (' + g.anggota.length + ' catatan)' : ''), alasan: a, jenisBatal: 'barang', jenis: g.jenis,
    dokumen: g.anggota.map((x) => ({ koleksi: x.koleksi, data: x.data })), efek: P.e, koreksi: { geser: R.geser } };
  const dokumen = [{ koleksi: 'bukuHapus', data: arsip }].concat(R.dokumen);
  if (g.jenis === 'pindahTempat') { const peta = petaTempat(); if (d.dari) peta[d.kunci] = d.dari; else delete peta[d.kunci]; dokumen.push({ koleksi: 'pengaturan', data: { id: 'tempatSimpan', peta, diubahPada: w.kini } }); }
  return { dokumen, hapus: g.anggota.map((x) => ({ koleksi: x.koleksi, id: String(x.data.id) })), jejakHapus: 'Batal: ' + arsip.ringkas + ' — ' + a,
    patch: { kabar: 'Dibatalkan — ' + arsip.ringkas + '. ' + R.akibat.join(' · ') + (R.akibat.length ? ' · ' : '') + 'Salinannya di daftar Dibatalkan (bisa dipulihkan).', kabarAwas: false } };
}
/** Pulihkan pembatalan barang `idBatal`: catatan kembali (id sama), hitungan sesudahnya digeser balik menurut keadaan SEKARANG, tempat simpan kembali. */
export function rbSusunPulih(idBatal, w) {
  const x = cacheMentah('bukuHapus').find((b) => String(b.id) === String(idBatal)); if (!x) return { tolak: 'Catatan dibatalkan itu tidak ditemukan' };
  if (x.jenisBatal !== 'barang' || !Array.isArray(x.dokumen) || !x.dokumen.length) return { tolak: 'Yang ini bukan pembatalan barang' };
  for (const d of x.dokumen) {
    if (rbCari(d.koleksi, d.data.id)) return { tolak: 'Catatan ' + d.koleksi + ' dengan nomor yang sama sudah ada lagi — tidak dipulihkan dua kali' };
    const k = tolakKunci(d.koleksi, d.data, 'bulan itu sudah dikunci — tidak bisa dipulihkan'); if (k) return { tolak: k };
  }
  const A = x.dokumen.map((d) => ({ koleksi: d.koleksi, data: d.data })); const kepala = A[0].data; const dokumen = A.slice();
  if (x.jenis === 'pindahTempat') { const peta = petaTempat(); if (String(peta[kepala.kunci] || '') !== String(kepala.dari || '')) return { tolak: String(kepala.barang || 'Barang ini') + ' sudah dipindah lagi sesudah dibatalkan — tidak dipulihkan' };
    if (kepala.ke) peta[kepala.kunci] = kepala.ke; else delete peta[kepala.kunci]; dokumen.push({ koleksi: 'pengaturan', data: { id: 'tempatSimpan', peta, diubahPada: w.kini } }); }
  const R = rbKoreksi(A, Object.assign({}, x.efek || rbJumlahPengaruh(A)), 1, x.id, w.kini);
  for (const d of R.dokumen) { const k = tolakKunci(d.koleksi, d.data, 'hitungan sesudahnya ada di bulan yang sudah dikunci — tidak bisa dipulihkan'); if (k) return { tolak: k }; }
  return { dokumen: dokumen.concat(R.dokumen), hapus: [{ koleksi: 'bukuHapus', id: String(idBatal) }], jejakHapus: 'Pulihkan: ' + String(x.ringkas || ''),
    patch: { kabar: 'Dipulihkan — ' + String(x.ringkas || '') + ' kembali di buku' + (R.akibat.length ? '. ' + R.akibat.join(' · ') : ''), kabarAwas: false } };
}
