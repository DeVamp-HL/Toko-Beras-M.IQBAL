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
import { hitungStokKarungPerMerk, hitungStokKemasan, hitungStokBahanLiteran, hitungPiutang, stokMaksJalur } from '../mesin/beku.js';
import { kunciKemasan, kunciPelanggan, bulatKeAtas500, bakuCaraBayar, merkPunyaKarungBerat, hargaKarungUtuh,
  tentukanKemasanLiteran, jumlahKemasanLiteran, hargaBahanLiteranEfektif, catatanPelangganBerisi, infoKreditPelanggan,
  pesananBelumTuntas, RASIO_KONVERSI, RASIO_DEFAULT, NEGO_LANTAI } from '../mesin/pembantu.js';
import { ambilHargaKemasan, ambilHargaLiteran, ambilPenjualan, ambilPenjualanSemua, ambilPelangganCatatan, ambilPesanan, setelKeranjang,
  wzDiKeranjangParkir, sumberData } from '../data/toko.js';
import { hariIniIso, RP } from '../inti/format.js';

export const JALUR = [['sering', 'Sering'], ['literan', 'Literan'], ['kemasan', 'Kemasan'], ['karung', 'Karung']];
export const JALUR_NANTI = [['wadah', 'Wadah'], ['repack', 'Repack'], ['retur', 'Retur']];   // putaran berikutnya
export const PECAHAN = [100000, 50000, 20000, 10000, 5000, 2000, 1000, 500];

