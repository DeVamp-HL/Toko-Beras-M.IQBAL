// LOGIKA layar MENU, tanpa DOM. Keluarga Menu dikunci owner 16 Sep 2026: N1 "Laci berkelompok" = PATOKAN UI (tiap pintu kelihatan dan
// membawa kabarnya sendiri), N9 = pita jam sebagai LACI PALING ATAS milik N1 (laci di bawahnya tidak pernah berpindah tempat), dan
// empat saudara yang memakai rangka laci yang sama dengan DASAR PENYUSUNAN lain: N2 Menu yang bertanya · N5 Menu yang tahu jam ·
// N6 Menu menurut orang · N8 Menu yang menolak (pintu yang tertutup, berikut sebabnya dan apa yang membukanya).
// Semua angka DIBACA dari data toko lewat mesin yang sama dengan sistem lama — tidak ada angka yang lahir di layar Menu.
// Tiap baris membawa TUJUAN: layar sistem baru (jual / stok + lembar / pelanggan / sistem), atau sistem lama (halaman yang belum ada di sini).
// Nama pembantu diprefiks `mn` karena bundel uji jsc satu lingkup.
import { hitungPiutang, hitungUtangPemasok, hitungKasbon, hitungStokKarungPerMerk, hitungStokKemasan, hitungLabaBersihRentang, hitungNeraca, kasPada } from '../mesin/beku.js';
import { cariHargaKarungPerKg, kunciPelanggan } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilSemuaBatch, ambilTutupHari, ambilPengeluaranHarian, ambilPiutangMutasi, ambilPenyesuaianStok, ambilPenyesuaianKemasan, ambilBahanKemasan, ambilBahanLiteran, ambilHargaKarung, ambilHargaKemasan, ambilHargaLiteran, ambilProduksiBerlaku, ambilPemasokCatatan, ambilTitikKas, cacheMentah } from '../data/toko.js';
import { RP, ANGKA, DESIMAL, hariIniIso, tanggalPendek } from '../inti/format.js';
import { semuaBon } from './bon-logika.js';
import { semuaOrang } from './pelanggan-logika.js';
import { ssHariKe, ssTambahHari, ssPerangkat, ssPersetujuan, ssCadangan, ssLokasi, ssPengingat, ssEraTutupBuku } from './sistem-logika.js';

// ---------- bagian hari (N5/N9): lima blok, batasnya dari desain terkunci ----------
export const MN_BAGIAN = [{ id: 0, nama: 'Dini hari', jam: '00–05', dari: 0, sampai: 5 }, { id: 1, nama: 'Pagi', jam: '06–10', dari: 6, sampai: 10 }, { id: 2, nama: 'Tengah hari', jam: '11–14', dari: 11, sampai: 14 }, { id: 3, nama: 'Sore', jam: '15–17', dari: 15, sampai: 17 }, { id: 4, nama: 'Malam', jam: '18–23', dari: 18, sampai: 23 }];
export const mnBagianDari = (jam) => (jam <= 5 ? 0 : jam <= 10 ? 1 : jam <= 14 ? 2 : jam <= 17 ? 3 : 4);
/** Jam (0–23) dari 'HH:MM' / 'HH.MM' / ISO; null bila tidak terbaca. */
export function mnJam(teks) {
  if (!teks) return null; const s = String(teks);
  if (s.indexOf('T') > 0) { const d = new Date(s); return isFinite(d.getTime()) ? d.getHours() : null; }
  const m = s.match(/^(\d{1,2})[:.](\d{2})/); if (!m) return null; const j = Number(m[1]); return j >= 0 && j <= 23 ? j : null;
}
// Tujuh pekerjaan yang jamnya terbaca (urutannya TETAP — baris tidak boleh berpindah tempat) + pintunya
export const MN_KERJA = [
  { id: 'jual', nama: 'Jual — nota di meja', ikon: 'keranjang', ket: 'jam yang tertulis di nota', tujuan: { ke: 'jual', teks: 'buka Jual' } },
  { id: 'karcis', nama: 'Rinci karcis — waktu disalin', ikon: 'karcis', ket: 'jam mesin waktu karcis darurat disalin jadi nota', tujuan: { ke: 'lama', halaman: 'Jual', teks: 'rinci karcis di sistem lama' } },
  { id: 'tutup', nama: 'Tutup hari & kas', ikon: 'bulan', ket: 'penutupan kas malam', tujuan: { ke: 'lama', halaman: 'Tutup Hari', teks: 'tutup hari di sistem lama' } },
  { id: 'belanja', nama: 'Belanja harian', ikon: 'dompet', ket: 'kopi, bensin, upah harian', tujuan: { ke: 'lama', halaman: 'Harian', teks: 'belanja harian di sistem lama' } },
  { id: 'bon', nama: 'Buku bon pelanggan', ikon: 'buku', ket: 'bayar & saldo awal', tujuan: { ke: 'pelanggan', keluarga: 'bon', teks: 'buka Pelanggan → Bon' } },
  { id: 'opname', nama: 'Opname beras & kemasan', ikon: 'papan', ket: 'hitung fisik', tujuan: { ke: 'stok', lembar: 'cocok', teks: 'buka Stok → Cocokkan' } },
  { id: 'harga', nama: 'Katalog harga', ikon: 'label', ket: 'harga jual disunting', tujuan: { ke: 'lama', halaman: 'Harga', teks: 'katalog harga di sistem lama' } },
];
const mnJamDok = { jual: (d) => (d.dirinciPada ? null : mnJam(d.jam)), karcis: (d) => mnJam(d.dirinciPada), tutup: (d) => mnJam(d.jam), belanja: (d) => mnJam(d.jam), bon: (d) => mnJam(d.jam), opname: (d) => mnJam(d.jam), harga: (d) => mnJam(d.diubahPada || d.diperbaruiPada) };
const mnDokKerja = { jual: () => ambilPenjualan(), karcis: () => ambilPenjualan(), tutup: () => ambilTutupHari(), belanja: () => ambilPengeluaranHarian(), bon: () => ambilPiutangMutasi(),
  opname: () => ambilPenyesuaianStok().concat(ambilPenyesuaianKemasan(), ambilBahanKemasan().filter((x) => x.tipe === 'opname'), ambilBahanLiteran().filter((x) => x.tipe === 'opname')), harga: () => ambilHargaKarung().concat(ambilHargaKemasan(), ambilHargaLiteran()) };
