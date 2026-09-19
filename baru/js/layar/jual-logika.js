// LAYAR JUAL — LOGIKA (tanpa DOM). Keadaan → turunan (rak, tagihan, hari ini, pelanggan) dan
// tindakan (ketuk chip, isi jumlah, keranjang, parkir, bayar). Dijaga alat-uji/uji_jual_baru.py di jsc.
//
// Aturan toko yang dipegang di sini (semua keputusan owner, tanggalnya di memori piagam 13–17 Sep):
//  - harga & sisa dibaca lewat mesin beku yang sama dengan index.html (hargaKarungUtuh, stokMaksJalur, …);
//  - pembulatan ke Rp500 KE ATAS untuk TUNAI dan BON, QRIS persis (17 Sep);
//  - struk yang diparkir MEMEGANG jatah stoknya — "siapa cepat dia dapat" (17 Sep);
//  - uang kurang → sisanya OTOMATIS jadi bon atas nama pembeli, nama wajib (17 Sep);
//  - nego hanya menyentuh harga, lantai Rp500 (NEGO_LANTAI live), tercatat di baris;
//  - PUTARAN 2: nota DICATAT dengan bentuk dokumen yang sama persis dengan simpanKeranjangJual() index.html
//    (potongan dibagi proporsional, pembulatan melekat ke baris terakhir, bayar sebagian = Kredit + pelunasan,
//    kemasan literan dipakai = dokumen stokBahanLiteran id+1); KR1 untuk bon; batalkan = tandai dibatalkan.
//  - PUTARAN 3 (paritas Jual lama): Repacking Dadakan (jenis 'repacking' = kg bebas dari kolam karung, harga per kg
//    katalog, nama jual bebas — bangunTrxJualDariForm 19325); bonus kemasan +1 (bonusUnit: stok & HPP ikut, uang tidak —
//    wzTambahItem 17633); pengganti retur (penggantiRetur + nilaiBarangPengganti, hargaTotal 0, tanpa pembulatan — 19383);
//    Pesanan: dipesan → diantar → DIBAYAR hanya lewat nota (simpanPesanan 16219, tutupPesananDariJual 16272), ikatan ikut diparkir.
import { hitungStokKarungPerMerk, hitungStokKemasan, hitungStokBahanLiteran, hitungPiutang, stokMaksJalur } from '../mesin/beku.js';
import { kunciKemasan, kunciPelanggan, bulatKeAtas500, bakuCaraBayar, merkPunyaKarungBerat, hargaKarungUtuh, cariHargaKarungPerKg,
  tentukanKemasanLiteran, jumlahKemasanLiteran, hargaBahanLiteranEfektif, catatanPelangganBerisi, infoKreditPelanggan,
  pesananBelumTuntas, RASIO_KONVERSI, RASIO_DEFAULT, NEGO_LANTAI } from '../mesin/pembantu.js';
import { ambilHargaKemasan, ambilHargaLiteran, ambilPenjualan, ambilPenjualanSemua, ambilPelangganCatatan, ambilPesanan, ambilRetur, ambilWadahLiteran, setelKeranjang,
  wzDiKeranjangParkir, sumberData } from '../data/toko.js';
import { hariIniIso, RP } from '../inti/format.js';
import { returAwal, cekDrafTukar, dokumenKarantina } from './retur-logika.js';

export const JALUR = [['sering', 'Sering'], ['literan', 'Literan'], ['kemasan', 'Kemasan'], ['karung', 'Karung'], ['repack', 'Repack'], ['retur', 'Retur']];
export const JALUR_NANTI = [['wadah', 'Wadah']];   // putaran berikutnya
export const PECAHAN = [100000, 50000, 20000, 10000, 5000, 2000, 1000, 500];
// ---------- WADAH LITERAN (kotak kayu bergunung) — praktik lapangan, keterangan owner 14 Sep & 19 Sep 2026 ----------
// Delapan kotak wadah; tiap wadah ±50 kg saat baru diisi (berasnya MENGGUNUNG di atas bibir kotak), diisi ulang begitu
// berkurang ±40 kg. Literan lain (ketan dll.) diserok langsung dari karung → bukan wadah.
// INI ALAT UKUR "kapan harus isi ulang", bukan stok: stok literan tetap dipotong dari kolam merek oleh mesin yang sama.
// Tiga angka di bawah adalah KEBIJAKAN owner — kelak diatur dari layar Stok khusus wadah, bukan dari kode.
export const DAFTAR_WADAH = ['Angsa', 'IR64 Elevate', 'Perahu Layar', 'IR64 Apex', 'IR42 Select', 'IR42 Value', 'Pandan Wangi', 'IR64 Ascent'];
export const WADAH_PENUH_KG = 50;        // isi wadah tepat sesudah diisi ulang (menggunung)
export const WADAH_ISI_ULANG_KG = 10;    // tersisa segini (sudah berkurang ±40 kg) → saatnya isi ulang
export const WADAH_RATA_BAGIAN = 0.6;    // di atas 60% isinya masih menggunung; di bawahnya permukaan rata lalu turun
export const STATUS_PESANAN = { dipesan: 'DIPESAN', diantar: 'DIANTAR', dibayar: 'DIBAYAR', batal: 'BATAL' };

export function keadaanAwal() {
  return {
    jalur: 'sering', lembar: null, pilih: null, ketik: '', satuanKarung: 50, namaRepack: '',
    keranjang: [], negoId: null, potongan: 0, penggantiTanya: null,
    pelanggan: '', cariPelanggan: '', cara: 'Tunai', uang: 0,
    antrean: [], aktifId: 1, idBerikut: 2, urutBaris: 0,
    kreditDibuka: false, notaTerakhir: null,
    pesananId: null, psNama: '', psIsi: '', psAlamat: '', psNilai: '', psSaring: '',
    tukar: null,   // PUTARAN 4: { returDraf, kredit, ringkas } — retur tukar yang diikat ke keranjang ini (_tukarKeJual index.html 16838)
    ...returAwal(),
    kabar: '', kabarAwas: false, sekarang: null,
  };
}

// ---------- pembacaan (bacaan mesin, bukan hitungan sendiri) ----------
const rasioMerk = (merk) => RASIO_KONVERSI[merk] || RASIO_DEFAULT;

/** Jembatan DOM warisan: stokMaksJalur() (mesin beku) membaca berat karung dari #jualKarungBerat. */
function setelBeratDom(berat) {
  const el = typeof document !== 'undefined' ? document.getElementById('jualKarungBerat') : null;
  if (el) el.value = String(berat);
}