export function keadaanAwal() {
  return {
    jalur: 'sering', lembar: null, pilih: null, ketik: '', satuanKarung: 50,
    keranjang: [], negoId: null, potongan: 0,
    pelanggan: '', cariPelanggan: '', cara: 'Tunai', uang: 0,
    antrean: [], aktifId: 1, idBerikut: 2, urutBaris: 0,
    kreditDibuka: false, notaTerakhir: null,
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
  const rak = { karung: [], kemasan: [], literan: [] };
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
  rak.kemasan.sort((a, b) => a.nama.localeCompare(b.nama) || a.ukuranKg - b.ukuranKg);
  // SERING: barang yang biasa dibeli orang ini (90 hari); tanpa nama → yang paling laku 28 hari terakhir
  rak.sering = susunSering(s, rak);
  return rak;
}

function kunciBaris(p) {
  if (p.jenis === 'kemasan') return 'kemasan|' + kunciKemasan(p.namaProduk, p.ukuranKemasan);
  if (p.jenis === 'karung') return 'karung|' + p.merkSumber + '|' + (p.beratKarungAcuan || 50);
  if (p.jenis === 'literan') return 'literan|' + p.merkSumber;
  return null;
}
function susunSering(s, rak) {
  const semua = [].concat(rak.karung.map((c) => Object.assign({}, c, { id: 'karung|' + c.kunci + '|' + c.berat })),
    rak.kemasan.map((c) => Object.assign({}, c, { id: 'kemasan|' + c.kunci })),
    rak.literan.map((c) => Object.assign({}, c, { id: 'literan|' + c.kunci })));
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

/** Baris keranjang dari chip + jumlah, dengan bentuk trx yang SAMA dengan penjualan index.html. */
export function bangunBaris(chip, jumlah, s) {
  const j = Number(jumlah) || 0;
  if (j <= 0) return null;
  if (chip.jalur === 'karung') {
    const totalKg = j * chip.berat;
    return { jenis: 'karung', merkSumber: chip.kunci, jumlahKarung: j, beratKarungAcuan: chip.berat, totalKg,
      namaProduk: chip.kunci + ' (karung utuh)', hargaSatuan: chip.harga, hargaAsli: chip.harga, hargaTotal: Math.round(chip.harga * j),
      hppTotalSaatJual: Math.round((chip.hppPerKg || 0) * totalKg), label: chip.nama + ' ' + chip.berat + ' kg', satuan: 'karung', jumlah: j };
  }
  if (chip.jalur === 'kemasan') {
    return { jenis: 'kemasan', namaProduk: chip.nama, ukuranKemasan: chip.ukuranKg, jumlahUnit: j, totalKg: chip.ukuranKg * j,
      hargaSatuan: chip.harga, hargaAsli: chip.harga, hargaTotal: Math.round(chip.harga * j), hppTotalSaatJual: Math.round((chip.hppPerUnit || 0) * j),
      label: chip.nama + ' ' + chip.ukuranKg + ' kg', satuan: 'kemasan', jumlah: j };
  }
  if (chip.jalur === 'literan') {
    const rasio = chip.rasio || rasioMerk(chip.kunci);
    const totalKg = Math.round(j * rasio * 1000) / 1000;
    const jenisK = tentukanKemasanLiteran(j); const nK = jenisK ? jumlahKemasanLiteran(j) : 0;
    const biayaK = jenisK ? hargaBahanLiteranEfektif(jenisK, hitungStokBahanLiteran()) * nK : 0;
    return { jenis: 'literan', merkSumber: chip.kunci, namaProduk: chip.kunci, jumlahLiter: j, rasioPakai: rasio, totalKg,
      hargaSatuan: chip.harga, hargaAsli: chip.harga, hargaTotal: Math.round(chip.harga * j), hppTotalSaatJual: Math.round((chip.hppPerKg || 0) * totalKg) + biayaK,
      kemasanLiteran: jenisK, biayaKemasanLiteran: biayaK, jumlahKemasanLiteranDipakai: nK, label: chip.nama + ' literan', satuan: 'L', jumlah: j };
  }
  return null;
}

/** Langit-langit stok untuk chip ini SEKARANG (keranjang aktif + parkir sudah dikurangi oleh mesin). */
export function maksUntuk(chip) {
  if (chip.jalur === 'karung') { setelBeratDom(chip.berat); return stokMaksJalur('karung', chip.kunci); }
  if (chip.jalur === 'kemasan') return stokMaksJalur('kemasan', chip.kunci);
  if (chip.jalur === 'literan') return bebasLiter(chip.kunci, chip.rasio || rasioMerk(chip.kunci));
  return null;
}
/** Liter yang bebas dijual: kolam kg merek itu dikurangi yang dipegang struk parkir & keranjang aktif (kolam yang sama dengan karung). */
function bebasLiter(merk, rasio) {
  const sisaKg = (hitungStokKarungPerMerk()[merk] || {}).sisaKg || 0;
  const dipakai = wzDiKeranjangParkir('karung', merk) + jumlahAktifKg(merk);
  return Math.max(0, Math.floor((sisaKg - dipakai) / rasio * 10) / 10);
}
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
  const bersih = subtotal - potongan;
  const bulat = pembulatanTagihan(bersih, s.cara);
  const total = bersih + bulat;
  const uang = s.cara === 'Tunai' ? Math.round(s.uang || 0) : 0;
  const kembalian = s.cara === 'Tunai' ? Math.max(0, uang - total) : 0;
  const kurang = s.cara === 'Tunai' && uang > 0 ? Math.max(0, total - uang) : 0;
  return { subtotal, potongan, bersih, bulat, total, uang, kembalian, kurang, sisaJadiBon: kurang > 0 };
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
  if (t === ',') { if (s.ketik.indexOf(',') >= 0 || (s.pilih && s.pilih.jalur !== 'literan')) return {}; return { ketik: (s.ketik || '0') + ',' }; }
  if (!/^\d+$/.test(t)) return {};
  if (s.ketik === '' && t === '0') return {};
  if ((s.ketik + t).replace(',', '').length > 9) return {};
  return { ketik: s.ketik + t };
}
export const angkaKetik = (teks) => parseFloat(String(teks || '').replace(',', '.')) || 0;

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
  return { keranjang, urutBaris: s.urutBaris + 1, pilih: null, lembar: null, ketik: '', kabar: baris.label + ' × ' + tulisJumlah(j, chip) + ' masuk', kabarAwas: false };
}
function tulisJumlah(n, chip) { return String(n).replace('.', ',') + ' ' + (chip.satuan === 'L' ? 'L' : chip.satuan); }
function tulisKg(kg, chip) { return chip.jalur === 'kemasan' ? kg + ' unit' : String(Math.round(kg * 100) / 100).replace('.', ',') + ' kg'; }
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
  const lain = Object.assign({}, s, { keranjang: s.keranjang.filter((x) => x.id !== id) }); sinkronKeranjang(lain);
  const maks = maksUntuk(chip);
  if (maks !== null && j > maks) return { kabar: 'Yang bebas dijual ' + tulisJumlah(maks, chip) + ' — ' + tulisJumlah(j, chip) + ' tidak bisa', kabarAwas: true };
  const baru = bangunBaris(chip, j, s); if (!baru) return {};
  if (b.trx.nego) { baru.hargaSatuan = b.trx.hargaSatuan; baru.hargaTotal = Math.round(b.trx.hargaSatuan * j); baru.nego = true; }
  return { keranjang: s.keranjang.map((x) => (x.id === id ? { id, trx: baru } : x)), kabar: '' };
}
function chipDariBaris(t) {
  const rak = susunRak({ pelanggan: '', sekarang: null });
  if (t.jenis === 'karung') return rak.karung.find((c) => c.kunci === t.merkSumber && c.berat === (t.beratKarungAcuan || 50)) || null;
  if (t.jenis === 'kemasan') return rak.kemasan.find((c) => c.kunci === kunciKemasan(t.namaProduk, t.ukuranKemasan)) || null;
  if (t.jenis === 'literan') return rak.literan.find((c) => c.kunci === t.merkSumber) || null;
  return null;
}
/** Nego: harga satuan baru; lantai NEGO_LANTAI (Rp500) di atas nol seperti live; di bawah HPP diberi tahu, tidak ditolak (owner: tanpa batas). */
export function terapkanNego(s, id, hargaBaru) {
  const b = s.keranjang.find((x) => x.id === id); if (!b) return {};
  const hg = Math.round(Number(hargaBaru) || 0);
  if (hg < NEGO_LANTAI) return { kabar: 'Harga nego paling rendah ' + RP(NEGO_LANTAI), kabarAwas: true };
  const trx = Object.assign({}, b.trx, { hargaSatuan: hg, hargaTotal: Math.round(hg * b.trx.jumlah), nego: true });
  const hppSatuan = b.trx.jumlah > 0 ? (b.trx.hppTotalSaatJual || 0) / b.trx.jumlah : 0;
  const awas = hppSatuan > 0 && hg < hppSatuan;
  return { keranjang: s.keranjang.map((x) => (x.id === id ? { id, trx } : x)), negoId: null, ketik: '', lembar: null,
    kabar: b.trx.label + ' dinego jadi ' + RP(hg) + (awas ? ' — DI BAWAH MODAL (' + RP(hppSatuan) + ')' : ''), kabarAwas: awas };
}
export function setelPotongan(s, nominal) { const sub = s.keranjang.reduce((a, b) => a + (b.trx.hargaTotal || 0), 0); const n = Math.max(0, Math.min(Math.round(Number(nominal) || 0), sub)); return { potongan: n, ketik: '', lembar: null, kabar: n ? 'Potongan ' + RP(n) : 'Potongan dihapus' }; }