/** Berapa tulisan tiap pekerjaan jatuh di tiap bagian hari (sel[5]), berapa yang jamnya terbaca (n) dari seluruhnya (tot). */
export function mnSilangJam() {
  return MN_KERJA.map((k) => { const sel = [0, 0, 0, 0, 0]; let n = 0, tot = 0; mnDokKerja[k.id]().forEach((d) => { tot += 1; const j = mnJamDok[k.id](d); if (j === null) return; n += 1; sel[mnBagianDari(j)] += 1; });
    const puncak = n ? sel.indexOf(Math.max.apply(null, sel)) : null; return Object.assign({}, k, { sel, n, tot, puncak, bagi: sel.map((x) => (n ? Math.round(x / n * 1000) / 10 : 0)) }); });
}
const mnPS = (x) => String(x).replace('.', ',') + '%';
/** N9 · laci paling atas: pekerjaan yang jatuh di bagian hari `bag` (bawaan: sekarang); tujuh baris selalu tujuh. */
export function susunPita(kini, bag) {
  const silang = mnSilangJam(); const ki = mnBagianDari(kini.getHours()); const b = bag === undefined || bag === null ? ki : Number(bag); const B = MN_BAGIAN[b];
  const isi = silang.map((k) => ({ id: k.id, ikon: k.ikon, judul: k.nama, angka: ANGKA(k.sel[b]), cap: k.sel[b] ? 'tulisan di bagian hari ini' : 'tidak ada di bagian hari ini',
    sub: k.sel[b] ? mnPS(k.bagi[b]) + ' dari ' + ANGKA(k.n) + ' tulisan pekerjaan ini yang jamnya terbaca' + (k.puncak === b ? ' · bagian hari PUNCAKNYA' : '') : (k.n ? 'nol tulisan — pekerjaan ini tidak pernah jatuh di jam-jam ini' : 'belum ada tulisan yang jamnya terbaca'), awas: false, tujuan: k.tujuan, n: k.sel[b] }));
  const bagian = MN_BAGIAN.map((x) => { const jumlah = silang.reduce((a, k) => a + k.sel[x.id], 0); const top = silang.slice().sort((p, q) => q.sel[x.id] - p.sel[x.id])[0]; return { id: x.id, nama: x.nama, jam: x.jam, jumlah, sekarang: x.id === ki, terbuka: x.id === b, pokok: jumlah ? 'paling banyak: ' + top.nama : 'belum ada tulisan' }; });
  return { bagian: B, sekarang: ki, terbuka: b, isi, daftarBagian: bagian, jumlah: bagian[b].jumlah, kepala: (b === ki ? 'Sekarang · ' : '') + B.nama, ket: B.jam + ' · ' + ANGKA(bagian[b].jumlah) + ' tulisan' };
}

// ---------- pembantu angka bersama ----------
const mnAwalBulan = (iso) => iso.slice(0, 7) + '-01';
function mnCatatanPertama() { let t = ''; ambilPenjualan().concat(ambilSemuaBatch().filter((b) => !b.stokAwal && !b.tutupBuku)).forEach((d) => { if (d.tanggal && (!t || d.tanggal < t)) t = d.tanggal; }); return t; }
const mnTempo = () => { const d = cacheMentah('aturan').find((x) => String(x.id) === 'catatStok'); const n = d ? Number(d.tempoHari) : NaN; return isFinite(n) && n > 0 ? n : 21; };
function mnUtang(iso) { const up = hitungUtangPemasok(); const tempo = mnTempo(); const bon = []; up.forEach((px) => (px.bon || []).forEach((b) => bon.push(Object.assign({ pemasok: px.pemasok, jatuh: b.tanggal ? ssTambahHari(b.tanggal, tempo) : '', lewat: b.tanggal ? ssHariKe(iso) - ssHariKe(ssTambahHari(b.tanggal, tempo)) : null }, b))));
  return { up, total: up.reduce((a, x) => a + (x.totalUtang || 0), 0), n: up.filter((x) => x.totalUtang > 0).length, bon, lewat: bon.filter((b) => b.lewat !== null && b.lewat > 0), tempo, tekor: up.reduce((a, x) => a + (x.tekor || 0), 0), berikut: bon.filter((b) => b.jatuh).sort((a, b) => a.jatuh.localeCompare(b.jatuh))[0] || null }; }
function mnOpname() { const semua = ambilPenyesuaianStok().concat(ambilPenyesuaianKemasan()).filter((x) => !x.dariRework).concat(ambilBahanKemasan().filter((x) => x.tipe === 'opname'), ambilBahanLiteran().filter((x) => x.tipe === 'opname'));
  let akhir = ''; semua.forEach((x) => { if ((x.tanggal || '') > akhir) akhir = x.tanggal; }); return { n: semua.length, akhir, tanpaRupiah: semua.filter((x) => typeof x.nilaiRp !== 'number').length }; }
function mnKatalog() { const k = ambilHargaKarung(), m = ambilHargaKemasan(), l = ambilHargaLiteran(); const stokK = hitungStokKarungPerMerk();
  const tipis = k.map((h) => ({ merk: h.merk, untung: (Number(h.hargaPerKg) || 0) - ((stokK[h.merk] || {}).hppTerakhirPerKg || 0), adaModal: !!(stokK[h.merk] && stokK[h.merk].hppTerakhirPerKg) })).filter((x) => x.adaModal).sort((a, b) => a.untung - b.untung);
  return { karung: k.length, kemasan: m.length, literan: l.length, total: k.length + m.length + l.length, tipis, rugi: tipis.filter((x) => x.untung < 0).length }; }