/** Rak per jalur dari data toko: chip yang tampil = punya harga di katalog (tanpa harga tidak muncul, bukan Rp0). */
export function susunRak(s) {
  const stokKarung = hitungStokKarungPerMerk();
  const stokKemasan = hitungStokKemasan();
  const hargaKemasan = ambilHargaKemasan();
  const hargaLiteran = ambilHargaLiteran();
  const rak = { karung: [], kemasan: [], literan: [], repack: [] };
  Object.keys(stokKarung).sort().forEach((merk) => {
    [50, 25].forEach((berat) => {
      if (!merkPunyaKarungBerat(merk, berat)) return;
      const hg = hargaKarungUtuh(merk, berat);
      if (!hg || !hg.perUnit) return;
      setelBeratDom(berat);
      const maks = stokMaksJalur('karung', merk);   // sudah dikurangi keranjang aktif + yang diparkir
      rak.karung.push({ jalur: 'karung', kunci: merk, nama: merk, ukuran: berat + ' kg', harga: hg.perUnit, satuan: 'karung',
        berat, sisa: maks === null ? 0 : maks, sisaTeks: (maks === null ? 0 : maks) + ' karung', hppPerKg: stokKarung[merk].hppTerakhirPerKg || 0,
        dipegang: wzDiKeranjangParkir('karung', merk) });
    });
    const hl = hargaLiteran.find((x) => x.merk === merk);
    if (hl && hl.hargaPerLiter > 0) {
      const sisaL = bebasLiter(merk, rasioMerk(merk));
      rak.literan.push({ jalur: 'literan', kunci: merk, nama: merk, ukuran: 'per liter', harga: hl.hargaPerLiter, satuan: 'L',
        rasio: rasioMerk(merk), sisa: sisaL, sisaTeks: '±' + sisaL.toString().replace('.', ',') + ' L', hppPerKg: stokKarung[merk].hppTerakhirPerKg || 0,
        dipegang: wzDiKeranjangParkir('karung', merk) });
    }
    // REPACKING DADAKAN: kg bebas dari kolam karung merek ini, harga per kg katalog (hitungTotalJual index.html 18926)
    const perKg = cariHargaKarungPerKg(merk);
    if (perKg !== null && perKg > 0) {
      const sisaKg = bebasKg(merk);
      rak.repack.push({ jalur: 'repack', kunci: merk, nama: merk, ukuran: 'kg bebas · buka sack', harga: perKg, satuan: 'kg',
        sisa: sisaKg, sisaTeks: '±' + DESIMAL2(sisaKg) + ' kg', hppPerKg: stokKarung[merk].hppTerakhirPerKg || 0,
        dipegang: wzDiKeranjangParkir('karung', merk) });
    }
  });
  Object.keys(stokKemasan).sort().forEach((kunci) => {
    const st = stokKemasan[kunci];
    const hg = hargaKemasan.find((x) => x.merk === st.namaProduk && Number(x.ukuran) === Number(st.ukuranKemasan));
    if (!hg || !hg.hargaPerUnit) return;
    const maks = stokMaksJalur('kemasan', kunci);
    rak.kemasan.push({ jalur: 'kemasan', kunci, nama: st.namaProduk, ukuran: st.ukuranKemasan + ' kg', harga: hg.hargaPerUnit, satuan: 'kemasan',
      ukuranKg: Number(st.ukuranKemasan), sisa: maks === null ? 0 : maks, sisaTeks: (maks === null ? 0 : maks) + ' sisa', hppPerUnit: st.hppRataRataPerUnit || 0,
      dipegang: wzDiKeranjangParkir('kemasan', kunci) });
  });
  // TATA LETAK (owner 19 Sep, seperti papan harga di toko): per kategori ukuran, tiap kategori dari yang TERMURAH
  const termurah = (a, b) => a.harga - b.harga || a.nama.localeCompare(b.nama);
  rak.kemasan.sort((a, b) => a.ukuranKg - b.ukuranKg || termurah(a, b));
  rak.karung.sort((a, b) => b.berat - a.berat || termurah(a, b));
  rak.literan.sort(termurah); rak.repack.sort(termurah);
  rak.literan.forEach((c) => { c.wadah = tinggiWadah(c.kunci, s); });
  const kelompokkan = (daftar, kunci, judul) => { const out = []; daftar.forEach((c) => { const k = kunci(c); let g = out.find((x) => x.k === k); if (!g) { g = { k, judul: judul(c), daftar: [] }; out.push(g); } g.daftar.push(c); }); return out; };
  rak.kelompok = { kemasan: kelompokkan(rak.kemasan, (c) => c.ukuranKg, (c) => String(c.ukuranKg).replace('.', ',') + ' kg'), karung: kelompokkan(rak.karung, (c) => c.berat, (c) => 'Karung ' + c.berat + ' kg') };
  // SERING: barang yang biasa dibeli orang ini (90 hari); tanpa nama → yang paling laku 28 hari terakhir
  rak.sering = susunSering(s, rak);
  return rak;
}

function kunciBaris(p) {
  if (p.jenis === 'kemasan') return 'kemasan|' + kunciKemasan(p.namaProduk, p.ukuranKemasan);
  if (p.jenis === 'karung') return 'karung|' + p.merkSumber + '|' + (p.beratKarungAcuan || 50);
  if (p.jenis === 'literan') return 'literan|' + p.merkSumber;
  if (p.jenis === 'repacking') return 'repack|' + p.merkSumber;
  return null;
}
function susunSering(s, rak) {
  const semua = [].concat(rak.karung.map((c) => Object.assign({}, c, { id: 'karung|' + c.kunci + '|' + c.berat })),
    rak.kemasan.map((c) => Object.assign({}, c, { id: 'kemasan|' + c.kunci })),
    rak.literan.map((c) => Object.assign({}, c, { id: 'literan|' + c.kunci })),
    rak.repack.map((c) => Object.assign({}, c, { id: 'repack|' + c.kunci })));
  const peta = {}; semua.forEach((c) => { peta[c.id] = c; });
  const k = kunciPelanggan(s.pelanggan);
  const hari = hariIniIso(s.sekarang);
  const batas = geser(hari, k ? -90 : -28);
  const hitung = {};
  ambilPenjualan().forEach((p) => {
    if ((p.tanggal || '') < batas) return;
    if (k && kunciPelanggan(p.namaPelanggan) !== k) return;
    const id = kunciBaris(p); if (!id || !peta[id]) return;
    hitung[id] = (hitung[id] || 0) + 1;
  });
  return Object.keys(hitung).sort((a, b) => hitung[b] - hitung[a]).slice(0, 8)
    .map((id) => Object.assign({}, peta[id], { jalur: peta[id].jalur, kali: hitung[id], keterangan: hitung[id] + '× ' + (k ? 'dibeli' : 'laku') }));
}
function geser(iso, n) { const d = new Date(iso + 'T00:00:00'); d.setDate(d.getDate() + n); return hariIniIso(d); }

/**
 * Baris keranjang dari chip + jumlah, dengan bentuk trx yang SAMA dengan penjualan index.html.
 * ekstra = { bonusUnit, penggantiRetur, namaProduk, hargaSatuan, nego } — bendera baris yang dipertahankan saat baris dibangun ulang.
 *   jumlah   = yang DIBAYAR (unit/karung/liter/kg); kemasan: jumlahUnit = jumlah + bonus (stok & HPP ikut bonus, uang tidak — wzTambahItem 17633).
 *   penggantiRetur: nilai barang disimpan sebagai jejak (nilaiBarangPengganti), uangnya Rp0 (bangunTrxJualDariForm 19383).
 */