// ---------- antrean: parkir memegang stok ----------
export function parkir(s) {
  if (!s.keranjang.length) return { kabar: 'Keranjang kosong — tidak ada yang diparkir', kabarAwas: true };
  const beku = { items: s.keranjang, pelanggan: s.pelanggan, cara: s.cara, uang: s.uang, potongan: s.potongan };
  const antrean = s.antrean.filter((a) => a.id !== s.aktifId).concat([{ id: s.aktifId, beku }]);
  return { antrean, keranjang: [], pelanggan: '', cara: 'Tunai', uang: 0, potongan: 0, negoId: null, lembar: null,
    aktifId: s.idBerikut, idBerikut: s.idBerikut + 1, kabar: (s.pelanggan || 'Struk') + ' diparkir — stoknya tetap dipegang', kabarAwas: false };
}
export function pakaiAntrean(s, id) {
  const a = s.antrean.find((x) => x.id === id); if (!a) return {};
  // keranjang yang sedang jalan ikut diparkir dulu (tidak dibuang)
  const dasar = s.keranjang.length ? parkir(s) : { antrean: s.antrean };
  const antrean = dasar.antrean.filter((x) => x.id !== id);
  return Object.assign({}, dasar, { antrean, keranjang: a.beku.items, pelanggan: a.beku.pelanggan, cara: a.beku.cara, uang: a.beku.uang, potongan: a.beku.potongan, aktifId: id, lembar: null, kabar: (a.beku.pelanggan || 'Struk') + ' dibuka lagi', kabarAwas: false });
}
export function buangAntrean(s, id) { return { antrean: s.antrean.filter((x) => x.id !== id), kabar: 'Struk dibuang — stoknya bebas lagi' }; }
export function pembeliLain(s) { return s.keranjang.length ? parkir(s) : { kabar: 'Keranjang sudah kosong' }; }

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
    const lain = Object.assign({}, s, { keranjang: s.keranjang.filter((x) => x.id !== b.id) }); sinkronKeranjang(lain);
    const maks = maksUntuk(chip);
    if (maks !== null && b.trx.jumlah > maks) { sinkronKeranjang(s); return b.trx.label + ': yang bebas dijual tinggal ' + tulisJumlah(maks, chip) + ', di keranjang ' + tulisJumlah(b.trx.jumlah, chip); }
  }
  sinkronKeranjang(s);
  return '';
}
/** Alasan nota belum bisa dicatat — '' kalau sah. */
export function alasanTolak(s) {
  if (!s.keranjang.length) return 'Keranjang kosong';
  const t = hitungTagihan(s);
  const nama = kunciPelanggan(s.pelanggan);
  if (s.cara === 'Kredit' && !nama) return 'Bon harus ada nama pembelinya';
  if (t.sisaJadiBon && !nama) return 'Uangnya kurang ' + RP(t.kurang) + ' — sisanya jadi bon, pilih nama pembelinya dulu';
  if (s.cara === 'Tunai' && t.uang <= 0) return 'Ketuk uang yang diterima (atau PAS)';
  if (s.cara === 'Kredit') { const k = alasanKunciKredit(s, t.total); if (k) return k; }   // bayar sebagian TIDAK kena KR1 (seperti live)
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
  const bulatNota = pembulatanTagihan(totalSetelahPot, cara);
  const tagihan = totalSetelahPot + bulatNota;
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
    if (cara === 'Kredit' && s.kreditDibuka) d.kreditDibukaOwner = true;
    if (uang > 0 && cara === 'Tunai') { d.uangDiterima = uang; d.kembalian = Math.max(0, uang - totalBayar); }
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
  const ket = [items.length + ' barang · ' + RP(totalBayar)];
  if (potDipakai > 0) ket.push('potongan ' + RP(potDipakai));
  if (bulatNota > 0) ket.push('dibulatkan +' + RP(bulatNota));
  if (bayarSebagian > 0) ket.push('dibayar ' + RP(bayarSebagian) + ' · BON ' + RP(totalBayar - bayarSebagian) + ' atas nama ' + nama);
  else if (cara === 'Kredit') ket.push('BON atas nama ' + nama);
  else if (uang > totalBayar) ket.push('kembalian ' + RP(uang - totalBayar));
  return { dokumen, trxId, totalBayar, tagihan, bulatNota, potDipakai, bayarSebagian, cara, ringkas: ket.join(' · '),
    idPenjualan: dokumen.filter((x) => x.koleksi === 'penjualan').map((x) => x.data.id), piutangId };
}