// ---------- N1 · LACI BERKELOMPOK (patokan) + dua baris Sistem (Lokasi, Pengingat) di laci "Toko ini" ----------
/** lokal = { antre, idPerangkat, autoTanggal, lsKb, … } dari peramban (boleh kosong di uji). */
export function susunLaci(kini, lokal) {
  const iso = hariIniIso(kini); const L = lokal || {};
  const U = mnUtang(iso); const bon = semuaBon(kini).filter((b) => b.sisa > 0); const totalBon = bon.reduce((a, b) => a + b.sisa, 0); const macet = bon.filter((b) => b.status === 'macet').length; const tagih = bon.filter((b) => b.status === 'janjiLewat' || b.status === 'perluTagih').length;
  const pertama = mnCatatanPertama(); const umur = pertama ? ssHariKe(iso) - ssHariKe(pertama) + 1 : 0; const laba = hitungLabaBersihRentang(mnAwalBulan(iso), iso);
  const K = mnKatalog(); const O = mnOpname(); const opUmur = O.akhir ? ssHariKe(iso) - ssHariKe(O.akhir) : null;
  const prod = ambilProduksiBerlaku(); const prodBulan = new Set(prod.filter((p) => (p.tanggal || '') >= mnAwalBulan(iso) && !p.dariTakar).map((p) => p.batchProduksi || p.id)).size; const prodSemua = new Set(prod.filter((p) => !p.dariTakar).map((p) => p.batchProduksi || p.id)).size;
  const era = ssEraTutupBuku(); const tahunLalu = pertama && Number(pertama.slice(0, 4)) < kini.getFullYear();
  const P = ssPerangkat(kini, L.antre || [], L.idPerangkat || ''); const S = ssPersetujuan(kini); const C = ssCadangan(kini, L); const LK = ssLokasi(); const G = ssPengingat(kini, L);
  const baris = (id, ikon, judul, sub, angka, cap, awas, tujuan) => ({ id, ikon, judul, sub, angka, cap, awas: !!awas, tujuan });
  return [
    { id: 'buku', nama: 'Buku besar', ket: 'yang dibaca: utang, piutang, laporan', isi: [
      baris('pemasok', 'truk', 'Pemasok & utang', U.n ? U.n + ' pemasok · ' + U.bon.length + ' bon terbuka' + (U.lewat.length ? ' · ' + U.lewat.length + ' lewat tempo ' + U.tempo + ' hari' : ' · belum ada yang lewat tempo') + (U.tekor ? ' · kelebihan bayar ' + RP(U.tekor) : '') : 'tidak ada utang ke pemasok yang tercatat', U.total ? RP(U.total) : 'nihil', 'utang toko ke pemasok', U.lewat.length > 0 || U.tekor > 0, { ke: 'lama', halaman: 'Pemasok', teks: 'bon & bayar pemasok masih di sistem lama' }),
      baris('pelanggan', 'orang', 'Pelanggan & piutang', bon.length ? bon.length + ' nama berutang' + (tagih ? ' · ' + tagih + ' waktunya ditagih' : '') + (macet ? ' · ' + macet + ' macet' : '') : 'tidak ada bon yang terbuka', totalBon ? RP(totalBon) : 'nihil', 'hak toko yang belum ditagih', macet > 0, { ke: 'pelanggan', keluarga: 'bon', teks: 'buka Pelanggan → Bon' }),
      baris('laporan', 'dokumen', 'Laporan', pertama ? 'catatan pertama ' + tanggalPendek(pertama) + ' · laba bersih bulan ini ' + RP(laba.labaBersih) + (laba.jumlahTanpaHpp ? ' (' + laba.jumlahTanpaHpp + ' baris tanpa modal tidak ikut)' : '') : 'belum ada catatan', umur ? umur + ' hari' : '—', 'seluruh umur buku toko ini', false, { ke: 'lama', halaman: 'Laba', teks: 'laporan laba, arus kas & neraca masih di sistem lama' }),
    ] },
    { id: 'alat', nama: 'Alat toko', ket: 'yang dikerjakan, bukan yang dibaca', isi: [
      baris('harga', 'label', 'Katalog harga', 'harga jual per merek, karung & literan' + (K.rugi ? ' · ' + K.rugi + ' merek karung di bawah modal' : K.tipis.length ? ' · paling tipis ' + K.tipis[0].merk + ' ' + RP(K.tipis[0].untung) + '/kg' : ''), K.total + ' baris', 'karung ' + K.karung + ' · kemasan ' + K.kemasan + ' · literan ' + K.literan, K.rugi > 0, { ke: 'lama', halaman: 'Harga', teks: 'katalog harga masih di sistem lama' }),
      baris('opname', 'papan', 'Opname', 'hitung fisik rak beras, kemasan & kantong' + (O.tanpaRupiah ? ' · ' + O.tanpaRupiah + ' catatan lama tanpa kolom rupiah' : ''), O.n ? O.n + ' catatan' : 'belum pernah', O.akhir ? 'terakhir ' + tanggalPendek(O.akhir) + (opUmur ? ' · ' + opUmur + ' hari lalu' : '') : 'belum pernah dicocokkan', opUmur === null || opUmur >= 14, { ke: 'stok', lembar: 'cocok', teks: 'buka Stok → Cocokkan' }),
      baris('produksi', 'kotak', 'Produksi & kemasan', 'adukan, bongkar kemasan, jahit karung bekas · ' + ANGKA(prodSemua) + ' adukan seluruhnya', ANGKA(prodBulan) + ' adukan', 'bulan ini', false, { ke: 'stok', lembar: 'adukan', teks: 'buka Stok → Adukan' }),
      baris('tutupBuku', 'buku', 'Tutup buku', 'menutup tahun buku dan menulis saldo pembuka' + (era ? '' : ' · cadangan WAJIB sebelum & sesudah'), era ? 'tahun ' + era : 'belum pernah', era ? 'saldo pembuka terakhir' : 'era tutup buku masih kosong', !era && tahunLalu, { ke: 'lama', halaman: 'Setelan', teks: 'tutup buku ada di sistem lama → Setelan' }),
    ] },
    { id: 'toko', nama: 'Toko ini', ket: 'siapa yang memakai, dan dari alat apa', isi: [
      baris('perangkat', 'perangkat', 'Perangkat & antrean', P.daftar.length ? P.hariIni + ' berdenyut hari ini' + (P.nAntre ? ' · ' + P.nAntre + ' catatan perangkat ini belum sampai server' : ' · semua catatan perangkat ini sudah sampai') + (P.lainAntre ? ' · ' + P.lainAntre + ' menunggu di perangkat lain' : '') : 'belum ada perangkat yang berdenyut', P.daftar.length + ' perangkat', P.daftar.filter((d) => d.dinamai).length + ' bernama · ' + P.daftar.filter((d) => !d.dinamai).length + ' belum dinamai', P.nAntre > 0 || P.lainAntre > 0, { ke: 'sistem', sistem: 'perangkat', teks: 'buka Perangkat & antrean' }),
      baris('peran', 'kunci', 'Peran & persetujuan', 'siapa boleh apa sendiri, apa yang minta owner · kunci perangkat diatur di perangkatnya', S.menunggu.length ? S.menunggu.length + ' menunggu' : '3 peran', S.menunggu.length ? 'permintaan menunggu owner' : 'owner · Ben · karyawan', S.menunggu.length > 0, { ke: 'sistem', sistem: 'peran', teks: 'buka Peran & persetujuan' }),
      baris('cadangan', 'arsip', 'Cadangan & simpanan', 'unduh berkas cadangan, kuota simpanan perangkat' + (C.kuota.awas ? ' · simpanan lokal di atas ambang' : ''), C.terakhir ? tanggalPendek(C.terakhir.tanggal) : 'belum pernah', C.terakhir ? 'cadangan terakhir · ' + C.terakhir.sumber : 'tidak ada cadangan tercatat', C.telat || C.kuota.awas, { ke: 'sistem', sistem: 'cadangan', teks: 'buka Cadangan & simpanan' }),
      baris('lokasi', 'peta', 'Lokasi', 'tiap catatan membawa lokasi perangkat yang mencatatnya' + (LK.daftar.length > 1 ? ' · pindah stok antarlokasi' : ' · pindah stok hidup begitu ada lokasi kedua'), LK.daftar.length + ' lokasi', 'utama: ' + LK.utama.nama, false, { ke: 'sistem', sistem: 'lokasi', teks: 'buka Lokasi' }),
      baris('pengingat', 'lonceng', 'Pengingat', G.ringkas, G.aktif.length ? G.aktif.length + ' pengingat' : 'beres', G.lewat.length ? G.lewat.length + ' sudah lewat' : 'bon pemasok · janji bayar · kantong · opname · cadangan', G.lewat.length > 0, { ke: 'sistem', sistem: 'pengingat', teks: 'buka Pengingat' }),
    ] },
  ];
}