export function bangunBaris(chip, jumlah, s, ekstra) {
  const j = Number(jumlah) || 0; const e = ekstra || {};
  if (j <= 0) return null;
  let t = null;
  if (chip.jalur === 'karung') {
    const totalKg = j * chip.berat;
    t = { jenis: 'karung', merkSumber: chip.kunci, jumlahKarung: j, beratKarungAcuan: chip.berat, totalKg, namaProduk: chip.kunci + ' (karung utuh)',
      hppTotalSaatJual: Math.round((chip.hppPerKg || 0) * totalKg), label: chip.nama + ' ' + chip.berat + ' kg', satuan: 'karung' };
  } else if (chip.jalur === 'kemasan') {
    const bonus = e.bonusUnit ? 1 : 0; const unit = j + bonus;
    t = { jenis: 'kemasan', namaProduk: chip.nama, ukuranKemasan: chip.ukuranKg, jumlahUnit: unit, totalKg: chip.ukuranKg * unit,
      hppTotalSaatJual: Math.round((chip.hppPerUnit || 0) * unit), label: chip.nama + ' ' + chip.ukuranKg + ' kg', satuan: 'kemasan' };
    if (bonus) t.bonusUnit = 1;
  } else if (chip.jalur === 'literan') {
    const rasio = chip.rasio || rasioMerk(chip.kunci);
    const totalKg = Math.round(j * rasio * 1000) / 1000;
    const jenisK = tentukanKemasanLiteran(j); const nK = jenisK ? jumlahKemasanLiteran(j) : 0;
    const biayaK = jenisK ? hargaBahanLiteranEfektif(jenisK, hitungStokBahanLiteran()) * nK : 0;
    t = { jenis: 'literan', merkSumber: chip.kunci, namaProduk: chip.kunci, jumlahLiter: j, rasioPakai: rasio, totalKg,
      hppTotalSaatJual: Math.round((chip.hppPerKg || 0) * totalKg) + biayaK, kemasanLiteran: jenisK, biayaKemasanLiteran: biayaK,
      jumlahKemasanLiteranDipakai: nK, label: chip.nama + ' literan', satuan: 'L' };
  } else if (chip.jalur === 'repack') {
    const nama = String(e.namaProduk !== undefined ? e.namaProduk : (s && s.namaRepack) || '').trim() || chip.nama;
    t = { jenis: 'repacking', merkSumber: chip.kunci, namaProduk: nama, totalKg: j, hppTotalSaatJual: Math.round((chip.hppPerKg || 0) * j),
      label: 'Repack ' + nama, satuan: 'kg' };
  }
  if (!t) return null;
  t.jumlah = j; t.hargaAsli = chip.harga; t.hargaSatuan = e.nego ? e.hargaSatuan : chip.harga; if (e.nego) t.nego = true;
  return selesaikanHarga(t, !!e.penggantiRetur);
}
/** Uang baris dari harga satuan × jumlah bayar; pengganti retur → nilai jadi jejak, hargaTotal 0. */
function selesaikanHarga(t, penggantiRetur) {
  const nilai = Math.round(t.hargaSatuan * t.jumlah);
  if (penggantiRetur) { t.penggantiRetur = true; t.nilaiBarangPengganti = nilai; t.hargaTotal = 0; }
  else { delete t.penggantiRetur; delete t.nilaiBarangPengganti; t.hargaTotal = nilai; }
  return t;
}
const benderaBaris = (t) => ({ bonusUnit: t.bonusUnit || 0, penggantiRetur: !!t.penggantiRetur, namaProduk: t.jenis === 'repacking' ? t.namaProduk : undefined, hargaSatuan: t.hargaSatuan, nego: !!t.nego });
/** Yang harus tersedia di stok untuk baris ini (kemasan: unit bayar + bonus). */
const butuhStok = (t) => t.jenis === 'kemasan' ? t.jumlah + (t.bonusUnit || 0) : t.jumlah;

/** Langit-langit stok untuk chip ini SEKARANG (keranjang aktif + parkir sudah dikurangi oleh mesin). */
export function maksUntuk(chip) {
  if (chip.jalur === 'karung') { setelBeratDom(chip.berat); return stokMaksJalur('karung', chip.kunci); }
  if (chip.jalur === 'kemasan') return stokMaksJalur('kemasan', chip.kunci);
  if (chip.jalur === 'literan') return bebasLiter(chip.kunci, chip.rasio || rasioMerk(chip.kunci));
  if (chip.jalur === 'repack') return bebasKg(chip.kunci);
  return null;
}
/** Liter yang bebas dijual: kolam kg merek itu dikurangi yang dipegang struk parkir & keranjang aktif (kolam yang sama dengan karung). */
function bebasLiter(merk, rasio) {
  const sisaKg = (hitungStokKarungPerMerk()[merk] || {}).sisaKg || 0;
  const dipakai = wzDiKeranjangParkir('karung', merk) + jumlahAktifKg(merk);
  return Math.max(0, Math.floor((sisaKg - dipakai) / rasio * 10) / 10);
}
/** Kg yang bebas dijual lepas (repacking) dari kolam yang sama. */
function bebasKg(merk) {
  const sisaKg = (hitungStokKarungPerMerk()[merk] || {}).sisaKg || 0;
  return Math.max(0, Math.floor((sisaKg - wzDiKeranjangParkir('karung', merk) - jumlahAktifKg(merk)) * 100) / 100);
}
const DESIMAL2 = (n) => String(Math.round(n * 100) / 100).replace('.', ',');
let _keranjangKini = [];
function jumlahAktifKg(merk) { return _keranjangKini.reduce((a, b) => a + ((b.trx.merkSumber === merk && (b.trx.jenis === 'karung' || b.trx.jenis === 'literan' || b.trx.jenis === 'repacking')) ? (b.trx.totalKg || 0) : 0), 0); }

/** Sinkronkan keranjang aktif & parkir ke lapisan data (dibaca stokMaksJalur lewat wzDiKeranjang). */
export function sinkronKeranjang(s) {
  _keranjangKini = s.keranjang;
  setelKeranjang(s.keranjang.map((b) => ({ trx: b.trx })), s.antrean.map((a) => ({ beku: { items: a.beku.items.map((b) => ({ trx: b.trx })), nama: a.beku.pelanggan } })));
}

// ---------- tagihan ----------
/** Pembulatan Rp500 ke atas untuk Tunai DAN Bon (keputusan owner 17 Sep 2026); QRIS persis. */
export function pembulatanTagihan(total, cara) {
  const c = bakuCaraBayar(cara);
  return (c === 'Tunai' || c === 'Kredit') && total > 0 ? bulatKeAtas500(total) - Math.round(total) : 0;
}
export function hitungTagihan(s) {
  const subtotal = s.keranjang.reduce((a, b) => a + (b.trx.hargaTotal || 0), 0);
  const potongan = Math.min(Math.max(0, Math.round(s.potongan || 0)), subtotal);
  // TUKAR: nilai barang yang kembali dipotong SEBELUM pembulatan — pembulatan dihitung atas selisih bersih (wzTagihan 17680)
  const kredit = s.tukar ? Math.round(s.tukar.kredit || 0) : 0;
  const bersih = subtotal - potongan - kredit;
  const bulat = pembulatanTagihan(bersih, s.cara);
  const total = bersih + bulat;
  const uang = s.cara === 'Tunai' ? Math.round(s.uang || 0) : 0;
  const kembalian = s.cara === 'Tunai' ? Math.max(0, uang - total) : 0;
  const kurang = s.cara === 'Tunai' && uang > 0 ? Math.max(0, total - uang) : 0;
  return { subtotal, potongan, kredit, bersih, bulat, total, uang, kembalian, kurang, sisaJadiBon: kurang > 0 };
}

// ---------- pelanggan ----------
export function daftarPelanggan(cari) {
  const c = kunciPelanggan(cari);
  const peta = {};
  const piutang = hitungPiutang();
  ambilPenjualan().forEach((p) => {
    const k = kunciPelanggan(p.namaPelanggan); if (!k) return;
    if (!peta[k]) peta[k] = { kunci: k, nama: String(p.namaPelanggan).trim(), terakhir: p.tanggal || '', kali: 0 };
    peta[k].kali += 1; if ((p.tanggal || '') > peta[k].terakhir) { peta[k].terakhir = p.tanggal; peta[k].nama = String(p.namaPelanggan).trim(); }
  });
  ambilPelangganCatatan().forEach((cat) => {
    const k = kunciPelanggan(cat.nama || cat.id); if (!k) return;
    if (!peta[k]) peta[k] = { kunci: k, nama: String(cat.nama || cat.id).trim(), terakhir: '', kali: 0 };
    peta[k].terdaftar = catatanPelangganBerisi(cat);
  });
  return Object.values(peta).map((o) => {
    const r = piutang.find((x) => x.kunci === o.kunci);
    return Object.assign(o, { sisaBon: r ? Math.max(0, r.sisa) : 0, umurHari: r ? r.umurHari : null, terdaftar: !!o.terdaftar });
  }).filter((o) => !c || o.kunci.indexOf(c) >= 0)
    .sort((a, b) => (b.terakhir > a.terakhir ? 1 : b.terakhir < a.terakhir ? -1 : a.nama.localeCompare(b.nama))).slice(0, 40);
}
export function infoPelanggan(nama) {
  if (!kunciPelanggan(nama)) return null;
  const i = infoKreditPelanggan(nama);
  const pesanan = ambilPesanan().filter((p) => pesananBelumTuntas(p) && kunciPelanggan(p.namaPelanggan || p.nama) === kunciPelanggan(nama));
  return Object.assign(i, { pesanan });
}