/** Jam dinding untuk mencatat (dipisah supaya uji bisa memberi jam tetap). */
export function waktuSekarang(d) {
  d = d || new Date();
  return { tanggal: hariIniIso(d), jam: d.toTimeString().slice(0, 5), idUnik: () => Date.now() + Math.random() };
}

/** Siapkan pencatatan: {tolak} atau {dokumen, patch, ringkas}. Menulisnya urusan layar (lewat toko.tulisDokumen). */
export function simpanNota(s, w) {
  const tolak = alasanTolak(s) || periksaStokKeranjang(s);
  if (tolak) return { tolak };
  const n = susunNotaDokumen(s, w || waktuSekarang(s.sekarang || undefined));
  const patch = { keranjang: [], pelanggan: '', cara: 'Tunai', uang: 0, potongan: 0, negoId: null, lembar: null, ketik: '', kreditDibuka: false,
    notaTerakhir: { trxId: n.trxId, idPenjualan: n.idPenjualan, piutangId: n.piutangId, pada: Date.now(), ringkas: n.ringkas, nama: String(s.pelanggan || '').trim() },
    kabar: 'Tersimpan — ' + n.ringkas, kabarAwas: false };
  return { dokumen: n.dokumen, patch, ringkas: n.ringkas, nota: n };
}

/** Batalkan nota barusan: tiap baris ditandai dibatalkan (tidak dihapus, seperti mulaiBatalkanTrx live); kantong literan & pelunasan sebagiannya dilepas. */
export function susunPembatalan(notaTerakhir, alasan) {
  if (!notaTerakhir) return null;
  const ids = notaTerakhir.idPenjualan.map(String);
  const baris = ambilPenjualanSemua().filter((p) => ids.indexOf(String(p.id)) >= 0 && !p.dibatalkan);
  if (!baris.length) return null;
  const kini = new Date().toISOString();
  const dokumen = baris.map((p) => ({ koleksi: 'penjualan', data: Object.assign({}, p, { dibatalkan: true, alasanKoreksi: alasan || 'Diurungkan dari sistem baru', dikoreksiPada: kini, dibatalkanPada: kini }) }));
  const hapus = baris.filter((p) => p.jenis === 'literan' && p.kemasanLiteran).map((p) => ({ koleksi: 'stokBahanLiteran', id: p.id + 1 }));
  if (notaTerakhir.piutangId) hapus.push({ koleksi: 'piutangMutasi', id: notaTerakhir.piutangId });
  return { dokumen, hapus, jumlah: baris.length };
}
export const BATAS_URUNGKAN_DETIK = 90;