// ---------- N2 · MENU YANG BERTANYA: sepuluh pertanyaan, jawabannya kelihatan sebelum diketuk ----------
export function susunTanya(kini) {
  const iso = hariIniIso(kini); const U = mnUtang(iso); const B = semuaBon(kini).filter((b) => b.sisa > 0); const out = [];
  const tanya = (id, t, n, j, awas, tujuan, ikon) => out.push({ id, ikon: ikon || 'tanya', judul: t, angka: n, sub: j, cap: tujuan.teks, awas: !!awas, tujuan });
  tanya('utang', 'Toko ini berutang ke siapa, berapa?', U.total ? RP(U.total) : 'nihil', U.n ? U.up.filter((x) => x.totalUtang > 0).map((x) => x.pemasok + ' ' + RP(x.totalUtang)).join(' · ') + (U.lewat.length ? '. ' + U.lewat.length + ' bon lewat tempo ' + U.tempo + ' hari.' : '.') + (U.tekor ? ' Kelebihan bayar ' + RP(U.tekor) + ' — ada kedatangan yang bonnya belum masuk buku.' : '') : 'Tidak ada bon pemasok yang terbuka.', U.lewat.length > 0 || U.tekor > 0, { ke: 'lama', halaman: 'Pemasok', teks: 'bon pemasok di sistem lama' }, 'truk');
  const bk = U.berikut; const sisaB = bk ? ssHariKe(bk.jatuh) - ssHariKe(iso) : null;
  tanya('jatuh', 'Bon pemasok berikutnya jatuh kapan?', bk ? tanggalPendek(bk.jatuh) : 'tidak ada', bk ? 'Bon ' + bk.pemasok + ' ' + RP(bk.sisa) + ' dari ' + tanggalPendek(bk.tanggal) + ' — tempo ' + U.tempo + ' hari (Atur pencatatan stok) → ' + (sisaB < 0 ? 'sudah lewat ' + (-sisaB) + ' hari' : sisaB === 0 ? 'hari ini' : sisaB + ' hari lagi') + '.' : 'Tidak ada bon pemasok terbuka yang bertanggal.', sisaB !== null && sisaB <= 3, { ke: 'sistem', sistem: 'pengingat', teks: 'pengingat bon pemasok' }, 'kalender');
  const kas = kasPada(); const titik = ambilTitikKas();
  tanya('kas', 'Uang toko sekarang ada di mana?', kas === null ? 'belum bisa dihitung' : RP(kas), kas === null ? 'Titik kas belum disetel di perangkat ini — sistem lama menyimpannya per perangkat (Tutup Hari → titik kas). Angka tidak ditebak.' : 'Kas tercatat semua kantong (laci, rekening, amplop laba, brankas) dari titik kas ' + (titik && titik.tanggal ? tanggalPendek(titik.tanggal) : '') + ' ditambah gerakan sesudahnya.', kas === null, { ke: 'ringkasan', teks: 'kartu kas di Ringkasan' }, 'dompet');
  const laba = hitungLabaBersihRentang(mnAwalBulan(iso), iso);
  tanya('laba', 'Bulan ini toko untung berapa?', laba.omzetHitung > 0 ? RP(laba.labaBersih) : 'belum ada', laba.omzetHitung > 0 ? 'Laba bersih ' + laba.nHari + ' hari bulan ini: margin kotor ' + RP(laba.margin) + ' − biaya toko ' + RP(laba.biayaToko) + (laba.hapusBuku ? ' − hapus buku ' + RP(laba.hapusBuku) : '') + (laba.susutStok ? ' ± susut ' + RP(laba.susutStok) : '') + (laba.jumlahTanpaHpp ? '. ' + laba.jumlahTanpaHpp + ' baris tanpa modal tidak ikut.' : '.') : 'Belum ada nota bulan ini.', laba.omzetHitung > 0 && laba.labaBersih < 0, { ke: 'lama', halaman: 'Laba', teks: 'laporan laba di sistem lama' }, 'naik');
  const N = hitungNeraca();
  tanya('kaya', 'Kalau semuanya dihitung, toko ini kaya atau tidak?', N.total === null ? 'belum bisa dihitung' : RP(N.total), N.total === null ? 'Kas belum bisa dihitung (titik kas belum disetel), jadi kekayaannya pun belum.' : 'Kas ' + RP(N.kas) + ' + stok ' + RP(N.stok) + ' + piutang ' + RP(N.piutang) + ' + kasbon ' + RP(N.kasbon) + ' − utang pemasok ' + RP(N.utangPemasok) + ' − utang ke owner ' + RP(N.utangOwner) + '. Batas BAWAH: aset tetap belum punya kolomnya.' + (N.adaStokMinus ? ' Ada stok yang catatannya minus.' : ''), N.total !== null && N.total < 0, { ke: 'lama', halaman: 'Laba', teks: 'neraca di sistem lama' }, 'timbangan');
  const macet = B.filter((b) => b.status === 'macet'); const tertua = Math.max(0, ...B.map((b) => b.umur || 0));
  tanya('piutang', 'Siapa yang belum bayar ke toko?', B.length ? RP(B.reduce((a, b) => a + b.sisa, 0)) : 'tidak ada', B.length ? B.length + ' nama. ' + (macet.length ? macet.length + ' macet (' + RP(macet.reduce((a, b) => a + b.sisa, 0)) + ') — ' : '') + 'bon tertua ' + tertua + ' hari. Terbesar: ' + B.slice().sort((a, b) => b.sisa - a.sisa).slice(0, 2).map((b) => b.nama + ' ' + RP(b.sisa)).join(', ') + '.' : 'Tidak ada bon pelanggan yang terbuka.', macet.length > 0, { ke: 'pelanggan', keluarga: 'bon', teks: 'buka Pelanggan → Bon' }, 'orang');
  const K = mnKatalog(); const t0 = K.tipis[0] || null;
  tanya('lantai', 'Harga jual boleh turun berapa sebelum untungnya habis?', t0 ? RP(t0.untung) + '/kg' : 'belum bisa dihitung', t0 ? 'Merek karung paling tipis: ' + t0.merk + ' (untung ' + RP(t0.untung) + '/kg di atas modal rata-rata). ' + (K.rugi ? K.rugi + ' merek sudah berdiri di bawah modalnya.' : 'Tidak ada merek di bawah modal.') : 'Katalog karung belum punya merek yang modalnya tercatat.', K.rugi > 0, { ke: 'lama', halaman: 'Harga', teks: 'katalog harga di sistem lama' }, 'label');
  const perJam = {}; const sejak = ssTambahHari(iso, -30); ambilPenjualan().forEach((p) => { if ((p.tanggal || '') < sejak) return; const j = mnJam(p.jam); if (j === null) return; const m = (p.hargaTotal || 0) - (p.hppTotalSaatJual || 0); perJam[j] = perJam[j] || { margin: 0, n: 0 }; perJam[j].margin += m; perJam[j].n += 1; });
  const jamUrut = Object.keys(perJam).map(Number).sort((a, b) => perJam[b].margin - perJam[a].margin);
  tanya('jam', 'Jam berapa toko paling menghasilkan?', jamUrut.length ? String(jamUrut[0]).padStart(2, '0') + ':00' : 'belum ada', jamUrut.length ? 'Margin ' + RP(perJam[jamUrut[0]].margin) + ' dari ' + ANGKA(perJam[jamUrut[0]].n) + ' baris nota dalam 30 hari terakhir' + (jamUrut[1] !== undefined ? '. Kedua: ' + String(jamUrut[1]).padStart(2, '0') + ':00 (' + RP(perJam[jamUrut[1]].margin) + ').' : '.') : 'Belum ada nota berjam dalam 30 hari terakhir.', false, { ke: 'ringkasan', teks: 'skala Jam di Ringkasan' }, 'jam');
  const stokK = hitungStokKarungPerMerk(); const nilai = Object.keys(stokK).map((m) => ({ m, v: Math.max(0, stokK[m].sisaKg || 0) * (stokK[m].hppTerakhirPerKg || 0), kg: Math.max(0, stokK[m].sisaKg || 0) })).sort((a, b) => b.v - a.v); const totalV = nilai.reduce((a, x) => a + x.v, 0);
  const arus = {}; let arusTotal = 0; ambilPenjualan().forEach((p) => { if ((p.tanggal || '') < sejak || !p.merkSumber) return; arus[p.merkSumber] = (arus[p.merkSumber] || 0) + (p.totalKg || 0); arusTotal += p.totalKg || 0; });
  tanya('rak', 'Barang siapa yang menumpuk di rak beras?', nilai.length && totalV ? RP(nilai[0].v) : 'belum ada', nilai.length && totalV ? DESIMAL(Math.round(nilai[0].v / totalV * 1000) / 10) + '% nilai rak beras di ' + nilai[0].m + ' (' + ANGKA(nilai[0].kg) + ' kg), yang ' + (arusTotal ? DESIMAL(Math.round((arus[nilai[0].m] || 0) / arusTotal * 1000) / 10) + '% dari kg terjual 30 hari terakhir' : 'belum punya angka arus') + '.' : 'Rak beras kosong menurut buku.', nilai.length > 0 && totalV > 0 && nilai[0].v / totalV > 0.4, { ke: 'stok', tab: 'gudang', teks: 'buka Stok → Gudang' }, 'kotak');
  let omzet = 0, qris = 0; ambilPenjualan().forEach((p) => { omzet += p.hargaTotal || 0; if (/qris/i.test(String(p.caraBayar || ''))) qris += p.hargaTotal || 0; });
  tanya('saksi', 'Berapa omzet yang bisa dibuktikan ke orang luar?', omzet ? DESIMAL(Math.round(qris / omzet * 1000) / 10) + '%' : 'belum ada', omzet ? 'Cuma QRIS (' + RP(qris) + ' dari ' + RP(omzet) + ') yang punya bukti di luar buku toko — sisanya berdiri di atas catatan toko sendiri.' : 'Belum ada nota.', omzet > 0 && qris / omzet < 0.1, { ke: 'ringkasan', teks: 'Ringkasan' }, 'pena');
  return out;
}