// ---------- hari ini ----------
export function hariIni(s) {
  const iso = hariIniIso(s.sekarang);
  const baris = ambilPenjualan().filter((p) => p.tanggal === iso);
  const nota = new Set(baris.map((p) => p.grupNota || p.id)).size;
  const omzet = baris.reduce((a, p) => a + (p.hargaTotal || 0), 0);
  const perCara = {}; baris.forEach((p) => { const c = bakuCaraBayar(p.caraBayar); perCara[c] = (perCara[c] || 0) + (p.hargaTotal || 0); });
  const terakhir = baris.slice(0, 6).map((p) => ({ jam: p.jam || '', nama: p.namaPelanggan || '', teks: ringkasBaris(p), n: p.hargaTotal || 0, cara: bakuCaraBayar(p.caraBayar) }));
  return { iso, nota, baris: baris.length, omzet, perCara, terakhir, kg: baris.reduce((a, p) => a + (p.totalKg || 0), 0) };
}
function ringkasBaris(p) {
  if (p.jenis === 'kemasan') return (p.namaProduk || '') + ' ' + (p.ukuranKemasan || '') + ' kg × ' + (p.jumlahUnit || '');
  if (p.jenis === 'karung') return (p.merkSumber || '') + ' ' + (p.beratKarungAcuan || 50) + ' kg × ' + (p.jumlahKarung || '');
  if (p.jenis === 'literan') return (p.merkSumber || '') + ' ' + (p.jumlahLiter || 0) + ' L';
  if (p.jenis === 'repacking') return 'Repack ' + (p.namaProduk || '') + ' ' + (p.totalKg || 0) + ' kg';
  return p.namaProduk || p.jenis || '';
}

// ---------- tindakan (mengembalikan patch keadaan; tidak menyentuh DOM) ----------
export function ketukChip(s, chip) {
  return { pilih: chip, lembar: 'jumlah', ketik: '', kabar: '' };
}
export function tekanTuts(s, t) {
  if (t === '⌫') return { ketik: s.ketik.slice(0, -1) };
  if (t === ',') { if (s.ketik.indexOf(',') >= 0 || (s.pilih && s.pilih.jalur !== 'literan' && s.pilih.jalur !== 'repack')) return {}; return { ketik: (s.ketik || '0') + ',' }; }
  if (!/^\d+$/.test(t)) return {};
  if (s.ketik === '' && t === '0') return {};
  if ((s.ketik + t).replace(',', '').length > 9) return {};
  return { ketik: s.ketik + t };
}
export const angkaKetik = (teks) => parseFloat(String(teks || '').replace(',', '.')) || 0;
/** Rupiah yang diketik bebas ("1.380.000", "1380000", "Rp 1.380.000") → bilangan bulat. */
export const angkaRupiah = (teks) => Math.round(Number(String(teks || '').replace(/[^\d]/g, '')) || 0);

/** Masukkan chip terpilih ke keranjang sejumlah ketikan/preset; ditolak kalau melampaui langit-langit. */
export function masukkan(s, jumlah) {
  const chip = s.pilih; if (!chip) return { kabar: 'Pilih barangnya dulu', kabarAwas: true };
  const j = Number(jumlah) || angkaKetik(s.ketik);
  if (j <= 0) return { kabar: 'Isi jumlahnya dulu', kabarAwas: true };
  if (chip.jalur === 'karung' && (j * 2) % 1 !== 0) return { kabar: 'Karung dijual utuh atau setengah (0,5 · 1 · 1,5 …)', kabarAwas: true };
  if (chip.jalur === 'kemasan' && j % 1 !== 0) return { kabar: 'Kemasan dijual per unit', kabarAwas: true };
  sinkronKeranjang(s);
  const maks = maksUntuk(chip);
  if (maks !== null && j > maks) {
    const dipegang = chip.jalur === 'kemasan' ? wzDiKeranjangParkir('kemasan', chip.kunci) : wzDiKeranjangParkir('karung', chip.kunci);
    const siapa = siapaParkir(s, chip);
    return { kabar: 'Yang bebas dijual sekarang ' + tulisJumlah(maks, chip) + ', diminta ' + tulisJumlah(j, chip)
      + (dipegang > 0 ? ' — ' + (siapa || 'struk lain') + ' masih memegang ' + tulisKg(dipegang, chip) : '') + '.', kabarAwas: true };
  }
  const baris = bangunBaris(chip, j, s); if (!baris) return { kabar: 'Jenis barang belum dikenal', kabarAwas: true };
  const id = 'b' + (s.urutBaris + 1);
  const keranjang = s.keranjang.concat([{ id, trx: baris }]);
  return { keranjang, urutBaris: s.urutBaris + 1, pilih: null, lembar: null, ketik: '', namaRepack: '', kabar: baris.label + ' × ' + tulisJumlah(j, chip) + ' masuk', kabarAwas: false };
}
function tulisJumlah(n, chip) { return String(n).replace('.', ',') + ' ' + (chip.satuan === 'L' ? 'L' : chip.satuan); }
function tulisKg(kg, chip) { return chip.jalur === 'kemasan' ? kg + ' unit' : String(Math.round(kg * 100) / 100).replace('.', ',') + ' kg'; }
/** Bangun ulang satu baris dengan jumlah baru, benderanya (bonus, pengganti retur, nama repack, nego) dipertahankan. */
function bangunUlang(b, chip, j, s, ubah) {
  return bangunBaris(chip, j, s, Object.assign(benderaBaris(b.trx), ubah || {}));
}
/** Langit-langit untuk baris ini tanpa dirinya sendiri di keranjang. */
function maksTanpaBaris(s, id, chip) {
  const lain = Object.assign({}, s, { keranjang: s.keranjang.filter((x) => x.id !== id) }); sinkronKeranjang(lain);
  const maks = maksUntuk(chip); sinkronKeranjang(s);
  return maks;
}
/** Bonus kemasan +1 (NG3): stok & modal menghitung unit + bonus, uang cuma unit bayar. */
export function toggleBonus(s, id) {
  const b = s.keranjang.find((x) => x.id === id); if (!b || b.trx.jenis !== 'kemasan') return {};
  const chip = chipDariBaris(b.trx); if (!chip) return {};
  const bonus = b.trx.bonusUnit ? 0 : 1;
  if (bonus) { const maks = maksTanpaBaris(s, id, chip); if (maks !== null && b.trx.jumlah + 1 > maks) return { kabar: 'Bonus butuh 1 unit lagi dari stok — yang bebas dijual cuma ' + tulisJumlah(maks, chip), kabarAwas: true }; }
  const baru = bangunUlang(b, chip, b.trx.jumlah, s, { bonusUnit: bonus }); if (!baru) return {};
  return { keranjang: s.keranjang.map((x) => (x.id === id ? { id, trx: baru } : x)), kabar: bonus ? b.trx.label + ' +1 bonus — stok & modal ikut ' + baru.jumlahUnit + ' unit, uang tetap ' + b.trx.jumlah : 'Bonus ' + b.trx.label + ' dilepas', kabarAwas: false };
}
/** Pengganti retur (cara lama, untuk tukar TANPA nota): omzet & kas baris ini Rp0, nilai barang jadi jejak; HPP tetap keluar. */
export function togglePenggantiRetur(s, id) {
  const b = s.keranjang.find((x) => x.id === id); if (!b) return {};
  const chip = chipDariBaris(b.trx); if (!chip) return {};
  const nyalakan = !b.trx.penggantiRetur;
  // PENJAGA MODEL B (index.html 19367): tukar yang MENUNJUK nota sudah mengkredit barangnya di dokumen retur — penggantinya wajib dijual PENUH.
  if (nyalakan && s.penggantiTanya !== id) {
    const hari = hariIniIso(s.sekarang);
    const tukarB = ambilRetur().filter((r) => r.tukarModel === 'kreditBarang' && r.tanggal === hari);
    if (tukarB.length) return { penggantiTanya: id, kabar: 'Hari ini ada ' + tukarB.length + ' tukar yang MENUNJUK NOTA — untuk tukar bernota, barang pengganti wajib dijual PENUH. Tanda ini cuma untuk tukar TANPA nota; ketuk sekali lagi kalau memang begitu.', kabarAwas: true };
  }
  const baru = bangunUlang(b, chip, b.trx.jumlah, s, { penggantiRetur: nyalakan }); if (!baru) return {};
  return { keranjang: s.keranjang.map((x) => (x.id === id ? { id, trx: baru } : x)), penggantiTanya: null,
    kabar: nyalakan ? b.trx.label + ' jadi PENGGANTI RETUR — omzet & kas Rp0, nilai barang ' + RP(baru.nilaiBarangPengganti) + ' tercatat, modal tetap keluar' : b.trx.label + ' dijual penuh lagi', kabarAwas: false };
}
function siapaParkir(s, chip) {
  const nama = s.antrean.filter((a) => a.beku.items.some((b) => (chip.jalur === 'kemasan' ? b.trx.jenis === 'kemasan' && kunciKemasan(b.trx.namaProduk, b.trx.ukuranKemasan) === chip.kunci : b.trx.merkSumber === chip.kunci)))
    .map((a, i) => (a.beku.pelanggan || '').trim() || ('pembeli ke-' + (i + 1)));
  return nama.length === 1 ? nama[0] : (nama.length ? nama.length + ' struk diparkir' : '');
}
export function hapusBaris(s, id) { return { keranjang: s.keranjang.filter((b) => b.id !== id), negoId: null, kabar: '' }; }
export function ubahJumlahBaris(s, id, selisih) {
  const b = s.keranjang.find((x) => x.id === id); if (!b) return {};
  const chip = chipDariBaris(b.trx); if (!chip) return {};
  const j = Math.round((b.trx.jumlah + selisih) * 10) / 10;
  if (j <= 0) return hapusBaris(s, id);
  const maks = maksTanpaBaris(s, id, chip);
  const butuh = j + (b.trx.jenis === 'kemasan' ? (b.trx.bonusUnit || 0) : 0);
  if (maks !== null && butuh > maks) return { kabar: 'Yang bebas dijual ' + tulisJumlah(maks, chip) + ' — ' + tulisJumlah(butuh, chip) + (b.trx.bonusUnit ? ' (termasuk bonus)' : '') + ' tidak bisa', kabarAwas: true };
  const baru = bangunUlang(b, chip, j, s); if (!baru) return {};
  return { keranjang: s.keranjang.map((x) => (x.id === id ? { id, trx: baru } : x)), kabar: '' };
}
function chipDariBaris(t) {
  const rak = susunRak({ pelanggan: '', sekarang: null });
  if (t.jenis === 'karung') return rak.karung.find((c) => c.kunci === t.merkSumber && c.berat === (t.beratKarungAcuan || 50)) || null;
  if (t.jenis === 'kemasan') return rak.kemasan.find((c) => c.kunci === kunciKemasan(t.namaProduk, t.ukuranKemasan)) || null;
  if (t.jenis === 'literan') return rak.literan.find((c) => c.kunci === t.merkSumber) || null;
  if (t.jenis === 'repacking') return rak.repack.find((c) => c.kunci === t.merkSumber) || null;
  return null;
}
/** Nego: harga satuan baru; lantai NEGO_LANTAI (Rp500) di atas nol seperti live; di bawah HPP diberi tahu, tidak ditolak (owner: tanpa batas). */
export function terapkanNego(s, id, hargaBaru) {
  const b = s.keranjang.find((x) => x.id === id); if (!b) return {};
  const hg = Math.round(Number(hargaBaru) || 0);
  if (hg < NEGO_LANTAI) return { kabar: 'Harga nego paling rendah ' + RP(NEGO_LANTAI), kabarAwas: true };
  const trx = selesaikanHarga(Object.assign({}, b.trx, { hargaSatuan: hg, nego: true }), !!b.trx.penggantiRetur);
  const hppSatuan = b.trx.jumlah > 0 ? (b.trx.hppTotalSaatJual || 0) / butuhStok(b.trx) : 0;
  const awas = hppSatuan > 0 && hg < hppSatuan;
  return { keranjang: s.keranjang.map((x) => (x.id === id ? { id, trx } : x)), negoId: null, ketik: '', lembar: null,
    kabar: b.trx.label + ' dinego jadi ' + RP(hg) + (awas ? ' — DI BAWAH MODAL (' + RP(hppSatuan) + ')' : ''), kabarAwas: awas };
}
export function setelPotongan(s, nominal) { const sub = s.keranjang.reduce((a, b) => a + (b.trx.hargaTotal || 0), 0); const n = Math.max(0, Math.min(Math.round(Number(nominal) || 0), sub)); return { potongan: n, ketik: '', lembar: null, kabar: n ? 'Potongan ' + RP(n) : 'Potongan dihapus' }; }

// ---------- antrean: parkir memegang stok ----------
export function parkir(s) {
  if (!s.keranjang.length) return { kabar: 'Keranjang kosong — tidak ada yang diparkir', kabarAwas: true };
  // ikatan pesanan ikut diparkir (wzBekuKeranjang 17453) — kalau tidak, ia pindah ke pembeli berikutnya
  const beku = { items: s.keranjang, pelanggan: s.pelanggan, cara: s.cara, uang: s.uang, potongan: s.potongan, pesananId: s.pesananId || null, tukar: s.tukar || null };
  const antrean = s.antrean.filter((a) => a.id !== s.aktifId).concat([{ id: s.aktifId, beku }]);
  return { antrean, keranjang: [], pelanggan: '', cara: 'Tunai', uang: 0, potongan: 0, negoId: null, lembar: null, pesananId: null, tukar: null, penggantiTanya: null,
    aktifId: s.idBerikut, idBerikut: s.idBerikut + 1, kabar: (s.pelanggan || 'Struk') + ' diparkir — stoknya tetap dipegang', kabarAwas: false };
}
export function pakaiAntrean(s, id) {
  const a = s.antrean.find((x) => x.id === id); if (!a) return {};
  // keranjang yang sedang jalan ikut diparkir dulu (tidak dibuang)
  const dasar = s.keranjang.length ? parkir(s) : { antrean: s.antrean };
  const antrean = dasar.antrean.filter((x) => x.id !== id);
  return Object.assign({}, dasar, { antrean, keranjang: a.beku.items, pelanggan: a.beku.pelanggan, cara: a.beku.cara, uang: a.beku.uang, potongan: a.beku.potongan,
    pesananId: a.beku.pesananId || null, tukar: a.beku.tukar || null, aktifId: id, lembar: null, kabar: (a.beku.pelanggan || 'Struk') + ' dibuka lagi', kabarAwas: false });
}
export function buangAntrean(s, id) { const a = s.antrean.find((x) => x.id === id); return { antrean: s.antrean.filter((x) => x.id !== id), kabar: 'Struk dibuang — stoknya bebas lagi' + (a && a.beku.pesananId ? '; ikatan pesanannya dilepas (pesanan tetap belum dibayar)' : '') + (a && a.beku.tukar ? '; ikatan TUKAR ikut dilepas — returnya BELUM tercatat' : '') }; }
export function pembeliLain(s) { return s.keranjang.length ? parkir(s) : { kabar: 'Keranjang sudah kosong' }; }