// ---------- N5 · MENU YANG TAHU JAM: lima laci bagian hari, isinya pekerjaan yang jatuh di situ ----------
export function susunMenurutJam(kini) {
  const silang = mnSilangJam(); const ki = mnBagianDari(kini.getHours());
  return MN_BAGIAN.map((b) => { const isi = silang.map((k) => ({ id: k.id + '-' + b.id, ikon: k.ikon, judul: k.nama, angka: ANGKA(k.sel[b.id]), cap: k.puncak === b.id && k.n ? 'bagian hari puncaknya' : 'tulisan di jam-jam ini', sub: k.n ? mnPS(k.bagi[b.id]) + ' dari ' + ANGKA(k.n) + ' tulisan ' + k.ket : 'belum ada tulisan yang jamnya terbaca', awas: false, tujuan: k.tujuan, n: k.sel[b.id] })).sort((p, q) => q.n - p.n);
    const jumlah = isi.reduce((a, x) => a + x.n, 0); return { id: 'jam' + b.id, nama: b.nama + (b.id === ki ? ' · sekarang' : ''), ket: b.jam + ' · ' + ANGKA(jumlah) + ' tulisan' + (jumlah ? ' · paling banyak ' + isi[0].judul.split(' — ')[0].toLowerCase() : ''), sekarang: b.id === ki, isi }; });
}