// ---------- pesanan: BUKAN uang sampai dicatat jual (G5, 21 Agu) ----------
export function daftarPesanan(saring) {
  const k = kunciPelanggan(saring);
  return ambilPesanan().slice().sort((a, b) => String(b.id).localeCompare(String(a.id)))
    .filter((p) => pesananBelumTuntas(p) && (!k || kunciPelanggan(p.namaPelanggan) === k))
    .map((p) => ({ id: String(p.id), nama: p.namaPelanggan || '', isi: p.isi || '', alamat: p.alamat || '', nilai: p.nilaiPerkiraan || 0, status: p.status || 'dipesan', tanggal: p.tanggal || '', jam: p.jam || '' }));
}
export function ambilPesananDoc(id) { return ambilPesanan().find((p) => String(p.id) === String(id)) || null; }
/** Pesanan baru — bentuk simpanPesanan() index.html 16224. */
export function susunPesananBaru(s, w) {
  const nama = String(s.psNama || '').trim(); const isi = String(s.psIsi || '').trim();
  if (!nama) return { tolak: 'Isi nama pemesannya' };
  if (!isi) return { tolak: 'Isi pesanannya apa' };
  const data = { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, namaPelanggan: nama, isi, alamat: String(s.psAlamat || '').trim(),
    nilaiPerkiraan: angkaRupiah(s.psNilai), status: 'dipesan', trxIdJual: null, riwayatStatus: [{ status: 'dipesan', pada: w.kini }] };
  return { dokumen: [{ koleksi: 'pesanan', data }], patch: { psNama: '', psIsi: '', psAlamat: '', psNilai: '', kabar: 'Pesanan ' + nama + ' dicatat — belum uang, belum stok; jadi DIBAYAR begitu notanya dicatat', kabarAwas: false } };
}
function pesananGanti(ps, status, w, trxId) {
  const d = Object.assign({}, ps, { status, riwayatStatus: (ps.riwayatStatus || []).concat([{ status, pada: w.kini }]) });
  if (trxId !== undefined) d.trxIdJual = trxId;
  return { koleksi: 'pesanan', data: d };
}
/** dipesan → diantar (majukanPesanan 16243); DIBAYAR hanya lewat catat jual. */
export function susunPesananAntar(id, w) {
  const ps = ambilPesananDoc(id); if (!ps) return { tolak: 'Pesanan tidak ditemukan' };
  if (ps.status !== 'dipesan') return { tolak: 'Pesanan ini sudah ' + (STATUS_PESANAN[ps.status] || ps.status) };
  return { dokumen: [pesananGanti(ps, 'diantar', w)], patch: { kabar: 'Pesanan ' + ps.namaPelanggan + ' → DIANTAR. Uang & stok baru bergerak saat notanya dicatat.', kabarAwas: false } };
}
export function susunPesananBatal(id, w) {
  const ps = ambilPesananDoc(id); if (!ps) return { tolak: 'Pesanan tidak ditemukan' };
  if (!pesananBelumTuntas(ps)) return { tolak: 'Pesanan ini sudah ' + (STATUS_PESANAN[ps.status] || ps.status) };
  return { dokumen: [pesananGanti(ps, 'batal', w)], patch: { kabar: 'Pesanan ' + ps.namaPelanggan + ' dibatalkan — jejaknya tetap tersimpan', kabarAwas: false } };
}
/** Ikat keranjang ke pesanan (catatJualPesanan 16284): nama ikut, begitu nota dicatat pesanan jadi DIBAYAR. */
export function ikatPesanan(s, id) {
  const ps = ambilPesananDoc(id); if (!ps || !pesananBelumTuntas(ps)) return { kabar: 'Pesanan itu sudah tuntas atau tidak ada', kabarAwas: true };
  if (s.tukar) return { kabar: 'Keranjang sedang terikat TUKAR (' + s.tukar.ringkas + '). Catat notanya atau batal tukar dulu, baru catat jual pesanan.', kabarAwas: true };
  return { pesananId: String(ps.id), pelanggan: String(ps.namaPelanggan || '').trim(), lembar: null, kabar: 'Susun keranjang untuk pesanan ' + ps.namaPelanggan + ' (' + (ps.isi || '') + ') — begitu dicatat, pesanan otomatis DIBAYAR', kabarAwas: false };
}
export function lepasPesanan(s) { return { pesananId: null, kabar: 'Ikatan pesanan dilepas — barang di keranjang tetap, pesanan tetap belum dibayar' }; }

// ---------- bayar ----------
export function pilihCara(s, cara) { return { cara: bakuCaraBayar(cara), uang: 0, kabar: '' }; }
export function tambahUang(s, pecahan) { return { uang: (s.uang || 0) + pecahan }; }
export function uangPas(s) { return { uang: hitungTagihan(s).total }; }
export function uangKetik(s) { const n = angkaKetik(s.ketik); return n > 0 ? { uang: n, ketik: '' } : {}; }

/** KR1 — sama dengan wzKreditTerkunci() index.html, tanpa DOM; null = boleh. */
export function alasanKunciKredit(s, totalKredit) {
  const nama = String(s.pelanggan || '').trim();
  if (!nama) return 'Isi nama pelanggan untuk penjualan kredit.';
  if (s.kreditDibuka) return null;   // owner membuka kredit sekali untuk nota ini (jejaknya kreditDibukaOwner)
  const info = infoKreditPelanggan(nama);
  if (!info.terdaftar) return nama + ' belum terdaftar di buku Pelanggan — kredit dimatikan (KR1). Isi ciri, catatan, atau rute di kartunya dulu.';
  if (info.batas <= 0) return 'Belum ada riwayat belanja — batas kredit belum terbentuk (KR1).';
  if (info.sisa + totalKredit > info.batas) return 'Melewati batas kredit ' + RP(info.batas) + ' (bon ' + RP(info.sisa) + ' + nota ini ' + RP(totalKredit) + ').';
  return null;
}
/** Stok dicek ULANG saat mencatat (bisa berubah sejak dimasukkan): baris pertama yang melampaui langit-langit. */
export function periksaStokKeranjang(s) {
  for (const b of s.keranjang) {
    const chip = chipDariBaris(b.trx); if (!chip) continue;
    const maks = maksTanpaBaris(s, b.id, chip);
    if (maks !== null && butuhStok(b.trx) > maks) return b.trx.label + ': yang bebas dijual tinggal ' + tulisJumlah(maks, chip) + ', di keranjang ' + tulisJumlah(butuhStok(b.trx), chip) + (b.trx.bonusUnit ? ' (termasuk bonus)' : '');
  }
  return '';
}
/** Alasan nota belum bisa dicatat — '' kalau sah. */
export function alasanTolak(s) {
  if (!s.keranjang.length) return 'Keranjang kosong';
  const t = hitungTagihan(s);
  const nama = kunciPelanggan(s.pelanggan);
  if (s.tukar) {   // simpanKeranjangJual 19103–19123
    if (s.cara === 'Kredit') return 'Tukar tidak bisa dicatat BON — barangnya dibayar dengan barang yang kembali, bukan dengan utang. Pilih Tunai atau QRIS.';
    if (t.bersih < 0) return 'Nilai retur ' + RP(t.kredit) + ' lebih besar dari keranjang pengganti ' + RP(t.subtotal - t.potongan) + ' — tambah barang, atau batal tukar lalu catat sebagai uang kembali';
    if (t.uang > 0 && t.uang < t.total) return 'Tukar tidak bisa dibayar sebagian: diterima ' + RP(t.uang) + ', yang harus dibayar ' + RP(t.total);
    const cek = cekDrafTukar(s.tukar.returDraf); if (cek) return cek;
  }
  if (s.cara === 'Kredit' && !nama) return 'Bon harus ada nama pembelinya';
  if (t.sisaJadiBon && !nama) return 'Uangnya kurang ' + RP(t.kurang) + ' — sisanya jadi bon, pilih nama pembelinya dulu';
  if (s.cara === 'Tunai' && t.uang <= 0 && t.total > 0) return 'Ketuk uang yang diterima (atau PAS)';
  if (s.cara === 'Kredit') { const k = alasanKunciKredit(s, t.total); if (k) return k; }   // bayar sebagian TIDAK kena KR1 (seperti live)
  if (s.pesananId) { const ps = ambilPesananDoc(s.pesananId); if (!ps || !pesananBelumTuntas(ps)) return 'Pesanan yang diikat sudah tuntas/tidak ada — lepas ikatannya dulu'; }
  return '';
}

/**
 * Susun dokumen nota — bentuk & urutan angka PERSIS simpanKeranjangJual() index.html:
 *   potongan proporsional (sisa ke baris terakhir) → pembulatan melekat ke baris terakhir bernilai →
 *   uang kurang: semua baris KREDIT + satu pelunasan piutang sebesar uang yang diterima →
 *   literan berkantong: dokumen stokBahanLiteran {id: id+1, tipe 'pakai'}.
 * w = { tanggal, jam, idUnik } supaya bisa diuji tanpa jam dinding.
 */
export function susunNotaDokumen(s, w) {
  const items = s.keranjang.map((b) => Object.assign({}, b.trx));
  const nama = String(s.pelanggan || '').trim();
  const subtotal = items.reduce((a, t) => a + t.hargaTotal, 0);
  const pot = Math.max(0, Math.round(s.potongan || 0));
  const potDipakai = Math.min(pot, subtotal);
  const totalSetelahPot = subtotal - potDipakai;
  let cara = bakuCaraBayar(s.cara); const caraAsli = cara;
  const tk = s.tukar || null; const kreditTukar = tk ? Math.round(tk.kredit || 0) : 0;
  const bulatNota = pembulatanTagihan(totalSetelahPot - kreditTukar, cara);   // atas SELISIH BERSIH bila tukar
  const tagihan = totalSetelahPot - kreditTukar + bulatNota;
  let bayarSebagian = 0;
  const uang = cara === 'Tunai' ? Math.round(s.uang || 0) : 0;
  if (cara !== 'Kredit' && uang > 0 && uang < tagihan) { bayarSebagian = uang; cara = 'Kredit'; }
  let terpakai = 0;
  items.forEach((t, i) => {
    const bagian = i === items.length - 1 ? potDipakai - terpakai : Math.min(t.hargaTotal, Math.round(potDipakai * t.hargaTotal / (subtotal || 1)));
    terpakai += bagian;
    if (bagian > 0) { t.potonganTransaksi = bagian; t.hargaTotal -= bagian; }
  });
  if (bulatNota > 0) { for (let i = items.length - 1; i >= 0; i--) { if (items[i].hargaTotal > 0) { items[i].pembulatan = bulatNota; items[i].hargaTotal += bulatNota; break; } } }
  const totalBayar = items.reduce((a, t) => a + t.hargaTotal, 0);
  const trxId = w.idUnik();
  const dokumen = [];
  items.forEach((t) => {
    const d = Object.assign({}, t);
    ['label', 'satuan', 'jumlah', 'hargaSatuan', 'hargaAsli', 'nego'].forEach((k) => { delete d[k]; });
    d.id = w.idUnik(); d.trxId = trxId; d.tanggal = w.tanggal; d.jam = w.jam; d.caraBayar = cara; d.namaPelanggan = nama;
    d.hargaAsliSatuan = t.hargaAsli;                                   // harga daftar sebelum tawar (kebal riwayat)
    if (t.nego) d.negoSelisih = t.hargaSatuan - t.hargaAsli;          // jejak tawar (NG1)
    if (tk) d.tukarReturId = String(tk.returDraf.id);                  // tautan ke retur tukarnya (19175)
    if (cara === 'Kredit' && s.kreditDibuka) d.kreditDibukaOwner = true;
    if (uang > 0 && cara === 'Tunai') { d.uangDiterima = uang; d.kembalian = Math.max(0, uang - (totalBayar - kreditTukar)); }
    dokumen.push({ koleksi: 'penjualan', data: d });
    if (d.kemasanLiteran && d.jumlahKemasanLiteranDipakai > 0) {
      dokumen.push({ koleksi: 'stokBahanLiteran', data: { id: d.id + 1, tipe: 'pakai', jenis: d.kemasanLiteran, jumlah: d.jumlahKemasanLiteranDipakai,
        hargaTotal: 0, tanggal: w.tanggal, catatan: 'Otomatis dari penjualan literan id ' + d.id } });
    }
  });
  let piutangId = null;
  if (bayarSebagian > 0) {
    piutangId = w.idUnik();
    dokumen.push({ koleksi: 'piutangMutasi', data: { id: piutangId, tipe: 'bayar', namaPelanggan: nama, nominal: bayarSebagian, tanggal: w.tanggal, jam: w.jam,
      caraBayar: caraAsli, dicatatDi: 'sistem', catatan: 'Dibayar langsung saat beli — sisa ' + RP(totalBayar - bayarSebagian) + ' jadi piutang' } });
  }
  // RETUR TUKAR lahir BERSAMA penjualan penggantinya — satu batch (index.html menulis penjualan dulu lalu retur, dijaga jurnal
  // localStorage kalau halaman mati di antaranya; di sini keduanya masuk atau tidak sama sekali). Bentuk: 19165.
  let retur = null;
  if (tk) {
    const rd = Object.assign({}, tk.returDraf, { tanggal: w.tanggal, jam: w.jam, penjualanPenggantiTrxId: String(trxId),
      hitunganTukarSistem: { pengganti: totalSetelahPot, kredit: kreditTukar, bersih: totalSetelahPot - kreditTukar, pembulatan: bulatNota, caraBayar: cara, dibayarPembeli: tagihan, dikembalikanToko: 0 } });
    dokumen.push({ koleksi: 'retur', data: rd });
    if (rd.kondisi === 'tidak_utuh') dokumen.push(dokumenKarantina(rd));
    retur = { id: rd.id, karantina: rd.kondisi === 'tidak_utuh' };
  }
  // PESANAN yang diikat ikut DIBAYAR dalam satu tulisan (tutupPesananDariJual 16272 menulisnya terpisah sesudah nota — di sini satu batch)
  let pesanan = null;
  if (s.pesananId) {
    const ps = ambilPesananDoc(s.pesananId);
    if (ps && pesananBelumTuntas(ps)) { dokumen.push(pesananGanti(ps, 'dibayar', w, trxId)); pesanan = { id: String(ps.id), statusSebelum: ps.status || 'dipesan', nama: ps.namaPelanggan || '' }; }
  }
  const nPengganti = items.filter((t) => t.penggantiRetur).length;
  const ket = [items.length + ' barang · ' + RP(totalBayar)];
  if (nPengganti) ket.push(nPengganti + ' pengganti retur Rp0');
  if (potDipakai > 0) ket.push('potongan ' + RP(potDipakai));
  if (bulatNota > 0) ket.push('dibulatkan +' + RP(bulatNota));
  if (bayarSebagian > 0) ket.push('dibayar ' + RP(bayarSebagian) + ' · BON ' + RP(totalBayar - bayarSebagian) + ' atas nama ' + nama);
  else if (cara === 'Kredit') ket.push('BON atas nama ' + nama);
  else if (uang > totalBayar - kreditTukar) ket.push('kembalian ' + RP(uang - (totalBayar - kreditTukar)));
  if (tk) ket.push('TUKAR: barang kembali ' + RP(kreditTukar) + ' · pembeli bayar ' + RP(tagihan));
  if (pesanan) ket.push('pesanan ' + pesanan.nama + ' DIBAYAR');
  return { dokumen, trxId, totalBayar, tagihan, bulatNota, potDipakai, bayarSebagian, cara, ringkas: ket.join(' · '),
    idPenjualan: dokumen.filter((x) => x.koleksi === 'penjualan').map((x) => x.data.id), piutangId, pesanan, retur };
}