// ---------- N6 · MENU MENURUT ORANG: satu nama, seluruh buku yang menyentuhnya ----------
export function susunMenurutOrang(kini) {
  const iso = hariIniIso(kini); const U = mnUtang(iso); const B = semuaBon(kini).filter((b) => b.sisa > 0); const kasbon = hitungKasbon(); const out = [];
  const baris = (id, ikon, judul, sub, angka, cap, awas, tujuan) => ({ id, ikon, judul, sub, angka, cap, awas: !!awas, tujuan });
  const kb = kasbon.filter((k) => k.sisa > 0).sort((a, b) => b.sisa - a.sisa);
  if (kb.length) out.push({ id: 'duaSisi', nama: 'Berdiri di dua sisi buku', ket: 'toko membayar upahnya DAN dia berutang kasbon ke toko', isi: kb.map((k) => baris('kb-' + k.kunci, 'orang', k.nama, 'pegawai · kasbon diambil ' + RP(k.ambil) + ', dikembalikan ' + RP(k.bayar) + ' · ' + k.mutasi.length + ' baris', RP(k.sisa), 'kasbon yang belum kembali', true, { ke: 'lama', halaman: 'Bulanan', teks: 'kasbon & gaji di sistem lama' })) });
  const pem = U.up.filter((x) => x.totalUtang > 0 || x.tekor > 0);
  out.push({ id: 'pemasok', nama: 'Pemasok', ket: pem.length ? pem.length + ' nama memegang seluruh utang toko' : 'tidak ada utang pemasok', isi: pem.map((x) => { const lw = U.lewat.filter((b) => b.pemasok === x.pemasok); const tua = Math.max(0, ...(x.bon || []).map((b) => b.umurHari || 0));
    return baris('pm-' + x.pemasok, 'truk', x.pemasok, (x.bon || []).length + ' bon terbuka' + (tua ? ' · tertua ' + tua + ' hari' : '') + (lw.length ? ' · ' + lw.length + ' lewat tempo' : '') + (x.tekor ? ' · kelebihan bayar ' + RP(x.tekor) : ''), RP(x.totalUtang), 'utang toko kepadanya', lw.length > 0 || x.tekor > 0, { ke: 'lama', halaman: 'Pemasok', teks: 'bon pemasok di sistem lama' }); }) });
  const besar = B.slice().sort((a, b) => b.sisa - a.sisa).slice(0, 3); const tua = B.slice().sort((a, b) => (b.umur || 0) - (a.umur || 0))[0]; const pembeli = besar.slice(); if (tua && !pembeli.some((b) => b.kunci === tua.kunci)) pembeli.push(tua);
  out.push({ id: 'pembeli', nama: 'Pembeli', ket: B.length ? B.length + ' nama berutang · yang paling menyentuh buku' : 'tidak ada bon pelanggan terbuka', isi: pembeli.map((b) => baris('pb-' + b.kunci, 'keranjang', b.nama, b.cap + ' · ' + b.ket + (b.dikenali ? '' : ' · belum dikenali'), RP(b.sisa), b.buka.length + ' bon terbuka', b.status === 'macet' || b.status === 'janjiLewat', { ke: 'pelanggan', keluarga: 'bon', orang: b.kunci, teks: 'buka bonnya' })) });
  const lunas = kasbon.filter((k) => !(k.sisa > 0) && k.ambil > 0);
  if (lunas.length) out.push({ id: 'pegawai', nama: 'Pegawai', ket: lunas.length + ' nama, kasbonnya lunas persis', isi: lunas.map((k) => baris('pg-' + k.kunci, 'orang', k.nama, 'kasbon diambil ' + RP(k.ambil) + ' dan dikembalikan ' + RP(k.bayar) + ' — tidak bersisa', 'lunas', k.mutasi.length + ' baris kasbon', false, { ke: 'lama', halaman: 'Bulanan', teks: 'gaji & kasbon di sistem lama' })) });
  const penulis = {}; let semua = 0; ambilPenjualan().forEach((p) => { const o = String(p.oleh || '').trim() || '(tanpa nama)'; penulis[o] = (penulis[o] || 0) + 1; semua += 1; });
  const urutP = Object.keys(penulis).sort((a, b) => penulis[b] - penulis[a]).slice(0, 4);
  out.push({ id: 'penulis', nama: 'Yang menulis', ket: semua ? 'nama di kolom penulis ' + ANGKA(semua) + ' baris nota' : 'belum ada nota', isi: urutP.map((o) => baris('pn-' + o, 'pena', o, o === '(tanpa nama)' ? 'baris nota tanpa nama penulis — ditulis sebelum jejak dicatat' : 'baris nota atas namanya · ' + DESIMAL(Math.round(penulis[o] / semua * 1000) / 10) + '% dari semua', ANGKA(penulis[o]), 'baris nota', o === '(tanpa nama)' && penulis[o] / semua > 0.5, { ke: 'sistem', sistem: 'perangkat', tab: 'jejak', teks: 'jejak pencatat' })) });
  return out;
}

// ---------- N8 · MENU YANG MENOLAK: pintu yang tertutup karena bukunya belum bisa menjawab ----------
export function susunTertutup(kini) {
  const iso = hariIniIso(kini); const era = ssEraTutupBuku(); const pertama = mnCatatanPertama(); const O = mnOpname(); const kartuPemasok = ambilPemasokCatatan().length; const hapus = ambilPiutangMutasi().filter((m) => m.tipe === 'hapusBuku').length;
  let bulanPenuh = 0; if (pertama) { let b = pertama.slice(0, 7); for (let i = 0; i < 240; i++) { const y = Number(b.slice(0, 4)), m = Number(b.slice(5, 7)); const awal = b + '-01'; const akhir = new Date(Date.UTC(y, m, 0)).toISOString().slice(0, 10); if (akhir >= iso) break; if (awal >= pertama) bulanPenuh += 1; b = (m === 12 ? (y + 1) + '-01' : y + '-' + String(m + 1).padStart(2, '0')); } }
  const telusur = ambilPenjualan().filter((p) => p.batchId || p.dariBatch || p.kedatanganId).length;
  const pintu = (id, ikon, judul, tertutup, sub, angka, cap, jawab, tujuan) => ({ id, ikon, judul, tertutup, sub, angka, cap, awas: tertutup, jawab, tujuan });
  const isi = [
    pintu('tutupBuku', 'buku', 'Tutup buku tahun', !era, era ? 'era terakhir tahun ' + era : 'era tutup buku masih kosong', era ? String(era) : '0', 'era pernah ditulis', 'Tidak ada garis yang memisahkan satu tahun buku dari tahun berikutnya. YANG MEMBUKANYA: menulis era pertama lewat tutup buku — cadangan WAJIB diunduh sebelum DAN sesudah ritualnya.', { ke: 'lama', halaman: 'Setelan', teks: 'tutup buku di sistem lama' }),
    pintu('bulanPenuh', 'kalender', 'Laporan satu bulan penuh', bulanPenuh === 0, bulanPenuh ? bulanPenuh + ' bulan kalender sudah utuh di buku' : 'belum ada satu bulan kalender yang utuh di buku', bulanPenuh ? bulanPenuh + ' bulan' : (pertama ? (ssHariKe(iso) - ssHariKe(pertama) + 1) + ' hari' : '—'), bulanPenuh ? 'bulan penuh' : 'umur buku', bulanPenuh ? 'Laporan bulan ke bulan sudah bisa dibandingkan utuh.' : 'YANG MEMBUKANYA: menunggu satu bulan kalender lewat penuh. Sampai itu, yang boleh dibandingkan cuma laju per hari dagang.', { ke: 'ringkasan', teks: 'skala Bulan di Ringkasan' }),
    pintu('opnameRupiah', 'label', 'Nilai rupiah opname', O.n > 0 && O.tanpaRupiah === O.n, O.n ? O.tanpaRupiah + ' dari ' + O.n + ' hitungan tanpa nilai rupiah' : 'belum pernah opname', O.n ? O.tanpaRupiah + ' dari ' + O.n : '0', 'tanpa kolom rupiah', O.tanpaRupiah ? 'Catatan lama tanpa rupiah tidak pernah bisa masuk laba. Sejak putaran 11, Cocokkan di sistem baru SELALU menulis selisih kg DAN rupiah.' : 'Semua hitungan fisik punya nilai rupiahnya.', { ke: 'stok', lembar: 'cocok', teks: 'buka Stok → Cocokkan' }),
    pintu('kartuPemasok', 'kartu', 'Tagih lewat kartu pemasok', kartuPemasok === 0, kartuPemasok ? kartuPemasok + ' kartu pemasok terisi' : 'kartu pengenal pemasok nol baris', String(kartuPemasok), 'kartu pemasok', kartuPemasok ? 'Nomor & tempo pemasok tersimpan di kartunya.' : 'Tidak ada nomor telepon, tempo, atau nama orang yang tersimpan. YANG MEMBUKANYA: mengisi kartu untuk pemasok yang memegang utang toko (layar Pemasok, belum di sistem baru).', { ke: 'lama', halaman: 'Pemasok', teks: 'kartu pemasok di sistem lama' }),
    pintu('hapusBuku', 'hapus', 'Hapus buku piutang mati', false, hapus ? hapus + ' hapus buku tercatat' : 'jenis baris hapus buku sudah ada — belum pernah dipakai', String(hapus), 'hapus buku', 'TERBUKA sejak putaran 13: Pelanggan → Bon → "Hapus dari buku" menulis baris hapusBuku beralasan (bukan uang masuk, kerugian bulan itu).', { ke: 'pelanggan', keluarga: 'bon', teks: 'buka Pelanggan → Bon' }),
    pintu('telusur', 'rantai', 'Telusur nota ke kedatangannya', telusur === 0, telusur ? telusur + ' baris nota menyebut kedatangan asalnya' : 'nol baris nota menyebut kedatangan asalnya', String(telusur), 'nota bertanda kedatangan', telusur ? 'Sebagian nota sudah bisa ditelusuri ke muatannya.' : 'Kebiasaan menyimpan penunjuk ADA di buku (nota menunjuk pesanan, retur menunjuk nota) — cuma tidak pernah ke kedatangan. YANG MEMBUKANYA: menyimpan id kedatangan di baris penjualan (butuh keputusan owner: FIFO per muatan).', { ke: 'belum', teks: 'belum ada layarnya' }),
  ];
  const tertutup = isi.filter((p) => p.tertutup).length;
  return [{ id: 'tertutup', nama: 'Tertutup karena bukunya belum bisa menjawab', ket: tertutup + ' dari ' + isi.length + ' pintu · angkanya yang menutup', isi }];
}