/** Jam dinding untuk mencatat (dipisah supaya uji bisa memberi jam tetap). */
export function waktuSekarang(d) {
  d = d || new Date();
  return { tanggal: hariIniIso(d), jam: d.toTimeString().slice(0, 5), kini: new Date().toISOString(), idUnik: () => Date.now() + Math.random() };
}

/** Siapkan pencatatan: {tolak} atau {dokumen, patch, ringkas}. Menulisnya urusan layar (lewat toko.tulisDokumen). */
export function simpanNota(s, w) {
  const tolak = alasanTolak(s) || periksaStokKeranjang(s);
  if (tolak) return { tolak };
  const n = susunNotaDokumen(s, w || waktuSekarang(s.sekarang || undefined));
  const patch = { keranjang: [], pelanggan: '', cara: 'Tunai', uang: 0, potongan: 0, negoId: null, lembar: null, ketik: '', kreditDibuka: false, pesananId: null, penggantiTanya: null, tukar: null,
    notaTerakhir: { trxId: n.trxId, idPenjualan: n.idPenjualan, piutangId: n.piutangId, pesanan: n.pesanan, retur: n.retur, pada: Date.now(), ringkas: n.ringkas, nama: String(s.pelanggan || '').trim() },
    kabar: 'Tersimpan — ' + n.ringkas, kabarAwas: false };
  return { dokumen: n.dokumen, patch, ringkas: n.ringkas, nota: n };
}

/** Batalkan nota barusan: tiap baris ditandai dibatalkan (tidak dihapus, seperti mulaiBatalkanTrx live); kantong literan, pelunasan sebagian, dan status pesanan dipulihkan. */
export function susunPembatalan(notaTerakhir, alasan, w) {
  if (!notaTerakhir) return null;
  const ids = notaTerakhir.idPenjualan.map(String);
  const baris = ambilPenjualanSemua().filter((p) => ids.indexOf(String(p.id)) >= 0 && !p.dibatalkan);
  if (!baris.length) return null;
  const kini = (w && w.kini) || new Date().toISOString();
  const dokumen = baris.map((p) => ({ koleksi: 'penjualan', data: Object.assign({}, p, { dibatalkan: true, alasanKoreksi: alasan || 'Diurungkan dari sistem baru', dikoreksiPada: kini, dibatalkanPada: kini }) }));
  const hapus = baris.filter((p) => p.jenis === 'literan' && p.kemasanLiteran).map((p) => ({ koleksi: 'stokBahanLiteran', id: p.id + 1 }));
  if (notaTerakhir.piutangId) hapus.push({ koleksi: 'piutangMutasi', id: notaTerakhir.piutangId });
  // nota TUKAR: retur (+ karantina) lahir bersama nota ini, jadi ikut dicabut — kalau tidak, barang tercatat kembali tanpa penggantinya
  if (notaTerakhir.retur) { hapus.push({ koleksi: 'retur', id: notaTerakhir.retur.id }); if (notaTerakhir.retur.karantina) hapus.push({ koleksi: 'karantina', id: notaTerakhir.retur.id }); }
  if (notaTerakhir.pesanan) {
    const ps = ambilPesananDoc(notaTerakhir.pesanan.id);
    if (ps && ps.status === 'dibayar' && String(ps.trxIdJual) === String(notaTerakhir.trxId)) dokumen.push(pesananGanti(ps, notaTerakhir.pesanan.statusSebelum, { kini }, null));
  }
  return { dokumen, hapus, jumlah: baris.length };
}
export const BATAS_URUNGKAN_DETIK = 90;

// ---------- tukar: retur yang diikat ke keranjang ----------
/** Ikat draf retur tukar ke keranjang (tkIkat 16926): satu ikatan per keranjang; tukar & pesanan saling meniadakan (16957). */
export function ikatTukar(s, ikat) {
  if (s.tukar) return { kabar: 'Keranjang ini MASIH terikat tukar: ' + s.tukar.ringkas + '. Catat notanya atau batal tukar dulu.', kabarAwas: true };
  return { tukar: ikat, pesananId: null, cara: s.cara === 'Kredit' ? 'Tunai' : s.cara };
}
export function batalTukar(s) { return s.tukar ? { tukar: null, kabar: 'Tukar dibatalkan — returnya TIDAK tercatat; barang di keranjang tetap', kabarAwas: false } : {}; }

// ---------- wadah literan: tinggi isi & penanda isi ulang ----------
const cap = (p) => (p.tanggal || '') + ' ' + (p.jam || '');
/**
 * Tinggi isi satu wadah SEKARANG: isi saat terakhir ditandai diisi ulang − literan merek itu yang terjual sesudahnya
 * − literan merek itu yang sedang di keranjang / struk parkir (supaya gunungnya turun begitu barang masuk keranjang).
 * null = merek ini bukan wadah (diserok dari karung). diketahui:false = belum pernah ditandai → layar MENOLAK menggambar isi.
 */
export function tinggiWadah(merk, s) {
  if (DAFTAR_WADAH.indexOf(merk) < 0) return null;
  const tanda = ambilWadahLiteran().filter((w) => w.wadah === merk && w.tipe === 'isi').sort((a, b) => cap(b).localeCompare(cap(a)) || String(b.id).localeCompare(String(a.id)))[0];
  if (!tanda) return { wadah: true, diketahui: false, penuhKg: WADAH_PENUH_KG };
  const sejak = cap(tanda);
  const terjual = ambilPenjualan().reduce((a, p) => a + (p.jenis === 'literan' && p.merkSumber === merk && cap(p) > sejak ? (p.totalKg || 0) : 0), 0);
  const literKeranjang = (daftar) => (daftar || []).reduce((a, b) => a + (b.trx.jenis === 'literan' && b.trx.merkSumber === merk ? (b.trx.totalKg || 0) : 0), 0);
  const dipegang = literKeranjang(s && s.keranjang) + ((s && s.antrean) || []).reduce((a, x) => a + literKeranjang(x.beku.items), 0);
  const isi = Number(tanda.isiKg) || WADAH_PENUH_KG;
  const sisaKg = Math.round((isi - terjual - dipegang) * 100) / 100;
  const bagian = Math.max(0, Math.min(1, sisaKg / WADAH_PENUH_KG));
  return { wadah: true, diketahui: true, penuhKg: WADAH_PENUH_KG, sisaKg: Math.max(0, sisaKg), lewat: sisaKg < 0 ? -sisaKg : 0, bagian,
    gunung: Math.max(0, Math.min(1, (bagian - WADAH_RATA_BAGIAN) / (1 - WADAH_RATA_BAGIAN))), dalam: Math.max(0, Math.min(1, bagian / WADAH_RATA_BAGIAN)),
    perluIsi: sisaKg <= WADAH_ISI_ULANG_KG, sejakTanggal: tanda.tanggal || '', sejakJam: tanda.jam || '' };
}
/** Tandai wadah baru diisi ulang (penuh, menggunung lagi). Dokumen koleksi wadahLiteran — alat ukur, bukan stok. */
export function susunIsiUlangWadah(merk, w) {
  if (DAFTAR_WADAH.indexOf(merk) < 0) return { tolak: merk + ' bukan wadah kotak — literannya diserok langsung dari karung' };
  return { dokumen: [{ koleksi: 'wadahLiteran', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, wadah: merk, tipe: 'isi', isiKg: WADAH_PENUH_KG } }],
    patch: { kabar: 'Wadah ' + merk + ' ditandai PENUH lagi (±' + WADAH_PENUH_KG + ' kg, menggunung) — dihitung turun dari penjualan literan berikutnya', kabarAwas: false } };
}