// ---------- CARI: layar, merek, atau nama orang ----------
export const MN_LAYAR = [
  { nama: 'Jual', sub: 'nota di meja', tujuan: { ke: 'jual', teks: 'buka Jual' } }, { nama: 'Ringkasan', sub: 'cincin detik · menit · jam · hari · minggu · bulan · tahun', tujuan: { ke: 'ringkasan', teks: 'buka Ringkasan' } },
  { nama: 'Stok · Gudang', sub: 'apa yang harus dibeli, modal tidur, tidak bergerak, belum dicocokkan', tujuan: { ke: 'stok', tab: 'gudang', teks: 'buka Stok' } }, { nama: 'Stok · Wadah literan', sub: 'W1–W8, karung di belakang wadah', tujuan: { ke: 'stok', tab: 'wadah', teks: 'buka Stok → Wadah' } },
  { nama: 'Stok · Papan Kapur', sub: 'perubahan stok hari ini', tujuan: { ke: 'stok', tab: 'kapur', teks: 'buka Stok → Papan Kapur' } }, { nama: 'Stok · Karantina', sub: 'barang kembali yang belum diputuskan', tujuan: { ke: 'stok', tab: 'karantina', teks: 'buka Stok → Karantina' } },
  { nama: 'Barang masuk', sub: 'satu mobil satu catatan', tujuan: { ke: 'stok', lembar: 'masuk', teks: 'buka Stok → Barang masuk' } }, { nama: 'Cocokkan (opname)', sub: 'tercatat vs dihitung', tujuan: { ke: 'stok', lembar: 'cocok', teks: 'buka Stok → Cocokkan' } }, { nama: 'Adukan', sub: 'timbangan adukan', tujuan: { ke: 'stok', lembar: 'adukan', teks: 'buka Stok → Adukan' } },
  { nama: 'Kantong', sub: 'beli kantong per lembar, rak, riwayat harga', tujuan: { ke: 'stok', lembar: 'kantong', teks: 'buka Stok → Kantong' } }, { nama: 'Tempat simpan', sub: 'denah toko, di mana tiap beras', tujuan: { ke: 'stok', lembar: 'tempat', teks: 'buka Stok → Tempat simpan' } }, { nama: 'HPP / modal', sub: 'modal per nama, margin, koreksi beralasan', tujuan: { ke: 'stok', lembar: 'hpp', teks: 'buka Stok → HPP' } },
  { nama: 'Pelanggan · Kenali', sub: 'wajah, tampah, belanja, jam, minggu, benang, hafalan', tujuan: { ke: 'pelanggan', keluarga: 'kenali', teks: 'buka Pelanggan' } }, { nama: 'Pelanggan · Bon', sub: 'buku bon, papan tagih, garis umur', tujuan: { ke: 'pelanggan', keluarga: 'bon', teks: 'buka Pelanggan → Bon' } }, { nama: 'Pelanggan · THR', sub: 'siapa dapat apa', tujuan: { ke: 'pelanggan', keluarga: 'thr', teks: 'buka Pelanggan → THR' } },
  { nama: 'Perangkat & antrean', sub: 'siapa memegang alat mana, apa yang belum sampai server, jejak pencatat', tujuan: { ke: 'sistem', sistem: 'perangkat', teks: 'buka Perangkat' } }, { nama: 'Peran & persetujuan', sub: 'siapa boleh apa', tujuan: { ke: 'sistem', sistem: 'peran', teks: 'buka Peran' } },
  { nama: 'Cadangan & simpanan', sub: 'unduh berkas cadangan, kuota', tujuan: { ke: 'sistem', sistem: 'cadangan', teks: 'buka Cadangan' } }, { nama: 'Lokasi', sub: 'lokasi perangkat, pindah stok', tujuan: { ke: 'sistem', sistem: 'lokasi', teks: 'buka Lokasi' } }, { nama: 'Pengingat', sub: 'bon pemasok, janji bayar, kantong, opname, cadangan', tujuan: { ke: 'sistem', sistem: 'pengingat', teks: 'buka Pengingat' } },
  { nama: 'Harga (sistem lama)', sub: 'katalog harga jual', tujuan: { ke: 'lama', halaman: 'Harga', teks: 'sistem lama' } }, { nama: 'Pemasok (sistem lama)', sub: 'bon & bayar pemasok', tujuan: { ke: 'lama', halaman: 'Pemasok', teks: 'sistem lama' } }, { nama: 'Laba & neraca (sistem lama)', sub: 'laporan', tujuan: { ke: 'lama', halaman: 'Laba', teks: 'sistem lama' } },
  { nama: 'Tutup hari (sistem lama)', sub: 'ritual malam', tujuan: { ke: 'lama', halaman: 'Tutup Hari', teks: 'sistem lama' } }, { nama: 'Belanja harian (sistem lama)', sub: 'pengeluaran harian', tujuan: { ke: 'lama', halaman: 'Harian', teks: 'sistem lama' } }, { nama: 'Bulanan (sistem lama)', sub: 'gaji, kasbon, biaya tetap', tujuan: { ke: 'lama', halaman: 'Bulanan', teks: 'sistem lama' } },
];
const mnPolos = (s) => String(s || '').toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
export function susunCari(kini, q) {
  const t = mnPolos(q); if (t.length < 2) return { teks: t, hasil: [], kosong: false };
  const cocok = (s) => mnPolos(s).indexOf(t) >= 0; const hasil = [];
  MN_LAYAR.forEach((l) => { if (cocok(l.nama) || cocok(l.sub)) hasil.push({ jenis: 'layar', judul: l.nama, sub: l.sub, tujuan: l.tujuan }); });
  const stokK = hitungStokKarungPerMerk(); Object.keys(stokK).forEach((m) => { if (cocok(m)) hasil.push({ jenis: 'merek', judul: m, sub: 'beras · buku ' + ANGKA(Math.round(stokK[m].sisaKg || 0)) + ' kg', tujuan: { ke: 'stok', tab: 'gudang', teks: 'buka Stok → Gudang' } }); });
  const stokM = hitungStokKemasan(); Object.keys(stokM).forEach((k) => { const x = stokM[k]; const nm = x.namaProduk + ' ' + x.ukuranKemasan + ' kg'; if (cocok(nm)) hasil.push({ jenis: 'merek', judul: nm, sub: 'kemasan · ' + ANGKA(x.sisaUnit || 0) + ' unit', tujuan: { ke: 'stok', tab: 'gudang', teks: 'buka Stok → Gudang' } }); });
  semuaOrang(kini).forEach((o) => { if (cocok(o.nama) || cocok(o.asli)) hasil.push({ jenis: 'orang', judul: o.nama, sub: (o.utang > 0 ? 'bon ' + RP(o.utang) + ' · ' : '') + o.kunjungan + ' kali datang', tujuan: { ke: 'pelanggan', keluarga: 'kenali', orang: o.kunci, teks: 'buka kartunya' } }); });
  return { teks: t, hasil: hasil.slice(0, 12), kosong: !hasil.length, lebih: Math.max(0, hasil.length - 12) };
}
export const mnKunci = kunciPelanggan;
export const MN_SUSUNAN = [['laci', 'Laci'], ['tanya', 'Tanya'], ['jam', 'Jam'], ['orang', 'Orang'], ['tertutup', 'Tertutup']];
